Here is the comprehensive interview preparation guide for **Graphs (Beginner Level)**, tailored for a Senior Software Engineer.
這是一份針對 **圖論（入門級）** 的完整面試準備指南，專為資深軟體工程師量身打造。

---

# Graph Theory: Beginner Module (圖論：入門模組)

## 1. Learning Objectives (學習目標)

1.  **Master Graph Representations:** Understand the trade-offs between Adjacency Matrix and Adjacency List, and implement them fluently in Python.
    **掌握圖的表示法：** 理解鄰接矩陣（Adjacency Matrix）與鄰接表（Adjacency List）之間的權衡，並能流利地用 Python 實作。
2.  **Core Traversal Algorithms:** Internalize BFS (Breadth-First Search) and DFS (Depth-First Search) mechanics, specifically knowing when to use which.
    **核心遍歷演算法：** 內化廣度優先搜尋（BFS）與深度優先搜尋（DFS）的機制，特別是知道何時該用哪一種。
3.  **State Management:** Learn how to track visited nodes to prevent cycles and infinite loops, a common failure point in interviews.
    **狀態管理：** 學習如何追蹤已訪問節點以防止環（Cycles）與無窮迴圈，這是面試中常見的失敗點。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Graph consists of a set of vertices (nodes) and a set of edges connecting these vertices.
圖由一組頂點（節點）和一組連接這些頂點的邊組成。

### Key Properties (關鍵屬性)
*   **Directed vs. Undirected:** Do edges have a direction (A $\to$ B) or are they bidirectional (A $-$ B)?
    **有向 vs. 無向：** 邊是有方向的（A $\to$ B）還是雙向的（A $-$ B）？
*   **Weighted vs. Unweighted:** Do edges carry a cost/weight? (Beginner module focuses on Unweighted).
    **有權 vs. 無權：** 邊是否帶有成本/權重？（入門模組專注於無權圖）。
*   **Cyclic vs. Acyclic:** Can you traverse from a node back to itself?
    **有環 vs. 無環：** 你能否從一個節點遍歷並回到它自己？

### Representation & Complexity (表示法與複雜度)

| Type (類型) | Description (描述) | Space Complexity (空間複雜度) | Lookup Edge (查詢邊) | Use Case (適用場景) |
| :--- | :--- | :--- | :--- | :--- |
| **Adjacency List** | Dictionary or List of Lists (`{u: [v1, v2]}`). <br> 字典或列表的列表。 | $O(V + E)$ | $O(\text{degree of } V)$ | Most interview problems (Sparse graphs). <br> 大多數面試題（稀疏圖）。 |
| **Adjacency Matrix** | 2D Array (`grid[u][v] = 1`). <br> 二維陣列。 | $O(V^2)$ | $O(1)$ | Dense graphs or when edge existence check must be constant time. <br> 稠密圖或需要常數時間檢查邊是否存在時。 |

*   **$V$**: Number of Vertices (頂點數).
*   **$E$**: Number of Edges (邊數).

---

## 3. Typical Patterns (典型題型 / 模式)

For beginner graph problems, there are two dominant patterns.
對於入門級圖論問題，有兩種主要模式。

### Pattern A: Breadth-First Search (BFS)
*   **Mechanism:** Uses a **Queue** (FIFO). Explores neighbors layer by layer.
    **機制：** 使用 **佇列**（先進先出）。逐層探索鄰居。
*   **Best For:** Finding the **shortest path** in unweighted graphs or level-order traversal.
    **適用於：** 在無權圖中尋找 **最短路徑** 或層序遍歷。

### Pattern B: Depth-First Search (DFS)
*   **Mechanism:** Uses a **Stack** (LIFO) or **Recursion**. Dives as deep as possible before backtracking.
    **機制：** 使用 **堆疊**（後進先出）或 **遞迴**。在回溯前盡可能深入探索。
*   **Best For:** Exhaustive search, path existence, cycle detection, or topological sorting.
    **適用於：** 窮舉搜尋、路徑存在性檢查、環檢測或拓撲排序。

---

## 4. Example Walkthrough (範例講解)

