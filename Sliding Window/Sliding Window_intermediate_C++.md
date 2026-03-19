Here is a comprehensive guide to Sliding Window, tailored for a Senior Software Engineer, focusing on C++ implementation and interview strategy.

這是一份針對資深軟體工程師量身打造的 Sliding Window（滑動視窗）完整指南，著重於 C++ 實作與面試策略。

---

# Sliding Window Interview Guide (Intermediate/Advanced)
# 滑動視窗面試指南（中階/進階）

## 1. Learning Goals (學習目標)

By the end of this guide, you should be able to:
閱讀完本指南後，您應該能夠：

1.  **Distinguish between Fixed and Dynamic Window patterns immediately.**
    立即區分「固定視窗」與「動態視窗」的模式。
2.  **Master the "Expand-Shrink" state management framework to ensure O(N) complexity.**
    掌握「擴張-收縮」的狀態管理框架，以確保 O(N) 的時間複雜度。
3.  **Implement optimized solutions in C++ using `unordered_map`, `vector`, or `deque` correctly.**
    正確使用 C++ 的 `unordered_map`、`vector` 或 `deque` 來實作優化解法。
4.  **Articulate the "Amortized Analysis" to prove why nested loops are still linear time.**
    闡述「攤銷分析」以證明為何巢狀迴圈仍然是線性時間。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Sliding Window is an optimization technique used primarily on arrays or strings to convert nested loops into a single pass.
滑動視窗是一種主要用於陣列或字串的優化技巧，將巢狀迴圈轉換為單次遍歷。

Instead of recalculating the state for every subarray from scratch, we utilize the result of the previous window to calculate the current one.
我們不從頭重新計算每個子陣列的狀態，而是利用前一個視窗的結果來計算當前視窗。

### Complexity (複雜度)
-   **Time:** $O(N)$. Although there is often a `while` loop inside a `for` loop, each element is added and removed at most once.
    **時間：** $O(N)$。雖然 `for` 迴圈內通常有一個 `while` 迴圈，但每個元素最多被加入和移除各一次。
-   **Space:** $O(1)$ or $O(K)$ (where K is the size of the character set or window size).
    **空間：** $O(1)$ 或 $O(K)$（其中 K 是字元集大小或視窗大小）。

### When to Use (適用場景)
-   Input is a linear data structure (Array, String, Linked List).
    輸入是線性資料結構（陣列、字串、連結串列）。
-   Problem asks for the "Longest/Shortest/Number of" **contiguous** subarrays or substrings satisfying a condition.
    問題要求滿足特定條件的「最長/最短/數量」**連續**子陣列或子字串。

### When NOT to Use (不適用場景)
-   Input requires finding **non-contiguous** subsequences (Use DP or Backtracking).
    輸入需要尋找**非連續**子序列（使用動態規劃或回溯法）。
