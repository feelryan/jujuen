Here is the comprehensive guide for **Advanced Graphs**, tailored for a Senior Software Engineer targeting Big Tech roles, using C++.

這是一份針對 **進階圖論（Advanced Graphs）** 的完整指南，專為目標 Big Tech 職位的資深軟體工程師量身打造，並使用 C++ 撰寫。

---

# Advanced Graphs for Senior Engineers (C++)
# 資深工程師的進階圖論指南 (C++)

## 1. Learning Goals（學習目標）

*   **Master Graph Modeling:** Ability to translate abstract problems (dependencies, state changes, network connectivity) into standard graph representations.
    **掌握圖的建模：** 能夠將抽象問題（依賴關係、狀態變遷、網路連通性）轉化為標準的圖論表示法。
*   **Proficiency in Advanced Algorithms:** Deep understanding of Dijkstra, Topological Sort, and Union-Find (Disjoint Set), beyond basic BFS/DFS.
    **精通進階演算法：** 深入理解 Dijkstra、拓撲排序（Topological Sort）與並查集（Union-Find），而不僅止於基礎的 BFS/DFS。
*   **Complexity Analysis & Optimization:** Accurately analyze time complexity in terms of $V$ (Vertices) and $E$ (Edges), and know when to optimize using heaps or path compression.
    **複雜度分析與優化：** 精準分析基於 $V$（頂點）與 $E$（邊）的時間複雜度，並知道何時使用堆積（Heap）或路徑壓縮（Path Compression）進行優化。
*   **C++ STL Mastery:** Leverage C++ specific containers like `std::priority_queue`, `std::unordered_map`, and `std::vector` for efficient graph implementation.
    **掌握 C++ STL：** 利用 C++ 特有的容器如 `std::priority_queue`、`std::unordered_map` 和 `std::vector` 來實現高效的圖算法。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definitions & Intuition（定義與直覺）

*   **Graph Representation:** For algorithm interviews, **Adjacency List** is almost always preferred over Adjacency Matrix due to space efficiency ($O(V+E)$ vs $O(V^2)$).
    **圖的表示：** 在演算法面試中，**鄰接表（Adjacency List）** 幾乎總是優於鄰接矩陣（Adjacency Matrix），因為空間效率較高（$O(V+E)$ vs $O(V^2)$）。
*   **Directed vs. Undirected:** Always clarify if edges have direction; this affects cycle detection logic and traversal.
    **有向 vs. 無向：** 務必確認邊是否有方向；這會影響環檢測邏輯與遍歷方式。
*   **Weighted vs. Unweighted:** Unweighted shortest path $\rightarrow$ BFS; Weighted (non-negative) $\rightarrow$ Dijkstra.
    **有權 vs. 無權：** 無權圖最短路徑 $\rightarrow$ BFS；有權圖（非負權重） $\rightarrow$ Dijkstra。

### Complexity（複雜度）

*   **BFS / DFS:** $O(V + E)$ time, $O(V)$ space.
    **BFS / DFS：** 時間 $O(V + E)$，空間 $O(V)$。
*   **Dijkstra (with Binary Heap):** $O(E \log V)$ time.
    **Dijkstra（使用二元堆積）：** 時間 $O(E \log V)$。
*   **Union-Find:** $O(\alpha(V))$ per operation (amortized nearly constant).
    **並查集：** 每次操作 $O(\alpha(V))$（均攤後近乎常數）。

### When to Use / Not Use（適用與不適用場景）

*   **Use Graphs when:** Relationships between objects are many-to-many, or problems involve "reachability," "shortest path," or "grouping."
    **適用場景：** 物件之間的關係是多對多，或問題涉及「可達性」、「最短路徑」或「分組」。
