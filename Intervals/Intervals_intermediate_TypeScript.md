# Intervals (Intermediate) - Interview Guide
# 區間問題（中階）- 面試指南

## 1. Learning Objectives (學習目標)

1.  **Master the "Sort & Sweep" Pattern:** Understand why sorting is the prerequisite for 90% of interval problems and how to iterate efficiently.
    **掌握「排序與掃描」模式：** 理解為何排序是 90% 區間問題的前置條件，以及如何高效地進行迭代。
2.  **Differentiate Sorting Strategies:** Know when to sort by start time (merging) vs. end time (scheduling/non-overlapping).
    **區分排序策略：** 知道何時該依據開始時間排序（合併類），何時依據結束時間排序（排程/不重疊類）。
3.  **Handle Edge Cases Precision:** Gain confidence in handling touching intervals (e.g., `[1,2], [2,3]`) vs. strictly overlapping ones.
    **精準處理邊界情況：** 建立處理相鄰區間（如 `[1,2], [2,3]`）與嚴格重疊區間的信心。
4.  **Apply the Sweep Line Algorithm:** Learn to decompose intervals into "events" to solve complex load/concurrency problems.
    **應用掃描線演算法：** 學習將區間分解為「事件」，以解決複雜的負載或並發問題。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition (定義)
An interval is a continuous range of values, usually represented as `[start, end]`.
區間是一個連續的數值範圍，通常表示為 `[start, end]`。

### Intuition (直覺)
Think of intervals as events on a calendar or segments on a 1D number line.
將區間想像成行事曆上的事件，或是 1D 數線上的線段。
The core challenge is usually determining the relationship between two intervals: Disjoint, Overlapping, or Contained.
核心挑戰通常在於判斷兩個區間的關係：不相交、重疊或包含。

### Complexity (複雜度)
-   **Time:** Usually **$O(N \log N)$** dominated by sorting. If already sorted, often **$O(N)$**.
    **時間：** 通常為 **$O(N \log N)$**，主要受排序影響。若已排序，通常為 **$O(N)$**。
-   **Space:** **$O(1)$** or **$O(N)$** depending on whether we modify the input in-place or return a new list.
    **空間：** **$O(1)$** 或 **$O(N)$**，取決於我們是原地修改輸入還是返回新列表。

### When to Use (適用場景)
-   Resource scheduling (CPU tasks, meeting rooms).
    資源排程（CPU 任務、會議室）。
-   Merging overlapping data (log entries, time ranges).
    合併重疊數據（日誌條目、時間範圍）。

### When NOT to Use (不適用場景)
-   If the data represents discrete points without continuity, Hash Maps might be better.
    若數據代表沒有連續性的離散點，雜湊表（Hash Maps）可能更好。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting & Merging (排序與合併)
Sort by `start` time. Iterate through the list and maintain a `current` interval, extending its `end` if the next interval overlaps.
依據 `start` 時間排序。迭代列表並維護一個 `current` 區間，若下一個區間重疊則延長其 `end`。

### B. Greedy Scheduling (貪婪排程)
To find the maximum number of non-overlapping intervals, sort by `end` time. This leaves the most room for subsequent intervals.
若要找出最大不重疊區間數量，依據 `end` 時間排序。這能為後續區間留出最大空間。

### C. Sweep Line / Event Processing (掃描線 / 事件處理)
Decompose `[start, end]` into two events: `(start, +1)` and `(end, -1)`. Sort events and iterate to track active intervals (e.g., max concurrent meetings).
將 `[start, end]` 分解為兩個事件：`(start, +1)` 與 `(end, -1)`。排序事件並迭代以追蹤活躍區間（例如：最大同時會議數）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge Intervals (合併區間)
**Problem Statement:** Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.
**問題重述：** 給定一個區間陣列 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間，並返回一個能夠覆蓋輸入中所有區間的不重疊區間陣列。

### Approach (思路)

1.  **Brute Force (暴力法):** Compare every interval with every other interval. Complexity $O(N^2)$. Not acceptable for Senior roles.
    **暴力法：** 將每個區間與其他所有區間進行比較。複雜度 $O(N^2)$。對於資深職位不可接受。
2.  **Optimization (優化):** Sort the intervals by `start` time. This ensures that if interval A overlaps with interval B (where index A < B), A must start before or at the same time as B.
    **優化：** 依據 `start` 時間對區間排序。這保證了若區間 A 與區間 B 重疊（且索引 A < B），A 必定在 B 之前或同時開始。
