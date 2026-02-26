# Interview Guide: Intervals (Intermediate to Advanced)
# 面試指南：區間問題（中階至進階）

## 1. Learning Goals (學習目標)

1.  **Master the "Sort & Sweep" Pattern:** Understand why sorting is almost always the first step in interval problems.
    **掌握「排序與掃描」模式：** 理解為何排序幾乎總是解決區間問題的第一步。
2.  **Handle Overlap Logic Flawlessly:** Gain muscle memory for detecting overlaps (`start_a <= end_b`) and merging logic (`max(end_a, end_b)`).
    **完美處理重疊邏輯：** 建立偵測重疊（`start_a <= end_b`）與合併邏輯（`max(end_a, end_b)`）的肌肉記憶。
3.  **Differentiate Greedy vs. Dynamic Programming:** Learn when to simply sort (Greedy) and when optimal substructure is required (DP).
    **區分貪婪演算法與動態規劃：** 學習何時只需排序（貪婪），何時需要最佳子結構（DP）。
4.  **Manage Edge Cases:** Comfortably handle empty lists, single intervals, and touching boundaries (e.g., `[1,2]` and `[2,3]`).
    **管理邊界情況：** 自在處理空列表、單一區間以及邊界接觸的情況（例如 `[1,2]` 與 `[2,3]`）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
An interval represents a range of values, usually defined by a start and an end point $[start, end]$.
區間代表數值的一個範圍，通常由起點與終點定義 $[start, end]$。

### Intuition (直覺)
Think of intervals as events on a calendar or segments on a 1D number line.
將區間想像成行事曆上的事件，或是 1D 數線上的線段。
The core complexity usually comes from the chaotic ordering of these segments.
核心複雜度通常來自這些線段的混亂排序。

### Complexity (複雜度)
-   **Time:** Most interval problems require sorting, leading to a baseline of $O(N \log N)$. If already sorted, often $O(N)$.
    **時間：** 大多數區間問題需要排序，導致基準為 $O(N \log N)$。若已排序，通常為 $O(N)$。
-   **Space:** $O(1)$ or $O(N)$ depending on whether we create a new list for the result.
    **空間：** $O(1)$ 或 $O(N)$，取決於我們是否為結果建立新列表。

### When to Use (適用場景)
-   Scheduling meetings (resource allocation).
    安排會議（資源分配）。
-   Merging file chunks or memory blocks.
    合併檔案區塊或記憶體區塊。
-   Analyzing continuous periods (e.g., stock trends, log analysis).
    分析連續期間（例如股票趨勢、日誌分析）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting + Linear Scan (排序 + 線性掃描)
Sort by start time. Iterate through the list and compare the current interval's start with the previous interval's end.
依開始時間排序。遍歷列表並將當前區間的開始時間與前一個區間的結束時間進行比較。
*Used in: Merge Intervals, Non-overlapping Intervals.*

### B. Two Pointers (雙指針)
Used when dealing with two sorted lists of intervals. One pointer for list A, one for list B.
用於處理兩個已排序的區間列表。一個指針指向列表 A，一個指向列表 B。
*Used in: Interval List Intersections.*

### C. Sweep Line / Events (掃描線 / 事件法)
Decompose an interval `[start, end]` into two events: `(start, +1)` and `(end, -1)`. Sort events and sweep across the timeline.
將區間 `[start, end]` 分解為兩個事件：`(start, +1)` 與 `(end, -1)`。排序事件並掃描時間軸。
*Used in: Meeting Rooms II (Max concurrent intervals).*

### D. Min-Heap (最小堆積)
Keep track of "active" intervals (usually their end times) to manage resources efficiently.
追蹤「活動中」的區間（通常是它們的結束時間），以有效管理資源。
*Used in: Meeting Rooms II (Alternative to Sweep Line).*

---

## 4. Example Walkthrough (範例講解)

### Example 1: Merge Intervals (經典題：合併區間)

**Problem Statement:**
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals.
給定一個 `intervals` 陣列，其中 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間。

**Approach (思路):**
1.  **Brute Force:** Compare every interval with every other interval. $O(N^2)$. Too slow.
    **暴力法：** 將每個區間與其他所有區間比較。$O(N^2)$。太慢。
2.  **Optimization:** If we sort by `start` time, overlapping intervals will be adjacent.
    **優化：** 如果我們按 `start` 時間排序，重疊的區間將會相鄰。
3.  **Logic:** Initialize `merged` list. For each interval, if it overlaps with the last one in `merged`, update the end time. Otherwise, add it.
    **邏輯：** 初始化 `merged` 列表。對於每個區間，若與 `merged` 中最後一個重疊，更新結束時間。否則，將其加入。

**Python Solution:**

