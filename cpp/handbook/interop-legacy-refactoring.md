# 跨語言整合與遺留代碼重構 / Interoperability & Legacy Code Refactoring

## Mental model｜心智模型

在處理 C++ 的邊界與舊代碼時，請建立以下兩個核心的心智模型：

### 1. 邊境管制與非軍事區 (Border Control & DMZ)
跨語言呼叫（Interop）就像是兩個不同國家（語言 runtime）之間的邊境。
- **C ABI 是通用語言（Lingua Franca）：** 無論是 Python、Rust 還是 Go，它們通常都聽不懂 C++ 的 Name Mangling 或 Exception，但它們都聽得懂 C ABI。因此，`extern "C"` 是你的外交協議。
- **資料轉換成本（Marshalling Tax）：** 在邊界傳遞資料是有代價的。盡量減少穿越邊界的次數（Chatty interface），改為一次性傳輸大塊數據（Chunky interface）。
- **異常防火牆（Exception Firewall）：** C++ 的 Exception 絕不能跨越 `extern "C"` 邊界。這就像病毒擴散，會導致 Undefined Behavior (UB)。必須在邊界設立 `try-catch` 攔截並轉換為 Error Code。

### 2. 忒修斯之船 (The Ship of Theseus)
重構 Legacy C++ 代碼庫不是「拆掉重建」，而是在航行中更換木板。
- **接縫（Seams）：** 在修改舊代碼前，先找出或創造「接縫」（通常是 Interface 或 Pimpl）。
- **黃金樣本（Golden Master）：** 舊代碼往往沒有單元測試。你的第一步不是寫測試，而是錄製「輸入/輸出」快照，確保重構後的行為與舊代碼完全一致（即使舊代碼有 Bug，重構階段也要保留該 Bug，修復是下一階段的事）。

---

## Patterns & best practices｜常見模式與最佳實務

### Interoperability (FFI)

#### 1. The C-Hourglass Pattern (沙漏模式)
這是 C++ 跨語言最穩健的模式。
- **Top:** 豐富的 Modern C++ API (Templates, Classes, Exceptions)。
- **Middle (Neck):** 扁平化的 C API (`extern "C"`, Opaque Pointers/Handles, Error Codes)。
- **Bottom:** 外部語言（Python/Rust/C#）的綁定層。
- **Why:** 避免 ABI 不相容問題，確保編譯器升級不破壞對外接口。

#### 2. Python Binding with pybind11
不要手寫 Python C API。使用 `pybind11` 讓 C++ 類別直接映射到 Python。
- **Keep Alive:** 注意 Python 與 C++ 的物件生命週期管理（Reference Counting vs. Deterministic Destruction）。使用 `pybind11::keep_alive` 策略來綁定依賴關係。
- **Buffer Protocol:** 使用 `pybind11::buffer` 或 `std::span` 讓 Python (NumPy) 與 C++ 共享記憶體，實現 Zero-copy 數據處理。

