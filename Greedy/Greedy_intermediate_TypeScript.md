Here is the comprehensive guide on **Greedy Algorithms**, tailored for a Senior Software Engineer, following your specified structure and bilingual format.

---

# Greedy Algorithms: Practical Interview Guide (Intermediate)
# 貪婪演算法：面試實戰指南（中級）

## 1. Learning Objectives（學習目標）

1.  **Identify Greedy Applicability**: Learn to distinguish when a problem can be solved by a local optimal choice versus when Dynamic Programming is required.
    **辨識貪婪適用性**：學會區分何時可以透過局部最佳解解決問題，以及何時需要動態規劃。
2.  **Master Sorting Strategies**: Understand how different sorting criteria (e.g., by start time vs. end time) drastically affect the correctness of a Greedy approach.
    **掌握排序策略**：理解不同的排序標準（例如：按開始時間 vs. 按結束時間）如何劇烈地影響貪婪策略的正確性。
3.  **Proof of Correctness Intuition**: Develop the ability to articulate *why* a greedy choice works using informal "Exchange Arguments" during an interview.
    **正確性證明的直覺**：培養在面試中運用非正式的「交換論證」來闡述*為何*貪婪選擇有效的溝通能力。
4.  **Optimize Complexity**: Move from $O(N^2)$ DP solutions to $O(N \log N)$ or $O(N)$ Greedy solutions.
    **優化複雜度**：從 $O(N^2)$ 的動態規劃解法進階至 $O(N \log N)$ 或 $O(N)$ 的貪婪解法。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
Greedy algorithms build up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法透過逐步構建解法，總是選擇當下能提供最大利益的下一步。

It relies on the **Greedy Choice Property**: A global optimal solution can be arrived at by making a locally optimal (greedy) choice.
它依賴於**貪婪選擇屬性**：透過做出局部最佳（貪婪）的選擇，最終可以達成全域最佳解。

### Intuition（直覺）
Think of it as "living in the moment." You make the best decision now, assuming it won't negatively impact your ability to reach the optimal goal later.
可以將其視為「活在當下」。你做出現在最好的決定，並假設這不會對稍後達成最佳目標的能力產生負面影響。

### Complexity（複雜度）
- **Time**: Usually $O(N \log N)$ due to sorting, or $O(N)$ if using a Heap/Priority Queue efficiently or if the input is pre-sorted.
  **時間**：通常為 $O(N \log N)$，因為需要排序；若有效利用堆積/優先佇列或輸入已排序，則為 $O(N)$。
- **Space**: Usually $O(1)$ or $O(N)$ depending on whether we need auxiliary structures for sorting.
  **空間**：通常為 $O(1)$ 或 $O(N)$，取決於排序是否需要輔助結構。

### When to Use / Not Use（適用與不適用場景）
- **Use when**: The problem has "Optimal Substructure" and the "Greedy Choice Property" holds (e.g., Interval Scheduling, Minimum Spanning Trees).
  **適用時機**：問題具備「最佳子結構」且「貪婪選擇屬性」成立時（例如：區間調度、最小生成樹）。
- **Do NOT use when**: A local optimal choice prevents a future global optimal (e.g., 0/1 Knapsack Problem, Coin Change with arbitrary denominations).
  **不適用時機**：局部最佳選擇會阻礙未來的全域最佳解時（例如：0/1 背包問題、任意面額的找零問題）。

---

## 3. Typical Patterns（典型題型 / 模式）

### 1. Interval Scheduling / Covering（區間調度 / 覆蓋）
**Scenario**: Given a set of intervals, find the max number of non-overlapping intervals or min intervals to cover a range.
**場景**：給定一組區間，找出最大不重疊區間數量，或覆蓋範圍所需的最小區間數。
**Key**: Sort by **end time** (usually) or start time.
**關鍵**：按**結束時間**（通常）或開始時間排序。

