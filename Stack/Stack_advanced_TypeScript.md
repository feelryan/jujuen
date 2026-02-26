# Advanced Data Structures: Stack (堆疊)

## 1. Learning Objectives (學習目標)

*   **Master Monotonic Stacks:** Understand how to solve "Next Greater Element" and "Histogram" type problems in $O(N)$ time.
    **掌握單調堆疊（Monotonic Stack）：** 理解如何在 $O(N)$ 時間內解決「下一個更大元素」與「直方圖」類型的問題。
*   **Recursion to Iteration:** Learn to convert recursive DFS or complex parsing logic into iterative solutions using an explicit stack to avoid stack overflow.
    **遞迴轉迭代：** 學習如何使用顯式堆疊將遞迴 DFS 或複雜解析邏輯轉換為迭代解法，以避免堆疊溢位。
*   **Complex Parsing & Evaluation:** Handle nested structures (parentheses, expressions) proficiently, a common pattern in system design and algorithm interviews.
    **複雜解析與評估：** 熟練處理巢狀結構（括號、表達式），這是系統設計與演算法面試中的常見模式。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
*   **LIFO (Last-In, First-Out):** The last element added is the first one processed. Think of it as a "deferred processing" mechanism.
    **後進先出：** 最後加入的元素最先被處理。將其視為一種「延遲處理」機制。
*   **The "History" Buffer:** Stacks are perfect for problems where you need to access the most recent data to make a decision about the current element.
    **「歷史」緩衝區：** 堆疊非常適合用於「需要存取最近的資料以對當前元素做出決策」的問題。

### Complexity (複雜度)
*   **Push/Pop/Peek:** $O(1)$.
    **推入/彈出/查看：** $O(1)$。
*   **Search/Access:** $O(N)$ (This is not what stacks are for).
    **搜尋/存取：** $O(N)$（這不是堆疊的用途）。

### When to Use (適用場景)
*   **Matching/Pairing:** Parentheses, tags, palindromes.
    **配對/匹配：** 括號、標籤、迴文。
*   **Monotonicity:** Finding the nearest greater/smaller element.
    **單調性：** 尋找最近的較大/較小元素。
*   **Tree/Graph Traversal:** Iterative DFS.
    **樹/圖遍歷：** 迭代式深度優先搜尋。
*   **Undo/Redo Operations:** Browser history, text editors.
    **復原/重做操作：** 瀏覽器歷史記錄、文字編輯器。

### When NOT to Use (不適用場景)
*   **Random Access:** If you need the $k$-th element frequently.
    **隨機存取：** 如果你需要頻繁存取第 $k$ 個元素。
*   **BFS (Breadth-First Search):** Use a Queue instead.
    **廣度優先搜尋：** 請改用佇列（Queue）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Monotonic Stack (單調堆疊)
*   **Concept:** Maintain a stack where elements are always sorted (increasing or decreasing).
    **概念：** 維護一個堆疊，其中的元素始終保持排序（遞增或遞減）。
*   **Use Case:** Finding the "Next Greater Element" or "Previous Smaller Element".
    **用途：** 尋找「下一個更大元素」或「上一個更小元素」。

### B. Parentheses & String Decoding (括號與字串解碼)
*   **Concept:** Push context onto the stack when entering a nested structure (e.g., `(` or `[`) and pop/process when exiting.
    **概念：** 進入巢狀結構（如 `(` 或 `[`）時將上下文推入堆疊，退出時彈出並處理。
*   **Use Case:** Valid Parentheses, Calculator, Decode String.
    **用途：** 有效括號、計算機、字串解碼。

### C. Iterative DFS (迭代式 DFS)
*   **Concept:** Simulating the system call stack explicitly.
    **概念：** 顯式模擬系統呼叫堆疊。
*   **Use Case:** Binary Tree Inorder Traversal, Graph connectivity.
    **用途：** 二元樹中序遍歷、圖的連通性。

---

## 4. Example Walkthrough (範例講解)

### Problem: Largest Rectangle in Histogram (Hard)
**問題：直方圖中的最大矩形（困難）**

#### Problem Statement (問題重述)
Given an array of integers `heights` representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
給定一個整數陣列 `heights` 代表直方圖的長條高度（每個長條寬度為 1），請回傳直方圖中最大矩形的面積。

#### Approach & Thought Process (思路)

1.  **Brute Force ($O(N^2)$):**
    *   For each bar `i`, expand left and right to find the first bars smaller than `heights[i]`.
    *   **暴力解：** 對於每個長條 `i`，向左和向右擴展，找到第一個小於 `heights[i]` 的長條。
    *   *Inefficient for large inputs.* (*對於大輸入效率低落。*)

