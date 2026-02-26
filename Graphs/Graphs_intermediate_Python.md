# Graph Algorithms: Intermediate Guide
# 圖演算法：中階指南

## 1. Learning Objectives（學習目標）

1.  **Master Graph Modeling**: Learn to recognize "implicit graphs" in problems that don't explicitly mention nodes and edges (e.g., state transitions, dependency resolution).
    **掌握圖的建模**：學會識別那些沒有明確提及節點與邊的「隱式圖」問題（例如：狀態轉移、依賴解析）。

2.  **Proficiency in Topological Sort**: Understand when and how to apply Kahn’s Algorithm or DFS for dependency problems.
    **精通拓撲排序**：理解何時以及如何應用 Kahn 演算法或 DFS 來解決依賴性問題。

3.  **Union-Find (Disjoint Set) Mastery**: Implement Union-Find efficiently with path compression and union by rank for connectivity problems.
    **掌握並查集（Union-Find）**：高效實作具備路徑壓縮與按秩合併功能的並查集，以解決連通性問題。

4.  **Differentiate Search Strategies**: Clearly distinguish when to use BFS (shortest path in unweighted graphs) vs. DFS (exhausting paths, cycle detection) vs. Dijkstra (weighted graphs).
    **區分搜尋策略**：清楚區分何時使用 BFS（無權圖最短路徑）、DFS（窮盡路徑、環檢測）與 Dijkstra（加權圖）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
A graph is simply a collection of objects (nodes/vertices) and the relationships (edges) between them.
圖僅僅是物件（節點/頂點）以及它們之間關係（邊）的集合。

For Senior Engineers, the intuition should shift from "traversing a structure" to "propagating states" or "managing connectivity."
對於資深工程師而言，直覺應從「遍歷結構」轉變為「傳播狀態」或「管理連通性」。

### Representations（表示法）
1.  **Adjacency List (鄰接表)**:
    *   `Map<Node, List<Node>>` or `List<List<int>>`.
    *   **Pros**: Space efficient $O(V+E)$, fast iteration over neighbors.
    *   **Cons**: Slow to check if edge $(u, v)$ exists ($O(\text{degree of } u)$).
    *   **優點**：空間效率高 $O(V+E)$，遍歷鄰居快。
    *   **缺點**：檢查邊 $(u, v)$ 是否存在較慢 ($O(\text{degree of } u)$)。
2.  **Adjacency Matrix (鄰接矩陣)**:
    *   `int[][]` or `bool[][]`.
    *   **Pros**: $O(1)$ edge check.
    *   **Cons**: $O(V^2)$ space. Only suitable for dense graphs or small $V$ ($V < 1000$).
    *   **優點**：$O(1)$ 檢查邊。
    *   **缺點**：$O(V^2)$ 空間。僅適用於稠密圖或 $V$ 較小的情況。

### Complexity（複雜度）
*   **Time**: Generally $O(V + E)$ for traversal (BFS/DFS).
    **時間**：遍歷通常為 $O(V + E)$。
*   **Space**: $O(V)$ for recursion stack or queue, plus $O(V + E)$ for graph storage.
    **空間**：遞迴堆疊或佇列為 $O(V)$，加上圖存儲的 $O(V + E)$。

### When to Use / Not to Use（適用與不適用場景）
*   **Use when**: Relationships are many-to-many, finding shortest paths, detecting cycles, or analyzing network connectivity.
    **適用時機**：關係是多對多、尋找最短路徑、檢測環或分析網路連通性時。
