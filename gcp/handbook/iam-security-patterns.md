# IAM 治理與資安實務模式 / IAM Governance & Security Patterns

在 GCP 的世界中，IAM (Identity and Access Management) 不僅僅是開通帳號，它是雲端架構的第一道防線，也是最容易因為配置錯誤導致資料外洩的環節。本章節將跳過基礎定義，直接切入如何在大規模組織中進行 IAM 治理與安全實作。

## Mental model｜心智模型

要掌握 GCP IAM，必須建立以下三個核心認知模型：

### 1. 綁定模型 (The Binding Model)
GCP IAM 不是將權限直接賦予使用者，而是建立一個 **Binding (綁定)**。
- **Who**: Principal (User, Group, Service Account)
- **What**: Role (Collection of Permissions)
- **Where**: Resource (Organization, Folder, Project, Resource)

> **Mental Image**: 想像 IAM 是一個「黏合劑」，它在特定的層級（Where），將名牌（Who）與職責說明書（What）黏在一起。

### 2. 繼承與聯集 (Inheritance & Union)
- **向下繼承**：在 Organization 層級賦予的權限，會自動流向所有的 Folders 和 Projects。你無法在下層「移除」上層賦予的 Allow 權限（除非使用 Deny Policy，但那是進階功能）。
- **權限聯集**：如果一個使用者同時在 Group A (Viewer) 和 Group B (Editor)，他在該資源上擁有的權限是兩者的總和 (Editor)。

### 3. 身份即邊界 (Identity as Perimeter)
在 Zero Trust 架構下，網路位置（IP）不再是唯一的信任來源。**Service Account (SA)** 是機器對機器的身份證。正確管理 SA 的生命週期與權限範圍，等同於維護防火牆規則。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Workload Identity Federation (取代長效型 Key)
這是目前最重要的安全模式。**永遠不要**為在 GCP 外部運行的服務（如 GitHub Actions, AWS Lambda, On-prem servers）下載 Service Account JSON Key。
- **作法**：設定 Workload Identity Federation，讓外部身份提供者 (IdP) 透過 OIDC 交換 GCP 的短效 Access Token。
- **優勢**：消除了 Key 洩漏的風險（Key rotation 也不再需要）。

### 2. Google Groups for Humans (以群組管理人員)
永遠不要將 IAM Role 直接綁定給個人的 Gmail 或 Cloud Identity 帳號。
- **Pattern**：
  - 建立功能性群組：`gcp-org-admins@company.com`, `gcp-data-viewers@company.com`。
  - 在 IAM Policy 中只對 Group 授權。
  - 人員入職/離職只需在 Google Workspace/Cloud Identity 修改群組成員，無需更動 GCP 架構。

### 3. Service Account per Workload (微服務隔離)
不要讓多個應用程式共用同一個 Service Account，更不要使用 Default Service Account（預設權限過大）。
- **Pattern**：
  - 每個微服務（Microservice）或 Cloud Function 都有自己專屬的 SA。
  - 該 SA 只擁有該服務所需的最小權限（例如：只能寫入特定的 GCS Bucket，不能讀取其他 Bucket）。

### 4. Custom Roles for Least Privilege (最小權限客製化)
GCP 的 Predefined Roles (如 `Pub/Sub Editor`) 有時仍包含過多權限。
- **作法**：使用 IAM Recommender 觀察實際使用的權限，建立 Custom Role，剔除不必要的 `delete` 或 `admin` 權限。
- **情境**：CI/CD Pipeline 通常只需要 `cloudbuild.builds.editor` 和 `appengine.appAdmin`，不需要 Project Editor。

### 5. Organization Policy Guardrails (組織策略護欄)
IAM 控制「誰可以做什麼」，Organization Policy 控制「什麼資源可以被建立」。
- **必須開啟的 Policies**：
  - `iam.disableServiceAccountKeyCreation`：禁止建立新的 SA Keys。
  - `iam.allowedPolicyMemberDomains`：限制只能授權給公司網域內的成員。
  - `storage.uniformBucketLevelAccess`：強制統一 Bucket 權限管理，停用 ACL。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Owner/Editor" Trap (濫用基本角色)
- **反模式**：為了方便，直接給開發者或 Service Account `roles/editor` 或 `roles/owner`。
- **後果**：Editor 權限極大，可以刪除資源、修改網路設定，甚至提升權限（Privilege Escalation）。
- **修正**：預設只給 `Viewer`，需要操作特定服務時，疊加該服務的 Admin/User Role。

