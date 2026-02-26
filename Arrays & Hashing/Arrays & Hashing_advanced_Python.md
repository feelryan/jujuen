# Module: Arrays & Hashing (Advanced)
# 模組：陣列與雜湊（進階）

## 1. Learning Objectives (學習目標)

*   **Master Space-Time Trade-offs:** Deeply understand when to trade $O(n)$ space for $O(1)$ access time, and conversely, when to use in-place algorithms to save memory.
    **掌握時空權衡：** 深刻理解何時該以 $O(n)$ 的空間換取 $O(1)$ 的存取時間，反之，何時該使用原地（in-place）演算法以節省記憶體。
*   **Optimize Hashing Strategy:** Move beyond basic dictionary usage to understand key design (tuple vs. string), collision handling implications, and amortized complexity analysis.
    **優化雜湊策略：** 超越基本的字典使用，理解鍵值設計（元組 vs 字串）、雜湊衝突的影響以及攤銷複雜度分析。
*   **Integrate Prefix Sums:** Combine hashing with prefix sums to solve subarray problems in linear time, a common pattern in senior-level interviews.
    **整合前綴和：** 將雜湊與前綴和結合，以線性時間解決子陣列問題，這是資深面試中常見的模式。
*   **Handle "In-Place" Constraints:** Solve array problems requiring $O(1)$ extra space by using the array itself as a hash map (cyclic sort pattern).
    **處理「原地」限制：** 透過將陣列本身作為雜湊表（循環排序模式），解決要求 $O(1)$ 額外空間的陣列問題。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Arrays (陣列)
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 儲存在連續記憶體位置的元素集合。
*   **Intuition:** Fast reads due to cache locality; slow inserts/deletes due to shifting.
    **直覺：** 由於快取局部性，讀取極快；由於需要位移，插入/刪除較慢。
*   **Advanced Insight:** In Python, lists are dynamic arrays (pointers to objects). Resizing happens exponentially (amortized $O(1)$ append).
    **進階洞察：** 在 Python 中，列表是動態陣列（指向物件的指標）。調整大小呈指數級增長（攤銷 $O(1)$ 附加）。

### Hashing (雜湊)
*   **Definition:** Mapping data of arbitrary size to fixed-size values (keys) for direct addressing.
    **定義：** 將任意大小的資料映射到固定大小的值（鍵），以便直接定址。
*   **Complexity:** Average $O(1)$ for search/insert/delete. Worst case $O(n)$ (collisions).
    **複雜度：** 搜尋/插入/刪除平均 $O(1)$。最差情況 $O(n)$（衝突）。
*   **Applicability:** Best for frequency counting, duplicate detection, and $O(1)$ lookups. Not suitable for finding "nearest" elements or range queries (use Trees/Heaps instead).
    **適用性：** 最適合頻率計數、重複檢測和 $O(1)$ 查找。不適用於尋找「最近」元素或範圍查詢（應改用樹/堆積）。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, simple iteration is rarely the answer. Look for these patterns:
對於資深工程師，簡單的迭代很少是答案。請尋找以下模式：

1.  **Hash Map as a State Tracker (雜湊表作為狀態追蹤器):**
    *   Storing `seen` elements to find complements (e.g., Two Sum).
    *   儲存 `seen`（已見）元素以尋找補數（例如：兩數之和）。
2.  **Prefix Sum + Hash Map (前綴和 + 雜湊表):**
    *   Used to find subarrays with a specific sum. Formula: `Sum(i, j) = Prefix[j] - Prefix[i-1]`.
    *   用於尋找特定總和的子陣列。公式：`Sum(i, j) = Prefix[j] - Prefix[i-1]`。
3.  **Encoding & Grouping (編碼與分組):**
    *   Converting complex objects (like strings or lists) into a hashable key (tuple) to group anagrams or patterns.
    *   將複雜物件（如字串或列表）轉換為可雜湊的鍵（元組），以對變位詞或模式進行分組。
4.  **Cyclic Sort / Index Mapping (循環排序 / 索引映射):**
    *   Using the array indices `0` to `n-1` as keys to simulate a hash map without extra space.
    *   使用陣列索引 `0` 到 `n-1` 作為鍵，在不使用額外空間的情況下模擬雜湊表。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Consecutive Sequence (最長連續序列)
**LeetCode 128 (Hard/Medium)**

**Problem Statement:**
Given an unsorted array of integers, find the length of the longest consecutive elements sequence. You must write an algorithm that runs in $O(n)$ time.
**問題重述：**
給定一個未排序的整數陣列，找出最長連續元素序列的長度。你必須編寫一個時間複雜度為 $O(n)$ 的演算法。

---

