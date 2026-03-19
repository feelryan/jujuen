Here is the complete interview preparation guide for Binary Search, tailored for a Senior Software Engineer, focusing on the Intermediate level and written in Java.
這是一份針對資深軟體工程師量身打造的二分搜尋法（Binary Search）面試完整指南，聚焦於中階難度，並使用 Java 撰寫。

---

# Binary Search Masterclass (Intermediate)
# 二分搜尋法大師班（中階）

## 1. Learning Objectives (學習目標)

*   **Master the Generalized Template:** Move beyond simple target finding to mastering the `left < right` template for finding boundaries.
    **掌握通用模板：** 超越單純的目標搜尋，掌握用於尋找邊界的 `left < right` 模板。
*   **Handle Rotated & Modified Arrays:** Solve problems where the sorting property is broken or modified (e.g., rotated arrays).
    **處理旋轉與變形陣列：** 解決排序屬性被破壞或修改的問題（例如旋轉陣列）。
*   **Apply "Binary Search on Answer":** Recognize problems where the solution space is monotonic, even if the input array is unsorted.
    **應用「對答案二分」：** 識別出解空間具備單調性的問題，即使輸入陣列未排序。
*   **Eliminate Off-by-One Errors:** Systematically avoid infinite loops and boundary bugs.
    **消除差一錯誤（Off-by-One Errors）：** 系統性地避免無窮迴圈與邊界 Bug。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Binary Search is a divide-and-conquer algorithm that repeatedly divides the search interval in half.
二分搜尋法是一種分治演算法，它重複地將搜尋區間減半。
It relies on the property of **monotonicity** (sorted order or a specific condition that splits the array into two distinct halves).
它依賴於**單調性**（排序順序或將陣列分為兩個截然不同部分的特定條件）。

### Complexity (複雜度)
*   **Time Complexity:** $O(\log N)$ — extremely efficient for large datasets.
    **時間複雜度：** $O(\log N)$ — 對於大型資料集極為高效。
*   **Space Complexity:** $O(1)$ iterative; $O(\log N)$ recursive (stack space).
    **空間複雜度：** 迭代法為 $O(1)$；遞迴法為 $O(\log N)$（堆疊空間）。

### When to Use (適用場景)
*   Finding an element in a sorted array.
    在已排序陣列中尋找元素。
*   Finding the first/last occurrence of a value (boundaries).
    尋找數值的第一次或最後一次出現（邊界）。
*   **Search on Solution Space:** Finding the minimum value that satisfies a condition (e.g., "min capacity", "max speed").
    **在解空間搜尋：** 尋找滿足條件的最小值（例如「最小容量」、「最大速度」）。

### When NOT to Use (不適用場景)
*   Small datasets (overhead might outweigh linear scan).
    小型資料集（開銷可能超過線性掃描）。
*   Unsorted data where sorting is too expensive ($O(N \log N)$).
    排序成本過高（$O(N \log N)$）的未排序資料。
*   Linked Lists (random access is not $O(1)$).
    鏈結串列（隨機存取不是 $O(1)$）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Standard Exact Match (標準精確匹配)
*   Loop: `while (left <= right)`
*   Update: `left = mid + 1`, `right = mid - 1`
*   Used for: Finding a specific index.
    用於：尋找特定索引。

### Pattern B: Finding Boundaries (Lower/Upper Bound) (尋找邊界)
*   Loop: `while (left < right)`
*   Update: `right = mid` (preserve potential answer) or `left = mid + 1`.
*   Used for: `first bad version`, `insertion point`, `minimum in rotated array`.
    用於：`第一個錯誤版本`、`插入點`、`旋轉陣列中的最小值`。

### Pattern C: Search in Rotated Sorted Array (旋轉排序陣列搜尋)
*   Logic: Determine which half is sorted, then check if target lies within that range.
    邏輯：判斷哪一半是有序的，然後檢查目標是否在該範圍內。

### Pattern D: Binary Search on Answer (對答案二分)
*   Context: The input is not sorted, but the range of possible answers (e.g., 1 to 10^9) is monotonic.
    情境：輸入未排序，但可能的答案範圍（如 1 到 10^9）是單調的。
*   Example: "Koko Eating Bananas", "Split Array Largest Sum".
    範例：「Koko 吃香蕉」、「分割陣列的最大值」。

---

## 4. Example Walkthrough (範例講解)

### Problem: Search in Rotated Sorted Array (LeetCode 33)
**Problem Statement:**
There is an integer array `nums` sorted in ascending order (with distinct values).
有一個整數陣列 `nums` 按升序排列（數值互不相同）。
Prior to being passed to your function, `nums` is possibly rotated at an unknown pivot index.
在傳遞給你的函式之前，`nums` 可能在未知的樞紐索引處進行了旋轉。
Given the array `nums` and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not.
給定陣列 `nums` 和一個整數 `target`，如果 `target` 在 `nums` 中，則返回其索引，否則返回 `-1`。

