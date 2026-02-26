# 1-D Dynamic Programming: Intermediate Guide
# 一維動態規劃：中階指南

## 1. Learning Goals（學習目標）

*   **Master State Definition:** Learn to define $dp[i]$ precisely—whether it means "result up to index $i$" or "result ending at index $i$."
    **掌握狀態定義：** 學習精確定義 $dp[i]$ —— 是代表「直到索引 $i$ 的結果」還是「以索引 $i$ 結尾的結果」。
*   **Transition Derivation:** Ability to derive recurrence relations ($dp[i] = f(dp[i-1], dp[i-2], ...)$) systematically rather than by guessing.
    **推導轉移方程式：** 具備系統性推導遞迴關係式（$dp[i] = f(dp[i-1], dp[i-2], ...)$）的能力，而非憑猜測。
*   **Space Optimization:** Move from $O(N)$ space to $O(1)$ space using "Rolling Arrays" or state variables.
    **空間優化：** 使用「滾動陣列」或狀態變數，將空間複雜度從 $O(N)$ 優化至 $O(1)$。
*   **Differentiate Subarray vs. Subsequence:** Understand how continuity constraints change the DP state transition.
    **區分「子陣列」與「子序列」：** 理解連續性限制如何改變 DP 的狀態轉移。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
1-D DP is an optimization technique where a problem is broken down into a linear sequence of overlapping subproblems.
一維 DP 是一種優化技術，將問題分解為線性序列的重疊子問題。

We store the solution to each subproblem (usually in an array) to avoid redundant calculations.
我們儲存每個子問題的解（通常在陣列中），以避免重複計算。

### Intuition（直覺）
Think of it as **mathematical induction**.
將其視為 **數學歸納法**。

If you know the optimal answer for the first $i-1$ elements, how do you calculate the answer for the $i$-th element using one simple decision?
如果你知道前 $i-1$ 個元素的最佳解，如何透過一個簡單的決策來計算第 $i$ 個元素的答案？

### Complexity（複雜度）
*   **Time:** Typically $O(N)$, where $N$ is the length of the input.
    **時間：** 通常為 $O(N)$，其中 $N$ 是輸入長度。
*   **Space:** Naively $O(N)$ for the DP table; Optimized to $O(1)$ if the transition only depends on a fixed number of previous states.
    **空間：** 樸素解法為 $O(N)$（DP 表）；若轉移僅依賴固定數量的先前狀態，可優化為 $O(1)$。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** You need the Maximum/Minimum value, number of ways, or existence (True/False) involving an array or string.
    **適用：** 當你需要求最大/最小值、方法數、或存在性（真/假），且涉及陣列或字串時。
*   **Don't use when:** The problem requires generating *all* permutations or combinations (use Backtracking), or if the data has no overlapping subproblems (use Divide & Conquer).
    **不適用：** 當問題需要生成「所有」排列或組合（使用回溯法），或資料沒有重疊子問題（使用分治法）時。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: The "Choice" at Step $i$ (Linear Scan)
**模式 A：第 $i$ 步的「選擇」（線性掃描）**
*   **Logic:** At index $i$, you either include $nums[i]$ or skip it, based on constraints.
    **邏輯：** 在索引 $i$，根據限制條件，你選擇包含 $nums[i]$ 或跳過它。
*   **Example:** House Robber ($dp[i] = \max(dp[i-1], nums[i] + dp[i-2])$).
    **範例：** 打家劫舍。

### Pattern B: Ending at Index $i$ (Subarray/Subsequence)
**模式 B：以索引 $i$ 結尾（子陣列/子序列）**
*   **Logic:** $dp[i]$ represents the optimal value of a subarray/subsequence that *must* include $nums[i]$ as the last element.
    **邏輯：** $dp[i]$ 代表「必須」包含 $nums[i]$ 作為最後一個元素的子陣列/子序列的最佳值。