-   The array contains negative numbers and you are looking for a specific sum (Sliding Window breaks because expanding doesn't guarantee increasing sum; use Prefix Sum + Hash Map).
    陣列包含負數且你在尋找特定總和（滑動視窗會失效，因為擴張不保證總和增加；應使用前綴和 + 雜湊表）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Fixed Window Size (固定視窗大小)
Maintain a window of size `k`. As you move right, add `nums[i]` and remove `nums[i-k]`.
維持大小為 `k` 的視窗。向右移動時，加入 `nums[i]` 並移除 `nums[i-k]`。

### Pattern B: Dynamic Window - Shrinkable (動態視窗 - 可收縮)
Expand `right` until the window becomes invalid (or valid, depending on logic), then increment `left` to restore validity or minimize size.
擴張 `right` 直到視窗變為無效（或有效，視邏輯而定），然後增加 `left` 以恢復有效性或最小化視窗。

**Template (C++):**
```cpp
int left = 0, right = 0;
// Data structure to track window state (e.g., sum, count)
// 用於追蹤視窗狀態的資料結構（例如：總和、計數）
while (right < n) {
    // 1. Add right element to state
    // 1. 將右側元素加入狀態
    add(nums[right]);
    
    // 2. Shrink window while condition is broken (or met)
    // 2. 當條件被破壞（或滿足）時收縮視窗
    while (condition_is_false) {
        remove(nums[left]);
        left++;
    }
    
    // 3. Update result
    // 3. 更新結果
    update_result();
    
    right++;
}
```

---

## 4. Example Walkthrough (範例講解)

### Problem: Longest Substring Without Repeating Characters (LeetCode 3)
**問題：無重複字元的最長子字串**

Given a string `s`, find the length of the longest substring without repeating characters.
給定一個字串 `s`，找出其中不含重複字元的最長子字串長度。

### Approach (思路)

1.  **Brute Force (暴力法):** Check all substrings. $O(N^3)$ or $O(N^2)$.
    **暴力法：** 檢查所有子字串。$O(N^3)$ 或 $O(N^2)$。
2.  **Optimization (優化):** Use a Sliding Window. Keep expanding `right`. If `s[right]` is already in the window, shrink `left` until the duplicate is removed.
    **優化：** 使用滑動視窗。持續擴張 `right`。如果 `s[right]` 已經在視窗中，收縮 `left` 直到重複項被移除。
3.  **Data Structure:** Use `unordered_set` or `vector` (if ASCII) to track characters in the current window.
    **資料結構：** 使用 `unordered_set` 或 `vector`（若是 ASCII）來追蹤當前視窗內的字元。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_set>

using namespace std;

class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        // Use a set to store characters in the current window
        // 使用集合來儲存當前視窗內的字元
        unordered_set<char> windowChars;
        
        int left = 0;
        int maxLen = 0;
        int n = s.length();
        
        // Iterate right pointer from 0 to n-1
        // 右指標從 0 遍歷到 n-1
        for (int right = 0; right < n; ++right) {
            char currentChar = s[right];
            
            // While the current character exists in the set, it's a duplicate.
            // Shrink from the left.
            // 當前字元存在於集合中時，表示有重複。從左側收縮。
            while (windowChars.count(currentChar)) {
                windowChars.erase(s[left]);
                left++;
            }
            
            // Add the current character to the window
            // 將當前字元加入視窗
            windowChars.insert(currentChar);
            
            // Update the maximum length found so far
            // 更新目前找到的最大長度
            maxLen = max(maxLen, right - left + 1);
        }
        
        return maxLen;
    }
};
```

### Advanced Optimization (進階優化)
Instead of shrinking one by one, we can use a Map to store the *index* of each character. If a repeat is found, jump `left` directly to `index + 1`.
我們可以使用 Map 儲存每個字元的*索引*，而非逐一收縮。如果發現重複，直接將 `left` 跳轉到 `index + 1`。

```cpp
// Optimized version using vector as a direct-address table (for ASCII)
// 使用 vector 作為直接定址表的優化版本（適用於 ASCII）
int lengthOfLongestSubstringOptimized(string s) {
    // vector initialized to -1, acting as a map: char -> last_seen_index
    // 初始化為 -1 的 vector，作為 map 使用：字元 -> 最後出現的索引
    vector<int> charIndex(128, -1); 
    
    int left = 0;
    int maxLen = 0;
    
    for (int right = 0; right < s.length(); ++right) {
        char c = s[right];
        
        // If char was seen and is inside the current window (index >= left)
        // 如果字元曾出現過且位於當前視窗內（索引 >= left）
        if (charIndex[c] >= left) {
            // Move left directly past the previous occurrence
            // 直接將 left 移動到前一次出現位置的下一格
            left = charIndex[c] + 1;
        }
        
        // Update the last seen index of the character
        // 更新字元最後出現的索引
        charIndex[c] = right;
        
        maxLen = max(maxLen, right - left + 1);
    }
    
    return maxLen;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall |
| :--- | :--- |
| **While vs. If** | Inside the loop, use `while` to shrink, not `if`. You might need to remove multiple elements to satisfy the condition.<br>在迴圈內，使用 `while` 來收縮，而非 `if`。你可能需要移除多個元素才能滿足條件。 |
| **Window Size** | The size is usually `right - left + 1`. A common off-by-one error is using `right - left`.<br>視窗大小通常是 `right - left + 1`。常見的差一錯誤是使用 `right - left`。 |
| **Result Update** | Know *when* to update the result. For "Max" problems, update after expanding. For "Min" problems, update after the window becomes valid (inside the shrink loop).<br>知道*何時*更新結果。對於「最大」問題，擴張後更新。對於「最小」問題，視窗變為有效後（在收縮迴圈內）更新。 |
| **C++ Map Performance** | `std::map` is $O(\log K)$, `std::unordered_map` is $O(1)$. Always use `unordered_map` or `vector` (for fixed char sets) in interviews unless ordering is required.<br>`std::map` 是 $O(\log K)$，`std::unordered_map` 是 $O(1)$。除非需要排序，否則面試中一律使用 `unordered_map` 或 `vector`（針對固定字元集）。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Verbal Framework (口條框架)
Start by identifying the pattern:
"This problem asks for a contiguous subarray satisfying a condition. I can use the Sliding Window technique to solve this in O(N) time."
從識別模式開始：「這個問題要求滿足條件的連續子陣列。我可以使用滑動視窗技巧在 O(N) 時間內解決。」

### 2. Whiteboard Strategy (白板策略)
-   **Draw Pointers:** Write `L` and `R` explicitly under the array.
    **畫出指標：** 在陣列下方明確寫出 `L` 和 `R`。
-   **Trace State:** Create a small table on the side tracking your variables (e.g., `currentSum`, `map`, `maxLen`) as you walk through an example.
    **追蹤狀態：** 在旁邊建立一個小表格，隨著範例演練追蹤變數（如 `currentSum`、`map`、`maxLen`）。

### 3. Common Follow-ups (常見追問)
-   **Q:** What if the input is an infinite stream?
    **問：** 如果輸入是無限串流怎麼辦？
    **A:** We cannot store the whole string. We might need a ring buffer or focus only on the current window state.
    **答：** 我們無法儲存整個字串。可能需要環形緩衝區，或僅關注當前視窗狀態。
-   **Q:** How to handle a very large character set (Unicode)?
    **問：** 如何處理非常大的字元集（Unicode）？
    **A:** Use `unordered_map` instead of a fixed-size array/vector.
    **答：** 使用 `unordered_map` 代替固定大小的陣列/vector。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Warm-up)