2.  **Optimization with Monotonic Stack ($O(N)$):**
    *   **Intuition:** For a rectangle defined by height $H$, we want to find the widest possible width. This width is determined by the *first* element to the left and right that is *shorter* than $H$.
    *   **直覺：** 對於高度為 $H$ 的矩形，我們想找到最大可能的寬度。這個寬度由左右兩側*第一個*比 $H$ *矮*的元素決定。
    *   **Mechanism:** Maintain a **Monotonic Increasing Stack**. When we see a bar `current` that is shorter than the bar at `stack.top()`, it means the rectangle with height `heights[stack.top()]` cannot extend further to the right. We pop and calculate its area.
    *   **機制：** 維護一個 **單調遞增堆疊**。當我們看到一個長條 `current` 比 `stack.top()` 矮時，意味著高度為 `heights[stack.top()]` 的矩形無法再向右延伸。我們將其彈出並計算面積。

#### TypeScript Solution (TypeScript 參考解)

```typescript
/**
 * Calculates the largest rectangle area in a histogram.
 * 計算直方圖中最大的矩形面積。
 * 
 * Time Complexity: O(N) - Each element is pushed and popped at most once.
 * Space Complexity: O(N) - Stack size.
 */
function largestRectangleArea(heights: number[]): number {
    // Append a 0 to the end to ensure the stack is cleared at the finish.
    // 在末尾添加 0，以確保結束時堆疊被清空（強制彈出所有剩餘元素）。
    const extendedHeights = [...heights, 0];
    const stack: number[] = []; // Stores indices (儲存索引)
    let maxArea = 0;

    for (let i = 0; i < extendedHeights.length; i++) {
        const currentHeight = extendedHeights[i];

        // While stack is not empty AND current bar is shorter than the bar at stack top
        // 當堆疊不為空 且 當前長條比堆疊頂端的長條矮
        while (stack.length > 0 && currentHeight < extendedHeights[stack[stack.length - 1]]) {
            const h = extendedHeights[stack.pop()!]; // Height of the popped bar (被彈出長條的高度)
            
            // Determine the width:
            // If stack is empty, it means 'h' was the smallest so far, extending from 0 to i.
            // Otherwise, it extends from the new stack top (exclusive) to i (exclusive).
            // 決定寬度：
            // 若堆疊為空，表示 'h' 是目前最小的，範圍從 0 到 i。
            // 否則，範圍從新的堆疊頂端（不含）到 i（不含）。
            const w = stack.length === 0 ? i : i - stack[stack.length - 1] - 1;
            
            maxArea = Math.max(maxArea, h * w);
        }
        
        stack.push(i);
    }

    return maxArea;
}
```

#### Common Mistakes (錯誤示範 & 為何錯)
*   **Storing Values instead of Indices:**
    *   *Mistake:* `stack.push(heights[i])`.
    *   *Why:* You lose the position information needed to calculate the width ($width = right\_index - left\_index - 1$).
    *   **存值而非索引：** 這樣會丟失計算寬度所需的位置資訊。
*   **Forgetting the "Sentinel" (Dummy 0):**
    *   *Mistake:* Looping only up to `heights.length`.
    *   *Why:* If the array is strictly increasing (e.g., `[1, 2, 3]`), nothing gets popped, and the area is never calculated.
    *   **忘記「哨兵」（虛擬 0）：** 如果陣列是嚴格遞增的，迴圈結束時堆疊內仍有元素，導致面積未被計算。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall |
| :--- | :--- |
| **Index vs. Value** | **Always ask:** Should I store the index or the value? <br> **Rule of Thumb:** If you need to calculate distance/width, store the **index**. |
| **索引 vs. 數值** | **常問：** 我該存索引還是數值？<br> **經驗法則：** 如果你需要計算距離/寬度，請存 **索引**。 |
| **Monotonic Increasing vs. Decreasing** | **Increasing Stack:** Finds the first element *smaller* than current. <br> **Decreasing Stack:** Finds the first element *larger* than current. <br> *Confusing naming: The stack content is increasing, but it helps find smaller bounds.* |
| **單調遞增 vs. 遞減** | **遞增堆疊：** 尋找第一個比當前 *小* 的元素。<br> **遞減堆疊：** 尋找第一個比當前 *大* 的元素。<br> *命名易混淆：堆疊內容是遞增的，但它幫助尋找較小的邊界。* |
| **Empty Stack Access** | Always check `if (stack.length > 0)` before `stack.pop()` or `stack[stack.length-1]`. In TS/JS, accessing out of bounds returns `undefined`, which can cause `NaN` in math ops. |
| **空堆疊存取** | 在操作前務必檢查堆疊是否為空。在 TS/JS 中，越界存取會回傳 `undefined`，導致數學運算出現 `NaN`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the LIFO nature:** "Since we need to process the most recent nested bracket first, a Stack is the natural choice."
    **識別 LIFO 特性：** 「因為我們需要優先處理最近的巢狀括號，堆疊是自然的選擇。」
