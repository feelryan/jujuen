# Module: Backtracking (Foundations / Beginner)
# 模組：回溯法（基礎 / 初級）

## 1. Learning Objectives (學習目標)

1.  **Master the Standard Template:** Understand the "Choose, Explore, Un-choose" pattern to solve combinatorial problems.
    **掌握標準模板：** 理解「選擇、探索、取消選擇」的模式以解決組合類問題。
2.  **Visualize the State Space Tree:** Learn to draw the decision tree to visualize the problem scope and recursion depth.
    **具象化狀態空間樹：** 學習繪製決策樹，以視覺化問題範圍與遞迴深度。
3.  **Handle Mutable State Correctly:** Specifically in Python, learn how to manage object references (deep copy vs. shallow copy) during recursion.
    **正確處理可變狀態：** 特別是在 Python 中，學習如何在遞迴過程中管理物件參照（深拷貝與淺拷貝）。
4.  **Differentiate Backtracking from DFS:** Understand that Backtracking is a specific form of DFS used for finding all solutions or a valid solution under constraints.
    **區分回溯法與深度優先搜尋（DFS）：** 理解回溯法是 DFS 的一種特定形式，用於尋找所有解或特定限制下的有效解。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time.
回溯法是一種遞迴解題的演算法技巧，透過一次一步的方式增量構建解決方案。

It removes those solutions that fail to satisfy the constraints of the problem at any point of time (this is called "pruning").
它會在任何時間點移除無法滿足問題限制的解決方案（這被稱為「剪枝」）。

### Intuition (直覺)
Think of walking through a maze.
想像你在走迷宮。
You choose a path and keep walking until you hit a dead end.
你選擇一條路徑並持續走，直到遇到死胡同。
Once you hit a dead end, you turn around (backtrack) to the last junction and try a different path.
一旦遇到死胡同，你轉身（回溯）回到上一個路口，並嘗試另一條路徑。

### Complexity (複雜度)
*   **Time Complexity:** Usually Exponential ($O(2^N)$) or Factorial ($O(N!)$). It is an exhaustive search.
    **時間複雜度：** 通常是指數級 ($O(2^N)$) 或階乘級 ($O(N!)$)。這是一種窮舉搜尋。
*   **Space Complexity:** Linear ($O(N)$), determined by the height of the recursion tree (stack depth).
    **空間複雜度：** 線性 ($O(N)$)，由遞迴樹的高度（堆疊深度）決定。

### When to Use (適用場景)
*   Find **all** solutions (e.g., all permutations, all subsets).
    尋找 **所有** 解（例如：所有排列、所有子集）。
*   Find **a** valid solution under constraints (e.g., Sudoku, N-Queens).
    尋找限制條件下的 **一個** 有效解（例如：數獨、八皇后問題）。

### When NOT to Use (不適用場景)
*   Find the **shortest** path (Use BFS).
    尋找 **最短** 路徑（使用 BFS）。
*   Find the **optimal** value (min/max) where subproblems overlap (Use DP or Greedy).
    尋找子問題重疊時的 **最佳** 值（極大/極小）（使用動態規劃或貪婪演算法）。

---

## 3. Typical Patterns (典型題型 / 模式)

For a beginner level, focus on these three fundamental patterns:
針對初級難度，專注於以下三種基礎模式：

1.  **Combinations / Subsets (組合 / 子集):**
    *   Order does not matter (`[1, 2]` is the same as `[2, 1]`).
    *   順序不重要（`[1, 2]` 與 `[2, 1]` 視為相同）。
    *   *Key:* Use a `start_index` to avoid reusing previous elements.
    *   *關鍵：* 使用 `start_index` 以避免重複使用先前的元素。

2.  **Permutations (排列):**
    *   Order matters (`[1, 2]` is distinct from `[2, 1]`).
    *   順序很重要（`[1, 2]` 與 `[2, 1]` 視為不同）。
    *   *Key:* Use a `visited` array or swap elements to track usage.
    *   *關鍵：* 使用 `visited` 陣列或交換元素來追蹤使用狀態。

3.  **Constraint Satisfaction (限制滿足):**
    *   Placing items on a grid/board (e.g., N-Queens, Sudoku).
    *   在網格/棋盤上放置項目（例如：八皇后、數獨）。
    *   *Key:* `isValid()` function to check constraints before exploring.
    *   *關鍵：* 在探索前使用 `isValid()` 函數檢查限制條件。

---

## 4. Example Walkthrough (範例講解)

### Problem: Permutations (全排列)
**Problem Statement:** Given an array `nums` of distinct integers, return all the possible permutations.
**問題重述：** 給定一個包含相異整數的陣列 `nums`，回傳所有可能的排列。

