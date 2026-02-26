# Module: Trees (Foundations)
# 模組：樹（基礎篇）

## 1. Learning Objectives (學習目標)

*   **Master Recursive Thinking:** Move beyond simple loops to confidently implement "Divide and Conquer" logic using the system stack.
    **掌握遞迴思維：** 超越簡單的迴圈，自信地利用系統堆疊實作「分治法」邏輯。
*   **Solidify Traversal Patterns:** Internalize DFS (Pre-order, In-order, Post-order) and BFS (Level-order) until they become muscle memory.
    **鞏固遍歷模式：** 內化 DFS（前序、中序、後序）與 BFS（層序），直到它們成為肌肉記憶。
*   **Handle Edge Cases & Null Safety:** Develop a reflex for checking `None` nodes to prevent runtime errors, a critical signal of seniority.
    **處理邊界情況與 Null 安全：** 養成檢查 `None` 節點的反射動作以防止執行期錯誤，這是資深程度的關鍵訊號。
*   **Understand Complexity Nuances:** Distinguish between Balanced Trees ($O(\log N)$ height) and Skewed Trees ($O(N)$ height).
    **理解複雜度細微差別：** 區分平衡樹（高度 $O(\log N)$）與歪斜樹（高度 $O(N)$）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with no cycles, and a single root.
樹是一種由邊連接節點組成的階層式資料結構，沒有迴圈，且只有一個根節點。

### Intuition (直覺)
Think of a Tree as a recursive definition: a Node contains a value and references to children (subtrees), which are themselves Trees.
將樹視為一種遞迴定義：一個節點包含一個數值以及指向子節點（子樹）的參照，而子樹本身也是樹。

### Complexity (複雜度)
*   **Time:** Most operations visit every node once, so $O(N)$.
    **時間：** 大多數操作會訪問每個節點一次，因此為 $O(N)$。
*   **Space:** Determined by the height of the tree ($H$) due to the recursion stack.
    **空間：** 由樹的高度（$H$）決定，因為需要遞迴堆疊。
    *   Balanced (平衡): $O(\log N)$
    *   Skewed (歪斜/最差情況): $O(N)$

### When to Use (適用場景)
*   Representing hierarchical data (File systems, DOM, Organizational charts).
    表示階層式資料（檔案系統、DOM、組織圖）。
*   Fast search/insert/delete operations (BST, Tries, Heaps).
    快速搜尋/插入/刪除操作（二元搜尋樹、Trie、堆積）。

### When NOT to Use (不適用場景)
*   Data with cyclic dependencies (Use a Graph).
    具有循環依賴的資料（請使用圖）。
*   Simple linear access patterns (Use Array or Linked List).
    簡單的線性存取模式（請使用陣列或連結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner level, focus on these three fundamental patterns:
針對初階程度，請專注於這三種基礎模式：

1.  **Top-Down DFS (Pre-order):**
    **由上而下 DFS（前序）：**
    Process the current node, then pass values down to children.
    處理當前節點，然後將數值向下傳遞給子節點。
    *(Usage: Path sums, printing hierarchy)*

2.  **Bottom-Up DFS (Post-order):**
    **由下而上 DFS（後序）：**
    Recursively call children first, aggregate their results, and return to the parent.
    先遞迴呼叫子節點，聚合它們的結果，然後返回給父節點。
    *(Usage: Height calculation, subtree validation)*

3.  **Breadth-First Search (Level-order):**
    **廣度優先搜尋（層序）：**
    Process nodes layer by layer using a Queue.
    使用佇列（Queue）逐層處理節點。
    *(Usage: Shortest path in unweighted graphs, level-based logic)*

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Depth of Binary Tree
### 問題：二元樹的最大深度

**Problem Statement:**
Given the root of a binary tree, return its maximum depth.
給定二元樹的根節點，回傳其最大深度。
A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.
二元樹的最大深度是從根節點到最遠葉子節點的最長路徑上的節點數量。

### Approach 1: Bottom-Up Recursion (DFS) - Recommended
### 思路 1：由下而上遞迴（DFS）— 推薦

