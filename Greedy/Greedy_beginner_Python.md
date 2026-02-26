Here is the comprehensive guide on **Greedy Algorithms**, tailored for a Senior Software Engineer, structured as requested.

這是一份針對資深軟體工程師量身打造的 **Greedy Algorithms（貪婪演算法）** 完整指南，並依照您的要求進行了結構化編排。

---

# Greedy Algorithms: Foundational Guide for Senior Engineers
# 貪婪演算法：資深工程師的基礎指南

## 1. Learning Goals (學習目標)

*   **Understand the "Greedy Choice Property":** Learn to identify when a local optimal choice leads to a global optimal solution.
    **理解「貪婪選擇性質」：** 學習識別何時「局部最佳解」能導向「全域最佳解」。
*   **Distinguish Greedy from Dynamic Programming:** Recognize when to optimize without backtracking or memoization.
    **區分貪婪與動態規劃：** 辨識何時可以在不回溯或不使用記憶體的情況下進行優化。
*   **Master Proof Techniques (Informal):** Use "Exchange Argument" or "Stay Ahead" logic to justify your approach during interviews.
    **掌握證明技巧（非正式）：** 在面試中使用「交換論證」或「保持領先」邏輯來證成你的解法。
*   **Handle Common Patterns:** Gain proficiency in Interval Scheduling and Array-based greedy problems.
    **掌握常見模式：** 熟練處理區間排程（Interval Scheduling）與基於陣列的貪婪問題。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A Greedy algorithm builds up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法透過逐步建構解法，總是選擇在當下能提供最大即時利益的下一步。

It never reconsiders choices once they are made (no backtracking).
一旦做出選擇，它絕不重新考慮（不回溯）。

### Intuition (直覺)
Imagine you are a cashier trying to give change using the fewest number of coins.
想像你是收銀員，試圖用最少數量的硬幣找零。
You naturally take the largest denomination coin possible first, then the next largest, and so on.
你會自然地先拿面額最大的硬幣，然後是次大的，依此類推。
This is a greedy strategy: optimizing the count at every single step.
這就是貪婪策略：在每一步驟都優化數量。

### Complexity (複雜度)
*   **Time:** Often $O(N \log N)$ due to sorting, or $O(N)$ if the input is already sorted or a heap is used efficiently.
    **時間：** 通常為 $O(N \log N)$，因為需要排序；若輸入已排序或高效使用 Heap，則為 $O(N)$。
*   **Space:** Usually $O(1)$ (in-place) or $O(N)$ for output storage.
    **空間：** 通常為 $O(1)$（原地操作）或 $O(N)$ 用於儲存輸出。

### When to Use (適用場景)
1.  **Greedy Choice Property:** You can make a locally optimal choice and still reach a globally optimal solution.
    **貪婪選擇性質：** 你可以做出局部最佳選擇，且仍能達成全域最佳解。
2.  **Optimal Substructure:** An optimal solution to the problem contains an optimal solution to subproblems.
    **最佳子結構：** 問題的最佳解包含了子問題的最佳解。

### When NOT to Use (不適用場景)
*   **0/1 Knapsack Problem:** Taking the item with the highest value-to-weight ratio first fails if items cannot be broken.
    **0/1 背包問題：** 如果物品不可分割，優先拿取「價值重量比」最高的物品會失敗。
*   **Longest Path in a Graph:** Greedy choices can lead to dead ends.
    **圖中的最長路徑：** 貪婪選擇可能會導致死胡同。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting + Iteration (排序 + 迭代)
*   **Scenario:** Interval scheduling, merging intervals.
    **場景：** 區間排程、合併區間。
*   **Strategy:** Sort by start or end time, then iterate to find overlaps or gaps.
    **策略：** 依開始或結束時間排序，然後迭代以尋找重疊或間隙。

### B. Priority Queue / Heap (優先佇列 / 堆積)
*   **Scenario:** Continuously finding the min/max element dynamically.
    **場景：** 動態地持續尋找最小/最大元素。
*   **Strategy:** Push candidates into a heap and pop the best one at each step.
    **策略：** 將候選者放入 Heap，每一步彈出最佳者。

### C. Two Pointers / Sweeping (雙指針 / 掃描)
*   **Scenario:** Partitioning arrays, trapping rain water (some variations).
    **場景：** 分割陣列、接雨水（部分變體）。
*   **Strategy:** Move pointers based on a greedy condition (e.g., always move the shorter wall).
    **策略：** 基於貪婪條件移動指針（例如：總是移動較短的牆）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Jump Game (LeetCode 55)
