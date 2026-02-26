# Advanced Trees: Mastery & Interview Strategy
# 進階樹結構：精通與面試策略

## 1. Learning Objectives (學習目標)

*   **Master Tree Dynamic Programming (Tree DP):** Learn how to pass information bottom-up to solve optimization problems (e.g., Maximum Path Sum).
    **掌握樹形動態規劃（Tree DP）：** 學習如何由下而上傳遞資訊以解決最佳化問題（例如：最大路徑和）。
*   **Deep Dive into Serialization:** Understand how to flatten and reconstruct trees, a bridge between algorithms and system design.
    **深入序列化與反序列化：** 理解如何扁平化並重建樹結構，這是演算法與系統設計之間的橋樑。
*   **Space Optimization (Morris Traversal):** Learn to traverse trees in $O(1)$ space without a stack, a common "follow-up" for senior roles.
    **空間最佳化（Morris 遍歷）：** 學習如何在不使用堆疊的情況下以 $O(1)$ 空間遍歷樹，這是資深職位常見的「進階追問」。
*   **Handling Complex State:** Manage global vs. local state during recursion to avoid common bugs in path-finding problems.
    **處理複雜狀態：** 在遞迴過程中管理全域與區域狀態，以避免路徑搜尋問題中常見的錯誤。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a connected, acyclic undirected graph with $N$ nodes and $N-1$ edges.
樹是一個由 $N$ 個節點與 $N-1$ 條邊組成的連通無環無向圖。

For Senior Engineers, treat Trees as a **recursive structure for decision making or hierarchy representation**.
對於資深工程師而言，應將樹視為**決策制定或階層表示的遞迴結構**。

### Complexity (複雜度)
*   **Time:** Usually $O(N)$ as we visit every node.
    **時間：** 通常為 $O(N)$，因為我們訪問每個節點。
*   **Space:** $O(H)$ where $H$ is height. Best case $\log N$ (balanced), worst case $N$ (skewed).
    **空間：** $O(H)$，其中 $H$ 為高度。最佳情況 $\log N$（平衡），最差情況 $N$（歪斜）。

### When to Use (適用場景)
*   Hierarchical data (File systems, DOM, Org charts).
    階層式資料（檔案系統、DOM、組織圖）。
*   Fast lookup/insertion requirements (BST, Tries).
    需要快速查找/插入的需求（二元搜尋樹、Trie）。
*   Syntax analysis (Abstract Syntax Trees).
    語法分析（抽象語法樹）。

### When NOT to Use (不適用場景)
*   Data with cycles (Use Graph algorithms).
    具有環狀結構的資料（請使用圖演算法）。
*   Simple linear access patterns (Use Arrays/Linked Lists).
    簡單的線性存取模式（請使用陣列/鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Bottom-Up DFS (Post-order Traversal)
**Pattern:** Process children first, then pass specific data (height, max path, is_balanced) up to the parent.
**模式：** 先處理子節點，然後將特定資料（高度、最大路徑、是否平衡）向傳遞給父節點。
**Application:** Diameter of Tree, Max Path Sum, Check Balanced.
**應用：** 樹的直徑、最大路徑和、檢查平衡。

### B. Top-Down DFS (Pre-order Traversal)
**Pattern:** Pass constraints or path history from parent to children.
**模式：** 將限制條件或路徑歷史從父節點傳遞給子節點。
**Application:** Validate BST (passing min/max range), Path Sum (root to leaf).
**應用：** 驗證 BST（傳遞最小/最大範圍）、路徑和（根到葉）。

### C. Level-Order Traversal (BFS)
**Pattern:** Use a `deque` to process nodes layer by layer.
**模式：** 使用 `deque` 逐層處理節點。
**Application:** Right side view, Zigzag traversal, Shortest path in unweighted graphs.
**應用：** 右側視圖、鋸齒狀遍歷、無權圖的最短路徑。

### D. Structure Modification
**Pattern:** Re-linking pointers to change structure.
**模式：** 重新連結指標以改變結構。
**Application:** Flatten Binary Tree to Linked List, Invert Tree, Trim BST.
**應用：** 將二元樹扁平化為鏈結串列、翻轉樹、修剪 BST。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Tree Maximum Path Sum (Hard)
### 問題：二元樹中的最大路徑和（困難）

**Problem Statement:**
Given the `root` of a binary tree, return the *maximum path sum* of any non-empty path.
給定二元樹的 `root`，返回任意非空路徑的*最大路徑和*。
A path does not need to pass through the root.
路徑不需要經過根節點。

**Example:**
Input: `[-10, 9, 20, null, null, 15, 7]`
Output: `42` (Path: 15 -> 20 -> 7)

---

### Approach 1: Brute Force (Not Recommended)
### 思路 1：暴力法（不推薦）
Calculate the max path sum starting from *every* node and extending downwards, then consider paths crossing through nodes. This is inefficient ($O(N^2)$).
計算從*每個*節點開始並向下延伸的最大路徑和，然後考慮穿過節點的路徑。這很低效（$O(N^2)$）。

