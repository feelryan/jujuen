# Advanced Two Pointers Interview Guide
# 進階雙指標面試指南

## 1. Learning Objectives (學習目標)

*   **Master Space Optimization:** Learn how to transform $O(N)$ space algorithms (using auxiliary arrays) into $O(1)$ space solutions using two pointers.
    **掌握空間優化：** 學習如何利用雙指標將 $O(N)$ 空間的演算法（使用輔助陣列）轉化為 $O(1)$ 空間的解法。
*   **Handle Complex Constraints:** Solve problems involving "at most K changes" or "3-way partitioning" efficiently.
    **處理複雜限制：** 有效解決涉及「最多 K 次修改」或「三路分區（3-way partitioning）」的問題。
*   **Prove Correctness:** Be able to articulate the mathematical intuition (monotonicity) behind why moving a pointer is safe, skipping redundant checks.
    **證明正確性：** 能夠清楚闡述移動指標為何是安全的（單調性），以及為何可以跳過多餘的檢查。
*   **Differentiate Patterns:** Clearly distinguish between Collision Pointers, Fast & Slow Pointers, and Sliding Window.
    **區分模式：** 清楚區分對撞指標、快慢指標與滑動視窗之間的差異。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Two Pointers is a technique where two distinct indices traverse a data structure (usually an array or linked list) to process data in linear time.
雙指標是一種技術，利用兩個不同的索引遍歷資料結構（通常是陣列或鏈結串列），以線性時間處理資料。

### Intuition (直覺)
The core power lies in turning nested loops ($O(N^2)$) into a single pass ($O(N)$) by utilizing the sorted property or specific logic to discard impossible solutions early.
其核心威力在於利用排序特性或特定邏輯提早排除不可能的解，將巢狀迴圈（$O(N^2)$）轉化為單次遍歷（$O(N)$）。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$.
    **時間：** 通常為 $O(N)$。
*   **Space:** $O(1)$ (In-place operations).
    **空間：** $O(1)$（原地操作）。

### When to Use (適用場景)
*   Processing sorted arrays (e.g., Two Sum II, 3Sum).
    處理已排序陣列（如：Two Sum II, 3Sum）。
*   In-place array manipulation (e.g., Remove Duplicates, Move Zeroes).
    原地陣列操作（如：移除重複項、移動零）。
*   Cycle detection or finding midpoints in Linked Lists.
    鏈結串列中的環檢測或尋找中點。
*   Partitioning algorithms (e.g., QuickSort partition).
    分區演算法（如：快速排序的分區）。

### When NOT to Use (不適用場景)
*   When the input data cannot be sorted and relative order matters (unless using Sliding Window).
    當輸入資料無法排序且相對順序很重要時（除非使用滑動視窗）。
*   When exact indices of the original unsorted array are required, and sorting destroys them (requires mapping).
    當需要原始未排序陣列的精確索引，而排序會破壞它們時（需要額外映射）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Collision Pointers (對撞指標)
*   **Concept:** One pointer starts at the beginning (`left = 0`), the other at the end (`right = n-1`). They move towards each other.
    **概念：** 一個指標從頭開始（`left = 0`），另一個從尾開始（`right = n-1`），兩者向中間移動。
*   **Use Case:** Binary Search, 2Sum/3Sum, Container With Most Water, Trapping Rain Water.
    **案例：** 二分搜尋、2Sum/3Sum、盛最多水的容器、接雨水。

### B. Fast & Slow Pointers (快慢指標)
*   **Concept:** Both pointers start at the same point, but one moves faster (e.g., 2 steps) than the other (1 step).
    **概念：** 兩個指標從同一點出發，但其中一個（如走 2 步）比另一個（走 1 步）移動得快。
*   **Use Case:** Cycle Detection (Floyd’s), Finding Middle of Linked List, Duplicate Number detection.
    **案例：** 環檢測（Floyd 演算法）、尋找鏈結串列中點、重複數字檢測。

### C. Multi-Pointers / Partitioning (多指標 / 分區)
*   **Concept:** Using 3 pointers (e.g., `low`, `mid`, `high`) to categorize elements into groups.
    **概念：** 使用 3 個指標（如 `low`、`mid`、`high`）將元素分類成不同群組。
*   **Use Case:** Sort Colors (Dutch National Flag problem).
    **案例：** 顏色分類（荷蘭國旗問題）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Trapping Rain Water (接雨水)
**Level:** Hard (Advanced Two Pointers)

#### Problem Statement (問題重述)
Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.
給定 `n` 個非負整數代表海拔高度圖，其中每個柱子的寬度為 1，計算下雨後它能接住多少水。

#### Approach 1: Brute Force (暴力法)
For each bar, find the maximum height to its left and right. The water level is `min(max_left, max_right) - current_height`.
對於每個柱子，找出其左邊和右邊的最大高度。水位高度為 `min(max_left, max_right) - current_height`。
*   **Time:** $O(N^2)$
*   **Space:** $O(1)$

