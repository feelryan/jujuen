# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，GCP 的資源階層（Resource Hierarchy）與 IAM（Identity and Access Management）不僅僅是「開設帳號」或「分配權限」的操作性工作，而是系統設計中定義**信任邊界（Trust Boundaries）**、**成本歸屬（Cost Allocation）**與**隔離策略（Isolation Strategy）**的基石。

For senior engineers, GCP Resource Hierarchy and IAM (Identity and Access Management) are not merely operational tasks of "creating accounts" or "assigning permissions." They are the cornerstones of system design that define **Trust Boundaries**, **Cost Allocation**, and **Isolation Strategies**.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計企業級資源階層**：理解 Organization、Folder 與 Project 的最佳實踐，並能針對多環境（Dev/Staging/Prod）與多租戶（Multi-tenant）場景設計架構。
    **Design Enterprise-Grade Resource Hierarchy**: Understand best practices for Organization, Folders, and Projects, and design architectures for multi-environment (Dev/Staging/Prod) and multi-tenant scenarios.
2.  **掌握 IAM 繼承與隔離機制**：清楚解釋權限如何在階層中繼承，以及如何利用 Deny Policies 和 VPC Service Controls 實施更嚴格的管控。
    **Master IAM Inheritance & Isolation**: Clearly explain how permissions propagate through the hierarchy and how to enforce stricter controls using Deny Policies and VPC Service Controls.
3.  **實作無金鑰身分驗證（Keyless Authentication）**：淘汰長效 Service Account Keys，改用 Workload Identity Federation 進行跨雲或 CI/CD 整合。
    **Implement Keyless Authentication**: Deprecate long-lived Service Account Keys in favor of Workload Identity Federation for cross-cloud or CI/CD integrations.
4.  **優化權限治理（Governance）**：運用 Google Groups 與 Custom Roles 解決大規模團隊的權限管理與「權限過大（Over-privileged）」問題。
    **Optimize Governance**: Utilize Google Groups and Custom Roles to manage permissions and solve "over-privileged" issues in large-scale teams.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 資源階層：檔案系統類比 (Resource Hierarchy: File System Analogy)

GCP 的資源階層類似於 Linux 的檔案系統，權限會由上往下繼承。
GCP's resource hierarchy resembles a Linux file system, where permissions are inherited from top to bottom.

*   **Organization (Root)**: 根節點。代表整間公司。所有策略（Policy）的起點。
    **Organization (Root)**: The root node. Represents the entire company. The starting point for all policies.
*   **Folder (Directory)**: 用於邏輯分組（如：部門、環境）。這是實施「隔離策略」的最佳層級。
    **Folder (Directory)**: Used for logical grouping (e.g., Departments, Environments). This is the best level to implement "isolation strategies."
*   **Project (File/Container)**: **這是最重要的概念**。Project 是 GCP 的基本計費單位與信任邊界。資源（VM, Buckets）是依附於 Project，而非依附於 User。
    **Project (File/Container)**: **This is the most critical concept**. The Project is the fundamental unit of billing and trust boundary in GCP. Resources (VMs, Buckets) belong to a Project, not a User.
*   **Resources**: 實際的服務實體（如 Compute Engine, BigQuery Dataset）。
    **Resources**: The actual service entities (e.g., Compute Engine, BigQuery Dataset).

> **Mental Model Comparison (AWS vs. GCP):**
> *   **AWS Account** $\approx$ **GCP Project**: 兩者都是資源隔離與計費的邊界。
> *   **AWS Organization Unit (OU)** $\approx$ **GCP Folder**: 用於分組管理。
> *   **AWS IAM Role** $\approx$ **GCP Service Account**: 機器或應用程式使用的身分。

## 2.2 IAM 模型：Who, What, Which (The IAM Model)

GCP IAM 由三個部分組成：
GCP IAM consists of three parts:

1.  **Principal (Who)**: Google Account, Service Account, Google Group, Cloud Identity domain.
2.  **Role (What)**: 一組權限的集合（Collection of Permissions）。
    *   *Primitive Roles* (Owner, Editor, Viewer): **Production 禁止使用**。範圍太廣。
    *   *Predefined Roles* (e.g., `roles/storage.objectViewer`): Google 管理，細粒度較佳。
    *   *Custom Roles*: 自定義權限集合，用於極致的 Least Privilege。
3.  **Policy (Binding)**: 將 Principal 與 Role 綁定在某個 Resource 上。

**關鍵規則 (Key Rule)**: 權限是**加法（Additive）**的。如果在 Org 層級給了 User A `Editor` 權限，你無法在 Project 層級移除它（除非使用 IAM Deny Policy，這是較新的進階功能）。
**Key Rule**: Permissions are **additive**. If you grant User A `Editor` permissions at the Org level, you cannot remove them at the Project level (unless using IAM Deny Policy, a newer advanced feature).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 環境隔離架構 (Environment Isolation Architecture)

在系統設計面試或實務中，常見錯誤是將 Dev/Staging/Prod 放在同一個 Project 的不同 VPC 中。
In system design interviews or practice, a common mistake is placing Dev/Staging/Prod within different VPCs in the same Project.

