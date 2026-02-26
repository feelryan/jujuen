# Sliding Window: Intermediate Guide
# 滑動視窗：中階指南

## 1. Learning Objectives (學習目標)

*   **Master the "Variable Size" Window Pattern:** Move beyond fixed-size windows to handle dynamic constraints (e.g., "longest substring with condition X").
    **掌握「變動大小」視窗模式：** 超越固定大小視窗，處理動態限制（例如：「符合條件 X 的最長子字串」）。
*   **Optimize $O(N^2)$ to $O(N)$:** Understand how to convert nested loops into a linear pass by maintaining a running state.
    **將 $O(N^2)$ 優化為 $O(N)$：** 理解如何透過維護運行狀態，將巢狀迴圈轉換為線性遍歷。
*   **Integrate Auxiliary Data Structures:** Learn to effectively use HashMaps or Sets within the window to track frequency or uniqueness.
    **整合輔助資料結構：** 學習在視窗內有效地使用 HashMap 或 Set 來追蹤頻率或唯一性。
*   **Identify "Contiguous" Problems:** Instantly recognize problems requiring processing of contiguous subarrays or substrings.
    **識別「連續」問題：** 能夠立即辨識出需要處理連續子陣列或子字串的問題。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Sliding Window is a technique used to perform operations on a specific window size of a given array or string, effectively converting two nested loops into a single loop.
滑動視窗是一種在給定陣列或字串的特定視窗大小上執行操作的技術，有效地將兩個巢狀迴圈轉換為單一迴圈。

### Intuition (直覺)
Instead of recalculating the entire subset every time the window moves, we only update the result based on the element entering the window and the element leaving it.
我們不需要在視窗移動時重新計算整個子集，而是僅根據進入視窗的元素和離開視窗的元素來更新結果。

### Complexity (複雜度)
*   **Time Complexity:** $O(N)$. Each element is added and removed from the window at most once.
    **時間複雜度：** $O(N)$。每個元素最多被加入和移出視窗各一次。
*   **Space Complexity:** $O(1)$ or $O(K)$ (where $K$ is the size of the auxiliary structure like a character set).
    **空間複雜度：** $O(1)$ 或 $O(K)$（其中 $K$ 是輔助結構如字元集的大小）。

### When to Use (適用場景)
*   Input is a linear data structure (Array, String, LinkedList).
    輸入是線性資料結構（陣列、字串、連結串列）。
*   Asking for longest/shortest substring/subarray satisfying a condition.
    要求滿足某條件的最長/最短子字串/子陣列。
*   Keywords: "Contiguous", "Consecutive", "Subarray", "Substring".
    關鍵字：「連續」、「連貫」、「子陣列」、「子字串」。

### When NOT to Use (不適用場景)
*   Input requires selecting non-contiguous elements (usually Dynamic Programming or Backtracking).
    輸入需要選擇非連續元素（通常是動態規劃或回溯法）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Fixed Size Window (固定大小視窗)
The window size $k$ is constant. We slide the window one step at a time.
視窗大小 $k$ 是固定的。我們每次將視窗滑動一步。
*   *Example: Maximum sum of a subarray of size k.*
    *範例：大小為 k 的子陣列的最大總和。*

### B. Variable Size - Expand to Find Max (變動大小 - 擴張以尋找最大值)
**Focus of this guide.** We expand `right` as much as possible while the condition holds. If it breaks, we increment `left`.
**本指南重點。** 我們盡可能擴張 `right` 指標，只要條件成立。如果條件破壞，我們增加 `left` 指標。
*   *Example: Longest substring without repeating characters.*
    *範例：無重複字元的最長子字串。*

### C. Variable Size - Shrink to Find Min (變動大小 - 收縮以尋找最小值)
We expand `right` until the condition is valid, then shrink `left` to find the minimum length while keeping it valid.
我們擴張 `right` 直到條件成立，然後收縮 `left` 以在保持條件成立的同時找到最小長度。
*   *Example: Minimum Size Subarray Sum.*
    *範例：長度最小的子陣列總和。*

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Substring Without Repeating Characters
### 問題：無重複字元的最長子字串

**Problem Statement:**
Given a string `s`, find the length of the longest substring without repeating characters.
給定一個字串 `s`，找出其中不包含重複字元的最長子字串的長度。

### Approach 1: Brute Force (暴力解)
Check all possible substrings, verify uniqueness for each, and track the maximum length.
檢查所有可能的子字串，驗證每個子字串的唯一性，並追蹤最大長度。
*   **Complexity:** $O(N^3)$ (Nested loops + uniqueness check).
    **複雜度：** $O(N^3)$（巢狀迴圈 + 唯一性檢查）。

### Approach 2: Sliding Window (Optimization) (滑動視窗優化)
Use two pointers (`left`, `right`) and a `Set` to track characters in the current window.
使用兩個指標（`left`, `right`）和一個 `Set` 來追蹤當前視窗內的字元。

