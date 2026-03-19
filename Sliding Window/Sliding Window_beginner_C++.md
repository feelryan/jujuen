Here is the comprehensive guide for **Sliding Window**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth (focusing on foundational mechanics and standard patterns), with **C++** implementation.

這是一份針對 **Sliding Window（滑動視窗）** 的完整教材，專為資深軟體工程師設計，難度調整為 **Beginner（基礎/入門）**（著重於基礎機制與標準模式），並使用 **C++** 實作。

---

# Sliding Window: Foundational Mechanics & Patterns
# 滑動視窗：基礎機制與模式

## 1. Learning Goals（學習目標）

*   **Identify Applicability:** Recognize problems involving contiguous subarrays or substrings that require optimization from $O(N^2)$ to $O(N)$.
    *   **識別適用性：** 辨識涉及連續子陣列或子字串，且需要將複雜度從 $O(N^2)$ 優化至 $O(N)$ 的問題。
*   **Master the "Caterpillar" Movement:** Understand the mechanics of expanding the `right` pointer and shrinking the `left` pointer.
    *   **掌握「毛毛蟲」移動法：** 理解擴張 `right` 指標與收縮 `left` 指標的運作機制。
*   **Differentiate Window Types:** Distinguish between Fixed Size Windows and Variable Size Windows.
    *   **區分視窗類型：** 分辨「固定大小視窗」與「可變大小視窗」的差異。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Sliding Window is a specific variation of the Two Pointers technique used primarily on arrays or strings.
滑動視窗是雙指標技巧的一種特定變體，主要用於陣列或字串。

Instead of re-calculating the entire subset every time, we maintain a "window" of state and update it incrementally as the window moves.
我們不每次重新計算整個子集，而是維護一個狀態「視窗」，並隨著視窗移動增量更新它。

Imagine looking at a film strip through a rectangular frame; you only see a portion at a time, and as you slide the frame, one picture enters and another leaves.
想像透過一個長方形框框看底片；你一次只能看到一部分，當你滑動框框時，一張畫面進入，另一張畫面離開。

### Complexity（複雜度）
*   **Time:** $O(N)$. Each element is added to the window once and removed at most once.
    *   **時間：** $O(N)$。每個元素被加入視窗一次，且最多被移除一次。
*   **Space:** $O(1)$ usually, unless auxiliary data structures (like Hash Maps) are needed for the window's state.
    *   **空間：** 通常為 $O(1)$，除非視窗狀態需要輔助資料結構（如雜湊表）。

### When to Use（適用場景）
*   Finding the **longest/shortest/number of** contiguous subarrays/substrings that satisfy a condition.
    *   尋找滿足特定條件的**最長/最短/數量**之連續子陣列或子字串。
*   Calculating a running average or sum of a fixed size.
    *   計算固定大小的移動平均或總和。

### When NOT to Use（不適用場景）
*   The problem involves non-contiguous elements (consider Dynamic Programming or Hashing).
    *   問題涉及非連續元素（考慮動態規劃或雜湊）。
