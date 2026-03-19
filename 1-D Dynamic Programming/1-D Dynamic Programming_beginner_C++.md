Here is the complete interview preparation guide for **1-D Dynamic Programming**, tailored for a Senior Software Engineer, at the **Beginner** depth level, using **C++**.

這是一份針對 **一維動態規劃（1-D Dynamic Programming）** 的完整面試準備指南，專為資深軟體工程師設計，深度設定為 **初學者（Beginner）**，並使用 **C++** 撰寫。

---

# 1-D Dynamic Programming: Interview Guide (Beginner Level)
# 一維動態規劃：面試指南（初學者級）

## 1. Learning Goals (學習目標)

*   **Understand the Core of DP:** Move from "intuition" to "formal definition" by understanding overlapping subproblems and optimal substructure.
    **理解 DP 核心：** 通過理解重疊子問題和最優子結構，從「直覺」過渡到「形式化定義」。
*   **Master the "State" & "Transition":** Learn to define `dp[i]` clearly and derive the recurrence relation $dp[i] = f(dp[i-1], ...)$.
    **掌握「狀態」與「轉移」：** 學會清晰定義 `dp[i]` 並推導遞迴關係式 $dp[i] = f(dp[i-1], ...)$。
*   **Space Optimization:** Learn how to reduce Space Complexity from $O(N)$ to $O(1)$ in 1-D problems.
    **空間優化：** 學習如何在一維問題中將空間複雜度從 $O(N)$ 降低到 $O(1)$。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Dynamic Programming is an optimization technique that solves complex problems by breaking them down into simpler subproblems and storing their solutions to avoid redundant computations.
動態規劃是一種優化技術，通過將複雜問題分解為更簡單的子問題並儲存其解，以避免重複計算來解決問題。

In **1-D DP**, the state of the problem depends on a single variable, typically the index $i$ of an array or a sequence.
在 **一維 DP** 中，問題的狀態取決於單個變量，通常是陣列或序列的索引 $i$。

### Intuition (直覺)
"Those who cannot remember the past are condemned to repeat it." — DP is about remembering the past (memoization/tabulation) to solve the future.
「記不住過去的人註定要重蹈覆轍。」— DP 就是關於記住過去（記憶化/列表法）以解決未來。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$, where $N$ is the length of the input. We calculate each state once.
    **時間：** 通常是 $O(N)$，其中 $N$ 是輸入的長度。我們計算每個狀態一次。
*   **Space:** Naively $O(N)$ to store the DP table, but often optimizable to $O(1)$ if we only need the previous $k$ values.
    **空間：** 儲存 DP 表通常需要 $O(N)$，但如果我們只需要前 $k$ 個值，通常可以優化為 $O(1)$。

### When to Use (適用場景)
*   **Counting:** "How many ways to reach step N?"
    **計數：** 「有多少種方法到達第 N 階？」
*   **Min/Max:** "Minimum cost to reach the end" or "Maximum profit from robbing houses."
    **極值：** 「到達終點的最小成本」或「搶劫房屋的最大利潤」。
*   **Dependency:** The decision at index $i$ depends only on previous indices ($i-1, i-2, ...$).
    **依賴性：** 在索引 $i$ 的決策僅取決於先前的索引（$i-1, i-2, ...$）。

### When NOT to Use (不適用場景)
*   If the data is not ordered or sequential (might need Graph algorithms or 2-D DP).
    如果數據沒有順序或序列性（可能需要圖算法或二維 DP）。
*   If the problem asks for *all* valid permutations/subsets (usually Backtracking).
    如果問題要求列出 *所有* 有效的排列/子集（通常是回溯法）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Linear Recurrence (線性遞迴)
The value at $i$ depends on a fixed number of previous values.
$i$ 處的值取決於固定數量的先前值。
*   *Equation:* $dp[i] = dp[i-1] + dp[i-2]$
*   *Example:* Climbing Stairs, Fibonacci.

### Pattern 2: Cost Accumulation (成本累積)
We want to minimize or maximize the cost to arrive at $i$.
我們希望最小化或最大化到達 $i$ 的成本。
*   *Equation:* $dp[i] = cost[i] + \min(dp[i-1], dp[i-2])$
*   *Example:* Min Cost Climbing Stairs.

### Pattern 3: Choice/State Machine (選擇/狀態機)
At each step, you have a binary choice (e.g., pick or skip), often with constraints (cannot pick adjacent).
在每一步，你有一個二元選擇（例如：選或不選），通常帶有約束（不能選相鄰的）。
*   *Equation:* $dp[i] = \max(dp[i-1], \text{value}[i] + dp[i-2])$
*   *Example:* House Robber.

---

## 4. Example Walkthrough (範例講解)

