# 程式碼考古：Blame 與 Bisect / Code Forensics: Blame and Bisect

在軟體維護中，除錯（Debugging）往往比開發新功能花費更多時間。Git 不僅是版本控制工具，更是一套強大的法醫鑑識系統（Forensic System）。本章節將探討如何利用 Git 的歷史紀錄來回答兩個關鍵問題：「這行程式碼為什麼會長這樣？（Context）」以及「這個 Bug 是什麼時候產生的？（Regression）」。

## Mental model｜心智模型

### 1. 歷史即地層 (History as Strata)
將 Git 的 commit history 視為地質層。每一行程式碼都是在某個特定時間點沈積下來的。`git blame` 不是用來指責（Blame）誰寫了爛 code，而是為了挖掘該地層沈積時的**上下文（Context）**。
- **核心價值**：程式碼只能告訴你「它怎麼做（How）」，但 Commit Message 和關聯的 PR 才能告訴你「為什麼這樣做（Why）」。

### 2. 二分搜尋法 (Binary Search)
當你不知道 Bug 何時發生，只知道「現在是壞的（Bad）」而「過去某個版本是好的（Good）」時，線性檢查每一個 commit 是極度低效的。
- **Git Bisect** 的運作原理就是演算法中的 **Binary Search**。
- 它將歷史切半，讓你驗證中間點，然後再切半。這將 $O(N)$ 的搜尋複雜度降低為 $O(\log N)$。即使有 1000 個 commits，通常只需要測試約 10 次就能找到元兇。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 高階 Blame 技巧 (Advanced Blame)
不要只會跑 `git blame filename`，這通常只會看到最後一次排版修改。

- **忽略空白變更**：使用 `-w` 參數忽略縮排或格式化造成的干擾。
  ```bash
  git blame -w src/main.js
  ```
- **追蹤程式碼搬移**：如果程式碼是從別的檔案搬過來的，使用 `-C` (Copy) 或 `-M` (Move) 來追蹤其原始出處。
  ```bash
  git blame -C -C -M src/utils.js
  ```
- **行範圍查詢**：只關心第 40 到 60 行的歷史。
  ```bash
  git blame -L 40,60 src/main.js
  ```

### 2. 自動化 Bisect (Automated Bisect)
資深工程師的標誌是「能自動化就不手動」。`git bisect run` 可以讓電腦幫你跑測試。

- **手動模式**：標記好壞，Git 切換 commit，你手動編譯/測試，告訴 Git `good` 或 `bad`。
- **自動模式**：寫一個 script，如果測試通過回傳 `0`，失敗回傳 `1`。
  ```bash
  # 開始 bisect
  git bisect start HEAD <last-known-good-tag>
  
  # 交給 script 自動跑
  git bisect run ./test-script.sh
  ```

