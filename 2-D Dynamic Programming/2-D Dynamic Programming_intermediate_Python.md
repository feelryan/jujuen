# 2-D Dynamic Programming (Intermediate)
# 二維動態規劃（中階）

## 1. Learning Goals (學習目標)

1.  **Identify 2-D DP Characteristics**: Recognize when a problem requires a state defined by two variables (e.g., coordinates in a grid, indices in two strings).
    **識別二維 DP 特徵**：辨識何時問題需要由兩個變數定義的狀態（例如：網格中的座標、兩個字串中的索引）。

2.  **Master the "Dual Sequence" Pattern**: Deeply understand how to handle problems involving two strings or arrays (like LCS, Edit Distance).
    **掌握「雙序列」模式**：深入理解如何處理涉及兩個字串或陣列的問題（如最長公共子序列、編輯距離）。

3.  **Implement Space Optimization**: Learn to reduce space complexity from $O(M \times N)$ to $O(\min(M, N))$ using "Rolling Array".
    **實作空間優化**：學習使用「滾動陣列」將空間複雜度從 $O(M \times N)$ 降低至 $O(\min(M, N))$。

4.  **Debug Transition Equations**: Systematically derive and verify the recurrence relation $dp[i][j] = f(dp[i-1][j], dp[i][j-1], ...)$.
    **除錯狀態轉移方程**：系統性地推導並驗證遞迴關係式 $dp[i][j] = f(dp[i-1][j], dp[i][j-1], ...)$。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
2-D DP involves solving a problem where the optimal substructure depends on two independent dimensions.
二維 DP 涉及解決最佳子結構依賴於兩個獨立維度的問題。
Typically, the state $dp[i][j]$ represents the solution to a subproblem ending at index $i$ of input A and index $j$ of input B (or coordinate $(i, j)$).
通常，狀態 $dp[i][j]$ 代表輸入 A 的索引 $i$ 與輸入 B 的索引 $j$（或座標 $(i, j)$）處的子問題解。

### Intuition (直覺)
Imagine filling a spreadsheet cell by cell; the value of the current cell depends on the values of its neighbors (usually top, left, or top-left).
想像逐格填寫試算表；當前儲存格的值取決於其鄰居的值（通常是上方、左方或左上方）。

### Complexity (複雜度)
-   **Time**: $O(M \times N)$, where $M$ and $N$ are the lengths of the two dimensions.
    **時間**：$O(M \times N)$，其中 $M$ 和 $N$ 是兩個維度的長度。
-   **Space**: Naively $O(M \times N)$, optimizable to $O(N)$.
    **空間**：原始為 $O(M \times N)$，可優化至 $O(N)$。

### When to Use (適用場景)
-   **Grid Problems**: Finding paths, min/max sums in a matrix.
    **網格問題**：在矩陣中尋找路徑、最小/最大總和。
-   **String/Sequence Alignment**: Comparing two strings (LCS, Edit Distance, Regex Matching).
    **字串/序列對齊**：比較兩個字串（LCS、編輯距離、正則表達式匹配）。
-   **Game Theory**: Simple board games involving coordinates.
    **賽局理論**：涉及座標的簡單棋盤遊戲。

### When NOT to Use (不適用場景)
-   If the data can be modeled as a graph where cyclic dependencies exist (use Dijkstra or BFS).
    如果資料可以建模為存在循環依賴的圖（請使用 Dijkstra 或 BFS）。
-   If the state requires more than 2 variables (e.g., 3-D DP or Bitmask DP).
    如果狀態需要超過 2 個變數（例如 3-D DP 或位元遮罩 DP）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Grid Traversal (網格遍歷)
-   **Scenario**: Robot moving from top-left to bottom-right.
    **場景**：機器人從左上角移動到右下角。
-   **Transition**: $dp[i][j] = dp[i-1][j] + dp[i][j-1]$.
    **轉移**：$dp[i][j] = dp[i-1][j] + dp[i][j-1]$。

### B. Dual Sequence Alignment (雙序列對齊)
-   **Scenario**: Matching characters between String A and String B.
    **場景**：在字串 A 和字串 B 之間匹配字元。
-   **Transition**:
    If $A[i] == B[j]$: Look at diagonal ($dp[i-1][j-1]$).
    If $A[i] \neq B[j]$: Look at top ($dp[i-1][j]$) or left ($dp[i][j-1]$).
    **轉移**：
    若 $A[i] == B[j]$：看對角線 ($dp[i-1][j-1]$)。
    若 $A[i] \neq B[j]$：看上方 ($dp[i-1][j]$) 或左方 ($dp[i][j-1]$)。

### C. Interval DP (區間 DP - Simplified)
-   **Scenario**: Palindrome check or matrix multiplication optimization.
    **場景**：迴文檢查或矩陣乘法優化。
