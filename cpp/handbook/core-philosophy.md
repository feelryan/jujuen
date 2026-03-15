# 核心哲學：值語意與物件生命週期 / Core Philosophy: Value Semantics & Object Lifetime

## Mental model｜心智模型

要寫好現代 C++，必須徹底拋棄 Java 或 Python 的「一切皆參考（Reference）」思維。C++ 的預設行為是 **Value Semantics（值語意）**。

### 1. 預設為「值」 (Default to Value)
將自定義的 `class` 或 `struct` 想像成 `int`。
- 當你宣告 `int a = 10;`，`a` 擁有那個數值。
- 當你宣告 `MyObject obj;`，`obj` 擁有那個物件的所有內容。
- **複製即深拷貝 (Copy is Deep Copy)**：`int b = a;` 是複製一份新的；同理，`MyObject copy = obj;` 預設也會複製整個物件內容（除非你自訂了特殊的行為）。

### 2. 作用域即生命週期 (Scope is Lifetime)
這是 C++ 最強大的特性：**Deterministic Destruction（確定性解構）**。
- 物件的生死與大括號 `{ ... }` 綁定。
- 當執行流離開宣告物件的 Scope（無論是正常執行、return、還是拋出 exception），物件的 Destructor **保證**會被呼叫。
- **心法**：你不需要「記得釋放資源」，你需要的是「將資源綁定在 Stack 變數的生命週期上」。

### 3. 移動而非複製 (Move, don't Copy)
自 C++11 起，我們有了 Move Semantics。
- 想像你在搬家。**Copy** 是把舊房子的傢俱全部照樣做一套新的放到新家（昂貴）。**Move** 是把舊房子的鑰匙交給新屋主，舊屋主不再持有（極度廉價）。
- 當一個物件是「將死之物」（例如暫時物件 rvalue），C++ 會自動選擇 Move。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Rule of Zero (零法則)
這是現代 C++ 最重要的實務原則。
- **原則**：你的類別應該 **不需要** 顯式撰寫 Destructor、Copy/Move Constructor 或 Assignment Operator。
- **做法**：使用 `std::string`, `std::vector`, `std::unique_ptr` 等已經管理好資源的成員變數。編譯器自動生成的預設行為通常就是正確的。

```cpp
// ✅ Good: Rule of Zero
class UserProfile {
    std::string name;          // 自動管理字串記憶體
    std::vector<int> scores;   // 自動管理陣列記憶體
    // 不需要寫 ~UserProfile()，編譯器生成的版本會自動呼叫 name 和 scores 的解構子
};
```

### 2. 參數傳遞決策 (Parameter Passing Strategy)
不要無腦使用指標或 Reference。請遵循以下決策樹：

- **輸入參數 (Input only)**:
    - **Cheap to copy** (如 `int`, `double`, 小 struct): **Pass by Value**.
    - **Expensive to copy** (如 `std::string`, `std::vector`): **Pass by `const T&`**.
- **輸入並持有 (Sink / Consume)**:
    - 如果函數內部需要保存這個物件的一份拷貝：**Pass by Value + `std::move`**.
- **輸出/修改 (In/Out)**:
    - 需要修改呼叫者的物件：**Pass by `T&`** (Non-const reference).

### 3. Return by Value (回傳值)
不要害怕回傳大物件。
- **RVO (Return Value Optimization)**：編譯器通常會完全消除回傳時的複製成本。
- 即使 RVO 未觸發，Move Semantics 也會確保成本極低。
- **切記**：**永遠不要**回傳 Local Variable 的 Pointer 或 Reference。

### 4. 顯式所有權 (Expressive Ownership)
看到指標型別，應該能立刻知道誰負責 `delete`。
- `std::unique_ptr<T>`: **專屬所有權**。我是唯一的擁有者。（預設使用這個）
- `std::shared_ptr<T>`: **共享所有權**。最後一個持有者負責釋放。（僅在真正需要共享時使用，如圖結構、非同步回呼）
- `T*` (Raw Pointer): **無所有權 (Non-owning observer)**。我只是來看看，我不負責生死。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Java/C# Habit" (濫用 `new`)
在現代 C++ 中，看到 `new` 是一個 Code Smell。
- **Bad**: `User* u = new User();` ... `delete u;`
- **Good**: `User u;` (Stack allocation) 或 `auto u = std::make_unique<User>();`
- **後果**：手動管理記憶體極易造成 Memory Leak 或 Double Free，且 Exception Unsafe。

### 2. Object Slicing (物件切割)
當你把一個 Derived Class 物件 assign 給 Base Class 的 **Value** 時，多型部分會被切掉。

```cpp
class Base { ... };
class Derived : public Base { ... };

void process(Base b); // ❌ 參數是 Value

Derived d;
process(d); // ⚠️ d 的 Derived 部分被切除，只剩下 Base 部分被複製進去
```
- **修正**：多型操作必須透過 Reference (`Base&`) 或 Pointer (`Base*`)。

