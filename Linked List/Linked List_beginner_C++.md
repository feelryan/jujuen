Here is the complete interview guide for **Linked List (Beginner Level)**, tailored for a Senior Software Engineer transitioning to C++.

這是一份針對 **Linked List（鏈結串列 - 初級篇）** 的完整面試指南，專為準備轉用 C++ 的資深軟體工程師量身打造。

---

# Linked List: Foundations & Memory Manipulation
# 鏈結串列：基礎與記憶體操作

## 1. Learning Goals (學習目標)

*   **Master Pointer Manipulation in C++:** Understand the difference between `Node*`, `Node**`, and how to safely navigate memory without segmentation faults.
    **掌握 C++ 指標操作：** 理解 `Node*` 與 `Node**` 的差異，以及如何在不發生區段錯誤（Segmentation Fault）的情況下安全地遍歷記憶體。
*   **Internalize the "Dummy Head" Technique:** Learn to use a sentinel node to simplify edge cases (like inserting/deleting at the head).
    **內化「虛擬頭節點（Dummy Head）」技巧：** 學習使用哨兵節點來簡化邊界情況（如在頭部進行插入或刪除）。
*   **Standardize Iteration Patterns:** Solidify the `while(curr != nullptr)` and `while(curr->next != nullptr)` loops.
    **標準化迭代模式：** 鞏固 `while(curr != nullptr)` 與 `while(curr->next != nullptr)` 的迴圈寫法。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Linked List is a linear data structure where elements are not stored at contiguous memory locations.
鏈結串列是一種線性資料結構，其元素並非儲存在連續的記憶體位置。
Instead, each element (node) points to the next, forming a chain.
取而代之的是，每個元素（節點）指向下一個元素，形成一條鏈。

### Intuition (直覺)
Think of a scavenger hunt where each clue holds the location of the next clue.
想像這是一場尋寶遊戲，每一條線索都包含下一條線索的位置。
You cannot jump to the 5th clue without visiting the previous 4.
你無法在不訪問前 4 條線索的情況下直接跳到第 5 條。

### Complexity (複雜度)

| Operation | Time Complexity (時間複雜度) | Space Complexity (空間複雜度) | Note (備註) |
| :--- | :--- | :--- | :--- |
| **Access (Access $i$-th element)** | $O(N)$ | $O(1)$ | Must traverse from head (必須從頭遍歷) |
| **Search (Find value)** | $O(N)$ | $O(1)$ | Linear scan (線性掃描) |
| **Insert/Delete (at Head)** | $O(1)$ | $O(1)$ | Very efficient (非常高效) |
| **Insert/Delete (at arbitrary pos)**| $O(N)$ | $O(1)$ | Time spent finding the position (時間花在尋找位置) |

### When to Use (適用場景)
*   Constant-time insertions/deletions at the beginning or end (with tail pointer).
    在開頭或結尾（若有尾指標）進行常數時間的插入/刪除。
*   Dynamic size requirements where memory is fragmented.
    記憶體破碎且需要動態大小的場景。

### When NOT to Use (不適用場景)
*   Random access is required (e.g., Binary Search).
    需要隨機存取時（例如：二分搜尋）。
*   Cache locality is critical (Linked Lists have poor cache performance compared to Arrays).
    快取局部性至關重要時（鏈結串列的快取效能遠低於陣列）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner level, focus on these three patterns:
針對初級階段，請專注於以下三種模式：

1.  **Single Pass Iteration (單趟遍歷):**
    Traversing the list to calculate length, find an element, or print values.
    遍歷串列以計算長度、尋找元素或列印數值。
2.  **Two Pointers (雙指標 - Basic):**
    Using `prev` and `curr` to modify links (e.g., delete a node).
    使用 `prev` 和 `curr` 來修改連結（例如：刪除節點）。
3.  **Dummy Head (虛擬頭節點):**
    Creating a temporary node that points to `head` to handle cases where the head itself might change.
    建立一個指向 `head` 的臨時節點，用來處理頭節點本身可能發生變化的情況。

---

## 4. Example Walkthrough (範例講解)

### Problem: Reverse Linked List (反轉鏈結串列)

