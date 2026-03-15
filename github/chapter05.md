# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，GitHub 不僅僅是一個存放程式碼的倉庫，它是團隊協作的法律與治理中心。隨著團隊規模擴大，依賴口頭約定（"請記得找我 review" 或 "不要直接 push 到 main"）是不可擴展且危險的。本章將探討如何透過 GitHub 的原生機制，將開發流程中的「人治」轉變為「法治」。

In a Senior Engineer's career, GitHub is not just a repository for code; it is the center of law and governance for team collaboration. As teams scale, relying on verbal agreements ("Please remember to ask me for a review" or "Don't push directly to main") is unscalable and dangerous. This chapter explores how to transform the development process from "rule by man" to "rule of law" using GitHub's native mechanisms.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作精確的權責歸屬 (Implement Precise Ownership):** 利用 `CODEOWNERS` 檔案自動指派正確的 Reviewers，解決 Monorepo 或大型專案中的權責不清問題。
    Use the `CODEOWNERS` file to automatically assign the correct Reviewers, solving ownership ambiguity in Monorepos or large projects.
2.  **強制執行品質閘門 (Enforce Quality Gates):** 設定 Branch Protection Rules，確保所有程式碼在合併前都經過 CI 測試與必要的人員審核。
    Configure Branch Protection Rules to ensure all code undergoes CI testing and mandatory human review before merging.
3.  **保護部署環境 (Protect Deployment Environments):** 運用 Environment Protection Rules 建立部署前的審核機制（Approval Gates），防止未經授權的變更進入 Production。
    Apply Environment Protection Rules to establish pre-deployment Approval Gates, preventing unauthorized changes from reaching Production.
4.  **理解合規性影響 (Understand Compliance Impact):** 解釋這些機制如何協助滿足 SOC2 或 ISO 27001 等資安合規要求（如職責分離 SoD）。
    Explain how these mechanisms help meet security compliance requirements like SOC2 or ISO 27001 (e.g., Segregation of Duties).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要掌握團隊治理，我們需要建立以下的心智模型，將 GitHub 的功能對應到組織管理的實體概念。

To master team governance, we need to establish the following mental models, mapping GitHub features to physical concepts in organizational management.

### 2.1 CODEOWNERS：程式碼的「RACI 矩陣」
### 2.1 CODEOWNERS: The "RACI Matrix" of Code

`CODEOWNERS` 檔案就像專案管理的 **RACI 矩陣**（Responsible, Accountable, Consulted, Informed）。它定義了誰對檔案庫中的特定路徑「負責」。
The `CODEOWNERS` file is like the **RACI matrix** (Responsible, Accountable, Consulted, Informed) in project management. It defines who is "responsible" for specific paths in the repository.

*   **定義 (Definition):** 一個位於 `.github/` 或根目錄下的特定格式檔案，將檔案路徑映射到 GitHub 使用者或團隊。
    A specifically formatted file located in `.github/` or the root directory that maps file paths to GitHub users or teams.
*   **行為 (Behavior):** 當有人發起 Pull Request (PR) 修改了特定檔案，GitHub 會自動將對應的 Owner 加入 Reviewers 列表。
    When a Pull Request (PR) modifies specific files, GitHub automatically adds the corresponding Owners to the Reviewers list.

### 2.2 Branch Protection Rules：合併前的「守門員」
### 2.2 Branch Protection Rules: The "Gatekeeper" Before Merging

如果 `main` branch 是金庫，Branch Protection Rules 就是金庫前的**守衛與安檢系統**。它不關心程式碼內容是什麼，它只關心「程序」是否合規。
If the `main` branch is a vault, Branch Protection Rules are the **guards and security screening systems** in front of it. It doesn't care what the code content is; it only cares if the "process" is compliant.

*   **關鍵控制 (Key Controls):**
    *   **Require pull request reviews:** 禁止直接 Push，必須透過 PR。
        Prohibits direct Pushes; must go through a PR.
    *   **Require status checks to pass:** 必須通過 CI (Continuous Integration) 測試。
        Must pass CI (Continuous Integration) tests.
    *   **Require conversation resolution:** 所有討論串必須被解決（Resolved）。
        All conversation threads must be resolved.

### 2.3 Environment Protection Rules：部署的「發射鑰匙」
### 2.3 Environment Protection Rules: The "Launch Keys" for Deployment

