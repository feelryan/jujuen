Here is the complete interview preparation guide for **Bit Manipulation (Beginner Level)**, tailored for a Senior Software Engineer using TypeScript.

這是一份針對 **位元操作（Bit Manipulation，入門級）** 的完整面試準備指南，專為使用 TypeScript 的資深軟體工程師量身打造。

---

# Bit Manipulation: The Foundation (Beginner)
# 位元操作：基礎篇（入門）

## 1. Learning Goals（學習目標）

*   **Master Fundamental Operators:** Deeply understand logical operators (`&`, `|`, `^`, `~`) and shift operators (`<<`, `>>`, `>>>`) within the context of TypeScript's number system.
    **掌握基礎運算符：** 深入理解 TypeScript 數字系統下的邏輯運算符（`&`, `|`, `^`, `~`）與位移運算符（`<<`, `>>`, `>>>`）。
*   **Internalize Bit Masks:** Learn how to construct masks to set, get, clear, and toggle specific bits.
    **內化位元遮罩（Bit Masks）：** 學習如何建構遮罩來設定、讀取、清除與切換特定的位元。
*   **Understand the "n & (n - 1)" Trick:** Recognize this pattern immediately for removing the least significant bit.
    **理解「n & (n - 1)」技巧：** 能夠立即識別此模式，用於移除最低有效位（Least Significant Bit）。
*   **Navigate JavaScript/TypeScript Specifics:** Handle the conversion between 64-bit floating-point numbers and 32-bit signed integers during bitwise operations.
    **掌握 JavaScript/TypeScript 特性：** 處理位元運算過程中，64 位元浮點數與 32 位元有號整數之間的轉換。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
Bit manipulation involves applying logical operations directly on the binary representations of integers.
位元操作涉及直接對整數的二進位表示形式應用邏輯運算。

### Intuition（直覺）
Think of an integer not as a number, but as a compact array of 32 booleans (0 is false, 1 is true).
不要把整數想成數字，而要把它想成是一個由 32 個布林值組成的緊湊陣列（0 代表 false，1 代表 true）。

### Complexity（複雜度）
*   **Time:** $O(1)$ for standard operations, as they run on a fixed number of bits (32 in TS).
    **時間：** 標準操作為 $O(1)$，因為它們在固定數量的位元上運行（TS 中為 32 位元）。
*   **Space:** $O(1)$ auxiliary space.
    **空間：** $O(1)$ 輔助空間。

### TypeScript Nuance（TypeScript 的細微差別）
In TypeScript (JavaScript), numbers are IEEE 754 doubles. However, bitwise operators truncate them to **32-bit signed integers**.
在 TypeScript (JavaScript) 中，數字是 IEEE 754 雙精度浮點數。然而，位元運算符會將它們截斷為 **32 位元有號整數**。
*   `>>` is Sign-propagating right shift (preserves sign).
    `>>` 是符號傳播右移（保留符號）。
*   `>>>` is Zero-fill right shift (logical shift, treats number as unsigned).
    `>>>` 是補零右移（邏輯位移，將數字視為無號）。

---

## 3. Typical Patterns（典型題型 / 模式）

For beginners, mastery comes from memorizing these "idioms".
對於初學者來說，精通來自於熟記這些「慣用語」。

| Operation (操作) | Formula (公式) | Explanation (解釋) |
| :--- | :--- | :--- |
| **Get Bit** (讀取位元) | `(num >> i) & 1` | Shift the $i$-th bit to position 0 and filter with 1.<br>將第 $i$ 位移至位置 0 並用 1 過濾。 |
| **Set Bit** (設定位元) | `num | (1 << i)` | Use OR to turn the $i$-th bit to 1, leaving others unchanged.<br>使用 OR 將第 $i$ 位變為 1，其餘保持不變。 |
| **Clear Bit** (清除位元) | `num & ~(1 << i)` | AND with a mask where only the $i$-th bit is 0.<br>與一個僅第 $i$ 位為 0 的遮罩進行 AND 運算。 |
| **Toggle Bit** (切換位元) | `num ^ (1 << i)` | XOR with 1 flips the bit; XOR with 0 keeps it.<br>與 1 進行 XOR 會翻轉位元；與 0 進行 XOR 則保持不變。 |
| **Check Power of 2** (檢查 2 的次方) | `(n > 0) && (n & (n - 1)) === 0` | Powers of 2 have exactly one bit set.<br>2 的次方數恰好只有一個位元被設定。 |
| **Remove Last 1** (移除最後一個 1) | `n & (n - 1)` | Flips the least significant set bit to 0.<br>將最低有效位的 1 翻轉為 0。 |

---

## 4. Example Walkthrough（範例講解）

### Problem: Number of 1 Bits (Hamming Weight)
### 問題：位元為 1 的個數（漢明權重）

