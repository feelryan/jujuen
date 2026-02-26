# Advanced Trees Interview Guide (進階樹結構面試指南)

## 1. Learning Goals (學習目標)

*   **Master Advanced Recursion Patterns:** Move beyond simple traversals to complex state management (bottom-up vs. top-down) and path construction.
    **掌握進階遞迴模式：** 超越單純的遍歷，掌握複雜的狀態管理（由下而上 vs. 由上而下）與路徑建構。
*   **Optimize Space Complexity:** Understand and implement iterative solutions or Morris Traversal to reduce space from $O(H)$ to $O(1)$ when required.
    **優化空間複雜度：** 理解並實作迭代解法或 Morris 遍歷，以便在需要時將空間從 $O(H)$ 降至 $O(1)$。
*   **Handle Structural Modifications:** Gain confidence in problems involving serialization, deserialization, and structural transformation (e.g., Tree to Linked List).
    **處理結構修改：** 建立處理序列化、反序列化以及結構轉換（如：樹轉鏈結串列）問題的信心。
*   **Trie & Segment Tree Awareness:** Recognize when to switch from a standard Binary Tree to a Trie (Prefix Tree) or Segment Tree for range queries.
    **Trie 與線段樹意識：** 辨識何時該從標準二元樹切換至 Trie（前綴樹）或線段樹以處理區間查詢。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with no cycles.
樹是一種由節點與邊連接而成的階層式資料結構，且不包含任何環（Cycle）。

For Senior Engineers, view a Tree as a **recursive definition**: A root with zero or more subtrees.
對於資深工程師而言，應將樹視為一個**遞迴定義**：一個根節點加上零個或多個子樹。

### Complexity (複雜度)

| Operation | Time Complexity (時間) | Space Complexity (空間) | Note (備註) |
| :--- | :--- | :--- | :--- |
| **Traversal (DFS/BFS)** | $O(N)$ | $O(H)$ | $H$ is height; $H=\log N$ (balanced) to $N$ (skewed). <br> $H$ 為高度；平衡時 $H=\log N$，歪斜時 $H=N$。 |
| **Search (BST)** | $O(H)$ | $O(H)$ | Worst case $O(N)$ if not balanced. <br> 若未平衡，最差情況為 $O(N)$。 |
| **Morris Traversal** | $O(N)$ | $O(1)$ | Modifies tree structure temporarily. <br> 暫時修改樹結構。 |

### When to Use (適用場景)
*   Representing hierarchical data (DOM, File Systems).
    表示階層式資料（DOM、檔案系統）。
*   Optimized searching and sorting (BST, Heaps).
    優化搜尋與排序（二元搜尋樹、堆積）。
*   Prefix matching (Tries).
    前綴匹配（Tries）。

### When NOT to Use (不適用場景)
*   Data with cyclic dependencies (Use Graphs).
    具有循環依賴的資料（請使用圖）。
*   Simple linear access patterns (Use Arrays/Linked Lists).
    單純的線性存取模式（請使用陣列/鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern 1: Bottom-Up DFS (Post-order Traversal)
**模式一：由下而上的深度優先搜尋（後序遍歷）**
*   **Concept:** Process children first, return values to the parent, and compute the result at the current node based on children's returns.
    **觀念：** 先處理子節點，將值回傳給父節點，並根據子節點的回傳值計算當前節點的結果。
*   **Use Cases:** Calculating height, diameter, checking balance, or maximum path sum.
    **適用案例：** 計算高度、直徑、檢查平衡或最大路徑和。

### Pattern 2: Top-Down DFS (Pre-order Traversal) with Global State
**模式二：由上而下的深度優先搜尋（前序遍歷）搭配全域狀態**
*   **Concept:** Pass values (like current path sum or min/max constraints) down to children.
    **觀念：** 將數值（如當前路徑和或最大/最小限制）向下傳遞給子節點。
*   **Use Cases:** Path sum target, validating BST, printing paths.
    **適用案例：** 路徑和目標、驗證二元搜尋樹、列印路徑。

### Pattern 3: Breadth-First Search (Level Order)
**模式三：廣度優先搜尋（層序遍歷）**
*   **Concept:** Use a Queue to process nodes level by level.
    **觀念：** 使用佇列（Queue）逐層處理節點。
*   **Use Cases:** Shortest path in unweighted graphs (trees), viewing the tree from the side (Right Side View).
    **適用案例：** 無權圖（樹）中的最短路徑、從側面觀察樹（右側視圖）。

### Pattern 4: Trie (Prefix Tree) Construction
**模式四：Trie（前綴樹）建構**
*   **Concept:** A tree where edges represent characters.
    **觀念：** 一種邊代表字元的樹。
