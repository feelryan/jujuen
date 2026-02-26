# Module: Trees (Intermediate)
# 模組：樹（中階）

## 1. Learning Objectives (學習目標)

1.  **Master Recursive Thinking & State Management:**
    掌握遞迴思維與狀態管理：
    Understand how to pass state down (parameters) and bubble results up (return values) effectively.
    理解如何有效地向下傳遞狀態（參數）並向上回傳結果（返回值）。

2.  **Differentiate Traversal Patterns (DFS vs. BFS):**
    區分遍歷模式（深度優先 vs. 廣度優先）：
    Know when to use Pre-order, In-order, Post-order, or Level-order traversal based on the problem requirements.
    根據問題需求，知道何時使用前序、中序、後序或層序遍歷。

3.  **Analyze Complexity with Edge Cases:**
    分析複雜度與邊界情況：
    Articulate the difference between balanced trees ($O(\log N)$ height) and skewed trees ($O(N)$ height).
    清楚闡述平衡樹（高度 $O(\log N)$）與歪斜樹（高度 $O(N)$）之間的差異。

4.  **Transition from Recursive to Iterative:**
    從遞迴轉換為迭代：
    Be able to implement traversals using an explicit Stack or Queue to avoid stack overflow in production environments.
    能夠使用顯式堆疊（Stack）或佇列（Queue）實作遍歷，以避免生產環境中的堆疊溢位。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition (定義)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with a single root node and no cycles.
樹是一種由節點與邊連接而成的階層式資料結構，擁有單一根節點且無迴圈。

### Intuition (直覺)
Think of a Tree as a recursive definition: a Node contains a value and references to children (subtrees).
將樹視為遞迴定義：一個節點包含數值以及對子節點（子樹）的參照。
Most tree problems are solved by solving the problem for the subtrees and combining the results.
大多數樹的問題都是透過解決子樹的問題，並合併結果來解決的。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$ to visit every node.
    **時間：** 通常為 $O(N)$ 以訪問每個節點。
*   **Space:** $O(H)$ for recursion stack, where $H$ is height.
    **空間：** 遞迴堆疊為 $O(H)$，其中 $H$ 為樹高。
    *   Best/Average (Balanced): $O(\log N)$.
        最佳/平均（平衡）：$O(\log N)$。
    *   Worst (Skewed/LinkedList-like): $O(N)$.
        最差（歪斜/類鏈結串列）：$O(N)$。

### When to Use (適用場景)
*   Hierarchical data (File systems, DOM, Organizational charts).
    階層式資料（檔案系統、DOM、組織圖）。
*   Fast search and sorting (Binary Search Trees, Heaps).
    快速搜尋與排序（二元搜尋樹、堆積）。
*   Routing algorithms and decision processes.
    路由演算法與決策過程。

### When NOT to Use (不適用場景)
*   Data with cycles or many-to-many relationships (Use Graphs).
    具有迴圈或多對多關係的資料（使用圖）。
*   Simple linear access requirements (Use Arrays or Linked Lists).
    簡單的線性存取需求（使用陣列或鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. DFS (Depth-First Search) - The "Recursion" Standard
**DFS（深度優先搜尋）——「遞迴」標準**
*   **Pre-order (Root-Left-Right):** Copying trees, prefix expression.
    **前序（根-左-右）：** 複製樹、前綴表達式。
*   **In-order (Left-Root-Right):** BST validation, sorted output.
    **中序（左-根-右）：** BST 驗證、排序輸出。
*   **Post-order (Left-Right-Root):** Deleting trees, bottom-up calculations (e.g., height, diameter).
    **後序（左-右-根）：** 刪除樹、由下而上的計算（如高度、直徑）。

### B. BFS (Breadth-First Search) - Level Order
**BFS（廣度優先搜尋）—— 層序**
*   Uses a `Queue`. Good for finding the "shortest path" in unweighted graphs/trees or processing level-by-level.
    使用 `Queue`。適合尋找無權圖/樹中的「最短路徑」或逐層處理。

### C. Top-down vs. Bottom-up
**由上而下 vs. 由下而上**
*   **Top-down:** Pass values (like `max_so_far` or `path_sum`) as arguments to children.
    **由上而下：** 將數值（如 `max_so_far` 或 `path_sum`）作為參數傳遞給子節點。
*   **Bottom-up:** Gather values from children (like `subtree_height`) to compute the current node's state.
    **由下而上：** 從子節點收集數值（如 `subtree_height`）以計算當前節點的狀態。

---

## 4. Example Walkthrough (範例講解)

### Problem: Lowest Common Ancestor (LCA) of a Binary Tree
**題目：二元樹的最近共同祖先**

