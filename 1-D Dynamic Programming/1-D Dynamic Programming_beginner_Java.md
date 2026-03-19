Here is the comprehensive guide for **1-D Dynamic Programming**, tailored for a Senior Engineer audience starting with DP foundations, using Java.

這是一份針對 **1-D Dynamic Programming（一維動態規劃）** 的完整教材，專為資深工程師設計，從基礎觀念切入，使用 Java 撰寫。

---

# 1-D Dynamic Programming: The Foundation (Beginner Level)
# 一維動態規劃：基礎篇

## 1. Learning Objectives (學習目標)

*   **Understand the core philosophy of DP:** Trade space for time to solve optimization problems.
    **理解 DP 的核心哲學：** 以空間換取時間來解決最佳化問題。
*   **Master the transition from Recursion to DP:** Learn how to convert Brute Force Recursion into Memoization (Top-Down) and Tabulation (Bottom-Up).
    **掌握從遞迴到 DP 的轉換：** 學習如何將暴力遞迴轉化為記憶化搜索（Top-Down）與列表法（Bottom-Up）。
*   **Define States and Transitions accurately:** The most critical skill is defining what `dp[i]` represents and how to derive it from `dp[i-1]`.
    **精準定義狀態與轉移方程：** 最關鍵的技能是定義 `dp[i]` 代表什麼，以及如何從 `dp[i-1]` 推導出它。
*   **Identify 1-D DP patterns:** Recognize problems that can be solved by linear iteration.
    **識別一維 DP 模式：** 辨識出可以透過線性迭代解決的問題。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
Dynamic Programming is an optimization technique for solving recursive problems with overlapping subproblems and optimal substructure.
動態規劃是一種最佳化技術，用於解決具有重疊子問題與最佳子結構的遞迴問題。

### Intuition (直覺)
"Those who cannot remember the past are condemned to repeat it." — DP is simply **recursion with caching**.
「記不住過去的人註定要重蹈覆轍。」—— DP 簡單來說就是**帶有快取的遞迴**。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$, where $N$ is the input size (solving each subproblem once).
    **時間：** 通常為 $O(N)$，其中 $N$ 是輸入大小（每個子問題只解一次）。
*   **Space:** Usually $O(N)$ for the DP array, often optimizable to $O(1)$ in 1-D problems.
    **空間：** DP 陣列通常為 $O(N)$，在一維問題中常可優化至 $O(1)$。

### When to Use (適用場景)
1.  **Overlapping Subproblems:** The problem can be broken down into smaller, repeated problems (e.g., Fibonacci).
    **重疊子問題：** 問題可以被分解為更小的、重複的問題（例如：費波那契數列）。
2.  **Optimal Substructure:** The optimal solution to the problem can be constructed from optimal solutions of its subproblems.
    **最佳子結構：** 問題的最佳解可以由其子問題的最佳解建構而成。
3.  **Counting/Min/Max/Existence:** Problems asking for "How many ways", "Minimum cost", "Maximum profit", or "Is it possible".
    **計數/極值/存在性：** 詢問「有多少種方法」、「最小成本」、「最大利潤」或「是否可能」的問題。

### When NOT to Use (不適用場景)
1.  **No Overlapping Subproblems:** Like Merge Sort, where subproblems are distinct.
    **無重疊子問題：** 像合併排序（Merge Sort），其子問題是獨立的。
2.  **Greedy is sufficient:** If a local optimal choice always leads to a global optimum, DP is overkill.
    **貪婪演算法已足夠：** 如果局部最佳選擇總是導致全域最佳解，使用 DP 則是大材小用。

---

## 3. Typical Patterns (典型題型 / 模式)

For 1-D DP, most problems fall into these linear scan patterns:
對於一維 DP，大多數問題屬於以下線性掃描模式：

1.  **Fibonacci Style (費波那契風格):**
    *   Dependency: `dp[i]` depends on `dp[i-1]` and `dp[i-2]`.
    *   依賴關係：`dp[i]` 取決於 `dp[i-1]` 和 `dp[i-2]`。
    *   *Examples: Climbing Stairs, House Robber.*

2.  **Cost Accumulation (成本累加):**
    *   Goal: Minimize or maximize cost to reach step `i`.
    *   目標：最小化或最大化到達第 `i` 步的成本。
    *   *Examples: Min Cost Climbing Stairs.*

3.  **String/Sequence Validity (字串/序列有效性):**
    *   Dependency: `dp[i]` depends on validity of previous substrings.
    *   依賴關係：`dp[i]` 取決於先前子字串的有效性。
    *   *Examples: Decode Ways, Word Break.*

---

## 4. Example Walkthrough (範例講解)

### Problem: Climbing Stairs (爬樓梯)
**Problem Statement:** You are climbing a staircase. It takes `n` steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?
**問題重述：** 你正在爬樓梯。需要 `n` 階才能到達頂端。每次你可以爬 1 或 2 階。你有多少種不同的方法可以爬到頂端？