### 3. Dangling References (懸空參考)
回傳了 Stack 記憶體的位址。

```cpp
int& getScore() {
    int score = 100;
    return score; // ❌ 炸彈！函數結束後 score 記憶體即失效
}
```
- **識別**：檢查所有回傳 Reference 的函數，確保回傳的物件生命週期長於函數呼叫。

### 4. Violation of Rule of Three/Five
如果你手寫了 Destructor，卻沒有寫 Copy Constructor/Assignment，預設的複製行為（淺拷貝）通常會導致 Double Free。
- **解法**：只要寫了 Destructor，就必須同時處理 Copy 和 Move 行為（或者明確 `delete` 掉它們）。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist: Object Lifetime
- [ ] **是否出現了 `new` 或 `delete`？**
    - 如果有，能否改用 `std::unique_ptr` 或直接用 Stack 變數？
- [ ] **類別是否遵循 Rule of Zero？**
    - 如果手寫了 `~Destructor`，是否也處理了 Copy/Move 建構子？
- [ ] **參數傳遞是否合理？**
    - 是否對 `std::string` 或 `std::vector` 使用了 Pass by Value 卻沒有在內部 Move？（造成無謂複製）
    - 是否對 `int` 或 `bool` 使用了 `const &`？（造成 pointer indirection overhead，雖然微小但無必要）
- [ ] **是否有回傳 Reference？**
    - 確保回傳的不是 Local Variable。
- [ ] **資源類別是否不可複製？**
    - 管理 File Handle 或 Socket 的類別，通常應該 `delete` Copy Constructor，只允許 Move。

### Workflow: Designing a New Class
1. **定義資料成員**：優先使用 RAII wrapper (`std::string`, `std::vector`, smart pointers)。
2. **決定語意**：
    - 它是「值」（如 Point, Date）？ -> 支援 Copy & Move。
    - 它是「資源/實體」（如 Socket, Window, Engine）？ -> 僅支援 Move，禁止 Copy (`delete` copy ops)。
3. **實作**：盡量讓編譯器自動生成特殊成員函數 (Rule of Zero)。

---

## Real-world examples｜實戰案例

### Scenario 1: The Config Loader (Refactoring Legacy Code)

**Legacy C++ (Anti-pattern):**
充滿了手動記憶體管理，容易洩漏，且所有權不明。

```cpp
// ❌ Old Style
Config* loadConfig(const char* path) {
    Config* cfg = new Config();
    if (!cfg->parse(path)) {
        delete cfg; // 容易忘記
        return nullptr;
    }
    return cfg; // 呼叫者必須記得 delete
}

void useConfig() {
    Config* c = loadConfig("settings.ini");
    if (c) {
        // ... use c
        delete c; // 繁瑣
    }
}
```

**Modern C++ (Value Semantics & Smart Pointers):**
利用 `std::optional` 表達「可能失敗」，利用 Value Semantics 自動管理生命週期。

```cpp
// ✅ Modern Style
std::optional<Config> loadConfig(std::string_view path) {
    Config cfg; // Stack allocation, cheap & safe
    if (!cfg.parse(path)) {
        return std::nullopt;
    }
    return cfg; // Return by value (Move/RVO), efficient
}

void useConfig() {
    auto cfg = loadConfig("settings.ini");
    if (cfg) {
        // use *cfg
    } 
    // cfg goes out of scope, destructor called automatically
}
```

### Scenario 2: The Heavy Resource (Move Semantics)

假設我們有一個包含巨大 Buffer 的類別。我們希望它能在函數間傳遞，但絕對不想發生 Deep Copy。

```cpp
class ImageBuffer {
    std::vector<uint8_t> data; // 假設這裡有 100MB

public:
    ImageBuffer() = default;
    
    // 顯式禁止 Copy，防止意外的效能殺手
    ImageBuffer(const ImageBuffer&) = delete;
    ImageBuffer& operator=(const ImageBuffer&) = delete;

    // 允許 Move (編譯器其實會自動生成，但這裡顯式寫出以示強調)
    ImageBuffer(ImageBuffer&&) = default;
    ImageBuffer& operator=(ImageBuffer&&) = default;

    void load(const std::string& filename) { /* ... */ }
};

// Factory function
ImageBuffer createThumbnail() {
    ImageBuffer buf;
    buf.load("huge_image.raw");
    // 這裡會觸發 Move Semantics 或 RVO
    // 100MB 的資料指標被「偷」給回傳值，而不是複製 100MB
    return buf; 
}

void process() {
    ImageBuffer img = createThumbnail(); // 零成本轉移所有權
    // ImageBuffer copy = img; // ❌ 編譯錯誤！保護你不小心複製大物件
}
```