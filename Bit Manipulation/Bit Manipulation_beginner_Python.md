Here is the comprehensive interview preparation guide for **Bit Manipulation**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level as requested.

這是一份針對 **位元運算（Bit Manipulation）** 的完整面試準備教材，專為資深軟體工程師設計，並根據要求調整為 **初階（Beginner）** 深度。

---

# Bit Manipulation: The Foundation (Beginner Level)
# 位元運算：基礎篇

## 1. Learning Objectives (學習目標)

1.  **Master Logical Operators & Truth Tables:** Understand `&`, `|`, `^`, `~` and their specific applications in extracting or modifying data.
    **掌握邏輯運算子與真值表：** 理解 `&`、`|`、`^`、`~` 及其在提取或修改資料中的具體應用。
2.  **Understand Bitwise Shifting:** Learn how left shift (`<<`) and right shift (`>>`) correspond to multiplication and division by powers of 2.
    **理解位元位移：** 學習左移（`<<`）與右移（`>>`）如何對應到乘以或除以 2 的冪次。
3.  **Utilize XOR Properties:** Grasp the "cancellation" property of XOR to solve unique element problems efficiently.
    **運用 XOR 特性：** 掌握 XOR 的「抵銷」特性，以高效解決唯一元素問題。
4.  **Handle Python-Specific Integer Behaviors:** Recognize how Python handles arbitrary-precision integers and how to simulate fixed-width (32-bit) integers.
    **處理 Python 特有的整數行為：** 認識 Python 如何處理任意精度整數，以及如何模擬固定寬度（32 位元）整數。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Bit manipulation involves applying logical operations on individual bits of integers to perform calculations at the hardware level.
位元運算涉及對整數的個別位元應用邏輯運算，以便在硬體層級執行計算。

### Intuition (直覺)
Think of an integer not as a number, but as an array of boolean flags (switches) packed into a single variable.
不要將整數視為數字，而應將其視為壓縮在單一變數中的布林標記（開關）陣列。

### Complexity (複雜度)
*   **Time:** $O(1)$ for standard operations on fixed-width integers (e.g., 32-bit or 64-bit).
    **時間：** 對於固定寬度整數（如 32 位元或 64 位元）的標準運算為 $O(1)$。
*   **Space:** $O(1)$ auxiliary space is usually sufficient.
    **空間：** 通常僅需 $O(1)$ 的輔助空間。

### When to Use (適用場景)
*   **Low-level Optimization:** Counting bits, reversing bits, or packing data.
    **底層優化：** 計算位元數、反轉位元或壓縮資料。
*   **Mathematical Tricks:** Checking for even/odd, powers of 2, or swapping numbers without temp variables.
    **數學技巧：** 檢查奇偶數、2 的冪次，或在不使用臨時變數的情況下交換數字。
*   **Set Operations:** Representing small sets of elements efficiently.
    **集合運算：** 高效地表示小型元素集合。

### When NOT to Use (不適用場景)
*   **Floating Point Math:** Bitwise operators generally do not apply to floats directly in high-level logic.
    **浮點數運算：** 位元運算子通常不直接應用於高層邏輯中的浮點數。
*   **Complex Business Logic:** Overusing bitwise hacks can reduce code readability significantly.
    **複雜商業邏輯：** 過度使用位元技巧會顯著降低程式碼的可讀性。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner level, we focus on the fundamental patterns that appear in 80% of easy/medium interview questions.
針對初階程度，我們專注於 80% 的簡單/中等面試題中出現的基礎模式。

### A. Masking (遮罩)
Using a specific bit pattern (mask) to clear, set, or query specific bits.
使用特定的位元模式（遮罩）來清除、設定或查詢特定位元。
*   `x & (1 << k)`: Check if the $k$-th bit is set. (檢查第 $k$ 個位元是否為 1)
*   `x | (1 << k)`: Set the $k$-th bit to 1. (將第 $k$ 個位元設為 1)

### B. XOR Cancellation (XOR 抵銷)
The property $A \oplus A = 0$ and $A \oplus 0 = A$ allows us to eliminate duplicate numbers.
利用 $A \oplus A = 0$ 與 $A \oplus 0 = A$ 的特性，讓我們能夠消除重複的數字。

### C. Brian Kernighan’s Algorithm
A trick to turn off the rightmost set bit.
一個用來關閉最右邊為 1 的位元的技巧。
*   `x & (x - 1)`: Removes the lowest set bit. (移除最低位的 1)

---

