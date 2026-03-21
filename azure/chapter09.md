# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，雲端基礎設施不再僅是「建立資源」，而是關於「治理（Governance）」、「可重複性（Reproducibility）」與「災難復原（Disaster Recovery）」。本章將從手動操作（ClickOps）轉向嚴謹的基礎設施即程式碼（IaC）工程實踐。

For senior engineers, cloud infrastructure is no longer just about "provisioning resources"; it is about **Governance**, **Reproducibility**, and **Disaster Recovery**. This chapter shifts the focus from manual operations (ClickOps) to rigorous Infrastructure as Code (IaC) engineering practices.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **評估 IaC 工具選擇 (Evaluate IaC Tooling)**：深入理解 Azure Bicep 與 Terraform 的架構差異、狀態管理機制（State Management）與適用場景。
    Deeply understand the architectural differences, state management mechanisms, and use cases between Azure Bicep and Terraform.
2.  **設計模組化架構 (Design Modular Architecture)**：建立可重複使用、高內聚低耦合的 IaC 模組，以支援多環境（Dev/Staging/Prod）部署。
    Create reusable, high-cohesion, low-coupling IaC modules to support multi-environment (Dev/Staging/Prod) deployments.
3.  **實作自動化流水線 (Implement Automated Pipelines)**：結合 GitHub Actions 或 Azure DevOps，利用 OIDC (OpenID Connect) 進行無密鑰驗證，實現安全的 CI/CD 部署。
    Combine GitHub Actions or Azure DevOps with OIDC (OpenID Connect) for keyless authentication to achieve secure CI/CD deployments.
4.  **處理狀態與飄移 (Handle State & Drift)**：理解如何偵測與修復配置飄移（Configuration Drift），確保雲端環境與程式碼定義一致。
    Understand how to detect and remediate configuration drift, ensuring the cloud environment remains consistent with code definitions.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 宣告式 vs. 命令式 (Declarative vs. Imperative)

**心智模型**：想像你在餐廳點餐。
**命令式 (Imperative)** 是告訴廚師：「拿平底鍋，開火，打蛋，翻面，裝盤」。這類似於 Azure CLI 或 PowerShell 腳本，你必須定義每一個步驟。
**宣告式 (Declarative)** 是看著菜單說：「我要一份荷包蛋」。你不關心過程，只關心最終結果（End State）。Bicep 和 Terraform 屬於此類。

**Mental Model**: Imagine ordering food at a restaurant.
**Imperative** is telling the chef: "Get a pan, turn on the stove, crack an egg, flip it, and plate it." This is akin to Azure CLI or PowerShell scripts, where you define every step.
**Declarative** is looking at the menu and saying: "I want a fried egg." You don't care about the process, only the **End State**. Bicep and Terraform belong to this category.

在 Azure 中，這意味著 IaC 工具會負責計算「當前狀態」與「目標狀態」的差異（Diff），並只執行必要的 API 呼叫。

In Azure, this means the IaC tool is responsible for calculating the difference (Diff) between the "current state" and the "desired state," executing only the necessary API calls.

## 2.2 狀態管理：ARM vs. Terraform State (State Management)

這是資深工程師必須理解的關鍵差異：

This is a critical distinction senior engineers must understand:

*   **Azure Bicep (Stateless / Azure-Native)**:
    Bicep 是 ARM Templates 的抽象層。它沒有本地狀態檔案。**Azure Resource Manager (ARM)** 本身就是「真實的狀態來源（Source of Truth）」。當你部署 Bicep 時，Azure 會直接比對現有資源。
    Bicep is an abstraction over ARM Templates. It has no local state file. **Azure Resource Manager (ARM)** itself is the "Source of Truth." When you deploy Bicep, Azure directly compares it against existing resources.

*   **Terraform (Stateful / Vendor-Agnostic)**:
    Terraform 依賴一個 `terraform.tfstate` 檔案（通常存放在 Azure Storage Account）來映射資源 ID 與程式碼。這提供了更快的讀取速度（不需每次都查詢 Azure API），但也帶來了狀態鎖定（State Locking）與狀態不同步（State Drift）的管理成本。
    Terraform relies on a `terraform.tfstate` file (usually stored in an Azure Storage Account) to map resource IDs to your code. This offers faster reads (no need to query Azure APIs every time) but introduces management overhead for State Locking and State Drift.

