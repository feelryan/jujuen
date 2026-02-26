# 1-D Dynamic Programming (Intermediate)
# 一維動態規劃（中階）

## 1. Learning Objectives（學習目標）

1.  **Master the "State Definition":** Learn to define $dp[i]$ precisely (e.g., "max profit ending at day $i$" vs. "max profit up to day $i$").
    **掌握「狀態定義」：** 學習精確定義 $dp[i]$（例如：「在第 $i$ 天結束時的最大利潤」與「截至第 $i$ 天為止的最大利潤」的區別）。

2.  **Transition from Recursion to Iteration:** Move confidently from Top-Down Memoization to Bottom-Up Tabulation to demonstrate architectural thinking.
    **從遞迴轉向迭代：** 自信地從「由上而下的記憶法」轉換為「由下而上的列表法」，以展現架構思維。

3.  **Space Optimization:** Identify when the dependency window is fixed (e.g., $i$ depends only on $i-1$ and $i-2$) to reduce space complexity from $O(N)$ to $O(1)$.
    **空間優化：** 識別依賴窗口何時是固定的（例如 $i$ 僅依賴 $i-1$ 和 $i-2$），將空間複雜度從 $O(N)$ 降至 $O(1)$。

4.  **Distinguish Greedy vs. DP:** Understand why local optima do not always lead to global optima in DP problems.
    **區分貪婪演算法與動態規劃：** 理解為何在動態規劃問題中，局部最佳解並不總能導向全域最佳解。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
**Definition:** 1-D DP solves problems by breaking them into overlapping subproblems where the state depends linearly on an index (usually $i$).
**定義：** 一維動態規劃透過將問題分解為重疊的子問題來求解，其狀態通常線性依賴於索引（通常是 $i$）。

**Intuition:** It's "smart recursion" or "mathematical induction". Instead of recalculating, we use history.
**直覺：** 這是「聰明的遞迴」或「數學歸納法」。我們利用歷史紀錄，而非重新計算。

### Complexity（複雜度）
-   **Time:** Typically $O(N)$ (linear scan) or $O(N^2)$ (nested dependency, like LIS).
    **時間：** 通常為 $O(N)$（線性掃描）或 $O(N^2)$（巢狀依賴，如最長遞增子序列）。
-   **Space:** $O(N)$ for the DP array, often optimizable to $O(1)$ if we only need the last $k$ values.
    **空間：** DP 陣列為 $O(N)$，若我們只需要最後 $k$ 個值，通常可優化至 $O(1)$。

### When to Use / Not to Use（適用與不適用場景）

| Scenario | Description (敘述) |
| :--- | :--- |
| **Use (適用)** | **Extremums (極值):** Max/Min cost, profit, or path.<br>**Counting (計數):** Number of ways to reach a target.<br>**Existence (存在性):** Can we reach index $N$? |
| **Not Use (不適用)** | **Cyclic Dependencies (循環依賴):** Requires Graph algorithms (BFS/Dijkstra).<br>**No Overlapping Subproblems (無重疊子問題):** Divide and Conquer (e.g., Merge Sort) is better.<br>**Simple Greedy (簡單貪婪):** If taking the immediate best step works (e.g., Activity Selection). |

---

## 3. Typical Patterns（典型題型 / 模式）

### A. The "Fibonacci" Pattern (Fixed Window)
**「費波那契」模式（固定窗口）**
-   **Relation:** $dp[i]$ depends on $dp[i-1], dp[i-2]$.
-   **關係式：** $dp[i]$ 依賴於 $dp[i-1], dp[i-2]$。
-   **Examples:** Climbing Stairs, House Robber.
-   **範例：** 爬樓梯、打家劫舍。

### B. The "Choice" Pattern (Take or Skip)
**「選擇」模式（選或不選）**
-   **Relation:** $dp[i] = \max(dp[i-1], \text{value}[i] + dp[i-k])$.
-   **關係式：** $dp[i] = \max(dp[i-1], \text{value}[i] + dp[i-k])$。
-   **Logic:** At step $i$, do we include this element or carry over the previous best?
-   **邏輯：** 在步驟 $i$，我們是包含這個元素，還是延續之前的最佳結果？

### C. The "Ending Here" Pattern (LIS Style)
**「以此為結尾」模式（LIS 風格）**
-   **Relation:** $dp[i] = \max(dp[j]) + 1$ for all $0 \le j < i$ where condition meets.
-   **關係式：** 對於所有符合條件的 $0 \le j < i$， $dp[i] = \max(dp[j]) + 1$。
-   **Complexity:** Usually $O(N^2)$.
-   **複雜度：** 通常為 $O(N^2)$。

---

## 4. Example Walkthrough（範例講解）

### Problem: House Robber (Medium)
### 問題：打家劫舍（中等）

**Problem Statement:**
You are a robber planning to rob houses along a street. Adjacent houses have security systems connected. You cannot rob two adjacent houses. Given an integer array `nums` representing the amount of money of each house, return the *maximum amount* you can rob.
**問題重述：**
你是一個計劃沿街搶劫房屋的強盜。相鄰的房屋有連接的保全系統。你不能搶劫兩間相鄰的房屋。給定一個整數陣列 `nums` 代表每間房子的金額，回傳你能搶到的 *最大金額*。

