# 1. 前言與學習目標 (Introduction & Learning Objectives)

在大型軟體專案中，程式碼庫（Codebase）往往累積了數年的歷史與成千上萬次提交。當生產環境出現 Regression（回歸錯誤）且無法立即定位原因時，資深工程師的價值在於能否利用 Git 提供的「考古工具」快速切入問題核心。本章不只教你指令，更教你如何像法醫一樣分析程式碼屍體。

In large-scale software projects, the codebase often accumulates years of history and thousands of commits. When a regression occurs in production and the root cause is not immediately apparent, the value of a Senior Engineer lies in their ability to use Git's "forensic tools" to quickly pinpoint the issue. This chapter teaches not just the commands, but how to analyze code artifacts like a forensic investigator.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精通 `git bisect` 自動化除錯**：不僅是手動二分搜尋，更學會撰寫腳本讓 Git 自動找出引入 Bug 的 Commit。
    **Master `git bisect` automation**: Go beyond manual binary search and learn to write scripts that let Git automatically identify the commit that introduced a bug.
2.  **掌握進階 `git blame` 技巧**：學會忽略空白變更與程式碼搬移，追蹤程式碼真正的起源，而非僅僅看到最後一次 Refactor 的人。
    **Master advanced `git blame` techniques**: Learn to ignore whitespace changes and code moves to trace the true origin of code, rather than just seeing who last refactored it.
3.  **使用 `git log` 進行內容搜尋**：利用 Pickaxe (`-S`, `-G`) 與 Line History (`-L`) 功能，精準定位特定函數或變數的變更歷史。
    **Use `git log` for content search**: Utilize the Pickaxe (`-S`, `-G`) and Line History (`-L`) features to precisely locate the change history of specific functions or variables.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Git 作為有向無環圖 (Git as a DAG)
要理解 Git 的除錯能力，必須將 Git 歷史視為一個**有向無環圖（DAG）**。除錯過程本質上是在這個圖上進行搜尋演算法。
To understand Git's debugging capabilities, you must view Git history as a **Directed Acyclic Graph (DAG)**. Debugging is essentially performing search algorithms on this graph.

-   **`git bisect`**：這是在 DAG 上進行**二分搜尋法（Binary Search）**。在線性歷史中，它的時間複雜度是 $O(\log N)$。這意味著即使有 10,000 個 commits，你只需要測試約 13-14 次即可找到壞掉的點。
    **`git bisect`**: This is a **Binary Search** on the DAG. In a linear history, its time complexity is $O(\log N)$. This means that even with 10,000 commits, you only need to test about 13-14 times to find the breaking point.

### 2.2 考古學而非指責 (Archaeology, not Blame)
雖然指令叫做 `blame`，但在資深工程師的心智模型中，這代表「Context Discovery（脈絡發現）」。
Although the command is called `blame`, in a Senior Engineer's mental model, this represents "Context Discovery".

-   **Code Movement vs. Code Change**：Git 其實不儲存 Diff，而是儲存 Snapshots。所謂的「移動」或「複製」是 Git 在讀取時動態計算出來的。理解這一點，你就能透過參數告訴 Git：「不要只看檔案名稱，去追蹤內容的雜湊值（Hash）」，從而跨越檔案重構的邊界找到原始作者。
    **Code Movement vs. Code Change**: Git doesn't actually store diffs; it stores snapshots. So-called "moves" or "copies" are calculated dynamically by Git at read time. Understanding this allows you to tell Git via arguments: "Don't just look at filenames, track the content hash," thereby crossing refactoring boundaries to find the original author.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 縮短平均修復時間 (Reducing MTTR)
在 DevOps 與 SRE 的指標中，**MTTR (Mean Time To Recovery)** 是關鍵。當 Production 發生 Incident，且無法透過簡單的 Rollback 解決（例如資料庫 schema 已變更，或 Bug 潛伏已久），快速定位 `Bad Commit` 是止血的第一步。
In DevOps and SRE metrics, **MTTR (Mean Time To Recovery)** is crucial. When a production incident occurs and cannot be solved by a simple rollback (e.g., database schema has changed, or the bug has been latent for a long time), quickly locating the `Bad Commit` is the first step to stopping the bleeding.

### 3.2 大型單體與微服務的除錯 (Debugging Monoliths vs. Microservices)
-   **Monorepo / Monolith**：歷史線長且複雜，多人協作導致 `git blame` 充滿雜訊（如 formatting changes）。這時 `git bisect` 配合自動化測試腳本是神器。
    **Monorepo / Monolith**: History is long and complex; multi-person collaboration fills `git blame` with noise (like formatting changes). Here, `git bisect` paired with automated test scripts is a godsend.
-   **Microservices**：雖然單一 Repo 歷史較短，但問題常跨服務。你可能需要在 Library 的 Repo 中使用 Git 考古工具，找出是哪個版本的共用套件導致了 API 行為改變。
    **Microservices**: Although a single repo history is shorter, issues often span across services. You might need to use Git forensic tools within a shared library's repo to find which version of the package caused an API behavior change.

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例：自動化定位回歸錯誤 (Scenario: Automating Regression Finding)

