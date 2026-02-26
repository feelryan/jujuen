# Linked List Masterclass for Senior Engineers
# 資深工程師鏈結串列大師班

## 1. Learning Objectives (學習目標)

*   **Master Pointer Manipulation without Memory Leaks:** Gain absolute confidence in rewiring `next` pointers without losing reference to the rest of the list.
    **掌握指標操作並避免記憶體洩漏：** 建立對重接 `next` 指標的絕對信心，確保不會丟失對剩餘串列的參照。
*   **Internalize the "Dummy Node" Pattern:** Learn to use sentinel nodes to eliminate edge case handling for the head of the list.
    **內化「虛擬節點（Dummy Node）」模式：** 學習使用哨兵節點來消除針對串列頭部的邊界情況處理。
*   **Combine Multiple Sub-routines:** Solve complex problems by breaking them down into standard operations (e.g., Find Middle + Reverse + Merge).
    **組合多個子程序：** 透過將問題拆解為標準操作（如：尋找中點 + 反轉 + 合併）來解決複雜問題。
*   **Optimize Space Complexity:** Move from O(N) space (using arrays/stacks) to O(1) space (in-place manipulation).
    **優化空間複雜度：** 從 O(N) 空間（使用陣列/堆疊）進階到 O(1) 空間（原地操作）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Linked List is a recursive data structure where each node contains data and a reference to the next node.
鏈結串列是一種遞迴資料結構，每個節點包含資料以及指向下一個節點的參照。

Unlike arrays, elements are not stored in contiguous memory locations.
與陣列不同，元素並非儲存在連續的記憶體位置中。

### Complexity Analysis (複雜度分析)

| Operation (操作) | Time (時間) | Space (空間) | Note (備註) |
| :--- | :--- | :--- | :--- |
| **Access (存取)** | O(N) | O(1) | No random access (無隨機存取) |
| **Search (搜尋)** | O(N) | O(1) | Must traverse (必須遍歷) |
| **Insert/Delete (Head) (頭部插入/刪除)** | O(1) | O(1) | Very efficient (非常高效) |
| **Insert/Delete (Middle) (中間插入/刪除)** | O(1)* | O(1) | *O(1) only if we already have the reference to the previous node (僅在已知前一個節點參照時為 O(1)) |

### When to Use (適用場景)
*   **Constant-time insertions/deletions:** When you need to frequently add or remove items from the beginning or end (e.g., implementing Queues or Stacks).
    **常數時間的插入/刪除：** 當你需要頻繁地從頭部或尾部新增或移除項目時（例如：實作佇列或堆疊）。
*   **Unknown size:** When the number of elements is not known in advance, avoiding array resizing costs.
    **未知大小：** 當元素數量無法預知時，可避免陣列重新調整大小的成本。
*   **Building blocks:** Basis for Hash Maps (chaining), Adjacency Lists (Graphs), and LRU Caches.
    **基礎積木：** 作為雜湊表（鏈結法）、鄰接表（圖論）以及 LRU 快取的基礎。

### When NOT to Use (不適用場景)
*   **Random Access:** If you need `arr[i]` frequently.
    **隨機存取：** 如果你需要頻繁使用 `arr[i]`。
*   **Cache Locality:** Arrays have better CPU cache performance due to contiguous memory; Linked Lists cause cache misses.
    **快取局部性：** 陣列因記憶體連續而具有較佳的 CPU 快取效能；鏈結串列容易導致快取未命中（Cache Miss）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. The "Runner" Technique (Fast & Slow Pointers)
**「跑者」技巧（快慢指標）**
*   **Use case:** Finding the middle node, detecting cycles, or finding the K-th node from the end.
    **適用場景：** 尋找中間節點、偵測環、或尋找倒數第 K 個節點。
*   **Mechanism:** `slow` moves 1 step, `fast` moves 2 steps.
    **機制：** `slow` 走 1 步，`fast` 走 2 步。

