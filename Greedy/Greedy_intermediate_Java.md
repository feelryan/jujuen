Here is the complete interview preparation guide for **Greedy Algorithms**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level with **Java** implementation.

這是一份針對 **貪婪演算法（Greedy Algorithms）** 的完整面試準備教材，專為資深軟體工程師設計，鎖定 **中階（Intermediate）** 難度，並使用 **Java** 實作。

---

# Greedy Algorithms: Interview Strategy & Practice Guide
# 貪婪演算法：面試策略與實戰指南

## 1. Learning Goals（學習目標）

*   **Distinguish between Greedy and Dynamic Programming (DP).**
    能夠區分貪婪演算法與動態規劃（DP）的差異。
    *(Greedy makes a final choice at each step; DP considers all choices and looks back.)*
    *（貪婪在每一步做出最終選擇；DP 考慮所有選擇並回溯。）*

*   **Master the "Sort & Iterate" pattern.**
    掌握「排序後遍歷」的解題模式。
    *(Most intermediate greedy problems require sorting the input first to reveal the optimal path.)*
    *（大多數中階貪婪問題需要先對輸入進行排序，以顯現最佳路徑。）*

*   **Learn to justify correctness using the "Exchange Argument".**
    學會使用「交換論證法」來證明解法的正確性。
    *(Understand why the local optimal choice leads to the global optimum without rigorous mathematical proof.)*
    *（理解為何局部最佳選擇能導致全域最佳解，而無需嚴格的數學證明。）*

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
**Greedy Algorithm** builds up a solution piece by piece, always choosing the next piece that offers the most obvious and immediate benefit.
**貪婪演算法** 透過一步步構建解法，總是選擇在當下能提供最明顯、最即時利益的那個選項。

### Intuition（直覺）
It is like hiking down a mountain in thick fog; you look at your immediate surroundings and take the step that goes down the steepest slope.
這就像在濃霧中下山；你觀察周圍的環境，並邁出坡度最陡峭向下的那一步。

### Key Properties（關鍵屬性）
1.  **Greedy Choice Property（貪婪選擇屬性）**: A global optimum can be arrived at by selecting a local optimum.
    透過選擇局部最佳解，最終可以達成全域最佳解。
2.  **Optimal Substructure（最佳子結構）**: An optimal solution to the problem contains an optimal solution to subproblems.
    問題的最佳解包含其子問題的最佳解。

### Complexity（複雜度）
*   **Time**: Often $O(N \log N)$ due to sorting, or $O(N)$ if using a linear scan/Priority Queue.
    **時間**：通常為 $O(N \log N)$，因為需要排序，若使用線性掃描或優先佇列則為 $O(N)$。
*   **Space**: Usually $O(1)$ or $O(N)$ depending on whether we store the output or sort in place.
    **空間**：通常為 $O(1)$ 或 $O(N)$，取決於我們是否儲存輸出結果或進行原地排序。

### When to Use vs. Not to Use（適用與不適用場景）
*   **Use**: Interval scheduling, Minimum Spanning Trees (Prim/Kruskal), Dijkstra, Huffman Coding.
    **適用**：區間排程、最小生成樹（Prim/Kruskal）、Dijkstra、霍夫曼編碼。
*   **Not Use**: When a choice depends on future consequences that cannot be predicted locally (e.g., 0/1 Knapsack).
    **不適用**：當選擇取決於無法在局部預測的未來後果時（例如：0/1 背包問題）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Interval Scheduling (Sort by End Time)
### 區間排程（依結束時間排序）
*   **Scenario**: Selecting the maximum number of non-overlapping events.
    **場景**：選擇最大數量的互不重疊事件。
*   **Strategy**: Sort intervals by their **end time**. Always pick the one that ends earliest to leave space for future events.
    **策略**：依據**結束時間**排序區間。總是選擇最早結束的那個，以便為未來的事件留出空間。

### B. Merge Intervals (Sort by Start Time)
### 合併區間（依開始時間排序）
*   **Scenario**: Merging overlapping intervals or counting coverage.
    **場景**：合併重疊區間或計算覆蓋範圍。
*   **Strategy**: Sort by **start time**. Iterate and extend the current interval if the next one overlaps.
    **策略**：依據**開始時間**排序。遍歷並在下一個區間重疊時延伸當前區間。

### C. Greedy on Arrays (Two Pointers / Peaks)
### 陣列上的貪婪（雙指針 / 波峰）
*   **Scenario**: Stock trading, jumping games, water containers.
    **場景**：股票交易、跳躍遊戲、盛水容器。
*   **Strategy**: Make the move that maximizes current gain or reach.
    **策略**：做出能最大化當前收益或可達範圍的移動。

---

## 4. Example Walkthrough（範例講解）

### Problem: Non-overlapping Intervals (LeetCode 435)
### 問題：無重疊區間

**Problem Statement:**
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the *minimum* number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳為了讓其餘區間互不重疊，所需移除的*最小*區間數量。

---

### Approach 1: Brute Force (Recursion)
### 思路 1：暴力解（遞迴）

Try all possible subsets of intervals, check if they overlap, and find the largest valid subset.
嘗試所有可能的區間子集，檢查它們是否重疊，並找出最大的有效子集。

