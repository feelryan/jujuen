
# 1-D Dynamic Programming: Advanced Mastery
# 一維動態規劃：進階精通

## 1. Learning Objectives（學習目標）

*   **Master State Definition beyond basic arrays:** Learn to define states that capture complex constraints (e.g., "skipping an element," "k-transactions").
    **掌握超越基礎陣列的狀態定義：** 學習定義能捕捉複雜限制條件的狀態（例如：「跳過一個元素」、「k 次交易」）。
*   **Optimize Space Complexity to O(1):** Move from standard `dp` arrays to rolling variables for memory efficiency, a key differentiator for senior roles.
    **優化空間複雜度至 O(1)：** 從標準的 `dp` 陣列進階到使用滾動變數以提升記憶體效率，這是資深職位的關鍵區別點。
*   **Differentiate Greedy vs. DP:** deeply understand when local optimality fails to guarantee global optimality.
    **區分貪婪演算法與動態規劃：** 深刻理解何時「局部最佳解」無法保證「全域最佳解」。
*   **Combine DP with other Data Structures:** Solve "Bar Raiser" problems by integrating DP with Deques (Monotonic Queue) or Binary Search.
    **結合 DP 與其他資料結構：** 透過整合 DP 與雙端佇列（單調佇列）或二分搜尋法，解決「提高標準（Bar Raiser）」級別的難題。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
1-D DP involves solving a problem by breaking it down into a linear sequence of overlapping subproblems.
一維動態規劃涉及將問題分解為一系列線性的重疊子問題來解決。

The intuition is "Decision Making on a Timeline": at index `i`, your optimal value depends only on the optimal values calculated at `i-1`, `i-2`, etc.
其直覺是「時間軸上的決策制定」：在索引 `i` 的最佳值僅取決於在 `i-1`、`i-2` 等處計算出的最佳值。

### Complexity（複雜度）
*   **Time:** Typically $O(N)$, where $N$ is the length of the input.
    **時間：** 通常為 $O(N)$，其中 $N$ 是輸入的長度。
*   **Space:** Naively $O(N)$, but often optimizable to $O(1)$ (constant space) or $O(K)$ (window size).
    **空間：** 樸素解法為 $O(N)$，但通常可優化至 $O(1)$（常數空間）或 $O(K)$（視窗大小）。

### When to Use (and Not)（適用與不適用場景）
*   **Use when:** You need to find a Maximum/Minimum, Count distinct ways, or check Existence (True/False), and the problem has optimal substructure.
    **適用於：** 你需要尋找最大值/最小值、計算不同路徑數、或檢查存在性（真/假），且問題具備最佳子結構時。
*   **Do NOT use when:** The problem requires listing *all* permutations/combinations (use Backtracking), or the data has no sequential dependency (e.g., disjoint sets).
    **不適用於：** 問題要求列出 *所有* 排列/組合（應使用回溯法），或資料沒有順序依賴性（例如不相交集合）。

---

## 3. Typical Patterns（典型題型 / 模式）

For Senior Engineers, we look beyond Fibonacci.
對於資深工程師，我們關注的不僅僅是費氏數列。

1.  **State Machine / Multi-State DP（狀態機 / 多狀態 DP）：**
    At each index `i`, you can be in one of several states (e.g., Stock problems: `hold`, `sold`, `rest`).
    在每個索引 `i`，你可能處於多種狀態之一（例如股票問題：`持有`、`賣出`、`休息`）。
2.  **Partitioning / Splitting（劃分 / 切割）：**
    Determine where to split a string or array to satisfy a condition (e.g., Word Break, Palindrome Partitioning II). This often involves a nested loop $O(N^2)$.
    決定在何處切割字串或陣列以滿足條件（例如斷字問題、迴文切割 II）。這通常涉及巢狀迴圈 $O(N^2)$。
3.  **Kadane’s Algorithm Variants（Kadane 演算法變體）：**
    Finding maximum subarrays with constraints (e.g., circular arrays, one deletion allowed).
    尋找帶有限制條件的最大子陣列（例如環狀陣列、允許刪除一次）。
