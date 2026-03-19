Here is the comprehensive guide designed for a Senior Software Engineer, focusing on **Advanced 2-D Dynamic Programming** with **Java** implementation.

---

# Advanced 2-D Dynamic Programming (進階二維動態規劃)

## 1. Learning Objectives (學習目標)

*   **Master State Definition in High-Dimensional Space:**
    精通高維空間中的狀態定義：不再僅僅依賴直覺，而是能夠精確定義 $dp[i][j]$ 代表的物理意義（如：編輯距離、最大利潤、區間回文數）。
    Move beyond intuition to precisely define the physical meaning of $dp[i][j]$ (e.g., edit distance, max profit, interval palindrome count).

*   **Derive Complex Recurrence Relations:**
    推導複雜的遞迴關係：能夠處理非線性的狀態轉移，包含多重條件判斷與依賴關係。
    Handle non-linear state transitions, including multiple conditional checks and dependencies.

*   **Optimize Space Complexity ($O(N^2) \to O(N)$):**
    優化空間複雜度：掌握「滾動陣列」（Rolling Array）技術，將空間從二維降至一維，這是資深職位面試的必備 Follow-up。
    Master the "Rolling Array" technique to reduce space from 2D to 1D, a mandatory follow-up for senior roles.

*   **Differentiate Between Grid, Sequence, and Interval Patterns:**
    區分網格、序列與區間模式：快速識別題目屬於「矩陣路徑」、「雙序列比對」還是「區間合併」類型。
    Quickly identify if a problem belongs to "Grid Paths", "Dual Sequence Alignment", or "Interval Merging" types.

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
2-D DP involves solving problems where the state depends on two independent variables, typically represented by a table (matrix).
二維動態規劃涉及解決狀態依賴於兩個獨立變數的問題，通常以表格（矩陣）表示。

The value at $dp[i][j]$ represents the optimal solution for the sub-problem ending at index $i$ of the first dimension and index $j$ of the second.
$dp[i][j]$ 的值代表了第一維度結尾於索引 $i$ 且第二維度結尾於索引 $j$ 的子問題之最佳解。

### Intuition (直覺)
Think of it as filling a grid where each cell's value is derived from its neighbors (usually top, left, or top-left).
將其想像為填滿一個網格，其中每個單元格的值源自其鄰居（通常是上方、左方或左上方）。

### Complexity (複雜度)
*   **Time:** Typically $O(M \times N)$, where $M$ and $N$ are the lengths of the two inputs.
    **時間：** 通常為 $O(M \times N)$，其中 $M$ 和 $N$ 是兩個輸入的長度。
*   **Space:** Naively $O(M \times N)$, optimizable to $O(\min(M, N))$ using state compression.
    **空間：** 樸素解法為 $O(M \times N)$，可利用狀態壓縮優化至 $O(\min(M, N))$。

### When to Use (適用場景) & When Not to Use (不適用場景)
*   **Use when:** You need to find the "best" (min/max) or "count" involving two strings, two arrays, or a grid traversal.
    **適用：** 當你需要尋找涉及兩個字串、兩個陣列或網格遍歷的「最佳」（最小/最大）或「計數」問題時。
*   **Don't use when:** The problem can be solved greedily (e.g., simple interval scheduling) or requires permutations (Backtracking).
    **不適用：** 當問題可以用貪婪演算法解決（例如簡單的區間調度）或需要排列組合（回溯法）時。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Dual Sequence Alignment (雙序列比對)
**Scenario:** Given two strings/arrays, find the relationship (LCS, Edit Distance).
**場景：** 給定兩個字串/陣列，找出其關係（最長公共子序列、編輯距離）。
**Transition:** $dp[i][j]$ usually depends on $dp[i-1][j-1]$, $dp[i-1][j]$, and $dp[i][j-1]$.
**轉移：** $dp[i][j]$ 通常依賴於 $dp[i-1][j-1]$、$dp[i-1][j]$ 和 $dp[i][j-1]$。

### B. Grid Traversal with Constraints (帶約束的網格遍歷)
**Scenario:** Robot moving from top-left to bottom-right with obstacles or costs.
**場景：** 機器人從左上移動到右下，帶有障礙物或成本。
**Transition:** $dp[i][j] = \text{func}(dp[i-1][j], dp[i][j-1]) + \text{cost}[i][j]$.
**轉移：** $dp[i][j] = \text{func}(dp[i-1][j], dp[i][j-1]) + \text{cost}[i][j]$。

### C. Interval DP (區間 DP - Advanced)
**Scenario:** Operations on subarrays where merging depends on boundaries (e.g., Burst Balloons, Matrix Chain Multiplication).
**場景：** 對子陣列進行操作，合併依賴於邊界（例如：戳氣球、矩陣鏈乘積）。
**Transition:** $dp[i][j] = \max(dp[i][k] + dp[k][j] + \text{cost})$ for $k$ between $i$ and $j$.
**轉移：** 對於 $i$ 和 $j$ 之間的所有 $k$，計算 $dp[i][j] = \max(dp[i][k] + dp[k][j] + \text{cost})$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Edit Distance (Levenshtein Distance)
**問題：編輯距離**

