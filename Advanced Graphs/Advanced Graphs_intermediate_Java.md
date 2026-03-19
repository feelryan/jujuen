Here is a comprehensive guide on **Advanced Graphs (Intermediate Level)**, tailored for a Senior Software Engineer.
這是一份針對 **進階圖論（中級難度）** 的完整教材，專為資深軟體工程師量身打造。

---

# Advanced Graphs: Topological Sort & Union-Find
# 進階圖論：拓撲排序與並查集

## 1. Learning Goals（學習目標）

1.  **Master Topological Sort (Kahn’s Algorithm & DFS):** Solve dependency resolution problems efficiently.
    **掌握拓撲排序（Kahn 演算法與 DFS）：** 高效解決依賴關係解析問題。
2.  **Internalize Union-Find (Disjoint Set Union):** Implement path compression and union by rank for dynamic connectivity.
    **內化並查集（DSU）：** 實作路徑壓縮與按秩合併以處理動態連通性。
3.  **Differentiate Graph Algorithms:** Know exactly when to use BFS/DFS vs. Dijkstra vs. Union-Find based on edge weights and direction.
    **區分圖論演算法：** 根據邊的權重與方向，精確判斷何時使用 BFS/DFS、Dijkstra 或 Union-Find。
4.  **Handle Disconnected Components & Cycles:** Robustly handle edge cases that break naive implementations.
    **處理非連通分量與環：** 穩健地處理能破壞樸素實作的邊界情況。

---

## 2. Core Concepts Speed Run（核心觀念速覽）

### A. Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 有向無環圖（DAG）中頂點的線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** "Peeling the onion." Remove nodes with no dependencies (indegree = 0), which unlocks new nodes.
    **直覺：** 「剝洋蔥」。移除沒有依賴（入度 = 0）的節點，進而解鎖新的節點。
*   **Complexity:** $O(V + E)$ Time, $O(V + E)$ Space.
    **複雜度：** 時間 $O(V + E)$，空間 $O(V + E)$。
*   **Use Case:** Build systems, course scheduling, task serialization.
    **適用場景：** 建置系統、課程排程、任務序列化。

### B. Union-Find (並查集 / Disjoint Set Union)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個互不相交（不重疊）子集的元素集合。
*   **Intuition:** "Representative Leadership." Every group has a "boss" (parent). To merge groups, make one boss report to the other.
    **直覺：** 「代表領導制」。每個群組都有一個「老大」（父節點）。要合併群組，就讓一個老大向另一個老大匯報。
*   **Complexity:** $O(\alpha(N))$ per operation (Inverse Ackermann function, effectively constant).
    **複雜度：** 每次操作 $O(\alpha(N))$（反阿克曼函數，實際上視為常數）。
