# Data Structure Module: Stack (Beginner)
# 資料結構模組：堆疊（初階）

## 1. Learning Objectives (學習目標)

*   **Master the LIFO Principle:** Understand deeply how Last-In, First-Out governs data flow and state management.
    **掌握 LIFO 原則：** 深刻理解「後進先出」如何主導資料流向與狀態管理。
*   **Implement with Proficiency:** Know how to implement a stack using Python's dynamic arrays (lists) and understand the amortized complexity.
    **熟練實作：** 知道如何使用 Python 的動態陣列（list）實作堆疊，並理解其均攤複雜度。
*   **Identify Matching Patterns:** Recognize problems involving nested structures (e.g., parentheses, HTML tags) as classic stack candidates.
    **識別配對模式：** 辨識涉及巢狀結構（如括號、HTML 標籤）的問題為經典的堆疊候選題。
*   **Handle Edge Cases:** Learn to prevent common runtime errors like popping from an empty stack.
    **處理邊界情況：** 學習如何防止如從空堆疊彈出元素等常見的執行期錯誤。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Stack is a linear data structure that follows the **LIFO (Last-In, First-Out)** order.
堆疊是一種遵循 **LIFO（後進先出）** 順序的線性資料結構。
The element added last is the first one to be removed.
最後被加入的元素是第一個被移除的。

### Intuition (直覺)
Think of a stack of dinner plates.
想像一疊晚餐盤子。
You can only add a new plate to the top or remove the top plate.
你只能將新盤子放到頂端，或從頂端移除盤子。
Trying to pull a plate from the middle or bottom is unsafe and inefficient.
試圖從中間或底部抽取盤子是不安全且低效的。

### Complexity (複雜度)

| Operation | Time Complexity | Note |
| :--- | :--- | :--- |
| **Push (Insert)** | $O(1)$ | Amortized $O(1)$ in Python lists due to resizing. (Python list 因調整大小為均攤 $O(1)$) |
| **Pop (Remove)** | $O(1)$ | Removing from the end. (從末端移除) |
| **Peek (Top)** | $O(1)$ | Accessing the last element. (存取最後一個元素) |
| **Search** | $O(N)$ | Requires scanning the stack. (需要掃描堆疊) |
| **Space** | $O(N)$ | Stores $N$ elements. (儲存 $N$ 個元素) |

### When to Use (適用場景)
*   **Reverse Order Processing:** When you need to process data in the reverse order of its arrival (e.g., Undo feature).
    **逆序處理：** 當你需要以資料到達的相反順序處理資料時（例如：復原功能）。
*   **Nested Structures:** Parsing code, validating parentheses, or evaluating expressions.
    **巢狀結構：** 解析程式碼、驗證括號或計算表達式。
*   **Function Call Management:** Recursion relies implicitly on the system call stack.
    **函式呼叫管理：** 遞迴隱含地依賴系統呼叫堆疊。

### When NOT to Use (不適用場景)
*   **Random Access:** If you need to access elements by index frequently ($O(1)$), use an Array or Hash Map.
    **隨機存取：** 如果你需要頻繁地透過索引存取元素（$O(1)$），請使用陣列或雜湊表。
*   **FIFO Requirements:** If the first element in needs to be processed first, use a Queue.
    **FIFO 需求：** 如果最先進入的元素需要最先被處理，請使用佇列。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner level, we focus on explicit stack usage.
針對初階程度，我們專注於顯式的堆疊使用。

1.  **Paired Matching (配對匹配):**
    Checking for balanced symbols (parentheses, brackets).
    檢查平衡的符號（小括號、中括號）。
2.  **String Reversal (字串反轉):**
    Using a stack to reverse a string or check for palindromes.
    使用堆疊來反轉字串或檢查迴文。
3.  **History Navigation (歷史導航):**
    Implementing browser back/forward buttons (often uses two stacks).
    實作瀏覽器的上一頁/下一頁按鈕（通常使用兩個堆疊）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Valid Parentheses (LeetCode 20)
**問題：有效的括號**

### Problem Statement (問題重述)
Given a string `s` containing just the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.
給定一個僅包含字元 `(`, `)`, `{`, `}`, `[` 和 `]` 的字串 `s`，判斷輸入字串是否有效。
An input string is valid if open brackets are closed by the same type of brackets in the correct order.
若左括號由相同類型的右括號以正確順序閉合，則輸入字串有效。

### Thought Process (思路)

