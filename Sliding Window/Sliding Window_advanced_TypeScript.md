# Advanced Sliding Window: From Mechanics to Mastery
# 進階滑動視窗：從機制到精通

## 1. Learning Objectives (學習目標)

*   **Master the "At Most K" Transformation:** Learn how to convert complex "Exactly K" counting problems into two simpler "At Most K" sliding window problems.
    **掌握「至多 K」的轉換技巧：** 學習如何將複雜的「恰好 K」計數問題轉化為兩個較簡單的「至多 K」滑動視窗問題。
*   **Integrate Auxiliary Data Structures:** Go beyond simple counters; combine windows with HashMaps, Deques (Monotonic Queues), or Multisets to handle dynamic constraints.
    **整合輔助資料結構：** 超越單純的計數器；將視窗與雜湊表、雙端佇列（單調佇列）或多重集結合，以處理動態限制。
*   **Optimize for Amortized Complexity:** Deeply understand why nested `while` loops inside a `for` loop remain $O(N)$, and how to articulate this proof during interviews.
    **優化均攤複雜度：** 深入理解為何 `for` 迴圈內嵌 `while` 迴圈仍然是 $O(N)$，並學會如何在面試中闡述此證明。
*   **Handle Streaming Data:** Adapt sliding window logic for scenarios where the input is an infinite stream rather than a fixed array.
    **處理串流數據：** 調整滑動視窗邏輯以適應輸入為無限串流而非固定陣列的場景。

---

## 2. Core Concepts & Intuition (核心觀念速覽)

### Definition (定義)
Sliding Window is an optimization technique used primarily on arrays or strings to convert nested loops into a single linear pass by maintaining a dynamic range `[left, right]` that satisfies specific constraints.
滑動視窗是一種主要用於陣列或字串的優化技術，透過維護一個滿足特定限制的動態範圍 `[left, right]`，將巢狀迴圈轉化為單次線性遍歷。

### Intuition (直覺)
Think of an accordion or a caterpillar: the window expands (right moves) to ingest data, and shrinks (left moves) to maintain validity or minimize size.
想像一個手風琴或毛毛蟲：視窗伸展（右移）以攝取數據，並收縮（左移）以維持有效性或最小化尺寸。

### Complexity (複雜度)
*   **Time:** $O(N)$. Although there is an inner loop to shrink the window, each element is added to the window once and removed once.
    **時間：** $O(N)$。雖然有一個內部迴圈用於收縮視窗，但每個元素只會被加入視窗一次並移除一次。
*   **Space:** $O(1)$ to $O(K)$ or $O(\Sigma)$, depending on the auxiliary structure (e.g., hash map size for distinct characters).
    **空間：** $O(1)$ 到 $O(K)$ 或 $O(\Sigma)$，取決於輔助結構（例如用於存儲相異字元的雜湊表大小）。

### When to Use (適用場景)
*   Finding the **longest/shortest** substring/subarray meeting a criteria.
    尋找符合標準的 **最長/最短** 子字串/子陣列。
*   **Counting** the number of subarrays meeting a criteria (often requires math tricks).
    **計算** 符合標準的子陣列數量（通常需要數學技巧）。
*   Replacing nested loops ($O(N^2)$) with linear scans ($O(N)$).
    用線性掃描 ($O(N)$) 替換巢狀迴圈 ($O(N^2)$)。

### When NOT to Use (不適用場景)
*   When the problem involves non-contiguous elements (consider Dynamic Programming or Backtracking).
    當問題涉及非連續元素時（考慮動態規劃或回溯法）。
*   When the input contains negative numbers AND the constraint is sum-based (monotonicity is broken; consider Prefix Sum + HashMap).
    當輸入包含負數 **且** 限制是基於總和時（單調性被破壞；考慮前綴和 + 雜湊表）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Dynamic Size: Expand & Shrink (動態大小：伸縮模式)
The standard pattern: Expand `right` until invalid, then shrink `left` until valid again.
標準模式：擴展 `right` 直到無效，然後收縮 `left` 直到再次有效。
*   *Use case:* Longest substring without repeating characters.
*   *適用：* 無重複字元的最長子字串。

