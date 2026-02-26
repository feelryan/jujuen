Here is the comprehensive guide for **Bit Manipulation** at an **Advanced** level, tailored for a Senior Software Engineer.

這是一份針對 **位元操作（Bit Manipulation）** 的 **進階（Advanced）** 完整教材，專為資深軟體工程師量身打造。

---

# Advanced Bit Manipulation Interview Guide
# 進階位元操作面試指南

## 1. Learning Goals（學習目標）

*   **Master State Compression:** Learn to use bits to represent sets or states to optimize Space Complexity from $O(N)$ to $O(1)$ or to facilitate Dynamic Programming.
    **掌握狀態壓縮：** 學習使用位元來表示集合或狀態，將空間複雜度從 $O(N)$ 優化至 $O(1)$，或用於輔助動態規劃。
*   **Deep Dive into XOR Properties:** Go beyond basic swapping; understand how XOR behaves as "addition without carry" and its application in grouping and unique element identification.
    **深入 XOR 特性：** 超越基本的交換變數；理解 XOR 作為「不進位加法」的行為，及其在分組與唯一元素識別中的應用。
*   **Optimize Arithmetic Operations:** Implement arithmetic operations (addition, subtraction, division) using only bitwise operators to demonstrate low-level understanding.
    **優化算術運算：** 僅使用位元運算符實作算術運算（加、減、除），以展示對底層原理的理解。
*   **Combine with Data Structures:** Integrate Bit Manipulation with Tries or Segment Trees for advanced range queries.
    **結合資料結構：** 將位元操作與字典樹（Trie）或線段樹（Segment Tree）結合，以處理進階的區間查詢。

---

## 2. Core Concepts at a Glance（核心觀念速覽）

### Definition & Intuition（定義與直覺）

Bit manipulation exploits the binary representation of data to perform operations at the machine level.
位元操作利用資料的二進位表示法，在機器層級執行運算。

For senior engineers, the intuition is not just about "flipping bits," but viewing an integer as a **compact array of booleans** (Bitmask).
對於資深工程師而言，直覺不僅在於「翻轉位元」，而是將整數視為一個**緊湊的布林陣列**（位元遮罩）。

### Key Advanced Operations（關鍵進階操作）

1.  **Remove the last set bit (Brian Kernighan’s Algorithm):** `x & (x - 1)`
    **移除最後一個為 1 的位元：** `x & (x - 1)`
    *   *Usage:* Counting set bits, power of 2 check.
    *   *用途：* 計算 1 的個數、檢查是否為 2 的次方。

2.  **Extract the last set bit (Lowbit):** `x & -x`
    **提取最後一個為 1 的位元：** `x & -x`
    *   *Usage:* Binary Indexed Tree (Fenwick Tree), differentiating two numbers based on bits.
    *   *用途：* 二元索引樹（Fenwick Tree）、基於位元區分兩個數字。

3.  **Enumerate Submasks (Subset of a mask):**
    **枚舉子遮罩（遮罩的子集）：**
    ```python
    sub = mask
    while sub > 0:
        # process sub
        sub = (sub - 1) & mask
    ```
    *   *Complexity:* $O(3^N)$ for iterating all submasks of all masks of length N.
    *   *複雜度：* 遍歷長度為 N 的所有遮罩的所有子遮罩時為 $O(3^N)$。

### Complexity（複雜度）

*   **Time:** Generally $O(1)$ for fixed-width integers (32/64-bit). For loops iterating over bits, it's $O(W)$ where $W$ is word size.
    **時間：** 對於固定寬度整數（32/64位元）通常為 $O(1)$。對於遍歷位元的迴圈，則為 $O(W)$，其中 $W$ 為字組大小。
*   **Space:** $O(1)$ auxiliary space.
    **空間：** $O(1)$ 輔助空間。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. The "XOR Cancellation" Pattern（XOR 抵銷模式）
