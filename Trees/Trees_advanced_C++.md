Here is the comprehensive guide for **Trees** at an **Advanced** level, tailored for a Senior Software Engineer targeting Big Tech roles.
這是一份針對 **樹（Trees）** 的 **進階（Advanced）** 完整教材，專為目標 Big Tech 職位的資深軟體工程師量身打造。

---

# Advanced Trees for Senior Engineers
# 資深工程師的進階樹結構指南

## 1. Learning Objectives (學習目標)

1.  **Master "Tree DP" (Bottom-up Recursion):** Learn to pass complex states (not just simple integers) from children to parents to solve optimization problems.
    **掌握「樹形動態規劃」（自底向上遞迴）：** 學習從子節點向父節點傳遞複雜狀態（而不僅僅是簡單整數）以解決最佳化問題。
2.  **Conquer Structure Modification & Serialization:** Handle problems involving reconstructing trees, serializing to strings, or flattening structures without losing data.
    **征服結構修改與序列化：** 處理涉及重建樹、序列化為字串或在不丟失數據的情況下扁平化結構的問題。
3.  **Optimize Space Complexity (Iterative & Morris):** Understand how to convert recursive solutions to iterative ones to avoid stack overflow, and learn Morris Traversal for $O(1)$ space.
    **優化空間複雜度（迭代與 Morris）：** 理解如何將遞迴解法轉換為迭代解法以避免堆疊溢位，並學習 Morris 遍歷以達到 $O(1)$ 空間複雜度。
4.  **Deep Dive into BST Properties:** Go beyond basic validation; handle range queries and structural adjustments in Binary Search Trees efficiently.
    **深入二元搜尋樹（BST）特性：** 超越基礎驗證；高效處理二元搜尋樹中的範圍查詢與結構調整。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
A Tree is a hierarchical data structure that represents relationships without cycles.
樹是一種分層數據結構，表示無環的關係。
For senior interviews, treat Trees as a subset of Graphs ($N$ nodes, $N-1$ edges, connected, acyclic) where recursion is the most natural control flow.
對於資深面試，應將樹視為圖的一個子集（$N$ 個節點，$N-1$ 條邊，連通，無環），其中遞迴是最自然的控制流。

### Complexity (複雜度)
-   **Time:** Usually $O(N)$ since we must visit every node at least once.
    **時間：** 通常為 $O(N)$，因為我們必須至少訪問每個節點一次。
-   **Space:** $O(H)$ where $H$ is height.
    **空間：** $O(H)$，其中 $H$ 為高度。
    -   Balanced Tree (平衡樹): $O(\log N)$.
    -   Skewed Tree (歪斜樹): $O(N)$ (Risk of Stack Overflow / 堆疊溢位風險).

### When to use (適用場景)
-   Hierarchical data (File systems, Org charts).
    層次化數據（文件系統、組織圖）。
-   Fast lookup/insertion/deletion required (BST/AVL/Red-Black).
    需要快速查找/插入/刪除（BST/AVL/紅黑樹）。
-   Prefix matching (Tries).
    前綴匹配（Tries）。

### When NOT to use (不適用場景)
-   Data with cycles (Use General Graph).
    具有環的數據（使用一般圖）。
-   Simple linear access patterns (Use Array/LinkedList for cache locality).
    簡單的線性訪問模式（使用陣列/鏈結串列以獲得快取局部性）。

---

## 3. Typical Patterns (典型題型 / 模式)

### Pattern A: The "Manager Report" (Post-order Traversal / Tree DP)
**模式 A：「經理報告」（後序遍歷 / 樹形 DP）**
-   **Concept:** Process children first, gather information (height, max path, is_balanced), and report to the parent.
    **觀念：** 先處理子節點，收集資訊（高度、最大路徑、是否平衡），然後向父節點報告。
-   **Key:** The return value is often a custom struct or object containing multiple metrics.
    **關鍵：** 返回值通常是一個包含多個指標的自定義結構或物件。

