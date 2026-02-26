# Binary Search Masterclass for Senior Engineers
# 資深工程師二分搜尋法大師班

## 1. Learning Objectives（學習目標）

*   **Master the Generalized Definition**: Understand that Binary Search is not just for sorted arrays, but for any **monotonic function** or search space.
    **掌握廣義定義**：理解二分搜尋不僅適用於排序陣列，更適用於任何具備 **單調性函數** 或搜索空間。
*   **Eliminate "Off-by-One" Errors**: Adopt a consistent template to handle loop invariants and boundary conditions, banishing infinite loops forever.
    **消除「差一錯誤」**：採用一致的模板來處理迴圈不變量與邊界條件，徹底杜絕無窮迴圈。
*   **Apply "Binary Search on Answer"**: Learn to transform optimization problems (min-max/max-min) into decision problems.
    **應用「對答案二分」**：學會將最佳化問題（極大化最小值/極小化最大值）轉化為判定問題。
*   **Identify Implicit Monotonicity**: Recognize when a problem has a hidden sorted property (e.g., rotated arrays, matrices).
    **識別隱性單調性**：辨識問題中隱藏的排序特性（例如：旋轉陣列、矩陣）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Binary Search is a divide-and-conquer strategy that iteratively halves the search space.
二分搜尋是一種「分治」策略，透過迭代將搜索空間減半。

**Key Requirement: Monotonicity (關鍵要求：單調性)**
It requires the search space to be monotonic (e.g., sorted values `[1, 3, 5...]` or a boolean predicate `[F, F, F, T, T, T]`).
它要求搜索空間必須具備單調性（例如：排序數值 `[1, 3, 5...]` 或布林判定 `[F, F, F, T, T, T]`）。

### Complexity（複雜度）
*   **Time Complexity**: $O(\log N)$ — extremely efficient; feasible even when $N = 10^{18}$.
    **時間複雜度**：$O(\log N)$ — 極度高效；即便 $N = 10^{18}$ 也是可行的。
*   **Space Complexity**: $O(1)$ iterative; $O(\log N)$ recursive (stack space).
    **空間複雜度**：迭代解法為 $O(1)$；遞迴解法為 $O(\log N)$（堆疊空間）。

### When to Use / Not Use（適用與不適用場景）
*   **Use when**: Input is sorted, or you are looking for a boundary in a monotonic function.
    **適用時機**：輸入已排序，或你正在單調函數中尋找邊界。
*   **Don't use when**: Data is unsorted and small (use Linear Search), or data structure is a Linked List (random access is $O(N)$).
    **不適用時機**：資料未排序且量少（使用線性搜尋），或資料結構是鏈結串列（隨機存取需 $O(N)$）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Standard Exact Match（標準精確匹配）
Looking for a specific value `target`. Returns index or -1.
尋找特定數值 `target`。回傳索引值或 -1。
*   *Template:* `while left <= right:`

### Pattern B: Find Boundary / Insertion Point (Lower/Upper Bound)（尋找邊界 / 插入點）
Looking for the first value `>= target` or the last value `<= target`. This is critical for handling duplicates.
尋找第一個 `>= target` 的值或最後一個 `<= target` 的值。這對於處理重複元素至關重要。
*   *Template:* `while left < right:` (Converges to a single element / 收斂至單一元素)

### Pattern C: Binary Search on Answer / Solution Space（對答案/解空間進行二分）
Instead of searching an array, we search the range of possible answers (e.g., "What is the minimum capacity required?").
我們不搜尋陣列，而是搜尋可能答案的範圍（例如：「所需的最小容量是多少？」）。
*   *Strategy:* Define a helper function `check(value) -> bool`.
    *策略：* 定義一個輔助函數 `check(value) -> bool`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Koko Eating Bananas (LC 875)
**Level**: Medium (Classic "Search on Answer" pattern)
**難度**：中等（經典的「對答案二分」模式）

#### Problem Statement（問題重述）
Koko loves to eat bananas. There are `n` piles of bananas, the `i-th` pile has `piles[i]` bananas. The guards have gone and will come back in `h` hours.
Koko 愛吃香蕉。這裡有 `n` 堆香蕉，第 `i` 堆有 `piles[i]` 根香蕉。警衛離開了，並將在 `h` 小時後回來。

Koko can decide her bananas-per-hour eating speed of `k`. Each hour, she chooses some pile of bananas and eats `k` bananas from that pile.
Koko 可以決定她每小時吃香蕉的速度 `k`。每個小時，她選擇某一堆香蕉並從中吃掉 `k` 根。

Return the minimum integer `k` such that she can eat all the bananas within `h` hours.
請回傳最小的整數 `k`，讓她能在 `h` 小時內吃完所有香蕉。

#### Approach & Thought Process（思路）

1.  **Brute Force (暴力法)**:
    *   Try speed $k=1$, check if valid. Then $k=2, k=3...$ until valid.
    *   從速度 $k=1$ 開始嘗試，檢查是否可行。接著 $k=2, k=3...$ 直到可行。
    *   Complexity: $O(max(piles) \cdot N)$. Too slow if piles are huge.
    *   複雜度：$O(max(piles) \cdot N)$。若香蕉堆很大則太慢。

