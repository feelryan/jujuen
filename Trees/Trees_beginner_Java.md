Here is the comprehensive interview preparation guide for **Trees**, tailored for a Senior Software Engineer, adjusted to the **Beginner** depth level as requested, with **Java** implementation.

這是一份針對 **Trees（樹）** 的完整面試準備教材，專為資深軟體工程師量身打造，並依據要求調整為 **初學者（Beginner）** 深度，使用 **Java** 實作。

---

# Module: Trees (Foundations)
# 模組：樹（基礎篇）

## 1. Learning Objectives (學習目標)

1.  **Master Recursive Thinking:** Move beyond iterative loops and become comfortable with the "leap of faith" required for recursion.
    **掌握遞迴思維：** 超越迭代迴圈，習慣並自如地運用遞迴所需的「信心飛躍（leap of faith）」。
2.  **Understand Basic Traversals:** deeply understand Pre-order, In-order, Post-order, and Level-order (BFS) traversals.
    **理解基本遍歷：** 深度理解前序、中序、後序以及層序（BFS）遍歷。
3.  **Analyze Complexity Correctly:** Distinguish between balanced ($O(\log N)$) and skewed ($O(N)$) scenarios in time and space complexity.
    **正確分析複雜度：** 區分平衡樹（$O(\log N)$）與歪斜樹（$O(N)$）在時間與空間複雜度上的差異。

---

## 2. Core Concepts (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with no cycles.
樹是一種階層式的資料結構，由節點（nodes）與邊（edges）組成，且不包含任何環（cycles）。

Ideally, think of a tree as a recursive definition: A tree is a root node where the left and right children are also trees.
理想情況下，將樹視為一種遞迴定義：樹是一個根節點，其左右子節點本身也是樹。

### Complexity (複雜度)

| Operation | Average (Balanced) | Worst (Skewed) | Note |
| :--- | :--- | :--- | :--- |
| **Access/Search** | $O(\log N)$ | $O(N)$ | Depends on tree height. (視樹高而定) |
| **Insertion** | $O(\log N)$ | $O(N)$ | Finding the spot takes time. (尋找插入點需耗時) |
| **Deletion** | $O(\log N)$ | $O(N)$ | Re-linking nodes takes constant time after search. (搜尋後重新連結僅需常數時間) |
| **Space (Stack)**| $O(\log N)$ | $O(N)$ | Recursion stack depth equals tree height. (遞迴堆疊深度等於樹高) |

### When to Use (適用場景)
- Representing hierarchical data (File systems, Organization charts, DOM).
  表示階層數據（檔案系統、組織圖、DOM）。
- Fast search and sorting requirements (Binary Search Trees, Heaps).
  快速搜尋與排序需求（二元搜尋樹、堆積）。

### When NOT to Use (不適用場景)
- Data with cycles or many-to-many relationships (Use Graphs).
  具備環狀或多對多關係的數據（請使用圖）。
- Simple linear access needs (Use Arrays or Linked Lists).
  簡單的線性存取需求（請使用陣列或連結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the beginner level, focus on these three fundamental patterns.
針對初學者程度，請專注於這三種基礎模式。

### A. Top-down Recursion (Pre-order) / 由上而下的遞迴（前序）
Pass values *down* from the parent to children to update the state.
將數值從父節點 *向下* 傳遞給子節點以更新狀態。
*Key:* `function(node, params)`

### B. Bottom-up Recursion (Post-order) / 由下而上的遞迴（後序）
Gather results from children and pass them *up* to the parent.
從子節點收集結果並 *向上* 傳遞給父節點。
*Key:* `leftResult = function(node.left); return merge(leftResult, rightResult);`

### C. Breadth-First Search (Level Order) / 廣度優先搜尋（層序）
Process the tree layer by layer using a Queue.
使用佇列（Queue）逐層處理樹。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Depth of Binary Tree
### 問題：二元樹的最大深度

**Problem Statement:**
Given the root of a binary tree, return its maximum depth.
給定二元樹的根節點，回傳其最大深度。

**Intuition (思路):**
The depth of a node is 1 (for itself) plus the maximum depth of its subtrees.
一個節點的深度是 1（它自己）加上其子樹的最大深度。
This suggests a **Bottom-up** recursive approach.
這暗示了 **由下而上** 的遞迴方法。

