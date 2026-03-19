Here is the comprehensive guide for **2-D Dynamic Programming**, tailored for a Senior Software Engineer targeting Big Tech interviews.
這是針對 **二維動態規劃（2-D Dynamic Programming）** 的完整指南，專為目標鎖定 Big Tech 面試的資深軟體工程師量身打造。

---

# 2-D Dynamic Programming: Intermediate Guide
# 二維動態規劃：中階指南

## 1. Learning Objectives (學習目標)

1.  **Master State Definition**: Learn to define $dp[i][j]$ representing the optimal solution for a sub-grid or two prefixes.
    **掌握狀態定義**：學會定義 $dp[i][j]$ 來代表子網格或兩個前綴（prefixes）的最佳解。
2.  **Derive Transition Equations**: Understand how to derive the current cell's value from its neighbors (top, left, or top-left).
    **推導轉移方程**：理解如何從相鄰格子（上方、左方或左上方）推導出當前格子的值。
3.  **Space Optimization**: Move from $O(M \times N)$ space to $O(N)$ using the "Rolling Array" technique.
    **空間優化**：利用「滾動陣列（Rolling Array）」技巧，將空間複雜度從 $O(M \times N)$ 降至 $O(N)$。
4.  **Handle Initialization & Boundaries**: Correctly set up the first row and column to avoid index-out-of-bounds errors.
    **處理初始化與邊界**：正確設定第一列與第一行，以避免索引越界錯誤。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
2-D DP involves solving problems where the state depends on two variables, typically represented as a grid or a matrix.
二維動態規劃涉及解決狀態依賴於兩個變數的問題，通常以網格或矩陣表示。

It is most commonly used for grid traversal problems or comparing two sequences (strings/arrays).
它最常用於網格遍歷問題或比較兩個序列（字串/陣列）。

### Intuition (直覺)
Imagine filling out a spreadsheet where each cell's value is calculated based on the values of the cells directly above or to the left of it.
想像正在填寫一張電子表格，其中每個儲存格的值是根據其正上方或左方儲存格的值計算出來的。

### Complexity (複雜度)
-   **Time**: $O(M \times N)$, where $M$ and $N$ are the dimensions of the grid or lengths of sequences.
    **時間**：$O(M \times N)$，其中 $M$ 和 $N$ 是網格的維度或序列的長度。
-   **Space**: Standard is $O(M \times N)$, optimized is $O(\min(M, N))$.
    **空間**：標準為 $O(M \times N)$，優化後為 $O(\min(M, N))$。

### When to Use (適用場景)
-   **Optimization**: Finding minimum path sum, maximum square area.
    **最佳化**：尋找最小路徑和、最大正方形面積。
-   **Sequence Alignment**: Longest Common Subsequence, Edit Distance.
    **序列比對**：最長公共子序列、編輯距離。
-   **Counting**: Number of unique paths.
    **計數**：唯一路徑的數量。

### When NOT to Use (不適用場景)
-   **Cyclic Dependencies**: If state $(i, j)$ depends on $(i+1, j)$, standard iteration won't work (might need BFS/Dijkstra).
    **循環依賴**：如果狀態 $(i, j)$ 依賴於 $(i+1, j)$，標準迭代將無法運作（可能需要 BFS/Dijkstra）。
-   **Input Size too Large**: If $N > 10^4$, $O(N^2)$ will TLE (Time Limit Exceeded).
    **輸入規模過大**：如果 $N > 10^4$，則 $O(N^2)$ 會導致超時。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Grid Traversal (網格遍歷)
-   **Scenario**: Robot moves from top-left to bottom-right.
    **場景**：機器人從左上角移動到右下角。
-   **Transition**: $dp[i][j] = f(dp[i-1][j], dp[i][j-1])$.
    **轉移**：$dp[i][j] = f(dp[i-1][j], dp[i][j-1])$。

### B. Dual Sequence Alignment (雙序列比對)
-   **Scenario**: Comparing String A and String B (e.g., LCS, Edit Distance).
    **場景**：比較字串 A 和字串 B（例如：LCS、編輯距離）。
-   **Transition**: Often involves $dp[i-1][j-1]$ (diagonal) when characters match.
    **轉移**：當字元匹配時，通常涉及 $dp[i-1][j-1]$（對角線）。

### C. Matrix Properties (矩陣屬性)
-   **Scenario**: Finding the largest square/rectangle of 1s in a binary matrix.
    **場景**：在二進位矩陣中尋找由 1 組成的最大正方形/矩形。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Common Subsequence (LCS)
**問題：最長公共子序列**

Given two strings `text1` and `text2`, return the length of their longest common subsequence.
給定兩個字串 `text1` 和 `text2`，返回它們最長公共子序列的長度。

*(Note: A subsequence is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.)*
*（註：子序列是從原始字串中刪除某些字元（可以是零個）後產生的新字串，且不改變剩餘字元的相對順序。）*

