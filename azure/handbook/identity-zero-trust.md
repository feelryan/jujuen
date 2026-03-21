# 身分識別與零信任實踐 / Identity Management & Zero Trust Practices

## Mental model｜心智模型

在雲端時代，傳統的「城堡與護城河」（Castle-and-Moat）網路邊界防禦已不足夠。我們必須將思維轉變為 **「身分即邊界」（Identity is the New Perimeter）**。

### 1. 核心哲學：Zero Trust (零信任)
不要預設信任任何請求，無論它來自內部網路還是外部。
- **Verify Explicitly (明確驗證)**：永遠驗證身分、位置、裝置健康狀態、服務分類與異常行為。
- **Use Least Privilege Access (最小權限存取)**：僅給予完成工作所需的最小權限與最短時間（JIT/JEA）。
- **Assume Breach (假設已遭入侵)**：設計架構時，假設攻擊者已經在網路內部，透過微切分（Micro-segmentation）與加密來限制損害範圍。

### 2. Azure 身分體系的三支柱
理解 Azure 身分管理時，請將其分為三個層次：
1.  **Authentication (AuthN / 驗證)**：你是誰？(Entra ID Users, Service Principals, Managed Identities)
2.  **Authorization (AuthZ / 授權)**：你能做什麼？(Azure RBAC)
3.  **Access Control Policies (存取控制策略)**：在什麼條件下你能做？(Conditional Access)

> **Mental Shortcut**:
> - **Entra ID (Azure AD)** 是你的「身分證發放局」。
> - **RBAC** 是你的「門禁卡權限設定」。
> - **Conditional Access** 是「門口的警衛」，即使你有卡，如果你看起來可疑（例如來自陌生國家 IP），警衛也不會讓你進去。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 應用程式身分：優先使用 Managed Identities
在 Azure 資源之間（如 App Service 到 SQL Database，或 VM 到 Key Vault）的通訊，**絕對不要**使用 Connection Strings 或含有帳號密碼的設定檔。

- **System-Assigned Managed Identity**：
  - **適用場景**：資源生命週期獨立，例如單一 Web App。
  - **優點**：隨資源建立與刪除，零維護成本。
- **User-Assigned Managed Identity**：
  - **適用場景**：多個資源共享同一身分（例如 VM Scale Set 中的所有 VM 都需要存取同一個 Storage Account）。
  - **優點**：建立一次，重複指派，權限管理較乾淨。

### 2. CI/CD 身分：Workload Identity Federation
不要再為 GitHub Actions 或 Azure DevOps 建立帶有長期 Secret 的 Service Principal。
- **Pattern**：使用 **Workload Identity Federation (OIDC)**。
- **Why**：讓 GitHub/GitLab 的 Token 直接換取 Azure 的短效 Access Token。無需管理 Client Secret，消除了 Secret 過期或洩漏的風險。

### 3. 人員存取：PIM (Privileged Identity Management)
沒有人應該擁有「永久」的 Admin/Owner 權限。
- **Pattern**：所有高權限（Contributor 以上）應設定為 **"Eligible" (符合資格)** 而非 "Active" (啟用中)。
- **Flow**：工程師需要修改權限時 -> 申請啟用 -> 強制 MFA -> 填寫理由 -> 獲得 4 小時權限 -> 時間到自動撤銷。

### 4. RBAC 權限設計：由上而下的繼承與群組
- **Scope Strategy**：盡量在 **Resource Group** 層級指派權限，避免在 Subscription 層級指派過多權限（爆炸半徑過大），也避免在單一 Resource 層級指派（難以維護）。
- **Group-Based Assignment**：將權限指派給 **Entra ID Group**，而非個別 User。當人員異動時，只需調整 Group 成員，無需修改 Azure 資源設定。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Keys in Code" Trap
- **Anti-pattern**：將 Storage Account Key 或 SQL Password 寫死在程式碼或 `appsettings.json` 中。
- **Consequence**：原始碼洩漏等於資料庫被駭。
- **Fix**：使用 `Azure.Identity` SDK (`DefaultAzureCredential`) 配合 Managed Identity。如果非得用 Secret，請放在 Key Vault 並透過 Managed Identity 讀取。

### 2. Over-privileged Service Principals
- **Anti-pattern**：為了方便，給予 Service Principal `Contributor` 權限在整個 Subscription 上。
- **Consequence**：如果 CI/CD Pipeline 被入侵，駭客可以刪除整個訂閱下的所有資源。
- **Fix**：建立 Custom Role，僅給予部署所需的特定 Action（例如 `Microsoft.Web/sites/publish/Action`）。

