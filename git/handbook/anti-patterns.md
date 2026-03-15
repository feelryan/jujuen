# 常見反模式與避坑指南 / Common Anti-patterns and Pitfalls

在 Git 的使用旅程中，掌握指令只是第一步。真正的挑戰在於如何避免那些「技術上可行，但協作上災難」的操作習慣。本章節將盤點資深團隊最痛恨的 Git 反模式，並提供修正這些壞習慣的具體策略。

In the journey of mastering Git, knowing the commands is just the first step. The real challenge lies in avoiding habits that are "technically possible but collaboratively disastrous." This chapter covers the anti-patterns most despised by senior teams and provides concrete strategies to fix them.

---

## Mental model｜心智模型

### 公共歷史 vs. 私人草稿 (Public History vs. Private Drafts)

要避開 Git 的大多數坑，核心觀念在於區分 **「私人工作區」** 與 **「公共共享區」**。

- **私人草稿 (Local/Private)**：在你的 Local branch，你可以隨意提交 (WIP commits)、搞亂歷史、甚至 Force push。這就像你的私人筆記本，亂一點沒關係。
- **公共歷史 (Shared/Public)**：一旦推送到遠端共享分支（如 `main`, `develop`），這就是團隊的「法律紀錄」。這裡必須保持原子性 (Atomic)、線性 (Linear) 且不可篡改 (Immutable)。

**The Golden Rule:** Never rewrite history that others rely on.
**黃金法則：** 永遠不要重寫他人依賴的歷史紀錄。

---

## Patterns & best practices｜常見模式與最佳實務

在討論錯誤之前，我們先定義什麼是「健康」的 Git 使用模式。

### 1. 原子性提交 (Atomic Commits)
每個 Commit 應該只做「一件事」，並且該 Commit 本身是可以獨立運作（Build & Test pass）的。
- **Why**: 方便 Code Review，也讓 `git revert` 或 `git bisect` 能夠精準定位問題。
- **How**: 使用 `git add -p` 來挑選部分程式碼進行提交，而不是一把抓 (`git add .`)。

### 2. 交互式重基 (Interactive Rebase)
在將功能分支合併回主線之前，先整理自己的 Commit 歷史。
- **Pattern**: `git rebase -i main`
- **Action**: 將瑣碎的 "fix typo", "wip" 合併 (Squash) 成有意義的 Commit，並重新撰寫清晰的 Commit Message。

### 3. 使用 Lease 模式強制推送 (Force Push with Lease)
當你需要修改遠端分支的歷史（例如 PR 修改期間的 Rebase），絕對不要使用單純的 `-f`。
- **Best Practice**: `git push --force-with-lease`
- **Why**: 它會檢查遠端分支是否在你不知情的情況下被其他人更新過。如果是，它會阻止推送，避免你覆蓋隊友的程式碼。

### 4. 短命分支策略 (Short-lived Branches)
分支存活時間越短，合併衝突 (Merge Conflict) 的機率是指數級下降的。
- **Goal**: Feature branch 壽命應以「天」為單位，而非「月」。
- **Technique**: 使用 Feature Flags 來合併尚未完成的功能，而不是長期維持一個 Feature Branch。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是真實專案中常見的「災難製造者」，請務必識別並避免。

### 1. The "God Commit" (上帝提交)
- **症狀**: 一個 Commit 修改了 50 個檔案，包含了重構、新功能以及修復 Bug。
- **後果**: 無法 Review，無法 Revert（因為會回滾掉其他正常的功能），隱藏 Bug 的溫床。
- **解法**: 嚴格執行 Atomic Commits。如果已經發生，用 `git reset HEAD~1` 拆解後重新分批提交。

### 2. The "WIP" Spam (洗版式提交)
- **症狀**: 歷史紀錄充滿了 `fix`, `temp`, `save`, `wip` 這種無意義的訊息。
- **後果**: 汙染專案歷史，讓 `git log` 失去閱讀價值。
- **解法**: 在 Local 隨意 Commit 沒問題，但在 Push 或 Merge 前，務必使用 `Squash` 清理。

### 3. Long-Running Branches (長壽分支)
- **症狀**: 一個分支開發了兩個月，累積了上百個 Commits，且遠遠落後於 `main`。
- **後果**: "Merge Hell"（合併地獄）。解決衝突的成本可能比重寫程式碼還高。
- **解法**: 頻繁地 `git merge main` 或 `git rebase main` 到你的分支，保持同步；盡早合併回主線。

