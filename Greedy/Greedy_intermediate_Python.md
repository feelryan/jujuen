# Greedy Algorithms: Intermediate Guide
# 貪婪演算法：中階指南

## 1. Learning Goals（學習目標）

*   **Distinguish between Greedy and Dynamic Programming:** Understand when a local optimal choice leads to a global optimum versus when you need to explore all sub-problems.
    **區分貪婪與動態規劃：** 理解何時「局部最佳解」能導向「全域最佳解」，以及何時需要探索所有子問題。
*   **Master the "Exchange Argument" Proof:** Learn how to justify your greedy approach to an interviewer by proving that swapping a non-greedy choice with a greedy one improves (or does not worsen) the result.
    **掌握「交換論證」證明：** 學習如何向面試官證明你的貪婪策略，即證明將「非貪婪選擇」替換為「貪婪選擇」會改善（或至少不惡化）結果。
*   **Proficiency in Interval & Heap Patterns:** Gain fluency in standard greedy patterns involving interval scheduling and priority queue-based decision making.
    **熟練區間與堆積模式：** 流暢運用涉及區間排程與基於優先佇列決策的標準貪婪模式。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Greedy algorithms build up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法透過逐步構建解法，總是選擇當下能提供最大利益的下一步。

It relies on the **Greedy Choice Property**: A global optimum can be arrived at by selecting a local optimum.
它依賴於 **貪婪選擇屬性**：透過選擇局部最佳解，最終可以達成全域最佳解。

### Complexity（複雜度）
*   **Time Complexity:** Often $O(N \log N)$ due to sorting, or $O(N)$ if using a heap/priority queue efficiently (or if input is pre-sorted).
    **時間複雜度：** 通常為 $O(N \log N)$，因為需要排序；若有效使用堆積/優先佇列（或輸入已排序），則可能為 $O(N)$。
*   **Space Complexity:** Usually $O(1)$ or $O(N)$ depending on whether we need auxiliary storage for the output or sorting.
    **空間複雜度：** 通常為 $O(1)$ 或 $O(N)$，取決於是否需要輔助空間來儲存輸出或進行排序。

### When to Use vs. Not to Use（適用與不適用場景）

| Feature | Greedy (貪婪) | Dynamic Programming (動態規劃) |
| :--- | :--- | :--- |
| **Decision (決策)** | Makes one optimal choice at each step and never looks back. <br> 每一步做一個最佳選擇，絕不回頭。 | Considers all possible choices and their consequences. <br> 考慮所有可能的選擇及其後果。 |
| **Correctness (正確性)** | Harder to prove; requires specific mathematical properties (Matroids). <br> 較難證明；需要特定的數學屬性（擬陣）。 | Guaranteed to find the optimal solution if state transitions are correct. <br> 若狀態轉移正確，保證能找到最佳解。 |
| **Example (範例)** | Fractional Knapsack, Dijkstra, Prim/Kruskal. <br> 分數背包問題、Dijkstra、Prim/Kruskal 演算法。 | 0/1 Knapsack, Longest Common Subsequence. <br> 0/1 背包問題、最長共同子序列。 |

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Interval Scheduling (Sorting by End Time):**
    **區間排程（依結束時間排序）：**
    *   Solving problems like "maximum number of non-overlapping meetings."
    *   解決如「最大不重疊會議數量」的問題。

2.  **Heap-based Greedy:**
    **基於堆積的貪婪：**
    *   Using a Min-Heap or Max-Heap to constantly retrieve the "best" current element (e.g., merging ropes with min cost).
    *   使用最小堆積或最大堆積來持續獲取當前「最好」的元素（例如：以最小成本合併繩子）。

3.  **Two Pointers / Partitioning:**
    **雙指針 / 分割：**
    *   Greedily expanding a window or partition until a condition breaks (e.g., Jump Game, Partition Labels).
    *   貪婪地擴展視窗或分區，直到條件被破壞（例如：跳躍遊戲、劃分字母區間）。

4.  **Sorting by Specific Attribute:**
    **依特定屬性排序：**
    *   Custom comparators are key (e.g., reconstruct queue by height).
    *   自定義比較器是關鍵（例如：根據身高重建佇列）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Non-overlapping Intervals (LeetCode 435)
### 問題：無重疊區間

**Problem Statement:**
Given an array of intervals `intervals` where `intervals[i] = [start, end]`, return the *minimum* number of intervals you need to remove to make the rest of the intervals non-overlapping.
給定一個區間陣列 `intervals`，其中 `intervals[i] = [start, end]`，回傳為了讓剩餘區間不重疊，所需移除的 *最小* 區間數量。

### Approach & Evolution（思路演進）

