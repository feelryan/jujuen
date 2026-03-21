# 1. 前言與學習目標 (Introduction & Learning Goals)

在微服務架構中，當一個請求跨越數十個服務、經歷非同步訊息佇列與多個資料庫時，「系統壞了」這句話往往只是調查的起點，而非結論。傳統的單體監控（Monolithic Monitoring）已無法應對這種複雜度。本章將探討如何建構完整的**可觀測性（Observability）**體系。

In a microservices architecture, when a request spans dozens of services, passes through asynchronous message queues, and hits multiple databases, saying "the system is down" is merely the starting point of an investigation, not the conclusion. Traditional monolithic monitoring is no longer sufficient to handle this complexity. This chapter explores how to build a comprehensive **Observability** ecosystem.

完成本章後，你應該能夠：

By the end of this chapter, you should be able to:

1.  **區分監控與可觀測性**：理解 Metrics（指標）、Logging（日誌）與 Tracing（追蹤）這「三大支柱」如何協同工作，而非獨立存在。
    **Distinguish between Monitoring and Observability**: Understand how the "Three Pillars"—Metrics, Logging, and Tracing—work synergistically rather than in isolation.
2.  **設計全鏈路追蹤（Distributed Tracing）**：掌握如何在同步（HTTP/gRPC）與非同步（Kafka/RabbitMQ）邊界中正確傳遞 Context 與 Trace ID。
    **Design Distributed Tracing**: Master the correct propagation of Context and Trace IDs across synchronous (HTTP/gRPC) and asynchronous (Kafka/RabbitMQ) boundaries.
3.  **解決高基數（High Cardinality）問題**：在設計 Metrics 時，避免引入導致監控系統崩潰的標籤（Labels/Tags）。
    **Solve High Cardinality Issues**: Avoid introducing labels/tags in your metrics design that could crash your monitoring system.
4.  **制定採樣策略（Sampling Strategy）**：在海量流量下，權衡成本與資料完整性，選擇適合的 Head-based 或 Tail-based 採樣。
    **Formulate Sampling Strategies**: Balance cost and data integrity under high traffic by choosing the appropriate Head-based or Tail-based sampling.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 可觀測性的三大支柱 (The Three Pillars of Observability)

對於資深工程師而言，不應只將這些視為三種工具，而應視為三種不同維度的資料視圖：

For senior engineers, these should not be viewed merely as three tools, but as three different dimensions of data views:

1.  **Metrics (指標)**:
    *   **定義 (Definition)**: 可聚合的數值資料，通常帶有時間戳記與標籤（Labels）。
    *   **用途 (Purpose)**: 回答「**What** is happening?」（例如：現在的 CPU 使用率是多少？QPS 有多高？）。
    *   **特點 (Characteristics)**: 儲存成本低，適合長期趨勢分析與即時告警，但缺乏單一請求的細節。
    *   **工具 (Tools)**: Prometheus, Datadog, CloudWatch.

2.  **Logging (日誌)**:
    *   **定義 (Definition)**: 離散的事件記錄，包含時間、等級與訊息內容。
    *   **用途 (Purpose)**: 回答「**Why** it happened?」（例如：資料庫連線失敗的錯誤訊息是什麼？）。
    *   **特點 (Characteristics)**: 訊息量大，成本高，包含最豐富的上下文（Context）。
    *   **工具 (Tools)**: ELK Stack (Elasticsearch, Logstash, Kibana), Loki, Splunk.

3.  **Distributed Tracing (分散式追蹤)**:
    *   **定義 (Definition)**: 請求在分散式系統中傳播的路徑記錄。
    *   **用途 (Purpose)**: 回答「**Where** is the bottleneck?」（例如：請求在 Payment Service 停頓了 2 秒）。
    *   **特點 (Characteristics)**: 串聯多個服務的 Log 與 Metrics，是微服務除錯的關鍵。
    *   **工具 (Tools)**: Jaeger, Zipkin, OpenTelemetry, Grafana Tempo.

## 2.2 心智模型：醫療診斷類比 (Mental Model: Medical Diagnosis Analogy)

想像你在診斷一位病人（你的系統）：

Imagine you are diagnosing a patient (your system):

-   **Metrics** 就像**生命徵象儀表板**（心跳、血壓）。它告訴你病人「是否健康」，如果心跳停止，儀器會發出警報（Alerting）。但它無法告訴你為什麼心跳停止。
    **Metrics** are like the **vital signs dashboard** (heart rate, blood pressure). It tells you *if* the patient is healthy. If the heart stops, the machine alerts you. But it won't tell you *why* it stopped.

