# 上線前檢核表與故障排除流程 / Production Readiness Checklist & Troubleshooting

## Mental model｜心智模型

在上線前夕，工程師的思維模式必須從 **「功能開發者 (Feature Builder)」** 切換為 **「系統維運者 (System Operator)」**。

一個功能完備（Feature Complete）的系統不等於生產就緒（Production Ready）。你的心智模型應該建立在 **「莫非定律 (Murphy's Law)」** 之上：假設資料庫會變慢、網路會抖動、第三方 API 會掛點。

### The "Flight Cockpit" Analogy (駕駛艙類比)
將你的 API 與資料庫系統想像成一架飛機：
1.  **儀表板 (Observability)**：你不能只靠感覺飛行。你需要精確的儀表（Metrics, Logs, Tracing）告訴你當前的請求量、延遲與錯誤率。
2.  **安全機制 (Safety Mechanisms)**：當亂流（流量暴衝）發生時，你需要自動斷路器（Circuit Breakers）與限流（Rate Limiting），而不是讓引擎過熱爆炸。
3.  **緊急程序 (Emergency Procedures)**：當引擎熄火（DB 死鎖或連線耗盡）時，你需要有標準作業程序（Checklist）來重啟或切換，而不是現場翻說明書。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Observability: The RED & USE Methods
不要隨意監控，請遵循業界標準模式：
*   **API 層採用 RED Method**：
    *   **R**ate (請求速率)：每秒有多少 Request？
    *   **E**rrors (錯誤率)：HTTP 5xx 的比例是多少？
    *   **D**uration (延遲)：P95 和 P99 的回應時間是多少？
*   **資料庫層採用 USE Method**：
    *   **U**tilization (使用率)：CPU、Memory、Disk I/O 佔用了多少？
    *   **S**aturation (飽和度)：是否有排隊現象（Run queue, Wait events）？
    *   **E**rrors (錯誤)：連線失敗、Deadlock 次數。

### 2. Timeouts & Retries (超時與重試策略)
*   **Layered Timeouts (分層超時)**：
    *   Load Balancer Timeout > API Server Timeout > DB Query Timeout。
    *   *Example:* LB (30s) -> API (25s) -> DB (10s). 確保內部先失敗，讓上層有機會處理錯誤。
*   **Fail Fast (快速失敗)**：不要讓使用者空等 60 秒才回傳 504 Gateway Timeout。
*   **Exponential Backoff (指數退避)**：重試時必須加入 Jitter (隨機抖動)，避免 Thundering Herd (驚群效應) 再次打垮資料庫。

### 3. Connection Pooling (連線池管理)
*   **Static Pool Size**：在生產環境中，固定連線池大小通常優於動態伸縮。避免在高負載時因為建立新連線的開銷（Handshake）導致延遲惡化。
*   **Validation Query**：配置 `testOnBorrow` (例如 `SELECT 1`)，確保拿到的連線是活的，避免拿到被防火牆切斷的 Zombie Connection。

### 4. Health Checks (健康檢查)
*   **Liveness Probe**：告訴 K8s/Load Balancer "我還活著嗎？" (若死掉則重啟 Pod)。
*   **Readiness Probe**：告訴 K8s/Load Balancer "我可以接客了嗎？" (若未準備好則不導流)。
    *   *Critical:* Readiness 檢查**不應該**包含對資料庫的依賴檢查，否則 DB 一閃斷，所有 API 實例同時下線，導致系統雪崩 (Cascading Failure)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Default Config" Trap (預設配置陷阱)
*   **陷阱**：使用框架或資料庫驅動的預設值上線。
*   **後果**：許多預設的 Timeout 是 `Infinite` (無限)，預設的 Pool Size 是 `Unlimited`。一旦 DB 變慢，API thread 會被無限期卡住，導致記憶體耗盡 (OOM)。

### 2. Logging Sensitive Data (紀錄敏感資訊)
*   **陷阱**：為了除錯方便，將 Request Body 全部印出。
*   **後果**：使用者的密碼、Token、個資被寫入 Log 系統，造成嚴重資安合規問題 (GDPR/PCI-DSS)。
*   **修正**：實作 Log Sanitization (脫敏) Middleware。

### 3. N+1 Query in Production (正式環境的 N+1)
*   **陷阱**：開發環境資料量少沒感覺，上線後資料量大增。
*   **後果**：一個 API 呼叫觸發數百次 DB 查詢，瞬間耗盡 DB CPU 與連線數。
*   **修正**：在 CI/CD 階段引入 Query Count Assertion，或使用 APM 工具偵測。

### 4. Lack of Graceful Shutdown (缺乏優雅停機)
*   **陷阱**：部署新版本時直接 `kill -9`。
*   **後果**：正在處理中的交易被強制中斷，導致資料不一致或前端收到 502 錯誤。
*   **修正**：監聽 `SIGTERM`，停止接收新請求，等待現有請求處理完畢 (設定 deadline，如 30s) 再關閉連線。

---

## Checklists & workflows｜檢查清單與流程

### ✅ Pre-flight Checklist (上線前檢核表)

#### Database & Schema
- [ ] **索引檢核**：所有 `WHERE`, `JOIN`, `ORDER BY` 欄位是否都有適當索引？(使用 `EXPLAIN` 確認)。
- [ ] **Schema Migration**：Migration script 是否具備冪等性 (Idempotent)？是否有 Rollback 腳本？
- [ ] **連線池設定**：`Max Connections` 是否小於 DB 伺服器的最大承載量？(考慮多個 API 實例的總和)。
- [ ] **敏感資料**：密碼、金鑰是否已加密儲存？

#### API Configuration
- [ ] **Timeouts**：Connect Timeout (建議 < 2s) 與 Read Timeout (建議 < 10s) 是否已明確設定？
- [ ] **Secrets**：所有 API Key、DB 密碼是否透過環境變數注入，而非 Hardcode？
- [ ] **CORS**：是否限制了允許的 Origin，而非 `*`？
- [ ] **Logging**：Log Level 是否設為 `INFO` (非 `DEBUG`)？是否已過濾 PII？

#### Infrastructure & Ops
- [ ] **Alerting**：是否設定了高延遲 (Latency > 1s) 與高錯誤率 (Error Rate > 1%) 的告警？
- [ ] **Backup**：DB 自動備份是否開啟？是否演練過還原流程？
- [ ] **Capacity**：是否進行過 Load Testing？知道系統的 TPS 上限在哪裡嗎？

---

### 🔧 Troubleshooting Workflow (故障排除流程)

當收到告警時，請依照以下決策樹進行排查：

#### Scenario A: High Latency (API 回應變慢)
1.  **Check APM/Tracing**：是 App 慢還是 DB 慢？
    *   **If DB is slow**:
        *   檢查 **Slow Query Log**：是否有全表掃描 (Full Table Scan)？
        *   檢查 **DB Locks**：是否有長交易 (Long Transaction) 鎖住了表？
        *   檢查 **Resources**：DB CPU 是否 100%？(可能是缺少索引或流量暴增)。
    *   **If App is slow**:
        *   檢查 **GC Logs**：是否發生頻繁 Full GC？
        *   檢查 **External Calls**：是否被第三方 API (如金流、簡訊) 拖累？

#### Scenario B: Connection Pool Exhausted (連線池耗盡)
*   **症狀**：API log 出現 `Connection pool exhausted` 或 `Timeout waiting for connection`。
*   **排查步驟**：
    1.  **Leak Check**：程式碼中是否有開啟 Transaction 但忘記 commit/rollback 的路徑？
    2.  **Slow Query**：是否有極慢的查詢佔用了連線，導致連線無法歸還？
    3.  **Scale Issue**：流量是否超過了當前 Pool Size 的負荷？(考慮擴展 Read Replica)。

#### Scenario C: Deadlocks (死鎖)
*   **症狀**：DB 拋出 `Deadlock found when trying to get lock`。
*   **排查步驟**：
    1.  **Capture Graph**：找出造成死鎖的兩條 SQL 語句。
    2.  **Analyze Order**：通常是因為兩個交易以「不同順序」存取相同的資源。
        *   *Tx1: Update A -> Update B*
        *   *Tx2: Update B -> Update A*
    3.  **Fix**：強制所有交易以「固定順序」鎖定資源 (例如依 ID 排序)。

---

## Real-world examples｜實戰案例

### Example 1: The "Firewall Cut" (防火牆切斷閒置連線)

**情境**：
系統每天早上第一波流量都會報錯，隨後恢復正常。Log 顯示 `Communications link failure`。

**原因分析**：
API 與 DB 之間經過防火牆。防火牆設定 TCP Idle Timeout 為 300 秒。應用程式的 Connection Pool 設定 `MaxLifetime` 為 30 分鐘。當連線閒置超過 5 分鐘，防火牆默默丟棄封包，但 App 認為連線仍有效。早上第一個 Request 拿到壞掉的連線，嘗試送出 SQL 時 Timeout。

**解決方案**：
```yaml
# HikariCP (Java) 或類似配置
dataSource:
  # 設定連線最大存活時間比防火牆 Timeout 短
  # 防火牆: 300s -> App: 240s (4分鐘)
  maxLifetime: 240000 
  
  # 每次從池中拿連線前，執行快速檢查 (雖然有損效能，但在不穩定網路環境很必要)
  connectionTestQuery: "SELECT 1" 
  # 或者使用驅動程式層級的 Keepalive
```

### Example 2: The "Migration Lock" (遷移鎖死)

**情境**：
開發者在上班時間執行 `ALTER TABLE users ADD COLUMN age INT DEFAULT 0;`。這是一個擁有 1000 萬筆資料的大表。

**災難現場**：
MySQL (5.6 或更舊版本) 在執行 ALTER TABLE 時鎖住了整張表 (Table Lock)。所有 `INSERT/UPDATE` `users` 的請求全部卡住，連線池瞬間爆滿，API 伺服器全部 503 Service Unavailable。

**解決方案**：
1.  **Immediate Action**：DBA 立即 `KILL` 該 ALTER TABLE 的 Process。
2.  **Long-term Fix**：
    *   使用 **Online DDL** (MySQL 5.7+ / PostgreSQL) 特性。
    *   或使用工具如 `gh-ost` 或 `pt-online-schema-change` 進行無鎖遷移。
    *   **Checklist 新增項目**：大表 Schema 變更必須在離峰時間執行，或確認該語句不會鎖表。