### Pattern B: The "Top-Down Constraint" (Pre-order Traversal)
**模式 B：「自頂向下約束」（前序遍歷）**
-   **Concept:** Pass constraints (like min/max values for BST validation) from parent to children.
    **觀念：** 將約束條件（如 BST 驗證的最小/最大值）從父節點傳遞給子節點。

### Pattern C: Structure Modification (Pointer Manipulation)
**模式 C：結構修改（指標操作）**
-   **Concept:** Trimming a BST, flattening a tree to a linked list, or inverting a tree.
    **觀念：** 修剪 BST、將樹扁平化為鏈結串列，或翻轉樹。
-   **Key:** Always handle the `root` reference carefully; sometimes a dummy node is needed.
    **關鍵：** 總是小心處理 `root` 引用；有時需要一個虛擬節點（dummy node）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Tree Maximum Path Sum (Hard)
### 問題：二元樹中的最大路徑和（困難）

**Problem Statement:**
Given the `root` of a binary tree, return the *maximum path sum* of any non-empty path.
給定二元樹的 `root`，返回任意非空路徑的 *最大路徑和*。
A path does not need to pass through the root.
路徑不需要經過根節點。

**Example:**
Input: `[-10, 9, 20, null, null, 15, 7]`
Output: `42` (Path: 15 -> 20 -> 7)

---

### Phase 1: Naive Approach (Brute Force)
### 第一階段：樸素解法（暴力法）

**Idea:** For every node, calculate the max path passing through it and extending to both sides.
**思路：** 對於每個節點，計算經過它並向兩側延伸的最大路徑。
**Why it fails:** Calculating the path sum for every node repeatedly results in $O(N^2)$ time complexity.
**為何失敗：** 重複計算每個節點的路徑和會導致 $O(N^2)$ 的時間複雜度。

---

### Phase 2: Optimized Approach (Tree DP / Post-order)
### 第二階段：優化解法（樹形 DP / 後序遍歷）

**Insight:**
A path can be split into two parts:
路徑可以分為兩部分：
1.  **The "Arch" (Internal Path):** Left Child + Node + Right Child. This cannot be extended to the parent.
    **「拱形」（內部路徑）：** 左子節點 + 節點 + 右子節點。這不能延伸到父節點。
2.  **The "Branch" (Extendable Path):** Node + max(Left, Right). This can be extended to the parent.
    **「分支」（可延伸路徑）：** 節點 + max(左, 右)。這可以延伸到父節點。

**Algorithm:**
Use a global variable (or reference parameter) to track the global maximum "Arch".
使用全域變數（或引用參數）來追蹤全域最大「拱形」。
The recursion function returns the max "Branch" sum to the parent.
遞迴函數將最大「分支」和返回給父節點。

---

### C++ Reference Solution (C++ 參考解)

```cpp
#include <algorithm>
#include <climits>
#include <iostream>

using namespace std;

// Definition for a binary tree node.
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

class Solution {
private:
    int globalMaxSum; // To store the result / 用於存儲結果

    // Helper function: Returns the max gain from one branch (left or right)
    // 輔助函數：返回從一個分支（左或右）能獲得的最大收益
    int maxGain(TreeNode* node) {
        if (node == nullptr) {
            return 0; // Base case: null node contributes 0 / 基本情況：空節點貢獻 0
        }

        // Recursively calculate max gain from left and right subtrees
        // 遞迴計算左右子樹的最大收益
        // Use max(0, ...) to ignore negative paths (we can choose not to include them)
        // 使用 max(0, ...) 來忽略負路徑（我們可以選擇不包含它們）
        int leftGain = max(maxGain(node->left), 0);
        int rightGain = max(maxGain(node->right), 0);

        // Current path sum including both children (The "Arch")
        // 當前路徑和，包含兩個子節點（「拱形」）
        int currentPathSum = node->val + leftGain + rightGain;

        // Update global maximum if current path is better
        // 如果當前路徑更好，更新全域最大值
        globalMaxSum = max(globalMaxSum, currentPathSum);

        // Return the max gain extendable to the parent (Node + one best child)
        // 返回可延伸至父節點的最大收益（節點 + 一個最佳子節點）
        return node->val + max(leftGain, rightGain);
    }

public:
    int maxPathSum(TreeNode* root) {
        globalMaxSum = INT_MIN; // Initialize with smallest integer / 初始化為最小整數
        maxGain(root);
        return globalMaxSum;
    }
};
```