**Problem Statement:**
You are given an integer array `nums`. You are initially positioned at the array's **first index**.
給定一個整數陣列 `nums`。你最初位於陣列的 **第一個索引**。
Each element in the array represents your maximum jump length at that position.
陣列中的每個元素代表你在該位置的最大跳躍長度。
Return `true` if you can reach the last index, or `false` otherwise.
如果你能到達最後一個索引，回傳 `true`，否則回傳 `false`。

### Approach 1: Backtracking (Brute Force) / 回溯法（暴力解）
*   **Idea:** Try every possible jump from every position.
    **思路：** 嘗試從每個位置出發的所有可能跳躍。
*   **Complexity:** $O(2^n)$. Extremely slow.
    **複雜度：** $O(2^n)$。極慢。

### Approach 2: Dynamic Programming (Memoization) / 動態規劃（記憶化）
*   **Idea:** Record "good" or "bad" indices. If I can jump to a "good" index, I am good.
    **思路：** 記錄「好」或「壞」的索引。如果我能跳到一個「好」索引，那我就是安全的。
*   **Complexity:** $O(n^2)$. Better, but not optimal.
    **複雜度：** $O(n^2)$。好一點，但非最佳。

### Approach 3: Greedy (Optimal) / 貪婪法（最佳解）
*   **Idea:** We don't need to know *every* path. We only need to know the **furthest index** we can currently reach.
    **思路：** 我們不需要知道「每一條」路徑。我們只需要知道目前能到達的 **最遠索引**。
*   **Logic:** Iterate through the array. Update `max_reachable`. If the current index is beyond `max_reachable`, we are stuck.
    **邏輯：** 迭代陣列。更新 `max_reachable`。如果當前索引超過了 `max_reachable`，表示我們卡住了。

### Python Solution (Reference)

