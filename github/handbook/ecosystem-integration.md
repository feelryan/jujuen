# 生態系整合與工具鏈邊界 / Ecosystem Integration & Toolchain Boundaries

## Mental model｜心智模型

在現代軟體工程中，GitHub 不僅僅是程式碼倉庫（Code Warehouse），它是 **DevOps 流程的中央樞紐（Central Nervous System）**。理解生態系整合的核心在於掌握資料流向與觸發機制，並劃清工具的職責邊界。

我們可以用 **「上下游與事件驅動（Upstream, Downstream & Event-Driven）」** 模型來思考：

1.  **上游（Upstream - Planning & Context）：**
    *   **來源**：Jira, Linear, Product Specs。
    *   **目的**：提供程式碼變更的「原因（Why）」與「脈絡（Context）」。
    *   **整合關鍵**：自動化連結（Linking）與狀態同步（State Sync）。不應讓開發者手動複製貼上資訊。

2.  **核心（Core - The Source of Truth）：**
    *   **來源**：GitHub Repo (Code, Config, Actions)。
    *   **角色**：唯一的真實來源。所有的變更都應以 Git Commit/PR 為原子單位。

3.  **下游（Downstream - Execution & Notification）：**
    *   **基礎設施（Infra）**：Terraform, Kubernetes, Cloud Providers。
    *   **通訊（Comms）**：Slack, Microsoft Teams, Email。
    *   **整合關鍵**：**信噪比（Signal-to-Noise Ratio）** 與 **最小權限原則（Least Privilege）**。

**邊界決策（Boundary Decision）：**
最常見的誤區是試圖用 GitHub Actions 做所有事情。
*   **CI (Continuous Integration)** 屬於 GitHub Actions（測試、建置、打包）。
*   **CD (Continuous Deployment)** 往往更適合交給專門的 GitOps 工具（如 ArgoCD）或基礎設施即代碼工具（Terraform Cloud/Atlantis），以保持狀態管理的嚴謹性。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 溝通整合模式：ChatOps 與信噪比管理
**Communication Integration: ChatOps & Signal-to-Noise Management**

*   **Actionable Notifications（可執行的通知）：**
    *   不要只發送「建置成功」的通知（這是常態）。
    *   只發送需要人類介入的通知：`Build Failed`、`Review Requested`、`Deployment Pending Approval`。
    *   **Pattern**：在 Slack/Teams 通知中包含直接連結（Deep Links）至 PR 或 Workflow Log，甚至包含 "Approve" 按鈕（若安全性允許）。
*   **Channel Routing（頻道分流）：**
    *   將 `Production` 部署通知發送到全體工程師頻道。
    *   將 `Staging` 或個別 Repo 的 PR 動態發送到特定的 Team Channel。
    *   避免將所有 Repos 的 commit log 灌入同一個頻道，這會導致「通知疲勞（Alert Fatigue）」。

### 2. 專案管理整合：雙向同步
**Project Management: Bi-directional Sync**

*   **Branch/PR Naming Convention（命名約定）：**
    *   強制分支名稱包含 Ticket ID（例如 `feat/PROJ-123-login-page`）。
    *   利用 GitHub Autolink references 功能，讓 PR 描述中的 `PROJ-123` 自動變成超連結。
*   **State Automation（狀態自動化）：**
    *   **Pattern**：
        *   PR Open -> Ticket moves to "In Review".
        *   PR Merged -> Ticket moves to "Done" / "Ready for QA".
    *   使用 Linear 或 Jira 的官方整合，而非自己寫複雜的 Webhook scripts，以降低維護成本。

### 3. GitOps 與基礎設施邊界
**GitOps & Infrastructure Boundaries**

*   **CI vs. CD Separation（CI 與 CD 分離）：**
    *   **GitHub Actions (CI)**：負責產出 Artifact（Docker Image, Jar, Binary）並推送到 Registry。它**不應該**直接擁有 Production Cluster 的 `admin` 權限。
    *   **GitOps Controller (CD)**：如 ArgoCD 或 Flux，監聽 Config Repo 的變更，主動拉取（Pull）並應用到 Cluster。
    *   **邊界優勢**：這樣做避免了將高權限的 Kubeconfig 暴露在 GitHub Actions Secrets 中。
*   **Infrastructure as Code (IaC) Workflow：**
    *   在 PR 中執行 `terraform plan` 並將結果以 Comment 形式貼回 PR（使用工具如 Atlantis 或 GitHub Actions bot）。
    *   只有在 Merge 到 main branch 後才執行 `terraform apply`。

### 4. 安全性整合：OIDC
**Security Integration: OIDC over Long-lived Keys**

*   **OpenID Connect (OIDC)**：
    *   **Best Practice**：永遠不要在 GitHub Secrets 存放 AWS `AWS_ACCESS_KEY_ID` 或 GCP Service Account Keys。
    *   配置 Cloud Provider 信任 GitHub 的 OIDC Token。這樣 GitHub Actions 只能在執行當下獲取短暫的權限，大幅降低金鑰洩漏風險。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Wall of Noise" (通知牆)
*   **現象**：Slack 頻道裡充滿了來自 GitHub 的綠色勾勾（Success）訊息，沒人看，最後大家都 Mute 該頻道。
*   **後果**：當真正的紅燈（Failure）出現時，被淹沒在雜訊中，導致反應延遲。
*   **修正**：預設關閉 Success 通知，只開啟 Failure 和 Change Request 通知。

