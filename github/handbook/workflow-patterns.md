# 分支策略與工作流模式 / Branching Strategies & Workflow Patterns

## Mental model｜心智模型

在 GitHub 上設計工作流時，不應只將分支（Branch）視為程式碼的容器，而應將其視為 **「信任層級的閘門」（Trust Gates）**。

### 1. The Integration Highway (整合高速公路)
想像 `main` 分支是一條高速公路。你的目標是讓車輛（Commits）快速且安全地匯入主幹道，而不是在路邊（Feature Branch）停太久。
- **GitHub Flow** 的本質是：`main` 隨時可部署（Deployable）。
- **Pull Request (PR)** 不是單純的合併請求，而是一個 **「品質控制站」（Quality Control Station）**。在這裡，我們執行自動化測試（CI）、程式碼審查（Code Review）與安全掃描。

### 2. Shift Left on Feedback (回饋左移)
傳統模式是在合併後才發現問題；現代 GitHub 工作流強調在 PR 階段（甚至 Commit 階段）就攔截錯誤。
- **Branch Protection Rules** 是強制執行的合約，確保沒有人（包含管理員）能繞過品質控制站。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. GitHub Flow (The Default Standard)
適用於大部分 Web 應用與持續部署（CD）場景。
- **規則**：
  - `main` 分支永遠保持穩定。
  - 所有新功能都在從 `main` 切出的短分支（Short-lived branches）上開發。
  - 透過 Pull Request 合併回 `main`。
  - 合併即部署（或觸發部署流程）。
- **實作關鍵**：開啟 **"Require pull request reviews before merging"**。

### 2. Scaled Trunk-Based Development (TBD)
適用於大型團隊或 Monorepo，強調極短的開發週期。
- **核心**：開發者每天多次將程式碼合併回主幹（Trunk/Main）。
- **Feature Flags**：未完成的功能透過 Feature Toggles 隱藏，而不是透過長期的 Feature Branch 隔離。這樣可以避免大規模的 Merge Conflict。
- **GitHub 設定**：使用 **Merge Queue** (GitHub Enterprise 功能) 來序列化高頻率的合併請求，確保並發的 PR 不會破壞主幹。

### 3. Strict Branch Protection Strategy (嚴格分支保護策略)
不要依賴口頭約定，使用 GitHub 的硬性規則：
- **Require status checks to pass before merging**：必須綁定 CI (GitHub Actions)。
- **Require branches to be up to date before merging**：防止 "Logical Conflicts"（雖然程式碼沒衝突，但邏輯上舊的 PR 蓋掉了新的修改）。
- **Code Owners**：在 `.github/CODEOWNERS` 定義誰負責審核哪些目錄，強制特定專家 Review 關鍵模組（如 `/security` 或 `/billing`）。

### 4. Semantic Commits & Linear History
- **Squash and Merge**：在 GitHub PR 介面設定預設使用 "Squash and Merge"。這會將 PR 中的數十個雜亂 Commits 壓縮成一個乾淨的 Commit 進入 `main`。
- **Linear History**：保持主幹歷史像一條直線，方便 `git bisect` 排查問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Mega PR" (巨型 PR)
- **現象**：一個 PR 包含 50+ 個檔案變更，混合了 Refactoring、新功能與 Bug fix。
- **後果**：Reviewer 無法有效審查，只能盲目 Approve；CI 跑很久；一旦出錯難以 Revert。
- **解法**：使用 **Stacked PRs** 技巧，將大功能拆解為多個相依的小 PR（PR1 基礎建設 -> PR2 核心邏輯 -> PR3 UI 實作）。

### 2. Long-Lived Feature Branches (長壽分支)
- **現象**：分支存活超過 3 天未合併。
- **後果**：與 `main` 脫節嚴重，合併時產生 "Merge Hell"。
- **解法**：頻繁 Rebase `main`，或者改用 Feature Flags 提早合併。

### 3. Gitflow in 2024 (過度工程化的 Gitflow)
- **現象**：堅持使用 `develop`, `release/*`, `hotfix/*`, `feature/*` 等複雜結構，但團隊只有 5 人且做的是 SaaS 產品。
- **後果**：流程繁瑣，`develop` 與 `main` 經常不同步，部署速度變慢。
- **建議**：除非你是發布「版本號軟體」（如手機 App 或桌面軟體），否則請優先選擇 GitHub Flow 或 TBD。

