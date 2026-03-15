# 非同步程式設計與 Event Loop / Asynchronous Programming & Event Loop

## Mental model｜心智模型

JavaScript 的單執行緒（Single-threaded）特性常被誤解為「一次只能做一件事」，但更精確的理解是：**「一次只能執行一段 JavaScript 程式碼，但瀏覽器（或 Node.js）可以同時處理多件事」**。

要掌握 Event Loop，請建立以下的角色模型：

### 1. The Chef (Call Stack / 主廚)
- **職責**：負責執行當下的程式碼。
- **特性**：只有一個人，一次切一道菜。如果遇到需要等待的事情（如煮湯、烤箱），他不會傻站著等，而是把工作交給外部設備，自己繼續切下一道菜。

### 2. The External Equipment (Web APIs & Node APIs / 外部設備)
- **職責**：處理計時器 (`setTimeout`)、網路請求 (`fetch`)、DOM 事件。
- **特性**：這些是在 JavaScript 引擎 **之外** 運行的。當它們完成工作（時間到、資料回傳），會把結果（Callback）丟進「待辦清單」。

### 3. The Queues (待辦清單)
這是最容易搞混的地方，待辦清單其實有兩條，且有嚴格的優先順序：

1.  **Microtask Queue (微任務佇列 / VIP 通道)**
    - **成員**：`Promise.then/catch/finally`, `queueMicrotask`, `MutationObserver`。
    - **規則**：**優先級最高**。只要這個隊伍裡還有人，主廚（Event Loop）絕對不會去理會一般通道。這意味著無限迴圈的 Promise 會卡死整個頁面。
2.  **Macrotask Queue (Task Queue / 一般通道)**
    - **成員**：`setTimeout`, `setInterval`, `setImmediate` (Node), I/O, UI Rendering。
    - **規則**：只有當 (1) Call Stack 空了 **且** (2) Microtask Queue 也空了，Event Loop 才會從這裡拿 **一個** 任務去執行。

> **The Golden Rule**: Event Loop 的工作就是不斷檢查 Call Stack 是否為空。如果空了，先清空所有的 Microtasks，然後再執行一個 Macrotask，接著再檢查 Microtasks... 如此循環。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 並行處理 vs 序列處理 (Parallel vs. Serial)
不要因為使用了 `async/await` 就把所有東西都寫成序列（Serial）。

- **Bad (Serial Waterfall)**: 互相不依賴的請求卻依序等待。
  ```javascript
  // 總耗時 = userTime + postsTime
  const user = await getUser(id);
  const posts = await getPosts(id);
  ```

- **Good (Parallel)**: 使用 `Promise.all` 同時發出請求。
  ```javascript
  // 總耗時 = max(userTime, postsTime)
  const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
  ```

- **Better (Fail-safe Parallel)**: 使用 `Promise.allSettled`，避免其中一個失敗導致全部炸裂。
  ```javascript
  const results = await Promise.allSettled([taskA(), taskB()]);
  // results[0].status === 'fulfilled' or 'rejected'
  ```

### 2. 處理 Race Condition (競態條件)
在前端搜尋或 Tab 切換功能中，舊的請求比新的請求晚回來是常見 Bug。

- **Pattern**: 使用 `AbortController` 取消過期的請求。
  ```javascript
  let currentController = null;

  async function search(query) {
    // 1. 取消上一次還沒完成的請求
    if (currentController) currentController.abort();
    
    // 2. 建立新的 controller
    currentController = new AbortController();
    
    try {
      const res = await fetch(`/api/search?q=${query}`, {
        signal: currentController.signal
      });
      const data = await res.json();
      render(data);
    } catch (err) {
      if (err.name === 'AbortError') {
        // 這是被我們主動取消的，忽略它
        return;
      }
      handleError(err);
    }
  }
  ```

### 3. 限制並發數量 (Concurrency Control)
當需要處理大量請求（例如上傳 100 張圖片）時，`Promise.all` 會瞬間發出所有請求，可能導致瀏覽器卡頓或後端崩潰。應使用 `p-limit` 或自製 Semaphore 模式限制同時執行數。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `forEach` Async Trap
`Array.prototype.forEach` 不支援 `async/await`。它會直接發射所有 callback 然後立刻結束，不會等待它們完成。

- **Wrong**:
  ```javascript
  async function saveAll(items) {
    items.forEach(async (item) => {
      await saveToDb(item); // 這裡的 await 對 saveAll 函式無效
    });
    console.log('Done'); // 這行會比 saveToDb 更早執行！
  }
  ```
- **Right**: 使用 `for...of` (序列執行) 或 `Promise.all` + `map` (並行執行)。
  ```javascript
  // 序列
  for (const item of items) { await saveToDb(item); }
  
  // 並行
  await Promise.all(items.map(item => saveToDb(item)));
  ```

