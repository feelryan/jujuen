Here is the comprehensive interview preparation guide for **Graphs (Beginner Level)**, tailored for a Senior Software Engineer using C++.
這是一份針對 **圖論（初階）** 的完整面試準備指南，專為使用 C++ 的資深軟體工程師量身打造。

---

# Module: Graph Fundamentals (Beginner)
# 模組：圖論基礎（初階）

## 1. Learning Objectives (學習目標)

1.  **Master Graph Representations:** Proficiently implement Adjacency Matrix and Adjacency List in C++, understanding the memory and performance trade-offs.
    **掌握圖的表示法：** 熟練地在 C++ 中實作鄰接矩陣（Adjacency Matrix）與鄰接表（Adjacency List），並理解記憶體與效能的權衡。
2.  **Internalize Traversal Algorithms:** Implement BFS and DFS (both recursive and iterative) without hesitation, serving as the skeleton for complex problems.
    **內化遍歷演算法：** 毫不猶豫地實作 BFS 和 DFS（包含遞迴與迭代版本），作為解決複雜問題的骨架。
3.  **Recognize Connected Components:** Learn to identify isolated sub-graphs using "Flood Fill" logic, a common pattern in matrix-based graph problems.
    **識別連通分量：** 學習使用「泛洪填充（Flood Fill）」邏輯來識別孤立的子圖，這是矩陣類圖論問題中的常見模式。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A graph is a collection of nodes (vertices) and edges connecting them, modeling relationships (dependencies, paths, connections).
圖是由節點（頂點）與連接它們的邊所組成的集合，用於對關係（依賴、路徑、連結）進行建模。

For a Senior Engineer, think of a Graph not just as circles and lines, but as a **state space** where you transition from one state to another.
對於資深工程師而言，不要只把圖看作圓圈和線條，而應將其視為**狀態空間**，你在其中從一個狀態轉移到另一個狀態。

### Representation (表示法)

| Feature | Adjacency Matrix (鄰接矩陣) | Adjacency List (鄰接表) |
| :--- | :--- | :--- |
| **Implementation** | `vector<vector<int>>` (2D Array) | `vector<vector<int>>` or `unordered_map<int, vector<int>>` |
| **Space Complexity** | $O(V^2)$ | $O(V + E)$ |
| **Check Connection** | $O(1)$ | $O(\text{degree of } V)$ |
| **Iterate Neighbors** | $O(V)$ | $O(\text{degree of } V)$ |
| **Best For** | Dense graphs, small $V$, weighted edges | Sparse graphs, most interview problems |

### Complexity (複雜度)
*   **Time:** BFS/DFS takes $O(V + E)$ using Adjacency List; $O(V^2)$ using Adjacency Matrix.
    **時間：** 使用鄰接表時，BFS/DFS 耗時 $O(V + E)$；使用鄰接矩陣時則為 $O(V^2)$。
*   **Space:** $O(V)$ for `visited` array and recursion stack/queue.
    **空間：** `visited` 陣列與遞迴堆疊/佇列需要 $O(V)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Depth-First Search (DFS)
**Core Idea:** Explore as deep as possible along each branch before backtracking.
**核心概念：** 沿著每個分支盡可能深入探索，然後再回溯。
**Use Cases:** Finding all paths, cycle detection, topological sort, solving mazes.
**適用場景：** 尋找所有路徑、環檢測、拓撲排序、解迷宮。

### Pattern 2: Breadth-First Search (BFS)
**Core Idea:** Explore neighbor nodes first, before moving to the next level neighbors.
**核心概念：** 先探索鄰居節點，再移動到下一層的鄰居。
**Use Cases:** Shortest path in unweighted graphs, level-order traversal, connected components.
**適用場景：** 無權圖的最短路徑、層序遍歷、連通分量。

---

## 4. Example Walkthrough (範例講解)

### Problem: Number of Islands (LeetCode 200)
**問題：島嶼數量**

**Problem Statement:**
Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.
給定一個 `m x n` 的二維二元網格 `grid`，其中 `'1'` 代表陸地，`'0'` 代表水域，請回傳島嶼的數量。

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.
島嶼被水包圍，由水平或垂直相鄰的陸地連接而成。

### Approach (思路)

1.  **Brute Force (Not applicable):** We must traverse the grid.
    **暴力解（不適用）：** 我們必須遍歷網格。