-   **Tracing** 就像**顯影劑追蹤**。你注入顯影劑（Trace ID），看血液流經身體的每一個器官（Microservices）。你會發現血液在肝臟（某個 Service）堵塞了。
    **Tracing** is like a **contrast dye trace**. You inject the dye (Trace ID) and watch the blood flow through every organ (Microservices). You discover a blockage in the liver (a specific Service).

-   **Logging** 就像**病歷與醫學影像**。當你知道問題出在肝臟後，你調閱詳細的 CT 掃描與病理報告（Logs），發現具體原因是「血管栓塞」（NullPointerException 或 DB Timeout）。
    **Logging** is like the **medical history and imaging**. Once you know the issue is in the liver, you pull up the detailed CT scans and pathology reports (Logs) to find the specific cause is a "blood clot" (NullPointerException or DB Timeout).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design 面試或架構規劃中，可觀測性通常是 "Non-functional Requirements" 的核心部分。

In System Design interviews or architecture planning, observability is often a core part of "Non-functional Requirements".

## 3.1 關聯性：The Golden Thread (Correlation)

最常見的反模式是三大支柱各自獨立。在 Production 環境中，我們必須建立 **Correlation ID**（通常是 Trace ID）。

The most common anti-pattern is having the three pillars isolated. In a Production environment, we must establish a **Correlation ID** (usually the Trace ID).

*   **Log Injection**: 每一行 Log 都必須自動附帶 `trace_id` 與 `span_id`。這樣當你在 Tracing UI 看到一個慢請求時，可以直接跳轉到該請求的所有 Logs。
    **Log Injection**: Every log line must automatically include `trace_id` and `span_id`. This way, when you see a slow request in the Tracing UI, you can jump directly to all Logs for that request.
*   **Exemplars**: 在 Metrics（如 Histogram）中嵌入 Trace ID 範例。當你在 Grafana 看到 P99 延遲飆高時，點擊該數據點可以直接看到一個具體的 Trace 範例。
    **Exemplars**: Embedding Trace ID examples in Metrics (like Histograms). When you see P99 latency spiking in Grafana, clicking that data point reveals a specific Trace example.

## 3.2 採樣策略 (Sampling Strategies)

在 Google 或 Netflix 級別的流量下，記錄 100% 的 Trace 是不切實際且昂貴的。

At Google or Netflix scale, recording 100% of Traces is impractical and expensive.

1.  **Head-based Sampling**:
    *   **機制**: 請求剛進入系統（Ingress）時就決定是否採樣（例如隨機 1%）。
    *   **優點**: 效能開銷低，對下游服務透明。
    *   **缺點**: 可能會錯過那些「發生錯誤」或「極端延遲」的請求（因為它們剛好沒被選中）。
    *   **Mechanism**: Decide whether to sample when the request first enters the system (Ingress) (e.g., random 1%).
    *   **Pros**: Low performance overhead, transparent to downstream services.
    *   **Cons**: You might miss requests that "error out" or have "extreme latency" (because they just happened not to be picked).

2.  **Tail-based Sampling**:
    *   **機制**: 先暫存所有 Span，等請求結束後，根據結果（是否有 Error、是否超過 2秒）決定是否保留。
    *   **優點**: 保證能捕捉到異常與慢請求。
    *   **缺點**: 需要巨大的緩存資源與複雜的後端架構。
    *   **Mechanism**: Buffer all Spans, and after the request finishes, decide whether to keep them based on the outcome (was there an Error? did it exceed 2s?).
    *   **Pros**: Guarantees capturing anomalies and slow requests.
    *   **Cons**: Requires massive buffering resources and complex backend architecture.

## 3.3 高基數災難 (The High Cardinality Disaster)

這是資深工程師必須防範的陷阱。

This is a pitfall senior engineers must guard against.

*   **Cardinality**: 一個 Metric 中唯一組合的數量。
    **Cardinality**: The number of unique combinations in a Metric.
*   **Bad Practice**: `http_request_duration_seconds{user_id="uuid-1234"}`. 如果你有 100 萬個使用者，這會產生 100 萬條時間序列，導致 Prometheus 記憶體溢出。
    **Bad Practice**: `http_request_duration_seconds{user_id="uuid-1234"}`. If you have 1 million users, this creates 1 million time series, causing Prometheus to OOM (Out of Memory).
*   **Good Practice**: 把 `user_id` 放在 **Logs** 或 **Trace Tags** 中，而不是 Metrics Labels 中。Metrics 只保留低基數標籤（如 `status_code`, `service_name`, `region`）。
    **Good Practice**: Put `user_id` in **Logs** or **Trace Tags**, not in Metrics Labels. Metrics should only keep low-cardinality labels (like `status_code`, `service_name`, `region`).

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：除錯「偶發性結帳緩慢」 (Scenario: Debugging "Intermittent Slow Checkout")

