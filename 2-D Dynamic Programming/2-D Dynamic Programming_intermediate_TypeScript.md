# 2-D Dynamic Programming: Intermediate Guide
# 二維動態規劃：中階指南

## 1. Learning Objectives（學習目標）

1.  **Master State Definition**: Learn to define $dp[i][j]$ precisely for grid-based and dual-sequence problems.
    **掌握狀態定義**：學會精確定義網格（Grid）與雙序列（Dual-sequence）問題中的 $dp[i][j]$。
2.  **Transition Derivation**: Systematically derive recurrence relations from "last step" logic.
    **推導轉移方程**：從「最後一步」的邏輯系統化地推導出遞迴關係。
3.  **Space Optimization**: Optimize space complexity from $O(M \times N)$ to $O(N)$ (Rolling Array).
    **空間優化**：將空間複雜度從 $O(M \times N)$ 優化至 $O(N)$（滾動陣列）。
4.  **Debug & Verification**: Develop intuition for boundary conditions and initialization pitfalls.
    **除錯與驗證**：建立對邊界條件與初始化陷阱的直覺。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
2-D DP involves solving problems where the state depends on two independent variables, typically represented as a table/matrix.
二維動態規劃涉及解決狀態取決於兩個獨立變數的問題，通常以表格或矩陣表示。

### Intuition（直覺）
Think of it as filling a spreadsheet cell by cell, where the value of the current cell depends on its immediate neighbors (usually top, left, or top-left).
將其想像為逐格填寫試算表，當前儲存格的值取決於其鄰近的儲存格（通常是上方、左方或左上方）。

### Complexity（複雜度）
-   **Time**: Typically $O(M \times N)$, where $M$ and $N$ are the dimensions of inputs.
    **時間**：通常為 $O(M \times N)$，其中 $M$ 和 $N$ 是輸入的維度。
-   **Space**: Naively $O(M \times N)$, optimizable to $O(\min(M, N))$.
    **空間**：直觀上為 $O(M \times N)$，可優化至 $O(\min(M, N))$。

### When to Use（適用場景）
-   **Grid Problems**: Finding paths, min costs, or areas in a matrix.
    **網格問題**：在矩陣中尋找路徑、最小成本或區域。
-   **Dual Sequence**: Comparing two strings/arrays (LCS, Edit Distance).
    **雙序列問題**：比較兩個字串或陣列（如最長公共子序列、編輯距離）。

### When NOT to Use（不適用場景）
-   If the problem requires looking back at *arbitrary* previous states (might need Graph/BFS).
    如果問題需要回顧*任意*先前的狀態（可能需要圖論/BFS）。
-   If the input size is huge (e.g., $N=10^5$), $O(N^2)$ will TLE (Time Limit Exceeded).
    如果輸入規模巨大（例如 $N=10^5$），$O(N^2)$ 會導致超時。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Grid Traveler (Robot on a Matrix)
### 模式 A：網格行者（矩陣上的機器人）
-   **State**: $dp[i][j]$ = distinct paths/min cost to reach cell $(i, j)$.
    **狀態**：$dp[i][j]$ = 到達單元格 $(i, j)$ 的相異路徑數或最小成本。
-   **Transition**: $dp[i][j] = f(dp[i-1][j], dp[i][j-1])$.
    **轉移**：$dp[i][j] = f(dp[i-1][j], dp[i][j-1])$。

### Pattern B: Dual Sequence (String Matching)
### 模式 B：雙序列（字串匹配）
-   **State**: $dp[i][j]$ = result considering `s1[0...i]` and `s2[0...j]`.
    **狀態**：$dp[i][j]$ = 考慮 `s1[0...i]` 與 `s2[0...j]` 的結果。
-   **Transition**: Depends on whether `s1[i] == s2[j]`.
    **轉移**：取決於 `s1[i]` 是否等於 `s2[j]`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Longest Common Subsequence (LCS)
### 問題：最長公共子序列

**Problem Statement:**
Given two strings `text1` and `text2`, return the length of their longest common subsequence.
給定兩個字串 `text1` 和 `text2`，返回它們最長公共子序列的長度。

**Example:**
Input: `text1 = "abcde"`, `text2 = "ace"`
Output: `3` ("ace")

### 1. Thought Process: Brute Force to Optimization
### 1. 思路：從暴力解到優化

-   **Brute Force (Recursion)**: Try all subsequences of `text1` and check if they exist in `text2`. Complexity is exponential $O(2^N)$.
    **暴力解（遞迴）**：嘗試 `text1` 的所有子序列並檢查它們是否存在於 `text2` 中。複雜度是指數級 $O(2^N)$。

-   **DP State Definition**: Let $dp[i][j]$ be the LCS length of `text1[0...i-1]` and `text2[0...j-1]`.
    **DP 狀態定義**：設 $dp[i][j]$ 為 `text1[0...i-1]` 和 `text2[0...j-1]` 的 LCS 長度。
    *(Note: We use 1-based indexing for the DP table to handle empty strings easily.)*
    *（註：我們對 DP 表使用 1-based 索引，以便輕鬆處理空字串。）*

