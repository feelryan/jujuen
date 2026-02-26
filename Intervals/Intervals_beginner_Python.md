# Interval Problems: The Foundation (區間問題：基礎篇)

## 1. Learning Objectives (學習目標)

1.  **Master the "Sort by Start Time" Reflex.**
    掌握「依開始時間排序」的直覺反應。
    *Understanding that sorting is the prerequisite for almost all linear scan solutions.*
    理解排序幾乎是所有線性掃描解法的前提。

2.  **Handle Overlap Logic Precisely.**
    精準處理重疊邏輯。
    *Distinguish between strictly overlapping `(b > c)` and touching `(b >= c)`.*
    區分嚴格重疊 `(b > c)` 與接觸 `(b >= c)` 的差異。

3.  **Implement the Merge Pattern.**
    實作合併模式。
    *Learn to merge intervals in-place or into a new list efficiently.*
    學習如何高效地原地或在列表中合併區間。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition (定義)
An interval is a range of values, typically represented as `[start, end]`.
區間是一個數值範圍，通常表示為 `[start, end]`。
In programming problems, it usually represents time durations (meetings) or geometric ranges.
在程式題目中，它通常代表時間長度（會議）或幾何範圍。

### Intuition (直覺)
Think of intervals as blocks on a calendar or segments on a 1D number line.
將區間想像成行事曆上的區塊，或是 1D 數線上的線段。
The core complexity arises from their relative positions: disjoint, overlapping, or containing.
核心複雜度來自於它們的相對位置：不相交、重疊或包含。

### Complexity (複雜度)
-   **Time (時間):** $O(N \log N)$ due to sorting. Once sorted, processing is usually $O(N)$.
    由於排序，時間複雜度為 $O(N \log N)$。一旦排序完成，處理通常為 $O(N)$。
-   **Space (空間):** $O(1)$ or $O(N)$ depending on whether we modify the input or return a new list.
    取決於我們是修改輸入還是返回新列表，空間複雜度為 $O(1)$ 或 $O(N)$。

### When to Use (適用場景)
-   Scheduling problems (e.g., "Can I attend all meetings?").
    排程問題（例如：「我能參加所有會議嗎？」）。
-   Merging continuous ranges (e.g., file chunks, IP ranges).
    合併連續範圍（例如：檔案區塊、IP 範圍）。

### When NOT to Use (不適用場景)
-   When the data is inherently 2D or graphical without a linear projection (requires Quad-trees or R-trees).
    當資料本質上是 2D 或圖形且沒有線性投影時（需要四元樹或 R-trees）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Sorting & Linear Scan (排序與線性掃描)
**Most Common.** Sort intervals by `start` time. Iterate through them and compare the `end` time of the current interval with the `start` time of the next.
**最常見。** 依 `start` 時間排序區間。遍歷它們並比較當前區間的 `end` 時間與下一個區間的 `start` 時間。

### Pattern B: Two Pointers (Starts and Ends) (雙指針：開始與結束)
Separate start and end times into two arrays, sort them independently. Useful for finding maximum concurrent intervals (e.g., minimum meeting rooms).
將開始與結束時間分開存入兩個陣列，獨立排序。適用於尋找最大同時並發區間（例如：最少會議室數量）。

### Pattern C: Greedy (貪婪演算法)
Sort by `end` time. Useful for selecting the maximum number of non-overlapping intervals.
依 `end` 時間排序。適用於選擇最大數量的互不重疊區間。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge Intervals (合併區間)
**LeetCode 56**

#### Problem Statement (問題重述)
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間，並返回一個不重疊的區間陣列，該陣列需覆蓋輸入中的所有區間。

#### Thought Process (思路)

1.  **Brute Force (暴力法):**
    Compare every interval with every other interval. If they overlap, merge them. Repeat until no overlaps exist.
    將每個區間與其他所有區間進行比較。如果重疊，則合併。重複此步驟直到沒有重疊為止。
    *Complexity:* $O(N^2)$ or worse. Not acceptable for Senior level.
    *複雜度：* $O(N^2)$ 或更差。對資深工程師來說不可接受。