```python
from typing import List

def merge(intervals: List[List[int]]) -> List[List[int]]:
    # Edge case: empty list
    # 邊界情況：空列表
    if not intervals:
        return []

    # Sort by start time. This is the crucial step.
    # 依開始時間排序。這是關鍵步驟。
    # Complexity: O(N log N)
    intervals.sort(key=lambda x: x[0])

    merged = []
    
    for interval in intervals:
        # If merged is empty or no overlap with the last merged interval
        # 如果 merged 為空，或與最後一個合併區間無重疊
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            # Overlap detected: merge by extending the end time
            # 偵測到重疊：藉由延伸結束時間來合併
            # Note: We must take the max, because the current interval might be fully inside the previous one.
            # 注意：我們必須取最大值，因為當前區間可能完全在包含在前一個區間內。
            merged[-1][1] = max(merged[-1][1], interval[1])
            
    return merged

# Time Complexity: O(N log N) due to sorting.
# Space Complexity: O(N) to store the output (or O(log N) for sorting stack depending on implementation).
```

---

### Example 2: Meeting Rooms II (會議室 II - Resource Allocation)

**Problem Statement:**
Given an array of meeting time intervals, find the minimum number of conference rooms required.
給定一組會議時間區間，找出所需的最少會議室數量。

**Approach (思路):**
1.  **Intuition:** We need a room for every overlapping meeting.
    **直覺：** 每個重疊的會議都需要一間房間。
2.  **Min-Heap Strategy:**
    **最小堆積策略：**
    -   Sort meetings by start time.
        依開始時間排序會議。
    -   Use a Min-Heap to store the **end times** of active meetings.
        使用最小堆積來儲存活動中會議的 **結束時間**。
    -   If the earliest ending meeting (heap top) ends before the new meeting starts, we can re-use that room (pop from heap).
        如果最早結束的會議（堆頂）在新會議開始前結束，我們可以重複使用該房間（從堆中彈出）。
    -   Always push the new meeting's end time.
        總是將新會議的結束時間推入堆中。

**Python Solution:**

