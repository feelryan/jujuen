Here is the comprehensive guide for **Heap / Priority Queue**, tailored for a Senior Software Engineer targeting Big Tech roles.
這是一份針對 **Heap / Priority Queue（堆積 / 優先佇列）** 的完整指南，專為目標 Big Tech 職位的資深軟體工程師量身打造。

---

# Heap & Priority Queue: Intermediate Guide
# 堆積與優先佇列：中階指南

## 1. Learning Objectives (學習目標)

*   **Master Java’s `PriorityQueue` API and Custom Comparators.**
    掌握 Java `PriorityQueue` API 及其自定義比較器（Comparator）的寫法。
*   **Distinguish between "Top K" (Static) and "Stream" scenarios.**
    區分「Top K」（靜態數據）與「串流數據」場景的差異。
*   **Understand the trade-off: Heap ($O(N \log K)$) vs. Sorting ($O(N \log N)$) vs. QuickSelect ($O(N)$).**
    理解權衡：堆積 ($O(N \log K)$) vs. 排序 ($O(N \log N)$) vs. 快速選擇 ($O(N)$)。
*   **Apply the "Two Heaps" pattern for median finding.**
    應用「雙堆積」模式來解決中位數查找問題。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition (定義)
A Heap is a specialized tree-based data structure that satisfies the heap property: in a **Min-Heap**, for any given node $I$, the value of $I$ is less than or equal to the values of its children.
堆積是一種特殊的樹狀資料結構，滿足堆積性質：在 **最小堆積（Min-Heap）** 中，對於任意節點 $I$，其值皆小於或等於其子節點的值。

In Java, `java.util.PriorityQueue` is implemented as a priority heap.
在 Java 中，`java.util.PriorityQueue` 是以優先堆積實作的。

### Intuition (直覺)
Think of a Heap as a "VIP Line" where the most important element (min or max) is always at the front, ready to be served immediately.
將堆積想像成一條「VIP 通道」，最重要（最小或最大）的元素永遠排在最前面，隨時準備被處理。

### Complexity (複雜度)

| Operation (操作) | Time Complexity (時間複雜度) | Note (備註) |
| :--- | :--- | :--- |
| **Peek (Top)** | $O(1)$ | Instant access to extremum (極值即時存取) |
| **Add (Offer)** | $O(\log N)$ | Sift up (上濾) |
| **Poll (Remove Top)** | $O(N)$ or $O(\log N)$ | $O(\log N)$ standard; Java `remove(Object)` is $O(N)$ (標準移除為對數級；Java 指定物件移除為線性級) |
| **Build Heap** | $O(N)$ | Linear time if built from array (若從陣列建構則為線性時間) |

### When to Use (適用場景)
1.  **Top K Elements:** Finding the K largest/smallest items.
    **Top K 元素：** 尋找第 K 個最大或最小的項目。
2.  **Streaming Data:** You need continuous access to the min/max as data flows in.
    **串流數據：** 當數據持續流入時，你需要持續存取最大或最小值。
3.  **Merge K Sorted Arrays/Lists:** Efficiently combining sorted inputs.
    **合併 K 個已排序陣列/鏈結串列：** 有效率地合併已排序的輸入。

### When NOT to Use (不適用場景)
1.  **Searching for an arbitrary element:** Heaps are not optimized for search ($O(N)$).
    **搜尋任意元素：** 堆積並未針對搜尋做優化（$O(N)$）。
2.  **Sorted output required immediately:** If you need the whole list sorted, just use Sort ($O(N \log N)$) or TreeMap.
    **需要立即的排序輸出：** 如果你需要整個列表是排序好的，直接使用排序 ($O(N \log N)$) 或 TreeMap。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Top K Elements (Top K 元素)
Keep a Min-Heap of size $K$. If a new element is larger than the heap's root, pop the root and push the new element.
維護一個大小為 $K$ 的最小堆積。如果新元素比堆積的根節點大，則彈出根節點並推入新元素。
*   *Result:* The heap contains the $K$ largest elements.
*   *結果：* 堆積中保留了 $K$ 個最大的元素。

### B. Merge K Sorted Lists (合併 K 個排序串列)
Push the head of each list into a Min-Heap. Poll the smallest, add it to the result, and push the next node from that specific list.
將每個串列的頭節點推入最小堆積。取出最小的節點，加入結果，並將該串列的下一個節點推入堆積。

### C. Two Heaps (雙堆積)
Maintain a Max-Heap for the lower half of numbers and a Min-Heap for the upper half to find the **Median** in $O(1)$.
維護一個最大堆積存放較小的一半數字，以及一個最小堆積存放較大的一半數字，以便在 $O(1)$ 時間內找到**中位數**。

---

## 4. Example Walkthrough (範例講解)

### Problem: Merge K Sorted Lists (合併 K 個排序鏈結串列)
**LeetCode 23 (Hard)**

#### Problem Statement (問題重述)
You are given an array of `k` linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.
給定一個包含 `k` 個鏈結串列的陣列，每個鏈結串列皆已按升序排序。將所有鏈結串列合併為一個排序的鏈結串列並返回。

