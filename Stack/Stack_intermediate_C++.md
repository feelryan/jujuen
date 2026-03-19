Here is the comprehensive study guide for **Stack (Intermediate)**, tailored for a Senior Software Engineer transitioning to C++.

這是一份針對 **Stack（堆疊 - 中階）** 的完整教材，專為準備轉向 C++ 的資深軟體工程師量身打造。

---

# Data Structure Module: Stack (Intermediate)
# 資料結構模組：堆疊（中階）

## 1. Learning Objectives (學習目標)

1.  **Master the Monotonic Stack Pattern:** Understand how to solve "Next Greater Element" type problems in $O(N)$ time.
    **掌握單調堆疊（Monotonic Stack）模式：** 理解如何在 $O(N)$ 時間內解決「下一個更大元素」類型的問題。
2.  **Proficiency in C++ STL Stack:** Transition from Python lists to C++ `std::stack` and `std::vector`, understanding the API differences (especially `pop()` return types).
    **熟練 C++ STL Stack：** 從 Python 列表轉換到 C++ `std::stack` 與 `std::vector`，理解 API 差異（特別是 `pop()` 的回傳類型）。
3.  **Complex Parsing & Simulation:** Use stacks to handle nested structures (parentheses, expressions) and simulate recursion.
    **複雜解析與模擬：** 使用堆疊處理巢狀結構（括號、表達式）並模擬遞迴。
4.  **Space Complexity Optimization:** Learn when a stack is necessary versus when pointers or counters suffice.
    **空間複雜度優化：** 學習何時必須使用堆疊，何時僅需指標或計數器即可。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Stack is a linear data structure following the **LIFO (Last In, First Out)** principle.
堆疊是一種遵循 **LIFO（後進先出）** 原則的線性資料結構。

### C++ Implementation (C++ 實作)
In C++, we typically use `<stack>` adapter or `std::vector`.
在 C++ 中，我們通常使用 `<stack>` 適配器或 `std::vector`。

*   **Key Difference from Python:** In Python, `list.pop()` returns the element. In C++, `std::stack::pop()` returns `void`. You must call `top()` to see the value before popping.
    **與 Python 的關鍵差異：** 在 Python 中，`list.pop()` 會回傳該元素。在 C++ 中，`std::stack::pop()` 回傳 `void`。你必須在彈出前呼叫 `top()` 來查看數值。

### Complexity (複雜度)
*   **Push/Pop/Top:** $O(1)$
    **推入/彈出/查看頂端：** $O(1)$
*   **Search:** $O(N)$
    **搜尋：** $O(N)$

### When to Use (適用場景)
1.  **Processing Nested Structures:** Parsing JSON, XML, or code syntax (parentheses matching).
    **處理巢狀結構：** 解析 JSON、XML 或程式語法（括號匹配）。
2.  **Reversing Data:** Palindromes or reversing strings.
    **反轉資料：** 回文或反轉字串。
3.  **Tracking State (DFS):** Simulating recursion iteratively.
    **追蹤狀態（DFS）：** 以迭代方式模擬遞迴。
4.  **Order Dependency (Monotonic Stack):** Finding the nearest larger/smaller element.
    **順序依賴（單調堆疊）：** 尋找最近的較大/較小元素。

### When NOT to Use (不適用場景)
1.  **Random Access Needed:** If you need to access the $k$-th element, use `std::vector`.
    **需要隨機存取：** 如果你需要存取第 $k$ 個元素，請使用 `std::vector`。
2.  **FIFO Requirements:** Use `std::queue` for breadth-first scenarios.
    **先進先出需求：** 對於廣度優先場景，請使用 `std::queue`。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Monotonic Stack (單調堆疊)
**Concept:** Maintain a stack where elements are always sorted (increasing or decreasing).
**觀念：** 維護一個堆疊，其中的元素始終保持排序（遞增或遞減）。
**Use Case:** "Find the next greater element for every element in an array."
**應用場景：** 「找出陣列中每個元素的下一個更大元素。」

### B. Parenthesis Matching / String Parsing (括號匹配 / 字串解析)
**Concept:** Push opening brackets; pop and check when encountering closing brackets.
**觀念：** 遇到左括號推入；遇到右括號時彈出並檢查匹配。
**Use Case:** Valid Parentheses, Decode String (e.g., `3[a]2[bc]`).
**應用場景：** 有效括號、解碼字串（如 `3[a]2[bc]`）。

### C. Expression Evaluation (表達式求值)
**Concept:** Use two stacks (operands and operators) or convert to Reverse Polish Notation (Postfix).
**觀念：** 使用兩個堆疊（運算元與運算子）或轉換為逆波蘭表示法（後綴表達式）。
**Use Case:** Basic Calculator implementation.
**應用場景：** 實作基本計算機。

---

## 4. Example Walkthrough (範例講解)

