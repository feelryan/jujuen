# 2-D Dynamic Programming (Advanced)
# 二維動態規劃（進階）

## 1. Learning Objectives (學習目標)

1.  **Master State Definition in Higher Dimensions:** Move beyond simple 1-D arrays to model problems requiring two variables (e.g., two string indices, grid coordinates, or interval boundaries).
    **掌握高維度的狀態定義：** 超越簡單的一維陣列，學會對需要兩個變數（例如兩個字串索引、網格座標或區間邊界）的問題進行建模。

2.  **Derive Complex Transition Equations:** Learn to identify relationships between $dp[i][j]$ and its neighbors ($dp[i-1][j]$, $dp[i][j-1]$, $dp[i-1][j-1]$) or sub-intervals ($dp[i][k] + dp[k][j]$).
    **推導複雜的轉移方程式：** 學習識別 $dp[i][j]$ 與其鄰居（$dp[i-1][j]$、$dp[i][j-1]$、$dp[i-1][j-1]$）或子區間（$dp[i][k] + dp[k][j]$）之間的關係。

3.  **Space Optimization (Rolling Array):** For Senior roles, optimizing space from $O(M \times N)$ to $O(min(M, N))$ is often a required follow-up.
    **空間優化（滾動陣列）：** 對於資深職位，將空間複雜度從 $O(M \times N)$ 優化至 $O(min(M, N))$ 通常是必考的後續問題。

4.  **Distinguish Patterns:** Quickly differentiate between "Grid DP," "Dual Sequence DP," and "Interval DP."
    **區分題型模式：** 快速區分「網格 DP」、「雙序列 DP」與「區間 DP」。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
2-D DP involves populating a two-dimensional table where each cell represents the solution to a subproblem defined by two parameters.
二維 DP 涉及填充一個二維表格，其中每個單元格代表由兩個參數定義的子問題的解。

### Intuition (直覺)
Think of it as filling a grid where the value of the current cell depends on decisions made in previous cells (usually top, left, or top-left).
將其想像為填充一個網格，當前單元格的值取決於先前單元格（通常是上方、左方或左上方）所做的決策。

### Complexity (複雜度)
-   **Time:** Typically $O(M \times N)$ or $O(N^2)$ for interval DP.
    **時間：** 通常為 $O(M \times N)$，若是區間 DP 則為 $O(N^2)$。
-   **Space:** Naively $O(M \times N)$, optimizable to $O(N)$ using a rolling array.
    **空間：** 樸素解法為 $O(M \times N)$，使用滾動陣列可優化至 $O(N)$。

### When to Use (適用場景)
-   **Grid Problems:** Finding paths, min sums in a matrix.
    **網格問題：** 在矩陣中尋找路徑或最小和。
-   **String Matching:** Edit distance, Longest Common Subsequence (LCS).
    **字串匹配：** 編輯距離、最長公共子序列 (LCS)。
-   **Interval Problems:** Merging stones, bursting balloons (matrix chain multiplication style).
    **區間問題：** 合併石子、戳氣球（矩陣鏈乘法類型）。

### When NOT to Use (不適用場景)
-   If the problem can be modeled as a graph shortest path (Dijkstra/BFS) with non-negative weights, DP might be overkill or slower if the state space is sparse.
    如果問題可以建模為非負權重的圖最短路徑（Dijkstra/BFS），且狀態空間稀疏，使用 DP 可能會過度設計或較慢。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Grid Traversal (網格遍歷)
-   **State:** $dp[i][j]$ = distinct paths or min cost to reach cell $(i, j)$.
    **狀態：** $dp[i][j]$ = 到達單元格 $(i, j)$ 的不同路徑數或最小成本。
-   **Transition:** $dp[i][j] = f(dp[i-1][j], dp[i][j-1])$.
    **轉移：** $dp[i][j] = f(dp[i-1][j], dp[i][j-1])$。

### Pattern B: Dual Sequence Alignment (雙序列對齊)
-   **State:** $dp[i][j]$ = result for the first $i$ chars of string A and first $j$ chars of string B.
    **狀態：** $dp[i][j]$ = 字串 A 的前 $i$ 個字元與字串 B 的前 $j$ 個字元的結果。
