Here is the comprehensive interview guide for **Math & Geometry**, tailored for a Senior Software Engineer, adjusted to the **Beginner** difficulty level (foundational concepts for this specific topic).

這是一份針對 **Math & Geometry（數學與幾何）** 的完整面試教材，專為資深軟體工程師設計，並依據參數調整為 **Beginner（基礎/入門）** 難度（針對此特定主題的基礎觀念）。

---

# Math & Geometry Interview Guide (Beginner Level)
# 數學與幾何面試指南（基礎級）

## 1. Learning Objectives（學習目標）

1.  **Master Matrix Manipulation:** Understand how to map coordinates and traverse 2D arrays (matrices) efficiently.
    **掌握矩陣操作：** 理解如何高效地映射座標與遍歷二維陣列（矩陣）。
2.  **Handle Integer Constraints:** Learn to manage boundaries, overflows (conceptually), and digit-by-digit manipulation.
    **處理整數限制：** 學習管理邊界、溢位（概念上）以及逐位操作。
3.  **Apply Basic Geometry Logic:** Solve problems involving points, lines, and simple shapes using coordinate arithmetic.
    **應用基礎幾何邏輯：** 使用座標算術解決涉及點、線與簡單形狀的問題。
4.  **Simulate Processes:** Translate mathematical rules directly into code without over-engineering.
    **模擬過程：** 將數學規則直接轉化為程式碼，避免過度設計。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
Math and Geometry problems in interviews usually don't require advanced calculus or linear algebra; they focus on **simulation**, **pattern recognition**, and **coordinate transformation**.
面試中的數學與幾何問題通常不需要高深的微積分或線性代數；它們專注於 **模擬**、**模式識別** 與 **座標轉換**。

### Intuition（直覺）
*   **Matrices:** Think of them as a grid where index `(r, c)` represents `(y, x)` in a Cartesian plane (but with `y` increasing downwards).
    **矩陣：** 將其視為網格，其中索引 `(r, c)` 代表笛卡爾平面中的 `(y, x)`（但 `y` 向下遞增）。
*   **Modulus Operator (`%`):** It is your best friend for cyclic problems (e.g., rotating arrays, time calculation) and extracting digits.
    **取模運算符（`%`）：** 這是處理週期性問題（如旋轉陣列、時間計算）與提取位數的最佳幫手。

### Complexity（複雜度）
*   **Time:** Usually $O(N)$ where $N$ is the total number of elements (or digits).
    **時間：** 通常為 $O(N)$，其中 $N$ 是元素（或位數）的總數。
*   **Space:** Ideally $O(1)$ (in-place) for matrix operations, or $O(N)$ if a new structure is needed.
    **空間：** 矩陣操作理想上為 $O(1)$（原地算法），若需新結構則為 $O(N)$。

### When to Use / Not to Use（適用與不適用場景）
*   **Use when:** The input is a grid, coordinates, or involves number properties (primes, GCD, palindromes).
    **適用於：** 輸入為網格、座標，或涉及數字屬性（質數、最大公因數、回文）時。
*   **Don't use when:** The problem involves complex relationships between entities (use Graphs) or finding optimal paths (use DP/BFS).
    **不適用於：** 問題涉及實體間的複雜關係（使用圖論）或尋找最佳路徑（使用 DP/BFS）時。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Matrix Traversal (Simulation)
**矩陣遍歷（模擬）**
Iterating through a matrix in a specific order (e.g., Spiral Order).
以特定順序迭代矩陣（例如：螺旋順序）。

### B. Coordinate Transformation
**座標轉換**
Mapping a point $(r, c)$ to a new position $(r', c')$ based on rotation or reflection rules.
根據旋轉或反射規則，將點 $(r, c)$ 映射到新位置 $(r', c')$。

### C. Digit Manipulation
**位數操作**
Extracting digits from an integer using `% 10` and `/ 10` (or `// 10` in Python).
使用 `% 10` 和 `/ 10`（Python 中為 `// 10`）從整數中提取位數。

### D. Basic Geometry
**基礎幾何**
Calculating slopes, areas, or checking if points overlap (rectangles/circles).
計算斜率、面積，或檢查點是否重疊（矩形/圓形）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Rotate Image (90 degrees clockwise)
### 問題：旋轉影像（順時針 90 度）

