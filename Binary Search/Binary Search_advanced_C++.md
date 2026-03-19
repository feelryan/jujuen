Here is the comprehensive guide on **Binary Search (Advanced)**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **二分搜尋法（進階）** 完整指南。

---

# Binary Search: Advanced Masterclass
# 二分搜尋法：進階大師課

**Role:** Principal Software Engineer & Interviewer (FAANG+)
**Target Audience:** Senior Software Engineer (7-12 YOE)
**Topic:** Binary Search (Advanced)
**Language:** C++

---

## 1. Learning Goals (學習目標)

1.  **Move beyond array lookups to "Search on Solution Space".**
    超越單純的陣列查找，掌握「在解空間中搜尋」的技巧。
2.  **Master the "Minimize the Maximum" and "Maximize the Minimum" patterns.**
    精通「最小化最大值」與「最大化最小值」這類最佳化問題的模式。
3.  **Deeply understand the generalized `check(x)` predicate function design.**
    深入理解廣義的 `check(x)` 判斷函數設計。
4.  **Handle complex boundary conditions without memorizing templates blindly.**
    在不死背模板的情況下，處理複雜的邊界條件。

---

## 2. Core Concepts: The Senior Perspective (核心觀念速覽：資深視角)

### Definition (定義)
Binary Search is not just about finding an index in a sorted array; it is a technique to find a specific transition point in a monotonic function $f(x)$.
二分搜尋法不僅是在排序陣列中尋找索引；它是一種在單調函數 $f(x)$ 中尋找特定轉折點的技術。

### Intuition (直覺)
If you can define a search space $S$ (range of possible answers) and a boolean function `check(x)` that exhibits monotonicity (e.g., `false, false, ..., true, true`), you can binary search for the boundary.
如果你能定義一個搜尋空間 $S$（可能答案的範圍），以及一個具備單調性的布林函數 `check(x)`（例如 `false, false, ..., true, true`），你就可以透過二分搜尋找到該邊界。

### Complexity (複雜度)
-   **Time:** $O(\log(\text{Range}) \cdot T(\text{check}))$.
    **時間：** $O(\log(\text{範圍}) \cdot T(\text{check}))$。
    *Note: For Senior interviews, identifying the cost of `check(x)` is crucial.*
    *註：在資深面試中，識別 `check(x)` 的成本至關重要。*
-   **Space:** $O(1)$ usually.
    **空間：** 通常為 $O(1)$。

### When to Use (適用場景)
-   Input is sorted (obviously).
    輸入已排序（顯而易見）。
-   **Optimization problems asking for min/max where the answer lies in a bounded range.**
    **要求極大/極小的最佳化問題，且答案位於有限範圍內。**
-   $N$ is large ($10^5+$), but the solution space allows logarithmic reduction.
    $N$ 很大（$10^5+$），但解空間允許對數級縮減。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Standard Search (標準搜尋)
Finding an exact value or insertion point (Lower/Upper Bound).
尋找精確值或插入點（下界/上界）。

### B. Search on Solution Space (解空間搜尋) - **Focus Area**
Instead of searching indices, we search for the **answer value** directly.
我們不搜尋索引，而是直接搜尋**答案數值**。
-   *Keywords:* "Minimize the maximum...", "Maximize the minimum...", "Kth smallest pair distance".
-   *關鍵字：*「最小化最大值...」、「最大化最小值...」、「第 K 小的配對距離」。

### C. Median/K-th Element of Two Sorted Arrays (雙排序陣列的中位數/第 K 元素)
Requires partitioning two arrays simultaneously to maintain logarithmic complexity.
需要同時對兩個陣列進行分割，以維持對數級複雜度。

---

## 4. Example Walkthrough (範例講解)

### Problem: Split Array Largest Sum (LeetCode 410)
### 問題：分割陣列的最大值

**Problem Statement (問題重述):**
Given an integer array `nums` and an integer `k`, split `nums` into `k` non-empty subarrays such that the largest sum of any subarray is minimized.
給定一個整數陣列 `nums` 和一個整數 `k`，將 `nums` 分割成 `k` 個非空子陣列，使得所有子陣列中「總和最大」的那個值越小越好。

**Thinking Process (思路):**

1.  **Brute Force (暴力解):**
    Try every possible cut point using DFS. Complexity is exponential. Not acceptable.
    使用 DFS 嘗試所有可能的切割點。複雜度是指數級。不可接受。