#### 3. Rust Integration with CXX
Rust 正逐漸取代 C++ 在安全性要求高的模組中的地位。
- 使用 **[CXX](https://cxx.rs/)** 庫而不是原始的 `bindgen`。CXX 會生成安全的橋接代碼，自動處理 `std::string` <-> `Rust String` 和 `std::vector` <-> `Rust Vec` 的轉換，大幅降低 `unsafe` 區塊的需求。

### Legacy Refactoring

#### 1. Characterization Testing (特徵測試)
面對無測試代碼，先寫「特徵測試」鎖定現有行為。
- 使用工具或簡單的 Script 捕捉舊函數對特定輸入的輸出。
- 只有在測試通過（綠燈）的情況下，才開始重構內部實作。

#### 2. RAII Wrapper (資源管理包裝)
不要試圖一次性把所有 `new/delete` 換成 `smart pointers`。
- **Step 1:** 創建一個小的 Class 包裝原始資源（Handle, File Descriptor, Raw Pointer）。
- **Step 2:** 在 Destructor 中釋放資源。
- **Step 3:** 逐步將業務邏輯中的手動資源管理替換為這個 Wrapper 實例。

#### 3. The Strangler Fig Pattern (絞殺榕模式)
針對大型模組的替換策略。
- 在舊系統之上建立一個新的 Facade。
- 新功能在 Facade 後用現代 C++ 實作。
- 舊功能逐步遷移到新實作，直到舊核心被完全「絞殺」並移除。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### Interop Pitfalls
- **❌ Leaking C++ Types across DLL Boundaries:**
  - 絕對不要在 DLL/Shared Object 的導出函數中使用 `std::string`, `std::vector` 或任何 STL 容器。不同編譯器（甚至不同版本）的 STL 實作記憶體佈局不同，會導致崩潰。
  - **Fix:** 使用 `char*`, `size_t` 或自定義的 C struct。
- **❌ Exceptions Crossing Boundaries:**
  - 讓 C++ exception 傳播到 C 或 Python runtime。
  - **Fix:** 在所有 `extern "C"` 函數入口處使用 `try { ... } catch (...) { return ERROR_CODE; }`。

### Refactoring Pitfalls
- **❌ The "Big Bang" Rewrite:**
  - 試圖在一個分支中重寫整個子系統。這通常會導致 Merge Hell 並且永遠無法合併。
  - **Fix:** 小步快跑，每次 commit 只做一件小事（例如：只替換一個 raw pointer 為 unique_ptr）。
- **❌ Mixing Formatting with Refactoring:**
  - 在重構邏輯的同時執行 `clang-format`。這會讓 Code Review 變得不可能，因為 Diff 會充滿雜訊。
  - **Fix:** 先提交一個純格式化的 Commit，再提交重構 Commit。
- **❌ Premature `std::shared_ptr`:**
  - 看到舊代碼的指標就無腦換成 `shared_ptr`。這會導致循環引用（Memory Leak）和效能下降。
  - **Fix:** 預設使用 `std::unique_ptr`。只有在確實需要共享所有權時才升級為 `shared_ptr`。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Safely Exposing C++ to Python
1.  **Define Interface:** 設計乾淨的 C++ Public API（避免過度使用 Template 於介面層）。
2.  **Binding:** 使用 `pybind11` 撰寫綁定代碼。
3.  **Policy Check:** 設定 `return_value_policy`（是 copy 還是 reference？）。
4.  **Exception Mapping:** 註冊自定義 Exception translator，將 C++ Exception 轉為 Python Errors。
5.  **Test:** 在 Python 端撰寫 `pytest` 驗證 C++ 邏輯。

### Checklist: Legacy Code Modernization
- [ ] **Safety Net:** 修改前是否已建立 Characterization Tests（黃金樣本）？
- [ ] **Build System:** 建置系統（CMake/Make）是否能穩定運作且無警告？
- [ ] **Static Analysis:** 是否跑過 `clang-tidy` 或 `cppcheck` 識別潛在炸彈？
- [ ] **Boundary Check:** 是否已將 `new/delete` 封裝進 RAII class？
- [ ] **Const Correctness:** 重構時是否順手補上了 `const` 修飾符？
- [ ] **Formatting:** 是否將格式化變更與邏輯變更分開提交？

---

## Real-world examples｜實戰案例

### Example 1: The "C-Hourglass" for ABI Safety
如何安全地將 C++ 類別暴露給外部（或其他 DLL）。

```cpp
// --- Internal C++ Implementation (Modern) ---
class AudioEngine {
public:
    void play(std::string_view file) { /* ... */ }
};

// --- The C Interface (The Neck) ---
// 這部分放在 header file 中，供外部使用
extern "C" {
    typedef struct OpaqueAudioEngine OpaqueAudioEngine;

    // Factory
    OpaqueAudioEngine* AudioEngine_Create() {
        return reinterpret_cast<OpaqueAudioEngine*>(new AudioEngine());
    }

    // Method Wrapper (Exception Safe!)
    int AudioEngine_Play(OpaqueAudioEngine* engine, const char* filename) noexcept {
        if (!engine || !filename) return -1;
        try {
            auto* self = reinterpret_cast<AudioEngine*>(engine);
            self->play(filename);
            return 0; // Success
        } catch (...) {
            return -2; // Generic Error
        }
    }

    // Destructor
    void AudioEngine_Destroy(OpaqueAudioEngine* engine) {
        delete reinterpret_cast<AudioEngine*>(engine);
    }
}
```

### Example 2: Refactoring `void*` Legacy Callback
舊代碼常使用 `void*` 傳遞上下文，類型不安全且難以維護。使用 Lambda 與 `std::function` 進行現代化包裝。

**Legacy C API (不可更改):**
```cpp
typedef void (*LegacyCallback)(void* user_data);
void register_callback(LegacyCallback cb, void* user_data);
```

**Modern C++ Wrapper:**
```cpp
class ModernHandler {
public:
    // 使用 std::function 允許傳遞 lambda, functors 等
    void setCallback(std::function<void()> cb) {
        m_callback = std::move(cb);
        
        // 註冊一個靜態轉發函數，將 "this" 指標作為 user_data 傳入
        register_callback([](void* user_data) {
            auto* self = static_cast<ModernHandler*>(user_data);
            if (self && self->m_callback) {
                self->m_callback();
            }
        }, this);
    }

private:
    std::function<void()> m_callback;
};

// Usage
handler.setCallback([=]() { 
    std::cout << "Modern C++ closure with captured variables!" << std::endl; 
});
```