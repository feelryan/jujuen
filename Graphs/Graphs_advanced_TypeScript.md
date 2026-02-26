# Advanced Graphs Interview Guide (進階圖論面試指南)

## 1. Learning Objectives (學習目標)

*   **Master Shortest Path Algorithms beyond BFS:** Understand when and how to implement **Dijkstra’s Algorithm** (weighted graphs) and **Bellman-Ford** (negative weights).
    **掌握 BFS 以外的最短路徑演算法：** 理解何時以及如何實作 **Dijkstra 演算法**（加權圖）與 **Bellman-Ford**（負權重）。
*   **Advanced Connectivity & Union-Find:** Implement Disjoint Set Union (DSU) with path compression and rank optimization for dynamic connectivity problems.
    **進階連通性與並查集：** 實作具備路徑壓縮與按秩合併優化的並查集（DSU），以解決動態連通性問題。
*   **Topological Sorting & Cycle Detection:** Distinguish between Kahn’s Algorithm (BFS-based) and DFS-based approaches for dependency resolution.
    **拓撲排序與環檢測：** 區分 Kahn 演算法（基於 BFS）與基於 DFS 的方法來解決依賴解析問題。
*   **Graph Modeling:** Ability to transform non-obvious problems (e.g., currency exchange, word ladders) into graph models.
    **圖模型建構：** 具備將非直觀問題（如貨幣兌換、單字接龍）轉化為圖模型的能力。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
At a senior level, a graph is not just nodes and edges; it is a model for **relationships** and **states**.
在資深層級，圖不僅僅是節點與邊；它是**關係**與**狀態**的模型。

*   **Directed vs. Undirected (有向 vs. 無向):** Does the relationship go one way (Twitter follow) or both ways (Facebook friend)?
    關係是單向的（Twitter 追蹤）還是雙向的（Facebook 好友）？
*   **Weighted vs. Unweighted (加權 vs. 無權):** Is there a cost/distance associated with the edge?
    邊是否關聯了成本或距離？
*   **Cyclic vs. Acyclic (有環 vs. 無環):** Can you return to the start? (Crucial for deadlocks/dependencies).
    你能否回到起點？（這對死鎖/依賴關係至關重要）。

### Complexity (複雜度)
*   **Time:** Generally $O(V + E)$ for traversal. Dijkstra is $O(E \log V)$ or $O(E + V \log V)$ with Fibonacci heap.
    **時間：** 遍歷通常為 $O(V + E)$。Dijkstra 為 $O(E \log V)$，若使用費氏堆積則為 $O(E + V \log V)$。
*   **Space:** $O(V + E)$ for Adjacency List; $O(V^2)$ for Adjacency Matrix.
    **空間：** 鄰接表為 $O(V + E)$；鄰接矩陣為 $O(V^2)$。

### When to Use (適用場景)
*   **Network Routing / Maps:** Shortest path with costs (Dijkstra).
    **網路路由 / 地圖：** 帶成本的最短路徑（Dijkstra）。
*   **Dependency Resolution:** Build systems, package managers (Topological Sort).
    **依賴解析：** 建置系統、套件管理器（拓撲排序）。
*   **Social Networks:** "Friends of friends" or connectivity (BFS / Union-Find).
    **社交網絡：** 「朋友的朋友」或連通性（BFS / 並查集）。

### When NOT to Use (不適用場景)
*   **Simple Grid Traversal without Obstacles:** Math/Simulation might be faster.
    **無障礙的簡單網格遍歷：** 數學計算或模擬可能更快。
*   **Linear Dependencies:** Simple arrays suffice.
    **線性依賴：** 簡單陣列即足夠。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Shortest Path in Weighted Graph (Dijkstra)
**Pattern:** Priority Queue + BFS.
**模式：** 優先隊列 + BFS。
**Use case:** Finding the fastest route, minimum latency, or cheapest flight (non-negative weights).
**適用：** 尋找最快路徑、最小延遲或最便宜航班（非負權重）。

### B. Topological Sort (Kahn's Algorithm)
**Pattern:** In-degree Array + Queue.
**模式：** 入度陣列 + 隊列。
**Use case:** Course schedule, project planning, detecting cycles in directed graphs.
**適用：** 課程表、專案規劃、檢測有向圖中的環。

### C. Dynamic Connectivity (Union-Find / Disjoint Set)
**Pattern:** `find()` with path compression + `union()` by rank.
**模式：** 帶路徑壓縮的 `find()` + 按秩合併的 `union()`。
**Use case:** Counting connected components, Kruskal’s MST, validating tree structures.
**適用：** 計算連通分量、Kruskal 最小生成樹、驗證樹結構。

---

## 4. Example Walkthrough (範例講解)

### Problem: Network Delay Time (網路延遲時間)
*(Similar to LeetCode 743)*

