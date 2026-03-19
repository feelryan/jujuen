Here is the complete interview preparation material for **2-D Dynamic Programming**, tailored for a Senior Software Engineer, adjusted to a **Beginner** depth (foundational concepts for 2-D DP), using **Java**.

這是一份針對 **二維動態規劃（2-D Dynamic Programming）** 的完整面試準備教材，專為資深軟體工程師設計，深度調整為 **初學者（Beginner）**（即 2-D DP 的奠基階段），並使用 **Java** 撰寫。

---

# 2-D Dynamic Programming: Foundations (二維動態規劃：基礎篇)

## 1. Learning Goals（學習目標）

*   **Master State Definition**: Learn how to define $dp[i][j]$ to represent the optimal solution for a subproblem.
    **掌握狀態定義**：學習如何定義 $dp[i][j]$ 來代表子問題的最佳解。
*   **Transition Equation Derivation**: Understand how to derive the value of a cell based on its neighbors (e.g., top and left).
    **推導轉移方程式**：理解如何根據鄰居（如上方和左方）的值來推導當前格子的值。
*   **Space Optimization**: Learn how to optimize space complexity from $O(M \times N)$ to $O(N)$ using a rolling array.
    **空間優化**：學習如何使用滾動陣列（Rolling Array）將空間複雜度從 $O(M \times N)$ 優化至 $O(N)$。
*   **Grid Traversal Intuition**: Build the mental model of filling a spreadsheet or traversing a grid.
    **網格遍歷直覺**：建立填寫試算表或遍歷網格的心智模型。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
2-D Dynamic Programming involves solving problems where the state depends on two variables, typically represented as a 2D array (matrix).
二維動態規劃涉及解決狀態取決於兩個變數的問題，通常以二維陣列（矩陣）表示。

### Intuition（直覺）
Think of it as filling out a spreadsheet cell by cell.
把它想像成逐格填寫試算表。
The value of the current cell usually depends on the values of the cells directly above it, to the left of it, or diagonally previous to it.
當前格子的值通常取決於它正上方、左方或對角線前方的格子數值。

### Complexity（複雜度）
*   **Time**: $O(M \times N)$, where $M$ and $N$ are the dimensions of the grid or the lengths of two sequences.
    **時間**：$O(M \times N)$，其中 $M$ 和 $N$ 是網格的維度或兩個序列的長度。
*   **Space**: Naively $O(M \times N)$, optimizable to $O(N)$ (linear space).
    **空間**：直觀上為 $O(M \times N)$，可優化至 $O(N)$（線性空間）。

### When to Use / Not Use（適用與不適用場景）
*   **Use when**: You need to find the number of paths on a grid, minimum cost to cross a grid, or basic string matching (e.g., Longest Common Subsequence).
    **適用時機**：需要尋找網格上的路徑數量、穿越網格的最小成本，或基礎字串匹配（如最長公共子序列）時。
*   **Do not use when**: The problem can be solved greedily (e.g., Dijkstra for general graphs) or if the grid allows movement in all 4 directions with cycles (use BFS/DFS).
    **不適用時機**：問題可以用貪婪演算法解決（如一般圖的 Dijkstra），或者網格允許四個方向移動且包含循環時（應使用 BFS/DFS）。

---

## 3. Typical Patterns（典型題型 / 模式）

For the "Beginner" level of 2-D DP, we focus on two main patterns:
針對 2-D DP 的「初學者」階段，我們專注於兩種主要模式：

1.  **Grid Traversal (Robot Paths)**
    **網格遍歷（機器人路徑）**
    *   Movement is restricted (e.g., only right or down).
    *   移動受限（例如：只能向右或向下）。
    *   $dp[i][j] = dp[i-1][j] + dp[i][j-1]$ (Sum) or $min(dp[i-1][j], dp[i][j-1])$ (Optimization).
    *   $dp[i][j] = dp[i-1][j] + dp[i][j-1]$（求和）或 $min(dp[i-1][j], dp[i][j-1])$（最佳化）。

