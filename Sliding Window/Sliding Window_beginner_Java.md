Here is a comprehensive guide on **Sliding Window**, tailored for a Senior Software Engineer, starting from foundational concepts (Beginner level) but structured for high-level interview performance.

這是一份針對 **Sliding Window（滑動視窗）** 的完整教材，專為資深軟體工程師量身打造，內容從基礎觀念（Beginner level）出發，但結構設計旨在提升高階面試表現。

---

# Sliding Window (Beginner Level)
# 滑動視窗（初學者難度）

## 1. Learning Objectives (學習目標)

*   **Understand the core mechanic:** Learn how to convert nested loops into a single linear pass using two pointers.
    **理解核心機制：** 學習如何利用雙指針將巢狀迴圈轉換為單次線性掃描。
*   **Distinguish window types:** Differentiate between "Fixed Size" and "Variable Size" windows and their specific templates.
    **區分視窗類型：** 分辨「固定大小」與「可變大小」視窗及其特定模板。
*   **Master the complexity reduction:** Visualize how $O(N^2)$ brute force solutions are optimized to $O(N)$.
    **掌握複雜度優化：** 具象化理解 $O(N^2)$ 的暴力解法如何優化至 $O(N)$。
*   **Identify applicability:** Recognize keywords in problem descriptions that signal a Sliding Window approach.
    **識別適用場景：** 辨識題目描述中暗示使用滑動視窗的關鍵字。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Sliding Window is a computational technique that maintains a subset of data (the "window") within a larger dataset (usually an array or string).
滑動視窗是一種運算技巧，它在較大的資料集（通常是陣列或字串）中維護一個資料子集（即「視窗」）。

The window moves across the data to process contiguous elements without re-calculating the overlapping parts.
視窗在資料上移動以處理連續元素，且無需重新計算重疊的部分。

### Intuition (直覺)
Imagine looking at a long train through a small rectangular frame; you only see a few cars at a time.
想像透過一個小的長方形框框看一列長火車；你一次只能看到幾節車廂。

As the train moves (or you move the frame), one car leaves the view, and a new one enters.
當火車移動（或你移動框框）時，一節車廂離開視野，新的一節進入。

### Complexity (複雜度)
*   **Time Complexity:** $O(N)$ — Each element is added and removed from the window at most once.
    **時間複雜度：** $O(N)$ — 每個元素最多被加入和移出視窗各一次。
*   **Space Complexity:** $O(1)$ (if only storing variables) or $O(K)$ (if storing window elements in a map/set).
    **空間複雜度：** $O(1)$（若僅儲存變數）或 $O(K)$（若需在 Map/Set 中儲存視窗元素）。

### Applicable Scenarios (適用場景)
*   Input is a linear data structure (Array, String, LinkedList).
    輸入為線性資料結構（陣列、字串、鏈結串列）。
*   Problem asks for the **longest/shortest** substring/subarray, or a specific **target value** within a **contiguous** range.
    題目要求找出**最長/最短**的子字串/子陣列，或是在**連續**範圍內的特定**目標值**。

### Non-Applicable Scenarios (不適用場景)
*   Input data requires non-contiguous selection (e.g., Subsequences).
    輸入資料需要非連續的選取（例如：子序列）。
    *   *Correction:* Subsequences usually require Dynamic Programming.
    *   *修正：* 子序列通常需要動態規劃。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Fixed Size Window (固定大小視窗)
The window size $k$ is constant. You slide the window one step at a time.
視窗大小 $k$ 是固定的。你每次將視窗滑動一步。
*   *Example:* Find the maximum sum of any contiguous subarray of size 3.
*   *範例：* 找出大小為 3 的連續子陣列的最大總和。

### Pattern B: Variable Size Window (可變大小視窗)
The window grows (`right++`) to meet a condition, then shrinks (`left++`) to optimize the result or restore validity.
視窗會擴張（`right++`）以滿足條件，然後收縮（`left++`）以優化結果或恢復合法性。
*   *Example:* Find the smallest subarray with a sum greater than or equal to $S$.
*   *範例：* 找出總和大於或等於 $S$ 的最小子陣列。

---

## 4. Example Walkthrough (範例講解)

### Problem: Minimum Size Subarray Sum (Variable Window)
### 問題：長度最小的子陣列（可變視窗）

**Problem Statement:**
Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a **contiguous subarray** of which the sum is greater than or equal to `target`. If there is no such subarray, return 0.
給定一個正整數陣列 `nums` 和一個正整數 `target`，回傳其總和大於或等於 `target` 的**連續子陣列**的最小長度。若不存在此類子陣列，則回傳 0。