```python
import heapq

def minMeetingRooms(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0
        
    # Sort by start time to process meetings chronologically
    # 依開始時間排序，以按時間順序處理會議
    intervals.sort(key=lambda x: x[0])
    
    # Min-heap to store end times of active meetings
    # 最小堆積，用於儲存活動中會議的結束時間
    free_rooms = []
    
    # Push the first meeting's end time
    # 推入第一個會議的結束時間
    heapq.heappush(free_rooms, intervals[0][1])
    
    for i in range(1, len(intervals)):
        # intervals[i][0] is current start time
        # free_rooms[0] is the earliest end time of current meetings
        # intervals[i][0] 是當前開始時間
        # free_rooms[0] 是當前會議中最早的結束時間
        
        # If the room with the earliest end time is free by now
        # 如果最早結束的房間現在已經空閒
        if free_rooms[0] <= intervals[i][0]:
            heapq.heappop(free_rooms) # Reuse room (remove old end time) / 重複使用房間（移除舊結束時間）
            
        # Add the current meeting's end time (whether new room or reused)
        # 加入當前會議的結束時間（無論是新房間還是重複使用的）
        heapq.heappush(free_rooms, intervals[i][1])
        
    # The size of the heap represents the max concurrent meetings
    # 堆積的大小代表最大同時進行的會議數
    return len(free_rooms)

# Time Complexity: O(N log N) for sorting + O(N log N) for heap operations.
# Space Complexity: O(N) for the heap.
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Sort by Start vs. End** | Usually sort by **Start** to merge/insert. Sort by **End** is typically for "Max Non-overlapping Intervals" (Greedy strategy to leave space for future intervals).<br>通常依 **開始時間** 排序來合併/插入。依 **結束時間** 排序通常用於「最大不重疊區間」（貪婪策略，為未來區間留出空間）。 |
| **Strict vs. Non-Strict** | `end < start` vs `end <= start`. Clarify if `[1,2]` and `[2,3]` overlap. Usually, they touch but don't overlap for merging, but consume resource continuity.<br>`end < start` 對比 `end <= start`。確認 `[1,2]` 與 `[2,3]` 是否重疊。通常它們接觸但不重疊（合併時），但會佔用資源連續性。 |
| **Modifying Input** | Avoid deleting from the list while iterating (index shifting bugs). Create a new result list instead.<br>避免在遍歷時從列表中刪除（會導致索引位移錯誤）。建立一個新的結果列表代替。 |
| **Max Logic** | When merging `[1, 5]` and `[2, 4]`, the new end is `max(5, 4) = 5`, not just the second interval's end.<br>當合併 `[1, 5]` 與 `[2, 4]` 時，新終點是 `max(5, 4) = 5`，而不僅是第二個區間的終點。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Ordering:** "Are the intervals sorted? If not, I should sort them first, which will cost $O(N \log N)$."
    **釐清排序：** 「區間是已排序的嗎？若沒有，我應該先排序，這會花費 $O(N \log N)$。」
2.  **Visual Analogy:** "I'll visualize this as a timeline. I want to sweep across and maintain the state of active intervals."
    **視覺類比：** 「我會將其視覺化為時間軸。我想要掃描過去並維護活動區間的狀態。」
3.  **Edge Cases First:** "I'll handle the empty input case immediately."
    **優先處理邊界：** 「我會立刻處理空輸入的情況。」

### Whiteboard Strategy (白板策略)
-   Draw a number line.
    畫一條數線。
-   Draw intervals as horizontal bars stacked vertically if they overlap.
    將區間畫成水平條，若重疊則垂直堆疊。
-   Use a specific variable name like `curr_end` to show you are tracking the boundary.
    使用特定的變數名稱如 `curr_end` 來顯示你正在追蹤邊界。

### Common Follow-ups (常見追問)
-   **Q:** What if the intervals are too large to fit in memory (Stream)?
    **問：** 如果區間太大無法放入記憶體（串流）怎麼辦？
    **A:** Use a Segment Tree or a Balanced BST (like `SortedDict` in Python/Java `TreeMap`) to store disjoint intervals dynamically.
    **答：** 使用線段樹或平衡二元搜尋樹（如 Python 的 `SortedDict` / Java 的 `TreeMap`）來動態儲存不相交的區間。

---

## 7. Practice Problems (練習題)

### Easy: Insert Interval
**Task:** Insert a new interval into a sorted non-overlapping list and merge if necessary.
**任務：** 將一個新區間插入已排序且不重疊的列表中，必要時進行合併。
*Hint:* Three stages: Add all before `newInterval`, merge overlapping with `newInterval`, add all after.
*提示：* 三階段：加入 `newInterval` 之前的所有區間，合併與 `newInterval` 重疊的區間，加入之後的所有區間。

### Medium: Non-overlapping Intervals
**Task:** Find the minimum number of intervals to remove to make the rest non-overlapping.
**任務：** 找出需要移除的最少區間數量，使剩餘區間不重疊。
*Hint:* Greedy approach. Sort by **end time**. Always pick the interval that ends earliest to leave space for the next one.
*提示：* 貪婪法。依 **結束時間** 排序。總是選擇最早結束的區間，以便為下一個區間留出空間。

### Hard: Data Stream as Disjoint Intervals
**Task:** Design a class that adds integers to a stream and returns disjoint intervals (e.g., add 1, 3, 7, 2 -> `[1,3], [7,7]`).
**任務：** 設計一個類別，將整數加入串流並返回不相交的區間（例如：加入 1, 3, 7, 2 -> `[1,3], [7,7]`）。
*Hint:* This is a design problem. Using a simple list + sort is $O(N \log N)$ per add. Optimal is using a BST (TreeMap) to find the nearest lower/higher intervals in $O(\log N)$.
*提示：* 這是設計題。使用簡單列表 + 排序每次加入需 $O(N \log N)$。最佳解是使用 BST（TreeMap）在 $O(\log N)$ 內找到最近的較低/較高區間。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
-   [ ] Did I handle `intervals = []`? (處理空列表了嗎？)
-   [ ] Did I sort the input? (輸入排序了嗎？)
-   [ ] Am I using `max(prev_end, curr_end)` for merging? (合併時是否使用了 `max`？)
-   [ ] Did I confuse index `i` with the interval values? (是否混淆了索引 `i` 與區間數值？)

### Complexity Check (複雜度確認)
-   [ ] Sorting dominates: $O(N \log N)$.
    排序佔主導：$O(N \log N)$。
-   [ ] One pass scan: $O(N)$.
    一次掃描：$O(N)$。
-   [ ] Total: $O(N \log N)$.
    總計：$O(N \log N)$。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### "The Zipper" (拉鍊)
Merging intervals is like closing a zipper. You pull the slider (iteration) up; if teeth (intervals) are close enough (overlap), they join into one continuous track.
合併區間就像拉上拉鍊。你將拉頭（遍歷）向上拉；如果齒（區間）夠近（重疊），它們就會結合成一條連續的軌道。

### "The Bus Passengers" (公車乘客 - for Sweep Line)
Imagine a bus.
-   Start time = Passenger gets ON (+1).
-   End time = Passenger gets OFF (-1).
-   Max capacity needed = Max number of people on the bus at any time.
想像一輛公車。
-   開始時間 = 乘客上車 (+1)。
-   結束時間 = 乘客下車 (-1)。
-   所需最大容量 = 任何時間點車上的最大人數。