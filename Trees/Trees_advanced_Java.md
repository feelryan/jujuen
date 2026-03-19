Here is the comprehensive guide for **Advanced Trees**, tailored for a Senior Software Engineer.
這是一份針對資深軟體工程師量身打造的 **進階樹結構（Advanced Trees）** 完整教材。

---

# Advanced Trees: Interview & Practical Guide
# 進階樹結構：面試與實戰指南

## 1. Learning Objectives (學習目標)

1.  **Master Tree Dynamic Programming (Tree DP):** Learn how to pass states bottom-up to solve complex path or structure optimization problems (e.g., Maximum Path Sum).
    **掌握樹形動態規劃（Tree DP）：** 學習如何由下而上（bottom-up）傳遞狀態，以解決複雜的路徑或結構優化問題（例如：最大路徑和）。

2.  **Handle Serialization & Deserialization:** Understand how to convert tree structures into linear formats for storage or transmission, a bridge between algorithms and system design.
    **處理序列化與反序列化：** 理解如何將樹結構轉換為線性格式以進行儲存或傳輸，這是連接演算法與系統設計的橋樑。

3.  **Optimize Space Complexity:** Move beyond standard recursion to understand iterative approaches and Morris Traversal for O(1) space requirements.
    **優化空間複雜度：** 超越標準遞迴，理解迭代解法與 Morris Traversal 以達到 O(1) 的空間要求。

4.  **Deepen LCA (Lowest Common Ancestor) Understanding:** Solve LCA variations efficiently without parent pointers.
    **深化最近共同祖先（LCA）的理解：** 在沒有父節點指針的情況下高效解決 LCA 的變體問題。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition & Intuition (定義與直覺)
In advanced scenarios, a Tree is not just a data structure for traversal, but a dependency graph where sub-problems (subtrees) contribute to the global solution.
在進階場景中，樹不僅是用於遍歷的資料結構，更是一個依賴圖，其中子問題（子樹）對全域解做出貢獻。

For Senior Engineers, the focus shifts from "how to visit nodes" to "what information to aggregate from children."
對資深工程師而言，焦點從「如何訪問節點」轉移到「從子節點聚合什麼資訊」。

### Complexity (複雜度)
- **Time:** Generally $O(N)$, where $N$ is the number of nodes. We must visit every node at least once.
  **時間：** 通常為 $O(N)$，其中 $N$ 是節點數。我們必須至少訪問每個節點一次。
- **Space:** $O(H)$ for recursion stack, where $H$ is height.
  **空間：** 遞迴堆疊需要 $O(H)$，其中 $H$ 是高度。
  - Balanced Tree: $O(\log N)$.
    平衡樹：$O(\log N)$。
  - Skewed Tree (Worst Case): $O(N)$.
    歪斜樹（最差情況）：$O(N)$。

### When to Use / Not Use (適用與不適用場景)
- **Use:** Hierarchical data, decision processes, parsing expressions, and problems requiring recursive sub-structure optimization.
  **適用：** 層級資料、決策過程、解析表達式，以及需要遞迴子結構優化的問題。
- **Not Use:** When data has cycles (use Graph), or when simple linear access is required (use Array/List for cache locality).
  **不適用：** 當資料有環時（使用圖），或需要簡單線性存取時（使用陣列/列表以獲得快取局部性）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Bottom-Up DFS (Post-order Traversal) / Tree DP
**Pattern:** Process children first, return a value to the parent, and update a global maximum/result simultaneously.
**模式：** 先處理子節點，將值返回給父節點，同時更新全域最大值/結果。
*Used in: Diameter of Tree, Max Path Sum, Check Balanced.*
*適用於：樹的直徑、最大路徑和、檢查平衡性。*

### B. Top-Down DFS (Pre-order Traversal)
**Pattern:** Pass constraints or path history from parent to children.
**模式：** 將限制條件或路徑歷史從父節點傳遞給子節點。
*Used in: Validate BST, Path Sum (Root to Leaf).*
*適用於：驗證二元搜尋樹、路徑和（根到葉）。*

### C. Level Order Traversal (BFS)
**Pattern:** Use a Queue to process nodes layer by layer.
**模式：** 使用佇列（Queue）逐層處理節點。
*Used in: Tree Serialization, Right Side View, Shortest Path in Tree.*
*適用於：樹的序列化、右視圖、樹中的最短路徑。*

### D. Trie (Prefix Tree)
**Pattern:** N-ary tree optimized for string prefix operations.
**模式：** 針對字串前綴操作優化的 N 元樹。
*Used in: Autocomplete, Word Search II.*
*適用於：自動補全、單詞搜尋 II。*

---

## 4. Example Walkthrough (範例講解)

### Problem: Binary Tree Maximum Path Sum (Hard)
### 問題：二元樹的最大路徑和（困難）

