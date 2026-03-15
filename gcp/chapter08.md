# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，手動點擊 GCP Console 進行資源配置（ClickOps）是不可接受的，因為它無法擴展、無法追溯且容易出錯。本章將帶你從單純的腳本撰寫，進階到企業級的 **Infrastructure as Code (IaC)** 與 **GitOps** 實踐。我們將重點放在如何使用 Terraform 管理 GCP 資源狀態，並結合 Cloud Build 與 Artifact Registry 建立自動化流水線。

In a Senior Engineer's career, manually configuring resources via the GCP Console (ClickOps) is unacceptable because it is unscalable, untraceable, and error-prone. This chapter takes you from simple scripting to enterprise-grade **Infrastructure as Code (IaC)** and **GitOps** practices. We will focus on managing GCP resource states with Terraform and building automated pipelines using Cloud Build and Artifact Registry.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計企業級 IaC 架構**：理解如何使用 Terraform Remote State (GCS Backend) 與 State Locking 來管理多人協作的基礎設施。
    **Design Enterprise IaC Architecture**: Understand how to use Terraform Remote State (GCS Backend) and State Locking to manage infrastructure in a collaborative environment.
2.  **實作 GitOps 流程**：使用 Cloud Build 建立 CI/CD pipeline，自動化 Docker Image 的構建（推送到 Artifact Registry）與基礎設施的變更（Terraform Apply）。
    **Implement GitOps Workflows**: Create CI/CD pipelines using Cloud Build to automate Docker Image builds (pushing to Artifact Registry) and infrastructure changes (Terraform Apply).
3.  **處理敏感資料與安全性**：在自動化流程中正確整合 Secret Manager，避免將憑證硬編碼（Hard-coding）在程式碼中。
    **Handle Secrets and Security**: Correctly integrate Secret Manager within automation workflows to avoid hard-coding credentials in the codebase.
4.  **解決狀態漂移（Drift）**：識別並修復實際雲端資源與 Terraform State 不一致的問題。
    **Resolve State Drift**: Identify and remediate inconsistencies between actual cloud resources and the Terraform State.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 宣告式 vs. 命令式 (Declarative vs. Imperative)

Terraform 採用的是**宣告式（Declarative）**模型。你不需要告訴 GCP 「如何」建立一台 VM（例如：先分配 IP，再建立磁碟，最後啟動實例），而是定義「我想要什麼」（例如：一台具有特定 IP 和磁碟的 VM）。Terraform 引擎負責計算從「當前狀態」到「期望狀態」所需的 API 呼叫路徑。

Terraform uses a **Declarative** model. You don't tell GCP "how" to create a VM (e.g., allocate IP first, then create disk, finally start instance); instead, you define "what you want" (e.g., a VM with a specific IP and disk). The Terraform engine calculates the necessary API calls to get from the "current state" to the "desired state".

這與傳統的 Shell Script 或 Ansible（在某些模式下）不同，後者通常是命令式的。
This differs from traditional Shell Scripts or Ansible (in some modes), which are often imperative.

## 2.2 狀態檔作為唯一真理來源 (State File as the Single Source of Truth)

**Terraform State (`terraform.tfstate`)** 是 IaC 的心臟。它映射了你的 `.tf` 設定檔與真實世界 GCP 資源 ID 的對應關係。
**Terraform State (`terraform.tfstate`)** is the heart of IaC. It maps your `.tf` configuration files to real-world GCP resource IDs.

*   **Mental Model**: 想像 State File 是一個「庫存清單」。如果清單上沒有這個資源，Terraform 就認為它不歸自己管；如果清單上有但雲端上沒有，Terraform 就會嘗試重建它。
    **Mental Model**: Imagine the State File as an "inventory list". If a resource isn't on the list, Terraform assumes it doesn't manage it; if it's on the list but missing in the cloud, Terraform tries to recreate it.

## 2.3 不可變基礎設施 (Immutable Infrastructure)

在雲端原生環境中，我們傾向於**不可變基礎設施**。當需要更新應用程式版本或 OS patch 時，我們不是 SSH 進去更新，而是構建一個新的 Container Image 或 VM Image，替換掉舊的資源。Artifact Registry 在此扮演了「可信任構建產物倉庫」的角色。

