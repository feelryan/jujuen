Here is the complete interview preparation guide for **1-D Dynamic Programming**, tailored for a Senior Software Engineer, following your specified structure and bilingual format.

---

# 1-D Dynamic Programming: Interview Guide
# 一維動態規劃：面試實戰指南

**Level:** Intermediate (中級)
**Language:** Java
**Target Audience:** Senior Software Engineers (7-12 YOE)

---

## 1. Learning Objectives (學習目標)

1.  **Master State Definition:** Learn to define `dp[i]` precisely (e.g., "max value ending at index `i`" vs. "max value up to index `i`").
    **掌握狀態定義：** 學習精確定義 `dp[i]`（例如：「以索引 `i` 結尾的最大值」與「截至索引 `i` 為止的最大值」的區別）。

2.  **Transition Equation Derivation:** Ability to derive the recurrence relation $dp[i] = f(dp[i-1], dp[i-2], ...)$ from problem constraints.
    **推導轉移方程式：** 具備從問題限制中推導出 $dp[i] = f(dp[i-1], dp[i-2], ...)$ 遞迴關係的能力。

3.  **Space Optimization:** Understand how to optimize space complexity from $O(N)$ to $O(1)$ using rolling variables.
    **空間優化：** 理解如何使用滾動變數將空間複雜度從 $O(N)$ 優化至 $O(1)$。

4.  **Distinguish Greedy vs. DP:** Recognize when a local optimum leads to a global optimum (Greedy) versus when all possibilities must be considered (DP).
    **分辨貪婪與動態規劃：** 識別何時局部最佳解能導致全域最佳解（貪婪演算法），以及何時必須考慮所有可能性（動態規劃）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Dynamic Programming is a method for solving complex problems by breaking them down into simpler subproblems, solving each of those subproblems just once, and storing their solutions.
動態規劃是一種透過將複雜問題分解為更簡單的子問題、僅解決每個子問題一次並儲存其解來解決問題的方法。

### Intuition (直覺)
For 1-D DP, imagine you are walking along a line. To decide the best action at step `i`, you only need to know the best outcomes of the previous few steps (`i-1`, `i-2`, etc.) and the current cost/value.
對於一維 DP，想像你沿著一條線行走。要決定第 `i` 步的最佳行動，你只需要知道前幾步（`i-1`、`i-2` 等）的最佳結果以及當前的成本/價值。

### Complexity (複雜度)
-   **Time:** Usually $O(N)$, where $N$ is the array length.
    **時間：** 通常為 $O(N)$，其中 $N$ 為陣列長度。
-   **Space:** Naively $O(N)$ for the DP table, often optimizable to $O(1)$ or $O(K)$ where $K$ is the lookback window.
    **空間：** 建立 DP 表通常為 $O(N)$，常可優化至 $O(1)$ 或 $O(K)$，其中 $K$ 為回溯窗口大小。

### When to Use (適用場景)
-   **Optimization:** Finding minimum cost, maximum profit, longest path.
    **最佳化：** 尋找最小成本、最大利潤、最長路徑。
-   **Counting:** Number of ways to reach a target.
    **計數：** 達成目標的方法數。
-   **Decision Making:** Can/Cannot reach a target (Boolean).
    **決策：** 能否達成目標（布林值）。

### When NOT to Use (不適用場景)
-   **Input is unsorted/static and requires search:** Use Binary Search or Hash Maps.
    **輸入未排序/靜態且需要搜尋：** 使用二分搜尋或雜湊表。
-   **Shortest path in unweighted graphs:** BFS is usually faster and simpler.
    **無權圖中的最短路徑：** BFS 通常更快且更簡單。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Linear Scan (Fibonacci Style) / 線性掃描（費波那契風格）
-   **Pattern:** $dp[i]$ depends only on $dp[i-1]$ and $dp[i-2]$.
    **模式：** $dp[i]$ 僅依賴於 $dp[i-1]$ 和 $dp[i-2]$。
-   **Examples:** Climbing Stairs, House Robber.
    **範例：** 爬樓梯、打家劫舍。

