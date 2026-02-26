# Sliding Window: Foundational Mechanics
# 滑動視窗：基礎機制

**Difficulty Level:** Beginner (Focus on Fixed Size & Basic Variable Size)
**難度等級：** 初學者（著重於固定視窗與基礎變動視窗）

---

## 1. Learning Goals (學習目標)

*   **Master the transition from $O(N^2)$ to $O(N)$:** Understand how sliding window optimizes nested loops by reusing computation.
    **掌握從 $O(N^2)$ 到 $O(N)$ 的轉變：** 理解滑動視窗如何透過重複利用計算結果來優化巢狀迴圈。
*   **Distinguish between Fixed and Variable Windows:** Identify when the window size is a constant constraint versus when it is the optimization target.
    **區分固定視窗與變動視窗：** 辨識視窗大小何時為固定限制，何時為優化目標。
*   **Implement "Delta Updates" cleanly:** Learn to update the window state by adding the new element and removing the old one, rather than re-scanning.
    **俐落地實作「增量更新」：** 學習透過加入新元素並移除舊元素來更新視窗狀態，而非重新掃描。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Sliding Window is an algorithmic pattern used to perform required operations on a specific window size of a given array or string.
滑動視窗是一種演算法模式，用於在陣列或字串的特定視窗大小上執行所需的操作。

### Intuition (直覺)
Imagine a window frame sliding over a sequence of data; as it moves one step right, one element enters and one leaves.
想像一個窗框在數據序列上滑動；當它向右移動一步時，一個元素進入，另一個元素離開。
Instead of recalculating the entire window, we only update the difference.
我們不重新計算整個視窗，而是僅更新差異部分。

### Complexity (複雜度)
*   **Time:** $O(N)$ — Each element is added and removed from the window at most once.
    **時間：** $O(N)$ — 每個元素最多被加入和移出視窗各一次。
*   **Space:** $O(1)$ (usually) or $O(K)$ if we need to store window elements explicitly.
    **空間：** 通常為 $O(1)$，若需明確儲存視窗元素則為 $O(K)$。

### When to Use (適用場景)
*   The problem asks for something related to a **contiguous** subarray or substring.
    問題詢問與**連續**子陣列或子字串相關的內容。
*   Keywords: "Maximum sum of subarray of size K", "Longest substring with...", "Smallest subarray with sum > S".
    關鍵字：「大小為 K 的子陣列最大和」、「具有...的最長子字串」、「總和大於 S 的最小子陣列」。

### When NOT to Use (不適用場景)
*   The required elements do not need to be contiguous (e.g., Subsequence problems).
    所需元素不需要連續（例如：子序列問題）。
*   The input data has no inherent order dependencies that a window can capture (e.g., standard Two Sum).
    輸入數據沒有視窗可以捕捉的內在順序依賴性（例如：標準的 Two Sum）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Fixed Window Size (固定視窗大小)
*   **Scenario:** Find the max/min/sum of a subarray with a fixed length $k$.
    **場景：** 尋找固定長度 $k$ 的子陣列之最大值/最小值/總和。
*   **Logic:** Initialize first $k$ elements. Then loop from $k$ to $n$, adding `arr[i]` and subtracting `arr[i-k]`.
    **邏輯：** 初始化前 $k$ 個元素。接著從 $k$ 迴圈至 $n$，加上 `arr[i]` 並減去 `arr[i-k]`。

### Pattern B: Variable Window Size (變動視窗大小)
*   **Scenario:** Find the longest or shortest subarray that satisfies a condition (e.g., sum $\ge$ target).
    **場景：** 尋找滿足特定條件（如總和 $\ge$ 目標值）的最長或最短子陣列。
*   **Logic:** Expand `right` pointer to satisfy condition; shrink `left` pointer to optimize (make it minimal) or restore validity.
    **邏輯：** 擴展 `right` 指標以滿足條件；收縮 `left` 指標以優化（使其最小化）或恢復合法性。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Sum Subarray of Size K (大小為 K 的最大子陣列和)

**Problem Statement:**
Given an array of integers and a number $k$, find the maximum sum of a subarray of size $k$.
給定一個整數陣列與數字 $k$，找出長度為 $k$ 的子陣列之最大總和。

**Input:** `[2, 1, 5, 1, 3, 2]`, `k = 3`
**Output:** `9` (Subarray `[5, 1, 3]`)

### Approach 1: Brute Force (暴力解)
Iterate through every index $i$, and for each $i$, calculate the sum of the next $k$ elements.
遍歷每個索引 $i$，並對每個 $i$ 計算接下來 $k$ 個元素的總和。
*   **Time:** $O(N \cdot K)$ — Inefficient for large $K$.
    **時間：** $O(N \cdot K)$ — 對於較大的 $K$ 效率低落。

