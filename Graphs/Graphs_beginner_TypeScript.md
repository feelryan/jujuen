Here is the comprehensive guide for **Graphs (Beginner Level)**, tailored for Senior Software Engineers preparing for Big Tech interviews.
這是一份針對 **圖論（初級）** 的完整指南，專為準備 Big Tech 面試的資深軟體工程師量身打造。

---

# Module: Graphs (Beginner)
# 模組：圖論（初級）

## 1. Learning Objectives（學習目標）

1.  **Master Graph Representations:** Understand the trade-offs between Adjacency Matrix and Adjacency List in terms of memory and lookup speed.
    **掌握圖的表示法：** 理解「鄰接矩陣」與「鄰接表」在記憶體與查詢速度上的權衡。
2.  **Internalize Traversal Algorithms:** deeply understand BFS (Queue-based) and DFS (Recursion/Stack-based) and when to use which.
    **內化遍歷演算法：** 深刻理解 BFS（基於佇列）與 DFS（基於遞迴/堆疊）及其適用時機。
3.  **Recognize Implicit Graphs:** Learn to identify graph problems disguised as 2D grids or state transitions.
    **識別隱式圖：** 學會辨識偽裝成 2D 網格或狀態轉移的圖論問題。
4.  **Handle Cycles and Disconnected Components:** Correctly manage `visited` states to prevent infinite loops.
    **處理環與非連通分量：** 正確管理 `visited`（已訪問）狀態以防止無窮迴圈。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
A Graph is a collection of nodes (vertices) and edges connecting them.
圖是由節點（頂點）與連接它們的邊所組成的集合。

It models relationships: $G = (V, E)$.
它模擬了關係：$G = (V, E)$。

### Key Types（關鍵類型）
*   **Directed vs. Undirected:** One-way street vs. two-way street.
    **有向 vs. 無向：** 單行道 vs. 雙向道。
*   **Weighted vs. Unweighted:** Edges have cost (distance, price) vs. uniform cost.
    **有權 vs. 無權：** 邊具有成本（距離、價格） vs. 成本一致。
*   **Cyclic vs. Acyclic:** Contains a loop vs. tree-like structure (DAG).
    **有環 vs. 無環：** 包含迴圈 vs. 樹狀結構（有向無環圖 DAG）。

### Complexity（複雜度）
*   **Time:** $O(V + E)$ for standard traversals (visiting every node and edge once).
    **時間：** 標準遍歷為 $O(V + E)$（訪問每個節點與邊各一次）。
*   **Space:** $O(V)$ to store visited states or recursion stack.
    **空間：** $O(V)$ 用於儲存已訪問狀態或遞迴堆疊。

### When to Use / Not Use（適用與不適用場景）
*   **Use for:** Network routing, social connections, dependency resolution, puzzle solving (shortest path).
    **適用於：** 網路路由、社交連結、依賴解析、解謎（最短路徑）。
*   **Not Use for:** Simple linear data storage or fast random access by index (use Arrays/HashMaps).
    **不適用於：** 簡單的線性資料儲存或依索引快速隨機存取（使用陣列/雜湊表）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern 1: Breadth-First Search (BFS)
**Best for:** Finding the **shortest path** in an unweighted graph.
**最適合：** 在無權圖中尋找**最短路徑**。
**Mechanism:** Level-by-level expansion using a `Queue` (FIFO).
**機制：** 使用 `Queue`（先進先出）進行層級式擴展。

### Pattern 2: Depth-First Search (DFS)
**Best for:** Exhausting possibilities, checking connectivity, or cycle detection.
**最適合：** 窮舉可能性、檢查連通性或檢測環。
**Mechanism:** Go deep before going wide using `Recursion` or a `Stack` (LIFO).
**機制：** 使用 `Recursion` 或 `Stack`（後進先出），在變寬之前先深入。

### Pattern 3: Matrix Traversal (Flood Fill)
**Best for:** Grid-based problems (islands, mazes).
**最適合：** 基於網格的問題（島嶼、迷宮）。
**Mechanism:** Treat each cell `(r, c)` as a node, and adjacent cells as neighbors.
**機制：** 將每個單元格 `(r, c)` 視為節點，相鄰單元格視為鄰居。

---

## 4. Example Walkthrough（範例講解）

