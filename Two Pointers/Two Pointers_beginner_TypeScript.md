# Two Pointers: Foundational Mechanics & Interview Strategy
# 雙指標：基礎機制與面試策略

## 1. Learning Objectives (學習目標)

*   **Master the two primary patterns:** Collision (opposite direction) and Fast & Slow (same direction).
    *   **掌握兩種主要模式：** 對撞指標（反向）與快慢指標（同向）。
*   **Identify the "Sorted" signal:** Recognize when sorted input data strongly suggests a Two Pointers approach to optimize from $O(N^2)$ to $O(N)$.
    *   **識別「已排序」訊號：** 辨識何時已排序的輸入資料強烈暗示使用雙指標將複雜度從 $O(N^2)$ 優化至 $O(N)$。
*   **Eliminate common off-by-one errors:** Solidify understanding of loop termination conditions (`left < right` vs `left <= right`).
    *   **消除常見的差一錯誤：** 鞏固對迴圈終止條件的理解（`left < right` 對比 `left <= right`）。
*   **Optimize Space Complexity:** Learn to solve problems in-place ($O(1)$ space) rather than using Hash Maps ($O(N)$ space).
    *   **優化空間複雜度：** 學習原地（In-place）解決問題（$O(1)$ 空間），而非使用雜湊表（$O(N)$ 空間）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Two Pointers is a technique where two distinct indices are used to traverse a linear data structure (like an array or string) to perform a task, often reducing the need for nested loops.
雙指標是一種使用兩個不同索引來遍歷線性資料結構（如陣列或字串）以執行任務的技巧，通常能減少對巢狀迴圈的需求。

### Intuition (直覺)
Instead of fixing one element and iterating through all others (Brute Force), we use the sorted property or specific logic to make a decision at every step that shrinks the search space from both ends or filters data in a single pass.
我們不固定一個元素並迭代其他所有元素（暴力解），而是利用排序特性或特定邏輯，在每一步做出決策，從兩端縮小搜尋範圍，或在單次遍歷中過濾資料。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$. We touch each element at most once or twice.
    *   **時間：** 通常為 $O(N)$。我們最多接觸每個元素一到兩次。
*   **Space:** Usually $O(1)$. We only store two integer variables.
    *   **空間：** 通常為 $O(1)$。我們只儲存兩個整數變數。

### When to Use (適用場景)
*   **Sorted Arrays:** Finding pairs (Two Sum), triplets, or subarrays.
    *   **已排序陣列：** 尋找配對（Two Sum）、三元組或子陣列。
*   **Palindromes:** Checking strings from both ends.
    *   **迴文：** 從兩端檢查字串。
*   **In-place Operations:** Removing duplicates, moving zeroes, reversing arrays.
    *   **原地操作：** 移除重複項、移動零、反轉陣列。

### When NOT to Use (不適用場景)
*   **Unsorted Arrays (where order matters):** If you cannot sort the array (because indices matter) and the problem requires finding specific indices based on values (unless using a Hash Map).
    *   **未排序陣列（順序重要時）：** 如果不能對陣列排序（因為索引很重要），且問題要求基於值尋找特定索引（除非使用雜湊表）。
*   **Complex Graph/Tree structures:** Though pointers are used, it's usually classified as DFS/BFS/Traversal.
    *   **複雜的圖/樹結構：** 雖然會用到指標，但通常歸類為 DFS/BFS/遍歷。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Collision Pointers (Opposite Direction)
### A. 對撞指標（反向）
*   **Concept:** One pointer starts at the beginning (`left = 0`), the other at the end (`right = n-1`). They move towards each other.
    *   **概念：** 一個指標從頭開始（`left = 0`），另一個從尾開始（`right = n-1`）。它們彼此靠近。
*   **Use Case:** Two Sum (Sorted), Valid Palindrome, Container With Most Water.
    *   **案例：** Two Sum（已排序）、驗證迴文、盛最多水的容器。

### B. Fast & Slow Pointers (Same Direction)
### B. 快慢指標（同向）
*   **Concept:** Both pointers start at the beginning. The `fast` pointer explores ahead, while the `slow` pointer builds the result or marks the boundary.
    *   **概念：** 兩個指標都從頭開始。`fast` 指標向前探索，而 `slow` 指標建構結果或標記邊界。
*   **Use Case:** Remove Duplicates from Sorted Array, Move Zeroes.
    *   **案例：** 從已排序陣列移除重複項、移動零。

