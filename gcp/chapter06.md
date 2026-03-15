# Chapter 06: Observability & SRE Practices
# 第六章：可觀測性與 SRE 維運實務

## 1. 前言與學習目標 (Introduction & Learning Objectives)

In the realm of distributed systems, "Monitoring" tells you whether the system is healthy, while "Observability" allows you to ask why it isn't. For a Senior Engineer, mastering GCP's Cloud Operations Suite is not just about viewing logs; it is about establishing a culture of reliability based on data.

在分散式系統的領域中，「監控（Monitoring）」告訴你系統是否健康，而「可觀測性（Observability）」則讓你能夠探究「為什麼」不健康。對於資深工程師而言，掌握 GCP 的 Cloud Operations Suite 不僅僅是查看 Log，而是建立一種基於數據的可靠性文化。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Distinguish between Monitoring and Observability**: Understand the three pillars (Logs, Metrics, Traces) and how to implement them using GCP native tools.
    **區分監控與可觀測性**：理解三大支柱（Logs, Metrics, Traces）並知曉如何使用 GCP 原生工具實作它們。
2.  **Define and Implement SRE Core Metrics**: Confidently define SLIs (Service Level Indicators) and SLOs (Service Level Objectives), and set up "Error Budget" alerts instead of spammy threshold alerts.
    **定義與實作 SRE 核心指標**：自信地定義 SLI 與 SLO，並設定「錯誤預算（Error Budget）」警報，取代令人疲乏的傳統閾值警報。
3.  **Debug Complex Distributed Systems**: Use Cloud Trace and Cloud Profiler to pinpoint latency bottlenecks across microservices.
    **除錯複雜的分散式系統**：利用 Cloud Trace 與 Cloud Profiler 在微服務架構中精準定位延遲瓶頸。
4.  **Design for Cost-Effective Telemetry**: Manage the volume of logs and metrics to balance visibility with cost (e.g., Log Sinks, Metric Sampling).
    **設計具成本效益的遙測方案**：管理 Log 與 Metric 的資料量，在可視性與成本之間取得平衡（例如：Log Sinks, Metric Sampling）。

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 The Three Pillars in GCP (GCP 中的三大支柱)

Think of Observability as a detective's toolkit. To solve a crime (an outage or bug), you need different types of evidence:
將可觀測性想像成偵探的工具箱。要破案（解決當機或 Bug），你需要不同類型的證據：

1.  **Cloud Logging (The "What"):** Detailed records of discrete events.
    *   *Mental Model:* The "Black Box" flight recorder.
    *   *Key Feature:* **Structured Logging**. Instead of parsing text, you log JSON objects to query fields directly (e.g., `jsonPayload.userId = "123"`).
    *   **Cloud Logging（發生了什麼）：** 離散事件的詳細記錄。
    *   *心智模型：* 飛機的「黑盒子」記錄器。
    *   *關鍵功能：* **結構化日誌（Structured Logging）**。與其解析純文字，不如記錄 JSON 物件以便直接查詢欄位（例如：`jsonPayload.userId = "123"`）。

2.  **Cloud Monitoring (The "Health"):** Aggregated numerical data over time.
    *   *Mental Model:* The car dashboard (Speedometer, Fuel gauge).
    *   *Key Feature:* **Golden Signals** (Latency, Traffic, Errors, Saturation).
    *   **Cloud Monitoring（健康狀況）：** 隨時間聚合的數值資料。
    *   *心智模型：* 汽車儀表板（時速表、油量表）。
    *   *關鍵功能：* **黃金訊號**（延遲、流量、錯誤、飽和度）。

3.  **Cloud Trace (The "Where"):** The path of a request through the system.
    *   *Mental Model:* A courier's tracking history showing every stop a package made.
    *   *Key Feature:* **Distributed Context Propagation**. Passing a `Trace-ID` across HTTP/gRPC headers to stitch services together.
    *   **Cloud Trace（在哪裡）：** 請求在系統中的流轉路徑。
    *   *心智模型：* 快遞的追蹤履歷，顯示包裹經過的每一個站點。
    *   *關鍵功能：* **分散式上下文傳遞**。透過 HTTP/gRPC 標頭傳遞 `Trace-ID` 以串聯各個服務。

### 2.2 SRE Terminology: SLI vs. SLO vs. SLA

This is often a confusion point in interviews.
這在面試中常是混淆點。

*   **SLI (Indicator):** *What are we measuring?* (e.g., "The latency of HTTP 200 responses").
    **SLI（指標）：** *我們在測量什麼？*（例如：「HTTP 200 回應的延遲時間」）。
