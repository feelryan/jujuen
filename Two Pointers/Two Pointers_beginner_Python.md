# Two Pointers Interview Guide (Beginner Level)
# 雙指針面試指南（初級篇）

## 1. Learning Objectives
## 1. 學習目標

*   **Master the "Collision" and "Forward" paradigms.**
    掌握「對撞指針」與「同向指針」兩種核心範式。
*   **Identify the "Sorted" signal.**
    識別「已排序」這個關鍵信號。
*   **Optimize Space Complexity to $O(1)$.**
    將空間複雜度優化至 $O(1)$。
*   **Eliminate nested loops.**
    消除巢狀迴圈（將 $O(N^2)$ 優化為 $O(N)$）。

---

## 2. Core Concepts Overview
## 2. 核心觀念速覽

### Definition (定義)
Two Pointers is a technique where two indices iterate through a data structure (usually an array or string) in tandem to satisfy a specific constraint.
雙指針是一種技巧，使用兩個索引協同遍歷資料結構（通常是陣列或字串），以滿足特定約束條件。

### Intuition (直覺)
Instead of iterating through all possible pairs (Brute Force), we use the sorted property or the logic of the problem to greedily shrink the search space.
我們不遍歷所有可能的配對（暴力解），而是利用排序特性或問題邏輯，貪婪地縮小搜尋空間。

### Complexity (複雜度)
*   **Time:** Typically $O(N)$. We touch each element at most a constant number of times.
    **時間：** 通常為 $O(N)$。我們接觸每個元素頂多常數次。
*   **Space:** Typically $O(1)$. We only store two integer variables.
    **空間：** 通常為 $O(1)$。我們只儲存兩個整數變數。

### When to Use (適用場景)
*   **Sorted Arrays:** Finding pairs that sum to a target.
    **已排序陣列：** 尋找總和為目標值的配對。
*   **In-place Operations:** Removing duplicates or moving elements without extra memory.
    **原地操作：** 在不使用額外記憶體的情況下移除重複項或移動元素。
*   **Palindrome Checking:** Comparing characters from both ends.
    **迴文檢查：** 從兩端比較字元。

### When NOT to Use (不適用場景)
*   **Unsorted Data (where sorting is too expensive):** If preserving original indices matters.
    **未排序資料（且排序成本過高）：** 如果保留原始索引很重要。
*   **Complex Dependencies:** When the decision depends on more than just the two ends.
    **複雜依賴：** 當決策不僅僅取決於兩端時。

---

## 3. Typical Patterns
## 3. 典型題型 / 模式

### A. Collision Pointers (Opposite Direction)
### A. 對撞指針（反向）
*   **Setup:** One pointer at the start (`left = 0`), one at the end (`right = n - 1`).
    **設定：** 一個指針在起點 (`left = 0`)，一個在終點 (`right = n - 1`)。
*   **Action:** Move towards each other until they meet.
    **動作：** 彼此靠近直到相遇。
*   **Use Case:** Two Sum (Sorted), Valid Palindrome, Container With Most Water.
    **案例：** 兩數之和（已排序）、驗證迴文、盛最多水的容器。

### B. Slow & Fast Pointers (Same Direction)
### B. 快慢指針（同向）
*   **Setup:** Both start at 0, or `slow = 0`, `fast = 1`.
    **設定：** 兩者皆從 0 開始，或 `slow = 0`, `fast = 1`。
*   **Action:** `fast` explores, `slow` builds the result.
    **動作：** `fast` 負責探索，`slow` 負責建構結果。
*   **Use Case:** Remove Duplicates, Move Zeroes, Intersection of Two Arrays.
    **案例：** 移除重複項、移動零、兩個陣列的交集。

---

## 4. Example Walkthrough
## 4. 範例講解

### Problem: Two Sum II - Input Array Is Sorted
### 問題：兩數之和 II - 輸入陣列已排序

**Problem Statement:**
Given a **1-indexed** array of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number.
**問題重述：**
給定一個 **1-indexed** 的整數陣列 `numbers`，該陣列已按 **非遞減順序排序**，請找出兩個數字，使它們相加等於特定的 `target` 數字。

---

