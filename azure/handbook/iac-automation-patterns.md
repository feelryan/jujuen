# 基礎設施即程式碼與自動化模式 / Infrastructure as Code (IaC) & Automation Patterns

## Mental model｜心智模型

在 Azure 環境中實踐 IaC，不應僅僅被視為「寫腳本來建立資源」，而應建立以下的心智模型：

1.  **宣告式終局狀態 (Declarative End-State)**：
    不要思考「如何建立」資源（Imperative），而是定義資源「應該長什麼樣子」（Declarative）。無論你執行程式碼一次還是的一百次，Azure 的狀態都應保持一致（Idempotency / 冪等性）。
    *   *Terraform*: 透過 State file 比較現狀與期望。
    *   *Bicep*: 透過 Azure Resource Manager (ARM) 直接比較現狀與 Template。

2.  **管線即守門員 (Pipeline as the Gatekeeper)**：
    Azure Portal 是唯讀的儀表板，CI/CD Pipeline 才是唯一的寫入介面。任何手動在 Portal 上的修改（ClickOps）都應被視為「技術債」或「配置漂移 (Configuration Drift)」。

3.  **基礎設施即軟體 (Infrastructure as Software)**：
    對待 `.bicep` 或 `.tf` 檔案應如同對待應用程式原始碼：
    *   需要版本控制 (Git)。
    *   需要 Code Review (PR)。
    *   需要測試 (Linting, Validation, What-if/Plan)。
    *   需要模組化 (DRY principle)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 工具選擇：Bicep vs. Terraform
在 Azure 上，這是一個經典的決策點。

| 特性 | Azure Bicep | Terraform (Azure Provider) |
| :--- | :--- | :--- |
| **State Management** | **Stateless** (State 存在 Azure 平台本身)。 | **Stateful** (需自行維護 `tfstate` 檔案)。 |
| **Day 0 Support** | 支援所有 Azure 最新功能 (Native)。 | 需等待 Provider 更新 (通常很快，但有延遲)。 |
| **Multi-cloud** | 僅限 Azure。 | 支援 AWS, GCP, Azure 等多雲。 |
| **語法與學習曲線** | 簡潔，對 Azure 工程師直觀。 | HCL 語言，通用性高，生態系龐大。 |
| **推薦場景** | **Azure-Only** 團隊，追求簡單維運與原生整合。 | **Multi-Cloud / Hybrid** 企業，或已有 Terraform 團隊。 |

### 2. Terraform State 管理模式 (The Remote State Pattern)
若選擇 Terraform，State 的安全性與鎖定至關重要。
*   **Storage Account**: 使用 Azure Storage Account (Blob) 存放 `.tfstate`。
*   **State Locking**: 必須啟用 Blob Lease 機制，防止多人同時執行導致 State 損毀。
*   **Security**: 啟用 Encryption at rest，並限制該 Storage Account 的網路存取（僅允許 CI/CD Runner IP）。

### 3. 模組化架構 (Modular Architecture)
無論使用 Bicep 或 Terraform，都應採用 **Modules (模組)** 與 **Live/Environment (環境)** 分離的模式。

*   **Modules Library**: 定義「單一資源的最佳實踐」。例如，一個 Storage Account 模組預設強制開啟 HTTPS 與 TLS 1.2。
*   **Composition (Environment)**: 組合多個模組來構成實際服務。

```text
/ (Root)
├── modules/                 # 可重複使用的元件
│   ├── networking/
│   ├── compute/
│   └── database/
└── environments/            # 實際部署定義
    ├── dev/
    │   └── main.bicep       # 呼叫 modules
    └── prod/
        └── main.bicep
```

### 4. CI/CD 安全整合：Workload Identity Federation
**不要再使用 Service Principal Client Secrets (密碼) 了！**
*   **Pattern**: 使用 **OIDC (OpenID Connect)** 連接 GitHub Actions/Azure DevOps 與 Azure。
*   **Benefit**: 不需要輪替密碼 (Secret rotation)，不需將長效憑證存放在 CI/CD 變數中。透過 Azure AD (Entra ID) 的 Federated Credentials 建立短效信任。

### 5. 部署預覽 (Deployment Preview)
在 Apply 之前，必須先讓工程師看到「將會發生什麼改變」。
*   **Bicep**: 使用 `az deployment group what-if`。
*   **Terraform**: 使用 `terraform plan` 並將 output 存檔，在 Apply 階段讀取該 plan 檔。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. ClickOps (手動點擊維運)
*   **現象**：緊急情況下直接在 Azure Portal 修改 Firewall 規則，卻沒有回寫到 Code。
*   **後果**：下次 CI/CD 執行時，Terraform/Bicep 會將該修改覆蓋回去，導致故障重現；或是 Terraform 偵測到 Drift 導致 Pipeline 失敗。
*   **解法**：嚴格執行 GitOps 流程，緊急修復也需透過 Hotfix Branch 進行。

