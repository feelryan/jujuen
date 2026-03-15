# 1. 前言與學習目標 (Introduction & Learning Objectives)

在現代 DevOps 實踐中，基礎設施即程式碼 (Infrastructure as Code, IaC) 已是標準配備。然而，資深工程師的價值不僅在於「會寫 Terraform」，更在於如何設計一個安全、可協作且自動化的 IaC 管理流程。GitLab 提供了內建的 Terraform State 管理功能與強大的 CI/CD 整合能力，使得基礎設施變更可以像應用程式代碼一樣經過 Code Review、測試與部署。

In modern DevOps practices, Infrastructure as Code (IaC) is a standard requirement. However, the value of a Senior Engineer lies not just in "knowing how to write Terraform," but in designing a secure, collaborative, and automated IaC management workflow. GitLab provides built-in Terraform State management and powerful CI/CD integration, allowing infrastructure changes to undergo Code Review, testing, and deployment just like application code.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作 GitLab Managed Terraform State**：不再依賴 S3 bucket 或本地檔案，利用 GitLab 內建後端安全地儲存與鎖定 State。
    **Implement GitLab Managed Terraform State**: Stop relying on ad-hoc S3 buckets or local files; use GitLab's built-in backend to securely store and lock state.
2.  **設計 IaC CI/CD 流水線**：建立包含 `plan`、`apply` 以及自動化測試（如 `tflint` 或 Policy Check）的完整流水線。
    **Design IaC CI/CD Pipelines**: Build comprehensive pipelines that include `plan`, `apply`, and automated testing (such as `tflint` or Policy Checks).
3.  **整合配置管理工具**：理解如何在 Terraform 部署基礎設施後，透過 GitLab CI 觸發 Ansible 或 Helm 進行應用層配置。
    **Integrate Configuration Management Tools**: Understand how to trigger Ansible or Helm via GitLab CI for application-layer configuration after Terraform provisions the infrastructure.
4.  **強化 IaC 安全性**：利用 GitLab OIDC 與 Cloud Provider 進行無金鑰驗證 (Keyless Authentication)，並管理敏感變數。
    **Harden IaC Security**: Leverage GitLab OIDC with Cloud Providers for Keyless Authentication and manage sensitive variables effectively.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 GitLab 作為 IaC 的控制平面 (GitLab as the IaC Control Plane)

將 GitLab 視為基礎設施的「控制平面 (Control Plane)」。傳統上，我們可能在工程師的筆電上執行 `terraform apply`，這導致了 State 不同步、權限過大且缺乏稽核紀錄的問題。在 GitLab 的模型中，GitLab CI Runner 是唯一被授權變更生產環境基礎設施的實體 (Entity)。

Think of GitLab as the "Control Plane" for your infrastructure. Traditionally, we might run `terraform apply` on an engineer's laptop, leading to desynchronized state, excessive permissions, and a lack of audit trails. In the GitLab model, the GitLab CI Runner is the sole entity authorized to mutate production infrastructure.

-   **Terraform State as a Service**: GitLab 提供了一個相容於 Terraform HTTP Backend 的 API。這意味著你不需要額外維護 AWS DynamoDB 來做 State Locking，GitLab 會自動處理鎖定與版本控制。
    **Terraform State as a Service**: GitLab provides an API compatible with the Terraform HTTP Backend. This means you don't need to maintain an extra AWS DynamoDB for State Locking; GitLab handles locking and versioning automatically.
-   **MR as a Gatekeeper**: 所有的基礎設施變更都必須透過 Merge Request (MR) 發生。MR 中的 `terraform plan` 輸出是決策的依據，而 Merge 動作則是執行的觸發器。
    **MR as a Gatekeeper**: All infrastructure changes must occur via a Merge Request (MR). The `terraform plan` output in the MR serves as the basis for decision-making, while the Merge action acts as the execution trigger.

## 2.2 與鄰近概念的差異 (Comparison with Adjacent Concepts)

| Feature | GitLab Managed State | AWS S3 + DynamoDB | Local State |
| :--- | :--- | :--- | :--- |
| **Setup Effort** | Low (Built-in, zero config infra) | Medium (Need to provision bucket/table) | Zero (But dangerous) |
| **Authentication** | GitLab CI Job Token / User Token | AWS IAM Credentials | Local User Credentials |
| **Locking** | Automatic (via HTTP API) | Requires DynamoDB setup | Filesystem (Flaky) |
| **Visibility** | Integrated in GitLab UI | AWS Console | None |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構流程 (Typical Architecture Flow)

