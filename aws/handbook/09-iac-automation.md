# 基礎設施即程式碼與自動化部署 / Infrastructure as Code (IaC) & CI/CD Automation

## Mental model｜心智模型

### 1. 宣告式終局狀態 (Declarative End-State)
不要把 IaC 當作是「一連串的指令腳本」（Imperative），而要將其視為「基礎設施的最終藍圖」（Declarative）。
- **Imperative (Scripting):** "Create a server, then install nginx, then open port 80." (Focus on *how*)
- **Declarative (IaC):** "I want a VPC with 2 subnets and an Auto Scaling Group running nginx on port 80." (Focus on *what*)

你的 IaC 工具（Terraform/CDK）是一個「差異計算機」。它的工作是不斷比對 **Code (Desired State)** 與 **Real World (Actual State)**，並計算出如何從 Actual 變更為 Desired。

### 2. 狀態檔即真理 (State as the Source of Truth)
在 AWS Console 上看到的資源是「投影」，儲存在 S3 Backend 的 State File 才是「真理」。
- 如果你在 Console 手動修改了資源（ClickOps），你就破壞了真理，這稱為 **Configuration Drift**。
- 任何不在 Code 裡的資源，理論上都不該存在（或者不該被長期信任）。

### 3. 不可變基礎設施 (Immutable Infrastructure)
盡量避免「原地修補」伺服器。
- **Mutable:** SSH 進去 EC2 跑 `yum update`。
- **Immutable:** 修改 IaC 中的 AMI ID，銷毀舊機器，啟動新機器。
這保證了環境的一致性，消除了 "It works on my machine" 的詭異問題。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 分層架構與狀態隔離 (Layering & State Isolation)
不要將所有資源寫在同一個 Terraform State 或 CDK Stack 中。這會導致 `plan` 時間過長，且爆炸半徑（Blast Radius）過大。

**Recommended Layers:**
1.  **Global/Bootstrap:** IAM Roles for CI/CD, S3 Buckets for State storage.
2.  **Network Layer:** VPC, Subnets, NAT Gateways, Transit Gateway. (很少變動)
3.  **Data Layer:** RDS, ElastiCache, DynamoDB. (極度危險，需啟用 Deletion Protection)
4.  **App Layer:** EC2, ECS Services, Lambda, ALBs. (頻繁變動)

### 2. 遠端狀態與鎖定 (Remote State & Locking)
**絕對不要**使用 Local State 進行團隊協作。
- **Terraform:** 使用 S3 Bucket 儲存 State，DynamoDB Table 進行 State Locking。
- **CDK:** `cdk bootstrap` 會自動幫你建立相關的 CloudFormation Stack 管理狀態。
- **Encryption:** 確保 State Bucket 啟用 SSE-KMS 加密，因為 State file 往往包含敏感資訊（即使是加密後的）。

### 3. 模組化策略 (Modularization Strategy)
- **Producer/Consumer Model:** 資深工程師/架構師撰寫經過安全加固的 Modules (Producers)，產品團隊引用這些 Modules (Consumers)。
- **Composition over Inheritance:** 不要寫一個 "Super Module" 包山包海。應該寫專注單一功能的 Module (e.g., `s3-private-bucket`, `rds-postgres`), 然後在 Root Module 中組裝它們。

### 4. CI/CD Pipeline Integration
IaC 的執行必須自動化，禁止工程師在本地電腦執行 `terraform apply` (Production 環境)。

**Standard Pipeline Flow:**
1.  **Feature Branch:** 執行 `fmt`, `validate`, `tflint/checkov` (Security Scan).
2.  **Pull Request:** 執行 `plan` 或 `diff`。Bot 將結果貼在 PR Comment 中供 Review。
3.  **Merge to Main:** 執行 `apply`。
4.  **Drift Detection:** 排程（如每晚）執行 `plan` 檢查是否有未被追蹤的 Console 修改。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. ClickOps (手動點擊控制台)
- **現象：** 緊急時刻直接在 AWS Console 修改 Security Group 開放 Port。
- **後果：** 下次部署 IaC 時，Terraform 會偵測到差異並試圖「修復」（覆蓋）你的修改，導致服務中斷；或是 State 已經與現實脫節。
- **解法：** 即使是 Hotfix，也必須透過 Code -> PR -> Apply 流程，或者事後立即補上 Code 並 `import` 狀態。

### 2. Hardcoded Secrets (硬編碼機密)
- **現象：** `password = "SuperSecret123"` 直接寫在 `.tf` 檔裡。
- **後果：** 密碼進入 Git 歷史，永久洩漏。
- **解法：** 使用 AWS Secrets Manager 或 SSM Parameter Store。IaC 只參照 Secret ARN，應用程式在 Runtime 讀取值；或是透過環境變數注入（但不要 commit 到 repo）。