4.  **DP + Binary Search (LIS)（DP + 二分搜尋）：**
    Reducing complexity from $O(N^2)$ to $O(N \log N)$ using patience sorting logic.
    利用耐性排序邏輯將複雜度從 $O(N^2)$ 降低至 $O(N \log N)$。

---

## 4. Example Walkthrough（範例講解）

### Problem: Maximum Subarray Sum with One Deletion (LeetCode 1186)
### 問題：允許刪除一次的最大子陣列和

**Problem Statement:**
Given an array of integers, return the maximum sum for a non-empty subarray (contiguous elements) with at most one element deletion.
給定一個整數陣列，回傳非空子陣列（連續元素）的最大和，該子陣列最多允許刪除一個元素。

**Why this fits "Advanced":** It requires managing two parallel states within a 1-D traversal.
**為何這屬於「進階」：** 它需要在一次一維遍歷中管理兩個並行的狀態。

### Approach & Evolution（思路與演進）

1.  **Brute Force:** Iterate all subarrays, for each subarray try deleting one element. $O(N^3)$.
    **暴力解：** 迭代所有子陣列，對每個子陣列嘗試刪除一個元素。$O(N^3)$。
2.  **Intermediate DP:** Standard Kadane's algorithm finds max subarray sum. We need to extend this.
    **中階 DP：** 標準 Kadane 演算法可找到最大子陣列和。我們需要對此進行擴充。
3.  **Advanced DP (State Machine):**
    At any index `i`, we have two choices/states:
    在任何索引 `i`，我們有兩個選擇/狀態：
    *   `ignored`: The max sum ending at `i` where one deletion **has already occurred**.
        `ignored`：在 `i` 結束的最大和，其中 **已經發生過** 一次刪除。
    *   `not_ignored`: The max sum ending at `i` where **no deletion** has occurred (Standard Kadane).
        `not_ignored`：在 `i` 結束的最大和，其中 **沒有發生** 刪除（標準 Kadane）。

    **Transition（轉移方程式）:**
    *   `not_ignored[i] = max(arr[i], not_ignored[i-1] + arr[i])`
    *   `ignored[i] = max(ignored[i-1] + arr[i], not_ignored[i-1])`
        *   *Option A:* Delete occurred previously (`ignored[i-1]`), add current `arr[i]`.
            *選項 A：* 刪除發生在之前（`ignored[i-1]`），加上當前 `arr[i]`。
        *   *Option B:* Delete current element `arr[i]`, so we take `not_ignored[i-1]`.
            *選項 B：* 刪除當前元素 `arr[i]`，所以我們取 `not_ignored[i-1]`。

### Python Solution (Optimized Space)
### Python 參考解（空間優化版）

```python
from typing import List

def maximumSum(arr: List[int]) -> int:
    """
    Calculates the maximum subarray sum allowing at most one deletion.
    計算最多允許刪除一個元素的最大子陣列和。
    
    Time Complexity: O(N) - Single pass.
    Space Complexity: O(1) - Using variables instead of arrays.
    """
    n = len(arr)
    if n == 0:
        return 0
    # Edge case: if all numbers are negative, return the max single element.
    # 邊界情況：如果所有數字都是負數，回傳最大的單一元素。
    if all(x < 0 for x in arr):
        return max(arr)

    # Initialize states
    # `no_del`: Max subarray sum ending here with 0 deletions.
    # `no_del`: 在此結束且刪除 0 次的最大子陣列和。
    # `one_del`: Max subarray sum ending here with 1 deletion.
    # `one_del`: 在此結束且刪除 1 次的最大子陣列和。
    
    no_del = arr[0]
    one_del = 0  # Technically impossible to delete at index 0 and have a non-empty subarray ending there conceptually for the first step logic, but handled in loop.
                 # 技術上在索引 0 刪除並讓非空子陣列在此結束是不可能的，但在迴圈邏輯中處理。
    
    # Initialize global max
    # 初始化全域最大值
    max_sum = arr[0]
    
    # Start from the second element
    # 從第二個元素開始
    for i in range(1, n):
        # Calculate new states based on previous values
        # 根據前一數值計算新狀態
        
        # Transition for one_del:
        # 1. We had a deletion before, so we MUST add current arr[i] (one_del + arr[i])
        # 2. We delete current arr[i], so we take the previous no_del sum (no_del)
        # 1. 之前已刪除過，所以必須加上當前 arr[i]
        # 2. 刪除當前 arr[i]，所以取之前的 no_del 和
        next_one_del = max(one_del + arr[i], no_del)
        
        # Transition for no_del (Standard Kadane):
        # Extend previous subarray or start new
        # 延伸之前的子陣列或重新開始
        next_no_del = max(no_del + arr[i], arr[i])
        
        # Update current states
        # 更新當前狀態
        one_del = next_one_del
        no_del = next_no_del
        
        # Update global maximum
        # 更新全域最大值
        max_sum = max(max_sum, no_del, one_del)
        
    return max_sum
```