#### Approach Evolution (思路演進)

1.  **Brute Force (暴力法):**
    *   Put all nodes into a list, sort them, and rebuild the linked list.
    *   將所有節點放入一個列表，進行排序，然後重建鏈結串列。
    *   *Complexity:* $O(N \log N)$ where $N$ is total nodes. Space $O(N)$.
    *   *複雜度：* $O(N \log N)$，其中 $N$ 為總節點數。空間 $O(N)$。

2.  **Pairwise Merge (兩兩合併):**
    *   Merge list 1 and 2, then result with 3, etc.
    *   合併串列 1 和 2，然後將結果與 3 合併，依此類推。
    *   *Complexity:* $O(kN)$. Inefficient for large $k$.
    *   *複雜度：* $O(kN)$。對於大的 $k$ 效率低落。

3.  **Optimal: Min-Heap (最佳解：最小堆積):**
    *   Since lists are sorted, the global minimum must be one of the heads of the $k$ lists.
    *   因為串列已排序，全域最小值必定是這 $k$ 個串列頭部的其中之一。
    *   Use a Min-Heap to track the current head of each list.
    *   使用最小堆積來追蹤每個串列當前的頭部。
    *   *Complexity:* Time $O(N \log k)$, Space $O(k)$.
    *   *複雜度：* 時間 $O(N \log k)$，空間 $O(k)$。

#### Java Reference Solution (Java 參考解)

```java
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
import java.util.PriorityQueue;

class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        // Edge case: empty input
        // 邊界條件：輸入為空
        if (lists == null || lists.length == 0) return null;

        // Min-Heap to store ListNodes, sorted by value
        // 最小堆積儲存 ListNode，依據數值排序
        // Note: Since Java 8, we can use lambda for Comparator
        // 註：自 Java 8 起，我們可以使用 lambda 表達式作為比較器
        PriorityQueue<ListNode> minHeap = new PriorityQueue<>((a, b) -> a.val - b.val);

        // Initialize heap with the head of each non-null list
        // 將每個非空串列的頭節點初始化入堆積
        for (ListNode node : lists) {
            if (node != null) {
                minHeap.offer(node);
            }
        }

        // Dummy head to simplify result list construction
        // 虛擬頭節點（Dummy head）以簡化結果串列的建構
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;

        // Process the heap until empty
        // 處理堆積直到為空
        while (!minHeap.isEmpty()) {
            // Extract the smallest node
            // 取出最小節點
            ListNode smallest = minHeap.poll();
            
            // Append to result list
            // 接到結果串列後
            current.next = smallest;
            current = current.next;

            // If there is a next node in the extracted list, push it to heap
            // 若取出的節點所在串列還有下一個節點，將其推入堆積
            if (smallest.next != null) {
                minHeap.offer(smallest.next);
            }
        }

        return dummy.next;
    }
}
```

#### Why this works (為何有效)
At any point, the heap size is at most $k$. Insertions and deletions take $O(\log k)$. We do this for every node ($N$ times).
在任何時間點，堆積大小最多為 $k$。插入與刪除耗時 $O(\log k)$。我們對每個節點執行此操作（共 $N$ 次）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

### A. Max-Heap vs. Min-Heap in Java (Java 中的最大堆與最小堆)
*   **Default:** `PriorityQueue` is a **Min-Heap**.
    **預設：** `PriorityQueue` 是 **最小堆積**。
*   **Trap:** Assuming it sorts large to small without configuration.
    **陷阱：** 假設它在未設定的情況下會由大到小排序。
*   **Fix:** Use `Collections.reverseOrder()` or `(a, b) -> b - a`.
    **修正：** 使用 `Collections.reverseOrder()` 或 `(a, b) -> b - a`。

### B. `remove(Object)` Complexity (`remove(Object)` 的複雜度)
*   **Concept:** `poll()` is $O(\log N)$, but `remove(someObject)` scans the array to find the object first.
    **觀念：** `poll()` 是 $O(\log N)$，但 `remove(someObject)` 會先掃描陣列以尋找該物件。
*   **Trap:** Using `remove(Object)` inside a loop creates $O(N^2)$ logic implicitly.
    **陷阱：** 在迴圈中使用 `remove(Object)` 會隱性地產生 $O(N^2)$ 的邏輯。
*   **Fix:** Use "Lazy Removal" (mark as deleted and ignore when polled) or use a `TreeMap` / `HashHeap` if frequent random removal is needed.
    **修正：** 使用「延遲刪除」（標記為刪除並在取出時忽略），或若需要頻繁隨機刪除，改用 `TreeMap` / `HashHeap`。

### C. Comparator Overflow (比較器溢位)
*   **Trap:** `(a, b) -> a - b` can overflow if `a` is large positive and `b` is large negative.
    **陷阱：** 若 `a` 是大正數而 `b` 是大負數，`(a, b) -> a - b` 可能會溢位。
