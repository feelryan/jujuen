# 1. 前言與學習目標 (Introduction & Learning Objectives)

在傳統的單體架構中，如果系統變慢，我們通常只需要查看單一伺服器的 CPU 使用率或應用程式日誌。然而，在雲原生與微服務架構中，一個使用者請求可能橫跨數十個服務與基礎設施元件。這時，「監控（Monitoring）」告訴你系統**是否**壞了，而「可觀測性（Observability）」則賦予你能力去詢問系統**為什麼**壞了。

In traditional monolithic architectures, if the system slowed down, we usually only needed to check the CPU usage or application logs of a single server. However, in cloud-native and microservices architectures, a single user request might traverse dozens of services and infrastructure components. In this context, "Monitoring" tells you **if** the system is broken, while "Observability" gives you the power to ask the system **why** it is broken.

完成本章後，身為資深工程師的你應該能夠：

After completing this chapter, as a senior engineer, you should be able to:

1.  **區分監控與可觀測性**：理解為何在複雜的分散式系統中，僅有 Dashboard 是不夠的。
    **Distinguish between Monitoring and Observability:** Understand why dashboards alone are insufficient in complex distributed systems.
2.  **掌握三大支柱（The Three Pillars）**：深入理解 Logging、Metrics 與 Tracing 的資料特性、儲存成本與適用場景。
    **Master the Three Pillars:** Deeply understand the data characteristics, storage costs, and use cases of Logging, Metrics, and Tracing.
3.  **實作 OpenTelemetry (OTel)**：學會如何標準化數據收集，並利用 Context Propagation（上下文傳播）串聯跨服務的請求。
    **Implement OpenTelemetry (OTel):** Learn how to standardize data collection and use Context Propagation to link requests across services.
4.  **設計採樣策略（Sampling Strategies）**：在系統設計面試或實務中，解決海量 Trace 數據帶來的效能與成本問題。
    **Design Sampling Strategies:** Solve performance and cost issues caused by massive Trace data in system design interviews or practice.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 監控 vs. 可觀測性 (Monitoring vs. Observability)

**直覺類比**：
監控就像是汽車儀表板上的「引擎檢查燈」，它亮起時你知道有問題，但不知道具體壞在哪。可觀測性則是當你打開引擎蓋，擁有完整的診斷電腦，可以查詢每個零件在特定時間點的狀態、溫度與訊號流向。

**Intuitive Analogy:**
Monitoring is like the "Check Engine" light on a car dashboard; when it lights up, you know there is a problem, but you don't know exactly what is wrong. Observability is like opening the hood and having a full diagnostic computer that can query the status, temperature, and signal flow of every part at a specific point in time.

**定義**：
可觀測性是系統的一種屬性，衡量我們能多大程度上僅透過其外部輸出（Logs, Metrics, Traces）來推斷其內部狀態。

**Definition:**
Observability is a property of a system, measuring how well we can infer its internal state solely from its external outputs (Logs, Metrics, Traces).

### 2.2 三大支柱 (The Three Pillars)

1.  **Metrics (指標)**：
    -   **What:** 可聚合的數值資料（Aggregatable numerical data）。
    -   **Use Case:** 趨勢分析、警報（Alerting）。例如：「過去 5 分鐘的平均延遲」、「目前的 CPU 使用率」。
    -   **Cost:** 低。成本與流量無關，與「維度（Cardinality）」有關。
2.  **Logs (日誌)**：
    -   **What:** 離散的事件紀錄（Discrete event records）。
    -   **Use Case:** 深入除錯、稽核（Auditing）。例如：「User X 在 10:00 付款失敗，錯誤訊息為 Y」。
    -   **Cost:** 高。成本隨流量線性增長。
3.  **Tracing (追蹤)**：
    -   **What:** 請求在服務間的傳播路徑與生命週期（Request lifecycle across services）。
    -   **Use Case:** 效能瓶頸定位、依賴關係分析。例如：「Checkout 服務呼叫 Inventory 服務花了 2 秒」。
    -   **Cost:** 中至高。通常需要採樣（Sampling）。

### 2.3 OpenTelemetry (OTel)