### 2. Monolithic Template (巨型樣板)
*   **現象**：一個 `main.bicep` 或 `main.tf` 超過 2000 行，包含 VNet, VM, DB 所有定義。
*   **後果**：可讀性極差，變更影響範圍難以預測，執行 Plan/Apply 速度極慢。
*   **解法**：依據生命週期拆分 (Lifecycle Splitting)。網路 (VNet) 變更頻率低，應用 (App Service) 變更頻率高，應分開管理。

### 3. Committing Secrets / State to Git
*   **現象**：將 `terraform.tfstate` 或包含 `client_secret` 的 `tfvars` 檔案推送到 Git Repo。
*   **後果**：重大資安漏洞。State file 包含所有資源的明文資訊（包括 DB 密碼）。
*   **解法**：`.gitignore` 必須包含 `*.tfstate`, `*.tfvars`, `.env`。使用 Azure Key Vault 引用機密。

### 4. Hardcoding Resource IDs
*   **現象**：直接在程式碼中寫死 Resource ID (e.g., `/subscriptions/xyz/resourceGroups/rg-1/...`)。
*   **後果**：無法跨 Subscription 或跨環境 (Dev/Prod) 部署。
*   **解法**：使用 `resourceId()` 函數 (Bicep) 或 Data Sources (Terraform) 動態獲取 ID。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Deployment Workflow

1.  **Local Development**:
    - [ ] 撰寫/修改 IaC 程式碼。
    - [ ] 執行 Linter (e.g., `bicep build`, `terraform validate`, `tflint`)。
    - [ ] (Optional) 本地執行 Dry-run (`what-if` / `plan`) 確認邏輯。

2.  **Pull Request (CI)**:
    - [ ] **Automated Linting**: 檢查語法錯誤。
    - [ ] **Security Scan**: 執行工具如 `tfsec`, `checkov` 或 `PSRule for Azure` 掃描設定漏洞 (如 Storage 公開存取)。
    - [ ] **Plan/What-if**: CI 產生變更預覽，並作為 Comment 貼在 PR 中供 Reviewer 審查。

3.  **Merge & Deploy (CD)**:
    - [ ] **Authentication**: 透過 OIDC 取得 Azure 存取權。
    - [ ] **Apply**: 執行實際部署。
    - [ ] **Smoke Test**: 簡單驗證關鍵資源是否上線 (e.g., HTTP Check)。

### Project Setup Checklist

- [ ] **State Backend**: 已設定 Azure Storage Account 存放 Terraform State，並啟用 Versioning 與 Soft Delete。
- [ ] **Identity**: 已建立 User Assigned Managed Identity 或 Service Principal 供 CI/CD 使用。
- [ ] **Naming Convention**: 已定義資源命名規則 (e.g., `res-app-env-region`) 並透過 Module 強制執行。
- [ ] **Tagging Strategy**: 強制加上 `CostCenter`, `Environment`, `Owner` 等 Tags 以利成本分析。
- [ ] **Locking**: 對於關鍵資源 (VNet, Prod DB) 設定 `CanNotDelete` Management Lock。

---

## Real-world examples｜實戰案例

### Scenario: Bicep Module for Standardized Storage
企業要求所有 Storage Account 必須停用公網存取 (Public Access) 並強制 TLS 1.2。

**1. Module Definition (`modules/storage.bicep`)**
```bicep
// 封裝最佳實踐，隱藏複雜度
param storageAccountName string
param location string = resourceGroup().location
param tags object = {}

resource stg 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: tags
  properties: {
    minimumTlsVersion: 'TLS1_2'      // 強制資安規範
    allowBlobPublicAccess: false     // 強制資安規範
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Deny'          // 預設拒絕網路存取
    }
  }
}

output id string = stg.id
```

**2. Usage in Production (`environments/prod/main.bicep`)**
```bicep
// 引用模組
module logsStorage '../../modules/storage.bicep' = {
  name: 'deploy-logs-storage'
  params: {
    storageAccountName: 'stmyappprodlogs001'
    tags: {
      Environment: 'Production'
      Project: 'MyApp'
    }
  }
}
```

### Scenario: Terraform Remote State with Azure Backend
設定 Terraform 以使用 Azure Storage 作為後端，並支援鎖定。

**`backend.tf`**
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstatecorp001"
    container_name       = "tfstate-myapp"
    key                  = "prod.terraform.tfstate"
    use_oidc             = true  // 使用 Workload Identity Federation
    // access_key is NOT used here for security
  }
}
```

### Scenario: CI/CD Pipeline (GitHub Actions)
一個簡化的 Workflow，展示 OIDC 登入與 Bicep 部署。

```yaml
name: Azure Bicep Deploy
on:
  push:
    branches: [ main ]
permissions:
  id-token: write # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login (OIDC)
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Validate (Lint)
        run: az bicep build --file ./main.bicep

      - name: Preview Changes (What-If)
        run: |
          az deployment group what-if \
            --resource-group rg-myapp-prod \
            --template-file ./main.bicep

      - name: Deploy
        run: |
          az deployment group create \
            --resource-group rg-myapp-prod \
            --template-file ./main.bicep
```