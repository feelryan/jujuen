Here is the comprehensive interview guide for **Intervals**, tailored for the **Advanced** level and **Senior Software Engineer** audience.

這是一份針對 **Intervals（區間）** 的完整面試教材，專為 **進階（Advanced）** 程度與 **資深軟體工程師** 受眾量身打造。

---

# Advanced Intervals Guide for Senior Engineers
# 資深工程師進階區間（Intervals）指南

## 1. Learning Objectives (學習目標)

1.  **Master the "Sweep Line" Algorithm:** Move beyond simple sorting; understand how to decompose intervals into "events" to solve complex overlap problems.
    **掌握「掃描線」演算法：** 超越單純的排序；理解如何將區間分解為「事件」，以解決複雜的重疊問題。
2.  **Handle Dynamic Data Streams:** Learn to use `TreeMap` or Balanced BSTs to manage intervals that change over time (add/remove), a common system design follow-up.
    **處理動態資料流：** 學習使用 `TreeMap` 或平衡二元搜尋樹來管理隨時間變化（新增/移除）的區間，這是常見的系統設計追問。
3.  **Optimize for Resource Allocation:** Solve problems related to CPU scheduling, meeting rooms, or bandwidth allocation using Heaps and Greedy approaches.
    **優化資源分配：** 使用堆積（Heaps）和貪婪演算法（Greedy）解決與 CPU 排程、會議室或頻寬分配相關的問題。
4.  **Differentiate Interval Variants:** Distinguish between merging, intersecting, and finding gaps, and apply the correct pattern immediately.
    **區分區間變體：** 區分合併、交集和尋找空隙，並立即應用正確的模式。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
An interval represents a continuous range of values, usually defined by a start point and an end point, denoted as `[start, end]`.
區間代表一個連續的數值範圍，通常由起點和終點定義，表示為 `[start, end]`。

### Intuition (直覺)
Think of intervals as blocks of time on a calendar or segments on a 1D number line.
將區間想像成日曆上的時間區塊，或是一維數線上的線段。
The core complexity usually arises from their relative positioning: disjoint, overlapping, or contained.
核心複雜度通常來自於它們的相對位置：不相交、重疊或包含。

### Complexity (複雜度)
-   **Time:** Most interval problems require sorting, leading to a baseline of $O(N \log N)$.
    **時間：** 大多數區間問題需要排序，導致基準複雜度為 $O(N \log N)$。
-   **Space:** $O(N)$ to store the result or auxiliary structures like a Heap.
    **空間：** $O(N)$ 用於儲存結果或輔助結構（如堆積）。

### When to Use (適用場景)
-   Scheduling problems (meetings, tasks).
    排程問題（會議、任務）。
-   Resource merging (file ranges, memory blocks).
    資源合併（檔案範圍、記憶體區塊）。
-   Analyzing peak loads (concurrent users).
    分析峰值負載（並發使用者）。

### When NOT to Use (不適用場景)
-   When data is discrete and order doesn't matter (use HashMaps).
    當資料是離散的且順序不重要時（使用雜湊表）。
-   When the relationships are graphical/network-based (use Graphs).
    當關係是基於圖形/網絡時（使用圖論）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting + Iteration (排序 + 迭代)
Sort by start time. Iterate through the list and compare `current.end` with `next.start`.
按開始時間排序。迭代列表並比較 `current.end` 與 `next.start`。
*Use case: Merge Intervals, Insert Interval.*
*適用案例：合併區間、插入區間。*

### B. Min-Heap / Priority Queue (最小堆積 / 優先佇列)
Sort by start time, but use a Min-Heap to track the `end` times of active intervals (resources).
按開始時間排序，但使用最小堆積來追蹤活動區間（資源）的 `end` 時間。
*Use case: Meeting Rooms II (Minimum resources required).*
*適用案例：會議室 II（所需最少資源）。*

