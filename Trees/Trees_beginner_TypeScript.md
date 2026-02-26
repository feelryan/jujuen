# Module: Trees (Beginner)
# 模組：樹（初級）

## 1. Learning Objectives (學習目標)

1.  **Master Recursive Thinking & The Call Stack:**
    掌握遞迴思維與呼叫堆疊：Understand how system stack handles tree traversal and how to calculate space complexity based on tree height.
    理解系統堆疊如何處理樹的遍歷，以及如何根據樹的高度計算空間複雜度。
2.  **Proficiency in Basic Traversals (DFS & BFS):**
    熟練基本遍歷（深度優先與廣度優先）：Implement Pre-order, In-order, Post-order, and Level-order traversals without hesitation.
    毫不猶豫地實作前序、中序、後序以及層序遍歷。
3.  **Handling Edge Cases & Null Safety:**
    處理邊界情況與 Null 安全：Develop a reflex for checking `null` nodes to prevent runtime errors, a common red flag in senior interviews.
    培養檢查 `null` 節點的直覺以防止執行時錯誤，這是資深面試中常見的警訊。

---

## 2. Core Concepts Snapshot (核心觀念速覽)

### Definition (定義)
A Tree is a hierarchical data structure consisting of nodes, where each node has a value and a list of references to children nodes, with no cycles.
樹是一種階層式的資料結構，由節點組成，每個節點包含一個數值以及指向子節點的參考列表，且不存在迴圈。

### Intuition (直覺)
Think of the DOM (Document Object Model) in a browser or a corporate organization chart.
想像瀏覽器中的 DOM（文件物件模型）或公司的組織架構圖。

### Complexity (複雜度)
*   **Time (時間):** $O(N)$ to visit every node.
    訪問每個節點需 $O(N)$。
*   **Space (空間):**
    *   Average/Balanced: $O(\log N)$ (height of the tree).
        平均/平衡情況：$O(\log N)$（樹高）。
    *   Worst Case (Skewed): $O(N)$ (linked list like).
        最差情況（歪斜）：$O(N)$（像鏈結串列）。

### When to Use (適用場景)
*   Representing hierarchical data (File systems, HTML).
    表示階層數據（檔案系統、HTML）。
*   Fast search and sorting (Binary Search Trees, Heaps - covered in intermediate).
    快速搜尋與排序（二元搜尋樹、堆積 - 中級課程涵蓋）。

### When NOT to Use (不適用場景)
*   Data with cycles or many-to-many relationships (Use a Graph).
    具備迴圈或多對多關係的數據（請使用圖）。
*   Simple linear access is required (Use Array or Linked List).
    需要簡單線性存取時（請使用陣列或鏈結串列）。

---

## 3. Typical Patterns (典型題型 / 模式)

For beginner tree problems, almost all solutions fall into two buckets:
對於初級樹題目，幾乎所有解法都歸類為兩類：

### A. Depth-First Search (DFS) - Recursion
**Concept:** Dive as deep as possible before backtracking.
**觀念：** 在回溯前盡可能深入挖掘。
*   **Pre-order (Root, Left, Right):** Copying trees, prefix expression.
    **前序（根、左、右）：** 複製樹、前綴表達式。
*   **In-order (Left, Root, Right):** BST validation, sorted output.
    **中序（左、根、右）：** BST 驗證、排序輸出。
*   **Post-order (Left, Right, Root):** Deleting trees, calculating height (bottom-up).
    **後序（左、右、根）：** 刪除樹、計算高度（由下而上）。

### B. Breadth-First Search (BFS) - Queue
**Concept:** Process level by level.
**觀念：** 逐層處理。
*   **Pattern:** Use a `Queue` (array in JS/TS) to store nodes to visit.
    **模式：** 使用 `Queue`（JS/TS 中的陣列）來儲存待訪問節點。
*   **Use Case:** Shortest path in unweighted graphs/trees, level-order printing.
    **用途：** 無權重圖/樹的最短路徑、層序列印。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum Depth of Binary Tree
### 問題：二元樹的最大深度

**Problem Statement:**
Given the root of a binary tree, return its maximum depth.
給定二元樹的根節點，回傳其最大深度。

**Intuition (思路):**
*   **Brute Force/Naïve:** Not applicable here, traversal is necessary.
    **暴力法/樸素法：** 此處不適用，必須遍歷。
*   **Optimization (DFS):** The depth of a node is `1 + max(depth of left child, depth of right child)`. This suggests a post-order traversal (bottom-up).
    **優化（DFS）：** 節點的深度是 `1 + max(左子樹深度, 右子樹深度)`。這暗示了後序遍歷（由下而上）。

**Complexity:**
*   Time: $O(N)$ - we visit each node once.
    時間：$O(N)$ - 我們訪問每個節點一次。
