# GCP 基礎設施即程式碼 (Terraform) 最佳實踐 / IaC Best Practices with Terraform on GCP

## Mental model｜心智模型

在 GCP 上使用 Terraform，與其他雲端平台最大的不同在於 **「資源階層 (Resource Hierarchy)」** 的嚴格性。你不能只是想著「我要建立一台 VM」，你必須先思考「這台 VM 屬於哪個 Project？這個 Project 屬於哪個 Folder？」。

### 1. The Project Factory Concept (專案工廠概念)
將 GCP 的 `Project` 視為一個 **軟體產出物 (Software Artifact)**，而不僅僅是一個邏輯邊界。
- **Traditional View:** Project 是一個靜態的容器，我在裡面手動開啟 API 並放入資源。
- **Terraform View:** Project 本身就是一個 Terraform Resource。你應該編寫程式碼來「生產」Project，自動綁定 Billing Account、開啟特定的 APIs、設定基礎 IAM 權限，並將其放入正確的 Folder 中。這就是 **Project Factory** 模式。

### 2. Layered State Management (分層狀態管理)
不要試圖用一個 State file 管理整個組織。應採用 **洋蔥式 (Onion Layers)** 的依賴結構：
1.  **Bootstrap Layer:** 建立 Terraform 運行所需的 GCS Bucket 和 Service Account。
2.  **Foundation/Organization Layer:** 設定 Folder 結構、Shared VPC、組織級 IAM 政策。
3.  **Application/Project Layer:** 實際的應用程式專案、GKE Cluster、Cloud SQL 等。

### 3. Identity as Code (身分即代碼)
在 GCP 中，Terraform 的執行身分 (Service Account) 是安全性的核心。
- **Mental Shift:** 不要使用長效的 JSON Key 檔案。
- **Best Practice:** 使用 **Service Account Impersonation (身分模擬)**。開發者使用自己的 Google 帳號 (`gcloud auth login`) 獲取短效 Token，去模擬擁有權限的 Service Account 來執行 Terraform。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Project Factory Pattern (專案工廠模式)
使用 Google 官方維護的模組 `terraform-google-modules/project-factory/google`。這不僅僅是建立專案，它解決了最頭痛的依賴問題：
- 自動啟用 APIs (`google_project_service`)。
- 自動關聯 Shared VPC。
- 處理 Default Service Account 的權限移除（安全性最佳實踐）。

```hcl
module "my_app_project" {
  source  = "terraform-google-modules/project-factory/google"
  version = "~> 14.0"

  name              = "my-app-prod"
  random_project_id = true
  org_id            = var.org_id
  folder_id         = var.folder_id
  billing_account   = var.billing_account_id

  activate_apis = [
    "compute.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com"
  ]
}
```

### 2. State Management with GCS (使用 GCS 管理狀態)
GCP 原生的 GCS Backend 是最穩定的選擇。
- **Versioning:** 務必在 GCS Bucket 上開啟版本控制 (Versioning)，以防 State 損壞時可回滾。
- **State Locking:** GCS Backend 原生支援 State Locking，防止多人同時寫入。
- **Impersonation:** 在 `provider` 區塊設定 `impersonate_service_account`。

```hcl
terraform {
  backend "gcs" {
    bucket                      = "tf-state-prod-bootstrap"
    prefix                      = "terraform/state"
    impersonate_service_account = "terraform-runner@admin-project.iam.gserviceaccount.com"
  }
}
```

### 3. Handling API Dependencies (處理 API 依賴)
在 GCP，資源建立前必須啟用對應 API。Terraform 常常因為 API 尚未啟用完畢就嘗試建立資源而失敗。
- **Pattern:** 使用 `google_project_service` 資源，並確保應用程式資源 `depends_on` 這些 API 啟用資源（通常 Project Factory 模組已內建處理）。
- **Critical Setting:** 設定 `disable_on_destroy = false`。
  - *Why?* 預設情況下，`terraform destroy` 會關閉 API。這可能導致該 Project 下的資料（如 GCS Bucket 內容、BigQuery Dataset）因為 API 被關閉而變得不可存取或被意外刪除。

### 4. Google Beta Provider
GCP 的新功能通常先在 Beta API 發布。
- **Practice:** 同時定義 `google` 和 `google-beta` provider。
- 當需要使用 Beta 功能（如 GKE 的某些進階網路設定）時，明確指定 `provider = google-beta`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "JSON Key" Trap (JSON Key 陷阱)
- **Anti-pattern:** 下載 Service Account 的 `.json` 金鑰檔案，並將其路徑寫在 `GOOGLE_APPLICATION_CREDENTIALS` 或 CI/CD 變數中。
- **Risk:** 金鑰極易洩漏，且難以輪替 (Rotate)。
- **Solution:** 在本地開發使用 `gcloud auth application-default login --impersonate-service-account`；在 CI/CD (如 GitHub Actions/GitLab CI) 使用 **Workload Identity Federation**。

### 2. Monolithic State (單體狀態)
- **Anti-pattern:** 將 Networking (VPC)、K8s Cluster 和 Database 全部寫在同一個 `main.tf` 或同一個 State file 中。
- **Consequence:** `terraform plan` 速度極慢；修改一個 Firewall rule 可能意外觸發 Database 的重建；Blast Radius (爆炸半徑) 過大。
- **Solution:** 拆分 State。Networking 一個 State，GKE Cluster 一個 State，應用層資源一個 State。透過 `terraform_remote_state` 讀取輸出變數。