### Approach 2: Sliding Window (Optimal) (滑動視窗 - 最佳解)
Maintain a running `currentSum`.
維護一個運行中的 `currentSum`。
As we move from index $i$ to $i+1$, we add `arr[i+1]` and subtract `arr[i-k+1]`.
當我們從索引 $i$ 移動到 $i+1$ 時，加上 `arr[i+1]` 並減去 `arr[i-k+1]`。

### TypeScript Implementation (TypeScript 實作)

```typescript
/**
 * Finds the maximum sum of any contiguous subarray of size k.
 * 找出大小為 k 的任意連續子陣列的最大總和。
 *
 * @param nums - The input array of integers (輸入的整數陣列)
 * @param k - The size of the sliding window (滑動視窗的大小)
 * @returns The maximum sum found (找到的最大總和)
 */
function maxSubarraySum(nums: number[], k: number): number | null {
    // Edge case: If array length is less than k, no solution exists.
    // 邊界情況：如果陣列長度小於 k，則不存在解。
    if (nums.length < k) return null;

    let maxSum = 0;
    let currentSum = 0;

    // Step 1: Calculate the sum of the first window.
    // 步驟 1：計算第一個視窗的總和。
    for (let i = 0; i < k; i++) {
        currentSum += nums[i];
    }
    
    // Initialize maxSum with the first window's sum.
    // 使用第一個視窗的總和初始化 maxSum。
    maxSum = currentSum;

    // Step 2: Slide the window from the k-th element to the end.
    // 步驟 2：將視窗從第 k 個元素滑動到末尾。
    for (let i = k; i < nums.length; i++) {
        // Add the new element entering the window.
        // 加上進入視窗的新元素。
        const incoming = nums[i];
        
        // Remove the element leaving the window.
        // 移除離開視窗的元素。
        // The element leaving is at index (i - k).
        // 離開的元素位於索引 (i - k)。
        const outgoing = nums[i - k];

        currentSum = currentSum + incoming - outgoing;

        // Update the maximum sum if the current window is larger.
        // 如果當前視窗更大，則更新最大總和。
        maxSum = Math.max(maxSum, currentSum);
    }

    return maxSum;
}

// Test case
console.log(maxSubarraySum([2, 1, 5, 1, 3, 2], 3)); // Output: 9
```

### Error Demonstration (錯誤示範)
A common mistake is re-initializing `currentSum` to 0 inside the loop, turning it back into $O(N \cdot K)$.
一個常見的錯誤是在迴圈內將 `currentSum` 重新初始化為 0，這會將其變回 $O(N \cdot K)$。

