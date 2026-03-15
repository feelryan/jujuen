# Express 核心生命週期與 Middleware 機制 / Core Lifecycle & Middleware Mechanics

## Mental model｜心智模型

### 1. The Assembly Line (流水線模型)
不要只把 Express 看作是路由 (Routing) 工具，它本質上是一條 **「請求處理流水線」 (Request Processing Pipeline)**。
- 每一個 Middleware 都是流水線上的一個工作站。
- `req` (Request) 和 `res` (Response) 是在這個流水線上傳遞的物件。
- `next` 是一個控制開關，決定是否將工件傳送到下一個工作站。

### 2. The Onion Model vs. The Stack (洋蔥模型 vs. 堆疊)
雖然 Koa 強調洋蔥模型（回頭執行），但在 Express 中，更適合將其想像為一個 **FIFO Stack (先進先出堆疊)**，但有一個關鍵例外：**錯誤處理 (Error Handling)**。
- **Normal Flow**: Request 進入 -> Global Middleware -> Router Middleware -> Route Handler -> Response Sent.
- **Error Flow**: 一旦呼叫 `next(err)`，Express 會跳過所有標準 Middleware，直接尋找下一個定義了 `(err, req, res, next)` 的 Error Handler。

### 3. The "Traffic Cop" (交通指揮)
`next()` 是交通指揮。
- `next()`: "綠燈，繼續走。"
- `next(new Error(...))`: "紅燈，發生事故，切換到緊急車道 (Error Handling Middleware)。"
- 不呼叫 `next()` 也不呼叫 `res.send()`: "塞車，請求會掛起 (Hanging) 直到 Timeout。"

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Always `return` next()
為了避免在觸發下一個 Middleware 後繼續執行當前函式的程式碼，養成習慣加上 `return`。
To prevent code execution after passing control, always use `return`.

```javascript
// ✅ Good Pattern
app.use((req, res, next) => {
  if (!req.headers['authorization']) {
    return next(new Error('Unauthorized')); // Stop execution here
  }
  return next(); // Explicitly pass control
});

// ❌ Bad Pattern
app.use((req, res, next) => {
  if (errorCondition) {
    next(new Error('Fail')); 
  }
  // Code here still runs! 可能導致 "Can't set headers after they are sent" 錯誤
  console.log('This should not run'); 
});
```

### 2. Async Error Handling Wrapper (For Express v4)
Express v4 無法自動捕獲 async function 中的錯誤。必須使用 wrapper 或 `express-async-handler`，否則 Promise rejection 會導致 Server Crash 或請求掛死。
Express v4 doesn't catch errors in async functions automatically. Use a wrapper.

```javascript
// Utility: async handler wrapper
const asyncHandler = fn => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Usage
app.get('/users', asyncHandler(async (req, res) => {
  const users = await db.getUsers(); // If this throws, .catch(next) handles it
  res.json(users);
}));
```
*(Note: Express v5 supports async/await error handling natively.)*

### 3. Middleware Ordering Strategy (三明治策略)
嚴格遵守 Middleware 的宣告順序：
1.  **Pre-processing**: Parsing (JSON/URL), Logging, CORS, Security Headers (Helmet).
2.  **Routing**: `app.use('/api', apiRoutes)`.
3.  **404 Handler**: 捕捉所有未匹配的路由。
4.  **Error Handling**: 必須放在最後，且必須有 4 個參數。

### 4. Controller Logic Separation
不要將所有邏輯寫在 `app.get(...)` 的 callback 中。將 Middleware 分為：
- **Sanitization/Validation Middleware**: 驗證輸入。
- **Controller/Handler**: 處理業務邏輯並回傳 Response。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Headers Already Sent" Error
這是 Express 開發者最常遇到的錯誤。發生原因通常是：
- 在 `res.send()` 或 `res.json()` 之後又呼叫了 `next()` 或再次 `res.send()`。
- 非同步操作中，多個路徑同時嘗試回應。

**Fix**: 確保每個 Request 路徑只有一個 Response 出口，並善用 `return` 終止函式。

### 2. Swallowing Errors (吞噬錯誤)
在 Middleware 中 `try...catch` 了錯誤卻沒有傳遞給 `next(err)`。
Catching an error but failing to pass it to `next(err)` leaves the request hanging.

