Here is the complete study material for **Sliding Window**, designed for a Senior Software Engineer, formatted in bilingual (English-Chinese) text with Java code.

---

# Module: Sliding Window (Intermediate)
# 模組：滑動視窗（中階）

**Author:** Principal Software Engineer (Big Tech)
**Target Audience:** Senior Software Engineer (7-12 YOE)
**Code Language:** Java

---

## 1. Learning Goals (學習目標)

*   **Master the transition from Brute Force to Linear Time.**
    掌握從暴力解法（$O(N^2)$）優化至線性時間（$O(N)$）的關鍵轉折。
*   **Distinguish between Fixed and Variable window patterns.**
    區分「固定窗口」與「可變窗口」的設計模式與適用場景。
*   **Integrate auxiliary data structures within the window.**
    學會如何在窗口邏輯中整合輔助資料結構（如 HashMap 或 HashSet）以處理複雜約束。
*   **Develop a standard code template for interview consistency.**
    建立一套標準化的程式碼模板，以確保面試時的穩定性。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Sliding Window is an optimization technique used primarily on arrays or strings to convert nested loops into a single loop.
滑動視窗是一種主要用於陣列或字串的優化技巧，旨在將巢狀迴圈轉換為單一迴圈。

It maintains a subset of elements (the "window") that satisfies certain constraints and slides over the data structure.
它維護一組滿足特定約束條件的元素子集（即「視窗」），並在資料結構上滑動。

### Intuition (直覺)
Instead of recalculating the properties of a subarray from scratch, we utilize the result of the previous window.
我們不從頭重新計算子陣列的屬性，而是利用前一個視窗的計算結果。

Think of it as "adding the new element entering the window and removing the old element leaving it."
將其想像為「加上進入視窗的新元素，並移除離開視窗的舊元素」。

### Complexity (複雜度)
*   **Time:** $O(N)$. Each element is added to the window once and removed once (at most).
    **時間：** $O(N)$。每個元素最多被加入視窗一次，並被移除一次。
*   **Space:** $O(1)$ (if only variables are used) or $O(K)$ (if a Map/Set is used for characters/elements).
    **空間：** $O(1)$（若僅使用變數）或 $O(K)$（若使用 Map/Set 儲存字元或元素）。

### When to Use (適用場景)
*   The problem asks for the **longest**, **shortest**, or **target value** of a **contiguous** subarray or substring.
    問題要求找出**連續**子陣列或子字串的**最長**、**最短**或**目標值**。
*   The input is linear (Array, String, LinkedList).
    輸入資料是線性的（陣列、字串、鏈結串列）。

### When NOT to Use (不適用場景)
*   The problem involves **non-contiguous** subsequences (usually Dynamic Programming).
    問題涉及**非連續**的子序列（通常屬於動態規劃）。
*   The order of elements does not matter (might be Hashing or Sorting).
    元素的順序不重要（可能屬於雜湊或排序問題）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Fixed Size Window (固定大小視窗)
The window size $k$ is constant. You slide the window one step at a time.
視窗大小 $k$ 是固定的。你每次將視窗向右滑動一步。
*   *Example:* Maximum Sum Subarray of size K.
    *範例：* 大小為 K 的最大子陣列和。

### B. Variable Size Window - Shrinkable (可變大小視窗——可收縮)
The window grows (`right` pointer moves) until the condition is broken, then it shrinks (`left` pointer moves) until valid again.
視窗持續擴張（`right` 指標移動）直到違反條件，然後收縮（`left` 指標移動）直到再次符合條件。
*   *Example:* Longest Substring Without Repeating Characters.
    *範例：* 無重複字元的最長子字串。

### C. Variable Size Window - Expandable (可變大小視窗——需滿足條件)
Similar to shrinkable, but often used for "Minimum Window" problems where you expand until valid, then shrink to optimize.
類似於可收縮模式，但常語用於「最小視窗」問題：先擴張直到符合條件，再收縮以進行優化。
*   *Example:* Minimum Window Substring.
    *範例：* 最小覆蓋子字串。

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Substring Without Repeating Characters
### 問題：無重複字元的最長子字串

**Problem Statement:**
Given a string `s`, find the length of the longest substring without repeating characters.
給定一個字串 `s`，請找出其中不含有重複字元的最長子字串的長度。

**Example:** Input: `s = "abcabcbb"`, Output: `3` (The answer is "abc").

### Approach (思路)

1.  **Brute Force (暴力解):**
    Iterate through all substrings, check if each has duplicates.
    遍歷所有子字串，檢查每一個是否有重複字元。
    *   Complexity: $O(N^3)$ or $O(N^2)$ depending on implementation.
    *   複雜度：$O(N^3)$ 或 $O(N^2)$，取決於實作方式。