2.  **Two Sequences (Prefix Comparison)**
    **雙序列（前綴比較）**
    *   Comparing two strings or arrays $A$ and $B$.
    *   比較兩個字串或陣列 $A$ 和 $B$。
    *   $dp[i][j]$ represents the result for $A[0...i]$ and $B[0...j]$.
    *   $dp[i][j]$ 代表 $A[0...i]$ 和 $B[0...j]$ 的結果。

---

## 4. Example Walkthrough（範例講解）

### Problem: Unique Paths (LeetCode 62)
**問題重述**：
A robot is located at the top-left corner of an `m x n` grid.
一個機器人位於 `m x n` 網格的左上角。
The robot can only move either down or right at any point in time.
機器人在任何時間點只能向下或向右移動。
The robot is trying to reach the bottom-right corner. How many possible unique paths are there?
機器人試圖到達右下角。請問有多少條可能的唯一路徑？

### Approach 1: Brute Force (Recursion) - **Bad**
**思路 1：暴力法（遞迴）— 差**
*   Recursively call `uniquePaths(i+1, j)` and `uniquePaths(i, j+1)`.
    遞迴呼叫 `uniquePaths(i+1, j)` 和 `uniquePaths(i, j+1)`。
*   **Why it fails**: Exponential time complexity $O(2^{m+n})$. Many overlapping subproblems.
    **為何失敗**：指數級時間複雜度 $O(2^{m+n})$。存在大量重疊子問題。

### Approach 2: 2-D Dynamic Programming (Tabulation) - **Good**
**思路 2：二維動態規劃（列表法）— 好**
*   **State**: $dp[i][j]$ is the number of paths to reach cell $(i, j)$.
    **狀態**：$dp[i][j]$ 是到達格子 $(i, j)$ 的路徑數量。
*   **Transition**: To reach $(i, j)$, you must come from top $(i-1, j)$ or left $(i, j-1)$.
    **轉移**：要到達 $(i, j)$，必須來自上方 $(i-1, j)$ 或左方 $(i, j-1)$。
    $$dp[i][j] = dp[i-1][j] + dp[i][j-1]$$
*   **Base Case**: First row and first column are all 1 (only one way to move straight right or straight down).
    **基本情況**：第一列和第一行全為 1（只有一種方式可以直走右邊或直走下面）。

### Approach 3: Space Optimization (Rolling Array) - **Best**
**思路 3：空間優化（滾動陣列）— 最佳**
*   Notice we only need the *current row* and the *previous row*. We don't need the whole matrix.
    注意我們只需要「當前行」和「上一行」。我們不需要整個矩陣。
*   We can compress this further to a single 1D array.
    我們可以進一步將其壓縮為單個一維陣列。

### Java Reference Solution (Optimized)
**Java 參考解（優化版）**

```java
class Solution {
    /**
     * Calculates the number of unique paths in an m x n grid.
     * 計算 m x n 網格中的唯一路徑數。
     *
     * Time Complexity: O(m * n) - We visit every cell once.
     * 時間複雜度：O(m * n) - 我們訪問每個格子一次。
     * Space Complexity: O(n) - We only store one row.
     * 空間複雜度：O(n) - 我們只儲存一行。
     */
    public int uniquePaths(int m, int n) {
        // Edge case: if grid is 1x1, there is only 1 path.
        // 邊界情況：如果網格是 1x1，只有 1 條路徑。
        if (m <= 0 || n <= 0) return 0;
        
        // Use a 1D array to store the results of the "previous row".
        // 使用一維陣列來儲存「上一行」的結果。
        // Originally dp[i][j], now compressed to dp[j].
        // 原本是 dp[i][j]，現在壓縮為 dp[j]。
        int[] dp = new int[n];
        
        // Initialize the first row. There is only 1 way to reach any cell in the first row (go right).
        // 初始化第一行。到達第一行任何格子的方法只有 1 種（一直向右）。
        for (int j = 0; j < n; j++) {
            dp[j] = 1;
        }
        
        // Iterate through the grid starting from the second row (index 1).
        // 從第二行（索引 1）開始遍歷網格。
        for (int i = 1; i < m; i++) {
            // For each column in the current row.
            // 對於當前行的每一列。
            for (int j = 1; j < n; j++) {
                // dp[j] currently holds the value from the row above (top).
                // dp[j] 目前持有來自上一行（上方）的值。
                // dp[j-1] holds the updated value from the current row (left).
                // dp[j-1] 持有當前行（左方）已更新的值。
                
                // The recurrence: new_dp[j] = old_dp[j] (top) + new_dp[j-1] (left)
                // 遞迴關係：new_dp[j] = old_dp[j] (上) + new_dp[j-1] (左)
                dp[j] = dp[j] + dp[j - 1];
            }
        }
        
        // The last element contains the number of paths to the bottom-right corner.
        // 最後一個元素包含到達右下角的路徑數量。
        return dp[n - 1];
    }
}
```

