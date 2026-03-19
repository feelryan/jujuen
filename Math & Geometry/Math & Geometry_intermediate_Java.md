Here is the comprehensive interview preparation guide for **Math & Geometry**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level.

這是一份針對 **數學與幾何（Math & Geometry）** 的完整面試準備指南，專為資深軟體工程師量身打造，聚焦於 **中階（Intermediate）** 難度。

---

# Math & Geometry Interview Guide (Intermediate)
# 數學與幾何面試指南（中階）

## 1. Learning Goals (學習目標)

1.  **Master Matrix Manipulations:** Confidently handle 2D array transformations (rotation, spiral traversal) without off-by-one errors.
    **掌握矩陣操作：** 自信地處理二維陣列變換（旋轉、螺旋遍歷），避免差一錯誤（off-by-one errors）。
2.  **Handle Numerical Edge Cases:** Develop an instinct for Integer overflow, floating-point precision issues, and division by zero.
    **處理數值邊界情況：** 培養對整數溢位、浮點數精度問題以及除以零的直覺。
3.  **Optimize Mathematical Logic:** Move beyond simulation to find mathematical properties (e.g., Euclidean algorithm, properties of powers) to reduce complexity from $O(N)$ to $O(\log N)$ or $O(1)$.
    **優化數學邏輯：** 超越單純模擬，尋找數學性質（如歐幾里得演算法、冪的性質），將複雜度從 $O(N)$ 降低至 $O(\log N)$ 或 $O(1)$。
4.  **Geometry Primitives:** Implement basic geometric checks (point in rectangle, overlapping areas) using coordinate logic.
    **幾何原語：** 使用坐標邏輯實作基本的幾何檢查（點在矩形內、區域重疊）。

---

## 2. Core Concepts (核心觀念速覽)

### Matrix Logic (矩陣邏輯)
*   **Definition:** Operations on a grid where `grid[r][c]` represents a value.
    **定義：** 在網格上的操作，其中 `grid[r][c]` 代表一個數值。
*   **Intuition:** Treat matrices as layers (onions) or apply linear algebra transformations (transpose/reflect).
    **直覺：** 將矩陣視為分層（洋蔥）結構，或應用線性代數變換（轉置/反射）。

### Modular Arithmetic (模運算)
*   **Definition:** Arithmetic for integers, where numbers "wrap around" upon reaching a certain value (the modulus).
    **定義：** 整數的算術運算，當數值達到特定值（模數）時會「繞回」。
*   **Key Property:** `(a + b) % m = ((a % m) + (b % m)) % m`. Crucial for preventing overflow in large calculations.
    **關鍵性質：** `(a + b) % m = ((a % m) + (b % m)) % m`。這對於防止大數運算中的溢位至關重要。

### Geometry Basics (幾何基礎)
*   **Distance:** Euclidean ($ \sqrt{(x_1-x_2)^2 + (y_1-y_2)^2} $) vs. Manhattan ($ |x_1-x_2| + |y_1-y_2| $).
    **距離：** 歐幾里得距離 ($ \sqrt{(x_1-x_2)^2 + (y_1-y_2)^2} $) 與 曼哈頓距離 ($ |x_1-x_2| + |y_1-y_2| $)。
*   **Slope:** $ \frac{\Delta y}{\Delta x} $. Watch out for vertical lines ($\Delta x = 0$).
    **斜率：** $ \frac{\Delta y}{\Delta x} $。注意垂直線的情況（$\Delta x = 0$）。

### Complexity (複雜度)
*   **Time:** Often $O(\log N)$ for number theory or $O(R \times C)$ for matrices.
    **時間：** 數論問題通常為 $O(\log N)$，矩陣問題通常為 $O(R \times C)$。
*   **Space:** Aim for $O(1)$ (in-place) whenever possible.
    **空間：** 盡可能追求 $O(1)$（原地操作）。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Simulation (模擬):**
    Simply following the instructions step-by-step (e.g., Spiral Matrix).
    單純一步步遵循指令（例如：螺旋矩陣）。
2.  **Math Tricks (數學技巧):**
    Using XOR for finding duplicates, or Boyer-Moore Voting Algorithm.
    使用 XOR 尋找重複項，或 Boyer-Moore 投票演算法。
3.  **Coordinate Geometry (坐標幾何):**
    Calculating overlap of rectangles or checking if points form a specific shape.
    計算矩形重疊或檢查點是否構成特定形狀。