2.  **Observation (觀察):**
    What is the range of the possible answer (the max sum)?
    可能答案（最大總和）的範圍是多少？
    -   **Lower Bound:** The maximum single element (we can't split an element).
        **下界：** 單個元素的最大值（我們不能分割元素）。
    -   **Upper Bound:** The sum of the entire array (case where $k=1$).
        **上界：** 整個陣列的總和（當 $k=1$ 的情況）。

3.  **Monotonicity (單調性):**
    If we set a capacity limit $X$, can we split the array into $\le k$ subarrays?
    如果我們設定容量上限為 $X$，我們能否將陣列分割成 $\le k$ 個子陣列？
    -   If yes, then any capacity $> X$ also works. (We can relax the constraint).
        如果是，那麼任何大於 $X$ 的容量也都可行。（我們可以放寬限制）。
    -   If no, then any capacity $< X$ definitely fails.
        如果否，那麼任何小於 $X$ 的容量肯定失敗。
    -   This allows Binary Search on the capacity $X$.
        這允許我們對容量 $X$ 進行二分搜尋。

4.  **Optimal Solution (最佳解):**
    Binary Search on the range `[max(nums), sum(nums)]`.
    在範圍 `[max(nums), sum(nums)]` 內進行二分搜尋。

**Time Complexity:** $O(N \cdot \log(\sum \text{nums}))$.
**時間複雜度：** $O(N \cdot \log(\sum \text{nums}))$。

**C++ Reference Solution (C++ 參考解):**

```cpp
#include <vector>
#include <numeric>
#include <algorithm>
#include <iostream>

class Solution {
public:
    // The predicate function: Can we split nums into <= k subarrays
    // such that no subarray sum exceeds 'max_sum_limit'?
    // 判斷函數：我們能否將 nums 分割成 <= k 個子陣列，
    // 使得沒有任何子陣列總和超過 'max_sum_limit'？
    bool canSplit(const std::vector<int>& nums, int k, long long max_sum_limit) {
        int subarrays = 1; // Start with 1 subarray / 從 1 個子陣列開始
        long long current_sum = 0;

        for (int num : nums) {
            // If adding this number exceeds the limit, we must cut here.
            // 如果加上這個數字超過限制，我們必須在此處切割。
            if (current_sum + num > max_sum_limit) {
                subarrays++;
                current_sum = num; // Start new subarray with current num / 用當前數字開始新的子陣列
                
                // Optimization: If we already exceed k, return false early.
                // 優化：如果已經超過 k，提早返回 false。
                if (subarrays > k) return false;
            } else {
                current_sum += num;
            }
        }
        return true;
    }

    int splitArray(std::vector<int>& nums, int k) {
        long long left = 0;
        long long right = 0;

        // Initialize boundaries
        // 初始化邊界
        for (int num : nums) {
            left = std::max(left, (long long)num); // Max element is the hard lower bound / 最大元素是硬下界
            right += num; // Sum is the hard upper bound / 總和是硬上界
        }

        long long ans = right;

        // Binary Search Template for "Minimizing" a value
        // 用於「最小化」數值的二分搜尋模板
        while (left <= right) {
            long long mid = left + (right - left) / 2;

            if (canSplit(nums, k, mid)) {
                ans = mid;      // This value is possible, try smaller / 這個值可行，嘗試更小的
                right = mid - 1;
            } else {
                left = mid + 1; // This value is too small, need larger / 這個值太小，需要更大的
            }
        }

        return (int)ans;
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall (陷阱) | Correction (修正) |
| :--- | :--- | :--- |
| **Loop Condition** | Using `left < right` vs `left <= right` inconsistently causes infinite loops. <br> 不一致地使用 `left < right` 與 `left <= right` 導致無窮迴圈。 | Stick to `left <= right` for most cases. If using `left < right`, ensure `right = mid` (not `mid-1`) to avoid excluding the answer. <br> 大多數情況堅持用 `left <= right`。若用 `left < right`，確保 `right = mid`（而非 `mid-1`）以免排除答案。 |
| **Mid Calculation** | `mid = (left + right) / 2` causes integer overflow. <br> `mid = (left + right) / 2` 導致整數溢位。 | Always use `mid = left + (right - left) / 2`. <br> 永遠使用 `mid = left + (right - left) / 2`。 |
| **Search Space** | Assuming search space is always indices `0` to `N-1`. <br> 假設搜尋空間總是索引 `0` 到 `N-1`。 | For advanced problems, the space is often the **range of values** (e.g., $1$ to $10^9$). <br> 對於進階問題，空間通常是**數值範圍**（例如 $1$ 到 $10^9$）。 |
| **Unsorted Input** | Applying BS on an unsorted array without a monotonic property. <br> 在沒有單調性質的未排序陣列上使用 BS。 | BS requires a monotonic predicate, not necessarily a sorted array (e.g., Rotated Array, Peak Element). <br> BS 需要單調的判斷函數，不一定是排序陣列（例如旋轉陣列、峰值元素）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Identify Range:** "The answer is bounded between `min_val` and `max_val`."
    **確認範圍：**「答案被限制在 `min_val` 和 `max_val` 之間。」
2.  **Propose Monotonicity:** "I observe that if a value $X$ is valid, then all values $>X$ are also valid. This suggests Binary Search."
    **提出單調性：**「我觀察到如果數值 $X$ 合法，則所有 $>X$ 的數值也合法。這暗示可以使用二分搜尋。」
3.  **Define Check Function:** "I will implement a helper function `check(mid)` that verifies if `mid` is a feasible solution in linear time."
    **定義檢查函數：**「我將實作一個輔助函數 `check(mid)`，以線性時間驗證 `mid` 是否為可行解。」

### Whiteboard Strategy (白板策略)
-   Write the `check` function first. It's often the logic core.
    先寫 `check` 函數。這通常是邏輯核心。
-   Use `long long` for `left`, `right`, and `mid` to show you are "Senior" enough to care about overflow without being asked.
    將 `left`, `right`, `mid` 設為 `long long`，顯示你夠「資深」，不用人提醒就會注意溢位問題。

### Common Follow-ups (常見追問)
-   *Q: What if the array contains duplicates?* (Usually affects standard search, less impact on "answer search").
    *問：如果陣列包含重複值怎麼辦？*（通常影響標準搜尋，對「答案搜尋」影響較小）。
-   *Q: Can we optimize the `check` function?* (e.g., using prefix sums or another binary search inside).
    *問：我們能優化 `check` 函數嗎？*（例如：使用前綴和或在內部使用另一個二分搜尋）。

---

## 7. Practice Problems (練習題)

### Easy / Warm-up
**Problem:** Search in Rotated Sorted Array (LeetCode 33)
**Hint:** Determine which half is sorted (left or right) and adjust boundaries accordingly.
**提示：** 判斷哪一半是有序的（左邊或右邊），並據此調整邊界。

### Intermediate (Target Level)
**Problem:** Koko Eating Bananas (LeetCode 875)
**Hint:** Similar to "Split Array". Search range is `[1, max(piles)]`. Predicate: `hours_needed(speed) <= h`.
**提示：** 類似「分割陣列」。搜尋範圍是 `[1, max(piles)]`。判斷式：`hours_needed(speed) <= h`。

### Advanced / Boss
**Problem:** Median of Two Sorted Arrays (LeetCode 4)
**Hint:** Binary search on the "cut positions" of the smaller array. Ensure elements on the left of cuts $\le$ elements on the right.
**提示：** 對較小陣列的「切割位置」進行二分搜尋。確保切割線左側元素 $\le$ 右側元素。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **Range Definition:** Is `right` inclusive (`N-1`) or exclusive (`N`)?
    **範圍定義：** `right` 是包含 (`N-1`) 還是不包含 (`N`)？
-   [ ] **Termination:** Does `while (left <= right)` cover the single element case?
    **終止條件：** `while (left <= right)` 是否涵蓋了單一元素的情況？
-   [ ] **Infinite Loop:** If `left = mid` is possible, did you use `mid = left + (right - left + 1) / 2` (ceiling division)?
    **無窮迴圈：** 如果 `left = mid` 是可能的，你是否使用了 `mid = left + (right - left + 1) / 2`（向上取整）？
-   [ ] **Overflow:** Are you adding `left + right`? (Don't).
    **溢位：** 你是否在做 `left + right`？（別這麼做）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Water Level" Analogy (水位類比)
For "Search on Answer" problems (like Split Array), imagine a landscape.
對於「答案搜尋」問題（如分割陣列），想像一片地形。
-   The answer is the **Water Level**.
    答案是**水位**。
-   If the water is too high (large max sum), all islands (subarrays) are connected/valid (easy to satisfy).
    如果水位太高（最大總和很大），所有島嶼（子陣列）都相連/有效（容易滿足）。
-   If the water is too low, islands fragment too much (too many subarrays).
    如果水位太低，島嶼會過度破碎（子陣列太多）。
-   We are finding the **lowest water level** that keeps the number of islands $\le k$.
    我們正在尋找能保持島嶼數量 $\le k$ 的**最低水位**。

### The "Guess Number" Game (猜數字遊戲)
Always revert to this simple game if you get confused about `high = mid - 1` vs `high = mid`.
如果你對 `high = mid - 1` 或 `high = mid` 感到困惑，永遠回到這個簡單的遊戲。
-   Is the number 50? "Too high".
    數字是 50 嗎？「太高了」。
-   Then 50 cannot be the answer. So `high` must be `49` (`mid - 1`).
    那麼 50 不可能是答案。所以 `high` 必須是 `49` (`mid - 1`)。
-   *Unless* the problem allows "approximate" matches (Lower Bound), then strict exclusion logic changes.
    *除非*問題允許「近似」匹配（下界），否則嚴格排除邏輯會改變。