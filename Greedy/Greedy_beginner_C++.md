Here is the complete interview preparation material for **Greedy Algorithms**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level (focusing on foundational rigor and standard patterns), with **C++** implementation.

這是一份針對 **貪婪演算法（Greedy Algorithms）** 的完整面試準備教材，專為資深軟體工程師設計，深度調整為 **初學者（Beginner）**（著重於基礎嚴謹性與標準模式），並使用 **C++** 實作。

---

# Greedy Algorithms: Foundational Rigor & Interview Patterns
# 貪婪演算法：基礎嚴謹性與面試模式

## 1. Learning Objectives（學習目標）

1.  **Understand the Core Philosophy**: Learn how to identify problems where making the locally optimal choice leads to the global optimum.
    **理解核心哲學**：學習如何識別「做出局部最佳選擇即可導致全域最佳解」的問題。

2.  **Master the "Sort & Iterate" Pattern**: 90% of basic greedy problems involve sorting followed by a linear scan.
    **掌握「排序與迭代」模式**：90% 的基礎貪婪問題涉及排序後進行線性掃描。

3.  **Distinguish Greedy from Dynamic Programming**: Understand why Greedy is faster but less powerful than DP, and when to use which.
    **區分貪婪與動態規劃**：理解為何貪婪比 DP 快但不夠強大，以及何時該使用哪一種。

4.  **Implement with Modern C++**: Use STL algorithms (`std::sort`, `std::priority_queue`) efficiently.
    **使用現代 C++ 實作**：高效使用 STL 演算法（如 `std::sort`、`std::priority_queue`）。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）

Greedy algorithms build up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法逐步建構解法，總是選擇當下能提供最大即時利益的下一個片段。

It relies on the **Greedy Choice Property**: A global optimum can be arrived at by selecting a local optimum.
它依賴於 **貪婪選擇屬性**：透過選擇局部最佳解，可以達成全域最佳解。

It also requires **Optimal Substructure**: An optimal solution to the problem contains an optimal solution to subproblems.
它也需要 **最佳子結構**：問題的最佳解包含其子問題的最佳解。

### Complexity（複雜度）

-   **Time**: Usually dominated by sorting, $O(N \log N)$. If the input is already sorted or a heap is used, it might be $O(N)$ or $O(N \log K)$.
    **時間**：通常由排序主導，為 $O(N \log N)$。若輸入已排序或使用堆積（Heap），可能是 $O(N)$ 或 $O(N \log K)$。
-   **Space**: Usually $O(1)$ or $O(N)$ depending on whether we need to store the output or auxiliary structures.
    **空間**：通常為 $O(1)$ 或 $O(N)$，取決於是否需要儲存輸出或輔助結構。

### When to Use vs. Not to Use（適用與不適用場景）

| Scenario | Description (敘述) |
| :--- | :--- |
| **Use Greedy (適用)** | Problems asking for min/max where previous choices don't restrict future valid choices in a complex way (e.g., Interval Scheduling). <br> 要求極大/極小值的問題，且先前的選擇不會以複雜的方式限制未來的有效選擇（例如：區間排程）。 |
| **Do NOT Use (不適用)** | When local greediness leads to a dead end or suboptimal total (e.g., 0/1 Knapsack, Coin Change with non-standard denominations). <br> 當局部貪婪會導致死路或非最佳總和時（例如：0/1 背包問題、非標準面額的找零問題）。 |

---

## 3. Typical Patterns（典型題型 / 模式）

At the beginner/intermediate boundary, most Greedy problems fall into these buckets:
在初級/中級的邊界，大多數貪婪問題屬於以下類別：

1.  **Interval Scheduling (Sorting by End Time)**
    **區間排程（依結束時間排序）**
    -   Goal: Fit as many activities as possible.
    -   目標：盡可能安排最多的活動。

2.  **Resource Allocation (Sorting by Size/Greed Factor)**
    **資源分配（依大小/貪婪因子排序）**
    -   Goal: Satisfy children with cookies, or assign tasks to workers.
    -   目標：用餅乾滿足孩子，或將任務分配給工人。

3.  **Partitioning / Merge Intervals (Sorting by Start Time)**
    **分割 / 合併區間（依開始時間排序）**
    -   Goal: Merge overlapping intervals or count gaps.
    -   目標：合併重疊區間或計算間隙。

---

## 4. Example Walkthrough（範例講解）

### Problem: Non-overlapping Intervals (LeetCode 435)
### 問題：無重疊區間

**Problem Statement:**
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳為了讓其餘區間不重疊，所需移除的最小區間數量。

### Approach: Thought Process（思路）

1.  **Brute Force (暴力法)**:
    Try all subsets of intervals, check if they overlap, and find the largest valid subset. Complexity is $O(2^N)$.
    嘗試所有區間的子集，檢查是否重疊，並找出最大的有效子集。複雜度為 $O(2^N)$。

