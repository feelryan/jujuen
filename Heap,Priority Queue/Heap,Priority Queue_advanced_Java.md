Here is the comprehensive guide for **Heap / Priority Queue** at an **Advanced** level, tailored for a Senior Software Engineer.

---

# Advanced Data Structures: Heap & Priority Queue
# 進階資料結構：堆積與優先佇列

## 1. Learning Objectives (學習目標)

1.  **Master Internal Mechanics & Array Representation**: Understand how binary heaps map to arrays and the mathematics of index manipulation (parent/child relationships) to implement custom heaps when standard libraries fall short.
    **掌握內部機制與陣列表示法**：理解二元堆積如何映射至陣列，以及索引操作的數學原理（父/子節點關係），以便在標準庫不足時實作客製化堆積。

2.  **Optimize "Arbitrary Removal" with Lazy Deletion**: Learn to bypass the $O(N)$ limitation of Java's `PriorityQueue.remove()` by implementing the "Lazy Deletion" pattern, crucial for advanced sliding window or interval problems.
    **透過延遲刪除優化「任意移除」**：學習實作「延遲刪除」模式，以繞過 Java `PriorityQueue.remove()` 的 $O(N)$ 限制，這對進階滑動視窗或區間問題至關重要。

3.  **Dominate Multi-Heap Patterns**: Gain fluency in using multiple heaps simultaneously (e.g., Two Heaps for Median, K-way Merge) to solve complex streaming data problems.
    **精通多堆積模式**：熟練同時使用多個堆積（例如：雙堆積求中位數、K 路合併）來解決複雜的串流資料問題。

4.  **System Design Bridging**: Connect local heap usage to distributed system concepts, such as Log-Structured Merge Trees (LSM) or Timer Wheel implementations vs. Priority Queues.
    **系統設計銜接**：將本地堆積的使用連結至分散式系統概念，例如日誌結構合併樹（LSM）或時間輪實作與優先佇列的對比。

---

## 2. Core Concepts & Deep Dive (核心觀念與深度剖析)

### Definition & Intuition (定義與直覺)
A Heap is a specialized tree-based data structure that satisfies the heap property: in a max-heap, for any given node I, the value of I is greater than or equal to the values of its children.
堆積是一種特殊的樹狀資料結構，滿足堆積性質：在最大堆積中，對於任意節點 I，I 的值皆大於或等於其子節點的值。

It is almost always implemented as an array (Complete Binary Tree) to ensure cache locality and memory efficiency.
它幾乎總是以陣列（完全二元樹）的形式實作，以確保快取局部性與記憶體效率。

### Complexity Analysis (複雜度分析)

| Operation | Time Complexity | Note (註記) |
| :--- | :--- | :--- |
| **Offer (Insert)** | $O(\log N)$ | Sift-up (Bubble-up) process. <br> 上濾（上浮）過程。 |
| **Poll (Extract Top)** | $O(\log N)$ | Swap root with last, remove last, Sift-down. <br> 交換根與末尾，移除末尾，下濾。 |
| **Peek (Top)** | $O(1)$ | Direct array access at index 0. <br> 直接存取陣列索引 0。 |
| **Heapify (Build)** | $O(N)$ | **Not $O(N \log N)$.** Building from an array is linear. <br> **非 $O(N \log N)$。** 從陣列建堆是線性的。 |
| **Remove (Arbitrary)**| $O(N)$ (Java) | Java's `remove(Object o)` scans the array linearly. <br> Java 的 `remove(Object o)` 會線性掃描陣列。 |

### When to Use (適用場景)
- **Continuous Extreme Value**: You need constant access to the min or max element in a dynamic dataset.
  **持續極值**：你需要持續存取動態資料集中的最小值或最大值。
- **K-th Element Problems**: Finding the top K elements in a stream or static set.
  **第 K 個元素問題**：在串流或靜態集合中尋找前 K 個元素。
- **Graph Algorithms**: Dijkstra’s (Shortest Path) and Prim’s (MST).
  **圖演算法**：Dijkstra（最短路徑）與 Prim（最小生成樹）。

### When NOT to Use (不適用場景)
- **Searching**: Finding an arbitrary element is $O(N)$. Use a Hash Map or BST instead.
  **搜尋**：尋找任意元素需 $O(N)$。應改用雜湊表或二元搜尋樹。
- **Ordered Iteration**: A heap is not sorted; it only guarantees the root is the extreme.
  **有序迭代**：堆積並未排序；它僅保證根節點為極值。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Top-K Elements (Static & Streaming)**
    -   Use a Min-Heap of size K to keep the largest K elements.
    -   使用大小為 K 的最小堆積來保留最大的 K 個元素。
