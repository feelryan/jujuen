# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲端原生時代，安全性不再是部署後的「附加選項」，而是架構設計的基石。對於資深工程師而言，理解 Azure 安全性不僅是配置防火牆，更在於如何實踐 **Zero Trust（零信任）** 模型，並在不犧牲開發速度的前提下，確保資料與身分的安全。

In the cloud-native era, security is no longer an "add-on" after deployment but the cornerstone of architectural design. For Senior Engineers, understanding Azure security goes beyond configuring firewalls; it’s about implementing the **Zero Trust** model and ensuring data and identity security without sacrificing development velocity.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實踐零信任架構 (Implement Zero Trust Architecture)：** 理解並應用 "Verify Explicitly"、"Use Least Privilege" 與 "Assume Breach" 三大原則於 Azure 環境。
2.  **精通機密管理 (Master Secret Management)：** 擺脫在程式碼或設定檔中硬編碼憑證的習慣，利用 **Azure Key Vault** 結合 **Managed Identities** 實現無密碼（Passwordless）存取。
3.  **設計網路防禦深度 (Design Network Defense in Depth)：** 區分並正確配置 **NSG (Network Security Groups)**、**Azure Firewall** 與 **Private Link**，以縮小攻擊面。
4.  **自動化合規與威脅防護 (Automate Compliance & Threat Protection)：** 利用 **Microsoft Defender for Cloud** 進行持續性的安全姿態管理（CSPM）。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 零信任模型 (The Zero Trust Model)

傳統的地端安全模型類似於「城堡與護城河」（Castle-and-Moat）：一旦進入內部網路，就被視為可信。然而在雲端，邊界已經模糊。**零信任**的心智模型是：「**永遠不信任，始終驗證**」。

The traditional on-premise security model resembles a "Castle-and-Moat" approach: once inside the internal network, you are trusted. However, in the cloud, the perimeter is blurred. The mental model for **Zero Trust** is: "**Never trust, always verify.**"

*   **身分即邊界 (Identity as the New Perimeter)：** 網路位置（IP）不再是信任的唯一依據，身分（Identity）才是新的控制點。
*   **微分割 (Micro-segmentation)：** 防止攻擊者在網路內部橫向移動（Lateral Movement）。

## 2.2 縱深防禦 (Defense in Depth)

想像一個洋蔥，核心是你的資料（Data）。每一層都提供獨立的保護，即使一層失效，下一層仍能阻擋攻擊。

Imagine an onion, where the core is your Data. Each layer provides independent protection, so even if one layer fails, the next can still block the attack.

1.  **Physical Security:** (Azure 負責 / Managed by Azure)
2.  **Identity & Access:** Azure AD (Entra ID), MFA.
3.  **Perimeter:** DDoS Protection, Azure Firewall.
4.  **Network:** NSG, VNet integration.
5.  **Compute:** OS patching, Malware protection.
6.  **Application:** WAF, Input validation.
7.  **Data:** Encryption at rest/transit, Key Vault.

## 2.3 Managed Identity vs. Service Principal

這是資深工程師必須釐清的概念。
This is a concept Senior Engineers must clarify.

*   **Service Principal (SP):** 類似於「服務帳號」。你需要手動管理 Client ID 和 Secret，且 Secret 會過期，容易洩漏。
    *   *Analogy:* 給外包商的一把實體鑰匙，如果他弄丟了或離職沒歸還，風險很高。
*   **Managed Identity (MI):** Azure 平台託管的身分。自動輪替憑證，與資源生命週期綁定。
    *   *Analogy:* 員工的生物辨識門禁卡。員工離職（資源刪除），權限自動失效，且無法被複製。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型微服務安全架構 (Typical Microservices Security Architecture)

在 Production 環境中，我們通常會採用 **Hub-Spoke** 網路拓撲來集中管理安全性。

In a Production environment, we typically adopt a **Hub-Spoke** network topology to centrally manage security.

*   **Hub VNet:** 部署 Azure Firewall、Bastion Host、VPN Gateway。所有進出流量（North-South）與跨 VNet 流量（East-West）皆受監控。
*   **Spoke VNet:** 部署 AKS 或 App Service。
*   **Data Services:** SQL Database、Cosmos DB、Storage Account。

### 關鍵設計決策 (Key Design Decisions)

1.  **公開存取 vs. 私有連線 (Public Access vs. Private Link):**
    *   **Anti-pattern:** 開啟 SQL Server 的 Public Endpoint 並允許 "Allow Azure Services"。這會讓所有 Azure 租戶（包括攻擊者的 VM）都有機會嘗試連線。
    *   **Best Practice:** 使用 **Private Link (Private Endpoint)**。將 PaaS 服務映射到 VNet 內的私有 IP，完全切斷公網存取。