2.  **Optimization (優化 - Sorting):**
    If we sort by start time, overlapping intervals will be adjacent in the list.
    如果我們按開始時間排序，重疊的區間在列表中將會相鄰。
    We can iterate through the sorted list once.
    我們可以遍歷排序後的列表一次。

3.  **Logic (邏輯):**
    -   Initialize `merged` list with the first interval.
    -   初始化 `merged` 列表並放入第一個區間。
    -   For each subsequent interval `curr`:
    -   對於隨後的每個區間 `curr`：
        -   If `curr.start` <= `last_merged.end`: Overlap detected. Merge by updating `last_merged.end = max(last_merged.end, curr.end)`.
        -   若 `curr.start` <= `last_merged.end`：檢測到重疊。透過更新 `last_merged.end = max(last_merged.end, curr.end)` 進行合併。
        -   Else: No overlap. Append `curr` to `merged`.
        -   否則：無重疊。將 `curr` 加入 `merged`。

#### Python Solution (Python 參考解)

```python
from typing import List

class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        # Edge case: empty list
        # 邊界情況：空列表
        if not intervals:
            return []

        # 1. Sort by start time. Critical step.
        # 1. 依開始時間排序。關鍵步驟。
        # Time: O(N log N)
        intervals.sort(key=lambda x: x[0])

        merged = []
        
        for interval in intervals:
            # If the list of merged intervals is empty or if the current
            # interval does not overlap with the previous, simply append it.
            # 如果已合併列表為空，或當前區間與前一個區間不重疊，直接加入。
            if not merged or merged[-1][1] < interval[0]:
                merged.append(interval)
            else:
                # Otherwise, there is overlap, so we merge the current and previous
                # intervals.
                # 否則，存在重疊，我們合併當前與前一個區間。
                # Note: We must take the max of the end times.
                # 注意：我們必須取結束時間的最大值。
                merged[-1][1] = max(merged[-1][1], interval[1])

        return merged

# Complexity Analysis (複雜度分析)
# Time: O(N log N) dominated by sorting.
# 時間：O(N log N)，由排序主導。
# Space: O(N) to store the output (or O(log N) for sorting stack depth).
# 空間：O(N) 用於儲存輸出（或 O(log N) 用於排序堆疊深度）。
```

