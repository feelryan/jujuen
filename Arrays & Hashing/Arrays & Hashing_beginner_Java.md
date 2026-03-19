這裡是一份針對 **Arrays & Hashing (陣列與雜湊)** 的完整面試教材。
Here is a complete interview preparation guide for **Arrays & Hashing**.

雖然這是基礎主題，但對於資深工程師來說，重點在於展現對「時空權衡（Space-Time Trade-off）」的深刻理解以及程式碼的簡潔性。
While this is a foundational topic, the focus for a Senior Engineer is demonstrating a deep understanding of "Space-Time Trade-offs" and code cleanliness.

---

# Module: Arrays & Hashing (Beginner/Foundational)

## 1. Learning Objectives（學習目標）

1.  **Master the Space-Time Trade-off:** Understand when to sacrifice $O(N)$ space (using a Hash Map) to achieve $O(1)$ access time.
    **掌握時空權衡：** 理解何時該犧牲 $O(N)$ 的空間（使用雜湊表）來換取 $O(1)$ 的存取時間。
2.  **Handle Edge Cases & Constraints:** Proficiently handle empty arrays, duplicates, and large number constraints.
    **處理邊界情況與限制：** 熟練處理空陣列、重複元素以及大數限制。
3.  **Optimize Key Generation:** Learn how to design custom keys for Hash Maps to group complex data types.
    **優化鍵值生成：** 學習如何為雜湊表設計自定義鍵值（Key），以對複雜資料類型進行分組。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Arrays (陣列)
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 儲存在連續記憶體位置的元素集合。
*   **Intuition:** Think of it as a row of numbered lockers; you know exactly where locker #5 is.
    **直覺：** 把它想像成一排有編號的置物櫃；你確切知道 5 號櫃在哪裡。
*   **Complexity (Time):** Access $O(1)$, Search $O(N)$, Insert/Delete $O(N)$ (due to shifting).
    **複雜度（時間）：** 存取 $O(1)$，搜尋 $O(N)$，插入/刪除 $O(N)$（因為需要移動元素）。

### Hashing (Hash Map / Hash Set)
*   **Definition:** A data structure that maps keys to values using a hash function.
    **定義：** 使用雜湊函數將鍵（Key）映射到值（Value）的資料結構。
*   **Intuition:** A library index system; you look up a book title (Key) to find its location (Value) instantly.
    **直覺：** 圖書館的索引系統；你查書名（Key）就能立刻找到它的位置（Value）。
*   **Complexity (Time):** Access/Insert/Delete Amortized $O(1)$. Worst case $O(N)$ (collisions).
    **複雜度（時間）：** 存取/插入/刪除 平均攤提 $O(1)$。最差情況 $O(N)$（發生碰撞）。

### When to use (適用場景)
*   **Arrays:** When index-based access is needed or memory is strictly constrained (no overhead).
    **陣列：** 當需要基於索引存取，或記憶體受到嚴格限制時（無額外開銷）。
*   **Hashing:** When you need to check for existence, count frequencies, or perform lookups in $O(1)$.
    **雜湊：** 當你需要檢查存在性、計算頻率或執行 $O(1)$ 查找時。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Frequency Map / Counter (頻率表):**
    Using a Hash Map to count occurrences of elements.
    使用雜湊表來計算元素的出現次數。
    *   *Target:* "Find the most frequent element", "Check if two strings are anagrams".
    *   *目標：* 「找出出現最頻繁的元素」、「檢查兩個字串是否為異位構詞」。

2.  **HashSet for Existence (利用 HashSet 檢查存在):**
    Using a Set to track seen elements to find duplicates or intersections.
    使用 Set 來追蹤已見過的元素，以找出重複項或交集。
    *   *Target:* "Contains Duplicate", "Intersection of Two Arrays".
    *   *目標：* 「包含重複項」、「兩個陣列的交集」。

3.  **Index Mapping (索引映射):**
    Using an array as a map when keys are small integers (e.g., `char` counts).
    當鍵值是小整數時（例如字元計數），使用陣列作為映射表。
    *   *Optimization:* `int[26]` is faster and lighter than `HashMap<Character, Integer>`.
    *   *優化：* `int[26]` 比 `HashMap<Character, Integer>` 更快且更省空間。

---

## 4. Example Walkthrough（範例講解）