### Approach (思路)

1.  **Brute Force / Intuition:** We have $N$ slots to fill. For the first slot, we have $N$ choices. For the second, $N-1$, and so on.
    **暴力法 / 直覺：** 我們有 $N$ 個空位要填。第一個空位有 $N$ 種選擇，第二個有 $N-1$ 種，依此類推。
2.  **Backtracking Strategy:**
    **回溯策略：**
    *   **Path:** Current list of numbers selected.
        **路徑：** 目前已選擇的數字列表。
    *   **Choices:** Numbers not yet in the `path`.
        **選擇：** 尚未在 `path` 中的數字。
    *   **Base Case:** When `len(path) == len(nums)`.
        **終止條件：** 當 `len(path) == len(nums)` 時。

### Python Solution (參考解)

```python
from typing import List

class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        res = []
        
        # Helper function for recursion
        # 遞迴輔助函數
        def backtrack(path: List[int], visited: set):
            # Base Case: If the path length equals nums length, we found a permutation
            # 終止條件：如果路徑長度等於 nums 長度，我們找到了一組排列
            if len(path) == len(nums):
                # CRITICAL: Append a copy of the path, not the reference
                # 關鍵：加入路徑的「副本」，而非參照
                res.append(path[:]) 
                return
            
            # Iterate through all possible candidates
            # 遍歷所有可能的候選者
            for num in nums:
                # Pruning: Skip if number is already used
                # 剪枝：如果數字已使用則跳過
                if num in visited:
                    continue
                
                # 1. Choose (Make a decision)
                # 1. 選擇（做出決策）
                path.append(num)
                visited.add(num)
                
                # 2. Explore (Recurse)
                # 2. 探索（遞迴）
                backtrack(path, visited)
                
                # 3. Un-choose (Backtrack / Undo the decision)
                # 3. 取消選擇（回溯 / 撤銷決策）
                visited.remove(num)
                path.pop()

        # Initial call
        # 初始呼叫
        backtrack([], set())
        return res
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(N \times N!)$. There are $N!$ permutations, and copying the list takes $O(N)$.
    **時間：** $O(N \times N!)$。共有 $N!$ 種排列，且複製列表需要 $O(N)$。
*   **Space:** $O(N)$. The recursion stack depth is $N$.
    **空間：** $O(N)$。遞迴堆疊深度為 $N$。

### Error Demonstration (錯誤示範)

```python
# Wrong! 錯誤！
if len(path) == len(nums):
    res.append(path) # Adds a reference to the mutable list
    return
