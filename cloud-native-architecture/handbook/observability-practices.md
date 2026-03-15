# 可觀測性實戰：不僅僅是監控 / Observability Practices: Beyond Monitoring

## Mental model｜心智模型

### 1. 監控 vs. 可觀測性 (Monitoring vs. Observability)
**監控 (Monitoring)** 告訴你系統「是否健康」（Is the system healthy?）。它關注的是「已知的未知」（Known Unknowns），例如 CPU 是否過高、磁碟空間是否不足。這像是汽車儀表板上的警示燈。

**可觀測性 (Observability)** 則賦予你詢問系統「為什麼發生這種狀況」（Why is it behaving this way?）的能力。它關注的是「未知的未知」（Unknown Unknowns），例如「為什麼只有在使用 iOS 且購物車超過 10 個項目的使用者會遇到延遲？」。這像是打開引擎蓋並擁有完整的診斷電腦。

### 2. 三大支柱與黏著劑 (The Three Pillars & The Glue)
不要將 Logs、Metrics 與 Tracing 視為三個獨立的工具，它們必須透過 **Correlation ID (Trace ID)** 緊密結合：

- **Metrics (指標)**：提供聚合的趨勢與警報（"What" & "When"）。*由點構成的線。*
- **Tracing (追蹤)**：提供請求在微服務間流轉的完整路徑與因果關係（"Where"）。*線條連接的點。*
- **Logs (日誌)**：提供特定事件的詳細上下文與錯誤訊息（"Why"）。*點上的詳細註釋。*

> **The Mental Shift:** In Cloud-Native, you cannot SSH into a server to `tail -f` logs. The system is ephemeral. Data must be pushed out, structured, and correlated *before* you need it.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 結構化日誌與關聯 ID (Structured Logging & Correlation IDs)
- **JSON over Text**: 不要再輸出純文字日誌。使用 JSON 格式，讓機器（如 ELK, Splunk, Loki）可以輕鬆解析與索引。
- **Context Propagation**: 在請求進入系統邊緣（Ingress/API Gateway）時生成一個全域唯一的 `Trace ID`，並確保它在所有下游服務調用（HTTP Headers, gRPC Metadata, Message Queues）中傳遞。
- **Log Injection**: 設定 Logger 自動將 `Trace ID` 與 `Span ID` 注入到每一條 Log entry 中。這讓你能透過一個 ID 瞬間撈出跨越 10 個微服務的所有相關 Log。

### 2. 指標設計模式 (Metrics Design Patterns)
- **The Golden Signals (Google SRE)**：針對終端使用者服務，關注這四個黃金訊號：
  - **Latency (延遲)**：請求花費的時間。
  - **Traffic (流量)**：系統有多忙碌（如 QPS）。
  - **Errors (錯誤)**：請求失敗的比率（HTTP 500s）。
  - **Saturation (飽和度)**：系統資源使用了多少（如 Queue depth, CPU usage）。
- **RED Method (for Services)**: Rate (請求率), Errors (錯誤率), Duration (耗時)。這是微服務最通用的儀表板模板。
- **USE Method (for Resources)**: Utilization (使用率), Saturation (飽和度), Errors (錯誤數)。適用於 CPU、Memory、Disk 等資源層級。

### 3. OpenTelemetry (OTel) 作為標準
- 採用 **OpenTelemetry** 作為收集遙測數據（Telemetry Data）的統一標準。避免被特定廠商（Vendor Lock-in）綁定。
- 使用 **OTel Collector** 作為 Sidecar 或 DaemonSet 來統一處理數據的清洗、採樣（Sampling）與轉發。

### 4. 採樣策略 (Sampling Strategies)
- **Head-based Sampling**: 在請求開始時決定是否保留（例如保留 1%）。優點是效能好，缺點是可能錯過稀有的錯誤案例。
- **Tail-based Sampling**: 先收集所有數據，在請求結束時根據結果（例如：是否有 Error？延遲是否超過 2秒？）決定是否保留。這是除錯最有效的方式，但對 Collector 的記憶體與頻寬要求較高。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 高基數指標災難 (High Cardinality Metrics)
這是最常見的 Metrics 陷阱。
- **Anti-pattern**: 在 Metrics 的 Label/Tag 中放入無限增長的值，例如 `User ID`、`Email`、`IP Address` 或 `UUID`。
  - `http_requests_total{user_id="12345"}` -> **WRONG**
- **Consequence**: 這會導致 Time Series Database (如 Prometheus) 的索引爆炸，記憶體耗盡，查詢極慢甚至崩潰。
- **Fix**: 將高基數資料放入 **Logs** 或 **Traces**，Metrics 只保留有限集合的 Tag（如 `status_code`, `service_name`, `region`）。

### 2. 斷裂的上下文 (Broken Context Propagation)
- **Anti-pattern**: 在服務內部使用非同步執行緒（Async Threads）或呼叫第三方 API 時，忘記傳遞 Trace Context。
- **Consequence**: Trace 斷成兩截。當你試圖追蹤一個慢請求時，路徑在中間憑空消失，無法定位下游的瓶頸。

