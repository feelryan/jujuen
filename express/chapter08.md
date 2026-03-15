# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，寫出能跑的程式碼只是基本功；如何讓系統在 Production 環境中「透明化」並具備「韌性」，才是區分 Senior 與 Junior 的關鍵。Express 應用程式若缺乏良好的可觀測性（Observability），在發生故障時將如同黑箱作業，導致 Mean Time To Recovery (MTTR) 大幅增加。

For a Senior Software Engineer, writing code that works is merely the baseline; making the system "transparent" and "resilient" in a Production environment is what distinguishes a Senior from a Junior. An Express application lacking good Observability becomes a black box during failures, significantly increasing the Mean Time To Recovery (MTTR).

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作結構化日誌（Structured Logging）**：捨棄 `console.log`，使用高效能 Logger（如 Pino）並結合 Context ID，以便在 Log Aggregation 系統中進行查詢。
    **Implement Structured Logging**: Move away from `console.log`, use high-performance loggers (like Pino) combined with Context IDs for efficient querying in Log Aggregation systems.
2.  **整合 OpenTelemetry 進行分散式追蹤**：理解並實作 OpenTelemetry SDK，解決微服務架構下跨服務請求追蹤（Distributed Tracing）的難題。
    **Integrate OpenTelemetry for Distributed Tracing**: Understand and implement the OpenTelemetry SDK to solve the challenge of tracing requests across services in a microservices architecture.
3.  **設計生產級的生命週期管理**：正確實作 Liveness/Readiness Probes 以及 Graceful Shutdown 機制，確保部署與自動擴展時零停機（Zero Downtime）。
    **Design Production-Grade Lifecycle Management**: Correctly implement Liveness/Readiness Probes and Graceful Shutdown mechanisms to ensure Zero Downtime during deployments and auto-scaling.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 可觀測性的三大支柱 (The Three Pillars of Observability)

在系統設計中，我們常將可觀測性分為 Log、Metric 與 Trace。對於 Express 應用程式而言，這意味著不同的實作層次：

In system design, Observability is often categorized into Logs, Metrics, and Traces. For an Express application, this implies different implementation layers:

*   **Logs (Events)**: "Something happened." Discrete events.
    *   *Express Context*: Error details, request completion info, debugging data.
    *   *Key*: Must be structured (JSON) and correlated.
