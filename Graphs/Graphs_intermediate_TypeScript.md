Here is the complete interview preparation guide for **Graphs (Intermediate)**, tailored for a Senior Software Engineer.
這是一份針對 **圖論（中級）** 的完整面試準備指南，專為資深軟體工程師量身打造。

---

# Graph Algorithms: Intermediate Level
# 圖論演算法：中級篇

## 1. Learning Objectives (學習目標)

1.  **Master Graph Modeling:** Learn to translate abstract problems (dependencies, state changes, grid maps) into graph representations (nodes and edges).
    **掌握圖的建模：** 學習將抽象問題（依賴關係、狀態變更、網格地圖）轉化為圖的表示形式（節點與邊）。
2.  **Proficiency in Traversal:** Deeply understand BFS and DFS, knowing exactly when to apply each based on requirements (shortest path vs. exhaustive search).
    **精通遍歷：** 深度理解廣度優先搜尋 (BFS) 與深度優先搜尋 (DFS)，並知道如何根據需求（最短路徑 vs. 窮舉搜尋）精準應用。
3.  **Topology & Cycle Detection:** Solve dependency resolution problems using Topological Sort and detect cycles in directed graphs.
    **拓樸與環檢測：** 使用拓樸排序解決依賴解析問題，並在有向圖中檢測環的存在。
4.  **Handling Disconnected Components:** Ensure algorithms work robustly across forests (multiple disconnected subgraphs), not just single connected trees.
    **處理非連通分量：** 確保演算法在森林（多個不相連的子圖）中也能穩健運行，而不僅僅是單一連通樹。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Graph consists of a set of vertices $V$ and a set of edges $E$ connecting them.
圖由一組頂點 $V$ 和一組連接這些頂點的邊 $E$ 組成。

### Representation (表示法)
For interviews, **Adjacency List** is preferred over Adjacency Matrix unless the graph is dense or the problem is on a grid.
在面試中，除非圖非常稠密或是網格類問題，否則**鄰接表 (Adjacency List)** 優於鄰接矩陣 (Adjacency Matrix)。

### Complexity (複雜度)
-   **Time:** $O(V + E)$ for traversal (visiting every node and edge once).
    **時間：** 遍歷為 $O(V + E)$（訪問每個節點與邊各一次）。
-   **Space:** $O(V)$ to store the graph and recursion stack/queue.
    **空間：** $O(V)$ 用於儲存圖結構以及遞迴堆疊/佇列。

### When to Use (適用場景)
-   **Relationships:** Social networks, peer-to-peer networks.
    **關係：** 社交網絡、點對點網絡。
-   **Pathfinding:** Shortest path in unweighted graphs (BFS).
    **路徑搜尋：** 無權重圖中的最短路徑 (BFS)。
-   **Dependencies:** Build systems, course prerequisites (Topological Sort).
    **依賴關係：** 建置系統、課程先修要求（拓樸排序）。

### When NOT to Use (不適用場景)
-   **Simple Linear Data:** If data has no branching or cycles, Arrays or Linked Lists are sufficient.
    **簡單線性資料：** 如果資料沒有分支或環，陣列或鏈結串列就足夠了。
-   **Random Access:** Graphs do not support $O(1)$ access to arbitrary elements without an index map.
    **隨機存取：** 若沒有額外的索引映射，圖不支援 $O(1)$ 的任意元素存取。

---

## 3. Typical Patterns (典型題型 / 模式)

### 1. Grid Traversal (Matrix as Graph) / 網格遍歷（矩陣即圖）
Treating a 2D array as a graph where cells are nodes and neighbors are edges.
將二維陣列視為圖，其中格子是節點，相鄰格子是邊。
*   **Keywords:** Number of Islands, Max Area of Island, Rotting Oranges.

### 2. Connected Components / 連通分量
Finding sets of nodes connected to each other but isolated from others.
尋找彼此相連但與其他部分隔離的節點集合。
*   **Keywords:** Count Components, Friend Circles.

### 3. Topological Sort / 拓樸排序
Ordering nodes linearly such that for every edge $u \to v$, $u$ comes before $v$.
將節點線性排序，使得對於每一條邊 $u \to v$，$u$ 都在 $v$ 之前。
*   **Keywords:** Course Schedule, Build Order, Alien Dictionary.

