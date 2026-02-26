# Binary Search (Advanced) | 二分搜尋法（進階篇）

## 1. Learning Objectives (學習目標)

*   **Master "Binary Search on Answer":** Move beyond searching in explicit arrays to searching within implicit solution spaces (value ranges).
    **掌握「對答案進行二分搜尋」：** 超越在顯式陣列中的搜尋，學會如何在隱式的解空間（數值範圍）中進行搜尋。
*   **Define Monotonicity Abstractly:** Identify monotonic properties in complex problems (e.g., resource allocation, minimization of maximums) where sorting isn't obvious.
    **抽象定義單調性：** 在排序不明顯的複雜問題（如資源分配、最小化最大值）中識別單調性質。
*   **Standardize Boundary Handling:** Adopt a consistent template to eliminate "off-by-one" errors and infinite loops during high-pressure interviews.
    **標準化邊界處理：** 採用一致的模板，以消除高壓面試中常見的「差一錯誤」與無窮迴圈。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Binary Search is an algorithm that finds a target value within a sorted sequence by repeatedly dividing the search interval in half.
二分搜尋法是一種在已排序序列中，藉由反覆將搜尋區間減半來尋找目標值的演算法。

For senior engineers, it is better defined as: **An optimization technique to find the boundary in a monotonic function $f(x)$ that maps to boolean values.**
對於資深工程師而言，更精確的定義是：**一種在映射為布林值的單調函數 $f(x)$ 中尋找邊界的最佳化技巧。**

### Intuition (直覺)
If you can determine that a value `x` is "too small" implies all values `< x` are also too small, you can discard half the space.
如果你能確定數值 `x` 「太小」意味著所有 `< x` 的數值也都太小，你就可以捨棄一半的空間。

### Complexity (複雜度)
*   **Time:** $O(\log (\text{Range}) \cdot F(\text{check}))$, where $F(\text{check})$ is the cost of the verification function.
    **時間：** $O(\log (\text{範圍}) \cdot F(\text{check}))$，其中 $F(\text{check})$ 是驗證函數的成本。
*   **Space:** $O(1)$ iterative.
    **空間：** $O(1)$ 迭代解法。

### Applicability (適用與不適用場景)
*   **Use when:** The search space is monotonic (sorted array, or a function where $f(x) = \text{true} \implies f(x+1) = \text{true}$).
    **適用於：** 搜尋空間具單調性（已排序陣列，或滿足 $f(x) = \text{true} \implies f(x+1) = \text{true}$ 的函數）。
*   **Don't use when:** The data is unsorted and cannot be sorted efficiently, or the dataset is extremely small (linear scan is faster due to branch prediction/caching).
    **不適用於：** 資料未排序且無法有效排序，或資料集極小（因分支預測與快取機制，線性掃描可能更快）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Generalized Binary Search (Binary Search on Answer)
**模式一：廣義二分搜尋（對答案二分）**
Instead of searching for an index, we search for the *value* of the answer.
我們不是搜尋索引，而是搜尋答案的 *數值*。
*   **Context:** "Minimize the maximum..." or "Maximize the minimum..."
    **情境：** 「最小化最大值...」或「最大化最小值...」
*   **Technique:** Define a `check(val)` function. If `check(val)` is true, try a tighter bound.
    **技巧：** 定義一個 `check(val)` 函數。如果 `check(val)` 為真，則嘗試更緊縮的邊界。

### Pattern 2: Lower Bound / Upper Bound
**模式二：下界 / 上界**
Finding the first or last occurrence of an element, or the insertion point.
尋找元素第一次或最後一次出現的位置，或是插入點。
*   **Key:** Crucial for handling duplicates.
    **關鍵：** 處理重複元素的關鍵。

### Pattern 3: Rotated Sorted Array
**模式三：旋轉排序陣列**
The array is split into two sorted subarrays.
陣列被分割成兩個已排序的子陣列。
*   **Technique:** Determine which half is sorted to decide how to move pointers.
    **技巧：** 判斷哪一半是有序的，以此決定如何移動指標。

---

## 4. Example Walkthrough (範例講解)

### Problem: Split Array Largest Sum (LC 410)
**問題：分割陣列的最大值**

#### Problem Statement (問題重述)
Given an integer array `nums` and an integer `k`, split `nums` into `k` non-empty subarrays such that the largest sum among these subarrays is minimized.
給定一個整數陣列 `nums` 和一個整數 `k`，將 `nums` 分割成 `k` 個非空子陣列，使得這些子陣列中「總和最大」的那個值最小化。

#### Approach (思路)

1.  **Brute Force (暴力法):**
    Try every possible way to insert `k-1` dividers. This is combinatorially explosive ($O(N^k)$).
    嘗試插入 `k-1` 個分隔線的所有可能方法。這是組合爆炸級別的複雜度 ($O(N^k)$)。

