# Module: Arrays & Hashing (Advanced)
# 模組：陣列與雜湊（進階篇）

## 1. Learning Objectives (學習目標)

1.  **Master Space-Time Trade-offs:** Understand when to sacrifice $O(N)$ space for $O(1)$ lookup time, and conversely, how to achieve $O(1)$ space using in-place modification.
    **掌握時空權衡：** 理解何時犧牲 $O(N)$ 空間以換取 $O(1)$ 查找時間，反之亦然，如何利用原地修改（in-place modification）達到 $O(1)$ 空間複雜度。

2.  **Handle "Invisible" Constraints:** Learn to identify constraints that rule out standard approaches (e.g., negative numbers breaking Sliding Window, or strict $O(1)$ space requirements).
    **處理「隱形」限制：** 學習識別那些排除標準解法的限制條件（例如：負數會破壞滑動視窗的單調性，或嚴格的 $O(1)$ 空間要求）。

3.  **Optimize for Cache Locality & Collisions:** Beyond Big-O, discuss practical implications like memory locality in arrays versus hash collisions in maps.
    **優化快取局部性與雜湊碰撞：** 除了 Big-O 之外，探討實務上的影響，如陣列的記憶體局部性（locality）對比 Map 的雜湊碰撞問題。

4.  **Prefix Sums & Hashing Synergy:** Deep dive into combining prefix sums with hash maps to solve sub-array problems efficiently.
    **前綴和與雜湊的協同效應：** 深入探討如何結合前綴和（Prefix Sums）與雜湊表（Hash Maps）來高效解決子陣列問題。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Hash Map (雜湊表)
*   **Intuition:** A mathematical function maps data to a fixed address for instant retrieval.
    **直覺：** 透過數學函數將資料映射到固定位址，以實現即時檢索。
*   **Complexity:** Average Time $O(1)$, Worst Case $O(N)$ (collisions); Space $O(N)$.
    **複雜度：** 平均時間 $O(1)$，最差情況 $O(N)$（碰撞）；空間 $O(N)$。
*   **Senior Insight:** In V8 (Node.js/Chrome), `Map` preserves insertion order, whereas `Object` keys are unordered (mostly). For integer keys, `Map` is generally more performant than `Object`.
    **資深洞察：** 在 V8 引擎中，`Map` 保留插入順序，而 `Object` 鍵則是無序的（大部分情況）。對於整數鍵，`Map` 通常比 `Object` 效能更好。

### Arrays (陣列)
*   **Intuition:** Contiguous memory blocks allowing index-based access.
    **直覺：** 允許基於索引存取的連續記憶體區塊。
*   **Senior Insight:** Arrays are cache-friendly. Iterating an array is often faster than a Linked List or Hash Map due to CPU prefetching.
    **資深洞察：** 陣列對快取友善（Cache-friendly）。由於 CPU 的預取機制（prefetching），遍歷陣列通常比鏈結串列或雜湊表更快。

### When to use (適用場景)
*   Finding duplicates, frequency counting, or "pair matching" (e.g., Two Sum).
    尋找重複項、頻率計數或「配對匹配」（如 Two Sum）。
*   $O(1)$ lookups are critical.
    $O(1)$ 查找至關重要時。

### When NOT to use (不適用場景)
*   When you need to search for a value in a range (use Binary Search Tree or Sorted Array).
    當需要在範圍內搜尋數值時（應使用二元搜尋樹或排序陣列）。
*   When strict $O(1)$ space is required (unless you use the array indices themselves as hash keys).
    當要求嚴格的 $O(1)$ 空間時（除非利用陣列索引本身作為雜湊鍵）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Prefix Sum + Hash Map (前綴和 + 雜湊表)
*   **Pattern:** Calculate the running sum `curr`. If `curr - k` exists in the map, a subarray summing to `k` exists.
    **模式：** 計算當前累加和 `curr`。如果 `curr - k` 存在於 Map 中，則表示存在和為 `k` 的子陣列。
