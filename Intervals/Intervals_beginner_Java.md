Here is the comprehensive interview preparation guide for **Intervals**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level (focusing on foundational mastery), with **Java** implementation.

這是一份針對 **區間（Intervals）** 的完整面試準備教材，專為資深軟體工程師量身打造，深度調整為 **初學者（Beginner）**（著重於基礎精通），並使用 **Java** 實作。

---

# Interview Guide: Intervals (Beginner Level)
# 面試指南：區間問題（初級）

## 1. Learning Objectives (學習目標)

*   **Master the Standard Representation:** Understand how to represent intervals and the difference between open `(a, b)` and closed `[a, b]` intervals.
    **掌握標準表示法：** 理解如何表示區間，以及開區間 `(a, b)` 與閉區間 `[a, b]` 的差異。
*   **Internalize the "Sort & Scan" Pattern:** Recognize that 90% of basic interval problems are solved by sorting by start time and iterating linearly.
    **內化「排序與掃描」模式：** 認知到 90% 的基礎區間問題都是通過按開始時間排序並進行線性遍歷來解決的。
*   **Handle Overlap Logic:** Learn the precise mathematical conditions for detecting overlaps and merging ranges.
    **處理重疊邏輯：** 學習檢測重疊與合併範圍的精確數學條件。
*   **Edge Case Management:** Develop reflexes for handling empty lists, single intervals, and touching boundaries (e.g., `[1,2]` and `[2,3]`).
    **邊界情況管理：** 培養處理空列表、單一區間以及接觸邊界（如 `[1,2]` 和 `[2,3]`）的直覺。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
An interval is a continuous range of values, usually defined by a start point and an end point.
區間是一個連續的數值範圍，通常由一個起點和一個終點定義。

### Intuition (直覺)
Think of intervals as events in a calendar or segments on a 1D number line.
將區間想像成行事曆中的事件，或是 1D 數線上的線段。

### Complexity (複雜度)
*   **Time:** Dominantly $O(N \log N)$ due to sorting. If already sorted, usually $O(N)$.
    **時間：** 由於排序，通常為主導的 $O(N \log N)$。如果已排序，通常為 $O(N)$。
*   **Space:** $O(1)$ or $O(N)$ depending on whether we modify the input in-place or return a new list.
    **空間：** $O(1)$ 或 $O(N)$，取決於我們是原地修改輸入還是返回新列表。

### When to Use (適用場景)
*   Scheduling problems (meeting rooms, CPU task scheduling).
    排程問題（會議室、CPU 任務調度）。
*   Merging continuous data ranges.
    合併連續的數據範圍。

### When NOT to Use (不適用場景)
*   When the data represents discrete, non-continuous points (use HashMaps or Sets).
    當數據代表離散、不連續的點時（使用 HashMaps 或 Sets）。
*   When dealing with 2D/3D spatial overlaps (requires Quad-Trees or R-Trees, though Sweep Line applies).
    當處理 2D/3D 空間重疊時（需要四元樹或 R-Trees，儘管掃描線算法也適用）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting by Start Time (按開始時間排序)
The most fundamental strategy. By sorting intervals based on their start times, you ensure that if an interval overlaps with the next one, they are adjacent in the list.
這是最基礎的策略。通過根據開始時間對區間進行排序，你可以確保如果一個區間與下一個區間重疊，它們在列表中是相鄰的。

### B. Greedy Approach (貪婪法)
Often used to find the maximum number of non-overlapping intervals (e.g., Activity Selection Problem). Usually involves sorting by **end time**.
常用於尋找最大數量的互不重疊區間（例如活動選擇問題）。通常涉及按 **結束時間** 排序。

### C. Pairwise Comparison (成對比較)
Iterating through the sorted list and comparing `current_interval` with `previous_interval` to decide whether to merge or insert.
遍歷已排序的列表，並將 `current_interval`（當前區間）與 `previous_interval`（前一個區間）進行比較，以決定合併或插入。

---

## 4. Example Walkthrough: Merge Intervals
## 範例講解：合併區間

### Problem Restatement (問題重述)
Given an array of intervals where `intervals[i] = [start, end]`, merge all overlapping intervals.
給定一個區間陣列，其中 `intervals[i] = [start, end]`，合併所有重疊的區間。
*Input:* `[[1,3],[2,6],[8,10],[15,18]]`
*Output:* `[[1,6],[8,10],[15,18]]`