*   **Use Case:** Network connectivity, cycle detection in undirected graphs, Minimum Spanning Tree (Kruskal's).
    **適用場景：** 網路連通性、無向圖中的環檢測、最小生成樹（Kruskal 演算法）。

---

## 3. Typical Patterns（典型題型 / 模式）

| Pattern (模式) | Keywords (關鍵字) | Algorithm Choice (演算法選擇) |
| :--- | :--- | :--- |
| **Dependency Resolution**<br>依賴解析 | "Order", "Prerequisites", "Serialize"<br>「順序」、「先修條件」、「序列化」 | **Topological Sort (Kahn's)**<br>拓撲排序（Kahn 演算法） |
| **Dynamic Connectivity**<br>動態連通性 | "Connected components", "Merge", "Equivalence"<br>「連通分量」、「合併」、「等價關係」 | **Union-Find**<br>並查集 |
| **Shortest Path (Weighted)**<br>最短路徑（帶權重） | "Min cost", "Min delay", "Positive weights"<br>「最小成本」、「最小延遲」、「正權重」 | **Dijkstra**<br>Dijkstra 演算法 |
| **Shortest Path (Unweighted)**<br>最短路徑（無權重） | "Min steps", "Shortest distance"<br>「最少步數」、「最短距離」 | **BFS**<br>廣度優先搜尋 |

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule II (課程表 II)
**LeetCode 210**

#### Problem Statement (問題重述)
You are given a total of `numCourses` courses labeled from `0` to `numCourses - 1`. You are also given an array `prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course `bi` first if you want to take course `ai`.
給定 `numCourses` 門課程，編號為 `0` 到 `numCourses - 1`。同時給定一個陣列 `prerequisites`，其中 `prerequisites[i] = [ai, bi]` 表示若想修習課程 `ai`，必須先修習課程 `bi`。

Return the ordering of courses you should take to finish all courses. If there are multiple valid answers, return any of them. If it is impossible, return an empty array.
回傳修完所有課程應採取的課程順序。若有多個有效答案，回傳其中任意一個。若無法完成，回傳空陣列。

#### Thought Process (思路)

1.  **Brute Force (DFS with Backtracking):**
    *   Try every permutation of courses and check if it satisfies constraints. $O(N!)$. Too slow.
    *   **暴力法（DFS 回溯）：** 嘗試所有課程排列組合並檢查是否符合限制。$O(N!)$。太慢。

2.  **Optimization (Topological Sort - Kahn's Algorithm):**
    *   Model the problem as a Directed Graph: Edge $B \to A$.
    *   Calculate **Indegree** (number of prerequisites) for each node.
    *   Push nodes with `Indegree == 0` into a Queue.
    *   Process Queue: Add node to result, decrement neighbors' indegree. If neighbor becomes 0, add to Queue.
    *   **優化（拓撲排序 - Kahn 演算法）：**
        *   將問題建模為有向圖：邊 $B \to A$。
        *   計算每個節點的 **入度（Indegree）**（先修課程數量）。
        *   將 `入度 == 0` 的節點放入佇列（Queue）。
        *   處理佇列：將節點加入結果，減少鄰居的入度。若鄰居入度變為 0，加入佇列。

3.  **Edge Cases (邊界條件):**
    *   **Cycle:** If the result size < numCourses, a cycle exists (impossible).
    *   **Disconnected Graph:** Kahn's algorithm naturally handles disconnected parts.
    *   **環：** 若結果長度 < numCourses，表示存在環（無法完成）。
    *   **非連通圖：** Kahn 演算法能自然處理非連通部分。

#### Java Solution (Reference)

```java
import java.util.*;

class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        // 1. Build Adjacency List and Indegree Array
        // 1. 建立鄰接表與入度陣列
        List<List<Integer>> adj = new ArrayList<>();
        int[] indegree = new int[numCourses];
        
        for (int i = 0; i < numCourses; i++) {
            adj.add(new ArrayList<>());
        }
        
        // Edge direction: prerequisite -> course (b -> a)
        // 邊的方向：先修課 -> 課程 (b -> a)
        for (int[] pair : prerequisites) {
            int course = pair[0];
            int prereq = pair[1];
            adj.get(prereq).add(course);
            indegree[course]++;
        }
        
        // 2. Initialize Queue with courses having no prerequisites
        // 2. 初始化佇列，放入沒有先修條件的課程
        Queue<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                queue.offer(i);
            }
        }
        
        // 3. Process the graph (BFS-like approach)
        // 3. 處理圖（類似 BFS 的方法）
        int[] result = new int[numCourses];
        int processedCount = 0;
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            result[processedCount++] = current;
            
            // Reduce indegree of neighbors
            // 減少鄰居節點的入度
            for (int neighbor : adj.get(current)) {
                indegree[neighbor]--;
                // If indegree becomes 0, it's ready to be taken
                // 若入度變為 0，表示該課程已可修習
                if (indegree[neighbor] == 0) {
                    queue.offer(neighbor);
                }
            }
        }
        
        // 4. Check for cycles
        // 4. 檢查是否存在環
        if (processedCount == numCourses) {
            return result;
        } else {
            // Cycle detected, impossible to finish all courses
            // 偵測到環，無法完成所有課程
            return new int[0];
        }
    }
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(V + E)$ — We visit every vertex and every edge once.
    **時間：** $O(V + E)$ — 我們訪問每個頂點與每條邊各一次。
