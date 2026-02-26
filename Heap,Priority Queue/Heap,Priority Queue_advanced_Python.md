# Advanced Heap & Priority Queue Guide
# 進階堆積與優先佇列指南

## 1. Learning Goals (學習目標)

By the end of this module, you should be able to:
完成本單元後，你應能夠：

1.  **Master Internal Mechanics & Complexity Nuances:** Understand why `heapify` is $O(N)$ while pushing $N$ elements is $O(N \log N)$, and how binary heaps differ from Fibonacci heaps in theory.
    **掌握內部機制與複雜度細節：** 理解為何 `heapify` 是 $O(N)$ 而推入 $N$ 個元素是 $O(N \log N)$，以及二元堆積與費氏堆積在理論上的差異。
2.  **Implement Advanced Patterns:** proficiently use "Two Heaps" (for median), "Lazy Deletion" (for dynamic updates), and "K-way Merge".
    **實作進階模式：** 熟練運用「雙堆積」（求中位數）、「延遲刪除」（處理動態更新）與「多路合併」。
3.  **Apply to System Design:** Recognize heap applications in Load Balancers, Rate Limiters, and Task Schedulers.
    **應用於系統設計：** 辨識堆積在負載平衡器、限流器與任務排程器中的應用。
4.  **Optimize for Python:** Handle Python's min-heap-only limitation elegantly using negation and custom wrappers.
    **針對 Python 優化：** 優雅地利用負值與自定義包裝器來處理 Python 僅有最小堆積的限制。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Heap is a specialized tree-based data structure that satisfies the heap property: in a max heap, for any given node C, if P is a parent node of C, then the key (the value) of P is greater than or equal to the key of C.
堆積是一種特殊的樹狀資料結構，滿足堆積屬性：在最大堆積中，對於任意節點 C，若 P 是 C 的父節點，則 P 的鍵值（數值）大於或等於 C 的鍵值。

### Intuition (直覺)
Think of a Heap as an **"Emergency Room Triage System."**
將堆積想像成**「急診室檢傷分類系統」。**
You don't care who is 5th or 6th in line; you only care about extracting the patient with the highest severity (priority) immediately.
你不在乎誰排在第 5 或第 6 位；你只在乎立即取出病情最嚴重（優先級最高）的病患。

### Complexity Analysis (複雜度分析)

| Operation | Time Complexity | Note (備註) |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(\log N)$ | Sift up (上濾) |
| **Pop (Extract Min/Max)** | $O(\log N)$ | Swap root with last, then sift down (根與末位交換後下濾) |
| **Peek (Top)** | $O(1)$ | Direct access to root (直接存取根節點) |
| **Build Heap (Heapify)** | **$O(N)$** | *Crucial for Senior interviews.* It converges mathematically faster than $N \log N$. (這對資深面試至關重要，數學上收斂速度快於 $N \log N$) |
| **Search (Arbitrary)** | $O(N)$ | Heaps are not sorted; they are only ordered vertically. (堆積並未完全排序，僅有垂直有序性) |

### Use Cases (適用場景)
*   **Top-K Problems:** Finding the K largest/smallest elements in real-time.
    **Top-K 問題：** 即時尋找第 K 大/小的元素。
*   **Scheduling:** Processing tasks by priority (e.g., OS process scheduling).
    **排程：** 依優先級處理任務（例如作業系統行程排程）。
*   **Graph Algorithms:** Dijkstra’s (Shortest Path), Prim’s (MST).
    **圖演算法：** Dijkstra（最短路徑）、Prim（最小生成樹）。
*   **Merge K Sorted Streams:** Efficiently combining multiple sorted data sources.
    **合併 K 個有序串流：** 有效率地結合多個已排序的資料來源。

### Not Suitable (不適用場景)
*   **Searching/Lookup:** Use a Hash Map or BST instead.
    **搜尋/查找：** 請改用雜湊表或二元搜尋樹。
*   **Range Queries:** Segment Trees are better suited.
    **區間查詢：** 線段樹更為合適。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, simple "Top K" is often just a sub-component. Focus on these patterns:
