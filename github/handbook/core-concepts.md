# 核心概念與協作心智模型 / Core Concepts & Collaboration Mental Models

本章節不討論 `git add` 或 `git commit` 的基礎指令，而是聚焦於 **GitHub 作為一個協作平台** 的核心邏輯。理解 GitHub 如何在 Git 協議之上構建「社交編碼（Social Coding）」層，是掌握高效協作的關鍵。

This chapter focuses on the core logic of **GitHub as a collaboration platform**, rather than basic Git commands. Understanding how GitHub builds a "Social Coding" layer on top of the Git protocol is key to mastering efficient collaboration.

---

## Mental model｜心智模型

### 1. The "Collaboration Layer" over Git Protocol
**協作層覆蓋於協議層之上**

- **Git (The Protocol):** 關注的是檔案的快照（Snapshots）、雜湊（Hashes）與歷史樹（History Tree）。它是分散式的，沒有所謂的「中心」。
- **GitHub (The Platform):** 關注的是 **權限（Permissions）**、**對話（Conversations）** 與 **流程（Workflows）**。它強行定義了一個「Single Source of Truth（唯一真理來源）」，即遠端儲存庫（Remote Repository）。
- **關鍵心法：** 在 GitHub 上，**Pull Request (PR)** 才是工作的基本單位（Unit of Work），而不是 Commit。Commit 是技術產物，PR 則是包含程式碼、CI 驗證結果、Code Review 討論與業務邏輯的完整交付包。

### 2. The Triangle of Upstream, Origin, and Local
**上游、原點與本地的三角關係**

在協作中，你必須清晰區分三個空間：
1.  **Upstream (Production/Team Repo):** 團隊的共享儲存庫，通常受到嚴格保護（Branch Protection Rules）。
2.  **Origin (Your Fork/Remote):** 你在 GitHub 上的個人副本（如果是 Fork 模式）或你推送到共享庫的遠端分支。
3.  **Local (Your Machine):** 你的開發環境。

> **Mental Image:** 你的 Local 是草稿紙，Origin 是你的私人筆記本，Upstream 則是最終出版的教科書。資料流向通常是 `Local -> Origin -> (via PR) -> Upstream`。

### 3. Conversation-Driven Development
**對話驅動開發**

GitHub 的核心哲學是「Code is a conversation」。每一行程式碼的變更都應該附帶上下文（Context）。
- **Issues** 定義 "Why" (為什麼要做)。
- **Pull Requests** 定義 "How" (如何實作) 並記錄 "Review" (審查過程)。
- **Actions** 提供 "Verification" (機器驗證)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Repository Collaboration Models
**儲存庫協作模式選擇**

在真實專案中，主要有兩種模式，選錯會導致流程混亂：

| Feature | **Shared Repository Model (共享儲存庫模式)** | **Fork & Pull Model (分叉與拉取模式)** |
| :--- | :--- | :--- |
| **適用場景** | 企業內部團隊、小型新創、信任度高的核心開發者。 | 開源專案、大型企業內部開源 (InnerSource)、外包廠商協作。 |
| **權限管理** | 所有開發者對 Repo 有 Write 權限。 | 開發者只有 Read 權限，必須 Fork 到自己帳號。 |
| **分支策略** | Feature branches 都在同一個 Repo 內 (`origin/feature-a`)。 | Feature branches 在開發者的 Fork 內 (`user/feature-a`)。 |
| **優點** | 協作速度快，CI 配置簡單，減少同步成本。 | 權限隔離極佳，主 Repo 保持乾淨，不會有雜亂的 stale branches。 |
| **最佳實務** | 搭配 **Branch Protection Rules** 強制 PR。 | 設定 **Upstream Remote** 以保持同步。 |

### 2. The "Draft First" Workflow
**草稿優先流程**

不要等到程式碼完美才開 PR。
- **Pattern:** 建立 PR 時直接標記為 **Draft**。
- **Benefit:**
    - 儘早觸發 CI Pipeline（提早發現測試失敗）。
    - 讓資深工程師或架構師可以早期介入給予方向（Early Feedback），避免走冤枉路。
    - 宣告「我正在處理這個問題」，避免重複工。

### 3. Contextual Linking
**上下文關聯**

利用 GitHub 的關鍵字自動化關聯 Issue 與 PR。
- 在 PR 描述中使用 `Closes #123`, `Fixes #456`。
- **Effect:** 當 PR Merge 到 Default Branch 時，相關聯的 Issue 會自動關閉。這保持了專案管理與程式碼狀態的一致性。

### 4. CODEOWNERS as Governance
**程式碼所有者機制**

在 Repo 根目錄或 `.github/` 下加入 `CODEOWNERS` 檔案。
- **Pattern:** 定義誰負責哪個目錄或檔案類型（例如：Frontend team 負責 `/src/ui`, Backend team 負責 `/src/api`）。
- **Effect:** 當有人修改特定檔案時，GitHub 會 **自動** 將對應的 Owner 加入 Reviewer 清單。這是落實 Governance 最直接的手段。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Rubber Stamp" Review
**橡皮圖章式的審查**

