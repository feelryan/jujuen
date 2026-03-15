# 非同步編程實戰與錯誤處理 / Asynchronous Programming & Error Handling

## Mental model｜心智模型

在 Node.js 中掌握非同步，關鍵在於理解 **「控制權的交接 (Handover of Control)」** 與 **「錯誤的傳遞路徑 (Error Propagation Path)」**。

### 1. The Ticket System (廚房點單模型)
不要將 Node.js 想像成一個多工處理的 CPU，請把它想像成一間 **只有一位主廚（Single Thread）的繁忙餐廳**。
- **Blocking (阻塞)**：主廚親自跑去種菜、收割，導致沒人做菜。
- **Non-blocking (非阻塞)**：主廚把「種菜」的任務外包給供應商（OS Kernel / Libuv Thread Pool），拿到一張「提貨單（Promise）」，然後繼續做下一道菜。
- **Await**：主廚暫停手邊動作，盯著供應商直到拿到菜（在語法上暫停，但 Event Loop 仍可處理其他請求）。

### 2. The Bubble Up Effect (錯誤冒泡效應)
在同步程式碼中，錯誤會沿著 Call Stack 向上拋出；在 Async/Await 中，錯誤依然遵循此規則，但如果中間斷了鏈（例如使用了 Callback 卻沒接 error，或是 Floating Promise），錯誤就會像氣球飄進外太空（Unhandled Rejection），導致 Process 崩潰或狀態不一致。

> **Core Principle**: Always return the Promise or await it. If you break the chain, you lose the context.
> **核心原則**：永遠要回傳 Promise 或使用 await。一旦鏈條斷裂，你將失去執行的上下文與錯誤捕捉的機會。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Concurrency Control (並發控制)
不要無腦 `await`，也不要無腦 `Promise.all`。
- **Sequential (`for...of` + `await`)**: 當後一個請求依賴前一個請求的結果時使用。
- **Parallel (`Promise.all`)**: 當多個請求互不相關，且需要「全部成功」才算成功（Fail-fast）。
- **Resilient Parallel (`Promise.allSettled`)**: 當多個請求互不相關，且容許部分失敗（例如：發送 10 封 Email，失敗 1 封不該影響其他 9 封）。

### 2. The "Async/Await" Wrapper for Express/Connect
在 Express v4 或舊版框架中，Async 函數拋出的錯誤無法被預設的 Error Handler 捕捉。
- **Pattern**: 使用 Wrapper 函數或庫（如 `express-async-errors`）確保 `catch` 能夠傳遞到 `next(err)`。
- **Modern Node**: 在 Node.js 原生 HTTP server 或 Fastify、NestJS 中，這已通常被內建處理，但理解原理至關重要。

### 3. Graceful Cancellation with AbortController
現代 Node.js (v15+) 支援標準的 `AbortController`。
- **Scenario**: 當使用者取消請求，或請求超時，應該停止後端的重運算或 DB 查詢。
- **Practice**: 將 `signal` 傳遞給 `fetch`、DB client 或檔案操作。

```javascript
// Example: Timeout Pattern using AbortController
async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 8000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(resource, { ...options, signal: controller.signal });
    return response;
  } finally {
    clearTimeout(id); // Clean up timer
  }
}
```

### 4. Operational vs. Programmer Errors
區分「可預期的操作錯誤」與「程式邏輯錯誤」。
- **Operational Errors**: 用戶輸入錯誤、DB 連線暫時失敗、外部 API 503。 **策略：Catch, Log, Retry, or User Feedback.**
- **Programmer Errors**: 變數未定義、語法錯誤、參數型別錯誤。 **策略：Crash (Let it fail), Fix code, Restart process.**

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `forEach` Trap (forEach 陷阱)
`Array.prototype.forEach` 不支援 async/await。它會啟動所有的 Promises 但不會等待它們完成，導致程式流程在資料處理完之前就繼續執行。

- **Bad**:
  ```javascript
  // ❌ The console.log runs before items are saved
  items.forEach(async (item) => {
    await saveItem(item);
  });
  console.log('Done'); 
  ```
- **Good**: 使用 `for...of` (序列執行) 或 `Promise.all` + `map` (並行執行)。

### 2. Floating Promises (懸浮 Promise)
呼叫了 async 函數卻沒有 `await` 它，也沒有 `.catch()` 它。這會導致 Race Condition，且錯誤發生時無人知曉（Unhandled Rejection）。

- **Bad**: `db.update({ id }, data); // Fire and forget? Dangerous.`
- **Good**: `void db.update({ id }, data).catch(logError); // Explicitly ignored await but handled error.`