1.  **Brute Force (暴力解):**
    *   Try all possible subsets of intervals, check if they overlap, and find the largest valid subset.
    *   嘗試所有可能的區間子集，檢查是否重疊，並找出最大的有效子集。
    *   Complexity: $O(2^N)$. Too slow.
    *   複雜度：$O(2^N)$。太慢。

2.  **Dynamic Programming (動態規劃):**
    *   Sort by start time. $DP[i]$ = max non-overlapping intervals ending at index $i$. This is similar to Longest Increasing Subsequence (LIS).
    *   依開始時間排序。$DP[i]$ = 在索引 $i$ 結束的最大不重疊區間數。這類似於最長遞增子序列 (LIS)。
    *   Complexity: $O(N^2)$. Acceptable but not optimal.
    *   複雜度：$O(N^2)$。可接受但非最佳。

3.  **Greedy (Optimal):**
    *   **Intuition:** To maximize the number of meetings we can attend, we should always pick the meeting that **ends the earliest**. Why? Because it leaves the most time remaining for subsequent meetings.
    *   **直覺：** 為了最大化我們能參加的會議數量，我們應該總是選擇 **最早結束** 的會議。為什麼？因為這樣能為後續會議留出最多的時間。
    *   **Strategy:** Sort by end time. Iterate through. If a new interval starts *after* the current one ends, keep it. Otherwise, remove it (count it as removed).
    *   **策略：** 依結束時間排序。遍歷陣列。若新區間的開始時間在當前區間結束 *之後*，則保留。否則，移除它（計入移除數）。

### Python Solution（Python 參考解）

```python
from typing import List

class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        # Edge case: empty list
        # 邊界條件：空列表
        if not intervals:
            return 0
        
        # Sort intervals by their end time (ascending)
        # 根據區間的結束時間進行排序（升序）
        # Key Logic: Finishing early leaves more room for the next interval.
        # 關鍵邏輯：越早結束，留給下一個區間的空間越多。
        intervals.sort(key=lambda x: x[1])
        
        end_time = intervals[0][1]
        count_removed = 0
        
        # Iterate starting from the second interval
        # 從第二個區間開始遍歷
        for i in range(1, len(intervals)):
            current_start, current_end = intervals[i]
            
            if current_start < end_time:
                # Overlap detected. We must remove the current interval 
                # because the previous one (which ends earlier) is "better".
                # 偵測到重疊。我們必須移除當前區間，
                # 因為前一個區間（結束得更早）是「較佳的」。
                count_removed += 1
            else:
                # No overlap. Update the end_time to the current interval's end.
                # 無重疊。將 end_time 更新為當前區間的結束時間。
                end_time = current_end
                
        return count_removed

# Complexity Analysis:
# Time: O(N log N) due to sorting. The iteration is O(N).
# Space: O(1) or O(N) depending on sort implementation (Timsort uses O(N)).
# 複雜度分析：
# 時間：O(N log N)，因為排序。遍歷為 O(N)。
# 空間：O(1) 或 O(N)，取決於排序實作（Timsort 使用 O(N)）。
```

### Common Mistake (錯誤示範)
*   **Sorting by Start Time:** If you pick the interval that starts earliest, you might pick a very long interval (e.g., `[0, 100]`) that blocks all other short intervals (e.g., `[1, 2], [3, 4]...`).
    **依開始時間排序：** 如果你選擇最早開始的區間，可能會選到一個非常長的區間（如 `[0, 100]`），它會擋住所有其他短區間（如 `[1, 2], [3, 4]...`）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Local vs Global** | **Pitfall:** Assuming local best is always global best without proof. <br> **陷阱：** 未經證明即假設局部最佳總是全域最佳。 <br> **Check:** Can I construct a counter-example where picking the greedy option now hurts me later? <br> **檢查：** 我能否建構一個反例，證明現在選擇貪婪選項會損害後續結果？ |
| **Sort Key** | **Pitfall:** Sorting by `start` vs `end` vs `duration`. <br> **陷阱：** 依 `start` vs `end` vs `duration` 排序。 <br> **Check:** For packing/scheduling, usually sort by `end`. For covering/merging, usually sort by `start`. <br> **檢查：** 對於打包/排程，通常依 `end` 排序。對於覆蓋/合併，通常依 `start` 排序。 |
| **Greedy vs DP** | **Pitfall:** Using Greedy on Knapsack (0/1) problems. <br> **陷阱：** 在 0/1 背包問題上使用貪婪法。 <br> **Reason:** In 0/1, you cannot take a fraction; taking a high-value item might waste space. Greedy works for **Fractional** Knapsack. <br> **原因：** 在 0/1 中，不能取分數部分；取高價值物品可能會浪費空間。貪婪法適用於 **分數** 背包問題。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. The "Greedy Hypothesis" (提出貪婪假設)
Don't just start coding. Say: "This looks like an optimization problem. I suspect a Greedy approach might work because [reason, e.g., we want to process tasks as early as possible]."
不要直接開始寫程式。說：「這看起來像是一個最佳化問題。我懷疑貪婪法可能行得通，因為 [理由，例如：我們希望儘早處理任務]。」

