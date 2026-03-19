Here is the comprehensive interview guide for **Math & Geometry (Beginner Level)**, tailored for a Senior Software Engineer using C++.

這是針對 **數學與幾何（初級）** 的完整面試指南，專為使用 C++ 的資深軟體工程師量身打造。

---

# Math & Geometry Interview Guide (Beginner)
# 數學與幾何面試指南（初級）

## 1. Learning Objectives (學習目標)

*   **Master Basic Number Theory & Modular Arithmetic:** Understand how to handle digits, divisibility, and the modulo operator, especially differences between C++ and Python.
    **掌握基礎數論與模運算：** 理解如何處理位數、整除性與模運算符，特別是 C++ 與 Python 之間的差異。
*   **Handle Integer Overflow & Boundary Conditions:** Learn to detect and prevent overflow before it happens, a critical skill in C++ that Python hides.
    **處理整數溢位與邊界條件：** 學習在溢位發生前進行檢測與預防，這是 C++ 中至關重要但 Python 會隱藏的技能。
*   **Visualize 2D Matrix Manipulations:** Develop spatial intuition for coordinate transformations (rotation, reflection) without using extra space.
    **具象化二維矩陣操作：** 培養在不使用額外空間的情況下進行座標轉換（旋轉、翻轉）的空間直覺。
*   **Implement Simulation Logic:** Translate mathematical rules directly into code accurately, focusing on clean logical flow.
    **實作模擬邏輯：** 將數學規則準確地轉化為程式碼，專注於清晰的邏輯流程。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
*   **Math:** Problems involving integer manipulation, prime numbers, GCD/LCM, and base conversions.
    **數學：** 涉及整數操作、質數、最大公因數/最小公倍數以及進制轉換的問題。
*   **Geometry:** Problems involving coordinates (2D arrays), shapes (rectangles, circles), and spatial relationships (overlap, distance).
    **幾何：** 涉及座標（二維陣列）、形狀（矩形、圓形）以及空間關係（重疊、距離）的問題。

### Intuition & Complexity (直覺與複雜度)
*   **Time Complexity:** Often $O(\log N)$ for number theory (processing digits) or $O(R \times C)$ for matrix grids.
    **時間複雜度：** 數論問題通常為 $O(\log N)$（處理位數），矩陣網格問題通常為 $O(R \times C)$。
*   **Space Complexity:** Ideally $O(1)$ (in-place) unless result storage is required.
    **空間複雜度：** 除非需要儲存結果，否則理想情況下為 $O(1)$（原地操作）。

### When to Use (適用場景)
*   When the problem asks for counting, divisibility, palindromes, or grid transformations.
    **當題目要求計數、整除性、迴文或網格轉換時。**

### When NOT to Use (不適用場景)
*   If the problem involves finding the "shortest path" in a grid (Use BFS) or complex connectivity (Use Union-Find/DFS).
    **如果題目涉及在網格中尋找「最短路徑」（應使用 BFS）或複雜的連通性（應使用 Union-Find/DFS）。**

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Peeling the Onion (Layer-by-Layer) / 剝洋蔥法（層層推進）
*   Used in matrix traversal (e.g., Spiral Matrix). Process the outer boundary, then move inwards.
    **用於矩陣遍歷（例如：螺旋矩陣）。先處理外邊界，然後向內移動。**

### B. Digit Extraction / 位數提取
*   Using `x % 10` to get the last digit and `x / 10` to remove it.
    **使用 `x % 10` 取得最後一位數，並使用 `x / 10` 移除它。**

### C. Coordinate Transformation / 座標轉換
*   Mapping `(r, c)` to a new position based on rotation rules (e.g., 90 degrees clockwise).
    **根據旋轉規則（例如順時針 90 度）將 `(r, c)` 映射到新位置。**

### D. Mathematical Simulation / 數學模擬
*   Implementing manual arithmetic (e.g., column-by-column addition) for large numbers represented as arrays/strings.
    **為以陣列/字串表示的大數實作手算算術（例如：逐列相加）。**

---

## 4. Example Walkthrough (範例講解)

### Problem: Rotate Image (NxN Matrix)
### 問題：旋轉影像（NxN 矩陣）

**Problem Statement:**
Given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
**問題重述：**
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須**原地**旋轉影像。

---

### Approach 1: Brute Force (Using Extra Space)
### 思路 1：暴力解（使用額外空間）

*   **Logic:** Create a new matrix `new_mat`. Map `matrix[i][j]` to `new_mat[j][n-1-i]`.
    **邏輯：** 建立一個新矩陣 `new_mat`。將 `matrix[i][j]` 映射到 `new_mat[j][n-1-i]`。
