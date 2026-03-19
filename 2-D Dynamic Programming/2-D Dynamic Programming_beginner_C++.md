Here is a comprehensive guide to **2-D Dynamic Programming**, tailored for a Senior Software Engineer (Beginner to this specific topic), using C++ with bilingual explanations.

這是一份針對 **二維動態規劃（2-D Dynamic Programming）** 的完整指南，專為資深軟體工程師（此主題的初學者）量身打造，使用 C++ 並附帶雙語解說。

---

# 2-D Dynamic Programming: From Grid to Mastery
# 二維動態規劃：從網格到精通

## 1. Learning Goals（學習目標）

1.  **Master State Definition**: Learn how to define `dp[i][j]` to represent the solution to a subproblem ending at specific coordinates or indices.
    **掌握狀態定義**：學習如何定義 `dp[i][j]` 來表示在特定座標或索引結束的子問題解。
2.  **Understand Transition Logic**: Visualize how values propagate through a 2D matrix (usually from top-left to bottom-right).
    **理解轉移邏輯**：視覺化數值如何在二維矩陣中傳遞（通常是從左上到右下）。
3.  **Space Optimization**: Learn how to reduce space complexity from $O(N \times M)$ to $O(N)$ using a rolling array.
    **空間優化**：學習如何使用滾動陣列（Rolling Array）將空間複雜度從 $O(N \times M)$ 降低到 $O(N)$。
4.  **Differentiate Patterns**: Distinguish between "Grid Path" problems and "Dual Sequence" (e.g., String Matching) problems.
    **區分題型模式**：分辨「網格路徑」問題與「雙序列」（如字串匹配）問題。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
2-D DP is an extension of 1-D DP where the state depends on two variables, typically represented as a table or grid.
二維動態規劃是一維 DP 的延伸，其狀態取決於兩個變數，通常以表格或網格表示。

### Intuition（直覺）
Imagine filling an Excel sheet cell by cell.
想像逐格填寫 Excel 表格。
The value of the current cell depends on its immediate neighbors (usually Top, Left, or Top-Left).
當前格子的值取決於其直接相鄰的格子（通常是上方、左方或左上方）。

### Complexity（複雜度）
-   **Time**: $O(N \times M)$ — We must visit every cell in the grid once.
    **時間**：$O(N \times M)$ — 我們必須訪問網格中的每個格子一次。
-   **Space**: $O(N \times M)$ for the full table, optimizable to $O(\min(N, M))$ (linear space).
    **空間**：完整表格為 $O(N \times M)$，可優化至 $O(\min(N, M))$（線性空間）。

### When to Use（適用場景）
-   **Grid Problems**: Finding paths, counting paths, or min/max sums in a matrix.
    **網格問題**：在矩陣中尋找路徑、計算路徑數或最小/最大總和。
-   **String/Sequence Matching**: Longest Common Subsequence (LCS), Edit Distance.
    **字串/序列匹配**：最長公共子序列 (LCS)、編輯距離。
-   **Knapsack Variations**: 0/1 Knapsack (State: Item Index, Capacity).
    **背包問題變體**：0/1 背包問題（狀態：物品索引、容量）。

### When NOT to Use（不適用場景）
-   **Graph with Cycles**: If movement allows going back to a visited state, it's likely a Graph (BFS/Dijkstra) problem, not DP.
    **帶環圖**：如果移動允許回到已訪問的狀態，這通常是圖論（BFS/Dijkstra）問題，而非 DP。
-   **Simple Greedy**: If a local optimal choice always leads to a global optimum, use Greedy.
    **簡單貪婪**：如果局部最佳選擇總是導致全局最佳，請使用貪婪演算法。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Grid Paths (Robot Movement)
### 模式 A：網格路徑（機器人移動）
-   **State**: `dp[i][j]` = Number of ways (or min cost) to reach cell $(i, j)$.
    **狀態**：`dp[i][j]` = 到達單元格 $(i, j)$ 的方法數（或最小成本）。
-   **Transition**: `dp[i][j] = dp[i-1][j] + dp[i][j-1]` (From Top and Left).
    **轉移**：`dp[i][j] = dp[i-1][j] + dp[i][j-1]`（來自上方與左方）。

### Pattern B: Dual Sequence (String Processing)
### 模式 B：雙序列（字串處理）
-   **State**: `dp[i][j]` = Result for comparing `string A[0...i]` and `string B[0...j]`.
    **狀態**：`dp[i][j]` = 比較 `string A[0...i]` 與 `string B[0...j]` 的結果。
-   **Transition**: Often involves `dp[i-1][j-1]` (Diagonal) if characters match.
    **轉移**：如果字元匹配，通常涉及 `dp[i-1][j-1]`（對角線）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Minimum Path Sum
### 問題：最小路徑和

