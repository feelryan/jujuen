# Advanced Heap & Priority Queue Interview Guide
# 進階堆積與優先佇列面試指南

## 1. Learning Goals（學習目標）

*   **Master Custom Comparators & Object Handling:**
    能夠在 TypeScript 中靈活處理複雜物件的優先級比較，而非僅限於數字。
    *Ability to handle complex object priority comparisons in TypeScript flexibly, not just numbers.*
*   **Internalize Advanced Patterns (Two Heaps & Lazy Removal):**
    熟練掌握「雙堆積（中位數）」與「延遲刪除（Lazy Removal）」技巧，解決動態數據流問題。
    *Master "Two Heaps (Median)" and "Lazy Removal" techniques to solve dynamic data stream problems.*
*   **Differentiate Heap vs. Sorting vs. BST:**
    在 $O(N \log K)$ 與 $O(N \log N)$ 之間做出精準的架構決策，並理解何時該用 `TreeSet` (BST) 代替 Heap。
    *Make precise architectural decisions between $O(N \log K)$ and $O(N \log N)$, and understand when to use `TreeSet` (BST) instead of Heap.*
*   **Handle TypeScript Ecosystem Gaps:**
    能夠在面試中快速實作或 Mock 一個生產級別的 Priority Queue（因為 TS 標準庫未內建）。
    *Ability to quickly implement or mock a production-grade Priority Queue in interviews (since TS std lib lacks one).*

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Heap 是一種特殊的完全二元樹（Complete Binary Tree），滿足堆積屬性：父節點總是小於（Min-Heap）或大於（Max-Heap）子節點。
*A Heap is a specialized complete binary tree that satisfies the heap property: parent nodes are always smaller (Min-Heap) or larger (Max-Heap) than their children.*

直覺上，它是「即時取得極值」的最優解，不需要維護整個序列的有序性。
*Intuitively, it is the optimal solution for "accessing extreme values in real-time" without maintaining the order of the entire sequence.*

### Complexity Analysis（複雜度分析）

| Operation | Time Complexity | Note |
| :--- | :--- | :--- |
| **Peek (Top)** | $O(1)$ | 僅查看根節點 / *Check root only* |
| **Push (Insert)** | $O(\log N)$ | 需要 Sift Up / *Requires Sift Up* |
| **Pop (Extract)** | $O(\log N)$ | 需要 Sift Down / *Requires Sift Down* |
| **Build Heap** | $O(N)$ | **Advanced:** 許多人誤以為是 $O(N \log N)$，但使用 `heapify` 是線性的。 / *Many mistake this for $O(N \log N)$, but `heapify` is linear.* |
| **Remove Arbitrary**| $O(N)$ or $O(\log N)$ | 若無 Hash Map 輔助查找為 $O(N)$；若有索引輔助則為 $O(\log N)$。 / *O(N) without Hash Map lookup; O(log N) with index tracking.* |

### When to Use (and Not)（適用與不適用場景）

*   **Use when:** 需要頻繁取得最大/最小值，且數據是動態變化的（Streaming）。
    *Use when: You frequently need the max/min value, and the data is dynamic (Streaming).*
*   **Don't use when:** 需要查找特定元素（Search）、需要區間查詢（Range Query），或數據是靜態且只需一次排序。
    *Don't use when: You need to search for specific elements, perform range queries, or data is static and only needs sorting once.*

---

## 3. Typical Patterns（典型題型 / 模式）

對於 Senior 工程師，單純的 Top K 已經是基本功。重點在於以下進階模式：

### A. Two Heaps (The Median Pattern)
使用一個 Max-Heap 儲存較小的一半數據，一個 Min-Heap 儲存較大的一半數據。
*Use a Max-Heap to store the smaller half of the data and a Min-Heap to store the larger half.*
*   **Application:** Find Median from Data Stream, Sliding Window Median.

### B. K-Way Merge / Sweep Line
多路歸併排序的核心。在處理多個有序來源（如 Log files, Matrix rows）時極為強大。
*The core of K-way merge sort. Extremely powerful when handling multiple sorted sources (e.g., Log files, Matrix rows).*
*   **Application:** Merge K Sorted Lists, Skyline Problem (Sweep Line + Heap).

### C. Lazy Removal (Delayed Deletion)
當需要從 Heap 中刪除非堆頂元素時，標準 Heap 很難做到 $O(\log N)$。
*When removing a non-root element from a Heap, standard Heaps struggle to do this in $O(\log N)$.*
**策略：** 記錄要刪除的元素（例如在 Hash Map 中計數），當該元素浮到堆頂（Top）時才真正丟棄。
*Strategy: Record the element to be deleted (e.g., count in a Hash Map), and only physically discard it when it floats to the top.*

