Here is the comprehensive guide on **Bit Manipulation (Intermediate)**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **位元操作（中階）** 完整指南。

---

# Bit Manipulation Masterclass for Senior Engineers
# 資深工程師的位元操作大師班

## 1. Learning Goals（學習目標）

*   **Master XOR Properties:** Understand how XOR works for cancellation and state toggling without extra memory.
    **掌握 XOR 特性：** 理解 XOR 如何在不使用額外記憶體的情況下進行抵銷與狀態切換。
*   **Proficiency in Bitmasks:** Learn to represent sets, permissions, or boolean states using a single integer.
    **熟練位元遮罩（Bitmasks）：** 學習使用單個整數來表示集合、權限或布林狀態。
*   **Low-Level Optimization:** Recognize when bitwise operations can replace arithmetic operations for performance (e.g., division/multiplication by powers of 2).
    **底層優化：** 識別何時可以使用位元運算取代算術運算以提升效能（例如：2 的次方的乘除法）。
*   **Handle Python Specifics:** Understand how Python’s arbitrary-precision integers differ from fixed-width integers (32/64-bit) in C++/Java.
    **處理 Python 特性：** 理解 Python 的任意精度整數與 C++/Java 中固定寬度整數（32/64 位元）的差異。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
Bit manipulation involves applying logical operations (AND, OR, XOR, NOT) and shift operations directly on the binary representation of data.
位元操作涉及直接對資料的二進位表示形式應用邏輯運算（AND、OR、XOR、NOT）和位移運算。

### Intuition（直覺）
Think of an integer not as a number, but as an array of 32 (or 64) boolean switches.
不要將整數視為數字，而應將其視為由 32（或 64）個布林開關組成的陣列。
This allows for $O(1)$ parallel processing of these switches.
這允許我們以 $O(1)$ 的時間複雜度並行處理這些開關。

### Complexity（複雜度）
*   **Time:** $O(1)$ for basic operations. For iterating bits, it's $O(k)$ where $k$ is the number of bits (usually constant 32/64).
    **時間：** 基本運算為 $O(1)$。若需遍歷位元，則為 $O(k)$，其中 $k$ 為位元數（通常為常數 32/64）。
*   **Space:** $O(1)$ usually, as it avoids auxiliary data structures like Arrays or Sets.
    **空間：** 通常為 $O(1)$，因為它避免了像陣列或集合這樣的輔助資料結構。

### When to Use / Not to Use（適用與不適用場景）
*   **Use (適用):** Compact state representation (DP states), finding unique elements, math optimization, network protocols.
    **適用：** 緊湊的狀態表示（DP 狀態）、尋找唯一元素、數學優化、網路協定。
*   **Not Use (不適用):** Complex business logic where readability is paramount, floating-point arithmetic.
    **不適用：** 可讀性至關重要的複雜商業邏輯、浮點數運算。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. The XOR Trick ($x \oplus x = 0$)
*   **Concept:** XORing a number with itself results in 0; XORing with 0 results in the number.
    **觀念：** 一個數字與自身進行 XOR 運算結果為 0；與 0 進行 XOR 運算結果為該數字。
*   **Application:** Finding the single number in a list of duplicates.
    **應用：** 在重複列表中尋找落單的數字。

### B. The Bitmask (Set Representation)
*   **Concept:** The $i$-th bit represents the presence of the $i$-th item in a set.
    **觀念：** 第 $i$ 個位元代表集合中第 $i$ 個項目的存在與否。
*   **Application:** Generating all subsets (Power Set), State Compression DP.
    **應用：** 生成所有子集（冪集）、狀態壓縮 DP。

### C. Brian Kernighan’s Algorithm
*   **Concept:** `x & (x - 1)` removes the rightmost set bit (1) from `x`.
    **觀念：** `x & (x - 1)` 會移除 `x` 中最右邊設為 1 的位元。
*   **Application:** Counting the number of set bits (Hamming Weight), checking if a number is a power of 2.
    **應用：** 計算設為 1 的位元數量（漢明權重）、檢查數字是否為 2 的次方。

### D. Extracting Lowest Set Bit (LSB)
*   **Concept:** `x & -x` isolates the rightmost 1-bit.
    **觀念：** `x & -x` 會分離出最右邊的 1 位元。
*   **Application:** Fenwick Trees (Binary Indexed Trees).
    **應用：** 樹狀陣列（Fenwick Trees）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Counting Bits (LeetCode 338)