-   **Transition:** Depends on whether $A[i] == B[j]$.
    **轉移：** 取決於 $A[i]$ 是否等於 $B[j]$。

### Pattern C: Interval DP (區間 DP - Advanced)
-   **State:** $dp[i][j]$ = best result for the subarray/substring from index $i$ to $j$.
    **狀態：** $dp[i][j]$ = 索引 $i$ 到 $j$ 的子陣列/子字串的最佳結果。
-   **Transition:** Iterate a split point $k$ between $i$ and $j$.
    **轉移：** 在 $i$ 和 $j$ 之間迭代一個分割點 $k$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Edit Distance (編輯距離)
**Difficulty:** Hard (Classic)

#### Problem Statement (問題重述)
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.
給定兩個字串 `word1` 和 `word2`，返回將 `word1` 轉換為 `word2` 所需的最小操作數。
You have the following three operations permitted on a word: Insert, Delete, Replace.
你可以對一個單字進行以下三種操作：插入、刪除、替換。

#### Approach (思路)

1.  **Brute Force (Recursion):**
    Try all operations at every step. Complexity is exponential $O(3^{m+n})$.
    **暴力法（遞迴）：** 在每一步嘗試所有操作。複雜度是指數級 $O(3^{m+n})$。

2.  **DP Optimization (Tabulation):**
    Define $dp[i][j]$ as the edit distance between `word1[0...i-1]` and `word2[0...j-1]`.
    **DP 優化（列表法）：** 定義 $dp[i][j]$ 為 `word1[0...i-1]` 和 `word2[0...j-1]` 之間的編輯距離。
    -   If `word1[i-1] == word2[j-1]`: No op needed. $dp[i][j] = dp[i-1][j-1]$.
        如果 `word1[i-1] == word2[j-1]`：不需要操作。$dp[i][j] = dp[i-1][j-1]$。
    -   Else: Take min of Insert ($dp[i][j-1]$), Delete ($dp[i-1][j]$), Replace ($dp[i-1][j-1]$) + 1.
        否則：取 插入 ($dp[i][j-1]$)、刪除 ($dp[i-1][j]$)、替換 ($dp[i-1][j-1]$) 的最小值 + 1。

3.  **Space Optimization:**
    Notice we only need the previous row to calculate the current row.
    **空間優化：** 注意我們只需要前一行來計算當前行。

#### TypeScript Solution (Reference)

```typescript
/**
 * Calculates the Edit Distance (Levenshtein Distance) between two strings.
 * 計算兩個字串之間的編輯距離（Levenshtein Distance）。
 *
 * Time Complexity: O(m * n)
 * Space Complexity: O(m * n) - Can be optimized to O(min(m, n))
 */
function minDistance(word1: string, word2: string): number {
    const m = word1.length;
    const n = word2.length;

    // dp[i][j] represents min operations to convert word1[0..i-1] to word2[0..j-1]
    // dp[i][j] 代表將 word1[0..i-1] 轉換為 word2[0..j-1] 所需的最小操作數
    const dp: number[][] = Array.from({ length: m + 1 }, () => 
        new Array(n + 1).fill(0)
    );

    // Initialization: Converting empty string to word2 requires j insertions
    // 初始化：將空字串轉換為 word2 需要 j 次插入
    for (let j = 0; j <= n; j++) {
        dp[0][j] = j;
    }

    // Initialization: Converting word1 to empty string requires i deletions
    // 初始化：將 word1 轉換為空字串需要 i 次刪除
    for (let i = 0; i <= m; i++) {
        dp[i][0] = i;
    }

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            // Check if characters match (note 0-based index vs 1-based DP)
            // 檢查字元是否匹配（注意 0-based 索引與 1-based DP 的區別）
            if (word1[i - 1] === word2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                // 1. Replace (dp[i-1][j-1])
                // 2. Delete (dp[i-1][j]) -> word1 has extra char
                // 3. Insert (dp[i][j-1]) -> word1 needs char from word2
                dp[i][j] = Math.min(
                    dp[i - 1][j - 1], // Replace / 替換
                    dp[i - 1][j],     // Delete / 刪除
                    dp[i][j - 1]      // Insert / 插入
                ) + 1;
            }
        }
    }

    return dp[m][n];
}

// Space Optimized Version (Rolling Array)
// 空間優化版本（滾動陣列）
function minDistanceOptimized(word1: string, word2: string): number {
    const m = word1.length;
    const n = word2.length;
    
    // Ensure we use the smaller dimension for space
    // 確保我們使用較小的維度來節省空間
    if (n < m) return minDistanceOptimized(word2, word1);

    // prev represents dp[i-1], curr represents dp[i]
    // prev 代表 dp[i-1]，curr 代表 dp[i]
    let prev = Array.from({ length: n + 1 }, (_, j) => j);
    let curr = new Array(n + 1).fill(0);

    for (let i = 1; i <= m; i++) {
        curr[0] = i; // Base case for first column / 第一列的基礎情況
        for (let j = 1; j <= n; j++) {
            if (word1[i - 1] === word2[j - 1]) {
                curr[j] = prev[j - 1];
            } else {
                curr[j] = Math.min(
                    prev[j - 1], // Replace
                    prev[j],     // Delete (from word1 perspective)
                    curr[j - 1]  // Insert
                ) + 1;
            }
        }
        // Move current row to previous for next iteration
        // 將當前行移至前一行以進行下一次迭代
        prev = [...curr]; 
    }

    return prev[n];
}
```

