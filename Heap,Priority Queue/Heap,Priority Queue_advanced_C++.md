Here is the advanced interview preparation material for **Heap / Priority Queue**, tailored for a Senior Software Engineer using **C++**.

---

# Advanced Heap & Priority Queue Guide (C++)
# 進階堆積與優先佇列指南 (C++)

## 1. Learning Objectives (學習目標)

*   **Master Custom Comparators in C++ STL:**
    Deeply understand how to customize `std::priority_queue` for complex objects (structs) using functors and lambdas.
    **精通 C++ STL 自定義比較器：** 深入理解如何使用仿函式 (functors) 和 Lambda 表達式為複雜物件（結構體）自定義 `std::priority_queue`。

*   **Implement "Lazy Removal" Technique:**
    Since C++'s `priority_queue` does not support random deletion, learn to handle dynamic updates efficiently using hash maps and delayed removal.
    **實作「延遲刪除」技巧：** 由於 C++ 的 `priority_queue` 不支援隨機刪除，需學會使用雜湊表 (Hash Map) 和延遲移除策略來高效處理動態更新。

*   **Optimize for System Design Scenarios:**
    Apply heaps to high-concurrency or data-intensive problems like "Load Balancing," "Top-K Streaming," and "Task Scheduling."
    **針對系統設計場景優化：** 將堆積應用於「負載平衡」、「串流 Top-K」和「任務調度」等高並發或數據密集型問題。

*   **Differentiate Heap vs. Balanced BST:**
    Clearly articulate when to use a Heap ($O(1)$ peek) versus a `std::set`/`std::map` ($O(\log N)$ search/delete) in an interview context.
    **區分堆積與平衡二元搜尋樹：** 在面試中清晰闡述何時使用堆積（$O(1)$ 查看極值）與何時使用 `std::set`/`std::map`（$O(\log N)$ 搜尋/刪除）。

---

## 2. Core Concepts & Complexity (核心觀念與複雜度)

### Definition & Intuition (定義與直覺)
A Heap is a complete binary tree that satisfies the heap property: parent nodes are always ordered (greater or smaller) with respect to their children.
堆積是一種完全二元樹，滿足堆積性質：父節點相對於子節點總是保持有序（較大或較小）。

It is the standard implementation for a Priority Queue.
它是優先佇列的標準實作方式。

### Complexity Analysis (複雜度分析)

| Operation | Time Complexity | Note (Senior Insight) |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(\log N)$ | Bubbles up (percolate up). <br> **上浮操作**。 |
| **Pop (Extract Top)** | $O(\log N)$ | Swaps root with last, then bubbles down. <br> **交換根與末尾，然後下濾**。 |
| **Peek (Top)** | $O(1)$ | Direct access to array index 0. <br> **直接存取陣列索引 0**。 |
| **Heapify (Build)** | $O(N)$ | **Crucial:** Building from an array is linear, not $O(N \log N)$. <br> **關鍵：** 從陣列建堆是線性的，而非 $O(N \log N)$。 |
| **Remove Arbitrary**| $O(N)$ | Standard STL PQ doesn't support this; requires $O(N)$ search. <br> **標準 STL PQ 不支援此操作；需 $O(N)$ 搜尋**。 |

### When to Use (適用場景)
*   **Continuous Extremum:** Need repeated access to the min/max element.
    **連續極值：** 需要重複存取最小或最大元素。
*   **Streaming Data:** Data comes in real-time, and you need the Top K so far.
    **串流數據：** 數據即時傳入，且需要目前的 Top K。

### When NOT to Use (不適用場景)
*   **Searching:** Finding an arbitrary element is $O(N)$. Use a Hash Map or BST instead.
    **搜尋：** 尋找任意元素需 $O(N)$。應改用雜湊表或 BST。
*   **Rank Queries:** Finding the $i$-th smallest element (if $i$ changes dynamically) is inefficient compared to Order Statistic Trees.
    **排名查詢：** 若 $i$ 動態變化，尋找第 $i$ 小元素的效率不如順序統計樹。

---

## 3. Typical Patterns (典型題型與模式)

1.  **Top K Elements (Static/Streaming):**
    *   Keep a Min-Heap of size $K$ to track the largest $K$ elements.
    *   **Top K 元素（靜態/串流）：** 維護一個大小為 $K$ 的最小堆積來追蹤最大的 $K$ 個元素。