**Problem Statement:**
Given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須 **原地** 旋轉影像。

### Approach 1: Brute Force (Use Extra Space)
**思路 1：暴力法（使用額外空間）**
Create a new matrix and map `matrix[i][j]` to `new_matrix[j][n-1-i]`.
建立一個新矩陣，並將 `matrix[i][j]` 映射到 `new_matrix[j][n-1-i]`。
*   **Critique:** Easy to implement, but uses $O(N^2)$ space, violating the "in-place" requirement.
    **評論：** 易於實作，但使用 $O(N^2)$ 空間，違反「原地」要求。

### Approach 2: Transpose + Reverse (Optimal)
**思路 2：轉置 + 反轉（最佳解）**
Mathematically, a 90-degree rotation is equivalent to transposing the matrix (swap rows and cols) followed by reversing each row.
數學上，90 度旋轉等同於先將矩陣轉置（交換行與列），然後反轉每一列。
1.  **Transpose:** Swap `matrix[i][j]` with `matrix[j][i]`.
    **轉置：** 交換 `matrix[i][j]` 與 `matrix[j][i]`。
2.  **Reflect:** Reverse elements in each row.
    **反射：** 反轉每一列中的元素。

### Complexity Analysis
**複雜度分析**
*   **Time:** $O(N^2)$ (Visit every cell once).
    **時間：** $O(N^2)$（訪問每個單元格一次）。
*   **Space:** $O(1)$ (No extra data structure used).
    **空間：** $O(1)$（未使用額外資料結構）。

### Python Solution (Bilingual Comments)