#### Common Mistakes (錯誤示範)
-   **Wrong:** `dp[i][j] = Math.min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])` without adding `+1`.
    **錯誤：** 在取最小值時忘記 `+1`（操作成本）。
-   **Wrong:** Forgetting to initialize the base cases (converting empty string to non-empty).
    **錯誤：** 忘記初始化基礎情況（將空字串轉換為非空字串）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Padding (填充)** | **Pitfall:** Using `dp[m][n]` instead of `dp[m+1][n+1]`. <br> **Trap:** String indices are 0-based, but DP tables often use 1-based indexing to handle empty string cases conveniently. <br> **陷阱：** 使用 `dp[m][n]` 而非 `dp[m+1][n+1]`。字串索引是從 0 開始，但 DP 表格通常使用從 1 開始的索引以方便處理空字串情況。 |
| **Initialization (初始化)** | **Pitfall:** Initializing with `0` when finding Minimums. <br> **Correction:** Initialize with `Infinity` or a sufficiently large number, except for the start point. <br> **陷阱：** 在尋找最小值時初始化為 `0`。應初始化為 `Infinity` 或足夠大的數字，起點除外。 |
| **Subarray vs Subsequence** | **Confusion:** Subarray must be contiguous; Subsequence maintains order but not continuity. <br> **Impact:** DP transitions differ significantly (Subsequence usually looks at $i-1$, Subarray resets if continuity breaks). <br> **混淆：** 子陣列必須連續；子序列保持順序但不需連續。這會顯著影響 DP 轉移方程。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define the State clearly:** "I will define `dp[i][j]` as the minimum cost to..."
    **清晰定義狀態：** 「我將 `dp[i][j]` 定義為...的最小成本。」
2.  **Establish Base Cases:** "For the first row/column, the values should be..."
    **建立基礎情況：** 「對於第一列/行，數值應該是...」
3.  **Explain the Recurrence:** "To solve for $(i, j)$, we have three choices..."
    **解釋遞迴關係：** 「為了解決 $(i, j)$，我們有三個選擇...」
4.  **Discuss Trade-offs:** "The standard solution uses $O(MN)$ space, but since we only access the previous row, we can optimize to $O(N)$."
    **討論權衡：** 「標準解法使用 $O(MN)$ 空間，但因為我們只存取前一行，我們可以優化至 $O(N)$。」

### Whiteboard Strategy (白板策略)
-   Draw a small 2D grid (e.g., 3x3 or 4x4) for the example inputs.
    為範例輸入畫一個小的二維網格（例如 3x3 或 4x4）。
-   Fill in the initialization (0th row/col) first to show you handle edge cases.
    先填入初始化（第 0 行/列）以顯示你處理了邊界情況。
-   Manually compute one generic cell $(i, j)$ to verify your logic.
    手動計算一個一般單元格 $(i, j)$ 以驗證你的邏輯。

### Common Follow-up (常見追問)
-   "Can you reconstruct the path/solution, not just the minimum value?" (Requires storing parent pointers or backtracking the DP table).
    「你能重建路徑/解法，而不僅僅是最小值嗎？」（需要儲存父指標或回溯 DP 表格）。
