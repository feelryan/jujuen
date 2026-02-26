# Advanced Intervals: Patterns & Interview Strategy
# 進階區間問題：模式與面試策略

## 1. Learning Objectives (學習目標)

1.  **Master the "Sweep Line" Algorithm:** Move beyond simple sorting; understand how to process events chronologically to solve complex overlap and resource scheduling problems.
    **掌握「掃描線」演算法：** 超越單純的排序；理解如何按時間順序處理事件，以解決複雜的重疊與資源調度問題。
2.  **Optimize for Space & Streams:** Learn how to handle intervals when data comes in a stream or when memory is constrained (avoiding $O(N)$ space when possible).
    **優化空間與串流數據：** 學習如何在資料流（Stream）或記憶體受限的情況下處理區間（盡可能避免 $O(N)$ 空間）。
3.  **Disambiguate Edge Cases:** Develop a reflex for handling inclusive vs. exclusive boundaries ($[a, b]$ vs $[a, b)$) and adjacent intervals.
    **釐清邊界情況：** 培養處理包含與互斥邊界（$[a, b]$ 對比 $[a, b)$）以及相鄰區間的直覺反射。
4.  **Differentiate Greedy vs. DP:** Recognize when a greedy approach (sorting by end time) works versus when Dynamic Programming is required (weighted intervals).
    **區分貪婪與動態規劃：** 辨識何時貪婪策略（按結束時間排序）有效，何時需要動態規劃（加權區間）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
An interval represents a range of values, typically defined by a start point and an end point.
區間代表數值的範圍，通常由起點與終點定義。

### Intuition (直覺)
Think of intervals as events on a calendar or segments on a 1D number line. The core challenge usually involves determining relationships: overlapping, merging, or finding gaps.
將區間想像成行事曆上的事件或一維數線上的線段。核心挑戰通常涉及判定關係：重疊、合併或尋找空隙。

### Complexity (複雜度)
-   **Time:** Most interval problems require sorting, leading to a baseline of $O(N \log N)$. Once sorted, processing is usually $O(N)$.
    **時間：** 大多數區間問題需要排序，導致基準為 $O(N \log N)$。排序後，處理通常是 $O(N)$。
-   **Space:** $O(1)$ or $O(N)$ depending on whether we create a new list of intervals or modify in-place.
    **空間：** $O(1)$ 或 $O(N)$，取決於我們是建立新的區間列表還是在原地修改。

### When to Use / Not Use (適用與不適用場景)
-   **Use when:** Resource allocation (CPU scheduling, meeting rooms), merging data ranges, finding intersections.
    **適用於：** 資源分配（CPU 排程、會議室）、合併資料範圍、尋找交集。
-   **Not Use when:** The problem involves 2D/3D spatial overlaps where Quad-Trees or R-Trees are more appropriate (though Sweep Line can extend to 2D).
    **不適用於：** 涉及 2D/3D 空間重疊的問題，此時四元樹（Quad-Trees）或 R-Trees 更合適（儘管掃描線可擴展至 2D）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Sorting & Merging (排序與合併)
Sort by start time. Iterate through and merge if `current.start <= previous.end`.
按開始時間排序。遍歷並合併，如果 `current.start <= previous.end`。

### B. Sweep Line / Chronological Ordering (掃描線 / 時序排列)
Decompose intervals into points: `(time, +1)` for start and `(time, -1)` for end. Sort points and iterate to track active intervals count.
將區間分解為點：起點為 `(time, +1)`，終點為 `(time, -1)`。排序這些點並遍歷以追蹤活躍區間的數量。

### C. Two Pointers (雙指針)
Used when comparing two lists of intervals (e.g., finding intersections). Move the pointer of the interval that ends earlier.
用於比較兩個區間列表時（例如，尋找交集）。移動結束時間較早的那個區間的指針。

