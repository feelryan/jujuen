Here is the comprehensive study guide for **Stack**, tailored for a Senior Software Engineer, adjusted to the **Beginner** level (focusing on fundamentals and standard library mastery), and written in **C++**.

---

# Data Structure Module: Stack (Beginner Level)
# 資料結構模組：堆疊（初階）

## 1. Learning Objectives (學習目標)

1.  **Master C++ STL Stack Operations**: Understand the specific API differences between C++ `std::stack` and Python lists or JS arrays (e.g., `top()` vs `pop()`).
    **掌握 C++ STL 堆疊操作**：理解 C++ `std::stack` 與 Python lists 或 JS arrays 之間的 API 差異（例如 `top()` 與 `pop()` 的區別）。

2.  **Internalize LIFO Logic**: deeply understand the Last-In, First-Out principle and identify problems requiring "reverse processing" or "pairing".
    **內化後進先出（LIFO）邏輯**：深刻理解「後進先出」原則，並識別需要「反向處理」或「配對」的問題。

3.  **Handle Edge Cases Robustly**: Learn to prevent common runtime errors like accessing `top()` on an empty stack.
    **穩健處理邊界情況**：學會防止常見的執行期錯誤，例如在空堆疊上呼叫 `top()`。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Stack is a linear data structure that follows the LIFO (Last-In, First-Out) order.
堆疊是一種遵循 LIFO（後進先出）順序的線性資料結構。

Imagine a stack of plates; you can only add or remove the top plate.
想像一疊盤子；你只能新增或移除最上面的盤子。

### Complexity (複雜度)

| Operation | Time Complexity (時間複雜度) | Space Complexity (空間複雜度) | Note (備註) |
| :--- | :--- | :--- | :--- |
| Push (Insert) | $O(1)$ | $O(1)$ | Amortized if using dynamic array backing. (若使用動態陣列底層則為均攤) |
| Pop (Remove) | $O(1)$ | $O(1)$ | Does not return value in C++. (在 C++ 中不回傳值) |
| Top (Peek) | $O(1)$ | $O(1)$ | Access element without removing. (存取元素但不移除) |
| Empty/Size | $O(1)$ | $O(1)$ | Check state. (檢查狀態) |

### When to Use (適用場景)
*   **Reverse Order Processing**: When you need to process data in the reverse order of its arrival (e.g., Undo features).
    **逆序處理**：當你需要以資料到達的相反順序進行處理時（例如：復原功能）。
*   **Matching/Pairing**: Balancing symbols like parentheses or HTML tags.
    **配對/平衡**：平衡符號，如括號或 HTML 標籤。
*   **Recursion Simulation**: Converting recursive algorithms (DFS) into iterative ones.
    **遞迴模擬**：將遞迴演算法（DFS）轉換為迭代算法。

### When NOT to Use (不適用場景)
*   **Random Access**: If you need to access the $k$-th element directly ($O(n)$ for stack).
    **隨機存取**：如果你需要直接存取第 $k$ 個元素（堆疊需要 $O(n)$）。
*   **FIFO Requirements**: Use a Queue instead for First-In, First-Out needs.
    **先進先出需求**：若需先進先出，請改用佇列（Queue）。

---

## 3. Typical Patterns (典型題型 / 模式)

Even at a beginner level, recognizing these patterns is crucial for Senior Engineers to quickly classify problems.
即使在初階程度，識別這些模式對於資深工程師快速分類問題至關重要。

1.  **Sequential Matching (序列配對)**
    *   Used for validating parentheses or formatting.
    *   用於驗證括號或格式。
2.  **String Reversal (字串反轉)**
    *   Using a stack to reverse characters or words.
    *   使用堆疊來反轉字元或單字。
3.  **Function Call Stack Simulation (函數呼叫堆疊模擬)**
    *   Handling nested structures or directory paths.
    *   處理巢狀結構或目錄路徑。

---

## 4. Example Walkthrough (範例講解)

### Problem: Valid Parentheses (LeetCode 20)
**問題：有效的括號**

Given a string `s` containing just the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.
給定一個僅包含字元 `(`, `)`, `{`, `}`, `[` 和 `]` 的字串 `s`，判斷輸入字串是否有效。

