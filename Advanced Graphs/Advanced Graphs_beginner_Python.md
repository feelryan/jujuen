Here is the comprehensive interview preparation guide for **Advanced Graphs**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **進階圖論（Advanced Graphs）** 完整面試準備指南。

The difficulty level is set to **Beginner** within the scope of Advanced Graphs (focusing on foundational "Advanced" algorithms like Dijkstra and Topological Sort, rather than research-level algorithms).
難度設定為進階圖論範疇內的 **入門級**（著重於 Dijkstra 和 拓撲排序 等基石級的進階演算法，而非研究級演算法）。

---

# Advanced Graphs: Foundation & Patterns
# 進階圖論：基礎與模式

## 1. Learning Goals（學習目標）

1.  **Master Shortest Path Algorithms in Weighted Graphs.**
    掌握加權圖中的最短路徑演算法（重點在於 Dijkstra）。
2.  **Understand Dependency Resolution using Topological Sort.**
    理解如何使用拓撲排序來解決依賴關係問題。
3.  **Differentiate between Graph Traversal (BFS/DFS) and Advanced Pathfinding.**
    區分基本圖遍歷（BFS/DFS）與進階路徑搜尋的差異。
4.  **Translate Real-world Problems into Graph Models.**
    將現實世界的問題轉化為圖論模型。

---

## 2. Core Concepts Overview（核心觀念速覽）

### A. Dijkstra’s Algorithm（Dijkstra 演算法）
*   **Definition:** A greedy algorithm to find the shortest path from a source node to all other nodes in a graph with **non-negative** edge weights.
    **定義：** 一種貪婪演算法，用於在邊權重 **非負** 的圖中，尋找從起點到所有其他節點的最短路徑。
*   **Intuition:** Always explore the "cheapest" node reachable from the current set of visited nodes.
    **直覺：** 總是優先探索從當前已訪問節點集合中可到達的「成本最低」的節點。
*   **Time Complexity:** $O(E \log V)$ using a Min-Heap (Priority Queue).
    **時間複雜度：** 使用最小堆積（優先佇列）時為 $O(E \log V)$。
*   **Applicability:** Routing, network delay, maps.
    **適用場景：** 路由、網路延遲、地圖導航。
*   **Constraint:** Does not work with negative edge weights.
    **限制：** 不適用於帶有負權重邊的圖。

### B. Topological Sort（拓撲排序）
*   **Definition:** A linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 有向無環圖（DAG）中頂點的線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** Finish prerequisites before taking a course; put on socks before shoes.
    **直覺：** 修課前先完成先修課程；穿鞋前先穿襪子。
