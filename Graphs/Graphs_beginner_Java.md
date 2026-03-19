Here is the comprehensive guide on **Graphs (Beginner Level)**, tailored for Senior Software Engineers preparing for Big Tech interviews.
這是一份針對 **圖論（入門級）** 的完整指南，專為準備大型科技公司面試的資深軟體工程師量身打造。

---

# Graph Algorithms: The Foundation (Beginner)
# 圖演算法：基礎篇（入門）

## 1. Learning Goals（學習目標）

*   **Master Graph Representations:** Understand the trade-offs between Adjacency Matrix and Adjacency List, and implement them in Java.
    **掌握圖的表示法：** 理解鄰接矩陣（Adjacency Matrix）與鄰接表（Adjacency List）之間的權衡，並能以 Java 實作。
*   **Internalize Traversal Algorithms:** deeply understand BFS (Breadth-First Search) and DFS (Depth-First Search), including their iterative and recursive implementations.
    **內化遍歷演算法：** 深度理解廣度優先搜尋（BFS）與深度優先搜尋（DFS），包含其迭代與遞迴實作。
*   **Analyze Complexity Correctly:** Be able to derive $O(V + E)$ time complexity and explain space complexity nuances.
    **正確分析複雜度：** 能夠推導出 $O(V + E)$ 的時間複雜度，並解釋空間複雜度的細微差別。
*   **Identify Implicit Graphs:** Recognize graph problems disguised as 2D grids or state transition problems.
    **識別隱式圖：** 能夠辨識偽裝成二維網格或狀態轉移問題的圖論題目。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
A Graph consists of vertices (nodes) and edges connecting them.
圖由頂點（節點）與連接它們的邊組成。
Think of it as a network: nodes are cities, edges are roads.
可以將其想像成一個網絡：節點是城市，邊是道路。

### Key Terminology（關鍵術語）
*   **Directed vs. Undirected:** One-way streets vs. two-way roads.
    **有向 vs. 無向：** 單行道 vs. 雙向道。
*   **Weighted vs. Unweighted:** Roads with toll costs/distances vs. all roads being equal.
    **有權 vs. 無權：** 帶有過路費/距離的道路 vs. 所有道路權重相等。
*   **Cyclic vs. Acyclic:** Can you loop back to the start?
    **有環 vs. 無環：** 你能否繞回起點？

### Representation（表示法）

1.  **Adjacency List (Map/List of Lists):**
    *   Space: $O(V + E)$. Best for sparse graphs.
    *   空間：$O(V + E)$。最適合稀疏圖。
2.  **Adjacency Matrix (2D Array):**
    *   Space: $O(V^2)$. Good for dense graphs or quick edge lookups ($O(1)$).
    *   空間：$O(V^2)$。適合稠密圖或快速查詢邊的存在 ($O(1)$)。

### Complexity（複雜度）
*   **Time:** $O(V + E)$ for standard traversals (visiting every node and edge once).
    **時間：** 標準遍歷為 $O(V + E)$（訪問每個節點與邊一次）。
*   **Space:** $O(V)$ for `visited` array and recursion stack/queue.
    **空間：** $O(V)$ 用於 `visited` 陣列與遞迴堆疊/佇列。

### When to Use（適用場景）
*   Finding connectivity (Is there a path?).
    尋找連通性（是否存在路徑？）。
*   Shortest path in unweighted graphs (BFS).
    無權圖中的最短路徑（BFS）。
*   Topological sorting (dependencies).
    拓撲排序（依賴關係）。

### When NOT to Use（不適用場景）
*   Simple linear data access (use Array/LinkedList).
    簡單的線性資料存取（使用 Array/LinkedList）。
*   Key-value lookups without relationships (use HashMap).
    沒有關聯性的鍵值查詢（使用 HashMap）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern 1: Breadth-First Search (BFS)
**Best for:** Shortest path in unweighted graphs, level-order traversal.
**適用於：** 無權圖的最短路徑、層序遍歷。
**Data Structure:** Queue (FIFO).
**資料結構：** 佇列（先進先出）。

### Pattern 2: Depth-First Search (DFS)
**Best for:** Exhaustive search, backtracking, checking connectivity, cycle detection.
**適用於：** 窮舉搜尋、回溯法、檢查連通性、環檢測。
**Data Structure:** Stack (LIFO) or Recursion.
**資料結構：** 堆疊（後進先出）或遞迴。

### Pattern 3: Matrix as a Graph (Flood Fill)
**Concept:** Each cell `(r, c)` is a node; adjacent cells are neighbors.
**觀念：** 每個格子 `(r, c)` 是一個節點；相鄰的格子是鄰居。
**Technique:** Use a `directions` array to navigate neighbors.
**技巧：** 使用 `directions` 陣列來導航鄰居。

---

## 4. Example Walkthrough（範例講解）

### Problem: Number of Islands（島嶼數量）
*(LeetCode 200 - Classic Beginner/Intermediate Graph Problem)*

