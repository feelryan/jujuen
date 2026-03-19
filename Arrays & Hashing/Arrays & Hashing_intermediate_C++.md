Here is a comprehensive guide tailored for a Senior Software Engineer, focusing on **Arrays & Hashing**.
這是一份專為資深軟體工程師量身打造的指南，重點在於 **陣列與雜湊（Arrays & Hashing）**。

---

# Arrays & Hashing: Intermediate to Advanced Guide
# 陣列與雜湊：中階至進階指南

## 1. Learning Objectives (學習目標)

*   **Master the Space-Time Trade-off:** Understand when to sacrifice memory (using Hash Maps) to reduce time complexity from $O(N^2)$ to $O(N)$.
    **掌握空間換取時間的權衡：** 理解何時該犧牲記憶體（使用雜湊表）將時間複雜度從 $O(N^2)$ 降低至 $O(N)$。
*   **Deep Dive into C++ STL Containers:** Differentiate between `std::vector`, `std::map`, and `std::unordered_map` specifically regarding internal implementation and performance implications.
    **深入 C++ STL 容器：** 區分 `std::vector`、`std::map` 與 `std::unordered_map`，特別是關於內部實作與效能的影響。
*   **Handle Edge Cases & Collisions:** Learn to identify boundary conditions (empty inputs, duplicates) and understand how hash collisions affect worst-case performance.
    **處理邊界情況與碰撞：** 學習識別邊界條件（空輸入、重複值），並理解雜湊碰撞如何影響最差情況的效能。
*   **Pattern Recognition:** Instantly recognize problems solvable by Frequency Counting, Prefix Sums, or Anagram grouping.
    **模式識別：** 能夠立即辨識出可透過頻率計數、前綴和或變位詞分組來解決的問題。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Arrays (Fixed-size / Dynamic) | 陣列（固定大小 / 動態）
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 儲存在連續記憶體位置的元素集合。
*   **Intuition:** Think of a row of numbered lockers; you can jump to locker #5 instantly.
    **直覺：** 想像一排有編號的置物櫃；你可以瞬間跳到第 5 號櫃子。
*   **Senior Insight:** In C++, `std::vector` guarantees contiguous memory, which is crucial for CPU cache locality and prefetching performance.
    **資深觀點：** 在 C++ 中，`std::vector` 保證連續記憶體，這對 CPU 快取局部性與預取效能至關重要。

### Hashing (Hash Table) | 雜湊（雜湊表）
*   **Definition:** A data structure that maps keys to values using a hash function to compute an index.
    **定義：** 一種資料結構，利用雜湊函數計算索引，將鍵（Key）映射到值（Value）。
*   **Intuition:** A library index card system; you look up a book title and get its exact shelf location immediately.
    **直覺：** 圖書館的索引卡系統；你查閱書名，便能立即得知其確切的書架位置。
*   **Complexity:** Average $O(1)$ for insertion/lookup; Worst case $O(N)$ (collisions).
    **複雜度：** 平均插入/查詢為 $O(1)$；最差情況為 $O(N)$（發生碰撞）。
*   **C++ Specific:** `std::unordered_map` uses a Hash Table (Average $O(1)$), while `std::map` uses a Red-Black Tree (Always $O(\log N)$). Use `unordered_map` unless order matters.
    **C++ 特性：** `std::unordered_map` 使用雜湊表（平均 $O(1)$），而 `std::map` 使用紅黑樹（總是 $O(\log N)$）。除非需要排序，否則應使用 `unordered_map`。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Frequency Map / Counter (頻率表 / 計數器):**
    *   Used to count occurrences of elements (e.g., Valid Anagram, Top K Frequent).
    *   用於計算元素出現的次數（例如：驗證變位詞、前 K 個高頻元素）。
2.  **Index Mapping / Hashing Key (索引映射 / 雜湊鍵):**
    *   Using the array index as a hash key (e.g., First Missing Positive) or transforming an object into a string key.
    *   將陣列索引作為雜湊鍵（例如：第一個缺失的正數），或將物件轉換為字串鍵。
3.  **Prefix Sum (前綴和):**
    *   Pre-calculating sums to answer range queries in $O(1)$ (e.g., Range Sum Query, Subarray Sum Equals K).
    *   預先計算總和，以便在 $O(1)$ 時間內回答範圍查詢（例如：範圍和查詢、子陣列和等於 K）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Group Anagrams (LeetCode 49)
### 問題：變位詞分組

**Problem Statement:**
Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.
給定一個字串陣列 `strs`，將變位詞（由相同字母重組而成的單字）分組在一起。你可以按任何順序返回答案。

**Example:**
Input: `["eat","tea","tan","ate","nat","bat"]`
Output: `[["bat"],["nat","tan"],["ate","eat","tea"]]`

---

### Phase 1: Brute Force Approach (暴力解法)

**Idea:** For every string, compare it with every other string to check if they are anagrams.
**思路：** 針對每個字串，與其他所有字串比較，檢查它們是否為變位詞。

