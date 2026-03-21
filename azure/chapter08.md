# 1. 前言與學習目標 (Introduction & Learning Objectives)

在分散式系統與微服務架構中，「系統是否活著 (Up)」只是監控的最低標準；資深工程師更關注的是「系統為何變慢」以及「故障的根因 (Root Cause) 是什麼」。Azure Monitor 與 Application Insights 提供了強大的可觀測性 (Observability) 平台，但許多團隊僅將其作為簡單的 Log 收集器，未能發揮其全貌。

In distributed systems and microservices architectures, knowing "if the system is up" is merely the baseline for monitoring. Senior engineers are more concerned with "why the system is slow" and "what is the root cause of the failure." Azure Monitor and Application Insights provide a powerful observability platform, yet many teams underutilize them, treating them merely as simple log collectors.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作分散式追蹤 (Distributed Tracing)**：理解並配置 Application Insights 以串聯跨服務 (Cross-service) 的請求路徑，解決「微服務迷宮」中的除錯難題。
    **Implement Distributed Tracing**: Understand and configure Application Insights to correlate cross-service request paths, solving debugging challenges in the "microservices maze."
2.  **精通 Log Analytics (KQL)**：撰寫進階 Kusto Query Language (KQL) 查詢，從海量數據中快速定位 P99 延遲異常與依賴服務 (Dependency) 故障。
    **Master Log Analytics (KQL)**: Write advanced Kusto Query Language (KQL) queries to rapidly pinpoint P99 latency anomalies and dependency failures from massive datasets.
3.  **優化成本與採樣策略 (Cost & Sampling)**：設計合理的採樣 (Sampling) 與資料保留策略，在不丟失關鍵除錯資訊的前提下控制監控成本。
    **Optimize Cost & Sampling Strategies**: Design reasonable sampling and data retention strategies to control monitoring costs without losing critical debugging information.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 監控 vs. 可觀測性 (Monitoring vs. Observability)

**監控 (Monitoring)** 告訴你系統的狀態（例如：「CPU 使用率 90%」或「HTTP 500 錯誤率上升」）。這通常是預定義的儀表板。
**Monitoring** tells you the state of the system (e.g., "CPU usage is at 90%" or "HTTP 500 error rate is rising"). This is usually represented by predefined dashboards.

**可觀測性 (Observability)** 則是一種屬性，讓你能夠透過檢視系統的輸出來推斷其內部狀態。它允許你詢問未曾預想過的問題（例如：「為什麼特定 Tenant ID 的用戶在呼叫 SQL Database 時延遲特別高？」）。
**Observability** is a property that allows you to infer the internal state of a system by examining its outputs. It enables you to ask questions you hadn't anticipated (e.g., "Why do users with a specific Tenant ID experience high latency when calling the SQL Database?").

## 2.2 Azure Monitor 生態系 (The Azure Monitor Ecosystem)

將 Azure Monitor 想像成一個大型的資料湖與分析引擎，主要包含兩個核心儲存：
Think of Azure Monitor as a large data lake and analytics engine, primarily consisting of two core stores:

1.  **Metrics Store**: 儲存時間序列數據 (Time-series data)，輕量、即時，適合用於 Alerting (警報)。
    **Metrics Store**: Stores time-series data; lightweight and real-time, ideal for Alerting.
2.  **Logs Store (Log Analytics Workspace)**: 儲存結構化與非結構化的 Log 記錄，查詢能力強大但延遲稍高，適合 Deep Dive 分析。
    **Logs Store (Log Analytics Workspace)**: Stores structured and unstructured log records; powerful querying capabilities but slightly higher latency, ideal for Deep Dive analysis.

**Application Insights** 則是建構在 Azure Monitor 之上的 APM (Application Performance Management) 服務。它透過 SDK 收集遙測數據 (Telemetry)，並將其寫入 Log Analytics Workspace。
**Application Insights** is an APM (Application Performance Management) service built on top of Azure Monitor. It collects telemetry via SDKs and writes it into a Log Analytics Workspace.

## 2.3 分散式追蹤模型 (Distributed Tracing Model)

在 Azure 中，這遵循 W3C Trace Context 標準：
In Azure, this follows the W3C Trace Context standard:

*   **Trace ID**: 代表整個端對端交易 (End-to-end transaction) 的唯一識別碼。
    **Trace ID**: A unique identifier representing the entire end-to-end transaction.
*   **Span ID (Parent ID)**: 代表單一操作 (如一次 HTTP 請求或一次 SQL 查詢) 的識別碼。
    **Span ID (Parent ID)**: An identifier for a single operation (e.g., an HTTP request or a SQL query).

