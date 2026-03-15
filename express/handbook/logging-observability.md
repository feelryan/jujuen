# 日誌記錄與可觀測性實踐 / Logging & Observability Practices

## Mental model｜心智模型

在 Express 應用程式中，日誌（Logging）不應該只是「把文字印在終端機上」，而應該被視為 **「事件流（Stream of Events）」** 與 **「請求的故事線（Storyline of a Request）」**。

### 1. The "Black Box" vs. "Glass Cockpit"
想像你的伺服器是一個黑盒子。
- **Console.log** 就像是在盒子外面隨意貼便利貼，雜亂無章且難以搜尋。
- **Structured Logging (結構化日誌)** 則是飛機的「玻璃駕駛艙（Glass Cockpit）」，每一個儀表數據（Log 欄位）都有固定的位置與格式（JSON），讓機器（如 ELK, Datadog, CloudWatch）能夠解析、索引並繪製圖表。

### 2. The Trace Context (追蹤上下文)
Express 是非同步且單執行緒的（Asynchronous & Single-threaded）。當多個請求同時進入時，它們的 Log 會在時間軸上交錯。
- **Mental Image**: 想像一團打結的耳機線。
- **Solution**: 給每一條線（Request）綁上一個獨一無二的顏色標籤（**Correlation ID / Request ID**）。無論這條線經過 Middleware、Controller 還是 Service 層，這個標籤都必須跟著走，這樣你才能把散落的 Log 串成一個完整的故事。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Structured Logging is Non-Negotiable (結構化日誌是必須的)
在生產環境中，**不要使用純文字 Log**。人類讀文字，機器讀 JSON。
- **Pattern**: 使用 `Winston` 或 `Pino` 並配置 JSON Transport。
- **Why**: 當你需要搜尋 `level="error" AND context="payment-service"` 時，純文字 Log 會讓你崩潰。

### 2. Correlation ID / Request ID Middleware
在請求進入系統的第一個瞬間（Entry Point），就賦予它一個 ID。
- **Implementation**:
  1.  檢查 Header 是否已有 `X-Request-ID`（來自 Load Balancer 或上游服務）。
  2.  如果沒有，生成一個 UUID。
  3.  將此 ID 掛載到 `req.id` 或 `res.locals.requestId`。
  4.  **關鍵點**：所有的 Log 輸出都必須包含這個 ID。

### 3. Integrating Morgan with Winston (Http Log 整合)
`Morgan` 擅長記錄 HTTP 流量，`Winston` 擅長應用程式邏輯 Log。兩者應該結合。
- **Pattern**: 建立一個 `stream` 介面，讓 Morgan 把 Log 寫入 Winston，而不是直接寫入 `process.stdout`。這樣你的 HTTP Log 也會變成統一的 JSON 格式。

### 4. Context Propagation with AsyncLocalStorage (進階上下文傳遞)
為了避免在每個函數都傳遞 `req` 物件只為了拿 `logger` 或 `requestId`，Node.js 提供了 `AsyncLocalStorage`。
- **Pattern**: 在 Middleware 初始化 store，存入 `requestId`。在 Service 層深處，你可以直接從 store 拿 ID，而不需要修改函數簽名（Function Signature）。

### 5. Log Levels Strategy (日誌級別策略)
嚴格區分 Log Level，避免雜訊淹沒訊號。
- **ERROR**: 系統崩潰、DB 連線失敗、未預期的 Exception。**需要有人立即處理**。
- **WARN**: 棄用的 API 被呼叫、重試操作發生、非致命的錯誤。**需要被關注，但不需半夜叫醒人**。
- **INFO**: 關鍵業務流程完成（如：訂單建立成功）、系統啟動。**用於追蹤正常行為**。
- **DEBUG**: Payload 內容、變數狀態。**僅在開發或除錯特定問題時開啟**。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `console.log` Trap (同步阻塞陷阱)
- **Anti-pattern**: 在生產環境大量使用 `console.log` 或 `console.error`。
- **Why**: `console.log` 在 Node.js 中寫入 stdout/stderr 某些情況下是**同步（Synchronous）且阻塞（Blocking）**的。在高併發下，這會嚴重拖慢 Event Loop。
- **Fix**: 使用非同步的 Logger library（如 Pino/Winston）。

### 2. Logging Sensitive Data (洩漏敏感資訊)
- **Anti-pattern**: 直接 Log 整個 `req.body`。
- **Risk**: 使用者的密碼、信用卡號、PII（個資）會被寫入 Log 系統，造成嚴重的合規問題（GDPR/HIPAA）。
- **Fix**: 實作 **Redaction (資料遮罩)** 機制，自動過濾 `password`, `token`, `creditCard` 等欄位。

### 3. The "Mega-Object" Log (巨型物件日誌)
- **Anti-pattern**: `logger.info(req)`。
- **Why**: `req` 物件包含巨大的 Circular References（循環參照）和大量無用資訊（Socket details）。這會導致 `JSON.stringify` 失敗或 Log 體積爆炸。
- **Fix**: 只 Log 你需要的欄位，或使用 Serializers（序列化器）來提取 `req` 的關鍵資訊（method, url, headers, id）。

