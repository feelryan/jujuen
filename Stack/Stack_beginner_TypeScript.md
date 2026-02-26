# Stack (Beginner) - Interview Guide
# 堆疊（基礎）- 面試指南

## 1. Learning Objectives（學習目標）

1.  **Understand the LIFO Principle deeply:** Not just the definition, but how it maps to system call stacks and recursion.
    **深入理解 LIFO 原則：** 不僅是定義，還要理解它如何對應到系統呼叫堆疊與遞迴。
2.  **Master TypeScript Array implementation:** Know the performance implications of array methods when used as a stack.
    **掌握 TypeScript 陣列實作：** 了解將陣列作為堆疊使用時的方法與效能影響。
3.  **Identify "Matching" and "Backtracking" patterns:** Recognize problems solvable by pairing elements or reverting states.
    **識別「配對」與「回溯」模式：** 辨識出可以透過配對元素或還原狀態來解決的問題。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
A Stack is a linear data structure that follows the **Last In, First Out (LIFO)** principle.
堆疊是一種遵循 **後進先出 (LIFO)** 原則的線性資料結構。

The element added last is the first one to be removed.
最後加入的元素會最先被移除。

### Intuition（直覺）
Think of a stack of plates in a cafeteria. You can only take the top plate, and you place new plates on top.
想像自助餐廳裡的一疊盤子。你只能拿取最上面的盤子，也只能將新盤子放在最上面。

### Complexity（複雜度）

| Operation | Time Complexity (時間複雜度) | Note (備註) |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(1)$ | Amortized if dynamic array resizing occurs (若發生動態陣列擴容則為均攤) |
| **Pop (Remove)** | $O(1)$ | Removes from the tail (從尾端移除) |
| **Peek/Top** | $O(1)$ | Inspects the last element (查看最後一個元素) |
| **Space** | $O(n)$ | Stores $n$ elements (儲存 $n$ 個元素) |

### When to Use（適用場景）
*   **Reversing items:** Strings, linked lists, or words.
    **反轉項目：** 字串、鏈結串列或單字。
*   **Matching/Pairing:** Validating parentheses, HTML tags.
    **配對/成對：** 驗證括號、HTML 標籤。
*   **Backtracking/History:** Browser back button, Undo features, DFS (Depth-First Search).
    **回溯/歷史紀錄：** 瀏覽器上一頁、復原功能、深度優先搜尋 (DFS)。

### When NOT to Use（不適用場景）
*   **Random Access:** If you need to access the $k$-th element frequently ($O(n)$ cost).
    **隨機存取：** 如果你需要頻繁存取第 $k$ 個元素（成本為 $O(n)$）。
*   **FIFO Requirements:** Use a Queue instead for task scheduling.
    **先進先出需求：** 任務排程請改用佇列 (Queue)。

---

## 3. Typical Patterns（典型題型 / 模式）

For the beginner level, we focus on the most structural patterns:
針對基礎級別，我們專注於最結構化的模式：

1.  **Sequential Matching (順序配對):**
    Processing a stream of symbols where the latest open symbol must match the earliest close symbol (e.g., Valid Parentheses).
    處理一系列符號，其中最新的開啟符號必須與最早遇到的關閉符號匹配（例如：有效括號）。

2.  **String Reversal / Manipulation (字串反轉/操作):**
    Using the stack to reverse the order of characters or words.
    利用堆疊來反轉字元或單字的順序。

3.  **Function Call Simulation (函數呼叫模擬):**
    Manually managing state to convert recursion into iteration.
    手動管理狀態以將遞迴轉換為迭代。

---

## 4. Example Walkthrough（範例講解）

### Problem: Valid Parentheses
### 問題：有效的括號

**Problem Statement:**
Given a string `s` containing just the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.
給定一個僅包含字元 `(`, `)`, `{`, `}`, `[` 和 `]` 的字串 `s`，判斷該輸入字串是否有效。

Input: `s = "()[]{}"` -> Output: `true`
Input: `s = "(]"` -> Output: `false`

### Thought Process（思路）

1.  **Brute Force (暴力法):**
    Repeatedly find and replace adjacent matching pairs like `()` with empty strings until no more pairs exist.
    重複尋找並替換相鄰的配對（如 `()`）為空字串，直到沒有配對為止。
    *Complexity:* $O(n^2)$ time (string concatenation/shifting is expensive).
    *複雜度：* 時間 $O(n^2)$（字串串接/位移成本高昂）。

2.  **Optimization (Stack Approach) (優化 - 堆疊法):**
    We observe that the *last* opening bracket must be closed *first*. This screams LIFO.
    我們觀察到*最後*一個開啟的括號必須*最先*被關閉。這強烈暗示了 LIFO 特性。
    *   Iterate through the string.
        遍歷字串。
    *   If it's an opening bracket, push it onto the stack.
        如果是開啟括號，將其推入堆疊。
    *   If it's a closing bracket, check if it matches the top of the stack.
        如果是關閉括號，檢查它是否與堆疊頂端匹配。
    *   If stack is empty at the end, it's valid.
        如果結束時堆疊為空，則為有效。