**Problem Statement:**
Given the `root` of a binary tree, return the maximum path sum of any non-empty path.
給定二元樹的 `root`，返回任意非空路徑的最大路徑和。
A path does not need to pass through the root.
路徑不需要經過根節點。

**Example:**
Input: `[-10, 9, 20, 15, 7]` (Tree structure)
Output: `42` (Path: 15 -> 20 -> 7)

---

### Thought Process (思路)

#### 1. Brute Force (暴力解)
Iterate through every node, and for each node, calculate the max path passing through it.
遍歷每個節點，並針對每個節點計算經過它的最大路徑。
*Drawback:* Extremely inefficient ($O(N^2)$) because path calculations overlap.
*缺點：* 極度低效（$O(N^2)$），因為路徑計算會重疊。

#### 2. Optimization Strategy (優化策略 - Tree DP)
We need a **Bottom-Up** approach.
我們需要一個 **由下而上** 的方法。
For any node `u`, the "max path passing through `u`" (which could be the global answer) is:
對於任意節點 `u`，「經過 `u` 的最大路徑」（可能是全域答案）是：
`u.val + max(left_gain, 0) + max(right_gain, 0)`

However, to its **parent**, node `u` can only contribute **one** side (it cannot branch back down).
然而，對於它的 **父節點**，節點 `u` 只能貢獻 **一邊** 的路徑（它不能分叉向下返回）。
Return value to parent: `u.val + max(left_gain, right_gain, 0)`

#### 3. Complexity (複雜度)
- **Time:** $O(N)$ - We visit each node exactly once.
  **時間：** $O(N)$ - 我們恰好訪問每個節點一次。
- **Space:** $O(H)$ - Recursion stack.
  **空間：** $O(H)$ - 遞迴堆疊。

---

### Java Reference Solution (Java 參考解)

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
    // Global variable to store the maximum path sum found so far.
    // Use Integer.MIN_VALUE to handle trees with all negative numbers.
    // 全域變數，用於儲存目前找到的最大路徑和。
    // 使用 Integer.MIN_VALUE 以處理全為負數的樹。
    private int globalMaxSum = Integer.MIN_VALUE;

    public int maxPathSum(TreeNode root) {
        calculateMaxGain(root);
        return globalMaxSum;
    }

    /**
     * Helper function: Post-order traversal.
     * Returns the max path sum starting from 'node' and going down one branch (left or right).
     * 輔助函數：後序遍歷。
     * 返回從 'node' 開始並向下走一條分支（左或右）的最大路徑和。
     */
    private int calculateMaxGain(TreeNode node) {
        // Base case: If node is null, the gain is 0.
        // 基本情況：如果節點為空，增益為 0。
        if (node == null) {
            return 0;
        }

        // Recursive step: Calculate max gain from left and right subtrees.
        // If a subtree gain is negative, we ignore it (take 0).
        // 遞迴步驟：計算左子樹和右子樹的最大增益。
        // 如果子樹增益為負，我們忽略它（取 0）。
        int leftGain = Math.max(calculateMaxGain(node.left), 0);
        int rightGain = Math.max(calculateMaxGain(node.right), 0);

        // Current path sum including both left and right children (the "arch" path).
        // This is a candidate for the global answer.
        // 包含左右子節點的當前路徑和（"拱形"路徑）。
        // 這是全域答案的候選者。
        int currentPathSum = node.val + leftGain + rightGain;

        // Update the global maximum.
        // 更新全域最大值。
        globalMaxSum = Math.max(globalMaxSum, currentPathSum);

        // Return value: The node can only extend the path to its parent via ONE branch.
        // Choose the larger one between left and right.
        // 返回值：該節點只能通過「一條」分支將路徑延伸至其父節點。
        // 選擇左右之間較大的一個。
        return node.val + Math.max(leftGain, rightGain);
    }
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Path vs. Height** | **Pitfall:** Confusing the value returned to the parent (single branch) with the value used to update the global max (double branch).<br>**陷阱：** 混淆「返回給父節點的值（單分支）」與「用於更新全域最大值的值（雙分支）」。 |
| **Negative Values** | **Pitfall:** Forgetting that path sums can be negative. Initializing `max` to 0 instead of `Integer.MIN_VALUE` will fail for trees like `[-3]`.<br>**陷阱：** 忘記路徑和可能為負。將 `max` 初始化為 0 而非 `Integer.MIN_VALUE` 會導致像 `[-3]` 這樣的樹出錯。 |
| **Global vs. Local** | **Pitfall:** Trying to pass the global maximum as a recursive parameter without a wrapper class (Java passes primitives by value).<br>**陷阱：** 試圖將全域最大值作為遞迴參數傳遞，但未使用的包裝類別（Java 傳遞基本型別是傳值）。 |
| **Null Handling** | **Pitfall:** Accessing `node.left` without checking `node != null`.<br>**陷阱：** 在未檢查 `node != null` 的情況下存取 `node.left`。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify:** "Does the path have to start at the root?" "Can node values be negative?"
    **釐清：** 「路徑必須從根節點開始嗎？」「節點值可以是負數嗎？」
