# 可觀測性與維運卓越 / Observability & Operational Excellence

## Mental model｜心智模型

### 1. 監控 vs. 可觀測性 (Monitoring vs. Observability)
不要將兩者混為一談。
- **監控 (Monitoring)** 是告訴你「系統是否健康」的儀表板（例如：CPU 使用率 90%、網站回應 200 OK）。它是**黑箱 (Black-box)** 的視角，回答 "Is it broken?"。
- **可觀測性 (Observability)** 是讓你有能力透過外部輸出來推斷系統內部狀態。它是**白箱 (White-box)** 的視角，回答 "Why is it broken?"。
- 在 AWS 中，你的目標是建立一個「能夠回答未預期問題」的系統，而不僅僅是看著預定義的儀表板亮紅燈。

### 2. 資料流的三支柱 (The Three Pillars Data Flow)
在 AWS 生態系中，建立可觀測性的心智模型應如下流動：
1.  **Metrics (CloudWatch Metrics)**: 觸發警報的訊號 (The "What")。例如：`5xxErrorRate > 5%`。
2.  **Traces (AWS X-Ray / ServiceLens)**: 定位問題發生的元件與依賴關係 (The "Where")。例如：延遲發生在 DynamoDB 寫入操作。
3.  **Logs (CloudWatch Logs)**: 挖掘根本原因的詳細資訊 (The "Why")。例如：`Exception: ConditionalCheckFailedException`。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 結構化日誌與關聯 ID (Structured Logging & Correlation IDs)
不要再輸出純文字日誌 (Plain text logs)。
- **Pattern**: 強制所有應用程式輸出 **JSON 格式** 的日誌。這讓 CloudWatch Logs Insights 可以直接 parse 欄位進行查詢。
- **Pattern**: 在請求進入系統邊界（如 ALB 或 API Gateway）時生成一個 `Trace ID` (或使用 AWS 預設的 `X-Amzn-Trace-Id`)，並將其注入到所有下游服務 (Lambda, ECS) 的日誌 context 中。
- **Benefit**: 你可以透過單一 ID 串聯跨服務的所有 Log entries。

### 2. 使用 EMF 節省成本並提升效能 (Embedded Metric Format)
避免在程式碼中頻繁呼叫 `PutMetricData` API，這會導致高延遲與高昂的 API 費用。
- **Best Practice**: 使用 **CloudWatch Embedded Metric Format (EMF)**。
- **How it works**: 你只需將 Metrics 作為 JSON log 的一部分寫入 `stdout`，CloudWatch 會在背景自動將其提取為 CloudWatch Metrics。
- **Benefit**: 非同步、無額外 API 呼叫成本、同時擁有 Log 與 Metric。

### 3. 黃金訊號儀表板 (Golden Signals Dashboard)
不要把所有 metrics 丟到一個 Dashboard。依照 Google SRE 書籍建議，針對每個關鍵服務建立包含以下四個維度的 Dashboard：
- **Latency**: 請求花多久時間？(關注 p50, p90, p99)。
- **Traffic**: 系統承受多少負載？(RPS, Throughput)。
- **Errors**: 請求失敗率？(HTTP 5xx, 4xx, Application Exceptions)。
- **Saturation**: 資源有多滿？(CPU, Memory, Connection Pool, DynamoDB RCU/WCU)。

### 4. 告警分級策略 (Tiered Alerting Strategy)
- **P1 (Critical)**: 影響使用者體驗或營收，需要立即介入 (Page on-call)。例如：Checkout API 失敗率 > 10%。
- **P2 (Warning)**: 系統異常但尚未影響使用者，需在上班時間處理 (Ticket)。例如：Disk Space > 80%。
- **P3 (Info)**: 僅供紀錄與分析，不發送通知。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 預設日誌保留期陷阱 (The "Never Expire" Trap)
- **Bad Practice**: 建立 CloudWatch Log Group 時使用預設的 "Never Expire"。
- **Consequence**: 儲存成本會隨時間指數成長，且大部分 3 個月前的 debug logs 毫無價值。
- **Fix**: 透過 IaC (Terraform/CDK) 強制設定 Log Retention (例如 Dev 7天, Prod 30-90天)，並將長期合規日誌匯出至 S3 Glacier。

### 2. 告警疲勞 (Alert Fatigue)
- **Bad Practice**: 設定過於敏感的閾值 (Threshold)，導致手機整天響個不停，最後工程師選擇忽略所有通知。
- **Consequence**: 當真正的 P1 事故發生時，沒人反應。
- **Fix**: 告警應針對「症狀 (Symptoms)」而非「原因 (Causes)」。告警「網站回應過慢」，而不是「CPU > 80%」（如果 CPU 高但回應快，其實沒問題）。