*   **Complexity**: $O(2^N)$. This is unacceptable for $N > 20$.
    **複雜度**：$O(2^N)$。這對於 $N > 20$ 的情況是不可接受的。

---

### Approach 2: Dynamic Programming
### 思路 2：動態規劃

Sort by start time. Let $DP[i]$ be the max non-overlapping intervals ending at index $i$.
依開始時間排序。設 $DP[i]$ 為以索引 $i$ 結束的最大無重疊區間數。

*   **Complexity**: $O(N^2)$. Better, but still slow for $N=10^5$.
    **複雜度**：$O(N^2)$。好一點，但對於 $N=10^5$ 來說仍然太慢。

---

### Approach 3: Greedy (Optimal Solution)
### 思路 3：貪婪演算法（最佳解）

**Core Insight**: To minimize removals, we must **maximize the number of intervals we keep**.
**核心洞察**：為了最小化移除數量，我們必須**最大化保留的區間數量**。

To keep as many as possible, we should always pick the interval that **ends the earliest**. Why? Because it leaves the most "room" for subsequent intervals.
為了保留盡可能多的區間，我們應該總是選擇**最早結束**的區間。為什麼？因為這為後續的區間留下了最多的「空間」。

**Algorithm**:
1.  Sort intervals by **end time**.
    依**結束時間**對區間進行排序。
2.  Select the first interval (earliest end time).
    選擇第一個區間（最早結束）。
3.  Iterate through the rest: if an interval starts *after* the current one ends, keep it and update the end time. Otherwise, it's an overlap, so we "remove" it (increment count).
    遍歷其餘區間：如果一個區間的開始時間在當前區間結束*之後*，保留它並更新結束時間。否則，視為重疊，我們將其「移除」（計數加一）。

---

### Java Solution (Bilingual Comments)
### Java 參考解（雙語註解）

```java
import java.util.Arrays;
import java.util.Comparator;

class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        // Edge case: Empty array
        // 邊界條件：空陣列
        if (intervals.length == 0) return 0;

        // Sort by end time (Ascending)
        // 依結束時間排序（升序）
        // Using Integer.compare is safer than a - b to avoid overflow, though not strictly needed here for valid ranges.
        // 使用 Integer.compare 比 a - b 更安全以避免溢位，雖然在此題有效範圍內不一定需要。
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));

        // Initialize the end time of the last added interval
        // 初始化最後加入區間的結束時間
        int end = intervals[0][1];
        
        // Count of intervals to remove
        // 需移除的區間計數
        int count = 0;

        // Iterate starting from the second interval
        // 從第二個區間開始遍歷
        for (int i = 1; i < intervals.length; i++) {
            // If the current interval starts before the previous one ends, it's an overlap.
            // 如果當前區間在由前一個區間結束之前就開始，則發生重疊。
            if (intervals[i][0] < end) {
                // We greedily "remove" this current interval because it ends later (or same time) 
                // than our current 'end', and we want to minimize end times.
                // 我們貪婪地「移除」當前這個區間，因為它結束得比我們目前的 'end' 晚（或相同），
                // 而我們希望最小化結束時間。
                count++;
            } else {
                // No overlap, update the end time to this interval's end.
                // 無重疊，將結束時間更新為此區間的結束時間。
                end = intervals[i][1];
            }
        }

        return count;
    }
}
```

**Complexity Analysis**:
*   **Time**: $O(N \log N)$ due to sorting. The iteration is $O(N)$.
    **時間**：$O(N \log N)$，歸因於排序。遍歷過程為 $O(N)$。
*   **Space**: $O(\log N)$ or $O(N)$ used by Java's internal sort stack (Timsort).
    **空間**：$O(\log N)$ 或 $O(N)$，取決於 Java 內部排序堆疊（Timsort）的使用。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision** | Makes the best choice *now* and never looks back. <br> 做出*當下*最佳選擇且永不回頭。 | Considers all choices and their future consequences. <br> 考慮所有選擇及其未來後果。 |
| **Backtracking** | No. <br> 否。 | Yes (implicitly via recursion or table look-up). <br> 是（隱含於遞迴或查表）。 |
| **Example** | **Fractional** Knapsack (Take highest value/weight ratio). <br> **分數**背包問題（取最高價值/重量比）。 | **0/1** Knapsack (Must take whole item or none). <br> **0/1** 背包問題（必須全取或不取）。 |
| **Failure Mode** | Fails if local optimum $\neq$ global optimum. <br> 若局部最佳 $\neq$ 全域最佳，則失敗。 | Fails if state space is too large (Memory Limit). <br> 若狀態空間過大則失敗（記憶體限制）。 |

**Crucial Pitfall**: Sorting by **Start Time** vs **End Time**.
**關鍵陷阱**：依**開始時間**還是**結束時間**排序。
*   In "Non-overlapping Intervals", sorting by *start time* fails because a very long interval starting early can block many short intervals.
    在「無重疊區間」中，依*開始時間*排序會失敗，因為一個很早開始的長區間可能會擋住許多短區間。
