Here is the comprehensive guide for **Advanced Binary Search**, tailored for a Senior Software Engineer, formatted as requested.

---

# Advanced Binary Search (進階二分搜尋法)

## 1. Learning Goals（學習目標）

*   **Master Generalized Binary Search:** Move beyond finding elements in an array to searching within a solution space (Binary Search on Answer).
    **掌握廣義二分搜尋：** 超越在陣列中尋找元素，進階至在解空間中進行搜尋（對答案二分）。
*   **Define Monotonic Predicates:** Learn to abstract problems into a function $f(x)$ that returns `true`/`false`, identifying the boundary.
    **定義單調判斷函數：** 學習將問題抽象化為回傳 `true`/`false` 的函數 $f(x)$，並識別其邊界。
*   **Handle Complex Edge Cases:** Eliminate "off-by-one" errors and infinite loops by standardizing boundary handling templates.
    **處理複雜邊界情況：** 透過標準化邊界處理模板，消除「差一錯誤」與無窮迴圈。
*   **Optimize for Senior Interviews:** Demonstrate the ability to decouple the search logic from the feasibility logic (Strategy Pattern mindset).
    **針對資深面試優化：** 展示將「搜尋邏輯」與「可行性邏輯」解耦的能力（策略模式思維）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
Binary Search is not just an algorithm for sorted arrays; it is a technique to find a specific boundary in a monotonic search space.
二分搜尋法不僅是針對已排序陣列的演算法；它是一種在單調搜尋空間中尋找特定邊界的技術。

### Intuition（直覺）
If you can define a predicate function `check(x)` such that the results look like `[T, T, T, ..., F, F, F]`, Binary Search can find the transition point in $O(\log N)$.
如果你能定義一個判斷函數 `check(x)`，使得結果呈現 `[T, T, T, ..., F, F, F]` 的形式，二分搜尋就能在 $O(\log N)$ 時間內找到轉折點。

### Complexity（複雜度）
*   **Time:** $O(\log(\text{Range}) \times O(\text{check}))$. For arrays, `check` is $O(1)$, so total is $O(\log N)$. For answer search, `check` might be $O(N)$.
    **時間：** $O(\log(\text{範圍}) \times O(\text{check}))$. 對於陣列，`check` 是 $O(1)$，故總時間為 $O(\log N)$。對於答案搜尋，`check` 可能是 $O(N)$。
*   **Space:** $O(1)$ iterative.
    **空間：** $O(1)$ 迭代解法。

### When to Use (Advanced)（適用場景 - 進階）
*   "Minimize the Maximum" or "Maximize the Minimum" problems.
    「最小化最大值」或「最大化最小值」的問題。
*   Finding the K-th element in implicit sorted structures (e.g., multiplication table, matrix).
    在隱式排序結構（如乘法表、矩陣）中尋找第 K 個元素。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Standard Boundary Search (Lower/Upper Bound)
**模式 A：標準邊界搜尋**
Finding the first or last occurrence of a target or condition.
尋找目標或條件的第一次或最後一次出現位置。

### Pattern B: Binary Search on Answer (The "Feasibility Check")
**模式 B：對答案二分（可行性檢查）**
Instead of searching an index, we search for the value of the answer itself.
我們不搜尋索引，而是直接搜尋答案的數值。
*   **Key:** Define the range `[min_ans, max_ans]` and a `canAchieve(value)` function.
    **關鍵：** 定義範圍 `[min_ans, max_ans]` 以及一個 `canAchieve(value)` 函數。

### Pattern C: Search in Rotated/Modified Array
**模式 C：在旋轉或變形陣列中搜尋**
The array is sorted but shifted (e.g., `[4,5,6,7,0,1,2]`). Requires logic to determine which half is sorted.
陣列已排序但發生位移（例如 `[4,5,6,7,0,1,2]`）。需要邏輯來判斷哪一半是有序的。

---

## 4. Example Walkthrough（範例講解）

### Problem: Split Array Largest Sum (Hard)
**問題：分割陣列的最大值（困難）**
*(LeetCode 410 / Similar to "Allocate Books")*

**Problem Statement:**
Given an integer array `nums` and an integer `k`, split `nums` into `k` non-empty subarrays such that the largest sum among these subarrays is **minimized**.
給定一個整數陣列 `nums` 和一個整數 `k`，將 `nums` 分割成 `k` 個非空子陣列，使得這些子陣列中的最大總和被 **最小化**。

### Thought Process（思路）

1.  **Brute Force (DFS):**
    Try every possible cut point. This is exponential time complexity.
    **暴力解（DFS）：** 嘗試每一個可能的切割點。這是指數級的時間複雜度。

