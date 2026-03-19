Here is the comprehensive guide for **2-D Dynamic Programming**, tailored for a Senior Software Engineer interview preparation.
這是一份針對資深軟體工程師面試準備的 **二維動態規劃（2-D Dynamic Programming）** 完整指南。

---

# 2-D Dynamic Programming (Intermediate)

## 1. Learning Objectives (學習目標)

1.  **Master State Definition**: Learn to define $dp[i][j]$ representing the optimal result for the first $i$ elements of one structure and first $j$ of another (or coordinates $(i, j)$ in a grid).
    **掌握狀態定義**：學會定義 $dp[i][j]$ 來表示第一個結構的前 $i$ 個元素與第二個結構的前 $j$ 個元素（或網格中的座標 $(i, j)$）的最佳結果。

2.  **Derive Transition Equations**: confidently identify the relationship between the current cell and its predecessors (usually top, left, or top-left diagonal).
    **推導轉移方程式**：自信地找出當前格子與其前驅格子（通常是上方、左方或左上對角線）之間的關係。

3.  **Implement Space Optimization**: Understand how to reduce space complexity from $O(M \times N)$ to $O(N)$ using a rolling array or 1-D array.
    **實作空間優化**：理解如何使用滾動陣列或一維陣列將空間複雜度從 $O(M \times N)$ 降低到 $O(N)$。

4.  **Handle Boundary Conditions**: Systematically manage initialization (padding) to avoid "Index Out of Bounds" errors.
    **處理邊界條件**：系統化地管理初始化（填充），以避免「索引越界」錯誤。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
2-D DP involves solving problems where the state depends on two independent variables, typically represented by a 2D array or table.
二維動態規劃涉及解決狀態取決於兩個獨立變數的問題，通常由二維陣列或表格表示。

### Intuition (直覺)
Visualize filling a spreadsheet cell by cell.
想像逐格填寫電子試算表。
The value of a cell depends on the values of previously calculated cells (usually neighbors).
一個格子的值取決於先前計算過的格子（通常是鄰居）的值。

### Complexity (複雜度)
-   **Time**: $O(M \times N)$, where $M$ and $N$ are the dimensions of the inputs.
    **時間**：$O(M \times N)$，其中 $M$ 和 $N$ 是輸入的維度。
-   **Space**: $O(M \times N)$ naive, optimizable to $O(\min(M, N))$.
    **空間**：直觀解法為 $O(M \times N)$，可優化至 $O(\min(M, N))$。

### When to Use (適用場景)
-   **Grid Problems**: Finding paths, min sums, or obstacles in a matrix.
    **網格問題**：在矩陣中尋找路徑、最小和或避開障礙物。
-   **Dual Sequence Problems**: Comparing two strings/arrays (e.g., LCS, Edit Distance).
    **雙序列問題**：比較兩個字串/陣列（例如：最長公共子序列、編輯距離）。
-   **Knapsack Variations**: Selecting items with weight and value constraints.
    **背包問題變體**：在重量與價值限制下選擇物品。

### When NOT to Use (不適用場景)
-   If the data can be modeled as a graph where cyclic dependencies exist (use BFS/Dijkstra).
    如果數據可以建模為存在循環依賴的圖（請使用 BFS/Dijkstra）。
-   If the problem requires simple permutations without overlapping subproblems (use Backtracking).
    如果問題需要簡單的排列而沒有重疊子問題（請使用回溯法）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Grid Traversal (網格遍歷)
-   **Concept**: Move from top-left to bottom-right.
    **概念**：從左上角移動到右下角。
-   **Transition**: $dp[i][j] = f(dp[i-1][j], dp[i][j-1])$.
    **轉移**：$dp[i][j] = f(dp[i-1][j], dp[i][j-1])$。

### B. Dual Sequence Alignment (雙序列對齊)
-   **Concept**: Matching characters between String A and String B.
    **概念**：匹配字串 A 和字串 B 之間的字元。
-   **Transition**: Often involves checking if `A[i] == B[j]`. If match, look at diagonal $dp[i-1][j-1]$; if not, look at left/top.
    **轉移**：通常涉及檢查 `A[i] == B[j]`。如果匹配，查看對角線 $dp[i-1][j-1]$；如果不匹配，查看左方/上方。

### C. Partition / Interval (區間/分割)
-   **Concept**: Splitting a sequence into $k$ parts or dealing with palindromes.
    **概念**：將序列分割成 $k$ 個部分或處理迴文。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Common Subsequence (最長公共子序列)
**Problem Statement**: Given two strings `text1` and `text2`, return the length of their longest common subsequence.
**問題重述**：給定兩個字串 `text1` 和 `text2`，返回它們最長公共子序列的長度。

### Approach (思路)

1.  **Brute Force (暴力法)**:
    -   Generate all subsequences of `text1` and check if they exist in `text2`.
        生成 `text1` 的所有子序列並檢查它們是否存在於 `text2` 中。
    -   Complexity: $O(2^N)$. Too slow.
        複雜度：$O(2^N)$。太慢了。