### 3. Try/Catch Hell (巢狀錯誤處理地獄)
過度使用 try/catch 包裹每一行 async 代碼，導致代碼難以閱讀且錯誤處理邏輯分散。

- **Fix**: 在 Controller 最上層或使用 Middleware 進行統一錯誤捕捉。讓錯誤自然冒泡（Bubble up）到邊界處理。

### 4. Mixing Callbacks and Promises
在同一個函數中混用 `cb(err, result)` 和 `return new Promise(...)`，容易造成重複呼叫 callback 或 Promise resolve 兩次。
- **Fix**: 使用 `util.promisify` 將舊式 Callback API 轉為 Promise，保持風格一致。

---

## Checklists & workflows｜檢查清單與流程

### Async Code Review Checklist
在提交 PR 或進行 Code Review 時，請檢查以下項目：

- [ ] **Loop Check**: 是否在 `forEach` 中使用了 `await`？（如果是，請改用 `map` 或 `for...of`）
- [ ] **Parallelism**: 這些連續的 `await` 之間有依賴關係嗎？如果沒有，是否該用 `Promise.all`？
- [ ] **Error Handling**: 所有的 Promise 鏈是否有 `catch` 區塊，或是被 `try/catch` 包裹？
- [ ] **Return Value**: Async 函數是否回傳了預期的值？（避免意外回傳 Promise 物件給 Client）
- [ ] **Resource Leak**: 是否在 `finally` 區塊中釋放了資源（如 DB 連線、File Handle）？
- [ ] **Swallowed Errors**: `catch` 區塊中是否只是 `console.log` 而沒有 `throw` 或妥善處理？（這會導致呼叫者誤以為成功）

### Decision Tree: Sequential vs. Parallel
1. **Does Task B need data from Task A?**
   - **Yes**: Use `await TaskA(); await TaskB();` (Sequential)
   - **No**: Go to step 2.
2. **Are there huge number of tasks (e.g., > 100)?**
   - **Yes**: Use a concurrency limit library (e.g., `p-limit` or `async.mapLimit`) to avoid memory spikes.
   - **No**: Use `Promise.all([TaskA(), TaskB()])`.

---

## Real-world examples｜實戰案例

### Scenario: User Dashboard Aggregation (使用者儀表板聚合)

**情境**：你需要為使用者的首頁載入：1. 基本資料、2. 最近訂單、3. 推薦商品。這三個來源來自不同的 Microservices 或 DB Tables。

#### ❌ Anti-pattern: Serial Execution (Slow)
使用者必須等待三個請求依序完成，總耗時 = T1 + T2 + T3。

```javascript
async function getDashboard(userId) {
  try {
    const user = await getUser(userId);       // Wait 100ms
    const orders = await getOrders(userId);   // Wait 200ms
    const recs = await getRecommendations();  // Wait 150ms
    // Total: 450ms
    return { user, orders, recs };
  } catch (err) {
    throw new AppError('Dashboard load failed', 500, err);
  }
}
```

#### ✅ Best Practice: Concurrent Execution with Resilience (Fast & Robust)
並行執行，總耗時 = Max(T1, T2, T3)。且使用 `Promise.allSettled` 容許「推薦商品」失敗而不影響主頁面顯示。

```javascript
async function getDashboard(userId) {
  // Start all tasks immediately
  const userPromise = getUser(userId);
  const ordersPromise = getOrders(userId);
  const recsPromise = getRecommendations(); // Non-critical

  // Critical Data: Must succeed
  const [user, orders] = await Promise.all([userPromise, ordersPromise]);

  // Non-critical Data: Can fail
  const recsResult = await Promise.allSettled([recsPromise]);
  const recs = recsResult[0].status === 'fulfilled' ? recsResult[0].value : [];

  // Total: ~200ms (Bottleneck is orders)
  return { user, orders, recs };
}
```

### Scenario: Batch Data Processing with Concurrency Limit

**情境**：需要處理 10,000 筆資料的更新，如果直接 `Promise.all` 會導致 Database 連線數耗盡 (Connection Pool Exhaustion) 或 API Rate Limit。

```javascript
import pLimit from 'p-limit'; // Popular utility for concurrency control

async function processBatch(items) {
  const limit = pLimit(10); // Only run 10 promises at once
  
  const input = items.map(item => {
    return limit(async () => {
      try {
        return await db.updateItem(item);
      } catch (err) {
        // Log error but keep processing other items
        logger.error(`Failed to update item ${item.id}`, err);
        return { id: item.id, status: 'failed', error: err.message };
      }
    });
  });

  // Wait for all to finish (managed by limit)
  const results = await Promise.all(input);
  return results;
}
```