2.  **Optimization (Sliding Window):**
    Use two pointers, `left` and `right`. `right` expands the window.
    使用雙指標 `left` 與 `right`。`right` 負責擴張視窗。
    If `s.charAt(right)` is already in the window, we have a duplicate.
    如果 `s.charAt(right)` 已經在視窗中，表示出現重複。
    We must move `left` forward to remove the duplicate character.
    我們必須將 `left` 向前移動以移除該重複字元。

3.  **Data Structure Choice (資料結構選擇):**
    A `HashSet` works, but a `HashMap` mapping `character -> index` allows us to jump `left` directly past the duplicate, rather than incrementing one by one.
    使用 `HashSet` 可行，但使用 `HashMap` 映射 `字元 -> 索引` 可以讓我們直接將 `left` 跳過重複的位置，而不是一步步遞增。

### Java Reference Solution (Java 參考解)

```java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        // Handle edge case: empty string
        // 處理邊界情況：空字串
        if (s == null || s.length() == 0) {
            return 0;
        }

        // Map stores the character and its most recent index
        // Map 儲存字元及其最近出現的索引位置
        Map<Character, Integer> map = new HashMap<>();
        
        int maxLength = 0;
        int left = 0;

        // Iterate with the right pointer
        // 使用右指標進行遍歷
        for (int right = 0; right < s.length(); right++) {
            char currentChar = s.charAt(right);

            // If the character is already in the map, update the left pointer
            // 如果字元已存在於 map 中，更新左指標
            if (map.containsKey(currentChar)) {
                // We take Math.max to ensure 'left' never moves backward
                // (e.g., case "abba", when at second 'a', left shouldn't go back to first 'b')
                // 我們使用 Math.max 確保 'left' 絕不向後移動
                // （例如：案例 "abba"，當處理第二個 'a' 時，left 不應跳回第一個 'b' 的位置）
                left = Math.max(left, map.get(currentChar) + 1);
            }

            // Update the character's latest index
            // 更新該字元的最新索引
            map.put(currentChar, right);

            // Update the maximum length found so far
            // 更新目前找到的最大長度
            maxLength = Math.max(maxLength, right - left + 1);
        }

        return maxLength;
    }
}
```

### Why the "Math.max" for left pointer? (為何左指標需要 Math.max？)
**Error Scenario:** Input `abba`.
1. `right` at 0 ('a'), map={'a':0}, max=1.
2. `right` at 1 ('b'), map={'a':0, 'b':1}, max=2.
3. `right` at 2 ('b'), duplicate 'b' found. `left` becomes `map.get('b') + 1` = 2. Map updates 'b':2.
4. `right` at 3 ('a'), duplicate 'a' found. Old 'a' is at index 0.
   *   **Without Max:** `left` would jump back to `0 + 1 = 1`. But `left` is currently at 2. This would include the duplicate 'b' again!
   *   **With Max:** `left = Math.max(2, 0 + 1) = 2`. Correct.

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description (描述) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Window Size** | `right - left + 1` | Calculating as `right - left` (Off-by-one error). <br> 計算成 `right - left`（差一錯誤）。 |
| **While Loop Condition** | Usually `while (condition is invalid)` inside the `for` loop. <br> 通常在 `for` 迴圈內使用 `while (條件不合法)`。 | Using `if` instead of `while`. This fails if removing one element isn't enough to make the window valid. <br> 使用 `if` 代替 `while`。如果移除一個元素不足以讓視窗恢復合法，這會出錯。 |
| **Result Update** | Update result *after* the window becomes valid. <br> 在視窗恢復合法*之後*更新結果。 | Updating result while the window is still invalid. <br> 在視窗仍然不合法時就更新結果。 |
| **Subarray vs Subsequence** | Subarray is contiguous; Subsequence is not. <br> 子陣列是連續的；子序列是不連續的。 | Trying to use Sliding Window on Subsequence problems (like LIS). <br> 試圖在子序列問題（如最長遞增子序列）上使用滑動視窗。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "Since we are looking for a contiguous substring with a specific constraint, this suggests a Sliding Window approach."
    **識別：**「由於我們正在尋找具有特定約束的連續子字串，這提示我們可以使用滑動視窗法。」
2.  **Define State:** "I will use a `left` and `right` pointer to define the window, and a HashMap to track the frequency of characters within the window."
    **定義狀態：**「我將使用 `left` 和 `right` 指標來定義視窗，並使用 HashMap 來追蹤視窗內字元的頻率。」
3.  **Explain Logic:** "I'll expand `right` to include elements. If the constraint is violated, I'll increment `left` to shrink the window until it's valid again."
    **解釋邏輯：**「我會擴張 `right` 來納入元素。如果違反了約束條件，我會增加 `left` 來收縮視窗，直到它再次合法。」

### Whiteboard Strategy (白板策略)
*   **Variable Names:** Use descriptive names like `windowStart`, `windowEnd` or `left`, `right`. Avoid `i`, `j` as they are generic.
    **變數命名：** 使用具描述性的名稱如 `windowStart`, `windowEnd` 或 `left`, `right`。避免使用 `i`, `j` 這種通用名稱。
