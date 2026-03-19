Here is the complete interview preparation guide for **Bit Manipulation** (Beginner Level), tailored for a Senior Software Engineer using Java.

這是一份針對 **位元操作（Bit Manipulation）**（初級難度）的完整面試準備教材，專為使用 Java 的資深軟體工程師量身打造。

---

# Bit Manipulation Interview Guide (Beginner)
# 位元操作面試指南（初級）

## 1. Learning Objectives (學習目標)

*   **Master Fundamental Operators:** Understand the mechanics of AND (`&`), OR (`|`), XOR (`^`), NOT (`~`), and Shifts (`<<`, `>>`, `>>>`).
    **掌握基本運算子：** 理解 AND (`&`)、OR (`|`)、XOR (`^`)、NOT (`~`) 以及位移（`<<`, `>>`, `>>>`）的運作機制。
*   **Understand Bit Masking:** Learn how to set, clear, toggle, and query specific bits using masks.
    **理解位元遮罩（Bit Masking）：** 學習如何使用遮罩來設定、清除、切換與查詢特定的位元。
*   **Leverage XOR Properties:** Recognize scenarios where XOR properties (e.g., self-inverse) optimize space complexity.
    **利用 XOR 特性：** 識別 XOR 特性（如自反性）能優化空間複雜度的場景。
*   **Java Specifics:** Distinguish between signed (`>>`) and unsigned (`>>>`) right shifts in Java.
    **Java 特性：** 區分 Java 中的有號右移（`>>`）與無號右移（`>>>`）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
Bit manipulation involves applying logical operations on individual bits of integers to perform calculations or manage state efficiently.
位元操作涉及對整數的個別位元應用邏輯運算，以高效地執行計算或管理狀態。

### Intuition (直覺)
Think of an integer not just as a number, but as an array of 32 (or 64) booleans, where each bit represents a flag or a power of 2.
不要只把整數看作數字，試著把它想像成一個包含 32（或 64）個布林值的陣列，其中每個位元代表一個標記或 2 的次方。

### Complexity (複雜度)
*   **Time:** $O(1)$ for standard operations on fixed-width integers (e.g., 32-bit `int`).
    **時間：** 對於固定寬度的整數（如 32 位元 `int`），標準操作為 $O(1)$。
*   **Space:** $O(1)$ auxiliary space.
    **空間：** $O(1)$ 輔助空間。

### When to Use (適用場景)
*   **State Compression:** Packing multiple boolean flags into a single integer.
    **狀態壓縮：** 將多個布林標記打包到單個整數中。
*   **Mathematical Optimization:** Calculating powers of 2, absolute values, or finding unique elements.
    **數學優化：** 計算 2 的次方、絕對值或尋找唯一元素。
*   **Low-level Systems:** Networking protocols, embedded systems, or permission systems.
    **底層系統：** 網路協定、嵌入式系統或權限系統。

### When NOT to Use (不適用場景)
*   **Floating Point Math:** Bitwise ops on floats/doubles are complex and rarely asked in general algo interviews.
    **浮點數運算：** 對浮點數進行位元運算非常複雜，且在一般演算法面試中極少問到。
*   **Readability First:** If business logic requires clarity over micro-optimization, avoid clever bit hacks.
    **可讀性優先：** 如果業務邏輯要求清晰度勝過微優化，請避免使用過於取巧的位元技巧。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Bit Masking (位元遮罩)
Using a "mask" to isolate or modify specific bits.
使用「遮罩」來隔離或修改特定的位元。
*   **Get $k$-th bit:** `(num >> k) & 1`
*   **Set $k$-th bit:** `num | (1 << k)`
*   **Clear $k$-th bit:** `num & ~(1 << k)`

### Pattern 2: XOR Tricks (XOR 技巧)
Utilizing the property $x \oplus x = 0$ and $x \oplus 0 = x$.
利用 $x \oplus x = 0$ 和 $x \oplus 0 = x$ 的特性。
*   **Swap variables:** Swap without temp variable (rare in production, common in trivia).
    **變數交換：** 不使用暫存變數進行交換（生產環境少見，冷知識題常見）。
