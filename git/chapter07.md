# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Git 不僅僅是版本控制工具，更是團隊溝通與自動化流程的基石。本章將焦點從「如何操作 Git 指令」轉移至「如何建立高效率的 Git 協作文化」。我們將探討如何透過規範化的 Commit Message 驅動 CI/CD，以及如何透過專業的 Code Review (CR) 流程與衝突解決策略，降低技術債並提升交付速度。

For senior engineers, Git is not merely a version control tool but the cornerstone of team communication and automation workflows. This chapter shifts the focus from "how to use Git commands" to "how to establish a high-efficiency Git collaboration culture." We will explore how to drive CI/CD through standardized Commit Messages, and how to reduce technical debt and accelerate delivery through professional Code Review (CR) processes and conflict resolution strategies.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作 Conventional Commits**：理解並應用語意化提交規範，以支援自動化版號管理與 Changelog 生成。
    **Implement Conventional Commits**: Understand and apply semantic commit standards to support automated versioning and Changelog generation.
2.  **優化 Code Review 流程**：區分「阻擋性問題」與「建議性優化」，並建立健康的 CR 禮儀以避免團隊摩擦。
    **Optimize the Code Review Process**: Distinguish between "blocking issues" and "suggestions," and establish healthy CR etiquette to avoid team friction.
3.  **掌握進階衝突解決策略**：運用 `git rerere` 與互動式 Rebase 處理複雜的合併衝突，保持主線歷史乾淨。
    **Master Advanced Conflict Resolution Strategies**: Use `git rerere` and interactive rebase to handle complex merge conflicts while keeping the main history clean.
4.  **制定分支策略治理 (Governance)**：針對不同規模的團隊（從新創到 Enterprise），選擇合適的 Merge Strategy（Squash vs. Merge Commit）。
    **Define Branch Strategy Governance**: Choose the appropriate Merge Strategy (Squash vs. Merge Commit) for teams of different sizes (from startups to enterprises).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Git 歷史即文檔 (Git History as Documentation)

**概念 (Concept)：**
初階工程師將 Git 視為「存檔點 (Save Point)」；資深工程師將 Git 歷史視為「專案演進的敘事文檔 (Narrative Documentation)」。一個混亂的歷史紀錄會導致 `git bisect` 失效，並增加追蹤 Bug 的認知負擔。

Junior engineers view Git as "Save Points"; senior engineers view Git history as "Narrative Documentation of project evolution." A messy history renders `git bisect` useless and increases the cognitive load when tracking bugs.

**類比 (Analogy)：**
想像 Git Log 是一份醫療病歷或法律合約。
*   **Bad Log**: "Update stuff", "Fix bug", "WIP". (像是醫生只寫「病人不舒服」，對後續治療無效)
*   **Good Log**: "fix(auth): handle expired JWT token gracefully". (精確描述病因與處置，具備可追溯性)

Imagine the Git Log as a medical record or a legal contract.
*   **Bad Log**: "Update stuff", "Fix bug", "WIP". (Like a doctor writing "Patient feels bad"—useless for future treatment.)
*   **Good Log**: "fix(auth): handle expired JWT token gracefully". (Precise description of the cause and action, ensuring traceability.)

## 2.2 語意化提交 (Conventional Commits)

這是一種輕量級的規範，用於在 Commit Message 中加入機器可讀的意義。
This is a lightweight convention to add machine-readable meaning to commit messages.

