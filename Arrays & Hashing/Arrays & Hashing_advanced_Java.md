這裡是一份針對 **Senior Software Engineer** 設計的 **Arrays & Hashing** 進階面試教材。
Here is an advanced interview study guide for **Arrays & Hashing** designed for **Senior Software Engineers**.

本教材假設你已經熟悉基本語法，我們將專注於優化策略、複雜度權衡以及高階面試技巧。
This guide assumes you are familiar with basic syntax; we will focus on optimization strategies, complexity trade-offs, and high-level interview techniques.

---

# Module: Arrays & Hashing (Advanced)

## 1. Learning Objectives（學習目標）

1.  **Master Space-Time Trade-offs:**
    掌握「空間換取時間」的精髓，利用 Hashing 將 $O(N)$ 的搜尋降低至 $O(1)$。
    Master the essence of "Space-Time Trade-offs," utilizing Hashing to reduce search time from $O(N)$ to $O(1)$.

2.  **Handle Complex Key Design:**
    學會為複雜物件（如字串變位詞、矩陣座標）設計自定義 Hash Key。
    Learn to design custom Hash Keys for complex objects (e.g., string anagrams, matrix coordinates).

3.  **In-place Manipulations:**
    在嚴格的空間限制下（$O(1)$ 額外空間），利用陣列索引本身作為 Hash Map（如 Cyclic Sort）。
    Under strict space constraints ($O(1)$ extra space), utilize array indices themselves as a Hash Map (e.g., Cyclic Sort).

4.  **Identify Patterns for Subarray Problems:**
    能夠迅速區分何時使用 Sliding Window，何時必須使用 Prefix Sum + Hashing（特別是涉及負數時）。
    Quickly distinguish when to use Sliding Window versus when Prefix Sum + Hashing is mandatory (especially involving negative numbers).

---

## 2. Core Concepts Snapshot（核心觀念速覽）

### Arrays (陣列)
*   **Definition:** A collection of elements identified by index or key, stored in contiguous memory locations.
    **定義：** 一組透過索引或鍵值識別的元素，儲存在連續的記憶體位置中。
*   **Intuition:** Fast access via math (pointer arithmetic), great CPU cache locality.
    **直覺：** 透過數學（指標運算）快速存取，具備極佳的 CPU 快取局部性。
*   **Complexity:** Access $O(1)$, Search $O(N)$, Insert/Delete $O(N)$.
    **複雜度：** 存取 $O(1)$，搜尋 $O(N)$，插入/刪除 $O(N)$。

### Hashing (雜湊)
*   **Definition:** Mapping data of arbitrary size to fixed-size values (hash codes) to index a hash table.
    **定義：** 將任意大小的資料映射為固定大小的值（雜湊碼），用以索引雜湊表。
*   **Intuition:** A "magic dictionary" where finding any word takes one step, provided collisions are handled well.
    **直覺：** 一本「魔法字典」，只要衝突處理得當，查找任何單字只需一步。
*   **Complexity:** Average Access/Insert/Delete $O(1)$; Worst case $O(N)$ (many collisions).
    **複雜度：** 平均存取/插入/刪除 $O(1)$；最差情況 $O(N)$（大量衝突）。

### Senior Insight (資深觀點)
For Senior roles, be prepared to discuss **Collision Resolution** (Chaining vs. Open Addressing) and **Load Factor** resizing logic in Java's `HashMap`.
對於資深職位，請準備好討論 **衝突解決方案**（鏈結法 vs. 開放定址法）以及 Java `HashMap` 中的 **負載因子** 擴容邏輯。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Prefix Sum + Hash Map (前綴和 + 雜湊表)
*   **Scenario:** Counting subarrays with a specific sum, especially when the array contains negative numbers.
    **場景：** 計算具有特定總和的子陣列，特別是當陣列包含負數時。
*   **Why:** Sliding window fails with negative numbers because the sum is not monotonic.
    **原因：** 滑動視窗在有負數時會失效，因為總和不具備單調性。

### B. Array as Hash Map (原地雜湊)
*   **Scenario:** Finding duplicates or missing numbers in a range $[1, N]$ with $O(1)$ space.
    **場景：** 在 $O(1)$ 空間下，尋找範圍 $[1, N]$ 內的重複或缺失數字。
*   **Technique:** Use the value at index `i` to mark the index `value` as visited (e.g., by negating it).
    **技巧：** 利用索引 `i` 處的值，將索引 `value` 標記為已訪問（例如將其變為負數）。

### C. Key Encoding (鍵值編碼)
*   **Scenario:** Grouping Anagrams or identifying patterns.
    **場景：** 變位詞分組或識別模式。
*   **Technique:** Instead of sorting a string ($O(K \log K)$), use a character count array converted to a string key (e.g., "1#0#2...") for $O(K)$.
    **技巧：** 不對字串排序（$O(K \log K)$），而是使用字元計數陣列轉換為字串鍵（如 "1#0#2..."）以達到 $O(K)$。

