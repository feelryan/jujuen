Here is the comprehensive guide for **Linked List (Advanced)**, tailored for a Senior Software Engineer, using Java.

這是一份針對 **Linked List (進階)** 的完整教材，專為資深軟體工程師設計，使用 Java 撰寫。

---

# Advanced Linked List Interview Guide (進階鏈結串列面試指南)

## 1. Learning Goals (學習目標)

*   **Master Complex Pointer Manipulation:** confidently handle multi-pointer operations without losing references or creating cycles (e.g., reversing in groups).
    **掌握複雜指標操作：** 自信地處理多指標運算，確保不丟失參照或產生循環（例如：分組反轉）。
*   **Understand Low-Level Memory Implications:** Explain why Linked Lists often suffer from poor cache locality compared to Arrays, despite theoretical O(1) insertions.
    **理解底層記憶體影響：** 解釋為何鏈結串列儘管在理論上具有 O(1) 的插入優勢，但在快取局部性（Cache Locality）上通常不如陣列。
*   **Bridge to System Design:** Apply Linked List concepts to design problems like LRU Cache, Skip Lists, or memory allocators.
    **連結系統設計：** 將鏈結串列概念應用於 LRU 快取、跳表（Skip Lists）或記憶體配置器等設計問題。
*   **Concurrency Awareness:** Discuss thread-safety issues in Linked Lists (e.g., Fine-grained locking vs. Coarse-grained locking).
    **並發意識：** 探討鏈結串列中的執行緒安全問題（例如：細粒度鎖與粗粒度鎖）。

---

## 2. Core Concepts at a Senior Level (資深視角的核心觀念)

### Memory Layout & Performance (記憶體佈局與效能)
*   **Definition:** A linear collection of data elements whose order is not given by their physical placement in memory, but by pointers.
    **定義：** 一種線性資料集合，其順序並非由記憶體中的物理位置決定，而是透過指標連結。
*   **The "Senior" Insight:** While Big-O notation says insertion is O(1), in modern CPU architectures, the random memory access of a Linked List causes frequent **Cache Misses**.
    **「資深」洞察：** 雖然 Big-O 標示插入為 O(1)，但在現代 CPU 架構中，鏈結串列的隨機記憶體存取會導致頻繁的 **快取未命中（Cache Misses）**。
*   **Trade-off:** Use Linked Lists when the cost of shifting elements (Array) outweighs the cost of pointer chasing and cache misses, or when implementing specific structures like Queues/Stacks/Graphs.
    **權衡：** 當移動元素（陣列）的成本高於指標追蹤與快取未命中的成本時，或是在實作佇列/堆疊/圖等特定結構時，才使用鏈結串列。

### Complexity (複雜度)
*   **Access:** O(N)
*   **Search:** O(N)
*   **Insertion/Deletion:** O(1) *if pointer to position is known (若已知位置指標)*.

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior interviews, simple traversal is assumed. Focus on these patterns:
對於資深面試，簡單遍歷已被視為基本功。請專注於以下模式：

1.  **The "Dummy" (Sentinel) Node Strategy:**
    **「虛擬」（哨兵）節點策略：**
    *   Used to simplify edge cases where the head might change (e.g., deleting the head, merging lists).
    *   用於簡化頭節點可能改變的邊界情況（例如：刪除頭節點、合併串列）。

2.  **Fast & Slow Pointers (Tortoise and Hare):**
    **快慢指標（龜兔賽跑）：**
    *   Cycle detection, finding the middle, finding the k-th node from the end.
    *   循環檢測、尋找中點、尋找倒數第 k 個節點。

3.  **In-place Reversal (Iterative):**
    **原地反轉（迭代法）：**
    *   Vital for problems like "Palindrome Linked List" or "Reverse Nodes in k-Group".
    *   對於「回文鏈結串列」或「K 個一組反轉鏈結串列」等問題至關重要。

4.  **Two-List Merging / Partitioning:**
    **雙串列合併 / 分割：**
    *   Used in Merge Sort for Linked Lists or partitioning based on values.
    *   用於鏈結串列的合併排序或基於數值的分割。

---

## 4. Example Walkthrough (範例講解)

### Problem: Reverse Nodes in k-Group (K 個一組反轉鏈結串列)
*LeetCode 25 (Hard)*