### C. Sweep Line (掃描線)
Decompose `[start, end]` into two events: `(start, +1)` and `(end, -1)`. Sort events by time and sweep across.
將 `[start, end]` 分解為兩個事件：`(start, +1)` 和 `(end, -1)`。按時間排序事件並進行掃描。
*Use case: Finding maximum overlap depth, Skyline problem.*
*適用案例：尋找最大重疊深度、天際線問題。*

### D. Two Pointers (雙指針)
Used when you have two sorted lists of intervals and need to find interactions between them.
當你有兩個已排序的區間列表，並需要找出它們之間的互動時使用。
*Use case: Interval List Intersections.*
*適用案例：區間列表交集。*

---

## 4. Example Walkthrough (範例講解)

### Problem: Meeting Rooms II (Minimum Conference Rooms)
### 問題：會議室 II（最少會議室數量）

**Problem Statement (問題重述):**
Given an array of meeting time intervals `intervals` where `intervals[i] = [start, end]`, return the minimum number of conference rooms required.
給定一個會議時間區間的陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳所需的最少會議室數量。

**Example:** `[[0, 30], [5, 10], [15, 20]]` -> Output: `2`

---

### Approach 1: Min-Heap (Standard Senior Solution)
### 思路 1：最小堆積（標準資深解法）

**Logic:**
1.  Sort meetings by start time.
    將會議按開始時間排序。
2.  Use a Min-Heap to store the **end times** of meetings currently in progress.
    使用最小堆積來儲存目前正在進行的會議之 **結束時間**。
3.  For each meeting, check if the earliest ending meeting (heap top) has finished before the current meeting starts.
    對於每個會議，檢查最早結束的會議（堆積頂部）是否在當前會議開始前已結束。
4.  If yes, reuse the room (poll from heap). If no, allocate a new room. Always add the current meeting's end time to the heap.
    如果是，重複使用該房間（從堆積取出）。如果否，分配新房間。總是將當前會議的結束時間加入堆積。

**Complexity:** Time $O(N \log N)$ (Sorting), Space $O(N)$ (Heap).

---

### Approach 2: Sweep Line (Advanced / Scalable Solution)
### 思路 2：掃描線（進階 / 可擴展解法）

**Logic:**
1.  Separate start and end times into two arrays/lists.
    將開始時間和結束時間分開存入兩個陣列/列表。
2.  Sort both arrays.
    對兩個陣列進行排序。
3.  Iterate through start times. If a start time is less than the current end time pointer, we need a room.
    迭代開始時間。如果開始時間小於當前的結束時間指針，我們需要一個房間。
4.  If a start time is greater or equal, a meeting ended, so we release a room (increment end pointer).
    如果開始時間大於或等於，表示有會議結束，我們釋放一個房間（增加結束指針）。

**Why this is better for Senior roles?** It avoids the overhead of a Heap object and demonstrates low-level pointer manipulation mastery.
**為什麼這對資深職位更好？** 它避免了堆積物件的開銷，並展示了對低階指針操作的掌握。

---

### Java Solution (Sweep Line Approach)
### Java 參考解（掃描線法）