### 4. Committing Dependencies & Binaries (提交依賴與二進位檔)
- **症狀**: `node_modules/`, `.env`, 編譯後的 `.dll`, `.o`, 或巨大的 `.psd` 檔案被 commit 進去。
- **後果**: Repo 體積暴增（Git 效能變差），且可能洩漏敏感資訊（Secrets）。
- **解法**:
    - 嚴格配置 `.gitignore`。
    - 大檔案使用 **Git LFS**。
    - 敏感資訊掃描（如 `git-secrets` 或 Pre-commit hooks）。

### 5. The Foxtrot Merge (狐步舞合併)
- **症狀**: 在 Feature branch 上 merge 了 `main`，然後 `main` 又 merge 了 Feature branch。這會導致 Git 線圖出現不必要的交叉與混亂。
- **後果**: 歷史線圖難以追蹤，`git log --first-parent` 會失效。
- **解法**: 在 Feature branch 上盡量使用 `rebase` 來同步 `main` 的變更，保持線性歷史。

---

## Checklists & workflows｜檢查清單與流程

### Daily Workflow Checklist (日常工作檢查清單)

在執行 `git push` 或發起 Pull Request 之前，請對照此清單：

- [ ] **Commit 粒度檢查**：我的每個 Commit 是否只做了一件邏輯上完整的事？
- [ ] **訊息檢查**：Commit Message 是否符合團隊規範（如 Conventional Commits）？
- [ ] **敏感資料檢查**：是否不小心 `git add` 了 `.env`、API Key 或 Config 檔？
- [ ] **歷史整潔度**：是否有多餘的 `WIP` 或 `Fix typo` 需要 Squash？
- [ ] **同步檢查**：我是否已經 Rebase 了最新的 `main` 分支？
- [ ] **測試驗證**：Rebase 之後，程式碼是否還能通過測試？

### Decision Tree: Merge vs. Rebase (決策樹)

當你需要同步程式碼時：

1. **我在公共分支上嗎？ (e.g., main, develop)**
   - **Yes** -> 使用 `Merge` (保留歷史真實性)。
   - **No** (我在 Feature branch) -> 進入下一步。

2. **我的 Feature branch 有其他人正在共用嗎？**
   - **Yes** -> 使用 `Merge` (避免破壞隊友的歷史)。
   - **No** (只有我在用) -> 使用 `Rebase` (保持歷史線性整潔)。

---

## Real-world examples｜實戰案例

### Case 1: The "Force Push" Catastrophe
**情境**:
工程師 A 在 `feature-login` 分支上工作，他覺得之前的 commit 訊息寫錯了，於是用了 `rebase` 修改並 `git push -f`。
同時，工程師 B 已經 pull 了 `feature-login` 並在其基礎上寫了新的 code。

**後果**:
工程師 A 的強制推送覆蓋了遠端歷史。工程師 B 下次 push 時會被拒絕，如果 B 不懂原理強行 pull merge，會導致歷史線圖出現重複的 commit (Duplicate Commits)，甚至遺失程式碼。

**正確做法**:
工程師 A 應使用 `git push --force-with-lease`。如果失敗，代表 B 有新進度，A 必須先 pull B 的變更，解決衝突後再推。

### Case 2: The "Config File" Trap
**情境**:
專案初期沒有設定好 `.gitignore`。工程師 C 為了方便測試，修改了 `config/database.yml` 指向自己的 localhost，並順手 `git add .` 提交了。

**後果**:
所有隊友 pull 下來後，資料庫連線全部壞掉（因為都指向了 C 的電腦）。更糟的是，如果這是正式環境的設定檔，可能導致 Production 服務連線錯誤。

**修復流程**:
1.  從 Git 索引中移除該檔案（但不刪除實體檔案）：`git rm --cached config/database.yml`
2.  將該檔案加入 `.gitignore`。
3.  提交變更：`git commit -m "chore: stop tracking database config"`
4.  如果是敏感資料（密碼），則需要使用 BFG Repo-Cleaner 或 `git filter-branch` 徹底清洗歷史。

### Case 3: The 500MB Repository
**情境**:
設計師直接將高清行銷圖檔 (`assets/banner.psd`, 100MB) 放入專案資料夾並提交。隨著版本迭代，Repo 迅速膨脹到 2GB。

**後果**:
`git clone` 需要花費 20 分鐘，CI/CD Pipeline 拉取程式碼超時失敗。

**解決方案**:
- **立即止血**: 移除大檔案並使用 `git filter-repo` 清洗歷史。
- **長治久安**: 安裝 Git LFS (`git lfs install`)，並設定 `git lfs track "*.psd"`，讓 Git 僅儲存指針 (Pointer)，實體檔案存放在物件儲存中。