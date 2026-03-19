Here is the comprehensive interview preparation guide for **Greedy Algorithms** at the **Advanced** level, tailored for Senior Software Engineers using **Java**.

***

# Advanced Greedy Algorithms Interview Guide
# 進階貪婪演算法面試指南

## 1. Learning Goals（學習目標）

*   **Distinguish Greedy from Dynamic Programming:** Understand when local optimality guarantees global optimality (Greedy Choice Property) versus when you need to explore all sub-problems (DP).
    **區分貪婪與動態規劃：** 理解何時局部最佳解保證全域最佳解（貪婪選擇屬性），以及何時需要探索所有子問題（DP）。
*   **Master the "Exchange Argument" Proof:** Learn to formally or intuitively prove correctness by showing that swapping a greedy choice with a non-greedy optimal choice does not worsen the solution.
    **掌握「交換論證」證明：** 學習如何透過「將貪婪選擇與非貪婪的最佳選擇交換，且結果不會變差」來形式化或直觀地證明正確性。
*   **Handle "Regret" Scenarios with Priority Queues:** Implement advanced patterns where you make a greedy choice but maintain a data structure to "undo" or "swap" that choice later if a better option appears.
    **利用優先佇列處理「後悔」場景：** 實作進階模式，先做出貪婪選擇，但維護一個資料結構以便在出現更好選項時「撤銷」或「交換」該選擇。
*   **Optimize Complexity:** Move beyond simple $O(N \log N)$ sorting solutions to $O(N)$ using buckets or linear scans where applicable.
    **優化複雜度：** 超越單純的 $O(N \log N)$ 排序解法，在適用情況下利用桶排序或線性掃描達到 $O(N)$。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
Greedy algorithms build up a solution piece by piece, always choosing the next piece that offers the most immediate and obvious benefit.
貪婪演算法透過一步步構建解法，總是選擇當下能提供最直接、最明顯利益的下一步。

### Intuition & Theory（直覺與理論）
For a Greedy algorithm to work, the problem must exhibit:
要讓貪婪演算法奏效，問題必須具備：
1.  **Greedy Choice Property:** A global optimum can be arrived at by selecting a local optimum.
    **貪婪選擇屬性：** 透過選擇局部最佳解，可以達到全域最佳解。
2.  **Optimal Substructure:** An optimal solution to the problem contains an optimal solution to sub-problems.
    **最佳子結構：** 問題的最佳解包含其子問題的最佳解。

### Complexity（複雜度）
*   **Time:** Usually dominated by sorting ($O(N \log N)$) or Heap operations ($O(N \log K)$). Occasionally linear $O(N)$.
    **時間：** 通常由排序 ($O(N \log N)$) 或堆積操作 ($O(N \log K)$) 主導。偶爾為線性 $O(N)$。
*   **Space:** Often $O(1)$ or $O(N)$ depending on whether output storage is counted.
    **空間：** 通常為 $O(1)$ 或 $O(N)$，取決於是否計算輸出儲存空間。

### When to Use vs. Avoid（適用與不適用場景）
*   **Use when:** You can prove (via contradiction or exchange) that taking the "best" current step never closes the door on the global optimal solution. (e.g., MST, Dijkstra, Interval Scheduling).
    **適用時機：** 你能證明（透過矛盾證法或交換論證）採取當前「最好」的步驟永遠不會阻斷通往全域最佳解的路。（例如：最小生成樹、Dijkstra、區間排程）。
*   **Avoid when:** Future consequences depend heavily on current choices in a non-linear way (e.g., 0/1 Knapsack, standard Shortest Path with negative edges).
    **避免時機：** 未來的後果以非線性方式高度依賴於當前的選擇（例如：0/1 背包問題、帶負邊的標準最短路徑）。

---

## 3. Typical Patterns（典型題型 / 模式）

### 1. Interval Scheduling / Sweeping (區間排程 / 掃描線)
Sorting intervals by **end time** (to maximize count) or **start time** (to merge intervals).
依據 **結束時間**（最大化數量）或 **開始時間**（合併區間）對區間進行排序。

