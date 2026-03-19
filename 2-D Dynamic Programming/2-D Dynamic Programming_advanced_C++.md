Here is the comprehensive guide on **2-D Dynamic Programming (Advanced)**, tailored for a Senior Software Engineer, written in C++ with a bilingual format.

---

# Advanced 2-D Dynamic Programming (二維動態規劃進階指南)

## 1. Learning Objectives (學習目標)

*   **Master State Definition & Transition:** Move beyond basic grid traversal to complex state definitions involving strings, intervals, and constraints.
    **掌握狀態定義與轉移：** 超越基礎網格遍歷，掌握涉及字串、區間與約束條件的複雜狀態定義。
*   **Optimize Space Complexity:** Learn to reduce space from $O(N \times M)$ to $O(\min(N, M))$ using Rolling Arrays.
    **優化空間複雜度：** 學習使用滾動陣列（Rolling Arrays）將空間從 $O(N \times M)$ 降低至 $O(\min(N, M))$。
*   **Identify Advanced Patterns:** Distinguish between Coordinate DP, Interval DP, and Knapsack-style 2-D variations.
    **識別進階模式：** 區分座標型 DP、區間型 DP 以及背包類型的二維變體。
*   **Debug & Verify:** Establish a mental framework for handling off-by-one errors and boundary conditions in matrix-based logic.
    **除錯與驗證：** 建立處理矩陣邏輯中「差一錯誤」（off-by-one errors）與邊界條件的心智框架。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
2-D Dynamic Programming involves solving problems where the state depends on two independent variables, typically represented as a table $dp[i][j]$.
二維動態規劃涉及解決狀態取決於兩個獨立變數的問題，通常表示為一個表格 $dp[i][j]$。

### Intuition (直覺)
Think of filling a matrix where each cell represents the optimal solution for a subproblem defined by row $i$ and column $j$.
想像填寫一個矩陣，其中每個單元格代表由行 $i$ 和列 $j$ 定義的子問題的最佳解。
The value of the current cell is derived from previously computed cells (usually left, top, or top-left).
當前單元格的值源自先前計算的單元格（通常是左方、上方或左上方）。

### Complexity (複雜度)
*   **Time:** Generally $O(N \times M)$ or $O(N^2)$ for Interval DP.
    **時間：** 通常為 $O(N \times M)$，若是區間 DP 則為 $O(N^2)$。
*   **Space:** Naively $O(N \times M)$, optimizable to $O(M)$ (linear space).
    **空間：** 樸素做法為 $O(N \times M)$，可優化至 $O(M)$（線性空間）。

### When to Use (適用場景)
*   **String Processing:** Edit Distance, Longest Common Subsequence.
    **字串處理：** 編輯距離、最長公共子序列。
*   **Grid Optimization:** Minimum path sum, counting unique paths with obstacles.
    **網格優化：** 最小路徑和、計算帶障礙物的唯一路徑。
*   **Interval Problems:** Matrix Chain Multiplication, Burst Balloons.
    **區間問題：** 矩陣鏈乘積、戳氣球。

### When NOT to Use (不適用場景)
*   If the problem can be modeled as a graph where Dijkstra or BFS is more efficient (e.g., cyclic dependencies or non-DAG structures).
    如果問題可以建模為圖，且 Dijkstra 或 BFS 更有效率時（例如循環依賴或非 DAG 結構）。
*   If the input size is too large (e.g., $N=10^5$), implying an $O(N \log N)$ or $O(N)$ solution is required.
    如果輸入規模過大（例如 $N=10^5$），暗示需要 $O(N \log N)$ 或 $O(N)$ 的解法。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Coordinate / Grid DP (座標/網格型)
*   **State:** $dp[i][j]$ depends on $dp[i-1][j]$ and $dp[i][j-1]$.
    **狀態：** $dp[i][j]$ 取決於 $dp[i-1][j]$ 和 $dp[i][j-1]$。
*   **Example:** Unique Paths, Minimum Path Sum.
    **範例：** 不同路徑、最小路徑和。

### B. Dual Sequence / String DP (雙序列/字串型)
*   **State:** $dp[i][j]$ represents the result for prefix $s1[0...i]$ and $s2[0...j]$.
    **狀態：** $dp[i][j]$ 代表前綴 $s1[0...i]$ 與 $s2[0...j]$ 的結果。