2.  **Optimization (優化)**:
    *   Notice the **Monotonicity**: If Koko can finish with speed `k`, she can definitely finish with speed `k+1`. If she fails with `k`, she fails with `k-1`.
    *   注意 **單調性**：如果 Koko 能以速度 `k` 吃完，她絕對也能以速度 `k+1` 吃完。如果她以 `k` 失敗，則 `k-1` 也必失敗。
    *   The solution space for `k` is `[1, max(piles)]`. We can binary search this range.
    *   `k` 的解空間為 `[1, max(piles)]`。我們可以對此範圍進行二分搜尋。

3.  **Optimal Solution (最佳解)**:
    *   Define `can_finish(k)`: Returns `True` if total hours needed <= `h`.
    *   定義 `can_finish(k)`：若所需總時數 <= `h` 則回傳 `True`。
    *   Find the **leftmost** `k` (smallest) where `can_finish(k)` is True.
    *   尋找 **最左側**（最小）的 `k`，使得 `can_finish(k)` 為真。

#### Python Reference Solution（Python 參考解）

```python
import math
from typing import List

class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        # Define the search space for speed k
        # 定義速度 k 的搜索空間
        # Lower bound is 1 (min speed), Upper bound is max pile (eating more than max pile per hour is wasteful)
        # 下界為 1（最小速度），上界為最大堆（每小時吃超過最大堆是浪費的）
        left, right = 1, max(piles)

        def can_finish(speed: int) -> bool:
            """
            Helper predicate: Can we finish all piles within h hours at this speed?
            輔助判定函數：以此速度是否能在 h 小時內吃完所有香蕉堆？
            """
            hours_needed = 0
            for pile in piles:
                # Ceiling division: (pile + speed - 1) // speed is equivalent to math.ceil(pile / speed)
                # 向上取整除法：(pile + speed - 1) // speed 等同於 math.ceil(pile / speed)
                hours_needed += (pile + speed - 1) // speed
            
            return hours_needed <= h

        # Binary Search Template (Finding the Left Boundary)
        # 二分搜尋模板（尋找左邊界）
        while left < right:
            mid = left + (right - left) // 2
            
            if can_finish(mid):
                # If we can finish, try a smaller speed (search left half)
                # potentially mid itself could be the answer, so right = mid
                # 若能吃完，嘗試更小的速度（搜尋左半部）
                # mid 本身可能是答案，因此 right = mid
                right = mid
            else:
                # If we cannot finish, we need a faster speed
                # mid is definitely not the answer, so left = mid + 1
                # 若吃不完，我們需要更快的速度
                # mid 絕對不是答案，因此 left = mid + 1
                left = mid + 1
        
        # When left == right, we found the minimum speed
        # 當 left == right 時，我們找到了最小速度
        return left

# Complexity Analysis:
# Time: O(N * log(M)), where N is len(piles) and M is max(piles).
# Space: O(1).
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **`while lo <= hi` vs `while lo < hi`** | **`lo <= hi`**: Used when searching for a specific value. Loop ends when search space is empty. <br> **`lo < hi`**: Used when searching for a boundary (like the example above). Loop ends when `lo == hi` (converged). <br> **`lo <= hi`**：用於尋找特定值。當搜索空間為空時迴圈結束。<br> **`lo < hi`**：用於尋找邊界（如上例）。當 `lo == hi` 時迴圈結束（收斂）。 |
| **Mid Calculation Overflow** | `mid = (lo + hi) // 2` can overflow in languages like C++/Java if `lo + hi` > MAX_INT. <br> **Safe way**: `mid = lo + (hi - lo) // 2`. Python handles large integers automatically, but it's good practice to know this. <br> `mid = (lo + hi) // 2` 在 C++/Java 等語言中若 `lo + hi` > MAX_INT 會溢位。<br> **安全寫法**：`mid = lo + (hi - lo) // 2`。Python 會自動處理大整數，但了解這一點是好習慣。 |
| **Infinite Loops (Deadlock)** | Often happens with `lo < hi` if `mid` calculation biases incorrectly. <br> If `left = mid`, then `mid` must be biased right: `(left + right + 1) // 2`. <br> If `right = mid`, then `mid` must be biased left: `(left + right) // 2`. <br> 常發生於 `lo < hi` 且 `mid` 計算偏差錯誤時。<br> 若 `left = mid`，則 `mid` 必須偏右：`(left + right + 1) // 2`。<br> 若 `right = mid`，則 `mid` 必須偏左：`(left + right) // 2`。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **Identify Monotonicity**: "I notice the problem asks for a minimum value, and the feasibility function is monotonic. This suggests Binary Search on the answer."
    **識別單調性**：「我注意到題目要求最小值，且可行性函數具備單調性。這提示可以使用對答案二分搜尋。」