### Approach & Evolution (思路與演進)

**1. Brute Force (暴力解):**
*   For each number, search for `num + 1`, `num + 2`, etc., in the array.
    對於每個數字，在陣列中搜尋 `num + 1`、`num + 2` 等等。
*   **Complexity:** $O(n^3)$ (loop x loop x search).
    **複雜度：** $O(n^3)$（迴圈 x 迴圈 x 搜尋）。

**2. Sorting (排序優化):**
*   Sort the array, then iterate to count consecutive streaks.
    將陣列排序，然後迭代計算連續條紋。
*   **Complexity:** $O(n \log n)$. This violates the $O(n)$ requirement.
    **複雜度：** $O(n \log n)$。這違反了 $O(n)$ 的要求。

**3. Optimal: HashSet (最佳解：雜湊集合):**
*   Throw all numbers into a `set` for $O(1)$ lookups.
    將所有數字丟入 `set` 以進行 $O(1)$ 查找。
*   Iterate through the set. Only start counting a sequence if `num - 1` is **not** in the set (this ensures we only start from the *beginning* of a sequence).
    迭代該集合。只有當 `num - 1` **不在** 集合中時才開始計數（這確保我們只從序列的 *開頭* 開始）。
*   **Complexity:** Time $O(n)$, Space $O(n)$.
    **複雜度：** 時間 $O(n)$，空間 $O(n)$。

---

### Python Solution (Python 參考解)

```python
from typing import List

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        # Handle edge case: empty array
        # 處理邊界情況：空陣列
        if not nums:
            return 0
        
        # Use a set for O(1) lookups. This removes duplicates automatically.
        # 使用集合進行 O(1) 查找。這會自動移除重複項。
        num_set = set(nums)
        longest_streak = 0
        
        for num in num_set:
            # Check if 'num' is the start of a sequence
            # 檢查 'num' 是否為序列的起點
            if (num - 1) not in num_set:
                current_num = num
                current_streak = 1
                
                # Expand the sequence as long as consecutive numbers exist
                # 只要連續數字存在，就擴展序列
                while (current_num + 1) in num_set:
                    current_num += 1
                    current_streak += 1
                
                # Update the global maximum
                # 更新全域最大值
                longest_streak = max(longest_streak, current_streak)
        
        return longest_streak

# Complexity Analysis:
# Time: O(n). Although there is a while loop inside a for loop, each number 
# is visited at most twice (once by the for loop, once by the while loop).
# 複雜度分析：
# 時間：O(n)。雖然 for 迴圈內有一個 while 迴圈，但每個數字最多被訪問兩次
# （一次由 for 迴圈，一次由 while 迴圈）。
# Space: O(n) to store the set.
# 空間：O(n) 用於儲存集合。
```

### Common Mistake (錯誤示範)
*   **Mistake:** Running the `while` loop for *every* number, not just the start of the sequence.
    **錯誤：** 對 *每個* 數字執行 `while` 迴圈，而不僅僅是序列的起點。
*   **Why it's wrong:** This degrades performance to $O(n^2)$ in the worst case (e.g., if input is `[1, 2, 3, 4, 5]`, you recount the tail repeatedly).
    **為何錯誤：** 這會使最差情況下的效能降至 $O(n^2)$（例如，如果輸入是 `[1, 2, 3, 4, 5]`，你會重複計算尾部）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Nuance (陷阱 / 細節) |
| :--- | :--- |
| **List as Key** | **Cannot** use a list as a dictionary key in Python because it is mutable. Use a `tuple` instead. <br> **不能** 使用列表作為 Python 字典的鍵，因為它是可變的。請改用 `tuple`。 |
| **String Hashing** | Hashing a string is not strictly $O(1)$; it depends on the length of the string, $O(L)$. For very long strings, this matters. <br> 雜湊字串嚴格來說不是 $O(1)$；它取決於字串長度 $O(L)$。對於非常長的字串，這很重要。 |
| **Collision Handling** | In an interview, don't assume collisions never happen. Mention that Python uses "Open Addressing" (with randomization) to handle them. <br> 面試中，不要假設衝突永不發生。提及 Python 使用「開放定址法」（搭配隨機化）來處理它們。 |
| **Modifying Iterables** | Never add/remove items from a dictionary/set while iterating over it. It throws a `RuntimeError`. <br> 絕對不要在迭代字典/集合時新增/移除項目。這會拋出 `RuntimeError`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Is the array sorted?", "Can it contain duplicates?", "What is the range of values?" (Hinting at Radix Sort or Array-as-Map).
    **釐清限制：** 「陣列已排序嗎？」、「包含重複項嗎？」、「數值範圍為何？」（暗示基數排序或陣列即雜湊表）。
