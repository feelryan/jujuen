Here is the comprehensive guide for **Greedy Algorithms**, tailored for a Senior Software Engineer targeting Big Tech roles.
這是一份針對資深軟體工程師目標 Big Tech 職位的 **貪婪演算法（Greedy Algorithms）** 完整指南。

---

# Advanced Greedy Algorithms Interview Guide
# 進階貪婪演算法面試指南

## 1. Learning Goals (學習目標)

*   **Distinguish Greedy from Dynamic Programming:** Understand when local optimality guarantees global optimality versus when exhaustive search (DP) is required.
    **區分貪婪與動態規劃：** 理解何時局部最佳解保證全域最佳解，以及何時需要窮舉搜尋（DP）。
*   **Master the "Exchange Argument" Proof:** Learn to justify your greedy choice by proving that swapping a greedy choice with a non-greedy one yields a suboptimal or equal result.
    **掌握「交換論證」證明：** 學習如何透過證明「將貪婪選擇替換為非貪婪選擇會導致次佳或相等的結果」來證成你的貪婪策略。
*   **Handle "Regret" Scenarios:** Implement patterns where past decisions are modified based on new information (often using Priority Queues).
    **處理「反悔」場景：** 實作基於新資訊修改過去決策的模式（通常使用優先佇列）。
*   **Optimize Complexity:** Achieve $O(N \log N)$ or $O(N)$ solutions where DP would be $O(N^2)$.
    **優化複雜度：** 在 DP 需要 $O(N^2)$ 的情況下，實現 $O(N \log N)$ 或 $O(N)$ 的解法。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Greedy algorithm builds up a solution piece by piece, always choosing the next piece that offers the most immediate benefit.
貪婪演算法逐步建構解法，總是選擇當下能提供最大即時利益的下一步。

### The Intuition (直覺)
It works only if the problem has the **Greedy Choice Property** (a global optimum can be arrived at by selecting a local optimum) and **Optimal Substructure**.
只有當問題具備 **貪婪選擇屬性**（透過選擇局部最佳解可達成全域最佳解）與 **最佳子結構** 時，此法才有效。

### Complexity (複雜度)
*   **Time:** Often dominated by sorting ($O(N \log N)$) or heap operations ($O(N \log K)$).
    **時間：** 通常由排序（$O(N \log N)$）或堆積操作（$O(N \log K)$）主導。
*   **Space:** Usually $O(1)$ or $O(N)$ for auxiliary storage.
    **空間：** 通常為 $O(1)$ 或 $O(N)$ 的輔助空間。

### When to Use (適用場景)
*   Interval Scheduling / Partitioning. (區間調度/分割)
*   Minimum Spanning Trees (Prim/Kruskal). (最小生成樹)
*   Huffman Coding. (霍夫曼編碼)
*   Problems asking for "Maximum/Minimum" where choices are independent or strictly constrained by a resource. (詢問「最大/最小」且選擇相互獨立或受限於單一資源的問題。)

### When NOT to Use (不適用場景)
*   When a choice depends on future consequences that cannot be predicted locally (e.g., 0/1 Knapsack).
    **當選擇依賴於無法局部預測的未來後果時（例如：0/1 背包問題）。**

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Sorting + Linear Scan (排序 + 線性掃描):**
    *   Sort intervals by end time or start time to find non-overlapping sets.
    *   依據結束時間或開始時間排序區間，以找出不重疊的集合。
2.  **Priority Queue / Min-Heap (優先佇列 / 最小堆積):**
    *   Keep track of the "best" candidates seen so far to enable a "regret" mechanism.
    *   追蹤目前為止見過的「最佳」候選者，以啟用「反悔」機制。
3.  **Two Pointers / Greedy on Arrays (雙指針 / 陣列貪婪):**
    *   Assigning resources (e.g., cookies to children) by matching smallest requirements first.
    *   透過優先匹配最小需求來分配資源（例如：分餅乾給小孩）。
4.  **Monotonic Stack (單調堆疊):**
    *   Removing elements to create the smallest/largest number (preserving relative order).
    *   移除元素以建立最小/最大數（保留相對順序）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule III (Hard)