2.  **Greedy Intuition (貪婪直覺)**:
    To keep as many intervals as possible (minimize removal), we should finish the current interval as early as possible.
    為了保留盡可能多的區間（最小化移除），我們應該盡早結束當前的區間。
    Why? Because finishing early leaves more "time" for subsequent intervals.
    為什麼？因為越早結束，留給後續區間的「時間」就越多。

3.  **Optimization (優化)**:
    Sort by **end time**. Iterate through. If an interval starts after the previous one ends, keep it. Otherwise, remove it (conceptually).
    依 **結束時間** 排序。遍歷陣列。如果一個區間的開始時間在由前一個區間結束之後，則保留它。否則，（概念上）移除它。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    int eraseOverlapIntervals(vector<vector<int>>& intervals) {
        // Edge case: empty input
        // 邊界情況：空輸入
        if (intervals.empty()) return 0;

        // Sort intervals by their end time (ascending).
        // 依據區間的結束時間進行排序（升冪）。
        // Lambda function used as a custom comparator.
        // 使用 Lambda 函式作為自定義比較器。
        sort(intervals.begin(), intervals.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[1] < b[1];
        });

        int count = 0; // Count of intervals to remove. 欲移除的區間計數。
        
        // Initialize the end time of the last added interval.
        // 初始化最後一個加入區間的結束時間。
        // We pick the first one (after sorting) because it ends earliest.
        // 我們選擇排序後的第一個，因為它最早結束。
        int prevEnd = intervals[0][1];

        // Iterate from the second interval.
        // 從第二個區間開始遍歷。
        for (size_t i = 1; i < intervals.size(); ++i) {
            int currentStart = intervals[i][0];
            int currentEnd = intervals[i][1];

            if (currentStart < prevEnd) {
                // Overlap detected. We must remove one.
                // 偵測到重疊。我們必須移除一個。
                // Since we sorted by end time, the current one ends later (or equal) than prevEnd.
                // 因為我們依結束時間排序，當前區間的結束時間晚於（或等於）prevEnd。
                // To be greedy, we keep the one that ends earlier (prevEnd) to save space.
                // 為了貪婪，我們保留結束較早的那個（prevEnd）以節省空間。
                // So we "remove" the current one.
                // 所以我們「移除」當前這個。
                count++;
            } else {
                // No overlap. Update the end time to the current interval's end.
                // 無重疊。更新結束時間為當前區間的結束時間。
                prevEnd = currentEnd;
            }
        }

        return count;
    }
};
```

### Complexity Analysis（複雜度分析）

-   **Time**: $O(N \log N)$ due to `std::sort`. The loop is $O(N)$.
    **時間**：由於 `std::sort`，為 $O(N \log N)$。迴圈為 $O(N)$。
-   **Space**: $O(\log N)$ or $O(N)$ depending on the implementation of sort (stack space).
    **空間**：$O(\log N)$ 或 $O(N)$，取決於排序的實作（堆疊空間）。

### Common Mistake（錯誤示範）

**Sorting by Start Time**:
**依開始時間排序**：
If you sort by start time, you might pick a very long interval that starts early but blocks everyone else.
如果你依開始時間排序，你可能會選到一個很早就開始但非常長的區間，擋住了其他所有人。
*Example*: `[1, 100], [2, 3], [4, 5]`.
If you pick `[1, 100]`, you lose `[2, 3]` and `[4, 5]`. Correct greedy choice is to pick intervals ending early.
若選了 `[1, 100]`，你會失去 `[2, 3]` 和 `[4, 5]`。正確的貪婪選擇是選結束得早的區間。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision**<br>**決策** | Makes the best choice *now* and never looks back.<br>做出*當下*最佳選擇，絕不回頭。 | Considers all choices and their consequences (often via recursion/table).<br>考慮所有選擇及其後果（通常透過遞迴/表格）。 |
| **Correctness**<br>**正確性** | Harder to prove. Requires "Exchange Argument".<br>較難證明。需要「交換論證」。 | Easier to verify if recurrence relation is correct.<br>若遞迴關係正確，較易驗證。 |
| **Example**<br>**範例** | US Coin Change (1, 5, 10, 25).<br>美式硬幣找零。 | General Coin Change (e.g., coins 1, 3, 4; target 6).<br>一般硬幣找零（如硬幣 1, 3, 4；目標 6）。 |

**Trap**: Assuming Greedy works for all "optimization" problems.
**陷阱**：假設貪婪適用於所有「最佳化」問題。
*Always verify*: "If I take the largest item now, does it prevent me from fitting two smaller items later that would be better combined?"
*務必驗證*：「如果我現在拿了最大的項目，會不會阻止我稍後放入兩個較小但組合起來更好的項目？」

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）

1.  **Identify**: "This looks like an optimization problem. I want to maximize X."
    **識別**：「這看起來是個最佳化問題。我想要最大化 X。」
2.  **Hypothesize**: "I suspect a greedy approach might work if I sort by [Criteria]."
    **假設**：「我懷疑如果依據 [標準] 排序，貪婪法或許行得通。」
3.  **Justify (Crucial for Seniors)**: "Intuitively, processing the element with the smallest ending time leaves the most room for future elements."
    **證成（資深者關鍵）**：「直覺上，處理結束時間最早的元素，能為未來的元素保留最多空間。」

### Whiteboard Strategy（白板策略）

-   **Comparators**: Write the comparator logic clearly or use a lambda. Don't waste time implementing a full sorting algorithm (QuickSort/MergeSort) unless asked; use `std::sort`.
    **比較器**：清楚寫出比較邏輯或使用 lambda。除非被要求，否則別浪費時間實作完整的排序演算法（快排/合併排序）；使用 `std::sort`。
-   **Structure**:
    1.  Handle Edge Cases (Empty?).
    2.  Sort.
    3.  Iterate & Update `prev`.

### Common Follow-ups（常見追問）

-   "Can you prove why sorting by start time fails?" (Draw the counter-example).
    「你能證明為何依開始時間排序會失敗嗎？」（畫出反例）。
-   "What if the input is a stream?" (Suggest using a Heap/Priority Queue).
    「如果輸入是串流怎麼辦？」（建議使用堆積/優先佇列）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Assign Cookies (LeetCode 455)
**Hint**: Sort both children (greed factor) and cookies (size). Give the smallest sufficient cookie to the least greedy child.
**提示**：將孩子（貪婪因子）和餅乾（大小）都排序。將最小且足夠的餅乾分給最不貪婪的孩子。

### 2. Medium: Jump Game (LeetCode 55)
**Hint**: Iterate through the array and maintain a `maxReach` variable. If current index `i > maxReach`, you can't proceed.
**提示**：遍歷陣列並維護一個 `maxReach` 變數。若當前索引 `i > maxReach`，則無法繼續前進。
*Key Insight*: You don't need to know *exactly* which jump to take, just the range of reachable indices.
*關鍵洞察*：你不需要知道*確切*跳哪一步，只需知道可到達的索引範圍。

### 3. Medium/Hard: Gas Station (LeetCode 134)
**Hint**: If you can't travel from A to B, you can't travel from any station between A and B to B.
**提示**：如果你無法從 A 走到 B，那你也無法從 A 與 B 之間的任何站點走到 B。
*Standard Solution*: Calculate total surplus. If total gas < total cost, return -1. Else, find the start point using a greedy pass.
*標準解法*：計算總剩餘量。若總油量 < 總消耗，回傳 -1。否則，使用貪婪遍歷找出起點。

---

## 8. Quick Checklists（快速檢核表）

-   [ ] **Sorting**: Did I sort the input? If so, based on what key?
    **排序**：我有排序輸入嗎？如果有，是依據什麼鍵值？
-   [ ] **Local Optimality**: Does my choice at step `i` depend *only* on the state at `i` and not on future data?
    **局部最佳性**：我在步驟 `i` 的選擇是否*僅*取決於 `i` 的狀態，而不依賴未來的資料？
-   [ ] **Irrevocability**: Once I make a greedy choice, do I ever need to undo it? (If yes, it's likely Backtracking/DP, not Greedy).
    **不可撤銷性**：一旦做出貪婪選擇，我是否需要撤銷它？（若是，那可能是回溯/DP，而非貪婪）。
-   [ ] **Complexity**: Is it $O(N \log N)$ or better?
    **複雜度**：是否為 $O(N \log N)$ 或更好？

---

## 9. Memory Anchors（記憶錨點）

**The "Cashier" Analogy (收銀員類比)**:
Imagine you are a cashier giving change. You always give the largest denomination bill possible first ($20, then $10, then $5, then $1).
想像你是正在找零的收銀員。你總是先給最大面額的鈔票（先 $20，再 $10，再 $5，再 $1）。
*Why?* Because using a larger bill reduces the *count* of bills remaining most rapidly.
*為什麼？* 因為使用較大面額的鈔票能最快減少剩餘鈔票的*數量*。
*(Note: This only works for canonical coin systems!)*
*（註：這僅適用於標準硬幣系統！）*

**The "Short-Sighted Hiker" (短視的登山客)**:
Greedy is like a hiker who always takes the steepest step up, hoping to reach the highest peak. It works on a simple hill (convex problem), but might get stuck on a false peak in a complex mountain range (non-convex).
貪婪就像一個總是往最陡峭方向踏出一步的登山客，希望到達最高峰。這在簡單的山丘（凸問題）有效，但在複雜的山脈（非凸問題）可能會受困於假高峰。