### 2. Promise Constructor Anti-pattern
不要將已經是 Promise 的東西再包一層 `new Promise`。這被稱為 "Explicit Promise Construction Antipattern"。

- **Wrong**:
  ```javascript
  function getData() {
    return new Promise((resolve, reject) => {
      fetch('/api').then(res => resolve(res)).catch(err => reject(err));
    });
  }
  ```
- **Right**:
  ```javascript
  function getData() {
    return fetch('/api');
  }
  ```

### 3. 遺失的錯誤處理 (Swallowed Errors)
在 Promise 鏈中沒有 `catch`，或者在 async function 中沒有 `try/catch` 且沒有全域處理，會導致 "Unhandled Promise Rejection"。

- **Pitfall**: 在 `setTimeout` 內部的錯誤無法被外部的 `try/catch` 捕獲。
  ```javascript
  try {
    setTimeout(() => {
      throw new Error('Boom'); // 這裡炸掉，catch 抓不到
    }, 1000);
  } catch (e) { ... }
  ```

---

## Checklists & workflows｜檢查清單與流程

### Async Logic Review Checklist
- [ ] **並行性檢查**：這幾個 `await` 之間有依賴關係嗎？如果沒有，是否改用了 `Promise.all`？
- [ ] **迴圈陷阱**：是否在 `forEach` 或 `map` 裡面使用了 `await` 但沒有正確處理回傳的 Promise？
- [ ] **錯誤邊界**：是否使用了 `try/catch` 或 `.catch()`？如果請求失敗，UI 會停在 Loading 狀態還是顯示錯誤訊息？
- [ ] **競態條件**：如果使用者快速連續觸發這個 async function（例如快速點擊分頁），程式會不會顯示錯誤的（舊的）資料？
- [ ] **記憶體洩漏**：如果在 async 操作完成前 Component Unmount 了，是否會嘗試更新 State？(React 中常見警告)

### Decision Tree: Choosing the Right Tool
1. **需要等待多個非同步任務？**
   - 全部都要成功才算成功？ -> `Promise.all`
   - 只要有一個成功就好（例如多個 CDN 來源）？ -> `Promise.any`
   - 不管成功失敗都要等全部跑完？ -> `Promise.allSettled`
   - 誰最快回來就用誰（包含失敗）？ -> `Promise.race` (小心使用)

2. **需要處理大量數據？**
   - 順序重要嗎？
     - 是 -> `for...of` loop with `await`
     - 否 -> `Promise.all` (搭配 Concurrency Limit)

---

## Real-world examples｜實戰案例

### 1. Event Loop 優先級面試題解析
這不僅是面試題，更是除錯時理解程式執行順序的關鍵。

```javascript
console.log('1. Script start');

setTimeout(() => {
  console.log('2. Macrotask (setTimeout)');
}, 0);

Promise.resolve().then(() => {
  console.log('3. Microtask (Promise)');
}).then(() => {
  console.log('4. Microtask (Promise chain)');
});

console.log('5. Script end');
```

**執行順序與原因：**
1. `1. Script start` (同步程式碼)
2. `5. Script end` (同步程式碼)
3. **Call Stack 清空，檢查 Microtasks**
4. `3. Microtask (Promise)`
5. `4. Microtask (Promise chain)` (前一個 then 產生的新 Microtask)
6. **Microtasks 清空，檢查 Macrotasks**
7. `2. Macrotask (setTimeout)`

### 2. 實作一個帶有重試機制的 Fetch (Retry Pattern)
在網路不穩定的環境（如行動裝置），這是一個非常實用的 Pattern。

```javascript
async function fetchWithRetry(url, options = {}, retries = 3, backoff = 300) {
  try {
    return await fetch(url, options);
  } catch (err) {
    if (retries <= 1) throw err;
    
    // 等待一段時間後重試 (Exponential Backoff 也是常見做法)
    await new Promise(r => setTimeout(r, backoff));
    
    return fetchWithRetry(url, options, retries - 1, backoff * 2);
  }
}

// Usage
// fetchWithRetry('/api/data').then(...).catch(...)
```

### 3. 解決 React `useEffect` 中的 Race Condition
這是在 React 開發中最常遇到的非同步問題。

```javascript
useEffect(() => {
  let ignore = false; // Flag to track if component is unmounted or re-run

  async function fetchData() {
    const result = await someAsyncApi(id);
    if (!ignore) {
      setData(result); // 只有在沒有被忽略時才更新 state
    }
  }

  fetchData();

  return () => {
    ignore = true; // Cleanup function runs before next effect or unmount
  };
}, [id]);
```