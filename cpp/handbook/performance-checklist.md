# 效能優化檢核表：從快取友善到零成本抽象 / Performance Optimization Checklist: Cache Friendliness to Zero-Overhead

## Mental model｜心智模型

在 C++ 中談論效能，不能只看演算法的時間複雜度（Big O），更必須具備 **「硬體同理心」（Hardware Sympathy）**。現代 CPU 的運算速度遠快於記憶體存取速度，因此效能優化的核心往往不在於減少指令數，而在於**減少記憶體延遲（Memory Latency）**與**最大化 CPU 流水線效率（Pipeline Efficiency）**。

### 1. The Memory Hierarchy is King (記憶體階層即王道)
不要把記憶體視為平坦的空間（Flat RAM）。想像資料存取是一個漏斗：
- **L1/L2 Cache**: 就像在辦公桌上拿文件（~1-4 ns）。
- **RAM**: 就像去圖書館地下室調閱檔案（~100 ns）。
- **Cache Miss** 是現代軟體效能最大的殺手。如果你的資料結構導致 CPU 頻繁等待 RAM，那麼再快的演算法也是徒勞。

### 2. Zero-Overhead Abstraction (零成本抽象)
C++ 的哲學是「你不需要為你不使用的東西付費」。
- **理想狀態**：高階抽象（如 `std::unique_ptr`、Templates、Iterators）編譯後的 Assembly 應該與手寫的 C 語言指針或原始迴圈完全一致。
- **現實檢核**：如果抽象層引入了額外的虛擬函式呼叫（Virtual Function Calls）、間接層（Indirection）或不必要的拷貝，它就不是零成本。

### 3. Data-Oriented Design (資料導向設計)
物件導向（OOP）強調將資料與行為封裝在一起，但這往往對 CPU 快取不友善。
- **Mental Shift**：從「單個物件如何運作」轉向「這批資料如何流經 CPU」。
- **Structure of Arrays (SoA)** 通常優於 **Array of Structures (AoS)**，因為前者能讓 CPU 一次載入更多相關資料進行 SIMD（單指令多資料）運算。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Memory Layout & Cache Locality (記憶體佈局與快取局部性)
- **Contiguous Memory (連續記憶體)**：預設使用 `std::vector`。它是 C++ 中最快取友善的容器。避免使用 `std::list` 或 `std::map`，除非你有極特殊的插入/刪除需求且資料量很小，因為它們會造成嚴重的 **Pointer Chasing**（指標追逐）。
- **Data Hot/Cold Splitting (冷熱資料分離)**：將頻繁存取的成員變數（Hot）與極少存取的變數（Cold，如 error logs、debug names）分開存放，避免 Cold data 佔用寶貴的 Cache line。

### 2. Minimizing Allocations & Copies (最小化配置與拷貝)
- **Stack over Heap**：盡可能在 Stack 上分配物件。Heap allocation（`new`, `malloc`）不僅慢，還會導致記憶體碎片化。
- **Reserve Upfront**：使用 `std::vector::reserve()` 預先配置記憶體，避免成長時的重新分配（Reallocation）與搬移。
- **String Views**：在唯讀情境下，使用 `std::string_view` (C++17) 代替 `const std::string&`，避免暫時物件的記憶體配置。
- **Move Semantics**：確保自定義類別實作了 Move Constructor 與 Move Assignment Operator，讓資源所有權轉移取代深拷貝（Deep Copy）。

### 3. Control Flow & Branch Prediction (控制流與分支預測)
- **Branchless Programming**：盡量減少 `if-else`，特別是在緊湊迴圈（Tight Loop）中。CPU 的分支預測失敗（Branch Misprediction）代價極高（需清空 Pipeline）。
- **Likely/Unlikely Attributes**：在 C++20 中，使用 `[[likely]]` 與 `[[unlikely]]` 提示編譯器優化分支佈局。
  ```cpp
  if (error_condition) [[unlikely]] {
      handle_error(); // 編譯器會將此區塊移至 cold section
  }
  ```

### 4. Inlining & Compile-Time Evaluation (內聯與編譯期計算)
- **LTO (Link Time Optimization)**：務必在 Release build 開啟 LTO，這允許編譯器跨越 Translation Unit 進行 Inline，消除函式呼叫開銷。
- **Constexpr / Consteval**：盡可能將計算移至編譯期（Compile-time）。如果一個值可以在編譯時算出，就不應該在執行時浪費 CPU 週期。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `shared_ptr` Epidemic (濫用共享指標)
- **陷阱**：為了省事，所有地方都用 `std::shared_ptr`。
- **後果**：`shared_ptr` 的引用計數（Reference Counting）是原子操作（Atomic Operation），在多執行緒環境下會導致鎖競爭（Cache Coherency traffic），且其記憶體佈局通常是兩次 allocation（控制塊 + 資料）。
- **修正**：預設使用 `std::unique_ptr` 或單純的 Reference/Pointer，只有在真正的「共享所有權」時才用 `shared_ptr`。

### 2. Virtual Function Abuse (虛擬函式濫用)
- **陷阱**：在極高頻率呼叫的小物件上使用 `virtual` 函式（例如粒子系統中的 `Particle::update()`）。
- **後果**：
  1.  **Indirection**：需透過 V-Table 查找函式位址。
  2.  **No Inlining**：編譯器通常無法 Inline 虛擬函式。
  3.  **Cache Miss**：V-Table 指標本身可能導致 Cache Miss。