*   **Do Not Use (or Overkill) when:** The structure is strictly hierarchical (use Trees) or linear (use Arrays/Linked Lists).
    **不適用（或大材小用）場景：** 結構是嚴格分層的（使用樹）或線性的（使用陣列/鏈結串列）。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Topological Sort (Kahn's Algorithm)
*   **Scenario:** Task scheduling, dependency resolution, detecting cycles in directed graphs.
    **場景：** 任務排程、依賴解析、檢測有向圖中的環。
*   **Key Data:** `in_degree` array and a `queue` for 0-in-degree nodes.
    **關鍵數據：** `in_degree` 陣列與存放 0 入度節點的 `queue`。

### B. Dijkstra’s Algorithm
*   **Scenario:** Shortest path in a weighted graph with non-negative weights.
    **場景：** 非負權重圖中的最短路徑。
*   **Key Data:** `priority_queue` (min-heap) storing `{distance, node}`.
    **關鍵數據：** 儲存 `{距離, 節點}` 的 `priority_queue`（最小堆積）。

### C. Union-Find (Disjoint Set Union - DSU)
*   **Scenario:** Dynamic connectivity, counting connected components, cycle detection in undirected graphs.
    **場景：** 動態連通性、計算連通分量、無向圖中的環檢測。
*   **Key Optimization:** Path Compression + Union by Rank.
    **關鍵優化：** 路徑壓縮 + 按秩合併。

---

## 4. Example Walkthrough（範例講解）

### Example 1: Network Delay Time (Dijkstra)
**Problem:** Given a network of $n$ nodes, labeled from 1 to $n$, and a list of travel times as directed edges `times[i] = (u, v, w)`, find the time it takes for all nodes to receive a signal sent from node $k$. If impossible, return -1.
**問題：** 給定一個由 $n$ 個節點組成的網路，標記為 1 到 $n$，以及一組傳輸時間作為有向邊 `times[i] = (u, v, w)`，求從節點 $k$ 發出的訊號傳遍所有節點所需的時間。若無法傳遍，返回 -1。

#### Approach（思路）

1.  **Modeling:** This is a "Single Source Shortest Path" problem on a weighted directed graph. We need the maximum of the shortest paths to all nodes.
    **建模：** 這是一個加權有向圖上的「單源最短路徑」問題。我們需要所有節點最短路徑中的最大值。
2.  **Brute Force (DFS):** DFS is bad for shortest paths in weighted graphs because it explores depth first, potentially recalculating paths many times. Complexity is exponential in worst case without memoization.
    **暴力解（DFS）：** DFS 不適合加權圖的最短路徑，因為它優先探索深度，可能多次重複計算路徑。最壞情況下複雜度是指數級的（若無記憶化）。
3.  **Optimization (BFS?):** Standard BFS only works for unweighted graphs.
    **優化（BFS？）：** 標準 BFS 僅適用於無權圖。
4.  **Optimal (Dijkstra):** Use a Min-Heap to always expand the node with the smallest accumulated distance.
    **最佳解（Dijkstra）：** 使用最小堆積（Min-Heap）來總是擴展累積距離最小的節點。

#### C++ Solution (Dijkstra)

```cpp
#include <vector>
#include <queue>
#include <unordered_map>
#include <algorithm>

using namespace std;

class Solution {
public:
    int networkDelayTime(vector<vector<int>>& times, int n, int k) {
        // 1. Build Adjacency List
        // 1. 建立鄰接表
        // vector<pair<neighbor, weight>>
        vector<vector<pair<int, int>>> adj(n + 1);
        for (const auto& t : times) {
            adj[t[0]].push_back({t[1], t[2]});
        }

        // 2. Initialize Distances
        // 2. 初始化距離陣列
        // Use INT_MAX to represent infinity
        // 使用 INT_MAX 代表無窮大
        vector<int> dist(n + 1, INT_MAX);
        dist[k] = 0;

        // 3. Min-Heap for Dijkstra
        // 3. Dijkstra 用的最小堆積
        // pair<distance, node>, ordered by distance ascending
        // pair<距離, 節點>，按距離升序排列
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;
        pq.push({0, k});

        while (!pq.empty()) {
            int d = pq.top().first;
            int u = pq.top().second;
            pq.pop();

            // Optimization: If current distance is greater than already found shortest distance, skip.
            // 優化：若當前距離大於已找到的最短距離，則跳過（Lazy Deletion）。
            if (d > dist[u]) continue;

            // Traverse neighbors
            // 遍歷鄰居
            for (auto& edge : adj[u]) {
                int v = edge.first;
                int weight = edge.second;

                // Relaxation step
                // 鬆弛步驟
                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    pq.push({dist[v], v});
                }
            }
        }

        // 4. Find the max distance among all nodes
        // 4. 找出所有節點中的最大距離
        int maxDist = 0;
        for (int i = 1; i <= n; ++i) {
            if (dist[i] == INT_MAX) return -1; // Unreachable node / 無法到達的節點
            maxDist = max(maxDist, dist[i]);
        }

        return maxDist;
    }
};
```

### Example 2: Number of Provinces (Union-Find)
**Problem:** Given an $n \times n$ matrix `isConnected`, where `isConnected[i][j] = 1` implies city $i$ and $j$ are connected, find the total number of provinces (connected components).
**問題：** 給定一個 $n \times n$ 矩陣 `isConnected`，其中 `isConnected[i][j] = 1` 表示城市 $i$ 和 $j$ 相連，求省份（連通分量）的總數。

#### Approach（思路）

1.  **Modeling:** We need to group nodes together. If A connects to B, they are in the same group.
    **建模：** 我們需要將節點分組。如果 A 連接 B，它們就在同一組。
2.  **Choice:** BFS/DFS can find components ($O(V^2)$ here due to matrix). Union-Find is elegant for dynamic connectivity and clearly demonstrates "grouping" logic.
    **選擇：** BFS/DFS 可以找到連通分量（此處因矩陣為 $O(V^2)$）。並查集（Union-Find）對於動態連通性非常優雅，且能清晰展示「分組」邏輯。

#### C++ Solution (Union-Find / DSU)

```cpp
#include <vector>
#include <numeric> // for std::iota

using namespace std;

// Modular DSU Class - Great for Interviews
// 模組化的 DSU 類別 - 面試時的加分項
class UnionFind {
private:
    vector<int> parent;
    vector<int> rank;
    int count; // Number of connected components / 連通分量數量

public:
    UnionFind(int n) : count(n) {
        parent.resize(n);
        rank.resize(n, 0);
        // Initialize parent[i] = i
        // 初始化 parent[i] = i
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        // Path Compression
        // 路徑壓縮
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    void unite(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);

        if (rootX != rootY) {
            // Union by Rank
            // 按秩合併
            if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            count--; // Decrement component count / 減少連通分量計數
        }
    }

    int getCount() const {
        return count;
    }
};

class Solution {
public:
    int findCircleNum(vector<vector<int>>& isConnected) {
        int n = isConnected.size();
        UnionFind uf(n);

        for (int i = 0; i < n; ++i) {
            // Matrix is symmetric, only check j > i to avoid double counting
            // 矩陣是對稱的，只需檢查 j > i 以避免重複計算
            for (int j = i + 1; j < n; ++j) {
                if (isConnected[i][j] == 1) {
                    uf.unite(i, j);
                }
            }
        }

        return uf.getCount();
    }
};
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Pitfall / Confusion (陷阱 / 混淆) | Correct Understanding (正確理解) |
| :--- | :--- | :--- |
| **Visited Array** | Marking visited *after* popping from queue in BFS. <br> 在 BFS 中從佇列取出 *後* 才標記 visited。 | **Mark visited *before* pushing to queue.** This prevents duplicate nodes from flooding the queue. <br> **在推入佇列 *前* 標記 visited。** 這能防止重複節點淹沒佇列。 |
| **Dijkstra** | Using Dijkstra on graphs with **negative edges**. <br> 在有 **負權邊** 的圖上使用 Dijkstra。 | Dijkstra assumes weights are non-negative. Use **Bellman-Ford** for negative edges. <br> Dijkstra 假設權重非負。負權邊請使用 **Bellman-Ford**。 |
| **DFS Recursion** | Forgetting to **backtrack** (reset visited) when finding *all* paths. <br> 在尋找 *所有* 路徑時忘記 **回溯**（重置 visited）。 | If finding *one* path/reachability, no backtrack needed. If finding *all* paths, must backtrack. <br> 若找 *一條* 路徑/可達性，無需回溯。若找 *所有* 路徑，必須回溯。 |
| **Priority Queue** | C++ `priority_queue` is a **Max-Heap** by default. <br> C++ 的 `priority_queue` 預設是 **最大堆積**。 | For Dijkstra, use `greater` comparator to make it a **Min-Heap**. <br> 對於 Dijkstra，使用 `greater` 比較器使其成為 **最小堆積**。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **Categorize:** "This looks like a graph connectivity problem / shortest path problem."
    **分類：** 「這看起來像是一個圖的連通性問題 / 最短路徑問題。」
2.  **Define Nodes & Edges:** "I will treat each city as a Node and the flight cost as the Edge weight."
    **定義節點與邊：** 「我會將每個城市視為節點，飛行成本視為邊的權重。」
3.  **Choose Algorithm:** "Since edge weights are non-negative, Dijkstra is optimal here."
    **選擇演算法：** 「由於邊的權重非負，這裡使用 Dijkstra 是最佳的。」

### Whiteboard Strategy（白板策略）
*   **Draw it out:** Draw a small graph (3-4 nodes) to trace your logic.
    **畫出來：** 畫一個小型的圖（3-4 個節點）來追蹤你的邏輯。
*   **Structs:** In C++, defining a simple `struct` or using `typedef/using` for `pair<int, int>` shows you care about readability.
    **結構體：** 在 C++ 中，定義簡單的 `struct` 或為 `pair<int, int>` 使用 `typedef/using` 顯示你重視可讀性。

### Common Follow-ups（常見追問）
*   "What if the graph is dynamic (edges added/removed)?" $\rightarrow$ Discuss Union-Find or dynamic graph algorithms.
    「如果圖是動態的（邊被新增/移除）怎麼辦？」 $\rightarrow$ 討論並查集或動態圖算法。
*   "What if weights can be negative?" $\rightarrow$ Bellman-Ford or SPFA.
    「如果權重可能是負的？」 $\rightarrow$ Bellman-Ford 或 SPFA。
*   "How to handle a graph too large for memory?" $\rightarrow$ Distributed processing (MapReduce) or processing adjacency lists in chunks.
    「如何處理記憶體裝不下的大圖？」 $\rightarrow$ 分散式處理（MapReduce）或分塊處理鄰接表。

---

## 7. Practice Problems（練習題）

### Easy: Clone Graph
*   **Prompt:** Deep copy a connected undirected graph.
    **題目：** 深拷貝一個連通無向圖。
*   **Hint:** Use a Hash Map (`unordered_map<Node*, Node*>`) to map original nodes to cloned nodes to avoid cycles.
    **提示：** 使用雜湊表（`unordered_map<Node*, Node*>`）將原始節點映射到克隆節點以避免無窮迴圈。

### Medium: Course Schedule II (Topological Sort)
*   **Prompt:** Given courses and prerequisites, return the ordering of courses.
    **題目：** 給定課程與先修限制，返回課程的修課順序。
*   **Hint:** Calculate `in-degree` for all nodes. Push nodes with `0` in-degree to queue. Pop, add to result, and decrement neighbors' in-degree.
    **提示：** 計算所有節點的 `入度`。將入度為 `0` 的節點推入佇列。取出並加入結果，然後減少鄰居的入度。

### Hard: Cheapest Flights Within K Stops
*   **Prompt:** Find cheapest price from source to dest with at most K stops.
    **題目：** 找出從起點到終點，且中轉不超過 K 次的最便宜價格。
*   **Hint:** This is Dijkstra but with a constraint on "depth" (stops). You cannot simply discard a path just because it's more expensive if it has fewer stops. Alternatively, use Bellman-Ford running $K+1$ iterations.
    **提示：** 這是 Dijkstra 但增加了「深度」（中轉次數）限制。你不能僅因為某條路徑較貴就丟棄它，如果它的中轉次數較少的話。或者，使用執行 $K+1$ 次迭代的 Bellman-Ford。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review / Debugging（自我審查 / 除錯）
- [ ] **Connectivity:** Did I handle disconnected graphs? (Loop through all nodes 1 to N).
    **連通性：** 我是否處理了非連通圖？（迴圈遍歷所有節點 1 到 N）。
- [ ] **Cycles:** If the graph has cycles, did I use a `visited` set?
    **環：** 如果圖有環，我是否使用了 `visited` 集合？
- [ ] **Direction:** Is `adj[u].push_back(v)` enough, or do I need `adj[v].push_back(u)` too?
    **方向：** `adj[u].push_back(v)` 足夠嗎，還是我也需要 `adj[v].push_back(u)`？
- [ ] **Complexity:** Is my solution $O(V+E)$ or accidentally $O(V^2)$?
    **複雜度：** 我的解法是 $O(V+E)$ 還是不小心變成了 $O(V^2)$？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **Dijkstra is like Water Spreading:** Water flows everywhere, but it flows *slower* through thick mud (high weight) and *faster* through pipes (low weight). It reaches the closest points first.
    **Dijkstra 就像水流擴散：** 水流向四處，但在濃泥（高權重）中流得*慢*，在管道（低權重）中流得*快*。它總是先到達最近的點。
*   **Union-Find is like Corporate Mergers:** Initially, every employee is their own boss. When companies merge, one boss reports to another. Path compression is like an employee remembering the *CEO* directly so they don't have to ask their manager's manager's manager next time.
    **並查集就像公司合併：** 最初，每個員工都是自己的老闆。當公司合併時，一位老闆向另一位匯報。路徑壓縮就像員工直接記住 *CEO* 是誰，這樣下次就不用層層向上詢問經理的經理的經理。
*   **Topological Sort is like Getting Dressed:** You can't put on shoes (Node B) before socks (Node A). The `in-degree` is how many garments you must wear *before* this one.
    **拓撲排序就像穿衣服：** 你不能在穿襪子（節點 A）之前穿鞋子（節點 B）。`入度` 代表在這件衣物*之前*必須穿多少件衣物。