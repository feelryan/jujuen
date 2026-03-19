Here is the comprehensive guide for **Arrays & Hashing**, tailored for a Senior Software Engineer, following the requested bilingual format and Java implementation.

這是針對 **Arrays & Hashing（陣列與雜湊）** 的完整教材，專為資深軟體工程師量身打造，遵循要求的雙語格式與 Java 實作。

---

# Arrays & Hashing Masterclass (Intermediate)
# 陣列與雜湊大師班（中階）

## 1. Learning Goals (學習目標)

*   **Master the trade-offs between Time and Space complexity using Hash Maps.**
    掌握使用雜湊表（Hash Maps）在時間與空間複雜度之間的權衡。
*   **Understand Java-specific data structure nuances (e.g., `ArrayList` resizing, `HashMap` collision handling).**
    理解 Java 特有的資料結構細節（例如 `ArrayList` 的動態擴容、`HashMap` 的碰撞處理）。
*   **Apply Prefix Sum and Hashing techniques to optimize range queries and lookups.**
    應用前綴和（Prefix Sum）與雜湊技術來優化區間查詢與查找操作。
*   **Transition from brute-force to optimal solutions by identifying "repeated work" that can be cached.**
    藉由識別可被快取的「重複工作」，從暴力解過渡到最佳解。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
*   **Array:** A collection of elements identified by index or key, stored in contiguous memory locations.
    **陣列：** 一組由索引或鍵識別的元素，儲存在連續的記憶體位置中。
*   **Hash Map:** A structure that maps keys to values using a hash function to compute an index into an array of buckets.
    **雜湊表：** 一種將鍵映射到值的結構，使用雜湊函數計算索引並指向桶陣列（buckets）中的位置。

### Intuition (直覺)
*   **Array:** Think of a row of numbered mailboxes; you know exactly where mailbox #5 is.
    **陣列：** 想像一排編號的信箱；你確切知道 5 號信箱在哪裡。
*   **Hash Map:** Think of a library index system; you look up a book title (Key) to find its shelf location (Value) instantly.
    **雜湊表：** 想像圖書館的索引系統；你查詢書名（鍵）以立即找到它的書架位置（值）。

### Complexity (複雜度)

| Operation | Array (Static) | ArrayList (Dynamic) | Hash Map (Avg) | Hash Map (Worst) |
| :--- | :--- | :--- | :--- | :--- |
| Access | $O(1)$ | $O(1)$ | $O(1)$ | $O(N)$ |
| Search | $O(N)$ | $O(N)$ | $O(1)$ | $O(N)$ |
| Insertion | N/A (Fixed) | $O(1)^*$ | $O(1)$ | $O(N)$ |
| Deletion | N/A (Fixed) | $O(N)$ | $O(1)$ | $O(N)$ |

*\* Amortized time (攤提時間)*

### When to Use / Not to Use (適用與不適用場景)

*   **Use Arrays when:** You need ordered data, fast iteration, or fixed-size collections.
    **使用陣列的時機：** 當你需要有序資料、快速迭代或固定大小的集合時。
*   **Use Hash Maps when:** You need $O(1)$ lookups, counting frequencies, or checking for existence.
    **使用雜湊表的時機：** 當你需要 $O(1)$ 查找、計算頻率或檢查存在性時。
*   **Avoid Hash Maps when:** You need to maintain order (unless using `LinkedHashMap`) or handle duplicate keys (requires special handling).
    **避免使用雜湊表的時機：** 當你需要維持順序（除非使用 `LinkedHashMap`）或處理重複的鍵（需要特殊處理）時。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Frequency Counter (頻率計數器):**
    Using a Hash Map to count occurrences of elements.
    使用雜湊表來計算元素的出現次數。
    *(e.g., Valid Anagram, Top K Frequent Elements)*

2.  **Two Pointers / Index Mapping (雙指標 / 索引映射):**
    Using a Map to store `value -> index` to solve pair problems in one pass.
    使用 Map 儲存 `數值 -> 索引`，以便在一次遍歷中解決配對問題。
    *(e.g., Two Sum)*