過去，Metrics 可能用 Prometheus SDK，Tracing 用 Jaeger SDK，導致程式碼充滿不同廠商的 library。**OpenTelemetry** 是目前的產業標準（CNCF 專案），提供了一套統一的 API、SDK 與通訊協定（OTLP），讓應用程式只需 instrument 一次，就能將數據發送到任何後端。

In the past, Metrics might have used the Prometheus SDK, and Tracing the Jaeger SDK, cluttering the code with vendor-specific libraries. **OpenTelemetry** is the current industry standard (CNCF project), providing a unified set of APIs, SDKs, and protocols (OTLP), allowing applications to be instrumented once and send data to any backend.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，可觀測性通常是「非功能性需求（Non-functional Requirements）」的關鍵部分。

In system design interviews or architectural planning, observability is often a critical part of "Non-functional Requirements".

### 3.1 架構元件 (Architecture Components)

一個典型的 Cloud-Native 可觀測性 pipeline 包含以下角色：

A typical Cloud-Native observability pipeline includes the following roles:

1.  **Instrumentation (SDKs/Agents):**
    應用程式內的程式碼，負責產生數據。現今多使用 Auto-instrumentation（如 Java Agent）或手動埋點。
    Code within the application responsible for generating data. Nowadays, Auto-instrumentation (e.g., Java Agent) or manual instrumentation is often used.

2.  **Collector (e.g., OTel Collector):**
    **關鍵角色**。它作為 Sidecar 或 DaemonSet 運行，負責接收應用程式的數據，進行處理（過濾、批次、匿名化），然後匯出到後端。這解耦了 App 與 Backend。
    **Key Role.** It runs as a Sidecar or DaemonSet, responsible for receiving data from applications, processing it (filtering, batching, anonymizing), and then exporting it to the backend. This decouples the App from the Backend.

3.  **Storage & Analysis Backends:**
    -   **Metrics:** Prometheus, Thanos, Cortex (Time-series DB).
    -   **Logs:** Elasticsearch (ELK), Loki, Splunk.
    -   **Traces:** Jaeger, Tempo, Honeycomb.

4.  **Visualization:**
    Grafana 是最常見的統一前端，能同時展示這三種數據。
    Grafana is the most common unified frontend, capable of displaying all three types of data simultaneously.

### 3.2 關聯性設計 (Correlation Design)

資深工程師必須確保這三大支柱不是孤島。
**Trace ID** 是串聯一切的關鍵。

Senior engineers must ensure these three pillars are not silos.
The **Trace ID** is the key to linking everything together.

*   **Logs <-> Traces:** 在每一行 Log 中自動注入目前的 `TraceID` 與 `SpanID`。這樣你在看 Log 時，可以直接跳轉到對應的 Trace 瀑布圖。
    **Logs <-> Traces:** Automatically inject the current `TraceID` and `SpanID` into every log line. This allows you to jump directly to the corresponding Trace waterfall chart when viewing logs.
*   **Metrics <-> Traces:** 使用 Exemplars（範例）。在 Metrics 的直方圖（Histogram）中，保留幾個具代表性的 Trace ID，讓你知道「這個 P99 延遲的請求具體是哪一個」。
    **Metrics <-> Traces:** Use Exemplars. In Metrics histograms, retain a few representative Trace IDs so you know "exactly which request caused this P99 latency".

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)
你的電商平台收到客訴，結帳 API (`POST /checkout`) 偶爾會非常慢（超過 5 秒），但 CPU 和記憶體監控看起來都很正常。

Your e-commerce platform receives complaints that the checkout API (`POST /checkout`) is occasionally very slow (over 5 seconds), but CPU and memory monitoring look normal.

### 步驟 1：傳統方法的侷限 (The Limitation of Traditional Approach)
你登入機器並 `grep` 日誌。你看到了成千上萬行 log，但很難分辨哪一行屬於那個慢的請求。即使找到了，你只看到「開始處理」和「處理結束」，中間發生了什麼事（例如呼叫了庫存服務、金流服務）完全是黑盒子。

You log into the machine and `grep` the logs. You see thousands of lines, but it's hard to distinguish which line belongs to the slow request. Even if you find it, you only see "Start processing" and "End processing"; what happened in between (e.g., calling inventory service, payment service) is a complete black box.

