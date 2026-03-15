# 合併策略與衝突解決指南 / Merge Strategies and Conflict Resolution

合併（Merge）是 Git 協作的核心，也是最容易引發焦慮的環節。本章節將協助你建立正確的合併心智模型，區分不同的合併策略（Fast-forward vs. Merge Commit），並提供處理複雜衝突（Merge Conflicts）的標準作業程序。

## Mental model｜心智模型

### 1. 三路合併 (3-Way Merge)
理解衝突的關鍵在於理解 Git 如何進行合併。除了 Fast-forward 之外，標準的合併並非只是比較兩個分支，而是涉及 **三個提交點**：
1.  **Base (Common Ancestor)**：兩個分支分岔的共同祖先。
2.  **Local (Ours/HEAD)**：你當前所在的分支。
3.  **Remote (Theirs)**：你要合併進來的分支。

Git 會比較 `Base` 到 `Local` 的變化，以及 `Base` 到 `Remote` 的變化。
- 如果只有一方修改了某行程式碼，Git 會自動採用該修改。
- 如果雙方都修改了同一行（且內容不同），Git 無法決定誰是對的，這就是 **衝突 (Conflict)**。

> **Key Insight**: 解決衝突不是在「二選一」，而是在「整合雙方的意圖」。

### 2. 合併的物理意義
- **Fast-forward (快轉)**：
  - 物理意義：沒有分岔，只是將指標（Pointer）向前移動。
  - 結果：線性的歷史紀錄，看不出「曾經有個分支存在」。
- **Merge Commit (Recursive / Ort strategy)**：
  - 物理意義：將兩個分岔的歷史線重新綁在一起，產生一個新的「繩結」（Merge Commit）。
  - 結果：保留了分支開發的上下文（Context），歷史線呈現 DAG（有向無環圖）結構。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 策略選擇：何時 FF，何時 Merge Commit？
在團隊規範中，應明確定義何時使用哪種策略：

| 情境 | 建議策略 | 指令 / 設定 | 理由 |
| :--- | :--- | :--- | :--- |
| **同步上游更新** (Pulling changes) | **Rebase** (or FF-only) | `git pull --rebase` | 避免在本地產生無意義的 "Merge branch 'main' of..." 提交，保持歷史乾淨。 |
| **合併 Feature 分支到 Main** | **Explicit Merge** | `git merge --no-ff` | 強制產生 Merge Commit，明確標示「這個功能是在此處完成並合併的」，方便日後 Revert 或追蹤。 |
| **短期/瑣碎的修復** | **Squash Merge** | (GitHub/GitLab UI 選項) | 將瑣碎的 commit (typo, wip) 壓縮成一個乾淨的 commit 進入主線。 |

### 2. 設定強大的 Merge Tool
不要試圖在純文字編輯器中看著 `<<<<<<<` 手動修復複雜衝突。配置一個圖形化工具（如 VS Code, Beyond Compare, KDiff3）是專業工程師的標配。

```bash
# 設定 VS Code 為預設 merge tool
git config --global merge.tool code
git config --global mergetool.code.cmd 'code --wait --merge $REMOTE $LOCAL $BASE $MERGED'
```

### 3. 啟用 `git rerere` (Reuse Recorded Resolution)
如果你在維護長期的 Feature branch，並頻繁 rebase 主線，你可能會重複解決相同的衝突。啟用 `rerere` 可以讓 Git 記住你解決衝突的方式並自動套用。

