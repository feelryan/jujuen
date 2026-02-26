# Advanced Graphs: Intermediate Level Guide
# 進階圖論：中級實戰指南

## 1. Learning Objectives (學習目標)

1.  **Master Topological Sort (Kahn’s Algorithm & DFS):** Understand how to handle dependency resolution and cycle detection in Directed Acyclic Graphs (DAGs).
    **掌握拓撲排序（Kahn 演算法與 DFS）：** 理解如何在有向無環圖（DAG）中處理依賴解析與環檢測。

2.  **Internalize Union-Find (Disjoint Set Union - DSU):** Implement `find` with path compression and `union` by rank/size to solve connectivity problems efficiently.
    **內化並查集（DSU）：** 實作具備路徑壓縮的 `find` 與按秩/大小合併的 `union`，以高效解決連通性問題。

3.  **Differentiate Shortest Path Algorithms:** Know precisely when to use BFS (unweighted) vs. Dijkstra (weighted, non-negative) vs. Bellman-Ford (negative weights).
    **區分最短路徑演算法：** 精確知道何時使用 BFS（無權重）、Dijkstra（有權重、非負）與 Bellman-Ford（負權重）。

4.  **Graph Modeling Capability:** Transform abstract problems (like currency exchange or software build orders) into standard graph representations.
    **圖形建模能力：** 將抽象問題（如貨幣匯率或軟體建置順序）轉化為標準的圖形表示法。

---

## 2. Core Concepts (核心觀念速覽)

### Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 頂點的線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** Organizing tasks where some tasks must be completed before others (e.g., University course prerequisites).
    **直覺：** 組織那些必須有先後順序的任務（例如：大學課程擋修機制）。
*   **Complexity:** Time $O(V + E)$, Space $O(V + E)$.
    **複雜度：** 時間 $O(V + E)$，空間 $O(V + E)$。
*   **Constraint:** Only works on DAGs (Directed Acyclic Graphs). If a cycle exists, no topological sort is possible.
    **限制：** 僅適用於有向無環圖（DAG）。若存在環，則無法進行拓撲排序。

### Union-Find (並查集 / DSU)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個不相交（無重疊）子集的元素集合。
*   **Intuition:** Determining if two people are in the same social network, or if adding a cable creates a loop in a network.
    **直覺：** 判斷兩個人是否在同一個社交網絡中，或者在網絡中增加一條電纜是否會形成迴路。
*   **Complexity:** Time $O(\alpha(N))$ (Inverse Ackermann function, nearly constant), Space $O(N)$.
    **複雜度：** 時間 $O(\alpha(N))$（反阿克曼函數，幾近常數），空間 $O(N)$。

### Dijkstra’s Algorithm (戴克斯特拉演算法)
*   **Definition:** Finds the shortest path from a source node to all other nodes in a graph with non-negative edge weights.
    **定義：** 在邊權重非負的圖中，尋找從源節點到所有其他節點的最短路徑。
