Here is a comprehensive guide on **Bit Manipulation** tailored for a Senior Software Engineer, designed for intermediate-level mastery and interview preparation.

這是一份針對 **位元操作（Bit Manipulation）** 的完整教材，專為資深軟體工程師量身打造，旨在達到中階掌握度並做好面試準備。

---

# Bit Manipulation Interview Guide (Intermediate)
# 位元操作面試指南（中階）

## 1. Learning Objectives (學習目標)

1.  **Master Core Operators & Precedence**: Deeply understand `&`, `|`, `^`, `~`, `<<`, `>>` and their precedence in C++.
    **掌握核心運算子與優先級**：深入理解 `&`、`|`、`^`、`~`、`<<`、`>>` 及其在 C++ 中的運算優先順序。

2.  **Internalize Key Patterns**: Proficiency in XOR cancellation (`x ^ x = 0`) and Brian Kernighan’s algorithm (`n & (n-1)`).
    **內化關鍵模式**：熟練運用 XOR 抵銷特性（`x ^ x = 0`）與 Brian Kernighan 演算法（`n & (n-1)`）。

3.  **Apply Bitmasks for State/Subsets**: Use bitmaps to represent sets or states for DP and combinatorial problems.
    **應用位元遮罩處理狀態/子集**：使用位圖（bitmap）來表示集合或狀態，以解決動態規劃與組合問題。

4.  **Optimize Space & Time**: Recognize when bit manipulation transforms $O(N)$ space to $O(1)$ space.
    **優化空間與時間**：識別何時位元操作能將 $O(N)$ 空間複雜度優化至 $O(1)$。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Bit manipulation involves applying logical operations directly on the binary representation of data.
位元操作涉及直接對資料的二進位表示形式應用邏輯運算。

### Intuition (直覺)
Think of an integer not as a number, but as a **vector of 32 (or 64) booleans**.
不要將整數視為數字，而應將其視為一個包含 **32（或 64）個布林值的向量**。
It allows parallel processing of these booleans and efficient set operations.
它允許對這些布林值進行平行處理以及高效的集合運算。

### Complexity (複雜度)
*   **Time**: $O(1)$ for standard operations on fixed-width integers (e.g., 32-bit `int`).
    **時間**：對於固定寬度的整數（如 32 位元 `int`），標準運算為 $O(1)$。
*   **Space**: $O(1)$ auxiliary space usually.
    **空間**：通常僅需 $O(1)$ 的輔助空間。

### When to Use (適用場景)
*   **Low-level optimization**: Packing data, flags, or permissions.
    **底層優化**：打包資料、標誌（flags）或權限。
*   **Set operations**: Intersection, union, or checking existence in a small universe.
    **集合運算**：在小範圍內的交集、聯集或存在性檢查。
*   **Math tricks**: Multiplying/dividing by powers of 2, finding unique numbers.
    **數學技巧**：乘以/除以 2 的冪次、尋找唯一數字。

### When NOT to Use (不適用場景)
*   **Complex Business Logic**: Reduces readability significantly.
    **複雜業務邏輯**：會顯著降低程式碼可讀性。
*   **Floating Point Arithmetic**: Unless you are implementing IEEE 754 logic directly.
    **浮點數運算**：除非你正在直接實作 IEEE 754 邏輯。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: The XOR Trick (XOR 技巧)
*   **Property**: `a ^ a = 0` and `a ^ 0 = a`.
    **特性**：`a ^ a = 0` 且 `a ^ 0 = a`。
*   **Use**: Finding unique elements in an array where others repeat an even number of times.
    **用途**：在其他元素重複偶數次的陣列中尋找唯一元素。

### Pattern B: Clearing the Lowest Set Bit (清除最低位元)
*   **Formula**: `n = n & (n - 1)`.
    **公式**：`n = n & (n - 1)`。
*   **Use**: Counting set bits (Hamming Weight), checking if a number is a power of 2.
    **用途**：計算設置位元（漢明權重）、檢查數字是否為 2 的冪次。

