# Interview Guide: Intervals (Beginner Depth)
# 面試指南：區間問題（初級深度）

## 1. Learning Objectives (學習目標)

*   **Master the Standard Representation:** Understand how to represent intervals (e.g., arrays, objects) and the physical meaning of `start` and `end`.
    **掌握標準表示法：** 理解如何表示區間（如陣列、物件）以及 `start` 與 `end` 的物理意義。
*   **The Power of Sorting:** Recognize that sorting is almost always the first step in solving interval problems ($O(N \log N)$).
    **排序的力量：** 體認到排序幾乎總是解決區間問題的第一步（$O(N \log N)$）。
*   **Handling Overlaps:** Learn the logic to detect and merge overlapping intervals using a greedy approach.
    **處理重疊：** 學習使用貪婪演算法（Greedy Approach）來偵測並合併重疊區間的邏輯。
*   **Edge Cases Management:** Handle edge cases like touching intervals (`[1,2], [2,3]`) and empty inputs.
    **邊界情況管理：** 處理如相切區間（`[1,2], [2,3]`）與空輸入等邊界情況。

---

## 2. Core Concepts Overview (核心觀念速覽)

| Concept (觀念) | Description (描述) |
| :--- | :--- |
| **Definition (定義)** | An interval represents a continuous range between a start point and an end point. <br> 區間代表起點與終點之間的一個連續範圍。 |
| **Intuition (直覺)** | Think of them as events in a calendar or segments on a 1D number line. <br> 將其視為行事曆中的事件，或是一維數線上的線段。 |
| **Complexity (複雜度)** | **Time:** Usually dominated by sorting: $O(N \log N)$. One pass scan is $O(N)$. <br> **時間：** 通常由排序主導：$O(N \log N)$。單次掃描為 $O(N)$。 <br> **Space:** $O(1)$ or $O(N)$ depending on whether output requires a new array. <br> **空間：** $O(1)$ 或 $O(N)$，取決於輸出是否需要新陣列。 |
| **When to Use (適用場景)** | Scheduling problems, resource allocation, merging time slots. <br> 排程問題、資源分配、合併時段。 |
| **When Not to Use (不適用)** | Data is discrete and has no continuity or range properties. <br> 資料是離散的，且不具備連續性或範圍屬性。 |

---

## 3. Typical Patterns (典型題型 / 模式)

For the "Beginner" level of Intervals, there is really only one dominant pattern: **Sort and Sweep (Greedy)**.
對於「初級」區間問題，實際上只有一個主導模式：**排序後掃描（貪婪法）**。

### Pattern: Sort & Sequential Processing (排序與循序處理)

1.  **Sort:** Sort the intervals based on their **start time**.
    **排序：** 根據區間的 **開始時間** 進行排序。
2.  **Iterate:** Loop through the sorted intervals and compare the `current` interval with the `previous` interval (or the last added interval in the result).
    **迭代：** 遍歷排序後的區間，將 `當前` 區間與 `前一個` 區間（或結果集中最後加入的區間）進行比較。
3.  **Decision:**
    **決策：**
    *   **Overlap:** If `current.start <= previous.end`, they overlap. Merge them (update `previous.end`).
        **重疊：** 若 `current.start <= previous.end`，則重疊。合併它們（更新 `previous.end`）。
    *   **Disjoint:** If `current.start > previous.end`, they do not overlap. Add `current` to the result.
        **不相交：** 若 `current.start > previous.end`，則不重疊。將 `current` 加入結果集。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge Intervals (合併區間)
**LeetCode 56**

#### Problem Statement (問題重述)
Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.
給定一個區間陣列，其中 `intervals[i] = [start_i, end_i]`，合併所有重疊的區間，並返回一個不重疊的區間陣列，該陣列需覆蓋輸入中的所有區間。

#### Approach (思路)

1.  **Brute Force (暴力法):** Compare every interval with every other interval. $O(N^2)$. Not acceptable for Senior roles.
    **暴力法：** 將每個區間與其他所有區間進行比較。$O(N^2)$。對於資深職位來說不可接受。
