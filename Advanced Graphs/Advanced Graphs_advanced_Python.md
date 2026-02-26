# Advanced Graphs Interview Guide (進階圖論面試指南)

## 1. Learning Objectives (學習目標)

*   **Master Shortest Path Algorithms beyond BFS:** Understand when and how to apply Dijkstra, Bellman-Ford, and Floyd-Warshall.
    **掌握 BFS 以外的最短路徑演算法：** 理解何時以及如何應用 Dijkstra、Bellman-Ford 與 Floyd-Warshall。
*   **Deep Dive into Connectivity:** Proficiency in Union-Find (Disjoint Set) for dynamic connectivity and Tarjan’s algorithm for Strongly Connected Components (SCC).
    **深入連通性問題：** 熟練使用並查集（Union-Find）處理動態連通性，以及 Tarjan 演算法處理強連通分量（SCC）。
*   **Topological Sorting & Dependency Resolution:** Solve complex dependency problems (like build systems or course schedules) using Kahn’s algorithm or DFS.
    **拓撲排序與依賴解析：** 使用 Kahn 演算法或 DFS 解決複雜的依賴問題（如建置系統或課程表）。
*   **Graph Modeling:** Ability to model abstract problems (e.g., currency exchange, word ladders) into graph representations.
    **圖形建模：** 具備將抽象問題（如匯率兌換、單字接龍）轉化為圖形表示的能力。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Dijkstra’s Algorithm (Dijkstra 演算法)
*   **Definition:** Finds the shortest path from a source node to all other nodes in a graph with non-negative edge weights.
    **定義：** 在邊權重非負的圖中，尋找從源節點到所有其他節點的最短路徑。
*   **Intuition:** A "Greedy" BFS using a Priority Queue. Always expand the "cheapest" known node first.
    **直覺：** 使用優先佇列（Priority Queue）的「貪婪」BFS。總是優先擴展已知「成本最低」的節點。
*   **Complexity:** $O(E \log V)$ using a binary heap.
    **複雜度：** 使用二元堆積時為 $O(E \log V)$。
*   **Use Case:** Google Maps routing, Network delay time.
    **適用場景：** Google Maps 路徑規劃、網路延遲時間。

### Union-Find / Disjoint Set Union (並查集)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個不相交子集的元素集合。
*   **Intuition:** Think of it as managing "gangs" or "clusters". You can merge two gangs (`union`) or check if two people belong to the same gang (`find`).
    **直覺：** 想像成管理「幫派」或「叢集」。你可以合併兩個幫派（`union`）或檢查兩個人是否屬於同一個幫派（`find`）。
*   **Complexity:** Nearly $O(1)$ on average (Inverse Ackermann function $\alpha(n)$) with Path Compression and Union by Rank.
    **複雜度：** 搭配路徑壓縮（Path Compression）與按秩合併（Union by Rank）後，平均接近 $O(1)$（反阿克曼函數 $\alpha(n)$）。

### Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 頂點的線性排序，使得對於每條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Applicability:** Only works on Directed Acyclic Graphs (DAGs).
    **適用性：** 僅適用於有向無環圖（DAG）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Shortest Path with States (帶狀態的最短路徑)
Instead of just `(node)`, the state in Dijkstra/BFS becomes `(node, k_stops_left)` or `(node, fuel_left)`.
Dijkstra/BFS 中的狀態不僅是 `(node)`，而是變為 `(node, k_stops_left)` 或 `(node, fuel_left)`。

### Pattern 2: Minimum Spanning Tree (MST) - Kruskal’s / Prim’s (最小生成樹)
Connecting all points with minimum total cost. Kruskal’s uses Union-Find; Prim’s uses Priority Queue.
以最小總成本連接所有點。Kruskal 使用並查集；Prim 使用優先佇列。

