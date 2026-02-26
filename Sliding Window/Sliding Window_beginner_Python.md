# Sliding Window: The Foundation of Linear Scans
# 滑動視窗：線性掃描的基石

## 1. Learning Objectives (學習目標)

*   **Master the transition from Brute Force to Linear Time.**
    掌握從暴力解法（Brute Force）轉型至線性時間（Linear Time）的關鍵。
*   **Distinguish between "Fixed Size" and "Variable Size" windows.**
    區分「固定大小」與「可變大小」視窗的應用場景。
*   **Implement the "Add Right, Remove Left" mechanic flawlessly.**
    完美實作「右進左出」的視窗移動機制。
*   **Identify contiguous subarray problems instantly.**
    能夠瞬間識別出連續子陣列（Contiguous Subarray）類型的問題。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A computational technique that converts nested loops into a single loop by maintaining a subset of elements within a specific range (the window).
這是一種計算技巧，透過維護特定範圍（視窗）內的元素子集，將巢狀迴圈轉換為單一迴圈。

### Intuition (直覺)
Imagine a window frame sliding over a sequence of data.
想像一個窗框在數據序列上滑動。
Instead of recalculating the entire content of the window every time it moves, you simply remove the element leaving the window and add the element entering it.
與其每次移動都重新計算視窗內的全部內容，不如直接移除離開視窗的元素，並加入進入視窗的元素。

### Complexity (複雜度)
*   **Time Complexity:** $O(N)$ — Each element is added and removed at most once.
    **時間複雜度：** $O(N)$ — 每個元素最多被加入和移除一次。
*   **Space Complexity:** $O(1)$ (usually) or $O(K)$ if storing elements in a set/map.
    **空間複雜度：** 通常為 $O(1)$，若需在 Set/Map 中儲存元素則為 $O(K)$。

### When to Use (適用場景)
*   Finding the maximum/minimum/sum/average of a subarray of size `k`.
    尋找大小為 `k` 的子陣列之最大值/最小值/總和/平均值。
*   Finding the longest/shortest substring with a specific condition (e.g., distinct characters).
    尋找符合特定條件（如：不重複字元）的最長/最短子字串。
*   Keywords: "Contiguous", "Subarray", "Substring", "Sequential".
    關鍵字：「連續」、「子陣列」、「子字串」、「序列」。

### When NOT to Use (不適用場景)
*   Subsequence problems (elements not contiguous) — usually Dynamic Programming.
    子序列問題（元素不連續）— 通常使用動態規劃。
*   Problems where the order of elements does not matter at all (often Hash Maps/Sorting).
    元素順序完全不重要的問題（通常使用雜湊表或排序）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the "Beginner" level, we focus on the two most fundamental patterns.
針對「基礎」級別，我們專注於最根本的兩種模式。

### A. Fixed Size Window (固定大小視窗)
The window size `k` is constant. You slide the window one step at a time.
視窗大小 `k` 是固定的。你一次將視窗滑動一步。
*   **Logic:** Initialize first `k` elements -> Loop from `k` to `n` -> Add `nums[i]`, Remove `nums[i-k]`.
    **邏輯：** 初始化前 `k` 個元素 -> 從 `k` 迴圈至 `n` -> 加入 `nums[i]`，移除 `nums[i-k]`。

### B. Variable Size Window (可變大小視窗)
The window grows or shrinks based on a condition (e.g., sum < target).
視窗根據特定條件（例如：總和 < 目標值）進行擴張或收縮。
*   **Logic:** Expand `right` pointer to include elements -> While condition is broken, increment `left` pointer to shrink.
    **邏輯：** 擴張 `right` 指標以納入元素 -> 當條件被破壞時，增加 `left` 指標以收縮視窗。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Average Subarray I (Fixed Size)
### 問題：子陣列最大平均數 I（固定大小）

**Problem Statement:**
Given an integer array `nums` consisting of `n` elements, and an integer `k`.
給定一個包含 `n` 個元素的整數陣列 `nums`，以及一個整數 `k`。
Find a contiguous subarray whose length is equal to `k` that has the maximum average value.
找出長度為 `k` 且具有最大平均值的連續子陣列。