- **修正**：使用 CRTP (Curiously Recurring Template Pattern) 或 `std::variant` + `std::visit` 實現靜態多型。

### 3. Hidden Conversions (隱式轉型)
- **陷阱**：`void func(const std::string& s);` 呼叫時傳入 `"hello"` (const char*)。
- **後果**：編譯器會偷偷建立一個臨時的 `std::string` 物件（Heap allocation + Copy），函式結束後再銷毀。
- **修正**：啟用編譯器警告，或使用 `explicit` 建構子，並改用 `std::string_view`。

---

## Checklists & workflows｜檢查清單與流程

在進行效能優化前，請先遵循：**Measure, don't guess (測量，不要猜測)**。

### Phase 1: Preparation & Profiling
- [ ] **Build Configuration**: 確保是在 `Release` 模式下測試，並開啟了優化旗標（如 `-O3`, `/O2`）與 LTO。
- [ ] **Baseline**: 建立可重複執行的基準測試（Benchmark）。
- [ ] **Profiler**: 使用工具（Linux: `perf`, `Hotspot`; Windows: `VTune`, `Superluminal`; Cross: `Tracy`）找出真正的熱點（Hotspots）。**80% 的時間花在 20% 的程式碼上。**

### Phase 2: The Optimization Checklist (針對熱點)

#### 記憶體與快取 (Memory & Cache)
- [ ] **容器選擇**：是否使用了 `std::vector` 或連續記憶體結構？是否避免了 `std::list`/`std::map`？
- [ ] **預先配置**：迴圈內的 `vector` 是否呼叫了 `.reserve()`？
- [ ] **資料對齊**：結構體（Struct）是否對齊以符合 Cache Line（通常 64 bytes）？是否需要 `alignas` 防止 False Sharing？
- [ ] **存取模式**：雙重迴圈中，是否依照記憶體順序存取（Row-major vs Column-major）？

#### 拷貝與配置 (Copies & Allocations)
- [ ] **參數傳遞**：複雜型別是否使用 `const T&` 或 `std::string_view` 傳遞？
- [ ] **回傳值優化**：是否依賴 RVO (Return Value Optimization) 而非手動 `std::move` 回傳區域變數（這會破壞 RVO）？
- [ ] **迴圈變數**：`for (auto x : vec)` 是否應該是 `for (const auto& x : vec)`？（避免無意間的拷貝）。
- [ ] **暫時物件**：是否在迴圈內反覆建立/銷毀物件？能否拉到迴圈外重用？

#### 演算法與指令 (Algorithms & Instructions)
- [ ] **複雜度檢查**：是否在 $O(N^2)$ 迴圈中做線性搜尋？
- [ ] **分支預測**：熱點迴圈中是否有可移除的 `if`？能否改用算術運算或查表法（Lookup Table）？
- [ ] **虛擬函式**：熱點迴圈中是否呼叫了 `virtual` 函式？能否改用 Template 或 `final` 關鍵字幫助 Devirtualization？

---

## Real-world examples｜實戰案例

### Case 1: The "Object-Oriented" Particle System (OOP 陷阱)

**Anti-Pattern (Cache Miss Heavy):**
每個粒子都是獨立物件，分散在 Heap 的不同位置。更新時 CPU 需跳躍存取記憶體，且 `update` 是虛擬函式，無法 Inline。

```cpp
// ❌ 慢：指標追逐 + 虛擬函式開銷 + 記憶體不連續
class IParticle { virtual void update() = 0; };
class FireParticle : public IParticle { 
    float x, y, vx, vy; 
    void update() override { /*...*/ } 
};

std::vector<std::unique_ptr<IParticle>> particles;
for (auto& p : particles) p->update(); 
```

**Best Practice (Data-Oriented / Cache Friendly):**
資料緊密排列。CPU 讀取 `x[i]` 時，`x[i+1]` 已經在 Cache 中。編譯器極易進行 SIMD 自動向量化。

```cpp
// ✅ 快：SoA (Structure of Arrays) + 無虛擬函式 + 連續記憶體
struct ParticleSystem {
    std::vector<float> x, y;
    std::vector<float> vx, vy;
    
    void update() {
        size_t count = x.size();
        // 迴圈極度緊湊，對 Cache 與 Branch Predictor 友善
        for (size_t i = 0; i < count; ++i) {
            x[i] += vx[i];
            y[i] += vy[i];
        }
    }
};
```

### Case 2: String Processing in a Loop (隱藏配置)

**Anti-Pattern:**
每次迴圈都從 `std::string` 產生子字串，導致大量 `malloc` 和 `free`。

```cpp
// ❌ 慢：substr 會配置新記憶體
void process_log(const std::string& line) {
    if (line.substr(0, 5) == "ERROR") { 
        // ...
    }
}
```

**Best Practice:**
使用 `std::string_view` 或 `starts_with` (C++20)，零配置，僅操作指標與長度。

```cpp
// ✅ 快：零記憶體配置 (Zero Allocation)
void process_log(std::string_view line) {
    // C++20
    if (line.starts_with("ERROR")) {
        // ...
    }
    // 或者 C++17
    if (line.substr(0, 5) == "ERROR") { // string_view::substr 是 O(1) 且不配置記憶體
        // ...
    }
}
```