**Problem Statement:** Given an integer `n`, return an array `ans` of length `n + 1` such that for each `i` ($0 \le i \le n$), `ans[i]` is the number of `1`'s in the binary representation of `i`.
**問題重述：** 給定一個整數 `n`，回傳一個長度為 `n + 1` 的陣列 `ans`，使得對於每個 `i` ($0 \le i \le n$)，`ans[i]` 是 `i` 的二進位表示中 `1` 的數量。

### Approach 1: Brute Force (Popcount)
**Idea:** Loop from 0 to n, and for each number, count bits using a loop.
**思路：** 從 0 迴圈到 n，並對每個數字使用迴圈計算位元。
**Complexity:** $O(n \cdot \log n)$ (since integers have $\log n$ bits).
**複雜度：** $O(n \cdot \log n)$（因為整數有 $\log n$ 個位元）。

### Approach 2: DP + Last Set Bit (Optimal)
**Idea:** We can reuse the result of a smaller number.
**思路：** 我們可以重用較小數字的計算結果。
Relationship: The number of 1s in `x` is equal to the number of 1s in `x` with its last bit removed (`x >> 1`), plus 1 if the last bit was a 1.
關係：`x` 中 1 的數量等於「移除了最後一位的 `x`」（`x >> 1`）中 1 的數量，加上最後一位是否為 1。
Formula: `dp[i] = dp[i >> 1] + (i & 1)`