2.  **K-Way Merge**
    -   Merging K sorted lists/arrays using a Min-Heap to track the current smallest head among all lists.
    -   使用最小堆積追蹤所有列表中當前最小的頭部元素，以合併 K 個已排序列表/陣列。
3.  **Two Heaps (Median Finding)**
    -   Maintain a Max-Heap (left half) and a Min-Heap (right half) to find the median in $O(1)$.
    -   維護一個最大堆積（左半部）與一個最小堆積（右半部），以便在 $O(1)$ 時間內找到中位數。
4.  **Lazy Deletion (Advanced)**
    -   Instead of removing an element immediately ($O(N)$), mark it as invalid (e.g., using a HashMap counter) and discard it only when it reaches the top of the heap.
    -   不立即移除元素（$O(N)$），而是將其標記為無效（例如使用 HashMap 計數器），僅當該元素到達堆積頂端時才將其丟棄。

---

## 4. Example Walkthrough (範例講解)

### Problem: Sliding Window Median (LC 480) - Hard
**問題重述**：
Given an array `nums` and an integer `k`, there is a sliding window of size `k` moving from the very left of the array to the very right. You need to return the median array for each window position.
給定一個陣列 `nums` 和一個整數 `k`，有一個大小為 `k` 的滑動視窗從陣列的最左側移動到最右側。你需要回傳每個視窗位置的中位數陣列。

### Approach (思路)

1.  **Brute Force (暴力法)**:
    -   Extract window, sort it ($O(K \log K)$), pick median. Total: $O((N-K) \cdot K \log K)$. Too slow.
    -   提取視窗，排序（$O(K \log K)$），選取中位數。總計：$O((N-K) \cdot K \log K)$。太慢。

2.  **Intermediate (Two Heaps with Standard Removal)**:
    -   Use Max-Heap (small half) and Min-Heap (large half).
    -   Add new element, remove old element as window slides.
    -   **Issue**: `pq.remove(element)` in Java is $O(K)$. Total: $O(N \cdot K)$. Acceptable but not optimal for very large K.
    -   **問題**：Java 中的 `pq.remove(element)` 是 $O(K)$。總計：$O(N \cdot K)$。可接受但對非常大的 K 來說並非最佳。

3.  **Advanced (Two Heaps with Lazy Deletion)**:
    -   Use a Hash Map to record elements that *should* be deleted but are still in the heap.
    -   Only physically `poll()` from heaps when the top element is "stale" (marked for deletion).
    -   Balance the heaps by tracking the *valid* size, not just `pq.size()`.
    -   Time Complexity: Amortized $O(N \log K)$.
    -   使用雜湊表記錄*應該*被刪除但仍在堆積中的元素。
    -   僅當堆積頂端元素為「過期」（標記為刪除）時，才物理性地執行 `poll()`。
    -   透過追蹤*有效*大小而非僅 `pq.size()` 來平衡堆積。
    -   時間複雜度：均攤 $O(N \log K)$。

### Java Reference Solution (Advanced: Lazy Deletion)

