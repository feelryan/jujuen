# Backtracking: The Art of Controlled Brute Force
# 回溯法：受控的暴力搜尋藝術

## 1. Learning Objectives (學習目標)

1.  **Master the General Template**: Internalize the "Choose, Explore, Un-choose" pattern to solve any combinatorial problem without memorizing code.
    **掌握通用模板**：內化「選擇、探索、撤銷」的模式，無需死記硬背程式碼即可解決任何組合類問題。
2.  **Pruning Strategy**: Learn how to identify "dead ends" early to optimize time complexity from impossible to feasible.
    **剪枝策略**：學會如何儘早識別「死胡同」，將時間複雜度從不可行優化為可行。
3.  **State Management**: Understand deep copy vs. shallow copy in Python recursion to avoid common reference bugs.
    **狀態管理**：理解 Python 遞迴中的深拷貝與淺拷貝，以避免常見的參照錯誤（Reference Bugs）。
4.  **Complexity Analysis**: Gain confidence in analyzing factorial $O(N!)$ and exponential $O(2^N)$ complexities.
    **複雜度分析**：建立分析階乘 $O(N!)$ 與指數 $O(2^N)$ 複雜度的信心。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Backtracking is essentially **Depth-First Search (DFS)** on a state-space tree. It builds candidates for the solution incrementally and abandons a candidate ("backtracks") as soon as it determines that the candidate cannot possibly be completed to a valid solution.
回溯法本質上是在狀態空間樹上的 **深度優先搜尋（DFS）**。它逐步建構候選解，並在確定該候選解無法構成有效解時立即放棄（「回溯」）。

### Intuition (直覺)
Imagine walking through a maze. You choose a path; if you hit a wall, you return to the last intersection and try a different path.
想像在迷宮中行走。你選擇一條路徑；如果撞到牆，你退回到上一個路口並嘗試另一條路徑。

### Complexity (複雜度)
-   **Time**: Often $O(N!)$ (Permutations) or $O(2^N)$ (Subsets). It is computationally expensive.
    **時間**：通常為 $O(N!)$（排列）或 $O(2^N)$（子集）。計算成本很高。
-   **Space**: $O(N)$ for the recursion stack, where $N$ is the depth of the tree.
    **空間**：$O(N)$ 用於遞迴堆疊，其中 $N$ 是樹的深度。

### When to Use / Not to Use (適用與不適用場景)
-   **Use when**: You need to find **all** solutions (e.g., all valid parentheses) or **one** valid solution in a constraint satisfaction problem (e.g., Sudoku).
    **適用時機**：你需要找出 **所有** 解（例如：所有合法的括號組合）或約束滿足問題中的 **一個** 有效解（例如：數獨）。
-   **Don't use when**: You need the shortest path (use BFS) or an optimal value (min/max) where overlapping subproblems exist (use Dynamic Programming).
    **不適用時機**：你需要最短路徑（使用 BFS）或存在重疊子問題的最佳值（極大/極小）（使用動態規劃）。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, recognize these three distinct flavors:
對於資深工程師，請識別這三種不同的類型：

1.  **Combinatorial Search (組合搜尋)**
    -   *Subsets, Permutations, Combinations.*
    -   *Focus*: Handling duplicates and ordering.
    -   *重點*：處理重複元素與順序。

2.  **String Partitioning (字串分割)**
    -   *Palindrome Partitioning, IP Address Restoration.*
    -   *Focus*: Where to "cut" the string.
    -   *重點*：在哪裡「切分」字串。

3.  **Grid Traversal (網格遍歷)**
    -   *Word Search, N-Queens, Sudoku.*
    -   *Focus*: Marking visited cells to avoid cycles and un-marking them (backtracking).
    -   *重點*：標記已訪問的單元格以避免循環，並取消標記（回溯）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Combination Sum (組合總和)
**Problem**: Given an array of **distinct** integers `candidates` and a target integer `target`, return a list of all **unique combinations** of `candidates` where the chosen numbers sum to `target`. You may choose the same number an unlimited number of times.
**問題**：給定一個由 **不同** 整數組成的陣列 `candidates` 和一個目標整數 `target`，回傳所有 `candidates` 中數字總和為 `target` 的 **唯一組合** 列表。你可以無限次選擇同一個數字。

### Thought Process (思路)

1.  **Brute Force**: Generate all possible subsets (including duplicates) and check the sum. This leads to infinite recursion since we can reuse numbers.
    **暴力法**：生成所有可能的子集（包括重複）並檢查總和。由於我們可以重複使用數字，這會導致無限遞迴。

