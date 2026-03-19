Here is a comprehensive interview study guide for **Heap / Priority Queue**, tailored for a **Beginner** depth level (focusing on foundations and standard library usage), specifically designed for Senior Engineers using **Java**.

這是一份針對 **Heap（堆積）/ Priority Queue（優先佇列）** 的完整面試教材，深度設定為 **Beginner（基礎/入門）**（著重於觀念與標準函式庫應用），專為使用 **Java** 的資深工程師設計。

---

# Interview Guide: Heap & Priority Queue (Beginner)
# 面試指南：堆積與優先佇列（基礎篇）

## 1. Learning Objectives (學習目標)

*   **Understand the internal structure:** Comprehend how a Binary Heap works as a complete binary tree and satisfies the heap property.
    **理解內部結構：** 理解二元堆積（Binary Heap）如何作為完全二元樹運作，並滿足堆積屬性。
*   **Master Java's API:** Gain proficiency in using `java.util.PriorityQueue`, including custom Comparators.
    **掌握 Java API：** 熟練使用 `java.util.PriorityQueue`，包含自定義比較器（Comparators）。
*   **Analyze Complexity:** Clearly articulate the time complexity differences between Heaps ($O(\log N)$) and Sorting ($O(N \log N)$).
    **分析複雜度：** 清晰闡述堆積（$O(\log N)$）與排序（$O(N \log N)$）在時間複雜度上的差異。
*   **Identify "Top K" Patterns:** Recognize problems that require finding the $K^{th}$ largest/smallest elements efficiently.
    **識別「Top K」模式：** 辨識出需要高效找出第 $K$ 大/小元素的題型。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A **Heap** is a specialized tree-based data structure that satisfies the heap property: in a **Min-Heap**, the parent is always smaller than or equal to its children; in a **Max-Heap**, the parent is greater.
**堆積（Heap）** 是一種特殊的樹狀資料結構，滿足堆積屬性：在 **最小堆積（Min-Heap）** 中，父節點永遠小於或等於子節點；在 **最大堆積（Max-Heap）** 中，父節點則較大。

A **Priority Queue** is an abstract data type often implemented using a Heap, where elements are served based on priority rather than insertion order.
**優先佇列（Priority Queue）** 是一種抽象資料型別，通常使用堆積實作，元素是根據優先級而非插入順序被取出。

### Intuition (直覺)
Think of a Heap as a corporate hierarchy or a triage room in a hospital.
將堆積想像成公司階級制度或醫院的檢傷分類室。
It doesn't matter who arrived first; the person with the highest rank (or urgency) is processed next.
誰先到並不重要；職位最高（或最緊急）的人會被優先處理。

### Complexity (複雜度)

| Operation (操作) | Time Complexity (時間) | Note (備註) |
| :--- | :--- | :--- |
| **Offer / Add (新增)** | $O(\log N)$ | Needs to "bubble up" (sift up). 需「上浮」。 |
| **Poll / Remove Top (移除頂端)** | $O(\log N)$ | Needs to "bubble down" (heapify down). 需「下沉」。 |
| **Peek (查看頂端)** | $O(1)$ | Direct access to the root. 直接存取根節點。 |
| **Build Heap (建堆)** | $O(N)$ | Mathematically proven tighter bound than $O(N \log N)$. 數學上證明比 $O(N \log N)$ 更緊湊。 |
| **Remove Arbitrary (移除任意)** | $O(N)$ | Finding the element takes linear time in Java's PQ. 在 Java PQ 中尋找元素需線性時間。 |

### When to Use (適用場景)
*   Finding the **Top K** elements (largest/smallest/most frequent).
    尋找 **前 K 個** 元素（最大/最小/最頻繁）。
*   Access to the min/max element is needed repeatedly while data changes.
    在數據變動的同時，需要反覆存取最小/最大值。
*   Merging multiple sorted streams (e.g., Merge K Sorted Lists).
    合併多個已排序的串流（例如：合併 K 個排序鏈結串列）。

### When NOT to Use (不適用場景)
*   Searching for a specific value (use Hash Map or BST).
    搜尋特定值（應使用雜湊表或二元搜尋樹）。
*   Need output in fully sorted order (just use Sorting, unless $K \ll N$).
    需要完全排序的輸出（直接使用排序，除非 $K$ 遠小於 $N$）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Top K Elements (Static or Streaming)
**模式一：前 K 個元素（靜態或串流）**
Use a Min-Heap of size $K$ to find the $K$ largest elements.
使用大小為 $K$ 的最小堆積來尋找前 $K$ 大的元素。
*   *Why?* If the heap exceeds size $K$, remove the smallest. The remaining $K$ are the largest seen so far.
*   *為何？* 若堆積超過大小 $K$，移除最小的。剩下的 $K$ 個即為目前為止最大的。

### Pattern 2: Merge K Sorted Resources
**模式二：合併 K 個排序資源**
Push the first element of each list into a Min-Heap.
將每個列表的第一個元素放入最小堆積。
Always pop the smallest, then push the next element from the same list into the heap.
總是取出最小的，然後將該元素所屬列表的下一個元素放入堆積。