### TypeScript Solution（TypeScript 參考解）

```typescript
/**
 * Determines if the input string has valid parentheses.
 * 判斷輸入字串是否包含有效的括號。
 *
 * Time Complexity: O(n) - We traverse the string once.
 * 時間複雜度：O(n) - 我們遍歷字串一次。
 * Space Complexity: O(n) - In the worst case (all open brackets), stack size is n.
 * 空間複雜度：O(n) - 在最差情況下（全為開啟括號），堆疊大小為 n。
 */
function isValid(s: string): boolean {
    // Edge case: Odd length strings cannot be valid
    // 邊界條件：奇數長度的字串不可能是有效的
    if (s.length % 2 !== 0) return false;

    // Use an array as a stack
    // 使用陣列作為堆疊
    const stack: string[] = [];
    
    // Map for easy lookup of matching pairs
    // 使用 Map 以便輕鬆查找配對
    const bracketMap = new Map<string, string>([
        [')', '('],
        ['}', '{'],
        [']', '[']
    ]);

    for (const char of s) {
        // If the character is a closing bracket (key in map)
        // 如果該字元是關閉括號（Map 中的鍵）
        if (bracketMap.has(char)) {
            // Pop the top element from stack. If stack is empty, pop() returns undefined.
            // 從堆疊彈出頂端元素。如果堆疊為空，pop() 回傳 undefined。
            const topElement = stack.pop();
            
            // Check if the popped element matches the expected opening bracket
            // 檢查彈出的元素是否與預期的開啟括號匹配
            if (topElement !== bracketMap.get(char)) {
                return false;
            }
        } else {
            // It is an opening bracket, push to stack
            // 這是開啟括號，推入堆疊
            stack.push(char);
        }
    }

    // If stack is empty, all brackets were matched correctly
    // 如果堆疊為空，表示所有括號都正確匹配
    return stack.length === 0;
}
```

### Common Mistake Example（錯誤示範）

