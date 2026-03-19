Here is the comprehensive interview preparation guide for **Bit Manipulation (Intermediate)**, tailored for a Senior Software Engineer, presented in a bilingual format with Java code.

這是一份針對 **位元操作（中階）** 的完整面試準備指南，專為資深軟體工程師量身打造，採用中英雙語對照並附帶 Java 程式碼。

---

# Bit Manipulation Interview Guide (Intermediate)
# 位元操作面試指南（中階）

## 1. Learning Goals（學習目標）

*   **Master Core Bitwise Operators & Precedence:** Understand the nuances of XOR, AND, OR, NOT, and Shift operators, especially in Java.
    **掌握核心位元運算子與優先級：** 理解 XOR、AND、OR、NOT 以及位移運算子的細微差別，特別是在 Java 中的表現。
*   **Optimize Space Complexity:** Learn how to use bits to replace HashSets or Boolean Arrays to achieve $O(1)$ space complexity.
    **優化空間複雜度：** 學習如何使用位元來取代 HashSet 或布林陣列，以達到 $O(1)$ 的空間複雜度。
*   **Recognize XOR Patterns:** Develop intuition for problems solvable by XOR properties (cancellation, commutativity).
    **識別 XOR 模式：** 培養對可通過 XOR 屬性（抵消、交換律）解決的問題的直覺。
*   **Handle Low-Level Bit Hacks:** Master techniques like `x & -x` (extract lowest set bit) and `x & (x - 1)` (clear lowest set bit).
    **掌握底層位元技巧：** 精通如 `x & -x`（提取最低位 1）與 `x & (x - 1)`（清除最低位 1）等技巧。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Bit manipulation involves applying logical operations on a sequence of bits at the hardware level.
位元操作涉及在硬體層級對位元序列應用邏輯運算。

Intuitively, think of an Integer not as a number, but as an array of 32 boolean switches (0 or 1).
直觀地說，不要把整數視為數字，而應將其視為由 32 個布林開關（0 或 1）組成的陣列。

### Complexity（複雜度）
*   **Time:** $O(1)$ for basic operations (`&`, `|`, `^`, `>>`). Iterating over bits is $O(W)$ where $W$ is the number of bits (usually 32 or 64, treated as constant).
    **時間：** 基本運算（`&`, `|`, `^`, `>>`）為 $O(1)$。遍歷位元為 $O(W)$，其中 $W$ 是位元數（通常為 32 或 64，視為常數）。
*   **Space:** $O(1)$ auxiliary space.
    **空間：** $O(1)$ 輔助空間。

### When to Use (and Not)（適用與不適用場景）
*   **Use when:** You need to track states, find unique elements, perform set operations efficiently, or optimize arithmetic (multiplication/division by powers of 2).
    **適用時機：** 當你需要追蹤狀態、尋找唯一元素、高效執行集合運算，或優化算術運算（乘以/除以 2 的冪次）時。
*   **Don't use when:** Readability is paramount over micro-optimization, or when dealing with floating-point logic directly.
    **不適用時機：** 當可讀性遠重於微優化時，或直接處理浮點數邏輯時。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. The XOR Trick (Cancellation)
**Property:** `x ^ x = 0` and `x ^ 0 = x`.
**屬性：** `x ^ x = 0` 且 `x ^ 0 = x`。
**Application:** Finding the unique element in an array where every other element appears twice.
**應用：** 在其他元素都出現兩次的陣列中尋找唯一元素。

### B. Masking (Set / Get / Unset / Toggle)
Using a "mask" to manipulate specific bits.
使用「遮罩」來操作特定的位元。
*   **Check $i$-th bit:** `(x >> i) & 1`
*   **Set $i$-th bit:** `x | (1 << i)`
*   **Unset $i$-th bit:** `x & ~(1 << i)`
*   **Toggle $i$-th bit:** `x ^ (1 << i)`

### C. Brian Kernighan’s Algorithm (Counting Bits)
**Logic:** `x & (x - 1)` drops the lowest set bit (turns the rightmost 1 into 0).
**邏輯：** `x & (x - 1)` 會移除最低位的 1（將最右邊的 1 變為 0）。
**Use Case:** Counting the number of set bits (Hamming Weight) efficiently.
**應用：** 高效計算設置位元的數量（漢明權重）。

