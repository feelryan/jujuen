Here is the advanced training material for **Arrays & Hashing**, tailored for a Senior Software Engineer using C++.

---

# Advanced Arrays & Hashing Interview Guide
# 進階陣列與雜湊面試指南

**Topic (主題):** Arrays & Hashing (In-place Optimization & State Encoding)
**Level (難度):** Advanced (針對 7+ 年資深工程師)
**Language (語言):** C++

---

## 1. Learning Goals (學習目標)

1.  **Master Space Optimization:** Move beyond standard `unordered_map` usage to understand **In-place Hashing** (using the array indices as keys) to achieve $O(1)$ auxiliary space.
    **掌握空間優化：** 超越標準的 `unordered_map` 使用，理解 **原地雜湊**（使用陣列索引作為鍵值）以達到 $O(1)$ 的輔助空間。

2.  **State Encoding & Hashing Keys:** Learn how to hash complex states (like `vector<int>` or grid coordinates) into unique keys for efficient lookup.
    **狀態編碼與雜湊鍵：** 學習如何將複雜狀態（如 `vector<int>` 或網格座標）雜湊為唯一鍵值以進行高效查找。

3.  **Amortized Analysis:** Deeply understand why Hash Map operations are $O(1)$ on average but $O(N)$ in worst-case, and how to discuss this trade-off in system design contexts.
    **攤銷分析：** 深入理解為何雜湊表操作平均為 $O(1)$ 但最差情況為 $O(N)$，並學會如何在系統設計情境中討論此權衡。

4.  **Handling Concurrency & Scale:** (For Seniors) Briefly touch upon thread-safety of C++ containers and distributed hashing concepts (Consistent Hashing).
    **處理並發與規模：**（針對資深者）簡要探討 C++ 容器的執行緒安全性以及分散式雜湊概念（一致性雜湊）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Hashing (雜湊)
*   **Definition:** Mapping data of arbitrary size to fixed-size values (keys) for fast access.
    **定義：** 將任意大小的資料映射到固定大小的值（鍵），以便快速存取。
*   **Intuition:** Trading space for time; a "magical" array where indices can be anything.
    **直覺：** 以空間換取時間；一個索引可以是任何東西的「魔法」陣列。
*   **Complexity:** Insert/Delete/Search: Average $O(1)$, Worst $O(N)$ (collision).
    **複雜度：** 插入/刪除/搜尋：平均 $O(1)$，最差 $O(N)$（碰撞）。
*   **C++ Note:** `std::unordered_map` uses chaining. `std::map` uses Red-Black Tree ($O(\log N)$). Know the difference.
    **C++ 註記：** `std::unordered_map` 使用鏈結法。`std::map` 使用紅黑樹（$O(\log N)$）。務必區分兩者。

### In-place Hashing / Cyclic Sort (原地雜湊 / 循環排序)
*   **Concept:** If the array contains numbers in range $[1, N]$ (or $[0, N-1]$), the value itself implies its "correct" position (index).
    **觀念：** 如果陣列包含範圍 $[1, N]$（或 $[0, N-1]$）內的數字，該數值本身暗示了其「正確」位置（索引）。
*   **Application:** Finding missing numbers, duplicates, or specific constraints without extra space.
    **應用：** 在不使用額外空間的情況下尋找缺失數、重複數或特定限制。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Frequency Map / Counter (頻率表 / 計數器):**
    Using a hash map to count occurrences.
    使用雜湊表計算出現次數。
    *   *Target:* Anagrams, Top K Elements.

2.  **Prefix Sum + Hashing (前綴和 + 雜湊):**
    Storing cumulative sums in a hash map to find subarrays with a specific sum.
    將累計和存入雜湊表，以尋找具有特定總和的子陣列。
    *   *Target:* Subarray Sum Equals K.

3.  **Index Mapping / Cyclic Sort (索引映射 / 循環排序):**
    Swapping elements to their correct indices `nums[i]` should be at `nums[nums[i] - 1]`.
    將元素交換至其正確索引 `nums[i]` 應位於 `nums[nums[i] - 1]`。
    *   *Target:* First Missing Positive, Find All Duplicates.

4.  **State Compression (狀態壓縮):**
    Converting a 2D coordinate `(r, c)` or a list of counts into a string/integer key.
    將二維座標 `(r, c)` 或計數列表轉換為字串/整數鍵值。
    *   *Target:* Group Anagrams, Grid problems.

---

## 4. Example Walkthrough (範例講解)

### Problem: First Missing Positive (缺失的第一個正整數)
**LeetCode 41 (Hard)**

#### Problem Statement (問題重述)
Given an unsorted integer array `nums`, return the smallest missing positive integer. You must implement an algorithm that runs in $O(n)$ time and uses $O(1)$ auxiliary space.
給定一個未排序的整數陣列 `nums`，回傳其中缺失的最小正整數。你必須實作一個時間複雜度為 $O(n)$ 且使用 $O(1)$ 輔助空間的演算法。

