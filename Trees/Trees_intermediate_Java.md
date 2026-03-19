Here is the comprehensive guide on **Trees**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level with **Java** implementation.

這是一份針對 **Trees（樹）** 的完整教材，專為資深軟體工程師量身打造，聚焦於 **中階（Intermediate）** 難度，並使用 **Java** 實作。

---

# Module: Trees (Intermediate)
# 模組：樹（中階）

## 1. Learning Objectives (學習目標)

*   **Master Recursive Thinking (The "Leap of Faith"):** Move beyond tracing every step and learn to trust the recursive definition for sub-problems.
    **掌握遞迴思維（信念之躍）：** 超越逐行追蹤的習慣，學會信任子問題的遞迴定義。
*   **Differentiate Traversal Patterns:** Know exactly when to use Pre-order (construction), In-order (BST sorting), Post-order (bottom-up logic), and Level-order (BFS).
    **區分遍歷模式：** 清楚何時使用前序（建構）、中序（BST 排序）、後序（由下而上邏輯）與層序（BFS）。
*   **Handle State in Recursion:** Learn how to pass state down (parameters) vs. bubble state up (return values).
    **處理遞迴中的狀態：** 學習如何向下傳遞狀態（參數）與向上回傳狀態（返回值）。
*   **Analyze Complexity for Skewed Trees:** Understand why tree height $H$ is the critical factor in complexity, and how it varies from $\log N$ to $N$.
    **分析歪斜樹的複雜度：** 理解為何樹高 $H$ 是複雜度的關鍵因子，以及它如何從 $\log N$ 變動至 $N$。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with no cycles.
樹是一種階層式的資料結構，由節點與邊連接而成，且不包含迴圈。

For Senior Engineers, treat a Tree as a **Recursive Definition**: A tree is a root node where `root.left` and `root.right` are also trees (or null).
對於資深工程師而言，應將樹視為 **遞迴定義**：樹是一個根節點，其 `root.left` 與 `root.right` 本身也是樹（或為空）。

### Complexity (複雜度)
*   **Time (時間):** $O(N)$ for traversal (visiting every node). Search in BST is $O(H)$.
    **時間：** 遍歷為 $O(N)$（訪問每個節點）。BST 搜尋為 $O(H)$。
*   **Space (空間):** $O(H)$ for recursion stack.
    **空間：** 遞迴堆疊為 $O(H)$。
    *   Balanced (平衡): $H = \log N$
    *   Skewed (歪斜/最差): $H = N$

### When to Use (適用場景)
*   Representing hierarchies (file systems, org charts).
    表示階層關係（檔案系統、組織圖）。
*   Fast search and sorting (Binary Search Trees, Heaps).
    快速搜尋與排序（二元搜尋樹、堆積）。
*   Prefix matching (Tries).
    前綴匹配（Trie 樹）。

### When NOT to Use (不適用場景)
*   Data with cycles (use Graph).
    具迴圈的資料（請用圖）。
*   Simple linear access required (use Array/LinkedList).
    僅需簡單線性存取（請用陣列/鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. DFS Recursion (Depth-First Search)
*   **Pre-order:** Root $\to$ Left $\to$ Right. Used for serialization or copying.
    **前序：** 根 $\to$ 左 $\to$ 右。用於序列化或複製。
*   **In-order:** Left $\to$ Root $\to$ Right. Used for BST to get sorted data.
    **中序：** 左 $\to$ 根 $\to$ 右。用於 BST 以取得排序資料。
*   **Post-order:** Left $\to$ Right $\to$ Root. Used for deleting nodes or aggregating values from children (e.g., height, subtree sum).
    **後序：** 左 $\to$ 右 $\to$ 根。用於刪除節點或從子節點聚合數值（如高度、子樹總和）。

### B. BFS Level Order (Breadth-First Search)
*   Uses a `Queue`. Essential for "shortest path" in unweighted trees or printing level by level.
    使用 `Queue`。對於無權重樹的「最短路徑」或逐層列印至關重要。

### C. Top-down vs. Bottom-up
*   **Top-down:** Pass parameters (e.g., `current_max`) to children.
    **由上而下：** 將參數（如 `current_max`）傳遞給子節點。
*   **Bottom-up:** Gather return values from children to compute result for current node.
    **由下而上：** 收集子節點的回傳值以計算當前節點的結果。

---

## 4. Example Walkthrough (範例講解)