### Error Demonstration (Common Mistake)
**錯誤示範（常見錯誤）**

```java
// Mistake: Forgetting to handle the first row/column separately in 2D array
// 錯誤：忘記在二維陣列中單獨處理第一行/第一列
int[][] dp = new int[m][n];
for (int i = 0; i < m; i++) {
    for (int j = 0; j < n; j++) {
        // This will throw IndexOutOfBoundsException when i=0 or j=0
        // 當 i=0 或 j=0 時，這會拋出 IndexOutOfBoundsException
        dp[i][j] = dp[i-1][j] + dp[i][j-1]; 
    }
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Padding (Padding)** | **Trap**: Accessing `dp[i-1]` when `i=0`. <br> **Fix**: Use a matrix of size `(m+1) x (n+1)` (1-based indexing) or handle base cases explicitly. <br> **陷阱**：當 `i=0` 時存取 `dp[i-1]`。<br> **解法**：使用大小為 `(m+1) x (n+1)` 的矩陣（1-based 索引）或明確處理基本情況。 |
| **Initialization (初始化)** | **Trap**: Assuming Java initializes arrays to what you want. <br> **Fact**: Java initializes `int[]` to 0. For "Minimum Path Sum", you might need to fill with `Integer.MAX_VALUE` initially. <br> **陷阱**：假設 Java 會將陣列初始化為你想要的值。<br> **事實**：Java 將 `int[]` 初始化為 0。對於「最小路徑和」，你可能需要先填入 `Integer.MAX_VALUE`。 |
| **M vs N (M 與 N)** | **Trap**: Confusing rows (`m`) and columns (`n`) in nested loops. <br> **Tip**: Always write `int rows = grid.length; int cols = grid[0].length;` at the start. <br> **陷阱**：在巢狀迴圈中混淆行 (`m`) 和列 (`n`)。<br> **技巧**：總是在開頭寫下 `int rows = grid.length; int cols = grid[0].length;`。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework (口條框架)
1.  **Define the State**: "I will define `dp[i][j]` as the number of paths to reach coordinates `(i, j)`."
    **定義狀態**：「我將定義 `dp[i][j]` 為到達座標 `(i, j)` 的路徑數量。」
2.  **Establish Recurrence**: "Since the robot can only move down or right, the value at `(i, j)` is the sum of the values from the top and left."
    **建立遞迴關係**：「由於機器人只能向下或向右移動，`(i, j)` 的值是來自上方和左方值的總和。」
3.  **Discuss Base Cases**: "The first row and first column are all 1s."
    **討論基本情況**：「第一列和第一行全都是 1。」
4.  **Optimize**: "A 2D matrix works, but we can optimize space to $O(N)$ since we only look at the previous row."
    **優化**：「二維矩陣可行，但我們可以將空間優化至 $O(N)$，因為我們只查看上一行。」

### Whiteboard Strategy (白板策略)
*   **Draw the Grid**: Draw a small 3x3 grid. Fill in the values manually to verify your logic before coding.
    **畫出網格**：畫一個小的 3x3 網格。在寫程式碼之前手動填入數值以驗證邏輯。
*   **Variable Naming**: Use `r` and `c` (row/col) or `i` and `j` consistently.
    **變數命名**：一致地使用 `r` 和 `c`（行/列）或 `i` 和 `j`。

### Common Follow-up (常見追問)
*   "What if there are obstacles in the grid?" (Set `dp[i][j] = 0` for obstacles).
    「如果網格中有障礙物怎麼辦？」（將障礙物的 `dp[i][j]` 設為 0）。
*   "Can you reconstruct the path?" (Store "parent" pointers or backtrack from the end).
    「你能重建路徑嗎？」（儲存「父節點」指標或從終點回溯）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Minimum Path Sum (LeetCode 64)
*   **Hint**: Similar to Unique Paths, but instead of adding ways, you take `grid[i][j] + min(top, left)`.
    **提示**：類似唯一路徑，但不是相加路徑數，而是取 `grid[i][j] + min(上, 左)`。
*   **Key**: Watch out for the first row/col initialization (accumulate sums).
    **關鍵**：注意第一行/列的初始化（累積總和）。

### 2. Medium: Unique Paths II (LeetCode 63)
*   **Hint**: Grid with obstacles. If `grid[i][j] == 1` (obstacle), then `dp[i][j] = 0`.
    **提示**：帶有障礙物的網格。如果 `grid[i][j] == 1`（障礙物），則 `dp[i][j] = 0`。
*   **Key**: Handle the case where the start or end is an obstacle.
    **關鍵**：處理起點或終點就是障礙物的情況。

### 3. Hard (Conceptual): Longest Common Subsequence (LeetCode 1143)
*   *Note: This is the gateway to Intermediate 2-D DP.*
    *註：這是通往中級 2-D DP 的入口。*
*   **Hint**: $dp[i][j]$ is LCS of `text1[0..i]` and `text2[0..j]`.
    **提示**：$dp[i][j]$ 是 `text1[0..i]` 和 `text2[0..j]` 的最長公共子序列。
*   **Logic**: If chars match, `1 + diagonal`. If not, `max(top, left)`.
    **邏輯**：如果字元匹配，`1 + 對角線`。如果不匹配，`max(上, 左)`。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review (自我審查)
- [ ] **State**: Does $dp[i][j]$ clearly mean something? (e.g., min cost, max profit, count).
    **狀態**：$dp[i][j]$ 是否有明確含義？（例如：最小成本、最大利潤、計數）。
- [ ] **Bounds**: Did I handle `i=0` and `j=0` correctly without crashing?
    **邊界**：我是否正確處理了 `i=0` 和 `j=0` 而沒有崩潰？
- [ ] **Return**: Am I returning `dp[m-1][n-1]` or something else?
    **回傳**：我是回傳 `dp[m-1][n-1]` 還是其他東西？

### Complexity Check (複雜度確認)
- [ ] Is Time Complexity $O(M \times N)$?
    時間複雜度是 $O(M \times N)$ 嗎？
- [ ] Is Space Complexity optimized to $O(N)$ if possible?
    空間複雜度是否盡可能優化至 $O(N)$？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Spreadsheet" Analogy (「試算表」類比)
Imagine you are writing a formula in Excel cell `C3`.
想像你在 Excel 的儲存格 `C3` 中寫公式。
You say `=B3 + C2`.
你寫 `=B3 + C2`。
You then drag this formula to fill the entire sheet.
然後你拖曳這個公式填滿整個表格。
**2-D DP is exactly this process**: Defining the formula for one cell and dragging it across the matrix.
**二維動態規劃正是這個過程**：定義一個格子的公式，然後將其應用於整個矩陣。

### The "Waterfall" Visualization (「瀑布」視覺化)
For space optimization, imagine a waterfall.
對於空間優化，想像一個瀑布。
Water flows from one level to the next.
水從一層流向下一層。
Once the water reaches level `i`, the water at level `i-1` is gone/irrelevant. You only need the current level to calculate the next.
一旦水流到達第 `i` 層，第 `i-1` 層的水就消失/無關了。你只需要當前層來計算下一層。