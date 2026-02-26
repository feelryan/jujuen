# Advanced 2-D Dynamic Programming Interview Guide
# 進階二維動態規劃面試實戰指南

## 1. Learning Objectives（學習目標）

*   **Master State Definition & Transition:** Move beyond basic grid problems to complex state definitions involving strings, subsequences, and intervals.
    **掌握狀態定義與轉移：** 超越基礎網格問題，掌握涉及字串、子序列與區間的複雜狀態定義。
*   **Space Optimization Techniques:** Confidently optimize space complexity from $O(M \times N)$ to $O(N)$ (Rolling Array) in real-time.
    **空間優化技巧：** 有自信地即時將空間複雜度從 $O(M \times N)$ 優化至 $O(N)$（滾動數組）。
*   **Disambiguate DP Patterns:** Distinguish between Sequence Alignment, Knapsack variations, and Interval DP.
    **釐清 DP 模式：** 區分序列對齊（Sequence Alignment）、背包變體（Knapsack）與區間 DP（Interval DP）。
*   **Handle Complex Initialization:** Correctly handle boundary conditions (padding) to avoid "off-by-one" errors.
    **處理複雜初始化：** 正確處理邊界條件（填充），避免「差一錯誤（off-by-one errors）」。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
2-D DP is used when the optimal solution depends on two independent variables (e.g., indices in two strings, or index + resource capacity).
二維 DP 適用於最佳解取決於兩個獨立變數的情況（例如：兩個字串的索引，或索引 + 資源容量）。

Visually, think of filling a table where cell `(i, j)` represents the solution to the subproblem considering the first `i` elements of input A and first `j` elements of input B.
視覺上，想像填寫一張表格，其中單元格 `(i, j)` 代表考慮輸入 A 的前 `i` 個元素與輸入 B 的前 `j` 個元素時的子問題解。

### Complexity（複雜度）
*   **Time:** Typically $O(M \times N)$, where M and N are the dimensions of the inputs.
    **時間：** 通常為 $O(M \times N)$，其中 M 和 N 是輸入的維度。
*   **Space:** Naively $O(M \times N)$, optimizable to $O(\min(M, N))$.
    **空間：** 樸素解法為 $O(M \times N)$，可優化至 $O(\min(M, N))$。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** You need the min/max/count of ways involving two sequences, or a grid with path dependencies.
    **適用：** 需要計算涉及兩個序列的極值/計數，或具有路徑依賴的網格問題。
*   **Do NOT use when:** The problem can be solved greedily (e.g., simple interval scheduling) or requires permutations where order matters significantly (often backtracking).
    **不適用：** 問題可用貪婪演算法解決（如簡單區間調度），或涉及順序極為重要的排列問題（通常是回溯法）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Sequence Alignment (Dual Sequence) / 序列對齊（雙序列）
*   **Scenario:** Compare two strings/arrays (e.g., LCS, Edit Distance).
    **場景：** 比較兩個字串/陣列（如最長公共子序列、編輯距離）。
*   **State:** `dp[i][j]` = result for `s1[0...i]` and `s2[0...j]`.
    **狀態：** `dp[i][j]` = `s1[0...i]` 與 `s2[0...j]` 的結果。

### B. Grid with Obstacles or States / 帶障礙或狀態的網格
*   **Scenario:** Robot moving from top-left to bottom-right with constraints.
    **場景：** 機器人從左上移動到右下，並帶有約束條件。
*   **State:** `dp[i][j]` = min path/ways to reach cell `(i, j)`.
    **狀態：** `dp[i][j]` = 到達單元格 `(i, j)` 的最短路徑/方法數。

### C. Interval DP / 區間 DP
*   **Scenario:** Operations on subarrays where merging depends on boundaries (e.g., Burst Balloons, Palindromic Substrings).
    **場景：** 對子陣列進行操作，合併取決於邊界（如戳氣球、回文子字串）。
