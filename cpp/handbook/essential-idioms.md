# 必備慣用語：RAII、Pimpl 與 Type Erasure / Essential Idioms: RAII, Pimpl & Type Erasure

在 C++ 的世界裡，語言特性提供了「機制」，而慣用語（Idioms）則定義了「文化」。掌握 RAII、Pimpl 與 Type Erasure，不僅是為了寫出正確的程式碼，更是為了寫出具備 **異常安全（Exception Safety）**、**編譯效率** 與 **低耦合** 的專業級系統。

---

## Mental model｜心智模型

### 1. RAII: Scope as the Owner (作用域即持有者)
不要將 RAII 僅僅理解為「釋放記憶體」。
- **核心概念**：資源的生命週期嚴格綁定物件的生命週期（Lifetime）。
- **譬喻**：就像旅館的房卡系統。你走進房間（Constructor）燈亮起；你離開房間（Destructor / Scope Exit）燈自動熄滅。你不需要打電話給櫃檯說「我要關燈」，離開這個動作本身就觸發了清理。
- **關鍵點**：利用 Stack Unwinding 機制，確保即使發生 Exception，資源也能被釋放。

### 2. Pimpl: The Compilation Firewall (編譯防火牆)
- **核心概念**：將「介面（Interface）」與「實作細節（Implementation）」在物理檔案層面上徹底分離。
- **譬喻**：就像智慧型手機。使用者只看得到觸控螢幕（Header file / Public API），看不到裡面的電路板、電池與晶片佈局（Private Implementation）。更重要的是，更換電池供應商（修改 Private Member）不需要更換整支手機的外殼，也不需要使用者重新學習操作。
- **價值**：減少標頭檔依賴（Header Dependency），加速編譯，保持 ABI 穩定。

### 3. Type Erasure: Duck Typing in C++ (靜態語言中的鴨子型別)
- **核心概念**：我不關心你是什麼型別，我只關心你能做什麼（Behavior-based polymorphism）。
- **譬喻**：通用轉接頭。無論你是筆電、手機還是刮鬍刀，只要插頭形狀對了（符合介面要求），就能插進插座供電。插座不需要知道電器的具體品牌或型號。
- **區別**：傳統繼承（Inheritance）要求物件「是（IS-A）」某個基底類別；Type Erasure 只要求物件「像（Acts-Like）」某個概念。

---

## Patterns & best practices｜常見模式與最佳實務

### RAII: The Rule of Zero & Custom Wrappers

在現代 C++ 中，你很少需要手寫解構子（Destructor）。

1.  **Rule of Zero**：優先使用 `std::unique_ptr`, `std::shared_ptr`, `std::vector`, `std::string` 等標準庫容器來管理資源。若類別成員都已具備 RAII 特性，編譯器生成的預設解構子就是正確的。
2.  **Legacy C API Wrapper**：當對接 C 語言庫（如 OpenSSL, POSIX File descriptors）時，使用 `unique_ptr` 搭配 Custom Deleter。

```cpp
// Pattern: Wrapping a C-style resource (e.g., FILE*)
struct FileCloser {
    void operator()(FILE* fp) const {
        if (fp) fclose(fp);
    }
};
using FilePtr = std::unique_ptr<FILE, FileCloser>;

void processFile() {
    FilePtr file(fopen("data.txt", "r")); // 自動管理關閉
    if (!file) return;
    // ... 即使這裡 throw exception，fclose 也會被呼叫
}
```

### Pimpl: Modern Implementation

使用 `std::unique_ptr` 來管理實作指標，但要注意 `const` 語意與解構子位置。

1.  **Header (`widget.h`)**：只宣告 `Impl` 結構，不定義。
2.  **Source (`widget.cpp`)**：定義 `Impl` 結構。
3.  **Destructor**：必須在 `.cpp` 中定義（即使是 default），因為 `unique_ptr` 需要在刪除點看到完整型別。

```cpp
// widget.h
#include <memory>

class Widget {
public:
    Widget();
    ~Widget(); // 必須宣告，不能在 header 寫 = default
    
    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    void draw();

private:
    class Impl; // Forward declaration
    std::unique_ptr<Impl> pImpl;
};
```

### Type Erasure: `std::function` & `std::any`

最常見的 Type Erasure 是 `std::function`（擦除函式指標、Lambda、Functor 的差異）。進階用法是手寫類似 Sean Parent 的 Concept-Model 模式。

- **日常用法**：使用 `std::function` 儲存 callback，解耦呼叫者與實作者。
- **進階用法**：當你需要多型，但不想強迫使用者繼承你的 Base Class 時。

