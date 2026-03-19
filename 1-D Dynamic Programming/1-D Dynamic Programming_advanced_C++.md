Here is the comprehensive guide tailored for a Senior Software Engineer, focusing on **Advanced 1-D Dynamic Programming**.

這是一份專為資深軟體工程師量身打造的指南，專注於 **進階一維動態規劃（Advanced 1-D Dynamic Programming）**。

---

# Advanced 1-D Dynamic Programming Interview Guide
# 進階一維動態規劃面試指南

## 1. Learning Goals（學習目標）

*   **Master State Definition & Transition:** Move beyond simple recurrence; learn to define states that capture constraints (e.g., "k transactions", "non-adjacent") without exploding complexity.
    **掌握狀態定義與轉移：** 超越簡單的遞迴關係；學習定義能捕捉限制條件（如「k 次交易」、「不相鄰」）的狀態，且不讓複雜度爆炸。
*   **Space Optimization:** Instinctively optimize $O(N)$ space to $O(1)$ or $O(K)$ using rolling arrays/variables, a key differentiator for senior roles.
    **空間優化：** 直覺地利用滾動陣列/變數將 $O(N)$ 空間優化至 $O(1)$ 或 $O(K)$，這是資深職位的關鍵區分點。
*   **Combine DP with Other Structures:** Solve $O(N^2)$ bottlenecks using Binary Search or Data Structures (e.g., LIS optimization) to achieve $O(N \log N)$.
    **結合 DP 與其他結構：** 利用二分搜尋或資料結構（如 LIS 優化）解決 $O(N^2)$ 的瓶頸，達到 $O(N \log N)$。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
1-D DP is essentially finding the optimal path on a Directed Acyclic Graph (DAG) that is topologically sorted linearly.
一維動態規劃本質上是在一個線性拓樸排序的有向無環圖（DAG）上尋找最佳路徑。

Unlike simple recursion, we store results of subproblems to avoid redundant computation (Memoization) or build the solution iteratively (Tabulation).
與簡單遞迴不同，我們儲存子問題的結果以避免重複計算（記憶法），或迭代地建構解（列表法）。

### Complexity（複雜度）
*   **Time:** Typically $O(N)$ or $O(N^2)$. For advanced problems, target $O(N \log N)$.
    **時間：** 通常為 $O(N)$ 或 $O(N^2)$。對於進階問題，目標是 $O(N \log N)$。
*   **Space:** Naively $O(N)$. Optimized to $O(1)$ (constant history) or $O(K)$ (window history).
    **空間：** 樸素解法為 $O(N)$。優化後為 $O(1)$（常數歷史）或 $O(K)$（視窗歷史）。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** Problem asks for Maximum/Minimum, Count ways, or Existence (True/False), and the decision at index $i$ depends only on previous states $0...i-1$.
    **適用：** 問題詢問最大/最小值、方法數或存在性（真/假），且索引 $i$ 的決策僅取決於先前的狀態 $0...i-1$。
*   **Do NOT use when:** The problem has cycles (use Graph algorithms) or the local optimal choice always leads to the global optimum (use Greedy).
    **不適用：** 問題包含環（使用圖演算法）或局部最佳解總是導向全域最佳解（使用貪婪演算法）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. The "Rolling Window" (Fibonacci Style)
**「滾動視窗」模式（費波那契風格）**
$dp[i]$ depends on a fixed number of previous states (e.g., $i-1, i-2$).
$dp[i]$ 取決於固定數量的先前狀態（例如 $i-1, i-2$）。
*   *Examples:* Climbing Stairs, House Robber.
*   *Optimization:* Reduce space to $O(1)$.

### B. The "Look Back" (Partition/Subsequence Style)
**「回溯」模式（分割/子序列風格）**
$dp[i]$ depends on **all** $j < i$. Usually involves a nested loop.
$dp[i]$ 取決於 **所有** $j < i$。通常涉及巢狀迴圈。
*   *Examples:* Longest Increasing Subsequence (LIS), Word Break.
*   *Optimization:* Use Binary Search or Segment Trees to speed up the lookup.

### C. Multi-State 1-D DP
**多狀態一維 DP**
At each index $i$, we maintain multiple states (e.g., `hold_stock`, `sold_stock`, `cooldown`).
在每個索引 $i$，我們維護多個狀態（例如 `持有股票`、`已賣出`、`冷卻中`）。
*   *Examples:* Best Time to Buy and Sell Stock with Cooldown.

---

## 4. Example Walkthrough（範例講解）

### Problem: Longest Increasing Subsequence (LIS) - Optimized
### 問題：最長遞增子序列 - 優化版

