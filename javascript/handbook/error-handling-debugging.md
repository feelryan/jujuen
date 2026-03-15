# 錯誤處理與除錯策略 / Error Handling & Debugging Strategies

在 JavaScript 的世界裡，錯誤處理不僅僅是為了「修復 Bug」，更是為了確保系統在面對不可預測狀況（網路斷線、資料異常、第三方服務掛點）時，能夠**優雅地降級（Graceful Degradation）**或**安全地失敗（Fail Safe）**。

本章節將協助你建立正確的錯誤處理心智模型，並提供實戰中的除錯流程。

---

## Mental model｜心智模型

### 1. 錯誤的分類：Operational vs. Programmer Errors
不要將所有錯誤一視同仁。在 Node.js 與瀏覽器環境中，應區分兩種層次：
*   **Operational Errors (操作型錯誤)**：這是**預期中**可能發生的異常（Runtime problems）。例如：API 請求 404、網路超時、資料庫連線失敗。這類錯誤需要被**處理（Handled）**並回饋給使用者。
*   **Programmer Errors (程式邏輯錯誤)**：這是**Bug**。例如：讀取 `undefined` 的屬性、傳遞錯誤的參數型別。這類錯誤通常無法自動恢復，最佳策略是 **Crash (Fail Fast)** 並修復程式碼，而不是試圖用 `try/catch` 掩蓋它。

### 2. 錯誤傳遞鏈（The Bubble Up Mechanism）
想像錯誤是一個氣泡，它會沿著 **Call Stack（呼叫堆疊）** 向上浮起。
*   **同步程式碼**：氣泡會自動向上層函式傳遞，直到被 `catch` 或導致程式崩潰。
*   **非同步程式碼（Async/Await）**：如果沒有正確使用 `await` 或 `.catch()`，氣泡會飄到「無人之境」（Unhandled Promise Rejection），導致上下文遺失或 Process 終止。

### 3. 錯誤即資料（Error as Data）
在 JS 中，`Error` 是一個物件。除錯的核心在於**保留上下文（Context）**。一個好的錯誤物件不應只有 `message`，還應包含 `stack trace`、`code`（錯誤代碼）以及導致錯誤的原始資料（Metadata）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用自定義錯誤類別 (Custom Error Classes)
不要只 `throw new Error('message')`。建立繼承自 `Error` 的類別，以便在上層邏輯中透過 `instanceof` 進行針對性處理。

```javascript
class AppError extends Error {
  constructor(message, statusCode, isOperational = true) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.isOperational = isOperational; // 標記是否為預期中的操作錯誤
    Error.captureStackTrace(this, this.constructor);
  }
}

// Usage
if (!user) {
  throw new AppError('User not found', 404);
}
```

### 2. 集中式錯誤處理 (Centralized Error Handling)
不要在每個函式裡都寫 `try/catch`。
*   **Backend (Node/Express/Koa)**: 使用 Middleware 統一接住所有錯誤，決定要 log 下來還是回傳 HTTP Response。
*   **Frontend (React/Vue)**: 使用 Error Boundaries 或 Global API Interceptor 處理 UI 崩潰或網路錯誤。

### 3. Error Chaining (使用 `cause` 屬性)
當你 catch 到一個底層錯誤（如 DB 連線失敗）並想拋出一個更高層級的錯誤（如「系統忙碌中」）時，**千萬不要丟失原始錯誤**。使用 ES2022 的 `cause` 屬性。

```javascript
try {
  await connectToDatabase();
} catch (err) {
  // 保留原始 err 資訊，方便除錯，同時對外拋出語意化錯誤
  throw new Error('Database connection failed', { cause: err });
}
```

### 4. 結構化日誌 (Structured Logging)
在生產環境中，`console.log` 是不夠的。使用如 `Winston`、`Pino` 或 `Bunyan` 等工具輸出 **JSON 格式**的 Log，並包含 `correlation-id` (Trace ID)，以便在分散式系統中追蹤單一請求的完整路徑。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Throwing Strings or Objects
**Bad:** `throw 'Something went wrong'` 或 `throw { code: 500 }`。
**Why:** 這樣做會丟失 **Stack Trace**（堆疊追蹤），讓你在除錯時完全不知道錯誤是從哪一行程式碼發生的。永遠要 `throw new Error(...)`。

### 2. The "Catch-All" Silence (吞沒錯誤)
**Bad:**
```javascript
try {
  doSomething();
} catch (e) {
  console.log('Error happened'); // 什麼都沒做，程式繼續跑
}
```
**Why:** 這會讓系統處於不一致的狀態（Inconsistent State），且讓 Bug 變得極難追蹤。除非你能當場修復該錯誤，否則應該 **Log 並 Re-throw**。

