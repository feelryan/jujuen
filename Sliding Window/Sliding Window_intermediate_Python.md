# Sliding Window: Intermediate to Advanced Guide
# 滑動視窗：中階至進階指南

## 1. Learning Objectives (學習目標)

1.  **Master the "Expand-Shrink" Paradigm**: Understand precisely when to expand the right pointer and when to shrink the left pointer to satisfy constraints.
    **掌握「擴張-收縮」範式**：精確理解何時擴張右指標，以及何時收縮左指標以滿足限制條件。
2.  **Optimize Inner Loop Operations**: Learn how to validate the window in $O(1)$ time using HashMaps or auxiliary variables, avoiding $O(K)$ scans.
    **優化內層迴圈操作**：學習如何使用雜湊表（HashMaps）或輔助變數在 $O(1)$ 時間內驗證視窗狀態，避免 $O(K)$ 的掃描。
3.  **Distinguish Subarray vs. Subsequence**: Clearly identify when Sliding Window applies (contiguous) versus when Dynamic Programming is needed (non-contiguous).
    **區分「子陣列」與「子序列」**：清楚識別何時適用滑動視窗（連續），以及何時需要動態規劃（非連續）。
4.  **Handle Fixed vs. Variable Sizes**: Recognize the pattern differences between finding a fixed-length optimal solution and a variable-length one.
    **處理「固定」與「可變」大小**：識別尋找固定長度最佳解與可變長度最佳解之間的模式差異。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Sliding Window is an optimization technique used primarily on arrays or strings to solve problems involving contiguous subarrays or substrings.
滑動視窗是一種優化技巧，主要用於陣列或字串，解決涉及連續子陣列或子字串的問題。

It converts a nested loop brute force approach into a single linear pass.
它將巢狀迴圈的暴力解法轉換為單次線性掃描。

### Intuition (直覺)
Instead of recalculating the properties of a subarray from scratch as we move, we utilize the overlapping part of the previous window.
我們不需在移動時從頭重新計算子陣列的屬性，而是利用前一個視窗的重疊部分。

Think of it as a window frame sliding over data: when it moves, one element enters (right) and one leaves (left).
將其想像為一個在資料上滑動的窗框：當它移動時，一個元素進入（右側），一個元素離開（左側）。

### Complexity (複雜度)
-   **Time**: $O(N)$. Each element is added and removed from the window at most once.
    **時間**：$O(N)$。每個元素最多被加入和移出視窗各一次。
-   **Space**: $O(1)$ or $O(K)$ (where $K$ is the size of the character set or auxiliary structure).
    **空間**：$O(1)$ 或 $O(K)$（其中 $K$ 是字元集大小或輔助結構的大小）。

### When to Use (適用場景)
-   Input is a linear data structure (Array, String, Linked List).
    輸入是線性資料結構（陣列、字串、連結串列）。
-   Problem asks for the "longest", "shortest", or "target value" of a **contiguous** subarray/substring.
    問題要求尋找**連續**子陣列/子字串的「最長」、「最短」或「目標值」。

### When NOT to Use (不適用場景)
-   Input requires non-contiguous selection (e.g., Longest Increasing Subsequence -> use DP).
    輸入需要非連續選取（例如：最長遞增子序列 -> 使用 DP）。
-   The array contains negative numbers and the problem asks for a sum target (monotonicity is broken -> use Prefix Sum + HashMap).
    陣列包含負數且問題要求總和目標（單調性被破壞 -> 使用前綴和 + HashMap）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Fixed Window Size (固定視窗大小)
-   **Goal**: Find the max/min sum or average of a subarray of size `k`.
    **目標**：尋找大小為 `k` 的子陣列之最大/最小總和或平均值。
-   **Logic**: Initialize window of size `k`. Loop from `k` to `n`, add `nums[i]`, remove `nums[i-k]`.
    **邏輯**：初始化大小為 `k` 的視窗。迴圈從 `k` 到 `n`，加入 `nums[i]`，移除 `nums[i-k]`。

