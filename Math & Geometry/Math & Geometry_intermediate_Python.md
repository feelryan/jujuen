# Math & Geometry: Intermediate Level Guide
# 數學與幾何：中階指南

## 1. Learning Objectives (學習目標)

1.  **Master Matrix Manipulation & Simulation:**
    精通矩陣操作與模擬：能夠熟練處理二維陣列的旋轉、螺旋遍歷與原地（In-place）變換。
    *Able to skillfully handle 2D array rotation, spiral traversal, and in-place transformations.*

2.  **Handle Geometric Precision & Edge Cases:**
    處理幾何精度與邊界情況：理解浮點數誤差（Floating Point Epsilon），並能妥善處理垂直線（斜率無限大）與重合點。
    *Understand floating point epsilon and properly handle vertical lines (infinite slope) and overlapping points.*

3.  **Optimize Space Complexity via Mathematical Properties:**
    透過數學性質優化空間複雜度：利用轉置（Transpose）或數學規律將 $O(N)$ 空間優化至 $O(1)$。
    *Utilize transposition or mathematical patterns to optimize space from $O(N)$ to $O(1)$.*

4.  **Bridge Math to Code Readability:**
    連結數學與程式可讀性：身為資深工程師，能寫出邏輯清晰而非僅是「能動」的數學邏輯代碼。
    *As a senior engineer, write mathematical logic code that is logically clear, not just "functional".*

---

## 2. Core Concepts (核心觀念速覽)

### Matrix as Coordinate System (矩陣即座標系)
*   **Definition:** In CS, a matrix is usually `matrix[row][col]`, where `row` increases downwards and `col` increases rightwards.
    **定義：** 在電腦科學中，矩陣通常表示為 `matrix[row][col]`，其中 `row` 向下遞增，`col` 向右遞增。
*   **Intuition:** Think of it as a Cartesian coordinate system but with the Y-axis flipped.
    **直覺：** 將其視為 Y 軸翻轉的笛卡爾座標系。

### Euclidean Distance & Slope (歐幾里得距離與斜率)
*   **Distance:** $\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$. In comparisons, use distance squared to avoid `sqrt` and floats.
    **距離：** $\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$。在比較大小時，使用距離平方以避免開根號與浮點數運算。
*   **Slope:** $m = \frac{y_2 - y_1}{x_2 - x_1}$. Watch out for division by zero ($x_2 = x_1$).
    **斜率：** $m = \frac{y_2 - y_1}{x_2 - x_1}$。注意除以零的情況（$x_2 = x_1$）。

### Modulo Arithmetic (模運算)
*   **Concept:** Essential for cyclic problems (e.g., circular array) and preventing overflow.
    **觀念：** 對於循環問題（如環狀陣列）與防止溢位至關重要。
*   **Key Property:** `(a + b) % n = ((a % n) + (b % n)) % n`.
    **關鍵性質：** `(a + b) % n = ((a % n) + (b % n)) % n`。

### Complexity (複雜度)
*   **Time:** Often $O(N)$ or $O(N^2)$ depending on dimensions. Math solutions can sometimes be $O(1)$ or $O(\log N)$ (like GCD).
    **時間：** 視維度而定，通常為 $O(N)$ 或 $O(N^2)$。數學解法有時可達 $O(1)$ 或 $O(\log N)$（如最大公因數）。
*   **Space:** The goal is usually $O(1)$ auxiliary space.
    **空間：** 目標通常是 $O(1)$ 的輔助空間。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Matrix Simulation (矩陣模擬)
*   **Scenario:** Spiral Matrix, Game of Life.
    **場景：** 螺旋矩陣、生命遊戲。
*   **Strategy:** Use boundary variables (`top`, `bottom`, `left`, `right`) and shrink them after processing each row/column.
    **策略：** 使用邊界變數（`top`, `bottom`, `left`, `right`），並在處理完每行/列後內縮邊界。

### B. Linear Algebra Transformations (線性代數變換)
*   **Scenario:** Rotate Image, Set Matrix Zeroes.
    **場景：** 旋轉影像、矩陣置零。
*   **Strategy:** Decompose complex movements into simple operations (e.g., Rotate 90° = Transpose + Reverse Rows).
    **策略：** 將複雜移動分解為簡單操作（例如：旋轉 90° = 轉置 + 反轉列）。

### C. Geometry & Hashing (幾何與雜湊)
*   **Scenario:** Max Points on a Line.
    **場景：** 直線上最多的點。
*   **Strategy:** Use slope (represented as a reduced fraction or GCD) as a hash map key to count collinear points.
    **策略：** 使用斜率（表示為最簡分數或 GCD）作為雜湊表的鍵來計算共線點。