### Problem Statement (問題重述)
Given a binary tree, find the lowest common ancestor (LCA) of two given nodes `p` and `q`.
給定一棵二元樹，找出兩個指定節點 `p` 和 `q` 的最近共同祖先（LCA）。
The LCA is defined as the lowest node `T` that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).
LCA 定義為最低的節點 `T`，使得 `p` 和 `q` 均為其後代（允許節點為其自身的後代）。

### Thought Process (思路)

1.  **Brute Force (暴力法):**
    Store the path from root to `p` and root to `q` in two lists.
    將從根到 `p` 和從根到 `q` 的路徑儲存在兩個列表中。
    Iterate through the lists to find the last common node.
    遍歷這兩個列表以找到最後一個共同節點。
    *Complexity:* Time $O(N)$, Space $O(N)$ (for storing paths).
    *複雜度：* 時間 $O(N)$，空間 $O(N)$（用於儲存路徑）。

2.  **Optimization (Recursive/Bottom-up) (優化 - 遞迴/由下而上):**
    We can solve this in a single traversal.
    我們可以透過單次遍歷解決此問題。
    For any node, if it is `p` or `q`, we return it.
    對於任何節點，如果它是 `p` 或 `q`，我們就回傳它。
    Otherwise, we search left and right.
    否則，我們搜尋左邊和右邊。
    *   If both left and right return a non-null value, it means `p` and `q` are in different subtrees, so the current node is the LCA.
        如果左邊和右邊都回傳非空值，表示 `p` 和 `q` 分別在不同的子樹中，因此當前節點即為 LCA。
    *   If only one side returns a value, pass that value up (the LCA is strictly in that subtree).
        如果只有一邊回傳數值，則向上傳遞該數值（LCA 嚴格位於該子樹中）。

### TypeScript Solution (TypeScript 參考解)

```typescript
// Definition for a binary tree node.
class TreeNode {
    val: number;
    left: TreeNode | null;
    right: TreeNode | null;
    constructor(val?: number, left?: TreeNode | null, right?: TreeNode | null) {
        this.val = (val === undefined ? 0 : val);
        this.left = (left === undefined ? null : left);
        this.right = (right === undefined ? null : right);
    }
}

/**
 * Finds the Lowest Common Ancestor of two nodes.
 * 尋找兩個節點的最近共同祖先。
 * 
 * Time Complexity: O(N) - We might visit every node in the worst case.
 * 時間複雜度：O(N) - 最壞情況下我們可能訪問每個節點。
 * Space Complexity: O(H) - Recursion stack height.
 * 空間複雜度：O(H) - 遞迴堆疊高度。
 */
function lowestCommonAncestor(root: TreeNode | null, p: TreeNode | null, q: TreeNode | null): TreeNode | null {
    // 1. Base Case: If root is null, or root is one of the targets, return root.
    // 1. 基本情況：如果根為空，或根是目標之一，回傳根。
    if (root === null || root === p || root === q) {
        return root;
    }

    // 2. Recursive Step: Search in left and right subtrees.
    // 2. 遞迴步驟：在左子樹與右子樹中搜尋。
    const left = lowestCommonAncestor(root.left, p, q);
    const right = lowestCommonAncestor(root.right, p, q);

    // 3. Logic: If both sides returned something, current node is the split point (LCA).
    // 3. 邏輯：如果兩邊都回傳了東西，當前節點即為分歧點（LCA）。
    if (left !== null && right !== null) {
        return root;
    }

    // 4. If only one side returned something, propagate it up.
    // 4. 如果只有一邊回傳了東西，將其向上傳遞。
    // If both are null, this returns null.
    // 如果兩者皆為空，這裡會回傳 null。
    return left !== null ? left : right;
}
```

### Common Mistake (錯誤示範)
*   **Mistake:** Assuming it's a Binary Search Tree (BST) and trying to compare values (`root.val > p.val`) to decide direction.
    **錯誤：** 假設這是二元搜尋樹（BST）並試圖比較數值（`root.val > p.val`）來決定方向。
*   **Why:** The problem states "Binary Tree", not "BST". The nodes are not sorted.
    **原因：** 題目說明是「二元樹」，而非「BST」。節點並未排序。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Binary Tree** | **Binary Search Tree (BST)** | BT is structural only; BST implies ordered data (Left < Node < Right). <br> BT 僅具結構性；BST 隱含排序資料（左 < 節點 < 右）。 |
| **Balanced Tree** | **Complete Tree** | Balanced means height is $O(\log N)$; Complete means filled level-by-level (left-to-right). <br> 平衡意指高度為 $O(\log N)$；完全意指逐層填滿（由左至右）。 |
| **Node Depth** | **Node Height** | Depth is edges from Root (Top-down); Height is edges to deepest Leaf (Bottom-up). <br> 深度是從根算起的邊數（由上而下）；高度是到最深葉子的邊數（由下而上）。 |
| **O(N) Space** | **O(H) Space** | In recursion, space is proportional to Height, not necessarily Node count (unless skewed). <br> 在遞迴中，空間與高度成正比，不一定與節點數成正比（除非歪斜）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Input:** "Is this a BST or a generic Binary Tree? Can nodes have duplicate values?"
    **釐清輸入：** 「這是 BST 還是普通二元樹？節點會有重複值嗎？」