在資深工程師設計的系統中，IaC 流程通常遵循 GitOps 原則。以下是一個標準的 Production 級流程：

In systems designed by senior engineers, the IaC process typically follows GitOps principles. Here is a standard Production-grade workflow:

1.  **Feature Branch**: 工程師修改 `.tf` 檔案。
    **Feature Branch**: Engineer modifies `.tf` files.
2.  **CI Pipeline (Pre-Merge)**:
    *   `fmt` / `validate`: 語法檢查。
    *   `security scan`: 使用 `tfsec` 或 `checkov` 掃描配置漏洞。
    *   `plan`: 產生執行計畫，並將輸出 (Plan Artifact) 貼回 MR 的 Comment 中供審閱。
3.  **Code Review**: 資深人員檢查 Plan 內容，確認沒有意外的刪除或高風險變更。
    **Code Review**: Seniors review the Plan content to ensure no accidental deletions or high-risk changes.
4.  **Merge to Main**: 程式碼合併。
    **Merge to Main**: Code is merged.
5.  **CD Pipeline (Post-Merge)**:
    *   `apply`: 使用先前 `plan` 階段生成的 Artifact（或重新 Plan）進行實際部署。
    *   `post-config`: 觸發 Ansible Playbook 或 Helm Chart 部署應用程式。

## 3.2 安全性與權限隔離 (Security & Isolation)

在系統設計面試或實務中，權限管理至關重要：

In system design interviews or practice, permission management is critical:

*   **OIDC (OpenID Connect)**: 推薦使用 GitLab OIDC 與 AWS/GCP 整合。Runner 在執行 Job 時會取得一個短期的 JWT Token，向 Cloud Provider 交換臨時憑證。這樣就不需要在 GitLab CI Variables 中儲存長效的 `AWS_ACCESS_KEY_ID`。
    **OIDC (OpenID Connect)**: It is recommended to use GitLab OIDC integrated with AWS/GCP. The Runner obtains a short-lived JWT Token during Job execution and exchanges it for temporary credentials from the Cloud Provider. This eliminates the need to store long-lived `AWS_ACCESS_KEY_ID` in GitLab CI Variables.
*   **State Encryption**: 雖然 GitLab 會加密儲存 State，但在 State 中包含敏感資料（如 RDS 密碼）仍是反模式。應結合 HashiCorp Vault 或 AWS Secrets Manager。
    **State Encryption**: Although GitLab encrypts the stored State, including sensitive data (like RDS passwords) in the State remains an anti-pattern. Integrate with HashiCorp Vault or AWS Secrets Manager instead.

---

# 4. 逐步示例 (Walkthrough / Example)

本範例將展示如何設定 GitLab 作為 Terraform Backend，並建立一個自動化的 CI/CD 流水線。

This example demonstrates how to configure GitLab as a Terraform Backend and build an automated CI/CD pipeline.

## 4.1 Terraform Backend 配置 (Terraform Backend Configuration)

在你的 `main.tf` 或 `backend.tf` 中，使用 `http` backend。注意我們不需要硬編碼 URL，因為我們會在 CI 執行時透過環境變數注入。

In your `main.tf` or `backend.tf`, use the `http` backend. Note that we don't need to hardcode the URL, as we will inject it via environment variables during CI execution.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # 使用 http backend 對接 GitLab
  # Use http backend to interface with GitLab
  backend "http" {
  }
}

provider "aws" {
  region = "us-east-1"
}
```

## 4.2 GitLab CI/CD Pipeline (`.gitlab-ci.yml`)

這是一個精簡但功能完整的 IaC Pipeline 配置。

This is a concise yet fully functional IaC Pipeline configuration.

```yaml
image:
  name: hashicorp/terraform:1.6
  entrypoint: [""]

variables:
  # GitLab 內建變數，用於組建 State URL
  # GitLab built-in variables for constructing the State URL
  TF_HTTP_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production
  TF_HTTP_LOCK_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production/lock
  TF_HTTP_UNLOCK_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production/lock
  
  # 使用 CI_JOB_TOKEN 進行 State 存取驗證
  # Use CI_JOB_TOKEN for State access authentication
  TF_HTTP_USERNAME: gitlab-ci-token
  TF_HTTP_PASSWORD: ${CI_JOB_TOKEN}
  
  # 快取目錄
  # Cache directory
  TF_ROOT: ${CI_PROJECT_DIR}

