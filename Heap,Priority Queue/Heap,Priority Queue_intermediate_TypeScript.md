# Heap & Priority Queue: Intermediate to Advanced Guide
# 堆積與優先佇列：中階至進階指南

## 1. Learning Objectives (學習目標)

1.  **Master the TypeScript Implementation Gap:** Since TypeScript/JS has no built-in Heap, learn to implement a concise, bug-free Binary Heap from scratch or mock its interface effectively.
    **掌握 TypeScript 的實作落差：** 由於 TypeScript/JS 沒有內建 Heap，需學會從頭實作一個精簡且無 bug 的 Binary Heap，或有效地模擬其介面。
2.  **Internalize Key Patterns:** Move beyond basic sorting; master "Top K", "Merge K Streams", and "Two Heaps" (Median) patterns.
    **內化關鍵模式：** 超越基礎排序；掌握「前 K 大」、「合併 K 個串流」與「雙堆積」（中位數）模式。
3.  **Understand Complexity Nuances:** Distinguish between $O(N)$ heapify and $O(N \log N)$ sequential pushes, and know when to use Lazy Deletion.
    **理解複雜度細節：** 區分 $O(N)$ 的堆積化與 $O(N \log N)$ 的連續推入，並知道何時使用延遲刪除（Lazy Deletion）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Heap is a specialized complete binary tree that satisfies the heap property: in a max-heap, for any given node $I$, the value of $I$ is greater than or equal to the values of its children.
Heap 是一種特殊的完全二元樹，滿足堆積性質：在最大堆積（Max-Heap）中，對於任意節點 $I$，其值皆大於或等於其子節點的值。

A Priority Queue is an abstract data type (ADT) often implemented using a Heap, where elements are served based on priority rather than insertion order.
優先佇列（Priority Queue）是一種通常由 Heap 實作的抽象資料型別（ADT），元素是根據優先級而非插入順序被取出。

### Intuition (直覺)
Think of a Heap as a "Dynamic Extremum Tracker". It allows you to access the highest (or lowest) priority element instantly while supporting updates efficiently.
將 Heap 視為「動態極值追蹤器」。它允許你即時存取最高（或最低）優先級的元素，同時支援高效的更新。

### Complexity (複雜度)

| Operation | Time Complexity | Note (備註) |
| :--- | :--- | :--- |
| **Peek (Top)** | $O(1)$ | Access root. (存取根節點) |
| **Push (Insert)** | $O(\log N)$ | Sift up (bubble up). (上濾) |
| **Pop (Extract)** | $O(\log N)$ | Swap root with last, sift down. (交換根與末尾，下濾) |
| **Heapify (Build)**| $O(N)$ | Mathematically proven tighter bound than $N \log N$. (數學證明比 $N \log N$ 更緊湊) |
| **Space** | $O(N)$ | Array storage. (陣列儲存) |

### When to Use (適用場景)
*   Continuous access to the min/max element is required. (需要持續存取最小/最大元素時)
*   Scheduling tasks based on priority. (基於優先級排程任務)
*   Finding the $K$ largest/smallest elements in a large dataset. (在大數據集中尋找前 $K$ 大/小的元素)

### When NOT to Use (不適用場景)
*   Searching for an arbitrary element ($O(N)$). (搜尋任意元素)
*   Finding the min element in a Max-Heap ($O(N)$). (在最大堆積中尋找最小值)
*   Data is static and fits in memory (Sorting is often simpler/faster due to cache locality). (資料是靜態且可放入記憶體，排序通常因快取局部性而更簡單/快速)

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Top K Elements (前 K 個元素)
*   **Pattern:** Use a Min-Heap of size $K$ to find the $K$ largest elements.
*   **模式：** 使用大小為 $K$ 的 Min-Heap 來尋找前 $K$ 大的元素。
*   **Logic:** If a new element is larger than the heap's root (the smallest of the top $K$), pop the root and push the new one.
*   **邏輯：** 若新元素大於堆積的根（前 $K$ 大中最小的），則彈出根並推入新元素。

