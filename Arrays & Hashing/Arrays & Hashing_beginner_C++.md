Here is the comprehensive guide for **Arrays & Hashing**, tailored for a Senior Software Engineer, focusing on the **Beginner** level (Foundational Mastery) using **C++**.

這是一份針對 **Arrays & Hashing** 的完整指南，專為資深軟體工程師量身打造，聚焦於 **初階（Beginner）** 層級（基礎精通），並使用 **C++** 撰寫。

---

# Module: Arrays & Hashing (Foundational Mastery)
# 模組：陣列與雜湊（基礎精通）

## 1. Learning Goals (學習目標)

*   **Master C++ STL Containers:** Deeply understand the internal implementation and performance characteristics of `std::vector` and `std::unordered_map`.
    **精通 C++ STL 容器：** 深入理解 `std::vector` 與 `std::unordered_map` 的內部實作與效能特性。
*   **Space-Time Trade-off:** Learn to intuitively trade $O(n)$ space for $O(1)$ lookup time to optimize brute-force solutions.
    **時空權衡：** 學習直覺地利用 $O(n)$ 的空間換取 $O(1)$ 的查詢時間，以優化暴力解法。
*   **Handling Edge Cases:** Develop a reflex for handling empty inputs, duplicates, and collisions in hashing.
    **處理邊界情況：** 培養處理空輸入、重複值以及雜湊碰撞的直覺反應。

---

## 2. Core Concepts (核心觀念速覽)

### Array (std::vector)
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 儲存於連續記憶體位置的元素集合。
*   **Intuition:** Think of it as a row of numbered mailboxes; you can jump to any box instantly if you know the index.
    **直覺：** 把它想像成一排有編號的信箱；如果你知道索引，就能瞬間跳轉到任何一個信箱。
*   **Complexity (複雜度):**
    *   Access (存取): $O(1)$
    *   Search (搜尋): $O(n)$ (unsorted), $O(\log n)$ (sorted + binary search)
    *   Insert/Delete (插入/刪除): $O(n)$ (due to shifting elements / 因為需要移動元素)
*   **When to use:** When index-based access is frequent or memory locality (cache friendliness) is critical.
    **適用場景：** 當頻繁使用索引存取，或記憶體局部性（快取友善度）至關重要時。

### Hashing (std::unordered_map / std::unordered_set)
*   **Definition:** A technique to map data of arbitrary size to fixed-size values (keys) using a hash function.
    **定義：** 使用雜湊函數將任意大小的資料映射到固定大小的值（鍵）的技術。
*   **Intuition:** Like a library filing system where a book's title determines exactly which shelf it belongs to, avoiding a full scan.
    **直覺：** 就像圖書館的歸檔系統，書名決定了它屬於哪個架子，避免了全面掃描。
*   **Complexity (複雜度):**
    *   Access/Search/Insert/Delete: $O(1)$ *Amortized (平均攤銷)*.
    *   Worst Case: $O(n)$ (due to collisions / 因為碰撞).
*   **When to use:** When you need fast lookups to check for existence or track frequency.
    **適用場景：** 當你需要快速查詢以檢查存在性或追蹤頻率時。

---

## 3. Typical Patterns (典型題型 / 模式)

Even at the beginner level, these patterns are the building blocks for hard problems.
即使在初階層級，這些模式也是解決困難問題的基石。

1.  **Frequency Map (頻率表):**
    Using a hash map to count occurrences of elements.
    使用雜湊表來計算元素的出現次數。
    *   *Target:* Anagrams, Majority Element.
2.  **Index Mapping (索引映射):**
    Storing `Value -> Index` in a map to look up previous elements instantly.
    在雜湊表中儲存 `數值 -> 索引`，以便瞬間查詢之前的元素。
    *   *Target:* Two Sum.
3.  **Fixed-Size Array as Hash (固定陣列作為雜湊):**
    Using `int[26]` instead of a map for character counts to save overhead.
    使用 `int[26]` 代替雜湊表來計算字元數，以節省開銷。
    *   *Target:* String manipulation.

---

## 4. Example Walkthrough (範例講解)

