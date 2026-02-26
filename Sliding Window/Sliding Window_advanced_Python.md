# Advanced Algorithm Guide: Sliding Window
# 進階演算法指南：滑動視窗

## 1. Learning Goals (學習目標)

*   **Master the "Expand-Shrink" Paradigm:** Understand the precise conditions for expanding the right pointer (`right`) and shrinking the left pointer (`left`).
    **掌握「擴張-收縮」範式：** 理解擴張右指標 (`right`) 與收縮左指標 (`left`) 的精確條件。
*   **Optimize Auxiliary Data Structures:** Learn when to use a simple variable, a Hash Map, or a Monotonic Deque (Deq) within the window to maintain $O(N)$ complexity.
    **優化輔助資料結構：** 學習何時在視窗內使用簡單變數、雜湊表（Hash Map）或單調雙端佇列（Monotonic Deque）以維持 $O(N)$ 複雜度。
*   **Differentiate Window Types:** Quickly identify whether a problem requires a **Fixed Size Window** or a **Variable Size Window**.
    **區分視窗類型：** 快速識別問題需要的是 **固定大小視窗** 還是 **可變大小視窗**。
*   **Handle Advanced Constraints:** Solve problems involving "at most K", "exactly K", or continuous stream data processing.
    **處理進階限制：** 解決涉及「至多 K 個」、「恰好 K 個」或連續串流資料處理的問題。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Sliding Window is an optimization technique used primarily on arrays or strings to convert nested loops into a single loop.
滑動視窗是一種主要用於陣列或字串的優化技巧，旨在將巢狀迴圈轉換為單一迴圈。

It maintains a subset of elements (the window) that satisfies certain constraints while moving across the data.
它在遍歷資料時，維護一個滿足特定限制條件的元素子集（視窗）。

### Intuition (直覺)
Imagine a caterpillar crawling over a leaf: it extends its head (right pointer) to eat, and pulls its tail (left pointer) to move forward.
想像一隻毛毛蟲在葉子上爬行：它伸展頭部（右指標）去進食，並收縮尾部（左指標）以前進。

### Complexity (複雜度)
*   **Time:** $O(N)$. Each element is added to the window once and removed once.
    **時間：** $O(N)$。每個元素被加入視窗一次，並被移除一次。
*   **Space:** $O(1)$ (if only variables are used) or $O(K)$ (if a map/set is used, where K is the alphabet size or window size).
    **空間：** $O(1)$（若僅使用變數）或 $O(K)$（若使用 map/set，K 為字母集大小或視窗大小）。

### When to Use (適用場景)
*   Input is a linear data structure (Array, String, Linked List).
    輸入為線性資料結構（陣列、字串、連結串列）。
*   Problem asks for the **longest/shortest** substring/subarray, or a specific **target value** (sum, average).
    問題要求尋找 **最長/最短** 的子字串/子陣列，或特定的 **目標值**（總和、平均值）。
*   The required result must be **contiguous**.
    所求結果必須是 **連續的**。

### When NOT to Use (不適用場景)
*   The problem requires a non-contiguous subsequence (usually Dynamic Programming).
    問題需要非連續的子序列（通常是動態規劃）。
