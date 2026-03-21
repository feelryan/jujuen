# 常見設計反模式與陷阱 / Common Anti-Patterns & Pitfalls

在 Azure 的實踐旅程中，最昂貴的教訓往往來自於將地端（On-premises）的思維直接套用到雲端環境，或是忽視了雲端資源的「共享租戶」特性。本章節整理了資深工程師在 Azure 上最常遇到的設計地雷，並提供具體的重構建議。

## Mental model｜心智模型

要避開 Azure 的反模式，你需要建立以下的核心心智模型：

1.  **資源並非無限，而是受限的共享池 (Limits & Throttling)**
    *   **誤區**：認為雲端資源是無限的，只要付錢就能線性擴展。
    *   **正解**：每個 Azure 資源（Storage Account, SQL DB, App Service Plan）都有其物理極限（IOPS, Connections, Throughput）。當你觸碰到這些隱形天花板時，Azure 會透過 Throttling（限流）來保護鄰居。
    *   **Key Concept**：**Noisy Neighbor & Limits**。設計時必須知道該資源的上限在哪裡（例如：單一 Storage Account 的 20k IOPS 上限）。

2.  **網路連接是動態且脆弱的 (Transient Faults)**
    *   **誤區**：網路連接是穩定且永久的。
    *   **正解**：在雲端，資源會動態移動（Failover, Patching），IP 會變，連線會瞬斷。應用程式必須具備「自我修復」能力。
    *   **Key Concept**：**Retry Logic is Mandatory**。沒有實作重試機制的程式碼在雲端就是 Bug。

3.  **身分識別優於金鑰 (Identity over Secrets)**
    *   **誤區**：習慣將 Connection Strings 或 Access Keys 寫在設定檔中。
    *   **正解**：金鑰管理是最大的資安漏洞來源。應盡可能依賴 Azure AD (Entra ID) 的身分驗證。
    *   **Key Concept**：**Managed Identity**。讓資源自己證明「我是誰」，而不是拿著鑰匙去開門。

---

## Patterns & best practices｜常見模式與最佳實務

在深入反模式之前，先確立正確的設計模式：

*   **Valet Key Pattern (代客泊車模式)**：
    *   不要讓 Web Server 充當檔案傳輸的中介。讓 Client 直接拿著 SAS Token (Shared Access Signature) 上傳/下載 Blob Storage，減輕運算資源負擔。
*   **Circuit Breaker (斷路器模式)**：
    *   當下游服務（如 SQL Database 或外部 API）故障時，快速失敗（Fail Fast）而不是持續重試導致資源耗盡。
*   **Throttling Pattern (限流模式)**：
    *   主動限制應用程式的請求速率，以符合後端服務（如 Cosmos DB RU/s）的配額，避免被 Azure 強制限流。
*   **Bulkhead Pattern (隔艙模式)**：
    *   將資源池隔離（例如為不同的服務使用不同的 Connection Pool），避免單一服務故障拖垮整個系統。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

這是本章的核心，以下列出 Azure 專案中最致命的常見錯誤：