### B. Dummy Node (Sentinel)
**虛擬節點（哨兵）**
*   **Use case:** Operations that might change the `head` (e.g., deleting head, merging lists).
    **適用場景：** 可能改變 `head` 的操作（例如：刪除頭部、合併串列）。
*   **Mechanism:** `let dummy = new ListNode(0); dummy.next = head; return dummy.next;`
    **機制：** 建立一個指向 head 的 dummy 節點，最後回傳 `dummy.next`。

### C. In-place Reversal
**原地反轉**
*   **Use case:** Reversing the whole list or a sub-segment (m to n) without extra memory.
    **適用場景：** 在不使用額外記憶體的情況下，反轉整個串列或子區段（m 到 n）。
*   **Mechanism:** Maintaining `prev`, `curr`, and `next` pointers to rewire direction.
    **機制：** 維護 `prev`、`curr` 和 `next` 指標來重接方向。

---

## 4. Example Walkthrough (範例講解)

### Problem: Reorder List (重排鏈結串列)
**LeetCode 143 (Medium)**

#### Problem Statement (問題重述)
You are given the head of a singly linked-list. The list can be represented as:
給定一個單向鏈結串列的頭部。該串列可表示為：
`L0 → L1 → … → Ln-1 → Ln`

Reorder the list to be on the following form:
將串列重排為以下形式：
`L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …`

You may not modify the values in the list's nodes. Only nodes themselves may be changed.
你不能修改節點中的數值。只能改變節點本身（的連接關係）。

---

#### Approach 1: Brute Force with Array (暴力法：使用陣列)
*   **Idea:** Store all nodes in an array `nodes[]`, then use two pointers (left, right) to reconstruct the links.
    **思路：** 將所有節點存入陣列 `nodes[]`，然後使用雙指標（左、右）重建連結。
*   **Pros:** Easy to implement.
    **優點：** 實作簡單。
*   **Cons:** O(N) Space complexity. In an interview, we want O(1) space.
    **缺點：** O(N) 空間複雜度。在面試中，我們追求 O(1) 空間。

#### Approach 2: Optimal Solution (最佳解)
This problem is actually a combination of three standard patterns.
這個問題實際上是三個標準模式的組合。

1.  **Find the Middle:** Split the list into two halves using Fast & Slow pointers.
    **尋找中點：** 使用快慢指標將串列切分為兩半。
2.  **Reverse the Second Half:** Reverse the second part of the list.
    **反轉後半部：** 將串列的後半部分反轉。
3.  **Merge Two Lists:** Alternately merge the first half and the reversed second half.
    **合併兩個串列：** 交替合併前半部與反轉後的後半部。

#### TypeScript Implementation (TypeScript 實作)

```typescript
// Definition for singly-linked list.
class ListNode {
    val: number
    next: ListNode | null
    constructor(val?: number, next?: ListNode | null) {
        this.val = (val===undefined ? 0 : val)
        this.next = (next===undefined ? null : next)
    }
}

/**
 * Main function to reorder the list
 * 主函數：重排串列
 */
function reorderList(head: ListNode | null): void {
    if (!head || !head.next) return;

    // Step 1: Find the middle of the list (Fast & Slow Pointers)
    // 步驟 1：尋找串列中點（快慢指標）
    let slow: ListNode | null = head;
    let fast: ListNode | null = head;

    // fast moves 2 steps, slow moves 1 step
    // fast 走兩步，slow 走一步
    while (fast && fast.next) {
        slow = slow!.next;
        fast = fast.next.next;
    }

    // Step 2: Reverse the second half
    // 步驟 2：反轉後半部
    // slow.next is the start of the second half
    // slow.next 是後半部的起點
    let prev: ListNode | null = null;
    let curr: ListNode | null = slow!.next;
    
    // Break the link between first half and second half to avoid cycles
    // 斷開前半部與後半部的連結以避免形成環
    slow!.next = null; 

    while (curr) {
        const nextTemp = curr.next; // Save next node / 暫存下一個節點
        curr.next = prev;           // Reverse pointer / 反轉指標
        prev = curr;                // Move prev forward / prev 前進
        curr = nextTemp;            // Move curr forward / curr 前進
    }
    // After loop, 'prev' is the head of the reversed second half
    // 迴圈結束後，'prev' 即為反轉後後半部的頭部

    // Step 3: Merge two halves
    // 步驟 3：合併兩半
    let first: ListNode | null = head;
    let second: ListNode | null = prev;

    while (second) {
        // Save next pointers
        // 暫存 next 指標
        const temp1 = first!.next;
        const temp2 = second.next;

        // Link first -> second
        // 連結 first -> second
        first!.next = second;
        // Link second -> original next of first
        // 連結 second -> first 原本的下一個節點
        second.next = temp1;

        // Move pointers forward
        // 指標前進
        first = temp1;
        second = temp2;
    }
}
```