對資深工程師而言，單純的「Top K」通常只是子元件。請專注於以下模式：

1.  **Two Heaps (Dual Priority Queues):**
    *   Maintain a Min-Heap and a Max-Heap to track the median or split data into two halves.
    *   維護一個最小堆積與一個最大堆積，以追蹤中位數或將資料切分為兩半。
2.  **Lazy Deletion (延遲刪除):**
    *   Since removing an arbitrary element is $O(N)$ or hard to implement, mark it as "deleted" in a Hash Map and actually remove it only when it floats to the top.
    *   由於刪除任意元素需 $O(N)$ 或難以實作，先在雜湊表中將其標記為「已刪除」，待其浮至堆積頂端時再實際移除。
3.  **K-Way Merge (多路合併):**
    *   Keep the head of $K$ lists in a heap to find the global minimum efficiently.
    *   將 $K$ 個列表的頭部放入堆積，以有效率地找出全域最小值。

---

## 4. Example Walkthrough (範例講解)

### Problem: Find Median from Data Stream (數據流的中位數)
**Difficulty:** Hard
**Context:** Classic "Two Heaps" pattern.
**情境：** 經典的「雙堆積」模式。

### Problem Statement (問題重述)
Implement a class that supports adding integers from a data stream and finding the median of all elements seen so far in $O(1)$ time.
實作一個類別，支援從數據流中添加整數，並在 $O(1)$ 時間內找出目前所有元素的中位數。

### Thought Process (思路)

1.  **Brute Force:** Store in a list, sort every time `findMedian` is called. Time: $O(N \log N)$. Too slow.
    **暴力解：** 存入列表，每次呼叫 `findMedian` 時排序。時間：$O(N \log N)$。太慢。
2.  **Optimization (Insertion Sort):** Keep the list sorted. Insert takes $O(N)$. Median is $O(1)$. Total $O(N)$. Better, but not optimal for large streams.
    **優化（插入排序）：** 保持列表有序。插入需 $O(N)$。中位數 $O(1)$。總計 $O(N)$。較好，但對大流量仍非最佳。
3.  **Optimal (Two Heaps):**
    *   Concept: Split the data into two halves: "Small Half" and "Large Half".
    *   概念：將資料切分為兩半：「較小半部」與「較大半部」。
    *   Use a **Max-Heap** for the Small Half (so we can quickly access the largest of the small numbers).
    *   使用**最大堆積**儲存較小半部（以便快速存取小數中的最大值）。
    *   Use a **Min-Heap** for the Large Half (so we can quickly access the smallest of the large numbers).
    *   使用**最小堆積**儲存較大半部（以便快速存取大數中的最小值）。
    *   Balance: Keep the sizes equal (or Max-Heap has 1 more).
    *   平衡：保持兩邊大小相等（或最大堆積多 1 個）。

### Python Solution (Python 參考解)