### Common Mistakes (錯誤示範)
*   **Mistake:** Initializing `one_del` to 0 without considering negative numbers properly, or failing to handle the "all negative" case where the answer should be the max element (deletion requires non-empty result).
    **錯誤：** 將 `one_del` 初始化為 0 而未正確考慮負數，或未能處理「全負數」的情況，此時答案應為最大元素（刪除後仍需保留非空結果）。
*   **Mistake:** Forgetting that `one_del` depends on the *previous* `no_del`. If you update `no_del` before calculating `one_del` in the same loop iteration without a temporary variable, you use the wrong state.
    **錯誤：** 忘記 `one_del` 依賴於 *前一個* `no_del`。如果在同一迴圈迭代中，未經暫存變數就先更新 `no_del` 再計算 `one_del`，會使用了錯誤的狀態。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Subarray (子陣列)** | **Subsequence (子序列)** | Subarray must be **contiguous** (use Kadane/Sliding Window). Subsequence can be **non-contiguous** (use LIS/LCS patterns). <br> 子陣列必須 **連續**；子序列可以 **不連續**。 |
| **Greedy** | **Dynamic Programming** | Greedy makes the best local choice immediately. DP considers all paths (via subproblems) to find the global optimum. <br> 貪婪立即做出局部最佳選擇；DP 考慮所有路徑（透過子問題）以尋找全域最佳解。 |
| **O(N) Space** | **O(1) Space** | In interviews, solving with `dp[N]` is often just "Acceptable". Solving with variables (`prev`, `curr`) is "Strong Hire". <br> 面試中，用 `dp[N]` 解題通常只是「可接受」；用變數（`prev`, `curr`）解題才是「強力錄取」。 |

---

## 6. Interview Strategy（面試實戰建議）

### Framework (口條框架)
1.  **Define the State clearly:** "I will define `dp[i]` as the maximum value ending at index `i`..."
    **清晰定義狀態：** 「我將定義 `dp[i]` 為在索引 `i` 結束的最大值...」
2.  **Establish Recurrence:** "The value at `i` depends on `i-1` and `i-2`. The transition equation is..."
    **建立遞迴關係：** 「`i` 的值取決於 `i-1` 和 `i-2`。轉移方程式為...」
3.  **Discuss Base Cases:** "For index 0 and 1, the values are fixed as..."
    **討論基本情況：** 「對於索引 0 和 1，數值固定為...」
4.  **Code & Optimize:** Write the O(N) space version first if complex, then refactor to O(1) verbally or in code.
    **編碼與優化：** 如果很複雜，先寫 O(N) 空間版本，然後口頭或在代碼中重構為 O(1)。

### Whiteboard Strategy (白板策略)
*   **Draw the Table:** Even for 1-D DP, draw a row of boxes representing the array and write the DP values underneath for a sample input (e.g., `[1, -2, 0, 3]`).
    **畫出表格：** 即使是 1-D DP，也要畫出一排方格代表陣列，並在下方寫出範例輸入（如 `[1, -2, 0, 3]`）的 DP 數值。
*   **Trace the Indices:** Explicitly mark `i`, `i-1` pointers to show you understand the data flow.
    **追蹤索引：** 明確標記 `i`、`i-1` 指標，以顯示你理解資料流向。

