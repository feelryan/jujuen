# Interview Guide: Trees (Intermediate)
# 面試指南：樹（中階）

## 1. Learning Objectives (學習目標)

*   **Master Recursive Thinking (Bottom-up vs. Top-down):**
    Understand when to pass information down to children (parameters) versus when to bubble information up to parents (return values).
    **掌握遞迴思維（自底向上 vs. 自頂向下）：** 理解何時將資訊向下傳遞給子節點（參數），以及何時將資訊向上回傳給父節點（回傳值）。

*   **Differentiate Traversal Strategies:**
    Know exactly when to use DFS (Preorder/Inorder/Postorder) versus BFS (Level Order) based on the problem constraints.
    **區分遍歷策略：** 根據問題限制，清楚知道何時使用 DFS（前序/中序/後序）與 BFS（層序）。

*   **Complexity Analysis for Skewed vs. Balanced Trees:**
    Correctly identify worst-case scenarios ($O(N)$ height) versus best-case scenarios ($O(\log N)$ height).
    **偏斜與平衡樹的複雜度分析：** 正確識別最差情況（$O(N)$ 高度）與最佳情況（$O(\log N)$ 高度）。

*   **Handle Edge Cases & Null Pointers:**
    Develop muscle memory for checking `if not root` to prevent runtime errors.
    **處理邊界情況與空指標：** 建立檢查 `if not root` 的肌肉記憶，以防止執行時期錯誤。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with no cycles.
樹是一種由邊連接節點組成的階層式資料結構，且不包含任何環。

For a Senior Engineer, think of a Tree as a **Recursive Definition**: A tree is a root node where each child is itself a tree (subtree).
對於資深工程師來說，應將樹視為**遞迴定義**：樹是一個根節點，其每個子節點本身也是一棵樹（子樹）。

### Complexity (複雜度)
*   **Time:** Traversal is typically $O(N)$, where $N$ is the number of nodes.
    **時間：** 遍歷通常為 $O(N)$，其中 $N$ 是節點數量。
*   **Space:** Determined by the height of the tree ($H$) due to the call stack.
    **空間：** 由樹的高度 ($H$) 決定，因為需要遞迴呼叫堆疊。
    *   Balanced Tree (平衡樹): $O(\log N)$
    *   Skewed Tree (偏斜樹/鏈狀): $O(N)$

### Use Cases (適用與不適用場景)
*   **Good for:** Hierarchical data (DOM, File Systems), searching (BST), analyzing dependencies.
    **適用於：** 階層式資料（DOM、檔案系統）、搜尋（二元搜尋樹）、分析依賴關係。
*   **Not good for:** Cyclic dependencies (use Graph), simple linear iteration (use Array/LinkedList).
    **不適用於：** 循環依賴（請用圖）、簡單線性迭代（請用陣列/連結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Top-Down DFS (Preorder)
Pass values from the root down to leaves. Used for path sums or validating BSTs.
**自頂向下 DFS（前序）：** 將數值從根節點傳遞至葉節點。用於路徑總和或驗證二元搜尋樹。

### B. Bottom-Up DFS (Postorder)
Gather information from children to compute a result for the parent. Used for calculating height, diameter, or checking balance.
**自底向上 DFS（後序）：** 收集子節點的資訊以計算父節點的結果。用於計算高度、直徑或檢查平衡。

### C. BFS (Level Order Traversal)
Process nodes layer by layer using a `Queue`. Used for finding the shortest path in unweighted graphs or printing structure.
**BFS（層序遍歷）：** 使用 `Queue` 逐層處理節點。用於在無權圖中尋找最短路徑或列印結構。

---

## 4. Example Walkthrough (範例講解)

### Problem: Lowest Common Ancestor of a Binary Tree
### 問題：二元樹的最近公共祖先 (LCA)

**Problem Statement:**
Given a binary tree, find the lowest common ancestor (LCA) of two given nodes `p` and `q`.
**問題重述：** 給定一棵二元樹，找出兩個指定節點 `p` 和 `q` 的最近公共祖先 (LCA)。

> **Definition of LCA:** The lowest node `T` that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).
> **LCA 定義：** 最低層級的節點 `T`，使得 `p` 和 `q` 都是其後代（允許節點是自己的後代）。

