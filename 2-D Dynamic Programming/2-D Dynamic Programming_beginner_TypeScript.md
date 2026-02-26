# 2-D Dynamic Programming: Foundations (Beginner)
# 二維動態規劃：基礎篇

## 1. Learning Goals（學習目標）

1.  **Transition from 1-D to 2-D Thinking**: Understand how to define a state with two variables `dp[i][j]` representing a subproblem solution.
    **從一維過渡到二維思維**：理解如何定義包含兩個變數的狀態 `dp[i][j]` 來表示子問題的解。
2.  **Master the Grid Pattern**: Solve pathfinding problems on matrices (e.g., minimizing costs or counting paths).
    **掌握網格模式**：解決矩陣上的路徑尋找問題（例如：最小化成本或計算路徑數）。
3.  **Understand Space Optimization**: Learn how to reduce space complexity from $O(M \times N)$ to $O(N)$ using a rolling array.
    **理解空間優化**：學習如何使用滾動陣列將空間複雜度從 $O(M \times N)$ 降低到 $O(N)$。
4.  **Standardize Initialization**: Correctly handle base cases and boundary conditions (padding vs. boundary checks).
    **標準化初始化**：正確處理基本情況與邊界條件（填充法 vs. 邊界檢查）。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
2-D DP is a technique used when the state of a problem depends on two independent variables, typically represented as a table or grid.
二維動態規劃是一種當問題狀態取決於兩個獨立變數時使用的技術，通常以表格或網格表示。

### Intuition（直覺）
Imagine filling out an Excel spreadsheet cell by cell.
想像逐格填寫 Excel 電子表格。
The value of the current cell depends on the values of its neighbors (usually top and left).
當前儲存格的值取決於其鄰居（通常是上方和左方）的值。

### Complexity（複雜度）
-   **Time**: $O(M \times N)$, where M and N are the dimensions of the inputs.
    **時間**：$O(M \times N)$，其中 M 和 N 是輸入的維度。
-   **Space**: $O(M \times N)$ for the full table, optimizable to $O(N)$ (where N is the column width).
    **空間**：完整表格為 $O(M \times N)$，可優化至 $O(N)$（其中 N 為列寬）。

### When to Use / Not to Use（適用與不適用場景）
-   **Use when**: Problems involve grids, comparing two strings/sequences, or "knapsack" style constraints.
    **適用於**：涉及網格、比較兩個字串/序列，或「背包」類型約束的問題。
-   **Don't use when**: The graph has cycles (unless restricted), or the input size is too large for quadratic complexity (e.g., $N=10^5$).
    **不適用於**：圖形具有環（除非有限制），或輸入規模太大以至於無法承受二次方複雜度（例如 $N=10^5$）。

---

## 3. Typical Patterns（典型題型 / 模式）

For the beginner level, we focus on two primary patterns:
對於初學者階段，我們專注於兩種主要模式：

1.  **Grid Traveler (Robot on a Matrix)**
    **網格行者（矩陣上的機器人）**
    -   **Scenario**: Moving from top-left to bottom-right.
    -   **情境**：從左上角移動到右下角。
    -   **Transition**: `dp[i][j] = f(dp[i-1][j], dp[i][j-1])`.
    -   **轉移方程**：`dp[i][j] = f(dp[i-1][j], dp[i][j-1])`。

2.  **Two-Sequence Alignment (Basic)**
    **雙序列對齊（基礎）**
    -   **Scenario**: Finding commonalities between String A and String B (e.g., Longest Common Subsequence).
    -   **情境**：尋找字串 A 與字串 B 之間的共通點（例如：最長公共子序列）。
    -   **Transition**: `dp[i][j]` depends on whether `A[i] == B[j]`.
    -   **轉移方程**：`dp[i][j]` 取決於 `A[i] == B[j]`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Minimum Path Sum（最小路徑和）

**Problem Statement**:
Given an `m x n` grid filled with non-negative numbers, find a path from top-left to bottom-right which minimizes the sum of all numbers along its path. You can only move either down or right.
給定一個填滿非負整數的 `m x n` 網格，找出從左上角到右下角的路徑，使其路徑上所有數字的總和最小。你只能向下或向右移動。

### Approach 1: Brute Force (Recursion)
**思路 1：暴力解（遞迴）**

-   At every cell, we branch into two paths: Down and Right.
    在每個格子，我們分支出兩條路徑：向下和向右。
-   **Complexity**: $O(2^{M+N})$. This is exponential and will TLE (Time Limit Exceeded).
    **複雜度**：$O(2^{M+N})$。這是指數級的，會導致超時（TLE）。

### Approach 2: 2-D DP (Tabulation)
**思路 2：二維 DP（列表法）**

-   **State**: `dp[i][j]` represents the minimum sum to reach cell `(i, j)` from `(0, 0)`.
    **狀態**：`dp[i][j]` 代表從 `(0, 0)` 到達格子 `(i, j)` 的最小總和。
