# Advanced Graphs: Interview Masterclass
# 進階圖論：面試大師班

## 1. Learning Goals (學習目標)

1.  **Master Advanced Traversal Algorithms**: Move beyond basic BFS/DFS to understand Dijkstra, Topological Sort, and Union-Find (Disjoint Set).
    **掌握進階遍歷演算法**：超越基礎的 BFS/DFS，深入理解 Dijkstra、拓撲排序（Topological Sort）與並查集（Union-Find）。

2.  **Detect Complex Graph Properties**: Efficiently identify cycles, connected components, and bridges/articulation points in large-scale systems.
    **檢測複雜圖屬性**：在大規模系統中高效識別環（Cycles）、連通分量（Connected Components）以及橋接點/關節點（Bridges/Articulation Points）。

3.  **Optimize for Scalability**: Understand the trade-offs between Adjacency Matrix and Adjacency List, and apply heuristics (like A*) or pruning where applicable.
    **優化可擴展性**：理解鄰接矩陣與鄰接表之間的權衡，並在適用時應用啟發式算法（如 A*）或剪枝策略。

4.  **Model Real-World Problems**: Translate abstract dependency or routing problems into graph representations instantly.
    **為現實問題建模**：能瞬間將抽象的依賴關係或路由問題轉化為圖的表示形式。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
-   **Graph ($G = (V, E)$)**: A collection of nodes (vertices) and edges connecting them.
    **圖 ($G = (V, E)$)**：節點（頂點）與連接它們的邊的集合。
-   **Advanced Intuition**: Think of graphs not just as maps, but as **state machines** or **dependency networks**.
    **進階直覺**：不要只把圖看作地圖，應將其視為**狀態機**或**依賴網絡**。

### Complexity (複雜度)
-   **Time**: Generally $O(V + E)$ for traversal. $O(E \log V)$ for Dijkstra (using Binary Heap).
    **時間**：遍歷通常為 $O(V + E)$。Dijkstra 為 $O(E \log V)$（使用二元堆積）。
-   **Space**: $O(V + E)$ for Adjacency List; $O(V^2)$ for Adjacency Matrix.
    **空間**：鄰接表為 $O(V + E)$；鄰接矩陣為 $O(V^2)$。

### When to Use (適用場景)
-   **Shortest Path (Weighted)**: Dijkstra (non-negative weights), Bellman-Ford (negative weights).
    **最短路徑（帶權重）**：Dijkstra（非負權重），Bellman-Ford（負權重）。
-   **Connectivity / Grouping**: Union-Find.
    **連通性 / 分組**：並查集（Union-Find）。
-   **Dependency Resolution**: Topological Sort.
    **依賴解析**：拓撲排序。