*   **Fix:** Use `Integer.compare(a, b)`.
    **修正：** 使用 `Integer.compare(a, b)`。

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify:** "Since we need the Kth largest/smallest dynamically, a Heap is a strong candidate."
    **識別：** 「由於我們需要動態取得第 K 大/小的元素，堆積是一個強力的候選方案。」
2.  **Trade-off:** "Sorting the whole array is $O(N \log N)$, but with a Heap of size K, we can reduce it to $O(N \log K)$."
    **權衡：** 「排序整個陣列是 $O(N \log N)$，但使用大小為 K 的堆積，我們可以將其降低至 $O(N \log K)$。」
3.  **Refine:** "For static arrays, QuickSelect is $O(N)$ average, but Heap is safer for worst-case or streaming data."
    **優化：** 「對於靜態陣列，QuickSelect 平均是 $O(N)$，但堆積在最壞情況或串流數據下更安全。」

### Whiteboard Strategy (白板策略)
*   Do **not** draw the binary tree structure unless asked to implement a heap from scratch.
    **不要**畫二元樹結構，除非被要求從頭實作堆積。
*   Draw a **"Bucket"** or a **"Funnel"** labeled "Min-Heap". Show items going in and the smallest item coming out.
    畫一個標示為「Min-Heap」的**「桶子」**或**「漏斗」**。展示項目進入以及最小項目出來的過程。

### Common Follow-ups (常見追問)
*   *Q: How to handle concurrent access?*
    *問：如何處理並發存取？*
    *A: Use `PriorityBlockingQueue` in Java.*
    *答：使用 Java 中的 `PriorityBlockingQueue`。*
*   *Q: What if K is small compared to N?*
    *問：如果 K 遠小於 N？*
    *A: Heap is great ($N \log K$).*
    *答：堆積非常好 ($N \log K$)。*

---

## 7. Practice Problems (練習題)

### Easy: Kth Largest Element in a Stream (串流中的第 K 大元素)
*   **LeetCode 703**
*   **Hint:** Keep a Min-Heap of size K. The root is always the Kth largest seen so far.
*   **提示：** 維護一個大小為 K 的最小堆積。根節點永遠是目前為止第 K 大的元素。

### Medium: Top K Frequent Elements (前 K 個高頻元素)
*   **LeetCode 347**
*   **Hint:** Count frequencies with a HashMap first. Then use a Min-Heap of size K to keep the top counts.
*   **提示：** 先用 HashMap 統計頻率。接著使用大小為 K 的最小堆積來保留最高頻次。
*   **Optimization:** Bucket Sort can do this in $O(N)$ if frequency range is limited.
*   **優化：** 若頻率範圍有限，桶排序（Bucket Sort）可在 $O(N)$ 完成。

### Hard: Find Median from Data Stream (從數據串流中尋找中位數)
*   **LeetCode 295**
*   **Hint:** Two Heaps pattern. `maxHeap` stores the smaller half, `minHeap` stores the larger half. Balance them so size difference is $\le 1$.
*   **提示：** 雙堆積模式。`maxHeap` 儲存較小的一半，`minHeap` 儲存較大的一半。平衡兩者使大小差異 $\le 1$。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] **Direction:** Did I define the Comparator correctly? (Min vs Max)
    **方向：** 我是否正確定義了比較器？（最小 vs 最大）
- [ ] **Size Control:** Am I polling from the heap when size > K? (For Top K problems)
    **大小控制：** 當大小 > K 時，我是否從堆積中移除元素？（針對 Top K 問題）
- [ ] **Object Equality:** If storing custom objects, did I override `equals()` and `hashCode()`? (Crucial for `remove()` or correctness)
    **物件相等性：** 若儲存自定義物件，我是否覆寫了 `equals()` 和 `hashCode()`？（對 `remove()` 或正確性至關重要）

### Complexity Check (複雜度確認)
- [ ] Is it $O(N \log K)$ or $O(N \log N)$? (Did I put *everything* in the heap or just keep K items?)
    **是 $O(N \log K)$ 還是 $O(N \log N)$？**（我是把**所有東西**都放進堆積，還是只保留 K 個項目？）

---

## 9. Memory Anchors (記憶錨點)

### The "Club Bouncer" Analogy (「夜店保鑣」類比)
*   **Scenario:** You want to keep the "Top K" richest people in the VIP room.
    **場景：** 你想在 VIP 包廂保留「Top K」最有錢的人。
*   **Mechanism:** The room holds K people. When a new person comes, you compare them with the **poorest** person in the room (the Root of a Min-Heap).
    **機制：** 包廂容納 K 人。當新人來時，你將他與包廂內**最窮**的人（最小堆積的根）比較。
*   **Action:** If the new person is richer, kick the poorest out and let the new person in.
    **動作：** 如果新人更有錢，把最窮的踢出去，讓新人進來。
*   **Why Min-Heap for Top K?** Because you only care about the "threshold" to stay in the club (the minimum value in the top set).
    **為何 Top K 用最小堆積？** 因為你只在乎留在俱樂部的「門檻」（前段班中的最小值）。