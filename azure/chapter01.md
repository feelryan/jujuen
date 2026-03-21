# 1. 前言與學習目標 (Introduction & Learning Objectives)

身為資深工程師，在 Azure 上構建系統時，往往容易將重心放在 Compute (AKS, App Service) 或 Data (SQL, Cosmos DB) 上，而忽略了最基礎但也最關鍵的「治理與身分識別」。在現代雲端架構中，**身分識別是新的防火牆 (Identity is the new firewall)**。若缺乏正確的治理觀念，隨著資源擴張，將導致權限管理混亂、資安漏洞以及合規性災難。

As a Senior Engineer building systems on Azure, it is easy to focus heavily on Compute (AKS, App Service) or Data (SQL, Cosmos DB), overlooking the foundational aspect of "Governance and Identity." In modern cloud architecture, **Identity is the new firewall**. Without proper governance concepts, resource expansion leads to chaotic permission management, security vulnerabilities, and compliance disasters.

完成本章後，你應該能夠達到以下目標：
By the end of this chapter, you should be able to:

1.  **區分並正確使用身分模型**：深刻理解 Microsoft Entra ID (原 Azure AD) 的運作機制，並能區分 Service Principal 與 Managed Identity 的適用場景。
    **Distinguish and correctly use identity models:** Deeply understand the mechanics of Microsoft Entra ID (formerly Azure AD) and differentiate between Service Principals and Managed Identities.
2.  **設計企業級資源階層**：利用 Management Groups、Subscriptions 與 Resource Groups 建立可擴展的治理架構。
    **Design enterprise-grade resource hierarchy:** Utilize Management Groups, Subscriptions, and Resource Groups to build a scalable governance architecture.
3.  **實作零信任 (Zero Trust) 存取控制**：結合 RBAC (Role-Based Access Control) 與 Azure Policy，確保「最小權限原則」與「合規性」自動化落地。
    **Implement Zero Trust access control:** Combine RBAC and Azure Policy to automate the "Principle of Least Privilege" and compliance enforcement.
4.  **消除程式碼中的靜態憑證**：展示如何透過 `DefaultAzureCredential` 與 Managed Identity，徹底移除 codebase 中的 connection strings 與 secrets。
    **Eliminate static credentials in code:** Demonstrate how to remove connection strings and secrets from the codebase using `DefaultAzureCredential` and Managed Identities.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 身分識別層級：Entra ID (AAD)
### Identity Layer: Entra ID (AAD)

**心智模型 (Mental Model)**：
將 **Microsoft Entra ID (前稱 Azure AD)** 想像成一個全球性的「護照簽發局」。它不屬於某個特定的 Virtual Machine 或 Application，而是獨立於 Azure Subscription 之外的全局服務 (Global Service)。Azure Subscription 只是「信任」這個簽發局的一個資源容器。

**Mental Model**:
Think of **Microsoft Entra ID (formerly Azure AD)** as a global "Passport Issuing Authority." It does not belong to a specific Virtual Machine or Application but is a Global Service independent of Azure Subscriptions. An Azure Subscription is merely a resource container that "trusts" this authority.

**關鍵區別 (Key Distinctions)**：
*   **Human Identities (Users)**: 真人使用者，通常受到 MFA 與 Conditional Access Policy 保護。
*   **Non-Human Identities (Workload Identities)**:
    *   **Service Principal**: 類似於「服務帳號 (Service Account)」，需要管理 Client ID 與 Secret/Certificate。
    *   **Managed Identity**: 這是 Azure 的殺手級功能。它是綁定在 Azure 資源（如 VM, App Service）上的身分。**它就像是資源的「生物特徵」，不需要密碼，且會隨資源刪除而自動銷毀。**

*   **Human Identities (Users)**: Real people, usually protected by MFA and Conditional Access Policies.
*   **Non-Human Identities (Workload Identities)**:
    *   **Service Principal**: Similar to a "Service Account," requiring management of Client ID and Secret/Certificate.
    *   **Managed Identity**: This is Azure's killer feature. It is an identity bound to an Azure resource (e.g., VM, App Service). **It acts like the resource's "biometrics"—no password is needed, and it is automatically destroyed when the resource is deleted.**