```python
from typing import List

class Solution:
    def canJump(self, nums: List[int]) -> bool:
        # Initialize the furthest index we can reach.
        # 初始化我們能到達的最遠索引。
        max_reachable = 0
        
        # Iterate through each index and its jump length.
        # 迭代每個索引及其跳躍長度。
        for i, jump_len in enumerate(nums):
            # If current index i is greater than max_reachable,
            # it means we cannot reach this position.
            # 如果當前索引 i 大於 max_reachable，
            # 表示我們無法到達此位置。
            if i > max_reachable:
                return False
            
            # Update the furthest point reachable.
            # It's either the current max, or reaching i and jumping jump_len.
            # 更新可到達的最遠點。
            # 它是當前的最大值，或是到達 i 並跳躍 jump_len 的結果。
            max_reachable = max(max_reachable, i + jump_len)
            
            # Optimization: If we can already reach the end, return True early.
            # 優化：如果我們已經能到達終點，提早回傳 True。
            if max_reachable >= len(nums) - 1:
                return True
                
        return True
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ — We pass through the array once.
    **時間：** $O(N)$ — 我們遍歷陣列一次。
*   **Space:** $O(1)$ — Only one variable `max_reachable` is used.
    **空間：** $O(1)$ — 僅使用一個變數 `max_reachable`。

### Why the Brute Force is Wrong (in Interview Context)
Using recursion for this problem signals a lack of observation.
在面試中對此題使用遞迴，顯示缺乏觀察力。
The "Greedy" insight is realizing that if you can reach index `k`, you can reach all indices `< k`.
「貪婪」的洞察在於意識到：如果你能到達索引 `k`，你就能到達所有小於 `k` 的索引。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Greedy (貪婪) | Dynamic Programming (動態規劃) |
| :--- | :--- | :--- |
| **Decision Making** | Makes the best choice *now* and never looks back. <br> 做出*當下*最佳選擇且絕不回頭。 | Considers all choices (or relies on sub-problems) to find the global optimum. <br> 考慮所有選擇（或依賴子問題）以尋找全域最佳解。 |
| **Backtracking** | No. <br> 否。 | Yes (conceptually) or implicit via table lookup. <br> 是（概念上）或透過查表隱含回溯。 |
| **Correctness** | Harder to prove. Requires specific properties. <br> 較難證明。需要特定性質。 | Guaranteed if transitions are correct. <br> 若轉移方程正確則保證正確。 |
| **Typical Speed** | Faster ($O(N)$ or $O(N \log N)$). <br> 較快。 | Slower ($O(N^2)$ or higher). <br> 較慢。 |

**Trap:** Assuming sorting solves everything.
**陷阱：** 以為排序能解決所有問題。
Sometimes sorting destroys the relative order required for the solution (e.g., "Jump Game" relies on index order, not value order).
有時排序會破壞解法所需的相對順序（例如：「跳躍遊戲」依賴索引順序，而非數值大小順序）。

---

## 6. Interview Strategy (面試實戰建議)

### 1. The "Try-Fail-Optimize" Framework (「嘗試-失敗-優化」框架)
Don't jump straight to Greedy. It looks like you memorized the answer.
不要直接跳到貪婪解法。這看起來像你背了答案。
*   **Step 1:** "I could explore all paths using DFS..." (Establish baseline).
    **第一步：** 「我可以用 DFS 探索所有路徑...」（建立基準）。
*   **Step 2:** "However, notice that if I take the longest jump..." (Identify property).
    **第二步：** 「然而，注意到如果我採取最遠的跳躍...」（識別性質）。
*   **Step 3:** "This suggests a greedy approach might work."
    **第三步：** 「這暗示貪婪方法可能行得通。」

### 2. Proving Correctness (證明正確性)
You don't need a mathematical proof, but use **"Proof by Contradiction"** logic.
你不需要數學證明，但要使用 **「反證法」** 邏輯。
*   *Say:* "Suppose the greedy choice isn't the best. That would mean taking a smaller step now allows a bigger step later that overtakes us. But in this problem, reaching further now strictly includes the possibilities of reaching shorter distances."
    *說：* 「假設貪婪選擇不是最好的。那意味著現在跨小步能讓後面跨大步並超越我們。但在這題中，現在到達越遠，嚴格包含了到達較近距離的所有可能性。」

### 3. Common Follow-ups (常見追問)
*   "What if the values can be negative?" (Usually breaks Greedy, requires DP).
    「如果數值可能是負的呢？」（通常會打破貪婪性質，需要 DP）。
*   "Output the actual path, not just true/false."
    「輸出實際路徑，而不僅是 true/false。」

---

## 7. Practice Problems (練習題)

### Level: Easy (暖身)
**Problem:** Best Time to Buy and Sell Stock II (LeetCode 122)
**Hint:** If tomorrow's price is higher than today's, buy today and sell tomorrow. Accumulate all positive slopes.
**提示：** 如果明天的價格高於今天，今天買明天賣。累加所有正斜率。

### Level: Medium (核心)
**Problem:** Gas Station (LeetCode 134)
**Hint:** If you can't go from station A to B, you can't go from any station between A and B to B. Reset start point.
**提示：** 如果你無法從加油站 A 到達 B，那你也無法從 A 和 B 之間的任何站到達 B。重置起點。

### Level: Hard (進階概念)
**Problem:** Candy (LeetCode 135)
**Hint:** Do two passes. Left-to-right to satisfy left neighbors, then right-to-left to satisfy right neighbors. Take the max.
**提示：** 做兩次掃描。從左到右滿足左鄰居，再從右到左滿足右鄰居。取最大值。

---

## 8. Rapid Checklist (快速檢核表)

*   [ ] **Optimization Problem?** Are you looking for min/max?
    **最佳化問題？** 你在尋找極小/極大值嗎？
*   [ ] **Greedy Property?** Does taking the "biggest" piece now restrict future valid moves?
    **貪婪性質？** 現在拿「最大」的一塊會限制未來的有效移動嗎？
*   [ ] **Sorted?** Did you sort the input (intervals/arrays) if order doesn't matter?
    **已排序？** 如果順序不重要，你是否對輸入（區間/陣列）進行了排序？
*   [ ] **Counter-example?** Can you think of ONE case where being greedy fails? If yes, switch to DP.
    **反例？** 你能想到一個貪婪失敗的案例嗎？如果有，轉向 DP。
*   [ ] **Edge Cases?** Empty array? Single element? All zeros?
    **邊界情況？** 空陣列？單一元素？全零？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Mountain Climber" (登山者)
Greedy is like climbing a mountain in thick fog. You always take the step that goes steepest up.
貪婪就像在濃霧中登山。你總是邁出坡度最陡向上的那一步。
*   **Success:** If it's a single peak (convex), you reach the top.
    **成功：** 如果是單一山峰（凸函數），你會到達頂端。
*   **Failure:** If there are multiple peaks, you might get stuck on a smaller hill (local optimum).
    **失敗：** 如果有多座山峰，你可能會卡在小山丘上（局部最佳解）。

### The "Marshmallow Test" (棉花糖實驗)
*   **Greedy:** Eat the marshmallow immediately.
    **貪婪：** 立刻吃掉棉花糖。
*   **Delayed Gratification (DP):** Wait to get two marshmallows later.
    **延遲滿足（DP）：** 等待以便稍後得到兩個棉花糖。
*   *Note:* Greedy algorithms fail the marshmallow test unless the rule is "eating now guarantees more later".
    *註：* 除非規則是「現在吃保證以後更多」，否則貪婪演算法通不過棉花糖測試。