# Binary Search: The Foundation (Beginner)
# 二分搜尋法：基礎篇

## 1. Learning Objectives (學習目標)

*   **Master the Standard Template:** Implement bug-free binary search without memorizing code, understanding the logic behind loop conditions.
    **掌握標準模板：** 在不死記硬背的情況下實作無 bug 的二分搜尋，理解迴圈條件背後的邏輯。
*   **Understand the Invariant:** Learn how to define and maintain the search space correctly to avoid infinite loops.
    **理解不變性：** 學習如何正確定義並維護搜索空間，以避免無窮迴圈。
*   **Recognize Applicability:** Instantly identify when Binary Search is the optimal solution (e.g., sorted arrays, monotonic functions).
    **識別適用性：** 能立即判斷何時二分搜尋是最佳解（例如：已排序陣列、單調函數）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Binary Search is an efficient algorithm for finding an item from a sorted list of items.
二分搜尋法是一種在已排序清單中尋找項目的高效演算法。
It works by repeatedly dividing in half the portion of the list that could contain the item, until you've narrowed down the possible locations to just one.
它的運作方式是反覆將可能包含該項目的清單部分對半分割，直到將可能的位置縮小到僅剩一個。

### Intuition (直覺)
Think of looking up a word in a physical dictionary.
想像在實體字典中查單字。
You open the book in the middle; if the word you seek is alphabetically after the current page, you ignore the left half and repeat the process on the right half.
你從中間翻開書；如果你要找的字按字母順序在當前頁面之後，你就忽略左半部，並在右半部重複此過程。

### Complexity (複雜度)
*   **Time Complexity:** $O(\log N)$ — The search space is halved in every step.
    **時間複雜度：** $O(\log N)$ — 搜索空間在每一步都會減半。
*   **Space Complexity:** $O(1)$ — It requires constant extra space for pointers (iterative approach).
    **空間複雜度：** $O(1)$ — 僅需常數額外空間來儲存指標（迭代法）。

### When to Use (適用場景)
*   Finding an element in a **sorted** array.
    在**已排序**陣列中尋找元素。
*   Finding a specific value where a function switches from false to true (monotonic properties).
    尋找函數從 false 轉變為 true 的特定值（單調性質）。

### When NOT to Use (不適用場景)
*   Unsorted data (unless sorting first is acceptable and fits within time limits).
    未排序的資料（除非先排序是可接受的，且符合時間限制）。
*   Linked Lists (random access is $O(N)$, negating the benefit).
    鏈結串列（隨機存取是 $O(N)$，抵消了二分搜尋的優勢）。
*   Very small datasets (linear scan might be faster due to CPU cache locality and lower overhead).
    非常小的資料集（由於 CPU 快取局部性和較低的開銷，線性掃描可能會更快）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the **Beginner** level, we focus on the most fundamental pattern:
針對 **基礎** 級別，我們專注於最基本的模式：

### Pattern 1: Standard Exact Match (標準精確匹配)
*   **Goal:** Find the index of a specific `target` value.
    **目標：** 尋找特定 `target` 值的索引。
*   **Condition:** `nums[mid] == target`.
    **條件：** `nums[mid] == target`。
*   **Outcome:** Return index if found, otherwise return -1.
    **結果：** 若找到則回傳索引，否則回傳 -1。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Search (Classic)
### 問題：二分搜尋（經典題）

**Problem Statement (問題重述):**
Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.
給定一個按升序排列的整數陣列 `nums` 和一個整數 `target`，寫一個函數在 `nums` 中搜尋 `target`。如果 `target` 存在，則回傳其索引。否則，回傳 `-1`。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Iterate through the array from start to finish.
        從頭到尾遍歷陣列。
    *   Time: $O(N)$. Too slow for large inputs.
        時間：$O(N)$。對於大型輸入來說太慢。

2.  **Optimal Solution (Binary Search):**
    *   Define two pointers, `left` and `right`, representing the current search space.
        定義兩個指標 `left` 和 `right`，代表當前的搜索空間。
    *   Calculate the middle index `mid`.
        計算中間索引 `mid`。
    *   Compare `nums[mid]` with `target`.
        比較 `nums[mid]` 與 `target`。
    *   Adjust `left` or `right` to discard the half that cannot contain the target.
        調整 `left` 或 `right` 以捨棄不可能包含目標的那一半。

