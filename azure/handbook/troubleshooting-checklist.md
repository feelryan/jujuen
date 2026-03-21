# 故障排除流程與檢核表 / Troubleshooting Workflows & Checklists

## Mental model｜心智模型

在 Azure 環境中進行故障排除（Troubleshooting）時，最有效的心智模型並非「隨機嘗試修復」，而是 **「分層剝洋蔥」（Layered Exclusion）** 與 **「證據導向偵查」（Evidence-based Investigation）**。

### 1. The 4-Layer Diagnosis Model (四層診斷模型)
Azure 的問題通常可以歸類為以下四個層級，排查時應由下而上或由外而內進行：

1.  **Platform & Resource Health (平台層)**: Azure 自身是否有服務中斷？資源（如 VM, Web App）是否處於 Running 狀態？
2.  **Identity & Access (身分層)**: 請求是否通過驗證（Authentication）？是否有足夠權限（Authorization/RBAC）？
3.  **Networking & Connectivity (網路層)**: 封包是否能到達目的地？NSG、Firewall、DNS 或 Route Table 是否阻擋了連線？
4.  **Application & Data (應用層)**: 程式碼是否拋出 Exception？配置（Config）是否正確？資料庫連線字串是否過期？

### 2. The Observability Pipeline (可觀測性管線)
不要依賴「猜測」，要依賴「訊號」。
- **Metrics (指標)**: 告訴你 **"What"** is happening (e.g., CPU 100%, 403 Errors spiking).
- **Logs (日誌)**: 告訴你 **"Why"** it is happening (e.g., Stack trace, Firewall deny rule).
- **Traces (追蹤)**: 告訴你 **"Where"** it is happening (e.g., Latency in dependency call).

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Centralized Logging with KQL (集中化日誌與 KQL)
- **Pattern**: 將所有資源的 Diagnostic Settings 導向同一個 **Log Analytics Workspace**。
- **Why**: 當問題發生時，你不需要跳轉於不同的 Resource Blade 之間。使用 KQL (Kusto Query Language) 可以跨資源關聯錯誤。
- **Action**: 熟練掌握 `AzureActivity`, `AzureDiagnostics`, `AppServiceHTTPLogs`, `StorageBlobLogs` 等核心資料表。

### 2. Use "Network Watcher" over Ping (善用網路監控程式)
- **Pattern**: 當懷疑連線問題時，不要只在 VM 裡跑 `ping` 或 `telnet`。
- **Tool**: 使用 **IP Flow Verify (IP 流量驗證)** 來模擬封包，它能明確告訴你是哪一條 NSG Rule 阻擋了流量。使用 **Next Hop (下一個躍點)** 來確認路由表（UDR）是否將流量導向了錯誤的地方（如 Blackhole）。

### 3. Resource Health as First Step (資源健康度優先)
- **Pattern**: 在深入 Log 之前，先看 **Resource Health**。
- **Why**: 如果是 Azure 區域性故障或實體主機維護，你的程式碼除錯將是徒勞無功。

### 4. Divide and Conquer via Endpoints (端點隔離法)
- **Pattern**: 對於 PaaS 服務（如 Storage, SQL），區分是 **Public Endpoint** 還是 **Private Endpoint** 的問題。
- **Action**: 嘗試從同 VNet 的 VM 連線，再嘗試從公網連線，以縮小問題範圍（是防火牆規則錯了，還是 Private DNS Zone 解析失敗）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Shotgun Debugging" (散彈槍式除錯)
- **Anti-pattern**: 遇到問題直接重啟 VM、重啟 App Service 或隨意更改 NSG 規則，希望問題「神奇消失」。
- **Risk**: 這會破壞現場證據（暫存 Log、Memory dump），且通常無法解決根本原因（Root Cause），問題稍後會復發。

### 2. Ignoring SNAT Port Exhaustion (忽略 SNAT 連接埠耗盡)
- **Anti-pattern**: 應用程式間歇性連線失敗，但 CPU/RAM 正常，查不出原因就放棄。
- **Pitfall**: 在 App Service 或 Load Balancer 後端，對外連線數過多且未重用連線，導致 SNAT Ports 用盡。這是 Azure PaaS 常見的隱形殺手。

### 3. Misunderstanding NSG Hierarchy (誤解 NSG 層級)
- **Anti-pattern**: 只檢查了 Subnet 層級的 NSG，卻忘了 NIC 層級也有 NSG。
- **Pitfall**: NSG 規則是 **Subnet** 和 **NIC** 的交集（對於 Inbound）或聯集效果。必須兩者都允許，流量才能通過。

### 4. Confusing RBAC with Data Plane Access (混淆控制層與資料層權限)
- **Anti-pattern**: 給予使用者 `Owner` 或 `Contributor` 權限，卻發現他仍無法讀取 Key Vault 的 Secret 或 Storage Blob 的內容。
- **Pitfall**: Azure RBAC 主要控制「資源管理」（Control Plane）；資料存取（Data Plane）通常需要特定的角色（如 `Key Vault Secrets User` 或 `Storage Blob Data Reader`），或是資源本身的 Access Policy/Firewall。

---

## Checklists & workflows｜檢查清單與流程

### Workflow 1: General Troubleshooting (通用排查流程)

- [ ] **Step 1: Scope & Impact**
    - [ ] 確認受影響的 Resource ID。
    - [ ] 確認是完全中斷（Down）還是效能下降（Slow）。
    - [ ] 確認是全域問題還是特定使用者/地區問題。