3.  **Prefix Sum (前綴和):**
    Pre-calculating cumulative sums to answer range queries in $O(1)$.
    預先計算累積和，以便在 $O(1)$ 時間內回答區間查詢。
    *(e.g., Range Sum Query, Subarray Sum Equals K)*

4.  **Grouping by Key (依鍵分組):**
    Categorizing items based on a canonical form (sorted string, count array).
    根據標準形式（排序後的字串、計數陣列）將項目分類。
    *(e.g., Group Anagrams)*

---

## 4. Example Walkthrough (範例講解)

### Problem: Group Anagrams (群組異位詞)

**Problem Statement:**
Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.
給定一個字串陣列 `strs`，將異位詞（由相同字母重組而成的單字）分組在一起。你可以按任何順序返回答案。

**Example:**
Input: `["eat","tea","tan","ate","nat","bat"]`
Output: `[["bat"],["nat","tan"],["ate","eat","tea"]]`

---

### Strategy (思路)

**1. Brute Force (暴力法):**
Iterate through every string and compare it with every other string to check if they are anagrams.
遍歷每個字串，並將其與所有其他字串進行比較，檢查它們是否為異位詞。
*   **Complexity:** $O(N^2 \cdot K \log K)$ or $O(N^2 \cdot K)$ depending on comparison method. (Too slow).
*   **複雜度：** $O(N^2 \cdot K \log K)$ 或 $O(N^2 \cdot K)$，取決於比較方法。（太慢）。

**2. Optimization 1: Sorting as Key (優化一：排序作為鍵):**
Two strings are anagrams if they look the same when sorted. Use the sorted string as the Key in a HashMap.
如果兩個字串排序後看起來相同，它們就是異位詞。使用排序後的字串作為 HashMap 中的鍵。
*   **Complexity:** $O(N \cdot K \log K)$, where $N$ is number of strings, $K$ is max length of a string.
*   **複雜度：** $O(N \cdot K \log K)$，其中 $N$ 是字串數量，$K$ 是字串最大長度。

**3. Optimization 2: Character Count as Key (優化二：字元計數作為鍵):**
Instead of sorting, count the frequency of each character (a-z). Use this count signature as the Key.
不進行排序，而是計算每個字元（a-z）的頻率。使用此計數特徵作為鍵。
*   **Complexity:** $O(N \cdot K)$. This is optimal because sorting takes $O(K \log K)$, but counting takes only $O(K)$.
*   **複雜度：** $O(N \cdot K)$。這是最佳解，因為排序需要 $O(K \log K)$，但計數只需要 $O(K)$。

---

### Java Reference Solution (Java 參考解)

```java
import java.util.*;

public class GroupAnagrams {
    public List<List<String>> groupAnagrams(String[] strs) {
        // Edge case: empty input
        // 邊界情況：空輸入
        if (strs == null || strs.length == 0) {
            return new ArrayList<>();
        }

        // Map to store the grouping key and the list of corresponding strings
        // Map 用於儲存分組鍵以及對應的字串列表
        Map<String, List<String>> map = new HashMap<>();

        for (String s : strs) {
            // Create a frequency array for 26 lowercase letters
            // 為 26 個小寫字母建立頻率陣列
            char[] count = new char[26];
            
            for (char c : s.toCharArray()) {
                count[c - 'a']++;
            }

            // Convert the count array to a unique string key
            // Ideally, we need a delimiter to ensure uniqueness, but for char counts, 
            // String.valueOf(char[]) works because it treats counts as chars. 
            // However, a more robust way for generic cases is Arrays.toString() or a StringBuilder with delimiters.
            // 將計數陣列轉換為唯一的字串鍵
            // 理想情況下，我們需要分隔符以確保唯一性，但對於 char 計數，
            // String.valueOf(char[]) 是可行的。
            // 然而，對於通用情況，更穩健的方法是使用 Arrays.toString() 或帶分隔符的 StringBuilder。
            
            // Using String.valueOf(count) is a specific optimization for this problem 
            // (assuming counts fit in char range). Let's use a safer approach for interview clarity.
            // 使用 String.valueOf(count) 是針對此問題的特定優化。
            // 為了面試清晰度，我們使用更安全的方法。
            
            String key = Arrays.toString(count); 
            // Key example: "[1, 0, 0, ... 1]" for "ac...z"
            
            // If key doesn't exist, initialize new list
            // 如果鍵不存在，初始化新列表
            map.putIfAbsent(key, new ArrayList<>());
            
            // Add the original string to the correct group
            // 將原始字串加入正確的群組
            map.get(key).add(s);
        }

        // Return all values from the map
        // 返回 map 中的所有值
        return new ArrayList<>(map.values());
    }
}
```

