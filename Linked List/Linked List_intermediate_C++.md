Here is the comprehensive guide on **Linked Lists**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level with **C++** implementation.

這是針對資深軟體工程師量身打造的 **Linked List（鏈結串列）** 完整指南，專注於 **中階（Intermediate）** 難度並使用 **C++** 實作。

---

# Linked List: Intermediate Mastery (鏈結串列：中階精通)

## 1. Learning Objectives (學習目標)

*   **Master Pointer Manipulation & Memory Safety:**
    Gain absolute confidence in manipulating `next` pointers without causing memory leaks or segmentation faults (segfaults).
    **掌握指標操作與記憶體安全：** 建立對操作 `next` 指標的絕對信心，避免記憶體洩漏或區段錯誤（segfaults）。

*   **Internalize the "Fast & Slow Pointers" Pattern:**
    Understand how to use differential speeds to detect cycles, find midpoints, and solve distance-based problems in one pass.
    **內化「快慢指標」模式：** 理解如何利用速度差來偵測環、尋找中點，以及在一次遍歷中解決基於距離的問題。

*   **Proficiency in In-Place Operations:**
    Learn to reverse or reorder lists with $O(1)$ space complexity, a key differentiator in senior interviews.
    **精通原地（In-Place）操作：** 學習以 $O(1)$ 空間複雜度反轉或重排串列，這是資深面試中的關鍵區分點。

*   **Handle Edge Cases Gracefully:**
    Develop a reflex for handling `nullptr`, single-node lists, and cycles automatically.
    **優雅處理邊界情況：** 培養自動處理 `nullptr`、單節點串列與環狀結構的直覺反射。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Linked List is a linear data structure where elements are not stored at contiguous memory locations; instead, each element points to the next.
鏈結串列是一種線性資料結構，其元素並非儲存在連續的記憶體位置；相反地，每個元素都指向下一個元素。

### Intuition (直覺)
Think of a scavenger hunt where each clue leads only to the location of the next clue. You cannot jump to the 5th clue without visiting the 1st through 4th.
想像一場尋寶遊戲，每一條線索只指向下一條線索的位置。你無法在未訪問第 1 到第 4 條線索的情況下直接跳到第 5 條。

### Complexity (複雜度)

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Access (Search)** | $O(N)$ | $O(1)$ | Must traverse from head. (必須從頭遍歷) |
| **Insert/Delete (Known Node)** | $O(1)$ | $O(1)$ | If you already have the pointer to the position. (若已知位置指標) |
| **Insert/Delete (Arbitrary)** | $O(N)$ | $O(1)$ | Includes time to find the node. (包含尋找節點的時間) |

### When to Use / Not Use (適用與不適用場景)
*   **Use when:** Frequent insertions/deletions at the beginning or middle; size is dynamic and unknown.
    **適用於：** 在開頭或中間頻繁插入/刪除；大小動態且未知。
*   **Avoid when:** Random access is required (e.g., binary search); memory overhead per element (pointer storage) is a concern.
    **避免於：** 需要隨機存取（如二分搜尋）；在意每個元素的記憶體開銷（指標儲存）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Two Pointers (Fast & Slow / Tortoise & Hare)
Used for cycle detection, finding the middle node, or finding the $k$-th node from the end.
**雙指標（快慢指標 / 龜兔賽跑）：** 用於偵測環、尋找中間節點，或尋找倒數第 $k$ 個節點。

### B. Dummy Head (Sentinel Node)
Creating a placeholder node before the actual head to simplify insertion/deletion logic, eliminating the need to handle the "empty list" or "head change" as a special case.
**虛擬頭節點（哨兵節點）：** 在實際頭節點前建立一個佔位節點，以簡化插入/刪除邏輯，消除將「空串列」或「頭節點變更」作為特殊情況處理的需求。

### C. Reverse Logic (Iterative & Recursive)
Reversing links is the building block for complex problems like "Palindrome Check" or "Add Two Numbers".
**反轉邏輯（迭代與遞迴）：** 反轉連結是解決複雜問題（如「回文檢查」或「兩數相加」）的基石。

---

## 4. Example Walkthrough (範例講解)

### Problem: Reorder List (重排鏈結串列)
**LeetCode 143 (Medium)**

#### Problem Statement (問題重述)
You are given the head of a singly linked-list. The list can be represented as:
$L_0 \rightarrow L_1 \rightarrow \dots \rightarrow L_{n-1} \rightarrow L_n$
Reorder the list to be on the following form:
$L_0 \rightarrow L_n \rightarrow L_1 \rightarrow L_{n-1} \rightarrow L_2 \rightarrow L_{n-2} \rightarrow \dots$
You may not modify the values in the list's nodes. Only nodes themselves may be changed.