### C. Merging Pointers
### C. 合併指標
*   **Concept:** Given two sorted arrays, use one pointer for each to merge them into a new sorted result.
    *   **概念：** 給定兩個已排序陣列，各使用一個指標將它們合併為一個新的已排序結果。

---

## 4. Example Walkthrough (範例講解)

### Problem: Two Sum II - Input Array Is Sorted
### 問題：兩數之和 II - 輸入陣列已排序

**Problem Statement:**
Given a **1-indexed** array of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number.
給定一個**下標從 1 開始**的整數陣列 `numbers`，該陣列已按**非遞減順序排序**，請找出兩個數，使它們相加等於特定的 `target` 數。

---

### Approach 1: Brute Force (暴力解)
Iterate through every pair of numbers.
迭代每一對數字。
*   **Time:** $O(N^2)$ - Too slow for large inputs. (太慢)
*   **Space:** $O(1)$.

### Approach 2: Binary Search (二分搜尋)
For each number `x`, binary search for `target - x`.
對於每個數字 `x`，二分搜尋 `target - x`。
*   **Time:** $O(N \log N)$. Better, but not optimal. (較好，但非最佳)

### Approach 3: Two Pointers (Optimal) (雙指標 - 最佳解)
Since the array is sorted, the smallest sum is `left + right` (initially). If the sum is too small, we *must* move the left pointer to increase the sum. If too large, we *must* move the right pointer to decrease it.
由於陣列已排序，最小的和是 `left + right`（初始時）。如果和太小，我們**必須**移動左指標來增加和。如果太大，我們**必須**移動右指標來減少和。

*   **Time:** $O(N)$ - Each element is visited at most once.
*   **Space:** $O(1)$ - No extra data structures.

---

### TypeScript Solution (參考解)

```typescript
/**
 * Two Sum II - Input Array Is Sorted
 * 兩數之和 II - 輸入陣列已排序
 * 
 * @param numbers Sorted array of integers (已排序整數陣列)
 * @param target The target sum (目標和)
 * @returns Indices of the two numbers (1-based) (兩個數字的索引，從 1 開始)
 */
function twoSum(numbers: number[], target: number): number[] {
    // Initialize pointers at both ends
    // 初始化兩端的指標
    let left = 0;
    let right = numbers.length - 1;

    // Loop until pointers meet
    // 迴圈直到指標相遇
    while (left < right) {
        const sum = numbers[left] + numbers[right];

        if (sum === target) {
            // Found the pair, return 1-based indices
            // 找到配對，返回從 1 開始的索引
            return [left + 1, right + 1];
        } else if (sum < target) {
            // Sum is too small, we need a larger number.
            // Since array is sorted, moving left pointer to the right increases the sum.
            // 和太小，我們需要更大的數字。
            // 因為陣列已排序，將左指標向右移會增加總和。
            left++;
        } else {
            // Sum is too large, we need a smaller number.
            // Moving right pointer to the left decreases the sum.
            // 和太大，我們需要更小的數字。
            // 將右指標向左移會減少總和。
            right--;
        }
    }

    // Should not reach here based on problem constraints (guaranteed solution)
    // 根據題目限制不應執行到此處（保證有解）
    return [-1, -1];
}
```

### Common Mistake (錯誤示範)
Using a Hash Map (like standard Two Sum) when the array is sorted.
當陣列已排序時仍使用雜湊表（像標準 Two Sum 一樣）。

**Why it's suboptimal (為何非最佳):**
It uses $O(N)$ space complexity. In an interview, failing to leverage the "sorted" property to achieve $O(1)$ space is a red flag for a Senior Engineer.
這使用了 $O(N)$ 的空間複雜度。在面試中，未能利用「已排序」特性來達到 $O(1)$ 空間，對資深工程師來說是一個警訊。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Loop Condition** <br> (`<` vs `<=`) | **Collision:** Use `left < right` if using elements at `left` and `right` as a pair (cannot be the same element). Use `left <= right` if the center element needs processing (e.g., Binary Search). <br> **對撞：** 若將 `left` 和 `right` 作為一對使用（不能是同一元素），使用 `left < right`。若中心元素需要處理（如二分搜尋），使用 `left <= right`。 |
| **Input Modification** <br> (輸入修改) | In "Remove Duplicates", you modify the array in-place. Ensure you clarify if the input array can be modified. <br> 在「移除重複項」中，你會原地修改陣列。請務必確認輸入陣列是否允許被修改。 |
| **Duplicate Handling** <br> (重複項處理) | In "3Sum", simply moving pointers isn't enough; you must manually `while` loop to skip duplicates to avoid duplicate triplets. <br> 在「3Sum」中，單純移動指標是不夠的；你必須手動使用 `while` 迴圈跳過重複項以避免重複的三元組。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify:** "I see the array is sorted, which suggests a Two Pointers approach or Binary Search."
    *   **識別：** 「我看到陣列是已排序的，這暗示可以使用雙指標或二分搜尋。」