## 2.2 治理層級：RBAC vs. Azure Policy
### Governance Layer: RBAC vs. Azure Policy

很多資深工程師會混淆這兩者。請用以下方式區分：
Many senior engineers confuse these two. Distinguish them as follows:

*   **RBAC (Role-Based Access Control)** 專注於 **"Who"** (誰可以做什麼)。
    *   *例如*：User A 可以重啟這台 VM。
*   **Azure Policy** 專注於 **"What"** (什麼事情是被允許的，無論是誰做的)。
    *   *例如*：所有 VM 都必須開啟 Backup，或者禁止在 `West US` 以外的區域建立資源。

*   **RBAC (Role-Based Access Control)** focuses on **"Who"** (Who can do what).
    *   *Example*: User A can restart this VM.
*   **Azure Policy** focuses on **"What"** (What actions are allowed, regardless of who performs them).
    *   *Example*: All VMs must have Backup enabled, or creating resources outside of `West US` is prohibited.

## 2.3 資源階層 (Resource Hierarchy)
### Resource Hierarchy

Azure 的資源組織結構是權限繼承的基礎：
Azure's resource organization structure is the basis for permission inheritance:

`Management Group` -> `Subscription` -> `Resource Group` -> `Resource`

*   **類比 (Analogy)**：這就像是公司的組織圖。你在「總部 (Root Management Group)」設定的規則，會自動套用到「分公司 (Subscription)」以及底下的「部門 (Resource Group)」。
*   **AWS 對照**：Azure Management Groups 類似於 AWS Organizations 的 OUs (Organizational Units)。

*   **Analogy**: This is like a corporate org chart. Rules set at "Headquarters (Root Management Group)" automatically apply to "Branches (Subscriptions)" and their "Departments (Resource Groups)."
*   **AWS Comparison**: Azure Management Groups are similar to AWS Organizations' OUs (Organizational Units).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或實際架構設計中，Identity 與 Governance 決定了系統的**安全性 (Security)** 與 **運維可擴展性 (Operational Scalability)**。

In System Design Interviews or actual architecture design, Identity and Governance determine the system's **Security** and **Operational Scalability**.

## 3.1 Landing Zone 與多租戶隔離
### Landing Zone and Multi-tenant Isolation

在設計大型企業系統時，我們通常採用 **Hub-Spoke** 網路拓撲，並配合 Subscription 級別的隔離。

When designing large enterprise systems, we typically adopt a **Hub-Spoke** network topology combined with Subscription-level isolation.

*   **Identity Subscription (Hub)**: 雖然 Entra ID 是全局的，但我們常會有一個專門的 Subscription 用於存放共享的 Key Vaults 或 DevOps Agents，這些資源擁有高度敏感的身分權限。
*   **Workload Subscriptions (Spokes)**: 每個專案或環境 (Prod/Dev) 擁有獨立的 Subscription。這限制了 RBAC 的爆炸半徑 (Blast Radius)。如果 Dev 環境的權限設定錯誤，不會影響到 Prod。

*   **Identity Subscription (Hub)**: While Entra ID is global, we often have a dedicated Subscription for shared Key Vaults or DevOps Agents, which hold highly sensitive identity permissions.
*   **Workload Subscriptions (Spokes)**: Each project or environment (Prod/Dev) has its own Subscription. This limits the RBAC Blast Radius. Misconfigured permissions in the Dev environment will not affect Prod.

## 3.2 應用程式身分設計模式
### Application Identity Design Patterns

在微服務架構中，服務間的驗證 (Service-to-Service Authentication) 是關鍵。

In microservices architecture, Service-to-Service Authentication is critical.