### Problem: Valid Path (有效路徑)
**Problem Statement:** Given `n` nodes (0 to `n-1`) and a list of `edges`, determine if there is a valid path from `source` to `destination`.
**問題重述：** 給定 `n` 個節點（0 到 `n-1`）和一個 `edges` 列表，判斷是否存在從 `source` 到 `destination` 的有效路徑。

### Thinking Process (思路)

1.  **Brute Force (Random Walk):** Just follow edges randomly.
    **暴力解（隨機遊走）：** 隨機沿著邊走。
    *   *Issue:* Will get stuck in cycles (infinite loop) and is inefficient.
    *   *問題：* 會卡在環中（無窮迴圈）且效率低。

2.  **Optimization (Systematic Traversal):** Use BFS or DFS with a `visited` set.
    **優化（系統性遍歷）：** 使用 BFS 或 DFS 搭配 `visited` 集合。
    *   Since we only need to know if a path *exists* (not necessarily the shortest), both work. DFS is often easier to write recursively.
    *   因為我們只需要知道路徑是否 *存在*（不一定是最短），兩者皆可。DFS 通常用遞迴寫起來較簡單。

3.  **Best Approach (Adjacency List + BFS/DFS):**
    **最佳解（鄰接表 + BFS/DFS）：**
    *   First, convert the edge list `[[0,1], [1,2]]` into an adjacency list `{0: [1], 1: [0, 2], ...}` for $O(1)$ access to neighbors.
    *   首先，將邊列表 `[[0,1], [1,2]]` 轉換為鄰接表 `{0: [1], 1: [0, 2], ...}`，以便 $O(1)$ 存取鄰居。

### Python Solution (BFS Approach)

```python
from collections import deque, defaultdict
from typing import List

def valid_path(n: int, edges: List[List[int]], source: int, destination: int) -> bool:
    # 1. Build Adjacency List (Graph Construction)
    # 1. 建立鄰接表（建圖）
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u) # For undirected graph (對於無向圖)
    
    # 2. Initialize BFS structures
    # 2. 初始化 BFS 結構
    queue = deque([source])
    visited = set([source]) # Crucial: Mark start as visited immediately (關鍵：立即標記起點為已訪問)
    
    # 3. Traverse
    # 3. 遍歷
    while queue:
        # Pop current node (O(1) operation with deque)
        # 取出當前節點（deque 的操作為 O(1)）
        curr = queue.popleft()
        
        # Check if we reached the target
        # 檢查是否到達目標
        if curr == destination:
            return True
        
        # Visit neighbors
        # 訪問鄰居
        for neighbor in graph[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return False

# Time Complexity: O(V + E) - We visit every node and edge at most once.
# 時間複雜度：O(V + E) - 我們最多訪問每個節點和邊一次。
# Space Complexity: O(V + E) - To store the graph and the visited set.
# 空間複雜度：O(V + E) - 用於儲存圖和已訪問集合。
```

### Common Mistake (錯誤示範)
Using a Python `list` as a queue with `pop(0)`.
使用 Python 的 `list` 作為佇列並使用 `pop(0)`。
*   **Why wrong:** `list.pop(0)` is $O(N)$ operation because it shifts all elements. This turns BFS into $O(V^2)$.
*   **為何錯：** `list.pop(0)` 是 $O(N)$ 操作，因為它會移動所有元素。這會將 BFS 變成 $O(V^2)$。
*   **Fix:** Always use `collections.deque`.
*   **修正：** 總是使用 `collections.deque`。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Tree (樹)** | **Graph (圖)** | A tree is a connected graph with **no cycles** and $N-1$ edges. A graph can have cycles and disconnected parts. <br> 樹是 **無環** 且有 $N-1$ 條邊的連通圖。圖可以有環和不連通的部分。 |
| **Visited Set** | **Recursion Stack** | `Visited` prevents reprocessing nodes (efficiency/cycles). Recursion stack tracks the current path (backtracking). <br> `Visited` 防止重複處理節點（效率/環）。遞迴堆疊追蹤當前路徑（回溯）。 |
| **Connected** | **Complete** | Connected means there is a path between any two nodes. Complete means there is an edge between *every* pair of nodes. <br> 連通意指任兩節點間皆有路徑。完全意指 *每對* 節點間皆有邊。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (闡述口條框架)
1.  **Clarify Input:** "Is this a directed or undirected graph? Can there be self-loops or parallel edges?"
    **釐清輸入：** 「這是有向圖還是無向圖？會有自環或平行邊嗎？」