### D. Heap / Priority Queue (堆積 / 優先佇列)
Maintain a Min-Heap of end times for active intervals. Useful for finding the minimum resources needed (e.g., Meeting Rooms II).
維護活躍區間結束時間的最小堆積（Min-Heap）。對於尋找所需最小資源（如會議室 II）非常有用。

---

## 4. Example Walkthrough (範例講解)

### Problem: Minimum Meeting Rooms (Meeting Rooms II)
**問題：最少會議室數量（會議室 II）**

**Problem Statement:**
Given an array of meeting time intervals `intervals` where `intervals[i] = [start_i, end_i]`, return the minimum number of conference rooms required.
給定一個會議時間區間陣列 `intervals`，其中 `intervals[i] = [start_i, end_i]`，回傳所需的最少會議室數量。

### Approach Evolution (思路演進)

1.  **Brute Force (暴力法):**
    For every meeting, check overlap with all other meetings. Complexity $O(N^2)$.
    對於每個會議，檢查與所有其他會議的重疊。複雜度 $O(N^2)$。

2.  **Optimization 1: Min-Heap (優化 1：最小堆積):**
    Sort meetings by start time. Use a Min-Heap to store end times of ongoing meetings. If a new meeting starts after the earliest ending meeting (heap top), pop the heap (reuse room). Always push the new meeting's end time.
    按開始時間排序會議。使用最小堆積儲存進行中會議的結束時間。若新會議在最早結束的會議（堆頂）之後開始，彈出堆積（重用房間）。總是將新會議的結束時間推入堆積。
    *Complexity:* $O(N \log N)$. *Space:* $O(N)$.

3.  **Optimization 2: Sweep Line / Two Pointers (優化 2：掃描線 / 雙指針):**
    Separate start and end times into two arrays and sort them independently. Iterate through start times. If a start time is less than the current end time, we need a new room. Otherwise, a room has freed up (increment end pointer).
    將開始和結束時間分開放入兩個陣列並獨立排序。遍歷開始時間。若開始時間小於當前結束時間，我們需要新房間。否則，有一個房間空出來了（增加結束指針）。
    *Complexity:* $O(N \log N)$ (due to sorting). *Space:* $O(N)$ (for arrays). *Note: This is often preferred in TypeScript as JS/TS lacks a built-in Heap.*

### TypeScript Solution (Optimization 2 - Sweep Line)

```typescript
/**
 * Calculates the minimum number of meeting rooms required.
 * 計算所需的最少會議室數量。
 * 
 * Approach: Chronological Ordering (Sweep Line variant)
 * 方法：時序排列（掃描線變體）
 * 
 * Time Complexity: O(N log N) due to sorting.
 * 時間複雜度：O(N log N)，因為需要排序。
 * 
 * Space Complexity: O(N) to store start and end times.
 * 空間複雜度：O(N)，用於儲存開始與結束時間。
 */
function minMeetingRooms(intervals: number[][]): number {
    // Edge case: No intervals
    // 邊界情況：無區間
    if (!intervals || intervals.length === 0) {
        return 0;
    }

    const n = intervals.length;

    // Extract and sort start times
    // 提取並排序開始時間
    const startTimes: number[] = intervals
        .map(interval => interval[0])
        .sort((a, b) => a - b);

    // Extract and sort end times
    // 提取並排序結束時間
    const endTimes: number[] = intervals
        .map(interval => interval[1])
        .sort((a, b) => a - b);

    let startPointer = 0;
    let endPointer = 0;
    let usedRooms = 0;

    // Iterate through all meetings
    // 遍歷所有會議
    while (startPointer < n) {
        // If the current meeting starts strictly before the earliest ending meeting finishes,
        // we need a new room (or increment active count).
        // 如果當前會議在最早結束的會議完成之前就開始，
        // 我們需要一個新房間（或增加活躍計數）。
        if (startTimes[startPointer] < endTimes[endPointer]) {
            usedRooms++;
            startPointer++;
        } else {
            // A meeting ended before or exactly when this one started.
            // Reuse the room (conceptually decrement active count, then increment for new meeting).
            // In this logic, we simply don't increment usedRooms, but move both pointers.
            // 有會議在當前會議開始之前或同時結束。
            // 重用房間（概念上減少活躍計數，然後為新會議增加）。
            // 在此邏輯中，我們僅不增加 usedRooms，而是移動兩個指針。
            startPointer++;
            endPointer++;
        }
    }

    return usedRooms;
}

// Test Case
const intervals = [[0, 30], [5, 10], [15, 20]];
console.log(minMeetingRooms(intervals)); // Output: 2
```