-   **Transition Equation**:
    **轉移方程**：
    1.  If `text1[i] == text2[j]`: We found a match! Add 1 to the result without these characters ($dp[i-1][j-1]$).
        如果 `text1[i] == text2[j]`：找到匹配！在不包含這些字元的結果 ($dp[i-1][j-1]$) 上加 1。
    2.  If `text1[i] != text2[j]`: Skip one character from either string and take the max.
        如果 `text1[i] != text2[j]`：從任一字串跳過一個字元並取最大值。

### 2. TypeScript Solution (Standard 2-D Table)
### 2. TypeScript 參考解（標準二維表格）

```typescript
function longestCommonSubsequence(text1: string, text2: string): number {
    const m = text1.length;
    const n = text2.length;

    // Create a (m+1) x (n+1) grid initialized with 0
    // 建立一個 (m+1) x (n+1) 的網格，初始化為 0
    const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            // Check if characters match. Note: string index is 0-based, so use i-1
            // 檢查字元是否匹配。注意：字串索引是從 0 開始，所以使用 i-1
            if (text1[i - 1] === text2[j - 1]) {
                // Match found: extend the diagonal result
                // 發現匹配：延伸對角線的結果
                dp[i][j] = 1 + dp[i - 1][j - 1];
            } else {
                // No match: take the best result by ignoring current char of text1 or text2
                // 未匹配：取忽略 text1 或 text2 當前字元後的最佳結果
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
    }

    // The bottom-right cell contains the answer
    // 右下角的單元格包含答案
    return dp[m][n];
}
```

### 3. Space Optimization (Rolling Array)
### 3. 空間優化（滾動陣列）

Since $dp[i][j]$ only depends on the current row ($i$) and the previous row ($i-1$), we only need two rows (or even one).
由於 $dp[i][j]$ 僅取決於當前行 ($i$) 和上一行 ($i-1$)，我們只需要兩行（甚至一行）。

```typescript
function longestCommonSubsequenceOptimized(text1: string, text2: string): number {
    const m = text1.length;
    const n = text2.length;
    
    // Previous row state
    // 上一行的狀態
    let prev: number[] = Array(n + 1).fill(0);
    
    // Current row state
    // 當前行的狀態
    let curr: number[] = Array(n + 1).fill(0);

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (text1[i - 1] === text2[j - 1]) {
                // Diagonal value comes from 'prev' array at index j-1
                // 對角線的值來自 'prev' 陣列的 j-1 索引
                curr[j] = 1 + prev[j - 1];
            } else {
                // Top value is prev[j], Left value is curr[j-1]
                // 上方值為 prev[j]，左方值為 curr[j-1]
                curr[j] = Math.max(prev[j], curr[j - 1]);
            }
        }
        // Move current row to previous for the next iteration
        // 將當前行移至上一行，供下一次迭代使用
        // Use spread syntax or slice to copy to avoid reference issues
        // 使用展開語法或 slice 進行複製以避免參照問題
        prev = [...curr]; 
    }

    return prev[n];
}
```

### Time & Space Complexity（時間與空間複雜度）
-   **Time**: $O(M \times N)$ — We iterate through every cell once.
    **時間**：$O(M \times N)$ — 我們遍歷每個單元格一次。
-   **Space**: $O(N)$ (Optimized) vs $O(M \times N)$ (Standard).
    **空間**：$O(N)$（優化後）vs $O(M \times N)$（標準）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake | Correction |
| :--- | :--- | :--- |
| **Indexing** | Using `dp[i][j]` with `s[i]` directly inside loops starting at 1. <br> 在從 1 開始的迴圈中直接使用 `dp[i][j]` 對應 `s[i]`。 | Use `s[i-1]` when loop is `1` to `N`. DP table is padded. <br> 當迴圈為 `1` 到 `N` 時使用 `s[i-1]`。DP 表有填充邊界。 |
| **Initialization** | Initializing boundaries with 0 when calculating "Min Cost". <br> 計算「最小成本」時將邊界初始化為 0。 | Initialize with `Infinity` for Min problems, `0` for Max/Sum. <br> 最小化問題應初始化為 `Infinity`，最大化/求和則為 `0`。 |
| **Base Cases** | Forgetting the first row/column initialization in Grid problems. <br> 在網格問題中忘記第一行/列的初始化。 | Handle row 0 and col 0 separately or use padding. <br> 單獨處理第 0 行和第 0 列，或使用填充。 |
| **Space Opt.** | Overwriting `prev[j]` before using it for `prev[j-1]` logic. <br> 在使用 `prev[j-1]` 邏輯前覆蓋了 `prev[j]`。 | Use a temporary variable (like `diag`) or distinct `curr` array. <br> 使用臨時變數（如 `diag`）或獨立的 `curr` 陣列。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Verbal Framework（口條框架）
-   **Identify**: "This looks like a decision problem on two sequences/grid, suggesting Dynamic Programming."
    **識別**：「這看起來是雙序列/網格上的決策問題，暗示可以使用動態規劃。」
