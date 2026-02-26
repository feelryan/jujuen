Here is the comprehensive interview preparation guide for **Math & Geometry**, tailored for a Senior Software Engineer, adjusted to the **Beginner** level (foundational concepts required for senior roles).

這是一份針對 **數學與幾何（Math & Geometry）** 的完整面試準備指南，專為資深軟體工程師設計，並依據 **初階（Beginner）** 設定調整深度（涵蓋資深職位必備的基礎觀念）。

---

# Math & Geometry Interview Guide (Beginner Level)
# 數學與幾何面試指南（初階）

## 1. Learning Objectives (學習目標)

1.  **Master Basic Number Theory & Manipulation:** Understand how to handle digits, overflow, and modular arithmetic without relying solely on libraries.
    **掌握基礎數論與操作：** 理解如何處理位數、溢位與模運算，而不僅僅依賴函式庫。

2.  **Develop Geometric Intuition on Grids:** proficiently manipulate 2D matrices (rotation, traversal) and coordinate geometry (distance, slope).
    **建立網格上的幾何直覺：** 熟練操作二維矩陣（旋轉、遍歷）與座標幾何（距離、斜率）。

3.  **Identify Mathematical Patterns over Simulation:** Learn to recognize when a problem can be solved via a formula ($O(1)$) instead of iterative simulation ($O(N)$).
    **識別數學模式而非單純模擬：** 學習辨識何時可以用公式解（$O(1)$）來替代迭代模擬（$O(N)$）。

4.  **Handle Edge Cases & Precision:** Specifically address floating-point precision issues and integer boundaries in TypeScript/JavaScript.
    **處理邊界情況與精度：** 特別針對 TypeScript/JavaScript 中的浮點數精度問題與整數邊界進行處理。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### A. Modular Arithmetic (模運算)
*   **Definition:** The remainder after division of one number by another.
    **定義：** 一數被另一數除後的餘數。
*   **Intuition:** Thinking in cycles (like a clock).
    **直覺：** 以週期性思考（像時鐘一樣）。
*   **Key for TS:** In JavaScript/TypeScript, `%` is the remainder operator, not the true mathematical modulo for negative numbers.
    **TS 關鍵：** 在 JavaScript/TypeScript 中，`%` 是餘數運算符，對於負數而言並非真正的數學模運算。

### B. Euclidean Distance vs. Manhattan Distance (歐幾里得距離 vs. 曼哈頓距離)
*   **Euclidean:** Straight line distance: $\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$.
    **歐幾里得：** 直線距離：$\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$。
*   **Manhattan:** Grid-based path (L1 norm): $|x_1-x_2| + |y_1-y_2|$.
    **曼哈頓：** 基於網格的路徑（L1 範數）：$|x_1-x_2| + |y_1-y_2|$。
*   **Use Case:** Use Manhattan for grid movement (robots); Euclidean for spatial proximity.
    **適用場景：** 網格移動（機器人）使用曼哈頓距離；空間鄰近性使用歐幾里得距離。

### C. Matrix Manipulation (矩陣操作)
*   **Concept:** Mapping 2D coordinates `(r, c)` to linear indices or transforming them.
    **觀念：** 將二維座標 `(r, c)` 映射到線性索引或進行變換。
*   **Complexity:** Usually $O(R \times C)$ time, $O(1)$ extra space if done in-place.
    **複雜度：** 時間通常為 $O(R \times C)$，若原地操作則額外空間為 $O(1)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### 1. Simulation / Traversal (模擬 / 遍歷)
*   **Description:** Following a specific path logic (e.g., Spiral Matrix).
    **描述：** 遵循特定的路徑邏輯（例如：螺旋矩陣）。
*   **Strategy:** Use boundary variables (`top`, `bottom`, `left`, `right`) to shrink the active area.
    **策略：** 使用邊界變數（`top`, `bottom`, `left`, `right`）來縮小活動區域。

### 2. Math Logic / Digit Extraction (數學邏輯 / 位數提取)
*   **Description:** Problems like "Palindrome Number" or "Reverse Integer".
    **描述：** 諸如「回文數」或「反轉整數」的問題。
*   **Strategy:** Use `x % 10` to get the last digit and `Math.floor(x / 10)` to remove it.
    **策略：** 使用 `x % 10` 取得末位數字，並用 `Math.floor(x / 10)` 移除它。

### 3. Linear Algebra Shortcuts (線性代數捷徑)
*   **Description:** Using Transpose or Reflection to achieve rotation.
    **描述：** 使用轉置或反射來達成旋轉。
*   **Strategy:** Rotate 90° clockwise = Transpose + Reverse each row.
    **策略：** 順時針旋轉 90 度 = 轉置 + 反轉每一列。