2.  **Define Search Space**: "The possible range for the answer is from `min_possible` to `max_possible`."
    **定義搜索空間**：「答案的可能範圍是從 `min_possible` 到 `max_possible`。」
3.  **Define Predicate**: "I will implement a helper function `check(x)` that returns true if `x` satisfies the condition."
    **定義判定函數**：「我將實作一個輔助函數 `check(x)`，若 `x` 滿足條件則回傳 true。」

### Whiteboard Strategy（白板策略）
*   **Write the Template First**: Don't think, just write the standard `while left < right` structure. It buys you time to think about the logic inside.
    **先寫模板**：不要思考，直接寫下標準的 `while left < right` 結構。這能為你爭取思考內部邏輯的時間。
*   **Dry Run Edge Cases**: Before saying "I'm done," manually trace an array of size 1 and size 2.
    **手動執行邊界情況**：在說「我完成了」之前，手動追蹤大小為 1 和 2 的陣列。

### Common Follow-ups（常見追問）
*   **Q**: What if the array is too large to fit in memory?
    **問**：如果陣列太大無法放入記憶體怎麼辦？
*   **A**: We can use a distributed file system or database. Binary search still works by seeking to specific offsets in the file (Random Access).
    **答**：我們可以使用分散式檔案系統或資料庫。二分搜尋仍然有效，透過在檔案中尋找特定偏移量（隨機存取）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Binary Search (Standard)
*   **Problem**: Given a sorted array, find the index of target. (LC 704)
*   **Hint**: Use `while left <= right`. Handle `mid + 1` and `mid - 1`.
*   **提示**：使用 `while left <= right`。處理 `mid + 1` 與 `mid - 1`。

### 2. Medium: Search in Rotated Sorted Array
*   **Problem**: Array is sorted but rotated at an unknown pivot. Find target. (LC 33)
*   **Hint**: One half of the array (left or right of mid) is always sorted. Check which side is sorted first, then decide where to move.
*   **提示**：陣列的一半（mid 的左側或右側）總是排序好的。先檢查哪一邊是有序的，再決定往哪裡移動。

### 3. Intermediate/Hard: Split Array Largest Sum
*   **Problem**: Split array into `m` subarrays such that the largest sum among them is minimized. (LC 410)
*   **Hint**: This is "Search on Answer". Range is `[max(nums), sum(nums)]`. Predicate: "Can we split into <= m subarrays with max sum `mid`?"
*   **提示**：這是「對答案二分」。範圍是 `[max(nums), sum(nums)]`。判定函數：「我們能否在最大和為 `mid` 的限制下，將其分割為 <= m 個子陣列？」

---

## 8. Quick Checklists（快速檢核表）

**Self-Review before running code (執行程式碼前的自我審查):**

- [ ] **Initialization**: Are `left` and `right` covering the entire possible search space? (e.g., `len(arr)` vs `len(arr)-1`)
    **初始化**：`left` 和 `right` 是否覆蓋了整個可能的搜索空間？
- [ ] **Loop Condition**: Did I use `<` or `<=`? Does it match my update logic?
    **迴圈條件**：我用了 `<` 還是 `<=`？這與我的更新邏輯匹配嗎？
- [ ] **Update Logic**:
    - If `right = mid`, loop must be `while left < right`.
    - If `right = mid - 1`, loop is usually `while left <= right`.
    **更新邏輯**：
    - 若 `right = mid`，迴圈必須是 `while left < right`。
    - 若 `right = mid - 1`，迴圈通常是 `while left <= right`。
- [ ] **Return Value**: Should I return `left`, `left - 1`, or check `nums[left] == target`?
    **回傳值**：我該回傳 `left`、`left - 1`，還是檢查 `nums[left] == target`？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Dictionary Game（字典遊戲）
Imagine finding a word in a physical dictionary. You open the middle.
想像在實體字典中找一個單字。你打開中間。
*   Word is "Apple", you opened to "Monkey".
    單字是 "Apple"，你翻到了 "Monkey"。
*   "Apple" < "Monkey", so you discard the entire right half (including "Monkey").
    "Apple" < "Monkey"，所以你捨棄整個右半部（包含 "Monkey"）。
*   **Visual**: Tearing the phone book in half repeatedly.
    **圖像**：不斷地將電話簿撕成兩半。

### The Boundary (T/F) Pattern（邊界 T/F 模式）
Visualize the search space as a series of booleans: `[F, F, F, F, T, T, T, T]`.
將搜索空間視覺化為一系列布林值：`[F, F, F, F, T, T, T, T]`。
*   We are looking for the **first T**.
    我們正在尋找 **第一個 T**。
*   If `mid` is `F`, we must go right (`left = mid + 1`).
    若 `mid` 是 `F`，我們必須往右走（`left = mid + 1`）。
*   If `mid` is `T`, we might be at the first one, or there are more to the left. We keep `mid` (`right = mid`).
    若 `mid` 是 `T`，我們可能就在第一個，或者左邊還有。我們保留 `mid`（`right = mid`）。