```bash
git config --global rerere.enabled true
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Foxtrot" Merge (狐步舞合併)
這是最常見的歷史污染源。
- **現象**：在 Feature branch 上直接執行 `git merge main` 來同步最新程式碼，然後再將 Feature branch merge 回 main。
- **後果**：歷史線會像狐步舞一樣交叉混亂，導致 `git log --graph` 難以閱讀，且破壞了 `first-parent` 的歷史純淨度。
- **修正**：在 Feature branch 上想同步主線時，請使用 **Rebase** (`git rebase main`)，而非 Merge。

### 2. 盲目接受 "Ours" 或 "Theirs"
- **現象**：遇到衝突時，不看程式碼邏輯，直接使用 `git checkout --ours file.js` 或 `git checkout --theirs file.js`。
- **後果**：可能會遺失對方的關鍵修改（例如對方加了安全檢查，你加了功能，選邊站會導致其中一個消失）。
- **修正**：永遠檢查 **Base**，理解雙方為何修改，通常正確答案是「兩者的組合」。

### 3. 提交衝突標記 (Committing Conflict Markers)
- **現象**：不小心將包含 `<<<<<<< HEAD` 的檔案 add 並 commit 進去。
- **後果**：破壞 Build，造成團隊困擾。
- **修正**：使用 Linter 或 Pre-commit hook 檢查程式碼中是否殘留衝突標記。

---

## Checklists & workflows｜檢查清單與流程

### 標準衝突解決流程 (Standard Conflict Resolution Workflow)

當你執行 `git merge` 或 `git rebase` 遇到衝突時：

1.  **保持冷靜，評估狀態**
    - [ ] 執行 `git status` 查看哪些檔案衝突。
    - [ ] 執行 `git log --oneline --graph --all -n 10` 確認當前位置。

2.  **啟動工具**
    - [ ] 執行 `git mergetool` 啟動圖形化介面。

3.  **解決衝突 (針對每個檔案)**
    - [ ] **Left (Local)**: 我的修改是什麼？
    - [ ] **Right (Remote)**: 對方的修改是什麼？
    - [ ] **Center (Base)**: 原本長怎樣？（這是理解衝突的關鍵）
    - [ ] **Result**: 合併邏輯。是否需要同時保留雙方邏輯？是否重構了函數名稱？

4.  **驗證與提交**
    - [ ] 解決完所有檔案後，執行 `git status` 確認所有衝突已標記為 resolved。
    - [ ] **關鍵步驟**：執行專案的 Test Suite (e.g., `npm test`)。**不要假設解決衝突後的程式碼能跑。**
    - [ ] 執行 `git commit` (如果是 merge) 或 `git rebase --continue` (如果是 rebase)。

### 決策樹：我該用哪種合併？

```text
我要將 Code 合併到哪裡？
├── 本地分支同步遠端對應分支 (e.g., local main <- origin/main)
│   └── 使用 `git pull --rebase` (保持線性)
│
├── Feature 分支合併回 Main/Master
│   ├── 團隊要求乾淨的線性歷史？
│   │   └── 使用 Squash Merge 或 Rebase 後 Fast-forward
│   │
│   └── 團隊希望保留開發軌跡？
│       └── 使用 `git merge --no-ff` (產生 Merge Commit)
│
└── Feature 分支同步 Main 的最新進度
    └── 使用 `git rebase main` (不要用 merge main，避免 Foxtrot)
```

---

## Real-world examples｜實戰案例

### 案例 1：語意衝突 (Semantic Conflict)
這是一種 Git 偵測不到，但會導致 Bug 的衝突。

**情境**：
- **Dev A (Branch A)**: 修改了函數 `calculatePrice(price)` 的內部實作，讓它回傳 `float` 而不是 `int`。
- **Dev B (Branch B)**: 在另一個檔案呼叫了 `calculatePrice`，並假設它回傳 `int` 進行字串處理。
- **Merge**: Git 認為修改的是不同檔案，**自動合併成功**。
- **結果**: Runtime Error。

**解決方案**:
- 機器無法解決這種衝突。這依賴於 **CI/CD 自動化測試**。
- **Rule**: Merge 後必須跑測試，而不僅僅是編譯通過。

### 案例 2：處理 `package-lock.json` 或 `yarn.lock` 衝突
這是前端開發最頭痛的衝突。

**錯誤做法**：
手動編輯 lock file 的衝突標記（極易破壞格式）。

**正確做法**：
1. 解除 lock file 的衝突狀態（例如先接受 ours 或 theirs，或者直接刪除 lock file）。
2. 重新產生 lock file。

```bash
# 當 yarn.lock 衝突時
git checkout --ours yarn.lock  # 先隨便選一邊，讓 git 閉嘴
yarn install                   # 讓套件管理器根據 package.json 重新生成正確的 lock file
git add yarn.lock              # 提交正確的版本
```

### 案例 3：Rebase 過程中的 "Conflict Hell"
當你太久沒同步主線，累積了 50 個 commits，現在要 `git rebase main`，結果發現每一個 commit 都要解衝突。

**解決方案**:
1. **Abort**: `git rebase --abort`。
2. **Squash First**: 先在自己的分支上將這 50 個 commits 壓縮（Interactive Rebase）成幾個邏輯完整的 commits。
3. **Rebase Again**: 這樣你只需要解決少數幾次衝突，而不是 50 次。