# Advanced Graphs: Topological Sort & Union-Find
# 進階圖論：拓撲排序與並查集

## 1. Learning Goals（學習目標）

*   **Master Topological Sort (Kahn’s Algorithm):** Understand how to linearize Directed Acyclic Graphs (DAGs) to solve dependency problems.
    **掌握拓撲排序（Kahn 演算法）：** 理解如何將有向無環圖（DAG）線性化，以解決依賴關係問題。
*   **Understand Union-Find (Disjoint Set Union):** Learn to efficiently manage disjoint sets to detect cycles in undirected graphs and count connected components.
    **理解並查集（DSU）：** 學習如何高效管理不相交集合，以偵測無向圖中的環並計算連通分量。
*   **Identify Graph Patterns:** Recognize when a problem is a "dependency resolution" problem or a "connectivity" problem.
    **識別圖論模式：** 辨識問題何時屬於「依賴解析」問題或「連通性」問題。
*   **Bridge to System Design:** See how these algorithms apply to build systems, job schedulers, and social networks.
    **連結系統設計：** 了解這些演算法如何應用於建置系統、排程器與社群網路。

---

## 2. Core Concepts（核心觀念速覽）

### Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices such that for every directed edge $u \to v$, vertex $u$ comes before $v$ in the ordering.
    **定義：** 頂點的線性排序，使得對於每一條有向邊 $u \to v$，頂點 $u$ 在排序中都位於 $v$ 之前。
*   **Condition:** Only works on **Directed Acyclic Graphs (DAGs)**. If a cycle exists, no topological sort exists.
    **條件：** 僅適用於 **有向無環圖（DAG）**。若存在環，則無拓撲排序。
*   **Intuition:** "Finish prerequisites before taking the course."
    **直覺：** 「修課前先完成擋修科目。」
*   **Complexity:** Time $O(V + E)$, Space $O(V + E)$.
    **複雜度：** 時間 $O(V + E)$，空間 $O(V + E)$。

### Union-Find (並查集 / Disjoint Set Union)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個不相交（無重疊）子集的元素集合。
*   **Operations:** `find` (determine which subset an element is in) and `union` (join two subsets).
    **操作：** `find`（確定元素屬於哪個子集）與 `union`（合併兩個子集）。
*   **Optimization:** **Path Compression** and **Union by Rank** make operations nearly constant time ($O(\alpha(N))$).
    **優化：** **路徑壓縮** 與 **按秩合併** 使操作幾乎達到常數時間（$O(\alpha(N))$）。
