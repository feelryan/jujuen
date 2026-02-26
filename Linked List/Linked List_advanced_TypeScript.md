# Advanced Linked List Interview Guide
# 進階鏈結串列面試指南

## 1. Learning Goals（學習目標）

1.  **Master Complex Pointer Manipulation:** Perform intricate operations (reversal, reordering) without memory leaks or cycle creation.
    **掌握複雜指標操作：** 執行錯綜複雜的操作（反轉、重排），且不造成記憶體洩漏或產生循環。
2.  **Deep Understanding of Memory & Caching:** Articulate why Linked Lists often underperform Arrays in modern CPU architectures (cache locality).
    **深入理解記憶體與快取：** 能清楚說明為何在現代 CPU 架構下，鏈結串列的效能常不如陣列（快取局部性）。
3.  **System Design Application:** Apply Linked List concepts to high-level designs like LRU Caches or Skip Lists.
    **系統設計應用：** 將鏈結串列概念應用於 LRU 快取或 Skip Lists 等高階設計。
4.  **Production-Ready Code:** Write clean, modular TypeScript code using Sentinel Nodes (Dummy Nodes) to eliminate edge cases.
    **生產級程式碼：** 使用哨兵節點（Dummy Nodes）撰寫乾淨、模組化的 TypeScript 程式碼，以消除邊界情況。

---

## 2. Core Concepts: Advanced View（核心觀念速覽：進階視角）

### Definition & Intuition（定義與直覺）
While a Junior Engineer sees a collection of nodes, a Senior Engineer sees a **non-contiguous memory structure** that trades random access for flexible insertion/deletion.
初階工程師看到的是節點的集合，而資深工程師看到的是**非連續記憶體結構**，它犧牲了隨機存取能力以換取靈活的插入與刪除。

### Complexity Analysis（複雜度分析）

| Operation | Time Complexity | Space Complexity | Note (Senior Insight) |
| :--- | :--- | :--- | :--- |
| **Access (Get)** | $O(N)$ | $O(1)$ | **Cache Misses:** High probability of CPU cache misses due to scattered memory. <br> **快取未命中：** 由於記憶體分散，極高機率導致 CPU 快取未命中。 |
| **Insert/Delete (Known Node)** | $O(1)$ | $O(1)$ | Requires reference to the *previous* node (for Singly LL). <br> 需要持有*前一個*節點的參照（針對單向鏈結串列）。 |
| **Search** | $O(N)$ | $O(1)$ | Cannot use Binary Search. <br> 無法使用二分搜尋法。 |

### When to Use (vs. Array)（適用場景）
*   **Constant-time insertions/deletions** at the head or tail are critical (e.g., Implementing Queues/Stacks).
    **頭尾的常數時間插入/刪除**至關重要時（例如：實作佇列/堆疊）。
*   **Memory fragmentation** is a concern, and you cannot allocate a large contiguous block.
    **記憶體碎片化**是一個問題，且無法分配大的連續區塊時。
*   **Building Blocks:** Basis for Hash Maps (chaining), Adjacency Lists (Graphs), and LRU Caches.
    **基礎建構單元：** 作為雜湊表（鏈結法）、鄰接串列（圖論）與 LRU 快取的基礎。

---

## 3. Typical Patterns（典型題型 / 模式）

For Senior roles, simple iteration is assumed. Focus on these patterns:
對於資深職位，簡單的迭代已被視為基本功。請專注於以下模式：

1.  **Sentinel / Dummy Node Strategy（哨兵/虛擬節點策略）**
    *   **Concept:** Place a node before the head to handle edge cases (like deleting the head) uniformly.
    *   **概念：** 在頭節點前放置一個節點，以統一處理邊界情況（如刪除頭節點）。