### 3. 「記錄一切」的迷思 (Log Everything)
- **Anti-pattern**: 開發人員為了「以防萬一」記錄了大量 DEBUG 等級的垃圾訊息，或者在迴圈中印 Log。
- **Consequence**: 儲存成本飆升，且真正的錯誤訊息被淹沒在雜訊中（Signal-to-Noise ratio is low）。
- **Fix**: 實施動態 Log Level 調整，或使用採樣。確保 Log 包含「行動所需的資訊」（Actionable Info）。

### 4. 僅依賴平均值 (Reliance on Averages)
- **Anti-pattern**: 監控「平均延遲」（Average Latency）。
- **Consequence**: 平均值會掩蓋極端值（Outliers）。如果 99% 的請求很快，但 1% 的請求卡死，平均值看起來還是很健康。
- **Fix**: 永遠關注 **Percentiles (P95, P99)**。P99 代表最慢的那 1% 使用者的體驗，這通常才是優化的重點。

---

## Checklists & workflows｜檢查清單與流程

### Definition of Done for Observability (可觀測性驗收清單)

- [ ] **Correlation**: 所有服務是否都已實作 Trace Context Propagation (W3C Trace Context 標準)？
- [ ] **Logging**: Log 是否為 JSON 格式？是否包含 `trace_id`, `span_id`, `service_name`, `environment`？
- [ ] **Metrics**: 關鍵 API 是否都有 RED (Rate, Errors, Duration) 指標？
- [ ] **Alerting**: 警報是否基於症狀（Symptom-based，如「錯誤率 > 1%」）而非原因（Cause-based，如「CPU > 80%」）？
- [ ] **Dashboards**: 是否有分層儀表板？（L1: 業務全景 -> L2: 服務概況 -> L3: Pod/Instance 詳細資源）。
- [ ] **Privacy**: 是否已過濾掉 PII (個人識別資訊) 如密碼、信用卡號？

### Troubleshooting Workflow (故障排查流程)

1.  **Alert Triggered**: 收到 PagerDuty/Slack 警報（例如：Checkout Service P99 Latency > 2s）。
2.  **Check Metrics Dashboard**: 確認影響範圍。是單一 Instance 問題？還是全域問題？流量是否暴增？
3.  **Find Exemplars**: 在 Metrics 圖表上找到異常的時間點，跳轉至對應的 **Trace**。
4.  **Analyze Trace Waterfall**: 查看瀑布圖。
    - 哪一段 Span 最長？
    - 是否有資料庫鎖定？
    - 是否有循環呼叫 (N+1 Query)？
5.  **Drill down to Logs**: 點擊異常 Span，查看關聯的 **Logs**。
    - 讀取具體的錯誤堆疊 (Stack Trace) 或錯誤訊息。
6.  **Fix & Verify**: 修復問題，並觀察 Metrics 確認 P99 延遲恢復正常。

---

## Real-world examples｜實戰案例

### Scenario: The "Ghost" Latency (幽靈延遲)

**情境**：
使用者回報「訂單列表」頁面偶爾會卡住 5 秒鐘才載入。運維團隊查看 CPU 和 Memory，發現一切正常（低於 40%）。資料庫也沒有慢查詢紀錄。

**Debugging with Observability**:

1.  **Metrics**: 查看 `GET /orders` 的 P99 Latency，確認確實有部分請求高達 5000ms。
2.  **Tracing**: 透過 Trace ID 搜尋慢請求，打開瀑布圖（Waterfall View）。
    - 發現 `OrderService` 呼叫了 `InventoryService`。
    - `InventoryService` 的 Span 耗時極短（50ms）。
    - 但是 `OrderService` 和 `InventoryService` 之間有一段長達 4.9秒的空白間隙。
3.  **Analysis**: 這段空白通常代表網路問題或 Client 端超時重試。
4.  **Logs**: 檢查 `OrderService` 在該 Trace ID 下的 Log。
    ```json
    {
      "level": "error",
      "ts": "2023-10-27T10:00:05Z",
      "service": "order-service",
      "trace_id": "a1b2c3d4e5f6",
      "msg": "DNS resolution failed for inventory-service.local",
      "error": "dial tcp: lookup inventory-service.local: i/o timeout"
    }
    ```
5.  **Root Cause**: 這是 Kubernetes CoreDNS 偶發性的延遲問題，導致服務發現超時。
6.  **Conclusion**: 如果沒有 Tracing 和關聯 Log，工程師可能會花幾天懷疑資料庫索引或程式碼邏輯，而忽略了基礎設施層的 DNS 問題。

### Code Example: Structured Log with Context (Go)

```go
// 錯誤示範：難以解析，沒有 Context
log.Printf("Failed to process order %s: %v", orderId, err)

// 最佳實務：結構化 + 自動注入 Trace Context
// 假設使用 Zap logger 與 OpenTelemetry
logger.Error("failed to process order",
    zap.String("order_id", orderId),
    zap.Error(err),
    zap.String("trace_id", span.SpanContext().TraceID().String()), // 關鍵：注入 Trace ID
    zap.String("span_id", span.SpanContext().SpanID().String()),
    zap.Int("attempt", retryCount),
)
```

**Output (JSON):**
```json
{
  "level": "error",
  "ts": 1698398400.123,
  "msg": "failed to process order",
  "order_id": "ord-123",
  "error": "payment gateway timeout",
  "trace_id": "5b8aa5a2d2c872e941a",
  "span_id": "5152152556",
  "attempt": 2
}
```