假設你接手維護一個交易系統，發現 `calculate_fee()` 函數在某些邊界條件下回傳錯誤數值。這個 Bug 似乎存在了幾個月，你不確定是誰、在什麼時候引入的。
Suppose you maintain a transaction system and discover that the `calculate_fee()` function returns incorrect values under certain edge cases. This bug seems to have existed for months, and you are unsure who introduced it or when.

#### Step 1: 準備測試腳本 (Prepare the Test Script)
資深工程師不會手動一次次測試。我們先寫一個腳本 `test_bug.sh`，如果 Bug 存在回傳 `1`，正常則回傳 `0`。
A Senior Engineer doesn't test manually over and over. First, we write a script `test_bug.sh` that returns `1` if the bug exists, and `0` if it works correctly.

```bash
#!/bin/bash
# test_bug.sh

# Run the unit test specifically for the fee calculation
# 執行針對費用計算的單元測試
npm test -- test/fee_calculation.test.js

# Note: Ensure the test command returns exit code 0 on success, non-zero on failure.
# 注意：確保測試指令在成功時回傳 exit code 0，失敗時回傳非 0。
```

#### Step 2: 啟動 Bisect (Start Bisect)
找到一個確定是好的 Commit（例如 `v1.0.0`）和目前壞掉的 `HEAD`。
Identify a known good commit (e.g., `v1.0.0`) and the current broken `HEAD`.

```bash
git bisect start
git bisect bad HEAD      # Current version is bad / 目前版本是壞的
git bisect good v1.0.0   # v1.0.0 was good / v1.0.0 是好的
```

#### Step 3: 自動化執行 (Run Automation)
讓 Git 自動跑二分搜尋。
Let Git run the binary search automatically.

```bash
git bisect run ./test_bug.sh
```

Git 會自動 checkout 中間的 commit，執行腳本，根據 exit code 標記 good/bad，直到鎖定唯一的 offending commit。
Git will automatically checkout intermediate commits, run the script, mark them as good/bad based on the exit code, until it isolates the single offending commit.

#### Step 4: 深入分析 (Deep Analysis with Advanced Blame)
假設 Bisect 告訴你 Commit `a1b2c3d` 是兇手。你查看該 Commit，發現它只是把程式碼從 `OldFile.js` 搬到 `NewFile.js`。
Suppose Bisect tells you Commit `a1b2c3d` is the culprit. You check that commit and see it only moved code from `OldFile.js` to `NewFile.js`.

這時，普通的 `git blame NewFile.js` 只會顯示搬移的人。你需要：
At this point, a normal `git blame NewFile.js` only shows the person who moved it. You need:

```bash
# -w: Ignore whitespace (忽略空白)
# -C: Detect copies/moves in the same commit (偵測同一次 commit 內的複製/移動)
# -C -C: Detect copies/moves from other files in the commit that created the file (偵測建立檔案時從其他檔案來的移動)
# -C -C -C: Detect copies/moves from any file in any commit (最強力模式：偵測任何 commit 中任何檔案的移動)

git blame -w -C -C -C src/core/NewFile.js
```

這能讓你穿透 Refactor 的迷霧，看到這行程式碼在 3 年前最初被寫下時的作者與 Commit Message。
This allows you to pierce through the fog of refactoring and see the original author and commit message from when that line of code was first written 3 years ago.

#### Step 5: 搜尋特定邏輯變更 (Search for Specific Logic Changes)
如果你只想知道 `MAX_RETRY` 這個常數什麼時候被改過，不要用 `grep`，用 `log -S` (Pickaxe)：
If you only want to know when the constant `MAX_RETRY` was changed, don't use `grep`, use `log -S` (Pickaxe):