**Problem Statement:**
Given an integer array `nums`, return the length of the longest strictly increasing subsequence.
給定一個整數陣列 `nums`，返回最長嚴格遞增子序列的長度。

**Input:** `[10,9,2,5,3,7,101,18]`
**Output:** `4` (The subsequence is `[2,3,7,101]`)

---

### Approach Evolution（思路演進）

#### 1. Brute Force (DFS)
Generate all subsequences and check if increasing.
生成所有子序列並檢查是否遞增。
*   Time: $O(2^N)$ - Unacceptable.
*   時間：$O(2^N)$ - 無法接受。

#### 2. Standard DP ($O(N^2)$)
Let $dp[i]$ be the length of LIS ending at index $i$.
令 $dp[i]$ 為以索引 $i$ 結尾的 LIS 長度。
For each $i$, check all $j < i$. If $nums[i] > nums[j]$, then $dp[i] = \max(dp[i], dp[j] + 1)$.
對於每個 $i$，檢查所有 $j < i$。如果 $nums[i] > nums[j]$，則 $dp[i] = \max(dp[i], dp[j] + 1)$。
*   Time: $O(N^2)$ - Acceptable for $N \le 5000$.
*   時間：$O(N^2)$ - 對於 $N \le 5000$ 可接受。

#### 3. Advanced Optimization: Patience Sorting ($O(N \log N)$)
Instead of storing the *length* at each index, we build the potential LIS array `tails`.
不儲存每個索引的長度，而是建構潛在的 LIS 陣列 `tails`。
`tails[k]` stores the **smallest tail of all increasing subsequences of length k+1**.
`tails[k]` 儲存**長度為 k+1 的所有遞增子序列中，最小的尾數**。
This array will always be sorted, allowing Binary Search.
此陣列將始終保持排序狀態，允許使用二分搜尋。

---

### C++ Reference Solution (Advanced)
### C++ 參考解（進階）

```cpp
#include <vector>
#include <algorithm> // for std::lower_bound

class Solution {
public:
    int lengthOfLIS(std::vector<int>& nums) {
        // tails array: tails[i] stores the smallest tail of all increasing subsequences of length i+1.
        // tails 陣列：tails[i] 儲存長度為 i+1 的所有遞增子序列中，數值最小的結尾元素。
        std::vector<int> tails;
        
        for (int num : nums) {
            // Use binary search to find the first element in tails that is >= num
            // 使用二分搜尋在 tails 中找到第一個 >= num 的元素
            auto it = std::lower_bound(tails.begin(), tails.end(), num);
            
            if (it == tails.end()) {
                // If num is greater than all tails, we can extend the longest subsequence.
                // 如果 num 比所有結尾元素都大，我們可以延長最長的子序列。
                tails.push_back(num);
            } else {
                // If we find an element, replace it with num.
                // This lowers the threshold for future elements to extend a subsequence of this length.
                // 如果找到元素，用 num 替換它。
                // 這降低了未來元素要延長此長度子序列的門檻（貪婪策略）。
                *it = num;
            }
        }
        
        // The size of tails represents the length of the LIS.
        // tails 的大小代表 LIS 的長度。
        return tails.size();
    }
};
```

### Why this works (Logic Check)
### 為何有效（邏輯檢查）
*   **Greedy Choice:** We want the increasing subsequence to grow as slowly as possible so we have room for more elements later. Replacing a larger tail with a smaller `num` achieves this.
    **貪婪選擇：** 我們希望遞增子序列增長得越慢越好，以便後續有空間容納更多元素。用較小的 `num` 替換較大的尾數可以達到此目的。
*   **Note:** The `tails` array does NOT necessarily represent the actual LIS elements in order, but its *length* is correct.
    **注意：** `tails` 陣列並不一定代表實際的 LIS 元素順序，但其 *長度* 是正確的。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Subarray vs Subsequence** | **Subarray:** Contiguous (slice). **Subsequence:** Non-contiguous (delete elements, keep order). <br> **子陣列：** 連續（切片）。**子序列：** 不連續（刪除元素，保持順序）。 |
| **Greedy vs DP** | Greedy makes the locally optimal choice at each step. DP considers all choices (or optimized past choices). <br> **貪婪 vs DP：** 貪婪在每一步做局部最佳選擇。DP 考慮所有選擇（或優化過的過去選擇）。 |
| **State Explosion** | Adding too many dimensions to the DP state (e.g., keeping the full set of used numbers) instead of just the necessary constraint (e.g., last number used). <br> **狀態爆炸：** 在 DP 狀態中加入過多維度（例如保留整組已用數字），而非僅保留必要的限制條件（例如最後使用的數字）。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Define the Recurrence Relation first:** "Let $dp[i]$ represent the max profit up to day $i$..."
    **首先定義遞迴關係：** 「令 $dp[i]$ 代表直到第 $i$ 天的最大利潤...」
