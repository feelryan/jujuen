Here is the complete interview preparation material for **Binary Search**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth (foundational mastery), with **C++** as the implementation language.

這是一份針對 **二分搜尋法 (Binary Search)** 的完整面試準備教材，專為資深軟體工程師設計，深度調整為 **初學者 (Beginner)**（強調基礎夯實），並使用 **C++** 實作。

---

# Binary Search: Foundational Mastery (二分搜尋法：基礎精通)

## 1. Learning Objectives (學習目標)

*   **Master the "Closed Interval" Template:** Write bug-free Binary Search code that handles edge cases (empty array, single element) without infinite loops.
    **掌握「閉區間」模板：** 撰寫無 Bug 的二分搜尋程式碼，能處理邊界情況（空陣列、單一元素）且不會陷入無窮迴圈。
*   **Understand the Mathematical Invariant:** Grasp why the time complexity is logarithmic and how the search space reduces.
    **理解數學不變量：** 掌握為何時間複雜度是對數級，以及搜尋空間如何縮減。
*   **Prevent Integer Overflow:** Learn the standard technique to calculate the midpoint safely in C++.
    **防止整數溢位：** 學習在 C++ 中安全計算中間點的標準技巧。
*   **Identify Applicability:** Recognize when Binary Search can be applied (sorted data or monotonic properties).
    **識別適用性：** 辨識何時可應用二分搜尋（已排序資料或單調性質）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Binary Search is an efficient algorithm for finding an item from a sorted list of items.
二分搜尋法是一種在已排序列表中尋找項目的高效演算法。
It works by repeatedly dividing in half the portion of the list that could contain the item.
它通過反覆將可能包含該項目的列表部分對半分割來運作。

### Intuition (直覺)
Think of looking up a word in a physical dictionary.
想像在實體字典中查一個單字。
You open the book in the middle; if the word is alphabetically after the current page, you discard the left half and search the right half.
你從中間翻開書；如果該單字的字母順序在當前頁面之後，你就捨棄左半部，只搜尋右半部。

### Complexity (複雜度)
*   **Time Complexity:** $O(\log N)$ - The search space is halved in every step.
    **時間複雜度：** $O(\log N)$ - 每一步驟搜尋空間都會減半。
*   **Space Complexity:** $O(1)$ - Iterative implementation requires constant extra space.
    **空間複雜度：** $O(1)$ - 迭代實作僅需常數額外空間。

### When to Use (適用場景)
*   Finding an element in a **sorted** array.
    在**已排序**陣列中尋找元素。
*   Finding the insertion point to maintain order.
    尋找插入點以維持順序。

### When NOT to Use (不適用場景)
*   Unsorted data (unless sorting first is acceptable and fits the time budget).
    未排序的資料（除非可以接受先排序且符合時間預算）。
*   Linked Lists (random access is required for $O(1)$ midpoint access).
    鏈結串列（需要隨機存取才能以 $O(1)$ 存取中間點）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the "Beginner" level, we focus on the most fundamental pattern.
針對「初學者」等級，我們專注於最基礎的模式。

### Pattern 1: Standard Exact Match (標準精確匹配)
*   **Goal:** Find the index of a specific `target` value.
    **目標：** 尋找特定 `target` 值的索引。
*   **Condition:** `nums[mid] == target`.
    **條件：** `nums[mid] == target`。
*   **Template:** Closed Interval `[left, right]`.
    **模板：** 閉區間 `[left, right]`。

### Pattern 2: Lower/Upper Bound (Introduction) (下界/上界 - 簡介)
*   **Goal:** Find the first position where a value can be inserted while maintaining order.
    **目標：** 尋找第一個可插入值並維持順序的位置。
*   **Note:** In C++, this corresponds to `std::lower_bound` and `std::upper_bound`.
    **註記：** 在 C++ 中，這對應於 `std::lower_bound` 和 `std::upper_bound`。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Search (Standard)
**LeetCode 704:** Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.
**LeetCode 704:** 給定一個按升序排列的整數陣列 `nums` 和一個整數 `target`，寫一個函式在 `nums` 中搜尋 `target`。如果 `target` 存在，則返回其索引。否則，返回 `-1`。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Iterate through the entire array. Time: $O(N)$.
    *   遍歷整個陣列。時間：$O(N)$。
    *   *Verdict:* Too slow for large datasets.
    *   *結論：* 對於大數據集來說太慢。

2.  **Binary Search (Optimization):**
    *   Since the array is sorted, we can check the middle element.
    *   因為陣列已排序，我們可以檢查中間元素。
    *   If `nums[mid] > target`, the target must be in the left half.
    *   如果 `nums[mid] > target`，目標一定在左半部。
    *   If `nums[mid] < target`, the target must be in the right half.
    *   如果 `nums[mid] < target`，目標一定在右半部。

### C++ Reference Solution (C++ 參考解)

We use the **Closed Interval `[left, right]`** approach. This is the most intuitive for beginners.
我們使用 **閉區間 `[left, right]`** 方法。這對初學者來說最直觀。