**Example:** `nums = [4,5,6,7,0,1,2]`, `target = 0` -> Output: `4`

---

### Approach (思路)

1.  **Brute Force (暴力解):**
    Linear scan. Time: $O(N)$.
    線性掃描。時間：$O(N)$。
    *Critique:* Does not utilize the sorted (albeit rotated) property.
    *評論：* 未利用排序（儘管已旋轉）的特性。

2.  **Optimization (優化):**
    We know that for any pivot, at least one half of the array remains sorted.
    我們知道對於任何樞紐，陣列中至少有一半保持排序。
    We can determine which half is sorted by comparing `nums[mid]` with `nums[left]`.
    我們可以通過比較 `nums[mid]` 和 `nums[left]` 來確定哪一半是有序的。

3.  **Algorithm (演算法):**
    *   If `nums[left] <= nums[mid]`: Left half is sorted.
        若 `nums[left] <= nums[mid]`：左半部有序。
    *   Check if `target` is in range `[nums[left], nums[mid]]`. If so, search left; else search right.
        檢查 `target` 是否在 `[nums[left], nums[mid]]` 範圍內。若是，搜左邊；否則搜右邊。
    *   Else: Right half is sorted.
        否則：右半部有序。
    *   Check if `target` is in range `[nums[mid], nums[right]]`.
        檢查 `target` 是否在 `[nums[mid], nums[right]]` 範圍內。

### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int search(int[] nums, int target) {
        // Boundary check
        // 邊界檢查
        if (nums == null || nums.length == 0) return -1;

        int left = 0;
        int right = nums.length - 1;

        // Use standard template allowing equality to handle single element
        // 使用允許相等的標準模板來處理單個元素
        while (left <= right) {
            // Avoid overflow: equivalent to (left + right) / 2 but safer
            // 避免溢位：等同於 (left + right) / 2 但更安全
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                return mid;
            }

            // Determine which part is sorted
            // 判斷哪一部分是有序的
            if (nums[left] <= nums[mid]) {
                // Left part is sorted
                // 左半部有序
                
                // Check if target is within the sorted left range
                // 檢查目標是否在有序的左半部範圍內
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1; // Target is in the left side / 目標在左側
                } else {
                    left = mid + 1;  // Target is in the right side / 目標在右側
                }
            } else {
                // Right part is sorted
                // 右半部有序
                
                // Check if target is within the sorted right range
                // 檢查目標是否在有序的右半部範圍內
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;  // Target is in the right side / 目標在右側
                } else {
                    right = mid - 1; // Target is in the left side / 目標在左側
                }
            }
        }

        return -1;
    }
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(\log N)$ because we discard half the array in every step.
    **時間：** $O(\log N)$，因為我們每一步都捨棄了一半的陣列。
*   **Space:** $O(1)$ as we only use pointers.
    **空間：** $O(1)$，因為我們只使用了指標。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Mid Calculation** | `left + (right - left) / 2` | `(left + right) / 2` causes integer overflow when left+right > 2^31-1. <br> `(left + right) / 2` 會在 left+right 超過整數上限時導致溢位。 |