2.  **DP State Definition (DP 狀態定義)**:
    -   Let $dp[i][j]$ be the LCS length of `text1[0...i-1]` and `text2[0...j-1]`.
        令 $dp[i][j]$ 為 `text1[0...i-1]` 和 `text2[0...j-1]` 的 LCS 長度。
    -   **Why padding?** Using size `(M+1) x (N+1)` handles empty string base cases automatically.
        **為什麼要填充？** 使用大小 `(M+1) x (N+1)` 可以自動處理空字串的基礎情況。

3.  **Transition Equation (轉移方程式)**:
    -   If `text1[i-1] == text2[j-1]`: We found a match! Add 1 to the result without these characters ($dp[i-1][j-1] + 1$).
        如果 `text1[i-1] == text2[j-1]`：我們找到了一個匹配！在不包含這些字元的結果上加 1 ($dp[i-1][j-1] + 1$)。
    -   Else: We take the best result by either skipping a char from `text1` or `text2`.
        否則：我們通過跳過 `text1` 或 `text2` 的一個字元來取最佳結果。
        $dp[i][j] = \max(dp[i-1][j], dp[i][j-1])$.

### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int longestCommonSubsequence(String text1, String text2) {
        int m = text1.length();
        int n = text2.length();
        
        // DP table initialization
        // dp[i][j] stores LCS length for text1[0..i-1] and text2[0..j-1]
        // DP 表初始化
        // dp[i][j] 儲存 text1[0..i-1] 與 text2[0..j-1] 的 LCS 長度
        int[][] dp = new int[m + 1][n + 1];
        
        // Iterate through both strings
        // 遍歷兩個字串
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                // Check if characters match (note index offset)
                // 檢查字元是否匹配（注意索引偏移）
                if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                    // Match found: extend the sequence from the diagonal
                    // 發現匹配：從對角線延伸序列
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    // No match: take the maximum of excluding current char from either string
                    // 無匹配：取排除任一字串當前字元後的較大值
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        
        // The bottom-right cell contains the answer
        // 右下角的格子包含答案
        return dp[m][n];
    }
}
```

### Space Optimization (空間優化)
Since $dp[i][j]$ only depends on row $i-1$, we can use two rows (current and previous) or even a single 1D array.
由於 $dp[i][j]$ 僅依賴於第 $i-1$ 行，我們可以使用兩行（當前行和上一行），甚至是一個一維陣列。

```java
// Optimized Space Version
// 空間優化版本
public int longestCommonSubsequenceOptimized(String text1, String text2) {
    int m = text1.length(), n = text2.length();
    int[] dp = new int[n + 1];
    
    for (int i = 1; i <= m; i++) {
        int prevDiagonal = 0; // Stores dp[i-1][j-1]
        for (int j = 1; j <= n; j++) {
            int temp = dp[j]; // Capture value before update (it acts as dp[i-1][j])
            if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                dp[j] = prevDiagonal + 1;
            } else {
                dp[j] = Math.max(dp[j], dp[j - 1]);
            }
            prevDiagonal = temp; // Update diagonal for next iteration
        }
    }
    return dp[n];
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Subsequence vs. Substring** | Thinking they are the same. <br> 以為它們是一樣的。 | **Substring**: Continuous (e.g., "abc" in "zabcde"). <br> **Subsequence**: Order preserved but not necessarily continuous (e.g., "ace" in "abcde"). <br> **子字串**：連續的。**子序列**：順序保留但不一定連續。 |
| **Initialization** | Forgetting to initialize base cases (e.g., row 0 or col 0). <br> 忘記初始化基礎情況（例如第 0 行或第 0 列）。 | For "Min Path Sum", initialize padding with `Integer.MAX_VALUE`, not 0. <br> 對於「最小路徑和」，填充值應初始化為 `Integer.MAX_VALUE`，而非 0。 |
| **Index Alignment** | `dp[i]` mapping to `s.charAt(i)`. <br> `dp[i]` 對應到 `s.charAt(i)`。 | Usually `dp[i]` corresponds to prefix length `i`, so it maps to `s.charAt(i-1)`. <br> 通常 `dp[i]` 對應前綴長度 `i`，所以它映射到 `s.charAt(i-1)`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (口條框架)
1.  **Define the subproblem**: "I will define `dp[i][j]` as the answer for the prefix of size `i` and `j`."
    **定義子問題**：「我將定義 `dp[i][j]` 為長度 `i` 和 `j` 的前綴的答案。」
2.  **Establish recurrence**: "To solve for `(i, j)`, I need to decide between option A and option B..."
    **建立遞迴關係**：「為了解決 `(i, j)`，我需要在選項 A 和選項 B 之間做決定...」
3.  **Discuss Base Cases**: "When one string is empty, the result is 0."
    **討論基礎情況**：「當其中一個字串為空時，結果為 0。」

