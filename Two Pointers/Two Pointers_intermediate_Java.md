Here is the comprehensive guide tailored for a Senior Software Engineer, focusing on **Two Pointers** with **Java** implementation.
這是一份專為資深軟體工程師量身打造的指南，專注於 **雙指針（Two Pointers）** 並使用 **Java** 實作。

---

# Two Pointers Interview Guide (Intermediate)
# 雙指針面試指南（中級）

## 1. Learning Objectives (學習目標)

1.  **Identify Pattern Applicability:** Quickly recognize when to use Two Pointers to optimize $O(N^2)$ solutions down to $O(N)$.
    **識別模式適用性：** 快速辨識何時使用雙指針將 $O(N^2)$ 的解法優化至 $O(N)$。
2.  **Master Pointer Movement Logic:** Understand the mathematical intuition behind "shrinking the search space" to prove correctness during interviews.
    **掌握指針移動邏輯：** 理解「縮小搜尋空間」背後的數學直覺，以便在面試中證明解法的正確性。
3.  **Handle Edge Cases in Java:** Proficiently manage array bounds, off-by-one errors, and object equality (e.g., String comparison) in Java.
    **處理 Java 邊界情況：** 熟練處理陣列邊界、差一錯誤（off-by-one errors）以及 Java 中的物件相等性（如字串比較）。
4.  **Differentiate Variations:** Distinguish between "Collision Pointers" (opposite direction) and "Fast & Slow Pointers" (same direction).
    **區分變體：** 區分「對撞指針」（反向）與「快慢指針」（同向）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Two Pointers is a technique where two distinct indices (pointers) are used to traverse a data structure (usually an array or string) to satisfy a specific condition.
雙指針是一種技術，使用兩個不同的索引（指針）來遍歷資料結構（通常是陣列或字串）以滿足特定條件。

### Intuition (直覺)
Instead of checking every pair (brute force), we use sorted properties or logic to rule out invalid pairs, effectively shrinking the search window.
我們利用排序特性或邏輯來排除無效的配對，從而有效地縮小搜尋視窗，而不是檢查每一對組合（暴力解）。

### Complexity (複雜度)
-   **Time:** Usually $O(N)$. We touch each element at most a constant number of times.
    **時間：** 通常為 $O(N)$。我們最多接觸每個元素常數次。
-   **Space:** $O(1)$. We only store two integer variables.
    **空間：** $O(1)$。我們只儲存兩個整數變數。

### When to Use (適用場景)
-   Processing sorted arrays (e.g., finding pairs).
    處理已排序陣列（例如：尋找配對）。
-   Reversing arrays or strings.
    反轉陣列或字串。
-   Partitioning arrays (e.g., moving zeros to the end).
    分割陣列（例如：將零移動到末端）。
-   Checking palindromes.
    檢查迴文。

### When NOT to Use (不適用場景)
-   When the input data cannot be sorted or sorting is too expensive ($O(N \log N)$ is acceptable, but sometimes strict $O(N)$ is required).
    當輸入資料無法排序或排序代價過高時（$O(N \log N)$ 可接受，但有時嚴格要求 $O(N)$）。
-   When you need to find *all* combinations in an unsorted structure without specific constraints.
    當需要在無特定限制的未排序結構中找出 *所有* 組合時。

---

## 3. Typical Patterns (典型題型 / 模式)

### 1. Collision Pointers (Opposite Direction) / 對撞指針（反向）
-   **Setup:** One pointer at the start (`left = 0`), one at the end (`right = n - 1`).
    **設定：** 一個指針在起點（`left = 0`），一個在終點（`right = n - 1`）。
-   **Movement:** Move towards each other until they meet.
    **移動：** 彼此靠近直到相遇。
-   **Use Case:** 2Sum in sorted array, Container With Most Water.
    **案例：** 排序陣列中的兩數之和、盛最多水的容器。

### 2. Fast & Slow Pointers (Same Direction) / 快慢指針（同向）
-   **Setup:** Both start at 0, or `slow = 0`, `fast = 1`.
    **設定：** 兩者皆從 0 開始，或 `slow = 0`, `fast = 1`。
-   **Movement:** `fast` moves every step; `slow` moves only when a condition is met.
    **移動：** `fast` 每步都移動；`slow` 僅在滿足條件時移動。
-   **Use Case:** Remove duplicates, Move Zeroes, Linked List Cycle detection.
    **案例：** 移除重複項、移動零、鏈結串列環檢測。

### 3. Merging Pointers / 合併指針
-   **Setup:** Pointers at the beginning of two separate arrays.
    **設定：** 指針分別位於兩個獨立陣列的開頭。