2.  **Start with Trade-offs:** "A brute force approach is $O(n^2)$. We can optimize time to $O(n)$ by using a Hash Map, costing $O(n)$ space."
    **從權衡開始：** 「暴力解法是 $O(n^2)$。我們可以透過使用雜湊表將時間優化為 $O(n)$，但需消耗 $O(n)$ 空間。」
3.  **Dry Run:** Before coding, trace your logic with a small example like `[100, 4, 200, 1, 3, 2]`.
    **模擬執行：** 編碼前，用一個小範例（如 `[100, 4, 200, 1, 3, 2]`）追蹤你的邏輯。

### Common Follow-ups (常見追問)
*   **Q:** How to handle data too large for memory?
    **問：** 如何處理大到記憶體裝不下的資料？
    *   **A:** Distributed Hashing (Consistent Hashing), Sharding, or External Sort.
    *   **答：** 分散式雜湊（一致性雜湊）、分片或外部排序。
*   **Q:** What if we cannot use extra space?
    **問：** 如果我們不能使用額外空間怎麼辦？
    *   **A:** Sort ($O(n \log n)$) or modify input array in-place ($O(n)$ but destructive).
    *   **答：** 排序 ($O(n \log n)$) 或原地修改輸入陣列 ($O(n)$ 但具破壞性)。

---

## 7. Practice Problems (練習題)

### 1. Easy/Medium: Group Anagrams (變位詞分組)
*   **Problem:** Given an array of strings, group anagrams together.
    **問題：** 給定一個字串陣列，將變位詞分組在一起。
*   **Hint:** Use a Hash Map where the key is a sorted tuple of characters or a count-array tuple (e.g., `(1, 0, 2...)` for 'a', 'b', 'c' counts).
    **提示：** 使用雜湊表，鍵為排序後的字元元組或計數陣列元組（例如：針對 'a', 'b', 'c' 計數的 `(1, 0, 2...)`）。

### 2. Medium: Subarray Sum Equals K (和為 K 的子陣列)
*   **Problem:** Find total number of continuous subarrays whose sum equals `k`.
    **問題：** 找出總和等於 `k` 的連續子陣列總數。
*   **Hint:** Prefix Sum + Hash Map. Store `{prefix_sum: count}`. Check if `current_sum - k` exists in the map.
    **提示：** 前綴和 + 雜湊表。儲存 `{prefix_sum: count}`。檢查 `current_sum - k` 是否存在於映射中。

### 3. Hard: First Missing Positive (第一個缺失的正整數)
*   **Problem:** Find the smallest missing positive integer in an unsorted array. $O(n)$ time, $O(1)$ space.
    **問題：** 在未排序陣列中找出最小的缺失正整數。$O(n)$ 時間，$O(1)$ 空間。
*   **Hint:** Cyclic Sort. Place number `x` at index `x-1`. Iterate again to find the first index `i` where `nums[i] != i+1`.
    **提示：** 循環排序。將數字 `x` 放到索引 `x-1` 的位置。再次迭代以找出第一個 `nums[i] != i+1` 的索引 `i`。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Empty Input:** Did I handle `[]` or `None`?
    **空輸入：** 我是否處理了 `[]` 或 `None`？
*   [ ] **Duplicates:** Does my logic break if the array has `[1, 1, 1]`?
    **重複項：** 如果陣列有 `[1, 1, 1]`，我的邏輯會崩潰嗎？
*   [ ] **Key Types:** Did I try to hash a list? (Use `tuple(my_list)`).
    **鍵類型：** 我是否嘗試雜湊列表？（使用 `tuple(my_list)`）。
*   [ ] **Complexity Proof:** Can I explain why my nested loop is actually $O(n)$ (amortized) and not $O(n^2)$?
    **複雜度證明：** 我能解釋為什麼我的巢狀迴圈實際上是 $O(n)$（攤銷）而不是 $O(n^2)$ 嗎？

---

## 9. Memory Anchors (記憶錨點)

*   **Hash Map = Wormhole (雜湊表 = 蟲洞):**
    *   Arrays require walking the path (iteration). Hash Maps teleport you directly to the destination (Key to Value).
    *   陣列需要走過路徑（迭代）。雜湊表將你直接傳送到目的地（鍵到值）。
*   **Prefix Sum = Snapshot History (前綴和 = 歷史快照):**
    *   `Prefix[i]` is the history of the world up to time `i`. To know what happened between time `i` and `j`, just subtract history `i` from history `j`.
    *   `Prefix[i]` 是截至時間 `i` 的世界歷史。要知道時間 `i` 和 `j` 之間發生了什麼，只需從歷史 `j` 中減去歷史 `i`。