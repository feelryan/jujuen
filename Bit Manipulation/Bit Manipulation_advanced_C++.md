這裡是一份針對 **Bit Manipulation (位元操作)** 的進階面試教材。
Here is an advanced interview preparation guide for **Bit Manipulation**.

這份教材專為具備 7–12 年經驗的資深工程師設計，採用 C++ 作為實作語言。
This guide is designed for Senior Engineers with 7–12 years of experience, using C++ for implementation.

---

# Advanced Bit Manipulation for Senior Engineers

## 1. Learning Objectives (學習目標)

1.  **Master Low-Level Optimization:** Understand how bitwise operations can reduce time complexity constants and optimize space usage (e.g., Bitmasking).
    **掌握底層優化：** 理解位元運算如何降低時間複雜度常數並優化空間使用（例如：位元遮罩）。
2.  **Internalize XOR Properties:** deeply understand the properties of XOR for problems involving pairing, unique elements, and state toggling.
    **內化 XOR 特性：** 深度理解 XOR 在配對、唯一元素查找以及狀態切換問題中的特性。
3.  **Handle Bitmask DP:** Recognize patterns where the input size ($N \le 20$) suggests an exponential solution using bitmasks to represent subsets or states.
    **掌握位元遮罩動態規劃：** 識別輸入規模 ($N \le 20$) 暗示使用位元遮罩來表示子集或狀態的指數級解法模式。
4.  **Proficiency with C++ Bit Manipulation:** Utilize C++ specific features and built-ins (like `__builtin_popcount`, `std::bitset`) effectively.
    **熟練 C++ 位元操作：** 有效利用 C++ 特有的功能與內建函數（如 `__builtin_popcount`, `std::bitset`）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
Bit manipulation involves applying logical operations (AND, OR, XOR, NOT) and shift operations directly on the binary representations of integers.
位元操作涉及直接對整數的二進位表示形式應用邏輯運算（AND, OR, XOR, NOT）和移位運算。

### Intuition (直覺)
Think of an integer not as a number, but as a **vector of booleans** or a **compact set** of small indices.
不要將整數視為數字，而應將其視為**布林值向量**或小索引的**緊湊集合**。

### Complexity (複雜度)
*   **Time:** $O(1)$ for basic operations. For iterating bits, it's $O(W)$ where $W$ is the word size (usually 32 or 64).
    **時間：** 基本運算為 $O(1)$。若需遍歷位元，則為 $O(W)$，其中 $W$ 為字長（通常為 32 或 64）。
*   **Space:** $O(1)$ auxiliary space usually.
    **空間：** 通常為 $O(1)$ 輔助空間。

### Use Cases (適用場景)
*   **State Compression:** Representing a set of items (up to 64) in a single integer (e.g., visited nodes in TSP).
    **狀態壓縮：** 在單個整數中表示一組項目（最多 64 個）（例如：TSP 問題中的已訪問節點）。
*   **Set Operations:** Intersection (`&`), Union (`|`), Difference (`& ~`).
    **集合運算：** 交集 (`&`)、聯集 (`|`)、差集 (`& ~`)。
*   **Parity/Unique Checks:** Using XOR to cancel out duplicates.
    **奇偶性/唯一性檢查：** 使用 XOR 消除重複項。

### Non-Use Cases (不適用場景)
*   **High-Level Business Logic:** When readability and maintainability outweigh micro-optimizations.
    **高層業務邏輯：** 當可讀性與可維護性重於微優化時。
*   **Floating Point Math:** Direct bit manipulation on floats is dangerous without deep IEEE 754 knowledge.
    **浮點數運算：** 在缺乏深厚 IEEE 754 知識的情況下，直接對浮點數進行位元操作是危險的。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. The "Brian Kernighan's Algorithm" (Turn off rightmost 1-bit)
**Formula:** `n & (n - 1)`
**Effect:** Removes the last set bit. Used for counting bits or checking power of 2.
**效果：** 移除最後一個設為 1 的位元。用於計算位元數或檢查是否為 2 的冪。

