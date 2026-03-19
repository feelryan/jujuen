Here is the comprehensive interview guide for **Math & Geometry**, tailored for a Senior Software Engineer, adjusted to the **Beginner** level (foundational concepts for interviews), using **Java**.

這是一份針對 **Math & Geometry** 的完整面試教材，專為資深軟體工程師量身打造，難度調整為 **Beginner**（面試基礎觀念），並使用 **Java** 撰寫。

---

# Math & Geometry Interview Guide (Beginner Level)
# 數學與幾何面試指南（基礎級）

## 1. Learning Objectives（學習目標）

1.  **Re-awaken Mathematical Intuition for Discrete Problems.**
    重新喚醒處理離散數學問題的直覺。
    *Goal: Handle digit manipulation, modular arithmetic, and basic 2D coordinates without hesitation.*
    目標：毫不猶豫地處理數字操作、模運算與基本二維座標。

2.  **Master Matrix Manipulation and Index Mapping.**
    掌握矩陣操作與索引映射。
    *Goal: confidently implement matrix rotation and traversal (e.g., spiral) using precise loop boundaries.*
    目標：自信地實作矩陣旋轉與遍歷（如螺旋矩陣），並使用精確的迴圈邊界。

3.  **Handle Java-Specific Numeric Pitfalls.**
    處理 Java 特有的數值陷阱。
    *Goal: Prevent Integer Overflow/Underflow and handle Floating Point precision correctly.*
    目標：防止整數溢位/下溢，並正確處理浮點數精確度。

---

## 2. Core Concepts at a Glance（核心觀念速覽）

### Definition & Intuition（定義與直覺）
**Math** in interviews rarely involves Calculus; it focuses on Number Theory (primes, GCD) and Discrete Math.
面試中的 **數學** 很少涉及微積分；它主要集中在數論（質數、最大公因數）與離散數學。

**Geometry** usually implies 2D Cartesian coordinates or Matrix (Grid) manipulation.
**幾何** 通常意味著二維笛卡爾座標或矩陣（網格）操作。

### Complexity（複雜度）
*   **Time:** Often $O(\sqrt{N})$ for primality tests, $O(\log N)$ for Euclidean GCD, or $O(R \times C)$ for matrices.
    **時間：** 質數測試通常為 $O(\sqrt{N})$，歐幾里得 GCD 為 $O(\log N)$，矩陣操作為 $O(R \times C)$。
*   **Space:** Usually $O(1)$ unless recursion stack or output storage is needed.
    **空間：** 除非需要遞迴堆疊或輸出儲存，否則通常為 $O(1)$。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** The input is a number/grid, and the problem asks for counting, existence, or transformation rules.
    **適用於：** 輸入是數字/網格，且問題要求計數、存在性證明或轉換規則時。
*   **Not Use when:** The problem involves complex relationships better modeled by Graphs or Trees.
    **不適用於：** 問題涉及更適合用圖或樹來建模的複雜關係時。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Digit Extraction & Manipulation (數字提取與操作)**
    *   Using `% 10` to get the last digit and `/ 10` to remove it.
    *   使用 `% 10` 取得最後一位數，使用 `/ 10` 移除它。
2.  **Matrix Simulation (矩陣模擬)**
    *   Iterating through a 2D array in non-standard orders (e.g., spiral, diagonal).
    *   以非標準順序（如螺旋、對角線）遍歷二維陣列。
3.  **Basic Number Theory (基礎數論)**
    *   GCD (Greatest Common Divisor), LCM, and Primality testing.
    *   最大公因數 (GCD)、最小公倍數 (LCM) 與質數測試。
4.  **Geometry Basics (幾何基礎)**
    *   Distance formula, slope calculation, and checking for overlap.
    *   距離公式、斜率計算與檢查重疊。

---

## 4. Example Walkthrough（範例講解）

### Problem: Rotate Image (Matrix Rotation)
### 問題：旋轉影像（矩陣旋轉）

**Problem Statement:**
You are given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**.
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須 **原地 (in-place)** 旋轉影像。

---

### Phase 1: Thought Process（思路）

**1. Brute Force (Intuitive but Space Inefficient):**
**暴力法（直覺但空間效率低）：**
Create a new matrix `new_matrix[col][n - 1 - row] = matrix[row][col]`.
建立一個新矩陣 `new_matrix[col][n - 1 - row] = matrix[row][col]`。
*   **Drawback:** Requires $O(N^2)$ extra space.
*   **缺點：** 需要 $O(N^2)$ 的額外空間。

