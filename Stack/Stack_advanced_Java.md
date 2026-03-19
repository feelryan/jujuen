Here is the advanced guide for **Stack**, tailored for a Senior Software Engineer, following your specified structure and bilingual format.

***

# Advanced Data Structures: Stack (堆疊)

## 1. Learning Goals (學習目標)

*   **Master Monotonic Stacks:** Understand how to solve "Next Greater Element" and "Histogram Area" problems in $O(N)$ time.
    **掌握單調堆疊（Monotonic Stack）：** 理解如何在 $O(N)$ 時間內解決「下一個更大元素」與「直方圖面積」類問題。
*   **Recursion to Iteration:** Learn to convert recursive DFS algorithms into iterative solutions using an explicit stack to avoid stack overflow.
    **遞迴轉迭代：** 學習如何使用顯式堆疊將遞迴 DFS 演算法轉換為迭代解法，以避免堆疊溢位。
*   **Parsing & Expression Evaluation:** Handle complex nested structures (like calculators or JSON parsers) proficiently.
    **解析與表達式求值：** 熟練處理複雜的巢狀結構（如計算機或 JSON 解析器）。
*   **Amortized Complexity Analysis:** Articulate why a monotonic stack is linear time despite nested loops.
    **攤銷複雜度分析：** 能夠清楚闡述為何單調堆疊儘管有巢狀迴圈，其時間複雜度仍為線性。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A linear data structure that follows the LIFO (Last In, First Out) principle.
一種遵循 LIFO（後進先出）原則的線性資料結構。

### Intuition (直覺)
Think of a stack of plates or the "Undo" button in a text editor.
想像一疊盤子，或是文字編輯器中的「復原」按鈕。
It is the natural data structure for processing nested hierarchies or reverting to a previous state.
它是處理巢狀層級或回復到先前狀態最自然的資料結構。

### Complexity (複雜度)
*   **Push/Pop/Peek:** $O(1)$
*   **Search:** $O(N)$
*   **Space:** $O(N)$

### When to Use (適用場景)
*   **Matching/Pairing:** Valid parentheses, HTML tags.
    **配對/匹配：** 有效括號、HTML 標籤。
*   **Reverse Processing:** Reversing a string, processing history.
    **反向處理：** 反轉字串、處理歷史紀錄。
*   **Monotonicity:** Finding the nearest larger/smaller element.
    **單調性：** 尋找最近的較大/較小元素。
*   **DFS/Backtracking:** Managing state in graph traversals.
    **深度優先搜尋/回溯：** 管理圖形遍歷中的狀態。

### When NOT to Use (不適用場景)
*   **Random Access:** If you need to access the $k$-th element frequently, use an `ArrayList`.
    **隨機存取：** 如果你需要頻繁存取第 $k$ 個元素，請使用 `ArrayList`。
*   **FIFO Requirements:** If order needs to be preserved (First In, First Out), use a `Queue`.
    **先進先出需求：** 如果需要保留順序（先進先出），請使用 `Queue`。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Monotonic Stack (單調堆疊)
Maintains elements in increasing or decreasing order.
維持元素處於遞增或遞減的順序。
Used for finding the "Next Greater Element" or spanning ranges (e.g., stock spans, histograms).
用於尋找「下一個更大元素」或跨度範圍（例如：股票跨度、直方圖）。

### B. Parentheses & Parsing (括號與解析)
Handles nested logic. When you encounter an opening bracket, push; when closing, pop and process.
處理巢狀邏輯。遇到左括號時推入；遇到右括號時彈出並處理。
Examples: Valid Parentheses, Basic Calculator.
範例：有效括號、基本計算機。

### C. Iterative DFS (迭代 DFS)
Simulates the system call stack to traverse trees or graphs without recursion.
模擬系統呼叫堆疊，在不使用遞迴的情況下遍歷樹或圖。

---

## 4. Example Walkthrough (範例講解)

### Problem: Largest Rectangle in Histogram (直方圖中最大的矩形)
*LeetCode 84 (Hard)*

#### Problem Restatement (問題重述)
Given an array of integers `heights` representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
給定一個整數陣列 `heights` 代表直方圖的柱狀高度（每個柱寬為 1），請回傳直方圖中最大矩形的面積。