### D. Number Theory Basics (數論基礎)
*   **Scenario:** Power(x, n), GCD/LCM.
    **場景：** 次方運算、最大公因數/最小公倍數。
*   **Strategy:** Binary Exponentiation (Fast Pow) reduces $O(N)$ to $O(\log N)$.
    **策略：** 快速冪運算將 $O(N)$ 降低至 $O(\log N)$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Rotate Image (旋轉影像)
**Problem Statement:**
You are given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須**原地**（In-place）旋轉影像。

---

### Approach 1: Brute Force (Allocate New Matrix)
**思路：暴力法（分配新矩陣）**

Create a new matrix and map `matrix[i][j]` to `new_matrix[j][n-1-i]`.
建立一個新矩陣，將 `matrix[i][j]` 映射到 `new_matrix[j][n-1-i]`。

*   **Pros:** Easy to implement. (優點：實作簡單)
*   **Cons:** Uses $O(N^2)$ space, violating the "in-place" requirement. (缺點：使用 $O(N^2)$ 空間，違反「原地」要求)

---

### Approach 2: Layer-by-Layer Simulation (Optimized Space)
**思路：分層模擬（優化空間）**

Move elements in groups of 4 (top-left, top-right, bottom-right, bottom-left) layer by layer.
分層將元素以 4 個為一組進行移動（左上、右上、右下、左下）。

*   **Pros:** $O(1)$ space. (優點：$O(1)$ 空間)
*   **Cons:** Indexing is messy and error-prone during interviews. (缺點：索引繁瑣，面試時容易出錯)

---

### Approach 3: Linear Algebra (Best Solution)
**思路：線性代數（最佳解）**

A 90-degree clockwise rotation is mathematically equivalent to:
1.  **Transpose** the matrix (swap `[i][j]` with `[j][i]`).
2.  **Reverse** each row (horizontal reflection).
順時針旋轉 90 度在數學上等同於：
1.  **轉置**矩陣（交換 `[i][j]` 與 `[j][i]`）。
2.  **反轉**每一列（水平鏡像）。

*   **Complexity:** Time $O(N^2)$, Space $O(1)$.
    **複雜度：** 時間 $O(N^2)$，空間 $O(1)$。

---

### Python Solution (Best Approach)

```python
from typing import List

class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        不返回任何值，而是原地修改矩陣。
        """
        n = len(matrix)
        
        # Step 1: Transpose the matrix (swap rows and columns)
        # 步驟 1：轉置矩陣（交換行與列）
        for i in range(n):
            # Start j from i to avoid swapping back (process upper triangle only)
            # j 從 i 開始以避免重複交換（僅處理上三角）
            for j in range(i, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        
        # Step 2: Reverse each row
        # 步驟 2：反轉每一列
        for i in range(n):
            # Two pointers to reverse the row
            # 使用雙指針反轉該列
            left, right = 0, n - 1
            while left < right:
                matrix[i][left], matrix[i][right] = matrix[i][right], matrix[i][left]
                left += 1
                right -= 1

# Test Case
# matrix = [[1,2,3],[4,5,6],[7,8,9]]
# After Transpose: [[1,4,7], [2,5,8], [3,6,9]]
# After Reverse:   [[7,4,1], [8,5,2], [9,6,3]] -> Correct 90 deg rotation
```

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A (概念 A) | Concept B (概念 B) | Comparison / Trap (對比 / 陷阱) |
| :--- | :--- | :--- |
| **Float Equality** (`==`) | **Epsilon Comparison** (`abs(a-b) < 1e-9`) | Never use `==` for floats. Always use a small epsilon threshold. <br> 永遠不要對浮點數使用 `==`，請使用微小的 epsilon 閾值。 |
| **Slope** ($y/x$) | **GCD Pair** (`(dy/g, dx/g)`) | Using float for slope loses precision. Store slope as a reduced fraction tuple `(dy, dx)`. <br> 使用浮點數表示斜率會損失精度。應儲存為最簡分數元組 `(dy, dx)`。 |
| **Matrix `(x, y)`** | **Matrix `[row][col]`** | In math, `(x, y)` usually means `(col, row)`. Don't mix them up. <br> 數學上的 `(x, y)` 通常對應 `(col, row)`。切勿混淆。 |
| **Modulo of Negative** | **Python `%` Operator** | In Python, `-1 % 5 == 4`. In C++/Java, it might be `-1`. Know your language behavior. <br> Python 中 `-1 % 5 == 4`。C++/Java 中可能是 `-1`。需了解語言特性。 |

---

## 6. Interview Strategy (面試實戰建議)

### A. Clarification (釐清需求)
*   "Are the inputs integers or floating-point numbers?"
    「輸入是整數還是浮點數？」
