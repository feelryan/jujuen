Here is the complete interview preparation guide for **Intervals**, tailored for a Senior Software Engineer, with an **Intermediate** depth level.
這是一份針對 **區間（Intervals）** 的完整面試準備教材，專為資深軟體工程師量身打造，深度設定為 **中階（Intermediate）**。

---

# Interview Guide: Intervals (區間問題)

## 1. Learning Goals (學習目標)

1.  **Master the "Sort & Sweep" Pattern:**
    掌握「排序與掃描」模式：理解為何大多數區間問題都始於根據開始時間（或結束時間）的排序。
    Understand why most interval problems start with sorting by start time (or end time).

2.  **Internalize Overlap Logic:**
    內化重疊邏輯：能夠在不畫圖的情況下，精確寫出判斷兩個區間 $[a, b]$ 與 $[c, d]$ 是否重疊的條件。
    Be able to precisely write the condition to check if two intervals $[a, b]$ and $[c, d]$ overlap without drawing a diagram.

3.  **Differentiate Greedy vs. Heap Approaches:**
    區分貪婪與堆積（Heap）解法：知道何時僅需追蹤「最後結束時間」（Greedy），何時需要維護「所有活動中的結束時間」（Min-Heap）。
    Know when you only need to track the "last end time" (Greedy) versus maintaining "all active end times" (Min-Heap).

4.  **Handle Edge Cases Fluently:**
    流暢處理邊界情況：如區間接觸（$[1,2], [2,3]$）、空區間或單點區間。
    Handle edge cases fluently: such as touching intervals ($[1,2], [2,3]$), empty intervals, or single-point intervals.

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
An interval is a continuous range of values, typically defined by a start point and an end point.
區間是一個連續的數值範圍，通常由一個起點和一個終點定義。

### Intuition (直覺)
Think of intervals as events on a calendar or segments on a 1D number line.
將區間想像成行事曆上的事件，或是 1D 數線上的線段。
The core difficulty usually lies in their relative positioning: disjoint, overlapping, or nested.
核心難點通常在於它們的相對位置：不相交、重疊或包含。

### Complexity (複雜度)
-   **Time:** Dominantly $O(N \log N)$ due to sorting. If input is pre-sorted, often $O(N)$.
    **時間：** 由於排序，通常主導為 $O(N \log N)$。若輸入已排序，通常為 $O(N)$。
-   **Space:** $O(1)$ or $O(N)$ depending on whether we modify the input in-place or return a new list.
    **空間：** 取決於我們是原地修改輸入還是回傳新列表，通常為 $O(1)$ 或 $O(N)$。

### When to Use (適用場景)
-   Resource scheduling (CPU tasks, meeting rooms).
    資源排程（CPU 任務、會議室）。
-   Merging overlapping data (log entries, time ranges).
    合併重疊數據（日誌條目、時間範圍）。

### When NOT to Use (不適用場景)
-   When the data represents discrete, non-continuous points without range semantics (use Hash Maps/Sets).
    當數據代表離散、非連續的點且無範圍語意時（使用 Hash Maps/Sets）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Sort and Merge (排序與合併)
**Strategy:** Sort intervals by start time. Iterate through and merge if `current.start <= previous.end`.
**策略：** 依開始時間排序區間。遍歷並合併，若 `current.start <= previous.end`。
**Use Case:** Merge Intervals, Insert Interval.
**適用：** 合併區間、插入區間。

### Pattern B: Sweep Line / Events (掃描線 / 事件法)
**Strategy:** Decompose each interval into two events: `(start, +1)` and `(end, -1)`. Sort events by time and sweep.
**策略：** 將每個區間分解為兩個事件：`(start, +1)` 與 `(end, -1)`。依時間排序事件並掃描。
**Use Case:** Meeting Rooms II (finding max concurrent intervals), Skyline Problem.
**適用：** 會議室 II（尋找最大同時段數）、天際線問題。

### Pattern C: Two Pointers / Greedy (雙指針 / 貪婪)
**Strategy:** Use two separate sorted arrays (starts and ends) or iterate to find the optimal subset (e.g., max non-overlapping).
**策略：** 使用兩個獨立的排序陣列（開始與結束）或遍歷以尋找最佳子集（例如：最大不重疊數量）。
**Use Case:** Non-overlapping Intervals, Meeting Rooms I.
**適用：** 無重疊區間、會議室 I。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge Intervals (合併區間)
Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals.
給定一個區間陣列 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間。

### Approach (思路)

