Here is the comprehensive interview guide for **Math & Geometry**, tailored for Senior Software Engineers.
這是一份針對資深軟體工程師量身打造的 **數學與幾何（Math & Geometry）** 面試完整教材。

---

# Math & Geometry Interview Guide (Intermediate)
# 數學與幾何面試指南（中階）

## 1. Learning Objectives（學習目標）

1.  **Master Matrix Manipulation:** confidently handle 2D array transformations (rotation, spiral traversal) without extra space.
    **掌握矩陣操作：** 自信地處理二維陣列變換（旋轉、螺旋遍歷），且不使用額外空間。
2.  **Geometry Primitives:** Understand how to represent coordinates, calculate slopes, and detect overlaps using simple math rather than complex libraries.
    **幾何原語：** 理解如何使用簡單數學而非複雜函式庫來表示座標、計算斜率與偵測重疊。
3.  **Handle Edge Cases & Precision:** Deal with integer overflow, division by zero, and floating-point precision issues common in geometry problems.
    **處理邊界情況與精度：** 處理幾何問題中常見的整數溢位、除以零以及浮點數精度問題。
4.  **Pattern Recognition:** Identify when a problem is a "Math" problem disguised as a simulation or dynamic programming problem.
    **模式識別：** 識別何時一個問題是偽裝成模擬或動態規劃問題的「數學」問題。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
-   **Math (Number Theory):** Focuses on properties of integers (primes, divisors, modulo arithmetic). In interviews, this often tests optimization (e.g., $O(\sqrt{N})$ vs $O(N)$).
    **數學（數論）：** 專注於整數的性質（質數、因數、模運算）。在面試中，這通常測試優化能力（例如 $O(\sqrt{N})$ 對比 $O(N)$）。
-   **Geometry:** Deals with points, lines, and shapes on a Cartesian plane. The key is often reducing geometric relationships to algebraic formulas.
    **幾何：** 處理笛卡兒平面上的點、線與形狀。關鍵通常是將幾何關係簡化為代數公式。
-   **Matrix:** A specific subset of geometry/arrays representing grids. The challenge is usually index management $(r, c)$.
    **矩陣：** 幾何/陣列的一個特定子集，代表網格。挑戰通常在於索引管理 $(r, c)$。

### Complexity（複雜度）
-   **Time:** Usually $O(N)$ or $O(R \times C)$ for matrices. Math problems can be $O(\log N)$ (like Euclidean GCD or Binary Exponentiation).
    **時間：** 矩陣通常為 $O(N)$ 或 $O(R \times C)$。數學問題可達 $O(\log N)$（如歐幾里得 GCD 或快速冪）。
-   **Space:** Ideally $O(1)$ (in-place) for matrix operations; $O(N)$ if storing hash maps for geometry lines.
    **空間：** 矩陣操作理想上為 $O(1)$（原地操作）；若需儲存幾何線條的雜湊表則為 $O(N)$。

### When to Use / Not Use（適用與不適用場景）
-   **Use when:** The problem involves grids, rotations, coordinates, or finding patterns in number sequences.
    **適用於：** 問題涉及網格、旋轉、座標或尋找數列規律時。
-   **Not Use when:** The problem is clearly a graph traversal (BFS/DFS) where the grid is just a representation of nodes (e.g., "Number of Islands").
    **不適用於：** 問題明顯是圖遍歷（BFS/DFS），而網格僅是節點的表示方式時（例如「島嶼數量」）。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Simulation / Traversal (模擬 / 遍歷):**
    -   Moving through a matrix in a specific order (Spiral, Diagonal).
    -   以特定順序移動矩陣（螺旋、對角線）。
2.  **In-place Transformation (原地變換):**
    -   Modifying the matrix without using a copy (Rotate Image, Set Matrix Zeroes).
    -   不使用副本修改矩陣（旋轉影像、矩陣置零）。
3.  **Math Logic & Number Theory (數學邏輯與數論):**
    -   Digit manipulation (Palindrome Number, Reverse Integer).
    -   數字操作（回文數、反轉整數）。