**Problem Statement:**
Given the `head` of a singly linked list, reverse the list, and return the reversed list.
給定單向鏈結串列的 `head`，請反轉該串列，並回傳反轉後的串列。

**Input:** `1 -> 2 -> 3 -> nullptr`
**Output:** `3 -> 2 -> 1 -> nullptr`

### Approach 1: Naive / Brute Force (Iterative with Stack)
**Idea:** Traverse the list, push values onto a stack, then create a new list by popping values.
**思路：** 遍歷串列，將數值推入堆疊，然後透過彈出數值來建立新串列。
**Critique:** Time $O(N)$, Space $O(N)$. We can do better in space.
**評論：** 時間 $O(N)$，空間 $O(N)$。我們可以在空間上做得更好。

### Approach 2: Optimal Iterative (In-Place)
**Idea:** Change the `next` pointer of each node to point to its previous node.
**思路：** 將每個節點的 `next` 指標改為指向其前一個節點。
**Key:** We need three pointers: `prev`, `curr`, and `next_temp`.
**關鍵：** 我們需要三個指標：`prev`、`curr` 和 `next_temp`。

### C++ Reference Solution (C++ 參考解)

```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */

class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        // Initialize prev to nullptr because the new tail will point to nothing.
        // 初始化 prev 為 nullptr，因為新的尾節點將指向空。
        ListNode* prev = nullptr;
        
        // Initialize curr to the head of the list.
        // 初始化 curr 為串列的頭。
        ListNode* curr = head;
        
        while (curr != nullptr) {
            // 1. Save the next node, otherwise we lose the rest of the chain.
            // 1. 保存下一個節點，否則我們會丟失剩下的鏈。
            ListNode* next_temp = curr->next;
            
            // 2. Reverse the pointer: point current node backwards to prev.
            // 2. 反轉指標：將當前節點指向後方的 prev。
            curr->next = prev;
            
            // 3. Move prev one step forward (to current node).
            // 3. 將 prev 向前移動一步（移至當前節點）。
            prev = curr;
            
            // 4. Move curr one step forward (to the saved next node).
            // 4. 將 curr 向前移動一步（移至保存的下一個節點）。
            curr = next_temp;
        }
        
        // At the end, curr is nullptr, and prev is the new head.
        // 結束時，curr 為 nullptr，而 prev 是新的頭節點。
        return prev;
    }
};
```

### Error Demonstration (錯誤示範)

```cpp
// WRONG CODE
while (curr != nullptr) {
    curr->next = prev; // Error: You just broke the link to the rest of the list!
                       // 錯誤：你剛剛斷開了與串列其餘部分的連結！
    prev = curr;
    curr = curr->next; // Error: curr->next is now pointing to prev (backwards). Infinite loop or wrong logic.
                       // 錯誤：curr->next 現在指向 prev（往回指）。會導致無窮迴圈或邏輯錯誤。
}
```

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept | Description (描述) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Dereferencing Null** | Accessing `node->next` or `node->val` when `node` is `nullptr`. <br> 當 `node` 為 `nullptr` 時存取 `node->next` 或 `node->val`。 | Forgetting to check `if (!head)` or `while (curr)`. <br> 忘記檢查 `if (!head)` 或 `while (curr)`。 |
| **Lost Head** | Moving the `head` pointer during traversal without keeping a reference. <br> 在遍歷過程中移動 `head` 指標，卻沒有保留參考。 | Returning the modified `head` which is now at the end or `nullptr`. <br> 回傳被修改過的 `head`，它現在可能在尾端或是 `nullptr`。 |
| **Memory Leak (C++)** | Removing a node from the list but failing to `delete` it. <br> 從串列中移除節點但忘記 `delete` 它。 | In interviews, clarify if you own the memory. In LeetCode, usually ignored; in system design, critical. <br> 面試時需釐清記憶體所有權。LeetCode 通常忽略；系統設計中則至關重要。 |
| **`curr` vs `curr->next`** | Loop condition logic. <br> 迴圈條件邏輯。 | Using `while(curr->next)` will skip the last node processing or crash on empty list. <br> 使用 `while(curr->next)` 會跳過最後一個節點的處理，或在空串列時崩潰。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Oral Framework (口條框架)
*   **Start with Edge Cases:** "First, I'll handle the case where the list is empty or has only one node."
    **從邊界情況開始：**「首先，我會處理串列為空或只有一個節點的情況。」