#### Problem Statement（問題重述）
Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.
給定一個 `m x n` 的二維二元網格 `grid`，其中 `'1'` 代表陸地，`'0'` 代表水域，請回傳島嶼的數量。
An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.
島嶼被水包圍，由水平或垂直相鄰的陸地連接而成。

#### Approach: From Brute Force to Optimal（思路：暴力 → 優化 → 最佳解）

1.  **Intuition:** We need to find connected components of `'1'`s.
    **直覺：** 我們需要找出 `'1'` 的連通分量。
2.  **Strategy:** Iterate through every cell. If we find a `'1'`, increment the count and trigger a traversal (DFS or BFS) to "sink" (mark as visited) the entire island so we don't count it again.
    **策略：** 遍歷每個格子。如果發現 `'1'`，計數加一，並觸發遍歷（DFS 或 BFS）將整座島嶼「沉沒」（標記為已訪問），以免重複計算。
3.  **Optimization:** Instead of using a separate `visited` set (Space $O(M \times N)$), we can modify the input grid directly by turning `'1'` to `'0'` (or `'#'`) upon visiting.
    **優化：** 不使用額外的 `visited` 集合（空間 $O(M \times N)$），我們可以直接修改輸入網格，在訪問時將 `'1'` 變為 `'0'`（或 `'#'`）。

#### Java Solution (DFS Approach)
*Note: DFS is often preferred in interviews for this problem due to shorter code length than BFS.*
*註：由於程式碼較短，面試中通常首選 DFS 來解決此問題。*

```java
class Solution {
    // Directions array for moving up, down, left, right
    // 用於上下左右移動的方向陣列
    private static final int[][] DIRECTIONS = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};

    public int numIslands(char[][] grid) {
        // Edge case check
        // 邊界條件檢查
        if (grid == null || grid.length == 0) {
            return 0;
        }

        int rows = grid.length;
        int cols = grid[0].length;
        int count = 0;

        // Iterate through every cell in the grid
        // 遍歷網格中的每個格子
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                // If we encounter land, it's a new island
                // 如果遇到陸地，這是一個新島嶼
                if (grid[r][c] == '1') {
                    count++;
                    // Start DFS to mark all connected land
                    // 開始 DFS 以標記所有相連的陸地
                    dfs(grid, r, c, rows, cols);
                }
            }
        }
        return count;
    }

    private void dfs(char[][] grid, int r, int c, int rows, int cols) {
        // Base cases for recursion:
        // 1. Out of bounds
        // 2. Water ('0') or already visited
        // 遞迴的基本情況：
        // 1. 超出邊界
        // 2. 是水域 ('0') 或已訪問過
        if (r < 0 || c < 0 || r >= rows || c >= cols || grid[r][c] == '0') {
            return;
        }

        // Mark current cell as visited (sink the island)
        // 將當前格子標記為已訪問（讓島嶼沉沒）
        grid[r][c] = '0';

        // Visit all 4 neighbors
        // 訪問所有 4 個鄰居
        for (int[] dir : DIRECTIONS) {
            int newRow = r + dir[0];
            int newCol = c + dir[1];
            dfs(grid, newRow, newCol, rows, cols);
        }
    }
}
```

#### Complexity Analysis（複雜度分析）
*   **Time:** $O(M \times N)$. Every cell is visited at most once.
    **時間：** $O(M \times N)$。每個格子最多被訪問一次。
*   **Space:** $O(M \times N)$ in the worst case (grid full of land) due to recursion stack.
    **空間：** 最壞情況下（網格全為陸地）為 $O(M \times N)$，源於遞迴堆疊。

#### Common Mistakes（錯誤示範 & 為何錯）
*   **Mistake:** Forgetting to mark the cell as visited *before* recursive calls.
    **錯誤：** 忘記在遞迴呼叫 *之前* 將格子標記為已訪問。
    *   **Consequence:** Infinite recursion (StackOverflowError).
    *   **後果：** 無窮遞迴（堆疊溢位錯誤）。
*   **Mistake:** Using BFS but marking visited *after* popping from queue.
    **錯誤：** 使用 BFS 但在從佇列 *取出後* 才標記已訪問。
    *   **Consequence:** Nodes are added to the queue multiple times, degrading performance to exponential or TLE.
    *   **後果：** 節點被多次加入佇列，效能退化至指數級或超時（TLE）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **DFS** | **Backtracking** | DFS is a traversal strategy; Backtracking is DFS *with state reset* (undoing choices). <br> DFS 是遍歷策略；回溯法是 *帶有狀態重置* 的 DFS（撤銷選擇）。 |
| **Connected** | **Strongly Connected** | "Connected" is for undirected graphs (path between any two nodes). "Strongly Connected" is for directed graphs (path $A \to B$ AND $B \to A$). <br> 「連通」用於無向圖；「強連通」用於有向圖（$A \to B$ 且 $B \to A$）。 |
| **Visited Array** | **Recursion Stack** | Visited array prevents cycles/re-processing. Recursion stack tracks the current path. <br> Visited 陣列防止環/重複處理。遞迴堆疊追蹤當前路徑。 |

