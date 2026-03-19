Here is the comprehensive guide on **Graphs (Intermediate)**, tailored for a Senior Software Engineer, following your specific constraints.

***

# Graph Algorithms: Intermediate Mastery
# 圖演算法：中階精通指南

## 1. Learning Objectives (學習目標)

1.  **Model Real-World Problems as Graphs:**
    Ability to instantly recognize when a problem (dependencies, network connectivity, state changes) can be modeled as a graph.
    能夠立即辨識何時將問題（依賴關係、網絡連通性、狀態變更）建模為圖。

2.  **Master Traversal & Topology:**
    Go beyond basic BFS/DFS to understand Topological Sort and Cycle Detection in both directed and undirected contexts.
    超越基礎的 BFS/DFS，深入理解有向與無向情境下的拓撲排序與環檢測。

3.  **Optimize for Connectivity:**
    Learn when to use Union-Find (Disjoint Set) over DFS/BFS for dynamic connectivity problems.
    學習在動態連通性問題中，何時該使用並查集（Union-Find）來取代 DFS/BFS。

4.  **Proficiency in C++ STL for Graphs:**
    Utilize `std::vector`, `std::queue`, and `std::unordered_map` efficiently to implement graph structures.
    高效利用 C++ STL 中的向量、隊列與雜湊表來實作圖結構。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition & Intuition (定義與直覺)

A Graph is a collection of nodes (vertices) and edges connecting them.
圖是節點（頂點）與連接它們的邊的集合。

For Senior Engineers, think of graphs not just as data structures, but as **relationships between states**.
對於資深工程師而言，不要只將圖視為資料結構，而應視為**狀態之間的關係**。

### Representation (表示法)

1.  **Adjacency List (鄰接表):**
    *   `vector<vector<int>> adj;`
    *   **Pros:** Space efficient $O(V+E)$, fast iteration over neighbors.
    *   **優點：** 空間效率高 $O(V+E)$，遍歷鄰居速度快。
    *   **Use Case:** Most interview problems (sparse graphs).
    *   **適用場景：** 大多數面試題（稀疏圖）。

2.  **Adjacency Matrix (鄰接矩陣):**
    *   `vector<vector<int>> matrix;`
    *   **Pros:** $O(1)$ edge lookup. **Cons:** $O(V^2)$ space.
    *   **優點：** $O(1)$ 查詢邊。 **缺點：** $O(V^2)$ 空間。
    *   **Use Case:** Dense graphs or when $V$ is small (< 1000).
    *   **適用場景：** 稠密圖或 $V$ 很小（< 1000）時。

### Complexity (複雜度)

*   **Time:** $O(V + E)$ for standard traversals (BFS/DFS).
    **時間：** 標準遍歷（BFS/DFS）為 $O(V + E)$。
*   **Space:** $O(V)$ for recursion stack or queue + visited array.
    **空間：** 遞迴堆疊或隊列 + 訪問陣列為 $O(V)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Topological Sort (拓撲排序)
*   **Scenario:** Task scheduling, dependency resolution, build systems.
    **場景：** 任務排程、依賴解析、建置系統。
*   **Method:** Kahn’s Algorithm (Indegree + BFS) or DFS Post-order.
    **方法：** Kahn 演算法（入度 + BFS）或 DFS 後序遍歷。

### B. Connected Components (連通分量)
*   **Scenario:** Counting islands, social network circles, malware spread.
    **場景：** 計算島嶼數量、社交圈、惡意軟體傳播。
*   **Method:** Union-Find (Disjoint Set) or Multi-source BFS/DFS.
    **方法：** 並查集（Union-Find）或多源 BFS/DFS。

### C. Shortest Path in Unweighted Graph (無權圖最短路徑)
*   **Scenario:** Word Ladder, minimum steps to reach a target state.
    **場景：** 單字接龍、到達目標狀態的最小步數。
*   **Method:** BFS (Level-order traversal guarantees shortest path).
    **方法：** BFS（層序遍歷保證最短路徑）。

### D. Bipartite Check (二分圖檢測)
*   **Scenario:** Splitting a group into two sets with no internal conflicts.
    **場景：** 將群體分成兩組且組內無衝突。
*   **Method:** Graph Coloring (0/1 coloring) via BFS/DFS.
    **方法：** 透過 BFS/DFS 進行圖著色（0/1 著色）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule II (LeetCode 210)
**Context:** Directed Graph, Cycle Detection, Topological Sort.
**情境：** 有向圖、環檢測、拓撲排序。

### Problem Statement (問題重述)
You are given a total of `numCourses` courses labeled from `0` to `numCourses - 1`.
給定總共 `numCourses` 門課程，編號從 `0` 到 `numCourses - 1`。