*   **Use Cases:** Autocomplete, spell checker, IP routing.
    **適用案例：** 自動完成、拼字檢查、IP 路由。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Tree Maximum Path Sum (Hard)
**題目：二元樹中的最大路徑和（困難）**

#### Problem Statement (問題重述)
A **path** in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.
二元樹中的**路徑**是被邊連接的節點序列。每個節點在序列中至多出現一次。注意，路徑**不需要**經過根節點。

The **path sum** is the sum of the node's values in the path. Given the `root` of a binary tree, return the maximum path sum of any non-empty path.
**路徑和**是路徑中所有節點值的總和。給定二元樹的 `root`，回傳任何非空路徑的最大路徑和。

#### Thought Process (思路)

1.  **Brute Force (暴力法):**
    *   For every node, calculate all paths passing through it. This is extremely inefficient ($O(N^2)$ or worse) because paths can branch in complex ways.
    *   對每個節點，計算所有經過它的路徑。這非常低效（$O(N^2)$ 或更差），因為路徑的分支方式很複雜。

2.  **Optimization Insight (優化洞察):**
    *   A path can be viewed as: `Left Branch + Node + Right Branch`.
    *   路徑可以被視為：`左分支 + 節點 + 右分支`。
    *   However, to contribute to a *parent's* path, we can only pick **one** branch (either left or right) + the node itself. We cannot have a "Y" shape path going up.
    *   然而，若要貢獻給*父節點*的路徑，我們只能選擇**一條**分支（左或右）加上節點本身。我們不能向上形成「Y」字型的路徑。
    *   This suggests a **Bottom-Up DFS**. We need to return the "max single-path contribution" to the parent, while updating a global "max path sum" that might include both children (creating a local peak).
    *   這暗示了**由下而上的 DFS**。我們需要回傳「最大單一路徑貢獻」給父節點，同時更新可能包含兩個子節點（形成局部頂點）的全域「最大路徑和」。

3.  **Handling Negatives (處理負值):**
    *   If a subtree returns a negative sum, it reduces our total. We should ignore negative branches (treat them as 0).
    *   如果子樹回傳負的總和，它會減少我們的總值。我們應該忽略負的分支（將其視為 0）。

#### TypeScript Solution (TypeScript 參考解)