### Pattern 3: Cycle Detection (環的檢測)
*   **Undirected:** Union-Find or DFS (check if we visit a visited node that isn't parent).
    **無向圖：** 並查集或 DFS（檢查是否訪問到非父節點的已訪問節點）。
*   **Directed:** DFS (recursion stack tracking) or Kahn's Algorithm (nodes with non-zero in-degree remaining).
    **有向圖：** DFS（遞迴堆疊追蹤）或 Kahn 演算法（剩餘入度非零的節點）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Cheapest Flights Within K Stops (K 站中轉內的最便宜航班)
*(LeetCode 787 - Medium/Hard)*

**Problem Statement:**
There are `n` cities connected by some number of flights. You are given an array `flights` where `flights[i] = [from, to, price]`.
有 `n` 個城市通過若干航班連接。給定一個陣列 `flights`，其中 `flights[i] = [from, to, price]`。
You are also given three integers `src`, `dst`, and `k`, return the cheapest price from `src` to `dst` with at most `k` stops. If there is no such route, return -1.
同時給定三個整數 `src`、`dst` 和 `k`，返回從 `src` 到 `dst` 最多經過 `k` 次中轉的最便宜價格。如果不存在這樣的路線，則返回 -1。

---

### Approach 1: Plain Dijkstra (Standard but Flawed)
**思路：**
Standard Dijkstra finds the absolute shortest path based on cost.
標準 Dijkstra 根據成本尋找絕對最短路徑。
However, the shortest path might take `k+5` stops, while a slightly more expensive path takes `k-1` stops.
然而，最短路徑可能需要 `k+5` 次中轉，而一條稍微貴一點的路徑可能只需要 `k-1` 次中轉。
**Why it fails:** Standard Dijkstra greedily settles a node once. We might discard a valid path because it's currently more expensive, even if it uses fewer stops.
**為何失敗：** 標準 Dijkstra 會貪婪地結算節點。我們可能會因為某條路徑目前較貴而丟棄它，即使它的中轉次數較少。

### Approach 2: Modified Dijkstra (Optimal for Senior Level)
**思路：**
We keep track of `stops` in our Priority Queue.
我們在優先佇列中追蹤 `stops`（中轉次數）。
Crucially, we also need an array `min_stops[node]` to track the minimum stops used to reach a node *at the current price point* (or simply relax logic).
關鍵在於，我們還需要一個陣列 `min_stops[node]` 來追蹤到達某節點所用的最小中轉次數（或調整鬆弛邏輯）。
Actually, a better optimization is: only push to PQ if we reach a node with **fewer stops** than previously recorded, or **lower cost** (standard).
事實上，更好的優化是：只有當我們到達某節點的**中轉次數少於**之前的記錄，或者**成本更低**時，才將其推入 PQ。

### Python Solution (Modified Dijkstra)

```python
import heapq
from collections import defaultdict
from typing import List

class Solution:
    def findCheapestPrice(self, n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
        # Build the adjacency list (graph)
        # 建立鄰接表（圖）
        graph = defaultdict(list)
        for u, v, price in flights:
            graph[u].append((v, price))
        
        # Priority Queue: (current_cost, stops_taken, current_node)
        # 優先佇列：(當前成本, 已用中轉次數, 當前節點)
        # We order by cost primarily.
        # 我們主要按成本排序。
        pq = [(0, 0, src)]
        
        # Optimization: track minimum stops to reach each node to prune search
        # 優化：追蹤到達每個節點的最小中轉次數以修剪搜尋
        # Initialize with infinity.
        # 初始化為無窮大。
        stops_visited = [float('inf')] * n
        
        while pq:
            cost, stops, node = heapq.heappop(pq)
            
            # If we reached destination, return cost (guaranteed to be min due to heap)
            # 如果到達目的地，返回成本（由於堆積特性，保證為最小值）
            if node == dst:
                return cost
            
            # If we have already exceeded K stops, continue
            # stops represents edges traversed. k stops means k+1 edges allowed.
            # 如果已經超過 K 次中轉，繼續
            # stops 代表經過的邊數。k 次中轉意味著允許 k+1 條邊。
            if stops > k:
                continue
            
            # Pruning: If we reached this node before with fewer or equal stops, 
            # and presumably lower cost (since we popped earlier), skip.
            # 修剪：如果我們之前以更少或相等的中轉次數到達此節點，
            # 且假設成本更低（因為我們較早彈出），則跳過。
            if stops_visited[node] <= stops:
                continue
            
            # Update the stops record
            # 更新中轉記錄
            stops_visited[node] = stops
            
            # Explore neighbors
            # 探索鄰居
            for neighbor, price in graph[node]:
                heapq.heappush(pq, (cost + price, stops + 1, neighbor))
                
        return -1

# Time Complexity: O(E * K * log(E * K)) in worst case, or roughly O(E log V) optimized.
# 時間複雜度：最壞情況下為 O(E * K * log(E * K))，優化後約為 O(E log V)。
# Space Complexity: O(V + E + K) for graph and heap.
# 空間複雜度：O(V + E + K) 用於圖和堆積。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Dijkstra** | **Bellman-Ford** | Dijkstra requires **non-negative** weights; Bellman-Ford handles **negative** weights (and detects negative cycles). <br> Dijkstra 要求**非負**權重；Bellman-Ford 可處理**負**權重（並檢測負環）。 |
| **DFS** | **Backtracking** | DFS is a traversal strategy; Backtracking is DFS **with state reset** to explore all possibilities. <br> DFS 是一種遍歷策略；回溯法是**帶狀態重置**的 DFS，用於探索所有可能性。 |
| **Prim's** | **Kruskal's** | Prim's grows a tree from a node (good for dense graphs); Kruskal's merges edges (good for sparse graphs). <br> Prim 從一個節點生成樹（適合稠密圖）；Kruskal 合併邊（適合稀疏圖）。 |
| **Visited Set** | **Path Visited Set** | In cycle detection (directed), `visited` tracks global history, `path_visited` tracks current recursion stack. <br> 在有向圖環檢測中，`visited` 追蹤全域歷史，`path_visited` 追蹤當前遞迴堆疊。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarification & Constraints (釐清與限制)
*   **Directed or Undirected?** (Changes traversal logic).
    **有向還是無向？**（改變遍歷邏輯）。
*   **Weighted or Unweighted?** (Decides BFS vs Dijkstra).
    **有權重還是無權重？**（決定 BFS 還是 Dijkstra）。
*   **Cycles allowed?** (Affects termination conditions).
    **允許環嗎？**（影響終止條件）。
*   **Graph size (V, E)?** (If $V < 20$, maybe $O(2^N)$ or $O(N!)$ is okay. If $V = 10^5$, need $O(V+E)$ or $O(E \log V)$).
    **圖的大小 (V, E)？**（如果 $V < 20$，也許 $O(2^N)$ 或 $O(N!)$ 可以。如果 $V = 10^5$，需要 $O(V+E)$ 或 $O(E \log V)$）。

### 2. Whiteboard Strategy (白板策略)
*   **Draw the graph:** Even if abstract, draw nodes and edges.
    **畫出圖形：** 即使很抽象，也要畫出節點和邊。
*   **Define State:** Explicitly write what your queue stores: `Queue<(Node, Cost, State)>`.
    **定義狀態：** 明確寫出佇列儲存的內容：`Queue<(Node, Cost, State)>`。
*   **Dry Run:** Trace 2-3 steps manually before coding.
    **手動演練：** 在編碼前手動追蹤 2-3 步。

### 3. Common Follow-ups (常見後續問題)
*   "What if edge weights change dynamically?" (Discuss D* or re-running Dijkstra).
    「如果邊權重動態變化怎麼辦？」（討論 D* 或重新執行 Dijkstra）。
*   "How to handle negative weights?" (Bellman-Ford / SPFA).
    「如何處理負權重？」（Bellman-Ford / SPFA）。
*   "Can we distribute this?" (MapReduce for graph processing, Pregel).
    「我們可以分散式處理嗎？」（用於圖處理的 MapReduce，Pregel）。

---

## 7. Practice Questions (練習題)

### Level: Easy (Warm-up)
**Problem:** **Network Delay Time (LC 743)**
**Hint:** Classic Dijkstra. Find max of shortest paths to all nodes.
**提示：** 經典 Dijkstra。找出到所有節點的最短路徑中的最大值。
**Key:** Handle unreachable nodes (return -1).
**關鍵：** 處理無法到達的節點（返回 -1）。

### Level: Medium (Core Pattern)
**Problem:** **Course Schedule II (LC 210)**
**Hint:** Topological Sort. Use Indegree array and a Queue (Kahn's Algorithm).
**提示：** 拓撲排序。使用入度陣列和佇列（Kahn 演算法）。
**Key:** Detect cycles (if result length != total courses).
**關鍵：** 檢測環（如果結果長度 != 總課程數）。

### Level: Hard (Differentiation)
**Problem:** **Critical Connections in a Network (LC 1192)**
**Hint:** Find "Bridges" in a graph. Requires Tarjan’s Algorithm (DFS with `discovery_time` and `low_link` values).
**提示：** 尋找圖中的「橋」。需要 Tarjan 演算法（帶有 `discovery_time` 和 `low_link` 值的 DFS）。
**Key:** An edge `u-v` is a bridge if `low[v] > disc[u]`.
**關鍵：** 如果 `low[v] > disc[u]`，則邊 `u-v` 是一座橋。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Connectivity:** Did I handle disconnected graphs? (Loop through all nodes to start traversal).
    **連通性：** 我是否處理了非連通圖？（迴圈遍歷所有節點以開始遍歷）。
*   [ ] **Infinity:** Did I initialize distances to `infinity`?
    **無窮大：** 我是否將距離初始化為 `infinity`？
*   [ ] **Bi-directional:** If undirected, did I add edges `u->v` AND `v->u`?
    **雙向：** 如果是無向圖，我是否添加了 `u->v` 和 `v->u` 的邊？
*   [ ] **Complexity:** Is my Dijkstra $O(E \log V)$ (Heap) or $O(V^2)$ (Array)? Use Heap for sparse graphs.
    **複雜度：** 我的 Dijkstra 是 $O(E \log V)$（堆積）還是 $O(V^2)$（陣列）？稀疏圖請使用堆積。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **Dijkstra is like water flowing:**
    **Dijkstra 就像水流：**
    Water spreads to the nearest cracks first. It can't flow uphill (negative weights).
    水會先流向最近的裂縫。它不能倒流（負權重）。

*   **Union-Find is like Corporate Mergers:**
    **並查集就像企業合併：**
    Employees (nodes) report to managers (parents), who report to the CEO (root). Path compression is like employees getting the CEO's direct phone number to skip middle management.
    員工（節點）向經理（父節點）匯報，經理向 CEO（根節點）匯報。路徑壓縮就像員工拿到了 CEO 的直線電話，跳過了中層管理。

*   **Topological Sort is like Dressing Up:**
    **拓撲排序就像穿衣服：**
    You must put on socks (dependency) before shoes. Underwear before pants.
    你必須先穿襪子（依賴）再穿鞋子。先穿內褲再穿褲子。