*   **Transition:** Often involves checking if $s1[i] == s2[j]$.
    **轉移：** 通常涉及檢查 $s1[i] == s2[j]$。
*   **Example:** Longest Common Subsequence (LCS), Edit Distance.
    **範例：** 最長公共子序列 (LCS)、編輯距離。

### C. Interval DP (區間型 - Advanced)
*   **State:** $dp[i][j]$ represents the optimal value for the subarray/substring from index $i$ to $j$.
    **狀態：** $dp[i][j]$ 代表從索引 $i$ 到 $j$ 的子陣列/子字串的最佳值。
*   **Transition:** Loop through a split point $k$ between $i$ and $j$.
    **轉移：** 在 $i$ 和 $j$ 之間遍歷一個分割點 $k$。
*   **Order:** Iterate by length of the interval, not just simple indices.
    **順序：** 依據區間長度迭代，而非僅依據簡單索引。

---

## 4. Example Walkthrough (範例講解)

### Problem: Edit Distance (Hard)
**Problem Statement:**
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.
給定兩個字串 `word1` 和 `word2`，返回將 `word1` 轉換為 `word2` 所需的最小操作數。
You have the following three operations permitted on a word: Insert, Delete, Replace.
你可以對一個單字進行以下三種操作：插入、刪除、替換。

### Approach 1: Brute Force (Recursion) - Mental Model
We compare characters from the end. If they match, we move both pointers. If not, we try all 3 operations and take the minimum.
我們從末端比較字元。若匹配，移動兩個指標。若不匹配，嘗試所有 3 種操作並取最小值。
*   **Complexity:** $O(3^{\max(N, M)})$ - Exponential, TLE (Time Limit Exceeded).
    **複雜度：** $O(3^{\max(N, M)})$ - 指數級，會超時。

### Approach 2: 2-D DP (Tabulation) - The Standard Solution
**State Definition:**
$dp[i][j]$ is the min operations to convert `word1[0...i-1]` to `word2[0...j-1]`.
$dp[i][j]$ 是將 `word1[0...i-1]` 轉換為 `word2[0...j-1]` 所需的最小操作數。

**Base Cases:**
*   $dp[0][0] = 0$ (Empty to empty).
    $dp[0][0] = 0$ (空對空)。
*   $dp[i][0] = i$ (Transforming `word1` of length `i` to empty requires `i` deletions).
    $dp[i][0] = i$ (將長度為 `i` 的 `word1` 變為空字串需要 `i` 次刪除)。
*   $dp[0][j] = j$ (Transforming empty to `word2` of length `j` requires `j` insertions).
    $dp[0][j] = j$ (將空字串變為長度為 `j` 的 `word2` 需要 `j` 次插入)。

**Transition:**
If `word1[i-1] == word2[j-1]`:
$$dp[i][j] = dp[i-1][j-1]$$
Else:
$$dp[i][j] = 1 + \min(dp[i-1][j] \text{ (del)}, dp[i][j-1] \text{ (ins)}, dp[i-1][j-1] \text{ (rep)})$$

### C++ Reference Solution (Standard & Space Optimized)

