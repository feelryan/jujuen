Here is the comprehensive interview study guide for **Heap / Priority Queue**, tailored for a Senior Software Engineer, focusing on C++ implementation.

這是一份針對 **Heap / Priority Queue（堆積 / 優先佇列）** 的完整面試教材，專為資深軟體工程師設計，並著重於 C++ 實作。

---

# Interview Guide: Heap & Priority Queue (Intermediate)
# 面試指南：堆積與優先佇列（中階）

## 1. Learning Goals（學習目標）

1.  **Master C++ STL `priority_queue` nuances**: specifically custom comparators and the default Max-Heap behavior.
    掌握 C++ STL `priority_queue` 的細節：特別是自定義比較器（Comparator）與預設的 Max-Heap 行為。
2.  **Internalize the "Top K" Pattern**: Understand when to use a Min-Heap of size K versus sorting.
    內化「Top K」模式：理解何時該使用大小為 K 的 Min-Heap，而非直接排序。
3.  **Optimize Heap Construction**: Distinguish between $O(N \log N)$ insertion and $O(N)$ heapify (Floyd's algorithm).
    優化堆積建構：區分 $O(N \log N)$ 的逐一插入與 $O(N)$ 的 heapify（Floyd 演算法）。
4.  **Handle Dynamic Data Streams**: Learn to manage medians and running metrics using dual heaps.
    處理動態資料流：學習使用雙堆積（Dual Heaps）來管理中位數與動態指標。

---

## 2. Core Concepts at a Glance（核心觀念速覽）

### Definition（定義）
A Heap is a specialized tree-based data structure that satisfies the heap property: in a Max-Heap, for any given node I, the value of I is greater than or equal to the values of its children.
堆積是一種特殊的樹狀資料結構，滿足堆積性質：在 Max-Heap 中，對於任意節點 I，I 的值皆大於或等於其子節點的值。

A Priority Queue is an abstract data type where each element has a "priority," and the element with the highest priority is served before others.
優先佇列是一種抽象資料型別，其中每個元素都有一個「優先級」，優先級最高的元素會最先被處理。

### Intuition（直覺）
Think of it as a "VIP line" where new people can join anytime, but the person with the highest status always stands at the front door.
將其想像成一條「VIP 排隊線」，新人隨時可以加入，但地位最高的人永遠站在門口。

### Complexity（複雜度）

| Operation | Time Complexity | Note |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(\log N)$ | Bubble up (Sift up) |
| **Pop (Extract Top)** | $O(\log N)$ | Bubble down (Sift down) |
| **Top (Peek)** | $O(1)$ | Root element |
| **Build Heap** | $O(N)$ | Using bottom-up approach (Floyd's) |
| **Search** | $O(N)$ | Heaps are not optimized for search |

### When to Use (適用場景)
*   Finding the $K^{th}$ largest/smallest element.
    尋找第 K 大或第 K 小的元素。
*   Merging multiple sorted streams (e.g., log merging).
    合併多個已排序的資料流（例如：日誌合併）。
*   Dijkstra’s Shortest Path or Prim’s MST algorithms.
    Dijkstra 最短路徑或 Prim 最小生成樹演算法。
*   Scheduling tasks based on priority.
    基於優先級的任務排程。

### When NOT to Use (不適用場景)
*   Searching for an arbitrary element (Use Hash Map or BST).
    搜尋任意元素（應使用雜湊表或二元搜尋樹）。
*   Finding the Min/Max of a static array only once (Linear scan is sufficient).
    僅需尋找靜態陣列的最小值/最大值一次（線性掃描即可）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern 1: Top K Elements (Top K 元素)
Keep a Min-Heap of size K to track the K largest elements seen so far.
維護一個大小為 K 的 Min-Heap，用來追蹤目前為止看到的 K 個最大元素。

### Pattern 2: Merge K Sorted Lists (合併 K 個排序串列)
Use a Min-Heap to keep track of the current head of each list.
使用 Min-Heap 來追蹤每個串列目前的頭部元素。

### Pattern 3: Two Heaps (雙堆積)
Maintain a Max-Heap for the lower half of data and a Min-Heap for the upper half to find the median.
維護一個 Max-Heap 儲存資料的下半部，以及一個 Min-Heap 儲存上半部，用以尋找中位數。

---

## 4. Example Walkthrough（範例講解）

### Problem: Merge K Sorted Lists
### 問題：合併 K 個已排序的鏈結串列

**Problem Statement:**
You are given an array of `k` linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.
給定一個包含 `k` 個鏈結串列的陣列，每個鏈結串列皆已按升序排序。請將所有鏈結串列合併為一個已排序的鏈結串列並回傳。

#### Approach 1: Brute Force (暴力法)
Collect all nodes into an array, sort the array, and rebuild the list.
將所有節點收集到一個陣列中，對陣列排序，然後重建串列。
*   **Time:** $O(N \log N)$ where $N$ is total nodes.
*   **Space:** $O(N)$.

#### Approach 2: Compare One by One (逐一比較)
Compare the heads of all `k` lists to find the minimum, add it to result, and move that pointer.
比較所有 `k` 個串列的頭部以找到最小值，將其加入結果，並移動該指標。
*   **Time:** $O(k \cdot N)$.
*   **Drawback:** Inefficient when `k` is large. (缺點：當 `k` 很大時效率低落。)

#### Approach 3: Min-Heap (Optimal) (最佳解：最小堆積)
Push the head of every list into a Min-Heap. Extract the minimum, add to result, and push the `next` node of the extracted element back into the heap.
將每個串列的頭部放入 Min-Heap。取出最小值加入結果，並將該取出元素的 `next` 節點放回堆積中。
*   **Time:** $O(N \log k)$. (Heap size is limited to $k$)
*   **Space:** $O(k)$.

#### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <queue>

using namespace std;

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
    // Custom comparator for the priority queue.
    // 自定義優先佇列的比較器。
    // Note: priority_queue is a Max-Heap by default. To get a Min-Heap behavior (smallest on top),
    // the comparator should return true if 'a' is "less priority" than 'b' (i.e., a > b).
    // 注意：priority_queue 預設為 Max-Heap。為了獲得 Min-Heap 行為（最小在頂端），
    // 比較器在 'a' 的「優先級低於」'b' 時應回傳 true（即 a > b）。
    struct CompareNode {
        bool operator()(ListNode* const& p1, ListNode* const& p2) {
            return p1->val > p2->val;
        }
    };

    ListNode* mergeKLists(vector<ListNode*>& lists) {
        // Define a priority_queue with Min-Heap logic using the custom comparator.
        // 使用自定義比較器定義具有 Min-Heap 邏輯的 priority_queue。
        priority_queue<ListNode*, vector<ListNode*>, CompareNode> pq;

        // Push the head of each list into the heap.
        // 將每個串列的頭部推入堆積。
        for (ListNode* list : lists) {
            if (list) {
                pq.push(list);
            }
        }

        // Dummy head to simplify result list construction.
        // 虛擬頭節點，簡化結果串列的建構。
        ListNode dummy(0);
        ListNode* tail = &dummy;

        while (!pq.empty()) {
            // Get the smallest node.
            // 取得最小的節點。
            ListNode* smallest = pq.top();
            pq.pop();

            // Append to result list.
            // 接到結果串列後。
            tail->next = smallest;
            tail = tail->next;

            // If there is a next node in that list, push it to heap.
            // 如果該串列還有下一個節點，將其推入堆積。
            if (smallest->next) {
                pq.push(smallest->next);
            }
        }

        return dummy.next;
    }
};
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

### 1. `std::priority_queue` Default Behavior
*   **Concept:** In C++, `priority_queue<int>` uses `std::less<int>` by default.
    **觀念：** 在 C++ 中，`priority_queue<int>` 預設使用 `std::less<int>`。
*   **Pitfall:** `std::less` causes the largest element to be at the top (Max-Heap). This is opposite to Python's `heapq` (Min-Heap).
    **陷阱：** `std::less` 會導致最大的元素位於頂端（Max-Heap）。這與 Python 的 `heapq`（Min-Heap）相反。
*   **Fix:** Use `priority_queue<int, vector<int>, greater<int>>` for Min-Heap.
    **修正：** 使用 `priority_queue<int, vector<int>, greater<int>>` 來建立 Min-Heap。

### 2. Comparator Logic
*   **Concept:** The comparator returns `true` if the first argument goes *after* the second argument in the strict weak ordering (conceptually "lower" in the heap).
    **觀念：** 如果第一個參數在嚴格弱序中排在第二個參數*之後*（概念上在堆積的「下方」），比較器應回傳 `true`。
*   **Pitfall:** Writing `return a < b` creates a Max-Heap. Writing `return a > b` creates a Min-Heap.
    **陷阱：** 寫 `return a < b` 會建立 Max-Heap。寫 `return a > b` 會建立 Min-Heap。

### 3. Modifying Heap Elements
*   **Concept:** Standard heaps do not support efficient updates of arbitrary elements (e.g., `decrease_key`).
    **觀念：** 標準堆積不支援高效更新任意元素（例如 `decrease_key`）。
*   **Workaround:** Use "Lazy Removal" (mark as deleted in a hash map and ignore when popped) or use `std::set` if updates are frequent (though `set` overhead is higher).
    **變通方法：** 使用「延遲刪除」（在雜湊表中標記為已刪除，彈出時忽略），或者如果更新頻繁則使用 `std::set`（儘管 `set` 的開銷較高）。

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework (口條框架)
1.  **Identify the need for ordering:** "Since we need continuous access to the minimum/maximum element..."
    **確認排序需求：** 「既然我們需要持續存取最小/最大元素……」
2.  **Propose Heap:** "A Heap is suitable here because it gives us $O(1)$ access to the extremum and $O(\log N)$ updates."
    **提出堆積：** 「這裡適合使用堆積，因為它提供 $O(1)$ 的極值存取與 $O(\log N)$ 的更新。」
3.  **Discuss Trade-offs:** "If the data is static, sorting once is simpler. But for streaming data, Heap is optimal."
    **討論權衡：** 「如果資料是靜態的，排序一次比較簡單。但對於串流資料，堆積是最佳選擇。」

### Whiteboard Strategy (白板策略)
*   **Don't implement the Heap class:** Unless asked, use STL `priority_queue`.
    **不要實作 Heap 類別：** 除非被要求，否則使用 STL `priority_queue`。
*   **Define Comparator clearly:** If using a struct/class, write the comparator struct separately for clarity.
    **清楚定義比較器：** 如果使用 struct/class，將比較器 struct 分開寫以求清晰。
*   **Check Empty:** Always wrap `pq.top()` with `!pq.empty()` checks.
    **檢查為空：** 永遠在 `pq.top()` 前加上 `!pq.empty()` 的檢查。

### Common Follow-ups (常見追問)
*   **Q:** How to implement `remove(element)`?
    **問：** 如何實作 `remove(element)`？
    *   **A:** Lazy removal (keep a hash map of deleted counts).
        **答：** 延遲刪除（維護一個紀錄刪除計數的雜湊表）。
*   **Q:** Complexity if we use a BST instead?
    **問：** 如果改用 BST 複雜度為何？
    *   **A:** Still $O(\log N)$, but higher constant factors and memory overhead.
        **答：** 仍然是 $O(\log N)$，但常數因子和記憶體開銷較高。

---

## 7. Practice Problems（練習題）

### Easy: Kth Largest Element in a Stream
**Goal:** Implement a class to find the $K^{th}$ largest element in a stream.
**目標：** 實作一個類別來尋找資料流中第 K 大的元素。
*   **Hint:** Keep a Min-Heap of size K. If a new number > top, pop and push.
    **提示：** 維護一個大小為 K 的 Min-Heap。如果新數字 > 堆頂，彈出並推入。

### Medium: K Closest Points to Origin
**Goal:** Find K points closest to $(0,0)$.
**目標：** 找出距離 $(0,0)$ 最近的 K 個點。
*   **Hint:** Max-Heap of size K. Store pairs `{distance, point}`. Custom comparator needed.
    **提示：** 大小為 K 的 Max-Heap。儲存 `{距離, 點}`。需要自定義比較器。

### Hard: Find Median from Data Stream
**Goal:** Design a structure that supports `addNum` and `findMedian`.
**目標：** 設計一個支援 `addNum` 和 `findMedian` 的結構。
*   **Hint:** Two Heaps. Max-Heap for the left half, Min-Heap for the right half. Balance sizes.
    **提示：** 雙堆積。Max-Heap 負責左半部，Min-Heap 負責右半部。保持大小平衡。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review (自我審查)
- [ ] Did I use `std::greater` for Min-Heap in C++? (C++ 中是否使用了 `std::greater` 來建立 Min-Heap？)
- [ ] Is the complexity $O(N \log K)$ or $O(N \log N)$? (複雜度是 $O(N \log K)$ 還是 $O(N \log N)$？)
- [ ] Did I handle the case where `k=0` or `lists` is empty? (是否處理了 `k=0` 或 `lists` 為空的情況？)

### Complexity Check (複雜度確認)
- [ ] **Build:** $O(N)$
- [ ] **Push/Pop:** $O(\log N)$
- [ ] **Top:** $O(1)$

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Tournament Bracket (錦標賽樹狀圖)
Visualize a Heap as a tennis tournament bracket.
將堆積想像成網球錦標賽的樹狀圖。
*   The winner (smallest/largest) is always at the top.
    贏家（最小/最大）總是在頂端。
*   To replace the winner, you must play a match at each level ($O(\log N)$) to determine the new champion.
    要替換贏家，你必須在每一層級進行比賽（$O(\log N)$）以決定新冠軍。

### The Bouncer (保鑣)
For "Top K" problems using a Min-Heap of size K:
對於使用大小為 K 的 Min-Heap 解決「Top K」問題：
*   The Heap is the VIP room with capacity K.
    堆積是容量為 K 的 VIP 室。
*   The `top()` element is the "poorest" VIP (the bouncer).
    `top()` 元素是「最窮」的 VIP（保鑣）。
*   A new person can only enter if they are richer than the bouncer. If so, the bouncer gets kicked out.
    新人只有比保鑣富有才能進入。如果是這樣，保鑣就會被踢出去。