## 4. Example Walkthrough (範例講解)

### Problem: Single Number (只出現一次的數字)
**Difficulty:** Easy | **Pattern:** XOR Cancellation

#### Problem Statement (問題重述)
Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.
給定一個非空的整數陣列 `nums`，除了某個元素只出現一次以外，其餘每個元素均出現兩次。找出那個只出現一次的元素。

#### Approach 1: Brute Force / Hash Map (暴力法 / 雜湊表)
*   **Idea:** Use a dictionary to count frequencies.
    **思路：** 使用字典來計算頻率。
*   **Complexity:** Time $O(N)$, Space $O(N)$.
    **複雜度：** 時間 $O(N)$，空間 $O(N)$。
*   **Critique:** Good, but the problem often asks for $O(1)$ space.
    **評論：** 不錯，但題目常要求 $O(1)$ 空間。

#### Approach 2: Sorting (排序)
*   **Idea:** Sort the array and check neighbors.
    **思路：** 將陣列排序並檢查相鄰元素。
*   **Complexity:** Time $O(N \log N)$, Space $O(1)$ (depending on sort).
    **複雜度：** 時間 $O(N \log N)$，空間 $O(1)$（取決於排序演算法）。

#### Approach 3: Bitwise XOR (最佳解：位元 XOR)
*   **Idea:** Since $A \oplus A = 0$, XORing all numbers together will cancel out the pairs, leaving only the unique number.
    **思路：** 由於 $A \oplus A = 0$，將所有數字進行 XOR 運算會抵銷成對的數字，僅留下唯一的那個數字。
*   **Complexity:** Time $O(N)$, Space $O(1)$.
    **複雜度：** 時間 $O(N)$，空間 $O(1)$。

#### Python Reference Solution (Python 參考解)