這與 Branch Protection 不同。Branch Protection 保護的是 **Code (Git Ref)**，而 Environment Protection 保護的是 **Runtime Target (Deployment Environment)**。
This differs from Branch Protection. Branch Protection guards the **Code (Git Ref)**, while Environment Protection guards the **Runtime Target (Deployment Environment)**.

*   **場景 (Scenario):** 即使程式碼已經合併到 `main`，要部署到 `Production` 環境時，可能仍需要 Engineering Manager 或 QA Lead 的額外批准。
    Even if the code is merged to `main`, deploying to the `Production` environment might still require explicit approval from an Engineering Manager or QA Lead.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統或微服務架構中，這些治理機制直接影響系統的穩定性與安全性。

In large-scale distributed systems or microservices architectures, these governance mechanisms directly impact system stability and security.

### 3.1 Monorepo 架構中的治理
### 3.1 Governance in Monorepo Architecture

在一個包含 Backend (Go), Frontend (React), 和 Infrastructure (Terraform) 的 Monorepo 中，你不會希望 Frontend 工程師意外修改了資料庫的 Terraform 設定檔並直接合併。

In a Monorepo containing Backend (Go), Frontend (React), and Infrastructure (Terraform), you don't want a Frontend engineer accidentally modifying database Terraform configs and merging them directly.

*   **設計 (Design):** 利用 `CODEOWNERS` 進行領域隔離。
    Use `CODEOWNERS` for domain isolation.
    *   `/infra/` -> owned by `@org/sre-team`
    *   `/backend/` -> owned by `@org/backend-leads`
    *   `/frontend/` -> owned by `@org/frontend-leads`
*   **Branch Protection:** 設定 "Require review from Code Owners"。這意味著，如果我改了 `/infra`，隨便找個後端同事 approve 是無效的，必須由 SRE team 成員 approve 才能合併。
    Configure "Require review from Code Owners". This means if I change `/infra`, getting an approval from a random backend colleague is invalid; it *must* be approved by an SRE team member to merge.

### 3.2 合規性與職責分離 (Compliance & Segregation of Duties)
### 3.2 Compliance & Segregation of Duties

對於 Fintech 或 Healthtech 公司，SOC2 或 ISO 27001 要求證明「開發者不能未經審核直接部署程式碼」。

For Fintech or Healthtech companies, SOC2 or ISO 27001 requires proof that "developers cannot deploy code directly without review."

*   **實作 (Implementation):**
    1.  **Branch Protection:** 鎖定 `main`，強制 PR review。
        Lock `main`, enforce PR reviews.
    2.  **Environment Protection:** 在 GitHub Actions Workflow 中參照 Environment。若該 Environment 設定了 "Required Reviewers"，部署 Job 會暫停，直到授權人員點擊批准。
        Reference an Environment in the GitHub Actions Workflow. If that Environment has "Required Reviewers" configured, the deployment Job will pause until authorized personnel click approve.

---

# 4. 逐步示例 (Walkthrough / Example)

假設我們正在管理一個名為 `payment-service` 的儲存庫，我們需要建立嚴格的 Code Review 流程。

Let's assume we are managing a repository named `payment-service`, and we need to establish a strict Code Review process.

### 步驟 1: 設定 CODEOWNERS (Setting up CODEOWNERS)

在 `.github/CODEOWNERS` 建立以下內容。注意由上而下的優先級（後面的規則覆蓋前面的）。

Create the following content in `.github/CODEOWNERS`. Note the top-down priority (later rules override earlier ones).

```gitignore
# .github/CODEOWNERS

# Default: The engineering team owns everything
# 預設：整個工程團隊擁有所有權
*       @my-org/engineering

# Infrastructure configs require SRE review
# 基礎設施設定需要 SRE 審核
/terraform/   @my-org/sre
/.github/     @my-org/sre

# Database migrations require DB Admin review
# 資料庫遷移腳本需要 DBA 審核
/migrations/  @my-org/dba

# Security sensitive files
# 安全敏感檔案
/auth/        @my-org/security-team
```

### 步驟 2: 設定 Branch Protection Rules (Configuring Branch Protection Rules)

前往 Repo `Settings` -> `Branches` -> `Add rule` (針對 `main`)：

Go to Repo `Settings` -> `Branches` -> `Add rule` (for `main`):

