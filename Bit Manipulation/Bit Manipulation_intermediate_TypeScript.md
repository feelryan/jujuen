Here is the complete interview preparation guide for **Bit Manipulation**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **位元操作（Bit Manipulation）** 面試實戰完整教材。

---

# Bit Manipulation: Intermediate Guide for Senior Engineers
# 位元操作：資深工程師的中階指南

## 1. Learning Objectives (學習目標)

By the end of this module, you should be able to:
完成本單元後，你應具備以下能力：

1.  **Master Bitwise Operators & Precedence**: Confidently use `&`, `|`, `^`, `~`, `<<`, `>>`, and `>>>` (TypeScript specific) without syntax errors.
    **掌握位元運算子與優先級**：自信地使用 `&`, `|`, `^`, `~`, `<<`, `>>` 以及 `>>>`（TypeScript 特有），並避免語法錯誤。
2.  **Utilize Bitmasks**: Implement set operations (union, intersection, check existence) using integers to optimize space complexity.
    **運用位元遮罩（Bitmasks）**：使用整數來實作集合操作（聯集、交集、存在檢查），以優化空間複雜度。
3.  **Apply XOR Properties**: Solve "finding unique elements" problems using the self-inverse property of XOR ($A \oplus A = 0$).
    **應用 XOR 特性**：利用 XOR 的自反特性（$A \oplus A = 0$）解決「尋找唯一元素」類型的問題。
4.  **Manipulate LSB (Least Significant Bit)**: Use tricks like `n & (n-1)` and `n & (-n)` for efficiency.
    **操作最低有效位（LSB）**：使用 `n & (n-1)` 和 `n & (-n)` 等技巧來提升效率。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Bit manipulation involves applying logical operations on individual bits of integers.
位元操作涉及對整數的個別位元進行邏輯運算。

**Intuition**: Think of an integer as a fixed-size array of booleans (32 or 64 flags), processed in parallel by the CPU.
**直覺**：將整數視為一個固定大小的布林值陣列（32 或 64 個標記），並由 CPU 進行平行處理。

### Complexity (複雜度)
*   **Time**: $O(1)$ for basic operations. $O(k)$ where $k$ is the number of bits (usually 32/64, effectively constant) for iteration.
    **時間**：基本操作為 $O(1)$。若需迭代位元，則為 $O(k)$，其中 $k$ 為位元數（通常為 32/64，實際上視為常數）。
*   **Space**: $O(1)$ auxiliary space.
    **空間**：$O(1)$ 輔助空間。

### When to Use / Not Use (適用與不適用場景)

| Scenario (場景) | Suitability (適用性) | Reason (理由) |
| :--- | :--- | :--- |
| **Compact State (緊湊狀態)** | ✅ Excellent | Efficiently store permissions, visited states, or board games (e.g., Chess/Sudoku). <br> 高效存儲權限、訪問狀態或棋盤遊戲（如西洋棋/數獨）。 |
| **Math Optimization (數學優化)** | ✅ Good | Fast multiplication/division by powers of 2, checking parity. <br> 快速進行 2 的冪次乘除、奇偶校驗。 |
| **Set Operations (集合操作)** | ✅ Excellent | Intersection/Union on small sets (< 64 elements) is ultra-fast. <br> 小集合（< 64 個元素）的交集/聯集運算極快。 |
| **Floating Point Math (浮點數運算)** | ❌ Avoid | Bitwise ops in JS/TS cast numbers to 32-bit integers, losing precision. <br> JS/TS 中的位元運算會將數字轉為 32 位整數，導致精度丟失。 |
| **High-level Business Logic (高階業務邏輯)** | ⚠️ Caution | Reduces readability; use only if performance is critical. <br> 降低可讀性；僅在效能至關重要時使用。 |

---

## 3. Typical Patterns (典型題型 / 模式)

