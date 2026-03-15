# 故障排除與除錯流程 / Troubleshooting & Debugging Workflow

在 Express 應用程式的維運中，我們常面臨三大魔王：**記憶體洩漏 (Memory Leaks)**、**請求掛起 (Hanging Requests)** 與 **不明的 500 錯誤**。本章節不談基礎語法，而是提供一套標準化的排查協定，協助你將「黑盒子」變成透明的「玻璃盒子」。

## Mental model｜心智模型

要有效地除錯 Express，你必須建立以下的心智模型：

1.  **洋蔥模型與中斷點 (The Onion & The Breakpoint)**
    Express 的 Middleware 機制就像洋蔥。請求掛起通常是因為洋蔥的某一層「忘記剝開下一層」（忘記呼叫 `next()`）或是「剝開了但沒有回應」（沒有 `res.send`）。除錯時，你需要定位請求是在哪一層 Middleware 停滯的。

2.  **單執行緒的阻塞 (The Single Thread Blockage)**
    Node.js 是單執行緒的。如果你的 Express 伺服器對所有請求都沒有回應（而不僅僅是單一請求），通常意味著 Event Loop 被阻塞了（CPU 密集運算或同步 I/O），或者 Garbage Collection (GC) 正在瘋狂運作（記憶體洩漏的前兆）。

3.  **錯誤的傳遞鏈 (The Error Propagation Chain)**
    錯誤必須被顯式地傳遞。在 Async/Await 時代，一個沒有 `catch` 且沒有傳遞給 `next(err)` 的 Promise Rejection，是導致請求掛起或 Process Crash 的主因。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 `debug` 模組進行命名空間除錯
不要在生產環境依賴 `console.log`。Express 內部使用 `debug` 模組。
- **Practice**: 在啟動時使用環境變數 `DEBUG=express:router,express:application node app.js` 可以看到路由匹配的詳細過程。
- **Custom**: 為你自己的模組建立命名空間：`const debug = require('debug')('app:users')`。

### 2. 關聯 ID (Correlation IDs)
在微服務或高併發環境下，單純看 Log 很難追蹤單一請求的流向。
- **Pattern**: 使用 `express-request-id` 或自製 Middleware，在每個請求進來時生成一個 UUID，並將其附加到 `req` 物件與 Response Header (`X-Request-ID`)。
- **Log**: 所有的 Log 輸出都必須包含這個 ID。

### 3. 記憶體快照比對 (Heap Snapshot Comparison)
面對 Memory Leak，猜測是無效的。
- **Tooling**: 使用 Chrome DevTools 連接 Node 實體 (`node --inspect`)。
- **Workflow**:
    1. 啟動伺服器，強制執行一次 GC，拍下 **Snapshot A**。
    2. 執行負載測試 (Load Test) 模擬大量請求。
    3. 再次強制 GC，拍下 **Snapshot B**。
    4. 比較 B 與 A，尋找 **Detached DOM** (在 Node 中通常是 Detached Objects) 或異常增長的 Array/Map。

### 4. 針對 Hanging Requests 的超時防護
永遠假設網路會斷、資料庫會鎖死。
- **Pattern**: 設定 `server.setTimeout` (Socket 層級) 與 `connect-timeout` (Middleware 層級)。
- **Goal**: 寧可回傳 503 Service Unavailable，也不要讓客戶端無限轉圈圈，這會耗盡 Server 的連線數。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Black Hole" Middleware (黑洞 Middleware)
最常見的掛起原因。
```javascript
// ❌ Anti-pattern
app.use((req, res, next) => {
  if (req.header('x-token')) {
    next();
  }
  // 如果沒有 token，這裡什麼都沒做，請求會永遠掛著直到 timeout
});

// ✅ Correct
app.use((req, res, next) => {
  if (req.header('x-token')) {
    return next();
  }
  res.status(401).send('No token'); // 必須終結請求或呼叫 next(err)
});
```

### 2. 吞噬錯誤 (Swallowing Errors)
在 Async 函式中 catch 了錯誤卻不處理。
```javascript
// ❌ Anti-pattern
app.get('/data', async (req, res, next) => {
  try {
    const data = await db.getData();
    res.json(data);
  } catch (e) {
    console.log(e); // 只有印出 log，Client 端仍在等待回應
  }
});
```