### Problem Statement (問題重述)
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.
給定兩個字串 `word1` 和 `word2`，返回將 `word1` 轉換為 `word2` 所需的最小操作數。
You have the following three operations permitted on a word: Insert, Delete, Replace.
你可以在一個單詞上執行以下三種操作：插入、刪除、替換。

### Approach (思路)

1.  **Brute Force (Recursion):**
    Try all operations at every step. Complexity is exponential $O(3^{M+N})$.
    **暴力解（遞迴）：** 在每一步嘗試所有操作。複雜度是指數級 $O(3^{M+N})$。

2.  **Optimization (DP Table):**
    Define $dp[i][j]$ as the edit distance between `word1[0...i-1]` and `word2[0...j-1]`.
    **優化（DP 表）：** 定義 $dp[i][j]$ 為 `word1[0...i-1]` 和 `word2[0...j-1]` 之間的編輯距離。

    *   If `word1[i-1] == word2[j-1]`: No operation needed. $dp[i][j] = dp[i-1][j-1]$.
        若 `word1[i-1] == word2[j-1]`：無需操作。$dp[i][j] = dp[i-1][j-1]$。
    *   If different: Take min of Insert, Delete, Replace + 1.
        若不同：取插入、刪除、替換的最小值 + 1。

### Java Solution (Java 參考解)

```java
class Solution {
    public int minDistance(String word1, String word2) {
        int m = word1.length();
        int n = word2.length();

        // Create a 2D DP table.
        // dp[i][j] represents the min operations to convert word1[0..i-1] to word2[0..j-1].
        // 建立二維 DP 表。
        // dp[i][j] 代表將 word1[0..i-1] 轉換為 word2[0..j-1] 所需的最小操作數。
        int[][] dp = new int[m + 1][n + 1];

        // Initialize base cases.
        // 初始化基本情況。
        
        // Converting word1[0..i-1] to empty string requires i deletions.
        // 將 word1[0..i-1] 轉換為空字串需要 i 次刪除。
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }

        // Converting empty string to word2[0..j-1] requires j insertions.
        // 將空字串轉換為 word2[0..j-1] 需要 j 次插入。
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }

        // Fill the DP table.
        // 填寫 DP 表。
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                // If characters match, no new operation is needed; inherit from diagonal.
                // 若字元匹配，無需新操作；繼承對角線的值。
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    // If mismatch, consider three operations:
                    // 1. Replace (diagonal + 1)
                    // 2. Delete (top + 1)
                    // 3. Insert (left + 1)
                    // 若不匹配，考慮三種操作：
                    // 1. 替換（對角線 + 1）
                    // 2. 刪除（上方 + 1）
                    // 3. 插入（左方 + 1）
                    dp[i][j] = 1 + Math.min(dp[i - 1][j - 1],    // Replace
                                   Math.min(dp[i - 1][j],        // Delete
                                            dp[i][j - 1]));      // Insert
                }
            }
        }

        // The answer is in the bottom-right cell.
        // 答案位於右下角的單元格。
        return dp[m][n];
    }
}
```

### Complexity & Constraints (複雜度與邊界條件)
*   **Time Complexity:** $O(M \times N)$ — We fill every cell once.
    **時間複雜度：** $O(M \times N)$ — 我們填寫每個單元格一次。
*   **Space Complexity:** $O(M \times N)$ — For the table. (Can be optimized to $O(\min(M, N))$).
    **空間複雜度：** $O(M \times N)$ — 用於表格。（可優化至 $O(\min(M, N))$）。

### Error Demonstration (錯誤示範)
**Common Mistake:** Ignoring the offset between 0-based string index and 1-based DP table index.
**常見錯誤：** 忽略 0-based 字串索引與 1-based DP 表索引之間的偏移。
*Wrong:* `if (word1.charAt(i) == word2.charAt(j))` inside the loop starting at 1. This causes `IndexOutOfBounds` or wrong comparison.
*錯誤：* 在從 1 開始的迴圈中使用 `if (word1.charAt(i) == word2.charAt(j))`。這會導致 `IndexOutOfBounds` 或錯誤的比較。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Padding (Padding)** | **Correct:** `dp[m+1][n+1]`. **Pitfall:** Using `dp[m][n]` makes handling empty string base cases messy and prone to bugs. <br> **正確：** `dp[m+1][n+1]`。**陷阱：** 使用 `dp[m][n]` 會讓處理空字串的基本情況變得混亂且容易出錯。 |
| **Initialization (初始化)** | **Correct:** Fill row 0 and col 0 correctly (e.g., 0, 1, 2...). **Pitfall:** Leaving them as default 0 when they should represent a cost (like deletion count). <br> **正確：** 正確填充第 0 列和第 0 行（如 0, 1, 2...）。**陷阱：** 當它們應該代表成本（如刪除次數）時，將其保留為預設值 0。 |
| **Subarray vs Subsequence (子陣列 vs 子序列)** | **Subarray:** Continuous. **Subsequence:** Non-continuous but ordered. DP transitions differ significantly (resetting vs accumulating). <br> **子陣列：** 連續。**子序列：** 不連續但有序。DP 轉移有顯著差異（重置 vs 累積）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Framework: REACTO (Clarify, Approach, Code, Test, Optimize)