### B. Subarray Ending at `i` / 以 `i` 結尾的子陣列
-   **Pattern:** $dp[i]$ represents the best value of a subarray *ending exactly* at index $i$. The answer is $\max(dp)$.
    **模式：** $dp[i]$ 代表*恰好結束*在索引 $i$ 的子陣列最佳值。答案為 $\max(dp)$。
-   **Examples:** Maximum Subarray (Kadane's), Maximum Product Subarray.
    **範例：** 最大子陣列（Kadane 演算法）、最大乘積子陣列。

### C. Longest Increasing Subsequence (LIS) / 最長遞增子序列
-   **Pattern:** To calculate $dp[i]$, we must check all $j < i$ where $nums[j] < nums[i]$. Complexity is $O(N^2)$.
    **模式：** 為了計算 $dp[i]$，我們必須檢查所有 $j < i$ 且 $nums[j] < nums[i]$ 的情況。複雜度為 $O(N^2)$。
-   **Note:** Often has an $O(N \log N)$ greedy optimization, but understanding the DP approach is crucial for variations.
    **註記：** 通常有 $O(N \log N)$ 的貪婪優化解，但理解 DP 方法對於處理變體至關重要。

---

## 4. Example Walkthrough (範例講解)

### Problem: House Robber (打家劫舍)
**Problem Statement:**
You are a professional robber planning to rob houses along a street. Adjacent houses have security systems connected. You cannot rob two adjacent houses. Given an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight.
**問題重述：**
你是一個專業強盜，計劃搶劫沿街的房屋。相鄰的房屋裝有連線的防盜系統。你不能搶劫兩間相鄰的房屋。給定一個整數陣列 `nums` 代表每間房子的金額，返回你今晚能搶到的最大金額。

### Approach (思路)

1.  **Brute Force (Recursion):**
    For each house, we have two choices: rob it (and skip the next one) or skip it (and consider the next one). This creates a binary tree of decisions.
    **暴力解（遞迴）：** 對於每間房子，我們有兩個選擇：搶（並跳過下一間）或不搶（並考慮下一間）。這會產生一個決策二元樹。
    *Complexity:* $O(2^N)$ - Time Limit Exceeded.

2.  **DP State Definition:**
    Let $dp[i]$ be the maximum money we can rob from the first $i$ houses (index $0$ to $i$).
    **DP 狀態定義：** 令 $dp[i]$ 為從前 $i$ 間房子（索引 $0$ 到 $i$）能搶到的最大金額。

3.  **Transition Equation:**
    At house $i$, we can either:
    在第 $i$ 間房子，我們可以：
    -   **Rob house $i$:** We get `nums[i]` + max money from $i-2$ houses ($dp[i-2]$).
        **搶第 $i$ 間：** 獲得 `nums[i]` + 前 $i-2$ 間房子的最大金額（$dp[i-2]$）。
    -   **Skip house $i$:** We keep the max money from $i-1$ houses ($dp[i-1]$).
        **跳過第 $i$ 間：** 保持前 $i-1$ 間房子的最大金額（$dp[i-1]$）。
    
    $$dp[i] = \max(nums[i] + dp[i-2], \quad dp[i-1])$$

4.  **Base Cases:**
    -   $dp[0] = nums[0]$
    -   $dp[1] = \max(nums[0], nums[1])$

### Java Reference Solution (Optimized) / Java 參考解（優化版）

We only need `prev1` ($dp[i-1]$) and `prev2` ($dp[i-2]$), so we can optimize space to $O(1)$.
我們只需要 `prev1` ($dp[i-1]$) 和 `prev2` ($dp[i-2]$)，因此可以將空間優化至 $O(1)$。

```java
class Solution {
    public int rob(int[] nums) {
        // Edge case: no houses
        // 邊界情況：沒有房子
        if (nums == null || nums.length == 0) {
            return 0;
        }
        
        // Edge case: only one house
        // 邊界情況：只有一間房子
        if (nums.length == 1) {
            return nums[0];
        }

        // prev2 represents dp[i-2], prev1 represents dp[i-1]
        // prev2 代表 dp[i-2]，prev1 代表 dp[i-1]
        int prev2 = 0; 
        int prev1 = 0;

        for (int num : nums) {
            // Calculate current max based on the recurrence relation
            // 根據遞迴關係計算當前最大值
            // dp[i] = max(rob current + dp[i-2], skip current -> dp[i-1])
            int current = Math.max(prev2 + num, prev1);
            
            // Shift the window for the next iteration
            // 為下一次迭代移動窗口
            prev2 = prev1;
            prev1 = current;
        }

        // After the loop, prev1 holds the result for the entire array
        // 迴圈結束後，prev1 包含整個陣列的結果
        return prev1;
    }
}
```

### Common Mistake (錯誤示範)
**Mistake:** Thinking Greedy. "Always rob the richest house available."
**錯誤：** 貪婪思維。「總是搶金額最高的房子。」
*Example:* `[10, 2, 2, 100]`.
*Greedy:* Rob 100 -> cannot rob 2 -> rob 10. Total = 110. (Wrong)
*DP:* Rob 10 + 2 (index 2) -> 12? No.
*Correct:* Rob 10, Skip 2, Skip 2, Rob 100? No, adjacent constraint applies to indices.
Correct Logic: `dp[0]=10`, `dp[1]=10`, `dp[2]=12`, `dp[3]=110`. Wait, let's trace `[10, 20, 10, 20]`.
Greedy might pick 20, then cannot pick adjacent.
The point is: Greedy fails because a local high value might prevent taking a huge value later.

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) |
| :--- | :--- |
| **Subarray vs. Subsequence** | **Subarray** is contiguous (e.g., `[1,2]` in `[1,2,3]`). **Subsequence** is not necessarily contiguous but maintains order (e.g., `[1,3]` in `[1,2,3]`). <br> **子陣列**是連續的。**子序列**不一定連續但保持順序。 |
| **State Definition** | Don't confuse "Max value **ending at** $i$" with "Max value **up to** $i$". <br> 別混淆「**以 $i$ 結尾**的最大值」與「**截至 $i$ 為止**的最大值」。 |
| **Initialization** | Initializing with `0` vs `Integer.MIN_VALUE`. If negative numbers are allowed (e.g., Max Subarray Sum), `0` is wrong. <br> 初始化為 `0` 與 `Integer.MIN_VALUE`。若允許負數（如最大子陣列和），設為 `0` 是錯的。 |
| **Off-by-one Errors** | DP arrays often need size `N+1` to handle the base case (index 0 representing empty/start). <br> DP 陣列通常需要大小 `N+1` 來處理基本情況（索引 0 代表空或開始）。 |