## 2.3 不可變基礎設施 (Immutable Infrastructure)

在雲端原生環境中，我們傾向於**不修補**伺服器或服務，而是**替換**它們。如果配置需要變更，我們修改 IaC 程式碼，重新部署整個資源或更新其配置，而不是 SSH 進去手動修改。

In cloud-native environments, we tend **not to patch** servers or services but to **replace** them. If a configuration needs to change, we modify the IaC code and redeploy the resource or update its configuration, rather than SSH-ing in to manually tweak it.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構中的角色 (Role in Typical Architecture)

在 Production 環境中，IaC 不僅僅是部署腳本，它是系統設計的一部分。

In a production environment, IaC is not just a deployment script; it is part of the system design.

*   **模組化設計 (Modular Design)**: 大型系統會將基礎設施拆分為 Network (VNet, Subnets, NSG), Data (SQL, Storage), Compute (AKS, App Service) 等模組。這降低了「爆炸半徑（Blast Radius）」。
    Large systems split infrastructure into modules like Network, Data, and Compute. This reduces the "Blast Radius."
*   **環境隔離 (Environment Isolation)**: 使用同一份程式碼庫，透過不同的參數檔（Parameter Files / `.tfvars`）來部署 Dev, Staging, 和 Prod。這保證了環境的一致性（Parity）。
    Use the same codebase with different parameter files to deploy Dev, Staging, and Prod. This ensures environment parity.

## 3.2 安全性與合規性 (Security & Compliance)

資深工程師會關注 IaC 如何提升安全性：

Senior engineers focus on how IaC enhances security:

*   **Policy as Code**: 結合 Azure Policy，確保沒有人能部署不合規的資源（例如：禁止在非授權區域建立 VM）。
    Combine with Azure Policy to ensure no one can deploy non-compliant resources (e.g., forbidding VM creation in unauthorized regions).
*   **Secret Management**: IaC 程式碼中絕不包含機密。所有機密應透過 Azure Key Vault 引用，或在部署時動態生成並注入。
    IaC code never contains secrets. All secrets should be referenced via Azure Key Vault or dynamically generated and injected at deployment time.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將使用 **Bicep** 搭配 **GitHub Actions** 來演示一個現代化的部署流程。這裡的重點是使用 **OIDC (OpenID Connect)** 消除長效憑證（Service Principal Secrets）。

We will use **Bicep** with **GitHub Actions** to demonstrate a modern deployment flow. The focus here is using **OIDC (OpenID Connect)** to eliminate long-lived credentials (Service Principal Secrets).

## 4.1 場景背景 (Scenario Context)

我們需要部署一個標準的 Web 應用程式架構：
1.  Resource Group
2.  App Service Plan (Server Farm)
3.  App Service (Web App)
4.  Application Insights

We need to deploy a standard web application architecture: Resource Group, App Service Plan, App Service, and Application Insights.

## 4.2 Step 1: 定義 Bicep 模組 (Defining Bicep Module)

首先，建立一個可重複使用的模組 `webapp.bicep`。注意我們如何使用 `output` 來傳遞生成的屬性。

First, create a reusable module `webapp.bicep`. Note how we use `output` to pass generated attributes.

```bicep
// webapp.bicep
param location string = resourceGroup().location
param appName string
param sku string = 'S1'

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: '${appName}-plan'
  location: location
  sku: {
    name: sku
  }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
    }
  }
}

// Output the hostname for verification or other modules
output defaultHostname string = webApp.properties.defaultHostName
```

## 4.3 Step 2: 主入口文件 (Main Entry Point)

建立 `main.bicep` 來調用模組。這模擬了真實世界中組裝不同元件的過程。

Create `main.bicep` to invoke the module. This simulates the real-world process of assembling different components.

```bicep
// main.bicep
targetScope = 'subscription' // Deploying at subscription level to create RG

param rgName string
param location string
param appBaseName string

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: rgName
  location: location
}

module myWebApp './webapp.bicep' = {
  name: 'webAppDeployment'
  scope: rg // Deploy inside the newly created RG
  params: {
    appName: '${appBaseName}-${uniqueString(rg.id)}'
    location: location
  }
}
```

## 4.4 Step 3: 設定 GitHub Actions 與 OIDC (GitHub Actions with OIDC)