給定一個單向鏈結串列的頭節點。該串列表示為：
$L_0 \rightarrow L_1 \rightarrow \dots \rightarrow L_{n-1} \rightarrow L_n$
請將其重排為以下形式：
$L_0 \rightarrow L_n \rightarrow L_1 \rightarrow L_{n-1} \rightarrow L_2 \rightarrow L_{n-2} \rightarrow \dots$
你不能修改節點中的數值，只能改變節點本身。

---

#### Approach & Thought Process (思路)

**1. Naive Approach (Linear Table / Deque):**
Store all nodes in a `std::vector` or `std::deque`. Use two pointers (start and end) to reconstruct the list.
**直觀解法（線性表 / 雙端佇列）：** 將所有節點存入 `std::vector` 或 `std::deque`。使用雙指標（頭和尾）來重建串列。
*   *Space Complexity:* $O(N)$ - Not ideal for Senior level. (不理想)

**2. Optimal Approach (Split + Reverse + Merge):**
This problem is a combination of three sub-problems.
這個問題是三個子問題的組合。
1.  **Find the Middle:** Use Fast & Slow pointers to split the list into two halves.
    **尋找中點：** 使用快慢指標將串列分為兩半。
2.  **Reverse the Second Half:** Reverse the right half of the list.
    **反轉後半部：** 將串列的右半部反轉。
3.  **Merge Two Lists:** Alternately merge the first half and the reversed second half.
    **合併兩個串列：** 交替合併前半部與反轉後的後半部。

---

#### C++ Reference Solution (C++ 參考解)

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
    void reorderList(ListNode* head) {
        // Edge case: Empty list or single node needs no reordering.
        // 邊界情況：空串列或單節點無需重排。
        if (!head || !head->next) return;

        // Step 1: Find the middle of the list using Fast & Slow pointers.
        // 步驟 1：使用快慢指標尋找串列中點。
        ListNode* slow = head;
        ListNode* fast = head;
        
        // While fast can move two steps forward.
        // 當快指標可以向前移動兩步時。
        while (fast->next && fast->next->next) {
            slow = slow->next;
            fast = fast->next->next;
        }

        // 'slow' is now at the end of the first half.
        // 'slow' 現在位於前半部的末端。
        // Split the list into two parts.
        // 將串列切分為兩部分。
        ListNode* secondHalf = slow->next;
        slow->next = nullptr; // Terminate the first half. (終止前半部)

        // Step 2: Reverse the second half.
        // 步驟 2：反轉後半部。
        secondHalf = reverseList(secondHalf);

        // Step 3: Merge two halves alternately.
        // 步驟 3：交替合併兩半部。
        ListNode* firstHalf = head;
        while (secondHalf) {
            // Save next pointers to avoid losing references.
            // 保存 next 指標以避免遺失參照。
            ListNode* temp1 = firstHalf->next;
            ListNode* temp2 = secondHalf->next;

            // Link first half node to second half node.
            // 將前半部節點連結至後半部節點。
            firstHalf->next = secondHalf;
            // Link second half node to the next node in first half.
            // 將後半部節點連結至前半部的下一個節點。
            secondHalf->next = temp1;

            // Move pointers forward.
            // 移動指標向前。
            firstHalf = temp1;
            secondHalf = temp2;
        }
    }

private:
    // Helper function to reverse a linked list.
    // 輔助函式：反轉鏈結串列。
    ListNode* reverseList(ListNode* head) {
        ListNode* prev = nullptr;
        ListNode* curr = head;
        while (curr) {
            ListNode* nextTemp = curr->next; // Store next node (暫存下個節點)
            curr->next = prev;               // Reverse link (反轉連結)
            prev = curr;                     // Move prev forward (prev 向前移)
            curr = nextTemp;                 // Move curr forward (curr 向前移)
        }
        return prev; // New head (新的頭節點)
    }
};
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ — We traverse the list to find the middle, reverse half, and merge.
    **時間：** $O(N)$ — 我們遍歷串列以尋找中點、反轉一半並合併。
*   **Space:** $O(1)$ — We only use a few pointers for manipulation.
    **空間：** $O(1)$ — 我們僅使用少數指標進行操作。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Error | Explanation (解釋) |