### Problem: Two Sum (兩數之和)
**Problem Statement:** Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `target`，返回兩個數字的索引，使它們的總和等於 `target`。

#### 1. Brute Force (暴力法)
Iterate through every pair of numbers.
遍歷每一對數字。
*   **Complexity:** Time $O(n^2)$ | Space $O(1)$.
*   **Verdict:** Acceptable for junior roles, but a Senior Engineer must skip this or mention it only as a baseline.
    **結論：** 初階職位可接受，但資深工程師應跳過此法，或僅將其作為基準提及。

#### 2. Optimal Approach: Hash Map (最佳解：雜湊表)
**Logic:** As we iterate, for each element `x`, we check if `target - x` exists in our map.
**思路：** 當我們遍歷時，對於每個元素 `x`，我們檢查 `target - x` 是否存在於我們的雜湊表中。
*   If yes, we found the pair.
    如果是，我們就找到了這對數字。
*   If no, we store `x` and its index in the map for future checks.
    如果否，我們將 `x` 及其索引存入表中，供日後檢查。

**Complexity:** Time $O(n)$ | Space $O(n)$.

#### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <unordered_map>

class Solution {
public:
    // Function to find two indices that sum up to target
    // 找出總和為 target 的兩個索引的函數
    std::vector<int> twoSum(std::vector<int>& nums, int target) {
        // Map to store value -> index mapping
        // 用於儲存 數值 -> 索引 映射的雜湊表
        std::unordered_map<int, int> prevMap; 

        for (int i = 0; i < nums.size(); i++) {
            int diff = target - nums[i];

            // Check if the complement (diff) exists in the map
            // 檢查補數 (diff) 是否存在於雜湊表中
            if (prevMap.find(diff) != prevMap.end()) {
                // Return the index of the complement and current index
                // 返回補數的索引與當前索引
                return {prevMap[diff], i};
            }

            // Store current number and its index
            // 儲存當前數字及其索引
            prevMap[nums[i]] = i;
        }
        
        // Return empty vector if no solution found (though problem guarantees one)
        // 若無解則返回空向量（儘管題目保證有解）
        return {};
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **std::map** | **std::unordered_map** | `map` is Tree-based ($O(\log n)$, sorted). `unordered_map` is Hash-based ($O(1)$, unsorted). Use `unordered` by default for interviews. <br> `map` 基於樹狀結構（$O(\log n)$，有序）。`unordered_map` 基於雜湊（$O(1)$，無序）。面試預設使用 `unordered`。 |
| **Array Resizing** | **Fixed Capacity** | `vector` resizing (doubling capacity) is $O(n)$ operation, though amortized $O(1)$. Pre-allocating with `reserve()` shows seniority. <br> `vector` 調整大小（容量倍增）是 $O(n)$ 操作，儘管攤銷後為 $O(1)$。使用 `reserve()` 預先分配能展現資深水準。 |
| **Key Existence** | **Value Access** | Using `map[key]` creates a default entry if the key doesn't exist. Use `map.find(key)` or `map.count(key)` to check existence without mutation. <br> 使用 `map[key]` 若鍵不存在會建立預設項目。使用 `map.find(key)` 或 `map.count(key)` 來檢查存在性而不修改內容。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (口條框架)
*   **Start with the Naive:** "The brute force way is to compare every pair, giving us $O(n^2)$."
    **從樸素解開始：** 「暴力解法是比較每一對數字，這會給我們 $O(n^2)$ 的複雜度。」
*   **Pivot to Optimization:** "However, we can trade space for time. By remembering what we've seen in a Hash Map, we can reduce lookups to $O(1)$."
    **轉向優化：** 「然而，我們可以用空間換取時間。透過在雜湊表中記住看過的數字，我們可以將查詢降至 $O(1)$。」
*   **Discuss Trade-offs:** "This increases space complexity to $O(n)$, which is acceptable given memory constraints."
    **討論權衡：** 「這會將空間複雜度增加到 $O(n)$，考慮到記憶體限制，這是可接受的。」

### Whiteboard Strategy (白板策略)
*   **Define Types Explicitly:** Don't just write `map`. Write `unordered_map<int, int>`. It shows C++ proficiency.
    **明確定義型別：** 不要只寫 `map`。寫 `unordered_map<int, int>`。這展現了 C++ 的熟練度。
*   **Dry Run:** Before coding, draw the array and the map state step-by-step for a small example (e.g., `[2, 7, 11, 15]`).
    **模擬執行：** 寫程式碼前，針對一個小範例（如 `[2, 7, 11, 15]`）畫出陣列與雜湊表的逐步狀態。

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (存在重複元素)
*   **Problem:** Return true if any value appears at least twice.
    **問題：** 如果任何數值出現至少兩次，則返回 true。
*   **Hint:** Compare `set.size()` vs `vector.size()` or iterate with a Hash Set.
    **提示：** 比較 `set.size()` 與 `vector.size()` 或使用雜湊集合遍歷。
*   **Key Concept:** `std::unordered_set`.

### 2. Medium: Valid Anagram (有效的異位詞)
*   **Problem:** Given strings `s` and `t`, return true if `t` is an anagram of `s`.
    **問題：** 給定字串 `s` 和 `t`，如果 `t` 是 `s` 的異位詞，則返回 true。
*   **Hint:** Use a frequency counter. Optimization: Use `int count[26]` instead of a generic map since inputs are likely lowercase English letters.
    **提示：** 使用頻率計數器。優化：由於輸入通常是小寫英文字母，使用 `int count[26]` 代替通用雜湊表。
*   **Key Concept:** Fixed-size array hashing.

### 3. Hard (for Beginner Module): Longest Consecutive Sequence (最長連續序列)
*   **Problem:** Given an unsorted array, find the length of the longest consecutive elements sequence. Must be $O(n)$.
    **問題：** 給定一個未排序陣列，找出最長連續元素序列的長度。必須是 $O(n)$。
*   **Hint:** Put all numbers in a `unordered_set`. Iterate through the set; only start counting if `num - 1` is **not** in the set (meaning `num` is the start of a sequence).
    **提示：** 將所有數字放入 `unordered_set`。遍歷集合；只有當 `num - 1` **不在** 集合中時才開始計數（這意味著 `num` 是序列的起點）。
*   **Key Concept:** Intelligent sequence building using Hashing.

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Corner Cases:** Did I handle empty arrays? Arrays with 1 element?
    **邊界情況：** 我是否處理了空陣列？只有一個元素的陣列？
*   [ ] **Collision Handling:** Did I assume Hash Map is always $O(1)$? (Mention worst case $O(n)$ to impress interviewer).
    **碰撞處理：** 我是否假設雜湊表總是 $O(1)$？（提及最差情況 $O(n)$ 以讓面試官印象深刻）。
*   [ ] **C++ Syntax:** Did I use `const vector<int>&` to avoid unnecessary copying in function arguments?
    **C++ 語法：** 我是否在函數參數中使用了 `const vector<int>&` 以避免不必要的複製？
*   [ ] **Index Bounds:** Did I check `i < nums.size()`?
    **索引邊界：** 我是否檢查了 `i < nums.size()`？

---

## 9. Memory Anchors (記憶錨點)

*   **The Hotel Receptionist (Hash Map):**
    Instead of knocking on every room door to find "Mr. Smith" (Array Search $O(n)$), you ask the receptionist who looks up the room number in a computer (Hash Map Lookup $O(1)$).
    **飯店櫃檯人員（雜湊表）：**
    與其敲每一間房門去找「史密斯先生」（陣列搜尋 $O(n)$），不如問櫃檯人員，他在電腦中查詢房號（雜湊表查詢 $O(1)$）。

*   **The Bucket (Hashing Collisions):**
    If multiple items map to the same "bucket", you have to dig through that specific bucket (Linked List/Chaining) to find the item, which takes time.
    **水桶（雜湊碰撞）：**
    如果多個物品映射到同一個「水桶」，你必須翻找那個特定的水桶（鏈結串列/鏈式法）才能找到物品，這需要時間。