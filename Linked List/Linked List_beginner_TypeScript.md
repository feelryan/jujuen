# Linked List: Foundational Mastery (鏈結串列：基礎精通)

## 1. Learning Objectives (學習目標)

1.  **Master Pointer Manipulation:** deeply understand how references work to avoid breaking the chain or creating cycles unintentionally.
    **精通指標操作：** 深刻理解引用（reference）的運作原理，以避免意外斷鍊或產生循環。
2.  **Internalize the "Dummy Head" Pattern:** learn to use sentinel nodes to simplify edge cases involving the head of the list.
    **內化「虛擬頭節點」模式：** 學習使用哨兵節點（sentinel nodes）來簡化涉及 list 頭部的邊界情況。
3.  **Implement Basic Operations Flawlessly:** achieve bug-free implementation of insertion, deletion, and reversal within 5-10 minutes.
    **完美實作基本操作：** 在 5–10 分鐘內無 bug 地實作插入、刪除與反轉。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A Linked List is a linear data structure where elements are not stored at contiguous memory locations.
鏈結串列是一種線性資料結構，其元素並非儲存在連續的記憶體位置。
The elements are linked using pointers (or references in TypeScript/JS).
元素之間透過指標（或 TypeScript/JS 中的引用）連結。

### Intuition (直覺)
Think of a treasure hunt where each clue holds the location of the next clue.
想像一場尋寶遊戲，每一條線索都包含下一條線索的位置。
You cannot jump to the 5th clue without visiting the previous 4.
你無法在不訪問前 4 條線索的情況下直接跳到第 5 條。

### Complexity (複雜度)

| Operation (操作) | Time Complexity (時間) | Space Complexity (空間) | Note (備註) |
| :--- | :--- | :--- | :--- |
| **Access (存取)** | $O(N)$ | $O(1)$ | No random access (無隨機存取) |
| **Search (搜尋)** | $O(N)$ | $O(1)$ | Linear scan (線性掃描) |
| **Insert/Delete (插入/刪除)** | $O(1)$ | $O(1)$ | Assuming we already have the pointer to the position (假設已取得該位置的指標) |

### When to Use (適用場景)
*   **Constant-time insertions/deletions:** When you frequently add or remove items from the beginning or middle of the list.
    **常數時間的插入/刪除：** 當你頻繁地從 list 的開頭或中間新增或移除項目時。
*   **Dynamic Size:** When the number of elements is unknown or changes frequently, avoiding memory reallocation overhead of Arrays.
    **動態大小：** 當元素數量未知或頻繁變動，且希望避免陣列的記憶體重新分配開銷時。

### When NOT to Use (不適用場景)
*   **Random Access Needed:** If you need to access elements by index (e.g., `arr[5]`).
    **需要隨機存取：** 如果你需要透過索引存取元素（例如 `arr[5]`）。
*   **Cache Locality:** Arrays have better cache locality due to contiguous memory; Linked Lists cause more cache misses.
    **快取局部性：** 陣列因記憶體連續而有較好的快取局部性；鏈結串列會導致較多的快取未命中（cache misses）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner/foundation level, these patterns are essential.
對於初階/基礎層級，這些模式至關重要。

1.  **Dummy Head (Sentinel Node):**
    Creating a placeholder node before the actual head to handle edge cases (like deleting the head) uniformly.
    **虛擬頭節點（哨兵節點）：** 在實際頭部之前建立一個佔位節點，以統一處理邊界情況（如刪除頭部）。

2.  **Two Pointers (Runner Technique):**
    Using pointers moving at different speeds (Fast/Slow) or with a fixed gap to find cycles, middle points, or $k$-th last elements.
    **雙指標（跑者技巧）：** 使用不同速度移動（快/慢）或保持固定間距的指標，來尋找循環、中點或倒數第 $k$ 個元素。

3.  **In-place Reversal:**
    Manipulating `next` pointers to change the direction of the list without using extra space.
    **原地反轉：** 操作 `next` 指標以改變 list 的方向，而不使用額外空間。

---

## 4. Example Walkthrough (範例講解)

### Problem: Remove N-th Node From End of List
### 問題：移除鏈結串列倒數第 N 個節點

**Problem Statement (問題重述):**
Given the `head` of a linked list, remove the $n$-th node from the end of the list and return its head.
給定一個鏈結串列的 `head`，移除倒數第 $n$ 個節點並回傳其 head。

**Approach (思路):**

1.  **Naive (暴力法):**
    Calculate the length $L$ of the list first. Then traverse to node $L-n$ and remove the next node.
    先計算 list 的長度 $L$。然後遍歷到第 $L-n$ 個節點並移除其下一個節點。
    *Constraint:* Requires two passes.
    *限制：* 需要兩次遍歷。