```python
import heapq

class MedianFinder:
    def __init__(self):
        # Max-heap for the smaller half of numbers.
        # Python's heapq is a min-heap, so we store negated values.
        # 最大堆積用於儲存較小的一半數字。
        # Python 的 heapq 是最小堆積，因此我們儲存負值。
        self.small_half = []  
        
        # Min-heap for the larger half of numbers.
        # 最小堆積用於儲存較大的一半數字。
        self.large_half = []  

    def addNum(self, num: int) -> None:
        """
        Adds a number to the data structure.
        Time Complexity: O(log N)
        將數字加入資料結構。
        時間複雜度：O(log N)
        """
        # Step 1: Always push to small_half (max-heap) first.
        # We push -num to simulate max-heap behavior.
        # 步驟 1：總是先推入 small_half（最大堆積）。
        # 我們推入 -num 以模擬最大堆積行為。
        heapq.heappush(self.small_half, -num)
        
        # Step 2: Ensure the largest element in small_half is <= smallest in large_half.
        # Move the top of small_half to large_half.
        # 步驟 2：確保 small_half 中的最大元素 <= large_half 中的最小元素。
        # 將 small_half 的頂端移至 large_half。
        val = -heapq.heappop(self.small_half)
        heapq.heappush(self.large_half, val)
        
        # Step 3: Balance the sizes. 
        # We allow small_half to have at most 1 more element than large_half.
        # 步驟 3：平衡大小。
        # 我們允許 small_half 比 large_half 最多由 1 個元素。
        if len(self.small_half) < len(self.large_half):
            val = heapq.heappop(self.large_half)
            heapq.heappush(self.small_half, -val)

    def findMedian(self) -> float:
        """
        Returns the median of current data stream.
        Time Complexity: O(1)
        回傳目前數據流的中位數。
        時間複雜度：O(1)
        """
        # If small_half has more elements, the median is its top.
        # 若 small_half 元素較多，中位數即為其頂端。
        if len(self.small_half) > len(self.large_half):
            return -self.small_half[0]
        
        # Otherwise, average the tops of both heaps.
        # 否則，取兩個堆積頂端的平均值。
        return (-self.small_half[0] + self.large_half[0]) / 2.0

# Example Usage
# obj = MedianFinder()
# obj.addNum(1)
# obj.addNum(2)
# print(obj.findMedian()) -> 1.5
# obj.addNum(3)
# print(obj.findMedian()) -> 2
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Clarification (陷阱 / 釐清) |
| :--- | :--- |
| **Python's `heapq`** | It is **only** a Min-Heap. For Max-Heap, you **must** negate numbers or write a wrapper class. <br> 它是**僅有**的最小堆積。若需最大堆積，**必須**將數字取負或撰寫包裝類別。 |
| **Heapify vs Push** | `heapify(list)` is $O(N)$. Creating an empty heap and pushing $N$ items is $O(N \log N)$. <br> `heapify(list)` 是 $O(N)$。建立空堆積並推入 $N$ 個項目是 $O(N \log N)$。 |
| **Sorted vs Heap** | A heap is **not** a sorted list. `heap[i]` is not necessarily smaller than `heap[i+1]`. <br> 堆積**不是**排序列表。`heap[i]` 不一定小於 `heap[i+1]`。 |
| **Removal** | Removing a non-root element is tricky. Don't try to `.remove()` from the list directly (it breaks the heap structure or is $O(N)$). Use **Lazy Deletion**. <br> 移除非根節點很棘手。不要嘗試直接從列表 `.remove()`（這會破壞堆積結構或導致 $O(N)$）。請使用**延遲刪除**。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the need for Order:** "We need repeated access to the minimum/maximum element, but we don't need the entire dataset to be sorted."
    **確認排序需求：** 「我們需要重複存取最小/最大元素，但不需要整個資料集完全排序。」
2.  **Justify Complexity:** "Using a Heap reduces the insertion/deletion time to logarithmic, compared to linear time with a sorted array."
    **論證複雜度：** 「相較於排序陣列的線性時間，使用堆積將插入/刪除時間降低至對數級。」
3.  **Address Python Specifics:** "Since I'm using Python, I will use `heapq`. For the max-heap requirement, I will store negated values."
    **處理 Python 特性：** 「由於我使用 Python，我會用 `heapq`。針對最大堆積的需求，我會儲存負值。」

### Whiteboard Strategy (白板策略)
*   Do **not** implement the Heap class from scratch unless explicitly asked. Use standard libraries (`import heapq`).
    **不要**從頭實作 Heap 類別，除非被明確要求。請使用標準函式庫（`import heapq`）。
*   If you need to store complex objects (e.g., `(priority, timestamp, task_id)`), explain how tuples are compared element-by-element.
    若需儲存複雜物件（如 `(priority, timestamp, task_id)`），請解釋 tuple 是如何逐項比較的。

### Common Follow-ups (常見追問)
*   **Q:** How to handle data that doesn't fit in memory?
    **A:** External Sort using Merge K Sorted Lists (Heaps).
    **問：** 如何處理記憶體放不下的資料？
    **答：** 使用基於堆積的外部排序（合併 K 個有序列表）。
*   **Q:** How to update the priority of an existing element?
    **A:** Use a Hash Map to map `item -> index` (complex to maintain) or use **Lazy Deletion**.
    **問：** 如何更新現有元素的優先級？
    **答：** 使用雜湊表映射 `item -> index`（維護困難）或使用**延遲刪除**。

---

## 7. Practice Problems (練習題)

### 1. Easy/Warm-up: Last Stone Weight
*   **Problem:** Smash two heaviest stones together. If $x \neq y$, the stone $y-x$ remains. Return last stone weight.
    **問題：** 將兩顆最重的石頭互砸。若 $x \neq y$，留下 $y-x$ 的石頭。回傳最後石頭的重量。
*   **Hint:** Max-Heap simulation.
    **提示：** 最大堆積模擬。
*   **Key:** Python requires negation for max-heap.
    **關鍵：** Python 需取負值以實現最大堆積。

### 2. Intermediate: Task Scheduler
*   **Problem:** CPU tasks with characters 'A'...'Z' and cooling time $n$. Minimize total intervals.
    **問題：** CPU 任務 'A'...'Z' 與冷卻時間 $n$。最小化總間隔數。
*   **Hint:** Greedy + Max-Heap. Always schedule the most frequent task available.
    **提示：** 貪婪法 + 最大堆積。總是排程當前可用的頻率最高任務。
*   **Key:** You might need a temporary queue to hold tasks during their "cooling" period before pushing them back to the heap.
    **關鍵：** 你可能需要一個暫存佇列來保留處於「冷卻期」的任務，之後再推回堆積。

### 3. Advanced: Minimum Cost to Hire K Workers
*   **Problem:** Hire $K$ workers. Pay them proportional to their quality relative to a "captain", but no less than their minimum wage expectation. Minimize total cost.
    **問題：** 雇用 $K$ 名工人。薪資需與其品質成比例（相對於某位「隊長」），但不得低於其最低薪資期望。最小化總成本。
*   **Hint:** Sort by `wage/quality` ratio. Iterate and maintain the smallest $K$ qualities using a Max-Heap (to remove the largest quality to minimize sum).
    **提示：** 依 `wage/quality` 比率排序。遍歷並使用最大堆積維護最小的 $K$ 個品質值（以便移除最大的品質值來最小化總和）。
*   **Why Advanced:** Combines Math (ratios), Sorting, and Heap.
    **為何進階：** 結合數學（比率）、排序與堆積。

---

## 8. Quick Checklists (快速檢核表)

Before submitting code, verify:
提交程式碼前，請確認：

- [ ] **Direction:** Did I use Min-Heap or Max-Heap correctly? (Negated values in Python?)
    **方向：** 我是否正確使用了最小堆積或最大堆積？（Python 中是否取負？）
- [ ] **Empty Checks:** Did I handle `heappop` on an empty heap?
    **空值檢查：** 我是否處理了對空堆積執行 `heappop` 的情況？
- [ ] **Complexity:** Did I use `heapify` ($O(N)$) instead of pushing one by one ($O(N \log N)$) for initial build?
    **複雜度：** 初始建構時，我是否使用了 `heapify` ($O(N)$) 而非逐一推入 ($O(N \log N)$)？
- [ ] **Tuple Comparison:** If storing tuples `(a, b)`, am I aware that if `a` is equal, it compares `b`?
    **Tuple 比較：** 若儲存 `(a, b)`，我是否意識到當 `a` 相等時，會比較 `b`？

---

## 9. Memory Anchors (記憶錨點)

*   **Visual:** **The Pyramid (金字塔)**. The Pharoah (Root) is at the top. He is the most important (Max/Min). The hierarchy below him is loosely ordered, but everyone directly under him is "lesser" than him.
    **圖像：****金字塔**。法老（根節點）在頂端。他是最重要的（最大/最小）。他底下的階層結構鬆散，但直接在他下面的人都比他「低階」。
*   **Analogy:** **The Bouncer (保鑣)**. A bouncer at a club only cares about letting the VIP (highest priority) in next. He doesn't line up everyone perfectly by height; he just grabs the most important person from the crowd.
    **類比：****保鑣**。夜店的保鑣只在乎接下來讓 VIP（最高優先級）進入。他不會把所有人按身高完美排隊；他只是從人群中抓出最重要的人。