2.  **Merge K Sorted Resources:**
    *   Use a Min-Heap to store the current head of each stream.
    *   **合併 K 個排序資源：** 使用最小堆積儲存每個串流目前的頭部元素。
3.  **Two Heaps (Median Maintenance):**
    *   Use a Max-Heap for the lower half and a Min-Heap for the upper half of data.
    *   **雙堆積（中位數維護）：** 使用最大堆積儲存數據的下半部，最小堆積儲存上半部。
4.  **Lazy Removal (Soft Delete):**
    *   Since `std::priority_queue` lacks `remove(value)`, mark elements as "deleted" in a Hash Map and discard them only when they reach the top of the heap.
    *   **延遲刪除（軟刪除）：** 由於 `std::priority_queue` 缺乏 `remove(value)`，在雜湊表中將元素標記為「已刪除」，僅當它們到達堆頂時才丟棄。

---

## 4. Example Walkthrough (範例講解)

### Problem: Sliding Window Median (LeetCode 480) - Hard
**Problem Statement:**
Given an array `nums` and an integer `k`, there is a sliding window of size `k` moving from the very left of the array to the very right. You can only see the `k` numbers in the window. Each time the sliding window moves right by one position. Return the median array for each window position.
**問題重述：**
給定一個陣列 `nums` 和一個整數 `k`，有一個大小為 `k` 的滑動視窗從陣列最左側移動到最右側。你只能看到視窗內的 `k` 個數字。每次滑動視窗向右移動一個位置。回傳每個視窗位置的中位數陣列。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Extract window, sort it, find median.
    *   Complexity: $O(N \cdot K \log K)$. Too slow.
    *   **提取視窗，排序，找中位數。複雜度過高。**

2.  **Balanced BST (`std::multiset`):**
    *   Maintain a window in a BST. Insert/Delete is $O(\log K)$. Finding median requires iterator movement ($O(K)$ or $O(1)$ with hints).
    *   Valid, but we want to demonstrate **Heap mastery** here.
    *   **有效，但我們想在此展示堆積的精通程度。**

3.  **Optimal: Two Heaps + Lazy Removal (最佳解：雙堆積 + 延遲刪除):**
    *   **Structure:** `small` (Max-Heap) stores the smaller half, `large` (Min-Heap) stores the larger half.
    *   **Balance:** `small` size equals `large` size (or `small` has +1).
    *   **Removal:** When an element leaves the window, we cannot easily find it in the heaps. We record it in a hash map (`debt`).
    *   **Pruning:** Before accessing `top()`, check if the top element is in `debt`. If so, pop it and decrement debt count.
    *   **結構：** `small`（最大堆積）儲存較小的一半，`large`（最小堆積）儲存較大的一半。
    *   **平衡：** `small` 的大小等於 `large` 的大小（或 `small` 多 1）。
    *   **移除：** 當元素離開視窗時，我們無法輕易在堆積中找到它。我們將其記錄在雜湊表 (`debt`) 中。
    *   **修剪：** 在存取 `top()` 之前，檢查堆頂元素是否在 `debt` 中。若是，則彈出並減少欠債計數。

### C++ Reference Solution (參考解)

