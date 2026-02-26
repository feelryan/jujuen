# Arrays & Hashing: Intermediate to Advanced
# 陣列與雜湊：進階指南

## 1. Learning Objectives (學習目標)

1.  **Master Space-Time Trade-offs:** Learn to confidently exchange $O(N)$ space for $O(1)$ access time to reduce overall algorithmic complexity from $O(N^2)$ to $O(N)$.
    **掌握時空權衡：** 學習自信地以 $O(N)$ 的空間換取 $O(1)$ 的存取時間，將整體演算法複雜度從 $O(N^2)$ 降低至 $O(N)$。

2.  **Differentiate Implementation Details:** Understand the nuances between JavaScript/TypeScript `Object` and `Map` regarding key types, iteration order, and performance.
    **區分實作細節：** 理解 JavaScript/TypeScript 中 `Object` 與 `Map` 在鍵值類型、迭代順序及效能上的細微差異。

3.  **Identify Implicit Patterns:** Recognize when a problem that seems to require sorting ($O(N \log N)$) can actually be solved using Hashing ($O(N)$).
    **識別隱性模式：** 辨識出那些看似需要排序（$O(N \log N)$）但實際上可以用雜湊（$O(N)$）解決的問題。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)

*   **Arrays:** Contiguous memory blocks offering constant-time access by index but linear-time search/insertion/deletion (unless at the end).
    **陣列：** 連續的記憶體區塊，提供透過索引的常數時間存取，但搜尋、插入或刪除（除非在末端）則需線性時間。
*   **Hashing (Hash Map/Set):** A technique that maps data of arbitrary size to fixed-size values (keys) to allow for average $O(1)$ lookups.
    **雜湊（雜湊表/集合）：** 一種將任意大小的資料映射到固定大小值（鍵）的技術，以允許平均 $O(1)$ 的查詢。

### Complexity (複雜度)

| Operation | Array (Unsorted) | Array (Sorted) | Hash Map / Set |
| :--- | :--- | :--- | :--- |
| **Access (Index)** | $O(1)$ | $O(1)$ | N/A |
| **Search (Value)** | $O(N)$ | $O(\log N)$ | $O(1)$ (Avg) |
| **Insert/Delete** | $O(N)$ | $O(N)$ | $O(1)$ (Avg) |

### When to Use (適用場景)
*   **Frequency Counting:** Counting occurrences of elements.
    **頻率計數：** 計算元素出現的次數。
*   **Existence Check:** Checking if an element has appeared before (deduplication).
    **存在性檢查：** 檢查元素是否曾經出現過（去重）。
*   **Caching/Memoization:** Storing results of expensive function calls.
    **快取/記憶化：** 儲存昂貴函數呼叫的結果。

