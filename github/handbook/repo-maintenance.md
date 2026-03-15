# 儲存庫維護與遷移策略 / Repository Maintenance & Migration Strategies

## Mental model｜心智模型

在軟體生命週期中，Git Repository 不僅僅是程式碼的容器，它更像是一個**有生命的有機體 (Living Organism)** 或是一個**需要維護的資料庫 (Database)**。

1.  **Git History as an Asset (歷史即資產)**：
    Git 的歷史紀錄不僅是備份，它是 Context（脈絡）。維護儲存庫意味著要保護這些脈絡的清晰度，同時移除雜訊（如誤傳的大檔、敏感資訊）。
2.  **The Broken Windows Theory (破窗效應)**：
    一個充滿過期分支、CI 失敗、沒有 README 或包含敏感資訊的 Repo，會降低團隊的維護意願。定期清理（Pruning）與標準化（Standardization）是保持工程品質的基礎。
3.  **Immutability vs. Mutability (不可變與可變)**：
    雖然我們常說 Git 歷史不可變，但在維護階段（特別是移除敏感資料或瘦身），我們必須將歷史視為可重寫的（Mutable），但這是一個破壞性操作（Destructive Operation），必須具備「核彈發射」般的謹慎心態。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 儲存庫瘦身與歷史重寫 (Repo Cleaning & History Rewriting)
當 Repo 體積過大（例如 `.git` 資料夾超過 1GB）或誤傳敏感資料時，單純刪除檔案是無效的，必須重寫歷史。

-   **使用 `git-filter-repo` (Modern Standard)**：
    -   這是目前官方推薦且效能最好的工具（取代了 `git filter-branch` 和 BFG）。
    -   **Pattern**: 分析 -> 備份 -> 過濾 -> 強制更新。
    -   **Best Practice**: 在執行任何重寫操作前，務必先建立一個全新的 `mirror clone` 作為備份。

### 2. 敏感資料處理 (Secret Sanitization)
-   **Rotate First, Rewrite Later**: 如果 API Key 進入了 commit history，第一件事**永遠是作廢該 Key (Rotate)**，而不是急著刪除 commit。因為歷史紀錄可能已經被 Fork 或 Cache。
-   **Tooling**: 結合 GitHub Advanced Security 的 Secret Scanning 或開源工具（如 TruffleHog）來定位洩漏點。

### 3. 樣板儲存庫標準化 (Template Repository Standardization)
不要讓團隊每次開新專案都從 `git init` 開始，也不要用 Fork 來當作樣板（這會污染 Commit Graph）。

-   **Template Repositories**: 將標準化的專案結構（Scaffolding）設為 GitHub Template Repository。
-   **The `.github` Repo**: 在 Organization 根目錄下建立一個名為 `.github` 的公開儲存庫。
    -   存放全組織共用的 Issue Templates, PR Templates, `CONTRIBUTING.md`, 和 `CODE_OF_CONDUCT.md`。
    -   這是 GitHub 的隱藏功能，能自動套用到組織內所有 Repo。

### 4. 封存策略 (Archiving Strategy)
當專案不再維護，不要直接刪除（Delete），應選擇封存（Archive）。

-   **Read-Only Mode**: GitHub 的 Archive 功能會將 Repo 轉為唯讀，保留 Issue 和 PR 歷史供後人參考。
-   **Deprecation Notice**: 在 `README.md` 頂部清楚標示「此專案已停止維護」，並提供替代方案或遷移路徑的連結。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `git filter-branch` Trap
-   **Anti-pattern**: 使用老舊的 `git filter-branch` 指令來清理歷史。
-   **Why**: 它極慢、語法複雜且容易導致資料損壞。請全面轉用 `git-filter-repo` 或 `BFG Repo-Cleaner`。

### 2. The "Ostrich Algorithm" for Secrets (鴕鳥心態)
-   **Anti-pattern**: 發現 commit 了 `.env` 檔，於是發一個新 commit 刪除該檔案，並假裝沒事發生。
-   **Why**: 該檔案仍存在於 `.git/objects` 中，任何能 clone 的人都能透過 `git checkout <old-commit-hash>` 找回密碼。

### 3. Forking for Divergence (濫用 Fork)
-   **Anti-pattern**: 為了建立一個類似的新專案而 Fork 舊專案，但兩者未來不會合併。
-   **Why**: Fork 的語意是「分岔後貢獻回原專案」。如果只是要抄程式碼，應使用 Template Repository 或 `git clone` 後移除 `.git` 資料夾重新 init。

