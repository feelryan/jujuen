Here is the comprehensive guide for **Advanced Graphs**, tailored for a Senior Software Engineer targeting Big Tech roles.
這是一份針對 **進階圖論（Advanced Graphs）** 的完整指南，專為目標 Big Tech 職位的資深軟體工程師量身打造。

---

# Advanced Graphs Interview Guide (C++)
# 進階圖論面試指南 (C++)

## 1. Learning Goals (學習目標)

1.  **Master Shortest Path Algorithms in Complex Scenarios:** Move beyond BFS to implement Dijkstra and Bellman-Ford for weighted graphs and state-dependent paths.
    **掌握複雜場景下的最短路徑演算法：** 超越 BFS，學會針對加權圖和狀態依賴路徑實作 Dijkstra 與 Bellman-Ford。

2.  **Deep Dive into Connectivity & Disjoint Sets:** Proficiency in Union-Find (DSU) with path compression and rank optimization, and identifying bridges/articulation points using Tarjan’s algorithm.
    **深入連結性與互斥集：** 熟練運用具路徑壓縮與秩優化的 Union-Find (DSU)，並使用 Tarjan 演算法識別橋樑與關節點。

3.  **Topological Sorting & Dependency Resolution:** Solve dependency problems and cycle detection in directed graphs using Kahn’s algorithm or DFS.
    **拓撲排序與依賴解析：** 使用 Kahn 演算法或 DFS 解決有向圖中的依賴問題與環檢測。

4.  **Graph Modeling Capability:** Translate abstract constraints (e.g., currency exchange, alien dictionary) into graph nodes and edges instantly.
    **圖論建模能力：** 能夠即時將抽象限制（如貨幣兌換、外星字典）轉化為圖的節點與邊。

---

## 2. Core Concepts Overview (核心觀念速覽)

### A. Dijkstra's Algorithm (Dijkstra 演算法)
*   **Definition:** A greedy algorithm to find the shortest path from a source to all other nodes in a graph with non-negative edge weights.
    **定義：** 一種貪婪演算法，用於在非負權重的圖中找出從起點到所有其他節點的最短路徑。
*   **Intuition:** "Expanding water spill" — always process the closest reachable node next.
    **直覺：** 「水漬擴散」——總是優先處理距離最近的可達節點。
*   **Complexity:** $O(E \log V)$ using a Min-Heap.
    **複雜度：** 使用最小堆積（Min-Heap）時為 $O(E \log V)$。
*   **When to use:** Weighted graphs, finding shortest path.
    **適用場景：** 加權圖，尋找最短路徑。
*   **When NOT to use:** Graphs with negative edge weights (use Bellman-Ford).
    **不適用場景：** 含有負權重邊的圖（應使用 Bellman-Ford）。

### B. Union-Find / Disjoint Set Union (聯集-尋找 / 互斥集)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個互斥（不重疊）子集的元素集合。
*   **Intuition:** Managing group memberships and merging cliques efficiently.
    **直覺：** 高效管理群組成員資格與合併小圈子。
*   **Complexity:** Almost $O(1)$ per operation (Inverse Ackermann function $\alpha(n)$).
    **複雜度：** 每次操作幾乎為 $O(1)$（反阿克曼函數 $\alpha(n)$）。
*   **When to use:** Dynamic connectivity, cycle detection in undirected graphs, Kruskal's MST.
    **適用場景：** 動態連結性，無向圖中的環檢測，Kruskal 最小生成樹。

### C. Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 頂點的線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** Resolving prerequisites (like compiling code dependencies).
    **直覺：** 解決先決條件（如編譯程式碼依賴關係）。
*   **Complexity:** $O(V + E)$.
    **複雜度：** $O(V + E)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Shortest Path with States (帶狀態的最短路徑)
Instead of just `dist[node]`, use `dist[node][state]` (e.g., remaining fuel, number of stops).
不只使用 `dist[node]`，而是使用 `dist[node][state]`（例如：剩餘燃料、中途停留次數）。

### Pattern 2: "Is it Connected?" (連結性問題)
Use Union-Find to merge edges dynamically or count connected components.
使用 Union-Find 動態合併邊或計算連通分量。

