# 核心心智模型：DAG 與物件儲存 / Core Mental Models: DAG and Object Storage

## Mental model｜心智模型

要精通 Git，必須拋棄「Git 儲存的是檔案差異（Diffs）」的直覺，轉而建立「Git 是一個內容定址檔案系統（Content-addressable filesystem）」的模型。

To master Git, you must abandon the intuition that "Git stores file differences (Diffs)" and instead adopt the model that "Git is a content-addressable filesystem."

### 1. 快照而非差異 (Snapshots, not Deltas)
Git 的核心資料庫（Object Storage）儲存的是專案在特定時間點的**完整快照（Snapshot）**。
- **Blob**: 檔案內容。如果兩個檔案內容完全一樣（即使檔名不同），它們共用同一個 Blob。
- **Tree**: 目錄結構。它將檔名對應到 Blob 或其他的 Tree。
- **Commit**: 版本的根節點。它指向一個頂層 Tree，並包含 metadata（作者、時間）以及**指向父 Commit 的指標**。

### 2. 有向無環圖 (The DAG)
所有的 Commit 透過父指標（Parent Pointers）連結，形成一個**有向無環圖（Directed Acyclic Graph, DAG）**。
- **方向性 (Directed)**: Commit 指向它的父節點（過去）。
- **無環 (Acyclic)**: 時間不會倒流，你無法建立一個指向未來的 Commit。
- **不可變性 (Immutability)**: 一旦 Commit 物件被建立，它就是唯讀的。任何「修改歷史」（如 rebase, amend）其實都是在**創造新的 Commit 物件**，並將指標移過去。

### 3. 分支只是指標 (Branches are just Pointers)
這是最關鍵的認知：**分支（Branch）不是一個容器，它只是一個輕量級的、可移動的指標（Reference/Ref），指向某個 Commit。**
- `HEAD`: 一個特殊的指標，通常指向「當前所在的分支名稱」（例如 `ref: refs/heads/main`）。
- 切換分支（Checkout）: 只是將 `HEAD` 指向不同的 Ref，並更新工作目錄（Working Directory）以符合該 Commit 的快照。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Graph-First Thinking (圖形優先思考)
在執行任何複雜操作（Merge, Rebase, Reset）之前，先在腦中或螢幕上視覺化 DAG。
- **Practice**: 使用 `git log --graph --oneline --all` 或 GUI 工具（如 GitKraken, Sourcetree）來確認當前的圖形結構。
- **Benefit**: 當你知道 `rebase` 只是將一串 Commit "剪下" 並 "貼上"（重新計算 Hash）到另一個基底上時，衝突處理會變得更有邏輯。

### 2. Atomic Commits based on DAG (基於 DAG 的原子性提交)
因為 Commit 是 DAG 的節點，每個節點應該代表一個邏輯上完整的狀態。
- **Pattern**: 確保每個 Commit 都是可編譯、可通過測試的。這使得 `git bisect`（二分法除錯）能夠在 DAG 上有效運作。
- **Why**: 如果你的 DAG 中包含「壞掉的中間狀態」，回溯歷史時會非常痛苦。

### 3. Understanding "Detached HEAD" as a Feature (理解並利用 Detached HEAD)
新手常對 "Detached HEAD" 感到恐慌，但資深工程師將其視為一種「唯讀探索模式」。
- **Usage**: 當你想檢查舊版本的 code，但不想建立新分支時，直接 `checkout <commit-hash>`。
- **Mental Model**: 此時 `HEAD` 直接指向 Commit，而不是指向 Branch Ref。你處於「游離」狀態。只要你不在此狀態下大量 commit（否則容易丟失），這是安全的瀏覽方式。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Folder" Fallacy (資料夾誤區)
- **Anti-pattern**: 認為分支是分開的資料夾或儲存空間。
- **Consequence**: 不敢刪除分支，以為會刪除程式碼。
- **Correction**: 刪除分支只是刪除一個指向 Commit 的文字檔（指標）。只要該 Commit 還被其他東西引用（或在 reflog 中），資料就在 Object Storage 裡。

