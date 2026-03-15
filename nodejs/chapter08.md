# Chapter 08: Observability & Debugging Engineering
# 第八章：可觀測性與除錯工程

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In modern distributed systems, "monitoring" tells you *that* something is wrong, while "observability" allows you to ask *why* it is wrong. For a Senior Node.js Engineer, mastering observability means moving beyond `console.log` and basic health checks to building a system that emits rich, correlated telemetry data. This chapter focuses on implementing the "Three Pillars of Observability" (Logs, Metrics, Traces) within the Node.js runtime and debugging complex production issues.
在現代分散式系統中，「監控（Monitoring）」告訴你系統*出了問題*，而「可觀測性（Observability）」則讓你能夠探究*為什麼*會出問題。對於資深 Node.js 工程師而言，掌握可觀測性意味著超越 `console.log` 和基本的健康檢查，轉而建構一個能發送豐富且具關聯性遙測數據（telemetry data）的系統。本章專注於在 Node.js 執行環境中實作「可觀測性三大支柱」（Logs、Metrics、Traces），以及如何除錯複雜的生產環境問題。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Implement OpenTelemetry:** Configure the OpenTelemetry (OTel) SDK in Node.js to auto-instrument HTTP requests, database queries, and propagate context across microservices.
    **實作 OpenTelemetry：** 在 Node.js 中配置 OpenTelemetry (OTel) SDK，自動對 HTTP 請求、資料庫查詢進行儀表化（Instrumentation），並在微服務間傳遞上下文。
2.  **Design Structured Logging:** Replace ad-hoc logging with high-performance, structured logging (e.g., Pino) that automatically correlates with trace IDs.
    **設計結構化日誌：** 使用高效能的結構化日誌（如 Pino）取代隨意式的日誌記錄，並自動與 Trace ID 進行關聯。
3.  **Monitor Node.js Internals:** Measure Event Loop Lag, GC pauses, and Heap usage to detect bottlenecks specific to the single-threaded nature of Node.js.
    **監控 Node.js 內部狀態：** 測量 Event Loop Lag、GC 暫停時間與 Heap 使用量，以偵測 Node.js 單執行緒特性特有的效能瓶頸。
4.  **Debug in Production:** Utilize CPU profiling and Heap Snapshots in live environments with minimal impact to diagnose memory leaks and CPU spikes.
    **生產環境除錯：** 在正式環境中利用 CPU Profiling 與 Heap Snapshots 進行診斷，以最小的效能影響找出記憶體洩漏與 CPU 飆升的原因。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Three Pillars + 1 (Profiles)
### 2.1 三大支柱 + 1 (Profiles)

To understand observability, visualize it as a medical checkup for your application:
要理解可觀測性，可以將其想像為對應用程式進行的健康檢查：

*   **Metrics (Vital Signs):** Aggregated numbers over time (e.g., "Heart rate is 80 bpm"). In Node.js, this is Request Rate, Error Rate, and Event Loop Lag. They are cheap to store but lack detail.
    **Metrics（生命徵象）：** 隨時間聚合的數值（例如：「心跳每分鐘 80 下」）。在 Node.js 中，這代表請求率、錯誤率與 Event Loop Lag。它們儲存成本低，但缺乏細節。
*   **Logs (Patient Diary):** Discrete events (e.g., "Felt dizzy at 10:00 AM"). In Node.js, these are JSON objects describing specific occurrences. They provide high detail but are expensive at scale.
    **Logs（病患日記）：** 離散的事件（例如：「早上 10 點感到頭暈」）。在 Node.js 中，這是描述特定事件的 JSON 物件。它們提供高度細節，但在大規模下成本高昂。
*   **Traces (X-Ray/MRI):** The path of a request through the system. It visualizes causality and latency across boundaries (e.g., Service A -> Service B -> DB).
    **Traces（X 光/MRI）：** 請求在系統中的路徑。它視覺化了跨邊界（例如：Service A -> Service B -> DB）的因果關係與延遲。