2.  **Choose Representation:** "Since $N$ can be large but edges are sparse, I'll use an adjacency list to save space."
    **選擇表示法：** 「由於 $N$ 可能很大但邊很稀疏，我將使用鄰接表來節省空間。」
3.  **State Algorithm:** "I will use BFS because it guarantees finding the shortest path in an unweighted graph."
    **說明演算法：** 「我將使用 BFS，因為它保證在無權圖中找到最短路徑。」

### Whiteboard Strategy (白板策略)
*   **Draw it out:** Draw a small graph (3-4 nodes) with a cycle. Trace your code logic on it manually.
    **畫出來：** 畫一個小的圖（3-4 個節點）並包含一個環。手動在上面追蹤你的程式邏輯。
*   **Corner Cases:** Handle `n=0` or `n=1` explicitly at the start.
    **邊界情況：** 在開始時明確處理 `n=0` 或 `n=1`。

---

## 7. Practice Problems (練習題)

### Easy: Find the Town Judge (LeetCode 997)
*   **Hint:** A graph problem disguised as an array problem. Think about "in-degree" (trusts received) vs "out-degree" (trusts given).
*   **提示：** 偽裝成陣列問題的圖論題。思考「入度」（被信任）與「出度」（信任別人）。
*   **Solution Logic:** The judge has in-degree $N-1$ and out-degree $0$.
*   **解題思路：** 法官的入度為 $N-1$，出度為 $0$。

### Medium: Number of Islands (LeetCode 200)
*   **Hint:** The "Grid" is an implicit graph. Each cell is a node; up/down/left/right are edges.
*   **提示：** 「網格」是隱式的圖。每個格子是節點；上/下/左/右是邊。
*   **Solution Logic:** Iterate through the grid. When you see '1', increment count and trigger BFS/DFS to sink (mark '0') all connected land.
*   **解題思路：** 遍歷網格。當看到 '1' 時，計數加一並觸發 BFS/DFS 將所有相連的陸地沉沒（標記為 '0'）。

### Medium/Hard (Beginner Challenge): Clone Graph (LeetCode 133)
*   **Hint:** You need to copy nodes and edges. How do you ensure you don't create a new copy of a node you've already copied?
*   **提示：** 你需要複製節點和邊。如何確保你不會為已經複製過的節點創建新的副本？
*   **Solution Logic:** Use a Hash Map `old_node -> new_node` to track created copies.
*   **解題思路：** 使用雜湊表 `old_node -> new_node` 來追蹤已建立的副本。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Input:** Did I build the graph correctly? (Directed vs Undirected handling).
    **輸入：** 我建圖建對了嗎？（有向 vs 無向的處理）。
*   [ ] **Loop:** Is the `while` loop condition correct? (`while queue:`).
    **迴圈：** `while` 迴圈條件正確嗎？（`while queue:`）。
*   [ ] **Visited:** Did I add the node to `visited` **before** pushing to queue? (Prevents duplicates in queue).
    **已訪問：** 我是否在推入佇列 **之前** 就將節點加入 `visited`？（防止佇列中出現重複）。
*   [ ] **Complexity:** Is my solution $O(V+E)$? Did I avoid $O(V^2)$ operations inside the loop?
    **複雜度：** 我的解法是 $O(V+E)$ 嗎？我有避免在迴圈內進行 $O(V^2)$ 的操作嗎？

---

## 9. Memory Anchors (記憶錨點)

*   **BFS is like a Ripple (BFS 像漣漪):**
    Imagine throwing a stone in a pond. The waves expand in concentric circles (layers). It hits close things first.
    想像往池塘丟一顆石頭。波紋以同心圓（層）擴散。它會先碰到近的東西。
    $\rightarrow$ **Shortest Path (最短路徑)**.

*   **DFS is like a Maze Runner (DFS 像迷宮跑者):**
    You run down a path until you hit a wall, then you backtrack to the last junction and try a different path.
    你沿著一條路跑直到撞牆，然後回溯到上一個路口並嘗試另一條路。
    $\rightarrow$ **Exhaustive Search (窮舉搜尋)**.