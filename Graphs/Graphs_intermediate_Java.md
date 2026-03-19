Here is the comprehensive guide on **Graphs (Intermediate)**, tailored for a Senior Software Engineer, designed by a Principal Engineer from Big Tech.

這是一份針對 **圖論（中階）** 的完整教材，專為資深軟體工程師量身打造，由 Big Tech 首席工程師設計。

---

# Graph Algorithms: Intermediate Level
# 圖論演算法：中階實戰

## 1. Learning Goals（學習目標）

1.  **Master Graph Representations:** Proficiently implement Adjacency Lists and Matrices in Java, knowing when to switch based on sparsity.
    **掌握圖的表示法：** 熟練地在 Java 中實作鄰接表（Adjacency List）與鄰接矩陣（Adjacency Matrix），並知道如何根據稀疏度切換。
2.  **Internalize Traversal Patterns:** Deeply understand BFS for shortest paths (unweighted) and DFS for connectivity/exhaustion, including iterative implementations.
    **內化遍歷模式：** 深刻理解用於最短路徑（無權重）的 BFS 與用於連通性/窮舉的 DFS，包含迭代實作方式。
3.  **Dependency Resolution:** Apply Topological Sort (Kahn’s Algorithm) to solve dependency problems.
    **依賴解析：** 應用拓撲排序（Kahn 演算法）來解決依賴性問題。
4.  **Disjoint Set Union (DSU):** Understand the Union-Find data structure for dynamic connectivity problems.
    **互斥集（DSU）：** 理解用於動態連通性問題的 Union-Find 資料結構。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
A Graph is a collection of nodes (vertices) and edges connecting them.
圖是由節點（頂點）與連接它們的邊所組成的集合。

Intuitively, think of it as a model for relationships: social networks (undirected), web crawling (directed), or state machines.
直觀上，將其視為關係的模型：社群網絡（無向）、網頁爬蟲（有向）或狀態機。

### Complexity（複雜度）
*   **Time:** Usually $O(V + E)$, where $V$ is vertices and $E$ is edges.
    **時間：** 通常為 $O(V + E)$，其中 $V$ 是頂點數，$E$ 是邊數。
*   **Space:** $O(V + E)$ for Adjacency List; $O(V^2)$ for Adjacency Matrix.
    **空間：** 鄰接表為 $O(V + E)$；鄰接矩陣為 $O(V^2)$。

### When to Use (Scenarios)（適用場景）
*   **Connectivity:** "Are these two users connected?"
    **連通性：** 「這兩個使用者是否相連？」
*   **Shortest Path:** "What is the fewest number of hops to reach the target?"
    **最短路徑：** 「到達目標所需的最少跳數是多少？」
*   **Dependencies:** "Which tasks must be done before others?"
    **依賴關係：** 「哪些任務必須在其他任務之前完成？」

### When NOT to Use（不適用場景）
*   **Simple Lookups:** If data has no relational structure, a HashMap or Array is faster.
    **簡單查找：** 如果資料沒有關係結構，HashMap 或 Array 會更快。
*   **Hierarchical Data:** Trees are specialized graphs; treat them as Trees (no cycles) for simpler recursion.
    **階層資料：** 樹是特化的圖；將它們視為樹（無環）處理，遞迴會更簡單。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Grid Traversal (Matrix DFS/BFS)
Treating a 2D array as a graph where cells are nodes and neighbors are edges.
將二維陣列視為圖，其中格子是節點，相鄰格子是邊。
*   *Key:* Direction arrays `int[][] dirs = {{0,1}, {1,0}, ...}`.
*   *關鍵：* 方向陣列 `int[][] dirs = {{0,1}, {1,0}, ...}`。

### B. Topological Sort (Kahn's Algorithm)
Used for finding a linear ordering of nodes in a Directed Acyclic Graph (DAG).
用於在有向無環圖（DAG）中尋找節點的線性排序。
*   *Key:* Indegree array and a Queue.
*   *關鍵：* 入度（Indegree）陣列與佇列（Queue）。

### C. Union-Find (Disjoint Set)
Efficiently manages a set of elements partitioned into disjoint subsets.
高效管理被劃分為互斥子集的元素集合。
*   *Key:* `find()` with path compression and `union()` by rank/size.
*   *關鍵：* 具備路徑壓縮的 `find()` 和依秩/大小合併的 `union()`。

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule (Topological Sort)
**Context:** LeetCode 207 - Can you finish all courses given prerequisites?
**背景：** LeetCode 207 - 給定先修條件，你能修完所有課程嗎？

**Problem Statement:**
There are `numCourses` courses labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return `true` if you can finish all courses.
共有 `numCourses` 門課程，編號從 `0` 到 `numCourses - 1`。給定一個陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修課程 `a`，必須先修課程 `b`。如果能修完所有課程，回傳 `true`。

### Approach Evolution（思路演進）