---

### Approach: Bottom-Up Recursion (思路：自底向上遞迴)

1.  **Base Case:** If the current node is `None`, return `None`. If the current node is `p` or `q`, return the current node.
    **終止條件：** 如果當前節點為 `None`，回傳 `None`。如果當前節點是 `p` 或 `q`，回傳當前節點。

2.  **Recursive Step:** Recursively search in the left and right subtrees.
    **遞迴步驟：** 在左子樹和右子樹中遞迴搜尋。

3.  **Logic:**
    *   If both left and right calls return a non-null value, it means `p` and `q` are found in different branches. The current node is the LCA.
    *   If only one side returns a value, it means both nodes are in that subtree (or one is the ancestor of the other). Pass that value up.
    *   **邏輯：**
        *   如果左右遞迴呼叫皆回傳非空值，表示 `p` 和 `q` 分別位於不同分支。當前節點即為 LCA。
        *   如果只有一邊回傳值，表示兩個節點都在該子樹中（或其中一個是另一個的祖先）。將該值向上傳遞。

---

### Python Solution (Python 參考解)

```python
from typing import Optional

class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        # Base Case: If root is None, or root matches p or q, return root.
        # 終止條件：如果 root 為空，或 root 等於 p 或 q，回傳 root。
        if not root or root == p or root == q:
            return root
        
        # Recursive Step: Search in left and right subtrees.
        # 遞迴步驟：在左子樹與右子樹中搜尋。
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        
        # Logic 1: If both left and right returned a node, current root is the split point (LCA).
        # 邏輯 1：如果左右兩邊都回傳了節點，當前 root 即為分岔點 (LCA)。
        if left and right:
            return root
        
        # Logic 2: If only one side returned a node, pass it up (found one or both in that subtree).
        # 邏輯 2：如果只有一邊回傳節點，將其向上傳遞（在該子樹中找到一個或兩個）。
        return left if left else right

# Time Complexity: O(N) - We might visit every node in the worst case.
# 時間複雜度：O(N) - 最差情況下我們可能訪問每個節點。

# Space Complexity: O(H) - Recursion stack depth, where H is height of tree.
# 空間複雜度：O(H) - 遞迴堆疊深度，H 為樹的高度。
```

### Common Mistake (錯誤示範)
**Storing Parent Pointers:**
Iterating through the tree to add a `parent` pointer to every node, then treating it as a "Intersection of Two Linked Lists" problem.
**儲存父節點指標：** 遍歷樹並為每個節點增加 `parent` 指標，然後將其視為「兩個連結串列的交點」問題。

*   **Why it's suboptimal:** It requires $O(N)$ extra space for the map/pointers and two passes. The recursive solution is single-pass and uses stack space only.
*   **為何次佳：** 這需要 $O(N)$ 的額外空間來儲存映射/指標，且需要兩次遍歷。遞迴解法只需一次遍歷且僅使用堆疊空間。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Height (高度)** | **Depth (深度)** | Height is bottom-up (leaf to root); Depth is top-down (root to node). <br> 高度是自底向上（葉到根）；深度是自頂向下（根到節點）。 |
| **Binary Tree** | **Binary Search Tree (BST)** | A Binary Tree has no order; BST implies `left < root < right`. <br> 二元樹無順序；BST 隱含 `左 < 根 < 右` 的規則。 |
| **Balanced** | **Symmetric** | Balanced refers to height differences; Symmetric refers to mirror image structure. <br> 平衡指高度差異；對稱指鏡像結構。 |
| **O(N) Space** | **O(H) Space** | Don't say $O(N)$ space for recursion unless it's a skewed tree. Say $O(H)$ to be precise. <br> 除非是偏斜樹，否則不要說遞迴空間是 $O(N)$。精確說法是 $O(H)$。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Clarify:** "Is this a BST or a generic Binary Tree? Can there be duplicate values?"
    **釐清：** 「這是二元搜尋樹還是一般二元樹？會有重複的值嗎？」