### A. The Mask Pattern (遮罩模式)
Used to check, set, or clear specific bits.
用於檢查、設定或清除特定位元。
*   **Check $i$-th bit**: `(n & (1 << i)) !== 0`
*   **Set $i$-th bit**: `n | (1 << i)`
*   **Clear $i$-th bit**: `n & ~(1 << i)`
*   **Toggle $i$-th bit**: `n ^ (1 << i)`

### B. The XOR Trick (XOR 技巧)
Key properties: $A \oplus 0 = A$, $A \oplus A = 0$, Commutative ($A \oplus B = B \oplus A$).
關鍵特性：$A \oplus 0 = A$, $A \oplus A = 0$, 交換律（$A \oplus B = B \oplus A$）。
*   **Pattern**: Used to find the "odd one out" in an array where elements repeat.
    **模式**：用於在元素重複的陣列中找出「落單」的那個。

### C. Brian Kernighan’s Algorithm (清除最低位 1)
*   **Formula**: `n & (n - 1)`
*   **Effect**: Turns off the rightmost set bit (1) of `n`.
    **效果**：將 `n` 最右邊的 1 變為 0。
*   **Usage**: Counting set bits (Hamming Weight) efficiently.
    **用途**：高效計算設為 1 的位元數量（漢明權重）。

### D. Lowbit Extraction (提取最低位 1)
*   **Formula**: `n & (-n)`
*   **Effect**: Isolates the rightmost 1 bit (e.g., `10110` -> `00010`).
    **效果**：分離出最右邊的 1（例如 `10110` -> `00010`）。
*   **Usage**: Binary Indexed Trees (Fenwick Tree), differentiating two unique numbers.
    **用途**：二元索引樹（Fenwick Tree），區分兩個唯一數字。

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number III (LeetCode 260)
**Problem Statement**: Given an integer array `nums`, in which exactly two elements appear only once and all the other elements appear exactly twice. Find the two elements that appear only once.
**問題重述**：給定一個整數陣列 `nums`，其中恰好有兩個元素只出現一次，其餘所有元素均出現兩次。找出這兩個只出現一次的元素。

### Approach (思路)

1.  **Brute Force (Hash Map)**:
    *   Count frequency of each number. Return those with count 1.
    *   計算每個數字的頻率。回傳計數為 1 的數字。
    *   **Complexity**: Time $O(N)$, Space $O(N)$. (Interview expectation: Optimize Space).
    *   **複雜度**：時間 $O(N)$，空間 $O(N)$。（面試期望：優化空間）。

2.  **Optimization (XOR)**:
    *   If we XOR all numbers, duplicates cancel out ($A \oplus A = 0$).
    *   若我們將所有數字進行 XOR，重複的會互相抵銷（$A \oplus A = 0$）。
    *   The result will be $X \oplus Y$ (where $X$ and $Y$ are the two unique numbers).
    *   結果將是 $X \oplus Y$（其中 $X$ 和 $Y$ 是那兩個唯一的數字）。
    *   Since $X \neq Y$, their XOR sum must have at least one bit set to `1`. This bit represents a position where $X$ and $Y$ differ.
    *   因為 $X \neq Y$，它們的 XOR 和必定至少有一個位元是 `1`。這個位元代表 $X$ 和 $Y$ 在該位置上不同。

3.  **The Partition Strategy (最佳解)**:
    *   Find the rightmost set bit of the XOR sum using `diff & (-diff)`.
    *   利用 `diff & (-diff)` 找出 XOR 和中最右邊為 1 的位元。
    *   Use this bit as a mask to split the array into two groups: those with the bit set, and those without.
    *   使用這個位元作為遮罩，將陣列分為兩組：該位元為 1 的，與該位元為 0 的。
    *   $X$ will be in one group, $Y$ in the other. XORing each group separately reveals $X$ and $Y$.
    *   $X$ 會在其中一組，$Y$ 在另一組。分別對每組進行 XOR 運算即可解出 $X$ 和 $Y$。

### TypeScript Solution (參考解)

