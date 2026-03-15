# 進階操作：Rebase、Cherry-pick 與 Stash / Advanced Operations: Rebase, Cherry-pick, and Stash

## Mental model｜心智模型

要掌握這些進階操作，必須暫時放下「時間軸」的概念，轉而關注 **DAG（有向無環圖）的重組與剪貼**。

### 1. Rebase: Base Changing & Replaying (更換地基與重播)
不要把 Rebase 想成「合併」，請把它想成 **「剪下並貼上」**。
- **概念**：你把一整串 Commit（你的 Feature branch）從原本的岔路口「剪下來」，然後貼到最新的 `main` 分支頂端。
- **機制**：Git 會依序讀取你的每一個 Commit，在新的 Base 上 **重新播放 (Replay)** 一次。
- **關鍵點**：雖然內容看起來一樣，但產生的 Commit Hash 全部都會改變（因為父節點變了）。這是在 **改寫歷史 (Rewriting History)**。

### 2. Cherry-pick: Precise Copy-Paste (精準複製貼上)
Cherry-pick 是 Commit 層級的 **「複製貼上」**。
- **概念**：你只想要另一個分支上的 **某一個特定變更**，而不想要合併整個分支。
- **機制**：Git 讀取該 Commit 的差異 (Diff)，並在當前分支上應用這個差異，生成一個全新的 Commit。

### 3. Stash: The Dirty Clipboard (臨時剪貼簿/堆疊)
Stash 是一個獨立於 Working Directory 和 Staging Area 之外的 **LIFO (Last-In, First-Out) 堆疊**。
- **概念**：當你的桌面（工作目錄）一團亂，但老闆叫你馬上修另一個 Bug 時，你把桌上所有東西掃進抽屜（Stash），修完 Bug 後再把東西倒回桌上。
- **關鍵點**：它不屬於任何分支，它是本地暫存區。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Clean History" Pattern (互動式 Rebase 整理歷史)
在發送 Pull Request (PR) 之前，使用 Interactive Rebase 來整理你的 Commit 歷史。這是一種禮貌，也是專業的展現。

```bash
# 整理最近的 5 個 commits
git rebase -i HEAD~5
```
- **Squash**: 將瑣碎的 "wip", "typo fix" 合併成一個完整的邏輯單元。
- **Reword**: 修改語意不清的 Commit Message。
- **Reorder**: 調整 Commit 順序，讓 Code Review 更順暢。

### 2. The "Update via Rebase" (以 Rebase 更新分支)
當你的 Feature branch 落後於 `main` 時，優先使用 Rebase 而不是 Merge 來更新。
- **做法**：`git fetch origin` -> `git rebase origin/main`
- **優點**：保持 Feature branch 的線性歷史，避免出現無意義的 "Merge branch 'main' into feature" 節點，讓最終的 Merge Request 更乾淨。

### 3. The "Fixup" Workflow (自動修復流程)
如果你發現之前的 Commit 有錯，不要新增一個 "Fix bug" commit，而是使用 `--fixup`。

```bash
# 1. 修改程式碼
# 2. 假設要修復的目標 commit hash 是 abc1234
git commit --fixup abc1234

# 3. 稍後進行 rebase 時自動處理
git rebase -i --autosquash origin/main
```
這會自動將修復的變更歸併到原本的 Commit 中，完全自動化。

### 4. Named Stashes (具名暫存)
永遠不要只打 `git stash`。過了一週你絕對看不懂 `WIP on master: ...` 是什麼。