```python
from typing import List

def singleNumber(nums: List[int]) -> int:
    """
    Finds the single number in an array where every other number appears twice.
    找出陣列中只出現一次的數字，其餘數字皆出現兩次。
    """
    result = 0
    
    # Iterate through each number in the list
    # 遍歷列表中的每一個數字
    for num in nums:
        # Apply XOR operation.
        # Logic: 
        # 1. a ^ 0 = a
        # 2. a ^ a = 0
        # 3. a ^ b ^ a = (a ^ a) ^ b = 0 ^ b = b
        # 應用 XOR 運算。
        # 邏輯：
        # 1. a ^ 0 = a
        # 2. a ^ a = 0
        # 3. a ^ b ^ a = (a ^ a) ^ b = 0 ^ b = b
        result ^= num
        
    return result

# Test Case
# print(singleNumber([4, 1, 2, 1, 2])) # Output: 4
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Operator Precedence**<br>(運算子優先級) | `a & 1 == 0` is interpreted as `a & (1 == 0)` because `==` has higher precedence than `&`. **Always use parentheses:** `(a & 1) == 0`.<br>`a & 1 == 0` 會被解釋為 `a & (1 == 0)`，因為 `==` 的優先級高於 `&`。**務必使用括號：** `(a & 1) == 0`。 |
| **Signed vs. Unsigned**<br>(有號與無號) | Python integers have arbitrary precision (infinite bits). `-1` is `...1111`. To simulate 32-bit unsigned behavior, use `n & 0xFFFFFFFF`.<br>Python 的整數具有任意精度（無限位元）。`-1` 是 `...1111`。若要模擬 32 位元無號行為，請使用 `n & 0xFFFFFFFF`。 |
| **Right Shift Types**<br>(右移類型) | Python only has `>>` (arithmetic shift, preserves sign). It does not have `>>>` (logical shift). For logical shift, mask after shifting or convert to positive first.<br>Python 只有 `>>`（算術位移，保留符號）。沒有 `>>>`（邏輯位移）。若需邏輯位移，需在位移後使用遮罩或先轉為正數。 |
| **Negation**<br>(取反) | `~x` is not just flipping bits in Python due to infinite precision; it equals `-x - 1`.<br>在 Python 中，由於無限精度，`~x` 不僅僅是翻轉位元；它等於 `-x - 1`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify the constraint:** "Since we need $O(1)$ space and the data involves binary states/duplicates, Bit Manipulation is a strong candidate."
    **識別限制：** 「由於我們需要 $O(1)$ 空間，且資料涉及二進位狀態或重複項，位元運算是強力的候選方案。」
2.  **Explain the operator:** "I will use XOR because it acts as a toggle switch that cancels out identical values."
    **解釋運算子：** 「我將使用 XOR，因為它就像一個切換開關，可以抵銷相同的值。」

### Whiteboard Strategy (白板策略)
*   **Write examples in Binary:** Don't just write `5 & 3`. Write:
    **用二進位寫出範例：** 不要只寫 `5 & 3`。寫出：
    ```text
      0101 (5)
    & 0011 (3)
    -------
      0001 (1)
    ```
    This visualizes your thought process clearly.
    這能清晰地視覺化你的思考過程。

### Common Follow-ups (常見追問)
*   **Q:** "How does this work with negative numbers?"
    **問：** 「這對負數如何運作？」
    *   **A:** Mention Two's Complement representation.
    *   **答：** 提及二補數表示法。
*   **Q:** "What if the input array is very large?"
    **問：** 「如果輸入陣列非常大怎麼辦？」
    *   **A:** Bitwise operations are extremely fast on CPU, but we must ensure we don't overflow if we are accumulating values (though Python handles this automatically).
    *   **答：** 位元運算在 CPU 上極快，但若我們在累加數值，必須確保不會溢位（雖然 Python 會自動處理）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Number of 1 Bits (Hamming Weight)
**Problem:** Write a function that takes an unsigned integer and returns the number of '1' bits it has.
**問題：** 寫一個函式，接收一個無號整數並回傳其含有 '1' 位元的數量。
*   **Hint:** Use `n & (n - 1)` loop or check last bit `n & 1` with shifting.
*   **提示：** 使用 `n & (n - 1)` 迴圈，或配合位移檢查最後一位 `n & 1`。

### 2. Medium (Beginner-High): Reverse Bits
**Problem:** Reverse bits of a given 32-bit unsigned integer.
**問題：** 反轉給定 32 位元無號整數的位元。
*   **Hint:** Iterate 32 times. Extract the last bit of input (`n & 1`) and push it to the output (`res = res << 1 | bit`).
*   **提示：** 迭代 32 次。提取輸入的最後一位（`n & 1`），並將其推入輸出（`res = res << 1 | bit`）。

### 3. Medium (Conceptual): Missing Number
**Problem:** Given an array containing `n` distinct numbers taken from `0, 1, 2, ..., n`, find the one that is missing.
**問題：** 給定一個包含 `n` 個相異數字的陣列，數字取自 `0, 1, 2, ..., n`，找出缺失的那個數字。
*   **Hint:** XOR all indices `0..n` and XOR all array values. The result is the missing number (similar to Single Number).
*   **提示：** 將 `0..n` 的所有索引與陣列中的所有數值進行 XOR。結果即為缺失的數字（類似於「只出現一次的數字」）。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] Did I use parentheses around bitwise operators in conditions? (e.g., `(x & 1) == 0`)
  在條件句中，我是否在位元運算子周圍使用了括號？
- [ ] Did I consider the integer width (32-bit vs Python arbitrary)?
  我是否考慮了整數寬度（32 位元 vs Python 任意精度）？
- [ ] Is my solution $O(1)$ space? (The main selling point of bit manipulation).
  我的解法是 $O(1)$ 空間嗎？（這是位元運算的主要賣點）。

### Complexity Check (複雜度確認)
- [ ] Standard bitwise ops: $O(1)$.
  標準位元運算：$O(1)$。
- [ ] Iterating over bits: $O(W)$ where $W$ is number of bits (often treated as $O(1)$ for fixed types).
  遍歷位元：$O(W)$，其中 $W$ 是位元數（對於固定類型通常視為 $O(1)$）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Light Switch Panel (開關面板)
*   **Integer:** A row of 32 light switches.
    **整數：** 一排 32 個電燈開關。
*   **`&` (AND):** Both switches must be ON for the light to stay ON.
    **`&` (AND)：** 兩個開關都必須開啟，燈才會亮。
*   **`|` (OR):** If either switch is ON, the light is ON.
    **`|` (OR)：** 只要任一開關開啟，燈就會亮。
*   **`^` (XOR):** "The Odd One Out Detector". Light is ON only if switches are different.
    **`^` (XOR)：** 「異類偵測器」。只有當開關狀態不同時，燈才會亮。

### The Mask (遮罩)
*   Imagine a stencil (mask) you put over a drawing. You only paint (modify/read) the parts where the stencil has holes (1s).
    想像一張覆蓋在畫上的型板（遮罩）。你只能在型板有孔洞（1）的地方進行繪畫（修改/讀取）。