#### 1. Brute Force / Naive Approach (暴力 / 樸素解法)
Traverse every path from root to leaf and track the maximum count.
遍歷從根到葉的每一條路徑並記錄最大計數。
*Critique:* DFS is essentially traversing paths, but we need to define the return value clearly.
*評論：* DFS 本質上就是在遍歷路徑，但我們需要清楚定義回傳值。

#### 2. Optimal Solution: Recursive DFS (最佳解：遞迴 DFS)
We define the base case: if the node is null, depth is 0.
我們定義基本情況（base case）：如果節點為空，深度為 0。
Otherwise, return `1 + max(depth(left), depth(right))`.
否則，回傳 `1 + max(左子樹深度, 右子樹深度)`。

#### Java Reference Code (Java 參考解)

```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */

class Solution {
    // Main function to find maximum depth
    // 尋找最大深度的主函數
    public int maxDepth(TreeNode root) {
        // Base Case: If the tree is empty, depth is 0.
        // 基本情況：如果樹是空的，深度為 0。
        if (root == null) {
            return 0;
        }

        // Recursive Step: Calculate depth of left and right subtrees.
        // 遞迴步驟：計算左子樹與右子樹的深度。
        int leftDepth = maxDepth(root.left);
        int rightDepth = maxDepth(root.right);

        // Logic: The depth of current node is 1 + the deeper of the two children.
        // 邏輯：當前節點的深度是 1 + 兩個子節點中較深的那一個。
        return Math.max(leftDepth, rightDepth) + 1;
    }
}
```

#### Complexity Analysis (複雜度分析)
- **Time:** $O(N)$ — We visit every node exactly once.
  **時間：** $O(N)$ — 我們確切地訪問每個節點一次。
- **Space:** $O(H)$ — Where $H$ is the height of the tree (stack usage). In worst case (skewed tree), $H = N$.
  **空間：** $O(H)$ — 其中 $H$ 是樹的高度（堆疊使用量）。在最差情況（歪斜樹），$H = N$.

#### Common Mistake (錯誤示範)
Using a global variable without resetting it, or forgetting the `+ 1`.
使用全域變數卻未重置，或是忘記 `+ 1`。

```java
// BAD PRACTICE: Relying on global state for simple recursion
// 不良實踐：依賴全域狀態來處理簡單遞迴
class BadSolution {
    int max = 0; // Global state is dangerous in interviews
                 // 全域狀態在面試中很危險
    public void dfs(TreeNode root, int depth) {
        if (root == null) return;
        if (depth > max) max = depth;
        dfs(root.left, depth + 1);
        dfs(root.right, depth + 1);
    }
}
```
*Why wrong:* While this works for one run, global variables make code hard to test and thread-unsafe. Prefer returning values.
*為何錯誤：* 雖然這跑一次能動，但全域變數讓程式碼難以測試且非執行緒安全。請優先選擇回傳數值的方式。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Height (高度)** | **Depth (深度)** | Height is bottom-up (leaf to node); Depth is top-down (root to node). <br> 高度是由下而上（葉到節點）；深度是由上而下（根到節點）。 |
| **Binary Tree** | **Binary Search Tree (BST)** | A Binary Tree has no order; BST implies `left < node < right`. <br> 二元樹沒有順序；BST 隱含 `左 < 節點 < 右` 的規則。 |
| **Balanced Tree** | **Complete Tree** | Balanced means height is $O(\log N)$; Complete means filled level-by-level. <br> 平衡樹指高度為 $O(\log N)$；完全二元樹指逐層填滿。 |
| **Base Case** | **Recursive Step** | Failing to handle `root == null` is the #1 cause of crashes. <br> 未處理 `root == null` 是導致崩潰的頭號原因。 |

---

## 6. Interview Strategy (面試實戰建議)

### Clarification (釐清需求)
- "Can the tree be null?" (樹可能是空的嗎？)
- "Is it a Binary Search Tree or just a Binary Tree?" (這是二元搜尋樹還是一般二元樹？)
- "Do we need to handle unbalanced trees?" (我們需要處理不平衡的樹嗎？)

