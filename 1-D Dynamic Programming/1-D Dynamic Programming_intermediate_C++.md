Here is the comprehensive guide for **1-D Dynamic Programming**, tailored for a Senior Software Engineer, formatted as requested.

---

# 1-D Dynamic Programming: Interview Handbook
# 一維動態規劃：面試實戰手冊

## 1. Learning Objectives (學習目標)

*   **Master the "State Definition" intuition:** Learn to define $dp[i]$ not just as "the answer for index $i$", but as the specific state (e.g., "max profit ending at day $i$").
    *   **掌握「狀態定義」的直覺：** 學習不僅將 $dp[i]$ 定義為「索引 $i$ 的答案」，而是具體的狀態（例如：「在第 $i$ 天結束時的最大利潤」）。
*   **Derive Recurrence Relations systematically:** Move from recursive thinking to mathematical equations before writing a single line of code.
    *   **系統化推導遞迴關係：** 在寫任何程式碼之前，先從遞迴思維轉向數學方程式。
*   **Optimize Space Complexity:** Transition from $O(N)$ space to $O(1)$ (rolling variables) for linear DP problems.
    *   **優化空間複雜度：** 針對線性 DP 問題，從 $O(N)$ 空間過渡到 $O(1)$（滾動變數）。
*   **Distinguish DP from Greedy:** Understand when a local optimal choice leads to a global optimum (Greedy) versus when you need to explore all sub-possibilities (DP).
    *   **區分 DP 與 Greedy：** 理解何時局部最佳解能導致全域最佳解（Greedy），以及何時需要探索所有子可能性（DP）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
1-D DP is an optimization technique used to solve problems by breaking them down into simpler, overlapping subproblems arranged in a linear sequence.
一維動態規劃是一種優化技術，用於透過將問題分解為線性排列的、簡單且重疊的子問題來解決問題。

### Intuition (直覺)
Think of it as "Mathematical Induction" with a cache.
把它想像成帶有快取的「數學歸納法」。
To solve for step $i$, you only need the results from step $i-1$, $i-2$, etc., and the decision logic for the current step.
要解決第 $i$ 步，你只需要第 $i-1$、$i-2$ 等步驟的結果，加上當前的決策邏輯。

### Complexity (複雜度)
*   **Time:** Typically $O(N)$, where $N$ is the size of the input array.
    *   **時間：** 通常為 $O(N)$，其中 $N$ 是輸入陣列的大小。
*   **Space:** Naively $O(N)$ using an array, often optimizable to $O(1)$ if the transition only depends on a fixed number of previous states.
    *   **空間：** 使用陣列時最基本為 $O(N)$，如果轉移僅依賴於固定數量的先前狀態，通常可優化為 $O(1)$。

### When to Use (適用場景)
*   **Maximum/Minimum:** e.g., "Max profit," "Min cost to climb stairs."
    *   **最大值/最小值：** 例如：「最大利潤」、「爬樓梯的最小成本」。
*   **Counting:** e.g., "Number of ways to decode a string."
    *   **計數：** 例如：「解碼字串的方法數」。
*   **Feasibility:** e.g., "Can we reach the end?" (Jump Game).
    *   **可行性：** 例如：「我們能到達終點嗎？」（跳躍遊戲）。

### When NOT to Use (不適用場景)
*   **Graph Shortest Path with weights:** Use Dijkstra.
    *   **帶權重的圖最短路徑：** 使用 Dijkstra 演算法。
*   **Simple Connectivity:** Use Union-Find or BFS/DFS.
    *   **簡單連通性：** 使用 Union-Find 或 BFS/DFS。
*   **Unordered sets:** If the order doesn't matter, it might be a Hash Map or Sorting problem.
    *   **無序集合：** 如果順序不重要，這可能是雜湊表或排序問題。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. The "Fibonacci" Style (斐波那契風格)
Depends strictly on fixed previous steps (e.g., $i-1, i-2$).
嚴格依賴於固定的前幾步（例如 $i-1, i-2$）。
*   *Equation:* $dp[i] = dp[i-1] + dp[i-2]$
*   *Example:* Climbing Stairs, Tiling Rectangle.