2.  **機密存取流程 (Secret Access Flow):**
    *   應用程式啟動時，透過 **Managed Identity** 向 Azure AD 取得 Token。
    *   使用該 Token 存取 **Key Vault** 讀取連線字串（若必須使用連線字串）或直接存取支援 AD 驗證的資料庫（如 Azure SQL）。

## 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **可維護性 (Maintainability):** 使用 Managed Identity 雖然初期設定較多（RBAC），但消除了後續「更換過期密碼」的維運負擔。
*   **效能 (Performance):** Key Vault 存取會有網路延遲。**設計模式**上應在應用程式啟動時快取 Secrets，而非每次 Request 都呼叫 Key Vault。
*   **可觀測性 (Observability):** 啟用 Key Vault 和 NSG 的 Diagnostic Settings，將 Log 送至 Log Analytics，以便追蹤「誰在什麼時候讀取了什麼機密」。

---

# 4. 逐步示例：從不安全到零信任 (Walkthrough: From Insecure to Zero Trust)

### 場景 (Scenario)
我們有一個 .NET Core Web API 部署在 **Azure App Service**，需要存取 **Azure SQL Database**。

We have a .NET Core Web API deployed on **Azure App Service** that needs to access an **Azure SQL Database**.

### Phase 1: Naive Approach (不推薦 / Not Recommended)

開發者直接將 SQL 連線字串（包含帳號密碼）寫在 `appsettings.json` 中。

The developer writes the SQL connection string (including username/password) directly in `appsettings.json`.

```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=tcp:mydb.database.windows.net;Database=Orders;User ID=admin;Password=superSecretPassword!;"
  }
}
```

*   **風險 (Risk):** 程式碼洩漏 = 資料庫淪陷。密碼輪替困難，需要重新部署應用程式。

### Phase 2: Key Vault Integration (較佳 / Better)

將密碼移至 Key Vault，App 透過 Key Vault Reference 或 SDK 讀取。

Move the password to Key Vault, and the App reads it via Key Vault Reference or SDK.

1.  建立 Key Vault，新增 Secret `DbConnectionString`。
2.  開啟 App Service 的 **System-assigned Managed Identity**。
3.  在 Key Vault 的 Access Policies (或 RBAC) 中，授權該 Identity 擁有 `Secret User` 權限。
4.  程式碼修改：

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