### Thought Process (思路)

1.  **Brute Force (Recursion):**
    To reach step `n`, we could have come from `n-1` or `n-2`.
    要到達第 `n` 階，我們可能來自 `n-1` 或 `n-2`。
    $f(n) = f(n-1) + f(n-2)$.
    *Issue:* Exponential time complexity $O(2^n)$. Re-calculates same values repeatedly.
    *問題：* 指數時間複雜度 $O(2^n)$。重複計算相同數值。

2.  **Optimization 1: Top-Down DP (Memoization):**
    Store the result of $f(n)$ in a map/array. If seen before, return it.
    **優化 1：Top-Down DP（記憶化）：** 將 $f(n)$ 的結果存入 map 或陣列。如果見過，直接回傳。

3.  **Optimization 2: Bottom-Up DP (Tabulation):**
    Start from base cases (step 1, step 2) and build up to `n`.
    **優化 2：Bottom-Up DP（列表法）：** 從基本情況（第 1 階、第 2 階）開始，一路推導到 `n`。

4.  **Optimization 3: Space Optimization:**
    We only need the last two values to calculate the current one. No need to keep the whole array.
    **優化 3：空間優化：** 我們只需要最後兩個數值來計算當前數值。不需要保留整個陣列。

### Java Reference Solution (Java 參考解)

```java
class Solution {
    /**
     * Calculates the number of distinct ways to climb to the top.
     * 計算爬到頂端的不同方法數。
     * 
     * Time Complexity: O(n) - Linear scan.
     * 時間複雜度：O(n) - 線性掃描。
     * Space Complexity: O(1) - Only storing two variables.
     * 空間複雜度：O(1) - 僅儲存兩個變數。
     */
    public int climbStairs(int n) {
        // Base cases handling
        // 處理基本情況
        if (n <= 1) {
            return 1;
        }
        
        // 'prev' represents dp[i-2], 'curr' represents dp[i-1]
        // 'prev' 代表 dp[i-2]，'curr' 代表 dp[i-1]
        // Initially: to reach step 1 (1 way), to reach step 2 (2 ways)
        // 初始狀態：到達第 1 階（1 種），到達第 2 階（2 種）
        // Note: For generic Fibonacci, usually start 0, 1. Here problem specific.
        int prev = 1; // dp[i-2]
        int curr = 2; // dp[i-1]
        
        // Start loop from step 3
        // 從第 3 階開始迴圈
        for (int i = 3; i <= n; i++) {
            int next = prev + curr; // dp[i] = dp[i-2] + dp[i-1]
            
            // Shift the window for the next iteration
            // 為下一次迭代移動視窗
            prev = curr;
            curr = next;
        }
        
        return curr;
    }
}
```

### Wrong Approach / Common Mistake (錯誤示範)

```java
// Mistake: Using simple recursion without memoization
// 錯誤：使用未經記憶化的簡單遞迴
public int climbStairsWrong(int n) {
    if (n <= 2) return n;
    // This will Time Limit Exceed (TLE) for n > 45
    // 這在 n > 45 時會導致超時 (TLE)
    return climbStairsWrong(n - 1) + climbStairsWrong(n - 2);
}
```

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Off-by-one Error**<br>(差一錯誤) | Confusing array size `n` vs `n+1`. If you need to access `dp[n]`, size must be `n+1`.<br>混淆陣列大小 `n` 與 `n+1`。如果你需要存取 `dp[n]`，大小必須是 `n+1`。 |
| **Base Case Initialization**<br>(基本情況初始化) | Forgetting to initialize `dp[0]` or `dp[1]`. For minimization problems, initialize array with `Integer.MAX_VALUE`.<br>忘記初始化 `dp[0]` 或 `dp[1]`。對於求最小值的問題，應將陣列初始化為 `Integer.MAX_VALUE`。 |
| **Greedy vs DP**<br>(貪婪與動態規劃) | Greedy makes the best local choice at each step. DP considers all paths (via subproblems) to find the global optimum.<br>貪婪法在每一步做出最佳局部選擇。DP 則考慮所有路徑（透過子問題）以找到全域最佳解。 |
| **Top-down vs Bottom-up** | Top-down is easier to write (recursion) but can hit stack overflow. Bottom-up is more efficient and allows space optimization.<br>Top-down 較易撰寫（遞迴）但可能導致堆疊溢位。Bottom-up 效率較高且允許空間優化。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify:** "This looks like an optimization problem where decisions at each step depend on previous outcomes. I'm thinking Dynamic Programming."
    **識別：** 「這看起來是一個最佳化問題，每一步的決策取決於先前的結果。我在考慮使用動態規劃。」
2.  **Define State:** "Let `dp[i]` represent the minimum cost to reach step `i`."
    **定義狀態：** 「讓 `dp[i]` 代表到達第 `i` 階的最小成本。」