2.  **Discuss Base Cases:** "For index 0, the value is simply..."
    **討論基本情況：** 「對於索引 0，其值僅為...」
3.  **Propose Optimization:** "Since $dp[i]$ only relies on $dp[i-1]$, we can optimize space to $O(1)$."
    **提出優化：** 「由於 $dp[i]$ 僅依賴 $dp[i-1]$，我們可以將空間優化至 $O(1)$。」

### Whiteboard Strategy（白板策略）
*   Draw a small table for `N=5`. Fill it manually to show you understand the transitions.
    畫一個 `N=5` 的小表格。手動填寫它以顯示你理解轉移過程。
*   Write the state transition equation **before** writing code.
    在寫程式碼**之前**先寫下狀態轉移方程式。

### Common Follow-ups（常見追問）
*   "How would you reconstruct the actual solution path, not just the value?" (Requires storing parent pointers).
    「你要如何重建實際的解路徑，而不僅僅是數值？」（需要儲存父指標）。
*   "What if the input stream is infinite?" (Discuss memory constraints).
    「如果輸入流是無限的怎麼辦？」（討論記憶體限制）。

---

## 7. Practice Problems（練習題）

### 1. Easy (Warm-up): House Robber
**題目：** 打家劫舍
*   **Constraint:** Cannot rob adjacent houses.
    **限制：** 不能搶劫相鄰的房屋。
*   **Hint:** $dp[i] = \max(dp[i-1], dp[i-2] + nums[i])$. Optimize to 2 variables.
    **提示：** $dp[i] = \max(dp[i-1], dp[i-2] + nums[i])$。優化為 2 個變數。

### 2. Medium: Word Break
**題目：** 單詞拆分
*   **Problem:** Can string `s` be segmented into dictionary words?
    **問題：** 字串 `s` 能否被分割成字典中的單詞？
*   **Hint:** $dp[i]$ is true if $dp[j]$ is true AND $s[j:i]$ is in dict. Complexity $O(N^2)$.
    **提示：** 若 $dp[j]$ 為真且 $s[j:i]$ 在字典中，則 $dp[i]$ 為真。複雜度 $O(N^2)$。

### 3. Hard: Maximum Profit in Job Scheduling
**題目：** 規劃兼職工作的最大收益
*   **Problem:** Jobs have `startTime`, `endTime`, `profit`. Non-overlapping.
    **問題：** 工作有 `開始時間`、`結束時間`、`利潤`。不可重疊。
*   **Hint:** Sort by end time. $dp[i] = \max(dp[i-1], \text{profit}[i] + dp[\text{prev\_compatible\_index}])$. Use `upper_bound` to find `prev_compatible_index`.
    **提示：** 按結束時間排序。$dp[i] = \max(dp[i-1], \text{profit}[i] + dp[\text{前一個相容索引}])$。使用 `upper_bound` 尋找 `前一個相容索引`。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review / Debugging（自我審查 / 除錯）
- [ ] **Base Case:** Did I handle $i=0$ or empty input?
    **基本情況：** 我是否處理了 $i=0$ 或空輸入？
- [ ] **Indexing:** Is the DP array size $N$ or $N+1$? (Usually $N+1$ helps avoid index -1 checks).
    **索引：** DP 陣列大小是 $N$ 還是 $N+1$？（通常 $N+1$ 有助於避免索引 -1 的檢查）。
- [ ] **Transition:** Does the recurrence cover all possibilities (e.g., take vs. skip)?
    **轉移：** 遞迴關係是否涵蓋了所有可能性（例如：選取 vs 跳過）？
- [ ] **Space:** Can I reduce `vector<int> dp` to `int prev, curr`?
    **空間：** 我能將 `vector<int> dp` 縮減為 `int prev, curr` 嗎？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Form Filling" Analogy
**「填表」類比**
Imagine 1-D DP as filling out a tax form. Line 10 depends on Line 5 and Line 8. You cannot calculate Line 10 until previous lines are done.
將一維 DP 想像成填寫稅務表格。第 10 行取決於第 5 行和第 8 行。在完成前面的行之前，你無法計算第 10 行。

### The "Domino" Analogy
**「骨牌」類比**
For simple dependencies ($i$ depends on $i-1$), it's like dominoes falling. You only need to know if the previous domino fell to know if the current one will fall.
對於簡單的依賴關係（$i$ 依賴於 $i-1$），這就像骨牌倒下。你只需要知道前一個骨牌是否倒下，就能知道當前這個是否會倒下。