### 步驟 2：引入 Distributed Tracing (Introducing Distributed Tracing)

我們使用 OpenTelemetry Go SDK 來包裝 HTTP Handler 並傳遞 Context。

We use the OpenTelemetry Go SDK to wrap the HTTP Handler and propagate the Context.

```go
// Middleware to start a span
func OTelMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 1. Extract context from incoming headers (W3C Trace Context)
        // 從傳入的標頭中提取上下文（W3C Trace Context）
        ctx := r.Context()
        tracer := otel.Tracer("checkout-service")
        
        // 2. Start a new span
        // 啟動一個新的 span
        ctx, span := tracer.Start(ctx, r.URL.Path)
        defer span.End()

        // 3. Inject TraceID into Logs (Conceptually)
        // 將 TraceID 注入日誌（概念上）
        log.WithField("trace_id", span.SpanContext().TraceID()).Info("Request started")

        // 4. Pass the context down
        // 向下傳遞上下文
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func CheckoutHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    
    // Call Inventory Service
    // 呼叫庫存服務
    err := callInventoryService(ctx)
    if err != nil {
        // Record error in span
        // 在 span 中記錄錯誤
        span := trace.SpanFromContext(ctx)
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
    }
}

func callInventoryService(ctx context.Context) error {
    // Start a child span
    // 啟動子 span
    tracer := otel.Tracer("checkout-service")
    ctx, span := tracer.Start(ctx, "call_inventory")
    defer span.End()

    // Simulate HTTP call with context propagation
    // 模擬帶有上下文傳播的 HTTP 呼叫
    req, _ := http.NewRequestWithContext(ctx, "GET", "http://inventory/check", nil)
    
    // The HTTP client automatically injects trace headers into the request
    // HTTP 客戶端會自動將 trace headers 注入請求中
    // ... logic to send request ...
    return nil
}
```

### 步驟 3：分析 Trace 瀑布圖 (Analyzing the Trace Waterfall)
在 Grafana/Jaeger 中，你輸入 `service="checkout-service" AND duration > 5s`。
你看到了一個 Trace，其結構如下：

In Grafana/Jaeger, you query `service="checkout-service" AND duration > 5s`.
You see a Trace with the following structure:

-   `checkout-service` (Total: 5.1s)
    -   `auth-service` (50ms)
    -   `inventory-service` (4.9s) ⚠️ **Bottleneck Found!**
        -   `db-query: select * from items...` (4.8s) ⚠️ **Root Cause: Missing Index**
    -   `payment-service` (150ms)

**結論**：問題不在 checkout 服務本身，而在於 inventory 服務的資料庫查詢缺少索引。Tracing 讓我們能在幾秒鐘內跨服務定位問題。

**Conclusion:** The problem is not in the checkout service itself, but in a missing index in the inventory service's database query. Tracing allows us to pinpoint issues across services in seconds.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 指標基數爆炸 (High Cardinality Metrics)
**錯誤**：將高變動性的資料放入 Metrics 的 Label (Tag) 中。
**Mistake:** Putting highly variable data into Metrics Labels (Tags).

```go
// BAD: UserID has millions of possibilities
// 壞的範例：UserID 有數百萬種可能性
metrics.Counter("http_requests_total").WithLabel("user_id", userID).Inc()
```

**為何不好**：Prometheus 等時序資料庫會為每個 Label 組合建立一個新的時間序列。如果 `user_id` 有 100 萬個，你的記憶體和儲存會迅速爆炸。
**Why it's bad:** Time-series databases like Prometheus create a new time series for each label combination. If `user_id` has 1 million values, your memory and storage will explode rapidly.

**正確做法**：將 `user_id` 放入 **Logs** 或 **Traces**，Metrics 只保留低基數資料（如 `status_code`, `method`, `service_version`）。
**Best Practice:** Put `user_id` in **Logs** or **Traces**, and keep Metrics for low-cardinality data (e.g., `status_code`, `method`, `service_version`).

