Here is the comprehensive guide for **Stack (Intermediate)**, tailored for a Senior Software Engineer using Java.
這是一份針對使用 Java 的資深軟體工程師量身打造的 **Stack (堆疊/棧) 中階** 完整教材。

---

# Module: Stack (Intermediate / 中階)

## 1. Learning Objectives (學習目標)

*   **Master the Monotonic Stack Pattern:** Understand how to solve "Next Greater Element" type problems in $O(N)$ time.
    **掌握單調堆疊（Monotonic Stack）模式：** 理解如何在 $O(N)$ 時間內解決「下一個更大元素」類型的問題。
*   **Handle Nested Structures & Parsing:** Use stacks to manage parentheses, expression evaluation, and recursive structures effectively.
    **處理巢狀結構與解析：** 有效使用堆疊來管理括號、表達式評估以及遞迴結構。
*   **Java Best Practices:** Transition from the legacy `Stack` class to `Deque`/`ArrayDeque` for production-grade code.
    **Java 最佳實踐：** 從過時的 `Stack` 類別轉向 `Deque`/`ArrayDeque` 以撰寫生產級程式碼。
*   **Amortized Complexity Analysis:** Articulate why nested loops in stack problems often result in linear time, not quadratic.
    **攤銷複雜度分析：** 清楚闡述為何堆疊問題中的巢狀迴圈通常導致線性時間，而非平方時間。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)
*   **LIFO (Last-In, First-Out):** The last element added is the first one removed. Think of a stack of dinner plates; you wash the top one first.
    **後進先出 (LIFO)：** 最後加入的元素最先被移除。想像一疊餐盤；你會先洗最上面的那一個。
*   **Logical Usage:** It represents a "pending state" or "history" that needs to be resolved in reverse order.
    **邏輯用途：** 它代表一種「待處理狀態」或「歷史記錄」，需要以相反的順序來解決。

### Complexity (複雜度)
*   **Push (Add):** $O(1)$
*   **Pop (Remove):** $O(1)$
*   **Peek (Top):** $O(1)$
*   **Search:** $O(N)$ (Not designed for random access / 非設計用於隨機存取)

### When to Use (適用場景)
*   **Parsing/Matching:** Valid parentheses, HTML tags, JSON parsing.
    **解析/配對：** 有效括號、HTML 標籤、JSON 解析。
*   **Monotonic Relationships:** Finding the next greater/smaller element in an array.
    **單調關係：** 尋找陣列中下一個更大或更小的元素。
*   **DFS/Recursion Simulation:** Converting recursive algorithms to iterative ones to avoid stack overflow.
    **DFS/遞迴模擬：** 將遞迴演算法轉換為迭代算法以避免堆疊溢位。

### When NOT to Use (不適用場景)
*   **Random Access Needed:** If you need to access the $k$-th element frequently, use an `ArrayList`.
    **需要隨機存取：** 如果你需要頻繁存取第 $k$ 個元素，請使用 `ArrayList`。
*   **FIFO Requirements:** If order needs to be preserved (First-In, First-Out), use a `Queue`.
    **先進先出需求：** 如果需要保留順序（先進先出），請使用 `Queue`。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Matching / Pairing (配對模式):**
    *   Used for validating balanced strings (e.g., `(([]))`).
    *   用於驗證平衡字串（例如 `(([]))`）。
2.  **Monotonic Stack (單調堆疊):**
    *   Maintains elements in increasing or decreasing order. Used for "Next Greater Element" or "Largest Rectangle".
    *   維持元素遞增或遞減的順序。用於「下一個更大元素」或「最大矩形」。
3.  **String Decoding / Calculator (字串解碼 / 計算機):**
    *   Handling operator precedence or nested instructions (e.g., `3[a2[c]]`).
    *   處理運算符優先級或巢狀指令（例如 `3[a2[c]]`）。
4.  **Min/Max Stack (最小/最大堆疊):**
    *   Designing a stack that supports `getMin()` in $O(1)$ using an auxiliary stack.
    *   利用輔助堆疊設計一個支援 $O(1)$ 時間 `getMin()` 的堆疊。

---

## 4. Example Walkthrough (範例講解)

### Problem: Daily Temperatures (LeetCode 739)
**問題：每日溫度**

