# Math & Geometry: Advanced Interview Guide
# 數學與幾何：進階面試指南

## 1. Learning Objectives (學習目標)

1.  **Master Vector Arithmetic for Geometry:** Understand how to use Dot Product and Cross Product to solve geometric predicates (e.g., orientation, intersection) without relying on complex trigonometry.
    **掌握幾何向量運算：** 理解如何使用點積（Dot Product）與外積（Cross Product）來解決幾何判斷（如方向、相交），而不依賴複雜的三角函數。

2.  **Handle Floating-Point Precision:** Learn strategies to deal with `epsilon` comparisons and numerical instability, which is critical in production-grade geometry code.
    **處理浮點數精度：** 學習處理 `epsilon` 比較與數值不穩定性的策略，這在生產級幾何程式碼中至關重要。

3.  **Optimize Number Theory Algorithms:** Move beyond basic iteration to $O(\sqrt{N})$ or logarithmic solutions for primality tests, GCD, and modular arithmetic.
    **優化數論演算法：** 超越基本迭代，針對質數測試、最大公因數（GCD）與模運算採用 $O(\sqrt{N})$ 或對數級解法。

4.  **Apply Geometric Sweep-Line & Convex Hull:** Implement advanced algorithms like Monotone Chain or Graham Scan for spatial boundary problems.
    **應用幾何掃描線與凸包：** 針對空間邊界問題實作如單調鏈（Monotone Chain）或 Graham Scan 等進階演算法。

---

## 2. Core Concepts (核心觀念速覽)

### Vector Math (向量數學)
*   **Cross Product (2D):** $A \times B = x_A y_B - x_B y_A$.
    **外積（2D）：** $A \times B = x_A y_B - x_B y_A$。
    *   *Intuition:* Determines orientation. Positive = Left turn (Counter-Clockwise), Negative = Right turn (Clockwise), Zero = Collinear.
    *   *直覺：* 決定方向。正值 = 左轉（逆時針），負值 = 右轉（順時針），零 = 共線。
*   **Dot Product:** $A \cdot B = x_A x_B + y_A y_B$.
    **點積：** $A \cdot B = x_A x_B + y_A y_B$。
    *   *Intuition:* Projections. Used to check perpendicularity or if a point lies within a segment range.
    *   *直覺：* 投影。用於檢查垂直性或點是否在線段範圍內。

### Number Theory (數論)
*   **Modulo Arithmetic:** $(a + b) \% m = ((a \% m) + (b \% m)) \% m$. Essential for preventing overflow.
    **模運算：** $(a + b) \% m = ((a \% m) + (b \% m)) \% m$。對於防止溢位至關重要。
*   **GCD (Euclidean):** $GCD(a, b) = GCD(b, a \% b)$. Complexity is $O(\log(\min(a, b)))$.
    **最大公因數（歐幾里得）：** $GCD(a, b) = GCD(b, a \% b)$。複雜度為 $O(\log(\min(a, b)))$。

### Complexity (複雜度)
*   **Time:** Geometry sorting usually dominates at $O(N \log N)$. Number theory is often $O(\log N)$ or $O(\sqrt{N})$.
    **時間：** 幾何排序通常佔主導地位，為 $O(N \log N)$。數論通常為 $O(\log N)$ 或 $O(\sqrt{N})$。
*   **Space:** $O(N)$ to store points or hulls.
    **空間：** $O(N)$ 用於儲存點或凸包。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Orientation Analysis (Cross Product):**
    **方向分析（外積）：**
    Used in Convex Hull, point-in-polygon tests, and intersection detection.
    用於凸包、點在多邊形內測試以及相交檢測。

2.  **Coordinate Compression:**
    **座標壓縮：**
    Mapping large sparse coordinates to a smaller dense range to apply Grid or Segment Tree approaches (e.g., Rectangle Area II).
    將稀疏的大座標映射到較小的密集範圍，以應用網格或線段樹方法（例如：矩形面積 II）。

3.  **Monotone Chain / Graham Scan:**
    **單調鏈 / Graham 掃描：**
    Standard algorithms for finding the Convex Hull (the smallest polygon enclosing all points).
    尋找凸包（包圍所有點的最小多邊形）的標準演算法。

4.  **Boyer-Moore Voting / Reservoir Sampling:**
    **Boyer-Moore 投票 / 水塘抽樣：**
    Statistical math problems often appearing in streaming data contexts.
    常出現於串流數據情境中的統計數學問題。

