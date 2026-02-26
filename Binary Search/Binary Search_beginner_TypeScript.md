# Binary Search: Foundational Mastery (二分搜尋法：基礎精通)

## 1. Learning Goals (學習目標)

*   **Master the Loop Invariant:** Understand exactly why we use `left <= right` versus `left < right` and how it affects boundary updates.
    **掌握迴圈不變性：** 徹底理解為何使用 `left <= right` 對比 `left < right`，以及它如何影響邊界更新。
*   **Eliminate Off-by-One Errors:** Learn a consistent template to avoid the most common bug in binary search.
    **消除差一錯誤：** 學習一套一致的模板，以避免二分搜尋中最常見的 Bug。
*   **Identify Applicability:** Quickly recognize problems solvable by binary search (sorted arrays, monotonic functions).
    **識別適用性：** 快速辨識可用二分搜尋解決的問題（已排序陣列、單調函數）。
*   **Analyze Complexity:** Deeply understand the $O(\log N)$ time complexity and $O(1)$ space complexity.
    **分析複雜度：** 深入理解 $O(\log N)$ 時間複雜度與 $O(1)$ 空間複雜度。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Binary Search is an efficient algorithm for finding an item from a sorted list of items.
二分搜尋法是一種在已排序清單中尋找項目的高效演算法。
It works by repeatedly dividing the portion of the list that could contain the item in half until you've narrowed down the possible locations to just one.
它的運作方式是不斷將可能包含該項目的清單部分對半分割，直到將可能的位置縮小到僅剩一個。

### Intuition (直覺)
Think of looking up a word in a physical dictionary.
想像在實體字典中查一個單字。
You open the book in the middle; if the word is alphabetically after the current page, you ignore the left half and search the right half.
你從中間翻開書；如果該單字的字母順序在當前頁面之後，你就忽略左半部，只搜尋右半部。

### Complexity (複雜度)
*   **Time:** $O(\log N)$ — Because the search space is halved in every step.
    **時間：** $O(\log N)$ — 因為搜尋空間在每一步都被減半。
*   **Space:** $O(1)$ — Iterative implementation requires only a few variables.
    **空間：** $O(1)$ — 迭代實作僅需要少數幾個變數。

### When to Use (適用場景)
*   Finding an element in a **sorted array**.
    在**已排序陣列**中尋找元素。
*   Finding a boundary in a monotonic function (e.g., first version that fails).
    在單調函數中尋找邊界（例如：第一個失敗的版本）。

### When NOT to Use (不適用場景)
*   **Unsorted Data:** Requires sorting first ($O(N \log N)$), which may be slower than a linear scan ($O(N)$) for a single search.
    **未排序資料：** 需要先排序（$O(N \log N)$），對於單次搜尋來說，這可能比線性掃描（$O(N)$）還慢。
*   **Linked Lists:** Direct access to the middle element is $O(N)$, negating the binary search advantage.
    **連結串列：** 直接存取中間元素的成本是 $O(N)$，這抵銷了二分搜尋的優勢。
*   **Tiny Datasets:** For very small $N$, the overhead of logic might exceed a simple loop (though negligible in high-level languages).
    **極小資料集：** 對於非常小的 $N$，邏輯開銷可能超過簡單迴圈（儘管在高階語言中可忽略不計）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the **Beginner/Foundational** level, we focus on the most critical pattern:
針對**基礎**層級，我們專注於最關鍵的模式：

1.  **Standard Exact Match (標準精確匹配):**
    Find if a target exists in the array and return its index.
    尋找目標是否存在於陣列中，並回傳其索引。
    *   *Key:* Loop `while (left <= right)`, return `mid` on match.
    *   *關鍵：* 迴圈 `while (left <= right)`，匹配時回傳 `mid`。

2.  **Lower Bound / Upper Bound (Introduction):**
    Find the insertion position or the first/last occurrence of a target.
    尋找插入位置，或目標的第一次/最後一次出現位置。
    *   *Key:* Narrow down the range to a single point.
    *   *關鍵：* 將範圍縮小到單一點。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Search (Standard)
**LeetCode 704:** Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, return its index. Otherwise, return `-1`.
**LeetCode 704:** 給定一個依升序排列的整數陣列 `nums` 和一個整數 `target`，寫一個函式在 `nums` 中搜尋 `target`。如果 `target` 存在，回傳其索引。否則，回傳 `-1`。

### Approach (思路)

