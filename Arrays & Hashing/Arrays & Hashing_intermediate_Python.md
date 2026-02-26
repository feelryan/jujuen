# Arrays & Hashing: Intermediate Masterclass
# 陣列與雜湊：中階大師班

## 1. Learning Objectives (學習目標)

*   **Master Space-Time Trade-offs:** Understand how to utilize $O(N)$ space (Hash Maps/Sets) to reduce time complexity from $O(N^2)$ to $O(N)$.
    **掌握空間換取時間的權衡：** 理解如何利用 $O(N)$ 的空間（雜湊表/集合）將時間複雜度從 $O(N^2)$ 降低至 $O(N)$。

*   **Identify Prefix State Patterns:** Learn to recognize problems where the solution depends on the cumulative state (e.g., prefix sums) stored in a Hash Map.
    **識別前綴狀態模式：** 學習辨識那些解決方案依賴於儲存在雜湊表中的累積狀態（如前綴和）的問題。

*   **Handle Edge Cases & Collisions:** Gain proficiency in handling duplicates, negative numbers, and boundary conditions that often break naive hashing solutions.
    **處理邊界情況與衝突：** 熟練處理重複項、負數以及常導致樸素雜湊解法崩潰的邊界條件。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Arrays (陣列)
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 儲存在連續記憶體位置的元素集合。
*   **Intuition:** Fast access via index, slow search (unsorted), expensive insertion/deletion.
    **直覺：** 透過索引存取極快，搜尋較慢（未排序時），插入/刪除代價高昂。
*   **Complexity:** Access $O(1)$, Search $O(N)$, Insert/Delete $O(N)$.
    **複雜度：** 存取 $O(1)$，搜尋 $O(N)$，插入/刪除 $O(N)$。

### Hashing (Hash Map / Hash Set) (雜湊)
*   **Definition:** A structure that maps keys to values using a hash function.
    **定義：** 使用雜湊函數將鍵映射到值的結構。
*   **Intuition:** The "Magic Lookup". It allows us to check "Have I seen this before?" or "Where is X?" instantly.
    **直覺：** 「神奇查找」。它允許我們瞬間檢查「我之前見過這個嗎？」或「X 在哪裡？」。
*   **Complexity:** Average Insert/Lookup/Delete $O(1)$; Worst case $O(N)$ (rare, due to collisions).
    **複雜度：** 平均插入/查找/刪除 $O(1)$；最差情況 $O(N)$（罕見，因雜湊衝突導致）。

### When to use (適用場景)
*   Finding duplicates or counting frequencies.
    尋找重複項或計算頻率。
*   Looking for a specific "complement" value (e.g., Target - Current).
    尋找特定的「補數」值（例如：目標值 - 當前值）。

### When NOT to use (不適用場景)
*   When finding the "nearest" or "largest/smallest" in a range (consider Heaps or Sorting).
    當尋找範圍內的「最近」或「最大/最小」值時（考慮堆積或排序）。
*   When strict $O(1)$ space is required.
    當嚴格要求 $O(1)$ 空間時。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Frequency Map / Counter (頻率表)
*   Used for Anagrams or "Top K Frequent Elements".
    用於變位詞（Anagrams）或「前 K 個高頻元素」。
*   **Python Tool:** `collections.Counter` or `dict`.

### B. State Caching (狀態快取)
*   Storing the result of a calculation (like a prefix sum) at a specific index to avoid re-calculation.
    將計算結果（如前綴和）儲存在特定索引處，以避免重複計算。
*   **Classic Case:** Subarray Sum Equals K.
    **經典案例：** 子陣列和等於 K。

### C. HashSet for Existence (用於存在性檢查的雜湊集合)
*   Checking if an element exists in $O(1)$ to construct sequences.
    以 $O(1)$ 檢查元素是否存在，用於建構序列。
*   **Classic Case:** Longest Consecutive Sequence.
    **經典案例：** 最長連續序列。

---

## 4. Example Walkthrough (範例講解)

### Problem: Subarray Sum Equals K (子陣列和等於 K)
**Problem Statement:** Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳和等於 `k` 的子陣列總數。

### Approach 1: Brute Force (暴力法)
*   **Idea:** Iterate through all possible subarrays using nested loops and calculate their sums.
    **思路：** 使用巢狀迴圈遍歷所有可能的子陣列並計算它們的和。
*   **Complexity:** Time $O(N^2)$ or $O(N^3)$ (depending on sum calculation), Space $O(1)$.
    **複雜度：** 時間 $O(N^2)$ 或 $O(N^3)$（取決於求和方式），空間 $O(1)$。
*   **Verdict:** Too slow for large inputs ($N > 10^4$).
    **結論：** 對於大輸入（$N > 10^4$）太慢。