#### Approach 2: Dynamic Programming (動態規劃)
Pre-compute `left_max` and `right_max` arrays.
預先計算 `left_max` 和 `right_max` 陣列。
*   **Time:** $O(N)$
*   **Space:** $O(N)$ (Interviewers will ask to optimize this. 面試官通常會要求優化此空間。)

#### Approach 3: Two Pointers (Optimal) (雙指標最佳解)
**Insight:** We don't need to store all max heights. If `left_max < right_max`, the water level at the `left` pointer is determined solely by `left_max`, regardless of what's between `left` and `right`.
**洞察：** 我們不需要儲存所有的最大高度。如果 `left_max < right_max`，則 `left` 指標處的水位僅由 `left_max` 決定，無論 `left` 和 `right` 之間有什麼。

#### TypeScript Solution (參考解)

```typescript
/**
 * Calculates the amount of trapped water using Two Pointers.
 * 使用雙指標計算接雨水量。
 *
 * Time Complexity: O(N) - Single pass. (單次遍歷)
 * Space Complexity: O(1) - Constant extra space. (常數額外空間)
 */
function trap(height: number[]): number {
    let left = 0;
    let right = height.length - 1;
    
    // Initialize max heights seen so far from both ends
    // 初始化從兩端觀測到的最大高度
    let leftMax = 0;
    let rightMax = 0;
    
    let totalWater = 0;

    while (left < right) {
        // We compare height[left] and height[right] to decide which pointer to move.
        // However, the core logic relies on leftMax and rightMax.
        // 我們比較 height[left] 與 height[right] 來決定移動哪個指標。
        // 但核心邏輯依賴於 leftMax 和 rightMax。
        
        if (height[left] < height[right]) {
            // If current left height is less than right, we know the bottleneck is on the left side
            // (or potentially leftMax). We don't care how tall the right side actually gets beyond this point.
            // 如果當前左邊高度小於右邊，我們知道瓶頸在左側（或是 leftMax）。
            // 我們不在乎右側在此之後到底有多高。
            
            if (height[left] >= leftMax) {
                // Update leftMax, no water can be trapped here
                // 更新 leftMax，此處無法接水
                leftMax = height[left];
            } else {
                // Water trapped = bottleneck - current height
                // 接水量 = 瓶頸高度 - 當前高度
                totalWater += leftMax - height[left];
            }
            left++;
        } else {
            // Similarly, if right side is smaller or equal, the bottleneck is determined by rightMax.
            // 同理，如果右側較小或相等，瓶頸由 rightMax 決定。
            
            if (height[right] >= rightMax) {
                // Update rightMax
                // 更新 rightMax
                rightMax = height[right];
            } else {
                // Calculate trapped water
                // 計算接水量
                totalWater += rightMax - height[right];
            }
            right--;
        }
    }

    return totalWater;
}
```

#### Why it works (為何有效)
The key is realizing that `min(max_left, max_right)` determines the water level. If `height[left] < height[right]`, then `max_left` (which is $\ge$ `height[left]`) is guaranteed to be smaller than some bar on the right (at least `height[right]`). Thus, we can safely process `left`.
關鍵在於理解 `min(max_left, max_right)` 決定了水位。如果 `height[left] < height[right]`，那麼 `max_left`（必然 $\ge$ `height[left]`）保證會小於右邊的某個柱子（至少是 `height[right]`）。因此，我們可以安全地處理 `left`。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Two Pointers (Collision) | Sliding Window |
| :--- | :--- | :--- |
| **Movement** | Usually `left++` AND `right--`. | Usually `right++` to expand, `left++` to shrink. |
| **Goal** | Find a pair or partition array. | Find a valid subarray/substring. |
| **Logic** | Decided by comparing ends. | Decided by window constraints (sum, count). |

**Common Mistakes (常見錯誤):**
1.  **Duplicate Handling in 3Sum:** Failing to skip identical values after finding a valid triplet, leading to duplicate results.
    **3Sum 中的重複處理：** 找到有效三元組後，忘記跳過相同的值，導致結果重複。
2.  **While Loop Condition:** Using `left <= right` vs `left < right`. In "Trapping Rain Water", pointers shouldn't cross or process the same index twice redundantly.
    **While 迴圈條件：** 使用 `left <= right` 還是 `left < right`。在「接雨水」中，指標不應交叉或重複處理同一索引。
3.  **Greedy Logic Flaws:** Assuming moving the smaller pointer is always correct without mathematical backing (e.g., in "Container With Most Water", moving the shorter line is the *only* way to potentially find a larger area).
    **貪婪邏輯缺陷：** 在沒有數學支持的情況下假設移動較小的指標總是正確的（例如在「盛最多水的容器」中，移動較短的線是*唯一*可能找到更大面積的方法）。

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **State the Naive Solution:** "Ideally, we could check every pair, but that's $O(N^2)$."
    **陳述樸素解法：** 「理想情況下，我們可以檢查每一對，但那是 $O(N^2)$。」
2.  **Propose Optimization:** "Since we are looking for a pair/boundary and the array is sorted (or has structural limits), we can use Two Pointers to reduce the search space."
    **提出優化：** 「由於我們在尋找配對或邊界，且陣列已排序（或有結構限制），我們可以使用雙指標來縮減搜尋空間。」