-   **Transition**: To reach `(i, j)`, we must come from either `(i-1, j)` (top) or `(i, j-1)` (left). We pick the smaller one.
    **轉移**：要到達 `(i, j)`，我們必須來自 `(i-1, j)`（上方）或 `(i, j-1)`（左方）。我們選擇較小的一個。
    $$dp[i][j] = grid[i][j] + \min(dp[i-1][j], dp[i][j-1])$$

### TypeScript Solution (With Space Optimization)
**TypeScript 參考解（含空間優化）**

We will skip the full $O(M \times N)$ matrix and jump straight to the "Senior" implementation using $O(N)$ space (Rolling Array).
我們將跳過完整的 $O(M \times N)$ 矩陣，直接進入使用 $O(N)$ 空間（滾動陣列）的「資深」實作。

```typescript
/**
 * Calculates the minimum path sum from top-left to bottom-right.
 * 計算從左上角到右下角的最小路徑和。
 *
 * Time Complexity: O(M * N) - We visit every cell once.
 * Space Complexity: O(N) - We only store the previous row.
 */
function minPathSum(grid: number[][]): number {
    const m = grid.length;
    const n = grid[0].length;

    // Edge case: empty grid
    // 邊界情況：空網格
    if (m === 0 || n === 0) return 0;

    // Use a 1D array to store the minimum path sums for the current row.
    // Initialize with Infinity to handle boundary comparisons easily.
    // 使用一維陣列儲存當前列的最小路徑和。
    // 初始化為 Infinity 以便輕鬆處理邊界比較。
    const dp: number[] = new Array(n).fill(Infinity);

    // Base case: The starting point simply costs the value of the grid itself.
    // Note: We set dp[0] to 0 before the loop logic effectively starts for the first cell,
    // or handle i=0, j=0 specifically. Let's handle it inside.
    // 基本情況：起點的成本僅為網格本身的值。
    
    // Initialize the first cell logic (conceptually)
    // 初始化第一個格子的邏輯（概念上）
    dp[0] = 0; 

    for (let i = 0; i < m; i++) {
        for (let j = 0; j < n; j++) {
            if (i === 0 && j === 0) {
                // Start point
                // 起點
                dp[j] = grid[i][j];
            } else if (i === 0) {
                // First row: can only come from the left
                // 第一列：只能來自左方
                dp[j] = dp[j - 1] + grid[i][j];
            } else if (j === 0) {
                // First column: can only come from above
                // 第一行：只能來自上方
                dp[j] = dp[j] + grid[i][j]; // dp[j] here represents the value from the row above
            } else {
                // General case: min(from above, from left)
                // 一般情況：min(來自上方, 來自左方)
                // dp[j] is 'above' (not yet updated), dp[j-1] is 'left' (already updated)
                dp[j] = Math.min(dp[j], dp[j - 1]) + grid[i][j];
            }
        }
    }

    // The last element contains the min path sum to the bottom-right corner.
    // 最後一個元素包含到達右下角的最小路徑和。
    return dp[n - 1];
}
```

### Why the "Wrong" Way is Wrong
**錯誤示範 & 為何錯**

*   **Greedy Approach**: "At each step, just pick the smaller neighbor."
    **貪婪法**：「每一步只選擇較小的鄰居。」
*   **Failure**: This fails because a locally optimal choice might lead to a very large number later.
    **失敗原因**：這會失敗，因為局部最優的選擇可能會導致後續遇到非常大的數字。
    *   Example:
        ```text
        [1, 100, 1]
        [1,   1, 1]
        ```
        Greedy might go Right (1->100) vs Down (1->1). Wait, bad example.
        Better example:
        ```text
        [1, 5, 5]
        [4, 1, 1]
        ```
        Path Right-Right-Down: $1+5+5+1 = 12$.
        Path Down-Right-Right: $1+4+1+1 = 7$.
        Greedy at (0,0) sees Right(5) and Down(4). It picks Down. This works here.
        
        Let's try:
        ```text
        [1, 10, 10]
        [5,  1,  1]
        ```
        Greedy at (0,0): Right is 10, Down is 5. Picks Down. Path: 1->5->1->1 = 8.
        Wait, if we go Right: 1->10->10... huge.
        
        Real Counter Example:
        ```text
        [1, 1, 100]
        [100, 1, 1]
        [100, 1, 1]
        ```
        Greedy is unreliable for global minimization. DP explores all valid combinations implicitly.
        貪婪法對於全域最小化是不可靠的。DP 隱式地探索了所有有效的組合。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall |
| :--- | :--- |
| **Padding (Sentinel)** | **Concept**: Adding an extra row/col of 0s or Infinity to avoid `if (i-1 < 0)` checks.<br>**Pitfall**: Forgetting to adjust indices when mapping back to the original grid.<br>**概念**：增加額外的一行/列（0 或無限大）以避免邊界檢查。<br>**陷阱**：映射回原始網格時忘記調整索引。 |
| **Initialization** | **Concept**: `dp` array must be initialized correctly.<br>**Pitfall**: Using `0` for minimization problems (should be `Infinity`) or `0` for product problems (might need `1`).<br>**概念**：`dp` 陣列必須正確初始化。<br>**陷阱**：在最小化問題中使用 `0`（應為 `Infinity`），或在乘積問題中使用 `0`（可能需要 `1`）。 |
| **Traversal Order** | **Concept**: Usually top-left to bottom-right.<br>**Pitfall**: Some problems require reverse traversal (e.g., "Minimum health needed to reach end").<br>**概念**：通常是從左上到右下。<br>**陷阱**：某些問題需要反向遍歷（例如：「到達終點所需的最小生命值」）。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Define the State**: "I will define `dp[r][c]` as the minimum cost to reach row `r`, column `c`."
    **定義狀態**：「我將定義 `dp[r][c]` 為到達第 `r` 列、第 `c` 行的最小成本。」