**Problem Statement:**
Write a function that takes an unsigned integer and returns the number of '1' bits it has (also known as the Hamming weight).
編寫一個函式，接收一個無號整數，並返回其擁有的 '1' 位元的數量（也稱為漢明權重）。

### Approach 1: Loop and Check (Brute Force)
### 思路 1：迴圈檢查（暴力法）

Iterate through all 32 bits, checking the last bit and shifting right.
遍歷所有 32 個位元，檢查最後一位並向右位移。

**Why it's suboptimal:** It always iterates 32 times, regardless of the number's value.
**為何次優：** 無論數字大小如何，它總是迭代 32 次。

### Approach 2: Bit Manipulation Trick (Optimal)
### 思路 2：位元操作技巧（最佳解）

Use `n & (n - 1)`. This operation removes the lowest set bit. We count how many times we can do this until `n` becomes 0.
使用 `n & (n - 1)`。此操作會移除最低位的 1。我們計算能執行此操作多少次，直到 `n` 變為 0。

**Complexity:**
*   Time: $O(k)$, where $k$ is the number of 1s (worst case 32, but usually faster).
    時間：$O(k)$，其中 $k$ 是 1 的數量（最壞情況 32，但通常更快）。
*   Space: $O(1)$.
    空間：$O(1)$。

### TypeScript Solution（TypeScript 參考解）

```typescript
/**
 * Calculates the Hamming Weight (number of 1 bits).
 * 計算漢明權重（位元為 1 的數量）。
 * 
 * @param n - The input integer (treated as unsigned 32-bit)
 * @returns The count of set bits
 */
function hammingWeight(n: number): number {
    let count = 0;

    // Loop until n becomes 0
    // 迴圈直到 n 變為 0
    while (n !== 0) {
        // Core Logic: n & (n - 1) flips the least significant 1-bit to 0.
        // 核心邏輯：n & (n - 1) 將最低有效位的 1 翻轉為 0。
        // Example: 
        // n     = 1100 (12)
        // n - 1 = 1011 (11)
        // &     = 1000 (8) -> One bit removed.
        n = n & (n - 1);
        
        count++;
    }

    return count;
}

// ---------------------------------------------------------
// Wrong Approach Demonstration (Common Mistake in JS/TS)
// 錯誤示範（JS/TS 常見錯誤）
// ---------------------------------------------------------
function hammingWeightWrong(n: number): number {
    let count = 0;
    while (n !== 0) {
        if ((n & 1) === 1) count++;
        
        // MISTAKE: Using '>>' (sign-propagating) instead of '>>>' (zero-fill).
        // If n is negative (e.g., starts with 1), '>>' fills with 1s.
        // This causes an infinite loop for negative numbers.
        // 錯誤：使用 '>>'（符號傳播）而非 '>>>'（補零）。
        // 如果 n 是負數（例如以 1 開頭），'>>' 會填補 1。
        // 這會導致負數進入無窮迴圈。
        n = n >> 1; 
    }
    return count;
}
```

---

## 5. Common Pitfalls & Confusing Concepts（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| `>>` (Arithmetic Shift) | `>>>` (Logical Shift) | `>>` preserves the sign bit (fills with 1 for negative numbers). `>>>` always fills with 0. **Crucial in TS.**<br>`>>` 保留符號位（負數填 1）。`>>>` 總是填 0。**在 TS 中至關重要。** |
| `^` (XOR) | `|` (OR) | XOR returns 1 only if bits are *different*. OR returns 1 if *any* bit is 1.<br>XOR 僅在位元*不同*時返回 1。OR 只要*任一*位元為 1 即返回 1。 |
| Operator Precedence | Parentheses | Bitwise operators have lower precedence than `==` or `+`. Always wrap bitwise ops in `()`.<br>位元運算符的優先級低於 `==` 或 `+`。務必用 `()` 包裹位元運算。 |
| `~n` (Bitwise NOT) | `-n` (Negation) | `~n` flips all bits. `-n` is Two's Complement (`~n + 1`).<br>`~n` 翻轉所有位元。`-n` 是二補數（`~n + 1`）。 |

---

## 6. Interview Strategy（面試實戰建議）

### Narration Framework（口條框架）
1.  **Acknowledge Representation:** "Since we are dealing with bits, I'll treat the number as a 32-bit integer."
    **確認表示法：** 「既然我們在處理位元，我會將該數字視為 32 位元整數。」
2.  **State the Idiom:** "To check the $i$-th bit efficiently, I'll use a mask with the AND operator."
    **陳述慣用語：** 「為了高效檢查第 $i$ 位，我會使用遮罩搭配 AND 運算符。」
3.  **Explain Choice:** "I'm using `n & (n-1)` instead of a loop because it skips all the zeros, optimizing for sparse numbers."
    **解釋選擇：** 「我使用 `n & (n-1)` 而非迴圈，因為它會跳過所有 0，針對稀疏數字進行了優化。」