1.  **Brute Force (暴力法):**
    Repeatedly find adjacent matching pairs like `()` and remove them until the string is empty or no pairs remain.
    重複尋找相鄰的匹配對如 `()` 並將其移除，直到字串為空或沒有剩餘的配對。
    *Complexity:* $O(N^2)$ due to string manipulation/re-scanning. This is inefficient.
    *複雜度：* 由於字串操作/重新掃描，為 $O(N^2)$。這是低效的。

2.  **Optimal Approach: Stack (最佳解：堆疊):**
    We process the string from left to right.
    我們從左到右處理字串。
    When we see an opening bracket, we don't know if it matches yet, so we **push** it onto the stack (wait for its partner).
    當我們看到左括號時，我們還不知道它是否匹配，所以將其 **推入** 堆疊（等待它的夥伴）。
    When we see a closing bracket, it *must* match the most recently seen opening bracket (the **top** of the stack).
    當我們看到右括號時，它 *必須* 與最近看到的左括號（堆疊的 **頂端**）匹配。

### Python Solution (Python 參考解)

```python
def isValid(s: str) -> bool:
    # Use a list as a stack
    # 使用 list 作為堆疊
    stack = []
    
    # Map closing brackets to their corresponding opening brackets
    # 將右括號映射到對應的左括號
    mapping = {")": "(", "}": "{", "]": "["}
    
    for char in s:
        # If the character is a closing bracket
        # 如果字元是右括號
        if char in mapping:
            # Pop the top element if stack is not empty, else assign a dummy value
            # 若堆疊不為空則彈出頂端元素，否則指派一個虛擬值
            top_element = stack.pop() if stack else '#'
            
            # Check if the popped element matches the mapping
            # 檢查彈出的元素是否與映射匹配
            if mapping[char] != top_element:
                return False
        else:
            # It is an opening bracket, push onto the stack
            # 這是左括號，推入堆疊
            stack.append(char)
    
    # If the stack is empty, all brackets were matched correctly
    # 如果堆疊為空，表示所有括號都正確匹配了
    return not stack
```

### Analysis (分析)
*   **Time Complexity:** $O(N)$. We traverse the string once. Each push/pop is $O(1)$.
    **時間複雜度：** $O(N)$。我們遍歷字串一次。每次 push/pop 都是 $O(1)$。
*   **Space Complexity:** $O(N)$. In the worst case (e.g., `((((`), the stack grows to the size of the string.
    **空間複雜度：** $O(N)$。在最壞情況下（例如 `((((`），堆疊增長到字串的大小。

### Common Mistakes (錯誤示範)
*   *Mistake:* Returning `True` immediately after the loop without checking `if not stack`.
    *錯誤：* 迴圈結束後立即回傳 `True`，而未檢查 `if not stack`。
    *Why:* The input might be `((`, which leaves elements in the stack.
    *原因：* 輸入可能是 `((`，這會留下元素在堆疊中。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Stack (LIFO) | Queue (FIFO) |
| :--- | :--- | :--- |
| **Analogy** | Stack of plates (盤子堆) | Line at a store (商店排隊) |
| **Insertion** | `append()` (End/Top) | `append()` (End/Rear) |
| **Removal** | `pop()` (End/Top) | `pop(0)` or `popleft()` (Front) |
| **Python Tool** | `list` is sufficient | `collections.deque` is preferred |

**Pitfalls (陷阱):**
1.  **Empty Stack Pop:** Always check `if stack` before popping. Python raises `IndexError` on `[].pop()`.
    **空堆疊彈出：** 在彈出前務必檢查 `if stack`。Python 對 `[].pop()` 會拋出 `IndexError`。
2.  **Leftovers:** A non-empty stack at the end of processing usually implies invalid input (e.g., unmatched opening tags).
    **殘留物：** 處理結束後堆疊非空通常意味著輸入無效（例如：未匹配的開始標籤）。
3.  **Variable Shadowing:** Avoid naming your variable `list` or `str`, as these shadow Python built-ins. Use `stack` or `stk`.
    **變數遮蔽：** 避免將變數命名為 `list` 或 `str`，因為這會遮蔽 Python 的內建型別。請使用 `stack` 或 `stk`。

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
*   **Identify:** "Since this problem involves matching nested elements/processing in reverse, I will use a Stack."
    **識別：** 「由於這個問題涉及匹配巢狀元素/逆序處理，我將使用堆疊。」
*   **Define State:** "The stack will store the [elements] that we are waiting to match/process."
    **定義狀態：** 「堆疊將儲存我們正在等待匹配/處理的 [元素]。」