### Whiteboard Strategy (白板策略)
-   Draw a small 2D grid (e.g., 3x3 or 4x4) for a simple example.
    為簡單範例畫一個小的 2D 網格（例如 3x3 或 4x4）。
-   Fill in the first row and column manually to show you understand initialization.
    手動填寫第一行和第一列，以表明你理解初始化。
-   Write the transition equation clearly *before* writing code.
    在寫程式碼*之前*清楚地寫出轉移方程式。

### Follow-up Handling (常見追問)
-   **Q**: "Can you optimize the space?"
    **問**：「你能優化空間嗎？」
-   **A**: "Yes, since we only look at the previous row, we can use a rolling array to reduce space to $O(N)$."
    **答**：「可以，因為我們只查看上一行，我們可以使用滾動陣列將空間減少到 $O(N)$。」
-   **Q**: "What if we need to print the actual path/string?"
    **問**：「如果我們需要列印實際的路徑/字串怎麼辦？」
-   **A**: "We cannot use space optimization then. We need the full 2D table to backtrack from `dp[m][n]` to `dp[0][0]`."
    **答**：「那樣我們就不能使用空間優化。我們需要完整的 2D 表格從 `dp[m][n]` 回溯到 `dp[0][0]`。」

---

## 7. Practice Problems (練習題)

### Easy: Unique Paths (不同路徑)
-   **Problem**: Robot moves from top-left to bottom-right. Can only move down or right. Count paths.
    **問題**：機器人從左上角移動到右下角。只能向下或向右移動。計算路徑數。
-   **Hint**: $dp[i][j] = dp[i-1][j] + dp[i][j-1]$.
    **提示**：$dp[i][j] = dp[i-1][j] + dp[i][j-1]$。

### Medium: Edit Distance (編輯距離)
-   **Problem**: Min operations (insert, delete, replace) to convert word1 to word2.
    **問題**：將 word1 轉換為 word2 所需的最少操作數（插入、刪除、替換）。
-   **Hint**:
    -   Match: $dp[i-1][j-1]$.
    -   Insert/Delete/Replace: $1 + \min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])$.
    **提示**：
    -   匹配：$dp[i-1][j-1]$。
    -   插入/刪除/替換：$1 + \min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])$。

### Hard: Maximal Square (最大正方形)
-   **Problem**: Find the largest square containing only 1s in a binary matrix.
    **問題**：在二進制矩陣中找到只包含 1 的最大正方形。
-   **Hint**: $dp[i][j]$ is the side length of the square ending at $(i, j)$.
    $dp[i][j] = \min(\text{left}, \text{up}, \text{diagonal}) + 1$.
    **提示**：$dp[i][j]$ 是以 $(i, j)$ 結尾的正方形邊長。
    $dp[i][j] = \min(\text{左}, \text{上}, \text{對角}) + 1$。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
-   [ ] Did I define the DP state clearly in comments? (我有在註解中清楚定義 DP 狀態嗎？)
-   [ ] are the dimensions `N` vs `N+1` handled consistently? (維度 `N` 與 `N+1` 的處理是否一致？)
-   [ ] Did I handle the `i=0` or `j=0` boundaries? (我有處理 `i=0` 或 `j=0` 的邊界嗎？)
-   [ ] Is the return value `dp[m][n]` or something else (like `max` over all cells)? (返回值是 `dp[m][n]` 還是其他東西（如所有格子中的最大值）？)

### Debugging (除錯)
-   If output is 0: Check initialization logic.
    如果輸出為 0：檢查初始化邏輯。
-   If IndexOutOfBounds: Check loop conditions (`<=` vs `<`) and array sizing.
    如果索引越界：檢查迴圈條件（`<=` vs `<`）和陣列大小。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Three Neighbors" Rule (「三個鄰居」法則)
For most 2D DP (like Edit Distance or Maximal Square), imagine looking at your three neighbors to make a decision:
對於大多數 2D DP（如編輯距離或最大正方形），想像看著你的三個鄰居來做決定：
1.  **Top ($i-1, j$)**: "Inherit from above".
    **上方 ($i-1, j$)**：「從上方繼承」。
2.  **Left ($i, j-1$)**: "Inherit from left".
    **左方 ($i, j-1$)**：「從左方繼承」。
3.  **Diagonal ($i-1, j-1$)**: "Extend from match/replace".
    **對角 ($i-1, j-1$)**：「從匹配/替換延伸」。

### Visual Anchor (圖像錨點)
Think of the DP table as a **Map**.
把 DP 表想像成一張**地圖**。
-   **Target**: Bottom-Right corner.
    **目標**：右下角。
-   **Obstacles**: Mismatched characters increasing cost.
    **障礙**：不匹配的字元會增加成本。
-   **Path**: The sequence of decisions leading to the optimal value.
    **路徑**：導致最佳值的決策序列。