#### Approach 1: Brute Force (暴力法)
For each pair of bars $(i, j)$, find the minimum height between them and calculate area.
對於每一對柱子 $(i, j)$，找出它們之間的最小高度並計算面積。
*   **Complexity:** $O(N^3)$ or $O(N^2)$ depending on implementation.
*   **Verdict:** TLE (Time Limit Exceeded).

#### Approach 2: Optimized with Monotonic Stack (最佳解)
We need to find the **left boundary** and **right boundary** for each bar where it serves as the height bottleneck.
我們需要為每一根柱子找出它作為「高度瓶頸」時的**左邊界**與**右邊界**。
Specifically, for a bar at index $i$, we want the first index to the left smaller than $h[i]$ and the first index to the right smaller than $h[i]$.
具體來說，對於索引 $i$ 的柱子，我們要找左邊第一個小於 $h[i]$ 的索引，以及右邊第一個小於 $h[i]$ 的索引。

We maintain a stack of indices with **increasing heights**.
我們維護一個儲存索引的堆疊，且對應的高度是**遞增的**。
When we see a bar $h[current]$ lower than the stack top $h[top]$, it means the bar at $top$ cannot extend further right.
當我們看到一個柱子 $h[current]$ 低於堆疊頂端 $h[top]$ 時，這意味著 $top$ 處的柱子無法再向右延伸。
We pop $top$ and calculate its area.
我們彈出 $top$ 並計算其面積。

*   Height: $h[top]$
*   Right Boundary: $current - 1$
*   Left Boundary: $peek() + 1$ (the new top after popping)
*   Width: $(current - 1) - (peek() + 1) + 1 = current - peek() - 1$