4.  **Fast Power / Binary Exponentiation (快速冪):**
    Computing $x^n$ in $O(\log n)$ time.
    在 $O(\log n)$ 時間內計算 $x^n$。

---

## 4. Example Walkthrough (範例講解)

### Problem: Rotate Image (LeetCode 48)
### 問題：旋轉影像

**Problem Statement:**
You are given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須 **原地（in-place）** 旋轉影像。

**Approach 1: Brute Force (Allocate New Matrix)**
**思路 1：暴力法（分配新矩陣）**
*   Create a new matrix. Map `matrix[i][j]` to `new_matrix[j][n-1-i]`.
    建立一個新矩陣。將 `matrix[i][j]` 映射到 `new_matrix[j][n-1-i]`。
*   **Drawback:** Uses $O(N^2)$ extra space. Not acceptable for "in-place" requirement.
    **缺點：** 使用 $O(N^2)$ 額外空間。不符合「原地」要求。

**Approach 2: Layer-by-Layer Rotation**
**思路 2：分層旋轉**
*   Rotate the outer ring, then the inner ring. Complex index management.
    旋轉外圈，然後旋轉內圈。索引管理複雜。

**Approach 3: Transpose + Reverse (Optimal)**
**思路 3：轉置 + 反轉（最佳解）**
*   **Step 1:** Transpose the matrix (swap `matrix[i][j]` with `matrix[j][i]`).
    **步驟 1：** 轉置矩陣（交換 `matrix[i][j]` 與 `matrix[j][i]`）。
*   **Step 2:** Reverse each row (swap elements horizontally).
    **步驟 2：** 反轉每一列（水平交換元素）。
*   **Why:** This combination mathematically results in a 90-degree clockwise rotation and is much easier to code bug-free.
    **原因：** 這種組合在數學上等同於順時針旋轉 90 度，且更容易寫出無 bug 的程式碼。

**Complexity:**
*   Time: $O(N^2)$ (Visit every cell).
    時間：$O(N^2)$（訪問每個儲存格）。
*   Space: $O(1)$ (In-place).
    空間：$O(1)$（原地操作）。

**Java Solution (Reference):**

```java
class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;

        // Step 1: Transpose the matrix (swap rows and columns)
        // 步驟 1：轉置矩陣（交換列與行）
        for (int i = 0; i < n; i++) {
            // Start j from i to avoid swapping back and forth (only upper triangle)
            // j 從 i 開始，以避免重複交換（僅處理上三角）
            for (int j = i; j < n; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }

        // Step 2: Reverse each row
        // 步驟 2：反轉每一列
        for (int i = 0; i < n; i++) {
            // Two pointers to swap elements in the row
            // 使用雙指針交換該列中的元素
            int left = 0;
            int right = n - 1;
            while (left < right) {
                int temp = matrix[i][left];
                matrix[i][left] = matrix[i][right];
                matrix[i][right] = temp;
                left++;
                right--;
            }
        }
    }
}
```

**Common Mistake (錯誤示範):**
Trying to map coordinates directly without a temp variable or overwriting data before it's used.
試圖在沒有暫存變數的情況下直接映射坐標，或在數據被使用前就將其覆蓋。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Modulo of Negative Numbers** | In Java, `-5 % 3 = -2`, not `1`. To get positive modulo, use `((a % n) + n) % n`. <br> 在 Java 中，`-5 % 3 = -2`，而非 `1`。若要取得正模數，請使用 `((a % n) + n) % n`。 |
| **Integer Overflow** | Calculating `x * x` or `a + b` might exceed `Integer.MAX_VALUE`. Use `long` or modulo arithmetic. <br> 計算 `x * x` 或 `a + b` 可能會超過 `Integer.MAX_VALUE`。請使用 `long` 或模運算。 |
| **Floating Point Precision** | Never use `==` to compare doubles. Use `Math.abs(a - b) < epsilon`. <br> 永遠不要使用 `==` 來比較雙精度浮點數。請使用 `Math.abs(a - b) < epsilon`。 |
| **Vertical Lines (Slope)** | When calculating slope $\frac{y_2-y_1}{x_2-x_1}$, if $x_2 == x_1$, it throws an error. Handle vertical lines separately. <br> 計算斜率 $\frac{y_2-y_1}{x_2-x_1}$ 時，若 $x_2 == x_1$ 會拋出錯誤。需單獨處理垂直線。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Constraints First (先釐清限制):**
    *   "Can the input numbers be negative?" (Affects modulo/division).
    *   「輸入數值可以是負數嗎？」（影響模運算/除法）。
    *   "What is the range of N?" (Determines if $O(N^2)$ is acceptable).
    *   「N 的範圍是多少？」（決定 $O(N^2)$ 是否可接受）。