| :--- | :--- |
| **Null Pointer Dereference** | **Fatal Error.** Accessing `node->next` when `node` is `nullptr`. Always check `if (node)` before access.<br>**致命錯誤。** 當 `node` 為 `nullptr` 時存取 `node->next`。存取前務必檢查 `if (node)`。 |
| **Losing the Head** | Moving the `head` pointer during traversal without keeping a backup reference. Use a `curr` pointer to traverse.<br>**遺失頭節點。** 在遍歷過程中移動 `head` 指標而未保留備份參照。請使用 `curr` 指標進行遍歷。 |
| **Cycle Creation** | Accidentally pointing a node back to a previous node in the same list during merging/reversing, creating an infinite loop.<br>**製造環路。** 在合併/反轉時意外將節點指向同一串列中的前一個節點，造成無窮迴圈。 |
| **Memory Leaks (C++)** | In C++, if you `delete` a node, ensure you've linked the previous node to the next one *before* deletion.<br>**記憶體洩漏 (C++)。** 在 C++ 中，若要 `delete` 一個節點，請確保在刪除 *之前* 已將前一個節點連結至下一個節點。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Clarify:** "Is it a singly or doubly linked list? Can I modify the structure in-place?"
    **釐清：** 「這是單向還是雙向鏈結串列？我可以原地修改結構嗎？」
2.  **Visualize:** Draw the list on the whiteboard. Draw arrows for pointer changes.
    **視覺化：** 在白板上畫出串列。畫出箭頭來表示指標的變更。
3.  **Edge Cases:** "I will handle the empty list and single-node list cases first."
    **邊界情況：** 「我會先處理空串列與單節點串列的情況。」
4.  **Dry Run:** Trace your code with a small example (e.g., 3-4 nodes) manually.
    **手動演練：** 用一個小範例（如 3-4 個節點）手動追蹤你的程式碼。

### Common Follow-ups (常見追問)
*   "How would you solve this if the list is too large to fit in RAM?" (External sorting/merging)
    「如果串列太大無法放入記憶體，你會如何解決？」
*   "Can you do this recursively?" (Tests stack overflow awareness)
    「你能用遞迴解嗎？」（測試對堆疊溢位的意識）

---

## 7. Practice Problems (練習題)

### Easy: Merge Two Sorted Lists (合併兩個排序串列)
*   **Hint:** Use a **Dummy Head** to simplify the logic of building the new list.
    **提示：** 使用 **虛擬頭節點** 來簡化建立新串列的邏輯。
*   **Focus:** Pointer manipulation basics.
    **重點：** 指標操作基礎。

### Medium: Remove N-th Node From End of List (移除倒數第 N 個節點)
*   **Hint:** Use **Two Pointers**. Move the first pointer $N+1$ steps ahead, then move both until the first hits the end.
    **提示：** 使用 **雙指標**。將第一個指標向前移動 $N+1$ 步，然後同時移動兩者直到第一個指標到達末端。
*   **Focus:** One-pass algorithm.
    **重點：** 一次遍歷演算法。

### Hard: Reverse Nodes in k-Group (K 個一組反轉鏈結串列)
*   **Hint:** Combine "Reverse Linked List" logic with a loop that checks if $k$ nodes exist remaining. Requires careful wiring of the `prev` group's tail to the `curr` group's new head.
    **提示：** 結合「反轉鏈結串列」邏輯與一個檢查是否剩餘 $k$ 個節點的迴圈。需要仔細將 `prev` 群組的尾部連結至 `curr` 群組的新頭部。
*   **Focus:** Complex state management.
    **重點：** 複雜狀態管理。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Null Check:** Did I handle `head == nullptr`?
    **空值檢查：** 我是否處理了 `head == nullptr`？
*   [ ] **Single Node:** Does the logic work for a list with size 1?
    **單節點：** 邏輯是否適用於大小為 1 的串列？
*   [ ] **Termination:** Did I set the last node's `next` to `nullptr` to prevent cycles?
    **終止：** 我是否將最後一個節點的 `next` 設為 `nullptr` 以防止環路？
*   [ ] **Pointer Loss:** Did I save `curr->next` before overwriting `curr->next`?
    **指標遺失：** 在覆寫 `curr->next` 之前，我是否保存了 `curr->next`？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Train Analogy (火車類比):**
    A Linked List is like a train. To remove a car, you must unhook it from the previous car and hook the previous car to the next car. You can't just teleport to the 10th car; you must walk through cars 1-9.
    **火車類比：** 鏈結串列就像一列火車。要移除一節車廂，你必須將它與前一節車廂脫鉤，並將前一節車廂鉤到下一節車廂。你不能直接傳送到第 10 節車廂；你必須走過第 1 到第 9 節。

*   **The "Bridge Burning" Image (過河拆橋):**
    When reversing a list, imagine you are crossing a bridge (`curr->next`) and then destroying it to build a new bridge backwards (`curr->next = prev`). You **must** know where the next island is (`nextTemp`) before you destroy the bridge, or you fall into the water (lose the list).
    **過河拆橋意象：** 反轉串列時，想像你正在過橋（`curr->next`），然後拆掉它以向後建立新橋（`curr->next = prev`）。在拆橋之前，你 **必須** 知道下一個島嶼在哪裡（`nextTemp`），否則你會掉進水裡（遺失串列）。