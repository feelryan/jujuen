Here is the comprehensive guide for **Stack**, tailored for a Senior Software Engineer, following the requested bilingual format and Java implementation.

這是一份針對資深軟體工程師量身打造的 **Stack（堆疊）** 完整教材，遵循您要求的雙語格式與 Java 實作。

---

# Stack (Data Structure) - Beginner Level
# 堆疊（資料結構）- 初階篇

## 1. Learning Goals (學習目標)

*   **Master the LIFO Principle:** Understand the "Last-In, First-Out" mechanism and its physical analogies.
    **掌握 LIFO 原則：** 理解「後進先出」機制及其物理類比。
*   **Java Implementation Best Practices:** Learn why `Deque` is preferred over the legacy `Stack` class in Java.
    **Java 實作最佳實務：** 學習為何在 Java 中 `Deque` 優於傳統的 `Stack` 類別。
*   **Identify Stack Patterns:** Recognize problems involving nesting, reversing, or maintaining history.
    **識別堆疊模式：** 辨識涉及巢狀結構、反轉或維護歷史紀錄的問題。
*   **Analyze Complexity:** confidently assess time and space complexity for basic stack operations.
    **分析複雜度：** 自信地評估基本堆疊操作的時間與空間複雜度。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A Stack is a linear data structure that follows a particular order in which the operations are performed: **LIFO** (Last In First Out).
堆疊是一種線性資料結構，遵循特定的操作順序：**LIFO**（後進先出）。

### Intuition (直覺)
Think of a stack of plates in a cafeteria. You can only take the top plate, and you can only add a new plate to the top.
想像自助餐廳裡的一疊盤子。你只能拿取最上面的盤子，也只能將新盤子放到最上面。

### Complexity (複雜度)

| Operation | Time Complexity (時間複雜度) | Notes (備註) |
| :--- | :--- | :--- |
| **Push (Add)** | $O(1)$ | No shifting of elements required. (無需移動元素) |
| **Pop (Remove)** | $O(1)$ | Removing from the top is instant. (從頂部移除是即時的) |
| **Peek (Top)** | $O(1)$ | Viewing the top element. (查看頂部元素) |
| **Search** | $O(N)$ | In worst case, you must pop everything to find an item. (最壞情況下需彈出所有元素才能找到) |

### Use Cases (適用場景)
*   **Function Call Stack:** Managing recursion and function execution contexts.
    **函式呼叫堆疊：** 管理遞迴與函式執行上下文。
*   **Undo/Redo Mechanisms:** Storing history of operations.
    **復原/重做機制：** 儲存操作歷史。
*   **Parsing/Syntax Analysis:** Validating parentheses, evaluating expressions (RPN).
    **解析/語法分析：** 驗證括號、計算表達式（逆波蘭表示法）。
*   **Depth-First Search (DFS):** Iterative implementation of DFS involves a stack.
    **深度優先搜尋 (DFS)：** DFS 的迭代實作涉及堆疊。

### Not Suitable For (不適用場景)
*   **Random Access:** If you need to access elements by index (e.g., `get(i)`), use an Array or ArrayList.
    **隨機存取：** 如果你需要透過索引存取元素（如 `get(i)`），請使用陣列或 ArrayList。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Matching & Nesting (配對與巢狀結構):**
    *   Validating balanced parentheses `(([]))`.
    *   驗證平衡括號 `(([]))`。
2.  **Reversing Data (反轉資料):**
    *   Reversing a string or a linked list.
    *   反轉字串或鏈結串列。
3.  **Expression Evaluation (表達式計算):**
    *   Converting Infix to Postfix, or evaluating Reverse Polish Notation.
    *   將中序轉為後序，或計算逆波蘭表示法。
4.  **Monotonic Stack (單調堆疊) [Intermediate Preview]:**
    *   Finding the "Next Greater Element". (We will focus on basics here, but keep this in mind).
    *   尋找「下一個更大元素」。（我們在此專注於基礎，但請記住這一點）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Valid Parentheses (LeetCode 20)
### 問題：有效的括號

