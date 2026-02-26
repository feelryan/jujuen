Here is the comprehensive guide for **1-D Dynamic Programming**, tailored for a Senior Software Engineer, focusing on foundational concepts (Beginner level relative to the DP domain) with TypeScript implementation.

這是一份針對 **一維動態規劃（1-D Dynamic Programming）** 的完整教材，專為資深軟體工程師量身打造，著重於基礎觀念建立（相對於 DP 領域的入門級），並使用 TypeScript 實作。

---

# 1-D Dynamic Programming: Foundation & Patterns
# 一維動態規劃：基礎與模式

## 1. Learning Goals（學習目標）

*   **Master the "State" Definition:** Learn to translate a problem into a mathematical definition $dp[i]$.
    **掌握「狀態」定義：** 學習將問題轉化為數學定義 $dp[i]$。
*   **Transition from Recursion to Iteration:** Understand the evolution from Brute Force Recursion $\to$ Memoization (Top-down) $\to$ Tabulation (Bottom-up).
    **從遞迴過渡到迭代：** 理解從暴力遞迴 $\to$ 記憶化搜索（由上而下） $\to$ 列表法（由下而上）的演進過程。
*   **Space Optimization:** Learn how to reduce space complexity from $O(N)$ to $O(1)$ using "Rolling Variables".
    **空間優化：** 學習如何使用「滾動變數」將空間複雜度從 $O(N)$ 降低至 $O(1)$。
*   **Distinguish DP from Greedy:** Recognize when local optimality does *not* lead to global optimality.
    **區分 DP 與貪婪演算法：** 辨識何時局部最佳解 *無法* 導向全域最佳解。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
Dynamic Programming is a method for solving complex problems by breaking them down into simpler subproblems, solving each of those subproblems just once, and storing their solutions.
動態規劃是一種解決複雜問題的方法，通過將其分解為更簡單的子問題，每個子問題僅解決一次，並儲存其解。

For **1-D DP**, the state of the problem depends on a single variable, typically the index $i$ of an array or a string.
對於 **一維 DP**，問題的狀態取決於單一變數，通常是陣列或字串的索引 $i$。

### Intuition（直覺）
Think of it as "Recursion with Caching" or "Filling out a form".
可以將其視為「帶有快取的遞迴」或「填寫表格」。
Instead of recalculating `fib(5)` every time, we look it up in a table.
我們不再每次重新計算 `fib(5)`，而是直接查表。

### Complexity（複雜度）
*   **Time:** Usually $O(N)$, where $N$ is the input size (we visit each state once).
    **時間：** 通常為 $O(N)$，其中 $N$ 是輸入大小（我們遍歷每個狀態一次）。
*   **Space:** $O(N)$ for the table, often optimizable to $O(1)$ if we only need the last few states.
    **空間：** 表格需要 $O(N)$，如果我們只需要最後幾個狀態，通常可優化至 $O(1)$。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** Problem asks for Maximum/Minimum, Total ways, or Existence (True/False), and has **Overlapping Subproblems**.
    **適用時機：** 問題詢問最大值/最小值、總方法數或存在性（真/假），且具有 **重疊子問題**。
*   **Don't use when:** The problem requires generating all permutations/combinations (use Backtracking) or the data has no sequential dependency.
    **不適用時機：** 問題需要生成所有排列/組合（使用回溯法），或數據沒有順序依賴性。

---

## 3. Typical Patterns（典型題型 / 模式）

For 1-D DP, most problems fall into these transition patterns:
對於一維 DP，大多數問題屬於以下轉移模式：

1.  **Fibonacci Style (Dependency on $i-1, i-2$):**
    *   $dp[i] = dp[i-1] + dp[i-2]$
    *   Examples: Climbing Stairs, House Robber.
    *   例：爬樓梯、打家劫舍。

2.  **Accumulation / Cost (Min/Max Path):**
    *   $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$
    *   Examples: Min Cost Climbing Stairs.
    *   例：最小花費爬樓梯。

3.  **Longest Subsequence (Dependency on $0 \dots i-1$):**
    *   $dp[i] = \max(dp[j]) + 1$ for all $j < i$ where condition met.
    *   Examples: Longest Increasing Subsequence (LIS).
    *   例：最長遞增子序列。

---

## 4. Example Walkthrough（範例講解）

### Problem: House Robber (打家劫舍)
**Problem Statement:**
You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. The only constraint stopping you is that adjacent houses have security systems connected and **it will automatically contact the police if two adjacent houses were broken into on the same night**. Given an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.

**問題重述：**
你是一個專業的搶匪，計劃搶劫沿街的房屋。每間房都有一定數量的現金。唯一的限制是相鄰的房屋裝有連動的防盜系統，**如果兩間相鄰的房屋在同一晚被闖入，系統會自動報警**。給定一個整數陣列 `nums` 代表每間房的現金，請返回在不觸發警報的情況下，今晚能搶到的最大金額。