*   **SLO (Objective):** *What is our target?* (e.g., "99.9% of requests < 300ms over 30 days"). This is an internal goal.
    **SLO（目標）：** *我們的目標是多少？*（例如：「30天內 99.9% 的請求需 < 300ms」）。這是內部目標。
*   **SLA (Agreement):** *What happens if we fail?* (e.g., "If availability < 99.0%, we refund 10%"). This is a legal contract.
    **SLA（協議）：** *如果失敗會怎樣？*（例如：「若可用性 < 99.0%，退款 10%」）。這是法律合約。

> **Senior Insight:** You generally don't alert on SLAs; you alert on SLOs (specifically, the *burn rate* of your error budget) to prevent breaching the SLA.
> **資深觀點：** 你通常不會針對 SLA 設定警報；你是針對 SLO（特別是錯誤預算的 *消耗率*）設定警報，以防止違反 SLA。

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 Architecture: Centralized Observability (架構：集中式可觀測性)

In a microservices environment on GKE or Cloud Run, you cannot rely on SSH-ing into machines. The standard design pattern involves:
在 GKE 或 Cloud Run 的微服務環境中，你無法依賴 SSH 登入機器。標準的設計模式包括：

1.  **Sidecar / Agent Pattern**:
    *   Applications write logs to `stdout/stderr`.
    *   The platform (GKE Fluentbit or Cloud Run agent) captures these streams, enriches them with metadata (Pod name, Project ID), and ships them to Cloud Logging.
    *   **Sidecar / Agent 模式**：
    *   應用程式將 Log 寫入 `stdout/stderr`。
    *   平台（GKE Fluentbit 或 Cloud Run agent）捕捉這些串流，豐富其 Metadata（Pod 名稱、Project ID），並傳送至 Cloud Logging。

2.  **Log Sinks & Exports**:
    *   **Hot Path (Troubleshooting)**: Logs stay in Cloud Logging buckets (retained for 30 days).
    *   **Cold Path (Analytics/Audit)**: Create a **Log Sink** to export logs to **BigQuery** (for SQL analysis) or **Cloud Storage** (for long-term compliance).
    *   **Log Sinks 與匯出**：
    *   **熱路徑（除錯）**：Log 留在 Cloud Logging buckets（保留 30 天）。
    *   **冷路徑（分析/稽核）**：建立 **Log Sink** 將 Log 匯出至 **BigQuery**（進行 SQL 分析）或 **Cloud Storage**（長期合規保存）。

### 3.2 Impact on System Design (對系統設計的影響)

*   **Performance (效能)**:
    *   Logging is blocking I/O in many languages. Use asynchronous logging libraries.
    *   Tracing adds overhead. Use **Sampling** (e.g., trace only 1% of requests) to manage performance and cost.
    *   **效能**：
    *   在許多語言中，Logging 是阻塞式 I/O。請使用非同步 Logging 函式庫。
    *   Tracing 會增加負擔。使用 **採樣（Sampling）**（例如：僅追蹤 1% 的請求）來管理效能與成本。

*   **Reliability (可靠性)**:
    *   If your monitoring system goes down, you are flying blind. GCP's Cloud Ops is a managed service, offering high availability out of the box, distinct from your own infrastructure.
    *   **可靠性**：
    *   如果監控系統當機，你就像在盲飛。GCP 的 Cloud Ops 是託管服務，提供開箱即用的高可用性，且與你自身的基礎設施隔離。

---

## 4. 逐步示例 (Walkthrough / Example)

### Scenario: Debugging "Occasional Slowness" in a Checkout API
### 情境：除錯結帳 API 的「偶發性緩慢」

**Background:** Users report that the checkout button sometimes spins for 10 seconds. CPU utilization looks normal.
**背景：** 使用者回報結帳按鈕有時會轉圈轉 10 秒鐘。CPU 使用率看起來很正常。

#### Step 1: Correlating Logs and Traces (關聯 Log 與 Trace)

To debug effectively, we need to link the Log entry to the Trace span. This requires injecting the `logging.googleapis.com/trace` field into your structured logs.
為了有效除錯，我們需要將 Log 條目連結到 Trace span。這需要將 `logging.googleapis.com/trace` 欄位注入到你的結構化 Log 中。

**Python Example (using `google-cloud-logging`):**