-   "What if the matrix is too large for memory?" (Discuss Divide and Conquer or Hirschberg's algorithm for linear space LCS).
    「如果矩陣太大無法放入記憶體怎麼辦？」（討論分治法或用於線性空間 LCS 的 Hirschberg 演算法）。

---

## 7. Practice Problems (練習題)

### 1. Easy/Intermediate: Unique Paths II (Grid with Obstacles)
-   **Problem:** Find paths from top-left to bottom-right with obstacles.
    **問題：** 在有障礙物的情況下，尋找從左上角到右下角的路徑。
-   **Hint:** If `grid[i][j]` is obstacle, `dp[i][j] = 0`. Else `dp[i][j] = dp[i-1][j] + dp[i][j-1]`.
    **提示：** 若 `grid[i][j]` 是障礙物，`dp[i][j] = 0`。否則 `dp[i][j] = dp[i-1][j] + dp[i][j-1]`。

### 2. Intermediate: Longest Common Subsequence (LCS)
-   **Problem:** Find the length of the longest subsequence common to two strings.
    **問題：** 尋找兩個字串共有的最長子序列長度。
-   **Hint:** If match: `1 + dp[i-1][j-1]`. If not: `max(dp[i-1][j], dp[i][j-1])`.
    **提示：** 若匹配：`1 + dp[i-1][j-1]`。若不匹配：`max(dp[i-1][j], dp[i][j-1])`。

### 3. Advanced: Burst Balloons (Interval DP)
-   **Problem:** Given `n` balloons, burst them to maximize coins. Bursting `i` gives `nums[i-1] * nums[i] * nums[i+1]`.
    **問題：** 給定 `n` 個氣球，戳破它們以最大化金幣。戳破 `i` 獲得 `nums[i-1] * nums[i] * nums[i+1]`。
-   **Hint:** Define `dp[i][j]` as max coins for range $(i, j)$. Iterate `k` (last balloon to burst) between $i$ and $j$.
    **提示：** 定義 `dp[i][j]` 為區間 $(i, j)$ 的最大金幣數。在 $i$ 和 $j$ 之間迭代 `k`（作為該區間最後一個被戳破的氣球）。
    -   *Note:* This is "Reverse Thinking" (think about what happens last, not first).
    -   *註：* 這是「逆向思維」（思考最後發生什麼，而不是最先）。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **State Definition:** Does `dp[i][j]` clearly represent a subproblem?
    **狀態定義：** `dp[i][j]` 是否清晰地代表一個子問題？
-   [ ] **Grid Dimensions:** Did I allocate `M+1` x `N+1` to handle empty cases?
    **網格維度：** 我是否分配了 `M+1` x `N+1` 來處理空情況？
-   [ ] **Initialization:** Are the borders (row 0, col 0) set correctly?
    **初始化：** 邊界（第 0 行，第 0 列）是否設定正確？
-   [ ] **Transition:** Does the index `i` in DP map to `i-1` in the string/array?
    **轉移：** DP 中的索引 `i` 是否對應到字串/陣列中的 `i-1`？
-   [ ] **Optimization:** Did I mention or implement space optimization?
    **優化：** 我是否提到或實作了空間優化？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Wavefront" Analogy (波前類比)
Imagine the DP table as a beach. The solution starts at the top-left (the source of the wave) and propagates down-right. You cannot calculate a cell until the "wave" has reached its neighbors.
將 DP 表格想像成海灘。解法從左上角（波源）開始，向右下方傳播。在「波浪」到達鄰居之前，你無法計算當前單元格。

### The "Bucket Filling" (填桶子)
For `dp[i][j]`, imagine you are holding a bucket. You can only fill it by taking water from the buckets directly above, to the left, or diagonally up-left.
對於 `dp[i][j]`，想像你拿著一個桶子。你只能從正上方、左方或左上方的桶子裡取水來裝滿它。

### "Look Back, Not Forward" (向後看，別向前)
In DP, we don't say "Where do I go next?" (that's Greedy/DFS). We say "How did I get here?"
在 DP 中，我們不說「我接下來去哪裡？」（那是貪婪法/DFS）。我們說「我是怎麼到達這裡的？」