### When NOT to Use (不適用場景)
*   **Ordering Matters:** Standard Hash Maps do not guarantee order (though ES6 `Map` preserves insertion order, it's not sorted).
    **順序很重要時：** 標準雜湊表不保證順序（雖然 ES6 `Map` 保留插入順序，但並非已排序狀態）。
*   **Nearest Neighbor/Range Queries:** Finding values "close to" X is inefficient; use BST or Heaps instead.
    **最近鄰/範圍查詢：** 尋找「接近」X 的值效率低落；應改用二元搜尋樹或堆積。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Frequency Map (Counter):**
    Use a Hash Map to count the frequency of each element to solve problems like Anagrams or Top K elements.
    **頻率表（計數器）：** 使用雜湊表計算每個元素的頻率，以解決變位詞（Anagrams）或前 K 個元素等問題。

2.  **Two Sum Variation (Complement Search):**
    Instead of iterating twice, iterate once and check if `target - current_value` exists in the Hash Map.
    **Two Sum 變體（補數搜尋）：** 不進行兩次迭代，而是迭代一次並檢查 `target - current_value` 是否存在於雜湊表中。

3.  **Prefix Sums (with Hashing):**
    Store the cumulative sum at each index in a Hash Map to find subarrays that sum to a specific value ($k$) by checking `current_sum - k`.
    **前綴和（搭配雜湊）：** 將每個索引的累加和儲存在雜湊表中，透過檢查 `current_sum - k` 來尋找總和為特定值 ($k$) 的子陣列。

4.  **Encoding Keys:**
    When using arrays or coordinates as keys (e.g., `[row, col]`), serialize them into strings (e.g., `"row,col"`) since arrays are reference types in JS/TS.
    **編碼鍵值：** 當使用陣列或座標作為鍵（例如 `[row, col]`）時，將它們序列化為字串（例如 `"row,col"`），因為陣列在 JS/TS 中是參考類型。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Consecutive Sequence (最長連續序列)
**LeetCode 128 (Medium)**

#### Problem Statement (問題重述)
Given an unsorted array of integers `nums`, return the length of the longest consecutive elements sequence.
給定一個未排序的整數陣列 `nums`，返回最長連續元素序列的長度。

*Constraint: You must write an algorithm that runs in $O(N)$ time.*
*限制：你必須撰寫一個時間複雜度為 $O(N)$ 的演算法。*

#### Thought Process (思路)

1.  **Brute Force (暴力解):**
    Sort the array first, then iterate to count consecutive numbers.
    先將陣列排序，然後迭代計算連續的數字。
    *   Complexity: $O(N \log N)$ due to sorting.
    *   複雜度：由於排序，為 $O(N \log N)$。
    *   *Verdict: Fails the $O(N)$ constraint.*
    *   *結論：不符合 $O(N)$ 的限制。*

2.  **Optimization (優化):**
    We need $O(1)$ lookups to check if a neighbor exists. We can throw everything into a `Set`.
    我們需要 $O(1)$ 的查詢來檢查鄰居是否存在。我們可以將所有內容放入 `Set` 中。
    However, if we iterate every number and check its neighbors, we might do redundant work.
    然而，如果我們迭代每個數字並檢查其鄰居，我們可能會做重複的工作。

3.  **Optimal Solution (最佳解):**
    Only start counting a sequence if the current number is the **start** of a sequence.
    只有當前數字是序列的 **起點** 時，才開始計數。
    How do we know it's the start? If `num - 1` does **not** exist in the set.
    我們如何知道它是起點？如果 `num - 1` **不** 存在於集合中。

#### TypeScript Reference Solution (TypeScript 參考解)

```typescript
function longestConsecutive(nums: number[]): number {
    // Edge case: empty array
    // 邊界條件：空陣列
    if (nums.length === 0) return 0;

    // Use a Set for O(1) lookups. This removes duplicates automatically.
    // 使用 Set 進行 O(1) 查詢。這會自動移除重複項。
    const numSet = new Set<number>(nums);
    let longestStreak = 0;

    for (const num of numSet) {
        // Only attempt to build a sequence if 'num' is the start.
        // Check if (num - 1) exists. If it does, 'num' is not the start.
        // 只有當 'num' 是起點時才嘗試建立序列。
        // 檢查 (num - 1) 是否存在。如果存在，則 'num' 不是起點。
        if (!numSet.has(num - 1)) {
            let currentNum = num;
            let currentStreak = 1;

            // Expand the sequence as long as the next number exists
            // 只要下一個數字存在，就擴展序列
            while (numSet.has(currentNum + 1)) {
                currentNum += 1;
                currentStreak += 1;
            }

            // Update the global maximum
            // 更新全域最大值
            longestStreak = Math.max(longestStreak, currentStreak);
        }
    }

    return longestStreak;
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Although there is a `while` loop inside a `for` loop, each number is visited at most twice (once by the `for` loop, and once by the `while` loop as part of a streak).
    **時間：** $O(N)$。雖然 `for` 迴圈內有一個 `while` 迴圈，但每個數字最多被訪問兩次（一次由 `for` 迴圈，一次作為序列的一部分由 `while` 迴圈訪問）。
*   **Space:** $O(N)$ to store the Set.
    **空間：** $O(N)$ 用於儲存 Set。

#### Common Mistake (錯誤示範)
```typescript
// BAD APPROACH: Checking every number without identifying the 'start'
// 錯誤方法：檢查每個數字卻沒有識別「起點」
for (const num of nums) {
    let current = num;
    while (numSet.has(current + 1)) { // This makes it O(N^2) in worst case
        current++;                     // 這在最壞情況下會變成 O(N^2)
    }
}
// Why? Imagine input: [1, 2, 3, 4, 5].
// You count 1->5, then 2->5, then 3->5... redundant calculations.
// 為什麼？想像輸入：[1, 2, 3, 4, 5]。
// 你會計算 1->5，然後 2->5，然後 3->5... 重複計算。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Map vs Object** | In TS/JS, `Object` keys are always strings (or Symbols). `Map` allows any type (numbers, objects) as keys. Use `Map` for frequent additions/removals. <br> **陷阱：** 在 TS/JS 中，`Object` 的鍵總是字串（或 Symbol）。`Map` 允許任何類型（數字、物件）作為鍵。頻繁增刪時請使用 `Map`。 |
| **Array as Key** | `myMap.set([1,2], "val")` followed by `myMap.get([1,2])` returns `undefined` because arrays are reference types. <br> **陷阱：** `myMap.set([1,2], "val")` 接著 `myMap.get([1,2])` 會回傳 `undefined`，因為陣列是參考類型（記憶體位址不同）。 |
| **Worst Case Hashing** | While Hash Map is avg $O(1)$, worst case (many collisions) is $O(N)$. In interviews, usually assume avg case unless asked about security/attacks. <br> **陷阱：** 雖然雜湊表平均是 $O(1)$，但最壞情況（大量碰撞）是 $O(N)$。面試中通常假設平均情況，除非被問及安全性/攻擊。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Are the inputs sorted? Can there be duplicates? What is the range of the numbers?"
    **釐清：** 「輸入是否已排序？會有重複值嗎？數字的範圍是多少？」
2.  **Propose:** "Since we need to find pairs/counts efficiently, a Hash Map allows us to do this in linear time, trading some space for speed."
    **提議：** 「由於我們需要有效率地尋找配對/計數，雜湊表允許我們以線性時間完成，用一些空間換取速度。」
3.  **Refine:** "Before coding, I'll handle edge cases like empty arrays."
    **優化：** 「在寫程式之前，我會先處理像空陣列這樣的邊界條件。」

### Whiteboard/Coding Strategy (白板策略)
*   **Define Types:** In TypeScript, explicitly define the Map types: `const map = new Map<string, number>();`. This shows seniority.
    **定義類型：** 在 TypeScript 中，明確定義 Map 類型：`const map = new Map<string, number>();`。這顯示了資深程度。
*   **Variable Naming:** Use `charCount` or `indexMap` instead of `map` or `h`.
    **變數命名：** 使用 `charCount` 或 `indexMap` 而非 `map` 或 `h`。

### Common Follow-up (常見追問)
*   **Q:** "What if the data is too large to fit in memory?"
    **問：** 「如果資料太大無法放入記憶體怎麼辦？」
*   **A:** "We would need to use external sorting or sharding (consistent hashing) to distribute data across multiple machines."
    **答：** 「我們需要使用外部排序或分片（一致性雜湊）將資料分佈到多台機器上。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (存在重複元素)
*   **Prompt:** Given an integer array, return true if any value appears at least twice.
    **題目：** 給定一個整數陣列，如果任何值出現至少兩次，則返回 true。
*   **Hint:** `Set.size !== nums.length`.
    **提示：** `Set.size !== nums.length`。

### 2. Medium: Top K Frequent Elements (前 K 個高頻元素)
*   **Prompt:** Given an integer array `nums` and an integer `k`, return the `k` most frequent elements.
    **題目：** 給定整數陣列 `nums` 和整數 `k`，返回出現頻率最高的 `k` 個元素。
*   **Hint:** Use a Hash Map for counting, then use Bucket Sort (array of arrays) where index represents frequency to solve in $O(N)$.
    **提示：** 使用雜湊表計數，然後使用桶排序（陣列的陣列），其中索引代表頻率，以在 $O(N)$ 內解決。

### 3. Medium/Hard: Product of Array Except Self (除自身以外陣列的乘積)
*   **Prompt:** Return an array such that `output[i]` is the product of all elements of `nums` except `nums[i]`. **Cannot use division.**
    **題目：** 返回一個陣列，使得 `output[i]` 是 `nums` 中除了 `nums[i]` 之外所有元素的乘積。**不能使用除法。**
*   **Hint:** Use two passes (Prefix product and Suffix product). While not strictly "Hashing", it uses the same pre-computation array pattern often grouped here.
    **提示：** 使用兩次遍歷（前綴乘積和後綴乘積）。雖然嚴格來說不是「雜湊」，但它使用了常歸類於此的預計算陣列模式。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Complexity:** Did I achieve $O(N)$ or $O(N \log N)$? Avoid $O(N^2)$.
    **複雜度：** 我是否達到了 $O(N)$ 或 $O(N \log N)$？避免 $O(N^2)$。
*   [ ] **Space:** Did I consider the space cost of the Map/Set?
    **空間：** 我是否考慮了 Map/Set 的空間成本？
*   [ ] **Key Types:** If using `Map`, am I using the correct key type? If using `Object`, are keys strings?
    **鍵值類型：** 如果使用 `Map`，我是否使用了正確的鍵類型？如果使用 `Object`，鍵是否為字串？
*   [ ] **Edge Cases:** Empty array? Array with 1 element? All duplicates?
    **邊界條件：** 空陣列？只有一個元素的陣列？全部重複？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Library Index (圖書館索引):**
    Searching an array is like walking through every aisle looking for a book ($O(N)$). Using a Hash Map is like looking up the book location in the computer system ($O(1)$) and walking straight to it.
    **圖書館索引：** 搜尋陣列就像走過每一條走道尋找一本書（$O(N)$）。使用雜湊表就像在電腦系統中查詢書籍位置（$O(1)$），然後直接走過去。

*   **The Locker Room (置物櫃):**
    An array is a row of lockers. You know locker #5 is at the 5th position. A Hash Function is the key fob that tells you exactly which locker belongs to "Alice" without checking every name tag.
    **置物櫃：** 陣列是一排置物櫃。你知道 5 號置物櫃就在第 5 個位置。雜湊函數就像是一個感應扣，它告訴你哪個置物櫃屬於 "Alice"，而不需要檢查每個名牌。