---

## 4. Example Walkthrough (範例講解)

### Problem: Rotate Image (矩陣旋轉)
**Problem Statement:** You are given an `n x n` 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
**問題重述：** 給定一個代表圖像的 `n x n` 二維矩陣，將圖像順時針旋轉 90 度。你必須**原地（in-place）**旋轉圖像。

### Approach (思路)

1.  **Brute Force (暴力解):**
    *   Create a new matrix. Map `matrix[i][j]` to `new_matrix[j][n-1-i]`.
    *   建立一個新矩陣。將 `matrix[i][j]` 映射到 `new_matrix[j][n-1-i]`。
    *   *Drawback:* Uses $O(N^2)$ extra space. Not in-place.
    *   *缺點：* 使用 $O(N^2)$ 額外空間。非原地操作。

2.  **Optimal Solution (最佳解 - Linear Algebra):**
    *   Step 1: **Transpose** the matrix (swap `matrix[i][j]` with `matrix[j][i]`).
    *   步驟一：**轉置**矩陣（交換 `matrix[i][j]` 與 `matrix[j][i]`）。
    *   Step 2: **Reflect** (Reverse) each row.
    *   步驟二：**反射**（反轉）每一列。
    *   *Why:* Transposing turns rows into columns. Reversing corrects the order for clockwise rotation.
    *   *原因：* 轉置將列變為行。反轉則修正順序以符合順時針旋轉。

### Complexity (複雜度)
*   **Time:** $O(N^2)$ — We visit each cell twice (once for transpose, once for reverse).
    **時間：** $O(N^2)$ — 我們訪問每個單元格兩次（一次轉置，一次反轉）。
*   **Space:** $O(1)$ — No extra data structures used.
    **空間：** $O(1)$ — 未使用額外資料結構。

### TypeScript Solution (TypeScript 參考解)

```typescript
/**
 * Rotates an n x n 2D matrix by 90 degrees clockwise in-place.
 * 將 n x n 二維矩陣順時針原地旋轉 90 度。
 */
function rotate(matrix: number[][]): void {
    const n = matrix.length;

    // Step 1: Transpose the matrix (swap rows and columns)
    // 步驟一：轉置矩陣（交換行與列）
    for (let i = 0; i < n; i++) {
        // Start j from i to avoid swapping back elements we already swapped
        // j 從 i 開始，以避免將已交換的元素再次換回
        for (let j = i; j < n; j++) {
            const temp = matrix[i][j];
            matrix[i][j] = matrix[j][i];
            matrix[j][i] = temp;
        }
    }

    // Step 2: Reverse each row
    // 步驟二：反轉每一列
    for (let i = 0; i < n; i++) {
        // Two pointers approach to reverse the row array
        // 使用雙指針法反轉列陣列
        let left = 0;
        let right = n - 1;
        while (left < right) {
            const temp = matrix[i][left];
            matrix[i][left] = matrix[i][right];
            matrix[i][right] = temp;
            left++;
            right--;
        }
        // Alternatively in JS/TS: matrix[i].reverse(); 
        // 在 JS/TS 中也可使用：matrix[i].reverse();
    }
}
```

### Common Mistake (錯誤示範)
```typescript
// Wrong: Trying to rotate cell by cell without a temp buffer or correct logic
// 錯誤：試圖在沒有臨時緩衝區或正確邏輯的情況下逐個單元格旋轉
for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
        // This overwrites data before it is used!
        // 這會在使用數據之前覆蓋它！
        matrix[j][n - 1 - i] = matrix[i][j]; 
    }
}
```

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept (觀念) | Pitfall / Nuance (陷阱 / 細微差別) |
| :--- | :--- |
| **Modulo of Negative Numbers**<br>**負數的模運算** | In Python `-5 % 3 == 1`. In TS/JS `-5 % 3 == -2`. <br> **Fix:** `((a % n) + n) % n` to get positive remainder.<br>在 Python 中 `-5 % 3 == 1`。在 TS/JS 中 `-5 % 3 == -2`。<br>**修正：** `((a % n) + n) % n` 以取得正餘數。 |
| **Floating Point Precision**<br>**浮點數精度** | `0.1 + 0.2 === 0.3` is `false`. Avoid exact equality checks for floats.<br>`0.1 + 0.2 === 0.3` 為 `false`。避免對浮點數進行精確相等檢查。 |
| **Integer Division**<br>**整數除法** | TS/JS division `/` results in floats. Use `Math.floor()` or `Math.trunc()`.<br>TS/JS 的除法 `/` 結果為浮點數。請使用 `Math.floor()` 或 `Math.trunc()`。 |
| **Matrix Coordinates**<br>**矩陣座標** | Standard math uses `(x, y)`. Matrices use `(row, col)` which maps to `(y, x)`. Don't mix them up.<br>標準數學使用 `(x, y)`。矩陣使用 `(row, col)` 對應到 `(y, x)`。不要混淆。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Constraints First (先釐清限制條件):**
    *   "Will the input fit in a standard integer?" (Ask about overflow).
    *   「輸入數值是否在標準整數範圍內？」（詢問溢位問題）。
    *   "Can I modify the input matrix?" (Important for space complexity).
    *   「我可以修改輸入矩陣嗎？」（對空間複雜度很重要）。