### D. Greedy + Priority Queue (IPO Pattern)
在資源有限的情況下，每次選擇當前「可負擔」選項中收益最大的一個。
*In resource-constrained situations, greedily choose the option with the highest return among currently "affordable" ones.*
*   **Application:** IPO, Course Schedule III.

---

## 4. Example Walkthrough（範例講解）

### Problem: Sliding Window Median (Hard)
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，有一個大小為 `k` 的滑動視窗從陣列最左側移動到最右側。找出每個視窗的中位數。
*Problem Statement: Given an integer array `nums` and an integer `k`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. Find the median of each window.*

### Approach（思路）

1.  **Brute Force:** 每次視窗移動，取出 k 個元素排序找中位數。
    *Complexity:* $O(N \cdot K \log K)$. Too slow.
2.  **Optimization (Two Heaps + Lazy Removal):**
    *   維護兩個 Heap：`small` (Max-Heap) 和 `large` (Min-Heap)。
    *   `small` 存前 $k/2$ 小的數，`large` 存後 $k/2$ 大的數。
    *   **難點 (The Hard Part):** 當視窗滑動時，移出的元素可能不在堆頂。我們不能直接刪除它。
    *   **Solution:** 使用 **Lazy Removal**。用一個 Hash Map 記錄「應該被刪除但還在 Heap 裡」的數字。當堆頂元素出現在 Hash Map 時，才將其 Pop 掉。

### TypeScript Solution (Advanced)

*注意：由於 TypeScript 無內建 Heap，面試時通常需手寫簡易版或假設有庫。以下提供包含 Lazy Removal 邏輯的完整解法。*

