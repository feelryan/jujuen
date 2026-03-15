# 效能優化與並發處理 / Performance Tuning & Concurrency

## Mental model｜心智模型

要掌握 Express 的效能優化，必須先理解 Node.js 的核心機制：**Single Threaded Event Loop（單執行緒事件迴圈）**。

將 Express 伺服器想像成一間**只有一位櫃檯經理（Main Thread）的餐廳**：

1.  **The Manager (Event Loop)**：這位經理動作極快，負責接收訂單（Request）並將其分派給廚房。只要經理不被卡住，餐廳就能處理成千上萬的併發訂單。
2.  **The Kitchen (Worker Pool / System Kernel)**：負責耗時的工作（如 DB 查詢、檔案讀寫、加密運算）。這些是並行處理的。
3.  **Blocking (阻塞)**：如果經理親自跑去切洋蔥（執行 CPU 密集任務，如複雜運算或同步讀檔），門口排隊的客人（Pending Requests）就會全部卡住，無論廚房有多空閒。

**優化的核心策略只有兩條路：**
1.  **Don't block the manager**：確保 Main Thread 永遠只做輕量級的調度，不做重運算。
2.  **Hire more managers**：透過 Clustering 利用多核心 CPU，開設多個櫃檯（Processes）來分流。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 啟用 Gzip/Brotli 壓縮 (Compression)
這是最廉價且高效的優化手段。大幅減少傳輸的 Payload 大小，降低延遲。

*   **Pattern**: 使用 `compression` middleware。
*   **Note**: 在高流量生產環境中，建議將壓縮工作交由 Reverse Proxy (如 Nginx) 處理，減輕 Node.js CPU 負擔；若無法控制 Proxy，則在 Express 層處理。

```javascript
const compression = require('compression');
const express = require('express');
const app = express();

// 應儘早載入
app.use(compression());
```

### 2. 正確使用非同步與 Promise (Asynchronous Handling)
避免在 Request 處理流程中使用任何 `*Sync` 結尾的函式（如 `fs.readFileSync`）。

*   **Best Practice**: 全面採用 `async/await`，並確保所有 I/O 操作都透過 Promise 處理。
*   **Why**: 同步函式會暫停 Event Loop，直到操作完成，這在伺服器端是致命的。

### 3. 多核心擴展 (Clustering & Process Management)
Node.js 預設只使用單一 CPU 核心。在多核機器上，必須使用 Cluster 模式來最大化吞吐量。

*   **Tool**: 推薦使用 **PM2** 作為 Process Manager，而非手寫 Node.js 原生 `cluster` 模組。
*   **Pattern**: `max` 模式會根據 CPU 核心數自動生成對應數量的 Instances。

```bash
# pm2 ecosystem.config.js example
module.exports = {
  apps: [{
    name: "api-server",
    script: "./app.js",
    instances: "max", // 利用所有 CPU 核心
    exec_mode: "cluster",
    env: {
      NODE_ENV: "production"
    }
  }]
}
```

### 4. 實作快取策略 (Caching Strategies)
最快的 Request 是不需要處理的 Request。

*   **HTTP Caching**: 對於靜態資源或不常變動的 API，設定正確的 `Cache-Control` header。
*   **Application Caching**: 使用 Redis 快取昂貴的資料庫查詢結果。

```javascript
// 簡單的 Redis Cache Pattern 示意
app.get('/heavy-data', async (req, res) => {
  const key = 'heavy-data-key';
  const cached = await redisClient.get(key);
  
  if (cached) {
    return res.json(JSON.parse(cached)); // Cache Hit
  }

  const data = await db.heavyQuery();
  await redisClient.set(key, JSON.stringify(data), 'EX', 3600); // Cache for 1 hour
  res.json(data); // Cache Miss
});
```

### 5. 高效的 JSON 處理
`JSON.parse` 和 `JSON.stringify` 是同步且 CPU 密集的。當物件極大時，會阻塞 Event Loop。

*   **Optimization**: 使用 `fast-json-stringify` 定義 Schema 來加速序列化。
*   **Offloading**: 如果必須處理 MB 等級的 JSON，考慮丟給 Worker Thread 處理。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `console.log` Trap
*   **Anti-pattern**: 在生產環境大量使用 `console.log`。
*   **Why**: `console.log` 在某些環境下（如寫入 TTY）是同步阻塞的，且格式化字串消耗 CPU。
*   **Fix**: 使用高效能的 Logger 函式庫，如 **Pino** 或 **Winston**，並開啟非同步寫入模式。

### 2. Memory Leaks in Closures (閉包記憶體洩漏)
*   **Anti-pattern**: 在 Request Handler 中註冊全域的 Event Listener 或未清除的 `setInterval`。
*   **Consequence**: 每次 Request 都增加一點記憶體佔用，最終導致 OOM (Out of Memory) crash。