### 2. The "God-Mode" CI Runner (上帝模式 Runner)
*   **現象**：為了方便部署，給予 GitHub Action Runner 對 AWS/GCP/K8s 的完全管理員權限。
*   **後果**：任何能修改 Workflow 檔案的開發者（或被盜用的帳號）都能輕易刪除整個 Production 環境或竊取資料。
*   **修正**：使用 OIDC，並嚴格限縮 IAM Role 的權限範圍（例如只能更新特定的 ECS Service，不能刪除 Cluster）。

### 3. Hard-Coupling Logic in Webhooks (Webhook 內的硬耦合邏輯)
*   **現象**：在 GitHub Webhook 接收端（自建的 Server）撰寫大量複雜的業務邏輯來處理 Jira/Slack 同步。
*   **後果**：難以除錯，且當 API 變更時容易損壞。GitHub 變成了隱形的「後端資料庫」。
*   **修正**：盡量使用 SaaS 原生整合（Native Integrations）。若必須自建，請使用 GitHub Actions 作為邏輯載體，而非外部 Webhook Server，以保持邏輯與程式碼同在。

### 4. Mixing Config and Code (混淆配置與程式碼)
*   **現象**：在 Application Repo 中直接包含大量 Kubernetes Manifests，且 CI 流程直接 `kubectl apply`。
*   **後果**：難以追蹤「目前 Production 到底跑的是哪個版本」，且 Rollback 困難。
*   **修正**：採用 GitOps 模式，將 App Code 與 Infra Config (Helm charts/Kustomize) 分離到不同的 Repo 或明確的目錄結構中。

---

## Checklists & workflows｜檢查清單與流程

### Integration Health Checklist (整合健康度檢查)

- [ ] **權限審計**：檢查所有 GitHub Secrets，移除長效型的 Cloud Credentials，改用 OIDC。
- [ ] **通知盤點**：檢查 Slack/Teams 整合，是否有人在過去一週內因「太吵」而抱怨？若是，調整通知層級。
- [ ] **票務連結**：隨機抽查 5 個已合併的 PR，是否都能在 1 次點擊內連到對應的 Jira/Linear Ticket？
- [ ] **狀態檢查**：PR 是否包含來自外部系統的 Status Checks（例如：`Terraform Plan`、`SonarQube`、`Vercel Preview`）？
- [ ] **GitOps 邊界**：CI Pipeline 是否只負責產出 Artifact？部署邏輯是否與 CI 分離（或至少有明確的 Approval Gate）？

### Decision Tree: Where to put the logic? (邏輯放在哪？)

1.  **Is it about building/testing code?** -> **GitHub Actions**.
2.  **Is it about managing infrastructure state (Terraform)?** -> **Atlantis / Terraform Cloud** (triggered by GitHub Webhook).
3.  **Is it about deploying containers to K8s?** -> **ArgoCD / Flux** (watching a Config Repo).
4.  **Is it about team notification?** -> **Native Slack/Teams App** (filtered).

---

## Real-world examples｜實戰案例

### Scenario 1: The "Clean" Linear Integration
**情境**：開發團隊使用 Linear 管理任務，希望 PR 與任務自動同步。

**Workflow**：
1.  開發者領取任務 `ENG-342: Fix login bug`。
2.  開發者使用工具（或手動）建立分支 `fix/ENG-342-login-bug`。
3.  GitHub Action (或 Linear App) 偵測到分支名稱符合 `ENG-\d+`。
4.  **自動化動作**：
    *   Linear Ticket 自動從 `Todo` 移動到 `In Progress`。
    *   PR 建立後，Linear Ticket 自動移動到 `In Review`。
    *   PR 描述中自動插入 `[ENG-342](https://linear.app/team/issue/ENG-342)` 連結。
5.  **結果**：PM 不需要詢問工程師進度，看 Linear 看板即可；工程師不需要離開 IDE/Terminal 去更新票務狀態。

### Scenario 2: GitOps with Image Updater
**情境**：前後端分離專案，需要自動部署到 Staging，但 Production 需要手動確認。

**Workflow**：
1.  **App Repo**: 開發者 Merge PR 到 `main`。
2.  **GitHub Actions (CI)**:
    *   執行單元測試。
    *   建置 Docker Image: `myapp:sha-12345`。
    *   Push Image 到 ECR/GCR。
    *   **邊界操作**：CI **不直接**連線 K8s。CI 觸發一個 commit 到 **Config Repo** (或使用 ArgoCD Image Updater)。
3.  **Config Repo**: `values.yaml` 中的 tag 被更新為 `sha-12345`。
4.  **ArgoCD (CD)**:
    *   偵測到 Config Repo 變更。
    *   自動 Sync 到 `Staging` Cluster。
    *   發送 Slack 通知：「Staging 已更新至 `sha-12345`」。
5.  **Production Promotion**:
    *   Release Manager 在 GitHub 建立一個 Release Tag。
    *   觸發另一個 Action 更新 Config Repo 的 `production/values.yaml`。
    *   ArgoCD Sync 到 `Production` Cluster。

### Scenario 3: Terraform Plan on PR
**情境**：基礎設施變更需要 Code Review，避免錯誤配置導致斷線。

**Workflow**：
1.  DevOps 工程師修改 `main.tf` 調整 Security Group，發送 PR。
2.  **GitHub Actions**:
    *   設定 AWS OIDC 認證。
    *   執行 `terraform fmt -check`。
    *   執行 `terraform plan -out=tfplan`。
    *   使用 script 將 `plan` 的輸出結果（變更摘要）**留言（Comment）** 在該 PR 中。
3.  **Reviewer**:
    *   在 GitHub PR 介面直接看到：「將會新增 1 個 Rule，刪除 0 個 Resource」。
    *   Approve PR。
4.  **Merge**:
    *   Merge 到 `main` 後，觸發 `terraform apply`。