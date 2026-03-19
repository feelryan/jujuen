Here is the comprehensive guide for **Advanced Graphs (Intermediate)**, tailored for a Senior Software Engineer targeting Big Tech roles.
這是一份針對 **進階圖論（中級）** 的完整教材，專為目標 Big Tech 職位的資深軟體工程師量身打造。

---

# Advanced Graphs: Topological Sort & Union-Find
# 進階圖論：拓撲排序與並查集

## 1. Learning Objectives (學習目標)

1.  **Master Dependency Resolution:** Understand how to model dependency problems using Directed Acyclic Graphs (DAG) and Topological Sort.
    **掌握依賴解析：** 理解如何使用有向無環圖（DAG）和拓撲排序來為依賴問題建模。
2.  **Conquer Connectivity Problems:** Utilize Union-Find (Disjoint Set Union) to solve dynamic connectivity and cycle detection in undirected graphs efficiently.
    **征服連通性問題：** 利用並查集（DSU）高效解決無向圖中的動態連通性與環檢測問題。
3.  **Graph Modeling Capability:** Develop the intuition to transform abstract problems (like build systems or social networks) into graph representations.
    **圖形建模能力：** 培養將抽象問題（如構建系統或社交網絡）轉化為圖形表示的直覺。
4.  **Complexity Analysis:** Deeply understand the time/space trade-offs, specifically $O(V+E)$ for traversal and $\alpha(N)$ for Union-Find.
    **複雜度分析：** 深入理解時間/空間權衡，特別是遍歷的 $O(V+E)$ 與並查集的 $\alpha(N)$。

---

## 2. Core Concepts (核心觀念速覽)

### Topological Sort (拓撲排序)
*   **Definition:** A linear ordering of vertices such that for every directed edge $u \to v$, vertex $u$ comes before $v$.
    **定義：** 頂點的線性排序，使得對於每條有向邊 $u \to v$，頂點 $u$ 都在 $v$ 之前。
*   **Intuition:** Think of it as a task scheduler; you cannot put on shoes before socks.
    **直覺：** 把它想像成任務排程器；你不能在穿襪子之前穿鞋子。
*   **Applicability:** Only works on **DAGs** (Directed Acyclic Graphs). If a cycle exists, no topological sort is possible.
    **適用性：** 僅適用於 **有向無環圖 (DAG)**。如果存在環，則無法進行拓撲排序。

### Union-Find / Disjoint Set Union (並查集)
*   **Definition:** A data structure that tracks a set of elements partitioned into a number of disjoint (non-overlapping) subsets.
    **定義：** 一種資料結構，用於追蹤被劃分為多個不相交（不重疊）子集的元素集合。
*   **Intuition:** Managing group memberships. "Is person A friends with person B (transitively)?"
    **直覺：** 管理群組成員資格。「A 和 B 是朋友嗎（具傳遞性）？」
*   **Complexity:** Near constant time $O(\alpha(N))$ per operation with Path Compression and Union by Rank.
    **複雜度：** 使用路徑壓縮和按秩合併後，每次操作接近常數時間 $O(\alpha(N))$。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: Kahn’s Algorithm (BFS based Topo Sort)
**Use case:** Course schedules, build order, detecting cycles in directed graphs.
**適用場景：** 課程表、構建順序、檢測有向圖中的環。

1.  Calculate **indegree** (number of incoming edges) for all nodes.
    計算所有節點的 **入度**（進入邊的數量）。
2.  Push nodes with `indegree == 0` into a queue.
    將 `indegree == 0` 的節點放入佇列。
3.  Process queue: Remove node $u$, add to result, and decrement indegree of neighbors.
    處理佇列：移除節點 $u$，加入結果集，並將鄰居的入度減一。
4.  If neighbor's indegree becomes 0, push to queue.
    若鄰居入度變為 0，則推入佇列。

### Pattern B: Union-Find (DSU)
**Use case:** Connected components, cycle detection in undirected graphs, "Redundant Connection".
**適用場景：** 連通分量、無向圖中的環檢測、「冗餘連接」。

1.  **Find:** Determine which subset a particular element is in (with Path Compression).
    **查找：** 確定特定元素屬於哪個子集（配合路徑壓縮）。
2.  **Union:** Join two subsets into a single subset (with Union by Rank/Size).
    **合併：** 將兩個子集合併為一個（配合按秩/大小合併）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Course Schedule II (LeetCode 210)