3.  **Logic (邏輯):**
    -   Initialize `result` with the first interval.
    -   Compare the `current` interval in `result` with the `next` interval in the list.
    -   If `next.start <= current.end`, they overlap. Merge them by updating `current.end = max(current.end, next.end)`.
    -   Otherwise, push `next` into `result`.
    -   初始化 `result` 放入第一個區間。
    -   比較 `result` 中的 `current` 區間與列表中的 `next` 區間。
    -   若 `next.start <= current.end`，則重疊。透過更新 `current.end = max(current.end, next.end)` 來合併它們。
    -   否則，將 `next` 推入 `result`。

### TypeScript Solution (參考解)

```typescript
type Interval = [number, number];

function merge(intervals: Interval[]): Interval[] {
    // Edge case: empty array
    // 邊界情況：空陣列
    if (intervals.length === 0) return [];

    // 1. Sort by start time.
    // Time complexity of sort is O(N log N).
    // 1. 依據開始時間排序。
    // 排序的時間複雜度為 O(N log N)。
    intervals.sort((a, b) => a[0] - b[0]);

    const merged: Interval[] = [];
    
    // Initialize with the first interval
    // 以第一個區間初始化
    let currentInterval = intervals[0];
    merged.push(currentInterval);

    for (let i = 1; i < intervals.length; i++) {
        const [nextStart, nextEnd] = intervals[i];
        const [currentStart, currentEnd] = currentInterval;

        // Check for overlap
        // 檢查是否重疊
        if (nextStart <= currentEnd) {
            // Overlap detected: Merge by updating the end time.
            // Note: We must take the max, because the next interval might be fully inside.
            // 偵測到重疊：透過更新結束時間來合併。
            // 注意：我們必須取最大值，因為下一個區間可能完全在內部。
            currentInterval[1] = Math.max(currentEnd, nextEnd);
        } else {
            // No overlap: Move to the next interval.
            // Update the reference of currentInterval to the new one.
            // 無重疊：移動至下一個區間。
            // 更新 currentInterval 的引用指向新的區間。
            currentInterval = intervals[i];
            merged.push(currentInterval);
        }
    }

    return merged;
}

// Example Usage
// const input: Interval[] = [[1,3],[2,6],[8,10],[15,18]];
// console.log(merge(input)); // Output: [[1,6],[8,10],[15,18]]
```

### Complexity Analysis (複雜度分析)
-   **Time:** $O(N \log N)$ due to sorting. The linear scan is $O(N)$.
    **時間：** $O(N \log N)$，歸因於排序。線性掃描為 $O(N)$。
-   **Space:** $O(N)$ to store the output (or $O(\log N)$ for sorting stack space depending on implementation).
    **空間：** $O(N)$ 用於儲存輸出（或 $O(\log N)$ 用於排序堆疊空間，視實作而定）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Sort Key** | **Start vs. End:** Sorting by `start` is for merging. Sorting by `end` is usually for finding the max number of non-overlapping intervals (Greedy). <br> **Start vs. End:** 依 `start` 排序用於合併。依 `end` 排序通常用於尋找最大不重疊區間數（貪婪法）。 |
| **Overlap Condition** | **Strict vs. Inclusive:** Does `[1,2]` and `[2,3]` overlap? Usually yes for merging (`[1,3]`), but check problem constraints. <br> **嚴格 vs. 包含：** `[1,2]` 和 `[2,3]` 重疊嗎？通常在合併時算重疊（變成 `[1,3]`），但需確認題目限制。 |
| **Sub-intervals** | **Encapsulation:** Don't forget cases like `[1, 10]` and `[2, 5]`. Simply setting `end = next.end` is wrong; use `max(curr.end, next.end)`. <br> **完全包含：** 別忘了像 `[1, 10]` 和 `[2, 5]` 的情況。直接設定 `end = next.end` 是錯的；要用 `max(curr.end, next.end)`。 |
| **In-place Mod** | **Side Effects:** Avoid modifying the input array unless allowed. It creates bugs in production. <br> **副作用：** 除非允許，否則避免修改輸入陣列。這在生產環境會導致 Bug。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Format:** "Are the intervals sorted? Are they integers or floats? Is `[1,2], [2,3]` considered overlapping?"
    **釐清格式：** 「區間已排序嗎？是整數還是浮點數？`[1,2]` 與 `[2,3]` 視為重疊嗎？」
2.  **Visual Confirmation:** "I will visualize this on a timeline. If we sort by start time, we can process them greedily."
    **視覺確認：** 「我會將其視覺化在時間軸上。如果我們依開始時間排序，就可以貪婪地處理它們。」
3.  **Edge Case Callout:** "I'll handle empty inputs and single-interval lists first."
    **標註邊界情況：** 「我會先處理空輸入與單一區間列表的情況。」

