這裡是一份針對 **Math & Geometry (數學與幾何)** 的進階面試教材，專為具備豐富經驗的資深工程師設計。
Here is an advanced interview tutorial for **Math & Geometry**, designed specifically for experienced Senior Software Engineers.

---

# Math & Geometry: Advanced Interview Guide
# 數學與幾何：進階面試指南

## 1. Learning Goals (學習目標)

1.  **掌握計算幾何的核心原語（Geometric Primitives）。**
    Master the core primitives of computational geometry.
    *目標是能熟練實作外積（Cross Product）來判斷點的方向性與相對位置。*
    *The goal is to proficiently implement Cross Product to determine directionality and relative position of points.*

2.  **處理浮點數精度與數值溢位問題。**
    Handle floating-point precision and numerical overflow issues.
    *資深工程師必須知道何時該用 `long` 替代 `int`，以及如何處理 `double` 的 epsilon 誤差。*
    *Senior engineers must know when to use `long` instead of `int`, and how to handle epsilon errors with `double`.*

3.  **熟練運用掃描線演算法（Line Sweep）與凸包（Convex Hull）。**
    Proficiently apply Line Sweep algorithms and Convex Hull.
    *這是區分中階與高階候選人的關鍵題型，涉及排序與幾何不變性。*
    *These are key topics distinguishing intermediate from advanced candidates, involving sorting and geometric invariants.*

4.  **理解採樣與機率（Sampling & Probability）的實作模式。**
    Understand implementation patterns for Sampling & Probability.
    *例如蓄水池抽樣（Reservoir Sampling）與拒絕採樣（Rejection Sampling）。*
    *For example, Reservoir Sampling and Rejection Sampling.*

---

## 2. Core Concepts (核心觀念速覽)

### 2.1 Vector Cross Product (向量外積)
*   **定義 (Definition):** 對於二維向量 $A$ 和 $B$，外積 $A \times B = x_A y_B - x_B y_A$。
    For 2D vectors $A$ and $B$, the cross product is $A \times B = x_A y_B - x_B y_A$.
*   **直覺 (Intuition):** 判斷旋轉方向。若結果 $>0$，表示逆時針（左轉）；$<0$ 表示順時針（右轉）；$=0$ 表示共線。
    Determines rotation direction. If result $>0$, it implies counter-clockwise (left turn); $<0$ implies clockwise (right turn); $=0$ implies collinear.
*   **適用場景 (Use Cases):** 凸包、判斷點在多邊形內、線段相交檢測。
    Convex Hull, Point-in-Polygon test, Line Segment Intersection detection.

### 2.2 Greatest Common Divisor (GCD / 最大公因數)
*   **定義 (Definition):** 歐幾里得演算法 (Euclidean Algorithm): `gcd(a, b) = gcd(b, a % b)`。
    Euclidean Algorithm: `gcd(a, b) = gcd(b, a % b)`.
*   **複雜度 (Complexity):** $O(\log(\min(a, b)))$。
*   **適用場景 (Use Cases):** 簡化分數（如直線斜率表示）、數論問題。
    Simplifying fractions (e.g., representing line slopes), number theory problems.

### 2.3 Reservoir Sampling (蓄水池抽樣)
*   **定義 (Definition):** 從包含 $N$ 個元素（$N$ 未知或很大）的串流中隨機選取 $k$ 個元素，使每個元素被選中的機率為 $k/N$。
    Randomly selecting $k$ elements from a stream of $N$ elements ($N$ is unknown or large) such that each element has a probability of $k/N$ of being chosen.
*   **直覺 (Intuition):** 對於第 $i$ 個元素，以 $k/i$ 的機率替換蓄水池中的元素。
    For the $i$-th element, replace an element in the reservoir with probability $k/i$.

---

## 3. Typical Patterns (典型題型 / 模式)