### Why the "Wrong" Approach Fails (錯誤示範)
**Mistake:** Sorting only by start time and checking `intervals[i]` against `intervals[i-1]`.
**錯誤：** 僅按開始時間排序，並將 `intervals[i]` 與 `intervals[i-1]` 進行比較。
**Why:** This only checks overlap with the *immediately preceding* meeting. It fails to account for a meeting that started long ago and is *still* ongoing (e.g., $[0, 100], [10, 20], [30, 40]$). You need to track *all* active meetings, not just the last one.
**原因：** 這只能檢查與*緊鄰前一個*會議的重疊。它無法考慮很久以前開始且*仍在進行*的會議（例如 $[0, 100], [10, 20], [30, 40]$）。你需要追蹤*所有*活躍的會議，而不僅僅是最後一個。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Inclusive vs. Exclusive**<br>包含 vs. 互斥 | Does `[1, 2]` overlap with `[2, 3]`? <br>In "Merge Intervals", usually **yes** ($[1, 3]$). <br>In "Meeting Rooms", usually **no** (meeting ends at 2, next starts at 2). <br>**Always clarify with the interviewer.**<br>`[1, 2]` 與 `[2, 3]` 重疊嗎？<br>在「合併區間」中，通常**是**（變成 $[1, 3]$）。<br>在「會議室」中，通常**否**（會議於 2 結束，下一個於 2 開始）。<br>**務必與面試官確認。** |
| **Modifying Input**<br>修改輸入 | Sorting the input array `intervals.sort(...)` modifies it in-place. <br>In production/interviews, ask if side effects are allowed. If not, `.slice()` or spread `[...intervals]` first.<br>對輸入陣列排序 `intervals.sort(...)` 會原地修改它。<br>在生產環境/面試中，詢問是否允許副作用。如果不允許，先使用 `.slice()` 或展開語法 `[...intervals]`。 |
| **Max Overlap vs. Merge**<br>最大重疊 vs. 合併 | Finding the maximum number of overlapping intervals (Meeting Rooms II) is different from merging them. <br>Merge reduces the count; Max Overlap finds the peak concurrency.<br>尋找最大重疊區間數量（會議室 II）與合併它們不同。<br>合併會減少數量；最大重疊是尋找並發峰值。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Are the intervals sorted? Are the boundaries inclusive or exclusive?"
    **釐清：** 「區間是否已排序？邊界是包含還是互斥的？」
2.  **Visual Analogy:** "I'll visualize this as a timeline. We want to find the point where the 'stack' of intervals is highest."
    **視覺類比：** 「我會將其想像成時間軸。我們要找出區間『堆疊』最高的時間點。」
3.  **Complexity Check:** "Since the input isn't sorted, the lower bound is dominated by sorting, so $O(N \log N)$."
    **複雜度確認：** 「由於輸入未排序，下限受排序主導，因此是 $O(N \log N)$。」

### Whiteboard Strategy (白板策略)
-   Draw a timeline with overlapping bars.
-   Draw vertical dashed lines at start and end points (Sweep Line visualization).
-   畫出帶有重疊條形的時間軸。
-   在起點和終點處畫垂直虛線（掃描線視覺化）。

