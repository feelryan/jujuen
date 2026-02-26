# Advanced Data Structures: Stack (堆疊)

## 1. Learning Goals (學習目標)

*   **Master Monotonic Stacks:** Understand how to solve "Next Greater/Smaller Element" problems in $O(N)$ time.
    **掌握單調堆疊（Monotonic Stack）：** 理解如何在 $O(N)$ 時間內解決「下一個更大/更小元素」類型的問題。
*   **Handle Complex Parsing:** Learn to use multiple stacks or recursion simulation for expression evaluation (calculators) and nested structure parsing.
    **處理複雜解析：** 學習使用多個堆疊或遞迴模擬來處理表達式評估（計算機）與巢狀結構解析。
*   **Optimize Space Complexity:** Identify scenarios where stacks can replace recursion to prevent Stack Overflow or optimize memory usage.
    **優化空間複雜度：** 識別可以使用堆疊取代遞迴的場景，以防止堆疊溢位（Stack Overflow）或優化記憶體使用。
*   **Amortized Analysis:** Be able to prove why a monotonic stack solution is $O(N)$ despite having nested loops.
    **攤提分析（Amortized Analysis）：** 能夠證明為何單調堆疊解法即使有巢狀迴圈，其複雜度仍為 $O(N)$。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
While a basic stack is LIFO (Last-In, First-Out), an **Advanced Stack** usage often involves maintaining a specific **invariant** (property) within the stack elements.
雖然基礎堆疊是後進先出（LIFO），但 **進階堆疊** 的使用通常涉及在堆疊元素中維護一個特定的 **不變性（invariant）**。

The most critical advanced concept is the **Monotonic Stack**, where elements are kept in increasing or decreasing order.
最關鍵的進階概念是 **單調堆疊（Monotonic Stack）**，其中元素保持遞增或遞減的順序。

### Complexity (複雜度)
*   **Time:** $O(1)$ for push/pop. For monotonic stacks, total time is $O(N)$ because each element is pushed and popped at most once.
    **時間：** 推入/彈出為 $O(1)$。對於單調堆疊，總時間為 $O(N)$，因為每個元素最多被推入和彈出一次。
*   **Space:** $O(N)$ in the worst case.
    **空間：** 最差情況下為 $O(N)$。

### When to Use (適用場景)
*   Finding the nearest greater/smaller element to the left/right.
    尋找左側或右側最近的更大/更小元素。
*   Parsing expressions with operator precedence (e.g., `3 * (2 + 4)`).
    解析具有運算符優先級的表達式（例如 `3 * (2 + 4)`）。
*   "Largest Rectangle" or "Water Trapping" type problems.
    「最大矩形」或「接雨水」類型的問題。

### When NOT to Use (不適用場景)
*   When random access to elements is required (use Array/Hash Map).
    當需要隨機存取元素時（請使用陣列/雜湊表）。
*   When simple queue behavior (FIFO) is needed (use Queue/Deque).
    當需要簡單的佇列行為（FIFO）時（請使用 Queue/Deque）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Monotonic Stack (單調堆疊)
Used to find the **Next Greater Element (NGE)** or **Previous Smaller Element (PSE)**.
用於尋找 **下一個更大元素（NGE）** 或 **上一個更小元素（PSE）**。
*   **Increasing Stack:** Keeps smaller elements; used to find the *next smaller* element.
    **遞增堆疊：** 保留較小元素；用於尋找 *下一個更小* 的元素。
*   **Decreasing Stack:** Keeps larger elements; used to find the *next greater* element.
    **遞減堆疊：** 保留較大元素；用於尋找 *下一個更大* 的元素。

### Pattern B: Parenthesis & Expression Parsing (括號與表達式解析)
Handling nested structures or mathematical precedence.
處理巢狀結構或數學優先級。
*   Often involves two stacks (one for numbers, one for operators) or a single stack converting infix to postfix (RPN).
    通常涉及兩個堆疊（一個存數字，一個存運算符）或單一堆疊將中序轉為後序（RPN）。

