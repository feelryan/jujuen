# 可觀測性實戰指南 / Observability Practices: Logs, Metrics & Tracing

## Mental model｜心智模型

在單體架構 (Monolith) 中，故障排除通常像是在「看醫生」：你檢查單一病人的生命徵象。但在微服務架構中，故障排除更像是「刑事偵查」：你需要追蹤跨越多個嫌疑人（服務）、多個地點（節點）的複雜交互。

要建立有效的可觀測性，必須從 **"Monitoring" (監控)** 轉變為 **"Observability" (可觀測性)**：

1.  **Monitoring (Known Unknowns)**：告訴你系統「壞了」。例如：CPU 飆高、HTTP 500 錯誤率上升。這是儀表板上的紅燈。
2.  **Observability (Unknown Unknowns)**：讓你有能力透過系統的輸出（Logs, Metrics, Traces）去問「為什麼壞了？」。例如：為什麼只有購買特定商品的 iOS 用戶在結帳時會延遲 5 秒？

### The Three Pillars + 1 (Correlation)
不要將這三者視為獨立的工具，它們是同一事件的不同切面，必須透過 **Correlation ID (Trace ID)** 串聯起來：

*   **Metrics (趨勢與聚合)**：*What is happening?* (e.g., "Latency is high"). 成本最低，適合觸發警報。
*   **Tracing (上下文與傳播)**：*Where is it happening?* (e.g., "Service B is waiting for Service C"). 展示請求的生命週期與依賴關係。
*   **Logs (細節與事件)**：*Why is it happening?* (e.g., "Database connection pool exhausted"). 提供最細顆粒度的錯誤訊息。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Metrics: The RED & USE Methods
不要隨意收集指標，應遵循業界標準方法論來建立 Dashboard。

*   **RED Method (For Services/Microservices)**：關注使用者體驗。
    *   **R**ate (請求速率)：每秒處理多少請求 (RPS)？
    *   **E**rrors (錯誤率)：有多少請求失敗了 (HTTP 5xx)？
    *   **D**uration (延遲/持續時間)：處理請求需要多久 (P95, P99 Latency)？
*   **USE Method (For Resources/Infrastructure)**：關注硬體與資源瓶頸。
    *   **U**tilization (使用率)：資源被使用了多少時間 (e.g., CPU 90%)？
    *   **S**aturation (飽和度)：有多少請求在排隊等待資源 (e.g., Disk I/O queue length)？
    *   **E**rrors (錯誤數)：資源本身發生的錯誤 (e.g., Disk read errors)。

### 2. Structured Logging & Context Injection
*   **JSON over Text**：絕對不要在生產環境輸出純文字日誌。使用 JSON 格式，讓 Log Aggregator (如 ELK, Splunk) 能自動解析欄位。
*   **Context Injection**：所有的 Log 必須自動包含當前的 `TraceID` 和 `SpanID`。這是將 Log 與 Tracing 連結的唯一紐帶。
    *   *Pattern:* 使用 MDC (Mapped Diagnostic Context) 或類似機制在 Middleware 層注入這些 ID。

### 3. Distributed Tracing Strategy
*   **W3C Trace Context**：使用標準協議 (如 `traceparent` header) 在服務間傳遞 Context，確保跨語言/跨框架的相容性。
*   **Sampling Strategies (採樣策略)**：
    *   *Head-based Sampling*：請求開始時決定是否採樣 (e.g., 10%)。優點是效能好，缺點是可能錯過稀有的錯誤案例。
    *   *Tail-based Sampling*：收集所有數據，但在結束時決定是否保留 (e.g., 只保留發生 Error 或 Latency > 2s 的 Trace)。成本較高，但對 Debug 最有價值。

### 4. Golden Signals Dashboard Design
*   **Top-Level View**：每個服務的首頁 Dashboard 應只顯示 RED 指標。
*   **Drill-down Links**：Dashboard 上的圖表應能直接跳轉到對應時間範圍的 Logs 或 Traces 搜尋頁面。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. High Cardinality Explosion (高基數爆炸)
這是 Metrics 系統 (尤其是 Prometheus) 最常見的死因。
*   **Anti-pattern**：將 `UserID`, `Email`, `UUID`, `URL Path` (包含 ID 參數) 放入 Metric Label 中。
*   **Consequence**：時間序列數量呈指數級增長，導致監控系統崩潰或查詢極慢。
*   **Fix**：Label 只能是有限的集合 (如 `status_code`, `method`, `service_version`)。具體 ID 請放在 Logs 或 Traces 中。

### 2. "Log and Throw" (記錄後拋出)
*   **Anti-pattern**：在 catch block 中記錄 error log，然後又將 exception 往上拋。
*   **Consequence**：同一個錯誤在 Call Stack 的每一層都被記錄一次，導致 Log 充滿重複雜訊，難以判斷根因。
*   **Fix**：只在最上層 (Global Exception Handler) 或邊界處記錄一次完整的 Stack Trace。