### Code Implementation (Python)

```python
from typing import List

def search(nums: List[int], target: int) -> int:
    # Initialize pointers to the start and end of the array
    # 初始化指標指向陣列的開頭與結尾
    left = 0
    right = len(nums) - 1
    
    # Loop as long as the search space is valid (left <= right)
    # 只要搜索空間有效（left <= right），就繼續迴圈
    # Key Note: We use <= because the target could be at the index where left == right
    # 關鍵註記：我們使用 <= 是因為目標可能位於 left == right 的索引處
    while left <= right:
        
        # Calculate mid to avoid potential integer overflow (though Python handles large ints automatically)
        # 計算 mid 以避免潛在的整數溢位（雖然 Python 會自動處理大整數）
        # Standard formula: left + (right - left) // 2
        # 標準公式：left + (right - left) // 2
        mid = left + (right - left) // 2
        
        if nums[mid] == target:
            # Target found, return the index
            # 找到目標，回傳索引
            return mid
        elif nums[mid] < target:
            # Target is in the right half, discard left half
            # 目標在右半部，捨棄左半部
            # We use mid + 1 because we know nums[mid] is not the target
            # 我們使用 mid + 1，因為我們知道 nums[mid] 不是目標
            left = mid + 1
        else:
            # Target is in the left half, discard right half
            # 目標在左半部，捨棄右半部
            # We use mid - 1 because we know nums[mid] is not the target
            # 我們使用 mid - 1，因為我們知道 nums[mid] 不是目標
            right = mid - 1
            
    # Target not found
    # 未找到目標
    return -1
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(\log N)$ - Base 2 logarithm. For $10^6$ elements, it takes only ~20 comparisons.
    **時間：** $O(\log N)$ - 以 2 為底的對數。對於 $10^6$ 個元素，僅需約 20 次比較。
*   **Space:** $O(1)$ - No extra data structures used.
    **空間：** $O(1)$ - 未使用額外資料結構。

### Common Mistake Demonstration (錯誤示範)

```python
# WRONG: Infinite Loop Risk
# 錯誤：無窮迴圈風險
while left <= right:
    mid = (left + right) // 2
    if nums[mid] < target:
        left = mid  # Mistake! If left == mid, this loops forever.
                    # 錯誤！如果 left == mid，這會造成無窮迴圈。
    else:
        right = mid 
```
*   **Why it's wrong:** If you don't exclude `mid` (by doing `mid + 1` or `mid - 1`), the search space might not shrink when only 2 elements remain, causing an infinite loop.
    **為何錯誤：** 如果你不排除 `mid`（透過 `mid + 1` 或 `mid - 1`），當僅剩 2 個元素時，搜索空間可能不會縮小，導致無窮迴圈。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept (概念) | `while left <= right` | `while left < right` |
| :--- | :--- | :--- |
| **Use Case (用途)** | Standard search (find exact index). <br> 標準搜尋（尋找確切索引）。 | Finding boundaries (first/last occurrence). <br> 尋找邊界（第一次/最後一次出現）。 |
| **Termination (終止)** | Loop ends when `left > right`. <br> 當 `left > right` 時迴圈結束。 | Loop ends when `left == right`. <br> 當 `left == right` 時迴圈結束。 |
| **Update Rule (更新規則)** | `left = mid + 1`, `right = mid - 1` | Often `right = mid` or `left = mid + 1`. <br> 通常是 `right = mid` 或 `left = mid + 1`。 |
| **Post-processing (後處理)** | Usually not needed. <br> 通常不需要。 | Need to check `nums[left]` after loop. <br> 迴圈後需要檢查 `nums[left]`。 |

**Beginner Tip:** Stick to `while left <= right` for simple "find the value" problems. It's the most intuitive.
**初學者建議：** 對於簡單的「尋找數值」問題，堅持使用 `while left <= right`。這是最直觀的。

---

## 6. Interview Strategy (面試實戰建議)

### Clarification (釐清需求)
*   "Is the input array guaranteed to be sorted?"
    「輸入陣列保證是已排序的嗎？」
*   "Are there duplicate values?" (Duplicates affect how we handle finding specific indices).
    「會有重複的值嗎？」（重複值會影響我們尋找特定索引的方式）。

### Whiteboard Strategy (白板策略)
*   **Write the bounds first:** Define `left` and `right` clearly.
    **先寫邊界：** 清楚定義 `left` 和 `right`。
*   **State the invariant:** "I am searching for the target within the closed interval `[left, right]`."
    **陳述不變性：** 「我正在閉區間 `[left, right]` 內搜尋目標。」
*   **Handle Overflow:** Verbally mention `mid = left + (right - left) // 2` shows seniority, even if Python doesn't strictly need it.
    **處理溢位：** 口頭提及 `mid = left + (right - left) // 2` 能展現資深度，即使 Python 嚴格來說不需要它。