```typescript
// ❌ WRONG: Ignoring the empty stack check during iteration
// ❌ 錯誤：忽略了迭代過程中的空堆疊檢查

function isValidWrong(s: string): boolean {
    const stack = [];
    for (let char of s) {
        if (char === '(') stack.push(')');
        // If stack is empty, pop() returns undefined. 
        // undefined !== ')' is true, but logic might fail in other languages or strict checks.
        // Also, logic is harder to read without a map for multiple types.
        else if (stack.pop() !== char) return false; 
    }
    // Forgot to check if stack is empty at the end! "(()" would pass here.
    // 忘記檢查結束時堆疊是否為空！"(()" 會在這裡通過測試。
    return true; 
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Stack vs Queue** | Stack is LIFO (Vertical pile); Queue is FIFO (Horizontal line). Don't mix up `pop()` (remove end) and `shift()` (remove start). <br> 堆疊是 LIFO（垂直堆疊）；佇列是 FIFO（水平排隊）。別混淆 `pop()`（移除末端）與 `shift()`（移除開頭）。 |
| **Stack Underflow** | Popping from an empty stack. In TS, `[].pop()` is `undefined`, which can cause silent bugs if not handled. <br> 從空堆疊彈出。在 TS 中，`[].pop()` 會回傳 `undefined`，若未處理可能導致隱性 Bug。 |
| **Leftover Elements** | Returning `true` just because the loop finished. You must check `stack.length === 0`. <br> 僅因迴圈結束就回傳 `true`。你必須檢查 `stack.length === 0`。 |
| **Space Complexity** | Seniors often forget that recursion *is* a stack. Recursive solutions have $O(n)$ space complexity due to the call stack. <br> 資深工程師常忘記遞迴*就是*堆疊。遞迴解法因呼叫堆疊而具有 $O(n)$ 的空間複雜度。 |

---

## 6. Interview Strategy（面試實戰建議）

### Narration Framework（口條框架）
1.  **Identify the LIFO nature:** "Since we need to process the most recent element first, a Stack is the natural choice."
    **識別 LIFO 特性：** 「由於我們需要優先處理最近的元素，堆疊是自然的選擇。」
2.  **Define the State:** "I will use the stack to store [Opening Brackets / Previous States / Indices]."
    **定義狀態：** 「我將使用堆疊來儲存 [開啟括號 / 先前狀態 / 索引]。」
3.  **Address Complexity:** "Using a stack allows us to process this in one pass, $O(n)$ time, with $O(n)$ auxiliary space."
    **說明複雜度：** 「使用堆疊讓我們能以 $O(n)$ 時間單次遍歷完成，並使用 $O(n)$ 的輔助空間。」

### Whiteboard Strategy（白板策略）
*   **Draw the Stack:** Visually draw a vertical container on the side. Trace the code by writing/erasing elements in it.
    **畫出堆疊：** 在旁邊畫一個垂直的容器。透過在裡面寫入/擦除元素來追蹤程式碼。
*   **Variable Naming:** Use `stack` or `history` instead of generic names like `arr` or `list`.
    **變數命名：** 使用 `stack` 或 `history`，而非 `arr` 或 `list` 等通用名稱。

### Common Follow-ups（常見追問）
*   "Can you solve this with $O(1)$ space?" (Usually implies modifying the input in-place or using two pointers if applicable).
    「你能用 $O(1)$ 空間解決嗎？」（通常暗示原地修改輸入或在適用時使用雙指標）。
*   "What if the input is too large to fit in memory?" (Stream processing).
    「如果輸入太大無法放入記憶體怎麼辦？」（串流處理）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Implement Stack using Queues (or vice versa)
**用佇列實作堆疊（反之亦然）**
*   **Prompt:** Implement a LIFO stack using only two queues.
    **題目：** 僅使用兩個佇列實作一個 LIFO 堆疊。
*   **Hint:** You need to move all elements from $q1$ to $q2$ whenever you push a new element to keep the order correct.
    **提示：** 每當推入新元素時，你需要將 $q1$ 的所有元素移至 $q2$ 以保持順序正確。
*   **Focus:** Understanding the cost of operations (Push becomes $O(n)$).
    **重點：** 理解操作的成本（Push 變成 $O(n)$）。

### 2. Medium: Min Stack
**最小堆疊**
*   **Prompt:** Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
    **題目：** 設計一個支援 push、pop、top 以及在常數時間內檢索最小元素的堆疊。
*   **Hint:** Use a second stack (`minStack`) to keep track of the minimums at each level.
    **提示：** 使用第二個堆疊 (`minStack`) 來追蹤每一層的最小值。
*   **Focus:** Synchronizing state between two data structures.
    **重點：** 在兩個資料結構之間同步狀態。

### 3. Hard (Conceptually): Evaluate Reverse Polish Notation
**逆波蘭表示法求值**
*   **Prompt:** Evaluate the value of an arithmetic expression in Reverse Polish Notation (e.g., `["2","1","+","3","*"]` -> `(2+1)*3` -> `9`).
    **題目：** 計算逆波蘭表示法中的算術表達式的值。
*   **Hint:** Push numbers; when you see an operator, pop two numbers, calculate, and push the result back.
    **提示：** 推入數字；當看到運算子時，彈出兩個數字，計算後將結果推回。
*   **Focus:** Handling operations where order matters (subtraction/division).
    **重點：** 處理順序至關重要的運算（減法/除法）。

---

## 8. Quick Checklists（快速檢核表）

Use this before submitting your code:
提交程式碼前請使用此表：

*   [ ] **Empty Check:** Did I handle the case where `pop()` or `peek()` is called on an empty stack?
    **空檢查：** 我是否處理了在空堆疊上呼叫 `pop()` 或 `peek()` 的情況？
*   [ ] **Return Value:** Is the final answer the *stack itself*, the *top element*, or a *boolean* (is empty)?
    **回傳值：** 最終答案是*堆疊本身*、*頂端元素*，還是*布林值*（是否為空）？
*   [ ] **Types:** In TypeScript, did I handle `undefined` return types from `pop()`?
    **型別：** 在 TypeScript 中，我是否處理了 `pop()` 回傳的 `undefined` 型別？
*   [ ] **Cleanup:** If the problem asks for the state *after* operations, is the stack order correct (bottom-up vs top-down)?
    **清理：** 如果題目要求操作*後*的狀態，堆疊順序是否正確（由底至頂 vs 由頂至底）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The "Ctrl+Z" Analogy:**
    Every time you type, you **push** a state. When you hit Ctrl+Z (Undo), you **pop** the state.
    **「Ctrl+Z」類比：** 每次打字，你都 **push** 一個狀態。當你按 Ctrl+Z（復原），你 **pop** 該狀態。

*   **The "Pringles Can" (洋芋片罐):**
    You can only eat the chip at the top. To get to the bottom one, you must eat all the ones above it.
    **「洋芋片罐」：** 你只能吃最上面的洋芋片。要拿到最底下的，你必須先吃掉上面所有的。

*   **Visual Anchor:**
    ⬇️ `Push` (Down into the bucket)
    ⬆️ `Pop` (Up out of the bucket)
    **視覺錨點：**
    ⬇️ `Push`（向下放入桶中）
    ⬆️ `Pop`（向上拿出桶外）