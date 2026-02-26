# Data Structure Module: Stack (Intermediate/Advanced Focus)
# 資料結構模組：Stack 堆疊（中高階聚焦）

## 1. Learning Objectives (學習目標)

By the end of this module, you should be able to:
完成本模組後，你應該能夠：

1.  **Master the Monotonic Stack pattern:** Identify problems requiring "Next Greater/Smaller Element" in $O(N)$ time.
    **掌握單調棧（Monotonic Stack）模式：** 識別需要在 $O(N)$ 時間內解決「下一個更大/更小元素」的問題。
2.  **Convert Recursion to Iteration:** Understand how to simulate system call stacks to transform DFS/Recursive solutions into iterative ones to avoid stack overflow.
    **將遞迴轉換為迭代：** 理解如何模擬系統呼叫堆疊，將 DFS/遞迴解法轉換為迭代解法，以避免堆疊溢位。
3.  **Handle Parsing & Expression Evaluation:** Solve problems involving nested structures (parentheses, calculators) efficiently.
    **處理解析與表達式評估：** 有效率地解決涉及巢狀結構（括號、計算機）的問題。
4.  **Optimize Space Complexity:** Distinguish when a stack is strictly necessary versus when a simple counter or pointer suffices.
    **優化空間複雜度：** 區分何時嚴格需要堆疊，以及何時僅需簡單計數器或指標即可。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Stack is a linear data structure following the **LIFO (Last-In, First-Out)** principle.
Stack 是一種遵循 **LIFO（後進先出）** 原則的線性資料結構。

Think of it as a stack of plates: you can only add or remove the top plate.
可以把它想像成一疊盤子：你只能增加或移除最上面的盤子。

### Complexity (複雜度)
- **Push (Insert):** $O(1)$
- **Pop (Remove):** $O(1)$
- **Peek/Top (Access):** $O(1)$
- **Search:** $O(N)$ (Not designed for random access / 非設計用於隨機存取)

### When to Use (適用場景)
- **Reversing data:** Strings, linked lists, or navigation history.
  **反轉資料：** 字串、鏈結串列或導航紀錄。
- **Matching/Pairing:** Validating parentheses, HTML tags.
  **配對/成對：** 驗證括號、HTML 標籤。
- **Monotonic Relationships:** Finding the nearest larger/smaller element.
  **單調關係：** 尋找最近的較大/較小元素。
- **DFS Simulation:** Iterative tree/graph traversals.
  **DFS 模擬：** 迭代式的樹/圖遍歷。

### When NOT to Use (不適用場景)
- **Random Access:** If you need to access the $k$-th element frequently, use an Array.
  **隨機存取：** 如果你需要頻繁存取第 $k$ 個元素，請使用陣列。
- **FIFO Requirements:** If order needs to be preserved (First-In, First-Out), use a Queue.
  **先進先出需求：** 如果需要保留順序（先進先出），請使用佇列（Queue）。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, basic `push/pop` is trivial. Focus on these patterns:
對於資深工程師而言，基本的 `push/pop` 太過簡單。請專注於以下模式：

### A. Monotonic Stack (單調棧)
Maintains elements in strictly increasing or decreasing order.
維持元素處於嚴格遞增或遞減的順序。
*   **Use case:** "Find the next greater element for every element in an array."
    **使用案例：** 「找出陣列中每個元素的下一個更大元素。」
*   **Mechanism:** Before pushing a new element $X$, pop all elements smaller than $X$ (for a decreasing stack).
    **機制：** 在推入新元素 $X$ 之前，彈出所有小於 $X$ 的元素（針對遞減棧）。

### B. Parentheses & Parsing (括號與解析)
Handles nested logic or order of operations.
處理巢狀邏輯或運算順序。
*   **Use case:** "Validate Parentheses", "Basic Calculator", "Decode String".
    **使用案例：** 「驗證括號」、「基本計算機」、「解碼字串」。

### C. Stack for History (歷史紀錄棧)
Stores previous states to allow backtracking (Undo/Redo).
儲存先前的狀態以允許回溯（復原/重做）。
*   **Use case:** Browser history, Text editor undo function.
    **使用案例：** 瀏覽器紀錄、文字編輯器的復原功能。

---

## 4. Example Walkthrough (範例講解)

### Problem: Daily Temperatures (Monotonic Stack)
### 題目：每日溫度（單調棧）