```cpp
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    // Standard 2-D DP Solution (O(N*M) Space)
    // 標準二維 DP 解法 (O(N*M) 空間)
    int minDistance(string word1, string word2) {
        int m = word1.length();
        int n = word2.length();

        // dp[i][j] represents min operations for word1[0...i-1] to word2[0...j-1]
        // dp[i][j] 代表 word1[0...i-1] 轉換至 word2[0...j-1] 的最小操作數
        // Size is (m+1) x (n+1) to handle empty string cases.
        // 大小為 (m+1) x (n+1) 以處理空字串情況。
        vector<vector<int>> dp(m + 1, vector<int>(n + 1));

        // Initialization / 初始化
        for (int i = 0; i <= m; i++) dp[i][0] = i; // Deletions / 刪除
        for (int j = 0; j <= n; j++) dp[0][j] = j; // Insertions / 插入

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                // Note: string indices are 0-based, so we use i-1 and j-1
                // 注意：字串索引從 0 開始，所以我們使用 i-1 和 j-1
                if (word1[i - 1] == word2[j - 1]) {
                    // Characters match, no new operation needed
                    // 字元匹配，不需要新操作
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    // Mismatch: take min of Insert, Delete, Replace + 1
                    // 不匹配：取 插入、刪除、替換 的最小值 + 1
                    dp[i][j] = 1 + min({
                        dp[i - 1][j],    // Delete from word1 (刪除)
                        dp[i][j - 1],    // Insert into word1 (插入)
                        dp[i - 1][j - 1] // Replace (替換)
                    });
                }
            }
        }
        return dp[m][n];
    }

    // Advanced: Space Optimized Solution (O(N) Space)
    // 進階：空間優化解法 (O(N) 空間)
    int minDistanceOptimized(string word1, string word2) {
        int m = word1.length();
        int n = word2.length();
        
        // We only need the previous row to calculate the current row.
        // 我們只需要上一行來計算當前行。
        vector<int> prev(n + 1), curr(n + 1);

        // Initialize base case for the first row (empty word1)
        // 初始化第一行的基礎情況 (word1 為空)
        for (int j = 0; j <= n; j++) prev[j] = j;

        for (int i = 1; i <= m; i++) {
            // Base case for the first column of current row (word2 is empty)
            // 當前行第一列的基礎情況 (word2 為空)
            curr[0] = i; 
            
            for (int j = 1; j <= n; j++) {
                if (word1[i - 1] == word2[j - 1]) {
                    curr[j] = prev[j - 1];
                } else {
                    curr[j] = 1 + min({
                        prev[j],    // Delete (look up / 看上方)
                        curr[j - 1], // Insert (look left / 看左方)
                        prev[j - 1] // Replace (look diagonal / 看對角)
                    });
                }
            }
            // Move current row to previous for next iteration
            // 將當前行移至上一行以供下次迭代
            prev = curr;
        }
        return prev[n];
    }
};
```

### Why the "Wrong" Approach Fails (錯誤示範)
**Greedy Approach:** Always moving to the character that matches the soonest.
**貪婪法：** 總是移動到最快匹配的字元。
*   **Why wrong:** It fails to account for global optimization. A local match might force expensive operations later.
    **為何錯誤：** 它無法顧及全域最佳化。局部的匹配可能會導致後續需要昂貴的操作。