*   **Profiles (Biopsy):** Deep analysis of resource usage (CPU/Memory) at a specific moment, crucial for performance tuning.
    **Profiles（切片檢查）：** 針對特定時刻資源使用（CPU/記憶體）的深度分析，對於效能調校至關重要。

### 2.2 Context Propagation & AsyncLocalStorage
### 2.2 上下文傳遞與 AsyncLocalStorage

In a synchronous language (like Java with ThreadLocal), context is tied to the thread. In Node.js, multiple requests share the same thread.
在同步語言（如擁有 ThreadLocal 的 Java）中，上下文是綁定在執行緒上的。在 Node.js 中，多個請求共享同一個執行緒。

The mental model for Node.js observability relies heavily on **`AsyncLocalStorage`**. Imagine a "backpack" that automatically follows your code execution across asynchronous jumps (Promises, callbacks). OpenTelemetry uses this to carry the `trace_id` and `span_id` throughout the request lifecycle, ensuring that a log written in a deep database callback knows which HTTP request triggered it.
Node.js 可觀測性的心智模型高度依賴 **`AsyncLocalStorage`**。想像有一個「背包」，它會隨著你的程式碼執行，自動跨越非同步跳轉（Promises、callbacks）。OpenTelemetry 利用這一點在請求的生命週期中攜帶 `trace_id` 和 `span_id`，確保即使是在深層資料庫 callback 中寫入的日誌，也能知道是由哪個 HTTP 請求觸發的。

### 2.3 Instrumentation vs. Exporting
### 2.3 儀表化 (Instrumentation) vs. 輸出 (Exporting)

*   **Instrumentation:** The code that measures what's happening (e.g., wrapping `http.request`).
    **儀表化：** 測量正在發生什麼的程式碼（例如：包裝 `http.request`）。
*   **Exporting:** Sending that data to a backend (e.g., Prometheus, Jaeger, Datadog).
    **輸出：** 將數據發送到後端（例如：Prometheus、Jaeger、Datadog）。

**OpenTelemetry** decouples these. You instrument once, and configure exporters to send data anywhere. This prevents vendor lock-in.
**OpenTelemetry** 將這兩者解耦。你只需儀表化一次，然後配置 Exporter 將數據發送到任何地方。這避免了供應商鎖定（Vendor Lock-in）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 The Observability Pipeline
### 3.1 可觀測性管線

In a production environment, you rarely send telemetry directly from the Node.js process to the storage backend.
在生產環境中，你很少直接將遙測數據從 Node.js 行程發送到儲存後端。

**Architecture:**
**架構：**
`Node.js App (OTel SDK)` -> `OpenTelemetry Collector (Sidecar/Agent)` -> `Backend (Elasticsearch/Prometheus/Vendor)`

*   **Why?** Offloading the network overhead and batch processing (compression, filtering, PII redaction) to a sidecar prevents the Node.js Event Loop from being blocked by heavy telemetry transmission.
    **為什麼？** 將網路開銷與批次處理（壓縮、過濾、PII 遮蔽）卸載到 Sidecar，可以防止 Node.js Event Loop 被繁重的遙測傳輸阻塞。

### 3.2 Sampling Strategies
### 3.2 採樣策略

At scale (e.g., 10k RPS), tracing every request is too expensive.
在大規模場景（例如 10k RPS），追蹤每一個請求太過昂貴。

*   **Head-based Sampling:** Decision is made at the start of the request (e.g., "Trace 1% of traffic"). Efficient but might miss errors in the 99%.
    **頭部採樣 (Head-based)：** 在請求開始時做出決定（例如：「追蹤 1% 的流量」）。效率高，但可能會錯過那 99% 中的錯誤。
*   **Tail-based Sampling:** All traces are collected in a buffer (e.g., in the OTel Collector), and the decision is made after the request finishes. You can keep 100% of errors and slow requests, and only 1% of success. This is the gold standard for debugging.
    **尾部採樣 (Tail-based)：** 所有 Trace 先收集在緩衝區（例如在 OTel Collector 中），請求結束後才做決定。你可以保留 100% 的錯誤與慢速請求，而只保留 1% 的成功請求。這是除錯的黃金標準。