```typescript
/**
 * Helper class for Priority Queue
 * 面試時可簡化，但需向面試官說明介面
 */
class PriorityQueue<T> {
    private heap: T[] = [];
    
    constructor(private compare: (a: T, b: T) => number) {}

    // 查看堆頂 / Peek at the top
    peek(): T | undefined {
        return this.heap[0];
    }

    // 加入元素 / Add element
    push(val: T): void {
        this.heap.push(val);
        this._siftUp();
    }

    // 取出堆頂 / Remove and return top
    pop(): T | undefined {
        if (this.size() === 0) return undefined;
        const top = this.heap[0];
        const bottom = this.heap.pop()!;
        if (this.size() > 0) {
            this.heap[0] = bottom;
            this._siftDown();
        }
        return top;
    }

    size(): number {
        return this.heap.length;
    }

    private _siftUp(): void {
        let nodeIdx = this.heap.length - 1;
        while (nodeIdx > 0) {
            const parentIdx = Math.floor((nodeIdx - 1) / 2);
            if (this.compare(this.heap[nodeIdx], this.heap[parentIdx]) < 0) {
                [this.heap[nodeIdx], this.heap[parentIdx]] = [this.heap[parentIdx], this.heap[nodeIdx]];
                nodeIdx = parentIdx;
            } else {
                break;
            }
        }
    }

    private _siftDown(): void {
        let nodeIdx = 0;
        while (nodeIdx * 2 + 1 < this.heap.length) {
            let leftChildIdx = nodeIdx * 2 + 1;
            let rightChildIdx = nodeIdx * 2 + 2;
            let swapIdx = leftChildIdx;

            if (rightChildIdx < this.heap.length && 
                this.compare(this.heap[rightChildIdx], this.heap[leftChildIdx]) < 0) {
                swapIdx = rightChildIdx;
            }

            if (this.compare(this.heap[swapIdx], this.heap[nodeIdx]) < 0) {
                [this.heap[nodeIdx], this.heap[swapIdx]] = [this.heap[swapIdx], this.heap[nodeIdx]];
                nodeIdx = swapIdx;
            } else {
                break;
            }
        }
    }
}

/**
 * Main Solution: Sliding Window Median using Dual Heaps + Lazy Removal
 */
function medianSlidingWindow(nums: number[], k: number): number[] {
    // Max-Heap: stores the smaller half. (a < b means b has higher priority -> Max Heap logic reversed for compare)
    // TypeScript trick: b - a for MaxHeap if numbers
    const small = new PriorityQueue<number>((a, b) => b - a); 
    
    // Min-Heap: stores the larger half.
    const large = new PriorityQueue<number>((a, b) => a - b);
    
    // Map to keep track of delayed removals: number -> count
    // 記錄待刪除元素的計數器
    const delayed = new Map<number, number>();
    
    const result: number[] = [];
    
    // Helper to balance heaps
    // 確保 small 的大小等於 large 或比 large 多 1
    const balance = () => {
        // Make sure small doesn't have "dead" roots
        prune(small);
        prune(large);

        // Move elements if size ratio is off
        // Note: We track logical size, but since we can't easily get logical size with lazy removal,
        // we rely on the loop invariant: we always add to small, then move to large, then balance back.
        // This part is tricky with Lazy Removal. 
        // A simpler strategy for interview: Always push to small, pop small push large, 
        // if large.size > small.size, move back.
        // But with lazy removal, .size() is inaccurate.
        // We need to track `balanceFactor`: smallSize - largeSize
    };

    // Simplified approach for Interview context (Focusing on logic flow)
    // 實際面試中，完全實作 Lazy Removal 的細節極易出錯。
    // 這裡展示核心邏輯：
    
    let balanceFactor = 0; // small size - large size

    for (let i = 0; i < nums.length; i++) {
        // 1. Add new element (In-window)
        // Always add to small first, then maybe move to large
        if (small.size() === 0 || nums[i] <= small.peek()!) {
            small.push(nums[i]);
            balanceFactor++;
        } else {
            large.push(nums[i]);
            balanceFactor--;
        }

        // 2. Remove old element (Out-window)
        if (i >= k) {
            const outNum = nums[i - k];
            // Mark for lazy removal
            delayed.set(outNum, (delayed.get(outNum) || 0) + 1);
            
            // Update balance factor logically
            if (outNum <= small.peek()!) {
                balanceFactor--;
            } else {
                balanceFactor++;
            }
        }

        // 3. Rebalance
        // We want balanceFactor to be 0 (even k) or 1 (odd k, small has 1 more)
        
        // Clean up dead roots first
        prune(small, delayed);
        prune(large, delayed);

        while (balanceFactor > 1) {
            large.push(small.pop()!);
            prune(small, delayed); // Clean up immediately after pop reveals new root
            balanceFactor -= 2; // small -1, large +1 => net change -2
        }
        while (balanceFactor < 0) {
            small.push(large.pop()!);
            prune(large, delayed);
            balanceFactor += 2;
        }

        // 4. Record Median
        if (i >= k - 1) {
            if (k % 2 === 1) {
                result.push(small.peek()!);
            } else {
                // Prevent overflow in other languages, TS uses double by default so it's fine
                result.push(small.peek()! / 2 + large.peek()! / 2);
            }
        }
    }

    return result;
}

// Lazy Removal Helper: Remove invalid top elements
// 輔助函式：移除堆頂已標記為刪除的元素
function prune(heap: PriorityQueue<number>, delayed: Map<number, number>) {
    while (heap.size() > 0 && delayed.has(heap.peek()!) && delayed.get(heap.peek()!)! > 0) {
        const val = heap.pop()!;
        delayed.set(val, delayed.get(val)! - 1);
    }
}
```

### Complexity Analysis
*   **Time:** $O(N \log K)$. 每個元素進出 Heap 各一次，Heap 大小最多約為 $N$ (考慮 lazy removal 堆積可能暫時包含所有元素，但均攤是 $\log K$)。
*   **Space:** $O(N)$. 最壞情況下，Lazy Removal 可能導致 Heap 存儲 $O(N)$ 個元素（如果刪除的元素一直不浮到堆頂）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake | Correction |
| :--- | :--- | :--- |
| **Heapify Complexity** | 認為將陣列轉為 Heap 是 $O(N \log N)$。 / *Thinking converting array to Heap is $O(N \log N)$.* | 實際上是 **$O(N)$**。這在「Top K from N elements」問題中是關鍵優化點。 / *It is actually $O(N)$. This is a key optimization for Top K problems.* |
| **Min vs Max Heap** | 在 Python/TS 中混淆比較器方向。 / *Confusing comparator direction in Python/TS.* | TS: `(a, b) => a - b` 是 Min-Heap (小在前)。Python `heapq` 預設是 Min-Heap，求 Max 需存負數。 / *TS: `a - b` is Min-Heap. Python defaults to Min-Heap; negate numbers for Max.* |
| **Arbitrary Removal** | 試圖在 Heap 中直接刪除中間節點。 / *Trying to delete a middle node directly.* | 這是 $O(N)$ 操作。必須使用 Lazy Removal 或輔助索引結構 (TreeMap/Hash)。 / *This is $O(N)$. Must use Lazy Removal or auxiliary structures.* |
| **Heap vs BST** | 認為 Heap 是有序的。 / *Thinking Heap is sorted.* | Heap 只是弱序（Weakly ordered）。只有 Parent-Child 關係，Sibling 之間無序。 / *Heap is weakly ordered. Only Parent-Child relation holds; siblings are unordered.* |

