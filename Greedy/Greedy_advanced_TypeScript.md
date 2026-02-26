# Advanced Greedy Algorithms Interview Guide
# 進階貪婪演算法面試指南

## 1. Learning Objectives（學習目標）

*   **Master the "Exchange Argument" for Proofs:**
    Learn how to rigorously prove the correctness of a greedy strategy, distinguishing it from intuition-based guessing.
    **掌握「交換論證法」進行證明：** 學習如何嚴謹地證明貪婪策略的正確性，將其與憑直覺的猜測區分開來。

*   **Differentiate Greedy from Dynamic Programming:**
    Understand when local optimality guarantees global optimality versus when an exhaustive search (DP) is required.
    **區分貪婪與動態規劃：** 理解何時局部最佳解保證全域最佳解，以及何時需要窮舉搜尋（DP）。

*   **Handle "Regret" Scenarios with Priority Queues:**
    Solve advanced problems where early greedy choices might need to be revoked or swapped later (Greedy with Backtracking/Heap).
    **利用優先佇列處理「反悔」場景：** 解決那些早期的貪婪選擇可能需要在稍後被撤銷或交換的進階問題（帶有回溯/堆積的貪婪）。

*   **Optimize Complexity:**
    Achieve $O(N \log N)$ or $O(N)$ solutions for problems that naively look like $O(N^2)$ or exponential.
    **優化複雜度：** 針對那些直觀上看起來像 $O(N^2)$ 或指數級的問題，實現 $O(N \log N)$ 或 $O(N)$ 的解法。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Greedy algorithms make the locally optimal choice at each step with the hope of finding a global optimum.
貪婪演算法在每一步都做出局部最佳的選擇，並希望藉此找到全域最佳解。

For Senior Engineers, "hope" is not enough; we rely on two properties:
對於資深工程師來說，「希望」是不夠的；我們依賴兩個屬性：

1.  **Greedy Choice Property（貪婪選擇屬性）:**
    A global optimum can be arrived at by selecting a local optimum.
    可以通過選擇局部最佳解來達到全域最佳解。
2.  **Optimal Substructure（最佳子結構）:**
    An optimal solution to the problem contains an optimal solution to subproblems.
    問題的最佳解包含其子問題的最佳解。

### Complexity（複雜度）
*   **Time:** Usually dominated by sorting ($O(N \log N)$) or Heap operations ($O(N \log K)$). Occasionally $O(N)$ if the input is pre-sorted or using bucket concepts.
    **時間：** 通常由排序 ($O(N \log N)$) 或堆積操作 ($O(N \log K)$) 主導。如果輸入已排序或使用桶概念，偶爾為 $O(N)$。
*   **Space:** $O(1)$ (in-place) or $O(N)$ (to store the result or a heap).
    **空間：** $O(1)$（原地操作）或 $O(N)$（儲存結果或堆積）。

### When to Use vs. Avoid（適用與不適用場景）
*   **Use when:** You can prove that the first choice you make is part of *some* optimal solution (Exchange Argument).
    **適用時機：** 當你能證明你做出的第一個選擇屬於*某個*最佳解的一部分時（交換論證）。
*   **Avoid when:** Constraints interact in complex ways where a decision now limits future options non-linearly (e.g., 0/1 Knapsack Problem requires DP).
    **避免時機：** 當限制條件以複雜方式交互，目前的決策非線性地限制了未來的選項時（例如：0/1 背包問題需要 DP）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Interval Scheduling (Sorting + Iteration)
**區間排程（排序 + 迭代）**
*   **Pattern:** Sort by end time (usually) or start time. Iterate and select non-overlapping intervals.
    **模式：** 按結束時間（通常）或開始時間排序。迭代並選擇不重疊的區間。
*   **Key:** Determining *what* to sort by is the crux of the problem.
    **關鍵：** 決定依據*什麼*來排序是問題的核心。

### B. Greedy with Priority Queue ("Regret" Strategy)
**帶優先佇列的貪婪（「反悔」策略）**
*   **Pattern:** Make a greedy choice. If a constraint is violated later, remove the "worst" previous choice from the heap to accommodate the new, better option.
    **模式：** 做出貪婪選擇。如果稍後違反了限制，從堆積中移除先前「最差」的選擇，以容納新的、更好的選項。

### C. String/Array Construction (Monotonic Stack/Queue)
**字串/陣列建構（單調堆疊/佇列）**
*   **Pattern:** Construct the lexicographically largest/smallest result by keeping elements in a monotonic order and discarding elements that break the order if constraints allow.
    **模式：** 通過保持元素單調順序，並在限制允許的情況下丟棄破壞順序的元素，來建構字典序最大/最小的結果。