### D. Low Bit Extraction
**Logic:** `x & -x` isolates the rightmost 1 bit.
**邏輯：** `x & -x` 隔離出最右邊的 1 位元。
**Why:** In Two's Complement, `-x` is `~x + 1`.
**原因：** 在二補數表示法中，`-x` 等於 `~x + 1`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Single Number II
**Problem:** Given an integer array `nums` where every element appears **three times** except for one, which appears exactly once. Find the single element.
**問題：** 給定一個整數陣列 `nums`，其中除了某個元素僅出現一次外，其餘每個元素都出現 **三次**。請找出那個單獨的元素。

### Approach 1: Brute Force (HashMap)
Count frequency of each number.
計算每個數字的頻率。
*   Time: $O(N)$
*   Space: $O(N)$ (Not optimal / 不夠優化)

### Approach 2: Optimal Bit Manipulation (Bit Counting)
**Idea:** If we sum the bits at each position ($0$ to $31$) for all numbers, the sum for any position where the single number has a `0` will be divisible by 3. If the single number has a `1`, the sum modulo 3 will be 1.
**思路：** 如果我們將所有數字在每個位置（$0$ 到 $31$）的位元加總，對於單獨數字該位為 `0` 的位置，其總和將能被 3 整除。如果單獨數字該位為 `1`，則總和除以 3 的餘數將為 1。

### Java Solution (Reference)

```java
class Solution {
    /**
     * Finds the element that appears once while others appear three times.
     * 找出出現一次的元素，其餘元素均出現三次。
     *
     * Time Complexity: O(N) - We iterate through the array 32 times (constant).
     * 時間複雜度：O(N) - 我們遍歷陣列 32 次（常數）。
     * Space Complexity: O(1) - No extra data structures used.
     * 空間複雜度：O(1) - 未使用額外資料結構。
     */
    public int singleNumber(int[] nums) {
        int ans = 0;

        // Iterate through all 32 bits of an integer
        // 遍歷整數的所有 32 個位元
        for (int i = 0; i < 32; i++) {
            int sum = 0;
            
            // Create a mask to check the i-th bit
            // 建立遮罩以檢查第 i 個位元
            int mask = 1 << i;

            for (int num : nums) {
                // If the i-th bit is set, increment sum
                // 如果第 i 個位元被設置，則增加 sum
                if ((num & mask) != 0) {
                    sum++;
                }
            }

            // If sum % 3 is not 0, it means the unique number has a 1 at this bit
            // 如果 sum % 3 不為 0，表示唯一數字在此位元上有一個 1
            if (sum % 3 != 0) {
                // Set the i-th bit in our answer
                // 將答案中的第 i 個位元設置為 1
                ans |= mask;
            }
        }
        return ans;
    }
}
```

### Common Mistake (錯誤示範)
Trying to use `XOR` directly like in "Single Number I".
試圖直接像「Single Number I」那樣使用 `XOR`。
*   **Why wrong:** `x ^ x ^ x = x`. XOR cancels out even occurrences, not odd occurrences greater than 1.
*   **為何錯：** `x ^ x ^ x = x`。XOR 抵消偶數次出現，而非大於 1 的奇數次出現。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation (解釋) | Pitfall (陷阱) |
| :--- | :--- | :--- |
| **Operator Precedence** | `==` has higher precedence than `&`. <br> `==` 的優先級高於 `&`。 | `if (x & 1 == 0)` actually evaluates as `x & (1 == 0)`. <br> **Always use parentheses:** `if ((x & 1) == 0)`. |
| **Signed vs Unsigned Shift** | `>>` preserves sign (arithmetic); `>>>` fills with 0 (logical). <br> `>>` 保留符號（算術）；`>>>` 補 0（邏輯）。 | Using `>>` on negative numbers when you meant to treat bits as raw data leads to infinite loops of 1s. <br> 在想將位元視為原始數據時對負數使用 `>>` 會導致 1 的無限循環。 |
| **Integer Overflow** | `1 << 31` creates `Integer.MIN_VALUE` (negative). <br> `1 << 31` 會產生 `Integer.MIN_VALUE`（負數）。 | Shifting `1` more than 31 times in Java wraps around (`1 << 32 == 1`). Ensure you know the bit width. <br> 在 Java 中位移 `1` 超過 31 次會循環（`1 << 32 == 1`）。確保你知道位元寬度。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Identify the Representation:** "Since we are dealing with states/sets/integers, I can represent this using bits to optimize space."
    **確認表示法：** 「由於我們在處理狀態/集合/整數，我可以使用位元來表示以優化空間。」
2.  **Propose the Mask:** "I will use a mask to isolate the bits we care about."
    **提出遮罩：** 「我將使用遮罩來隔離我們關心的位元。」