### Problem: Number of Islands (LeetCode 200)
**Problem Statement:** Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.
**問題重述：** 給定一個 `m x n` 的二維二進位網格 `grid`，代表 `'1'`（陸地）和 `'0'`（水），請回傳島嶼的數量。

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.
島嶼被水包圍，由水平或垂直相鄰的陸地連接而成。

### Approach: From Brute Force to Optimal（思路：暴力 → 優化 → 最佳解）

1.  **Intuition:** We need to find connected components of `'1'`s.
    **直覺：** 我們需要找出 `'1'` 的連通分量。
2.  **Strategy:** Iterate through every cell. If we see a `'1'`, it's a new island. Increment count, then "sink" the entire island (turn `'1'` to `'0'`) using DFS or BFS so we don't count it again.
    **策略：** 遍歷每個單元格。如果看到 `'1'`，這是一個新島嶼。增加計數，然後使用 DFS 或 BFS「沉沒」整個島嶼（將 `'1'` 變為 `'0'`），以免重複計算。
3.  **Optimization:** Modifying the input grid saves $O(V)$ space (no `visited` set needed). If input modification is forbidden, use a `Set<string>` or a boolean matrix.
    **優化：** 修改輸入網格可節省 $O(V)$ 空間（不需要 `visited` 集合）。如果禁止修改輸入，則使用 `Set<string>` 或布林矩陣。

### TypeScript Solution (DFS Approach)

```typescript
/**
 * Calculates the number of islands in a grid.
 * 計算網格中的島嶼數量。
 * 
 * Time Complexity: O(M * N) - We visit each cell at most once.
 * 時間複雜度：O(M * N) - 我們最多訪問每個單元格一次。
 * Space Complexity: O(M * N) - Worst case recursion stack (if the whole grid is land).
 * 空間複雜度：O(M * N) - 最壞情況下的遞迴堆疊（如果整個網格都是陸地）。
 */
function numIslands(grid: string[][]): number {
    if (!grid || grid.length === 0) return 0;

    const rows = grid.length;
    const cols = grid[0].length;
    let count = 0;

    // Helper function for DFS traversal
    // DFS 遍歷的輔助函式
    const dfs = (r: number, c: number) => {
        // Base Case: Check boundaries and if it is water
        // 基本情況：檢查邊界以及是否為水
        if (
            r < 0 || 
            c < 0 || 
            r >= rows || 
            c >= cols || 
            grid[r][c] === '0'
        ) {
            return;
        }

        // Mark as visited by sinking the island (changing '1' to '0')
        // 透過沉沒島嶼（將 '1' 改為 '0'）標記為已訪問
        grid[r][c] = '0';

        // Visit all 4 adjacent directions
        // 訪問所有 4 個相鄰方向
        dfs(r + 1, c); // Down (下)
        dfs(r - 1, c); // Up (上)
        dfs(r, c + 1); // Right (右)
        dfs(r, c - 1); // Left (左)
    };

    // Iterate through every cell in the grid
    // 遍歷網格中的每個單元格
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            // If we find a piece of land, it's a new island
            // 如果我們發現一塊陸地，它就是一個新島嶼
            if (grid[r][c] === '1') {
                count++;
                // Start DFS to mark the entire island
                // 啟動 DFS 以標記整個島嶼
                dfs(r, c); 
            }
        }
    }

    return count;
}
```