*   **Example:** Maximum Subarray Sum (Kadane's Algorithm), Longest Increasing Subsequence (LIS).
    **範例：** 最大子陣列和（Kadane 演算法）、最長遞增子序列（LIS）。

### Pattern C: State Machine (Multi-state 1-D DP)
**模式 C：狀態機（多狀態一維 DP）**
*   **Logic:** At each index $i$, you can be in one of $k$ states (e.g., holding stock, sold stock, cooldown).
    **邏輯：** 在每個索引 $i$，你可能處於 $k$ 種狀態之一（例如：持有股票、已賣出、冷卻期）。
*   **Example:** Best Time to Buy and Sell Stock with Cooldown.
    **範例：** 買賣股票的最佳時機（含冷卻期）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Maximum Product Subarray (LeetCode 152)
### 問題：最大乘積子陣列

**Problem Statement:**
Given an integer array `nums`, find a contiguous non-empty subarray within the array that has the largest product, and return the product.
給定一個整數陣列 `nums`，找出陣列中乘積最大的連續非空子陣列，並返回該乘積。

**Input:** `[2, 3, -2, 4]` -> **Output:** `6` (`[2, 3]`)
**Input:** `[-2, 0, -1]` -> **Output:** `0`

---

### Thought Process（思路）

#### 1. Brute Force (暴力解)
Iterate through all possible subarrays and calculate their products.
遍歷所有可能的子陣列並計算其乘積。
*   Complexity: $O(N^2)$. Too slow.
    複雜度：$O(N^2)$。太慢。

#### 2. Naive DP Attempt (樸素 DP 嘗試)
Let $dp[i]$ be the max product ending at index $i$.
設 $dp[i]$ 為以索引 $i$ 結尾的最大乘積。
*   Transition: $dp[i] = \max(nums[i], dp[i-1] * nums[i])$.
    轉移：$dp[i] = \max(nums[i], dp[i-1] * nums[i])$。
*   **Issue:** This fails with negative numbers. If we have `[-2, 3, -4]`, the max product at index 2 should be $(-2 * 3 * -4) = 24$. But a simple max function would discard the negative product from previous steps.
    **問題：** 這在負數時會失效。如果我們有 `[-2, 3, -4]`，索引 2 的最大乘積應為 24。但簡單的 max 函數會丟棄先前的負乘積。

#### 3. Optimal Solution: Tracking Min and Max (最佳解：同時追蹤最小值與最大值)
Because a negative number multiplied by a negative number becomes positive, we must track both the **maximum** and **minimum** product ending at the current position.
因為負數乘以負數會變正數，我們必須同時追蹤以當前位置結尾的 **最大乘積** 與 **最小乘積**。

*   **State:**
    *   `curMax`: Max product ending at current index.
    *   `curMin`: Min product ending at current index.
*   **Transition:**
    When we see a negative number, `curMax` and `curMin` swap roles.
    當我們遇到負數時，`curMax` 和 `curMin` 互換角色。
    $curMax[i] = \max(nums[i], nums[i] * curMax[i-1], nums[i] * curMin[i-1])$
    $curMin[i] = \min(nums[i], nums[i] * curMax[i-1], nums[i] * curMin[i-1])$

---

### TypeScript Solution（參考解）

```typescript
/**
 * Calculates the maximum product of a contiguous subarray.
 * 計算連續子陣列的最大乘積。
 * 
 * Time Complexity: O(N) - Single pass.
 * Space Complexity: O(1) - Using variables instead of arrays.
 */
function maxProduct(nums: number[]): number {
    if (nums.length === 0) return 0;

    // Initialize global result with the first element
    // 用第一個元素初始化全域結果
    let maxSoFar = nums[0];

    // Current max and min ending at the previous position
    // 在前一個位置結尾的當前最大值與最小值
    let currentMax = nums[0];
    let currentMin = nums[0];

    for (let i = 1; i < nums.length; i++) {
        const num = nums[i];

        // If current number is negative, max and min could swap
        // 如果當前數字是負數，最大值與最小值可能會互換
        if (num < 0) {
            [currentMax, currentMin] = [currentMin, currentMax];
        }

        // Calculate new max/min ending at current position i
        // We compare num itself vs num * previous_state to handle restarts (e.g., after a 0)
        // 計算以當前位置 i 結尾的新最大/最小值
        // 我們比較 num 本身與 num * previous_state，以處理重新開始的情況（例如遇到 0 之後）
        currentMax = Math.max(num, currentMax * num);
        currentMin = Math.min(num, currentMin * num);

        // Update global maximum
        // 更新全域最大值
        maxSoFar = Math.max(maxSoFar, currentMax);
    }

    return maxSoFar;
}
```

### Common Mistake (錯誤示範)
```typescript
// WRONG: Ignoring the negative number effect
// 錯誤：忽略負數的影響
// Input: [-2, 3, -4] -> Returns 3, Expected 24
let dp = nums[0];
let maxRes = nums[0];
for(let i=1; i<nums.length; i++) {
    dp = Math.max(nums[i], nums[i] * dp); // Fails to keep the negative chain
    maxRes = Math.max(maxRes, dp);
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Subarray (子陣列)** | **Subsequence (子序列)** | Subarray must be **contiguous** (use `dp[i]` ending at $i$). Subsequence can skip elements (use `dp[i]` as max length up to $i$). <br> 子陣列必須**連續**；子序列可以跳過元素。 |
| **$dp[i]$ = Result at $i$** | **$dp[i]$ = Result ending at $i$** | "Result at $i$" usually implies cumulative max/min seen so far. "Ending at $i$" implies strict inclusion of index $i$. <br> 「在 $i$ 的結果」通常指至今為止的累計最值；「以 $i$ 結尾」暗示必須包含索引 $i$。 |
| **Greedy** | **Dynamic Programming** | Greedy makes the local optimal choice at each step without looking back. DP considers previous states. <br> 貪婪法每步只做局部最佳選擇而不回頭看；DP 則考慮先前的狀態。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework (闡述口條框架)
1.  **Identify the Recursive Structure:** "This problem asks for an optimal value based on array choices, which suggests Dynamic Programming."
    **識別遞迴結構：** 「這個問題要求基於陣列選擇的最佳值，這暗示了動態規劃。」
2.  **Define State Clearly:** "Let's define $dp[i]$ as the maximum product of a subarray **ending at index $i$**."
    **清晰定義狀態：** 「讓我們定義 $dp[i]$ 為**以索引 $i$ 結尾**的子陣列之最大乘積。」
3.  **Discuss Base Cases:** "For index 0, the max is just the element itself."
    **討論基本情況：** 「對於索引 0，最大值就是元素本身。」
4.  **Propose Optimization:** "Since $dp[i]$ only depends on $dp[i-1]$, we can optimize space to $O(1)$."
    **提出優化：** 「由於 $dp[i]$ 僅依賴 $dp[i-1]$，我們可以將空間優化至 $O(1)$。」

### Whiteboard Strategy (白板策略)
*   Draw a table for input `[-2, 3, -4]`.
    為輸入 `[-2, 3, -4]` 畫一個表格。
*   Columns: `i`, `num`, `curMax`, `curMin`, `GlobalMax`.
    欄位：`i`, `num`, `curMax`, `curMin`, `GlobalMax`。
*   Walk through the trace manually *before* writing code.
    在寫程式碼*之前*，手動演練一次追蹤過程。

---

## 7. Practice Problems（練習題）

### Easy: Climbing Stairs (LeetCode 70)
*   **Prompt:** Count ways to reach step $n$ if you can take 1 or 2 steps.
    **題目：** 如果你可以走 1 步或 2 步，計算到達第 $n$ 階的方法數。
*   **Hint:** Fibonacci sequence. $dp[i] = dp[i-1] + dp[i-2]$.
    **提示：** 費氏數列。$dp[i] = dp[i-1] + dp[i-2]$。

### Intermediate: House Robber II (LeetCode 213)
*   **Prompt:** Houses are arranged in a circle. Cannot rob adjacent houses.
    **題目：** 房屋排列成圓圈。不能搶劫相鄰的房屋。
*   **Hint:** Break the circle. Run linear DP twice: once on `nums[0...n-2]` and once on `nums[1...n-1]`. Take the max.
    **提示：** 打破圓圈。執行兩次線性 DP：一次針對 `nums[0...n-2]`，一次針對 `nums[1...n-1]`。取最大值。

### Hard: Longest Valid Parentheses (LeetCode 32)
*   **Prompt:** Find the length of the longest valid (well-formed) parentheses substring.
    **題目：** 找出最長有效（格式正確）括號子字串的長度。
*   **Hint:** $dp[i]$ represents the length of the longest valid substring ending at $i$. If `s[i] == ')'` and `s[i-1] == '('`, $dp[i] = dp[i-2] + 2$. Handle nested cases `(())` carefully.
    **提示：** $dp[i]$ 代表以 $i$ 結尾的最長有效子字串長度。若 `s[i] == ')'` 且 `s[i-1] == '('`，則 $dp[i] = dp[i-2] + 2$。需小心處理巢狀情況 `(())`。

---

## 8. Checklists（快速檢核表）

Use this during your interview to debug or verify your solution.
在面試中使用此表來除錯或驗證你的解法。

- [ ] **Initialization:** Did I handle $i=0$ or empty input correctly?
    **初始化：** 我是否正確處理了 $i=0$ 或空輸入？
- [ ] **State Definition:** Does my $dp[i]$ mean "ending at $i$" or "best up to $i$"?
    **狀態定義：** 我的 $dp[i]$ 是指「以 $i$ 結尾」還是「直到 $i$ 的最佳解」？
- [ ] **Transition Logic:** Did I cover all choices (e.g., take vs. skip)?
    **轉移邏輯：** 我是否涵蓋了所有選擇（例如：選取 vs 跳過）？
- [ ] **Space Complexity:** Can I reduce the array to 2 variables?
    **空間複雜度：** 我能將陣列縮減為 2 個變數嗎？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Domino Effect" (骨牌效應)
Imagine 1-D DP as a row of dominoes. To knock down the $i$-th domino (calculate $dp[i]$), you rely on the force/position of the $(i-1)$-th domino.
將一維 DP 想像成一排骨牌。要推倒第 $i$ 個骨牌（計算 $dp[i]$），你依賴於第 $i-1$ 個骨牌的力量/位置。

### The "Amnesiac Traveler" (失憶的旅人)
The traveler (algorithm) at step $i$ doesn't remember the entire path from step 0. They only carry a small note (the `dp` variables) telling them the best result from yesterday.
旅人（演算法）在第 $i$ 步時不記得從第 0 步開始的整條路徑。他們只帶著一張小紙條（`dp` 變數），上面寫著昨天的最佳結果。