### Common Mistakes in this Problem (此題常見錯誤)

1.  **Using Array as Map Key:** In Java, arrays do not override `equals()` and `hashCode()`. Using `int[]` directly as a key will rely on reference equality, failing to group correctly. You must convert it to a String or a List.
    **將陣列作為 Map 的鍵：** 在 Java 中，陣列沒有覆寫 `equals()` 和 `hashCode()`。直接使用 `int[]` 作為鍵會依賴引用相等性（reference equality），導致分組失敗。你必須將其轉換為 String 或 List。
2.  **Complexity Analysis:** Forgetting that string sorting is $O(K \log K)$ inside the loop.
    **複雜度分析：** 忘記迴圈內的字串排序是 $O(K \log K)$。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept | Pitfall / Nuance (陷阱 / 細節) |
| :--- | :--- |
| **Java `HashMap` Keys** | Mutable objects should generally **not** be used as keys. If the object changes, its hashCode changes, and you lose the value. <br> **Java `HashMap` 的鍵：** 可變物件通常**不應**用作鍵。如果物件改變，其 hashCode 也會改變，你會丟失該值。 |
| **`Array` vs `ArrayList`** | `int[]` is a primitive array (fast, fixed). `ArrayList<Integer>` involves boxing/unboxing overhead. <br> **`Array` 與 `ArrayList`：** `int[]` 是原始陣列（快、固定）。`ArrayList<Integer>` 涉及裝箱/拆箱的開銷。 |
| **Collision Handling** | Java 8+ uses a balanced tree (Red-Black Tree) instead of a linked list for buckets when collisions exceed a threshold (8), improving worst-case from $O(N)$ to $O(\log N)$. <br> **碰撞處理：** 當碰撞超過閾值（8）時，Java 8+ 使用平衡樹（紅黑樹）代替鏈結串列，將最差情況從 $O(N)$ 改善為 $O(\log N)$。 |
| **`contains` Method** | `ArrayList.contains()` is $O(N)$. `HashSet.contains()` is $O(1)$. Don't use List for lookups inside a loop! <br> **`contains` 方法：** `ArrayList.contains()` 是 $O(N)$。`HashSet.contains()` 是 $O(1)$。不要在迴圈中使用 List 進行查找！ |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
*   **Clarify:** "Are the inputs only lowercase English letters? Can the input be empty?"
    **釐清：** 「輸入是否僅包含小寫英文字母？輸入可以是空的嗎？」
*   **Propose:** "I will use a Hash Map to group the data. The key will be the character count signature."
    **提議：** 「我將使用雜湊表來分組資料。鍵將是字元計數特徵。」
*   **Analyze:** "The time complexity will be $O(N \cdot K)$ because we iterate each string once."
    **分析：** 「時間複雜度將是 $O(N \cdot K)$，因為我們遍歷每個字串一次。」

### Whiteboard Strategy (白板策略)
*   Write the **Type Signature** first (e.g., `public List<List<String>> solve(String[] strs)`).
    首先寫下**型別簽章**。
*   Define the **Map** clearly with generics (`Map<String, List<String>>`).
    清楚地定義帶有泛型的 **Map**。
*   Handle **Edge Cases** (null/empty) at the very top.
    在最上方處理**邊界情況**（null/空）。

### Common Follow-up (常見追問)
*   **Q:** "What if the dataset is too large to fit in memory?"
    **問：** 「如果資料集太大而無法放入記憶體怎麼辦？」