### 2. Priority Queue with "Regret" (帶有「後悔」機制的優先佇列)
Iterate through items, greedily accepting them. If constraints are violated, remove the "worst" item previously accepted (using a Heap) to make room for the current one.
遍歷項目並貪婪地接受它們。如果違反限制，則移除先前接受過的「最差」項目（使用堆積），為當前項目騰出空間。

### 3. Huffman Coding / Merge Patterns (霍夫曼編碼 / 合併模式)
Repeatedly merging the two smallest/largest elements to minimize/maximize cost.
重複合併兩個最小/最大的元素以最小化/最大化成本。

### 4. String/Array Canonical Construction (字串/陣列正規建構)
Building the lexicographically largest/smallest result by using a Monotonic Stack or simple greedy checks (e.g., "Remove K Digits").
透過單調堆疊或簡單的貪婪檢查來建構字典序最大/最小的結果（例如：「移除 K 個數字」）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule III (Hard)
**LeetCode 630**

#### Problem Statement（問題重述）
There are `n` different online courses numbered from `1` to `n`. You are given an array `courses` where `courses[i] = [duration_i, lastDay_i]` indicate that the `i-th` course should be taken continuously for `duration_i` days and must be finished before or on `lastDay_i`.
有 `n` 門不同的線上課程，編號從 `1` 到 `n`。給定一個陣列 `courses`，其中 `courses[i] = [duration_i, lastDay_i]` 表示第 `i` 門課必須連續上 `duration_i` 天，且必須在 `lastDay_i` 或之前完成。

You will start on the `1st` day. You cannot take two or more courses simultaneously. Return the *maximum number of courses* that you can take.
你從第 `1` 天開始。不能同時修兩門或以上的課。回傳你可以修習的 *最大課程數量*。

#### Thought Process（思路）

1.  **Brute Force (DFS):** Try every permutation of courses. Check if valid.
    **暴力法 (DFS)：** 嘗試課程的所有排列組合。檢查是否合法。
    *   Complexity: $O(N!)$. Impossible for $N=10^4$.
    *   複雜度：$O(N!)$。對於 $N=10^4$ 不可行。

2.  **Greedy Intuition (Sorting):**
    *   Should we sort by duration? No, a short course might have a very early deadline.
        我們應該按持續時間排序嗎？不，短課程可能有非常早的截止日期。
    *   Should we sort by deadline? Yes. Processing courses with earlier deadlines first gives us more flexibility for later deadlines.
        我們應該按截止日期排序嗎？是的。先處理截止日期較早的課程，能為較晚截止的課程保留更多彈性。

3.  **The "Regret" Strategy (Optimization):**
    *   Iterate through courses sorted by deadline.
        遍歷按截止日期排序的課程。
    *   Maintain a `currentTotalTime`. If we can fit the current course, take it.
        維護一個 `currentTotalTime`。如果能塞入當前課程，就接受它。
    *   **Crucial Step:** If we *cannot* fit the current course, check if the current course is shorter than the *longest* course we have already accepted. If so, swap them!
        **關鍵步驟：** 如果 *無法* 塞入當前課程，檢查當前課程是否比我們已經接受的 *最長* 課程還短。如果是，交換它們！
    *   *Why?* By removing the longest course and adding a shorter one, the count of courses stays the same, but `currentTotalTime` decreases, giving us more room for future courses.
        *為什麼？* 移除最長的課程並加入較短的，課程數量不變，但 `currentTotalTime` 減少了，為未來的課程騰出更多空間。

4.  **Data Structure:** Max-Heap to keep track of durations of taken courses.
    **資料結構：** 使用最大堆積（Max-Heap）來追蹤已修習課程的持續時間。

#### Java Solution（Java 參考解）