### 4. Shortest Path in Unweighted Graph / 無權重圖最短路徑
Using BFS to find the minimum number of edges to reach a target.
使用 BFS 尋找到達目標所需的最小邊數。
*   **Keywords:** Word Ladder, Minimum Knight Moves.

---

## 4. Example Walkthroughs (範例講解)

### Example 1: Number of Islands (Grid DFS)
### 範例一：島嶼數量（網格 DFS）

**Problem Statement (問題重述):**
Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.
給定一個 `m x n` 的二維二元網格 `grid`，代表由 `'1'`（陸地）和 `'0'`（水）組成的地圖，請回傳島嶼的數量。

**Approach (思路):**
1.  **Iterate:** Loop through every cell in the grid.
    **迭代：** 遍歷網格中的每一個格子。
2.  **Trigger:** If we encounter a `'1'`, it's a new island. Increment the counter.
    **觸發：** 如果遇到 `'1'`，表示發現新島嶼。計數器加一。
3.  **Sink (Flood Fill):** Start a DFS/BFS from that cell to mark all connected land as visited (turn `'1'` to `'0'`) to avoid recounting.
    **沉沒（泛洪填充）：** 從該格子開始進行 DFS/BFS，將所有相連的陸地標記為已訪問（將 `'1'` 變為 `'0'`），以避免重複計算。

**TypeScript Solution (TypeScript 參考解):**

```typescript
/**
 * Calculates the number of islands in a grid.
 * 計算網格中的島嶼數量。
 * 
 * Time Complexity: O(M * N) - We visit each cell at most once.
 * 時間複雜度：O(M * N) - 我們最多訪問每個格子一次。
 * Space Complexity: O(M * N) - Worst case recursion stack (if grid is all land).
 * 空間複雜度：O(M * N) - 最壞情況下的遞迴堆疊（如果網格全是陸地）。
 */
function numIslands(grid: string[][]): number {
    if (!grid || grid.length === 0) return 0;

    const rows = grid.length;
    const cols = grid[0].length;
    let count = 0;

    // Helper function for DFS traversal
    // 用於 DFS 遍歷的輔助函式
    const dfs = (r: number, c: number) => {
        // Boundary checks and water check
        // 邊界檢查與水域檢查
        if (r < 0 || c < 0 || r >= rows || c >= cols || grid[r][c] === '0') {
            return;
        }

        // Mark as visited (sink the island)
        // 標記為已訪問（將島嶼沉沒）
        grid[r][c] = '0';

        // Visit neighbors (Up, Down, Left, Right)
        // 訪問鄰居（上、下、左、右）
        dfs(r - 1, c);
        dfs(r + 1, c);
        dfs(r, c - 1);
        dfs(r, c + 1);
    };

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            // Found a piece of land
            // 發現一塊陸地
            if (grid[i][j] === '1') {
                count++;
                // Start traversal to sink the entire connected component
                // 開始遍歷以沉沒整個連通分量
                dfs(i, j);
            }
        }
    }

    return count;
}
```

---

### Example 2: Course Schedule (Topological Sort)
### 範例二：課程表（拓樸排序）

**Problem Statement (問題重述):**
There are `numCourses` courses you have to take. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return `true` if you can finish all courses.
你需要修習 `numCourses` 門課程。給定一個陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修習課程 `a`，必須先修習課程 `b`。如果能修完所有課程，回傳 `true`。

**Approach: Kahn's Algorithm (BFS) (思路：Kahn 演算法)**
1.  **Graph Building:** Convert edge list to Adjacency List and calculate **Indegree** (number of incoming edges) for each node.
    **建圖：** 將邊列表轉換為鄰接表，並計算每個節點的**入度**（進入邊的數量）。
2.  **Queue Initialization:** Add all nodes with Indegree 0 (no prerequisites) to a queue.
    **佇列初始化：** 將所有入度為 0（無先修課）的節點加入佇列。
3.  **Process:** Dequeue a node, reduce the Indegree of its neighbors. If a neighbor's Indegree becomes 0, add it to the queue.
    **處理：** 從佇列取出節點，減少其鄰居的入度。若鄰居入度變為 0，將其加入佇列。