*   **State:** `dp[i][j]` = best result for subarray from index `i` to `j`.
    **狀態：** `dp[i][j]` = 索引 `i` 到 `j` 的子陣列之最佳結果。
    *   *Note: Iteration order is usually by length of the interval.*
    *   *註：迭代順序通常依據區間長度。*

---

## 4. Example Walkthrough（範例講解）

### Problem: Edit Distance (Levenshtein Distance)
### 問題：編輯距離

**Problem Statement:**
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.
You have the following three operations permitted on a word: Insert, Delete, Replace.
給定兩個字串 `word1` 與 `word2`，返回將 `word1` 轉換為 `word2` 所需的最少操作次數。
你可以對一個單字進行以下三種操作：插入、刪除、替換。

---

### Phase 1: Brute Force (Recursive) / 暴力解（遞迴）

**Idea:** Compare the last characters. If equal, recurse on `(i-1, j-1)`. If not, try all 3 operations and take the minimum + 1.
**思路：** 比較最後一個字元。若相等，遞迴 `(i-1, j-1)`。若不等，嘗試所有 3 種操作並取最小值 + 1。

*   **Insert:** Recurse `(i, j-1)`
*   **Delete:** Recurse `(i-1, j)`
*   **Replace:** Recurse `(i-1, j-1)`

**Why it fails:** Exponential time complexity $O(3^{M+N})$ due to overlapping subproblems.
**為何失敗：** 由於重疊子問題，時間複雜度呈指數級 $O(3^{M+N})$。

---

### Phase 2: Optimized 2-D DP / 優化二維 DP

**State Definition:** `dp[i][j]` represents the edit distance between `word1[0...i-1]` and `word2[0...j-1]`.
**狀態定義：** `dp[i][j]` 代表 `word1[0...i-1]` 與 `word2[0...j-1]` 之間的編輯距離。

**Padding:** We use size `(M+1) x (N+1)` to handle empty strings easily.
**填充：** 我們使用 `(M+1) x (N+1)` 的大小來輕鬆處理空字串。

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        
        # Initialize DP table with 0
        # 初始化 DP 表格為 0
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Base cases: transforming empty string to non-empty requires insertions
        # 基本情況：將空字串轉換為非空字串需要插入操作
        for i in range(m + 1):
            dp[i][0] = i  # Deleting all characters from word1 / 刪除 word1 所有字元
        for j in range(n + 1):
            dp[0][j] = j  # Inserting all characters from word2 / 插入 word2 所有字元
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # If characters match, no new operation needed
                # 若字元匹配，無需新操作
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Take min of: Replace, Delete, Insert
                    # 取 替換、刪除、插入 的最小值
                    dp[i][j] = 1 + min(
                        dp[i - 1][j - 1], # Replace (替換)
                        dp[i - 1][j],     # Delete (刪除)
                        dp[i][j - 1]      # Insert (插入)
                    )
        
        return dp[m][n]
```

**Complexity:**
*   Time: $O(M \times N)$
*   Space: $O(M \times N)$

---

### Phase 3: Space Optimization (Rolling Array) / 空間優化（滾動數組）

**Observation:** To calculate `dp[i][j]`, we only need the current row `i` and the previous row `i-1`.
**觀察：** 計算 `dp[i][j]` 時，我們只需要當前行 `i` 與上一行 `i-1`。

**Refinement:** We can reduce space to $O(\min(M, N))$.
**精進：** 我們可以將空間減少至 $O(\min(M, N))$。

```python
class Solution:
    def minDistanceOptimized(self, word1: str, word2: str) -> int:
        # Ensure word2 is the shorter one to minimize space
        # 確保 word2 是較短的字串以最小化空間
        if len(word1) < len(word2):
            return self.minDistanceOptimized(word2, word1)
            
        m, n = len(word1), len(word2)
        
        # Previous row (representing dp[i-1])
        # 上一行（代表 dp[i-1]）
        prev = [j for j in range(n + 1)]
        
        # Current row (representing dp[i])
        # 當前行（代表 dp[i]）
        curr = [0] * (n + 1)
        
        for i in range(1, m + 1):
            curr[0] = i # Base case for current row (transforming word1[:i] to empty)
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    curr[j] = prev[j - 1]
                else:
                    curr[j] = 1 + min(prev[j - 1], prev[j], curr[j - 1])
            
            # Move current row to previous for next iteration
            # 將當前行移至上一行，供下一次迭代使用
            # Using slice assignment or list() to copy is safer than reference assignment
            # 使用切片賦值或 list() 複製比引用賦值更安全
            prev = list(curr)
            
        return prev[n]
