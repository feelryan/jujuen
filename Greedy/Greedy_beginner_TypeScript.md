# Greedy Algorithms: Foundational Mastery for Senior Engineers
# 貪婪演算法：資深工程師的基礎精通指南

## 1. Learning Objectives（學習目標）

1.  **Understand the Core Philosophy**: Grasp how making locally optimal choices can lead to a global optimum without backtracking.
    **理解核心哲學**：掌握如何透過做出局部最佳選擇，在不回溯的情況下達成全域最佳解。

2.  **Identify Greedy Scenarios**: Recognize patterns (like intervals or partitioning) where Greedy is applicable versus where Dynamic Programming is required.
    **識別貪婪場景**：辨識適用貪婪演算法的模式（如區間或分割問題），並區分何時需要動態規劃。

3.  **Master the "Sort & Iterate" Pattern**: Learn why sorting is often the precursor to a greedy solution and how to determine the sorting criteria.
    **精通「排序與迭代」模式**：學習為何排序通常是貪婪解法的前置步驟，以及如何決定排序的標準。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
A Greedy algorithm builds up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法透過一步步建構解法，總是選擇在當下能提供最大即時利益的那個部分。

It relies on the **Greedy Choice Property** (local optimality leads to global optimality) and **Optimal Substructure**.
它依賴於 **貪婪選擇性質**（局部最佳性導向全域最佳性）與 **最佳子結構**。

### Intuition（直覺）
Imagine you are a cashier trying to give change using the fewest number of coins.
想像你是收銀員，試圖用最少數量的硬幣找零。
You naturally take the largest denomination coin possible first, then the next largest, and so on.
你會自然地先拿面額最大的硬幣，然後是次大的，依此類推。

### Complexity（複雜度）
*   **Time**: Usually $O(N \log N)$ due to sorting, or $O(N)$ if the input is already sorted or a heap is used.
    **時間**：通常為 $O(N \log N)$，因為需要排序；若輸入已排序或使用堆積（Heap），則為 $O(N)$。
*   **Space**: Usually $O(1)$ or $O(N)$ depending on whether we store the output or modify in-place.
    **空間**：通常為 $O(1)$ 或 $O(N)$，取決於我們是儲存輸出還是原地修改。

### When to Use vs. Not Use（適用與不適用場景）
*   **Use when**: The problem asks for a maximum/minimum, and a decision made now never needs to be revisited (no future consequences invalidate current choices).
    **適用時機**：問題要求最大值/最小值，且當下所做的決定永遠不需要重新檢視（未來的後果不會讓當前的選擇無效）。
*   **Do NOT use when**: Constraints interact in complex ways (e.g., 0/1 Knapsack Problem), requiring you to "look ahead" or try all combinations.
    **不適用時機**：約束條件以複雜的方式交互作用（例如 0/1 背包問題），需要你「向前看」或嘗試所有組合。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Interval Scheduling (Activity Selection)
**區間排程（活動選擇）**
*   **Concept**: Given a set of intervals, find the max number of non-overlapping intervals.
    **概念**：給定一組區間，找出最大數量的互不重疊區間。
*   **Key**: Sort by **end time**.
    **關鍵**：依據 **結束時間** 排序。

### B. Simple Array Partitioning / Allocation
**簡單陣列分割 / 分配**
*   **Concept**: Assign resources (cookies, gas) to demands (children, cost) to maximize satisfaction.
    **概念**：將資源（餅乾、汽油）分配給需求（孩童、成本）以最大化滿意度。
*   **Key**: Sort both arrays or use a Two-Pointer approach.
    **關鍵**：將兩個陣列排序，或使用雙指針法。

### C. Subarray / Subsequence Optimization
**子陣列 / 子序列優化**
*   **Concept**: Problems like "Jump Game" or "Maximum Subarray".
    **概念**：諸如「跳躍遊戲」或「最大子陣列」的問題。
*   **Key**: Track the "farthest reach" or "current sum" dynamically.
    **關鍵**：動態追蹤「最遠可達距離」或「當前總和」。

---

## 4. Example Walkthrough（範例講解）

### Problem: Non-overlapping Intervals (LeetCode 435)
**問題：無重疊區間**

### Problem Restatement（問題重述）
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳你需要移除的最小區間數量，使剩餘的區間互不重疊。

### Approach: Brute Force $\to$ Optimization（思路：暴力 $\to$ 優化）

1.  **Brute Force**: Try every combination of intervals, check if they overlap, and count the max valid set. Complexity is exponential $O(2^N)$.
    **暴力法**：嘗試區間的所有組合，檢查它們是否重疊，並計算最大的有效集合。複雜度是指數級 $O(2^N)$。

2.  **Greedy Intuition**: To keep as many intervals as possible, we should finish an interval as early as possible to leave room for the next ones.
    **貪婪直覺**：為了保留盡可能多的區間，我們應該儘早結束一個區間，以便為下一個區間留出空間。