### Whiteboard Strategy (白板策略)
-   Draw a horizontal axis.
    畫一條水平軸。
-   Draw intervals as bars stacked vertically if they overlap.
    若區間重疊，將它們畫成垂直堆疊的長條。
-   Use a vertical line (imaginary sweep line) moving from left to right to demonstrate the algorithm.
    使用一條垂直線（想像的掃描線）從左向右移動來演示演算法。

### Common Follow-ups (常見追問)
-   **Q:** What if the intervals are too large to fit in memory (Stream)?
    **問：** 如果區間大到無法放入記憶體（串流）怎麼辦？
    **A:** If sorted, process one by one. If unsorted, we might need a segment tree or map-reduce approach depending on the query.
    **答：** 若已排序，逐一處理。若未排序，視查詢需求可能需要線段樹或 Map-Reduce 方法。
-   **Q:** How to handle intervals with open/closed bounds (e.g., `(1, 5]` vs `[1, 5]`)?
    **問：** 如何處理開/閉區間（如 `(1, 5]` vs `[1, 5]`）？
    **A:** Normalize them (e.g., convert integers `(1, 5]` to `[2, 5]`) or use a custom comparator.
    **答：** 正規化它們（例如將整數 `(1, 5]` 轉為 `[2, 5]`）或使用自定義比較器。

---

## 7. Practice Problems (練習題)

### Easy: Insert Interval (插入區間)
*Given a set of non-overlapping intervals sorted by start time, insert a new interval (merge if necessary).*
*給定一組依開始時間排序的不重疊區間，插入一個新區間（必要時合併）。*
-   **Hint:** Three stages: 1. Add intervals ending before new one. 2. Merge overlapping ones. 3. Add remaining.
-   **提示：** 三階段：1. 加入在新區間前結束的。2. 合併重疊的。3. 加入剩餘的。

### Medium: Non-overlapping Intervals (無重疊區間)
*Find the minimum number of intervals to remove to make the rest non-overlapping.*
*找出需移除的最小區間數量，使剩餘區間不重疊。*
-   **Hint:** Greedy. Sort by **end time**. Always pick the interval that ends earliest to leave space for others.
-   **提示：** 貪婪法。依 **結束時間** 排序。總是選擇最早結束的區間，以留空間給其他區間。

### Hard: Meeting Rooms II (會議室 II)
*Given start and end times, find the minimum number of conference rooms required.*
*給定開始與結束時間，找出所需的最少會議室數量。*
-   **Hint:** Sweep Line approach. Separate into `(start, +1)` and `(end, -1)`. Sort events. Max cumulative sum is the answer. Or use a Min-Heap to track end times of occupied rooms.
-   **提示：** 掃描線法。拆分為 `(start, +1)` 與 `(end, -1)`。排序事件。最大累計和即為答案。或使用 Min-Heap 追蹤被佔用房間的結束時間。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
-   [ ] Did I sort the input? (Unless explicitly stated it's sorted).
    我有排序輸入嗎？（除非明確說明已排序）。
-   [ ] Did I handle the `max` logic for the end time? (`[1,5], [2,4]` -> `[1,5]`).
    我有處理結束時間的 `max` 邏輯嗎？（`[1,5], [2,4]` -> `[1,5]`）。
-   [ ] Is my loop condition correct? (Usually `1` to `length`).
    我的迴圈條件正確嗎？（通常是 `1` 到 `length`）。

### Complexity Check (複雜度確認)
-   [ ] Is it $O(N \log N)$? Can I do $O(N)$? (Only if input is pre-sorted).
    是 $O(N \log N)$ 嗎？能做到 $O(N)$ 嗎？（僅當輸入已預排序時）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Zipper Analogy (拉鍊類比)
Merging intervals is like closing a zipper.
合併區間就像拉上拉鍊。
You align the teeth (sort by start), and as the slider moves up (iteration), connected teeth become one continuous unit (merged interval).
你對齊鏈齒（依開始時間排序），當拉頭向上移動（迭代）時，相連的鏈齒變成一個連續的單元（合併的區間）。

### The Paint Roller (油漆滾筒)
Think of intervals as strokes of paint on a wall.
將區間想像成牆上的油漆筆觸。
-   **Merge:** Where paint overlaps, it becomes one long patch.
    **合併：** 油漆重疊處變成一長塊。
-   **Sweep Line:** Moving a vertical scanner across the wall to count how many layers of paint are at any specific point.
    **掃描線：** 在牆上移動垂直掃描器，計算任一點上有幾層油漆。