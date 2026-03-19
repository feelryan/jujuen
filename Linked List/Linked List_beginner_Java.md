Here is the comprehensive study guide for **Linked List**, tailored for a Senior Software Engineer revisiting the basics (Beginner Level), presented in a bilingual format with Java code.

這是針對 **Linked List（鏈結串列）** 的完整學習指南，專為複習基礎（初學者難度）的資深軟體工程師量身打造，採用中英雙語對照並搭配 Java 程式碼。

---

# Linked List (Beginner) | 鏈結串列（初級）

## 1. Learning Goals（學習目標）

*   **Master Pointer Manipulation:** deeply understand how to reassign references without losing track of the remaining list.
    **掌握指標操作：** 深刻理解如何在不丟失剩餘串列的情況下重新指派參照（reference）。
*   **Internalize the "Dummy Head" Pattern:** learn to use a sentinel node to simplify edge cases involving the head of the list.
    **內化「虛擬頭節點」模式：** 學習使用哨兵節點（sentinel node）來簡化涉及串列頭部的邊界情況。
*   **Understand Memory Layout:** contrast the non-contiguous memory of linked lists with the contiguous memory of arrays.
    **理解記憶體佈局：** 對比鏈結串列的非連續記憶體與陣列的連續記憶體。
*   **Handle Edge Cases:** automatically consider empty lists, single-node lists, and processing the very last node.
    **處理邊界情況：** 自動考慮空串列、單節點串列以及處理最後一個節點的情況。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）

A Linked List is a linear data structure where elements are not stored at contiguous memory locations.
鏈結串列是一種線性資料結構，其元素並非儲存在連續的記憶體位置。

Instead, each element (Node) points to the next using a reference.
取而代之的是，每個元素（節點）使用參照（reference）指向下一個元素。

**Analogy:** Think of a **Treasure Hunt**. You only have the clue to the first location; once you get there, you find the clue to the next location. You cannot jump to the 5th location directly.
**類比：** 想像一場**尋寶遊戲**。你只有第一個地點的線索；一旦到達那裡，你會找到下一個地點的線索。你無法直接跳到第 5 個地點。

### Complexity Analysis（複雜度分析）

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Access / Lookup** | $O(N)$ | $O(1)$ | Must traverse from head. <br> 必須從頭遍歷。 |
| **Insert / Delete (Head)** | $O(1)$ | $O(1)$ | Just update pointers. <br> 僅需更新指標。 |
| **Insert / Delete (Known Node)**| $O(1)$ | $O(1)$ | If we already have the reference to the node *before* the target. <br> 如果我們已經擁有目標 *之前* 節點的參照。 |
| **Insert / Delete (Unknown)** | $O(N)$ | $O(1)$ | Time spent finding the position. <br> 時間花在尋找位置上。 |

### When to Use (and Not)（適用與不適用場景）

*   **Use when:** You need constant-time insertions/deletions and don't know the size of the data beforehand.
    **適用於：** 你需要常數時間的插入/刪除操作，且預先不知道資料的大小。
*   **Don't use when:** You need random access (e.g., `arr[5]`) or memory is extremely tight (due to pointer overhead).
    **不適用於：** 你需要隨機存取（例如 `arr[5]`）或記憶體極度吃緊時（因為指標會佔用額外空間）。

---

## 3. Typical Patterns（典型題型 / 模式）

For the beginner level, two patterns dominate almost all problems:
針對初級難度，有兩種模式主導了幾乎所有問題：

### A. The "Runner" Technique (Iteration)
**「跑者」技巧（迭代）**

Simply traversing the list using a pointer (often named `curr`).
單純使用一個指標（通常命名為 `curr`）遍歷串列。
Crucial for searching or modifying values.
對於搜尋或修改數值至關重要。

### B. The Dummy Head (Sentinel Node)
**虛擬頭節點（哨兵節點）**

Creating a placeholder node that points to the actual head of the list.
建立一個指向串列實際頭部的佔位節點。
**Why?** It eliminates the need to write separate logic for operations that might change the head (e.g., deleting the first node).
**為什麼？** 它消除了為可能改變頭部的操作（例如刪除第一個節點）編寫單獨邏輯的需求。

---

## 4. Example Walkthrough（範例講解）

### Problem: Reverse Linked List
### 問題：反轉鏈結串列

**Problem Statement:** Given the `head` of a singly linked list, reverse the list, and return the reversed list.
**問題重述：** 給定單向鏈結串列的 `head`，請反轉該串列，並回傳反轉後的串列。

### Thought Process（思路）

