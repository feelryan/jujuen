# Advanced Graphs: Intermediate Guide (Topological Sort & Union-Find)
# 進階圖論：中階指南（拓撲排序與並查集）

## 1. Learning Objectives (學習目標)

1.  **Master Topological Sorting for Dependency Resolution.**
    掌握用於解決依賴關係問題的拓撲排序。
2.  **Implement and Optimize Union-Find (Disjoint Set Union).**
    實作並優化並查集（DSU）資料結構。
3.  **Distinguish between Directed/Undirected Cycle Detection.**
    區分有向圖與無向圖中的環檢測差異。
4.  **Apply these patterns to real-world scenarios (Build Systems, Social Networks).**
    將這些模式應用於現實場景（如建置系統、社群網絡）。

---

## 2. Core Concepts (核心觀念速覽)

### Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 在有向無環圖（DAG）中，將頂點線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** Putting on clothes (socks before shoes) or compiling code (libraries before app).
    **直覺：** 穿衣服（先穿襪子再穿鞋）或編譯程式碼（先編譯函式庫再編譯應用程式）。
*   **Complexity:** Time $O(V + E)$, Space $O(V + E)$.
    **複雜度：** 時間 $O(V + E)$，空間 $O(V + E)$。

### Union-Find / Disjoint Set Union (並查集)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個不相交（無重疊）子集的元素集合。
*   **Intuition:** Merging social circles. If Person A knows B, and B knows C, they all belong to the same "connected component".
    **直覺：** 合併社交圈。如果 A 認識 B，且 B 認識 C，則他們都屬於同一個「連通分量」。
*   **Complexity:** Time $O(\alpha(N))$ (Inverse Ackermann function, nearly constant), Space $O(N)$.
    **複雜度：** 時間 $O(\alpha(N))$（反阿克曼函數，幾近常數），空間 $O(N)$。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Kahn’s Algorithm (BFS for Topo Sort)
**模式 A：Kahn 演算法（用於拓撲排序的 BFS）**
*   **Use Case:** Finding a valid execution order; detecting cycles in a directed graph.
    **適用場景：** 尋找合法的執行順序；檢測有向圖中的環。
*   **Key Concept:** `In-degree` (number of incoming edges). Start with nodes having 0 in-degree.
    **核心概念：** `入度`（進入邊的數量）。從入度為 0 的節點開始。

### Pattern B: Union-Find with Path Compression & Rank
**模式 B：具路徑壓縮與按秩合併的並查集**
*   **Use Case:** Dynamic connectivity (adding edges and checking if connected), finding redundant connections, counting islands/provinces.
    **適用場景：** 動態連通性（新增邊並檢查是否連通）、尋找多餘連線、計算島嶼/省份數量。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule II (課程表 II)
**問題重述：**
You are given a total of `numCourses` courses labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return the ordering of courses you should take to finish all courses. If impossible, return an empty array.
給定 `numCourses` 門課程，編號為 `0` 到 `numCourses - 1`。給定陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若要修習課程 `a`，必須先修習課程 `b`。請回傳修完所有課程的順序。若不可能，回傳空陣列。

### Approach (思路)

1.  **Brute Force (DFS without states):**
    **暴力解（無狀態 DFS）：**
    Trying to permute all courses and check validity is $O(N!)$, which is infeasible.
    嘗試排列所有課程並檢查合法性是 $O(N!)$，不可行。