*   **Metrics (Aggregates)**: "What is the trend?" Aggregatable data over time.
    *   *Express Context*: Request rate (RPS), Error rate, Latency (p99, p95).
    *   *Key*: Low cardinality is crucial (don't put UserID in metric labels).
*   **Traces (Context)**: "Where did it happen?" The journey of a request.
    *   *Express Context*: The path a request takes through middleware, DB calls, and external APIs.
    *   *Key*: Propagation of `Trace Context` (e.g., W3C Trace Context headers).

## 2.2 關聯性 ID 與上下文傳遞 (Correlation IDs & Context Propagation)

最核心的心智模型是「請求的生命週期（Request Lifecycle）」。在 Node.js 的單執行緒事件迴圈模型中，我們不能依賴 Thread Local Storage (TLS) 來儲存每個請求的上下文。

The core mental model is the "Request Lifecycle." In Node.js's single-threaded event loop model, we cannot rely on Thread Local Storage (TLS) to store context for each request.

*   **Naive Approach**: 將 `req` 物件一路傳遞到所有函數中（Parameter Drilling）。
    **Naive Approach**: Passing the `req` object down to every function (Parameter Drilling).
*   **Senior Approach**: 使用 `AsyncLocalStorage` (ALS)。這是 Node.js 內建的 API，允許我們在非同步呼叫鏈中保持狀態（如 TraceID 或 Logger instance），而無需修改函數簽名。
    **Senior Approach**: Using `AsyncLocalStorage` (ALS). This is a built-in Node.js API that allows us to maintain state (like TraceID or Logger instance) across asynchronous call chains without modifying function signatures.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 架構中的角色 (Role in System Architecture)

在典型的微服務或雲原生架構中，Express 服務通常位於 Load Balancer 之後。

In a typical microservices or cloud-native architecture, the Express service usually sits behind a Load Balancer.

1.  **Log Flow**: Express (stdout/JSON) -> Log Shipper (Fluentd/Filebeat) -> ElasticSearch/Datadog/CloudWatch.
2.  **Trace Flow**: Express (OTel SDK) -> OTel Collector (Sidecar/Agent) -> Jaeger/Tempo/X-Ray.
3.  **Health Check Flow**: K8s Kubelet -> Express Routes (`/health/*`) -> Restart or Remove from Service Endpoint.

## 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **Performance (效能)**:
    *   **Logging**: `console.log` 是同步且阻塞的（synchronous and blocking）。在高流量下，這會直接卡死 Event Loop。必須使用非同步寫入（Asynchronous logging）。
    *   **Tracing**: 過度採樣（100% Sampling）會帶來 CPU 與網路開銷。通常在 Production 設定 1% - 10% 的採樣率。
*   **Reliability (可靠性)**:
    *   **Graceful Shutdown**: 當 K8s 刪除 Pod 時，若 Express 直接 `process.exit()`，會導致正在處理中的請求失敗（5xx error）。必須先停止接收新請求，處理完舊請求，並關閉 DB 連線後再退出。

---

# 4. 逐步示例 (Walkthrough / Example)

我們將構建一個具備結構化日誌、自動追蹤與優雅關機的 Express 伺服器。

We will build an Express server equipped with structured logging, automatic tracing, and graceful shutdown.

### Step 1: 結構化日誌與 Context (Structured Logging with Context)

我們使用 `pino`（極速 Logger）與 `pino-http`。

We use `pino` (very fast logger) and `pino-http`.

```javascript
// logger.js
const pino = require('pino');

// In production, log to stdout as JSON.
// In development, you might use pino-pretty for readability.
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => {
      return { level: label.toUpperCase() };
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
});

module.exports = logger;
```

### Step 2: OpenTelemetry 設置 (OpenTelemetry Setup)

這是最關鍵的一步。我們需要在應用程式啟動**最早期**載入 OTel SDK。

This is the most critical step. We need to load the OTel SDK at the very **beginning** of the application startup.

```javascript
// tracing.js
// Must run before importing any other modules
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Configure the trace exporter (sends traces to Jaeger/Tempo/Datadog)
const traceExporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
});

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'payment-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),
  traceExporter,
  // Auto-instrumentations hook into http, express, pg, redis, etc.
  instrumentations: [getNodeAutoInstrumentations()],
});

// Start the SDK
sdk.start();

// Handle process exit to flush traces
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;
```

### Step 3: Express App 整合 (Express App Integration)

整合 Logger、Health Checks 與 Graceful Shutdown。

Integrating Logger, Health Checks, and Graceful Shutdown.

```javascript
// server.js
require('./tracing'); // Initialize OTel first!

const express = require('express');
const pinoHttp = require('pino-http');
const logger = require('./logger');
const { createTerminus } = require('@godaddy/terminus'); // Helper for graceful shutdown
const http = require('http');

const app = express();

// 1. Structured Logging Middleware
// Auto-injects request-id and logs request/response details
app.use(pinoHttp({ 
  logger,
  // Custom logic to define what counts as an error
  customSuccessMessage: (req, res) => `${req.method} ${req.url} completed`,
  customErrorMessage: (req, res, err) => `${req.method} ${req.url} failed: ${err.message}`
}));

// 2. Business Logic
app.get('/', (req, res) => {
  // req.log is injected by pino-http, containing the request context (reqId)
  req.log.info('Handling business logic...');
  
  // Simulate DB call (OTel will auto-trace this if using pg/mysql driver)
  setTimeout(() => {
    res.json({ message: 'Hello from Senior Express!' });
  }, 100);
});

// 3. Health Checks (Liveness vs Readiness)
// Liveness: Is the process running?
app.get('/health/live', (req, res) => res.status(200).send('OK'));

// Readiness: Can it accept traffic? (Check DB connection, Redis, etc.)
app.get('/health/ready', async (req, res) => {
  const isDbConnected = true; // Replace with actual DB check
  if (isDbConnected) {
    res.status(200).send('OK');
  } else {
    res.status(503).send('Service Unavailable');
  }
});

const server = http.createServer(app);

// 4. Graceful Shutdown Setup
function onSignal() {
  logger.info('server is starting cleanup');
  // Close DB connections, Redis clients, etc. here
  return Promise.all([
    // db.close(),
    // redis.quit()
  ]);
}

async function onHealthCheck() {
  // Optional: checks used by load balancers during shutdown
  return Promise.resolve();
}

createTerminus(server, {
  signal: 'SIGTERM',
  healthChecks: { '/health/live': onHealthCheck },
  onSignal,
  timeout: 5000, // Force kill after 5s if cleanup hangs
  logger: (msg, err) => logger.error(err, msg) // Use our structured logger
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  logger.info(`Server listening on port ${PORT}`);
});
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在生產環境使用 `console.log` (Using `console.log` in Production)

*   **Anti-pattern**: `console.log('User logged in', userObj);`
*   **Why**:
    1.  **Blocking**: 在 Node.js 中，寫入 stdout/stderr 在某些系統（如 TTY）上是同步的，會阻塞 Event Loop。
    2.  **Unstructured**: 輸出是純文字，難以在 Datadog/ELK 中用 SQL-like 語法查詢（例如 `log.user_id = 123`）。
    3.  **Serialization Risk**: 若物件包含循環引用（Circular Reference），`JSON.stringify` 會拋出錯誤導致 Crash。
*   **Solution**: 使用 Pino 或 Winston，並確保開啟非同步寫入模式（Async mode）。

## 5.2 混淆 Liveness 與 Readiness (Confusing Liveness and Readiness)

*   **Anti-pattern**: 在 Liveness Probe 中檢查資料庫連線。
*   **Why**: 若資料庫短暫斷線，Liveness check 失敗會導致 K8s **重啟 Pod**。但重啟 Pod 無法解決資料庫問題，反而可能因為所有 Pod 同時重啟而造成「重啟風暴（Restart Storm）」。
*   **Solution**:
    *   **Liveness**: 只檢查 Process 是否存活（例如 Deadlock 檢測）。
    *   **Readiness**: 檢查相依服務（DB/Redis）是否可用。若失敗，K8s 僅會停止發送流量給該 Pod，而不會殺死它。

## 5.3 指標基數爆炸 (High Cardinality Metrics)

*   **Anti-pattern**: `metrics.increment('http_requests_total', { userId: req.user.id })`
*   **Why**: Metrics 系統（如 Prometheus）是為聚合設計的。若 Label 中包含無限增長的數值（如 UserID, RequestID, Email），會導致 Time Series 數量爆炸，拖垮監控系統記憶體。
*   **Solution**: 只在 Label 中放有限集合的資料（如 `status_code`, `method`, `route`）。具體 UserID 應放在 Log 或 Trace 中。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在微服務架構中，如何追蹤一個請求經過了哪些服務？
**How do you trace a request as it passes through multiple services in a microservices architecture?**

*   **Key Points**:
    *   提到 **Distributed Tracing** 與 **OpenTelemetry**。
    *   解釋 **Context Propagation**：當 Service A 呼叫 Service B 時，必須將 `traceparent` (W3C standard) 或 `b3` headers 注入 HTTP 請求頭中。
    *   Service B 收到請求後，解析 Header，使用相同的 TraceID 繼續產生 Span。
    *   強調這通常由 Auto-instrumentation 自動處理，但理解原理有助於除錯（例如 Header 被 Nginx 丟棄的情況）。

### Q2: 為什麼 Node.js 的 Graceful Shutdown 很重要？具體步驟是什麼？
**Why is Graceful Shutdown important in Node.js, and what are the specific steps?**

*   **Key Points**:
    *   **Data Integrity**: 防止正在寫入 DB 的請求被強制中斷。
    *   **User Experience**: 防止使用者收到 502 Bad Gateway 或 Connection Reset。
    *   **步驟**:
        1.  監聽 `SIGTERM` / `SIGINT` 信號。
        2.  停止 `server.listen`（不再接收新連線）。
        3.  設定 `server.close` 等待現有請求完成（Keep-Alive 連線處理）。
        4.  關閉 DB 連線、Redis 連線、停止 Consumer。
        5.  設定強制退出的 Timeout（防止 Zombie process）。

### Q3: 高流量下，Log 寫入量過大導致效能瓶頸，你會如何優化？
**Under high traffic, excessive log writing causes performance bottlenecks. How would you optimize this?**

*   **Key Points**:
    *   **Log Level**: 動態調整 Log Level（平時 Info/Warn，除錯時 Debug）。
    *   **Asynchronous Logging**: 使用 Worker Thread 或獨立的 Log Shipper process 來寫入檔案/網路，避免阻塞主執行緒。
    *   **Sampling**: 對於成功請求（200 OK）進行採樣（例如只記 10%），但對錯誤請求（5xx）全記。
    *   **Format**: 確保 Log 訊息盡量精簡，避免 dump 巨大物件。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)
1.  **結構化日誌 (Structured Logging)** 是現代可觀測性的基礎，務必使用 JSON 格式並包含 `reqId`。
2.  **OpenTelemetry** 是分散式追蹤的業界標準，善用 Auto-instrumentation 可以大幅降低導入成本。
3.  **Context Propagation** 在 Node.js 中依賴 `AsyncLocalStorage`，這是串聯 Log 與 Trace 的關鍵技術。
4.  **Graceful Shutdown** 是區分 Demo App 與 Production App 的重要細節，確保部署時使用者無感。
5.  **Liveness vs Readiness**：前者決定重啟，後者決定流量，切勿混用。

### 後續延伸 (Next Steps)
*   **Performance Tuning**: 學習如何分析 CPU Profile 與 Memory Heap Snapshot（當 Metrics 顯示異常時的下一步）。
*   **Security**: 學習如何在 Log 中自動遮蔽敏感資訊（PII Redaction），這在處理使用者資料時至關重要。
*   **Service Mesh**: 探索 Istio 或 Linkerd 如何在基礎設施層自動處理 Tracing 與 Metrics，減輕 Express 應用程式的負擔。