2.  **Optimized (Sort & Sweep):**
    **優化（排序與掃描）：**
    *   Sort by start time. This ensures that if intervals overlap, they must be adjacent in the sorted list.
        按開始時間排序。這確保了如果區間重疊，它們在排序後的列表中必定是相鄰的。
    *   Create a `result` array and push the first interval.
        建立一個 `result` 陣列並推入第一個區間。
    *   Iterate through the rest. If an overlap is found, extend the `end` of the last interval in `result`. Otherwise, push the new interval.
        遍歷剩餘區間。若發現重疊，延長 `result` 中最後一個區間的 `end`。否則，推入新區間。

#### TypeScript Solution (TypeScript 參考解)

```typescript
/**
 * Merges overlapping intervals.
 * 合併重疊的區間。
 *
 * Time Complexity: O(N log N) - due to sorting.
 * 時間複雜度：O(N log N) - 因為排序。
 * Space Complexity: O(N) - to store the result (or O(log N) for sorting stack).
 * 空間複雜度：O(N) - 用於儲存結果（或 O(log N) 用於排序堆疊）。
 */
function merge(intervals: number[][]): number[][] {
    // 1. Handle edge case: empty input
    // 1. 處理邊界情況：空輸入
    if (intervals.length === 0) return [];

    // 2. Sort intervals by start time (ascending)
    // 2. 依開始時間對區間進行排序（升冪）
    // Note: Creating a copy using slice() avoids modifying the original input (good practice).
    // 注意：使用 slice() 建立副本以避免修改原始輸入（良好習慣）。
    const sortedIntervals = intervals.slice().sort((a, b) => a[0] - b[0]);

    const result: number[][] = [];
    
    // Initialize with the first interval
    // 以第一個區間初始化
    result.push(sortedIntervals[0]);

    for (let i = 1; i < sortedIntervals.length; i++) {
        const current = sortedIntervals[i];
        const lastMerged = result[result.length - 1];

        // 3. Check for overlap
        // 3. 檢查是否重疊
        // If current start time is less than or equal to last merged end time
        // 如果當前的開始時間小於或等於最後合併的結束時間
        if (current[0] <= lastMerged[1]) {
            // Merge: Update the end time to the max of both
            // 合併：將結束時間更新為兩者中的最大值
            lastMerged[1] = Math.max(lastMerged[1], current[1]);
        } else {
            // No overlap: Add current interval to result
            // 無重疊：將當前區間加入結果
            result.push(current);
        }
    }

    return result;
}
```

#### Common Mistake (錯誤示範)