```
**Why it's wrong:** In Python, lists are mutable. If you append `path` directly, `res` will contain multiple references to the *same* list object. When you later `pop()` from that list, all entries in `res` will become empty.
**為何錯誤：** 在 Python 中，列表是可變的。如果你直接加入 `path`，`res` 將包含多個指向 *同一個* 列表物件的參照。當你稍後對該列表執行 `pop()` 時，`res` 中的所有項目都會變為空。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Shallow vs Deep Copy**<br>(淺拷貝 vs 深拷貝) | **Pitfall:** Forgetting `path[:]` or `path.copy()`.<br>**陷阱：** 忘記使用 `path[:]` 或 `path.copy()`。<br>**Result:** Output is a list of empty lists `[[], [], []]`.<br>**結果：** 輸出變成一堆空列表 `[[], [], []]`。 |
| **Backtracking vs Recursion**<br>(回溯 vs 遞迴) | **Contrast:** Recursion is the mechanism; Backtracking is the strategy using recursion to search.<br>**對比：** 遞迴是機制；回溯是利用遞迴進行搜尋的策略。<br>**Key:** Backtracking explicitly *undoes* state changes (`pop()`).<br>**關鍵：** 回溯法會明確地 *撤銷* 狀態變更（`pop()`）。 |
| **Permutation vs Combination**<br>(排列 vs 組合) | **Confusion:** Using `start_index` for Permutations.<br>**混淆：** 在排列問題中使用 `start_index`。<br>**Fix:** Permutations scan from index `0` every time (checking `visited`); Combinations scan from `start_index`.<br>**修正：** 排列每次從索引 `0` 開始掃描（檢查 `visited`）；組合從 `start_index` 開始掃描。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This looks like a combinatorial problem where we need to generate all possibilities. I'll use Backtracking."
    **識別：** 「這看起來像是一個組合問題，我們需要生成所有可能性。我將使用回溯法。」
2.  **Define State:** "I need to track the `current_path` and the `available_choices`."
    **定義狀態：** 「我需要追蹤 `current_path`（當前路徑）以及 `available_choices`（可用選擇）。」
3.  **Draw the Tree:** Briefly sketch the first 2 levels of the decision tree on the whiteboard. This proves you understand the complexity.
    **繪製樹狀圖：** 在白板上簡略畫出決策樹的前兩層。這證明你理解其複雜度。

### Whiteboard Strategy (白板策略)
*   Write the skeleton first: `def backtrack(path, ...):`.
    先寫骨架：`def backtrack(path, ...):`。
*   Write the Base Case immediately. This prevents infinite recursion bugs.
    立即寫下終止條件。這能防止無限遞迴的 Bug。
*   Leave space for the "Constraint Check" inside the loop.
    在迴圈內預留「限制檢查」的空間。

### Common Follow-up (常見追問)
*   "How would you handle duplicates in the input?" (Requires sorting + skipping logic).
    「你會如何處理輸入中的重複項？」（需要排序 + 跳過邏輯）。
*   "Can we optimize space?" (Discuss swapping in-place vs. using new lists).
    「我們可以優化空間嗎？」（討論原地交換 vs 使用新列表）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Subsets (子集)
*   **Prompt:** Given unique integers, return all possible subsets.
    **題目：** 給定相異整數，回傳所有可能的子集。
*   **Hint:** Use `start_index` in your recursion to ensure you only move forward.
    **提示：** 在遞迴中使用 `start_index` 以確保只向前移動。
*   **Key Logic:** `backtrack(start_index, current_path)`

### 2. Medium: Combination Sum (組合總和)
*   **Prompt:** Given distinct integers and a target, find all unique combinations that sum to target. Numbers can be reused.
    **題目：** 給定相異整數與目標值，找出總和為目標值的所有唯一組合。數字可重複使用。
*   **Hint:** Since numbers can be reused, pass the *same* `index` to the next recursion, not `index + 1`.
    **提示：** 由於數字可重複使用，傳遞 *同一個* `index` 給下一次遞迴，而非 `index + 1`。

### 3. Hard (for Beginner module): N-Queens (八皇后)
*   **Prompt:** Place $N$ queens on an $N \times N$ chessboard so no two queens attack each other.
    **題目：** 在 $N \times N$ 的棋盤上放置 $N$ 個皇后，使得沒有兩個皇后互相攻擊。
*   **Hint:** The state needs to track `cols`, `diagonals`, and `anti-diagonals`.
    **提示：** 狀態需要追蹤 `cols`（行）、`diagonals`（對角線）與 `anti-diagonals`（反對角線）。

---

## 8. Quick Checklists (快速檢核表)

Use this during your coding or code review:
在編碼或程式碼審查時使用此表：

- [ ] **Base Case:** Does the recursion stop? (e.g., `index == n` or `sum == target`)
    **終止條件：** 遞迴會停止嗎？（例如 `index == n` 或 `sum == target`）
- [ ] **Copying:** Did I append `path[:]` (copy) instead of `path` (reference)?
    **複製：** 我是否加入了 `path[:]`（副本）而非 `path`（參照）？
- [ ] **Restoration:** Did I `pop()` or revert changes after the recursive call?
    **狀態還原：** 我是否在遞迴呼叫後執行了 `pop()` 或還原變更？
- [ ] **Valid State:** Do I check constraints *before* entering the next recursion level?
    **有效狀態：** 我是否在進入下一層遞迴 *前* 檢查了限制條件？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Dr. Strange" Analogy (奇異博士類比)
*   **Concept:** Backtracking explores all possible futures.
    **觀念：** 回溯法探索所有可能的未來。
*   **Visual:** Dr. Strange looking at 14 million outcomes. If a timeline leads to Thanos winning (invalid constraint), he stops looking at that timeline and goes back to try a different decision.
    **畫面：** 奇異博士檢視 1400 萬種結果。如果某條時間線導致薩諾斯獲勝（無效限制），他會停止檢視該時間線，並回到過去嘗試不同的決策。

### The "Ctrl+Z" Pattern (Ctrl+Z 模式)
*   **Action:** `path.append(x)` is typing a letter.
    **動作：** `path.append(x)` 就像打一個字。
*   **Recursion:** `backtrack(...)` is saving the document.
    **遞迴：** `backtrack(...)` 就像存檔。
*   **Backtracking:** `path.pop()` is pressing **Ctrl+Z** to undo the typing so you can type a different letter.
    **回溯：** `path.pop()` 就像按 **Ctrl+Z** 撤銷打字，這樣你才能打另一個字。