---

## 4. Walkthrough: Building an Observable Service
## 4. 逐步示例：建構可觀測的服務

We will implement a setup where Logs, Metrics, and Traces are correlated.
我們將實作一個 Logs、Metrics 和 Traces 相互關聯的設定。

### Step 1: Structured Logging with Correlation
### 第一步：具備關聯性的結構化日誌

Using `console.log` is a performance killer (synchronous blocking in some environments) and hard to parse. We use `pino`.
使用 `console.log` 是效能殺手（在某些環境下是同步阻塞的）且難以解析。我們使用 `pino`。

```javascript
// logger.js
const pino = require('pino');
const { trace, context } = require('@opentelemetry/api');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => {
      return { level: label.toUpperCase() };
    },
    // Inject Trace ID into every log entry
    // 將 Trace ID 注入到每一條日誌中
    log: (object) => {
      const span = trace.getSpan(context.active());
      if (!span) return object;
      const { spanId, traceId } = span.spanContext();
      return { ...object, span_id: spanId, trace_id: traceId };
    },
  },
  // In production, use asynchronous logging to avoid blocking event loop
  // 在生產環境中，使用非同步日誌以避免阻塞 Event Loop
  transport: process.env.NODE_ENV === 'production' 
    ? { target: 'pino/file', options: { destination: 1 } } // stdout
    : undefined
});

module.exports = logger;
```

### Step 2: OpenTelemetry Instrumentation
### 第二步：OpenTelemetry 儀表化

This code must run **before** any other module is required.
這段程式碼必須在任何其他模組被 require **之前** 執行。

```javascript
// instrumentation.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-grpc');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');

// Configure Exporters (sending data to OTel Collector)
// 配置 Exporters（將數據發送到 OTel Collector）
const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317', // Default OTel Collector gRPC port
});

const metricExporter = new OTLPMetricExporter({
  url: 'http://localhost:4317',
});

const sdk = new NodeSDK({
  serviceName: 'order-service',
  traceExporter,
  metricReader: new PeriodicExportingMetricReader({
    exporter: metricExporter,
    exportIntervalMillis: 10000,
  }),
  // Auto-instrument common modules: Http, Express, Postgres, Redis, etc.
  // 自動儀表化常用模組：Http, Express, Postgres, Redis 等
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});
```

### Step 3: Production Profiling (On-Demand)
### 第三步：生產環境 Profiling（隨選即用）

When CPU spikes to 100%, you need a profile. Using `v8-profiler-next` or simply the built-in inspector is powerful.
當 CPU 飆升至 100% 時，你需要 Profile。使用 `v8-profiler-next` 或直接使用內建的 inspector 非常強大。

**Scenario:** You want to capture a heap snapshot without stopping the server.
**情境：** 你想在不停止伺服器的情況下捕捉 Heap Snapshot。

```javascript
// debug-utils.js
const inspector = require('inspector');
const fs = require('fs');

function captureHeapSnapshot() {
  const session = new inspector.Session();
  session.connect();

  const fd = fs.openSync(`heap-${Date.now()}.heapsnapshot`, 'w');

  session.post('HeapProfiler.takeHeapSnapshot', null, (err, r) => {
    console.log('Snapshot done');
    session.disconnect();
    fs.closeSync(fd);
  });
}

// Trigger via a specific signal or a secured admin API endpoint
// 透過特定訊號或受保護的管理 API 端點觸發
process.on('SIGUSR2', captureHeapSnapshot);
```

*Note: In a containerized environment (Kubernetes), you might trigger this via `kubectl exec` sending the signal.*
*注意：在容器化環境（Kubernetes）中，你可以透過 `kubectl exec` 發送訊號來觸發此操作。*

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 High Cardinality Metrics (The "Explosion" Problem)
### 5.1 高基數 Metrics（「爆炸」問題）