### Problem: Daily Temperatures (LeetCode 739)
**問題：每日溫度**

### Problem Statement (問題重述)
Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i`th day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0`.
給定一個整數陣列 `temperatures` 代表每日溫度，回傳一個陣列 `answer`，其中 `answer[i]` 是在第 `i` 天之後，你需要等待多少天才能獲得更溫暖的溫度。如果未來沒有這樣的一天，則保持 `answer[i] == 0`。

### Approach 1: Brute Force (暴力解)
For each day, iterate through all future days to find the first one that is warmer.
對於每一天，遍歷未來的所有天數，找出第一個更溫暖的日子。

*   **Time Complexity:** $O(N^2)$ — Unacceptable for large $N$ (e.g., $N=10^5$).
    **時間複雜度：** $O(N^2)$ — 對於大的 $N$（如 $N=10^5$）是不可接受的。

### Approach 2: Monotonic Decreasing Stack (Optimal) (單調遞減堆疊 - 最佳解)
**Intuition:** We want to know the "Next Greater Element". We can maintain a stack of indices representing temperatures that haven't found a warmer day yet.
**直覺：** 我們想知道「下一個更大元素」。我們可以維護一個索引堆疊，代表尚未找到更溫暖日子的溫度。

1.  Iterate through the array.
    遍歷陣列。
2.  While the current temperature is **greater** than the temperature at the index stored at the top of the stack:
    當前溫度 **大於** 堆疊頂端索引所對應的溫度時：
    *   It means we found the "warmer day" for the index at the top.
        這意味著我們找到了堆疊頂端索引的「更溫暖日子」。
    *   Pop the index, calculate the distance (`current_index - popped_index`), and store it.
        彈出該索引，計算距離（`current_index - popped_index`），並儲存。
3.  Push the current index onto the stack.
    將當前索引推入堆疊。
4.  The stack remains sorted in descending order of temperatures (Monotonic Decreasing).
    堆疊中的溫度保持遞減順序（單調遞減）。

*   **Time Complexity:** $O(N)$ — Each element is pushed once and popped at most once.
    **時間複雜度：** $O(N)$ — 每個元素被推入一次，且最多被彈出一次。
*   **Space Complexity:** $O(N)$ — For the stack.
    **空間複雜度：** $O(N)$ — 用於堆疊。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <stack>
#include <iostream>

