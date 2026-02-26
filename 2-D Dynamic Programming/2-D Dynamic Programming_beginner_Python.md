# 2-D Dynamic Programming: Foundations (二維動態規劃：基礎篇)

## 1. Learning Objectives (學習目標)

1.  **Transition from 1-D to 2-D Thinking:** Understand how to define a state that depends on two variables (e.g., coordinates in a grid or indices in two strings).
    **從一維過渡到二維思維：** 理解如何定義依賴於兩個變數的狀態（例如網格中的坐標或兩個字串中的索引）。

2.  **Master the Grid Pattern:** Learn the standard traversal techniques for matrix-based problems.
    **掌握網格模式：** 學習基於矩陣問題的標準遍歷技巧。

3.  **Space Optimization:** Understand how to reduce space complexity from $O(M \times N)$ to $O(N)$ using a rolling array.
    **空間優化：** 理解如何使用滾動陣列將空間複雜度從 $O(M \times N)$ 降低到 $O(N)$。

4.  **Base Case Identification:** Correctly initialize the DP table boundaries (row 0 and column 0).
    **基本情況識別：** 正確初始化 DP 表的邊界（第 0 列和第 0 行）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
2-D DP involves solving problems where the optimal solution depends on subproblems defined by two parameters, usually represented as a table $DP[i][j]$.
二維 DP 涉及解決最佳解依賴於由兩個參數定義的子問題的情況，通常表示為一個表格 $DP[i][j]$。

### Intuition (直覺)
Think of it as filling out a spreadsheet.
把它想像成填寫電子試算表。
To calculate the value of a specific cell, you need values from neighboring cells (usually top, left, or top-left diagonal) that have already been computed.
要計算特定儲存格的值，你需要來自鄰近儲存格（通常是上方、左方或左上對角線）且已經計算好的值。

### Complexity (複雜度)
-   **Time:** $O(M \times N)$, where $M$ and $N$ are the dimensions of the inputs.
    **時間：** $O(M \times N)$，其中 $M$ 和 $N$ 是輸入的維度。
-   **Space:** $O(M \times N)$ for the full table, optimizable to $O(\min(M, N))$.
    **空間：** 完整表格為 $O(M \times N)$，可優化至 $O(\min(M, N))$。

### When to Use (適用場景)
-   **Grid Problems:** Finding paths, counting paths, or min/max sums in a matrix.
    **網格問題：** 在矩陣中尋找路徑、計算路徑數量或最小/最大總和。
-   **String/Sequence Alignment:** Longest Common Subsequence, Edit Distance (comparing two strings).
    **字串/序列對齊：** 最長共同子序列、編輯距離（比較兩個字串）。

### When NOT to Use (不適用場景)
-   If the problem requires looking at the *current* state's future to decide (Greedy might be better).
    如果問題需要查看 *當前* 狀態的未來來做決定（貪婪演算法可能更好）。
-   If the input size is huge (e.g., $N=10^5$), $O(N^2)$ will time out.
    如果輸入規模巨大（例如 $N=10^5$），$O(N^2)$ 會超時。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Grid Navigation (網格導航)
-   **State:** $DP[i][j]$ = value to reach cell $(i, j)$.
    **狀態：** $DP[i][j]$ = 到達儲存格 $(i, j)$ 的值。
-   **Transition:** $DP[i][j] = f(DP[i-1][j], DP[i][j-1])$.
    **轉移：** $DP[i][j] = f(DP[i-1][j], DP[i][j-1])$。
-   **Direction:** Top-left to Bottom-right.
    **方向：** 左上到右下。

### Pattern B: Two Sequence Comparison (雙序列比較)
-   **State:** $DP[i][j]$ = result comparing `str1[0...i]` and `str2[0...j]`.
    **狀態：** $DP[i][j]$ = 比較 `str1[0...i]` 和 `str2[0...j]` 的結果。
-   **Transition:** Often involves checking if `str1[i] == str2[j]`.
    **轉移：** 通常涉及檢查 `str1[i] == str2[j]`。

---

## 4. Example Walkthrough (範例講解)