```java
import java.util.Arrays;
import java.util.PriorityQueue;

class Solution {
    public int scheduleCourse(int[][] courses) {
        // Sort by lastDay (deadline) ascending.
        // If deadlines are same, order doesn't strictly matter for correctness,
        // but stable sort or secondary sort by duration is fine.
        // 按 lastDay（截止日期）升序排序。
        // 如果截止日期相同，順序對正確性沒有嚴格影響，但穩定排序或按持續時間次級排序皆可。
        Arrays.sort(courses, (a, b) -> a[1] - b[1]);

        // Max-Heap to store durations of taken courses.
        // Allows us to efficiently find and remove the longest course.
        // 最大堆積，用於儲存已修習課程的持續時間。
        // 讓我們能高效地找到並移除最長的課程。
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);

        int time = 0; // Current time elapsed / 當前經過的時間

        for (int[] course : courses) {
            int duration = course[0];
            int lastDay = course[1];

            // Greedy check: If adding this course doesn't exceed its deadline
            // 貪婪檢查：如果加入這門課不會超過其截止日期
            if (time + duration <= lastDay) {
                maxHeap.offer(duration);
                time += duration;
            } 
            // Regret mechanism: If we can't fit it, but this course is shorter 
            // than the longest course we've already taken, swap them.
            // 後悔機制：如果塞不下，但這門課比我們已經修過的最長課程還短，則交換。
            else if (!maxHeap.isEmpty() && maxHeap.peek() > duration) {
                // Remove the longest duration to save time
                // 移除最長的持續時間以節省時間
                time -= maxHeap.poll();
                time += duration;
                maxHeap.offer(duration);
            }
        }

        return maxHeap.size();
    }
}
```

#### Complexity Analysis（複雜度分析）
*   **Time:** $O(N \log N)$ for sorting + $O(N \log N)$ for Heap operations (worst case inserting/removing every element). Total: $O(N \log N)$.
    **時間：** 排序 $O(N \log N)$ + 堆積操作 $O(N \log N)$（最差情況下插入/移除每個元素）。總計：$O(N \log N)$。
*   **Space:** $O(N)$ for the Priority Queue.
    **空間：** 優先佇列需 $O(N)$。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision Making** | Makes the best local choice at each step and **never looks back**. <br> 在每一步做出最佳局部選擇，且**絕不回頭**。 | Considers all possible choices and their consequences (often via recursion/memoization). <br> 考慮所有可能的選擇及其後果（通常透過遞迴/記憶化）。 |
| **Correctness** | Harder to prove (requires Exchange Argument). <br> 較難證明（需要交換論證）。 | Correctness usually follows from the recurrence relation. <br> 正確性通常源自遞迴關係式。 |
| **Typical Trap** | Sorting by the wrong parameter (e.g., start time vs end time). <br> 按錯誤的參數排序（例如：開始時間 vs 結束時間）。 | Over-optimizing space before solving the recurrence. <br> 在解決遞迴關係前過度優化空間。 |
| **Backtracking?** | No (unless using "Regret" heap pattern, which is still linear-ish). <br> 否（除非使用「後悔」堆積模式，該模式仍類線性）。 | Yes (conceptually explores multiple branches). <br> 是（概念上探索多個分支）。 |

**Key Trap:** Assuming "Greedy works" without checking edge cases.
**關鍵陷阱：** 在未檢查邊界情況下假設「貪婪法有效」。
*   *Example:* Coin change problem. Greedy works for US Dollars (1, 5, 10, 25), but fails for a system like {1, 3, 4} aiming for 6 (Greedy: 4+1+1=3 coins; Optimal: 3+3=2 coins).
*   *範例：* 找零問題。貪婪法適用於美金（1, 5, 10, 25），但在像 {1, 3, 4} 這樣的系統中要湊 6 元時會失敗（貪婪：4+1+1=3 枚；最佳：3+3=2 枚）。

---

## 6. Interview Strategy（面試實戰建議）

### 1. Verbal Framework (口條框架)
*   **Start with Brute Force:** "Ideally, we would check all combinations, but that's exponential."
    **從暴力法開始：** 「理想情況下，我們會檢查所有組合，但那是指數級的。」
*   **Propose Greedy Hypothesis:** "I suspect we can solve this greedily by sorting by [Criteria]. My intuition is that processing [X] first leaves the most room for [Y]."
    **提出貪婪假設：** 「我懷疑我們可以透過按 [標準] 排序來貪婪地解決此問題。我的直覺是先處理 [X] 能為 [Y] 留出最多空間。」
*   **Mention the "Why":** "This looks like a variation of the Interval Scheduling problem."
    **提及「為什麼」：** 「這看起來像是區間排程問題的變體。」