### B. Fixed Size (固定大小)
Window size `k` is constant. Initialize first `k`, then slide one by one.
視窗大小 `k` 是固定的。初始化前 `k` 個，然後逐一滑動。
*   *Use case:* Maximum sum of subarray of size K.
*   *適用：* 大小為 K 的子陣列最大和。

### C. "At Most K" to "Exactly K" (「至多 K」轉「恰好 K」)
**Advanced Pattern:** Solving for "Exactly K" is hard. Solve `atMost(K) - atMost(K-1)`.
**進階模式：** 直接解「恰好 K」很難。透過計算 `atMost(K) - atMost(K-1)` 來解決。
*   *Use case:* Subarrays with K different integers.
*   *適用：* 具有 K 個不同整數的子陣列。

### D. Monotonic Queue Window (單調佇列視窗)
Using a Deque to maintain max/min candidates within the window in $O(1)$ amortized time.
使用雙端佇列（Deque）在 $O(1)$ 均攤時間內維護視窗內的最大/最小值候選者。
*   *Use case:* Sliding Window Maximum.
*   *適用：* 滑動視窗最大值。

---

## 4. Example Walkthrough (範例講解)

### Problem: Subarrays with K Different Integers (LeetCode 992)
### 問題：具有 K 個不同整數的子陣列

**Problem Statement:**
Given an integer array `nums` and an integer `k`, return the number of **good subarrays** of `nums`. A good subarray is defined as an array where the number of different integers in that array is exactly `k`.
給定一個整數陣列 `nums` 和一個整數 `k`，回傳 `nums` 中 **好子陣列** 的數量。好子陣列定義為該陣列中不同整數的數量恰好為 `k`。

**Approach: Brute Force → Optimization → Optimal**
**思路：暴力 → 優化 → 最佳解**

1.  **Brute Force ($O(N^3)$ or $O(N^2)$):**
    Iterate all subarrays ($O(N^2)$), put elements in a Set, check size ($O(N)$). Too slow.
    遍歷所有子陣列 ($O(N^2)$)，將元素放入 Set，檢查大小 ($O(N)$)。太慢了。

2.  **Failed Sliding Window Attempt:**
    Standard sliding window finds the *longest* or *shortest*. Counting "exactly K" is tricky because valid windows aren't strictly monotonic in a simple way (moving `left` might keep distinct count same or decrease it).
    標準滑動視窗尋找 *最長* 或 *最短*。計算「恰好 K」很棘手，因為有效視窗並非以簡單的方式嚴格單調（移動 `left` 可能保持相異計數不變或減少）。

3.  **Optimal Solution ($O(N)$):**
    Use the property: `Exactly(K) = AtMost(K) - AtMost(K-1)`.
    Function `atMost(K)` counts subarrays with $\le K$ distinct numbers. This is a standard sliding window because if `[left, right]` has $\le K$ distinct, then all subarrays ending at `right` and starting after `left` are also valid.
    利用性質：`Exactly(K) = AtMost(K) - AtMost(K-1)`。
    函數 `atMost(K)` 計算具有 $\le K$ 個不同數字的子陣列。這是一個標準的滑動視窗，因為如果 `[left, right]` 有 $\le K$ 個不同數字，那麼所有以 `right` 結尾且起點在 `left` 之後的子陣列也都是有效的。

**Complexity:**
*   **Time:** $O(N)$. We run the sliding window pass twice.
    **時間：** $O(N)$。我們執行滑動視窗遍歷兩次。
*   **Space:** $O(N)$. Map to store frequency.
    **空間：** $O(N)$。用於存儲頻率的 Map。

**TypeScript Solution:**