**最佳實踐 (Best Practice)**: 使用 **Project** 作為環境隔離邊界。
**Best Practice**: Use **Projects** as the boundary for environment isolation.

*   **Prod Project**: 只有 CI/CD Pipeline 與極少數 SRE 擁有存取權。
*   **Staging Project**: 開發者有唯讀權限，Pipeline 有部署權限。
*   **Dev Project**: 開發者擁有較高權限（如 Editor），用於快速實驗。

**為何這樣設計？ (Why?)**
1.  **Blast Radius**: 若 Dev Project 被駭或誤刪資源，不會影響 Prod 的 IAM 或 Quota。
2.  **Quota Isolation**: 避免 Dev 的壓力測試耗盡 Prod 的 API Quota。
3.  **Billing Clarity**: 清楚區分各環境成本。

## 3.2 共享服務模式 (Shared Services Pattern)

在大型組織中，網路與安全通常由中央團隊管理。
In large organizations, networking and security are usually managed by a central team.

*   **Shared VPC Host Project**: 集中管理網路（Subnets, Firewalls, VPN）。
*   **Service Projects**: 各個應用團隊的 Project，依附於 Host Project 使用網路資源。

這種模式允許應用團隊擁有自己的 Project 管理權（部署 VM、使用 BigQuery），但無法更改網路拓樸，實現了 **Separation of Duties (SoD)**。
This pattern allows application teams to manage their own Projects (deploy VMs, use BigQuery) but restricts them from altering the network topology, achieving **Separation of Duties (SoD)**.

---

# 4. 逐步示例：Workload Identity Federation (Walkthrough: Workload Identity Federation)

## 背景 (Context)
你需要設計一個 CI/CD 流程，讓 GitHub Actions 自動部署 Terraform 到 GCP。
You need to design a CI/CD pipeline where GitHub Actions automatically deploys Terraform to GCP.

## Naive Approach (反模式 / Anti-pattern)
1.  建立一個 Service Account (SA)。
2.  下載 JSON Key file。
3.  將 JSON 內容貼到 GitHub Secrets。
4.  **風險**: Key 洩漏風險極高，且 Key 預設有效期長達 9999 年，難以輪替（Rotation）。
    **Risk**: High risk of Key leakage; Keys are valid for 9999 years by default and difficult to rotate.

## Mature Solution: Workload Identity Federation
讓 GCP 信任 GitHub 的 OIDC Token，無需管理任何長效 Key。
Let GCP trust GitHub's OIDC Token, eliminating the need to manage any long-lived keys.

### Step 1: 定義 Workload Identity Pool 與 Provider (Terraform)
Define Workload Identity Pool and Provider.

```hcl
# 1. Create a Pool
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  disabled                  = false
}

# 2. Create a Provider (OIDC)
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  
  # GitHub's OIDC Issuer
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}
```

### Step 2: 綁定 Service Account 權限
Bind Service Account permissions.

我們不給 GitHub 直接權限，而是允許符合特定條件（特定 Repo）的 GitHub Token "Impersonate"（扮演）GCP Service Account。
We don't grant permissions directly to GitHub; instead, we allow a GitHub Token meeting specific criteria (specific Repo) to "Impersonate" a GCP Service Account.

```hcl
resource "google_service_account_iam_binding" "workload_identity_user" {
  service_account_id = google_service_account.ci_cd_sa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    # Only allow requests from a specific GitHub Repository
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/my-org/my-repo"
  ]
}
```

### Step 3: GitHub Actions Config
在 YAML 中使用 `google-github-actions/auth`。
Use `google-github-actions/auth` in YAML.