1.  **Clarify (釐清):** "Can the strings be empty?", "Are operations weighted equally?"
    **釐清：** 「字串可以是空的嗎？」「所有操作的權重是否相等？」
2.  **Whiteboard Strategy (白板策略):**
    *   Draw the grid for a small example (e.g., "HORSE" vs "ROS").
    *   畫出一個小範例的網格（例如："HORSE" vs "ROS"）。
    *   Fill the first row/column manually to show you understand the base case.
    *   手動填寫第一行/列，以表明你理解基本情況。
3.  **Verbalize the Recurrence (口述遞迴):**
    "If characters match, we inherit the diagonal. If not, we take the minimum of neighbors plus one."
    「如果字元匹配，我們繼承對角線。如果不匹配，我們取鄰居的最小值加一。」
4.  **Follow-up (追問):**
    *   **Interviewer:** "Can you improve space?"
    *   **You:** "Yes, since `dp[i][j]` only depends on row `i-1` and `i`, we can use two rows or even a single 1D array with a temporary variable for the diagonal."
    *   **面試官：** 「你能改善空間嗎？」
    *   **你：** 「可以，因為 `dp[i][j]` 只依賴於第 `i-1` 行和第 `i` 行，我們可以使用兩行，甚至使用帶有對角線臨時變數的一維陣列。」

---

## 7. Practice Problems (練習題)

### Easy: Unique Paths II (Grid with Obstacles)
**Hint:** Standard grid traversal. If `grid[i][j] == 1` (obstacle), then `dp[i][j] = 0`. Else `dp[i][j] = up + left`.
**提示：** 標準網格遍歷。若 `grid[i][j] == 1`（障礙），則 `dp[i][j] = 0`。否則 `dp[i][j] = 上 + 左`。

### Medium: Longest Common Subsequence (LCS)
**Hint:** Very similar to Edit Distance but without replacement/insertion costs. Just finding max length.
**提示：** 與編輯距離非常相似，但沒有替換/插入成本。只需找出最大長度。
**Core Logic:** `if match: diag + 1`, `else: max(up, left)`.
**核心邏輯：** `若匹配: 對角線 + 1`，`否則: max(上, 左)`。

### Advanced: Wildcard Matching (LC 44) or Regular Expression Matching (LC 10)
**Hint:** Handling `*` is the key. In Wildcard, `*` matches any sequence.
**提示：** 處理 `*` 是關鍵。在萬用字元中，`*` 匹配任何序列。
**Logic:** If `p[j-1] == '*'`, `dp[i][j] = dp[i][j-1]` (match empty) `|| dp[i-1][j]` (match one more char).
**邏輯：** 若 `p[j-1] == '*'`, `dp[i][j] = dp[i][j-1]`（匹配空） `|| dp[i-1][j]`（多匹配一個字元）。

---

## 8. Checklists (快速檢核表)

*   [ ] **State Definition:** Does `dp[i][j]` mean "ending at" or "range i to j"?
    **狀態定義：** `dp[i][j]` 是指「結束於」還是「範圍 i 到 j」？
*   [ ] **Base Cases:** Did I handle empty strings/arrays correctly? (Row 0/Col 0).
    **基本情況：** 我是否正確處理了空字串/陣列？（第 0 行/第 0 列）。
*   [ ] **Indices:** Am I accessing `string.charAt(i-1)` when using `dp[i]`?
    **索引：** 當使用 `dp[i]` 時，我是否存取了 `string.charAt(i-1)`？
*   [ ] **Optimization:** Did I mention space optimization ($O(N)$) even if I coded $O(N^2)$?
    **優化：** 即使我寫了 $O(N^2)$ 的代碼，我是否提到了空間優化 ($O(N)$)？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Pixel Filling" Analogy (像素填充類比)
Imagine 2D DP as rendering an image row by row. To determine the color of a pixel (current state), you only need to look at the pixels immediately above and to the left (past states).
將二維 DP 想像為逐行渲染圖像。要確定一個像素（當前狀態）的顏色，你只需要查看緊鄰上方和左側的像素（過去的狀態）。

### The "Forgetful Traveler" (健忘的旅人 - Space Optimization)
When optimizing space, imagine a traveler who only remembers the previous day's journey. Once row `i` is calculated, row `i-1` is forgotten forever.
在優化空間時，想像一個健忘的旅人，他只記得前一天的旅程。一旦計算出第 `i` 行，第 `i-1` 行就會被永遠遺忘。