**Brute Force Approach (暴力解法):**
Use two nested loops. The outer loop picks the start, the inner loop expands to find valid sums.
使用兩個巢狀迴圈。外層迴圈選擇起點，內層迴圈向外擴張以尋找符合的總和。
*   Complexity: $O(N^2)$. This is inefficient for large $N$.
*   複雜度：$O(N^2)$。這對於大的 $N$ 來說效率低落。

**Optimization Strategy (優化策略):**
Use two pointers, `left` and `right`, both starting at 0.
使用兩個指針 `left` 和 `right`，皆從 0 開始。
1.  **Expand:** Move `right` to add numbers until `sum >= target`.
    **擴張：** 移動 `right` 加入數字，直到 `sum >= target`。
2.  **Shrink:** Once valid, move `left` to remove numbers to find the smallest length, while keeping `sum >= target`.
    **收縮：** 一旦符合條件，移動 `left` 移除數字以找出最小長度，同時保持 `sum >= target`。

**Java Reference Solution (Java 參考解):**

```java
class Solution {
    public int minSubArrayLen(int target, int[] nums) {
        // Initialize the result to MAX_VALUE to easily find the minimum later.
        // 初始化結果為 MAX_VALUE，以便稍後找出最小值。
        int minLength = Integer.MAX_VALUE;
        
        // 'left' pointer for the start of the window.
        // 'left' 指針代表視窗的起點。
        int left = 0;
        
        // Current sum of the window.
        // 視窗當前的總和。
        int currentSum = 0;

        // 'right' pointer iterates through the array (Expanding phase).
        // 'right' 指針遍歷陣列（擴張階段）。
        for (int right = 0; right < nums.length; right++) {
            // Add the current element to the window sum.
            // 將當前元素加入視窗總和。
            currentSum += nums[right];

            // While the window condition is met (sum >= target), try to shrink it.
            // 當視窗條件滿足時（sum >= target），嘗試收縮視窗。
            while (currentSum >= target) {
                // Update the minimum length found so far.
                // 更新目前找到的最小長度。
                minLength = Math.min(minLength, right - left + 1);

                // Remove the element at 'left' from the sum (Shrinking phase).
                // 從總和中移除 'left' 位置的元素（收縮階段）。
                currentSum -= nums[left];
                
                // Move the left pointer forward.
                // 將左指針向前移動。
                left++;
            }
        }

        // If minLength is still MAX_VALUE, it means no valid subarray was found.
        // 如果 minLength 仍為 MAX_VALUE，表示未找到符合條件的子陣列。
        return (minLength == Integer.MAX_VALUE) ? 0 : minLength;
    }
}
```

**Why Brute Force Fails / Error Analysis (為何暴力解失敗 / 錯誤分析):**
In the brute force approach, for every new starting position, we re-calculate the sum from scratch.
在暴力解法中，對於每個新的起始位置，我們都從頭重新計算總和。
Sliding window reuses the sum by simply subtracting the element leaving the window.
滑動視窗透過簡單地減去離開視窗的元素來重複利用總和。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept / Pitfall (概念/陷阱) | Explanation (解釋) |
| :--- | :--- |
| **While vs. If** | Inside the loop, use `while` to shrink variable windows (to minimize fully), use `if` for fixed windows. <br> 在迴圈內，可變視窗使用 `while` 來收縮（以達到最小化），固定視窗使用 `if`。 |
| **Window Size Calculation** | The length is `right - left + 1`. Don't forget the `+1`. <br> 長度是 `right - left + 1`。別忘了 `+1`。 |
| **Initialization** | For "Minimum" problems, init with `Integer.MAX_VALUE`. For "Maximum", init with `Integer.MIN_VALUE` or 0. <br> 對於「最小化」問題，初始值設為 `Integer.MAX_VALUE`。對於「最大化」，設為 `Integer.MIN_VALUE` 或 0。 |
| **Negative Numbers** | If the array contains negative numbers, the "sum increases as window grows" logic breaks. Sliding window might not apply directly (use Prefix Sum + Map instead). <br> 若陣列包含負數，「視窗變大總和增加」的邏輯會被打破。滑動視窗可能不直接適用（改用前綴和 + Map）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "Since we are looking for a contiguous subarray with a specific property, I'm thinking of using the Sliding Window technique."
    **識別：** 「由於我們在尋找具有特定屬性的連續子陣列，我考慮使用滑動視窗技巧。」
2.  **Define State:** "I will maintain a window defined by `left` and `right` pointers and a variable `currentSum` to track the state."
    **定義狀態：** 「我將維護一個由 `left` 和 `right` 指針定義的視窗，以及一個變數 `currentSum` 來追蹤狀態。」