2.  **Optimization (Observation):**
    *   What is the range of possible answers?
        答案的可能範圍是什麼？
        *   Lower bound: `max(nums)` (if each element is a subarray).
            下界：`max(nums)`（如果每個元素自成一個子陣列）。
        *   Upper bound: `sum(nums)` (if the whole array is one subarray).
            上界：`sum(nums)`（如果整個陣列是一個子陣列）。
    *   Monotonicity: If we can split the array with a max sum of $X$, we can also do it with any sum $> X$.
        單調性：如果我們能以最大和 $X$ 分割陣列，我們也能以任何大於 $X$ 的總和完成分割。

3.  **Approach: Binary Search on Answer:**
    We guess a value `mid` as the "allowed max sum". We write a greedy function to check if it's possible to split `nums` into $\le k$ subarrays where no subarray sum exceeds `mid`.
    **方法：對答案二分：** 我們猜測一個值 `mid` 作為「允許的最大和」。我們寫一個貪婪函數來檢查是否能將 `nums` 分割成 $\le k$ 個子陣列，且沒有任何子陣列總和超過 `mid`。

### Java Reference Solution（Java 參考解）

```java
class Solution {
    /**
     * Main function to find the minimized largest sum.
     * 主函數：尋找最小化的最大總和。
     */
    public int splitArray(int[] nums, int k) {
        // 1. Define the search space boundaries.
        // 1. 定義搜尋空間的邊界。
        int maxVal = 0;
        int sumVal = 0;
        for (int num : nums) {
            maxVal = Math.max(maxVal, num);
            sumVal += num;
        }

        // The answer must be at least the largest element, and at most the total sum.
        // 答案至少是陣列中的最大元素，至多是總和。
        int left = maxVal;
        int right = sumVal;
        
        // Use a variable to store the best valid answer found so far.
        // 使用變數儲存目前找到的最佳合法答案。
        int result = right;

        // 2. Binary Search Template.
        // 2. 二分搜尋模板。
        while (left <= right) {
            int mid = left + (right - left) / 2;

            // 3. Feasibility Check.
            // 3. 可行性檢查。
            if (canSplit(nums, k, mid)) {
                // If feasible, try to find a smaller maximum sum (move left).
                // 如果可行，嘗試尋找更小的最大和（向左移動）。
                result = mid;
                right = mid - 1;
            } else {
                // If not feasible (subarrays needed > k), we need a larger capacity.
                // 如果不可行（需要的子陣列數 > k），我們需要更大的容量。
                left = mid + 1;
            }
        }
        return result;
    }

    /**
     * Predicate function: Can we split nums into <= k subarrays such that
     * no subarray sum exceeds 'capacity'?
     * 判斷函數：我們能否將 nums 分割成 <= k 個子陣列，使得沒有子陣列總和超過 'capacity'？
     */
    private boolean canSplit(int[] nums, int k, int capacity) {
        int subarrays = 1; // Start with 1 subarray / 從 1 個子陣列開始
        int currentSum = 0;

        for (int num : nums) {
            // Greedy approach: add to current subarray if it fits.
            // 貪婪法：如果放得下，就加入當前子陣列。
            if (currentSum + num <= capacity) {
                currentSum += num;
            } else {
                // If it doesn't fit, start a new subarray.
                // 如果放不下，開啟一個新的子陣列。
                subarrays++;
                currentSum = num;
                
                // Optimization: Fail early if we exceed k.
                // 優化：如果超過 k，提早回傳失敗。
                if (subarrays > k) {
                    return false;
                }
            }
        }
        return true;
    }
}
```

### Complexity Analysis（複雜度分析）
*   **Time:** $O(N \times \log(\text{Sum} - \text{Max}))$. The search space is the sum of numbers, and for each step, we iterate the array ($O(N)$).
    **時間：** $O(N \times \log(\text{總和} - \text{最大值}))$. 搜尋空間是數字總和，每一步我們遍歷陣列 ($O(N)$)。
*   **Space:** $O(1)$.
    **空間：** $O(1)$.

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Mid Calculation** | `mid = (left + right) / 2` can overflow in Java. <br> **Fix:** Always use `mid = left + (right - left) / 2`. <br> **修正：** 永遠使用 `mid = left + (right - left) / 2` 以避免溢位。 |
| **Loop Condition** | `while(left < right)` vs `while(left <= right)`. <br> Use `<=` when the answer could be `mid` and you move `right = mid - 1`. Use `<` when narrowing search space to a single element. <br> 當答案可能是 `mid` 且你移動 `right = mid - 1` 時用 `<=`。當將搜尋空間縮小至單一元素時用 `<`。 |
| **Dead Loop** | Setting `left = mid` when `mid` is calculated rounding down (integer division). <br> **Fix:** If `left = mid`, then `mid` must be `left + (right - left + 1) / 2` (ceiling). <br> **修正：** 若邏輯包含 `left = mid`，則 `mid` 計算需向上取整。 |
| **Unsorted Input** | Applying BS on an unsorted array without a monotonic property. <br> **Check:** Ensure the property (value or predicate) is monotonic. <br> **檢查：** 確保屬性（數值或判斷函數）具備單調性。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Identify the Pattern (辨識模式)
If the problem asks for "Minimum of Maximum" or involves searching in a range $1$ to $10^9$, explicitly state:
"This looks like a Binary Search on Answer problem because the solution space is monotonic."
如果問題要求「最大值的最小值」或涉及 $1$ 到 $10^9$ 的範圍，明確指出：「這看起來像是一個對答案二分的問題，因為解空間是單調的。」

