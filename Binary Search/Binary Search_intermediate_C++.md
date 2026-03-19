Here is a comprehensive guide on **Binary Search**, tailored for a Senior Software Engineer, designed to bridge the gap between theoretical knowledge and interview performance.
這是一份針對資深軟體工程師量身打造的 **二分搜尋法（Binary Search）** 完整指南，旨在填補理論知識與面試表現之間的落差。

---

# Binary Search: From Mechanics to Mastery
# 二分搜尋法：從機制到精通

## 1. Learning Objectives (學習目標)

1.  **Master the Generalized Binary Search Template**: Move beyond searching for a value in an array to searching for a boundary in a solution space.
    **掌握廣義二分搜尋模板**：從「在陣列中搜尋數值」進階到「在解空間中搜尋邊界」。
2.  **Internalize Loop Invariants**: Understand how to define `left` and `right` precisely to avoid infinite loops and off-by-one errors.
    **內化迴圈不變性**：理解如何精確定義 `left` 和 `right`，以避免無窮迴圈與差一錯誤（Off-by-one errors）。
3.  **Identify "Search on Answer" Patterns**: Recognize optimization problems that can be reduced to a binary search on the result range.
    **識別「對答案二分」模式**：辨識出可簡化為「在結果範圍內進行二分搜尋」的最佳化問題。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Binary Search is an efficient algorithm for finding an item from a sorted list of items by repeatedly dividing the search interval in half.
二分搜尋法是一種高效演算法，透過反覆將搜尋區間減半，從已排序的項目列表中找出目標項目。

### Intuition (直覺)
If the search space is monotonic (sorted), checking the middle element allows you to discard half of the remaining possibilities instantly.
如果搜尋空間是單調的（已排序），檢查中間元素能讓你瞬間排除剩餘可能性的一半。

### Complexity (複雜度)
-   **Time Complexity**: $O(\log N)$ — The search space reduces exponentially.
    **時間複雜度**：$O(\log N)$ — 搜尋空間呈指數級縮減。
-   **Space Complexity**: $O(1)$ iterative; $O(\log N)$ recursive (stack space).
    **空間複雜度**：迭代法為 $O(1)$；遞迴法為 $O(\log N)$（堆疊空間）。

### When to Use (適用場景)
-   Finding an element in a sorted array.
    在已排序陣列中尋找元素。
-   Finding the first/last occurrence of a value.
    尋找某個值的第一次或最後一次出現位置。
-   **Search on Answer**: When the output is monotonic (e.g., "Is it possible to complete task in $K$ days?").
    **對答案二分**：當輸出具有單調性時（例如：「是否能在 $K$ 天內完成任務？」）。

### When NOT to Use (不適用場景)
-   Unsorted data (unless sorting is cheap enough).
    未排序的資料（除非排序成本夠低）。
-   Linked Lists (random access is $O(N)$, defeating the purpose).
    鏈結串列（隨機存取為 $O(N)$，會抵消二分法的優勢）。
-   Very small datasets (linear scan might be faster due to CPU cache locality).
    極小的資料集（由於 CPU 快取局部性，線性掃描可能更快）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Standard Exact Match (標準精確匹配)
Searching for a specific target index. Returns -1 if not found.
搜尋特定的目標索引。若未找到則回傳 -1。
*   *Key*: `while (left <= right)`

### Pattern B: Lower/Upper Bound (尋找邊界)
Finding the first index where a condition is true (e.g., `arr[i] >= target`).
尋找滿足條件的第一個索引（例如 `arr[i] >= target`）。
*   *Key*: `while (left < right)`, shrink search space to a single point.
*   *關鍵*：`while (left < right)`，將搜尋空間收斂至單一點。

### Pattern C: Search on Solution Space (解空間搜尋)
Instead of an index, we search for a value (e.g., minimum capacity, maximum speed) where a condition `check(val)` switches from False to True.
我們不是搜尋索引，而是搜尋一個數值（如最小容量、最大速度），使得條件 `check(val)` 從 False 變為 True。
*   *Key*: Define range `[min_ans, max_ans]`, define monotonic `check()` function.
*   *關鍵*：定義範圍 `[min_ans, max_ans]`，定義單調的 `check()` 函數。

---

## 4. Example Walkthrough (範例講解)

### Problem: Koko Eating Bananas (LeetCode 875)
**Problem Statement**:
Koko loves to eat bananas. There are `n` piles of bananas, the `i-th` pile has `piles[i]` bananas. The guards have gone and will come back in `h` hours. Koko can decide her bananas-per-hour eating speed of `k`. Return the minimum integer `k` such that she can eat all the bananas within `h` hours.
**問題重述**：
Koko 愛吃香蕉。有 `n` 堆香蕉，第 `i` 堆有 `piles[i]` 根。警衛離開了，將在 `h` 小時後回來。Koko 可以決定她每小時吃香蕉的速度 `k`。請回傳最小的整數 `k`，讓她能在 `h` 小時內吃完所有香蕉。

### Approach (思路)