**2. Pattern Recognition (Linear Algebra):**
**模式識別（線性代數）：**
Rotating 90 degrees clockwise is mathematically equivalent to two simpler operations:
順時針旋轉 90 度在數學上等同於兩個較簡單的操作：
1.  **Transpose:** Swap elements across the main diagonal (`matrix[i][j]` $\leftrightarrow$ `matrix[j][i]`).
    **轉置：** 交換主對角線兩側的元素（`matrix[i][j]` $\leftrightarrow$ `matrix[j][i]`）。
2.  **Reflect (Reverse):** Reverse each row horizontally.
    **映射（反轉）：** 水平反轉每一列。

**3. Optimal Solution:**
**最佳解：**
Perform Transpose then Reflect. Both are in-place operations.
執行轉置然後映射。兩者皆為原地操作。

---

### Phase 2: Java Solution with Bilingual Comments
### Java 參考解（雙語註解）

```java
class Solution {
    public void rotate(int[][] matrix) {
        // Edge case check: empty matrix
        // 邊界條件檢查：空矩陣
        if (matrix == null || matrix.length == 0) return;

        int n = matrix.length;

        // Step 1: Transpose the matrix (swap matrix[i][j] with matrix[j][i])
        // 第一步：轉置矩陣（交換 matrix[i][j] 與 matrix[j][i]）
        for (int i = 0; i < n; i++) {
            // Start j from i to avoid swapping back elements we already swapped
            // j 從 i 開始，以避免將已經交換過的元素再次交換回來
            for (int j = i; j < n; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }

        // Step 2: Reverse each row (horizontal reflection)
        // 第二步：反轉每一列（水平映射）
        for (int i = 0; i < n; i++) {
            // Two pointers approach to reverse the row
            // 使用雙指針法來反轉該列
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

### Phase 3: Complexity & Analysis
### 複雜度與分析

*   **Time Complexity:** $O(N^2)$. We visit each cell twice (once for transpose, once for reverse).
    **時間複雜度：** $O(N^2)$。我們訪問每個單元格兩次（一次轉置，一次反轉）。
*   **Space Complexity:** $O(1)$. We only use a few temporary variables.
    **空間複雜度：** $O(1)$。我們只使用了幾個暫存變數。

### Phase 4: Common Mistake (Why it fails)
### 常見錯誤（為何會錯）

*   **Mistake:** In the Transpose step, iterating `j` from `0` to `n`.
    **錯誤：** 在轉置步驟中，將 `j` 從 `0` 迭代到 `n`。
*   **Consequence:** This swaps elements twice, returning the matrix to its original state. You must iterate `j` starting from `i` (upper triangle only).
    **後果：** 這會將元素交換兩次，使矩陣回到原始狀態。你必須從 `i` 開始迭代 `j`（僅處理上三角）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Pitfall / Difference (陷阱 / 差異) |
| :--- | :--- |
| **Modulo of Negative Numbers**<br>(負數取模) | In Java, `-5 % 3` is `-2`, not `1`. <br>在 Java 中，`-5 % 3` 是 `-2`，而不是 `1`。 <br>**Fix:** `((a % b) + b) % b` to get positive result. |
| **Integer Overflow**<br>(整數溢位) | `int mid = (left + right) / 2` can overflow.<br>`int mid = (left + right) / 2` 可能會溢位。<br>**Fix:** `int mid = left + (right - left) / 2;` |
| **Floating Point Equality**<br>(浮點數相等性) | Never use `a == b` for doubles.<br>永遠不要對 double 使用 `a == b`。<br>**Fix:** `Math.abs(a - b) < epsilon`. |
| **Matrix Coordinates**<br>(矩陣座標) | Standard math uses $(x, y)$, but matrices use `[row][col]` which is effectively $(y, x)$.<br>標準數學使用 $(x, y)$，但矩陣使用 `[row][col]`，實際上是 $(y, x)$。 |

---

## 6. Interview Strategy（面試實戰建議）

1.  **Clarify the Range (釐清範圍):**
    *   "Will the numbers fit in a standard 32-bit integer?"
    *   「這些數字是否適合標準的 32 位元整數？」
    *   *Why:* Shows you are a senior engineer who cares about system limits.
    *   *原因：* 顯示你是關注系統限制的資深工程師。

2.  **Visualize on Whiteboard (白板視覺化):**
    *   For geometry or matrix problems, draw a small $3 \times 3$ grid.
    *   對於幾何或矩陣問題，畫一個小的 $3 \times 3$ 網格。
    *   Manually trace the index changes (e.g., `(0,0) -> (0,2)`).
    *   手動追蹤索引變化（例如：`(0,0) -> (0,2)`）。

3.  **Handle "Math Magic" (處理「數學魔法」):**
    *   If you don't recall a specific theorem (e.g., Euclidean Algorithm), derive the brute force first, then ask: "Is there a mathematical property to optimize this?"
    *   如果你不記得特定的定理（如歐幾里得演算法），先推導暴力解，然後問：「是否有數學性質可以優化這個？」

---

## 7. Practice Problems（練習題）

### 1. Easy: Plus One (加一)
*   **Task:** Given a large integer as an array of digits, add one to the integer.
    **任務：** 給定一個以數字陣列表示的大整數，將該整數加一。
*   **Hint:** Handle the carry-over (9 -> 10). If the most significant digit carries over, resize array.
    **提示：** 處理進位（9 -> 10）。如果最高位進位，調整陣列大小。
*   **Core Skill:** Array iteration + Carry logic.
    **核心技能：** 陣列迭代 + 進位邏輯。

### 2. Medium: Spiral Matrix (螺旋矩陣)
*   **Task:** Return all elements of an $m \times n$ matrix in spiral order.
    **任務：** 以螺旋順序回傳 $m \times n$ 矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`) and shrink them as you traverse.
    **提示：** 使用 4 個邊界（`top`、`bottom`、`left`、`right`），並在遍歷時縮小它們。