3.  **Explain Logic:** "I'll expand `right` to satisfy the condition, then shrink `left` to optimize."
    **解釋邏輯：** 「我會擴張 `right` 以滿足條件，然後收縮 `left` 進行優化。」

### Whiteboard Strategy (白板策略)
*   Draw the array and use arrows ($\uparrow$) for `L` and `R`.
    畫出陣列並使用箭頭（$\uparrow$）標示 `L` 和 `R`。
*   Trace one iteration: Show `R` moving, `Sum` updating, then `L` moving.
    追蹤一次迭代：展示 `R` 移動，`Sum` 更新，然後 `L` 移動。

### Common Follow-ups (常見追問)
*   **Q:** What if the input is an infinite stream?
    **問：** 如果輸入是無限的串流怎麼辦？
    *   **A:** We cannot store all elements. Sliding window still works if we only need to store the current window in memory.
    *   **答：** 我們無法儲存所有元素。如果只需要將當前視窗保留在記憶體中，滑動視窗仍然有效。

---

## 7. Practice Problems (練習題)

### 1. Easy: Maximum Average Subarray I (Fixed Window)
**Problem:** Find the contiguous subarray of length `k` that has the maximum average value.
**問題：** 找出長度為 `k` 且具有最大平均值的連續子陣列。
*   **Hint:** Initialize window with first `k` elements. Then slide: subtract `nums[i-k]`, add `nums[i]`.
*   **提示：** 用前 `k` 個元素初始化視窗。然後滑動：減去 `nums[i-k]`，加上 `nums[i]`。

### 2. Medium: Longest Substring Without Repeating Characters (Variable Window)
**Problem:** Given a string, find the length of the longest substring without repeating characters.
**問題：** 給定一個字串，找出不含重複字元的最長子字串長度。
*   **Hint:** Use a `HashSet` or `HashMap` to track characters in the window. If `s[right]` exists in the set, increment `left` and remove `s[left]` until valid.
*   **提示：** 使用 `HashSet` 或 `HashMap` 追蹤視窗內的字元。若 `s[right]` 已存在於集合中，增加 `left` 並移除 `s[left]` 直到合法。

### 3. Hard: Permutation in String (Fixed Window + Hashing)
**Problem:** Given two strings `s1` and `s2`, return true if `s2` contains a permutation of `s1`.
**問題：** 給定兩個字串 `s1` 和 `s2`，若 `s2` 包含 `s1` 的排列組合，則回傳 true。
*   **Hint:** Fixed window of size `s1.length()`. Use two frequency arrays (size 26) to compare the window in `s2` against `s1`.
*   **提示：** 大小為 `s1.length()` 的固定視窗。使用兩個頻率陣列（大小 26）來比較 `s2` 中的視窗與 `s1`。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] **Contiguity:** Is the problem asking for a *contiguous* range? (If not, Sliding Window is wrong).
    **連續性：** 題目是否要求*連續*範圍？（若否，滑動視窗是錯的）。
- [ ] **Monotonicity:** Does adding an element always increase/decrease the metric? (Crucial for validity).
    **單調性：** 加入元素是否總是增加/減少指標？（對有效性至關重要）。
- [ ] **Boundary:** Did I handle the case where the array length is smaller than the window size?
    **邊界：** 我是否處理了陣列長度小於視窗大小的情況？

### Debugging (除錯)
- [ ] **Infinite Loop:** Did I forget to increment `left` inside the `while` loop?
    **無窮迴圈：** 我是否忘記在 `while` 迴圈內增加 `left`？
- [ ] **Result Update:** Did I update the result *before* or *after* shrinking? (Depends on problem type: Max vs Min).
    **結果更新：** 我是在收縮*之前*還是*之後*更新結果？（取決於問題類型：求最大還是最小）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Caterpillar" Method (毛毛蟲法)
Visualize the window as a caterpillar moving over a leaf (the array).
將視窗想像成一隻在葉子（陣列）上移動的毛毛蟲。
1.  **Eat (Expand):** The head (`right`) moves forward, eating leaf parts (adding to sum).
    **進食（擴張）：** 頭部（`right`）向前移動，吃掉葉子（加入總和）。
2.  **Digest (Shrink):** If it gets too full (condition met), the tail (`left`) pulls forward to excrete waste (remove from sum).
    **消化（收縮）：** 如果太飽了（滿足條件），尾巴（`left`）向前拉，排出廢物（從總和移除）。

### Visual Anchor (圖像錨點)
```text
[ 2, 1, 5, 2, 8 ]
   ^     ^
   L     R
   |-----|
   Window
```
Always draw this simple diagram on the whiteboard before coding.
寫程式碼前，永遠先在白板上畫出這個簡單的圖示。