# 錯誤處理策略：Exceptions vs. Error Codes vs. std::expected / Error Handling Strategy: Exceptions vs. Error Codes vs. std::expected

## Mental model｜心智模型

在 C++ 中，錯誤處理不僅僅是語法選擇，更是**API 合約（Contract）**與**控制流（Control Flow）**的設計哲學。我們應將錯誤分為三類，並對應不同的處理機制：

1.  **程式錯誤（Bugs / Logic Errors）**：
    *   **定義**：程式寫錯了，例如 Array index out of bounds、Null pointer dereference。
    *   **模型**：**不可恢復**。這不是執行時期的「意外」，而是開發者的疏忽。
    *   **對策**：`assert`、`std::terminate` 或 Contract (C++26)。不要試圖用 `try-catch` 恢復，讓程式崩潰以便除錯。

2.  **執行環境錯誤（Exceptional Runtime Errors）**：
    *   **定義**：外部資源耗盡或不可用，例如 `std::bad_alloc`（記憶體不足）、網路斷線、硬碟損壞。
    *   **模型**：**隱式跳轉（Implicit Jump）**。這類錯誤發生頻率低，且通常無法在當前函式解決，需要層層上報。
    *   **對策**：**Exceptions**。就像火災警報，打斷正常流程，撤離到安全區域（Catch block）處理。

3.  **預期內的失敗（Expected Failures / Domain Errors）**：
    *   **定義**：業務邏輯的一部分，例如「找不到使用者」、「密碼錯誤」、「解析失敗」。
    *   **模型**：**顯式資料流（Explicit Data Flow）**。失敗是函式回傳值的一種可能性。
    *   **對策**：**`std::expected` (C++23)** 或 **Error Codes**。強迫呼叫者檢查結果，因為這不是「意外」，而是「結果的一種」。

### The "Happy Path" Trade-off

*   **Exceptions**: 優化 Happy Path（正常路徑無額外檢查成本），但錯誤路徑成本極高（Stack Unwinding）。
*   **Error Codes / std::expected**: 稍微拖慢 Happy Path（因為每個呼叫都要檢查分支），但錯誤路徑成本低且可預測。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 `std::expected` 取代錯誤碼 (C++23)
傳統錯誤碼（Error Codes）最大的問題是將「錯誤資訊」與「回傳值」分離（例如回傳 `int` 錯誤碼，透過 reference 參數傳回值）。`std::expected<T, E>` 是一個 Sum Type（類似 Rust 的 `Result`），它要嘛是值 `T`，要嘛是錯誤 `E`。

*   **Pattern**: 使用 `.and_then()` 進行 Monadic 操作，將錯誤處理鏈式化，避免 "Pyramid of Doom"（過多的 `if` 巢狀）。
*   **Legacy Support**: 若未升級至 C++23，可使用 `tl::expected` 或 `boost::outcome`。

### 2. 建構子（Constructors）必須使用 Exceptions
建構子沒有回傳值，若建構失敗（例如開啟檔案失敗），唯一的標準 C++ 方式是拋出例外。

*   **Pattern**: **RAII (Resource Acquisition Is Initialization)**。確保資源在建構子獲取，在解構子釋放。若建構失敗，拋出例外，確保物件不會處於「半初始化」的殭屍狀態。
*   **Alternative**: 若環境禁用了 Exception（如嵌入式），則必須使用 `init()` 模式（Two-phase initialization），但這容易被誤用（忘記呼叫 `init()`）。

### 3. 強異常保證（Strong Exception Guarantee）
若你決定使用 Exception，必須保證：**如果函式拋出例外，程式狀態應回復到呼叫前（Commit or Rollback）**。

*   **Pattern**: **Copy-and-Swap**。先在臨時物件上操作，成功後再與原物件交換。

### 4. 邊界處的 `noexcept` 防火牆
在 C++ 與 C 語言、OS Callback 或其他語言（如 Python/C#）的邊界，絕對不能讓 Exception 逃逸（這會導致 Undefined Behavior 或 Crash）。

*   **Pattern**: 在邊界函式使用 `try { ... } catch (...) { ... }` 攔截所有例外，並轉換為 Error Code 傳遞給外部。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 Exceptions 控制流程 (Exceptions for Control Flow)
不要用 Exception 來處理正常的業務邏輯（例如：用 `throw UserNotFound` 來代表查詢結果為空）。
*   **後果**：效能極差（比 `if` 慢數十倍甚至百倍），且讓程式碼難以閱讀（GOTO 隱喻）。
*   **修正**：使用 `std::optional` 或 `std::expected`。

### 2. 在解構子中拋出例外 (Throwing in Destructors)
這是 C++ 的死罪。如果 Stack Unwinding 過程中解構子又拋出例外，程式會直接呼叫 `std::terminate` 結束。
*   **修正**：解構子永遠標記為 `noexcept`。若解構過程出錯（如 log 寫入失敗），只能吞掉或記錄，不能拋出。