### 3. 在 Request Handler 中註冊 Event Listener
這是導致 **Memory Leak** 的經典原因。
```javascript
// ❌ Anti-pattern
app.get('/stream', (req, res) => {
  const stream = getSomeStream();
  // 每次請求都會對 globalBus 註冊一個新的 listener
  // 請求結束後 listener 並未移除，導致 closure 內的 req/res 無法被回收
  globalBus.on('data', (data) => {
    res.write(data);
  });
});
```

---

## Checklists & workflows｜檢查清單與流程

### 🚨 請求掛起排查流程 (Hanging Request Workflow)

- [ ] **檢查 Middleware 鏈**：是否所有路徑都有 `return next()` 或 `res.send()`？特別檢查 `if/else` 的邊界條件。
- [ ] **檢查 Async/Await**：是否有 `await` 了一個永遠不會 resolve 的 Promise？
- [ ] **檢查資料庫鎖 (DB Locks)**：查詢是否被 DB Transaction 鎖死？
- [ ] **檢查 Event Loop**：使用 `clinic doctor` 檢查 Event Loop 延遲。如果延遲很高，代表有同步程式碼阻塞了主執行緒。

### 🚨 記憶體洩漏排查清單 (Memory Leak Checklist)

- [ ] **Global Variables**：是否將 User Session 或 Cache 存放在全域變數 (Global Map/Array) 中且沒有清理機制？
- [ ] **Event Emitters**：是否有在 Request 生命週期內 `on()` 卻沒有 `off()` 或 `once()`？
- [ ] **Closures**：是否有 Timer (`setInterval`) 引用了 `req` 物件導致無法回收？
- [ ] **Dependencies**：檢查 `package.json`，是否有已知的 leaky library (如舊版的某些 XML parser)。

### 🚨 500 錯誤排查流程 (500 Error Workflow)

- [ ] **重現步驟**：能否用 `curl` 穩定重現？
- [ ] **Log 分析**：
    - 尋找 `Error: ...` 的 Stack Trace。
    - 檢查發生錯誤前的最後一條 Log (定位發生在哪個 Middleware)。
- [ ] **環境變數**：檢查 `NODE_ENV` 與 Config 是否讀取正確（常見於連線字串錯誤）。
- [ ] **輸入驗證**：是否因為惡意或異常的 Payload (如極大的 JSON) 導致 parser 崩潰？

---

## Real-world examples｜實戰案例

### 案例一：被遺忘的 `return` 導致的 "Headers Sent" 錯誤

這不是掛起，但常與除錯掛起時混淆。

```javascript
// ❌ 錯誤範例
app.get('/user/:id', async (req, res, next) => {
  const user = await db.findUser(req.params.id);
  if (!user) {
    res.status(404).send('Not found');
    // 這裡忘記 return，程式會繼續往下執行
  }
  
  // 這裡會再次嘗試發送回應，導致 "Error [ERR_HTTP_HEADERS_SENT]: Cannot set headers after they are sent to the client"
  // 這會讓 Log 充滿雜訊，掩蓋真正的問題
  res.json(user);
});
```

### 案例二：使用 `clinic.js` 定位效能瓶頸

當 Express 伺服器回應變慢，但沒有報錯時：

1.  **安裝工具**：`npm install -g clinic`
2.  **執行診斷**：
    ```bash
    clinic doctor --on-port 'autocannon -c 100 localhost:3000' -- node app.js
    ```
3.  **分析報告**：
    - 如果 **Event Loop Delay** 很高，但 **CPU Usage** 低：可能是外部 I/O (DB/API) 等待過久。
    - 如果 **Event Loop Delay** 高 且 **CPU Usage** 高：你的程式碼中有同步的密集運算（例如在主執行緒進行大型 JSON parse 或加密運算）。
    - 解決方案：將密集運算移至 Worker Threads 或優化演算法。

### 案例三：不明的 Promise Rejection

Node.js 舊版本會忽略 Unhandled Rejection，新版本會直接 Crash。

```javascript
// 在 app.js 最上層加入此監聽器，捕捉漏網之魚
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // 建議：記錄 Log 後優雅重啟 Server，因為此時 App 狀態可能已不穩定
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});
```