### D. Huffman Coding / Merge Patterns
**霍夫曼編碼 / 合併模式**
*   **Pattern:** Always merge the two smallest/largest elements to minimize/maximize cost.
    **模式：** 總是合併兩個最小/最大的元素以最小化/最大化成本。

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule III (Hard)
### 題目：課程表 III (Hard)

**Problem Statement:**
There are `n` different online courses numbered from `1` to `n`. You are given an array `courses` where `courses[i] = [duration_i, lastDay_i]`.
這裡有 `n` 門不同的線上課程，編號從 `1` 到 `n`。給定一個陣列 `courses`，其中 `courses[i] = [duration_i, lastDay_i]`。

You will start on the `1st` day. A course should be taken continuously for `duration_i` days and must be finished before or on `lastDay_i`. You can only take one course at a time.
你將從第 `1` 天開始。一門課程需要持續上 `duration_i` 天，且必須在 `lastDay_i` 之前或當天完成。你一次只能上一門課。

Return the *maximum number of courses* that you can take.
回傳你能修習的*最大課程數量*。

---

### Approach: From Brute Force to Greedy with Regret
### 思路：從暴力解到帶反悔機制的貪婪解

#### 1. Intuition (Sorting) / 直覺（排序）
Should we sort by duration? No, a short course might have a very early deadline.
我們應該按持續時間排序嗎？不，短課程可能有非常早的截止日期。
Should we sort by deadline? Yes, processing tasks with earlier deadlines first gives us more room for later tasks.
我們應該按截止日期排序嗎？是的，先處理截止日期較早的任務，能為後續任務留出更多空間。

#### 2. The Conflict / 衝突
What if we pick a course with an early deadline, but it takes a huge amount of time, preventing us from taking 3 shorter courses later?
如果我們選了一門截止日期早但耗時極長的課程，導致我們無法修習後面 3 門較短的課程怎麼辦？

*   **Standard Greedy:** Just take it if it fits. (Fails here).
    **標準貪婪：** 如果塞得進去就選。（在此會失敗）。
*   **Greedy with Regret:** Take it. If we later find we can't fit a new course, check if the new course is shorter than the *longest* course we've already accepted. If so, swap them!
    **帶反悔的貪婪：** 先選它。如果稍後發現塞不下新課程，檢查新課程是否比我們已經接受的*最長*課程更短。如果是，交換它們！

#### 3. Algorithm / 演算法
1.  Sort courses by `lastDay`.
    將課程按 `lastDay` 排序。
2.  Iterate through courses. Maintain a `currentTotalTime` and a Max-Heap of `durations` of taken courses.
    迭代課程。維護一個 `currentTotalTime` 和一個包含已修課程 `durations` 的最大堆積。
3.  If `currentTotalTime + duration <= lastDay`, take it (push to heap).
    如果 `currentTotalTime + duration <= lastDay`，修它（推入堆積）。
4.  Else, if `duration < max(heap)`, remove the max from heap, subtract its time, and add the current one.
    否則，如果 `duration < max(heap)`，從堆積移除最大值，減去其時間，並加入當前課程。
    *(Why? We save time but keep the count the same. This creates more space for future courses.)*
    *（為什麼？我們節省了時間但保持課程數量不變。這為未來的課程創造了更多空間。）*

---

### TypeScript Solution (Advanced)
### TypeScript 參考解（進階）