### Problem: Lowest Common Ancestor of a Binary Tree (二元樹的最近共同祖先)
Given a binary tree, find the lowest common ancestor (LCA) of two given nodes `p` and `q`.
給定一個二元樹，找出兩個指定節點 `p` and `q` 的最近共同祖先 (LCA)。

> **Definition:** The lowest node `T` that has both `p` and `q` as descendants.
> **定義：** 最底層的節點 `T`，使得 `p` 與 `q` 均為其後代。

### Approach 1: Brute Force (Path Storage) / 暴力法（路徑儲存）
**Idea:** Find the path from root to `p` and root to `q`, store them in lists, and find the last common node.
**思路：** 找出從根到 `p` 與從根到 `q` 的路徑，存入列表，並找出最後一個共同節點。
**Complexity:** Time $O(N)$, Space $O(N)$ (to store paths).
**複雜度：** 時間 $O(N)$，空間 $O(N)$（儲存路徑）。
**Verdict:** Acceptable, but requires extra space and two traversals.
**結論：** 可接受，但需要額外空間且需兩次遍歷。

### Approach 2: Optimized Recursive (Bottom-up) / 優化遞迴（由下而上）
**Idea:** Traverse the tree. If we find `p` or `q`, return it up. If a node receives non-null values from *both* left and right, it is the LCA.
**思路：** 遍歷樹。若發現 `p` 或 `q`，將其向上回傳。若某節點從左與右 *同時* 收到非空值，則該節點即為 LCA。

**Logic Flow (邏輯流):**
1.  Base case: If root is null, return null. If root is `p` or `q`, return root.
    基本情況：若根為空，回傳 null。若根為 `p` 或 `q`，回傳 root。
2.  Recurse left and right.
    遞迴左與右。
3.  If both left and right return non-null, current node is LCA.
    若左與右皆回傳非空值，當前節點即為 LCA。
4.  If only one returns non-null, pass that one up.
    若僅一邊回傳非空值，將該值向上傳遞。

### Java Solution (Reference)