// 使用 DefaultAzureCredential，它會自動依序嘗試：
// Environment Vars -> Managed Identity -> Visual Studio Creds -> Azure CLI Creds
var client = new SecretClient(new Uri("https://my-kv.vault.azure.net/"), new DefaultAzureCredential());
KeyVaultSecret secret = client.GetSecret("DbConnectionString");
string connStr = secret.Value;
```

### Phase 3: Zero Trust & Passwordless (最佳實踐 / Best Practice)

完全移除連線字串中的密碼，改用 Azure AD Authentication 直接連線 SQL。

Completely remove the password from the connection string and use Azure AD Authentication to connect to SQL directly.

1.  **SQL Server 設定:** 將 Azure AD User 設為 SQL Admin。
2.  **DB 授權:** 在 SQL 中執行 T-SQL，將 App Service 的 Managed Identity 加為使用者並授權。
    ```sql
    CREATE USER [my-app-service-identity] FROM EXTERNAL PROVIDER;
    ALTER ROLE db_datareader ADD MEMBER [my-app-service-identity];
    ```
3.  **程式碼設定:** 修改連線字串，不需要 Password。
    ```json
    "ConnectionStrings": {
      "DefaultConnection": "Server=tcp:mydb.database.windows.net;Database=Orders;Authentication=Active Directory Default;"
    }
    ```
    *注意：具體實作可能依 Driver 版本略有不同，核心是利用 Token 驗證。*

4.  **網路層:** 關閉 SQL Public Access，建立 Private Endpoint 連接至 App Service 所在的 VNet (需啟用 VNet Integration)。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 "Allow Azure Services" 的陷阱 (The "Allow Azure Services" Trap)

*   **錯誤 (Mistake):** 在 Azure SQL Firewall 設定中勾選 "Allow Azure services and resources to access this server"。
*   **為何不好 (Why it's bad):** 這不是指「我的 Azure 資源」，而是指「**所有** Azure 雲端內的 IP」。攻擊者只要在 Azure 開一台 VM，就能通過網路層防火牆（當然他還需要帳號密碼，但少了一層防護）。
*   **修正 (Fix):** 使用 VNet Rules 或 Private Link。

## 5.2 濫用 Key Vault 存取權限 (Over-permissive Key Vault Access)

*   **錯誤 (Mistake):** 給予 App Service `Key Vault Contributor` 或在 Access Policy 中勾選所有 Secret 權限（Get, List, Set, Delete...）。
*   **為何不好 (Why it's bad):** 違反最小權限原則（Least Privilege）。如果 App 被攻破，攻擊者可以刪除你的 Keys 造成勒索軟體效果。
*   **修正 (Fix):** 只給予 `Get` 和 `List` 權限，或者使用更細緻的 RBAC (`Key Vault Secrets User`)。

## 5.3 忽略 NSG 的 Outbound Rules (Ignoring NSG Outbound Rules)

*   **錯誤 (Mistake):** 只設定 Inbound 規則擋外部連線，Outbound 全部 Allow Any。
*   **為何不好 (Why it's bad):** 如果伺服器被植入惡意軟體，它可以輕易將資料外傳（Data Exfiltration）到攻擊者的 C&C 伺服器。
*   **修正 (Fix):** 限制 Outbound 流量，僅允許必要的目的地（如 Azure SQL, Storage, 必要的 3rd party API）。使用 **Azure Firewall** 的 FQDN filtering 會比 NSG 的 IP 規則更好管理。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試候選人，或在團隊內部進行架構審查（Architecture Review）。

These questions can be used to interview candidates or during internal Architecture Reviews.

### Q1: 如何在不更改程式碼的情況下，提升 Legacy App 的安全性？
**How to improve the security of a Legacy App without changing the code?**

*   **高分回答要點 (Key Points):**
    *   **Network:** 使用 VNet Integration 和 Private Endpoints 隔離 PaaS 服務。
    *   **WAF:** 在前方加上 Application Gateway (WAF) 過濾 SQL Injection / XSS。
    *   **Config:** 使用 App Service 的 "Key Vault References" 功能，讓環境變數直接解析 Key Vault 內容，程式碼只需讀取環境變數即可，無需引入 SDK。

### Q2: 請解釋 Azure Policy 與 RBAC 的區別，以及它們如何協同工作？
**Explain the difference between Azure Policy and RBAC, and how they work together?**

*   **高分回答要點 (Key Points):**
    *   **RBAC (Role-Based Access Control):** 專注於 **"Who"** (誰可以做什麼)。例如：User A 可以建立 VM。
    *   **Azure Policy:** 專注於 **"What"** (資源必須長什麼樣子)。例如：建立的 VM 必須是 `Standard_D2s_v3` 且不能有 Public IP。
    *   **協同:** 即使 RBAC 允許你建立 VM，如果違反 Policy，操作仍會被拒絕（Deny）。Policy 是防護網（Guardrails）。

### Q3: 在微服務架構中，如何處理跨服務的身分驗證（Service-to-Service Auth）？
**In a microservices architecture, how do you handle Service-to-Service Auth?**

*   **高分回答要點 (Key Points):**
    *   避免使用 Shared Keys 或 API Keys。
    *   利用 **Managed Identity** 獲取 Azure AD Token。
    *   接收端服務驗證 Token 的 Audience 和 Claims。
    *   如果是 AKS 環境，可以使用 **Workload Identity** (將 K8s Service Account 對應到 Azure Managed Identity)。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **Identity is the Perimeter:** 在雲端，身分驗證比網路邊界更重要。
2.  **Managed Identity First:** 盡可能使用 Managed Identity，避免處理 Service Principal 的 Credential 輪替。
3.  **Private Link over Public:** 生產環境的資料庫與儲存體應關閉 Public Access，僅透過 Private Endpoint 存取。
4.  **Least Privilege:** Key Vault 與 RBAC 設定應遵循最小權限原則。
5.  **Defender for Cloud:** 啟用它來自動掃描配置錯誤（Misconfigurations）與合規性問題。

### 後續延伸 (Next Steps)

*   **實作 (Action):** 檢查你目前的專案，是否仍有 Connection Strings 裸露在 `appsettings.json`？嘗試將其遷移至 Key Vault + Managed Identity。
*   **閱讀 (Read):** 下一章將探討 **Azure Monitor & Observability**，這對於偵測安全性事件至關重要。
*   **進階 (Advanced):** 研究 **Azure Sentinel (SIEM)**，了解如何聚合 Logs 並進行自動化威脅回應（SOAR）。