### 3. 忽略 X-Ray 採樣率 (Ignoring Sampling Rules)
- **Bad Practice**: 在高流量生產環境開啟 100% 的 X-Ray Tracing。
- **Consequence**: 產生巨大的 X-Ray 費用，且對效能有輕微影響。
- **Fix**: 設定合理的 Sampling Rules (例如：每秒保留 1 個請求，超過的部分保留 5%)。

### 4. 高基數維度災難 (High Cardinality Cardinality)
- **Bad Practice**: 在 Custom Metrics 中使用 User ID 或 Request ID 作為 Dimension。
- **Consequence**: CloudWatch Metrics 是依據「Metric Name + Dimensions 組合」計費。這會產生數百萬個 unique metrics，導致帳單爆炸。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Operational Checklist
- [ ] **Log Retention**: 確認所有新建的 Log Group 都有設定過期時間 (Retention Policy)。
- [ ] **Structured Logs**: 確認應用程式日誌是 JSON 格式，且包含 `service_name`, `environment`, `trace_id`, `log_level`。
- [ ] **Alarm Action**: 確認所有 Critical Alarms 都有對應的 Action (SNS -> PagerDuty/Slack)，而不僅僅是變紅燈。
- [ ] **Dead Letter Queues (DLQ)**: 檢查 SQS/Lambda 的 DLQ 是否有堆積訊息，並設定對應的 Alarm。

### Incident Response Workflow (事故回應流程)
1.  **Detect (偵測)**: CloudWatch Alarm 觸發，通知發送到 Slack/PagerDuty。
2.  **Triage (分流)**:
    - 查看 **CloudWatch ServiceLens Map** 確認是哪個服務節點變紅。
    - 檢查 **Golden Signals Dashboard** 確認是 Latency 飆高還是 Error 飆高。
3.  **Investigate (調查)**:
    - 點擊 ServiceLens 中的節點，跳轉至 **X-Ray Traces** 查看個別請求的 Waterfall 圖。
    - 複製 Trace ID，使用 **CloudWatch Logs Insights** 查詢該 ID 的所有相關日誌。
4.  **Mitigate (緩解)**: 執行 Rollback、擴容 (Scale out) 或啟用 Feature Flag 關閉功能。
5.  **Post-mortem (事後檢討)**: 撰寫 COE (Correction of Error) 報告，調整 Alarm 閾值以防止誤報或漏報。

---

## Real-world examples｜實戰案例

### 案例：使用 CloudWatch Logs Insights 快速排查 API 500 錯誤

情境：你的 API Gateway + Lambda 架構突然出現大量 500 錯誤。你需要在一分鐘內找出是哪個 Exception 導致的。

**傳統做法**：在 CloudWatch Logs 介面一頁一頁翻閱，肉眼尋找 "Error"。

**實戰做法 (Logs Insights)**：
使用以下查詢語法，直接統計最常發生的錯誤訊息：

```sql
# CloudWatch Logs Insights Query
fields @timestamp, @message, @logStream
| filter @message like /Error/ or level = "ERROR"
| stats count(*) as exceptionCount by @message
| sort exceptionCount desc
| limit 20
```

### 案例：使用 EMF 實作商業邏輯監控

情境：你需要監控「購物車結帳失敗」的次數，但不希望因為呼叫 `PutMetricData` 增加 API 延遲。

**Node.js 實作範例 (使用 `aws-embedded-metrics` 函式庫)**：

```javascript
const { metricScope, Unit } = require("aws-embedded-metrics");

const checkoutHandler = metricScope(metrics => async (event) => {
    metrics.setNamespace("ECommercePlatform");
    metrics.putDimensions({ Service: "CheckoutService" });

    try {
        await processOrder(event);
        metrics.putMetric("SuccessfulCheckout", 1, Unit.Count);
        // 這是 Log 也是 Metric，不會發起額外 HTTP Request
    } catch (error) {
        metrics.putMetric("FailedCheckout", 1, Unit.Count);
        metrics.setProperty("ErrorMessage", error.message);
        metrics.setProperty("CartId", event.cartId); // 加入 Context 方便 debug
        throw error;
    }
});
```

### 案例：Dashboard 設計層次 (The Layered Approach)

不要試圖在一個 Dashboard 解決所有人的問題。建立三層視圖：

1.  **Business View (給老闆/PM看)**:
    - Order Rate (每分鐘訂單數)
    - Revenue (預估營收)
    - Active Users
2.  **Service View (給 SRE/Tech Lead 看)**:
    - API Gateway 4xx/5xx Rate
    - Lambda Duration (p99)
    - DynamoDB Throttled Events
3.  **Instance/Debug View (給開發者 Debug 用)**:
    - 個別 Container 的 CPU/Memory
    - JVM Heap Usage
    - Detailed Error Logs stream