*   **Avoid when**: The data is strictly hierarchical (use Trees) or linear (use Arrays/Lists), or when random access by index is the primary operation.
    **避免時機**：數據是嚴格分層的（使用樹）或線性的（使用陣列/鏈表），或者當透過索引隨機存取是主要操作時。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Topological Sort (Kahn's Algorithm)
*   **Scenario**: Course schedules, build systems, resolving dependencies.
*   **Logic**: Track `indegree`. Process nodes with 0 indegree, remove them, and update neighbors.
*   **場景**：課程表、構建系統、解析依賴。
*   **邏輯**：追蹤 `入度`。處理入度為 0 的節點，移除它們，並更新鄰居。

### B. Union-Find (Disjoint Set Union - DSU)
*   **Scenario**: Counting connected components, checking if adding an edge creates a cycle in undirected graphs, "friends circles".
*   **Logic**: `find(x)` gets the representative; `union(x, y)` merges sets.
*   **場景**：計算連通分量、檢查無向圖加邊是否成環、「朋友圈」問題。
*   **邏輯**：`find(x)` 取得代表元；`union(x, y)` 合併集合。

### C. Multi-Source BFS
*   **Scenario**: "Rotten Oranges", "01 Matrix", spreading infection from multiple points simultaneously.
*   **Logic**: Initialize Queue with *all* starting nodes (distance 0) instead of just one.
*   **場景**：「腐爛的橘子」、「01 矩陣」、從多點同時擴散感染。
*   **邏輯**：初始化佇列時放入 *所有* 起始節點（距離為 0），而非僅放入一個。

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule II (LeetCode 210)
**Problem Statement**:
You are given a total of `numCourses` courses labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return the ordering of courses you should take to finish all courses. If there are multiple valid answers, return any of them. If it is impossible, return an empty array.

**問題重述**：
給定 `numCourses` 門課程，編號為 `0` 到 `numCourses - 1`。給定一個陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修讀課程 `a`，必須先修讀課程 `b`。請回傳修完所有課程的順序。若有多種有效答案，回傳其中任意一種。若無法完成，回傳空陣列。

### Approach: From Brute Force to Optimal（思路：暴力 → 優化 → 最佳解）

1.  **Brute Force (Permutations)**: Try every permutation of courses and check if it satisfies prerequisites.
    **暴力法（排列）**：嘗試課程的所有排列組合，檢查是否滿足先修條件。
    *   *Complexity*: $O(N! \cdot E)$. Impossible for $N > 10$.
    *   *複雜度*：$O(N! \cdot E)$。當 $N > 10$ 時不可行。

2.  **DFS with Cycle Detection**: Build the graph. Use DFS to visit nodes. We need 3 states: `Unvisited`, `Visiting` (current recursion stack), `Visited`. If we meet a `Visiting` node, there is a cycle.
    **DFS 搭配環檢測**：建立圖。使用 DFS 訪問節點。我們需要 3 種狀態：`未訪問`、`訪問中`（當前遞迴堆疊）、`已訪問`。若遇到 `訪問中` 的節點，表示有環。

3.  **Optimal: Kahn's Algorithm (BFS based Topological Sort)**:
    **最佳解：Kahn 演算法（基於 BFS 的拓撲排序）**：
    *   Calculate `indegree` for all nodes.
    *   Push all nodes with `indegree == 0` into a Queue.
    *   While Queue is not empty: Pop node, add to result, decrement neighbors' indegree. If neighbor becomes 0, push to Queue.
    *   If result length != numCourses, a cycle exists.
    *   計算所有節點的 `入度`。
    *   將所有 `入度 == 0` 的節點放入佇列。
    *   當佇列非空：取出節點，加入結果，將鄰居入度減一。若鄰居入度變為 0，放入佇列。
    *   若結果長度 != numCourses，表示存在環。

### Python Solution (Kahn's Algorithm)

```python
from collections import deque
from typing import List

class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        # Build the graph and calculate indegrees
        # 建立圖並計算入度
        adj = {i: [] for i in range(numCourses)}
        indegree = {i: 0 for i in range(numCourses)}
        
        for dest, src in prerequisites:
            adj[src].append(dest)
            indegree[dest] += 1
            
        # Initialize the queue with nodes having 0 indegree (no dependencies)
        # 初始化佇列，放入入度為 0 的節點（無依賴）
        queue = deque([k for k, v in indegree.items() if v == 0])
        
        topo_order = []
        
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            
            # Reduce indegree of neighbors
            # 減少鄰居的入度
            for neighbor in adj[node]:
                indegree[neighbor] -= 1
                # If indegree becomes 0, it's ready to be processed
                # 若入度變為 0，表示可以被處理
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we processed all nodes, return the order. Otherwise, there is a cycle.
        # 若處理了所有節點，回傳順序。否則，表示存在環。
        return topo_order if len(topo_order) == numCourses else []

# Complexity Analysis:
# Time: O(V + E) - We visit every node and every edge once.
# Space: O(V + E) - Adjacency list and indegree array.
# 複雜度分析：
# 時間：O(V + E) - 我們訪問每個節點和每條邊各一次。
# 空間：O(V + E) - 鄰接表與入度陣列。
```

### Common Mistake (錯誤示範)
Using simple `visited` set (boolean) for DFS cycle detection in a directed graph.
在有向圖中使用簡單的 `visited` 集合（布林值）進行 DFS 環檢測。

*   **Why it fails**: In a directed graph, node A pointing to B, and C pointing to B is valid (merge). A simple `visited` set might flag B as "visited" when coming from C, falsely claiming a cycle or stopping valid traversal. You need the "Visiting" (currently in stack) state.
*   **為何失敗**：在有向圖中，節點 A 指向 B，且 C 指向 B 是合法的（匯合）。簡單的 `visited` 集合可能在從 C 到達 B 時將 B 標記為「已訪問」，錯誤地報告環的存在或停止合法的遍歷。你需要「訪問中」（當前在堆疊中）的狀態。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Key Distinction (關鍵區別) |
| :--- | :--- | :--- |
| **Directed Graph Cycle** | **Undirected Graph Cycle** | Directed needs "Recursion Stack" tracking (3 colors). Undirected just needs `visited` check (and ensuring not going back to parent). <br> 有向圖需要「遞迴堆疊」追蹤（三色標記）。無向圖僅需 `visited` 檢查（並確保不回頭找父節點）。 |
| **DFS** | **Backtracking** | DFS is a traversal strategy. Backtracking is DFS *plus* resetting state after visiting to explore other possibilities. <br> DFS 是遍歷策略。回溯是 DFS *加上* 訪問後重置狀態以探索其他可能性。 |
| **Connectivity** | **Strong Connectivity** | Connectivity (Undirected): Path exists between any two nodes. Strong Connectivity (Directed): Path exists $A \to B$ AND $B \to A$. <br> 連通性（無向）：任意兩點間存在路徑。強連通性（有向）：存在 $A \to B$ 且 $B \to A$ 的路徑。 |
| **Dijkstra** | **BFS** | Use BFS for unweighted graphs. Use Dijkstra for weighted non-negative graphs. <br> 無權圖用 BFS。非負加權圖用 Dijkstra。 |

---

## 6. Interview Strategy（面試實戰建議）

### Clarification Framework (口條框架)
1.  **Graph Type**: "Is the graph directed or undirected? Weighted or unweighted?"
    **圖的類型**：「請問圖是有向還是無向？加權還是無權？」
2.  **Constraints**: "Are there cycles? Is the graph connected? What is the range of $V$ and $E$?" (Determines Matrix vs List).
    **限制條件**：「會有環嗎？圖是連通的嗎？$V$ 和 $E$ 的範圍是多少？」（決定用矩陣還是鄰接表）。
3.  **Input Format**: "Is the input an adjacency list, edge list, or matrix?"
    **輸入格式**：「輸入是鄰接表、邊列表還是矩陣？」

### Whiteboard Strategy (白板策略)
*   **Draw it out**: Always draw a small graph (e.g., 3-4 nodes) to visualize the relationship.
    **畫出來**：永遠先畫一個小圖（例如 3-4 個節點）來視覺化關係。
*   **Define Variables**: Explicitly write `N = nodes`, `adj = graph`.
    **定義變數**：明確寫下 `N = 節點數`, `adj = 圖`。
*   **Corner Cases**: Write down "Disconnected Graph" and "Cycle" on the side as reminders.
    **邊界情況**：在旁邊寫下「非連通圖」和「環」作為提醒。

### Common Follow-up
*   **Q**: "How to handle if the graph is too large for memory?"
    **問**：「如果圖太大無法放入記憶體怎麼辦？」
*   **A**: Discuss **Distributed BFS** (MapReduce) or storing the adjacency list in a database/disk and loading chunks. Mention dealing with boundary nodes between chunks.
    **答**：討論 **分散式 BFS** (MapReduce) 或將鄰接表存入資料庫/磁碟並分塊讀取。提及處理分塊間的邊界節點。

---

## 7. Practice Problems（練習題）

### 1. Easy: Number of Islands (LeetCode 200)
*   **Goal**: Count connected components in a grid.
*   **Hint**: Treat grid as a graph. Iterate loops. If `grid[i][j] == '1'`, trigger BFS/DFS/Union-Find to mark all connected land as visited.
*   **目標**：計算網格中的連通分量。
*   **提示**：將網格視為圖。遍歷迴圈。若 `grid[i][j] == '1'`，觸發 BFS/DFS/Union-Find 將所有相連陸地標記為已訪問。

### 2. Medium: Redundant Connection (LeetCode 684)
*   **Goal**: Find an edge that causes a cycle in an undirected graph.
*   **Hint**: Classic **Union-Find**. Iterate edges; if both nodes already have the same parent, that edge is the answer.
*   **目標**：找出無向圖中導致成環的那條邊。
*   **提示**：經典 **Union-Find**。遍歷邊；若兩節點已有相同父節點，該邊即為答案。

### 3. Medium/Hard: Network Delay Time (LeetCode 743)
*   **Goal**: Find time for signal to reach all nodes (Shortest Path in Weighted Graph).
*   **Hint**: Use **Dijkstra’s Algorithm** with a Min-Heap. BFS will fail because edges have weights. Return the max distance found, or -1 if not all reachable.
*   **目標**：計算訊號到達所有節點所需時間（加權圖最短路徑）。
*   **提示**：使用搭配最小堆積（Min-Heap）的 **Dijkstra 演算法**。BFS 會失敗，因為邊有權重。回傳找到的最大距離，若非全部可達則回傳 -1。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Visited Set**: Did I initialize a `visited` set to prevent infinite loops?
    **已訪問集合**：我是否初始化了 `visited` 集合以防止無窮迴圈？
*   [ ] **Disconnected Components**: Did I loop through *all* nodes (0 to N-1) to start traversal, not just node 0?
    **非連通分量**：我是否遍歷了 *所有* 節點（0 到 N-1）來開始遍歷，而不僅僅是節點 0？
*   [ ] **Graph Build**: Did I handle both directions if the graph is undirected? (`adj[u].append(v)` AND `adj[v].append(u)`)
    **建圖**：若是無向圖，我是否處理了兩個方向？（`adj[u].append(v)` 和 `adj[v].append(u)`）
*   [ ] **Complexity**: Is my solution $O(V+E)$ or did I accidentally nest loops making it $O(V^2)$?
    **複雜度**：我的解法是 $O(V+E)$ 嗎？還是我不小心巢狀迴圈導致變成 $O(V^2)$？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

*   **Kahn's Algorithm**: Think of **"Peeling an Onion"** or **"Eating Grapes"**. You pick the grapes hanging loose (indegree 0), which exposes new stems (reduces neighbor indegree), allowing you to pick more.
    **Kahn 演算法**：想像 **「剝洋蔥」** 或 **「吃葡萄」**。你摘下懸掛著的葡萄（入度為 0），這會暴露出新的梗（減少鄰居入度），讓你這摘更多。

*   **Union-Find**: Think of **"Corporate Mergers"**. Every employee points to their manager. `find()` goes up the chain to the CEO. `union()` makes one CEO report to the other.
    **Union-Find**：想像 **「企業併購」**。每個員工指向經理。`find()` 向上追溯到 CEO。`union()` 讓一位 CEO 向另一位匯報。

*   **DFS vs BFS**:
    *   **DFS**: A maze runner touching the wall with one hand, going as deep as possible before turning back. (Depth).
    *   **BFS**: Dropping a stone in water, ripples expanding in circles. (Layers/Breadth).
    *   **DFS**：走迷宮的人單手扶牆，走得越深越好，直到必須回頭。（深度）
    *   **BFS**：將石頭丟入水中，漣漪呈圓形向外擴散。（層級/廣度）