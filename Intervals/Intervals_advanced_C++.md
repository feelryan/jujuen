Here is the comprehensive guide on **Intervals**, tailored for a Senior Software Engineer, focusing on advanced patterns and C++ implementation.

---

# Advanced Intervals Guide for Senior Engineers
# 資深工程師進階區間（Intervals）指南

**Role:** Principal Software Engineer & Senior Interviewer
**Topic:** Intervals (Advanced)
**Language:** C++ (with Bilingual Comments)

---

## 1. Learning Objectives（學習目標）

1.  **Master the "Sweep Line" Algorithm beyond basic sorting.**
    掌握超越基礎排序的「掃描線演算法」（Sweep Line Algorithm）。
2.  **Differentiate between "Greedy Strategy" and "Dynamic Programming" in interval selection.**
    區分區間選擇問題中的「貪婪策略」與「動態規劃」差異。
3.  **Handle dynamic interval updates using Balanced BST (`std::map`/`std::set`).**
    利用平衡二元搜尋樹（`std::map`/`std::set`）處理動態區間更新。
4.  **Perfect boundary handling (Open vs. Closed intervals).**
    完美處理邊界條件（開區間 vs. 閉區間）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
**Intervals** represent a range of values, typically time or 1D coordinates, denoted as `[start, end]`.
**區間（Intervals）** 代表數值範圍，通常是時間或一維座標，表示為 `[start, end]`。

Intuitively, visualize them as horizontal bars on a timeline. The core challenge usually involves finding overlaps, gaps, or optimal packing.
直觀上，將它們想像成時間軸上的水平長條。核心挑戰通常涉及尋找重疊、空隙或最佳填充。

### Complexity（複雜度）
-   **Time:** Usually **$O(N \log N)$** dominated by sorting. If intervals are already sorted, many problems become **$O(N)$**.
    **時間：** 通常由排序主導，為 **$O(N \log N)$**。若區間已排序，許多問題可降為 **$O(N)$**。
-   **Space:** **$O(N)$** to store results or auxiliary structures (like a heap or event list).
    **空間：** **$O(N)$** 用於儲存結果或輔助結構（如 Heap 或事件列表）。

### When to Use / Not Use（適用與不適用場景）
-   **Use when:** Resource scheduling (CPU, Meeting Rooms), calendar merging, range queries.
    **適用：** 資源排程（CPU、會議室）、行事曆合併、範圍查詢。
-   **Not use when:** The data is multi-dimensional without a clear linear ordering (consider Quad-Trees or R-Trees instead).
    **不適用：** 資料是多維且缺乏清晰線性順序時（此時應考慮四元樹或 R-Tree）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Sort by Start Time (The Standard)
**以開始時間排序（標準做法）**
Most merging/overlapping problems start here. It allows you to process intervals linearly.
大多數合併/重疊問題由此開始。這允許你線性地處理區間。

### B. Sweep Line / Event Processing (Advanced)
**掃描線 / 事件處理（進階）**
Decompose an interval `[s, e]` into two events: `(s, +1)` and `(e, -1)`. Sort events by time. This is powerful for counting "max concurrent" usage.
將區間 `[s, e]` 分解為兩個事件：`(s, +1)` 與 `(e, -1)`。依時間排序事件。這對於計算「最大同時」使用量非常強大。

### C. Two Pointers
**雙指針**
Used when finding intersections between two **sorted** lists of intervals.
用於在兩個**已排序**的區間列表中尋找交集時。

### D. Greedy by End Time
**以結束時間貪婪排序**
Specifically for "Maximum Non-overlapping Intervals" (Activity Selection Problem). Finishing early leaves more room for others.
專用於「最大不重疊區間數」（活動選擇問題）。越早結束，留給其他人的空間越多。

---

## 4. Example Walkthrough（範例講解）

### Problem: Minimum Number of Arrows to Burst Balloons (Advanced Variation)
### 問題：引爆氣球所需的最小箭數（進階變體）

*Note: While this is a classic LeetCode problem, we will analyze it deeply to contrast Greedy vs. Sorting approaches.*
*註：雖然這是經典 LeetCode 題，我們將深入分析以對比貪婪與排序方法。*

**Problem Statement:**
Given an array of points where `points[i] = [x_start, x_end]`, find the minimum number of arrows that must be shot to burst all balloons. An arrow shot at `x` bursts balloons if `x_start <= x <= x_end`.
給定一個點陣列 `points[i] = [x_start, x_end]`，找出引爆所有氣球所需的最小箭數。若箭射在 `x`，且 `x_start <= x <= x_end`，則氣球被引爆。

---

### Approach Analysis（思路分析）

#### 1. Brute Force (Thinking Process)
**暴力法（思考過程）**
Try every possible coordinate? Impossible since coordinates are continuous. Try shooting at every interval's end? $O(N^2)$ or $O(2^N)$ depending on implementation.
嘗試所有可能的座標？不可能，因為座標是連續的。嘗試射擊每個區間的結束點？取決於實作，可能是 $O(N^2)$ 或 $O(2^N)$。