2.  **Define the Invariant (for Monotonic Stack):** "I will maintain a stack of indices such that the heights corresponding to these indices are always strictly increasing."
    **定義不變性（針對單調堆疊）：** 「我將維護一個索引堆疊，使得這些索引對應的高度始終嚴格遞增。」

### Whiteboard Strategy (白板策略)
*   **Trace with a Table:** Draw columns for `Current Element`, `Stack State`, and `Variables` (e.g., `maxArea`). Update them row by row.
    **表格追蹤：** 畫出 `當前元素`、`堆疊狀態` 和 `變數` 的欄位，逐行更新。
*   **Visualize the "Wall":** For Histogram/Water problems, draw the bars and physically cross them out as they are popped from the stack.
    **視覺化「牆」：** 對於直方圖/接雨水問題，畫出長條，並在它們從堆疊彈出時將其劃掉。

### Common Follow-ups (常見追問)
*   **Q:** What if the input is a continuous stream?
    **問：** 如果輸入是連續串流怎麼辦？
    *   *A:* We might need to process elements immediately or limit the buffer size.
*   **Q:** Can we optimize space to O(1)?
    **問：** 能將空間優化至 O(1) 嗎？
    *   *A:* Usually no for stack problems, unless we modify the input array (Morris Traversal for trees) or use Two Pointers (for specific water container problems).

---

## 7. Practice Problems (練習題)

### Easy/Medium: Evaluate Reverse Polish Notation
**易/中：逆波蘭表示法求值**
*   **Prompt:** Evaluate the value of an arithmetic expression in Reverse Polish Notation (e.g., `["2","1","+","3","*"]` -> `(2+1)*3` -> `9`).
    **題目：** 計算逆波蘭表示法的算術表達式的值。
*   **Hint:** Iterate through tokens. If number, push to stack. If operator, pop two numbers, calculate, push result back.
    **提示：** 遍歷標記。若是數字則推入堆疊；若是運算符，彈出兩個數字，計算後將結果推回。

### Medium: Decode String
**中等：字串解碼**
*   **Prompt:** Given `3[a]2[bc]`, return `"aaabcbc"`. Supports nested `3[a2[c]]`.
    **題目：** 給定 `3[a]2[bc]`，回傳 `"aaabcbc"`。支援巢狀 `3[a2[c]]`。
*   **Hint:** Use two stacks (one for count, one for string) OR a single stack storing objects. When `]` is met, pop, repeat string, and append to the previous context.
    **提示：** 使用兩個堆疊（一個存次數，一個存字串）或一個存物件的堆疊。遇到 `]` 時，彈出、重複字串，並附加到前一個上下文。

### Hard: Trapping Rain Water
**困難：接雨水**
*   **Prompt:** Given an elevation map, compute how much water it can trap.
    **題目：** 給定高度圖，計算能接多少雨水。
*   **Hint:** This is the inverse of the Histogram problem. Use a Monotonic **Decreasing** Stack. When we find a bar *taller* than the top, we have a "valley". The water is bounded by the current bar and the new stack top.
    **提示：** 這是直方圖問題的反轉。使用單調 **遞減** 堆疊。當發現比頂端 *高* 的長條時，就形成了一個「山谷」。水被當前長條與新的堆疊頂端所限制。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Empty Check:** Did I guard against `stack.pop()` on an empty stack?
    **空檢查：** 我是否防止了對空堆疊執行 `stack.pop()`？
*   [ ] **Type Safety:** Am I pushing consistent types (always indices OR always values)?
    **型別安全：** 我推入的型別是否一致（總是索引 或 總是數值）？
*   [ ] **Cleanup:** Do I need a dummy element at the end to force process remaining items?
    **清理：** 我是否需要在末尾添加虛擬元素以強制處理剩餘項目？
*   [ ] **Complexity:** Is it truly $O(N)$? (Ensure each element is pushed/popped at most once).
    **複雜度：** 真的是 $O(N)$ 嗎？（確保每個元素最多被推入/彈出一次）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Dirty Plates" Analogy:**
    *   You can only wash the plate at the top. If you put a new dirty plate on top, the one beneath it must wait.
    *   **「髒盤子」類比：** 你只能洗最上面的盤子。如果你放了一個新的髒盤子在上面，下面的就必須等待。
*   **The "Line of Sight" (Monotonic Stack):**
    *   Imagine people standing in a line. If a tall person stands in front of a short person, the short person can't see anything ahead. The stack stores the people who can still "see" the stage.
    *   **「視線」（單調堆疊）：** 想像人們排成一列。如果一個高個子站在矮個子前面，矮個子就看不到前面的任何東西。堆疊儲存的是那些仍然能「看見」舞台的人。