---

### Phase 1: The Thought Process (思路)

**1. Brute Force (Recursion):**
For each house $i$, we have two choices: rob it (and skip $i+1$, move to $i+2$) or skip it (move to $i+1$).
**暴力解（遞迴）：**
對於每間房子 $i$，我們有兩個選擇：搶它（跳過 $i+1$，移動到 $i+2$）或跳過它（移動到 $i+1$）。
*Complexity:* $O(2^N)$ - Exponential, will Time Out (TLE).
*複雜度：* $O(2^N)$ - 指數級，會超時 (TLE)。

**2. Optimization (DP State):**
Let $dp[i]$ be the max money we can rob from the first $i$ houses.
**優化（DP 狀態）：**
令 $dp[i]$ 為從前 $i$ 間房子能搶到的最大金額。

**3. Recurrence Relation (轉移方程式):**
$$dp[i] = \max(\underbrace{dp[i-1]}_{\text{Skip house } i}, \underbrace{nums[i] + dp[i-2]}_{\text{Rob house } i})$$

---

### Phase 2: Python Solution (Best Practice)
### 階段二：Python 解答（最佳實踐）

```python
from typing import List

class Solution:
    def rob(self, nums: List[int]) -> int:
        # Edge case: No houses
        # 邊界情況：沒有房子
        if not nums:
            return 0
        
        # Edge case: Only one house
        # 邊界情況：只有一間房子
        if len(nums) == 1:
            return nums[0]
        
        # -------------------------------------------
        # Approach 1: Tabulation (O(N) Space)
        # 方法一：列表法 (O(N) 空間)
        # -------------------------------------------
        n = len(nums)
        # dp[i] represents max profit considering houses 0 to i
        # dp[i] 代表考慮房屋 0 到 i 時的最大利潤
        dp = [0] * n
        
        # Base cases
        # 基礎情況
        dp[0] = nums[0]
        dp[1] = max(nums[0], nums[1])
        
        for i in range(2, n):
            # Decision: Skip current vs. Rob current + previous non-adjacent best
            # 決策：跳過當前 vs. 搶當前 + 前一個非相鄰的最佳結果
            dp[i] = max(dp[i-1], nums[i] + dp[i-2])
            
        # return dp[n-1]  <-- This is the O(N) space answer
        
        # -------------------------------------------
        # Approach 2: Space Optimization (O(1) Space)
        # 方法二：空間優化 (O(1) 空間)
        # -------------------------------------------
        
        # We only need the previous two values to calculate the current one.
        # 我們只需要前兩個值來計算當前值。
        prev2 = nums[0]             # Equivalent to dp[i-2]
        prev1 = max(nums[0], nums[1]) # Equivalent to dp[i-1]
        
        for i in range(2, n):
            current = max(prev1, nums[i] + prev2)
            
            # Shift the window
            # 移動窗口
            prev2 = prev1
            prev1 = current
            
        return prev1
```

### Complexity Analysis（複雜度分析）
-   **Time:** $O(N)$ — We iterate through the array once.
    **時間：** $O(N)$ — 我們遍歷陣列一次。
-   **Space:** $O(1)$ — We only store two variables (`prev1`, `prev2`).
    **空間：** $O(1)$ — 我們只儲存兩個變數（`prev1`, `prev2`）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

### 1. Indexing Hell (索引地獄)
-   **Pitfall:** Defining $dp$ array size as `len(nums)` but trying to access `dp[i-2]` when `i=1`.
-   **陷阱：** 將 $dp$ 陣列大小定義為 `len(nums)`，但在 `i=1` 時嘗試存取 `dp[i-2]`。
-   **Fix:** Either handle base cases explicitly (as in the code above) or pad the DP array (size $N+1$) to handle offsets gracefully.
-   **修正：** 明確處理基礎情況（如上述代碼），或填充 DP 陣列（大小為 $N+1$）以優雅地處理偏移。

### 2. Greedy vs. DP (貪婪與動態規劃)
-   **Confusion:** "Why not just pick the largest house, then the next valid largest?"
-   **混淆：** 「為什麼不直接選最大的房子，然後選下一個合法的最大房子？」
-   **Counter-example:** `[10, 20, 15, 100]`.
    -   Greedy (pick max 100): `100 + 20 = 120`.
    -   DP (Global optimal): `10 + 15` is bad... wait, actually `10 + 100 = 110`.
    -   Let's try `[2, 10, 10, 2]`. Greedy picks 10 (index 1), leaving index 3 (2). Total 12. Optimal: 10 (index 1) + 2? No, Optimal is 10+10? No, adjacent.
    -   Better example: `[100, 1, 1, 100]`.
    -   Greedy might pick first 100, then last 100. Total 200.
    -   Wait, Greedy usually means "locally optimal choice".
    -   Example `[5, 5, 10, 100, 10, 5]`.
    -   Greedy at step 0: Pick 5? Or look ahead?
    -   **Key:** Greedy makes a choice and *never looks back*. DP explores all relevant combinations implicitly.
