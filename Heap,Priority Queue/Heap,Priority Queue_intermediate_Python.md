# Comprehensive Guide: Heap & Priority Queue
# 全方位指南：堆積與優先佇列

## 1. Learning Objectives (學習目標)

*   **Master the internal mechanics and complexity nuances.**
    掌握內部運作機制與複雜度細節（特別是 $O(N)$ 的建堆與 $O(N \log N)$ 的差異）。
*   **Identify patterns for "Top K" and "Streaming Data" problems.**
    識別「前 K 個元素」與「串流數據」問題的解題模式。
*   **Proficiency in Python’s `heapq` module and handling Max-Heap tricks.**
    熟練 Python `heapq` 模組以及處理最大堆積（Max-Heap）的技巧。
*   **Understand advanced applications like Two Heaps and Lazy Removal.**
    理解如「雙堆積」與「延遲刪除」等進階應用。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
*   **Definition:** A Heap is a specialized tree-based data structure that satisfies the heap property (parent is always $\le$ or $\ge$ children). A Priority Queue is an Abstract Data Type (ADT) often implemented using a Heap.
    **定義：** 堆積是一種滿足堆積性質（父節點總是 $\le$ 或 $\ge$ 子節點）的樹狀資料結構。優先佇列是一種抽象資料型別 (ADT)，通常使用堆積來實作。
*   **Intuition:** Think of it as an ER triage system, not a FIFO queue. Patients are treated based on severity (priority), not arrival time.
    **直覺：** 將其視為急診室檢傷分類系統，而非先進先出 (FIFO) 佇列。病患是根據嚴重程度（優先級）被治療，而非到達時間。

### Time Complexity (時間複雜度)
*   **Push (Insertion):** $O(\log N)$
*   **Pop (Extract Min/Max):** $O(\log N)$
*   **Peek (Get Min/Max):** $O(1)$
*   **Heapify (Build from array):** $O(N)$ — *Crucial for Senior interviews.*
    **建堆（從陣列建立）：** $O(N)$ — *這對資深面試至關重要。*

### Use Cases (適用場景)
*   Finding the $K^{th}$ largest/smallest element. (尋找第 K 大/小的元素)
*   Merging $K$ sorted lists/streams. (合併 K 個已排序的列表/串流)
*   Dijkstra’s Algorithm / Prim’s Algorithm. (Dijkstra 或 Prim 演算法)
*   Scheduling tasks based on priority. (基於優先級的任務排程)

### Non-Use Cases (不適用場景)
*   Searching for an arbitrary element ($O(N)$). (搜尋任意元素)
*   Finding the Successor/Predecessor ($O(N)$). (尋找後繼/前驅節點)

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Top K Elements (前 K 個元素)
*   **Pattern:** Keep a Min-Heap of size $K$ to find the $K$ largest elements.
    **模式：** 維護一個大小為 $K$ 的最小堆積，以找出 $K$ 個最大元素。
*   **Why:** The root of the Min-Heap is the $K^{th}$ largest seen so far; anything smaller is discarded.
    **原因：** 最小堆積的根節點是目前為止第 $K$ 大的元素；任何比它小的都會被丟棄。

### B. Merge K Sorted Lists (合併 K 個排序列表)
*   **Pattern:** Push the first element of each list into a Min-Heap. Pop the smallest, then push the next element from the same list.
    **模式：** 將每個列表的第一個元素推入最小堆積。彈出最小的元素，然後將該元素所屬列表的下一個元素推入堆積。

### C. Two Heaps (雙堆積)
*   **Pattern:** Maintain a Max-Heap for the lower half of data and a Min-Heap for the upper half to find the Median.
    **模式：** 維護一個最大堆積存放數據的下半部，以及一個最小堆積存放上半部，用以尋找中位數。

---

## 4. Example Walkthrough (範例講解)

### Problem: Top K Frequent Elements
### 問題：前 K 個高頻元素

**Problem Statement:** Given an integer array `nums` and an integer `k`, return the `k` most frequent elements.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `k`，回傳出現頻率最高的 `k` 個元素。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Count frequencies, sort all unique elements by frequency.
    *   計算頻率，將所有唯一元素按頻率排序。
    *   Complexity: $O(N \log N)$. (Sorting dominates)
    *   複雜度：$O(N \log N)$。（排序佔主導）

