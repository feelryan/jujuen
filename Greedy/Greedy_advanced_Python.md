這是一份針對 **Senior Software Engineer** 設計的 **Advanced Greedy Algorithms** 面試實戰教材。內容專注於如何識別貪婪策略的適用性、如何運用「後悔策略（Regret Strategy）」與「交換論證（Exchange Argument）」來證明解法，以及如何區分 Greedy 與 DP。

This is an **Advanced Greedy Algorithms** interview preparation guide designed for **Senior Software Engineers**. The content focuses on identifying the applicability of greedy strategies, applying "Regret Strategy" and "Exchange Argument" to prove solutions, and distinguishing Greedy from DP.

---

# Advanced Greedy Algorithms (貪婪演算法進階指南)

## 1. Learning Objectives (學習目標)

1.  **Master the "Exchange Argument" for Proofs:**
    學會使用「交換論證法」來驗證貪婪策略的正確性，這是資深工程師與初階工程師的分水嶺。
    Learn to use the "Exchange Argument" to verify the correctness of a greedy strategy, which distinguishes senior engineers from juniors.

2.  **Implement "Regret" with Priority Queues:**
    掌握結合 Heap（堆積）的貪婪模式，允許在遍歷過程中「反悔」以優化局部決策。
    Master the greedy pattern combined with Heaps, allowing "regret" during traversal to optimize local decisions.

3.  **Distinguish Greedy from Dynamic Programming:**
    能夠精準判斷問題是否具有「貪婪選擇性質」，避免在需要 DP 的場景錯誤使用 Greedy。
    Accurately determine if a problem possesses the "Greedy Choice Property" to avoid using Greedy in scenarios requiring DP.

4.  **Optimize for Scale:**
    理解貪婪算法通常提供 $O(N \log N)$ 或 $O(N)$ 的解法，這在大規模系統設計討論中至關重要。
    Understand that greedy algorithms usually offer $O(N \log N)$ or $O(N)$ solutions, which is crucial in large-scale system design discussions.

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
貪婪演算法是一種在每一步選擇中都採取在當前狀態下最好（局部最佳）的選擇，從而希望導致結果是全局最佳的算法。
A greedy algorithm is an algorithm that makes the locally optimal choice at each step with the hope of finding a global optimum.

### Intuition (直覺)
想像你在登山，貪婪算法就是「每一步都往更高的地方走」，而不考慮下山再上另一座更高的山。
Imagine hiking; a greedy algorithm is "taking every step upwards," without considering going downhill to climb a higher peak later.

### Complexity (複雜度)
*   **Time:** Usually dominated by sorting ($O(N \log N)$) or heap operations ($O(N \log N)$).
    **時間：** 通常由排序 ($O(N \log N)$) 或堆積操作 ($O(N \log N)$) 主導。
*   **Space:** $O(1)$ (if sorting in-place) or $O(N)$ (if using a heap/auxiliary array).
    **空間：** $O(1)$（若原地排序）或 $O(N)$（若使用堆積/輔助陣列）。

### When to Use (適用場景)
1.  **Greedy Choice Property:** You can choose the local best and never look back.
    **貪婪選擇性質：** 你可以做出局部最佳選擇且永不回頭。
2.  **Optimal Substructure:** An optimal solution to the problem contains an optimal solution to subproblems.
    **最佳子結構：** 問題的最佳解包含子問題的最佳解。

### When NOT to Use (不適用場景)
If a decision today restricts valid options tomorrow in a way that prevents the global optimum (e.g., 0/1 Knapsack Problem).
如果今天的決策限制了明天的有效選項，從而阻礙了全局最佳解（例如：0/1 背包問題）。

---

## 3. Typical Patterns (典型題型 / 模式)

對於 Advanced Level，我們關注以下模式：
For the Advanced Level, we focus on the following patterns:

1.  **Sorting + Interval Scheduling (排序 + 區間調度):**
    Sorting by end time or start time to maximize non-overlapping intervals.
    依據結束時間或開始時間排序，以最大化不重疊區間。

2.  **Greedy with Heap (Priority Queue) - The "Regret" Strategy:**
    When you encounter a new element, you might decide to discard a previously selected element if the new one offers a better long-term advantage.
    當遇到新元素時，如果它提供更好的長期優勢，你可能會決定丟棄之前選擇的元素（反悔策略）。

3.  **String Concatenation / Lexicographical Order:**
    Custom sorting logic (e.g., sort `a` and `b` by comparing `a+b` vs `b+a`).
    自定義排序邏輯（例如：通過比較 `a+b` 與 `b+a` 來排序 `a` 和 `b`）。

4.  **Huffman Coding / Merge Patterns:**
    Repeatedly merging the two smallest/largest elements.
    重複合併兩個最小/最大的元素。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule III (LeetCode 630)
**Level:** Hard