**結構 (Structure)：**
```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

*   **Type**: `feat` (新功能), `fix` (修補), `docs` (文件), `style` (格式), `refactor` (重構), `perf` (效能), `test` (測試), `chore` (雜項)。
*   **Scope**: 影響範圍（如 `api`, `ui`, `database`）。
*   **Description**: 簡短描述。
*   **Breaking Change**: 在 Footer 或 Type 後加 `!` 標示，對應 SemVer 的 Major version 升級。

## 2.3 Code Review 的雙重漏斗模型 (The Dual-Funnel Model of Code Review)

Code Review 應被視為兩個漏斗的結合：
1.  **機器漏斗 (Machine Funnel)**：Linter, Formatter, Static Analysis, Unit Tests。這些應該在人工 Review 之前自動完成。
2.  **人工漏斗 (Human Funnel)**：架構設計、可讀性、安全性、業務邏輯正確性。

Code Review should be viewed as a combination of two funnels:
1.  **Machine Funnel**: Linter, Formatter, Static Analysis, Unit Tests. These must pass automatically before human review.
2.  **Human Funnel**: Architectural design, readability, security, and business logic correctness.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 驅動自動化發布 (Driving Automated Releases)

在現代 CI/CD 系統（如 GitHub Actions, GitLab CI, Jenkins）中，Git Commit Message 是自動化流程的觸發器。

In modern CI/CD systems (e.g., GitHub Actions, GitLab CI, Jenkins), the Git Commit Message is the trigger for automation workflows.

*   **場景 (Scenario)**：團隊使用 `semantic-release` 工具。
*   **流程 (Flow)**：
    1.  工程師 Push `feat(payment): add stripe integration`。
    2.  CI Pipeline 檢測到 `feat` 類型。
    3.  自動將版號從 `1.4.0` 升級至 `1.5.0` (Minor update)。
    4.  自動生成 `CHANGELOG.md` 並發布 Release Tag。
*   **效益 (Benefit)**：移除了人工管理版號的風險，確保版號與實際程式碼變更嚴格對應。

*   **Scenario**: The team uses `semantic-release`.
*   **Flow**:
    1.  Engineer pushes `feat(payment): add stripe integration`.
    2.  CI Pipeline detects the `feat` type.
    3.  Automatically bumps version from `1.4.0` to `1.5.0` (Minor update).
    4.  Automatically generates `CHANGELOG.md` and publishes the Release Tag.
*   **Benefit**: Removes the risk of manual version management and ensures strict alignment between version numbers and actual code changes.

## 3.2 Monorepo 的變更偵測 (Change Detection in Monorepos)

在大型 Monorepo (如使用 Nx, Turborepo, Bazel) 中，精確的 Commit Scope 至關重要。

In large Monorepos (e.g., using Nx, Turborepo, Bazel), precise Commit Scopes are critical.

*   **設計視角 (Design View)**：
    如果 Commit Message 是 `fix(cart): update tax calculation`，建置系統可以分析依賴圖 (Dependency Graph)，只重新建置與測試 `cart` 服務及其相依的模組，而不必重新建置整個 `user-service` 或 `inventory-service`。
*   **可擴充性 (Scalability)**：
    隨著專案規模擴大，這種基於 Git 歷史的「受影響分析 (Affected Analysis)」是維持 CI 速度的唯一解法。

*   **Design View**:
    If the commit message is `fix(cart): update tax calculation`, the build system can analyze the Dependency Graph and only rebuild/test the `cart` service and its dependents, without rebuilding the entire `user-service` or `inventory-service`.
*   **Scalability**:
    As the project scales, this "Affected Analysis" based on Git history is the only solution to maintain CI speed.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 整理髒亂的提交歷史 (Cleaning Up Messy Commit History)

**背景 (Context)**：
你在開發一個複雜功能，過程中產生了許多 "wip", "typo", "fix" 的瑣碎 Commits。現在準備發 PR，需要整理成符合規範的歷史。

**Context**:
You are developing a complex feature, resulting in many trivial commits like "wip", "typo", "fix". Now you are ready to open a PR and need to organize the history to meet standards.

**原始狀態 (Initial State)**：
```text
a1b2c3d wip: start implementing auth
e5f6g7h fix typo in user model
i9j0k1l wip: working on login logic
m2n3o4p fix: login works now
```

**步驟 1：啟動互動式 Rebase (Step 1: Start Interactive Rebase)**
假設我們要整理最近 4 個 commits：
Assuming we want to organize the last 4 commits:

```bash
git rebase -i HEAD~4
```

**步驟 2：編輯 Rebase 腳本 (Step 2: Edit Rebase Script)**
編輯器會打開如下內容。我們將使用 `squash` (或 `fixup`) 來合併瑣碎變更，並用 `reword` 修改訊息。

The editor opens the following. We will use `squash` (or `fixup`) to merge trivial changes and `reword` to modify the message.

```text
# Before
pick a1b2c3d wip: start implementing auth
pick e5f6g7h fix typo in user model
pick i9j0k1l wip: working on login logic
pick m2n3o4p fix: login works now