#### Complexity (複雜度)
*   **Time:** O(N) — We traverse the list a constant number of times (find middle, reverse, merge).
    **時間：** O(N) — 我們遍歷串列常數次（找中點、反轉、合併）。
*   **Space:** O(1) — We only use pointers, no extra data structures.
    **空間：** O(1) — 我們僅使用指標，無額外資料結構。

#### Common Mistake (常見錯誤)
*   **Forgetting to break the link:** If you don't set `slow.next = null` after finding the middle, the list will contain a cycle or infinite loop during traversal.
    **忘記斷開連結：** 如果在找到中點後沒有設定 `slow.next = null`，串列在遍歷時將包含環或導致無窮迴圈。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept / Pitfall (概念/陷阱) | Explanation (解釋) |
| :--- | :--- |
| **`curr = curr.next` vs `curr.next = node`** | The former moves the pointer (traversal); the latter changes the structure (wiring). <br> 前者移動指標（遍歷）；後者改變結構（接線）。 |
| **Lost Head (丟失頭部)** | If you move `head` directly (`head = head.next`) without keeping a reference, you lose the list. Always use a `curr` pointer for traversal. <br> 如果直接移動 `head` 而未保留參照，你會丟失整個串列。請務必使用 `curr` 指標進行遍歷。 |
| **Null Pointer Exception** | Checking `while(curr.next)` when `curr` itself might be null. Always check `curr && curr.next`. <br> 當 `curr` 本身可能為 null 時檢查 `while(curr.next)`。務必檢查 `curr && curr.next`。 |
| **Cycle Handling (環的處理)** | In problems like "Merge", forgetting to nullify the end of a list can create unintended cycles. <br> 在「合併」類問題中，忘記將串列尾端設為 null 可能導致非預期的環。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Is it a singly or doubly linked list? Can I modify the list in-place?"
    **釐清：** 「這是單向還是雙向鏈結串列？我可以原地修改串列嗎？」
2.  **Visualize:** "I will draw a diagram to trace the pointer changes." (Crucial for Linked Lists).
    **視覺化：** 「我會畫一個圖來追蹤指標的變化。」（對鏈結串列至關重要）。
3.  **Edge Cases:** "I will handle the cases where the list is empty or has only one node."
    **邊界情況：** 「我會處理串列為空或只有一個節點的情況。」

### Whiteboard Strategy (白板策略)
*   **Draw boxes and arrows:** Don't just write code. Draw `[1] -> [2] -> null`.
    **畫框框和箭頭：** 不要只寫程式碼。畫出 `[1] -> [2] -> null`。
*   **Trace with variables:** Write `prev`, `curr`, `next` under the nodes to show where they point at each step.
    **標註變數位置：** 在節點下方寫上 `prev`、`curr`、`next`，展示每一步它們指向哪裡。

### Common Follow-ups (常見追問)
*   "How would you solve this if the list is too large to fit in RAM?" (Hint: External sorting / processing chunks).
    「如果串列大到無法放入記憶體，你會怎麼解決？」（提示：外部排序 / 分塊處理）。
*   "Is your solution thread-safe?" (Hint: No, linked lists usually require locking for concurrent modification).
    「你的解法是執行緒安全的嗎？」（提示：不是，鏈結串列的並發修改通常需要鎖）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Merge Two Sorted Lists (合併兩個已排序串列)