```java
import java.util.Arrays;

public class MeetingRooms {

    /**
     * Calculates the minimum number of conference rooms required.
     * 計算所需的最少會議室數量。
     *
     * @param intervals 2D array representing start and end times.
     * @return Minimum rooms needed.
     */
    public int minMeetingRooms(int[][] intervals) {
        // Edge case check
        // 邊界條件檢查
        if (intervals == null || intervals.length == 0) {
            return 0;
        }

        int n = intervals.length;
        int[] startTimes = new int[n];
        int[] endTimes = new int[n];

        // Deconstruct intervals into separate start and end arrays
        // 將區間解構為獨立的開始與結束陣列
        for (int i = 0; i < n; i++) {
            startTimes[i] = intervals[i][0];
            endTimes[i] = intervals[i][1];
        }

        // Sort both arrays individually.
        // This is the essence of Sweep Line: we treat starts and ends as independent events.
        // 分別對兩個陣列排序。
        // 這是掃描線的精髓：我們將開始和結束視為獨立事件。
        Arrays.sort(startTimes);
        Arrays.sort(endTimes);

        int rooms = 0;
        int endPointer = 0;

        // Iterate through all start times
        // 迭代所有開始時間
        for (int i = 0; i < n; i++) {
            // If the current meeting starts BEFORE the earliest ending meeting finishes
            // 如果當前會議在最早結束的會議完成之前開始
            if (startTimes[i] < endTimes[endPointer]) {
                // We need a new room
                // 我們需要一個新房間
                rooms++;
            } else {
                // A meeting ended, we can reuse that room.
                // Move the end pointer to the next finishing meeting.
                // 有會議結束，我們可以重複使用該房間。
                // 將結束指針移動到下一個結束的會議。
                endPointer++;
            }
        }

        return rooms;
    }
}
```

### Common Mistake (錯誤示範)
**Mistake:** Sorting intervals by end time and just counting overlaps greedily without a heap or dual-sort.
**錯誤：** 僅按結束時間排序區間，並在沒有堆積或雙重排序的情況下貪婪地計算重疊。
**Why:** This works for "Max Non-Overlapping Intervals" (activity selection problem), but fails for counting *concurrent* depth.
**原因：** 這適用於「最大不重疊區間」（活動選擇問題），但無法正確計算 *並發* 深度。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description (描述) | Critical Detail (關鍵細節) |
| :--- | :--- | :--- |
| **Overlap Condition** | Checking if `[a, b]` and `[c, d]` overlap. | Overlap if `a < d` AND `c < b`. Be careful with `<=` vs `<`. <br> 重疊條件：`a < d` 且 `c < b`。注意 `<=` 與 `<` 的區別。 |
| **Interval Merging** | Combining `[1,3], [2,6]` into `[1,6]`. | New end is `Math.max(end1, end2)`, not just `end2`. <br> 新的結束點是 `Math.max(end1, end2)`，而不僅僅是 `end2`。 |
| **Comparator** | Sorting logic. | `(a, b) -> Integer.compare(a[0], b[0])` avoids overflow compared to `a[0] - b[0]`. <br> 使用 `Integer.compare` 避免減法造成的溢位。 |
| **Modifying List** | Removing items while iterating. | Do not remove from a list while iterating forward. Use a result list or iterate backward. <br> 不要在向前迭代時從列表中移除項目。使用結果列表或向後迭代。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Boundaries:** "Are the intervals inclusive `[a, b]` or exclusive `[a, b)`? Does `[1, 2]` and `[2, 3]` count as overlapping?"
    **釐清邊界：** 「區間是包含 `[a, b]` 還是不包含 `[a, b)`？`[1, 2]` 和 `[2, 3]` 算重疊嗎？」
2.  **Visualize:** Draw a number line on the whiteboard immediately. Draw stacked bars to represent overlaps.
    **視覺化：** 立即在白板上畫出一條數線。畫出堆疊的條形圖來表示重疊。
3.  **Propose Sort:** "Since the input is unsorted, my first instinct is to sort by start time to linearize the processing."
    **提出排序：** 「由於輸入未排序，我的第一直覺是按開始時間排序，以便線性化處理。」

### Whiteboard Strategy (白板策略)
-   Use `S` (Start) and `E` (End) markers on your number line.
    在數線上使用 `S`（起點）和 `E`（終點）標記。
-   Write down the sorting Lambda explicitly to show language proficiency.
    明確寫出排序 Lambda 表達式以展示語言熟練度。