### Problem: Unique Paths (LeetCode 62)
**Problem Statement:**
A robot is located at the top-left corner of an `m x n` grid. The robot can only move either down or right at any point in time. The robot is trying to reach the bottom-right corner. How many possible unique paths are there?
**問題重述：**
一個機器人位於 `m x n` 網格的左上角。機器人任何時候只能向下或向右移動。機器人試圖到達右下角。請問有多少條可能的唯一路徑？

### Approach 1: Brute Force (DFS / Recursion)
**Idea:** Recursively try moving Right and Down.
**思路：** 遞迴地嘗試向右和向下移動。

```python
def uniquePaths_recursive(m: int, n: int) -> int:
    # Base case: reached the start (or end, depending on direction)
    # 基本情況：到達起點（或終點，視方向而定）
    if m == 1 or n == 1:
        return 1
    # Recursive step: sum of paths from top and left
    # 遞迴步驟：來自上方和左方的路徑之和
    return uniquePaths_recursive(m - 1, n) + uniquePaths_recursive(m, n - 1)
```
*   **Critique:** Time Complexity is exponential $O(2^{m+n})$. Terrible for large inputs.
    **評論：** 時間複雜度是指數級 $O(2^{m+n})$。對於大輸入非常糟糕。

### Approach 2: 2-D DP (Tabulation)
**Idea:** Store the number of paths to reach each cell $(i, j)$.
**思路：** 儲存到達每個儲存格 $(i, j)$ 的路徑數量。

```python
def uniquePaths_dp(m: int, n: int) -> int:
    # Initialize a 2D table with 1s (base case for row 0 and col 0 is always 1 path)
    # 初始化一個全為 1 的二維表格（第 0 行和第 0 列的基本情況永遠是 1 條路徑）
    dp = [[1] * n for _ in range(m)]

    # Iterate through the grid starting from (1, 1)
    # 從 (1, 1) 開始遍歷網格
    for i in range(1, m):
        for j in range(1, n):
            # The number of paths to (i, j) is sum of paths from top and left
            # 到達 (i, j) 的路徑數等於來自上方和左方的路徑數之和
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
            
    return dp[m-1][n-1]
```
*   **Time:** $O(m \times n)$.
*   **Space:** $O(m \times n)$.

### Approach 3: Space Optimization (Rolling Array) - **Best Practice**
**Idea:** We only need the previous row to calculate the current row. We don't need the entire matrix.
**思路：** 我們只需要上一列來計算當前列。我們不需要整個矩陣。

```python
def uniquePaths_optimal(m: int, n: int) -> int:
    # Initialize a 1D array representing the "previous row"
    # 初始化一個代表「上一列」的一維陣列
    # Initially, for the first row, all paths are 1
    # 最初，對於第一列，所有路徑數都是 1
    row = [1] * n

    # Iterate through rows (skipping the first one as it's initialized)
    # 遍歷每一列（跳過第一列，因為已經初始化）
    for i in range(1, m):
        # Iterate through columns
        # 遍歷每一行
        for j in range(1, n):
            # Current cell = value from top (current row[j]) + value from left (new row[j-1])
            # 當前儲存格 = 來自上方的值 (當前 row[j]) + 來自左方的值 (新的 row[j-1])
            # row[j] currently holds the value from the previous iteration (top)
            # row[j] 目前保存著上一次迭代的值（上方）
            row[j] += row[j-1]
            
    return row[n-1]
```
*   **Time:** $O(m \times n)$.
*   **Space:** $O(n)$ (Can be $O(\min(m, n))$ by swapping loops).

---

## 5. Common Pitfalls (常見陷阱)

| Concept | Pitfall (陷阱) | Correct Approach (正確做法) |
| :--- | :--- | :--- |
| **Initialization** | Forgetting to handle the 0-th row/col separately. <br> 忘記單獨處理第 0 列/行。 | Initialize boundaries first or use padding. <br> 先初始化邊界或使用填充。 |
| **Index Mapping** | Confusing `m` (rows) and `n` (cols) or `i` and `j`. <br> 混淆 `m`（列）和 `n`（行）或 `i` 和 `j`。 | Stick to `r` (row) and `c` (col) variable names if confused. <br> 如果容易混淆，堅持使用 `r` 和 `c` 變數名。 |
| **Space Opt** | Overwriting data in the 1-D array before using it. <br> 在使用一維陣列的數據前就將其覆蓋。 | Ensure the calculation order preserves the "old" value if needed. <br> 確保計算順序在需要時保留「舊」值。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define the State:** "I will define `dp[i][j]` as the [metric] to reach index `i` and `j`."
    **定義狀態：** 「我將定義 `dp[i][j]` 為到達索引 `i` 和 `j` 的 [指標]。」