*   **Use Case:** Network connectivity, image processing, lowest common ancestor.
    **適用場景：** 網路連通性、影像處理、最近共同祖先。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Dependency Resolution (Kahn's Algorithm)
**模式 A：依賴解析（Kahn 演算法）**
*   **Scenario:** Build order, compiler dependency, course schedule.
    **場景：** 建置順序、編譯器依賴、課程表。
*   **Key Logic:** Maintain an `in-degree` array. Process nodes with `in-degree == 0` (no dependencies), then decrease neighbors' in-degrees.
    **關鍵邏輯：** 維護一個 `in-degree`（入度）陣列。處理 `in-degree == 0`（無依賴）的節點，然後減少其鄰居的入度。

### Pattern B: Dynamic Connectivity (Union-Find)
**模式 B：動態連通性（並查集）**
*   **Scenario:** "Number of islands" (grid version is DFS/BFS, but dynamic edges is Union-Find), "Redundant Connection".
    **場景：** 「島嶼數量」（網格版用 DFS/BFS，但動態邊用 Union-Find）、「冗餘連接」。
*   **Key Logic:** Iterate through edges. If two nodes have different parents, `union` them. If same parent, a cycle is detected.
    **關鍵邏輯：** 遍歷邊。若兩節點父節點不同，則 `union` 合併。若父節點相同，則發現環。

---

## 4. Example Walkthrough（範例講解）

### Problem: Course Schedule II (LeetCode 210)
**問題：課程表 II**

**Problem Statement:**
You have `numCourses` labeled `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`. Return the ordering of courses. If impossible, return empty.
**問題重述：**
你有 `numCourses` 門課，編號 `0` 到 `numCourses - 1`。給定陣列 `prerequisites`，其中 `prerequisites[i] = [a, b]` 表示若想修課 `a`，必須先修課 `b`。回傳修課順序。若不可能，回傳空陣列。

### Approach（思路）

1.  **Brute Force (DFS all paths):** Try every permutation and validate. $O(N!)$. Too slow.
    **暴力解（DFS 所有路徑）：** 嘗試所有排列並驗證。$O(N!)$。太慢。
2.  **Optimization (Kahn's Algorithm):**
    **優化（Kahn 演算法）：**
    *   Build Adjacency List (Graph) and In-Degree Array.
        建立鄰接表（圖）與入度陣列。
    *   Add all nodes with `in-degree == 0` to a Queue.
        將所有 `in-degree == 0` 的節點加入佇列。
    *   Process Queue: Add node to result, decrement neighbors' in-degree. If neighbor becomes 0, add to Queue.
        處理佇列：將節點加入結果，減少鄰居入度。若鄰居入度變為 0，加入佇列。
    *   If result size != numCourses, there is a cycle.
        若結果長度 != numCourses，表示有環。

### TypeScript Solution (Reference)

```typescript
/**
 * Calculates the topological sort order for courses.
 * 計算課程的拓撲排序順序。
 * 
 * Time Complexity: O(V + E) - Process each vertex and edge once.
 * 時間複雜度：O(V + E) - 處理每個頂點與邊一次。
 * Space Complexity: O(V + E) - Adjacency list and arrays.
 * 空間複雜度：O(V + E) - 鄰接表與陣列。
 */
function findOrder(numCourses: number, prerequisites: number[][]): number[] {
    // 1. Initialize Graph and In-Degree Array
    // 1. 初始化圖與入度陣列
    const adjList: Map<number, number[]> = new Map();
    const inDegree: number[] = new Array(numCourses).fill(0);

    // Build the graph
    // 建構圖
    for (const [course, pre] of prerequisites) {
        // Pre -> Course (Pre is the dependency)
        // 先修課 -> 目標課（先修課是依賴項）
        if (!adjList.has(pre)) {
            adjList.set(pre, []);
        }
        adjList.get(pre)!.push(course);
        inDegree[course]++;
    }

    // 2. Initialize Queue with nodes having 0 in-degree
    // 2. 將入度為 0 的節點初始化至佇列
    const queue: number[] = [];
    for (let i = 0; i < numCourses; i++) {
        if (inDegree[i] === 0) {
            queue.push(i);
        }
    }

    const result: number[] = [];

    // 3. Process the queue (BFS style)
    // 3. 處理佇列（BFS 風格）
    while (queue.length > 0) {
        const current = queue.shift()!; // Dequeue / 出列
        result.push(current);

        if (adjList.has(current)) {
            for (const neighbor of adjList.get(current)!) {
                inDegree[neighbor]--; // Reduce dependency count / 減少依賴計數
                
                // If all dependencies are met, add to queue
                // 若所有依賴皆滿足，加入佇列
                if (inDegree[neighbor] === 0) {
                    queue.push(neighbor);
                }
            }
        }
    }

    // 4. Check for cycles
    // 4. 檢查是否有環
    // If result length is less than numCourses, a cycle exists (dependencies never resolved).
    // 若結果長度小於課程數，表示存在環（依賴永遠無法解析）。
    return result.length === numCourses ? result : [];
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Confusion | Correction / Clarification |
| :--- | :--- | :--- |
| **Cycle Detection** | Using Union-Find for **Directed** Graphs. <br> 在**有向**圖中使用並查集。 | Union-Find works for **Undirected** cycle detection. For Directed graphs, use Topo Sort or DFS (recursion stack). <br> 並查集適用於**無向**圖環偵測。有向圖請用拓撲排序或 DFS（遞迴堆疊）。 |
| **Graph Construction** | Confusing `[a, b]` as `a -> b` vs `b -> a`. <br> 混淆 `[a, b]` 是 `a -> b` 還是 `b -> a`。 | Always clarify direction. In Course Schedule, `[a, b]` usually means `b` is prereq for `a` (`b -> a`). <br> 務必釐清方向。在課程表中，`[a, b]` 通常指 `b` 是 `a` 的先修（`b -> a`）。 |
| **Disconnected Graphs** | Assuming the graph is fully connected. <br> 假設圖是完全連通的。 | Kahn's Algo handles disconnected components naturally. Standard DFS needs a loop over all nodes. <br> Kahn 演算法自然處理非連通分量。標準 DFS 需要對所有節點進行迴圈。 |
| **Complexity** | Thinking Union-Find is $O(1)$. <br> 認為並查集是 $O(1)$。 | It is $O(\alpha(N))$ (Inverse Ackermann function), practically constant but theoretically growing. <br> 它是 $O(\alpha(N))$（反阿克曼函數），實務上是常數，但理論上會增長。 |

---

## 6. Interview Strategy（面試實戰建議）

### Framework (口條框架)
1.  **Model the Problem:** "This problem involves dependencies/connections, so I will model it as a [Directed/Undirected] Graph."
    **將問題建模：** 「這個問題涉及依賴/連接，所以我會將其建模為 [有向/無向] 圖。」
2.  **Select Algorithm:** "Since we need a valid ordering, Topological Sort is the standard approach." OR "Since we are checking connectivity dynamically, Union-Find is optimal."
    **選擇演算法：** 「因為我們需要合法順序，拓撲排序是標準解法。」或「因為我們動態檢查連通性，並查集最優。」
3.  **Edge Cases:** "I will handle cases like disconnected components or cycles (impossible dependencies)."
    **邊界情況：** 「我會處理非連通分量或環（不可能的依賴）的情況。」

### Whiteboard Strategy (白板策略)
*   **Draw the Graph:** Don't just write code. Draw nodes and arrows.
    **畫出圖形：** 不要只寫程式碼。畫出節點與箭頭。
*   **Trace the In-Degrees:** Write `[0, 1, 2, 0]` next to nodes to show you understand Kahn's algorithm state.
    **追蹤入度：** 在節點旁寫下 `[0, 1, 2, 0]` 以展示你理解 Kahn 演算法的狀態。

### Common Follow-up
*   **Q:** Can we do this in parallel? (Parallel Course Schedule)
    **問：** 我們可以平行處理嗎？（平行課程表）
*   **A:** Yes, process all nodes currently in the Queue simultaneously. The number of "layers" (BFS levels) is the minimum time required.
    **答：** 可以，同時處理目前佇列中的所有節點。「層數」（BFS 層級）即為所需的最少時間。

---

## 7. Practice Problems（練習題）

### 1. Easy: Find if Path Exists in Graph
*   **Concept:** Basic BFS/DFS or Union-Find.
*   **Hint:** Just traverse from source. If you hit destination, return true.
*   **提示：** 從起點遍歷。若碰到終點，回傳 true。

### 2. Medium: Number of Provinces (LeetCode 547)
*   **Concept:** Connected Components (Union-Find or DFS).
*   **Hint:** Iterate through the matrix. If `isConnected[i][j] == 1`, perform `union(i, j)`. Count unique roots at the end.
*   **提示：** 遍歷矩陣。若 `isConnected[i][j] == 1`，執行 `union(i, j)`。最後計算唯一的根節點數量。

### 3. Hard: Alien Dictionary (LeetCode 269)
*   **Concept:** Advanced Topological Sort.
*   **Hint:** You must build the graph by comparing adjacent words to find the first differing character (e.g., "wrt", "wrf" -> `t -> f`). Then Topo Sort. Watch out for invalid inputs (prefix issues).
*   **提示：** 必須透過比較相鄰單字來建構圖，找出第一個不同的字元（如 "wrt", "wrf" -> `t -> f`）。然後進行拓撲排序。注意無效輸入（前綴問題）。

---

## 8. Quick Checklists（快速檢核表）

### For Topological Sort (Kahn's)
- [ ] Did I build the `inDegree` array correctly? (Check direction `u -> v` increases `v`'s in-degree).
- [ ] Did I handle the initial Queue (all 0 in-degree nodes)?
- [ ] Did I check `result.length == numNodes` to detect cycles?

### For Union-Find
- [ ] Did I implement **Path Compression** in `find()`? (Crucial for performance).
- [ ] Did I initialize the `parent` array where `parent[i] = i`?
- [ ] Am I counting components correctly? (Start with `N`, decrement on valid `union`).

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### Topological Sort = Getting Dressed (穿衣服)
*   **Analogy:** You cannot put on shoes before socks. You cannot put on a jacket before a shirt.
    **類比：** 你不能在穿襪子前穿鞋。你不能在穿襯衫前穿外套。
*   **Visual:** The "In-Degree 0" pile is the clothes currently on the bed ready to be worn. Once you wear the shirt, the jacket moves to the "ready" pile.
    **圖像：** 「入度為 0」的那堆是床上準備好可以穿的衣服。一旦穿上襯衫，外套就移到「準備好」的那堆。

### Union-Find = Corporate Mergers (企業合併)
*   **Analogy:** Every employee belongs to a company. When Company A buys Company B, the CEO of B now reports to the CEO of A.
    **類比：** 每個員工屬於一家公司。當 A 公司收購 B 公司，B 的 CEO 現在向 A 的 CEO 匯報。
*   **Path Compression:** Instead of reporting to a manager who reports to a director who reports to the CEO, everyone just remembers the CEO's name directly to save time.
    **路徑壓縮：** 與其向經理匯報，經理向總監匯報，總監向 CEO 匯報，不如每個人直接記住 CEO 的名字以節省時間。