4.  **Geometry & Slope (幾何與斜率):**
    -   Using $y = mx + b$ or vector cross products to determine collinearity.
    -   使用 $y = mx + b$ 或向量外積來判斷共線。

---

## 4. Example Walkthrough（範例講解）

### Example 1: Rotate Image (Matrix)
### 範例一：旋轉影像（矩陣）

#### Problem Statement（問題重述）
You are given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須**原地**旋轉影像。

#### Thought Process（思路）

1.  **Brute Force (Not Allowed):** Create a new matrix `newMat`, map `newMat[j][n-1-i] = matrix[i][j]`. Space is $O(N^2)$.
    **暴力解（不允許）：** 建立新矩陣 `newMat`，映射 `newMat[j][n-1-i] = matrix[i][j]`。空間為 $O(N^2)$。
2.  **Optimization (Layer-by-Layer):** Move elements in groups of 4 (top-left, top-right, bottom-right, bottom-left). Complex to implement correctly under pressure.
    **優化（逐層處理）：** 以 4 個為一組移動元素（左上、右上、右下、左下）。在壓力下難以正確實作。
3.  **Optimal (Linear Algebra Trick):**
    -   Step 1: **Transpose** the matrix (swap `matrix[i][j]` with `matrix[j][i]`).
    -   Step 2: **Reverse** each row.
    -   Result: 90-degree clockwise rotation.
    **最佳解（線性代數技巧）：**
    -   步驟 1：**轉置**矩陣（交換 `matrix[i][j]` 與 `matrix[j][i]`）。
    -   步驟 2：**反轉**每一列。
    -   結果：順時針旋轉 90 度。

#### TypeScript Solution（參考解）

```typescript
/**
 * Rotates an n x n 2D matrix 90 degrees clockwise in-place.
 * 將 n x n 二維矩陣原地順時針旋轉 90 度。
 */
function rotate(matrix: number[][]): void {
    const n = matrix.length;

    // Step 1: Transpose the matrix (swap rows and columns)
    // 步驟 1：轉置矩陣（交換行與列）
    for (let i = 0; i < n; i++) {
        // Start j from i to avoid swapping back (only upper triangle)
        // j 從 i 開始以避免換回（僅處理上三角）
        for (let j = i; j < n; j++) {
            const temp = matrix[i][j];
            matrix[i][j] = matrix[j][i];
            matrix[j][i] = temp;
        }
    }

    // Step 2: Reverse each row
    // 步驟 2：反轉每一列
    for (let i = 0; i < n; i++) {
        // Two pointers to reverse the row array
        // 使用雙指針反轉列陣列
        let left = 0;
        let right = n - 1;
        while (left < right) {
            const temp = matrix[i][left];
            matrix[i][left] = matrix[i][right];
            matrix[i][right] = temp;
            left++;
            right--;
        }
        // Or simply: matrix[i].reverse(); if built-ins are allowed
        // 或者簡單地使用：matrix[i].reverse(); 如果允許使用內建函式
    }
}
```

#### Complexity（複雜度）
-   **Time:** $O(N^2)$ (Visit every cell once).
    **時間：** $O(N^2)$（訪問每個單元格一次）。
-   **Space:** $O(1)$ (In-place).
    **空間：** $O(1)$（原地操作）。

---

### Example 2: Happy Number (Math & Cycle Detection)
### 範例二：快樂數（數學與循環偵測）

#### Problem Statement（問題重述）
Write an algorithm to determine if a number `n` is "happy". A happy number is a number defined by the following process: Starting with any positive integer, replace the number by the sum of the squares of its digits. Repeat until the number equals 1 (happy), or it loops endlessly in a cycle (not happy).
寫一個演算法來判斷數字 `n` 是否為「快樂數」。快樂數定義如下：從任意正整數開始，將該數替換為其各位數字的平方和。重複此過程直到數字變為 1（快樂），或者無限循環（不快樂）。

#### Thought Process（思路）

1.  **Intuition:** This is implicitly a "Linked List" cycle detection problem. The sequence of numbers forms a chain.
    **直覺：** 這隱含著「鏈結串列」的循環偵測問題。數字序列形成一條鏈。
