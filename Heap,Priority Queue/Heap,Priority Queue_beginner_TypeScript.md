# Heap & Priority Queue (堆積與優先隊列) - Beginner Level

## 1. Learning Objectives (學習目標)

1.  **Understand the Internal Structure:** Comprehend how a Binary Heap maps to an array and the logic behind parent-child index relationships.
    **理解內部結構：** 理解二元堆積（Binary Heap）如何映射到陣列，以及父子節點索引關係背後的邏輯。
2.  **Master Core Operations:** Be able to implement `push` (sift-up) and `pop` (sift-down) from scratch in TypeScript.
    **掌握核心操作：** 能夠在 TypeScript 中從頭實作 `push`（上濾）與 `pop`（下濾）。
3.  **Identify Use Cases:** Recognize when to use a Heap (e.g., "Top K elements", "Dynamic merging") versus sorting.
    **識別使用場景：** 辨識何時該使用 Heap（例如「前 K 個元素」、「動態合併」）而非排序。
4.  **Complexity Awareness:** Internalize the time complexity differences between Heap operations and standard Array operations.
    **複雜度意識：** 內化 Heap 操作與標準陣列操作之間的時間複雜度差異。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A **Heap** is a specialized tree-based data structure that satisfies the heap property.
**堆積（Heap）** 是一種特殊的樹狀資料結構，它滿足堆積屬性。
-   **Max-Heap:** The key at the root must be maximum among all keys present in the binary heap. The same property must be recursively true for all nodes.
    **最大堆積（Max-Heap）：** 根節點的鍵值必須是所有節點中最大的。此屬性對所有節點遞迴成立。
-   **Min-Heap:** The key at the root must be minimum.
    **最小堆積（Min-Heap）：** 根節點的鍵值必須是最小的。

A **Priority Queue** is an abstract data type where each element has a "priority", and the element with the highest priority is served first. It is usually implemented using a Heap.
**優先隊列（Priority Queue）** 是一種抽象資料型別，每個元素都有「優先級」，優先級最高的元素最先被處理。通常使用 Heap 來實作。

### Intuition (直覺)
Think of a Heap as a "dynamically sorting" container that only guarantees the order of the extreme element (top), not the entire collection.
將 Heap 視為一個「動態排序」的容器，它只保證極值元素（頂端）的順序，而不保證整個集合的順序。

### Complexity (複雜度)

| Operation | Time Complexity | Note |
| :--- | :--- | :--- |
| **Peek (Get Max/Min)** | $O(1)$ | No removal. / 不移除元素。 |
| **Push (Insert)** | $O(\log N)$ | Needs to sift up. / 需要上濾。 |
| **Pop (Remove Max/Min)** | $O(\log N)$ | Needs to sift down. / 需要下濾。 |
| **Build Heap** | $O(N)$ | If built from an existing array. / 若從現有陣列建構。 |
| **Space Complexity** | $O(N)$ | Array storage. / 陣列儲存。 |

### When to Use (適用場景)
-   Finding the $K$-th largest/smallest element.
    尋找第 $K$ 大/小的元素。
-   Tasks requiring constant access to the highest priority item (e.g., Task Scheduling).
    需要持續存取最高優先級項目的任務（例如：任務排程）。
-   Merge $K$ sorted streams.
    合併 $K$ 個已排序的串流。

### When NOT to Use (不適用場景)
-   Searching for an arbitrary element (Time: $O(N)$).
    搜尋任意元素（時間複雜度：$O(N)$）。
-   Finding the Max in a Min-Heap (Time: $O(N)$ - requires scanning leaves).
    在最小堆積中尋找最大值（時間複雜度：$O(N)$ - 需要掃描葉節點）。

---

## 3. Typical Patterns (典型題型 / 模式)

Since TypeScript does not have a built-in Heap class (unlike Python's `heapq` or Java's `PriorityQueue`), knowing how to implement a basic one is a "Pattern" in itself for TS developers.
由於 TypeScript 沒有內建的 Heap 類別（不像 Python 的 `heapq` 或 Java 的 `PriorityQueue`），知道如何實作一個基礎 Heap 對 TS 開發者來說本身就是一種「模式」。