#### Approach Evolution (思路演進)

1.  **Brute Force (Sorting):**
    *   Sort the array ($O(N \log N)$), then iterate to find the gap.
    *   *Critique:* Too slow. We need $O(N)$.
    *   將陣列排序（$O(N \log N)$），然後迭代尋找缺口。
    *   *評論：* 太慢。我們需要 $O(N)$。

2.  **Intermediate (Hash Set):**
    *   Put all numbers into a `std::unordered_set`. Iterate from 1 to $N+1$ and check existence.
    *   *Critique:* Time $O(N)$, but Space $O(N)$. Fails the space constraint.
    *   將所有數字放入 `std::unordered_set`。從 1 迭代到 $N+1$ 並檢查是否存在。
    *   *評論：* 時間 $O(N)$，但空間 $O(N)$。不符合空間限制。

3.  **Optimal (In-place Hashing / Cyclic Sort):**
    *   **Insight:** If the array length is $N$, the answer must be in the range $[1, N+1]$. We can use the array itself as a hash map.
    *   **洞察：** 若陣列長度為 $N$，答案必在 $[1, N+1]$ 範圍內。我們可以使用陣列本身作為雜湊表。
    *   **Logic:** Iterate through the array. If we see a number `x` between `1` and `N`, put it at index `x-1`. (e.g., value 3 goes to index 2).
    *   **邏輯：** 迭代陣列。若看到一個介於 `1` 和 `N` 之間的數字 `x`，將其放到索引 `x-1` 處。（例如，數值 3 放到索引 2）。
    *   **Final Pass:** Walk through the array. The first index `i` where `nums[i] != i + 1` is the missing number `i + 1`.
    *   **最後掃描：** 遍歷陣列。第一個滿足 `nums[i] != i + 1` 的索引 `i`，其缺失數即為 `i + 1`。

#### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