**LeetCode 630**

### Problem Statement (問題重述)
There are `n` different online courses numbered from `1` to `n`. You are given an array `courses` where `courses[i] = [duration_i, lastDay_i]` indicate that the `i-th` course should be taken continuously for `duration_i` days and must be finished before or on `lastDay_i`.
有 `n` 門不同的線上課程，編號從 `1` 到 `n`。給定一個陣列 `courses`，其中 `courses[i] = [duration_i, lastDay_i]` 表示第 `i` 門課必須連續上 `duration_i` 天，且必須在 `lastDay_i` 之前或當天完成。

You will start on the 1st day. Return the *maximum number of courses* that you can take.
你將從第 1 天開始。請回傳你所能修習的 **最大課程數量**。

### Approach & Evolution (思路演進)

#### 1. Brute Force (暴力法)
Try every permutation of courses. Check if valid.
嘗試課程的所有排列組合。檢查是否合法。
*   **Complexity:** $O(N!)$. Impossible for $N > 20$.
    **複雜度：** $O(N!)$。當 $N > 20$ 時不可行。

#### 2. Greedy Attempt 1 (Sort by Duration) (貪婪嘗試 1：依時長排序)
Intuition: Take the shortest courses first to fit more in.
直覺：先修最短的課程，以便塞入更多課。
*   **Flaw:** A short course might have a very late deadline, while a slightly longer course has an immediate deadline. Taking the short one first might make us miss the urgent one.
    **缺陷：** 短課程可能有很晚的截止日，而稍長的課程可能有迫切的截止日。先修短課可能導致錯過急迫的課程。

#### 3. Greedy Attempt 2 (Sort by Deadline) (貪婪嘗試 2：依截止日排序)
Intuition: Process courses that end sooner first.
直覺：優先處理較早結束的課程。
*   **Issue:** If we blindly take a course just because it ends soon, its long duration might block us from taking 3 shorter courses later.
    **問題：** 如果我們僅因某課程較早結束就盲目修習，其過長的時長可能會阻礙我們後續修習 3 門較短的課程。

#### 4. Optimal Strategy: Sort by Deadline + Priority Queue (Regret) (最佳策略：依截止日排序 + 優先佇列反悔機制)
*   **Sort:** By `lastDay` ascending. We must satisfy earlier deadlines first.
    **排序：** 依 `lastDay` 遞增排序。我們必須先滿足較早的截止期限。
*   **Iterate:** Maintain a `current_time`.
    **迭代：** 維護一個 `current_time`。
*   **Decision:**
    1.  If we can fit the current course (`current_time + duration <= lastDay`), take it. Push duration to Max-Heap.
        若能塞入當前課程（`current_time + duration <= lastDay`），則修習之。將時長推入最大堆積。
    2.  If we *cannot* fit it, check if the current course is *shorter* than the longest course we've already taken (top of Max-Heap).
        若 **無法** 塞入，檢查當前課程是否比我們已修習過的最長課程（最大堆積頂端）**更短**。
    3.  **Regret (Swap):** If yes, remove the long course, add the current shorter one. This reduces `current_time`, buying us more space for future courses without changing the count (count stays same, time optimized).
        **反悔（交換）：** 若是，移除該長課程，加入當前較短的課程。這會減少 `current_time`，為未來課程爭取更多空間，且不改變課程數量（數量不變，時間優化）。

### C++ Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <queue>
#include <iostream>

using namespace std;

class Solution {
public:
    int scheduleCourse(vector<vector<int>>& courses) {
        // Sort by lastDay ascending.
        // If lastDays are equal, the relative order doesn't strictly matter for correctness,
        // but sorting by duration could be a tie-breaker (not strictly needed).
        // 依據 lastDay 遞增排序。
        // 若 lastDay 相同，相對順序對正確性無嚴格影響，但可依時長作為次要排序（非必須）。
        sort(courses.begin(), courses.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[1] < b[1];
        });

