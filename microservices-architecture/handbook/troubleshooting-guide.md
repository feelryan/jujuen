# 故障排除流程與維運檢核 / Troubleshooting Guide & Operational Checklist

在微服務架構中，當系統出現問題時，我們不再是面對單一進程（Process）進行除錯，而是面對一個由網絡連接的複雜分散式系統。本章節將指導你如何從「單機除錯」思維轉向「系統鑑識」思維，並提供上線前的維運檢核標準。

In microservices architecture, troubleshooting is no longer about debugging a single process but investigating a complex distributed system connected by networks. This chapter guides you to shift from a "monolithic debugging" mindset to a "system forensics" mindset and provides operational checklists for production readiness.

---

## Mental model｜心智模型

### 1. 從「除錯」轉向「鑑識」 (From Debugging to Forensics)
在單體應用中，你可以掛載 Debugger 逐步執行；但在微服務中，問題通常發生在服務之間的「縫隙」裡（網路延遲、序列化錯誤、部分失敗）。
- **核心思維**：你是一名**數位鑑識專家**。你無法總是「重現現場」，你必須依賴現場留下的證據（Logs, Metrics, Traces）來重建案發經過。
- **Core Mindset**: You are a **digital forensics expert**. You cannot always "reproduce the crime scene"; you must reconstruct the event based on the evidence left behind (Logs, Metrics, Traces).

### 2. MTTR > MTBF
分散式系統中，失敗是必然的（Inevitability of Failure）。
- 不要只追求「系統永遠不壞」（Mean Time Between Failures, MTBF）。
- 要追求「壞了能多快恢復」（Mean Time To Recovery, MTTR）。
- 故障排除的首要目標是 **止血（Mitigation）**，其次才是 **根治（Remediation）**。

### 3. 觀察的三支柱 (The Three Pillars of Observability)
故障排除依賴三個維度的資料，缺一不可：
1.  **Metrics (指標)**: *What* is happening? (e.g., CPU is 90%, Latency is 2s). 告訴你**有問題**。
2.  **Tracing (追蹤)**: *Where* is it happening? (e.g., Service A called Service B, and B timed out). 告訴你**問題在哪**。
3.  **Logs (日誌)**: *Why* is it happening? (e.g., NullPointerException, Connection Refused). 告訴你**問題原因**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 全局請求追蹤 (Distributed Tracing with Correlation IDs)
這是微服務除錯的黃金法則。
- **Pattern**: 在系統邊界（API Gateway）為每個請求生成一個唯一的 `Trace ID` (或 `Correlation ID`)。
- **Implementation**: 這個 ID 必須透過 HTTP Headers (如 `X-Request-ID` 或 `traceparent`) 傳遞給所有下游服務，並寫入每一行 Log 中。
- **Benefit**: 當客戶投訴「訂單失敗」時，你只需用一個 ID 就能在 Kibana/Splunk 中撈出跨越 10 個服務的所有相關 Logs。

### 2. RED 方法監控服務 (The RED Method)
由 Tom Wilkie 提出，針對微服務最有效的監控模式：
- **Rate (請求率)**: 每秒處理多少請求？ (Traffic volume)
- **Errors (錯誤率)**: 有多少請求失敗了？ (5xx codes)
- **Duration (延遲)**: 請求處理需要多久？ (Latency distribution, p50/p90/p99)
- **Action**: 為每個微服務建立標準化的 RED Dashboard。

### 3. 結構化日誌 (Structured Logging)
不要再寫純文字 Log 了。
- **Bad**: `logger.info("User login failed for " + userId)`
- **Good (JSON)**: `logger.info("User login failed", { "event": "login_failed", "user_id": 123, "reason": "bad_password" })`
- **Why**: 機器可讀（Machine-readable）。讓 Log Aggregation 工具可以輕易地進行 `WHERE user_id = 123` 的查詢。

### 4. 故障隔離與降級 (Fault Isolation & Degradation)
- **Circuit Breaker**: 當下游服務掛掉時，主動熔斷，避免連鎖反應（Cascading Failure）。
- **Fallback**: 熔斷後提供預設值或快取資料，而不是直接噴 500 錯誤給使用者。

### 5. 無指責事後檢討 (Blameless Post-mortem)
- 發生重大事故後，撰寫 RCA (Root Cause Analysis) 報告。
- 重點不是「誰」犯了錯，而是「流程或系統」哪裡有漏洞，允許這個錯誤發生。
- **5 Whys**: 連續問五次「為什麼」，直到找到根本原因。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 吞噬錯誤 (Swallowing Exceptions)
- **Anti-pattern**: `catch (Exception e) { // do nothing }` 或只印出一行 `Error happened` 而沒有 Stack Trace。
- **Consequence**: 線索中斷。你在 Trace 中看到請求成功，但業務邏輯卻失敗了，完全找不到原因。

### 2. 警報疲勞 (Alert Fatigue)
- **Anti-pattern**: 設定太多不具備行動性（Actionable）的警報。例如：「CPU > 60%」就發 Slack 通知。
- **Consequence**: 團隊成員會將警報靜音或忽略。
- **Fix**: 警報應該針對 **症狀（Symptoms）**（如：使用者無法結帳），而不是 **原因（Causes）**（如：CPU 高）。除非 CPU 高導致了延遲增加。

