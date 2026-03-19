Here is the comprehensive interview preparation guide for **Bit Manipulation** at the **Advanced** level, tailored for a Senior Software Engineer.

這是一份針對 **位元操作（Bit Manipulation）** 的 **進階（Advanced）** 面試準備指南，專為資深軟體工程師量身打造。

---

# Advanced Bit Manipulation Interview Guide
# 進階位元操作面試指南

## 1. Learning Goals (學習目標)

*   **Master State Compression (Bitmasking):** Learn to represent complex sets or boolean states using integers to optimize Space Complexity and facilitate Dynamic Programming.
    **掌握狀態壓縮（Bitmasking）：** 學習使用整數來表示複雜的集合或布林狀態，以優化空間複雜度並促進動態規劃（DP）。
*   **Deep Dive into XOR Properties:** Understand advanced XOR applications beyond simple swapping, such as isolating unique elements in linear time.
    **深入理解 XOR 特性：** 理解 XOR 在簡單交換之外的進階應用，例如在線性時間內分離唯一元素。
*   **Low-level Optimization Techniques:** Utilize techniques like `x & (-x)` (lowbit) and Brian Kernighan’s algorithm for high-performance counting and indexing.
    **底層優化技巧：** 運用如 `x & (-x)`（lowbit）與 Brian Kernighan 演算法來進行高效能的計數與索引。
*   **Handle Java Specifics:** Navigate Java's signed integers, 2's complement representation, and logical vs. arithmetic shifts (`>>` vs `>>>`).
    **掌握 Java 特性：** 熟悉 Java 的有號整數、二補數表示法，以及邏輯位移與算術位移的區別（`>>` vs `>>>`）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Bit manipulation involves applying logical operations on the binary representations of integers.
位元操作涉及對整數的二進位表示形式應用邏輯運算。
For senior engineers, it is not just about binary math; it is about **parallelism** (processing 32/64 bits at once) and **hashing** (mapping states to unique integers).
對於資深工程師而言，這不僅是二進位數學；它是關於**平行處理**（一次處理 32/64 位元）與**雜湊**（將狀態映射為唯一整數）。

### Complexity (複雜度)
*   **Time:** Most bitwise operations are $O(1)$ (CPU cycle level).
    **時間：** 大多數位元運算皆為 $O(1)$（CPU 週期等級）。
*   **Space:** $O(1)$ auxiliary space is common, replacing $O(N)$ boolean arrays.
    **空間：** 通常為 $O(1)$ 輔助空間，用以取代 $O(N)$ 的布林陣列。

### When to Use (適用場景)
*   **State Compression DP:** When $N$ is small (e.g., $N \le 20$), allowing $O(2^N)$ complexity.
    **狀態壓縮 DP：** 當 $N$ 很小（例如 $N \le 20$），允許 $O(2^N)$ 複雜度時。
*   **Set Operations:** Intersection, union, and negation of small sets.
    **集合運算：** 小集合的交集、聯集與補集運算。
*   **Mathematical Tricks:** Finding duplicates, missing numbers, or parity checks.
    **數學技巧：** 尋找重複值、缺失數字或奇偶校驗。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: The XOR Trick (XOR 技巧)
*   **Concept:** $A \oplus A = 0$ and $A \oplus 0 = A$. Order doesn't matter.
    **觀念：** $A \oplus A = 0$ 且 $A \oplus 0 = A$。順序不影響結果。
*   **Application:** "Single Number" problems, finding missing numbers in arrays.
    **應用：** 「只出現一次的數字」問題，尋找陣列中的缺失數字。

### Pattern B: Masking & State Compression (遮罩與狀態壓縮)
*   **Concept:** Use the $i$-th bit to represent the presence of the $i$-th item.
    **觀念：** 使用第 $i$ 個位元來表示第 $i$ 個項目的存在與否。
*   **Operations:**
    *   Set bit: `mask | (1 << i)`
    *   Check bit: `(mask >> i) & 1` or `(mask & (1 << i)) != 0`
    *   Toggle bit: `mask ^ (1 << i)`