### Approach 1: Brute Force (暴力解)
Iterate through every pair `(i, j)` where `i < j`.
遍歷每一對 `(i, j)`，其中 `i < j`。

*   **Time:** $O(N^2)$ — Too slow for large inputs. (太慢，無法處理大輸入)
*   **Space:** $O(1)$.

### Approach 2: Binary Search (二分搜尋)
For each element `i`, binary search for `target - numbers[i]` in the rest of the array.
對於每個元素 `i`，在陣列其餘部分二分搜尋 `target - numbers[i]`。

*   **Time:** $O(N \log N)$ — Better, but not optimal. (較好，但非最佳)

### Approach 3: Two Pointers (Optimal) (雙指針 - 最佳解)
Since the array is sorted, we can use the sum to decide which pointer to move.
由於陣列已排序，我們可以用總和來決定移動哪個指針。

*   **Logic:**
    *   If `sum > target`: The sum is too big. We need a smaller number. Move `right` pointer to the left.
        若 `sum > target`：總和太大。我們需要較小的數字。將 `right` 指針向左移。
    *   If `sum < target`: The sum is too small. We need a larger number. Move `left` pointer to the right.
        若 `sum < target`：總和太小。我們需要較大的數字。將 `left` 指針向右移。
*   **Time:** $O(N)$ — Each element is visited at most once. (每個元素最多被訪問一次)
*   **Space:** $O(1)$.

---

### Python Reference Solution
### Python 參考解

```python
from typing import List

def twoSum(numbers: List[int], target: int) -> List[int]:
    # Initialize pointers at both ends
    # 初始化兩端的指針
    left, right = 0, len(numbers) - 1
    
    while left < right:
        current_sum = numbers[left] + numbers[right]
        
        if current_sum == target:
            # Problem asks for 1-based index
            # 題目要求 1-based 索引
            return [left + 1, right + 1]
        
        elif current_sum > target:
            # Sum is too large, decrease the larger element
            # 總和太大，減小較大的元素
            right -= 1
            
        else: # current_sum < target
            # Sum is too small, increase the smaller element
            # 總和太小，增大較小的元素
            left += 1
            
    # Should not reach here based on problem constraints (guaranteed solution)
    # 根據題目約束（保證有解），不應執行到此處
    return []
```

---

### Common Mistake (錯誤示範)
Using a Hash Map (Dictionary) for this specific problem.
針對此特定問題使用雜湊表（字典）。

*   **Why it's suboptimal:** While it is $O(N)$ time, it uses $O(N)$ space. In a Senior interview, failing to leverage the "sorted" property to save memory is a red flag.
    **為何非最佳：** 雖然時間是 $O(N)$，但使用了 $O(N)$ 空間。在資深面試中，未能利用「已排序」特性來節省記憶體是一個警訊。

---

## 5. Common Pitfalls & Confusions
## 5. 常見陷阱與易混淆概念

| Concept | Description (描述) | Warning (警示) |
| :--- | :--- | :--- |
| **While Condition** | `left < right` vs `left <= right` | For "Two Sum", use `<` (distinct elements). For "Palindrome" or "Reverse Array", `<=` might be needed to handle the middle element. <br> 對於「兩數之和」，使用 `<`（不同元素）。對於「迴文」或「反轉陣列」，可能需要 `<=` 來處理中間元素。 |
| **Infinite Loop** | Pointers not moving | Ensure every branch of your `if/else` logic moves at least one pointer. <br> 確保 `if/else` 邏輯的每個分支都至少移動一個指針。 |
| **Duplicate Handling** | Skipping repeated values | In problems like "3Sum", you must manually `while` loop to skip duplicates to avoid repeated result sets. <br> 在像「三數之和」這樣的問題中，必須手動使用 `while` 迴圈跳過重複項，以避免重複的結果集。 |

---

## 6. Interview Strategy
## 6. 面試實戰建議

### Communication Framework (口條框架)
1.  **Identify the Invariant:** "I will maintain a window defined by `left` and `right`."
    **確認不變性：** 「我將維護一個由 `left` 和 `right` 定義的視窗。」
2.  **Justify the Move:** "Since the array is sorted, moving the right pointer left is the *only* way to reduce the sum."
    **證成移動邏輯：** 「由於陣列已排序，將右指針向左移是減少總和的 *唯一* 方法。」