2.  **Establish Recurrence**: "Since I can only move down or right, the value at `[r][c]` depends on `[r-1][c]` and `[r][c-1]`."
    **建立遞迴關係**：「因為我只能向下或向右移動，`[r][c]` 的值取決於 `[r-1][c]` 和 `[r][c-1]`。」
3.  **Discuss Base Cases**: "The first row and first column are special cases because they have only one valid predecessor."
    **討論基本情況**：「第一列和第一行是特殊情況，因為它們只有一個有效的前驅。」
4.  **Propose Optimization**: "Initially, I'll use a 2D array, but we can optimize this to O(N) space since we only need the previous row."
    **提出優化**：「最初我會使用二維陣列，但我們可以將其優化為 O(N) 空間，因為我們只需要前一列的數據。」

### Whiteboard Strategy（白板策略）
-   Draw a small 3x3 grid.
    畫一個小的 3x3 網格。
-   Write the indices `i` and `j`.
    寫下索引 `i` 和 `j`。
-   Manually fill the first few cells to verify your logic before coding.
    在寫程式碼之前，手動填寫前幾個格子以驗證邏輯。

---

## 7. Practice Problems（練習題）

### 1. Easy: Unique Paths
**題目**：A robot is at `(0,0)`, wants to go to `(m-1, n-1)`. Can only move Down or Right. How many unique paths?
**機器人位於 `(0,0)`，想去 `(m-1, n-1)`。只能向下或向右。有多少條唯一路徑？**
-   **Hint**: `dp[i][j] = dp[i-1][j] + dp[i][j-1]`. Base case: first row/col are all 1.
-   **提示**：`dp[i][j] = dp[i-1][j] + dp[i][j-1]`。基本情況：第一列/行全為 1。

### 2. Medium: Longest Common Subsequence (LCS)
**題目**：Given strings `text1` and `text2`, return the length of their longest common subsequence.
**給定字串 `text1` 和 `text2`，返回它們最長公共子序列的長度。**
-   **Hint**: If `c1 == c2`, `dp[i][j] = 1 + dp[i-1][j-1]`. Else `max(dp[i-1][j], dp[i][j-1])`.
-   **提示**：如果 `c1 == c2`，`dp[i][j] = 1 + dp[i-1][j-1]`。否則 `max(dp[i-1][j], dp[i][j-1])`。

### 3. Hard (Conceptually): Maximal Square
**題目**：Given an `m x n` binary matrix, find the largest square containing only 1s and return its area.
**給定一個 `m x n` 的二進制矩陣，找出只包含 1 的最大正方形並返回其面積。**
-   **Hint**: `dp[i][j]` is the side length of the square ending at `(i,j)`. It depends on Top, Left, and Top-Left neighbors.
-   **提示**：`dp[i][j]` 是以 `(i,j)` 為結束點的正方形邊長。它取決於上方、左方和左上方的鄰居。

---

## 8. Quick Checklists（快速檢核表）

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

-   [ ] **Dimensions**: Did I handle `m=0` or `n=0`?
    **維度**：我是否處理了 `m=0` 或 `n=0`？
-   [ ] **Initialization**: Is the DP table initialized with a value that won't interfere (e.g., 0 for sum, Infinity for min)?
    **初始化**：DP 表是否初始化為不會干擾的值（例如：求和為 0，求最小值為 Infinity）？
-   [ ] **Indices**: Am I accessing `i-1` or `j-1` without checking if `i>0` or `j>0`?
    **索引**：我是否在未檢查 `i>0` 或 `j>0` 的情況下存取 `i-1` 或 `j-1`？
-   [ ] **Return Value**: Am I returning `dp[m-1][n-1]` or something else?
    **返回值**：我是返回 `dp[m-1][n-1]` 還是其他值？

---

## 9. Memory Anchors（記憶錨點）

### The "Spreadsheet" Analogy（電子表格類比）
Visualize 2-D DP as writing formulas in Excel.
將二維 DP 想像成在 Excel 中編寫公式。
-   Cell B2 `= A2 + B1`.
-   You cannot calculate B2 until A2 and B1 are calculated.
-   在計算出 A2 和 B1 之前，你無法計算 B2。

### The "Rolling Pin"（桿麵棍）
For space optimization, imagine a rolling pin moving down the dough.
對於空間優化，想像一根桿麵棍在麵團上向下移動。
-   You only care about the part of the dough the pin is currently touching (current row) and the part it just left (previous row).
-   你只關心桿麵棍當前接觸的麵團部分（當前列）和它剛離開的部分（前一列）。