### Pattern C: Lowbit / Isolation (Lowbit / 隔離)
*   **Concept:** Extract the rightmost 1-bit.
    **觀念：** 提取最右側的 1-bit。
*   **Formula:** `x & (-x)`
    **公式：** `x & (-x)`
*   **Why:** In 2's complement, `-x` is `~x + 1`. This effectively isolates the lowest set bit.
    **原因：** 在二補數系統中，`-x` 等於 `~x + 1`。這能有效地隔離出最低位的 1。

### Pattern D: Brian Kernighan’s Algorithm (Brian Kernighan 演算法)
*   **Concept:** Turn off the rightmost 1-bit.
    **觀念：** 消除最右側的 1-bit。
*   **Formula:** `x & (x - 1)`
    **公式：** `x & (x - 1)`
*   **Application:** Counting set bits (Hamming Weight) efficiently.
    **應用：** 高效計算設置位元的數量（漢明權重）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number III (LeetCode 260)
**Problem Statement:** Given an integer array `nums`, in which exactly two elements appear only once and all the other elements appear exactly twice. Find the two elements that appear only once.
**問題重述：** 給定一個整數陣列 `nums`，其中恰好有兩個元素只出現一次，其餘所有元素皆出現兩次。找出這兩個只出現一次的元素。

#### 1. Approach: Brute Force (HashMap)
*   **Logic:** Count frequency of every number.
    **邏輯：** 計算每個數字的頻率。
*   **Complexity:** Time $O(N)$, Space $O(N)$.
    **複雜度：** 時間 $O(N)$，空間 $O(N)$。
*   **Critique:** Not optimal for space. The interviewer expects $O(1)$ space.
    **評論：** 空間並非最佳。面試官通常期望 $O(1)$ 空間。

#### 2. Optimization: XOR All (Global XOR)
*   **Logic:** If we XOR all numbers, the duplicates cancel out ($A \oplus A = 0$).
    **邏輯：** 如果我們對所有數字進行 XOR，重複的數字會互相抵銷（$A \oplus A = 0$）。
*   **Result:** The result is $X \oplus Y$, where $X$ and $Y$ are the two unique numbers.
    **結果：** 結果為 $X \oplus Y$，其中 $X$ 與 $Y$ 是那兩個唯一的數字。
*   **Challenge:** How to separate $X$ and $Y$ from $X \oplus Y$?
    **挑戰：** 如何從 $X \oplus Y$ 中分離出 $X$ 和 $Y$？

#### 3. Optimal Solution: XOR + Grouping (The Divider)
*   **Insight:** Since $X \neq Y$, their XOR sum must have at least one bit set to 1. This bit represents a position where $X$ and $Y$ differ (one has 0, the other has 1).
    **洞察：** 由於 $X \neq Y$，它們的 XOR 和必然至少有一個位元是 1。這個位元代表 $X$ 和 $Y$ 在該位置上不同（一個是 0，另一個是 1）。
*   **Strategy:** Pick the rightmost 1-bit (using `diff & -diff`) as a "divider". Use this divider to split the original array into two groups.
    **策略：** 選取最右側的 1-bit（使用 `diff & -diff`）作為「分隔符」。利用此分隔符將原陣列分為兩組。
*   **Result:** One group contains $X$ (and duplicates), the other contains $Y$ (and duplicates). XORing each group reveals $X$ and $Y$.
    **結果：** 一組包含 $X$（及重複值），另一組包含 $Y$（及重複值）。對每組進行 XOR 即可解出 $X$ 與 $Y$。

#### Java Reference Solution (Java 參考解)