*   **Goal:** Merge two sorted linked lists and return it as a sorted list.
    **目標：** 合併兩個已排序的鏈結串列並回傳一個排序後的串列。
*   **Hint:** Use a **Dummy Node** to simplify the head logic. Iterate while both lists are non-null.
    **提示：** 使用 **虛擬節點（Dummy Node）** 來簡化頭部邏輯。當兩個串列皆非空時進行迭代。

### 2. Medium: Add Two Numbers (兩數相加)
*   **Goal:** Lists represent numbers in reverse order (e.g., 2->4->3 is 342). Add them.
    **目標：** 串列代表逆序儲存的數字（如 2->4->3 代表 342）。將它們相加。
*   **Hint:** Simulate manual addition. Maintain a `carry` variable. Watch out for the final carry (e.g., 5+5=10, need extra node for '1').
    **提示：** 模擬手算加法。維護一個 `carry`（進位）變數。注意最後的進位（如 5+5=10，需要額外節點存 '1'）。

### 3. Medium/Hard: Copy List with Random Pointer (複製帶隨機指標的串列)
*   **Goal:** Deep copy a list where each node has a `next` and a `random` pointer.
    **目標：** 深拷貝一個串列，每個節點除了 `next` 還有一個 `random` 指標。
*   **Hint:**
    1.  **HashMap:** Map `originalNode -> clonedNode`. (O(N) space).
    2.  **Interweaving (Optimal):** Create clone `A'` next to `A` (`A -> A' -> B -> B'`). Set random pointers, then separate. (O(1) space).
    **提示：**
    1.  **雜湊表：** 映射 `originalNode -> clonedNode`。（O(N) 空間）。
    2.  **交織法（最佳）：** 在 `A` 旁邊建立複製的 `A'`（`A -> A' -> B -> B'`）。設定 random 指標，然後分離。（O(1) 空間）。

---

## 8. Rapid Checklists (快速檢核表)

### Self-Review / Debugging (自我審查/除錯)
- [ ] **Head Handling:** Did I handle the case where `head` is null?
    **頭部處理：** 我是否處理了 `head` 為 null 的情況？
- [ ] **Single Node:** Does the logic work if the list has only 1 node?
    **單一節點：** 如果串列只有 1 個節點，邏輯是否正確？
- [ ] **Pointer Loss:** Did I save `curr.next` before overwriting `curr.next`?
    **指標丟失：** 在覆蓋 `curr.next` 之前，我是否先備份了它？
- [ ] **Termination:** Does the `while` loop condition guarantee termination (no cycles)?
    **終止條件：** `while` 迴圈條件是否保證會終止（無無窮迴圈）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Treasure Hunt (尋寶遊戲)
Think of a Linked List as a **Scavenger Hunt**.
把鏈結串列想像成一場**尋寶遊戲**。
*   You only have the clue to the **first** location (Head).
    你只有前往**第一個**地點（Head）的線索。
*   At each location, you find a note (Data) and the address of the **next** location (Pointer).
    在每個地點，你會找到一張紙條（資料）和前往**下一個**地點的地址（指標）。
*   If you lose the address slip before you get to the next spot, the rest of the treasure path is lost forever (Memory Leak).
    如果你在到達下一個地點前弄丟了地址條，剩下的寶藏路徑就永遠丟失了（記憶體洩漏）。

### The Train Cars (火車車廂)
*   **Insert:** To add a car in the middle, you must unhook the coupler (pointer) of the previous car, hook it to the new car, and hook the new car to the next one.
    **插入：** 要在中間加掛車廂，必須解開前一節車廂的掛鉤（指標），鉤上新車廂，再將新車廂鉤上下一個車廂。
*   **Dummy Node:** The locomotive engine that pulls the train but doesn't carry passengers. It ensures there's always something to pull the first car.
    **虛擬節點：** 就像牽引火車但不載客的火車頭。它確保總是有東西可以拉動第一節車廂。