### Problem: Group Anagrams (異位構詞分組)
**Problem Statement:** Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.
**問題重述：** 給定一個字串陣列 `strs`，將異位構詞（由相同字母重組而成的單字）分組在一起。你可以按任何順序返回答案。

*Example:* Input: `["eat","tea","tan","ate","nat","bat"]` -> Output: `[["bat"],["nat","tan"],["ate","eat","tea"]]`

### Approach 1: Sorting (Brute Force / Naive)
**思路：** Sort each string alphabetically. Anagrams will become identical strings. Use the sorted string as the Map Key.
**思路：** 將每個字串按字母順序排序。異位構詞將變成相同的字串。使用排序後的字串作為 Map 的鍵。

*   **Complexity:** $O(N \cdot K \log K)$, where $N$ is the number of strings and $K$ is the max length of a string.
*   **複雜度：** $O(N \cdot K \log K)$，其中 $N$ 是字串數量，$K$ 是字串最大長度。
*   **Verdict:** Good, but sorting takes extra time.
*   **結論：** 不錯，但排序需要額外時間。

### Approach 2: Frequency Array Hashing (Optimal)
**思路：** Instead of sorting, count the character frequency of each string (a-z). Use this count signature as the Map Key.
**思路：** 不進行排序，而是計算每個字串的字元頻率（a-z）。使用這個計數特徵作為 Map 的鍵。

*   **Complexity:** $O(N \cdot K)$. We iterate through each string once.
*   **複雜度：** $O(N \cdot K)$。我們遍歷每個字串一次。
*   **Why Better:** Counting is $O(K)$, faster than Sorting $O(K \log K)$.
*   **為何更好：** 計數是 $O(K)$，比排序 $O(K \log K)$ 快。

### Java Reference Solution (Optimal)

```java
import java.util.*;

public class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        // Handle edge case: empty input
        // 處理邊界情況：空輸入
        if (strs == null || strs.length == 0) {
            return new ArrayList<>();
        }

        // Map to store the grouping: Key is the "signature", Value is list of anagrams
        // 用於儲存分組的 Map：Key 是「特徵簽名」，Value 是異位構詞列表
        Map<String, List<String>> map = new HashMap<>();

        for (String s : strs) {
            // Create a frequency count for characters a-z
            // 為 a-z 字元建立頻率計數
            char[] count = new char[26];
            for (char c : s.toCharArray()) {
                count[c - 'a']++;
            }

            // Convert the count array to a String to use as a Hash Key
            // Ideally, we need a unique representation. String.valueOf(char[]) works.
            // 將計數陣列轉換為字串以用作 Hash Key
            // 理想情況下，我們需要一個唯一的表示法。String.valueOf(char[]) 是可行的。
            String key = String.valueOf(count);

            // If key doesn't exist, initialize the list
            // 如果 key 不存在，初始化列表
            map.putIfAbsent(key, new ArrayList<>());

            // Add the original string to the correct group
            // 將原始字串加入正確的群組
            map.get(key).add(s);
        }

        // Return the values as a list of lists
        // 將 values 作為列表的列表返回
        return new ArrayList<>(map.values());
    }
}
```

### Common Mistake (錯誤示範)
Using the `int[]` array directly as the Map Key.
直接使用 `int[]` 陣列作為 Map 的鍵。

*   **Why Wrong:** In Java, arrays use reference equality for `hashCode()` and `equals()`. Two different arrays with the same content are considered different keys.
*   **為何錯：** 在 Java 中，陣列的 `hashCode()` 和 `equals()` 使用參考（記憶體位址）相等性。兩個內容相同但實例不同的陣列會被視為不同的鍵。
*   **Fix:** Convert to `String` or use `Arrays.deepToString()` (though slower) or wrap in a `List`.
*   **修正：** 轉換為 `String`，或使用 `Arrays.deepToString()`（較慢），或包裝在 `List` 中。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Pitfall / Nuance (陷阱/細節) |
| :--- | :--- |
| **Hash Collisions** | Don't assume $O(1)$ is guaranteed worst-case. In Java 8+, HashMap uses a Red-Black tree for collisions (improving worst case to $O(\log N)$), but malicious inputs can still degrade performance. <br> 不要假設 $O(1)$ 是保證的最差情況。Java 8+ 的 HashMap 使用紅黑樹處理碰撞（將最差情況提升至 $O(\log N)$），但惡意輸入仍可能降低效能。 |
| **Mutable Keys** | Never use a mutable object as a Map Key. If the object changes, its hashCode changes, and you lose the value. <br> 永遠不要使用可變物件作為 Map 的鍵。如果物件改變，其 hashCode 也會改變，你將無法找回對應的值。 |
| **Array vs ArrayList** | `int[]` is primitive and fixed size. `ArrayList<Integer>` is an object wrapper and dynamic. For performance-critical code (like DP or counters), prefer `int[]`. <br> `int[]` 是原始型別且固定大小。`ArrayList<Integer>` 是物件包裝且動態的。對於效能關鍵的程式碼（如 DP 或計數器），優先選擇 `int[]`。 |