*   **Find unique:** Eliminate duplicates in an array.
    **尋找唯一值：** 消除陣列中的重複項。

### Pattern 3: LSB Extraction (最低有效位提取)
Isolating the rightmost `1` bit.
隔離最右邊的 `1` 位元。
*   **Formula:** `x & (-x)` (Two's complement magic).
    **公式：** `x & (-x)`（二補數的魔法）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number (LeetCode 136)
**Problem Statement:** Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.
**問題重述：** 給定一個非空的整數陣列 `nums`，除了某個元素只出現一次以外，其餘每個元素均出現兩次。找出那個只出現一次的元素。

### Approach (思路)

1.  **Brute Force (HashMap):**
    *   Count frequency of every number.
    *   **Time:** $O(N)$, **Space:** $O(N)$.
    *   *Critique:* Good, but we can do better on space.
    *   **暴力解（雜湊表）：** 計算每個數字的頻率。**時間：** $O(N)$，**空間：** $O(N)$。*評論：* 不錯，但我們可以在空間上做得更好。

2.  **Optimal (XOR):**
    *   Recall that $A \oplus A = 0$.
    *   If we XOR all numbers together, the pairs will cancel each other out, leaving only the unique number.
    *   **Time:** $O(N)$, **Space:** $O(1)$.
    *   **最佳解（XOR）：** 回想 $A \oplus A = 0$。如果我們將所有數字進行 XOR 運算，成對的數字會互相抵銷，只留下唯一的那個數字。**時間：** $O(N)$，**空間：** $O(1)$。

### Java Reference Solution (Java 參考解)

```java
class Solution {
    /**
     * Finds the single number in an array where every other number appears twice.
     * 尋找陣列中唯一的數字，其中其他數字均出現兩次。
     *
     * @param nums The input array of integers (輸入的整數陣列)
     * @return The single number (唯一的數字)
     */
    public int singleNumber(int[] nums) {
        int result = 0; // 0 XOR x = x, so 0 is the identity element (0 是單位元素)
        
        for (int num : nums) {
            // Apply XOR operation cumulatively
            // 累計應用 XOR 運算
            result ^= num;
        }
        
        return result;
    }
}
```

### Common Mistake (錯誤示範)

```java
// Mistake: Using addition/subtraction to find the unique number
// 錯誤：使用加減法來尋找唯一數字
public int wrongApproach(int[] nums) {
    // This logic fails because we don't know the values beforehand to subtract them correctly.
    // 這種邏輯會失敗，因為我們無法預知數值以便正確地減去它們。
    // It also risks Integer Overflow.
    // 這也有整數溢位（Integer Overflow）的風險。
    int sum = 0;
    for (int n : nums) sum += n; 
    return sum; // Returns total sum, not the unique element. (回傳總和，而非唯一元素)
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Explanation (解釋) |
| :--- | :--- |
| **`>>` vs `>>>`** | `>>` is **Signed** Right Shift (preserves sign bit). `>>>` is **Unsigned** Right Shift (fills with 0). <br> `>>` 是 **有號** 右移（保留符號位）。`>>>` 是 **無號** 右移（補 0）。 |
| **Precedence** | Bitwise operators have lower precedence than equality checks (`==`). Always use `()`. <br> 位元運算子的優先級低於相等檢查（`==`）。請務必使用 `()`。 |
| **Negative Numbers** | Java uses **Two's Complement**. `-x` is equivalent to `~x + 1`. <br> Java 使用 **二補數**。`-x` 等同於 `~x + 1`。 |
| **`&` vs `&&`** | `&` is bitwise AND (processes bits). `&&` is logical AND (short-circuits booleans). <br> `&` 是位元 AND（處理位元）。`&&` 是邏輯 AND（布林短路運算）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify the constraint:** "Since we need $O(1)$ space and the data involves binary states/duplicates, I'm thinking of Bit Manipulation."
    **識別限制：** 「由於我們需要 $O(1)$ 空間，且資料涉及二進位狀態或重複項，我考慮使用位元操作。」
2.  **Explain the operator:** "I will use XOR because it acts as a toggle switch..."
    **解釋運算子：** 「我會使用 XOR，因為它的作用就像一個切換開關……」
3.  **Address the sign:** "Since this is Java, I will be careful with the signed shift operator."
    **處理符號：** 「因為這是 Java，我會小心處理有號位移運算子。」

### Whiteboard Strategy (白板策略)
*   **Truth Tables:** If you get confused, quickly draw a small truth table (e.g., for XOR) in the corner.
    **真值表：** 如果你感到困惑，在角落快速畫一個小的真值表（例如 XOR）。
*   **Binary Representation:** Write out the number 5 as `...00101` to visualize shifts.
    **二進位表示：** 將數字 5 寫成 `...00101` 以視覺化位移過程。

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單)
**Problem:** **Number of 1 Bits (Hamming Weight)**
**Hint:** Use `n & (n-1)` to drop the lowest set bit repeatedly until `n` becomes 0.
**提示：** 使用 `n & (n-1)` 重複消除最低位的設定位元，直到 `n` 變為 0。

### Level: Medium (中等) - *Beginner friendly context*
**Problem:** **Counting Bits** (Given $n$, return array of 1-bits count for $0$ to $n$)
**Hint:** Use Dynamic Programming with bits. `count[i] = count[i >> 1] + (i & 1)`.
**提示：** 結合動態規劃與位元。`count[i] = count[i >> 1] + (i & 1)`。

### Level: Hard (困難) - *Implementation heavy*
**Problem:** **Reverse Bits** (Reverse bits of a 32-bit unsigned integer)
**Hint:** Iterate 32 times. Extract the last bit of input, shift result left, add the extracted bit. Use `>>>` for input.
**提示：** 迭代 32 次。提取輸入的最後一位，將結果左移，加上提取的位元。輸入使用 `>>>`。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Parentheses:** Did I wrap my bitwise operations in `()`? (e.g., `(a & b) == 0`)
    **括號：** 我是否將位元運算用 `()` 包起來了？（例如 `(a & b) == 0`）
*   [ ] **Shift Type:** Did I use `>>>` when dealing with unsigned logic in Java?
    **位移類型：** 在 Java 處理無號邏輯時，我是否使用了 `>>>`？
*   [ ] **Base Case:** Does it work for `0`, `-1`, or `Integer.MAX_VALUE`?
    **基本情況：** 這對 `0`、`-1` 或 `Integer.MAX_VALUE` 有效嗎？
*   [ ] **Complexity:** Is this strictly $O(1)$ space? (Not creating strings/arrays).
    **複雜度：** 這是否嚴格為 $O(1)$ 空間？（沒有建立字串/陣列）。

---

## 9. Memory Anchors (記憶錨點)

*   **XOR (`^`) is a "Difference Detector":**
    *   0 if same, 1 if different. Also "Addition without carry".
    *   **XOR (`^`) 是「差異偵測器」：** 相同為 0，不同為 1。也是「不進位加法」。
*   **AND (`&`) is a "Filter/Mask":**
    *   It only lets bits pass through where the mask is 1.
    *   **AND (`&`) 是「過濾器/遮罩」：** 它只允許遮罩為 1 的位置的位元通過。
*   **Right Shift (`>>` vs `>>>`):**
    *   `>>` is "Sticky" (drags the sign bit along).
    *   `>>>` is "Clean" (fills with fresh zeros).
    *   **右移（`>>` vs `>>>`）：** `>>` 是「黏的」（會拖著符號位走）。`>>>` 是「乾淨的」（填入新鮮的 0）。