### 5.2 盲目採樣 (Blind Sampling)
**錯誤**：對所有請求進行 100% 的 Tracing 記錄。
**Mistake:** Recording 100% of Traces for all requests.

**為何不好**：在流量大的系統中，儲存與傳輸 Trace 的成本極高，且 99% 的成功請求 Trace 價值很低。
**Why it's bad:** In high-traffic systems, the cost of storing and transmitting Traces is extremely high, and 99% of successful request traces have low value.

**正確做法**：
1.  **Probabilistic Sampling (Head-based):** 隨機紀錄 1% 或 0.1% 的請求。
2.  **Tail-based Sampling:** 先暫存所有 Trace，只保留「發生錯誤」或「延遲過高」的 Trace（需要較複雜的架構，如 OTel Collector Load Balancing）。

### 5.3 日誌缺乏結構化 (Unstructured Logging)
**錯誤**：使用 `printf("User %s failed", user)`。
**Mistake:** Using `printf("User %s failed", user)`.

**為何不好**：難以查詢和聚合。你無法輕易回答「有多少錯誤是來自 User A？」
**Why it's bad:** Hard to query and aggregate. You cannot easily answer "How many errors came from User A?"

**正確做法**：使用 JSON 結構化日誌。`logger.Info("login failed", "user", user, "reason", err)`。
**Best Practice:** Use JSON structured logging.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋 Head-based Sampling 與 Tail-based Sampling 的差異與取捨？
**Explain the difference and trade-offs between Head-based and Tail-based Sampling.**

*   **高分回答要點**：
    *   **Head-based**：在請求開始時（Root Span）就決定是否採樣。優點是簡單、效能開銷低；缺點是可能會錯過那些「罕見但重要」的錯誤請求（如果運氣不好沒被抽中）。
    *   **Tail-based**：在請求結束後，根據結果（是否有 Error，是否 Latency > X）決定是否保留。優點是能精準捕捉異常；缺點是需要暫存所有 Spans，對 Collector 的記憶體與架構要求極高。

### Q2: 如果系統導入了 OpenTelemetry，但發現 Trace 資料斷裂（Broken Traces），可能原因為何？
**If OpenTelemetry is implemented but "Broken Traces" are observed, what could be the reasons?**

*   **高分回答要點**：
    *   **Context Propagation 失敗**：某個中間服務沒有正確提取（Extract）並注入（Inject）Trace Context（例如 HTTP Headers 中的 `traceparent`）。
    *   **非同步處理**：請求被放入 Message Queue（如 Kafka），但 Consumer 沒有正確繼承 Producer 的 Context。
    *   **第三方服務**：呼叫了不支援 Trace 標準的外部 API 或資料庫。

### Q3: 在微服務架構中，如何設計一個具備成本效益的可觀測性平台？
**How to design a cost-effective observability platform in a microservices architecture?**

*   **高分回答要點**：
    *   **分層儲存**：熱數據（近 3 天）存高效能 SSD，冷數據存 S3/GCS。
    *   **積極採樣**：對成功請求進行低採樣率，對錯誤請求進行高採樣率。
    *   **預聚合 (Pre-aggregation)**：在 Collector 層將原始 Trace 轉換為 Metrics（如 Span Metrics），然後丟棄原始 Trace，只留統計數據。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **可觀測性 > 監控**：不僅要知道系統壞了，還要能快速找出原因。
2.  **三大支柱**：Metrics (趨勢/警報), Logs (事件詳情), Traces (跨服務路徑)。
3.  **Context Propagation**：是分散式追蹤的靈魂，確保 `TraceID` 能貫穿整個請求鏈路。
4.  **OpenTelemetry**：是目前收集數據的黃金標準，解耦了程式碼與後端廠商。
5.  **Cardinality Matters**：永遠不要將 UserID 或 RequestID 放入 Metrics 的 Label 中。

### 後續延伸 (Next Steps)
*   **Service Mesh (Chapter 09)**：學習 Istio 或 Linkerd 如何在不修改程式碼的情況下，自動完成大部分的 Metrics 與 Tracing 工作（透明代理）。
*   **Chaos Engineering**：利用可觀測性工具來驗證當你故意注入故障時，系統是否如預期般運作並發出警報。