*   Input data has negative numbers *and* you need a specific sum (Sliding Window breaks because expanding doesn't guarantee increasing sum; use Prefix Sum + Map).
    *   輸入資料包含負數*且*你需要特定總和（滑動視窗會失效，因為擴張不保證總和增加；應使用前綴和 + Map）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Fixed Size Window（固定大小視窗）
The window size $k$ is constant. We initialize the first $k$ elements, then slide one step at a time.
視窗大小 $k$ 是固定的。我們先初始化前 $k$ 個元素，然後一次滑動一步。

*   **Logic:** Add `arr[i]`, Remove `arr[i-k]`.
*   **邏輯：** 加入 `arr[i]`，移除 `arr[i-k]`。

### Pattern B: Variable Size Window (Shrinkable)（可變大小視窗——可收縮）
The window grows to satisfy a condition, then shrinks to optimize it (e.g., find minimum length).
視窗擴張以滿足條件，然後收縮以進行優化（例如：尋找最小長度）。

*   **Logic:** Expand `right` until valid -> Shrink `left` while valid -> Repeat.
*   **邏輯：** 擴張 `right` 直到合法 -> 當合法時收縮 `left` -> 重複。

---

## 4. Example Walkthrough（範例講解）

### Problem: Minimum Size Subarray Sum
### 問題：長度最小的子陣列

**Problem Statement:**
Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a subarray whose sum is greater than or equal to `target`. If none exists, return 0.
給定一個正整數陣列 `nums` 和一個正整數 `target`，回傳其總和大於或等於 `target` 的最小子陣列長度。若不存在，回傳 0。

**Input:** `target = 7, nums = [2,3,1,2,4,3]`
**Output:** `2` (Subarray `[4,3]` has sum 7)

### Approach: From Brute Force to Optimal
### 思路：從暴力解到最佳解

1.  **Brute Force ($O(N^2)$):**
    Iterate through every possible starting point `i`, and for each `i`, iterate forward `j` calculating the sum until it hits `target`.
    遍歷每個可能的起點 `i`，對於每個 `i`，向後遍歷 `j` 計算總和直到達到 `target`。

2.  **Optimization (Sliding Window - $O(N)$):**
    We use two pointers, `left` and `right`.
    我們使用雙指標，`left` 和 `right`。
    
    *   **Expand:** Move `right` to add numbers to `current_sum`.
        *   **擴張：** 移動 `right` 將數字加入 `current_sum`。
    *   **Check:** Once `current_sum >= target`, the window is valid.
        *   **檢查：** 一旦 `current_sum >= target`，視窗即為合法。
    *   **Shrink:** While valid, try to make the window smaller by moving `left` forward to find the minimal length.
        *   **收縮：** 當視窗合法時，嘗試透過移動 `left` 向前來縮小視窗，以尋找最小長度。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <algorithm>
#include <climits> // For INT_MAX

using namespace std;

class Solution {
public:
    int minSubArrayLen(int target, vector<int>& nums) {
        int n = nums.size();
        // Initialize answer to MAX to find minimum later
        // 初始化答案為 MAX 以便稍後尋找最小值
        int min_len = INT_MAX;
        
        // 'left' pointer for the start of the window
        // 'left' 指標代表視窗的起點
        int left = 0;
        
        // Current sum of the window
        // 視窗目前的總和
        int current_sum = 0;

        // 'right' pointer expands the window
        // 'right' 指標擴張視窗
        for (int right = 0; right < n; ++right) {
            // Add the new element to the window
            // 將新元素加入視窗
            current_sum += nums[right];

            // While the window satisfies the condition (sum >= target)
            // 當視窗滿足條件時（總和 >= target）
            while (current_sum >= target) {
                // Update the minimum length found so far
                // 更新目前找到的最小長度
                min_len = min(min_len, right - left + 1);

                // Shrink the window from the left to try and find a smaller valid window
                // 從左側收縮視窗，嘗試尋找更小的合法視窗
                current_sum -= nums[left];
                left++;
            }
        }

        // If min_len never changed, it means no valid subarray was found
        // 如果 min_len 從未改變，表示未找到合法的子陣列
        return (min_len == INT_MAX) ? 0 : min_len;
    }
};
```

### Why Brute Force Fails / Common Mistakes
### 為何暴力解失敗 / 常見錯誤

*   **Mistake:** Resetting `right` pointer to `left + 1` after finding a valid window.
    *   **錯誤：** 找到合法視窗後，將 `right` 指標重置為 `left + 1`。
*   **Correction:** `right` never moves back. Only `left` moves forward. This guarantees $O(N)$.
    *   **修正：** `right` 絕不往回走。只有 `left` 往前走。這保證了 $O(N)$。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Description (描述) |
| :--- | :--- |
| **While vs. If** | Inside the `for` loop, use `while` to shrink `left` if you need to find the *minimum* window or process *all* valid start positions. Use `if` only if the window size is fixed. <br> 在 `for` 迴圈內，若需尋找*最小*視窗或處理*所有*合法起點，使用 `while` 收縮 `left`。僅在視窗大小固定時使用 `if`。 |
| **Window Size** | The size is usually `right - left + 1`. A common off-by-one error is using `right - left`. <br> 大小通常是 `right - left + 1`。常見的差一錯誤是使用 `right - left`。 |
| **Index Out of Bounds** | Always ensure `left <= right` implicitly, though the loop logic usually handles this. Be careful when accessing `nums[right]` if incrementing manually. <br> 總是隱性確保 `left <= right`，雖然迴圈邏輯通常會處理這點。手動增加指標時，存取 `nums[right]` 需小心。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **State the approach:** "Since we are looking for a contiguous subarray, I will use the Sliding Window technique to optimize from $O(N^2)$ to $O(N)$."
    *   **陳述方法：** 「由於我們在尋找連續子陣列，我將使用滑動視窗技巧將複雜度從 $O(N^2)$ 優化至 $O(N)$。」
2.  **Define the Invariant:** "I will maintain a window `[left, right]` such that the sum of elements inside is tracked."
    *   **定義不變性：** 「我將維護一個視窗 `[left, right]`，並追蹤其中的元素總和。」

### Whiteboard Strategy（白板策略）
*   Draw the array and write `L` and `R` underneath indices.
    *   畫出陣列並在索引下方寫上 `L` 和 `R`。
*   Trace the variables: `current_sum`, `max_len`/`min_len`.
    *   追蹤變數：`current_sum`, `max_len`/`min_len`。

### Common Follow-ups（常見追問）
*   **Q:** What if the array contains negative numbers?
    *   **A:** Sliding window might fail because adding an element doesn't guarantee the sum increases. I would switch to **Prefix Sum + Hash Map**.
    *   **問：** 如果陣列包含負數怎麼辦？
    *   **答：** 滑動視窗可能會失效，因為加入元素不保證總和增加。我會改用 **前綴和 + 雜湊表**。

---

## 7. Practice Problems（練習題）

### Easy: Maximum Average Subarray I (Fixed Window)
### 易：最大平均子陣列 I（固定視窗）
*   **Prompt:** Find the contiguous subarray of length `k` that has the maximum average value.
    *   **題目：** 找出長度為 `k` 且具有最大平均值的連續子陣列。
*   **Hint:** Initialize sum of first `k`. Then loop from `k` to `n`, add `nums[i]`, subtract `nums[i-k]`.
    *   **提示：** 初始化前 `k` 個的總和。然後從 `k` 迴圈至 `n`，加上 `nums[i]`，減去 `nums[i-k]`。

### Medium: Longest Substring Without Repeating Characters (Variable Window)
### 中：無重複字元的最長子字串（可變視窗）
*   **Prompt:** Given a string, find the length of the longest substring without repeating characters.
    *   **題目：** 給定一個字串，找出不含重複字元的最長子字串長度。
*   **Hint:** Use a `std::unordered_set` or `vector<int>` (for ASCII) to track characters in the window. If `s[right]` exists in set, shrink `left` until it's removed.
    *   **提示：** 使用 `std::unordered_set` 或 `vector<int>`（針對 ASCII）追蹤視窗內的字元。若 `s[right]` 已存在集合中，收縮 `left` 直到該字元被移除。

### Hard (Conceptually): Longest Substring with At Most K Distinct Characters
### 難（觀念上）：至多包含 K 個不同字元的最長子字串
*   **Prompt:** Find the length of the longest substring that contains at most `k` distinct characters.
    *   **題目：** 找出至多包含 `k` 個不同字元的最長子字串長度。
*   **Hint:** Use a Hash Map to count frequencies. `map.size()` tells you the number of distinct characters. If `map.size() > k`, shrink `left` and decrement counts. Remove key if count becomes 0.
    *   **提示：** 使用雜湊表計算頻率。`map.size()` 告訴你不同字元的數量。若 `map.size() > k`，收縮 `left` 並減少計數。若計數歸零則移除該鍵。

---

## 8. Quick Checklists（快速檢核表）

Use this during your implementation or self-review.
在實作或自我審查時使用此表。

*   [ ] **Initialization:** Are `left`, `right`, and `current_result` initialized correctly? (e.g., `0` vs `INT_MAX`).
    *   **初始化：** `left`、`right` 和 `current_result` 是否正確初始化？（例如：`0` 對比 `INT_MAX`）。
*   [ ] **Loop Range:** Does `right` go from `0` to `n-1`?
    *   **迴圈範圍：** `right` 是否從 `0` 跑到 `n-1`？
*   [ ] **Shrink Condition:** Is the inner loop (`while`) condition correct? Does it shrink when the window is *valid* (for min problems) or *invalid* (for max problems)?
    *   **收縮條件：** 內部迴圈（`while`）條件是否正確？是在視窗*合法*時收縮（針對最小化問題）還是*不合法*時收縮（針對最大化問題）？
*   [ ] **Update Logic:** Did you remember to remove `nums[left]` from the state before doing `left++`?
    *   **更新邏輯：** 你是否記得在執行 `left++` 之前從狀態中移除 `nums[left]`？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Caterpillar (毛毛蟲)
*   **Visual:** Think of a caterpillar moving. It stretches its head forward (`right++`), eats some food (update state), and then pulls its tail forward (`left++`) to digest or move on.
    *   **圖像：** 想像一隻毛毛蟲在移動。牠將頭向前伸（`right++`），吃點食物（更新狀態），然後將尾巴向前拉（`left++`）以消化或繼續前進。

### The Accordion (手風琴)
*   **Visual:** The window expands and contracts like an accordion playing music. It never flips inside out (`left` never passes `right`).
    *   **圖像：** 視窗像演奏中的手風琴一樣擴張和收縮。它永遠不會內外翻轉（`left` 永遠不會超過 `right`）。