*   **Use Case:** Subarray Sum Equals K.
    **案例：** 子陣列和為 K。

### B. Index as a Hash Key (Cyclic Sort / In-place Hashing)
*   **Pattern:** Map the value `x` to index `x-1` by swapping.
    **模式：** 透過交換，將數值 `x` 映射到索引 `x-1` 的位置。
*   **Use Case:** First Missing Positive, Find All Duplicates in an Array ($O(1)$ Space).
    **案例：** 第一個缺失的正數，找出陣列中所有重複數（$O(1)$ 空間）。

### C. Frequency Map / Counter
*   **Pattern:** Count occurrences of each element.
    **模式：** 計算每個元素的出現次數。
*   **Use Case:** Top K Frequent Elements, Group Anagrams.
    **案例：** 前 K 個高頻元素，字母異位詞分組。

---

## 4. Example Walkthrough (範例講解)

### Problem: Subarray Sum Equals K (LeetCode 560)
**Problem Statement:** Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳和為 `k` 的子陣列總數。

> **Constraint Note:** `nums[i]` can be negative. This invalidates the standard Sliding Window approach.
> **限制註記：** `nums[i]` 可能為負數。這使得標準的滑動視窗（Sliding Window）解法無效。

#### Approach 1: Brute Force (暴力法)
*   Iterate all start and end points, calculate sum.
    遍歷所有起點與終點，計算總和。
*   **Complexity:** Time $O(N^2)$ or $O(N^3)$, Space $O(1)$.
    **複雜度：** 時間 $O(N^2)$ 或 $O(N^3)$，空間 $O(1)$。

#### Approach 2: Optimized with Prefix Sum + HashMap (最佳解)
*   **Idea:** `Sum(i, j) = PrefixSum[j] - PrefixSum[i-1]`.
    **思路：** `Sum(i, j) = PrefixSum[j] - PrefixSum[i-1]`。
*   We want `Sum(i, j) == k`, which implies `PrefixSum[j] - k == PrefixSum[i-1]`.
    我們希望 `Sum(i, j) == k`，這意味著 `PrefixSum[j] - k == PrefixSum[i-1]`。
*   As we iterate, we store the frequency of every `PrefixSum` encountered so far.
    在遍歷過程中，我們儲存目前為止遇到的每個 `PrefixSum` 的出現頻率。

#### TypeScript Solution (Reference)