**Problem Statement:**
There are `n` different online courses numbered from `1` to `n`. You are given an array `courses` where `courses[i] = [duration_i, lastDay_i]`. You must start the course at some day `t` and finish it by `lastDay_i`. You cannot take two courses simultaneously. Return the *maximum number of courses* you can take.
有 `n` 門不同的線上課程，編號為 `1` 到 `n`。給定一個陣列 `courses`，其中 `courses[i] = [duration_i, lastDay_i]`。你必須在某天 `t` 開始課程，並在 `lastDay_i` 之前完成。你不能同時修兩門課。請返回你能修讀的 *最大課程數量*。

---

### Thought Process (思路)

#### 1. Naive Approach (暴力法)
Try all permutations of courses.
嘗試所有課程的排列組合。
*   **Complexity:** $O(N!)$. Impossible for $N > 20$.
*   **複雜度：** $O(N!)$。對於 $N > 20$ 是不可能的。

#### 2. Greedy Intuition (貪婪直覺)
Should we sort by duration? No, a short course might have a very early deadline.
我們應該按持續時間排序嗎？不，短課程可能有一個非常早的截止日期。
Should we sort by deadline? Yes, processing tasks with earlier deadlines first gives us more room for later tasks.
我們應該按截止日期排序嗎？是的，優先處理截止日期較早的任務能為後續任務留出更多空間。

#### 3. The "Regret" Logic (反悔邏輯 - Advanced Step)
What if we pick a course (sorted by deadline) that is very long, preventing us from taking two shorter courses later?
如果我們選擇了一門（按截止日期排序的）非常長的課程，導致後來無法修讀兩門較短的課程怎麼辦？
*   **Strategy:** Iterate through courses sorted by deadline. Keep track of current total time. If a course fits, take it. If it doesn't fit, check if it's *shorter* than the *longest* course we've already taken. If so, **swap them** (regret taking the long one).
*   **策略：** 遍歷按截止日期排序的課程。記錄當前總時間。如果課程塞得進去，就修。如果塞不進去，檢查它是否比我們已經修過的 *最長* 課程還 *短*。如果是，**交換它們**（後悔修了那門長課）。
*   **Why?** By swapping a long course for a shorter one, the count remains the same, but the total time consumed decreases, giving us more space for future courses.
*   **為什麼？** 將長課程換成短課程，課程數量不變，但消耗的總時間減少了，為未來的課程留出更多空間。

---

### Python Solution (Python 參考解)

