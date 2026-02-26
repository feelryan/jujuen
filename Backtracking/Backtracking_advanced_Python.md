# Advanced Backtracking for Senior Engineers
# 給資深工程師的進階回溯法 (Backtracking) 指南

## 1. Learning Objectives (學習目標)

1.  **Master State Space Pruning:** Learn to identify "dead ends" early to drastically reduce the search space.
    **掌握狀態空間剪枝：** 學習如何儘早識別「死胡同」，以大幅縮減搜尋空間。
2.  **Optimize State Representation:** Move beyond simple arrays/lists to using Bitmasks or Hash Maps for $O(1)$ constraint checking.
    **優化狀態表示：** 超越簡單的陣列/列表，轉而使用位元遮罩 (Bitmasks) 或雜湊表來進行 $O(1)$ 的限制檢查。
3.  **Distinguish Permutations vs. Combinations:** deeply understand how loop start indices (`start_index`) affect the result set (ordered vs. unordered).
    **區分排列與組合：** 深刻理解迴圈起始索引 (`start_index`) 如何影響結果集（有序與無序）。
4.  **Analyze Exponential Complexity:** Articulate time complexity for NP-hard problems clearly (e.g., $O(N!)$ vs $O(2^N)$).
    **分析指數複雜度：** 清晰地闡述 NP-hard 問題的時間複雜度（例如 $O(N!)$ 對比 $O(2^N)$）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time, removing those solutions that fail to satisfy the constraints of the problem at any point of time.
回溯法是一種遞迴演算法技術，透過一次構建一部分的方式逐步嘗試建立解，並在任何時間點移除那些無法滿足問題限制的解。

### Intuition (直覺)
Think of it as a Depth-First Search (DFS) on a "State Space Tree."
將其視為在「狀態空間樹」上進行的深度優先搜尋 (DFS)。
You explore a path until you reach a valid solution (leaf) or violate a constraint (dead end), then you "backtrack" to the previous decision point.
你沿著一條路徑探索，直到找到有效解（葉節點）或違反限制（死胡同），然後「回溯」到上一個決策點。

### Complexity (複雜度)
*   **Time:** Usually exponential or factorial. e.g., $O(k^N)$ for subsets, $O(N!)$ for permutations.
    **時間：** 通常是指數級或階乘級。例如：子集問題為 $O(k^N)$，排列問題為 $O(N!)$。
*   **Space:** $O(N)$ for the recursion stack, where $N$ is the depth of the tree.
    **空間：** $O(N)$ 用於遞迴堆疊，其中 $N$ 是樹的深度。

### When to Use (適用場景)
*   **Combinatorial Problems:** Find *all* permutations, combinations, or subsets.
    **組合問題：** 尋找*所有*排列、組合或子集。
*   **Constraint Satisfaction:** Sudoku, N-Queens, Crossword puzzles.
    **滿足限制問題：** 數獨、八皇后、填字遊戲。

### When NOT to Use (不適用場景)
*   **Optimization (Max/Min):** If you only need the *best* value (not all paths), Dynamic Programming or Greedy is usually preferred due to overlapping subproblems.
    **最佳化（最大/最小）：** 如果你只需要*最佳*數值（而非所有路徑），由於存在重疊子問題，動態規劃 (DP) 或貪婪演算法 (Greedy) 通常更佳。

---

## 3. Typical Patterns (典型題型 / 模式)

| Pattern (模式) | Description (描述) | Key Logic (關鍵邏輯) |
| :--- | :--- | :--- |
| **Combinations / Subsets** | Choose $k$ items from $N$. Order doesn't matter. <br> 從 $N$ 個項目中選 $k$ 個。順序不重要。 | Use `start_index` to avoid duplicates (forward only). <br> 使用 `start_index` 避免重複（僅向後選）。 |
| **Permutations** | Arrange $N$ items. Order matters. <br> 排列 $N$ 個項目。順序重要。 | Use a `used` array or swap elements to track usage. <br> 使用 `used` 陣列或交換元素來追蹤使用情況。 |
| **Grid Traversal (DFS)** | Find paths in a 2D grid (e.g., Word Search). <br> 在 2D 網格中尋找路徑（如：文字搜尋）。 | Mark cell as visited before recursion, unmark after. <br> 遞迴前標記格子為已訪問，遞迴後取消標記。 |
| **Constraint Satisfaction** | Fill blanks subject to rules (Sudoku, N-Queens). <br> 根據規則填空（數獨、八皇后）。 | `isValid()` check before diving deeper. <br> 在深入搜尋前進行 `isValid()` 檢查。 |