*   **Intuition:** BFS with a Priority Queue instead of a standard Queue, prioritizing the "cheapest" path explored so far.
    **直覺：** 使用優先佇列（Priority Queue）代替標準佇列的 BFS，優先探索目前為止「代價最低」的路徑。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Dependency Resolution (Kahn's Algorithm)
### 模式一：依賴解析（Kahn 演算法）
*   **Scenario:** "Find the order to compile files," "Course Schedule," "Alien Dictionary."
    **場景：** 「找出編譯檔案的順序」、「課程表」、「外星字典」。
*   **Key Logic:** Track `in-degree` (number of incoming edges). Process nodes with `in-degree == 0`, then decrement neighbors.
    **關鍵邏輯：** 追蹤 `入度`（進入邊的數量）。處理 `入度 == 0` 的節點，然後遞減其鄰居的入度。

### Pattern 2: Dynamic Connectivity (Union-Find)
### 模式二：動態連通性（並查集）
*   **Scenario:** "Number of Provinces," "Graph Valid Tree," "Redundant Connection."
    **場景：** 「省份數量」、「圖是否為有效樹」、「冗餘連接」。
*   **Key Logic:** Initialize each node as its own parent. `Union` operations merge sets; `Find` checks if two nodes share the same ultimate root.
    **關鍵邏輯：** 初始化每個節點為其自身的父節點。`Union` 操作合併集合；`Find` 檢查兩個節點是否共享同一個最終根節點。

### Pattern 3: Shortest Path in Weighted Graph (Dijkstra)
### 模式三：加權圖最短路徑（Dijkstra）
*   **Scenario:** "Network Delay Time," "Cheapest Flights Within K Stops," "Path with Maximum Probability."
    **場景：** 「網路延遲時間」、「K 站內的最便宜航班」、「最大機率路徑」。
*   **Key Logic:** Use a Min-Heap `(current_dist, node)`. Relax edges: if `dist[u] + weight(u, v) < dist[v]`, update `dist[v]` and push to heap.
    **關鍵邏輯：** 使用最小堆積 `(current_dist, node)`。鬆弛邊：若 `dist[u] + weight(u, v) < dist[v]`，更新 `dist[v]` 並推入堆積。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule II (LeetCode 210)
### 問題：課程表 II

**Problem Statement:**
You are given a total of `numCourses` and a list of `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return the ordering of courses to finish all courses. If impossible, return an empty array.
**問題重述：**
給定課程總數 `numCourses` 和先修條件列表 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修課程 `a`，必須先修課程 `b`。請回傳修完所有課程的順序。若不可能，回傳空陣列。

#### 1. Approach: Brute Force (DFS without states)
#### 思路：暴力解（無狀態的 DFS）
*   Try to find a path for every node. Without memoization or state tracking (visiting/visited), this leads to TLE or infinite loops in cycles.
    嘗試為每個節點尋找路徑。若沒有記憶化或狀態追蹤（正在訪問/已訪問），這會導致超時（TLE）或在環中無限循環。

#### 2. Optimization: Kahn's Algorithm (BFS Based)
#### 優化：Kahn 演算法（基於 BFS）
*   This is the standard industry solution for dependency problems.
    這是處理依賴問題的業界標準解法。
*   **Step 1:** Build Adjacency List and calculate In-Degrees.
    **步驟一：** 建立鄰接表（Adjacency List）並計算入度（In-Degrees）。
*   **Step 2:** Push all nodes with `in-degree == 0` to a Queue.
    **步驟二：** 將所有 `入度 == 0` 的節點推入佇列。
*   **Step 3:** Process Queue. For each node, add to result, and decrement in-degree of neighbors. If neighbor becomes 0, push to Queue.
    **步驟三：** 處理佇列。對每個節點，加入結果集，並遞減鄰居的入度。若鄰居入度變為 0，推入佇列。
*   **Step 4:** If result length == numCourses, valid; otherwise, cycle detected.
    **步驟四：** 若結果長度 == numCourses，則有效；否則，表示檢測到環。

#### Python Solution (Reference)
#### Python 參考解

```python
from collections import deque, defaultdict
from typing import List

class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        # Build the graph and in-degree array
        # 建立圖形與入度陣列
        adj = defaultdict(list)
        in_degree = {i: 0 for i in range(numCourses)}
        
        for dest, src in prerequisites:
            adj[src].append(dest)
            in_degree[dest] += 1
            
        # Initialize the queue with courses that have no prerequisites
        # 將沒有先修條件的課程初始化入佇列
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        topo_order = []
        
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            
            # Visit neighbors
            # 訪問鄰居節點
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                # If in-degree becomes 0, all prerequisites are met
                # 若入度變為 0，表示所有先修條件已滿足
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check if we were able to schedule all courses (Cycle detection)
        # 檢查是否能夠安排所有課程（環檢測）
        if len(topo_order) == numCourses:
            return topo_order
        else:
            return [] # Cycle detected, impossible to finish / 檢測到環，無法完成

# Time Complexity: O(V + E) - Process each vertex and edge once.
# 時間複雜度：O(V + E) - 每個頂點與邊各處理一次。
# Space Complexity: O(V + E) - Adjacency list and in-degree array.
# 空間複雜度：O(V + E) - 鄰接表與入度陣列。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **DFS Cycle Detection** | **BFS (Kahn's) Cycle Detection** | DFS uses `visiting` vs `visited` states (recursion stack). BFS checks if `result_count < total_nodes`. <br> DFS 使用 `visiting` 與 `visited` 狀態（遞迴堆疊）。BFS 檢查 `result_count < total_nodes`。 |
| **Dijkstra** | **BFS** | BFS finds shortest path in **unweighted** graphs. Dijkstra is needed for **weighted** graphs. Using BFS on weighted graphs is a fatal error. <br> BFS 尋找**無權重**圖的最短路徑。**加權**圖需要 Dijkstra。在加權圖上使用 BFS 是致命錯誤。 |
| **Backtracking** | **DFS** | All Backtracking is DFS, but not all DFS is backtracking. Backtracking explicitly "undoes" a choice after exploring. <br> 所有回溯法都是 DFS，但並非所有 DFS 都是回溯。回溯法在探索後會明確地「撤銷」選擇。 |
| **O(V+E)** | **O(V*E)** | Adjacency List traversal is $O(V+E)$. Adjacency Matrix traversal is $O(V^2)$. Be careful with graph representation. <br> 鄰接表遍歷是 $O(V+E)$。鄰接矩陣遍歷是 $O(V^2)$。注意圖的表示法。 |

---

## 6. Interview Strategy (面試實戰建議)

1.  **Clarify Graph Type First:**
    **首先釐清圖的類型：**
    *   "Is the graph directed or undirected?" (Affects cycle detection logic).
        「圖是有向還是無向？」（影響環檢測邏輯）。
    *   "Are there weights? Can weights be negative?" (Decides BFS vs Dijkstra vs Bellman-Ford).
        「有權重嗎？權重可以是負的嗎？」（決定使用 BFS、Dijkstra 還是 Bellman-Ford）。

2.  **Narrate the "Why":**
    **敘述「為什麼」：**
    *   *Bad:* "I will use Union-Find."
        *壞：*「我會用並查集。」
    *   *Good:* "Since we are dealing with dynamic connectivity and need to detect cycles in an undirected graph efficiently, Union-Find is optimal here due to its near-constant time complexity."
        *好：*「由於我們處理的是動態連通性問題，且需要在無向圖中高效檢測環，並查集因其幾近常數的時間複雜度，是這裡的最佳選擇。」

3.  **Code Structure for Senior Roles:**
    **資深角色的程式碼結構：**
    *   Separate the graph construction from the core logic.
        將圖的建構與核心邏輯分開。
    *   If using Union-Find, write a helper class or clear helper functions (`find`, `union`). Don't inline everything messily.
        若使用並查集，撰寫輔助類別或清晰的輔助函式（`find`, `union`）。不要雜亂地將所有程式碼寫在一起。

---

## 7. Practice Problems (練習題)

### Easy/Mid: Number of Provinces (LeetCode 547)
*   **Prompt:** Given an $n \times n$ matrix `isConnected`, find the total number of connected components.
    **題目：** 給定 $n \times n$ 矩陣 `isConnected`，找出連通分量的總數。
*   **Hint:** Classic Union-Find. Initialize count = n, decrement count on every successful `union`.
    **提示：** 經典並查集。初始化 count = n，每次成功 `union` 時將 count 減一。

### Mid: Network Delay Time (LeetCode 743)
*   **Prompt:** Given a network of nodes with travel times (weights), find the time it takes for a signal to reach all nodes from node K.
    **題目：** 給定具有傳輸時間（權重）的節點網絡，找出訊號從節點 K 傳達到所有節點所需的時間。
*   **Hint:** Dijkstra’s Algorithm. Return the maximum value in the distance array. If any node is unreachable, return -1.
    **提示：** Dijkstra 演算法。回傳距離陣列中的最大值。若有任何節點無法到達，回傳 -1。

### Hard: Alien Dictionary (LeetCode 269)
*   **Prompt:** Given a list of words sorted lexicographically by an alien language, derive the order of characters in that language.
    **題目：** 給定一份按外星語言字典序排列的單字列表，推導出該語言中字元的順序。
*   **Hint:** Build graph by comparing adjacent words to find the first differing character ($u \to v$). Then apply Topological Sort. Handle edge cases (prefix issues like "abc" before "ab").
    **提示：** 透過比較相鄰單字找出第一個不同的字元來建圖（$u \to v$）。接著應用拓撲排序。處理邊界情況（如前綴問題："abc" 排在 "ab" 之前）。

---

## 8. Quick Checklists (快速檢核表)

### Complexity Check (複雜度確認)
- [ ] **BFS/DFS/Topo Sort:** $O(V + E)$? (Using Adjacency List)
- [ ] **Dijkstra:** $O(E \log V)$? (Using Min-Heap)
- [ ] **Union-Find:** $O(N \cdot \alpha(N))$? (Using Path Compression + Rank)

### Bug Prevention (防錯機制)
- [ ] **Directed vs Undirected:** Did I add edges both ways for undirected graphs?
    **有向與無向：** 對於無向圖，我是否雙向都添加了邊？
- [ ] **Zero-Index vs One-Index:** Are nodes 0 to N-1 or 1 to N?
    **0-索引與 1-索引：** 節點是 0 到 N-1 還是 1 到 N？
- [ ] **Disconnected Graph:** Did I handle cases where the graph is not fully connected? (Loop through all nodes to start traversal).
    **非連通圖：** 我是否處理了圖未完全連通的情況？（循環遍歷所有節點以開始遍歷）。
- [ ] **Infinite Loop:** Did I use a `visited` set?
    **無限循環：** 我是否使用了 `visited` 集合？

---

## 9. Memory Anchors (記憶錨點)

*   **Topological Sort = "Getting Dressed"**
    **拓撲排序 = 「穿衣服」**
    *   You must put on socks (dependency) before shoes. You can't put on shoes then socks (Cycle error).
    *   必須先穿襪子（依賴）才能穿鞋子。不能先穿鞋子再穿襪子（環錯誤）。

*   **Union-Find = "Corporate Mergers"**
    **並查集 = 「企業併購」**
    *   Company A acquires B. Everyone in B now reports to A's CEO (Root). Path compression is like memorizing who the big boss is so you don't ask middle management every time.
    *   A 公司收購 B。B 的所有人現在都向 A 的 CEO（根節點）匯報。路徑壓縮就像是記住了大老闆是誰，這樣就不必每次都問中層管理人員。

*   **Dijkstra = "Water Spreading with Friction"**
    **Dijkstra = 「帶摩擦力的水流擴散」**
    *   Water flows from the source. It reaches closer (lower weight) areas first. The priority queue manages which "wavefront" advances next based on least resistance.
    *   水從源頭流出。它會先到達較近（低權重）的區域。優先佇列根據最小阻力管理下一個推進的「波前」。