#### Problem Statement (問題重述)
Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0`.
給定一個整數陣列 `temperatures` 代表每日溫度，回傳一個陣列 `answer`，其中 `answer[i]` 是在第 `i` 天之後，需要等待多少天才能獲得更溫暖的溫度。如果未來沒有這一天，則保持 `answer[i] == 0`。

#### Approach 1: Brute Force (暴力解)
*   **Idea:** For each day, scan all subsequent days until a warmer one is found.
    **思路：** 對於每一天，掃描隨後的所有天數，直到找到更溫暖的一天。
*   **Complexity:** Time $O(N^2)$, Space $O(1)$.
    **複雜度：** 時間 $O(N^2)$，空間 $O(1)$。
*   **Why it's bad:** If temperatures are decreasing (e.g., `[99, 98, ..., 1]`), we scan the rest of the array for every element.
    **缺點：** 如果溫度是遞減的（例如 `[99, 98, ..., 1]`），我們對每個元素都要掃描剩餘的陣列。

#### Approach 2: Monotonic Decreasing Stack (Optimal) (最佳解：單調遞減堆疊)
*   **Idea:** We maintain a stack of indices representing days that haven't found a warmer day yet. The temperatures corresponding to these indices should be in decreasing order.
    **思路：** 我們維護一個索引堆疊，代表尚未找到更暖日子的天數。這些索引對應的溫度應該是遞減順序。
*   **Logic:** When we see a current temperature $T_{curr}$ that is warmer than the temperature at the top of the stack $T_{top}$, it means $T_{curr}$ is the "next greater element" for $T_{top}$. We pop the stack and calculate the distance.
    **邏輯：** 當我們看到當前溫度 $T_{curr}$ 比堆疊頂端的溫度 $T_{top}$ 更暖時，意味著 $T_{curr}$ 是 $T_{top}$ 的「下一個更大元素」。我們將堆疊頂端彈出並計算距離。

#### Java Solution (Reference)

```java
import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int[] dailyTemperatures(int[] temperatures) {
        int n = temperatures.length;
        int[] result = new int[n]; // Default is 0 / 預設值為 0

        // Use Deque as Stack. 'Stack' class is legacy in Java.
        // 使用 Deque 作為堆疊。Java 中的 'Stack' 類別已過時。
        Deque<Integer> stack = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            int currentTemp = temperatures[i];

            // While stack is not empty and current temp is warmer than the temp at stack top
            // 當堆疊不為空且當前溫度比堆疊頂端的溫度更暖時
            while (!stack.isEmpty() && currentTemp > temperatures[stack.peek()]) {
                
                int prevDayIndex = stack.pop();
                
                // Calculate the wait days
                // 計算等待天數
                result[prevDayIndex] = i - prevDayIndex;
            }

            // Push current index to stack (it's now a pending day)
            // 將當前索引推入堆疊（它現在是一個待處理的日子）
            stack.push(i);
        }

        return result;
    }
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Although there is a `while` loop inside the `for` loop, each element is pushed once and popped at most once. This is **amortized $O(1)$** per element.
    **時間：** $O(N)$。雖然 `for` 迴圈內有一個 `while` 迴圈，但每個元素只會被推入一次，且最多被彈出一次。這對每個元素來說是 **攤銷 $O(1)$**。
*   **Space:** $O(N)$ for the stack in the worst case (strictly decreasing input).
    **空間：** 最壞情況下（嚴格遞減輸入）堆疊需要 $O(N)$。