*   In "Merge Intervals", sorting by *start time* is correct because we just need to find connectivity.
    在「合併區間」中，依*開始時間*排序是正確的，因為我們只需要找出連通性。

---

## 6. Interview Strategy（面試實戰建議）

### 1. Don't shout "Greedy!" immediately.
### 不要立刻大喊「這是貪婪演算法！」
Start by analyzing the problem. Say: "It looks like an optimization problem. I could try DP, but let's see if a greedy choice property holds."
從分析問題開始。說：「這看起來像是一個最佳化問題。我可以嘗試 DP，但我們先看看貪婪選擇屬性是否成立。」

### 2. Use Counter-Examples (The "Disproof" Method).
### 使用反例（「反證」法）。
When you propose a greedy strategy (e.g., "pick the largest number first"), immediately try to break it with a small example.
當你提出貪婪策略時（例如：「先選最大的數字」），立刻嘗試用一個小範例去推翻它。
*   *Interviewer:* "Good habit."
    *面試官：「好習慣。」*

### 3. The "Exchange Argument" (For Bonus Points).
### 「交換論證法」（加分項）。
If asked "Why does this work?", explain: "If we have an optimal solution that *doesn't* use our greedy choice, we can swap a part of it with our greedy choice without making the solution worse. Thus, our greedy choice is safe."
若被問到「為什麼這行得通？」，解釋：「如果有一個最佳解*沒有*使用我們的貪婪選擇，我們可以將其一部分與我們的貪婪選擇交換，而不會讓解變差。因此，我們的貪婪選擇是安全的。」

---

## 7. Practice Problems（練習題）

### Level: Easy (Warm-up)
**Problem**: **Assign Cookies (LeetCode 455)**
**Hint**: Sort both children (greed factor) and cookies (size). Give the smallest sufficient cookie to the child with the smallest greed.
**提示**：對孩子（貪婪因子）和餅乾（尺寸）都進行排序。將最小且足夠的餅乾分給貪婪度最小的孩子。

### Level: Intermediate (Core)
**Problem**: **Jump Game (LeetCode 55)** or **Jump Game II (LeetCode 45)**
**Hint**:
*   *Jump Game*: Track the `maxReach`. If `i > maxReach`, you can't proceed.
    *跳躍遊戲*：追蹤 `maxReach`。如果 `i > maxReach`，則無法繼續。
*   *Jump Game II*: Implicit BFS. Update the range `[curBegin, curEnd]` for the current jump level.
    *跳躍遊戲 II*：隱式 BFS。更新當前跳躍層級的範圍 `[curBegin, curEnd]`。

### Level: Advanced (Challenge)
**Problem**: **Gas Station (LeetCode 134)**
**Hint**: If you can't travel from A to B, you can't travel from any station between A and B to B. Reset start point to `i + 1`.
**提示**：如果你無法從 A 走到 B，那麼你也無法從 A 和 B 之間的任何站點走到 B。將起點重置為 `i + 1`。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Sorting**: Did I sort the input? If so, based on what criteria (start time, end time, size, cost)?
    **排序**：我是否對輸入進行了排序？如果是，基於什麼標準（開始時間、結束時間、大小、成本）？
*   [ ] **Local Decision**: Does my choice at step `i` restrict valid choices for `i+1` in a way that might miss the optimal solution? (If yes, use DP).
    **局部決策**：我在步驟 `i` 的選擇是否會限制 `i+1` 的有效選擇，從而導致錯過最佳解？（如果是，請使用 DP）。
*   [ ] **Complexity**: Is my sorting $O(N \log N)$ dominating the logic? Is the rest linear $O(N)$?
    **複雜度**：我的排序 $O(N \log N)$ 是否主導了邏輯？其餘部分是否為線性 $O(N)$？
*   [ ] **Edge Cases**: Empty array? Single element? All intervals overlapping?
    **邊界條件**：空陣列？單一元素？所有區間重疊？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Cashier Analogy (Change Making)
### 收銀員類比（找零錢）
Imagine you are a cashier giving change for $0.99 using the fewest coins.
想像你是收銀員，要用最少的硬幣找零 $0.99。
*   **Greedy**: You automatically grab the largest coin possible (0.25) repeatedly until you can't, then the next largest (0.10). This works for standard currency systems.
    **貪婪**：你會自動抓取盡可能大的硬幣（0.25），直到無法再取，然後取下一個最大的（0.10）。這在標準貨幣系統中有效。
*   **Non-Greedy System**: If coins were 1, 3, 4 and you need to make 6. Greedy takes 4, then 1, 1 (3 coins). Optimal is 3, 3 (2 coins).
    **非貪婪系統**：如果硬幣是 1、3、4，而你要湊 6。貪婪會拿 4，然後 1、1（3 枚）。最佳解是 3、3（2 枚）。

**Anchor**: **"Greedy is short-sighted."** It works perfectly when the path ahead is predictable (like standard coins or sorted intervals), but fails in complex mazes (like generic knapsacks).
**錨點**：**「貪婪是短視的。」** 當前方路徑可預測時（如標準硬幣或已排序區間），它完美運作；但在複雜迷宮中（如一般背包問題）則會失敗。