2.  **Optimal (Two Pointers - One Pass) (最佳解 - 雙指標一次遍歷):**
    Use two pointers, `fast` and `slow`.
    使用兩個指標，`fast` 與 `slow`。
    Move `fast` $n$ steps ahead.
    將 `fast` 向前移動 $n$ 步。
    Then move both `fast` and `slow` until `fast` reaches the end.
    接著同時移動 `fast` 與 `slow`，直到 `fast` 到達末端。
    `slow` will be at the node right *before* the target node.
    此時 `slow` 將位於目標節點的*前一個*節點。

**Complexity (複雜度):**
*   Time: $O(N)$ - One pass. (時間：$O(N)$ - 一次遍歷)
*   Space: $O(1)$ - Only pointers used. (空間：$O(1)$ - 僅使用指標)

**TypeScript Solution (TypeScript 參考解):**

```typescript
/**
 * Definition for singly-linked list.
 * 單向鏈結串列的定義。
 */
class ListNode {
    val: number
    next: ListNode | null
    constructor(val?: number, next?: ListNode | null) {
        this.val = (val===undefined ? 0 : val)
        this.next = (next===undefined ? null : next)
    }
}

function removeNthFromEnd(head: ListNode | null, n: number): ListNode | null {
    // Use a dummy node to handle the case where the head itself needs to be removed.
    // 使用虛擬節點來處理需要移除 head 本身的情況。
    const dummy = new ListNode(0);
    dummy.next = head;

    let fast: ListNode | null = dummy;
    let slow: ListNode | null = dummy;

    // Move fast pointer n + 1 steps ahead so that slow stops one node BEFORE the target.
    // 將 fast 指標向前移動 n + 1 步，這樣 slow 會停在目標節點的「前一個」位置。
    for (let i = 0; i <= n; i++) {
        // Safety check, though problem constraints usually guarantee valid n.
        // 安全檢查，雖然題目限制通常保證 n 有效。
        if (fast === null) return head; 
        fast = fast.next;
    }

    // Move both pointers until fast reaches the end.
    // 同時移動兩個指標，直到 fast 到達末端。
    while (fast !== null) {
        slow = slow!.next; // slow cannot be null here because fast is ahead.
        fast = fast.next;
    }

    // Remove the nth node from the end.
    // 移除倒數第 n 個節點。
    // slow!.next is the target; we skip it by pointing to slow!.next!.next.
    // slow!.next 是目標；我們透過指向 slow!.next!.next 來跳過它。
    if (slow && slow.next) {
        slow.next = slow.next.next;
    }

    // Return dummy.next, which is the new head (or the original head).
    // 回傳 dummy.next，即為新的 head（或是原本的 head）。
    return dummy.next;
}
```

**Why the "Dummy" is crucial here? (為何「虛擬節點」在此至關重要？)**
If the list has 5 nodes and we want to remove the 5th from the end (the head), `slow` needs to be *before* the head. The `dummy` node provides that position.
如果 list 有 5 個節點，而我們要移除倒數第 5 個（即 head），`slow` 需要位於 head 的*前面*。`dummy` 節點提供了這個位置。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱 / 混淆) | Correct Understanding (正確理解) |
| :--- | :--- | :--- |
| **Null Pointer Exception** | Accessing `node.next` when `node` is `null`. <br> 存取 `node.next` 當 `node` 為 `null` 時。 | Always check `if (node !== null)` before accessing properties. <br> 存取屬性前務必檢查 `if (node !== null)`。 |
| **Lost Head** | Moving the `head` pointer directly during traversal. <br> 遍歷時直接移動 `head` 指標。 | Use a temporary pointer (e.g., `let curr = head`) to traverse. <br> 使用臨時指標（如 `let curr = head`）來遍歷。 |
| **Cycle Handling** | `while (curr !== null)` loops forever if a cycle exists. <br> 若存在循環，`while (curr !== null)` 會造成無窮迴圈。 | Use Floyd’s Cycle-Finding Algorithm (Fast/Slow pointers) or a Hash Set. <br> 使用 Floyd 判圈演算法（快慢指標）或 Hash Set。 |
| **Memory Leaks** | (More relevant in C++) Not freeing memory. In JS/TS, detaching nodes is enough. <br> （C++較相關）未釋放記憶體。在 JS/TS 中，斷開節點連結即可。 | In TS, ensure no references point to the "deleted" node so GC can collect it. <br> 在 TS 中，確保沒有引用指向「已刪除」的節點，以便 GC 回收。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Input:** "Is it a singly or doubly linked list? Can the list be empty?"
    **釐清輸入：** 「這是單向還是雙向鏈結串列？List 可能是空的嗎？」
2.  **Visual Confirmation:** "I will draw a few nodes to visualize the pointer changes."
    **視覺確認：** 「我會畫幾個節點來視覺化指標的變動。」
3.  **Edge Cases First:** "I'll use a dummy head to handle the case where the head is deleted."
    **優先處理邊界：** 「我會使用虛擬頭節點來處理 head 被刪除的情況。」