*   **Legacy Pattern (Anti-pattern)**: 在 Config 檔中存放 Shared Keys 或 Service Principal 的 Client Secret。這導致了 Secret Rotation 的痛苦與洩漏風險。
*   **Modern Pattern (Best Practice)**:
    1.  啟用 **User-Assigned Managed Identity** (如果多個資源共享同一個身分) 或 **System-Assigned Managed Identity** (如果是一對一)。
    2.  在目標資源 (如 Azure SQL, Storage Account, Key Vault) 上，透過 RBAC 授權給該 Managed Identity。
    3.  應用程式使用 SDK (`Azure.Identity`) 自動獲取 Token。

*   **Legacy Pattern (Anti-pattern)**: Storing Shared Keys or Service Principal Client Secrets in config files. This leads to painful Secret Rotation and leak risks.
*   **Modern Pattern (Best Practice)**:
    1.  Enable **User-Assigned Managed Identity** (if multiple resources share the identity) or **System-Assigned Managed Identity** (if 1-to-1).
    2.  Grant RBAC permissions to that Managed Identity on the target resource (e.g., Azure SQL, Storage Account, Key Vault).
    3.  The application uses the SDK (`Azure.Identity`) to automatically acquire tokens.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：無密碼存取 Azure SQL Database
### Scenario: Passwordless Access to Azure SQL Database

**目標**：一個 .NET/Java/Python 應用程式 (跑在 App Service 上) 需要存取 Azure SQL，且**不允許**在 Connection String 中出現使用者名稱與密碼。

**Goal**: A .NET/Java/Python application (running on App Service) needs to access Azure SQL, and **no** username or password is allowed in the Connection String.

### 步驟 1：啟用 Managed Identity
### Step 1: Enable Managed Identity

在 App Service 中開啟 System-assigned identity。
Enable System-assigned identity in the App Service.

```bash
# Azure CLI Example
az webapp identity assign --name "my-app-service" --resource-group "my-rg"
```

### 步驟 2：設定 SQL Database 的 AAD Admin
### Step 2: Set AAD Admin for SQL Database

為了讓 SQL Server 接受 Entra ID 驗證，必須先設定一個管理員。
To allow SQL Server to accept Entra ID authentication, an admin must be set first.

```bash
az sql server ad-admin create --resource-group "my-rg" --server-name "my-sql-server" --display-name "my-admin-user" --object-id "<user-object-id>"
```

### 步驟 3：在資料庫中授權
### Step 3: Grant Permission inside the Database

登入 SQL Database (使用 AAD Admin 帳號)，執行 SQL 指令將 App Service 的身分加入為使用者。
Log in to the SQL Database (using the AAD Admin account) and execute SQL commands to add the App Service's identity as a user.

```sql
-- Create the user from the Managed Identity name
CREATE USER [my-app-service] FROM EXTERNAL PROVIDER;

-- Grant permissions (Least Privilege)
ALTER ROLE db_datareader ADD MEMBER [my-app-service];
ALTER ROLE db_datawriter ADD MEMBER [my-app-service];
```

### 步驟 4：修改程式碼 (使用 DefaultAzureCredential)
### Step 4: Modify Code (Use DefaultAzureCredential)

這是資深工程師必須掌握的 SDK 模式。`DefaultAzureCredential` 會自動依序嘗試：Environment Variables -> Managed Identity -> Visual Studio/CLI login。這意味著同一份 code 在本機開發時用你的帳號，部署後自動切換成 Managed Identity。

This is an SDK pattern every Senior Engineer must master. `DefaultAzureCredential` automatically tries in order: Environment Variables -> Managed Identity -> Visual Studio/CLI login. This means the same code uses your account during local dev and automatically switches to Managed Identity after deployment.

**Python Example:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import pyodbc
import struct

# 1. Acquire Token for SQL
credential = DefaultAzureCredential()
token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
SQL_COPT_SS_ACCESS_TOKEN = 1256 

# 2. Connect without password
conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:my-sql-server.database.windows.net,1433;Database=my-db;"
conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})

