Here is the comprehensive study guide for **Heap / Priority Queue**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level (focusing on fundamentals and standard library mastery), with **C++** as the implementation language.

---

# Heap & Priority Queue: The Fundamentals (Beginner Level)
# 堆積與優先佇列：基礎篇 (初級難度)

## 1. Learning Objectives (學習目標)

1.  **Understand the Internal Structure:** Grasp the definition of a Complete Binary Tree and the Heap Property (Min-Heap vs. Max-Heap).
    **理解內部結構：** 掌握完全二元樹（Complete Binary Tree）的定義以及堆積性質（最小堆積與最大堆積）。
2.  **Master C++ STL Usage:** Gain proficiency with `std::priority_queue`, including custom comparators and underlying container manipulation.
    **精通 C++ STL 用法：** 熟練使用 `std::priority_queue`，包含自定義比較器（Comparators）與底層容器的操作。
3.  **Analyze Complexity:** Clearly distinguish between the costs of building a heap ($O(N)$) versus dynamic updates ($O(\log N)$).
    **分析複雜度：** 清楚區分建構堆積（$O(N)$）與動態更新（$O(\log N)$）的成本差異。
4.  **Identify Basic Patterns:** Recognize scenarios requiring "access to the extremum" or "Top-K elements".
    **識別基本模式：** 辨識需要「存取極值」或「前 K 個元素」的場景。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
-   **Definition:** A Heap is a specialized tree-based data structure that satisfies the heap property: in a Max-Heap, for any given node $I$, the value of $I$ is greater than or equal to the values of its children.
    **定義：** 堆積是一種特殊的樹狀資料結構，滿足堆積性質：在最大堆積中，任意節點 $I$ 的值皆大於或等於其子節點的值。
-   **Intuition:** Think of it as a "VIP line" or an "Emergency Room". You don't care about the order of everyone; you only care who has the highest priority right now.
    **直覺：** 將其視為「VIP 通道」或「急診室」。你不在乎所有人的具體順序，你只在乎當下誰的優先級最高。

### Time & Space Complexity (時間與空間複雜度)

| Operation (操作) | Complexity (複雜度) | Note (備註) |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(\log N)$ | Sift-up / Bubble-up (上浮) |
| **Pop (Remove Top)** | $O(\log N)$ | Swap with last, then Sift-down (下沉) |
| **Top (Peek)** | $O(1)$ | Access root element (存取根節點) |
| **Build Heap** | $O(N)$ | Using Floyd's algorithm (bottom-up) (使用 Floyd 演算法，自底向上) |
| **Space** | $O(N)$ | Array-based implementation (基於陣列的實作) |

### Use Cases (適用場景)
-   **Top K Elements:** Finding the K largest or smallest items in a dataset.
    **Top K 元素：** 在資料集中尋找前 K 大或前 K 小的項目。
-   **Task Scheduling:** Processing tasks based on priority rather than arrival time.
    **任務排程：** 根據優先級而非到達時間來處理任務。
-   **Graph Algorithms:** Essential for Dijkstra’s (Shortest Path) and Prim’s (MST).
    **圖演算法：** Dijkstra（最短路徑）與 Prim（最小生成樹）演算法的核心。

### When NOT to Use (不適用場景)
-   **Searching:** Finding an arbitrary element takes $O(N)$.
    **搜尋：** 尋找任意特定元素需要 $O(N)$ 時間。
-   **Sorted Order:** If you need the entire sequence sorted, just use Sort ($O(N \log N)$). A Heap is only beneficial if you need dynamic access or partial ordering.
    **完全排序：** 如果你需要整個序列有序，直接使用排序即可。堆積僅在你需要動態存取或部分排序時才有優勢。

---

## 3. Typical Patterns (典型題型 / 模式)

Since this is the **Beginner** module, we focus on the two most foundational patterns.
由於這是 **初級** 模組，我們專注於兩個最基礎的模式。

### Pattern 1: Top K Elements (Static or Streaming)
**模式一：前 K 個元素（靜態或串流）**
-   **Concept:** Maintain a heap of size K.
    **概念：** 維護一個大小為 K 的堆積。
-   **Strategy:**
    -   To find the **Kth Largest**, use a **Min-Heap** of size K. (Keep the largest K candidates; the top is the smallest of the large ones).
    -   若要找 **第 K 大**，使用大小為 K 的 **最小堆積**。（保留最大的 K 個候選者；堆頂即為這些大數中最小的那個）。

### Pattern 2: Merge K Sorted Structures
**模式二：合併 K 個已排序結構**
-   **Concept:** Put the head of each sorted list into a Min-Heap.
    **概念：** 將每個已排序串列的頭部放入最小堆積。
-   **Strategy:** Always pop the smallest element from the heap and push the next element from the same list.
    **策略：** 總是從堆積彈出最小元素，並將該元素所屬串列的下一個元素推入堆積。

---

## 4. Example Walkthrough (範例講解)

### Problem: Kth Largest Element in an Array
**問題：陣列中的第 K 大元素**