1.  **Brute Force (暴力法):**
    Compare every interval with every other interval. Treat it as a graph problem (connected components).
    將每個區間與其他所有區間比較。將其視為圖論問題（連通分量）。
    *Complexity:* $O(N^2)$. Too slow.
    *複雜度：* $O(N^2)$。太慢。

2.  **Optimization (Sorting):**
    If we sort by start time, overlapping intervals will be adjacent in the sorted list.
    如果我們依開始時間排序，重疊的區間在排序後的列表中將會相鄰。
    We only need one pass to merge them.
    我們只需要一次遍歷即可合併它們。

### Java Reference Solution (Java 參考解)

```java
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

class Solution {
    public int[][] merge(int[][] intervals) {
        // 1. Handle edge cases
        // 1. 處理邊界情況
        if (intervals.length <= 1) {
            return intervals;
        }

        // 2. Sort by start time
        // 2. 依據開始時間排序
        // Using Integer.compare is safer for potential overflow, though unlikely here.
        // 使用 Integer.compare 對潛在的溢位更安全，雖然在此不太可能發生。
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));

        List<int[]> result = new ArrayList<>();
        
        // Initialize with the first interval
        // 用第一個區間初始化
        int[] currentInterval = intervals[0];
        result.add(currentInterval);

        for (int[] interval : intervals) {
            int currentEnd = currentInterval[1];
            int nextStart = interval[0];
            int nextEnd = interval[1];

            if (nextStart <= currentEnd) {
                // Overlap detected: Merge by updating the end time
                // 偵測到重疊：藉由更新結束時間來合併
                // We must take the max, because the next interval might be fully inside.
                // 我們必須取最大值，因為下一個區間可能完全在內部。
                currentInterval[1] = Math.max(currentEnd, nextEnd);
            } else {
                // No overlap: Move to the next interval
                // 無重疊：移動到下一個區間
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

### Analysis (分析)
-   **Time Complexity:** $O(N \log N)$ due to sorting. The iteration is $O(N)$.
    **時間複雜度：** 由於排序為 $O(N \log N)$。遍歷為 $O(N)$。
-   **Space Complexity:** $O(\log N)$ or $O(N)$ for the sorting stack space (depending on Java's sort implementation variants like Dual-Pivot Quicksort or Timsort).
    **空間複雜度：** $O(\log N)$ 或 $O(N)$ 用於排序的堆疊空間（取決於 Java 的排序實作變體，如 Dual-Pivot Quicksort 或 Timsort）。

### Common Mistake (錯誤示範)
```java
// Mistake: Forgetting to take Math.max for the end time
// 錯誤：忘記對結束時間取 Math.max
if (nextStart <= currentEnd) {
    currentInterval[1] = nextEnd; // WRONG! Example: [1, 5], [2, 4] -> becomes [1, 4] instead of [1, 5]
    // 錯！範例：[1, 5], [2, 4] -> 變成 [1, 4] 而非 [1, 5]
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall (陷阱) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Overlap Condition** (重疊條件) | Checking `start1 < end2 && start2 < end1` vs `start1 <= end2`. | For sorted intervals ($start1 \le start2$), you only need `start2 <= end1`. <br> 對於已排序區間（$start1 \le start2$），僅需 `start2 <= end1`。 |
| **Comparator** (比較器) | `a[0] - b[0]` | Can cause integer overflow if values are large negative/positive. Use `Integer.compare(a[0], b[0])`. <br> 若數值為極大正負數可能導致溢位。請用 `Integer.compare`。 |
| **Interval Types** (區間類型) | Confusing `(a, b)` vs `[a, b]`. | Clarify if boundaries are inclusive. Usually, `[1,2]` and `[2,3]` merge in LeetCode problems. <br> 確認邊界是否包含。通常在 LeetCode 中，`[1,2]` 與 `[2,3]` 會合併。 |
| **In-place Modification** (原地修改) | Removing elements from a list while iterating. | Use a separate result list or a `write_index` pattern to avoid `ConcurrentModificationException`. <br> 使用獨立的結果列表或 `write_index` 模式以避免並發修改異常。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Sort Order:** "Since the input isn't guaranteed to be sorted, my first step is to sort by start time to linearize the processing."
    **確認排序：**「由於輸入不保證已排序，我的第一步是依開始時間排序，以便線性化處理。」
2.  **Define Overlap:** "I will define two intervals as overlapping if the start of the current interval is less than or equal to the end of the previous one."
    **定義重疊：**「我將定義若當前區間的開始時間小於或等於前一個區間的結束時間，則視為重疊。」
3.  **Propose Data Structure:** "I'll use a dynamic list (ArrayList) to build the result set since we don't know the final number of merged intervals."
    **提出資料結構：**「我會使用動態列表（ArrayList）來建立結果集，因為我們不知道最終合併後的區間數量。」

### Whiteboard Strategy (白板策略)
-   **Draw a Number Line:** Visually represent `[1, 3]` and `[2, 6]`.
    **畫出數線：** 視覺化呈現 `[1, 3]` 與 `[2, 6]`。
-   **Trace Variables:** Keep a table on the side tracking `currentStart`, `currentEnd`, and `resultList`.
    **追蹤變數：** 在旁邊列出表格追蹤 `currentStart`、`currentEnd` 與 `resultList`。

### Common Follow-ups (常見追問)
-   **Q:** What if the intervals are too large to fit in memory (Stream)?
    **問：** 如果區間大到無法放入記憶體（串流）怎麼辦？
    **A:** "If sorted, we process one by one. If unsorted, we might need an Interval Tree or store chunks on disk (External Sort)."
    **答：**「若已排序，逐一處理。若未排序，可能需要區間樹或將區塊存於磁碟（外部排序）。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Meeting Rooms (會議室)
**Problem:** Can a person attend all meetings? (Determine if any overlap).
**問題：** 一個人能否參加所有會議？（判斷是否有任何重疊）。
**Hint:** Sort and check if `intervals[i][0] < intervals[i-1][1]`.
**提示：** 排序並檢查 `intervals[i][0] < intervals[i-1][1]`。

### 2. Medium: Non-overlapping Intervals (無重疊區間)
**Problem:** Minimum number of intervals to remove to make the rest non-overlapping.
**問題：** 移除最少數量的區間，使剩餘區間互不重疊。
**Hint:** Greedy approach. Sort by **end time**. If overlap, discard the one that ends later to leave space for future intervals.
**提示：** 貪婪法。依 **結束時間** 排序。若重疊，捨棄結束較晚的那個，以便為後續區間留出空間。

### 3. Hard (Upper Medium): Meeting Rooms II (會議室 II)
**Problem:** Minimum number of conference rooms required.
**問題：** 所需的最少會議室數量。
**Hint:**
-   **Method 1 (Min-Heap):** Sort by start time. Use a Min-Heap to store end times of active meetings. If `current.start >= heap.peek()`, pop (room released). Always push current end time. Heap size is the answer.
    **方法 1 (Min-Heap)：** 依開始時間排序。使用 Min-Heap 儲存進行中會議的結束時間。若 `current.start >= heap.peek()`，彈出（釋放房間）。永遠推入當前結束時間。Heap 大小即為答案。
-   **Method 2 (Sweep Line):** Separate starts and ends into two arrays, sort both. Iterate with two pointers.
    **方法 2 (掃描線)：** 將開始與結束時間分至兩個陣列，皆排序。使用雙指針遍歷。

---

## 8. Rapid Checklist (快速檢核表)

-   [ ] **Did I sort the input?** (Most interval problems fail without this).
    **我有排序輸入嗎？**（大多數區間問題沒有這步都會失敗）。
-   [ ] **Did I handle `start == end`?** (Is `[1,2]` and `[2,3]` an overlap?).
    **我有處理 `start == end` 嗎？**（`[1,2]` 和 `[2,3]` 算重疊嗎？）。
-   [ ] **Did I use `Math.max` for merging?** (Don't just take the second interval's end).
    **我在合併時有使用 `Math.max` 嗎？**（不要只取第二個區間的結束時間）。
-   [ ] **Is the return type correct?** (List vs Array conversion in Java).
    **回傳型別正確嗎？**（Java 中 List 對 Array 的轉換）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Zipper" Analogy (拉鍊類比)
Merging intervals is like closing a zipper.
合併區間就像拉上拉鍊。
You sort the teeth (intervals) and run the slider (iterator) up. If teeth overlap/interlock, they become one continuous closed section.
你排列齒（區間）並向上滑動拉頭（迭代器）。如果齒重疊/互鎖，它們就變成一個連續的閉合部分。

### The "Bus Passenger" Analogy (Sweep Line) (公車乘客類比——掃描線)
For "Meeting Rooms II" or concurrent intervals:
對於「會議室 II」或同時段區間：
-   Start time = Passenger gets ON (+1 person).
    開始時間 = 乘客上車（+1 人）。
-   End time = Passenger gets OFF (-1 person).
    結束時間 = 乘客下車（-1 人）。
-   Max capacity needed = Max people on the bus at any time.
    所需最大容量 = 任何時間點公車上的最大人數。