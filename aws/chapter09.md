# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，手動在 AWS Console 點擊資源（ClickOps）是不可接受的風險。基礎設施即程式碼（IaC）不僅是自動化腳本，更是系統架構的「藍圖」與「合約」。本章將超越基礎語法，深入探討如何在大規模生產環境中管理 IaC 的生命週期。

In the career of a Senior Software Engineer, manually provisioning resources via the AWS Console (ClickOps) is an unacceptable risk. Infrastructure as Code (IaC) is not merely automation scripting; it serves as the "blueprint" and "contract" of your system architecture. This chapter moves beyond basic syntax to explore how to manage the IaC lifecycle in large-scale production environments.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **評估與選擇工具 (Evaluate & Select Tools)**：深入理解 CloudFormation 與 Terraform 的架構差異，並根據團隊需求（如 State 管理、供應商鎖定風險）做出技術決策。
    Deeply understand the architectural differences between CloudFormation and Terraform, and make technical decisions based on team needs (e.g., state management, vendor lock-in risks).
2.  **設計模組化架構 (Design Modular Architecture)**：實作模組化（Modularity）與分層架構（Layering），以縮小爆炸半徑（Blast Radius）並提升程式碼重用性。
    Implement modularity and layered architecture to reduce the blast radius and improve code reusability.
3.  **掌握狀態管理 (Master State Management)**：解決多人協作時的 State Locking、Remote State 安全性以及 Drift Detection（配置漂移偵測）。
    Solve issues related to State Locking, Remote State security, and Drift Detection during team collaboration.
4.  **實踐不可變基礎設施 (Practice Immutable Infrastructure)**：結合 Packer 與 IaC 工具，實現從 AMI 建置到 Blue/Green 部署的完整自動化流程。
    Combine Packer with IaC tools to achieve a complete automation workflow from AMI building to Blue/Green deployment.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 宣告式 vs. 命令式 (Declarative vs. Imperative)

**心智模型**：想像你在餐廳點餐。
**命令式（Imperative）**是走進廚房告訴廚師：「先切洋蔥，再熱鍋，加油，炒洋蔥...」。
**宣告式（Declarative）**是看著菜單說：「我要一份牛排，五分熟」。你只定義「最終狀態（Desired State）」，而不需關心實作步驟。

**Mental Model**: Imagine ordering food at a restaurant.
**Imperative** is walking into the kitchen and telling the chef: "First chop the onions, then heat the pan, add oil, sauté the onions...".
**Declarative** is looking at the menu and saying: "I want a steak, medium-rare." You define the "Desired State" without worrying about the implementation steps.

AWS CloudFormation 與 Terraform 主要都是**宣告式**工具。這意味著你的程式碼描述的是基礎設施的**最終樣貌**，而非建立過程。

AWS CloudFormation and Terraform are primarily **declarative** tools. This means your code describes what the infrastructure should **look like** at the end, not the process of building it.

## 2.2 狀態檔 (The State File)

IaC 工具必須知道「現實世界（AWS 實際資源）」與「程式碼（你的 .tf 或 .yaml 檔）」之間的對應關係。這就是 **State** 的作用。

IaC tools must understand the mapping between the "Real World" (actual AWS resources) and the "Code" (your `.tf` or `.yaml` files). This is the role of **State**.

*   **Terraform**: 使用 `terraform.tfstate` 檔案（通常存放在 S3 + DynamoDB Lock）。它是 Terraform 認知的世界觀。如果 State 檔遺失或損壞，Terraform 會認為資源不存在，可能會嘗試重建（導致災難）。
    Uses a `terraform.tfstate` file (usually stored in S3 + DynamoDB Lock). It is Terraform's view of the world. If the State file is lost or corrupted, Terraform assumes resources don't exist and might try to recreate them (leading to disaster).
*   **CloudFormation**: State 由 AWS 託管（Managed Service）。你不需要維護狀態檔，AWS 會追蹤 Stack 的狀態。這降低了維運負擔，但也減少了對狀態操作的靈活性。
    State is managed by AWS. You don't need to maintain a state file; AWS tracks the Stack's status. This reduces operational burden but also limits flexibility in manipulating the state.

