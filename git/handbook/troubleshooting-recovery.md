# 災難救援與 Reflog 實戰 / Troubleshooting and Recovery with Reflog

## Mental model｜心智模型

### 1. Git 幾乎不刪除資料 (Git rarely deletes data)
許多開發者在執行 `git reset --hard` 或刪除分支時會感到恐慌，認為資料「消失」了。但 Git 的底層設計是一個 **Append-only 的物件資料庫**。
當你「刪除」一個分支，你只是移除了指向某個 Commit 的指標（標籤）；當你「重置」程式碼，你只是將 HEAD 指標移到了另一個地方。原本的 Commit 物件依然存在於 `.git/objects` 中，直到 Git 執行垃圾回收（Garbage Collection, GC，預設通常為兩週以上）前，它們都是可復原的。

### 2. Reflog 是你的時光機軌跡 (Reflog is your breadcrumb trail)
如果說 `git log` 是專案的歷史（Project History），那麼 `git reflog` 就是**你個人的操作歷史（Action History）**。
Reflog 記錄了 `HEAD` 指標在本地端每一次的移動軌跡（checkout, commit, reset, merge, rebase）。即使你 Reset 掉了一個 Commit 導致它在 `git log` 中消失，它依然會存在於 `git reflog` 中。

> **Mental Image**: 想像你在攀岩。`git commit` 是打釘子，`git reset` 是解開繩索跳回上一個釘子。雖然你看不到剛才打的釘子了，但 Reflog 是一台攝影機，它錄下了你「曾經站在那個釘子上」的畫面，讓你可以隨時回去。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Reflog 撤銷錯誤的 Reset
這是最經典的救援模式。當你誤用了 `git reset --hard` 導致剛寫好的程式碼消失時：

```bash
# 1. 查看操作紀錄，找到災難發生前的那個點（例如 HEAD@{1}）
git reflog

# 2. 將 HEAD 指標強制指回該時間點
git reset --hard HEAD@{1}
```

### 2. 復活被刪除的分支 (Resurrecting deleted branches)
如果你不小心刪除了一個還沒 Merge 的分支 `feature-login`：

```bash
# 1. 在 Reflog 中尋找該分支最後一次 Commit 的 SHA-1 hash (假設是 a1b2c3d)
git reflog

# 2. 原地重建分支
git branch feature-login a1b2c3d
```

### 3. 處理 Detached HEAD 狀態
當你 Checkout 到某個舊的 Commit（而非分支名）時，Git 會進入 **Detached HEAD** 狀態。這不是錯誤，只是 Git 告訴你：「你現在沒有在任何分支上，新的 Commit 就像孤兒一樣，一旦切換走就會找不到。」

**Best Practice**:
如果你在 Detached HEAD 狀態下寫了程式碼，**立刻建立一個暫存分支**來保存它：
```bash
git switch -c temp-fix-branch
```

### 4. 預防勝於治療：備份分支 (The "Backup Branch" Pattern)
在執行高風險操作（如複雜的 Rebase、互動式 Rebase 或 Reset）之前，先為當前狀態貼上一個標籤：

```bash
# 在做傻事之前，先存檔
git branch backup/feature-x-before-rebase
```
如果操作失敗，隨時可以 `git reset --hard backup/feature-x-before-rebase`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目刪除 `.git` 資料夾 (The Nuclear Option)
**Anti-pattern**: 遇到 Merge Conflict 或狀態混亂時，直接刪除整個 repo 重新 clone。
**Why it's bad**: 你會失去所有未推送到遠端的 Reflog 紀錄、Stash 內容以及本地的 Hooks 設定。這是最後手段，絕不該是第一反應。

### 2. 依賴 IDE 的 Undo 而非 Git
**Anti-pattern**: 誤刪檔案後，試圖用編輯器的 Ctrl+Z 或 Local History 來救。
**Why it's bad**: 雖然有時有效，但 IDE 的歷史紀錄通常不包含 Git 的 metadata（如 Commit message、Author）。使用 Git 內建的救援機制更可靠且完整。

### 3. 在 Detached HEAD 上長期工作
**Anti-pattern**: 在 Detached HEAD 狀態下 Commit 了多次，然後直接 `git checkout main`。
**Consequence**: 這些 Commits 會變成 "Dangling Commits"（懸空 Commit）。雖然可以透過 Reflog 找回，但如果時間過久被 GC 清除，就真的救不回來了。

