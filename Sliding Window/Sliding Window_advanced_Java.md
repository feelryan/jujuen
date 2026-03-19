Here is the comprehensive guide for **Sliding Window** at an **Advanced** level, tailored for a Senior Software Engineer, with Java code examples.

這是一份針對 **Sliding Window（滑動視窗）** 的 **進階（Advanced）** 完整教材，專為資深軟體工程師量身打造，並附帶 Java 程式碼範例。

---

# Advanced Sliding Window: Interview & Practical Guide
# 進階滑動視窗：面試與實戰指南

## 1. Learning Objectives（學習目標）

*   **Master the "At Most K" Pattern:** Learn to transform "Exactly K" problems into "At Most K" to reduce complexity.
    **掌握「至多 K 個」模式：** 學習將「恰好 K 個」的問題轉化為「至多 K 個」以降低複雜度。
*   **Integrate Auxiliary Data Structures:** Combine Sliding Window with Monotonic Deques or TreeMaps to handle constraints beyond simple sums (e.g., Min/Max in window).
    **整合輔助資料結構：** 結合滑動視窗與單調雙端隊列（Monotonic Deque）或 TreeMap，以處理簡單總和以外的限制（例如視窗內的最大/最小值）。
*   **Optimize for Amortized Complexity:** Prove $O(N)$ complexity even when inner loops exist, distinguishing it from $O(N^2)$.
    **優化均攤複雜度：** 即使存在內部迴圈，也能證明 $O(N)$ 的複雜度，並將其與 $O(N^2)$ 區分開來。
*   **Handle Dynamic Window Invariants:** Manage complex validity conditions involving frequency maps or distinct character counts efficiently.
    **處理動態視窗不變性：** 高效管理涉及頻率表或相異字元計數的複雜有效性條件。

---

## 2. Core Concepts Snapshot（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Sliding Window is an optimization technique used primarily on arrays or strings to convert nested loops into a single pass.
滑動視窗是一種主要用於陣列或字串的優化技巧，將巢狀迴圈轉化為單次遍歷。

Imagine a flexible frame (like an accordion) expanding to find a valid state and shrinking to optimize it.
想像一個可伸縮的框架（像手風琴），透過擴張來尋找有效狀態，並透過收縮來優化它。

### Complexity（複雜度）
*   **Time:** Typically $O(N)$. Although there is a `while` loop inside the `for` loop, each element is added and removed at most once.
    **時間：** 通常為 $O(N)$。雖然 `for` 迴圈內有一個 `while` 迴圈，但每個元素最多被加入和移除各一次。
*   **Space:** $O(1)$ for pointers, or $O(K)$/$O(\Sigma)$ if using a Hash Map/Set for the window content.
    **空間：** 指標為 $O(1)$，若使用 Hash Map/Set 儲存視窗內容則為 $O(K)$ 或 $O(\Sigma)$。

### When to Use (Scenarios)（適用場景）
1.  **Contiguous Subarrays/Substrings:** Finding the longest, shortest, or number of subarrays satisfying a condition.
    **連續子陣列/子字串：** 尋找滿足特定條件的最長、最短或子陣列數量。
2.  **Sequential Data Processing:** Streaming data where you only care about the recent $K$ elements.
    **序列資料處理：** 串流資料中，你只關心最近 $K$ 個元素的情況。

### When NOT to Use（不適用場景）
1.  **Non-contiguous Subsequences:** If elements can be skipped (e.g., Longest Increasing Subsequence), use Dynamic Programming.
    **非連續子序列：** 如果元素可以被跳過（例如最長遞增子序列），請使用動態規劃。
2.  **Negative Numbers (sometimes):** If the array contains negative numbers, expanding the window doesn't guarantee the sum increases, breaking the monotonicity required for some standard logic (requires Prefix Sum + HashMap instead).
    **負數（有時）：** 如果陣列包含負數，擴張視窗不能保證總和增加，這會破壞某些標準邏輯所需的單調性（此時需改用前綴和 + HashMap）。

---

## 3. Typical Patterns（典型題型 / 模式）