*   Space: $O(H)$ - recursion stack depends on height.
    空間：$O(H)$ - 遞迴堆疊取決於高度。

### TypeScript Implementation (TypeScript 實作)

First, let's define the standard Tree Node interface.
首先，我們定義標準的樹節點介面。

```typescript
/**
 * Definition for a binary tree node.
 * 二元樹節點的定義。
 */
class TreeNode {
    val: number;
    left: TreeNode | null;
    right: TreeNode | null;
    
    constructor(val?: number, left?: TreeNode | null, right?: TreeNode | null) {
        this.val = (val === undefined ? 0 : val);
        this.left = (left === undefined ? null : left);
        this.right = (right === undefined ? null : right);
    }
}
```

#### Incorrect Approach (Common Mistake)
#### 錯誤示範（常見錯誤）

```typescript
function maxDepthWrong(root: TreeNode | null): number {
    // Mistake: Not handling the null case immediately causes a crash or wrong logic.
    // 錯誤：沒有立即處理 null 情況會導致崩潰或邏輯錯誤。
    if (!root) return 0; // This is correct, but let's see the logic error below.
                         // 這行是對的，但我們看下面的邏輯錯誤。
    
    // Mistake: Trying to access properties without checking existence in a complex way
    // or forgetting to add 1 for the current level.
    // 錯誤：以複雜的方式存取屬性而未檢查存在性，或忘記為當前層級加 1。
    
    let leftD = maxDepthWrong(root.left);
    let rightD = maxDepthWrong(root.right);
    
    // If we forget +1, the result is always 0.
    // 如果我們忘記 +1，結果永遠是 0。
    return Math.max(leftD, rightD); 
}
```

#### Best Solution (DFS - Recursion)
#### 最佳解（DFS - 遞迴）

```typescript
function maxDepth(root: TreeNode | null): number {
    // Base Case: If the node is null, depth is 0.
    // 基本情況：如果節點為 null，深度為 0。
    if (root === null) {
        return 0;
    }

    // Recursive Step: Calculate depth of left and right subtrees.
    // 遞迴步驟：計算左子樹與右子樹的深度。
    const leftDepth = maxDepth(root.left);
    const rightDepth = maxDepth(root.right);

    // Logic: The depth of current node is max of children + 1 (self).
    // 邏輯：當前節點的深度是子節點最大值 + 1（自己）。
    return Math.max(leftDepth, rightDepth) + 1;
}
```

#### Alternative Solution (BFS - Iterative)
#### 替代解法（BFS - 迭代）

This is useful if the interviewer asks to avoid recursion (stack overflow risk).
如果面試官要求避免遞迴（堆疊溢位風險），這很有用。

