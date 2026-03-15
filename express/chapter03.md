# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Middleware（中介軟體）不僅僅是攔截請求的函數，它是 Express 應用程式的骨架與神經系統。本章將超越基礎的 `(req, res, next)` 實作，探討如何構建可配置、可擴展且具備高觀測性的 Middleware 架構。

For senior engineers, Middleware is not just a function to intercept requests; it is the backbone and nervous system of an Express application. This chapter moves beyond basic `(req, res, next)` implementation to explore how to build middleware architectures that are configurable, scalable, and highly observable.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計 Middleware Factory 模式**：建立可透過參數配置的高階 Middleware，提升程式碼重用性。
    **Design Middleware Factory Patterns**: Create higher-order middleware configurable via parameters to enhance code reusability.
2.  **掌握 Request Context 管理**：利用 `AsyncLocalStorage` 在不污染 `req` 物件的情況下，於深層 Service 中存取 Request-scoped 資訊（如 Trace ID）。
    **Master Request Context Management**: Use `AsyncLocalStorage` to access request-scoped information (like Trace IDs) in deep services without polluting the `req` object.
3.  **實作全域錯誤處理策略**：區分 Operational Errors 與 Programmer Errors，並理解 Express 4 與 5 在非同步錯誤處理（Async Error Handling）上的關鍵差異。
    **Implement Global Error Handling Strategies**: Distinguish between Operational Errors and Programmer Errors, and understand the critical differences in Async Error Handling between Express 4 and 5.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Middleware Factory (Configurable Middleware)

**直覺類比**：
如果標準 Middleware 是一個「固定的檢查站」（例如：所有人都必須出示證件），那麼 Middleware Factory 就是一個「檢查站產生器」。你可以告訴產生器：「我要一個只檢查 VIP 的站」或「我要一個只允許帶紅色帽子的站」。

**Intuitive Analogy**:
If standard middleware is a "fixed checkpoint" (e.g., everyone must show ID), a Middleware Factory is a "checkpoint generator." You can tell the generator: "I want a checkpoint that only checks VIPs" or "I want one that only allows people with red hats."

**正規定義**：
Middleware Factory 是一個**高階函數（Higher-Order Function）**，它接收配置選項（Options），並返回一個標準的 Express Middleware 函數。

**Formal Definition**:
A Middleware Factory is a **Higher-Order Function** that accepts configuration options and returns a standard Express Middleware function.

```javascript
// Conceptual Model
const factory = (options) => {
  // Initialization logic (runs once)
  return (req, res, next) => {
    // Request logic (runs per request)
    if (check(req, options)) next();
  };
};
```

## 2.2 Context Isolation & AsyncLocalStorage

**核心差異**：
在傳統 Express 開發中，我們習慣將使用者資訊掛載在 `req.user` 上。然而，當業務邏輯深入到 Service 層或 Repository 層時，傳遞 `req` 物件會導致層次耦合（Coupling）。

**Core Distinction**:
In traditional Express development, we are used to attaching user info to `req.user`. However, passing the `req` object down to Service or Repository layers causes coupling.

**解決方案**：
Node.js 的 `AsyncLocalStorage` (ALS) 提供了一種在非同步呼叫鏈中儲存資料的機制，類似於多執行緒語言中的 Thread-Local Storage。這允許我們在 Controller 設定 Context，並在任何深層函數中讀取，而無需顯式傳遞參數。

**Solution**:
Node.js's `AsyncLocalStorage` (ALS) provides a mechanism to store data throughout an asynchronous call chain, similar to Thread-Local Storage in multi-threaded languages. This allows us to set context in the Controller and read it in any deep function without explicit parameter passing.

## 2.3 Error Propagation (Express 4 vs 5)

**Express 4 的痛點**：
Express 4 無法自動捕獲 Promise 中的 Rejection。如果 `async` 函數拋出錯誤且未被 `catch` 並傳遞給 `next(err)`，請求將會掛起（Hang）直到超時。

**Pain Point in Express 4**:
Express 4 does not automatically catch Promise rejections. If an `async` function throws an error and it isn't caught and passed to `next(err)`, the request will hang until it times out.