#### Common Mistake (錯誤示範)
```python
# Wrong Logic: Only comparing adjacent elements without a result list
# 錯誤邏輯：僅比較相鄰元素而未使用結果列表
for i in range(1, len(intervals)):
    if intervals[i][0] < intervals[i-1][1]:
        # This modifies input but doesn't handle multi-step merges correctly
        # like [1,4], [2,3], [3,6] -> might miss extending the first one fully
        # 這修改了輸入，但無法正確處理多步合併
        # 例如 [1,4], [2,3], [3,6] -> 可能會錯過完全擴展第一個區間
        pass 
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall (陷阱) | Correction (修正) |
| :--- | :--- | :--- |
| **Sorting Key** | Sorting by `end` time for merge problems. | Always sort by `start` time for merging. Sort by `end` time usually for Greedy/Activity Selection. <br> 合併問題請依 `start` 排序。貪婪/活動選擇問題才依 `end` 排序。 |
| **Overlap Condition** | Using `<` vs `<=`. | Clarify if `[1, 2]` and `[2, 3]` overlap. Usually, they "touch" and are merged. So `end >= start` is an overlap. <br> 確認 `[1, 2]` 與 `[2, 3]` 是否重疊。通常它們「接觸」並需合併。所以 `end >= start` 視為重疊。 |
| **Sub-intervals** | Forgetting that an interval can be completely inside another (e.g., `[1, 10]`, `[2, 3]`). | Use `max(end1, end2)` when merging, don't just take the second one's end. <br> 合併時使用 `max(end1, end2)`，不要只取第二個區間的結束時間。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Input:** "Are the intervals sorted? Can I assume valid input (start <= end)?"
    **釐清輸入：**「區間是否已排序？我可以假設輸入有效（start <= end）嗎？」
2.  **State the Approach:** "Since this is an interval problem, my intuition is to sort them first to process them linearly."
    **陳述方法：**「既然這是區間問題，我的直覺是先排序，以便線性處理。」
3.  **Visual Confirmation:** Draw `[1, 3]` and `[2, 6]` on the whiteboard to define "overlap" visually.
    **視覺確認：** 在白板上畫出 `[1, 3]` 和 `[2, 6]` 以視覺化定義「重疊」。

### Whiteboard Strategy (白板策略)
-   Draw a horizontal axis (Time).
    畫一條水平軸（時間）。
-   Use vertical ticks for Start/End.
    用垂直刻度表示開始/結束。
-   Write the variable names `prev_end` and `curr_start` explicitly under the diagram.
    在圖下方明確寫出變數名稱 `prev_end` 和 `curr_start`。

### Common Follow-ups (常見追問)
-   **Q:** "How to handle this if the stream of intervals is infinite?"
    **問：**「如果區間串流是無限的，該如何處理？」
    **A:** "We might need an Interval Tree or store them in a BST to query/merge dynamically."
    **答：**「我們可能需要區間樹（Interval Tree），或將它們存入二元搜尋樹（BST）以動態查詢/合併。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Meeting Rooms (會議室)
**Problem:** Given intervals, can a person attend all meetings?
**問題：** 給定區間，一個人能否參加所有會議？
*Hint:* Sort by start. Check if `intervals[i][1] > intervals[i+1][0]`.
*提示：* 依開始時間排序。檢查是否 `intervals[i][1] > intervals[i+1][0]`。

### 2. Medium: Insert Interval (插入區間)
**Problem:** Insert a new interval into a sorted list of non-overlapping intervals and merge if necessary.
**問題：** 將一個新區間插入已排序且不重疊的區間列表中，必要時進行合併。
*Hint:* Three phases: Add all before new interval -> Merge overlapping with new interval -> Add all after.
*提示：* 三階段：加入新區間之前的所有區間 -> 合併與新區間重疊的部分 -> 加入之後的所有區間。

### 3. Medium (Harder logic): Non-overlapping Intervals (不重疊區間)
**Problem:** Minimum number of intervals to remove to make the rest non-overlapping.
**問題：** 移除最少數量的區間，使剩餘區間互不重疊。
*Hint:* Greedy approach. Sort by **end time**. Always pick the interval that ends earliest to leave space for future intervals.
*提示：* 貪婪法。依 **結束時間** 排序。總是選擇最早結束的區間，以便為未來區間留出空間。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **Sorting:** Did I sort the input? (Most interval problems require this).
    **排序：** 我是否對輸入進行了排序？（大多數區間問題都需要）。
-   [ ] **Empty Input:** Did I handle `[]`?
    **空輸入：** 我是否處理了 `[]`？
-   [ ] **Max End:** When merging, did I use `max(curr.end, next.end)`?
    **最大結束時間：** 合併時，我是否使用了 `max(curr.end, next.end)`？
-   [ ] **Loop Range:** Did I iterate to `len - 1` if accessing `i+1`?
    **迴圈範圍：** 如果存取 `i+1`，迴圈是否只跑到 `len - 1`？

---

## 9. Memory Anchors (記憶錨點)

### The "Zipper" Analogy (拉鍊類比)
Imagine a zipper merging two tracks.
想像拉鍊合併兩條軌道。
Sorting aligns the teeth. The linear scan is the slider moving up, fusing overlapping teeth into one continuous block.
排序將齒對齊。線性掃描是拉頭向上移動，將重疊的齒融合成一個連續的區塊。

### Mnemonic (口訣)
**"Sort Starts, Max Ends."**
**「排序開始，取最大結束。」**
-   Sort by Start time to align.
    依開始時間排序以對齊。
-   Extend by Max End time to merge.
    透過取最大結束時間來延伸合併。