2.  **Define Recursion:** "I will use a helper function that returns the max gain a subtree can contribute to its parent."
    **定義遞迴：** 「我將使用一個輔助函數，返回子樹能貢獻給其父節點的最大增益。」
3.  **State Management:** "I'll keep a global variable to track the maximum path found *within* the recursion."
    **狀態管理：** 「我會保留一個全域變數來追蹤遞迴過程*內部*發現的最大路徑。」

### Whiteboard Strategy (白板策略)
- Draw a small tree (3 nodes) to visualize the "split" (left + root + right) vs. the "return" (root + max(left, right)).
  畫一個小樹（3 個節點）來視覺化「分叉」（左+根+右）與「返回」（根+max(左, 右)）的區別。
- Write the function signature clearly first.
  先清楚寫下函數簽名。

### Common Follow-ups (常見追問)
- **Q:** How to print the actual path?
  **問：** 如何印出實際路徑？
  *A: Store parent pointers or re-traverse using the optimal values.*
  *答：儲存父節點指針，或使用最佳值重新遍歷。*
- **Q:** What if it's an N-ary tree?
  **問：** 如果是 N 元樹怎麼辦？
  *A: Sort children gains, take the top 2 for the internal path, return top 1 to parent.*
  *答：對子節點增益排序，取前兩名作為內部路徑，返回第一名給父節點。*

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Diameter of Binary Tree** (LeetCode 543)
**Hint:** Similar to Max Path Sum, but counting edges instead of node values.
**提示：** 類似最大路徑和，但計算的是邊數而非節點值。
**Key Logic:** `maxDiameter = max(maxDiameter, leftHeight + rightHeight)`

### Level: Medium (Standard)
**Problem:** **Lowest Common Ancestor of a Binary Tree** (LeetCode 236)
**Hint:** If root is `p` or `q`, return root. If left and right recursions both return non-null, root is the LCA.
**提示：** 如果根是 `p` 或 `q`，返回根。如果左右遞迴都返回非空值，則根即為 LCA。
**Key Logic:** Post-order traversal bubbling up the found nodes.

### Level: Hard (Advanced)
**Problem:** **Serialize and Deserialize Binary Tree** (LeetCode 297)
**Hint:** Use Pre-order traversal with a sentinel value (e.g., "#" or "null") for null nodes.
**提示：** 使用帶有哨兵值（例如 "#" 或 "null"）的前序遍歷來表示空節點。
**Key Logic:**
- Serialize: `sb.append(val).append(",");`
- Deserialize: Use a `Queue` or global index to consume the string tokens recursively.

---

## 8. Quick Checklists (快速檢核表)

### Self-Review during Interview (面試自我審查)
- [ ] **Base Case:** Did I handle `node == null`?
  **基本情況：** 我處理了 `node == null` 嗎？
- [ ] **Return Value:** Does the function return what the *parent* needs (e.g., height/single path) or the *global answer*?
  **返回值：** 函數返回的是*父節點*需要的（如高度/單一路徑），還是*全域答案*？
- [ ] **State Update:** Did I update the global maximum at the right time (usually post-order)?
  **狀態更新：** 我是否在正確的時間（通常是後序）更新了全域最大值？
- [ ] **Complexity:** Is it $O(N)$ time? Is the recursion depth safe?
  **複雜度：** 時間是 $O(N)$ 嗎？遞迴深度安全嗎？

---

## 9. Memory Anchors (記憶錨點)

### The "Manager vs. CEO" Analogy (「經理 vs. CEO」類比)

- **The Recursive Function (Manager):**
  **遞迴函數（經理）：**
  Reports to the boss (parent node). Can only report **one** best result from their department (single branch path).
  向老闆（父節點）匯報。只能匯報其部門中**一個**最好的結果（單分支路徑）。

- **The Global Variable (CEO):**
  **全域變數（CEO）：**
  Observes everything. Can see the internal success of a department (left + root + right) and record it as the company's best record, even if that structure cannot be reported up the chain.
  觀察一切。可以看到部門內部的成功（左+根+右）並將其記錄為公司的最佳紀錄，即使該結構無法向上級匯報。

***

**Final Advice:** For Senior roles, clean code structure (separating helper functions) and handling edge cases (negative values, single node trees) are as important as the algorithm itself.
**最後建議：** 對於資深職位，乾淨的程式碼結構（分離輔助函數）與處理邊界情況（負值、單節點樹）與演算法本身同樣重要。