### 2. Fear of Rewriting History (過度恐懼修改歷史)
- **Anti-pattern**: 堅持只用 `merge`，拒絕使用 `rebase` 或 `commit --amend`，導致歷史線混亂（Spaghetti History）。
- **Consequence**: 專案歷史難以閱讀，無法追蹤功能的演進。
- **Correction**: 在**推送到遠端共用分支之前**，修改歷史（整理 DAG）是負責任的表現。只有在「已分享的 Commit」上才需要避免修改歷史。

### 3. Misunderstanding `git reset` (誤解 Reset)
- **Anti-pattern**: 把 `git reset` 當作「復原」按鈕亂按，而不理解它對 Index 和 Working Directory 的影響。
- **Correction**: 用心智模型理解 `reset` 的三個層次：
    1. **Soft**: 只移動 `HEAD` 指標（保留 Index 和 Working Dir）。
    2. **Mixed (Default)**: 移動 `HEAD` + 重置 Index（保留 Working Dir）。
    3. **Hard**: 移動 `HEAD` + 重置 Index + 重置 Working Dir（徹底回到該快照）。

---

## Checklists & workflows｜檢查清單與流程

當你迷失在 Git 操作中，或搞砸了儲存庫狀態時，請使用此決策流程：

### The "Fix-it" Loop based on Mental Model

- [ ] **Stop & Visualize (停下並視覺化)**
    - 執行 `git log --graph --oneline --all --decorate`。
    - 確認 `HEAD` 指向哪裡？
    - 確認 `master`/`main` 指向哪裡？
    - 確認你的目標 Commit 在哪裡？

- [ ] **Identify the State (確認狀態)**
    - 我的工作目錄（Working Directory）髒了嗎？(`git status`)
    - 我是否處於 Detached HEAD 狀態？
    - 我是否在 rebase/merge 的中間狀態？

- [ ] **Pointer Manipulation (指標操作)**
    - **情境 A：我想放棄最近的 commit 但保留檔案修改**
        - Action: `git reset --soft HEAD~1`
        - Model: 將分支指標往回移一格，但將差異留在 Index 中。
    - **情境 B：我 commit 錯了分支**
        - Action:
            1. 建立新指標: `git branch feature/new-topic`
            2. 移動原指標回頭: `git reset --hard HEAD~1`
            3. 切換到新指標: `git checkout feature/new-topic`
    - **情境 C：我把分支指標弄丟了（找不到 commit）**
        - Action: `git reflog` 找回該 Commit 的 SHA-1，然後 `git checkout -b <branch-name> <sha-1>`。

---

## Real-world examples｜實戰案例

### Example 1: The "Rebase" Mental Model
想像你正在 `feature` 分支開發，而 `main` 分支已經有了新的更新。

```text
Before Rebase:
A <- B <- C (main)
      ^
       \
        D <- E (feature)
```

當你執行 `git checkout feature` 然後 `git rebase main` 時，Git 實際上做了什麼？
1.  Git 找到兩者的共同祖先 (B)。
2.  Git 計算 D 和 E 相對於 B 的差異（Diff）。
3.  Git 以 C 為新的基底，**創造** 新的 Commit D' 和 E'（內容相同但父節點不同）。
4.  Git 將 `feature` 指標從 E 移到 E'。

```text
After Rebase:
              D' <- E' (feature)
             /
A <- B <- C (main)
```
*舊的 D 和 E 仍然存在於 Object Storage 中（直到被 Garbage Collected），但不再有分支指向它們。*

### Example 2: Exploring Object Storage
身為資深工程師，你可以直接檢查 Git 的內部資料結構來驗證這個模型。

```bash
# 1. 建立一個簡單的 commit
echo "Hello World" > test.txt
git add test.txt
git commit -m "Initial commit"

# 2. 查看 HEAD 指向的 Commit SHA-1
git rev-parse HEAD
# Output: e.g., a1b2c3d...

# 3. 檢查該 Commit 物件的內容 (Cat-file is your X-ray)
git cat-file -p HEAD
# Output:
# tree <tree-sha>
# author ...
# committer ...
#
# Initial commit

# 4. 檢查 Tree 物件
git cat-file -p <tree-sha>
# Output:
# 100644 blob <blob-sha>    test.txt

# 5. 檢查 Blob 物件 (這就是檔案內容)
git cat-file -p <blob-sha>
# Output:
# Hello World
```

透過這個練習，你會深刻理解：Git 真的只是一堆互相參照的物件（Objects）和指向這些物件的指標（Refs）。