### Complexity Analysis (複雜度分析)
-   **Time:** $O(N)$ — We visit each node exactly once.
    **時間：** $O(N)$ — 我們精確地訪問每個節點一次。
-   **Space:** $O(H)$ — Recursion stack depth depends on tree height.
    **空間：** $O(H)$ — 遞迴堆疊深度取決於樹的高度。

### Common Mistakes in this Problem (此題常見錯誤)
1.  **Forgetting negative numbers:** Not handling cases where all nodes are negative (should return the single largest node, not 0).
    **忘記負數：** 未處理所有節點均為負數的情況（應返回單個最大節點，而非 0）。
    *Fix:* Initialize `globalMaxSum` to `INT_MIN`.
    *修正：* 將 `globalMaxSum` 初始化為 `INT_MIN`。
2.  **Confusing return value with global update:** Returning the "Arch" sum to the parent breaks the path definition (paths cannot branch).
    **混淆返回值與全域更新：** 將「拱形」和返回給父節點會破壞路徑定義（路徑不能分叉）。

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept A | Concept B | Distinction (區別) |
| :--- | :--- | :--- |
| **Height (高度)** | **Depth (深度)** | Height is bottom-up (leaf is 0 or 1); Depth is top-down (root is 0 or 1). <br> 高度是自底向上（葉子為0或1）；深度是自頂向下（根為0或1）。 |
| **Binary Tree** | **Binary Search Tree (BST)** | BT has no order; BST enforces `left < node < right`. <br> 二元樹無序；BST 強制 `左 < 節點 < 右`。 |
| **Balanced (平衡)** | **Symmetric (對稱)** | Balanced refers to height diff; Symmetric refers to mirror image structure. <br> 平衡指高度差；對稱指鏡像結構。 |
| **Complete Tree** | **Full Tree** | Complete: Filled left-to-right (Heap); Full: Every node has 0 or 2 children. <br> 完全樹：從左到右填滿（堆積）；滿二元樹：每個節點有 0 或 2 個子節點。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are node values negative?", "Is the tree balanced?", "Can I modify the tree structure?"
    **釐清限制：** 「節點值是否為負？」、「樹是否平衡？」、「我可以修改樹結構嗎？」
2.  **Visualize:** Draw a generic tree (not just a perfect triangle) to spot edge cases like skewed lines.
    **視覺化：** 畫一個一般的樹（不要只畫完美的三角形），以發現像歪斜線這樣的邊界情況。
3.  **Define Recursion Signature:** Before coding, explicitly state: "My recursive function will return X and take Y as arguments."
    **定義遞迴簽名：** 在編碼之前，明確說明：「我的遞迴函數將返回 X 並接受 Y 作為參數。」

### Whiteboard Strategy (白板策略)
-   **Space Management:** Write the `TreeNode` struct in a corner first so you can refer to `node->left` without ambiguity.
    **空間管理：** 先在角落寫下 `TreeNode` 結構，這樣你可以無歧義地引用 `node->left`。
-   **Base Cases First:** Always write `if (!root) return ...` immediately. It shows discipline.
    **基本情況優先：** 總是立即寫下 `if (!root) return ...`。這顯示了紀律性。

### Common Follow-ups (常見追問)
-   **Q:** "How to solve this if the tree is too deep for recursion (Stack Overflow)?"
    **問：** 「如果樹太深導致遞迴堆疊溢位（Stack Overflow），該如何解決？」
    -   **A:** Use iterative DFS with an explicit `std::stack`, or Morris Traversal for $O(1)$ space.
    -   **答：** 使用帶有顯式 `std::stack` 的迭代 DFS，或使用 Morris 遍歷以獲得 $O(1)$ 空間。
