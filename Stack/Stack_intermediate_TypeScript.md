# Stack (Intermediate Level)
# 堆疊（中階深度）

## 1. Learning Objectives (學習目標)

*   **Master the Monotonic Stack pattern for $O(N)$ optimizations.**
    掌握單調堆疊（Monotonic Stack）模式，以實現 $O(N)$ 的時間複雜度優化。
*   **Handle nested structures and parsing logic efficiently.**
    高效處理巢狀結構與解析邏輯（如括號匹配、表達式求值）。
*   **Understand the implicit stack in recursion and convert to iterative solutions.**
    理解遞迴中的隱式堆疊，並能將其轉換為迭代解法。
*   **Design stack-based classes with specific constraints (e.g., Min Stack).**
    設計具有特定限制的基於堆疊的類別（例如：最小堆疊）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)
*   **Definition:** A linear data structure following the Last-In, First-Out (LIFO) principle.
    **定義：** 一種遵循「後進先出」（LIFO）原則的線性資料結構。
*   **Intuition:** Think of it as a stack of plates or the "Undo" button in an editor; you interact only with the top element.
    **直覺：** 把它想像成一疊盤子或編輯器中的「復原」按鈕；你只能與最頂端的元素互動。

### Complexity (複雜度)
*   **Time:** `push` (add), `pop` (remove), `peek` (view top) are all $O(1)$. Searching is $O(N)$.
    **時間：** `push`（新增）、`pop`（移除）、`peek`（查看頂端）皆為 $O(1)$。搜尋則為 $O(N)$。
*   **Space:** $O(N)$ to store elements.
    **空間：** 儲存元素需 $O(N)$。

### Use Cases (適用場景)
*   **Processing Nested Structures:** JSON parsing, HTML tag matching, arithmetic expression evaluation.
    **處理巢狀結構：** JSON 解析、HTML 標籤匹配、算術表達式求值。
*   **"Next Greater/Smaller Element":** Finding the nearest element that satisfies a condition (Monotonic Stack).
    **「下一個更大/更小元素」：** 尋找最近且滿足特定條件的元素（單調堆疊）。
*   **Depth-First Search (DFS):** Iterative implementation of graph traversals.
    **深度優先搜尋（DFS）：** 圖形遍歷的迭代實作。

### When NOT to use (不適用場景)
*   **Random Access:** If you need to access the $k$-th element frequently, use an Array.
    **隨機存取：** 如果你需要頻繁存取第 $k$ 個元素，請使用陣列。
*   **FIFO Requirements:** If order needs to be preserved like a queue line, use a Queue.
    **先進先出需求：** 如果需要像排隊一樣保留順序，請使用佇列（Queue）。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Matching & Parsing (配對與解析):**
    *   Valid Parentheses, Simplify Path, Evaluate Reverse Polish Notation.
    *   有效括號、簡化路徑、逆波蘭表示法求值。
2.  **Monotonic Stack (單調堆疊):**
    *   Maintains elements in increasing or decreasing order to find the "next greater/smaller element" in linear time.
    *   維持元素遞增或遞減的順序，以便在線性時間內找到「下一個更大/更小的元素」。
    *   *Examples:* Daily Temperatures, Largest Rectangle in Histogram.
    *   *範例：* 每日溫度、直方圖中的最大矩形。
3.  **String Decoding / Simulation (字串解碼/模擬):**
    *   Handling nested commands like `3[a2[c]]`.
    *   處理巢狀指令，如 `3[a2[c]]`。

---

## 4. Example Walkthrough (範例講解)