```java
class Solution {
    public int[] singleNumber(int[] nums) {
        // Step 1: XOR all numbers to get (x ^ y)
        // 步驟 1：對所有數字進行 XOR 以取得 (x ^ y)
        int bitmask = 0;
        for (int num : nums) {
            bitmask ^= num;
        }

        // Step 2: Get the rightmost set bit (the differentiator)
        // 步驟 2：取得最右側的設置位元（區分者）
        // Note: In 2's complement, -bitmask is (~bitmask + 1)
        // 註：在二補數中，-bitmask 即為 (~bitmask + 1)
        int diff = bitmask & (-bitmask);

        int x = 0;
        // Step 3: Iterate again and group numbers based on the 'diff' bit
        // 步驟 3：再次遍歷，並根據 'diff' 位元將數字分組
        for (int num : nums) {
            // If the bit is set, XOR into x.
            // 如果該位元被設置，則 XOR 進 x。
            // (We don't need a variable for y; y can be derived later)
            // (我們不需要 y 的變數；y 可以稍後推導出來)
            if ((num & diff) != 0) {
                x ^= num;
            }
        }

        // Step 4: Derive y from the original bitmask (x ^ y)
        // 步驟 4：從原始的 bitmask (x ^ y) 推導出 y
        // Since bitmask = x ^ y, then bitmask ^ x = y
        // 因為 bitmask = x ^ y，所以 bitmask ^ x = y
        int y = bitmask ^ x;

        return new int[]{x, y};
    }
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Operator Precedence**<br>運算符優先級 | `==` has higher precedence than `&`.<br>`a & b == 0` is interpreted as `a & (b == 0)`. **Always use parentheses:** `(a & b) == 0`.<br>`==` 的優先級高於 `&`。<br>`a & b == 0` 會被解讀為 `a & (b == 0)`。**務必使用括號：** `(a & b) == 0`。 |
| **Signed vs Unsigned Shift**<br>有號 vs 無號位移 | `>>` preserves the sign bit (arithmetic shift). `>>>` fills with zero (logical shift).<br>Use `>>>` for raw bit manipulation to avoid infinite loops with negative numbers.<br>`>>` 保留符號位元（算術位移）。`>>>` 補零（邏輯位移）。<br>進行純位元操作時請使用 `>>>`，以避免負數造成的無窮迴圈。 |
| **Integer Overflow**<br>整數溢位 | Shifting `1 << 31` is negative in a 32-bit signed integer. If you need a mask for index > 30, use `1L << i`.<br>在 32 位元有號整數中，`1 << 31` 是負數。若需大於 30 的索引遮罩，請使用 `1L << i`。 |
| **Mod vs AND**<br>取模 vs AND | `x % 2^k` is equivalent to `x & (2^k - 1)`. This is faster but only works for powers of 2.<br>`x % 2^k` 等價於 `x & (2^k - 1)`。這比較快，但僅適用於 2 的冪次。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (口條框架)
1.  **Identify Binary Nature:** "Since we are dealing with two states/unique IDs/set operations, I'm thinking about Bit Manipulation to optimize space."
    **識別二進位本質：** 「既然我們在處理兩種狀態/唯一 ID/集合運算，我考慮使用位元操作來優化空間。」
2.  **Explain the Mask:** "I will use an integer as a bitmask where the $i$-th bit represents..."
    **解釋遮罩：** 「我將使用一個整數作為位元遮罩，其中第 $i$ 個位元代表...」
3.  **Justify Complexity:** "This allows us to perform set union/intersection in $O(1)$ time, reducing the overhead of HashSets."
    **證成複雜度：** 「這允許我們在 $O(1)$ 時間內執行集合聯集/交集，減少 HashSet 的開銷。」

### Whiteboard Strategy (白板策略)
*   **Write Helpers:** Define `getBit(n, i)`, `setBit(n, i)` if the logic is complex. It shows clean coding standards.
    **撰寫輔助函式：** 若邏輯複雜，定義 `getBit(n, i)`、`setBit(n, i)`。這展現了整潔的編碼標準。
*   **Trace with Examples:** Write binary explicitly (e.g., `5 (101) ^ 3 (011) = 6 (110)`) to visualize logic for the interviewer.
    **用範例追蹤：** 明確寫出二進位（例如 `5 (101) ^ 3 (011) = 6 (110)`）以便向面試官視覺化邏輯。

### Common Follow-ups (常見追問)
*   "What if the input array is very large (billions)?" -> Discuss **BitSet** or Bloom Filters.
    「如果輸入陣列非常大（數十億）怎麼辦？」 -> 討論 **BitSet** 或 Bloom Filters。
*   "What if we need to handle negative numbers?" -> Discuss 2's complement implications.
    「如果我們需要處理負數怎麼辦？」 -> 討論二補數的影響。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Number of 1 Bits (Hamming Weight)**
**Hint:** Use `n & (n-1)` loop to count until `n` becomes 0.
**提示：** 使用 `n & (n-1)` 迴圈計數，直到 `n` 變為 0。

### Level: Medium (Standard)
**Problem:** **Subsets (LeetCode 78)**
**Hint:** Iterate from `0` to `2^N - 1`. The bitmask of the iterator determines which elements are included in the current subset.
**提示：** 從 `0` 迭代至 `2^N - 1`。迭代器的位元遮罩決定當前子集包含哪些元素。

### Level: Hard (Differentiation)
**Problem:** **Smallest Sufficient Team (LeetCode 1125)**
**Hint:** This is **Bitmask DP**.
1. Map each skill to a bit index (0 to `m-1`).
2. `dp[mask]` stores the smallest team for a given skill set `mask`.
3. Transition: `dp[mask | person_skills] = min(dp[mask | person_skills], dp[mask] + person)`.
**提示：** 這是 **位元遮罩動態規劃（Bitmask DP）**。
1. 將每項技能映射為位元索引（0 到 `m-1`）。
2. `dp[mask]` 儲存給定技能集 `mask` 的最小團隊。
3. 轉移方程式：`dp[mask | person_skills] = min(dp[mask | person_skills], dp[mask] + person)`。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
- [ ] **Parentheses:** Did I wrap bitwise operations in `( )` before comparing?
    **括號：** 我是否在比較前將位元運算用 `( )` 包起來了？
- [ ] **Loop Termination:** If using `>>`, did I use `>>>` to handle negative inputs correctly?
    **迴圈終止：** 如果使用 `>>`，我是否使用了 `>>>` 來正確處理負數輸入？
- [ ] **Data Type:** Will `1 << i` overflow? Should I use `1L << i`?
    **資料型態：** `1 << i` 會溢位嗎？我應該使用 `1L << i` 嗎？
- [ ] **Base Case:** Is the mask initialized to 0 or -1 (all 1s) correctly?
    **基本情況：** 遮罩是否正確初始化為 0 或 -1（全 1）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Light Switch Panel (開關面板):**
    Think of an integer as a row of 32 light switches.
    *   **AND:** Are *both* switches on?
    *   **OR:** Is *at least one* switch on?
    *   **XOR:** Are the switches *different*? (Toggle switch).
    **將整數想像成一排 32 個電燈開關。**
    *   **AND：** *兩個*開關都開了嗎？
    *   **OR：** *至少有一個*開關開了嗎？
    *   **XOR：** 開關狀態*不同*嗎？（切換開關）。

*   **The DNA Strand (DNA 鏈):**
    Bitmasking is like compressing a complex DNA sequence into a single numeric ID. Instead of storing `["skill_a", "skill_b"]`, we store `011` (binary).
    **位元遮罩就像將複雜的 DNA 序列壓縮成單一數字 ID。** 我們不儲存 `["skill_a", "skill_b"]`，而是儲存 `011`（二進位）。

*   **The Magic Eraser (神奇橡皮擦):**
    `n & (n-1)` is a magic eraser that specifically rubs out the last "1" you drew, leaving everything else untouched.
    **`n & (n-1)` 是一個神奇橡皮擦**，它專門擦掉你畫的最後一個「1」，而保持其他部分不動。