| **Loop Condition** | `while (left <= right)` vs `while (left < right)` | Using `<=` when you need to narrow down to a single element boundary (often leads to infinite loop if logic isn't precise). <br> 當需要縮小到單一元素邊界時使用 `<=`（若邏輯不精確常導致無窮迴圈）。 |
| **Update Logic** | `right = mid` vs `right = mid - 1` | In `while(left < right)`, use `right = mid` to keep `mid` as a candidate. Using `mid - 1` might skip the answer. <br> 在 `while(left < right)` 中，使用 `right = mid` 來保留 `mid` 作為候選。使用 `mid - 1` 可能會跳過答案。 |
| **Duplicates** | `[1, 0, 1, 1, 1]` | Rotated array logic fails with duplicates because `nums[left] == nums[mid]` doesn't guarantee left side is sorted. Worst case becomes $O(N)$. <br> 旋轉陣列邏輯在有重複值時會失效，因為 `nums[left] == nums[mid]` 無法保證左側有序。最差情況變為 $O(N)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (闡述口條框架)
1.  **State the Invariant:** "I will maintain a search space `[left, right]` where the target, if it exists, must be within this range."
    **陳述不變量：** 「我將維護一個搜尋空間 `[left, right]`，如果目標存在，它必須在此範圍內。」
2.  **Justify Binary Search:** "Since the data shows monotonicity (or rotated sorted property), we can reduce the search space by half at each step."
    **證成二分搜尋：** 「由於資料顯示出單調性（或旋轉排序屬性），我們可以每一步將搜尋空間減半。」
3.  **Address Edge Cases:** "I will handle empty arrays and single-element arrays specifically."
    **處理邊界情況：** 「我會特別處理空陣列和單元素陣列。」

### Whiteboard Strategy (白板策略)
*   Write `left`, `right`, `mid` clearly.
    清楚寫出 `left`, `right`, `mid`。
*   **Dry Run Table:** Create a small table tracking `L`, `R`, `Mid`, `Val` to prove your loop terminates.
    **模擬執行表：** 建立一個小表格追蹤 `L`, `R`, `Mid`, `Val` 以證明你的迴圈會終止。

### Common Follow-ups (常見追問)
*   "What if the array contains duplicates?" (Requires skipping duplicates).
    「如果陣列包含重複值怎麼辦？」（需要跳過重複值）。
*   "What if the array is too large to fit in memory?" (Discuss distributed search or indexing).
    「如果陣列太大無法放入記憶體怎麼辦？」（討論分散式搜尋或索引）。

---

## 7. Practice Problems (練習題)

### 1. Easy: First Bad Version (LeetCode 278)
*   **Goal:** Find the first `true` in `[false, false, ..., true, true]`.
    **目標：** 在 `[false, false, ..., true, true]` 中找到第一個 `true`。
*   **Hint:** Use `while (left < right)` template. If `isBad(mid)`, `right = mid`; else `left = mid + 1`.
    **提示：** 使用 `while (left < right)` 模板。如果 `isBad(mid)`，則 `right = mid`；否則 `left = mid + 1`。

### 2. Medium: Find Minimum in Rotated Sorted Array (LeetCode 153)
*   **Goal:** Find the pivot point where the order resets.
    **目標：** 找到順序重置的樞紐點。
*   **Hint:** Compare `nums[mid]` with `nums[right]`. If `mid > right`, min is to the right.
    **提示：** 比較 `nums[mid]` 與 `nums[right]`。如果 `mid > right`，最小值在右邊。

### 3. Hard (Intermediate+): Koko Eating Bananas (LeetCode 875)
*   **Goal:** Find minimum speed `k` to eat all bananas within `h` hours.
    **目標：** 找到在 `h` 小時內吃完所有香蕉的最小速度 `k`。
*   **Hint:** **Binary Search on Answer**. The speed range is `[1, max(piles)]`. Define a helper function `canFinish(speed)` which is monotonic.
    **提示：** **對答案二分**。速度範圍是 `[1, max(piles)]`。定義一個單調的輔助函式 `canFinish(speed)`。

---

## 8. Quick Checklists (快速檢核表)

### Debugging Checklist (除錯檢核)
*   [ ] **Overflow:** Did I use `left + (right - left) / 2`?
    **溢位：** 我是否使用了 `left + (right - left) / 2`？
*   [ ] **Termination:** If `left = mid` or `right = mid` is used, does the loop condition (`<` vs `<=`) prevent infinite loops?
    **終止：** 如果使用了 `left = mid` 或 `right = mid`，迴圈條件（`<` vs `<=`）是否能防止無窮迴圈？
*   [ ] **Post-processing:** If loop ends with `left == right`, do I need to check `nums[left]` one last time?
    **後處理：** 如果迴圈結束時 `left == right`，我是否需要最後檢查一次 `nums[left]`？

### Complexity Check (複雜度確認)
*   [ ] Is the logic strictly cutting the space? (No linear scans inside the loop unless intended).
    邏輯是否嚴格地切割空間？（除非有意為之，否則迴圈內不應有線性掃描）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The Dictionary Game (字典遊戲)
Imagine finding a word in a physical dictionary. You don't read every page. You open the middle.
想像在實體字典中找一個單字。你不會每一頁都讀。你會打開中間。
*   If the word is alphabetically *after*, you discard the *left* chunk (throw it away mentally).
    如果單字按字母順序在*後面*，你會捨棄*左邊*那疊（在腦海中丟掉它）。
*   **Key:** You must be confident the answer is NOT in the discarded part.
    **關鍵：** 你必須確信答案**不**在被捨棄的那部分中。

### The "Shrinking Wall" (縮牆理論)
For `while (left < right)`:
對於 `while (left < right)`：
*   Imagine `left` and `right` are walls closing in.
    想像 `left` 和 `right` 是正在逼近的牆。
*   When `left == right`, the walls have crushed the search space into a single candidate. That is your answer (or the place to check).
    當 `left == right` 時，牆壁已經將搜尋空間擠壓成單一候選者。那就是你的答案（或需要檢查的地方）。