### Approach (思路)

#### 1. Brute Force (暴力法)
Generate all subsequences of `text1` and check if they exist in `text2`.
生成 `text1` 的所有子序列，並檢查它們是否存在於 `text2` 中。
-   **Complexity**: $O(2^N \times M)$. This is exponential and unacceptable.
    **複雜度**：$O(2^N \times M)$。這是指數級的，無法接受。

#### 2. Dynamic Programming (動態規劃)
Define $dp[i][j]$ as the length of the LCS of `text1[0...i-1]` and `text2[0...j-1]`.
定義 $dp[i][j]$ 為 `text1[0...i-1]` 和 `text2[0...j-1]` 的 LCS 長度。

**Logic (邏輯)**:
-   If `text1[i] == text2[j]`: We found a match! Add 1 to the result of the previous prefixes (diagonal).
    如果 `text1[i] == text2[j]`：我們找到了一個匹配！在之前的結果（對角線）上加 1。
    $$dp[i][j] = 1 + dp[i-1][j-1]$$
-   If `text1[i] != text2[j]`: We cannot match these two. The answer is the max of ignoring the current char of `text1` OR ignoring the current char of `text2`.
    如果 `text1[i] != text2[j]`：我們無法匹配這兩個。答案是「忽略 `text1` 當前字元」或「忽略 `text2` 當前字元」兩者中的最大值。
    $$dp[i][j] = \max(dp[i-1][j], dp[i][j-1])$$

#### 3. Space Optimization (空間優化)
Notice we only need the current row and the previous row. We can reduce space to $O(\min(M, N))$.
注意我們只需要當前列和上一列。我們可以將空間減少到 $O(\min(M, N))$。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

