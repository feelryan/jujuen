Here is the comprehensive interview guide for **Linked List**, tailored for a Senior Software Engineer, at the **Advanced** level, using **C++**.

這是一份針對 **Linked List（鏈結串列）** 的完整面試教材，專為資深軟體工程師設計，難度設定為 **Advanced（進階）**，並使用 **C++** 撰寫。

---

# Advanced Linked List Guide for Senior Engineers
# 資深工程師進階鏈結串列指南

## 1. Learning Objectives（學習目標）

*   **Master Complex Pointer Manipulation:** Perform intricate rewiring (e.g., reversing in groups, flattening) without memory leaks or segmentation faults.
    **掌握複雜指標操作：** 執行錯綜複雜的重連操作（如分組反轉、扁平化），且不發生記憶體洩漏或區段錯誤（Segmentation Faults）。
*   **Deep Understanding of Memory Layout:** Analyze the impact of non-contiguous memory on CPU cache locality compared to arrays.
    **深刻理解記憶體佈局：** 分析非連續記憶體相較於陣列對 CPU 快取局部性（Cache Locality）的影響。
*   **System Design Integration:** Understand how Linked Lists form the backbone of complex structures like LRU/LFU Caches, Memory Allocators, and Skip Lists.
    **系統設計整合：** 理解鏈結串列如何構成 LRU/LFU 快取、記憶體配置器（Allocators）與跳躍表（Skip Lists）等複雜結構的骨幹。
*   **C++ Specific Proficiency:** Demonstrate mastery of raw pointers versus smart pointers (`unique_ptr`, `shared_ptr`) in a systems context.
    **C++ 特有精通度：** 在系統情境中展示對原始指標與智慧指標（`unique_ptr`、`shared_ptr`）的掌握。

---

## 2. Core Concepts Snapshot（核心觀念速覽）

### Definition & Intuition（定義與直覺）
A Linked List is a linear data structure where elements are not stored at contiguous memory locations; elements are linked using pointers.
鏈結串列是一種線性資料結構，其元素不儲存於連續的記憶體位置；元素透過指標連結。

**Intuition:** Think of a **Treasure Hunt**. You only have the clue to the next location, not a map of the entire area.
**直覺：** 想像一場**尋寶遊戲**。你只擁有前往下一個地點的線索，而不是整個區域的地圖。

### Complexity Analysis（複雜度分析）

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Access (Index)** | $O(N)$ | $O(1)$ | No random access; requires traversal. (無隨機存取；需遍歷) |
| **Search** | $O(N)$ | $O(1)$ | Worst case requires scanning the whole list. (最差情況需掃描全表) |
| **Insert/Delete (Head)** | $O(1)$ | $O(1)$ | Immediate pointer update. (立即更新指標) |
| **Insert/Delete (Known Node)**| $O(1)$ | $O(1)$ | If you already hold the pointer to the target/prev node. (若已持有目標或前驅節點的指標) |

### Advanced Context: Why NOT use Linked Lists?（進階情境：為何**不**使用鏈結串列？）
For Senior Engineers, the answer isn't just "slow search." It is **Cache Misses**.
對於資深工程師，答案不只是「搜尋慢」。重點在於 **快取未命中（Cache Misses）**。
Arrays profit from spatial locality (prefetching); Linked List nodes can be scattered across the heap, causing frequent CPU pipeline stalls.
陣列受惠於空間局部性（預取）；鏈結串列的節點可能散落在堆積（Heap）各處，導致頻繁的 CPU 管線停頓。

---

## 3. Typical Patterns / Modes（典型題型 / 模式）

For advanced interviews, basic traversal is assumed. Focus on these patterns:
對於進階面試，基本的遍歷被視為理所當然。請專注於以下模式：

1.  **Pointer Rewiring / Surgery (指標重連/手術):**
    *   Reversing segments, swapping nodes, flattening multilevel lists.
    *   反轉片段、交換節點、扁平化多層串列。