2.  **Optimization (Traversal + Marking):**
    **優化（遍歷 + 標記）：**
    *   Iterate through every cell in the grid.
        遍歷網格中的每一個格子。
    *   If we encounter a `'1'`, it is a new island. Increment count.
        如果遇到 `'1'`，這是一個新島嶼。計數加一。
    *   Trigger a traversal (DFS or BFS) to "sink" the island (mark all connected `'1'`s as `'0'` or visited) so we don't count them again.
        觸發一次遍歷（DFS 或 BFS）來「沉沒」這座島嶼（將所有相連的 `'1'` 標記為 `'0'` 或已訪問），以免重複計算。

### C++ Reference Solution (DFS Approach)
**C++ 參考解答（DFS 解法）**

```cpp
#include <vector>

class Solution {
public:
    // Main function to count islands
    // 計算島嶼數量的主函數
    int numIslands(std::vector<std::vector<char>>& grid) {
        if (grid.empty() || grid[0].empty()) return 0;

        int rows = grid.size();
        int cols = grid[0].size();
        int count = 0;

        // Iterate through every cell
        // 遍歷每一個格子
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                // If we find land, it's a root of a new island
                // 如果發現陸地，它是一個新島嶼的根
                if (grid[i][j] == '1') {
                    count++;
                    // Start DFS to mark the entire island
                    // 開始 DFS 以標記整座島嶼
                    dfs(grid, i, j);
                }
            }
        }
        return count;
    }

private:
    // Helper function for Depth First Search
    // 深度優先搜尋的輔助函數
    void dfs(std::vector<std::vector<char>>& grid, int r, int c) {
        int rows = grid.size();
        int cols = grid[0].size();

        // Boundary checks and water check
        // 邊界檢查與水域檢查
        // If out of bounds or is water ('0'), stop recursion
        // 如果超出邊界或是水域 ('0')，停止遞迴
        if (r < 0 || c < 0 || r >= rows || c >= cols || grid[r][c] == '0') {
            return;
        }

        // Mark current cell as visited (turn land to water)
        // 將當前格子標記為已訪問（將陸地變為水域）
        // This avoids using a separate 'visited' matrix, saving space
        // 這避免了使用額外的 'visited' 矩陣，節省空間
        grid[r][c] = '0';

        // Visit all 4 adjacent directions
        // 訪問所有 4 個相鄰方向
        dfs(grid, r - 1, c); // Up (上)
        dfs(grid, r + 1, c); // Down (下)
        dfs(grid, r, c - 1); // Left (左)
        dfs(grid, r, c + 1); // Right (右)
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time Complexity:** $O(M \times N)$. Each cell is visited at most once by the outer loop and once by the DFS.
    **時間複雜度：** $O(M \times N)$。每個格子最多被外層迴圈訪問一次，並被 DFS 訪問一次。
*   **Space Complexity:** $O(M \times N)$ in the worst case (if the entire grid is one island, the recursion stack depth is $M \times N$).
    **空間複雜度：** 最壞情況下為 $O(M \times N)$（如果整個網格是一座島嶼，遞迴堆疊深度為 $M \times N$）。

### Common Mistake (錯誤示範)
*   **Mistake:** Forgetting to mark the node as visited *before* making recursive calls.
    **錯誤：** 忘記在進行遞迴呼叫*之前*將節點標記為已訪問。
*   **Why wrong:** This leads to infinite recursion (stack overflow) as the algorithm bounces back and forth between two adjacent `'1'`s.
    **為何錯誤：** 這會導致無限遞迴（堆疊溢位），因為演算法會在兩個相鄰的 `'1'` 之間來回跳動。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Graph vs. Tree** | **圖 vs. 樹** | A tree is a connected graph with **no cycles** and $N-1$ edges. A graph can have cycles and disconnected parts. <br> 樹是**沒有環**且有 $N-1$ 條邊的連通圖。圖可以有環和不連通的部分。 |
| **DFS (Stack)** | **BFS (Queue)** | DFS goes deep (good for path existence); BFS goes wide (good for shortest path in unweighted graphs). <br> DFS 深入（適合路徑存在性）；BFS 廣度（適合無權圖最短路徑）。 |
| **Visited Array** | **In-place Modification** | Using a separate `visited` array preserves the original input but costs $O(V)$ space. Modifying input saves space but destroys data. <br> 使用獨立的 `visited` 陣列保留原始輸入但消耗 $O(V)$ 空間。修改輸入節省空間但會破壞資料。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (闡述口條框架)
1.  **Clarify Graph Type:** "Is the graph directed or undirected? Weighted or unweighted? Are there cycles? Is it guaranteed to be connected?"
    **釐清圖的類型：** 「是有向圖還是無向圖？有權還是無權？有環嗎？保證是連通的嗎？」
2.  **Define Representation:** "Since $N$ is up to 10,000, I will use an Adjacency List to optimize space."
    **定義表示法：** 「由於 $N$ 高達 10,000，我將使用鄰接表來優化空間。」
3.  **State Algorithm:** "I will use BFS here because we are looking for the shortest path in an unweighted graph."
    **說明演算法：** 「我會在這裡使用 BFS，因為我們正在尋找無權圖中的最短路徑。」

### Whiteboard Strategy (白板策略)
*   **Draw a small example:** Draw 3-4 nodes with edges. Trace your algorithm manually before coding.
    **畫一個小範例：** 畫出 3-4 個節點及其邊。在寫程式碼之前手動追蹤你的演算法。
*   **Modularize:** Write `bfs()` or `dfs()` as a helper function. This keeps the main logic clean.
    **模組化：** 將 `bfs()` 或 `dfs()` 寫成輔助函數。這能保持主邏輯清晰。

### Common Follow-up (常見追問)
*   **Q:** What if the graph is too large to fit in memory?
    **問：** 如果圖太大無法放入記憶體怎麼辦？
*   **A:** Discuss distributed graph processing (e.g., MapReduce, Spark) or storing the graph in a database/disk and loading chunks.
    **答：** 討論分散式圖處理（如 MapReduce, Spark）或將圖儲存在資料庫/磁碟中並分塊載入。

---

## 7. Practice Problems (練習題)

### Easy: Find if Path Exists in Graph (LC 1971)
*   **Prompt:** Given edges and `n` nodes, determine if there is a valid path from `source` to `destination`.
    **題目：** 給定邊和 `n` 個節點，判斷是否存在從 `source` 到 `destination` 的有效路徑。
*   **Hint:** Build an adjacency list. Run DFS/BFS starting from `source`. If you encounter `destination`, return `true`.
    **提示：** 建立鄰接表。從 `source` 開始執行 DFS/BFS。如果遇到 `destination`，回傳 `true`。

### Medium: Clone Graph (LC 133)
*   **Prompt:** Return a deep copy of a connected undirected graph.
    **題目：** 回傳一個連通無向圖的深拷貝。
*   **Hint:** Use a Hash Map `unordered_map<Node*, Node*>` to map original nodes to their clones. DFS/BFS to traverse; if a node is in the map, link it; if not, create it.
    **提示：** 使用雜湊表 `unordered_map<Node*, Node*>` 將原始節點映射到其複製節點。使用 DFS/BFS 遍歷；如果節點在表中，則連結它；如果不在，則建立它。

### Medium/Hard (Conceptual): Course Schedule (LC 207)
*   **Prompt:** Can you finish all courses given prerequisites? (Detect Cycle in Directed Graph).
    **題目：** 給定先修條件，你能完成所有課程嗎？（有向圖環檢測）。
*   **Hint:** This is a "Topological Sort" precursor. Use DFS with 3 states (0=unvisited, 1=visiting, 2=visited). If you meet a node in state 1, there is a cycle.
    **提示：** 這是「拓撲排序」的前身。使用具有 3 種狀態的 DFS（0=未訪問，1=訪問中，2=已訪問）。如果遇到狀態 1 的節點，則存在環。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Visited Set:** Did I initialize a `visited` array/set to prevent infinite loops?
    **已訪問集合：** 我是否初始化了 `visited` 陣列/集合以防止無限迴圈？
*   [ ] **Boundary Checks:** (For Grid problems) Did I check `r < 0`, `c < 0`, `r >= rows`, `c >= cols`?
    **邊界檢查：** （針對網格問題）我是否檢查了 `r < 0`, `c < 0`, `r >= rows`, `c >= cols`？
*   [ ] **Graph Construction:** Did I correctly handle undirected edges (add connection both ways)?
    **圖的建構：** 我是否正確處理了無向邊（雙向添加連接）？
*   [ ] **Corner Cases:** Did I handle $N=0$ or disconnected graphs?
    **邊界情況：** 我是否處理了 $N=0$ 或不連通圖？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **BFS is like a Ripple (水波紋):**
    Imagine dropping a stone in a pond. The waves expand layer by layer. This is why it finds the shortest path (nearest layer first).
    **BFS 就像水波紋：** 想像將石頭丟入池塘。波浪一層一層向外擴展。這就是為什麼它能找到最短路徑（先到達最近的一層）。

*   **DFS is like a Maze Runner (迷宮跑者):**
    You keep running down a path until you hit a wall, then you backtrack to the last junction and try a different path.
    **DFS 就像迷宮跑者：** 你沿著一條路一直跑，直到撞到牆，然後回溯到上一個路口並嘗試另一條路。