**Problem Statement (問題重述):**
Given a string `s` containing just the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid. Open brackets must be closed by the same type of brackets in the correct order.
給定一個僅包含字元 `(`, `)`, `{`, `}`, `[` 和 `]` 的字串 `s`，判斷輸入字串是否有效。開括號必須由相同類型的括號以正確順序閉合。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Repeatedly find adjacent matching pairs like `()` and remove them until the string is empty or no pairs remain.
    *   重複尋找相鄰的配對如 `()` 並將其移除，直到字串為空或沒有配對為止。
    *   *Complexity:* $O(N^2)$ due to string manipulation. (因字串操作導致效率低落)。

2.  **Optimal Approach: Stack (最佳解：堆疊):**
    *   Iterate through the string.
    *   遍歷字串。
    *   If we see an **opening** bracket, push it onto the stack.
    *   如果看到**開**括號，將其推入堆疊。
    *   If we see a **closing** bracket, check if the stack is empty or if the top element matches. If it matches, pop the stack; otherwise, it's invalid.
    *   如果看到**閉**括號，檢查堆疊是否為空或頂部元素是否匹配。若匹配則彈出堆疊；否則無效。
    *   Finally, the stack must be empty.
    *   最後，堆疊必須為空。

### Java Reference Solution (Java 參考解)