*   **Drawback:** Space complexity is $O(N^2)$, which violates the "in-place" requirement.
    **缺點：** 空間複雜度為 $O(N^2)$，違反了「原地」的要求。

---

### Approach 2: Optimal (Transpose + Reverse)
### 思路 2：最佳解（轉置 + 反轉）

*   **Observation:** A 90-degree clockwise rotation is mathematically equivalent to transposing the matrix (swapping rows and columns) followed by reversing each row.
    **觀察：** 順時針旋轉 90 度在數學上等同於先將矩陣轉置（交換行與列），然後反轉每一列。
*   **Step 1 (Transpose):** Swap `matrix[i][j]` with `matrix[j][i]`. Note: only iterate where `j > i` to avoid double swapping.
    **步驟 1（轉置）：** 交換 `matrix[i][j]` 與 `matrix[j][i]`。注意：僅在 `j > i` 時迭代，以避免重複交換。
*   **Step 2 (Reflect):** Reverse every row using two pointers or a library function.
    **步驟 2（翻轉）：** 使用雙指針或函式庫函數反轉每一列。

**Complexity / 複雜度:**
*   Time: $O(N^2)$ (Visit every cell twice).
    時間：$O(N^2)$（訪問每個單元格兩次）。
*   Space: $O(1)$ (In-place modifications).
    空間：$O(1)$（原地修改）。

---

### C++ Reference Solution
### C++ 參考解

```cpp
#include <vector>
#include <algorithm> // for std::swap, std::reverse

class Solution {
public:
    void rotate(std::vector<std::vector<int>>& matrix) {
        int n = matrix.size();

        // Step 1: Transpose the matrix (swap rows and cols)
        // 步驟 1：轉置矩陣（交換行與列）
        for (int i = 0; i < n; ++i) {
            // Start j from i + 1 to avoid swapping back and touching diagonal
            // j 從 i + 1 開始，以避免換回原值並觸碰對角線
            for (int j = i + 1; j < n; ++j) {
                std::swap(matrix[i][j], matrix[j][i]);
            }
        }

        // Step 2: Reverse each row
        // 步驟 2：反轉每一列
        for (int i = 0; i < n; ++i) {
            // Using standard library to reverse the vector representing the row
            // 使用標準函式庫反轉代表該列的向量
            std::reverse(matrix[i].begin(), matrix[i].end());
            
            // Manual implementation for interview demonstration:
            // 面試演示用的手動實作：
            // int left = 0, right = n - 1;
            // while (left < right) {
            //     std::swap(matrix[i][left], matrix[i][right]);
            //     left++;
            //     right--;
            // }
        }
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / 概念 | Pitfall / 陷阱 | Correct Approach / 正確做法 |
| :--- | :--- | :--- |
| **Integer Overflow** (C++) | Calculating `a * b` or `a + b` might exceed `INT_MAX`. <br> 計算 `a * b` 或 `a + b` 可能超過 `INT_MAX`。 | Check before operation: `if (a > INT_MAX - b)` or use `long long`. <br> 運算前檢查：`if (a > INT_MAX - b)` 或使用 `long long`。 |
| **Modulo of Negative Numbers** | In C++, `-5 % 3` is `-2`. In Python, `-5 % 3` is `1`. <br> 在 C++ 中，`-5 % 3` 是 `-2`。在 Python 中，`-5 % 3` 是 `1`。 | To get positive modulo in C++: `((a % n) + n) % n`. <br> 在 C++ 中取得正模數：`((a % n) + n) % n`。 |
| **Matrix Coordinates** | Confusing `(x, y)` (Cartesian) with `[row][col]` (Matrix). <br> 混淆 `(x, y)`（笛卡兒座標）與 `[row][col]`（矩陣座標）。 | Always use `r` (row) and `c` (col). Remember `y` usually maps to `row`, `x` to `col`. <br> 始終使用 `r`（列）和 `c`（行）。記住 `y` 通常對應 `row`，`x` 對應 `col`。 |
| **Floating Point Equality** | Checking `a == b` for floats/doubles. <br> 對浮點數/雙精度數使用 `a == b` 檢查。 | Use epsilon: `abs(a - b) < 1e-9`. <br> 使用 epsilon：`abs(a - b) < 1e-9`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Clarify Inputs:** "Are the numbers always positive? Does the matrix fit in memory?"
    **釐清輸入：** 「數字總是正數嗎？矩陣是否能放入記憶體？」
2.  **Propose Simulation:** "I will simulate the process manually first to identify the pattern."
    **提出模擬：** 「我會先手動模擬這個過程來找出規律。」
3.  **Address Overflow:** "Since I'm using C++, I will be careful about integer overflow during intermediate calculations."
    **處理溢位：** 「因為我使用 C++，我會小心中間計算過程中的整數溢位。」

### Whiteboard Strategy (白板策略)
*   **Draw the Grid:** For matrix problems, draw a $3 \times 3$ or $4 \times 4$ grid. Don't just imagine it.
    **畫出網格：** 對於矩陣問題，畫出一個 $3 \times 3$ 或 $4 \times 4$ 的網格。不要只憑空想像。
*   **Trace Indices:** Write down the indices $(0,0) \to (0,2)$ explicitly to verify your rotation logic.
    **追蹤索引：** 明確寫下索引變化 $(0,0) \to (0,2)$ 以驗證你的旋轉邏輯。

### Common Follow-ups (常見追問)
*   "What if the matrix is non-square ($M \times N$)?" (Cannot rotate in-place easily, requires new matrix).
    「如果矩陣不是正方形 ($M \times N$) 怎麼辦？」（無法輕易原地旋轉，需要新矩陣）。
*   "How to handle extremely large integers?" (Use string simulation).
    「如何處理極大的整數？」（使用字串模擬）。

---

## 7. Practice Problems (練習題)

### Easy: Plus One
### 易：加一
*   **Prompt:** Given a large integer as an array of digits, add one to the integer.
    **題目：** 給定一個以數字陣列表示的大整數，將該整數加一。
*   **Hint:** Iterate from back. If digit is 9, set to 0 and carry over. If not 9, increment and return. Handle the case `999` $\to$ `1000`.
    **提示：** 從後往前迭代。如果是 9，設為 0 並進位。如果不是 9，加一並返回。處理 `999` $\to$ `1000` 的情況。
*   **Key Concept:** Carry handling (進位處理).

### Medium: Spiral Matrix
### 中：螺旋矩陣
*   **Prompt:** Return all elements of an $m \times n$ matrix in spiral order.
    **題目：** 以螺旋順序返回 $m \times n$ 矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`). Loop while `top <= bottom` and `left <= right`. Update boundaries after traversing each side.
    **提示：** 使用 4 個邊界（`top`, `bottom`, `left`, `right`）。當 `top <= bottom` 且 `left <= right` 時循環。遍歷每一邊後更新邊界。