### Whiteboard Strategy（白板策略）
*   **Draw the Bits:** Don't calculate in decimal. Write `1011` on the board.
    **畫出位元：** 不要用十進位計算。在白板上寫下 `1011`。
*   **Trace the Operation:** Show the `Mask`, show the `Original`, and show the `Result` line by line.
    **追蹤操作：** 逐行展示「遮罩」、「原始值」和「結果」。

### Common Follow-ups（常見追問）
*   "How does this work with negative numbers?" (Answer: TS uses Two's Complement).
    「這對負數如何運作？」（答：TS 使用二補數）。
*   "What if the integer is larger than 32 bits?" (Answer: In JS/TS, we might need `BigInt`, but standard bitwise ops only work on 32-bit safely without coercion).
    「如果整數大於 32 位元怎麼辦？」（答：在 JS/TS 中可能需要 `BigInt`，但標準位元運算符僅能安全作用於 32 位元）。

---

## 7. Practice Problems（練習題）

### Easy: Single Number
**Problem:** Given an array where every element appears twice except for one. Find that single one.
**問題：** 給定一個陣列，除了某個元素外，其餘每個元素都出現兩次。找出那個單獨的元素。
*   **Hint:** $A \oplus A = 0$ and $A \oplus 0 = A$.
    **提示：** $A \oplus A = 0$ 且 $A \oplus 0 = A$。
*   **Key Logic:** XOR all numbers together.
    **關鍵邏輯：** 將所有數字進行 XOR 運算。

### Medium: Reverse Bits
**Problem:** Reverse bits of a given 32-bit unsigned integer.
**問題：** 翻轉給定 32 位元無號整數的位元。
*   **Hint:** Iterate 32 times. Extract the last bit of input, shift result left, add extracted bit.
    **提示：** 迭代 32 次。提取輸入的最後一位，將結果左移，加上提取的位元。
*   **Key Logic:** `res = (res << 1) | (n & 1); n >>>= 1;`
    **關鍵邏輯：** `res = (res << 1) | (n & 1); n >>>= 1;`

### Hard (for Beginner): Missing Number
**Problem:** Given an array containing $n$ distinct numbers taken from $0, 1, \dots, n$, find the one that is missing.
**問題：** 給定一個包含 $n$ 個相異數字的陣列，數字取自 $0, 1, \dots, n$，找出缺失的那個數字。
*   **Hint:** XOR the array elements with all numbers from $0$ to $n$.
    **提示：** 將陣列元素與 $0$ 到 $n$ 的所有數字進行 XOR 運算。
*   **Key Logic:** Index matches value. The mismatch remains after XOR.
    **關鍵邏輯：** 索引應匹配數值。XOR 後留下的就是不匹配的數。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Parentheses:** Did I wrap my `(a & b)` checks in parentheses? (e.g., `if ((n & 1) === 0)`)
    **括號：** 我是否用括號包裹了 `(a & b)` 檢查？
*   [ ] **Shift Type:** Did I use `>>>` for logical right shifts to avoid infinite loops with negative numbers?
    **位移類型：** 我是否使用了 `>>>` 進行邏輯右移，以避免負數導致無窮迴圈？
*   [ ] **Base Case:** Did I handle `0` or `-1` correctly?
    **基本情況：** 我是否正確處理了 `0` 或 `-1`？
*   [ ] **Type Safety:** Remember that bitwise ops return `number`, not `boolean`. `if (n & 1)` works in JS/TS (truthy), but `if ((n & 1) == 1)` is more explicit.
    **型別安全：** 記住位元運算返回 `number` 而非 `boolean`。`if (n & 1)` 在 JS/TS 可行（真值判斷），但 `if ((n & 1) == 1)` 更明確。

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **XOR (`^`) is a "Toggle Switch" or "Difference Detector":**
    **XOR (`^`) 是「切換開關」或「差異偵測器」：**
    *   Think of it as: "If inputs are different, output is TRUE."
    *   想成：「如果輸入不同，輸出為真。」
*   **AND (`&`) is a "Gatekeeper" (Mask):**
    **AND (`&`) 是「守門員」（遮罩）：**
    *   It forces bits to 0 unless the mask allows them to be 1.
    *   除非遮罩允許為 1，否則它強制作位元為 0。
*   **Left Shift (`<<`) is "Doubling":**
    **左移 (`<<`) 是「加倍」：**
    *   $x << 1$ is $x \times 2$.
    *   $x << 1$ 等於 $x \times 2$。
*   **Right Shift (`>>`) is "Halving":**
    **右移 (`>>`) 是「減半」：**
    *   $x >> 1$ is $\lfloor x / 2 \rfloor$.
    *   $x >> 1$ 等於 $\lfloor x / 2 \rfloor$。