For a Senior Engineer, we skip the basic fixed window and focus on advanced patterns.
對於資深工程師，我們跳過基礎的固定視窗，專注於進階模式。

### A. Dynamic Window (Shrinkable)
**Pattern:** Expand `right` to satisfy condition; shrink `left` to optimize (min length) or restore validity.
**模式：** 擴張 `right` 以滿足條件；收縮 `left` 以優化（最小長度）或恢復有效性。

### B. Sliding Window + Monotonic Queue (Advanced)
**Pattern:** Finding the max/min in a sliding window in $O(N)$ time.
**模式：** 在 $O(N)$ 時間內尋找滑動視窗內的最大/最小值。
**Key:** Use a `Deque` to store indices, maintaining elements in decreasing (or increasing) order.
**關鍵：** 使用 `Deque` 儲存索引，並保持元素處於遞減（或遞增）順序。

### C. The "Exactly K" Transformation
**Pattern:** Counting subarrays with *exactly* K distinct integers.
**模式：** 計算具有 *恰好* K 個相異整數的子陣列數量。
**Formula:** $Exactly(K) = AtMost(K) - AtMost(K-1)$.
**公式：** $Exactly(K) = AtMost(K) - AtMost(K-1)$。
**Why:** Implementing "at most K" is easier (just expand and count) than "exactly K".
**原因：** 實作「至多 K 個」比「恰好 K 個」容易（只需擴張並計數）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Sliding Window Maximum (LeetCode 239)
**Level:** Hard (Advanced)

#### Problem Statement（問題重述）
You are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. You can only see the `k` numbers in the window. Each time the sliding window moves right by one position. Return the max sliding window.
給你一個整數陣列 `nums`，有一個大小為 `k` 的滑動視窗從陣列的最左側移動到最右側。你只能看到視窗內的 `k` 個數字。滑動視窗每次向右移動一個位置。回傳每個視窗內的最大值。

#### Approach & Evolution（思路演進）

1.  **Brute Force (暴力解):**
    *   Iterate through all windows, scan $K$ elements to find max.
    *   遍歷所有視窗，掃描 $K$ 個元素尋找最大值。
    *   Complexity: $O(N \cdot K)$. Too slow if $K$ is large.
    *   複雜度：$O(N \cdot K)$。若 $K$ 很大則太慢。

2.  **Heap / PriorityQueue (堆疊優化):**
    *   Maintain a Max Heap of size $K$.
    *   維護一個大小為 $K$ 的最大堆疊。
    *   Add element: $O(\log K)$. Remove old element: $O(K)$ (in Java PQ) or $O(\log K)$ with lazy removal.
    *   加入元素：$O(\log K)$。移除舊元素：$O(K)$（Java PQ）或 $O(\log K)$（延遲移除）。
    *   Total: $O(N \log K)$. Acceptable, but not optimal.
    *   總計：$O(N \log K)$。可接受，但非最佳。

3.  **Monotonic Deque (Optimal - 最佳解):**
    *   We need the max. If we have `[1, 5]`, the `1` is useless because `5` is larger and newer.
    *   我們需要最大值。如果我們有 `[1, 5]`，`1` 是沒用的，因為 `5` 更大且更新。
    *   Maintain a Deque of **indices** where values are strictly decreasing.
    *   維護一個儲存 **索引** 的雙端隊列（Deque），其對應數值嚴格遞減。
    *   The front of the Deque is always the max of the current window.
    *   Deque 的前端永遠是當前視窗的最大值。
    *   Complexity: $O(N)$.
    *   複雜度：$O(N)$。