### 4. Ignoring "Require branches to be up to date"
- **陷阱**：CI 在分支建立時通過了，但 `main` 已經前進了。直接合併可能導致 CI 在 `main` 上失敗（Broken Trunk）。
- **解法**：在 Branch Protection Rules 中勾選此選項，強迫 PR 在合併前必須包含 `main` 的最新變更。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing a Strategy
- **Q1: Do you release multiple times a day? (Web/SaaS)**
  - Yes -> **GitHub Flow** or **Trunk-Based Development**.
  - No (Scheduled Releases/App Store) -> Consider a simplified **Release Branching** strategy.
- **Q2: Do you have 20+ developers on the same repo?**
  - Yes -> **Trunk-Based** with **Feature Flags** and **Merge Queue**.
  - No -> **GitHub Flow** is sufficient.

### Workflow: Setting up "Production-Grade" Branch Protection
請對照你的 GitHub Repository Settings 檢查：

- [ ] **Branch name pattern**: `main`
- [ ] **Require a pull request before merging**:
    - [ ] Require approvals: `1` (or `2` for critical repos).
    - [ ] Dismiss stale pull request approvals when new commits are pushed.
    - [ ] Require review from Code Owners.
- [ ] **Require status checks to pass before merging**:
    - [ ] Select your CI job (e.g., `build`, `test`, `lint`).
    - [ ] **Require branches to be up to date before merging** (Crucial!).
- [ ] **Require conversation resolution before merging**: 確保所有 Comments 都被處理。
- [ ] **Include administrators**: 勾選此項，確保管理員也不能繞過規則（避免手滑）。

### Workflow: The Developer's Daily Loop
1.  `git checkout main` & `git pull`
2.  `git checkout -b feature/my-task`
3.  Coding... Commit...
4.  **Before Pushing**: `git fetch origin main` & `git rebase origin/main` (Keep history clean).
5.  Push & Open PR.
6.  CI Checks Pass (Green).
7.  Code Review (Address comments).
8.  Merge (Squash).
9.  Delete Branch.

---

## Real-world examples｜實戰案例

### Scenario 1: The Fast-Paced SaaS Startup (GitHub Flow)
*情境：一個 React 前端 + Node.js 後端的團隊，每天部署多次。*

- **Branching**: 只有 `main` 和短期的 `feature/*` 分支。
- **Automation**:
  - 開 PR -> 觸發 Vercel Preview Deployment（每個 PR 都有獨立預覽網址）。
  - Merge to `main` -> 自動部署到 Production。
- **Protection**: 只需要 1 個 Approval，但 CI (Lint/Test) 必須全過。
- **優勢**: 速度極快，開發者對 Production 負責。

### Scenario 2: The Regulated Fintech App (Compliance Heavy)
*情境：涉及金流，需要稽核與嚴格控管。*

- **Branching**: 使用 Release Branches (`release/v1.2`) 來控管發布版本。
- **Access Control**:
  - 使用 `.github/CODEOWNERS`：
    ```text
    /migrations  @org/db-admins
    /payments    @org/security-team
    ```
  - 任何涉及資料庫遷移的 PR，必須由 DB Team 核准。
- **Protection**:
  - Require **Signed Commits** (GPG/SSH signature) 驗證開發者身分。
  - Require **2 Approvals**。
  - 禁止 Force Push。
- **優勢**: 安全性高，變更可追溯，符合合規要求。

### Scenario 3: Handling Hotfixes
*情境：Production 出現 Critical Bug，但 `main` 上已經有正在開發中的新功能代碼。*

1.  從 `main` 的 **上一個穩定 Tag** (e.g., `v1.0.0`) 切出 `hotfix/v1.0.1` 分支。
2.  修復 Bug，通過測試。
3.  將 `hotfix` 分支部署到 Production。
4.  **關鍵步驟**：將 `hotfix` 分支 **同時** Merge 回 `main`（或是 Cherry-pick），確保修復不會在下一次發布時被覆蓋。