Here is the comprehensive guide on **Advanced Graphs**, tailored for a Senior Software Engineer, following your specified structure and bilingual format.

---

# Advanced Graphs for Senior Engineers
# 資深工程師進階圖論指南

## 1. Learning Objectives (學習目標)

1.  **Master Advanced Traversal States:** Move beyond simple "visited" sets to handling nodes visited with different states (e.g., cost, remaining moves).
    掌握進階遍歷狀態：超越簡單的「已訪問」集合，學會處理帶有不同狀態（如成本、剩餘步數）的節點訪問。
2.  **Internalize Union-Find (Disjoint Set):** Implement and apply Union-Find for dynamic connectivity and cycle detection efficiently.
    內化並查集（Union-Find）：高效實作並應用並查集來解決動態連通性與環檢測問題。
3.  **Optimize Shortest Path Algorithms:** Understand when to apply Dijkstra vs. Bellman-Ford, and how to adapt them for constrained paths.
    優化最短路徑演算法：理解何時使用 Dijkstra 與 Bellman-Ford，以及如何調整它們以適應受限路徑。
4.  **Topological Sorting Proficiency:** Solve dependency resolution problems using both Kahn’s Algorithm (BFS) and DFS.
    熟練拓撲排序：使用 Kahn 演算法（BFS）和 DFS 解決依賴解析問題。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)
Graphs model relationships between objects.
圖論模擬物件之間的關係。
For senior roles, the challenge lies not in the definition, but in modeling abstract problems (like currency exchange or state transitions) as graphs.
對於資深職位而言，挑戰不在於定義，而在於將抽象問題（如貨幣兌換或狀態轉換）建模為圖。

### Representations (表示法)
1.  **Adjacency List (鄰接表):** `Map<Node, List<Edge>>`. Best for sparse graphs. Space: $O(V + E)$.
    鄰接表：`Map<Node, List<Edge>>`。最適合稀疏圖。空間複雜度：$O(V + E)$。
2.  **Adjacency Matrix (鄰接矩陣):** `int[][]`. Best for dense graphs or when edge lookup needs $O(1)$. Space: $O(V^2)$.
    鄰接矩陣：`int[][]`。最適合稠密圖或需要 $O(1)$ 查找邊的場景。空間複雜度：$O(V^2)$。

### Complexity (複雜度)
*   **DFS/BFS:** Time $O(V + E)$, Space $O(V)$.
    DFS/BFS：時間 $O(V + E)$，空間 $O(V)$。
*   **Dijkstra:** Time $O(E \log V)$ (with Binary Heap).
    Dijkstra：時間 $O(E \log V)$（使用二元堆積）。
*   **Union-Find:** Time $\approx O(1)$ (amortized $\alpha(N)$).
    並查集：時間 $\approx O(1)$（攤銷後 $\alpha(N)$）。

### When to Use / Not Use (適用與不適用場景)
*   **Use BFS** for shortest path in unweighted graphs.
    在無權圖中尋找最短路徑時使用 BFS。
*   **Use Dijkstra** for shortest path in weighted, non-negative graphs.
    在加權非負圖中尋找最短路徑時使用 Dijkstra。
*   **Do NOT use DFS** for shortest path (unless searching for *any* path or exhaustive search).
    不要使用 DFS 尋找最短路徑（除非是尋找「任意」路徑或窮舉搜索）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Topological Sort (拓撲排序)
