# 可觀測性與 Cloud Operations 實戰 / Observability & Cloud Operations Practices

## Mental model｜心智模型

在 GCP 上構建可觀測性（Observability），不應只視為「收集 Log」或「看 CPU圖表」，而應建立以下兩個核心心智模型：

### 1. The Observability Pipeline: From Unstructured to Actionable
**從非結構化數據到可行動的訊號**

GCP 的 Cloud Operations (以前稱為 Stackdriver) 是一條資料處理流水線。你必須意識到資料的流動方向：
1.  **Raw Data**: 應用程式產出的 JSON Logs、基礎設施產生的 Metrics。
2.  **Aggregation**: 透過 **Log-based Metrics** 將雜亂的 Log 轉化為數值指標（Counter/Distribution）。
3.  **Visualization**: 將 Metrics 匯總為 **SRE Golden Signals** 儀表板。
4.  **Action**: 當指標異常時，觸發 Alerting Policy 通知人或自動化腳本。

> **Key Takeaway**: 不要只儲存 Log，要「提煉」Log。Log 是昂貴的儲存（Storage），Metric 是便宜的趨勢（Trend）。

### 2. Monitoring tells you "What", Observability tells you "Why"
**監控告訴你「什麼壞了」，可觀測性告訴你「為什麼」**

- **Monitoring (Dashboard/Alerts)**: 告訴你系統現在很慢（Latency High）。
- **Observability (Trace/Logs/Profiler)**: 允許你透過 Trace ID 鑽取（Drill-down），發現是因為某個 SQL Query 在特定參數下沒有吃到 Index。

在 GCP 中，這意味著你需要將 **Cloud Trace**、**Cloud Logging** 與 **Cloud Monitoring** 透過 `Trace ID` 和 `Span ID` 串聯起來，而不是三個獨立的工具。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Implement SRE Golden Signals
**實作 SRE 黃金訊號**

不要從 CPU 或 Memory 開始建立 Dashboard，那是給機器看的。給人（SRE/Dev）看的 Dashboard 應專注於使用者體驗：
- **Latency (延遲)**: 請求需要多久？(e.g., 95th/99th percentile latency)
- **Traffic (流量)**: 系統有多忙？(e.g., QPS, HTTP requests/sec)
- **Errors (錯誤)**: 請求失敗率？(e.g., HTTP 5xx rate)
- **Saturation (飽和度)**: 系統有多滿？(e.g., Queue depth, Quota usage)

### 2. Structured Logging is Mandatory
**強制使用結構化日誌 (JSON)**

在 GCP 中，`textPayload` 是二等公民，`jsonPayload` 才是王道。
- **Why**: Cloud Logging 的查詢效能與 Log-based Metrics 的建立完全依賴 JSON 結構。
- **How**: 應用程式 Log 輸出必須是單行 JSON。
  - *Bad*: `printf("User %s login failed", user_id)`
  - *Good*: `logger.info({event: "login_failed", user_id: "123", reason: "bad_password"})`

### 3. Leverage Log-based Metrics
**善用 Log-based Metrics 填補監控盲點**

很多業務邏輯指標（Business Metrics）無法透過標準 Agent 取得。與其在程式碼中埋點 Prometheus client，有時直接分析 Log 更快且解耦。
- **Counter Metric**: 統計特定錯誤發生的次數（例如：付款失敗次數）。
- **Distribution Metric**: 從 Log 數值中提取分佈（例如：從 Log 中的 `processing_time_ms` 欄位建立直方圖）。

### 4. Use Error Reporting for Noise Reduction
**使用 Error Reporting 降噪**

不要手動去 Log 裡撈 Exception。GCP **Error Reporting** 會自動將相同的 Stack Trace 聚合（Group）在一起。
- **Pattern**: 確保你的 App 發生 Crash 或 Exception 時，輸出的 Log 格式符合 GCP 規範（包含 `serviceContext` 和 `stack_trace`），這樣 Error Reporting 就能自動捕捉並通知。

### 5. Cost Control with Exclusion Filters
**使用排除過濾器控制成本**

Cloud Logging 非常昂貴。
- **Pattern**: 在 Log Router (Sink) 設定 **Exclusion Filters**。
- **Target**: 排除 `200 OK` 的健康檢查（Health Check）Log、開發環境的 Debug Log，或 VPC Flow Logs 的取樣數據。只保留「有分析價值」的 Log。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. High Cardinality Labels in Metrics
**在指標中使用高基數標籤**

- **Anti-pattern**: 在 Metric Label 中放入 `User ID`、`Email` 或 `UUID`。
- **Consequence**: 這會導致 Metric Series 爆炸，查詢變慢，甚至產生巨額帳單（Custom Metrics 依 Series 數量計費）。
- **Fix**: Label 只能是有限集合（如 `region`, `status_code`, `instance_type`）。詳細資訊請留在 Logs 或 Trace 中。

### 2. Alerting on "Causes" instead of "Symptoms"
**針對「原因」而非「症狀」設定告警**