1.  **Top K Elements (前 K 個元素):**
    -   Keep a Min-Heap of size $K$.
    -   維護一個大小為 $K$ 的最小堆積。
    -   If a new element is larger than the heap's root, pop the root and push the new element.
    -   若新元素比堆積根節點大，彈出根節點並推入新元素。
2.  **Merge Intervals / Lists (合併區間/列表):**
    -   Put the head of each list into a Min-Heap.
    -   將每個列表的頭部放入最小堆積。
    -   Always extract the minimum and add the next element from that specific list.
    -   總是取出最小值，並加入該特定列表的下一個元素。

---

## 4. Example Walkthrough (範例講解)

### Problem: Kth Largest Element in an Array
### 問題重述：陣列中第 K 大的元素

Given an integer array `nums` and an integer `k`, return the $k$-th largest element in the array.
給定一個整數陣列 `nums` 和一個整數 `k`，回傳陣列中第 $k$ 大的元素。

**Example:**
Input: `nums = [3,2,1,5,6,4], k = 2`
Output: `5`

---

### Approach 1: Brute Force (Sorting)
### 思路 1：暴力解（排序）

Sort the array in descending order and take the element at index $k-1$.
將陣列由大到小排序，取索引 $k-1$ 的元素。

-   **Time:** $O(N \log N)$
-   **Space:** $O(1)$ or $O(N)$ (depending on sort implementation).

### Approach 2: Min-Heap (Optimal for Streaming)
### 思路 2：最小堆積（適用於串流資料的最佳解）

Maintain a Min-Heap of size $k$. The root of the heap represents the $k$-th largest element seen so far.
維護一個大小為 $k$ 的最小堆積。堆積的根節點代表目前為止看到的第 $k$ 大元素。

1.  Iterate through `nums`.
    遍歷 `nums`。
2.  Push element into Heap.
    將元素推入 Heap。
3.  If Heap size > $k$, pop the minimum (root).
    如果 Heap 大小 > $k$，彈出最小值（根節點）。
4.  The remaining root is the answer.
    剩下的根節點即為答案。

-   **Time:** $O(N \log k)$
-   **Space:** $O(k)$

---

### TypeScript Implementation (Minimal Heap Class + Solution)
### TypeScript 實作（極簡 Heap 類別 + 解法）

Since this is a "Beginner" depth guide, we will implement a clean, simple MinHeap class.
由於這是「初學者」深度的指南，我們將實作一個乾淨、簡單的 MinHeap 類別。