1.  **Brute Force (暴力法)**:
    Try speed $k=1, 2, 3, \dots$ until she can finish.
    嘗試速度 $k=1, 2, 3, \dots$ 直到她能吃完為止。
    *   *Complexity*: $O(M \cdot N)$, where $M$ is the max pile size. Too slow.
    *   *複雜度*：$O(M \cdot N)$，其中 $M$ 是最大堆的大小。太慢了。

2.  **Optimization (優化 - Binary Search)**:
    Observe that if Koko can finish with speed $k$, she can definitely finish with speed $k+1$. The function `canFinish(k)` is monotonic (False, False, ..., True, True).
    觀察到如果 Koko 能以速度 $k$ 吃完，她絕對也能以速度 $k+1$ 吃完。函數 `canFinish(k)` 是單調的（False, False, ..., True, True）。
    We want the **first** $k$ that returns True.
    我們想要找出回傳 True 的 **第一個** $k$。

3.  **Search Space (搜尋空間)**:
    *   Lower bound: 1 (minimum speed).
    *   Upper bound: Max element in `piles` (eating faster than the largest pile per hour doesn't help reduce hours for that pile further than 1 hour).
    *   下界：1（最小速度）。
    *   上界：`piles` 中的最大值（每小時吃得比最大堆還多，對於該堆的時間消耗無法低於 1 小時，故無幫助）。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>

class Solution {
public:
    // Helper function to check if Koko can finish with speed k
    // 輔助函數：檢查 Koko 是否能以速度 k 吃完
    bool canFinish(const std::vector<int>& piles, int h, int k) {
        long long hoursUsed = 0; // Use long long to prevent overflow during accumulation
                                 // 使用 long long 防止累加時溢位
        for (int p : piles) {
            // Calculate hours needed for this pile: ceil(p / k)
            // 計算此堆所需時間：ceil(p / k)
            // Equivalent to (p + k - 1) / k using integer arithmetic
            // 等同於整數運算的 (p + k - 1) / k
            hoursUsed += (p + k - 1) / k;
        }
        return hoursUsed <= h;
    }

    int minEatingSpeed(std::vector<int>& piles, int h) {
        // 1. Define the search space
        // 1. 定義搜尋空間
        int left = 1;
        int right = *std::max_element(piles.begin(), piles.end());
        
        // 2. Binary Search for the minimal k
        // 2. 二分搜尋最小的 k
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (canFinish(piles, h, mid)) {
                // If we can finish, try a smaller speed, but mid could be the answer
                // 如果能吃完，嘗試更小的速度，但 mid 可能是答案
                right = mid;
            } else {
                // If we cannot finish, we need a higher speed. mid is invalid.
                // 如果吃不完，我們需要更快的速度。mid 無效。
                left = mid + 1;
            }
        }
        
        // When left == right, we found the smallest valid k
        // 當 left == right 時，我們找到了最小的有效 k
        return left;
    }
};
```

### Complexity Analysis (複雜度分析)
-   **Time**: $O(N \log M)$, where $N$ is the number of piles and $M$ is the maximum pile size.
    **時間**：$O(N \log M)$，其中 $N$ 是堆數， $M$ 是最大堆的大小。
-   **Space**: $O(1)$.
    **空間**：$O(1)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall (陷阱) | Solution (解法) |
| :--- | :--- | :--- |
| **Mid Calculation** | `(left + right) / 2` causes integer overflow. <br> `(left + right) / 2` 導致整數溢位。 | Use `left + (right - left) / 2`. <br> 使用 `left + (right - left) / 2`。 |
| **Infinite Loop** | `left = mid` when `mid` is calculated biased to the left. <br> 當 `mid` 偏左計算時，`left = mid` 導致死循環。 | If `left = mid`, use `mid = left + (right - left + 1) / 2` (ceiling). Or stick to `right = mid` and `left = mid + 1`. <br> 若需 `left = mid`，`mid` 應向上取整。或堅持使用 `right = mid` 與 `left = mid + 1`。 |
| **Loop Condition** | Confusing `while(l < r)` vs `while(l <= r)`. <br> 混淆 `while(l < r)` 與 `while(l <= r)`。 | Use `l <= r` for finding exact value. Use `l < r` for finding boundaries (minimization). <br> 找精確值用 `l <= r`。找邊界（極值）用 `l < r`。 |
| **Boundary Update** | Setting `right = mid - 1` vs `right = mid`. <br> 設定 `right = mid - 1` 對比 `right = mid`。 | If `mid` *could* be the answer, keep it (`right = mid`). If `mid` is definitely invalid, discard it (`right = mid - 1`). <br> 若 `mid` *可能*是答案，保留它（`right = mid`）。若 `mid` 絕對無效，捨棄它（`right = mid - 1`）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **State the Monotonicity**: "Since the problem implies that if $X$ works, any value $>X$ also works, this suggests a monotonic property suitable for Binary Search."
    **陳述單調性**：「由於題目暗示如果 $X$ 可行，任何 $>X$ 的值也可行，這顯示出適合二分搜尋的單調性質。」
2.  **Define the Search Space**: "I will search on the range of possible answers, from [Min, Max]."
    **定義搜尋空間**：「我將在可能的答案範圍 [Min, Max] 內進行搜尋。」
3.  **Define the `check` function**: "I will implement a helper function to verify if a specific value satisfies the condition."
    **定義 `check` 函數**：「我會實作一個輔助函數來驗證特定數值是否滿足條件。」

### Whiteboard Strategy (白板策略)
-   **Trace with Variables**: Write `L`, `R`, `Mid` columns on the side.
    **變數追蹤**：在旁邊寫下 `L`、`R`、`Mid` 的欄位。
-   **Corner Cases**: Explicitly mention "What if the array has 1 element?" or "What if the answer doesn't exist?"
    **邊界情況**：明確提到「如果陣列只有一個元素？」或「如果答案不存在？」。

### Common Follow-ups (常見追問)
-   **Q**: What if the array is too large for memory?
    **問**：如果陣列大到記憶體裝不下怎麼辦？
    **A**: We can't access by index directly. However, if we are searching on the *answer* (integers), memory isn't an issue. If searching a distributed file, we need an API to fetch the $i$-th element efficiently.
    **答**：我們無法直接透過索引存取。但如果是對*答案*（整數）進行搜尋，記憶體不是問題。如果是搜尋分散式檔案，我們需要一個能高效抓取第 $i$ 個元素的 API。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Standard)
**Problem**: Binary Search (LeetCode 704)
**Hint**: Focus on the basic `while(l <= r)` loop and returning -1.
**提示**：專注於基礎的 `while(l <= r)` 迴圈並回傳 -1。
**Concept**: Basic Template.

### Level 2: Intermediate (Rotated)
**Problem**: Search in Rotated Sorted Array (LeetCode 33)
**Hint**: One half of the array is always sorted. Determine which half is sorted first, then decide if the target lies within that half.
**提示**：陣列的一半總是已排序的。先判斷哪一半是有序的，再決定目標是否在該範圍內。
**Concept**: Conditional Logic + Binary Search.

### Level 3: Advanced (Search on Answer)
**Problem**: Split Array Largest Sum (LeetCode 410)
**Hint**: We want to minimize the largest sum. The range of possible sums is `[max(nums), sum(nums)]`. Use a greedy approach in the `check` function to see if we can split array into $m$ subarrays with max sum $\le$ mid.
**提示**：我們想要最小化最大和。可能的和之範圍為 `[max(nums), sum(nums)]`。在 `check` 函數中使用貪婪法，確認是否能將陣列分割成 $m$ 個子陣列，且最大和 $\le$ mid。
**Concept**: Generalized Binary Search (Min-Max problem).

---

## 8. Quick Checklists (快速檢核表)

### Before Coding (編碼前)
- [ ] Is the data sorted or does the solution space have a monotonic property? (資料是否已排序，或解空間具有單調性？)
- [ ] What is the exact range `[left, right]`? (確切範圍為何？)
- [ ] Should `right` be `n` or `n-1`? (Right 該是 `n` 還是 `n-1`？)

### During Coding (編碼中)
- [ ] Did I handle overflow? `l + (r - l) / 2`. (有無處理溢位？)
- [ ] Is my `while` condition consistent with my update logic? (While 條件與更新邏輯是否一致？)
    - `while(l <= r)` $\to$ `r = mid - 1`, `l = mid + 1`
    - `while(l < r)` $\to$ `r = mid`, `l = mid + 1` (usually)

### Debugging (除錯)
- [ ] Infinite loop? Check if `left` and `right` are stuck on adjacent values. (無窮迴圈？檢查 `left` 和 `right` 是否卡在相鄰值。)
- [ ] Answer is one index off? Check initialization of `right`. (答案差一個索引？檢查 `right` 的初始化。)

---

## 9. Memory Anchors (記憶錨點)

### The "Guess Number" Game (猜數字遊戲)
Visualize Binary Search as the High-Low game.
將二分搜尋想像成「猜大小」遊戲。
-   "Too high" $\to$ discard top half (`right = mid - 1`).
    「太大了」 $\to$ 捨棄上半部。
-   "Too low" $\to$ discard bottom half (`left = mid + 1`).
    「太小了」 $\to$ 捨棄下半部。

### The "T/F Boundary" Image (T/F 邊界圖像)
For "Search on Answer", visualize the search space as a series of booleans:
對於「對答案二分」，將搜尋空間想像成一系列布林值：
`[F, F, F, F, T, T, T, T]`
We are looking for the **first T**.
我們在尋找 **第一個 T**。
-   If we hit `F` (left side), we must move right (`left = mid + 1`).
    如果撞到 `F`（左側），必須向右移。
-   If we hit `T` (right side), this *could* be the answer, but there might be an earlier `T`, so move left but keep index (`right = mid`).
    如果撞到 `T`（右側），這*可能*是答案，但前面可能有更早的 `T`，所以向左移但保留索引。