### 2. Merge Intervals（合併區間）
**Scenario**: Merge all overlapping intervals.
**場景**：合併所有重疊的區間。
**Key**: Sort by **start time**.
**關鍵**：按**開始時間**排序。

### 3. Allocation / Fitting（分配 / 適配）
**Scenario**: Assigning resources (cookies, tasks) to demands (children, workers) to maximize satisfaction.
**場景**：將資源（餅乾、任務）分配給需求（孩童、工人）以最大化滿意度。
**Key**: Sort both resources and demands, then use Two Pointers.
**關鍵**：將資源與需求雙雙排序，接著使用雙指針。

### 4. String / Array Manipulation（字串 / 陣列操作）
**Scenario**: Reorganize a string to meet criteria (e.g., no adjacent duplicates) or partition an array.
**場景**：重組字串以符合標準（例如：無相鄰重複）或分割陣列。
**Key**: Count frequencies (Hash Map) + Max Heap.
**關鍵**：計算頻率（雜湊表）+ 最大堆積。

---

## 4. Example Walkthrough（範例講解）

### Problem: Non-overlapping Intervals (LeetCode 435)
### 問題：無重疊區間

**Problem Statement**:
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，請回傳為了讓其餘區間不重疊，所需移除的最小區間數量。

### Approach 1: Brute Force / DP (Mental Check)
### 思路 1：暴力解 / 動態規劃（心智檢核）

We could sort by start time and define $DP[i]$ as the max non-overlapping intervals ending at index $i$.
我們可以按開始時間排序，並定義 $DP[i]$ 為以索引 $i$ 結尾的最大不重疊區間數。
This is equivalent to the Longest Increasing Subsequence (LIS) problem, taking $O(N^2)$.
這等同於最長遞增子序列（LIS）問題，耗時 $O(N^2)$。
**Verdict**: Too slow for $N=10^5$.
**結論**：對於 $N=10^5$ 來說太慢。

### Approach 2: Greedy (Optimization)
### 思路 2：貪婪演算法（優化）

**Intuition**: To keep as many intervals as possible (minimize removal), we should always pick the interval that ends the **earliest**.
**直覺**：為了保留盡可能多的區間（最小化移除），我們應該總是選擇**最早結束**的區間。
Why? Because finishing early leaves more room for subsequent intervals.
為什麼？因為越早結束，留給後續區間的空間就越大。

**Algorithm**:
1. Sort intervals by **end time**.
2. Pick the first interval.
3. Iterate through the rest: if an interval overlaps with the current one, remove it (increment count); otherwise, keep it and update the "current end".

**演算法**：
1. 按**結束時間**對區間排序。
2. 選取第一個區間。
3. 遍歷其餘區間：若某區間與當前區間重疊，則移除它（計數加一）；否則，保留它並更新「當前結束時間」。

### TypeScript Solution（TypeScript 參考解）

```typescript
/**
 * Calculates the minimum number of intervals to remove to ensure non-overlapping.
 * 計算為確保不重疊所需移除的最小區間數。
 *
 * Time Complexity: O(N log N) - dominated by sorting.
 * 時間複雜度：O(N log N) - 主要取決於排序。
 * Space Complexity: O(1) or O(log N) - depending on sorting implementation.
 * 空間複雜度：O(1) 或 O(log N) - 取決於排序實作。
 */
function eraseOverlapIntervals(intervals: number[][]): number {
    if (intervals.length === 0) return 0;

    // Sort by end time ascending.
    // 按結束時間升序排列。
    // If end times are equal, sorting by start time doesn't strictly matter for correctness here,
    // but consistent sorting is good practice.
    // 若結束時間相同，按開始時間排序對此處正確性無嚴格影響，但保持一致的排序是好習慣。
    intervals.sort((a, b) => a[1] - b[1]);

    let removedCount = 0;
    
    // Initialize the end of the last added interval.
    // 初始化最後一個加入區間的結束時間。
    let prevEnd = intervals[0][1];

    // Start iterating from the second interval.
    // 從第二個區間開始遍歷。
    for (let i = 1; i < intervals.length; i++) {
        const [currentStart, currentEnd] = intervals[i];

        if (currentStart < prevEnd) {
            // Overlap detected.
            // 偵測到重疊。
            // We greedily "remove" the current interval because the previous one
            // ends earlier (due to sorting), leaving more space for future intervals.
            // 我們貪婪地「移除」當前區間，因為前一個區間結束得更早（基於排序），
            // 為未來的區間留出了更多空間。
            removedCount++;
        } else {
            // No overlap. Update the end time to the current interval's end.
            // 無重疊。將結束時間更新為當前區間的結束時間。
            prevEnd = currentEnd;
        }
    }

    return removedCount;
}
```