**Logic:**
1.  **Base Case:** If the node is `None`, depth is 0.
    **基本情況：** 如果節點為 `None`，深度為 0。
2.  **Recursive Step:** Ask the left child for its depth and the right child for its depth.
    **遞迴步驟：** 詢問左子節點的深度與右子節點的深度。
3.  **Combine:** The depth of the current node is `max(left, right) + 1`.
    **合併：** 當前節點的深度為 `max(左, 右) + 1`。

**Complexity:**
*   Time: $O(N)$ (We visit every node).
*   Space: $O(H)$ (Stack depth).

### Python Solution (Reference)

```python
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        # Base case: if the tree is empty, depth is 0
        # 基本情況：如果樹是空的，深度為 0
        if not root:
            return 0
        
        # Recursively find the depth of left and right subtrees
        # 遞迴地尋找左子樹和右子樹的深度
        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        
        # The depth of current node is max of children + 1 (for self)
        # 當前節點的深度是子節點最大值 + 1（加上自己）
        return max(left_depth, right_depth) + 1

    # Alternative: Iterative BFS (Level Order)
    # 替代方案：迭代 BFS（層序遍歷）
    # Useful to demonstrate knowledge of Queues and avoiding stack overflow
    # 用於展示對 Queue 的了解並避免堆疊溢位
    def maxDepthIterative(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        
        from collections import deque
        queue = deque([root])
        depth = 0
        
        while queue:
            depth += 1
            # Process all nodes at the current level
            # 處理當前層級的所有節點
            level_size = len(queue)
            for _ in range(level_size):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        
        return depth
```

### Common Mistakes (錯誤示範)

**Mistake:** Forgetting the `+ 1` in the return statement.
**錯誤：** 在回傳語句中忘記 `+ 1`。
*Why it's wrong:* You count the children's depth but forget to count the current node itself.
*為何錯：* 你計算了子節點的深度，卻忘了計算當前節點本身。

**Mistake:** Using a global variable for depth without resetting it.
**錯誤：** 使用全域變數紀錄深度但未重置。
*Why it's wrong:* Not thread-safe and fails if the class instance is reused for multiple test cases.
*為何錯：* 非執行緒安全，且若類別實例被重複用於多個測試案例時會失敗。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Depth (深度)** | **Height (高度)** | **Depth** is distance from Root (Root is 0 or 1). **Height** is distance from Leaf (Leaf is 0). <br> **深度**是離根的距離；**高度**是離葉子的距離。 |
| **Binary Tree** | **Binary Search Tree (BST)** | A Binary Tree has no order. A **BST** implies `Left < Node < Right`. <br> 二元樹無順序；**BST** 隱含 `左 < 節點 < 右` 的規則。 |
| **Balanced Tree** | **Complete Tree** | **Balanced**: Height is minimized ($O(\log N)$). **Complete**: Filled level by level, left to right. <br> **平衡**：高度最小化；**完全**：逐層從左至右填滿。 |

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **State the Traversal:** "Since this is a tree problem requiring information from subtrees, I will use a **Post-order DFS** (Bottom-up approach)."
    **說明遍歷方式：** 「由於這是一個需要子樹資訊的樹問題，我將使用 **後序 DFS**（由下而上法）。」
2.  **Define Base Case:** "The recursion terminates when we hit a `None` node, returning 0/False/Null."
    **定義基本情況：** 「當遇到 `None` 節點時遞迴終止，回傳 0/False/Null。」
3.  **Address Complexity:** "Time complexity is $O(N)$ as we visit each node. Space is $O(H)$ for the stack."
    **說明複雜度：** 「時間複雜度為 $O(N)$，因為我們訪問每個節點。空間為 $O(H)$ 用於堆疊。」

### Whiteboard Strategy (白板策略)
*   **Draw a small tree:** A root, two children, and one grandchild. This covers depth 1, 2, and 3.
    **畫一棵小樹：** 一個根，兩個子節點，一個孫節點。這涵蓋了深度 1、2 和 3。
