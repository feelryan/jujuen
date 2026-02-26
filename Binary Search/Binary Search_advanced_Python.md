# Advanced Binary Search: From Array Indexing to Solution Space Reduction
# 進階二分搜尋：從陣列索引到解空間縮減

## 1. Learning Goals (學習目標)

*   **Master "Binary Search on Answer":** Move beyond searching in explicit arrays to searching within implicit solution spaces (e.g., minimizing the maximum value).
    *   **掌握「對答案進行二分搜尋」：** 超越在顯式陣列中的搜尋，轉向在隱式解空間中搜尋（例如：最小化最大值）。
*   **Generalized Binary Search Template:** Understand the generic pattern of finding the boundary in a monotonic boolean function $f(x)$ (FFFFTTTT).
    *   **通用二分搜尋模板：** 理解在單調布林函數 $f(x)$ 中尋找邊界的通用模式（FFFFTTTT）。
*   **Handling Complex Monotonicity:** Tackle problems where the sorted property is rotated (Rotated Arrays) or exists in multiple dimensions (2D Matrix).
    *   **處理複雜單調性：** 解決排序屬性被旋轉（旋轉陣列）或存在於多維度（2D 矩陣）的問題。
*   **Precision & Boundary Control:** Eliminate "off-by-one" errors by standardizing loop invariants.
    *   **精準度與邊界控制：** 透過標準化迴圈不變量來消除「差一錯誤」（off-by-one errors）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Binary Search is an algorithm that finds the position of a target value within a sorted array or finds the boundary in a monotonic search space by repeatedly dividing the search interval in half.
二分搜尋是一種演算法，透過重複將搜尋區間減半，在已排序陣列中尋找目標值的位置，或在單調搜尋空間中尋找邊界。

### Intuition (直覺)
If you are looking for a word in a dictionary, you don't turn pages one by one; you open the middle. If the word is alphabetically after, you discard the first half.
如果你在字典裡找一個單字，你不會一頁頁翻，而是翻開中間。如果單字的字母順序在後，你就捨棄前半部。

### Complexity (複雜度)
*   **Time:** $O(\log N)$ — The search space reduces exponentially ($N \to N/2 \to N/4 \dots$).
    *   **時間：** $O(\log N)$ — 搜尋空間呈指數級縮減。
*   **Space:** $O(1)$ iterative; $O(\log N)$ recursive (due to stack).
    *   **空間：** 迭代法為 $O(1)$；遞迴法為 $O(\log N)$（因堆疊空間）。

### When to Use (適用場景)
*   **Sorted Data:** Arrays, Matrices (row/col sorted).
    *   **已排序資料：** 陣列、矩陣（行/列已排序）。
*   **Implicit Monotonicity:** Optimization problems asking for "Minimum value that satisfies condition X" (Binary Search on Answer).
    *   **隱式單調性：** 詢問「滿足條件 X 的最小值」的最佳化問題（對答案二分）。
*   **Finding Boundaries:** First occurrence, Last occurrence, Insertion point.
    *   **尋找邊界：** 第一次出現、最後一次出現、插入點。

### When NOT to Use (不適用場景)
*   **Unsorted/Random Data:** Unless sorting ($O(N \log N)$) is acceptable beforehand.
    *   **未排序/隨機資料：** 除非預先排序（$O(N \log N)$）是可以接受的。
*   **Small Datasets:** Linear search might be faster due to CPU cache locality and branch prediction overhead.
    *   **極小資料集：** 由於 CPU 快取局部性和分支預測的開銷，線性搜尋可能更快。
*   **Linked Lists:** Random access is $O(N)$, degrading Binary Search to $O(N)$.
    *   **連結串列：** 隨機存取為 $O(N)$，會將二分搜尋退化為 $O(N)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Standard & Boundary (標準與邊界)
