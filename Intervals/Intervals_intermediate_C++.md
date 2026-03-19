Here is the complete interview preparation guide for **Intervals**, tailored for a Senior Software Engineer, written in C++ with bilingual explanations.

這是一份針對 **區間（Intervals）** 的完整面試準備指南，專為資深軟體工程師量身打造，使用 C++ 撰寫並附帶雙語解說。

---

# Interview Guide: Intervals (Intermediate)
# 面試指南：區間問題（中階）

## 1. Learning Goals（學習目標）

1.  **Master the "Sort & Merge" Pattern:** Understand why sorting by start time is the prerequisite for 90% of interval problems.
    **掌握「排序與合併」模式：** 理解為何依據開始時間排序是 90% 區間問題的先決條件。
2.  **Internalize the "Sweep Line" Concept:** Learn to decompose intervals into "Start" and "End" events to handle complex overlaps.
    **內化「掃描線」概念：** 學習將區間分解為「開始」與「結束」事件，以處理複雜的重疊問題。
3.  **Handle Edge Cases Precisely:** Distinguish between open `(a, b)` and closed `[a, b]` intervals, and handle touching intervals `[1,2], [2,3]`.
    **精確處理邊界情況：** 區分開區間 `(a, b)` 與閉區間 `[a, b]`，並處理相切區間 `[1,2], [2,3]`。
4.  **Optimize Space Complexity:** Learn to perform operations in-place or with minimal auxiliary space.
    **優化空間複雜度：** 學習如何原地（in-place）執行操作或使用最小輔助空間。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
An interval represents a continuous range of values, usually time or numbers, denoted as `[start, end]`.
區間代表數值（通常是時間或數字）的連續範圍，表示為 `[start, end]`。

Intuitively, visualize them as horizontal bars on a timeline. The core challenge is almost always determining the relationship between two bars: do they overlap, touch, or are they disjoint?
直觀上，將它們想像成時間軸上的水平長條。核心挑戰幾乎總是判斷兩條長條的關係：它們是重疊、相切，還是不相交？

### Complexity Analysis（複雜度分析）
*   **Time Complexity:** Usually dominated by sorting, $O(N \log N)$. If the input is already sorted, many problems can be solved in $O(N)$.
    **時間複雜度：** 通常由排序主導，即 $O(N \log N)$。如果輸入已排序，許多問題可在 $O(N)$ 內解決。
*   **Space Complexity:** $O(1)$ or $O(N)$ depending on whether we create a new list for the result.
    **空間複雜度：** $O(1)$ 或 $O(N)$，取決於我們是否為結果建立新的列表。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** Scheduling meetings, merging calendar events, finding gaps in coverage, resource allocation.
    **適用於：** 會議排程、合併行事曆事件、尋找覆蓋缺口、資源分配。
*   **Not use when:** The data represents discrete points without continuity, or when the problem is actually a graph problem (e.g., dependency resolution).
    **不適用於：** 資料代表不具連續性的離散點，或問題實際上是圖論問題（例如依賴解析）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Sorting by Start Time (Most Common)
**依開始時間排序（最常見）**
Sort intervals by their start times. This ensures that when you process intervals, you only need to compare the current interval with the *previous* one or the *last added* one.
依據開始時間對區間進行排序。這確保了在處理區間時，你只需要將當前區間與「前一個」或「最後加入」的區間進行比較。

### B. Sweep Line (Events Decomposition)
**掃描線（事件分解）**
Break an interval `[start, end]` into two events: `(start, +1)` and `(end, -1)`. Sort these events by time. Iterate through them to count active intervals.
將區間 `[start, end]` 分解為兩個事件：`(start, +1)` 與 `(end, -1)`。依時間排序這些事件。遍歷它們以計算當前活躍的區間數量。

