# 現代 C++ 風格指南與最佳實踐 / Modern C++ Style Guide & Best Practices

## Mental model｜心智模型

在現代 C++ (C++11/14/17/20+) 中，撰寫程式碼的核心思維已從「如何操作記憶體」轉變為「如何表達意圖 (Intent) 與所有權 (Ownership)」。

### 1. 預設更安全 (Safety by Default)
不要依賴工程師的記憶力去釋放資源。現代 C++ 的風格建立在 **RAII** (Resource Acquisition Is Initialization) 之上。你的心智模型應該是：**「如果我沒有明確說要共享這個物件，那它就應該是獨有的；如果我不需要修改它，那它就應該是唯讀的。」**

### 2. 編譯器是你的副駕駛 (Compiler as Co-pilot)
現代風格強調利用型別系統 (Type System) 讓編譯器幫你抓錯。
- 使用 `const` 讓編譯器阻止意外修改。
- 使用 `auto` 避免隱式轉型 (Implicit Conversion) 造成的精度遺失或效能損耗。
- 使用 Smart Pointers 讓編譯器管理生命週期。

### 3. 所有權金字塔 (The Ownership Pyramid)
對於指標的使用，應建立以下層級觀念：
1.  **`std::unique_ptr`**: 預設選項。擁有物件，獨佔控制權。
2.  **Raw Pointer (`T*`)**: 僅作「觀察者 (Observer)」。**不擁有**資源，不負責釋放，僅用於存取。
3.  **`std::shared_ptr`**: 僅在「真正需要共享所有權」時使用（例如：圖結構中的節點、多執行緒間的共享資源）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 初始化：統一使用大括號 (Uniform Initialization)
盡量使用 `{}` 進行初始化，因為它禁止了縮窄轉換 (Narrowing Conversion)，且語法統一。

```cpp
// Recommended
int x{0};
double d{3.14};
std::string s{"Hello"};
std::vector<int> v{1, 2, 3};

// Avoid (Old style)
int x = 0; 
int y(0); // 容易被誤認為函式宣告 (Most Vexing Parse)
```

> **注意**：對於 `std::vector` 等容器，`{}` 代表元素列表，`()` 代表建構參數（如大小）。
> `std::vector<int> v{10};` // 一個元素，值為 10
> `std::vector<int> v(10);` // 十個元素，值為 0

### 2. AAA (Almost Always Auto)
除非型別非常明顯且簡單（如 `int`, `bool`），否則優先使用 `auto`。這能強迫你初始化變數，並避免隱式轉型。

```cpp
// Recommended
auto employee = get_employee_record(id); // 閱讀重點在變數名，而非型別
auto& name = employee.name;              // 避免複製

// Why? Consider this anti-pattern:
std::map<int, std::string> m;
// ... fill map ...
// 錯誤：map 的 key-value pair 是 std::pair<const int, std::string>
// 下面這行會導致整個 pair 被複製，因為 key 型別不匹配 (int vs const int)
for (const std::pair<int, std::string>& item : m) { ... } 

// Correct with auto:
for (const auto& item : m) { ... }
```

### 3. Const 正確性 (Const Correctness)
將 `const` 視為預設狀態。如果一個變數或方法不需要修改狀態，就**必須**加上 `const`。

- **變數**：`const auto limit = 100;`
- **方法**：`int get_value() const { return value_; }`
- **指標**：
    - `const T*` (指向常數的指標 - 指標可變，內容不可變) -> **最常用於觀察者**。
    - `T* const` (常數指標 - 指標不可變，內容可變)。

### 4. 智慧指標的使用策略 (Smart Pointer Strategy)

- **Factory Functions**: 使用 `std::make_unique` 和 `std::make_shared` 建立物件，而非直接 `new`。這能確保 Exception Safety 並減少重複代碼。

```cpp
// Recommended
auto widget = std::make_unique<Widget>();

// Avoid
std::unique_ptr<Widget> widget(new Widget());
```

- **參數傳遞 (Parameter Passing)**:
    - **不涉及所有權移轉**：傳遞 `const T&` 或 `T*` (若可為 null)。**不要**傳遞 `const std::unique_ptr<T>&`，這限制了呼叫者必須持有 unique_ptr。
    - **移轉所有權 (Sink)**：傳遞 `std::unique_ptr<T>` (By Value)。
    - **共享所有權**：傳遞 `std::shared_ptr<T>` (By Value)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 `std::shared_ptr` (Shared Pointer Abuse)
**現象**：專案中充滿了 `shared_ptr`，幾乎看不到 `unique_ptr`。
**後果**：
- **效能低落**：`shared_ptr` 的引用計數 (Reference Counting) 是 atomic 操作，有顯著開銷。
- **物件生命週期不明**：很難知道物件何時真正被釋放，容易造成 Memory Leak (因 Cyclic Reference)。
**修正**：預設使用 `unique_ptr`，只有在多個擁有者確實需要同時持有該物件時才轉為 `shared_ptr`。