### Common Mistake: Sorting by Start Time
### 常見錯誤：按開始時間排序

If you sort by start time, a very long interval might start early but cover everything (e.g., `[1, 100]`, `[2, 3]`, `[4, 5]`).
如果你按開始時間排序，一個非常長的區間可能很早就開始，但覆蓋了所有範圍（例如：`[1, 100]`, `[2, 3]`, `[4, 5]`）。
If you pick `[1, 100]` just because it starts first, you eliminate all others. This is not optimal.
如果你僅因為 `[1, 100]` 最早開始而選擇它，你會排除掉所有其他區間。這不是最佳解。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision Making**<br>**決策方式** | Makes the best local choice at each step and never looks back.<br>在每一步做出最佳局部選擇，且絕不回頭。 | Considers all possible choices (or previous states) to find the global optimum.<br>考慮所有可能的選擇（或先前狀態）以找出全域最佳解。 |
| **Backtracking**<br>**回溯** | No. Once a choice is made, it is final.<br>無。一旦做出選擇，即為定局。 | Implicitly yes (via recursion) or explicitly via table lookup.<br>隱含地有（透過遞迴）或顯式地透過查表。 |
| **Correctness**<br>**正確性** | Harder to prove. Requires specific mathematical properties.<br>較難證明。需要特定的數學屬性。 | Generally guaranteed if the state transition is correct.<br>若狀態轉移正確，通常能保證正確性。 |
| **Example**<br>**範例** | Fractional Knapsack (take items by value/weight ratio).<br>分數背包問題（按價值/重量比選取物品）。 | 0/1 Knapsack (must take whole item or leave it).<br>0/1 背包問題（必須選取整個物品或放棄）。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. The "Try and Fail" Narrative（「嘗試與修正」的敘述框架）
Don't jump straight to Greedy. Start by saying:
不要直接跳到貪婪解法。開頭可以這樣說：
> "Initially, this looks like a search problem where we might need DP to explore all combinations. However, let's see if a local optimal choice leads to a global solution."
> 「起初，這看起來像是一個搜尋問題，我們可能需要 DP 來探索所有組合。不過，讓我們看看局部最佳選擇是否能導向全域解。」

### 2. Justifying Greedy (The Exchange Argument)（證成貪婪：交換論證）
If the interviewer asks "Are you sure?", use this logic:
如果面試官問「你確定嗎？」，使用此邏輯：
> "If we have an optimal solution that *doesn't* use our greedy choice, can we swap one of its elements with our greedy choice without making the solution worse? If yes, then the greedy choice is safe."
> 「如果我們有一個*不*使用貪婪選擇的最佳解，我們能否將其中的一個元素與我們的貪婪選擇交換，而不讓解法變差？如果可以，那麼貪婪選擇就是安全的。」

### 3. Whiteboard Strategy（白板策略）
- **Draw a timeline**: For interval problems, visualize the overlap.
  **畫出時間軸**：對於區間問題，將重疊部分視覺化。
- **Sort Explicitly**: Write `intervals.sort(...)` clearly. The sorting criteria is often the most important line of code.
  **明確排序**：清楚寫下 `intervals.sort(...)`。排序標準往往是最重要的一行程式碼。

