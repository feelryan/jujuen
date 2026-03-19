Here is the comprehensive guide for **1-D Dynamic Programming** at an **Advanced** level, tailored for a Senior Software Engineer.

這是一份針對 **一維動態規劃（1-D Dynamic Programming）** 的 **進階（Advanced）** 完整教材，專為資深軟體工程師量身打造。

---

# 1-D Dynamic Programming: Advanced Interview Guide
# 一維動態規劃：進階面試指南

## 1. Learning Objectives (學習目標)

*   **Master State Definition & Transition:** Move beyond simple recurrence; learn to define states that capture constraints (e.g., "max ending here") and handle multiple simultaneous states.
    **掌握狀態定義與轉移：** 超越簡單的遞迴，學習定義能捕捉限制條件的狀態（如「以此結尾的最大值」）並處理多個同時存在的狀態。
*   **Optimize Space Complexity:** Systematically reduce space from $O(N)$ to $O(1)$ using "rolling variables."
    **優化空間複雜度：** 系統性地使用「滾動變數」將空間從 $O(N)$ 降低至 $O(1)$。
*   **Identify "Hidden" DP:** Recognize problems that look like array manipulation or greedy problems but require DP guarantees.
    **識別「隱藏」的 DP：** 辨識那些看似陣列操作或貪婪演算法，但實際上需要 DP 保證的問題。
*   **Handle Edge Cases & Initialization:** Deal with empty inputs, single elements, and initialization values (e.g., `Integer.MIN_VALUE` vs `0`) flawlessly.
    **處理邊界條件與初始化：** 完美處理空輸入、單一元素以及初始值設定（例如 `Integer.MIN_VALUE` 與 `0` 的區別）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
1-D DP is an optimization technique where we solve a problem by solving subproblems indexed by a linear integer $i$, typically representing an index in an input array.
一維 DP 是一種優化技術，我們透過解決由線性整數 $i$ 索引的子問題（通常代表輸入陣列中的索引）來解決原問題。

### Intuition (直覺)
"History matters, but only the recent history."
「歷史很重要，但只有『最近』的歷史才重要。」

At index $i$, the optimal solution depends only on the optimal solutions at $i-1$, $i-2$, etc., not on the entire raw history.
在索引 $i$ 的最佳解僅取決於 $i-1$、$i-2$ 等處的最佳解，而非整個原始歷史。

### Complexity (複雜度)
*   **Time:** Typically $O(N)$. We visit each state once.
    **時間：** 通常為 $O(N)$。我們訪問每個狀態一次。
*   **Space:** Naively $O(N)$ (table), optimized to $O(1)$ (rolling variables) or $O(K)$ (window).
    **空間：** 樸素做法為 $O(N)$（表格），優化後可達 $O(1)$（滾動變數）或 $O(K)$（視窗大小）。

### When to Use / Not Use (適用與不適用場景)
*   **Use when:** Problem asks for Maximum/Minimum, Count distinct ways, or Existence (True/False), and the decision at $i$ depends on previous decisions.
    **適用時機：** 問題詢問最大/最小值、計算不同方法數、或存在性（真/假），且在 $i$ 的決策取決於先前的決策。
*   **Do NOT use when:** The problem requires generating *all* permutations/subsets (use Backtracking), or if the array can be reordered (sort + greedy might apply).
    **不適用時機：** 問題要求生成「所有」排列/子集（應使用回溯法），或者陣列可以重新排序（排序 + 貪婪演算法可能適用）。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, simple "Climbing Stairs" is insufficient. Focus on these advanced patterns:
對於資深工程師，簡單的「爬樓梯」已不足夠。請專注於以下進階模式：

1.  **Multiple States per Step (多狀態/步驟):**
    *   Example: *Maximum Product Subarray*, *Buy/Sell Stock with Cooldown*.
    *   Concept: You need to track more than one value (e.g., `max_positive` and `min_negative`) at each index.
    *   概念：在每個索引處需要追蹤多個值（例如 `最大正值` 和 `最小負值`）。