### Pattern 3: Critical Connections (關鍵連結)
Finding edges that, if removed, disconnect the graph (Bridges). Requires Tarjan’s algorithm (DFS with `discovery` and `low` times).
尋找那些一旦移除就會使圖斷開的邊（橋樑）。需要 Tarjan 演算法（帶有 `discovery` 和 `low` 時間的 DFS）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Critical Connections in a Network (LeetCode 1192)
**問題重述：**
Given a network of `n` servers and a list of `connections` (undirected edges), find all "critical connections." A connection is critical if removing it makes some servers unable to reach some other server.
給定由 `n` 個伺服器組成的網路與一份 `connections`（無向邊）清單，找出所有「關鍵連結」。如果移除某個連結會導致某些伺服器無法連接到其他伺服器，則該連結為關鍵連結。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Iterate through every edge, remove it temporarily.
    *   Run BFS/DFS to check if the graph is still connected.
    *   **Complexity:** $O(E \cdot (V+E))$, too slow for $N=10^5$.
    *   **複雜度：** $O(E \cdot (V+E))$，對於 $N=10^5$ 來說太慢。

2.  **Optimization (Best Solution - Tarjan's Bridge-Finding):**
    *   Use DFS to traverse the graph. Keep track of the time we first visit a node (`disc`) and the lowest discovery time reachable from that node (including back-edges) (`low`).
    *   使用 DFS 遍歷圖。記錄我們首次訪問節點的時間（`disc`）以及從該節點可到達的最低發現時間（包含回邊）（`low`）。
    *   If for an edge $u \to v$, we find that `low[v] > disc[u]`, it means there is no back-edge from $v$ (or its descendants) to $u$ (or its ancestors). Thus, $u \to v$ is a bridge.
    *   如果對於邊 $u \to v$，我們發現 `low[v] > disc[u]`，這意味著從 $v$（或其後代）沒有回邊可以連回 $u$（或其祖先）。因此，$u \to v$ 是一座橋。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

class Solution {
public:
    // Global timer for DFS discovery time
    // DFS 發現時間的全域計時器
    int timer;
    
    // Result list to store critical edges
    // 儲存關鍵邊的結果列表
    vector<vector<int>> bridges;
    
    // Adjacency list for the graph
    // 圖的鄰接表
    vector<vector<int>> adj;
    
    // Arrays to store discovery time and lowest reachable time
    // 儲存發現時間與最低可達時間的陣列
    vector<int> disc;
    vector<int> low;

    void dfs(int u, int p = -1) {
        disc[u] = low[u] = timer++;
        
        for (int v : adj[u]) {
            if (v == p) {
                // Do not go back to parent immediately in undirected graph
                // 在無向圖中，不要立即走回父節點
                continue; 
            }
            
            if (disc[v] != -1) {
                // If v is already visited, it's a back-edge.
                // Update low[u] using disc[v] (not low[v]!).
                // 如果 v 已被訪問，這是一條回邊。
                // 使用 disc[v] 更新 low[u]（注意不是 low[v]！）。
                low[u] = min(low[u], disc[v]);
            } else {
                // If v is not visited, recurse.
                // 如果 v 未被訪問，遞迴處理。
                dfs(v, u);
                
                // On return, update low[u] based on child's low value.
                // 返回時，根據子節點的 low 值更新 low[u]。
                low[u] = min(low[u], low[v]);
                
                // Check bridge condition
                // 檢查橋樑條件
                if (low[v] > disc[u]) {
                    bridges.push_back({u, v});
                }
            }
        }
    }

    vector<vector<int>> criticalConnections(int n, vector<vector<int>>& connections) {
        // Initialize data structures
        // 初始化資料結構
        adj.resize(n);
        disc.assign(n, -1);
        low.assign(n, -1);
        timer = 0;
        
        // Build the graph
        // 建構圖
        for (const auto& edge : connections) {
            adj[edge[0]].push_back(edge[1]);
            adj[edge[1]].push_back(edge[0]);
        }
        
        // Start DFS from node 0 (assuming graph is connected initially)
        // 從節點 0 開始 DFS（假設圖初始是連通的）
        dfs(0);
        
        return bridges;
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Dijkstra** | **Bellman-Ford** | Dijkstra is faster ($O(E \log V)$) but fails with negative weights. Bellman-Ford handles negative weights but is slower ($O(VE)$). <br> Dijkstra 較快但無法處理負權重；Bellman-Ford 可處理負權重但較慢。 |
| **Back-edge (Tarjan)** | **Parent-edge** | In undirected graphs, a back-edge connects to an ancestor that is NOT the immediate parent. <br> 在無向圖中，回邊連接到非直接父節點的祖先。 |
| **Kruskal's** | **Prim's** | Kruskal's adds edges (good for sparse graphs, uses Union-Find). Prim's adds nodes (good for dense graphs, uses Priority Queue). <br> Kruskal 加邊（適合稀疏圖，用 Union-Find）；Prim 加點（適合稠密圖，用 Priority Queue）。 |
| **Topological Sort** | **Cycle Detection** | Topo sort only exists in DAGs (Directed Acyclic Graphs). If a cycle exists, Topo sort is impossible. <br> 拓撲排序僅存在於 DAG 中。若存在環，則無法進行拓撲排序。 |

---

## 6. Interview Strategy (面試實戰建議)

### A. Narrative Framework (闡述口條框架)
1.  **Model the Problem:** "This looks like a graph problem where cities are nodes and flight costs are weights."
    **問題建模：** 「這看起來像個圖論問題，城市是節點，機票費用是權重。」
2.  **Choose the Algorithm:** "Since we need the shortest path and weights are positive, Dijkstra is optimal."
    **選擇演算法：** 「因為我們需要最短路徑且權重為正，Dijkstra 是最佳選擇。」
3.  **Discuss Complexity:** "Using a heap, time complexity will be $O(E \log V)$."
    **討論複雜度：** 「使用堆積，時間複雜度將是 $O(E \log V)$。」

### B. Whiteboard Strategy (白板策略)
*   **Draw the Graph:** Don't just write code. Draw nodes and edges to visualize the traversal.
    **畫出圖形：** 不要只寫程式碼。畫出節點與邊來視覺化遍歷過程。
*   **Define State:** Clearly write what your `visited` set or `dist` array stores.
    **定義狀態：** 清楚寫下你的 `visited` 集合或 `dist` 陣列儲存什麼。

### C. Common Follow-ups (常見追問)
*   "What if the graph is dynamic (edges added/removed)?" -> Suggest Union-Find or dynamic graph algorithms.
    「如果圖是動態的（邊會新增/移除）怎麼辦？」 -> 建議 Union-Find 或動態圖演算法。
*   "What if the graph is too large for memory?" -> Discuss distributed BFS or storing adjacency lists in a database.
    「如果圖太大無法放入記憶體？」 -> 討論分散式 BFS 或將鄰接表存入資料庫。

---

## 7. Practice Questions (練習題)

### Level 1: Easy/Intermediate (Concept Check)
**Problem:** **Network Delay Time (LeetCode 743)**
*   **Hint:** Standard Dijkstra. Find the max value in the distance array after traversal.
*   **提示：** 標準 Dijkstra。遍歷後找出距離陣列中的最大值。

### Level 2: Intermediate (Logic)
**Problem:** **Course Schedule II (LeetCode 210)**
*   **Hint:** Topological Sort. Detect cycles. If a cycle exists, return empty. Use `indegree` array and a queue.
*   **提示：** 拓撲排序。檢測環。若存在環則返回空。使用 `indegree` 陣列與佇列。

### Level 3: Advanced (Application)
**Problem:** **Alien Dictionary (LeetCode 269)**
*   **Hint:** Build a graph from character order differences. `w[i]` vs `w[i+1]` gives an edge. Then run Topological Sort. Handle edge cases (prefix issues).
*   **提示：** 根據字元順序差異建構圖。`w[i]` 與 `w[i+1]` 形成一條邊。接著執行拓撲排序。需處理邊界情況（前綴問題）。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
*   [ ] **Directed or Undirected?** (Does $A \to B$ imply $B \to A$?)
    **有向還是無向？**（$A \to B$ 是否隱含 $B \to A$？）
*   [ ] **Weighted or Unweighted?** (BFS vs Dijkstra)
    **加權還是無權？**（BFS vs Dijkstra）
*   [ ] **Cyclic or Acyclic?** (Need `visited` array or `recursion stack` tracking?)
    **有環還是無環？**（需要 `visited` 陣列或 `遞迴堆疊` 追蹤嗎？）
*   [ ] **Connectivity?** (Is the graph guaranteed to be one component?)
    **連通性？**（保證圖是單一連通分量嗎？）

### Debugging (除錯)
*   [ ] Did I handle the start node distance (0) and others (infinity)?
    我是否處理了起點距離（0）和其他點（無窮大）？
*   [ ] In Dijkstra, did I use `priority_queue<pair<int, int>, ... greater...>` (Min-Heap)? Default C++ PQ is Max-Heap.
    在 Dijkstra 中，我是否使用了 `greater`（最小堆積）？C++ 預設 PQ 是最大堆積。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **Dijkstra:** Like pouring water on the floor. It spreads to the lowest/closest points first.
    **Dijkstra：** 像是在地板上倒水。它會先流向最低/最近的地方。
*   **Union-Find:** Like corporate mergers. Each employee points to their boss. When two companies merge, one CEO reports to the other. Path compression is employees remembering the CEO directly.
    **Union-Find：** 像是企業合併。每個員工指向老闆。兩間公司合併時，一位 CEO 向另一位匯報。路徑壓縮就是員工直接記住大老闆是誰。
*   **Topological Sort:** Like putting on clothes. Underwear before pants, pants before shoes.
    **拓撲排序：** 像是穿衣服。先穿內褲再穿褲子，先穿褲子再穿鞋子。