Input: `s = "()[]{}"` -> Output: `true`
Input: `s = "([)]"` -> Output: `false`

### Approach 1: Brute Force (Not Recommended)
**思路 1：暴力法（不推薦）**

Repeatedly find and replace adjacent pairs like `()`, `[]`, `{}` with an empty string until no more pairs exist.
重複尋找並將相鄰的配對如 `()`, `[]`, `{}` 替換為空字串，直到沒有配對為止。

*   **Complexity**: $O(n^2)$ because string replacement/shifting is expensive.
    **複雜度**：$O(n^2)$，因為字串替換/移位成本很高。

### Approach 2: Stack (Optimal)
**思路 2：堆疊（最佳解）**

Iterate through the string. If it's an opening bracket, push it onto the stack. If it's a closing bracket, check if it matches the top of the stack.
遍歷字串。如果是左括號，將其推入堆疊。如果是右括號，檢查它是否與堆疊頂部匹配。

*   **Time Complexity**: $O(n)$ - We traverse the string once.
    **時間複雜度**：$O(n)$ - 我們遍歷字串一次。
*   **Space Complexity**: $O(n)$ - Worst case, all are opening brackets.
    **空間複雜度**：$O(n)$ - 最壞情況下，全部都是左括號。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <stack>
#include <string>
#include <unordered_map>
#include <iostream>