Used for scheduling tasks or resolving dependencies (e.g., build systems).
用於任務排程或解析依賴關係（例如建置系統）。
*   **Key:** Indegree array + Queue (Kahn's Algo).
    **關鍵：** 入度陣列 + 佇列（Kahn 演算法）。

### B. Union-Find / Disjoint Set (並查集)
Used for connecting components dynamically, checking if two nodes are in the same group, or detecting cycles in undirected graphs.
用於動態連接組件、檢查兩個節點是否在同一組，或檢測無向圖中的環。
*   **Key:** `find()` with path compression, `union()` with rank/size.
    **關鍵：** 帶路徑壓縮的 `find()`，帶秩/大小優化的 `union()`。

### C. Dijkstra with State (帶狀態的 Dijkstra)
Standard Dijkstra finds the shortest path to a node.
標準 Dijkstra 尋找到達節點的最短路徑。
Advanced problems require finding the shortest path to a `(node, state)` tuple (e.g., node `u` with `k` fuel remaining).
進階問題需要尋找到達 `(node, state)` 元組的最短路徑（例如：剩餘 `k` 燃料到達節點 `u`）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Cheapest Flights Within K Stops (K 站中轉內的最便宜航班)
*LeetCode 787 (Medium/Hard)*

#### Problem Statement (問題重述)
There are `n` cities connected by some number of flights. You are given an array `flights` where `flights[i] = [from, to, price]`.
有 `n` 個城市通過若干航班相連。給定陣列 `flights`，其中 `flights[i] = [from, to, price]`。

You are also given three integers `src`, `dst`, and `k`, return the **cheapest price** from `src` to `dst` with at most `k` stops. If there is no such route, return -1.
同時給定三個整數 `src`、`dst` 和 `k`，返回從 `src` 到 `dst` 最多經過 `k` 次中轉的**最便宜價格**。如果不存在這樣的路線，則返回 -1。

#### Thought Process (思路)

1.  **Brute Force (DFS):**
    Traverse all paths from `src` to `dst`. Prune if depth > `k`. Calculate min cost.
    遍歷從 `src` 到 `dst` 的所有路徑。如果深度 > `k` 則剪枝。計算最小成本。
    *Drawback:* Exponential time complexity $O(V^k)$ in worst case.
    *缺點：* 最壞情況下是指數級時間複雜度 $O(V^k)$。

2.  **Optimization (Dijkstra):**
    Standard Dijkstra greedily picks the cheapest node. However, the cheapest path might have too many stops.
    標準 Dijkstra 貪婪地選擇最便宜的節點。然而，最便宜的路徑可能有太多的中轉站。
    We need to track `stops` as part of our state.
    我們需要將 `stops`（中轉次數）作為狀態的一部分來追蹤。

3.  **Best Solution (Modified Dijkstra):**
    Priority Queue stores `[cost, current_node, stops_remaining]`.
    優先佇列存儲 `[cost, current_node, stops_remaining]`。
    Crucial optimization: Only push to PQ if we find a cheaper price for the *same or fewer* stops. actually, simpler logic: track `minCost` array for each node.
    關鍵優化：只有當我們以「相同或更少」的中轉次數找到更便宜的價格時，才推入 PQ。實際上，更簡單的邏輯是：追蹤每個節點的 `minCost` 陣列。
    *Correction:* Standard Dijkstra `dist[node]` is not enough. We need `dist[node]` to track stops, or simply allow re-visiting nodes if the number of stops is fewer than before.
    *修正：* 標準 Dijkstra 的 `dist[node]` 是不夠的。我們需要 `dist[node]` 來追蹤中轉次數，或者簡單地允許在「中轉次數比之前少」的情況下重新訪問節點。

#### Java Solution (Java 參考解)

```java
import java.util.*;

class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        // Build Adjacency List: Map<From, List<int[]{To, Price}>>
        // 建立鄰接表：Map<出發點, List<int[]{目的地, 價格}>>
        Map<Integer, List<int[]>> graph = new HashMap<>();
        for (int[] f : flights) {
            graph.computeIfAbsent(f[0], x -> new ArrayList<>()).add(new int[]{f[1], f[2]});
        }

        // Priority Queue: {cost, currentNode, stopsTaken}
        // Ordered by cost (Min-Heap)
        // 優先佇列：{成本, 當前節點, 已用中轉數}，按成本排序（最小堆積）
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, src, 0});

        // Array to track minimum stops to reach a node with current cost
        // Ideally, we want to track min cost for each number of stops, 
        // but here we can just track min stops for a visited node to prune.
        // 陣列用於追蹤到達某節點的最小中轉數。
        // 理想情況下，我們想追蹤每個中轉數的最小成本，但這裡我們可以僅追蹤已訪問節點的最小中轉數來進行剪枝。
        int[] minStops = new int[n];
        Arrays.fill(minStops, Integer.MAX_VALUE);

        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int cost = current[0];
            int node = current[1];
            int stops = current[2];

            // If destination reached, return cost immediately (Dijkstra guarantees optimality)
            // 如果到達目的地，立即返回成本（Dijkstra 保證最優性）
            if (node == dst) {
                return cost;
            }

            // Pruning: If we have visited this node with fewer or equal stops before, 
            // the current path is suboptimal because it costs more (since it came out of PQ later).
            // 剪枝：如果我們之前以更少或相等的中轉次數訪問過此節點，
            // 則當前路徑次優，因為它的成本更高（因為它是後來才從 PQ 出來的）。
            if (stops >= minStops[node] || stops > k + 1) {
                continue;
            }
            
            // Update the minimum stops seen for this node
            // 更新此節點所見過的最小中轉數
            minStops[node] = stops;

            if (graph.containsKey(node)) {
                for (int[] neighbor : graph.get(node)) {
                    int nextNode = neighbor[0];
                    int price = neighbor[1];
                    
                    // Add to PQ only if within stop limits
                    // 僅在中轉限制內時加入 PQ
                    pq.offer(new int[]{cost + price, nextNode, stops + 1});
                }
            }
        }

        return -1;
    }
}
```

#### Complexity (複雜度)
*   **Time:** $O(E \cdot K \log (E \cdot K))$ or roughly $O(E \log V)$ depending on implementation nuances. Since we might revisit nodes, it's strictly bounded by the number of edges times allowed stops.
    **時間：** $O(E \cdot K \log (E \cdot K))$ 或大約 $O(E \log V)$，取決於實作細節。由於我們可能會重新訪問節點，嚴格來說受限於邊數乘以允許的中轉次數。
*   **Space:** $O(V + E + K)$.
    **空間：** $O(V + E + K)$。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Visited Set (Global)** | **Recursion Stack (Path)** | In DFS cycle detection (directed), use a recursion stack (visiting), not just a global visited set. <br> 在有向圖 DFS 環檢測中，使用遞迴堆疊（正在訪問），而不僅僅是全域已訪問集合。 |
| **Dijkstra** | **Bellman-Ford** | Dijkstra fails with negative edge weights. Bellman-Ford handles them (and detects negative cycles) but is slower ($O(VE)$). <br> Dijkstra 在負權邊時會失效。Bellman-Ford 可以處理（並檢測負環），但較慢（$O(VE)$）。 |
| **Prim's Algo** | **Kruskal's Algo** | Both find MST. Prim's grows from a node (good for dense). Kruskal's merges edges (good for sparse, uses Union-Find). <br> 兩者都找最小生成樹。Prim 從節點擴展（適合稠密圖）。Kruskal 合併邊（適合稀疏圖，使用並查集）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Model the Problem:** "This looks like a graph problem where cities are nodes and flights are directed weighted edges."
    **問題建模：**「這看起來像是一個圖論問題，城市是節點，航班是有向加權邊。」
2.  **Select Algorithm:** "Since we need the shortest path with positive weights, Dijkstra is a candidate. However, due to the 'K stops' constraint, we need to modify the state."
    **選擇演算法：**「由於我們需要正權重的最短路徑，Dijkstra 是一個候選。然而，由於『K 次中轉』的限制，我們需要修改狀態。」
3.  **Discuss Trade-offs:** "Standard BFS ignores weights. DFS might TLE. Modified Dijkstra balances cost and depth."
    **討論權衡：**「標準 BFS 忽略權重。DFS 可能會超時。修改後的 Dijkstra 平衡了成本與深度。」

### Whiteboard Strategy (白板策略)
*   **Draw the Graph:** Visualizing directed vs. undirected edges prevents logic errors.
    **畫出圖形：** 視覺化有向與無向邊可以防止邏輯錯誤。
*   **Define State:** Explicitly write `State = {u, cost, k}` before coding.
    **定義狀態：** 在寫程式碼前明確寫下 `State = {u, cost, k}`。

### Common Follow-ups (常見追問)
*   *What if edges can be negative?* -> Switch to Bellman-Ford or SPFA.
    *如果邊可以是負的怎麼辦？* -> 轉用 Bellman-Ford 或 SPFA。
*   *What if the graph is dynamic (edges added continuously)?* -> Discuss Union-Find or dynamic graph algorithms.
    *如果圖是動態的（持續增加邊）怎麼辦？* -> 討論並查集或動態圖演算法。

---

## 7. Practice Problems (練習題)

### Easy: Find the Town Judge (尋找小鎮法官)
*   **Hint:** Directed graph indegree/outdegree calculation.
    **提示：** 有向圖的入度/出度計算。
*   **Core:** Judge has indegree $N-1$ and outdegree $0$.
    **核心：** 法官的入度為 $N-1$，出度為 $0$。

### Medium: Course Schedule II (課程表 II)
*   **Hint:** Topological Sort.
    **提示：** 拓撲排序。
*   **Core:** Detect cycle. If cycle exists, return empty. Else return order. Use `indegree` array and a Queue.
    **核心：** 檢測環。若存在環，返回空。否則返回順序。使用 `indegree` 陣列和佇列。

### Hard: Word Ladder II (單詞接龍 II)
*   **Hint:** BFS for shortest distance + DFS for path reconstruction (or BFS storing paths).
    **提示：** BFS 用於最短距離 + DFS 用於路徑重建（或 BFS 存儲路徑）。
*   **Core:** Standard BFS finds length. To output *all* shortest paths, you need to build a DAG of predecessors during BFS, then backtrack.
    **核心：** 標準 BFS 找到長度。要輸出「所有」最短路徑，需在 BFS 期間建立前驅節點的 DAG，然後回溯。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Connectivity:** Did I handle the case where the graph is not fully connected? (Loop through all nodes if necessary).
    **連通性：** 我是否處理了圖未完全連通的情況？（必要時迴圈遍歷所有節點）。
*   [ ] **Cycles:** Will my code loop infinitely if there is a cycle? (Visited set / Distance array).
    **環：** 如果有環，我的程式碼會無限迴圈嗎？（已訪問集合 / 距離陣列）。
*   [ ] **Direction:** Is the graph directed or undirected? (Did I add edges both ways for undirected?).
    **方向：** 圖是有向還是無向的？（無向圖是否雙向添加了邊？）。
*   [ ] **Self-loops:** Can a node connect to itself?
    **自環：** 節點可以連接到自己嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **BFS is like a ripple in a pond:** It expands uniformly layer by layer. Good for "closest" in unweighted graphs.
    **BFS 就像池塘裡的漣漪：** 它一層一層均勻地擴散。適合無權圖中的「最近」問題。
*   **DFS is like a maze runner:** It goes as deep as possible, hits a dead end, and backtracks. Good for "does a path exist" or puzzles.
    **DFS 就像走迷宮的人：** 它走得越深越好，撞到死胡同後回溯。適合「路徑是否存在」或解謎。
*   **Dijkstra is like water flowing in pipes of different widths:** It fills the easiest (lowest cost) pipes first.
    **Dijkstra 就像水流過不同寬度的管子：** 它首先填滿最容易（成本最低）的管子。
*   **Union-Find is like corporate mergers:** Companies (sets) merge, and everyone reports to one CEO (root parent).
    **並查集就像企業合併：** 公司（集合）合併，每個人都向一位 CEO（根父節點）匯報。