*   **Core Skill:** Simulation + Boundary control.
    **核心技能：** 模擬 + 邊界控制。

### 3. Medium (Advanced for Beginner): Happy Number (快樂數)
*   **Task:** Determine if a number is "happy" (sum of squares of digits eventually equals 1).
    **任務：** 判斷一個數字是否為「快樂數」（數字平方和最終等於 1）。
*   **Hint:** This is actually a **Cycle Detection** problem. Use a HashSet or Floyd's Cycle Finding (Fast/Slow pointers) to detect infinite loops.
    **提示：** 這實際上是一個 **循環檢測** 問題。使用 HashSet 或 Floyd 判圈法（快慢指針）來檢測無限迴圈。
*   **Core Skill:** Digit extraction + Hashing/Two Pointers.
    **核心技能：** 數字提取 + 雜湊/雙指針。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Division by Zero:** Did I check if the denominator is 0?
    **除以零：** 我是否檢查了分母為 0 的情況？
*   [ ] **Overflow:** If I multiply two `int`, did I cast to `long` first?
    **溢位：** 如果我將兩個 `int` 相乘，我是否先轉型為 `long`？
*   [ ] **Boundaries:** In matrix loops, is it `< n` or `<= n`? Did I handle `matrix[0].length`?
    **邊界：** 在矩陣迴圈中，是 `< n` 還是 `<= n`？我是否處理了 `matrix[0].length`？
*   [ ] **Negative Inputs:** Does my logic hold for negative numbers (especially for modulo)?
    **負數輸入：** 我的邏輯對負數是否成立（特別是模運算）？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **Matrix Rotation = Onion Peeling or Transpose+Flip.**
    **矩陣旋轉 = 剝洋蔥 或 轉置+翻轉。**
    *   *Analogy:* To rotate a square piece of paper, you can flip it over its diagonal (transpose), then flip it horizontally.
    *   *類比：* 要旋轉一張正方形的紙，你可以沿著對角線翻轉它（轉置），然後水平翻轉。

*   **Modulo Operator `%` = Clock Arithmetic.**
    **模運算符 `%` = 時鐘算術。**
    *   *Analogy:* 13:00 is 1:00 because $13 \% 12 = 1$. It wraps around.
    *   *類比：* 13:00 就是 1:00，因為 $13 \% 12 = 1$。它是循環的。

*   **GCD (Euclidean) = Reduction.**
    **GCD（歐幾里得）= 縮減。**
    *   *Analogy:* To find the common tile size for a $A \times B$ floor, keep cutting the larger side by the length of the smaller side until they are equal (or one becomes 0).
    *   *類比：* 要為 $A \times B$ 的地板找到共同的磁磚尺寸，持續用較短邊的長度去切割較長邊，直到兩者相等（或其中一邊變為 0）。