class Solution {
public:
    std::vector<int> dailyTemperatures(std::vector<int>& temperatures) {
        int n = temperatures.size();
        // Initialize result vector with 0s
        // 初始化結果向量，預設為 0
        std::vector<int> result(n, 0);
        
        // Stack stores indices, not values!
        // 堆疊儲存的是索引，而非數值！
        std::stack<int> st; 

        for (int i = 0; i < n; ++i) {
            // Check if current temp is warmer than the temp at stack's top index
            // 檢查當前溫度是否比堆疊頂端索引對應的溫度更暖
            while (!st.empty() && temperatures[i] > temperatures[st.top()]) {
                int prevIndex = st.top();
                st.pop(); // In C++, pop() returns void. C++ 中 pop() 回傳 void
                
                // Calculate the wait days
                // 計算等待天數
                result[prevIndex] = i - prevIndex;
            }
            
            // Push current index to wait for a warmer day
            // 推入當前索引以等待更溫暖的日子
            st.push(i);
        }
        
        return result;
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Storing Value vs. Index** | **Critical:** In Monotonic Stack problems, usually store the **index**, not the value, because you need to calculate distance. <br> **關鍵：** 在單調堆疊問題中，通常儲存 **索引** 而非數值，因為你需要計算距離。 |
| **C++ `pop()` Behavior** | Unlike Python, `st.pop()` removes the element but does **not** return it. Access it with `st.top()` first. <br> 不同於 Python，`st.pop()` 移除元素但 **不** 回傳它。請先用 `st.top()` 存取。 |
| **Empty Stack Check** | Always check `!st.empty()` before calling `top()` or `pop()`. Accessing an empty stack causes a Segmentation Fault (Runtime Error). <br> 在呼叫 `top()` 或 `pop()` 前務必檢查 `!st.empty()`。存取空堆疊會導致區段錯誤（執行期錯誤）。 |
| **Strict vs. Non-Strict** | Be careful with `>` vs `>=`. Does "next greater" mean strictly greater? This determines when you pop. <br> 注意 `>` 與 `>=` 的區別。「下一個更大」是指嚴格大於嗎？這決定了你何時彈出。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the LIFO nature:** "Since we need to process the most recent elements first / find the nearest related element, a Stack is suitable."
    **識別 LIFO 特性：** 「由於我們需要優先處理最近的元素 / 尋找最近的相關元素，堆疊很合適。」
2.  **Define the Stack content:** "I will use a stack to store indices (or values) that we haven't resolved yet."
    **定義堆疊內容：** 「我將使用堆疊來儲存我們尚未解決的索引（或數值）。」
3.  **State Complexity:** "This allows us to process the array in one pass, giving us O(N) time complexity."
    **說明複雜度：** 「這允許我們一次遍歷處理陣列，提供 O(N) 的時間複雜度。」

### Whiteboard Strategy (白板策略)
*   **Draw the Stack:** Physically draw a vertical bucket. Write elements entering from the top.
    **畫出堆疊：** 實際畫一個垂直的桶子。寫下從頂部進入的元素。
*   **Trace an Example:** Use a small input (e.g., `[73, 74, 75, 71, 69, 72]`) and update the stack state step-by-step alongside the code.
    **追蹤範例：** 使用小型的輸入並在代碼旁逐步更新堆疊狀態。

### Common Follow-ups (常見追問)
*   **Q:** Can you do this without `std::stack`?
    **問：** 你能不使用 `std::stack` 做到嗎？
    *   **A:** Yes, use `std::vector` and `back()`, `push_back()`, `pop_back()`. It is often faster due to memory locality.
    *   **答：** 可以，使用 `std::vector` 搭配 `back()`、`push_back()`、`pop_back()`。由於記憶體局部性，這通常更快。

---

## 7. Practice Problems (練習題)

### Easy: Valid Parentheses (LeetCode 20)
**Hint:** Use a map to match closing brackets to opening brackets. Push openers, pop and check closers.
**提示：** 使用 map 將右括號對應到左括號。推入左括號，遇到右括號時彈出並檢查。
**Focus:** Basic stack operations and edge cases (e.g., `"]"`, `"(]"`).
**重點：** 基本堆疊操作與邊界情況（如 `"]"`, `"(]"`）。

### Medium: Asteroid Collision (LeetCode 735)
**Hint:** Iterate through asteroids. If current is moving right (`>0`), push. If moving left (`<0`), collide with stack top if top is moving right.
**提示：** 遍歷小行星。如果當前向右移動（`>0`），推入。如果向左移動（`<0`），且堆疊頂端向右移動，則發生碰撞。
**Focus:** Simulation logic and handling multiple collisions in a `while` loop.
**重點：** 模擬邏輯與在 `while` 迴圈中處理多次碰撞。

### Hard: Largest Rectangle in Histogram (LeetCode 84)
**Hint:** Monotonic Increasing Stack. When you see a bar shorter than the top, the top bar's range is determined. Pop and calculate area.
**提示：** 單調遞增堆疊。當你看到一個比頂端短的柱子時，頂端柱子的範圍就確定了。彈出並計算面積。
**Focus:** Advanced Monotonic Stack application. Handling boundaries (add 0 height at end).
**重點：** 進階單調堆疊應用。處理邊界（在末尾添加高度 0）。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
- [ ] **Empty Check:** Did I wrap `st.top()` and `st.pop()` with `!st.empty()` check?
  **空檢查：** 我是否在 `st.top()` 和 `st.pop()` 外包覆了 `!st.empty()` 檢查？
- [ ] **Return Type:** Did I remember that C++ `pop()` returns void?
  **回傳類型：** 我是否記得 C++ `pop()` 回傳 void？
- [ ] **Stack Content:** Am I storing the index or the value? (Index is usually more flexible).
  **堆疊內容：** 我存的是索引還是數值？（索引通常更有彈性）。
- [ ] **Leftovers:** After the loop, is there anything left in the stack that needs processing?
  **剩餘物：** 迴圈結束後，堆疊中是否還有需要處理的剩餘元素？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Dirty Plate" Analogy (髒盤子類比)
*   **LIFO:** You pile dirty plates in the sink. The last one you put on top is the first one you wash.
    **LIFO：** 你把髒盤子堆在水槽裡。你最後放上去的那個盤子是你第一個洗的。

### The "Looking Back" Analogy (Monotonic Stack) (回頭看類比 - 單調堆疊)
*   Imagine people standing in a line.
    想像人們排成一列。
*   **Next Greater:** Everyone looks to the right. If a taller person stands in front of you, they block your view. The stack maintains the people who are still "visible" (waiting for someone taller).
    **下一個更大：** 每個人都向右看。如果一個更高的人站在你前面，他會擋住你的視線。堆疊維護的是那些仍然「可見」的人（正在等待更高的人出現）。

---

**Final Note for the Senior Engineer:**
Transitioning to C++ for interviews requires muscle memory. Practice writing `std::stack<int> st;` and the `while (!st.empty())` loop until it feels as natural as `stack = []` in Python.
**給資深工程師的最後提示：**
為了面試轉換到 C++ 需要肌肉記憶。練習寫 `std::stack<int> st;` 和 `while (!st.empty())` 迴圈，直到它感覺像 Python 中的 `stack = []` 一樣自然。