```typescript
function maxDepthIterative(root: TreeNode | null): number {
    if (!root) return 0;

    // Use an array as a queue.
    // 使用陣列作為佇列。
    const queue: TreeNode[] = [root];
    let depth = 0;

    while (queue.length > 0) {
        // Capture the size of the current level.
        // 捕捉當前層級的大小。
        const levelSize = queue.length;
        
        // Process all nodes at this level.
        // 處理該層級的所有節點。
        for (let i = 0; i < levelSize; i++) {
            const node = queue.shift()!; // Non-null assertion safe here.
            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }
        
        // Increment depth after finishing a level.
        // 完成一層後增加深度。
        depth++;
    }

    return depth;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (觀念) | Pitfall / Distinction (陷阱 / 區別) |
| :--- | :--- |
| **Height vs. Depth**<br>(高度 vs. 深度) | **Depth**: Edges from root to node (Top-down). **Height**: Edges from node to deepest leaf (Bottom-up).<br>**深度**：從根到節點的邊數（由上而下）。**高度**：從節點到最深葉子的邊數（由下而上）。 |
| **Null Checks**<br>(Null 檢查) | Accessing `root.left` without checking `if (root)` is the #1 reason for interview failure.<br>在未檢查 `if (root)` 的情況下存取 `root.left` 是面試失敗的第一大原因。 |
| **Stack Overflow**<br>(堆疊溢位) | In a skewed tree (linked list), recursion depth is $N$. Mention this risk to show seniority.<br>在歪斜樹（鏈結串列）中，遞迴深度為 $N$。提及此風險以展現資深程度。 |
| **Leaf Node**<br>(葉節點) | A node is a leaf only if `!node.left && !node.right`. Don't just check one side.<br>只有當 `!node.left && !node.right` 時才是葉節點。不要只檢查一邊。 |

---

## 6. Interview Strategy (面試實戰建議)

### Clarification Phase (釐清階段)
*   **Ask:** "Can the tree be `null`?" (Usually yes).
    **問：**「樹可以是 `null` 嗎？」（通常可以）。
*   **Ask:** "Is the tree balanced? Or can it be skewed?" (Affects complexity analysis).
    **問：**「樹是平衡的嗎？還是可能是歪斜的？」（影響複雜度分析）。
*   **Ask:** "What is the node value range?" (Important for sum/overflow problems).
    **問：**「節點數值範圍為何？」（對總和/溢位問題很重要）。

### Whiteboard Strategy (白板策略)
1.  **Draw a small tree:** 3 levels max. Visualizing helps you trace the recursion.
    **畫一棵小樹：** 最多 3 層。視覺化有助於你追蹤遞迴。
2.  **Write the Base Case first:** Before writing logic, write `if (!root) return ...`.
    **先寫基本情況：** 在寫邏輯之前，先寫 `if (!root) return ...`。
3.  **Speak the traversal:** "I will perform a post-order traversal to bubble up the values."
    **口述遍歷方式：**「我將執行後序遍歷將數值向上傳遞。」

### Common Follow-ups (常見追問)
*   "How would you solve this without recursion?" (Implement BFS or Iterative DFS with stack).
    「如果不使用遞迴，你會如何解決？」（實作 BFS 或使用堆疊的迭代 DFS）。
*   "What if the tree is too large to fit in memory?" (Discuss distributed processing or disk-based storage).
    「如果樹太大無法放入記憶體怎麼辦？」（討論分散式處理或基於磁碟的儲存）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Invert Binary Tree (翻轉二元樹)
*   **Prompt:** Given root, invert the tree (mirror image).
    **題目：** 給定根節點，翻轉整棵樹（鏡像）。
*   **Hint:** Swap left and right children, then recurse.
    **提示：** 交換左右子節點，然後遞迴。
*   **Key Logic:** `[root.left, root.right] = [invert(root.right), invert(root.left)]`.

### 2. Medium (Beginner Tree Level): Symmetric Tree (對稱樹)
*   **Prompt:** Check if a tree is a mirror of itself.
    **題目：** 檢查一棵樹是否為自身的鏡像。
*   **Hint:** You need a helper function `isMirror(t1, t2)`.
    **提示：** 你需要一個輔助函式 `isMirror(t1, t2)`。
*   **Key Logic:** `t1.val === t2.val` AND `isMirror(t1.left, t2.right)` AND `isMirror(t1.right, t2.left)`.

### 3. Hard (Beginner Tree Level): Path Sum (路徑總和)
*   **Prompt:** Return true if the tree has a root-to-leaf path summing to `targetSum`.
    **題目：** 如果樹中存在一條從根到葉的路徑總和等於 `targetSum`，回傳 true。
*   **Hint:** Subtract node value from target as you go down. Check leaf status.
    **提示：** 向下走時從目標值減去節點值。檢查是否為葉節點。
*   **Key Logic:** Base case: `if (!root) return false`. Leaf check: `if (!left && !right && val === target) return true`.

---

## 8. Quick Checklists (快速檢核表)

Use this before saying "I'm done" in an interview.
在面試中說「我完成了」之前，使用此表。

*   [ ] **Base Case:** Did I handle `root === null`?
    **基本情況：** 我處理 `root === null` 了嗎？
*   [ ] **Leaf Logic:** Did I handle leaf nodes correctly (if specific logic applies)?
    **葉節點邏輯：** 我是否正確處理了葉節點（如果有特定邏輯）？
*   [ ] **Return Value:** Does every recursive path return a value?
    **回傳值：** 每個遞迴路徑都有回傳值嗎？
*   [ ] **Complexity:** Did I distinguish between Balanced ($O(\log N)$) and Skewed ($O(N)$) space complexity?
    **複雜度：** 我是否區分了平衡 ($O(\log N)$) 與歪斜 ($O(N)$) 的空間複雜度？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Recursion is a "Russian Doll" (Matryoshka):**
    **遞迴是「俄羅斯娃娃」：**
    You open the doll (call function), do something, and find a smaller doll inside (recursive call). You keep going until the doll is solid (base case), then you close them back up (return).
    你打開娃娃（呼叫函式），做些事，發現裡面有個更小的娃娃（遞迴呼叫）。你繼續直到娃娃是實心的（基本情況），然後將它們關回去（回傳）。

*   **BFS is "Water Ripples":**
    **BFS 是「水波紋」：**
    Like throwing a stone in a pond, the search expands equally in all directions (levels) from the center (root).
    就像往池塘丟石頭，搜尋從中心（根）向所有方向（層級）均勻擴展。

*   **The "CEO" Analogy (Post-order):**
    **「CEO」類比（後序）：**
    The CEO (Root) cannot make a decision (calculate height/sum) until they get reports from their VPs (Children). The VPs wait for their Managers. Information flows bottom-up.
    CEO（根）在收到副總裁（子節點）的報告前無法做決定（計算高度/總和）。副總裁等待經理的報告。資訊由下而上流動。