3.  **Address Signedness:** "Since Java integers are signed, I will use `>>>` for logical shifts to handle negative inputs correctly."
    **處理符號：** 「由於 Java 整數是有號的，我將使用 `>>>` 進行邏輯位移以正確處理負數輸入。」

### Whiteboard Strategy（白板策略）
*   **Draw 4-bit examples:** Don't write 32 bits. Use `n = 5 (0101)` and `n = 6 (0110)` to demonstrate logic.
    **畫出 4 位元範例：** 不要寫出 32 個位元。使用 `n = 5 (0101)` 和 `n = 6 (0110)` 來演示邏輯。
*   **Write Precedence Explicitly:** Always wrap bitwise ops in `()`.
    **明確寫出優先級：** 永遠將位元運算包在 `()` 中。

### Common Follow-up（常見追問）
*   "What if the input is negative?" (Check `>>>` usage).
    「如果輸入是負數怎麼辦？」（檢查 `>>>` 的使用）。
*   "Can this scale to large bitsets?" (Discuss `BitSet` class or array of longs).
    「這能擴展到大型位元集嗎？」（討論 `BitSet` 類別或 long 陣列）。

---

## 7. Practice Problems（練習題）

### Easy: Number of 1 Bits (Hamming Weight)
*   **Problem:** Write a function that takes an unsigned integer and returns the number of '1' bits it has.
    **問題：** 寫一個函式，接收一個無號整數並回傳其擁有的 '1' 位元數量。
*   **Hint:** Use `n & (n - 1)` loop.
    **提示：** 使用 `n & (n - 1)` 迴圈。

### Medium: Sum of Two Integers
*   **Problem:** Calculate the sum of two integers `a` and `b` without using `+` or `-` operators.
    **問題：** 計算兩個整數 `a` 和 `b` 的和，不使用 `+` 或 `-` 運算子。
*   **Hint:** XOR (`^`) is sum without carry. AND (`&`) shifted left (`<< 1`) is the carry. Loop until carry is 0.
    **提示：** XOR (`^`) 是不進位加法。AND (`&`) 左移 (`<< 1`) 是進位。迴圈直到進位為 0。

### Hard: Maximum Product of Word Lengths
*   **Problem:** Given a string array `words`, find the maximum value of `length(word[i]) * length(word[j])` where the two words do not share common letters.
    **問題：** 給定字串陣列 `words`，找出 `length(word[i]) * length(word[j])` 的最大值，其中這兩個字串不包含共同字母。
*   **Hint:** Convert each word into a 26-bit integer mask (State Compression). Use `(mask[i] & mask[j]) == 0` to check for collision.
    **提示：** 將每個字串轉換為 26 位元的整數遮罩（狀態壓縮）。使用 `(mask[i] & mask[j]) == 0` 來檢查是否衝突。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Parentheses Check:** Did I wrap `(a & b)` before comparing?
    **括號檢查：** 我是否在比較前將 `(a & b)` 包起來了？
*   [ ] **Shift Type Check:** Did I use `>>>` for unsigned/logical shifting?
    **位移類型檢查：** 我是否使用了 `>>>` 進行無號/邏輯位移？
*   [ ] **Loop Termination:** Will my loop terminate if `n` is negative (e.g., `while(n != 0)` vs `while(n > 0)`)?
    **迴圈終止：** 如果 `n` 是負數，我的迴圈會終止嗎（例如 `while(n != 0)` vs `while(n > 0)`）？
*   [ ] **Boundary:** Did I handle `Integer.MIN_VALUE` or `0`?
    **邊界：** 我是否處理了 `Integer.MIN_VALUE` 或 `0`？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **XOR is a "Difference Detector":** It returns 1 only if bits are different. It's also a "Toggle Switch".
    **XOR 是「差異偵測器」：** 只有當位元不同時才回傳 1。它也是個「切換開關」。
*   **AND is a "Filter/Mask":** It forces bits to 0 unless they are allowed by the mask.
    **AND 是「過濾器/遮罩」：** 除非遮罩允許，否則它強制位元變為 0。
*   **`n & (n-1)` is "Shaving":** Imagine shaving off the rightmost hair (1) from the number.
    **`n & (n-1)` 是「刮鬍子」：** 想像把數字最右邊的那根毛（1）刮掉。
*   **`n & -n` is "Sniper":** It targets and isolates the rightmost soldier (1).
    **`n & -n` 是「狙擊手」：** 它鎖定並隔離最右邊的士兵（1）。