```java
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

public class ValidParentheses {
    
    public boolean isValid(String s) {
        // Use Map to store matching pairs for cleaner code
        // 使用 Map 儲存配對關係，使程式碼更整潔
        Map<Character, Character> map = new HashMap<>();
        map.put(')', '(');
        map.put('}', '{');
        map.put(']', '[');

        // Best Practice: Use Deque interface with ArrayDeque implementation
        // 最佳實務：使用 Deque 介面搭配 ArrayDeque 實作
        // Avoid using 'Stack' class as it is synchronized (slower) and legacy
        // 避免使用 'Stack' 類別，因為它是同步的（較慢）且為遺留類別
        Deque<Character> stack = new ArrayDeque<>();

        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);

            // If it is a closing bracket (key in map)
            // 如果是閉括號（Map 中的 key）
            if (map.containsKey(c)) {
                // Get the top element. If stack is empty, use a dummy value
                // 取得頂部元素。如果堆疊為空，使用虛擬值
                char topElement = stack.isEmpty() ? '#' : stack.pop();

                // Check if the top element matches the required opening bracket
                // 檢查頂部元素是否與所需的開括號匹配
                if (topElement != map.get(c)) {
                    return false;
                }
            } else {
                // It is an opening bracket, push to stack
                // 是開括號，推入堆疊
                stack.push(c);
            }
        }

        // If stack is empty, all brackets were matched correctly
        // 如果堆疊為空，表示所有括號皆正確匹配
        return stack.isEmpty();
    }
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ - We traverse the string once. Each push/pop is $O(1)$.
    **時間：** $O(N)$ - 我們遍歷字串一次。每次 push/pop 皆為 $O(1)$。
*   **Space:** $O(N)$ - In the worst case (e.g., `(((((`), we push all characters onto the stack.
    **空間：** $O(N)$ - 最壞情況下（如 `(((((`），我們將所有字元推入堆疊。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) |
| :--- | :--- |
| **Stack vs. Deque (Java)** | **Pitfall:** Using `java.util.Stack`. It inherits from `Vector` and is synchronized (thread-safe), causing performance overhead. <br> **Fix:** Always use `Deque<Integer> stack = new ArrayDeque<>();`. <br> **陷阱：** 使用 `java.util.Stack`。它繼承自 `Vector` 且是同步的（執行緒安全），會導致效能開銷。<br> **修正：** 總是使用 `Deque<Integer> stack = new ArrayDeque<>();`。 |
| **Empty Stack Exception** | **Pitfall:** Calling `.pop()` or `.peek()` on an empty stack throws an exception. <br> **Fix:** Always check `!stack.isEmpty()` before accessing. <br> **陷阱：** 在空堆疊上呼叫 `.pop()` 或 `.peek()` 會拋出例外。<br> **修正：** 存取前務必檢查 `!stack.isEmpty()`。 |
| **Stack Overflow** | **Pitfall:** In recursion, if the base case is missing, the call stack exceeds memory limits. <br> **陷阱：** 在遞迴中，若缺少基本情況（base case），呼叫堆疊將超出記憶體限制。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify LIFO:** "Since we need to process the most recent element first / match nested structures, a Stack is the natural choice."
    **識別 LIFO：** 「由於我們需要優先處理最近的元素 / 匹配巢狀結構，堆疊是自然的選擇。」
2.  **Discuss Implementation:** "I will use Java's `ArrayDeque` as a stack for better performance compared to the legacy `Stack` class."
    **討論實作：** 「我將使用 Java 的 `ArrayDeque` 作為堆疊，相較於傳統的 `Stack` 類別，它有更好的效能。」

### Whiteboard Strategy (白板策略)
*   **Draw the Stack:** Visually draw a vertical container. As you trace the code, write values inside and cross them out when popped.
    **畫出堆疊：** 視覺化地畫出一個垂直容器。當你追蹤程式碼時，將數值寫在裡面，彈出時將其劃掉。
*   **Edge Cases:** Explicitly write down "Empty Input", "Single Element", "No Matches" on the side.
    **邊界情況：** 在旁邊明確寫下「空輸入」、「單一元素」、「無匹配」。

### Common Follow-ups (常見追問)
*   **Q:** How would you implement a Stack using an Array?
    **問：** 你如何使用陣列實作堆疊？
    *   *A:* Handle resizing (doubling capacity) when full.
    *   *答：* 當陣列滿時處理重新調整大小（容量加倍）。
*   **Q:** How to make it thread-safe?
    **問：** 如何使其執行緒安全？
    *   *A:* Use `ConcurrentLinkedDeque` or explicit locking.
    *   *答：* 使用 `ConcurrentLinkedDeque` 或顯式鎖定。

---

## 7. Practice Problems (練習題)

### 1. Easy: Min Stack (最小堆疊)
*   **Desc:** Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
    **描述：** 設計一個支援 push、pop、top，並能在常數時間內檢索最小元素的堆疊。
*   **Hint:** Use two stacks (one for data, one for current minimum) or store pairs/deltas.
    **提示：** 使用兩個堆疊（一個存資料，一個存當前最小值）或儲存數對/差值。

### 2. Medium: Evaluate Reverse Polish Notation (計算逆波蘭表示法)
*   **Desc:** Evaluate the value of an arithmetic expression in Reverse Polish Notation (e.g., `["2","1","+","3","*"]` -> `(2+1)*3` -> `9`).
    **描述：** 計算逆波蘭表示法中的算術表達式值。
*   **Hint:** Push numbers; when seeing an operator, pop two numbers, calculate, and push result back.
    **提示：** 推入數字；看到運算子時，彈出兩個數字，計算後將結果推回。

### 3. Hard (for Beginner topic): Decode String (解碼字串)
*   **Desc:** Given `3[a]2[bc]`, return `aaabcbc`. Involves nested brackets.
    **描述：** 給定 `3[a]2[bc]`，回傳 `aaabcbc`。涉及巢狀括號。
*   **Hint:** Use two stacks: one for repeat counts, one for built strings. Handle nested cases recursively or iteratively.
    **提示：** 使用兩個堆疊：一個存重複次數，一個存已建立的字串。以遞迴或迭代方式處理巢狀情況。

---

## 8. Quick Checklist (快速檢核表)

*   [ ] **Empty Check:** Did I handle the case where `pop()` is called on an empty stack?
    **空檢查：** 我是否處理了在空堆疊上呼叫 `pop()` 的情況？
*   [ ] **Return Value:** Does the problem require returning the stack content or a boolean?
    **回傳值：** 問題要求回傳堆疊內容還是布林值？
*   [ ] **Type Safety:** Am I pushing the correct type (e.g., Index vs. Value)?
    **型別安全：** 我是否推入了正確的型別（例如：索引 vs 數值）？
*   [ ] **Leftovers:** After the loop, is the stack supposed to be empty? (Crucial for validation problems).
    **剩餘物：** 迴圈結束後，堆疊應該是空的嗎？（對驗證類問題至關重要）。

---

## 9. Memory Anchors (記憶錨點)

*   **The "Ctrl+Z" Mental Model:**
    Every time you type, you **push** a state. When you hit Ctrl+Z (Undo), you **pop** the most recent state.
    **「Ctrl+Z」心智模型：** 每次打字時，你 **push** 一個狀態。當你按 Ctrl+Z（復原）時，你 **pop** 最近的狀態。
*   **The Pringles Can (洋芋片罐):**
    You can only eat the chip at the top. To get to the bottom chip, you must eat all the ones above it.
    **洋芋片罐：** 你只能吃最上面的洋芋片。要拿到最底下的洋芋片，必須先吃掉上面所有的。