*   **Anti-pattern:** Including User IDs, Email addresses, or full URLs (with query params) as metric labels.
    **反模式：** 將 User ID、Email 地址或完整的 URL（包含查詢參數）作為 Metric 的標籤（Label）。
    ```javascript
    // BAD: Creates a new timeseries for every user
    // 壞範例：為每個使用者建立一個新的時間序列
    requestCounter.add(1, { user_id: req.user.id }); 
    ```
*   **Why it's bad:** Time-series databases (Prometheus, InfluxDB) index every unique combination of labels. Millions of users = Millions of indexes = DB crash.
    **為何不好：** 時間序列資料庫（Prometheus、InfluxDB）會為每個唯一的標籤組合建立索引。數百萬使用者 = 數百萬索引 = 資料庫崩潰。
*   **Solution:** Use low cardinality values (Status Code, Route Template, Region). Put high cardinality data in **Logs** or **Traces**, not Metrics.
    **解決方案：** 使用低基數值（狀態碼、路由模板、區域）。將高基數數據放在 **Logs** 或 **Traces** 中，而非 Metrics。

### 5.2 Blocking the Event Loop with Observability
### 5.2 因可觀測性阻塞 Event Loop

*   **Anti-pattern:** Synchronous logging to console or file in production.
    **反模式：** 在生產環境中同步將日誌寫入 console 或檔案。
*   **Why it's bad:** `console.log` writes to `stdout`. In some container runtimes or if piped to a slow consumer, this blocks the V8 thread.
    **為何不好：** `console.log` 寫入 `stdout`。在某些容器執行環境中，或者如果管道連接到一個緩慢的消費者，這會阻塞 V8 執行緒。
*   **Solution:** Use logging libraries with asynchronous buffering (like `pino.destination({ sync: false })`).
    **解決方案：** 使用具備非同步緩衝功能的日誌庫（如 `pino.destination({ sync: false })`）。

### 5.3 Over-Tracing
### 5.3 過度追蹤

*   **Anti-pattern:** Tracing health checks (`/healthz`) or static asset requests.
    **反模式：** 追蹤健康檢查（`/healthz`）或靜態資源請求。
*   **Why it's bad:** Adds noise to your data and increases storage costs significantly.
    **為何不好：** 增加數據雜訊並顯著增加儲存成本。
*   **Solution:** Configure your OTel sampler or HTTP instrumentation to ignore specific routes.
    **解決方案：** 配置 OTel 採樣器或 HTTP 儀表化設定以忽略特定路由。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you debug a memory leak in a production Node.js service without restarting it?
### Q1: 你如何在不重啟的情況下，除錯生產環境中 Node.js 服務的記憶體洩漏？

*   **Key Points:**
    *   **Metrics First:** Identify the leak trend via metrics (Heap Used increasing over time, frequent GC).
    *   **Heap Snapshots:** Explain taking multiple snapshots (e.g., using `heapdump` or Inspector API) and comparing them (Allocation comparison) to find objects that are not being GC'd.
    *   **Impact Management:** Acknowledge that taking a snapshot pauses the main thread. Suggest doing it on a canary instance or removing the instance from the load balancer briefly.
    *   **Common Culprits:** Mention closures, global variables, or event listeners not being removed.
    *   **關鍵點：**
        *   **Metrics 優先：** 透過 Metrics 確認洩漏趨勢（Heap Used 隨時間增加、頻繁 GC）。
        *   **Heap Snapshots：** 說明獲取多個快照（例如使用 `heapdump` 或 Inspector API）並進行比較（分配比較），找出未被 GC 回收的物件。
        *   **影響管理：** 承認獲取快照會暫停主執行緒。建議在 Canary 實例上進行，或暫時將該實例從負載平衡器中移除。
        *   **常見元兇：** 提及閉包（Closures）、全域變數或未移除的事件監聽器。

### Q2: Why is "Event Loop Lag" a critical metric, and how is it measured?
### Q2: 為什麼 "Event Loop Lag" 是一個關鍵指標，它是如何測量的？