---

## 7. Practice Problems（練習題）

### Easy: Assign Cookies (LeetCode 455)
**Problem**: Distribute cookies of size `s[j]` to children with greed factor `g[i]`.
**問題**：將大小為 `s[j]` 的餅乾分發給貪婪指數為 `g[i]` 的孩童。
**Hint**: Sort both arrays. Give the smallest sufficient cookie to the least greedy child.
**提示**：將兩個陣列排序。將最小且足夠的餅乾分給最不貪婪的孩童。

### Medium: Jump Game II (LeetCode 45)
**Problem**: Min number of jumps to reach the last index.
**問題**：到達最後一個索引所需的最小跳躍次數。
**Hint**: Implicit BFS / Greedy. Maintain `currentEnd` of the current jump and `farthest` reachable. When `i` reaches `currentEnd`, increment jumps and update `currentEnd = farthest`.
**提示**：隱式 BFS / 貪婪。維護當前跳躍的 `currentEnd` 和可到達的 `farthest`。當 `i` 到達 `currentEnd` 時，增加跳躍次數並更新 `currentEnd = farthest`。

### Hard: Candy (LeetCode 135)
**Problem**: Distribute candies based on ratings. Neighbors with higher ratings get more candies.
**問題**：根據評分分發糖果。評分較高的鄰居應獲得更多糖果。
**Hint**: Two-pass Greedy. Left-to-right to satisfy left neighbors, then right-to-left to satisfy right neighbors. Take the `max` at each index.
**提示**：兩次遍歷的貪婪策略。從左到右滿足左鄰居，再從右到左滿足右鄰居。在每個索引處取 `max`。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review during Interview（面試自我審查）
- [ ] **Sorting**: Did I sort the input? Is the sorting order (asc/desc, start/end) justified?
  **排序**：我是否對輸入進行了排序？排序順序（升/降，開始/結束）是否合理？
- [ ] **Edge Cases**: Empty array? One element? Intervals touching (e.g., `[1,2]` and `[2,3]`)?
  **邊界條件**：空陣列？單一元素？區間相接（如 `[1,2]` 和 `[2,3]`）？
- [ ] **Complexity**: Is it $O(N \log N)$? Can it be $O(N)$ (e.g., bucket sort / counting)?
  **複雜度**：是 $O(N \log N)$ 嗎？能優化成 $O(N)$ 嗎（如桶排序/計數）？

### Debugging Logic（除錯邏輯）
- [ ] If Greedy fails on test cases, try to find a counter-example where "sacrificing short-term gain yields long-term profit." If such a case exists, switch to DP.
  **若貪婪法測試失敗**，試著找出一個「犧牲短期利益能換取長期獲利」的反例。若存在此類情況，請切換至 DP。

---

## 9. Memory Anchors（記憶錨點）

### The "Cashier" Analogy（「收銀員」類比）
When giving change (in most currencies), you always give the largest bill possible first.
找零時（在大多數貨幣體系中），你總是先給出面額最大的鈔票。
*   $67 \to 50 + 10 + 5 + 1 + 1$.
*   You don't think "Maybe if I save the 50, I can use three 20s later."
*   你不會想「也許我省下這張 50，稍後可以用三張 20。」
*   **Anchor**: Greedy is about grabbing the biggest value *now*.
*   **錨點**：貪婪就是*現在*抓取最大價值。

### The "Overlapping Meetings" Image（「重疊會議」圖像）
Imagine a calendar. To attend the most meetings, you pick the one that **ends soonest**.
想像一個行事曆。為了參加最多的會議，你會選擇**最快結束**的那一個。
*   Why? Because it frees you up earlier to attend the next one.
*   為什麼？因為它讓你更早有空去參加下一場。
*   **Anchor**: Sort by **End Time** for maximum capacity.
*   **錨點**：為了最大容量，按**結束時間**排序。