### 2. Committed Keys (金鑰提交到版控)
- **反模式**：將 `service-account.json` 放在專案目錄中，並不小心 git push 到 GitHub。
- **後果**：這是 GCP 帳號被駭客用來挖礦的最常見途徑。Bot 會在幾秒鐘內掃描到並開始攻擊。
- **修正**：使用 Workload Identity；如果必須用 Key，使用 Secret Manager 並在 `.gitignore` 嚴格排除。

### 3. User-Managed Keys for Service Accounts
- **反模式**：開發人員自行建立 SA Key 並長期持有，沒有輪替機制 (Key Rotation)。
- **後果**：離職員工可能仍持有有效的 Key。
- **修正**：強制 Key Rotation (譬如每 90 天)，或完全禁止建立 Key。

### 4. Service Account User Role Misunderstanding
- **陷阱**：隨意賦予使用者 `roles/iam.serviceAccountUser`。
- **解釋**：擁有此權限的使用者可以「冒充」該 Service Account 執行任務。如果該 SA 有 Owner 權限，該使用者實質上就是 Owner。
- **修正**：嚴格限制誰可以 Act As Service Account。

---

## Checklists & workflows｜檢查清單與流程

### 🚀 新專案 IAM 初始化清單 (Project Setup Checklist)

- [ ] **移除預設權限**：移除 Default Compute Engine Service Account 的 Editor 權限。
- [ ] **群組授權**：確認沒有個人帳號直接綁定在 IAM 列表，全部透過 Group 管理。
- [ ] **啟用 Org Policy**：在專案層級確認繼承或覆寫了關鍵的安全限制（如禁止 External IP）。
- [ ] **Terraform 管理**：確認所有 IAM Binding 都是透過 IaC (Terraform) 定義，而非手動 Console 點擊。

### 🛡️ 安全審計流程 (Security Audit Workflow)

1. **檢查 Service Account Keys**：
   - 使用 Cloud Asset Inventory 查詢所有 Key 的年齡。
   - 標記並停用超過 90 天未輪替的 Key。
2. **審查 IAM Recommender**：
   - 進入 IAM Console，查看 Google 建議的 "Over-granted permissions"。
   - 根據建議縮減權限（例如將 Editor 降級為特定的 Viewer + Operator）。
3. **檢查 Public Access**：
   - 確認沒有 GCS Bucket 或 Cloud Run 服務被意外設定為 `allUsers` 或 `allAuthenticatedUsers`（除非是公開網站）。

---

## Real-world examples｜實戰案例

### 案例一：GitHub Actions 部署 Cloud Run (無 Key 實作)

傳統做法是下載 JSON Key 貼到 GitHub Secrets，現代做法是 **Workload Identity Federation**。

**Terraform 實作概念：**

```hcl
# 1. 建立 Workload Identity Pool
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
}

# 2. 建立 Provider (連結 GitHub OIDC)
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  attribute_mapping                  = {
    "google.subject" = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# 3. 授權 GitHub Repo 扮演特定的 Service Account
resource "google_service_account_iam_binding" "workload_identity_user" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/my-org/my-repo"
  ]
}
```

### 案例二：GKE Workload Identity (Pod 到 GCP 資源的存取)

**情境**：GKE 中的 Pod 需要讀取 Cloud SQL 和 GCS，但不希望將 Key 掛載進 Container。

**流程**：
1. **GCP 端**：建立 Google Service Account (GSA)，賦予 `Cloud SQL Client` 和 `Storage Object Viewer` 角色。
2. **K8s 端**：建立 Kubernetes Service Account (KSA)。
3. **綁定**：將 GSA 與 KSA 綁定 (`roles/iam.workloadIdentityUser`)。
4. **Annotation**：在 KSA 上標註 GSA 的 Email。

```bash
# 綁定指令範例
gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[$K8S_NAMESPACE/$KSA_NAME]"

# K8s Service Account Annotation
kubectl annotate serviceaccount $KSA_NAME \
    --namespace $K8S_NAMESPACE \
    iam.gke.io/gcp-service-account=$GSA_EMAIL
```

**結果**：Pod 啟動時，GKE 會自動注入身份憑證，應用程式使用 Standard Client Library 即可自動取得權限，完全無需管理 Key 檔案。