2.  **Optimization (優化 - Binary Search on Answer):**
    *   **Observation:** The answer (max subarray sum) must lie between `max(nums)` (smallest possible max sum) and `sum(nums)` (largest possible max sum).
    *   **觀察：** 答案（子陣列最大總和）必定介於 `max(nums)`（最小可能的「最大和」）與 `sum(nums)`（最大可能的「最大和」）之間。
    *   **Monotonicity:** If we can split the array with a max sum capacity of $X$, we can definitely do it with capacity $X+1$. This is monotonic.
    *   **單調性：** 如果我們能在最大總和容量為 $X$ 的限制下分割陣列，那麼在容量為 $X+1$ 時絕對也能做到。這具備單調性。

3.  **Algorithm (演算法):**
    *   Binary search the range `[max(nums), sum(nums)]`.
    *   `check(capacity)`: Can we split `nums` into $\le k$ subarrays where no subarray sum exceeds `capacity`?
    *   對 `[max(nums), sum(nums)]` 範圍進行二分搜尋。
    *   `check(capacity)`：我們能否將 `nums` 分割成 $\le k$ 個子陣列，且沒有任何子陣列總和超過 `capacity`？

#### Complexity (複雜度)
*   **Time:** $O(N \cdot \log(\sum \text{nums}))$. The `check` function takes $O(N)$, binary search takes $O(\log(\text{Range}))$.
    **時間：** $O(N \cdot \log(\sum \text{nums}))$。`check` 函數耗時 $O(N)$，二分搜尋耗時 $O(\log(\text{範圍}))$。
*   **Space:** $O(1)$.
    **空間：** $O(1)$。

#### TypeScript Solution (參考解)

```typescript
/**
 * Calculates the minimum largest sum of split subarrays.
 * 計算分割子陣列後的最小「最大總和」。
 *
 * @param nums The input array of non-negative integers.
 * @param k The number of subarrays.
 */
function splitArray(nums: number[], k: number): number {
    let left = 0;
    let right = 0;

    // Initialize boundaries
    // 初始化邊界
    for (const num of nums) {
        left = Math.max(left, num); // Lower bound: largest single element
                                    // 下界：最大的單一元素
        right += num;               // Upper bound: sum of all elements
                                    // 上界：所有元素的總和
    }

    // Helper function to verify if a given capacity is feasible
    // 輔助函數：驗證給定的容量是否可行
    const canSplit = (capacity: number): boolean => {
        let cuts = 1; // Start with 1 subarray
                      // 從 1 個子陣列開始
        let currentSum = 0;

        for (const num of nums) {
            // If adding this number exceeds capacity, we need a cut
            // 如果加入此數字會超過容量，我們需要切割
            if (currentSum + num > capacity) {
                cuts++;
                currentSum = num; // Start new subarray with current num
                                  // 用當前數字開始新的子陣列
            } else {
                currentSum += num;
            }
        }
        // If we used <= k subarrays, this capacity is sufficient
        // 如果我們使用的子陣列數量 <= k，則此容量是充足的
        return cuts <= k;
    };

    // Binary Search Template: Find the minimal value satisfying the condition
    // 二分搜尋模板：尋找滿足條件的最小值
    while (left < right) {
        // Prevent overflow, equivalent to Math.floor((left + right) / 2)
        // 防止溢位，等同於 Math.floor((left + right) / 2)
        const mid = left + Math.floor((right - left) / 2);

        if (canSplit(mid)) {
            // If feasible, try a smaller capacity (search left half)
            // answer could be mid, so we include it.
            // 如果可行，嘗試更小的容量（搜尋左半部）
            // 答案可能是 mid，所以我們包含它。
            right = mid;
        } else {
            // If not feasible, we need a larger capacity
            // 如果不可行，我們需要更大的容量
            left = mid + 1;
        }
    }

    return left;
}
```

#### Why this template? (為何使用此模板？)
We use `while (left < right)` with `right = mid` and `left = mid + 1`. This is designed to find the **leftmost** element (minimum value) that satisfies the condition.
我們使用 `while (left < right)` 搭配 `right = mid` 與 `left = mid + 1`。這是專為尋找滿足條件的 **最左側** 元素（最小值）而設計的。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall (陷阱) | Solution (解法) |
| :--- | :--- | :--- |
| **Mid Calculation** | `(left + right) / 2` can overflow in languages like C++/Java (less issue in JS/TS but good habit). | Use `left + Math.floor((right - left) / 2)`. <br> 使用 `left + Math.floor((right - left) / 2)`。 |
| **Infinite Loop** | `left = mid` combined with floor division causes infinite loop when `left` and `right` are adjacent. | If using `left = mid`, use ceil division or `while(left + 1 < right)`. Ideally, stick to the `[left, right)` template. <br> 若使用 `left = mid`，需用無條件進位或 `while(left + 1 < right)`。最好堅持使用 `[left, right)` 模板。 |
| **Search Space** | Forgetting that the search space can be the *answer range*, not just indices. | Always ask: "Is the answer bounded and monotonic?" <br> 永遠自問：「答案是否有範圍且具單調性？」 |
| **Return Value** | Returning `left` vs `left - 1` vs `mid`. | Trace the loop termination. In `while(left < right)`, `left` is the first valid element. <br> 追蹤迴圈終止條件。在 `while(left < right)` 中，`left` 是第一個合法元素。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify Monotonicity:** "Since the function is monotonic (adding capacity never hurts feasibility), I can use Binary Search."
    **識別單調性：** 「由於該函數具單調性（增加容量絕不會降低可行性），我可以使用二分搜尋法。」