#### Problem Statement (問題重述)
Given the head of a linked list, reverse the nodes of the list `k` at a time, and return the modified list. If the number of nodes is not a multiple of `k` then left-out nodes, in the end, should remain as it is.
給定一個鏈結串列的頭節點，每 `k` 個節點一組進行反轉，並返回修改後的串列。如果節點總數不是 `k` 的倍數，則最後剩餘的節點應保持原樣。

#### Approach (思路)

1.  **Brute Force:** Store all nodes in an array, reverse subarrays, and rebuild the list. Space O(N). **Reject this.**
    **暴力解：** 將所有節點存入陣列，反轉子陣列，然後重建串列。空間 O(N)。**拒絕此解法。**
2.  **Optimal (Iterative):**
    **最佳解（迭代法）：**
    *   Use a `dummy` node to handle the new head.
    *   使用 `dummy` 節點來處理新的頭節點。
    *   Check if there are at least `k` nodes left.
    *   檢查是否至少還有 `k` 個節點。
    *   Reverse the sub-segment.
    *   反轉該子區段。
    *   Connect the `prev` group's tail to the new head of this group, and the new tail of this group to the `next` segment.
    *   將 `prev` 群組的尾部連接到本群組的新頭部，並將本群組的新尾部連接到 `next` 區段。