#### 2. Optimization: Sort by Start Time?
**優化：依開始時間排序？**
If we sort by start time, we might shoot an arrow that covers the first balloon but misses a balloon that starts later but ends earlier. It's tricky to decide the optimal shot position.
若依開始時間排序，我們射出的箭可能覆蓋第一個氣球，但錯過了一個開始較晚卻結束較早的氣球。很難決定最佳射擊位置。

#### 3. Optimal: Greedy Sort by End Time
**最佳解：依結束時間貪婪排序**
Sort by `x_end`. Why? The balloon ending earliest **must** be burst. To maximize efficiency, we should shoot exactly at its rightmost edge (`x_end`). This gives us the best chance to burst overlapping balloons starting after it.
依 `x_end` 排序。為什麼？最早結束的氣球**必須**被引爆。為了最大化效率，我們應該正好射在其最右邊緣（`x_end`）。這讓我們最有機會引爆在其之後開始的重疊氣球。

---

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    int findMinArrowShots(vector<vector<int>>& points) {
        // Edge case: empty input
        // 邊界情況：空輸入
        if (points.empty()) return 0;

        // Sort by end coordinate.
        // Using a lambda for custom comparison.
        // 依結束座標排序。使用 lambda 進行自定義比較。
        sort(points.begin(), points.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[1] < b[1];
        });

        int arrows = 1;
        // The position of the current arrow (at the end of the first balloon)
        // 當前箭的位置（位於第一個氣球的末端）
        int currentArrowPos = points[0][1];

        for (size_t i = 1; i < points.size(); ++i) {
            // If the current balloon starts AFTER the arrow position,
            // it means the current arrow cannot hit this balloon.
            // 如果當前氣球的開始位置在箭的位置之後，
            // 代表這支箭無法擊中此氣球。
            if (points[i][0] > currentArrowPos) {
                arrows++;
                // Shoot a new arrow at the end of this new balloon
                // 在這個新氣球的末端射出一支新箭
                currentArrowPos = points[i][1];
            }
            // Else: The balloon is hit by the current arrow, ignore it.
            // 否則：該氣球已被當前箭擊中，忽略它。
        }

        return arrows;
    }
};
```

### Complexity Analysis（複雜度分析）
-   **Time:** $O(N \log N)$ due to `std::sort`. The iteration is $O(N)$.
    **時間：** 因 `std::sort` 為 $O(N \log N)$。遍歷為 $O(N)$。
-   **Space:** $O(\log N)$ or $O(N)$ depending on the sort implementation (stack depth).
    **空間：** 取決於排序實作（堆疊深度），為 $O(\log N)$ 或 $O(N)$。

---

### Advanced Example: Meeting Rooms II (Sweep Line Approach)
### 進階範例：會議室 II（掃描線法）

**Problem:** Given intervals, find the minimum number of conference rooms required.
**問題：** 給定區間，找出所需的最少會議室數量。

**Why Sweep Line?**
While a Min-Heap approach is standard, **Sweep Line** is more generic for "maximum concurrency" problems.
**為何選掃描線？**
雖然 Min-Heap 是標準解法，但**掃描線**對於「最大並發」類問題更具通用性。

```cpp
#include <vector>
#include <algorithm>
#include <map>

using namespace std;