### Approach 1: Brute Force Recursion (暴力遞迴)
*   **Idea:** For each house, we have two choices: Rob it (and skip the next one) or Skip it (and consider the next one).
    **思路：** 對於每間房，我們有兩個選擇：搶它（並跳過下一間）或 跳過它（並考慮下一間）。
*   **Complexity:** $O(2^N)$ Time (Tree grows exponentially).
    **複雜度：** $O(2^N)$ 時間（樹狀結構指數增長）。

### Approach 2: Top-Down DP (Memoization) (由上而下：記憶化)
*   **Idea:** Store the result of `rob(i)` so we don't re-solve it.
    **思路：** 儲存 `rob(i)` 的結果，這樣我們就不必重新計算。
*   **Complexity:** $O(N)$ Time, $O(N)$ Space (Recursion stack + Map).
    **複雜度：** $O(N)$ 時間，$O(N)$ 空間（遞迴堆疊 + Map）。

### Approach 3: Bottom-Up DP (Tabulation) (由下而上：列表法) - **Best Practice**
*   **State Definition:** $dp[i]$ = Max money robbable from first $i$ houses.
    **狀態定義：** $dp[i]$ = 從前 $i$ 間房子能搶到的最大金額。
*   **Transition:** At house $i$, we either:
    1.  Don't rob house $i$: Take max from house $i-1$ ($dp[i-1]$).
    2.  Rob house $i$: Take money from house $i$ + max from house $i-2$ ($nums[i] + dp[i-2]$).
    **轉移方程：** 在第 $i$ 間房，我們要麼：
    1.  不搶第 $i$ 間：取第 $i-1$ 間的最大值 ($dp[i-1]$)。
    2.  搶第 $i$ 間：取第 $i$ 間的錢 + 第 $i-2$ 間的最大值 ($nums[i] + dp[i-2]$)。
    *   $dp[i] = \max(dp[i-1], nums[i] + dp[i-2])$

### TypeScript Solution (Reference)

```typescript
/**
 * Calculates the maximum amount of money that can be robbed.
 * 計算可以搶劫的最大金額。
 * 
 * Time Complexity: O(N) - One pass through the array.
 * Space Complexity: O(1) - Using rolling variables (optimized from O(N)).
 */
function rob(nums: number[]): number {
    const n = nums.length;
    
    // Base Case handling
    // 基礎情況處理
    if (n === 0) return 0;
    if (n === 1) return nums[0];

    // Instead of an array dp[], we use two variables to save space.
    // prev2 represents dp[i-2], prev1 represents dp[i-1].
    // 我們不使用陣列 dp[]，而是使用兩個變數來節省空間。
    // prev2 代表 dp[i-2]，prev1 代表 dp[i-1]。
    
    let prev2 = 0;        // Theoretically dp[-2] or initial state
    let prev1 = 0;        // Theoretically dp[-1] or initial state
    
    // Iterate through each house
    // 遍歷每一間房子
    for (const num of nums) {
        // The core recurrence relation:
        // Max of (Skipping current, Robbing current + previous non-adjacent)
        // 核心遞迴關係：
        // (跳過當前，搶劫當前 + 前一個非相鄰) 取最大值
        const current = Math.max(prev1, num + prev2);
        
        // Shift the rolling variables forward
        // 將滾動變數向前移動
        prev2 = prev1;
        prev1 = current;
    }

    return prev1;
}
```

### Why the "Wrong" Approach Fails (錯誤示範)
**Greedy Approach:** "Always rob the richest house available."
**貪婪法：**「總是搶眼前最有錢的房子。」
*   Input: `[10, 20, 15, 80]`
*   Greedy might pick 20, then cannot pick 15 or 10. Remaining is 80? No, if you pick 20, you can't pick 80 if they were adjacent (in a different config).
*   Better example: `[2, 10, 10, 2]`
    *   Greedy picks max 10. Then you can't pick the other 10. Total = 12.
    *   Optimal: Pick 2 + 10 (index 2) is wrong. Optimal is 10 + 10? No, adjacent.
    *   Correct Example for Greedy failure: `[1, 100, 1, 1, 100]`
    *   Greedy picks 100. Then adjacent are blocked.
    *   DP ensures we evaluate the *combination* of choices.
    *   DP 確保我們評估的是選擇的 *組合*。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast |
| :--- | :--- |
| **Off-by-one Error** | **Confusion:** Is $dp[i]$ the result for index $i$ or length $i$? <br> **Fix:** Be consistent. Usually, make $dp$ array size $N+1$ to handle base case 0 easily. <br> **混淆：** $dp[i]$ 是指索引 $i$ 還是長度 $i$ 的結果？ <br> **解法：** 保持一致。通常將 $dp$ 陣列大小設為 $N+1$ 以便處理基礎情況 0。 |
| **Greedy vs DP** | **Confusion:** Why not just take the best step now? <br> **Truth:** Greedy makes a locally optimal choice at each step. DP considers future consequences of current choices. <br> **混淆：** 為什麼不直接採取當前最好的一步？ <br> **真相：** 貪婪法每一步都做局部最佳選擇。DP 則考慮當前選擇對未來的影響。 |
| **Base Cases** | **Pitfall:** Forgetting $i=0$ or $i=1$. <br> **Fix:** Always manually calculate the first 1-2 elements before the loop. <br> **陷阱：** 忘記 $i=0$ 或 $i=1$。 <br> **解法：** 總是在迴圈前手動計算前 1-2 個元素。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Framework: REACT (Repeat, Examples, Approach, Code, Test)
*   **Approach Phase:** Do not jump to DP immediately. Say: "This looks like an optimization problem involving choices. I see overlapping subproblems, so DP might be suitable."
    **方法階段：** 不要立刻跳到 DP。說：「這看起來像是一個涉及選擇的優化問題。我看到了重疊子問題，所以 DP 可能很適合。」