### 2. Define the Predicate (定義判斷函數)
Before writing the BS loop, write the signature of your helper function on the whiteboard/editor:
在寫二分迴圈之前，先在白板/編輯器上寫下輔助函數的簽名：
`boolean isFeasible(int value)`
Explain what `true` and `false` mean in this context.
解釋在此情境下 `true` 和 `false` 代表什麼。

### 3. Handle Bounds Carefully (謹慎處理邊界)
Verbally verify your `left` and `right` initialization.
口頭驗證你的 `left` 和 `right` 初始化。
"The smallest possible answer is X, and the largest is Y. I will search within this closed interval."
「最小可能的答案是 X，最大是 Y。我將在這個閉區間內進行搜尋。」

### 4. Follow-up
Interviewer: "What if the input array contains floating point numbers?"
面試官：「如果輸入陣列包含浮點數怎麼辦？」
Answer: "We change the loop condition to a fixed precision delta (e.g., `while (right - left > 1e-6)`) or run the loop for a fixed number of iterations (e.g., 100 times) to guarantee precision."
回答：「我們將迴圈條件改為固定精度的差值（如 `while (right - left > 1e-6)`），或執行固定次數的迴圈（如 100 次）以保證精度。」

---

## 7. Practice Problems（練習題）

### 1. Warm-up (Easy/Medium): Search in Rotated Sorted Array
**暖身（易/中）：在旋轉排序陣列中搜尋**
*   **Context:** Array is sorted but rotated. Find target index.
    **情境：** 陣列已排序但被旋轉。尋找目標索引。
*   **Hint:** One half of the array (left or right) is always sorted. Check which side is sorted first.
    **提示：** 陣列的一半（左或右）永遠是有序的。先檢查哪一邊是有序的。
*   **LeetCode:** 33

### 2. Core (Medium): Koko Eating Bananas
**核心（中）：Koko 吃香蕉**
*   **Context:** Minimize eating speed `k` to finish piles within `h` hours.
    **情境：** 最小化吃香蕉速度 `k`，以便在 `h` 小時內吃完所有堆。
*   **Hint:** Classic "Binary Search on Answer". Range is `[1, max(piles)]`. Predicate calculates hours needed for a given speed.
    **提示：** 經典的「對答案二分」。範圍是 `[1, max(piles)]`。判斷函數計算給定速度所需的小時數。
*   **LeetCode:** 875

### 3. Advanced (Hard): Median of Two Sorted Arrays
**進階（難）：兩個排序陣列的中位數**
*   **Context:** Find the median of two sorted arrays of size m and n in $O(\log(m+n))$.
    **情境：** 在 $O(\log(m+n))$ 時間內找出兩個大小為 m 和 n 的排序陣列的中位數。
*   **Hint:** Perform binary search on the smaller array to find a partition point such that elements on the left side are smaller than elements on the right side.
    **提示：** 對較小的陣列進行二分搜尋，找到一個分割點，使得左側的元素皆小於右側的元素。
*   **LeetCode:** 4

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Overflow Protection:** Did I use `left + (right - left) / 2`?
    **溢位保護：** 我是否使用了 `left + (right - left) / 2`？
*   [ ] **Termination:** Will my loop terminate? (Check `left = mid + 1` vs `right = mid` logic).
    **終止條件：** 我的迴圈會結束嗎？（檢查 `left = mid + 1` 對比 `right = mid` 的邏輯）。
*   [ ] **Search Space:** Is the range `[left, right]` inclusive or exclusive? Does it cover all possible answers?
    **搜尋空間：** 範圍 `[left, right]` 是包含還是排除？是否涵蓋所有可能的答案？
*   [ ] **Monotonicity:** Is the predicate function strictly monotonic (TTTFFF or FFFTTT)?
    **單調性：** 判斷函數是否嚴格單調（TTTFFF 或 FFFTTT）？

---

## 9. Memory Anchors（記憶錨點）

### The "TTTFFF" Cliff (TTTFFF 懸崖)
Visualize the search space as a cliff. You are looking for the edge where the ground (True) turns into air (False).
將搜尋空間想像成懸崖。你正在尋找地面（True）變成空氣（False）的邊緣。

### The "Guess and Check" Strategy (猜測與驗證策略)
For advanced problems, imagine you have a magic oracle (the `check` function). If you guess a number, the oracle tells you "Too High" or "Possible". Binary search is just the most efficient way to query this oracle.
對於進階問題，想像你有一個神奇的預言機（`check` 函數）。如果你猜一個數字，預言機會告訴你「太高」或「可能」。二分搜尋只是查詢這個預言機最有效率的方法。