---

## 4. Example Walkthrough (範例講解)

### Problem: Erect the Fence (Convex Hull)
### 問題：架設圍欄（凸包）

**Problem Statement:**
You are given an array of trees where `trees[i] = [xi, yi]` represents the location of a tree in the garden. You are asked to fence the entire garden using the minimum length of rope as it is expensive. The garden is well fenced only if all the trees are enclosed. Return the coordinates of trees that are exactly on the fence perimeter.
**問題重述：**
給定一個樹木陣列，其中 `trees[i] = [xi, yi]` 代表花園中樹木的位置。要求用最短的繩索圍住整個花園。只有當所有樹木都被圍住時，花園才算被妥善圍好。請回傳正好位於圍欄周邊的樹木座標。

---

### Approach (思路)

1.  **Brute Force (Jarvis March / Gift Wrapping):**
    **暴力法（Jarvis March / 禮物包裝法）：**
    *   Start from the leftmost point. For every point, find the next point that is "most counter-clockwise" relative to the current point.
    *   從最左邊的點開始。對於每個點，找到相對於當前點「最逆時針」的下一個點。
    *   *Complexity:* $O(N^2)$ in worst case (if all points are on the hull).
    *   *複雜度：* 最壞情況下為 $O(N^2)$（如果所有點都在凸包上）。

2.  **Optimization (Monotone Chain):**
    **優化（單調鏈演算法）：**
    *   Sort points by x-coordinate (then y).
    *   依 x 座標（然後 y）對點進行排序。
    *   Build the **Lower Hull**: Iterate through points, maintaining a stack. If adding a new point makes a "right turn" (clockwise), pop the last point from the stack because it's now inside the hull.
    *   建立**下凸包**：遍歷所有點，維護一個堆疊。如果加入新點導致「右轉」（順時針），則從堆疊中彈出上一點，因為它現在位於凸包內部。
    *   Build the **Upper Hull**: Iterate in reverse order with the same logic.
    *   建立**上凸包**：以相同邏輯反向遍歷。
    *   *Complexity:* $O(N \log N)$ due to sorting.
    *   *複雜度：* 因排序而為 $O(N \log N)$。

---

### TypeScript Solution (Monotone Chain)

```typescript
type Point = [number, number];

/**
 * Calculates the cross product of vectors OA and OB.
 * 計算向量 OA 與 OB 的外積。
 * A positive value indicates a counter-clockwise turn (Left).
 * 正值表示逆時針轉向（左轉）。
 * A negative value indicates a clockwise turn (Right).
 * 負值表示順時針轉向（右轉）。
 * Zero indicates collinearity.
 * 零表示共線。
 */
function crossProduct(o: Point, a: Point, b: Point): number {
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
}

function outerTrees(trees: Point[]): Point[] {
    const n = trees.length;
    // If less than 4 points, all are on the hull.
    // 如果少於 4 個點，則所有點都在凸包上。
    if (n <= 3) return trees;

    // Sort by x-coordinate, then y-coordinate.
    // 依 x 座標排序，若相同則依 y 座標排序。
    trees.sort((a, b) => {
        return a[0] === b[0] ? a[1] - b[1] : a[0] - b[0];
    });

    const upperHull: Point[] = [];
    const lowerHull: Point[] = [];

    // Build Lower Hull
    // 建立下凸包
    for (const point of trees) {
        // While we have at least 2 points and the turn is NOT counter-clockwise (it's a right turn or straight),
        // we remove the last point because it is inside the hull.
        // 當堆疊中至少有 2 個點，且轉向「非」逆時針（即右轉或直線）時，
        // 我們移除最後一個點，因為它在凸包內部。
        while (
            lowerHull.length >= 2 &&
            crossProduct(
                lowerHull[lowerHull.length - 2],
                lowerHull[lowerHull.length - 1],
                point
            ) < 0 // < 0 means right turn (clockwise). For collinear points (==0), we keep them.
                  // < 0 表示右轉（順時針）。對於共線點（==0），我們保留它們。
        ) {
            lowerHull.pop();
        }
        lowerHull.push(point);
    }

    // Build Upper Hull (Iterate backwards)
    // 建立上凸包（反向遍歷）
    for (let i = n - 1; i >= 0; i--) {
        const point = trees[i];
        while (
            upperHull.length >= 2 &&
            crossProduct(
                upperHull[upperHull.length - 2],
                upperHull[upperHull.length - 1],
                point
            ) < 0
        ) {
            upperHull.pop();
        }
        upperHull.push(point);
    }

    // Concatenate and remove duplicates (start/end points might be duplicated).
    // 合併並移除重複項（起點/終點可能會重複）。
    // Using a Set of strings to filter unique coordinates.
    // 使用字串 Set 來過濾唯一的座標。
    const uniquePoints = new Set<string>();
    for (const p of [...lowerHull, ...upperHull]) {
        uniquePoints.add(`${p[0]},${p[1]}`);
    }

    const result: Point[] = [];
    uniquePoints.forEach(val => {
        const [x, y] = val.split(',').map(Number);
        result.push([x, y]);
    });

    return result;
}
```