### 3. Blind Spots in Context Propagation
*   **Anti-pattern**：使用非同步處理 (如 `ThreadPool`, `Message Queue`) 時，忘記手動複製 Trace Context。
*   **Consequence**：Tracing 斷裂 (Broken Traces)。你看得到請求進入 Service A，然後消失，接著 Service B 莫名其妙開始工作，兩者無法關聯。
*   **Fix**：使用支援 Context Propagation 的 Wrapper 或 SDK (如 OpenTelemetry instrumentation) 包裝執行緒池與 Kafka/RabbitMQ 客戶端。

### 4. Alert Fatigue (警報疲勞)
*   **Anti-pattern**：為每一個 CPU 小幅波動或 Warning Log 設定 PagerDuty/Slack 通知。
*   **Consequence**：工程師習慣忽略警報，導致真正的 P0 事故被錯過。
*   **Fix**：警報應針對 **Symptom (症狀)** 而非 **Cause (原因)**。例如：針對 "Error Rate > 5%" 報警 (症狀)，而不是 "DB CPU > 80%" (原因)。

---

## Checklists & workflows｜檢查清單與流程

### Developer Checklist: Definition of Done (DoD)
在提交程式碼前，請確認：

- [ ] **Logs**: 是否使用了結構化日誌 (JSON)？
- [ ] **Logs**: 關鍵流程 (如付款、下單) 是否有 Info 等級的 Log？
- [ ] **Logs**: Error Log 是否包含足夠的上下文 (Input params, UserID) 而不僅僅是 "Something went wrong"？
- [ ] **Metrics**: 新增的 API Endpoint 是否已自動納入 RED 指標監控？
- [ ] **Tracing**: 如果使用了新的執行緒或外部呼叫，Trace Context 是否成功傳遞？
- [ ] **Cardinality**: 確認沒有將無限增長的變數放入 Metric Labels。

### Troubleshooting Workflow (The "Look Left" Flow)
當收到 "High Latency" 警報時的標準排查流程：

1.  **Start with Metrics (Dashboard)**:
    *   確認是整體變慢還是單一實例變慢？
    *   確認是依賴服務 (Downstream) 變慢還是自身邏輯 (CPU/GC) 變慢？
2.  **Jump to Traces**:
    *   在 Dashboard 上選取異常時間段，跳轉至 Tracing 系統。
    *   過濾出 `Duration > P99` 的 Trace。
    *   查看 Waterfall 圖：哪一個 Span 佔用了最長時間？是 DB Query？還是 HTTP Call？
3.  **Drill down to Logs**:
    *   複製該慢速 Span 的 `TraceID`。
    *   在 Log 系統搜尋該 ID。
    *   查看該時間點的詳細 Log 訊息 (e.g., "Connection timeout", "Retrying...")。

---

## Real-world examples｜實戰案例

### Scenario: The "Mystery Spike"
**情境**：每隔一小時，Payment Service 的 P99 Latency 會從 200ms 飆升到 3s，持續 1 分鐘後恢復。

#### 1. Bad Practice (無可觀測性)
*   工程師盯著 `top` 指令看 CPU。
*   隨機 grep log 檔案找 "Error"。
*   猜測是網路問題，重啟服務 (重啟治百病)。
*   **結果**：問題反覆發生，無法根治。

#### 2. Good Practice (Observability in Action)
*   **Metrics**: 查看 Dashboard，發現 Latency 飆高時，Payment Service 的 Throughput (RPS) 沒有變化，但 DB 的 CPU 使用率暴增。
*   **Tracing**: 採樣到一個慢請求 (3.1s)。
    *   Trace 顯示：`PaymentService` -> `UserDB` (Select) 耗時 2.8s。
    *   Span Tag 顯示 SQL 語句：`SELECT * FROM users WHERE last_login < ?`。
*   **Logs**: 搜尋該 TraceID，發現 Log 紀錄：`Job: CleanUpInactiveUsers started`。
*   **Root Cause**: 原來是一個 Cron Job 每小時執行一次全表掃描清理使用者，鎖住了 DB 表格，導致付款請求被阻塞。
*   **Solution**: 將 Cron Job 移至 Read Replica 資料庫執行，或優化 SQL 索引。

### Code Snippet: Structured Logging with Context (Golang/Zap example)

```go
// ❌ Bad: Unstructured, no context
log.Println("Failed to process payment for user " + userID)

// ✅ Good: Structured, with Trace Context
// 假設 logger 已經透過 middleware 注入了 trace_id
logger.Error("Failed to process payment",
    zap.String("event", "payment_processing_failed"), // 易於搜尋的事件名
    zap.String("user_id", userID),                    // 高基數資料放在欄位中
    zap.Float64("amount", amount),
    zap.String("trace_id", span.SpanContext().TraceID().String()), // 關鍵：關聯 ID
    zap.Error(err),
)
```

### Code Snippet: Metric Labels (Prometheus example)

```text
# ❌ Bad: High Cardinality (包含 UserID)
http_requests_total{method="POST", path="/api/buy", user_id="u-12345"} 1

# ✅ Good: Low Cardinality (聚合數據)
http_requests_total{method="POST", path="/api/buy", status="500", region="us-east"} 1
```