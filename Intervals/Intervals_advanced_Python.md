# Advanced Intervals Guide for Senior Engineers
# 資深工程師區間（Intervals）進階指南

## 1. Learning Objectives (學習目標)

1.  **Master the "Sort & Sweep" Pattern:** Understand why sorting is the prerequisite for 90% of interval problems and how to iterate efficiently.
    **掌握「排序與掃描」模式：** 理解為何排序是 90% 區間問題的先決條件，以及如何高效地進行迭代。
2.  **Differentiate Greedy Strategies:** Know when to sort by *start time* (merging/expanding) vs. *end time* (scheduling/max capacity).
    **區分貪婪策略：** 知道何時該依 *開始時間* 排序（合併/擴展），何時依 *結束時間* 排序（排程/最大容量）。
3.  **Handle "Sweep Line" Events:** Learn to decompose intervals into "Start" and "End" events to solve concurrency problems.
    **處理「掃描線」事件：** 學習將區間分解為「開始」與「結束」事件，以解決並發性問題。
4.  **Edge Case Precision:** Flawlessly handle open vs. closed intervals (`(a, b)` vs `[a, b]`) and single-point intervals.
    **精準處理邊界情況：** 完美處理開區間與閉區間（`(a, b)` vs `[a, b]`）以及單點區間。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Intervals represent continuous ranges in a 1D space, typically time or distance.
區間代表一維空間中的連續範圍，通常是時間或距離。
Intuitively, think of them as "blocks" on a timeline that can overlap, touch, or be disjoint.
直觀上，將它們視為時間軸上的「區塊」，這些區塊可能會重疊、接觸或不相交。

### Complexity (複雜度)
*   **Time:** Dominantly **$O(N \log N)$** due to sorting. Once sorted, processing is usually **$O(N)$**.
    **時間：** 由於排序，主要為 **$O(N \log N)$**。一旦排序完成，處理通常為 **$O(N)$**。
*   **Space:** **$O(1)$** or **$O(N)$** depending on whether we modify in-place or return a new list.
    **空間：** 取決於我們是原地修改還是返回新列表，通常為 **$O(1)$** 或 **$O(N)$**。

### When to Use (適用場景)
*   Scheduling conflicts (Calendar apps).
    排程衝突（行事曆應用）。
*   Merging overlapping data ranges.
    合併重疊的資料範圍。
*   Resource allocation (CPU tasks, memory blocks).
    資源分配（CPU 任務、記憶體區塊）。

### When NOT to Use (不適用場景)
*   When the data is inherently 2D or graph-based without a linear dimension.
    當資料本質上是二維或基於圖形，且沒有線性維度時。
*   When the order of input strictly matters and cannot be reordered (rare for interval problems).
    當輸入順序嚴格重要且不可重新排序時（在區間問題中較少見）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting by Start Time (依開始時間排序)
*   **Use case:** Merging intervals, finding coverage.
    **使用場景：** 合併區間、尋找覆蓋範圍。
*   **Logic:** If `current.start <= previous.end`, they overlap.
    **邏輯：** 若 `current.start <= previous.end`，則它們重疊。

### B. Sorting by End Time (依結束時間排序)
*   **Use case:** Finding the maximum number of non-overlapping intervals (Activity Selection Problem).
    **使用場景：** 尋找最大不重疊區間數量（活動選擇問題）。
*   **Logic:** Pick the interval that ends earliest to leave space for future intervals.
    **邏輯：** 選擇最早結束的區間，以便為未來的區間留出空間。

### C. Sweep Line / Event Processing (掃描線 / 事件處理)
*   **Use case:** Finding maximum concurrency (e.g., minimum meeting rooms).
    **使用場景：** 尋找最大並發量（例如：最少會議室）。
*   **Logic:** Decompose `[start, end]` into `(start, +1)` and `(end, -1)`, sort events, and maintain a running sum.
    **邏輯：** 將 `[start, end]` 分解為 `(start, +1)` 與 `(end, -1)`，排序事件，並維護累加總和。

### D. Two Pointers (雙指針)
*   **Use case:** Finding intersections between two sorted interval lists.
    **使用場景：** 在兩個已排序的區間列表中尋找交集。

---

## 4. Example Walkthrough (範例講解)

### Problem: Meeting Rooms II (Medium/Hard)
**Problem Statement:** Given an array of meeting time intervals `intervals` where `intervals[i] = [start_i, end_i]`, return the minimum number of conference rooms required.
**問題重述：** 給定一個會議時間區間陣列 `intervals`，其中 `intervals[i] = [start_i, end_i]`，回傳所需的最少會議室數量。

### Approach Evolution (思路演進)

1.  **Brute Force (暴力法):**
    *   For every meeting, check overlap with all other meetings. $O(N^2)$.
    *   對每個會議，檢查與其他所有會議的重疊情況。$O(N^2)$。