```typescript
/**
 * Calculates the number of subarrays with exactly K distinct integers.
 * 計算具有恰好 K 個不同整數的子陣列數量。
 * 
 * Strategy: exactly(K) = atMost(K) - atMost(K-1)
 * 策略：exactly(K) = atMost(K) - atMost(K-1)
 */
function subarraysWithKDistinct(nums: number[], k: number): number {
    return atMostKDistinct(nums, k) - atMostKDistinct(nums, k - 1);
}

/**
 * Helper function: Sliding Window to count subarrays with at most K distinct integers.
 * 輔助函數：滑動視窗計算至多具有 K 個不同整數的子陣列。
 */
function atMostKDistinct(nums: number[], k: number): number {
    let left = 0;
    let count = 0;
    // Map to keep track of frequency of each number in the current window
    // Map 用於追蹤當前視窗中每個數字的頻率
    const freqMap = new Map<number, number>();

    for (let right = 0; right < nums.length; right++) {
        const rightNum = nums[right];
        
        // Add new element to window
        // 將新元素加入視窗
        freqMap.set(rightNum, (freqMap.get(rightNum) || 0) + 1);

        // While distinct count exceeds k, shrink the window from left
        // 當不同整數數量超過 k 時，從左側收縮視窗
        while (freqMap.size > k) {
            const leftNum = nums[left];
            const currentFreq = freqMap.get(leftNum)!;
            
            if (currentFreq === 1) {
                // Remove the key entirely to decrease size of map (distinct count)
                // 完全移除該鍵以減少 Map 的大小（不同整數計數）
                freqMap.delete(leftNum);
            } else {
                freqMap.set(leftNum, currentFreq - 1);
            }
            left++;
        }

        // Key Logic: Number of valid subarrays ending at 'right' is length of window
        // 關鍵邏輯：以 'right' 結尾的有效子陣列數量等於視窗長度
        // Example: Window [1, 2, 1], k=2. Subarrays ending at index 2: [1], [2, 1], [1, 2, 1]
        // 範例：視窗 [1, 2, 1], k=2。以索引 2 結尾的子陣列有：[1], [2, 1], [1, 2, 1]
        count += (right - left + 1);
    }

    return count;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Confusion (陷阱 / 混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Window Shrinking** | Using `if` instead of `while` to shrink. <br> 使用 `if` 而非 `while` 來收縮。 | The window might need to shrink multiple steps to become valid again. <br> 視窗可能需要收縮多步才能再次有效。 |
| **Counting Logic** | Thinking `count++` adds one valid subarray. <br> 認為 `count++` 只增加一個有效子陣列。 | In "At Most" problems, adding a new element creates `right - left + 1` new valid subarrays. <br> 在「至多」問題中，加入一個新元素會產生 `right - left + 1` 個新的有效子陣列。 |
| **Map vs Set** | Using `Set` when frequency matters. <br> 當頻率很重要時使用 `Set`。 | If duplicates are allowed in window but distinct count matters, you need a `Map` to know when to fully remove an item. <br> 如果視窗允許重複但需計算相異數，需用 `Map` 才知道何時完全移除該項目。 |
| **Negative Numbers** | Applying sliding window on `Sum < K` with negative numbers. <br> 在含有負數的情況下對 `Sum < K` 應用滑動視窗。 | Negative numbers break the monotonicity (expanding doesn't always increase sum). Use Prefix Sum. <br> 負數破壞了單調性（擴展不一定增加總和）。應使用前綴和。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This problem asks for a contiguous subarray satisfying a constraint, which suggests a Sliding Window approach."
    **識別：** 「這個問題要求滿足限制的連續子陣列，這暗示了滑動視窗的方法。」
2.  **Define State:** "I will maintain a window `[left, right]` and a HashMap to track the frequency of characters."
    **定義狀態：** 「我將維護一個視窗 `[left, right]` 和一個 HashMap 來追蹤字元的頻率。」
3.  **Explain Logic:** "I'll expand `right` to include elements. If the constraint is violated, I'll increment `left` to shrink the window until it's valid."
    **解釋邏輯：** 「我會擴展 `right` 來包含元素。如果違反限制，我會增加 `left` 來收縮視窗直到它有效。」
4.  **Complexity:** "Since `left` and `right` each visit every element at most once, the time complexity is $O(N)$."
    **複雜度：** 「由於 `left` 和 `right` 每個元素最多訪問一次，時間複雜度為 $O(N)$。」

### Whiteboard Strategy (白板策略)
*   Draw the array and use two arrows ($\downarrow$) for `L` and `R`.
    畫出陣列並用兩個箭頭 ($\downarrow$) 代表 `L` 和 `R`。
*   Write down the variables: `maxLen`, `currentSum`, `map`.
    寫下變數：`maxLen`, `currentSum`, `map`。
*   Trace one iteration where the window becomes invalid and demonstrate the shrinking loop.
    追蹤一次視窗變為無效的迭代，並演示收縮迴圈。

### Common Follow-ups (常見追問)
*   **Q:** What if the input is a stream?
    **問：** 如果輸入是串流怎麼辦？
    *   **A:** We can't store the whole array. We maintain the buffer/deque and drop elements from the left as they fall out of the window or become irrelevant.
    *   **答：** 我們不能存儲整個陣列。我們維護緩衝區/雙端佇列，當元素掉出視窗或變得不相關時，從左側丟棄它們。

---

## 7. Practice Problems (練習題)

### Easy (Warm-up)
**Problem:** Max Consecutive Ones III (LeetCode 1004)
**Hint:** Find the longest subarray with at most K zeros.
**提示：** 找出至多包含 K 個零的最長子陣列。
**Core Logic:** Expand right. If `zeros > K`, increment left. `Ans = max(Ans, right - left + 1)`.

### Medium (Standard)
**Problem:** Longest Repeating Character Replacement (LeetCode 424)
**Hint:** Valid if `windowLength - maxFrequency <= k`.
**提示：** 如果 `視窗長度 - 最大頻率 <= k` 則有效。
**Core Logic:** You don't actually need to shrink the window size, just shift it (advanced optimization), but standard shrink works too.

### Hard (Advanced)
**Problem:** Sliding Window Maximum (LeetCode 239)
**Hint:** You need $O(1)$ access to the max element. Use a Monotonic Deque.
**提示：** 你需要 $O(1)$ 時間存取最大元素。使用單調雙端佇列。
**Core Logic:** Store indices in Deque. Remove indices out of window from front. Remove indices with values smaller than `nums[right]` from back (they can never be max). Head is max.

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] **Initialization:** Are `left` and `right` starting at 0?
    **初始化：** `left` 和 `right` 是否從 0 開始？
- [ ] **Loop Condition:** Is the outer loop `right < n`?
    **迴圈條件：** 外層迴圈是 `right < n` 嗎？
- [ ] **Shrink Logic:** Is the shrink condition inside a `while` loop, not an `if`?
    **收縮邏輯：** 收縮條件是否在 `while` 迴圈內，而不是 `if`？
- [ ] **State Update:** Did I update the hashmap/sum *before* checking validity? Did I update it *while* shrinking?
    **狀態更新：** 我是否在檢查有效性 *之前* 更新了 hashmap/sum？我是否在收縮 *時* 更新了它？
- [ ] **Result Calculation:** Is the answer updated at the correct spot (usually after the `while` shrink loop)?
    **結果計算：** 答案是否在正確的位置更新（通常在 `while` 收縮迴圈之後）？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The Hungry Caterpillar (飢餓的毛毛蟲)
*   **Eating (Right++):** The caterpillar extends its head to eat leaves (data). It grows.
    **進食 (Right++)：** 毛毛蟲伸出頭吃葉子（數據）。它變長了。
*   **Indigestion (Invalid State):** It ate something bad (constraint violated).
    **消化不良 (無效狀態)：** 它吃了壞東西（違反限制）。
*   **Pooping (Left++):** It pulls its tail forward, excreting the old leaves until it feels better.
    **排泄 (Left++)：** 它把尾巴向前拉，排出舊葉子直到感覺好轉。

### The "At Most" Sandwich (「至多」三明治)
*   To get exactly the meat (K), you take the whole sandwich with bread (At Most K) and subtract the sandwich with just bread (At Most K-1).
    為了只吃到肉 (K)，你拿整個含麵包的三明治 (至多 K)，減去只有麵包的三明治 (至多 K-1)。