### Pattern C: Coordinate Geometry with Stack (幾何堆疊)
Problems involving histograms or grids where the stack stores indices to calculate areas based on width and height.
涉及直方圖或網格的問題，堆疊儲存索引以根據寬度和高度計算面積。

---

## 4. Example Walkthrough (範例講解)

### Problem: Largest Rectangle in Histogram (直方圖中的最大矩形)
*LeetCode 84 (Hard)*

#### Problem Statement (問題重述)
Given an array of integers `heights` representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
給定一個整數陣列 `heights` 代表直方圖的長條高度，其中每個長條的寬度為 1，請回傳直方圖中最大矩形的面積。

#### Thought Process (思路)

**1. Brute Force (暴力解):**
Iterate through every pair of bars `(i, j)`, find the minimum height between them, and calculate area.
遍歷每一對長條 `(i, j)`，找出它們之間的最小高度，並計算面積。
*   Complexity: $O(N^3)$ or $O(N^2)$ with optimization. Too slow for $N=10^5$.
    複雜度：$O(N^3)$ 或優化後 $O(N^2)$。對於 $N=10^5$ 來說太慢。

**2. Optimization Intuition (優化直覺):**
For any bar `i` with height `h`, if we treat `h` as the height of the rectangle, we need to find how far we can extend to the left and right without encountering a bar shorter than `h`.
對於任何高度為 `h` 的長條 `i`，如果我們將 `h` 視為矩形的高度，我們需要找出在不遇到比 `h` 短的長條的情況下，可以向左和向右延伸多遠。
*   We need the index of the **First Smaller Element** on the left and right.
    我們需要左側和右側 **第一個更小元素** 的索引。

**3. Optimal Solution: Monotonic Stack (最佳解：單調堆疊):**
We maintain a stack of indices with **increasing heights**.
我們維護一個索引堆疊，其對應的高度是 **遞增的**。
*   When we encounter a current bar `h` that is **smaller** than the bar at the stack top, it means the rectangle defined by the stack top cannot extend further right.
    當我們遇到當前長條 `h` 比堆疊頂部的長條 **更小** 時，這意味著由堆疊頂部定義的矩形無法再向右延伸。
*   We pop the stack top, calculate its area, and treat the current `i` as the right boundary.
    我們彈出堆疊頂部，計算其面積，並將當前 `i` 視為右邊界。

#### Python Reference Solution (Python 參考解)