2.  **State Traversal:** "I will use a post-order traversal because I need information from the children before processing the parent."
    **說明遍歷：** 「我將使用後序遍歷，因為我在處理父節點之前需要來自子節點的資訊。」
3.  **Address Stack Overflow:** "For production code, I would consider an iterative approach to avoid stack overflow on very deep trees."
    **提及堆疊溢位：** 「對於生產環境程式碼，我會考慮迭代解法，以避免在極深的樹上發生堆疊溢位。」

### Whiteboard Strategy (白板策略)
*   **Draw a "Messy" Tree:** Don't draw a perfect triangle. Draw a lopsided tree to remind yourself of the $O(N)$ height worst case.
    **畫一棵「亂」的樹：** 不要畫完美的三角形。畫一棵歪斜的樹來提醒自己 $O(N)$ 高度的最壞情況。
*   **Trace Recursion:** Use indentation or a small stack diagram on the side to show you understand how the recursion unwinds.
    **追蹤遞迴：** 使用縮排或在旁邊畫一個小堆疊圖，以顯示你理解遞迴如何展開。

### Common Follow-ups (常見追問)
*   "How would you solve this iteratively?" (Prepare Stack/Queue implementations).
    「你會如何用迭代方式解決此問題？」（準備 Stack/Queue 的實作）。
*   "What if the tree is too large to fit in memory?" (Discuss serialization or processing chunks).
    「如果樹大到無法放入記憶體怎麼辦？」（討論序列化或分塊處理）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Invert Binary Tree
**簡單：翻轉二元樹**
*   *Hint:* Swap left and right children, then recurse.
    *提示：* 交換左右子節點，然後遞迴。
*   *Focus:* Basic manipulation.
    *重點：* 基本操作。

### 2. Medium: Binary Tree Right Side View
**中等：二元樹的右側視圖**
*   *Hint:* Use BFS (Level Order). The last element in each level's queue is visible from the right.
    *提示：* 使用 BFS（層序）。每層佇列中的最後一個元素即為右側可見元素。
*   *Focus:* BFS and level tracking.
    *重點：* BFS 與層級追蹤。

### 3. Hard: Serialize and Deserialize Binary Tree
**困難：二元樹的序列化與反序列化**
*   *Hint:* Use Pre-order traversal with a marker (e.g., `#` or `null`) for null pointers to preserve structure uniquely.
    *提示：* 使用帶有標記（如 `#` 或 `null`）的前序遍歷來表示空指標，以唯一地保留結構。
*   *Focus:* System design thinking, string parsing, and reconstructing trees.
    *重點：* 系統設計思維、字串解析與重建樹。

---

## 8. Quick Checklist (快速檢核表)

*   [ ] **Base Case:** Did I handle `root === null`?
    **基本情況：** 我是否處理了 `root === null`？
*   [ ] **Leaf Nodes:** Does the logic hold for leaf nodes (both children null)?
    **葉節點：** 邏輯是否適用於葉節點（左右子節點皆空）？
*   [ ] **Return Value:** Am I returning the correct type (Node vs. Boolean vs. Number)?
    **返回值：** 我是否回傳了正確的型別（節點 vs. 布林值 vs. 數字）？
*   [ ] **State Passing:** Should `current_sum` be a parameter or a return value?
    **狀態傳遞：** `current_sum` 應該是參數還是返回值？
*   [ ] **Complexity:** Did I mention $O(H)$ vs $O(N)$ for space?
    **複雜度：** 我是否提到了空間複雜度是 $O(H)$ 還是 $O(N)$？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Russian Dolls" (Recursion)
**「俄羅斯娃娃」（遞迴）**
Opening a doll (calling function) reveals a smaller version of the same doll (sub-problem). You must reach the smallest solid doll (base case) before you can put them all back together (return).
打開娃娃（呼叫函式）會露出同一個娃娃的縮小版（子問題）。你必須到達最小的實心娃娃（基本情況），才能將它們全部組裝回去（回傳）。

### The "Maze Runner" (DFS) vs. "Water Ripple" (BFS)
**「迷宮跑者」（DFS） vs. 「水波紋」（BFS）**
*   **DFS:** A runner who touches the wall with one hand, going as deep as possible into a dead-end before backtracking.
    **DFS：** 一個手扶著牆的跑者，盡可能深入死胡同，然後才折返。
*   **BFS:** Dropping a stone in a pond. The ripples expand uniformly in all directions (levels) at the same time.
    **BFS：** 往池塘丟一顆石頭。漣漪同時向所有方向（層級）均勻擴散。