3.  **The Strategy**: Sort by **end time**. Pick the first one. Then pick the next one that starts *after* the previous one ends.
    **策略**：依據 **結束時間** 排序。選取第一個。然後選取下一個「開始時間」晚於前一個「結束時間」的區間。

### Why Sort by End Time?（為何依結束時間排序？）
*   If we sort by start time, a very long interval might start early but block everyone else.
    如果我們依開始時間排序，一個非常長的區間可能很早開始，但會擋住其他所有人。
*   Sorting by end time guarantees we leave the maximum capacity for future intervals.
    依結束時間排序保證我們為未來的區間留出最大容量。

### TypeScript Solution（TypeScript 參考解）

```typescript
function eraseOverlapIntervals(intervals: number[][]): number {
    // Edge case: if empty, no removal needed
    // 邊界條件：若是空的，不需要移除
    if (intervals.length === 0) return 0;

    // Sort intervals by their end time in ascending order
    // 將區間依據結束時間由小到大排序
    intervals.sort((a, b) => a[1] - b[1]);

    // Initialize the end time of the last added interval
    // 初始化最後加入區間的結束時間
    // We pick the first interval (after sorting) as part of our non-overlapping set
    // 我們選取排序後的第一個區間作為無重疊集合的一部分
    let prevEnd = intervals[0][1];
    
    // Count of intervals to remove
    // 計算需要移除的區間數量
    let removeCount = 0;

    // Iterate starting from the second interval
    // 從第二個區間開始迭代
    for (let i = 1; i < intervals.length; i++) {
        const [currentStart, currentEnd] = intervals[i];

        if (currentStart < prevEnd) {
            // Overlap detected!
            // 偵測到重疊！
            // Since we sorted by end time, the current interval ends later or equal to prevEnd.
            // 因為我們依結束時間排序，當前區間的結束時間晚於或等於 prevEnd。
            // To minimize removals (maximize kept), we keep the one that ends earlier (prevEnd).
            // 為了最小化移除數（最大化保留數），我們保留結束較早的那個（prevEnd）。
            // Therefore, we remove the current one.
            // 因此，我們移除當前的這個。
            removeCount++;
        } else {
            // No overlap.
            // 無重疊。
            // We can keep this interval, so we update the end boundary.
            // 我們可以保留此區間，所以更新結束邊界。
            prevEnd = currentEnd;
        }
    }

    return removeCount;
}
```

### Complexity Analysis（複雜度分析）
*   **Time**: $O(N \log N)$ dominated by the sorting step. The iteration is $O(N)$.
    **時間**：$O(N \log N)$，主要由排序步驟決定。迭代過程為 $O(N)$。
*   **Space**: $O(1)$ or $O(\log N)$ depending on the sorting implementation's stack usage.
    **空間**：$O(1)$ 或 $O(\log N)$，取決於排序實作的堆疊使用量。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision**<br>**決策** | Makes the best choice *now* and never looks back.<br>做出*當下*最佳選擇且絕不回頭。 | Considers all choices and their consequences (often via recursion/memoization).<br>考慮所有選擇及其後果（通常透過遞迴/記憶法）。 |
| **Correctness**<br>**正確性** | Hard to prove (requires mathematical intuition).<br>難以證明（需要數學直覺）。 | Guaranteed to find optimal if state transitions are correct.<br>若狀態轉移正確，保證找到最佳解。 |
| **Example**<br>**範例** | Fractional Knapsack (Take highest value/weight ratio).<br>分數背包問題（拿取最高價值/重量比）。 | 0/1 Knapsack (Must take whole item or nothing).<br>0/1 背包問題（必須拿取整個物品或不拿）。 |

**Trap**: Applying Greedy to "Coin Change" with arbitrary coins (e.g., coins [1, 3, 4], target 6).
**陷阱**：將貪婪法應用於任意面額的「找零問題」（例如硬幣 [1, 3, 4]，目標 6）。
*   **Greedy**: 4 + 1 + 1 (3 coins).
    **貪婪解**：4 + 1 + 1（3 枚硬幣）。
*   **Optimal (DP)**: 3 + 3 (2 coins).
    **最佳解（DP）**：3 + 3（2 枚硬幣）。
*   **Lesson**: Greedy only works for "canonical" coin systems (like US dollars).
    **教訓**：貪婪法僅適用於「標準」貨幣系統（如美元）。

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Propose Greedy**: "This looks like an optimization problem. My intuition suggests a greedy approach where we..."
    **提出貪婪法**：「這看起來像個最佳化問題。我的直覺建議使用貪婪法，我們可以...」
2.  **Justify Choice**: "If we sort by $X$, picking the top element leaves us the most resources for the rest."
    **證成選擇**：「如果我們依據 $X$ 排序，選取頂端元素能為剩餘部分保留最多資源。」