# After (Plan)
reword a1b2c3d feat(auth): implement jwt login flow  <-- Rename the first one
fixup e5f6g7h fix typo in user model                 <-- Merge into previous
fixup i9j0k1l wip: working on login logic            <-- Merge into previous
fixup m2n3o4p fix: login works now                   <-- Merge into previous
```

**步驟 3：撰寫最終 Commit Message (Step 3: Write Final Commit Message)**
Git 會提示輸入合併後的訊息。我們採用 Conventional Commits 格式：

Git will prompt for the merged message. We use the Conventional Commits format:

```text
feat(auth): implement jwt login flow

- Added JWT token generation in AuthService
- Updated UserModel to support hashed passwords
- Added /api/login endpoint

Closes #123
```

**結果 (Result)**：
歷史變得乾淨且具備語意，Reviewer 可以一次看懂整個功能的意圖，CI 也能正確識別這是一個 Feature。

The history becomes clean and semantic. Reviewers can understand the intent of the entire feature at a glance, and CI can correctly identify this as a Feature.

## 4.2 使用 `git rerere` 解決重複衝突 (Using `git rerere` for Repetitive Conflicts)

**情境 (Scenario)**：
你正在維護一個長期分支 (Long-lived feature branch)，每次從 `main` rebase 時都會遇到相同的衝突（例如 `config.yaml` 的某幾行）。

**Scenario**:
You are maintaining a long-lived feature branch. Every time you rebase from `main`, you encounter the same conflicts (e.g., specific lines in `config.yaml`).

**解決方案 (Solution)**：啟用 `rerere` (Reuse Recorded Resolution)。
**Solution**: Enable `rerere` (Reuse Recorded Resolution).

```bash
git config --global rerere.enabled true
```

1.  第一次遇到衝突時，手動解決並 commit。Git 會記錄下「衝突前的狀態」與「解決後的狀態」。
    When you encounter the conflict for the first time, resolve it manually and commit. Git records the "pre-conflict state" and the "resolved state".
2.  下次 Rebase 遇到相同區塊的衝突時，Git 會自動應用上次的解決方案，無需人工介入。
    The next time you rebase and hit a conflict in the same block, Git automatically applies the previous resolution without human intervention.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 巨型 PR (The Giant PR)

**錯誤描述 (Description)**：
提交一個包含 50+ 檔案變更、2000+ 行程式碼的 Pull Request。

**Description**:
Submitting a Pull Request containing 50+ file changes and 2000+ lines of code.

**為何不好 (Why it's bad)**：
*   **Review Fatigue**：Reviewer 無法維持專注，傾向於 "LGTM" (Looks Good To Me) 草草通過，導致 Bug 溜進 Production。
*   **Blocking**：只要有一個小問題（如 CSS 樣式），整個功能就被卡住無法合併。

**最佳實踐 (Best Practice)**：
*   **Stacked PRs**：將大功能拆解為多個相依的小 PR（例如：先合 Database Schema，再合 Backend Logic，最後合 Frontend）。
*   **Feature Flags**：允許將未完成的程式碼合併進主線（只要被 Flag 關閉），避免長期分支。

## 5.2 在 Code Review 中爭論格式 (Bikeshedding on Formatting)

**錯誤描述 (Description)**：
資深工程師花時間評論：「這裡應該加個空格」、「這裡縮排不對」。

**Description**:
Senior engineers spending time commenting: "Add a space here", "Indentation is wrong here".

**為何不好 (Why it's bad)**：
這是對昂貴人力資源的浪費。這類問題應由機器解決。

**Why it's bad**:
This is a waste of expensive human resources. Such issues should be solved by machines.

**最佳實踐 (Best Practice)**：
*   配置 Pre-commit hooks (使用 Husky + Lint-staged)。
*   如果 CI 沒過（Lint 失敗），根本不允許發起 Code Review。
*   **Rule**: "If it's not in the linter config, it's not a rule."

## 5.3 依賴 Merge Commit 同步上游 (Syncing Upstream with Merge Commits)

**錯誤描述 (Description)**：
在 Feature branch 上頻繁執行 `git merge main` 來獲取最新變更。

**Description**:
Frequently running `git merge main` on a feature branch to get the latest changes.

**為何不好 (Why it's bad)**：
這會產生大量的 "Merge branch 'main' into feature-xxx" 提交，汙染歷史線，形成 "Guitar Hero" 形狀的混亂線圖。

**Why it's bad**:
This creates numerous "Merge branch 'main' into feature-xxx" commits, polluting the history and creating a messy "Guitar Hero" style graph.

**最佳實踐 (Best Practice)**：
使用 `git rebase main`。這會將你的變更「重播」在最新的 main 之上，保持線圖線性。

**Best Practice**:
Use `git rebase main`. This "replays" your changes on top of the latest main, keeping the graph linear.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 Merge Strategy 的選擇

**問題 (Question)**：
「在 GitHub/GitLab 上合併 PR 時，有 'Create a merge commit', 'Squash and merge', 'Rebase and merge' 三種選項。你會如何為團隊選擇？考量點是什麼？」

"When merging a PR on GitHub/GitLab, there are three options: 'Create a merge commit', 'Squash and merge', and 'Rebase and merge'. How would you choose for your team? What are the considerations?"

**高分回答要點 (Key Points)**：
*   **Squash and merge**：適合大多數 Feature 開發。保持主線乾淨（一個功能 = 一個 Commit），方便 Revert。缺點是會丟失開發過程的詳細歷史。
*   **Merge commit**：適合長期分支合併（如 `develop` 合併回 `main`），保留了「這是一次合併動作」的語意與時間點。
*   **Rebase and merge**：保留所有 Commits 但線性化。適合極度要求原子性提交 (Atomic Commits) 的高紀律團隊，但若中間有壞 Commit，Bisect 會很痛苦。
*   **結論**：通常推薦 Feature Branch -> Main 使用 **Squash**；Release Branch -> Main 使用 **Merge Commit**。

## 6.2 處理 Git Hooks 繞過問題

**問題 (Question)**：
「我們設置了 Pre-commit hook 來跑測試，但有緊急 Hotfix 需要立刻上線，測試跑太久了。你會怎麼做？這在流程治理上意味著什麼？」

"We set up a Pre-commit hook to run tests, but there's an urgent Hotfix that needs to go live immediately, and tests take too long. What do you do? What does this imply for process governance?"

**高分回答要點 (Key Points)**：
*   **技術解**：可以使用 `git commit --no-verify` (或 `-n`) 繞過 Hooks。
*   **治理觀點**：這是一個「破窗」風險。資深工程師應確保這種繞過是「例外」而非「常態」。
*   **系統解**：如果 Pre-commit 跑太久，代表 Hook 設計不良（應該只跑受影響的測試，或移到 CI 階段跑）。正確做法是優化 Hook 速度，而非繞過它。

## 6.3 如何導入 Conventional Commits

**問題 (Question)**：
「團隊目前 Commit Message 很隨意，你要如何導入 Conventional Commits 而不引起團隊反彈？」

"The team's current Commit Messages are messy. How would you introduce Conventional Commits without causing pushback?"

**高分回答要點 (Key Points)**：
*   **漸進式 (Incremental)**：先從 CI 檢查開始（設為 Warning 而非 Error）。
*   **工具輔助 (Tooling)**：引入 `Commitizen` (CLI 工具) 引導工程師撰寫，而不是強迫他們背誦格式。
*   **價值展示 (Value Proposition)**：展示自動生成 Changelog 的好處，讓大家看到「寫好 Commit = 省下寫 Release Note 的時間」。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Git 歷史即資產**：清晰的歷史能加速 Debug (`git bisect`) 與自動化發布。
2.  **Conventional Commits**：是連接「程式碼變更」與「語意化版號 (SemVer)」的橋樑。
3.  **Code Review 禮儀**：區分機器檢查 (Lint) 與人工檢查 (Design)，善用 Stacked PRs 避免巨型變更。
4.  **Rebase 優先**：在 Feature Branch 上使用 Rebase 同步上游，避免無意義的 Merge Commits。
5.  **衝突管理**：善用 `git rerere` 解決重複衝突，減少重複勞動。

## 後續延伸 (Next Steps)

*   **實作練習**：在你的專案中配置 `husky` 和 `commitlint`，強制執行 Conventional Commits。
*   **延伸閱讀**：研究 **Trunk Based Development** (主幹開發模式)，這是 Google/Meta 等大廠常用的分支策略，與本章的 CI/CD 觀念高度相關。
*   **下一章預告**：Chapter 08 將深入探討 **Git Internals & Troubleshooting** (Git 內部原理與疑難排解)，理解 `.git` 資料夾下的 Object Model，讓你成為真正的 Git 黑魔法師。