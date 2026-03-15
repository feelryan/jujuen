# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，CI/CD 不僅僅是自動化測試與構建，更關鍵的是「如何安全、可控地將程式碼交付到生產環境」。GitHub 提供了強大的 **Environments** 與 **Deployments API**，讓我們能將部署流程從單純的腳本執行，提升為具備狀態追蹤、審核機制與策略控制（如 Blue-Green 或 Canary）的系統工程。

In a Senior Software Engineer's career, CI/CD is more than just automated testing and building; it is critically about "how to safely and controllably deliver code to production." GitHub provides powerful **Environments** and the **Deployments API**, allowing us to elevate deployment processes from simple script execution to system engineering capable of state tracking, approval mechanisms, and strategic controls (such as Blue-Green or Canary deployments).

完成本章後，你將能夠：

By the end of this chapter, you will be able to:

1.  **掌握 Environments 的治理機制**：利用 Protection Rules（保護規則）與 Environment Secrets 實現符合 SOC2 或企業合規要求的部署流程。
    **Master Environment Governance**: Utilize Protection Rules and Environment Secrets to implement deployment workflows compliant with SOC2 or enterprise standards.
2.  **運用 Deployments API 解耦部署邏輯**：理解如何透過 API 觸發部署並回報狀態，將 GitHub 作為部署的「控制平面 (Control Plane)」，而非僅是觸發器。
    **Decouple Deployment Logic via Deployments API**: Understand how to trigger deployments and report status via API, treating GitHub as the deployment "Control Plane" rather than just a trigger.
3.  **實作進階部署策略**：設計並實作基於 GitHub Actions 的 Blue-Green 或 Canary 部署流程，並整合第三方監控（如 Datadog/Prometheus）來決定是否自動 rollback。
    **Implement Advanced Deployment Strategies**: Design and implement Blue-Green or Canary deployment workflows based on GitHub Actions, integrating third-party monitoring (e.g., Datadog/Prometheus) to decide on automatic rollbacks.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Environments：部署的「閘門」 (Environments: The "Gates" of Deployment)

**直覺類比**：想像 Environments 是進入金庫（Production）前的多道安全閘門。每一道閘門都有特定的守衛（Reviewers）、計時鎖（Wait Timer）以及該區域專屬的鑰匙（Environment Secrets）。

**Intuitive Analogy**: Imagine Environments as multiple security gates before entering a vault (Production). Each gate has specific guards (Reviewers), time locks (Wait Timer), and keys exclusive to that zone (Environment Secrets).

**正規定義**：GitHub Environments 是 Repository 中的邏輯實體，用於定義部署目標（如 `staging`, `production`）。它允許設定：
- **Protection Rules**: 必須經過特定人員核准或 CI 檢查通過才能部署。
- **Environment Secrets**: 僅在該環境的 Job 執行時才能存取的敏感資訊。

**Formal Definition**: GitHub Environments are logical entities within a Repository used to define deployment targets (e.g., `staging`, `production`). They allow configuration of:
- **Protection Rules**: Deployments must pass specific approvals or CI checks.
- **Environment Secrets**: Sensitive information accessible only when a Job runs in that specific environment.

### 2.2 Deployments API：意圖與狀態的分離 (Deployments API: Separation of Intent and State)

**核心概念**：大多數人習慣 `git push` 觸發 Action。但 Deployments API 引入了「事件驅動」模型。
1.  **Deployment (Intent)**: "I *want* to deploy commit X to environment Y."
2.  **Deployment Status (State)**: "The deployment is `pending`, `in_progress`, `success`, or `failure`."

**Core Concept**: Most are used to `git push` triggering Actions. However, the Deployments API introduces an "event-driven" model.
1.  **Deployment (Intent)**: "I *want* to deploy commit X to environment Y."
2.  **Deployment Status (State)**: "The deployment is `pending`, `in_progress`, `success`, or `failure`."

這使得 GitHub 能與外部系統（如 AWS CodeDeploy, K8s Controllers, Slack Bots）深度整合。外部系統可以接收 GitHub 的部署指令，執行後再回報狀態給 GitHub，讓 PR 介面顯示即時部署進度。

This enables deep integration between GitHub and external systems (like AWS CodeDeploy, K8s Controllers, Slack Bots). External systems can receive deployment instructions from GitHub, execute them, and report the status back, allowing the PR interface to show real-time deployment progress.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，我們通常不會讓 GitHub Actions 直接 SSH 到伺服器執行指令。相反，我們將 GitHub 視為 **Orchestrator (協調者)**。