3.  **Recurrence Relation:** "To compute `dp[i]`, we can transition from..."
    **遞迴關係：** 「為了計算 `dp[i]`，我們可以從...轉移過來。」

### Whiteboard Strategy (白板策略)
*   **Draw the array:** Visualize `dp` array indices `0` to `n`.
    **畫出陣列：** 視覺化 `dp` 陣列索引 `0` 到 `n`。
*   **Manual Trace:** Walk through `n=3` or `n=4` manually to verify the formula before coding.
    **手動追蹤：** 在寫程式碼前，手動走一遍 `n=3` 或 `n=4` 來驗證公式。

### Common Follow-ups (常見追問)
*   "Can you optimize the space complexity?" (Hint: Do you need the whole array?)
    「你能優化空間複雜度嗎？」（提示：你需要整個陣列嗎？）
*   "What if the steps allowed were dynamic (e.g., [1, 3, 5]) instead of just 1 or 2?"
    「如果允許的步數是動態的（例如 [1, 3, 5]）而不僅僅是 1 或 2 呢？」

---

## 7. Practice Problems (練習題)

### 1. Easy: Fibonacci Number (費波那契數)
*   **Prompt:** Calculate $F(n)$ where $F(n) = F(n-1) + F(n-2)$.
    **題目：** 計算 $F(n)$，其中 $F(n) = F(n-1) + F(n-2)$。
*   **Hint:** Just like Climbing Stairs. Focus on space optimization ($O(1)$ space).
    **提示：** 就像爬樓梯一樣。專注於空間優化（$O(1)$ 空間）。

### 2. Medium: House Robber (打家劫舍)
*   **Prompt:** Given an integer array `nums`, find maximum sum such that no two elements are adjacent.
    **題目：** 給定整數陣列 `nums`，找出最大總和，條件是不能選取相鄰的兩個元素。
*   **Hint:** `dp[i] = max(dp[i-1], nums[i] + dp[i-2])`. Rob current and skip previous, or skip current and take previous.
    **提示：** `dp[i] = max(dp[i-1], nums[i] + dp[i-2])`。搶當前並跳過前一個，或跳過當前並取前一個。

### 3. Hard (for beginner DP): Decode Ways (解碼方法)
*   **Prompt:** Decode a string of digits to letters ('A'->1, 'B'->2...). Count ways. Handle '0'.
    **題目：** 將數字字串解碼為字母（'A'->1, 'B'->2...）。計算方法數。需處理 '0'。
*   **Hint:** `dp[i]` depends on single digit `s[i]` (if valid) and double digit `s[i-1...i]` (if valid). Edge cases with '0' are tricky.
    **提示：** `dp[i]` 取決於單個數字 `s[i]`（若有效）和雙位數字 `s[i-1...i]`（若有效）。'0' 的邊界情況很棘手。

---

## 8. Quick Checklists (快速檢核表)

Use this during your interview or practice:
在面試或練習時使用此表：

*   [ ] **State Definition:** Does `dp[i]` clearly mean something (e.g., max profit ending at day `i`)?
    **狀態定義：** `dp[i]` 是否有明確意義（例如：在第 `i` 天結束時的最大利潤）？
*   [ ] **Base Cases:** Did I handle `i=0` and `i=1`? Did I handle empty input?
    **基本情況：** 我是否處理了 `i=0` 和 `i=1`？我是否處理了空輸入？
*   [ ] **Loop Bounds:** Does the loop go up to `<= n` or `< n`? (Usually `<= n` for DP array of size `n+1`).
    **迴圈邊界：** 迴圈是到 `<= n` 還是 `< n`？（通常對於大小為 `n+1` 的 DP 陣列是 `<= n`）。
*   [ ] **Return Value:** Am I returning `dp[n]` or `dp[n-1]`?
    **回傳值：** 我是回傳 `dp[n]` 還是 `dp[n-1]`？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Domino Effect" (骨牌效應)
Imagine 1-D DP as a row of dominoes. To knock down the $i$-th domino, the force comes from the $(i-1)$-th (and maybe $(i-2)$-th). You cannot calculate the state of the last domino without the energy transfer from the previous ones.
想像一維 DP 是一排骨牌。要推倒第 $i$ 個骨牌，力量來自第 $(i-1)$ 個（可能還有 $(i-2)$ 個）。如果沒有前一個骨牌的能量傳遞，你無法計算最後一個骨牌的狀態。

### The "Fill-in-the-Blank" Form (填空題)
You have a form (array) with `n` empty boxes. You cannot fill box 5 until you have filled box 4 (and maybe 3). Tabulation is just filling out this form from top to bottom.
你有一張有 `n` 個空格的表格（陣列）。在填好第 4 格（可能還有第 3 格）之前，你不能填第 5 格。列表法（Tabulation）就是從上到下填寫這張表格。