### 1. SNAT Port Exhaustion (SNAT 連接埠耗盡)
這是 App Service 和 Azure Functions 最經典的網路問題。
*   **The Problem**: 當你的應用程式大量向外發起 HTTP 連線（例如呼叫外部 API 或 SQL），且沒有適當重用連線時，會耗盡 Azure Load Balancer 分配給你的 SNAT Ports（通常每個實例只有 128 個預分配）。
*   **Symptoms**: 應用程式隨機出現連線逾時、DNS 解析失敗，但在低負載時正常。
*   **The Fix**:
    *   **Code Level**: 確保 `HttpClient` 是 Singleton (C#) 或適當重用連線，不要每個 Request 都 `new HttpClient()`。
    *   **Infrastructure Level**: 使用 **Azure NAT Gateway** 綁定 Subnet。NAT Gateway 提供每 IP 64,000 個 SNAT ports，且處理機制更優於預設的 Load Balancer。

### 2. Improper Storage Account Sharing (不當的儲存帳戶共用)
*   **The Problem**: 將所有的 Logs、Images、VHDs 和 Application Data 全部塞進同一個 Storage Account。
*   **Symptoms**: 系統效能突然下降，出現 `ServerBusy` 或 `503 Service Unavailable` 錯誤。這是因為觸發了單一 Storage Account 的總吞吐量上限（例如 Standard 帳戶的 20 Gbps Ingress/Egress）。
*   **The Fix**:
    *   **Sharding**: 依據用途分割 Storage Accounts（例如：`stlogs`, `stdata`, `stapp`）。
    *   **Tiering**: 高頻存取使用 Premium Block Blob Storage；封存資料使用 Cool/Archive tier。

### 3. "ClickOps" & Configuration Drift (手動點擊維運)
*   **The Problem**: 在 Azure Portal 上手動修改資源設定（如增加 App Service 記憶體、修改 Firewall 規則），導致開發環境 (Dev) 與生產環境 (Prod) 不一致。
*   **Symptoms**: "It works on my machine/environment but fails in Prod." 災難復原時無法快速重建環境。
*   **The Fix**:
    *   嚴格執行 **Infrastructure as Code (IaC)**。使用 Bicep 或 Terraform 管理所有資源。Portal 僅用於「唯讀」檢視或緊急故障排除，任何變更必須回到 Code Repository。

### 4. Ignoring Cosmos DB Partition Keys (忽視分區鍵設計)
*   **The Problem**: 在 Cosmos DB 中選擇了基數（Cardinality）太低或分佈不均的 Partition Key（例如用 `Date` 或 `TenantId` 但某個 Tenant 超大）。
*   **Symptoms**: **Hot Partition** 問題。即使總 RU/s 足夠，特定 Partition 仍被限流（429 Too Many Requests），且擴展成本極高。
*   **The Fix**:
    *   選擇高基數且寫入均勻的 Key（如 `DeviceId`, `UserId`）。若需跨 Partition 查詢，考慮使用 Read-optimized 的設計或 Azure Synapse Link。

### 5. N+1 Query Problem in Cloud (雲端版 N+1 查詢)
*   **The Problem**: 應用程式對資料庫進行迴圈查詢，且應用程式與資料庫位於不同區域（Region）或有顯著延遲。
*   **Symptoms**: 頁面載入極慢。在地端低延遲環境下不明顯，但在雲端每一毫秒的 Network Round-trip 都會被放大。
*   **The Fix**:
    *   使用 Batch Query 或 Stored Procedures。
    *   啟用 **Azure Cache for Redis** 快取熱點資料。

---

## Checklists & workflows｜檢查清單與流程

在將服務部署到生產環境前，請執行以下「反模式掃描」：

### 🚀 Pre-flight Checklist (上線前檢核)

- [ ] **Networking & SNAT**:
    - [ ] 是否已配置 **NAT Gateway** 於 outbound subnet？
    - [ ] 檢查程式碼中的 HTTP Client 是否為 Singleton 或使用了 Connection Pooling？
- [ ] **Resilience & Retry**:
    - [ ] 應用程式是否對 Azure SQL/Storage/Service Bus 實作了 **Exponential Backoff** 重試機制？
    - [ ] 是否配置了 Circuit Breaker 防止級聯故障？
- [ ] **Security & Identity**:
    - [ ] 是否已移除程式碼中的 Connection Strings/Secrets？
    - [ ] 服務是否已啟用 **Managed Identity** 並透過 RBAC 授權存取 Key Vault/SQL/Storage？
    - [ ] Storage Account 是否已關閉 "Allow Blob public access"？
- [ ] **Observability**:
    - [ ] 是否設定了 **Diagnostic Settings** 將 Log 送至 Log Analytics？
    - [ ] 是否針對關鍵指標（CPU, Memory, HTTP 5xx, DTU/RU consumption）設定了 **Azure Monitor Alerts**？
- [ ] **Limits & Quotas**:
    - [ ] 檢查 Subscription 的 vCPU Quota 是否足夠應對 Auto-scale？
    - [ ] 確認 Storage Account 是否接近 20k IOPS 或 5 PB 容量上限？

---

## Real-world examples｜實戰案例

### Case 1: The "Black Friday" Timeout (SNAT 災難)

**情境**：
一家電商在黑色星期五促銷時，Web App 突然大量報錯 `System.Net.Sockets.SocketException`，但 CPU 和 Memory 使用率都很低。重啟 App Service 後恢復幾分鐘又掛掉。

**根本原因 (Root Cause)**：
開發者在處理訂單的迴圈中，每次呼叫外部金流 API 都 `using (var client = new HttpClient())`。高併發流量瞬間耗盡了 Azure Load Balancer 分配的 128 個 SNAT Ports。舊連線處於 `TIME_WAIT` 狀態無法釋放。

**解決方案 (Refactoring)**：
1.  **Code**: 改用 `IHttpClientFactory` (在 .NET Core 中) 注入單一 Client 實例。
2.  **Infra**: 在 VNet Subnet 上啟用 **NAT Gateway**，將可用 SNAT Ports 提升至 64k+。

### Case 2: The "Infinite" Log Bill (可觀測性反模式)

**情境**：
某新創團隊收到一張驚人的 Azure 帳單，其中 Log Analytics 的費用佔了 80%。

**根本原因 (Root Cause)**：
開發團隊將 Application Insights 的 Sampling (取樣) 關閉，並將所有 `Information` 和 `Debug` 等級的 Log 全部送往雲端。此外，在迴圈中記錄了大型 JSON 物件。

**解決方案 (Refactoring)**：
1.  **Configuration**: 啟用 Application Insights 的 **Adaptive Sampling**。
2.  **Filter**: 在 `host.json` 或 `appsettings.json` 中將預設 Log Level 設為 `Warning` 或 `Error`，僅對特定 Namespace 開啟 `Information`。
3.  **Design**: 避免在 Log 中寫入完整 Payload，僅記錄 ID 或關鍵 Metadata。