### 3. The Monolithic State (巨型狀態檔)
- **現象：** 一個 `main.tf` 有 5000 行，管理 VPC + DB + 20 個 Microservices。
- **後果：** `terraform plan` 需要跑 10 分鐘；修改一個 Lambda 可能意外刪除 RDS。
- **解法：** 依據生命週期（Lifecycle）拆分 State。

### 4. Ignoring `.gitignore`
- **現象：** 把 `.terraform/` 資料夾或 `*.tfstate` 檔案 commit 到 Git。
- **後果：** 包含敏感資訊的 State 洩漏，且造成團隊間的 State 衝突。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the right tool
- 團隊熟悉 TypeScript/Python 且喜歡 OOP？ 👉 **AWS CDK**
- 團隊是混合雲（AWS + GCP + Azure）或偏好 HCL 宣告式語法？ 👉 **Terraform / OpenTofu**
- 只需要簡單的 Serverless 部署？ 👉 **AWS SAM** or **Serverless Framework**

### Pre-Commit / PR Checklist
- [ ] **Linting:** 程式碼格式是否符合標準 (`terraform fmt`, `eslint`)？
- [ ] **Security Scan:** 是否已通過靜態安全掃描 (Checkov, tfsec, cdk-nag)？
  - *e.g., S3 bucket沒有公開讀取權限、EBS Volume 有加密、Security Group 沒有開放 0.0.0.0/0 到 SSH。*
- [ ] **Plan Review:** `plan` 的輸出是否包含 `destroy`？如果是，是否預期？
  - *特別注意 Database 或 Stateful 資源的 Replacement。*
- [ ] **Tagging:** 所有資源是否都標上了 Cost Allocation Tags (e.g., `Project`, `Environment`, `Owner`)？

### Workflow: Handling Drift (當發現 Console 被手動修改時)
1.  **Identify:** 執行 `terraform plan` 看到 "Objects have changed outside of Terraform"。
2.  **Assess:** 該修改是合理的緊急修補，還是錯誤操作？
3.  **Remediate:**
    - *如果是合理的：* 修改 Code 以匹配現況 (Backporting)，再次執行 Plan 確保 No Changes。
    - *如果是錯誤的：* 執行 Apply 強制覆蓋，將基礎設施恢復到 Code 定義的狀態。

---

## Real-world examples｜實戰案例

### 1. Directory Structure for Terraform (Layered)
這是一個適合中大型團隊的目錄結構，強調環境隔離與模組重用。

```text
├── modules/                 # Shared Modules (Internal Library)
│   ├── networking/
│   ├── database/
│   └── app-service/
├── environments/            # Live Environments
│   ├── dev/
│   │   ├── 01-network/      # VPC, IGW (Change rarely)
│   │   ├── 02-data/         # RDS, ElastiCache (Stateful)
│   │   └── 03-app/          # ECS, Lambda (Stateless, frequent deploys)
│   └── prod/
│       ├── 01-network/
│       ├── 02-data/
│       └── 03-app/
└── pipelines/               # CI/CD Configuration
```

### 2. Terraform S3 Backend Configuration (Best Practice)
確保狀態檔安全且支援鎖定的標準設定。

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state-prod"
    key            = "network/terraform.tfstate" # Unique key per layer
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock" # For locking
  }
}
```

### 3. AWS CDK: Policy as Code with Aspects
使用 CDK 的 Aspects 機制，強制檢查所有 S3 Bucket 是否開啟加密（在生成 CloudFormation 之前就會失敗）。

```typescript
// EnforceEncryption.ts
import { IAspect, CfnResource } from 'aws-cdk-lib';
import { CfnBucket } from 'aws-cdk-lib/aws-s3';
import { IConstruct } from 'constructs';

export class EnforceS3Encryption implements IAspect {
  public visit(node: IConstruct): void {
    if (node instanceof CfnBucket) {
      if (!node.bucketEncryption) {
        throw new Error(`S3 Bucket ${node.logicalId} must have encryption enabled!`);
      }
    }
  }
}

// In your Stack entry point
const app = new cdk.App();
const stack = new MyStack(app, 'MyStack');
cdk.Aspects.of(app).add(new EnforceS3Encryption());
```

### 4. GitHub Actions Workflow Snippet (The Plan Step)
自動化 PR 檢查流程。

```yaml
name: Terraform Plan
on: [pull_request]

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Init
        run: terraform init
        
      - name: Terraform Format Check
        run: terraform fmt -check
        
      - name: Security Scan (tfsec)
        uses: aquasecurity/tfsec-action@v1.0.0
        
      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color
        continue-on-error: true
        
      - name: Update PR
        uses: actions/github-script@v6
        with:
          script: |
            // Script to post plan output to PR comments
            // Allows team to review infrastructure changes without leaving GitHub
```