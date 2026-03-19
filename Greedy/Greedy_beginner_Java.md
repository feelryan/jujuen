Here is the comprehensive interview preparation guide for **Greedy Algorithms**, tailored for a Senior Software Engineer, covering the **Beginner** level concepts with deep insights suitable for your experience level.

這是一份針對 **貪婪演算法（Greedy Algorithms）** 的完整面試準備教材，專為資深軟體工程師量身打造，涵蓋 **初學者（Beginner）** 難度的核心概念，並提供符合您經驗深度的洞察。

---

# Greedy Algorithms: A Practical Guide for Senior Engineers
# 貪婪演算法：資深工程師實戰指南

## 1. Learning Objectives (學習目標)

*   **Understand the Core Philosophy:** Grasp how making the locally optimal choice leads to a global optimum in specific scenarios.
    **理解核心哲學：** 掌握如何在特定場景下，透過做出局部最佳選擇來達成全域最佳解。
*   **Identify Greedy Patterns:** Recognize problems solvable by Greedy approaches (e.g., Interval Scheduling, Huffman Coding).
    **識別貪婪模式：** 辨識可用貪婪策略解決的問題（例如區間排程、霍夫曼編碼）。
*   **Differentiate from DP:** Clearly distinguish when to use Greedy versus Dynamic Programming (DP).
    **區分貪婪與動態規劃：** 清楚分辨何時該使用貪婪演算法，何時該使用動態規劃（DP）。
*   **Master Proof of Correctness (Intuitively):** Learn to validate your Greedy logic using "Exchange Arguments" or counter-examples.
    **掌握正確性證明（直覺層面）：** 學習使用「交換論證」或反例來驗證貪婪邏輯。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A Greedy algorithm builds up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法透過逐步構建解決方案，總是選擇在當下能提供最大即時利益的下一步。

It relies on the **Greedy Choice Property** and **Optimal Substructure**.
它依賴於 **貪婪選擇性質** 與 **最佳子結構**。

### Intuition (直覺)
Think of it as "living in the moment." You don't worry about the future consequences; you just take the best deal available right now.
將其視為「活在當下」。你不擔心未來的後果，只選取眼前可得的最佳交易。

### Complexity (複雜度)
*   **Time:** Often $O(N \log N)$ (dominated by sorting) or $O(N)$ (if using a heap/priority queue efficiently or if input is pre-sorted).
    **時間：** 通常為 $O(N \log N)$（主要消耗在排序），或 $O(N)$（若有效利用堆積/優先佇列，或輸入已排序）。
*   **Space:** Usually $O(1)$ or $O(N)$ depending on whether auxiliary structures are needed.
    **空間：** 通常為 $O(1)$ 或 $O(N)$，取決於是否需要輔助結構。

### When to Use (適用場景)
*   Optimization problems where local decisions do not restrict future optimal solutions.
    最佳化問題，且當下的決策不會限制未來的最佳解。
*   Common domains: Interval scheduling, Minimum Spanning Trees (Prim/Kruskal), Dijkstra's algorithm.
    常見領域：區間排程、最小生成樹（Prim/Kruskal）、Dijkstra 演算法。

### When NOT to Use (不適用場景)
*   When a local "bad" choice is necessary to achieve a global "good" outcome (e.g., 0/1 Knapsack Problem, Longest Path).
    當必須做出局部的「壞」選擇才能達成全域的「好」結果時（例如：0/1 背包問題、最長路徑）。
*   In these cases, DP or Backtracking is required.
    在這些情況下，需要使用動態規劃或回溯法。

---

## 3. Typical Patterns (典型題型 / 模式)

Even at a beginner level, recognizing these patterns is crucial for Seniors to quickly categorize problems.
即使在初級階段，識別這些模式對於資深工程師快速分類問題至關重要。

1.  **Sorting + Iteration (排序 + 迭代):**
    Sort the input (by start time, end time, size, etc.) and iterate linearly to make choices.
    將輸入排序（依開始時間、結束時間、大小等），並線性迭代以做出選擇。
    *   *Example: Meeting Rooms, Assign Cookies.*

2.  **Priority Queue / Heap (優先佇列 / 堆積):**
    Dynamically select the minimum or maximum element available at the current state.
    動態選擇當前狀態下可用的最小或最大元素。
    *   *Example: Merge K Sorted Lists (can be seen as greedy), Task Scheduler.*

3.  **Two Pointers (Starts/Ends) (雙指針):**
    Often used in conjunction with sorting to match elements from two ends or arrays.
    常與排序結合使用，以匹配兩端或兩個陣列中的元素。
    *   *Example: Boats to Save People.*

4.  **From End to Start (逆向思考):**
    Sometimes solving the problem backwards simplifies the greedy choice.
    有時逆向解決問題能簡化貪婪選擇。
    *   *Example: Jump Game II (sometimes), Reconstruct Queue by Height.*