### Pattern B: Variable Window Size - Shrinkable (可變視窗大小 - 可收縮)
-   **Goal**: Find the longest/shortest subarray meeting a criteria (e.g., sum $\ge$ target).
    **目標**：尋找符合條件（例如：總和 $\ge$ 目標值）的最長/最短子陣列。
-   **Logic**:
    1.  Expand `right` pointer to include elements.
        擴張 `right` 指標以包含元素。
    2.  While the condition is invalid (or valid, depending on min/max goal), shrink `left` pointer.
        當條件無效（或有效，取決於求最小/最大值目標）時，收縮 `left` 指標。
    3.  Update the global optimum.
        更新全域最佳解。

---

## 4. Example Walkthrough (範例講解)

### Problem: Minimum Window Substring (Hard)
### 問題：最小覆蓋子字串（困難）

**Problem Statement (問題重述)**:
Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `""`.
給定兩個字串 `s` 和 `t`，回傳 `s` 中包含 `t` 所有字元（含重複字元）的最小視窗子字串。若不存在此類子字串，則回傳空字串 `""`。

**Brute Force Approach (暴力思路)**:
Iterate all substrings of `s` ($O(N^2)$), and for each substring, count characters to check if it covers `t` ($O(N)$). Total: $O(N^3)$.
遍歷 `s` 的所有子字串（$O(N^2)$），並對每個子字串計算字元以檢查是否覆蓋 `t`（$O(N)$）。總計：$O(N^3)$。

**Optimized Approach (最佳解思路)**:
Use a Variable Sliding Window with two HashMaps (or arrays for ASCII).
使用搭配兩個 HashMaps（或 ASCII 陣列）的可變滑動視窗。

1.  **Expand**: Move `right` to add characters. Update the window's frequency map.
    **擴張**：移動 `right` 加入字元。更新視窗的頻率表。
2.  **Check**: Maintain a variable `formed` to track how many unique characters from `t` have their frequency requirements met in the current window.
    **檢查**：維護一個變數 `formed` 來追蹤目前視窗中，有多少來自 `t` 的獨特字元已滿足頻率需求。
3.  **Shrink**: Once `formed` equals the number of unique chars in `t`, the window is valid. Try to shrink from `left` to find the *minimum* valid window.
    **收縮**：一旦 `formed` 等於 `t` 中獨特字元的數量，視窗即為有效。嘗試從 `left` 收縮以找到「最小」有效視窗。

**Python Solution (Python 參考解)**:

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""

    # Dictionary which keeps a count of all the unique characters in t.
    # 字典用於記錄 t 中所有獨特字元的計數。
    dict_t = Counter(t)

    # Number of unique characters in t, which need to be present in the desired window.
    # t 中獨特字元的數量，這些字元必須出現在目標視窗中。
    required = len(dict_t)

    # Left and Right pointer
    # 左指標與右指標
    l, r = 0, 0

    # formed is used to keep track of how many unique characters in t
    # are present in the current window in its desired frequency.
    # formed 用於追蹤目前視窗中，有多少 t 的獨特字元已滿足其目標頻率。
    formed = 0

    # Dictionary which keeps a count of all the unique characters in the current window.
    # 字典用於記錄目前視窗中所有獨特字元的計數。
    window_counts = {}

    # ans tuple of the form (window length, left, right)
    # ans 元組格式為 (視窗長度, 左邊界, 右邊界)
    # Initialize with infinity for length to find minimum.
    # 初始化長度為無限大以便尋找最小值。
    ans = float("inf"), None, None

    while r < len(s):
        # Add one character from the right to the window
        # 從右側將一個字元加入視窗
        character = s[r]
        window_counts[character] = window_counts.get(character, 0) + 1

        # If the frequency of the current character added equals to the
        # desired count in t then increment the formed count.
        # 如果目前加入字元的頻率等於 t 中的目標計數，則增加 formed 計數。
        if character in dict_t and window_counts[character] == dict_t[character]:
            formed += 1

        # Try and contract the window till the point where it ceases to be 'desirable'.
        # 嘗試收縮視窗，直到它不再「符合要求」為止。
        while l <= r and formed == required:
            character = s[l]

            # Save the smallest window until now.
            # 儲存目前的最小視窗。
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r)

            # The character at the position pointed by the
            # `left` pointer is no longer a part of the window.
            # `left` 指標指向的字元不再屬於視窗的一部分。
            window_counts[character] -= 1
            
            # If this character was in t and its count falls below required, update formed.
            # 如果此字元在 t 中且其計數低於需求，更新 formed。
            if character in dict_t and window_counts[character] < dict_t[character]:
                formed -= 1

            # Move the left pointer ahead, this would help to look for a new window.
            # 將左指標向前移動，這有助於尋找新的視窗。
            l += 1

        # Keep expanding the window once we are done contracting.
        # 完成收縮後，繼續擴張視窗。
        r += 1

    return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]
