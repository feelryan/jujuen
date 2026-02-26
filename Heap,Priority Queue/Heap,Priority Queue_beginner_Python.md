# Heap & Priority Queue: The Essentials (Beginner Level)
# 堆積與優先佇列：基礎精要

## 1. Learning Objectives (學習目標)

1.  **Master the Internal Structure:** Understand how a binary heap maps to an array and the index relationships ($parent$, $left$, $right$).
    **掌握內部結構：** 理解二元堆積如何映射到陣列，以及索引之間的關係（$parent$, $left$, $right$）。
2.  **Proficiency with Python’s `heapq`:** Gain fluency in using the standard library for Min-Heaps and the workarounds for Max-Heaps.
    **熟練 Python 的 `heapq`：** 流暢使用標準函式庫處理最小堆積（Min-Heap），並掌握最大堆積（Max-Heap）的變通解法。
3.  **Complexity Analysis:** Distinguish between building a heap ($O(N)$) and maintaining it ($O(\log N)$).
    **複雜度分析：** 區分建構堆積（$O(N)$）與維護堆積（$O(\log N)$）的差異。
4.  **Identify "Top K" Patterns:** Recognize problems requiring access to the extreme elements (min/max) efficiently.
    **識別「Top K」模式：** 辨識需要高效存取極值（最小/最大）的問題。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A **Heap** is a specialized tree-based data structure that satisfies the heap property: in a **Min-Heap**, the parent is always smaller than or equal to its children.
**堆積（Heap）** 是一種特殊的樹狀資料結構，滿足堆積屬性：在 **最小堆積（Min-Heap）** 中，父節點總是小於或等於其子節點。

A **Priority Queue** is an abstract data type where each element has a priority, and the element with the highest priority is served first; a Heap is the most common implementation.
**優先佇列（Priority Queue）** 是一種抽象資料型別，每個元素都有優先級，優先級最高的元素最先被處理；堆積是其最常見的實作方式。

### Intuition (直覺)
Think of a Heap as a "dynamic organizer" that only guarantees the order of the top element (the root).
將堆積視為一個「動態整理器」，它只保證最頂端元素（根節點）的順序。
It does not sort the entire data; it only ensures you can grab the "most important" item instantly.
它不對整個資料進行排序；它只確保你能瞬間抓取「最重要」的項目。

### Complexity (複雜度)

| Operation | Time Complexity | Description |
| :--- | :--- | :--- |
| **Peek (Top)** | $O(1)$ | Access the min/max element without removal.<br>存取最小/最大元素但不移除。 |
| **Push (Insert)** | $O(\log N)$ | Add element and "bubble up".<br>新增元素並「向上浮動」。 |
| **Pop (Extract)** | $O(\log N)$ | Remove top, move last to top, and "sift down".<br>移除頂端，將末端移至頂端，並「向下過濾」。 |
| **Heapify (Build)**| $O(N)$ | Build heap from an unsorted array (mathematically proven).<br>從未排序陣列建構堆積（數學上已證明）。 |
| **Space** | $O(N)$ | Array storage.<br>陣列儲存空間。 |

### When to Use (適用場景)
*   Finding the $K$-th largest/smallest element.
    尋找第 $K$ 大/小的元素。
*   Continuous access to the minimum/maximum element in a data stream.
    在資料流中持續存取最小/最大值。
*   Scheduling tasks based on priority.
    基於優先級的任務排程。

### When NOT to Use (不適用場景)
*   Searching for an arbitrary element ($O(N)$).
    搜尋任意元素（$O(N)$）。
*   Finding the min/max in a static, sorted array ($O(1)$ is enough).
    在靜態且已排序的陣列中找極值（$O(1)$ 就足夠了）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Top K Elements (Top K 元素)
Keep a heap of size $K$ to track the largest or smallest elements seen so far.
維護一個大小為 $K$ 的堆積，用來追蹤目前為止遇到的最大或最小元素。

### Pattern 2: Merge K Sorted Lists (合併 K 個排序串列)
Use a Min-Heap to keep track of the current smallest head among $K$ lists.
使用最小堆積來追蹤 $K$ 個串列中目前最小的頭部元素。

### Pattern 3: Two Heaps (雙堆積 - 稍進階)
Use a Max-Heap for the lower half and a Min-Heap for the upper half to find the median.
使用一個最大堆積儲存下半部數據，一個最小堆積儲存上半部數據，以尋找中位數。

