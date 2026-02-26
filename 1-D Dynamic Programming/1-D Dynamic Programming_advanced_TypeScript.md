# 1-D Dynamic Programming: Advanced Guide
# 一維動態規劃：進階指南

## 1. Learning Goals（學習目標）

*   **Master State Definition**: Learn to define $dp[i]$ precisely—whether it represents the result "ending at index $i$" or the "best result up to index $i$".
    **掌握狀態定義**：學會精確定義 $dp[i]$——它是代表「以索引 $i$ 結尾」的結果，還是「截至索引 $i$ 為止」的最佳結果。
*   **Optimize Space Complexity**: Move beyond standard tabulation to $O(1)$ space using rolling variables (state compression).
    **優化空間複雜度**：超越標準的列表法，使用滾動變數（狀態壓縮）將空間優化至 $O(1)$。
*   **Identify Subsequence vs. Subarray**: Distinguish between contiguous (subarray) and non-contiguous (subsequence) constraints, as they dictate the transition equation.
    **識別子序列與子陣列**：區分連續（子陣列）與非連續（子序列）的限制，因為它們決定了轉移方程式的寫法。
*   **Handle Circular & Edge Constraints**: Solve variations where the array is circular or contains specific blocking conditions.
    **處理環狀與邊界限制**：解決陣列是環狀或包含特定阻擋條件的變體問題。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
1-D DP is an optimization technique where the solution to a problem at index $i$ depends on the solutions at previous indices ($0$ to $i-1$).
一維動態規劃是一種優化技術，其中索引 $i$ 的問題解取決於先前索引（$0$ 到 $i-1$）的解。

It is essentially "smart recursion" with caching, or filling a table iteratively to avoid redundant calculations.
它本質上是帶有快取的「聰明遞迴」，或是透過迭代填表來避免重複計算。

### Complexity（複雜度）
*   **Time**: Typically $O(N)$ (linear scan) or $O(N^2)$ (nested dependency, like LIS).
    **時間**：通常為 $O(N)$（線性掃描）或 $O(N^2)$（巢狀依賴，如最長遞增子序列）。
*   **Space**: Standard is $O(N)$, often optimizable to $O(1)$ or $O(K)$ if dependency is limited to the last $K$ steps.
    **空間**：標準為 $O(N)$，若依賴僅限於最後 $K$ 步，通常可優化至 $O(1)$ 或 $O(K)$。

### When to Use / Not Use（適用與不適用場景）
*   **Use when**: The problem asks for maximum/minimum, counting ways, or existence (True/False), and the problem has *Optimal Substructure* and *Overlapping Subproblems*.
    **適用時機**：問題詢問最大/最小值、計算方法數或存在性（真/假），且問題具備「最佳子結構」與「重疊子問題」特性。
*   **Do NOT use when**: You need to return all valid permutations/combinations (use Backtracking) or the data is unsorted and requires simple lookup (use HashMap).
    **不適用時機**：需要回傳所有有效的排列/組合（應使用回溯法），或數據未排序且僅需簡單查找（應使用雜湊表）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Linear Transition (Fibonacci Style)
**線性轉移（費波那契風格）**
*   **Equation**: $dp[i] = dp[i-1] + dp[i-2]$
*   **Examples**: Climbing Stairs, House Robber.
*   **Key**: Depends only on a fixed number of previous states.
    **關鍵**：僅依賴固定數量的先前狀態。