3.  **Check Counter-examples**: "Before coding, let me quickly check if a local optimum could block a global solution."
    **檢查反例**：「在寫程式碼之前，讓我快速檢查局部最佳解是否會阻礙全域解。」

### Whiteboard Strategy（白板策略）
*   Draw a timeline for interval problems.
    針對區間問題，畫出一條時間軸。
*   Write down the sorting criteria clearly (e.g., `Sort: A[i].end ASC`).
    清楚寫下排序標準（例如：`Sort: A[i].end ASC`）。

### Common Follow-ups（常見追問）
*   "What if the input is a stream (cannot sort)?" $\to$ Use a Heap/Priority Queue.
    「如果輸入是串流（無法排序）怎麼辦？」$\to$ 使用堆積/優先佇列。
*   "Can you prove why this works?" $\to$ Use "Exchange Argument" (Assume there is an optimal solution that differs, show that swapping our choice in makes it no worse).
    「你能證明為何這行得通嗎？」$\to$ 使用「交換論證」（假設有一個不同的最佳解，證明將我們的選擇交換進去不會讓結果變差）。

---

## 7. Practice Problems（練習題）

### Easy: Assign Cookies (LeetCode 455)
*   **Problem**: Maximize content children given cookie sizes and greed factors.
    **問題**：給定餅乾大小與貪婪因子，最大化滿足的孩童數量。
*   **Hint**: Sort both. Give the smallest cookie that satisfies the least greedy child.
    **提示**：兩者皆排序。給予能滿足最小貪婪孩童的最小餅乾。
*   **Focus**: Basic sorting and two-pointer iteration.
    **重點**：基礎排序與雙指針迭代。

### Medium: Jump Game (LeetCode 55)
*   **Problem**: Can you reach the last index?
    **問題**：你能到達最後一個索引嗎？
*   **Hint**: Track `maxReach`. Iterate through array; if `i > maxReach`, you failed. Update `maxReach = max(maxReach, i + nums[i])`.
    **提示**：追蹤 `maxReach`。迭代陣列；若 `i > maxReach`，則失敗。更新 `maxReach = max(maxReach, i + nums[i])`。
*   **Focus**: Dynamic updating of a greedy constraint.
    **重點**：貪婪約束的動態更新。

### Hard (Conceptually): Gas Station (LeetCode 134)
*   **Problem**: Find the starting gas station to complete a circuit.
    **問題**：找出能完成繞行一圈的起始加油站。
*   **Hint**: If total gas < total cost, impossible. Otherwise, iterate. If `currentTank < 0`, reset start to `i + 1` and `currentTank = 0`.
    **提示**：若總油量 < 總消耗，不可能達成。否則進行迭代。若 `currentTank < 0`，重設起點為 `i + 1` 並將 `currentTank` 歸零。
*   **Focus**: Proving that skipping failed stations is safe.
    **重點**：證明跳過失敗的站點是安全的。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review during Interview（面試自我審查）
- [ ] **Sorting**: Did I sort the input? If not, is it implicitly sorted or using a Heap?
    **排序**：我有排序輸入嗎？如果沒有，它是隱式排序的還是使用了堆積？
- [ ] **Criteria**: Did I sort by Start Time or End Time? (Intervals usually End Time).
    **標準**：我是依開始時間還是結束時間排序？（區間問題通常是結束時間）。
- [ ] **Future Proof**: Does my choice restrict future valid options unnecessarily?
    **未來驗證**：我的選擇是否不必要地限制了未來的有效選項？
- [ ] **Complexity**: Is it $O(N \log N)$? If it's $O(N^2)$, can I optimize the search?
    **複雜度**：是 $O(N \log N)$ 嗎？如果是 $O(N^2)$，我能優化搜尋嗎？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Hill Climber"（登山者）
Greedy is like climbing a mountain in thick fog. You only look at the ground immediately around you and take the steepest step up.
貪婪法就像在濃霧中登山。你只看周圍的地面，並踏出最陡峭的一步向上。
*   **Risk**: You might end up on a small hill (local optimum), not the summit (global optimum).
    **風險**：你可能最終停在一個小山丘（局部最佳），而不是山頂（全域最佳）。
*   **Success**: For "Convex" problems (like simple money change), the hill leads directly to the summit.
    **成功**：對於「凸性」問題（如簡單找零），山丘直接通往山頂。

### The "Short-Sighted Manager"（短視的經理）
A manager who always approves the project that finishes quickest *right now*, ignoring long-term strategy.
一位總是批准*現在*能最快完成的專案，而忽略長期策略的經理。
*   Works well for clearing a backlog of small tasks (Interval Scheduling).
    對於清理積壓的小任務（區間排程）很有效。
*   Fails if a long project now enables huge profits later.
    若現在的一個長專案能帶來未來的巨額利潤，則會失敗。