1.  Move `right` to expand.
    移動 `right` 進行擴張。
2.  If `s[right]` is already in the `Set`, it's a duplicate.
    如果 `s[right]` 已經在 `Set` 中，表示有重複。
3.  Shrink from `left` (remove `s[left]`) until the duplicate is removed.
    從 `left` 收縮（移除 `s[left]`），直到重複被移除。
4.  Update maximum length.
    更新最大長度。

### TypeScript Solution (參考解)

```typescript
/**
 * Calculates the length of the longest substring without repeating characters.
 * 計算無重複字元的最長子字串長度。
 *
 * @param s - The input string (輸入字串)
 * @returns The length of the longest unique substring (最長唯一子字串的長度)
 */
function lengthOfLongestSubstring(s: string): number {
    // Use a Set to store characters in the current window
    // 使用 Set 來儲存當前視窗內的字元
    const charSet = new Set<string>();
    
    let left = 0;
    let maxLength = 0;

    // Iterate with the right pointer to expand the window
    // 使用右指標迭代以擴張視窗
    for (let right = 0; right < s.length; right++) {
        const currentChar = s[right];

        // If the character is already in the set, shrink the window from the left
        // 如果字元已存在於集合中，從左側收縮視窗
        while (charSet.has(currentChar)) {
            // Remove the character at the left pointer and move left forward
            // 移除左指標處的字元並將左指標向前移動
            charSet.delete(s[left]);
            left++;
        }

        // Add the current character to the set
        // 將當前字元加入集合
        charSet.add(currentChar);

        // Update the maximum length found so far
        // The window size is (right - left + 1)
        // 更新目前為止找到的最大長度
        // 視窗大小為 (right - left + 1)
        maxLength = Math.max(maxLength, right - left + 1);
    }

    return maxLength;
}

// Test cases
console.log(lengthOfLongestSubstring("abcabcbb")); // Output: 3 ("abc")
console.log(lengthOfLongestSubstring("bbbbb"));    // Output: 1 ("b")
console.log(lengthOfLongestSubstring("pwwkew"));   // Output: 3 ("wke")
```

### Analysis (分析)
*   **Time Complexity:** $O(N)$. `left` and `right` each travel across the string at most once.
    **時間複雜度：** $O(N)$。`left` 和 `right` 各自最多遍歷字串一次。
*   **Space Complexity:** $O(min(N, M))$, where $M$ is the size of the charset (e.g., 26 for lowercase English, 128 for ASCII).
    **空間複雜度：** $O(min(N, M))$，其中 $M$ 是字元集的大小（例如小寫英文字母為 26，ASCII 為 128）。

### Common Mistake (錯誤示範)
Using an `if` instead of `while` to shrink the window.
使用 `if` 而不是 `while` 來收縮視窗。
*   *Why wrong:* If the duplicate character is deep inside the window (e.g., "abcz...a"), you need to remove everything up to the first 'a', not just one character.
    *為何錯誤：* 如果重複字元在視窗深處（例如 "abcz...a"），你需要移除直到第一個 'a' 的所有內容，而不僅僅是一個字元。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **While vs If** | Use `while` loop inside the `for` loop to shrink the window until the condition is valid again. Using `if` only shrinks once, which might be insufficient. <br> 在 `for` 迴圈內使用 `while` 迴圈來收縮視窗，直到條件再次有效。使用 `if` 只會收縮一次，可能不足。 |
| **Window Size Calculation** | The length is always `right - left + 1`. A common off-by-one error is forgetting the `+1`. <br> 長度總是 `right - left + 1`。常見的差一錯誤是忘記 `+1`。 |
| **Subarray vs Subsequence** | Sliding Window is for **Subarrays** (contiguous). Subsequences (non-contiguous) usually require Dynamic Programming. <br> 滑動視窗適用於 **子陣列**（連續）。子序列（非連續）通常需要動態規劃。 |
| **Shrink Logic** | Ensure you update your auxiliary structure (Map/Set/Sum) *before* incrementing `left`. <br> 確保在增加 `left` *之前* 更新你的輔助結構（Map/Set/Sum）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Framework (口條框架)
1.  **Identify the Pattern:** "Since this problem asks for a contiguous substring satisfying a condition, I'm thinking of using the Sliding Window technique."
    **識別模式：** 「由於這個問題要求滿足條件的連續子字串，我考慮使用滑動視窗技術。」
2.  **Define Invariants:** "I will maintain a window `[left, right]` such that the substring inside always satisfies [condition X] (or I will shrink until it does)."
    **定義不變量：** 「我將維護一個視窗 `[left, right]`，使得內部的子字串總是滿足 [條件 X]（或者我會收縮直到它滿足）。」