- [ ] **Step 2: Platform Health**
    - [ ] 檢查 [Azure Status](https://status.azure.com/) 頁面。
    - [ ] 檢查該資源的 "Resource Health" Blade。
    - [ ] 檢查 "Service Health" 中的 Planned Maintenance。
- [ ] **Step 3: Metrics (The "What")**
    - [ ] 檢查 CPU, Memory, Disk I/O 是否觸及上限。
    - [ ] 檢查 Throttling 指標（如 SQL DTU percentage, Storage ServerLatency）。
- [ ] **Step 4: Logs (The "Why")**
    - [ ] 查詢 `AzureActivity` 查看最近是否有變更部署（Deployment）。
    - [ ] 查詢 Application Logs (AppInsights) 或 Resource Logs (Log Analytics)。

### Workflow 2: Connectivity Issues (網路連線問題)

- [ ] **DNS Resolution**
    - [ ] `nslookup <endpoint>` 解析出的 IP 是否正確？
    - [ ] 如果使用 Private Endpoint，是否解析到 Private IP？
- [ ] **Network Security Groups (NSG)**
    - [ ] 使用 **Network Watcher -> IP Flow Verify** 測試 Source IP 到 Destination IP/Port。
    - [ ] 檢查 Subnet NSG 和 NIC NSG 是否有 Deny 規則。
- [ ] **Firewall / NVA**
    - [ ] 流量是否經過 Azure Firewall 或 NVA？檢查 Firewall Logs。
    - [ ] 檢查 Route Table (UDR)，確認 Next Hop 是否正確。
- [ ] **PaaS Firewalls**
    - [ ] SQL Server / Storage Account 的 "Networking" 頁籤是否設為 "Selected Networks"？
    - [ ] Client IP 是否已加入白名單？

### Workflow 3: Permission & Access Denied (權限拒絕)

- [ ] **Control Plane (ARM)**
    - [ ] 使用者是否有 `Reader`, `Contributor` 等適當 RBAC 角色？
    - [ ] 是否有 Deny Assignment（通常來自 Blueprints 或 Managed Apps）？
- [ ] **Data Plane**
    - [ ] **Storage**: 檢查是否需要 `Storage Blob Data Contributor`（不僅僅是 Storage Account Contributor）。
    - [ ] **Key Vault**: 檢查 Access Policies 或 RBAC 模型設定。
    - [ ] **SQL**: 檢查 SQL Firewall 及 SQL Authentication (User/Password vs. Entra ID)。
- [ ] **Conditional Access**
    - [ ] 是否因為來源 IP、裝置狀態或 MFA 未通過而被 Entra ID (AAD) 阻擋？

---

## Real-world examples｜實戰案例

### Case 1: The "It works locally, but fails in Azure" (Web App VNet Integration)
**情境**: 開發者在本地可以連線 Azure SQL，但部署到 App Service 後無法連線。
**排查步驟**:
1.  **Check Error**: 錯誤訊息為 "The network path was not found" 或 Timeout。
2.  **Hypothesis**: App Service 的流量沒有正確進入 VNet。
3.  **Validation**:
    - 檢查 App Service 的 **Networking -> VNet Integration** 是否已開啟。
    - 檢查 Azure SQL Firewall，是否允許了該 VNet 的 Subnet。
    - **關鍵點**: App Service 預設走公網，若 SQL 關閉公網存取，必須配置 VNet Integration。
4.  **Fix**: 啟用 VNet Integration 並確認 Route All 設定正確。

### Case 2: The "Sudden Performance Drop" (SNAT Port Exhaustion)
**情境**: 一個高流量的 API 服務突然出現大量連線 Timeout，但後端資料庫正常。
**排查步驟**:
1.  **Check Metrics**: CPU/Memory 正常。
2.  **Check Logs**: 發現大量 `SocketException` 或連線嘗試失敗。
3.  **Tool**: 在 App Service 的 "Diagnose and solve problems" 中搜尋 "SNAT Port Exhaustion"。
4.  **Root Cause**: 程式碼每次 HTTP 請求都建立新的 `HttpClient` 實例，導致 Outbound Ports 用盡。
5.  **Fix**: 重構程式碼使用 Singleton `HttpClient`，或啟用 NAT Gateway 來增加可用 Ports。

### Case 3: "403 Forbidden" on Storage Account
**情境**: 應用程式無法寫入 Blob Storage，收到 403 錯誤。
**排查步驟**:
1.  **Identify Auth Type**: 應用程式是使用 Access Key 還是 Managed Identity？
2.  **Scenario A (Access Key)**:
    - 檢查 Storage Account Networking 設定。是否選了 "Selected networks" 且未包含應用程式 IP？
3.  **Scenario B (Managed Identity)**:
    - 檢查 IAM。該 Identity 是否只有 `Contributor`？
    - **Fix**: 需要賦予 `Storage Blob Data Contributor` 角色。`Contributor` 只能管理帳號屬性，不能操作資料。

### KQL Snippet for Troubleshooting
快速查找最近的失敗請求（適用於 App Service）：

```kusto
// 查詢最近 1 小時內的 HTTP 5xx 錯誤
AppServiceHTTPLogs
| where TimeGenerated > ago(1h)
| where ScStatus >= 500
| project TimeGenerated, CsMethod, CsUriStem, ScStatus, ScSubStatus, UserAgent, ResultDescription
| order by TimeGenerated desc
```