4.  **Result:** If the number of processed nodes equals `numCourses`, there is no cycle.
    **結果：** 若處理過的節點數量等於 `numCourses`，則表示無環。

**TypeScript Solution (TypeScript 參考解):**

```typescript
/**
 * Determines if all courses can be finished using Kahn's Algorithm.
 * 使用 Kahn 演算法判斷是否能修完所有課程。
 * 
 * Time Complexity: O(V + E) - Build graph and process every edge/node.
 * 時間複雜度：O(V + E) - 建立圖並處理每個邊/節點。
 * Space Complexity: O(V + E) - Adjacency list and Indegree array.
 * 空間複雜度：O(V + E) - 鄰接表與入度陣列。
 */
function canFinish(numCourses: number, prerequisites: number[][]): boolean {
    // 1. Initialize Graph and Indegree Array
    // 1. 初始化圖與入度陣列
    const adjList = new Map<number, number[]>();
    const indegree = new Array(numCourses).fill(0);

    for (const [course, pre] of prerequisites) {
        // pre -> course
        if (!adjList.has(pre)) {
            adjList.set(pre, []);
        }
        adjList.get(pre)!.push(course);
        indegree[course]++;
    }

    // 2. Add sources (nodes with 0 indegree) to queue
    // 2. 將源頭（入度為 0 的節點）加入佇列
    const queue: number[] = [];
    for (let i = 0; i < numCourses; i++) {
        if (indegree[i] === 0) {
            queue.push(i);
        }
    }

    let processedCount = 0;

    // 3. Process the queue (BFS)
    // 3. 處理佇列 (BFS)
    while (queue.length > 0) {
        const current = queue.shift()!;
        processedCount++;

        if (adjList.has(current)) {
            for (const neighbor of adjList.get(current)!) {
                indegree[neighbor]--;
                // If dependency is resolved, add to queue
                // 若依賴已解決，加入佇列
                if (indegree[neighbor] === 0) {
                    queue.push(neighbor);
                }
            }
        }
    }

    // 4. If we processed all courses, no cycle exists
    // 4. 若我們處理了所有課程，表示不存在環
    return processedCount === numCourses;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Pitfall | Explanation (解釋) |
| :--- | :--- |
| **Directed vs. Undirected**<br>有向 vs. 無向 | **Pitfall:** Treating a directed edge $A \to B$ as $A \leftrightarrow B$. This breaks cycle detection logic.<br>**陷阱：** 將有向邊 $A \to B$ 視為 $A \leftrightarrow B$。這會破壞環檢測邏輯。 |
| **Visited Set Scope**<br>Visited 集合的作用域 | **Pitfall:** In DFS (backtracking), removing a node from `visited` is for finding *all paths*. For simple traversal/reachability, **never** remove from `visited`.<br>**陷阱：** 在 DFS（回溯）中，從 `visited` 移除節點是為了找*所有路徑*。對於單純的遍歷/可達性，**千萬不要**從 `visited` 移除。 |
| **Disconnected Graphs**<br>非連通圖 | **Pitfall:** Assuming the graph is fully connected. Always loop through all nodes `0` to `n-1` to launch traversal if not visited.<br>**陷阱：** 假設圖是完全連通的。務必透過迴圈檢查 `0` 到 `n-1` 的所有節點，若未訪問則啟動遍歷。 |
| **BFS vs. DFS for Shortest Path**<br>BFS vs. DFS 找最短路徑 | **Concept:** BFS guarantees shortest path in unweighted graphs. DFS does not.<br>**觀念：** BFS 保證在無權重圖中找到最短路徑。DFS 則無法保證。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarification Phase (釐清階段)
*   **Input Format:** "Is the input an adjacency matrix, adjacency list, or a list of edges?"
    **輸入格式：** 「輸入是鄰接矩陣、鄰接表，還是邊的列表？」
*   **Connectivity:** "Can the graph be disconnected? Should I handle multiple components?"
    **連通性：** 「圖可能是不連通的嗎？我需要處理多個分量嗎？」
*   **Cycles:** "Does the graph contain cycles? How should we handle them?"
    **環：** 「圖中包含環嗎？我們該如何處理？」

### 2. Communication Framework (口條框架)
*   "I will model this problem as a **Directed Graph** where courses are nodes and prerequisites are edges."
    「我會將此問題建模為**有向圖**，其中課程是節點，先修要求是邊。」
*   "Since we need to detect dependencies, **Topological Sort** is the natural choice."
    「由於我們需要檢測依賴關係，**拓樸排序**是自然的選擇。」
*   "I will use a `visited` Set to avoid processing the same node twice and prevent infinite loops."
    「我會使用 `visited` 集合來避免重複處理相同節點並防止無窮迴圈。」

### 3. Whiteboard Strategy (白板策略)
*   **Modularize:** Write a separate `buildGraph` function. It keeps the main logic clean.
    **模組化：** 撰寫獨立的 `buildGraph` 函式。這能保持主邏輯乾淨。
*   **Define Constants:** Use `const DIRECTIONS = [[0,1], [1,0], [0,-1], [-1,0]];` for grid problems.
    **定義常數：** 在網格問題中使用 `const DIRECTIONS = ...`。

---

## 7. Practice Problems (練習題)

### Easy: Find the Town Judge
**Prompt:** Everyone trusts the Judge; the Judge trusts no one.
**提示：** 每個人都信任法官；法官不信任任何人。
*   **Hint:** Think about **Indegree** and **Outdegree**. The Judge has Indegree $N-1$ and Outdegree $0$.
*   **提示：** 思考**入度**與**出度**。法官的入度為 $N-1$，出度為 $0$。

### Medium: Clone Graph
**Prompt:** Deep copy a connected undirected graph.
**提示：** 深拷貝一個連通無向圖。
*   **Hint:** Use a Hash Map `Map<Node, Node>` to map original nodes to their clones. Use DFS/BFS to traverse and link.
*   **提示：** 使用雜湊表 `Map<Node, Node>` 將原始節點映射到其複本。使用 DFS/BFS 遍歷並連結。

### Hard (Intermediate Scope): Word Ladder
**Prompt:** Transform `beginWord` to `endWord` by changing one letter at a time. Find the shortest sequence.
**提示：** 透過一次改變一個字母，將 `beginWord` 轉換為 `endWord`。找出最短序列。
*   **Hint:** This is a **Shortest Path** problem on an unweighted graph. Use **BFS**. Pre-process the dictionary to find neighbors efficiently (e.g., `*ot` matches `hot`, `dot`).
*   **提示：** 這是無權重圖上的**最短路徑**問題。使用 **BFS**。預處理字典以有效率地尋找鄰居（例如 `*ot` 匹配 `hot`, `dot`）。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Corner Case:** Empty graph? Single node?
    **邊界情況：** 空圖？單一節點？
*   [ ] **Corner Case:** Disconnected components handled? (Outer loop required?)
    **邊界情況：** 處理了非連通分量嗎？（需要外層迴圈？）
*   [ ] **Complexity:** Is it $O(V+E)$? Did I accidentally create $O(V^2)$ inside the loop?
    **複雜度：** 是 $O(V+E)$ 嗎？我是否在迴圈內意外造成了 $O(V^2)$？
*   [ ] **Infinite Loop:** Did I mark nodes as visited *before* pushing to queue (BFS) or upon entry (DFS)?
    **無窮迴圈：** 我是否在推入佇列*之前* (BFS) 或進入時 (DFS) 標記節點為已訪問？

---

## 9. Memory Anchors (記憶錨點)

*   **BFS is like a Ripple (漣漪):** It expands layer by layer. Good for finding the nearest exit.
    **BFS 像漣漪：** 它一層一層擴散。適合尋找最近的出口。
*   **DFS is like a Maze Runner (迷宮跑者):** It goes as deep as possible, hits a dead end, and backtracks. Good for exhaustive search.
    **DFS 像迷宮跑者：** 它盡可能深入，撞到死路後回溯。適合窮舉搜尋。
*   **Topological Sort is like Dressing Up (穿衣):** You can't put on shoes (Node B) before socks (Node A).
    **拓樸排序像穿衣服：** 你不能在穿襪子（節點 A）之前穿鞋子（節點 B）。