```typescript
/**
 * A minimal Min-Heap implementation for interview purposes.
 * 為了面試目的的極簡最小堆積實作。
 */
class MinHeap {
    private heap: number[];

    constructor() {
        this.heap = [];
    }

    // Get parent index / 取得父節點索引
    private getParentIndex(i: number): number {
        return Math.floor((i - 1) / 2);
    }

    // Get left child index / 取得左子節點索引
    private getLeftChildIndex(i: number): number {
        return 2 * i + 1;
    }

    // Get right child index / 取得右子節點索引
    private getRightChildIndex(i: number): number {
        return 2 * i + 2;
    }

    // Swap two elements / 交換兩個元素
    private swap(i1: number, i2: number): void {
        [this.heap[i1], this.heap[i2]] = [this.heap[i2], this.heap[i1]];
    }

    // Helper to get the top element / 取得頂端元素的輔助方法
    peek(): number | undefined {
        return this.heap[0];
    }

    size(): number {
        return this.heap.length;
    }

    // Insert a new value / 插入新值
    push(value: number): void {
        this.heap.push(value);
        this.heapifyUp(); // Restore heap property / 恢復堆積屬性
    }

    // Remove and return the minimum value / 移除並回傳最小值
    pop(): number | undefined {
        if (this.heap.length === 0) return undefined;
        if (this.heap.length === 1) return this.heap.pop();

        const root = this.heap[0];
        // Move the last element to the root / 將最後一個元素移到根部
        this.heap[0] = this.heap.pop()!;
        this.heapifyDown(); // Restore heap property / 恢復堆積屬性
        return root;
    }

    // Sift up: move the last element up to its correct position
    // 上濾：將最後一個元素向上移動到正確位置
    private heapifyUp(): void {
        let index = this.heap.length - 1;
        while (
            index > 0 && 
            this.heap[this.getParentIndex(index)] > this.heap[index]
        ) {
            const parentIndex = this.getParentIndex(index);
            this.swap(index, parentIndex);
            index = parentIndex;
        }
    }

    // Sift down: move the root down to its correct position
    // 下濾：將根節點向下移動到正確位置
    private heapifyDown(): void {
        let index = 0;
        while (this.getLeftChildIndex(index) < this.heap.length) {
            let smallerChildIndex = this.getLeftChildIndex(index);
            const rightChildIndex = this.getRightChildIndex(index);

            // Check if right child exists and is smaller than left child
            // 檢查右子節點是否存在且比左子節點小
            if (
                rightChildIndex < this.heap.length &&
                this.heap[rightChildIndex] < this.heap[smallerChildIndex]
            ) {
                smallerChildIndex = rightChildIndex;
            }

            // If current element is smaller than the smallest child, we are done
            // 如果當前元素比最小的子節點還小，則完成
            if (this.heap[index] <= this.heap[smallerChildIndex]) {
                break;
            }

            this.swap(index, smallerChildIndex);
            index = smallerChildIndex;
        }
    }
}

/**
 * Solution for Kth Largest Element using MinHeap
 * 使用 MinHeap 解決第 K 大元素問題
 */
function findKthLargest(nums: number[], k: number): number {
    const minHeap = new MinHeap();

    for (const num of nums) {
        minHeap.push(num);
        
        // If heap size exceeds k, remove the smallest element
        // 如果堆積大小超過 k，移除最小的元素
        if (minHeap.size() > k) {
            minHeap.pop();
        }
    }

    // The root of the min-heap is the kth largest element
    // 最小堆積的根節點即為第 k 大的元素
    return minHeap.peek()!;
}

// Test / 測試
console.log(findKthLargest([3,2,1,5,6,4], 2)); // Output: 5
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Confusion (錯誤/混淆) | Correction (修正) |
| :--- | :--- | :--- |
| **Heap vs. BST** | Thinking Heap is sorted like a Binary Search Tree (left < root < right). / 認為 Heap 像二元搜尋樹一樣排序（左 < 根 < 右）。 | Heap only guarantees Root is min/max. Left child can be larger than right child. / Heap 只保證根是最小/最大。左子節點可以比右子節點大。 |
| **Array Representation** | Forgetting the index formula. / 忘記索引公式。 | Parent: $\lfloor (i-1)/2 \rfloor$, Left: $2i+1$, Right: $2i+2$. |
| **Space Complexity** | Thinking Heap Sort is always $O(N)$ space. / 認為 Heap Sort 總是 $O(N)$ 空間。 | It can be $O(1)$ if implemented in-place (modifying original array), but usually $O(N)$ in interview problems using a separate Heap class. / 若原地實作可為 $O(1)$，但在面試中使用獨立 Heap 類別通常為 $O(N)$。 |
| **Max vs Min** | Using a Max-Heap to find the $K$-th largest element. / 使用最大堆積尋找第 $K$ 大元素。 | While possible (pop $k-1$ times), Min-Heap of size $k$ is cleaner for streaming data. / 雖然可行（pop $k-1$ 次），但大小為 $k$ 的最小堆積對串流資料更簡潔。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Address the Language Limitation (解決語言限制)
Since you use TypeScript, start by saying:
"TypeScript doesn't have a built-in Priority Queue. Is it okay if I assume a `MinHeap` class exists, or should I implement a basic one first?"
「TypeScript 沒有內建的 Priority Queue。我可以假設有一個 `MinHeap` 類別可用嗎？還是我應該先實作一個基礎版本？」

### 2. Whiteboard Strategy (白板策略)
-   **Draw the Tree:** Even if you implement it with an array, draw the tree structure to visualize `sift-up` and `sift-down`.
    **畫出樹狀圖：** 即使你用陣列實作，畫出樹狀結構以視覺化 `sift-up` 和 `sift-down`。
-   **Trace with Example:** Use a small array (e.g., `[3, 1, 5]`) to trace the `push` logic.
    **用範例追蹤：** 使用小陣列（如 `[3, 1, 5]`）來追蹤 `push` 邏輯。

### 3. Common Follow-ups (常見追問)
-   **Q:** How to handle dynamic updates? (e.g., change priority of an item)
    **問：** 如何處理動態更新？（例如：改變項目的優先級）
    **A:** Standard heaps don't support efficient search. We need a `HashMap` to map values to heap indices to update in $O(\log N)$.
    **答：** 標準 Heap 不支援高效搜尋。我們需要一個 `HashMap` 將值映射到 Heap 索引，以便在 $O(\log N)$ 內更新。

---

## 7. Practice Problems (練習題)

### Easy: Last Stone Weight
**Problem:** You have stones with weights. Smash two heaviest. If $x == y$, both destroyed. If $x \neq y$, $y-x$ remains. Return last stone.
**問題：** 有一堆石頭。粉碎兩顆最重的。若 $x == y$，兩者皆毀。若 $x \neq y$，留下 $y-x$。回傳最後剩下的石頭。
-   **Hint:** Use a Max-Heap. Pop twice, push result back.
-   **提示：** 使用最大堆積。彈出兩次，將結果推回。

### Medium: K Closest Points to Origin
**Problem:** Find $K$ points closest to $(0,0)$.
**問題：** 找出距離 $(0,0)$ 最近的 $K$ 個點。
-   **Hint:** Calculate distance squared. Use a Max-Heap of size $K$. If new point is closer than the farthest in heap (root), replace it.
-   **提示：** 計算距離平方。使用大小為 $K$ 的最大堆積。若新點比堆積中最遠的點（根）更近，則替換之。

### Medium (Advanced for Beginner): Sort Characters By Frequency
**Problem:** Sort string based on character frequency.
**問題：** 根據字元頻率排序字串。
-   **Hint:** Count frequencies (Map). Push `(frequency, char)` into a Max-Heap. Pop and build string.
-   **提示：** 計算頻率（Map）。將 `(頻率, 字元)` 推入最大堆積。彈出並建構字串。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **Index Math:** Did I use `Math.floor` for the parent index? (Integer division).
    **索引數學：** 計算父節點索引時有用 `Math.floor` 嗎？（整數除法）。
-   [ ] **Empty Check:** Did I handle `pop` or `peek` on an empty heap?
    **空值檢查：** 有處理空堆積的 `pop` 或 `peek` 嗎？
-   [ ] **Comparison Logic:** Is it a Min-Heap (`<`) or Max-Heap (`>`)? Check the `if` conditions in `heapify`.
    **比較邏輯：** 是最小堆積（`<`）還是最大堆積（`>`）？檢查 `heapify` 中的 `if` 條件。
-   [ ] **Swap:** Did I implement the swap correctly?
    **交換：** 交換實作正確嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Corporate Hierarchy (企業階層) - Max Heap
-   **CEO (Root):** The highest paid/most powerful person is at the top.
    **CEO（根）：** 薪水最高/權力最大的人在頂端。
-   **Subordinates (Children):** Every manager is more powerful than their direct reports.
    **下屬（子節點）：** 每個經理都比他們的直接下屬權力大。
-   **No Order Between Siblings:** The VP of Sales isn't necessarily more powerful than the VP of Engineering; they just both report to the CEO.
    **手足間無順序：** 業務副總不一定比工程副總權力大；他們只是都向 CEO 匯報。

### The Emergency Room (急診室) - Priority Queue
-   Patients arrive randomly (Push).
    病患隨機到達（Push）。
-   The doctor always sees the most critical patient next, regardless of arrival time (Pop Max Priority).
    醫生總是接著看最危急的病患，不管到達時間為何（Pop Max Priority）。