### Common Follow-up (常見追問)
*   "Can you reconstruct the path/solution?" (Requires storing parent pointers or backtracking the DP table).
    「你能重建路徑/解法嗎？」（需要儲存父指標或回溯 DP 表）。
*   "What if the array is circular?" (Run DP twice: once `0` to `n-2`, once `1` to `n-1`).
    「如果是環狀陣列怎麼辦？」（執行兩次 DP：一次 `0` 到 `n-2`，一次 `1` 到 `n-1`）。

---

## 7. Practice Problems（練習題）

### Easy (Warm-up): House Robber II (LeetCode 213)
*   **Prompt:** Circular houses, cannot rob adjacent.
    **題目：** 環狀房屋，不能搶劫相鄰的。
*   **Hint:** Break the circle. Solve linear House Robber for `nums[0...n-2]` and `nums[1...n-1]`. Take max.
    **提示：** 打破圓環。對 `nums[0...n-2]` 和 `nums[1...n-1]` 分別解線性搶劫問題。取最大值。

### Medium (Core): Longest Increasing Subsequence (LeetCode 300)
*   **Prompt:** Find length of longest strictly increasing subsequence.
    **題目：** 尋找最長嚴格遞增子序列的長度。
*   **Hint:** Standard DP is $O(N^2)$. **Challenge yourself to implement the $O(N \log N)$ greedy + binary search solution.** This is a Senior expectation.
    **提示：** 標準 DP 為 $O(N^2)$。**挑戰自己實作 $O(N \log N)$ 的貪婪 + 二分搜尋解法。** 這是對資深工程師的期望。

### Hard (Bar Raiser): Constrained Subsequence Sum (LeetCode 1425)
*   **Prompt:** Max subsequence sum where difference between indices of selected elements $\le k$.
    **題目：** 最大子序列和，其中被選元素的索引差 $\le k$。
*   **Hint:** This is $DP[i] = nums[i] + \max(DP[i-k \dots i-1])$. To find the max in the window efficiently ($O(1)$), use a **Monotonic Queue (Deque)**.
    **提示：** 這是 $DP[i] = nums[i] + \max(DP[i-k \dots i-1])$。為了高效地（$O(1)$）在視窗中找到最大值，使用 **單調佇列（Deque）**。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Base Cases:** Did I handle `len(arr) == 0` or `len(arr) == 1`?
    **基本情況：** 我是否處理了 `len(arr) == 0` 或 `len(arr) == 1`？
*   [ ] **Initialization:** Are my DP variables initialized to `0`, `-inf`, or `arr[0]`? (Critical for max/min problems).
    **初始化：** 我的 DP 變數是否初始化為 `0`、`-inf` 或 `arr[0]`？（對最大/最小問題至關重要）。
*   [ ] **Loop Bounds:** `range(1, n)` or `range(n)`? Do I access `i-1` when `i=0`?
    **迴圈邊界：** `range(1, n)` 還是 `range(n)`？當 `i=0` 時我是否存取了 `i-1`？
*   [ ] **Return Value:** Do I return `dp[-1]` (last element) or `max(dp)` (best of all)?
    **回傳值：** 我是回傳 `dp[-1]`（最後一個元素）還是 `max(dp)`（所有中的最佳值）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The "Rolling Window" (滾動視窗):**
    Imagine looking at the array through a narrow slit. You only see the previous 1 or 2 values needed to make the next decision. You don't need to remember the entire history of the universe (entire DP array).
    想像透過一條狹縫看陣列。你只看到做下一個決策所需的、之前的 1 或 2 個數值。你不需要記住整個宇宙的歷史（整個 DP 陣列）。

*   **The "Domino Effect" (骨牌效應):**
    1-D DP is like pushing dominoes. The fall of domino `i` is entirely determined by the energy transferred from `i-1`. If you know the state of the previous domino, you know the state of the current one.
    一維 DP 就像推骨牌。骨牌 `i` 的倒下完全取決於從 `i-1` 傳遞過來的能量。如果你知道前一張骨牌的狀態，你就知道當前這張的狀態。