**Alternative (Brian Kernighan's DP):**
`dp[i] = dp[i & (i - 1)] + 1`
(The bits of `i` are the same as `i` with the lowest bit removed, plus exactly one bit).
（`i` 的位元數等於「移除最低位元後的 `i`」的位元數，再加上剛好一個位元）。

### Python Reference Solution（Python 參考解）

```python
from typing import List

class Solution:
    def countBits(self, n: int) -> List[int]:
        # Initialize the DP array with 0s.
        # 初始化 DP 陣列為 0。
        dp = [0] * (n + 1)
        
        # Iterate from 1 to n to fill the array.
        # 從 1 迭代到 n 來填充陣列。
        for i in range(1, n + 1):
            # Approach: x // 2 is x >> 1. 
            # If x is even, bits(x) = bits(x >> 1).
            # If x is odd, bits(x) = bits(x >> 1) + 1.
            # 方法：x // 2 等同於 x >> 1。
            # 如果 x 是偶數，bits(x) = bits(x >> 1)。
            # 如果 x 是奇數，bits(x) = bits(x >> 1) + 1。
            
            # dp[i] = dp[i >> 1] + (i & 1)
            
            # Alternative using Brian Kernighan's logic (slightly faster convergence logic):
            # 另一種使用 Brian Kernighan 邏輯的方法（收斂邏輯略快）：
            # i & (i - 1) removes the lowest set bit.
            # i & (i - 1) 移除最低位的 1。
            dp[i] = dp[i & (i - 1)] + 1
            
        return dp

# Time Complexity: O(n) - One pass through the numbers.
# 時間複雜度：O(n) - 對數字進行一次遍歷。
# Space Complexity: O(1) - Ignoring the return array space.
# 空間複雜度：O(1) - 忽略回傳陣列的空間。
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall (觀念與陷阱) |
| :--- | :--- |
| **Operator Precedence**<br>運算子優先級 | `==` has higher precedence than `&`.<br>`if x & 1 == 0` is interpreted as `if x & (1 == 0)`.<br>**Fix:** Always use parentheses: `if (x & 1) == 0`.<br>`==` 的優先級高於 `&`。<br>`if x & 1 == 0` 會被解釋為 `if x & (1 == 0)`。<br>**修正：** 務必使用括號：`if (x & 1) == 0`。 |
| **Python's Infinite Integers**<br>Python 的無限整數 | Python integers do not overflow. `~0` is `-1`, not `0xFFFFFFFF`.<br>To simulate 32-bit unsigned behavior, apply mask: `(x & 0xFFFFFFFF)`.<br>Python 整數不會溢位。`~0` 是 `-1`，而不是 `0xFFFFFFFF`。<br>若要模擬 32 位元無號整數行為，請套用遮罩：`(x & 0xFFFFFFFF)`。 |
| **Right Shift (`>>`)**<br>右移運算 | In Python/Java, `>>` is arithmetic shift (preserves sign). `>>>` (Java/JS) is logical.<br>Python has no `>>>`. For logical shift on negative numbers, mask first.<br>在 Python/Java 中，`>>` 是算術位移（保留符號）。`>>>` (Java/JS) 是邏輯位移。<br>Python 沒有 `>>>`。若要對負數進行邏輯位移，需先套用遮罩。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarify Constraints (釐清限制)
"Are we dealing with 32-bit signed integers? Can the input be negative?"
「我們處理的是 32 位元有號整數嗎？輸入可以是負數嗎？」
*Why:* This determines if you need to handle overflow or Python's infinite precision quirks.
*原因：* 這決定了你是否需要處理溢位或 Python 無限精度的特性。

### 2. Start with Logical/Arithmetic (從邏輯/算術開始)
Don't jump to bits immediately unless the problem screams "Bit Manipulation" (e.g., "without using + operator").
除非題目明顯暗示「位元操作」（例如：「不使用 + 運算子」），否則不要立刻跳到位元運算。
State the brute force, then say: "We can optimize space/time by looking at the binary representation."
先說明暴力解，然後說：「我們可以透過觀察二進位表示來優化空間/時間。」

### 3. Whiteboard Strategy (白板策略)
Write out the binary examples.
寫出二進位範例。
Example: `5 (101)` and `4 (100)`.
Visually showing the bits helps the interviewer follow your logic regarding AND/XOR operations.
視覺化地展示位元有助於面試官理解你關於 AND/XOR 運算的邏輯。

---

## 7. Practice Problems（練習題）

### Easy: Single Number
**Problem:** Given a non-empty array of integers, every element appears twice except for one. Find that single one.
**問題：** 給定一個非空的整數陣列，除了某個元素只出現一次以外，其餘每個元素均出現兩次。找出那個只出現一次的元素。
**Hint:** $A \oplus A = 0$.
**提示：** $A \oplus A = 0$。

### Medium: Subsets (Power Set)
**Problem:** Given an integer array `nums` of unique elements, return all possible subsets.
**問題：** 給定一個包含唯一元素的整數陣列 `nums`，回傳所有可能的子集。
**Hint:** Iterate from $0$ to $2^n - 1$. If the $j$-th bit of $i$ is set, include `nums[j]`.
**提示：** 從 $0$ 迭代到 $2^n - 1$。如果 $i$ 的第 $j$ 個位元是 1，則包含 `nums[j]`。

### Hard (Intermediate+): Maximum Product of Word Lengths
**Problem:** Given a string array `words`, find the maximum value of `length(word[i]) * length(word[j])` where the two words do not share common letters.
**問題：** 給定一個字串陣列 `words`，找出 `length(word[i]) * length(word[j])` 的最大值，其中這兩個單字不包含共同的字母。
**Hint:** Precompute a bitmask for each word (26 bits for 'a'-'z'). If `mask[i] & mask[j] == 0`, they are disjoint.
**提示：** 為每個單字預先計算位元遮罩（26 個位元對應 'a'-'z'）。如果 `mask[i] & mask[j] == 0`，則它們不相交。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Parentheses:** Did I wrap my bitwise ops? `(a & b) == c` instead of `a & b == c`.
    **括號：** 我是否將位元運算包起來了？應為 `(a & b) == c` 而非 `a & b == c`。
*   [ ] **Negative Numbers:** Did I handle Python's negative integer representation (infinite 1s padding)? Used `& 0xFFFFFFFF`?
    **負數：** 我是否處理了 Python 的負整數表示（無限的 1 填充）？是否使用了 `& 0xFFFFFFFF`？
*   [ ] **Base Case:** Did I handle 0 or empty inputs?
    **基本情況：** 我是否處理了 0 或空輸入？
*   [ ] **Complexity:** Is this actually faster than the arithmetic version? (Usually yes, but check logic).
    **複雜度：** 這真的比算術版本快嗎？（通常是，但請檢查邏輯）。

---

## 9. Memory Anchors（記憶錨點）

*   **XOR ($\oplus$):** "The Difference Detector" or "Toggle Switch".
    **XOR ($\oplus$)：** 「差異偵測器」或「切換開關」。
    *   *Image:* Two identical waves cancelling each other out to flatline (0).
    *   *圖像：* 兩個相同的波互相抵銷成直線 (0)。
*   **`x & (x-1)`:** "Turn off the rightmost light".
    **`x & (x-1)`：** 「關掉最右邊的那盞燈」。
    *   *Analogy:* Snipping the lowest hanging fruit.
    *   *類比：* 剪掉位置最低的果實。
*   **Mask (`1 << i`):** "The Stencil".
    **Mask (`1 << i`)：** 「模板/遮罩」。
    *   *Analogy:* Spray painting over a stencil where only one hole is open.
    *   *類比：* 在只有一個孔洞開啟的模板上噴漆。