---

## 4. Example Walkthrough (範例講解)

### Problem: Kth Largest Element in an Array
### 問題：陣列中第 K 大的元素

**Problem Statement (問題重述):**
Given an integer array `nums` and an integer `k`, return the $k^{th}$ largest element in the array.
給定一個整數陣列 `nums` 和一個整數 `k`，回傳陣列中第 $k$ 大的元素。

**Approach 1: Brute Force (Sorting)**
**思路 1：暴力法（排序）**
Sort the entire array descending and take index $k-1$.
將整個陣列降序排序，取索引 $k-1$。
*   Time: $O(N \log N)$
*   Space: $O(1)$ or $O(\log N)$ depending on sort implementation.

**Approach 2: Min-Heap (Optimal for this level)**
**思路 2：最小堆積（本階段最佳解）**
Maintain a Min-Heap of size $K$.
維護一個大小為 $K$ 的最小堆積。
Iterate through the array. Add numbers to the heap.
遍歷陣列。將數字加入堆積。
If the heap size exceeds $K$, remove the smallest element (the root).
若堆積大小超過 $K$，移除最小的元素（根節點）。
At the end, the root of the heap is the $K^{th}$ largest element.
最後，堆積的根節點即為第 $K$ 大的元素。
*   Time: $O(N \log K)$ — Better than sorting when $K < N$.
*   Space: $O(K)$ — To store the heap.

**Java Reference Solution (Java 參考解):**

```java
import java.util.PriorityQueue;

public class KthLargest {
    public int findKthLargest(int[] nums, int k) {
        // Create a Min-Heap (default in Java)
        // 建立一個最小堆積（Java 預設即為最小堆積）
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();

        for (int num : nums) {
            // Add current number to the heap
            // 將當前數字加入堆積
            minHeap.offer(num);

            // If heap size exceeds k, remove the smallest element
            // because it cannot be among the top k largest.
            // 若堆積大小超過 k，移除最小的元素，
            // 因為它不可能是前 k 大的元素之一。
            if (minHeap.size() > k) {
                minHeap.poll();
            }
        }

        // The root of the min-heap is the kth largest element
        // 最小堆積的根節點即為第 k 大的元素
        return minHeap.peek();
    }
}
```

**Common Mistake (錯誤示範):**
Using a **Max-Heap** of size $N$ and popping $K-1$ times.
使用大小為 $N$ 的 **最大堆積** 並彈出 $K-1$ 次。
*   *Why is this suboptimal?* It requires $O(N)$ space and building the heap takes $O(N)$, but popping $K$ times costs $O(K \log N)$. While valid, the Min-Heap approach ($O(N \log K)$) is generally preferred for streaming data or when memory is constrained ($O(K)$ space).
*   *為何次佳？* 這需要 $O(N)$ 空間，建堆需 $O(N)$，彈出 $K$ 次需 $O(K \log N)$。雖然可行，但最小堆積法（$O(N \log K)$）在處理串流數據或記憶體受限時（$O(K)$ 空間）通常更佳。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Clarification (陷阱 / 釐清) |
| :--- | :--- |
| **Default Order (預設順序)** | Java `PriorityQueue` is a **Min-Heap**. Python `heapq` is Min-Heap. C++ `priority_queue` is **Max-Heap**. <br> Java `PriorityQueue` 是 **最小堆積**。Python 也是。但 C++ 是 **最大堆積**。 |
| **Kth Largest vs. Smallest** | To find $K^{th}$ **Largest**, use a **Min-Heap** (keep the large ones, discard smalls). <br> To find $K^{th}$ **Smallest**, use a **Max-Heap** (keep the small ones, discard larges). <br> 找第 $K$ **大**，用 **最小堆積**。找第 $K$ **小**，用 **最大堆積**。 |
| **Remove Object** | `pq.remove(object)` is $O(N)$, not $O(\log N)$. It requires scanning the array. <br> `pq.remove(object)` 是 $O(N)$，而非 $O(\log N)$。它需要掃描陣列。 |
| **Array to Heap** | Passing a collection to the constructor `new PriorityQueue<>(list)` is $O(N)$ (heapify), not $O(N \log N)$. <br> 將集合傳入建構子 `new PriorityQueue<>(list)` 是 $O(N)$（建堆），而非 $O(N \log N)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the property:** "Since we need the $K$ largest items, strict ordering isn't necessary, just the boundary. A Heap is perfect here."
    **確認性質：** 「因為我們需要前 $K$ 大的項目，不需要嚴格排序，只需知道邊界。堆積在這裡非常適合。」
2.  **Discuss Trade-offs:** "Sorting takes $O(N \log N)$. Using a Heap reduces this to $O(N \log K)$, which is significant if $K$ is small relative to $N$."
    **討論權衡：** 「排序需要 $O(N \log N)$。使用堆積將其降低為 $O(N \log K)$，若 $K$ 遠小於 $N$ 這差異很顯著。」