**背景**: 使用者回報在結帳時偶爾會卡住 5 秒以上，但監控顯示平均延遲正常。

**Context**: Users report that checkout occasionally hangs for over 5 seconds, but monitoring shows average latency is normal.

### 步驟 1: Metrics 發現異常 (Metrics Detect Anomaly)

我們不看平均值（Average），而是看 **P99 Latency**。

We don't look at the Average; we look at **P99 Latency**.

```promql
# Prometheus Query
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="checkout"}[5m])) by (le))
```

結果顯示 P99 確實有尖峰。

The result shows a spike in P99.

### 步驟 2: 透過 Trace 定位瓶頸 (Locate Bottleneck via Trace)

我們進入 Jaeger/Tempo，搜尋 `service="checkout"` 且 `duration > 5s` 的 Trace。
找到一個 Trace ID: `1a2b3c4d`。

We go into Jaeger/Tempo, search for traces where `service="checkout"` and `duration > 5s`.
We find a Trace ID: `1a2b3c4d`.

**Trace View**:
- `Checkout Service` (Total: 5.1s)
  - `Auth Service` (50ms)
  - `Inventory Service` (40ms)
  - `Payment Service` (5.0s) !!! **Root Cause Candidate**

### 步驟 3: 關聯 Logs 尋找根因 (Correlate Logs for Root Cause)

我們拿著 Trace ID `1a2b3c4d` 去 Log 系統（如 Kibana）搜尋。

We take Trace ID `1a2b3c4d` and search in the Log system (e.g., Kibana).

*Query*: `trace_id: "1a2b3c4d" AND service: "payment-service"`

*Log Result*:
```json
{
  "timestamp": "2023-10-27T10:00:05Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "1a2b3c4d",
  "msg": "Database lock wait timeout exceeded; try restarting transaction",
  "db_query": "UPDATE accounts SET balance = ..."
}
```
**結論**: 資料庫鎖競爭（Lock Contention）導致 Payment Service 超時。

**Conclusion**: Database lock contention caused the Payment Service to timeout.

### 程式碼實作：Context Propagation (Code Implementation)

在 Go 中使用 OpenTelemetry 傳遞 Context 是關鍵。若 Context 中斷，Trace 就會斷裂。

In Go, using OpenTelemetry to propagate Context is key. If Context is dropped, the Trace breaks.