```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode(int x) { val = x; }
 * }
 */
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        // 1. Base Case: End of branch OR found one of the targets
        // 1. 基本情況：分支結尾 或 找到目標節點之一
        if (root == null || root == p || root == q) {
            return root;
        }

        // 2. Recursive Step: Search in left and right subtrees
        // 2. 遞迴步驟：在左子樹與右子樹中搜尋
        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);

        // 3. Logic: If both sides returned a node, root is the split point (LCA)
        // 3. 邏輯：若兩邊皆回傳節點，則 root 為分岔點（LCA）
        if (left != null && right != null) {
            return root;
        }

        // 4. If only one side found a target (or LCA), propagate it up
        // 4. 若僅一邊找到目標（或 LCA），將其向上傳遞
        // If left is not null, return left; otherwise return right (which could be null)
        // 若 left 不為 null，回傳 left；否則回傳 right（可能為 null）
        return left != null ? left : right;
    }
}
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$ - We visit every node in the worst case.
    **時間：** $O(N)$ - 最差情況下訪問每個節點。
*   **Space:** $O(H)$ - Recursion stack height.
    **空間：** $O(H)$ - 遞迴堆疊高度。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Confusion (錯誤/混淆) | Correct Understanding (正確理解) |
| :--- | :--- | :--- |
| **Base Cases** | Forgetting to check `if (root == null)` causing NPE. <br> 忘記檢查 `if (root == null)` 導致 NPE。 | Always handle the null case first as the terminator of recursion. <br> 總是先處理 null 情況作為遞迴終止條件。 |
| **BST vs Binary Tree** | Assuming the tree is sorted (BST) when the problem says "Binary Tree". <br> 當題目說是「二元樹」時，誤以為是排序過的（BST）。 | A Binary Tree has no order guarantees. A BST guarantees `left < root < right`. <br> 二元樹無順序保證。BST 保證 `left < root < right`。 |
| **Symmetric Tree** | Comparing `root.left` with `root.right` directly inside one function call. <br> 在單次函數呼叫中直接比較 `root.left` 與 `root.right`。 | You usually need a helper function taking two nodes: `isMirror(node1, node2)`. <br> 通常需要一個接受兩個節點的輔助函數：`isMirror(node1, node2)`。 |
| **Java Object References** | Thinking `==` compares values. <br> 認為 `==` 比較數值。 | In Trees, we often compare node *identity* (references), so `==` is correct for checking if it's the *same node*. Use `.val` for values. <br> 在樹中，我們常比較節點*身分*（參考），故 `==` 用於檢查是否為*同一節點*是正確的。數值比較請用 `.val`。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarification (釐清需求)
*   "Is it a Binary Search Tree (BST) or a generic Binary Tree?" (Crucial for optimization).
    「這是二元搜尋樹 (BST) 還是普通二元樹？」（對優化至關重要）。
*   "Can the tree contain duplicate values?"
    「樹是否包含重複數值？」
*   "What should I return if the tree is empty or the target isn't found?"
    「若樹為空或找不到目標，我該回傳什麼？」

### 2. Visualization (視覺化)
*   Draw a small tree (e.g., 3 levels). Don't just draw a balanced one; draw a skewed one (linked list style) to remind yourself of edge cases.
    畫一棵小樹（如 3 層）。不要只畫平衡樹；畫一棵歪斜樹（鏈結串列狀）以提醒自己邊界情況。

### 3. Coding Strategy (編碼策略)
*   **Define the Node Class:** Even if provided, write `class TreeNode { int val; TreeNode left, right; }` quickly to show you know the structure.
    **定義節點類別：** 即使題目已提供，快速寫下 `class TreeNode...` 以展示你熟悉結構。
*   **Trust the Recursion:** Explain, "I assume the recursive call `solve(root.left)` will correctly solve the sub-problem for the left side."
    **信任遞迴：** 解釋：「我假設遞迴呼叫 `solve(root.left)` 會正確解決左邊的子問題。」

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Invert Binary Tree** (翻轉二元樹)
*   **Hint:** Swap `left` and `right` children, then recurse.
    **提示：** 交換 `left` 與 `right` 子節點，然後遞迴。
*   **Focus:** Getting comfortable with modifying the tree structure.
    **重點：** 習慣修改樹的結構。

### Level: Medium (Core)
**Problem:** **Binary Tree Right Side View** (二元樹的右視圖)
*   **Hint:** Use BFS (Level Order) and capture the last element of each level. OR use DFS (Root $\to$ Right $\to$ Left) and record the first node reached at each depth.
    **提示：** 使用 BFS（層序）並捕捉每層的最後一個元素。或使用 DFS（根 $\to$ 右 $\to$ 左）並記錄每個深度第一個到達的節點。
*   **Focus:** Traversal variations.
    **重點：** 遍歷的變體。

### Level: Medium/Hard (Design)
**Problem:** **Serialize and Deserialize Binary Tree** (二元樹的序列化與反序列化)
*   **Hint:** Use Pre-order traversal with a sentinel value (e.g., "X" or "null") for null nodes to preserve structure.
    **提示：** 使用前序遍歷，並對空節點使用哨兵值（如 "X" 或 "null"）以保留結構。
*   **Focus:** Reconstructing a tree from a string/array.
    **重點：** 從字串/陣列重建樹。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or coding:
在模擬面試或編碼時使用此表：

*   [ ] **Base Case:** Did I handle `root == null`?
    **基本情況：** 我是否處理了 `root == null`？
*   [ ] **Leaf Nodes:** Does the logic hold for leaf nodes (both children null)?
    **葉節點：** 邏輯是否適用於葉節點（兩子節點皆空）？
*   [ ] **Return Value:** Am I returning the correct type (Node vs. int vs. boolean)?
    **回傳值：** 我是否回傳正確型別（Node vs int vs boolean）？
*   [ ] **State:** If calculating a global max (like diameter), am I updating a global variable or passing an object?
    **狀態：** 若計算全域最大值（如直徑），我是更新全域變數還是傳遞物件？
*   [ ] **Complexity:** Did I mention $O(H)$ vs $O(N)$?
    **複雜度：** 我是否提到 $O(H)$ 與 $O(N)$ 的區別？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "CEO and Report" Analogy (CEO 與匯報類比)
*   **Recursion (Post-order):** The CEO (Root) cannot make a decision until they get reports from the VP of Engineering (Left) and VP of Sales (Right). The data flows **bottom-up**.
    **遞迴（後序）：** CEO（根）在收到工程副總（左）與銷售副總（右）的報告前無法決策。資料流向是 **由下而上**。

### The "Scanner" Analogy (掃描器類比)
*   **Pre-order:** Like a scanner copying a document. You see the header (Root) first, then read the first paragraph (Left), then the second (Right). Good for **cloning**.
    **前序：** 像掃描器複製文件。你先看到標題（根），接著讀第一段（左），再讀第二段（右）。適合 **複製**。

### The "Bookshelf" Analogy (書架類比)
*   **BST (In-order):** Reading books on a shelf from left to right. They are perfectly sorted.
    **BST（中序）：** 從左到右閱讀書架上的書。它們是完美排序的。