3.  **Discuss Trade-offs:** "This approach avoids the $O(N)$ space of a hash map at the cost of requiring sorted input."
    **討論權衡：** 「這種方法避免了雜湊表的 $O(N)$ 空間，代價是需要已排序的輸入。」

### Whiteboard Strategy (白板策略)
*   Draw the array indices explicitly (0 to N-1).
    明確畫出陣列索引（0 到 N-1）。
*   Use arrows ($\uparrow$) to represent pointers `L` and `R`.
    使用箭頭 ($\uparrow$) 代表指針 `L` 和 `R`。
*   Trace one iteration: "Current sum is 15, target is 9, so R moves left."
    追蹤一次迭代：「目前總和是 15，目標是 9，所以 R 向左移。」

### Common Follow-up (常見追問)
*   **Q:** What if the array is stored on disk and is too huge for memory?
    **問：** 如果陣列儲存在磁碟上且太大無法放入記憶體怎麼辦？
*   **A:** Two pointers still works if we can seek/read from ends. However, caching becomes critical.
    **答：** 如果我們可以從兩端讀取/搜尋，雙指針仍然有效。然而，快取機制變得至關重要。

---

## 7. Practice Problems
## 7. 練習題

### Level: Easy (簡單)
**Problem:** **Valid Palindrome** (LeetCode 125)
**Hint:** Use `left` and `right` pointers. Skip non-alphanumeric characters. Compare `lower()` case.
**提示：** 使用 `left` 和 `right` 指針。跳過非字母數字字符。比較 `lower()` 小寫。

### Level: Medium (中等)
**Problem:** **3Sum** (LeetCode 15)
**Hint:** Sort the array first. Iterate `i` from `0` to `n`. For each `i`, run "Two Sum" on the rest of the array (`i+1` to `n`) to find target `-nums[i]`. **Crucial:** Skip duplicates for both `i` and the pointers.
**提示：** 先排序陣列。遍歷 `i` 從 `0` 到 `n`。對於每個 `i`，在陣列其餘部分（`i+1` 到 `n`）執行「兩數之和」以尋找 `-nums[i]`。**關鍵：** 對 `i` 和指針都要跳過重複項。

### Level: Hard (困難)
**Problem:** **Trapping Rain Water** (LeetCode 42)
**Hint:** This is a "Collision" pattern optimization. Maintain `max_left` and `max_right`. Calculate water based on the smaller of the two max heights, moving the pointer of the smaller side.
**提示：** 這是「對撞」模式的優化。維護 `max_left` 和 `max_right`。根據兩個最大高度中較小的一個來計算水量，並移動較小那邊的指針。

---

## 8. Quick Checklists
## 8. 快速檢核表

*   [ ] **Sorted?** Did I confirm the input is sorted? If not, did I sort it? ($O(N \log N)$)
    **已排序？** 我確認輸入已排序了嗎？如果沒有，我排序了嗎？
*   [ ] **Bounds?** Did I check `left < right` or `left <= right` correctly?
    **邊界？** 我是否正確檢查了 `left < right` 或 `left <= right`？
*   [ ] **Movement?** Does every loop iteration guarantee a pointer move? (Avoid infinite loops)
    **移動？** 每次迴圈迭代是否保證指針移動？（避免無窮迴圈）
*   [ ] **0/1 Indexing?** Does the problem require returning 0-based or 1-based indices?
    **0/1 索引？** 題目要求返回 0-based 還是 1-based 索引？

---

## 9. Memory Anchors & Analogies
## 9. 記憶錨點與類比

### The Telescope (望遠鏡)
Imagine a telescope focusing. You start with a wide view (pointers at ends). You adjust the lens (move pointers inward) to find the sharpest image (the target pair).
想像望遠鏡對焦。你從廣角開始（指針在兩端）。你調整鏡頭（向內移動指針）以找到最清晰的影像（目標配對）。

### The Meeting (會面)
Two friends walking towards each other on a street to meet. If they haven't met yet (`left < right`), they keep walking. If they pass each other, the loop ends.
兩個朋友在街上相向而行準備會面。如果他們還沒相遇 (`left < right`)，他們繼續走。如果他們錯過了彼此，迴圈結束。