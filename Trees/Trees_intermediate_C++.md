Here is a comprehensive guide on **Trees (Intermediate Level)**, tailored for a Senior Software Engineer, using C++ as the implementation language.
這是一份針對 **樹（中級難度）** 的完整教材，專為資深軟體工程師量身打造，並使用 C++ 作為實作語言。

---

# Module: Trees (Intermediate) / 模組：樹（中級）

## 1. Learning Objectives (學習目標)

1.  **Master the distinction between Top-down and Bottom-up DFS.**
    掌握「由上而下」與「由下而上」深度優先搜尋（DFS）的區別。
    *Goal: Know when to pass parameters down (e.g., constraints) versus bubbling values up (e.g., subtree properties).*
    *目標：知道何時向下傳遞參數（如限制條件），何時向上回傳數值（如子樹屬性）。*

2.  **Handle Global State vs. Local Return Values.**
    處理全域狀態與區域回傳值。
    *Goal: Solve problems where the answer is updated globally during traversal, while the recursion returns something else (e.g., Max Path Sum).*
    *目標：解決那些在遍歷過程中更新全域答案，但遞迴函數回傳不同數值的問題（例如：最大路徑和）。*

3.  **Deepen understanding of BST Invariants.**
    加深對二元搜尋樹（BST）不變性的理解。
    *Goal: Go beyond simple lookups to validating and fixing BST structures efficiently.*
    *目標：超越單純的查找，能夠高效地驗證與修復 BST 結構。*

---

## 2. Core Concepts at a Glance (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a connected, undirected graph with no cycles, typically visualized as a hierarchical structure with a root.
樹是一個連通、無向且無環的圖，通常被視覺化為具有根節點的階層結構。

For Senior Engineers, treat trees as **recursive data definitions**: A tree is a node containing a value and a list of references to other trees (children).
對於資深工程師而言，應將樹視為**遞迴資料定義**：樹是一個包含數值以及指向其他樹（子節點）之參考列表的節點。

### Complexity (複雜度)

| Operation | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity | Note |
| :--- | :--- | :--- | :--- | :--- |
| **DFS/BFS Traversal** | $O(N)$ | $O(N)$ | $O(H)$ | $H$ is height ($ \log N $ to $ N $). / $H$ 為高度。 |
| **BST Search/Insert** | $O(\log N)$ | $O(N)$ | $O(H)$ | Worst case is a skewed line. / 最差情況為歪斜成一直線。 |
| **Deletion** | $O(\log N)$ | $O(N)$ | $O(H)$ | Requires pointer manipulation. / 需要指標操作。 |

### When to Use (適用場景)
*   **Hierarchical Data:** File systems, DOM structures, Organizational charts.
    **階層式資料：** 檔案系統、DOM 結構、組織圖。
*   **Fast Lookup & Ordering:** Binary Search Trees (BST), Heaps (Priority Queues).
    **快速查找與排序：** 二元搜尋樹（BST）、堆積（優先佇列）。
*   **Syntax Analysis:** Abstract Syntax Trees (AST) in compilers.
    **語法分析：** 編譯器中的抽象語法樹（AST）。

### When NOT to Use (不適用場景)
*   **Cyclic Dependencies:** Use a general Graph.
    **循環依賴：** 請使用一般圖形（Graph）。
*   **Simple Linear Access:** Arrays or Linked Lists are more cache-friendly and simpler.
    **簡單線性存取：** 陣列或連結串列對快取更友善且更簡單。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: One-Pass Global Update (Post-order DFS)
**模式 A：單次遍歷全域更新（後序 DFS）**
Used when the result depends on the relationship between left and right subtrees (e.g., Diameter, Max Path Sum).
適用於結果取決於左子樹與右子樹關係的情況（例如：直徑、最大路徑和）。
*   **Key:** The recursive function returns "info to parent", but updates a "global answer" internally.
    **關鍵：** 遞迴函數回傳「給父節點的資訊」，但在內部更新「全域答案」。

### Pattern B: Path Construction / Backtracking (Pre-order DFS)
**模式 B：路徑建構 / 回溯（前序 DFS）**
Used when you need to list paths meeting criteria (e.g., Path Sum II).
適用於需要列出符合條件之路徑的情況（例如：路徑總和 II）。
*   **Key:** Maintain a `current_path` list, push node on entry, pop on exit.
    **關鍵：** 維護一個 `current_path` 列表，進入節點時推入，離開時彈出。

### Pattern C: Level-Order Traversal (BFS)
**模式 C：層序遍歷（BFS）**
Used for "nearest" problems or structure serialization.
適用於「最近距離」問題或結構序列化。
*   **Key:** Use a `std::queue` and process `size` of queue at each iteration to track levels.
    **關鍵：** 使用 `std::queue` 並在每次迭代處理佇列當前的 `size` 以追蹤層級。

---

## 4. Example Walkthrough (範例講解)

### Problem: Lowest Common Ancestor of a Binary Tree (二元樹的最近共同祖先)