-   **State**: $dp[i][j]$ represents the result for the substring from index $i$ to $j$.
    **狀態**：$dp[i][j]$ 代表從索引 $i$ 到 $j$ 的子字串結果。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Common Subsequence (LCS)
### 問題：最長公共子序列

**Problem Statement (問題重述)**:
Given two strings `text1` and `text2`, return the length of their longest common subsequence.
給定兩個字串 `text1` 和 `text2`，返回它們最長公共子序列的長度。
A subsequence is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.
子序列是從原始字串中刪除某些字元（可以是零個）後生成的新字串，且不改變剩餘字元的相對順序。

**Input**: `text1 = "abcde"`, `text2 = "ace"`
**Output**: `3` ("ace")

---

### Thought Process (思路)

**1. Brute Force (暴力解)**
-   Generate all subsequences of `text1` ($2^N$) and check if they exist in `text2`.
    生成 `text1` 的所有子序列（$2^N$），並檢查它們是否存在於 `text2` 中。
-   **Complexity**: Exponential time. Unacceptable.
    **複雜度**：指數時間。不可接受。

**2. Dynamic Programming (Optimization)**
-   **State**: Let $dp[i][j]$ be the LCS length of `text1[0...i-1]` and `text2[0...j-1]`.
    **狀態**：設 $dp[i][j]$ 為 `text1[0...i-1]` 和 `text2[0...j-1]` 的 LCS 長度。
-   **Choice**: Compare characters `text1[i-1]` and `text2[j-1]`.
    **選擇**：比較字元 `text1[i-1]` 和 `text2[j-1]`。
-   **Transition**:
    -   Match: $1 + dp[i-1][j-1]$
    -   No Match: $\max(dp[i-1][j], dp[i][j-1])$
    **轉移**：
    -   匹配：$1 + dp[i-1][j-1]$
    -   不匹配：$\max(dp[i-1][j], dp[i][j-1])$

**3. Space Optimization (最佳解)**
-   Notice we only need the previous row ($i-1$) to calculate the current row ($i$). We can reduce space to $O(\min(N, M))$.
    注意我們只需要前一列（$i-1$）來計算當前列（$i$）。我們可以將空間減少到 $O(\min(N, M))$。

---

### Python Solution (參考解)

```python
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        
        # Space Optimization: Ensure text2 is the shorter string to minimize space
        # 空間優化：確保 text2 是較短的字串以最小化空間
        if m < n:
            return self.longestCommonSubsequence(text2, text1)
            
        # Initialize the previous row (representing row i-1)
        # 初始化前一列（代表第 i-1 列）
        # dp[j] will store the LCS length for text1[...current_i] and text2[...j]
        prev = [0] * (n + 1)
        
        # Iterate through text1 (rows)
        # 遍歷 text1（列）
        for i in range(1, m + 1):
            # Current row being calculated
            # 正在計算的當前列
            curr = [0] * (n + 1)
            
            # Iterate through text2 (columns)
            # 遍歷 text2（行）
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    # Characters match: take diagonal value + 1
                    # 字元匹配：取對角線值 + 1
                    curr[j] = 1 + prev[j - 1]
                else:
                    # No match: take max of top or left
                    # 不匹配：取上方或左方的最大值
                    # prev[j] is "top" (same col, prev row)
                    # curr[j-1] is "left" (prev col, same row)
                    curr[j] = max(prev[j], curr[j - 1])
            
            # Move current row to previous for the next iteration
            # 將當前列移至前一列，供下一次迭代使用
            prev = curr
            
        return prev[n]

# Time Complexity: O(M * N)
# Space Complexity: O(min(M, N))
```

### Common Mistake (錯誤示範)