#### 1. Brute Force (DFS Cycle Detection)
Traverse from every node to check for cycles.
從每個節點遍歷以檢查是否有環。
*   *Drawback:* Requires complex state management (visiting, visited, unvisited) to distinguish current path cycles from cross edges.
*   *缺點：* 需要複雜的狀態管理（正在訪問、已訪問、未訪問）來區分當前路徑的環與交叉邊。

#### 2. Optimal: Kahn's Algorithm (BFS based)
Model the problem as a dependency graph. Nodes with 0 indegree (no prerequisites) can be taken immediately.
將問題建模為依賴圖。入度為 0（無先修條件）的節點可以立即修習。
*   **Step 1:** Build Adjacency List and Indegree Array.
    **步驟 1：** 建立鄰接表與入度陣列。
*   **Step 2:** Push all 0-indegree nodes to a Queue.
    **步驟 2：** 將所有入度為 0 的節點推入佇列。
*   **Step 3:** Process Queue, decrement neighbor indegrees. If a neighbor hits 0, add to Queue.
    **步驟 3：** 處理佇列，遞減鄰居的入度。若鄰居入度降為 0，加入佇列。
*   **Step 4:** Count processed nodes. If count equals `numCourses`, no cycle exists.
    **步驟 4：** 計算已處理節點數。若計數等於 `numCourses`，則無環存在。

### Complexity Analysis（複雜度分析）
*   **Time:** $O(V + E)$ - We process every node and edge once.
    **時間：** $O(V + E)$ - 我們處理每個節點與邊一次。
*   **Space:** $O(V + E)$ - To store the graph and queue.
    **空間：** $O(V + E)$ - 用於儲存圖與佇列。

### Java Reference Solution（Java 參考解）

```java
import java.util.*;

class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        // 1. Build the graph and indegree array
        // 1. 建立圖與入度陣列
        List<List<Integer>> graph = new ArrayList<>();
        int[] indegree = new int[numCourses];

        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }

        for (int[] pair : prerequisites) {
            int course = pair[0];
            int prereq = pair[1];
            // Edge: prereq -> course (prereq must be done before course)
            // 邊：先修課 -> 課程（先修課必須在課程前完成）
            graph.get(prereq).add(course);
            indegree[course]++;
        }

        // 2. Initialize Queue with nodes having 0 indegree
        // 2. 初始化佇列，放入入度為 0 的節點
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                queue.offer(i);
            }
        }

        int processedCount = 0;

        // 3. Process the graph
        // 3. 處理圖
        while (!queue.isEmpty()) {
            int current = queue.poll();
            processedCount++;

            for (int neighbor : graph.get(current)) {
                // Remove the dependency
                // 移除依賴
                indegree[neighbor]--;
                
                // If all prerequisites are met, add to queue
                // 若所有先修條件皆滿足，加入佇列
                if (indegree[neighbor] == 0) {
                    queue.offer(neighbor);
                }
            }
        }

        // 4. If we processed all courses, it's a DAG (no cycles)
        // 4. 若我們處理了所有課程，則為 DAG（無環）
        return processedCount == numCourses;
    }
}
```

### Common Mistake（錯誤示範）
Using a simple `visited` boolean array for DFS cycle detection in a directed graph.
在有向圖中使用簡單的 `visited` 布林陣列進行 DFS 環檢測。
*   *Why it fails:* It cannot distinguish between a "cycle" and two different paths merging into the same node (a valid DAG structure). You need three states (0=unvisited, 1=visiting, 2=visited).
*   *為何失敗：* 它無法區分「環」與兩條不同路徑匯合到同一節點的情況（合法的 DAG 結構）。你需要三種狀態（0=未訪問，1=訪問中，2=已訪問）。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Directed Graph (有向圖)** | **Undirected Graph (無向圖)** | In undirected graphs, an edge `(u, v)` implies `(v, u)`. Beware of infinite loops if you don't track `visited` or `parent`. <br> 在無向圖中，邊 `(u, v)` 隱含 `(v, u)`。若不追蹤 `visited` 或 `parent`，小心無窮迴圈。 |
| **DFS** | **Backtracking** | DFS is a traversal method; Backtracking is DFS *with state reset* to explore all combinations. <br> DFS 是一種遍歷方法；回溯是*帶有狀態重置*的 DFS，用於探索所有組合。 |
| **Connectivity (連通性)** | **Strong Connectivity (強連通性)** | Connectivity applies to undirected graphs. Strong connectivity (every node reachable from every other) applies to directed graphs. <br> 連通性適用於無向圖。強連通性（任兩點皆可互達）適用於有向圖。 |

---

## 6. Interview Strategy（面試實戰建議）

### Articulation Framework（口條框架）
1.  **Clarify Input:** "Is the graph directed or undirected? Can there be disconnected components? Is the input an edge list or matrix?"
    **釐清輸入：** 「圖是有向還是無向？會有不連通的組件嗎？輸入是邊列表還是矩陣？」