### 3. 使用 Pickaxe 搜尋 "消失" 的程式碼
有時候 Bug 是因為某行程式碼被**刪除**了，這時 `git blame` 幫不上忙（因為行已經不在了）。
- 使用 `git log -S` (Pickaxe) 來搜尋特定字串「何時被加入」或「何時被刪除」。
  ```bash
  # 找出是誰刪除了 "API_KEY" 這個變數
  git log -S "API_KEY" path/to/file
  ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目相信 Blame 的作者 (Trusting the Author Blindly)
- **陷阱**：看到某行 code 是同事 A 提交的，就認為是他寫的邏輯。
- **真相**：同事 A 可能只是執行了 Prettier/Linter 進行全域格式化，或者只是搬移了檔案。
- **解法**：務必配合 `git show <commit-id>` 檢查該次 commit 的完整變更，確認是否為邏輯修改。

### 2. Bisect 時未清理環境 (Dirty Environment during Bisect)
- **陷阱**：在切換 commit 的過程中，沒有清除編譯快取或 `node_modules`，導致舊的 artifact 影響測試結果，造成 Bisect 誤判（False Positive/Negative）。
- **解法**：在測試腳本中，確保每次都執行 clean build。

### 3. 歷史紀錄不乾淨 (Messy History)
- **陷阱**：專案中有大量「無法編譯」或「測試本身就壞掉」的 commit。這會導致 Bisect 過程中頻繁遇到無法驗證的節點。
- **解法**：
  - 團隊應維持 Main branch 的綠燈（Green Build）。
  - 使用 `git bisect skip` 跳過無法測試的 commit。

### 4. 誤用 Squash Merge 導致粒度過大
- **陷阱**：如果一個 PR 包含了 50 個檔案的變更，且被 Squash 成一個 commit。當 Bisect 定位到這個 commit 時，你仍然需要在大海撈針。
- **解法**：保持適當的 commit 粒度（Atomic Commits），讓每個 commit 只做一件事。

---

## Checklists & workflows｜檢查清單與流程

### 🔍 鑑識調查流程 (Forensic Investigation Workflow)

當遇到一個不知何時產生的 Bug：

- [ ] **Step 1: 定義範圍**
  - 確認當前版本（Bad）與上一個已知穩定版本（Good）。
- [ ] **Step 2: 準備測試案例**
  - 能否寫一個單元測試來重現此 Bug？（這是自動化 Bisect 的關鍵）。
- [ ] **Step 3: 執行 Bisect**
  - [ ] `git bisect start`
  - [ ] `git bisect bad` (Current)
  - [ ] `git bisect good <tag-or-sha>`
  - [ ] 如果有 script: `git bisect run <script>`
  - [ ] 如果手動: 驗證 -> `git bisect good/bad` -> 重複直到找到。
- [ ] **Step 4: 分析兇手 (Culprit Analysis)**
  - 找到 commit 後，執行 `git show <sha>`。
  - 閱讀 Commit Message 與關聯的 Pull Request。
  - [ ] **關鍵**：不要只修復 Bug，要理解當初為什麼這樣寫，避免修復了 Bug 卻破壞了當初的 Edge case 處理。
- [ ] **Step 5: 恢復現場**
  - `git bisect reset` 回到工作狀態。

### 🕵️‍♂️ 代碼考古流程 (Blame Workflow)

當想知道某段程式碼的由來：

- [ ] `git blame -w <file>` (忽略空白)。
- [ ] 找到 Commit ID。
- [ ] `git show <commit-id>` 查看該次提交的完整 diff。
- [ ] 如果該 commit 只是 "Refactor" 或 "Move"，針對該行之前的版本繼續 blame (使用 `git blame <commit-id>^ -- <file>`)。

---

## Real-world examples｜實戰案例

### 案例一：自動化抓出效能退化 (Performance Regression)

**情境**：App 啟動時間從 2 秒變成了 5 秒，但不確定是過去三個月內哪一次 merge 造成的。

**解決方案**：
1. 建立一個 script `check_perf.sh`：
   ```bash
   #!/bin/bash
   # 建置專案
   npm install && npm run build
   # 執行效能測試，如果啟動時間 > 3s 則 exit 1 (Bad)，否則 exit 0 (Good)
   node perf-test.js --threshold 3000
   ```
2. 執行自動化 Bisect：
   ```bash
   git bisect start
   git bisect bad HEAD
   git bisect good v2.0.0
   git bisect run ./check_perf.sh
   ```
3. **結果**：Git 會自動跑完幾十個版本，最後停在導致效能變慢的那個 Commit 上。喝杯咖啡回來就破案了。

### 案例二：追蹤幽靈程式碼 (The Phantom Code)

**情境**：你發現一段處理 `UserSession` 的邏輯不見了，導致登入功能異常，但 `git blame` 當前檔案看不出端倪，因為那幾行已經不在檔案裡了。

**解決方案**：
使用 Pickaxe 搜尋字串變更。

```bash
# 搜尋 "validateUserSession" 這個字串涉及的變更
# -S: 搜尋字串出現次數的變化（新增或刪除）
git log -S "validateUserSession" --source --all
```

**結果**：找到一個月前的一個 Commit，訊息寫著 "Refactor: remove unused code"，原來是同事誤以為該函數沒被使用而刪除了。

### 案例三：忽略排版雜訊 (Ignoring the Noise)

**情境**：團隊剛導入 Prettier，整個檔案都被重新格式化了。你現在想知道某個函數的核心邏輯是誰寫的，但 `git blame` 每一行都顯示是 "Style Fix" 的那個 Commit。

**解決方案**：
使用 `git blame` 搭配忽略參數，或使用 GitHub/GitLab UI 上的 "Blame (ignore revs)" 功能。

```bash
# 忽略特定的 commit (例如那個全域格式化的 commit hash)
git blame --ignore-rev <style-fix-commit-hash> src/logic.ts

# 或者設定全域忽略檔案 (將格式化 commits 記錄在 .git-blame-ignore-revs)
git config blame.ignoreRevsFile .git-blame-ignore-revs
```