### C. Two Pointers
**雙指針**
Used when you have two separate lists of intervals (e.g., finding the intersection of two users' free times).
當你有兩個獨立的區間列表時使用（例如：尋找兩個使用者空閒時間的交集）。

### D. Greedy Strategy (Sorting by End Time)
**貪婪策略（依結束時間排序）**
Specifically used for "Maximum Non-overlapping Intervals" problems. Sorting by end time allows you to finish the current task as early as possible to leave room for the next.
專門用於「最大不重疊區間」問題。依結束時間排序讓你能儘早結束當前任務，為下一個任務留出空間。

---

## 4. Example Walkthrough: Merge Intervals
## 範例講解：合併區間

### Problem Statement（問題重述）
Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.
給定一個區間陣列，其中 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間，並返回一個涵蓋輸入中所有區間的不重疊區間陣列。

### Approach: Brute Force → Optimization（思路：暴力 → 優化）

1.  **Brute Force:** Compare every interval with every other interval. If they overlap, merge them. Repeat until no overlaps exist. Complexity: $O(N^2)$.
    **暴力法：** 將每個區間與其他所有區間比較。如果重疊，則合併。重複直到沒有重疊為止。複雜度：$O(N^2)$。

2.  **Optimal (Sort & Merge):**
    **最佳解（排序與合併）：**
    *   Sort the intervals by `start` time.
        依 `start` 時間排序區間。
    *   Iterate through the sorted list.
        遍歷排序後的列表。
    *   If the current interval overlaps with the last merged interval (i.e., `current.start <= last_merged.end`), merge them by updating the `end` of the last merged interval.
        如果當前區間與最後合併的區間重疊（即 `current.start <= last_merged.end`），透過更新最後合併區間的 `end` 來合併它們。
    *   Otherwise, push the current interval as a new entry.
        否則，將當前區間作為新條目加入。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        // Edge case: empty input
        // 邊界情況：輸入為空
        if (intervals.empty()) return {};

        // 1. Sort by start time.
        //    std::sort on vector<vector<int>> sorts by the first element by default.
        // 1. 依開始時間排序。
        //    std::sort 對 vector<vector<int>> 預設會依第一個元素排序。
        sort(intervals.begin(), intervals.end());

        vector<vector<int>> merged;
        
        // Initialize with the first interval
        // 用第一個區間進行初始化
        merged.push_back(intervals[0]);

        for (int i = 1; i < intervals.size(); ++i) {
            // Get reference to the last added interval to avoid copying
            // 取得最後加入區間的引用以避免複製
            vector<int>& last = merged.back();
            const vector<int>& current = intervals[i];

            // Check for overlap. Note: [1,3] and [3,6] overlap/touch.
            // 檢查重疊。注意：[1,3] 和 [3,6] 視為重疊/相切。
            if (current[0] <= last[1]) {
                // Merge: The new end is the max of both ends.
                // 合併：新的結束時間是兩者結束時間的最大值。
                last[1] = max(last[1], current[1]);
            } else {
                // No overlap, add current interval to result.
                // 無重疊，將當前區間加入結果。
                merged.push_back(current);
            }
        }

        return merged;
    }
};
```

### Complexity & Analysis（複雜度與分析）
*   **Time:** $O(N \log N)$ due to sorting. The linear scan takes $O(N)$.
    **時間：** $O(N \log N)$，歸因於排序。線性掃描花費 $O(N)$。
*   **Space:** $O(N)$ to store the output (or $O(\log N)$ stack space for sorting if we ignore output).
    **空間：** $O(N)$ 用於儲存輸出（若忽略輸出，則為排序所需的 $O(\log N)$ 堆疊空間）。

### Common Mistake（錯誤示範）
*   **Mistake:** Updating `last[1] = current[1]` directly without `max`.
    **錯誤：** 直接更新 `last[1] = current[1]` 而未使用 `max`。
*   **Why wrong:** Consider `[1, 10]` and `[2, 5]`. If you just take `current[1]`, the result becomes `[1, 5]`, shrinking the interval incorrectly.
    **為何錯：** 考慮 `[1, 10]` 和 `[2, 5]`。如果你只取 `current[1]`，結果變成 `[1, 5]`，錯誤地縮小了區間。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation (解釋) |
| :--- | :--- |
| **Sort by Start vs. End** | **Start:** Merging intervals, finding gaps. <br> **End:** Finding max non-overlapping intervals (Greedy scheduling). <br> **開始：** 合併區間、尋找缺口。<br> **結束：** 尋找最大不重疊區間（貪婪排程）。 |
| **Overlapping Condition** | Overlap exists if `Start_B <= End_A` (assuming A starts before B). <br> Be careful with `<` vs `<=`. Usually, `[1,2]` and `[2,3]` are merged. <br> 重疊發生於 `Start_B <= End_A`（假設 A 在 B 之前開始）。<br> 小心 `<` 與 `<=` 的區別。通常 `[1,2]` 與 `[2,3]` 會被合併。 |
| **Modifying Input** | Avoid deleting elements from the input vector while iterating (causes $O(N^2)$ shifting). Create a new `result` vector. <br> 避免在遍歷時從輸入向量中刪除元素（會導致 $O(N^2)$ 的位移）。建立一個新的 `result` 向量。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **Clarify Order:** "Is the input list sorted by start time, or should I handle the sorting first?"
    **確認順序：** 「輸入列表是否已按開始時間排序，還是我需要先處理排序？」
2.  **Define Overlap:** "Does `[1, 2]` and `[2, 3]` count as overlapping? (Touching vs Overlapping)"
    **定義重疊：** 「`[1, 2]` 和 `[2, 3]` 算重疊嗎？（相切 vs 重疊）」
3.  **Propose Approach:** "I will sort the intervals and use a greedy approach to merge them in a single pass."
    **提出方法：** 「我將對區間進行排序，並使用貪婪策略在一次遍歷中合併它們。」

### Whiteboard Strategy（白板策略）
*   Draw a timeline axis.
    畫一條時間軸。
*   Draw bars above the axis.
    在軸上方畫出長條。
*   Use vertical dotted lines to show where comparisons happen (e.g., `current.start` vs `prev.end`).
    使用垂直虛線顯示比較發生的位置（例如 `current.start` 對比 `prev.end`）。

### Common Follow-ups（常見追問）
*   *Q: What if the intervals are too large to fit in memory (Stream of intervals)?*
    *A: If sorted, process one by one. If unsorted, we might need a Segment Tree or map-reduce approach (sharding by time range).*
    *問：如果區間太大無法放入記憶體（區間串流）怎麼辦？*
    *答：若已排序，逐一處理。若未排序，可能需要線段樹或 Map-Reduce 方法（依時間範圍分片）。*

---

## 7. Practice Problems（練習題）

### Easy: Meeting Rooms (Overlap Check)
**題目：** Given an array of meeting time intervals, determine if a person can attend all meetings.
**給定一組會議時間區間，判斷一個人是否能參加所有會議。**
*   **Hint:** Sort by start time. Check if `intervals[i][0] < intervals[i-1][1]`.
*   **提示：** 依開始時間排序。檢查是否 `intervals[i][0] < intervals[i-1][1]`。

### Medium: Insert Interval
**題目：** Insert a new interval into a sorted list of non-overlapping intervals and merge if necessary.
**將一個新區間插入已排序且不重疊的區間列表中，必要時進行合併。**
*   **Hint:** Three stages: 1. Add all intervals ending before newInterval. 2. Merge overlapping intervals with newInterval. 3. Add remaining intervals.
*   **提示：** 三階段：1. 加入所有在新區間之前結束的區間。 2. 合併與新區間重疊的區間。 3. 加入剩餘區間。

### Hard: Employee Free Time (Sweep Line / Heap)
**題目：** Given schedules of multiple employees, find the finite common free time intervals.
**給定多位員工的行程表，找出有限的共同空閒時間區間。**
*   **Hint:** Flatten all intervals into one list, sort by start time. Use a counter or track `max_end` to find gaps where no one is working. Alternatively, use a Min-Heap to track the earliest ending active interval.
*   **提示：** 將所有區間攤平為一個列表，依開始時間排序。使用計數器或追蹤 `max_end` 來找出無人工作的空檔。或者，使用 Min-Heap 追蹤最早結束的活躍區間。

---

## 8. Quick Checklists（快速檢核表）

**Self-Review / Debugging (自我審查/除錯):**

*   [ ] **Sorting:** Did I sort the input? (Most interval bugs come from unsorted input).
    **排序：** 我是否對輸入進行了排序？（大多數區間 Bug 來自未排序的輸入）。
*   [ ] **Empty Input:** Did I handle `intervals.size() == 0`?
    **空輸入：** 我是否處理了 `intervals.size() == 0`？
*   [ ] **Max Logic:** In merge logic, did I use `max(prev.end, curr.end)`?
    **最大值邏輯：** 在合併邏輯中，我是否使用了 `max(prev.end, curr.end)`？
*   [ ] **Reference:** Did I use `vector<int>&` to avoid copying large vectors in loops?
    **引用：** 我是否使用了 `vector<int>&` 以避免在迴圈中複製大型向量？

---

## 9. Memory Anchors（記憶錨點）

*   **The Zipper (拉鍊):**
    Imagine the "Merge Intervals" algorithm as a zipper. It moves from left to right, pulling separate teeth (intervals) together if they are close enough (overlap).
    將「合併區間」演算法想像成拉鍊。它從左向右移動，如果牙齒（區間）夠近（重疊），就將它們拉在一起。

*   **The Security Guard (保全):**
    For "Non-overlapping Intervals" (Greedy), imagine a security guard who wants to finish their shift as early as possible. They always pick the task that *ends* earliest to be free for the next one.
    對於「不重疊區間」（貪婪法），想像一個想儘早下班的保全。他們總是選擇*最早結束*的任務，以便有空處理下一個任務。