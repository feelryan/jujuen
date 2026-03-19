Here is the complete interview preparation guide for **Math & Geometry**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level with **C++** implementation.

這是一份針對 **Math & Geometry（數學與幾何）** 的完整面試準備指南，專為資深軟體工程師設計，聚焦於 **中階（Intermediate）** 難度並使用 **C++** 實作。

---

# Math & Geometry Interview Guide (Intermediate)
# 數學與幾何面試指南（中階）

## 1. Learning Goals（學習目標）

*   **Master Matrix Manipulation:** Gain proficiency in traversing and modifying 2D grids (matrices) in-place without using extra space.
    **掌握矩陣操作：** 熟練地在不使用額外空間的情況下，原地（in-place）遍歷與修改二維網格（矩陣）。
*   **Handle Geometric Logic:** Understand how to represent coordinates, calculate distances, and detect overlaps (rectangles/circles) robustly.
    **處理幾何邏輯：** 理解如何穩健地表示座標、計算距離以及檢測重疊（矩形/圓形）。
*   **Avoid Precision & Overflow Issues:** Learn to handle floating-point inaccuracies and integer overflows, which are the most common "silent killers" in math interviews.
    **避免精度與溢位問題：** 學習處理浮點數誤差與整數溢位，這是數學面試中最常見的「隱形殺手」。
*   **Apply Mathematical Tricks:** Utilize GCD (Greatest Common Divisor) and basic number theory to optimize algorithms from $O(N)$ to $O(\log N)$ or $O(\sqrt{N})$.
    **應用數學技巧：** 利用最大公因數（GCD）與基礎數論將演算法從 $O(N)$ 優化至 $O(\log N)$ 或 $O(\sqrt{N})$。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）

*   **Matrix Indexing:** In programming, a matrix is usually `matrix[row][col]`, which corresponds to $(y, x)$ in Cartesian coordinates, not $(x, y)$. This flip often causes bugs.
    **矩陣索引：** 在程式設計中，矩陣通常是 `matrix[row][col]`，這對應笛卡爾座標系中的 $(y, x)$，而非 $(x, y)$。這種反轉常導致 Bug。
*   **Modulo Arithmetic:** $(a + b) \% m = ((a \% m) + (b \% m)) \% m$. This is crucial for keeping numbers within integer limits during large calculations.
    **模運算：** $(a + b) \% m = ((a \% m) + (b \% m)) \% m$。這對於在大數運算中將數值保持在整數範圍內至關重要。

### Complexity（複雜度）

*   **Time:** Usually $O(1)$ for formulas, $O(R \times C)$ for matrix traversal.
    **時間：** 公式計算通常為 $O(1)$，矩陣遍歷為 $O(R \times C)$。
*   **Space:** The gold standard for Senior Engineers is $O(1)$ extra space (in-place modification).
    **空間：** 資深工程師的黃金標準是 $O(1)$ 額外空間（原地修改）。

### When to use / Not to use（適用與不適用場景）

*   **Use when:** The problem involves grids, rotations, shapes, or finding the "nth" number in a sequence.
    **適用於：** 問題涉及網格、旋轉、形狀或尋找序列中的「第 n 個」數字。
*   **Not to use:** When the problem is clearly a graph traversal (BFS/DFS) disguised as a grid, unless the geometry properties simplify the search.
    **不適用於：** 當問題明顯是偽裝成網格的圖遍歷（BFS/DFS）時，除非幾何屬性能簡化搜尋。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Simulation (Matrix):** Following a specific path (e.g., Spiral Matrix) or transforming the grid (e.g., Rotate Image).
    **模擬（矩陣）：** 遵循特定路徑（如螺旋矩陣）或轉換網格（如旋轉影像）。
2.  **Geometry Overlap:** Checking if two rectangles or circles intersect.
    **幾何重疊：** 檢查兩個矩形或圓形是否相交。
3.  **Basic Number Theory:** Prime checking, GCD/LCM, or digit manipulation (e.g., Palindrome Number).
    **基礎數論：** 質數檢查、GCD/LCM 或位數操作（如回文數）。
4.  **Boyer-Moore Voting Algorithm:** Finding the majority element in $O(N)$ time and $O(1)$ space.
    **Boyer-Moore 投票演算法：** 在 $O(N)$ 時間與 $O(1)$ 空間內找出多數元素。

---

## 4. Example Walkthrough（範例講解）

### Problem: Rotate Image (LeetCode 48)
### 問題：旋轉影像

**Problem Statement:**
You are given an $n \times n$ 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image **in-place**, which means you have to modify the input 2D matrix directly. DO NOT allocate another 2D matrix and do the rotation.
**問題重述：**
給定一個代表影像的 $n \times n$ 二維矩陣，將影像順時針旋轉 90 度。你必須**原地**旋轉影像，這意味著直接修改輸入的二維矩陣。請勿分配另一個二維矩陣來進行旋轉。

---

