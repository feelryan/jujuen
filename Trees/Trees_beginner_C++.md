Here is the complete interview preparation guide for **Trees (Beginner Level)**, tailored for a Senior Software Engineer using C++.

這是一份針對 **樹（初級）** 的完整面試準備指南，專為使用 C++ 的資深軟體工程師量身打造。

---

# Module: Trees (Beginner)
# 模組：樹（初級）

## 1. Learning Goals (學習目標)

*   **Master the Recursive Mindset:** Move beyond iterative thinking (loops) to trust the "leap of faith" in recursion.
    **掌握遞迴思維：** 超越迭代思考（迴圈），學會信任遞迴中的「信心飛躍（leap of faith）」。
*   **Solidify Traversal Algorithms:** Deeply understand DFS (Pre-order, In-order, Post-order) and BFS (Level-order).
    **鞏固遍歷演算法：** 深刻理解深度優先搜尋（前序、中序、後序）與廣度優先搜尋（層序）。
*   **Handle Edge Cases Gracefully:** Develop muscle memory for checking `nullptr` to prevent segmentation faults.
    **優雅處理邊界情況：** 培養檢查 `nullptr` 的肌肉記憶，以防止區段錯誤（Segmentation Faults）。
*   **Time & Space Complexity Analysis:** Understand why tree operations are typically $O(N)$ and space is $O(H)$.
    **時間與空間複雜度分析：** 理解為何樹的操作通常是 $O(N)$，而空間複雜度是 $O(H)$。

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition (定義)
A Tree is a hierarchical data structure consisting of nodes connected by edges, with a single root and no cycles.
樹是一種階層式的資料結構，由節點與邊連接而成，擁有單一根節點且無迴圈。

It is essentially a directed acyclic graph (DAG) with specific restrictions ($N$ nodes, $N-1$ edges).
它本質上是一種具有特定限制的有向無環圖（DAG）（$N$ 個節點，$N-1$ 條邊）。

### Intuition (直覺)
Think of a tree as a recursive structure: every node is the "root" of its own subtree.
將樹視為一種遞迴結構：每個節點都是其自身子樹的「根」。

### Complexity (複雜度)
*   **Time (時間):** $O(N)$ for traversal (visiting every node).
    $O(N)$ 用於遍歷（訪問每個節點）。
*   **Space (空間):** $O(H)$ where $H$ is the height of the tree (stack space for recursion).
    $O(H)$，其中 $H$ 為樹的高度（遞迴的堆疊空間）。
    *   Best Case (Balanced): $O(\log N)$.
        最佳情況（平衡）：$O(\log N)$。
    *   Worst Case (Skewed/Linked List): $O(N)$.
        最差情況（歪斜/鏈結串列）：$O(N)$。

### Use Cases (適用場景)
*   Representing hierarchical data (File systems, DOM, Org charts).
    表示階層數據（檔案系統、DOM、組織圖）。
*   Fast search and sorting (Binary Search Trees, Heaps).
    快速搜尋與排序（二元搜尋樹、堆積）。

### Non-Use Cases (不適用場景)
*   Data with cycles or many-to-many relationships (Use a Graph).
    具有迴圈或多對多關係的數據（請使用圖）。
*   Simple linear access (Use Arrays or Linked Lists).
    簡單的線性存取（請使用陣列或鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

For beginner-level tree problems, 90% of solutions fall into two categories:
對於初級樹的題目，90% 的解法歸類為以下兩類：

### 1. Depth-First Search (DFS) / Recursion (深度優先搜尋 / 遞迴)
*   **Pattern:** Process the current node, then recursively call the function on left and right children.
    **模式：** 處理當前節點，然後對左子節點和右子節點遞迴呼叫該函數。
*   **Types:**
    *   **Pre-order (前序):** Root $\to$ Left $\to$ Right (Copying tree, Prefix expression).
    *   **In-order (中序):** Left $\to$ Root $\to$ Right (BST validation, Sorted output).
    *   **Post-order (後序):** Left $\to$ Right $\to$ Root (Deleting tree, Bottom-up calculation like height).

### 2. Breadth-First Search (BFS) / Level Order (廣度優先搜尋 / 層序)
*   **Pattern:** Use a `std::queue` to process nodes level by level.
    **模式：** 使用 `std::queue` 逐層處理節點。
*   **Application:** Finding the shortest path in an unweighted tree/graph, or printing structure level-by-level.
    **應用：** 在無權重樹/圖中尋找最短路徑，或逐層列印結構。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Depth of Binary Tree
### 問題：二元樹的最大深度

**Problem Statement:**
Given the root of a binary tree, return its maximum depth.
給定二元樹的根節點，回傳其最大深度。