---

## 4. Example Walkthrough (範例講解)

### Problem: Jump Game (LeetCode 55)
**Problem Statement:**
You are given an integer array `nums`. You are initially positioned at the array's **first index**. Each element in the array represents your maximum jump length at that position. Return `true` if you can reach the last index, or `false` otherwise.
**問題重述：**
給定一個整數陣列 `nums`。你最初位於陣列的 **第一個索引**。陣列中的每個元素代表你在該位置的最大跳躍長度。如果你能到達最後一個索引，則回傳 `true`，否則回傳 `false`。

### Approach 1: Backtracking (Brute Force)
**思路：暴力解（回溯法）**
Try every possible jump from every position. This is exhaustive.
嘗試從每個位置出發的所有可能跳躍。這是窮舉法。
*   **Complexity:** $O(2^N)$. This will Time Out (TLE).
    **複雜度：** $O(2^N)$。這會導致超時（TLE）。

### Approach 2: Greedy (Optimal)
**思路：貪婪（最佳解）**
Instead of trying all jumps, we only care about the **maximum reach**.
與其嘗試所有跳躍，我們只關心 **最遠能到達的位置**。
As we iterate through the array, we update the farthest index we can reach. If the current index is reachable, we update our "max reach".
當我們遍歷陣列時，更新我們能到達的最遠索引。如果當前索引是可到達的，我們就更新「最大到達範圍」。

### Java Solution (Reference)

```java
class Solution {
    public boolean canJump(int[] nums) {
        // 'reachable' tracks the furthest index we can currently reach.
        // 'reachable' 追蹤我們目前能到達的最遠索引。
        int reachable = 0;

        for (int i = 0; i < nums.length; i++) {
            // If the current index 'i' is greater than 'reachable',
            // it means we cannot reach this step from any previous step.
            // 如果當前索引 'i' 大於 'reachable'，
            // 這意味著我們無法從之前的任何步驟到達此處。
            if (i > reachable) {
                return false;
            }

            // Update the furthest reachable index.
            // The choice is greedy: at index i, we take the max jump possible (i + nums[i]).
            // 更新最遠可達索引。
            // 這是貪婪選擇：在索引 i，我們取可能的最大跳躍（i + nums[i]）。
            reachable = Math.max(reachable, i + nums[i]);
            
            // Optimization: If we can already reach the end, stop early.
            // 優化：如果我們已經能到達終點，提早結束。
            if (reachable >= nums.length - 1) {
                return true;
            }
        }

        return true;
    }
}
```

### Analysis (分析)
*   **Time Complexity:** $O(N)$. We iterate through the array once.
    **時間複雜度：** $O(N)$。我們遍歷陣列一次。
*   **Space Complexity:** $O(1)$. No extra space needed.
    **空間複雜度：** $O(1)$。不需要額外空間。

### Why Greedy works here? (為何貪婪法有效？)
Because reaching a further index never hurts. Being at index `k` implies you could also be at any index `< k`. Therefore, maximizing `k` encompasses all sub-possibilities.
因為到達更遠的索引永遠沒有壞處。處於索引 `k` 意味著你也可能處於任何小於 `k` 的索引。因此，最大化 `k` 涵蓋了所有子可能性。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Greedy (貪婪) | Dynamic Programming (動態規劃) |
| :--- | :--- | :--- |
| **Decision Type** | Makes the best choice *now* and never looks back. <br> 做出*當下*最佳選擇，且絕不回頭。 | Considers all choices and builds from sub-problems. <br> 考慮所有選擇，並從子問題構建。 |
| **Backtracking** | No. Once a choice is made, it's final. <br> 否。一旦做出選擇，即為定局。 | Implicitly yes (via memoization/tabulation). <br> 隱含地是（透過記憶法/列表法）。 |
| **Correctness** | Harder to prove. Requires specific properties. <br> 較難證明。需要特定性質。 | Guaranteed if transitions are correct. <br> 若轉移方程正確，則保證正確。 |
| **Trap** | **"The Short-Sighted Trap"**: Choosing the largest immediate value might block a massive value later. <br> **「短視陷阱」**：選擇當前最大值可能會阻礙後續獲得巨大價值。 | **"Over-Engineering"**: Using DP for a problem solvable by Greedy is inefficient. <br> **「過度設計」**：對可用貪婪解決的問題使用 DP 是低效的。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Hypothesize:** "This looks like an optimization problem. I suspect a Greedy approach might work because [reason]."
    **假設：** 「這看起來像是一個最佳化問題。我懷疑貪婪方法可能有效，因為 [理由]。」
2.  **Validate:** "Let's try a simple example. If I always choose X, does it prevent me from getting Y?"
    **驗證：** 「讓我們試一個簡單的例子。如果我總是選擇 X，這會阻止我得到 Y 嗎？」
