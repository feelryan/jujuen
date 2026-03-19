Here is the complete study guide for **Binary Search**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level, with **Java** implementation.

這是一份針對 **二分搜尋法 (Binary Search)** 的完整教材，專為資深軟體工程師量身打造，難度調整為 **初學者 (Beginner)** 級別，並使用 **Java** 實作。

---

# Binary Search: The Foundation of Logarithmic Scale
# 二分搜尋法：對數規模的基石

## 1. Learning Goals (學習目標)

*   **Master the Standard Template:** Write bug-free Binary Search code in under 3 minutes without off-by-one errors.
    **掌握標準模板：** 在 3 分鐘內寫出無 Bug 的二分搜尋程式碼，並避免「差一錯誤（off-by-one errors）」。
*   **Understand Invariants:** Clearly define the search space `[left, right]` and maintain loop invariants.
    **理解不變性：** 清晰定義搜尋區間 `[left, right]` 並維護迴圈不變性。
*   **Handle Overflows:** Learn the safe way to calculate the midpoint to prevent integer overflow.
    **處理溢位：** 學習計算中間點的安全方法，以防止整數溢位。
*   **Identify Applicability:** Recognize when to apply Binary Search beyond simple sorted arrays.
    **識別適用性：** 辨識何時將二分搜尋應用於簡單排序陣列以外的場景。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Binary Search is an efficient algorithm for finding an item from a sorted list of items by repeatedly dividing the search interval in half.
二分搜尋法是一種高效演算法，透過反覆將搜尋區間減半，從已排序的清單中尋找項目。

### Intuition (直覺)
If the value of the search key is less than the item in the middle of the interval, narrow the interval to the lower half; otherwise, narrow it to the upper half.
如果搜尋目標值小於區間中間的項目，則將區間縮小至下半部；否則，縮小至上半部。

### Complexity (複雜度)
*   **Time Complexity:** $O(\log n)$ — The search space is halved in every step.
    **時間複雜度：** $O(\log n)$ — 每一步驟搜尋空間都會減半。
*   **Space Complexity:** $O(1)$ — Iterative implementation requires constant extra space.
    **空間複雜度：** $O(1)$ — 迭代實作僅需常數額外空間。

### When to Use (適用場景)
*   Finding an element in a sorted array.
    在已排序陣列中尋找元素。
*   Finding boundaries (first or last occurrence) in a sorted array.
    在已排序陣列中尋找邊界（第一次或最後一次出現的位置）。

### When NOT to Use (不適用場景)
*   Unsorted data (unless sorting is cheap or pre-processing is allowed).
    未排序的資料（除非排序成本很低或允許預處理）。
*   Data structures with slow random access (e.g., Linked Lists), where accessing the middle element is $O(n)$.
    隨機存取緩慢的資料結構（如鏈結串列），其存取中間元素的成本為 $O(n)$。

---

## 3. Typical Patterns (典型題型 / 模式)

For the **Beginner** level, we focus on the most fundamental pattern.
針對 **初學者** 級別，我們專注於最基礎的模式。

1.  **Exact Match (Standard Template):** Find the index of a target value; return -1 if not found.
    **精確匹配（標準模板）：** 尋找目標值的索引；若未找到則回傳 -1。
2.  **Boundary Search (Lower/Upper Bound):** Find the insertion position or the first/last occurrence of a target.
    **邊界搜尋（下界/上界）：** 尋找目標值的插入位置，或其第一次/最後一次出現的位置。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Search (LeetCode 704)
### 問題：二分搜尋 (LeetCode 704)

**Problem Statement:**
Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.
**問題重述：**
給定一個按升序排列的整數陣列 `nums` 和一個整數 `target`，寫一個函式在 `nums` 中搜尋 `target`。如果 `target` 存在，則回傳其索引。否則，回傳 `-1`。

### Approach (思路)

1.  **Brute Force:** Scan the array from left to right. Time: $O(n)$. Too slow for large datasets.
    **暴力解：** 從左到右掃描陣列。時間：$O(n)$。對大數據集來說太慢。