A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.
二元樹的最大深度是從根節點到最遠葉節點的最長路徑上的節點數。

### Approach 1: Recursive DFS (Bottom-Up)
### 思路 1：遞迴 DFS（由下而上）

*   **Logic:** The depth of a node is $1 + \max(\text{depth of left child}, \text{depth of right child})$.
    **邏輯：** 一個節點的深度是 $1 + \max(\text{左子節點深度}, \text{右子節點深度})$。
*   **Base Case:** If the node is `nullptr`, depth is 0.
    **基本情況：** 如果節點是 `nullptr`，深度為 0。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <algorithm> // for std::max
#include <iostream>

// Definition for a binary tree node.
// 二元樹節點的定義。
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

class Solution {
public:
    int maxDepth(TreeNode* root) {
        // Base Case: If the tree is empty, depth is 0.
        // 基本情況：如果樹是空的，深度為 0。
        if (root == nullptr) {
            return 0;
        }

        // Recursive Step: Calculate depth of left and right subtrees.
        // 遞迴步驟：計算左子樹和右子樹的深度。
        int leftDepth = maxDepth(root->left);
        int rightDepth = maxDepth(root->right);

        // The depth of current node is 1 (itself) + max of children.
        // 當前節點的深度為 1（自己）+ 子節點中的最大值。
        return 1 + std::max(leftDepth, rightDepth);
    }
};
```

### Common Mistake (錯誤示範) & Why (為何錯)

```cpp
// ❌ WRONG: Accessing children without checking nullptr first
// ❌ 錯誤：在未檢查 nullptr 的情況下存取子節點
int maxDepthWrong(TreeNode* root) {
    // Missing base case for root == nullptr
    // 缺少 root == nullptr 的基本情況
    
    // This will cause Segmentation Fault if root is null, or on leaf's children.
    // 如果 root 為空，或在葉節點的子節點上，這將導致區段錯誤 (Segmentation Fault)。
    int left = maxDepthWrong(root->left); 
    int right = maxDepthWrong(root->right);
    return 1 + std::max(left, right);
}
```

### BFS

```cpp
#include <queue>