2.  **Partition DP (分割型 DP):**
    *   Example: *Word Break*, *Decode Ways*.
    *   Concept: $dp[i]$ checks validity of substrings like $s[j...i]$ combined with $dp[j]$.
    *   概念：$dp[i]$ 檢查子字串如 $s[j...i]$ 與 $dp[j]$ 結合後的有效性。

3.  **Subsequence with Constraints (帶限制的子序列):**
    *   Example: *Longest Increasing Subsequence (LIS)*.
    *   Concept: $dp[i]$ depends on all $j < i$ where condition meets. Complexity often $O(N^2)$, optimizable to $O(N \log N)$.
    *   概念：$dp[i]$ 取決於所有滿足條件的 $j < i$。複雜度通常為 $O(N^2)$，可優化至 $O(N \log N)$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Product Subarray (LeetCode 152)
**問題：乘積最大子陣列**

### Problem Statement (問題重述)
Given an integer array `nums`, find a contiguous non-empty subarray within the array that has the largest product, and return the product.
給定一個整數陣列 `nums`，找出陣列中乘積最大的連續非空子陣列，並返回該乘積。

*Example:* `[2, 3, -2, 4]` $\rightarrow$ `6` (`[2, 3]`)
*Example:* `[-2, 0, -1]` $\rightarrow$ `0`

### Thought Process (思路)

#### 1. Brute Force (暴力法)
Iterate all pairs $(i, j)$, calculate product.
遍歷所有配對 $(i, j)$，計算乘積。
*   **Complexity:** $O(N^2)$ Time. Too slow.
*   **複雜度：** 時間 $O(N^2)$。太慢。

#### 2. Naive DP Attempt (樸素 DP 嘗試)
Let $dp[i]$ be the max product ending at index $i$.
設 $dp[i]$ 為以索引 $i$ 結尾的最大乘積。
*   Transition: $dp[i] = \max(nums[i], nums[i] \times dp[i-1])$?
*   **Failure:** This fails with negative numbers. If $nums[i]$ is negative, multiplying it by a large positive previous product makes it a large negative (bad). But multiplying it by a large *negative* previous product makes it a large positive (good).
*   **失敗點：** 這在負數時會失效。如果 $nums[i]$ 是負數，乘以一個大的正數會變成大的負數（不好）。但乘以一個大的「負數」會變成大的正數（好）。

#### 3. Advanced DP (Optimal) (進階 DP - 最佳解)
We need to track **two** states at each step: the **max** product so far and the **min** product so far.
我們需要在每一步追蹤 **兩個** 狀態：目前的 **最大** 乘積與目前的 **最小** 乘積。

*   `maxDP[i]`: Max product ending at $i$.
*   `minDP[i]`: Min product ending at $i$ (waiting for a negative number to flip it to max).
*   `maxDP[i]`：以 $i$ 結尾的最大乘積。
*   `minDP[i]`：以 $i$ 結尾的最小乘積（等待一個負數將其翻轉為最大值）。

### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int maxProduct(int[] nums) {
        // Edge case: empty array
        // 邊界條件：空陣列
        if (nums == null || nums.length == 0) return 0;

        // Initialize current max/min and global result with the first element
        // 使用第一個元素初始化當前最大值/最小值與全域結果
        int currentMax = nums[0];
        int currentMin = nums[0];
        int result = nums[0];

        // Iterate starting from the second element
        // 從第二個元素開始遍歷
        for (int i = 1; i < nums.length; i++) {
            int num = nums[i];

            // Store currentMax temporarily because it will be updated
            // 暫存 currentMax，因為它即將被更新
            int tempMax = currentMax;

            // The new max is either:
            // 1. The number itself (starting a new subarray)
            // 2. num * previous max (positive * positive)
            // 3. num * previous min (negative * negative)
            // 新的最大值可能是：
            // 1. 數字本身（開始新的子陣列）
            // 2. 數字 * 前一個最大值（正 * 正）
            // 3. 數字 * 前一個最小值（負 * 負）
            currentMax = Math.max(num, Math.max(num * tempMax, num * currentMin));
            
            // Similarly update currentMin for future negative flips
            // 同樣更新 currentMin 以備未來的負數翻轉
            currentMin = Math.min(num, Math.min(num * tempMax, num * currentMin));

            // Update global result
            // 更新全域結果
            result = Math.max(result, currentMax);
        }

        return result;
    }
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ - Single pass.
    **時間：** $O(N)$ - 單次遍歷。