In cloud-native environments, we lean towards **Immutable Infrastructure**. When updating application versions or OS patches, we don't SSH in to update; instead, we build a new Container Image or VM Image and replace the old resources. Artifact Registry plays the role of a "trusted artifact repository" here.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，IaC 不僅僅是為了「省時間」，更是為了**可審計性（Auditability）**與**災難復原（Disaster Recovery）**。

In large-scale distributed systems, IaC is not just about "saving time"; it's about **Auditability** and **Disaster Recovery**.

## 3.1 架構角色 (Architectural Roles)

*   **Source of Truth (Git)**: 所有的基礎設施變更都必須透過 Pull Request (PR) 發生。
    **Source of Truth (Git)**: All infrastructure changes must occur via Pull Requests (PR).
*   **Orchestrator (Cloud Build)**: 這是你的 CI/CD 引擎。它是 Serverless 的，這意味著你不需要像維護 Jenkins Master 那樣維護它。它負責執行 `terraform plan` 和 `terraform apply`。
    **Orchestrator (Cloud Build)**: This is your CI/CD engine. It is serverless, meaning you don't need to maintain it like a Jenkins Master. It is responsible for executing `terraform plan` and `terraform apply`.
*   **Artifact Store (Artifact Registry)**: 存放 Docker Images 或 Helm Charts。Cloud Build 構建完成後推送到這裡，Cloud Run 或 GKE 再從這裡拉取。
    **Artifact Store (Artifact Registry)**: Stores Docker Images or Helm Charts. Cloud Build pushes here after building, and Cloud Run or GKE pulls from here.
*   **State Backend (GCS Bucket)**: 存放 Terraform State。必須啟用 **Versioning**（防止狀態損壞）和 **Encryption**（保護敏感資訊）。
    **State Backend (GCS Bucket)**: Stores Terraform State. Must enable **Versioning** (to prevent corruption) and **Encryption** (to protect secrets).

## 3.2 安全性考量 (Security Considerations)

在設計時，資深工程師會特別關注 **Service Account (SA)** 的權限最小化。
In design, a Senior Engineer focuses heavily on **Service Account (SA)** least privilege.

*   **Cloud Build SA**: 預設的 Cloud Build SA 權限很大。最佳實踐是為 Cloud Build 創建自定義 SA，僅賦予其部署特定資源（如 Cloud Run Admin, Storage Admin）的權限。
    **Cloud Build SA**: The default Cloud Build SA has broad permissions. Best practice is to create a custom SA for Cloud Build, granting it only the permissions needed to deploy specific resources (e.g., Cloud Run Admin, Storage Admin).
*   **Separation of Duties**: CI 階段（PR check）只執行 `terraform plan`（Read-only），只有在 Merge 到 main branch 後的 CD 階段才執行 `terraform apply`。
    **Separation of Duties**: The CI stage (PR check) only executes `terraform plan` (Read-only), and `terraform apply` is executed only in the CD stage after merging to the main branch.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將演示一個典型的 GitOps 流程：**使用 Cloud Build 自動化部署 Cloud Run 服務，並透過 Terraform 管理該服務的定義。**

We will demonstrate a typical GitOps flow: **Using Cloud Build to automate the deployment of a Cloud Run service, with the service definition managed via Terraform.**

### 步驟 1: Terraform 設定 (Terraform Setup)

首先，定義 Backend 與 Provider。我們使用 GCS 作為 Backend 以支援鎖定（Locking）與共享狀態。

First, define the Backend and Provider. We use GCS as the Backend to support Locking and shared state.

```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket  = "my-company-tf-state-prod"
    prefix  = "services/payment-service"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# main.tf
resource "google_cloud_run_service" "default" {
  name     = "payment-service"
  location = "us-central1"

  template {
    spec {
      containers {
        # 注意：這裡使用變數，因為 Image Tag 每次構建都會變
        # Note: Using a variable here because the Image Tag changes with every build
        image = var.container_image
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

variable "container_image" {
  description = "The docker image to deploy"
  type        = string
}
```

### 步驟 2: Cloud Build 設定 (Cloud Build Configuration)

接著，編寫 `cloudbuild.yaml`。這個流程包含兩個主要部分：構建應用程式 Image，以及更新基礎設施。

Next, write `cloudbuild.yaml`. This process consists of two main parts: building the application Image and updating the infrastructure.