**Problem Statement:**
Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0`.
給定一個整數陣列 `temperatures` 代表每日溫度，請回傳一個陣列 `answer`，其中 `answer[i]` 是在第 `i` 天之後，需要等待多少天才能獲得更溫暖的溫度。如果未來沒有這一天，則保持 `answer[i] == 0`。

**Example:**
Input: `[73, 74, 75, 71, 69, 72, 76, 73]`
Output: `[1, 1, 4, 2, 1, 1, 0, 0]`

---

### Approach & Evolution (思路與演進)

#### 1. Brute Force (暴力法)
For each day, iterate through all future days to find the first one strictly larger.
對於每一天，遍歷未來的所有天數，找到第一個嚴格較大的溫度。
*   **Complexity:** Time $O(N^2)$, Space $O(1)$.
    **複雜度：** 時間 $O(N^2)$，空間 $O(1)$。
*   **Critique:** Too slow for large inputs ($N=10^5$).
    **評論：** 對於大型輸入（$N=10^5$）來說太慢。

#### 2. Monotonic Stack (Optimization / 最佳解)
We maintain a stack of indices representing days with temperatures that haven't found a warmer day yet.
我們維護一個索引堆疊，代表那些尚未找到更暖日子的天數。

*   **Logic:**
    1. Iterate through the array.
       遍歷陣列。
    2. If the current temperature is warmer than the temperature at the top of the stack, it means we found the "next warmer day" for the day at the top.
       如果當前溫度比堆疊頂端的溫度更暖，這意味著我們找到了堆疊頂端那天的「下一個更暖日」。
    3. Pop the index, calculate the distance, and store it.
       彈出索引，計算距離，並儲存結果。
    4. Repeat until the stack is empty or the top is warmer than current.
       重複此步驟，直到堆疊為空或頂端溫度比當前溫度更暖。
    5. Push the current index.
       推入當前索引。

*   **Complexity:** Time $O(N)$ (Each element is pushed and popped at most once), Space $O(N)$.
    **複雜度：** 時間 $O(N)$（每個元素最多被推入和彈出一次），空間 $O(N)$。

---

### Python Solution (參考解)

```python
from typing import List

def dailyTemperatures(temperatures: List[int]) -> List[int]:
    n = len(temperatures)
    # Initialize answer array with 0s
    # 初始化答案陣列為 0
    answer = [0] * n
    
    # Stack stores indices, not values. This is crucial.
    # Stack 儲存索引，而非數值。這點至關重要。
    stack: List[int] = []
    
    for curr_day, curr_temp in enumerate(temperatures):
        # Check if current temp is warmer than the temp at the top of the stack
        # 檢查當前溫度是否比 stack 頂端的溫度更暖
        while stack and curr_temp > temperatures[stack[-1]]:
            prev_day = stack.pop()
            
            # Calculate the difference in days
            # 計算天數差
            answer[prev_day] = curr_day - prev_day
            
        # Push current index to stack to wait for a warmer day
        # 將當前索引推入 stack，等待更暖的一天
        stack.append(curr_day)
        
    return answer
```

### Common Mistake (錯誤示範)
```python
# MISTAKE: Storing values instead of indices
# 錯誤：儲存數值而非索引
stack = []
for t in temperatures:
    while stack and t > stack[-1]:
        val = stack.pop()
        # We know 'val' found a warmer day, but we lost its position (index)!
        # 我們知道 'val' 找到了更暖的一天，但我們丟失了它的位置（索引）！
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description | Pitfall |
| :--- | :--- | :--- |
| **Stack vs Queue** | LIFO vs FIFO. | Using `list.pop(0)` in Python simulates a Queue but is $O(N)$. Use `collections.deque` for Queues. <br> 在 Python 中使用 `list.pop(0)` 模擬 Queue 但它是 $O(N)$。Queue 請使用 `collections.deque`。 |
| **Storing Values** | Pushing `nums[i]` onto the stack. | **Always store indices** (`i`) if you need to calculate distance or update the original array. <br> 如果需要計算距離或更新原始陣列，**務必儲存索引** (`i`)。 |
| **Monotonicity** | Strictly increasing vs Non-decreasing. | Be careful with `>=` vs `>`. Handling duplicates incorrectly can break the logic. <br> 小心 `>=` 與 `>` 的區別。錯誤處理重複值可能會破壞邏輯。 |
| **Empty Stack** | Accessing `stack[-1]`. | Always check `if stack` before peeking or popping. <br> 在查看或彈出之前，務必檢查 `if stack`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the LIFO nature:** "Since we need to process the most recent unmatched element first, a Stack is appropriate."
    **識別 LIFO 特性：** 「由於我們需要優先處理最近未匹配的元素，因此使用 Stack 是合適的。」