### 3. Ignoring Conditional Access for Admins
- **Anti-pattern**：為了避免被鎖在門外，將 Global Admin 排除在 MFA 政策之外，且沒有設定 Break-glass account。
- **Consequence**：最高權限帳號只需密碼即可登入，極易被釣魚攻擊。
- **Fix**：強制所有 Admin 開啟 MFA，但保留 1-2 個 **Break-glass Accounts**（緊急帳號），設定極其嚴格的監控警報，僅在 Entra ID 故障時使用。

### 4. Confusing Control Plane vs. Data Plane
- **Pitfall**：以為有了 Azure RBAC 的 `Owner` 權限就能存取 Key Vault 內的 Secret 或 Storage 內的 Data。
- **Reality**：Azure 區分 **Control Plane** (管理資源本身) 與 **Data Plane** (存取內部資料)。
- **Fix**：Key Vault 需使用 RBAC 模式（推薦）或 Access Policy；Storage Account 需指派 `Storage Blob Data Contributor` 等 Data Plane 角色。

---

## Checklists & workflows｜檢查清單與流程

### Developer Implementation Checklist (開發階段)
- [ ] **Secret Scan**：已確認程式碼庫中沒有任何 Hardcoded Secrets (使用 GitGuardian 或 GitHub Advanced Security)。
- [ ] **Managed Identity**：應用程式是否已啟用 Managed Identity？
- [ ] **Local Dev Auth**：本機開發是否使用 `DefaultAzureCredential` (支援 Visual Studio, Azure CLI, VS Code 登入狀態)，確保與生產環境程式碼一致？
- [ ] **Key Vault References**：如果是 App Service，是否使用 `@Microsoft.KeyVault(...)` 語法來參考必要的 Secrets？

### Architecture & Security Review (架構審查)
- [ ] **RBAC Audit**：檢查 Subscription 下是否有不明的 `Owner` 或 `User Access Administrator`。
- [ ] **Service Principal Expiry**：檢查是否有即將過期或設為「永不過期」的 Client Secrets。
- [ ] **Public Access**：是否已關閉 Storage Account、SQL DB 的 Public Network Access，並強制走 Private Endpoint + Identity Auth？
- [ ] **PIM Setup**：生產環境的寫入權限是否都已納入 PIM 管控？

### Emergency Workflow (緊急應變)
- [ ] **Break-glass Account**：是否已建立緊急帳號（排除在一般 Conditional Access 外），並測試過登入流程？
- [ ] **Sign-in Logs**：是否知道如何使用 KQL 查詢 `SigninLogs` 與 `AuditLogs` 來追蹤異常登入？

---

## Real-world examples｜實戰案例

### Scenario 1: Web App 存取 SQL Database (The Modern Way)

**傳統做法 (Legacy)**：
在 Connection String 中包含 `User ID=admin;Password=supersecret;`。

**零信任實踐 (Zero Trust Practice)**：
1.  **Infrastructure**：
    - 開啟 Azure SQL 的 "Microsoft Entra authentication only" 模式（停用 SQL 驗證）。
    - 為 App Service 開啟 System-Assigned Managed Identity。
2.  **Database Setup**：
    ```sql
    -- 在 SQL DB 中執行，將 App Service 的身分加入為使用者
    CREATE USER [my-webapp-prod] FROM EXTERNAL PROVIDER;
    ALTER ROLE db_datareader ADD MEMBER [my-webapp-prod];
    ALTER ROLE db_datawriter ADD MEMBER [my-webapp-prod];
    ```
3.  **Code (C# Example)**：
    ```csharp
    // 不需要任何密碼，DefaultAzureCredential 會自動抓取 Managed Identity Token
    var conn = new SqlConnection("Server=tcp:mydb.database.windows.net;Database=mydb;");
    var credential = new DefaultAzureCredential();
    var token = credential.GetToken(new TokenRequestContext(new[] { "https://database.windows.net/.default" }));
    conn.AccessToken = token.Token;
    await conn.OpenAsync();
    ```

### Scenario 2: GitHub Actions 部署到 Azure

**反模式 (Anti-Pattern)**：
建立 Service Principal，產生 Client Secret (有效期 2 年)，將 JSON 貼到 GitHub Secrets。兩年後 Pipeline 突然壞掉，因為 Secret 過期。

**最佳實踐 (Best Practice - Workload Identity Federation)**：
1.  在 Entra ID App Registration 中設定 **Federated Credentials**。
2.  指定 `Subject` 為 `repo:my-org/my-repo:ref:refs/heads/main` (限制只有這個 Repo 的 main branch 能用)。
3.  **GitHub Workflow YAML**：
    ```yaml
    permissions:
      id-token: write # 必須允許取得 OIDC token
      contents: read

    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          # 注意：這裡完全不需要 client-secret
    ```