```yaml
# cloudbuild.yaml
steps:
  # 1. Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/payment-service:$SHORT_SHA', '.']

  # 2. Push the image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/payment-service:$SHORT_SHA']

  # 3. Terraform Init
  - name: 'hashicorp/terraform:light'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        terraform init

  # 4. Terraform Plan (Optional but recommended for logs)
  - name: 'hashicorp/terraform:light'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        terraform plan -var="container_image=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/payment-service:$SHORT_SHA" -out=tfplan

  # 5. Terraform Apply
  - name: 'hashicorp/terraform:light'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        terraform apply -auto-approve tfplan

options:
  logging: CLOUD_LOGGING_ONLY
```

### 分析與權衡 (Analysis & Trade-offs)

*   **為何將 Image Tag 傳遞給 Terraform？**
    這確保了基礎設施狀態（Terraform State）準確記錄了當前運行的軟體版本。如果僅使用 `gcloud run deploy` 命令式部署，Terraform State 會與實際運行的 Image 脫節（Drift），下一次 `terraform apply` 可能會意外將版本回滾。
    **Why pass the Image Tag to Terraform?**
    This ensures the infrastructure state (Terraform State) accurately records the currently running software version. If you only use the imperative `gcloud run deploy`, the Terraform State will drift from the actual running image, and the next `terraform apply` might accidentally roll back the version.

*   **複雜度 (Complexity)**:
    這種方法比單純的 `gcloud run deploy` 複雜，因為它引入了 Terraform 狀態鎖定和變數傳遞。但在多人協作和稽核要求高的環境下，這是必要的。
    **Complexity**:
    This approach is more complex than a simple `gcloud run deploy` because it introduces Terraform state locking and variable passing. However, in environments with multiple collaborators and high audit requirements, this is necessary.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 單體狀態檔 (Monolithic State File)

*   **錯誤 (Pitfall)**: 將所有資源（網路、資料庫、應用程式）放在同一個 `main.tf` 和同一個 state file 中。
    **Pitfall**: Putting all resources (networking, database, applications) into a single `main.tf` and a single state file.
*   **後果 (Consequence)**: `terraform plan` 速度極慢；爆炸半徑（Blast Radius）太大，修改一個防火牆規則可能意外破壞資料庫。
    **Consequence**: `terraform plan` becomes extremely slow; the Blast Radius is too large, where modifying a firewall rule might accidentally destroy a database.
*   **修正 (Fix)**: 使用**分層架構（Layered Architecture）**。將基礎設施分為 `foundation` (VPC, IAM), `data` (Cloud SQL, GCS), `app` (Cloud Run, GKE)。每層有獨立的 State file。
    **Fix**: Use a **Layered Architecture**. Split infrastructure into `foundation` (VPC, IAM), `data` (Cloud SQL, GCS), and `app` (Cloud Run, GKE). Each layer has its own State file.

## 5.2 忽略 `.gitignore` 與敏感資料 (Ignoring .gitignore & Secrets)

*   **錯誤 (Pitfall)**: 將 `terraform.tfstate` 或含有 Service Account Key 的 `.json` 檔案 commit 到 Git。
    **Pitfall**: Committing `terraform.tfstate` or `.json` files containing Service Account Keys to Git.
*   **後果 (Consequence)**: 嚴重的安全漏洞。一旦 Key 洩漏，攻擊者可完全控制你的 GCP 專案。
    **Consequence**: Severe security breach. Once the Key is leaked, attackers can take full control of your GCP project.
*   **修正 (Fix)**: 嚴格配置 `.gitignore`。使用 GCP **Secret Manager** 儲存敏感變數，並在 Terraform 中透過 `data source` 讀取，或在 Cloud Build 中作為環境變數注入。
    **Fix**: Strictly configure `.gitignore`. Use GCP **Secret Manager** to store sensitive variables and read them via `data source` in Terraform, or inject them as environment variables in Cloud Build.

## 5.3 混合使用 ClickOps 與 IaC (Mixing ClickOps and IaC)

*   **錯誤 (Pitfall)**: 工程師為了「快速修復」，直接在 GCP Console 修改 Cloud Run 的記憶體設定，而沒有更新 Terraform code。
    **Pitfall**: Engineers modify Cloud Run memory settings directly in the GCP Console for a "quick fix" without updating the Terraform code.