### Why it works & Complexity (為何有效與複雜度)
*   **Time:** $O(N \log N)$ dominated by sorting. The hull construction is linear $O(N)$ because each point is pushed and popped at most once.
    **時間：** $O(N \log N)$，由排序主導。凸包建構是線性 $O(N)$，因為每個點最多被推入與彈出一次。
*   **Space:** $O(N)$ to store the hull points.
    **空間：** $O(N)$ 用於儲存凸包點。
*   **Key Detail:** The condition `< 0` in the `while` loop handles collinear points correctly by keeping them. If the problem asked for *only* vertices (no points on edges), we would use `<= 0`.
    **關鍵細節：** `while` 迴圈中的 `< 0` 條件正確地處理了共線點（保留它們）。如果題目要求*僅*頂點（邊上無點），我們會使用 `<= 0`。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Pitfall (錯誤/陷阱) | Correct Approach (正確方法) |
| :--- | :--- | :--- |
| **Floating Point Equality** | Checking `a === b` with floats. <br> 檢查浮點數 `a === b`。 | Use epsilon: `Math.abs(a - b) < 1e-9`. <br> 使用 epsilon：`Math.abs(a - b) < 1e-9`。 |
| **Slope Calculation** | Using `y/x` to store slopes (division by zero risk). <br> 使用 `y/x` 儲存斜率（除以零風險）。 | Store slope as a reduced fraction `(dy, dx)` using GCD, or handle vertical lines separately. <br> 使用 GCD 將斜率存為約分後的分數 `(dy, dx)`，或單獨處理垂直線。 |
| **Cross Product Overflow** | `(x2-x1)*(y3-y1)` can exceed standard integer limits. <br> `(x2-x1)*(y3-y1)` 可能超出標準整數限制。 | In Python this is handled automatically. In TS/JS, use `BigInt` if coordinates are very large (though `number` is double precision, usually safe up to $2^{53}$). <br> Python 自動處理。在 TS/JS 中，若座標極大請用 `BigInt`（雖然 `number` 是雙精度，通常 $2^{53}$ 內安全）。 |
| **Modulo of Negative Numbers** | `-5 % 3` results in `-2` in JS/TS, but mathematically should be `1`. <br> `-5 % 3` 在 JS/TS 中結果為 `-2`，但數學上應為 `1`。 | Use `((a % n) + n) % n` to ensure positive results. <br> 使用 `((a % n) + n) % n` 確保正數結果。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Precision Requirements:**
    **釐清精度需求：**
    "Should I handle floating point coordinates, or are inputs strictly integers?"
    「我需要處理浮點數座標嗎？還是輸入嚴格為整數？」

2.  **Define Helper Functions First:**
    **先定義輔助函式：**
    Don't write raw math inside loops. Define `getGCD(a, b)`, `getCrossProduct(a, b, c)`, or `getDistance(p1, p2)`. This shows abstraction skills and keeps code clean.
    不要在迴圈中寫原始數學運算。定義 `getGCD`、`getCrossProduct` 或 `getDistance`。這展現抽象化能力並保持程式碼整潔。

3.  **Visualize the "Sweep":**
    **視覺化「掃描」過程：**
    For geometry, draw a line on the whiteboard moving across the plane. Explain what state you maintain (e.g., active intervals) as the line moves.
    對於幾何題，在白板上畫一條移動穿過平面的線。解釋當線移動時你維護了什麼狀態（例如：活動區間）。