## 2.3 不可變基礎設施 (Immutable Infrastructure)

**定義**：一旦伺服器被部署，就不再對其進行修改（SSH 進去 patch、更新 config）。若需要變更，則是建立新的伺服器來替換舊的。

**Definition**: Once a server is deployed, it is never modified (no SSH patching, no config updates). If a change is needed, a new server is built to replace the old one.

*   **Pets vs. Cattle**:
    *   **Pets (Mutable)**: 給伺服器取名（如 `db-primary`），生病了（故障）你會修復它。
    *   **Cattle (Immutable)**: 給伺服器編號（如 `web-001`），生病了你直接終止它並啟動一台新的。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在資深工程師的系統設計中，IaC 不僅是部署工具，更是**可靠性（Reliability）**與**安全性（Security）**的基石。

In a Senior Engineer's system design, IaC is not just a deployment tool but the cornerstone of **Reliability** and **Security**.

## 3.1 分層架構設計 (Layered Architecture)

不要將所有資源寫在同一個 Stack 或 Terraform Workspace 中。這會導致「爆炸半徑」過大，且 `plan/apply` 速度極慢。

Do not put all resources into a single Stack or Terraform Workspace. This leads to a massive "Blast Radius" and extremely slow `plan/apply` times.

**建議的分層策略 (Recommended Layering Strategy)**:

1.  **Foundation Layer (很少變更)**: VPC, Subnets, Route Tables, VPN/Direct Connect.
2.  **Data Layer (極度敏感)**: RDS, ElastiCache, S3 Buckets, KMS Keys. (Stateful resources need extra protection).
3.  **App Layer (頻繁變更)**: EC2 Auto Scaling Groups, ECS Services, Lambda, Load Balancers.

這種設計允許你頻繁更新 App Layer，而不會意外觸碰到 Data Layer 或 Network Layer。

This design allows you to frequently update the App Layer without accidentally impacting the Data Layer or Network Layer.

## 3.2 GitOps 與 CI/CD 整合 (GitOps & CI/CD Integration)

在 Production 環境中，**嚴禁**從工程師的筆電執行 `terraform apply`。

In a Production environment, running `terraform apply` from an engineer's laptop is **strictly prohibited**.

*   **流程 (Workflow)**:
    1.  工程師提交 PR (Pull Request)。
    2.  CI Pipeline (如 GitHub Actions/Jenkins) 執行 `terraform plan` 並將結果貼回 PR comment。
    3.  資深工程師 Code Review 並 Merge PR。
    4.  CD Pipeline 在 Main branch 觸發，執行 `terraform apply`。
*   **優勢 (Benefits)**:
    *   **Audit Trail**: 所有的變更都有 Git commit 紀錄。
    *   **Security**: 只有 CI/CD Server 擁有 AWS Admin 權限，工程師個人帳號只需 Read-only 權限。

---

# 4. 逐步示例 (Walkthrough / Example)

我們將以 **Terraform** 為例，展示如何從一個簡單的設定演進到具備 Remote State 與 Locking 的生產級配置。

We will use **Terraform** as an example to demonstrate the evolution from a simple setup to a production-grade configuration with Remote State and Locking.

## 4.1 階段一：Naive Approach (Local State)

剛開始接觸時，你可能會寫一個 `main.tf` 並直接執行。