### Common Follow-ups (常見追問)
-   **Q:** What if the range of numbers is small (e.g., 0 to 1000)?
    **A:** Use Bucket Sort / Counting Array for $O(N)$ or $O(Range)$ time.
    **問：** 如果數字範圍很小（例如 0 到 1000）怎麼辦？
    **答：** 使用桶排序（Bucket Sort）/ 計數陣列，時間複雜度為 $O(N)$ 或 $O(Range)$。
-   **Q:** What if the stream of intervals is infinite?
    **A:** Discuss Interval Trees or Segment Trees.
    **問：** 如果區間流是無限的怎麼辦？
    **答：** 討論區間樹（Interval Trees）或線段樹（Segment Trees）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Merge Intervals (合併區間)
-   **Prompt:** Merge all overlapping intervals.
    **題目：** 合併所有重疊的區間。
-   **Hint:** Sort by start. Iterate. If `curr.start <= last.end`, update `last.end = max(last.end, curr.end)`.
    **提示：** 按開始時間排序。遍歷。若 `curr.start <= last.end`，更新 `last.end = max(last.end, curr.end)`。

### 2. Medium: Interval List Intersections (區間列表交集)
-   **Prompt:** Given two lists of closed intervals, return their intersection.
    **題目：** 給定兩個閉區間列表，回傳它們的交集。
-   **Hint:** Two pointers. `start = max(A.start, B.start)`, `end = min(A.end, B.end)`. If `start <= end`, add to result. Advance the pointer with the smaller `end` value.
    **提示：** 雙指針。`start = max(A.start, B.start)`，`end = min(A.end, B.end)`。若 `start <= end`，加入結果。移動結束值較小的那個指針。

### 3. Hard: Employee Free Time (員工空閒時間)
-   **Prompt:** Given schedules of employees (list of lists), find common free time for all.
    **題目：** 給定員工的行程表（列表的列表），找出所有人的共同空閒時間。
-   **Hint:** Flatten all intervals into one list, sort by start time. Merge them into one big "busy" timeline. The gaps between merged intervals are the "free time".
    **提示：** 將所有區間攤平為一個列表，按開始時間排序。將它們合併成一個大的「忙碌」時間軸。合併區間之間的空隙即為「空閒時間」。

---

## 8. Checklist (快速檢核表)

-   [ ] **Sorted?** Did I sort the input? If not, why? (Most interval problems fail without sorting).
    **已排序？** 我是否對輸入進行了排序？如果沒有，為什麼？（大多數區間問題不排序就會失敗）。
-   [ ] **Empty Input?** Did I handle `[]`?
    **空輸入？** 我是否處理了 `[]`？
-   [ ] **Max Logic:** When merging, did I use `Math.max(prevEnd, currEnd)`? (Don't just assume `currEnd` is larger).
    **最大值邏輯：** 合併時，我是否使用了 `Math.max(prevEnd, currEnd)`？（不要假設 `currEnd` 一定比較大）。
-   [ ] **Loop Invariant:** Am I modifying the array I'm iterating over? (Dangerous).
    **迴圈不變性：** 我是否正在修改我正在遍歷的陣列？（危險）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### "The Zipper" (拉鍊)
For **Interval Intersections**: Imagine two zippers closing. You always move the slider that is lagging behind (the one ending earlier) to catch up.
針對 **區間交集**：想像兩條拉鍊正在拉上。你總是移動落後的那一邊（結束較早的那個）來趕上。

### "The Bus Stop" (公車站)
For **Sweep Line**: Imagine a bus stop.
-   Start time = Passenger gets **on** (+1 person).
-   End time = Passenger gets **off** (-1 person).
-   Max overlap = Max people on the bus at any time.
針對 **掃描線**：想像一個公車站。
-   開始時間 = 乘客**上車**（+1 人）。
-   結束時間 = 乘客**下車**（-1 人）。
-   最大重疊 = 任何時間點車上的最大人數。