2.  **Define the Invariant:** "I will maintain a monotonic decreasing stack, meaning elements in the stack are always waiting for a larger element."
    **定義不變性：** 「我將維護一個單調遞減棧，這意味著棧中的元素總是在等待一個更大的元素。」
3.  **Discuss Complexity early:** "A brute force approach is $O(N^2)$. Using a stack allows us to process each element exactly twice (push/pop), reducing it to $O(N)$."
    **儘早討論複雜度：** 「暴力解法是 $O(N^2)$。使用 Stack 讓我們能精確地處理每個元素兩次（推入/彈出），將其降至 $O(N)$。」

### Whiteboard Strategy (白板策略)
*   Draw the stack vertically or horizontally on the side.
    在旁邊垂直或水平地畫出 Stack。
*   Trace the loop: `Index | Value | Stack State | Answer Array`.
    追蹤迴圈：`索引 | 數值 | Stack 狀態 | 答案陣列`。
*   This visualizes the "waiting" process clearly for the interviewer.
    這能為面試官清晰地視覺化「等待」的過程。

### Common Follow-ups (常見追問)
*   **Q:** What if the array is circular? (The last element considers the first element as "next").
    **問：** 如果陣列是循環的怎麼辦？（最後一個元素將第一個元素視為「下一個」）。
    *   *A:* Iterate through the array twice (simulate concatenation) or use modulo operator `%`.
    *   *答：* 遍歷陣列兩次（模擬串接）或使用取餘運算子 `%`。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** Valid Parentheses (LeetCode 20)
**Hint:** Use a hash map to match closing brackets to opening ones. Push openers, pop and check closers.
**提示：** 使用雜湊表將右括號與左括號配對。推入左括號，彈出並檢查右括號。

### Level: Medium (Must Do)
**Problem:** Evaluate Reverse Polish Notation (LeetCode 150)
**Hint:** Iterate through tokens. If number, push to stack. If operator, pop top two numbers, calculate, and push result back.
**提示：** 遍歷標記。如果是數字，推入 Stack。如果是運算子，彈出頂端兩個數字，計算後將結果推回。

### Level: Hard (Differentiation)
**Problem:** Largest Rectangle in Histogram (LeetCode 84)
**Hint:** This is the ultimate Monotonic Stack problem. Maintain increasing heights. When a smaller bar comes, calculate areas for all taller bars in the stack because their right boundary is determined.
**提示：** 這是終極的單調棧問題。維護遞增的高度。當遇到較矮的柱子時，計算 Stack 中所有較高柱子的面積，因為它們的右邊界已經確定了。

---

## 8. Quick Checklists (快速檢核表)

Before submitting code, check these:
提交程式碼前，請檢查以下幾點：

- [ ] **Empty Check:** Did I handle the case where `stack` is empty before calling `pop()` or `peek()`?
  **空檢查：** 在呼叫 `pop()` 或 `peek()` 之前，我是否處理了 `stack` 為空的情況？
- [ ] **Leftovers:** After the loop finishes, does the stack still contain elements? (e.g., in Daily Temperatures, these stay 0).
  **剩餘元素：** 迴圈結束後，Stack 中是否還有元素？（例如在每日溫度中，這些保持為 0）。
- [ ] **Type Consistency:** Am I storing indices, values, or objects? Be consistent.
  **型別一致性：** 我存的是索引、數值還是物件？保持一致。
- [ ] **Complexity:** Is there any hidden loop inside the `while` loop that breaks $O(N)$? (e.g., slicing a list).
  **複雜度：** `while` 迴圈內是否有隱藏的迴圈破壞了 $O(N)$？（例如切片列表）。

---

## 9. Memory Anchors (記憶錨點)

**Visual Analogy: The "Pending Tray"**
**視覺類比：「待辦公文匣」**

*   Imagine a tray on your desk. You put tasks (elements) in it.
    想像桌上有一個公文匣。你把任務（元素）放進去。
*   **Monotonic Stack:** You can only process a task if the new task coming in is *more urgent* (larger). If a super urgent task comes, you clear out the smaller pending tasks immediately.
    **單調棧：** 只有當新進來的任務*更緊急*（數值更大）時，你才能處理舊任務。如果一個超級緊急的任務來了，你會立即清空那些較小的待辦任務。
*   **Indices:** Remember to write the "Time Received" (Index) on the task, not just the "Urgency Level" (Value), so you know how long it waited.
    **索引：** 記得在任務上寫下「接收時間」（索引），而不僅僅是「緊急程度」（數值），這樣你才知道它等了多久。