### B. Merge K Sorted Arrays/Lists (合併 K 個已排序陣列)
*   **Pattern:** Push the first element of each array into a Min-Heap. Pop the min, and push the next element from the same array.
*   **模式：** 將每個陣列的第一個元素推入 Min-Heap。彈出最小值，並將該值所屬陣列的下一個元素推入。

### C. Two Heaps (Median Maintenance) (雙堆積：中位數維護)
*   **Pattern:** Maintain a Max-Heap for the lower half of data and a Min-Heap for the upper half.
*   **模式：** 維護一個 Max-Heap 存放資料的下半部，以及一個 Min-Heap 存放資料的上半部。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge K Sorted Lists (合併 K 個排序鏈結串列)
*LeetCode 23 (Hard) - Classic Senior Interview Question*

**Problem Statement:**
You are given an array of $k$ linked-lists `lists`, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.
給定一個包含 $k$ 個鏈結串列的陣列 `lists`，每個鏈結串列皆已按升序排序。將所有鏈結串列合併為一個排序的鏈結串列並回傳。

### Approach Evolution (思路演進)

1.  **Brute Force (暴力法):**
    *   Collect all nodes into an array, sort them, and rebuild the list.
    *   將所有節點收集到陣列中，排序，然後重建串列。
    *   *Time:* $O(N \log N)$ where $N$ is total nodes. (時間：$O(N \log N)$，其中 $N$ 為總節點數)
    *   *Critique:* Ignores the fact that inputs are already sorted. (批評：忽略了輸入已排序的事實)

2.  **Compare One by One (逐一比較):**
    *   Compare the heads of all $k$ lists to find the minimum, add to result, move pointer.
    *   比較所有 $k$ 個串列的頭部以找到最小值，加入結果，移動指標。
    *   *Time:* $O(k \cdot N)$. If $k$ is large, this is slow. (時間：$O(k \cdot N)$。若 $k$ 很大，這會很慢)

3.  **Optimal: Min-Heap (最佳解：最小堆積):**
    *   Use a Min-Heap to keep track of the current head of each list. The heap size is at most $k$.
    *   使用 Min-Heap 來追蹤每個串列當前的頭部。堆積大小最多為 $k$。
    *   *Time:* $O(N \log k)$. Since $k \le N$, this is better than $O(N \log N)$.
    *   *時間：* $O(N \log k)$。由於 $k \le N$，這優於 $O(N \log N)$。

### TypeScript Reference Solution (TypeScript 參考解)

*Note: Since TS has no built-in Heap, we implement a minimal one. In a real interview, ask if you can assume a `PriorityQueue` class exists.*
*注意：由於 TS 無內建 Heap，我們實作一個精簡版。在實際面試中，請問是否可假設 `PriorityQueue` 類別已存在。*