1.  **Brute Force (Stack):** Traverse the list, push values onto a stack, then create a new list by popping values.
    **暴力解（堆疊）：** 遍歷串列，將數值推入堆疊，然後透過彈出數值建立新串列。
    *   *Critique:* $O(N)$ space complexity. We can do better in-place.
    *   *評論：* $O(N)$ 空間複雜度。我們可以做到原地（in-place）操作。

2.  **Optimal Approach (Iterative Pointer Manipulation):**
    **最佳解（迭代指標操作）：**
    We need to reverse the arrows. For a node `curr`, we want `curr.next` to point to `prev` instead of the next node.
    我們需要反轉箭頭。對於節點 `curr`，我們希望 `curr.next` 指向 `prev` 而不是下一個節點。
    However, if we change `curr.next` immediately, we lose the reference to the rest of the list.
    然而，如果我們立即更改 `curr.next`，我們會失去對剩餘串列的參照。
    *Solution:* Save the next node in a temporary variable before changing the pointer.
    *解法：* 在更改指標之前，將下一個節點儲存在暫存變數中。

### Java Reference Solution（Java 參考解）

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
    public ListNode reverseList(ListNode head) {
        // Initialize previous pointer to null (new tail of the list)
        // 初始化前一個指標為 null（串列的新尾部）
        ListNode prev = null;
        
        // Initialize current pointer to head
        // 初始化當前指標為 head
        ListNode curr = head;

        while (curr != null) {
            // 1. Save the next node so we don't lose the rest of the list
            // 1. 儲存下一個節點，以免丟失剩餘的串列
            ListNode nextTemp = curr.next;

            // 2. Reverse the pointer: point current node backwards to prev
            // 2. 反轉指標：將當前節點指向後方的 prev
            curr.next = prev;

            // 3. Advance prev and curr one step forward
            // 3. 將 prev 和 curr 向前推進一步
            prev = curr;
            curr = nextTemp;
        }

        // At the end, curr is null, and prev is the new head
        // 結束時，curr 為 null，而 prev 是新的頭節點
        return prev;
    }
}
```

### Complexity & Edge Cases（複雜度與邊界條件）

*   **Time:** $O(N)$ — We visit every node once.
    **時間：** $O(N)$ — 我們訪問每個節點一次。
*   **Space:** $O(1)$ — We only use pointers, no extra data structures.
    **空間：** $O(1)$ — 我們只使用指標，沒有額外的資料結構。
*   **Edge Case:** If `head` is `null`, the loop doesn't run, returns `null` (correct). If list has 1 node, loop runs once, returns that node (correct).
    **邊界條件：** 如果 `head` 為 `null`，迴圈不執行，回傳 `null`（正確）。如果串列有 1 個節點，迴圈執行一次，回傳該節點（正確）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall |
| :--- | :--- |
| **NPE (Null Pointer Exception)** | **Most Common Error.** Accessing `curr.next` when `curr` is already `null`. Always check `if (curr != null)` before access. <br> **最常見錯誤。** 當 `curr` 已經是 `null` 時存取 `curr.next`。存取前務必檢查 `if (curr != null)`。 |
| **Losing the Head** | If you move the `head` pointer directly (`head = head.next`) without saving it, you lose the start of the list. Use a separate `curr` pointer for traversal. <br> **丟失頭部。** 如果你直接移動 `head` 指標（`head = head.next`）而沒有保存它，你會失去串列的開頭。請使用單獨的 `curr` 指標進行遍歷。 |
| **Cycle Creation** | In complex wiring (like reordering), accidentally making a node point to itself or a previous node creates an infinite loop. <br> **製造循環。** 在複雜的連接操作中（如重新排序），意外地讓節點指向自己或前一個節點會造成無窮迴圈。 |
| **Java References** | Remember Java is "Pass by Value", but for objects, the value is the reference. Changing `node.val` changes the original object; changing `node = newNode` only changes the local variable. <br> **Java 參照。** 記住 Java 是「傳值呼叫」，但對於物件，該值是參照。更改 `node.val` 會改變原始物件；更改 `node = newNode` 只會改變區域變數。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
"Since this is a linked list, random access isn't possible, so I'll need to iterate linearly. I'll use pointers to track my position."
「由於這是鏈結串列，無法進行隨機存取，所以我需要線性遍歷。我會使用指標來追蹤我的位置。」

### Whiteboard Strategy（白板策略）
**Draw Boxes and Arrows!** Never try to solve Linked List problems purely in your head.
**畫出方框和箭頭！** 永遠不要試圖純粹在腦海中解決鏈結串列問題。
1.  Draw the initial state (e.g., `1 -> 2 -> 3`).
    畫出初始狀態（例如 `1 -> 2 -> 3`）。
2.  Draw the pointers (`prev`, `curr`) above the boxes.
    在方框上方畫出指標（`prev`, `curr`）。
3.  Cross out old arrows and draw new ones as you simulate your code.
    模擬程式碼時，劃掉舊箭頭並畫出新箭頭。

### Common Follow-ups（常見追問）
*   "Can you do this recursively?" (Tests understanding of stack frames).
    「你能用遞迴做這個嗎？」（測試對堆疊框架的理解）。
*   "How would you handle a Doubly Linked List?" (Tests handling `prev` pointers).
    「你會如何處理雙向鏈結串列？」（測試對 `prev` 指標的處理）。

---

## 7. Practice Problems（練習題）

### 1. Merge Two Sorted Lists (Easy)
**合併兩個已排序串列（簡單）**
*   **Prompt:** Merge two sorted linked lists and return it as a sorted list.
    **題目：** 合併兩個已排序的鏈結串列，並將其作為一個已排序串列回傳。
*   **Hint:** Use a **Dummy Head** to build the result list easily. Compare heads of both lists, attach the smaller one, and move forward.
    **提示：** 使用 **虛擬頭節點** 來輕鬆建立結果串列。比較兩個串列的頭部，接上較小的那一個，然後向前移動。
*   **Key Logic:** `if (l1.val < l2.val) { curr.next = l1; l1 = l1.next; }`

### 2. Remove Duplicates from Sorted List (Easy)
**從已排序串列中刪除重複項（簡單）**
*   **Prompt:** Delete all duplicates such that each element appears only once.
    **題目：** 刪除所有重複項，使得每個元素只出現一次。
*   **Hint:** Iterate. If `curr.val == curr.next.val`, skip the next node (`curr.next = curr.next.next`). Otherwise, move `curr` forward.
    **提示：** 遍歷。如果 `curr.val == curr.next.val`，跳過下一個節點（`curr.next = curr.next.next`）。否則，將 `curr` 向前移動。

### 3. Middle of the Linked List (Beginner/Intermediate)
**鏈結串列的中間節點（初級/中級）**
*   **Prompt:** Return the middle node of the linked list.
    **題目：** 回傳鏈結串列的中間節點。
*   **Hint:** Introduce the **Fast & Slow Pointers** concept. Fast moves 2 steps, Slow moves 1 step. When Fast reaches the end, Slow is at the middle.
    **提示：** 引入 **快慢指標** 概念。快指標走 2 步，慢指標走 1 步。當快指標到達終點時，慢指標位於中間。

---

## 8. Quick Checklists（快速檢核表）

Use this list to debug your code mentally before telling the interviewer you are done.
在告訴面試官你完成之前，使用此清單在腦海中除錯你的程式碼。

*   [ ] **Null Head:** Did I handle the case where `head` is null?
    **空頭部：** 我是否處理了 `head` 為 null 的情況？
*   [ ] **Single Node:** Does my logic work if the list has only one node?
    **單節點：** 如果串列只有一個節點，我的邏輯是否有效？
*   [ ] **Pointer Updates:** Did I actually move the pointers (`curr = curr.next`) inside the `while` loop? (Infinite loop check).
    **指標更新：** 我是否在 `while` 迴圈內實際移動了指標（`curr = curr.next`）？（無窮迴圈檢查）。
*   [ ] **Return Value:** Did I return the new head (e.g., `prev` in reversal) or the original head?
    **回傳值：** 我是回傳了新的頭部（例如反轉中的 `prev`）還是原始頭部？
*   [ ] **Broken Chains:** Did I save `next` before overwriting it?
    **斷鏈：** 我是否在覆蓋 `next` 之前保存了它？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Train Car" Analogy（「火車車廂」類比）
*   **Linked List:** A train where each car is connected to the next by a coupler (pointer). To find the dining car, you must walk through every car from the engine.
    **鏈結串列：** 一列火車，每節車廂透過連結器（指標）與下一節相連。要找到餐車，你必須從火車頭走過每一節車廂。
*   **Array:** A long shelf of numbered boxes. You can instantly grab the item in box #5.
    **陣列：** 一個標有編號的長架子。你可以立即拿取第 5 號盒子裡的物品。

### The "Bridge Burning" Visual（「過河拆橋」視覺化）
*   When reversing or deleting, imagine you are on a bridge. Before you burn the bridge behind you (delete/change pointer), make sure you have a rope thrown to the other side (saved `next` reference), or you will fall into the abyss (lose the list).
    **鏈結串列操作：** 當進行反轉或刪除時，想像你在橋上。在你燒掉身後的橋（刪除/更改指標）之前，確保你已經把繩子拋向了對岸（保存 `next` 參照），否則你會掉入深淵（丟失串列）。