*   **Complexity:** $O(N^2 \cdot K \log K)$ or $O(N^2 \cdot K)$, where $N$ is number of strings, $K$ is max string length.
    **複雜度：** $O(N^2 \cdot K \log K)$ 或 $O(N^2 \cdot K)$，其中 $N$ 是字串數量，$K$ 是最大字串長度。
*   **Why it fails:** Too slow for large $N$.
    **為何失敗：** 當 $N$ 很大時太慢。

---

### Phase 2: Optimal Approach with Hashing (最佳雜湊解法)

**Idea:** Two strings are anagrams if and only if their sorted characters are identical. We can use this sorted string as a **Key** in a Hash Map.
**思路：** 當且僅當兩個字串排序後的字元完全相同時，它們才是變位詞。我們可以使用這個排序後的字串作為雜湊表中的 **鍵（Key）**。

**Algorithm:**
1.  Initialize `unordered_map<string, vector<string>>`.
    初始化 `unordered_map<string, vector<string>>`。
2.  Iterate through each string.
    遍歷每個字串。
3.  Sort the string to generate the key (e.g., "tea" -> "aet").
    將字串排序以生成鍵（例如："tea" -> "aet"）。
4.  Append original string to the map entry.
    將原始字串加入對應的映射條目中。

**Complexity (複雜度):**
*   **Time:** $O(N \cdot K \log K)$ (Sorting each string takes $K \log K$, done $N$ times).
    **時間：** $O(N \cdot K \log K)$（排序每個字串需 $K \log K$，共執行 $N$ 次）。
*   **Space:** $O(N \cdot K)$ (To store all strings in the map).
    **空間：** $O(N \cdot K)$（用於在映射表中儲存所有字串）。

---

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>