### B. Low-bit Extraction (Extract rightmost 1-bit)
**Formula:** `n & -n` (Two's complement magic)
**Effect:** Isolates the rightmost 1-bit. Essential for Fenwick Trees (Binary Indexed Trees).
**效果：** 隔離出最右邊的 1。對於 Fenwick Tree（二元索引樹）至關重要。

### C. XOR Swapping & Cancellation
**Property:** `a ^ a = 0`, `a ^ 0 = a`, `a ^ b ^ a = b`
**Application:** Finding the unique element in an array where others appear twice.
**應用：** 在其他元素出現兩次的陣列中尋找唯一元素。

### D. Bitmask DP (Subset Iteration)
**Pattern:** Iterate through all submasks of a mask `m`.
**模式：** 遍歷遮罩 `m` 的所有子遮罩。
```cpp
// Iterate all submasks of m
// 遍歷 m 的所有子遮罩
for (int s = m; s; s = (s - 1) & m) {
    // process submask s
}
```

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number III (LeetCode 260)
**Problem Statement:** Given an integer array `nums`, in which exactly two elements appear only once and all the other elements appear exactly twice. Find the two elements that appear only once.
**問題重述：** 給定一個整數陣列 `nums`，其中恰好有兩個元素只出現一次，其餘所有元素均出現兩次。找出這兩個只出現一次的元素。

### Approach (思路)

1.  **Brute Force (Hash Map):** Count frequencies.
    *   Time: $O(N)$, Space: $O(N)$.
    *   **Critique:** Not memory efficient enough for strict constraints.
    *   **暴力法（雜湊表）：** 計算頻率。時間 $O(N)$，空間 $O(N)$。不夠節省記憶體。

2.  **Optimization (XOR All):**
    *   If we XOR all numbers, duplicates cancel out (`x ^ x = 0`).
    *   The result will be `A ^ B` (where A and B are the unique numbers).
    *   Since $A \neq B$, `A ^ B` must have at least one bit set to 1.
    *   **優化（全部 XOR）：** 若我們將所有數字 XOR，重複項會抵銷。結果將是 `A ^ B`。因為 $A \neq B$，`A ^ B` 至少有一位元是 1。

3.  **The "Aha!" Moment (Partitioning):**
    *   Pick *any* bit that is set in `A ^ B` (usually the rightmost one using `diff & -diff`).
    *   This bit acts as a differentiator: A has this bit as 1 (or 0), and B has it as 0 (or 1).
    *   We can split the original array into two groups based on this bit.
    *   **關鍵時刻（分組）：** 選取 `A ^ B` 中任一為 1 的位元（通常用 `diff & -diff` 取最右位）。此位元作為區分符：A 的該位元為 1（或 0），而 B 為 0（或 1）。我們可以根據此位元將原陣列分為兩組。

4.  **Final Step:**
    *   XOR all numbers in "Group 1" -> Result is A.
    *   XOR all numbers in "Group 2" -> Result is B.
    *   **最後步驟：** XOR "第一組" 所有數字 -> 得到 A。XOR "第二組" 所有數字 -> 得到 B。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <numeric>

class Solution {
public:
    std::vector<int> singleNumber(std::vector<int>& nums) {
        // Step 1: XOR all numbers to get (A ^ B)
        // 步驟 1：XOR 所有數字以得到 (A ^ B)
        long long diff = 0; // Use long long to prevent overflow in specific edge cases (like INT_MIN)
                            // 使用 long long 以防止特定邊界情況下的溢位（如 INT_MIN）
        for (int num : nums) {
            diff ^= num;
        }

        // Step 2: Get the rightmost set bit (the differentiator)
        // 步驟 2：取得最右邊的設定位元（區分符）
        // Note: -diff is the two's complement. (diff & -diff) isolates the last 1 bit.
        // 註：-diff 是二補數。(diff & -diff) 隔離出最後一個 1 位元。
        diff &= -diff;

        std::vector<int> result = {0, 0};

        // Step 3: Partition and XOR again
        // 步驟 3：分組並再次 XOR
        for (int num : nums) {
            if ((num & diff) == 0) {
                // Group where the bit is not set
                // 該位元未設定的組
                result[0] ^= num;
            } else {
                // Group where the bit is set
                // 該位元已設定的組
                result[1] ^= num;
            }
        }

        return result;
    }
};
```

### Complexity & Edge Cases (複雜度與邊界條件)
*   **Time:** $O(N)$ (Two passes).
    **時間：** $O(N)$（兩次遍歷）。
*   **Space:** $O(1)$ (Only variables used).
    **空間：** $O(1)$（僅使用變數）。
*   **Edge Case:** `INT_MIN`. Its negation in 32-bit signed integer is undefined/overflows. Using `long long` or casting to `unsigned int` handles this safely.
    **邊界條件：** `INT_MIN`。其 32 位元有號整數的負值是未定義或溢位的。使用 `long long` 或轉型為 `unsigned int` 可安全處理。

---

## 5. Common Pitfalls (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Operator Precedence** <br> **運算符優先級** | `a & b == 0` is parsed as `a & (b == 0)`. **Always wrap bitwise ops in parentheses.** <br> `a & b == 0` 會被解析為 `a & (b == 0)`。**務必將位元運算用括號包起來。** |
| **Signed Shift (`>>`)** <br> **有號移位** | In C++, `>>` on negative numbers is implementation-defined (usually arithmetic shift, preserving sign). <br> 在 C++ 中，對負數使用 `>>` 是實作定義的（通常是算術移位，保留符號）。 |
| **Overflow on Shift** <br> **移位溢位** | `1 << 31` implies a signed integer. If you need a mask for the 31st bit, use `1U << 31` or `1LL << 31`. <br> `1 << 31` 隱含為有號整數。若需第 31 位元的遮罩，請用 `1U << 31` 或 `1LL << 31`。 |
| **Logical vs Bitwise** <br> **邏輯與位元** | `&&` vs `&`. `&&` short-circuits and returns bool; `&` processes all bits. Don't mix them up. <br> `&&` 與 `&`。`&&` 會短路並回傳布林值；`&` 處理所有位元。切勿混淆。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify the constraint:** "Since the input array size is small ($N \le 20$), this suggests an exponential time complexity solution, likely involving Bitmask DP."
    **識別限制：** 「由於輸入陣列規模很小 ($N \le 20$)，這暗示了指數級時間複雜度的解法，很可能涉及位元遮罩動態規劃。」
2.  **Justify Bit Manipulation:** "I will use a bitmask to represent the state of the set. This allows $O(1)$ set operations and reduces memory overhead compared to `std::set` or `std::vector<bool>`."
    **論證位元操作：** 「我將使用位元遮罩來表示集合狀態。這允許 $O(1)$ 的集合運算，且比 `std::set` 或 `std::vector<bool>` 更節省記憶體開銷。」
3.  **Clarify Types:** "I'll use `unsigned int` or `uint32_t` to avoid issues with sign extension during shifts."
    **釐清型別：** 「我會使用 `unsigned int` 或 `uint32_t` 以避免移位時的符號擴展問題。」

### Whiteboard Strategy (白板策略)
*   **Write helper functions:** If doing complex masking, define `bool isSet(int mask, int i)` or `int toggle(int mask, int i)` to keep the main logic clean.
    **撰寫輔助函數：** 若進行複雜遮罩操作，定義 `bool isSet(...)` 或 `int toggle(...)` 以保持主邏輯清晰。
*   **Trace with small example:** Use 4 bits (e.g., `1010`) to demonstrate your logic manually before coding loops.
    **用小範例追蹤：** 在編寫迴圈前，使用 4 位元（如 `1010`）手動演示你的邏輯。

---

## 7. Practice Problems (練習題)

### Easy: Number of 1 Bits (Hamming Weight)
*   **Prompt:** Write a function that takes an unsigned integer and returns the number of '1' bits it has.
    **題目：** 寫一個函數，接收無號整數並回傳其 '1' 位元的數量。
*   **Hint:** Use `n & (n-1)` loop or `__builtin_popcount(n)` (mentioning you know the builtin is a bonus).
    **提示：** 使用 `n & (n-1)` 迴圈或 `__builtin_popcount(n)`（提及你知道內建函數是加分項）。

### Medium: Subsets (Power Set)
*   **Prompt:** Given an integer array `nums` of unique elements, return all possible subsets.
    **題目：** 給定一個包含唯一元素的整數陣列 `nums`，回傳所有可能的子集。
*   **Hint:** Iterate from `0` to `2^N - 1`. If the $j$-th bit of iterator `i` is set, include `nums[j]`.
    **提示：** 從 `0` 遍歷到 `2^N - 1`。若迭代器 `i` 的第 $j$ 位元已設定，則包含 `nums[j]`。

### Hard: Smallest Sufficient Team (LeetCode 1125)
*   **Prompt:** Given a list of required skills and a list of people with their skills, find the smallest team to cover all skills.
    **題目：** 給定所需技能列表與擁有所述技能的人員列表，找出能覆蓋所有技能的最小團隊。
*   **Hint:**
    1. Map each skill to a bit index (0 to M-1).
    2. Convert each person's skills into a bitmask.
    3. Use DP: `dp[mask]` = minimum people to achieve skill mask.
    4. Transition: `dp[mask | person_skill] = min(dp[mask | person_skill], dp[mask] + 1)`.
    **提示：**
    1. 將每個技能映射到位元索引 (0 到 M-1)。
    2. 將每個人的技能轉換為位元遮罩。
    3. 使用 DP：`dp[mask]` = 達成技能遮罩所需的最小人數。
    4. 轉移方程：`dp[mask | person_skill] = min(...)`。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] **Parentheses:** Did I wrap `(a & b)` before comparing?
    **括號：** 我是否在比較前將 `(a & b)` 包起來了？
- [ ] **Base:** Did I use `1LL` when shifting more than 31 bits?
    **基底：** 當移位超過 31 位時，我是否使用了 `1LL`？
- [ ] **Loop Termination:** In `while (n > 0)`, does `n` actually decrease? (e.g., `n >>= 1` or `n &= (n-1)`).
    **迴圈終止：** 在 `while (n > 0)` 中，`n` 真的有減少嗎？
- [ ] **Sign:** Am I using `unsigned` for logical shifts to avoid sign extension dragging 1s from the left?
    **符號：** 我是否使用 `unsigned` 進行邏輯移位，以避免符號擴展從左側拖入 1？

---

## 9. Memory Anchors (記憶錨點)

### Visual Analogy (圖像類比)
*   **XOR as a Light Switch:** Pressing the switch twice returns it to the original state. `A ^ B ^ B = A`.
    **XOR 像電燈開關：** 按兩次開關會回到原始狀態。`A ^ B ^ B = A`。
*   **Mask as a Gatekeeper:** `x & mask` only lets bits pass where `mask` is 1. Like a security filter.
    **Mask 像守門員：** `x & mask` 只允許 `mask` 為 1 的位置通過。就像安全過濾器。

### Key Idioms (關鍵慣用語)
*   **"Strip the last 1":** `n & (n-1)`
*   **"Isolate the last 1":** `n & -n`
*   **"Toggle bit k":** `n ^ (1 << k)`
*   **"Check bit k":** `(n >> k) & 1`