*   **Space:** $O(1)$ - Only used `currentMax`, `currentMin`, `result` variables.
    **空間：** $O(1)$ - 僅使用 `currentMax`, `currentMin`, `result` 變數。

### Error Demonstration (錯誤示範)

```java
// WRONG: Ignoring the negative number flipping effect
// 錯誤：忽略了負數翻轉的效應
for (int i = 1; i < nums.length; i++) {
    dp[i] = Math.max(nums[i], nums[i] * dp[i-1]); // Fails on [-2, 3, -4]
}
```
*   **Why it's wrong:** Input `[-2, 3, -4]`.
    *   Correct: $(-2 \times 3 \times -4) = 24$.
    *   This code: `dp` becomes `[-2, 3, -12]`, max is 3. It missed that `-4` could combine with the accumulated negative chain.
*   **為何錯：** 輸入 `[-2, 3, -4]`。
    *   正確解：$(-2 \times 3 \times -4) = 24$。
    *   此程式碼：`dp` 變成 `[-2, 3, -12]`，最大值為 3。它錯過了 `-4` 可以與累積的負數鏈結合的機會。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description (描述) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Subarray vs. Subsequence** | Subarray is contiguous; Subsequence preserves relative order but skips elements. <br> 子陣列是連續的；子序列保留相對順序但可跳過元素。 | Applying LIS ($O(N^2)$) logic to Maximum Subarray ($O(N)$) problems or vice versa. <br> 將 LIS 邏輯套用於最大子陣列問題，反之亦然。 |
| **Base Case Initialization** | Setting initial DP values. <br> 設定初始 DP 值。 | Using `0` for max problems when answers can be negative (use `Integer.MIN_VALUE` or `nums[0]`). <br> 在答案可能為負的最大值問題中使用 `0`（應使用 `Integer.MIN_VALUE` 或 `nums[0]`）。 |
| **Greedy vs. DP** | Greedy makes locally optimal choice; DP considers all paths via subproblems. <br> 貪婪法做局部最佳選擇；DP 透過子問題考慮所有路徑。 | Trying to solve "Jump Game II" (Min jumps) with simple greedy without proving the "farthest reach" property. <br> 試圖用簡單貪婪法解決「跳躍遊戲 II」，卻未證明「最遠可達」屬性。 |
| **Circular Dependencies** | Array is circular (last connects to first). <br> 陣列是環狀的（首尾相連）。 | Forgetting to break the circle into two linear cases (e.g., House Robber II: `0 to n-2` and `1 to n-1`). <br> 忘記將環拆解為兩個線性情況（如打家劫舍 II：`0 到 n-2` 與 `1 到 n-1`）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define State:** "I will define `dp[i]` as the maximum value achievable considering elements up to index `i`."
    **定義狀態：** 「我將定義 `dp[i]` 為考慮到索引 `i` 為止能達到的最大值。」
2.  **Recurrence Relation:** "The value at `i` depends on `i-1` and `i-2`. The transition equation is..."
    **遞迴關係：** 「`i` 的值取決於 `i-1` 和 `i-2`。轉移方程式為……」
3.  **Base Cases:** "For index 0, the value is simply..."
    **基本情況：** 「對於索引 0，值就是……」
4.  **Optimization:** "Since I only need the last two states, I can optimize space to $O(1)$."
    **優化：** 「由於我只需要最後兩個狀態，我可以將空間優化至 $O(1)$。」

### Whiteboard Strategy (白板策略)
*   Draw a small array (e.g., size 5).
*   Write the DP table values underneath the array indices as you trace the logic.
*   畫一個小陣列（例如大小為 5）。
*   在追蹤邏輯時，將 DP 表格的值寫在陣列索引下方。