### Whiteboard Strategy (白板策略)
*   **Draw Boxes and Arrows:** Represent nodes as boxes and pointers as arrows.
    **畫框與箭頭：** 用方框代表節點，箭頭代表指標。
*   **Label Pointers:** Clearly mark `prev`, `curr`, `next` on your diagram before writing code.
    **標記指標：** 寫程式碼前，在圖上清楚標示 `prev`、`curr`、`next`。
*   **Trace the Code:** Physically trace the arrows with your finger during the dry run.
    **追蹤程式碼：** 在模擬執行（dry run）時，用手指實際追蹤箭頭的走向。

### Common Follow-ups (常見追問)
*   "How would you solve this if the linked list is too large to fit in RAM?" (External sorting/storage).
    「如果鏈結串列大到無法放入記憶體，你會如何解決？」（外部排序/儲存）。
*   "What if it's a Doubly Linked List?" (Update `prev` pointers too).
    「如果是雙向鏈結串列呢？」（也需要更新 `prev` 指標）。

---

## 7. Practice Problems (練習題)

### Easy: Merge Two Sorted Lists (合併兩個已排序串列)
*   **Hint:** Use a dummy head to build the result list. Compare heads of both lists and attach the smaller one.
    **提示：** 使用虛擬頭節點來建立結果 list。比較兩個 list 的 head 並接上較小的那個。
*   **Focus:** Pointer manipulation, base cases.
    **重點：** 指標操作、基本情況。

### Medium: Swap Nodes in Pairs (成對交換節點)
*   **Hint:** Iterative approach is safer. You need three pointers: `prev`, `first`, `second`.
    **提示：** 迭代法較安全。你需要三個指標：`prev`、`first`、`second`。
*   **Focus:** Complex pointer rewiring without losing the rest of the list.
    **重點：** 複雜的指標重接，且不丟失 list 的其餘部分。

### Hard (for this level): Reverse Linked List II (Partial Reverse) (反轉鏈結串列 II - 局部反轉)
*   **Hint:** Move to position $m-1$. Reverse the sub-list from $m$ to $n$. Connect the prefix to the new head of the sub-list, and the tail of the sub-list to the suffix.
    **提示：** 移動到位置 $m-1$。反轉從 $m$ 到 $n$ 的子 list。將前綴連接到子 list 的新 head，並將子 list 的尾部連接到後綴。
*   **Focus:** Precise indexing and combining traversal with reversal.
    **重點：** 精確的索引定位，以及結合遍歷與反轉。

---

## 8. Quick Checklists (快速檢核表)

Use this during your interview coding phase.
在面試寫程式階段使用此表。

*   [ ] **Null Check:** Did I handle `head === null` or `head.next === null`?
    **Null 檢查：** 我是否處理了 `head === null` 或 `head.next === null`？
*   [ ] **Dummy Head:** Did I use a dummy head if the head node might change?
    **虛擬頭節點：** 如果 head 節點可能改變，我是否使用了虛擬頭節點？
*   [ ] **Pointer Update:** Did I remember to advance the pointers (`curr = curr.next`) in the `while` loop?
    **指標更新：** 我是否記得在 `while` 迴圈中推進指標（`curr = curr.next`）？
*   [ ] **Cycle Safety:** Is my termination condition correct to prevent infinite loops?
    **循環安全：** 我的終止條件是否正確，以防止無窮迴圈？
*   [ ] **Return Value:** Am I returning `head` or `dummy.next`? (Usually `dummy.next` if dummy is used).
    **回傳值：** 我是回傳 `head` 還是 `dummy.next`？（若使用 dummy，通常是 `dummy.next`）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Train" Analogy (火車類比)
*   **Nodes are Train Cars:** Each car holds cargo (data) and is hooked to the next car (pointer).
    **節點是車廂：** 每個車廂裝載貨物（資料）並勾連到下一個車廂（指標）。
*   **Insertion:** To add a car in the middle, you must unhook two cars, hook the new one to the front car, and then hook the back car to the new one.
    **插入：** 要在中間加掛車廂，你必須解開兩個車廂，將新車廂勾到前一節，再將後一節勾到新車廂上。
*   **Loss:** If the hook breaks (pointer lost), the rest of the train is left behind on the tracks (memory leak/lost data).
    **遺失：** 如果掛勾斷裂（指標遺失），剩下的列車就會被遺留在軌道上（記憶體洩漏/資料遺失）。

### The "Scavenger Hunt" (尋寶遊戲)
*   You only know where the **first** clue is (`head`).
    你只知道**第一條**線索在哪裡（`head`）。
*   The only way to find the 10th clue is to go to the 1st, read it to find the 2nd, and so on.
    找到第 10 條線索的唯一方法是先去第 1 條，讀取它以找到第 2 條，依此類推。
*   This explains why Access is $O(N)$.
    這解釋了為什麼存取是 $O(N)$。