---

## 4. Example Walkthrough (範例講解)

### Problem: N-Queens II (Optimized with Bitmasking)
### 問題：N-Queens II（使用位元遮罩優化）

**Problem Statement:**
The **n-queens** puzzle is the problem of placing `n` queens on an `n x n` chessboard such that no two queens attack each other. Given an integer `n`, return *the number of distinct solutions*.
**n 皇后**謎題是將 `n` 個皇后放置在 `n x n` 的棋盤上，使得沒有兩個皇后互相攻擊。給定整數 `n`，返回*不同解的數量*。

### Approach (思路)

1.  **Naive (暴力法):** Place queens one by one. For each placement, iterate the whole board to check conflicts.
    **Naive (暴力法):** 逐一放置皇后。每次放置時，遍歷整個棋盤檢查衝突。
    *   *Critique:* Checking takes $O(N)$, total $O(N \cdot N!)$. Too slow.
    *   *評論：* 檢查耗時 $O(N)$，總計 $O(N \cdot N!)$。太慢。

2.  **Intermediate (Sets):** Use three Sets to track occupied columns, diagonals (`row - col`), and anti-diagonals (`row + col`).
    **中階 (集合):** 使用三個 Set 來追蹤被佔用的列 (cols)、主對角線 (`row - col`) 和副對角線 (`row + col`)。
    *   *Improvement:* Checking becomes $O(1)$. Total $O(N!)$.
    *   *改進：* 檢查變為 $O(1)$。總計 $O(N!)$。

3.  **Advanced (Bitmasking):** Since $N$ is usually small ($N \le 16$), we can use integers as bitmasks to represent the board state. This reduces overhead and improves cache locality.
    **進階 (位元遮罩):** 由於 $N$ 通常很小 ($N \le 16$)，我們可以使用整數作為位元遮罩來表示棋盤狀態。這減少了開銷並提升了快取局部性。

### Python Solution (Bitmask Optimization)

