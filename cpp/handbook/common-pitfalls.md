# 常見陷阱與反模式：Undefined Behavior 實錄 / Common Pitfalls & Anti-Patterns: The UB Chronicles

## Mental model｜心智模型

### 1. The "Contract" with the Compiler (與編譯器的契約)
C++ 的核心哲學是效能優先。為了達成極致優化，編譯器假設你的程式碼 **永遠不會** 觸發 Undefined Behavior (UB)。
- **誤區**：UB 等於程式崩潰 (Crash)。
- **真相**：UB 代表「任何事情都可能發生」。編譯器有權刪除它認為「不可能執行到」的檢查代碼，導致邏輯憑空消失、無限迴圈，甚至在看似無關的地方引發資料損壞。
- **心法**：不要試圖推測 UB 的行為（例如：「我在 x86 上跑沒事」）。一旦觸發 UB，你的程式就不再遵循邏輯，而是處於無效狀態。

### 2. Object Lifetime & Ownership (物件生命週期與所有權)
大部分的記憶體錯誤（Dangling References, Use-after-free）都源自於對「誰擁有這塊記憶體」以及「它何時消亡」的認知不清。
- **View vs. Owner**：指標 (`T*`) 和引用 (`T&`) 只是「視圖 (View)」，它們不保證背後的物件還活著。
- **Invalidation**：容器（如 `std::vector`）在擴容時會搬遷記憶體，這會導致所有指向舊位置的 View 瞬間失效。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 防禦性編碼慣例 (Defensive Coding Standards)
- **Rule of Zero/Five**：正確管理資源複製與移動，避免 Double-free 或淺拷貝 (Shallow copy)。
- **Pass-by-Reference for Polymorphism**：永遠使用 `const Base&` 或 `Base*` 來傳遞多型物件，避免 Object Slicing。
- **Scoped Enums**：使用 `enum class` 避免隱式轉型帶來的整數溢位或邏輯錯誤。

### 2. 現代 C++ 的安全替代方案
| 危險舊習 (Legacy/Risky) | 推薦做法 (Modern/Safe) | 原因 |
| :--- | :--- | :--- |
| `T*` (Owning raw pointer) | `std::unique_ptr<T>`, `std::shared_ptr<T>` | 明確所有權，自動釋放。 |
| `new` / `delete` | `std::make_unique`, `std::make_shared` | 避免 exception safety 問題與記憶體洩漏。 |
| C-style Cast `(int)x` | `static_cast`, `dynamic_cast` | 編譯期檢查，避免意外轉型。 |
| `printf` | `std::print` (C++23) / `fmt::print` | 避免格式字串與參數類型不匹配。 |
| Raw loops for removal | `std::erase_if` (C++20) | 避免 Iterator Invalidation 的手動處理錯誤。 |

### 3. 工具鏈整合 (Tooling Integration)
單靠肉眼無法抓出所有 UB，必須依賴工具：
- **Sanitizers (必須開啟)**：
  - AddressSanitizer (ASan): 偵測 Out-of-bounds, Use-after-free。
  - UndefinedBehaviorSanitizer (UBSan): 偵測整數溢位、空指標解引用等。
- **Static Analysis**: 使用 `clang-tidy` 或 `cppcheck` 在編譯前攔截問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Dangling View" Trap (懸空視圖陷阱)
這是現代 C++ 最常見的陷阱，特別是配合 `auto` 或 `std::string_view` 時。

```cpp
// ❌ Anti-pattern: Returning a reference/view to a temporary
std::string_view get_name() {
    std::string s = "Hello World";
    return s; // WRONG! 's' is destroyed when function returns.
}

// ❌ Anti-pattern: Storing lambda capture by reference to local var
auto create_callback() {
    int x = 42;
    return [&x]() { std::cout << x; }; // WRONG! 'x' is gone later.
}
```

### 2. Iterator Invalidation (迭代器失效)
在迴圈中修改容器結構是致命傷。

```cpp
std::vector<int> vec = {1, 2, 3, 4};
// ❌ Anti-pattern: Modifying vector while iterating
for (auto it = vec.begin(); it != vec.end(); ++it) {
    if (*it % 2 == 0) {
        vec.push_back(10); // WRONG! push_back might reallocate, invalidating 'it'.
    }
}
```

