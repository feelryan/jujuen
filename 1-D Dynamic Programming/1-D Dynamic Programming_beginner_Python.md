
# 1-D Dynamic Programming: From Recursion to Optimization
# 一維動態規劃：從遞迴到優化

## 1. Learning Objectives (學習目標)

*   **Understand the "Overlapping Subproblems" property.**
    理解「重疊子問題」的特性。
*   **Master the transition from Top-Down Recursion to Bottom-Up Tabulation.**
    掌握從「由上而下的遞迴」轉換為「由下而上的列表法」的技巧。
*   **Learn to identify the Recurrence Relation (State Transition Equation).**
    學會識別遞迴關係式（狀態轉移方程式）。
*   **Optimize Space Complexity from $O(N)$ to $O(1)$ where applicable.**
    在適用情況下，將空間複雜度從 $O(N)$ 優化至 $O(1)$。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Dynamic Programming (DP) is a method for solving complex problems by breaking them down into simpler subproblems, solving each of those subproblems just once, and storing their solutions.
動態規劃（DP）是一種透過將複雜問題分解為較簡單的子問題，每個子問題僅解決一次並儲存其解，來解決問題的方法。

### Intuition (直覺)
Think of it as "Recursion with Caching" or "Filling a table based on previous entries."
可以將其視為「帶有快取的遞迴」或「基於先前的項目來填表」。

### Complexity (複雜度)
*   **Time:** Usually reduces exponential time $O(2^n)$ (brute force recursion) to linear time $O(n)$ or polynomial time.
    **時間：** 通常將指數時間 $O(2^n)$（暴力遞迴）降低至線性時間 $O(n)$ 或多項式時間。
*   **Space:** Typically $O(n)$ for the DP table, often optimizable to $O(1)$ in 1-D problems.
    **空間：** DP 表通常需要 $O(n)$，在一維問題中常可優化至 $O(1)$。

### When to Use (適用場景)
1.  **Overlapping Subproblems:** The problem can be broken down into subproblems which are reused several times.
    **重疊子問題：** 問題可以分解為被多次重複使用的子問題。
2.  **Optimal Substructure:** An optimal solution to the problem contains within it optimal solutions to subproblems.
    **最佳子結構：** 問題的最佳解包含其子問題的最佳解。

### When NOT to Use (不適用場景)
*   If the subproblems do not overlap (use Divide and Conquer, e.g., Merge Sort).
    如果子問題不重疊（使用分治法，例如合併排序）。
*   If a local optimal choice always leads to a global optimum (use Greedy).
    如果局部最佳選擇總是導致全域最佳解（使用貪婪演算法）。

---

## 3. Typical Patterns (典型題型 / 模式)

For 1-D DP (Beginner), patterns usually fall into:
對於一維 DP（初級），模式通常分為：

1.  **Linear Recurrence (Fibonacci Style):**
    **線性遞迴（費氏數列風格）：**
    $dp[i] = dp[i-1] + dp[i-2]$
    *(e.g., Climbing Stairs)*

2.  **Cost Accumulation:**
    **成本累積：**
    $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$
    *(e.g., Min Cost Climbing Stairs)*

3.  **Choice at Step i (Include or Exclude):**
    **步驟 i 的選擇（包含或排除）：**
    $dp[i] = \max(dp[i-1], \text{val}[i] + dp[i-2])$
    *(e.g., House Robber)*

---

## 4. Example Walkthrough (範例講解)

### Problem: Climbing Stairs (爬樓梯)
**Problem Statement:**
You are climbing a staircase. It takes `n` steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?
**問題重述：**
你正在爬樓梯。需要 `n` 階才能到達頂端。每次你可以爬 1 或 2 階。你有多少種不同的方法可以爬到頂端？

---

### Phase 1: Brute Force Recursion (暴力遞迴)
**Idea:** To reach step $n$, we could have come from $n-1$ or $n-2$.
**思路：** 要到達第 $n$ 階，我們可能來自 $n-1$ 階或 $n-2$ 階。