```python
from typing import List

def rotate(matrix: List[List[int]]) -> None:
    """
    Do not return anything, modify matrix in-place instead.
    不要返回任何東西，請原地修改矩陣。
    """
    n = len(matrix)

    # Step 1: Transpose the matrix (swap rows and columns)
    # 步驟 1：轉置矩陣（交換行與列）
    for i in range(n):
        # Only iterate over the upper triangle to avoid swapping back
        # 僅迭代上三角區域，以避免重複交換
        for j in range(i, n):
            # Swap elements across the main diagonal
            # 交換主對角線兩側的元素
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    # Step 2: Reverse each row
    # 步驟 2：反轉每一列
    for i in range(n):
        # Pythonic way to reverse a list in-place
        # Python 風格的原地反轉列表方法
        matrix[i].reverse()
        
        # Alternatively, using two pointers:
        # 或者，使用雙指針：
        # left, right = 0, n - 1
        # while left < right:
        #     matrix[i][left], matrix[i][right] = matrix[i][right], matrix[i][left]
        #     left += 1
        #     right -= 1

# Example Usage
# 範例用法
grid = [[1,2,3],[4,5,6],[7,8,9]]
rotate(grid)
print(grid) # Output: [[7,4,1],[8,5,2],[9,6,3]]
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction（區別） |
| :--- | :--- | :--- |
| **Matrix `(x, y)`** | **Cartesian `(x, y)`** | In matrices, `row` is usually `y` (vertical) and `col` is `x` (horizontal). Don't mix up `matrix[y][x]` with `point(x, y)`. <br> 在矩陣中，`row` 通常是 `y`（垂直），`col` 是 `x`（水平）。別搞混 `matrix[y][x]` 與 `point(x, y)`。 |
| **`%` (Modulo)** | **`/` (Division)** | Modulo gives the remainder (last digit), Division shifts the number (removes last digit). <br> 取模給出餘數（最後一位），除法移動數字（移除最後一位）。 |
| **In-place** | **Output new array** | Always clarify if the interviewer wants the input modified or a new result returned. <br> 務必確認面試官希望修改輸入還是返回新結果。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Visualization is Key (視覺化是關鍵)
For matrix or geometry problems, **always draw a diagram** on the whiteboard.
對於矩陣或幾何問題，**務必在白板上畫圖**。
*   *Say:* "Let me visualize the 3x3 matrix indices to ensure my rotation logic maps (0,0) to (0,2)."
    *話術：*「讓我視覺化一下 3x3 矩陣的索引，以確保我的旋轉邏輯正確地將 (0,0) 映射到 (0,2)。」

### 2. Handle Edge Cases Early (儘早處理邊界情況)
Math problems often crash on empty inputs or single-element inputs.
數學問題常在空輸入或單一元素輸入時崩潰。
*   *Check:* Empty matrix `[]`, Single row `[[1]]`, Non-square matrix (if applicable).
    *檢查：* 空矩陣 `[]`、單行 `[[1]]`、非方陣（若適用）。

### 3. Complexity Confirmation (複雜度確認)
Since math operations are often $O(1)$ or $O(N)$, explicitly state this to show efficiency.
由於數學操作通常是 $O(1)$ 或 $O(N)$，請明確說明這一點以展示效率。

### 4. Common Follow-up (常見追問)
*   "What if the matrix is rectangular ($M \times N$)?" (Cannot rotate in-place easily).
    「如果矩陣是長方形 ($M \times N$) 怎麼辦？」（很難原地旋轉）。
*   "What if the integer overflows?" (Python handles large integers automatically, but in Java/C++ you need to check boundaries).
    「如果整數溢位怎麼辦？」（Python 自動處理大整數，但在 Java/C++ 中需檢查邊界）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Plus One
**題目：加一**
*   **Problem:** Given a large integer represented as an array of digits, add one to the integer.
    **問題：** 給定一個由數字陣列表示的大整數，將該整數加一。
*   **Hint:** Iterate from the back. Handle the carry (9 -> 0). If all are 9s, prepend 1.
    **提示：** 從後往前迭代。處理進位（9 -> 0）。若全為 9，則在最前面加 1。
*   **Key Concept:** Carry handling (進位處理).

### 2. Medium: Spiral Matrix
**題目：螺旋矩陣**
*   **Problem:** Return all elements of an $m \times n$ matrix in spiral order.
    **問題：** 以螺旋順序返回 $m \times n$ 矩陣的所有元素。
*   **Hint:** Use 4 boundaries: `top`, `bottom`, `left`, `right`. Loop while `top <= bottom` and `left <= right`.
    **提示：** 使用 4 個邊界：`top`、`bottom`、`left`、`right`。當 `top <= bottom` 且 `left <= right` 時循環。
*   **Key Concept:** Simulation / Boundary Management (模擬 / 邊界管理).

### 3. Medium: Set Matrix Zeroes
**題目：矩陣置零**
*   **Problem:** If an element is 0, set its entire row and column to 0. Do it in-place.
    **問題：** 若某元素為 0，將其整列與整行設為 0。請原地執行。
*   **Hint:** Use the first row and first column as markers to store states, instead of using extra space.
    **提示：** 使用第一列與第一行作為標記來儲存狀態，而非使用額外空間。
*   **Key Concept:** Space Optimization (空間優化).

---

## 8. Quick Checklists（快速檢核表）

### Code Review / Debugging
*   [ ] Did I confuse `i` (row) and `j` (col)?
    我是否搞混了 `i`（行）和 `j`（列）？
*   [ ] Did I handle the "carry" correctly in arithmetic problems?
    在算術問題中，我是否正確處理了「進位」？
*   [ ] Are my loops inclusive or exclusive of the end index? (e.g., `range(n)` vs `range(n-1)`)
    我的迴圈是包含還是排除結束索引？
*   [ ] Did I modify the matrix while iterating it (causing dirty reads)?
    我是否在迭代矩陣時修改了它（導致髒讀）？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

### The Onion Analogy (Spiral Matrix)
**洋蔥類比（螺旋矩陣）**
*   **Concept:** Peeling layers.
    **觀念：** 剝洋蔥。
*   **Visual:** Process the outer rectangle (layer), then shrink the boundaries (`top++`, `bottom--`, `left++`, `right--`) to process the inner layer.
    **圖像：** 處理外部矩形（層），然後縮小邊界（`top++`, `bottom--`, `left++`, `right--`）以處理內部層。

### The Transpose-Reflect Trick
**轉置-反射技巧**
*   **Concept:** Rotating a physical photo.
    **觀念：** 旋轉實體照片。
*   **Visual:** Imagine flipping the image over its diagonal (transpose), then looking at it in a mirror (reflect/reverse). That's a 90-degree turn.
    **圖像：** 想像沿對角線翻轉影像（轉置），然後照鏡子（反射/反轉）。這就是 90 度旋轉。