1.  **Brute Force (暴力法):**
    Iterate through the array from start to finish.
    從頭到尾遍歷陣列。
    *   Time: $O(N)$
    *   *Verdict:* Too slow for large datasets if sorted.
    *   *結論：* 若資料已排序，對大數據集來說太慢。

2.  **Binary Search (Optimized/Best):**
    Maintain a search interval `[left, right]`. Calculate the middle index. Compare and adjust boundaries.
    維護一個搜尋區間 `[left, right]`。計算中間索引。比較並調整邊界。
    *   Time: $O(\log N)$

### TypeScript Solution (Standard Template)

This template handles the **closed interval** `[left, right]`.
此模板處理**閉區間** `[left, right]`。

```typescript
function search(nums: number[], target: number): number {
    // Initialize pointers to the start and end of the array
    // 初始化指標指向陣列的開頭與結尾
    let left = 0;
    let right = nums.length - 1;

    // Loop condition: left <= right
    // This ensures we process the case where left == right (array of size 1)
    // 迴圈條件：left <= right
    // 這確保我們能處理 left == right 的情況（大小為 1 的陣列）
    while (left <= right) {
        // Calculate mid to avoid potential integer overflow (though less likely in JS/TS)
        // logic: left + distance / 2
        // 計算中間點以避免潛在的整數溢位（雖然在 JS/TS 中較少見）
        // 邏輯：left + 距離 / 2
        const mid = left + Math.floor((right - left) / 2);
        
        const midVal = nums[mid];

        if (midVal === target) {
            // Target found, return index
            // 找到目標，回傳索引
            return mid;
        } else if (midVal < target) {
            // Target is in the right half, exclude mid
            // 目標在右半部，排除 mid
            left = mid + 1;
        } else {
            // Target is in the left half, exclude mid
            // 目標在左半部，排除 mid
            right = mid - 1;
        }
    }

    // Target not found
    // 未找到目標
    return -1;
}
```

### Common Error (錯誤示範) & Why

```typescript
// ❌ BAD PRACTICE
while (left < right) { // Error 1: Misses the last element if left == right
    // ...
    if (nums[mid] < target) {
        left = mid; // Error 2: Potential infinite loop if mid == left
    }
    // ...
}
```

*   **Why it fails:** If `left` and `right` are adjacent (e.g., 0 and 1), `mid` becomes 0. If we set `left = mid`, `left` remains 0. The loop runs forever.
*   **為何失敗：** 如果 `left` 和 `right` 相鄰（例如 0 和 1），`mid` 變成 0。如果我們設定 `left = mid`，`left` 保持為 0。迴圈將永遠執行。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) |
| :--- | :--- |
| **`mid` Calculation** | Use `left + Math.floor((right - left) / 2)` instead of `(left + right) / 2`. <br> **Mid 計算**：使用前者而非後者，以防止在其他強型別語言（如 C++/Java）中發生整數溢位。 |
| **Loop Condition** | `while(left <= right)` processes the element when pointers collide. `while(left < right)` stops before they collide. <br> **迴圈條件**：`<=` 會在指標碰撞時處理該元素；`<` 會在碰撞前停止。 |
| **Boundary Update** | Always use `mid + 1` or `mid - 1` in the standard template. Using `left = mid` causes infinite loops. <br> **邊界更新**：在標準模板中總是使用 `mid + 1` 或 `mid - 1`。使用 `left = mid` 會導致無窮迴圈。 |
| **Array Sorted?** | Binary search produces garbage results on unsorted arrays. Always check preconditions. <br> **陣列已排序？**：二分搜尋在未排序陣列上會產生無效結果。務必檢查前置條件。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **State the Precondition:** "Since the input array is sorted, I can use Binary Search to optimize from $O(N)$ to $O(\log N)$."
    **陳述前置條件：**「由於輸入陣列已排序，我可以使用二分搜尋法將複雜度從 $O(N)$ 優化至 $O(\log N)$。」
2.  **Define the Invariant:** "I will search within the closed range `[left, right]`. At every step, I will exclude `mid` because I've already checked it."
    **定義不變性：**「我將在閉區間 `[left, right]` 內搜尋。每一步驟中，我會排除 `mid`，因為我已經檢查過它了。」

### Whiteboard Strategy (白板策略)
*   **Variable Names:** Use clear names like `left`, `right`, `mid` (or `low`, `high`). Avoid single letters like `i`, `j`, `k` for binary search boundaries.
    **變數命名：** 使用清晰的名稱如 `left`, `right`, `mid`（或 `low`, `high`）。避免在二分搜尋邊界使用 `i`, `j`, `k` 等單字母。