當 Service A 呼叫 Service B 時，App Insights SDK 會自動將 `traceparent` header 注入 HTTP request 中，確保兩邊的 Log 擁有相同的 `Trace ID`。
When Service A calls Service B, the App Insights SDK automatically injects the `traceparent` header into the HTTP request, ensuring logs on both sides share the same `Trace ID`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 微服務架構中的角色 (Role in Microservices Architecture)

在典型的 System Design 面試或實務架構中，我們會有如下流程：
In a typical System Design interview or real-world architecture, we have the following flow:

`Client App` -> `API Gateway` -> `Order Service` -> `Inventory Service` -> `SQL Database`

若沒有分散式追蹤，當 Client 收到 500 Error 時，你必須分別登入 Gateway、Order Service 和 Inventory Service 的機器去撈 Log，且難以將它們關聯起來。
Without distributed tracing, when a Client receives a 500 Error, you have to manually log into the Gateway, Order Service, and Inventory Service machines to dig through logs, and correlating them is extremely difficult.

**Azure 的解決方案 (The Azure Solution):**
所有服務都將 Telemetry 送往同一個 (或透過 Azure Lighthouse 連結的) **Log Analytics Workspace**。透過 `operation_Id` (即 Trace ID)，我們可以繪製出完整的 **Application Map**，視覺化顯示服務間的依賴關係與延遲。
All services send Telemetry to the same (or Azure Lighthouse-linked) **Log Analytics Workspace**. Using the `operation_Id` (Trace ID), we can render a complete **Application Map**, visualizing dependencies and latency between services.

## 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **可維護性 (Maintainability)**: 透過 Log Analytics，開發者不需要 SSH 進入機器即可除錯。
    **Maintainability**: With Log Analytics, developers don't need to SSH into machines to debug.
*   **效能 (Performance)**: App Insights SDK 預設會進行**採樣 (Sampling)**。若設定不當（如 100% 採樣且流量巨大），SDK 的序列化與傳輸開銷可能會影響 Application 的 Throughput。
    **Performance**: The App Insights SDK performs **Sampling** by default. If misconfigured (e.g., 100% sampling with high traffic), the serialization and transmission overhead of the SDK can impact the application's throughput.
*   **成本 (Cost)**: Log Analytics 是按**寫入量 (Ingestion Volume)** 與**保留時間 (Retention)** 收費。過多的 `Information` 級別 Log 會導致帳單爆炸。
    **Cost**: Log Analytics bills based on **Ingestion Volume** and **Retention**. Excessive `Information` level logs can lead to billing explosions.

---

# 4. 逐步示例：診斷 API 效能瓶頸 (Walkthrough: Diagnosing API Performance Bottlenecks)

## 場景 (Scenario)

你負責維護一個電子商務的 `Checkout API`。最近收到警報，P99 延遲從 500ms 飆升至 3秒，但 CPU 與記憶體使用率正常。
You maintain an e-commerce `Checkout API`. Recently, you received an alert that P99 latency spiked from 500ms to 3 seconds, but CPU and memory usage are normal.

## 步驟 1: 使用 Application Map 初步定位 (Initial Triage with Application Map)

進入 Azure Portal -> Application Insights -> **Application Map**。
Navigate to Azure Portal -> Application Insights -> **Application Map**.

*   **觀察**: 你看到 `Checkout Service` 到 `Payment Gateway` (外部依賴) 的連線變紅，平均呼叫時間顯示為 2.5s。
*   **Observation**: You see the line from `Checkout Service` to `Payment Gateway` (external dependency) has turned red, showing an average call time of 2.5s.
*   **結論**: 問題很可能不在我們的程式碼邏輯，而在於外部依賴。
*   **Conclusion**: The issue is likely not in our code logic, but in the external dependency.

## 步驟 2: 使用 KQL 深入分析 (Deep Dive with KQL)

我們需要證實這是否只發生在特定客戶或特定時段。打開 **Logs** 面板。
We need to verify if this only happens to specific customers or during specific times. Open the **Logs** blade.

### 查詢 1: 找出最慢的依賴呼叫 (Find the slowest dependency calls)

```kusto
dependencies
| where type == "HTTP" // 或者是 "SQL", "Azure Service Bus" 等
| where target contains "payment-api.com"
| where timestamp > ago(1h)
| summarize P95_Duration = percentile(duration, 95), 
            Avg_Duration = avg(duration), 
            Count = count() by operation_Name
| order by P95_Duration desc
```

### 查詢 2: 關聯 Request 與 Dependency (Correlate Request with Dependency)