```python
import heapq
from typing import List

class Solution:
    def scheduleCourse(self, courses: List[List[int]]) -> int:
        # Sort by lastDay (deadline) ascending.
        # 按截止日期（lastDay）升序排序。
        # If deadlines are same, duration doesn't strictly matter for correctness due to the heap logic,
        # but logically we process earlier deadlines first.
        courses.sort(key=lambda x: x[1])
        
        # Max-heap to store durations of taken courses.
        # Python's heapq is a min-heap, so we store negative values to simulate max-heap.
        # 最大堆積，用於存儲已修課程的持續時間。
        # Python 的 heapq 是最小堆積，所以我們存儲負值來模擬最大堆積。
        max_heap = []
        
        # Current total time consumed.
        # 當前消耗的總時間。
        total_time = 0
        
        for duration, last_day in courses:
            if total_time + duration <= last_day:
                # If we can fit the course, take it.
                # 如果能塞進這門課，就修它。
                total_time += duration
                heapq.heappush(max_heap, -duration)
            elif max_heap and -max_heap[0] > duration:
                # If we can't fit it, but this course is shorter than the longest course we took...
                # 如果塞不進去，但这門課比我們修過的最長課程還短...
                
                # "Regret": Remove the longest course and add the current shorter one.
                # 「反悔」：移除最長的課程並加入當前較短的課程。
                longest_duration = -heapq.heappop(max_heap)
                total_time -= longest_duration
                total_time += duration
                heapq.heappush(max_heap, -duration)
                
                # Note: The count of courses didn't change, but total_time decreased.
                # 注意：課程數量沒有改變，但 total_time 減少了。
        
        return len(max_heap)

# Time Complexity: O(N log N) due to sorting and heap operations.
# Space Complexity: O(N) for the heap.
# 時間複雜度：O(N log N)，源於排序和堆積操作。
# 空間複雜度：O(N)，用於堆積。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation | Example |
| :--- | :--- | :--- |
| **Greedy vs. DP** | Greedy makes a final choice at each step; DP considers all choices and propagates the best. <br> Greedy 每一步做最終決定；DP 考慮所有選擇並傳遞最佳解。 | **0/1 Knapsack (DP)** vs. **Fractional Knapsack (Greedy)**. |
| **Local vs. Global** | A common mistake is proving local optimality but failing to prove it leads to global optimality. <br> 常見錯誤是證明了局部最佳，但未能證明它能導向全局最佳。 | **Coin Change**: Greedy works for US coins (1, 5, 10, 25) but fails for system like (1, 3, 4). |
| **Wrong Sorting Key** | Sorting by the wrong attribute is the most common bug. <br> 按錯誤的屬性排序是最常見的 Bug。 | Interval Scheduling: Sort by **end time**, not start time or duration. |

---

## 6. Interview Strategy (面試實戰建議)

### 1. The "Exchange Argument" (交換論證法 - Use this to impress)
When the interviewer asks "Are you sure Greedy works?", don't just say "It feels right."
當面試官問「你確定貪婪法行得通嗎？」時，不要只說「感覺是對的」。

**Say this:**
"Let's assume there is an optimal solution $O$ that differs from my greedy solution $G$. If I can show that I can replace an element in $O$ with an element from $G$ without worsening the result, then $G$ must also be optimal."
「假設有一個最佳解 $O$ 與我的貪婪解 $G$ 不同。如果我能證明可以用 $G$ 中的元素替換 $O$ 中的元素而不使結果變差，那麼 $G$ 必然也是最佳的。」

### 2. Whiteboard Strategy (白板策略)
1.  **Generate Examples:** Write down a small case where the "obvious" greedy choice fails. This shows seniority.
    **生成範例：** 寫下一個「顯而易見」的貪婪選擇會失敗的小案例。這顯示了資深程度。
2.  **Define the Greedy Choice:** Explicitly state: "I will sort by X and pick Y."
    **定義貪婪選擇：** 明確陳述：「我將按 X 排序並選擇 Y。」
3.  **Trace:** Walk through the example with your logic.
    **追蹤：** 用你的邏輯演練一遍範例。

### 3. Common Follow-ups
*   "What if the input is a stream?" (Hint: Keep a Heap).
    「如果輸入是串流怎麼辦？」（提示：維護一個 Heap）。
*   "What if we can do tasks in parallel?" (Hint: Multiple Heaps or Sweep Line).
    「如果我們可以並行處理任務怎麼辦？」（提示：多個 Heap 或掃描線）。

---

## 7. Practice Problems (練習題)

### Easy: Assign Cookies (LeetCode 455)
*   **Hint:** Sort both children (greed factor) and cookies (size). Match smallest greed with smallest valid cookie.
*   **提示：** 對孩子（貪婪因子）和餅乾（大小）進行排序。將最小的貪婪因子與最小的有效餅乾匹配。

### Medium: Task Scheduler (LeetCode 621)
*   **Hint:** Focus on the most frequent task. It defines the structure (skeleton) of the schedule. Fill gaps with other tasks. Math/Greedy hybrid.
*   **提示：** 關注頻率最高的任務。它定義了調度的結構（骨架）。用其他任務填充空隙。這是數學與貪婪的混合題。

### Hard: Minimum Number of Refueling Stops (LeetCode 871)
*   **Hint:** Drive as far as you can. When you run out of gas, "retroactively" stop at the gas station with the *most* fuel that you passed along the way. (Requires Max-Heap for "Regret").
*   **提示：** 盡可能開得遠。當油用完時，「事後諸葛」地決定在沿途經過的油量 *最大* 的加油站加油。（需要 Max-Heap 來實現「反悔」）。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Sorting:** Did I sort the input? If so, by what key? (Start time, End time, Size, Ratio?)
    **排序：** 我是否對輸入進行了排序？如果是，按什麼鍵？（開始時間、結束時間、大小、比率？）
*   [ ] **Constraints:** Is $N$ up to $10^5$? If so, $O(N^2)$ is too slow. Aim for $O(N \log N)$.
    **限制：** $N$ 是否高達 $10^5$？如果是，$O(N^2)$ 太慢。目標是 $O(N \log N)$。
*   [ ] **Counter-example:** Can I construct a case where taking the largest/smallest item now hurts me later?
    **反例：** 我能否構建一個案例，現在拿最大/最小的項目會害了我？
*   [ ] **Data Structure:** Do I need a Heap to efficiently find the min/max of "seen" elements?
    **資料結構：** 我是否需要 Heap 來高效查找「已見」元素的最小/最大值？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Cashier" (收銀員)
Making change with currency (1, 5, 10, 20). You always grab the largest bill that fits. This is standard Greedy.
用貨幣（1, 5, 10, 20）找零。你總是拿最大的合適鈔票。這是標準的貪婪。

### The "Time Traveler" (時間旅行者 - Regret Strategy)
Imagine you are walking through a timeline. You pick up gold. Suddenly you see a diamond but your bag is full. You use a time machine (Heap) to swap the heaviest rock you picked up earlier for this diamond.
想像你在時間線上行走。你撿起金子。突然你看到一顆鑽石，但你的包滿了。你使用時光機（Heap）將你之前撿起的最重的石頭換成這顆鑽石。