**Problem Statement:**
Given a total of `numCourses` and a list of prerequisite pairs `[a, b]` (meaning you must take course `b` before `a`), return the ordering of courses to finish all. If impossible, return empty.
**問題重述：**
給定課程總數 `numCourses` 和先修課程對 `[a, b]`（意味著必須先修 `b` 才能修 `a`），返回修完所有課程的順序。若不可能，返回空。

### Approach (思路)

1.  **Brute Force (DFS without states):** Try all permutations. $O(N!)$. Impossible for $N=2000$.
    **暴力法（無狀態 DFS）：** 嘗試所有排列。$O(N!)$。對於 $N=2000$ 不可行。
2.  **Optimization (DFS with 3 colors):** Mark nodes as Unvisited (0), Visiting (1), Visited (2). If we meet a 'Visiting' node, a cycle exists.
    **優化（三色標記 DFS）：** 將節點標記為未訪問 (0)、訪問中 (1)、已訪問 (2)。若遇到「訪問中」的節點，則存在環。
3.  **Best Solution (Kahn's Algorithm):** More intuitive for "ordering" problems and easier to implement iteratively.
    **最佳解（Kahn 演算法）：** 對於「排序」問題更直觀，且更容易以迭代方式實作。

### C++ Reference Solution (Kahn's Algorithm)

```cpp
#include <vector>
#include <queue>
#include <iostream>

using namespace std;

class Solution {
public:
    vector<int> findOrder(int numCourses, vector<vector<int>>& prerequisites) {
        // 1. Build Adjacency List and Indegree Array
        // 1. 建立鄰接表和入度陣列
        vector<vector<int>> adj(numCourses);
        vector<int> indegree(numCourses, 0);
        
        for (const auto& pair : prerequisites) {
            int course = pair[0];
            int prereq = pair[1];
            
            // Edge direction: prereq -> course
            // 邊的方向：先修課 -> 課程
            adj[prereq].push_back(course);
            indegree[course]++;
        }
        
        // 2. Initialize Queue with nodes having 0 indegree
        // 2. 將入度為 0 的節點放入佇列初始化
        queue<int> q;
        for (int i = 0; i < numCourses; ++i) {
            if (indegree[i] == 0) {
                q.push(i);
            }
        }
        
        vector<int> result;
        
        // 3. Process the graph (BFS)
        // 3. 處理圖形 (BFS)
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            result.push_back(current);
            
            for (int neighbor : adj[current]) {
                indegree[neighbor]--;
                // If dependencies are met, add to queue
                // 若依賴已滿足，加入佇列
                if (indegree[neighbor] == 0) {
                    q.push(neighbor);
                }
            }
        }
        
        // 4. Cycle Detection: If result size != numCourses, there is a cycle
        // 4. 環檢測：若結果大小 != 課程總數，表示有環
        if (result.size() != numCourses) {
            return {};
        }
        
        return result;
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(V + E)$. We visit every vertex and every edge exactly once.
    **時間：** $O(V + E)$。我們確切地訪問每個頂點和每條邊一次。
*   **Space:** $O(V + E)$. Adjacency list stores all edges; indegree array and queue store vertices.
    **空間：** $O(V + E)$。鄰接表儲存所有邊；入度陣列和佇列儲存頂點。

### Error Demonstration (錯誤示範)
*   **Mistake:** Forgetting to check `result.size() != numCourses`.
    **錯誤：** 忘記檢查 `result.size() != numCourses`。
*   **Why wrong:** Even if the queue becomes empty, nodes involved in a cycle will never have `indegree == 0` and will remain unprocessed. The function would return a partial list, which is incorrect.
    **為何錯：** 即使佇列變空，參與環的節點之入度永遠不會是 0，因此不會被處理。函式會返回部分清單，這是錯誤的。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Topological Sort (Kahn's) | DFS Traversal |
| :--- | :--- | :--- |
| **Cycle Handling** | Implicitly detects cycles (nodes left over). <br> 隱式檢測環（剩餘未處理節點）。 | Needs explicit recursion stack tracking (visited set). <br> 需要顯式的遞迴堆疊追蹤（visited 集合）。 |
| **Graph Type** | **Directed** only. <br> 僅限 **有向圖**。 | Directed or Undirected. <br> 有向或無向皆可。 |
| **Start Point** | All nodes with `indegree == 0`. <br> 所有 `indegree == 0` 的節點。 | Arbitrary node (often loop through all). <br> 任意節點（通常迴圈遍歷所有）。 |

**Crucial Pitfall in Union-Find:**
**並查集的關鍵陷阱：**
Not implementing **Path Compression**. Without it, the tree can become a linked list, degrading `find` operations to $O(N)$.
未實作 **路徑壓縮**。若無此優化，樹可能退化成連結串列，導致 `find` 操作退化為 $O(N)$。

---

## 6. Interview Strategy (面試實戰建議)

### Framework (口條框架)
1.  **Model the Problem:** "This problem involves dependencies/connectivity, which suggests a Graph approach."
    **問題建模：** 「這個問題涉及依賴/連通性，這提示了使用圖論方法。」
2.  **Define Nodes & Edges:** "I will treat courses as nodes and prerequisites as directed edges."
    **定義節點與邊：** 「我將課程視為節點，先修要求視為有向邊。」
3.  **Select Algorithm:** "Since we need a linear ordering, Topological Sort is the standard approach."
    **選擇演算法：** 「由於我們需要線性排序，拓撲排序是標準做法。」

### Whiteboard Strategy (白板策略)
*   **Draw the Graph:** Don't just write code. Draw nodes and arrows. Visually show a cycle to demonstrate the edge case.
    **畫出圖形：** 不要只寫程式碼。畫出節點和箭頭。視覺化地畫出一個環來展示邊界情況。
*   **Trace the Queue:** Write `Q: [0, 1] -> [1, 2]` on the side to show you understand the flow.
    **追蹤佇列：** 在旁邊寫下 `Q: [0, 1] -> [1, 2]` 以展示你理解流程。

### Common Follow-ups (常見追問)
*   **Q:** Can we do this in parallel?
    **問：** 我們可以並行處理嗎？
    *   **A:** Yes, in Kahn's algo, all nodes currently in the Queue can be processed simultaneously (e.g., taking multiple courses in one semester).
    *   **答：** 可以，在 Kahn 演算法中，目前佇列中的所有節點都可以同時處理（例如，一個學期修多門課）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Find if Path Exists in Graph (LeetCode 1971)
*   **Goal:** Basic graph construction and BFS/DFS/Union-Find.
    **目標：** 基礎圖形建構與 BFS/DFS/並查集。
*   **Hint:** Just check if `find(source) == find(destination)` using Union-Find.
    **提示：** 使用並查集檢查 `find(source) == find(destination)` 即可。

### 2. Medium: Number of Provinces (LeetCode 547)
*   **Goal:** Counting connected components.
    **目標：** 計算連通分量數量。
*   **Hint:** Iterate through the matrix. If `isConnected[i][j]`, `union(i, j)`. Count unique roots at the end.
    **提示：** 遍歷矩陣。若 `isConnected[i][j]`，執行 `union(i, j)`。最後計算唯一根節點的數量。

### 3. Hard: Alien Dictionary (LeetCode 269)
*   **Goal:** Constructing a graph from strings + Topological Sort.
    **目標：** 從字串建構圖形 + 拓撲排序。
*   **Hint:** Compare adjacent words to find edge directions (first differing character). Watch out for prefix edge cases (e.g., "abc" before "ab" is invalid).
    **提示：** 比較相鄰單字以找出邊的方向（第一個不同的字元）。注意前綴邊界情況（例如 "abc" 在 "ab" 之前是無效的）。

---

## 8. Checklists (快速檢核表)

### Complexity Check (複雜度確認)
- [ ] Did I handle the adjacency list construction cost? ($O(E)$)
      我有考慮鄰接表建構的成本嗎？($O(E)$)
- [ ] Is my Union-Find using Path Compression?
      我的並查集有使用路徑壓縮嗎？

### Edge Cases (邊界條件)
- [ ] Disconnected graph? (Does the problem guarantee connectivity?)
      非連通圖？（題目保證連通嗎？）
- [ ] Cycle in a directed graph? (Topo sort fails)
      有向圖中的環？（拓撲排序失敗）
- [ ] Self-loops? (Graph contains edge $i \to i$)
      自環？（圖包含邊 $i \to i$）

---

## 9. Memory Anchors (記憶錨點)

*   **Topological Sort = Peeling an Onion (剝洋蔥)**
    *   The skin (nodes with indegree 0) must be removed first to reveal the next layer.
    *   外皮（入度為 0 的節點）必須先移除，才能露出下一層。
*   **Union-Find = Corporate Mergers (企業併購)**
    *   Smaller companies point to the parent company. `find()` asks "Who is the CEO?". Path compression is memorizing the CEO's name directly so you don't ask your manager's manager's manager next time.
    *   小公司指向母公司。`find()` 詢問「誰是 CEO？」。路徑壓縮就是直接記住 CEO 的名字，這樣下次就不用問經理的經理的經理了。