---

## 6. Interview Strategy（面試實戰建議）

### Framework（口條框架）
1.  **Clarify Graph Type:** "Is this directed or undirected? Are there weights? Can there be cycles?"
    **釐清圖的類型：** 「這是有向圖還是無向圖？有權重嗎？會有環嗎？」
2.  **Choose Representation:** "Since the input is a grid, I will treat it as an implicit graph." or "I'll build an adjacency list for efficient traversal."
    **選擇表示法：** 「因為輸入是網格，我會將其視為隱式圖。」或「我會建立鄰接表以利高效遍歷。」
3.  **State Algorithm:** "I will use BFS to find the shortest path because it guarantees the optimal solution in an unweighted graph."
    **陳述演算法：** 「我會使用 BFS 來尋找最短路徑，因為它保證了無權圖中的最佳解。」

### Whiteboard Strategy（白板策略）
*   **Define Directions:** Always write `int[][] dirs = {{0,1}, {0,-1}, ...}` first for grid problems. It keeps code clean.
    **定義方向：** 處理網格問題時，總是先寫下 `dirs` 陣列。這能保持程式碼整潔。
*   **Modularize:** If the logic is complex, write a helper function `getNeighbors(node)`.
    **模組化：** 如果邏輯複雜，寫一個輔助函式 `getNeighbors(node)`。

### Follow-up Questions（常見追問）
*   "What if the grid is too large to fit in memory?" (Answer: Process in chunks or assume stream of edges).
    「如果網格太大無法放入記憶體怎麼辦？」（答：分塊處理或假設是邊的串流）。
*   "How would you handle it if we allow diagonal movement?" (Answer: Update `directions` array to size 8).
    「如果允許對角線移動怎麼處理？」（答：將 `directions` 陣列更新為 8 個方向）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Find if Path Exists in Graph
*   **Prompt:** Given `n` nodes and edges, determine if there is a valid path from `source` to `destination`.
    **題目：** 給定 `n` 個節點與邊，判斷是否存在從 `source` 到 `destination` 的有效路徑。
*   **Hint:** Use DFS or BFS. Maintain a `visited` set. If you reach `destination`, return `true`.
    **提示：** 使用 DFS 或 BFS。維護一個 `visited` 集合。如果到達 `destination`，回傳 `true`。

### 2. Medium: Clone Graph
*   **Prompt:** Deep copy a connected undirected graph.
    **題目：** 深拷貝一個連通無向圖。
*   **Hint:** Use a `HashMap<Node, Node>` to map original nodes to their clones. Use DFS/BFS to traverse and link clones.
    **提示：** 使用 `HashMap<Node, Node>` 將原始節點映射到其複製節點。使用 DFS/BFS 遍歷並連接複製節點。

### 3. Medium (Borderline Hard for Beginner): Course Schedule
*   **Prompt:** Can you finish all courses given prerequisites? (Cycle Detection).
    **題目：** 給定先修條件，能否修完所有課程？（環檢測）。
*   **Hint:** This is a directed graph. Use DFS with 3 states (unvisited, visiting, visited) to detect cycles, or use Kahn's Algorithm (Topological Sort).
    **提示：** 這是有向圖。使用帶有 3 種狀態（未訪問、訪問中、已訪問）的 DFS 來檢測環，或使用 Kahn 演算法（拓撲排序）。

---

## 8. Quick Checklists（快速檢核表）

### Debugging / Self-Review
- [ ] **Visited Set:** Did I mark nodes as visited? (Avoid infinite loops).
      **Visited 集合：** 我有標記節點為已訪問嗎？（避免無窮迴圈）。
- [ ] **Base Cases:** Did I handle out-of-bounds (grid) or null nodes?
      **基本情況：** 我有處理越界（網格）或空節點嗎？
- [ ] **Connectivity:** Did I handle the case where the graph is disconnected? (Outer loop iterating over all nodes).
      **連通性：** 我有處理圖不連通的情況嗎？（外層迴圈遍歷所有節點）。
- [ ] **BFS Queue:** Am I marking visited *when pushing* to queue (correct) or *when popping* (slow/wrong)?
      **BFS 佇列：** 我是在 *加入* 佇列時標記已訪問（正確），還是在 *取出* 時標記（慢/錯誤）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **DFS is a Maze Runner:** You touch the wall with your right hand and keep walking until you hit a dead end, then backtrack.
    **DFS 是迷宮跑者：** 你用右手摸著牆壁一直走，直到遇到死路，然後往回走。
*   **BFS is a Ripple:** Like throwing a stone in a pond. The water expands in concentric circles (layers) equally in all directions.
    **BFS 是漣漪：** 就像往池塘丟一顆石頭。水波以同心圓（層）的方式向所有方向等距擴散。
*   **Visited Set is Ariadne's Thread:** It leaves a trail so you don't walk in circles forever.
    **Visited 集合是阿里阿德涅之線：** 它留下了痕跡，讓你不至於永遠在圈子裡打轉。