When starting out, you might write a single `main.tf` and run it directly.

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-app-logs-dev"
}
```

*   **問題 (Problem)**: `terraform.tfstate` 產生在你的本機。如果你的電腦壞了，狀態就丟了。如果你同事也要修改，你們無法同步狀態，會互相覆蓋。
    *   **Issue**: `terraform.tfstate` is generated locally. If your machine crashes, the state is lost. If a colleague needs to modify it, you cannot sync the state, leading to overwrites.

## 4.2 階段二：Production Ready (Remote State + Locking)

資深工程師會首先配置 Backend。這通常包含一個 S3 Bucket 存狀態，和一個 DynamoDB Table 用於鎖定（防止兩個人同時執行 apply）。

A Senior Engineer sets up the Backend first. This typically involves an S3 Bucket for storing state and a DynamoDB Table for locking (preventing two people from running apply simultaneously).

```hcl
# backend.tf
terraform {
  required_version = ">= 1.0.0"

  backend "s3" {
    # 替換為你的 Bucket 名稱
    bucket         = "my-company-terraform-state"
    # State 檔案的路徑 key，這裡體現了分層設計
    key            = "networking/vpc/terraform.tfstate"
    region         = "us-east-1"
    
    # 啟用加密
    encrypt        = true
    
    # 使用 DynamoDB 進行鎖定 (Locking)
    dynamodb_table = "terraform-state-lock"
  }
}
```

**思考步驟 (Thinking Process)**:

1.  **為何需要 DynamoDB?** 當 CI/CD 正在執行 `apply` 時，DynamoDB 會寫入一個 Lock ID。若另一個工程師嘗試執行，Terraform 會檢查到 Lock 存在並報錯，防止 Race Condition 導致資源損壞。
    **Why DynamoDB?** When CI/CD runs `apply`, a Lock ID is written to DynamoDB. If another engineer tries to run it, Terraform detects the lock and errors out, preventing Race Conditions that corrupt resources.
2.  **Key 的命名**: `networking/vpc/...` 顯示我們將 VPC 獨立管理，與 App 層分開。
    **Key Naming**: `networking/vpc/...` indicates that we are managing the VPC independently, separate from the App layer.

## 4.3 階段三：模組化 (Modularity)

不要重複造輪子。將常用的模式（如「一個標準的 Microservice ECS Service」）封裝成 Module。

Don't reinvent the wheel. Encapsulate common patterns (e.g., "a standard Microservice ECS Service") into Modules.

```hcl
# main.tf (Using a module)
module "payment_service" {
  source = "git::https://github.com/my-org/terraform-modules//ecs-service?ref=v1.2.0"