### Whiteboard Strategy (白板策略)
*   **Don't implement Heap from scratch:** Unless explicitly asked, assume `PriorityQueue` exists.
    **不要從頭實作堆積：** 除非被明確要求，否則假設 `PriorityQueue` 已存在。
*   **Syntax Check:** Remember how to write a reverse comparator for Max-Heap in Java: `(a, b) -> b - a` or `Collections.reverseOrder()`.
    **語法檢查：** 記住如何在 Java 中撰寫最大堆積的反向比較器：`(a, b) -> b - a` 或 `Collections.reverseOrder()`。

### Common Follow-ups (常見追問)
*   **Q:** What if the array is too large to fit in memory (External Sort)?
    **問：** 如果陣列太大無法放入記憶體怎麼辦（外部排序）？
    *   **A:** We can stream the data. The Heap only needs to store $K$ elements in memory at a time.
    *   **答：** 我們可以串流處理數據。堆積一次只需要在記憶體中儲存 $K$ 個元素。

---

## 7. Practice Problems (練習題)

### 1. Easy: Last Stone Weight
*   **Prompt:** Smash two heaviest stones together. If $x \neq y$, the stone $y-x$ remains. Return the last stone.
    **題目：** 將兩顆最重的石頭互砸。若 $x \neq y$，留下 $y-x$ 的石頭。回傳最後剩下的石頭。
*   **Hint:** You always need the *heaviest* two. Use a Max-Heap.
    **提示：** 你總是需要 *最重* 的兩顆。使用最大堆積。
*   **Solution Logic:** `PriorityQueue<Integer> pq = new PriorityQueue<>((a, b) -> b - a);` Loop while size > 1.

### 2. Medium: K Closest Points to Origin
*   **Prompt:** Find $K$ points closest to $(0,0)$.
    **題目：** 找出距離 $(0,0)$ 最近的 $K$ 個點。
*   **Hint:** We want the $K$ *smallest* distances. Use a Max-Heap of size $K$ to keep track of the closest, ejecting the farthest when capacity is exceeded.
    **提示：** 我們想要 $K$ 個 *最小* 的距離。使用大小為 $K$ 的最大堆積來追蹤最近的點，當容量超過時彈出最遠的。
*   **Solution Logic:** Store objects/arrays in PQ. Comparator calculates Euclidean distance.

### 3. Medium/Hard: Merge k Sorted Lists
*   **Prompt:** Merge $k$ linked lists that are already sorted.
    **題目：** 合併 $k$ 個已排序的鏈結串列。
*   **Hint:** The smallest head among all lists is the next node in the result.
    **提示：** 所有串列中最小的頭節點即為結果中的下一個節點。
*   **Solution Logic:** Add all `head` nodes to a Min-Heap. Poll the smallest, add to result, then push `node.next` into the Heap.

---

## 8. Rapid Checklist (快速檢核表)

*   [ ] **Import:** Did I import `java.util.PriorityQueue`?
    **引入：** 我是否引入了 `java.util.PriorityQueue`？
*   [ ] **Direction:** Is it a Min-Heap (default) or Max-Heap? Did I write the comparator correctly?
    **方向：** 這是最小堆積（預設）還是最大堆積？比較器寫對了嗎？
*   [ ] **Empty Check:** Did I handle the case where the queue is empty before calling `poll()` or `peek()`? (Though `poll` returns null, `remove` throws exception).
    **空檢查：** 在呼叫 `poll()` 或 `peek()` 之前是否處理了佇列為空的情況？（雖然 `poll` 回傳 null，但 `remove` 會拋出異常）。
*   [ ] **Complexity:** Is my complexity $O(N \log K)$ or $O(N \log N)$? Did I justify the choice?
    **複雜度：** 我的複雜度是 $O(N \log K)$ 還是 $O(N \log N)$？我有解釋選擇的原因嗎？

---

## 9. Memory Anchors (記憶錨點)

### The "VIP Club" Analogy (「VIP 俱樂部」類比)
*   **Min-Heap for Top K Largest:** Imagine a VIP club with a capacity of $K$.
    **最小堆積求前 K 大：** 想像一個容量為 $K$ 的 VIP 俱樂部。
*   To ensure the club only has the *richest* people, who do you kick out when a new person enters?
    為了確保俱樂部裡只有 *最富有* 的人，當新人進來時你要踢掉誰？
*   You kick out the **poorest** person inside the club (the Min).
    你會踢掉俱樂部裡 **最窮** 的人（最小值）。
*   Therefore, use a **Min-Heap** to maintain the **Largest** elements.
    因此，使用 **最小堆積** 來維護 **最大** 的元素群。

### Visual Anchor (圖像錨點)
*   **Triangle/Pyramid:** The top is always the extreme (smallest or largest). You can't see what's deep inside the bottom quickly, but you always know who the "King" is at the top.
    **三角形/金字塔：** 頂端永遠是極值（最小或最大）。你無法快速看到底部深處有什麼，但你永遠知道頂端的「國王」是誰。