2.  **Define Search Space:** "My search space is from `min_possible` to `max_possible`."
    **定義搜尋空間：** 「我的搜尋空間是從 `min_possible` 到 `max_possible`。」
3.  **Define Invariant:** "I will maintain the invariant that the answer lies within `[left, right]`."
    **定義不變性：** 「我將維持『答案位於 `[left, right]` 之間』的不變性。」

### Whiteboard Strategy (白板策略)
*   **Write the `check` function first:** This isolates the logic and shows you can decompose the problem.
    **先寫 `check` 函數：** 這能隔離邏輯，並展示你具備拆解問題的能力。
*   **Stick to ONE template:** Don't improvise. I recommend `while (left < right)` for minimization problems.
    **堅守單一模板：** 不要即興發揮。針對最小化問題，我推薦 `while (left < right)`。

### Common Follow-ups (常見追問)
*   "What if the array contains floats?" (Change loop to `while (right - left > epsilon)`).
    「如果陣列包含浮點數怎麼辦？」（將迴圈改為 `while (right - left > epsilon)`）。
*   "Can we optimize the `check` function?" (e.g., parallel processing or greedy approach).
    「我們能優化 `check` 函數嗎？」（例如：平行處理或貪婪演算法）。

---

## 7. Practice Problems (練習題)

### 1. Easy (Warm-up): Find First and Last Position of Element in Sorted Array (LC 34)
*   **Goal:** Implement `lower_bound` and `upper_bound`.
    **目標：** 實作 `lower_bound` 與 `upper_bound`。
*   **Hint:** Run binary search twice. First to find the start index, second to find the end index.
    **提示：** 執行兩次二分搜尋。第一次找起始索引，第二次找結束索引。

### 2. Medium: Koko Eating Bananas (LC 875)
*   **Goal:** Classic "Binary Search on Answer".
    **目標：** 經典的「對答案二分搜尋」。
*   **Hint:** Similar to the example above. Search space is `[1, max(piles)]`. Check if speed `k` allows finishing within `h` hours.
    **提示：** 與上述範例相似。搜尋空間為 `[1, max(piles)]`。檢查速度 `k` 是否能在 `h` 小時內吃完。

### 3. Hard (Advanced): Median of Two Sorted Arrays (LC 4)
*   **Goal:** Binary search on partition indices, not values.
    **目標：** 對分割索引進行二分搜尋，而非數值。
*   **Hint:** You want to partition both arrays such that elements on the left are $\le$ elements on the right. Search on the smaller array's index to minimize cost $O(\log(\min(M, N)))$.
    **提示：** 你需要分割兩個陣列，使得左側元素皆 $\le$ 右側元素。對較小陣列的索引進行搜尋以最小化成本 $O(\log(\min(M, N)))$。

---

## 8. Quick Checklist (快速檢核表)

*   [ ] **Monotonicity Check:** Is the problem monotonic? (T, T, T, **F**, F, F) or (F, F, **T**, T, T)?
    **單調性檢查：** 問題是否具單調性？
*   [ ] **Boundary Check:** Did I handle `left = 0` and `right = length` (or `length - 1`) correctly?
    **邊界檢查：** 我是否正確處理了 `left = 0` 和 `right = length`（或 `length - 1`）？
*   [ ] **Termination:** Will `left` and `right` eventually meet? (Avoid `left = mid` without `+1` in `while(left < right)`).
    **終止條件：** `left` 和 `right` 最終會相遇嗎？（避免在 `while(left < right)` 中使用 `left = mid` 而未 `+1`）。
*   [ ] **Overflow:** Did I use `left + (right - left) / 2`?
    **溢位檢查：** 我是否使用了 `left + (right - left) / 2`？

---

## 9. Memory Anchors (記憶錨點)

### The "True/False Boundary" Image (真/假邊界圖像)
Visualize Binary Search not as finding a number, but as finding the edge of a cliff where the ground turns from **Green (Possible)** to **Red (Impossible)**.
將二分搜尋想像成不是在找一個數字，而是在找懸崖的邊緣，地面從 **綠色（可行）** 變成了 **紅色（不可行）**。

*   **Minimization Problem:** Look for the **first Green** index.
    **最小化問題：** 尋找 **第一個綠色** 的索引。
*   **Maximization Problem:** Look for the **last Green** index.
    **最大化問題：** 尋找 **最後一個綠色** 的索引。

### The "1-2-3" Rule
1.  **Define Range** (Start, End).
    **定義範圍**（起點，終點）。
2.  **Define Check** (Function returning boolean).
    **定義檢查**（回傳布林值的函數）。
3.  **Move Bounds** (If Check is true, do we go left or right?).
    **移動邊界**（如果檢查為真，我們該往左還是往右？）。