```python
class Solution:
    def totalNQueens(self, n: int) -> int:
        # Counter for valid solutions
        # 有效解的計數器
        self.count = 0
        
        # The mask implies all bits are 1 for size n. e.g., n=4 -> 1111 (binary)
        # 遮罩意味著大小為 n 的所有位元皆為 1。例如 n=4 -> 1111 (二進位)
        full_mask = (1 << n) - 1
        
        def backtrack(row: int, cols: int, diags: int, anti_diags: int):
            """
            row: current row index (當前列索引)
            cols: bitmask of occupied columns (被佔用行的位元遮罩)
            diags: bitmask of occupied diagonals (被佔用主對角線的位元遮罩)
            anti_diags: bitmask of occupied anti-diagonals (被佔用副對角線的位元遮罩)
            """
            # Base Case: If all rows are filled, we found a solution
            # 終止條件：如果所有列都填滿，我們找到了一個解
            if row == n:
                self.count += 1
                return

            # Available positions are where NO constraints exist.
            # ~(cols | diags | anti_diags) gives 1s at available spots (but infinite 1s to the left).
            # & full_mask truncates it to just N bits.
            # 可用位置是沒有限制的地方。
            # ~(cols | diags | anti_diags) 在可用位置給出 1（但左側有無窮個 1）。
            # & full_mask 將其截斷為僅 N 個位元。
            available_positions = ~(cols | diags | anti_diags) & full_mask
            
            while available_positions:
                # Extract the lowest set bit (standard bit hack: x & -x)
                # 取出最低位的 1（標準位元操作技巧：x & -x）
                position = available_positions & -available_positions
                
                # Remove this position from available set to process next
                # 從可用集合中移除此位置以便處理下一個
                available_positions &= available_positions - 1
                
                # Recurse to next row:
                # 1. cols | position: mark column as taken
                # 2. (diags | position) << 1: shift diagonal constraints to the left for next row
                # 3. (anti_diags | position) >> 1: shift anti-diagonal constraints to the right for next row
                # 遞迴至下一列：
                # 1. cols | position: 標記該行已被佔用
                # 2. (diags | position) << 1: 將主對角線限制左移以對應下一列
                # 3. (anti_diags | position) >> 1: 將副對角線限制右移以對應下一列
                backtrack(
                    row + 1,
                    cols | position,
                    (diags | position) << 1,
                    (anti_diags | position) >> 1
                )

        # Start from row 0 with empty constraints
        # 從第 0 列開始，沒有任何限制
        backtrack(0, 0, 0, 0)
        return self.count

# Complexity Analysis:
# Time: O(N!) - We try to place queens, but the branching factor decreases (N, N-1, N-2...).
# Space: O(N) - Recursion stack depth.
# 複雜度分析：
# 時間：O(N!) - 我們嘗試放置皇后，但分支因子會遞減 (N, N-1, N-2...)。
# 空間：O(N) - 遞迴堆疊深度。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake (錯誤) | Correct Approach (正確做法) |
| :--- | :--- | :--- |
| **Mutable State** <br> **可變狀態** | Appending a list to the result without copying: `res.append(path)`. <br> 將列表加入結果時未複製：`res.append(path)`。 | Always copy the mutable object: `res.append(path[:])` or `path.copy()`. <br> 始終複製可變物件：`res.append(path[:])` 或 `path.copy()`。 |
| **Backtracking Step** <br> **回溯步驟** | Forgetting to `pop()` or unmark visited after the recursive call. <br> 忘記在遞迴呼叫後執行 `pop()` 或取消標記。 | Symmetry is key: **Do** $\to$ **Recurse** $\to$ **Undo**. <br> 對稱性是關鍵：**執行** $\to$ **遞迴** $\to$ **撤銷**。 |
| **Duplicates** <br> **重複項** | In problems like "Subsets II" (with duplicate inputs), generating duplicate subsets. <br> 在「子集 II」（有重複輸入）等問題中，生成了重複的子集。 | Sort input first. Skip if `nums[i] == nums[i-1]` within the same recursion level. <br> 先排序輸入。若在同一遞迴層級中 `nums[i] == nums[i-1]` 則跳過。 |
| **Loop Range** <br> **迴圈範圍** | Using `range(0, n)` for combinations. <br> 在組合問題中使用 `range(0, n)`。 | For combinations, use `range(start_index, n)` to avoid reusing previous elements/permutations. <br> 對於組合，使用 `range(start_index, n)` 以避免重複使用先前的元素/排列。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. The "Template" Pitch (口條框架)
Start by identifying the problem type.
從識別問題類型開始。
> "This problem asks for all possible combinations/permutations, which suggests an exhaustive search. I will use Backtracking to explore the state space tree."
> 「這個問題要求所有可能的組合/排列，這暗示需要窮舉搜尋。我將使用回溯法來探索狀態空間樹。」

### 2. Whiteboard Strategy (白板策略)
*   **Draw the Tree:** Don't just write code. Draw a small decision tree (e.g., for input `[1, 2, 3]`) to show the interviewer you understand the recursion flow.
    **畫出樹狀圖：** 不要只寫程式碼。畫一個小的決策樹（例如輸入 `[1, 2, 3]`），向面試官展示你理解遞迴流程。
*   **Define State:** Explicitly write down what arguments your helper function needs (e.g., `index`, `current_path`, `visited`).
    **定義狀態：** 明確寫下你的輔助函數需要哪些參數（例如 `index`, `current_path`, `visited`）。

### 3. Common Follow-ups (常見追問)
*   **"Can you optimize space?"** (Suggest iterative backtracking or bitmasks).
    **「你能優化空間嗎？」**（建議迭代回溯或位元遮罩）。
*   **"What if N is large?"** (Discuss heuristics, pruning, or switching to randomized algorithms like Simulated Annealing if an exact solution isn't strictly required or is impossible).
    **「如果 N 很大怎麼辦？」**（討論啟發式算法、剪枝，或者如果不需要精確解/不可能求精確解時，轉向模擬退火等隨機算法）。

---

## 7. Practice Problems (練習題)

### Level: Easy (Warm-up)
**Problem:** **Generate Parentheses** (LeetCode 22)
**Hint:** Track `open` and `close` counts. Only add `(` if `open < n`. Only add `)` if `close < open`.
**提示：** 追蹤 `open` 和 `close` 的數量。只有當 `open < n` 時才加 `(`。只有當 `close < open` 時才加 `)`。

### Level: Medium (Standard)
**Problem:** **Palindrome Partitioning** (LeetCode 131)
**Hint:** The loop iterates through possible cut points. Check if `s[start:i+1]` is a palindrome. If yes, recurse on `s[i+1:]`.
**提示：** 迴圈遍歷可能的切割點。檢查 `s[start:i+1]` 是否為回文。如果是，則對 `s[i+1:]` 進行遞迴。

### Level: Advanced (Differentiation)
**Problem:** **Word Search II** (LeetCode 212) - *Backtracking + Trie*
**Description:** Find all words from a dictionary in a 2D board.
**描述：** 在 2D 棋盤中找出字典裡的所有單字。
**Strategy:**
1.  Build a **Trie** from the dictionary to prune invalid prefixes early.
    從字典建立 **Trie（字典樹）** 以儘早剪除無效前綴。
2.  DFS from every cell. If the current character path doesn't exist in the Trie, stop immediately (Pruning).
    從每個格子進行 DFS。如果當前的字元路徑不存在於 Trie 中，立即停止（剪枝）。
3.  **Optimization:** Remove "leaf" nodes from Trie once a word is found to avoid re-finding it.
    **優化：** 一旦找到單字，從 Trie 中移除「葉」節點以避免重複尋找。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

- [ ] **Base Case:** Does the recursion terminate correctly? (e.g., `index == n` or `sum == target`)
    **終止條件：** 遞迴是否正確終止？（例如 `index == n` 或 `sum == target`）
- [ ] **State Restoration:** Do I pop/remove the element after the recursive call?
    **狀態還原：** 我是否在遞迴呼叫後彈出/移除了該元素？
- [ ] **Deep Copy:** Am I adding a copy of the list to the result, not the reference?
    **深拷貝：** 我加入結果的是列表的副本，而不是參照嗎？
- [ ] **Pruning:** Did I add conditions to skip invalid branches early?
    **剪枝：** 我是否加入了條件以儘早跳過無效分支？
- [ ] **Complexity:** Can I explain why it's $O(2^N)$ or $O(N!)$?
    **複雜度：** 我能解釋為什麼是 $O(2^N)$ 或 $O(N!)$ 嗎？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Dr. Strange" Analogy (奇異博士類比)
Backtracking is like Dr. Strange in *Infinity War* viewing 14 million possible futures.
回溯法就像《無限之戰》中的奇異博士查看 1,400 萬種可能的未來。
*   He goes down a timeline (path).
    他沿著一條時間線（路徑）走下去。
*   If everyone dies (constraint violation), he reverses time (backtracks) to the decision point.
    如果大家都死了（違反限制），他會倒轉時間（回溯）到決策點。
*   He tries a different action until he finds the one winning path (solution).
    他嘗試不同的行動，直到找到那條唯一的勝利路徑（解）。

### The "Maze with a String" (帶線走迷宮)
Imagine exploring a dark maze with a ball of string (Ariadne's thread).
想像帶著一團線（阿麗阿德涅之線）探索黑暗迷宮。
*   **Lay string:** Make a choice (recurse).
    **放線：** 做決定（遞迴）。
*   **Hit wall:** Invalid state.
    **撞牆：** 無效狀態。
*   **Roll up string:** Backtrack to the junction.
    **收線：** 回溯到交叉路口。