2.  **Establish Recurrence:** "The value at `dp[i][j]` depends on..."
    **建立遞迴關係：** 「`dp[i][j]` 的值取決於……」
3.  **Discuss Base Cases:** "For the first row and column..."
    **討論基本情況：** 「對於第一列和第一行……」

### Whiteboard Strategy (白板策略)
-   Draw a small 3x3 grid.
    畫一個小的 3x3 網格。
-   Fill in the values manually for the first few cells to verify your logic before coding.
    在寫程式碼之前，手動填寫前幾個儲存格的值以驗證你的邏輯。

### Common Follow-up (常見追問)
-   **Q:** "Can you optimize the space?"
    **問：** 「你能優化空間嗎？」
-   **A:** Transition from 2D matrix to 1D array (Rolling Array).
    **答：** 從二維矩陣轉換到一維陣列（滾動陣列）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Minimum Path Sum (LeetCode 64)
**Hint:** Similar to Unique Paths, but instead of adding paths, you take `min(top, left) + current_val`.
**提示：** 類似於 Unique Paths，但不是相加路徑，而是取 `min(上方, 左方) + 當前值`。

### 2. Medium: Longest Common Subsequence (LeetCode 1143)
**Hint:** If `text1[i] == text2[j]`, `dp[i][j] = 1 + dp[i-1][j-1]`. Else, `max(dp[i-1][j], dp[i][j-1])`.
**提示：** 如果 `text1[i] == text2[j]`，`dp[i][j] = 1 + dp[i-1][j-1]`。否則，`max(dp[i-1][j], dp[i][j-1])`。

### 3. Hard (Conceptual): Maximal Square (LeetCode 221)
**Hint:** `dp[i][j]` represents the side length of the largest square ending at `(i, j)`. It depends on `min(top, left, top-left)`.
**提示：** `dp[i][j]` 代表以 `(i, j)` 為結尾的最大正方形的邊長。它取決於 `min(上方, 左方, 左上方)`。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **State Definition:** Does `dp[i][j]` clearly represent a subproblem solution?
    **狀態定義：** `dp[i][j]` 是否清楚地代表了一個子問題的解？
-   [ ] **Dimensions:** Did I allocate `m+1` or `n+1` size if using 1-based indexing?
    **維度：** 如果使用 1-based 索引，我是否分配了 `m+1` 或 `n+1` 的大小？
-   [ ] **Base Cases:** Are the edges (row 0, col 0) handled correctly to avoid `IndexError`?
    **基本情況：** 邊緣（第 0 列，第 0 行）是否正確處理以避免 `IndexError`？
-   [ ] **Result:** Is the answer at `dp[m-1][n-1]` or somewhere else (like `max(dp)` matrix)?
    **結果：** 答案是在 `dp[m-1][n-1]` 還是在其他地方（例如 `max(dp)` 矩陣）？

---

## 9. Memory Anchors (記憶錨點)

### The "Waterfall" Analogy (瀑布類比)
Imagine water flowing down a terraced field. The water in a lower pool comes from the pools directly above it.
想像水流下梯田。下方水池的水來自其正上方的水池。
*   **Grid DP:** Water flows from Top/Left -> Bottom/Right.
    **網格 DP：** 水從 上/左 -> 下/右 流動。

### The "Zipper" Analogy (拉鍊類比)
For String DP (LCS, Edit Distance), imagine zipping two jackets together.
對於字串 DP（LCS，編輯距離），想像將兩件夾克的拉鍊拉在一起。
*   If teeth match (`char1 == char2`), the zipper moves up diagonally (`i-1, j-1`).
    如果拉鍊齒匹配（`char1 == char2`），拉鍊沿對角線向上移動（`i-1, j-1`）。
*   If they don't match, you have to skip a tooth on one side (`i-1` or `j-1`).
    如果不匹配，你必須跳過某一邊的一個齒（`i-1` 或 `j-1`）。