**Problem Statement (問題重述)**:
Given a $m \times n$ grid filled with non-negative numbers, find a path from top-left to bottom-right which minimizes the sum of all numbers along its path. You can only move either down or right at any point in time.
給定一個填滿非負整數的 $m \times n$ 網格，找出從左上角到右下角的路徑，使其路徑上所有數字的總和最小。你在任何時間點只能向下或向右移動。

### Thought Process（思路）

1.  **Brute Force (DFS)**: Try every possible path.
    **暴力法 (DFS)**：嘗試每一條可能的路徑。
    -   Complexity: $O(2^{N+M})$. Too slow.
    -   複雜度：$O(2^{N+M})$。太慢了。

2.  **DP Optimization**: The min path to $(i, j)$ only depends on the min path to $(i-1, j)$ and $(i, j-1)$.
    **DP 優化**：到達 $(i, j)$ 的最小路徑僅取決於到達 $(i-1, j)$ 和 $(i, j-1)$ 的最小路徑。
    -   Equation: `dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])`.
    -   方程式：`dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])`。

3.  **Boundary Conditions**: First row can only come from the left; first column can only come from above.
    **邊界條件**：第一列只能來自左邊；第一行只能來自上方。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    int minPathSum(vector<vector<int>>& grid) {
        // Handle edge case: empty grid
        // 處理邊界情況：空網格
        if (grid.empty() || grid[0].empty()) return 0;

        int m = grid.size();
        int n = grid[0].size();

        // Initialize DP table with same dimensions as grid
        // 初始化與網格相同大小的 DP 表
        vector<vector<int>> dp(m, vector<int>(n, 0));

        // Base case: The starting point cost is the grid value itself
        // 基本情況：起點的成本即為網格該處的數值
        dp[0][0] = grid[0][0];

        // Initialize the first column (can only come from top)
        // 初始化第一行（只能從上方來）
        for (int i = 1; i < m; ++i) {
            dp[i][0] = dp[i - 1][0] + grid[i][0];
        }

        // Initialize the first row (can only come from left)
        // 初始化第一列（只能從左方來）
        for (int j = 1; j < n; ++j) {
            dp[0][j] = dp[0][j - 1] + grid[0][j];
        }

        // Fill the rest of the grid
        // 填滿剩餘的網格
        for (int i = 1; i < m; ++i) {
            for (int j = 1; j < n; ++j) {
                // Transition: Current cost + min(Top, Left)
                // 轉移：當前成本 + min(上方, 左方)
                dp[i][j] = grid[i][j] + min(dp[i - 1][j], dp[i][j - 1]);
            }
        }

        // The answer is at the bottom-right corner
        // 答案位於右下角
        return dp[m - 1][n - 1];
    }
};
```

### Space Optimization (Advanced)
### 空間優化（進階）
We only need the previous row to calculate the current row. We can reduce space to $O(N)$.
我們只需要前一列的數據來計算當前列。我們可以將空間減少到 $O(N)$。

```cpp
// Optimized Space: O(N)
// 空間優化：O(N)
int minPathSumOptimized(vector<vector<int>>& grid) {
    int m = grid.size();
    int n = grid[0].size();
    
    // Use a 1D vector to store the current row's minimums
    // 使用一維向量儲存當前列的最小值
    vector<int> dp(n, 0);

    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == 0 && j == 0) {
                // Start point
                // 起點
                dp[j] = grid[i][j];
            } else if (i == 0) {
                // First row: can only come from left (previous j)
                // 第一列：只能來自左方（前一個 j）
                dp[j] = dp[j - 1] + grid[i][j];
            } else if (j == 0) {
                // First column: can only come from top (current j, which holds previous row's value)
                // 第一行：只能來自上方（當前的 j，此時保存著上一列的值）
                dp[j] = dp[j] + grid[i][j];
            } else {
                // General case: min(Top, Left)
                // 一般情況：min(上方, 左方)
                // dp[j] is 'Top' (from prev iteration), dp[j-1] is 'Left' (just updated)
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j];
            }
        }
    }
    return dp[n - 1];
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Padding vs. No Padding** <br> **填充 vs. 無填充** | **Pitfall**: In string problems (LCS), it's often easier to make the DP table size $(N+1) \times (M+1)$ to handle empty strings gracefully. Without padding, index handling (`i-1`) becomes messy. <br> **陷阱**：在字串問題（LCS）中，通常將 DP 表大小設為 $(N+1) \times (M+1)$ 以優雅處理空字串。若無填充，索引處理（`i-1`）會變得很混亂。 |
| **Initialization** <br> **初始化** | **Pitfall**: For "Minimum Path" problems, padding cells should be initialized to `Infinity`, not `0`. For "Counting" problems, they might be `0` or `1`. <br> **陷阱**：對於「最小路徑」問題，填充的格子應初始化為 `Infinity`，而非 `0`。對於「計數」問題，則可能是 `0` 或 `1`。 |
| **Coordinate Confusion** <br> **座標混淆** | **Pitfall**: In math, $(x, y)$ is (col, row). In matrices, `grid[i][j]` is (row, col). Don't mix them up. <br> **陷阱**：數學上 $(x, y)$ 是（行，列）。在矩陣中，`grid[i][j]` 是（列，行）。不要混淆。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **Define State**: "I will use a 2D array `dp[i][j]` where each cell represents..."
    **定義狀態**：「我將使用一個二維陣列 `dp[i][j]`，其中每個格子代表……」