Finding a specific value or the `lower_bound` / `upper_bound` (Python's `bisect_left` / `bisect_right`).
尋找特定值或 `lower_bound` / `upper_bound`（Python 的 `bisect_left` / `bisect_right`）。

### B. Search on Solution Space (解空間搜尋) — *High Frequency for Seniors*
Instead of searching an index, we search for the **answer value** (e.g., capacity, time, speed).
我們不搜尋索引，而是搜尋**答案數值**（如：容量、時間、速度）。
*   **Range:** $[MinPossible, MaxPossible]$
*   **Check Function:** `can_complete(value) -> bool`
*   **Pattern:** Minimize $k$ such that `condition(k)` is True.

### C. Rotated Sorted Array (旋轉排序陣列)
The array is split into two sorted subarrays. Key logic involves determining which half is sorted to decide the move.
陣列被分割成兩個已排序的子陣列。關鍵邏輯在於判斷哪一半是有序的，以決定移動方向。

### D. Median/K-th Element in Two Sorted Arrays
More complex partitioning logic requiring $O(\log(\min(N, M)))$.
更複雜的分割邏輯，需要 $O(\log(\min(N, M)))$ 的時間複雜度。

---

## 4. Example Walkthrough (範例講解)

### Problem: Split Array Largest Sum (LeetCode 410)
**Level:** Hard (Advanced)

#### Problem Statement (問題重述)
Given an integer array `nums` and an integer `k`, split `nums` into `k` non-empty subarrays such that the largest sum among these subarrays is **minimized**.
給定一個整數陣列 `nums` 和一個整數 `k`，將 `nums` 分割成 `k` 個非空子陣列，使得這些子陣列中「總和最大」的那個值被**最小化**。

#### Thought Process (思路)

1.  **Brute Force (DFS):** Try every possible cut point. Complexity is exponential. Not feasible.
    *   **暴力法 (DFS)：** 嘗試所有可能的切割點。複雜度是指數級。不可行。
2.  **Observation (Optimization):**
    *   If we define a "max sum cap" as $X$, can we split the array into $\le k$ subarrays?
    *   如果我們定義「最大總和上限」為 $X$，我們能否將陣列分割成 $\le k$ 個子陣列？
    *   This `check(X)` function is **monotonic**:
        *   If a capacity $X$ works, any capacity $> X$ also works.
        *   If $X$ is too small, any capacity $< X$ also fails.
    *   這個 `check(X)` 函數是**單調的**：
        *   如果容量 $X$ 可行，任何 $> X$ 的容量也可行。
        *   如果 $X$ 太小，任何 $< X$ 的容量也會失敗。
3.  **Optimal Approach (Binary Search on Answer):**
    *   **Search Space:**
        *   Lower bound (`left`): `max(nums)` (The largest single element must fit in a subarray).
        *   Upper bound (`right`): `sum(nums)` (The case where $k=1$).
    *   **Predicate:** Greedy approach to count subarrays needed for a given max sum.
    *   **最佳解 (對答案二分)：**
        *   **搜尋空間：**
            *   下界 (`left`)：`max(nums)`（最大的單一元素必須能放入子陣列）。
            *   上界 (`right`)：`sum(nums)`（$k=1$ 的情況）。
        *   **判斷函數：** 貪婪法計算給定最大總和下所需的子陣列數量。

#### Python Solution (Python 參考解)

```python
from typing import List

class Solution:
    def splitArray(self, nums: List[int], k: int) -> int:
        # Define the check function: Can we split nums into <= k subarrays
        # such that no subarray sum exceeds 'max_sum_allowed'?
        # 定義檢查函數：我們能否將 nums 分割成 <= k 個子陣列，
        # 且沒有任何子陣列總和超過 'max_sum_allowed'？
        def can_split(max_sum_allowed: int) -> bool:
            subarrays = 1
            current_sum = 0
            
            for num in nums:
                # If adding this number exceeds the limit, start a new subarray
                # 如果加上此數字會超過限制，則開始一個新的子陣列
                if current_sum + num > max_sum_allowed:
                    subarrays += 1
                    current_sum = num
                else:
                    current_sum += num
            
            # If we need more than k subarrays, this max_sum_allowed is too small
            # 如果我們需要超過 k 個子陣列，表示這個 max_sum_allowed 太小了
            return subarrays <= k

        # Binary Search Range
        # 二分搜尋範圍
        left = max(nums)  # Minimum possible answer (cannot be smaller than largest element)
                          # 最小可能答案（不能小於最大元素）
        right = sum(nums) # Maximum possible answer (entire array as one subarray)
                          # 最大可能答案（整數陣列作為一個子陣列）
        
        # Standard Binary Search Template for "Minimizing a Value"
        # 用於「最小化數值」的標準二分搜尋模板
        while left < right:
            mid = left + (right - left) // 2
            
            if can_split(mid):
                # If mid works, try to find a smaller valid value (search left half)
                # 如果 mid 可行，嘗試尋找更小的有效值（搜尋左半部）
                right = mid
            else:
                # If mid doesn't work, we need a larger capacity (search right half)
                # 如果 mid 不可行，我們需要更大的容量（搜尋右半部）
                left = mid + 1
                
        return left
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N \cdot \log(S))$, where $N$ is array length and $S$ is the sum of array (search space size).
    *   **時間：** $O(N \cdot \log(S))$，其中 $N$ 是陣列長度，$S$ 是陣列總和（搜尋空間大小）。
*   **Space:** $O(1)$
    *   **空間：** $O(1)$

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Contrast |
| :--- | :--- |
| **`left < right` vs `left <= right`** | Use `<` when the search space shrinks to a single element (answer is `left`). Use `<=` when you return inside the loop or search space can be empty.<br>當搜尋空間縮減至單一元素時使用 `<`（答案即 `left`）。當在迴圈內返回或搜尋空間可能為空時使用 `<=`。 |
| **`mid = (l+r)//2` vs `mid = l+(r-l)//2`** | In Python, integers have arbitrary precision, so overflow isn't an issue. In C++/Java, the second form prevents overflow.<br>在 Python 中，整數具有任意精度，因此溢位不是問題。在 C++/Java 中，第二種形式可防止溢位。 |
| **`right = mid` vs `right = mid - 1`** | If `mid` **could be** the answer (e.g., finding min valid value), use `right = mid`. If `mid` is definitely **not** the answer, use `right = mid - 1`.<br>如果 `mid` **可能是**答案（如尋找最小有效值），使用 `right = mid`。如果 `mid` 絕對**不是**答案，使用 `right = mid - 1`。 |
| **Monotonicity Violation** | Binary search fails if the function isn't monotonic (sorted). Ensure the "True/False" boundary is clean.<br>如果函數不是單調的（已排序），二分搜尋會失敗。確保「真/假」邊界是乾淨的。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the Monotonicity:** "This problem asks for the minimum $X$ such that condition $Y$ is met. This suggests the solution space is monotonic."
    *   **識別單調性：** 「這個問題要求滿足條件 $Y$ 的最小 $X$。這暗示了解空間是單調的。」
2.  **Define Search Space:** "The answer must lie between `max(nums)` and `sum(nums)`."
    *   **定義搜尋空間：** 「答案必定介於 `max(nums)` 和 `sum(nums)` 之間。」
3.  **Define Predicate:** "I will implement a helper function `check(val)` that returns true if..."
    *   **定義判斷函數：** 「我將實作一個輔助函數 `check(val)`，如果...則回傳 true。」

### Whiteboard Strategy (白板策略)
*   **Write the Template First:** Write the `while left < right` skeleton immediately. It buys you thinking time for the `check` logic.
    *   **先寫模板：** 立即寫下 `while left < right` 的骨架。這能為你爭取思考 `check` 邏輯的時間。
*   **Modularize:** Keep the `check` function separate. It makes the code cleaner and easier to debug.
    *   **模組化：** 將 `check` 函數分開。這使程式碼更乾淨且更易於除錯。

### Common Follow-ups (常見追問)
*   **Q:** What if the array contains duplicates? (Usually affects rotated array problems).
    *   **問：** 如果陣列包含重複值怎麼辦？（通常影響旋轉陣列問題）。
*   **Q:** Can we do this with floating point numbers? (Change loop condition to `while right - left > epsilon`).
    *   **問：** 我們可以用浮點數做這個嗎？（將迴圈條件改為 `while right - left > epsilon`）。

---

## 7. Practice Problems (練習題)

### 1. Easy (Warm-up): Find First and Last Position of Element (LC 34)
*   **Goal:** Implement `lower_bound` and `upper_bound` manually.
    *   **目標：** 手動實作 `lower_bound` 和 `upper_bound`。
*   **Hint:** Run binary search twice. First for the left boundary, second for the right.
    *   **提示：** 執行兩次二分搜尋。第一次找左邊界，第二次找右邊界。

### 2. Medium (Standard): Search in Rotated Sorted Array (LC 33)
*   **Goal:** Handle split monotonicity.
    *   **目標：** 處理分割的單調性。
*   **Hint:** Determine which half is sorted (`nums[left] <= nums[mid]`). If target is in that range, search there; otherwise search the other half.
    *   **提示：** 判斷哪一半是有序的（`nums[left] <= nums[mid]`）。如果目標在該範圍內，則在該處搜尋；否則搜尋另一半。

### 3. Hard (Advanced): K-th Smallest Number in Multiplication Table (LC 668)
*   **Goal:** Binary Search on Answer Space (Implicit Matrix).
    *   **目標：** 對答案空間進行二分搜尋（隱式矩陣）。
*   **Hint:** We cannot generate the table ($M \times N$ is too big). Search range $[1, M \times N]$. `check(x)`: count how many numbers in the table are $\le x$.
    *   **提示：** 我們無法生成表格（$M \times N$ 太大）。搜尋範圍 $[1, M \times N]$。`check(x)`：計算表格中有多少數字 $\le x$。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Invariant:** Does my loop maintain the invariant that the answer is always within `[left, right]`?
    *   **不變量：** 我的迴圈是否維持「答案始終在 `[left, right]` 內」的不變量？
*   [ ] **Termination:** Will `left` and `right` eventually meet? (Check `mid` calculation vs `left/right` update).
    *   **終止：** `left` 和 `right` 最終會相遇嗎？（檢查 `mid` 計算與 `left/right` 更新）。
*   [ ] **Infinite Loop:** If `left = mid`, does `mid` bias towards the right (`(l+r+1)//2`)? If `right = mid`, does `mid` bias towards left (`(l+r)//2`)?
    *   **無限迴圈：** 如果 `left = mid`，`mid` 是否偏向右側（`(l+r+1)//2`）？如果 `right = mid`，`mid` 是否偏向左側（`(l+r)//2`）？
*   [ ] **Return Value:** Should I return `left`, `left - 1`, or check `nums[left] == target`?
    *   **回傳值：** 我應該回傳 `left`、`left - 1`，還是檢查 `nums[left] == target`？

---

## 9. Mental Models & Analogies (記憶錨點與類比)

### The "True/False Boundary" (真假邊界)
Visualize the search space as a series of boolean values derived from your `check` function:
將搜尋空間想像成由 `check` 函數導出的一系列布林值：
`[F, F, F, F, T, T, T, T]`
Your goal is to find the **first T** (Minimize valid) or the **last F** (Maximize invalid).
你的目標是找到**第一個 T**（最小化有效值）或**最後一個 F**（最大化無效值）。

### The "Guessing Game" (猜數字遊戲)
Binary Search on Answer is simply playing "High-Low" with the universe.
*   "Is 50 capacity enough?" -> "No, too small." -> `left = 51`
*   "Is 75 capacity enough?" -> "Yes." -> "Can we do better?" -> `right = 75`
對答案二分搜尋就像是跟宇宙玩「猜大小」遊戲。
*   「容量 50 夠嗎？」 -> 「不，太小。」 -> `left = 51`
*   「容量 75 夠嗎？」 -> 「夠。」 -> 「我們能做得更好嗎？」 -> `right = 75`