#### Java Reference Solution (Java 參考解)

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class LargestRectangle {
    public int largestRectangleArea(int[] heights) {
        // Use Deque as Stack. ArrayDeque is faster than java.util.Stack
        // 使用 Deque 作為 Stack。ArrayDeque 比 java.util.Stack 更快
        Deque<Integer> stack = new ArrayDeque<>();
        
        // Add a sentinel -1 to handle the start boundary conveniently
        // 加入哨兵值 -1 以方便處理起始邊界
        stack.push(-1);
        
        int maxArea = 0;
        int n = heights.length;
        
        for (int i = 0; i < n; i++) {
            // While current bar is lower than the bar at stack top,
            // it means the rectangle with height heights[stack.peek()] ends at i.
            // 當前柱子低於堆疊頂端的柱子時，
            // 代表以 heights[stack.peek()] 為高度的矩形在 i 處結束。
            while (stack.peek() != -1 && heights[stack.peek()] >= heights[i]) {
                int currentHeight = heights[stack.pop()];
                int currentWidth = i - stack.peek() - 1;
                maxArea = Math.max(maxArea, currentHeight * currentWidth);
            }
            stack.push(i);
        }
        
        // Process remaining bars in the stack
        // 處理堆疊中剩餘的柱子
        while (stack.peek() != -1) {
            int currentHeight = heights[stack.pop()];
            int currentWidth = n - stack.peek() - 1;
            maxArea = Math.max(maxArea, currentHeight * currentWidth);
        }
        
        return maxArea;
    }
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Each element is pushed once and popped once.
    **時間：** $O(N)$。每個元素被推入一次且彈出一次。
*   **Space:** $O(N)$. In the worst case (sorted ascending), the stack holds all elements.
    **空間：** $O(N)$。在最壞情況下（遞增排序），堆疊保存所有元素。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **`Stack` vs `Deque`** | **Avoid `java.util.Stack`.** It extends `Vector` and is synchronized (slow). Use `ArrayDeque` or `LinkedList`. <br> **避免使用 `java.util.Stack`。** 它繼承自 `Vector` 且是同步的（較慢）。請使用 `ArrayDeque` 或 `LinkedList`。 |
| **Amortized Analysis** | Don't confuse the `while` loop inside the `for` loop as $O(N^2)$. Since each item is processed at most twice (push/pop), it is $O(N)$. <br> **不要將 `for` 迴圈內的 `while` 誤認為 $O(N^2)$。** 因為每個項目最多被處理兩次（推入/彈出），所以是 $O(N)$。 |
| **Boundary Conditions** | Forgetting to handle elements left in the stack after the loop finishes. <br> **忘記處理迴圈結束後仍留在堆疊中的元素。** |
| **Storing Index vs Value** | In Monotonic Stacks, usually store **indices**, not values, to calculate width. <br> **在單調堆疊中，通常儲存「索引」而非數值，以便計算寬度。** |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the LIFO nature:** "Since we need to process the most recently seen element first to determine the range/validity, a Stack is appropriate."
    **識別 LIFO 特性：** 「由於我們需要先處理最近看到的元素來決定範圍/有效性，因此堆疊是合適的。」
2.  **Justify Monotonicity:** "To find the *next* greater element efficiently, we can maintain a decreasing stack..."
    **證成單調性：** 「為了有效率地找到*下一個*較大元素，我們可以維護一個遞減堆疊...」

### Whiteboard Strategy (白板策略)
*   **Trace with a Table:** Draw columns for `Index`, `Value`, `Stack State`, and `Result`.
    **用表格追蹤：** 畫出 `Index`、`Value`、`Stack State` 和 `Result` 欄位。
*   **Visual Stack:** Draw the stack vertically to avoid confusion with the array.
    **視覺化堆疊：** 垂直畫出堆疊，以避免與陣列混淆。

### Common Follow-ups (常見追問)
*   "Can you do this with $O(1)$ space?" (Usually implies modifying the input array or using Two Pointers if applicable).
    「你能用 $O(1)$ 空間做到嗎？」（通常暗示修改輸入陣列或在適用時使用雙指標）。
*   "What if the data comes as a stream?" (Requires maintaining stack state between calls).
    「如果資料是以串流形式進來呢？」（需要在呼叫之間維護堆疊狀態）。

---

## 7. Practice Problems (練習題)

### Easy: Valid Parentheses (有效括號)
*   **Goal:** Check if string has valid matching brackets `()[]{}`.
*   **Hint:** Map closing brackets to opening ones. Push opening, pop and check matching on closing.
*   **提示：** 將右括號映射到左括號。推入左括號，遇到右括號時彈出並檢查是否匹配。

### Medium: Daily Temperatures (每日溫度)
*   **Goal:** For each day, find how many days until a warmer temperature.
*   **Hint:** Monotonic decreasing stack storing indices. When current temp > stack top, pop and calculate distance.
*   **提示：** 儲存索引的單調遞減堆疊。當前溫度 > 堆疊頂端時，彈出並計算距離。

### Hard: Basic Calculator (基本計算機)
*   **Goal:** Evaluate string with `+`, `-`, `(`, `)`.
*   **Hint:** Use a stack to store `result` and `sign` before entering a parenthesis. Handle numbers digit by digit.
*   **提示：** 進入括號前，使用堆疊儲存當前的 `result` 和 `sign`。逐位處理數字。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Class Choice:** Did I use `Deque<Integer> stack = new ArrayDeque<>();`?
    **類別選擇：** 我是否使用了 `Deque<Integer> stack = new ArrayDeque<>();`？
*   [ ] **Empty Check:** Do I check `!stack.isEmpty()` before calling `pop()` or `peek()`?
    **空堆疊檢查：** 我在呼叫 `pop()` 或 `peek()` 之前是否檢查了 `!stack.isEmpty()`？
*   [ ] **Leftovers:** Did I process elements remaining in the stack after the main loop?
    **剩餘元素：** 我是否處理了主迴圈結束後堆疊中剩餘的元素？
*   [ ] **Type Safety:** Am I pushing indices (int) or values? (Indices are usually more versatile).
    **型別安全：** 我推入的是索引（int）還是數值？（索引通常更通用）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Cafeteria Tray" (自助餐廳托盤):**
    You can only take the top tray. If you want the one at the bottom, you must remove all above it.
    你只能拿最上面的托盤。如果你想要底部的，必須移除上面的所有托盤。

*   **The "Mountain Range" (Monotonic Stack) (山脈/單調堆疊):**
    Imagine looking from right to left. A high mountain blocks the view of smaller hills behind it. The visible peaks form a monotonic sequence.
    想像從右向左看。一座高山會擋住後面較小山丘的視線。可見的山峰形成一個單調序列。

*   **Recursion is a Stack (遞迴即堆疊):**
    Every time you call a function, you push a "todo note" onto a pile. When you return, you pop the note and continue.
    每次呼叫函式，就像往堆疊上放一張「待辦便條」。當你回傳時，你彈出便條並繼續執行。