**Problem Statement:**
You are given a network of `n` nodes, labeled from 1 to `n`. You are also given `times`, a list of travel times as directed edges `times[i] = (u, v, w)`, where `u` is the source node, `v` is the target node, and `w` is the time it takes for a signal to travel from source to target.
We send a signal from a given node `k`. Return the minimum time it takes for all `n` nodes to receive the signal. If it is impossible for all `n` nodes to receive the signal, return -1.

**問題重述：**
給定一個包含 `n` 個節點的網路，標記為 1 到 `n`。同時給定 `times`，這是一個有向邊的傳輸時間列表 `times[i] = (u, v, w)`，其中 `u` 是來源節點，`v` 是目標節點，`w` 是訊號從來源傳輸到目標所需的時間。
我們從給定的節點 `k` 發送訊號。請返回所有 `n` 個節點接收到訊號所需的最短時間。如果無法讓所有 `n` 個節點都接收到訊號，則返回 -1。

### Thought Process (思路)

1.  **Brute Force (DFS):**
    *   Explore all paths from `k` to every other node to find the minimum cost.
    *   **Issue:** Extremely inefficient ($O(N!)$ in worst case) and handles cycles poorly.
    *   **暴力解（DFS）：** 探索從 `k` 到所有其他節點的所有路徑以找到最小成本。
    *   **問題：** 極度低效（最壞情況 $O(N!)$）且難以處理環。

2.  **Optimization 1 (BFS):**
    *   Use a standard Queue.
    *   **Issue:** Standard BFS assumes all edges have weight 1. It finds the path with the *fewest edges*, not the *smallest total weight*.
    *   **優化 1（BFS）：** 使用標準隊列。
    *   **問題：** 標準 BFS 假設所有邊的權重為 1。它找到的是*邊數最少*的路徑，而不是*總權重最小*的路徑。

3.  **Optimal Solution (Dijkstra):**
    *   Since edge weights are non-negative, Dijkstra is the standard choice.
    *   Use a **Min-Heap (Priority Queue)** to always expand the node with the smallest accumulated time.
    *   Keep track of the minimum time to reach each node in a `dist` map/array.
    *   **最佳解（Dijkstra）：** 由於邊權重非負，Dijkstra 是標準選擇。
    *   使用 **最小堆積（優先隊列）** 來始終擴展累積時間最小的節點。
    *   在 `dist` 映射/陣列中記錄到達每個節點的最小時間。

### Complexity (複雜度)
*   **Time:** $O(E \log V)$ where $E$ is edges, $V$ is vertices.
*   **Space:** $O(V + E)$ for the adjacency list and distance map.

### TypeScript Solution (TypeScript 參考解)

*Note: Since JS/TS does not have a built-in Priority Queue, a simplified implementation is provided. In an interview, ask if you can assume a `MinHeap` class exists.*
*註：由於 JS/TS 沒有內建優先隊列，此處提供簡化實作。在面試中，請詢問是否可以假設 `MinHeap` 類別已存在。*