2.  **Optimization (Binary Search):** Since the array is sorted, check the middle element.
    **優化（二分搜尋）：** 由於陣列已排序，檢查中間元素。
    *   If `nums[mid] == target`, we found it.
        如果 `nums[mid] == target`，我們找到了。
    *   If `nums[mid] < target`, the target must be in the right half.
        如果 `nums[mid] < target`，目標必定在右半部。
    *   If `nums[mid] > target`, the target must be in the left half.
        如果 `nums[mid] > target`，目標必定在左半部。

### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int search(int[] nums, int target) {
        // Define the search space: [left, right] (inclusive)
        // 定義搜尋空間：[left, right]（包含邊界）
        int left = 0;
        int right = nums.length - 1;

        // Loop while the search space is valid
        // 當搜尋空間有效時持續迴圈
        while (left <= right) {
            // Prevent integer overflow: equivalent to (left + right) / 2
            // 防止整數溢位：等同於 (left + right) / 2
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                // Target found
                // 找到目標
                return mid;
            } else if (nums[mid] < target) {
                // Target is in the right half, discard left half
                // 目標在右半部，捨棄左半部
                left = mid + 1;
            } else {
                // Target is in the left half, discard right half
                // 目標在左半部，捨棄右半部
                right = mid - 1;
            }
        }

        // Target not found
        // 未找到目標
        return -1;
    }
}
```

### Error Demonstration & Why (錯誤示範 & 為何錯)

```java
// WRONG WAY / 錯誤寫法
int mid = (left + right) / 2; 
```
*   **Why it's wrong:** If `left` and `right` are both large positive integers (near `Integer.MAX_VALUE`), their sum will overflow into a negative number, causing an `ArrayIndexOutOfBoundsException`.
*   **為何錯：** 如果 `left` 和 `right` 都是很大的正整數（接近 `Integer.MAX_VALUE`），它們的總和會溢位變成負數，導致 `ArrayIndexOutOfBoundsException`。

---

## 5. Common Pitfalls (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Loop Condition** <br> **迴圈條件** | `while(left < right)` vs `while(left <= right)`. <br> For exact match, use `<=`. If you use `<`, you might miss the last element when `left == right`. <br> 對於精確匹配，使用 `<=`。若使用 `<`，當 `left == right` 時可能會漏掉最後一個元素。 |
| **Mid Calculation** <br> **中間點計算** | `(L+R)/2` causes overflow. Always use `L + (R-L)/2`. <br> `(L+R)/2` 會導致溢位。務必使用 `L + (R-L)/2`。 |
| **Boundary Update** <br> **邊界更新** | Setting `left = mid` or `right = mid` incorrectly can cause infinite loops. In the standard template, always use `mid + 1` or `mid - 1`. <br> 錯誤地設定 `left = mid` 或 `right = mid` 會導致無窮迴圈。在標準模板中，務必使用 `mid + 1` 或 `mid - 1`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **State the Assumption:** "Since the input is sorted, I can use Binary Search to optimize from O(n) to O(log n)."
    **陳述假設：** 「由於輸入已排序，我可以使用二分搜尋將複雜度從 O(n) 優化至 O(log n)。」
2.  **Define Invariants:** "I will maintain a search interval `[left, right]` inclusive."
    **定義不變性：** 「我將維護一個包含邊界的搜尋區間 `[left, right]`。」
3.  **Address Edge Cases:** "I will handle the case where the array is empty or the target doesn't exist."
    **處理邊界情況：** 「我會處理陣列為空或目標不存在的情況。」

### Whiteboard Strategy (白板策略)
*   **Trace with Examples:** Write `[1, 3, 5, 7]` and `target = 5`. Manually update `L`, `R`, `mid` values on the board to show correctness.
    **用範例追蹤：** 寫下 `[1, 3, 5, 7]` 和 `target = 5`。在白板上手動更新 `L`、`R`、`mid` 的數值以展示正確性。

### Common Follow-ups (常見追問)
*   **Q:** What if there are duplicates?
    **問：** 如果有重複元素怎麼辦？
    *   *A:* The standard template finds *any* match. To find the first/last, we need to adjust the condition (remove early return).
    *   *答：* 標準模板會找到 *任意* 匹配。若要找第一個/最後一個，需調整條件（移除提早回傳）。

---

## 7. Practice Problems (練習題)

### 1. Easy: First Bad Version (LeetCode 278)
*   **Prompt:** You have `n` versions `[1, 2, ..., n]`. Find the first bad one. `isBadVersion(version)` API is given.
    **題目：** 你有 `n` 個版本 `[1, 2, ..., n]`。找出第一個壞掉的版本。已提供 `isBadVersion(version)` API。
*   **Hint:** This is a "Left Boundary" problem. If `mid` is bad, the first bad version is `mid` or to the left.
    **提示：** 這是「左邊界」問題。如果 `mid` 是壞的，第一個壞版本是 `mid` 或在左邊。
*   **Key Logic:** `right = mid` (preserve potential answer) vs `left = mid + 1`.

### 2. Medium: Search Insert Position (LeetCode 35)
*   **Prompt:** Given a sorted array and a target, return the index if found, or the index where it would be if inserted in order.
    **題目：** 給定排序陣列與目標，若找到則回傳索引，否則回傳按順序插入時的索引。
*   **Hint:** Standard Binary Search. If the loop finishes without finding target, `left` will be the insert position.
    **提示：** 標準二分搜尋。如果迴圈結束未找到目標，`left` 即為插入位置。

### 3. Medium (Conceptual): Sqrt(x) (LeetCode 69)
*   **Prompt:** Compute and return the square root of `x` (integer part).
    **題目：** 計算並回傳 `x` 的平方根（整數部分）。
*   **Hint:** Search space is `[0, x]`. Find `k` such that `k*k <= x`. Be careful of overflow when computing `mid * mid`.
    **提示：** 搜尋空間為 `[0, x]`。尋找 `k` 使得 `k*k <= x`。計算 `mid * mid` 時需注意溢位。

---

## 8. Quick Checklists (快速檢核表)

Use this before saying "I'm done" in an interview.
在面試中說「我完成了」之前，請使用此表。

- [ ] **Initialization:** Are `left` and `right` initialized correctly (`0` to `n-1` or `0` to `n`)?
    **初始化：** `left` 和 `right` 是否正確初始化（`0` 到 `n-1` 或 `0` 到 `n`）？
- [ ] **Loop Condition:** Is it `<=`, `<`, or `+ 1`? Does it match your update logic?
    **迴圈條件：** 是 `<=`、`<` 還是 `+ 1`？是否符合你的更新邏輯？
- [ ] **Mid Calculation:** Did you use `left + (right - left) / 2`?
    **中間點計算：** 你是否使用了 `left + (right - left) / 2`？
- [ ] **Convergence:** Is the search space guaranteed to shrink in every iteration? (No `left = mid` without logic change).
    **收斂性：** 搜尋空間是否保證在每次迭代中縮小？（避免無邏輯變化的 `left = mid`）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Dictionary Game (字典遊戲)
Imagine finding a word in a physical dictionary. You open the middle.
想像在實體字典中找一個單字。你打開中間。
*   Word is "Apple", you opened to "Monkey".
    單字是 "Apple"，你翻到了 "Monkey"。
*   "Apple" is before "Monkey". You discard the entire second half of the book.
    "Apple" 在 "Monkey" 之前。你捨棄後半本字典。
*   **Visual:** Ripping the phone book in half repeatedly.
    **圖像：** 反覆將電話簿撕成兩半。

### The "Two Pointers" Clamp (雙指針夾具)
Visualize `left` and `right` as two walls of a clamp closing in on the target.
將 `left` 和 `right` 想像成夾具的兩道牆，向目標夾緊。
*   **Condition `left <= right`:** The walls can touch and cross each other.
    **條件 `left <= right`：** 牆壁可以接觸並穿過彼此。
*   **Termination:** When `left` crosses `right`, the space is empty.
    **終止：** 當 `left` 穿過 `right`，空間即為空。