2.  **Optimization (Constraint & Pruning)**:
    -   We need a base case: `sum == target` (Success) or `sum > target` (Fail).
    -   To avoid duplicate sets (e.g., `[2, 2, 3]` and `[2, 3, 2]`), we enforce an ordering: once we move past an index `i`, we never look back at it.
    -   **Pruning**: If we sort the candidates, we can stop the loop early if `current_sum + candidate > target`.
    **優化（約束與剪枝）**：
    -   我們需要基本情況：`sum == target`（成功）或 `sum > target`（失敗）。
    -   為了避免重複集合（例如 `[2, 2, 3]` 和 `[2, 3, 2]`），我們強制執行順序：一旦我們移過索引 `i`，就永遠不再回頭看它。
    -   **剪枝**：如果我們對候選數進行排序，當 `current_sum + candidate > target` 時，我們可以提前停止迴圈。

### Python Reference Solution (Python 參考解)

```python
from typing import List

class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        results = []
        # Sorting is crucial for optimization (Pruning)
        # 排序對於優化（剪枝）至關重要
        candidates.sort()
        
        def backtrack(start_index: int, current_path: List[int], current_sum: int):
            # Base Case 1: Goal reached
            # 基本情況 1：達成目標
            if current_sum == target:
                # CRITICAL: Append a copy of the path, not the reference
                # 關鍵：加入路徑的副本，而非參照
                results.append(list(current_path))
                return
            
            # Base Case 2: Exceeded target (Implicitly handled by loop break below, but good for safety)
            # 基本情況 2：超過目標（雖然下方的迴圈中斷已隱式處理，但為了安全起見保留）
            if current_sum > target:
                return

            # Iterate through choices
            # 遍歷選擇
            for i in range(start_index, len(candidates)):
                num = candidates[i]
                
                # Pruning: If adding this number exceeds target, larger numbers will too
                # 剪枝：如果加上這個數字超過目標，更大的數字也會超過
                if current_sum + num > target:
                    break
                
                # Choose (選擇)
                current_path.append(num)
                
                # Explore (探索)
                # We pass 'i' not 'i + 1' because we can reuse the same element
                # 我們傳入 'i' 而非 'i + 1'，因為我們可以重複使用同一個元素
                backtrack(i, current_path, current_sum + num)
                
                # Un-choose / Backtrack (撤銷 / 回溯)
                current_path.pop()

        backtrack(0, [], 0)
        return results
```

### Complexity Analysis (複雜度分析)
-   **Time**: $O(N^{\frac{T}{M}})$, where $N$ is the number of candidates, $T$ is the target value, and $M$ is the minimum value in candidates. This is a loose upper bound. In practice, it's the number of nodes in the search tree.
    **時間**：$O(N^{\frac{T}{M}})$，其中 $N$ 是候選數的數量，$T$ 是目標值，$M$ 是候選數中的最小值。這是一個寬鬆的上界。實際上，它是搜尋樹中的節點數量。
-   **Space**: $O(\frac{T}{M})$ for the recursion stack (longest possible combination).
    **空間**：$O(\frac{T}{M})$ 用於遞迴堆疊（最長可能的組合）。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Mistake / Confusion | Correct Approach |
| :--- | :--- | :--- |
| **Reference Handling** | Appending `path` directly to `results` (e.g., `res.append(path)`). The result will contain empty lists because `path` is mutated later. | Always append a copy: `res.append(path[:])` or `res.append(list(path))`. |
| **參照處理** | 直接將 `path` 加入 `results`（例如 `res.append(path)`）。結果將包含空列表，因為 `path` 稍後會被修改。 | 永遠加入副本：`res.append(path[:])` 或 `res.append(list(path))`。 |
| **Start Index** | Passing `i` vs `i + 1` in the recursive call. | Pass `i` if reuse is allowed. Pass `i + 1` if elements must be unique. |
| **起始索引** | 在遞迴呼叫中傳入 `i` 與 `i + 1` 的混淆。 | 如果允許重複使用，傳入 `i`。如果元素必須唯一，傳入 `i + 1`。 |
| **Pruning Position** | Checking constraints only at the start of the function. | Check constraints inside the `for` loop *before* the recursive call to save stack frames. |
| **剪枝位置** | 僅在函式開頭檢查約束。 | 在 `for` 迴圈內、遞迴呼叫 *之前* 檢查約束，以節省堆疊幀（Stack Frames）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify**: "This looks like a combinatorial problem where we need to explore all valid configurations. I'll use Backtracking."
    **識別**：「這看起來像是一個組合問題，我們需要探索所有有效的配置。我將使用回溯法。」
