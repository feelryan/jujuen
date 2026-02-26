Here is the advanced training material for Bit Manipulation, tailored for Senior Software Engineers.
這是一份針對資深軟體工程師量身定做的位元操作（Bit Manipulation）進階教材。

---

# Advanced Bit Manipulation for Senior Engineers
# 資深工程師的進階位元操作指南

## 1. Learning Objectives (學習目標)

*   **Master State Compression:** Learn how to map complex system states or subsets into integers for $O(1)$ access and storage (essential for Advanced DP).
    **掌握狀態壓縮：** 學習如何將複雜的系統狀態或子集映射為整數，以實現 $O(1)$ 的存取與儲存（這對進階動態規劃至關重要）。
*   **Internalize XOR Properties:** Go beyond basic swapping; understand XOR as "stateless addition" or "parity checks" for solving frequency and missing element problems.
    **內化 XOR 屬性：** 超越基本的交換變數；理解 XOR 作為「無狀態加法」或「奇偶校驗」來解決頻率與缺失元素問題。
*   **Optimize Space-Time Complexity:** Use bit-level operations to reduce space from $O(N)$ to $O(1)$ or $O(N/32)$, demonstrating deep understanding of memory layout.
    **優化時空複雜度：** 利用位元級操作將空間從 $O(N)$ 降至 $O(1)$ 或 $O(N/32)$，展現對記憶體佈局的深刻理解。
*   **Handle TypeScript Specifics:** Navigate the quirks of JavaScript/TypeScript bitwise operators (32-bit signed integer coercion).
    **處理 TypeScript 特性：** 駕馭 JavaScript/TypeScript 位元運算子的怪癖（32 位元有號整數強制轉換）。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Bit manipulation is the act of algorithmically manipulating bits or other pieces of data shorter than a word.
位元操作是指以演算法操作位元或比字組（word）更短的資料片段。

Intuitively, treat it as **"Parallel Boolean Algebra"**. A single integer represents a vector of 32 (or 64) boolean flags that can be processed simultaneously.
直觀上，將其視為**「平行布林代數」**。一個整數代表一個由 32（或 64）個布林標記組成的向量，可以同時被處理。

### Complexity (複雜度)
*   **Time:** Generally $O(1)$ for standard operations.
    **時間：** 標準操作通常為 $O(1)$。
*   **Space:** $O(1)$ auxiliary space (registers).
    **空間：** $O(1)$ 輔助空間（暫存器）。

### When to Use (適用場景)
*   **State Compression DP:** Representing visited nodes in TSP (Traveling Salesman Problem) or subsets.
    **狀態壓縮 DP：** 表示 TSP（旅行推銷員問題）中的已訪問節點或子集。
*   **Set Operations:** Intersection, union, and negation of small sets.
    **集合操作：** 小集合的交集、聯集與補集。
*   **Heavy Optimization:** Bloom Filters, Bitmaps, or low-level system flags.
    **重度優化：** 布隆過濾器、點陣圖或底層系統標記。

### When NOT to Use (不適用場景)
*   **High Precision Math:** JS/TS numbers are IEEE 754 doubles; bitwise ops truncate to 32-bit ints. Large integers require `BigInt`.
    **高精度數學：** JS/TS 的數字是 IEEE 754 雙精度浮點數；位元運算會截斷為 32 位元整數。大整數需要 `BigInt`。
*   **Readability First:** If logic is complex business rules, bitmasks harm maintainability.
    **可讀性優先：** 如果邏輯是複雜的商業規則，位元遮罩會損害可維護性。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. The "Masking" Pattern (遮罩模式)
Used to select, clear, or toggle specific bits.
用於選擇、清除或切換特定位元。
*   **Set bit $k$:** `num | (1 << k)`
*   **Clear bit $k$:** `num & ~(1 << k)`
*   **Check bit $k$:** `(num >> k) & 1`
*   **Toggle bit $k$:** `num ^ (1 << k)`

### B. The "Lowbit" Technique (最低位元技術)
Extracts the lowest set bit (used in Fenwick Trees).
提取最低位的 1（用於 Fenwick Trees / Binary Indexed Trees）。
*   **Formula:** `x & -x`
*   **Remove lowest bit:** `x & (x - 1)` (Brian Kernighan’s algorithm)

### C. XOR Tricks (XOR 技巧)
Leveraging $A \oplus A = 0$ and $A \oplus 0 = A$.
利用 $A \oplus A = 0$ 和 $A \oplus 0 = A$ 的特性。
*   **Problem Type:** "Find the element that appears once/odd times."
    **問題類型：** 「找出出現一次/奇數次的元素。」

### D. Submask Iteration (子遮罩迭代)
Iterating through all submasks of a mask $m$ efficiently.
高效地迭代遮罩 $m$ 的所有子遮罩。
*   **Pattern:** `for (let s = m; s > 0; s = (s - 1) & m) { ... }`
*   **Complexity:** $O(3^N)$ for iterating all submasks of all masks of length $N$, not $O(4^N)$.
    **複雜度：** 迭代長度為 $N$ 的所有遮罩的所有子遮罩為 $O(3^N)$，而非 $O(4^N)$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Find the Longest Substring Containing Vowels in Even Counts