Using the property `A ^ A = 0` and `A ^ 0 = A` to find unique elements or duplicates in linear time.
利用 `A ^ A = 0` 和 `A ^ 0 = A` 的特性，在線性時間內找出唯一元素或重複元素。

### B. Bitmask Dynamic Programming（位元遮罩動態規劃）
Used when $N$ is small ($N \le 20$). The state is represented by an integer mask where the $i$-th bit being set means item $i$ is visited/used.
當 $N$ 很小（$N \le 20$）時使用。狀態由一個整數遮罩表示，其中第 $i$ 個位元被設置意味著項目 $i$ 已被訪問或使用。
*   *Example:* Traveling Salesman Problem, Assigning tasks to workers.
*   *範例：* 旅行推銷員問題、分配任務給工人。

### C. Bitwise Trie (Prefix Tree)（位元字典樹）
Storing binary representations of numbers in a Trie to solve "Maximum XOR" or "Prefix Match" problems.
將數字的二進位表示存儲在 Trie 中，以解決「最大 XOR」或「前綴匹配」問題。

---

## 4. Example Walkthrough（範例講解）

### Problem: Maximum XOR of Two Numbers in an Array
### 問題：陣列中兩個數字的最大 XOR 值

**Problem Statement:**
Given an integer array `nums`, return the maximum result of `nums[i] XOR nums[j]`.
給定一個整數陣列 `nums`，回傳 `nums[i] XOR nums[j]` 的最大結果。

**Constraints:** $O(N)$ time complexity preferred.
**限制：** 偏好 $O(N)$ 的時間複雜度。

---

### Phase 1: Brute Force (Naive)
### 第一階段：暴力解（樸素）

Iterate through all pairs and calculate XOR.
遍歷所有數對並計算 XOR。

```python
def findMaximumXOR_brute(nums: list[int]) -> int:
    max_xor = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            max_xor = max(max_xor, nums[i] ^ nums[j])
    return max_xor
```
*   **Analysis:** Time $O(N^2)$. Too slow for $N=10^5$.
*   **分析：** 時間 $O(N^2)$。對於 $N=10^5$ 來說太慢。

---

### Phase 2: Optimization with Bitwise Prefixes (Greedy Strategy)
### 第二階段：利用位元前綴優化（貪婪策略）

**Intuition:**
To maximize XOR, we want the Most Significant Bit (MSB) to be 1 if possible. We iterate from the 31st bit down to 0.
**直覺：**
為了最大化 XOR，我們希望最高有效位（MSB）盡可能為 1。我們從第 31 位元向下遍歷到 0。

For each bit position, we check: "Can we form a current prefix such that the current bit is 1?"
對於每個位元位置，我們檢查：「我們能否形成一個當前前綴，使得當前位元為 1？」

**Key Logic:**
If `A ^ B = Target`, then `A ^ Target = B`.
We guess a `Target` (current max with the next bit set to 1) and check if it exists using a Set.
**關鍵邏輯：**
如果 `A ^ B = Target`，那麼 `A ^ Target = B`。
我們猜測一個 `Target`（當前最大值並將下一位設為 1），並使用 Set 檢查其是否存在。

### Python Solution (Advanced)
### Python 參考解（進階）