### Approach: Brute Force → Mathematical Optimization
### 思路：暴力法 → 數學優化

1.  **Brute Force (Not Acceptable for Seniors):** Create a new matrix `new_mat`. Map `matrix[i][j]` to `new_mat[j][n-1-i]`.
    **暴力法（資深不適用）：** 建立新矩陣 `new_mat`。將 `matrix[i][j]` 對應到 `new_mat[j][n-1-i]`。
    *   *Space Complexity:* $O(N^2)$. Too expensive.
    *   *空間複雜度：* $O(N^2)$。太昂貴。

2.  **Optimal Solution (Mathematical Transformation):**
    **最佳解（數學變換）：**
    *   Observation: A 90-degree clockwise rotation is equivalent to a **Transpose** followed by a **Horizontal Reflection** (reversing each row).
    *   觀察：順時針旋轉 90 度等同於先進行**轉置（Transpose）**，再進行**水平鏡像（Horizontal Reflection）**（反轉每一列）。
    *   Step 1: Transpose: Swap `matrix[i][j]` with `matrix[j][i]`.
    *   步驟 1：轉置：交換 `matrix[i][j]` 與 `matrix[j][i]`。
    *   Step 2: Reverse: Reverse each row.
    *   步驟 2：反轉：反轉每一列。

### C++ Reference Solution
### C++ 參考解

```cpp
#include <vector>
#include <algorithm> // for std::swap, std::reverse

using namespace std;

class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();

        // Step 1: Transpose the matrix
        // 步驟 1：轉置矩陣
        // We only iterate the upper triangle to avoid swapping back.
        // 我們只遍歷上三角矩陣，以避免重複交換回來。
        for (int i = 0; i < n; ++i) {
            for (int j = i + 1; j < n; ++j) {
                // Swap element at (i, j) with (j, i)
                // 交換 (i, j) 與 (j, i) 的元素
                std::swap(matrix[i][j], matrix[j][i]);
            }
        }

        // Step 2: Reverse each row
        // 步驟 2：反轉每一列
        // This converts the transpose into a 90-degree rotation.
        // 這將轉置矩陣轉換為 90 度旋轉。
        for (int i = 0; i < n; ++i) {
            // Using STL reverse for cleaner code. 
            // Often acceptable in interviews, but know how to implement it manually (two pointers).
            // 使用 STL reverse 讓程式碼更簡潔。
            // 面試中通常可接受，但要知道如何手動實作（雙指針）。
            std::reverse(matrix[i].begin(), matrix[i].end());
        }
    }
};
```

### Complexity Analysis
### 複雜度分析

*   **Time:** $O(N^2)$. We visit each cell twice (once for transpose, once for reverse).
    **時間：** $O(N^2)$。我們訪問每個單元格兩次（一次轉置，一次反轉）。
*   **Space:** $O(1)$. We modify the matrix in place.
    **空間：** $O(1)$。我們原地修改矩陣。

### Common Mistake
### 常見錯誤

*   **Mistake:** Trying to rotate cell-by-cell in a spiral loop (4-way swap) without careful index tracking.
    **錯誤：** 試圖在螺旋迴圈中逐個單元格旋轉（4 向交換），但沒有仔細追蹤索引。
*   **Why it fails:** It is extremely error-prone to calculate the 4 coordinates `(i, j) -> (j, n-1-i) -> (n-1-i, n-1-j) -> (n-1-j, i)` correctly under pressure. The "Transpose + Reverse" method is much harder to mess up.
    **為何失敗：** 在壓力下正確計算 4 個座標 `(i, j) -> (j, n-1-i) -> (n-1-i, n-1-j) -> (n-1-j, i)` 極易出錯。「轉置 + 反轉」的方法則難以出錯。

---

## 5. Common Pitfalls & Confusing Concepts（常見陷阱與易混淆概念）

| Concept | Trap / Nuance (陷阱 / 細微差別) |
| :--- | :--- |
| **Integer Overflow** | `int mid = (left + right) / 2` can overflow. Use `left + (right - left) / 2`. <br> `int mid = (left + right) / 2` 可能溢位。應使用 `left + (right - left) / 2`。 |
| **Float Equality** | Never use `a == b` for floats. Use `abs(a - b) < epsilon`. <br> 永遠不要對浮點數使用 `a == b`。應使用 `abs(a - b) < epsilon`。 |
| **Matrix Coordinates** | $(x, y)$ in geometry usually means $(col, row)$ in matrices. Always clarify if inputs are `(row, col)` or `(x, y)`. <br> 幾何中的 $(x, y)$ 在矩陣中通常意味著 $(col, row)$。務必確認輸入是 `(row, col)` 還是 `(x, y)`。 |
| **Modulo Negative** | In C++, `-5 % 3` is `-2`, not `1`. To get mathematical modulo: `((a % n) + n) % n`. <br> 在 C++ 中，`-5 % 3` 是 `-2`，不是 `1`。要得到數學模數：`((a % n) + n) % n`。 |