### 2. The Exchange Argument (交換論證 - High Value for Seniors)
If the interviewer asks "Are you sure?", use this logic:
如果面試官問「你確定嗎？」，使用此邏輯：
*   "Suppose there is an optimal solution $O$ that differs from my greedy choice $G$."
    「假設有一個最佳解 $O$ 與我的貪婪選擇 $G$ 不同。」
*   "If I swap the choice in $O$ with my choice $G$, the solution remains valid and is no worse (or better)."
    「如果我將 $O$ 中的選擇替換為我的選擇 $G$，解法仍然有效且不會變差（甚至更好）。」
*   "Therefore, the greedy choice is safe."
    「因此，貪婪選擇是安全的。」

### 3. Whiteboard Strategy (白板策略)
*   Write down 2-3 small examples. One standard, one edge case, one counter-intuitive case.
    寫下 2-3 個小範例。一個標準的，一個邊界情況，一個反直覺的情況。
*   Sort the data visually on the board to see patterns.
    在白板上視覺化地排序數據以觀察模式。

---

## 7. Practice Problems（練習題）

### Level: Easy (暖身)
**Problem:** **Partition Labels (LeetCode 763)**
**Hint:** Store the last occurrence index of each character. Iterate and extend the current partition end until the index reaches the partition end.
**提示：** 儲存每個字元最後出現的索引。遍歷並擴展當前分區結束點，直到索引到達分區結束點。

### Level: Intermediate (中階)
**Problem:** **Jump Game II (LeetCode 45)**
**Hint:** Don't just check if you *can* jump (Jump Game I). Instead, track `current_end` of the jump range and `farthest` you can reach. Only increment steps when you reach `current_end`. This is an implicit BFS/Greedy.
**提示：** 不要只檢查是否 *能* 跳到（Jump Game I）。相反，追蹤跳躍範圍的 `current_end` 和你能到達的 `farthest`。只有當你到達 `current_end` 時才增加步數。這是一種隱式的 BFS/貪婪法。

### Level: Hard (進階)
**Problem:** **Gas Station (LeetCode 134)**
**Hint:**
1. If total gas < total cost, impossible.
2. If you can't reach station $B$ from $A$, you can't reach $B$ from any station between $A$ and $B$. Start over from $B+1$.
**提示：**
1. 若總油量 < 總消耗，則不可能。
2. 若你無法從 $A$ 到達 $B$，則 $A$ 與 $B$ 之間的所有站點也都無法到達 $B$。從 $B+1$ 重新開始。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Sorting:** Did I sort the input? If not, is it implicitly sorted or using a Heap?
    **排序：** 我是否對輸入進行了排序？如果沒有，它是否隱式排序或使用了堆積？
*   [ ] **Direction:** Am I going forward (start to end) or backward? Sometimes backward is easier (e.g., Jump Game).
    **方向：** 我是向前（從頭到尾）還是向後？有時向後更容易（例如：跳躍遊戲）。
*   [ ] **Destruction:** Does my choice limit future valid choices more than necessary?
    **破壞性：** 我的選擇是否比必要時更多地限制了未來的有效選擇？
*   [ ] **Complexity:** Is my sorting bottleneck ($N \log N$) acceptable for $N=10^5$?
    **複雜度：** 我的排序瓶頸 ($N \log N$) 對於 $N=10^5$ 是否可接受？

---

## 9. Memory Anchors（記憶錨點）

*   **The "Cashier" Analogy:**
    **「收銀員」類比：**
    When giving change, you always give the largest denomination coin possible first (in most currency systems). This is the classic Greedy example.
    找零時，你總是先給面額最大的硬幣（在大多數貨幣系統中）。這是經典的貪婪範例。

*   **The "Shortest Job First" (SJF):**
    **「最短作業優先」(SJF)：**
    Imagine you are a printer. To minimize the average waiting time for everyone, you print the shortest documents first.
    想像你是一台印表機。為了最小化每個人的平均等待時間，你先列印最短的文件。

*   **Visual Anchor - The Horizon:**
    **視覺錨點 - 地平線：**
    In interval problems, imagine looking at the horizon. You want to fit as many buildings as possible without them overlapping. You prioritize the ones that "finish" (leave the view) the soonest.
    在區間問題中，想像看著地平線。你想放入盡可能多的建築物而不重疊。你優先考慮那些最快「結束」（離開視野）的建築物。