```javascript
// ❌ Anti-pattern
app.get('/', (req, res, next) => {
  try {
    throw new Error('Boom');
  } catch (e) {
    console.log(e); 
    // Request hangs here forever! Client gets a timeout.
  }
});
```

### 3. Misunderstanding `app.use` Scope
將特定路由需要的 Middleware (如 `authMiddleware`) 註冊為全域 (`app.use(authMiddleware)`)，導致公開路由 (如 `/login` 或 `/health`) 也被阻擋。
**Fix**: 只在需要的 Router 或 Route 層級掛載 Middleware。

### 4. Modifying `req.body` unpredictably
在多個 Middleware 中隨意修改 `req.body` 會導致資料流難以追蹤 (Mutation hell)。
**Fix**: 若需附加資料，建議掛載在 `req.locals` 或 `req.user` (慣例)，盡量保持 `req.body` 為原始輸入狀態，或在單一 validation 層進行清洗。

---

## Checklists & workflows｜檢查清單與流程

### Middleware Implementation Checklist
在撰寫或 Review 一個新的 Middleware 時使用：

- [ ] **Termination Check**: 每個邏輯分支是否最終都會呼叫 `next()`、`next(err)` 或 `res.send()`？
- [ ] **Return Check**: 呼叫 `next()` 或回應後，是否使用了 `return` 防止後續程式碼執行？
- [ ] **Async Check**: 如果是 async function，是否有 `try...catch` 並呼叫 `next(err)` (或使用 wrapper)？
- [ ] **Order Check**: 這個 Middleware 是否依賴於 `body-parser` 或 `cookie-parser`？如果是，確保它在這些 parser 之後宣告。
- [ ] **Error Signature**: 如果這是錯誤處理 Middleware，是否明確宣告了 4 個參數 `(err, req, res, next)`？

### Debugging "Hanging Request" Workflow
當請求發出後一直在 loading 直到 timeout：

1.  **Check the chain**: 找出該路由經過的所有 Middleware。
2.  **Add Logs**: 在每個 Middleware 的開頭和 `next()` 前加上 `console.log`。
3.  **Identify the blocker**: 找出哪一個 Middleware 印出了 "Enter" 但沒有印出 "Exit/Next"。
4.  **Check Async**: 檢查該 blocker 是否有未捕獲的 Promise rejection。

---

## Real-world examples｜實戰案例

### 1. Context-Aware Request Logging (with Trace ID)
在微服務或大型系統中，追蹤單一請求的生命週期至關重要。

```javascript
const { v4: uuidv4 } = require('uuid');

// 1. Assign Trace ID early in the lifecycle
const traceIdMiddleware = (req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', req.id); // Return to client
  return next();
};

// 2. Logger that uses the Trace ID
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Hook into the response 'finish' event to log after response is sent
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[${req.id}] ${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`);
  });
  
  return next();
};

app.use(traceIdMiddleware);
app.use(requestLogger);
```

### 2. Centralized Error Handling Pipeline
生產環境的標準錯誤處理架構。

```javascript
// ... define routes ...

// 1. 404 Handler (Not Found) - Placed AFTER all routes
app.use((req, res, next) => {
  const error = new Error(`Path not found: ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
});

// 2. Global Error Handler - Placed LAST
app.use((err, req, res, next) => {
  // Operational errors (trusted) vs Programming errors
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  // Log error for developers (include stack trace)
  console.error(`[Error] ${statusCode} - ${message}`, err.stack);

  // Send safe response to client
  res.status(statusCode).json({
    success: false,
    error: {
      message: message,
      // Only show stack trace in development
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
});
```

### 3. Conditional Middleware (Feature Flagging)
有時你需要根據條件動態決定是否執行某個 Middleware。

```javascript
const requireAuth = (req, res, next) => { /* ... check token ... */ };

const featureFlagMiddleware = (flagName) => {
  return (req, res, next) => {
    if (checkFeatureFlag(flagName)) {
      // If flag is on, proceed to specific logic or apply extra middleware logic
      console.log(`Feature ${flagName} is active`);
    }
    next();
  };
};

// Route specific usage
app.post('/beta-feature', 
  requireAuth, 
  featureFlagMiddleware('new-ui'), 
  betaController
);
```