2.  **Whiteboard Strategy (白板策略):**
    *   For matrix problems, draw a small $3 \times 3$ grid. Write the indices $(0,0), (0,1)...$ to visualize the transformation.
    *   對於矩陣問題，畫一個小的 $3 \times 3$ 網格。寫下索引 $(0,0), (0,1)...$ 以視覺化變換過程。
    *   For math problems, write down the first few iterations to spot the pattern (e.g., $n=1, n=2, n=3$).
    *   對於數學問題，寫下前幾次迭代以找出規律（例如 $n=1, n=2, n=3$）。

3.  **Common Follow-up (常見追問):**
    *   "How would you handle this if the matrix is too large to fit in memory?" (Answer: Process row by row or load chunks).
    *   「如果矩陣大到無法放入記憶體，你會怎麼處理？」（回答：逐列處理或分塊載入）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Happy Number (快樂數)
*   **Prompt:** Determine if a number is "happy" (sum of squares of digits eventually equals 1).
    **題目：** 判斷一個數字是否為「快樂數」（各位數字平方和最終等於 1）。
*   **Hint:** This is implicitly a cycle detection problem. Use a HashSet or Floyd’s Cycle-Finding Algorithm (Fast/Slow pointers).
    **提示：** 這隱含著循環檢測問題。使用 HashSet 或 Floyd 判圈演算法（快慢指針）。

### 2. Medium: Spiral Matrix (螺旋矩陣)
*   **Prompt:** Return all elements of an $m \times n$ matrix in spiral order.
    **題目：** 以螺旋順序回傳 $m \times n$ 矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`). Loop while `top <= bottom` and `left <= right`. Be careful with the condition check inside the loop to avoid duplicates.
    **提示：** 使用 4 個邊界（`top`, `bottom`, `left`, `right`）。當 `top <= bottom` 且 `left <= right` 時迴圈。注意迴圈內的條件檢查以避免重複。

### 3. Medium/Hard: Pow(x, n)
*   **Prompt:** Implement `pow(x, n)`, which calculates $x$ raised to the power $n$.
    **題目：** 實作 `pow(x, n)`，計算 $x$ 的 $n$ 次方。
*   **Hint:** Don't use a loop ($O(n)$). Use Binary Exponentiation (Recursion) to get $O(\log n)$. Handle negative $n$ and `Integer.MIN_VALUE`.
    **提示：** 不要使用迴圈（$O(n)$）。使用二分冪（遞迴）以達到 $O(\log n)$。處理負數 $n$ 和 `Integer.MIN_VALUE`。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
- [ ] **Overflow:** Did I use `long` for products or sums that might exceed $2^{31}-1$?
    **溢位：** 對於可能超過 $2^{31}-1$ 的乘積或總和，我是否使用了 `long`？
- [ ] **Division by Zero:** Did I check the denominator?
    **除以零：** 我是否檢查了分母？
- [ ] **Boundaries:** In matrix loops, is it `< n` or `<= n`? Did I handle the last element?
    **邊界：** 在矩陣迴圈中，是 `< n` 還是 `<= n`？我是否處理了最後一個元素？
- [ ] **Base Cases:** For recursion (like `pow(x, n)`), did I handle $n=0$?
    **基本情況：** 對於遞迴（如 `pow(x, n)`），我是否處理了 $n=0$？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Matrix Rotation = Transpose + Reflection**
    **矩陣旋轉 = 轉置 + 鏡像反射**
    *   Imagine printing the matrix on transparency paper. Flip it over the diagonal (Transpose), then flip it left-to-right (Reverse).
    *   想像將矩陣印在投影片上。沿對角線翻轉（轉置），然後左右翻轉（反轉）。

*   **Modulo = Clock**
    **模運算 = 時鐘**
    *   Numbers wrap around a circle. 13 o'clock is 1 o'clock ($13 \% 12 = 1$). Negative time goes counter-clockwise.
    *   數字在圓圈上繞行。13 點就是 1 點（$13 \% 12 = 1$）。負時間則是逆時針走。

*   **Binary Exponentiation = Squaring**
    **二分冪 = 平方**
    *   To calculate $2^{10}$, you don't multiply 2 ten times. You calculate $2^5$, then square it.
    *   計算 $2^{10}$ 時，你不需要將 2 乘十次。你計算 $2^5$，然後將其平方。