*   The array contains negative numbers *and* you are looking for a specific sum (Sliding Window breaks because expanding doesn't guarantee increasing sum; use Prefix Sum + HashMap instead).
    陣列包含負數 *且* 你在尋找特定總和（滑動視窗會失效，因為擴張不保證總和增加；應改用前綴和 + HashMap）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Fixed Size Window (固定大小視窗)
*   **Scenario:** "Find the max sum of any contiguous subarray of size K."
    **場景：** 「找出長度為 K 的連續子陣列的最大總和。」
*   **Logic:** Initialize window of size K. Slide one step: add `arr[i]`, remove `arr[i-k]`.
    **邏輯：** 初始化大小為 K 的視窗。滑動一步：加入 `arr[i]`，移除 `arr[i-k]`。

### B. Variable Size - Shrinkable (可變大小 - 可收縮)
*   **Scenario:** "Find the smallest subarray with sum $\ge$ S."
    **場景：** 「找出總和 $\ge$ S 的最小子陣列。」
*   **Logic:** Expand `right` until valid. While valid, record answer and shrink `left` to find the minimum.
    **邏輯：** 擴張 `right` 直到符合條件。當條件符合時，記錄答案並收縮 `left` 以尋找最小值。

### C. Variable Size - Longest with Constraint (可變大小 - 帶限制的最長)
*   **Scenario:** "Longest substring with at most K distinct characters."
    **場景：** 「至多包含 K 個不同字元的最長子字串。」
*   **Logic:** Expand `right`. If constraint broken (distinct > K), shrink `left` until valid again.
    **邏輯：** 擴張 `right`。若違反限制（不同字元數 > K），收縮 `left` 直到再次符合條件。

### D. Sliding Window with Auxiliary Structure (帶輔助結構的滑動視窗)
*   **Scenario:** "Sliding Window Maximum."
    **場景：** 「滑動視窗最大值。」
*   **Logic:** Use a **Monotonic Deque** to store indices of potential max values.
    **邏輯：** 使用 **單調雙端佇列** 來儲存潛在最大值的索引。

---

## 4. Example Walkthrough (範例講解)

### Problem: Minimum Window Substring (Hard)
### 題目：最小覆蓋子字串 (Hard)

**Problem Statement:**
Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `""`.
給定兩個字串 `s` 和 `t`，回傳 `s` 中包含 `t` 所有字元（含重複）的最小視窗子字串。若不存在此類子字串，則回傳空字串 `""`。

**Example:**
Input: `s = "ADOBECODEBANC"`, `t = "ABC"`
Output: `"BANC"`

---

### Thought Process (思路)

**1. Brute Force (暴力解):**
Generate all substrings of `s`, check if they contain all chars of `t`.
產生 `s` 的所有子字串，檢查它們是否包含 `t` 的所有字元。
*   Complexity: $O(N^3)$ (Generating $N^2$ substrings * checking $O(N)$).
*   複雜度：$O(N^3)$（產生 $N^2$ 個子字串 * 檢查 $O(N)$）。

**2. Optimization (優化):**
Use two pointers `left` and `right`. Maintain a frequency map of the current window.
使用雙指標 `left` 和 `right`。維護當前視窗的頻率表。
*   Expand `right` until the window contains all chars of `t`.
    擴張 `right` 直到視窗包含 `t` 的所有字元。
*   Once valid, shrink `left` to minimize the window size while keeping it valid.
    一旦符合條件，收縮 `left` 以在保持符合條件的前提下最小化視窗大小。

**3. Efficient Validation (高效驗證):**
Instead of checking the full map every time ($O(26)$ or $O(52)$), maintain a variable `formed` (or `count`) that tracks how many unique characters satisfy the requirement.
與其每次檢查完整的 map（$O(26)$ 或 $O(52)$），不如維護一個變數 `formed`（或 `count`）來追蹤有多少個唯一字元滿足了要求。

---

### Python Solution (參考解)

```python
from collections import Counter

def minWindow(s: str, t: str) -> str:
    if not t or not s:
        return ""

    # Dictionary to keep a count of all the unique characters in t.
    # 字典用於記錄 t 中所有唯一字元的計數。
    dict_t = Counter(t)

    # Number of unique characters in t, which need to be present in the desired window.
    # t 中需要出現在目標視窗內的唯一字元數量。
    required = len(dict_t)

    # Left and Right pointer
    # 左指標與右指標
    l, r = 0, 0

    # formed is used to keep track of how many unique characters in t
    # are present in the current window in its desired frequency.
    # formed 用於追蹤當前視窗中，有多少個 t 的唯一字元已達到所需頻率。
    formed = 0

    # Dictionary which keeps a count of all the unique characters in the current window.
    # 字典用於記錄當前視窗中所有唯一字元的計數。
    window_counts = {}

    # ans tuple of the form (window length, left, right)
    # ans 元組格式為 (視窗長度, 左邊界, 右邊界)
    # Initialize with infinity for length to find minimum.
    # 初始化長度為無窮大以便尋找最小值。
    ans = float("inf"), None, None

    while r < len(s):
        # Add one character from the right to the window
        # 將右側的一個字元加入視窗
        character = s[r]
        window_counts[character] = window_counts.get(character, 0) + 1

        # If the frequency of the current character added equals to the desired count in t
        # then increment the formed count.
        # 若當前加入字元的頻率等於 t 中所需的計數，則增加 formed 計數。
        if character in dict_t and window_counts[character] == dict_t[character]:
            formed += 1

        # Try and contract the window till the point where it ceases to be 'desirable'.
        # 嘗試收縮視窗，直到它不再「符合要求」為止。
        while l <= r and formed == required:
            character = s[l]

            # Save the smallest window until now.
            # 儲存目前為止最小的視窗。
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r)

            # The character at the position pointed by the `left` pointer is no longer a part of the window.
            # 左指標指向的字元不再屬於視窗的一部分。
            window_counts[character] -= 1
            
            # If this character was required and its count falls below required, decrement formed.
            # 若此字元是必須的且其計數低於需求，則減少 formed。
            if character in dict_t and window_counts[character] < dict_t[character]:
                formed -= 1

            # Move the left pointer ahead, this would help to look for a new window.
            # 移動左指標向前，這有助於尋找新的視窗。
            l += 1

        # Keep expanding the window once we are done contracting.
        # 完成收縮後，繼續擴張視窗。
        r += 1

    # Return the smallest window or empty string if no such window exists.
    # 回傳最小視窗，若不存在則回傳空字串。
    return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(|S| + |T|)$. `right` moves $N$ times, `left` moves at most $N$ times.
    **時間：** $O(|S| + |T|)$。`right` 移動 $N$ 次，`left` 最多移動 $N$ 次。
*   **Space:** $O(|S| + |T|)$ for the hash maps (or $O(1)$ if char set is fixed like ASCII).
    **空間：** $O(|S| + |T|)$ 用於雜湊表（若字元集固定如 ASCII 則為 $O(1)$）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **`while` vs `if`** | Inside the outer loop, use `while` to shrink the window, not `if`. You might need to shrink multiple times for one expansion.<br>在外層迴圈內，使用 `while` 而非 `if` 來收縮視窗。一次擴張可能需要多次收縮。 |
| **Subarray vs Subsequence** | Window only works for **contiguous** subarrays. For subsequences, think DP or Two Pointers (Greedy).<br>視窗僅適用於 **連續** 子陣列。對於子序列，考慮 DP 或雙指標（貪婪）。 |
| **Window Size Calculation** | The size is `right - left + 1`. A common off-by-one error is using `right - left`.<br>大小為 `right - left + 1`。常見的差一錯誤是使用 `right - left`。 |
| **Negative Numbers** | If input has negative numbers and you want `sum >= k`, simple sliding window fails (monotonicity is broken).<br>若輸入含負數且要求 `sum >= k`，簡單滑動視窗會失效（單調性被破壞）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify:** "Since we are looking for a contiguous substring satisfying condition X, I'm thinking of using the Sliding Window technique."
    **識別：** 「由於我們在尋找滿足條件 X 的連續子字串，我考慮使用滑動視窗技巧。」
2.  **Define Invariants:** "I will maintain a window `[left, right]` that tries to satisfy the condition."
    **定義不變量：** 「我將維護一個試圖滿足條件的視窗 `[left, right]`。」
3.  **Explain Movement:** "I'll expand `right` to include elements, and shrink `left` when the constraint is violated (or met, depending on min/max problem)."
    **解釋移動：** 「我將擴張 `right` 以包含元素，並在違反限制（或滿足限制，視求極大/極小而定）時收縮 `left`。」

### Whiteboard Strategy (白板策略)
*   Write `L` and `R` explicitly on example inputs.
    在範例輸入上明確寫出 `L` 和 `R`。
*   Use a table to track `Window State` (e.g., Map counts) vs `Required State`.
    使用表格追蹤 `視窗狀態`（如 Map 計數）與 `需求狀態` 的對比。

### Common Follow-ups (常見追問)
*   **Q:** What if the input is a stream (infinite)?
    **問：** 如果輸入是串流（無限）怎麼辦？
    *   **A:** We can't store everything. We might need a ring buffer or process in chunks, but the window logic persists locally.
    *   **答：** 我們無法儲存所有內容。可能需要環形緩衝區或分塊處理，但視窗邏輯在局部仍然適用。

---

## 7. Practice Problems (練習題)

### Easy: Maximum Average Subarray I (LeetCode 643)
*   **Hint:** Fixed size window. Compute initial sum, then slide: `sum += nums[i] - nums[i-k]`.
    **提示：** 固定大小視窗。計算初始總和，然後滑動：`sum += nums[i] - nums[i-k]`。
*   **Goal:** Practice basic fixed-window mechanics without re-calculating sums.
    **目標：** 練習基本的固定視窗機制，避免重複計算總和。

### Medium: Longest Repeating Character Replacement (LeetCode 424)
*   **Hint:** Condition is `(window_len - max_freq_char) <= k`. Don't need to shrink `max_freq` perfectly accurately when shrinking window (advanced trick).
    **提示：** 條件是 `(視窗長度 - 出現最多次字元的頻率) <= k`。收縮視窗時不需要完美精確地更新 `max_freq`（進階技巧）。
*   **Goal:** Learn to derive the mathematical condition for the window validity.
    **目標：** 學習推導視窗有效性的數學條件。

### Hard: Subarrays with K Different Integers (LeetCode 992)
*   **Hint:** "Exactly K" is hard. Convert to `atMost(K) - atMost(K-1)`.
    **提示：** 「恰好 K 個」很難。轉換為 `至多(K) - 至多(K-1)`。
*   **Goal:** Master the "At Most" pattern to solve "Exactly" problems.
    **目標：** 掌握「至多」模式以解決「恰好」類問題。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Monotonicity Check:** Does adding an element *always* increase/maintain the state (e.g., sum, count)? If negatives exist, be careful.
    **單調性檢查：** 加入元素是否 *總是* 增加/維持狀態（如總和、計數）？若存在負數，請小心。
*   [ ] **Initialization:** Did you handle the case where `k > n` or string is empty?
    **初始化：** 你是否處理了 `k > n` 或字串為空的情況？
*   [ ] **Shrink Logic:** Is it `while condition:` or `if condition:`? (Usually `while` for variable windows).
    **收縮邏輯：** 是 `while condition:` 還是 `if condition:`？（可變視窗通常用 `while`）。
*   [ ] **Result Update:** Are you updating the result *before* or *after* shrinking? (Depends on if you want valid max or valid min).
    **結果更新：** 你是在收縮 *前* 還是 *後* 更新結果？（取決於你要找合法的最大值還是最小值）。

---

## 9. Memory Anchors (記憶錨點)

### The "Accordion" (手風琴)
Think of the window as an **accordion**.
把視窗想像成一把 **手風琴**。
*   **Expand (Pull out):** To capture more music (data).
    **擴張（拉開）：** 為了捕捉更多音樂（資料）。
*   **Shrink (Push in):** When it gets too wide to handle or to find a tighter tune.
    **收縮（推入）：** 當它變得太寬無法控制，或為了尋找更緊湊的曲調時。

### The "Valid Sandwich" (合法三明治)
*   You want the thickest sandwich (Max Window) that fits in your mouth (Constraint).
    你想要塞進嘴裡（限制）的最厚三明治（最大視窗）。
*   Keep adding layers (Right++) until you can't open your mouth wide enough. Then remove layers from the bottom (Left++) until it fits again.
    持續加層（Right++）直到嘴巴張不開。然後從底部移除層（Left++）直到再次合適。