```

**Complexity:**
*   Time: $O(M \times N)$
*   Space: $O(\min(M, N))$

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake | Correct Approach |
| :--- | :--- | :--- |
| **Index Alignment** | Accessing `word[i]` inside the loop when DP is 1-indexed. <br> 在 DP 為 1-based 索引時，迴圈內直接存取 `word[i]`。 | Use `word[i-1]` to match the 1-based DP table logic. <br> 使用 `word[i-1]` 來對應 1-based 的 DP 表邏輯。 |
| **Initialization** | Initializing grid with `0` when searching for `min`. <br> 尋找最小值時將網格初始化為 `0`。 | Initialize with `float('inf')` or a sufficiently large number. <br> 初始化為 `float('inf')` 或足夠大的數字。 |
| **Subarray vs Subsequence** | Confusing continuous (subarray) with non-continuous (subsequence). <br> 混淆連續（子陣列）與非連續（子序列）。 | Subarray usually resets if condition breaks; Subsequence carries over previous max. <br> 子陣列通常在條件中斷時重置；子序列則繼承之前的最大值。 |
| **Space Optimization** | Overwriting `dp[j]` (prev) with new value before using it for `dp[j+1]`. <br> 在計算 `dp[j+1]` 需使用舊值前，就覆蓋了 `dp[j]`。 | Use a temporary variable `temp` to store `dp[i-1][j-1]` (diagonal) in 1-D array optimization. <br> 在一維陣列優化中，使用臨時變數 `temp` 儲存 `dp[i-1][j-1]`（對角線值）。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Define the State clearly:** "I will define `dp[i][j]` as the minimum cost to..."
    **清晰定義狀態：** 「我將定義 `dp[i][j]` 為...的最小成本。」
2.  **Establish Base Cases:** "For the 0-th row/column, it represents empty strings, so the values should be..."
    **確立基本情況：** 「對於第 0 行/列，它代表空字串，因此數值應為...」
3.  **Explain Transitions:** "If characters match, we inherit the diagonal. If not, we consider three possibilities..."
    **解釋轉移方程：** 「若字元匹配，我們繼承對角線的值。若不匹配，我們考慮三種可能性...」
4.  **Discuss Optimization:** "The naive space is $O(N^2)$, but since we only look back one row, we can optimize to $O(N)$."
    **討論優化：** 「樸素空間是 $O(N^2)$，但因為我們只回顧一行，可以優化至 $O(N)$。」

### Whiteboard Strategy（白板策略）
*   Draw a small 2D matrix (e.g., 3x3 or 4x4) for a simple example (e.g., "horse" to "ros").
*   Fill the first row/column manually to show you understand initialization.
*   Write the recurrence relation ($DP[i][j] = \dots$) *before* writing code.
*   畫一個小的二維矩陣（如 3x3 或 4x4）作為簡單範例（例如 "horse" 到 "ros"）。
*   手動填寫第一行/列，表明你理解初始化。
*   在寫程式碼 *之前*，先寫下遞迴關係式（$DP[i][j] = \dots$）。

### Common Follow-ups（常見追問）
*   "Can you reconstruct the path/operations?" (Requires storing parent pointers or backtracking the DP table).
    「你能重建路徑/操作步驟嗎？」（需要儲存父指標或回溯 DP 表）。
*   "What if the costs for insert/delete/replace are different?"
    「如果插入/刪除/替換的成本不同怎麼辦？」

---

## 7. Practice Problems（練習題）

### Easy: Unique Paths II (Grid with Obstacles)
**Hint:** Standard grid DP. If `grid[i][j]` is an obstacle, `dp[i][j] = 0`.
**提示：** 標準網格 DP。若 `grid[i][j]` 是障礙物，`dp[i][j] = 0`。

### Medium: Longest Common Subsequence (LCS)
**Hint:** Very similar to Edit Distance but only "Match" or "Skip". No replace/insert cost logic.
**提示：** 與編輯距離非常相似，但只有「匹配」或「跳過」。沒有替換/插入的成本邏輯。
*   *Key Transition:* `if s1[i] == s2[j]: 1 + diag` else `max(up, left)`.

### Hard: Regular Expression Matching (LC 10)
**Problem:** Implement regex support for `.` and `*`.
**問題：** 實作支援 `.` 和 `*` 的正則表達式。
**Hint:** The `*` is the tricky part. It can match zero elements of the preceding char (look at `dp[i][j-2]`) or one/more elements (check match & look at `dp[i-1][j]`).
**提示：** `*` 是棘手的部分。它可以匹配前一個字元的零個元素（看 `dp[i][j-2]`）或一個/多個元素（檢查匹配並看 `dp[i-1][j]`）。

---

## 8. Rapid Checklists（快速檢核表）

*   [ ] **Dimensions:** Did I allocate `(m + 1) * (n + 1)` or `m * n`? Does it match my loop range?
    **維度：** 我分配了 `(m + 1) * (n + 1)` 還是 `m * n`？這與我的迴圈範圍相符嗎？
*   [ ] **Base Cases:** Are `dp[0][0]`, row 0, and col 0 correctly initialized?
    **基本情況：** `dp[0][0]`、第 0 行和第 0 列是否正確初始化？
*   [ ] **Indices:** Am I accessing `string[i-1]` inside the loop `for i in range(1, m+1)`?
    **索引：** 我是否在 `for i in range(1, m+1)` 迴圈中存取 `string[i-1]`？
*   [ ] **Return Value:** Am I returning `dp[m][n]` or something else?
    **返回值：** 我是返回 `dp[m][n]` 還是其他值？
*   [ ] **Space Opt:** If using 1-D array, did I handle the "diagonal" value (usually needed for replace/match) correctly using a temp variable?
    **空間優化：** 若使用一維陣列，我是否正確使用臨時變數處理了「對角線」值（通常用於替換/匹配）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "DAG" Visualization（有向無環圖視覺化）
Imagine the DP table as a graph. Each cell `(i, j)` is a node.
想像 DP 表是一個圖。每個單元格 `(i, j)` 是一個節點。
*   **Edges:** Come from Top, Left, or Top-Left.
    **邊：** 來自上方、左方或左上方。
*   **Cost:** The weight of the edge depends on the operation (e.g., +1 for edit, +0 for match).
    **成本：** 邊的權重取決於操作（例如：編輯 +1，匹配 +0）。
*   **Goal:** Find Shortest Path (Min Cost) or Longest Path (LCS) from `(0,0)` to `(m,n)`.
    **目標：** 尋找從 `(0,0)` 到 `(m,n)` 的最短路徑（最小成本）或最長路徑（LCS）。

### The "Photocopier" Analogy (Rolling Array)
### 「影印機」類比（滾動數組）
You don't need to keep all previous pages of a document to write the *current* page. You only need to glance at the **previous line** you just wrote.
你不需要保留文件的所有舊頁面來書寫*當前*頁面。你只需要瞄一眼你剛剛寫完的**上一行**。
*   **2-D Array:** Keeping the whole book open.
    **二維陣列：** 保持整本書打開。
*   **Rolling Array:** Using a ruler to cover everything except the line above.
    **滾動數組：** 用尺遮住除上一行以外的所有內容。