```typescript
// Wrong Logic: Assuming the second interval ends after the first one just because it starts later.
// 錯誤邏輯：僅因為第二個區間開始得較晚，就假設它的結束時間也較晚。
if (current[0] <= lastMerged[1]) {
    lastMerged[1] = current[1]; // WRONG! Example: [1, 10] and [2, 3] -> becomes [1, 3]
    // 錯！範例：[1, 10] 與 [2, 3] -> 會變成 [1, 3]（原本應維持 [1, 10]）
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Strict Inequality (`<`)** | **Non-strict (`<=`)** | In intervals, `[1, 2]` and `[2, 3]` usually merge. Use `<=` to catch touching points. <br> 在區間問題中，`[1, 2]` 與 `[2, 3]` 通常會合併。使用 `<=` 來捕捉相切點。 |
| **Subarray** | **Subsequence** | Intervals problems usually deal with the whole set, but sorting changes the original order (making it a subsequence logic rather than subarray). <br> 區間問題通常處理整個集合，但排序會改變原始順序（使其成為子序列邏輯而非子陣列）。 |
| **Modifying Input** | **New Array** | Modifying `intervals` in-place while iterating is risky (index shifting). Always prefer a `result` stack. <br> 迭代時原地修改 `intervals` 有風險（索引位移）。總是優先使用 `result` 堆疊。 |

---

## 6. Interview Strategy (面試實戰建議)

As a Senior Engineer, you are judged not just on code, but on **requirements gathering** and **systematic thinking**.
身為資深工程師，評估標準不僅是程式碼，還有 **需求收集** 與 **系統性思考**。

1.  **Clarify Input Format (釐清輸入格式):**
    *   "Are the intervals sorted by default?" (Crucial question).
        「區間是否預設已排序？」（關鍵問題）。
    *   "Can intervals have negative numbers or be empty?"
        「區間是否包含負數或為空？」
2.  **Define "Overlap" (定義「重疊」):**
    *   "Does `[1, 2]` and `[2, 3]` count as overlapping?" (Usually yes).
        「`[1, 2]` 和 `[2, 3]` 算重疊嗎？」（通常是）。
3.  **Whiteboard Strategy (白板策略):**
    *   Draw a number line. Visualizing helps you catch the case where one interval completely swallows another (e.g., `[1, 10]` vs `[2, 5]`).
        畫一條數線。視覺化有助於你捕捉一個區間完全吞沒另一個區間的情況（如 `[1, 10]` vs `[2, 5]`）。
4.  **Follow-up (常見追問):**
    *   *Q: What if the intervals are too large to fit in memory (Stream)?*
        *問：如果區間太大無法放入記憶體（串流）怎麼辦？*
    *   *A: Mention processing them in chunks if sorted, or using an Interval Tree / Segment Tree for online queries.*
        *答：若已排序可分塊處理，或使用區間樹 / 線段樹進行線上查詢。*

---

## 7. Practice Problems (練習題)

### 1. Easy: Meeting Rooms (會議室)
**Problem:** Given an array of meeting time intervals, determine if a person can attend all meetings.
**問題：** 給定會議時間區間陣列，判斷一個人是否能參加所有會議。
*   **Hint:** Sort by start time. If `current.start < previous.end`, return false.
    **提示：** 按開始時間排序。若 `current.start < previous.end`，回傳 false。

### 2. Medium: Insert Interval (插入區間)
**Problem:** Given a set of non-overlapping intervals (sorted), insert a new interval and merge if necessary.
**問題：** 給定一組不重疊的區間（已排序），插入一個新區間並在必要時進行合併。
*   **Hint:** Three phases: 1. Add all before new interval. 2. Merge overlapping with new interval. 3. Add all after.
    **提示：** 三階段：1. 加入新區間前的所有區間。2. 合併與新區間重疊的部分。3. 加入剩餘區間。

### 3. Medium/Hard: Non-overlapping Intervals (無重疊區間)
**Problem:** Find the minimum number of intervals to remove to make the rest non-overlapping.
**問題：** 找出需移除的最小區間數量，使剩餘區間互不重疊。
*   **Hint:** Greedy. Sort by **end time**. Always keep the interval that ends earliest to leave space for future intervals.
    **提示：** 貪婪法。按 **結束時間** 排序。總是保留結束最早的區間，以便為未來區間留出空間。

---

## 8. Quick Checklist (快速檢核表)

Use this during your mock interview or self-review.
在模擬面試或自我審查時使用此表。

*   [ ] **Sorted?** Did I sort the input? If not, did I ask if it's sorted?
    **已排序？** 我是否對輸入進行了排序？如果沒有，我是否詢問了它是否已排序？
*   [ ] **Max End:** When merging, did I use `Math.max(prevEnd, currEnd)`? (Don't just take `currEnd`).
    **最大結束時間：** 合併時，我是否使用了 `Math.max(prevEnd, currEnd)`？（不要只取 `currEnd`）。
*   [ ] **Touching:** Did I handle the `==` case correctly (e.g., `end == start`)?
    **相切：** 我是否正確處理了 `==` 的情況（例如 `end == start`）？
*   [ ] **Empty:** Did I handle `[]` input?
    **空值：** 我是否處理了 `[]` 輸入？
*   [ ] **Complexity:** Is my time complexity $O(N \log N)$ or better?
    **複雜度：** 我的時間複雜度是 $O(N \log N)$ 或更好嗎？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **The "Sticky Tape" Analogy (膠帶類比):**
    Imagine laying strips of tape on a table. If a new strip touches or overlaps the previous one, they become one long strip. If there's a gap, it's a separate piece.
    想像在桌上貼膠帶。如果新的一條膠帶接觸或重疊了前一條，它們就變成一條長膠帶。如果有空隙，它就是獨立的一塊。

*   **Visual Anchor (圖像錨點):**
    **Sort First, Then Glue.**
    **先排序，再黏合。**
    (Without sorting, you are trying to glue random pieces of paper scattered all over the room).
    （如果不排序，你就像是在試圖黏合散落在房間各處的隨機紙片）。