### Thought Process (思路)

1.  **Brute Force (暴力法):** Compare every interval with every other interval. $O(N^2)$.
    **暴力法：** 將每個區間與其他所有區間進行比較。$O(N^2)$。
2.  **Optimization (優化):** If we sort them, overlapping intervals must be adjacent.
    **優化：** 如果我們對它們進行排序，重疊的區間必須是相鄰的。
3.  **Logic (邏輯):**
    *   Sort by `start`.
    *   Take the first interval as `current`.
    *   Check next interval: Does `next.start <= current.end`?
        *   **Yes:** Overlap! Extend `current.end` to `max(current.end, next.end)`.
        *   **No:** Disjoint. Add `current` to result, make `next` the new `current`.
    *   按 `start` 排序。
    *   取第一個區間作為 `current`。
    *   檢查下一個區間：`next.start <= current.end` 嗎？
        *   **是：** 重疊！將 `current.end` 擴展為 `max(current.end, next.end)`。
        *   **否：** 不相交。將 `current` 加入結果，讓 `next` 成為新的 `current`。

### Java Reference Solution (Java 參考解)

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public int[][] merge(int[][] intervals) {
        // 1. Handle edge cases: empty or null input
        // 1. 處理邊界情況：輸入為空或 null
        if (intervals == null || intervals.length <= 1) {
            return intervals;
        }

        // 2. Sort by start time (Ascending)
        // Time Complexity of sort: O(N log N)
        // 2. 按開始時間排序（升序）
        // 排序的時間複雜度：O(N log N)
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));

        List<int[]> result = new ArrayList<>();
        
        // Initialize with the first interval
        // 用第一個區間進行初始化
        int[] currentInterval = intervals[0];
        result.add(currentInterval);

        for (int[] interval : intervals) {
            int currentEnd = currentInterval[1];
            int nextStart = interval[0];
            int nextEnd = interval[1];

            // 3. Check for overlap
            // If the next interval starts before (or when) the current one ends
            // 3. 檢查重疊
            // 如果下一個區間在當前區間結束之前（或同時）開始
            if (nextStart <= currentEnd) {
                // Merge: Update the end time to the maximum of both
                // 合併：將結束時間更新為兩者中的最大值
                currentInterval[1] = Math.max(currentEnd, nextEnd);
            } else {
                // Disjoint: Move to the next interval
                // 不相交：移動到下一個區間
                currentInterval = interval;
                result.add(currentInterval);
            }
        }

        // Convert List<int[]> back to int[][]
        // 將 List<int[]> 轉回 int[][]
        return result.toArray(new int[result.size()][]);
    }
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N \log N)$ due to sorting. The linear scan is $O(N)$.
    **時間：** 由於排序為 $O(N \log N)$。線性掃描為 $O(N)$。
*   **Space:** $O(N)$ to store the output (or $O(\log N)$ for sorting stack space).
    **空間：** $O(N)$ 用於儲存輸出（或 $O(\log N)$ 用於排序堆疊空間）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Difference (陷阱 / 差異) |
| :--- | :--- |
| **Sorting Field** (排序欄位) | **Start vs. End Time:** Usually sort by *Start* for merging. Sort by *End* for removing minimum intervals (greedy scheduling). <br> **開始 vs. 結束時間：** 合併通常按 *開始* 排序。移除最少區間（貪婪排程）通常按 *結束* 排序。 |
| **Condition** (條件) | **Strict vs. Inclusive:** Overlap is usually `start <= end`. If `start < end`, then `[1,2]` and `[2,3]` do not overlap. Clarify this! <br> **嚴格 vs. 包含：** 重疊通常是 `start <= end`。如果是 `start < end`，則 `[1,2]` 和 `[2,3]` 不重疊。務必釐清這一點！ |
| **Object Reference** (物件引用) | **Modifying in Loop:** In Java, modifying `currentInterval[1]` inside the list works because arrays are objects (pass-by-reference). Be careful not to lose the reference. <br> **迴圈中修改：** 在 Java 中，修改列表內的 `currentInterval[1]` 是有效的，因為陣列是物件（傳址）。小心不要丟失引用。 |

---

## 6. Interview Strategy (面試實戰建議)