這是資深實踐的精髓：**不要在 GitHub Secrets 中儲存 Azure Client Secret**。使用 Azure 的 "Federated Credentials" 信任 GitHub 的 Repo。

This is the essence of senior practice: **Do not store Azure Client Secrets in GitHub Secrets**. Use Azure's "Federated Credentials" to trust the GitHub Repo.

**GitHub Workflow (`.github/workflows/deploy.yml`):**

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [ main ]

permissions:
  id-token: write # Required for OIDC requesting the JWT
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Azure Login (OIDC)
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Validate Bicep
        run: az deployment sub validate --location eastus --template-file ./main.bicep --parameters rgName=my-prod-rg location=eastus appBaseName=myapp

      - name: Deploy Bicep
        uses: azure/arm-deploy@v1
        with:
          scope: subscription
          region: eastus
          template: ./main.bicep
          parameters: rgName=my-prod-rg location=eastus appBaseName=myapp
```

**Why this works:**
1.  **安全性 (Security)**: GitHub Actions 向 Azure 請求 Token，Azure 驗證 Repo/Branch 是否匹配 Federated Credential，匹配則發放短效 Token。沒有密碼需要輪替（Rotate）。
    GitHub Actions requests a token from Azure. Azure validates if the Repo/Branch matches the Federated Credential. If so, it issues a short-lived token. No passwords to rotate.
2.  **冪等性 (Idempotency)**: Bicep 部署是冪等的。如果資源已存在且配置相同，Azure 什麼都不會做；如果配置不同，Azure 會更新它。
    Bicep deployment is idempotent. If the resource exists and configuration matches, Azure does nothing; if different, Azure updates it.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 混合使用 ClickOps 與 IaC (Mixing ClickOps and IaC)

*   **錯誤描述**: 團隊使用 Terraform/Bicep 部署，但在發生緊急事故（Incident）時，工程師直接在 Azure Portal 修改設定（例如擴充 VM 大小），卻忘記回寫到程式碼中。
    **Description**: The team uses Terraform/Bicep for deployment, but during an incident, engineers modify settings directly in the Azure Portal (e.g., scaling up a VM) and forget to backport the changes to the code.
*   **後果**: 下一次部署時，IaC 工具會檢測到「飄移（Drift）」並強制覆蓋，導致緊急修復失效，甚至引發二次故障。
    **Consequence**: During the next deployment, the IaC tool detects "Drift" and forcibly overwrites the changes, reverting the hotfix and potentially causing a secondary outage.
*   **解決方案**: 嚴格禁止手動寫入權限（Read-Only in Portal），或實施定期 Drift Detection 警報。
    **Solution**: Strictly enforce Read-Only permissions in the Portal, or implement regular Drift Detection alerts.

## 5.2 巨型單體 IaC 文件 (Monolithic IaC Files)

*   **錯誤描述**: 將所有資源（VNet, DB, App）寫在一個巨大的 `main.tf` 或 `main.bicep` 中。
    **Description**: Putting all resources (VNet, DB, App) into a single giant `main.tf` or `main.bicep`.
*   **後果**: 部署速度極慢，且任何小改動都有可能破壞整個環境（High Blast Radius）。
    **Consequence**: Deployment becomes extremely slow, and any small change carries the risk of breaking the entire environment (High Blast Radius).
*   **解決方案**: 依生命週期分層。網路層（變動少）與應用層（變動多）應分開管理與部署。
    **Solution**: Layer by lifecycle. The Network layer (changes rarely) and Application layer (changes frequently) should be managed and deployed separately.

## 5.3 在 IaC 中硬編碼機密 (Hardcoding Secrets in IaC)

*   **錯誤描述**: `password = "MySecret123!"` 直接寫在程式碼中。
    **Description**: Writing `password = "MySecret123!"` directly in the code.
*   **後果**: 機密進入 Git 歷史，永久洩漏。
    **Consequence**: Secrets enter Git history and are permanently compromised.
*   **解決方案**: 使用 Key Vault Reference (Bicep: `getSecret`) 或 Terraform Data Sources 讀取 Key Vault。
    **Solution**: Use Key Vault References (Bicep: `getSecret`) or Terraform Data Sources to read from Key Vault.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 Bicep vs. Terraform 的選擇策略

*   **問題**: "如果你要為一個新的 Azure 專案選擇 IaC 工具，你會選 Bicep 還是 Terraform？為什麼？"
    **Question**: "If you were to choose an IaC tool for a new Azure project, would you pick Bicep or Terraform? Why?"
*   **高分回答要點**:
    *   **多雲策略 (Multi-cloud)**: 如果公司同時使用 AWS/GCP，Terraform 是唯一選擇，因為它統一了工作流（雖然程式碼本身不通用）。
    *   **Day 0 支援 (Day 0 Support)**: Bicep 是 Azure 原生，所有新功能發布當天即可使用；Terraform 需要等待 Provider 更新。
    *   **狀態管理 (State Management)**: Bicep 不需要維護 State File，降低了維運複雜度；Terraform 需要處理 State Locking 和 Backend Storage。
    *   **結論**: 單純 Azure 環境且追求簡化維運 -> Bicep；混合雲或已有 Terraform 生態 -> Terraform。

## 6.2 處理現存資源 (Brownfield Deployment)

*   **問題**: "我們有一堆手動建立的資源，現在想導入 IaC，你會怎麼做？"
    **Question**: "We have a lot of manually created resources and want to introduce IaC. How would you approach this?"
*   **高分回答要點**:
    *   不要試圖一次重寫所有東西。
    *   **Terraform**: 使用 `import` block 將現有資源導入 State，再生成配置。
    *   **Bicep**: 使用 Azure Portal 的 "Export Template" 或 Visual Studio Code 的 "Insert Resource" 功能反向生成 Bicep code。
    *   驗證：先執行 `plan` (Terraform) 或 `what-if` (Bicep) 確保程式碼與現狀一致，再接管管理。

## 6.3 秘密管理與 CI/CD 安全

*   **問題**: "如何在自動化流水線中安全地將資料庫密碼傳遞給 App Service？"
    **Question**: "How do you securely pass a database password to an App Service in an automated pipeline?"
*   **高分回答要點**:
    *   **最佳解**: 根本不要傳遞密碼。使用 **Managed Identity** 讓 App Service 直接存取 SQL Database (Azure AD Auth)。
    *   **次佳解**: 如果必須用密碼，將密碼存入 Key Vault。在 Bicep/Terraform 中設定 App Service 的 App Settings 為 Key Vault Reference (`@Microsoft.KeyVault(...)`)，讓 App 啟動時自行去 Key Vault 抓取。CI/CD Pipeline 本身不需要接觸密碼明文。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點回顧 (Key Takeaways)

1.  **IaC 是軟體工程**: 對待基礎設施代碼應如同應用程式代碼一樣（Code Review, Version Control, CI/CD）。
    **IaC is Software Engineering**: Treat infrastructure code just like application code (Code Review, Version Control, CI/CD).
2.  **宣告式優於命令式**: 描述「它是什麼」，而不是「怎麼做」。
    **Declarative over Imperative**: Describe "what it is," not "how to do it."
3.  **狀態管理是核心**: 理解 Bicep (無狀態/Azure原生) 與 Terraform (有狀態/跨平台) 的取捨。
    **State Management is Core**: Understand the trade-offs between Bicep (Stateless/Azure-Native) and Terraform (Stateful/Cross-Platform).
4.  **身份驗證現代化**: 在 CI/CD 中使用 OIDC (Federated Credentials) 取代 Service Principal Secrets。
    **Modern Authentication**: Use OIDC (Federated Credentials) instead of Service Principal Secrets in CI/CD.
5.  **模組化**: 透過 Modules 實現標準化與重複使用，降低維護成本。
    **Modularization**: Achieve standardization and reuse through Modules, reducing maintenance costs.

## 下一步 (Next Steps)

*   **延伸閱讀**: 研究 **Azure Verified Modules (AVM)**，這是微軟官方維護的高品質 Bicep/Terraform 模組庫。
    **Further Reading**: Research **Azure Verified Modules (AVM)**, the official library of high-quality Bicep/Terraform modules maintained by Microsoft.
*   **下一章預告**: 基礎設施建立後，如何確保其健康運作？下一章將探討 **可觀測性與監控 (Observability & Monitoring)**，包括 Azure Monitor, Log Analytics 與 Application Insights 的進階應用。
    **Next Chapter**: Once infrastructure is up, how do you ensure it runs healthily? The next chapter will explore **Observability & Monitoring**, including advanced applications of Azure Monitor, Log Analytics, and Application Insights.