2.  **State Approach:** "Since this is a tree structure, I'm thinking of using a recursive DFS approach. Specifically, a post-order traversal to bubble up the results."
    **陳述思路：** 「既然這是樹狀結構，我考慮使用遞迴 DFS 方法。具體來說，使用後序遍歷將結果向上回傳。」
3.  **Address Complexity:** "This will be $O(N)$ time complexity as we visit each node once."
    **說明複雜度：** 「這將是 $O(N)$ 的時間複雜度，因為我們訪問每個節點一次。」

### Whiteboard Strategy (白板策略)
*   **Draw a small tree:** Use a 3-level tree (root, children, grand-children) to trace your code.
    **畫一棵小樹：** 使用 3 層的樹（根、子、孫）來追蹤你的程式碼。
*   **Visualize the Stack:** If you get stuck, write down the "Call Stack" on the side to show you understand recursion depth.
    **視覺化堆疊：** 如果卡住了，在旁邊寫下「呼叫堆疊」以顯示你理解遞迴深度。

### Common Follow-ups (常見追問)
*   "How would you solve this iteratively?" (Hint: Use an explicit `Stack` or `Queue`).
    「你會如何用迭代方式解決？」 （提示：使用顯式的 `Stack` 或 `Queue`）。
*   "What if the tree is too large to fit in memory?" (Hint: Discuss serialization or processing subtrees).
    「如果樹大到記憶體裝不下怎麼辦？」 （提示：討論序列化或分批處理子樹）。

---

## 7. Practice Problems (練習題)

### Level: Easy
**Problem:** Invert Binary Tree (翻轉二元樹)
**Hint:** Swap `left` and `right` children, then recurse.
**提示：** 交換 `left` 和 `right` 子節點，然後遞迴。
**Focus:** Basic manipulation. (基礎操作)

### Level: Medium
**Problem:** Binary Tree Level Order Traversal (二元樹層序遍歷)
**Hint:** Use a `deque` (queue). Process size of queue at start of loop to separate levels.
**提示：** 使用 `deque` (佇列)。在迴圈開始時處理佇列的大小以區分層級。
**Focus:** BFS pattern. (BFS 模式)

### Level: Hard
**Problem:** Binary Tree Maximum Path Sum (二元樹最大路徑和)
**Hint:** Postorder traversal. Return "max gain from one branch" to parent, but update a global "max path sum" considering "left + root + right".
**提示：** 後序遍歷。回傳「單一分支的最大增益」給父節點，但同時考慮「左 + 根 + 右」來更新全域的「最大路徑和」。
**Focus:** State passing vs. Global state update. (狀態傳遞 vs 全域狀態更新)

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Base Case:** Did I handle `if not root`?
    **終止條件：** 我是否處理了 `if not root`？
*   [ ] **Return Value:** Does my recursive function return the correct type (e.g., Node vs. Integer)?
    **回傳值：** 我的遞迴函式是否回傳正確的型別（例如：節點 vs 整數）？
*   [ ] **Null Safety:** Am I accessing `.left` or `.right` on a potentially `None` object?
    **空值安全：** 我是否在可能為 `None` 的物件上存取 `.left` 或 `.right`？
*   [ ] **Complexity:** Did I distinguish between Balanced ($O(\log N)$) and Worst Case ($O(N)$)?
    **複雜度：** 我是否區分了平衡情況 ($O(\log N)$) 與最差情況 ($O(N)$)？

---

## 9. Memory Anchors (記憶錨點)

*   **The "Manager-Delegate" Model (經理-代理人模型):**
    *   **Root (Manager):** Delegates work to `left` and `right` (Subordinates).
    *   **Recursion:** Waiting for reports from subordinates.
    *   **Return:** Aggregating reports to pass to the boss (Parent).
    *   **根（經理）：** 將工作委派給 `left` 和 `right`（下屬）。
    *   **遞迴：** 等待下屬的報告。
    *   **回傳：** 彙整報告並呈交給上司（父節點）。

*   **DFS vs BFS:**
    *   **DFS = Diver:** Dives deep to the bottom first (Stack).
    *   **BFS = Scanner:** Scans horizontally layer by layer (Queue).
    *   **DFS = 潛水員：** 先深入到底部（堆疊）。
    *   **BFS = 掃描器：** 水平逐層掃描（佇列）。