---

## 4. Example Walkthrough（範例講解）

### Problem: Subarray Sum Equals K (LeetCode 560)
**Problem Statement:** Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳總和等於 `k` 的子陣列總數。

#### 1. Approach Evolution (思路演進)

*   **Brute Force ($O(N^2)$):**
    Iterate all start and end points, calculating sum.
    遍歷所有起點和終點，計算總和。
    *Critique:* Too slow for large inputs ($N=20,000$).
    *評論：* 對於大輸入（$N=20,000$）太慢。

*   **Sliding Window (Incorrect here):**
    Expand right, shrink left if sum > k.
    向右擴展，若總和大於 k 則縮減左側。
    *Fatal Flaw:* If `nums` has negative numbers, shrinking doesn't guarantee sum decreases.
    *致命缺陷：* 若 `nums` 含有負數，縮減左側無法保證總和減少。

*   **Optimal: Prefix Sum + HashMap ($O(N)$):**
    Equation: $Sum(i, j) = PrefixSum(j) - PrefixSum(i-1) = k$.
    公式：$Sum(i, j) = PrefixSum(j) - PrefixSum(i-1) = k$。
    Therefore, we look for: $PrefixSum(i-1) = PrefixSum(j) - k$.
    因此，我們尋找：$PrefixSum(i-1) = PrefixSum(j) - k$。
    We iterate through the array, maintaining a running sum, and check how many times `current_sum - k` has appeared before.
    我們遍歷陣列，維護當前累加和，並檢查 `current_sum - k` 在之前出現過幾次。

#### 2. Java Reference Solution (Java 參考解)

```java
import java.util.HashMap;
import java.util.Map;

public class Solution {
    public int subarraySum(int[] nums, int k) {
        // Map stores <PrefixSum, Frequency>
        // Map 儲存 <前綴和, 出現頻率>
        Map<Integer, Integer> map = new HashMap<>();
        
        // Base case: A prefix sum of 0 appears once (representing an empty subarray before the start)
        // 基礎情況：前綴和為 0 出現一次（代表開始前的空子陣列）
        // This is crucial for subarrays starting from index 0.
        // 這對於從索引 0 開始的子陣列至關重要。
        map.put(0, 1);
        
        int count = 0;
        int currentSum = 0;
        
        for (int num : nums) {
            currentSum += num;
            
            // Check if (currentSum - k) exists in the map
            // 檢查 map 中是否存在 (currentSum - k)
            // If it exists, it means there are subarrays ending here with sum k
            // 若存在，表示有以這裡結尾的子陣列總和為 k
            if (map.containsKey(currentSum - k)) {
                count += map.get(currentSum - k);
            }
            
            // Update the frequency of the current prefix sum
            // 更新當前前綴和的頻率
            map.put(currentSum, map.getOrDefault(currentSum, 0) + 1);
        }
        
        return count;
    }
}
```

#### 3. Complexity & Boundaries (複雜度與邊界)
*   **Time Complexity:** $O(N)$ - Single pass.
    **時間複雜度：** $O(N)$ - 單次遍歷。
*   **Space Complexity:** $O(N)$ - HashMap can store up to N distinct prefix sums.
    **空間複雜度：** $O(N)$ - HashMap 最多儲存 N 個不同的前綴和。
*   **Edge Case:** `k` can be negative; `nums` can be empty (though constraints usually say length >= 1).
    **邊界條件：** `k` 可以是負數；`nums` 可以是空的（雖然限制條件通常長度 >= 1）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Subarray (子陣列)** | **Subsequence (子序列)** | Subarray is **contiguous**; Subsequence is not (order preserved). <br> 子陣列是**連續**的；子序列則否（保留順序）。 |
| **Set** | **Map** | Use Set for existence checks; Use Map for counting/associating data. <br> 用 Set 檢查存在性；用 Map 進行計數或關聯資料。 |
| **HashMap `get`** | **HashMap `getOrDefault`** | Always use `getOrDefault` for counters to avoid `NullPointerException` or extra checks. <br> 計數器務必使用 `getOrDefault` 以避免空指針異常或額外檢查。 |
| **Array Key** | **String Key** | In Java, `int[]` as a Map key uses object identity (address), not content. Must convert to String or List. <br> 在 Java 中，`int[]` 作為 Map 鍵使用的是物件識別（位址），而非內容。必須轉換為 String 或 List。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are the numbers sorted? Can they be negative? What is the range of values?"
    **釐清限制：** 「數字有排序嗎？會有負數嗎？數值範圍是多少？」
2.  **Propose High-Level Idea:** "Since we need to find pairs/subarrays, a Brute Force is $O(N^2)$. I can optimize this using a Hash Map to store visited elements for $O(1)$ lookup."
    **提出高層思路：** 「既然我們需要尋找配對/子陣列，暴力解是 $O(N^2)$。我可以利用 Hash Map 儲存已訪問元素，將查找優化至 $O(1)$。」