2.  **Optimization (Kahn's Algorithm):**
    **優化（Kahn 演算法）：**
    *   Model the problem as a graph: Course = Node, Prereq = Edge ($b \to a$).
        將問題建模為圖：課程 = 節點，先修要求 = 邊 ($b \to a$)。
    *   Calculate **in-degree** for every node.
        計算每個節點的**入度**。
    *   Push nodes with `in-degree == 0` into a queue (courses with no prereqs).
        將 `入度 == 0` 的節點放入佇列（無先修要求的課程）。
    *   Process queue: remove node, add to result, and decrement in-degree of neighbors.
        處理佇列：移除節點，加入結果，並將鄰居的入度減一。
    *   If a neighbor's in-degree becomes 0, add to queue.
        若鄰居入度變為 0，加入佇列。

3.  **Cycle Detection:**
    **環檢測：**
    If the result length does not equal `numCourses`, a cycle exists (dependencies cannot be resolved).
    如果結果長度不等於 `numCourses`，則存在環（依賴關係無法解析）。

### TypeScript Solution (參考解)

```typescript
function findOrder(numCourses: number, prerequisites: number[][]): number[] {
    // Adjacency list to store the graph: index -> list of dependent courses
    // 鄰接表儲存圖：索引 -> 依賴該課程的後續課程列表
    const adjList: number[][] = Array.from({ length: numCourses }, () => []);
    
    // Array to store in-degrees (number of prerequisites for each course)
    // 陣列儲存入度（每門課程的先修要求數量）
    const inDegree: number[] = new Array(numCourses).fill(0);

    // Build the graph
    // 建構圖
    for (const [course, pre] of prerequisites) {
        // Edge direction: pre -> course (pre must be taken before course)
        // 邊的方向：先修 -> 課程（先修必須在課程之前）
        adjList[pre].push(course);
        inDegree[course]++;
    }

    // Queue for courses with no prerequisites (in-degree 0)
    // 佇列用於存放無先修要求的課程（入度為 0）
    const queue: number[] = [];
    for (let i = 0; i < numCourses; i++) {
        if (inDegree[i] === 0) {
            queue.push(i);
        }
    }

    const result: number[] = [];

    // Process the queue (BFS)
    // 處理佇列（廣度優先搜尋）
    while (queue.length > 0) {
        // Use shift() for queue behavior (FIFO). Note: shift is O(K) in JS arrays, 
        // but acceptable here as total operations are bounded by V+E. 
        // For strict O(1), use a pointer or a proper Queue implementation.
        // 使用 shift() 實現佇列行為（先進先出）。注意：JS 陣列的 shift 是 O(K)，
        // 但在此處可接受，因為總操作受限於 V+E。若需嚴格 O(1)，請使用指標或真正的 Queue 實作。
        const current = queue.shift()!;
        result.push(current);

        // Visit neighbors
        // 訪問鄰居
        for (const neighbor of adjList[current]) {
            inDegree[neighbor]--;
            // If prerequisites are met, add to queue
            // 若先修要求已滿足，加入佇列
            if (inDegree[neighbor] === 0) {
                queue.push(neighbor);
            }
        }
    }

    // Check for cycles: if result size != numCourses, there is a cycle
    // 檢查環：如果結果長度 != numCourses，表示有環
    return result.length === numCourses ? result : [];
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(V + E)$ where $V$ is `numCourses` and $E$ is `prerequisites.length`. We visit every vertex and edge once.
    **時間：** $O(V + E)$，其中 $V$ 是 `numCourses`， $E$ 是 `prerequisites.length`。我們訪問每個頂點和邊各一次。
*   **Space:** $O(V + E)$ for the adjacency list and in-degree array.
    **空間：** $O(V + E)$，用於鄰接表和入度陣列。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Confusion (錯誤/混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Cycle Detection (DFS)** | Using a simple `visited` set for directed graphs. <br> 在有向圖中僅使用簡單的 `visited` 集合。 | You need **three states**: `unvisited`, `visiting` (current recursion stack), and `visited`. A cycle is found if you meet a node in `visiting` state. <br> 你需要**三種狀態**：`未訪問`、`訪問中`（當前遞迴堆疊）、`已訪問`。若遇到 `訪問中` 的節點，則表示有環。 |
| **Union-Find vs DFS** | Using Union-Find for directed graphs. <br> 在有向圖中使用並查集。 | Union-Find is primarily for **undirected** connectivity. For directed reachability, use BFS/DFS. <br> 並查集主要用於**無向**連通性。對於有向可達性，請使用 BFS/DFS。 |
| **Topological Sort** | Thinking it produces a unique order. <br> 認為它產生的順序是唯一的。 | There can be multiple valid topological sorts if multiple nodes have 0 in-degree simultaneously. <br> 若同時有多個節點入度為 0，則可能存在多種合法的拓撲排序。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarify Graph Properties (釐清圖的性質)
*   **Ask:** "Is the graph directed or undirected?" (Crucial for algorithm selection).
    **問：** 「圖是有向的還是無向的？」（對選擇演算法至關重要）。
*   **Ask:** "Can the graph contain cycles?" (Determines if you need cycle detection logic).
    **問：** 「圖中是否可能包含環？」（決定是否需要環檢測邏輯）。
*   **Ask:** "Is the graph connected?" (You might need to iterate over all nodes to trigger BFS/DFS).
    **問：** 「圖是連通的嗎？」（你可能需要遍歷所有節點來觸發 BFS/DFS）。

### 2. Whiteboard Strategy (白板策略)
*   **Draw it out:** Draw nodes and edges. For Topo Sort, write the "In-degree" next to each node and update it manually as you simulate.
    **畫出來：** 畫出節點和邊。對於拓撲排序，在每個節點旁寫下「入度」，並在模擬時手動更新。
*   **Data Structure Definition:** Explicitly state: "I will use an Array of Arrays for the adjacency list because the nodes are dense integers from 0 to N-1."
    **資料結構定義：** 明確說明：「我將使用陣列的陣列作為鄰接表，因為節點是從 0 到 N-1 的稠密整數。」

### 3. Follow-up Questions (常見追問)
*   **Q:** How to handle parallel execution? (e.g., build system)
    **問：** 如何處理平行執行？（例如建置系統）
    *   **A:** In Kahn's algo, the size of the queue at any step represents tasks that can be run in parallel.
    *   **答：** 在 Kahn 演算法中，任何步驟中佇列的大小代表可以平行執行的任務。

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單)
**Problem:** [Find the Town Judge](https://leetcode.com/problems/find-the-town-judge/)
*   **Hint:** Treat trust as a directed graph. The judge has in-degree $N-1$ and out-degree $0$.
    **提示：** 將信任視為有向圖。法官的入度為 $N-1$，出度為 $0$。

### Level: Intermediate (中等) - **Highly Recommended**
**Problem:** [Number of Provinces](https://leetcode.com/problems/number-of-provinces/)
*   **Hint:** Classic Union-Find application. Initialize $N$ components, union them when connected, count remaining components.
    **提示：** 經典並查集應用。初始化 $N$ 個分量，連通時合併，計算剩餘分量。

### Level: Hard (困難)
**Problem:** [Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) (Premium/Classic)
*   **Hint:** Build a graph from character order differences. Perform Topological Sort. Handle edge cases like prefix issues ("abc" before "ab" is invalid).
    **提示：** 根據字元順序差異建構圖。執行拓撲排序。處理邊界情況，如前綴問題（"abc" 在 "ab" 之前是不合法的）。

---

## 8. Quick Checklists (快速檢核表)

### Complexity Check (複雜度檢查)
- [ ] Did I use Adjacency Matrix ($O(V^2)$) or Adjacency List ($O(V+E)$)? List is usually better.
      我用的是鄰接矩陣 ($O(V^2)$) 還是鄰接表 ($O(V+E)$)？通常鄰接表較佳。
- [ ] For Union-Find, did I implement **Path Compression**? Without it, it's $O(N)$ per op, not $O(\alpha(N))$.
      對於並查集，我是否實作了**路徑壓縮**？若無，每次操作是 $O(N)$ 而非 $O(\alpha(N))$。

### Bug Check (除錯檢查)
- [ ] **Directed vs Undirected:** Did I add edges both ways (`adj[u].push(v)` and `adj[v].push(u)`) for undirected graphs?
      **有向 vs 無向：** 對於無向圖，我是否雙向添加了邊？
- [ ] **Disconnected Components:** Did I loop through `0` to `n-1` to ensure all nodes are visited, or just start from node 0?
      **非連通分量：** 我是否迴圈遍歷 `0` 到 `n-1` 以確保訪問所有節點，還是只從節點 0 開始？

---

## 9. Memory Anchors (記憶錨點)

*   **Topological Sort = "Unlocking Levels"**
    **拓撲排序 = 「解鎖關卡」**
    Imagine a video game skill tree. You cannot unlock "Fireball II" until you have "Fireball I" and "Mana Boost". The queue holds skills currently available to be learned.
    想像電玩遊戲的技能樹。在擁有「火球術 I」和「魔力增幅」之前，你無法解鎖「火球術 II」。佇列中存放的是當前可以學習的技能。

*   **Union-Find = "Mafia Families"**
    **並查集 = 「黑手黨家族」**
    Everyone reports to a "Godfather" (root parent). When two families merge, one Godfather bows to the other. Path compression is realizing you don't need to talk to the middle-man; you report directly to the top boss.
    每個人都向「教父」（根父節點）匯報。當兩個家族合併時，一位教父向另一位臣服。路徑壓縮就是意識到你不需要透過中間人，而是直接向最高老闆匯報。