*   **Example:** `word1 = "aa"`, `word2 = "b"`. Greedy might try to keep 'a's, but the answer is replace+delete or delete+replace.

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Confusion (陷阱/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Grid Size vs. Index** | Declaring `dp[N][M]` but accessing `dp[N][M]`. | Declare `dp[N+1][M+1]` for 1-based logic or handle 0-index carefully. Often `dp[i]` corresponds to `string[i-1]`. <br> 宣告 `dp[N+1][M+1]` 以適應 1-based 邏輯，或小心處理 0-index。通常 `dp[i]` 對應 `string[i-1]`。 |
| **Initialization** | Leaving `dp` array with default 0s when finding Minimum. | Initialize with `INT_MAX` or a sufficiently large number when minimizing; 0 is fine for maximizing. <br> 求最小值時需初始化為 `INT_MAX` 或夠大的數；求最大值時 0 即可。 |
| **Subarray vs. Subsequence** | Confusing continuity requirements. | **Subarray/Substring:** Continuous ($dp[i][j]$ breaks if chars don't match). **Subsequence:** Discontinuous (carry over previous max value even if mismatch). <br> **子陣列/子字串：** 連續（若字元不匹配則中斷）。**子序列：** 不連續（即使不匹配也繼承先前最大值）。 |
| **Loop Order (Interval DP)** | Looping `i` from 0 to N, `j` from `i` to N. | For Interval DP, outer loop must be **Length (len)**, inner loop is **Start (i)**. You need small intervals computed before large ones. <br> 對於區間 DP，外層迴圈必須是 **長度 (len)**，內層是 **起點 (i)**。你需要先計算小區間才能算大區間。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define the State clearly:** "I will define `dp[i][j]` as the [max/min/count] of [object] considering indices $0..i$ and $0..j$."
    **清晰定義狀態：** 「我將 `dp[i][j]` 定義為考慮索引 $0..i$ 和 $0..j$ 的 [物件] 的 [最大值/最小值/計數]。」
2.  **Propose the Recurrence:** Write the math equation on the board *before* coding. This is your contract with the interviewer.
    **提出遞迴關係：** 在寫程式碼 *之前* 先在白板上寫下數學方程式。這是你與面試官的契約。
3.  **Discuss Base Cases:** "The table needs padding/initialization because..."
    **討論基礎情況：** 「表格需要填充/初始化，因為……」

### Whiteboard Strategy (白板策略)
*   Draw a small 2D grid (e.g., 3x3 or 4x4).
    畫一個小的二維網格（例如 3x3 或 4x4）。
*   Fill in the first row and column manually to verify your base cases.
    手動填寫第一行和第一列以驗證你的基礎情況。
*   **Follow-up Prep:** Be ready to convert $O(N \times M)$ space to $O(N)$ space (Rolling Array) immediately if asked.
    **後續追問準備：** 準備好在被問到時立即將 $O(N \times M)$ 空間轉換為 $O(N)$ 空間（滾動陣列）。

---

## 7. Practice Problems (練習題)

### Level 1: Intermediate (中級)
**Problem:** Longest Common Subsequence (LCS)
**Hint:** Similar to Edit Distance but only "keep" or "skip". No replacement cost.
**提示：** 類似編輯距離，但只有「保留」或「跳過」。沒有替換成本。
**Key Logic:** `if s1[i]==s2[j]: dp[i][j] = 1 + dp[i-1][j-1]; else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])`

### Level 2: Advanced (進階)
**Problem:** Maximal Square (LeetCode 221)
**Hint:** $dp[i][j]$ represents the side length of the largest square ending at $(i, j)$.
**提示：** $dp[i][j]$ 代表以 $(i, j)$ 為右下角的最大正方形邊長。
**Key Logic:** `dp[i][j] = min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]}) + 1` only if `matrix[i][j] == '1'`.

### Level 3: Expert (專家 - Interval DP)
**Problem:** Burst Balloons (LeetCode 312)
**Hint:** Think in reverse. Which balloon is the *last* to be burst?
**提示：** 反向思考。哪顆氣球是 *最後* 被戳破的？
**Key Logic:** $dp[i][j] = \max(dp[i][k] + dp[k][j] + nums[i] \times nums[k] \times nums[j])$ for all $k$ between $i, j$.
**Note:** This requires iterating by length (len = 1 to N).

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查/除錯)
- [ ] Did I allocate `N+1` size for the DP table to handle 1-based logic or empty strings?
    我是否為 DP 表分配了 `N+1` 的大小以處理 1-based 邏輯或空字串？
- [ ] Are the loops iterating in the correct direction (e.g., reverse for some Knapsack variants)?
    迴圈迭代方向是否正確（例如某些背包變體需要反向）？
- [ ] Did I handle the boundary indices (i=0, j=0) correctly inside the loop?
    我是否在迴圈內正確處理了邊界索引（i=0, j=0）？
- [ ] Is the return value `dp[n][m]` or something else (like `max` over the whole table)?
    返回值是 `dp[n][m]` 還是其他（如整張表的最大值）？

### Complexity Check (複雜度確認)
- [ ] **Time:** Is it $O(N^2)$, $O(N^3)$ (Interval DP), or $O(2^N)$ (Accidental recursion)?
    **時間：** 是 $O(N^2)$、$O(N^3)$（區間 DP）還是 $O(2^N)$（意外的遞迴）？
- [ ] **Space:** Can I optimize this to 1D array?
    **空間：** 我能將其優化為一維陣列嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Robot" Analogy (Grid DP):**
    Imagine a robot that can only move Right or Down. The value at any cell is the best result from where the robot *came from* (Top or Left).
    **「機器人」類比（網格 DP）：** 想像一個只能向右或向下移動的機器人。任何單元格的值都是機器人 *來源*（上方或左方）的最佳結果。

*   **The "Russian Dolls" Analogy (Interval DP):**
    Solving for a large interval $[i, j]$ is like enclosing two smaller Russian dolls $[i, k]$ and $[k, j]$. You must build the small dolls first (loop by length).
    **「俄羅斯套娃」類比（區間 DP）：** 求解大區間 $[i, j]$ 就像包裹兩個較小的俄羅斯套娃 $[i, k]$ 和 $[k, j]$。你必須先製作小套娃（按長度迴圈）。

*   **The "Scanner" Visualization (Space Optimization):**
    You don't need the memory of the whole page to read a line; you only need your eyes on the current line and the memory of the previous line context.
    **「掃描器」視覺化（空間優化）：** 閱讀一行不需要整頁的記憶體；你只需要注視當前行以及對上一行語境的記憶。