2.  **Define Approach:** "I will model this as a graph problem. Since we need to find dependencies, Topological Sort is the natural choice."
    **定義方法：** 「我會將此建模為圖論問題。由於我們需要尋找依賴關係，拓撲排序是自然的選擇。」
3.  **Handle Corner Cases:** "I will handle the case where the graph is empty or has disconnected nodes."
    **處理邊界情況：** 「我會處理圖為空或有不連通節點的情況。」

### Whiteboard Strategy（白板策略）
*   **Draw the Graph:** Don't just look at the array. Draw circles and arrows.
    **畫出圖形：** 不要只看陣列。畫出圓圈和箭頭。
*   **Separate Construction:** Write a helper function or a distinct block for building the graph (`buildGraph`). It keeps the main logic clean.
    **分離建構：** 寫一個輔助函式或獨立區塊來建立圖（`buildGraph`）。這能保持主邏輯乾淨。

### Common Follow-ups（常見追問）
*   "What if the graph is huge and cannot fit in memory?" (Answer: Distributed Graph Processing / MapReduce).
    「如果圖大到無法放入記憶體怎麼辦？」（答：分散式圖處理 / MapReduce）。
*   "How to print the cycle if one exists?" (Answer: Use DFS and store the `path` stack).
    「如果存在環，如何印出該環？」（答：使用 DFS 並儲存 `path` 堆疊）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Number of Islands (LeetCode 200)
*   **Concept:** Disconnected Components / Grid DFS.
    **觀念：** 不連通組件 / 網格 DFS。
*   **Hint:** Loop through the matrix. When you see a '1', increment count and trigger DFS/BFS to sink (mark '0') all connected land.
    **提示：** 遍歷矩陣。當看到 '1' 時，計數加一並觸發 DFS/BFS 將所有相連陸地「沉沒」（標記為 '0'）。

### 2. Medium: Redundant Connection (LeetCode 684)
*   **Concept:** Union-Find (Undirected Cycle Detection).
    **觀念：** Union-Find（無向圖環檢測）。
*   **Hint:** Iterate through edges. For edge `(u, v)`, if `find(u) == find(v)`, adding this edge creates a cycle. Return it.
    **提示：** 遍歷邊。對於邊 `(u, v)`，若 `find(u) == find(v)`，加入此邊會形成環。回傳該邊。

### 3. Medium/Hard: Word Ladder (LeetCode 127)
*   **Concept:** Shortest Path in Unweighted Graph (BFS).
    **觀念：** 無權重圖的最短路徑（BFS）。
*   **Hint:** Words are nodes. Edges exist if words differ by 1 char. Use BFS level-by-level to find the shortest transformation sequence. **Do not use DFS.**
    **提示：** 單字是節點。若單字差一個字元則存在邊。使用 BFS 逐層搜尋以找到最短轉換序列。**不要使用 DFS。**

---

## 8. Quick Checklists（快速檢核表）

### Debugging / Self-Review
- [ ] **Visited Set:** Did I initialize a `visited` set to prevent infinite loops?
    **已訪問集合：** 我是否初始化了 `visited` 集合以防止無窮迴圈？
- [ ] **Graph Build:** Did I correctly handle both directions if the graph is undirected? `adj.get(u).add(v)` AND `adj.get(v).add(u)`.
    **建圖：** 如果是無向圖，我是否正確處理了兩個方向？`adj.get(u).add(v)` 以及 `adj.get(v).add(u)`。
- [ ] **Disconnected Graph:** Does my algorithm assume the graph is fully connected? Did I loop through all nodes `0` to `n-1` to start traversal?
    **不連通圖：** 我的演算法是否假設圖是完全連通的？我是否遍歷了所有節點 `0` 到 `n-1` 來啟動遍歷？
- [ ] **Boundary Checks:** For grid problems, did I check `r < 0 || c < 0 || r >= rows || c >= cols`?
    **邊界檢查：** 對於網格問題，我是否檢查了 `r < 0 || c < 0 || r >= rows || c >= cols`？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **DFS is a Maze Runner:** Keep your hand on the wall, go as deep as possible, and only backtrack when you hit a dead end.
    **DFS 是迷宮跑者：** 手扶著牆，盡可能深入，只有在遇到死路時才回頭。
*   **BFS is a Ripple:** Like throwing a stone in a pond. The waves expand uniformly layer by layer. Best for "closest" targets.
    **BFS 是漣漪：** 就像往池塘丟石頭。波紋一層層均勻擴散。最適合尋找「最近」的目標。
*   **Topological Sort is Getting Dressed:** You cannot put on shoes (Node B) before putting on socks (Node A). Socks have `indegree = 0`.
    **拓撲排序是穿衣服：** 你不能在穿襪子（節點 A）之前穿鞋子（節點 B）。襪子的 `indegree = 0`。