### 4. Force Push without Lease
-   **Anti-pattern**: 在重寫歷史後，使用 `git push -f`。
-   **Why**: 如果在你重寫的過程中，有同事 push 了新程式碼，`-f` 會無聲無息地覆蓋掉他們的貢獻。
-   **Correction**: 永遠使用 `git push --force-with-lease`，它會在遠端 ref 被更動時阻止推送。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: 移除誤傳的大型檔案 (Removing Large Files)

此流程適用於 `.git` 資料夾過大，需要移除歷史紀錄中的大型 Binary 檔。

1.  **安裝工具**: 確保已安裝 `git-filter-repo` (需 Python 環境)。
2.  **分析**:
    ```bash
    git clone --mirror https://github.com/org/repo.git
    cd repo.git
    git filter-repo --analyze
    # 查看 .git/filter-repo/analysis/path-all-sizes.txt 找出元兇
    ```
3.  **執行清理**:
    ```bash
    # 假設要移除所有 mp4 檔案
    git filter-repo --path-glob '*.mp4' --invert-paths
    ```
4.  **垃圾回收**:
    ```bash
    git reflog expire --expire=now --all
    git gc --prune=now
    ```
5.  **推送**:
    ```bash
    git push --mirror origin  # 注意：這會重寫遠端所有分支
    ```
6.  **通知團隊**: 要求所有開發者刪除本地 Repo 並重新 Clone (不要 pull，會導致歷史混亂)。

### Checklist: 專案遷移/交接 (Project Migration/Handover)

- [ ] **權限審計**: 檢查 `Settings > Manage access`，移除不再需要的個人帳號，改用 Team 權限管理。
- [ ] **CI/CD Secrets**: 檢查 GitHub Actions Secrets，確保沒有綁定「個人帳號」的 Token (PAT)，應改用 GitHub App 或 Machine User。
- [ ] **Webhook 清理**: 移除指向舊 Slack 頻道或失效 Jenkins 的 Webhooks。
- [ ] **Branch Protection**: 確認 `main` / `master` 分支已啟用保護規則 (Require PR, Require Status Checks)。
- [ ] **Documentation**: `README.md` 是否包含最新的 setup 步驟？是否連結到正確的設計文件？

---

## Real-world examples｜實戰案例

### Case 1: 從 Monolith 拆分出特定服務 (Subtree Splitting)

**情境**：你有一個巨大的單體 Repo (`monorepo`)，裡面有一個資料夾 `packages/auth-service`，你想把它拆成一個獨立的 Repo，但**必須保留該資料夾的 Git Commit 歷史**。

**Solution**:
使用 `git-filter-repo` 的子目錄過濾功能。

```bash
# 1. Clone 原始大 Repo
git clone https://github.com/org/monorepo.git auth-service-new
cd auth-service-new

# 2. 只保留 packages/auth-service 目錄的內容與歷史，並將其提升到根目錄
git filter-repo --path packages/auth-service/ --to-subdirectory-filter /

# 3. 此時 Repo 根目錄就是原本 auth-service 的內容，且 log 只包含相關改動
git remote add origin https://github.com/org/auth-service.git
git push -u origin main
```

### Case 2: 敏感金鑰洩漏處理 (The "Leaked AWS Key" Protocol)

**情境**：CI 報警偵測到 AWS Secret Key 被 commit 進了 `feature/login` 分支。

**Action Plan**:

1.  **Stop the Bleeding (止血)**:
    *   立即登入 AWS Console，**停用 (Deactivate)** 並 **刪除 (Delete)** 該 Key。
    *   產生新的 Key 並更新到 GitHub Secrets 或 Vault。
2.  **Assess Scope (評估)**:
    *   檢查 CloudTrail Logs，確認該 Key 在洩漏期間是否有異常存取紀錄。
3.  **Scrub History (清洗)**:
    *   如果該分支尚未 merge 到 main：直接刪除該分支，強迫開發者在本地修正後重新 push (rebase/amend)。
    *   如果已 merge 到 main：
        ```bash
        # 使用 BFG 快速移除檔案 (適合簡單情境)
        java -jar bfg.jar --delete-files .env repo.git
        # 或者使用 filter-repo 移除特定文字 (進階)
        git filter-repo --replace-text expressions.txt
        ```
4.  **Force Push & Notify**:
    *   `git push --force-with-lease`
    *   在 Slack 頻道公告：「Repo 歷史已重寫，請大家刪除本地 `feature/login` 分支並重新 fetch。」