---

## 4. Example Walkthrough (範例講解)

### Problem: Kth Largest Element in an Array
### 問題：陣列中第 K 大的元素

**Problem Statement:** Given an integer array `nums` and an integer `k`, return the $k^{th}$ largest element in the array.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳陣列中第 $k$ 大的元素。

#### Approach 1: Brute Force (Sorting) / 暴力法（排序）
Sort the array descending and take index $k-1$.
將陣列降序排列，取索引 $k-1$。
*   Time: $O(N \log N)$
*   Space: $O(1)$ or $O(N)$ depending on sort implementation.

#### Approach 2: Min-Heap of Size K (Optimal for Stream) / 大小為 K 的最小堆積（資料流最佳解）
Maintain a Min-Heap of size $K$.
維護一個大小為 $K$ 的最小堆積。
If the heap size exceeds $K$, remove the smallest element.
如果堆積大小超過 $K$，移除最小的元素。
The root of the heap will be the $K^{th}$ largest.
堆積的根節點即為第 $K$ 大的元素。
*   Time: $O(N \log K)$
*   Space: $O(K)$

#### Python Solution (Python 參考解)

```python
import heapq
from typing import List

class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        """
        Finds the Kth largest element using a Min-Heap of size K.
        使用大小為 K 的最小堆積尋找第 K 大元素。
        """
        
        # Initialize a min-heap
        # 初始化一個最小堆積
        min_heap = []
        
        for num in nums:
            # Push the current number into the heap
            # 將當前數字推入堆積
            heapq.heappush(min_heap, num)
            
            # If the heap grows larger than k, remove the smallest element
            # Because we want the K *largest*, we discard the small ones.
            # 如果堆積大小超過 k，移除最小的元素
            # 因為我們要找第 K *大*，所以捨棄較小的數值。
            if len(min_heap) > k:
                heapq.heappop(min_heap)
                
        # The root of the min-heap is now the Kth largest element
        # 最小堆積的根節點現在就是第 K 大的元素
        return min_heap[0]

# Example Usage / 範例用法
# nums = [3, 2, 1, 5, 6, 4], k = 2
# Heap evolution:
# [3] -> [2, 3] -> [1, 2, 3] -> pop 1 -> [2, 3]
# [2, 3] push 5 -> [2, 3, 5] -> pop 2 -> [3, 5]
# [3, 5] push 6 -> [3, 5, 6] -> pop 3 -> [5, 6]
# [5, 6] push 4 -> [4, 5, 6] -> pop 4 -> [5, 6]
# Result: 5
```

#### Why this is better than sorting? (為何比排序好？)
While $O(N \log N)$ is acceptable, $O(N \log K)$ is faster when $K$ is small relative to $N$.
雖然 $O(N \log N)$ 可接受，但當 $K$ 遠小於 $N$ 時，$O(N \log K)$ 更快。
Crucially, this approach works on **streaming data** where you cannot sort the whole input at once.
關鍵在於，此方法適用於**串流資料**，因為你無法一次對所有輸入進行排序。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Clarification (釐清) |
| :--- | :--- |
| **Python Max-Heap** | Python has no native Max-Heap. Use `heapq` with **negated values** (multiply by -1).<br>Python 沒有原生的最大堆積。使用 `heapq` 搭配**負值**（乘以 -1）。 |
| **Sorted vs. Heap** | A heap is **NOT** a sorted array. It only guarantees `parent <= children`.<br>堆積**不是**已排序陣列。它只保證 `父節點 <= 子節點`。 |
| **Heapify Complexity** | `heapq.heapify(list)` is **$O(N)$**, not $O(N \log N)$. This is a common optimization point.<br>`heapq.heapify(list)` 是 **$O(N)$**，而非 $O(N \log N)$。這是常見的優化點。 |
| **Index 0** | `heap[0]` is always the min element, but `heap[1]` is not necessarily the second smallest.<br>`heap[0]` 總是最小元素，但 `heap[1]` 不一定是第二小的。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the need:** "Since we need to repeatedly access the smallest/largest element..."
    **確認需求：** 「由於我們需要重複存取最小/最大元素……」