```cpp
#include <vector>
#include <queue>
#include <unordered_map>
#include <iostream>

using namespace std;

class Solution {
public:
    // Max-Heap for the smaller half of numbers
    // 用於儲存較小一半數字的最大堆積
    priority_queue<int> small;
    
    // Min-Heap for the larger half of numbers
    // 用於儲存較大一半數字的最小堆積
    priority_queue<int, vector<int>, greater<int>> large;
    
    // Tracks numbers that need to be removed (Lazy Removal)
    // 追蹤需要被移除的數字（延遲刪除）
    unordered_map<int, int> debt;
    
    // Helper to get current balance of valid elements
    // 輔助函式：獲取當前有效元素的平衡狀態
    // Returns balance factor: small.size() - large.size()
    // Note: We cannot simply use .size() because heaps contain "deleted" elements.
    // 注意：我們不能簡單使用 .size()，因為堆積包含「已刪除」的元素。
    int smallSize = 0;
    int largeSize = 0;

    // Prune invalid elements from the top of the heap
    // 從堆頂修剪無效元素
    template<typename T>
    void prune(T& heap) {
        while (!heap.empty() && debt[heap.top()] > 0) {
            debt[heap.top()]--;
            if (debt[heap.top()] == 0) {
                debt.erase(heap.top());
            }
            heap.pop();
        }
    }

    void makeBalance() {
        // If small heap has too many elements, move to large
        // 如果 small 堆積元素過多，移至 large
        if (smallSize > largeSize + 1) {
            large.push(small.top());
            small.pop();
            // Prune strictly after pop to ensure top is valid next time
            // Pop 後嚴格執行修剪，確保下次 top 有效
            prune(small); 
            smallSize--;
            largeSize++;
        }
        // If large heap has too many elements, move to small
        // 如果 large 堆積元素過多，移至 small
        else if (smallSize < largeSize) {
            small.push(large.top());
            large.pop();
            prune(large);
            smallSize++;
            largeSize--;
        }
    }

    void addNum(int num) {
        if (small.empty() || num <= small.top()) {
            small.push(num);
            smallSize++;
        } else {
            large.push(num);
            largeSize++;
        }
        makeBalance();
    }

    void removeNum(int num) {
        debt[num]++;
        // Logically decrement size
        // 邏輯上減少大小
        if (num <= small.top()) {
            smallSize--;
        } else {
            largeSize--;
        }
        // Physical removal happens lazily at prune()
        // 物理移除在 prune() 時延遲發生
        prune(small);
        prune(large);
        makeBalance();
    }

    double findMedian() {
        if (smallSize > largeSize) return small.top();
        return ((double)small.top() + (double)large.top()) * 0.5;
    }

    vector<double> medianSlidingWindow(vector<int>& nums, int k) {
        vector<double> result;
        
        // Initialize first window
        // 初始化第一個視窗
        for (int i = 0; i < k; i++) {
            addNum(nums[i]);
        }
        result.push_back(findMedian());

        // Slide window
        // 滑動視窗
        for (int i = k; i < nums.size(); i++) {
            int outNum = nums[i - k];
            int inNum = nums[i];
            
            removeNum(outNum);
            addNum(inNum);
            
            result.push_back(findMedian());
        }
        
        return result;
    }
};
```

### Complexity (複雜度)
*   **Time:** $O(N \log K)$. Each element is pushed and popped at most once. The `prune` operation amortizes to constant time per element over the course of the algorithm.
    **時間：** $O(N \log K)$。每個元素最多 push 和 pop 一次。`prune` 操作在整個演算法過程中分攤為常數時間。
*   **Space:** $O(N)$ in worst case (if we have many lazy deletions pending), but effectively $O(K)$ for valid elements.
    **空間：** 最壞情況 $O(N)$（如果有許多待處理的延遲刪除），但對於有效元素實際上是 $O(K)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake | Correction |
| :--- | :--- | :--- |
| **C++ Min-Heap Syntax** | `priority_queue<int, greater<int>>` (Compile Error) | Needs the container type: `priority_queue<int, vector<int>, greater<int>>`. <br> **需要指定容器類型**。 |
| **Comparator Logic** | Thinking `less<int>` means Min-Heap. | In `priority_queue`, `less` (default) puts the largest element at the top (Max-Heap). `greater` puts the smallest at the top (Min-Heap). **Think: "The top element is X than the rest".** <br> **在 PQ 中，`less` 是最大堆積，`greater` 是最小堆積。** |
| **Custom Structs** | Forgetting `const` in operator overloading. | `bool operator<(const Node& other) const { ... }` is required. <br> **運算子多載必須標記為 `const`**。 |
| **Lazy Removal** | Forgetting to prune *both* heaps or pruning only before `push`. | Always prune before `top()` or after `pop()` to ensure the exposed element is valid. <br> **務必在 `top()` 前或 `pop()` 後修剪，確保暴露的元素有效**。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Identify the Property:** "Since we need continuous access to the minimum/maximum element while data changes, a Heap is appropriate."
    **識別性質：** 「由於我們需要在數據變化時持續存取最小/最大元素，堆積是合適的選擇。」
2.  **Address the Limitation:** "Standard Heaps don't support random removal. I will use the **Lazy Removal** technique with a Hash Map to handle the sliding window constraints."
    **解決限制：** 「標準堆積不支援隨機移除。我將使用搭配雜湊表的**延遲刪除**技巧來處理滑動視窗的限制。」