### 3. 忽略 `[[nodiscard]]` 的錯誤碼
傳統錯誤碼最危險的是「開發者忘記檢查」。
*   **修正**：對於回傳 Error Code 或 `std::expected` 的函式，務必加上 `[[nodiscard]]` 屬性，強迫呼叫者處理。

### 4. 捕捉所有例外卻不處理 (Pokemon Exception Handling)
```cpp
try { do_something(); } catch (...) { /* ignore */ } // Gotta catch 'em all!
```
*   **後果**：隱藏了真正的 Bug，導致系統處於不一致狀態繼續執行，日後更難除錯。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 如何選擇錯誤處理機制？

請依照以下順序回答問題，決定使用哪種機制：

1.  **這是一個 Bug 嗎？** (Index out of bounds, Nullptr)
    *   YES -> **Assert / Terminate** (Fix the code, don't handle it).
    *   NO -> 下一題。

2.  **專案是否強制禁用 Exceptions？** (Embedded, Real-time constraints, Google Style)
    *   YES -> **`std::expected`** (首選) 或 **Error Codes**。
    *   NO -> 下一題。

3.  **這個錯誤是「預期內」的業務邏輯嗎？** (File not found, Invalid input)
    *   YES -> **`std::expected`** (C++23) 或 **`std::optional`** (若錯誤原因不重要)。
    *   NO -> 下一題。

4.  **這是一個建構子 (Constructor) 嗎？**
    *   YES -> **Exceptions**。
    *   NO -> 下一題。

5.  **這是一個運算子重載 (Operator Overload) 嗎？**
    *   YES -> **Exceptions** (通常運算子不適合回傳 expected)。
    *   NO -> **Exceptions** (針對資源耗盡等罕見錯誤) 或 **`std::expected`** (視團隊風格而定)。

### Implementation Checklist

- [ ] **Interface**: 函式簽名是否清楚表達了可能失敗？(使用 `std::expected` 或 `std::optional` 而非隱晦的 int)。
- [ ] **Safety**: 解構子（Destructors）與移動建構子（Move Constructors）是否標記為 `noexcept`？
- [ ] **Visibility**: 是否對重要的回傳值加上了 `[[nodiscard]]`？
- [ ] **Leak-Freedom**: 在 Exception 拋出時，RAII 物件是否能正確釋放資源？
- [ ] **Boundary**: 在 `extern "C"` 介面處是否攔截了所有 Exceptions？

---

## Real-world examples｜實戰案例

### Scenario 1: 解析設定檔 (Business Logic Error)

這裡使用 `std::expected`，因為「設定檔格式錯誤」是預期內可能發生的，且我們需要知道具體的錯誤訊息。

```cpp
#include <expected>
#include <string>
#include <iostream>

enum class ConfigError {
    FileNotFound,
    ParseError,
    InvalidValue
};

struct Config {
    int timeout;
    std::string host;
};

// 使用 std::expected 明確表達：可能回傳 Config，也可能回傳 ConfigError
[[nodiscard]] 
std::expected<Config, ConfigError> load_config(const std::string& path) {
    if (path.empty()) return std::unexpected(ConfigError::FileNotFound);
    // ... 假設解析過程 ...
    bool parse_success = false; 
    if (!parse_success) return std::unexpected(ConfigError::ParseError);
    
    return Config{30, "localhost"};
}

void startup() {
    auto result = load_config("config.json");
    
    if (result) {
        std::cout << "Starting with timeout: " << result->timeout << "\n";
    } else {
        // 強迫處理錯誤路徑
        switch (result.error()) {
            case ConfigError::FileNotFound: std::cerr << "Missing config!\n"; break;
            case ConfigError::ParseError:   std::cerr << "Bad JSON!\n"; break;
            default: std::cerr << "Unknown error\n"; break;
        }
    }
}
```

### Scenario 2: 資源獲取 (Resource Acquisition)

這裡使用 Exception，因為建構子無法回傳值，且資料庫連線失敗通常導致該物件無法使用。

```cpp
#include <stdexcept>
#include <string>

class DatabaseConnection {
public:
    // 建構子：建立失敗則拋出例外
    DatabaseConnection(const std::string& conn_str) {
        if (!connect_impl(conn_str)) {
            throw std::runtime_error("Failed to connect to DB: " + conn_str);
        }
    }

    // 解構子：必須 noexcept
    ~DatabaseConnection() noexcept {
        try {
            disconnect_impl();
        } catch (...) {
            // 吞掉錯誤，避免 terminate
            // log_error("Disconnect failed");
        }
    }

    void query(const std::string& sql) {
        if (!is_connected) throw std::logic_error("Connection lost");
        // ...
    }

private:
    bool connect_impl(const std::string& s) { return true; /* stub */ }
    void disconnect_impl() { /* stub */ }
    bool is_connected = true;
};

void process_data() {
    try {
        // RAII: 若成功則 conn 存在，若失敗則跳至 catch，不會有「半初始化」物件
        DatabaseConnection conn("postgres://...");
        conn.query("SELECT * FROM users");
    } catch (const std::exception& e) {
        // 統一處理資源獲取失敗
        std::cerr << "Fatal error: " << e.what() << "\n";
    }
}
```