```typescript
function subarraySum(nums: number[], k: number): number {
    // Map stores <prefixSum, frequency>
    // Map 儲存 <前綴和, 出現頻率>
    const prefixSumMap = new Map<number, number>();
    
    // Base case: A prefix sum of 0 exists once (conceptually before the array starts)
    // 基礎情況：前綴和為 0 出現一次（概念上在陣列開始之前）
    prefixSumMap.set(0, 1);
    
    let count = 0;
    let currentSum = 0;
    
    for (const num of nums) {
        currentSum += num;
        
        // Check if there is a prefix sum that satisfies: currentSum - target = k
        // 檢查是否存在一個前綴和滿足：currentSum - target = k
        // Derived from: currentSum - k = target_prefix_sum
        // 推導自：currentSum - k = 目標前綴和
        const complement = currentSum - k;
        
        if (prefixSumMap.has(complement)) {
            // Add the number of times this complement has appeared
            // 加上該補數出現過的次數
            count += prefixSumMap.get(complement)!;
        }
        
        // Update the map with the current sum
        // 更新 Map 中的當前和
        prefixSumMap.set(currentSum, (prefixSumMap.get(currentSum) || 0) + 1);
    }
    
    return count;
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ — We iterate the array once, and Map lookups are amortized $O(1)$.
    **時間：** $O(N)$ — 我們遍歷陣列一次，Map 查找攤提為 $O(1)$。
*   **Space:** $O(N)$ — In the worst case, all prefix sums are distinct.
    **空間：** $O(N)$ — 最差情況下，所有前綴和皆不相同。

#### Common Mistake (錯誤示範)
*   **Using Sliding Window:** Since inputs can be negative, the sum doesn't grow monotonically as we expand the window.
    **使用滑動視窗：** 由於輸入可能為負數，當擴展視窗時，總和不會單調遞增。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Map vs Object (JS/TS)** | **Object keys are strings.** Using numbers as keys in Objects converts them to strings (slow). Use `Map` for integer keys. <br> **Object 的鍵是字串。** 在 Object 中使用數字作為鍵會將其轉換為字串（較慢）。整數鍵請使用 `Map`。 |
| **Sliding Window vs Prefix Sum** | **Sliding Window** requires monotonicity (usually non-negative numbers). **Prefix Sum + Hash** handles negatives. <br> **滑動視窗** 需要單調性（通常是非負數）。**前綴和 + Hash** 可處理負數。 |
| **Array.sort()** | In JS/TS, `sort()` converts elements to strings by default! `[1, 10, 2]` becomes `[1, 10, 2]`. Always use `(a, b) => a - b`. <br> 在 JS/TS 中，`sort()` 預設將元素轉為字串！`[1, 10, 2]` 排序後仍是 `[1, 10, 2]`。務必使用 `(a, b) => a - b`。 |
| **Hash Collisions** | In system design interviews, failing to mention collision resolution (chaining vs open addressing) is a red flag. <br> 在系統設計面試中，若未提及碰撞解決方案（鏈結法 vs 開放定址法），是一個警訊。 |

---

## 6. Interview Strategy (面試實戰建議)

### A. Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are the numbers sorted? Can they be negative? What is the range of values?"
    **釐清限制：** 「數字有排序嗎？會有負數嗎？數值範圍是多少？」
2.  **Propose High-Level Idea:** "Since we need to find subarrays summing to K and we have negative numbers, a sliding window won't work. I propose using a Prefix Sum with a Hash Map to store historical sums."
    **提出高層次思路：** 「由於我們需要尋找和為 K 的子陣列且存在負數，滑動視窗行不通。我建議使用前綴和搭配雜湊表來儲存歷史總和。」
3.  **Dry Run:** Before coding, walk through a small example (e.g., `[1, -1, 1]`, k=1) on the whiteboard.
    **模擬執行：** 寫程式前，在白板上跑過一個小範例（如 `[1, -1, 1]`, k=1）。

### B. Whiteboard Strategy (白板策略)
*   Define types clearly (e.g., `Map<number, number>`).
    清楚定義型別。
*   Handle `undefined` explicitly when getting from Map (`map.get(key) || 0`).
    從 Map 取值時明確處理 `undefined`。

### C. Common Follow-ups (常見追問)
*   "What if the array is too large to fit in memory?" (Answer: Distributed processing / MapReduce, or stream processing).
    「如果陣列太大無法放入記憶體怎麼辦？」（答：分散式處理 / MapReduce，或串流處理）。
*   "What if the input is a continuous stream?" (Answer: We can't store everything; maybe keep a sliding window of the last N elements or use probabilistic data structures like Bloom Filters if checking existence).
    「如果輸入是連續串流？」（答：無法儲存所有內容；可能保留最後 N 個元素的滑動視窗，或若檢查存在性可使用 Bloom Filters 等機率資料結構）。

---

## 7. Practice Problems (練習題)

### Easy / Warm-up: Longest Consecutive Sequence
*   **Prompt:** Given an unsorted array, find the length of the longest consecutive elements sequence. Time $O(N)$.
    **題目：** 給定未排序陣列，找出最長連續元素序列的長度。時間 $O(N)$。
*   **Hint:** Use a `Set` for $O(1)$ lookups. Only start counting if `num - 1` is NOT in the set (identifying the start of a sequence).
    **提示：** 使用 `Set` 進行 $O(1)$ 查找。只有當 `num - 1` 不在集合中時才開始計數（識別序列的起點）。

### Medium: Product of Array Except Self
*   **Prompt:** Return an array where `output[i]` is the product of all elements except `nums[i]`. **No division allowed.** Time $O(N)$, Space $O(1)$ (excluding output).
    **題目：** 回傳一個陣列，其中 `output[i]` 是除 `nums[i]` 外所有元素的乘積。**不允許使用除法。** 時間 $O(N)$，空間 $O(1)$（不計輸出陣列）。
*   **Hint:** Use two passes. Pass 1: Calculate prefix products. Pass 2: Multiply by suffix products on the fly.
    **提示：** 使用兩次遍歷。第一遍：計算前綴乘積。第二遍：即時乘以其後綴乘積。

### Hard: First Missing Positive
*   **Prompt:** Find the smallest missing positive integer. Time $O(N)$, Space $O(1)$.
    **題目：** 找出最小的缺失正整數。時間 $O(N)$，空間 $O(1)$。
*   **Hint:** **Cyclic Sort / Index as Hash Key**. Place number `x` at index `x-1` (i.e., `nums[x-1] = x`). Ignore numbers $\le 0$ or $> N$. Then scan to find the first index `i` where `nums[i] != i + 1`.
    **提示：** **循環排序 / 索引即雜湊鍵**。將數字 `x` 放到索引 `x-1` 的位置（即 `nums[x-1] = x`）。忽略 $\le 0$ 或 $> N$ 的數字。然後掃描找出第一個 `nums[i] != i + 1` 的索引 `i`。

---

## 8. Quick Checklists (快速檢核表)

### Debugging & Self-Review (除錯與自我審查)
- [ ] Did I handle empty arrays? (`if (nums.length === 0)`)
    我是否處理了空陣列？
- [ ] Did I handle duplicates correctly? (Especially when using Sets/Maps)
    我是否正確處理了重複項？（特別是使用 Sets/Maps 時）
- [ ] Did I handle negative numbers? (Crucial for sum problems)
    我是否處理了負數？（對求和問題至關重要）
- [ ] Is my Map key type correct? (Avoid `[1,2]` as a key in Map without serialization)
    我的 Map 鍵型別正確嗎？（避免在未序列化的情況下使用 `[1,2]` 作為 Map 的鍵）

### Complexity Check (複雜度確認)
- [ ] Is it strictly $O(N)$? (Avoid nested loops unless intended)
    是否嚴格為 $O(N)$？（除非有意為之，否則避免巢狀迴圈）
- [ ] Is space complexity optimized? (Can I modify input in-place?)
    空間複雜度優化了嗎？（我能原地修改輸入嗎？）

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Library" Analogy (Hash Map):**
    Imagine a library where every book has a unique GPS coordinate calculated from its title. You don't browse shelves (Array scan); you teleport directly to the book (Hash lookup).
    **「圖書館」類比（雜湊表）：** 想像一座圖書館，每本書都有一個根據書名計算出的唯一 GPS 座標。你不需要瀏覽書架（陣列掃描）；你直接傳送（Teleport）到書的位置（雜湊查找）。

*   **The "Receipt" Analogy (Prefix Sum):**
    To know how much you spent between March 5th and March 10th, you don't add up daily receipts again. You take the "Total Year-to-Date Spend on March 10th" minus "Total Year-to-Date Spend on March 4th".
    **「收據」類比（前綴和）：** 想知道 3月5日 到 3月10日 花了多少錢，你不需要重新加總每天的收據。你只需要用「3月10日的年度累計支出」減去「3月4日的年度累計支出」。

*   **The "Correct Seat" Analogy (Cyclic Sort):**
    Students are sitting randomly. You tell student #5 to go to seat #5. If someone is already there, you swap them. Repeat until everyone is in their right seat or ignored.

    **「對號入座」類比（循環排序）：** 學生隨意亂坐。你叫 5 號學生去坐 5 號座位。如果那裡已經有人，你就交換他們。重複此步驟直到每個人都在正確座位上或被忽略。