print("Successfully connected to SQL using Managed Identity!")
```

**為何這個做法優越？ (Why is this superior?)**
*   **Security**: 沒有靜態密碼 (Secret Zero problem solved)。
*   **Maintenance**: 不需要定期更換密碼 (Rotation is handled by Azure)。
*   **DevEx**: 本機與雲端使用統一的驗證邏輯。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Owner/Contributor 角色
### Abusing Owner/Contributor Roles

**錯誤 (Pitfall)**：為了方便，將 Service Principal 或 Developer Group 設定為 Subscription 的 `Contributor` 甚至 `Owner`。
**後果 (Impact)**：違反最小權限原則。`Contributor` 可以刪除資源、修改網路設定，甚至在某些情況下提升權限。
**修正 (Fix)**：使用 Custom Roles 或更細粒度的 Built-in Roles (如 `Storage Blob Data Contributor`，注意這與 `Storage Account Contributor` 不同，後者只能管理帳號本身，不能讀寫資料)。

**Pitfall**: For convenience, setting Service Principals or Developer Groups as `Contributor` or even `Owner` of a Subscription.
**Impact**: Violates the Principle of Least Privilege. `Contributor` can delete resources, modify network settings, and in some cases escalate privileges.
**Fix**: Use Custom Roles or more granular Built-in Roles (e.g., `Storage Blob Data Contributor` - note this is different from `Storage Account Contributor`, which manages the account but cannot read/write data).

## 5.2 忽略 PIM (Privileged Identity Management)
### Ignoring PIM (Privileged Identity Management)

**錯誤 (Pitfall)**：給予資深工程師「永久」的 Admin 權限。
**後果 (Impact)**：如果該工程師帳號被駭，攻擊者擁有無限期的最高權限。
**修正 (Fix)**：啟用 Entra ID PIM。預設工程師只有一般權限，當需要執行高權限操作時，需申請 "Just-In-Time" (JIT) 存取，並設定由時限 (例如 4 小時)。

**Pitfall**: Granting Senior Engineers "permanent" Admin access.
**Impact**: If that engineer's account is compromised, the attacker has indefinite supreme access.
**Fix**: Enable Entra ID PIM. By default, engineers have standard access. When high-privilege actions are needed, they request "Just-In-Time" (JIT) access with a time limit (e.g., 4 hours).

## 5.3 混淆 App Registration 與 Enterprise Application
### Confusing App Registration vs. Enterprise Application

**錯誤 (Pitfall)**：不清楚這兩者的關係，導致在多租戶 (Multi-tenant) 場景下配置錯誤。
**觀念 (Concept)**：
*   **App Registration**: 應用程式的「定義 (Definition)」(藍圖)。存在於開發者的 Tenant。
*   **Enterprise App (Service Principal)**: 應用程式的「實例 (Instance)」。存在於每一個使用該 App 的 Tenant 中。
**修正 (Fix)**：在設計 SaaS 應用時，理解當客戶同意 (Consent) 你的 App 時，是在他們的 Tenant 中建立了一個 Service Principal。

**Pitfall**: Unclear relationship between the two, leading to misconfiguration in Multi-tenant scenarios.
**Concept**:
*   **App Registration**: The "Definition" (Blueprint) of the app. Lives in the developer's Tenant.
*   **Enterprise App (Service Principal)**: The "Instance" of the app. Lives in every Tenant that uses the app.
**Fix**: When designing SaaS apps, understand that when a customer Consents to your app, a Service Principal is created in *their* Tenant.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試候選人，或在團隊內部進行架構審查 (Architecture Review)。

These questions can be used to interview candidates or for internal Architecture Reviews.

## Q1: 如何在不重構程式碼的情況下，強制執行合規性？
### Q1: How to enforce compliance without refactoring code?

*   **切入點**：Azure Policy。
*   **高分回答**：
    *   提到 **Azure Policy** 的 "Deny" 效果可以阻止不合規資源的建立 (例如：禁止 Public IP)。
    *   提到 "Audit" 模式可以用於現有資源的掃描而不中斷服務。
    *   提到 "DeployIfNotExist" 可以自動修復資源 (例如：自動安裝 Monitoring Agent)。

*   **Hook**: Azure Policy.
*   **Key Points**:
    *   Mention **Azure Policy**'s "Deny" effect to block non-compliant resource creation (e.g., forbid Public IP).
    *   Mention "Audit" mode for scanning existing resources without disruption.
    *   Mention "DeployIfNotExist" for auto-remediation (e.g., auto-install Monitoring Agent).

## Q2: 請解釋 Managed Identity 的原理，以及它為何比 Service Principal 安全？
### Q2: Explain how Managed Identity works and why it is safer than a Service Principal?

*   **切入點**：Secret Management 與 Lifecycle。
*   **高分回答**：
    *   Managed Identity 不需要開發者管理 Credential (沒有 Client Secret 需要輪替)。
    *   它的生命週期與 Azure 資源綁定 (VM 刪除，身分就刪除)。
    *   它避免了將機密簽入 Git 的風險。
    *   能區分 System-assigned (1:1, 隨資源生死) 與 User-assigned (1:N, 獨立生命週期) 的差異。

*   **Hook**: Secret Management and Lifecycle.
*   **Key Points**:
    *   Managed Identity requires no credential management by developers (no Client Secret to rotate).
    *   Its lifecycle is bound to the Azure resource (VM deleted, identity deleted).
    *   It eliminates the risk of checking secrets into Git.
    *   Ability to distinguish between System-assigned (1:1, dies with resource) and User-assigned (1:N, independent lifecycle).

## Q3: 在微服務架構中，如果一個 Service 需要存取另一個 Service，你會如何設計驗證機制？
### Q3: In a microservices architecture, how would you design authentication for one Service accessing another?

*   **切入點**：Service-to-Service Auth。
*   **高分回答**：
    *   不建議使用 API Keys (難管理、不安全)。
    *   建議使用 **Entra ID OAuth 2.0 Client Credentials Flow**。
    *   呼叫方 (Caller) 使用 Managed Identity 獲取 Token。
    *   接收方 (Receiver) 驗證 Token 的 Audience 與 Claims (App Roles)。
    *   這實現了標準化的身分驗證，無需自幹 Auth 系統。

*   **Hook**: Service-to-Service Auth.
*   **Key Points**:
    *   Discourage API Keys (hard to manage, insecure).
    *   Recommend **Entra ID OAuth 2.0 Client Credentials Flow**.
    *   The Caller uses Managed Identity to acquire a Token.
    *   The Receiver validates the Token's Audience and Claims (App Roles).
    *   This achieves standardized authentication without rolling your own Auth system.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Identity is the Perimeter**: 在雲端，身分識別比網路邊界更靈活且關鍵。
2.  **Managed Identity First**: 只要資源支援，優先使用 Managed Identity，拒絕在程式碼中寫死 Connection Strings。
3.  **RBAC for Who, Policy for What**: 用 RBAC 控制人員權限，用 Policy 控制資源合規性。
4.  **Least Privilege**: 善用 Custom Roles 與 PIM，避免濫用 Contributor/Owner。
5.  **Hierarchy Matters**: 妥善規劃 Management Groups 與 Subscriptions，以利大規模治理。

1.  **Identity is the Perimeter**: In the cloud, identity is more flexible and critical than network boundaries.
2.  **Managed Identity First**: Whenever supported, use Managed Identity; refuse to hardcode Connection Strings.
3.  **RBAC for Who, Policy for What**: Use RBAC for user permissions, Policy for resource compliance.
4.  **Least Privilege**: Utilize Custom Roles and PIM to avoid abusing Contributor/Owner.
5.  **Hierarchy Matters**: Plan Management Groups and Subscriptions carefully for scalable governance.

## 下一步 (Next Steps)
掌握了身分識別後，下一步我們將進入網路層面的安全設計。身分驗證通過了，但網路連線是否安全？
Having mastered Identity, the next step is Network Security Design. Authentication is passed, but is the network connection secure?

*   **Next Chapter**: `Azure Networking & Private Access`
*   **Topics**: Virtual Networks (VNet), Private Link (Private Endpoints), 與 Hub-Spoke Network Topology。