```python
from typing import List

def largestRectangleArea(heights: List[int]) -> int:
    # Append a 0 to the end to ensure all elements in stack are popped eventually
    # 在末尾添加一個 0，以確保堆疊中的所有元素最終都會被彈出
    heights.append(0)
    stack = [-1] # Sentinel value to handle the left boundary / 哨兵值，用於處理左邊界
    max_area = 0
    
    for i, h in enumerate(heights):
        # Maintain a monotonic increasing stack
        # If current height is less than stack top height, we found a right boundary
        # 維護單調遞增堆疊
        # 如果當前高度小於堆疊頂部高度，我們找到了右邊界
        while stack[-1] != -1 and heights[stack[-1]] >= h:
            current_height = heights[stack.pop()]
            current_width = i - stack[-1] - 1
            max_area = max(max_area, current_height * current_width)
            
        stack.append(i)
    
    return max_area

# Example Usage / 範例用法
# heights = [2, 1, 5, 6, 2, 3]
# Result: 10 (from bars 5 and 6)
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Each element is pushed once and popped once.
    **時間：** $O(N)$。每個元素被推入一次且彈出一次。
*   **Space:** $O(N)$. The stack can grow up to size N.
    **空間：** $O(N)$。堆疊大小最多可達 N。

#### Common Mistakes (錯誤示範)
*   **Mistake:** Forgetting to clear the stack at the end.
    **錯誤：** 忘記在最後清空堆疊。
    *   *Fix:* Append `0` to `heights` or add a loop after the main loop to process remaining items.
    *   *修正：* 在 `heights` 末尾添加 `0`，或在主迴圈後添加一個迴圈來處理剩餘項目。
*   **Mistake:** Calculating width incorrectly as `i - index`.
    **錯誤：** 錯誤地將寬度計算為 `i - index`。
    *   *Fix:* Width is `Right Boundary - Left Boundary - 1`. Left boundary is the *new* top after pop.
    *   *修正：* 寬度應為 `右邊界 - 左邊界 - 1`。左邊界是彈出後的 *新* 堆疊頂部。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description (描述) | Common Pitfall (常見陷阱) |
| :--- | :--- | :--- |
| **Monotonicity Direction** | Increasing vs. Decreasing stack. <br> 遞增 vs. 遞減堆疊。 | Confusing which one finds the "Next Greater" vs "Next Smaller". <br> 混淆哪一個是用來找「下一個更大」或「下一個更小」。 |
| **Index vs. Value** | Storing indices vs. actual values in stack. <br> 在堆疊中儲存索引 vs. 實際值。 | Usually, store **indices** so you can calculate width/distance. <br> 通常應儲存 **索引**，以便計算寬度/距離。 |
| **Strict vs. Non-Strict** | Handling duplicate values (`>=` vs `>`). <br> 處理重複值（`>=` vs `>`）。 | In Histogram, popping on equal height is safe, but in other problems (e.g., sum of subarray minimums), strictness matters to avoid double counting. <br> 在直方圖題中，高度相等時彈出是安全的，但在其他問題（如子陣列最小值總和）中，嚴格性對於避免重複計算很重要。 |
| **Sentinel Values** | Dummy values at start/end (e.g., -1, 0, infinity). <br> 起始/結束處的虛擬值（如 -1, 0, 無窮大）。 | Forgetting them leads to complex `if stack is empty` checks inside the loop. <br> 忘記使用它們會導致迴圈內需要複雜的 `if stack is empty` 檢查。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (闡述口條框架)
1.  **Identify the bottleneck:** "A brute force approach would take $O(N^2)$ because for each element, we scan its neighbors..."
    **識別瓶頸：** 「暴力解法需要 $O(N^2)$，因為對於每個元素，我們都要掃描其鄰居……」
2.  **Propose Stack:** "Since we are looking for the *first* element that breaks a pattern (next smaller/greater), a Monotonic Stack is ideal here."
    **提出堆疊：** 「由於我們正在尋找 *第一個* 打破模式（下一個更小/更大）的元素，單調堆疊在這裡非常理想。」
3.  **Define Invariant:** "I will maintain a stack of indices where the corresponding values are strictly increasing."
    **定義不變性：** 「我將維護一個索引堆疊，其對應的值是嚴格遞增的。」

### Whiteboard Strategy (白板策略)
*   **Trace with a small example:** Draw the stack vertically on the side. Show elements entering and leaving.
    **用小範例追蹤：** 在旁邊垂直畫出堆疊。展示元素的進入和離開。
*   **Variable Naming:** Use `stack`, `current_val`, `top_index` clearly. Don't use single letters like `s`, `x`, `t`.
    **變數命名：** 清楚使用 `stack`, `current_val`, `top_index`。不要使用 `s`, `x`, `t` 等單字母。

### Common Follow-ups (常見追問)
*   "What if the input is a stream (infinite)?" (Hint: You might need to limit stack depth or process in chunks).
    「如果輸入是串流（無限的）怎麼辦？」（提示：可能需要限制堆疊深度或分塊處理）。
*   "Can we solve this without extra space?" (Usually no for $O(N)$ time, but sometimes Morris Traversal applies for trees).
    「我們可以在不使用額外空間的情況下解決這個問題嗎？」（通常對於 $O(N)$ 時間來說不行，但有時 Morris Traversal 適用於樹）。

---

## 7. Practice Problems (練習題)

### 1. Easy/Warm-up: Daily Temperatures (每日溫度)
*LeetCode 739*
*   **Prompt:** Return an array showing how many days you have to wait for a warmer temperature.
    **題目：** 回傳一個陣列，顯示需要等待多少天才能等到更溫暖的氣溫。
*   **Hint:** Monotonic Decreasing Stack. Store indices.
    **提示：** 單調遞減堆疊。儲存索引。
*   **Key:** `stack[-1]` is the index of the previous day that hasn't found a warmer day yet.
    **關鍵：** `stack[-1]` 是尚未找到更暖日子的前一天的索引。

### 2. Intermediate: Basic Calculator II (基本計算機 II)
*LeetCode 227*
*   **Prompt:** Evaluate string "3+2*2". No parentheses, but `*` `/` have precedence over `+` `-`.
    **題目：** 評估字串 "3+2*2"。沒有括號，但 `*` `/` 的優先級高於 `+` `-`。
*   **Hint:** Use a stack to store numbers. For `+` push `num`, for `-` push `-num`. For `*` pop, multiply, push back. Sum the stack at the end.
    **提示：** 使用堆疊儲存數字。遇到 `+` 推入 `num`，遇到 `-` 推入 `-num`。遇到 `*` 彈出，相乘，再推回。最後將堆疊求和。

### 3. Advanced: Maximal Rectangle (最大矩形)
*LeetCode 85*
*   **Prompt:** Given a 2D binary matrix, find the largest rectangle containing only 1s.
    **題目：** 給定一個二維二進位矩陣，找出只包含 1 的最大矩形。
*   **Hint:** This is "Largest Rectangle in Histogram" applied to each row.
    **提示：** 這是應用於每一列的「直方圖中的最大矩形」。
*   **Strategy:** Accumulate heights row by row. If `matrix[i][j] == 0`, height resets to 0. Run the histogram algorithm for each row.
    **策略：** 逐列累積高度。如果 `matrix[i][j] == 0`，高度重置為 0。對每一列執行直方圖演算法。

---

## 8. Checklists (快速檢核表)

*   [ ] **Empty Stack Check:** Did I check `if stack:` before calling `stack.pop()` or `stack[-1]`?
    **空堆疊檢查：** 在呼叫 `stack.pop()` 或 `stack[-1]` 之前，我是否檢查了 `if stack:`？
*   [ ] **Sentinel Value:** Did I consider adding a dummy element (0 or -1) to flush the stack at the end?
    **哨兵值：** 我是否考慮添加虛擬元素（0 或 -1）以便在最後清空堆疊？
*   [ ] **Index vs Value:** Am I pushing the correct data type (index vs value)?
    **索引 vs 值：** 我推入的資料類型正確嗎（索引 vs 值）？
*   [ ] **Complexity Proof:** Can I explain why the `while` loop inside the `for` loop doesn't make it $O(N^2)$? (Amortized analysis).
    **複雜度證明：** 我能解釋為什麼 `for` 迴圈內的 `while` 迴圈不會使其變成 $O(N^2)$ 嗎？（攤提分析）。

---

## 9. Memory Anchors (記憶錨點與類比)

*   **The "Mountain View" (山景):**
    Imagine looking from right to left. You can only see the mountains (elements) that are higher than the ones in front of them. The blocked mountains are "popped". This visualizes the Monotonic Stack.
    想像從右向左看。你只能看到比前面的山（元素）更高的山。被擋住的山就被「彈出」了。這具象化了單調堆疊。

*   **The "Telescope" (望遠鏡):**
    A monotonic stack collapses a range of "useless" smaller data points into a single "next greater" relationship, just like a telescope collapses distance.
    單調堆疊將一系列「無用」的較小數據點摺疊成單一的「下一個更大」關係，就像望遠鏡摺疊距離一樣。