| Pattern (模式) | Description (描述) | Key Algorithms (關鍵演算法) |
| :--- | :--- | :--- |
| **Geometry Construction** | 從點集構建幾何形狀。 <br> Constructing geometric shapes from a set of points. | **Monotone Chain**, Jarvis March (Convex Hull) |
| **Line Sweep** | 透過一條掃描線處理區間重疊或面積問題。 <br> Processing interval overlaps or area problems via a sweep line. | Sorting events by coordinate + Active Set maintenance |
| **Coordinate Compression** | 當座標範圍很大但點很稀疏時，將座標映射到離散的索引。 <br> Mapping coordinates to discrete indices when the range is large but points are sparse. | `HashMap` or `Binary Search` on sorted unique coordinates |
| **Math Simulation** | 模擬數學過程，通常涉及大數運算或矩陣。 <br> Simulating mathematical processes, often involving big integer arithmetic or matrices. | Matrix Exponentiation (Fibonacci $O(\log N)$) |

---

## 4. Example Walkthrough (範例講解)

### Problem: Erect the Fence (Convex Hull)
**問題重述 (Problem Restatement):**
給定一個二維平面上的點集，求出圍繞這些點的最小凸多邊形（凸包）的頂點。
Given a set of points on a 2D plane, find the vertices of the smallest convex polygon (Convex Hull) that encloses these points.
*(LeetCode 587 - Hard)*

### Approach (思路)

1.  **暴力法 (Brute Force):**
    找出所有點對，檢查其餘所有點是否都在這條線的同一側。時間複雜度 $O(N^3)$。
    Find all pairs of points and check if all other points lie on the same side of the line. Time complexity $O(N^3)$.

2.  **優化：Jarvis March (Gift Wrapping):**
    從最左下的點開始，每次尋找「最右側」的點。時間複雜度 $O(NH)$，其中 $H$ 是凸包上的點數。最差情況 $O(N^2)$。
    Start from the bottom-left point, and repeatedly find the "rightmost" point. Time complexity $O(NH)$, where $H$ is the number of points on the hull. Worst case $O(N^2)$.

3.  **最佳解：Monotone Chain Algorithm (單調鏈演算法):**
    將點按 x 座標排序。分別構建「上凸包」和「下凸包」。遍歷排序後的點，利用 Stack 維護凸性（若新加入的點造成「右轉」或凹陷，則彈出 Stack 頂端）。
    Sort points by x-coordinate. Construct the "Upper Hull" and "Lower Hull" separately. Iterate through sorted points, using a Stack to maintain convexity (pop from Stack if the new point causes a "right turn" or concavity).
    **時間複雜度 (Time Complexity):** $O(N \log N)$ (dominated by sorting).
    **空間複雜度 (Space Complexity):** $O(N)$ (for the hull).

### Java Solution (Monotone Chain)