3.  **Define Invariants:** "I will maintain `left` and `right` such that all elements outside them are processed."
    **定義不變量：** 「我將維護 `left` 和 `right`，確保它們之外的所有元素都已被處理。」

### Whiteboard Strategy (白板策略)
*   Use descriptive names: `left/right` is better than `i/j` for collision; `slow/fast` is better for cycles.
    使用描述性名稱：對於對撞指標，`left/right` 優於 `i/j`；對於環檢測，`slow/fast` 更好。
*   Trace a small example (e.g., `[0, 1, 0, 2]`) manually before coding to verify logic.
    在寫程式碼之前，手動追蹤一個小範例（如 `[0, 1, 0, 2]`）以驗證邏輯。

### Common Follow-ups (常見追問)
*   **Q:** "What if the input is a data stream (infinite)?"
    **問：** 「如果輸入是資料流（無限的）怎麼辦？」
    *   **A:** Two pointers require random access. For streams, we might need a sliding window with a buffer or a monotonic stack.
    *   **答：** 雙指標需要隨機存取。對於資料流，我們可能需要帶緩衝區的滑動視窗或單調堆疊。

---

## 7. Practice Problems (練習題)

### Easy: Valid Palindrome (有效迴文)
*   **Hint:** Use `left` and `right`. Skip non-alphanumeric characters. Case insensitive.
    **提示：** 使用 `left` 和 `right`。跳過非字母數字字符。不區分大小寫。
*   **Focus:** Handling edge cases (empty string, all symbols).
    **重點：** 處理邊界情況（空字串、全符號）。

### Medium: 3Sum (三數之和)
*   **Hint:** Sort the array first ($O(N \log N)$). Iterate `i` from `0` to `n-2`, then use 2 pointers for the remaining part.
    **提示：** 先排序陣列 ($O(N \log N)$)。遍歷 `i` 從 `0` 到 `n-2`，然後對剩餘部分使用雙指標。
*   **Focus:** **Crucial:** Skip duplicates for `i`, `left`, and `right` to avoid duplicate triplets.
    **重點：** **關鍵：** 跳過 `i`、`left` 和 `right` 的重複值以避免重複的三元組。

### Hard: Sort Colors (Dutch National Flag) (顏色分類)
*   **Hint:** Use 3 pointers: `p0` (for 0s), `p2` (for 2s), and `curr` (iterator).
    **提示：** 使用 3 個指標：`p0`（放 0）、`p2`（放 2）和 `curr`（遍歷器）。
*   **Logic:**
    *   If `nums[curr] == 0`: swap with `p0`, `p0++`, `curr++`.
    *   If `nums[curr] == 2`: swap with `p2`, `p2--` (Don't increment `curr`! Need to check swapped value).
    *   If `nums[curr] == 1`: `curr++`.
*   **Focus:** In-place modification with one pass.
    **重點：** 單次遍歷的原地修改。

---

## 8. Quick Checklists (快速檢核表)

### Pre-coding (編碼前)
- [ ] Is the array sorted? If not, can I sort it? (Time complexity trade-off).
      陣列是否已排序？如果沒有，我可以排序嗎？（時間複雜度權衡）。
- [ ] Do I need to return indices or values? (Sorting destroys original indices).
      我需要返回索引還是值？（排序會破壞原始索引）。
- [ ] Will pointers collide (`left < right`) or cross (`left <= right`)?
      指標會對撞（`left < right`）還是交叉（`left <= right`）？

### Debugging (除錯中)
- [ ] Infinite loop? (Did I forget `left++` or `right--` in a specific `if` branch?)
      無限迴圈？（我是否在特定的 `if` 分支中忘記 `left++` 或 `right--`？）
- [ ] Out of bounds? (Check `right` initialization: `length` vs `length - 1`).
      越界？（檢查 `right` 初始化：是 `length` 還是 `length - 1`）。
- [ ] Missed duplicates? (Check inputs like `[-1, -1, 0, 1, 1]`).
      遺漏重複項？（檢查如 `[-1, -1, 0, 1, 1]` 的輸入）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Collision Pointers:** Like **"Closing the Curtains"**. You pull both sides towards the center until they meet.
    **對撞指標：** 就像 **「拉上窗簾」**。你將兩邊向中間拉，直到它們相遇。
*   **Container With Most Water:** Like **"Seeking the Tallest Partner"**. If you are the short line, you are the bottleneck, so you must move to find a taller partner. The tall line stays put because moving it can only decrease the area.
    **盛最多水的容器：** 就像 **「尋找最高伴侶」**。如果你是短的那條線，你就是瓶頸，所以你必須移動去尋找更高的伴侶。高的那條線保持不動，因為移動它只會減少面積。
*   **Dutch National Flag:** Like **"Sorting Laundry"**. One bin for whites (left), one for darks (right), and you examine the pile in the middle, tossing them to their respective bins immediately.
    **荷蘭國旗問題：** 就像 **「分類洗衣服」**。一個籃子放白色（左），一個放深色（右），你檢查中間的一堆衣服，立即將它們丟到各自的籃子裡。