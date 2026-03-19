Here is the comprehensive guide for **Sliding Window (Advanced)**, tailored for a Senior Software Engineer, following the requested bilingual format and C++ implementation.

這是一份針對 **Sliding Window (進階)** 的完整指南，專為資深軟體工程師量身打造，遵循要求的雙語格式與 C++ 實作。

---

# Advanced Sliding Window Interview Guide
# 進階滑動視窗面試指南

## 1. Learning Goals (學習目標)

*   **Master the "Amortized Analysis" intuition.**
    掌握「攤銷分析」的直覺。
    *Understand why nested loops in sliding window result in $O(N)$ complexity, not $O(N^2)$.*
    *理解為何滑動視窗中的巢狀迴圈會導致 $O(N)$ 而非 $O(N^2)$ 的複雜度。*

*   **Differentiate between "Fixed Size" and "Variable Size" patterns.**
    區分「固定大小」與「可變大小」的模式。
    *Learn when to shrink the left pointer aggressively versus when to maintain a specific window width.*
    *學習何時該積極收縮左指標，以及何時該維持特定的視窗寬度。*

*   **Integrate with auxiliary data structures (Monotonic Queue / Hash Map).**
    結合輔助資料結構（單調佇列 / 雜湊表）。
    *Solve advanced problems like "Sliding Window Maximum" using `std::deque` for $O(1)$ extrema retrieval.*
    *利用 `std::deque` 解決如「滑動視窗最大值」等進階問題，以實現 $O(1)$ 的極值讀取。*

*   **Handle "Exactly K" constraints via "At Most K" transformation.**
    透過「至多 K」的轉換來處理「恰好 K」的限制。
    *Apply the technique: $Exact(K) = AtMost(K) - AtMost(K-1)$.*
    *應用此技巧：$Exact(K) = AtMost(K) - AtMost(K-1)$。*

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Sliding Window is an optimization technique used primarily on arrays or strings to convert a nested loop solution into a linear time solution.
滑動視窗是一種主要用於陣列或字串的優化技巧，將巢狀迴圈解法轉換為線性時間解法。
It involves maintaining a subset of data within a specific range (the window) that satisfies certain constraints.
它涉及在特定範圍（視窗）內維護滿足特定限制的資料子集。

### Intuition (直覺)
Instead of recalculating the properties of a subarray from scratch, we utilize the result of the previous window.
我們不從頭重新計算子陣列的屬性，而是利用前一個視窗的結果。
As the window moves, we add the new element entering from the right and remove the old element leaving from the left.
當視窗移動時，我們加入從右側進入的新元素，並移除從左側離開的舊元素。

### Complexity (複雜度)
*   **Time:** $O(N)$. Each element is added to the window once and removed at most once.
    **時間：** $O(N)$。每個元素被加入視窗一次，且最多被移除一次。
*   **Space:** $O(1)$ if using fixed variables, or $O(K)$/$O(\Sigma)$ if using a Hash Map/Set (where $\Sigma$ is the alphabet size).
    **空間：** 若使用固定變數則為 $O(1)$，若使用雜湊表/集合則為 $O(K)$/$O(\Sigma)$（其中 $\Sigma$ 為字母集大小）。

### When to Use (適用場景)
*   Finding the longest/shortest substring/subarray satisfying a condition.
    尋找滿足某條件的最長/最短子字串/子陣列。
*   Calculating a running average or sum.
    計算移動平均或總和。
*   String permutation or anagram matching.
    字串排列或異位構詞匹配。