```typescript
/**
 * Definition for singly-linked list.
 */
class ListNode {
    val: number
    next: ListNode | null
    constructor(val?: number, next?: ListNode | null) {
        this.val = (val===undefined ? 0 : val)
        this.next = (next===undefined ? null : next)
    }
}

// Minimal MinHeap Implementation for Interview
// 面試用的精簡 MinHeap 實作
class MinHeap<T> {
    private data: T[];
    private compare: (a: T, b: T) => number;

    constructor(compare: (a: T, b: T) => number) {
        this.data = [];
        this.compare = compare;
    }

    // Access the top element (O(1))
    // 存取頂端元素 (O(1))
    peek(): T | undefined {
        return this.data[0];
    }

    // Add element and sift up (O(log k))
    // 加入元素並上濾 (O(log k))
    push(val: T): void {
        this.data.push(val);
        this._siftUp(this.data.length - 1);
    }

    // Remove top element and sift down (O(log k))
    // 移除頂端元素並下濾 (O(log k))
    pop(): T | undefined {
        if (this.size() === 0) return undefined;
        const top = this.data[0];
        const bottom = this.data.pop();
        if (this.size() > 0 && bottom !== undefined) {
            this.data[0] = bottom;
            this._siftDown(0);
        }
        return top;
    }

    size(): number {
        return this.data.length;
    }

    private _siftUp(idx: number): void {
        while (idx > 0) {
            // Parent index formula: floor((i - 1) / 2)
            // 父節點索引公式：floor((i - 1) / 2)
            const parentIdx = (idx - 1) >>> 1; 
            if (this.compare(this.data[idx], this.data[parentIdx]) < 0) {
                [this.data[idx], this.data[parentIdx]] = [this.data[parentIdx], this.data[idx]];
                idx = parentIdx;
            } else {
                break;
            }
        }
    }

    private _siftDown(idx: number): void {
        const halfLength = this.data.length >>> 1;
        while (idx < halfLength) {
            const left = (idx << 1) + 1;
            const right = left + 1;
            let best = left;

            // Find the smaller child
            // 找出較小的子節點
            if (right < this.data.length && this.compare(this.data[right], this.data[left]) < 0) {
                best = right;
            }

            // If current is smaller than best child, we are done
            // 若當前節點小於最佳子節點，則完成
            if (this.compare(this.data[idx], this.data[best]) <= 0) break;

            [this.data[idx], this.data[best]] = [this.data[best], this.data[idx]];
            idx = best;
        }
    }
}

function mergeKLists(lists: Array<ListNode | null>): ListNode | null {
    // Comparator for ListNode based on val
    // 基於 val 的 ListNode 比較器
    const heap = new MinHeap<ListNode>((a, b) => a.val - b.val);

    // 1. Initialize heap with the head of each list
    // 1. 將每個串列的頭部初始化入堆積
    for (const list of lists) {
        if (list) {
            heap.push(list);
        }
    }

    // Dummy head to simplify result construction
    // 虛擬頭節點以簡化結果建構
    const dummy = new ListNode(0);
    let current = dummy;

    // 2. Extract min and push next
    // 2. 取出最小值並推入下一個節點
    while (heap.size() > 0) {
        const node = heap.pop()!;
        current.next = node;
        current = current.next;

        if (node.next) {
            heap.push(node.next);
        }
    }

    return dummy.next;
}
```

### Common Mistake (錯誤示範)
*   **Mistake:** Re-sorting the array inside the loop.
*   **錯誤：** 在迴圈內重新排序陣列。
*   **Why:** `Array.sort()` is $O(N \log N)$. Doing this inside a loop makes it $O(N^2 \log N)$ or worse.
*   **原因：** `Array.sort()` 是 $O(N \log N)$。在迴圈內執行會變成 $O(N^2 \log N)$ 或更糟。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Min-Heap for Top K** | **Max-Heap for Top K** | To find the **largest** K elements, use a **Min-Heap** (keep the large ones, discard the smallest of the heap). <br> 為了找**最大**的 K 個，使用 **Min-Heap**（保留大的，丟棄堆積中最小的）。 |
| **Heapify** | **Push Loop** | `Heapify` builds a heap from an array in $O(N)$. Pushing $N$ items one by one is $O(N \log N)$. <br> `Heapify` 以 $O(N)$ 從陣列建立堆積。逐一推入 $N$ 個項目是 $O(N \log N)$。 |
| **Array** | **Heap** | A heap is implicitly stored as an array, but it is **not sorted**. Only the parent-child relationship is ordered. <br> 堆積隱式儲存為陣列，但它**未排序**。只有父子關係是有序的。 |

---

## 6. Interview Strategy (面試實戰建議)

### The "No Native Heap" Strategy (「無內建 Heap」策略)
Since you are using TypeScript:
1.  **Declare Intent:** "TypeScript doesn't have a standard Priority Queue. I can implement a Helper Class, or assume one exists. Which do you prefer?"
    **聲明意圖：** 「TypeScript 沒有標準的 Priority Queue。我可以實作一個輔助類別，或者假設它已存在。您偏好哪種？」
2.  **Stubbing:** If they say "assume it exists", write the interface clearly:
    **介面定義：** 若他們說「假設存在」，清楚寫下介面：
    ```typescript
    // I will assume a MinHeap class with push(val), pop(), peek(), and size() methods.
    const minHeap = new MinHeap<number>();
    ```