### 3. Object Slicing (物件切割)
當你把 Derived object 賦值給 Base object (by value) 時，Derived 的部分會被「切掉」，多型行為消失。

```cpp
class Base { public: virtual void draw() { ... } };
class Derived : public Base { public: void draw() override { ... } };

void render(Base b) { // ❌ Passed by value
    b.draw(); // Always calls Base::draw(), never Derived::draw()
}

Derived d;
render(d); // Slicing happens here.
```

### 4. Signed Integer Overflow (有號整數溢位)
在 C++ 中，`int` 溢位是 UB（不同於 `unsigned` 是 wrap-around）。編譯器可能會假設 `i + 1 > i` 永遠成立，導致無限迴圈。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist (代碼審查清單)

- [ ] **Lifetime Check**: 是否有函式回傳了指向 local variable 的 Reference 或 Pointer？
- [ ] **Container Mutation**: 在迴圈中是否對容器進行了 `push_back`, `insert`, `erase`？如果是，迭代器是否正確更新？
- [ ] **Slicing Check**: 多型類別作為參數時，是否使用了 Reference (`&`) 或 Pointer (`*`)？
- [ ] **Uninitialized Check**: 所有 POD (Plain Old Data) 類型變數是否都有初始值？
- [ ] **String View**: `std::string_view` 指向的來源字串，其生命週期是否長於 view 本身？

### Debugging Workflow for UB (UB 除錯流程)

1. **Enable Sanitizers**: 使用 `-fsanitize=address,undefined` 重新編譯並執行測試。
2. **Maximize Warnings**: 開啟 `-Wall -Wextra -Wpedantic` 並將警告視為錯誤。
3. **Minimize Scope**: 如果懷疑是記憶體損壞，嘗試縮小重現範圍，UB 往往發生在崩潰點之前的很久。
4. **Check Optimizations**: 在 `-O0` 和 `-O3` 下行為是否不同？如果不同，極大機率是 UB。

---

## Real-world examples｜實戰案例

### Case 1: The `std::string_view` Use-After-Free
這是一個在現代 C++ 專案中極易發生的錯誤，因為 `string_view` 輕量且高效，但它不擁有資料。

```cpp
#include <iostream>
#include <string>
#include <string_view>

std::string get_string() {
    return "temporary string";
}

int main() {
    // ❌ 陷阱：
    // get_string() 回傳一個暫時物件 (temporary std::string)。
    // std::string_view 綁定到這個暫時物件的內部 buffer。
    // 這一行結束後，暫時物件被銷毀。
    std::string_view sv = get_string(); 
    
    // 此時 sv 指向已釋放的記憶體 (Dangling Pointer)。
    // 運氣好：印出亂碼。運氣不好：Crash 或看起來正常 (最危險)。
    std::cout << sv << std::endl; 
    
    return 0;
}
```
**修正**：延長暫時物件生命週期，或直接複製。
```cpp
std::string s = get_string(); // Keep ownership
std::string_view sv = s;      // View is valid as long as 's' is valid
```

### Case 2: The Vector Reallocation Crash
在處理大量數據輸入時，工程師為了方便，保存了指向 vector 元素的指標。

```cpp
struct User { int id; std::string name; };
std::vector<User> users;

void process_users() {
    users.push_back({1, "Alice"});
    User* alice_ptr = &users[0]; // 指向 Alice
    
    // ... 經過一段複雜邏輯 ...
    
    // 觸發 vector 擴容 (Reallocation)
    for (int i = 0; i < 1000; ++i) {
        users.push_back({i, "Bot"});
    }
    
    // ❌ 陷阱：
    // 上面的 loop 導致 vector 重新分配記憶體並搬家。
    // alice_ptr 現在指向舊的、已經被釋放的記憶體位置。
    std::cout << alice_ptr->name << std::endl; // UB: Use-after-free
}
```
**修正**：使用 Index 存取，或在擴容後重新獲取指標，或預先 `reserve` 足夠空間。