---

## 6. Interview Strategy (面試實戰建議)

### The Framework (口條框架)
1.  **Define the objective:** "We want to maximize X subject to constraint Y."
    **定義目標：** 「我們想要在限制 Y 下最大化 X。」
2.  **Identify the recurrence:** "The decision at step `i` depends on..."
    **識別遞迴：** 「第 `i` 步的決策取決於……」
3.  **Propose DP:** "Since this has overlapping subproblems, I will use DP."
    **提出 DP：** 「由於這具有重疊子問題，我將使用 DP。」
4.  **Optimize:** "I can optimize the space from $O(N)$ to $O(1)$."
    **優化：** 「我可以將空間從 $O(N)$ 優化到 $O(1)$。」

### Whiteboard Strategy (白板策略)
-   Draw an array of size 5. Fill in the DP values manually for the first 3 indices to verify your logic before coding.
    畫一個大小為 5 的陣列。在寫程式碼之前，手動填寫前 3 個索引的 DP 值以驗證邏輯。
-   Write the Transition Equation clearly on the board: $dp[i] = \dots$
    在白板上清楚寫下轉移方程式：$dp[i] = \dots$

### Common Follow-ups (常見追問)
-   **Q:** What if the array is circular? (e.g., House Robber II)
    **問：** 如果陣列是環狀的怎麼辦？（例如：打家劫舍 II）
    **A:** Run the linear DP twice: once from `0` to `n-2`, once from `1` to `n-1`, take the max.
    **答：** 執行兩次線性 DP：一次從 `0` 到 `n-2`，一次從 `1` 到 `n-1`，取最大值。