```

**Complexity Analysis (複雜度分析)**:
-   **Time**: $O(|S| + |T|)$. We iterate `right` once over `s`, and `left` once over `s`. Inner operations are $O(1)$.
    **時間**：$O(|S| + |T|)$。我們將 `right` 遍歷 `s` 一次，`left` 遍歷 `s` 一次。內部操作為 $O(1)$。
-   **Space**: $O(|S| + |T|)$ for the hash maps.
    **空間**：$O(|S| + |T|)$ 用於雜湊表。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **While vs. If** | In variable windows, use `while` to shrink the left pointer. Using `if` only shrinks once, missing smaller valid windows. <br> 在可變視窗中，使用 `while` 來收縮左指標。使用 `if` 只會收縮一次，會錯過更小的有效視窗。 |
| **Update Order** | Updating the result (min/max) inside the `while` loop vs. outside matters. For "Minimum Window", update *inside* the shrink loop (when valid). For "Longest Substring", update *after* the shrink loop (when valid). <br> 在 `while` 迴圈內或外更新結果（最小/最大）很重要。對於「最小視窗」，在收縮迴圈*內*更新（當有效時）。對於「最長子字串」，在收縮迴圈*後*更新（當有效時）。 |
| **Valid Condition** | Ensure you define exactly what makes a window "valid". Is it `sum >= k` or `sum == k`? <br> 確保你精確定義了什麼使視窗「有效」。是 `sum >= k` 還是 `sum == k`？ |
| **Negative Numbers** | If an array has negative numbers, expanding the window doesn't guarantee the sum increases. Sliding window may fail for "Subarray Sum Equals K" (Use Prefix Sum instead). <br> 若陣列含負數，擴張視窗不保證總和增加。滑動視窗可能無法解決「子陣列總和等於 K」（應改用前綴和）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify**: "Since we are looking for a contiguous subarray satisfying condition X, I'm thinking of using the Sliding Window technique."
    **識別**：「由於我們正在尋找滿足條件 X 的連續子陣列，我考慮使用滑動視窗技巧。」
2.  **Define Invariants**: "I will maintain a window `[left, right]` such that the window always contains..."
    **定義不變性**：「我將維護一個視窗 `[left, right]`，使得該視窗始終包含...」
3.  **Explain Flow**: "I'll expand `right` to find a valid window, then shrink `left` to optimize it."
    **解釋流程**：「我將擴張 `right` 以找到有效視窗，然後收縮 `left` 來優化它。」

### Whiteboard Strategy (白板策略)
-   Use descriptive variable names: `window_start`, `window_end` (or `left`, `right`), `current_sum`, `max_len`.
    使用具描述性的變數名稱：`window_start`、`window_end`（或 `left`、`right`）、`current_sum`、`max_len`。
-   Trace a small example manually before coding to verify logic (especially the shrink condition).
    在寫程式碼前，手動追蹤一個小範例以驗證邏輯（特別是收縮條件）。

### Common Follow-ups (常見追問)
-   **Stream Data**: "What if the input is an infinite stream?" (Answer: Maintain the window state in memory, handle eviction carefully).
    **串流資料**：「如果輸入是無限串流怎麼辦？」（答：在記憶體中維護視窗狀態，小心處理移除邏輯）。
-   **Large Char Set**: "What if we deal with Unicode instead of ASCII?" (Answer: Use a HashMap instead of a fixed-size array).
    **大字元集**：「如果我們處理 Unicode 而非 ASCII 怎麼辦？」（答：使用 HashMap 而非固定大小陣列）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Maximum Average Subarray I
**Prompt**: Find the contiguous subarray of given length `k` that has the maximum average value.
**題目**：找出長度為 `k` 且具有最大平均值的連續子陣列。
-   **Hint**: Fixed window size. Initialize sum of first `k`, then slide: `sum += nums[i] - nums[i-k]`.
    **提示**：固定視窗大小。初始化前 `k` 個的總和，然後滑動：`sum += nums[i] - nums[i-k]`。

### 2. Medium: Max Consecutive Ones III
**Prompt**: Given a binary array `nums` and an integer `k`, return the max number of consecutive `1`s if you can flip at most `k` `0`s.
**題目**：給定二元陣列 `nums` 和整數 `k`，若最多可翻轉 `k` 個 `0`，回傳連續 `1` 的最大數量。
-   **Hint**: Variable window. Valid condition: `count(zeros) <= k`. Expand right; if zeros > k, shrink left.
    **提示**：可變視窗。有效條件：`count(zeros) <= k`。向右擴張；若零的數量 > k，向左收縮。

### 3. Hard: Sliding Window Maximum
**Prompt**: Given an array `nums` and size `k`, return the max value in the window at each position.
**題目**：給定陣列 `nums` 和大小 `k`，回傳每個位置視窗內的最大值。
-   **Hint**: Standard sliding window is $O(N \cdot K)$. To get $O(N)$, use a **Monotonic Deque** (decreasing) to store indices. The front of the deque is always the max.
    **提示**：標準滑動視窗是 $O(N \cdot K)$。要達到 $O(N)$，請使用**單調雙端佇列**（遞減）來儲存索引。佇列前端永遠是最大值。

---

## 8. Quick Checklists (快速檢核表)

### Debugging / Self-Review (自我審查)
-   [ ] **Initialization**: Are `left` and `right` initialized to 0?
    **初始化**：`left` 和 `right` 是否初始化為 0？
-   [ ] **Loop Bounds**: Does `right` go up to `len(nums)`?
    **迴圈邊界**：`right` 是否執行到 `len(nums)`？
-   [ ] **Shrink Logic**: Is the inner loop `while` (correct) or `if` (incorrect for variable size)?
    **收縮邏輯**：內層迴圈是 `while`（正確）還是 `if`（可變大小時錯誤）？
-   [ ] **Result Update**: Are you updating the result when the window is valid?
    **結果更新**：你是否在視窗有效時更新結果？
-   [ ] **Empty Input**: Did you handle `len(s) == 0` or `k == 0`?
    **空輸入**：你是否處理了 `len(s) == 0` 或 `k == 0`？

---

## 9. Memory Anchors (記憶錨點)

### The "Caterpillar" Method (毛毛蟲法)
Visualize the window as a caterpillar moving across a leaf (the array).
將視窗想像成一隻在葉子（陣列）上移動的毛毛蟲。
1.  **Eat (Expand)**: The head (`right`) moves forward, eating leaf parts (adding data).
    **吃（擴張）**：頭部（`right`）向前移動，吃掉葉子部分（加入資料）。
2.  **Digest/Poop (Shrink)**: If the caterpillar gets too full or needs to shorten, the tail (`left`) moves forward, leaving parts behind (removing data).
    **消化/排泄（收縮）**：如果毛毛蟲太飽或需要縮短，尾部（`left`）向前移動，留下部分（移除資料）。
3.  **Goal**: Measure the caterpillar's length at specific moments.
    **目標**：在特定時刻測量毛毛蟲的長度。

![Sliding Window Visualization](https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Sliding_window_protocol_animation.gif/220px-Sliding_window_protocol_animation.gif)
*(Mental Image: A frame moving over a strip of paper)*
*(心像：一個框框在一長條紙帶上移動)*