-   **關鍵：** 貪婪演算法做出選擇後*絕不回頭*。動態規劃則隱式地探索所有相關組合。

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework (口條框架)
1.  **Define the State:** "I will define `dp[i]` as the maximum value achievable considering elements up to index `i`."
    **定義狀態：** 「我將 `dp[i]` 定義為考慮到索引 `i` 為止所能達到的最大值。」
2.  **Establish Recurrence:** "To calculate `dp[i]`, I have two choices..."
    **建立遞迴關係：** 「為了計算 `dp[i]`，我有兩個選擇……」
3.  **Discuss Base Cases:** "The recursion bottoms out when..."
    **討論基礎情況：** 「遞迴在……時終止。」

### Whiteboard Strategy (白板策略)
-   Draw a 1-D array box. Fill the first few indices manually with the interviewer.
-   畫一個一維陣列方框。與面試官一起手動填寫前幾個索引。
-   Write the transition equation **before** writing code. This is your contract.
-   在寫程式碼**之前**先寫出轉移方程式。這是你的契約。

### Common Follow-ups (常見追問)
-   "Can you optimize the space?" (Hint: $O(1)$ sliding window).
    「你能優化空間嗎？」（提示：$O(1)$ 滑動窗口）。
-   "What if the houses are arranged in a circle?" (Hint: Run DP twice, once $0 \to n-2$, once $1 \to n-1$).
    「如果房子排成一圈呢？」（提示：執行兩次 DP，一次 $0 \to n-2$，一次 $1 \to n-1$）。

---

## 7. Practice Problems（練習題）

### Easy: Climbing Stairs / Min Cost Climbing Stairs
**簡單：爬樓梯 / 使用最小花費爬樓梯**
-   **Hint:** $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$.
-   **提示：** $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$。

### Medium: Maximum Product Subarray
**中等：最大乘積子陣列**
-   **Hint:** Keep track of both `max_so_far` and `min_so_far` because a negative number multiplied by a negative `min` becomes a positive `max`.
-   **提示：** 同時追蹤 `max_so_far` 和 `min_so_far`，因為負數乘以負的 `min` 會變成正的 `max`。
-   **Core Skill:** Handling state that requires more than just one value (current max and current min).
-   **核心技能：** 處理需要不只一個值（當前最大值與當前最小值）的狀態。

### Hard: Longest Increasing Subsequence (LIS)
**困難：最長遞增子序列**
-   **Hint:** $dp[i]$ = length of LIS ending at index $i$. Nested loop required for basic DP ($O(N^2)$).
-   **提示：** $dp[i]$ = 以索引 $i$ 結尾的 LIS 長度。基本 DP 需要巢狀迴圈 ($O(N^2)$)。
-   **Follow-up:** Optimize to $O(N \log N)$ using Binary Search (Patience Sorting).
-   **追問：** 使用二分搜尋法（Patience Sorting）優化至 $O(N \log N)$。

---

## 8. Quick Checklists（快速檢核表）

**Self-Review before saying "I'm done":**
**在說「我完成了」之前的自我審查：**

-   [ ] **Base Cases:** Did I handle $N=0, N=1, N=2$?
    **基礎情況：** 我處理了 $N=0, N=1, N=2$ 嗎？
-   [ ] **Initialization:** Is the DP array initialized correctly (0, -1, or -infinity)?
    **初始化：** DP 陣列初始化正確嗎（0、-1 或負無限大）？
-   [ ] **Loop Bounds:** Does the loop range `range(2, n)` cover the last element?
    **迴圈邊界：** 迴圈範圍 `range(2, n)` 是否涵蓋了最後一個元素？
-   [ ] **Return Value:** Am I returning `dp[-1]` or `max(dp)`? (Depends on problem type).
    **回傳值：** 我是回傳 `dp[-1]` 還是 `max(dp)`？（取決於問題類型）。

---

## 9. Memory Anchors（記憶錨點）

### The "Domino Effect" (骨牌效應)
Visualize 1-D DP as knocking down dominoes. To knock down the $i$-th domino (calculate state $i$), the energy comes from the previous dominoes ($i-1, i-2$). You cannot calculate $i$ without the momentum from the past.
將一維動態規劃想像成推倒骨牌。要推倒第 $i$ 張骨牌（計算狀態 $i$），能量來自前面的骨牌（$i-1, i-2$）。沒有過去的動量，你無法計算 $i$。

### The "Telescope" (望遠鏡)
Space optimization is like a collapsing telescope. Even though the telescope is long (size $N$), when you look through it, you only focus on the lens right in front of your eye (size $O(1)$). You discard the parts you've already passed.
空間優化就像一個可伸縮的望遠鏡。雖然望遠鏡很長（大小 $N$），但當你透過它觀看時，你只專注於眼前的那片鏡片（大小 $O(1)$）。你丟棄了已經經過的部分。