#### Java Solution (Bilingual Comments)

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        if (nums == null || k <= 0) return new int[0];
        
        int n = nums.length;
        int[] result = new int[n - k + 1];
        int ri = 0; // Index for result array / 結果陣列的索引
        
        // Deque stores indices of potential max candidates
        // Deque 儲存潛在最大值候選人的索引
        Deque<Integer> deque = new ArrayDeque<>();
        
        for (int i = 0; i < n; i++) {
            // 1. Remove indices that are out of the current window from the front
            // 1. 從前端移除已經超出當前視窗範圍的索引
            // Current window is [i - k + 1, i]
            while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
                deque.pollFirst();
            }
            
            // 2. Maintain monotonicity: remove elements smaller than current from the back
            //    Because they can never be the maximum if the current element exists
            // 2. 維護單調性：從後端移除比當前元素小的元素
            //    因為只要當前元素存在，它們就不可能是最大值
            while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
                deque.pollLast();
            }
            
            // 3. Add current index
            // 3. 加入當前索引
            deque.offerLast(i);
            
            // 4. Record result if the first window is fully formed
            // 4. 若第一個視窗已形成，則記錄結果
            if (i >= k - 1) {
                // The front is always the max index
                // 前端永遠是最大值的索引
                result[ri++] = nums[deque.peekFirst()];
            }
        }
        
        return result;
    }
}
```

#### Complexity Analysis（複雜度分析）
*   **Time:** $O(N)$. Each element is added to the Deque once and removed at most once.
    **時間：** $O(N)$。每個元素被加入 Deque 一次，且最多被移除一次。
*   **Space:** $O(K)$. The Deque stores at most $K$ indices (in the worst case of descending sorted array).
    **空間：** $O(K)$。Deque 最多儲存 $K$ 個索引（在陣列為遞減排序的最差情況下）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Pitfall (錯誤/陷阱) | Correct Approach (正確做法) |
| :--- | :--- | :--- |
| **Window Size** | Using `right - left` as size. <br> 誤用 `right - left` 作為大小。 | Size is `right - left + 1` (inclusive). <br> 大小應為 `right - left + 1`（包含邊界）。 |
| **Shrink Logic** | Using `if` to shrink window. <br> 使用 `if` 來收縮視窗。 | Use `while` loop (e.g., `while (sum > target)`). <br> 使用 `while` 迴圈（例如 `while (sum > target)`）。 |
| **Deque Content** | Storing **values** in Deque. <br> 在 Deque 中儲存 **數值**。 | Store **indices** to validate window range easily. <br> 儲存 **索引** 以便輕鬆驗證視窗範圍。 |
| **Result Update** | Updating result only after shrinking. <br> 僅在收縮後更新結果。 | Depends on goal: Max length -> update after expand; Min length -> update after shrink. <br> 視目標而定：求最大長度 -> 擴張後更新；求最小長度 -> 收縮後更新。 |

---

## 6. Interview Battle Strategy（面試實戰建議）

### Narration Framework（口條框架）
1.  **Define Invariants:** "I will use a sliding window defined by `[left, right]`. The invariant is that the window usually contains valid elements..."
    **定義不變性：** 「我將使用由 `[left, right]` 定義的滑動視窗。其不變性在於視窗內通常包含有效元素……」
2.  **Explain Movement:** "I will expand `right` to include new elements, and shrink `left` when the constraint is violated."
    **解釋移動：** 「我將擴張 `right` 以納入新元素，並在違反限制時收縮 `left`。」
3.  **Discuss Trade-offs:** "A Heap would give $O(N \log K)$, but since we need strict linear time, a Monotonic Deque is better."
    **討論權衡：** 「使用 Heap 會導致 $O(N \log K)$，但因為我們需要嚴格的線性時間，單調 Deque 會更好。」

### Whiteboard Strategy（白板策略）
*   Draw the array and brackets `[` `]` representing the window.
    畫出陣列以及代表視窗的括號 `[` `]`。
*   Trace one iteration: Move `]`, update state, check condition, move `[`.
    追蹤一次迭代：移動 `]`，更新狀態，檢查條件，移動 `[`。

### Common Follow-ups（常見追問）
*   **Q:** What if the stream is infinite?
    **問：** 如果是無限串流怎麼辦？
    *   **A:** We cannot store the whole array. We only store the window buffer.
    *   **答：** 我們不能儲存整個陣列。我們只儲存視窗緩衝區。
*   **Q:** What if numbers are negative? (For sum problems)
    **問：** 如果數字是負數怎麼辦？（針對總和問題）
    *   **A:** Sliding window fails. Switch to **Prefix Sum + HashMap**.
    *   **答：** 滑動視窗會失效。轉用 **前綴和 + HashMap**。

---

## 7. Practice Problems（練習題）

### 1. Easy (Warm-up): Maximum Average Subarray I
*   **Goal:** Find contiguous subarray of length `k` with max average.
*   **Hint:** Fixed size window. Just subtract `nums[i-k]` and add `nums[i]`.
*   **目標：** 找出長度為 `k` 且平均值最大的連續子陣列。
*   **提示：** 固定大小視窗。只需減去 `nums[i-k]` 並加上 `nums[i]`。

### 2. Medium (Standard): Longest Substring Without Repeating Characters
*   **Goal:** Find max length unique substring.
*   **Hint:** Use a `HashSet` or `int[128]` array. If `s[right]` exists in set, shrink `left` until it's removed.
*   **目標：** 找出不含重複字元的最長子字串。
*   **提示：** 使用 `HashSet` 或 `int[128]` 陣列。若 `s[right]` 已存在集合中，收縮 `left` 直到將其移除。

### 3. Hard (Target): Subarrays with K Different Integers (LeetCode 992)
*   **Goal:** Count subarrays with *exactly* K distinct integers.
*   **Hint:** Use the $Exactly(K) = AtMost(K) - AtMost(K-1)$ trick.
*   **Solution Logic (AtMost):**
    *   Expand `right`, add to frequency map.
    *   While map size > K, shrink `left` and remove from map.
    *   Count += `right - left + 1`.
*   **目標：** 計算具有 *恰好* K 個相異整數的子陣列數量。
*   **提示：** 使用 $Exactly(K) = AtMost(K) - AtMost(K-1)$ 的技巧。
*   **解題邏輯 (AtMost)：**
    *   擴張 `right`，加入頻率表。
    *   當表的大小 > K，收縮 `left` 並從表中移除。
    *   計數 += `right - left + 1`。

---

## 8. Quick Checklists（快速檢核表）

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

- [ ] **Initialization:** Are `left`, `right`, and `result` initialized correctly? (e.g., `result` to 0 or Min/Max value?)
    **初始化：** `left`、`right` 和 `result` 是否正確初始化？（例如 `result` 設為 0 或極大/極小值？）
- [ ] **Loop Condition:** Is the outer loop iterating `right` from 0 to `n-1`?
    **迴圈條件：** 外部迴圈是否將 `right` 從 0 迭代到 `n-1`？
- [ ] **Shrink Condition:** Is the `while` loop condition correct for the problem constraints?
    **收縮條件：** `while` 迴圈的條件是否符合題目限制？
- [ ] **Index Bounds:** When accessing `nums[left]` inside the shrink loop, is `left` guaranteed to be within bounds?
    **索引邊界：** 在收縮迴圈內存取 `nums[left]` 時，是否保證 `left` 在邊界內？
- [ ] **Update Logic:** Are you updating the global result (`maxLen` or `minLen`) at the correct spot (inside/after the while loop)?
    **更新邏輯：** 你是否在正確的位置（while 迴圈內/後）更新全域結果（`maxLen` 或 `minLen`）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The Caterpillar (毛毛蟲):**
    The window moves like a caterpillar. It stretches its head (`right++`) to eat, and pulls its tail (`left++`) when it's full or needs to move.
    視窗移動像一隻毛毛蟲。它伸展頭部（`right++`）進食，並在吃飽或需要移動時拉動尾部（`left++`）。

*   **The Bouncer (保鑣 - Monotonic Queue):**
    In the Monotonic Queue pattern, the new element is a "stronger" bouncer. When it enters, it kicks out everyone weaker than him from the back of the line because they are no longer useful (they can't be the max anymore).
    在單調隊列模式中，新元素是一個「更強壯」的保鑣。當它進入時，它會把隊伍後方比它弱的人踢出去，因為他們不再有用了（他們不再可能是最大值）。