#### Java Solution (Java 參考解)

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
class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        if (head == null || k == 1) return head;

        // Dummy node acts as an anchor before the head.
        // 虛擬節點作為頭節點前的錨點。
        ListNode dummy = new ListNode(0);
        dummy.next = head;

        // 'prev' tracks the tail of the previous reversed group.
        // 'prev' 追蹤前一個已反轉群組的尾部。
        ListNode prev = dummy;
        ListNode curr = head;

        // Count total nodes to know how many groups to reverse.
        // 計算總節點數以得知需要反轉多少組。
        int count = 0;
        while (curr != null) {
            count++;
            curr = curr.next;
        }

        // Reset curr to head for processing.
        // 將 curr 重置為 head 以進行處理。
        curr = head; 

        // Loop while we have enough nodes for a full group.
        // 當我們有足夠的節點組成一個完整群組時進行迴圈。
        while (count >= k) {
            // This will be the tail after reversal.
            // 這將是反轉後的尾部。
            ListNode groupTail = curr; 
            ListNode prevNode = null;
            
            // Standard reversal logic for k nodes.
            // 針對 k 個節點的標準反轉邏輯。
            for (int i = 0; i < k; i++) {
                ListNode nextNode = curr.next;
                curr.next = prevNode;
                prevNode = curr;
                curr = nextNode;
            }

            // Connect the previous group to the new head (prevNode).
            // 將前一個群組連接到新的頭部 (prevNode)。
            prev.next = prevNode;
            
            // Connect the new tail to the remaining list (curr).
            // 將新的尾部連接到剩餘的串列 (curr)。
            groupTail.next = curr;

            // Move 'prev' to the end of the current group for the next iteration.
            // 將 'prev' 移動到當前群組的末端，以便進行下一次迭代。
            prev = groupTail;
            
            count -= k;
        }

        return dummy.next;
    }
}
```

#### Common Mistakes (錯誤示範 & 為何錯)

*   **Mistake:** Reversing the remaining nodes when `count < k`.
    **錯誤：** 當 `count < k` 時反轉了剩餘節點。
    *   *Why:* The problem explicitly states remaining nodes should stay as is.
    *   *原因：* 題目明確規定剩餘節點應保持原樣。
*   **Mistake:** Losing the connection to the rest of the list (`curr` becomes null or lost).
    **錯誤：** 失去與剩餘串列的連接（`curr` 變為 null 或丟失）。
    *   *Why:* You must cache `curr.next` before changing pointers.
    *   *原因：* 更改指標前必須暫存 `curr.next`。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Node Value (`val`)** | **Node Reference (`next`)** | Changing `val` modifies data; changing `next` modifies structure. Don't confuse swapping values with swapping nodes. <br> 更改 `val` 修改數據；更改 `next` 修改結構。不要混淆交換數值與交換節點。 |
| **`head`** | **`dummy.next`** | `head` moves during traversal. `dummy.next` is the permanent reference to the start of the result. <br> `head` 在遍歷時會移動。`dummy.next` 是結果起始點的永久參照。 |
| **`curr = curr.next`** | **`curr.next = curr.next.next`** | The first moves the pointer forward (traversal). The second deletes a node (modification). <br> 第一個是將指標向前移動（遍歷）。第二個是刪除節點（修改）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Is it a singly or doubly linked list? Can I modify the list in-place, or should I create a copy?"
    **釐清：** 「這是單向還是雙向鏈結串列？我可以原地修改串列，還是應該建立副本？」
2.  **Visualize:** "I will use a dummy node to handle the edge case where the head is deleted."
    **視覺化：** 「我將使用虛擬節點來處理頭節點被刪除的邊界情況。」
3.  **Verify:** "Let's trace this with a small example: 1 -> 2 -> 3."
    **驗證：** 「讓我們用一個小範例來追蹤：1 -> 2 -> 3。」

### Whiteboard Strategy (白板策略)
*   **Draw Boxes & Arrows:** Never try to visualize pointer swaps in your head. Draw the state *before* and *after*.
    **畫方塊與箭頭：** 永遠不要試圖在腦中想像指標交換。畫出 *之前* 和 *之後* 的狀態。
*   **Label Pointers:** Clearly mark `prev`, `curr`, `next` on your diagram.
    **標記指標：** 在圖上清楚標記 `prev`、`curr`、`next`。

### Common Follow-ups (常見追問)
*   **Q:** How to handle this in a multi-threaded environment?
    **問：** 如何在多執行緒環境中處理此問題？
    *   **A:** Mention `ConcurrentLinkedQueue` (CAS algorithms) or fine-grained locking (locking individual nodes).
    *   **答：** 提及 `ConcurrentLinkedQueue`（CAS 演算法）或細粒度鎖（鎖定個別節點）。

---

## 7. Practice Problems (練習題)

### 1. Copy List with Random Pointer (Medium)
*   **Prompt:** Deep copy a list where each node has a `next` and a `random` pointer.
    **題目：** 深拷貝一個串列，其中每個節點都有 `next` 和 `random` 指標。
*   **Hint:** Use a `HashMap<OldNode, NewNode>` or interweave the new nodes (`A -> A' -> B -> B'`).
    **提示：** 使用 `HashMap<OldNode, NewNode>` 或交錯插入新節點（`A -> A' -> B -> B'`）。

### 2. LRU Cache (Medium/Hard)
*   **Prompt:** Design a data structure that follows Least Recently Used constraints with O(1) operations.
    **題目：** 設計一個遵循「最近最少使用」限制且操作為 O(1) 的資料結構。
*   **Hint:** Combine a `HashMap` (for lookup) with a `Doubly Linked List` (for ordering).
    **提示：** 結合 `HashMap`（用於查找）與 `雙向鏈結串列`（用於排序）。

### 3. Merge k Sorted Lists (Hard)
*   **Prompt:** Merge `k` sorted linked lists into one sorted list.
    **題目：** 將 `k` 個已排序的鏈結串列合併為一個已排序串列。
*   **Hint:** Use a Min-Heap (PriorityQueue) to keep track of the smallest head among `k` lists. Complexity: O(N log k).
    **提示：** 使用最小堆積（PriorityQueue）來追蹤 `k` 個串列中最小的頭節點。複雜度：O(N log k)。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Null Check:** Did I handle `head == null` or `head.next == null`?
    **空值檢查：** 我是否處理了 `head == null` 或 `head.next == null`？
*   [ ] **Cycle Check:** Did I accidentally create a cycle (e.g., `curr.next = curr`)?
    **循環檢查：** 我是否意外產生了循環（例如：`curr.next = curr`）？
*   [ ] **Lost Head:** Do I have a reference to the new head (or `dummy.next`)?
    **遺失頭部：** 我是否保留了新頭部（或 `dummy.next`）的參照？
*   [ ] **Tail Termination:** Did I set the last node's `next` to `null` if required?
    **尾部終止：** 如果需要，我是否將最後一個節點的 `next` 設為 `null`？

---

## 9. Memory Anchors (記憶錨點)

*   **The "Train" Analogy:** Think of a Linked List as a train. To remove a car, you must unhook it from the previous car and hook the previous car to the next car. You cannot just "delete" the car without reconnecting the couplers.
    **「火車」類比：** 將鏈結串列視為一列火車。要移除一節車廂，你必須將其與前一節解鉤，並將前一節鉤到下一節。你不能在不重新連接鉤子的情況下直接「刪除」車廂。
*   **The "Anchor" (Dummy Node):** A ship needs an anchor to stay put. Your `dummy` node is the anchor that holds the list in place while you mess around with the links.
    **「錨」（虛擬節點）：** 船需要錨才能停泊。你的 `dummy` 節點就是那個錨，當你在擺弄連結時，它能固定住串列的位置。