---

## 6. Interview Strategy（面試實戰建議）

1.  **Clarify Constraints (釐清限制):**
    *   "Are the inputs sorted?" (If yes, think Two Pointers/Binary Search).
    *   「輸入是否已排序？」（若是，考慮雙指針/二分搜尋）。
    *   "What is the range of values?" (If small, e.g., ASCII, use Array instead of HashMap).
    *   「數值的範圍是多少？」（若很小，例如 ASCII，使用陣列代替 HashMap）。

2.  **Narrative Framework (口條框架):**
    *   "A brute force approach would be $O(N^2)$, but we can trade space for time using a Hash Map to achieve $O(N)$."
    *   「暴力解法是 $O(N^2)$，但我們可以利用雜湊表以空間換取時間，達到 $O(N)$。」

3.  **Whiteboard Strategy (白板策略):**
    *   Define the Map clearly: `Map<Element, Frequency>` or `Map<Element, Index>`.
    *   清楚定義 Map：`Map<元素, 頻率>` 或 `Map<元素, 索引>`。

---

## 7. Practice Problems（練習題）

### 1. Easy: Contains Duplicate
**Task:** Return true if any value appears at least twice.
**任務：** 如果任何數值出現至少兩次，返回 true。
*   **Hint:** Use a `HashSet`. Add elements while iterating. If `add()` returns false, it's a duplicate.
*   **提示：** 使用 `HashSet`。遍歷時加入元素。如果 `add()` 返回 false，即為重複。

### 2. Medium: Top K Frequent Elements
**Task:** Given an integer array, return the $k$ most frequent elements.
**任務：** 給定一個整數陣列，返回出現頻率最高的 $k$ 個元素。
*   **Hint:** 1. Count frequencies with HashMap. 2. Use a Bucket Sort (array where index = frequency) OR a Min-Heap.
*   **提示：** 1. 用 HashMap 計算頻率。 2. 使用桶排序（陣列索引 = 頻率）或最小堆積（Min-Heap）。

### 3. Hard (Conceptually): Longest Consecutive Sequence
**Task:** Given an unsorted array, find the length of the longest consecutive elements sequence. Must be $O(N)$.
**任務：** 給定未排序陣列，找出最長連續元素序列的長度。必須是 $O(N)$。
*   **Hint:** Put all numbers in a HashSet. Iterate array. Only start counting sequence if `num - 1` is NOT in the set (this ensures you start at the beginning of a sequence).
*   **提示：** 將所有數字放入 HashSet。遍歷陣列。只有當 `num - 1` **不在** Set 中時才開始計算序列（這確保你從序列的開頭開始）。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] Did I handle `null` or empty array inputs? (我有處理 `null` 或空陣列輸入嗎？)
*   [ ] Did I clarify if the array contains negative numbers? (我有釐清陣列是否包含負數嗎？)
*   [ ] Is my Hash Key unique and immutable? (我的 Hash Key 是唯一且不可變的嗎？)
*   [ ] Did I use `equals()` for objects/strings instead of `==`? (我是否對物件/字串使用了 `equals()` 而非 `==`？)

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **Hash Map as a "Valet Parking Service" (代客泊車服務):**
    You give them a ticket (Key), they get your car (Value). You don't care *where* it's parked, just that you get it back instantly.
    **雜湊表就像「代客泊車」：** 你給他們票根（Key），他們取回你的車（Value）。你不在乎車停在*哪裡*，只在乎能立刻取回。

*   **Space-Time Trade-off:**
    "Buying a bigger desk (Space) so you don't have to walk to the filing cabinet (Time)."
    **時空權衡：** 「買一張更大的桌子（空間），這樣你就不用一直走到檔案櫃（時間）。」