In large-scale distributed systems, we typically don't let GitHub Actions SSH directly into servers to execute commands. Instead, we treat GitHub as an **Orchestrator**.

### 3.1 架構角色 (Architectural Roles)

-   **GitHub (Control Plane)**: 負責權限管理（誰能部署？）、審核流程、以及記錄部署歷史（Audit Log）。
-   **GitHub Actions / External CD (Execution Plane)**: 負責實際的基礎設施操作（Terraform apply, Helm upgrade）。
-   **Observability Platform (Feedback Loop)**: 監控部署後的健康狀況，透過 API 回報給 GitHub。

-   **GitHub (Control Plane)**: Responsible for permission management (who can deploy?), approval workflows, and recording deployment history (Audit Log).
-   **GitHub Actions / External CD (Execution Plane)**: Responsible for actual infrastructure operations (Terraform apply, Helm upgrade).
-   **Observability Platform (Feedback Loop)**: Monitors health post-deployment and reports back to GitHub via API.

### 3.2 對系統屬性的影響 (Impact on System Attributes)

-   **可觀測性 (Observability)**: 開發者不需要登入 AWS Console 或 K8s Dashboard，直接在 GitHub Pull Request 的 "Timeline" 就能看到該 Commit 何時被部署到哪個環境，以及當前的狀態。
-   **安全性 (Security)**: 透過 Environment Secrets，Production 的金鑰永遠不會暴露給 Staging 的 Job，大幅降低 Supply Chain Attack 風險。
-   **可靠性 (Reliability)**: 配合 Deployment Status，我們可以實作「自動化 Rollback」。若狀態回報為 `failure`，系統自動觸發上一個穩定版本的部署。

-   **Observability**: Developers don't need to log into AWS Console or K8s Dashboard; they can see when a commit was deployed to which environment and its current status directly on the GitHub Pull Request "Timeline".
-   **Security**: Via Environment Secrets, Production keys are never exposed to Staging jobs, significantly reducing Supply Chain Attack risks.
-   **Reliability**: Coupled with Deployment Status, we can implement "Automated Rollback". If the status reports `failure`, the system automatically triggers a deployment of the last stable version.

---

# 4. 逐步示例：實作 Canary 部署流程 (Walkthrough: Implementing a Canary Deployment Workflow)

### 情境 (Scenario)
我們有一個微服務 `payment-service`，需要部署到 Kubernetes。為了降低風險，我們採用 Canary 策略：先部署 10% 流量，觀察 5 分鐘，若無錯誤則全量部署。

We have a microservice `payment-service` needing deployment to Kubernetes. To mitigate risk, we use a Canary strategy: deploy to 10% traffic first, observe for 5 minutes, and if no errors occur, proceed to full deployment.

### 步驟 1: 設定 Environments (Step 1: Setup Environments)

在 GitHub Repo Settings -> Environments 中建立 `production`。
設定 **Deployment protection rules**:
-   **Required reviewers**: 資深工程師群組。
-   **Wait timer**: 0 分鐘 (由流程控制)。

Create `production` in GitHub Repo Settings -> Environments.
Configure **Deployment protection rules**:
-   **Required reviewers**: Senior Engineer group.
-   **Wait timer**: 0 minutes (controlled by workflow).

### 步驟 2: Workflow 定義 (Step 2: Workflow Definition)

我們使用 `deployment` 事件觸發 Workflow，而非 `push`。這允許我們透過 ChatOps 或 API 觸發部署。

We use the `deployment` event to trigger the Workflow, instead of `push`. This allows us to trigger deployments via ChatOps or API.

```yaml
# .github/workflows/deploy.yml
name: Deploy to K8s

on:
  deployment: # Triggered by API or ChatOps

jobs:
  canary-deploy:
    runs-on: ubuntu-latest
    environment: 
      name: production # Uses production secrets & protection rules
      url: https://api.example.com
    
    steps:
      - name: Update Deployment Status to In Progress
        uses: bobheadxi/deployments@v1
        with:
          step: start
          token: ${{ secrets.GITHUB_TOKEN }}
          env: production

      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Deploy Canary (10%)
        run: |
          # 模擬 Helm 部署指令
          # helm upgrade --install payment-service ./charts --set canary.enabled=true
          echo "Deploying Canary version..."
          sleep 10

      - name: Health Check (Integration Test)
        id: health_check
        run: |
          # 呼叫監控 API 確認錯誤率
          # curl -f https://monitoring.internal/check?service=payment
          echo "Health check passed."

      - name: Promote to Full (100%)
        if: success()
        run: |
          echo "Promoting to 100% traffic..."

      - name: Update Deployment Status (Success)
        if: success()
        uses: bobheadxi/deployments@v1
        with:
          step: finish
          token: ${{ secrets.GITHUB_TOKEN }}
          status: success
          env: production

      - name: Update Deployment Status (Failure)
        if: failure()
        uses: bobheadxi/deployments@v1
        with:
          step: finish
          token: ${{ secrets.GITHUB_TOKEN }}
          status: failure
          env: production
```