### 4. Error Swallowing (吞噬錯誤)
- **Anti-pattern**:
  ```javascript
  try { ... } catch (e) { logger.error('Something went wrong'); }
  ```
- **Why**: 你丟失了 `Stack Trace` 和原始錯誤訊息 `e.message`。
- **Fix**: 總是 Log 錯誤物件：`logger.error('Order failed', { error: e })`。

---

## Checklists & workflows｜檢查清單與流程

### Production Readiness Checklist (生產環境準備清單)

- [ ] **Format**: Log 輸出格式是否已設為 JSON？
- [ ] **Correlation**: 每個 Request 是否都有唯一的 `trace_id` / `request_id`？
- [ ] **Transport**: Log 是否輸出到 `stdout`（容器化標準做法）而非寫死在本地檔案？
- [ ] **Levels**: 生產環境的 Log Level 是否設為 `INFO`（避免 DEBUG 雜訊）？
- [ ] **Security**: 是否已配置 Redaction/Sanitization 來過濾敏感欄位（密碼、Token）？
- [ ] **Error Handling**: 全域錯誤處理器（Global Error Handler）是否會記錄完整的 Stack Trace？
- [ ] **HTTP Logs**: 是否整合了 Morgan/Pino-http 來記錄每個 HTTP 請求的狀態碼與回應時間？

### Debugging Workflow (除錯流程)

1. **Trigger**: 收到警報或用戶回報錯誤。
2. **Search**: 在 Log 系統中搜尋相關關鍵字（如 User ID 或 Error Message）。
3. **Trace**: 找到一條相關 Log，複製其 `request_id`。
4. **Filter**: 篩選 `request_id == <COPIED_ID>`。
5. **Reconstruct**: 依時間序查看該請求的所有 Log，重建案發現場。

---

## Real-world examples｜實戰案例

### Setup: Winston + Morgan + Correlation ID

這是一個標準的生產環境配置範例，展示如何將 Request ID 貫穿整個 Log 系統。

```javascript
// logger.js
const winston = require('winston');

// 定義敏感欄位過濾
const replacer = (key, value) => {
  if (['password', 'token', 'authorization'].includes(key)) return '[REDACTED]';
  return value;
};

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json({ replacer }) // 強制 JSON 格式並過濾敏感資料
  ),
  defaultMeta: { service: 'user-service' }, // 標記服務名稱
  transports: [new winston.transports.Console()],
});

// 建立一個 stream 給 Morgan 使用
logger.stream = {
  write: (message) => {
    // Morgan 輸出的字串通常包含換行，需去除
    logger.info(message.trim(), { type: 'http-access' });
  },
};

module.exports = logger;
```

```javascript
// app.js
const express = require('express');
const morgan = require('morgan');
const { v4: uuidv4 } = require('uuid');
const logger = require('./logger');

const app = express();

// 1. Request ID Middleware (最先執行)
app.use((req, res, next) => {
  // 優先使用上游傳來的 ID，否則生成新的
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// 2. Morgan HTTP Logging (整合 Winston)
// 定義 Morgan 格式，包含 Trace ID
morgan.token('id', (req) => req.id);
const morganFormat = ':id :method :url :status :response-time ms';

app.use(morgan(morganFormat, { stream: logger.stream }));

// 3. Application Logic
app.get('/api/users/:id', async (req, res, next) => {
  // 在業務邏輯中使用 Logger，並帶上 requestId
  // 注意：這裡手動傳遞 req.id 較繁瑣，進階做法可配合 AsyncLocalStorage
  logger.info('Fetching user details', { 
    requestId: req.id, 
    userId: req.params.id 
  });

  try {
    // 模擬錯誤
    if (req.params.id === '0') throw new Error('Invalid User ID');
    
    res.json({ id: req.params.id, name: 'Alice' });
  } catch (error) {
    next(error);
  }
});

// 4. Global Error Handler
app.use((err, req, res, next) => {
  logger.error(err.message, { 
    requestId: req.id, // 關鍵：錯誤 Log 必須包含 ID
    stack: err.stack,
    url: req.originalUrl 
  });
  
  res.status(500).json({ error: 'Internal Server Error', requestId: req.id });
});

module.exports = app;
```

### Log Output Example (JSON)

當發生錯誤時，你的 Log 系統會收到兩條結構化的紀錄，且可以透過 `requestId` 關聯起來：

```json
// 1. 業務邏輯 Log
{
  "level": "info",
  "message": "Fetching user details",
  "requestId": "a1b2-c3d4-e5f6",
  "userId": "0",
  "service": "user-service",
  "timestamp": "2023-10-27T10:00:00.123Z"
}

// 2. 錯誤 Log
{
  "level": "error",
  "message": "Invalid User ID",
  "requestId": "a1b2-c3d4-e5f6",
  "stack": "Error: Invalid User ID\n    at ...",
  "url": "/api/users/0",
  "service": "user-service",
  "timestamp": "2023-10-27T10:00:00.150Z"
}

// 3. Morgan HTTP Access Log
{
  "level": "info",
  "message": "a1b2-c3d4-e5f6 GET /api/users/0 500 27.5 ms",
  "type": "http-access",
  "service": "user-service",
  "timestamp": "2023-10-27T10:00:00.155Z"
}
```