### Clarification Framework (闡述口條框架)
1.  **Ask about Order:** "Is the input list already sorted by start time, or should I handle that?"
    **詢問順序：**「輸入列表是否已經按開始時間排序，還是我需要處理？」
2.  **Define Overlap:** "Does `[1, 2]` and `[2, 3]` count as overlapping or just touching? I assume they merge into `[1, 3]`."
    **定義重疊：**「`[1, 2]` 和 `[2, 3]` 算作重疊還是僅僅接觸？我假設它們合併為 `[1, 3]`。」
3.  **State Strategy:** "I will sort the intervals first to bring potential overlaps together, then perform a linear scan."
    **陳述策略：**「我將首先對區間進行排序，將潛在的重疊聚集在一起，然後執行線性掃描。」

### Whiteboard Strategy (白板策略)
*   Draw a number line.
    畫一條數線。
*   Draw intervals as horizontal bars stacked vertically to show overlaps clearly.
    將區間畫成垂直堆疊的水平條，以清晰顯示重疊。
*   Use variable names like `currStart`, `currEnd`, `nextStart` to avoid index confusion (e.g., `intervals[i][0]`).
    使用 `currStart`, `currEnd`, `nextStart` 等變數名稱，以避免索引混淆（例如 `intervals[i][0]`）。

---

## 7. Practice Problems (練習題)

### Easy: Meeting Rooms (會議室)
*   **Problem:** Given an array of meeting time intervals, determine if a person can attend all meetings.
    **問題：** 給定一個會議時間區間的陣列，判斷一個人是否可以參加所有會議。
*   **Hint:** Sort by start time. If `intervals[i].end > intervals[i+1].start`, return false.
    **提示：** 按開始時間排序。如果 `intervals[i].end > intervals[i+1].start`，返回 false。

### Medium: Insert Interval (插入區間)
*   **Problem:** Insert a new interval into a sorted list of non-overlapping intervals and merge if necessary.
    **問題：** 將一個新區間插入到已排序且不重疊的區間列表中，並在必要時進行合併。
*   **Hint:** Three phases: 1. Add all before new interval. 2. Merge overlapping with new interval. 3. Add all after.
    **提示：** 三個階段：1. 加入新區間之前的所有區間。2. 合併與新區間重疊的部分。3. 加入之後的所有區間。

### Medium (Hard logic): Non-overlapping Intervals (無重疊區間)
*   **Problem:** Find the minimum number of intervals to remove to make the rest non-overlapping.
    **問題：** 找出需要移除的最少區間數量，使剩餘區間互不重疊。
*   **Hint:** Greedy approach. Sort by **end time**. Always keep the interval that ends earliest to leave space for future intervals.
    **提示：** 貪婪法。按 **結束時間** 排序。總是保留結束最早的區間，以便為未來的區間留出空間。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Sorted?** Did I sort the input? If not, is the logic valid?
    **已排序？** 我是否對輸入進行了排序？如果沒有，邏輯是否有效？
*   [ ] **Max End?** When merging, did I use `Math.max(end1, end2)`? (Common bug: using `end2` directly).
    **最大結束時間？** 合併時，我是否使用了 `Math.max(end1, end2)`？（常見錯誤：直接使用 `end2`）。
*   [ ] **Empty Input?** Did I handle `[]` or `null`?
    **空輸入？** 我是否處理了 `[]` 或 `null`？
*   [ ] **Return Type?** Does the problem ask for a count (int), a boolean, or a list of intervals?
    **返回類型？** 問題要求的是數量（int）、布林值，還是區間列表？

---

## 9. Memory Anchors (記憶錨點)

### The Zipper (拉鍊)
Visualize merging intervals like closing a **zipper**. You start from the bottom (earliest time) and as you move up, teeth (intervals) that are close together mesh into one continuous track.
將合併區間想像成拉上 **拉鍊**。你從底部（最早的時間）開始，當你向上移動時，靠得很近的齒（區間）會嚙合成一條連續的軌道。

### The Train Tracks (鐵軌)
Imagine laying down tracks. If a new track starts before the previous one ends, you don't build a new segment; you just **weld** them together to make the current track longer.
想像鋪設鐵軌。如果新鐵軌在前一條結束之前就開始了，你不需要建造新的路段；你只是將它們 **焊接** 在一起，使當前的鐵軌變長。