2.  **Detection:** If we reach 1, return true. If we see a number we have seen before, we are in a loop, return false.
    **偵測：** 如果達到 1，回傳 true。如果看到之前出現過的數字，表示進入循環，回傳 false。
3.  **Approaches:**
    -   **HashSet:** Store seen numbers. Easy to implement. Space $O(N)$.
    -   **Floyd's Cycle-Finding (Tortoise and Hare):** Use two pointers (slow/fast) to detect loops with $O(1)$ space.
    **方法：**
    -   **HashSet：** 儲存見過的數字。易於實作。空間 $O(N)$。
    -   **Floyd 判圈法（龜兔賽跑）：** 使用雙指針（快/慢）以 $O(1)$ 空間偵測循環。

#### TypeScript Solution（參考解）

```typescript
/**
 * Calculates the sum of squares of digits.
 * 計算各位數字的平方和。
 */
function getSumOfSquares(num: number): number {
    let sum = 0;
    while (num > 0) {
        const digit = num % 10;
        sum += digit * digit;
        num = Math.floor(num / 10);
    }
    return sum;
}

/**
 * Determines if a number is a Happy Number using Floyd's Cycle-Finding Algorithm.
 * 使用 Floyd 判圈演算法判斷是否為快樂數。
 */
function isHappy(n: number): boolean {
    let slow = n;
    let fast = getSumOfSquares(n);

    // Continue until fast reaches 1 (happy) or fast meets slow (cycle detected)
    // 持續直到 fast 達到 1（快樂）或 fast 遇見 slow（偵測到循環）
    while (fast !== 1 && slow !== fast) {
        slow = getSumOfSquares(slow);           // Move 1 step
        fast = getSumOfSquares(getSumOfSquares(fast)); // Move 2 steps
    }

    return fast === 1;
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Pitfall (錯誤/陷阱) | Correct Approach (正確方法) |
| :--- | :--- | :--- |
| **Matrix Coordinates** | Confusing $(x, y)$ with $(row, col)$. In math, $x$ is horizontal. In matrices, $row$ is vertical. <br> 混淆 $(x, y)$ 與 $(row, col)$。數學中 $x$ 是水平的，矩陣中 $row$ 是垂直的。 | Always use `r` (row) and `c` (col) variables instead of `x` and `y` to avoid ambiguity. <br> 總是使用 `r` 和 `c` 變數代替 `x` 和 `y` 以避免歧義。 |
| **Division by Zero** | Calculating slope `(y2-y1)/(x2-x1)` when `x2 == x1` (vertical line). <br> 當 `x2 == x1`（垂直線）時計算斜率 `(y2-y1)/(x2-x1)`。 | Handle vertical lines separately or use Cross Product form: `(y2-y1)*dx == (x2-x1)*dy`. <br> 分開處理垂直線，或使用外積形式：`(y2-y1)*dx == (x2-x1)*dy`。 |
| **Modulo Arithmetic** | Negative numbers modulo in Python/JS can be tricky (e.g., `-1 % 5`). <br> Python/JS 中負數的模運算可能很棘手（如 `-1 % 5`）。 | Use `((a % n) + n) % n` to ensure positive results. <br> 使用 `((a % n) + n) % n` 確保結果為正。 |
| **Floating Point** | `0.1 + 0.2 === 0.3` is false. <br> `0.1 + 0.2 === 0.3` 是錯的。 | Use an epsilon for comparison: `Math.abs(a - b) < 1e-9`. <br> 使用 epsilon 進行比較：`Math.abs(a - b) < 1e-9`。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarification (釐清需求)
-   **Input Range:** "Can the numbers be negative?" "Will the matrix be empty?"
    **輸入範圍：** 「數字可以是負的嗎？」「矩陣會是空的嗎？」
-   **Space Constraints:** "Is modifying the input allowed?" (Crucial for matrix problems).
    **空間限制：** 「允許修改輸入嗎？」（對矩陣問題至關重要）。

### 2. Whiteboard / Verbal Strategy (白板/口條策略)
-   **Visualize:** Draw the matrix or the geometry. Don't try to visualize indices in your head.
    **視覺化：** 畫出矩陣或幾何圖形。不要試圖在腦中想像索引。
-   **Derive, Don't Memorize:** For math formulas, quickly derive them if possible. E.g., "Let me check the rotation logic with a $2 \times 2$ matrix first."
    **推導而非死記：** 對於數學公式，儘可能快速推導。例如：「讓我先用 $2 \times 2$ 矩陣檢查旋轉邏輯。」

### 3. Follow-up (常見追問)
-   "What if the matrix is too large to fit in memory?" (Answer: Process row by row or chunks).
    「如果矩陣太大無法放入記憶體怎麼辦？」（答：逐列處理或分塊處理）。
-   "Can you do this with $O(1)$ space?" (Usually implies identifying a cycle or in-place swapping).
    「你能用 $O(1)$ 空間做這個嗎？」（通常暗示識別循環或原地交換）。

---

## 7. Practice Problems（練習題）

### Easy: Plus One
**Problem:** Given a large integer represented as an integer array `digits`, increment the large integer by one.
**問題：** 給定一個由整數陣列 `digits` 表示的大整數，將該整數加一。
-   **Hint:** Handle the carry (99 -> 100). Loop from back to front.
-   **提示：** 處理進位（99 -> 100）。從後往前迴圈。

### Medium: Spiral Matrix
**Problem:** Given an $m \times n$ matrix, return all elements of the matrix in spiral order.
**問題：** 給定一個 $m \times n$ 矩陣，依螺旋順序回傳所有元素。
-   **Hint:** Use 4 boundaries: `top`, `bottom`, `left`, `right`. Loop while `top <= bottom` and `left <= right`.
-   **提示：** 使用 4 個邊界：`top`、`bottom`、`left`、`right`。當 `top <= bottom` 且 `left <= right` 時迴圈。

### Medium/Hard: Set Matrix Zeroes
**Problem:** If an element is 0, set its entire row and column to 0. Do it in-place ($O(1)$ space).
**問題：** 如果一個元素為 0，將其整列與整行設為 0。原地執行（$O(1)$ 空間）。
-   **Hint:** Use the first row and first column as "flags" to store the state of the rest of the matrix. Handle the first row/col separately.
-   **提示：** 使用第一列與第一行作為「標記」，儲存矩陣其餘部分的狀態。分開處理第一列/行。

---

## 8. Quick Checklists（快速檢核表）

-   [ ] **Boundaries:** Did I check `r < 0`, `c < 0`, `r >= R`, `c >= C`?
    **邊界：** 我是否檢查了 `r < 0`, `c < 0`, `r >= R`, `c >= C`？
-   [ ] **Empty Input:** What if the array is `[]` or `[[]]`?
    **空輸入：** 如果陣列是 `[]` 或 `[[]]` 怎麼辦？
-   [ ] **Types:** Did I handle floating point precision or integer overflow?
    **型別：** 我是否處理了浮點數精度或整數溢位？
-   [ ] **Copy vs Reference:** Did I accidentally modify the input when I shouldn't have?
    **複製 vs 引用：** 我是否在不該修改輸入時意外修改了它？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

1.  **Rotation = Transpose + Reflect:**
    -   To rotate clockwise: Transpose, then reflect horizontally (swap columns/reverse rows).
    -   **旋轉 = 轉置 + 鏡像：** 順時針旋轉：轉置，然後水平鏡像（交換行/反轉列）。
2.  **Tortoise and Hare (Cycle Detection):**
    -   Think of a race track. If there is a loop, the faster runner will eventually lap the slower runner.
    -   **龜兔賽跑（循環偵測）：** 想像一個賽道。如果有迴圈，跑得快的人終究會倒追上跑得慢的人。
3.  **Matrix Indices:**
    -   **R**ow comes first, like **R**oyal (King). `matrix[r][c]`.
    -   **R**ow（列）先來，就像 **R**oyal（皇室）。`matrix[r][c]`。