Here is the comprehensive interview preparation guide for **Bit Manipulation**, tailored for a Senior Software Engineer, adjusted to a **Beginner** depth level for this specific topic, using **C++**.

這是一份針對 **位元操作（Bit Manipulation）** 的完整面試準備教材，專為資深軟體工程師設計，針對此特定主題調整為 **初學者（Beginner）** 深度，並使用 **C++** 撰寫。

---

# Bit Manipulation Interview Guide (Beginner Level)
# 位元操作面試指南（初學者等級）

## 1. Learning Objectives (學習目標)

*   **Master Fundamental Operators:** Understand the behavior of AND, OR, XOR, NOT, and Bitwise Shifts in C++.
    **掌握基礎運算子：** 理解 C++ 中 AND、OR、XOR、NOT 以及位元位移（Shifts）的行為。
*   **Internalize the "Masking" Concept:** Learn how to set, clear, toggle, and check specific bits using masks.
    **內化「遮罩」概念：** 學習如何使用遮罩（Masks）來設定、清除、切換與檢查特定的位元。
*   **Leverage XOR Properties:** Recognize scenarios where XOR ($\oplus$) can eliminate duplicates or swap values without temporary storage.
    **利用 XOR 特性：** 辨識 XOR ($\oplus$) 可以消除重複值或在不使用暫存空間下交換數值的場景。
*   **Understand Low-Level Efficiency:** Appreciate why bitwise operations are faster and how they map to CPU instructions.
    **理解底層效率：** 體會為何位元運算較快，以及它們如何對應到 CPU 指令。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Bit manipulation involves applying logical operations on individual bits of integers to perform calculations or manage states efficiently.
位元操作涉及對整數的個別位元應用邏輯運算，以高效地執行計算或管理狀態。

### Intuition (直覺)
Think of an integer as an array of boolean switches (0 = OFF, 1 = ON).
將整數視為一組布林開關的陣列（0 = 關，1 = 開）。
Bitwise operations allow you to flip, check, or group these switches in parallel.
位元運算允許你平行地翻轉、檢查或分組這些開關。

### Complexity (複雜度)
*   **Time:** Generally $O(1)$ for fixed-width integers (like 32-bit or 64-bit), as they execute in a single CPU cycle.
    **時間：** 對於固定寬度的整數（如 32 位元或 64 位元）通常為 $O(1)$，因為它們在單個 CPU 週期內執行。
*   **Space:** $O(1)$, as operations are performed in-place on registers.
    **空間：** $O(1)$，因為運算是在暫存器上原地（in-place）執行的。

### Operators Cheat Sheet (運算子速查表)

| Operator | Symbol (C++) | Logic | Example (4-bit) |
| :--- | :---: | :--- | :--- |
| **AND** | `&` | Both must be 1 | `1010 & 1100 = 1000` |
| **OR** | `\|` | Either is 1 | `1010 \| 1100 = 1110` |
| **XOR** | `^` | Different is 1 | `1010 ^ 1100 = 0110` |
| **NOT** | `~` | Invert all bits | `~1010 = ...110101` (depends on type width) |
| **Left Shift** | `<<` | Multiply by $2^k$ | `0011 << 1 = 0110` (3 -> 6) |
| **Right Shift** | `>>` | Divide by $2^k$ | `0110 >> 1 = 0011` (6 -> 3) |

### When to Use (適用場景)
*   Compact state representation (e.g., permission flags).
    緊湊的狀態表示（例如：權限標誌）。
*   Mathematical optimizations (multiplying/dividing by powers of 2).
    數學優化（乘以或除以 2 的冪次）。
*   Problems involving "unique elements" or "missing numbers".
    涉及「唯一元素」或「缺失數字」的問題。

### When NOT to Use (不適用場景)
*   Complex business logic where readability is paramount over micro-optimization.
    可讀性重於微優化的複雜商業邏輯。
*   Floating point arithmetic (unless manipulating the raw IEEE 754 bits).
    浮點數運算（除非是操作原始的 IEEE 754 位元）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Basic Masking (基礎遮罩)
Using a "mask" to manipulate the $k$-th bit.
使用「遮罩」來操作第 $k$ 個位元。

*   **Check bit:** `(num & (1 << k)) != 0`
*   **Set bit:** `num | (1 << k)`
*   **Clear bit:** `num & ~(1 << k)`
*   **Toggle bit:** `num ^ (1 << k)`