class Solution {
public:
    int maxDepth(TreeNode* root) {
        if (root == nullptr) {
            return 0;
        }
        std:queue<TreeNode*> q;
        q.push(root);
        int depth = 0;
        while (q.empty() != true) {
            depth += 1;
            int depthLevel = q.size();
            for (int i=0 ; i < depthLevel; i++) {
                TreeNode *node = q.front();
                q.pop();
                if (node->left != nullptr) {
                    q.push(node->left);
                }
                if (node->right != nullptr) {
                    q.push(node->right);
                }
            }
        }
        return depth;
    }
};
```

### Analysis (分析)
*   **Time Complexity:** $O(N)$ — We visit every node exactly once.
    **時間複雜度：** $O(N)$ — 我們確切地訪問每個節點一次。
*   **Space Complexity:** $O(H)$ — In the worst case (skewed tree), the recursion stack grows to height $N$. In a balanced tree, it is $\log N$.
    **空間複雜度：** $O(H)$ — 在最差情況下（歪斜樹），遞迴堆疊增長到高度 $N$。在平衡樹中，它是 $\log N$。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept (概念) | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Height vs. Depth**<br>(高度 vs. 深度) | **Depth**: Distance from Root (Root is depth 0 or 1).<br>**Height**: Distance from Leaf (Leaf is height 0).<br>⚠️ *Pitfall:* Don't mix them up in problem descriptions.<br>**深度**：距根節點的距離。<br>**高度**：距葉節點的距離。<br>⚠️ *陷阱：* 不要在問題描述中混淆它們。 |
| **Nullptr Check**<br>(空指標檢查) | Always the first line of your recursive function.<br>遞迴函數的第一行永遠要是這個。<br>⚠️ *Pitfall:* Forgetting this causes immediate crash.<br>⚠️ *陷阱：* 忘記這一點會導致立即崩潰。 |
| **Pass by Value vs. Reference**<br>(傳值 vs. 傳參考) | `TreeNode* root` is a pointer passed by value. Changing `root` inside the function does not change the caller's pointer unless you use `TreeNode*& root`.<br>`TreeNode* root` 是傳值的指標。除非使用 `TreeNode*& root`，否則在函數內更改 `root` 不會更改呼叫者的指標。 |
| **Global Variables**<br>(全域變數) | Avoid using global variables for state (e.g., `int maxVal`). Pass a reference or use a helper class member instead for thread safety.<br>避免使用全域變數來儲存狀態。請改為傳遞參考或使用輔助類別成員以確保執行緒安全。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarification (釐清需求)
*   "Can the tree be empty (null root)?"
    「樹可以是空的嗎（空根節點）？」
*   "Is the tree balanced, or can it be a linked list?" (Affects complexity analysis).
    「樹是平衡的，還是可能像鏈結串列？」 （影響複雜度分析）。
*   "What are the node values? Are they unique?"
    「節點的值是什麼？它們是唯一的嗎？」

### 2. Whiteboard Strategy (白板策略)
*   **Draw a small tree:** A root with two children, and one child having a child. This covers general cases and leaf cases.
    **畫一棵小樹：** 一個根節點有兩個子節點，其中一個子節點還有一個子節點。這涵蓋了通用的情況和葉節點的情況。
*   **Trace the Recursion:** Use indentation on the whiteboard to simulate the stack.
    **追蹤遞迴：** 在白板上使用縮排來模擬堆疊。

### 3. Verbal Framework (口條框架)
*   "I will use a **Depth First Search** approach."
    「我將使用**深度優先搜尋**的方法。」
*   "My **base case** is when the node is null, I return..."
    「我的**基本情況**是當節點為空時，我回傳...」
*   "In the **recursive step**, I will process the left subtree, then..."
    「在**遞迴步驟**中，我將處理左子樹，然後...」

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單) - Invert Binary Tree
*   **Problem:** Swap left and right children for every node.
    **問題：** 交換每個節點的左右子節點。
*   **Hint:** Post-order traversal. Swap children, then recurse (or recurse then swap).
    **提示：** 後序遍歷。交換子節點，然後遞迴（或先遞迴再交換）。
*   **Key Code:** `std::swap(root->left, root->right);`

### Level: Medium (中等) - Symmetric Tree
*   **Problem:** Check if a tree is a mirror of itself.
    **問題：** 檢查樹是否是其自身的鏡像。
*   **Hint:** You need a helper function `isMirror(node1, node2)`.
    **提示：** 你需要一個輔助函數 `isMirror(node1, node2)`。
*   **Logic:** `node1->val == node2->val` AND `isMirror(node1->left, node2->right)` AND `isMirror(node1->right, node2->left)`.
    **邏輯：** 值相等 **且** 外側對外側 **且** 內側對內側。

### Level: Hard (for Beginner) - Diameter of Binary Tree
*   **Problem:** Length of the longest path between any two nodes (may not pass through root).
    **問題：** 任意兩個節點之間的最長路徑長度（可能不經過根節點）。
*   **Hint:** Use a global/member variable `maxDiameter` to keep track of the max path found so far while calculating height.
    **提示：** 在計算高度的同時，使用全域/成員變數 `maxDiameter` 來記錄目前找到的最長路徑。
*   **Logic:** At each node, `diameter = leftHeight + rightHeight`. Update global max. Return `1 + max(leftHeight, rightHeight)` to parent.
    **邏輯：** 在每個節點，`直徑 = 左高度 + 右高度`。更新全域最大值。回傳 `1 + max(左高度, 右高度)` 給父節點。

---

## 8. Quick Checklists (快速檢核表)

Before you say "I'm done":
在你說「我完成了」之前：

*   [ ] **Base Case:** Did I handle `root == nullptr`?
    **基本情況：** 我處理了 `root == nullptr` 嗎？
*   [ ] **Return Value:** Does my recursive function return the correct type (e.g., `int` vs `TreeNode*`)?
    **回傳值：** 我的遞迴函數回傳了正確的型別嗎？
*   [ ] **Leaf Nodes:** Does the logic hold for a node with no children?
    **葉節點：** 邏輯適用於沒有子節點的節點嗎？
*   [ ] **Complexity:** Is it $O(N)$ time? Did I acknowledge $O(H)$ stack space?
    **複雜度：** 是 $O(N)$ 時間嗎？我是否確認了 $O(H)$ 的堆疊空間？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Recursion as "Delegation" (遞迴即「授權」):**
    You are the manager (Root). You don't calculate the depth yourself. You shout to your two subordinates (Left & Right): "Tell me your depth!" They do the same. You just add 1 to the winner.
    你是經理（根節點）。你不自己計算深度。你對兩個下屬（左和右）大喊：「告訴我你們的深度！」他們也做同樣的事。你只需要將贏家的結果加 1。

*   **The Stack as "Russian Dolls" (堆疊即「俄羅斯娃娃」):**
    Entering a recursive call is like opening a doll. Hitting the base case (`nullptr`) is finding the smallest solid doll inside. Returning is closing the dolls back up one by one.
    進入遞迴呼叫就像打開一個娃娃。碰到基本情況（`nullptr`）就像找到裡面最小的實心娃娃。回傳就像把娃娃一個接一個地關回去。