2.  **Don't Rush to Code (不要急著寫程式):**
    *   For math problems, write out a few examples (n=1, n=2, n=3) to spot the pattern.
    *   對於數學題，寫下幾個範例（n=1, n=2, n=3）來找出規律。
    *   *Say:* "Let me trace the movement of indices to derive the formula."
    *   *口述：* 「讓我追蹤索引的移動來推導公式。」

3.  **Follow-up Preparation (追問準備):**
    *   **Q:** What if the matrix is huge and sparse?
    *   **問：** 如果矩陣巨大且稀疏怎麼辦？
    *   **A:** Switch to a Sparse Matrix representation (Hash Map or List of Lists) storing only non-zero values.
    *   **答：** 轉用稀疏矩陣表示法（雜湊表或列表的列表），僅儲存非零數值。

---

## 7. Practice Problems (練習題)

### Easy: Plus One (加一)
*   **Prompt:** Given a large integer represented as an array of digits, add one to the integer.
    **題目：** 給定一個由數字陣列表示的大整數，將該整數加一。
*   **Hint:** Iterate from the back. Handle the carry (9 -> 0). If the first digit becomes 0, unshift a 1.
    **提示：** 從後往前迭代。處理進位（9 -> 0）。若首位變成 0，則在最前面插入 1。

### Medium: Spiral Matrix (螺旋矩陣)
*   **Prompt:** Return all elements of an `m x n` matrix in spiral order.
    **題目：** 以螺旋順序回傳 `m x n` 矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`). Loop while `top <= bottom` and `left <= right`. Handle the edge case where a row/column is traversed twice inside the loop.
    **提示：** 使用 4 個邊界（`top`, `bottom`, `left`, `right`）。當 `top <= bottom` 且 `left <= right` 時迴圈。處理在迴圈內重複遍歷同一行/列的邊界情況。

### Medium (Harder for Beginners): Set Matrix Zeroes (矩陣置零)
*   **Prompt:** If an element is 0, set its entire row and column to 0. Do it in-place with $O(1)$ space.
    **題目：** 若某元素為 0，將其整列與整行設為 0。需原地操作且空間複雜度為 $O(1)$。
*   **Hint:** Use the first row and first column as "flags" to store the state of the rest of the matrix. Use a separate variable for `matrix[0][0]`.
    **提示：** 使用第一列與第一行作為「標記」，儲存矩陣其餘部分的狀態。使用一個獨立變數來處理 `matrix[0][0]`。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Division:** Did I use `Math.floor()` for integer division?
    **除法：** 我是否使用了 `Math.floor()` 進行整數除法？
*   [ ] **Boundaries:** Did I handle empty inputs (`[]`) or single-element inputs?
    **邊界：** 我是否處理了空輸入（`[]`）或單一元素輸入？
*   [ ] **Loops:** In matrix traversal, did I mix up `rows` (height) and `cols` (width)?
    **迴圈：** 在矩陣遍歷中，我是否混淆了 `rows`（高）與 `cols`（寬）？
*   [ ] **Negative Mod:** Did I handle negative numbers in modulo operations correctly?
    **負數取模：** 我是否正確處理了模運算中的負數？

---

## 9. Memory Anchors (記憶錨點)

*   **Rotation = Transpose + Reverse**
    **旋轉 = 轉置 + 反轉**
    *   *Visual:* Imagine printing a transparency, flipping it over its diagonal (transpose), then flipping it horizontally (reverse).
    *   *圖像：* 想像印出一張投影片，沿對角線翻轉（轉置），然後水平翻轉（反轉）。

*   **Modulo is a Clock**
    **模運算是時鐘**
    *   *Visual:* When you go past 12, you start at 1. When you go back from 1, you go to 12.
    *   *圖像：* 當你超過 12 點，從 1 開始。當你從 1 往回走，會回到 12。

*   **Manhattan vs Euclidean**
    **曼哈頓 vs 歐幾里得**
    *   *Analogy:* Manhattan is a taxi driving in a city (grid blocks). Euclidean is a helicopter flying straight.
    *   *類比：* 曼哈頓是計程車在城市行駛（網格街區）。歐幾里得是直升機直線飛行。