3.  **Discuss Trade-offs:** "Using a Set gives us $O(N)$ time, but costs $O(K)$ space. If space is strictly limited, we might need a different approach, but usually $O(128)$ is negligible."
    **討論權衡：** 「使用 Set 給我們 $O(N)$ 時間，但花費 $O(K)$ 空間。如果空間嚴格受限，我們可能需要不同方法，但通常 $O(128)$ 可以忽略不計。」

### Whiteboard Strategy (白板策略)
*   Write `left`, `right`, `result` variables clearly at the top.
    在頂部清楚寫下 `left`, `right`, `result` 變數。
*   Draw a small example (e.g., array boxes) and trace the pointers physically.
    畫一個小範例（如陣列方格）並實際追蹤指標。

### Common Follow-ups (常見追問)
*   "What if the stream is infinite?" (Handle data in chunks / persistent storage).
    「如果資料流是無限的怎麼辦？」（分塊處理資料 / 持久化儲存）。
*   "How to handle a very large character set (Unicode)?" (Use a Map instead of a fixed-size array).
    「如何處理非常大的字元集（Unicode）？」（使用 Map 而非固定大小陣列）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Maximum Average Subarray I
*   **Prompt:** Find the contiguous subarray of length `k` that has the maximum average value.
    **題目：** 找出長度為 `k` 且具有最大平均值的連續子陣列。
*   **Hint:** Fixed size window. Initialize sum for first `k`, then subtract `nums[i-k]` and add `nums[i]`.
    **提示：** 固定大小視窗。初始化前 `k` 個的總和，然後減去 `nums[i-k]` 並加上 `nums[i]`。

### 2. Intermediate: Max Consecutive Ones III
*   **Prompt:** Given a binary array, find the max length of contiguous 1s if you can flip at most `k` 0s.
    **題目：** 給定二進位陣列，若最多可以翻轉 `k` 個 0，找出連續 1 的最大長度。
*   **Hint:** The window is valid if `count(0) <= k`. Expand right. If `count(0) > k`, increment left.
    **提示：** 若 `count(0) <= k` 視窗有效。向右擴張。若 `count(0) > k`，增加左指標。

### 3. Hard: Minimum Window Substring
*   **Prompt:** Find the smallest substring in `s` containing all characters of `t`.
    **題目：** 在 `s` 中找出包含 `t` 所有字元的最小子字串。
*   **Hint:** Use a frequency Map for `t`. Expand right until window has all chars. Then shrink left *as much as possible* while still valid to find the min length.
    **提示：** 對 `t` 使用頻率 Map。向右擴張直到視窗包含所有字元。然後在保持有效的情況下，盡可能向左收縮以找到最小長度。

---

## 8. Quick Checklists (快速檢核表)

Use this during your implementation to self-correct.
在實作過程中使用此表進行自我修正。

*   [ ] **Initialization:** Are `left`, `right`, and `result` initialized correctly? (e.g., `result` to 0 for max, Infinity for min).
    **初始化：** `left`, `right` 和 `result` 是否正確初始化？（例如：求最大值時 `result` 為 0，求最小值時為 Infinity）。
*   [ ] **Movement:** Does `right` increment in every iteration?
    **移動：** `right` 是否在每次迭代中增加？
*   [ ] **Shrink Condition:** Is the `while` loop condition for shrinking correct?
    **收縮條件：** 收縮用的 `while` 迴圈條件是否正確？
*   [ ] **Update Logic:** Am I updating the `result` at the correct time (after expanding for Max, after shrinking for Min)?
    **更新邏輯：** 我是否在正確的時間更新 `result`（求最大值時在擴張後，求最小值時在收縮後）？
*   [ ] **Boundary:** Did I handle empty strings or arrays?
    **邊界：** 我是否處理了空字串或空陣列？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Caterpillar (Inchworm) Analogy (毛毛蟲/尺蠖類比)
Imagine a caterpillar moving along a branch (the array).
想像一隻毛毛蟲沿著樹枝（陣列）移動。
1.  **Eating (Expand):** The head (`right` pointer) moves forward to eat leaves (add elements). The caterpillar grows.
    **進食（擴張）：** 頭部（`right` 指標）向前移動吃葉子（加入元素）。毛毛蟲變長。
2.  **Digesting/Full (Shrink):** If it eats something bad or gets too long (invalid condition), the tail (`left` pointer) moves forward to excrete/shrink.
    **消化/太飽（收縮）：** 如果吃到壞東西或太長（無效條件），尾部（`left` 指標）向前移動排泄/收縮。
3.  **Goal:** Measure the caterpillar's length at specific moments.
    **目標：** 在特定時刻測量毛毛蟲的長度。

![Sliding Window Visual](https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Inchworm.jpg/320px-Inchworm.jpg)
*(Visualize the movement: Head extends -> Check State -> Tail follows if needed)*
*（視覺化移動：頭伸出 -> 檢查狀態 -> 若需要則尾巴跟上）*