### Approach 1: Brute Force (暴力解)
Calculate the sum for every possible subarray of size `k`.
計算每一個可能的大小為 `k` 的子陣列總和。

*   **Flaw:** Repeated work. The sum of `nums[1]...nums[k-1]` is calculated twice for overlapping windows.
    **缺陷：** 重複做工。重疊視窗中的 `nums[1]...nums[k-1]` 總和被計算了兩次。
*   **Time Complexity:** $O(N \cdot K)$ — Can be $O(N^2)$ if $k \approx N/2$.
    **時間複雜度：** $O(N \cdot K)$ — 若 $k \approx N/2$ 則接近 $O(N^2)$。

### Approach 2: Sliding Window (Optimal)
### 方法 2：滑動視窗（最佳解）

1.  Calculate the sum of the first `k` elements.
    計算前 `k` 個元素的總和。
2.  Slide the window: Subtract the element falling out on the left, add the element coming in on the right.
    滑動視窗：減去左邊掉出的元素，加上右邊進來的元素。
3.  Track the maximum sum seen so far.
    追蹤目前為止見過的最大總和。

*   **Time Complexity:** $O(N)$
    **時間複雜度：** $O(N)$

### Python Solution (Reference)

```python
from typing import List

def findMaxAverage(nums: List[int], k: int) -> float:
    # Edge case: if the array is smaller than k (though constraints usually prevent this)
    # 邊界條件：如果陣列小於 k（雖然題目限制通常會防止這種情況）
    if len(nums) < k:
        return 0.0

    # 1. Initialize the first window
    # 1. 初始化第一個視窗
    # Calculate sum of the first k elements
    # 計算前 k 個元素的總和
    current_sum = sum(nums[:k])
    max_sum = current_sum

    # 2. Slide the window
    # 2. 滑動視窗
    # Start from index k and go to the end
    # 從索引 k 開始直到結束
    for i in range(k, len(nums)):
        # Core Logic: Add Right (nums[i]), Remove Left (nums[i-k])
        # 核心邏輯：加右 (nums[i])，去左 (nums[i-k])
        current_sum += nums[i] - nums[i - k]
        
        # Update max_sum if the new window is larger
        # 如果新視窗較大，更新 max_sum
        max_sum = max(max_sum, current_sum)

    # Return the average
    # 回傳平均值
    return max_sum / k
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Off-by-one Error**<br>差一錯誤 | Confusing indices when removing the left element. Usually, if current index is `i`, the element to remove is `i-k`.<br>移除左側元素時搞混索引。通常若當前索引為 `i`，需移除的元素為 `i-k`。 |
| **Variable Window "While"**<br>可變視窗的 While 迴圈 | In variable windows, use `while` (not `if`) to shrink the left side. You might need to remove multiple elements to satisfy the condition.<br>在可變視窗中，使用 `while`（而非 `if`）來收縮左側。你可能需要移除多個元素才能滿足條件。 |
| **Initialization**<br>初始化 | Forgetting to process the first `k` elements before the loop starts.<br>忘記在迴圈開始前先處理前 `k` 個元素。 |
| **Global vs Local**<br>全域與區域變數 | Confusing `current_sum` (local window) with `max_sum` (global answer).<br>混淆 `current_sum`（當前視窗）與 `max_sum`（全域答案）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This asks for a contiguous subarray property, which suggests a Sliding Window approach."
    **識別：** 「這題要求連續子陣列的屬性，這暗示了可以使用滑動視窗方法。」
2.  **Contrast:** "A brute force approach would be $O(N \cdot K)$, but we can optimize to $O(N)$ by reusing the overlapping part of the window."
    **對比：** 「暴力解法會是 $O(N \cdot K)$，但我們可以透過重複利用視窗重疊部分將其優化至 $O(N)$。」
3.  **Define Variables:** "I'll use `left` and `right` pointers (or just `i` and `i-k` for fixed size) and a `current_sum` variable."
    **定義變數：** 「我會使用 `left` 和 `right` 指標（若是固定大小則用 `i` 和 `i-k`），以及一個 `current_sum` 變數。」

### Whiteboard Strategy (白板策略)
*   Draw an array and draw a box around the first `k` elements.
    畫出一個陣列，並在框住前 `k` 個元素。
*   Draw an arrow showing the box moving right.
    畫一個箭頭顯示框框向右移動。
*   Write `+` under the new element and `-` under the old element to visualize the operation.
    在新元素下方寫 `+`，舊元素下方寫 `-` 以視覺化操作。

### Common Follow-up (常見追問)
*   **Q:** What if the input is a stream of data (infinite)?
    **問：** 如果輸入是資料流（無限長）怎麼辦？
    *   **A:** We cannot store all data. We just maintain the `current_sum` and a queue of size `k` to know what to remove.
    *   **答：** 我們無法儲存所有資料。我們只需維護 `current_sum` 和一個大小為 `k` 的佇列（Queue）來知道該移除什麼。

---

## 7. Practice Problems (練習題)

### 1. Easy (Beginner): Maximum Sum Subarray of Size K
*   **Goal:** Find max sum of contiguous subarray of size K.
    **目標：** 尋找大小為 K 的連續子陣列最大總和。
*   **Hint:** Exactly the same as the example, just return sum instead of average.
    **提示：** 與範例完全相同，只需回傳總和而非平均值。

### 2. Medium (Intermediate): Longest Substring Without Repeating Characters
*   **Goal:** Find length of longest substring with unique chars.
    **目標：** 尋找不含重複字元的最長子字串長度。
*   **Hint:** Variable size window. Use a `Set`. If `char` in set, shrink left until `char` is removed.
    **提示：** 可變大小視窗。使用 `Set`。若 `char` 已在集合中，收縮左側直到該 `char` 被移除。

### 3. Hard (Conceptual): Minimum Size Subarray Sum
*   **Goal:** Find minimal length subarray where sum $\ge$ target.
    **目標：** 尋找總和 $\ge$ target 的最小長度子陣列。
*   **Hint:** Variable size. Expand right to increase sum. Once sum $\ge$ target, shrink left to minimize length while keeping sum $\ge$ target.
    **提示：** 可變大小。向右擴張增加總和。一旦總和 $\ge$ target，向左收縮以最小化長度，同時保持總和 $\ge$ target。

---

## 8. Quick Checklists (快速檢核表)

Before you say "I'm done":
在你說「我寫完了」之前：

- [ ] **Initialization:** Did I handle the first window (indices `0` to `k-1`)?
    **初始化：** 我是否處理了第一個視窗（索引 `0` 到 `k-1`）？
- [ ] **Loop Range:** Does the loop go up to `len(nums)`? (Python `range` is exclusive at the end).
    **迴圈範圍：** 迴圈是否執行到 `len(nums)`？（Python 的 `range` 結尾是不包含的）。
- [ ] **Empty Input:** What if `nums` is empty or `k=0`?
    **空輸入：** 如果 `nums` 為空或 `k=0` 怎麼辦？
- [ ] **Type Safety:** If calculating average, did I return float? If sum, int?
    **型別安全：** 如果計算平均值，是否回傳浮點數？如果是總和，是否為整數？

---

## 9. Memory Anchors (記憶錨點)

### The "Caterpillar" (毛毛蟲)
Think of the window as a caterpillar crawling over a leaf.
將視窗想像成一隻在葉子上爬行的毛毛蟲。
*   **Fixed Size:** The caterpillar has a constant length. It moves one leg forward (add right), and pulls the last leg up (remove left).
    **固定大小：** 毛毛蟲長度固定。它將一隻腳向前移（加右），並收起最後一隻腳（去左）。
*   **Variable Size:** The caterpillar stretches its head forward to eat (expand right), and pulls its tail forward when it's full or needs to move (shrink left).
    **可變大小：** 毛毛蟲將頭向前伸以進食（向右擴張），當吃飽或需要移動時將尾巴向前拉（向左收縮）。