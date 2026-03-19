Here is the complete interview preparation material for **Greedy Algorithms**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **Greedy Algorithms（貪婪演算法）** 面試準備教材。

---

# Greedy Algorithms: From Intuition to Rigorous Proof
# 貪婪演算法：從直覺到嚴謹證明

## 1. Learning Goals (學習目標)

*   **Identify Greedy Suitability:** Recognize problems satisfying the "Greedy Choice Property" and "Optimal Substructure."
    **識別貪婪適用性：** 辨識滿足「貪婪選擇性質」與「最佳子結構」的問題。
*   **Distinguish from DP:** Understand the boundary between Greedy and Dynamic Programming to avoid over-engineering.
    **區分貪婪與動態規劃：** 理解貪婪與動態規劃的界線，避免過度設計。
*   **Master Interval Patterns:** Gain proficiency in classic interval scheduling and resource allocation problems.
    **掌握區間模式：** 熟練經典的區間排程與資源分配問題。
*   **Justify Correctness:** Learn to articulate *why* a greedy approach works using "Exchange Arguments" or "Proof by Contradiction."
    **驗證正確性：** 學習使用「交換論證」或「反證法」來闡述 *為何* 貪婪解法有效。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Greedy algorithms build up a solution piece by piece, always choosing the next piece that offers the most immediate and obvious benefit.
貪婪演算法透過逐步建構解法，總是選擇在當下能提供最立即且顯著效益的下一步。

It assumes that a local optimum will lead to a global optimum.
它假設局部最佳解將導向全域最佳解。

### Intuition (直覺)
Think of it as "living in the moment." You make the best decision based on current information without worrying about the distant future or backtracking.
將其視為「活在當下」。你根據現有資訊做出最佳決策，而不擔心遙遠的未來或回頭修正。

### Complexity (複雜度)
*   **Time:** Often $O(N \log N)$ due to sorting, or $O(N)$ if using a heap/priority queue effectively.
    **時間：** 通常為 $O(N \log N)$，因為需要排序，若有效使用堆積/優先佇列則可能為 $O(N)$。
*   **Space:** Usually $O(1)$ or $O(N)$ depending on whether output storage is counted.
    **空間：** 通常為 $O(1)$ 或 $O(N)$，取決於是否計算輸出儲存空間。

### When to Use (適用場景)
*   **Optimization Problems:** Finding minimum/maximum (e.g., min coins, max events).
    **最佳化問題：** 尋找極小值/極大值（例如：最少硬幣、最多活動）。
*   **Greedy Choice Property:** A global optimal solution can be arrived at by selecting a local optimal.
    **貪婪選擇性質：** 全域最佳解可以透過選取局部最佳解來達成。

### When NOT to Use (不適用場景)
*   **Constraints affect future validity:** If taking the "biggest" item now prevents you from fitting two "medium" items later that would sum to more.
    **限制影響未來有效性：** 如果現在拿了「最大」的項目，導致稍後無法放入兩個總和更大的「中等」項目。
*   **Example:** Coin change with denominations $\{1, 3, 4\}$ to make 6. Greedy takes 4, then 1, 1 (3 coins). Optimal is 3, 3 (2 coins).
    **範例：** 使用面額 $\{1, 3, 4\}$ 的硬幣湊出 6。貪婪法會拿 4，然後 1, 1（共 3 枚）。最佳解是 3, 3（共 2 枚）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting + Linear Scan (排序 + 線性掃描)
Most greedy problems require the input to be sorted (by start time, end time, size, etc.) to reveal the greedy choice.
大多數貪婪問題需要對輸入進行排序（按開始時間、結束時間、大小等），以顯現貪婪選擇。
*   *Keywords:* Intervals, Meeting Rooms, Merge.

### B. Heap / Priority Queue (堆積 / 優先佇列)
When you need to dynamically access the "best" current element while the state changes.
當你需要在狀態改變時動態存取當前「最佳」元素時。
*   *Keywords:* K-th elements, Huffman Coding, Dijkstra.

### C. Two Pointers (Greedy Variation) (雙指針貪婪變體)
Using pointers to greedily match elements from two ends or two arrays.
使用指針從兩端或兩個陣列中貪婪地匹配元素。
*   *Keywords:* Container with Most Water, Trapping Rain Water (can be seen as greedy).

### D. String Manipulation (字串操作)
Constructing the lexicographically smallest/largest result.
建構字典序最小/最大的結果。
*   *Keywords:* Remove K Digits, Smallest Subsequence.

---

## 4. Example Walkthrough (範例講解)

### Problem: Non-overlapping Intervals (無重疊區間)
**Difficulty:** Medium | **Pattern:** Interval Scheduling

#### Problem Statement (問題重述)
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳為了讓剩餘區間互不重疊，所需移除的最小區間數量。

#### Thought Process (思路)