*   **Time Complexity:** $O(V + E)$ (Kahn's Algorithm or DFS).
    **時間複雜度：** $O(V + E)$（Kahn 演算法或 DFS）。
*   **Applicability:** Build systems, task scheduling, dependency resolution.
    **適用場景：** 建置系統、任務排程、依賴解析。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern 1: Shortest Path in Weighted Graph (Dijkstra)
### 模式一：加權圖最短路徑（Dijkstra）
*   **Scenario:** "Find the minimum time/cost/distance to reach target X."
    **情境：** 「尋找到達目標 X 所需的最小時間/成本/距離。」
*   **Key Data Structure:** `PriorityQueue` (Min-Heap).
    **關鍵資料結構：** `PriorityQueue`（最小堆積）。

### Pattern 2: Dependency Resolution (Kahn's Algorithm)
### 模式二：依賴解析（Kahn 演算法）
*   **Scenario:** "Can you finish all courses?" or "Find a valid build order."
    **情境：** 「你能修完所有課程嗎？」或「找出一個合法的建置順序。」
*   **Key Data Structure:** `Indegree Array` + `Queue`.
    **關鍵資料結構：** `入度陣列` + `佇列`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Network Delay Time
### 問題：網路延遲時間

**Problem Statement:**
You are given a network of `n` nodes, labeled from 1 to `n`. You are also given `times`, a list of travel times as directed edges `times[i] = (u, v, w)`, where `u` is the source node, `v` is the target node, and `w` is the time it takes for a signal to travel from source to target. We send a signal from a given node `k`. Return the time it takes for all `n` nodes to receive the signal. If it is impossible for all `n` nodes to receive the signal, return -1.

**問題重述：**
給定一個包含 `n` 個節點的網路，標記為 1 到 `n`。同時給定 `times` 列表，表示有向邊的傳輸時間 `times[i] = (u, v, w)`，其中 `u` 是起點，`v` 是終點，`w` 是訊號傳輸所需時間。我們從節點 `k` 發出訊號。請返回所有 `n` 個節點接收到訊號所需的時間。如果無法讓所有節點都收到訊號，則返回 -1。

### Approach & Evolution（思路演進）

1.  **Brute Force / BFS (Incorrect for Weighted):**
    **暴力解 / BFS（對加權圖錯誤）：**
    *   *Thought:* Use standard BFS level by level.
        *想法：* 使用標準 BFS 逐層遍歷。
    *   *Flaw:* BFS assumes each "step" has equal weight (1). Here, edges have different weights. A path with more edges might actually be "shorter" (faster) than a path with fewer edges.
        *缺陷：* BFS 假設每「步」權重相等（為 1）。這裡邊有不同權重。邊數較多的路徑實際上可能比邊數較少的路徑「更短」（更快）。

2.  **Optimal Solution: Dijkstra’s Algorithm:**
    **最佳解：Dijkstra 演算法：**
    *   *Strategy:* Use a Min-Heap to always process the node with the shortest accumulated time found so far.
        *策略：* 使用最小堆積，總是優先處理目前累積時間最短的節點。
    *   *State:* Track the minimum time to reach each node in a `dist` map.
        *狀態：* 在 `dist` 雜湊表中記錄到達每個節點的最小時間。

### Python Solution（Python 參考解）

```python
import heapq
from collections import defaultdict
from typing import List

def networkDelayTime(times: List[List[int]], n: int, k: int) -> int:
    # 1. Build the Adjacency List (Graph)
    # 1. 建立鄰接表（圖）
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    
    # 2. Initialize Min-Heap and Distance Map
    # Priority Queue stores tuples: (current_accumulated_time, current_node)
    # 2. 初始化最小堆積與距離表
    # 優先佇列儲存元組：(當前累積時間, 當前節點)
    min_heap = [(0, k)]
    
    # Map to store the minimum time to reach a node. 
    # If a node is in this map, we have found the shortest path to it.
    # 用於儲存到達某節點的最小時間。
    # 如果節點已在此表中，表示我們已找到到達它的最短路徑。
    dist = {}
    
    while min_heap:
        time, node = heapq.heappop(min_heap)
        
        # If we have already visited this node with a shorter time, skip it.
        # 如果我們已經用更短的時間訪問過此節點，則跳過。
        if node in dist:
            continue
        
        # Record the shortest time for this node
        # 記錄此節點的最短時間
        dist[node] = time
        
        # Explore neighbors
        # 探索鄰居
        for neighbor, weight in graph[node]:
            if neighbor not in dist:
                heapq.heappush(min_heap, (time + weight, neighbor))
    
    # 3. Result Calculation
    # If we visited all n nodes, the answer is the max time in dist (the last node reached).
    # 3. 結果計算
    # 如果我們訪問了所有 n 個節點，答案是 dist 中的最大時間（最後一個被到達的節點）。
    if len(dist) == n:
        return max(dist.values())
    else:
        return -1

# Example Usage
# times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
# Output should be 2
```

### Complexity Analysis（複雜度分析）
*   **Time:** $O(E \log E)$ or $O(E \log V)$. In the worst case, we push every edge onto the heap.
    **時間：** $O(E \log E)$ 或 $O(E \log V)$。在最壞情況下，我們將每條邊都推入堆積中。
*   **Space:** $O(V + E)$ for the adjacency list and the heap.
    **空間：** $O(V + E)$ 用於鄰接表和堆積。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Standard BFS (標準 BFS) | Dijkstra (Dijkstra 演算法) |
| :--- | :--- | :--- |
| **Edge Weights** (邊權重) | Unweighted (all 1) (無權重/全為 1) | Weighted (non-negative) (加權/非負) |
| **Data Structure** (資料結構) | Queue (FIFO) (佇列) | Priority Queue (Min-Heap) (優先佇列) |
| **Visited Logic** (訪問邏輯) | Mark visited upon **pushing** to queue (入隊時標記) | Mark visited upon **popping** from heap (出堆時標記) |
| **Complexity** (複雜度) | $O(V + E)$ | $O(E \log V)$ |

**Critical Mistake:** Using a `visited` set immediately when pushing to the heap in Dijkstra.
**嚴重錯誤：** 在 Dijkstra 中，將節點推入堆積時立即使用 `visited` 集合標記。
*   *Correction:* You must allow nodes to be pushed multiple times if a shorter path is found later. Only mark as "finalized" when you **pop** it from the heap.
    *修正：* 如果稍後發現更短的路徑，必須允許節點被多次推入。只有當從堆積中 **取出** 時，才將其標記為「已定案」。

---

## 6. Interview Strategy（面試實戰建議）

### Framework (口條框架)
1.  **Clarify Constraints:** "Are edge weights positive? Is the graph directed or undirected? Can there be cycles?"
    **釐清限制：** 「邊的權重是正數嗎？是有向圖還是無向圖？會有環嗎？」
2.  **Model the Problem:** "This looks like a shortest path problem. Since weights are non-negative, Dijkstra is the optimal choice."
    **建立模型：** 「這看起來是個最短路徑問題。因為權重非負，Dijkstra 是最佳選擇。」
3.  **Define State:** "I will use a Min-Heap to store `(cost, node)` and a hash map for finalized distances."
    **定義狀態：** 「我會用一個最小堆積來存 `(成本, 節點)`，並用雜湊表來存已定案的距離。」

### Whiteboard Strategy (白板策略)
*   Draw a small graph (3-4 nodes) with weights.
    畫一個帶有權重的小型圖（3-4 個節點）。
*   Write down the `Heap` state and `Dist` map state step-by-step as you trace.
    在追蹤過程中，逐步寫下 `Heap` 狀態和 `Dist` 表的狀態。

### Common Follow-ups (常見追問)
*   **Q:** What if weights can be negative?
    **問：** 如果權重可能是負的怎麼辦？
    *   **A:** Dijkstra fails. We need Bellman-Ford ($O(VE)$).
        **答：** Dijkstra 會失效。我們需要 Bellman-Ford ($O(VE)$)。
*   **Q:** What if we need the path itself, not just the distance?
    **問：** 如果我們需要路徑本身，而不僅僅是距離？
    *   **A:** Store a `parent` map: `parent[v] = u` whenever we update the distance to `v`. Backtrack from target to source.
        **答：** 儲存一個 `parent` 映射：每當更新到 `v` 的距離時記錄 `parent[v] = u`。最後從終點回溯到起點。

---

## 7. Practice Problems（練習題）

### Easy: Find the Town Judge
### 易：尋找小鎮法官
*   **Concept:** Graph Degrees (Indegree/Outdegree).
    **觀念：** 圖的度數（入度/出度）。
*   **Hint:** The judge has indegree $N-1$ and outdegree $0$.
    **提示：** 法官的入度為 $N-1$，出度為 $0$。

### Medium: Course Schedule II
### 中：課程表 II
*   **Concept:** Topological Sort.
    **觀念：** 拓撲排序。
*   **Hint:** Build an adjacency list and an indegree array. Add nodes with 0 indegree to the queue.
    **提示：** 建立鄰接表和入度陣列。將入度為 0 的節點加入佇列。

### Hard: Cheapest Flights Within K Stops
### 難：K 站中轉內的最便宜航班
*   **Concept:** BFS / Modified Dijkstra.
    **觀念：** BFS / 修改版 Dijkstra。
*   **Hint:** This is Dijkstra but with a depth constraint ($K$). You cannot simply discard a path just because it's more expensive if it uses fewer stops.
    **提示：** 這是 Dijkstra 但帶有深度限制（$K$）。你不能僅僅因為某條路徑較貴就丟棄它，如果它的中轉次數較少，可能後續會用到。

---

## 8. Quick Checklists（快速檢核表）

Use this during your coding phase.
在編碼階段使用此表。

*   [ ] **Graph Representation:** Did I handle directed vs. undirected correctly? (Undirected needs `graph[v].append(u)` too).
    **圖的表示：** 我是否正確處理了有向與無向？（無向圖也需要 `graph[v].append(u)`）。
*   [ ] **Heap Elements:** Is the tuple `(cost, node)`? Python heaps sort by the first element.
    **堆積元素：** 元組是 `(cost, node)` 嗎？Python 堆積是根據第一個元素排序的。
*   [ ] **Initialization:** Is the start node pushed to the heap with cost 0?
    **初始化：** 起始節點是否以成本 0 推入堆積？
*   [ ] **Loop Termination:** Did I handle the case where the graph is disconnected (heap empty but target not reached)?
    **迴圈終止：** 我是否處理了圖不連通的情況（堆積為空但未到達目標）？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **Dijkstra is like Water Spreading:**
    **Dijkstra 就像水流擴散：**
    Water flows through pipes. It reaches the nearest points first. The pipe width is the "weight". It naturally finds the path of least resistance.
    水流經管道。它會最先到達最近的點。管道的寬度就是「權重」。它自然會找到阻力最小的路徑。

*   **Topological Sort is like Getting Dressed:**
    **拓撲排序就像穿衣服：**
    Underwear -> Pants -> Belt. You cannot put on the belt before the pants. The "Indegree" is the number of clothing items you *must* put on before the current item.
    內褲 -> 褲子 -> 皮帶。你不能在穿褲子之前繫皮帶。「入度」就是你在穿當前物品前 *必須* 先穿上的衣物數量。