*   **Trace the recursion:** Use indentation or a stack diagram on the side to show you understand how the OS handles recursion.
    **追蹤遞迴：** 在旁邊使用縮排或堆疊圖，顯示你理解作業系統如何處理遞迴。

### Common Follow-ups (常見追問)
*   "What if the tree is very deep (skewed) and causes a Stack Overflow?"
    「如果樹非常深（歪斜）導致堆疊溢位怎麼辦？」
    *   *Answer:* Switch to **Iterative DFS** (using an explicit stack) or **BFS** (if the problem allows level-order processing).
    *   *回答：* 改用 **迭代 DFS**（使用顯式堆疊）或 **BFS**（如果問題允許層序處理）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Invert Binary Tree (翻轉二元樹)
*   **Prompt:** Swap left and right children for every node.
    **題目：** 交換每個節點的左右子節點。
*   **Hint:** Post-order traversal. Invert left, invert right, then swap `self.left` and `self.right`.
    **提示：** 後序遍歷。翻轉左邊，翻轉右邊，然後交換 `self.left` 和 `self.right`。

### 2. Medium: Validate Binary Search Tree (驗證二元搜尋樹)
*   **Prompt:** Check if a tree satisfies the BST property (Left < Node < Right) for *all* descendants.
    **題目：** 檢查樹是否對*所有*後代滿足 BST 屬性（左 < 節點 < 右）。
*   **Hint:** Pass down a range `(min_val, max_val)` to children. Root is `(-inf, inf)`. Left child must be `(parent_min, parent_val)`.
    **提示：** 將範圍 `(min_val, max_val)` 向下傳遞給子節點。根是 `(-inf, inf)`。左子節點必須在 `(parent_min, parent_val)` 之間。

### 3. Medium/Hard: Lowest Common Ancestor (最近共同祖先)
*   **Prompt:** Find the lowest node that has both `p` and `q` as descendants.
    **題目：** 尋找最低的節點，使其同時擁有 `p` 和 `q` 作為後代。
*   **Hint:** If `root` is `p` or `q`, return `root`. If `left` and `right` both return a node, `root` is the LCA.
    **提示：** 如果 `root` 是 `p` 或 `q`，回傳 `root`。如果 `left` 和 `right` 都回傳了節點，則 `root` 是 LCA。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] Did I handle the `root is None` case immediately?
      我是否立即處理了 `root is None` 的情況？
- [ ] Are my recursive calls actually converging towards the base case (calling on `node.left`/`node.right`)?
      我的遞迴呼叫是否真的收斂向基本情況（呼叫 `node.left`/`node.right`）？
- [ ] Did I return the result of the recursion? (Common bug: calling `self.dfs(root.left)` without `return` or assignment).
      我是否回傳了遞迴的結果？（常見 Bug：呼叫 `self.dfs(root.left)` 卻沒有 `return` 或賦值）。

### Complexity Check (複雜度確認)
- [ ] **Time:** Is it $O(N)$? Do I visit nodes more than once unnecessarily?
      **時間：** 是 $O(N)$ 嗎？我是否不必要地多次訪問節點？
- [ ] **Space:** Did I mention $O(H)$ instead of just $O(N)$? (Shows depth of understanding).
      **空間：** 我是否提到了 $O(H)$ 而不僅僅是 $O(N)$？（顯示理解深度）。

---

## 9. Memory Anchors (記憶錨點)

*   **Russian Nesting Dolls (Matryoshka):**
    **俄羅斯套娃：**
    Solving a tree problem is like opening a doll. You do the same operation on the smaller doll inside until you reach the smallest solid one (Base Case).
    解決樹的問題就像打開套娃。你在裡面的小娃娃上做同樣的操作，直到到達最小的實心娃娃（基本情況）。

*   **Corporate Hierarchy:**
    **公司層級：**
    **Pre-order:** CEO gives an order, it trickles down to managers, then interns.
    **前序：** CEO 下達命令，傳給經理，再傳給實習生。
    **Post-order:** Interns do work, report to managers, managers aggregate and report to CEO.
    **後序：** 實習生做工作，回報給經理，經理彙整後回報給 CEO。