**1. Brute Force (暴力法):**
Try all subsets of intervals, check if they overlap, and find the largest valid subset.
嘗試所有區間的子集，檢查是否重疊，並找出最大的有效子集。
*   *Complexity:* $O(2^N)$. Too slow. (太慢)

**2. Dynamic Programming (動態規劃):**
Sort by start time. $DP[i]$ = max non-overlapping intervals ending at index $i$.
按開始時間排序。$DP[i]$ = 以索引 $i$ 結尾的最大無重疊區間數。
*   *Complexity:* $O(N^2)$. Better, but not optimal. (較好，但非最佳)

**3. Greedy (Optimal) (貪婪 - 最佳解):**
*   *Intuition:* To fit as many intervals as possible, we should finish the current interval as early as possible to leave space for the next ones.
    *直覺：* 為了放入盡可能多的區間，我們應該盡早結束當前區間，以便為下一個區間留出空間。
*   *Strategy:* Sort by **end time**. Always pick the interval that ends earliest and doesn't overlap with the previous one.
    *策略：* 按 **結束時間** 排序。總是選擇結束最早且與前一個不重疊的區間。

#### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    int eraseOverlapIntervals(vector<vector<int>>& intervals) {
        // Edge case: empty input
        // 邊界條件：空輸入
        if (intervals.empty()) return 0;

        // Sort intervals by their end time (ascending)
        // 依據區間的結束時間進行升冪排序
        sort(intervals.begin(), intervals.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[1] < b[1];
        });

        // Initialize count of non-overlapping intervals
        // 初始化無重疊區間的計數
        int count = 1; 
        
        // Track the end time of the last added interval
        // 追蹤最後加入區間的結束時間
        int end = intervals[0][1];

        // Iterate starting from the second interval
        // 從第二個區間開始迭代
        for (size_t i = 1; i < intervals.size(); ++i) {
            // If the current interval starts after or exactly when the previous one ends
            // 如果當前區間的開始時間在前一個區間結束之後（或剛好同時）
            if (intervals[i][0] >= end) {
                count++;        // Include this interval (納入此區間)
                end = intervals[i][1]; // Update the end time (更新結束時間)
            }
            // Else: Implicitly remove this interval (greedy choice)
            // 否則：隱含地移除此區間（貪婪選擇）
        }

        // Result is total intervals minus the max non-overlapping count
        // 結果為總區間數減去最大無重疊區間數
        return intervals.size() - count;
    }
};
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N \log N)$ dominated by sorting. The iteration is $O(N)$.
    **時間：** $O(N \log N)$，由排序主導。迭代過程為 $O(N)$。
*   **Space:** $O(\log N)$ or $O(N)$ depending on the implementation of `std::sort`.
    **空間：** $O(\log N)$ 或 $O(N)$，取決於 `std::sort` 的實作。

#### Why Sorting by Start Time is Wrong (為何按開始時間排序是錯的)
If you sort by start time, you might pick a very long interval that starts early but blocks everyone else (e.g., `[1, 100]`, `[2, 3]`, `[4, 5]`).
如果按開始時間排序，你可能會選到一個開始得很早但非常長的區間，擋住了其他所有人（例如 `[1, 100]`，而錯過 `[2, 3]` 和 `[4, 5]`）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Greedy (貪婪) | Dynamic Programming (動態規劃) |
| :--- | :--- | :--- |
| **Decision Type** | Makes the best local choice immediately. <br> 立即做出最佳局部選擇。 | Considers all choices and sub-problems. <br> 考慮所有選擇與子問題。 |
| **Backtracking** | No. Once a choice is made, it's final. <br> 否。一旦做出選擇，即為定局。 | Yes (implicitly via recursion/table lookups). <br> 是（透過遞迴/查表隱含地進行）。 |
| **Proof** | Harder. Requires mathematical proof (Exchange Argument). <br> 較難。需要數學證明（交換論證）。 | Easier. Relies on state transition logic. <br> 較易。依賴狀態轉移邏輯。 |
| **Failure Mode** | Fails if local optimum $\neq$ global optimum. <br> 若局部最佳 $\neq$ 全域最佳則失敗。 | Fails on Time Limit Exceeded (if not optimized). <br> 若未優化則會超時（TLE）。 |

**Senior Tip:**
Do not default to Greedy just because it looks like an optimization problem. If constraints involve "summing up to a target" (Knapsack) or "path dependencies," it's likely DP.
**資深提示：** 不要因為看起來像最佳化問題就預設使用貪婪法。如果限制條件涉及「總和達到目標」（背包問題）或「路徑依賴」，則很可能是動態規劃。

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Hypothesize:** "This looks like an optimization problem. I suspect a greedy approach might work because [reason]."
    **假設：** 「這看起來是個最佳化問題。我猜測貪婪法可能行得通，因為 [理由]。」