-   **Use Case:** Merge Sort, Intersection of two arrays.
    **案例：** 合併排序、兩個陣列的交集。

---

## 4. Example Walkthrough (範例講解)

### Problem: Container With Most Water (盛最多水的容器)
*LeetCode 11 (Medium)*

#### Problem Restatement (問題重述)
Given an integer array `height` of length `n`. Find two lines that together with the x-axis form a container, such that the container contains the most water.
給定一個長度為 `n` 的整數陣列 `height`。找出兩條線，使其與 x 軸共同構成一個容器，該容器能容納最多的水。

#### Approach: Brute Force to Optimal (思路：暴力 → 優化)

1.  **Brute Force ($O(N^2)$):** Check every pair of lines.
    **暴力解 ($O(N^2)$)：** 檢查每一對線段。
    *   For a Senior engineer, this is the starting point to establish a baseline, but immediately discarded.
    *   對於資深工程師，這是建立基準的起點，但應立即捨棄。

2.  **Optimal - Two Pointers ($O(N)$):**
    **最佳解 - 雙指針 ($O(N)$)：**
    *   Start with the widest possible container (indices 0 and n-1).
        從最寬的容器開始（索引 0 和 n-1）。
    *   **Crucial Logic:** The area is determined by the shorter line. If we move the pointer of the *taller* line inward, the width decreases, and the height is still limited by the existing short line (or an even shorter one). The area *cannot* increase.
        **關鍵邏輯：** 面積由較短的線決定。如果我們向內移動 *較高* 線段的指針，寬度會減少，而高度仍然受限於現有的短線（或更短的線）。面積 *不可能* 增加。
    *   **Strategy:** Therefore, we must move the pointer of the *shorter* line to potentially find a taller line.
        **策略：** 因此，我們必須移動 *較短* 線段的指針，以期找到更高的線段。

#### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int maxArea(int[] height) {
        // Initialize pointers at both ends
        // 初始化指針於兩端
        int left = 0;
        int right = height.length - 1;
        int maxArea = 0;

        // Loop until pointers meet
        // 迴圈直到指針相遇
        while (left < right) {
            // Calculate current width and height
            // 計算當前寬度與高度
            int width = right - left;
            
            // The container height is limited by the shorter side
            // 容器高度受限於較短的一邊
            int currentHeight = Math.min(height[left], height[right]);
            
            // Update max area
            // 更新最大面積
            int currentArea = width * currentHeight;
            maxArea = Math.max(maxArea, currentArea);

            // Greedy Strategy: Move the shorter pointer inward
            // 貪婪策略：將較短的指針向內移動
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }

        return maxArea;
    }
}
```

#### Common Mistakes (錯誤示範)
-   **Moving both pointers:** If `height[left] == height[right]`, some might move both. While acceptable here, in problems like 3Sum, skipping logic requires care.
    **同時移動兩個指針：** 如果 `height[left] == height[right]`，有些人可能會同時移動兩者。雖然在此題可接受，但在像 3Sum 這樣的問題中，跳過邏輯需要小心。
-   **Condition Error:** Using `left <= right`. Since width is 0 when pointers meet, strictly `<` is cleaner, though `<=` doesn't break correctness here (just wastes a cycle).
    **條件錯誤：** 使用 `left <= right`。由於指針相遇時寬度為 0，嚴格使用 `<` 較為乾淨，雖然 `<=` 在此不會破壞正確性（只是浪費一次循環）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **`left < right` vs `left <= right`** | Use `<` when processed elements are pairs (e.g., 2Sum). Use `<=` when the center element matters (e.g., Binary Search, Valid Palindrome). <br> 當處理成對元素時使用 `<`（如 2Sum）。當中心元素重要時使用 `<=`（如二分搜尋、驗證迴文）。 |
| **Index Out of Bounds** | In `while` loops, always check bounds before accessing array, especially when incrementing inside the loop (e.g., skipping duplicates). <br> 在 `while` 迴圈中，存取陣列前務必檢查邊界，特別是在迴圈內遞增時（例如跳過重複項）。 |
| **Handling Duplicates** | In problems like 3Sum, failing to skip duplicates leads to wrong result counts. <br> 在像 3Sum 的問題中，若未跳過重複項會導致結果數量錯誤。 |
| **Sliding Window vs Two Pointers** | Sliding Window is a *subset* of Two Pointers where the pointers define a "window" maintaining a state. Standard Two Pointers often just compare values at indices. <br> 滑動視窗是雙指針的 *子集*，其中指針定義了一個維持狀態的「視窗」。標準雙指針通常僅比較索引處的值。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Verbalize the "Why" (口述「為什麼」)
-   **Don't just say:** "I will use two pointers."
    **不要只說：** 「我會用雙指針。」
-   **Do say:** "Since the array is sorted (or we are looking for a boundary condition), a brute force approach is $O(N^2)$. We can optimize this to $O(N)$ by using two pointers to shrink the search space from both ends."
    **要說：** 「由於陣列已排序（或我們正在尋找邊界條件），暴力解法是 $O(N^2)$。我們可以透過雙指針從兩端縮小搜尋空間，將其優化為 $O(N)$。」

### 2. Whiteboard Strategy (白板策略)
-   **Variables:** Clearly name them `left`, `right` (or `low`, `high`). Avoid `i`, `j` unless it's a nested loop.
    **變數：** 清楚命名為 `left`, `right`（或 `low`, `high`）。除非是巢狀迴圈，否則避免使用 `i`, `j`。
-   **Dry Run:** Before coding, draw an array and arrows. Move them manually to show you handle the logic (especially the "move shorter pointer" logic).
    **模擬執行：** 寫程式碼前，畫出陣列與箭頭。手動移動它們以展示你掌握了邏輯（特別是「移動較短指針」的邏輯）。

### 3. Common Follow-ups (常見追問)
-   "What if the input is too large to fit in memory?" (Stream processing / External sort).
    「如果輸入太大無法放入記憶體怎麼辦？」（串流處理 / 外部排序）。
-   "Can we do this without sorting?" (Hash Map approach).
    「我們可以在不排序的情況下做這件事嗎？」（雜湊表解法）。

---

## 7. Practice Problems (練習題)

### Level: Easy - Valid Palindrome
**Hint:** Use `Character.isLetterOrDigit` to skip non-alphanumeric characters. Move pointers inward.
**提示：** 使用 `Character.isLetterOrDigit` 跳過非字母數字字元。將指針向內移動。
**Core Logic:** Collision Pointers.
**核心邏輯：** 對撞指針。

### Level: Medium - 3Sum (LeetCode 15)
**Hint:** Sort the array first. Iterate `i` from `0` to `n-2`, then use Two Pointers (Collision) for the remaining part to find `sum = -nums[i]`. **Crucial:** Skip duplicates for both `i` and the pointers.
**提示：** 先排序陣列。遍歷 `i` 從 `0` 到 `n-2`，然後對剩餘部分使用雙指針（對撞）尋找 `sum = -nums[i]`。**關鍵：** 對 `i` 和指針都要跳過重複項。

### Level: Hard - Trapping Rain Water (LeetCode 42)
**Hint:** Similar to Container With Most Water, but you track `leftMax` and `rightMax`. Water trapped at a position is `min(leftMax, rightMax) - height[i]`.
**提示：** 類似盛最多水的容器，但你需要追蹤 `leftMax` 和 `rightMax`。某位置滯留的水量為 `min(leftMax, rightMax) - height[i]`。

---

## 8. Quick Checklists (快速檢核表)

Use this during your implementation phase:
在實作階段使用此表：

- [ ] **Initialization:** Are `left` and `right` set correctly (0 vs 1, n-1 vs n)?
    **初始化：** `left` 和 `right` 設定正確嗎（0 對 1，n-1 對 n）？
- [ ] **Loop Condition:** Is it `<` or `<=`? Does the problem allow the pointers to overlap?
    **迴圈條件：** 是 `<` 還是 `<=`？題目允許指針重疊嗎？
- [ ] **Movement Logic:** Do you always move at least one pointer in every iteration? (Avoid infinite loops).
    **移動邏輯：** 你是否在每次迭代中都至少移動了一個指針？（避免無窮迴圈）。
- [ ] **Bounds Check:** If moving pointers inside the `while` loop (e.g., `while (left < right && nums[left] == nums[left+1]) left++`), did you check `left < right` again?
    **邊界檢查：** 如果在 `while` 迴圈內部移動指針（例如跳過重複項），你有再次檢查 `left < right` 嗎？

---

## 9. Memory Anchors (記憶錨點)

### "Closing the Curtains" (拉窗簾)
Imagine a large window. To find the perfect gap or match, you pull the curtains from both sides inward. This is **Collision Pointers**.
想像一扇大窗戶。為了找到完美的縫隙或配對，你從兩側向內拉窗簾。這就是 **對撞指針**。

### "The Tortoise and the Hare" (龜兔賽跑)
One runs fast, one runs slow. If there is a loop (circular track), they will meet. If it's a straight line, the fast one clears the path for the slow one (e.g., removing duplicates). This is **Fast & Slow Pointers**.
一隻跑得快，一隻跑得慢。如果有環（圓形跑道），牠們會相遇。如果是直線，快的那隻為慢的那隻清理路徑（例如移除重複項）。這就是 **快慢指針**。