```python
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

# Setup Cloud Logging
client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logger = logging.getLogger('checkout_service')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def process_checkout(request):
    # Retrieve Trace ID from the incoming HTTP header (X-Cloud-Trace-Context)
    # Format: "TRACE_ID/SPAN_ID;o=TRACE_TRUE"
    trace_header = request.headers.get('X-Cloud-Trace-Context')
    trace_id = trace_header.split('/')[0] if trace_header else None
    
    # Construct the full trace path required by GCP
    # Format: projects/[PROJECT_ID]/traces/[TRACE_ID]
    gcp_trace_path = f"projects/{client.project}/traces/{trace_id}" if trace_id else None

    # Log with the trace field
    logger.info("Starting checkout process", extra={
        "json_fields": {
            "cart_size": 5,
            "user_tier": "gold"
        },
        # This is the magic key that links Logs to Trace
        "logging.googleapis.com/trace": gcp_trace_path
    })
    
    # ... business logic ...
```

#### Step 2: Analyzing in Cloud Console (在 Cloud Console 中分析)

1.  **Trace List**: Go to **Trace > Trace list**. Filter by latency > 5s.
    **Trace 列表**：前往 **Trace > Trace list**。篩選延遲 > 5秒。
2.  **Waterfall View**: Click on a slow trace. You see a waterfall chart.
    *   *Observation:* The `checkout-service` calls `inventory-service` (fast), then calls `payment-gateway`.
    *   *Finding:* The `payment-gateway` span takes 9.8s.
    **瀑布視圖**：點擊一個緩慢的 Trace。你會看到瀑布圖。
    *   *觀察：* `checkout-service` 呼叫 `inventory-service`（很快），然後呼叫 `payment-gateway`。
    *   *發現：* `payment-gateway` 的 span 花了 9.8 秒。
3.  **Logs Integration**: In the Trace details panel, click "Show Logs".
    *   Because we injected the trace ID (Step 1), specific logs for *this exact request* appear.
    *   *Log Message:* "Timeout waiting for 3rd party provider X".
    **Logs 整合**：在 Trace 詳細面板中，點擊「Show Logs」。
    *   因為我們注入了 Trace ID（步驟 1），針對 *該特定請求* 的 Log 會出現。
    *   *Log 訊息：* 「等待第三方供應商 X 時逾時」。

#### Step 3: Defining an SLO (定義 SLO)

Instead of alerting every time a single request is slow, we define an SLO.
我們不針對單一請求緩慢發出警報，而是定義 SLO。

*   **SLI**: Latency of `POST /checkout`. Valid if response code is 2xx.
*   **SLO**: 99.0% of requests < 2000ms (rolling 28 days).
*   **Alert**: Trigger if the **Burn Rate** is fast (e.g., we are consuming the error budget at a rate that will exhaust it in 2 hours).

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 High Cardinality Metrics (高基數指標)

*   **Anti-pattern**: Adding dynamic values (like `user_id`, `email`, or `uuid`) as **Labels** in Cloud Monitoring metrics.
    **反模式**：將動態數值（如 `user_id`、`email` 或 `uuid`）作為 **Labels** 加入 Cloud Monitoring 指標中。
*   **Why it's bad**: A metric is a time-series. If you have 1 million users, you create 1 million time-series. This explodes costs and slows down query performance significantly.
    **為何不好**：指標是時間序列。如果你有 100 萬個使用者，你就建立了 100 萬條時間序列。這會導致成本爆炸並嚴重拖慢查詢效能。
*   **Solution**: Use Logs for high-cardinality data. Use Metrics for aggregates (e.g., `status_code`, `region`).
    **解決方案**：高基數資料請使用 Logs。指標僅用於聚合資料（如 `status_code`、`region`）。

### 5.2 "Log Everything" without Sampling (無採樣的「記錄所有」)

*   **Anti-pattern**: Logging every entry and exit of every function in Production at `INFO` level.
    **反模式**：在 Production 環境以 `INFO` 層級記錄每個函式的進入與退出。
*   **Why it's bad**: Cloud Logging costs are based on ingestion volume ($/GiB). This creates noise and high bills.
    **為何不好**：Cloud Logging 的費用是基於寫入量（$/GiB）。這會製造雜訊並產生高額帳單。
*   **Solution**:
    1.  Use `DEBUG` level for verbose logs and set the production filter to `INFO` or `WARN`.
    2.  Use **Log Exclusion** rules to drop low-value logs at the ingestion API (saving cost).
    **解決方案**：
    1.  詳細 Log 使用 `DEBUG` 層級，並將 Production 過濾器設為 `INFO` 或 `WARN`。
    2.  使用 **Log Exclusion** 規則在寫入 API 端丟棄低價值 Log（節省成本）。

### 5.3 Alerting on Symptoms, Not Causes (針對症狀而非原因警報)

*   **Anti-pattern**: Alerting on "CPU > 80%".
    **反模式**：針對「CPU > 80%」發出警報。
