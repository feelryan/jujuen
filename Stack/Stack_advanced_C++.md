Here is the comprehensive guide for **Stack (Advanced Level)**, tailored for a Senior Software Engineer, using C++ as the implementation language.

這是一份針對 **Stack（進階級別）** 的完整教材，專為資深軟體工程師量身打造，並使用 C++ 作為實作語言。

---

# Advanced Data Structures: Stack (單調堆疊與複雜解析)

## 1. Learning Goals（學習目標）

1.  **Master Monotonic Stacks:** Understand how to optimize $O(N^2)$ problems involving "Next Greater/Smaller Element" to $O(N)$.
    **掌握單調堆疊：** 理解如何將涉及「下一個更大/更小元素」的 $O(N^2)$ 問題優化至 $O(N)$。
2.  **Handle Complex Parsing:** Solve expression evaluation and nested structure problems using multiple stacks or recursion simulation.
    **處理複雜解析：** 使用多個堆疊或遞迴模擬來解決表達式評估與巢狀結構問題。
3.  **Bridge Theory and Practice:** Translate abstract stack properties into solutions for geometric problems (e.g., Histograms, Trapping Rain Water).
    **連結理論與實務：** 將抽象的堆疊特性轉化為幾何問題的解法（例如直方圖、接雨水問題）。
4.  **C++ STL Proficiency:** Utilize `std::stack`, `std::vector` (as stack), and `std::deque` efficiently with modern C++ semantics.
    **精通 C++ STL：** 有效利用 `std::stack`、`std::vector`（作為堆疊）以及 `std::deque`，並結合現代 C++ 語意。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
While a basic stack is LIFO (Last-In, First-Out), an **Advanced Stack** usage often acts as a "buffer of postponed decisions."
雖然基礎堆疊是 LIFO（後進先出），但 **進階堆疊** 的用法通常充當「延遲決策的緩衝區」。

We keep elements in the stack because we don't have enough information to process them yet; we process them once a "trigger" element appears.
我們將元素保留在堆疊中，是因為尚未有足夠的資訊來處理它們；一旦「觸發」元素出現，我們便會進行處理。

### Complexity（複雜度）
- **Time:** $O(1)$ for push/pop. In Monotonic Stacks, each element is pushed and popped at most once, resulting in amortized $O(N)$ time.
  **時間：** push/pop 為 $O(1)$。在單調堆疊中，每個元素最多進出一次，因此攤銷時間為 $O(N)$。
- **Space:** $O(N)$ in the worst case (e.g., strictly increasing input for a decreasing stack).
  **空間：** 最差情況下為 $O(N)$（例如遞減堆疊遇到嚴格遞增的輸入）。

### When to Use (Advanced)（適用場景 - 進階）
- **Range Queries based on Value:** Finding the nearest element larger/smaller than current.
  **基於數值的範圍查詢：** 尋找比當前元素更大/更小的最近元素。
- **Parsing/Validation:** Compilers, calculators, XML/JSON parsing.
  **解析/驗證：** 編譯器、計算機、XML/JSON 解析。
- **Recursion Removal:** Converting DFS or recursive algorithms to iterative ones to avoid stack overflow.
  **消除遞迴：** 將 DFS 或遞迴演算法轉換為迭代式，以避免堆疊溢位。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Monotonic Stack (單調堆疊)
Maintains elements in sorted order (increasing or decreasing). Used for "Next Greater Element" or "Largest Rectangle".
維持元素處於排序狀態（遞增或遞減）。用於「下一個更大元素」或「最大矩形」。

### B. Parenthesis/Tag Matching (括號/標籤匹配)
Handling nested structures where the most recent open tag must be closed first.
處理巢狀結構，其中最近開啟的標籤必須最先關閉。

### C. Calculator / Expression Evaluation (計算機 / 表達式評估)
Using two stacks (operands and operators) or converting Infix to Postfix (Reverse Polish Notation).
使用兩個堆疊（運算元與運算子）或將中序轉換為後序（逆波蘭表示法）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Largest Rectangle in Histogram (LeetCode 84)
**問題：直方圖中的最大矩形**

#### Problem Statement（問題重述）
Given an array of integers `heights` representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
給定一個整數陣列 `heights` 代表直方圖的長條高度，其中每個長條的寬度為 1，請回傳直方圖中最大矩形的面積。

#### Approach: From Brute Force to Optimal（思路：從暴力到最佳解）

1.  **Brute Force ($O(N^2)$):**
    For each bar, expand to the left and right as long as the neighbors are taller. Calculate width $\times$ height.
    **暴力解：** 對於每個長條，只要鄰居較高就向左和向右擴展。計算 寬度 $\times$ 高度。
    *Why it fails:* Too slow for $N=10^5$.
    *為何失敗：* 對於 $N=10^5$ 來說太慢。

