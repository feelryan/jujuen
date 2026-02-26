# Advanced Graphs Interview Guide (進階圖論面試指南)

## 1. Learning Objectives (學習目標)

*   **Master Shortest Path Algorithms beyond BFS:** Understand when to apply Dijkstra, Bellman-Ford, or Floyd-Warshall based on edge weights and constraints.
    **掌握 BFS 以外的最短路徑演算法：** 理解何時根據邊的權重與限制條件，應用 Dijkstra、Bellman-Ford 或 Floyd-Warshall。
*   **Deep Dive into Connectivity & Disjoint Sets:** Utilize Union-Find (with path compression and union by rank) for dynamic connectivity problems and cycle detection.
    **深入連結性與互斥集：** 利用 Union-Find（搭配路徑壓縮與按秩合併）解決動態連結問題與環檢測。
*   **Handle Dependencies and Ordering:** Implement Topological Sort (Kahn’s Algorithm & DFS) for scheduling and dependency resolution problems.
    **處理依賴關係與排序：** 實作拓撲排序（Kahn 演算法與 DFS）以解決排程與依賴解析問題。
*   **Identify Critical Structures:** Learn algorithms like Tarjan’s to find bridges (critical connections) and articulation points in a network.
    **識別關鍵結構：** 學習如 Tarjan 等演算法，以找出網路中的橋樑（關鍵連接）與關節點。

---

## 2. Core Concepts Overview (核心觀念速覽)

### A. Dijkstra’s Algorithm (Dijkstra 演算法)
*   **Definition:** Finds the shortest path from a source node to all other nodes in a graph with **non-negative** weights.
    **定義：** 在**非負**權重的圖中，找出從源節點到所有其他節點的最短路徑。
*   **Intuition:** A greedy approach that always extends the shortest known path (using a Priority Queue).
    **直覺：** 一種貪婪策略，總是延伸目前已知最短的路徑（使用優先佇列）。
*   **Complexity:** $O(E \log V)$ or $O(E + V \log V)$ with Fibonacci heap.
    **複雜度：** $O(E \log V)$，若使用費氏堆積則為 $O(E + V \log V)$。
*   **Use Case:** Google Maps routing, network delay time.
    **適用場景：** Google Maps 路線規劃、網路延遲時間。

### B. Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every edge $u \to v$, $u$ comes before $v$.
    **定義：** 有向無環圖（DAG）中頂點的線性排序，使得對於每條邊 $u \to v$，$u$ 都在 $v$ 之前。