```go
// BAD: Losing context
func (s *Server) HandleCheckout(w http.ResponseWriter, r *http.Request) {
    // Creating a new context breaks the trace chain from the incoming request
    ctx := context.Background() 
    s.paymentClient.Process(ctx, order) 
}

// GOOD: Propagating context
func (s *Server) HandleCheckout(w http.ResponseWriter, r *http.Request) {
    // 1. Extract context from incoming HTTP request (contains TraceID)
    ctx := r.Context()
    
    // 2. Start a new span for this operation
    tracer := otel.Tracer("checkout-service")
    ctx, span := tracer.Start(ctx, "HandleCheckout")
    defer span.End()

    // 3. Pass the SAME context to downstream dependencies
    // The HTTP client will automatically inject TraceID into headers
    err := s.paymentClient.Process(ctx, order)
    
    if err != nil {
        // Record error in span
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
    }
}
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 "Log and Throw" (記錄並拋出)

這是程式碼中最常見的噪音來源。

This is the most common source of noise in code.

*   **Anti-pattern**:
    ```java
    try {
        callService();
    } catch (Exception e) {
        logger.error("Service failed", e); // Log 1
        throw e; // Rethrow
    }
    ```
    如果在 5 層的 Stack 中每一層都這樣做，同一個錯誤會被記錄 5 次，汙染 Log 系統並增加成本。

    If you do this in every layer of a 5-layer stack, the same error gets logged 5 times, polluting the log system and increasing costs.

*   **Solution**: 只在最上層（Entry Point）或完全處理掉錯誤的地方記錄 Log。中間層只負責豐富 Context（Wrap Error）。
    **Solution**: Only log at the top level (Entry Point) or where the error is fully handled. Middle layers should only enrich the Context (Wrap Error).

## 5.2 忽略非同步邊界 (Ignoring Async Boundaries)

當請求被放入 Kafka 或 RabbitMQ 時，Trace Context 不會自動傳遞，除非你手動處理。

When a request is put into Kafka or RabbitMQ, the Trace Context does not propagate automatically unless you handle it manually.

*   **Pitfall**: 生產者發送訊息，消費者處理訊息，但在 Tracing UI 中這是兩條不相干的 Trace。
    **Pitfall**: Producer sends a message, Consumer processes it, but in the Tracing UI, these appear as two unrelated Traces.
*   **Solution**: 在訊息的 Header/Metadata 中注入 `traceparent`。消費者讀取 Header 並提取 Context (`Extract`)，作為新 Span 的 Parent。
    **Solution**: Inject `traceparent` into the message Header/Metadata. The Consumer reads the Header, extracts the Context (`Extract`), and uses it as the Parent of the new Span.

## 5.3 過度依賴 Log 進行監控 (Over-reliance on Logs for Monitoring)

*   **Pitfall**: 使用 Log 分析工具計算 QPS 或錯誤率。
    **Pitfall**: Using log analysis tools to calculate QPS or error rates.
*   **Why it's bad**: Log 處理非常昂貴且延遲高。
    **Why it's bad**: Log processing is very expensive and has high latency.
*   **Solution**: 使用 Metrics (Counters/Histograms) 進行聚合數據監控。Log 只用於除錯細節。
    **Solution**: Use Metrics (Counters/Histograms) for aggregated data monitoring. Use Logs only for debugging details.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你如何設計一個支援百萬級 QPS 的分散式追蹤系統？
**How would you design a distributed tracing system supporting 1M QPS?**

*   **高分回答要點 (Key Points)**:
    *   **採樣 (Sampling)**: 必須提到 Head-based sampling (例如 0.1%) 來保護儲存與頻寬。若需要精準捕捉錯誤，可討論 Tail-based sampling 的架構挑戰（需要 buffering layer）。
    *   **儲存 (Storage)**: 選擇寫入優化的 DB（如 Cassandra, Elasticsearch 或 ClickHouse）。
    *   **非同步寫入 (Async Write)**: Agent (Sidecar) 收集 Spans 後，透過 UDP 或 gRPC 批量非同步發送到 Collector，避免阻塞主業務邏輯。

## Q2: 在微服務中，Metrics 和 Logs 的邊界在哪裡？如果我想知道「哪個 User 買了什麼」，該放哪？
**In microservices, where is the boundary between Metrics and Logs? If I want to know "which User bought what", where should it go?**

*   **高分回答要點 (Key Points)**:
    *   **Cardinality Rule**: User ID 是高基數資料，絕對不能放入 Metrics 的 Label。
    *   **Logs/Trace**: 具體的交易細節（User ID, Item ID）應放入 Structured Logs 或 Trace Spans 的 Attributes 中。
    *   **Metrics**: 僅用於記錄「購買發生了」（Counter +1）以及「購買金額分佈」（Histogram），標籤僅限於 `category` 或 `region` 等低基數維度。

## Q3: 系統變慢了，但 CPU 和 Memory 都很低，你會怎麼排查？
**The system is slow, but CPU and Memory are low. How do you troubleshoot?**

*   **高分回答要點 (Key Points)**:
    *   這通常意味著 **I/O Wait** 或 **Lock Contention**。
    *   **Tracing**: 檢查 Span 是否有大段的空白時間（Gap）或長時間的 DB/Network 呼叫。
    *   **Saturation Metrics**: 檢查 Thread Pool 是否滿了？DB Connection Pool 是否耗盡？
    *   **Logs**: 尋找 Timeout 或 Connection Refused 的錯誤。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **三大支柱 (Three Pillars)**: Metrics (趨勢/告警), Logs (細節/原因), Tracing (路徑/瓶頸)。
2.  **關聯性 (Correlation)**: 透過 Trace ID 將 Metrics、Logs 與 Tracing 串聯起來是可觀測性的靈魂。
3.  **基數控制 (Cardinality Control)**: 嚴禁在 Metrics 中使用 User ID 或 Request ID 等高基數標籤。
4.  **上下文傳遞 (Context Propagation)**: 在程式碼中（尤其是跨服務與非同步呼叫）正確傳遞 Context 是 Tracing 生效的前提。
5.  **採樣權衡 (Sampling Trade-off)**: 理解 Head-based 與 Tail-based 採樣在成本與可視性之間的取捨。

## 下一步 (Next Steps)

*   **Service Mesh (Istio/Linkerd)**: 學習如何透過 Sidecar 模式自動完成 Metrics 與 Tracing 的收集，減少對業務程式碼的侵入（Chapter 07）。
*   **OpenTelemetry**: 深入實作 OTel Collector 的配置，學習如何標準化遙測數據的收集與導出。
*   **SLO/SLI**: 從技術指標（CPU/Latency）轉向業務可靠性指標（Service Level Objectives）的定義與監控。