### Common Follow-up (常見追問)
*   "What if the array is too large to fit in memory?" (Distributed search / Indexing).
    「如果陣列太大無法放入記憶體怎麼辦？」（分散式搜尋 / 索引）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Binary Search (Standard)
*   **LeetCode 704:** Given sorted array, find target.
    **LeetCode 704:** 給定已排序陣列，尋找目標。
*   **Hint:** Use the standard template `left <= right`.
    **提示：** 使用標準模板 `left <= right`。

### 2. Medium (Beginner-Friendly): Search Insert Position
*   **LeetCode 35:** Return the index where the target would be if it were inserted in order.
    **LeetCode 35:** 回傳目標若按順序插入時應所在的索引。
*   **Hint:** If target is not found, `left` will end up at the insertion point.
    **提示：** 如果未找到目標，`left` 最終會停在插入點。
*   **Key Insight:** The loop terminates when `left > right`. The `left` pointer indicates the first element greater than target.
    **關鍵洞察：** 迴圈在 `left > right` 時終止。`left` 指標指向第一個大於目標的元素。

### 3. Medium (Concept): Sqrt(x)
*   **LeetCode 69:** Compute the square root of x (integer part).
    **LeetCode 69:** 計算 x 的平方根（整數部分）。
*   **Hint:** Binary search on the **answer space** (from 0 to x). If `mid * mid > x`, search left.
    **提示：** 在**答案空間**（從 0 到 x）進行二分搜尋。如果 `mid * mid > x`，向左搜尋。

---

## 8. Quick Checklists (快速檢核表)

### Pre-coding Check (編碼前檢查)
*   [ ] Is the data sorted? (資料是否已排序？)
*   [ ] Can I access elements by index in $O(1)$? (能否以 $O(1)$ 透過索引存取元素？)

### Debugging Check (除錯檢查)
*   [ ] **Termination:** Did I use `left <= right`? (If yes, did I update `left = mid + 1` and `right = mid - 1`?)
    **終止條件：** 我是否使用了 `left <= right`？（若是，我是否更新了 `left = mid + 1` 和 `right = mid - 1`？）
*   [ ] **Mid Calculation:** Did I handle potential overflow? `left + (right - left) // 2`.
    **中間值計算：** 我是否處理了潛在的溢位？`left + (right - left) // 2`。
*   [ ] **Return Value:** Did I return `-1` or `left` depending on the requirement?
    **回傳值：** 我是否根據需求回傳了 `-1` 或 `left`？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Guess the Number" Game (「猜數字」遊戲)
*   **Scenario:** I pick a number between 1 and 100. You guess 50.
    **情境：** 我選了一個 1 到 100 之間的數字。你猜 50。
*   **Feedback:** I say "Too high".
    **回饋：** 我說「太大了」。
*   **Action:** You intuitively discard 50–100. Your new range is 1–49.
    **動作：** 你直覺地捨棄了 50–100。你的新範圍是 1–49。
*   **Analogy:**
    *   Your guess = `mid`
    *   "Too high" = `nums[mid] > target` -> `right = mid - 1`
    *   "Too low" = `nums[mid] < target` -> `left = mid + 1`

### Visual Anchor (視覺錨點)
Imagine two walls (`left` and `right`) closing in on a suspect.
想像兩堵牆（`left` 和 `right`）向嫌疑犯逼近。
Every step, one wall jumps halfway towards the other. They must cross each other (`left > right`) for the search to end if the suspect isn't found.
每一步，其中一堵牆會跳躍一半的距離靠近另一堵牆。如果沒找到嫌疑犯，它們必須互相交叉（`left > right`），搜尋才會結束。