```typescript
/**
 * Simple MinHeap implementation for the interview context.
 * 為了面試情境設計的簡單最小堆積實作。
 */
class MinHeap {
  private heap: [number, number][] = []; // [cost, node]

  push(val: [number, number]): void {
    this.heap.push(val);
    this.bubbleUp(this.heap.length - 1);
  }

  pop(): [number, number] | undefined {
    if (this.heap.length === 0) return undefined;
    const min = this.heap[0];
    const end = this.heap.pop()!;
    if (this.heap.length > 0) {
      this.heap[0] = end;
      this.sinkDown(0);
    }
    return min;
  }

  size(): number {
    return this.heap.length;
  }

  private bubbleUp(idx: number): void {
    const element = this.heap[idx];
    while (idx > 0) {
      let parentIdx = Math.floor((idx - 1) / 2);
      let parent = this.heap[parentIdx];
      if (element[0] >= parent[0]) break;
      this.heap[parentIdx] = element;
      this.heap[idx] = parent;
      idx = parentIdx;
    }
  }

  private sinkDown(idx: number): void {
    const length = this.heap.length;
    const element = this.heap[idx];
    while (true) {
      let leftChildIdx = 2 * idx + 1;
      let rightChildIdx = 2 * idx + 2;
      let leftChild, rightChild;
      let swap = null;

      if (leftChildIdx < length) {
        leftChild = this.heap[leftChildIdx];
        if (leftChild[0] < element[0]) {
          swap = leftChildIdx;
        }
      }
      if (rightChildIdx < length) {
        rightChild = this.heap[rightChildIdx];
        if (
          (swap === null && rightChild[0] < element[0]) ||
          (swap !== null && rightChild[0] < leftChild![0])
        ) {
          swap = rightChildIdx;
        }
      }
      if (swap === null) break;
      this.heap[idx] = this.heap[swap];
      this.heap[swap] = element;
      idx = swap;
    }
  }
}

function networkDelayTime(times: number[][], n: number, k: number): number {
  // 1. Build Adjacency List (Graph representation)
  // 1. 建立鄰接表（圖的表示）
  const graph: Map<number, Array<[number, number]>> = new Map();
  
  for (const [u, v, w] of times) {
    if (!graph.has(u)) graph.set(u, []);
    graph.get(u)!.push([v, w]); // neighbor, weight
  }

  // 2. Initialize Dijkstra structures
  // 2. 初始化 Dijkstra 結構
  // dist stores the minimum time to reach node i from k
  // dist 儲存從 k 到達節點 i 的最小時間
  const dist: Map<number, number> = new Map();
  const minHeap = new MinHeap();

  // Start point: cost 0 to reach itself
  // 起點：到達自己的成本為 0
  minHeap.push([0, k]); 
  dist.set(k, 0);

  while (minHeap.size() > 0) {
    const [currentCost, u] = minHeap.pop()!;

    // Optimization: If we found a shorter path to u already, skip this stale entry
    // 優化：如果我們已經找到到達 u 的更短路徑，跳過這個過時的條目
    if (dist.has(u) && dist.get(u)! < currentCost) {
      continue;
    }

    // Explore neighbors
    // 探索鄰居
    if (graph.has(u)) {
      for (const [v, weight] of graph.get(u)!) {
        const newCost = currentCost + weight;
        
        // If new path is shorter, update dist and push to heap
        // 如果新路徑更短，更新 dist 並推入堆積
        if (!dist.has(v) || newCost < dist.get(v)!) {
          dist.set(v, newCost);
          minHeap.push([newCost, v]);
        }
      }
    }
  }

  // 3. Result Calculation
  // 3. 結果計算
  // If we haven't visited all n nodes, return -1
  // 如果我們沒有訪問所有 n 個節點，返回 -1
  if (dist.size !== n) return -1;

  // The time it takes for *all* nodes to receive signal is the max time in dist
  // 所有節點接收到訊號所需的時間是 dist 中的最大值
  let maxTime = 0;
  for (const time of dist.values()) {
    maxTime = Math.max(maxTime, time);
  }

  return maxTime;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Dijkstra** | **BFS** | **BFS** is for unweighted graphs (shortest path = fewest edges). **Dijkstra** is for weighted graphs (shortest path = min sum of weights). <br> **BFS** 適用於無權圖（最短路徑 = 最少邊）。**Dijkstra** 適用於加權圖（最短路徑 = 最小權重和）。 |
| **Backtracking (DFS)** | **Graph DFS** | Backtracking usually involves "un-visiting" nodes (resetting state) to find *all* paths. Graph DFS typically keeps nodes visited to avoid cycles and redundant work. <br> 回溯通常涉及「取消訪問」節點（重置狀態）以尋找*所有*路徑。圖 DFS 通常保留節點的訪問狀態以避免環和重複工作。 |
| **Dijkstra** | **Bellman-Ford** | Dijkstra fails with **negative weights**. Bellman-Ford handles negative weights and can detect negative cycles, but is slower ($O(VE)$). <br> Dijkstra 在**負權重**下會失效。Bellman-Ford 可處理負權重並檢測負環，但速度較慢（$O(VE)$）。 |
| **Visited Set** | **Recursion Stack** | In cycle detection (directed graph), `visited` tracks processed nodes, while `recursionStack` tracks nodes in the *current path*. <br> 在環檢測（有向圖）中，`visited` 追蹤已處理的節點，而 `recursionStack` 追蹤*當前路徑*中的節點。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (闡述口條框架)
1.  **Model the Problem:** "This looks like a graph problem where cities are nodes and flight costs are edge weights."
    **問題建模：** 「這看起來像是一個圖論問題，城市是節點，機票成本是邊的權重。」
2.  **Select Algorithm:** "Since we have weights and need the shortest path, BFS isn't enough. I'll use Dijkstra's algorithm."
    **選擇演算法：** 「由於有權重且需要最短路徑，BFS 不夠用。我將使用 Dijkstra 演算法。」
3.  **Discuss Data Structures:** "I'll represent the graph using an Adjacency List for $O(1)$ neighbor lookup. I'll need a Priority Queue for Dijkstra."
    **討論資料結構：** 「我將使用鄰接表來表示圖，以實現 $O(1)$ 的鄰居查找。我需要一個優先隊列來執行 Dijkstra。」

### Whiteboard Strategy (白板策略)
*   **Draw it out:** Always draw a small graph (3-4 nodes) to visualize the connections.
    **畫出來：** 務必畫一個小圖（3-4 個節點）來視覺化連接關係。
*   **Mock the Heap:** Don't implement the Heap from scratch unless asked. Write `const pq = new MinHeap();` and define its interface (`push`, `pop`).
    **模擬堆積：** 除非被要求，否則不要從頭實作堆積。寫下 `const pq = new MinHeap();` 並定義其介面（`push`, `pop`）。

### Common Follow-ups (常見追問)
*   "What if the weights can be negative?" -> Switch to Bellman-Ford or SPFA.
    「如果權重可能是負的怎麼辦？」 -> 切換到 Bellman-Ford 或 SPFA。
*   "What if the graph is extremely dense ($E \approx V^2$)?" -> Adjacency Matrix might be better, or Prim's for MST.
    「如果圖非常稠密（$E \approx V^2$）怎麼辦？」 -> 鄰接矩陣可能更好，或在 MST 中使用 Prim 演算法。

---

## 7. Practice Problems (練習題)

### Easy: Find the Town Judge (尋找小鎮法官)
*   **Concept:** In-degree vs Out-degree.
*   **Hint:** The judge has in-degree $N-1$ and out-degree $0$.
*   **觀念：** 入度 vs 出度。
*   **提示：** 法官的入度為 $N-1$，出度為 $0$。

### Medium: Course Schedule II (課程表 II)
*   **Concept:** Topological Sort (Kahn's Algorithm).
*   **Hint:** Build an adjacency list and an in-degree array. Process nodes with 0 in-degree, adding their neighbors to the queue as you decrement their in-degrees.
*   **觀念：** 拓撲排序（Kahn 演算法）。
*   **提示：** 建立鄰接表和入度陣列。處理入度為 0 的節點，將其鄰居的入度減 1，若減為 0 則加入隊列。

### Hard: Cheapest Flights Within K Stops (K 站中轉內最便宜的航班)
*   **Concept:** Modified Dijkstra or Bellman-Ford.
*   **Hint:** Standard Dijkstra finds the shortest path regardless of stops. You need to track `(cost, node, stops)` in the Priority Queue or run Bellman-Ford for exactly `K+1` iterations.
*   **觀念：** 修改版 Dijkstra 或 Bellman-Ford。
*   **提示：** 標準 Dijkstra 會忽略中轉次數尋找最短路徑。你需要在優先隊列中追蹤 `(cost, node, stops)`，或者執行 Bellman-Ford 恰好 `K+1` 次迭代。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] **Directed vs Undirected?** Did I handle the edges correctly when building the graph? (Double entry for undirected).
    **有向 vs 無向？** 建圖時是否正確處理了邊？（無向圖需雙向輸入）。
- [ ] **Connectivity:** Did I handle the case where the graph is disconnected? (Outer loop over all nodes).
    **連通性：** 是否處理了圖不連通的情況？（外層迴圈遍歷所有節點）。
- [ ] **Infinite Loop:** Did I use a `visited` set or distance array to prevent reprocessing nodes?
    **無限迴圈：** 是否使用了 `visited` 集合或距離陣列來防止重複處理節點？

### Complexity Check (複雜度確認)
- [ ] **Dijkstra:** $O(E \log V)$. If using an array instead of Heap, it becomes $O(V^2)$.
    **Dijkstra：** $O(E \log V)$。若使用陣列而非堆積，會變成 $O(V^2)$。
- [ ] **Union-Find:** Nearly $O(1)$ per operation with path compression ($\alpha(N)$).
    **並查集：** 配合路徑壓縮，每次操作近乎 $O(1)$（$\alpha(N)$）。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

*   **BFS is a Ripple (BFS 是漣漪):** Like dropping a stone in a pond, it expands layer by layer uniformly. Good for unweighted shortest path.
    **BFS 就像漣漪：** 像是在池塘丟入石頭，均勻地一層層擴散。適用於無權最短路徑。
*   **DFS is a Maze Runner (DFS 是迷宮跑者):** Runs as far as possible, hits a wall, and backtracks. Good for puzzles and exhaustive search.
    **DFS 就像迷宮跑者：** 跑得越遠越好，撞牆後回頭。適用於解謎和窮舉搜尋。
*   **Dijkstra is a Greedy Explorer (Dijkstra 是貪婪探險家):** Always takes the next step that looks cheapest *right now* from the starting point.
    **Dijkstra 就像貪婪探險家：** 總是選擇從起點看來*當前*最便宜的下一步。
*   **Union-Find is a Corporate Merger (Union-Find 是企業併購):** Small companies (nodes) merge into larger conglomerates (sets). You report to the CEO (root parent).
    **Union-Find 就像企業併購：** 小公司（節點）合併成大集團（集合）。你向 CEO（根父節點）匯報。