### Whiteboard Strategy (白板策略)
1.  **Draw a small tree:** A root, two children, and maybe one grandchild.
    **畫一棵小樹：** 一個根，兩個子節點，也許再加一個孫節點。
2.  **Trace the recursion:** Use an arrow to show the flow going down, and a value circle to show it returning up.
    **追蹤遞迴：** 用箭頭表示向下的流程，用數值圈圈表示向上的回傳。
3.  **Handle Nulls first:** Write the `if (root == null)` line before anything else.
    **先處理 Null：** 在做任何事之前先寫下 `if (root == null)` 這一行。

### Follow-up Questions (常見追問)
- "How would you solve this iteratively?" (Hint: Use a `Stack` or `Queue`).
  「你會如何用迭代方式解決此題？」（提示：使用 `Stack` 或 `Queue`）。
- "What if the tree is an N-ary tree?" (Hint: Loop through `children` list).
  「如果是 N 元樹怎麼辦？」（提示：遍歷 `children` 列表）。

---

## 7. Practice Problems (練習題)

### Easy: Invert Binary Tree (翻轉二元樹)
*Prompt:* Swap left and right children for every node.
*提示：* 交換每個節點的左右子節點。
*Key Idea:* Post-order traversal. Swap children after visiting them (or Pre-order works too).
*核心思路：* 後序遍歷。訪問後交換子節點（前序也可以）。

### Medium: Validate Binary Search Tree (驗證二元搜尋樹)
*Prompt:* Check if a tree satisfies the BST property.
*提示：* 檢查樹是否符合 BST 的性質。
*Key Idea:* Top-down recursion. Pass a range `(min, max)` down. Left child must be `< node.val`, right child must be `> node.val`.
*核心思路：* 由上而下的遞迴。向下傳遞範圍 `(min, max)`。左子節點必須 `< node.val`，右子節點必須 `> node.val`。

### Medium (Advanced for Beginner): Path Sum (路徑總和)
*Prompt:* Does the tree have a root-to-leaf path summing to `targetSum`?
*提示：* 樹中是否存在一條從根到葉的路徑，其總和等於 `targetSum`？
*Key Idea:* Subtract node value from target as you go down. Base case: leaf node checks if `remainingSum == 0`.
*核心思路：* 向下走時從目標值減去節點值。基本情況：葉節點檢查 `remainingSum == 0`。

---

## 8. Quick Checklists (快速檢核表)

- [ ] **Base Case:** Did I handle `root == null`?
  **基本情況：** 我是否處理了 `root == null`？
- [ ] **Leaf Logic:** Do I need special logic for leaf nodes (e.g., `left == null && right == null`)?
  **葉節點邏輯：** 我是否需要針對葉節點的特殊邏輯（例如 `left == null && right == null`）？
- [ ] **Return Value:** Does my recursive function return the correct type (int, boolean, node)?
  **回傳值：** 我的遞迴函數是否回傳了正確的型別（int, boolean, node）？
- [ ] **Complexity:** Is my solution $O(N)$ time? Did I accidentally make it $O(N^2)$?
  **複雜度：** 我的解法是 $O(N)$ 時間嗎？我有沒有不小心寫成 $O(N^2)$？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Manager-Employee" Analogy for Recursion
### 遞迴的「經理-員工」類比
- **The Root is the CEO:** He doesn't do the work; he delegates to his VPs (Left and Right children).
  **根節點是 CEO：** 他不做具體工作；他委派給副總裁（左與右子節點）。
- **The Delegation:** "Tell me the max depth of your department."
  **委派：** 「告訴我你們部門的最大深度。」
- **The Result:** The CEO waits for answers, adds 1 (himself), and reports to the board.
  **結果：** CEO 等待答案，加上 1（他自己），然後向董事會報告。

### Visualizing Traversals
### 視覺化遍歷
- **Pre-order:** Visit **Me** first, then children. (Self-centered)
  **前序：** 先訪問 **我**，然後是孩子。（以自我為中心）
- **In-order:** Left child, **Me**, Right child. (Polite/Sorted)
  **中序：** 左孩子，**我**，右孩子。（禮貌/有序）
- **Post-order:** Children first, **Me** last. (Responsible leader cleaning up)
  **後序：** 孩子先，**我** 最後。（負責任的領導者做收尾）