### Approach 2: Optimized Tree DP (Bottom-Up)
### 思路 2：優化樹形動態規劃（由下而上）

**Intuition:**
For any node `u`, the max path *through* `u` (as the turning point) is:
對於任意節點 `u`，*穿過* `u`（作為轉折點）的最大路徑為：
`u.val + max(left_gain, 0) + max(right_gain, 0)`

However, to its parent, `u` can only contribute one single path (either left or right side extension).
然而，對於它的父節點，`u` 只能貢獻一條單一路徑（向左或向右延伸）。
Return to parent: `u.val + max(left_gain, right_gain, 0)`

**Algorithm:**
1.  Initialize a global `max_sum` to negative infinity.
    初始化全域變數 `max_sum` 為負無窮大。
2.  Use DFS (Post-order).
    使用 DFS（後序遍歷）。
3.  Base case: if node is null, return 0.
    基本情況：如果節點為空，返回 0。
4.  Recursive step: Get max gain from left and right subtrees. **Important:** Ignore negative gains (treat as 0).
    遞迴步驟：獲取左子樹和右子樹的最大增益。**重要：** 忽略負增益（視為 0）。
5.  Update global `max_sum` with the path *crossing* the current node.
    使用*穿過*當前節點的路徑更新全域 `max_sum`。
6.  Return the max single path extending from this node to the parent.
    返回從此節點延伸至父節點的最大單一路徑。

### Python Solution (Reference)
### Python 參考解

