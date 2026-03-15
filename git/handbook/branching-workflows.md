# 分支策略決策與工作流設計 / Branching Strategies and Workflow Design

## Mental model｜心智模型

### 1. 流量控制與整合頻率 (Traffic Control & Integration Frequency)
將分支策略視為程式碼的「交通管制系統」。
- **Git Flow** 像是擁有複雜交流道、緩衝區與多層閘道的傳統高速公路系統，旨在確保只有經過層層檢查的車輛（程式碼）才能進入主幹道。這適合發布週期長、容錯率低的環境。
- **Trunk-based Development (TBD)** 則像是一條無限速的高速公路，強調車輛（程式碼）快速匯入主流。安全依賴於車輛本身的品質（自動化測試）與路況監控（CI/CD），而非閘道攔截。

**核心指標：** 分支壽命（Branch Lifespan）。分支存在的時間越長，與主幹（Main/Trunk）的差異越大，合併時的「整合債務」（Integration Debt）就越高。

### 2. 發布與部署的解耦 (Decoupling Release from Deployment)
在現代工作流中，分支策略應協助將「部署（Deployment）」與「發布（Release）」分開。
- **Deployment**: 技術行為，將程式碼推送到伺服器。
- **Release**: 商業行為，將功能開放給使用者。
- **Mental Shift**: 不要依賴長壽命的分支來控制功能發布，應轉向使用 **Feature Flags**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. GitHub Flow (Feature Branch Workflow)
最適合 SaaS 與 Web 應用程式的輕量級流程。
- **適用場景**：持續部署（CD）、團隊規模中小型、單一版本線上運行。
- **核心規則**：
  - `main` 分支隨時處於可部署狀態（Deployable）。
  - 所有新功能/修復都在 `feature/*` 或 `fix/*` 分支進行。
  - 透過 Pull Request (PR) 進行 Code Review 與討論。
  - 合併即部署（Merge triggers deployment）。

### 2. Trunk-Based Development (TBD)
高效能 DevOps 團隊的黃金標準（Google, Meta 採用）。
- **適用場景**：資深團隊、高覆蓋率自動化測試、需要極致的開發速度。
- **核心規則**：
  - 開發者直接 commit 到 `main` 或使用壽命極短（< 1天）的分支。
  - **Feature Flags** 是必要條件：未完成的功能透過開關隱藏，而非留在分支上。
  - 避免 "Merge Hell" 的最佳解法。

### 3. Git Flow (The Classic)
結構嚴謹但稍顯臃腫的傳統模型。
- **適用場景**：開源專案、手機 App、桌面軟體（有明確版本號且需同時維護多個舊版本）。
- **核心規則**：
  - 雙主幹：`main` (正式版) 與 `develop` (開發中)。
  - 輔助分支：`feature/*`, `release/*`, `hotfix/*`。
  - **Trade-off**：流程繁瑣，容易導致 CI/CD 管道複雜化，不建議用於單純的 Web 服務。

### 4. Release Branching Strategy (Release Train)
針對定期發布產品的折衷方案。
- **做法**：平時在 `main` 開發，每兩週（或特定週期）切出一條 `release/v1.x` 分支。
- **特點**：Release 分支凍結功能（Code Freeze），只修 Bug。修復後需 Cherry-pick 回 `main` 或設定自動合併。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Long-Lived Feature Branches (長壽命功能分支)
- **現象**：一個功能分支開發了兩週甚至一個月才合併。
- **後果**：合併衝突（Merge Conflicts）將會是指數級的災難；重構（Refactoring）變得不可能，因為會破壞別人的分支。
- **解法**：將大功能拆解為小任務，頻繁合併（即使功能尚未對使用者開啟）。

### 2. Integration Branches (虛假的整合分支)
- **現象**：建立 `qa`、`uat`、`staging` 等永久分支，並規定「測完 QA 才能合到 UAT」。
- **後果**：
  - 違反 "Build once, deploy anywhere" 原則。
  - `qa` 分支的程式碼組合可能永遠不會出現在 `main` 中（因為有些功能被退回，有些通過），導致在 QA 驗證過的程式碼與 Production 不一致。
- **解法**：環境是基礎設施的概念，不應與 Git 分支直接綁定。同一份 Artifact（Docker Image）應流轉於不同環境。