1.  **Check:** `Require a pull request before merging`
2.  **Check:** `Require approvals` (設定為 1 或 2)
3.  **Critical Check:** `Require review from Code Owners`
    *   *解釋:* 這啟用了 `CODEOWNERS` 的強制力。如果沒有勾選此項，`CODEOWNERS` 只是自動加人進來，但他們的 Approval 不是必須的。
    *   *Explanation:* This enables the enforcement of `CODEOWNERS`. Without this checked, `CODEOWNERS` only automatically adds people, but their Approval is not mandatory.
4.  **Check:** `Require status checks to pass before merging`
    *   搜尋並選取你的 CI Job 名稱（例如 `ci/circleci: test`, `build (github-actions)`）。
    *   Search and select your CI Job names (e.g., `ci/circleci: test`, `build (github-actions)`).

### 步驟 3: 設定 Environment Protection (Configuring Environment Protection)

前往 Repo `Settings` -> `Environments` -> `New environment` (命名為 `production`)：

Go to Repo `Settings` -> `Environments` -> `New environment` (name it `production`):

1.  **Check:** `Required reviewers`
    *   新增 `@my-org/tech-leads` 或特定資深人員。
    *   Add `@my-org/tech-leads` or specific senior personnel.
2.  **Deployment Branch Policy:**
    *   限制只有 `main` branch 可以部署到此環境。
    *   Restrict that only the `main` branch can deploy to this environment.

**GitHub Actions Workflow 範例:**
**GitHub Actions Workflow Example:**

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production  # This triggers the protection rules
    steps:
      - uses: actions/checkout@v3
      - run: ./deploy.sh