*   **A:** "We can use **External Sort** or **MapReduce**. We would hash each string to a specific shard/file based on its signature, then process each shard individually."
    **答：** 「我們可以使用**外部排序**或 **MapReduce**。我們可以根據字串的特徵將其雜湊到特定的分片/檔案，然後單獨處理每個分片。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (存在重複元素)
*   **Prompt:** Given an integer array, return true if any value appears at least twice.
    **題目：** 給定一個整數陣列，如果任何數值出現至少兩次，則返回 true。
*   **Hint:** Use a `HashSet` to store seen elements. Return true immediately if `add()` returns false (or check `contains`).
    **提示：** 使用 `HashSet` 儲存看過的元素。如果 `add()` 返回 false（或檢查 `contains`），則立即返回 true。

### 2. Medium: Top K Frequent Elements (前 K 個高頻元素)
*   **Prompt:** Given an integer array `nums` and an integer `k`, return the `k` most frequent elements.
    **題目：** 給定一個整數陣列 `nums` 和一個整數 `k`，返回出現頻率最高的 `k` 個元素。
*   **Hint:**
    1. Count frequency with HashMap ($O(N)$).
    2. Use a Bucket Sort (Array of Lists) where index represents frequency ($O(N)$).
    3. Alternatively, use a Min-Heap ($O(N \log k)$). Bucket sort is preferred for $O(N)$.
    **提示：**
    1. 用 HashMap 計算頻率 ($O(N)$)。
    2. 使用桶排序（List 的陣列），其中索引代表頻率 ($O(N)$)。
    3. 或者，使用最小堆積 ($O(N \log k)$)。為了 $O(N)$，首選桶排序。

### 3. Hard (Conceptual): Longest Consecutive Sequence (最長連續序列)
*   **Prompt:** Given an unsorted array of integers, find the length of the longest consecutive elements sequence. Must be $O(N)$.
    **題目：** 給定一個未排序的整數陣列，找出最長連續元素序列的長度。必須是 $O(N)$。
*   **Hint:** Put all numbers in a `HashSet`. Iterate through the set. Only start counting a sequence if `num - 1` is **not** in the set (this ensures you only start from the beginning of a sequence).
    **提示：** 將所有數字放入 `HashSet`。遍歷該集合。只有當 `num - 1` **不在**集合中時才開始計算序列（這確保你只從序列的開頭開始）。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Null Checks:** Did I handle `null` input or empty arrays?
    **空值檢查：** 我是否處理了 `null` 輸入或空陣列？
*   [ ] **Map Methods:** Did I use `getOrDefault` or `putIfAbsent` to make code cleaner?
    **Map 方法：** 我是否使用了 `getOrDefault` 或 `putIfAbsent` 來讓程式碼更簡潔？
*   [ ] **Key Uniqueness:** If using a custom object or array as a key, did I convert it to a String or override `hashCode/equals`?
    **鍵的唯一性：** 如果使用自訂物件或陣列作為鍵，我是否將其轉換為 String 或覆寫了 `hashCode/equals`？
*   [ ] **Loop Bounds:** Did I access index `i+1` or `i-1` without checking bounds?
    **迴圈邊界：** 我是否在未檢查邊界的情況下存取了索引 `i+1` 或 `i-1`？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **Hash Map is a Coat Check:** You give a ticket (Key), you get your specific coat (Value). You don't search through all coats.
    **雜湊表是衣帽間寄物：** 你給出一張票（鍵），你拿回你特定的外套（值）。你不需要搜尋所有的外套。
*   **Array is a Ruler:** Fixed length, markings are at equal distances. You can jump to 5cm instantly, but you can't stretch the ruler easily.
    **陣列是一把尺：** 固定長度，刻度距離相等。你可以立即跳到 5 公分處，但你無法輕易拉長這把尺。
*   **Anagrams are Lego Sets:** "eat" and "tea" are different structures built with the exact same Lego bricks (counts).
    **異位詞是樂高組：** "eat" 和 "tea" 是用完全相同的樂高積木（計數）構建的不同結構。