class Solution {
public:
    int firstMissingPositive(std::vector<int>& nums) {
        int n = nums.size();

        // Pass 1: Place each number in its right place
        // 第一遍：將每個數字放到正確的位置
        for (int i = 0; i < n; ++i) {
            // While the current number is in range [1, n]
            // AND it is not already at the correct position
            // 當前數字在 [1, n] 範圍內，且尚未位於正確位置時
            while (nums[i] > 0 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {
                
                // Swap current number to its target index (nums[i] - 1)
                // 將當前數字交換至其目標索引 (nums[i] - 1)
                std::swap(nums[i], nums[nums[i] - 1]);
            }
        }

        // Pass 2: Find the first index that doesn't match
        // 第二遍：尋找第一個不匹配的索引
        for (int i = 0; i < n; ++i) {
            if (nums[i] != i + 1) {
                // Found the gap. The missing number is index + 1
                // 發現缺口。缺失的數字是 索引 + 1
                return i + 1;
            }
        }

        // If all positions [0, n-1] are correct (1, 2, ..., n), then n+1 is missing
        // 若所有位置 [0, n-1] 都正確 (1, 2, ..., n)，則缺失的是 n+1
        return n + 1;
    }
};
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Although there is a `while` loop inside `for`, each number is swapped to its correct position at most once.
    **時間：** $O(N)$。雖然 `for` 迴圈內有 `while`，但每個數字最多只會被交換到正確位置一次。
*   **Space:** $O(1)$. We modify the input array in place.
    **空間：** $O(1)$。我們原地修改輸入陣列。

#### Common Mistakes (錯誤示範)
*   **Infinite Loop:** Not checking `nums[nums[i] - 1] != nums[i]`. If duplicates exist (e.g., `[1, 1]`), you might swap 1 with 1 infinitely.
    **無窮迴圈：** 未檢查 `nums[nums[i] - 1] != nums[i]`。若存在重複值（如 `[1, 1]`），可能會無限地將 1 與 1 交換。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **std::map** | **std::unordered_map** | `map` is sorted (Tree, $O(\log N)$). `unordered_map` is hashed (Hash Table, $O(1)$). Use `unordered` by default for speed. <br> `map` 是排序的（樹，$O(\log N)$）。`unordered_map` 是雜湊的（雜湊表，$O(1)$）。預設使用 `unordered` 以求速度。 |
| **Subarray (子陣列)** | **Subsequence (子序列)** | Subarray is contiguous (continuous block). Subsequence preserves order but can skip elements. <br> 子陣列是連續的（連續區塊）。子序列保留順序但可跳過元素。 |
| **O(N) Space** | **O(1) Space** | Creating a `vector<bool> visited(n)` is $O(N)$. Modifying the sign bit of input `nums[i] *= -1` is $O(1)$. <br> 建立 `vector<bool> visited(n)` 是 $O(N)$。修改輸入的正負號 `nums[i] *= -1` 是 $O(1)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are negative numbers allowed? Is the array mutable? What is the range of values?"
    **釐清限制：** 「允許負數嗎？陣列可變嗎？數值範圍為何？」
2.  **Propose High-Level Idea:** "Since we need $O(1)$ space and lookups are involved, I'm thinking of using the array indices as implicit hash keys."
    **提出高層次思路：** 「由於需要 $O(1)$ 空間且涉及查找，我考慮使用陣列索引作為隱式雜湊鍵。」
3.  **Address Trade-offs:** "This approach modifies the input. If the input must remain read-only, we'd need $O(N)$ space or $O(N \log N)$ time."
    **討論權衡：** 「此方法會修改輸入。若輸入必須唯讀，我們則需要 $O(N)$ 空間或 $O(N \log N)$ 時間。」

### Whiteboard Strategy (白板策略)
*   **Dry Run:** Before coding, write `[3, 4, -1, 1]` and trace the swap logic manually to show you understand the edge cases.
    **演練：** 寫程式碼前，寫下 `[3, 4, -1, 1]` 並手動追蹤交換邏輯，以展示你理解邊界情況。

### Common Follow-up (常見追問)
*   **Q:** "How to handle this if the data stream is too large for memory?"
    **問：** 「如果資料流太大無法放入記憶體，該如何處理？」
*   **A:** "We would use a Bloom Filter for probabilistic existence checking, or Sharding/Consistent Hashing to distribute data across machines."
    **答：** 「我們會使用布隆過濾器進行機率性存在檢查，或使用分片/一致性雜湊將資料分佈到不同機器上。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (存在重複元素)
*   **Prompt:** Check if any value appears at least twice.
    **題目：** 檢查是否有任何數值出現至少兩次。
*   **Hint:** Use `std::unordered_set` or Sort.
    **提示：** 使用 `std::unordered_set` 或排序。

### 2. Medium: Group Anagrams (字母異位詞分組)
*   **Prompt:** Group strings that have the same characters (e.g., "eat", "tea").
    **題目：** 將具有相同字元的字串分組（如 "eat", "tea"）。
*   **Hint:** The key is the sorted string ("aet") OR a character count array converted to a string key (e.g., "1#0#2...").
    **提示：** 鍵值是排序後的字串（"aet"）或轉換為字串鍵的字元計數陣列（如 "1#0#2..."）。
*   **Senior Focus:** Discuss the complexity of sorting the string ($O(K \log K)$) vs counting ($O(K)$).
    **資深重點：** 討論排序字串（$O(K \log K)$）與計數（$O(K)$）的複雜度差異。

### 3. Hard: Longest Consecutive Sequence (最長連續序列)
*   **Prompt:** Find the length of the longest consecutive elements sequence in an unsorted array. $O(N)$ required.
    **題目：** 在未排序陣列中找出最長連續元素序列的長度。要求 $O(N)$。
*   **Hint:** Put all numbers in a `unordered_set`. Iterate array. Only start counting if `num - 1` is **not** in the set (this ensures you only start from the beginning of a sequence).
    **提示：** 將所有數字放入 `unordered_set`。迭代陣列。只有當 `num - 1` **不在** 集合中時才開始計數（這確保你只從序列的開頭開始）。

---

## 8. Rapid Checklist (快速檢核表)

- [ ] **Boundary Conditions:** Empty array? Array with 1 element? All duplicates?
    **邊界條件：** 空陣列？單一元素陣列？全重複？
- [ ] **Index Out of Bounds:** When accessing `nums[nums[i]]`, is `nums[i]` valid?
    **索引越界：** 存取 `nums[nums[i]]` 時，`nums[i]` 是否有效？
- [ ] **Complexity:** Is your hash map solution truly $O(N)$? Did you accidentally put a loop inside a loop that isn't amortized?
    **複雜度：** 你的雜湊表解法真的是 $O(N)$ 嗎？是否意外地寫出了無法攤銷的雙重迴圈？
- [ ] **Hash Function:** If using a custom object as a key, did you implement `operator==` and a custom `hash` struct?
    **雜湊函數：** 若使用自訂物件作為鍵，是否實作了 `operator==` 與自訂 `hash` 結構？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Pigeonhole Principle" (鴿籠原理):**
    Think of the array as a hotel with rooms numbered 1 to N. If you have guests numbered 1 to N, everyone gets a room. If guest "5" is in room "2", you tell him to go to room "5".
    將陣列想像成一間房間編號為 1 到 N 的旅館。如果你有編號 1 到 N 的客人，每個人都有房間。如果客人「5」在房間「2」，你就叫他去房間「5」。

*   **Hash Collision as "Parking Lot":**
    Open addressing is like finding a parking spot; if your spot is taken, you look for the next one. Chaining is like a multi-level parking spot at that specific location.
    開放定址法就像找停車位；如果你的位置被佔了，你找下一個。鏈結法就像在該特定位置有一個立體停車場。