cache:
  key: production-terraform
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - terraform --version
  - terraform init

stages:
  - validate
  - plan
  - apply

validate:
  stage: validate
  script:
    - terraform validate
    - terraform fmt -check

plan:
  stage: plan
  script:
    - terraform plan -out=tfplan
    # 將 plan 轉為文字檔以便人工檢閱 (Optional)
    # Convert plan to text for human review (Optional)
    - terraform show -no-color tfplan > tfplan.txt
  artifacts:
    name: plan
    paths:
      - tfplan
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'

apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual # 生產環境通常建議手動觸發
```

### 關鍵點解析 (Key Points Analysis)

1.  **Backend Authentication**: 我們利用 `CI_JOB_TOKEN` 作為密碼，這讓 GitLab Runner 自動獲得讀寫 State 的權限，無需額外管理憑證。
    **Backend Authentication**: We use `CI_JOB_TOKEN` as the password, allowing the GitLab Runner to automatically gain read/write access to the State without extra credential management.
2.  **Artifact Passing**: `plan` 階段產生的 `tfplan` 二進位檔案被傳遞給 `apply` 階段。這保證了我們 Apply 的內容嚴格等於我們 Plan（且經過 Review）的內容。
    **Artifact Passing**: The `tfplan` binary generated in the `plan` stage is passed to the `apply` stage. This ensures that what we Apply is strictly identical to what we Planned (and Reviewed).
3.  **Manual Gate**: 在 `apply` 階段設定 `when: manual` 是資深工程師常見的防護措施，特別是在 Production 環境。
    **Manual Gate**: Setting `when: manual` in the `apply` stage is a common safeguard for senior engineers, especially in Production environments.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 將 `.tfstate` 提交到 Git (Committing `.tfstate` to Git)

*   **錯誤描述**: 初學者常誤將 `.tfstate` 檔案加入版控。
    **Description**: Beginners often mistakenly add `.tfstate` files to version control.
*   **為何不好**: State 檔案包含純文字的敏感資訊（如資料庫密碼、私鑰）。一旦進入 Git 歷史紀錄，就很難徹底清除。此外，多人協作時會造成嚴重的 Merge Conflict。
    **Why it's bad**: State files contain sensitive information in plain text (e.g., DB passwords, private keys). Once in Git history, it's hard to scrub completely. Also, it causes severe Merge Conflicts during collaboration.
*   **解決方案**: 在 `.gitignore` 中排除 `*.tfstate` 和 `*.tfstate.backup`。使用 Remote Backend（如 GitLab Managed State）。
    **Solution**: Exclude `*.tfstate` and `*.tfstate.backup` in `.gitignore`. Use a Remote Backend (like GitLab Managed State).

## 5.2 忽略 State Locking (Ignoring State Locking)

*   **錯誤描述**: 使用不支援 Locking 的 Backend（如單純的 S3 但未配置 DynamoDB，或某些自製 HTTP Backend）。
    **Description**: Using a Backend that doesn't support Locking (e.g., plain S3 without DynamoDB, or some custom HTTP Backends).
*   **為何不好**: 如果兩個 CI Pipeline 同時執行（例如兩個 MR 同時合併），可能會導致 State 損壞 (Corruption)，造成基礎設施狀態不一致。
    **Why it's bad**: If two CI pipelines run simultaneously (e.g., two MRs merging at once), it can lead to State Corruption and inconsistent infrastructure.
*   **解決方案**: GitLab HTTP Backend 原生支援 Locking，務必確保 Pipeline 配置正確使用了 `TF_HTTP_LOCK_ADDRESS`。
    **Solution**: GitLab HTTP Backend supports Locking natively; ensure your pipeline configuration correctly uses `TF_HTTP_LOCK_ADDRESS`.

## 5.3 巨型單體 State (Monolithic State)

*   **錯誤描述**: 將整個公司的基礎設施（VPC, EKS, RDS, Lambda）全部寫在一個 Terraform 專案與 State 中。
    **Description**: Putting the entire company's infrastructure (VPC, EKS, RDS, Lambda) into a single Terraform project and State.
*   **為何不好**: `plan` 速度極慢；爆炸半徑 (Blast Radius) 太大，修改一個 Lambda 可能意外破壞 VPC。
    **Why it's bad**: `plan` becomes extremely slow; the Blast Radius is too large—modifying a Lambda might accidentally break the VPC.
*   **解決方案**: 拆分 State。例如：`networking`, `data-layer`, `app-layer` 分別對應不同的 GitLab State ID。
    **Solution**: Split the State. For example: `networking`, `data-layer`, `app-layer` should correspond to different GitLab State IDs.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 如何處理基礎設施的「配置漂移 (Drift)」？
**How do you handle infrastructure "Configuration Drift"?**

*   **高分回答要點**:
    *   解釋 Drift 是指實際雲端資源狀態與 Terraform State 不一致。
    *   **主動偵測**: 設定排程 Pipeline (Scheduled Pipeline)，例如每晚執行 `terraform plan`。若檢測到變更（Exit code != 0），則發送 Slack 通知或開立 Issue。
    *   **GitLab 整合**: GitLab 有 "Terraform reports" 功能，可以在 UI 上顯示變更摘要。
    *   **強制同步**: 在某些嚴格環境，可以設定排程自動執行 `terraform apply` 把配置「刷」回去（需謹慎）。

## 6.2 在 CI/CD 中，如何安全地將 Terraform 創建的資源資訊傳遞給 Ansible/Helm？
**In CI/CD, how do you securely pass resource info created by Terraform to Ansible/Helm?**

*   **高分回答要點**:
    *   **Terraform Outputs**: 使用 `output` 定義需要傳遞的值（如 DB Endpoint, Cluster IP）。
    *   **Artifacts**: 在 CI 中，將 `terraform output -json > output.json` 存為 Artifact，傳遞給下一個 Job。
    *   **Dynamic Inventory**: 對於 Ansible，使用 Dynamic Inventory 插件直接查詢雲端 API（透過 Tag），而不是依賴靜態 IP 列表，這樣更具彈性。
    *   **Secret Management**: 敏感資料不應透過 Artifact 明文傳遞，應存入 Vault 或 Cloud Secret Manager，並由 Ansible/Helm 在執行時讀取。

## 6.3 你會選擇 Monorepo 還是 Polyrepo 來管理 IaC？為什麼？
**Would you choose Monorepo or Polyrepo for IaC management? Why?**

*   **高分回答要點**:
    *   **沒有絕對答案，視規模而定**。
    *   **Monorepo 優勢**: 容易共享 Modules，統一版本控制，原子性提交（一次 Commit 修改 App 和 Infra）。適合中型團隊。
    *   **Monorepo 挑戰**: CI 變慢（需使用 `changes` 規則只跑變更部分），權限控制較複雜（需使用 `CODEOWNERS`）。
    *   **Polyrepo 優勢**: 權限隔離清楚（不同 Team 管不同 Repo），部署獨立。適合大型組織或微服務架構。
    *   **資深觀點**: 傾向於將核心基礎設施（VPC, Shared K8s）獨立為一個 Repo，而應用層基礎設施（S3 bucket, SQS）隨應用程式 Repo 放在一起 (Application-coupled IaC)。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點回顧 (Key Takeaways)

1.  **GitLab as Backend**: 利用 GitLab 內建的 HTTP Backend 來儲存 Terraform State，無需自行維護 S3/DynamoDB，並享有原生的 State Locking。
2.  **Pipeline Strategy**: 嚴格區分 `plan` (MR 階段) 與 `apply` (Main Branch 階段)，並透過 Artifacts 傳遞 Plan file 以確保執行的一致性。
3.  **Security First**: 使用 OIDC 取代長效 Key，絕不將 `.tfstate` 入庫，並對 Production Apply 設置人工審核閘門。
4.  **Automation**: IaC 不只是 Provisioning，還包含 Drift Detection 與 Policy Check (如 `tflint`, `checkov`)。

## 後續延伸 (Next Steps)

*   **進階安全性**: 研究 **GitLab Secure** 功能，將 SAST/DAST 整合進 IaC 流程（Infrastructure Scanning）。
*   **GitOps Agent**: 學習 **GitLab Agent for Kubernetes**，這是在 K8s 環境下比傳統 CI/CD Push 模式更先進的 Pull 模式部署方案。
*   **Policy as Code**: 深入研究 **Open Policy Agent (OPA)**，在 GitLab CI 中強制執行合規性政策（例如：禁止建立公開的 S3 Bucket）。