### Pattern C: Extracting the Lowest Set Bit (提取最低位元)
*   **Formula**: `bit = n & (-n)` (Two's complement magic).
    **公式**：`bit = n & (-n)`（二補數的魔法）。
*   **Use**: Fenwick Trees (Binary Indexed Trees), partitioning numbers based on bits.
    **用途**：Fenwick Tree（二元索引樹）、基於位元對數字進行分區。

### Pattern D: Bitmasking for Subsets (子集位元遮罩)
*   **Logic**: Iterate from `0` to `2^N - 1`. If the $j$-th bit is set, include the $j$-th element.
    **邏輯**：從 `0` 迭代到 `2^N - 1`。如果第 $j$ 個位元被設置，則包含第 $j$ 個元素。

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number III (LeetCode 260)
**Problem Statement**: Given an integer array `nums`, in which exactly two elements appear only once and all the other elements appear exactly twice. Find the two elements that appear only once.
**問題重述**：給定一個整數陣列 `nums`，其中恰好有兩個元素只出現一次，其餘所有元素均出現兩次。找出這兩個只出現一次的元素。

### Approach (思路)

1.  **Brute Force (Hash Map)**:
    *   Count frequency of every number. Return those with count 1.
    *   計算每個數字的頻率。回傳計數為 1 的數字。
    *   *Time*: $O(N)$, *Space*: $O(N)$. (Interview expectation: Optimize Space).
    *   *時間*：$O(N)$，*空間*：$O(N)$。（面試期望：優化空間）。

2.  **Optimization (XOR Global)**:
    *   XOR all numbers. Result `diff = x ^ y` (where `x` and `y` are the targets).
    *   對所有數字進行 XOR。結果 `diff = x ^ y`（其中 `x` 和 `y` 是目標數字）。
    *   Since `x != y`, `diff` must have at least one bit set to 1.
    *   因為 `x != y`，`diff` 必定至少有一個位元為 1。

3.  **Optimal (Divide and Conquer via Bitmask)**:
    *   Find the rightmost set bit of `diff` using `diff & (-diff)`. Let's call this `mask`.
    *   使用 `diff & (-diff)` 找出 `diff` 最右邊的設置位元。我們稱之為 `mask`。
    *   This bit is 1 in `x` and 0 in `y` (or vice versa).
    *   這個位元在 `x` 中為 1，在 `y` 中為 0（反之亦然）。
    *   Divide all numbers into two groups: those with this bit set, and those without.
    *   將所有數字分為兩組：該位元被設置的，與該位元未被設置的。
    *   XORing each group separately reveals `x` and `y`.
    *   分別對每組進行 XOR 運算即可揭示 `x` 和 `y`。

### C++ Reference Solution (參考解)

```cpp
#include <vector>
#include <numeric>

class Solution {
public:
    std::vector<int> singleNumber(std::vector<int>& nums) {
        // Step 1: XOR all numbers to get (x ^ y)
        // 步驟 1：對所有數字進行 XOR 以取得 (x ^ y)
        long long diff = 0; // Use long long to prevent overflow in step 2 (e.g., INT_MIN)
                            // 使用 long long 防止步驟 2 中的溢位（例如 INT_MIN）
        for (int num : nums) {
            diff ^= num;
        }

        // Step 2: Extract the rightmost set bit
        // 步驟 2：提取最右邊的設置位元
        // Explanation: -diff is the two's complement (~diff + 1)
        // 解釋：-diff 是二補數 (~diff + 1)
        // Example: diff = 6 (110), -diff = (010), result = 010 (2)
        int mask = diff & (-diff);

        int x = 0;
        int y = 0;

        // Step 3: Partition numbers into two groups and XOR separately
        // 步驟 3：將數字分為兩組並分別進行 XOR
        for (int num : nums) {
            if ((num & mask) == 0) {
                // Group A: Bit is not set
                // A 組：位元未設置
                x ^= num;
            } else {
                // Group B: Bit is set
                // B 組：位元已設置
                y ^= num;
            }
        }

        return {x, y};
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time**: $O(N)$ — We iterate through the array twice.
    **時間**：$O(N)$ — 我們遍歷陣列兩次。
*   **Space**: $O(1)$ — Only a few variables used.
    **空間**：$O(1)$ — 僅使用了少數變數。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall (概念/陷阱) | Explanation (解釋) |
| :--- | :--- |
| **Operator Precedence**<br>**運算子優先級** | `==` has higher precedence than `&`.<br>`if (x & 1 == 0)` actually evaluates as `if (x & (1 == 0))` which is wrong.<br>**Correct**: `if ((x & 1) == 0)`.<br>`==` 的優先級高於 `&`。<br>`if (x & 1 == 0)` 實際上會被評估為 `if (x & (1 == 0))`，這是錯誤的。<br>**正確**：`if ((x & 1) == 0)`。 |
| **Signed Integer Overflow**<br>**有號整數溢位** | Left shifting a negative number or shifting into the sign bit is undefined behavior in older C++ standards (fixed in C++20, but risky).<br>**Advice**: Always use `unsigned` types for bit manipulation.<br>左移負數或移入符號位元在舊版 C++ 標準中是未定義行為（C++20 已修正，但仍有風險）。<br>**建議**：進行位元操作時始終使用 `unsigned` 類型。 |
| **Right Shift: `>>`**<br>**右移：`>>`** | **Arithmetic Shift** (preserves sign) vs **Logical Shift** (fills with 0).<br>In C++, `>>` on signed integers is usually arithmetic.<br>**算術移位**（保留符號）vs **邏輯移位**（補 0）。<br>在 C++ 中，對有號整數使用 `>>` 通常是算術移位。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify the Binary Nature**: "Since we are dealing with states/sets/unique IDs, bit manipulation might offer $O(1)$ space optimization."
    **識別二進位本質**：「由於我們正在處理狀態/集合/唯一 ID，位元操作可能提供 $O(1)$ 的空間優化。」
2.  **Propose the Pattern**: "I can use XOR to cancel out duplicates..." or "I can use a bitmask to iterate subsets..."
    **提出模式**：「我可以使用 XOR 來抵銷重複項……」或「我可以使用位元遮罩來迭代子集……」
3.  **Address Constraints**: Mention word size (32/64 bit) limitations immediately.
    **處理限制**：立即提及字組大小（32/64 位元）的限制。

### Whiteboard Strategy (白板策略)
*   **Trace with Small Bits**: Don't use `254`. Use `6` (`110`) or `5` (`101`).
    **用小位元數追蹤**：不要使用 `254`。使用 `6` (`110`) 或 `5` (`101`)。
*   **Columnar Addition**: When explaining XOR or counting, align bits vertically on the board.
    **直式加法**：解釋 XOR 或計數時，在白板上垂直對齊位元。

### Common Follow-ups (常見追問)
*   **Q**: What if the number of bits exceeds 64?
    **問**：如果位元數超過 64 怎麼辦？
    *   **A**: Use `std::bitset` or an array of integers (BitSet implementation).
    *   **答**：使用 `std::bitset` 或整數陣列（BitSet 實作）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Number of 1 Bits (Hamming Weight)
*   **Task**: Write a function that takes an unsigned integer and returns the number of '1' bits it has.
    **任務**：編寫一個函式，接收一個無號整數並回傳其擁有的 '1' 位元數量。
*   **Hint**: Loop with `n = n & (n-1)` until `n` is 0.
    **提示**：使用 `n = n & (n-1)` 進行迴圈，直到 `n` 為 0。

### 2. Medium: Subsets (LeetCode 78)
*   **Task**: Given an integer array `nums` of unique elements, return all possible subsets (the power set).
    **任務**：給定一個包含唯一元素的整數陣列 `nums`，回傳所有可能的子集（冪集）。
*   **Hint**: Iterate `i` from `0` to `2^n - 1`. If `(i >> j) & 1` is true, include `nums[j]`.
    **提示**：將 `i` 從 `0` 迭代到 `2^n - 1`。如果 `(i >> j) & 1` 為真，則包含 `nums[j]`。

### 3. Hard: Single Number II (LeetCode 137)
*   **Task**: Every element appears **three** times except for one. Find that single one.
    **任務**：除了某個元素外，每個元素都出現 **三次**。找出那個唯一的元素。
*   **Hint**: Design a digital logic circuit. Count bits at each position modulo 3. Or use `ones` and `twos` variables to track state transitions.
    **提示**：設計一個數位邏輯電路。計算每個位置的位元數並對 3 取模。或者使用 `ones` 和 `twos` 變數來追蹤狀態轉換。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] **Parentheses**: Did I wrap `(a & b)` in parentheses inside `if` conditions?
    **括號**：我是否在 `if` 條件中將 `(a & b)` 用括號包起來了？
- [ ] **Type Safety**: Am I using `unsigned` for shifting logic to avoid sign extension issues?
    **型別安全**：我是否在移位邏輯中使用了 `unsigned` 以避免符號擴展問題？
- [ ] **Base Case**: Does the code handle `0`, `INT_MAX`, `INT_MIN`?
    **基本情況**：程式碼是否處理了 `0`、`INT_MAX`、`INT_MIN`？
- [ ] **Loop Termination**: If using `n >>= 1`, does it terminate for `-1` (if signed)?
    **迴圈終止**：如果使用 `n >>= 1`，對於 `-1`（若為有號數）是否會終止？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### XOR is a "Difference Detector" (XOR 是「差異偵測器」)
*   **Image**: Imagine two identical switches toggled. The light stays OFF (0). One switch toggled? Light ON (1).
    **圖像**：想像兩個相同的開關被切換。燈保持關閉（0）。切換其中一個開關？燈亮起（1）。
*   **Mnemonic**: "Same is Zero, Different is One."
    **口訣**：「相同為零，不同為一。」

### `n & (n-1)` is "Turning off the rightmost light" (`n & (n-1)` 是「關掉最右邊的燈」)
*   **Image**: Imagine a row of lights. This operation finds the last light that is ON and smashes it.
    **圖像**：想像一排燈。這個操作會找到最後一盞亮著的燈並將其打破。

### Masking is a "Filter" (遮罩是「濾鏡」)
*   **Analogy**: Like a stencil in spray painting. `&` blocks paint where the stencil is solid (0) and lets paint through where cut out (1).
    **類比**：就像噴漆中的模板。`&` 在模板實心（0）的地方阻擋油漆，在鏤空（1）的地方讓油漆通過。