### 3. Hardcoding Project IDs (硬編碼專案 ID)
- **Anti-pattern:** 指定 `project = "my-company-prod"`。
- **Pitfall:** GCP Project ID 全球唯一且刪除後有一段時間無法重用。如果你需要重建環境，硬編碼會導致失敗。
- **Solution:** 讓 Terraform 產生隨機後綴 (Random Suffix)，例如 `my-company-prod-x9z2`。

### 4. Modifying "Default" Resources (修改預設資源)
- **Anti-pattern:** 嘗試 import 並修改 GCP 建立專案時自動生成的 "default" VPC 或 "default" Service Account。
- **Solution:** 刪除 default VPC，建立全新的 Custom VPC。停用或不使用 Default Service Account，為每個應用建立專案屬性的 Custom Service Account。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Workflow (日常工作流程)

1.  **Init & Auth:**
    - [ ] `gcloud auth application-default login` (確認是否需要 `--impersonate-service-account`)
    - [ ] `terraform init`
2.  **Validation:**
    - [ ] `terraform fmt -recursive` (保持代碼風格一致)
    - [ ] `terraform validate` (語法檢查)
3.  **Planning:**
    - [ ] `terraform plan -out=tfplan`
    - [ ] **Critical Review:** 檢查 Plan 輸出中是否有 `destroy` 或 `replace` 的資源。特別注意 Database、Disk、IP Address 這些有狀態資源。
4.  **Apply:**
    - [ ] `terraform apply tfplan`

### Production Readiness Checklist (生產環境就緒清單)

- [ ] **State Bucket Security:** 存放 State 的 GCS Bucket 是否已啟用 Object Versioning？是否限制了公開存取 (Public Access Prevention)？
- [ ] **API Consistency:** 是否所有需要的 API (`compute`, `container`, `sqladmin`...) 都已在 `google_project_service` 中宣告？
- [ ] **Deletion Protection:** 對於生產環境的 Database (Cloud SQL) 和 GKE Cluster，是否已開啟 `deletion_protection = true`？
- [ ] **Service Account Scope:** Terraform 運行的 Service Account 是否遵循最小權限原則 (Least Privilege)？(例如：不要給予 `Owner`，而是給予 `Editor` + `Security Admin` 或更細粒度的角色)。
- [ ] **Network Tags:** 是否避免使用 `0.0.0.0/0` 開放 SSH/RDP？是否使用 IAP (Identity-Aware Proxy) 替代？

---

## Real-world examples｜實戰案例

### Scenario: Bootstrapping a Microservice Environment (啟動微服務環境)

這是一個典型的分層架構範例，展示如何將基礎設施與應用部署分離。

#### Layer 1: Networking (由 Platform Team 管理)

```hcl
# networking/main.tf
# 建立 Shared VPC 和 Subnets

module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 6.0"

  project_id   = var.host_project_id
  network_name = "shared-vpc-prod"
  subnets = [
    {
      subnet_name   = "subnet-gke-prod"
      subnet_ip     = "10.10.0.0/20"
      subnet_region = "asia-northeast1"
      # 啟用 Private Google Access 以便無公網 IP 存取 GCP APIs
      private_ip_google_access = "true"
    }
  ]
}

output "network_name" { value = module.vpc.network_name }
output "subnets_names" { value = module.vpc.subnets_names }
```

#### Layer 2: Service Project Creation (由 Platform Team 或自動化流程管理)

使用 Project Factory 建立專案並掛載到 Shared VPC。

```hcl
# projects/order-service.tf

module "project_order_service" {
  source  = "terraform-google-modules/project-factory/google"
  
  name              = "order-service"
  random_project_id = true
  org_id            = var.org_id
  folder_id         = var.apps_folder_id
  billing_account   = var.billing_account
  
  # 自動啟用需要的 API
  activate_apis = ["container.googleapis.com", "sqladmin.googleapis.com"]

  # Shared VPC 設定
  svpc_host_project_id = var.host_project_id
  shared_vpc_subnets = [
    "projects/${var.host_project_id}/regions/asia-northeast1/subnetworks/subnet-gke-prod"
  ]
  
  # 避免刪除專案時關閉 API 導致數據遺失
  disable_services_on_destroy = false
}
```

#### Layer 3: Application Resources (由 App Team 管理)

App Team 在自己的 State 中引用上述基礎設施。

```hcl
# app-resources/main.tf

# 讀取 Networking State (假設使用 remote state)
data "terraform_remote_state" "networking" {
  backend = "gcs"
  config = {
    bucket = "tf-state-prod-networking"
    prefix = "terraform/state"
  }
}

# 建立 Cloud SQL，指定 Private IP (來自 Shared VPC)
resource "google_sql_database_instance" "main" {
  name             = "order-db-prod"
  database_version = "POSTGRES_14"
  region           = "asia-northeast1"
  project          = var.project_id # 來自 Layer 2 的 Output

  settings {
    tier = "db-custom-2-7680"
    ip_configuration {
      ipv4_enabled    = false
      private_network = data.terraform_remote_state.networking.outputs.network_self_link
    }
  }
  
  deletion_protection = true # 生產環境必備
}
```