class Solution {
public:
    bool isValid(std::string s) {
        // Use std::stack for LIFO behavior
        // 使用 std::stack 來實現後進先出行為
        std::stack<char> st;
        
        // Map for easy lookup of matching pairs
        // 使用 Map 以便輕鬆查找匹配對
        std::unordered_map<char, char> pairs = {
            {')', '('},
            {']', '['},
            {'}', '{'}
        };

        for (char c : s) {
            // If character is a closing bracket (exists in map keys)
            // 如果字元是右括號（存在於 map 的鍵中）
            if (pairs.count(c)) {
                // Check if stack is empty OR top doesn't match
                // 檢查堆疊是否為空 或者 頂部不匹配
                if (st.empty() || st.top() != pairs[c]) {
                    return false;
                }
                // Match found, pop the opening bracket
                // 找到匹配，彈出左括號
                st.pop();
            } else {
                // It's an opening bracket, push to stack
                // 是左括號，推入堆疊
                st.push(c);
            }
        }

        // Valid only if stack is empty (all opened brackets are closed)
        // 只有當堆疊為空時才有效（所有開啟的括號都已關閉）
        return st.empty();
    }
};
```

### Common Mistake (錯誤示範)

A common mistake for beginners is using a simple counter for each type of bracket.
初學者常見的錯誤是為每種類型的括號使用簡單的計數器。

*   **Why it fails**: `([)]` has 1 `(`, 1 `)`, 1 `[`, 1 `]`. Counters would say it's balanced, but the order is wrong.
    **為何錯誤**：`([)]` 擁有各一個 `(`, `)`, `[`, `]`。計數器會認為它是平衡的，但順序是錯的。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **`pop()` Return Value** | In Python, `pop()` returns the element. **In C++, `pop()` returns `void`.** You must call `top()` first to get the value. <br> 在 Python 中，`pop()` 回傳元素。**在 C++ 中，`pop()` 回傳 `void`。** 你必須先呼叫 `top()` 取得數值。 |
| **Empty Check** | Calling `top()` or `pop()` on an empty stack causes **Undefined Behavior** (usually a crash). Always check `!st.empty()` first. <br> 在空堆疊上呼叫 `top()` 或 `pop()` 會導致**未定義行為**（通常是崩潰）。務必先檢查 `!st.empty()`。 |
| **`std::vector` vs `std::stack`** | `std::stack` is a container adapter (wrapper). Sometimes using `std::vector` as a stack (via `push_back`/`pop_back`) is faster due to cache locality. <br> `std::stack` 是一個容器適配器（包裝器）。有時使用 `std::vector` 作為堆疊（透過 `push_back`/`pop_back`）因為快取局部性而更快。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (闡述口條框架)
1.  **Identify the LIFO nature**: "Since we need to process the most recent element first, a Stack is the natural choice."
    **識別 LIFO 本質**：「由於我們需要優先處理最近的元素，堆疊是自然的選擇。」
2.  **State the Invariant**: "The stack will always contain [unmatched opening brackets / pending operations]."
    **陳述不變性**：「堆疊將始終包含 [未匹配的左括號 / 待處理的操作]。」
3.  **Address Edge Cases**: "I will handle the case where the stack is empty before popping."
    **處理邊界情況**：「在彈出之前，我會處理堆疊為空的情況。」

### Whiteboard Strategy (白板策略)
*   Draw the stack vertically on the side to trace the algorithm.
    在旁邊垂直畫出堆疊來追蹤演算法。
*   Write `st.empty()` checks explicitly before writing `st.top()`.
    在寫 `st.top()` 之前，明確寫下 `st.empty()` 檢查。

---

## 7. Practice Problems (練習題)

### 1. Min Stack (Easy) - Design
**題目：最小堆疊（簡單）- 設計**
*   **Prompt**: Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
    **提示**：設計一個堆疊，支援 push、pop、top，並能在常數時間內檢索最小元素。
*   **Hint**: Use two stacks. One for data, one for keeping track of the minimums seen so far.
    **提示**：使用兩個堆疊。一個存資料，一個記錄目前為止看到的最小值。

### 2. Evaluate Reverse Polish Notation (Medium)
**題目：逆波蘭表達式求值（中等）**
*   **Prompt**: Evaluate the value of an arithmetic expression in Reverse Polish Notation (e.g., `["2","1","+","3","*"]` -> `(2+1)*3` -> `9`).
    **提示**：計算逆波蘭表示法中的算術表達式的值。
*   **Hint**: Push numbers. When seeing an operator, pop two numbers, calculate, and push the result back.
    **提示**：推入數字。當看到運算符時，彈出兩個數字，計算後將結果推回。

### 3. Simplify Path (Medium/Hard for Beginner)
**題目：簡化路徑（中等/對初學者偏難）**
*   **Prompt**: Given an absolute path for a Unix-style file system (e.g., `/a/./b/../../c/`), simplify it to the canonical path (`/c`).
    **提示**：給定 Unix 風格檔案系統的絕對路徑，將其簡化為規範路徑。
*   **Hint**: Split string by `/`. Push valid directory names. Pop for `..`. Ignore `.` and empty strings.
    **提示**：用 `/` 分割字串。推入有效的目錄名稱。遇到 `..` 則彈出。忽略 `.` 和空字串。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] Did I check `!st.empty()` before every `st.top()` or `st.pop()`?
      我是否在每次 `st.top()` 或 `st.pop()` 之前檢查了 `!st.empty()`？
- [ ] Do I understand that `pop()` returns `void` in C++?
      我是否理解 C++ 中 `pop()` 回傳 `void`？
- [ ] Are the types inside the stack consistent?
      堆疊內的型別是否一致？

### Complexity Check (複雜度確認)
- [ ] Is the time complexity $O(n)$? (Usually we touch each element twice: push once, pop once).
      時間複雜度是 $O(n)$ 嗎？（通常我們接觸每個元素兩次：一次推入，一次彈出）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **The "Stack of Plates"**: You wash a plate and put it on top. You dry a plate by taking it from the top. The bottom plate waits the longest.
    **「一疊盤子」**：你洗好一個盤子放在最上面。你從最上面拿一個盤子去擦乾。最底下的盤子等最久。
*   **"Browser Back Button"**: The browser history is a stack. Current page is top. Clicking back pops the current page and shows the new top.
    **「瀏覽器上一頁按鈕」**：瀏覽器歷史記錄是一個堆疊。當前頁面在頂部。點擊上一頁會彈出當前頁面並顯示新的頂部。
*   **C++ API**: **"Peek before you Pop"**. You must look (`top`) before you remove (`pop`) if you want the data.
    **C++ API**：**「彈出前先偷看」**。如果你想要資料，必須在移除（`pop`）之前先看（`top`）。