> **Problem Statement:** Given an integer array `nums` and an integer `k`, return the $k^{th}$ largest element in the array.
> **問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳陣列中第 $k$ 大的元素。

### Approach (思路)

1.  **Brute Force (Sorting):**
    -   Sort the entire array descending. Return index $k-1$.
    -   **暴力法（排序）：** 將整個陣列降序排列。回傳索引 $k-1$。
    -   Complexity: $O(N \log N)$. Acceptable, but not optimal for large $N$ with small $K$.

2.  **Optimization (Min-Heap):**
    -   Maintain a Min-Heap of size $K$.
    -   Iterate through the array. If the heap size < $K$, push.
    -   If heap size == $K$ and current number > heap.top(), pop and push current.
    -   **優化（最小堆積）：** 維護一個大小為 $K$ 的最小堆積。遍歷陣列，若堆積大小 < $K$，直接推入。若堆積已滿且當前數字 > 堆頂，彈出堆頂並推入當前數字。
    -   Complexity: $O(N \log K)$. Better when $K < N$.

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <queue>
#include <functional> // for std::greater

class Solution {
public:
    int findKthLargest(std::vector<int>& nums, int k) {
        // Use a Min-Heap to store the top K largest elements.
        // In C++, priority_queue is a Max-Heap by default.
        // We use std::greater<int> to invert it to a Min-Heap.
        // 使用最小堆積來儲存前 K 大的元素。
        // 在 C++ 中，priority_queue 預設為最大堆積。
        // 我們使用 std::greater<int> 將其反轉為最小堆積。
        
        std::priority_queue<int, std::vector<int>, std::greater<int>> minHeap;

        for (int num : nums) {
            minHeap.push(num);

            // If the heap size exceeds K, remove the smallest element.
            // This ensures the heap always contains the K largest elements seen so far.
            // 如果堆積大小超過 K，移除最小的元素。
            // 這確保堆積中始終包含目前為止最大的 K 個元素。
            if (minHeap.size() > k) {
                minHeap.pop();
            }
        }

        // The top of the min-heap is the smallest among the top K largest,
        // which is exactly the Kth largest element.
        // 最小堆積的頂端是前 K 大元素中最小的，這正是第 K 大的元素。
        return minHeap.top();
    }
};
```

### Common Mistake (錯誤示範)
-   **Mistake:** Using a **Max-Heap** of size $N$, pushing everything, and popping $K-1$ times.
    **錯誤：** 使用大小為 $N$ 的 **最大堆積**，推入所有元素，然後彈出 $K-1$ 次。
-   **Why it's suboptimal:** Building the heap takes $O(N)$, and popping takes $O(K \log N)$. Total $O(N + K \log N)$. Space is $O(N)$. The Min-Heap approach uses only $O(K)$ space.
    **為何次佳：** 建構堆積耗時 $O(N)$，彈出耗時 $O(K \log N)$。總計 $O(N + K \log N)$。空間為 $O(N)$。而最小堆積法僅需 $O(K)$ 空間。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Nuance (陷阱 / 細節) |
| :--- | :--- |
| **C++ Default Behavior** | C++ `priority_queue` is a **Max-Heap** (`less<T>`). Python's `heapq` is a **Min-Heap**. Don't mix them up. <br> C++ 的 `priority_queue` 預設是 **最大堆積**。Python 的 `heapq` 是 **最小堆積**。別搞混了。 |
| **Complexity of Construction** | `priority_queue(begin, end)` is $O(N)$. Pushing elements one by one is $O(N \log N)$. <br> `priority_queue(begin, end)` 的建構是 $O(N)$。逐一推入元素則是 $O(N \log N)$。 |
| **Kth Largest vs Min-Heap** | To find the **Largest** elements, you usually need a **Min-Heap** to evict the small ones. It's counter-intuitive. <br> 要找 **最大** 的元素，通常需要 **最小堆積** 來驅逐較小的元素。這有點反直覺。 |
| **Random Access** | You cannot iterate over a `priority_queue` or access index `i`. You can only see `top()`. <br> 你無法遍歷 `priority_queue` 或存取索引 `i`。你只能看到 `top()`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the need:** "Since we need to dynamically access the largest/smallest element..." or "We need the top K items..."
    **確認需求：** 「由於我們需要動態存取最大/最小元素……」或「我們需要前 K 個項目……」
2.  **Propose Heap:** "A Heap (Priority Queue) is suitable here because it gives us $O(1)$ access to the extremum and efficient $O(\log N)$ updates."
    **提出堆積：** 「堆積（優先佇列）很適合這裡，因為它提供 $O(1)$ 的極值存取和高效的 $O(\log N)$ 更新。」
3.  **Clarify Max vs Min:** "I will use a Min-Heap of size K to maintain the K largest elements." (Be explicit).
    **釐清最大/最小：** 「我將使用大小為 K 的最小堆積來維護前 K 大的元素。」（務必明確）。

### Whiteboard Strategy (白板策略)
-   Do **not** implement the Heap class from scratch unless explicitly asked. Use `std::priority_queue`.
    **不要** 從頭實作 Heap 類別，除非被明確要求。使用 `std::priority_queue`。
-   If using a custom struct/class, remember to define `operator<` or a comparator struct.
    如果使用自定義結構/類別，記得定義 `operator<` 或比較器結構。

### Common Follow-up (常見追問)
-   **Q:** How to handle data that doesn't fit in memory?
    **問：** 如何處理無法放入記憶體的資料？
    -   **A:** External Sort or streaming with a fixed-size Heap. (外部排序或使用固定大小堆積進行串流處理)。
-   **Q:** What if we need to update the priority of an element already in the heap?
    **問：** 如果我們需要更新堆積中既有元素的優先級怎麼辦？
    -   **A:** `std::priority_queue` doesn't support `decrease_key` efficiently. We might need `std::set` (Tree-based, supports removal) or "Lazy Removal" (mark as deleted and ignore when popped).
    -   **答：** `std::priority_queue` 不支援高效的 `decrease_key`。我們可能需要 `std::set`（基於樹，支援刪除）或「延遲刪除」（標記為已刪除，彈出時忽略）。

---

## 7. Practice Problems (練習題)

### 1. Last Stone Weight (Easy)
-   **Prompt:** Smash two heaviest stones together. If $x \neq y$, put $y-x$ back.
    **題目：** 將兩顆最重的石頭互砸。若 $x \neq y$，將 $y-x$ 放回。
-   **Hint:** Simulation using a Max-Heap.
    **提示：** 使用最大堆積進行模擬。
-   **Key:** Simply `pop` twice, calculate diff, `push` back.
    **關鍵：** 簡單地 `pop` 兩次，計算差值，`push` 回去。

### 2. K Closest Points to Origin (Medium)
-   **Prompt:** Find K points closest to $(0,0)$.
    **題目：** 找出距離 $(0,0)$ 最近的 K 個點。
-   **Hint:** Max-Heap of size K.
    **提示：** 大小為 K 的最大堆積。
-   **Key:** Custom comparator based on Euclidean distance. Keep the *closest* points means evicting the *farthest*, so use Max-Heap.
    **關鍵：** 基於歐幾里得距離的自定義比較器。保留 *最近* 的點意味著驅逐 *最遠* 的點，故使用最大堆積。

### 3. Sort Characters By Frequency (Medium)
-   **Prompt:** Sort string based on character frequency.
    **題目：** 根據字元頻率排序字串。
-   **Hint:** Count freq ($O(N)$) $\rightarrow$ Max-Heap ($O(D \log D)$ where $D$ is unique chars).
    **提示：** 計算頻率 ($O(N)$) $\rightarrow$ 最大堆積 ($O(D \log D)$，其中 $D$ 為唯一字元數)。
-   **Key:** Store `pair<int, char>` in heap.
    **關鍵：** 在堆積中儲存 `pair<int, char>`。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **Direction:** Did I choose the right heap? (Min-Heap for "K Largest", Max-Heap for "K Smallest").
    **方向：** 我選對堆積了嗎？（找「前 K 大」用最小堆積，找「前 K 小」用最大堆積）。
-   [ ] **Syntax:** Did I use `greater<int>` for Min-Heap in C++?
    **語法：** 我在 C++ 中是否為了最小堆積使用了 `greater<int>`？
-   [ ] **Complexity:** Am I pushing $N$ elements into a heap of size $K$ ($N \log K$) or size $N$ ($N \log N$)?
    **複雜度：** 我是將 $N$ 個元素推入大小為 $K$ 的堆積（$N \log K$）還是大小為 $N$ 的堆積（$N \log N$）？
-   [ ] **Corner Case:** What if $K=0$ or the array is empty?
    **邊界條件：** 如果 $K=0$ 或陣列為空怎麼辦？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

-   **The Corporate Ladder (企業階梯):**
    -   **Max-Heap:** The CEO is at the top. Every manager is more powerful (larger value) than their direct reports. You can find the CEO instantly ($O(1)$), but finding a specific intern requires searching the whole building ($O(N)$).
    -   **最大堆積：** CEO 在頂端。每個經理的權力（數值）都大於其直接下屬。你可以瞬間找到 CEO ($O(1)$)，但要找特定的實習生需要搜尋整棟大樓 ($O(N)$)。
-   **The Bouncer (保鑣):**
    -   **Top K Largest Pattern:** The club only holds $K$ people. To maintain the "richest" $K$ people inside, the bouncer stands at the door. When a new person comes, he compares them with the *poorest* person currently inside (Min-Heap top). If the new person is richer, the poorest gets kicked out.
    -   **前 K 大模式：** 俱樂部只能容納 $K$ 人。為了保持裡面是「最富有」的 $K$ 人，保鑣站在門口。當新人來時，他將新人與裡面目前 *最窮* 的人（最小堆積頂端）比較。如果新人更富有，最窮的人就被踢出去。