```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
        if (root == nullptr || root == p || root == q) {
            return root;
        }

        TreeNode *left = lowestCommonAncestor(root->left, p, q);
        TreeNode *right = lowestCommonAncestor(root->right, p, q);

        if (left != nullptr && right != nullptr) {
            return root;
        }

        return left != nullptr ? left : right;
    }
};
```

### Problem: Binary Tree Maximum Path Sum (Hard)
**問題：二元樹中的最大路徑和（困難）**

#### Problem Statement (問題重述)
Given the `root` of a binary tree, return the maximum path sum of any non-empty path.
給定二元樹的 `root`，回傳任何非空路徑的最大路徑和。
The path does not need to pass through the root. Nodes can have negative values.
路徑不需要經過根節點。節點可能包含負值。

#### Thought Process (思路)

1.  **Naive Approach (Brute Force):**
    **暴力法：**
    Calculate the max path starting from every single node.
    計算從每一個節點出發的最大路徑。
    *Complexity:* $O(N^2)$. Too slow.
    *複雜度：* $O(N^2)$。太慢了。

2.  **Optimization (Bottom-up DFS):**
    **優化（由下而上 DFS）：**
    A path can be defined by a "pivot" node where the path curves (goes up from left child, turns at pivot, goes down to right child).
    一條路徑可以由一個「樞紐」節點定義，路徑在此轉彎（從左子節點上來，在樞紐轉彎，下到右子節點）。
    
    For any node `u`, the max path passing *through* `u` as the highest point is:
    對於任何節點 `u`，以 `u` 為最高點並經過它的最大路徑為：
    `u->val + max(left_gain, 0) + max(right_gain, 0)`

    However, `u` can only contribute `u->val + max(left_gain, right_gain)` to its own parent.
    然而，`u` 只能向其父節點貢獻 `u->val + max(left_gain, right_gain)`。

3.  **Optimal Solution:**
    **最佳解：**
    Use a helper function (DFS) that returns the "max single-path gain" to the parent, while updating the global maximum path sum using the "split path" formula.
    使用一個輔助函數（DFS），回傳「最大單一路徑增益」給父節點，同時使用「分岔路徑」公式更新全域最大路徑和。

#### C++ Reference Solution (C++ 參考解)

```cpp
#include <algorithm>
#include <climits>
#include <iostream>

// Definition for a binary tree node.
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};

class Solution {
private:
    int globalMaxSum; // Stores the result / 儲存結果

    // Helper function: returns max gain from one branch (left or right) including self
    // 輔助函數：回傳包含自身在內的單一分支（左或右）最大增益
    int maxGain(TreeNode* node) {
        if (node == nullptr) {
            return 0; // Base case: null node contributes 0 / 基本情況：空節點貢獻為 0
        }

        // Recursively calculate max gain from left and right subtrees
        // 遞迴計算左右子樹的最大增益
        // Use max(..., 0) to ignore negative paths
        // 使用 max(..., 0) 來忽略負數路徑
        int leftGain = std::max(maxGain(node->left), 0);
        int rightGain = std::max(maxGain(node->right), 0);

        // Current path sum including both children (Split path)
        // 包含兩個子節點的當前路徑和（分岔路徑）
        int currentPathSum = node->val + leftGain + rightGain;

        // Update global maximum
        // 更新全域最大值
        globalMaxSum = std::max(globalMaxSum, currentPathSum);

        // Return the max gain the current node can provide to its parent
        // Note: Can only choose ONE side (left or right) to continue the path upwards
        // 回傳當前節點能提供給父節點的最大增益
        // 注意：只能選擇一邊（左或右）以繼續向上延伸路徑
        return node->val + std::max(leftGain, rightGain);
    }

public:
    int maxPathSum(TreeNode* root) {
        globalMaxSum = INT_MIN; // Initialize with smallest integer / 初始化為最小整數
        maxGain(root);
        return globalMaxSum;
    }
};
```

#### Complexity Analysis (複雜度分析)
*   **Time:** $O(N)$. We visit every node exactly once.
    **時間：** $O(N)$。我們確切地訪問每個節點一次。
*   **Space:** $O(H)$. The recursion stack depth depends on tree height.
    **空間：** $O(H)$。遞迴堆疊深度取決於樹的高度。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Binary Tree (BT)** | **Binary Search Tree (BST)** | BT has no order; BST implies `Left < Node < Right`. Don't assume BST properties unless specified. <br> BT 無序；BST 隱含 `左 < 節點 < 右`。除非特別說明，否則不要假設是 BST。 |
| **Depth (深度)** | **Height (高度)** | Depth is distance from Root (Top-down); Height is distance from Leaf (Bottom-up). <br> 深度是距根節點的距離（由上而下）；高度是距葉節點的距離（由下而上）。 |
| **Balanced Tree** | **Complete Tree** | Balanced means height difference $\le 1$; Complete means filled left-to-right. <br> 平衡指高度差 $\le 1$；完全指由左至右填滿。 |
| **Node Value** | **Node Reference** | In C++, `node` is a pointer, `node->val` is data. Confusing them causes compile errors. <br> 在 C++ 中，`node` 是指標，`node->val` 是資料。混淆兩者會導致編譯錯誤。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Clarification (釐清需求)
*   "Can node values be negative?" (Crucial for path sums).
    「節點數值可以是負的嗎？」（對路徑和問題至關重要）。