### Pattern 2: The XOR Trick (XOR 技巧)
XOR is its own inverse: $x \oplus x = 0$ and $x \oplus 0 = x$.
XOR 是其自身的反運算：$x \oplus x = 0$ 且 $x \oplus 0 = x$。
This is useful for finding unique elements in an array where others repeat twice.
這對於在其他元素重複兩次的陣列中尋找唯一元素非常有用。

### Pattern 3: Brian Kernighan’s Algorithm (清除最低位的 1)
Expression: `n & (n - 1)`
運算式：`n & (n - 1)`
This operation removes the rightmost set bit (1) from `n`.
此操作會移除 `n` 中最右邊被設定為 1 的位元。
*   Example: `1010 (10) & 1001 (9) = 1000 (8)`.
*   Used for counting set bits efficiently.
    用於高效計算被設定的位元數量。

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number (LeetCode 136)
**Problem Statement:** Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.
**問題重述：** 給定一個非空的整數陣列 `nums`，除了某個元素只出現一次以外，其餘每個元素均出現兩次。找出那個只出現一次的元素。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Use a Hash Map to count frequencies.
        使用雜湊表（Hash Map）來計算頻率。
    *   Time: $O(N)$, Space: $O(N)$.
    *   *Critique:* Uses extra memory.
        *評論：* 使用了額外的記憶體。

2.  **Sorting (排序法):**
    *   Sort the array and check neighbors.
        將陣列排序並檢查相鄰元素。
    *   Time: $O(N \log N)$, Space: $O(1)$ (depending on sort).
    *   *Critique:* Too slow compared to linear time.
        *評論：* 與線性時間相比太慢。

3.  **Optimal: Bitwise XOR (最佳解：位元 XOR):**
    *   Concept: $a \oplus a = 0$. If we XOR all numbers together, pairs cancel out.
        觀念：$a \oplus a = 0$。如果我們將所有數字進行 XOR 運算，成對的數字會互相抵銷。
    *   Only the single number remains.
        只剩下那個單獨的數字。
    *   Time: $O(N)$, Space: $O(1)$.

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <iostream>