### 2. Whiteboard Strategy (白板策略)
*   Write $dp[i] = \dots$ clearly on the board/screen before coding.
    在寫程式碼之前，先在白板/螢幕上清楚寫下 $dp[i] = \dots$。
*   Draw a small table for inputs like `[1, 2, 3, 1]` to trace the values.
    畫一個小表格來追蹤輸入（如 `[1, 2, 3, 1]`）的數值變化。

### 3. Common Follow-ups (常見追問)
*   **Q:** Can you optimize the space?
    **問：** 你能優化空間嗎？
    *   **A:** Yes, use rolling variables (as shown in the example).
    *   **答：** 可以，使用滾動變數（如範例所示）。
*   **Q:** What if the houses are arranged in a circle? (House Robber II)
    **問：** 如果房子排成一圈怎麼辦？（打家劫舍 II）
    *   **A:** Run the linear DP twice: once from $0 \to n-2$, once from $1 \to n-1$, and take the max.
    *   **答：** 執行兩次線性 DP：一次從 $0 \to n-2$，一次從 $1 \to n-1$，然後取最大值。

---

## 7. Practice Problems（練習題）

### Easy: Climbing Stairs (爬樓梯)
*   **Prompt:** Count ways to reach step $n$ if you can take 1 or 2 steps.
    **題目：** 如果你可以走 1 步或 2 步，計算到達第 $n$ 階的方法數。
*   **Hint:** It is exactly the Fibonacci sequence. $dp[i] = dp[i-1] + dp[i-2]$.
    **提示：** 這完全就是費氏數列。$dp[i] = dp[i-1] + dp[i-2]$。

### Medium: Decode Ways (解碼方法)
*   **Prompt:** Given a string of digits, count how many ways to decode it to letters (A=1, B=2...Z=26).
    **題目：** 給定一個數字字串，計算有多少種方法將其解碼為字母（A=1, B=2...Z=26）。
*   **Hint:** Handle '0' carefully. $dp[i]$ depends on single digit valid check ($dp[i-1]$) and two-digit valid check ($dp[i-2]$).
    **提示：** 小心處理 '0'。$dp[i]$ 取決於單個數字是否有效 ($dp[i-1]$) 和兩個數字組合是否有效 ($dp[i-2]$)。

### Hard (for this level): Coin Change (零錢兌換)
*   **Prompt:** Fewest coins to make up amount $k$.
    **題目：** 湊成金額 $k$ 所需的最少硬幣數量。
*   **Hint:** $dp[i] = \min(dp[i - coin]) + 1$ for all coins. Initialize array with Infinity.
    **提示：** 對於所有硬幣，$dp[i] = \min(dp[i - coin]) + 1$。將陣列初始化為無限大。

---

## 8. Quick Checklists（快速檢核表）

Use this during your interview coding phase:
在面試寫程式階段使用此表：

- [ ] **State Definition:** Does $dp[i]$ mean "result ending at $i$" or "result up to $i$"?
    **狀態定義：** $dp[i]$ 是指「以 $i$ 結尾的結果」還是「截至 $i$ 的結果」？
- [ ] **Base Cases:** Did I handle $n=0, n=1$ explicitly?
    **基礎情況：** 我是否明確處理了 $n=0, n=1$？
- [ ] **Array Bounds:** Will `dp[i-2]` crash when `i=1`?
    **陣列邊界：** 當 `i=1` 時，`dp[i-2]` 會崩潰嗎？
- [ ] **Return Value:** Should I return `dp[n]` or `dp[n-1]`?
    **回傳值：** 我應該回傳 `dp[n]` 還是 `dp[n-1]`？

---

## 9. Memory Anchors（記憶錨點）

*   **The "Domino" Analogy:**
    **「骨牌」類比：**
    To knock down the $i$-th domino, you rely on the force from the $(i-1)$-th. DP is just setting up the dominos so the answer falls into place automatically.
    要推倒第 $i$ 個骨牌，你依賴於第 $(i-1)$ 個骨牌的力量。DP 就是排列骨牌，讓答案自動顯現。

*   **The "Toll Booth" Analogy (Min Cost):**
    **「收費站」類比（最小花費）：**
    You are driving on a highway. At each mile marker, you look in the rearview mirror to see which previous toll booth was cheaper to come from.
    你在高速公路上開車。在每個里程碑，你看看後視鏡，看從哪個之前的收費站過來比較便宜。