### 3. 依賴「英雄」 (Hero Culture)
- **Anti-pattern**: 只有資深工程師 Bob 知道怎麼重啟那個老舊的 Payment Service，或者只有他看得懂那些 Log。
- **Consequence**: 當 Bob 休假時，系統癱瘓時間（Downtime）會無限延長。
- **Fix**: 建立 Runbooks（維運手冊），讓任何人都能照表操課。

### 4. 本地環境與生產環境差異過大 (Environment Drift)
- **Anti-pattern**: 開發用 Docker Compose，生產用 Kubernetes，且配置（Config）管理混亂。
- **Consequence**: "It works on my machine" 成為常態，除錯變成猜謎。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 故障排除標準流程 (The Firefighting Workflow)

1.  **Triage (檢傷分類)**:
    - 影響範圍多大？（全站癱瘓 vs 單一功能異常）
    - 是否需要立即回滾（Rollback）？
2.  **Mitigate (止血)**:
    - 目標是恢復服務，不是修復 Bug。
    - 動作：重啟、擴容（Scale out）、開啟熔斷（Circuit Break）、切換流量、回滾版本。
3.  **Investigate (調查)**:
    - 查看 RED Metrics 確認異常點。
    - 透過 Trace ID 追蹤請求路徑。
    - 檢查 Logs 尋找錯誤訊息。
4.  **Remediate (根治)**:
    - 在非生產環境重現問題。
    - 修復 Bug 並經過測試後發布 Hotfix。
5.  **Post-mortem (檢討)**:
    - 填寫事故報告，更新 Runbook。

### ✅ Production Readiness Checklist (上線前檢核)

在將微服務推向 Production 之前，請確認以下項目：

#### Observability (可觀測性)
- [ ] **Logging**: 所有 Log 是否都包含 `Trace ID`？格式是否為 JSON？
- [ ] **Metrics**: 是否已配置 RED (Rate, Errors, Duration) 儀表板？
- [ ] **Alerting**: 關鍵路徑（如登入、結帳）失敗時是否有 P1 警報？警報是否發送給正確的 On-call 人員？
- [ ] **Health Checks**: 是否配置了 Liveness Probe (重啟) 和 Readiness Probe (流量進入)？

#### Resilience (韌性)
- [ ] **Timeouts**: 所有對外呼叫（DB, API）是否都設定了合理的超時時間？（預設值通常是無限，這很危險）
- [ ] **Retries**: 重試機制是否包含 Exponential Backoff（指數退避）與 Jitter（隨機抖動）？
- [ ] **Circuit Breakers**: 針對非關鍵依賴（如推薦服務）是否配置了熔斷器？

#### Operations (維運)
- [ ] **Configuration**: 設定檔（Config）與密鑰（Secrets）是否與程式碼分離？
- [ ] **Runbooks**: 是否有文件說明常見問題的處理方式（如：如何手動觸發 Batch Job）？
- [ ] **Capacity**: 是否進行過負載測試（Load Testing）？是否設定了 Auto-scaling 規則？

---

## Real-world examples｜實戰案例

### 案例：神秘的 "504 Gateway Timeout"

**情境**:
使用者回報在「結帳頁面」偶爾會遇到超時錯誤，但在開發環境無法重現。

**除錯步驟 (The Investigation)**:

1.  **Check Metrics (Dashboard)**:
    - 查看 Checkout Service 的 RED Dashboard。
    - 發現 `p99 Latency` 在尖峰時刻飆升到 30秒，但 `Error Rate` 沒有明顯增加（除了 Timeout）。
    - *初步判斷*: 這是效能問題，不是邏輯崩潰。

2.  **Trace Analysis (Jaeger/Zipkin)**:
    - 在 Log 系統中搜尋 `status=504`，抓出一個受害者的 `Trace ID: abc-123`。
    - 在 Jaeger 中輸入 `abc-123`。
    - **視覺化結果**:
      ```text
      |-- API Gateway (Total: 30s)
          |-- Checkout Service (29.8s)
              |-- Get User Profile (50ms)
              |-- Validate Stock (100ms)
              |-- Calculate Tax (200ms)
              |-- **Apply Coupon Service (29s) -> RED BAR (Timeout)**
      ```
    - *發現*: 罪魁禍首是 `Apply Coupon Service`。

3.  **Deep Dive into Logs**:
    - 搜尋 `Apply Coupon Service` 在該時間段的 Logs。
    - 發現大量 `Connection Pool Exhausted` 錯誤。

4.  **Root Cause (RCA)**:
    - `Apply Coupon Service` 在查詢舊資料庫時，因為沒有加 Index，導致查詢變慢。
    - 連線佔用時間過長，耗盡了 DB Connection Pool。
    - 上游的 Checkout Service 等待直到 30s 超時。

5.  **Fix & Prevention**:
    - **Immediate**: 重啟 Coupon Service (暫時釋放連線)，並暫時關閉 Coupon 功能（Feature Flag）。
    - **Fix**: 為資料庫補上 Index。
    - **Prevention**: 在 Checkout Service 呼叫 Coupon Service 處加上 2秒的 Timeout 與 Circuit Breaker。這樣就算 Coupon 掛了，使用者仍能結帳（只是沒折扣）。