找出那些因為 Payment API 慢而導致整體 Request 超時的案例。
Identify cases where the overall Request timed out specifically because the Payment API was slow.

```kusto
let slow_dependencies = dependencies
| where timestamp > ago(1h)
| where duration > 2000 // 超過 2 秒的依賴
| project operation_Id, dep_duration = duration, target;

requests
| where timestamp > ago(1h)
| where success == false or duration > 2000
| project timestamp, operation_Id, req_duration = duration, name, resultCode
| join kind=inner (slow_dependencies) on operation_Id
| project timestamp, name, resultCode, req_duration, dep_duration, target
| order by timestamp desc
| take 20
```

**分析 (Analysis)**:
這個查詢使用了 `join` 操作，透過 `operation_Id` 將 `requests` (進入 API 的流量) 與 `dependencies` (API 發出的呼叫) 連結起來。這證實了 API 的緩慢直接由 `payment-api.com` 的高延遲引起。
This query uses a `join` operation to link `requests` (incoming traffic) with `dependencies` (outgoing calls) via `operation_Id`. This confirms that the API slowness is directly caused by high latency from `payment-api.com`.

## 步驟 3: 加入 Custom Dimensions 進行業務分析 (Adding Custom Dimensions for Business Context)

為了知道哪些 VIP 客戶受影響，我們在程式碼中加入 Context。
To know which VIP customers are affected, we add context in the code.

```csharp
// C# Example using TelemetryClient
var telemetry = new RequestTelemetry();
telemetry.Name = "Checkout";
// 關鍵：加入高基數 (High Cardinality) 的業務資料
telemetry.Properties["TenantId"] = currentTenantId; 
telemetry.Properties["UserTier"] = currentUserTier; // e.g., "Gold", "Silver"

_telemetryClient.TrackRequest(telemetry);
```

**KQL 更新 (KQL Update)**:

```kusto
requests
| where timestamp > ago(1h)
| where duration > 2000
// 展開 customDimensions
| extend TenantId = tostring(customDimensions["TenantId"])
| extend UserTier = tostring(customDimensions["UserTier"])
| summarize Slow_Count = count() by UserTier
| render piechart
```

這能讓你直接回答老闆：「80% 的效能問題影響的是 Gold Tier 用戶」。
This allows you to directly answer your boss: "80% of the performance issues are affecting Gold Tier users."

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Log 導致成本失控 (Logging Everything leading to Cost Explosion)

*   **錯誤 (Mistake)**: 開發者在 `Information` 層級記錄所有 Request 的 Payload (Body)。
    **Mistake**: Developers log the full payload (body) of every request at the `Information` level.
*   **後果 (Consequence)**: Log Analytics 費用暴增，且包含 PII (個人識別資訊) 風險。
    **Consequence**: Log Analytics costs skyrocket, and there is a risk of exposing PII (Personally Identifiable Information).
*   **最佳實踐 (Best Practice)**:
    1.  使用 **Sampling (採樣)**：例如使用 `AdaptiveSampling`，在流量低時保留 100%，流量高時自動降至 5%。
    2.  僅在 `Warning` 或 `Error` 層級記錄詳細資訊。
    3.  使用 **Log-Based Metrics** 來統計次數，而不是依賴原始 Log 進行 `count()`。
    **Best Practice**:
    1.  Use **Sampling**: E.g., `AdaptiveSampling`, which keeps 100% at low traffic but drops to 5% at high traffic.
    2.  Log details only at `Warning` or `Error` levels.
    3.  Use **Log-Based Metrics** for counting, rather than relying on raw logs for `count()`.

## 5.2 自訂維度基數過高 (High Cardinality in Custom Dimensions)

*   **錯誤 (Mistake)**: 將 `TraceId` 或 `UniqueTimestamp` 作為 Metric 的 Dimension。
    **Mistake**: Using `TraceId` or `UniqueTimestamp` as a Dimension for a Metric.
*   **後果 (Consequence)**: Metrics 系統是為聚合設計的，過高的基數 (Cardinality) 會導致 Metrics 系統崩潰或被 Azure 限流 (Throttling)。
    **Consequence**: Metrics systems are designed for aggregation. Excessively high cardinality will cause the metrics system to crash or be throttled by Azure.
*   **修正 (Correction)**: 高基數資料 (如 UserID, OrderID) 應放在 **Logs** (Properties) 中，而非 Metrics 中。Metrics 的 Dimension 應該是有限集合 (如 Region, UserTier, ErrorCode)。
    **Correction**: High cardinality data (like UserID, OrderID) should be placed in **Logs** (Properties), not Metrics. Metric Dimensions should be finite sets (like Region, UserTier, ErrorCode).