### 3. ReDoS (Regular Expression Denial of Service)
*   **Anti-pattern**: 使用巢狀量詞 (Nested Quantifiers) 的正規表達式處理使用者輸入，例如 `(a+)+`。
*   **Consequence**: 惡意輸入可導致 Regex 引擎耗費數秒甚至數分鐘進行回溯 (Backtracking)，完全卡死 Event Loop。
*   **Fix**: 使用 `safe-regex` 檢查，或避免對不可信輸入進行複雜 Regex 匹配。

### 4. Serving Static Files with Express
*   **Anti-pattern**: 使用 `res.sendFile` 或 `express.static` 處理大量高併發的圖片/影片請求。
*   **Fix**: 讓 Nginx 或 CDN 處理靜態檔案。Express 應該專注於處理 API 邏輯。

### 5. Using `MemoryStore` for Sessions
*   **Anti-pattern**: 在生產環境使用 `express-session` 預設的 `MemoryStore`。
*   **Consequence**: 會導致記憶體洩漏，且無法在 Cluster 模式下共享 Session（使用者重新整理後會被登出）。
*   **Fix**: 務必使用 `connect-redis` 或 `connect-mongo`。

---

## Checklists & workflows｜檢查清單與流程

### Performance Audit Checklist (效能審計清單)

- [ ] **Environment Variable**: 確認 `NODE_ENV` 已設為 `production`（這會停用許多開發時的除錯檢查與 View caching，效能差異可達 3 倍）。
- [ ] **Compression**: 確認回應已啟用 Gzip/Brotli 壓縮（檢查 Response Headers）。
- [ ] **Logging**: 確認已移除 `console.log`，並改用結構化 Logger (Pino/Winston) 且設定適當的 Log Level (如 `info` 或 `error`)。
- [ ] **Clustering**: 確認已配置 PM2 或 Cluster Mode 以利用多核心 CPU。
- [ ] **Database Indexing**: 確認所有 API 查詢的 SQL/NoSQL 欄位都已建立索引。
- [ ] **Timeout Handling**: 設定 `server.timeout` 與資料庫連線 Timeout，避免連線無限掛起。
- [ ] **Security/Performance Headers**: 檢查是否移除了 `X-Powered-By: Express`（雖然主要是安全考量，但也節省了幾個 bytes）。
- [ ] **Exceptions**: 確認有全域的 `uncaughtException` 與 `unhandledRejection` 處理機制，避免 Process 意外重啟。

---

## Real-world examples｜實戰案例

### Case 1: The "Event Loop Blocker" (CPU 密集任務分離)

**情境**：一個使用者註冊 API 需要使用 `pbkdf2` 進行密碼雜湊運算。當併發量達到 100 req/s 時，伺服器回應時間從 50ms 暴增至 5s，且無法處理其他簡單的 API 請求。

**問題代碼 (Bad)**：
```javascript
// 即使是 crypto 也有同步版本，這會完全卡死 Event Loop
app.post('/register', (req, res) => {
  const user = req.body;
  const hash = crypto.pbkdf2Sync(user.password, salt, 100000, 64, 'sha512'); // BLOCKING!
  db.saveUser({ ...user, hash });
  res.sendStatus(201);
});
```

**解決方案 (Good)**：
使用非同步版本，讓 Node.js 使用 libuv 的 Thread Pool 處理雜湊，釋放 Event Loop 處理其他請求。

```javascript
app.post('/register', async (req, res, next) => {
  try {
    const user = req.body;
    // 使用 Promise wrapper 或 util.promisify
    const hash = await pbkdf2Async(user.password, salt, 100000, 64, 'sha512'); // Non-blocking
    await db.saveUser({ ...user, hash });
    res.sendStatus(201);
  } catch (err) {
    next(err);
  }
});
```

### Case 2: Scaling with PM2 (零停機部署與擴展)

**情境**：單一 Node.js Process 在 AWS t3.medium (2 vCPU) 上只能吃到 50% 的總 CPU 資源（因為只用了一核），浪費了一半的運算能力。

**解決方案**：
配置 `ecosystem.config.js` 並使用 PM2 的 Reload 功能實現 Zero-downtime deployment。

1.  **Config**: 設定 `instances: "max"`。
2.  **Deploy**: 使用 `pm2 reload api-server` 而不是 `restart`。`reload` 會逐一重啟 instance，確保服務不中斷。

### Case 3: Middleware Overhead (Middleware 的順序與必要性)

**情境**：所有 API 的回應時間都增加了 20ms，經排查發現是一個負責解析 XML Body 的 Middleware 被放在了全域 (`app.use`)，但只有 1% 的 Endpoint 需要 XML。

**優化**：
只在需要的 Route 上掛載特定的 Middleware，而非全域掛載。

```javascript
// Bad: 解析所有請求的 Body，浪費 CPU
app.use(bodyParser.xml());

// Good: 只在特定路由解析
app.post('/legacy-xml-endpoint', bodyParser.xml(), (req, res) => {
  // ...
});
```