2.  **Fast & Slow Pointers (Floyd's Cycle-Finding)（快慢指標）**
    *   **Concept:** Use two pointers moving at different speeds to detect cycles or find the midpoint.
    *   **概念：** 使用兩個移動速度不同的指標來偵測循環或尋找中點。
3.  **Reverse in Groups / Recursion（分組反轉/遞迴）**
    *   **Concept:** Processing the list in chunks ($K$ nodes at a time) requiring complex wiring of `prev`, `curr`, and `next`.
    *   **概念：** 分塊處理串列（每次 $K$ 個節點），需要複雜的 `prev`、`curr` 與 `next` 連接。
4.  **Merging & Sorting（合併與排序）**
    *   **Concept:** Merge Sort is the preferred algorithm for sorting Linked Lists ($O(N \log N)$ time, $O(1)$ space if implemented iteratively).
    *   **概念：** 合併排序是排序鏈結串列的首選演算法（時間 $O(N \log N)$，若採迭代實作則空間 $O(1)$）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Reverse Nodes in k-Group (Hard)
### 問題：K 個一組翻轉鏈結串列（困難）

**Problem Statement:**
Given the head of a linked list, reverse the nodes of the list $k$ at a time, and return the modified list. If the number of nodes is not a multiple of $k$, then left-out nodes, in the end, should remain as it is.
給定一個鏈結串列的頭節點，每 $k$ 個節點一組進行翻轉，並返回修改後的串列。如果節點數量不是 $k$ 的倍數，則最後剩餘的節點應保持原樣。

---

### Strategy: From Brute Force to Optimal
### 思路：從暴力法到最佳解

1.  **Naive Approach (Stack):**
    *   Store $k$ nodes in a stack (array), then pop them to create a new list.
    *   **Critique:** $O(N)$ space. Senior engineers must optimize for $O(1)$ space.
    *   **直觀法（堆疊）：** 將 $k$ 個節點存入堆疊（陣列），然後彈出以建立新串列。
    *   **評論：** 空間複雜度 $O(N)$。資深工程師必須優化至 $O(1)$ 空間。

2.  **Optimal Approach (Iterative Pointer Manipulation):**
    *   Use a **Dummy Node** to simplify the head reversal.
    *   Count length or probe ahead to check if $k$ nodes exist.
    *   Reverse the sub-segment.
    *   Connect the `pre` segment to the new head of the reversed segment, and the new tail to the `next` segment.
    *   **最佳解（迭代指標操作）：**
    *   使用 **Dummy Node** 簡化頭部反轉。
    *   計算長度或向前探查以確認是否有 $k$ 個節點。
    *   反轉子區段。
    *   將 `pre` 區段連接到反轉後的新頭部，並將新尾部連接到 `next` 區段。

---

### TypeScript Reference Solution (Bilingual Comments)
### TypeScript 參考解（雙語註解）

```typescript
// Definition for singly-linked list.
class ListNode {
    val: number
    next: ListNode | null
    constructor(val?: number, next?: ListNode | null) {
        this.val = (val === undefined ? 0 : val)
        this.next = (next === undefined ? null : next)
    }
}

function reverseKGroup(head: ListNode | null, k: number): ListNode | null {
    if (!head || k === 1) return head;

    // 1. Use a dummy node to handle the edge case where the head itself changes.
    // 1. 使用虛擬節點來處理頭節點本身會改變的邊界情況。
    const dummy = new ListNode(0);
    dummy.next = head;

    // 'pre' points to the node immediately before the group we are reversing.
    // 'pre' 指向我們即將反轉的群組之前的那一個節點。
    let pre = dummy;
    let end: ListNode | null = dummy;

    while (end.next !== null) {
        // 2. Move 'end' k steps forward to define the group boundary.
        // 2. 將 'end' 向前移動 k 步以定義群組邊界。
        for (let i = 0; i < k && end !== null; i++) {
            end = end.next;
        }

        // If fewer than k nodes remain, we stop (do not reverse).
        // 如果剩餘節點少於 k 個，我們停止（不進行反轉）。
        if (end === null) break;

        // 3. Identify the start of the group and the node after the group.
        // 3. 識別群組的起始點以及群組後的下一個節點。
        let start = pre.next!;
        let nextGroup = end.next;

        // 4. Break the link to isolate the group for reversal.
        // 4. 斷開連結以隔離該群組進行反轉。
        end.next = null;

        // 5. Reverse the isolated group and connect it back.
        // 5. 反轉被隔離的群組並將其接回。
        pre.next = reverse(start);
        
        // After reversal, 'start' becomes the tail of this group. Connect it to nextGroup.
        // 反轉後，'start' 變成了該群組的尾部。將其連接到 nextGroup。
        start.next = nextGroup;

        // 6. Move pointers for the next iteration.
        // 6. 移動指標以進行下一次迭代。
        pre = start;
        end = pre;
    }

    return dummy.next;
}

// Helper function: Standard Linked List Reversal
// 輔助函式：標準鏈結串列反轉
function reverse(head: ListNode | null): ListNode | null {
    let prev: ListNode | null = null;
    let curr = head;
    
    while (curr !== null) {
        let nextTemp = curr.next; // Save next / 保存下一個
        curr.next = prev;         // Reverse link / 反轉連結
        prev = curr;              // Move prev / 移動 prev
        curr = nextTemp;          // Move curr / 移動 curr
    }
    return prev;
}
```

### Common Mistake (Error Demo)
### 常見錯誤（錯誤示範）

```typescript
// WRONG: Losing reference to the rest of the list
// 錯誤：失去對串列其餘部分的參照
let curr = head;
for(let i=0; i<k; i++) {
    let next = curr.next;
    curr.next = prev; // If you don't track the connection to the OUTSIDE of the group...
                      // 如果你沒有追蹤與群組「外部」的連接...
}
// Result: You reverse the sublist but cannot reconnect it to the main list.
// 結果：你反轉了子串列，但無法將其重新連接回主串列。
```

---

## 5. Common Pitfalls & Confusing Concepts（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Node Value (`val`)** | **Node Reference (`next`)** | Changing `val` updates data; changing `next` rewires the structure. Beginners confuse copying a node vs. copying a reference. <br> 改變 `val` 更新數據；改變 `next` 重組結構。初學者常混淆複製節點與複製參照。 |
| **Logical Deletion** | **Memory Deletion** | In TS/JS, removing a reference allows Garbage Collection. In C++, you must manually `delete`. Mentioning this shows seniority. <br> 在 TS/JS 中，移除參照即可觸發垃圾回收。在 C++ 中需手動 `delete`。提及此點能展現資深程度。 |
| **Odd vs Even Length** | **Midpoint Finding** | When using Fast/Slow pointers, the stop condition differs slightly for odd/even lengths. Always test both. <br> 使用快慢指標時，奇偶長度的停止條件略有不同。務必兩者都測試。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarification Phase (The "Senior" Check)
### 釐清階段（「資深」檢核）
*   **Input Constraints:** "Does the linked list fit in memory? If not, we might need external sorting."
    **輸入限制：** 「鏈結串列是否能完全放入記憶體？如果不能，我們可能需要外部排序。」
*   **Structure:** "Is it singly or doubly linked? Is it circular?"
    **結構：** 「是單向還是雙向鏈結？是循環的嗎？」

### 2. Whiteboard Strategy
### 白板策略
*   **Draw it out:** Always draw nodes as boxes and pointers as arrows.
    **畫出來：** 永遠將節點畫成方塊，指標畫成箭頭。
*   **Visualize the "Before" and "After":** Specifically for reversal problems, draw the state of pointers (`prev`, `curr`, `next`) at step $i$.
    **視覺化「前」與「後」：** 特別是反轉問題，畫出第 $i$ 步時指標（`prev`, `curr`, `next`）的狀態。

### 3. Follow-up Questions
### 常見追問
*   **Q:** How to handle concurrent access?
    **A:** Discuss **Fine-grained locking** (locking individual nodes) vs. **Coarse-grained locking** (locking the whole list), or **Lock-free** structures (CAS operations).
    **問：** 如何處理並發存取？
    **答：** 討論**細粒度鎖**（鎖定個別節點）與**粗粒度鎖**（鎖定整個串列），或**無鎖**結構（CAS 操作）。

---

## 7. Practice Problems（練習題）

### Easy: Merge Two Sorted Lists
### 簡單：合併兩個已排序串列
*   **Hint:** Use a recursive approach for elegance or iterative with a dummy head for performance.
*   **提示：** 使用遞迴法追求優雅，或使用帶有虛擬頭節點的迭代法追求效能。

### Medium: Reorder List ($L_0 \to L_n \to L_1 \to L_{n-1} \dots$)
### 中等：重排鏈結串列
*   **Hint:** This is a combination of 3 skills: Find Middle (Fast/Slow) + Reverse Second Half + Merge Two Lists.
*   **提示：** 這是三種技巧的結合：找中點（快慢指標）+ 反轉後半部 + 合併兩個串列。

### Hard: Copy List with Random Pointer
### 困難：複製帶有隨機指標的鏈結串列
*   **Hint:** Can be done in $O(1)$ space (interweaving nodes: $A \to A' \to B \to B'$) or $O(N)$ space (using a HashMap `Map<OldNode, NewNode>`).
*   **提示：** 可用 $O(1)$ 空間（交織節點：$A \to A' \to B \to B'$）或 $O(N)$ 空間（使用雜湊表 `Map<OldNode, NewNode>`）完成。

---

## 8. Quick Checklists（快速檢核表）

Use this before submitting your code:
在提交程式碼前使用此表：

- [ ] **Null Head Check:** Did I handle `head === null` or `head.next === null`?
    **空頭檢查：** 我是否處理了 `head === null` 或 `head.next === null`？
- [ ] **Cycle Check:** Did I create a cycle by pointing a node to itself or a previous node unintentionally?
    **循環檢查：** 我是否不小心將節點指向自己或前一個節點而產生了循環？
- [ ] **Lost Head:** Do I still have a reference to the new head of the list? (Usage of `dummy.next`).
    **遺失頭部：** 我是否還持有串列新頭部的參照？（使用 `dummy.next`）。
- [ ] **Tail Termination:** Does the new tail point to `null`? (Crucial for preventing infinite loops in traversal).
    **尾部終止：** 新的尾部是否指向 `null`？（對於防止遍歷時的無窮迴圈至關重要）。

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The Treasure Hunt (Pointer Traversal):**
    You only have the map to the *next* location. You cannot look at the whole map at once. If you lose the piece of paper (pointer) to the next spot, the rest of the treasure is lost forever.
    **尋寶遊戲（指標遍歷）：**
    你只有前往*下一個*地點的地圖。你無法一次看到整張地圖。如果你弄丟了前往下一站的紙條（指標），剩下的寶藏就永遠丟失了。

*   **The Train Couplers (Insertion/Deletion):**
    To remove a train car, you must unhook the coupler from the *previous* car and attach it to the *next* car. If you just pull the car out without re-coupling, the train breaks apart.
    **火車掛鉤（插入/刪除）：**
    要移除一節車廂，你必須解開*前一節*車廂的掛鉤，並將其扣在*後一節*車廂上。如果你只是把車廂拉出來而沒有重新掛鉤，火車就會斷裂。