4.  **Follow-up on Scalability:**
    **針對可擴展性的追問：**
    "What if coordinates are GPS data (lat/long)?" -> Discuss spherical geometry or projection approximations.
    「如果座標是 GPS 數據（經緯度）怎麼辦？」 -> 討論球面幾何或投影近似。

---

## 7. Practice Problems (練習題)

### 1. Easy: Happy Number (快樂數)
*   **Concept:** Cycle Detection (Floyd's Cycle-Finding) + Digit Math.
*   **Hint:** Use two pointers (slow/fast) on the sequence of sum-of-squares. If fast reaches 1, it's happy. If fast meets slow, it's a cycle (not happy).
*   **觀念：** 週期檢測（Floyd 判圈法）+ 位數數學。
*   **提示：** 在平方和序列上使用雙指針（快/慢）。若快指針到達 1，則為快樂數。若快慢相遇，則為循環（非快樂數）。

### 2. Medium: Max Points on a Line (直線上最多的點數)
*   **Concept:** Geometry + Hash Map + GCD.
*   **Hint:** Fix one point $i$, iterate all other points $j$. Calculate slope $(y_j - y_i) / (x_j - x_i)$. Store slopes in a Map. Handle duplicates and vertical lines. Use GCD to store slope as a unique string key `"dy/dx"`.
*   **觀念：** 幾何 + 雜湊表 + 最大公因數。
*   **提示：** 固定一點 $i$，遍歷所有其他點 $j$。計算斜率 $(y_j - y_i) / (x_j - x_i)$。將斜率存入 Map。處理重複點與垂直線。使用 GCD 將斜率存為唯一字串鍵值 `"dy/dx"`。

### 3. Hard: Rectangle Area II (矩形面積 II)
*   **Concept:** Coordinate Compression + Sweep Line (or Segment Tree).
*   **Hint:** Collect all unique x-coordinates and sort them to create vertical strips. Iterate through strips; for each strip, calculate the union of y-intervals covered by rectangles active in that x-range.
*   **觀念：** 座標壓縮 + 掃描線（或線段樹）。
*   **提示：** 收集所有唯一的 x 座標並排序以建立垂直條帶。遍歷條帶；對於每個條帶，計算在該 x 範圍內活動的矩形所覆蓋的 y 區間聯集。

---

## 8. Checklists (快速檢核表)

*   [ ] **Zero Division:** Did I handle `x2 - x1 == 0` when calculating slope?
    **除以零：** 計算斜率時是否處理了 `x2 - x1 == 0`？
*   [ ] **Integer Overflow:** Are intermediate products (like in cross product) exceeding $2^{31}-1$? (JS uses doubles safely up to $2^{53}$, but be aware in other languages).
    **整數溢位：** 中間乘積（如外積）是否超過 $2^{31}-1$？（JS 使用雙精度可安全至 $2^{53}$，但在其他語言需注意）。
*   [ ] **Collinear Points:** Does my Convex Hull logic handle points lying on the same line correctly (keep or discard)?
    **共線點：** 我的凸包邏輯是否正確處理位於同一直線上的點（保留或丟棄）？
*   [ ] **Negative Modulo:** Did I fix the JS `%` operator behavior for negative numbers?
    **負數模運算：** 我是否修正了 JS `%` 運算符對負數的行為？

---

## 9. Memory Anchors (記憶錨點)

*   **Cross Product = Steering Wheel:**
    **外積 = 方向盤：**
    Imagine driving from $O$ to $A$. To get to $B$, do you turn the steering wheel **Left (Positive)** or **Right (Negative)**?
    想像從 $O$ 開車到 $A$。要到達 $B$，你是將方向盤**向左轉（正）**還是**向右轉（負）**？

*   **GCD = Reducing Fractions:**
    **GCD = 約分：**
    Think of GCD not just as a math function, but as the tool to normalize any ratio (slope, aspect ratio) to its canonical form.
    不要只把 GCD 當作數學函式，把它想成將任何比例（斜率、長寬比）標準化為其規範形式的工具。

*   **Convex Hull = Rubber Band:**
    **凸包 = 橡皮筋：**
    Imagine stretching a rubber band around a set of nails (points). When released, it snaps to the outermost nails—that's the hull.
    想像將橡皮筋撐開包住一組釘子（點）。鬆手後，它會彈回並貼緊最外層的釘子——這就是凸包。