```python
def climbStairs_recursive(n: int) -> int:
    # Base cases: If n is 0 or 1, there is only 1 way (doing nothing or taking 1 step)
    # 基本情況：如果 n 為 0 或 1，只有 1 種方法（不做任何事或走 1 步）
    if n <= 1:
        return 1
    
    # Recurrence: sum of ways to reach n-1 and n-2
    # 遞迴關係：到達 n-1 和 n-2 的方法總和
    return climbStairs_recursive(n - 1) + climbStairs_recursive(n - 2)
```
**Critique:** Time Complexity is $O(2^n)$. This will TLE (Time Limit Exceeded) for $n=45$.
**評論：** 時間複雜度為 $O(2^n)$。當 $n=45$ 時會超時（TLE）。

---

### Phase 2: Recursion with Memoization (Top-Down DP) (遞迴加記憶化)
**Idea:** Store the result of each step so we don't recalculate.
**思路：** 儲存每一步的結果，這樣我們就不必重新計算。

```python
def climbStairs_memo(n: int) -> int:
    memo = {}
    
    def helper(i: int) -> int:
        if i <= 1:
            return 1
        if i in memo:
            return memo[i]
        
        # Store result in memo before returning
        # 返回前將結果存入 memo
        memo[i] = helper(i - 1) + helper(i - 2)
        return memo[i]
        
    return helper(n)
```
**Complexity:** Time $O(n)$, Space $O(n)$ (recursion stack + hash map).
**複雜度：** 時間 $O(n)$，空間 $O(n)$（遞迴堆疊 + 雜湊表）。

---

### Phase 3: Tabulation (Bottom-Up DP) (列表法)
**Idea:** Iteratively fill an array from base cases up to `n`. This avoids recursion overhead.
**思路：** 迭代地從基本情況填入陣列直到 `n`。這避免了遞迴的開銷。

```python
def climbStairs_tabulation(n: int) -> int:
    if n <= 1:
        return 1
    
    # Initialize DP array
    # 初始化 DP 陣列
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    
    # Fill table
    # 填表
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        
    return dp[n]
```
**Complexity:** Time $O(n)$, Space $O(n)$.
**複雜度：** 時間 $O(n)$，空間 $O(n)$。

---

### Phase 4: Space Optimization (空間優化) - **The Best Solution**
**Idea:** We only need the previous two values (`dp[i-1]` and `dp[i-2]`) to calculate the current one. We don't need the whole array.
**思路：** 我們只需要前兩個值（`dp[i-1]` 和 `dp[i-2]`）來計算當前值。我們不需要整個陣列。

```python
def climbStairs_optimal(n: int) -> int:
    if n <= 1:
        return 1
    
    # prev2 represents dp[i-2], prev1 represents dp[i-1]
    # prev2 代表 dp[i-2]，prev1 代表 dp[i-1]
    prev2, prev1 = 1, 1
    
    for _ in range(2, n + 1):
        current = prev1 + prev2
        # Shift the window
        # 移動視窗
        prev2 = prev1
        prev1 = current
        
    return prev1
```
**Complexity:** Time $O(n)$, Space $O(1)$.
**複雜度：** 時間 $O(n)$，空間 $O(1)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Base Case Initialization** | **Pitfall:** Initializing `dp[0]` or `dp[1]` incorrectly breaks the chain. Always manually verify $n=0, 1, 2$.<br>**陷阱：** 錯誤初始化 `dp[0]` 或 `dp[1]` 會破壞鏈條。務必手動驗證 $n=0, 1, 2$。 |
| **Off-by-one Errors** | **Pitfall:** Array size should often be `n + 1` to accommodate the 0-th index to the n-th index.<br>**陷阱：** 陣列大小通常應為 `n + 1`，以容納第 0 個索引到第 n 個索引。 |
| **Greedy vs. DP** | **Confusion:** Greedy makes the locally optimal choice. DP explores all necessary combinations (via subproblems).<br>**混淆：** 貪婪法做出局部最佳選擇。DP 探索所有必要的組合（透過子問題）。 |
| **State Definition** | **Pitfall:** Not clearly defining what `dp[i]` represents (e.g., "max profit ending at day i" vs "max profit up to day i").<br>**陷阱：** 沒有清楚定義 `dp[i]` 代表什麼（例如，「第 i 天結束時的最大利潤」與「截至第 i 天的最大利潤」）。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. The Framework (口條框架)
*   **Identify:** "This looks like a problem where future decisions depend on past results, suggesting DP."
    **識別：** 「這看起來像是一個未來的決策取決於過去結果的問題，暗示使用 DP。」
*   **Define State:** "Let `dp[i]` be the number of ways to reach step `i`."
    **定義狀態：** 「設 `dp[i]` 為到達第 `i` 階的方法數。」