- **Anti-pattern**: 設定 "CPU > 80%" 的 PagerDuty 告警。
- **Pitfall**: CPU 高不代表服務壞了（可能是背景任務）。半夜把工程師叫起來看 CPU 高，但他發現服務運作正常，這是 **Alert Fatigue**（告警疲勞）的元兇。
- **Fix**: 告警應設在 SLO 違規上（如：Error Rate > 1% 或 Latency p99 > 500ms）。CPU 高只需記錄 Ticket 供上班時間調查。

### 3. Ignoring "_Default" Sink Costs
**忽略預設 Log Sink 的成本**

- **Pitfall**: 預設情況下，GCP 會保留大量系統 Log。如果不管理 `_Default` sink，可能會為你根本不看的 Log 付費。
- **Fix**: 檢視 Log Volume，針對不需要的 Log 類別進行 Exclude。

### 4. "Log and Ignore"
**記錄後即遺忘**

- **Anti-pattern**: 寫了大量的 Log，但沒有關聯 Trace ID，也沒有設定 Log-based Metrics。
- **Consequence**: 當發生問題時，你擁有一片 Log 海洋，卻找不到那根針。

---

## Checklists & workflows｜檢查清單與流程

### Dashboard & Alerting Readiness Checklist
- [ ] **Golden Signals**: 是否已為關鍵服務建立了包含 Latency, Traffic, Errors, Saturation 的儀表板？
- [ ] **Structured Logging**: 應用程式是否輸出 JSON 格式的 Log？關鍵欄位（如 `order_id`, `user_id`）是否在 `jsonPayload` 的頂層？
- [ ] **Trace Context**: Log 中是否自動注入了 `logging.googleapis.com/trace` 欄位以關聯 Cloud Trace？
- [ ] **Alerting Policy**:
    - [ ] 是否區分了 P1 (Page/SMS) 與 P2 (Email/Ticket) 等級？
    - [ ] P1 告警是否基於使用者影響（Symptoms）而非基礎設施雜訊（Causes）？
- [ ] **Cost Management**:
    - [ ] 是否已設定 Log Router 的 Exclusion Filters 以排除無用 Log？
    - [ ] 是否檢查過 Custom Metrics 的 Cardinality？

### Troubleshooting Workflow (The "Drill-down" Path)
當收到 Latency 告警時的標準排查流程：
1.  **Alert**: 收到 Slack/PagerDuty 通知（e.g., "Checkout Latency p99 > 2s"）。
2.  **Dashboard**: 查看 Cloud Monitoring Dashboard，確認是整體變慢還是單一 Zone/Instance 變慢。
3.  **Trace**: 點擊慢速請求的 Trace Sample，查看 Waterfall 圖表。是 DB 慢？還是外部 API 慢？
4.  **Logs**: 透過 Trace ID 跳轉至 Cloud Logging，查看該請求相關的所有 Log entries（包含 Payload 細節）。
5.  **Fix**: 根據 Log 中的錯誤訊息或 Trace 中的瓶頸進行修復。

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Checkout Failure Analysis
**情境：電商結帳失敗率飆升**

#### 1. Log Structure (Application Side)
應用程式輸出標準化的 JSON Log，便於 GCP 解析：

```json
// GOOD: Structured JSON Log
{
  "severity": "ERROR",
  "message": "Payment gateway rejected transaction",
  "serviceContext": {
    "service": "checkout-service",
    "version": "v1.2.3"
  },
  "logging.googleapis.com/trace": "projects/my-project/traces/a1b2c3d4...",
  "jsonPayload": {
    "event_type": "payment_failure",
    "cart_id": "cart-888",
    "amount": 150.00,
    "gateway_response_time_ms": 3500,
    "error_code": "GATEWAY_TIMEOUT"
  }
}
```

#### 2. Log-based Metric Definition
為了監控這種錯誤，我們在 Cloud Logging 建立一個 Metric：
- **Type**: Counter
- **Name**: `checkout_payment_errors`
- **Filter**:
  ```text
  resource.type="k8s_container"
  jsonPayload.event_type="payment_failure"
  severity>=ERROR
  ```
- **Labels (Optional)**: Extract `jsonPayload.error_code` as a label (注意基數!).

#### 3. Alerting Policy (MQL)
使用 Monitoring Query Language (MQL) 設定告警，當錯誤率超過 5% 時通知：

```text
fetch k8s_container
| metric 'logging.googleapis.com/user/checkout_payment_errors'
| align rate(1m)
| group_by [resource.cluster_name], sliding(5m), sum(val())
| condition val() > 0.05 '1/s'
```

#### 4. Outcome
當外部金流閘道不穩時：
1.  Log 捕捉到 `GATEWAY_TIMEOUT`。
2.  Metric 計數器飆升。
3.  SRE 收到告警，打開 Dashboard 看到 `checkout-service` 的 Error Rate 上升。
4.  點擊 Trace 發現是呼叫第三方 API 超時，立即切換備用金流管道。