```java
import java.util.*;

class Solution {
    // 定義點的結構，方便操作
    // Define a Point structure for easier manipulation
    static class Point {
        int x, y;
        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
        
        // 覆寫 equals 和 hashCode 以便去重
        // Override equals and hashCode for deduplication
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Point point = (Point) o;
            return x == point.x && y == point.y;
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }
    }

    public int[][] outerTrees(int[][] trees) {
        int n = trees.length;
        if (n <= 1) return trees;

        // 1. 將輸入轉換為 Point 物件並排序
        // 1. Convert input to Point objects and sort
        List<Point> points = new ArrayList<>();
        for (int[] t : trees) {
            points.add(new Point(t[0], t[1]));
        }
        
        // 排序規則：先按 x 升序，若 x 相同則按 y 升序
        // Sorting rule: Ascending by x first, then by y if x is same
        points.sort((a, b) -> a.x == b.x ? a.y - b.y : a.x - b.x);

        // 2. 構建凸包 (使用 Stack 概念，但在 Java 中用 ArrayList 模擬)
        // 2. Build Convex Hull (Using Stack concept, simulated with ArrayList in Java)
        List<Point> hull = new ArrayList<>();

        // 2a. 構建下凸包 (Lower Hull)
        // 2a. Build Lower Hull
        for (Point p : points) {
            // 當加入新點 p 會導致順時針轉向 (crossProduct < 0) 時，移除最後一個點
            // Remove the last point if adding new point p causes a clockwise turn (crossProduct < 0)
            // 注意：題目要求凸包邊上的點也要保留，所以嚴格右轉才移除 (< 0)
            // Note: Problem requires keeping collinear points on hull, so remove only on strict right turn (< 0)
            while (hull.size() >= 2 && 
                   crossProduct(hull.get(hull.size() - 2), hull.get(hull.size() - 1), p) < 0) {
                hull.remove(hull.size() - 1);
            }
            hull.add(p);
        }

        // 2b. 構建上凸包 (Upper Hull)
        // 2b. Build Upper Hull
        // 從右向左遍歷
        // Iterate from right to left
        int lowerHullSize = hull.size();
        for (int i = points.size() - 2; i >= 0; i--) {
            Point p = points.get(i);
            // 邏輯相同：維持逆時針方向
            // Same logic: maintain counter-clockwise direction
            while (hull.size() > lowerHullSize && 
                   crossProduct(hull.get(hull.size() - 2), hull.get(hull.size() - 1), p) < 0) {
                hull.remove(hull.size() - 1);
            }
            hull.add(p);
        }

        // 3. 去重並格式化輸出
        // 3. Deduplicate and format output
        // 最後一個點是起點的重複，需要處理 (HashSet 自動去重)
        // The last point is a duplicate of the start, need handling (HashSet handles deduplication)
        HashSet<Point> uniqueHull = new HashSet<>(hull);
        int[][] res = new int[uniqueHull.size()][2];
        int i = 0;
        for (Point p : uniqueHull) {
            res[i][0] = p.x;
            res[i][1] = p.y;
            i++;
        }
        return res;
    }

    // 計算外積：(b - a) X (c - b)
    // Calculate Cross Product: (b - a) X (c - b)
    // 返回值 > 0: 左轉 (逆時針), < 0: 右轉 (順時針), = 0: 共線
    // Returns > 0: Left turn (CCW), < 0: Right turn (CW), = 0: Collinear
    private int crossProduct(Point a, Point b, Point c) {
        // 使用 int 運算可能會溢位，雖然這題座標範圍小，但面試建議轉為 long
        // Integer arithmetic might overflow. Though coords are small here, prefer casting to long in interviews.
        long cp = (long)(b.x - a.x) * (c.y - b.y) - (long)(b.y - a.y) * (c.x - b.x);
        if (cp > 0) return 1;
        if (cp < 0) return -1;
        return 0;
    }
}
```

### Common Mistakes (錯誤示範)
*   **Mistake:** 使用斜率 (`slope = (y2-y1)/(x2-x1)`) 來判斷方向。
    Using slope to determine direction.
*   **Why:** 垂直線會導致除以零錯誤；且浮點數精度不穩定。
    Vertical lines cause division by zero; floating-point precision is unstable.
*   **Correction:** 始終使用乘法形式的外積。
    Always use the multiplication form of the Cross Product.

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Cross Product (外積)** | **Dot Product (內積)** | 外積判斷**方向** (左/右) 與面積；內積判斷**角度** (垂直/投影)。<br>Cross product for **direction** (L/R) & area; Dot product for **angle** (orthogonal/projection). |
| **int** | **double** | 在幾何題中，能用整數運算絕不用浮點數。若必須用 `double`，比較時需使用 `Math.abs(a-b) < epsilon`。<br>In geometry, avoid floats if integer math suffices. If `double` is needed, use `epsilon` for comparisons. |
| **O(N^2)** | **O(N log N)** | 幾何題的暴力解通常是 $O(N^2)$ 或 $O(N^3)$，但大多數進階幾何問題（最近點對、凸包）都可透過排序優化至 $O(N \log N)$。<br>Brute force is often $O(N^2)/O(N^3)$, but advanced problems (Closest Pair, Convex Hull) can be optimized to $O(N \log N)$ via sorting. |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Coordinates (釐清座標範圍):**
    *   "Are the coordinates integers or floats?" (座標是整數還是浮點數？)
    *   "What is the range? Do I need to worry about overflow?" (範圍多大？需要擔心溢位嗎？)
    *   *Strategy:* 即使範圍看似安全，主動提及 `long` 展現資深經驗。
    *   *Strategy:* Even if the range looks safe, proactively mentioning `long` shows seniority.