### Problem: Climbing Stairs (爬樓梯)
**Problem Statement:**
You are climbing a staircase. It takes $n$ steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?
**問題重述：**
你正在爬樓梯。需要 $n$ 階才能到達頂端。每次你可以爬 1 或 2 個階梯。你有多少種不同的方法可以爬到頂端？

### Approach (思路)

1.  **Brute Force (Recursion):**
    Try every combination. This creates a binary tree of height $n$.
    **暴力法（遞迴）：** 嘗試每一種組合。這會產生一個高度為 $n$ 的二元樹。
    *   Complexity: $O(2^n)$ (Time Limit Exceeded).

2.  **DP (Tabulation):**
    To reach step $i$, we must have come from step $i-1$ (1 step jump) or step $i-2$ (2 step jump).
    **DP（列表法）：** 要到達第 $i$ 階，我們必須來自第 $i-1$ 階（跳 1 階）或第 $i-2$ 階（跳 2 階）。
    *   State: $dp[i]$ = ways to reach step $i$.
    *   Transition: $dp[i] = dp[i-1] + dp[i-2]$.
    *   Base Cases: $dp[1] = 1$, $dp[2] = 2$.

3.  **Optimization:**
    We only need the last two values. We don't need the whole array.
    **優化：** 我們只需要最後兩個值。我們不需要整個陣列。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <iostream>

class Solution {
public:
    // Method 1: Standard DP Array (Space O(N))
    // 方法一：標準 DP 陣列（空間 O(N)）
    int climbStairsStandard(int n) {
        if (n <= 2) return n; // Base cases handling / 基礎情況處理
        
        // dp[i] stores the number of ways to reach step i
        // dp[i] 儲存到達第 i 階的方法數
        std::vector<int> dp(n + 1);
        dp[1] = 1;
        dp[2] = 2;
        
        for (int i = 3; i <= n; ++i) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        
        return dp[n];
    }