- **Anti-pattern:** Reviewer 僅僅看了一眼，沒有提出問題就按 "Approve"，或者只檢查語法錯誤（Linting error）。
- **Solution:** 語法錯誤應由 CI/Linter 抓出。Reviewer 應專注於架構、邏輯漏洞、安全性與可維護性。
- **Consequence:** 錯誤的程式碼進入 Production，且責任被分散（"因為某某也 approve 了"）。

### 2. Long-Lived Feature Branches
**長壽命的功能分支**

- **Anti-pattern:** 一個分支開發了兩週以上，累積了數十個 Commits 且未與 Main branch 同步。
- **Pitfall:** "Merge Hell"（合併地獄）。解決衝突的成本將指數級上升。
- **Remedy:** 使用 Feature Flags，頻繁將小變更 Merge 回主線（Trunk-Based Development 精神）。

### 3. Committing Secrets / Large Files
**提交金鑰或大型檔案**

- **Anti-pattern:** 不小心將 `.env` 或 `database.dump` 推送到 GitHub。
- **Pitfall:** 即使你隨後刪除了檔案，它仍存在於 `.git` 歷史紀錄中。駭客工具可以輕易掃描出歷史中的 Secrets。
- **Remedy:**
    - 使用 `git-secrets` 或 GitHub Advanced Security 的 Secret Scanning。
    - 若已發生，必須使用 `BFG Repo-Cleaner` 或 `git filter-repo` 清洗歷史，並**立即輪替（Rotate）所有洩漏的金鑰**。

### 4. Ignoring the "Bus Factor"
**忽視巴士係數**

- **Anti-pattern:** 只有一個 Admin 擁有 Repo 的完整設定權限。
- **Pitfall:** 當該員工離職或休假，CI 壞掉或 Branch Protection 需要緊急調整時，團隊癱瘓。
- **Remedy:** 使用 GitHub Teams 進行權限管理，而非個人帳號授權。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Which Workflow to use?
**決策樹：該使用哪種工作流？**

1.  **Is this an Open Source project?**
    *   Yes -> **Fork & Pull Model**
    *   No -> Go to 2.
2.  **Do you trust every contributor with write access?**
    *   Yes -> **Shared Repository Model** (Most corporate teams)
    *   No (e.g., Contractors, Interns) -> **Fork & Pull Model**

### Repository "Day 1" Setup Checklist
**儲存庫「第一天」設定清單**

建立新 Repo 時，請務必執行以下檢查：

- [ ] **Access Control:** 建立 GitHub Team 並賦予權限（避免直接加人）。
- [ ] **Branch Protection (Main/Master):**
    - [ ] Require pull request reviews before merging (至少 1 人)。
    - [ ] Require status checks to pass before merging (綁定 CI，如 Build/Test)。
    - [ ] Require conversation resolution before merging (確保所有留言都被處理)。
- [ ] **Documentation:**
    - [ ] `README.md` (專案做什麼、如何跑起來)。
    - [ ] `CONTRIBUTING.md` (如何開 PR、Coding Style)。
- [ ] **Governance:**
    - [ ] `.github/CODEOWNERS` (定義程式碼負責人)。
    - [ ] `.gitignore` (確保垃圾檔案不入庫)。
- [ ] **Security:**
    - [ ] 開啟 Dependabot alerts (相依性漏洞掃描)。
    - [ ] 開啟 Secret scanning (如果方案支援)。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Shared Repo" Feature Lifecycle
**場景：企業內部團隊的功能開發**

1.  **Sync:** Developer Alice pulls the latest `main`.
2.  **Branch:** Alice creates `feature/login-page`.
3.  **Work:** Alice commits code.
4.  **PR:** Alice pushes to `origin/feature-login-page` and opens a PR.
    *   *GitHub Action triggers:* Unit tests pass.
    *   *GitHub Action triggers:* Linter fails.
5.  **Fix:** Alice fixes lint errors, pushes again. CI passes.
6.  **Review:** Bob (Code Owner) reviews. Requests changes on error handling logic.
7.  **Resolve:** Alice updates code, replies "Fixed", and resolves the conversation.
8.  **Merge:** Bob approves. Alice clicks "Squash and Merge".
9.  **Cleanup:** The branch `feature/login-page` is automatically deleted.

### Scenario 2: Syncing a Fork (The "Upstream" Problem)
**場景：開源貢獻者同步上游**

很多新手 Fork 之後不知道如何跟上原專案的更新。

```bash
# 1. 設定上游 (只做一次)
git remote add upstream https://github.com/original-owner/repo.git

# 2. 定期同步流程 (Standard Workflow)
git checkout main          # 切換回本地主分支
git fetch upstream         # 抓取上游最新狀態 (不會自動合併)
git merge upstream/main    # 將上游的更新合併到本地 main
# 或者使用 git pull upstream main

# 3. 更新你的 GitHub Fork (Origin)
git push origin main       # 現在你的 GitHub Fork 也跟上游同步了
```

*注意：GitHub UI 現在也提供了 "Sync Fork" 按鈕，但在複雜衝突時，上述 CLI 流程仍是必須的技能。*