```

當此 Job 執行時，它會進入 "Waiting" 狀態，直到 Reviewer 在 GitHub UI 上批准。
When this Job runs, it will enter a "Waiting" state until a Reviewer approves it in the GitHub UI.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 擁有權過於廣泛 (Broad Ownership / Alert Fatigue)
*   **錯誤 (Mistake):** 將根目錄 `*` 指派給 `@org/everyone` 或一個包含 50 人的大群組。
    Assigning the root directory `*` to `@org/everyone` or a large group of 50 people.
*   **後果 (Consequence):** 每一個 PR 都會通知所有人。結果就是「警報疲勞 (Alert Fatigue)」，大家都會忽略通知，導致無人真正負責 Review。
    Every PR notifies everyone. The result is "Alert Fatigue," where everyone ignores notifications, leading to no one actually reviewing.
*   **修正 (Fix):** 保持 `CODEOWNERS` 顆粒度適中。根目錄可以留空或指派給核心維護者，具體目錄指派給具體 Feature Team。
    Keep `CODEOWNERS` granularity moderate. The root can be left empty or assigned to core maintainers, while specific directories are assigned to specific Feature Teams.

### 5.2 忽略 "Require branches to be up to date" (Ignoring "Require branches to be up to date")
*   **錯誤 (Mistake):** 在 Branch Protection 中未勾選此項。
    Not checking this option in Branch Protection.
*   **後果 (Consequence):** 雖然通過了 CI，但在合併時 `main` 可能已經前進了。這會導致「語意衝突 (Semantic Conflict)」——程式碼沒有 Git 衝突，但邏輯上壞掉了（例如別人改了函數簽名，你的分支還在用舊的）。
    Even if CI passes, `main` might have moved forward by the time of merge. This leads to "Semantic Conflicts"—no Git conflicts, but logic is broken (e.g., someone changed a function signature, and your branch is still using the old one).
*   **修正 (Fix):** 勾選此項，強制 PR 必須包含 `main` 的最新變更才能合併（GitHub 提供 "Update branch" 按鈕）。
    Check this option to force PRs to include the latest changes from `main` before merging (GitHub provides an "Update branch" button).

### 5.3 管理員特權濫用 (Abuse of Admin Privileges)
*   **錯誤 (Mistake):** 勾選 `Do not allow bypassing the above settings` 但 Admin 習慣性地為了方便而自行解鎖合併。
    Checking `Do not allow bypassing the above settings` but Admins habitually unlock and merge for convenience.
*   **後果 (Consequence):** 破壞了審計軌跡 (Audit Trail)，並使保護規則形同虛設。
    Destroys the Audit Trail and renders protection rules useless.
*   **修正 (Fix):** 即使是 Admin/Principal Engineer，也應遵守 "Enforce all configured restrictions for administrators"。只有在 Production 失火的極端緊急情況下才使用 Bypass。
    Even Admins/Principal Engineers should adhere to "Enforce all configured restrictions for administrators". Bypass should only be used in extreme emergencies like a Production fire.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在緊急修復 (Hotfix) 情境下，嚴格的 Branch Protection 會阻礙發布速度，你會如何設計流程？
### Q1: In a Hotfix scenario, strict Branch Protection can hinder release speed. How would you design the process?

*   **高分回答要點 (Key Points):**
    *   不建議完全移除保護規則。
    *   可以設立一個特殊的 `hotfix/*` 分支策略，或使用 GitHub 的 "Bypass branch protections" 權限，但必須限制在極少數資深人員（如 Tech Lead/Manager）身上。
    *   強調 **Post-mortem (事後檢討)**：每次 Bypass 都必須記錄原因並在事後補上測試或 Review。
    *   Do not recommend removing protection rules entirely.
    *   Establish a special `hotfix/*` branch strategy, or use GitHub's "Bypass branch protections" permission, but restrict it to a very few senior roles (e.g., Tech Lead/Manager).
    *   Emphasize **Post-mortem**: Every bypass must be documented, and tests or reviews must be backfilled afterwards.

### Q2: 如何處理 Monorepo 中跨團隊的依賴修改？
### Q2: How do you handle cross-team dependency changes in a Monorepo?

*   **高分回答要點 (Key Points):**
    *   利用 `CODEOWNERS` 強制相關團隊 Review。
    *   如果我修改了 Shared Library，`CODEOWNERS` 應該自動加入依賴該 Library 的所有團隊作為 Reviewer（這可能導致噪音），或者更佳的做法是：加入一個核心架構團隊 (Core/Platform Team) 來審核 Shared Code。
    *   提及 **Automated Impact Analysis**：進階做法是在 CI 中偵測依賴圖，只對受影響的服務執行測試。
    *   Use `CODEOWNERS` to enforce reviews from relevant teams.
    *   If I modify a Shared Library, `CODEOWNERS` might automatically add all teams depending on it (which causes noise), or better: add a Core/Platform Team to review Shared Code.
    *   Mention **Automated Impact Analysis**: Advanced practice involves detecting the dependency graph in CI and running tests only for affected services.

### Q3: `CODEOWNERS` 的語法陷阱有哪些？
### Q3: What are the syntax pitfalls of `CODEOWNERS`?

*   **高分回答要點 (Key Points):**
    *   **沒有 Inline Comments**：行尾不能加註解，會導致該行失效。
    *   **路徑格式**：`/build/logs/` (目錄) vs `build/logs` (檔案或目錄) 的差異。
    *   **優先級**：檔案底部的規則會覆蓋頂部的規則。
    *   **No Inline Comments**: You cannot add comments at the end of a line; it invalidates the rule.
    *   **Path Format**: The difference between `/build/logs/` (directory) vs `build/logs` (file or directory).
    *   **Priority**: Rules at the bottom of the file override rules at the top.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **CODEOWNERS** 是將組織架構映射到程式碼庫的路由表 (Routing Table)，而非單純的建議名單。
    **CODEOWNERS** is a Routing Table mapping organizational structure to the codebase, not just a suggestion list.
2.  **Branch Protection** 保護程式碼完整性 (Code Integrity)，強制執行 CI 與 Peer Review。
    **Branch Protection** guards Code Integrity, enforcing CI and Peer Review.
3.  **Environment Protection** 保護部署目標 (Deployment Target)，實作部署審批閘門。
    **Environment Protection** guards Deployment Targets, implementing deployment approval gates.
4.  啟用 **"Require review from Code Owners"** 是讓 `CODEOWNERS` 具有強制力的關鍵開關。
    Enabling **"Require review from Code Owners"** is the critical switch to make `CODEOWNERS` enforceable.
5.  治理是為了**規模化 (Scale)**：自動化規則減少了人為溝通成本與錯誤。
    Governance is for **Scale**: Automated rules reduce human communication costs and errors.

### 後續延伸 (Next Steps)
*   **GitHub Actions (CI/CD):** 深入研究如何撰寫 Reusable Workflows，並結合 Environment Protection 實現自動化部署管線。
    **GitHub Actions (CI/CD):** Dive deep into writing Reusable Workflows and combining them with Environment Protection to achieve automated deployment pipelines.
*   **GitHub Advanced Security:** 學習如何整合 Code Scanning (CodeQL) 與 Secret Scanning 到 Branch Protection 規則中，將資安左移 (Shift Left)。
    **GitHub Advanced Security:** Learn how to integrate Code Scanning (CodeQL) and Secret Scanning into Branch Protection rules, shifting security left.