    // Method 2: Space Optimized (Space O(1)) - Recommended for Senior Level
    // 方法二：空間優化（空間 O(1)）- 資深級別推薦
    int climbStairsOptimized(int n) {
        // Edge cases are crucial in interviews
        // 邊界情況在面試中至關重要
        if (n <= 2) return n;

        int prev2 = 1; // Represents dp[i-2] / 代表 dp[i-2]
        int prev1 = 2; // Represents dp[i-1] / 代表 dp[i-1]
        
        for (int i = 3; i <= n; ++i) {
            int current = prev1 + prev2;
            
            // Shift the window for the next iteration
            // 為下一次迭代移動視窗
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ — We iterate from 3 to $N$ once.
    **時間：** $O(N)$ — 我們從 3 迭代到 $N$ 一次。
*   **Space:** $O(1)$ — We only use two integer variables (`prev1`, `prev2`).
    **空間：** $O(1)$ — 我們只使用了兩個整數變數（`prev1`, `prev2`）。

### Common Mistake (錯誤示範)
```cpp
// Mistake: Greedy Approach
// 錯誤：貪婪法
// Thinking: "I should always take the biggest step possible."
// 想法：「我應該總是盡可能跨大步。」
// This fails because it doesn't count ALL ways, just one specific path.
// 這會失敗，因為它沒有計算「所有」方法，只計算了一條特定路徑。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Greedy vs. DP** | **Greedy** makes the locally optimal choice at each step hoping for a global optimum (often fails for counting paths). **DP** considers all relevant past states to make a decision. <br> **貪婪法** 在每一步做出局部最優選擇，希望達到全局最優（在計算路徑時常失敗）。**DP** 考慮所有相關的過去狀態來做決策。 |
| **Top-down vs. Bottom-up** | **Top-down (Memoization)** starts from $N$ and recurses down. **Bottom-up (Tabulation)** starts from 0/1 and loops up. Bottom-up is preferred in C++ to avoid stack overflow overhead. <br> **由上而下（記憶化）** 從 $N$ 開始遞迴向下。**由下而上（列表法）** 從 0/1 開始循環向上。C++ 中首選由下而上，以避免堆疊溢位開銷。 |
| **Off-by-one Errors** | Confusing 0-based index with 1-based problem steps (e.g., array size `n` vs `n+1`). Always verify your DP table size. <br> **差一錯誤：** 混淆 0-based 索引與 1-based 問題階數（例如：陣列大小 `n` vs `n+1`）。務必驗證你的 DP 表大小。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Define the State:** "Let `dp[i]` represent the max profit/ways to reach index `i`."
    **定義狀態：** 「讓 `dp[i]` 代表到達索引 `i` 的最大利潤/方法數。」
2.  **Establish Recurrence:** "To solve for `dp[i]`, we can transition from `dp[i-1]` or `dp[i-2]`..."
    **建立遞迴關係：** 「為了解決 `dp[i]`，我們可以從 `dp[i-1]` 或 `dp[i-2]` 轉移...」
3.  **Identify Base Cases:** "The recursion stops at index 0, where the value is..."
    **確定基礎情況：** 「遞迴在索引 0 處停止，其值為...」

### Whiteboard Strategy (白板策略)
*   Write the **Recurrence Relation** ($dp[i] = ...$) at the top before coding. It guides your implementation.
    在寫程式碼之前，先在頂部寫下 **遞迴關係式** ($dp[i] = ...$)。它會引導你的實作。
*   Use meaningful variable names (`current`, `prev`, `maxProfit`) instead of just `a`, `b`, `c`.
    使用有意義的變數名稱（`current`, `prev`, `maxProfit`），而不僅僅是 `a`, `b`, `c`。

### Common Follow-ups (常見追問)
*   "Can you optimize the space complexity?" (Hint: Rolling variables).
    「你能優化空間複雜度嗎？」（提示：滾動變數）。
*   "What if the step sizes can be $\{1, 2, 5\}$ instead of just 1 or 2?" (Generalize the loop).
    「如果步長可以是 $\{1, 2, 5\}$ 而不僅僅是 1 或 2 呢？」（泛化迴圈）。

---

## 7. Exercises (練習題)

### Level: Easy (簡單)
**Problem:** **Fibonacci Number** (LeetCode 509)
*   **Hint:** Almost identical to Climbing Stairs. $F(n) = F(n-1) + F(n-2)$.
*   **提示：** 與爬樓梯幾乎相同。$F(n) = F(n-1) + F(n-2)$。

### Level: Medium (中等) - *Crucial for Beginners*
**Problem:** **House Robber** (LeetCode 198)
*   **Problem:** Cannot rob adjacent houses. Maximize money.
*   **Hint:** At house $i$, you can either rob it (value + $dp[i-2]$) or skip it ($dp[i-1]$).
*   **提示：** 在房屋 $i$，你可以搶劫它（價值 + $dp[i-2]$）或跳過它（$dp[i-1]$）。
*   **Recurrence:** $dp[i] = \max(nums[i] + dp[i-2], dp[i-1])$.

### Level: Hard (困難) - *Contextually Hard for Beginner DP*
**Problem:** **Decode Ways** (LeetCode 91)
*   **Problem:** Decode a string of digits to letters ('A'->1, 'B'->2...). Handle '0'.
*   **Hint:** Similar to climbing stairs (1 digit or 2 digits), but with validity checks (e.g., "06" is invalid).
*   **提示：** 類似於爬樓梯（1 位數或 2 位數），但有有效性檢查（例如："06" 無效）。

---

## 8. Quick Checklists (快速檢核表)

Use this mentally before saying "I'm done".
在說「我完成了」之前，先在心裡過一遍這個。

*   [ ] **State Definition:** Does `dp[i]` mean "exactly at $i$" or "up to $i$"?
    **狀態定義：** `dp[i]` 是指「恰好在 $i$」還是「截止到 $i$」？
*   [ ] **Base Cases:** Did I handle $i=0$ and $i=1$ correctly? Will $i-2$ cause an index out of bounds?
    **基礎情況：** 我是否正確處理了 $i=0$ 和 $i=1$？$i-2$ 會導致索引越界嗎？
*   [ ] **Return Value:** Should I return `dp[n]` or `dp[n-1]`? (0-indexed vs 1-indexed).
    **返回值：** 我應該返回 `dp[n]` 還是 `dp[n-1]`？（0 索引 vs 1 索引）。
*   [ ] **Complexity:** Is it strictly $O(N)$? Did I accidentally put a loop inside the DP loop?
    **複雜度：** 它是嚴格的 $O(N)$ 嗎？我是否不小心在 DP 迴圈內放了另一個迴圈？

---

## 9. Memory Anchors (記憶錨點)

*   **The Domino Effect (骨牌效應):**
    To knock down the $i$-th domino, the $(i-1)$-th domino must fall. DP is calculating the force needed for the last domino by observing the previous ones.
    要推倒第 $i$ 個骨牌，第 $(i-1)$ 個骨牌必須倒下。DP 就是通過觀察前面的骨牌來計算最後一個骨牌所需的力。

*   **The "No-Amnesia" Hiker (不失憶的徒步者):**
    A hiker (Recursion) walks a path, forgets it, and walks it again. A smart hiker (DP) writes down the map (Table) so they never walk the same dead-end twice.
    一個徒步者（遞迴）走過一條路，忘記了，然後再走一次。一個聰明的徒步者（DP）寫下地圖（表），所以他們從不走同一條死路兩次。