```typescript
/**
 * Max Heap implementation helper (Simplified for interview context)
 * 實作最大堆積輔助類別（為面試情境簡化）
 */
class MaxHeap {
    private data: number[] = [];

    push(val: number): void {
        this.data.push(val);
        this.bubbleUp(this.data.length - 1);
    }

    pop(): number | undefined {
        if (this.size() === 0) return undefined;
        const max = this.data[0];
        const last = this.data.pop()!;
        if (this.size() > 0) {
            this.data[0] = last;
            this.bubbleDown(0);
        }
        return max;
    }

    peek(): number | undefined {
        return this.data[0];
    }

    size(): number {
        return this.data.length;
    }

    private bubbleUp(index: number): void {
        while (index > 0) {
            const parentIndex = Math.floor((index - 1) / 2);
            if (this.data[index] <= this.data[parentIndex]) break;
            [this.data[index], this.data[parentIndex]] = [this.data[parentIndex], this.data[index]];
            index = parentIndex;
        }
    }

    private bubbleDown(index: number): void {
        const lastIndex = this.data.length - 1;
        while (true) {
            let swapIndex = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (left <= lastIndex && this.data[left] > this.data[swapIndex]) {
                swapIndex = left;
            }
            if (right <= lastIndex && this.data[right] > this.data[swapIndex]) {
                swapIndex = right;
            }
            if (swapIndex === index) break;
            [this.data[index], this.data[swapIndex]] = [this.data[swapIndex], this.data[index]];
            index = swapIndex;
        }
    }
}

function scheduleCourse(courses: number[][]): number {
    // 1. Sort by deadline (lastDay) ascending.
    // 1. 依照截止日期 (lastDay) 升序排序。
    // If deadlines are same, sorting by duration doesn't strictly matter for correctness due to the swap logic,
    // but usually stable sort is preferred.
    // 如果截止日期相同，由於交換邏輯的存在，按持續時間排序對正確性沒有嚴格影響，但通常偏好穩定排序。
    courses.sort((a, b) => a[1] - b[1]);

    const maxHeap = new MaxHeap();
    let totalTime = 0;

    for (const [duration, lastDay] of courses) {
        // Optimization: If current course fits, just take it.
        // 優化：如果當前課程塞得進去，就直接修。
        if (totalTime + duration <= lastDay) {
            maxHeap.push(duration);
            totalTime += duration;
        } else {
            // Greedy with Regret:
            // If we can't fit it, check if this course is shorter than the longest course we've taken.
            // 帶反悔的貪婪：
            // 如果塞不下，檢查這門課是否比我們已修的最長課程更短。
            const longestDuration = maxHeap.peek();
            
            if (longestDuration !== undefined && longestDuration > duration) {
                // Swap logic: Remove the longest, add the current shorter one.
                // 交換邏輯：移除最長的，加入當前較短的。
                // We gain (longest - current) extra time buffer for future courses.
                // 我們為未來的課程爭取到了 (longest - current) 的額外時間緩衝。
                totalTime -= longestDuration;
                maxHeap.pop();
                
                totalTime += duration;
                maxHeap.push(duration);
            }
        }
    }

    return maxHeap.size();
}
```

### Complexity Analysis
*   **Time:** $O(N \log N)$ for sorting + $O(N \log N)$ for heap operations (each element pushed/popped once). Total: $O(N \log N)$.
    **時間：** 排序需 $O(N \log N)$ + 堆積操作需 $O(N \log N)$（每個元素推入/彈出一次）。總計：$O(N \log N)$。
*   **Space:** $O(N)$ to store the priority queue.
    **空間：** $O(N)$ 用於儲存優先佇列。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Greedy | Dynamic Programming (DP) |
| :--- | :--- | :--- |
| **Decision Making** | Makes the best local choice immediately and never reconsiders (unless using "Regret" heap). <br> 立即做出最佳局部選擇且不再重新考慮（除非使用「反悔」堆積）。 | Considers all possible choices and their consequences before deciding. <br> 在決定前考慮所有可能的選擇及其後果。 |
| **Backtracking** | Generally No (except Priority Queue patterns). <br> 通常沒有（除優先佇列模式外）。 | Implicitly Yes (via recursion or table lookup). <br> 隱含地有（透過遞迴或查表）。 |
| **Correctness** | Harder to prove (requires Exchange Argument). <br> 較難證明（需要交換論證）。 | Guaranteed if state transition is correct. <br> 如果狀態轉移正確則保證正確。 |
| **Example** | Fractional Knapsack (Take highest value/weight ratio). <br> 分數背包（取最高價值/重量比）。 | 0/1 Knapsack (Must take whole item or none). <br> 0/1 背包（必須取整件物品或不取）。 |

**Common Mistake:** Applying Greedy to problems requiring DP.
**常見錯誤：** 將貪婪演算法應用於需要 DP 的問題。
*   *Example:* "Coin Change" with denominations `[1, 3, 4]` and target `6`.
    *   Greedy: `4, 1, 1` (3 coins).
    *   Optimal (DP): `3, 3` (2 coins).
    *   *Why Greedy fails:* The "greedy choice" (taking 4) eliminates the possibility of the optimal combination (3+3).

---

## 6. Interview Strategy（面試實戰建議）

### The Framework（口條框架）
1.  **State the Intuition:** "My initial thought is to process items based on [Criteria], because..."
    **陳述直覺：** 「我最初的想法是根據 [標準] 來處理項目，因為...」
2.  **Propose Greedy:** "If we sort by X, we can iterate and pick Y."
    **提出貪婪：** 「如果我們按 X 排序，我們可以迭代並選擇 Y。」