2.  **Optimization (Heap):**
    *   Count frequencies ($O(N)$).
    *   計算頻率 ($O(N)$)。
    *   Maintain a heap of size $k$.
    *   維護一個大小為 $k$ 的堆積。
    *   Complexity: $O(N \log K)$. (Better than $N \log N$ when $K < N$)
    *   複雜度：$O(N \log K)$。（當 $K < N$ 時優於 $N \log N$）

3.  **Best Solution (Bucket Sort - for this specific problem):**
    *   Map frequency to a list of numbers. Complexity $O(N)$.
    *   將頻率映射到數字列表。複雜度 $O(N)$。
    *   *Note: In a Heap interview, show the Heap solution first, then mention Bucket Sort as a follow-up optimization.*
    *   *註：在堆積的面試中，先展示堆積解法，再提及桶排序作為後續優化。*

### Python Reference Solution (Python 參考解)

```python
import heapq
from collections import Counter
from typing import List

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # 1. Count frequencies
        # 1. 計算頻率
        count = Counter(nums) 
        
        # 2. Use a Min-Heap to keep the top k elements
        # 2. 使用最小堆積來保留前 k 個元素
        # The heap will store tuples: (frequency, value)
        # 堆積將儲存元組：(頻率, 數值)
        heap = []
        
        for num, freq in count.items():
            # Push current element
            # 推入當前元素
            heapq.heappush(heap, (freq, num))
            
            # If heap size exceeds k, remove the smallest frequency
            # 如果堆積大小超過 k，移除頻率最小的元素
            if len(heap) > k:
                heapq.heappop(heap)
        
        # 3. Extract the values from the heap
        # 3. 從堆積中提取數值
        return [val for freq, val in heap]

# Alternative One-Liner (Good to know, but explain the manual way first)
# 替代的一行解法（值得知道，但先解釋手動實作的方式）
# return [item for item, count in Counter(nums).most_common(k)]
```

### Error Demonstration & Why (錯誤示範 & 為何錯)