class Solution {
public:
    int longestCommonSubsequence(std::string text1, std::string text2) {
        int m = text1.length();
        int n = text2.length();

        // DP table initialization. 
        // dp[i][j] stores LCS length for text1[0...i-1] and text2[0...j-1].
        // Size is (m+1) x (n+1) to handle empty string base cases easily.
        // DP 表初始化。
        // dp[i][j] 儲存 text1[0...i-1] 和 text2[0...j-1] 的 LCS 長度。
        // 大小設為 (m+1) x (n+1) 以便輕鬆處理空字串的基礎情況。
        std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));

        for (int i = 1; i <= m; ++i) {
            for (int j = 1; j <= n; ++j) {
                // Check if characters match. Note: string indices are 0-based.
                // 檢查字元是否匹配。注意：字串索引是從 0 開始的。
                if (text1[i - 1] == text2[j - 1]) {
                    // Match found: extend the result from the diagonal (both prefixes shorter).
                    // 發現匹配：從對角線（兩個前綴都較短的情況）延伸結果。
                    dp[i][j] = 1 + dp[i - 1][j - 1];
                } else {
                    // No match: take the best result by excluding current char from either string.
                    // 無匹配：通過排除任一字串的當前字元來取最佳結果。
                    dp[i][j] = std::max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        return dp[m][n];
    }
};
```

### Common Mistake in this Problem (此題常見錯誤)
-   **Index Mismatch**: Accessing `text1[i]` inside the loop when `i` goes from 1 to `m`. It should be `text1[i-1]`.
    **索引不匹配**：當 `i` 從 1 到 `m` 時，在迴圈內存取 `text1[i]`。應該是 `text1[i-1]`。
-   **Why it's wrong**: The DP table is 1-indexed (padding for base case), but strings are 0-indexed.
    **為何錯誤**：DP 表是 1-based 索引（為了基礎情況的填充），但字串是 0-based 索引。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Subsequence (子序列)** | **Substring (子字串)** | Subsequence can be discontinuous; Substring must be continuous. DP transitions differ significantly. <br> 子序列可以是不連續的；子字串必須是連續的。DP 轉移方程有顯著差異。 |
| **0-based DP Table** | **1-based DP Table** | 1-based (size $N+1$) is usually preferred to handle "empty" base cases without `if (i==0)` checks inside loops. <br> 1-based（大小 $N+1$）通常較好，因為可以處理「空」基礎情況，而無需在迴圈內進行 `if (i==0)` 檢查。 |
| **$O(N^2)$ Space** | **$O(N)$ Space** | In interviews, start with $O(N^2)$ for clarity, then optimize to $O(N)$ (Rolling Array) if asked. <br> 面試時，為了清晰起見先寫 $O(N^2)$，如果被問到再優化至 $O(N)$（滾動陣列）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define the State**: "I will define $dp[i][j]$ as the [metric] for the first $i$ elements of A and first $j$ elements of B."
    **定義狀態**：「我將定義 $dp[i][j]$ 為 A 的前 $i$ 個元素和 B 的前 $j$ 個元素的 [指標]。」
2.  **Establish Base Cases**: "For the 0-th row/column, the value should be 0 (or 1/infinity) because..."
    **建立基礎情況**：「對於第 0 列/行，值應該是 0（或 1/無窮大），因為...」
3.  **Explain Transition**: "At each step, we have two choices..."
    **解釋轉移**：「在每一步，我們有兩個選擇...」

### Whiteboard Strategy (白板策略)
-   **Draw the Grid**: Draw a small $3 \times 3$ or $4 \times 4$ table. Fill the first row and column manually before coding.
    **畫出網格**：畫一個小的 $3 \times 3$ 或 $4 \times 4$ 表格。在寫程式碼之前手動填寫第一列和第一行。
-   **Visualize Dependencies**: Draw arrows pointing to cell $(i, j)$ from its dependencies (top, left, diagonal).
    **視覺化依賴關係**：畫箭頭從依賴項（上方、左方、對角線）指向單元格 $(i, j)$。

### Common Follow-ups (常見追問)
-   "Can you reduce the space complexity?" (Hint: Rolling Array)
    「你能降低空間複雜度嗎？」（提示：滾動陣列）
-   "What if we need to print the actual path/subsequence, not just the length?" (Hint: Backtrack from $dp[M][N]$).
    「如果我們需要印出實際的路徑/子序列，而不僅僅是長度呢？」（提示：從 $dp[M][N]$ 回溯）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Unique Paths (LeetCode 62)
-   **Problem**: Robot moves from top-left to bottom-right. How many unique paths?
    **問題**：機器人從左上角移動到右下角。有多少條唯一路徑？
-   **Hint**: $dp[i][j] = dp[i-1][j] + dp[i][j-1]$. Base case: First row/col are all 1.
    **提示**：$dp[i][j] = dp[i-1][j] + dp[i][j-1]$。基礎情況：第一列/行全為 1。

### 2. Medium: Edit Distance (LeetCode 72)
-   **Problem**: Min operations (insert, delete, replace) to convert word1 to word2.
    **問題**：將 word1 轉換為 word2 的最少操作次數（插入、刪除、替換）。
-   **Hint**:
    -   Match: $dp[i-1][j-1]$
    -   Replace: $1 + dp[i-1][j-1]$
    -   Insert/Delete: $1 + \min(dp[i][j-1], dp[i-1][j])$
    **提示**：
    -   匹配：$dp[i-1][j-1]$
    -   替換：$1 + dp[i-1][j-1]$
    -   插入/刪除：$1 + \min(dp[i][j-1], dp[i-1][j])$

### 3. Hard: Maximal Square (LeetCode 221)
-   **Problem**: Find the largest square containing only 1s in a binary matrix.
    **問題**：在二進位矩陣中找到僅包含 1 的最大正方形。
-   **Hint**: $dp[i][j]$ represents the side length of the max square ending at $(i, j)$.
    $$dp[i][j] = \min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1$$
    **提示**：$dp[i][j]$ 代表以 $(i, j)$ 結尾的最大正方形的邊長。
    $$dp[i][j] = \min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1$$

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **State Definition**: Does $dp[i][j]$ refer to index $i$ or length $i$? (Usually length is safer).
    **狀態定義**：$dp[i][j]$ 是指索引 $i$ 還是長度 $i$？（通常長度比較安全）。
-   [ ] **Dimensions**: Is the DP table size $(M+1) \times (N+1)$?
    **維度**：DP 表的大小是 $(M+1) \times (N+1)$ 嗎？
-   [ ] **Initialization**: Are the 0-th row and 0-th column initialized correctly (0, 1, or Infinity)?
    **初始化**：第 0 列和第 0 行是否正確初始化（0、1 或無窮大）？
-   [ ] **Return Value**: Are you returning $dp[M][N]$ or something else (like a max value found during iteration)?
    **返回值**：你是返回 $dp[M][N]$ 還是其他值（例如迭代過程中找到的最大值）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "L" Shape Dependency (「L」形依賴)
Visualize the dependency of cell $(i, j)$ as an inverted "L" shape covering its neighbors:
將單元格 $(i, j)$ 的依賴關係視覺化為覆蓋其鄰居的倒「L」形：
```
[i-1][j-1]  |  [i-1][j]
-----------------------
 [i][j-1]   |  [i][j]  <-- Current
```
-   **Grid Paths**: Look Top and Left.
    **網格路徑**：看上方和左方。
-   **String Matching**: Look Diagonal (Match) or Top/Left (Mismatch).
    **字串匹配**：看對角線（匹配）或上方/左方（不匹配）。

### The "Padding" Analogy (「填充」類比)
Think of the extra row and column (index 0) as the "margin" of a page. You can't write content there, but it defines the boundaries so you don't fall off the paper.
將額外的行和列（索引 0）想像成頁面的「邊距」。你不能在那裡寫內容，但它定義了邊界，讓你不至於寫出紙外。