*   **Trace:** "I'll iterate through the input. If I see X, I push. If I see Y, I check the top of the stack..."
    **追蹤：** 「我將遍歷輸入。如果看到 X，我推入。如果看到 Y，我檢查堆疊頂端...」

### Whiteboard Strategy (白板策略)
*   Draw a vertical container open at the top.
    畫一個頂部開口的垂直容器。
*   Write the input string horizontally (e.g., `( [ ] )`).
    水平寫下輸入字串（例如 `( [ ] )`）。
*   Use an arrow to point to the current character and physically write/erase elements in your drawn stack to show the state change.
    使用箭頭指向當前字元，並在畫出的堆疊中實際寫入/擦除元素以展示狀態變化。

### Common Follow-ups (常見追問)
*   **Q:** How would you implement this if the stack size is limited?
    **問：** 如果堆疊大小受限，你會如何實作？
    *A:* Check for overflow before pushing. (檢查溢位再推入。)
*   **Q:** Can we optimize space to $O(1)$?
    **問：** 我們能將空間優化至 $O(1)$ 嗎？
    *A:* Usually no for matching problems, unless we can modify the input string in-place or use a counter (only works for single type of parenthesis).
    *答：* 對於匹配問題通常不行，除非我們可以原地修改輸入字串或使用計數器（僅適用於單一類型的括號）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Min Stack (最小堆疊)
*   **Goal:** Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
    **目標：** 設計一個支援 push、pop、top，並能在常數時間內檢索最小元素的堆疊。
*   **Hint:** Use two stacks. One for data, one for keeping track of the current minimums.
    **提示：** 使用兩個堆疊。一個存資料，一個追蹤當前的最小值。

### 2. Medium: Evaluate Reverse Polish Notation (逆波蘭表示法求值)
*   **Goal:** Evaluate the value of an arithmetic expression in Reverse Polish Notation (Postfix). e.g., `["2","1","+","3","*"]` -> `(2+1)*3` -> `9`.
    **目標：** 計算逆波蘭表示法（後綴）算術表達式的值。
*   **Hint:** Push numbers. When you see an operator, pop two numbers, calculate, and push the result back.
    **提示：** 推入數字。當看到運算子時，彈出兩個數字，計算後將結果推回。

### 3. Medium (Harder for beginner): Simplify Path (簡化路徑)
*   **Goal:** Given an absolute path for a Unix-style file system (e.g., `/a/./b/../../c/`), convert it to the canonical path (`/c`).
    **目標：** 給定 Unix 風格檔案系統的絕對路徑，將其轉換為規範路徑。
*   **Hint:** Split string by `/`. Iterate parts. Push valid directory names. Pop on `..`. Ignore `.` and empty strings.
    **提示：** 用 `/` 分割字串。遍歷各部分。推入有效的目錄名。遇到 `..` 則彈出。忽略 `.` 和空字串。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or coding:
在模擬面試或寫程式時使用此表：

- [ ] **Initialization:** Did I initialize the stack (list) correctly?
    **初始化：** 我是否正確初始化了堆疊（list）？
- [ ] **Empty Check:** Did I guard against `pop()` or `peek()` on an empty stack?
    **空檢查：** 我是否防範了對空堆疊執行 `pop()` 或 `peek()`？
- [ ] **Final State:** Did I check if the stack is empty at the end (for matching problems)?
    **最終狀態：** 我是否檢查了結束時堆疊是否為空（針對匹配問題）？
- [ ] **Type Consistency:** Am I pushing and comparing consistent data types (chars vs strings)?
    **型別一致性：** 我推入和比較的資料型別是否一致（字元 vs 字串）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The "Ctrl+Z" Mental Model:**
    **「Ctrl+Z」心智模型：**
    Every time you type, you push a state. When you hit Undo (Ctrl+Z), you pop the last state.
    每次打字，你推入一個狀態。當你按復原（Ctrl+Z），你彈出最後一個狀態。

*   **The "Pringles Can":**
    **「品客洋芋片罐」：**
    You can only eat the chip at the very top. To get to the bottom chip, you must eat all the ones above it.
    你只能吃最上面的洋芋片。要拿到最底下的，你必須先吃掉上面所有的。

*   **Visual Anchor:**
    **視覺錨點：**
    ```text
      |     |  <-- Push / Pop here (在此進出)
      |  C  |
      |  B  |
      |__A__|
    ```