**Express 5 的變革**：
Express 5 (及 4.x 的 router patch) 自動處理返回 Promise 的 Middleware。若 Promise reject，Express 會自動呼叫 `next(err)`。

**Evolution in Express 5**:
Express 5 (and 4.x router patches) automatically handles middleware that returns a Promise. If the Promise rejects, Express automatically calls `next(err)`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統或微服務架構中，Middleware 與錯誤處理不僅是程式碼風格問題，更直接影響**系統的可觀測性（Observability）**與**彈性（Resilience）**。

In large-scale distributed systems or microservices architectures, middleware and error handling are not just matters of coding style; they directly impact **System Observability** and **Resilience**.

## 3.1 可觀測性與追蹤 (Observability & Tracing)

**場景**：
當一個請求失敗時，你需要跨多個微服務追蹤該請求。
**Scenario**:
When a request fails, you need to trace that request across multiple microservices.

**設計**：
使用 Middleware 在請求進入時生成或提取 `X-Request-ID`，並將其存入 `AsyncLocalStorage`。Logger（如 Winston/Pino）會自動從 ALS 讀取該 ID 並附加到每一行 Log 中。這樣即使在深層 DB 查詢出錯，Log 也會帶有該 Request ID。

**Design**:
Use middleware to generate or extract an `X-Request-ID` upon entry and store it in `AsyncLocalStorage`. Loggers (like Winston/Pino) automatically read this ID from ALS and attach it to every log line. This way, even if a deep DB query fails, the log will carry that Request ID.

## 3.2 統一錯誤回應標準 (Standardized Error Responses)

**場景**：
前端或第三方開發者抱怨 API 錯誤格式不一致（有時是 `{ error: "msg" }`，有時是 HTML stack trace）。
**Scenario**:
Frontend or third-party developers complain about inconsistent API error formats (sometimes `{ error: "msg" }`, sometimes HTML stack traces).

**設計**：
建立一個全域 Error Handling Middleware。所有業務邏輯只負責 `throw new AppError(...)`。全域 Handler 負責：
1.  **Sanitization**：隱藏內部 Stack Trace（生產環境）。
2.  **Normalization**：轉換為標準 JSON 格式（如 RFC 7807 Problem Details）。
3.  **Metrics**：記錄錯誤計數（Prometheus/Datadog）。

**Design**:
Establish a global Error Handling Middleware. All business logic is only responsible for `throw new AppError(...)`. The global handler is responsible for:
1.  **Sanitization**: Hiding internal stack traces (in production).
2.  **Normalization**: Converting to standard JSON format (e.g., RFC 7807 Problem Details).
3.  **Metrics**: Recording error counts (Prometheus/Datadog).

---

# 4. 逐步示例 (Walkthrough / Example)

我們將實作一個進階場景：
1.  **Context Middleware**：初始化 `AsyncLocalStorage` 並生成 Request ID。
2.  **Auth Factory**：一個可配置角色的驗證 Middleware。
3.  **Global Error Handler**：處理 Async 錯誤與標準化輸出。

We will implement an advanced scenario:
1.  **Context Middleware**: Initialize `AsyncLocalStorage` and generate a Request ID.
2.  **Auth Factory**: A configurable role-based authentication middleware.
3.  **Global Error Handler**: Handle async errors and standardize output.

### Step 1: Context Management (AsyncLocalStorage)

```javascript
// lib/context.js
const { AsyncLocalStorage } = require('node:async_hooks');
const { v4: uuidv4 } = require('uuid');

// Singleton instance
const context = new AsyncLocalStorage();

const contextMiddleware = (req, res, next) => {
  const store = new Map();
  const requestId = req.headers['x-request-id'] || uuidv4();
  
  store.set('requestId', requestId);
  res.setHeader('X-Request-ID', requestId); // Return to client

  // Run the rest of the request lifecycle within this context
  context.run(store, () => {
    next();
  });
};

const getRequestId = () => {
  const store = context.getStore();
  return store ? store.get('requestId') : 'N/A';
};

module.exports = { contextMiddleware, getRequestId };
```

### Step 2: Middleware Factory (Role-Based Auth)

這裡展示如何傳入 `allowedRoles` 來動態產生 Middleware。