*   **Explain the Pointer Movement:** "I will use pointers to traverse the list. I need to be careful not to lose the reference to the next node."
    **解釋指標移動：**「我會使用指標來遍歷串列。我需要小心不要丟失對下一個節點的引用。」

### 2. Whiteboard Strategy (白板策略)
*   **Draw Boxes and Arrows:** Always draw a visual representation: `[1] -> [2] -> [3] -> X`.
    **畫出方框與箭頭：** 永遠畫出視覺化表示：`[1] -> [2] -> [3] -> X`。
*   **Trace the Code:** Use a table to track `prev`, `curr`, and `next` values at each iteration.
    **追蹤程式碼：** 使用表格來追蹤每一次迭代中的 `prev`、`curr` 和 `next` 的值。

### 3. Common Follow-ups (常見追問)
*   **Recursive Solution:** "Can you solve this recursively?" (Be ready for stack overflow discussions).
    **遞迴解法：**「你能用遞迴解決這個問題嗎？」（準備好討論堆疊溢位問題）。
*   **Constant Space:** "Can you do this without allocating new nodes?"
    **常數空間：**「你能不配置新節點來完成嗎？」

---

## 7. Practice Problems (練習題)

### Level: Easy (Merge Two Sorted Lists)
**Problem:** Merge two sorted linked lists and return it as a sorted list.
**問題：** 合併兩個已排序的鏈結串列，並將其作為一個排序串列回傳。
**Hint:** Use a **Dummy Head** to build the result easily. Compare `list1->val` and `list2->val`.
**提示：** 使用 **虛擬頭節點（Dummy Head）** 來輕鬆建構結果。比較 `list1->val` 與 `list2->val`。

### Level: Medium (Remove Nth Node From End of List)
**Problem:** Remove the $n$-th node from the end of the list and return its head.
**問題：** 移除串列倒數第 $n$ 個節點並回傳頭節點。
**Hint:** Use **Two Pointers** (Fast and Slow). Move `fast` $n$ steps ahead, then move both until `fast` reaches the end.
**提示：** 使用 **雙指標**（快慢指標）。將 `fast` 向前移動 $n$ 步，然後同時移動兩者直到 `fast` 到達末端。

### Level: Hard (for Beginner topic) (Palindrome Linked List)
**Problem:** Given the head of a singly linked list, return true if it is a palindrome.
**問題：** 給定單向鏈結串列的頭，如果是迴文則回傳 true。
**Hint:** Find the middle (slow/fast), **reverse** the second half, then compare with the first half.
**提示：** 找出中間點（快慢指標），**反轉**後半部分，然後與前半部分進行比較。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Null Check:** Did I handle `head == nullptr`?
    **空值檢查：** 我是否處理了 `head == nullptr`？
*   [ ] **Single Node:** Does the code work if the list has only one node?
    **單一節點：** 如果串列只有一個節點，程式碼能運作嗎？
*   [ ] **Cycle Safety:** Did I ensure the loop terminates (e.g., `curr = curr->next`)?
    **迴圈安全：** 我是否確保迴圈會終止（例如：`curr = curr->next`）？
*   [ ] **Return Value:** Am I returning the correct new head (especially if the head changed)?
    **回傳值：** 我是否回傳了正確的新頭節點（特別是當頭節點改變時）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Train Cars (火車車廂):**
    Each node is a train car. The coupling (hook) is the pointer.
    每個節點是一節火車車廂。掛鉤就是指標。
    To rearrange cars, you must unhook (save `next`) before hooking to a new car (`curr->next = prev`). If you unhook without holding the rest of the train, the rest of the train rolls away and is lost forever.
    要重新排列車廂，你必須在掛上新車廂之前先解開掛鉤（保存 `next`）。如果你解開掛鉤卻沒有抓住剩下的列車，剩下的列車就會滑走並永遠丟失。

*   **The Dummy Head (虛擬頭節點):**
    Think of it as a "Handle" on a bucket. Even if the contents (the actual list) change or become empty, you still hold the handle.
    把它想像成水桶的「提把」。即使內容物（實際的串列）改變或變空，你仍然握著提把。