class Solution {
public:
    std::vector<std::vector<std::string>> groupAnagrams(std::vector<std::string>& strs) {
        // Map to store sorted string as key and list of anagrams as value
        // 用於儲存排序後字串作為鍵，變位詞列表作為值的映射表
        std::unordered_map<std::string, std::vector<std::string>> map;

        // Optimization: Reserve space if N is large to avoid rehashing (optional but "Senior")
        // 優化：如果 N 很大，預留空間以避免重新雜湊（選用，但展現資深水準）
        map.reserve(strs.size());

        for (const auto& s : strs) { // Use const reference to avoid copying | 使用常數引用避免複製
            std::string key = s;
            
            // Sort the key to canonicalize the anagram | 排序鍵值以規範化變位詞
            std::sort(key.begin(), key.end());
            
            // Insert original string into the corresponding vector | 將原始字串插入對應的向量中
            // operator[] creates a new vector if key doesn't exist | operator[] 若鍵不存在會建立新向量
            map[key].emplace_back(s); 
        }

        // Prepare the result structure | 準備結果結構
        std::vector<std::vector<std::string>> result;
        result.reserve(map.size());

        // Iterate through the map and move vectors to result | 遍歷映射表並將向量移動到結果中
        for (auto& pair : map) {
            // Use std::move to transfer ownership without copying | 使用 std::move 轉移所有權而不複製
            result.emplace_back(std::move(pair.second));
        }

        return result;
    }
};
```

---

### Advanced Optimization Note (進階優化註記)
Instead of sorting ($K \log K$), you can create a key based on character counts (e.g., "1#0#2#..." for a, b, c counts). This makes complexity $O(N \cdot K)$.
不使用排序（$K \log K$），你可以根據字元計數建立鍵（例如："1#0#2#..." 代表 a, b, c 的數量）。這將複雜度降低為 $O(N \cdot K)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **`map` vs `unordered_map`** | `map` is a Tree ($O(\log n)$), sorted keys. `unordered_map` is Hash Table ($O(1)$). **Pitfall:** Using `map` when order is irrelevant slows down the code. <br> `map` 是樹（$O(\log n)$），鍵有序。`unordered_map` 是雜湊表（$O(1)$）。**陷阱：** 在不需要排序時使用 `map` 會拖慢程式碼。 |
| **Array Index Out of Bounds** | Accessing `arr[n]` instead of `arr[n-1]`. **Pitfall:** Often happens in loops or when using calculated hash indices. <br> 存取 `arr[n]` 而非 `arr[n-1]`。**陷阱：** 常發生在迴圈或使用計算出的雜湊索引時。 |
| **Hash Collisions** | When two different keys produce the same hash. **Pitfall:** Assuming $O(1)$ is guaranteed. In a bad scenario (e.g., all keys hash to 0), it degrades to $O(N)$. <br> 當兩個不同的鍵產生相同的雜湊值。**陷阱：** 假設 $O(1)$ 是絕對保證的。在糟糕的情況下（如所有鍵都雜湊為 0），會退化為 $O(N)$。 |
| **Iterator Invalidation** | Modifying a container (adding elements to a vector/map) while iterating over it. **Pitfall:** Causes undefined behavior or crashes. <br> 在遍歷容器時修改它（向 vector/map 新增元素）。**陷阱：** 導致未定義行為或崩潰。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are the inputs only lowercase English letters? Can the array be empty?"
    **釐清限制：** 「輸入是否僅包含小寫英文字母？陣列可能為空嗎？」
2.  **State the Naive Solution:** "I could sort every string, but that would be $O(N \cdot K \log K)$."
    **陳述樸素解法：** 「我可以排序每個字串，但那會是 $O(N \cdot K \log K)$。」
3.  **Propose Optimization:** "To optimize, I'll use a Hash Map to group them in linear time relative to the input size."
    **提出優化：** 「為了優化，我將使用雜湊表，以相對於輸入大小的線性時間將它們分組。」
4.  **Discuss Trade-offs:** "This uses more space to store the map, but significantly improves runtime."
    **討論權衡：** 「這會使用更多空間來儲存映射表，但顯著改善執行時間。」

### Whiteboard Strategy (白板策略)
*   **Define Types Clearly:** Write `unordered_map<string, vector<string>>` early to show you know the data structure.
    **清晰定義型別：** 儘早寫下 `unordered_map<string, vector<string>>` 以顯示你了解該資料結構。
*   **Use Helper Functions:** If the key generation logic is complex, abstract it: `string getKey(string s) { ... }`.
    **使用輔助函數：** 如果鍵生成邏輯很複雜，將其抽象化：`string getKey(string s) { ... }`。

### Common Follow-ups (常見追問)
*   **Q:** What if the inputs are too large to fit in memory?
    **問：** 如果輸入太大無法放入記憶體怎麼辦？
*   **A:** Discuss **External Sort** or **MapReduce**. We would hash strings to different chunks/shards on disk, then process each shard individually.
    **答：** 討論 **外部排序** 或 **MapReduce**。我們會將字串雜湊到磁碟上的不同區塊/分片，然後單獨處理每個分片。

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (LeetCode 217)
*   **Problem:** Return true if any value appears at least twice.
    **問題：** 如果任何值出現至少兩次，則返回 true。
*   **Hint:** Use `std::unordered_set`. If `set.find(x)` is not `end()`, return true.
    **提示：** 使用 `std::unordered_set`。如果 `set.find(x)` 不是 `end()`，返回 true。

### 2. Medium: Top K Frequent Elements (LeetCode 347)
*   **Problem:** Return the $k$ most frequent elements.
    **問題：** 返回 $k$ 個出現頻率最高的元素。
*   **Hint:**
    1. Count frequency with `unordered_map`.
    2. Use a "Bucket Sort" approach (array where index is frequency) OR a Min-Heap of size $k$.
    **提示：**
    1. 用 `unordered_map` 計算頻率。
    2. 使用「桶排序」方法（索引為頻率的陣列）或大小為 $k$ 的最小堆積（Min-Heap）。

### 3. Hard: Longest Consecutive Sequence (LeetCode 128)
*   **Problem:** Find the length of the longest consecutive elements sequence in an unsorted array. $O(N)$ required.
    **問題：** 在未排序陣列中找出最長連續元素序列的長度。要求 $O(N)$。
*   **Hint:**
    1. Put all numbers in a `unordered_set`.
    2. Iterate through the set. Only start counting if `num - 1` does **not** exist (meaning `num` is the start of a sequence).
    **提示：**
    1. 將所有數字放入 `unordered_set`。
    2. 遍歷集合。只有當 `num - 1` **不**存在時才開始計數（這意味著 `num` 是序列的起點）。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] Did I handle the **empty array** case?
    我是否處理了 **空陣列** 的情況？
*   [ ] Did I use references (`const auto&`) in loops to avoid copying strings/vectors?
    我是否在迴圈中使用了引用（`const auto&`）以避免複製字串/向量？
*   [ ] Did I confuse `map` (ordered) with `unordered_map` (hashed)?
    我是否混淆了 `map`（有序）與 `unordered_map`（雜湊）？
*   [ ] Is my custom Hash Key unique enough to avoid logic errors?
    我的自定義雜湊鍵是否足夠獨特以避免邏輯錯誤？
*   [ ] Complexity check: Is it truly $O(N)$ or did I hide a loop inside a library call?
    複雜度檢查：這真的是 $O(N)$ 嗎，還是我在函式庫調用中隱藏了一個迴圈？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Array = Hotel Corridor (陣列 = 飯店走廊):**
    *   Rooms are next to each other. You know exactly where Room 105 is relative to 100. Fast to walk (cache locality).
    *   房間彼此相鄰。你確切知道 105 號房相對於 100 號房的位置。走起來很快（快取局部性）。

*   **Hash Map = Coat Check (雜湊表 = 衣帽間):**
    *   You give a ticket (Key), they use a system to find the hook (Hash Function). Usually instant. Sometimes two coats get put on the same hook (Collision), and it takes a moment to find yours.
    *   你給出一張票（鍵），他們使用系統找到掛鉤（雜湊函數）。通常是即時的。有時兩件外套掛在同一個鉤子上（碰撞），需要一點時間找到你的。