        // Max-Heap to store durations of taken courses.
        // Allows us to find and remove the longest course efficiently (Regret strategy).
        // 最大堆積，用於儲存已修習課程的時長。
        // 允許我們高效地找到並移除最長的課程（反悔策略）。
        priority_queue<int> pq;
        
        int currentTime = 0;

        for (const auto& course : courses) {
            int duration = course[0];
            int lastDay = course[1];

            // If adding this course doesn't exceed its deadline, take it.
            // 若加入此課程不超過其截止日，則修習之。
            if (currentTime + duration <= lastDay) {
                pq.push(duration);
                currentTime += duration;
            } 
            // If we can't fit it, but this course is shorter than the longest one we've taken...
            // 若無法塞入，但此課程比我們已修習過的最長課程還短...
            else if (!pq.empty() && pq.top() > duration) {
                // Swap logic: Remove the longest course, take the current shorter one.
                // Total courses count remains same, but currentTime decreases.
                // 交換邏輯：移除最長課程，修習當前較短者。
                // 總課程數不變，但 currentTime 減少。
                currentTime -= pq.top();
                pq.pop();
                
                currentTime += duration;
                pq.push(duration);
            }
        }

        return pq.size();
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N \log N)$ for sorting + $O(N \log N)$ for heap operations (each element pushed/popped once). Total: $O(N \log N)$.
    **時間：** 排序 $O(N \log N)$ + 堆積操作 $O(N \log N)$（每個元素推入/彈出一次）。總計：$O(N \log N)$。
*   **Space:** $O(N)$ for the priority queue.
    **空間：** 優先佇列需 $O(N)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Greedy (貪婪) | Dynamic Programming (動態規劃) |
| :--- | :--- | :--- |
| **Decision (決策)** | Makes the best local choice immediately. Never looks back (unless using specific regret structures). <br> 立即做出最佳局部選擇。絕不回頭（除非使用特定反悔結構）。 | Considers all possible choices (or a subset via recursion) to find the global optimum. <br> 考慮所有可能的選擇（或透過遞迴考慮子集）以找出全域最佳解。 |
| **Backtracking (回溯)** | No (usually). <br> 否（通常）。 | Yes (implicitly via overlapping subproblems). <br> 是（隱含於重疊子問題中）。 |
| **Example (範例)** | **Fractional Knapsack:** Take the item with highest value/weight ratio. <br> **分數背包：** 拿取價值/重量比最高的物品。 | **0/1 Knapsack:** Must either take or leave whole item. Greedy fails here. <br> **0/1 背包：** 必須拿取或放棄整個物品。貪婪法在此會失敗。 |

**Trap:** Sorting by the wrong attribute.
**陷阱：** 依據錯誤的屬性排序。
*   *Example:* In Interval Scheduling, sorting by `start_time` is a common mistake. You must sort by `end_time` to maximize the room left for future intervals.
    *範例：* 在區間調度中，依 `start_time` 排序是常見錯誤。必須依 `end_time` 排序，以最大化留給未來區間的空間。

---

## 6. Interview Strategy (面試實戰建議)

### 1. The "Hypothesis" Phase (假設階段)
*   **Say:** "This looks like an optimization problem. Since the constraints are tight ($N=10^5$), $O(N^2)$ DP might TLE. I'll explore if a Greedy approach with Sorting or Heap works."
    **口述：** 「這看起來像個最佳化問題。由於限制嚴格（$N=10^5$），$O(N^2)$ 的 DP 可能會超時。我將探討是否可用排序或堆積的貪婪解法。」

### 2. The "Counter-Example" Check (反例檢查)
*   Before coding, try to break your greedy logic.
    在寫程式前，試著推翻你的貪婪邏輯。
*   **Say:** "If I sort by X, can I construct a case where picking the top X is bad? Yes, if..."
    **口述：** 「如果我依 X 排序，我能建構一個反例證明選 X 是錯的嗎？是的，如果...」