Here we demonstrate how to pass `allowedRoles` to dynamically generate middleware.

```javascript
// middleware/auth.js
const AppError = require('../lib/AppError'); // Custom error class

// The Factory
const requireRole = (allowedRoles = []) => {
  return async (req, res, next) => {
    try {
      // Mock user extraction (usually from JWT)
      const user = req.user; 
      
      if (!user) {
        throw new AppError('Unauthorized', 401);
      }

      if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        throw new AppError('Forbidden: Insufficient permissions', 403);
      }

      next();
    } catch (err) {
      next(err); // Essential for Express 4 compatibility
    }
  };
};

module.exports = requireRole;
```

### Step 3: Global Error Handler & Usage

結合 Express 5 (或使用 `express-async-errors` patch) 的寫法。

Combining with Express 5 (or using `express-async-errors` patch) style.

```javascript
// app.js
const express = require('express');
const { contextMiddleware, getRequestId } = require('./lib/context');
const requireRole = require('./middleware/auth');
const AppError = require('./lib/AppError');

const app = express();

// 1. Apply Context Middleware globally
app.use(contextMiddleware);

// 2. Route using the Factory
// Only 'admin' can access this route
app.get('/admin/dashboard', requireRole(['admin']), async (req, res) => {
  // Simulate logic deep in the service layer
  console.log(`Processing request: ${getRequestId()}`); 
  
  // Simulate an async error
  // In Express 5, this rejection is automatically caught.
  throw new AppError('Database connection failed', 500); 
});

// 3. Centralized Error Handler (Must have 4 arguments)
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const requestId = getRequestId(); // Retrieve from ALS

  // Log the error (Structured Logging)
  console.error(JSON.stringify({
    level: 'error',
    requestId,
    message: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
  }));

  // Send standardized response
  res.status(statusCode).json({
    status: 'error',
    code: statusCode,
    requestId, // Highly useful for debugging
    message: err.isOperational ? err.message : 'Internal Server Error',
  });
});

module.exports = app;
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `req` 物件 (Polluting the `req` Object)

**錯誤案例**：
Middleware 隨意將資料掛載到 `req` 上，例如 `req.dbData`、`req.config`、`req.utils`。
**Error Case**:
Middleware arbitrarily attaches data to `req`, such as `req.dbData`, `req.config`, `req.utils`.

**為何不好**：
1.  **型別安全低**：在 TypeScript 中需要不斷擴充 Request Interface。
2.  **隱式依賴**：下游 Controller 依賴上游 Middleware 注入的隱藏屬性，難以測試與重構。
3.  **命名衝突**：不同 Middleware 可能覆蓋同名屬性。

**Why it's bad**:
1.  **Low Type Safety**: Requires constant extension of the Request Interface in TypeScript.
2.  **Implicit Dependencies**: Downstream controllers rely on hidden properties injected by upstream middleware, making testing and refactoring difficult.
3.  **Naming Conflicts**: Different middleware might overwrite properties with the same name.

**較佳方案**：
僅將與請求直接相關的（如 Auth User）掛載到 `req`。全域工具或 Context 應使用 `AsyncLocalStorage` 或 Dependency Injection。

**Better Approach**:
Only attach data directly related to the request (like Auth User) to `req`. Global tools or Context should use `AsyncLocalStorage` or Dependency Injection.

## 5.2 錯誤處理中的 "Catch and Log" (Catch and Log without Propagation)

**錯誤案例**：
```javascript
try {
  await service.doSomething();
} catch (err) {
  console.log(err);
  res.status(500).send('Error'); // 中斷了 Middleware 鏈，且未觸發全域錯誤處理
}
```

**為何不好**：
這導致錯誤處理邏輯分散在各個 Controller 中，無法統一監控，且容易遺漏 Request ID 等 metadata。

**Why it's bad**:
This scatters error handling logic across controllers, making unified monitoring impossible, and often leads to missing metadata like Request IDs.

**較佳方案**：
永遠將錯誤傳遞給 `next(err)`（或在 Express 5 中直接 throw），由全域 Handler 統一處理。

**Better Approach**:
Always pass errors to `next(err)` (or simply throw in Express 5), letting the global handler manage it centrally.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: Express 5 對於 Error Handling 做了什麼重大改變？這如何影響你的程式碼結構？
**Express 5 made significant changes to Error Handling. How does this affect your code structure?**

*   **高分回答要點**：
    *   指出 Express 4 無法捕獲 Promise Rejection，需要 `try/catch` 配合 `next(err)` 或使用 `express-async-errors`。
    *   指出 Express 5 自動處理 Async Middleware 的 Rejection。
    *   影響：程式碼更乾淨，移除大量的 `try/catch` 區塊，降低因忘記呼叫 `next` 而導致請求掛起的風險。

*   **Key Points for a High Score**:
    *   Mention that Express 4 cannot catch Promise Rejections, requiring `try/catch` with `next(err)` or `express-async-errors`.
    *   State that Express 5 automatically handles Rejections in Async Middleware.
    *   Impact: Cleaner code, removal of massive `try/catch` blocks, and reduced risk of hanging requests due to forgotten `next` calls.

## Q2: 你如何在不將 `req` 物件傳遞給每一層函數的情況下，在 Service 層獲取當前的 User ID 或 Trace ID？
**How do you access the current User ID or Trace ID in the Service layer without passing the `req` object to every function?**

*   **高分回答要點**：
    *   提到 `AsyncLocalStorage` (ALS) 是 Node.js 的原生解決方案。
    *   描述 Middleware 流程：在請求開始時 `store.run()`，並將 ID 寫入 store。
    *   比較優劣：ALS 解決了 "Prop drilling" 問題，但引入了隱式依賴（Implicit Dependency），使用時需權衡。

*   **Key Points for a High Score**:
    *   Mention `AsyncLocalStorage` (ALS) as the native Node.js solution.
    *   Describe the flow: `store.run()` at the start of the request, writing the ID into the store.
    *   Pros/Cons: ALS solves "Prop drilling" but introduces Implicit Dependencies; usage requires trade-offs.

## Q3: 在設計一個供多個微服務使用的 Shared Middleware Library 時，你會考慮哪些因素？
**What factors would you consider when designing a Shared Middleware Library for multiple microservices?**

*   **高分回答要點**：
    *   **Configurability (Factory Pattern)**：允許各服務自定義參數（如 Rate Limit 閾值、Auth Server URL）。
    *   **Fail-safe**：Middleware 故障不應導致整個服務崩潰（例如 Logger 出錯應被忽略）。
    *   **Versioning**：確保 Middleware 更新不會破壞現有服務。
    *   **Performance**：避免在 Middleware 中進行昂貴的同步運算。

*   **Key Points for a High Score**:
    *   **Configurability (Factory Pattern)**: Allow services to customize parameters (e.g., Rate Limit thresholds, Auth Server URL).
    *   **Fail-safe**: Middleware failure should not crash the entire service (e.g., Logger errors should be ignored).
    *   **Versioning**: Ensure middleware updates do not break existing services.
    *   **Performance**: Avoid expensive synchronous operations within middleware.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Middleware Factory**：使用高階函數模式（Higher-Order Functions）來建立可配置、可重用的 Middleware。
2.  **AsyncLocalStorage**：是現代 Node.js 處理 Request Context 的標準做法，避免了參數透傳（Prop Drilling）。
3.  **Express 5 Async Handling**：原生支援 Promise Rejection，大幅簡化了非同步錯誤處理程式碼。
4.  **Centralized Error Handling**：將錯誤日誌、格式化、監控集中在一處管理，確保 API 行為一致性。
5.  **Operational vs Programmer Errors**：區分「可預期的執行期錯誤」與「程式碼 Bug」，並給予不同的處理策略（前者回傳 4xx/5xx，後者可能需要重啟 Process）。

## 後續延伸 (Next Steps)
*   **Next Chapter**: **Express 效能優化與安全性 (Performance Optimization & Security)**。
*   **Action Item**: 檢視你目前的專案，嘗試將 `req.user` 或 `traceId` 的傳遞方式重構為 `AsyncLocalStorage`。
*   **Reading**: 深入閱讀 Node.js 官方文件中的 `AsyncHooks` 與 `AsyncLocalStorage` 章節，了解其對效能的輕微影響。