-   **Q:** How to reconstruct the path/solution?
    **問：** 如何重建路徑/解？
    **A:** Use a separate array `parent[i]` to store which index led to the optimal value at `i`.
    **答：** 使用一個單獨的陣列 `parent[i]` 來儲存是哪個索引導致了 `i` 處的最佳值。

---

## 7. Exercises (練習題)

### Easy: Min Cost Climbing Stairs (最小花費爬樓梯)
-   **Hint:** $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$.
-   **Focus:** Handling the start (can start at index 0 or 1).
    **重點：** 處理起點（可以從索引 0 或 1 開始）。

### Medium: Decode Ways (解碼方法)
-   **Problem:** 'A'->1, 'B'->2... Given "12", return 2 ("AB" or "L").
    **問題：** 'A'->1, 'B'->2... 給定 "12"，返回 2 ("AB" 或 "L")。
-   **Hint:** Similar to Climbing Stairs, but conditional. If `s[i]` is valid single digit, add `dp[i-1]`. If `s[i-1...i]` is valid two digits (10-26), add `dp[i-2]`.
    **提示：** 類似爬樓梯，但是有條件的。若 `s[i]` 是有效單個數字，加 `dp[i-1]`。若 `s[i-1...i]` 是有效兩位數 (10-26)，加 `dp[i-2]`。
-   **Trap:** Handling '0' (e.g., "06" is invalid, "10" is valid).
    **陷阱：** 處理 '0'（例如："06" 無效，"10" 有效）。

### Hard/Medium: Longest Increasing Subsequence (最長遞增子序列)
-   **Problem:** Find length of longest subsequence where elements are strictly increasing.
    **問題：** 尋找元素嚴格遞增的最長子序列長度。
-   **Hint:** $dp[i]$ = length of LIS ending at index $i$. Loop $j$ from $0$ to $i-1$. If $nums[i] > nums[j]$, $dp[i] = \max(dp[i], dp[j] + 1)$.
    **提示：** $dp[i]$ = 以索引 $i$ 結尾的 LIS 長度。迴圈 $j$ 從 $0$ 到 $i-1$。若 $nums[i] > nums[j]$，則 $dp[i] = \max(dp[i], dp[j] + 1)$。

---

## 8. Quick Checklists (快速檢核表)

### Debugging / Self-Review (自我審查)
-   [ ] **Base Case:** Did I handle $N=0$ or $N=1$?
    **基本情況：** 我是否處理了 $N=0$ 或 $N=1$？
-   [ ] **Initialization:** Is the DP array initialized correctly (0, -1, or MIN_VALUE)?
    **初始化：** DP 陣列初始化是否正確（0、-1 或 MIN_VALUE）？
-   [ ] **Index Bounds:** Does `i-2` cause an IndexOutOfBounds exception?
    **索引邊界：** `i-2` 是否會導致索引越界異常？
-   [ ] **Return Value:** Am I returning `dp[n-1]` or `max(dp)`? (Depends on state definition).
    **回傳值：** 我是回傳 `dp[n-1]` 還是 `max(dp)`？（取決於狀態定義）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Domino Effect" (骨牌效應)
Think of 1-D DP as pushing dominoes. To know if domino `i` falls (or how hard it falls), you just need to look at the dominoes immediately behind it. You don't need to look at the start of the chain again.
將一維 DP 想像成推骨牌。要知道骨牌 `i` 是否倒下（或倒下的力道），你只需要看它緊後面的骨牌。你不需要重新看鏈條的起點。

### The "Toll Booth" (收費站)
Imagine a highway with toll booths. At each booth, you calculate the cumulative cost to get there based on the cheaper of the previous connected roads. You write this cost down on the booth so the next driver doesn't have to recalculate.
想像一條有收費站的高速公路。在每個收費站，你根據之前連接道路中較便宜的一條來計算到達那裡的累計成本。你將這個成本寫在收費站上，這樣下一個駕駛就不必重新計算。