### Approach 2: Optimal - Prefix Sum + Hash Map (最佳解 - 前綴和 + 雜湊表)
*   **Intuition:** If the cumulative sum up to index `j` is `S_j`, and the cumulative sum up to index `i` (where $i < j$) is `S_i`, then the sum of the subarray between `i` and `j` is $S_j - S_i$.
    **直覺：** 如果到索引 `j` 的累積和是 `S_j`，而到索引 `i`（其中 $i < j$）的累積和是 `S_i`，那麼 `i` 和 `j` 之間的子陣列和就是 $S_j - S_i$。
*   **Equation:** We want $S_j - S_i = k$. This implies $S_i = S_j - k$.
    **方程式：** 我們想要 $S_j - S_i = k$。這意味著 $S_i = S_j - k$。
*   **Strategy:** As we iterate and calculate the current prefix sum (`S_j`), we check the Hash Map: "Have I seen a prefix sum of `S_j - k` before?" If yes, add the count of those occurrences to our answer.
    **策略：** 當我們遍歷並計算當前前綴和（`S_j`）時，我們檢查雜湊表：「我之前見過 `S_j - k` 這個前綴和嗎？」如果是，將出現的次數加到答案中。

### Python Solution (Python 參考解)

```python
from typing import List
from collections import defaultdict

def subarraySum(nums: List[int], k: int) -> int:
    # Map to store the frequency of prefix sums found so far.
    # 用於儲存目前為止發現的前綴和頻率的雜湊表。
    # Key: prefix_sum, Value: count of occurrences
    # 鍵：前綴和，值：出現次數
    prefix_sum_counts = {0: 1}  
    
    current_sum = 0
    result = 0
    
    for num in nums:
        current_sum += num
        
        # Calculate the value we need to find in our history to form a valid subarray.
        # 計算我們需要在歷史紀錄中找到的值，以形成有效的子陣列。
        diff = current_sum - k
        
        # If (current_sum - k) exists in the map, it means there are subarrays ending here with sum k.
        # 如果 (current_sum - k) 存在於表中，表示有以這裡結尾且和為 k 的子陣列。
        if diff in prefix_sum_counts:
            result += prefix_sum_counts[diff]
            
        # Update the map with the current prefix sum.
        # 更新雜湊表，記錄當前的前綴和。
        # We use .get() to handle the case where the key doesn't exist yet.
        # 我們使用 .get() 來處理鍵尚不存在的情況。
        prefix_sum_counts[current_sum] = prefix_sum_counts.get(current_sum, 0) + 1
        
    return result

# Time Complexity: O(N) - Single pass through the array.
# 時間複雜度：O(N) - 只需遍歷陣列一次。
# Space Complexity: O(N) - In worst case, all prefix sums are distinct.
# 空間複雜度：O(N) - 最差情況下，所有前綴和都不同。
```

### Common Mistake (錯誤示範)
*   **Mistake:** Initializing the map as empty `{}` instead of `{0: 1}`.
    **錯誤：** 將雜湊表初始化為空 `{}` 而不是 `{0: 1}`。
*   **Why it fails:** If `nums = [3]` and `k = 3`, `current_sum` becomes 3. `diff` is 0. If 0 is not in the map, we miss the subarray that starts from the beginning.
    **為何失敗：** 如果 `nums = [3]` 且 `k = 3`，`current_sum` 變為 3。`diff` 為 0。如果 0 不在表中，我們會漏掉從頭開始的那個子陣列。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱 / 混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Map Keys** | Using mutable types (lists) as keys. <br> 使用可變類型（列表）作為鍵。 | Keys must be immutable (int, str, tuple). <br> 鍵必須是不可變的（整數、字串、元組）。 |
| **Subarray vs Subsequence** | Confusing contiguous vs non-contiguous. <br> 混淆連續與非連續。 | **Subarray:** Contiguous (slice). **Subsequence:** Order matters, gaps allowed. <br> **子陣列：** 連續（切片）。**子序列：** 順序重要，允許間隔。 |
| **Uniqueness** | Assuming input has no duplicates. <br> 假設輸入沒有重複項。 | Always ask: "Can the array contain duplicates?" This affects Set vs Map choice. <br> 永遠要問：「陣列包含重複項嗎？」這影響選擇 Set 還是 Map。 |
| **Sorting** | Sorting an array to solve "Two Sum". <br> 排序陣列來解決「兩數之和」。 | Sorting destroys original indices. If indices are required, use a Hash Map. <br> 排序會破壞原始索引。如果需要回傳索引，請使用雜湊表。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Constraints (釐清限制):**
    *   "Are the numbers sorted?" (Hint for Two Pointers)
        「數字是排序過的嗎？」（雙指針的提示）
    *   "Can numbers be negative?" (Breaks Sliding Window logic sometimes)
        「數字可以是負數嗎？」（有時會破壞滑動視窗的邏輯）
    *   "What is the range of values?" (Hint for Bucket Sort/Counting)
        「數值的範圍是多少？」（桶排序/計數的提示）