### When NOT to Use (不適用場景)
-   **Simple Linear Data**: If the data has no branching or cycles, Arrays or Linked Lists are sufficient.
    **簡單線性數據**：如果數據沒有分支或循環，陣列或鏈結串列就足夠了。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Topological Sort (Kahn's Algorithm / DFS)
-   **Use Case**: Build systems, course schedules, task serialization.
    **使用案例**：建置系統、課程表、任務序列化。
-   **Key**: Indegree array (Kahn's) or Post-order DFS reversal.
    **關鍵**：入度陣列（Kahn 演算法）或後序 DFS 反轉。

### B. Union-Find (Disjoint Set Union - DSU)
-   **Use Case**: Cycle detection in undirected graphs, counting connected components, Kruskal’s MST.
    **使用案例**：無向圖中的環檢測、計算連通分量、Kruskal 最小生成樹。
-   **Optimization**: Path Compression + Union by Rank/Size (Amortized $O(\alpha(N)) \approx O(1)$).
    **優化**：路徑壓縮 + 按秩/大小合併（均攤複雜度 $O(\alpha(N)) \approx O(1)$）。

### C. Dijkstra’s Algorithm
-   **Use Case**: Shortest path in weighted graphs (e.g., network latency, flight costs).
    **使用案例**：帶權圖的最短路徑（例如：網絡延遲、航班成本）。
-   **Key**: Priority Queue (Min-Heap) + `dist` array.
    **關鍵**：優先佇列（最小堆積）+ `dist` 陣列。

### D. Tarjan’s / Kosaraju’s Algorithm (Advanced)
-   **Use Case**: Finding Strongly Connected Components (SCCs) or Bridges (Critical Connections).
    **使用案例**：尋找強連通分量（SCCs）或橋（關鍵連接）。
-   **Key**: `discovery_time` and `low_link` values.
    **關鍵**：`discovery_time`（發現時間）與 `low_link`（低位連結）值。

---

## 4. Example Walkthrough (範例講解)

### Problem: Critical Connections in a Network (Finding Bridges)
### 問題：網絡中的關鍵連接（尋找橋）

**Problem Statement (問題重述)**:
There are `n` servers numbered from `0` to `n-1` connected by undirected server-to-server `connections`.
有 `n` 個伺服器，編號從 `0` 到 `n-1`，通過無向的 `connections` 相互連接。
Return all critical connections. A critical connection is a connection that, if removed, will make some servers unable to reach some other server.
返回所有關鍵連接。關鍵連接是指如果移除該連接，將導致某些伺服器無法連接到其他伺服器。

---

#### 1. Approach: Brute Force (暴力解)
-   **Idea**: Iterate through every edge, remove it, and run DFS/BFS to check if the graph is still connected.
    **思路**：遍歷每一條邊，將其移除，然後執行 DFS/BFS 檢查圖是否仍然連通。
-   **Complexity**: $O(E \times (V + E))$. Too slow for large graphs.
    **複雜度**：$O(E \times (V + E))$。對於大型圖來說太慢。

#### 2. Optimization: Tarjan's Algorithm (Rank/Low-Link) (最佳解)
-   **Concept**: Use DFS to track the depth (rank) of each node.
    **概念**：使用 DFS 追蹤每個節點的深度（秩）。
-   **Low-Link Value**: The lowest rank reachable from the current node (including back-edges).
    **低位連結值**：從當前節點可到達的最低秩（包括回邊）。
-   **Condition**: If `low[neighbor] > rank[node]`, it means the neighbor has no way back to `node` or its ancestors without this edge. Thus, it's a bridge.
    **條件**：如果 `low[neighbor] > rank[node]`，這意味著鄰居在沒有這條邊的情況下無法回到 `node` 或其祖先。因此，這是一座橋。

#### 3. Python Solution (Advanced)

```python
from typing import List, Dict, Set
import collections

class Solution:
    def criticalConnections(self, n: int, connections: List[List[int]]) -> List[List[int]]:
        # Build the graph using adjacency list
        # 使用鄰接表構建圖
        graph = collections.defaultdict(list)
        for u, v in connections:
            graph[u].append(v)
            graph[v].append(u)
        
        # Arrays to store discovery time (rank) and lowest reachable rank
        # 用於存儲發現時間（秩）和最低可達秩的陣列
        # Initialize with -1 to represent unvisited
        # 初始化為 -1 代表未訪問
        rank = [-1] * n
        low = [-1] * n
        
        bridges = []
        self.time = 0  # Global timer / 全局計時器
        
        def dfs(node: int, parent: int):
            # Set discovery time and low-link value
            # 設定發現時間與低位連結值
            rank[node] = low[node] = self.time
            self.time += 1
            
            for neighbor in graph[node]:
                if neighbor == parent:
                    # Don't go back along the tree edge immediately
                    # 不要立即沿著樹邊返回
                    continue
                
                if rank[neighbor] == -1:
                    # Neighbor not visited, continue DFS
                    # 鄰居未被訪問，繼續 DFS
                    dfs(neighbor, node)
                    
                    # On return, update low-link value
                    # 返回時，更新低位連結值
                    low[node] = min(low[node], low[neighbor])
                    
                    # Check bridge condition:
                    # If the neighbor cannot reach node or above, it's a bridge
                    # 檢查橋接條件：如果鄰居無法到達當前節點或更上層，則為橋
                    if low[neighbor] > rank[node]:
                        bridges.append([node, neighbor])
                else:
                    # Neighbor visited (Back-edge found)
                    # 鄰居已被訪問（發現回邊）
                    # Update low[node] based on the discovery time of the ancestor
                    # 根據祖先的發現時間更新 low[node]
                    low[node] = min(low[node], rank[neighbor])

        # Start DFS from node 0 (assuming connected graph for simplicity)
        # 從節點 0 開始 DFS（為簡化起見假設圖是連通的）
        dfs(0, -1)
        return bridges

# Time Complexity: O(V + E) - We visit every node and edge once.
# 時間複雜度：O(V + E) - 我們訪問每個節點和邊一次。
# Space Complexity: O(V + E) - Recursion stack and graph storage.
# 空間複雜度：O(V + E) - 遞迴堆疊與圖的存儲。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Back Edge (回邊)** | **Tree Edge (樹邊)** | Tree edges are part of the DFS structure; Back edges point to an ancestor, creating a cycle. <br> 樹邊是 DFS 結構的一部分；回邊指向祖先，形成環。 |
| **Dijkstra** | **BFS** | BFS finds shortest path in *unweighted* graphs. Dijkstra is for *weighted* graphs. <br> BFS 尋找*無權*圖的最短路徑。Dijkstra 用於*帶權*圖。 |
| **O(V+E)** | **O(V*E)** | Adjacency List traversal is $V+E$. Bellman-Ford or bad implementations are $V \times E$. <br> 鄰接表遍歷是 $V+E$。Bellman-Ford 或糟糕的實作為 $V \times E$。 |
| **Visited Set** | **Recursion Stack** | In directed cycle detection, you need to track nodes currently in the recursion stack, not just "visited". <br> 在有向圖環檢測中，你需要追蹤當前遞迴堆疊中的節點，而不僅僅是「已訪問」。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarify the Input (釐清輸入)
-   "Is the graph directed or undirected?" (圖是有向還是無向？)
-   "Can the graph have cycles?" (圖可能有環嗎？)
-   "Is the graph connected, or can there be disjoint parts?" (圖是連通的，還是可能有不相連的部分？)
-   "Are weights non-negative?" (權重是非負的嗎？ -> Crucial for Dijkstra).

### 2. Whiteboard Strategy (白板策略)
-   **Draw it out**: Draw a small graph with 4-5 nodes.
    **畫出來**：畫一個有 4-5 個節點的小圖。
-   **Define State**: Explicitly write what your variables mean (e.g., `dist[i]` = min distance from source to `i`).
    **定義狀態**：明確寫下變數的意義（例如：`dist[i]` = 從源點到 `i` 的最小距離）。
-   **Handle Disconnected Components**: Always wrap your traversal in a loop: `for i in range(n): if not visited[i]: bfs(i)`.
    **處理非連通分量**：總是將遍歷包裹在迴圈中：`for i in range(n): if not visited[i]: bfs(i)`。

### 3. Common Follow-ups (常見後續問題)
-   "How would you handle dynamic updates (edges added/removed)?" -> Mention **Union-Find** or dynamic graph algorithms.
    「你會如何處理動態更新（邊的增加/移除）？」-> 提及 **並查集** 或動態圖演算法。
-   "What if the graph is too large for memory?" -> Distributed Graph Processing (e.g., Pregel) or storing adjacency lists in a DB.
    「如果圖大到記憶體裝不下怎麼辦？」-> 分散式圖處理（如 Pregel）或將鄰接表存入資料庫。

---

## 7. Practice Problems (練習題)

### Level: Easy/Intermediate
**1. Number of Provinces (LeetCode 547)**
-   **Task**: Count connected components.
    **任務**：計算連通分量。
-   **Hint**: Classic Union-Find or DFS loop.
    **提示**：經典的並查集或 DFS 迴圈。
-   **Key**: Handle the adjacency matrix input correctly.
    **關鍵**：正確處理鄰接矩陣輸入。

### Level: Intermediate/Advanced
**2. Course Schedule II (LeetCode 210)**
-   **Task**: Return ordering of courses given prerequisites.
    **任務**：給定先修條件，返回課程順序。
-   **Hint**: Topological Sort. Detect cycles (impossible schedule).
    **提示**：拓撲排序。檢測環（不可能的課表）。
-   **Key**: Use an `indegree` array and a queue.
    **關鍵**：使用 `indegree`（入度）陣列和佇列。

### Level: Advanced
**3. Network Delay Time (LeetCode 743)**
-   **Task**: Find time for signal to reach all nodes.
    **任務**：找出訊號到達所有節點所需的時間。
-   **Hint**: Dijkstra's Algorithm.
    **提示**：Dijkstra 演算法。
-   **Key**: Use `heapq`. Max of the shortest paths is the answer. Return -1 if disconnected.
    **關鍵**：使用 `heapq`。最短路徑中的最大值即為答案。若不連通則返回 -1。

---

## 8. Quick Checklists (快速檢核表)

### Debugging / Logic Check (除錯/邏輯檢查)
-   [ ] **Directed vs Undirected**: Did I handle back-edges correctly? (有向 vs 無向：我是否正確處理了回邊？)
-   [ ] **Cycles**: Will my code infinite loop if there is a cycle? (環：如果有環，我的程式碼會無窮迴圈嗎？)
-   [ ] **Connectivity**: Did I visit *all* nodes, or just the ones connected to node 0? (連通性：我是訪問了*所有*節點，還是只訪問了連接到節點 0 的那些？)
-   [ ] **Initialization**: Are `visited` sets and `dist` arrays initialized correctly (e.g., infinity)? (初始化：`visited` 集合和 `dist` 陣列是否正確初始化（如無窮大）？)

### Complexity Check (複雜度確認)
-   [ ] Is it $O(V+E)$ or $O(V^2)$? (Did I iterate all nodes inside a node loop?)
    是 $O(V+E)$ 還是 $O(V^2)$？（我是否在節點迴圈內遍歷了所有節點？）

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

-   **Dijkstra is like Water Spreading**: Water flows through pipes; it reaches the closest points first. The priority queue manages the "wavefront".
    **Dijkstra 就像水流擴散**：水流經管道；它最先到達最近的點。優先佇列管理著「波前」。

-   **Union-Find is like Corporate Mergers**: Each set has a "CEO" (parent). `Union` means one CEO reports to another. Path compression is realizing you don't need to talk to middle-management; just talk to the CEO directly.
    **並查集就像公司合併**：每個集合都有一個「CEO」（父節點）。`Union` 意味著一位 CEO 向另一位匯報。路徑壓縮就是意識到你不需要跟中層管理對話，直接找 CEO 即可。

-   **Topological Sort is like Dressing Up**: You can't put on shoes (Node B) before socks (Node A).
    **拓撲排序就像穿衣服**：你不能在穿襪子（節點 A）之前穿鞋子（節點 B）。