2.  **Propose:** "I will use two pointers, one at the start and one at the end, to find the target sum in $O(N)$ time and $O(1)$ space."
    *   **提案：** 「我將使用兩個指標，一個在頭一個在尾，以 $O(N)$ 時間和 $O(1)$ 空間找出目標和。」
3.  **Justify:** "This is better than the brute force $O(N^2)$ and saves space compared to the Hash Map approach."
    *   **論證：** 「這比暴力解的 $O(N^2)$ 更好，且比雜湊表解法節省空間。」

### Whiteboard Strategy (白板策略)
*   Draw the array with indices.
*   Use arrows ($\uparrow$) labeled `L` and `R` below the array.
*   Trace one iteration: calculate sum, compare with target, cross out the old pointer position and draw the new one.
*   畫出帶有索引的陣列。
*   在陣列下方使用標有 `L` 和 `R` 的箭頭（$\uparrow$）。
*   追蹤一次迭代：計算總和，與目標比較，劃掉舊的指標位置並畫出新的。

### Common Follow-ups (常見追問)
*   "What if the array contains duplicates?" (Handle skipping logic).
    *   「如果陣列包含重複項怎麼辦？」（處理跳過邏輯）。
*   "What if the input is too large to fit in memory?" (Discuss streams or loading chunks).
    *   「如果輸入太大無法放入記憶體怎麼辦？」（討論串流或分塊讀取）。

---

## 7. Practice Problems (練習題)

### Level: Easy (易)
**Problem:** **Valid Palindrome** (LeetCode 125)
**Hint:** Use two pointers moving towards the center. Skip non-alphanumeric characters. Compare characters case-insensitively.
**提示：** 使用雙指標向中心移動。跳過非字母數字字符。不區分大小寫比較字符。

### Level: Medium (中)
**Problem:** **Container With Most Water** (LeetCode 11)
**Hint:** Area is limited by the shorter line. Always move the pointer of the *shorter* line inward to potentially find a taller line. Moving the taller line can never increase area (width decreases, height limited by shorter).
**提示：** 面積受限於較短的線。總是將*較短*線的指標向內移動，以期找到更高的線。移動較高的線絕不會增加面積（寬度減少，高度受限於較短者）。

### Level: Hard (難 - Conceptual Ceiling)
**Problem:** **Trapping Rain Water** (LeetCode 42)
**Hint:** Maintain `leftMax` and `rightMax`. Water trapped at a position is determined by `min(leftMax, rightMax) - height[i]`. Move the pointer with the smaller max value.
**提示：** 維護 `leftMax` 和 `rightMax`。某位置蓄水量由 `min(leftMax, rightMax) - height[i]` 決定。移動擁有較小最大值的那個指標。

---

## 8. Checklists (快速檢核表)

Use this before saying "I'm done" in an interview:
在面試中說「我完成了」之前，請使用此表：

*   [ ] **Termination:** Will `left` and `right` cross or meet correctly? Is it `<` or `<=`?
    *   **終止條件：** `left` 和 `right` 會正確交叉或相遇嗎？是 `<` 還是 `<=`？
*   [ ] **Movement:** Do I always increment/decrement pointers inside the loop? (Avoid infinite loops).
    *   **移動：** 我是否總是在迴圈內增加/減少指標？（避免無窮迴圈）。
*   [ ] **Bounds:** Are pointers initialized correctly (`0` and `length - 1`)?
    *   **邊界：** 指標初始化正確嗎（`0` 和 `length - 1`）？
*   [ ] **Edge Cases:** Empty array? Array with 1 element? No solution found?
    *   **邊界情況：** 空陣列？只有一個元素的陣列？找不到解？

---

## 9. Memory Anchors (記憶錨點)

*   **Collision (Two Sum):** Like **folding a piece of paper**. You check the edges and fold inwards until you find the crease (solution).
    *   **對撞（Two Sum）：** 就像**摺紙**。你檢查邊緣並向內摺疊，直到找到摺痕（解）。
*   **Fast & Slow:** Like **The Tortoise and the Hare**. One runs ahead to scout/process, the other follows to build the clean result.
    *   **快慢指標：** 就像**龜兔賽跑**。一個向前跑去偵查/處理，另一個跟隨在後建構乾淨的結果。