-   **Define State**: "I will define `dp[i][j]` as the [metric] for the first `i` items and first `j` items."
    **定義狀態**：「我將定義 `dp[i][j]` 為前 `i` 個項目與前 `j` 個項目的 [指標]。」
-   **Base Case**: "When either string is empty, the result is 0."
    **基本情況**：「當任一字串為空時，結果為 0。」

### 2. Whiteboard Strategy（白板策略）
-   Draw a small 2D matrix (e.g., 3x3) to trace the values manually before coding.
    在寫程式碼之前，畫一個小的二維矩陣（例如 3x3）手動追蹤數值。
-   Write the Transition Equation ($dp[i][j] = \dots$) clearly on the board/screen.
    在白板/螢幕上清楚寫下轉移方程（$dp[i][j] = \dots$）。

### 3. Follow-up Handling（常見追問）
-   **Q**: "Can you improve space complexity?"
    **問**：「你能改善空間複雜度嗎？」
-   **A**: "Yes, we can use a Rolling Array to reduce space to $O(N)$ since we only look at the previous row."
    **答**：「可以，我們可以使用滾動陣列將空間減少到 $O(N)$，因為我們只查看上一行。」
-   **Q**: "What if we need to print the actual path/string?"
    **問**：「如果我們需要印出實際的路徑/字串呢？」
-   **A**: "We cannot use space optimization easily. We need the full $O(MN)$ table to backtrack from $dp[M][N]$ to start."
    **答**：「我們無法輕易使用空間優化。我們需要完整的 $O(MN)$ 表格從 $dp[M][N]$ 回溯到起點。」

---

## 7. Practice Problems（練習題）

### 1. Easy: Unique Paths (Grid)
**Problem**: Robot moves from top-left to bottom-right, only moves down or right. Count paths.
**問題**：機器人從左上移動到右下，只能向下或向右。計算路徑數。
-   **Hint**: $dp[i][j] = dp[i-1][j] + dp[i][j-1]$.
-   **提示**：$dp[i][j] = dp[i-1][j] + dp[i][j-1]$。

### 2. Medium: Edit Distance (Dual Sequence)
**Problem**: Min operations (insert, delete, replace) to convert word1 to word2.
**問題**：將 word1 轉換為 word2 的最少操作數（插入、刪除、替換）。
-   **Hint**: If chars match, $dp[i][j] = dp[i-1][j-1]$. If not, $1 + \min(\text{insert}, \text{delete}, \text{replace})$.
-   **提示**：若字元匹配，繼承左上角；若不匹配，$1 + \min(\text{插入}, \text{刪除}, \text{替換})$。

### 3. Hard: Maximal Square (Grid + Logic)
**Problem**: Find the largest square containing only '1's in a binary matrix and return its area.
**問題**：在二進位矩陣中找到只包含 '1' 的最大正方形並返回其面積。
-   **Hint**: $dp[i][j]$ represents the side length of the square ending at $(i, j)$.
    $dp[i][j] = \min(\text{top}, \text{left}, \text{top-left}) + 1$.
-   **提示**：$dp[i][j]$ 代表以 $(i, j)$ 為終點的正方形邊長。
    $dp[i][j] = \min(\text{上}, \text{左}, \text{左上}) + 1$。

---

## 8. Quick Checklists（快速檢核表）

-   [ ] **Padding**: Did I add `+1` to DP dimensions to handle empty cases (index -1 issues)?
    **填充**：我是否在 DP 維度上加了 `+1` 以處理空情況（索引 -1 問題）？
-   [ ] **Initialization**: Is the 0th row/col initialized correctly (0 for sums, 1 for products/existence)?
    **初始化**：第 0 行/列是否正確初始化（求和為 0，乘積/存在性為 1）？
-   [ ] **Indices**: Am I accessing `string[i-1]` inside the loop `i=1..N`?
    **索引**：我是否在 `i=1..N` 的迴圈中存取 `string[i-1]`？
-   [ ] **Return**: Am I returning `dp[m][n]` or `dp[m-1][n-1]`?
    **返回**：我是返回 `dp[m][n]` 還是 `dp[m-1][n-1]`？

---

## 9. Memory Anchors（記憶錨點）

### The "Look Back" Triangle
### 「回頭看」三角形
Visualize the cell $(i, j)$ looking at its three predecessors:
想像單元格 $(i, j)$ 看著它的三個前身：
```text
(i-1, j-1)  (i-1, j)
      \       |
       \      |
(i, j-1) -- (i, j)
```
-   **LCS/Edit Distance**: Usually cares about the diagonal (match) and sides (mismatch).
    **LCS/編輯距離**：通常關心對角線（匹配）和兩側（不匹配）。
-   **Grid Paths**: Usually cares only about Top and Left.
    **網格路徑**：通常只關心上方和左方。

### The "Space Compression" Scroll
### 「空間壓縮」卷軸
Imagine rolling up a carpet. You only need to see the edge of the carpet (the previous row) to weave the next part. The rest of the carpet is rolled away (discarded).
想像捲起地毯。你只需要看到地毯的邊緣（上一行）來編織下一部分。地毯的其餘部分都被捲走了（丟棄）。