### Why this works (為何有效)
It guarantees every node in a connected component is visited exactly once via the recursive calls triggered by the main loop.
它保證透過主迴圈觸發的遞迴呼叫，連通分量中的每個節點恰好被訪問一次。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Pitfall / Confusion (陷阱/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **BFS Queue** | Adding to `visited` when **popping** from queue. <br> 在從佇列 **取出** 時才加入 `visited`。 | **WRONG.** Add to `visited` when **pushing** to queue to avoid duplicates. <br> **錯誤。** 應在 **推入** 佇列時加入，以避免重複處理。 |
| **DFS Recursion** | Forgetting base cases (boundary checks). <br> 忘記基本情況（邊界檢查）。 | Causes Stack Overflow. Always check bounds first. <br> 導致堆疊溢位。務必先檢查邊界。 |
| **Graph vs Tree** | Assuming no cycles. <br> 假設沒有環。 | Graphs can have cycles; Trees cannot. Always track `visited` in graphs. <br> 圖可能有環；樹沒有。在圖中務必追蹤 `visited`。 |
| **Shortest Path** | Using DFS for shortest path. <br> 使用 DFS 尋找最短路徑。 | DFS does not guarantee shortest path. Use BFS for unweighted graphs. <br> DFS 不保證最短路徑。無權圖請使用 BFS。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarify Input Format (釐清輸入格式)
*   "Is the graph given as an adjacency list, matrix, or a list of edges?"
    「圖是以鄰接表、矩陣還是邊的列表形式給出的？」
*   "Is it directed or undirected? Weighted or unweighted?"
    「是有向還是無向？有權還是無權？」

### 2. Whiteboard Strategy (白板策略)
*   **Draw it out:** Draw a small example (nodes and edges) to visualize connections.
    **畫出來：** 畫一個小範例（節點和邊）來視覺化連接。
*   **Define State:** Explicitly write down what `visited` means.
    **定義狀態：** 明確寫下 `visited` 的意義。
*   **Modularize:** Separate the BFS/DFS logic into a helper function (like `getNeighbors` or `traverse`).
    **模組化：** 將 BFS/DFS 邏輯分離到輔助函式中（如 `getNeighbors` 或 `traverse`）。

### 3. Common Follow-ups (常見追問)
*   "What if the grid is too large to fit in memory?" (Answer: Process chunks or iterative DFS).
    「如果網格太大無法放入記憶體怎麼辦？」（答：分塊處理或迭代式 DFS）。
*   "Can you do this without modifying the input?" (Answer: Use a separate `visited` set).
    「能不能在不修改輸入的情況下完成？」（答：使用獨立的 `visited` 集合）。

---

## 7. Practice Problems（練習題）

### Easy: Flood Fill (LeetCode 733)
*   **Prompt:** Change the color of a connected region of pixels.
    **題目：** 改變相連像素區域的顏色。
*   **Hint:** Standard DFS/BFS starting from `(sr, sc)`. Watch out if `newColor` is same as `oldColor`.
    **提示：** 從 `(sr, sc)` 開始的標準 DFS/BFS。注意 `newColor` 是否與 `oldColor` 相同。

### Medium: Clone Graph (LeetCode 133)
*   **Prompt:** Deep copy a connected undirected graph.
    **題目：** 深拷貝一個連通無向圖。
*   **Hint:** Use a HashMap `Map<Node, Node>` to map original nodes to their clones to handle cycles.
    **提示：** 使用 HashMap `Map<Node, Node>` 將原始節點映射到其克隆節點，以處理環。

### Medium/Hard: Word Ladder (LeetCode 127)
*   **Prompt:** Find shortest transformation sequence from `beginWord` to `endWord`.
    **題目：** 找出從 `beginWord` 到 `endWord` 的最短轉換序列。
*   **Hint:** This is a BFS shortest path problem. The "graph" is implicit: words are nodes, edges exist if words differ by 1 char.
    **提示：** 這是 BFS 最短路徑問題。「圖」是隱式的：單字是節點，如果單字相差 1 個字元則存在邊。

---

## 8. Rapid Checklist（快速檢核表）

*   [ ] Did I handle the empty graph case? (e.g., `grid.length == 0`)
    我有處理空圖的情況嗎？
*   [ ] Am I marking nodes as visited **before** processing them (or immediately upon pushing to queue)?
    我是否在處理節點**之前**（或推入佇列時立即）將其標記為已訪問？
*   [ ] For grids, did I check `r < 0`, `c < 0`, `r >= rows`, `c >= cols`?
    對於網格，我有檢查邊界嗎？
*   [ ] Did I confuse BFS (Queue) with DFS (Stack)?
    我有混淆 BFS（佇列）與 DFS（堆疊）嗎？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### DFS is a Maze Runner (DFS 是迷宮跑者)
Imagine a person in a maze keeping their hand on the **left wall**. They keep walking until they hit a dead end, then backtrack to the last junction and try a different path.
想像一個人在迷宮中，手扶著**左側牆壁**。他們一直走到死胡同，然後回溯到上一個路口並嘗試另一條路。

### BFS is a Ripple (BFS 是漣漪)
Imagine dropping a stone in a pond. The water ripples out in **concentric circles**. It touches everything at distance 1, then distance 2, then distance 3.
想像將一塊石頭丟入池塘。水波以**同心圓**向外擴散。它先接觸距離為 1 的所有物體，然後是距離 2，接著是距離 3。