### Common Follow-ups (常見追問)
-   **Q:** What if the intervals are too large to fit in memory (Stream)?
    **問：** 如果區間太大無法放入記憶體（串流）怎麼辦？
    **A:** Discuss processing in chunks or using a database/disk-based merge sort. If it's about checking overlaps in a stream, mention **Interval Trees** or **Segment Trees**.
    **答：** 討論分塊處理或使用資料庫/基於磁碟的合併排序。如果是檢查串流中的重疊，請提及 **區間樹** 或 **線段樹**。

---

## 7. Exercises (練習題)

### Easy: Merge Intervals
**Prompt:** Given a collection of intervals, merge all overlapping intervals.
**提示：** 給定一組區間，合併所有重疊的區間。
*Hint: Sort by start. Maintain a `currentInterval` and update its end if overlap occurs.*
*提示：按開始排序。維護一個 `currentInterval`，如果發生重疊則更新其結束點。*

### Medium: Interval List Intersections
**Prompt:** Given two lists of closed intervals, where each list is pairwise disjoint and sorted, return the intersection of these two interval lists.
**提示：** 給定兩個已排序且內部不相交的封閉區間列表，回傳這兩個區間列表的交集。
*Hint: Two pointers `i` and `j`. Intersection is `[max(start_i, start_j), min(end_i, end_j)]`. Move the pointer with the smaller end time.*
*提示：雙指針 `i` 和 `j`。交集為 `[max(start_i, start_j), min(end_i, end_j)]`。移動結束時間較小的指針。*

### Hard: Data Stream as Disjoint Intervals
**Prompt:** Implement a class that summarizes a data stream of integers into disjoint intervals. e.g., adding 1, 3, 7, 2, 6 should result in `[1, 3], [6, 7]`.
**提示：** 實作一個類別，將整數資料流總結為不相交的區間。例如，加入 1, 3, 7, 2, 6 應得到 `[1, 3], [6, 7]`。
*Hint: Use a `TreeMap<Start, End>` in Java. Use `floorKey` and `higherKey` to find adjacent intervals to merge dynamically.*
*提示：在 Java 中使用 `TreeMap<Start, End>`。使用 `floorKey` 和 `higherKey` 來尋找並動態合併相鄰的區間。*

---

## 8. Quick Checklist (快速檢核表)

-   [ ] **Sorted?** Did I sort the input? (Most interval problems fail without this).
    **已排序？** 我是否對輸入進行了排序？（大多數區間問題沒有這步都會失敗）。
-   [ ] **Empty Input?** Did I handle `null` or `[]`?
    **空輸入？** 我是否處理了 `null` 或 `[]`？
-   [ ] **Boundary Logic:** Did I use `Math.max` for merging ends and `Math.min` for intersections?
    **邊界邏輯：** 我是否在合併結束點時使用了 `Math.max`，在計算交集時使用了 `Math.min`？
-   [ ] **Loop Invariant:** Is my `prev` or `current` pointer updated correctly after a merge?
    **迴圈不變性：** 我的 `prev` 或 `current` 指針在合併後是否正確更新？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Paint Layers" Analogy (Sweep Line)
### 「油漆層」類比（掃描線）
Imagine painting stripes on a wall.
想像在牆上刷條紋。
-   Start time = Start painting a layer (+1 thickness).
    開始時間 = 開始刷一層（厚度 +1）。
-   End time = Stop painting a layer (-1 thickness).
    結束時間 = 停止刷一層（厚度 -1）。
-   The number of rooms needed is the **maximum thickness** of the paint at any point.
    所需的房間數量是任何點上的 **最大油漆厚度**。

### The "Zipper" Analogy (Two Pointers)
### 「拉鍊」類比（雙指針）
When finding intersections between two sorted lists, imagine closing a zipper.
當尋找兩個已排序列表的交集時，想像拉上拉鍊。
-   The teeth must align (overlap) to lock.
    齒必須對齊（重疊）才能鎖定。
-   You always pull the slider up past the tooth that ends first.
    你總是將拉鍊頭拉過最先結束的那個齒。