## 5.3 警報疲勞 (Alert Fatigue)

*   **錯誤 (Mistake)**: 設定 "CPU > 80%" 就發送 Email。
    **Mistake**: Setting an alert to send an Email whenever "CPU > 80%".
*   **後果 (Consequence)**: 團隊忽略警報，因為 CPU 飆高不代表服務掛掉 (可能是背景任務)。
    **Consequence**: The team ignores alerts because high CPU doesn't necessarily mean the service is down (it could be a background task).
*   **最佳實踐 (Best Practice)**: 針對 **Golden Signals** 設定警報：延遲 (Latency)、錯誤率 (Error Rate)、流量 (Traffic)、飽和度 (Saturation)。只有當使用者體驗受損時才叫醒工程師。
    **Best Practice**: Alert on **Golden Signals**: Latency, Error Rate, Traffic, and Saturation. Only wake up engineers when user experience is degraded.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在分散式系統中追蹤一個請求的完整生命週期？
**How do you trace the full lifecycle of a request in a distributed system?**

*   **Key Points**:
    *   提及 **Correlation ID** 的概念 (Trace ID / Span ID)。
    *   提及 **W3C Trace Context** 標準 (Azure 預設支援)。
    *   說明如何在 Log Analytics 中使用 `join` 查詢跨服務的 Logs。
    *   解釋 **Application Map** 如何自動生成依賴圖。

## Q2: 我們的 Log 費用太高了，你會如何優化？
**Our logging costs are too high. How would you optimize them?**

*   **Key Points**:
    *   **Sampling (採樣)**: 固定採樣 vs. 自適應採樣 (Adaptive Sampling)。
    *   **Filtering (過濾)**: 在 SDK 端過濾掉不必要的 Log (如 Health Check endpoints)。
    *   **Data Retention (資料保留)**: 調整 Log Analytics 的保留天數 (預設 30-90 天)，將舊資料匯出至 Azure Storage (Archive Tier) 以降低成本。
    *   **Log Levels**: 確保 Production 環境不開啟 Debug 級別。

## Q3: 系統變慢了，但沒有報錯，你會如何排查？
**The system is slow, but there are no errors. How do you investigate?**

*   **Key Points**:
    *   檢查 **Dependencies** 的 Duration (通常是 DB 或外部 API 變慢)。
    *   使用 KQL 查詢 P95 或 P99 延遲，排除平均值的誤導 (Averages lie)。
    *   檢查資源飽和度 (CPU/Memory/Thread Pool)。
    *   查看是否有最近的 Deployment (Change Analysis)。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Observability > Monitoring**: 目標是能夠回答「為什麼發生」，而不僅是「發生了什麼」。
    **Observability > Monitoring**: The goal is to answer "why it happened," not just "what happened."
2.  **KQL is a Superpower**: 熟練 KQL 是資深 Azure 工程師的必備技能，能大幅縮短 MTTR (Mean Time To Recovery)。
    **KQL is a Superpower**: Proficiency in KQL is a must-have skill for senior Azure engineers, significantly reducing MTTR.
3.  **Context is King**: 善用 `customDimensions` 豐富 Log 的業務上下文，但要注意 Cardinality。
    **Context is King**: Leverage `customDimensions` to enrich logs with business context, but be mindful of Cardinality.
4.  **Distributed Tracing**: 理解 W3C Trace Context 與 Application Map 的運作原理，是解決微服務問題的關鍵。
    **Distributed Tracing**: Understanding W3C Trace Context and how Application Map works is key to solving microservices issues.
5.  **Cost Management**: 透過採樣與分層儲存策略，平衡可觀測性與成本。
    **Cost Management**: Balance observability and cost through sampling and tiered storage strategies.

## 下一步 (Next Steps)

*   **進階 KQL**: 學習 `make-series` 進行時間序列分析與異常偵測。
    **Advanced KQL**: Learn `make-series` for time-series analysis and anomaly detection.
*   **Infrastructure as Code (IaC)**: 學習如何使用 Bicep 或 Terraform 自動化部署 Log Analytics Workspace 與 Alert Rules (下一章可能涉及的主題)。
    **Infrastructure as Code (IaC)**: Learn how to automate the deployment of Log Analytics Workspaces and Alert Rules using Bicep or Terraform.
*   **OpenTelemetry**: 研究 Azure Monitor 如何支援 OpenTelemetry 標準，以實現更通用的供應商中立性 (Vendor Neutrality)。
    **OpenTelemetry**: Investigate how Azure Monitor supports the OpenTelemetry standard for greater vendor neutrality.