*   "Can the matrix be non-square (rectangular)?"
    「矩陣可能是非正方形（長方形）嗎？」
*   "How should we handle infinite slope (vertical lines)?"
    「我們該如何處理無限大斜率（垂直線）？」

### B. Whiteboard Strategy (白板策略)
*   **Draw it out:** For matrix problems, draw a $3 \times 3$ or $4 \times 4$ grid. Don't simulate in your head.
    **畫出來：** 對於矩陣問題，畫出 $3 \times 3$ 或 $4 \times 4$ 的網格。不要在腦中模擬。
*   **Modularize:** For geometry, define helper functions like `get_gcd(a, b)` or `get_slope(p1, p2)` immediately. This shows Seniority.
    **模組化：** 對於幾何題，立即定義輔助函式如 `get_gcd` 或 `get_slope`。這展現資深水準。

### C. Follow-up Preparation (追問準備)
*   **Q:** "What if the matrix is too large to fit in memory?"
    **問：**「如果矩陣大到無法放入記憶體怎麼辦？」
*   **A:** Discuss loading chunks from disk or processing stream-wise if possible.
    **答：** 討論從硬碟分塊讀取或串流處理的可能性。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (暖身)
**Problem:** **Plus One** (LeetCode 66)
*   **Description:** Given a large integer represented as an integer array digits, increment the large integer by one.
    **描述：** 給定一個由整數陣列表示的大整數，將該整數加一。
*   **Hint:** Handle the carry (9 -> 0). If all digits are 9, resize array.
    **提示：** 處理進位（9 -> 0）。如果所有位數都是 9，調整陣列大小。

### Level 2: Medium (核心)
**Problem:** **Spiral Matrix** (LeetCode 54)
*   **Description:** Return all elements of an $m \times n$ matrix in spiral order.
    **描述：** 以螺旋順序返回 $m \times n$ 矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`). Loop `while top <= bottom and left <= right`.
    **提示：** 使用 4 個邊界。迴圈條件為 `while top <= bottom and left <= right`。

### Level 3: Hard (挑戰)
**Problem:** **Max Points on a Line** (LeetCode 149)
*   **Description:** Given an array of points, find the maximum number of points that lie on the same straight line.
    **描述：** 給定一組點，找出位於同一直線上的最大點數。
*   **Hint:** Fix one point $i$, calculate slopes to all other points $j$. Use a Hash Map to count slopes. **Crucial:** Use GCD to store slope as `(dy, dx)` to avoid float precision issues.
    **提示：** 固定一點 $i$，計算到其他所有點 $j$ 的斜率。使用雜湊表計算斜率數量。**關鍵：** 使用 GCD 將斜率存為 `(dy, dx)` 以避免浮點數精度問題。

---

## 8. Quick Checklists (快速檢核表)

### Before Coding (編碼前)
- [ ] Did I clarify if the coordinate system is Cartesian or Matrix-style? (確認是笛卡爾還是矩陣座標系？)
- [ ] Did I consider $N=0$ or $N=1$? (考慮過 $N=0$ 或 $N=1$ 嗎？)
- [ ] Did I ask about Integer Overflow? (詢問過整數溢位嗎？)

### During Coding (編碼中)
- [ ] Are my loop boundaries correct (`< n` vs `<= n`)? (迴圈邊界正確嗎？)
- [ ] Did I handle division by zero for slopes? (處理斜率除以零了嗎？)
- [ ] Am I modifying the matrix while reading from it (causing dirty reads)? (是否在讀取矩陣時同時修改它導致髒讀？)

### Complexity Check (複雜度確認)
- [ ] Is my solution strictly $O(1)$ space if required? (如果要求，解法是否嚴格為 $O(1)$ 空間？)
- [ ] Is my geometry solution $O(N^2)$ or better? (幾何解法是 $O(N^2)$ 或更好嗎？)

---

## 9. Memory Anchors (記憶錨點)

> **"Rotate = Transpose + Reverse"**
> **「旋轉 = 轉置 + 反轉」**
>
> *   Imagine a transparent sheet. Flip it over the diagonal (Transpose), then flip it horizontally (Reverse).
> *   想像一張透明片。沿對角線翻轉（轉置），然後水平翻轉（反轉）。

> **"Slope is a Ratio, not a Float"**
> **「斜率是比率，不是浮點數」**
>
> *   Visualize slope as steps on a staircase: "Rise over Run". Store the step size `(3, 2)`, not `1.5`.
> *   將斜率想像成樓梯的階梯：「垂直升幅除以水平跨度」。儲存步伐大小 `(3, 2)`，而非 `1.5`。