2.  **Define State**: "I need to keep track of the `current_path`, the `current_sum`, and the `start_index` to handle duplicates."
    **定義狀態**：「我需要追蹤 `current_path`（當前路徑）、`current_sum`（當前總和）以及 `start_index`（起始索引）來處理重複項。」
3.  **Draw the Tree**: Briefly sketch the decision tree on the whiteboard. Show where you prune.
    **畫樹**：在白板上簡要畫出決策樹。展示你在哪裡進行剪枝。

### Whiteboard Strategy (白板策略)
-   Write the helper function (`backtrack` or `dfs`) inside the main function to avoid passing global variables like `res` or `candidates` repeatedly.
    將輔助函式（`backtrack` 或 `dfs`）寫在主函式內部，以避免重複傳遞 `res` 或 `candidates` 等全域變數。

### Common Follow-ups (常見追問)
-   *Q: What if the array contains duplicates?*
    *A: Sort the array first, then inside the loop add: `if i > start_index and candidates[i] == candidates[i-1]: continue`.*
    *問：如果陣列包含重複項怎麼辦？*
    *答：先對陣列排序，然後在迴圈內加入：`if i > start_index and candidates[i] == candidates[i-1]: continue`。*

---

## 7. Practice Problems (練習題)

### 1. Easy: Binary Watch (二進位手錶)
-   **Prompt**: Given `n` LEDs turned on, return all possible times.
    **題目**：給定 `n` 個亮起的 LED，回傳所有可能的時間。
-   **Hint**: Backtrack on the 10 positions (4 hours, 6 minutes).
    **提示**：在 10 個位置（4 個小時，6 個分鐘）上進行回溯。

### 2. Medium: Generate Parentheses (產生括號)
-   **Prompt**: Generate all well-formed parentheses for `n` pairs.
    **題目**：生成 `n` 對所有格式正確的括號。
-   **Hint**: Track `open_count` and `close_count`. Only add `(` if `open < n`. Only add `)` if `close < open`.
    **提示**：追蹤 `open_count` 和 `close_count`。只有當 `open < n` 時才加入 `(`。只有當 `close < open` 時才加入 `)`。

### 3. Hard: Word Search II (單字搜尋 II)
-   **Prompt**: Find all words from a dictionary in a 2D board.
    **題目**：在 2D 版面上找出字典中的所有單字。
-   **Hint**: Pure backtracking is too slow. Combine **Backtracking with a Trie (Prefix Tree)**. Build a Trie from the dictionary, then DFS the board. If a prefix doesn't exist in Trie, prune immediately.
    **提示**：純回溯法太慢。結合 **回溯法與 Trie（前綴樹）**。從字典建立 Trie，然後對版面進行 DFS。如果前綴不存在於 Trie 中，立即剪枝。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

-   [ ] **Base Case**: Does the recursion terminate? (e.g., `index == len` or `sum == target`)
    **基本情況**：遞迴會終止嗎？（例如 `index == len` 或 `sum == target`）
-   [ ] **State Reset**: Did I `pop()` after the recursive call?
    **狀態重置**：我在遞迴呼叫後有執行 `pop()` 嗎？
-   [ ] **Result Copy**: Did I append `path[:]` instead of `path`?
    **結果複製**：我是加入 `path[:]` 而不是 `path` 嗎？
-   [ ] **Pruning**: Did I sort the input (if applicable) to enable early breaking?
    **剪枝**：我有對輸入進行排序（如果適用）以啟用提前中斷嗎？
-   [ ] **Constraints**: Did I handle the `start_index` correctly to avoid duplicate combinations?
    **約束**：我有正確處理 `start_index` 以避免重複組合嗎？

---

## 9. Memory Anchors (記憶錨點)

### The "Ctrl+Z" Metaphor ("Ctrl+Z" 隱喻)
Think of Backtracking as typing a document.
把回溯法想成在打文件。
1.  **Type a character** (Make a choice / `append`).
    **打一個字**（做出選擇 / `append`）。
2.  **Check if it makes sense** (Validate / Recursion).
    **檢查是否合理**（驗證 / 遞迴）。
3.  **Ctrl+Z** (Undo / `pop`).
    **Ctrl+Z**（撤銷 / `pop`）。

### Visual Anchor: The Template (視覺錨點：模板)
Visualize the code structure as a sandwich:
將程式碼結構視覺化為三明治：

```text
      [ Choice ]      <-- Top Bun (上層麵包)
      [ Recurse ]     <-- Meat (肉 / 核心邏輯)
      [ Un-choice ]   <-- Bottom Bun (底層麵包)
```
If you forget the Bottom Bun, the sandwich falls apart (state gets corrupted).
如果你忘了底層麵包，三明治就會散掉（狀態會損壞）。