2.  **State the Trade-off:** "Sorting takes $O(N \log N)$, but a Heap allows us to maintain the top K elements in $O(N \log K)$."
    **說明權衡：** 「排序需要 $O(N \log N)$，但堆積允許我們以 $O(N \log K)$ 維護前 K 個元素。」
3.  **Mention Python specifics:** "I will use Python's `heapq` module, which implements a min-heap. For max-heap behavior, I'll negate the numbers."
    **提及 Python 特性：** 「我將使用 Python 的 `heapq` 模組，它實作了最小堆積。為了達到最大堆積的效果，我會將數字取負值。」

### Whiteboard Strategy (白板策略)
*   Do not draw a complex tree structure if the array representation suffices.
    如果陣列表示法足夠，不要畫複雜的樹狀結構。
*   If you draw a tree, clearly label the root as the Min/Max.
    如果你畫樹，清楚標示根節點為 Min/Max。
*   Write down the complexity ($N \log K$) immediately to show seniority.
    立即寫下複雜度（$N \log K$）以展現資深程度。

---

## 7. Practice Problems (練習題)

### 1. Last Stone Weight (Easy)
**Concept:** Simulation with Max-Heap.
**概念：** 使用最大堆積進行模擬。
**Hint:** Python `heapq` is min-heap. Store stone weights as negative values to simulate max-heap.
**提示：** Python `heapq` 是最小堆積。將石頭重量存為負值以模擬最大堆積。

### 2. K Closest Points to Origin (Medium)
**Concept:** Top K Pattern.
**概念：** Top K 模式。
**Hint:** Calculate distance squared ($x^2 + y^2$). Maintain a Max-Heap of size $K$. Why Max-Heap? Because to keep the *smallest* $K$ distances, you need to pop the *largest* one when the heap is full.
**提示：** 計算距離平方（$x^2 + y^2$）。維護一個大小為 $K$ 的最大堆積。為什麼是最大堆積？因為要保留*最小*的 $K$ 個距離，當堆積滿時你需要彈出*最大*的那一個。

### 3. Sort Characters By Frequency (Medium)
**Concept:** Hash Map + Heap.
**概念：** 雜湊表 + 堆積。
**Hint:** Count frequencies first ($O(N)$), then push `(-frequency, char)` into a heap, then pop to build the string.
**提示：** 先計算頻率（$O(N)$），然後將 `(-頻率, 字元)` 推入堆積，接著彈出以建構字串。

---

## 8. Checklists (快速檢核表)

*   [ ] **Empty Input:** Did I handle `nums` being empty or $K=0$?
    **空輸入：** 我是否處理了 `nums` 為空或 $K=0$ 的情況？
*   [ ] **Min vs Max:** Did I use the correct heap type? (Remember: Python `heapq` = Min-Heap).
    **最小 vs 最大：** 我是否使用了正確的堆積類型？（記住：Python `heapq` = 最小堆積）。
*   [ ] **Negation:** If using Max-Heap in Python, did I negate values on **both** push and pop?
    **負值處理：** 如果在 Python 使用最大堆積，我是否在推入**和**彈出時都處理了負值？
*   [ ] **Complexity:** Is my solution $O(N \log K)$ or accidentally $O(N \log N)$?
    **複雜度：** 我的解法是 $O(N \log K)$ 還是不小心變成了 $O(N \log N)$？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Corporate Ladder (企業階梯)
*   **The Boss (Root):** In a "Competence Heap" (Max-Heap), the most competent person is at the top.
    **老闆（根節點）：** 在「能力堆積」（最大堆積）中，最有能力的人在頂端。
*   **Middle Management:** They are less competent than the boss, but more competent than their interns.
    **中階主管：** 他們的能力不如老闆，但比實習生強。
*   **No Total Order:** We don't know if the Manager of Dept A is better than the Manager of Dept B. We only know they are both worse than the CEO.
    **無完全順序：** 我們不知道 A 部門經理是否比 B 部門經理強。我們只知道他們都比 CEO 弱。

### The Emergency Room (急診室)
*   **Triage:** Patients are treated based on severity (Priority), not arrival time (Queue).
    **檢傷分類：** 病患是根據嚴重程度（優先級）治療，而非到達時間（佇列）。
*   **The Heap:** The doctor always sees the most critical patient next.
    **堆積：** 醫生總是接著看最危急的病患。