3.  **Complexity Check:** "This ensures $O(\log K)$ for updates, which is superior to resorting the window ($O(K \log K)$)."
    **複雜度確認：** 「這確保了更新操作為 $O(\log K)$，優於重新排序視窗 ($O(K \log K)$)。」

### Whiteboard Strategy (白板策略)
*   **Define Structs Early:** If solving a graph problem (Dijkstra) or task scheduler, define your `struct Node { int cost; int id; ... }` and the comparator immediately.
    **儘早定義結構：** 如果解決圖論問題或任務調度，立即定義結構體和比較器。
*   **Don't Implement Heap from Scratch:** Unless asked. Use `std::priority_queue`. If asked to implement, use a `vector` and helper functions `siftUp`/`siftDown`.
    **不要從頭實作堆積：** 除非被要求。使用 `std::priority_queue`。若被要求實作，使用 `vector` 和 `siftUp`/`siftDown` 輔助函式。

### Common Follow-ups (常見追問)
*   *Q: How to handle thread safety?*
    *   A: Use a mutex to lock the heap during push/pop operations. For high concurrency, consider concurrent priority queues (skip lists or relaxed ordering).
*   *Q: What if the data doesn't fit in memory?*
    *   A: External Merge Sort using Heaps (k-way merge) on disk chunks.

---

## 7. Practice Problems (練習題)

### 1. Easy/Mid: Kth Largest Element in an Array (LeetCode 215)
*   **Hint:** Compare Min-Heap of size K ($O(N \log K)$) vs. QuickSelect ($O(N)$ average).
*   **Key:** In an interview, mention QuickSelect for optimal time, but Heap is safer to implement bug-free.
*   **提示：** 比較大小為 K 的最小堆積 ($O(N \log K)$) 與快速選擇演算法 ($O(N)$ 平均)。

### 2. Mid/Advanced: Task Scheduler (LeetCode 621)
*   **Hint:** Greedy approach. Always pick the task with the highest frequency that is not in the "cooldown" period.
*   **Key:** Use a Max-Heap to store counts. Use a temporary queue to store tasks currently in cooldown.
*   **提示：** 貪婪法。總是選擇頻率最高且不在「冷卻」期的任務。使用最大堆積儲存計數，臨時佇列儲存冷卻中的任務。

### 3. Advanced: Trapping Rain Water II (LeetCode 407)
*   **Hint:** This is a BFS + Heap problem. Start from the boundary (min-heap of heights).
*   **Key:** Visualize water level rising from the lowest boundary inwards. The heap maintains the current lowest barrier.
*   **提示：** 這是 BFS + 堆積的問題。從邊界開始（高度的最小堆積）。想像水位從最低邊界向內上升。堆積維護當前的最低屏障。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Container Type:** Did I write `vector<T>` in the template arguments for Min-Heap?
    **容器類型：** 我是否在最小堆積的模板參數中寫了 `vector<T>`？
*   [ ] **Comparator Direction:** Does my comparator return `true` if left < right? (For `priority_queue`, this creates a Max-Heap).
    **比較器方向：** 我的比較器在 left < right 時是否回傳 `true`？（對於 PQ，這會建立最大堆積）。
*   [ ] **Empty Check:** Do I check `!pq.empty()` before calling `top()` or `pop()`?
    **空檢查：** 我是否在呼叫 `top()` 或 `pop()` 前檢查了 `!pq.empty()`？
*   [ ] **Reference in Loops:** When iterating or processing, am I using references `const auto&` to avoid copying complex structs?
    **迴圈引用：** 迭代或處理時，我是否使用了引用 `const auto&` 來避免複製複雜結構？

---

## 9. Memory Anchors (記憶錨點)

*   **The VIP Line (VIP 通道):**
    Imagine a club entrance. A Queue is First-Come-First-Serve. A **Priority Queue** lets the VIP (highest value/priority) cut to the front immediately.
    想像夜店入口。一般佇列是先到先服務。**優先佇列**讓 VIP（最高價值/優先級）直接插隊到最前面。

*   **The Pyramid (金字塔):**
    Max-Heap is a pyramid where the Pharaoh (Max value) is always at the peak. Every manager (parent) is more powerful than their subordinates (children).
    最大堆積是一座金字塔，法老（最大值）總是在頂端。每個管理者（父節點）都比其下屬（子節點）更有權力。