2.  **Modularize Code (模組化程式碼):**
    *   不要在主邏輯中寫一長串數學公式。
    *   Don't write long math formulas in the main logic.
    *   建立 helper functions：`getCrossProduct(p1, p2, p3)`, `getDistance(p1, p2)`, `gcd(a, b)`。
    *   Create helper functions. 這讓程式碼可讀性極高且易於除錯。

3.  **Draw Diagrams (畫圖輔助):**
    *   幾何題很難純口述。在白板或線上畫板上畫出三個點，標註 $A, B, C$，演示外積的方向。
    *   Geometry is hard to narrate. Draw three points $A, B, C$ on the whiteboard, demonstrating the direction of the cross product.

4.  **Handle Edge Cases (處理邊界):**
    *   共線 (Collinear points)。
    *   重疊點 (Duplicate points)。
    *   只有 1 或 2 個點的情況。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Happy Number** (LeetCode 202)
*   **Hint:** 使用快慢指針 (Floyd's Cycle Finding) 檢測數字平方和序列中的循環。
    Use Fast & Slow Pointers (Floyd's Cycle Finding) to detect cycles in the sequence of squared digit sums.
*   **Key:** 這是 Math 與 Linked List 概念的結合。

### Level: Medium
**Problem:** **Max Points on a Line** (LeetCode 149)
*   **Hint:** 固定一個點，計算其他點與該點的斜率。使用 `HashMap<String, Integer>` 儲存斜率（用 "dy/dx" 的最簡分數形式作為 Key，避免浮點誤差）。
    Fix one point, calculate slopes to other points. Use `HashMap` to store slopes (use reduced fraction "dy/dx" as Key to avoid float errors).
*   **Key:** 需要實作 `gcd` 來化簡分數。

### Level: Hard
**Problem:** **Rectangle Area II** (LeetCode 850)
*   **Hint:** 計算多個矩形的聯集面積。使用 **Line Sweep (掃描線)** 演算法結合 **Coordinate Compression (座標壓縮)** 或 Segment Tree。
    Calculate the union area of multiple rectangles. Use **Line Sweep** combined with **Coordinate Compression** or Segment Tree.
*   **Key:** 將二維面積問題轉化為一維區間覆蓋問題。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Overflow Check:** Does intermediate multiplication (like in Cross Product) exceed `Integer.MAX_VALUE`? Use `long`.
    (溢位檢查：中間運算是否超過整數範圍？使用 `long`。)
*   [ ] **Precision Check:** If using `double`, did I use an `EPSILON` (e.g., `1e-9`) for equality checks?
    (精度檢查：若使用浮點數，是否使用了 `EPSILON` 進行相等比較？)
*   [ ] **Division by Zero:** Did I handle vertical lines (dx = 0) when calculating slopes?
    (除以零：計算斜率時是否處理了垂直線？)
*   [ ] **Sorting:** Did I sort the points correctly? (e.g., by x, then by y).
    (排序：點的排序是否正確？)

---

## 9. Memory Anchors (記憶錨點)

*   **Cross Product = Steering Wheel (方向盤):**
    *   正值 (+) = 左轉 (Left Turn)
    *   負值 (-) = 右轉 (Right Turn)
    *   零 (0) = 直行 (Straight/Collinear)

*   **Convex Hull = Rubber Band (橡皮筋):**
    *   想像一條橡皮筋縮緊在釘子上，最外圈的釘子就是凸包。
    *   Imagine a rubber band snapping around nails; the outermost nails form the Convex Hull.

*   **GCD = Tile Fitting (鋪磁磚):**
    *   GCD 是能完美鋪滿 $A \times B$ 矩形的最大正方形邊長。
    *   GCD is the side length of the largest square that perfectly tiles an $A \times B$ rectangle.