3.  **Refine:** "Since sorting the input simplifies the decision process, I'll start by sorting."
    **優化：** 「由於排序輸入能簡化決策過程，我將從排序開始。」

### Whiteboard Strategy (白板策略)
*   **Sort First:** If the data isn't sorted, ask if you can sort it. Write `Arrays.sort()` clearly.
    **先排序：** 如果數據未排序，詢問是否可以排序。清楚寫下 `Arrays.sort()`。
*   **Variable Naming:** Use descriptive names like `maxReach`, `currentEnd`, `intervals`. Avoid `i`, `j`, `k` for logic variables.
    **變數命名：** 使用具描述性的名稱，如 `maxReach`、`currentEnd`、`intervals`。避免在邏輯變數使用 `i`、`j`、`k`。

### Common Follow-ups (常見追問)
*   "Can you prove this works?" (Use a counter-example logic: "If there existed a better solution that didn't take this step...")
    「你能證明這行得通嗎？」（使用反例邏輯：「如果存在一個不採取此步驟的更好解法……」）
*   "What if the input is a stream?" (Suggest using a Heap/PriorityQueue).
    「如果輸入是串流怎麼辦？」（建議使用堆積/優先佇列）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Assign Cookies (LeetCode 455)
*   **Prompt:** Give each child at most one cookie. Maximize the number of content children.
    **題目：** 每個孩子最多給一塊餅乾。最大化滿足的孩子數量。
*   **Hint:** Sort both children (greed factor) and cookies (size). Match smallest appetite with smallest sufficient cookie.
    **提示：** 將孩子（貪婪因子）和餅乾（大小）都排序。將最小胃口與最小足夠的餅乾匹配。
*   **Key Concept:** Sorting + Two Pointers.
    **關鍵概念：** 排序 + 雙指針。

### 2. Medium: Best Time to Buy and Sell Stock II (LeetCode 122)
*   **Prompt:** You can buy and sell as many times as you want. Maximize profit.
    **題目：** 你可以買賣任意次數。最大化利潤。
*   **Hint:** If tomorrow's price is higher than today's, buy today and sell tomorrow. Capture every upward slope.
    **提示：** 如果明天的價格高於今天，今天買明天賣。捕捉每一個上升坡段。
*   **Key Concept:** Accumulate local positives.
    **關鍵概念：** 累積局部正值。

### 3. Medium/Hard: Gas Station (LeetCode 134)
*   **Prompt:** Find the starting gas station to travel around the circuit once.
    **題目：** 找出能繞行一圈的起始加油站。
*   **Hint:** If you can't reach station B from station A, you can't reach B from any station between A and B. Reset start point.
    **提示：** 如果你無法從 A 站到達 B 站，那你也無法從 A 和 B 之間的任何站到達 B。重置起點。
*   **Key Concept:** Greedy elimination of impossible start points.
    **關鍵概念：** 貪婪地排除不可能的起點。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

- [ ] **Sorting:** Did I consider sorting the input? It's the prerequisite for 80% of greedy problems.
    **排序：** 我是否考慮過排序輸入？這是 80% 貪婪問題的先決條件。
- [ ] **Counter-Example:** Can I construct a case where taking the biggest item now leads to failure?
    **反例：** 我能否建構一個案例，顯示現在拿最大的項目會導致失敗？
- [ ] **Edge Cases:** What if the array is empty? What if all values are identical?
    **邊界情況：** 如果陣列為空怎麼辦？如果所有值都相同怎麼辦？
- [ ] **Complexity:** Is my sorting $O(N \log N)$ acceptable given the constraints ($N < 10^5$)?
    **複雜度：** 考慮到限制條件（$N < 10^5$），我的排序 $O(N \log N)$ 可接受嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Hiking" Analogy (登山類比)
*   **Greedy:** You are hiking in thick fog. You always take the step that goes steepest upwards. You might reach the peak (Global Optimum), or you might get stuck on a small hill (Local Optimum).
    **貪婪：** 你在濃霧中登山。你總是邁出最陡峭向上的一步。你可能會到達頂峰（全域最佳解），也可能被困在一個小山丘上（局部最佳解）。
*   **Lesson:** Greedy works best for "Convex" problems (single peak).
    **教訓：** 貪婪法最適用於「凸性」問題（單一頂峰）。

### The "Cashier" Analogy (收銀員類比)
*   **Change Making:** When giving change, you instinctively grab the largest bill possible first (e.g., $20, then $10, then $1). This is a Greedy algorithm that works for standard currency systems.
    **找零：** 找零時，你本能地先拿最大的鈔票（如 $20，然後 $10，然後 $1）。這是一個適用於標準貨幣系統的貪婪演算法。

### Visual Anchor (視覺錨點)
*   **Jump Game:** Imagine a "horizon" line moving forward. You only care about pushing that line as far right as possible.
    **跳躍遊戲：** 想像一條向前移動的「地平線」。你只關心將那條線盡可能向右推。