### 問題：找出母音出現次數皆為偶數的最長子字串

**Source:** LeetCode 1371 (Medium/Hard conceptual)

#### Problem Statement (問題重述)
Given the string `s`, return the size of the longest substring containing each vowel ('a', 'e', 'i', 'o', 'u') an even number of times.
給定字串 `s`，回傳包含每個母音（'a', 'e', 'i', 'o', 'u'）偶數次的最長子字串長度。

#### Approach: From Brute Force to Bitmask Prefix (思路：從暴力法到位元遮罩前綴)

**1. Brute Force (暴力法):**
Check all substrings ($O(N^2)$), count vowels ($O(N)$). Total $O(N^3)$. Too slow.
檢查所有子字串 ($O(N^2)$)，計算母音 ($O(N)$)。總共 $O(N^3)$。太慢。

**2. Optimization Intuition (優化直覺):**
We don't care about the *exact count* of vowels, only the *parity* (odd or even).
我們不在乎母音的**確切數量**，只在乎**奇偶性**（奇數或偶數）。
We can represent the state of 5 vowels using 5 bits: `00000` to `11111`.
我們可以用 5 個位元來表示 5 個母音的狀態：`00000` 到 `11111`。
*   Bit 0: 'a', Bit 1: 'e', etc.
*   0 = Even count, 1 = Odd count.

**3. Prefix XOR Strategy (前綴 XOR 策略):**
If `state[i]` represents the parity mask from index `0` to `i`, and `state[j]` represents `0` to `j` (where $j < i$).
如果 `state[i]` 代表索引 `0` 到 `i` 的奇偶遮罩，而 `state[j]` 代表 `0` 到 `j`（其中 $j < i$）。
If `state[i] == state[j]`, it means the substring between $j+1$ and $i$ has effectively "cancelled out" all parity changes.
如果 `state[i] == state[j]`，這意味著 $j+1$ 到 $i$ 之間的子字串有效地「抵消」了所有的奇偶變化。
Therefore, the substring `s[j+1...i]` has all vowels in even counts.
因此，子字串 `s[j+1...i]` 的所有母音數量皆為偶數。

#### TypeScript Solution (TypeScript 參考解)