```typescript
// ❌ BAD PRACTICE: Nested loop disguised as sliding window
// ❌ 不良實踐：偽裝成滑動視窗的巢狀迴圈
for (let i = 0; i <= nums.length - k; i++) {
    let currentSum = 0; 
    for (let j = 0; j < k; j++) { // This inner loop kills performance
        currentSum += nums[i + j];
    }
    maxSum = Math.max(maxSum, currentSum);
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Contrast (描述與對比) |
| :--- | :--- |
| **Off-by-one Errors**<br>(差一錯誤) | **Issue:** Accessing `nums[i-k]` when `i < k` or loop bounds.<br>**Fix:** Initialize the first window separately (0 to k-1), then loop from `k` to `n-1`.<br>**問題：** 當 `i < k` 時存取 `nums[i-k]` 或迴圈邊界錯誤。<br>**解法：** 分開初始化第一個視窗（0 到 k-1），然後從 `k` 迴圈至 `n-1`。 |
| **Variable Window Logic**<br>(變動視窗邏輯) | **Confusion:** When to shrink the window (`left++`)?<br>**Rule:** Expand `right` to make it valid; shrink `left` to make it optimal (or valid again).<br>**混淆：** 何時收縮視窗（`left++`）？<br>**規則：** 擴展 `right` 使其合法；收縮 `left` 使其最佳化（或恢復合法）。 |
| **Sliding Window vs Two Pointers**<br>(滑動視窗 vs 雙指標) | **Contrast:** Sliding Window maintains a "state" between pointers. Two Pointers usually just compare values at ends.<br>**對比：** 滑動視窗在指標之間維護一個「狀態」。雙指標通常僅比較兩端的值。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This problem asks for a contiguous subarray with a constraint, which suggests a Sliding Window approach."
    **識別：** 「這個問題要求具有限制條件的連續子陣列，這暗示了滑動視窗的方法。」
2.  **Baseline:** "A brute force approach would take $O(N^2)$ or $O(N \cdot K)$."
    **基準：** 「暴力解法將花費 $O(N^2)$ 或 $O(N \cdot K)$。」
3.  **Optimize:** "We can optimize to $O(N)$ by reusing the sum from the previous window and just updating the head and tail."
    **優化：** 「我們可以透過重複利用前一個視窗的總和，僅更新頭尾來優化至 $O(N)$。」

### Whiteboard Strategy (白板策略)
*   Draw the array and use brackets `[` `]` to represent the window.
    畫出陣列並使用括號 `[` `]` 代表視窗。
*   Write down the variables: `windowStart`, `windowEnd`, `currentSum`, `maxSum`.
    寫下變數：`windowStart`, `windowEnd`, `currentSum`, `maxSum`。
*   Trace one step: Show `sum` changing as `[` moves right and `]` moves right.
    追蹤一步：展示當 `[` 向右移且 `]` 向右移時 `sum` 的變化。

### Common Follow-up (常見追問)
*   **Q:** What if the array contains negative numbers?
    **問：** 如果陣列包含負數怎麼辦？
    *   **A:** Fixed window logic stays the same. Variable window logic (like "subarray sum $\ge$ target") breaks because adding elements doesn't guarantee growth.
    *   **答：** 固定視窗邏輯不變。變動視窗邏輯（如「子陣列和 $\ge$ 目標」）會失效，因為增加元素不保證數值增長。

---

## 7. Practice Problems (練習題)

### 1. Easy: Maximum Average Subarray I (LeetCode 643)
*   **Problem:** Find the contiguous subarray of length `k` that has the maximum average value.
    **問題：** 找出長度為 `k` 且具有最大平均值的連續子陣列。
*   **Hint:** Same as "Max Sum", just divide by `k` at the end or compare sums directly.
    **提示：** 與「最大和」相同，僅需在最後除以 `k` 或直接比較總和。

### 2. Medium: Minimum Size Subarray Sum (LeetCode 209)
*   **Problem:** Find the minimal length of a contiguous subarray of which the sum is $\ge$ target.
    **問題：** 找出總和 $\ge$ 目標值的最小長度連續子陣列。
*   **Hint:** Variable window. Expand `right` until sum $\ge$ target, then increment `left` to shrink while sum $\ge$ target. Record min length.
    **提示：** 變動視窗。擴展 `right` 直到總和 $\ge$ 目標，然後增加 `left` 收縮視窗，同時保持總和 $\ge$ 目標。記錄最小長度。

### 3. Medium: Longest Substring Without Repeating Characters (LeetCode 3)
*   **Problem:** Find the length of the longest substring without repeating characters.
    **問題：** 找出不含重複字元的最長子字串長度。
*   **Hint:** Use a `Set` or `Map` to track characters in the window. If `s[right]` exists in Set, shrink `left` until duplicate is removed.
    **提示：** 使用 `Set` 或 `Map` 追蹤視窗內的字元。若 `s[right]` 存在於 Set 中，收縮 `left` 直到重複被移除。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Initialization:** Did I handle the first window (indices $0$ to $k-1$) correctly?
    **初始化：** 我是否正確處理了第一個視窗（索引 $0$ 到 $k-1$）？
*   [ ] **Bounds:** Is my loop condition correct (`i < n`)? Do I access `i-k` safely?
    **邊界：** 我的迴圈條件正確嗎（`i < n`）？我是否安全地存取了 `i-k`？
*   [ ] **Empty Input:** Did I handle `nums.length == 0` or `k > nums.length`?
    **空輸入：** 我是否處理了 `nums.length == 0` 或 `k > nums.length` 的情況？
*   [ ] **Update Logic:** Am I adding the *new* element and removing the *old* element correctly?
    **更新邏輯：** 我是否正確地加上*新*元素並移除*舊*元素？

---

## 9. Memory Anchors (記憶錨點)

### The "Caterpillar" (毛毛蟲)
*   **Visual:** Think of a caterpillar moving. It extends its head (expands window) and then pulls its tail (shrinks window).
    **圖像：** 想像一隻毛毛蟲在移動。它伸展頭部（擴展視窗），然後拉動尾巴（收縮視窗）。
*   **Application:** Especially for **Variable Windows**. Head moves to find potential solutions; tail moves to optimize.
    **應用：** 特別適用於**變動視窗**。頭部移動以尋找潛在解；尾部移動以進行優化。

### The "Train View" (火車窗景)
*   **Visual:** You are on a train looking out a fixed-size window. As the train moves, one tree enters your view, and one tree leaves.
    **圖像：** 你在火車上透過固定大小的窗戶向外看。當火車移動時，一棵樹進入視野，一棵樹離開視野。
*   **Application:** **Fixed Windows**. The number of items in view never changes, just the content.
    **應用：** **固定視窗**。視野中的物品數量從未改變，只有內容改變。