*   **Dry Run:** Manually trace a 3-element array (e.g., `[1, 3, 5]` searching for `5`) to prove your loop termination logic is correct.
    **手動演練：** 手動追蹤一個 3 元素的陣列（例如 `[1, 3, 5]` 搜尋 `5`），以證明你的迴圈終止邏輯是正確的。

### Common Follow-up (常見追問)
*   "What if the array contains duplicates?" (Does it affect finding *any* instance vs. the *first* instance?)
    「如果陣列包含重複元素怎麼辦？」（這會影響尋找*任一*實例還是*第一個*實例嗎？）
*   "What if the array size exceeds memory?" (Distributed search / Indexing).
    「如果陣列大小超過記憶體怎麼辦？」（分散式搜尋 / 索引）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Search Insert Position (搜尋插入位置)
**Problem:** Given a sorted array and a target, return the index if found. If not, return the index where it would be if inserted in order.
**問題：** 給定已排序陣列與目標，若找到則回傳索引。若無，回傳其按順序插入時的索引。
*   **Hint:** The standard template works. If the loop finishes without finding the target, `left` will be the insertion point.
*   **提示：** 標準模板適用。如果迴圈結束未找到目標，`left` 即為插入點。

### 2. Medium: First Bad Version (第一個錯誤版本)
**Problem:** You have versions `[1, 2, ..., n]`. If version `k` is bad, all following versions are bad. Find the first bad one.
**問題：** 你有版本 `[1, 2, ..., n]`。如果版本 `k` 是壞的，之後的所有版本都是壞的。找出第一個壞的版本。
*   **Hint:** This is a "Leftmost Binary Search". If `mid` is bad, the answer could be `mid` or to the left (`right = mid`). If `mid` is good, answer is to the right (`left = mid + 1`).
*   **提示：** 這是「最左二分搜尋」。如果 `mid` 是壞的，答案可能是 `mid` 或在左邊（`right = mid`）。如果 `mid` 是好的，答案在右邊（`left = mid + 1`）。

### 3. Medium (Conceptual): Sqrt(x) (x 的平方根)
**Problem:** Compute `int(sqrt(x))` without using built-in functions.
**問題：** 在不使用內建函式的情況下計算 `int(sqrt(x))`。
*   **Hint:** Search range is `[0, x]`. The condition is `mid * mid <= x`. You are looking for the largest `mid` that satisfies this.
*   **提示：** 搜尋範圍是 `[0, x]`。條件是 `mid * mid <= x`。你在尋找滿足此條件的最大 `mid`。

---

## 8. Checklist (快速檢核表)

Use this during your interview coding phase:
在面試寫程式階段使用此表：

- [ ] **Sorted Input?** Did I confirm the array is sorted? (已排序輸入？我確認陣列已排序了嗎？)
- [ ] **Interval:** Am I using `[left, right]` (closed) or `[left, right)` (open)? (區間：我使用的是閉區間還是開區間？)
- [ ] **Loop Condition:** Does `while (left <= right)` match my interval choice? (迴圈條件：`while` 條件是否符合我的區間選擇？)
- [ ] **Overflow:** Did I calculate mid using `left + (right - left) / 2`? (溢位：我有使用安全的 `mid` 計算方式嗎？)
- [ ] **Termination:** Does my logic guarantee the search space shrinks every iteration? (終止：我的邏輯能保證搜尋空間每次迭代都會縮小嗎？)

---

## 9. Memory Anchors (記憶錨點)

### The "Three-Pointer Snapshot" (三指標快照)
Visualize the state.
視覺化狀態。
*   **Left:** The wall of "Too Small".
    **Left:** 「太小」的高牆。
*   **Right:** The wall of "Too Big".
    **Right:** 「太大」的高牆。
*   **Mid:** The scout checking the unknown territory.
    **Mid:** 檢查未知領域的偵查兵。
*   **Goal:** Move the walls inward until they cross each other.
    **目標：** 將牆向內移動，直到它們彼此錯過。

### The "Phone Book" Analogy (電話簿類比)
You don't start reading a phone book from page 1 to find "Smith". You open the middle. "M"? Go right. "T"? Go left. You repeat this until you are holding the single page with "Smith".
你不會從第一頁開始讀電話簿來找 "Smith"。你會翻開中間。"M"？往右找。"T"？往左找。你重複這動作直到你手中只剩下包含 "Smith" 的那一頁。