```python
# Bad Approach: Pushing all N elements then popping K times
# 糟糕的方法：推入所有 N 個元素，然後彈出 K 次
for num, freq in count.items():
    heapq.heappush(heap, (-freq, num)) # Max-Heap simulation
    
# Why wrong? 
# Complexity becomes O(N log N) because the heap grows to size N.
# 為何錯？
# 複雜度變成 O(N log N)，因為堆積增長到了大小 N。
# Keeping size K ensures O(N log K).
# 保持大小為 K 能確保 O(N log K)。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱 / 混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Min-Heap vs Max-Heap** | Python's `heapq` only implements Min-Heap. | Multiply numbers by `-1` to simulate a Max-Heap. <br> 將數字乘以 `-1` 來模擬最大堆積。 |
| **Heapify vs Push** | `heapq.heapify(list)` vs pushing elements one by one. | `heapify` is $O(N)$. Pushing $N$ times is $O(N \log N)$. Always prefer `heapify` for initial build. <br> `heapify` 是 $O(N)$。推入 $N$ 次是 $O(N \log N)$。初始建立時總是優先選擇 `heapify`。 |
| **Tuple Comparison** | Pushing `(priority, item)` where item is an object without `__lt__`. | If priorities are equal, Python compares the second element. If it's not comparable, it crashes. Use a wrapper class or ensure unique priorities. <br> 若優先級相等，Python 會比較第二個元素。若不可比較，程式會崩潰。使用封裝類別或確保優先級唯一。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the need for Extremums:** "Since we need to repeatedly access the smallest/largest element..."
    **識別對極值的需求：** 「由於我們需要重複存取最小/最大的元素……」
2.  **Discuss Trade-offs:** "Sorting allows access, but maintaining a sorted array is expensive ($O(N)$). A heap balances access ($O(1)$) and maintenance ($O(\log N)$)."
    **討論權衡：** 「排序允許存取，但維護排序陣列很昂貴 ($O(N)$)。堆積在存取 ($O(1)$) 和維護 ($O(\log N)$) 之間取得了平衡。」

### Whiteboard Strategy (白板策略)
*   **Draw the Tree:** Visualize the heap as a binary tree to explain the logic.
    **畫出樹狀圖：** 將堆積視覺化為二元樹以解釋邏輯。
*   **Map to Array:** Briefly show how indices map (Parent $i$ $\rightarrow$ Children $2i+1, 2i+2$) to show implementation knowledge.
    **映射到陣列：** 簡要展示索引如何映射（父節點 $i$ $\rightarrow$ 子節點 $2i+1, 2i+2$）以展示實作知識。

### Common Follow-ups (常見追問)
*   **Q:** How to handle dynamic updates (change priority)?
    **問：** 如何處理動態更新（改變優先級）？
    *   **A:** Python `heapq` doesn't support efficient remove. Use "Lazy Removal" (mark as deleted in a hash map, pop only when it comes to top).
    *   **答：** Python `heapq` 不支援高效刪除。使用「延遲刪除」（在雜湊表中標記為已刪除，只有當它浮到頂端時才彈出）。

---

## 7. Practice Problems (練習題)

### Easy: Last Stone Weight
*   **Prompt:** Smash two heaviest stones together. If $x < y$, $y-x$ remains. Return last stone.
    **題目：** 將兩顆最重的石頭互砸。若 $x < y$，剩下 $y-x$。回傳最後剩下的石頭。
*   **Hint:** Standard Max-Heap simulation.
    **提示：** 標準的最大堆積模擬。
*   **Key:** Remember to negate values for Python heap.
    **關鍵：** 記得在 Python 堆積中將數值取負。

### Medium: K Closest Points to Origin
*   **Prompt:** Find $K$ points closest to $(0,0)$.
    **題目：** 找出距離 $(0,0)$ 最近的 $K$ 個點。
*   **Hint:** Max-Heap of size $K$. Why Max-Heap? Because we want to evict the *farthest* points to keep the closest ones.
    **提示：** 大小為 $K$ 的最大堆積。為什麼是最大堆積？因為我們要驅逐*最遠*的點，以保留最近的點。

### Hard: IPO (LeetCode 502)
*   **Prompt:** Maximize capital by selecting at most $k$ projects. Each project has profit and capital requirement.
    **題目：** 透過選擇最多 $k$ 個專案來最大化資本。每個專案都有利潤和資本需求。
*   **Hint:** Greedy + Two Heaps (or Sort + Heap).
    **提示：** 貪婪演算法 + 雙堆積（或排序 + 堆積）。
*   **Approach:** Sort projects by capital. Push affordable projects into a Max-Heap (based on profit). Pop max profit, increase capital, repeat.
    **思路：** 按資本對專案排序。將負擔得起的專案推入最大堆積（基於利潤）。彈出最大利潤，增加資本，重複。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] Did I handle the Min-Heap vs Max-Heap logic correctly (negation)? (我是否正確處理了最小堆積與最大堆積的邏輯（取負）？)
- [ ] Is my complexity $O(N \log K)$ or $O(N \log N)$? (我的複雜度是 $O(N \log K)$ 還是 $O(N \log N)$？)
- [ ] Did I consider the case where $K > N$? (我是否考慮了 $K > N$ 的情況？)
- [ ] If using tuples `(priority, item)`, are items comparable? (如果使用元組 `(priority, item)`，項目是否可比較？)

---

## 9. Memory Anchors (記憶錨點)

*   **Visual:** **The Pyramid of Power (權力金字塔)**.
    The CEO (Min or Max) is at the top. You can only access the CEO directly. To find the middle manager, you have to fire the CEO first.
    CEO（最小值或最大值）在頂端。你只能直接接觸 CEO。要找到中層管理者，你必須先開除 CEO。
*   **Analogy:** **VIP Club Bouncer (VIP 俱樂部保鑣)**.
    (For Top K problem) The club only holds $K$ people. When a new person comes, the "least important" person inside (Min-Heap root) gets kicked out if the new person is more important.
    （針對前 K 個問題）俱樂部只能容納 $K$ 人。當新人到來時，如果新人更重要，裡面的「最不重要」的人（最小堆積根節點）就會被踢出去。