```python
import sys
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        # Initialize with the smallest possible integer
        # 初始化為最小可能的整數
        self.max_sum = -float('inf')
        
        def get_max_gain(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            
            # Recursive call: calculate max gain from left and right subtrees
            # 遞迴呼叫：計算左右子樹的最大增益
            # Use max(..., 0) to ignore negative paths (we can choose not to include them)
            # 使用 max(..., 0) 來忽略負路徑（我們可以選擇不包含它們）
            left_gain = max(get_max_gain(node.left), 0)
            right_gain = max(get_max_gain(node.right), 0)
            
            # Calculate the price of the new path crossing the current node
            # 計算穿過當前節點的新路徑價值
            current_path_price = node.val + left_gain + right_gain
            
            # Update global maximum if current path is better
            # 如果當前路徑更好，更新全域最大值
            self.max_sum = max(self.max_sum, current_path_price)
            
            # Return max gain to the parent (can only choose one side)
            # 返回最大增益給父節點（只能選擇一邊）
            return node.val + max(left_gain, right_gain)
        
        get_max_gain(root)
        return int(self.max_sum)
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. We visit each node exactly once.
    **時間：** $O(N)$。我們確切地訪問每個節點一次。
*   **Space:** $O(H)$. Recursive stack depth depends on tree height.
    **空間：** $O(H)$。遞迴堆疊深度取決於樹的高度。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Path Sum (Root-to-Leaf)** | **Max Path Sum (Any-to-Any)** | Root-to-leaf is Top-Down (Pre-order). Any-to-Any is usually Bottom-Up (Post-order) with a global max. <br> 根到葉是上而下（前序）。任意點對任意點通常是下而上（後序）並搭配全域最大值。 |
| **Tree Depth** | **Tree Height** | Depth is distance from Root (Top-down). Height is distance from Leaf (Bottom-up). <br> 深度是距離根節點的距離（上而下）。高度是距離葉節點的距離（下而上）。 |
| **Binary Tree** | **Binary Search Tree (BST)** | BST implies strict ordering (`left < root < right`). A regular Binary Tree has no ordering. <br> BST 意味著嚴格的排序（`左 < 根 < 右`）。一般的二元樹沒有排序。 |
| **BFS (Queue)** | **DFS (Stack/Recursion)** | BFS finds shortest path in unweighted graphs (layers). DFS is better for exhaustive search or connectivity. <br> BFS 尋找無權圖中的最短路徑（層級）。DFS 較適合窮舉搜尋或連通性問題。 |

**Critical Mistake:** Forgetting to handle negative values in path sums.
**關鍵錯誤：** 在路徑和問題中忘記處理負值。
*   *Wrong:* `left_gain = get_max_gain(node.left)`
*   *Right:* `left_gain = max(get_max_gain(node.left), 0)`

---

## 6. Interview Strategy (面試實戰建議)

### A. Clarification Framework (釐清框架)
Before coding, ask:
在寫程式碼之前，請問：
1.  **Node Values:** Can they be negative? Are they integers or floats?
    **節點數值：** 可以是負數嗎？是整數還是浮點數？
2.  **Structure:** Is it a BST? Is it balanced? Can it be `null`?
    **結構：** 是 BST 嗎？是平衡的嗎？可以是 `null` 嗎？
3.  **Output:** Do you need the value (sum) or the path itself (list of nodes)?
    **輸出：** 需要數值（總和）還是路徑本身（節點列表）？

### B. Whiteboard Strategy (白板策略)
*   **Draw a messy tree:** Don't just draw a perfect triangle. Draw a skewed tree to test edge cases visually.
    **畫一棵雜亂的樹：** 不要只畫完美的三角形。畫一棵歪斜的樹來視覺化測試邊界情況。
*   **Define the Recursion Signature:** Write down exactly what your recursive function takes and returns *before* implementing logic.
    **定義遞迴簽章：** 在實作邏輯*之前*，寫下遞迴函數接收什麼參數以及返回什麼。
    *   *Example:* "My helper function returns the max single-path sum extending downwards from the current node."
    *   *範例：* 「我的輔助函數返回從當前節點向下延伸的最大單一路徑和。」

### C. Follow-up Handling (追問處理)
*   **"Can you do this iteratively?"**
    **「你能用迭代方式做嗎？」**
    *   Mention using a Stack to simulate recursion. For post-order iterative, it's tricky (requires two stacks or a `last_visited` pointer).
    *   提及使用堆疊來模擬遞迴。對於後序迭代，這比較棘手（需要兩個堆疊或一個 `last_visited` 指標）。
*   **"What if the tree is too large for memory?"**
    **「如果樹太大導致記憶體不足怎麼辦？」**
    *   Discuss **Morris Traversal** for $O(1)$ space (modifies tree structure temporarily).
    *   討論 **Morris 遍歷** 以達到 $O(1)$ 空間（暫時修改樹結構）。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Diameter of Binary Tree** (LeetCode 543)
**Hint:** Very similar to Max Path Sum. The diameter passing through a node is `height(left) + height(right)`.
**提示：** 與最大路徑和非常相似。穿過節點的直徑是 `height(left) + height(right)`。

### Level: Medium (Standard)
**Problem:** **Serialize and Deserialize Binary Tree** (LeetCode 297)
**Hint:** Use Pre-order traversal (DFS) for simplicity. Store `None` as a special character (e.g., "#").
**提示：** 為了簡單起見，使用前序遍歷（DFS）。將 `None` 儲存為特殊字元（例如 "#"）。
**Key Concept:** Reconstructing a tree uniquely requires handling null pointers explicitly.
**關鍵觀念：** 唯一地重建一棵樹需要明確處理空指標。

### Level: Hard (Differentiation)
**Problem:** **Recover Binary Search Tree** (LeetCode 99)
**Hint:** Two nodes were swapped by mistake. Perform an **In-order traversal**. In a valid BST, in-order values should be sorted. Find the two anomalies where `prev.val > current.val`.
**提示：** 兩個節點被錯誤交換了。執行 **中序遍歷**。在有效的 BST 中，中序數值應該是排序好的。找出 `prev.val > current.val` 的兩個異常點。
**Challenge:** Can you do it in $O(1)$ space using Morris Traversal?
**挑戰：** 你能使用 Morris 遍歷在 $O(1)$ 空間內完成嗎？

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
- [ ] **Base Case:** Did I handle `root is None`?
    **基本情況：** 我處理了 `root is None` 嗎？
- [ ] **Leaf Logic:** Does the logic hold for leaf nodes (left/right are None)?
    **葉節點邏輯：** 邏輯適用於葉節點嗎（左右皆為 None）？
- [ ] **Return Value:** Am I returning the correct value to the parent vs. updating a global answer?
    **返回值：** 我是返回正確的值給父節點，還是更新全域答案？
- [ ] **Complexity:** Is it strictly $O(N)$? Did I accidentally create $O(N^2)$ by calling a height function inside a loop?
    **複雜度：** 嚴格來說是 $O(N)$ 嗎？我是否因為在迴圈中呼叫高度函數而意外造成 $O(N^2)$？

---

## 9. Memory Anchors (記憶錨點)

### The "Manager-Employee" Analogy (「經理-員工」類比)
*   **Tree DP (Post-order):**
    Imagine you are a Manager (Node). You ask your Employees (Children) for their best performance numbers (Return values). You calculate your team's total result (Global update), but you can only report *your* personal best contribution up to *your* boss (Return to parent).
    **樹形動態規劃（後序）：**
    想像你是經理（節點）。你要求員工（子節點）提供他們最好的績效數據（返回值）。你計算團隊的總結果（全域更新），但你只能向*你的*老闆匯報*你*個人的最佳貢獻（返回給父節點）。

### The "Leap of Faith" (「信心的一躍」)
*   **Recursion:**
    Don't try to trace the recursion stack in your head for complex trees. Assume `recursive_call(node.left)` **magically** returns exactly what the docstring says it returns. Write the logic for the *current* node based on that trust.
    **遞迴：**
    不要試圖在腦海中追蹤複雜樹的遞迴堆疊。假設 `recursive_call(node.left)` 會**神奇地**準確返回 docstring 所描述的內容。基於這份信任編寫*當前*節點的邏輯。