2.  **Define the Greedy Rule:** "My proposed greedy choice is to always pick [X] based on sorting by [Y]."
    **定義貪婪規則：** 「我提出的貪婪選擇是根據 [Y] 排序後總是選取 [X]。」
3.  **Challenge Yourself:** "Let me quickly check if a counter-example exists. What if we have [Edge Case]?"
    **自我挑戰：** 「讓我快速檢查是否存在反例。如果我們有 [邊界情況] 會怎樣？」
4.  **Fallback:** "If greedy fails, I will pivot to Dynamic Programming."
    **備案：** 「如果貪婪法失敗，我會轉向動態規劃。」

### Whiteboard Strategy (白板策略)
*   **Draw the timeline:** For interval problems, draw lines on a number axis. Visually showing "overlaps" helps justify sorting by end-time.
    **畫出時間軸：** 對於區間問題，在數軸上畫線。視覺化「重疊」有助於解釋為何按結束時間排序。
*   **Variable Naming:** Use `currEnd`, `nextStart`, `globalMax` clearly.
    **變數命名：** 清晰地使用 `currEnd`、`nextStart`、`globalMax`。

### Common Follow-ups (常見追問)
*   "Can you prove this works?" (Use logic: "If we chose a different interval that ended later, we would only have *less* room for future intervals, not more.")
    「你能證明這有效嗎？」（使用邏輯：「如果我們選了一個較晚結束的區間，我們留給未來的空間只會*更少*，不會更多。」）
*   "What if the input is a stream?" (Suggest keeping a sorted structure or Heap).
    「如果輸入是串流怎麼辦？」（建議維護排序結構或堆積）。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Warm-up)
**Problem:** Assign Cookies (LeetCode 455)
**Hint:** Sort both children (greed factor) and cookies (size). Match smallest appetite child with smallest valid cookie.
**提示：** 對孩童（貪婪指數）和餅乾（大小）進行排序。將胃口最小的孩童與最小的有效餅乾配對。

### Level 2: Intermediate (Core)
**Problem:** Gas Station (LeetCode 134)
**Hint:** If total gas < total cost, return -1. Else, iterate. If `current_tank < 0`, reset start point to `i + 1`.
**提示：** 若總油量 < 總消耗，回傳 -1。否則進行迭代。若 `current_tank < 0`，將起點重置為 `i + 1`。

### Level 3: Advanced (Differentiation)
**Problem:** Candy (LeetCode 135)
**Hint:** Do two passes. Left-to-right: ensure higher rating gets more candy than left neighbor. Right-to-left: ensure higher rating gets more than right neighbor. Take `max` of both.
**提示：** 進行兩次掃描。從左至右：確保評分較高者比左鄰居拿更多糖果。從右至左：確保評分較高者比右鄰居拿更多。取兩者的 `max`。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
- [ ] **Sorting:** Did I sort the input? Is the sorting criteria (key) correct?
    **排序：** 我是否對輸入進行了排序？排序標準（鍵值）是否正確？
- [ ] **Local Decision:** Does my choice strictly leave the problem in a solvable state?
    **局部決策：** 我的選擇是否嚴格保證問題仍處於可解狀態？
- [ ] **Complexity:** Is sorting ($N \log N$) acceptable for the constraints ($N \le 10^5$)?
    **複雜度：** 排序 ($N \log N$) 對於限制條件 ($N \le 10^5$) 是否可接受？
- [ ] **Edge Cases:** What if all intervals overlap? What if the array is empty?
    **邊界條件：** 如果所有區間都重疊怎麼辦？如果陣列為空怎麼辦？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Cashier" Analogy (「收銀員」類比)
When giving change, a cashier doesn't use DP. They grab the largest bill possible that fits the remaining amount. This is Greedy.
找零時，收銀員不會用動態規劃。他們會拿取能放入剩餘金額中的最大面額鈔票。這就是貪婪。

### The "Earliest Deadline First" (「最早截止期限優先」)
Imagine you have 10 homework assignments. To finish the maximum number of them, you should always work on the one due *soonest*. Working on a project due next month while ignoring the one due tomorrow is anti-greedy (and foolish).
想像你有 10 份作業。為了完成最多份，你應該總是先做*最快到期*的那份。忽略明天到期的作業而先做下個月到期的專案，是反貪婪（且愚蠢）的。

### Visual Anchor: The "Bump" (視覺錨點：「凸起」)
Think of Greedy as climbing a hill in fog. You just step where the slope is steepest upwards. You might reach the peak (Global Optimum), or you might get stuck on a small hill (Local Optimum). The "Greedy Choice Property" guarantees there is only one peak.
將貪婪想像成在霧中爬山。你只往坡度最陡向上的地方走。你可能會到達頂峰（全域最佳），也可能被困在小山丘（局部最佳）。「貪婪選擇性質」保證了只有一座頂峰。