class Solution {
public:
    int singleNumber(std::vector<int>& nums) {
        // Initialize result with 0 because 0 ^ x = x
        // 初始化結果為 0，因為 0 ^ x = x
        int result = 0;

        // Iterate through every number in the vector
        // 遍歷向量中的每一個數字
        for (int num : nums) {
            // XOR the current number with the running result
            // 將當前數字與目前的結果進行 XOR 運算
            // Logic: A ^ B ^ A = B (Order doesn't matter)
            // 邏輯：A ^ B ^ A = B（順序不影響結果）
            result ^= num;
        }

        return result;
    }
};
```

### Edge Conditions & Complexity (邊界條件與複雜度)
*   **Time Complexity:** $O(N)$ — We iterate through the array once.
    **時間複雜度：** $O(N)$ — 我們遍歷陣列一次。
*   **Space Complexity:** $O(1)$ — No extra data structures used.
    **空間複雜度：** $O(1)$ — 未使用額外的資料結構。
*   **Edge Cases:** Array with only 1 element (loop runs once, returns element).
    **邊界情況：** 只有 1 個元素的陣列（迴圈執行一次，回傳該元素）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Bitwise AND (`&`)** | **Logical AND (`&&`)** | `&` processes bits (10 & 01 = 00); `&&` processes booleans (true && false = false). <br> `&` 處理位元；`&&` 處理布林值。 |
| **Operator Precedence** | **Expected Logic** | In C++, `==` has higher precedence than `&`. <br> `x & 1 == 0` is parsed as `x & (1 == 0)`. **ALWAYS use parentheses:** `(x & 1) == 0`. <br> 在 C++ 中，`==` 優先權高於 `&`。務必使用括號。 |
| **Signed Shift (`>>`)** | **Unsigned Shift (`>>`)** | Right shifting a negative number is implementation-defined (usually arithmetic shift, fills with 1). Use `unsigned` types for logical shifts. <br> 右移負數是實作定義的（通常是算術位移，補 1）。若要邏輯位移，請使用 `unsigned` 型別。 |
| **`n`** | **`n - 1`** | `n - 1` flips the rightmost `1` to `0` and all subsequent `0`s to `1`s. <br> `n - 1` 會將最右邊的 `1` 翻轉為 `0`，並將其後的所有 `0` 翻轉為 `1`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the Binary Nature:** "Since this problem deals with states/sets/duplicates, I'm thinking about Bit Manipulation to optimize space."
    **識別二進位本質：** 「既然這個問題涉及狀態/集合/重複項，我考慮使用位元操作來優化空間。」
2.  **Specify the Operator:** Don't just say "combine them". Say "I will use XOR to cancel out duplicates."
    **明確指出運算子：** 不要只說「結合它們」。要說「我將使用 XOR 來抵銷重複項。」
3.  **Trace with Small Bits:** "Let's trace this with 4-bit integers to verify."
    **用少量位元追蹤：** 「讓我們用 4 位元整數來追蹤驗證一下。」

### Whiteboard Strategy (白板策略)
*   Write numbers in binary vertically to visualize the columns.
    將數字以二進位垂直書寫，以便視覺化各個位元行。
*   Example:
    ```text
    A: 0 1 0 1
    B: 0 0 1 1
    &  -------
       0 0 0 1
    ```

### Common Follow-ups (常見追問)
*   **Q:** "What if the input contains negative numbers?"
    **問：** 「如果輸入包含負數怎麼辦？」
    *   **A:** In C++ (Two's Complement), bitwise logic generally holds, but be careful with right shifts (sign extension).
    *   **答：** 在 C++（二補數）中，位元邏輯通常成立，但要小心右移運算（符號擴充）。

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單)
**Problem:** **Number of 1 Bits (Hamming Weight)**
**問題：** 計算 1 位元的數量（漢明權重）
*   **Hint:** Use `n & (n - 1)` in a loop to clear the least significant bit until `n` becomes 0.
    **提示：** 在迴圈中使用 `n & (n - 1)` 清除最低有效位元，直到 `n` 變為 0。
*   **Key Concept:** Brian Kernighan’s Algorithm.
    **關鍵觀念：** Brian Kernighan 演算法。

### Level: Medium (中等 - for Beginner Bit Manip)
**Problem:** **Reverse Bits**
**問題：** 反轉位元
*   **Hint:** Iterate 32 times. Extract the $i$-th bit from input and place it in the $(31-i)$-th position of the result.
    **提示：** 迭代 32 次。從輸入提取第 $i$ 個位元，並將其放置在結果的第 $(31-i)$ 個位置。
*   **Key Concept:** Masking and Shifting (`result = (result << 1) | (n & 1)`).
    **關鍵觀念：** 遮罩與位移。

### Level: Hard (困難 - Conceptual)
**Problem:** **Missing Number**
**問題：** 缺失的數字
*   **Context:** Array contains $n$ distinct numbers from $0$ to $n$.
    **情境：** 陣列包含從 $0$ 到 $n$ 的 $n$ 個相異數字。
*   **Hint:** XOR all indices ($0 \dots n$) and XOR all array values. The result is the missing number.
    **提示：** 將所有索引 ($0 \dots n$) 進行 XOR，並將所有陣列值進行 XOR。結果即為缺失的數字。
*   **Key Concept:** XOR index vs value mapping.
    **關鍵觀念：** 索引與數值的 XOR 映射。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] Did I use parentheses around bitwise operations inside conditions? (e.g., `(a & b) == 0`)
      我是否在條件句中的位元運算周圍使用了括號？
- [ ] Did I handle potential integer overflows if shifting left too far?
      如果左移太遠，我是否處理了潛在的整數溢位？
- [ ] Are variables initialized correctly? (Usually 0 for XOR/OR sums, all 1s for AND).
      變數是否正確初始化？（XOR/OR 總和通常為 0，AND 通常為全 1）。

### Complexity Check (複雜度確認)
- [ ] Is the solution $O(1)$ space? (The main selling point of bit manipulation).
      解法是否為 $O(1)$ 空間？（這是位元操作的主要賣點）。
- [ ] Is the time complexity related to the number of bits (32/64) or the input size $N$?
      時間複雜度是與位元數（32/64）相關，還是與輸入大小 $N$ 相關？

---

## 9. Memory Anchors (記憶錨點)

*   **XOR ($\oplus$) is a "Toggle Switch" or "Odd One Out Detector".**
    **XOR ($\oplus$) 是一個「切換開關」或「異類偵測器」。**
    *   Image: Two identical switches cancel each other out.
    *   圖像：兩個相同的開關會互相抵銷。
*   **Left Shift (`<<`) is "Growing".**
    **左移 (`<<`) 是「成長」。**
    *   Analogy: Adding a zero at the end of a decimal number multiplies it by 10; here it multiplies by 2.
    *   類比：在十進位數字末尾加一個零會使其乘以 10；在這裡則是乘以 2。
*   **`n & (n-1)` is "Shaving".**
    **`n & (n-1)` 是「削皮」。**
    *   Analogy: It shaves off the lowest standing hair (bit 1).
    *   類比：它削掉了最低的一根豎起的頭髮（位元 1）。