2.  **Optimal Strategy - Monotonic Stack ($O(N)$):**
    We need to find the **first smaller element** to the left and to the right for every bar. These boundaries determine the width.
    **最佳策略 - 單調堆疊：** 我們需要為每個長條找到左邊和右邊的 **第一個更小元素**。這些邊界決定了寬度。

    *   Maintain a stack of **indices** with increasing heights.
        維護一個存儲 **索引** 的堆疊，且對應的高度遞增。
    *   When we see a bar `h[i]` **lower** than the bar at `stack.top()`, it means the rectangle defined by `stack.top()` cannot extend further to the right. `i` is the right boundary.
        當我們看到一個長條 `h[i]` 比 `stack.top()` 的長條 **更低** 時，代表由 `stack.top()` 定義的矩形無法再向右延伸。`i` 即為右邊界。
    *   The left boundary is the new top after popping.
        左邊界則是 pop 之後新的堆疊頂端。

#### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <stack>
#include <algorithm>
#include <iostream>

class Solution {
public:
    int largestRectangleArea(std::vector<int>& heights) {
        // Use a stack to store indices. The heights corresponding to these indices
        // will be in non-decreasing order.
        // 使用堆疊來儲存索引。這些索引對應的高度將會是「非遞減」的順序。
        std::stack<int> st;
        int maxArea = 0;
        int n = heights.size();

        // Iterate through all bars. We go up to n to handle the remaining bars in stack.
        // 遍歷所有長條。我們遍歷到 n 是為了處理堆疊中剩餘的長條。
        for (int i = 0; i <= n; ++i) {
            // If i == n, we treat the height as 0 to force pop all remaining elements.
            // 如果 i == n，我們將高度視為 0，以強制彈出所有剩餘元素。
            int currentHeight = (i == n) ? 0 : heights[i];

            // While stack is not empty and current bar is lower than the top bar:
            // 當堆疊不為空且當前長條低於堆疊頂端的長條時：
            while (!st.empty() && currentHeight < heights[st.top()]) {
                // The bar at the top is the "height" of the candidate rectangle.
                // 堆疊頂端的長條即為候選矩形的「高度」。
                int h = heights[st.top()];
                st.pop();

                // Determine the width.
                // 決定寬度。
                // Right boundary is 'i' (the first smaller element on the right).
                // 右邊界是 'i'（右側第一個更小的元素）。
                // Left boundary is the new st.top() (the first smaller element on the left).
                // 左邊界是新的 st.top()（左側第一個更小的元素）。
                int w = st.empty() ? i : (i - st.top() - 1);

                maxArea = std::max(maxArea, h * w);
            }
            st.push(i);
        }

        return maxArea;
    }
};
```

#### Common Mistakes (Why it fails)（錯誤示範與原因）
*   **Mistake:** Storing values instead of indices.
    **錯誤：** 儲存數值而非索引。
    *Reason:* If you store values, you lose the information about the position, making it impossible to calculate the width ($right - left - 1$).
    *原因：* 如果儲存數值，你會丟失位置資訊，導致無法計算寬度（$right - left - 1$）。

*   **Mistake:** Forgetting to process remaining elements in the stack.
    **錯誤：** 忘記處理堆疊中剩餘的元素。
    *Fix:* The loop condition `i <= n` with virtual height 0 handles this elegantly.
    *修正：* 迴圈條件 `i <= n` 配合虛擬高度 0 可以優雅地解決此問題。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Indices vs. Values** | **Always store indices** in Monotonic Stacks if you need to calculate distance/width. Values are rarely enough.<br>**務必儲存索引**，若你需要計算距離/寬度。光存數值通常不夠。 |
| **Strict vs. Non-Strict** | Should you pop when `current == top`? Usually, for "Next Greater", strict inequality matters. For histograms, keeping duplicates is fine but popping them doesn't hurt correctness if logic is sound.<br>當 `current == top` 時該 pop 嗎？通常對於「下一個更大」問題，嚴格不等式很重要。對直方圖而言，保留重複項沒問題，但若邏輯正確，pop 掉也不影響正確性。 |
| **Boundary Conditions** | Handling empty stack when calculating width. Usually implies the range extends to index -1.<br>計算寬度時處理空堆疊的情況。通常意味著範圍延伸到了索引 -1。 |
| **Stack Overflow** | In recursion problems, Python has a low recursion limit. C++ is better but still limited. Explicit stack is safer for deep trees.<br>在遞迴問題中，Python 的遞迴限制較低。C++ 較好但也有限制。對於深層樹結構，顯式堆疊更安全。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Identify the Property:** "This problem asks for the next greater element / range bounded by smaller elements, which suggests a Monotonic Stack."
    **識別特性：** 「這個問題要求下一個更大元素 / 由更小元素界定的範圍，這暗示了單調堆疊。」
2.  **Define the Invariant:** "I will maintain a stack of indices where the corresponding heights are strictly increasing."
    **定義不變性：** 「我將維護一個索引堆疊，其中對應的高度是嚴格遞增的。」
3.  **Explain the Trigger:** "When we encounter a smaller element, it breaks the increasing property, triggering the calculation for the elements being popped."
    **解釋觸發點：** 「當我們遇到一個較小的元素時，它破壞了遞增特性，從而觸發對被彈出元素的計算。」

### Whiteboard Strategy（白板策略）
-   **Draw a Histogram:** Visually draw bars.
    **畫出直方圖：** 視覺化地畫出長條。
-   **Trace the Stack:** On the side, write `Stack: [0, 2, ...]` and cross out elements as you pop. This proves you understand the flow.
    **追蹤堆疊：** 在旁邊寫下 `Stack: [0, 2, ...]`，並在 pop 時劃掉元素。這證明你理解流程。

### Common Follow-ups（常見追問）
-   **Q:** What if the input is a stream (infinite)?
    **問：** 如果輸入是串流（無限的）怎麼辦？
    *A:* We might need to process partial results or use a persistent data structure, but Monotonic Stack usually requires seeing the "future" smaller element to resolve the "past".
    *答：* 我們可能需要處理部分結果或使用持久化資料結構，但單調堆疊通常需要看到「未來」的更小元素來解決「過去」的元素。
-   **Q:** Can we solve this in 2D? (Maximal Rectangle)
    **問：** 我們能解決 2D 版本嗎？（最大矩形）
    *A:* Yes, by treating each row as the base of a histogram built from previous rows.
    *答：* 可以，將每一列視為基於前幾列建立的直方圖底部。

---

## 7. Practice Problems（練習題）

### Easy: Valid Parentheses (LC 20)
*   **Hint:** Use a map for matching pairs. Return false immediately on mismatch.
    **提示：** 使用 map 來匹配對應關係。不匹配時立即回傳 false。
*   **Focus:** Clean code, handling edge cases (e.g., `"]"`).
    **重點：** 程式碼整潔度，處理邊界情況（例如 `"]"`）。

### Medium: Daily Temperatures (LC 739)
*   **Hint:** Classic Monotonic Decreasing Stack. Store indices. Result `res[top] = current_index - top`.
    **提示：** 經典單調遞減堆疊。儲存索引。結果 `res[top] = current_index - top`。
*   **Focus:** $O(N)$ time complexity proof.
    **重點：** $O(N)$ 時間複雜度證明。

### Hard: Basic Calculator (LC 224) or Trapping Rain Water (LC 42)
*   **Hint (Calculator):** Handle parentheses and signs. Use a stack to store the `result` and `sign` before entering a parenthesis.
    **提示（計算機）：** 處理括號與正負號。進入括號前，使用堆疊儲存當前的 `result` 和 `sign`。
*   **Hint (Rain Water):** Similar to Histogram. We accumulate water when we find a right boundary taller than the bottom (current popped element).
    **提示（接雨水）：** 類似直方圖。當我們找到比底部（當前彈出元素）更高的右邊界時，累積水量。

---

## 8. Quick Checklist（快速檢核表）

- [ ] **Empty Check:** Did I check `!st.empty()` before accessing `st.top()`?
  **空檢查：** 存取 `st.top()` 前是否有檢查 `!st.empty()`？
- [ ] **Sentinel Value:** Did I handle the end of the array? (e.g., pushing a 0 or $\infty$ at the end to flush the stack).
  **哨兵值：** 是否處理了陣列末端？（例如在末尾推入 0 或 $\infty$ 以清空堆疊）。
- [ ] **Index vs Value:** Am I pushing the correct data type?
  **索引 vs 數值：** 我推入的資料型態正確嗎？
- [ ] **Complexity:** Is the inner `while` loop confusing me? (Remember: each element is pushed once and popped once $\rightarrow O(N)$).
  **複雜度：** 內層的 `while` 迴圈是否讓我困惑？（記住：每個元素進一次出一次 $\rightarrow O(N)$）。

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Cafeteria Tray" (自助餐廳托盤)
-   **Basic Stack:** You can only take the top tray.
    **基礎堆疊：** 你只能拿最上面的托盤。

### The "Sunset View" (日落景觀 - Monotonic Stack)
-   Imagine buildings in a line looking at the sunset (to the right).
    想像一排建築物望向日落（向右看）。
-   If a building is taller than the one in front of it, it blocks the view. The smaller building is "popped" from the view.
    如果一棟建築物比前面的高，它會擋住視線。較矮的建築物會從視野中被「彈出」。
-   The stack represents the buildings that can currently see the sunset.
    堆疊代表目前能看到日落的建築物。

---