class Solution {
public:
    int minMeetingRooms(vector<vector<int>>& intervals) {
        // Map to store time points and the net change in rooms (+1 or -1)
        // Map 用於儲存時間點與房間的淨變化量（+1 或 -1）
        // Using map keeps keys sorted automatically.
        // 使用 map 會自動將鍵值（時間）排序。
        map<int, int> timeline;

        for (const auto& interval : intervals) {
            timeline[interval[0]]++; // Meeting starts: need a room (+1)
            timeline[interval[1]]--; // Meeting ends: release a room (-1)
        }

        int maxRooms = 0;
        int currentRooms = 0;

        // Iterate through the sorted timeline
        // 遍歷已排序的時間軸
        for (auto const& [time, change] : timeline) {
            currentRooms += change;
            maxRooms = max(maxRooms, currentRooms);
        }

        return maxRooms;
    }
};
```

**Critique of Map approach:**
Using `std::map` is $O(N \log N)$ due to tree insertions. It handles duplicate times naturally.
**Map 方法的評論：**
使用 `std::map` 因樹的插入操作為 $O(N \log N)$。它能自然地處理重複的時間點。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Description & Pitfall |
| :--- | :--- |
| **Strict vs. Non-Strict** | Does `[1, 2]` overlap with `[2, 3]`? <br> **Pitfall:** In "Merge Intervals", yes. In "Meeting Rooms", usually no (meeting ends at 2, next starts at 2). Always clarify. <br> **嚴格 vs. 非嚴格**：`[1, 2]` 與 `[2, 3]` 是否重疊？<br> **陷阱：** 在「合併區間」中，是。在「會議室」中，通常否。務必確認。 |
| **Sorting Criteria** | **Start Time:** For merging, finding gaps. <br> **End Time:** For max non-overlapping count (Greedy). <br> **排序標準**：**開始時間：** 用於合併、找空隙。<br> **結束時間：** 用於最大不重疊數量（貪婪）。 |
| **Modifying Input** | **Pitfall:** Sorting the input reference `vector<vector<int>>&` modifies the caller's data. <br> **Fix:** Ask if in-place modification is allowed, or sort a copy/index array. <br> **修改輸入**：**陷阱：** 排序輸入參考會修改呼叫者的資料。<br> **修正：** 詢問是否允許原地修改，或排序副本/索引陣列。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarification Phase (The "Senior" Touch)
**釐清階段（資深風範）**
-   "Are the intervals sorted?" (Usually no, but asking shows awareness).
    「區間是否已排序？」（通常沒有，但提問顯示警覺性）。
-   "How do we handle boundary overlap? Is `[1,5]` and `[5,6]` overlapping?"
    「如何處理邊界重疊？`[1,5]` 和 `[5,6]` 算重疊嗎？」
-   "Is the time scale discrete (integers) or continuous (floats)?" (Affects Sweep Line logic).
    「時間尺度是離散（整數）還是連續（浮點數）？」（影響掃描線邏輯）。

### 2. Whiteboard Strategy
**白板策略**
-   Draw a timeline. Visually represent the "Sweep Line" as a vertical bar moving left to right.
    畫出時間軸。視覺化地將「掃描線」表現為從左向右移動的垂直線。
-   Define the `struct` or `pair` for events clearly before coding.
    在寫程式碼前，清楚定義事件的 `struct` 或 `pair`。

### 3. Common Follow-ups
**常見追問**
-   **Q:** "What if the range is small (e.g., 0 to 24 hours) but N is huge?"
    **A:** Use Bucket Sort or a fixed-size array (Frequency Array) for $O(N)$ or $O(1)$ sorting.
    **問：**「如果範圍很小（如 0 到 24 小時）但 N 很大？」
    **答：** 使用桶排序或固定大小陣列（頻率陣列）以達到 $O(N)$ 或 $O(1)$ 排序。
-   **Q:** "How to handle a continuous stream of intervals?"
    **A:** Discuss `Interval Tree` or `std::map` (TreeMap) for dynamic queries.
    **問：**「如何處理連續的區間串流？」
    **答：** 討論 `Interval Tree` 或 `std::map` (TreeMap) 用於動態查詢。

---

## 7. Practice Problems（練習題）

### Easy: Merge Intervals
**易：合併區間**
-   **Goal:** Merge overlapping intervals.
-   **Hint:** Sort by start. Iterate and extend `end` if overlap.
-   **目標：** 合併重疊的區間。
-   **提示：** 依開始時間排序。若重疊則遍歷並延伸 `end`。

### Medium: Interval List Intersections
**中：區間列表交集**
-   **Goal:** Find intersection of two sorted lists.
-   **Hint:** Two pointers. Intersection is `[max(start1, start2), min(end1, end2)]`. Move the pointer with the smaller `end`.
-   **目標：** 找出兩個已排序列表的交集。
-   **提示：** 雙指針。交集為 `[max(start1, start2), min(end1, end2)]`。移動 `end` 較小的那個指針。

### Hard: The Skyline Problem
**難：天際線問題**
-   **Goal:** Output the contour of buildings.
-   **Hint:** Classic Sweep Line. Events: `(x, height, type)`. Use a `multiset` (max-heap behavior) to track current active heights.
-   **目標：** 輸出建築物的輪廓。
-   **提示：** 經典掃描線。事件：`(x, height, type)`。使用 `multiset`（最大堆積行為）追蹤當前有效高度。

---

## 8. Quick Checklists（快速檢核表）

-   [ ] **Sorted?** Did I sort the intervals? (Crucial for $O(N \log N)$ logic).
    **已排序？** 我是否排序了區間？（對 $O(N \log N)$ 邏輯至關重要）。
-   [ ] **Empty Input?** Did I handle `intervals.size() == 0`?
    **空輸入？** 我是否處理了 `intervals.size() == 0`？
-   [ ] **Update Logic?** When merging, did I use `max(currentEnd, nextEnd)`?
    **更新邏輯？** 合併時，我是否使用了 `max(currentEnd, nextEnd)`？
-   [ ] **Loop Termination?** In `while` loops (two pointers), did I check `i < N && j < M`?
    **迴圈終止？** 在 `while` 迴圈（雙指針）中，我是否檢查了 `i < N && j < M`？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Zipper (Two Pointers)
**拉鍊（雙指針）**
When finding intersections between two sorted lists, imagine closing a zipper. The teeth must align. You always advance the side that is "lagging behind" (ending earlier).
當尋找兩個已排序列表的交集時，想像拉上拉鍊。齒必須對齊。你總是推進「落後」（較早結束）的那一側。

### The Bus (Sweep Line)
**公車（掃描線）**
Imagine a bus traveling through time.
-   Start of interval = Passenger gets **ON** (+1).
-   End of interval = Passenger gets **OFF** (-1).
-   Max capacity needed = Max passengers on the bus at any instant.
想像一輛穿越時間的公車。
-   區間開始 = 乘客**上車** (+1)。
-   區間結束 = 乘客**下車** (-1)。
-   所需最大容量 = 任何時刻車上的最大乘客人數。