### 3. 混用 Async/Await 與 `.then().catch()`
**Bad:** 在 `async` 函式內部混用 Callback 風格或 Promise chain，卻沒有正確 return 或 await，導致錯誤無法被外層的 `try/catch` 捕獲。
**Pitfall:** 忘記在 `try` block 裡面加 `await`。
```javascript
async function bad() {
  try {
    return apiCall(); // 如果 apiCall 失敗，這裡不會 catch 到，而是回傳一個 rejected Promise
  } catch (e) {
    // 這裡永遠不會執行
  }
}
// Fix: return await apiCall();
```

### 4. 在生產環境洩漏敏感資訊
**Bad:** 直接將 `err.stack` 或 `err.message` 回傳給前端 API Client。
**Why:** 駭客可以看到你的資料庫結構、檔案路徑等資訊。對外應只回傳通用訊息（如 "Internal Server Error"）與 Error ID。

---

## Checklists & workflows｜檢查清單與流程

### 🛡️ Error Handling Checklist (開發階段)
- [ ] **類型檢查**：我是否拋出了 `Error` 物件而非字串？
- [ ] **邊界處理**：所有的 Promise 是否都有 `.catch()` 或被 `try/catch` 包裹？
- [ ] **資訊安全**：錯誤訊息是否過濾了敏感資料（Token, SQL query, PII）？
- [ ] **可追蹤性**：Log 中是否包含足夠的 Context（User ID, Request ID, Input params）？
- [ ] **清理資源**：在 `finally` 區塊中，是否有釋放 DB 連線或 File handle？

### 🐞 Debugging Workflow (除錯流程)
當遇到 Bug 時，依照此決策樹行動：

1.  **Reproduce (重現)**：
    *   能否在本地端穩定重現？
    *   如果是偶發（Flaky），檢查 Race Condition 或外部依賴狀態。
2.  **Isolate (隔離)**：
    *   使用 **二分法（Binary Search）** 註解掉一半程式碼，確認問題區塊。
    *   確認輸入資料（Input）是否符合預期。
3.  **Trace (追蹤)**：
    *   **Node.js**: 使用 `node --inspect` 配合 Chrome DevTools 或 VS Code Debugger。不要只靠 `console.log`。
    *   **Browser**: 使用 `debugger;` 指令暫停執行，檢查 Scope 變數。
    *   檢查 Network Tab 的 Response Body（往往錯誤細節藏在 HTTP 500 的回應裡）。
4.  **Fix & Test (修復與測試)**：
    *   修復後，撰寫一個 **Regression Test（回歸測試）** 確保此 Bug 不會再次出現。

---

## Real-world examples｜實戰案例

### 案例 1：強健的 Fetch Wrapper (Robust Fetch)
處理 `fetch` API 的常見陷阱：HTTP 4xx/5xx 不會 throw error，只有網路斷線才會。

```javascript
class HttpError extends Error {
  constructor(response) {
    super(`HTTP Error: ${response.status} ${response.statusText}`);
    this.response = response;
    this.status = response.status;
  }
}

async function secureFetch(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    // Fetch 只有在網路斷線時才會 throw，所以要手動檢查 ok 狀態
    if (!response.ok) {
      // 嘗試讀取後端回傳的錯誤詳情
      const errorBody = await response.json().catch(() => null);
      const error = new HttpError(response);
      error.body = errorBody;
      throw error;
    }

    return await response.json();
  } catch (error) {
    // 區分是網路錯誤還是 HTTP 狀態錯誤
    if (error instanceof HttpError) {
      console.error(`API Error [${error.status}]:`, error.body);
      // 可以在這裡做 Token Refresh 邏輯 (如果是 401)
    } else {
      console.error('Network/Parsing Error:', error);
    }
    throw error; // Re-throw 讓 UI 層處理顯示
  }
}
```

### 案例 2：全域未捕獲錯誤處理 (Node.js Last Resort)
當所有防護網都失效時，這是最後一道防線，確保 Process 結束前能留下遺言（Log）。

```javascript
// 處理未被 catch 的 Promise Rejection
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // 最佳實務：記錄後重啟 Process，因為應用程式可能處於未定義狀態
  process.exit(1);
});

// 處理同步程式碼的未捕獲異常
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception thrown:', error);
  process.exit(1);
});
```

### 案例 3：使用 `debugger` 進行斷點除錯
在複雜的邏輯中，不要寫 10 個 `console.log`。

```javascript
function calculateTotal(items) {
  let total = 0;
  
  items.forEach(item => {
    // 在這裡暫停：瀏覽器 DevTools 會自動開啟並停在這行
    // 你可以 hover 查看 item 的值，或在 Console 執行表達式
    debugger; 
    
    if (item.price && typeof item.price === 'number') {
      total += item.price;
    }
  });
  
  return total;
}
```