### Problem: Daily Temperatures (每日溫度)
**Problem Statement:** Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0`.
**問題重述：** 給定一個整數陣列 `temperatures` 代表每日溫度，請回傳一個陣列 `answer`，其中 `answer[i]` 是第 `i` 天之後需要等待多少天才能遇到更溫暖的氣溫。如果未來沒有這一天，則 `answer[i] == 0`。

### Approach (思路)

#### 1. Brute Force (暴力解)
*   For each day `i`, iterate through all future days `j > i` to find the first one where `T[j] > T[i]`.
    對於每一天 `i`，遍歷所有未來的天數 `j > i`，找到第一個 `T[j] > T[i]` 的日子。
*   **Complexity:** Time $O(N^2)$, Space $O(1)$. This will TLE (Time Limit Exceeded) on large inputs.
    **複雜度：** 時間 $O(N^2)$，空間 $O(1)$。這在大數據輸入時會超時（TLE）。

#### 2. Optimization: Monotonic Stack (優化：單調堆疊)
*   **Intuition:** We need to find the *next greater element*. We can maintain a stack of indices representing days whose "warmer future day" hasn't been found yet.
    **直覺：** 我們需要尋找「下一個更大的元素」。我們可以維護一個索引堆疊，代表那些尚未找到「未來更暖日子」的天數。
*   **Invariant:** The stack should always be **monotonically decreasing** (based on temperature values). Why? Because if we see a temperature higher than the stack top, it means we found the "warmer day" for the stack top.
    **不變性：** 堆疊應始終保持（基於溫度值的）**單調遞減**。為什麼？因為如果我們遇到一個比堆疊頂端更高的溫度，這意味著我們找到了堆疊頂端那一天的「更暖日子」。

### Code Implementation (TypeScript)

```typescript
function dailyTemperatures(temperatures: number[]): number[] {
    const n = temperatures.length;
    // Initialize result array with 0s
    // 初始化結果陣列為 0
    const result: number[] = new Array(n).fill(0);
    
    // Stack stores indices, not values
    // 堆疊儲存的是索引，而非數值
    const stack: number[] = [];

    for (let i = 0; i < n; i++) {
        const currentTemp = temperatures[i];

        // While stack is not empty AND current temp is warmer than the temp at stack top
        // 當堆疊不為空 且 當前氣溫比堆疊頂端的氣溫更暖時
        while (stack.length > 0 && currentTemp > temperatures[stack[stack.length - 1]]) {
            // Pop the index of the colder day
            // 彈出較冷日子的索引
            const prevIndex = stack.pop()!;
            
            // Calculate the difference in days
            // 計算天數差
            result[prevIndex] = i - prevIndex;
        }

        // Push current index to stack to wait for a warmer day
        // 將當前索引推入堆疊，等待更暖的日子
        stack.push(i);
    }

    return result;
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. Each element is pushed onto the stack once and popped at most once.
    **時間：** $O(N)$。每個元素只會被推入堆疊一次，且最多被彈出一次。
*   **Space:** $O(N)$. In the worst case (strictly decreasing temperatures), the stack holds all indices.
    **空間：** $O(N)$。在最差情況下（溫度嚴格遞減），堆疊會保存所有索引。

### Common Mistakes (錯誤示範)
*   **Storing values instead of indices:** If you store the temperature value `73`, you lose the information about *when* it happened, making it impossible to calculate the distance `i - prevIndex`.
    **儲存數值而非索引：** 如果你只存溫度值 `73`，你會丟失它發生的*時間*資訊，導致無法計算距離 `i - prevIndex`。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Monotonic Increasing vs. Decreasing**<br>單調遞增 vs. 遞減 | **Increasing Stack:** Finds next *smaller* element.<br>**Decreasing Stack:** Finds next *greater* element.<br>**遞增堆疊：** 找下一個*更小*元素。<br>**遞減堆疊：** 找下一個*更大*元素。 |
| **Stack Empty Check**<br>堆疊為空檢查 | Always check `stack.length > 0` before accessing `stack[stack.length - 1]`. In TS, accessing an empty array index returns `undefined`, which can break logic.<br>在存取堆疊頂端前務必檢查 `stack.length > 0`。在 TS 中，存取空陣列索引會回傳 `undefined`，這可能會破壞邏輯。 |
| **Array as Stack**<br>陣列作為堆疊 | In TypeScript/JS, `push()` and `pop()` are efficient (amortized $O(1)$). Do not use `shift()`/`unshift()` as they are $O(N)$.<br>在 TypeScript/JS 中，`push()` 和 `pop()` 是高效的（均攤 $O(1)$）。切勿使用 `shift()`/`unshift()`，因為它們是 $O(N)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the LIFO nature:** "Since we need to process the most recent unmatched parenthesis/element first, a Stack is suitable."
    **確認 LIFO 特性：** 「由於我們需要優先處理最近一個未匹配的括號/元素，因此堆疊很適合。」
2.  **Define the Invariant:** "I will maintain a monotonic decreasing stack to keep track of elements waiting for a greater value."
    **定義不變性：** 「我將維護一個單調遞減堆疊，用來追蹤那些正在等待更大數值的元素。」
3.  **Trace with an example:** Draw the stack state at each iteration on the whiteboard.
    **用範例追蹤：** 在白板上畫出每次迭代時的堆疊狀態。

### Whiteboard Strategy (白板策略)
*   Draw a vertical "bucket" or a horizontal list with a pointer indicating the `TOP`.
    畫一個垂直的「桶子」或一個水平列表，並用指標標示 `TOP`。
*   When tracing recursion, explicitly draw the "Call Stack" to show you understand the underlying mechanism.
    在追蹤遞迴時，明確畫出「呼叫堆疊（Call Stack）」，顯示你理解底層機制。

### Common Follow-ups (常見追問)
*   **Q:** How to implement a Stack using Queues? (Or vice versa)
    **問：** 如何使用佇列（Queue）來實作堆疊？（反之亦然）
*   **Q:** What if the input is a continuous stream? (Online algorithm)
    **問：** 如果輸入是連續的串流怎麼辦？（線上演算法）
*   **Q:** What if stack depth is limited? (Recursion depth limit)
    **問：** 如果堆疊深度有限制怎麼辦？（遞迴深度限制）

---

## 7. Practice Problems (練習題)

### 1. Easy: Valid Parentheses (有效括號)
*   **Prompt:** Given a string containing `(`, `)`, `{`, `}`, `[`, `]`, determine if it is valid.
    **題目：** 給定包含 `(`, `)`, `{`, `}`, `[`, `]` 的字串，判斷其是否有效。
*   **Hint:** Use a map for matching pairs. Push openers, pop and check closers.
    **提示：** 使用 Map 來匹配對應關係。遇到左括號推入，遇到右括號彈出並檢查。

### 2. Medium: Min Stack (最小堆疊)
*   **Prompt:** Design a stack that supports `push`, `pop`, `top`, and retrieving the minimum element in constant time.
    **題目：** 設計一個堆疊，支援 `push`、`pop`、`top`，並能在常數時間內取得最小元素。
*   **Hint:** Use two stacks. One for data, one for keeping the current minimum at that level.
    **提示：** 使用兩個堆疊。一個存資料，另一個存該層級對應的當前最小值。

### 3. Hard: Largest Rectangle in Histogram (直方圖中的最大矩形)
*   **Prompt:** Given an array of integers representing histogram bar heights, find the area of the largest rectangle.
    **題目：** 給定一個整數陣列代表直方圖的高度，找出最大矩形的面積。
*   **Hint:** Monotonic Increasing Stack. When you pop a bar, that bar is the "height", the current index is the "right boundary", and the new stack top is the "left boundary".
    **提示：** 單調遞增堆疊。當你彈出一個長條時，該長條為「高度」，當前索引為「右邊界」，新的堆疊頂端為「左邊界」。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Empty Check:** Did I handle the case where `pop()` or `peek()` is called on an empty stack?
    **空檢查：** 我是否處理了對空堆疊呼叫 `pop()` 或 `peek()` 的情況？
*   [ ] **Leftovers:** After the loop, are there elements remaining in the stack that need processing? (Crucial for Monotonic Stack).
    **剩餘元素：** 迴圈結束後，堆疊中是否還有需要處理的剩餘元素？（對單調堆疊至關重要）。
*   [ ] **Types:** Are you pushing indices (`number`) or values (`T`)? Don't mix them up.
    **型別：** 你推入的是索引（`number`）還是數值（`T`）？不要混淆。
*   [ ] **Complexity:** Is the solution strictly $O(N)$? (Ensure inner `while` loops don't re-scan processed elements redundantly).
    **複雜度：** 解法是否嚴格為 $O(N)$？（確保內部 `while` 迴圈不會多餘地重新掃描已處理的元素）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **The "Dirty Plates" Analogy:**
    **「髒盤子」類比：**
    You can only wash the top plate. If you put a new dirty plate on top, you must wash that one before reaching the ones below.
    你只能洗最上面的盤子。如果你放了一個新的髒盤子在上面，你必須先洗那個，才能接觸到下面的盤子。

*   **Monotonic Stack = "The Skyline View":**
    **單調堆疊 = 「天際線視野」：**
    Imagine people standing in a line.
    *   **Decreasing Stack:** Like looking to the right. A tall person blocks the view of shorter people behind them. The stack keeps the people who can still "see" the future.
    *   **遞減堆疊：** 就像向右看。高個子會擋住後面矮個子的視線。堆疊保留了那些仍然能「看見」未來的人。