### 2. 裸指標擁有權 (Raw Pointer Ownership)
**現象**：`Widget* w = new Widget();` 出現在應用層代碼中。
**後果**：Exception 發生時無法釋放記憶體；忘記 `delete`；Double free。
**修正**：除了實作底層資料結構（如自訂 Vector），現代 C++ 應用層代碼**不應出現** `new` 和 `delete`。

### 3. `auto` 推導陷阱 (Auto Deduction Pitfalls)
**現象**：忽略 `auto` 預設是「值複製 (By Value)」。
**後果**：無意間的深層複製 (Deep Copy)。

```cpp
const std::string& get_name();

auto name = get_name(); // name 是 std::string (複製)，而非 reference
// 修正：
auto& name_ref = get_name(); 
// 或
const auto& name_cref = get_name();
```

### 4. 輸出參數 (Output Parameters)
**現象**：`void get_data(std::vector<int>& out_vec);`
**後果**：代碼閱讀困難，無法使用 `const`。
**修正**：直接回傳數值。現代編譯器有 RVO (Return Value Optimization)，回傳大型物件通常是零成本的。
```cpp
std::vector<int> get_data(); // Better
```

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構時，請使用此清單檢查現代化程度：

### Initialization & Types
- [ ] 是否使用了 `auto` 來宣告變數（除非型別不明確影響閱讀）？
- [ ] 是否使用了 `{}` 進行初始化（Uniform Initialization）？
- [ ] 變數宣告是否盡可能靠近第一次使用的位置（而非函式開頭）？
- [ ] 唯讀變數是否都加上了 `const`？

### Memory Management
- [ ] 是否完全消除了 `new` 和 `delete` 關鍵字？
- [ ] 是否優先使用 `std::unique_ptr` 而非 `std::shared_ptr`？
- [ ] 函式參數若不涉及所有權轉移，是否使用 `const T&` 或 `T*`（而非 Smart Pointer）？
- [ ] 是否使用 `std::make_unique` / `std::make_shared` 來建立物件？

### Class Design
- [ ] 類別成員變數是否有預設初始值 (In-class initializers)？
- [ ] 單參數建構子是否標記為 `explicit` 以避免意外轉型？
- [ ] 唯讀的成員函式是否標記為 `const`？
- [ ] 是否使用 `override` 關鍵字標記覆寫的虛擬函式？

---

## Real-world examples｜實戰案例

### 案例：重構遺留代碼 (Refactoring Legacy Code)

我們有一個處理影像的函式，舊版寫法充滿了 C++98 的風格與風險。

#### Before (Legacy / Risky)

```cpp
// 舊式風格：手動管理記憶體，型別重複，缺乏 const
Image* process_image(const char* path, int* err_code) {
    Image* img = new Image(path); // 風險：若建構失敗或後續拋出異常，誰來 delete？
    
    if (!img->is_valid()) {
        *err_code = -1;
        delete img; // 手動釋放，容易遺漏
        return NULL;
    }

    // 繁瑣的迭代器語法
    std::vector<Pixel>::iterator it;
    for (it = img->pixels.begin(); it != img->pixels.end(); ++it) {
        it->adjust_brightness(10);
    }

    *err_code = 0;
    return img; // 回傳裸指標，所有權不明確
}
```

#### After (Modern / Safe)

```cpp
// 現代風格：RAII，自動推導，異常處理，明確所有權
#include <memory>
#include <optional>

// 使用 std::unique_ptr 明確表示回傳值的所有權移轉
// 使用 std::string_view 避免字串複製 (C++17)
std::unique_ptr<Image> process_image(std::string_view path) {
    // 使用 make_unique 確保 Exception Safety
    auto img = std::make_unique<Image>(path);

    if (!img->is_valid()) {
        // 拋出異常或回傳 nullptr，資源會自動釋放 (RAII)
        throw std::runtime_error("Invalid image format");
    }

    // Range-based for loop 與 auto 讓代碼更乾淨
    // 使用 reference 避免複製 Pixel
    for (auto& pixel : img->pixels) {
        pixel.adjust_brightness(10);
    }

    return img; // 編譯器自動處理 move 語意，無須手動釋放
}
```

### Key Takeaways from Example:
1.  **Ownership**: 回傳 `unique_ptr` 清楚告知呼叫者：「這個物件現在歸你管」。
2.  **Safety**: 移除了所有 `delete`，即使發生 Exception 也不會 Memory Leak。
3.  **Readability**: `auto& pixel` 比 `std::vector<Pixel>::iterator` 易讀得多。
4.  **Efficiency**: `string_view` 避免了將 `const char*` 轉為 `std::string` 的記憶體配置。