*   **Key Concept:** Simulation / Boundary shrinking (模擬 / 邊界收縮).

### Medium/Hard: Pow(x, n)
### 中/難：Pow(x, n)
*   **Prompt:** Implement `pow(x, n)`.
    **題目：** 實作 `pow(x, n)`。
*   **Hint:** Don't use a loop (TLE). Use Binary Exponentiation (Recursive or Iterative). $x^{10} = (x^2)^5$. Handle negative `n` and `INT_MIN`.
    **提示：** 不要使用迴圈（會超時）。使用二分冪（遞迴或迭代）。$x^{10} = (x^2)^5$。處理負數 `n` 和 `INT_MIN`。
*   **Key Concept:** Divide and Conquer / Bit manipulation (分治法 / 位元操作).

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Overflow Check:** Did I check for `INT_MAX` / `INT_MIN` when reversing or adding?
    **溢位檢查：** 在反轉或相加時，我是否檢查了 `INT_MAX` / `INT_MIN`？
*   [ ] **Zero/Negative Handling:** Does my code work for 0, -1, or negative inputs?
    **零/負數處理：** 我的程式碼是否適用於 0、-1 或負數輸入？
*   [ ] **Matrix Bounds:** Did I mix up `rows` and `cols` in the loops? (`i < rows`, `j < cols`).
    **矩陣邊界：** 我是否在迴圈中混淆了 `rows` 和 `cols`？（`i < rows`, `j < cols`）。
*   [ ] **Type Casting:** Did I need `long long` for intermediate sums?
    **型別轉換：** 中間總和是否需要 `long long`？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **Rotate Matrix = Transpose + Reflect**
    *   *Image:* Imagine printing the matrix on transparency paper. Flip it over its diagonal (Transpose), then flip it horizontally (Reflect).
    *   **旋轉矩陣 = 轉置 + 翻轉**
    *   *圖像：* 想像將矩陣印在透明投影片上。沿著對角線翻轉（轉置），然後水平翻轉（翻轉）。
*   **Modulo Operator (%)**
    *   *Analogy:* A clock face. 13 o'clock is 1 o'clock because $13 \% 12 = 1$. It wraps around.
    *   **模運算符 (%)**
    *   *類比：* 時鐘面。13 點就是 1 點，因為 $13 \% 12 = 1$。它是循環的。
*   **Spiral Matrix**
    *   *Analogy:* Peeling an onion or a snake coiling inward.
    *   **螺旋矩陣**
    *   *類比：* 剝洋蔥或蛇向內盤繞。