-   **Q:** "Can you parallelize this?"
    **問：** 「你能將其並行化嗎？」
    -   **A:** For read-only traversals, yes (MapReduce style). For structure modification, locking is complex.
    -   **答：** 對於唯讀遍歷，可以（MapReduce 風格）。對於結構修改，鎖定機制很複雜。

---

## 7. Practice Problems (練習題)

### Easy: Subtree of Another Tree
### 易：另一棵樹的子樹
-   **Hint:** Serialize both trees (Pre-order with null markers) and check for substring. Or double recursion.
    **提示：** 序列化兩棵樹（帶有 null 標記的前序遍歷）並檢查子字串。或者使用雙重遞迴。
-   **Focus:** Correctness of base cases.
    **重點：** 基本情況的正確性。

### Medium: Lowest Common Ancestor of a Binary Tree
### 中：二元樹的最近共同祖先
-   **Hint:** Bottom-up. If a node sees `p` on left and `q` on right, it is the LCA.
    **提示：** 自底向上。如果一個節點在左邊看到 `p`，在右邊看到 `q`，那它就是 LCA。
-   **Focus:** Handling cases where `p` or `q` is the ancestor of the other.
    **重點：** 處理 `p` 或 `q` 是對方祖先的情況。

### Hard: Serialize and Deserialize Binary Tree
### 難：二元樹的序列化與反序列化
-   **Hint:** Use Pre-order (Root -> Left -> Right). Store `null` as `#`. Use a queue/iterator for deserialization to track progress.
    **提示：** 使用前序遍歷（根 -> 左 -> 右）。將 `null` 存為 `#`。反序列化時使用佇列/迭代器來追蹤進度。
-   **Focus:** System design aspect (format efficiency) and state management during reconstruction.
    **重點：** 系統設計層面（格式效率）和重建過程中的狀態管理。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review / Debugging (自我審查 / 除錯)
-   [ ] **Null Pointer:** Did I check `if (!root)` at the very start?
    **空指標：** 我是否在一開始就檢查了 `if (!root)`？
-   [ ] **Leaf Logic:** Does the code work for a leaf node (left/right are null)?
    **葉節點邏輯：** 代碼對葉節點（左右為空）是否有效？
-   [ ] **Single Child:** Does it handle nodes with only one child correctly?
    **單子節點：** 是否正確處理只有一個子節點的節點？
-   [ ] **Return Values:** Am I returning the correct type (pointer vs value)?
    **返回值：** 我返回的類型正確嗎（指標 vs 數值）？

### Complexity Confirmation (複雜度確認)
-   [ ] Time: Is it $O(N)$? Did I accidentally do $O(N^2)$ by calling a height function inside a loop?
    時間：是 $O(N)$ 嗎？我是否因在迴圈內調用高度函數而意外造成 $O(N^2)$？
-   [ ] Space: Is it $O(H)$?
    空間：是 $O(H)$ 嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "CEO Report" (Bottom-Up / Post-Order)
### 「CEO 報告」（自底向上 / 後序）
-   **Image:** Employees (leaves) fill out spreadsheets. Managers (internal nodes) aggregate them and add their own summary. The CEO (root) gets the final report.
-   **圖像：** 員工（葉子）填寫電子表格。經理（內部節點）匯總它們並添加自己的摘要。CEO（根）獲得最終報告。
-   **Use for:** Height, Diameter, Sum, Balanced Check.
-   **用於：** 高度、直徑、總和、平衡檢查。

### The "Red Thread" (Morris Traversal)
### 「紅線」（Morris 遍歷）
-   **Image:** Imagine sewing a thread from a leaf back to its ancestor so you can climb back up without a stack (map).
-   **圖像：** 想像從葉子縫一條線回到它的祖先，這樣你就可以在沒有堆疊（地圖）的情況下爬回去。
-   **Use for:** $O(1)$ Space constraints.
-   **用於：** $O(1)$ 空間限制。