*   **Key Points:**
    *   **Definition:** It measures the delay between scheduling a callback and its execution. It indicates if the CPU is blocked by synchronous code.
    *   **Consequence:** High lag means the server cannot accept new requests or process I/O, leading to timeouts even if CPU usage isn't 100%.
    *   **Measurement:** Use `perf_hooks.monitorEventLoopDelay()` (modern) or a simple `setTimeout` loop (legacy) to measure the delta between expected and actual execution time.
    *   **關鍵點：**
        *   **定義：** 測量排程一個 callback 到其實際執行之間的延遲。它顯示 CPU 是否被同步程式碼阻塞。
        *   **後果：** 高延遲意味著伺服器無法接受新請求或處理 I/O，即使 CPU 使用率未達 100% 也會導致超時。
        *   **測量：** 使用 `perf_hooks.monitorEventLoopDelay()`（現代做法）或簡單的 `setTimeout` 迴圈（傳統做法）來測量預期與實際執行時間的差值。

### Q3: How does context propagation work in Node.js across async boundaries?
### Q3: 在 Node.js 中，上下文傳遞是如何跨越非同步邊界運作的？

*   **Key Points:**
    *   Explain **`AsyncLocalStorage`** (ALS) as the underlying mechanism.
    *   It allows storing data (like Trace ID) that is accessible throughout the lifetime of an asynchronous resource chain.
    *   Before ALS, we relied on monkey-patching (like `continuation-local-storage`) which was fragile.
    *   OTel uses ALS to maintain the "Span" context.
    *   **關鍵點：**
        *   解釋 **`AsyncLocalStorage`** (ALS) 為底層機制。
        *   它允許儲存可在非同步資源鏈的整個生命週期中存取的數據（如 Trace ID）。
        *   在 ALS 之前，我們依賴 Monkey-patching（如 `continuation-local-storage`），那很脆弱。
        *   OTel 使用 ALS 來維護 "Span" 上下文。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Three Pillars:** Observability requires correlating **Logs** (events), **Metrics** (aggregates), and **Traces** (workflow).
    **三大支柱：** 可觀測性需要關聯 **Logs**（事件）、**Metrics**（聚合數據）和 **Traces**（工作流）。
2.  **OpenTelemetry is Standard:** Use OTel SDKs for vendor-neutral instrumentation.
    **OpenTelemetry 是標準：** 使用 OTel SDK 進行與供應商無關的儀表化。
3.  **Correlation is Key:** Always inject `trace_id` into your logs to jump from a log error to a full distributed trace.
    **關聯性是關鍵：** 務必將 `trace_id` 注入日誌，以便從日誌錯誤跳轉到完整的分散式追蹤。
4.  **AsyncLocalStorage:** The engine powering context propagation in Node.js.
    **AsyncLocalStorage：** 驅動 Node.js 上下文傳遞的引擎。
5.  **Watch the Loop:** Monitor Event Loop Lag specifically; it's the heartbeat of a Node.js app.
    **關注 Event Loop：** 特別監控 Event Loop Lag；它是 Node.js 應用程式的心跳。

### Next Steps
### 後續延伸

*   **Advanced Profiling:** Learn to use Linux `perf` or eBPF tools to profile Node.js at the kernel level (outside the V8 runtime).
    **進階 Profiling：** 學習使用 Linux `perf` 或 eBPF 工具在核心層級（V8 執行環境之外）對 Node.js 進行剖析。
*   **Alerting Strategy:** Design SLOs (Service Level Objectives) and SLIs (Service Level Indicators) based on the metrics you collected.
    **告警策略：** 根據收集到的 Metrics 設計 SLOs（服務層級目標）和 SLIs（服務層級指標）。
*   **Next Chapter:** Proceed to **Performance Optimization & Internals** to learn how to fix the bottlenecks you identified using these observability tools.
    **下一章：** 進入 **效能優化與內部原理**，學習如何修復你利用這些可觀測性工具所發現的瓶頸。