  service_name   = "payment-api"
  instance_count = 3
  environment    = "production"
  vpc_id         = data.terraform_remote_state.vpc.outputs.vpc_id
}
```

*   **Best Practice**: 使用 `ref=v1.2.0` 指定版本。這確保了 Infrastructure 的變更是可預測的，不會因為 Module 的主線更新而意外壞掉。
    Use `ref=v1.2.0` to pin the version. This ensures infrastructure changes are predictable and won't break unexpectedly due to updates in the module's main branch.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 混合手動操作與 IaC (Drift / ClickOps)

**錯誤描述**：使用 Terraform 建立了 Security Group，但因為緊急修復（Hotfix），工程師直接在 AWS Console 手動開放了 Port 22。

**Error Description**: You created a Security Group with Terraform, but due to an urgent hotfix, an engineer manually opened Port 22 in the AWS Console.

*   **後果**：下次執行 `terraform apply` 時，Terraform 可能會把 Port 22 關掉（造成服務中斷），或者因為狀態不一致導致報錯。
    **Consequence**: The next time `terraform apply` runs, Terraform might close Port 22 (causing an outage) or error out due to state inconsistency.
*   **解法**：嚴格禁止手動變更。若發生緊急狀況必須手動，事後必須立即 `import` 狀態或更新程式碼以反映變更。使用 AWS Config 或 Drift Detection 工具監控。
    **Solution**: Strictly forbid manual changes. If a manual hotfix is unavoidable, immediately `import` the state or update the code to reflect the change afterwards. Use AWS Config or Drift Detection tools to monitor.

## 5.2 敏感資訊硬編碼 (Hardcoding Secrets)

**錯誤描述**：在 `.tf` 檔案中直接寫 `password = "SuperSecret123"`。

**Error Description**: Writing `password = "SuperSecret123"` directly in `.tf` files.

*   **後果**：密碼進入 Git 歷史紀錄，永久洩漏。即使是 Private Repo 也不安全。
    **Consequence**: The password enters Git history and is permanently leaked. Even Private Repos are not secure.
*   **解法**：
    1.  使用 **AWS Secrets Manager** 或 **SSM Parameter Store**。
    2.  在 Terraform 中使用 `data` source 讀取，或在 Resource 中引用 Secret ARN。
    **Solution**:
    1.  Use **AWS Secrets Manager** or **SSM Parameter Store**.
    2.  Use a `data` source in Terraform to read it, or reference the Secret ARN in the Resource.

## 5.3 忽略資源刪除保護 (Ignoring Deletion Protection)

**錯誤描述**：對 RDS 或 S3 Bucket 執行 `terraform destroy` 或刪除 Stack，導致生產數據遺失。

**Error Description**: Running `terraform destroy` or deleting a Stack on RDS or S3 Buckets, resulting in production data loss.

*   **解法**：對 Stateful 資源（DB, S3）啟用 `deletion_protection = true` (Terraform) 或 `DeletionPolicy: Retain` (CloudFormation)。
    **Solution**: Enable `deletion_protection = true` (Terraform) or `DeletionPolicy: Retain` (CloudFormation) for Stateful resources (DB, S3).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: Terraform 與 CloudFormation 的主要區別是什麼？你會如何選擇？
**What are the main differences between Terraform and CloudFormation? How would you choose?**

*   **高分回答要點 (Key Points)**:
    *   **Scope**: Terraform 是 Multi-cloud（支援 AWS, GCP, Azure, Datadog 等）；CloudFormation 是 AWS Native。
    *   **State Management**: Terraform 需要自行管理 State file（有風險也有彈性）；CloudFormation 由 AWS 託管 State。
    *   **Rollback**: CloudFormation 預設失敗會自動 Rollback（Auto-rollback）；Terraform 失敗時會停在半途（Partial state），需要人工介入修復。這是一個關鍵的維運差異。
    *   **選擇策略**: 若公司是全 AWS 且重視原生支援（如 Service Catalog），選 CFN/CDK。若追求多雲策略或更強的模組化語法，選 Terraform。

## Q2: 如何處理現有的、未被 IaC 管理的基礎設施 (Legacy Infrastructure)？
**How do you handle existing infrastructure that is not managed by IaC (Legacy Infrastructure)?**

*   **高分回答要點 (Key Points)**:
    *   不能直接覆蓋。
    *   **Terraform**: 使用 `terraform import` 指令將現有資源 ID 導入 State，然後編寫對應的 `.tf` 程式碼直到 `terraform plan` 顯示 "No changes"。
    *   **CloudFormation**: 使用 "Resource Import" 功能。
    *   強調這是一個漸進過程，優先處理高風險/高變更頻率的資源。

## Q3: 在 CI/CD Pipeline 中，如何安全地部署 IaC 變更？
**How do you safely deploy IaC changes in a CI/CD Pipeline?**

*   **高分回答要點 (Key Points)**:
    *   **Linting/Validation**: 先跑 `terraform validate` 或 `cfn-lint`。
    *   **Plan Review**: 在 Pull Request 中展示 `terraform plan` 的輸出，讓人審核變更內容（特別注意 Deletions）。
    *   **Least Privilege**: CI/CD 的 IAM Role 權限應最小化。
    *   **Policy as Code**: 整合 OPA (Open Policy Agent) 或 Sentinel，自動阻擋違規配置（例如：禁止建立公開的 S3 Bucket）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 小結 (Summary)

1.  **State is King**: 理解 State 檔案的重要性與風險，務必使用 Remote State + Locking。
2.  **Declarative over Imperative**: 專注於描述「最終狀態」，而非腳本步驟。
3.  **Blast Radius**: 透過分層（Layering）與模組化（Modularity）設計，將故障隔離在最小範圍。
4.  **Immutable Infrastructure**: 結合 Packer 與 IaC，避免原地修補伺服器，改採替換策略。
5.  **No ClickOps**: 所有生產環境變更必須透過 Code + CI/CD 進行。

## 後續延伸 (Next Steps)

*   **AWS CDK (Cloud Development Kit)**: 如果你喜歡用 Python/TypeScript 寫邏輯而非 YAML/HCL，這是 CloudFormation 的現代化封裝。
*   **Policy as Code**: 學習使用 OPA (Open Policy Agent) 或 Checkov 來自動化掃描 IaC 的安全性漏洞。
*   **Observability**: 下一章將探討如何監控這些基礎設施（CloudWatch, X-Ray, Prometheus）。