### Common Follow-ups (常見追問)
*   "Can you reconstruct the solution path (not just the max value)?" -> Need to store `parent` pointers or backtrack the DP table.
    「你能重建解的路徑（而不僅是最大值）嗎？」 -> 需要儲存 `parent` 指標或回溯 DP 表格。
*   "What if the input stream is infinite?" -> Rolling variables are essential here.
    「如果輸入流是無限的呢？」 -> 滾動變數在此至關重要。

---

## 7. Practice Problems (練習題)

### 1. Easy/Intermediate: House Robber (LeetCode 198)
*   **Goal:** Maximize sum of non-adjacent elements.
*   **Hint:** $dp[i] = \max(dp[i-1], nums[i] + dp[i-2])$.
*   **目標：** 最大化非相鄰元素的總和。
*   **提示：** $dp[i] = \max(dp[i-1], nums[i] + dp[i-2])$。

### 2. Intermediate: Decode Ways (LeetCode 91)
*   **Goal:** Count ways to decode a string of digits (A=1, B=2... Z=26).
*   **Hint:** Handle '0' carefully. $dp[i] += dp[i-1]$ (1 digit) and $dp[i] += dp[i-2]$ (2 digits if valid).
*   **目標：** 計算數字字串解碼的方法數（A=1, B=2... Z=26）。
*   **提示：** 小心處理 '0'。$dp[i] += dp[i-1]$（1 位數）以及 $dp[i] += dp[i-2]$（若 2 位數有效）。

### 3. Advanced: Longest Increasing Subsequence (LeetCode 300)
*   **Goal:** Find length of longest subsequence where elements are increasing.
*   **Hint:** Standard DP is $O(N^2)$.
    *   **Senior Challenge:** Implement the $O(N \log N)$ solution using **Patience Sorting** (building the `tails` array with Binary Search). This is a frequent "Bar Raiser" question.
*   **目標：** 找出元素遞增的最長子序列長度。
*   **提示：** 標準 DP 為 $O(N^2)$。
    *   **資深挑戰：** 使用 **Patience Sorting**（利用二分搜尋建立 `tails` 陣列）實作 $O(N \log N)$ 解法。這是常見的「提高標準」題。

---

## 8. Quick Checklist (快速檢核表)

Before you say "I'm done":
在你說「我完成了」之前：

- [ ] **Initialization:** Did I handle `i=0` and `i=1` correctly? (Avoid `ArrayIndexOutOfBounds`).
    **初始化：** 我是否正確處理了 `i=0` 和 `i=1`？（避免陣列越界）。
- [ ] **Empty Input:** Did I return 0 or appropriate value for `nums.length == 0`?
    **空輸入：** 對於 `nums.length == 0`，我是否返回了 0 或適當的值？
- [ ] **State Meaning:** Does `dp[i]` mean "ending at i" or "best up to i"? (Crucial distinction).
    **狀態意義：** `dp[i]` 是指「以 i 結尾」還是「截至 i 為止的最佳解」？（關鍵區別）。
- [ ] **Space Opt:** Can I reduce `int[] dp` to just `int prev, curr`?
    **空間優化：** 我能將 `int[] dp` 縮減為僅 `int prev, curr` 嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Domino" Analogy (骨牌效應)
Think of 1-D DP as pushing dominoes. To knock down domino $i$, you need the force/state from domino $i-1$ (and maybe $i-2$). You don't need to look at domino 0 anymore once you are at 100.
將一維 DP 想像成推骨牌。要推倒骨牌 $i$，你需要來自骨牌 $i-1$（或許還有 $i-2$）的力量/狀態。當你推到第 100 個時，你不再需要回頭看第 0 個。

### The "Decision Tree" Pruning (決策樹修剪)
Imagine a massive tree of decisions. DP is simply identifying that two different branches reached the exact same state (same index, same constraints), so we merge them. We only calculate that node once.
想像一棵巨大的決策樹。DP 僅僅是識別出兩個不同的分支到達了完全相同的狀態（相同的索引、相同的限制），因此我們將它們合併。我們只計算該節點一次。