### 2. Whiteboard Strategy (白板策略)
*   **Sort Explicitly:** Write `Arrays.sort(...)` early. It anchors your thought process.
    **明確排序：** 儘早寫下 `Arrays.sort(...)`。這能錨定你的思考過程。
*   **Trace an Edge Case:** Before saying "Done", manually trace a case where the greedy choice *might* seem wrong (e.g., a very long task with an early deadline) to show your logic holds.
    **追蹤邊界情況：** 在說「完成」之前，手動追蹤一個貪婪選擇 *可能* 看起來錯誤的案例（例如：一個截止日期很早但持續時間很長的任務），以證明你的邏輯成立。

### 3. Common Follow-ups (常見追問)
*   "What if the input is a stream?" (Hint: Keep the Heap, drop the Sort).
    「如果輸入是串流怎麼辦？」（提示：保留堆積，捨棄排序）。
*   "Can we parallelize this?" (Greedy is inherently sequential; usually hard to parallelize without partitioning).
    「我們可以平行化這個嗎？」（貪婪本質上是順序性的；若不進行分區通常很難平行化）。

---

## 7. Practice Problems（練習題）

### Level 1: Warm-up (Easy/Medium)
**Problem:** **Jump Game II (LC 45)**
**Hint:** Maintain the `farthest` index reachable. When you reach the end of the current jump range, update the range to `farthest` and increment jumps.
**提示：** 維護可到達的 `farthest`（最遠）索引。當到達當前跳躍範圍的末端時，將範圍更新為 `farthest` 並增加跳躍次數。

### Level 2: Intermediate (Medium)
**Problem:** **Gas Station (LC 134)**
**Hint:** If total gas < total cost, impossible. Otherwise, iterate. If `currentTank < 0`, the start point must be *after* the current station. Reset `currentTank`.
**提示：** 如果總油量 < 總消耗，則不可能。否則，遍歷。如果 `currentTank < 0`，起點必須在當前加油站 *之後*。重置 `currentTank`。

### Level 3: Advanced (Hard)
**Problem:** **IPO (LC 502)**
**Hint:** Use two Heaps. Sort projects by capital required. Push all affordable projects into a Max-Heap (based on profit). Pick the best profit, increase capital, and repeat.
**提示：** 使用兩個堆積。按所需資本對專案排序。將所有負擔得起的專案推入最大堆積（基於利潤）。選取最高利潤，增加資本，然後重複。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review (自我審查)
- [ ] **Sorting:** Did I sort? Is the sorting criteria (asc/desc, start/end) correct?
    **排序：** 我排序了嗎？排序標準（升/降、開始/結束）正確嗎？
- [ ] **Proof:** Can I construct a counter-example? If not, does the "Exchange Argument" hold?
    **證明：** 我能建構反例嗎？如果不能，「交換論證」成立嗎？
- [ ] **Data Structures:** Do I need a Heap to track history/regrets?
    **資料結構：** 我需要堆積來追蹤歷史/後悔嗎？

### Complexity Check (複雜度確認)
- [ ] If $N=10^5$, is my solution $O(N)$ or $O(N \log N)$? ($O(N^2)$ will TLE).
    如果 $N=10^5$，我的解法是 $O(N)$ 或 $O(N \log N)$ 嗎？（$O(N^2)$ 會超時）。

---

## 9. Memory Anchors（記憶錨點）

### The "Cashier" Analogy (收銀員類比)
Think of making change. You always grab the largest bill possible first ($20, then $10, then $5). This is the essence of Greedy: **Local Best = Global Best**.
想像找零錢。你總是先拿最大的鈔票（$20，然後 $10，然後 $5）。這就是貪婪的本質：**局部最佳 = 全域最佳**。

### The "Mountain Climber" (登山者)
A greedy climber always takes the steepest step up. In a "Convex" landscape (Greedy-compatible problem), they reach the highest peak. In a complex landscape (Non-Greedy), they get stuck on a small hill (Local Maxima).
貪婪的登山者總是邁出最陡峭的一步向上。在「凸」地形（適用貪婪的問題）中，他們會到達最高峰。在複雜地形（不適用貪婪）中，他們會被困在小山丘上（局部極大值）。