```bash
# 推薦做法：加上訊息
git stash push -m "experimenting with new login logic"
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Public History Rewrite" (改寫公共歷史)
**絕對禁止 (Cardinal Sin)**：對已經 Push 到共享分支（如 `main`, `develop`）且他人正在使用的 Commit 進行 Rebase。
- **後果**：隊友的歷史會與遠端衝突，導致他們必須強制合併，產生重複的 Commit 災難。
- **原則**：**Only rebase commits that exist ONLY on your machine.** (只 Rebase 尚未公開的 Commit)。

### 2. The "Cherry-pick Dependency" (過度依賴 Cherry-pick)
如果你發現自己頻繁地在分支間 Cherry-pick 大量的 Commits。
- **問題**：這通常代表分支策略 (Branching Strategy) 有問題。相同的程式碼邏輯分散在不同 Hash 的 Commit 中，未來追蹤 Bug 會非常困難。
- **解法**：考慮重構公共模組，或調整分支合併流程。

### 3. Stash as Permanent Storage (把 Stash 當倉庫)
Stash 是暫時的。如果你把東西放在 Stash 超過一天，你通常會忘記它，或者在清理時不小心 Drop 掉。
- **建議**：如果你需要保存實驗性程式碼超過數小時，請建立一個 `temp/experiment` 分支並 Commit 上去，而不是留在 Stash。

### 4. Resolving Conflicts in Rebase Panic (Rebase 衝突恐慌)
在 Rebase 過程中遇到衝突時，新手容易恐慌並亂修。
- **正確心態**：Rebase 是逐個 Commit 應用。遇到衝突時，Git 停在「當下那個 Commit」。
- **操作**：解衝突 -> `git add .` -> `git rebase --continue` (不要執行 `git commit`)。
- **逃生門**：搞不定時，隨時執行 `git rebase --abort` 回到原點。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Pre-Merge Cleanup (合併前清理)
在將你的功能分支合併回主線之前，請執行以下檢查：

- [ ] **Check Push Status**: 這些 Commits 是否已經被其他人拉取 (Pull) 過？如果是，**停止 Rebase**。
- [ ] **Interactive Rebase**:
    - [ ] 是否有 "WIP" 或 "Fix typo" 等無意義的節點需要 Squash？
    - [ ] Commit Message 是否符合團隊規範？
- [ ] **Sync with Main**: 執行 `git rebase origin/main` 確保基底是最新的。
- [ ] **Test**: Rebase 完成後，**必須**重新執行測試（因為程式碼組合改變了）。
- [ ] **Force Push**: 如果之前已經 Push 過該分支（且只有你在用），使用 `git push --force-with-lease` 更新遠端。

### Decision Tree: Merge vs. Rebase vs. Cherry-pick
- **我要更新我的私有分支 (Private Branch) 以同步主線：** -> **Rebase**
- **我要將完成的功能合併回公共主線 (Public Branch)：** -> **Merge** (通常使用 Squash Merge 或 Merge Commit 以保留功能邊界)
- **我只需要另一個分支的某個 Hotfix，不需要其他改動：** -> **Cherry-pick**
- **我寫到一半需要切換分支修 Bug：** -> **Stash**

---

## Real-world examples｜實戰案例

### Scenario 1: The "Emergency Context Switch" (緊急切換情境)
你在開發 `feature-A`，改了 10 個檔案，還沒寫完，老闆突然說線上 `main` 有個緊急 Bug 要修。

```bash
# 1. 保存當前進度
git stash push -m "WIP: feature-A api integration"

# 2. 切換到主線並建立修復分支
git checkout main
git pull
git checkout -b hotfix-login-error

# ... 修復 Bug, Commit, Push, Merge ...

# 3. 回到原本工作
git checkout feature-A
git stash pop
# 繼續工作
```

### Scenario 2: Cleaning up a messy history (整理髒亂的歷史)
你的 Commit log 看起來像這樣：
1. `feat: add user login`
2. `fix: syntax error`
3. `wip: styling`
4. `style: fix css`
5. `fix: typo in login`

你希望它變成一個乾淨的 Commit：`feat: implement user login with styling`

```bash
# 啟動互動式 Rebase，處理前 5 個 commit
git rebase -i HEAD~5

# 編輯器會打開，將內容改為：
# pick   <hash1> feat: add user login
# fixup  <hash2> fix: syntax error     <-- fixup 會併入上一個 commit 且丟棄 log
# squash <hash3> wip: styling          <-- squash 會併入但保留 log 供編輯
# fixup  <hash4> style: fix css
# fixup  <hash5> fix: typo in login

# 儲存離開，Git 會跳出編輯器讓你撰寫最終的 Commit Message
```

### Scenario 3: Porting a Hotfix (移植修補程式)
你在 `main` 分支修復了一個嚴重的安全性漏洞 (Commit Hash: `a1b2c3d`)，但這個漏洞也存在於舊版本 `v1.0-maintenance` 分支中，你需要把這個修復也帶過去。

```bash
# 切換到維護分支
git checkout v1.0-maintenance

# 撿選該修復 Commit
git cherry-pick a1b2c3d

# 如果有衝突，解決衝突 -> git add -> git cherry-pick --continue
```