You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`.
給定一個陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修習課程 `a`，必須先修習課程 `b`。

Return the ordering of courses you should take to finish all courses. If there are multiple valid answers, return any of them. If it is impossible, return an empty array.
回傳修完所有課程的順序。若有多種有效答案，回傳任一種。若不可能完成，回傳空陣列。

### Thought Process (思路)

#### 1. Naive / Brute Force (暴力法)
Try to generate all permutations of courses and check if they satisfy constraints.
嘗試生成所有課程的排列組合，並檢查是否滿足限制。
*   **Complexity:** $O(V! \cdot E)$. Extremely inefficient.
*   **複雜度：** $O(V! \cdot E)$。極度低效。

#### 2. Optimization: Modeling as a Graph (優化：建模為圖)
Treat courses as nodes and prerequisites as directed edges ($b \to a$).
將課程視為節點，先修要求視為有向邊 ($b \to a$)。
The problem asks for a linear ordering of vertices such that for every edge $u \to v$, $u$ comes before $v$. This is the definition of **Topological Sort**.
問題要求頂點的線性排序，使得對於每條邊 $u \to v$，$u$ 都在 $v$ 之前。這正是**拓撲排序**的定義。

#### 3. Best Solution: Kahn's Algorithm (BFS) (最佳解：Kahn 演算法)
*   Calculate **indegree** (number of incoming edges) for all nodes.
    計算所有節點的**入度**（進入該節點的邊數）。
*   Nodes with `indegree == 0` have no prerequisites; add them to a Queue.
    `indegree == 0` 的節點沒有先修課；將它們加入 Queue。
*   Process Queue: Add node to result, then decrement the indegree of its neighbors.
    處理 Queue：將節點加入結果，並將其鄰居的入度減一。
*   If a neighbor's indegree becomes 0, add it to the Queue.
    若鄰居的入度變為 0，將其加入 Queue。
*   **Cycle Detection:** If the result size < total courses, a cycle exists (impossible).
    **環檢測：** 若結果的大小 < 總課程數，表示存在環（不可能完成）。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <queue>
#include <iostream>

using namespace std;

class Solution {
public:
    vector<int> findOrder(int numCourses, vector<vector<int>>& prerequisites) {
        // 1. Build Adjacency List and Indegree Array
        // 1. 建立鄰接表與入度陣列
        vector<vector<int>> adj(numCourses);
        vector<int> indegree(numCourses, 0);

        for (const auto& edge : prerequisites) {
            int course = edge[0];
            int prereq = edge[1];
            // Edge direction: prereq -> course
            // 邊的方向：先修課 -> 課程
            adj[prereq].push_back(course);
            indegree[course]++;
        }

        // 2. Initialize Queue with nodes having 0 indegree
        // 2. 初始化隊列，加入入度為 0 的節點
        queue<int> q;
        for (int i = 0; i < numCourses; ++i) {
            if (indegree[i] == 0) {
                q.push(i);
            }
        }

        vector<int> result;
        
        // 3. Process the graph (BFS)
        // 3. 處理圖（BFS）
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            result.push_back(current);

            // Visit neighbors
            // 訪問鄰居
            for (int neighbor : adj[current]) {
                indegree[neighbor]--;
                // If dependencies are met, add to queue
                // 若依賴已滿足，加入隊列
                if (indegree[neighbor] == 0) {
                    q.push(neighbor);
                }
            }
        }

        // 4. Check for cycles
        // 4. 檢查是否存在環
        if (result.size() != numCourses) {
            return {}; // Cycle detected, impossible to finish
                       // 檢測到環，無法完成
        }

        return result;
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(V + E)$. We process each node and each edge exactly once.
    **時間：** $O(V + E)$。我們處理每個節點與每條邊恰好一次。
*   **Space:** $O(V + E)$. Adjacency list stores edges, indegree array stores nodes.
    **空間：** $O(V + E)$。鄰接表儲存邊，入度陣列儲存節點。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Confusion (錯誤/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Visited Array** | Forgetting to reset `visited` in DFS backtracking (for path finding). <br> 在 DFS 回溯尋找路徑時忘記重置 `visited`。 | Only reset `visited` if you need to find *all* paths. For simple reachability or topo sort, do not reset. <br> 只有在尋找*所有*路徑時才需重置。對於單純的可達性或拓撲排序，不需要重置。 |
| **Cycle Detection** | Using a simple `visited` set for Directed Graphs. <br> 在有向圖中使用單純的 `visited` 集合。 | Directed graphs need 3 states: `0` (unvisited), `1` (visiting/current path), `2` (visited). A cycle is finding a node in state `1`. <br> 有向圖需要 3 種狀態：`0`（未訪問）、`1`（訪問中/當前路徑）、`2`（已訪問）。遇到狀態 `1` 的節點即為環。 |
| **Graph Building** | Assuming node IDs are always `0` to `N-1`. <br> 假設節點 ID 總是 `0` 到 `N-1`。 | Sometimes inputs are strings or non-contiguous integers. Use `unordered_map` to map them to `0..N-1` or use the map as the graph directly. <br> 有時輸入是字串或不連續整數。使用 `unordered_map` 映射至 `0..N-1` 或直接用 map 作為圖。 |
| **Union-Find** | Forgetting Path Compression or Union by Rank. <br> 忘記路徑壓縮或按秩合併。 | Without these optimizations, Union-Find degrades to $O(N)$ instead of nearly $O(1)$ ($\alpha(N)$). <br> 若無這些優化，並查集會退化成 $O(N)$ 而非接近 $O(1)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Map to Graph:** "This problem can be modeled as a graph where [Entity] are nodes and [Relationship] are edges."
    **映射至圖：** 「這個問題可以建模為一個圖，其中 [實體] 是節點，[關係] 是邊。」
2.  **Choose Traversal:** "Since we need the shortest path/dependency order, I will use BFS/Topological Sort."
    **選擇遍歷：** 「由於我們需要最短路徑/依賴順序，我將使用 BFS/拓撲排序。」
3.  **Define State:** "I'll use a `visited` array to prevent cycles and redundant processing."
    **定義狀態：** 「我會使用 `visited` 陣列來防止環與重複處理。」

### Whiteboard Strategy (白板策略)
*   **Draw it:** Always draw a small graph (3-4 nodes) to visualize the example.
    **畫出來：** 永遠畫一個小圖（3-4 個節點）來視覺化範例。
*   **Corner Cases:** Immediately ask: "Can the graph be disconnected?" "Are there self-loops?"
    **邊界情況：** 立即詢問：「圖是否可能不連通？」「是否有自環？」

### Common Follow-ups (常見追問)
*   "What if the graph is huge and cannot fit in memory?" (Distributed BFS / External storage).
    「如果圖非常大，記憶體放不下怎麼辦？」（分散式 BFS / 外部儲存）。
*   "How to handle dynamic edge additions?" (Union-Find is better than DFS/BFS for connectivity).
    「如何處理動態新增邊的情況？」（處理連通性時，Union-Find 優於 DFS/BFS）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Number of Islands (LeetCode 200)
*   **Concept:** Connected Components (Grid Graph).
    **觀念：** 連通分量（網格圖）。
*   **Hint:** Iterate through the grid. When you see '1', increment count and trigger BFS/DFS to sink the island (mark as '0').
    **提示：** 遍歷網格。看到 '1' 時，計數加一並觸發 BFS/DFS 將島嶼沉沒（標記為 '0'）。

### 2. Intermediate: Number of Provinces (LeetCode 547)
*   **Concept:** Connectivity (Union-Find vs DFS).
    **觀念：** 連通性（並查集 vs DFS）。
*   **Hint:** The input is an adjacency matrix. Use Union-Find to merge nodes. The answer is the number of disjoint sets remaining.
    **提示：** 輸入是鄰接矩陣。使用並查集來合併節點。答案是剩餘的不相交集合數量。

### 3. Advanced (Intermediate+): Network Delay Time (LeetCode 743)
*   **Concept:** Shortest Path in Weighted Graph (Dijkstra).
    **觀念：** 加權圖最短路徑（Dijkstra）。
*   **Hint:** Use `priority_queue` (min-heap). Store `{accumulated_dist, node}`. Standard BFS assumes weight=1, Dijkstra handles weight > 0.
    **提示：** 使用 `priority_queue`（最小堆積）。儲存 `{累積距離, 節點}`。標準 BFS 假設權重=1，Dijkstra 處理權重 > 0。

---

## 8. Quick Checklists (快速檢核表)

### Debugging / Self-Review (除錯 / 自我審查)
- [ ] **Directed vs Undirected:** Did I handle edge direction correctly? (e.g., `adj[u].push(v)` vs `adj[u].push(v); adj[v].push(u)`).
    **有向 vs 無向：** 邊的方向處理正確嗎？
- [ ] **Connectivity:** Did I assume the graph is fully connected? (Loop through all nodes `0..N-1` to start traversal if disconnected).
    **連通性：** 我是否假設圖是完全連通的？（若不連通，需迴圈遍歷所有節點 `0..N-1` 來啟動遍歷）。
- [ ] **Infinite Loops:** Do I check `visited` *before* pushing to queue/stack or *after* popping? (Usually check before pushing or immediately after popping).
    **無窮迴圈：** 我是在推入隊列/堆疊*前*檢查 `visited`，還是取出*後*？（通常在推入前或取出後立即檢查）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **BFS is like Ripples:**
    Dropping a stone in a pond. The waves expand layer by layer. Good for "closest" things.
    **BFS 像漣漪：** 投石入池，波紋一層層擴散。適合找「最近」的事物。

*   **DFS is like a Maze Runner:**
    Keep going down one path until you hit a wall, then backtrack. Good for "existence" (is there a path?).
    **DFS 像迷宮跑者：** 沿著一條路一直走直到撞牆，然後回頭。適合找「存在性」（是否有路？）。

*   **Topological Sort is like Getting Dressed:**
    Socks before shoes. Underwear before pants. You cannot put on shoes if socks aren't "visited" (processed).
    **拓撲排序像穿衣服：** 先穿襪子再穿鞋，先穿內褲再穿褲子。如果襪子還沒「訪問」（處理），就不能穿鞋。