2.  **Optimization - Min-Heap (優化 - 最小堆積):**
    *   Sort meetings by start time. Use a Min-Heap to track the **end times** of ongoing meetings.
    *   依開始時間排序會議。使用最小堆積（Min-Heap）來追蹤進行中會議的 **結束時間**。
    *   If `current_meeting.start >= heap.min`, the room is free; pop the old meeting. Push the current meeting's end time.
    *   若 `current_meeting.start >= heap.min`，表示房間空閒；彈出舊會議。將當前會議的結束時間推入堆積。
    *   Heap size represents active rooms.
    *   堆積的大小代表活躍的房間數。
3.  **Optimization - Chronological Ordering (最佳解 - 時序排序):**
    *   Separate start and end times into two arrays, sort both. Use two pointers. This simulates the Sweep Line.
    *   將開始與結束時間分開為兩個陣列，分別排序。使用雙指針。這模擬了掃描線演算法。

### Python Solution (Min-Heap Approach)
*We choose the Heap approach as it is more intuitive for "resource allocation" interviews.*
*我們選擇堆積法，因為它在「資源分配」類的面試中更直觀。*

```python
import heapq
from typing import List

def minMeetingRooms(intervals: List[List[int]]) -> int:
    # Edge case: no intervals
    # 邊界情況：無區間
    if not intervals:
        return 0

    # 1. Sort by start time. This is crucial to process meetings chronologically.
    # 1. 依開始時間排序。這對於按時間順序處理會議至關重要。
    intervals.sort(key=lambda x: x[0])

    # Min-heap to store the end times of active meetings.
    # 最小堆積，用於儲存活躍會議的結束時間。
    free_rooms = []

    # Add the first meeting's end time.
    # 加入第一個會議的結束時間。
    heapq.heappush(free_rooms, intervals[0][1])

    # Iterate through the rest of the meetings
    # 迭代剩餘的會議
    for i in intervals[1:]:
        start_time = i[0]
        end_time = i[1]

        # Check if the room with the earliest end time is free.
        # 檢查最早結束的房間是否空閒。
        # If the earliest ending meeting ends before or at the current start time...
        # 如果最早結束的會議在當前開始時間之前或剛好結束...
        if free_rooms[0] <= start_time:
            # Reuse the room (pop the old meeting).
            # 重複使用該房間（彈出舊會議）。
            heapq.heappop(free_rooms)

        # If room is not free, we don't pop (allocate a new room).
        # Regardless, we push the current meeting's end time into the heap.
        # 如果房間不空閒，我們不彈出（分配新房間）。
        # 無論如何，我們將當前會議的結束時間推入堆積。
        heapq.heappush(free_rooms, end_time)

    # The size of the heap tells us the minimum rooms required.
    # 堆積的大小告訴我們所需的最少房間數。
    return len(free_rooms)

# Complexity Analysis:
# Time: O(N log N) due to sorting. Heap operations take O(N log N) in worst case.
# Space: O(N) for the heap.
# 複雜度分析：
# 時間：O(N log N)，因為排序。堆積操作最壞情況下為 O(N log N)。
# 空間：O(N)，用於堆積。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall | Correction |
| :--- | :--- | :--- |
| **Sorting Key** | Sorting by `end` time for merging problems. | **Always sort by `start`** for merging. Sort by `end` for removing overlaps (greedy activity selection). <br> **合併問題永遠依 `start` 排序**。移除重疊（貪婪活動選擇）才依 `end` 排序。 |
| **Overlap Condition** | Confusing `>` with `>=`. | Clarify if `[1, 2]` and `[2, 3]` overlap. Usually, touching is merging, but not conflict. <br> 釐清 `[1, 2]` 與 `[2, 3]` 是否重疊。通常，接觸算合併，但不算衝突。 |
| **Loop Modification** | Modifying the list while iterating (e.g., `del list[i]`). | Create a `merged` list and append to it, or use a `while` loop with manual index control. <br> 建立一個 `merged` 列表並加入其中，或使用 `while` 迴圈手動控制索引。 |
| **Input Mutation** | Sorting the input array in-place without permission. | Ask the interviewer if side effects are allowed. If not, sort a copy. <br> 詢問面試官是否允許副作用。如果不允許，請對副本進行排序。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Are the intervals sorted? Does `[1,2]` and `[2,3]` count as overlapping?"
    **釐清：** 「區間是否已排序？`[1,2]` 和 `[2,3]` 算重疊嗎？」
2.  **Visualise:** "I will draw a number line to visualize the overlaps." (Draw simple lines on the whiteboard).
    **視覺化：** 「我會畫一條數線來視覺化重疊情況。」（在白板上畫出簡單的線段）。
3.  **Propose:** "Since we are dealing with merging/overlaps, sorting by start time is the natural first step to linearize the problem."
    **提案：** 「由於我們在處理合併/重疊，依開始時間排序是將問題線性化的自然第一步。」

### Whiteboard Strategy (白板策略)
*   Draw intervals stacked vertically to show concurrency clearly.
    垂直堆疊畫出區間，以清晰顯示並發性。
*   Use a variable like `curr_end` to mark the active boundary.
    使用如 `curr_end` 的變數來標記當前邊界。

### Common Follow-ups (常見追問)
*   **Q:** What if the range of numbers is small (e.g., 0 to 1000)?
    **A:** Use **Bucket Sort** or a static array (Boolean array) for $O(N)$ or $O(Range)$ time.
    **問：** 如果數字範圍很小（例如 0 到 1000）怎麼辦？
    **答：** 使用 **桶排序** 或靜態陣列（布林陣列），時間複雜度為 $O(N)$ 或 $O(Range)$。
*   **Q:** What if the data comes as a stream?
    **A:** Use a **Balanced BST (TreeMap in Java)** or **Segment Tree** to insert/query in $O(\log N)$.
    **問：** 如果資料是以串流形式進來怎麼辦？
    **答：** 使用 **平衡二元搜尋樹（Java 中的 TreeMap）** 或 **線段樹**，以 $O(\log N)$ 進行插入/查詢。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Warm-up)
**Problem:** **Merge Intervals** (LeetCode 56)
**Hint:** Sort by start. Iterate. If `curr.start <= last_merged.end`, update `last_merged.end = max(last_merged.end, curr.end)`.
**提示：** 依開始時間排序。迭代。若 `curr.start <= last_merged.end`，更新 `last_merged.end = max(last_merged.end, curr.end)`。

### Level 2: Intermediate (Core Pattern)
**Problem:** **Interval List Intersections** (LeetCode 986)
**Hint:** Two pointers `i`, `j`. Intersection is `[max(start_i, start_j), min(end_i, end_j)]`. Move the pointer of the interval that ends earlier.
**提示：** 雙指針 `i`, `j`。交集為 `[max(start_i, start_j), min(end_i, end_j)]`。移動較早結束的區間的指針。

### Level 3: Advanced (Differentiation)
**Problem:** **Employee Free Time** (LeetCode 759 - Hard)
**Problem Statement:** Given a list of schedules for employees (non-overlapping per employee), find the common free time for all.
**問題重述：** 給定員工的行程表列表（每位員工內部不重疊），找出所有人的共同空閒時間。
**Hint:** Flatten all intervals into one list. Sort by start time. Merge them into one big "busy" timeline. The gaps between merged intervals are the "free time".
**提示：** 將所有區間展平為一個列表。依開始時間排序。將它們合併為一個大的「忙碌」時間軸。合併區間之間的空隙即為「空閒時間」。

---

## 8. Quick Checklist (快速檢核表)

*   [ ] **Sorted?** Did I sort the input? (Most interval problems fail without this).
    **已排序？** 我是否對輸入進行了排序？（大多數區間問題沒有這步都會失敗）。
*   [ ] **Empty Input?** Did I handle `intervals = []`?
    **空輸入？** 我是否處理了 `intervals = []`？
*   [ ] **Max End?** When merging, did I use `max(prev_end, curr_end)`? (Don't just take `curr_end`, the previous one might be longer).
    **最大結束時間？** 合併時，我是否使用了 `max(prev_end, curr_end)`？（不要只取 `curr_end`，前一個可能更長）。
*   [ ] **Strictness?** Did I check `<` vs `<=` correctly for the specific problem constraints?
    **嚴格性？** 我是否針對特定問題限制正確檢查了 `<` 與 `<=`？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Zipper" (拉鍊)
*   **Concept:** Merging Intervals.
*   **Image:** Imagine a zipper closing. If the teeth (intervals) overlap, they become one continuous track. You only start a new track when there is a gap.
*   **概念：** 合併區間。
*   **圖像：** 想像拉鍊拉上。如果齒（區間）重疊，它們變成一條連續的軌道。只有當出現空隙時，你才開始一條新軌道。

### The "Hotel Check-in" (飯店登記入住)
*   **Concept:** Meeting Rooms II (Sweep Line).
*   **Image:**
    *   `Start Time`: Guest arrives (+1 person in lobby).
    *   `End Time`: Guest leaves (-1 person in lobby).
    *   **Max people in lobby** = Max rooms needed.
*   **概念：** 會議室 II（掃描線）。
*   **圖像：**
    *   `開始時間`：客人到達（大廳人數 +1）。
    *   `結束時間`：客人離開（大廳人數 -1）。
    *   **大廳最大人數** = 所需最大房間數。