### When NOT to Use (不適用場景)
*   Input contains negative numbers (for sum problems), breaking the monotonicity (adding an element doesn't guarantee growth).
    輸入包含負數（針對總和問題），這會破壞單調性（加入元素不保證增長）。
*   Problems requiring non-contiguous subsequences (usually Dynamic Programming).
    需要非連續子序列的問題（通常是動態規劃）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Fixed Window Size (固定視窗大小)
The window size $k$ is constant. We initialize the first $k$ elements, then slide one step at a time.
視窗大小 $k$ 是固定的。我們先初始化前 $k$ 個元素，然後一次滑動一步。

### B. Variable Window - Shrinkable (可變視窗 - 可收縮)
**Most common interview pattern.**
**最常見的面試模式。**
Expand `right` pointer to find a valid window, then shrink `left` pointer to optimize (e.g., find minimum length) or to restore validity.
擴展 `right` 指標以找到有效視窗，然後收縮 `left` 指標以進行優化（例如：尋找最小長度）或恢復有效性。

### C. Variable Window - Monotonic Queue (可變視窗 - 單調佇列)
**Advanced / Hard.**
**進階 / 困難。**
Used when we need the maximum/minimum inside the window in $O(1)$ time.
用於當我們需要在 $O(1)$ 時間內取得視窗內的最大值/最小值時。
We maintain a `std::deque` of indices where values are strictly increasing or decreasing.
我們維護一個儲存索引的 `std::deque`，其中的數值保持嚴格遞增或遞減。

---

## 4. Example Walkthrough (範例講解)

### Problem: Minimum Window Substring (LeetCode 76)
**Difficulty:** Hard
**難度：** 困難

### Problem Restatement (問題重述)
Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window.
給定兩個字串 `s` 和 `t`，回傳 `s` 中最小的視窗子字串，使得 `t` 中的每個字元（包含重複）都包含在該視窗內。
If there is no such substring, return the empty string `""`.
如果沒有這樣的子字串，則回傳空字串 `""`。

### Thought Process (思路)

1.  **Brute Force (暴力解):**
    Iterate all substrings of `s`, check if they contain `t`.
    遍歷 `s` 的所有子字串，檢查它們是否包含 `t`。
    Complexity: $O(N^3)$ or $O(N^2)$ depending on implementation. Too slow.
    複雜度：$O(N^3)$ 或 $O(N^2)$ 取決於實作。太慢了。

2.  **Optimization (優化):**
    Use two pointers, `left` and `right`.
    使用雙指標，`left` 和 `right`。
    Move `right` to expand until the window contains all chars of `t`.
    移動 `right` 擴展，直到視窗包含 `t` 的所有字元。
    Then, move `left` to shrink the window to minimize length while maintaining validity.
    接著，移動 `left` 收縮視窗以最小化長度，同時保持有效性。

3.  **Data Structure (資料結構):**
    Use a frequency map (array of size 128 for ASCII) to track character counts.
    使用頻率表（大小為 128 的陣列用於 ASCII）來追蹤字元計數。
    Use a variable `required` to track how many unique characters from `t` are still needed.
    使用變數 `required` 來追蹤還需要 `t` 中的多少個唯一字元。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <string>
#include <vector>
#include <climits>
#include <iostream>

using namespace std;

string minWindow(string s, string t) {
    // Edge case check
    // 邊界條件檢查
    if (s.empty() || t.empty()) return "";

    // Frequency map for characters in t. Using vector for performance over unordered_map.
    // t 中字元的頻率表。使用 vector 以獲得優於 unordered_map 的效能。
    vector<int> map(128, 0);
    for (char c : t) {
        map[c]++;
    }

    int left = 0, right = 0;
    int minLen = INT_MAX;
    int startIdx = 0;
    
    // Count of characters required to be found in the current window
    // 當前視窗中需要找到的字元數量
    int count = t.length(); 

    while (right < s.length()) {
        // 1. Expand window: Add s[right]
        // 1. 擴展視窗：加入 s[right]
        
        // If s[right] is a char required by t (map value > 0), decrease count
        // 如果 s[right] 是 t 需要的字元（map 值 > 0），減少 count
        if (map[s[right]] > 0) {
            count--;
        }
        
        // Decrease frequency in map (can go negative for chars not in t or extra chars)
        // 減少 map 中的頻率（對於不在 t 中的字元或多餘字元，值可能變為負數）
        map[s[right]]--;
        right++;

        // 2. Shrink window: While valid (count == 0), try to minimize
        // 2. 收縮視窗：當有效時（count == 0），嘗試最小化
        while (count == 0) {
            // Update global minimum if current window is smaller
            // 如果當前視窗更小，更新全域最小值
            if (right - left < minLen) {
                minLen = right - left;
                startIdx = left;
            }

            // Before moving left pointer, we need to remove s[left] from window
            // 在移動左指標之前，我們需要從視窗中移除 s[left]
            
            // Restore frequency in map
            // 恢復 map 中的頻率
            map[s[left]]++;
            
            // If map[s[left]] becomes > 0, it means we needed this char and just lost it.
            // 如果 map[s[left]] 變為 > 0，表示我們需要這個字元且剛才失去了它。
            // Therefore, the window is no longer valid, increment count.
            // 因此，視窗不再有效，增加 count。
            if (map[s[left]] > 0) {
                count++;
            }
            
            left++;
        }
    }

    return minLen == INT_MAX ? "" : s.substr(startIdx, minLen);
}
```

### Analysis (分析)
*   **Time Complexity:** $O(N + M)$, where $N$ is length of `s` and $M$ is length of `t`. `left` and `right` scan the string at most once.
    **時間複雜度：** $O(N + M)$，其中 $N$ 是 `s` 的長度，$M$ 是 `t` 的長度。`left` 和 `right` 最多掃描字串一次。
*   **Space Complexity:** $O(1)$ (since ASCII size is fixed at 128).
    **空間複雜度：** $O(1)$（因為 ASCII 大小固定為 128）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Nuance (陷阱 / 細節) |
| :--- | :--- |
| **While vs. If** (內層迴圈) | Use `while` to shrink the window as much as possible. Using `if` only shrinks once, which might not find the *minimal* window. <br> 使用 `while` 盡可能收縮視窗。使用 `if` 只會收縮一次，可能無法找到「最小」視窗。 |
| **Result Update** (更新結果位置) | For "Minimum" problems, update result *inside* the shrink loop (when valid). For "Maximum" problems, update result *after* the shrink loop (when valid). <br> 對於「最小」問題，在收縮迴圈「內」更新結果（當有效時）。對於「最大」問題，在收縮迴圈「後」更新結果（當有效時）。 |
| **Map Logic** (Map 邏輯) | Handling negative values in the map is tricky. A negative value usually means "we have extra of this character". <br> 處理 Map 中的負值很棘手。負值通常意味著「我們有多餘的這個字元」。 |
| **Off-by-one** (差一錯誤) | Be careful with substring length calculation: `right - left + 1` vs `right - left`. In my code, `right` is incremented *before* calculating length, so it's `right - left`. <br> 小心子字串長度計算：`right - left + 1` vs `right - left`。在我的程式碼中，`right` 在計算長度「前」已遞增，所以是 `right - left`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This problem asks for a contiguous subarray satisfying a condition, which suggests a Sliding Window approach."
    **識別：** 「這個問題要求滿足條件的連續子陣列，這暗示了滑動視窗的方法。」
2.  **Define Invariant:** "I will maintain a window `[left, right)` that attempts to satisfy the condition..."
    **定義不變性：** 「我將維護一個視窗 `[left, right)`，試圖滿足該條件...」
3.  **Explain Steps:** "I'll expand `right` to include elements and shrink `left` to optimize/validate."
    **解釋步驟：** 「我將擴展 `right` 以包含元素，並收縮 `left` 以進行優化/驗證。」

### Whiteboard Strategy (白板策略)
*   **Variable Names:** Use descriptive names like `windowStart`, `windowEnd` (or `left`, `right`), `charFrequency`. Avoid `i`, `j`.
    **變數命名：** 使用具描述性的名稱，如 `windowStart`, `windowEnd`（或 `left`, `right`），`charFrequency`。避免使用 `i`, `j`。
*   **Dry Run:** Before coding, trace a small example (e.g., `s = "ADOBECODEBANC", t = "ABC"`) to show you understand the pointer movements.
    **手動演練：** 在編碼前，追蹤一個小範例（例如 `s = "ADOBECODEBANC", t = "ABC"`）以顯示你理解指標的移動。

### Common Follow-ups (常見追問)
*   **Q:** What if the input is a stream?
    **問：** 如果輸入是串流怎麼辦？
    **A:** We cannot keep the whole string. We might need a ring buffer or just store the indices/counts relevant to the current window.
    **答：** 我們無法保留整個字串。我們可能需要環形緩衝區，或者只儲存與當前視窗相關的索引/計數。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Warm-up)
**Problem:** Maximum Sum Subarray of Size K.
**問題：** 大小為 K 的最大總和子陣列。
**Hint:** Fixed size window. Subtract `nums[i-k]` and add `nums[i]`.
**提示：** 固定大小視窗。減去 `nums[i-k]` 並加上 `nums[i]`。

### Level 2: Intermediate (Must Know)
**Problem:** Longest Substring Without Repeating Characters (LeetCode 3).
**問題：** 無重複字元的最長子字串 (LeetCode 3)。
**Hint:** Use a Set or Map. If `s[right]` exists in Set, shrink `left` until duplicate is removed.
**提示：** 使用 Set 或 Map。如果 `s[right]` 存在於 Set 中，收縮 `left` 直到重複被移除。

### Level 3: Advanced (Differentiation)
**Problem:** Sliding Window Maximum (LeetCode 239).
**問題：** 滑動視窗最大值 (LeetCode 239)。
**Hint:** Use a **Monotonic Deque**. Store indices. Keep elements in deque decreasing. Remove indices out of window from front. The front is always the max.
**提示：** 使用 **單調雙端佇列 (Monotonic Deque)**。儲存索引。保持 Deque 內元素遞減。從前端移除超出視窗的索引。前端永遠是最大值。

#### Advanced Solution Sketch (C++)
```cpp
// Core logic for Sliding Window Maximum
deque<int> dq; // Stores indices
vector<int> res;
for (int i = 0; i < nums.size(); ++i) {
    // 1. Remove indices out of window [i-k+1, i]
    if (!dq.empty() && dq.front() == i - k) dq.pop_front();
    
    // 2. Maintain monotonicity: remove elements smaller than current from back
    while (!dq.empty() && nums[dq.back()] < nums[i]) dq.pop_back();
    
    // 3. Add current index
    dq.push_back(i);
    
    // 4. Add result (once first window is formed)
    if (i >= k - 1) res.push_back(nums[dq.front()]);
}
```

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Initialization:** Are `left` and `right` initialized to 0?
    **初始化：** `left` 和 `right` 是否初始化為 0？
*   [ ] **Loop Condition:** Is it `right < n`?
    **迴圈條件：** 是否為 `right < n`？
*   [ ] **Shrink Logic:** Did I use `while` for variable windows? Did I update the global result inside/outside the loop correctly?
    **收縮邏輯：** 對於可變視窗我是否使用了 `while`？我是否在迴圈內/外正確更新了全域結果？
*   [ ] **State Update:** Did I update the hash map/counter *before* moving pointers?
    **狀態更新：** 我是否在移動指標*之前*更新了雜湊表/計數器？
*   [ ] **Complexity:** Is the inner loop operation actually amortized $O(1)$? (Avoid iterating the whole map inside the loop).
    **複雜度：** 內層迴圈操作真的是攤銷 $O(1)$ 嗎？（避免在迴圈內遍歷整個 Map）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Caterpillar (毛毛蟲)
Visualize the window as a caterpillar moving across a leaf.
將視窗想像成一隻在葉子上移動的毛毛蟲。
*   **Eating (Expand):** The head (`right`) moves forward to eat more leaf (add data).
    **進食（擴展）：** 頭部（`right`）向前移動以吃更多葉子（加入資料）。
*   **Digesting/Pooping (Shrink):** The tail (`left`) moves forward to excrete waste (remove data) when the caterpillar gets too full or needs to shrink.
    **消化/排泄（收縮）：** 當毛毛蟲太飽或需要收縮時，尾部（`left`）向前移動以排出廢物（移除資料）。

### The Accordion (手風琴)
The window expands and contracts like an accordion playing music.
視窗像演奏音樂的手風琴一樣擴張和收縮。
You pull it open (`right++`) to get range, and squeeze it (`left++`) to find the tightest fit.
你拉開它（`right++`）以取得範圍，並擠壓它（`left++`）以找到最緊密的貼合。