2.  **Cycle & Intersection Detection (Floyd's Cycle-Finding):**
    *   Detecting loops and finding entry points using fast/slow pointers.
    *   使用快慢指標偵測迴圈並找出進入點。
3.  **Merge & Sort (合併與排序):**
    *   Merge Sort on Linked Lists (O(1) space unlike array merge sort).
    *   鏈結串列上的合併排序（不同於陣列合併排序，此為 O(1) 空間）。
4.  **Deep Copy with Random Pointers (含隨機指標的深拷貝):**
    *   Mapping old nodes to new nodes via Hash Map or Interweaving.
    *   透過雜湊表或交錯編織（Interweaving）將舊節點映射至新節點。
5.  **Doubly Linked List for Caches (用於快取的雙向鏈結串列):**
    *   Implementing O(1) `move_to_head` for LRU.
    *   實作 LRU 所需的 O(1) `move_to_head` 操作。

---

## 4. Example Walkthrough（範例講解）

### Problem: Reverse Nodes in k-Group (LeetCode 25)
**問題：K 個一組翻轉鏈結串列**

**Problem Statement:**
Given the head of a linked list, reverse the nodes of the list $k$ at a time, and return the modified list. If the number of nodes is not a multiple of $k$ then left-out nodes, in the end, should remain as it is.
給定一個鏈結串列的頭節點，每 $k$ 個節點一組進行翻轉，並返回修改後的串列。如果節點數量不是 $k$ 的倍數，則最後剩餘的節點應保持原狀。

### Approach: Optimization Strategy（思路：優化策略）

1.  **Brute Force (Stack/Array):**
    *   Read $k$ nodes into a stack/array, pop them to reverse values or pointers.
    *   將 $k$ 個節點讀入堆疊/陣列，彈出以反轉數值或指標。
    *   *Critique:* $O(N)$ space complexity. Not acceptable for a Senior role targeting systems programming.
    *   *評論：* $O(N)$ 空間複雜度。對於針對系統程式設計的資深職位來說不可接受。

2.  **Iterative Pointer Rewiring (Best Practice):**
    *   Use a `dummy` node to handle the head change easily.
    *   使用 `dummy`（啞節點）來輕鬆處理頭部變更。
    *   Check if there are $k$ nodes left. If yes, reverse them; if no, stop.
    *   檢查是否剩餘 $k$ 個節點。若是，則反轉；若否，則停止。
    *   Maintain `prev_group_tail` to connect the reversed segment back to the main list.
    *   維護 `prev_group_tail` 以將反轉後的片段接回主串列。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <iostream>
#include <utility>

// Definition for singly-linked list.
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution {
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        if (!head || k == 1) return head;

        // Dummy node simplifies edge cases where the head itself changes.
        // Dummy 節點簡化了頭部本身發生變化的邊界情況。
        ListNode* dummy = new ListNode(0);
        dummy->next = head;
        
        ListNode* prev_group_tail = dummy;
        ListNode* curr = head;

        while (curr) {
            // 1. Check if there are k nodes left to reverse
            // 1. 檢查是否剩下 k 個節點可供反轉
            ListNode* tail = curr;
            int count = 0;
            while (curr && count < k) {
                curr = curr->next;
                count++;
            }

            if (count < k) {
                // Less than k nodes remaining, no need to reverse.
                // 剩餘節點不足 k 個，無需反轉。
                break;
            }

            // 2. Reverse the group (standard linked list reversal)
            // 2. 反轉該組（標準鏈結串列反轉）
            // 'tail' is actually the START of the group before reversal.
            // 'tail' 實際上是反轉前該組的「起始」節點。
            // 'curr' is now the first node of the NEXT group.
            // 'curr' 現在是「下一組」的第一個節點。
            
            ListNode* group_head = prev_group_tail->next;
            ListNode* prev = curr; // Connect to the next group immediately (trick) / 立即連接到下一組（技巧）
            ListNode* temp_curr = group_head;
            
            while (count > 0) {
                ListNode* next_node = temp_curr->next;
                temp_curr->next = prev;
                prev = temp_curr;
                temp_curr = next_node;
                count--;
            }

            // 3. Connect previous group to the new head of this reversed group
            // 3. 將前一組連接到此反轉組的新頭部
            // 'prev' is now the new head of this reversed group.
            // 'prev' 現在是此反轉組的新頭部。
            prev_group_tail->next = prev;
            
            // 4. Update pointer for the next iteration
            // 4. 更新指標以進行下一次迭代
            // 'group_head' is now the tail of the reversed group.
            // 'group_head' 現在是反轉組的尾部。
            prev_group_tail = group_head; 
        }

        ListNode* new_head = dummy->next;
        delete dummy; // Avoid memory leak / 避免記憶體洩漏
        return new_head;
    }
};
```

### Complexity & Edge Cases
*   **Time:** $O(N)$ - Each node is visited at most twice (once for counting, once for reversing).
    **時間：** $O(N)$ - 每個節點最多被訪問兩次（一次計數，一次反轉）。
*   **Space:** $O(1)$ - Only pointers are used.
    **空間：** $O(1)$ - 僅使用指標。
*   **Edge Cases:** $k=1$, $k > length$, empty list.
    **邊界條件：** $k=1$， $k > 長度$，空串列。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Trap / Confusion (陷阱 / 混淆) | Correction (修正) |
| :--- | :--- | :--- |
| **Memory Management** | Forgetting to `delete` dummy nodes or removed nodes in C++. | Always clean up heap memory in C++ unless using smart pointers or specifically told memory is managed by a pool. <br> 在 C++ 中務必清理堆積記憶體，除非使用智慧指標或已知有記憶體池管理。 |
| **Pointer Loss** | Overwriting `curr->next` before saving the next node. <br> 在保存下一個節點前覆蓋 `curr->next`。 | Always cache `next_node = curr->next` before breaking the link. <br> 在斷開連結前，永遠先快取 `next_node = curr->next`。 |
| **Head Updates** | Returning the original `head` after the list structure changed. <br> 在串列結構改變後返回原始的 `head`。 | Use a `dummy` node and return `dummy->next`. <br> 使用 `dummy` 節點並返回 `dummy->next`。 |
| **Cycle Termination** | Iterating forever in a cyclic list. <br> 在環狀串列中無限迭代。 | Use Floyd’s Cycle detection or a Hash Set to track visited nodes. <br> 使用 Floyd 判圈法或雜湊集合追蹤已訪問節點。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **Clarify Constraints:** "Is this a singly or doubly linked list? Can I modify the values, or must I only change pointers?"
    **釐清限制：** 「這是單向還是雙向鏈結串列？我可以修改數值嗎，還是必須只改變指標？」
2.  **State the Trade-off:** "I can do this recursively for cleaner code, but it uses O(N) stack space. I will implement the iterative approach for O(1) space efficiency."
    **說明權衡：** 「我可以用遞迴寫出更簡潔的程式碼，但會消耗 O(N) 堆疊空間。我將實作迭代法以達到 O(1) 空間效率。」
3.  **Visual Debugging:** Draw boxes and arrows. When you change a pointer, erase the old arrow and draw a new one.
    **視覺除錯：** 畫出方塊與箭頭。當你改變指標時，擦掉舊箭頭並畫上新的。

### Common Follow-ups（常見追問）
*   **Concurrency:** "How would you make this thread-safe?" (Answer: Fine-grained locking, Lock-free CAS operations, or Read-Copy-Update).
    **並發性：** 「你會如何使其具備執行緒安全？」 （回答：細粒度鎖、無鎖 CAS 操作，或 RCU）。
*   **Scale:** "What if the list is too large for RAM?" (Answer: Store nodes on disk, treat pointers as file offsets/IDs).
    **規模：** 「如果串列大到記憶體裝不下怎麼辦？」 （回答：將節點存於磁碟，將指標視為檔案偏移量/ID）。

---

## 7. Practice Problems（練習題）

### 1. Easy (Warm-up): Merge Two Sorted Lists
**題目：合併兩個排序鏈結串列**
*   **Hint:** Use a recursive approach first for logic check, then optimize to iterative with a dummy head.
*   **提示：** 先用遞迴法檢查邏輯，再優化為帶有 dummy head 的迭代法。
*   **Focus:** Code cleanliness and null checks. (專注於程式碼整潔度與空值檢查)。

### 2. Intermediate: Copy List with Random Pointer (LeetCode 138)
**題目：複製帶隨機指標的鏈結串列**
*   **Hint:** Can you do this without a Hash Map? Try interweaving the new nodes ($A \to A' \to B \to B'$).
*   **提示：** 能否不使用雜湊表完成？嘗試交錯編織新節點 ($A \to A' \to B \to B'$)。
*   **Goal:** $O(N)$ Time, $O(1)$ Space.

### 3. Advanced: Merge k Sorted Lists (LeetCode 23)
**題目：合併 k 個排序鏈結串列**
*   **Hint:** Don't just merge one by one ($O(kN)$). Use a Min-Heap (Priority Queue) or Divide & Conquer.
*   **提示：** 不要只是一個接一個合併 ($O(kN)$)。使用最小堆積（優先佇列）或分治法。
*   **Senior Check:** Discuss the cache locality difference between the Heap approach vs. Divide & Conquer.
*   **資深檢核：** 討論堆積解法與分治法在快取局部性上的差異。

---

## 8. Quick Checklists（快速檢核表）

**Self-Review before running code:**
**執行程式碼前的自我審查：**

*   [ ] Did I handle the case where `head` is `nullptr`? (我是否處理了 `head` 為 `nullptr` 的情況？)
*   [ ] Did I handle the case with a single node? (我是否處理了只有一個節點的情況？)
*   [ ] If I used a `while(curr->next)` loop, did I check if `curr` itself is valid first? (如果我用了 `while(curr->next)`，我有先檢查 `curr` 是否有效嗎？)
*   [ ] Did I break any cycles I created? (我是否打破了我建立的任何迴圈？)
*   [ ] **C++ Specific:** Did I `delete` any temporary nodes (like dummy) to prevent leaks? (C++ 特有：我是否刪除了臨時節點如 dummy 以防止洩漏？)

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The Train Coupler (火車掛鉤):**
    *   Manipulating Linked Lists is like uncoupling and recoupling train cars. You cannot uncouple the current car from the next one until you have attached a chain to the next one, or you lose the rest of the train forever.
    *   操作鏈結串列就像解開並重新掛上火車車廂。在將鏈條掛到下一節車廂之前，你不能解開當前車廂與下一節的連結，否則你會永遠失去剩下的列車。

*   **The Dummy Node (替身演員):**
    *   The `dummy` node is a stunt double. It stands at the front of the line so the real star (`head`) can move around, get swapped, or disappear without the director losing track of where the scene starts.
    *   `dummy` 節點是替身演員。它站在隊伍最前面，讓真正的明星（`head`）可以移動、被交換或消失，而導演不會失去場景開始位置的追蹤。