```python
# Mistake: Initializing 2D array with shared references
# 錯誤：使用共享引用初始化二維陣列
dp = [[0] * n] * m 
# If you modify dp[0][0], dp[1][0] also changes because rows are references to the same object.
# 如果你修改 dp[0][0]，dp[1][0] 也會改變，因為各列是對同一個物件的引用。

# Correct way:
# 正確方式：
dp = [[0] * n for _ in range(m)]
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) |
| :--- | :--- |
| **Padding (Padding)** | Often we size the DP table as $(M+1) \times (N+1)$ to handle empty string base cases easily. <br> 我們通常將 DP 表設為 $(M+1) \times (N+1)$ 以便輕鬆處理空字串的基礎情況。 |
| **Initialization (初始化)** | For "Max" problems, initialize with 0 or $-\infty$. For "Min" problems, initialize with $\infty$. <br> 對於「最大值」問題，初始化為 0 或 $-\infty$。對於「最小值」問題，初始化為 $\infty$。 |
| **Subsequence vs Substring** | **Subsequence**: Non-contiguous (LCS). **Substring**: Contiguous. <br> **子序列**：不連續（LCS）。**子字串**：連續。 |
| **Rolling Array Direction** | When optimizing 1D Knapsack, we iterate backwards. For LCS (using 2 rows), we iterate forwards. <br> 優化一維背包問題時，我們反向迭代。對於 LCS（使用兩列），我們正向迭代。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Framework (口條框架)**:
    -   "This looks like a 2D DP problem because we are matching two sequences/navigating a grid."
        「這看起來像是一個二維 DP 問題，因為我們正在匹配兩個序列/遍歷一個網格。」
    -   "Let's define $dp[i][j]$ as..."
        「讓我們將 $dp[i][j]$ 定義為...」
    -   "The base case is when one string is empty..."
        「基礎情況是當其中一個字串為空時...」

2.  **Whiteboard Strategy (白板策略)**:
    -   Draw a small $3 \times 3$ grid. Fill it manually to show the interviewer you understand the recurrence.
        畫一個小的 $3 \times 3$ 網格。手動填寫它，向面試官展示你理解遞迴關係。
    -   Write the recurrence relation ($dp[i][j] = \dots$) *before* writing code.
        在寫程式碼*之前*先寫出遞迴關係式（$dp[i][j] = \dots$）。

3.  **Follow-up (常見追問)**:
    -   "Can you reconstruct the path/string?" (Requires storing pointers or backtracking the DP table).
        「你能重建路徑/字串嗎？」（需要儲存指標或回溯 DP 表）。
    -   "Can you optimize the space?" (Rolling array).
        「你能優化空間嗎？」（滾動陣列）。

---

## 7. Practice Problems (練習題)

### 1. Unique Paths II (Easy/Mid)
**Hint**: Grid with obstacles. If `grid[i][j] == 1`, then $dp[i][j] = 0$. Otherwise sum top and left.
**提示**：帶有障礙物的網格。如果 `grid[i][j] == 1`，則 $dp[i][j] = 0$。否則將上方和左方相加。
**Focus**: Boundary conditions and obstacle handling.
**重點**：邊界條件與障礙物處理。

### 2. Edit Distance (Mid)
**Hint**: Operations are Insert, Delete, Replace.
$dp[i][j] = 1 + \min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])$.
**提示**：操作有插入、刪除、替換。
$dp[i][j] = 1 + \min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])$。
**Focus**: Understanding what each neighbor represents (Delete vs Insert vs Replace).
**重點**：理解每個鄰居代表什麼（刪除 vs 插入 vs 替換）。

### 3. Maximal Square (Mid/Hard)
**Hint**: Find the largest square containing only 1s.
$dp[i][j] = \min(top, left, diag) + 1$ if `matrix[i][j] == '1'`.
**提示**：找出只包含 1 的最大正方形。
如果 `matrix[i][j] == '1'`，則 $dp[i][j] = \min(top, left, diag) + 1$。
**Focus**: Geometric intuition in DP.
**重點**：DP 中的幾何直覺。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **State Definition**: Does $dp[i][j]$ mean "ending at" or "best within range"?
    **狀態定義**：$dp[i][j]$ 是指「結束於」還是「範圍內的最佳解」？
-   [ ] **Dimensions**: Did I allocate $N+1$ or $N$? (Usually $N+1$ for empty base case).
    **維度**：我分配了 $N+1$ 還是 $N$？（通常為 $N+1$ 以處理空基礎情況）。
-   [ ] **Indices**: Am I accessing `string[i-1]` when filling `dp[i]`?
    **索引**：填寫 `dp[i]` 時，我是否在存取 `string[i-1]`？
-   [ ] **Return Value**: Is the answer in $dp[M][N]$ or the max of the whole table?
    **回傳值**：答案是在 $dp[M][N]$ 還是在整個表的最大值？

---

## 9. Memory Anchors (記憶錨點)

### The "Three Neighbors" Rule (三鄰居法則)
For most 2D DP problems involving two sequences, you only care about three cells relative to $(i, j)$:
對於大多數涉及雙序列的二維 DP 問題，你只關心相對於 $(i, j)$ 的三個儲存格：

1.  **Top** ($i-1, j$): Usually means "Delete from A" or "Skip A".
    **上方** ($i-1, j$)：通常意味著「從 A 刪除」或「跳過 A」。
2.  **Left** ($i, j-1$): Usually means "Delete from B" or "Insert into A".
    **左方** ($i, j-1$)：通常意味著「從 B 刪除」或「插入 A」。
3.  **Top-Left** ($i-1, j-1$): Usually means "Match/Replace" or "Extend".
    **左上方** ($i-1, j-1$)：通常意味著「匹配/替換」或「延伸」。

### Visual Analogy (圖像類比)
Think of 2D DP as a **Wavefront**.
將二維 DP 視為一個 **波前（Wavefront）**。
The calculation propagates from the top-left corner to the bottom-right corner, like a wave moving across a pool.
計算從左上角傳播到右下角，就像波浪穿過水池一樣。