```yaml
steps:
  - id: 'auth'
    uses: 'google-github-actions/auth@v1'
    with:
      workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider'
      service_account: 'ci-cd-sa@my-project.iam.gserviceaccount.com'
      # No JSON keys involved!
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 使用 Primitive Roles (Owner/Editor/Viewer)
*   **錯誤描述**: 為了方便，給予開發者 `Editor` 權限。
    **Description**: Granting `Editor` permissions to developers for convenience.
*   **為何不好**: `Editor` 幾乎可以做任何事（除了修改 IAM），包括刪除整個 DB 或修改防火牆。這違反了 Least Privilege 原則。
    **Why it's bad**: `Editor` can do almost anything (except modifying IAM), including deleting entire DBs or changing firewalls. This violates the Principle of Least Privilege.
*   **替代方案**: 使用 Predefined Roles (如 `roles/compute.instanceAdmin`) 或 Custom Roles。
    **Alternative**: Use Predefined Roles (e.g., `roles/compute.instanceAdmin`) or Custom Roles.

## 5.2 直接將 IAM 綁定給 User (Direct User Assignment)
*   **錯誤描述**: `alice@company.com` 離職了，SRE 需要去 50 個 Projects 移除她的權限。
    **Description**: `alice@company.com` leaves the company, and SRE needs to remove her permissions from 50 Projects.
*   **為何不好**: 管理噩夢，且容易有漏網之魚。
    **Why it's bad**: A management nightmare and prone to oversight.
*   **替代方案**: **Google Groups**。將 IAM 綁定給 `developers@company.com` 群組。人員異動時，只需在 Google Workspace 修改群組成員，無需更動 GCP IAM Policy。
    **Alternative**: **Google Groups**. Bind IAM to the `developers@company.com` group. When personnel changes occur, simply update group membership in Google Workspace without touching GCP IAM Policies.

## 5.3 忽視 Service Account 的權限範圍 (Ignoring SA Scopes)
*   **錯誤描述**: 在 VM 上使用 Default Compute Engine Service Account，並給予 `Editor` 權限。
    **Description**: Using the Default Compute Engine Service Account on a VM and granting it `Editor` permissions.
*   **為何不好**: 如果該 VM 被攻陷（SSRF 攻擊等），攻擊者將獲得整個 Project 的控制權。
    **Why it's bad**: If the VM is compromised (e.g., via SSRF), the attacker gains control over the entire Project.
*   **替代方案**: 為每個微服務建立專用的 Service Account，並只給予必要的權限（如只能寫入特定的 GCS Bucket）。
    **Alternative**: Create dedicated Service Accounts for each microservice and grant only necessary permissions (e.g., write access to a specific GCS Bucket).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何設計一個多租戶（Multi-tenant）SaaS 的 GCP 架構？
**How would you design a GCP architecture for a multi-tenant SaaS?**

*   **高分回答要點 (Key Points)**:
    *   討論 **Isolation Level**：是 Namespace 隔離（K8s）、Project 隔離，還是 Database 隔離？
    *   **Project per Tenant**: 這是最強的隔離（IAM、Quota、Billing 都獨立），但管理成本高，需要強大的 Automation (Terraform)。
    *   **Shared Project**: 成本低，但需依賴 Application 層級的邏輯隔離（Logical Isolation），風險較高。
    *   提到 **Service Consumer Management**: 如果是 SaaS，是否考慮使用 PSC (Private Service Connect) 讓客戶連線。

## Q2: 開發者抱怨「我明明有權限，為什麼還是 Access Denied」？你會如何排查？
**Developers complain "I have the permission, why is it still Access Denied?" How do you troubleshoot?**

*   **高分回答要點 (Key Points)**:
    *   **IAM Policy Troubleshooter**: 使用 GCP 內建工具檢查 Principal 與 Resource 的權限綁定。
    *   **Hierarchy Inheritance**: 檢查是否有上層（Org/Folder）的 Deny Policy。
    *   **VPC Service Controls (VPC-SC)**: 這是一個常見陷阱。即使 IAM 通過，如果請求來自受信任邊界之外（例如從公網存取受保護的 Bucket），VPC-SC 會攔截請求。
    *   **Scope (for VMs)**: 檢查 VM 實體的 Access Scopes 是否限制了 API 呼叫。

## Q3: 請解釋 Service Account Impersonation 的運作原理與優勢。
**Explain the mechanism and benefits of Service Account Impersonation.**

*   **高分回答要點 (Key Points)**:
    *   **機制**: 使用者（User A）不直接擁有資源權限，而是擁有「使用 Service Account B」的權限 (`roles/iam.serviceAccountTokenCreator`)。User A 請求 GCP 產生 SA B 的短效 Token 來執行操作。
    *   **優勢**:
        1.  **可追溯性 (Auditability)**: Log 會顯示 "User A impersonated SA B"。
        2.  **安全性**: 無需下載長效 Key。
        3.  **最小權限**: User A 平時無權限，只有在需要執行特定任務時才切換身分。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **Project 是邊界**：將 Project 視為計費、配額與安全的基本隔離單元。
    **Project is the Boundary**: Treat the Project as the fundamental unit of isolation for billing, quotas, and security.
2.  **Groups > Users**：永遠將 IAM Role 綁定給 Google Groups，而非個人帳號。
    **Groups > Users**: Always bind IAM Roles to Google Groups, not individual user accounts.
3.  **Workload Identity > Keys**：在機器對機器的溝通中，盡可能避免下載 JSON Keys。
    **Workload Identity > Keys**: Avoid downloading JSON Keys for machine-to-machine communication whenever possible.
4.  **權限是繼承的**：Org -> Folder -> Project。善用 Folder 進行大規模管理。
    **Permissions are Inherited**: Org -> Folder -> Project. Leverage Folders for management at scale.
5.  **Least Privilege**：避免使用 Primitive Roles (Editor/Owner)，優先使用 Predefined 或 Custom Roles。
    **Least Privilege**: Avoid Primitive Roles (Editor/Owner); prefer Predefined or Custom Roles.

## 下一步 (Next Steps)
掌握了身分與架構後，下一步我們需要連接這些資源。下一章將探討 **GCP 網路架構 (VPC, Shared VPC, Interconnect)**，這是分散式系統在雲端運作的血管。
Having mastered identity and architecture, the next step is connecting these resources. The next chapter will explore **GCP Network Architecture (VPC, Shared VPC, Interconnect)**, the blood vessels of distributed systems in the cloud.