3.  **Implementation:** If asked to implement, stick to the array-based binary heap. Do not try to implement Fibonacci Heap or Pairing Heap.
    **實作：** 若被要求實作，堅持使用基於陣列的 Binary Heap。不要嘗試實作 Fibonacci Heap 或 Pairing Heap。

### Whiteboard / Communication (白板 / 溝通)
*   **Visualize:** Draw the tree structure, but write the array indices $[0, 1, 2, ...]$ underneath to show you understand the mapping.
    **視覺化：** 畫出樹狀結構，但在下方寫出陣列索引 $[0, 1, 2, ...]$ 以顯示你理解其對映關係。
*   **Justify:** "I'm using a Heap here because we need repeated access to the minimum element, and the data is dynamic."
    **證成：** 「我在這裡使用 Heap 是因為我們需要重複存取最小值，且資料是動態的。」

---

## 7. Practice Problems (練習題)

### Easy: Kth Largest Element in a Stream (串流中的第 K 大元素)
*   **Hint:** Maintain a Min-Heap of size $K$. If size $> K$, pop the min. The root is always the $K^{th}$ largest.
*   **提示：** 維護一個大小為 $K$ 的 Min-Heap。若大小 $> K$，彈出最小值。根節點永遠是第 $K$ 大。

### Medium: Task Scheduler (任務排程器)
*   **Hint:** Greedy approach. Count frequencies. Use a Max-Heap to always pick the most frequent task that is not on "cooldown".
*   **提示：** 貪婪法。計算頻率。使用 Max-Heap 總是選取頻率最高且不在「冷卻中」的任務。

### Hard: Find Median from Data Stream (數據串流的中位數)
*   **Hint:** Two Heaps pattern. `low` (Max-Heap) stores the smaller half, `high` (Min-Heap) stores the larger half. Balance sizes so $|low| \approx |high|$.
*   **提示：** 雙堆積模式。`low` (Max-Heap) 儲存較小的一半，`high` (Min-Heap) 儲存較大的一半。平衡大小使得 $|low| \approx |high|$。

---

## 8. Checklists (快速檢核表)

### Self-Review during Coding (編碼時自我審查)
- [ ] **Index Math:** Did I use `(i-1) >>> 1` for parent and `2*i + 1` for left child? (Zero-indexed)
  **索引數學：** 父節點是否用 `(i-1) >>> 1`，左子節點是否用 `2*i + 1`？（零基索引）
- [ ] **Empty Check:** Did I handle `pop()` or `peek()` on an empty heap?
  **空檢查：** 是否處理了空堆積的 `pop()` 或 `peek()`？
- [ ] **Comparator:** Does my comparator return negative for `a < b`? (Crucial for Min vs Max heap logic).
  **比較器：** 我的比較器在 `a < b` 時是否回傳負值？（對 Min vs Max heap 邏輯至關重要）。

### Complexity Check (複雜度確認)
- [ ] Am I calling `indexOf` or `remove` (by value) on the heap array? That makes it $O(N)$, defeating the purpose of a heap ($O(\log N)$).
  **複雜度：** 我是否在堆積陣列上呼叫 `indexOf` 或 `remove`（按值刪除）？這會變成 $O(N)$，違背了堆積（$O(\log N)$）的初衷。

---

## 9. Memory Anchors (記憶錨點)

### The Corporate Hierarchy (企業階層)
*   **Max-Heap:** The CEO is at the top. Every manager is "greater" (more powerful) than their direct reports. However, a manager in Sales isn't necessarily more powerful than a manager in Engineering (siblings are not ordered).
*   **Max-Heap：** CEO 在頂端。每個經理都比其直接下屬「大」（權力更大）。然而，業務部的經理不一定比工程部的經理權力大（兄弟節點無序）。

### The ER Triage (急診室檢傷)
*   **Priority Queue:** Patients arrive at random times. The doctor doesn't see the "first come", but the "most critical" (Priority). The triage nurse (Heap logic) constantly shuffles the queue so the most critical is always at the door.
*   **優先佇列：** 病患隨機到達。醫生不看「先到的」，而是看「最危急的」（優先級）。檢傷護理師（Heap 邏輯）不斷調整隊伍，讓最危急的總是在門口。