### B. The "Choice" Style (決策風格)
At each step, you make a choice (take or skip) that affects the value.
在每一步，你做出一個影響數值的選擇（選取或跳過）。
*   *Equation:* $dp[i] = \max(dp[i-1], \text{value}[i] + dp[i-2])$
*   *Example:* House Robber.

### C. The "Partition" Style (分割風格)
Determine if the array can be segmented based on conditions.
確定陣列是否可以根據條件進行分割。
*   *Equation:* $dp[i] = \text{valid}(s[j:i]) \land dp[j]$ for some $j < i$.
*   *Example:* Word Break, Decode Ways.

### D. Multi-State Tracking (多狀態追蹤)
Sometimes one array isn't enough; you need to track min and max, or "hold" vs "sold".
有時一個陣列是不夠的；你需要追蹤最小值和最大值，或者「持有」與「賣出」。
*   *Example:* Maximum Product Subarray, Best Time to Buy and Sell Stock with Cooldown.

---

## 4. Example Walkthrough (範例講解)

### Problem: House Robber (打家劫舍)
**Problem Statement:**
You are a robber planning to rob houses along a street. Each house has a certain amount of money stashed.
你是一個計劃沿街搶劫房屋的強盜。每棟房子都藏有一定數量的錢。
The only constraint stopping you is that adjacent houses have security systems connected and **it will automatically contact the police if two adjacent houses were broken into on the same night**.
阻止你的唯一限制是相鄰的房屋有連接的防盜系統，**如果兩棟相鄰的房屋在同一晚被闖入，它會自動聯繫警察**。
Given an integer array `nums`, return the maximum amount of money you can rob tonight without alerting the police.
給定一個整數陣列 `nums`，傳回你在不驚動警察的情況下今晚能搶到的最大金額。

### Thought Process (思路)

#### 1. Define the State (定義狀態)
Let $dp[i]$ be the maximum money we can rob from the first $i$ houses (index $0$ to $i$).
設 $dp[i]$ 為我們能從前 $i$ 棟房子（索引 $0$ 到 $i$）搶到的最大金額。

#### 2. The Choice (決策)
For house $i$, we have two choices:
對於第 $i$ 棟房子，我們有兩個選擇：
1.  **Rob it:** We gain `nums[i]`, but we couldn't have robbed house $i-1$. So we take the max from $i-2$. Value: `nums[i] + dp[i-2]`.
    **搶劫它：** 我們獲得 `nums[i]`，但我們不能搶第 $i-1$ 棟房子。所以我們取 $i-2$ 的最大值。價值：`nums[i] + dp[i-2]`。
2.  **Skip it:** We don't rob house $i$. The max money is whatever we had at $i-1$. Value: `dp[i-1]`.
    **跳過它：** 我們不搶第 $i$ 棟房子。最大金額就是我們在 $i-1$ 時擁有的。價值：`dp[i-1]`。

#### 3. Recurrence Relation (遞迴關係)
$$dp[i] = \max(dp[i-1], nums[i] + dp[i-2])$$

#### 4. Base Cases (基本情況)
*   $dp[0] = nums[0]$
*   $dp[1] = \max(nums[0], nums[1])$

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