*   **後果 (Consequence)**: 下次 Pipeline 執行時，Terraform 會檢測到 Drift 並強制將設定改回舊值，導致「修復」失效甚至服務中斷。
    **Consequence**: The next time the Pipeline runs, Terraform will detect the Drift and force the settings back to the old values, causing the "fix" to be lost or even service interruption.
*   **修正 (Fix)**: 嚴格遵守 GitOps 流程。如果必須緊急手動修改，事後必須立即將變更回填（Backport）到 Terraform code。
    **Fix**: Strictly adhere to the GitOps process. If an emergency manual change is necessary, the change must be immediately backported to the Terraform code afterwards.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

作為面試官或被面試者，以下問題能展現你對 GCP 自動化的深度理解：

As an interviewer or candidate, the following questions demonstrate your deep understanding of GCP automation:

### Q1: 如何處理 Terraform State 的並發寫入問題？
**How do you handle concurrent writes to Terraform State?**

*   **高分回答要點 (Key Points)**:
    *   解釋 Local State 與 Remote State 的區別。
    *   提到 **GCS Backend** 原生支援 State Locking。
    *   說明當兩人同時執行 `terraform apply` 時，GCS 會鎖定 state file，第二個人會收到 Error 訊息，防止狀態損壞。
    *   Explain the difference between Local State and Remote State.
    *   Mention that **GCS Backend** natively supports State Locking.
    *   Explain that when two people run `terraform apply` simultaneously, GCS locks the state file, and the second person receives an error, preventing corruption.

### Q2: 你如何在 CI/CD Pipeline 中安全地管理資料庫密碼？
**How do you securely manage database passwords in a CI/CD Pipeline?**

*   **高分回答要點 (Key Points)**:
    *   絕對不將密碼明文寫在 Terraform code 中。
    *   使用 **Secret Manager** 存儲密碼。
    *   在 Terraform 中使用 `google_secret_manager_secret_version` data source 動態獲取密碼。
    *   或者，讓 Terraform 創建隨機密碼並存入 Secret Manager，應用程式啟動時再去讀取（解耦）。
    *   Never write passwords in plain text in Terraform code.
    *   Use **Secret Manager** to store passwords.
    *   Use the `google_secret_manager_secret_version` data source in Terraform to dynamically retrieve passwords.
    *   Alternatively, let Terraform create a random password and store it in Secret Manager, which the application reads upon startup (decoupling).

### Q3: 如果 `terraform apply` 在一半失敗了，你會怎麼做？
**What do you do if `terraform apply` fails halfway?**

*   **高分回答要點 (Key Points)**:
    *   不要驚慌，Terraform 會將已完成的部分寫入 State (Partial State)。
    *   閱讀錯誤 Log，修復 `.tf` 檔案中的問題。
    *   再次執行 `terraform plan` 查看剩餘的變更。
    *   如果資源陷入 Tainted 狀態或無法透過 Terraform 修復，可能需要 `terraform import` 或手動清理殘留資源（作為最後手段）。
    *   Don't panic; Terraform writes completed parts to the State (Partial State).
    *   Read the error logs and fix the issues in the `.tf` files.
    *   Run `terraform plan` again to see remaining changes.
    *   If resources are in a Tainted state or unfixable via Terraform, `terraform import` or manual cleanup of residual resources might be needed (as a last resort).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **IaC is Mandatory**: 在 GCP 上，Terraform 是管理資源的標準，GCS Backend 是存放 State 的標準。
2.  **GitOps Flow**: Code -> Git -> Cloud Build -> Terraform -> GCP。
3.  **Artifact Registry**: 是現代 GCP 專案中存放 Docker Image 的地方（取代了舊的 Container Registry）。
4.  **State Management**: 妥善規劃 State file 的分割（分層管理），避免單體地獄。
5.  **Security**: 使用 Secret Manager，並為 Cloud Build 配置最小權限的 Service Account。

### 後續延伸 (Next Steps)

*   **Advanced Networking**: 學習如何使用 Terraform 配置 Shared VPC 和 Private Service Access（下一章可能涉及）。
*   **Observability as Code**: 嘗試用 Terraform 建立 Cloud Monitoring Dashboards 和 Alert Policies，將監控也納入版本控制。
*   **Terraform Modules**: 學習編寫可重用的 Modules，讓團隊其他成員能快速建立符合公司規範的資源。