```python
class Solution:
    def findMaximumXOR(self, nums: list[int]) -> int:
        max_xor = 0
        mask = 0
        
        # Iterate from the 31st bit down to 0 (assuming 32-bit integers)
        # 從第 31 位元向下遍歷到 0（假設為 32 位元整數）
        for i in range(31, -1, -1):
            # The mask grows like: 100...000, 110...000, 111...000
            # 遮罩增長形式如：100...000, 110...000, 111...000
            mask = mask | (1 << i)
            
            # Store prefixes of all numbers up to the current bit
            # 儲存所有數字截至當前位元的前綴
            prefixes = set()
            for num in nums:
                prefixes.add(num & mask)
            
            # We hope the i-th bit of the result can be 1
            # "candidate" is the potential new max_xor if this bit is set
            # 我們希望結果的第 i 位元可以是 1
            # "candidate" 是如果此位元被設置後的潛在 max_xor
            candidate = max_xor | (1 << i)
            
            # Check if there exist two prefixes p1, p2 such that p1 ^ p2 = candidate
            # Equivalent to checking: p1 ^ candidate = p2
            # 檢查是否存在兩個前綴 p1, p2 使得 p1 ^ p2 = candidate
            # 等同於檢查：p1 ^ candidate = p2
            found = False
            for prefix in prefixes:
                if (prefix ^ candidate) in prefixes:
                    found = True
                    break
            
            # If possible, update max_xor
            # 如果可能，更新 max_xor
            if found:
                max_xor = candidate
                
        return max_xor

# Complexity Analysis:
# Time: O(N * 32) -> O(N). We iterate 32 times, and each time iterate through N numbers.
# Space: O(N) to store the set of prefixes.
# 複雜度分析：
# 時間：O(N * 32) -> O(N)。我們迭代 32 次，每次遍歷 N 個數字。
# 空間：O(N) 用於儲存前綴集合。
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Description (描述) | Pitfall / Warning (陷阱 / 警告) |
| :--- | :--- | :--- |
| **Operator Precedence** | `==` has higher precedence than `&` `|` `^`. <br> `==` 的優先級高於 `&` `|` `^`。 | `if x & 1 == 0` is parsed as `x & (1 == 0)`. **Always use parentheses:** `if (x & 1) == 0`. <br> 務必使用括號。 |
| **Negative Shifting** | Shifting negative numbers in Python. <br> 在 Python 中移位負數。 | Python integers have infinite precision. `~0` is `-1`, not `11...11`. Be careful with infinite leading 1s. Mask with `0xFFFFFFFF` to simulate 32-bit. <br> Python 整數無限精度。需用 `0xFFFFFFFF` 遮罩來模擬 32 位元行為。 |
| **`>>` vs `>>>`** | Arithmetic vs Logical Right Shift. <br> 算術右移 vs 邏輯右移。 | Python only has `>>` (Arithmetic). To simulate logical shift (zero-fill) on negative numbers, mask first: `(n & 0xFFFFFFFF) >> k`. <br> Python 只有 `>>`。若要模擬邏輯右移，需先做遮罩。 |
| **XOR Self-Inverse** | `A ^ B = C` implies `A ^ C = B`. | Forgetting this property leads to complex algebraic solutions instead of simple bitwise checks. <br> 忘記此特性會導致使用複雜代數解法而非簡單位元檢查。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Identify the Representation:** "Since the constraints are small ($N \le 20$) or we are dealing with sets, I'm thinking about **Bitmasking** to represent the state efficiently."
    **識別表示法：** 「由於限制很小（$N \le 20$）或者我們正在處理集合，我在考慮使用 **位元遮罩** 來高效表示狀態。」
2.  **Propose Optimization:** "Instead of using a Hash Map or Array to track visited elements, a single integer can track up to 32/64 elements, reducing space overhead and constant factors."
    **提出優化：** 「與其使用雜湊表或陣列來追蹤已訪問元素，單個整數可以追蹤多達 32/64 個元素，從而減少空間開銷和常數因子。」
3.  **Address Language Specifics:** "Since I'm using Python, I will handle the infinite precision of integers by masking with `0xFFFFFFFF` if we need strictly 32-bit unsigned behavior."
    **處理語言特性：** 「因為我使用 Python，如果我們需要嚴格的 32 位元無號行為，我會通過與 `0xFFFFFFFF` 進行遮罩來處理整數的無限精度。」

### Whiteboard Strategy（白板策略）
*   Define helper functions early: `get_bit(n, i)`, `set_bit(n, i)`. This cleans up your main logic.
    儘早定義輔助函式：`get_bit(n, i)`、`set_bit(n, i)`。這能讓你的主邏輯更清晰。
*   Use binary literals for clarity: `mask = 0b101` is clearer than `mask = 5` in bit contexts.
    為求清晰使用二進位字面量：在位元情境下，`mask = 0b101` 比 `mask = 5` 更清晰。

---

## 7. Practice Problems（練習題）

### Level 1: Easy (Warm-up)
**Problem:** **Number of 1 Bits** (Hamming Weight)
**問題：** **1 的位元個數**
*   **Hint:** Use `n & (n-1)` to drop the lowest set bit repeatedly.
*   **提示：** 使用 `n & (n-1)` 重複移除最低位的 1。

### Level 2: Intermediate (Core Pattern)
**Problem:** **Single Number III** (LeetCode 260)
**問題：** **只出現一次的數字 III**
*   **Desc:** Two numbers appear once, others twice. Find the two numbers.
*   **描述：** 兩個數字出現一次，其餘出現兩次。找出這兩個數字。
*   **Hint:** XOR all numbers to get `A ^ B`. Find the rightmost set bit of `A ^ B` (using `diff & -diff`). This bit differs between A and B. Use it to split the array into two groups and XOR separately.
*   **提示：** 將所有數字 XOR 得到 `A ^ B`。找出 `A ^ B` 最右邊的 1（使用 `diff & -diff`）。此位元在 A 和 B 中不同。利用它將陣列分為兩組並分別 XOR。

### Level 3: Advanced (Bitmask DP)
**Problem:** **Smallest Sufficient Team** (LeetCode 1125)
**問題：** **最小的必要團隊**
*   **Desc:** Given required skills and people with specific skills, find the smallest team to cover all skills.
*   **描述：** 給定所需技能和具備特定技能的人員，找出能涵蓋所有技能的最小團隊。
*   **Hint:** $N_{skills} \le 16$. Use DP where `dp[mask]` = smallest team for skill set `mask`. Iterate through people and update states: `new_mask = old_mask | person_skills`.
*   **提示：** $N_{skills} \le 16$。使用 DP，其中 `dp[mask]` = 技能集合 `mask` 所需的最小團隊。遍歷人員並更新狀態：`new_mask = old_mask | person_skills`。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Parentheses:** Did I wrap my bitwise operations in `()` before comparing? e.g., `(a & b) == 0`.
    **括號：** 我是否在比較前將位元運算用 `()` 包起來了？
*   [ ] **Constraint Check:** Is $N \le 64$? If yes, Bitmask is viable. If $N > 64$, use `BitSet` or Array.
    **限制檢查：** $N \le 64$ 嗎？若是，位元遮罩可行。若 $N > 64$，使用 `BitSet` 或陣列。
*   [ ] **Overflow/Sign:** In Python, did I handle negative numbers correctly for shifts?
    **溢位/符號：** 在 Python 中，我是否正確處理了負數的移位？
*   [ ] **Base Case:** Did I handle the `0` case correctly (e.g., counting bits of 0)?
    **基本情況：** 我是否正確處理了 `0` 的情況（例如計算 0 的位元數）？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **XOR is a "Difference Detector":**
    Think of XOR as a machine that outputs `1` only when inputs are *different*.
    **XOR 是「差異偵測器」：**
    將 XOR 想像成一台只有當輸入*不同*時才輸出 `1` 的機器。

*   **AND is "Intersection":**
    `A & B` keeps only the bits present in *both*. Like the intersection of two sets.
    **AND 是「交集」：**
    `A & B` 僅保留*兩者*皆有的位元。就像兩個集合的交集。

*   **`x & (x-1)` is "Shaving":**
    Imagine shaving off the lowest hair (bit) on your arm. It removes exactly one 1 from the bottom.
    **`x & (x-1)` 是「刮鬍子」：**
    想像刮掉手臂上最低的一根毛髮（位元）。它精確地從底部移除一個 1。