```java
import java.util.*;

public class SlidingWindowMedian {
    // Max-heap for the smaller half of numbers
    // 用於儲存較小一半數字的最大堆積
    private PriorityQueue<Integer> smallHalf;
    
    // Min-heap for the larger half of numbers
    // 用於儲存較大一半數字的最小堆積
    private PriorityQueue<Integer> largeHalf;
    
    // Map to keep track of numbers to be removed (Lazy Deletion)
    // 用於追蹤待移除數字的 Map（延遲刪除）
    // Key: number, Value: count of pending removals
    private Map<Integer, Integer> staleElements;
    
    // Actual count of valid elements in heaps
    // 堆積中有效元素的實際數量
    private int smallSize;
    private int largeSize;

    public double[] medianSlidingWindow(int[] nums, int k) {
        // Initialize structures
        // 初始化結構
        smallHalf = new PriorityQueue<>(Collections.reverseOrder()); // Max Heap
        largeHalf = new PriorityQueue<>(); // Min Heap
        staleElements = new HashMap<>();
        smallSize = 0;
        largeSize = 0;

        double[] result = new double[nums.length - k + 1];
        int r = 0;

        // Initialize first window
        // 初始化第一個視窗
        for (int i = 0; i < k; i++) {
            add(nums[i]);
        }
        result[r++] = getMedian(k);

        // Slide the window
        // 滑動視窗
        for (int i = k; i < nums.length; i++) {
            // Remove the element going out of window (Lazy)
            // 移除滑出視窗的元素（延遲）
            int outNum = nums[i - k];
            remove(outNum);
            
            // Add the new element coming into window
            // 加入滑入視窗的新元素
            int inNum = nums[i];
            add(inNum);
            
            result[r++] = getMedian(k);
        }

        return result;
    }

    private void add(int num) {
        // Always add to smallHalf first, then balance
        // 總是先加入 smallHalf，然後平衡
        if (smallHalf.isEmpty() || num <= smallHalf.peek()) {
            smallHalf.offer(num);
            smallSize++;
        } else {
            largeHalf.offer(num);
            largeSize++;
        }
        rebalance();
    }

    private void remove(int num) {
        // Mark for deletion
        // 標記為刪除
        staleElements.put(num, staleElements.getOrDefault(num, 0) + 1);
        
        // Decrement logical size
        // 減少邏輯大小
        if (!smallHalf.isEmpty() && num <= smallHalf.peek()) {
            smallSize--;
        } else {
            largeSize--;
        }
        // Prune stale elements from tops and rebalance
        // 清除堆頂的過期元素並重新平衡
        prune(smallHalf);
        prune(largeHalf);
        rebalance();
    }

    private void prune(PriorityQueue<Integer> pq) {
        // Remove elements from top if they are in the stale map
        // 若堆頂元素在過期 map 中，則將其移除
        while (!pq.isEmpty() && staleElements.containsKey(pq.peek())) {
            int top = pq.peek();
            int count = staleElements.get(top);
            if (count == 1) {
                staleElements.remove(top);
            } else {
                staleElements.put(top, count - 1);
            }
            pq.poll(); // Physically remove
        }
    }

    private void rebalance() {
        // Maintain property: smallSize == largeSize OR smallSize == largeSize + 1
        // 維護性質：smallSize 等於 largeSize 或 smallSize 等於 largeSize + 1
        if (smallSize > largeSize + 1) {
            largeHalf.offer(smallHalf.poll());
            smallSize--;
            largeSize++;
            prune(smallHalf); // Prune after moving
        } else if (smallSize < largeSize) {
            smallHalf.offer(largeHalf.poll());
            largeSize--;
            smallSize++;
            prune(largeHalf); // Prune after moving
        }
    }

    private double getMedian(int k) {
        if (k % 2 == 1) {
            return (double) smallHalf.peek();
        } else {
            // Be careful with integer overflow
            // 注意整數溢位
            return ((double) smallHalf.peek() + (double) largeHalf.peek()) / 2.0;
        }
    }
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Clarification (陷阱 / 釐清) |
| :--- | :--- |
| **Java `remove(Object)`** | **Trap**: It is $O(N)$, not $O(\log N)$. It requires a linear scan to find the object. <br> **陷阱**：它是 $O(N)$，而非 $O(\log N)$。它需要線性掃描來找到該物件。 |
| **Comparator Logic** | `(a, b) -> a - b` (Min-Heap) vs `(a, b) -> b - a` (Max-Heap). Watch out for integer overflow if using subtraction! Use `Integer.compare(a, b)`. <br> `(a, b) -> a - b`（最小堆）vs `(a, b) -> b - a`（最大堆）。若使用減法請小心整數溢位！應使用 `Integer.compare(a, b)`。 |
| **Modifying Elements** | Never modify the value of an object *while* it sits inside the Heap. The Heap invariant will break, and the object may become irretrievable. <br> 絕不要在物件位於堆積*內部*時修改其值。堆積不變性將被破壞，且該物件可能無法被檢索。 |
| **Array to Heap** | Building a heap one by one is $O(N \log N)$. Using `heapify` (passing collection to constructor) is $O(N)$. <br> 逐一建堆是 $O(N \log N)$。使用 `heapify`（傳遞集合給建構子）是 $O(N)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Identify the Property**: "Since we need to constantly access the smallest/largest element while data is changing, a Heap is appropriate."
    **識別性質**：「由於我們需要在資料變動時持續存取最小/最大元素，堆積是合適的選擇。」
2.  **Discuss Trade-offs**: "Standard removal is $O(N)$. I can optimize this to $O(\log N)$ using Lazy Deletion or by using a TreeMap (if language allows), but Heap has better constant factors."
    **討論權衡**：「標準移除是 $O(N)$。我可以使用延遲刪除或 TreeMap（若語言允許）將其優化為 $O(\log N)$，但堆積擁有較佳的常數因子。」
3.  **Complexity Check**: Explicitly state $O(N \log K)$ vs $O(N \log N)$.

### Whiteboard Strategy (白板策略)
-   **Visualize**: Draw the tree structure for small examples, but use the array representation `[0, 1, 2...]` to debug index logic if implementing from scratch.
    **視覺化**：為小範例畫出樹狀結構，但若從頭實作，請使用陣列表示法 `[0, 1, 2...]` 來除錯索引邏輯。
-   **Variable Naming**: Use `minHeap`/`maxHeap` instead of `pq1`/`pq2`. Clear naming saves explanation time.
    **變數命名**：使用 `minHeap`/`maxHeap` 代替 `pq1`/`pq2`。清晰的命名節省解釋時間。

### Common Follow-ups (常見追問)
-   **Q**: How to implement a Priority Queue that supports efficient update of priorities?
    **問**：如何實作一個支援高效更新優先級的優先佇列？
    -   **A**: Use an **Indexed Priority Queue** (hash map mapping value to array index) to allow $O(\log N)$ updates. (Common in Dijkstra implementations).
    -   **答**：使用**索引優先佇列**（雜湊表將值映射至陣列索引）以允許 $O(\log N)$ 更新。（常見於 Dijkstra 實作）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Kth Largest Element in a Stream (LC 703)
-   **Goal**: Design a class to find the kth largest element in a stream.
    **目標**：設計一個類別以在串流中尋找第 k 大的元素。
-   **Hint**: Keep a Min-Heap of size K. The root is always the Kth largest.
    **提示**：保留一個大小為 K 的最小堆積。根節點永遠是第 K 大的元素。

### 2. Medium: Task Scheduler (LC 621)
-   **Goal**: Schedule tasks with cooling intervals to minimize total time.
    **目標**：在有冷卻區間的情況下排程任務，以最小化總時間。
-   **Hint**: Greedy approach. Always pick the most frequent task available. Use a Max-Heap to store frequencies and a Queue to handle cooling logic.
    **提示**：貪婪法。總是選取當前頻率最高的任務。使用最大堆積儲存頻率，並使用佇列處理冷卻邏輯。

### 3. Hard: IPO (LC 502)
-   **Goal**: Maximize capital by selecting at most k distinct projects.
    **目標**：透過選取最多 k 個不同的專案來最大化資本。
-   **Hint**: Two data structures. Sort projects by capital (or put in Min-Heap). Move affordable projects to a Max-Heap (based on profit). Always pick from Max-Heap.
    **提示**：兩個資料結構。依資本排序專案（或放入最小堆積）。將可負擔的專案移至最大堆積（基於利潤）。總是從最大堆積選取。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
-   [ ] Did I handle the case where `k > nums.length`? (If applicable)
    我是否處理了 `k > nums.length` 的情況？（若適用）
-   [ ] Did I use `Collections.reverseOrder()` for Max-Heap in Java?
    我是否在 Java 中使用 `Collections.reverseOrder()` 來建立最大堆積？
-   [ ] If using custom objects, did I implement `Comparable` or provide a `Comparator`?
    若使用自訂物件，我是否實作了 `Comparable` 或提供 `Comparator`？
-   [ ] **Complexity**: Did I mistake `remove()` for $O(\log N)$?
    **複雜度**：我是否誤將 `remove()` 當作 $O(\log N)$？

### Debugging (除錯)
-   [ ] **Infinite Loop**: Check if your `while` loop for lazy deletion correctly updates the map/counter.
    **無窮迴圈**：檢查延遲刪除的 `while` 迴圈是否正確更新了 map/計數器。
-   [ ] **NullPointerException**: `pq.poll()` returns null if empty. Do not unbox directly to `int`.
    **NullPointerException**：若為空，`pq.poll()` 回傳 null。不要直接拆箱為 `int`。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "VIP Club Bouncer" (VIP 俱樂部保鑣)
-   **Concept**: Top-K Pattern.
-   **Analogy**: The club only holds K people (Min-Heap of size K). When a new person arrives, if they are richer (larger) than the poorest person inside (root), the bouncer kicks the poorest out and lets the new person in.
    **類比**：俱樂部只能容納 K 人（大小為 K 的最小堆積）。當新人到達時，若他比裡面最窮的人（根節點）富有（數值更大），保鑣就會把最窮的人踢出去，讓新人進來。

### The "Pyramid of Power" (權力金字塔)
-   **Concept**: Heap Property.
-   **Analogy**: The boss (root) is always more powerful than subordinates (children). However, the "left manager" isn't necessarily stronger than the "right manager". There is no horizontal ordering, only vertical dominance.
    **類比**：老闆（根節點）總是比下屬（子節點）更有權力。然而，「左經理」不一定比「右經理」強。這裡沒有水平排序，只有垂直支配。