*   **Why it's bad**: A batch job might legitimately use 100% CPU without impacting users. This causes "Pager Fatigue".
    **為何不好**：批次作業可能合理地使用 100% CPU 且不影響使用者。這會導致「呼叫器疲勞（Pager Fatigue）」。
*   **Solution**: Alert on **User Impact** (High Latency, High Error Rate). Use CPU alerts only as a secondary investigation signal.
    **解決方案**：針對 **使用者影響**（高延遲、高錯誤率）發出警報。CPU 警報僅作為次要的調查訊號。

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: How would you design an observability strategy for a multi-region system to balance cost and visibility?
### Q1: 你會如何為多區域系統設計可觀測性策略，以平衡成本與可視性？

*   **Key Points**:
    *   **Aggregation**: Don't centralize *all* raw logs if not needed. Keep logs in regional buckets for compliance/debugging, aggregate metrics globally.
    *   **Sampling**: Implement Trace sampling (e.g., 1% normally, 100% for errors).
    *   **Log Sinks**: Use Log Router to send only critical logs (Audit, Error) to a central BigQuery for analytics, discard or archive debug logs.
    *   **關鍵點**：
    *   **聚合**：若非必要，不要集中 *所有* 原始 Log。將 Log 留在區域性 Bucket 以供合規/除錯，僅全域聚合指標。
    *   **採樣**：實作 Trace 採樣（例如：正常時 1%，錯誤時 100%）。
    *   **Log Sinks**：使用 Log Router 僅將關鍵 Log（稽核、錯誤）傳送至中央 BigQuery 進行分析，丟棄或封存 Debug Log。

### Q2: Explain the difference between White-box and Black-box monitoring. Which one does Cloud Monitoring Uptime Checks fall into?
### Q2: 解釋白箱與黑箱監控的差異。Cloud Monitoring Uptime Checks 屬於哪一種？

*   **Key Points**:
    *   **White-box**: Monitoring based on internals exposed by the app (Logs, Metrics, Profiling). "The app says it's slow."
    *   **Black-box**: Monitoring from the outside looking in (Pinging the endpoint). "The user sees it's down."
    *   **Uptime Checks**: This is Black-box monitoring. It verifies reachability from global locations (e.g., "Can Singapore reach my US Load Balancer?").
    *   **關鍵點**：
    *   **白箱**：基於應用程式暴露的內部資訊進行監控（Logs, Metrics, Profiling）。「應用程式說它很慢。」
    *   **黑箱**：從外部向內看進行監控（Ping 端點）。「使用者看到它掛了。」
    *   **Uptime Checks**：這是黑箱監控。它驗證從全球各地的可達性（例如：「新加坡能連到我的美國負載平衡器嗎？」）。

### Q3: We are migrating a monolithic app to microservices. How does our approach to debugging change?
### Q3: 我們正在將單體應用程式遷移至微服務。我們的除錯方法會有什麼改變？

*   **Key Points**:
    *   **Correlation ID**: In a monolith, a stack trace is enough. In microservices, you need a Trace ID propagated across network boundaries.
    *   **Centralization**: You can't `grep` logs on a server. You need centralized log aggregation (Cloud Logging).
    *   **Network Fallacies**: Latency is no longer just code execution; it includes network serialization/deserialization.
    *   **關鍵點**：
    *   **關聯 ID**：在單體中，Stack trace 就夠了。在微服務中，你需要跨越網路邊界傳遞 Trace ID。
    *   **集中化**：你不能在伺服器上 `grep` Log。你需要集中式的 Log 聚合（Cloud Logging）。
    *   **網路謬誤**：延遲不再只是程式碼執行時間；還包含網路序列化/反序列化的時間。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### Summary (小結)

1.  **Three Pillars**: Logs (Events), Metrics (Trends), Traces (Context).
2.  **Structured Logging**: Always log in JSON to enable powerful querying and correlation.
3.  **Trace Context**: The "glue" that connects Logs and Traces across microservices.
4.  **SLO/SLI**: Alert on what matters to the user (Latency/Errors), not just machine health (CPU/RAM).
5.  **Cost Management**: Use Sampling and Log Exclusions to prevent observability bills from exceeding infrastructure bills.

### Next Steps (後續延伸)

*   **Automation**: Now that you can observe the system, how do you deploy it reliably?
    *   *Next Chapter:* **Infrastructure as Code (Terraform) & CI/CD on GCP**.
*   **Advanced Tracing**: Look into **OpenTelemetry**. It is the vendor-neutral standard for generating telemetry that GCP Cloud Ops fully supports.
    *   **進階追蹤**：研究 **OpenTelemetry**。這是產生遙測資料的供應商中立標準，GCP Cloud Ops 全面支援。