*   **Recurrence:** "To get to `i`, I must come from `i-1` or `i-2`."
    **遞迴關係：** 「要到達 `i`，我必須來自 `i-1` 或 `i-2`。」

### 2. Whiteboard Strategy (白板策略)
*   Don't jump to $O(1)$ space immediately. Write the $O(N)$ space solution first (it's easier to debug).
    不要立刻跳到 $O(1)$ 空間解法。先寫出 $O(N)$ 空間的解法（較易除錯）。
*   Draw a small array `[0, 1, 2, 3, 4]` and fill in values manually to verify logic.
    畫一個小陣列 `[0, 1, 2, 3, 4]` 並手動填入數值以驗證邏輯。

### 3. Common Follow-ups (常見追問)
*   "What if you can climb 1, 2, or 3 steps?" (Change recurrence to sum of last 3).
    「如果你可以爬 1、2 或 3 階呢？」（將遞迴關係改為前三項之和）。
*   "What if the stairs have costs?" (Min Cost Climbing Stairs).
    「如果樓梯有成本呢？」（最小成本爬樓梯）。
*   "How to handle huge `n`?" (Matrix Exponentiation $O(\log n)$ - Advanced).
    「如何處理巨大的 `n`？」（矩陣快速冪 $O(\log n)$ - 進階）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Min Cost Climbing Stairs (最小成本爬樓梯)
*   **Hint:** $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$. Watch out for where you start (index 0 or 1).
    **提示：** $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$。注意從哪裡開始（索引 0 或 1）。
*   **Focus:** Cost accumulation.
    **重點：** 成本累積。

### 2. Medium: House Robber (打家劫舍)
*   **Hint:** You cannot rob adjacent houses. $dp[i] = \max(\text{rob current} + dp[i-2], \text{skip current} + dp[i-1])$.
    **提示：** 不能搶劫相鄰的房子。$dp[i] = \max(\text{搶當前} + dp[i-2], \text{跳過當前} + dp[i-1])$。
*   **Focus:** The "Include/Exclude" pattern.
    **重點：** 「包含/排除」模式。

### 3. Hard (for this level): Decode Ways (解碼方法)
*   **Hint:** 'A'=1, 'B'=2... 'Z'=26. Similar to climbing stairs, but with conditions. Check if single digit is valid (1-9) and if double digit is valid (10-26). Handle '0' carefully.
    **提示：** 'A'=1, 'B'=2... 'Z'=26。類似爬樓梯，但有條件限制。檢查單個數字是否有效（1-9）以及兩個數字是否有效（10-26）。小心處理 '0'。
*   **Focus:** Conditional transitions.
    **重點：** 條件式轉移。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **State Definition:** Can I articulate exactly what `dp[i]` stores?
    **狀態定義：** 我能確切說明 `dp[i]` 儲存什麼嗎？
*   [ ] **Base Cases:** Did I handle `i=0` and `i=1`?
    **基本情況：** 我處理了 `i=0` 和 `i=1` 嗎？
*   [ ] **Transitions:** Does `dp[i]` depend on `i+1` (wrong direction) or `i-1` (correct)?
    **轉移：** `dp[i]` 是依賴 `i+1`（方向錯誤）還是 `i-1`（正確）？
*   [ ] **Result:** Is the answer in `dp[n]` or `dp[n-1]`?
    **結果：** 答案是在 `dp[n]` 還是 `dp[n-1]`？

---

## 9. Memory Anchors (記憶錨點)

### The "Form Filling" Analogy (「填表」類比)
Imagine you are a bureaucrat filling out a tax form. Line 5 says "Add Line 3 and Line 4". You don't re-calculate Line 3 from scratch; you just look at the number you already wrote there.
想像你是一個正在填寫稅務表格的官僚。第 5 行說「將第 3 行和第 4 行相加」。你不會從頭重新計算第 3 行；你只會看你已經寫在那裡的數字。

### The "Domino" Visual (「骨牌」視覺)
1-D DP is like a line of dominoes. To knock down the $i$-th domino, the force must come from the $(i-1)$-th domino. You push the first one (Base Case), and the logic propagates to the end.
一維 DP 就像一排骨牌。要推倒第 $i$ 個骨牌，力量必須來自第 $(i-1)$ 個骨牌。你推倒第一個（基本情況），邏輯就會傳遞到最後。