---

## 6. Interview Strategy（面試實戰建議）

1.  **Clarify Constraints First:**
    **首先釐清限制條件：**
    *   "Will the numbers fit in a standard 32-bit integer?" (Checks for overflow awareness).
    *   「數字是否在標準 32 位元整數範圍內？」（檢查對溢位的警覺性）。
    *   "Is the matrix square ($N \times N$) or rectangular ($N \times M$)?"
    *   「矩陣是正方形（$N \times N$）還是長方形（$N \times M$）？」

2.  **Whiteboard Strategy (Draw it out):**
    **白板策略（畫出來）：**
    *   For geometry or matrix problems, **always** draw a small example (e.g., $3 \times 3$ matrix) and manually simulate the indices.
    *   對於幾何或矩陣問題，**務必**畫一個小範例（如 $3 \times 3$ 矩陣）並手動模擬索引。
    *   Do not try to derive the index formula $matrix[i][j] \to matrix[j][n-1-i]$ purely in your head.
    *   不要試圖純粹在腦海中推導索引公式 $matrix[i][j] \to matrix[j][n-1-i]$。

3.  **Talk Through the Math:**
    **口述數學邏輯：**
    *   "Since we are looking for overlapping areas, I will project the shapes onto the X and Y axes separately."
    *   「因為我們在尋找重疊區域，我會將形狀分別投影到 X 軸和 Y 軸上。」

---

## 7. Practice Exercises（練習題）

### 1. Easy: Plus One
**Problem:** Given a large integer represented as an integer array `digits`, increment the large integer by one.
**問題：** 給定一個由整數陣列 `digits` 表示的大整數，將該整數加一。
*   **Hint:** Handle the carry (999 -> 1000). Iterate backwards.
*   **提示：** 處理進位（999 -> 1000）。反向遍歷。

### 2. Medium: Spiral Matrix
**Problem:** Given an $m \times n$ matrix, return all elements of the matrix in spiral order.
**問題：** 給定一個 $m \times n$ 矩陣，以螺旋順序回傳矩陣的所有元素。
*   **Hint:** Use 4 boundaries (`top`, `bottom`, `left`, `right`). Shrink them after traversing each row/column.
*   **提示：** 使用 4 個邊界（`top`, `bottom`, `left`, `right`）。遍歷每一行/列後縮小邊界。

### 3. Hard: Max Points on a Line
**Problem:** Given an array of points where `points[i] = [xi, yi]`, find the maximum number of points that lie on the same straight line.
**問題：** 給定一個點的陣列 `points[i] = [xi, yi]`，找出位於同一直線上的最大點數。
*   **Hint:** Use a Hash Map to store slopes for each point. Be careful with vertical lines (slope = infinity). Use GCD to store slope as a reduced fraction `dy/dx` to avoid floating point issues.
*   **提示：** 對每個點使用雜湊表（Hash Map）儲存斜率。小心垂直線（斜率 = 無窮大）。利用 GCD 將斜率儲存為最簡分數 `dy/dx` 以避免浮點數問題。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Overflow:** Did I use `long long` for area calculations or intermediate sums?
    **溢位：** 我是否在面積計算或中間總和使用了 `long long`？
*   [ ] **Division by Zero:** Did I check if the denominator is 0 (e.g., calculating slope)?
    **除以零：** 我是否檢查了分母為 0 的情況（例如計算斜率時）？
*   [ ] **Boundaries:** In matrix loops, is it `< n` or `<= n`? Did I handle the empty matrix `[]`?
    **邊界：** 在矩陣迴圈中，是 `< n` 還是 `<= n`？我是否處理了空矩陣 `[]`？
*   [ ] **In-place:** Did I strictly follow the $O(1)$ space requirement if asked?
    **原地操作：** 如果有要求，我是否嚴格遵守了 $O(1)$ 空間限制？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **Matrix Rotation = Onion Peeling:**
    **矩陣旋轉 = 剝洋蔥：**
    Think of processing a matrix in layers (outer shell, then inner shell). This applies to both Rotation and Spiral Matrix.
    想像分層處理矩陣（外殼，然後內殼）。這適用於旋轉與螺旋矩陣。

*   **Slope = Rise over Run (Reduced):**
    **斜率 = 垂直變化除以水平變化（最簡化）：**
    Don't store `double slope = 0.3333`. Store the "DNA" of the slope: `pair<int, int> = {1, 3}` (after dividing by GCD).
    不要儲存 `double slope = 0.3333`。儲存斜率的「DNA」：`pair<int, int> = {1, 3}`（除以 GCD 後）。

*   **Transpose = Mirror on Diagonal:**
    **轉置 = 對角線鏡像：**
    Imagine a mirror placed from top-left to bottom-right. Elements swap across this mirror.
    想像一面鏡子從左上角放置到右下角。元素跨越這面鏡子進行交換。