3.  **Self-Correction/Proof:** "However, let's verify if a local optimum leads to a global one. Let's consider a counter-example..."
    **自我修正/證明：** 「然而，讓我們驗證局部最佳解是否導向全域最佳解。讓我們考慮一個反例...」
4.  **Refine:** "Since a simple greedy approach fails in case Z, I will use a Priority Queue to allow 'swapping' previous decisions."
    **優化：** 「由於簡單貪婪法在情況 Z 下會失敗，我將使用優先佇列來允許『交換』先前的決定。」

### Whiteboard Strategy（白板策略）
*   **Draw a Timeline:** For interval problems, visual overlaps make the sorting criteria obvious.
    **畫時間軸：** 對於區間問題，視覺化的重疊讓排序標準變得顯而易見。
*   **Trace the "Regret":** Manually trace the Heap state. Show *why* removing the max element helps.
    **追蹤「反悔」過程：** 手動追蹤堆積狀態。展示*為什麼*移除最大元素會有幫助。

---

## 7. Practice Problems（練習題）

### Easy: Assign Cookies (455)
*   **Prompt:** Distribute cookies sizes `s` to children with greed factors `g` to maximize content children.
    **題目：** 將尺寸為 `s` 的餅乾分給貪婪指數為 `g` 的孩子，以最大化滿足的孩子數量。
*   **Hint:** Sort both. Smallest cookie to smallest greed requirement.
    **提示：** 兩者皆排序。最小的餅乾給需求最小的孩子。

### Medium: Gas Station (134)
*   **Prompt:** Can you complete a circuit? Return starting index.
    **題目：** 你能完成環形路程嗎？回傳起始索引。
*   **Hint:** If `total_gas < total_cost`, impossible. Else, iterate. If `current_tank < 0`, reset start point to `i + 1`. (Greedy choice: if A can't reach B, no point between A and B can reach B).
    **提示：** 如果 `total_gas < total_cost`，不可能。否則，迭代。如果 `current_tank < 0`，將起點重設為 `i + 1`。（貪婪選擇：如果 A 到不了 B，A 和 B 之間的任何點也到不了 B）。

### Hard: IPO (502)
*   **Prompt:** Pick `k` projects to maximize capital. Projects have cost and profit.
    **題目：** 選擇 `k` 個專案以最大化資本。專案有成本與利潤。
*   **Hint:** Two Heaps or Sort + Heap. Sort projects by capital cost. Push affordable projects into a Max-Heap (by profit). Pop best profit, update capital, repeat.
    **提示：** 兩個堆積或排序+堆積。按資本成本排序專案。將負擔得起的專案推入最大堆積（按利潤）。彈出最佳利潤，更新資本，重複。

---

## 8. Checklists（快速檢核表）

*   [ ] **Sorting Criteria:** Did I sort by Start Time, End Time, or Duration? Did I justify why?
    **排序標準：** 我是按開始時間、結束時間還是持續時間排序？我有證明原因嗎？
*   [ ] **Independence:** Does choosing X affect the *value* of future Y (not just availability)? If values change dynamically, consider DP or Flow.
    **獨立性：** 選擇 X 是否會影響未來 Y 的*價值*（而不僅僅是可用性）？如果價值動態改變，考慮 DP 或網路流。
*   [ ] **Counter-Example:** Can I construct a case where taking the biggest/smallest first fails?
    **反例：** 我能建構一個「先拿最大/最小」會失敗的案例嗎？
*   [ ] **Edge Cases:** What if all intervals overlap? What if `k=0`?
    **邊界條件：** 如果所有區間都重疊怎麼辦？如果 `k=0` 怎麼辦？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

### The "Short-Sighted Mountaineer" (Simple Greedy)
**「短視的登山客」（簡單貪婪）**
Imagine climbing a mountain in fog. You only take the step that goes steepest up.
想像在霧中登山。你只走往上最陡的那一步。
*   *Works for:* Convex mountains (simple problems).
    *適用於：* 凸型山峰（簡單問題）。
*   *Fails for:* Rugged terrain (local peaks trap you).
    *失敗於：* 崎嶇地形（局部高峰會困住你）。

### The "Regretful Shopper" (Greedy with Heap)
**「後悔的購物者」（帶堆積的貪婪）**
You buy items as you see them. When you run out of money but see something better, you return the most expensive item you bought previously to afford the new one.
你看到商品就買。當你錢花光了但看到更好的東西時，你退掉之前買過最貴的商品來買新的。
*   *Key:* You maintain a "receipt" (Heap) of what you bought to return the worst decision.
    *關鍵：* 你保留已買商品的「收據」（堆積），以便退掉最差的決定。