#### Common Mistake (錯誤示範)
*   **Storing Values instead of Indices:** If you store the temperature value (e.g., `73`) in the stack, you lose the information about *when* that temperature occurred, making it impossible to calculate the distance.
    **存儲數值而非索引：** 如果你在堆疊中存儲溫度值（例如 `73`），你會丟失該溫度發生的 *時間* 資訊，導致無法計算距離。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall/Confusion (陷阱/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Java Stack Class** | Using `Stack<Integer> s = new Stack<>();` | **Avoid.** It extends `Vector` and is synchronized (slow). Use `Deque<Integer> s = new ArrayDeque<>();`. <br> **避免。** 它繼承自 `Vector` 且是同步的（較慢）。請使用 `ArrayDeque`。 |
| **Monotonicity Direction** | Confusing when to use increasing vs. decreasing stack. | **Rule of Thumb:** Find Next **Greater** $\rightarrow$ **Decreasing** Stack. Find Next **Smaller** $\rightarrow$ **Increasing** Stack. <br> **經驗法則：** 找下一個**更大** $\rightarrow$ **遞減**堆疊。找下一個**更小** $\rightarrow$ **遞增**堆疊。 |
| **Stack vs Recursion** | Thinking they are completely different. | Recursion **is** implicitly using the system call stack. Any recursive solution can be rewritten iteratively using an explicit stack. <br> 遞迴**就是**隱式地使用系統呼叫堆疊。任何遞迴解法都可以用顯式堆疊重寫為迭代解法。 |
| **Empty Check** | Forgetting `!stack.isEmpty()` before `peek()` or `pop()`. | This causes `EmptyStackException` or `NoSuchElementException`. Always check first. <br> 這會導致異常。務必先檢查。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the Pattern:** "This problem involves matching/nested dependencies/finding the next greater element, which suggests a Stack approach."
    **識別模式：** 「這個問題涉及配對/巢狀依賴/尋找下一個更大元素，這暗示了使用堆疊的方法。」
2.  **Define the Stack:** "I will use a stack to store the indices of the elements we haven't resolved yet."
    **定義堆疊：** 「我將使用一個堆疊來存儲我們尚未解決的元素索引。」
3.  **Explain the Invariant:** "The stack will remain monotonic decreasing because..."
    **解釋不變性：** 「堆疊將保持單調遞減，因為……」

### Whiteboard Strategy (白板策略)
*   **Draw the Stack:** Draw a vertical bucket open at the top.
    **畫出堆疊：** 畫一個頂部開口的垂直桶子。
*   **Trace with Pointer:** Use an arrow `i` for the current array element and visually push/pop items in your bucket.
    **用指標追蹤：** 用箭頭 `i` 代表當前陣列元素，並視覺化地將項目推入/彈出桶子。
*   **Table Trace:** Create a table with columns: `Current Element`, `Stack Content`, `Action`.
    **表格追蹤：** 建立一個表格，包含欄位：`當前元素`、`堆疊內容`、`動作`。

### Common Follow-ups (常見後續問題)
*   **Q:** Can you do this with $O(1)$ space?
    **問：** 你能用 $O(1)$ 空間做到嗎？
    *   *A:* Usually no, unless we can overwrite the input array or if the problem logic allows two-pointers (rare for pure stack problems).
    *   *答：* 通常不行，除非我們可以覆蓋輸入陣列，或者問題邏輯允許雙指針（純堆疊問題很少見）。
*   **Q:** What if the array is circular?
    **問：** 如果陣列是循環的怎麼辦？
    *   *A:* Iterate through the array twice (loop up to `2 * n`) using modulo operator `% n`.
    *   *答：* 遍歷陣列兩次（迴圈至 `2 * n`），並使用模運算符 `% n`。

---

## 7. Practice Problems (練習題)

### 1. Easy: Valid Parentheses (LeetCode 20)
*   **Prompt:** Determine if the input string has valid brackets `()[]{}`.
    **題目：** 判斷輸入字串是否有有效的括號 `()[]{}`。
*   **Hint:** Push opening brackets; check matching closing brackets on pop.
    **提示：** 推入左括號；彈出時檢查是否匹配右括號。
*   **Key:** Use a Map for mapping `)` to `(`, etc.
    **關鍵：** 使用 Map 來映射 `)` 到 `(` 等。

### 2. Medium: Min Stack (LeetCode 155)
*   **Prompt:** Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
    **題目：** 設計一個支援推入、彈出、頂端查看，並能在常數時間內檢索最小元素的堆疊。
*   **Hint:** Use two stacks. One for data, one for current minimums.
    **提示：** 使用兩個堆疊。一個存數據，一個存當前最小值。
*   **Key:** The `minStack` push logic: `minStack.push(Math.min(val, minStack.peek()))`.
    **關鍵：** `minStack` 的推入邏輯：`minStack.push(Math.min(val, minStack.peek()))`。

### 3. Hard: Largest Rectangle in Histogram (LeetCode 84)
*   **Prompt:** Given heights of bars, find the largest rectangle area.
    **題目：** 給定柱狀圖的高度，找出最大的矩形面積。
*   **Hint:** Monotonic Increasing Stack. When a bar is shorter than the top, the top bar's right boundary is determined.
    **提示：** 單調遞增堆疊。當一個柱子比頂端短時，頂端柱子的右邊界就確定了。
*   **Key:** Calculate area during `pop()`. Height is `heights[pop()]`, width is `i - stack.peek() - 1`.
    **關鍵：** 在 `pop()` 時計算面積。高度是 `heights[pop()]`，寬度是 `i - stack.peek() - 1`。

---

## 8. Rapid Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] **Empty Stack:** Did I check `!stack.isEmpty()` before every `pop()` or `peek()`?
    **空堆疊：** 我是否在每次 `pop()` 或 `peek()` 前檢查了 `!stack.isEmpty()`？
- [ ] **Return Value:** If the stack is not empty at the end, does that mean something (e.g., invalid parentheses)?
    **回傳值：** 如果結束時堆疊不為空，這是否意味著什麼（例如：無效括號）？
- [ ] **Index vs Value:** Am I storing the index (for distance calculation) or the value?
    **索引 vs 數值：** 我是存儲索引（用於距離計算）還是數值？
- [ ] **Duplicates:** How do I handle duplicate values in a monotonic stack? (Strictly greater vs greater or equal).
    **重複值：** 我如何處理單調堆疊中的重複值？（嚴格大於 vs 大於等於）。

### Complexity Confirmation (複雜度確認)
- [ ] **Linear Scan:** Do I verify that every element enters and leaves the stack at most once? ($O(N)$).
    **線性掃描：** 我是否確認每個元素最多進出堆疊一次？($O(N)$)。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Dirty Plates" Analogy (髒盤子類比):**
    *   You can only wash the top plate. If you need the bottom plate, you must remove all plates above it.
    *   你只能洗最上面的盤子。如果你需要最底下的盤子，必須移開上面所有的盤子。
    
*   **The "Monotonic Valley" (單調山谷):**
    *   **Decreasing Stack:** Imagine looking for a mountain peak to the right. You keep people in a line sorted by height. If a giant comes, he blocks the view of everyone shorter than him (pop them).
    *   **遞減堆疊：** 想像在尋找右邊的山峰。你讓人們按身高排隊。如果一個巨人來了，他會擋住所有比他矮的人的視線（將他們彈出）。

*   **Visual Anchor (視覺錨點):**
    *   `ArrayDeque` is a double-ended tube, but for Stack, we block one end.
    *   `ArrayDeque` 是一根雙頭通的管子，但對於 Stack，我們封住了其中一端。