```typescript
/**
 * Finds the two numbers that appear exactly once in an array where all others appear twice.
 * 找出陣列中兩個只出現一次的數字，其餘數字皆出現兩次。
 * 
 * Time Complexity: O(N) - Two passes over the array.
 * Space Complexity: O(1) - Only constant extra space used.
 */
function singleNumber(nums: number[]): number[] {
    // Step 1: XOR all numbers to get (x ^ y)
    // 步驟 1：對所有數字進行 XOR，得到 (x ^ y)
    let xorSum = 0;
    for (const num of nums) {
        xorSum ^= num;
    }

    // Step 2: Find the rightmost set bit (LSB) to use as a differentiator.
    // 步驟 2：找出最右邊的 1 (LSB) 作為區分依據。
    // Note: In Two's Complement, -x is (~x + 1). So x & -x isolates the LSB.
    // 註：在二補數系統中，-x 等於 (~x + 1)。因此 x & -x 可分離出 LSB。
    const diffBit = xorSum & (-xorSum);

    let x = 0;
    let y = 0;

    // Step 3: Partition numbers into two groups and XOR separately.
    // 步驟 3：將數字分為兩組並分別進行 XOR。
    for (const num of nums) {
        if ((num & diffBit) !== 0) {
            // Group 1: The bit is set
            // 第一組：該位元為 1
            x ^= num;
        } else {
            // Group 2: The bit is not set
            // 第二組：該位元為 0
            y ^= num;
        }
    }

    return [x, y];
}

// Example Usage
const input = [1, 2, 1, 3, 2, 5];
console.log(singleNumber(input)); // Output: [3, 5] or [5, 3]
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

### 1. Operator Precedence (運算子優先級)
*   **Trap**: `a & b == 0` is interpreted as `a & (b == 0)` because `==` has higher precedence than `&`.
    **陷阱**：`a & b == 0` 會被解釋為 `a & (b == 0)`，因為 `==` 的優先級高於 `&`。
*   **Fix**: Always wrap bitwise operations in parentheses: `(a & b) == 0`.
    **修正**：永遠將位元運算用括號包起來：`(a & b) == 0`。

### 2. JavaScript/TypeScript 32-bit Limitation (JS/TS 的 32 位元限制)
*   **Fact**: JS numbers are 64-bit doubles, but bitwise operators truncate them to 32-bit signed integers.
    **事實**：JS 的數字是 64 位元浮點數，但位元運算子會將其截斷為 32 位元有號整數。
*   **Risk**: If you shift `1 << 31`, it becomes a negative number (`-2147483648`).
    **風險**：如果你執行 `1 << 31`，它會變成負數（`-2147483648`）。
*   **Fix**: Use `>>>` (Zero-fill right shift) for unsigned interpretation if needed, or BigInt for large integers.
    **修正**：如有需要，使用 `>>>`（補零右移）進行無號解釋，或針對大整數使用 BigInt。

### 3. `>>` vs `>>>` (Sign-propagating vs Zero-fill)
*   `>>`: Preserves the sign bit (arithmetic shift). `-2 >> 1` is `-1`.
    `>>`：保留符號位（算術位移）。`-2 >> 1` 是 `-1`。
*   `>>>`: Fills with zeros (logical shift). `-2 >>> 1` is `2147483647`.
    `>>>`：補零（邏輯位移）。`-2 >>> 1` 是 `2147483647`。

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Acknowledge the Data Type**: "Since we are dealing with integers/booleans and need $O(1)$ space, bit manipulation is a strong candidate."
    **確認資料型態**：「既然我們處理的是整數/布林值且需要 $O(1)$ 空間，位元操作是一個強力的候選方案。」
2.  **Explain the Mask**: "I'll use a mask to isolate the bits we care about."
    **解釋遮罩**：「我將使用遮罩來分離我們關注的位元。」
3.  **Justify Complexity**: "This avoids the overhead of a Hash Map / Set."
    **證成複雜度**：「這避免了 Hash Map / Set 的額外開銷。」

### Whiteboard Strategy (白板策略)
*   **Draw Bits**: Don't just write numbers (e.g., `5`). Write `101` or `...00101`.
    **畫出位元**：不要只寫數字（如 `5`）。寫出 `101` 或 `...00101`。
*   **Trace with Small Examples**: Use 4-bit numbers to demonstrate logic manually.
    **用小範例追蹤**：使用 4 位元數字手動演示邏輯。

### Common Follow-up (常見追問)
*   "What if the numbers are larger than $2^{32}$?" -> **Ans**: Use `BigInt` in TS/JS or Python (which handles arbitrary length integers).
    「如果數字大於 $2^{32}$ 怎麼辦？」-> **答**：在 TS/JS 中使用 `BigInt`，或使用 Python（自動處理任意長度整數）。

---

## 7. Practice Problems (練習題)

### Easy: Number of 1 Bits (Hamming Weight)
*   **Hint**: Use `n & (n-1)` in a loop to clear the least significant bit until `n` becomes 0.
    **提示**：在迴圈中使用 `n & (n-1)` 清除最低有效位，直到 `n` 變為 0。
*   **Focus**: Basic loop and bit clearing.
    **重點**：基本迴圈與位元清除。

### Intermediate: Subsets (Power Set)
*   **Problem**: Generate all subsets of a set `[1, 2, 3]`.
    **問題**：生成集合 `[1, 2, 3]` 的所有子集。
*   **Hint**: Iterate from `0` to `2^N - 1`. The bit pattern of the index determines which elements to include (e.g., `5` is `101` -> include elements at index 0 and 2).
    **提示**：從 `0` 迭代到 `2^N - 1`。索引的位元模式決定包含哪些元素（例如 `5` 是 `101` -> 包含索引 0 和 2 的元素）。

### Advanced: Maximum Product of Word Lengths
*   **Problem**: Given a string array, find max product of lengths of two words that share no letters.
    **問題**：給定字串陣列，找出兩個不共用任何字母的單字長度乘積的最大值。
*   **Hint**: Precompute a bitmask for each word (26 bits for 'a'-'z'). If `mask[i] & mask[j] == 0`, they share no letters.
    **提示**：為每個單字預先計算位元遮罩（26 個位元對應 'a'-'z'）。若 `mask[i] & mask[j] == 0`，則它們無共用字母。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] Did I wrap bitwise operations in parentheses? `(x & 1) == 0`
    有無將位元運算用括號包起來？
*   [ ] Am I handling negative numbers correctly? (Are they possible in input?)
    有無正確處理負數？（輸入中是否可能出現？）
*   [ ] Did I consider the 32-bit limit in TypeScript?
    有無考慮 TypeScript 的 32 位元限制？
*   [ ] Is the loop termination condition correct (e.g., `while (n !== 0)` instead of `while (n > 0)` for signed integers)?
    迴圈終止條件是否正確（例如針對有號整數應使用 `while (n !== 0)` 而非 `while (n > 0)`）？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **XOR is a "Difference Detector"**:
    *   $1 \oplus 1 = 0$ (Same is zero)
    *   $1 \oplus 0 = 1$ (Different is one)
    *   **XOR 是「差異偵測器」**：相同為 0，不同為 1。

*   **AND is a "Filter/Mask"**:
    *   Like placing a stencil over a drawing. Only parts under the holes (1s) show through.
    *   **AND 是「濾網/遮罩」**：就像在畫作上放一個模版。只有孔洞（1）下的部分會顯示出來。

*   **`n & (n-1)` is "Turning off the lights"**:
    *   Imagine a row of lights. This operation walks from right to left and turns off the *first* switch that is currently ON.
    *   **`n & (n-1)` 是「關燈」**：想像一排燈。這個操作會從右向左走，並關掉目前是「開」著的*第一個*開關。