### 3. Dependence on Merge Commits for History (過度依賴合併節點)
- **現象**：為了保留歷史，禁止 Squash Merge，導致 `main` 充滿了 "Fix typo", "WIP" 等無意義 commit。
- **建議**：使用 **Squash and Merge** 保持主幹乾淨，一個功能一個 Commit。

### 4. Git Flow used for Web Apps (在 Web 專案誤用 Git Flow)
- **現象**：為了修一個線上的小字體錯誤，必須走 `hotfix` -> `main` -> `develop` 的完整流程。
- **後果**：流程阻礙了修復速度，團隊感到疲憊。

---

## Checklists & workflows｜檢查清單與流程

### Decision Matrix: Choosing a Strategy (決策矩陣)

| 評估維度 (Dimension) | Trunk-Based / GitHub Flow | Git Flow / Release Branches |
| :--- | :--- | :--- |
| **產品型態** | SaaS, Web App, Backend API | Mobile App, Desktop, Firmware |
| **發布頻率** | 每天多次 (Multiple times/day) | 數週或數月一次 (Weeks/Months) |
| **團隊資歷** | 資深，習慣自動化測試 | 混合，依賴人工 QA |
| **多版本維護** | 不需要 (Always latest) | 需要 (v1.0, v1.1, v2.0 並存) |

### Workflow: Feature Development (日常開發檢查清單)

- [ ] **Scope Check**: 這個功能是否能在 1-2 天內完成？如果不行，是否已拆分？
- [ ] **Sync First**: 在建立分支前，是否已 `git pull origin main` 確保基底最新？
- [ ] **Naming Convention**: 分支名稱是否符合團隊規範？(e.g., `feat/user-login`, `JIRA-123-fix-bug`)
- [ ] **Draft PR**: 是否在寫第一行程式碼後就建立了 Draft PR 以便提早獲得回饋？
- [ ] **CI Status**: 在請求 Review 前，CI (Linter, Tests) 是否全綠？
- [ ] **Cleanup**: 合併後，是否刪除了遠端與本地的功能分支？

---

## Real-world examples｜實戰案例

### Scenario 1: The "Release Train" for Mobile Apps
**情境**：一個 iOS 團隊，每兩週需送審 App Store。
**策略**：
1.  所有開發者向 `main` 合併程式碼。
2.  **雙週三**：從 `main` 切出 `release/v1.2.0`。
3.  **Code Freeze**：`release/v1.2.0` 進入 QA 階段，禁止新功能，只允許 Bug fix。
4.  **Fixes**：發現 Bug 時，在 `release/v1.2.0` 修復，並同時 **Cherry-pick** 回 `main`（確保下個版本也有修復）。
5.  **發布**：審核通過後，`release/v1.2.0` 打上 Tag `v1.2.0`，封存。

### Scenario 2: Transitioning from Git Flow to Trunk-Based
**情境**：一個 Web 團隊發現 Git Flow 導致合併衝突頻發，決定轉型。
**過渡步驟**：
1.  **廢除 `develop` 分支**：將 `develop` 合併回 `main`，並宣布 `main` 為唯一真理來源。
2.  **引入 Feature Toggles**：
    ```javascript
    // Pseudo-code for Feature Flag
    if (featureFlags.isEnabled('new-checkout-flow')) {
        renderNewCheckout();
    } else {
        renderOldCheckout();
    }
    ```
3.  **改變 Review 習慣**：不再等到功能 100% 完成才 Review。只要 Feature Flag 是關閉的，半成品（Backend API 寫好但 Frontend 還沒接）也可以合併進 `main`。
4.  **結果**：`main` 隨時可部署，不再有 "Integration Week"（整合週）這種惡夢。

### Scenario 3: Hotfix in GitHub Flow
**情境**：線上生產環境發現嚴重 Bug。
**流程**：
1.  從 `main` 建立分支 `fix/payment-error`。
2.  提交修復程式碼與 **Regression Test**（防止再次發生）。
3.  開啟 PR，標記為 `Critical`。
4.  CI 通過 + Code Review 通過。
5.  合併回 `main` -> 自動觸發 Deploy 到 Production。
6.  不需要像 Git Flow 那樣同時處理 `master` 和 `develop` 的同步問題。