```bash
# Find commits that added or removed the string "MAX_RETRY"
# 找出新增或移除了 "MAX_RETRY" 字串的 commits
git log -S "MAX_RETRY" --source --all
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在 Bisect 過程中遇到 Build Failure (Build Failures During Bisect)
-   **錯誤**：當 `git bisect` checkout 到某個歷史版本時，該版本可能因為語法錯誤或依賴問題無法編譯（Build Broken）。如果直接標記為 `bad`，會誤導二分搜尋的方向。
    **Mistake**: When `git bisect` checks out a historical version, it might fail to build due to syntax errors or dependency issues. Marking it directly as `bad` will mislead the binary search.
-   **修正**：使用 `git bisect skip`。這會告訴 Git：「這個點無法測試，請換另一個附近的點」。
    **Correction**: Use `git bisect skip`. This tells Git: "This point is untestable, please pick another nearby point."

### 5.2 過度依賴 Commit Message 搜尋 (Over-reliance on Commit Message Search)
-   **錯誤**：只用 `git log --grep="fix bug"` 來找問題。很多時候，引入 Bug 的 Commit Message 寫的是 "Refactor user module" 或 "Update dependencies"，完全看不出與 Bug 的關聯。
    **Mistake**: Relying solely on `git log --grep="fix bug"` to find issues. Often, the commit introducing the bug has a message like "Refactor user module" or "Update dependencies", showing no obvious link to the bug.
-   **修正**：使用 `git log -S` (Pickaxe) 或 `git log -L` (Line History) 來搜尋**程式碼內容的變更**，而非訊息。
    **Correction**: Use `git log -S` (Pickaxe) or `git log -L` (Line History) to search for **changes in code content**, not messages.

### 5.3 忽略 `.git-blame-ignore-revs` (Ignoring `.git-blame-ignore-revs`)
-   **錯誤**：團隊進行了一次全域的 Prettier/Linter 格式化，導致 `git blame` 全部變成格式化那天的紀錄，失去了歷史脈絡。
    **Mistake**: The team performed a global Prettier/Linter formatting, causing `git blame` to show only the formatting date for everything, losing historical context.
-   **修正**：設定 `.git-blame-ignore-revs` 檔案，將純格式化的 Commit Hash 加入其中，並配置 Git 使用它。
    **Correction**: Set up a `.git-blame-ignore-revs` file, add the pure formatting commit hashes to it, and configure Git to use it.
    ```bash
    git config blame.ignoreRevsFile .git-blame-ignore-revs
    ```

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何在不了解專案全貌的情況下，快速定位一個邏輯錯誤？
**How do you quickly pinpoint a logic error without understanding the full scope of the project?**

-   **重點回答**：提及 `git bisect`。強調**二分搜尋法**的效率（$O(\log N)$）。
-   **資深亮點**：提到 `git bisect run` 自動化測試，以及如何處理 "Untestable builds" (使用 `skip`)。這顯示你有處理真實世界混亂歷史的經驗。
-   **Key Points**: Mention `git bisect`. Emphasize the efficiency of **Binary Search** ($O(\log N)$).
-   **Senior Highlight**: Mention `git bisect run` for automation, and how to handle "Untestable builds" (using `skip`). This shows experience dealing with real-world messy history.

### Q2: 我們的 Codebase 經過多次檔案搬移與重構，`git blame` 幾乎失效，該怎麼辦？
**Our codebase has undergone multiple file moves and refactors, rendering `git blame` almost useless. What do you do?**

-   **重點回答**：解釋 Git 追蹤的是內容而非檔案。
-   **資深亮點**：具體列出 `git blame -w -C -C -C` 參數組合。說明 `-w` 忽略空白，`-C` 跨檔案追蹤內容複製。也可以提到 `git log -L :funcName:filePath` 來追蹤特定函數的演變。
-   **Key Points**: Explain that Git tracks content, not files.
-   **Senior Highlight**: Specifically list the `git blame -w -C -C -C` parameter combination. Explain `-w` ignores whitespace, and `-C` tracks content copies across files. Also mention `git log -L :funcName:filePath` to track the evolution of a specific function.

### Q3: 什麼是 "Pickaxe" 搜尋？它與一般的 grep 有何不同？
**What is "Pickaxe" search? How does it differ from a standard grep?**

-   **重點回答**：`git log -S <string>`。一般的 grep 搜尋當前檔案內容；`log --grep` 搜尋 Commit 訊息；Pickaxe 則是搜尋**Diff 的內容**。
-   **資深亮點**：解釋這能找出「某行程式碼是在哪一次 Commit 被**新增**或**刪除**的」，特別適用於尋找變數何時被移除，或某個 Side Effect 呼叫何時被加入。
-   **Key Points**: `git log -S <string>`. Standard grep searches current file content; `log --grep` searches commit messages; Pickaxe searches **Diff content**.
-   **Senior Highlight**: Explain that this finds "in which commit a line of code was **added** or **removed**", especially useful for finding when a variable was deleted or when a side-effect call was introduced.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Bisect is Binary Search**: 利用 `git bisect run` 將 $O(N)$ 的手動除錯轉化為 $O(\log N)$ 的自動化流程。
2.  **Blame is for Context**: 使用 `-w` (ignore whitespace) 與 `-C` (detect copies) 來穿透重構，找到真正的程式碼起源。
3.  **Search the Diff**: 使用 `git log -S` (Pickaxe) 搜尋程式碼的增刪，而非僅搜尋 Commit Message。
4.  **Trace the Function**: 使用 `git log -L` 專注於特定函數的歷史演變。
5.  **Handle the Noise**: 設定 `ignore-revs` 來排除大規模格式化對歷史紀錄的干擾。

### 後續延伸 (Next Steps)
-   **Advanced Internals**: 下一章將探討 Git 的底層物件模型（Blob, Tree, Commit, Tag），理解這些指令背後是如何操作 SHA-1 雜湊的。
    **Advanced Internals**: The next chapter will explore Git's underlying object model (Blob, Tree, Commit, Tag) to understand how these commands manipulate SHA-1 hashes under the hood.
-   **Git Hooks**: 學習如何利用 Pre-commit hooks 防止壞程式碼進入歷史，從源頭減少使用 `bisect` 的需求。
    **Git Hooks**: Learn how to use Pre-commit hooks to prevent bad code from entering history, reducing the need for `bisect` in the first place.