### 步驟 3: 透過 API 觸發部署 (Step 3: Trigger Deployment via API)

資深工程師或 Release Tool 可以透過 `curl` 觸發這個流程：

A Senior Engineer or Release Tool can trigger this workflow via `curl`:

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/my-org/payment-service/deployments \
  -d '{
    "ref": "main",
    "environment": "production",
    "required_contexts": [], 
    "payload": { "strategy": "canary" },
    "description": "Deploying v1.2.0 via API"
  }'
```

**分析 (Analysis)**:
-   **複雜度**: 我們將部署邏輯封裝在 Workflow 中，但觸發權限交由 API 控制。
-   **狀態同步**: Workflow 中的 `bobheadxi/deployments` (或直接呼叫 API) 確保了 GitHub UI 上的狀態與實際 K8s 狀態一致。

**Analysis**:
-   **Complexity**: We encapsulate deployment logic within the Workflow, but trigger authority is controlled via API.
-   **State Synchronization**: The `bobheadxi/deployments` action (or direct API calls) in the Workflow ensures the status in GitHub UI matches the actual K8s state.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 `workflow_dispatch` 進行生產部署 (Misusing `workflow_dispatch` for Production)

-   **錯誤 (Pitfall)**: 依賴手動點擊 `workflow_dispatch` 按鈕來部署 Production，且沒有連結到 GitHub Environments。
-   **為何不好 (Why it's bad)**: 缺乏 Audit Trail（誰點的？批准了嗎？），且無法利用 Protection Rules 強制 Review。此外，這使得自動化工具難以介入。
-   **修正 (Fix)**: 應使用 `deployment` 事件或將 `workflow_dispatch` 連結到 Environment，確保規則生效。

-   **Pitfall**: Relying on manually clicking the `workflow_dispatch` button to deploy Production without linking to GitHub Environments.
-   **Why it's bad**: Lacks an Audit Trail (who clicked it? was it approved?), and cannot enforce Protection Rules like mandatory reviews. It also makes it hard for automation tools to intervene.
-   **Fix**: Use the `deployment` event or link `workflow_dispatch` to an Environment to ensure rules are enforced.

### 5.2 忽略並發部署問題 (Ignoring Concurrent Deployments)

-   **錯誤 (Pitfall)**: 當一個部署正在進行（例如 Canary 等待期），另一個 Commit 被觸發部署。
-   **為何不好 (Why it's bad)**: 可能導致 Race Condition，例如舊版本的部署覆蓋了新版本，或 Terraform state 鎖定衝突。
-   **修正 (Fix)**: 在 GitHub Actions 中使用 `concurrency` group，設定 `cancel-in-progress: false` (排隊) 或 `true` (取消舊的)，視策略而定。

-   **Pitfall**: Another commit triggers a deployment while one is already in progress (e.g., during a Canary wait period).
-   **Why it's bad**: Can lead to Race Conditions, such as an old version overwriting a new one, or Terraform state lock conflicts.
-   **Fix**: Use `concurrency` groups in GitHub Actions, setting `cancel-in-progress: false` (queue) or `true` (cancel old), depending on the strategy.

### 5.3 狀態回報不完整 (Incomplete Status Reporting)

-   **錯誤 (Pitfall)**: Workflow 失敗了，但沒有呼叫 API 更新 Deployment Status 為 `failure`。
-   **為何不好 (Why it's bad)**: GitHub UI 會一直顯示 "Pending" 或 "In Progress"，誤導開發者，且會卡住依賴該狀態的後續自動化流程。
-   **修正 (Fix)**: 使用 `if: always()` 或 `try/catch` 區塊確保無論成功失敗，都會發送最終狀態。

-   **Pitfall**: The Workflow fails, but does not call the API to update the Deployment Status to `failure`.
-   **Why it's bad**: GitHub UI will perpetually show "Pending" or "In Progress", misleading developers and blocking subsequent automation that relies on that status.
-   **Fix**: Use `if: always()` or `try/catch` blocks to ensure a final status is sent regardless of success or failure.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何設計一個支援 "One-Click Rollback" 的系統？
**How would you design a system that supports "One-Click Rollback"?**

*   **高分回答要點 (Key Points)**:
    *   **不可變性 (Immutability)**: 每次部署都應產生唯一的 Artifact (Docker Image Tag / Helm Chart Version)。
    *   **GitHub API 應用**: Rollback 本質上是「重新部署舊的 Commit/Tag」。
    *   **流程**: 前端/CLI 呼叫 Deployments API -> 指定舊的 `ref` -> GitHub Actions 執行標準部署流程。
    *   **資料庫考量**: 提及 DB schema 的向後相容性 (Backward Compatibility) 是 Rollback 成功的關鍵前提。

*   **Key Points**:
    *   **Immutability**: Every deployment should produce a unique Artifact (Docker Image Tag / Helm Chart Version).
    *   **GitHub API Usage**: A rollback is essentially "re-deploying an old Commit/Tag".
    *   **Flow**: Frontend/CLI calls Deployments API -> specifies old `ref` -> GitHub Actions executes standard deployment workflow.
    *   **Database Considerations**: Mention that DB schema backward compatibility is a prerequisite for successful rollbacks.

### Q2: 在微服務架構中，如何管理數十個 Repo 的 Environment Secrets？
**In a microservice architecture, how do you manage Environment Secrets across dozens of Repos?**

*   **高分回答要點 (Key Points)**:
    *   **反模式**: 手動在每個 Repo 的 UI 設定 Secret 是不可維護的。
    *   **Organization Secrets**: 將通用 Secret 設在 Org 層級並分享給特定 Repos。
    *   **外部 Secret Store**: 推薦使用 HashiCorp Vault 或 AWS Secrets Manager。GitHub Action 僅需持有 OIDC Token (Identity)，在 Runtime 動態去外部 Store 抓取 Secret，而非將 Secret 靜態存在 GitHub。

*   **Key Points**:
    *   **Anti-pattern**: Manually setting secrets in the UI for each Repo is unmaintainable.
    *   **Organization Secrets**: Set common secrets at the Org level and share with specific Repos.
    *   **External Secret Store**: Recommend using HashiCorp Vault or AWS Secrets Manager. GitHub Actions should only hold an OIDC Token (Identity) and fetch secrets dynamically from the external store at runtime, rather than storing secrets statically in GitHub.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點 (Key Takeaways)
1.  **Environments 是治理核心**：利用 Protection Rules 強制執行 Code Review 與部署審核。
2.  **Deployments API 是整合關鍵**：透過 API 將 GitHub 轉變為部署控制平面，解耦觸發意圖與執行細節。
3.  **狀態回報至關重要**：確保 Workflow 能夠正確處理成功與失敗的狀態回報，維持可觀測性。
4.  **安全性最佳實踐**：使用 Environment Secrets 與 OIDC 整合，避免長期憑證洩漏。

1.  **Environments are Governance Core**: Use Protection Rules to enforce Code Reviews and deployment approvals.
2.  **Deployments API is Integration Key**: Transform GitHub into a deployment control plane via API, decoupling trigger intent from execution details.
3.  **Status Reporting is Critical**: Ensure Workflows correctly handle success/failure status reporting to maintain observability.
4.  **Security Best Practices**: Use Environment Secrets and OIDC integration to avoid long-lived credential leakage.

### 後續延伸 (Next Steps)
-   **GitHub Actions 自託管 Runner (Self-hosted Runners)**: 學習如何在私有網路（VPC）內執行部署 Job，進一步提升安全性。（對應下一章節：Security & Compliance）。
-   **GitOps (ArgoCD/Flux)**: 比較 Push-based (GitHub Actions 直接部署) 與 Pull-based (ArgoCD 監聽 Git 變更) 的差異與整合方式。

-   **GitHub Actions Self-hosted Runners**: Learn how to run deployment jobs within a private network (VPC) to further enhance security. (Corresponds to next chapter: Security & Compliance).
-   **GitOps (ArgoCD/Flux)**: Compare Push-based (GitHub Actions deploys directly) vs. Pull-based (ArgoCD listens for Git changes) approaches and their integration.