```cpp
#include <vector>
#include <iostream>

class Solution {
public:
    int search(std::vector<int>& nums, int target) {
        // Initialize pointers to the start and end of the array.
        // 初始化指標指向陣列的開頭與結尾。
        int left = 0;
        int right = nums.size() - 1;

        // Loop as long as the search interval is valid.
        // The condition '<=' allows the loop to check the case where left == right (single element).
        // 只要搜尋區間有效就持續迴圈。
        // 條件 '<=' 允許迴圈檢查 left == right（單一元素）的情況。
        while (left <= right) {
            // Calculate mid to avoid integer overflow.
            // Equivalent to (left + right) / 2 but safe for large integers.
            // 計算中間點以避免整數溢位。
            // 等同於 (left + right) / 2，但在大整數時更安全。
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                // Target found, return the index.
                // 找到目標，返回索引。
                return mid;
            } else if (nums[mid] < target) {
                // Target is in the right half.
                // We exclude mid because we already checked it.
                // 目標在右半部。
                // 我們排除 mid，因為已經檢查過它了。
                left = mid + 1;
            } else {
                // Target is in the left half.
                // Exclude mid.
                // 目標在左半部。
                // 排除 mid。
                right = mid - 1;
            }
        }

        // Target not found.
        // 目標未找到。
        return -1;
    }
};
```

### Common Mistake (錯誤示範)

```cpp
// WRONG: Potential Infinite Loop & Overflow
// 錯誤：潛在的無窮迴圈與溢位
int mid = (left + right) / 2; // Overflow risk! (溢位風險！)
if (nums[mid] < target) {
    left = mid; // Infinite loop if left and right are adjacent!
                // 如果 left 和 right 相鄰，會陷入無窮迴圈！
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Correct Approach (正確做法) | Pitfall (陷阱) |
| :--- | :--- | :--- |
| **Mid Calculation**<br>中間點計算 | `left + (right - left) / 2` | `(left + right) / 2` causes overflow if `left + right > INT_MAX`.<br>若 `left + right > INT_MAX` 會導致溢位。 |
| **Loop Condition**<br>迴圈條件 | `while (left <= right)` for exact match.<br>尋找精確匹配時用 `while (left <= right)`。 | Using `while (left < right)` might miss the last element if not handled carefully.<br>使用 `while (left < right)` 若未小心處理可能會漏掉最後一個元素。 |
| **Pointer Update**<br>指標更新 | `left = mid + 1`, `right = mid - 1` | `left = mid` or `right = mid` causes infinite loops in the `left <= right` template.<br>在 `left <= right` 模板中，使用 `left = mid` 或 `right = mid` 會導致無窮迴圈。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarify Constraints (釐清限制)
*   "Is the input array guaranteed to be sorted?"
    「輸入陣列保證是已排序的嗎？」
*   "Are there duplicate elements?" (Duplicates can affect how we skip elements).
    「有重複的元素嗎？」（重複元素會影響我們跳過元素的方式）。

### 2. Verbalize the Invariant (口述不變量)
*   "I will maintain a search interval `[left, right]`. At each step, I verify `mid`. If `mid` is not the target, I can safely discard half the array because it is sorted."
    「我將維護一個搜尋區間 `[left, right]`。每一步我驗證 `mid`。如果 `mid` 不是目標，我可以安全地捨棄一半的陣列，因為它是已排序的。」

### 3. Dry Run Strategy (演練策略)
*   Trace your code with a 2-element array (e.g., `[1, 3]`, target `3`) to prove your loop terminates.
    使用 2 個元素的陣列（例如 `[1, 3]`，目標 `3`）來追蹤你的程式碼，證明迴圈會終止。

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單)
**Problem:** Search Insert Position (LeetCode 35)
**Hint:** If target is found, return index. If loop finishes, `left` will be the insertion index.
**提示：** 若找到目標，返回索引。若迴圈結束，`left` 即為插入索引。

### Level: Medium (中等) - *Conceptually Beginner logic*
**Problem:** First Bad Version (LeetCode 278)
**Hint:** This is a variation where `bool isBadVersion(version)` is monotonic (False, False, ... True, True). Find the *first* True.
**提示：** 這是一個變體，其中 `bool isBadVersion(version)` 是單調的（False, False, ... True, True）。尋找 *第一個* True。

### Level: "Hard" (Conceptually) (概念上的困難)
**Problem:** Sqrt(x) (LeetCode 69)
**Hint:** Search space is `1` to `x`. You are looking for `k` such that `k*k <= x`. Do not use built-in sqrt.
**提示：** 搜尋空間是 `1` 到 `x`。你在尋找 `k` 使得 `k*k <= x`。不要使用內建 sqrt。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Sorted?** Did I confirm the input is sorted?
    **已排序？** 我確認輸入是已排序的嗎？
*   [ ] **Overflow?** Did I use `l + (r - l) / 2`?
    **溢位？** 我有使用 `l + (r - l) / 2` 嗎？
*   [ ] **Base Case?** Does it handle `size == 0` or `size == 1`?
    **基本情況？** 它能處理 `size == 0` 或 `size == 1` 嗎？
*   [ ] **Termination?** Do `left` and `right` always move closer to each other?
    **終止？** `left` 和 `right` 總是彼此靠近嗎？

---

## 9. Memory Anchors (記憶錨點)

### The "Bracket Squeeze" (括號擠壓)
Visualize `left` and `right` as brackets `[` and `]`.
將 `left` 和 `right` 想像成括號 `[` 和 `]`。
*   `while (left <= right)` means the brackets can overlap on one element `[x]`.
    `while (left <= right)` 意味著括號可以在一個元素上重疊 `[x]`。
*   `mid + 1` and `mid - 1` strictly move the brackets past the checked element, ensuring the space shrinks.
    `mid + 1` 和 `mid - 1` 嚴格地將括號移動越過已檢查的元素，確保空間縮小。

### The "Safe Mid" Mantra (安全中間點口訣)
"Left plus distance halved."
「左加距離除以二。」
`left + (right - left) / 2`