*   **Intuition:** "Finish prerequisites before the advanced course." Use Indegree (Kahn's) or DFS post-order.
    **直覺：** 「先修完基礎課程再修進階課程。」使用入度（Kahn 演算法）或 DFS 後序遍歷。
*   **Complexity:** $O(V + E)$.
    **複雜度：** $O(V + E)$。

### C. Union-Find / Disjoint Set Union (並查集)
*   **Definition:** A data structure that tracks elements partitioned into disjoint subsets.
    **定義：** 一種追蹤被分割成不相交子集之元素的資料結構。
*   **Intuition:** "Are these two computers in the same network?" Merging sets is fast.
    **直覺：** 「這兩台電腦是否在同一個網路內？」合併集合的速度非常快。
*   **Complexity:** Nearly $O(1)$ per operation (Inverse Ackermann function $\alpha(n)$).
    **複雜度：** 每次操作近乎 $O(1)$（反阿克曼函數 $\alpha(n)$）。

### D. Tarjan’s Algorithm (Bridge Finding) (Tarjan 橋樑尋找演算法)
*   **Definition:** Uses DFS to find edges that, if removed, increase the number of connected components.
    **定義：** 使用 DFS 找出那些一旦移除就會增加連通分量數量的邊。
*   **Intuition:** An edge $(u, v)$ is a bridge if there is no "back edge" from the subtree of $v$ to $u$ or an ancestor of $u$.
    **直覺：** 如果 $v$ 的子樹沒有「回邊」連回 $u$ 或 $u$ 的祖先，則邊 $(u, v)$ 為橋樑。

---

## 3. Typical Patterns (典型題型 / 模式)

| Pattern | Keywords / Signals | Algorithm Choice |
| :--- | :--- | :--- |
| **Shortest Path (Weighted)** | "Min cost", "Min delay", "Cheapest flight", Non-negative weights | **Dijkstra** (BFS if unweighted) |
| **Dependency Resolution** | "Prerequisites", "Order of tasks", "Build order", "Deadlock detection" | **Topological Sort** |
| **Connectivity / Grouping** | "Number of provinces", "Redundant connection", "Merge networks" | **Union-Find** (or DFS/BFS) |
| **Critical Vulnerability** | "Single point of failure", "Critical connection", "Split the network" | **Tarjan's (Bridges)** |
| **Shortest Path (Negative)**| "Negative cycles", "Arbitrage" | **Bellman-Ford** |

---

## 4. Example Walkthrough (範例講解)

### Problem: Critical Connections in a Network (Hard)
### 問題：網路中的關鍵連接（困難）

**Problem Statement:**
There are `n` servers numbered from `0` to `n-1` connected by undirected server-to-server `connections`.
有 `n` 個伺服器，編號從 `0` 到 `n-1`，透過無向的 `connections` 互相連接。
Return all critical connections (bridges). A critical connection is a connection that, if removed, will make some server unable to reach some other server.
回傳所有的關鍵連接（橋樑）。關鍵連接是指如果移除該連接，將導致某些伺服器無法連接到其他伺服器。

---

#### 1. Approach: Brute Force (暴力法)
*   **Idea:** Iterate through every edge, remove it, and run BFS/DFS to check if the graph is still connected.
    **思路：** 遍歷每一條邊，將其移除，然後執行 BFS/DFS 檢查圖是否仍然連通。
*   **Complexity:** $O(E \times (V + E))$. For dense graphs, this is $O(E^2)$ or $O(V^4)$, which is too slow (TLE).
    **複雜度：** $O(E \times (V + E))$。對於稠密圖，這是 $O(E^2)$ 或 $O(V^4)$，太慢了（會超時）。

#### 2. Approach: Optimal Solution using Tarjan's Algorithm (最佳解：Tarjan 演算法)
*   **Idea:** Use DFS to track the `discovery time` (rank) and `lowest reachable rank` (low-link) for each node.
    **思路：** 使用 DFS 追蹤每個節點的「發現時間」（rank）與「最低可達秩」（low-link）。
*   **Key Logic:** If we traverse edge $u \to v$, and after exploring $v$, we find that `low[v] > rank[u]`, it means there is no back-edge from $v$ (or its descendants) to $u$ or $u$'s ancestors. Thus, $(u, v)$ is a bridge.
    **關鍵邏輯：** 如果我們遍歷邊 $u \to v$，且在探索完 $v$ 之後發現 `low[v] > rank[u]`，這表示從 $v$（或其後代）沒有回邊連回 $u$ 或 $u$ 的祖先。因此，$(u, v)$ 是一座橋。

#### 3. TypeScript Solution (TypeScript 參考解)

```typescript
/**
 * Finds all critical connections (bridges) in a network.
 * 找出網路中所有的關鍵連接（橋樑）。
 * 
 * Time Complexity: O(V + E) - We visit every node and edge once via DFS.
 * 時間複雜度：O(V + E) - 我們透過 DFS 訪問每個節點與邊一次。
 * Space Complexity: O(V + E) - Adjacency list and recursion stack.
 * 空間複雜度：O(V + E) - 鄰接表與遞迴堆疊。
 */
function criticalConnections(n: number, connections: number[][]): number[][] {
    // Build the graph (Adjacency List)
    // 建立圖（鄰接表）
    const graph: number[][] = Array.from({ length: n }, () => []);
    for (const [u, v] of connections) {
        graph[u].push(v);
        graph[v].push(u);
    }

    // Array to store the discovery time (rank) of each node. -1 implies unvisited.
    // 陣列用於儲存每個節點的發現時間（rank）。-1 代表未訪問。
    const rank: number[] = new Array(n).fill(-1);
    
    // Array to store the lowest rank reachable from the node (including back-edges).
    // 陣列用於儲存從該節點可達到的最低秩（包含回邊）。
    const low: number[] = new Array(n).fill(-1);
    
    const bridges: number[][] = [];
    let time = 0; // Global timer / 全域計時器

    /**
     * DFS function to traverse the graph.
     * 用於遍歷圖的 DFS 函數。
     * 
     * @param u Current node / 當前節點
     * @param p Parent node (to avoid going back immediately) / 父節點（避免立即走回頭路）
     */
    const dfs = (u: number, p: number) => {
        rank[u] = time;
        low[u] = time;
        time++;

        for (const v of graph[u]) {
            if (v === p) {
                // Do not go back to the parent immediately in undirected graph
                // 在無向圖中，不要立即走回父節點
                continue;
            }

            if (rank[v] === -1) {
                // If v is not visited, recurse on it
                // 如果 v 尚未訪問，對其進行遞迴
                dfs(v, u);
                
                // On return, update low[u] based on child's low value
                // 回傳時，根據子節點的 low 值更新 low[u]
                low[u] = Math.min(low[u], low[v]);

                // BRIDGE CHECK:
                // If the lowest vertex reachable from v is strictly deeper than u,
                // it means there is no back-edge to u or above. The edge u-v is a bridge.
                // 橋樑檢查：
                // 如果從 v 可達到的最低頂點嚴格深於 u，
                // 表示沒有回邊連回 u 或其上方。邊 u-v 即為橋樑。
                if (low[v] > rank[u]) {
                    bridges.push([u, v]);
                }
            } else {
                // If v is already visited, it's a back-edge. Update low[u].
                // 如果 v 已被訪問，這是一條回邊。更新 low[u]。
                low[u] = Math.min(low[u], rank[v]);
            }
        }
    };

    // Start DFS from node 0 (assuming graph is connected, otherwise loop 0 to n-1)
    // 從節點 0 開始 DFS（假設圖是連通的，否則需迴圈遍歷 0 到 n-1）
    dfs(0, -1);

    return bridges;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Dijkstra** | **BFS** | BFS only works for **unweighted** graphs (or equal weights). Dijkstra handles **weighted** graphs. <br> BFS 僅適用於**無權重**圖（或等權重）。Dijkstra 處理**有權重**圖。 |
| **Back Edge (回邊)** | **Cross Edge (橫邊)** | In DFS, a back edge points to an ancestor. A cross edge points to a visited node that is NOT an ancestor. Undirected graphs usually only have tree edges and back edges. <br> 在 DFS 中，回邊指向祖先。橫邊指向已訪問但非祖先的節點。無向圖通常只有樹邊和回邊。 |
| **O(V+E)** | **O(V*E)** | Standard DFS/BFS is $O(V+E)$. Bellman-Ford is $O(V \times E)$. Don't confuse linear time with quadratic time. <br> 標準 DFS/BFS 為 $O(V+E)$。Bellman-Ford 為 $O(V \times E)$。不要混淆線性時間與二次時間。 |
| **Topological Sort** | **Cycle Detection** | Topo sort **fails** if there is a cycle. You must detect cycles (via `indegree` check or recursion stack) while attempting Topo sort. <br> 若存在環，拓撲排序會**失敗**。嘗試拓撲排序時必須同時檢測環（透過 `indegree` 檢查或遞迴堆疊）。 |

---

## 6. Interview Strategy (面試實戰建議)

### A. Clarification Phase (釐清階段)
*   **Direction:** "Is the graph directed or undirected?" (Crucial for cycle detection logic).
    **方向性：** 「圖是有向的還是無向的？」（這對環檢測邏輯至關重要）。
*   **Weights:** "Are edges weighted? Can weights be negative?" (Decides BFS vs Dijkstra vs Bellman-Ford).
    **權重：** 「邊是否有權重？權重可以是負的嗎？」（決定使用 BFS、Dijkstra 或 Bellman-Ford）。
*   **Connectivity:** "Is the graph guaranteed to be connected? Can there be multiple components?"
    **連通性：** 「圖保證是連通的嗎？是否可能有多個分量？」

### B. Whiteboard Strategy (白板策略)
*   **Draw it out:** Always draw a small graph (3-5 nodes) with a cycle and a bridge.
    **畫出來：** 務必畫一個包含環與橋樑的小型圖（3-5 個節點）。
*   **Define State:** Explicitly write what your arrays mean (e.g., `visited[i] = 0` means unvisited, `1` visiting, `2` visited).
    **定義狀態：** 明確寫下陣列的意義（例如：`visited[i] = 0` 代表未訪問，`1` 訪問中，`2` 已訪問）。

### C. Follow-up Questions (常見追問)
*   **Q:** "How does this change if the graph is dynamic (edges added over time)?"
    **問：** 「如果圖是動態的（隨時間增加邊），這會如何改變？」
    *   **A:** Suggest **Union-Find** for incremental connectivity.
    *   **答：** 建議使用 **Union-Find** 來處理增量連通性。
*   **Q:** "What if the graph is too large for memory?"
    **問：** 「如果圖太大無法放入記憶體怎麼辦？」
    *   **A:** Discuss distributed graph processing (e.g., MapReduce, Pregel) or storing adjacency lists in a database.
    *   **答：** 討論分散式圖形處理（如 MapReduce、Pregel）或將鄰接表存入資料庫。

---

## 7. Practice Problems (練習題)

### Level: Easy / Intermediate (基礎/中級)
**1. Network Delay Time (LeetCode 743)**
*   **Prompt:** Given a network of `n` nodes and directed weighted edges (times), find the time for all nodes to receive a signal from node `k`.
    **題目：** 給定 `n` 個節點與有向加權邊（時間）的網路，找出所有節點從節點 `k` 收到訊號所需的時間。
*   **Hint:** Classic Dijkstra. Use a Min-Heap (or simulate one). Return max of shortest paths.
    **提示：** 經典 Dijkstra。使用最小堆積（或模擬一個）。回傳最短路徑中的最大值。

### Level: Intermediate / Advanced (中級/進階)
**2. Course Schedule II (LeetCode 210)**
*   **Prompt:** Return the ordering of courses to finish all courses given prerequisites. Detect if impossible.
    **題目：** 給定先修條件，回傳完成所有課程的順序。若不可能則檢測出來。
*   **Hint:** Topological Sort. Use Kahn’s algorithm (Indegree array + Queue). If result length != n, cycle exists.
    **提示：** 拓撲排序。使用 Kahn 演算法（入度陣列 + 佇列）。若結果長度不等於 n，則存在環。

### Level: Hard (困難)
**3. Checking Existence of Edge Length Limited Paths (LeetCode 1697)**
*   **Prompt:** Given an undirected graph and queries `(p, q, limit)`, check if there is a path between `p` and `q` using only edges with weight < `limit`.
    **題目：** 給定無向圖與查詢 `(p, q, limit)`，檢查 `p` 與 `q` 之間是否存在僅使用權重 < `limit` 的邊的路徑。
*   **Hint:** Sort queries by limit and edges by weight. Use **Union-Find**. Iterate through sorted queries, adding valid edges to UF, then check connectivity.
    **提示：** 將查詢按 limit 排序，邊按 weight 排序。使用 **Union-Find**。遍歷排序後的查詢，將符合條件的邊加入 UF，然後檢查連通性。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Constraints Check:** Is $N \le 20$ (Exponential OK), $N \le 1000$ ($O(N^2)$ OK), or $N \le 10^5$ ($O(N \log N)$ or $O(N)$ required)?
    **限制檢查：** $N \le 20$（指數級可），$N \le 1000$（$O(N^2)$ 可），還是 $N \le 10^5$（需 $O(N \log N)$ 或 $O(N)$）？
*   [ ] **Corner Cases:** Disconnected graph? Single node? Self-loops? Parallel edges?
    **邊界情況：** 不連通圖？單一節點？自環？平行邊？
*   [ ] **TS Specifics:** Since TS/JS has no built-in Priority Queue, did I mention I would implement a simple Heap or assume a library?
    **TS 特性：** 由於 TS/JS 沒有內建優先佇列，我是否提到會實作簡單的 Heap 或假設使用函式庫？
*   [ ] **Visited Set:** Did I remember to mark nodes as visited to avoid infinite loops?
    **訪問集合：** 我是否記得標記節點為已訪問以避免無限迴圈？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Dijkstra is like Water Spreading:** Water flows through pipes (edges). It reaches closer/wider pipes (lower weight) first.
    **Dijkstra 就像水流擴散：** 水流經水管（邊）。它會先到達較近/較寬的水管（低權重）。
*   **Union-Find is like Corporate Mergers:** Initially, every employee is their own CEO. When companies merge, one CEO reports to another. `find()` asks "Who is your ultimate boss?".
    **Union-Find 就像企業合併：** 最初，每個員工都是自己的 CEO。當公司合併時，一位 CEO 向另一位匯報。`find()` 詢問「你的最終老闆是誰？」。
*   **Topological Sort is like Getting Dressed:** You can't put on shoes (node V) before socks (node U).
    **拓撲排序就像穿衣服：** 你不能在穿襪子（節點 U）之前穿鞋子（節點 V）。
*   **Tarjan's Low-Link is a "Safety Rope":** `low[u]` tells you the highest ancestor you can grapple back to without using the edge you just came from. If you can't grapple back up, you are hanging on a bridge.
    **Tarjan 的 Low-Link 是一條「安全繩」：** `low[u]` 告訴你在不使用剛經過的那條邊的情況下，你能鉤回的最高祖先。如果你鉤不回去，你就懸掛在橋上。