---

## 6. Interview Strategy（面試實戰建議）

### The "No Built-in Heap" Strategy (TS Specific)
在 TS 面試中，這是一個常見痛點。建議採取以下策略：

1.  **Ask Permission:** "TypeScript doesn't have a built-in Priority Queue. Is it okay if I assume a `MinHeap` class exists with `push`, `pop`, and `peek` methods?"
    *（TypeScript 沒有內建優先佇列。我是否可以假設存在一個具備 `push`, `pop`, `peek` 方法的 `MinHeap` 類別？）*
2.  **Offer Implementation:** "If needed, I can implement a basic binary heap using an array in about 5-10 minutes."
    *（如果有需要，我可以在 5-10 分鐘內用陣列實作一個基本的 Binary Heap。）*
3.  **Use the Interface:** 寫程式碼時，先定義介面，讓主邏輯保持乾淨。

### Whiteboard / Communication
*   **Visualize:** 當提到 "Two Heaps" 時，畫一個漏斗形狀（上寬下窄），上面是 Max-Heap（存較小值），下面是 Min-Heap（存較大值），中間接觸點是中位數。
*   **Trade-off:** 主動提及 "Why Heap?"。
    *   "Sorting the whole array is $O(N \log N)$, but we only need the top K, so a Heap gives us $O(N \log K)$."

---

## 7. Practice Problems（練習題）

### Level 1: Warm-up (Concept Check)
**Problem:** **Kth Largest Element in an Array** (LeetCode 215)
*   **Hint:** Compare Min-Heap of size K vs. QuickSelect ($O(N)$ average).
*   **Key:** Senior engineers should discuss QuickSelect as the optimal solution, but implement Heap for stability/worst-case guarantees if asked.

### Level 2: Intermediate (Standard Pattern)
**Problem:** **Merge k Sorted Lists** (LeetCode 23)
*   **Hint:** Put the head of each list into a Min-Heap. Always pop the smallest and push its `next` node.
*   **Key:** Handle the custom comparator for ListNodes. Complexity $O(N \log k)$.

### Level 3: Advanced (Complex Application)
**Problem:** **IPO** (LeetCode 502) or **Task Scheduler** (LeetCode 621)
*   **Hint (IPO):** Use two heaps. Sort projects by capital. Push affordable projects into a Max-Heap (based on profit). Pop the best profit, update capital, repeat.
*   **Key:** Greedy strategy combined with dynamic availability managed by Heaps.

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Boundary:** Did I handle `k=0` or empty input?
    *（邊界：是否處理了 k=0 或空輸入？）*
*   [ ] **Comparator:** Is my comparator correct? `a - b` for Min, `b - a` for Max.
    *（比較器：`a - b` 是小頂堆，`b - a` 是大頂堆。）*
*   [ ] **Complexity:** Did I say $O(N \log N)$ when it's actually $O(N \log K)$?
    *（複雜度：是否誤將 N log K 說成 N log N？）*
*   [ ] **Object Reference:** When storing objects, am I mutating them? Does that affect the heap order? (Heap doesn't auto-rebalance if internal values change).
    *（物件引用：修改堆中物件的屬性會破壞堆積屬性嗎？Heap 不會自動重排。）*

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

### The "VIP Club" Analogy (Priority Queue)
想像一家夜店（The Processor），門口有保鏢（The Heap）。
*Imagine a nightclub (The Processor) with a bouncer (The Heap) at the door.*

*   **Min-Heap:** 這是個「比爛」的俱樂部，越爛（數值越小）的越先被踢進去。
*   **Max-Heap:** 這是個 VIP 俱樂部，身價最高（數值最大）的排在最前面進場。
*   **Push/Pop:** 新人來排隊（Push）或放人進場（Pop）都需要重新調整隊伍（log N），但保鏢一眼就能看到排頭是誰（Peek, O(1)）。

### The "Floating Bubble" (Sift Up/Down)
*   **Sift Up:** 像氣泡在水中上浮，輕的（符合條件的）往上飄。
*   **Sift Down:** 像石頭沉入水底，重的往下掉。