```typescript
/**
 * Definition for a binary tree node.
 */
class TreeNode {
    val: number
    left: TreeNode | null
    right: TreeNode | null
    constructor(val?: number, left?: TreeNode | null, right?: TreeNode | null) {
        this.val = (val === undefined ? 0 : val)
        this.left = (left === undefined ? null : left)
        this.right = (right === undefined ? null : right)
    }
}

function maxPathSum(root: TreeNode | null): number {
    // Initialize with a very small number to handle trees with all negative values.
    // 初始化為極小值，以處理全為負值的樹。
    let globalMax = -Infinity;

    /**
     * Helper function: Post-order traversal (Bottom-up).
     * Returns the maximum path sum extending downwards from the current node (one-way).
     * 輔助函式：後序遍歷（由下而上）。
     * 回傳從當前節點向下延伸的最大路徑和（單向）。
     */
    function dfs(node: TreeNode | null): number {
        // Base case: null nodes contribute 0.
        // 終止條件：空節點貢獻為 0。
        if (!node) return 0;

        // Recursively calculate max sum from left and right subtrees.
        // Use Math.max(0, ...) to ignore negative paths (pruning).
        // 遞迴計算左子樹與右子樹的最大和。
        // 使用 Math.max(0, ...) 來忽略負路徑（剪枝）。
        const leftGain = Math.max(dfs(node.left), 0);
        const rightGain = Math.max(dfs(node.right), 0);

        // Calculate the price of the new path passing through THIS node (potentially the peak).
        // This includes left child + node + right child.
        // 計算經過「此」節點的新路徑價值（此節點可能為頂點）。
        // 這包含 左子節點 + 節點本身 + 右子節點。
        const currentPathPrice = node.val + leftGain + rightGain;

        // Update the global maximum if the current "arch" is the largest found so far.
        // 如果當前的「拱形路徑」是目前發現最大的，則更新全域最大值。
        globalMax = Math.max(globalMax, currentPathPrice);

        // Return the max gain to the parent.
        // We can only choose ONE side to continue the path upwards.
        // 回傳最大增益給父節點。
        // 我們只能選擇一邊來繼續向上延伸路徑。
        return node.val + Math.max(leftGain, rightGain);
    }

    dfs(root);
    return globalMax;
}
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ — We visit every node exactly once.
    **時間：** $O(N)$ — 我們確切訪問每個節點一次。
*   **Space:** $O(H)$ — Recursion stack depth depends on tree height.
    **空間：** $O(H)$ — 遞迴堆疊深度取決於樹的高度。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Depth (深度)** | **Height (高度)** | Depth is edges from Root (Top-down). Height is edges from Leaf (Bottom-up). <br> 深度是從根算起的邊數（由上而下）。高度是從葉子算起的邊數（由下而上）。 |
| **Binary Tree** | **Binary Search Tree (BST)** | BT has no order. BST requires `Left < Node < Right`. <br> 二元樹無順序。BST 要求 `左 < 節點 < 右`。 |
| **Balanced Tree** | **Complete Tree** | Balanced: Height diff $\le 1$. Complete: Filled left-to-right. <br> 平衡樹：高度差 $\le 1$。完全樹：由左至右填滿。 |
| **Node vs Edge** | - | Path length is often defined by edges, but sometimes by nodes. **Clarify this!** <br> 路徑長度通常由邊定義，但有時由節點定義。**務必釐清！** |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarify Constraints (釐清限制)
*   "Is the tree balanced?" (Affects complexity).
    「這棵樹是平衡的嗎？」（影響複雜度）。
*   "Can node values be negative?" (Crucial for path sums).
    「節點值可以是負的嗎？」（對路徑和至關重要）。
*   "Are references to parent nodes available?" (Simplifies some traversals).
    「有父節點的參照嗎？」（簡化某些遍歷）。

### 2. The "Leap of Faith" (信心的跳躍)
When explaining recursion, don't trace every step. Say:
解釋遞迴時，不要追蹤每一步。請說：
> "Assuming the recursive function correctly returns the max path for the left and right subtrees, I will now process the current node by..."
> 「假設遞迴函式能正確回傳左子樹與右子樹的最大路徑，我現在將透過...來處理當前節點。」

### 3. Whiteboard Strategy (白板策略)
*   Draw a generic tree (not just a perfect triangle). Include a "zigzag" or a single long branch to test edge cases visually.
    畫一個一般的樹（不要只畫完美的三角形）。包含「之字形」或單一長分支，以視覺化測試邊界情況。
*   Define the `TreeNode` structure explicitly at the top.
    在上方明確定義 `TreeNode` 結構。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Diameter of Binary Tree**
**Hint:** Similar to Max Path Sum, but counting edges instead of values. Return height, update diameter globally.
**提示：** 類似最大路徑和，但計算的是邊數而非數值。回傳高度，全域更新直徑。

### Level: Medium (Standard)
**Problem:** **Lowest Common Ancestor (LCA) of a Binary Tree**
**Hint:** If `root` is `p` or `q`, return `root`. If both left and right returns are non-null, `root` is the LCA.
**提示：** 若 `root` 是 `p` 或 `q`，回傳 `root`。若左右回傳皆非空，則 `root` 即為 LCA。

### Level: Hard (Differentiation)
**Problem:** **Serialize and Deserialize Binary Tree**
**Hint:** Use Pre-order traversal with a sentinel value (e.g., `#` or `null`) for null children to preserve structure uniquely.
**提示：** 使用前序遍歷搭配哨兵值（如 `#` 或 `null`）來標記空子節點，以唯一地保留結構。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Base Case:** Did I handle `node === null`?
    **終止條件：** 我處理 `node === null` 了嗎？
*   [ ] **Return Value:** Does my recursive function return what the *parent* needs (e.g., height), or the final answer (e.g., diameter)?
    **回傳值：** 我的遞迴函式是回傳*父節點*需要的資訊（如高度），還是最終答案（如直徑）？
*   [ ] **Global vs Local:** Do I need a global variable (or class property) to track the maximum found so far?
    **全域 vs 區域：** 我需要全域變數（或類別屬性）來追蹤目前找到的最大值嗎？
*   [ ] **Null Pointer:** Did I check `node.left` before accessing `node.left.val`?
    **空指標：** 存取 `node.left.val` 之前，我檢查 `node.left` 了嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **The Corporate Hierarchy (公司階層):**
    *   **Root:** CEO.
    *   **Leaves:** Interns.
    *   **Bottom-Up Recursion:** Interns report status to managers, managers aggregate and report to directors. (Reporting chain).
    *   **由下而上遞迴：** 實習生回報狀況給經理，經理彙整後回報給總監。（匯報鏈）。
    *   **Top-Down Recursion:** CEO issues a budget constraint, passed down to departments. (Budget allocation).
    *   **由上而下遞迴：** CEO 發布預算限制，向下傳遞給各部門。（預算分配）。

*   **The Coat Hanger (衣架):**
    *   Imagine picking up the tree by a specific node. Gravity pulls the rest down. This helps visualize **re-rooting** problems.
    *   想像抓住某個節點把樹提起來。重力會將其餘部分往下拉。這有助於視覺化**換根（re-rooting）**問題。