3.  **Discuss Trade-offs:** "The Hash Map approach uses $O(N)$ space. If space is tight, we might need sorting ($O(N \log N)$ time, $O(1)$ or $O(\log N)$ space)."
    **討論權衡：** 「Hash Map 方法使用 $O(N)$ 空間。若空間吃緊，我們可能需要排序（$O(N \log N)$ 時間， $O(1)$ 或 $O(\log N)$ 空間）。」

### Whiteboard Strategy (白板策略)
*   **Variable Naming:** Use `freqMap`, `prefixSum`, `curr`, `target` instead of `map`, `sum`, `i`, `k`.
    **變數命名：** 使用 `freqMap`, `prefixSum`, `curr`, `target` 代替 `map`, `sum`, `i`, `k`。
*   **Dry Run:** Before saying "I'm done", manually trace the code with a small example (e.g., `[1, -1, 1]`, `k=1`).
    **手動演練：** 在說「我完成了」之前，用一個小範例（如 `[1, -1, 1]`, `k=1`）手動追蹤程式碼。

---

## 7. Practice Problems（練習題）

### Easy (Warm-up): Valid Anagram
*   **Prompt:** Given two strings `s` and `t`, return true if `t` is an anagram of `s`.
    **題目：** 給定兩個字串 `s` 和 `t`，若 `t` 是 `s` 的變位詞則回傳 true。
*   **Hint:** Use a fixed-size array `int[26]` instead of a HashMap for better performance.
    **提示：** 使用固定大小陣列 `int[26]` 代替 HashMap 以獲得更好效能。
*   **Key Insight:** Character ASCII subtraction (`char - 'a'`).
    **關鍵洞察：** 字元 ASCII 相減（`char - 'a'`）。

### Intermediate: Longest Consecutive Sequence
*   **Prompt:** Given an unsorted array, find the length of the longest consecutive elements sequence. Must be $O(N)$.
    **題目：** 給定未排序陣列，找出最長連續元素序列的長度。必須是 $O(N)$。
*   **Hint:** Put all numbers in a `HashSet`. Iterate, but only build sequence if `num - 1` is **not** in the set (start of a sequence).
    **提示：** 將所有數字放入 `HashSet`。遍歷時，只有當 `num - 1` **不在** 集合中時（序列起點），才開始構建序列。

### Advanced: First Missing Positive
*   **Prompt:** Given an unsorted integer array, find the smallest missing positive integer. Must be $O(N)$ time and $O(1)$ space.
    **題目：** 給定未排序整數陣列，找出最小缺失的正整數。必須是 $O(N)$ 時間與 $O(1)$ 空間。
*   **Hint:** Use the array indices as the hash keys. Place number `x` at index `x-1` (Cyclic Sort logic).
    **提示：** 利用陣列索引作為雜湊鍵。將數字 `x` 放置在索引 `x-1` 的位置（循環排序邏輯）。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Empty Input:** Did I handle `nums.length == 0`?
    **空輸入：** 我處理了 `nums.length == 0` 嗎？
*   [ ] **Map Key Existence:** Did I use `containsKey` before `get` (or use `getOrDefault`)?
    **Map 鍵存在性：** 我在 `get` 之前使用了 `containsKey`（或使用 `getOrDefault`）嗎？
*   [ ] **Duplicate Handling:** Does the problem allow duplicates? Does my logic break?
    **重複處理：** 題目允許重複嗎？我的邏輯會因此崩潰嗎？
*   [ ] **Complexity:** Is my solution strictly $O(N)$ or did I accidentally put a loop inside a loop?
    **複雜度：** 我的解法嚴格是 $O(N)$ 嗎？還是我不小心寫了巢狀迴圈？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **The "Hotel Key" Analogy (Hashing):**
    Imagine a hotel (Array). Instead of checking every room for "Mr. Smith", you look up his name in the computer (Hash Map) to get the room number directly.
    **「飯店房卡」類比（雜湊）：**
    想像一家飯店（陣列）。你不需要逐間房尋找「Smith 先生」，而是在電腦（Hash Map）中查詢他的名字，直接取得房號。

*   **The "Receipt Stack" (Prefix Sum):**
    To know how much you spent between March and May, you don't re-add all receipts. You take the "Year-to-Date total at May" minus "Year-to-Date total at February".
    **「收據堆疊」（前綴和）：**
    要知道三月到五月花了多少錢，你不需要重新加總所有收據。你拿「五月的年度累計總額」減去「二月的年度累計總額」。

*   **Visual Anchor:**
    $Hash Map = O(1) \text{ Lookup, } O(N) \text{ Space}$
    $Sorting = O(\log N) \text{ Search, } O(N \log N) \text{ Prep}$