2.  **Establish Recurrence**: "To solve for `dp[i][j]`, I need to look at..." (Write the math equation on the board).
    **建立遞迴關係**：「為了求解 `dp[i][j]`，我需要查看……」（在白板上寫下數學方程式）。
3.  **Base Cases**: "The edges of the grid are special because..."
    **基本情況**：「網格的邊緣很特殊，因為……」

### Whiteboard Strategy（白板策略）
-   Draw a small $3 \times 3$ grid.
    畫一個小的 $3 \times 3$ 網格。
-   Fill the first row and first column manually before writing code. This proves you understand the initialization.
    在寫程式碼之前，手動填寫第一列和第一行。這證明你理解初始化過程。

### Common Follow-ups（常見追問）
-   "Can you optimize the space complexity?" (Hint: Rolling Array).
    「你能優化空間複雜度嗎？」（提示：滾動陣列）。
-   "What if obstacles are introduced?" (Hint: If obstacle, `dp[i][j] = 0` or `Infinity`).
    「如果有障礙物怎麼辦？」（提示：若有障礙，`dp[i][j] = 0` 或 `Infinity`）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Unique Paths
**Hint**: Similar to Min Path Sum, but you sum the *possibilities*, not the values. `dp[i][j] = dp[i-1][j] + dp[i][j-1]`.
**提示**：類似最小路徑和，但你是加總「可能性」，而非數值。`dp[i][j] = dp[i-1][j] + dp[i][j-1]`。

### 2. Intermediate: Longest Common Subsequence (LCS)
**Hint**: Input is two strings. If `text1[i] == text2[j]`, then `dp[i][j] = 1 + dp[i-1][j-1]`. Else, take max of Top or Left.
**提示**：輸入是兩個字串。如果 `text1[i] == text2[j]`，則 `dp[i][j] = 1 + dp[i-1][j-1]`。否則，取上方或左方的最大值。

### 3. Advanced (for Beginner 2D): Maximal Square
**Hint**: Find the largest square containing only 1s. `dp[i][j]` represents the side length of the largest square ending at $(i, j)$. Transition involves `min(Top, Left, Top-Left) + 1`.
**提示**：找出只包含 1 的最大正方形。`dp[i][j]` 代表以 $(i, j)$ 結尾的最大正方形邊長。轉移涉及 `min(上方, 左方, 左上方) + 1`。

---

## 8. Quick Checklists（快速檢核表）

-   [ ] **State**: Does `dp[i][j]` clearly mean something? (e.g., min cost, max items).
    **狀態**：`dp[i][j]` 是否有明確意義？（例如：最小成本、最大物品數）。
-   [ ] **Dimensions**: Did I allocate `m` rows and `n` cols, or `m+1` and `n+1`?
    **維度**：我配置了 `m` 列 `n` 行，還是 `m+1` 和 `n+1`？
-   [ ] **Base Case**: Is `dp[0][0]` (or the borders) initialized correctly?
    **基本情況**：`dp[0][0]`（或邊界）是否正確初始化？
-   [ ] **Loops**: Are loops starting from 0 or 1? (Depends on initialization).
    **迴圈**：迴圈是從 0 還是 1 開始？（取決於初始化）。
-   [ ] **Return**: Am I returning `dp[m-1][n-1]` or something else?
    **回傳**：我是回傳 `dp[m-1][n-1]` 還是其他東西？

---

## 9. Memory Anchors（記憶錨點）

### Visualizing the Dependencies (視覺化依賴關係)

Think of the **"Empire Expansion" (帝國擴張)**:

1.  **Grid Paths**: You can only expand your territory from the **North** or **West**.
    **網格路徑**：你只能從**北方**或**西方**擴張領土。
    *(Dependency: Top & Left)*

2.  **String Matching (LCS)**: Sometimes you find a secret tunnel from the **North-West** (Diagonal) when characters match.
    **字串匹配 (LCS)**：當字元匹配時，有時你會發現一條來自**西北方**（對角線）的秘密通道。
    *(Dependency: Top, Left, & Diagonal)*

```text
[Diagonal]  [Top]
    \         |
     \        |
      \       v
[Left] ->  [Target]
```

Use this visual to quickly decide which previous cells you need to query.
使用這個視覺圖像來快速決定你需要查詢哪些之前的格子。