### B. "Ending at $i$" (Subsequence/Subarray)
**「以 $i$ 結尾」（子序列/子陣列）**
*   **Equation**: $dp[i] = \max(dp[j]) + 1$ for $0 \le j < i$ (LIS), or $dp[i] = \max(nums[i], nums[i] + dp[i-1])$ (Kadane's).
*   **Examples**: Longest Increasing Subsequence, Maximum Subarray Sum.
*   **Key**: You must decide whether to extend the previous sequence or start a new one.
    **關鍵**：必須決定是延續先前的序列，還是重新開始一個新的。

### C. Partitioning / Splitting
**分割 / 切分**
*   **Equation**: $dp[i] = \text{OR}(dp[j] \land \text{isValid}(j, i))$
*   **Examples**: Word Break, Palindrome Partitioning II.
*   **Key**: Checking all possible split points $j$ before $i$.
    **關鍵**：檢查 $i$ 之前的所有可能切分點 $j$。

---

## 4. Example Walkthrough（範例講解）

### Problem: Longest Increasing Subsequence (LIS)
### 問題：最長遞增子序列

**Problem Statement**:
Given an integer array `nums`, return the length of the longest strictly increasing subsequence.
給定一個整數陣列 `nums`，回傳最長嚴格遞增子序列的長度。

**Example**:
Input: `[10, 9, 2, 5, 3, 7, 101, 18]`
Output: `4` (The subsequence is `[2, 3, 7, 101]`)

---

### Approach 1: Brute Force (DFS)
**思路 1：暴力法（深度優先搜尋）**
Try every possible subsequence. Include or exclude each element.
嘗試所有可能的子序列。包含或排除每個元素。
*   **Complexity**: $O(2^N)$ time.
    **複雜度**：時間 $O(2^N)$。
*   **Verdict**: TLE (Time Limit Exceeded).
    **結論**：超時。

---

### Approach 2: DP ($O(N^2)$)
**思路 2：動態規劃（$O(N^2)$）**

**State Definition**: $dp[i]$ represents the length of the LIS **ending at index $i$**.
**狀態定義**：$dp[i]$ 代表**以索引 $i$ 結尾**的 LIS 長度。

**Transition**:
For every $i$, check all $j < i$. If $nums[i] > nums[j]$, then $nums[i]$ can be appended to the sequence ending at $j$.
**轉移**：
對於每個 $i$，檢查所有 $j < i$。如果 $nums[i] > nums[j]$，則 $nums[i]$ 可以接在以 $j$ 結尾的序列後面。
$$dp[i] = \max(dp[i], dp[j] + 1)$$

**TypeScript Solution (DP)**:

```typescript
function lengthOfLIS_DP(nums: number[]): number {
    if (nums.length === 0) return 0;

    // Initialize DP array with 1, as every element is an LIS of length 1 by itself.
    // 初始化 DP 陣列為 1，因為每個元素本身就是長度為 1 的 LIS。
    const dp: number[] = new Array(nums.length).fill(1);
    let maxLen = 1;

    for (let i = 1; i < nums.length; i++) {
        for (let j = 0; j < i; j++) {
            // If current element is greater than previous element, we can extend.
            // 如果當前元素大於之前的元素，我們可以延續序列。
            if (nums[i] > nums[j]) {
                dp[i] = Math.max(dp[i], dp[j] + 1);
            }
        }
        // Update global maximum.
        // 更新全域最大值。
        maxLen = Math.max(maxLen, dp[i]);
    }

    return maxLen;
}
```

---

### Approach 3: Patience Sorting / Greedy + Binary Search (Optimal)
**思路 3：耐心排序 / 貪婪 + 二分搜尋（最佳解）**

*Note: While strictly not "pure" DP, this is the expected Advanced solution for this specific problem.*
*註：雖然嚴格來說這不是「純」DP，但這是此特定問題預期的進階解法。*

**Intuition**: We want to make the increasing subsequence grow as slowly as possible to allow room for more elements. We maintain a `tails` array where `tails[i]` is the smallest tail of all increasing subsequences of length `i+1`.
**直覺**：我們希望遞增子序列增長得越慢越好，以便容納更多元素。我們維護一個 `tails` 陣列，其中 `tails[i]` 是長度為 `i+1` 的所有遞增子序列中，結尾最小的那個數值。

**TypeScript Solution (Optimal)**:

```typescript
function lengthOfLIS_Optimal(nums: number[]): number {
    // tails[i] stores the smallest tail of all increasing subsequences of length i+1.
    // tails[i] 儲存長度為 i+1 的所有遞增子序列中最小的結尾數值。
    const tails: number[] = [];

    for (const num of nums) {
        // Use Binary Search to find the first element in tails >= num.
        // 使用二分搜尋在 tails 中找到第一個 >= num 的元素。
        let left = 0, right = tails.length;
        
        while (left < right) {
            const mid = Math.floor((left + right) / 2);
            if (tails[mid] < num) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        // If num is greater than all tails, append it (extend largest LIS).
        // 如果 num 大於所有 tails 元素，將其附加在後（延長最長的 LIS）。
        if (left === tails.length) {
            tails.push(num);
        } else {
            // Otherwise, replace the existing element to maintain "smallest tail" property.
            // 否則，替換現有元素以維持「最小結尾」的特性。
            tails[left] = num;
        }
    }

    return tails.length;
}
```

### Complexity Analysis（複雜度分析）
*   **Time**: $O(N \log N)$ (Binary search inside a loop).
    **時間**：$O(N \log N)$（迴圈內進行二分搜尋）。
*   **Space**: $O(N)$ (for the `tails` array).
    **空間**：$O(N)$（用於 `tails` 陣列）。

---

### Incorrect Approach (Common Mistake)
**錯誤示範（常見錯誤）**

*   **Mistake**: Sorting the array first and finding the longest contiguous subarray.
    **錯誤**：先對陣列排序，然後尋找最長連續子陣列。
*   **Why it's wrong**: Sorting destroys the original relative order of indices, which is crucial for the definition of a "subsequence".
    **為何錯**：排序會破壞原始索引的相對順序，而這對於「子序列」的定義至關重要。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Subarray (子陣列)** | **Subsequence (子序列)** | Subarray must be **contiguous** (e.g., `nums[i...j]`). Subsequence maintains order but can skip elements. <br> 子陣列必須**連續**。子序列保持順序但可跳過元素。 |
| **$dp[i]$ = Result ending at $i$** | **$dp[i]$ = Result up to $i$** | "Ending at $i$" usually requires checking previous states to connect (LIS). "Up to $i$" usually carries the global max forward (House Robber). <br> 「以 $i$ 結尾」通常需要檢查先前狀態來連接。「截至 $i$ 為止」通常將全域最大值帶入下一步。 |
| **Greedy** | **Dynamic Programming** | Greedy makes the locally optimal choice at each step. DP considers previous choices to find the global optimum. <br> 貪婪法在每一步做出局部最佳選擇。DP 考慮先前的選擇以找到全域最佳解。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Define the State**: "I will define `dp[i]` as the maximum profit we can make considering houses `0` to `i`."
    **定義狀態**：「我將 `dp[i]` 定義為考慮房屋 `0` 到 `i` 時能獲得的最大利潤。」
2.  **Establish Recurrence**: "To calculate `dp[i]`, I have two choices: rob house `i` (and add to `dp[i-2]`) or skip it (taking `dp[i-1]`)."
    **建立遞迴關係**：「為了計算 `dp[i]`，我有兩個選擇：搶劫房屋 `i`（並加上 `dp[i-2]`）或跳過它（取 `dp[i-1]`）。」
3.  **Discuss Base Cases**: "For index 0, the value is just `nums[0]`. For index 1..."
    **討論基本情況**：「對於索引 0，值就是 `nums[0]`。對於索引 1...」
4.  **Optimize**: "Since `dp[i]` only depends on `i-1` and `i-2`, I can reduce space from $O(N)$ to $O(1)$."
    **優化**：「由於 `dp[i]` 僅依賴 `i-1` 和 `i-2`，我可以將空間從 $O(N)$ 減少到 $O(1)$。」

### Whiteboard Strategy（白板策略）
*   Draw a small table for `dp` values corresponding to the input array.
    為輸入陣列繪製一個對應的小型 `dp` 數值表。
*   Manually fill the first 3-4 indices to verify your recurrence relation before coding.
    在寫程式碼之前，手動填寫前 3-4 個索引以驗證你的遞迴關係。

### Common Follow-ups（常見追問）
*   "What if the array is circular?" (e.g., House Robber II -> Run DP twice).
    「如果陣列是環狀的怎麼辦？」（例如：House Robber II -> 執行兩次 DP）。
*   "How to reconstruct the solution path?" (Store `parent` pointers).
    「如何重建解的路徑？」（儲存 `parent` 指標）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Climbing Stairs (or Fibonacci Number)
*   **Prompt**: Count ways to reach step $n$ taking 1 or 2 steps.
    **題目**：計算到達第 $n$ 階的方法數，每次可走 1 或 2 步。
*   **Hint**: $dp[i] = dp[i-1] + dp[i-2]$. Space optimize to $O(1)$.
    **提示**：$dp[i] = dp[i-1] + dp[i-2]$。空間優化至 $O(1)$。

### 2. Intermediate: Decode Ways
*   **Prompt**: Decode a string of digits where '1'->'A', '26'->'Z'. Handle '0'.
    **題目**：解碼數字字串，其中 '1'->'A', '26'->'Z'。需處理 '0'。
*   **Hint**: $dp[i]$ depends on single digit valid check ($s[i]$) and two-digit valid check ($s[i-1...i]$). Watch out for leading zeros.
    **提示**：$dp[i]$ 取決於單一數字有效性檢查 ($s[i]$) 和兩位數字有效性檢查 ($s[i-1...i]$)。注意前導零。

### 3. Advanced: Maximum Profit in Job Scheduling
*   **Prompt**: Given `startTime`, `endTime`, and `profit` arrays, find max profit without overlapping jobs.
    **題目**：給定 `startTime`、`endTime` 和 `profit` 陣列，找出不重疊工作的最大利潤。
*   **Hint**: Sort by end time. $dp[i] = \max(dp[i-1], \text{profit}[i] + dp[\text{prev\_non\_overlap}])$. Use Binary Search to find `prev_non_overlap`.
    **提示**：依結束時間排序。$dp[i] = \max(dp[i-1], \text{profit}[i] + dp[\text{prev\_non\_overlap}])$。使用二分搜尋找到 `prev_non_overlap`。

---

## 8. Checklists（快速檢核表）

*   [ ] **State Definition**: Does $dp[i]$ mean "exactly at $i$" or "up to $i$"?
    **狀態定義**：$dp[i]$ 是指「恰好在 $i$」還是「截至 $i$」？
*   [ ] **Initialization**: Did you handle $dp[0]$ and $dp[1]$ correctly? Is the array size $N$ or $N+1$?
    **初始化**：你是否正確處理了 $dp[0]$ 和 $dp[1]$？陣列大小是 $N$ 還是 $N+1$？
*   [ ] **Loop Direction**: Are you iterating forward (typical) or backward (sometimes needed)?
    **迴圈方向**：你是向前迭代（典型）還是向後迭代（有時需要）？
*   [ ] **Space Optimization**: Can you replace the array with 2-3 variables?
    **空間優化**：你能用 2-3 個變數取代陣列嗎？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The "Domino Effect" (骨牌效應)**:
    Think of 1-D DP as pushing dominos. To know if domino $i$ falls (or how hard it falls), you only need to know the state of the domino immediately pushing it ($i-1$ or $i-2$). You don't need to look back at the start of the chain every time.
    將一維 DP 想像成推骨牌。要知道骨牌 $i$ 是否倒下（或倒下的力道），你只需要知道直接推動它的骨牌（$i-1$ 或 $i-2$）的狀態。你不需要每次都回頭看鏈條的起點。

*   **"Filling a Form" (填寫表格)**:
    DP is like filling out a tax form. Line 10 asks for "Sum of Line 8 and Line 9". You don't recalculate Line 8 from scratch; you just look at the box you already wrote in.
    DP 就像填寫稅務表格。第 10 行要求「第 8 行與第 9 行之和」。你不會從頭重新計算第 8 行；你只是看一眼你已經填好的格子。