```cpp
// Pattern: Storing heterogeneous objects that satisfy a concept
#include <vector>
#include <functional>

using Drawable = std::function<void()>;

void renderAll(const std::vector<Drawable>& objects) {
    for (const auto& draw : objects) {
        draw(); // 多型呼叫，但沒有繼承關係
    }
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. RAII Pitfalls
- **❌ Naked `new`/`delete`**：在現代 C++ 程式碼中看到 `delete` 關鍵字通常是個警訊（Code Smell）。這表示你在手動管理資源，容易發生洩漏。
- **❌ Throwing in Destructor**：永遠不要讓 Exception 逃出解構子。如果解構子是在 Stack Unwinding 過程中被呼叫的，再次拋出異常會導致 `std::terminate`（程式直接崩潰）。

### 2. Pimpl Pitfalls
- **❌ Inline Constructor/Destructor**：如果在 Header 檔裡寫了 `Widget::~Widget() = default;`，編譯器會報錯（因為 `unique_ptr` 此時不知道 `Impl` 的大小）。**解法**：務必在 `.cpp` 檔實作解構子。
- **❌ Broken Const Correctness**：`unique_ptr` 的 const 性質只保護指標本身，不保護指向的物件。`const Widget` 的方法可以修改 `pImpl` 指向的內容。
    - **修正**：使用 `std::experimental::propagate_const` (若可用) 或在存取 `pImpl` 時手動檢查。

### 3. Type Erasure Pitfalls
- **❌ Performance Overhead**：Type Erasure 通常涉及虛擬函式呼叫（Virtual dispatch）與堆積記憶體配置（Heap allocation）。在極度效能敏感的迴圈（Hot path）中需謹慎使用 `std::function`。
- **❌ Over-Engineering**：如果你能控制所有型別，且型別數量有限，使用 `std::variant` (C++17) 往往比 Type Erasure 更高效且型別安全。

---

## Checklists & workflows｜檢查清單與流程

在設計一個新的類別或模組時，請依序使用此決策樹：

### Decision Tree: Which Idiom?
1.  **我是否需要管理非記憶體資源（檔案、鎖、Socket）？**
    - [ ] 是 → 使用 **RAII** 封裝成 Class，並刪除 Copy Constructor。
2.  **我的 Class 是否包含大量 Private 成員，且 Header 被廣泛 include？**
    - [ ] 是 → 使用 **Pimpl** 減少編譯時間依賴。
3.  **我是否需要儲存不同型別的物件，且不想強迫它們繼承特定 Base Class？**
    - [ ] 是 → 使用 **Type Erasure** (`std::function`, `std::any` 或自定義)。

### Code Review Checklist
- **RAII**
    - [ ] 是否完全避免了手動 `delete`？
    - [ ] 自定義的 RAII Class 是否正確處理了 Copy/Move 語意（通常是禁止 Copy，允許 Move）？
- **Pimpl**
    - [ ] `~Widget()` 是否定義在 `.cpp` 檔？
    - [ ] Move Constructor 與 Move Assignment 是否正確實作（`unique_ptr` 需要）？
    - [ ] 是否真的有必要？（不要為了 Pimpl 而 Pimpl，簡單類別不需要）。
- **Type Erasure**
    - [ ] 是否考慮過 `template` 或 `std::variant` 作為替代方案？
    - [ ] 是否意識到可能的記憶體配置成本？

---

## Real-world examples｜實戰案例

### Scenario 1: The "SDK Wrapper" (RAII + Pimpl)
**情境**：你需要封裝一個第三方的 C 語言 SDK（例如一個相機驅動），它依賴大量的 header 檔案，且你不希望污染你的專案 namespace。

```cpp
// Camera.h - Clean Interface
#include <memory>
#include <vector>

class Camera {
public:
    Camera();
    ~Camera(); // Defined in .cpp
    
    // Move-only type (RAII resource handle)
    Camera(const Camera&) = delete;
    Camera& operator=(const Camera&) = delete;
    Camera(Camera&&) noexcept;
    Camera& operator=(Camera&&) noexcept;

    void capture();

private:
    class Impl;
    std::unique_ptr<Impl> m_impl;
};
```

```cpp
// Camera.cpp - Dirty Details
#include "Camera.h"
#include <3rd_party_driver.h> // 只有這裡包含髒 header

class Camera::Impl {
public:
    Impl() { 
        handle_ = DriverInit(); // RAII: Acquire
    }
    ~Impl() { 
        DriverCleanup(handle_); // RAII: Release
    }
    void doCapture() { DriverSnap(handle_); }
    
    DRIVER_HANDLE handle_;
};

Camera::Camera() : m_impl(std::make_unique<Impl>()) {}
Camera::~Camera() = default; // 這裡看得到 Impl 定義，unique_ptr 能正常工作
// ... move implementation ...
void Camera::capture() { m_impl->doCapture(); }
```

### Scenario 2: The "Event System" (Type Erasure)
**情境**：設計一個 GUI 按鈕，點擊時觸發行為。行為可能是一個函式指標、一個 Lambda，或者一個物件的方法。

```cpp
// Button.h
#include <functional>
#include <string>

class Button {
public:
    using ClickHandler = std::function<void()>; // Type Erasure

    void setOnClick(ClickHandler handler) {
        m_handler = std::move(handler);
    }

    void click() {
        if (m_handler) m_handler();
    }

private:
    ClickHandler m_handler;
};

// Usage
void setupUI() {
    Button btn;
    
    // 1. Lambda
    btn.setOnClick([](){ printf("Clicked!\n"); });
    
    // 2. Binding member function
    MyWindow win;
    btn.setOnClick(std::bind(&MyWindow::onClose, &win));
    
    // Button 不需要知道 handler 背後是什麼，只要能被 "call" 即可。
}
```