*   **Space:** $O(V + E)$ — Adjacency list stores all edges; arrays store vertex data.
    **空間：** $O(V + E)$ — 鄰接表儲存所有邊；陣列儲存頂點資料。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

### A. Directed vs. Undirected Cycle Detection (有向圖與無向圖的環檢測)
*   **Undirected:** Union-Find is the best tool. If you try to union two nodes that already share a parent, there is a cycle.
    **無向圖：** 並查集是最佳工具。若嘗試合併兩個已擁有相同父節點的節點，則存在環。
*   **Directed:** Union-Find generally **cannot** be used directly for directed cycles (it ignores direction). Use DFS (recursion stack tracking) or Kahn's Algorithm (nodes left over).
    **有向圖：** 並查集通常**不能**直接用於有向環（它忽略方向）。應使用 DFS（追蹤遞迴堆疊）或 Kahn 演算法（剩餘未處理節點）。

### B. Visited Array in DFS (DFS 中的已訪問陣列)
*   **Confusion:** Using a simple boolean `visited` for cycle detection in directed graphs.
    **混淆：** 在有向圖中僅使用簡單的布林值 `visited` 來檢測環。
*   **Correction:** You need **three states**: `0` (unvisited), `1` (visiting/current path), `2` (visited/safe). A cycle exists only if you encounter a node in state `1`.
    **修正：** 你需要 **三種狀態**：`0`（未訪問）、`1`（訪問中/當前路徑）、`2`（已訪問/安全）。只有遇到狀態為 `1` 的節點時，才表示有環。

### C. Dijkstra with Negative Weights (Dijkstra 與負權重)
*   **Pitfall:** Using Dijkstra on graphs with negative edges.
    **陷阱：** 在有負邊的圖上使用 Dijkstra。
*   **Result:** Dijkstra assumes once a node is processed, its optimal distance is found. Negative edges break this greedy assumption. Use Bellman-Ford instead.
    **結果：** Dijkstra 假設一旦節點被處理，其最佳距離即已確定。負邊會打破此貪婪假設。應改用 Bellman-Ford。

---

## 6. Interview Strategy（面試實戰建議）

### Framework (口條框架)
1.  **Model the Data:** "This problem can be modeled as a [Directed/Undirected] graph where [Entities] are nodes and [Relationships] are edges."
    **資料建模：** 「這個問題可以建模為 [有向/無向] 圖，其中 [實體] 是節點，[關係] 是邊。」
2.  **Select Algorithm:** "Since we need to resolve dependencies/find connectivity, I will use [Topo Sort/Union-Find]."
    **選擇演算法：** 「由於我們需要解析依賴關係/尋找連通性，我將使用 [拓撲排序/並查集]。」
3.  **Discuss Trade-offs:** "I'm choosing Adjacency List over Matrix because the graph is likely sparse ($E \ll V^2$)."
    **討論權衡：** 「我選擇鄰接表而非矩陣，因為這張圖很可能是稀疏的（$E \ll V^2$）。」

### Whiteboard Strategy (白板策略)
*   **Define Inputs:** Write `N` (nodes) and `edges` clearly.
    **定義輸入：** 清楚寫下 `N`（節點數）與 `edges`（邊）。
*   **Modularize:** For Union-Find, write the class/functions separately. Don't inline the logic inside the main loop; it looks messy.
    **模組化：** 對於並查集，將類別/函數分開寫。不要將邏輯內聯在主迴圈中；那樣看起來很亂。
*   **Dry Run:** Trace a small example with a cycle (if applicable) to show your logic handles it.
    **模擬執行：** 追蹤一個帶有環的小範例（若適用），以展示你的邏輯能處理它。

---

## 7. Practice Problems（練習題）

### Level 1: Easy/Intermediate (暖身)
**Problem:** Number of Provinces (LeetCode 547)
**Concept:** Union-Find (Basic) or DFS.
**Hint:** Iterate through the matrix. If `isConnected[i][j] == 1`, `union(i, j)`. Count distinct parents or decrement count on successful union.
**提示：** 遍歷矩陣。若 `isConnected[i][j] == 1`，執行 `union(i, j)`。計算不同的父節點數量，或在成功合併時減少計數。