class Solution {
public:
    int rob(std::vector<int>& nums) {
        int n = nums.size();
        
        // Boundary check: Handle empty or single element cases
        // 邊界檢查：處理空陣列或單一元素的情況
        if (n == 0) return 0;
        if (n == 1) return nums[0];

        // We only need the previous two states to calculate the current one.
        // 我們只需要前兩個狀態來計算當前狀態。
        // prev2 represents dp[i-2], prev1 represents dp[i-1]
        // prev2 代表 dp[i-2]，prev1 代表 dp[i-1]
        int prev2 = nums[0];
        int prev1 = std::max(nums[0], nums[1]);

        for (int i = 2; i < n; ++i) {
            // Apply the recurrence relation: max(skip current, rob current + prev2)
            // 應用遞迴關係：max(跳過當前, 搶劫當前 + prev2)
            int current = std::max(prev1, nums[i] + prev2);
            
            // Shift the states for the next iteration
            // 為下一次迭代移動狀態
            prev2 = prev1;
            prev1 = current;
        }

        // prev1 holds the result for the last house (dp[n-1])
        // prev1 持有最後一棟房子的結果 (dp[n-1])
        return prev1;
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ - One pass through the array.
    *   **時間：** $O(N)$ - 遍歷陣列一次。
*   **Space:** $O(1)$ - Only used two variables (`prev1`, `prev2`) instead of a full DP array.
    *   **空間：** $O(1)$ - 僅使用了兩個變數（`prev1`, `prev2`），而非完整的 DP 陣列。

---

## 5. Common Pitfalls (常見陷阱)

| Pitfall (陷阱) | Description (描述) | Correction (修正) |
| :--- | :--- | :--- |
| **Off-by-one Errors**<br>差一錯誤 | Confusing index $i$ with the $i$-th element (1-based vs 0-based).<br>混淆索引 $i$ 與第 $i$ 個元素（1-based 與 0-based）。 | Always pad your DP array with a dummy 0 index if it simplifies logic, or be strict about $dp[i]$ mapping to `nums[i]`.<br>如果能簡化邏輯，可以在 DP 陣列前填充一個虛擬的 0 索引，或者嚴格對應 $dp[i]$ 與 `nums[i]`。 |
| **Greedy Trap**<br>貪婪陷阱 | Assuming taking the biggest number now is always best.<br>假設現在取最大數總是最好的。 | Verify if a local loss allows a larger future gain. If yes, use DP.<br>驗證局部損失是否允許更大的未來收益。如果是，使用 DP。 |
| **Initialization**<br>初始化 | Forgetting to handle empty arrays or arrays with size 1.<br>忘記處理空陣列或大小為 1 的陣列。 | Always write edge cases at the top of the function.<br>總是在函數頂部寫下邊界情況。 |
| **State Definition**<br>狀態定義 | Defining $dp[i]$ vaguely (e.g., "result at i").<br>模糊地定義 $dp[i]$（例如：「i 的結果」）。 | Be specific: "Max profit ending exactly at $i$" vs "Max profit up to $i$".<br>要具體：「恰好在 $i$ 結束的最大利潤」 vs 「截至 $i$ 為止的最大利潤」。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This looks like an optimization problem where decisions at each step depend on previous outcomes. I'm thinking Dynamic Programming."
    *   **識別：** 「這看起來像是一個優化問題，每一步的決策都取決於先前的結果。我在考慮動態規劃。」
2.  **Define:** "Let's define $dp[i]$ as..." (Write this on the board).
    *   **定義：** 「讓我們將 $dp[i]$ 定義為...」（寫在白板上）。
3.  **Relate:** "To find $dp[i]$, I can either [Option A] or [Option B]. So the equation is..."
    *   **關聯：** 「為了找到 $dp[i]$，我可以 [選擇 A] 或 [選擇 B]。所以方程式是...」
4.  **Optimize:** "I see I only need the last 2 values. I can optimize space to $O(1)$."
    *   **優化：** 「我發現我只需要最後兩個值。我可以將空間優化為 $O(1)$。」

### Whiteboard Strategy (白板策略)
*   Don't start coding immediately. Write the **Recurrence Relation** first. It is the "pseudocode" for DP.
    *   不要立即開始寫程式碼。先寫下 **遞迴關係式**。這是 DP 的「虛擬碼」。
*   Draw a small table (indices 0 to 4) and manually fill it to verify your logic.
    *   畫一個小表格（索引 0 到 4）並手動填寫以驗證你的邏輯。

### Common Follow-ups (常見追問)
*   "What if the houses are arranged in a circle?" (Answer: Run DP twice, once $0 \to n-2$, once $1 \to n-1$).
    *   「如果房子是圍成一圈排列的呢？」（回答：執行兩次 DP，一次 $0 \to n-2$，一次 $1 \to n-1$）。
*   "We need to output the list of houses robbed, not just the max value." (Answer: Use a parent pointer array `from[i]` to backtrack).
    *   「我們需要輸出被搶劫的房屋列表，而不僅僅是最大值。」（回答：使用父指標陣列 `from[i]` 進行回溯）。

---

## 7. Practice Problems (練習題)

### Easy: Climbing Stairs (爬樓梯)
*   **Prompt:** You can climb 1 or 2 steps. How many distinct ways to reach the top?
    *   **題目：** 你可以爬 1 或 2 階。有多少種不同的方法可以到達頂部？
*   **Hint:** Exactly Fibonacci. $dp[i] = dp[i-1] + dp[i-2]$.
    *   **提示：** 完全是斐波那契數列。$dp[i] = dp[i-1] + dp[i-2]$。

### Medium: Decode Ways (解碼方法)
*   **Prompt:** 'A'->1, 'B'->2... Given string "12", it could be "AB" (1, 2) or "L" (12). Count ways.
    *   **題目：** 'A'->1, 'B'->2... 給定字串 "12"，它可以是 "AB" (1, 2) 或 "L" (12)。計算方法數。
*   **Hint:** Handle '0' carefully. $dp[i]$ depends on single digit valid check ($s[i]$) and two-digit valid check ($s[i-1...i]$).
    *   **提示：** 小心處理 '0'。$dp[i]$ 取決於單數位有效性檢查 ($s[i]$) 和兩位數有效性檢查 ($s[i-1...i]$)。

### Hard: Maximum Product Subarray (最大乘積子陣列)
*   **Prompt:** Find the contiguous subarray within an array which has the largest product.
    *   **題目：** 在陣列中找到具有最大乘積的連續子陣列。
*   **Hint:** A negative number can flip a minimum product to a maximum. You need to track both `max_so_far` and `min_so_far` at each step.
    *   **提示：** 負數可以將最小乘積翻轉為最大乘積。你需要每一步都追蹤 `max_so_far` 和 `min_so_far`。
*   **Transition:**
    ```cpp
    temp_max = max(nums[i], nums[i]*cur_max, nums[i]*cur_min);
    cur_min = min(nums[i], nums[i]*cur_max, nums[i]*cur_min);
    cur_max = temp_max;
    ```

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Base Cases:** Did I handle $i=0$ and $i=1$?
    *   **基本情況：** 我是否處理了 $i=0$ 和 $i=1$？
*   [ ] **Loop Bounds:** Does the loop go up to $n$ or $n-1$? Does the array access go out of bounds?
    *   **迴圈邊界：** 迴圈是執行到 $n$ 還是 $n-1$？陣列存取是否越界？
*   [ ] **Initialization:** Are my DP variables initialized to 0, -infinity, or the first element?
    *   **初始化：** 我的 DP 變數是初始化為 0、負無窮大，還是第一個元素？
*   [ ] **Return Value:** Am I returning `dp[n-1]` or `max(dp)`?
    *   **回傳值：** 我是回傳 `dp[n-1]` 還是 `max(dp)`？

---

## 9. Memory Anchors (記憶錨點)

### The "Domino Effect" (骨牌效應)
Visualize 1-D DP as pushing dominoes.
將一維 DP 想像成推骨牌。
To knock down domino $i$, the force comes from domino $i-1$. You don't need to know who pushed domino 0, just that the force was transferred to $i-1$.
要推倒第 $i$ 個骨牌，力量來自第 $i-1$ 個骨牌。你不需要知道誰推了第 0 個骨牌，只需要知道力量傳遞到了 $i-1$。

### The "Sliding Window" of State (狀態的滑動視窗)
If your recurrence is $dp[i] = f(dp[i-1], dp[i-2])$, imagine a window of size 2 sliding through the array.
如果你的遞迴關係是 $dp[i] = f(dp[i-1], dp[i-2])$，想像一個大小為 2 的視窗在陣列上滑動。
Everything outside the window is irrelevant garbage. This reminds you to optimize space to $O(1)$.
視窗之外的所有東西都是無關的垃圾。這提醒你將空間優化為 $O(1)$。