*   "Is the tree a BST or a generic Binary Tree?"
    「這是二元搜尋樹還是一般二元樹？」
*   "What should I return if the root is null?"
    「如果根節點為空，我該回傳什麼？」

### 2. Whiteboard/Thinking Strategy (白板/思考策略)
*   **Draw a recursive diagram:** Draw a node, a triangle for Left child, a triangle for Right child. Ask: "If I know the answer for L and R, how do I compute Root?"
    **畫遞迴圖：** 畫一個節點，左子節點畫三角形，右子節點畫三角形。問自己：「如果我知道 L 和 R 的答案，我該如何計算 Root？」
*   **State the Traversal:** "I will use post-order traversal because I need information from children to process the parent."
    **陳述遍歷方式：** 「我將使用後序遍歷，因為我需要子節點的資訊來處理父節點。」

### 3. Common Follow-ups (常見追問)
*   "How would you handle this iteratively?" (Prepare Stack for DFS, Queue for BFS).
    「你會如何用迭代方式處理這個問題？」（準備 Stack 做 DFS，Queue 做 BFS）。
*   "What if the tree is too large for memory?" (Discussion on Serialization/Disk storage).
    「如果樹大到記憶體裝不下怎麼辦？」（討論序列化/磁碟儲存）。

---

## 7. Practice Problems (練習題)

### Level 1: Easy (Warm-up)
**Problem:** **Invert Binary Tree** (翻轉二元樹)
*   **Hint:** Swap left and right pointers, then recurse.
    **提示：** 交換左右指標，然後遞迴。
*   **Focus:** Writing clean, 3-line recursive code.
    **重點：** 寫出乾淨、三行的遞迴程式碼。

### Level 2: Medium (Core Pattern)
**Problem:** **Validate Binary Search Tree** (驗證二元搜尋樹)
*   **Hint:** Top-down DFS. Pass `min` and `max` range constraints down. `validate(node, long min, long max)`.
    **提示：** 由上而下 DFS。向下傳遞 `min` 和 `max` 範圍限制。 `validate(node, long min, long max)`。
*   **Trap:** Checking only `left < node < right` is wrong; you must check the entire subtree against ancestral bounds.
    **陷阱：** 只檢查 `左 < 節點 < 右` 是錯的；必須針對祖先的邊界檢查整個子樹。

### Level 3: Hard (System Design Flavor)
**Problem:** **Serialize and Deserialize Binary Tree** (二元樹的序列化與反序列化)
*   **Hint:** Use Pre-order traversal with a sentinel (e.g., "#") for nulls.
    **提示：** 使用前序遍歷，並用哨兵值（如 "#"）代表空節點。
*   **Focus:** String manipulation in C++ (`stringstream`) and reconstructing tree state.
    **重點：** C++ 中的字串操作（`stringstream`）與重建樹的狀態。

---

## 8. Quick Checklists (快速檢核表)

### Debugging / Self-Review (除錯 / 自我審查)
- [ ] Did I handle `root == nullptr`? (Base case)
      我是否處理了 `root == nullptr`？（基本情況）
- [ ] Am I returning the correct type? (Node pointer vs. Integer value)
      我回傳的型別正確嗎？（節點指標 vs. 整數數值）
- [ ] If using C++, did I check for `nullptr` before accessing `node->left`?
      如果使用 C++，我在存取 `node->left` 之前是否檢查了 `nullptr`？
- [ ] Is my complexity strictly $O(N)$? Did I accidentally nest traversals?
      我的複雜度嚴格為 $O(N)$ 嗎？我是否不小心巢狀遍歷了？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Corporate Hierarchy" Analogy (「企業階層」類比)
*   **Top-down (Pre-order):** The CEO sends a memo down to all employees. "Everyone, make sure your budget is < $10k".
    **由上而下（前序）：** CEO 發備忘錄給所有員工。「各位，確保你們的預算 < 1萬」。
    *(Used for: Validating constraints).*
    *（用於：驗證限制條件）。*

*   **Bottom-up (Post-order):** Employees report their earnings up to the manager. The manager sums them up and reports to the director.
    **由下而上（後序）：** 員工向上級回報收益。經理加總後回報給總監。
    *(Used for: Subtree sums, height, diameter).*
    *（用於：子樹總和、高度、直徑）。*

### The "Coat Hanger" Visual (「衣架」視覺化)
*   Imagine the tree is a mobile/coat hanger.
    想像樹是一個懸掛式掛飾/衣架。
*   **Balancing:** If one side is too heavy (deep), the whole thing tips over. Rotations (AVL/Red-Black) are just shifting weights to the other hook.
    **平衡：** 如果一邊太重（太深），整個東西會傾倒。旋轉（AVL/紅黑樹）只是將重量移到另一個掛鉤上。