### 4. 誤以為 `git revert` 是 `git reset`
**Pitfall**: 想要「刪除」剛才的 Commit，卻用了 `git revert`。
**Correction**: `revert` 會新增一個「反向操作」的 Commit，保留歷史紀錄；`reset` 則是將時間倒流。在已經 Push 到公共分支的情況下，請用 `revert`；在本地私有分支，可用 `reset`。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 The Panic Button Protocol (災難發生時的標準動作)

當你意識到「我搞砸了」或「程式碼不見了」，請立即停止手邊動作，依照以下順序處理：

- [ ] **Stop**: 停止任何新的 Commit 或 Checkout 動作，避免 Reflog 被洗版。
- [ ] **Status**: 執行 `git status` 確認當前狀態（是否在 Detached HEAD？是否有未追蹤檔案？）。
- [ ] **Log**: 執行 `git reflog` 查看最近 10 筆操作，確認災難發生前的 `HEAD@{n}`。
- [ ] **Backup**: (選用) 如果當前工作區還有未 Commit 的修改，先執行 `git stash` 或複製檔案到外部資料夾。
- [ ] **Recovery**:
    - 如果是 Reset 錯了：`git reset --hard HEAD@{n}`
    - 如果是分支刪了：`git branch <branch-name> <commit-hash>`
    - 如果是 Commit 丟了：`git cherry-pick <commit-hash>`

### Decision Tree: How to recover?

1. **我剛剛 Commit 了，但我後悔了，想回到 Commit 前的狀態（保留檔案修改）：**
   -> `git reset --soft HEAD~1`
2. **我剛剛 Commit 了，我想徹底放棄這次修改（不保留檔案）：**
   -> `git reset --hard HEAD~1`
3. **我執行了 `git reset --hard`，但我發現我刪錯了，我想找回剛剛那個 Commit：**
   -> `git reflog` -> 找到 hash -> `git reset --hard <hash>`
4. **我修改了歷史 (Rebase/Amend)，現在後悔了，想回到修改前：**
   -> `git reflog` -> 找到 `rebase (start)` 或 `commit (amend)` 之前的 hash -> `git reset --hard <hash>`

---

## Real-world examples｜實戰案例

### Case 1: 誤用 Reset Hard 導致程式碼遺失

**情境**：你正在開發功能，想撤銷最近一次 Commit，結果手快打了 `--hard`，發現連工作區辛苦寫了半天的程式碼都不見了。

```bash
# 1. 災難發生
$ git reset --hard HEAD~1
HEAD is now at a1b2c3d Fix typo

# 2. 驚覺不對，查看 Reflog
$ git reflog
a1b2c3d HEAD@{0}: reset: moving to HEAD~1
e4f5g6h HEAD@{1}: commit: WIP: implementing complex algorithm  <-- 這是你要找回的！
a1b2c3d HEAD@{2}: commit: Fix typo

# 3. 救援
$ git reset --hard HEAD@{1}
HEAD is now at e4f5g6h WIP: implementing complex algorithm

# 4. 驗證
# 檔案回來了，世界和平。
```

### Case 2: 找回 `git commit --amend` 覆蓋掉的舊內容

**情境**：你提交了一個 Commit，然後用 `--amend` 修改了它。後來發現新寫的邏輯有錯，舊的那個版本其實是對的。

```bash
$ git reflog
890abcd HEAD@{0}: commit (amend): Feature X implementation (v2)
1234567 HEAD@{1}: commit: Feature X implementation (v1)  <-- 被覆蓋掉的舊版本其實還在

# 救援方式 A：直接 Reset 回去
$ git reset --hard HEAD@{1}

# 救援方式 B：如果你想保留 v2，但把 v1 找回來變成另一個分支參考
$ git branch feature-x-v1-backup HEAD@{1}
```

### Case 3: 搶救 Detached HEAD 的孤兒 Commits

**情境**：你 Checkout 到某個 Tag 檢查 Bug，順手修復並 Commit 了兩次，然後習慣性地 `git switch main`，這時 Git 警告你留下了孤兒 Commit。

```bash
# 1. 發現切換分支後，剛剛修的 code 不見了
$ git reflog
aabbccd HEAD@{0}: checkout: moving from 9988776 to main
9988776 HEAD@{1}: commit: Fix critical bug part 2
5544332 HEAD@{2}: commit: Fix critical bug part 1
aabbccd HEAD@{3}: checkout: moving from main to v1.0.0

# 2. 建立一支新分支指向剛剛那個孤兒 Commit (HEAD@{1})
$ git branch fix/from-detached-head 9988776

# 3. 現在該分支包含了 part 1 和 part 2 的修復
$ git switch fix/from-detached-head
```