2.  **Narrative Arc (口條框架):**
    *   "I will start with a brute force approach to establish a baseline."
        「我會先從暴力解法開始，建立一個基準。」
    *   "The bottleneck here is the repeated lookup/summation, which takes $O(N)$."
        「這裡的瓶頸是重複的查找/求和，耗時 $O(N)$。」
    *   "I can optimize this by trading space for time using a Hash Map to store [State]."
        「我可以透過空間換取時間來優化，使用雜湊表來儲存 [狀態]。」

3.  **Whiteboard Strategy (白板策略):**
    *   Write the example input/output at the top.
        在頂部寫下範例輸入/輸出。
    *   Trace the variables (`current_sum`, `map`) manually for the first few iterations before coding.
        在寫程式碼之前，手動追蹤前幾次迭代的變數（`current_sum`, `map`）。

---

## 7. Practice Problems (練習題)

### Level 1: Valid Anagram (有效的變位詞)
*   **Prompt:** Given two strings, return true if they are anagrams.
    **題目：** 給定兩個字串，如果它們是變位詞則回傳 true。
*   **Hint:** Frequency counting.
    **提示：** 頻率計數。
*   **Solution Logic:** Use an array of size 26 (for lowercase English) or a Hash Map to count char frequencies. Compare counts.
    **解題思路：** 使用大小為 26 的陣列（針對小寫英文字母）或雜湊表來計算字元頻率。比較計數。

### Level 2: Group Anagrams (變位詞分組)
*   **Prompt:** Given an array of strings, group the anagrams together.
    **題目：** 給定一個字串陣列，將變位詞分組在一起。
*   **Hint:** What is the "canonical" representation of a word?
    **提示：** 一個單字的「標準」表示形式是什麼？
*   **Solution Logic:** Map Key = Sorted String (or Tuple of counts), Value = List of original strings.
    **解題思路：** Map 的鍵 = 排序後的字串（或計數元組），值 = 原始字串的列表。

### Level 3: Longest Consecutive Sequence (最長連續序列)
*   **Prompt:** Given an unsorted array, find the length of the longest consecutive elements sequence. Must be $O(N)$.
    **題目：** 給定一個未排序陣列，找出最長連續元素序列的長度。必須是 $O(N)$。
*   **Hint:** You need $O(1)$ lookups. Use a Set. Only start counting if it's the *start* of a sequence.
    **提示：** 你需要 $O(1)$ 的查找。使用集合（Set）。只有當它是序列的 *起點* 時才開始計數。
*   **Solution Logic:** Convert list to Set. Iterate `num` in Set. If `num - 1` is NOT in set, `num` is a start. Loop `while (num + length) in set`.
    **解題思路：** 將列表轉為集合。遍歷集合中的 `num`。如果 `num - 1` 不在集合中，則 `num` 是起點。執行 `while (num + length) in set` 迴圈。

---

## 8. Rapid Checklists (快速檢核表)

*   [ ] **Empty Input:** Did I handle `nums = []`?
    **空輸入：** 我是否處理了 `nums = []`？
*   [ ] **Initialization:** Is my accumulator (sum/count) initialized correctly (0 vs 1 vs -1)?
    **初始化：** 我的累加器（和/計數）初始化正確嗎（0 vs 1 vs -1）？
*   [ ] **Key Existence:** Did I use `.get()` or `defaultdict` or check `if key in map`?
    **鍵的存在性：** 我是否使用了 `.get()` 或 `defaultdict` 或檢查了 `if key in map`？
*   [ ] **Complexity:** Is the solution strictly $O(N)$ or did I accidentally put a loop inside a loop (e.g., `list.count()` inside a loop)?
    **複雜度：** 解法是嚴格的 $O(N)$ 嗎？還是我不小心在迴圈內放了另一個迴圈（例如：迴圈內的 `list.count()`）？

---

## 9. Memory Anchors (記憶錨點)

*   **The "Time Machine" (時光機):**
    *   Think of the Hash Map as a time machine. It remembers what the state (prefix sum) was in the past.
    *   想像雜湊表是一台時光機。它記得過去的狀態（前綴和）是什麼。
    *   *Analogy:* "To find a subarray of sum K, I look back in time to see if I was ever at `Current - K`."
    *   *類比：* 「要找到和為 K 的子陣列，我回顧過去，看看我是否曾經處於 `Current - K` 的狀態。」

*   **The "Lost & Found" Box (失物招領箱):**
    *   For Two Sum / Complement problems. You hold an item `X` and check the box for `Target - X`. If it's there, you match. If not, you put `X` in the box for someone else to find later.
    *   用於兩數之和 / 補數問題。你拿著物品 `X` 並在箱子裡檢查 `Target - X`。如果有，就配對成功。如果沒有，你把 `X` 放進箱子讓別人以後來找。