*   **Dry Run:** Before coding, write a small example (e.g., `A B C B A`) and manually move the pointers to show you understand the edge cases.
    **模擬執行：** 寫程式前，寫下一個小範例（如 `A B C B A`）並手動移動指標，以展示你理解邊界情況。

### Common Follow-ups (常見追問)
*   **Q:** What if the string is a stream of data (infinite)?
    **問：** 如果字串是資料流（無限長）怎麼辦？
    *   *A:* We cannot store the whole string. We might only store the window buffer or use a circular buffer.
    *   *答：* 我們無法儲存整個字串。我們可能只儲存視窗緩衝區或使用環形緩衝區。
*   **Q:** What if the character set is very large (Unicode)?
    **問：** 如果字元集非常大（Unicode）怎麼辦？
    *   *A:* Use `HashMap` instead of a fixed-size array (like `int[26]`).
    *   *答：* 使用 `HashMap` 代替固定大小的陣列（如 `int[26]`）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Maximum Average Subarray I (LeetCode 643)
*   **Problem:** Find the contiguous subarray of length `k` that has the maximum average value.
    **問題：** 找出長度為 `k` 且具有最大平均值的連續子陣列。
*   **Hint:** Fixed size window. Initialize sum with first `k` elements, then subtract `nums[i-k]` and add `nums[i]`.
    **提示：** 固定大小視窗。用前 `k` 個元素初始化總和，然後減去 `nums[i-k]` 並加上 `nums[i]`。

### 2. Medium: Max Consecutive Ones III (LeetCode 1004)
*   **Problem:** Given a binary array, find the max number of consecutive 1s if you can flip at most `k` 0s.
    **問題：** 給定一個二進位陣列，如果你最多可以翻轉 `k` 個 0，找出連續 1 的最大數量。
*   **Hint:** The problem translates to "Find the longest subarray with at most `k` zeros." Use a variable window. Expand right; if zeros > k, shrink left.
    **提示：** 問題轉化為「找出最多包含 `k` 個 0 的最長子陣列」。使用可變視窗。向右擴張；如果 0 的數量 > k，則左側收縮。

### 3. Intermediate/Hard: Sliding Window Maximum (LeetCode 239)
*   **Problem:** Return the max value in the window of size `k` as it moves.
    **問題：** 當大小為 `k` 的視窗移動時，回傳視窗內的最大值。
*   **Hint:** A simple variable isn't enough. You need a **Monotonic Deque** (Double-ended queue) to store indices of potential max values in decreasing order.
    **提示：** 單純的變數不足以解決。你需要一個**單調雙端佇列（Monotonic Deque）**來依遞減順序儲存潛在最大值的索引。

---

## 8. Quick Checklists (快速檢核表)

Use this list to debug your code mentally:
使用此清單在腦中除錯你的程式碼：

*   [ ] **Initialization:** Are `left`, `right`, and `result` initialized correctly (e.g., `result` to 0 or -Infinity)?
    **初始化：** `left`、`right` 和 `result` 是否正確初始化（例如 `result` 設為 0 或負無限大）？
*   [ ] **Movement:** Does `right` always increment? Does `left` only increment when constraints are violated?
    **移動：** `right` 是否總是遞增？`left` 是否僅在違反約束時遞增？
*   [ ] **Validity:** Is the `while` loop condition strictly checking for the *invalid* state?
    **合法性：** `while` 迴圈的條件是否嚴格檢查*不合法*的狀態？
*   [ ] **Size Calculation:** Is the window size calculated as `right - left + 1`?
    **大小計算：** 視窗大小是否計算為 `right - left + 1`？
*   [ ] **Empty Input:** Did I handle `arr.length == 0`?
    **空輸入：** 我是否處理了 `arr.length == 0` 的情況？

---

## 9. Memory Anchors (記憶錨點)

### The Caterpillar (毛毛蟲)
Visualize the sliding window as a **caterpillar** moving across a leaf (the array).
將滑動視窗想像成一隻在葉子（陣列）上移動的**毛毛蟲**。
1.  **Eat (Expand):** The head (`right`) moves forward, eating leaf parts (adding to window).
    **進食（擴張）：** 頭部（`right`）向前移動，吃掉葉子部分（加入視窗）。
2.  **Digest (Check):** The belly gets full (constraint violated).
    **消化（檢查）：** 肚子飽了（違反約束）。
3.  **Poop (Shrink):** The tail (`left`) moves forward to release waste (remove from window) so it can eat again.
    **排泄（收縮）：** 尾部（`left`）向前移動排出廢物（從視窗移除），以便再次進食。

### Image
`[ L ... ... R ]` -> `[ ... L ... ... R ]`
The window crawls. It never jumps back (usually).
視窗在爬行。它絕不向後跳（通常情況下）。