### Level 2: Intermediate (核心)
**Problem:** Course Schedule II (LeetCode 210)
**Concept:** Topological Sort.
**Hint:** See the example walkthrough above. Focus on handling the "impossible" case correctly.
**提示：** 參見上方的範例講解。專注於正確處理「不可能」的情況。

### Level 3: Advanced (挑戰)
**Problem:** Alien Dictionary (LeetCode 269) or Sequence Reconstruction (LeetCode 444)
**Concept:** Topo Sort + String Parsing + Edge Cases.
**Hint:** Build the graph by comparing adjacent words character by character. The first differing character defines the edge order. Watch out for prefix edge cases (e.g., "abc" before "ab" is invalid).
**提示：** 透過逐字元比較相鄰單字來建圖。第一個不同的字元定義了邊的順序。注意前綴邊界情況（例如 "abc" 在 "ab" 之前是無效的）。

---

## 8. Quick Checklists（快速檢核表）

### Debugging / Self-Review (自我審查)
- [ ] **Graph Construction:** Did I handle 0-based vs 1-based indexing?
    **圖的建置：** 我是否處理了 0-based 與 1-based 的索引差異？
- [ ] **Direction:** Is the graph directed or undirected? Did I add edges both ways if undirected?
    **方向性：** 圖是有向還是無向？若是無向，我是否雙向都加了邊？
- [ ] **Cycle Handling:** Does my code crash or loop infinitely if there is a cycle?
    **環處理：** 若存在環，我的程式碼會崩潰還是無窮迴圈？
- [ ] **Connectivity:** Did I account for nodes that are completely isolated?
    **連通性：** 我是否考慮了完全孤立的節點？

### Complexity Check (複雜度確認)
- [ ] **Union-Find:** Did I implement Path Compression? (Without it, it's $O(N)$, not $O(1)$).
    **並查集：** 我是否實作了路徑壓縮？（沒有它，複雜度是 $O(N)$ 而非 $O(1)$）。
- [ ] **Topo Sort:** Are we removing edges efficiently? (Using an indegree array is $O(1)$ lookup).
    **拓撲排序：** 我們是否高效地移除了邊？（使用入度陣列查詢是 $O(1)$）。

---

## 9. Memory Anchors（記憶錨點）

### Topological Sort: "The University Degree" (大學學位)
*   **Visual:** Imagine a flowchart of university courses.
*   **Analogy:** You cannot take "Advanced Algorithms" (Node B) without "Data Structures" (Node A).
*   **Action:** You hold a list of courses you *can* take right now (Queue). Once you finish one, you check if it unlocks new ones.
*   **圖像：** 想像大學課程的流程圖。
*   **類比：** 沒有修過「資料結構」（節點 A），就不能修「進階演算法」（節點 B）。
*   **動作：** 你手上有一個現在*可以*修的課程清單（佇列）。一旦修完一門，就檢查它是否解鎖了新課程。

### Union-Find: "The Mafia Families" (黑手黨家族)
*   **Visual:** Several small gangs merging.
*   **Analogy:**
    *   `find(x)`: Ask a gangster "Who is your Godfather?" They ask their boss, who asks their boss, until the Don is found.
    *   `union(x, y)`: Two families merge. The Don of family X now reports to the Don of family Y.
    *   **Path Compression:** Once you find out who the Don is, you save his number directly so you don't have to ask the middle-managers next time.
*   **圖像：** 幾個小幫派正在合併。
*   **類比：**
    *   `find(x)`：問一個混混「你的教父是誰？」他問他的老大，老大再問他的老大，直到找到最高領袖（Don）。
    *   `union(x, y)`：兩個家族合併。家族 X 的教父現在向家族 Y 的教父匯報。
    *   **路徑壓縮：** 一旦你知道最高領袖是誰，直接存下他的號碼，下次就不用再問中間的主管了。