**Problem:** Maximum Average Subarray I (LeetCode 643)
**Hint:** Fixed window size `k`. Initialize sum of first `k`, then slide: `sum += nums[i] - nums[i-k]`.
**提示：** 固定視窗大小 `k`。初始化前 `k` 個元素的總和，然後滑動：`sum += nums[i] - nums[i-k]`。

### Level 2: Intermediate (Core)
**Problem:** Permutation in String (LeetCode 567)
**Hint:** Fixed window size equal to `s1.length()`. Use two frequency arrays (or maps) and compare them. Or use one `count` variable to track matches.
**提示：** 固定視窗大小等於 `s1.length()`。使用兩個頻率陣列（或 map）進行比較。或者使用一個 `count` 變數來追蹤匹配數。

### Level 3: Advanced (Differentiation)
**Problem:** Sliding Window Maximum (LeetCode 239)
**Hint:** This requires a **Monotonic Deque**. The window slides, but finding the max in O(1) requires keeping indices in a deque sorted by their values in descending order.
**提示：** 這需要**單調雙端佇列（Monotonic Deque）**。視窗滑動，但要在 O(1) 內找到最大值，需要將索引保存在 deque 中，並按其數值降序排列。

---

## 8. Quick Checklists (快速檢核表)

Use this during your implementation:
在實作過程中使用此表：

-   [ ] **Initialization:** Are `left` and `right` initialized to 0?
    **初始化：** `left` 和 `right` 是否初始化為 0？
-   [ ] **Loop Condition:** Is the outer loop `right < n`?
    **迴圈條件：** 外層迴圈是否為 `right < n`？
-   [ ] **Shrink Logic:** Did I use `while` (not `if`) to fix an invalid window?
    **收縮邏輯：** 我是否使用 `while`（而非 `if`）來修正無效視窗？
-   [ ] **Boundary Checks:** When accessing `nums[right]` or `nums[left]`, are indices valid? (Usually handled by loop condition).
    **邊界檢查：** 存取 `nums[right]` 或 `nums[left]` 時，索引是否有效？（通常由迴圈條件處理）。
-   [ ] **Empty Input:** Did I handle `s.length() == 0` or `k > n`?
    **空輸入：** 我是否處理了 `s.length() == 0` 或 `k > n` 的情況？

---

## 9. Memory Anchors (記憶錨點)

### The Caterpillar (毛毛蟲)
Think of the window as a **caterpillar**.
將視窗想像成一隻**毛毛蟲**。
1.  It eats (expands `right`) to grow.
    它進食（擴張 `right`）以生長。
2.  If it gets too fat or eats something bad (invalid state), it pulls its tail (shrinks `left`) to digest or move forward.
    如果它太胖或吃到壞東西（無效狀態），它會收縮尾巴（收縮 `left`）來消化或前進。

### The Recycle Bin (資源回收桶)
When moving the window, don't throw away the calculation. **Recycle** the middle part.
移動視窗時，不要丟棄計算結果。**回收**中間的部分。
`New Sum = Old Sum + New Head - Old Tail`.
`新總和 = 舊總和 + 新頭部 - 舊尾巴`。