### 3. The "Exchange Argument" (交換論證)
*   If the interviewer asks "Are you sure?", use this logic: "Suppose there exists an optimal solution $O$ that differs from my greedy choice $G$. If I can replace the choice in $O$ with $G$ without worsening the result, then my greedy strategy is valid."
    若面試官問「你確定嗎？」，使用此邏輯：「假設存在一個最佳解 $O$ 與我的貪婪選擇 $G$ 不同。如果我能將 $O$ 中的選擇替換為 $G$ 且不使結果變差，則我的貪婪策略有效。」

---

## 7. Practice Problems (練習題)

### Easy: Assign Cookies (LC 455)
*   **Hint:** Sort both children (greed factor) and cookies (size). Match smallest cookie that satisfies the smallest greed factor.
    **提示：** 排序小孩（貪婪因子）與餅乾（尺寸）。將最小的餅乾匹配給能滿足的最小貪婪因子。
*   **Core:** Two Pointers.
    **核心：** 雙指針。

### Medium: Gas Station (LC 134)
*   **Hint:** If you can't reach station B from A, you can't reach B from any station between A and B. Reset start point to B+1.
    **提示：** 若你無法從 A 到達 B，則你也無法從 A 與 B 之間的任何站到達 B。將起點重置為 B+1。
*   **Core:** One pass greedy accumulation.
    **核心：** 單遍貪婪累加。

### Advanced: Minimum Number of Taps to Open to Water a Garden (LC 1326)
*   **Hint:** Convert taps into intervals `[i-ranges[i], i+ranges[i]]`. This becomes "Minimum Interval Coverage" (Jump Game II variation). At each step, jump to the interval that extends the furthest.
    **提示：** 將水龍頭轉換為區間 `[i-ranges[i], i+ranges[i]]`。這變成了「最小區間覆蓋」（跳躍遊戲 II 變體）。每一步跳到能延伸最遠的區間。
*   **Core:** Interval Greedy (Farthest Reach).
    **核心：** 區間貪婪（最遠可達距離）。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Sorting:** Did I sort? By start, end, or duration? (Usually required).
    **排序：** 我排序了嗎？依開始、結束或時長？（通常需要）。
*   [ ] **Local Optimality:** Does taking the "best" now restrict me from a MUCH better option later? (If yes, try DP or Regret-Greedy).
    **局部最佳性：** 現在拿「最好」的會限制我之後拿到「好很多」的選項嗎？（若是，嘗試 DP 或反悔式貪婪）。
*   [ ] **Complexity:** Is it $O(N \log N)$? If $N \le 2000$, maybe DP is safer. If $N \ge 10^5$, Greedy is likely.
    **複雜度：** 是 $O(N \log N)$ 嗎？若 $N \le 2000$，也許 DP 較安全。若 $N \ge 10^5$，很可能是貪婪。
*   [ ] **Edge Cases:** $N=0$, $N=1$, all intervals overlapping, no intervals overlapping.
    **邊界情況：** $N=0$，$N=1$，所有區間重疊，無區間重疊。

---

## 9. Memory Anchors (記憶錨點)

### The "Cashier" (收銀員)
*   **Concept:** Making change with standard coins (1, 5, 10, 25).
    **觀念：** 用標準硬幣找零（1, 5, 10, 25）。
*   **Visual:** You always grab the largest coin possible first. This is canonical Greedy.
    **圖像：** 你總是先拿最大的硬幣。這是標準的貪婪法。

### The "Mountaineer" (登山客)
*   **Concept:** Finding the highest peak.
    **觀念：** 尋找最高峰。
*   **Visual:** In Greedy, you only look at the step immediately in front of you that goes up. You might get stuck on a false peak (local optimum).
    **圖像：** 在貪婪法中，你只看眼前向上的一步。你可能會被困在假高峰（局部最佳解）。

### The "Time Manager" (時間管理者)
*   **Concept:** Interval Scheduling.
    **觀念：** 區間調度。
*   **Visual:** To finish the most tasks, always pick the one that **finishes earliest**, leaving your calendar open for more.
    **圖像：** 為了完成最多任務，總是選擇 **最早結束** 的那個，讓你的行事曆空出來給更多任務。