```typescript
function findTheLongestSubstring(s: string): number {
    // Map vowels to specific bit positions
    // 將母音映射到特定的位元位置
    const vowelToBit: Record<string, number> = {
        'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4
    };

    // Store the first occurrence index of each state (mask).
    // Initialize with -1 for state 0 (empty prefix has even counts).
    // 儲存每個狀態（遮罩）首次出現的索引。
    // 初始化狀態 0 為 -1（空前綴具有偶數計數）。
    const stateFirstIndex = new Map<number, number>();
    stateFirstIndex.set(0, -1);

    let currentMask = 0;
    let maxLength = 0;

    for (let i = 0; i < s.length; i++) {
        const char = s[i];

        // If char is a vowel, toggle its corresponding bit using XOR
        // 如果字元是母音，使用 XOR 切換其對應的位元
        if (vowelToBit[char] !== undefined) {
            const bit = vowelToBit[char];
            // XOR toggles: 0->1, 1->0
            // XOR 切換：0變1，1變0
            currentMask ^= (1 << bit);
        }

        // If we have seen this state before, the substring between the
        // previous occurrence and now has net zero parity change.
        // 如果我們之前見過這個狀態，則前次出現與現在之間的子字串
        // 淨奇偶變化為零。
        if (stateFirstIndex.has(currentMask)) {
            // Calculate length
            // 計算長度
            const prevIndex = stateFirstIndex.get(currentMask)!;
            maxLength = Math.max(maxLength, i - prevIndex);
        } else {
            // Record the first time we see this state
            // 記錄我們第一次見到此狀態的時間
            stateFirstIndex.set(currentMask, i);
        }
    }

    return maxLength;
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. We traverse the string once. Map operations are $O(1)$ on average.
    **時間：** $O(N)$。我們遍歷字串一次。Map 操作平均為 $O(1)$。
*   **Space:** $O(1)$. The mask has only $2^5 = 32$ possible states. The map size is constant.
    **空間：** $O(1)$。遮罩只有 $2^5 = 32$ 種可能的狀態。Map 的大小是常數。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Pitfall / Nuance (陷阱/細節) |
| :--- | :--- |
| **Operator Precedence** | `a & b == c` is parsed as `a & (b == c)`. **Always wrap bitwise ops in parentheses:** `(a & b) == c`.<br> `a & b == c` 會被解析為 `a & (b == c)`。**務必將位元運算用括號包起來：** `(a & b) == c`。 |
| **JS/TS Integers** | Numbers are 64-bit floats. Bitwise ops truncate them to **32-bit signed integers**. `1 << 31` becomes negative.<br> 數字是 64 位元浮點數。位元運算會將其截斷為 **32 位元有號整數**。`1 << 31` 會變成負數。 |
| **Right Shift** | `>>` is arithmetic (preserves sign). `>>>` is logical (zero-fill). For bitmasks, usually prefer `>>>` to avoid sign extension issues.<br> `>>` 是算術位移（保留符號）。`>>>` 是邏輯位移（補零）。對於位元遮罩，通常偏好 `>>>` 以避免符號擴充問題。 |
| **Negation** | `!x` is boolean (true/false). `~x` is bitwise NOT (inverts bits). Don't mix them.<br> `!x` 是布林運算。`~x` 是位元反相。不要混用。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Identify the State:** "Since $N$ is small ($N \le 20$) or we deal with binary states (on/off), I can optimize space using a bitmask."
    **識別狀態：** 「由於 $N$ 很小（$N \le 20$）或者我們處理的是二元狀態（開/關），我可以使用位元遮罩來優化空間。」
2.  **Explain the Mapping:** "I will map each element to a bit index. Intersection becomes AND, Union becomes OR."
    **解釋映射：** 「我會將每個元素映射到一個位元索引。交集變為 AND，聯集變為 OR。」
3.  **Address JS Limitations:** "I'm aware JS bitwise operators work on 32-bit ints. If inputs exceed this, I'd use `BigInt` or an array of numbers."
    **處理 JS 限制：** 「我知道 JS 位元運算子作用於 32 位元整數。如果輸入超過此範圍，我會使用 `BigInt` 或數字陣列。」

### Whiteboard Strategy (白板策略)
*   Define helper functions for readability: `setBit(mask, i)`, `hasBit(mask, i)`. It shows you care about clean code even with low-level ops.
    定義輔助函式以增加可讀性：`setBit(mask, i)`，`hasBit(mask, i)`。這顯示即使在處理底層操作時，你也在乎程式碼的整潔。
*   Use binary literals for constants if clear: `const MASK = 0b1111;` (ES6 feature).
    如果清晰的話，使用二進位字面常數：`const MASK = 0b1111;`（ES6 特性）。

---

## 7. Practice Problems (練習題)

### Easy: Number of 1 Bits (Hamming Weight)
**Hint:** Use `n & (n - 1)` loop to count.
**提示：** 使用 `n & (n - 1)` 迴圈來計數。

### Medium: Single Number III (Two numbers appear once)
**Hint:** XOR all numbers to get `x ^ y`. Find the rightmost set bit of the result to distinguish `x` and `y`. Split array into two groups based on that bit.
**提示：** XOR 所有數字得到 `x ^ y`。找出結果中最右邊的 1 來區分 `x` 和 `y`。根據該位元將陣列分為兩組。

### Hard: Smallest Sufficient Team (LeetCode 1125)
**Problem:** Select minimum people to cover all required skills.
**問題：** 選擇最少的人員以涵蓋所有所需技能。
**Hint:** DP with Bitmask. `dp[mask]` = minimum team for skill set `mask`. Transitions involve `new_mask = old_mask | person_skills`.
**提示：** 位元遮罩 DP。`dp[mask]` = 技能集合 `mask` 所需的最小團隊。轉移方程式涉及 `new_mask = old_mask | person_skills`。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Parentheses Check:** Did I wrap `&`, `|`, `^` operations in `()` when comparing?
    **括號檢查：** 在比較時，我是否將 `&`, `|`, `^` 操作用 `()` 包起來了？
*   [ ] **Sign Check:** Am I using `>>>` for unsigned shifting if dealing with raw bits?
    **符號檢查：** 如果處理原始位元，我是否使用了 `>>>` 進行無號位移？
*   [ ] **Range Check:** Is the bit index $< 31$? If $\ge 32$, standard `number` won't work.
    **範圍檢查：** 位元索引是否 $< 31$？如果 $\ge 32$，標準 `number` 無法運作。
*   [ ] **Base Case:** Did I handle the `0` mask correctly (e.g., empty set)?
    **基本情況：** 我是否正確處理了 `0` 遮罩（例如空集合）？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Light Switch Panel (開關面板):**
    Think of an integer as a row of 32 light switches.
    *   `&` is checking if **both** switches are up.
    *   `|` is turning switches **on** (if not already).
    *   `^` is **toggling** the switch.
    將整數想像成一排 32 個電燈開關。
    *   `&` 是檢查是否**兩個**開關都向上。
    *   `|` 是將開關**打開**（如果尚未打開）。
    *   `^` 是**切換**開關。

*   **The Parallel Universe (平行宇宙):**
    Bitwise operations allow you to perform 32 additions or comparisons in parallel universes simultaneously.
    位元運算允許你在平行宇宙中同時執行 32 次加法或比較。

*   **XOR as "The Odd One Out" Detector (XOR 作為「異類」偵測器):**
    Imagine a party where everyone comes in couples (A, A). XOR cancels them out ($A \oplus A = 0$). The person left alone is the result.
    想像一個派對，每個人都成對出現 (A, A)。XOR 會將他們抵消 ($A \oplus A = 0$)。剩下的那個人就是結果。