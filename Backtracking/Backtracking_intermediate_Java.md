Here is the complete interview guide for Backtracking, tailored for a Senior Software Engineer, using Java as the coding language.

這是一份針對資深軟體工程師量身打造的 Backtracking（回溯法）面試指南，使用 Java 撰寫。

---

# Backtracking Interview Guide (Intermediate)
# 回溯法面試指南（中階）

## 1. Learning Objectives（學習目標）

*   **Master the Standard Template:** Internalize the "Choose, Explore, Un-choose" structure to convert any decision tree problem into code within minutes.
    **掌握標準模板：** 內化「選擇、探索、取消選擇」的結構，以便在幾分鐘內將任何決策樹問題轉化為程式碼。
*   **Deep Understanding of State Management:** Distinguish between passing state by value (immutable) vs. by reference (mutable), and why Java requires explicit copying.
    **深刻理解狀態管理：** 區分按值傳遞（不可變）與按引用傳遞（可變）的狀態，以及為何 Java 需要顯式複製。
*   **Pruning Strategies:** Learn how to identify "dead ends" early to optimize from brute force to an acceptable solution.
    **剪枝策略：** 學習如何儘早識別「死胡同」，將暴力解優化為可接受的方案。
*   **Complexity Analysis:** Confidently articulate Time and Space complexity for exponential algorithms (e.g., $O(N!)$ vs $O(2^N)$).
    **複雜度分析：** 自信地闡述指數級演算法的時間與空間複雜度（例如 $O(N!)$ 對比 $O(2^N)$）。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
Backtracking is essentially a Depth-First Search (DFS) on a state space tree (decision tree).
回溯法本質上是在狀態空間樹（決策樹）上進行的深度優先搜尋（DFS）。

It builds candidates incrementally and abandons a candidate ("backtracks") as soon as it determines that the candidate cannot lead to a valid solution.
它逐步構建候選解，並在確定該候選解無法導向有效解時立即放棄（「回溯」）。

### Intuition（直覺）
Think of it as walking through a maze. You choose a path; if you hit a wall, you turn back (backtrack) to the last junction and try a different path.
把它想像成走迷宮。你選擇一條路；如果撞到牆，你就退回（回溯）到上一個路口，嘗試另一條路。

### Complexity（複雜度）
*   **Time:** Usually Exponential ($O(k^N)$) or Factorial ($O(N!)$). It is computationally expensive.
    **時間：** 通常是指數級（$O(k^N)$）或階乘級（$O(N!)$）。計算成本很高。
*   **Space:** $O(N)$ for the recursion stack, where $N$ is the depth of the decision tree.
    **空間：** $O(N)$ 用於遞迴堆疊，其中 $N$ 是決策樹的深度。

### When to Use（適用場景）
*   Find **all** solutions (e.g., all subsets, all permutations).
    尋找**所有**解（例如：所有子集、所有排列）。
*   Constraint satisfaction problems (e.g., Sudoku, N-Queens).
    約束滿足問題（例如：數獨、N 皇后）。

### When NOT to Use（不適用場景）
*   Find the **shortest** path (BFS is usually better).
    尋找**最短**路徑（BFS 通常更好）。
*   Find if a solution **exists** or count solutions (DP might be more efficient).
    尋找解是否**存在**或計算解的數量（動態規劃可能更有效率）。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Combinations / Subsets (組合 / 子集):**
    *   Order doesn't matter (`[1,2]` is same as `[2,1]`).
    *   Pattern: `start_index` parameter to avoid reusing previous elements.
    *   順序不重要（`[1,2]` 等同於 `[2,1]`）。
    *   模式：使用 `start_index` 參數以避免重複使用先前的元素。

2.  **Permutations (排列):**
    *   Order matters (`[1,2]` is different from `[2,1]`).
    *   Pattern: `used` boolean array or swapping elements to track usage.
    *   順序很重要（`[1,2]` 不同於 `[2,1]`）。
    *   模式：使用 `used` 布林陣列或交換元素來追蹤使用情況。

3.  **Grid Search (網格搜尋):**
    *   Moving in 2D array (e.g., Word Search).
    *   Pattern: Mark cell as visited, recurse, then unmark (backtrack).
    *   在二維陣列中移動（例如：文字搜尋）。
    *   模式：標記格子為已訪問，遞迴，然後取消標記（回溯）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Combination Sum II (LeetCode 40)
**問題重述：**
Given a collection of candidate numbers (`candidates`) and a target number (`target`), find all unique combinations in `candidates` where the candidate numbers sum to `target`. Each number in `candidates` may only be used **once** in the combination. The solution set must not contain duplicate combinations.
給定一組候選數字（`candidates`）和一個目標數字（`target`），找出 `candidates` 中所有數字和為 `target` 的唯一組合。`candidates` 中的每個數字在組合中只能使用**一次**。解集不能包含重複的組合。

### Approach: Brute Force -> Optimization（思路：暴力 -> 優化）

1.  **Naive DFS:** Generate all subsets, sum them up, check if equal to target, and use a `Set` to deduplicate.
    **樸素 DFS：** 生成所有子集，將其加總，檢查是否等於目標值，並使用 `Set` 去除重複。
    *   *Issue:* Extremely slow due to generating invalid branches and heavy `Set` operations.
    *   *問題：* 由於生成無效分支和繁重的 `Set` 操作，速度極慢。

2.  **Backtracking with Pruning (Optimization):**
    **帶剪枝的回溯法（優化）：**
    *   **Sort** the array first. This brings duplicates together.
        首先對陣列進行**排序**。這將重複的元素聚在一起。
    *   Use a loop to iterate through candidates.
        使用迴圈遍歷候選元素。
    *   **Pruning 1 (Sum):** If `current_sum > target`, stop (since array is sorted, subsequent numbers will also be too big).
        **剪枝 1（和）：** 如果 `current_sum > target`，停止（因為陣列已排序，後續數字也會太大）。
    *   **Pruning 2 (Duplicates):** If `candidates[i] == candidates[i-1]` and this is not the first iteration of the current recursion level, skip it.
        **剪枝 2（重複）：** 如果 `candidates[i] == candidates[i-1]` 且這不是當前遞迴層級的第一次迭代，則跳過它。

### Java Reference Solution（Java 參考解）

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        List<List<Integer>> result = new ArrayList<>();
        // Sorting is crucial for deduplication logic to work
        // 排序對於去重邏輯的運作至關重要
        Arrays.sort(candidates);
        
        backtrack(result, new ArrayList<>(), candidates, target, 0);
        return result;
    }

    private void backtrack(List<List<Integer>> result, List<Integer> tempList, 
                           int[] nums, int remain, int start) {
        // Base Case 1: Target reached
        // 基本情況 1：達到目標值
        if (remain == 0) {
            // CRITICAL: Must create a deep copy of tempList
            // 關鍵：必須建立 tempList 的深拷貝
            result.add(new ArrayList<>(tempList));
            return;
        }

        // Base Case 2: Target exceeded (Pruning)
        // 基本情況 2：超過目標值（剪枝）
        if (remain < 0) {
            return;
        }

        for (int i = start; i < nums.length; i++) {
            // Skip duplicates:
            // If current number is same as previous, and it's not the first element 
            // we are considering in this specific recursive step, skip it.
            // 跳過重複項：
            // 如果當前數字與前一個相同，且它不是我們在當前遞迴步驟中考慮的第一個元素，則跳過。
            if (i > start && nums[i] == nums[i - 1]) {
                continue;
            }

            // 1. Choose (加入選擇)
            tempList.add(nums[i]);

            // 2. Explore (向下探索)
            // Note: pass 'i + 1' because we cannot reuse the same element
            // 注意：傳遞 'i + 1' 因為我們不能重複使用同一個元素
            backtrack(result, tempList, nums, remain - nums[i], i + 1);

            // 3. Un-choose (Backtrack / 撤銷選擇)
            // Remove the last element to restore state for the next iteration
            // 移除最後一個元素以恢復狀態，供下一次迭代使用
            tempList.remove(tempList.size() - 1);
        }
    }
}
```

### Complexity Analysis（複雜度分析）
*   **Time Complexity:** $O(2^N)$ in the worst case (all subsets), but significantly faster on average due to pruning. Sorting takes $O(N \log N)$.
    **時間複雜度：** 最壞情況下為 $O(2^N)$（所有子集），但由於剪枝，平均速度快得多。排序耗時 $O(N \log N)$。
*   **Space Complexity:** $O(N)$ for the recursion stack depth (where N is the number of candidates) + space for output.
    **空間複雜度：** $O(N)$ 用於遞迴堆疊深度（N 為候選數量）+ 輸出所需的空間。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Mutable State (Java)** | **Trap:** Adding `tempList` directly to `result` (`result.add(tempList)`). <br> **Fix:** You end up with empty lists because `tempList` is modified later. Always use `new ArrayList<>(tempList)`. <br> **陷阱：** 直接將 `tempList` 加入 `result`。 <br> **修正：** 你最終會得到空列表，因為 `tempList` 隨後被修改。務必使用 `new ArrayList<>(tempList)`。 |
| **Start Index vs. 0** | **Usage:** Use `start` (or `i+1`) for Combinations (no duplicates/order doesn't matter). Use `0` for Permutations (reuse elements/order matters). <br> **用法：** 組合問題用 `start`（或 `i+1`）；排列問題從 `0` 開始掃描（需配合 `used` 陣列）。 |
| **`i` vs `i + 1`** | **Logic:** Pass `i` if elements can be reused (unlimited supply). Pass `i + 1` if elements can only be used once. <br> **邏輯：** 如果元素可重複使用，傳遞 `i`；如果元素只能用一次，傳遞 `i + 1`。 |
| **Base Case Return** | **Trap:** Forgetting `return` after finding a valid solution. <br> **Consequence:** The code might continue to add elements, causing IndexOutOfBounds or wrong answers. <br> **陷阱：** 找到有效解後忘記 `return`。 <br> **後果：** 程式碼可能繼續添加元素，導致越界或錯誤答案。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Framework (口條框架)
Start with the "State-Space Tree" analogy.
從「狀態空間樹」的比喻開始。
> "I will approach this using Backtracking. I visualize the problem as a decision tree where at each step, I decide whether to include a number or not."
> 「我將使用回溯法來解決這個問題。我將問題視覺化為一個決策樹，在每一步，我決定是否包含一個數字。」

### 2. Whiteboard Strategy (白板策略)
*   **Draw the Tree:** Draw a small example (e.g., input `[1, 2, 3]`) to show the recursion depth and branches. This proves you understand the flow before writing code.
    **畫出樹狀圖：** 畫一個小範例（如輸入 `[1, 2, 3]`）來展示遞迴深度與分支。這證明你在寫程式碼前已理解流程。
*   **Define State:** Clearly write down what arguments your helper function needs (`index`, `currentSum`, `currentList`).
    **定義狀態：** 清楚寫下你的輔助函式需要哪些參數（`index`, `currentSum`, `currentList`）。

### 3. Common Follow-ups (常見追問)
*   *Q: What if the input contains duplicates?* -> A: Sort and skip `nums[i] == nums[i-1]`.
    *問：如果輸入包含重複項怎麼辦？* -> 答：排序並跳過 `nums[i] == nums[i-1]`。
*   *Q: Can we do this iteratively?* -> A: Yes, but it requires an explicit Stack and is much harder to read.
    *問：我們可以用迭代方式做嗎？* -> 答：可以，但需要顯式的 Stack，且可讀性差得多。
*   *Q: Time complexity analysis?* -> A: Be ready to explain why it's $O(2^N)$ or $O(N!)$.
    *問：時間複雜度分析？* -> 答：準備好解釋為什麼是 $O(2^N)$ 或 $O(N!)$。

---

## 7. Practice Problems（練習題）

### Easy: Subsets (LeetCode 78)
*   **Hint:** The most basic template. Decision: Include `nums[i]` or don't.
*   **提示：** 最基礎的模板。決策：包含 `nums[i]` 或不包含。
*   **Focus:** Correctly managing the `start` index.
*   **重點：** 正確管理 `start` 索引。

### Medium: Palindrome Partitioning (LeetCode 131)
*   **Hint:** Instead of picking a number, you are picking a "cut point" in a string.
*   **提示：** 不是選擇數字，而是在字串中選擇一個「切割點」。
*   **Logic:** Loop `i` from `start` to `end`. If `s.substring(start, i+1)` is palindrome, recurse on `i+1`.
*   **邏輯：** 迴圈 `i` 從 `start` 到 `end`。如果 `s.substring(start, i+1)` 是迴文，則對 `i+1` 進行遞迴。

### Hard: N-Queens (LeetCode 51)
*   **Hint:** Grid-based constraint. You don't need a full 2D array to track attacks.
*   **提示：** 基於網格的約束。你不需要完整的二維陣列來追蹤攻擊。
*   **Optimization:** Use three Sets (or boolean arrays) to track: `cols`, `diagonals` (row-col), and `anti-diagonals` (row+col).
*   **優化：** 使用三個 Set（或布林陣列）來追蹤：`cols`（列）、`diagonals`（對角線 row-col）和 `anti-diagonals`（反對角線 row+col）。

---

## 8. Quick Checklists（快速檢核表）

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

- [ ] **State Restoration:** Did I remove the last element (`remove(size-1)`) after the recursive call?
    **狀態重置：** 我是否在遞迴呼叫後移除了最後一個元素？
- [ ] **Deep Copy:** Did I add `new ArrayList<>(current)` to the result instead of `current`?
    **深拷貝：** 我是否將 `new ArrayList<>(current)` 加入結果，而不是 `current`？
- [ ] **Base Case:** Does my recursion definitely terminate? (Check `index >= length` or `target == 0`).
    **基本情況：** 我的遞迴是否肯定會終止？（檢查 `index >= length` 或 `target == 0`）。
- [ ] **Pruning:** Did I add checks to skip obviously wrong paths early?
    **剪枝：** 我是否添加了檢查以儘早跳過明顯錯誤的路徑？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Save Game" Analogy (存檔類比)
Imagine playing a video game (RPG).
想像在玩電子遊戲（RPG）。

1.  **Save Point (Snapshot):** Before entering a boss room (making a decision), you save the game.
    **存檔點（快照）：** 在進入魔王房（做決定）之前，你存檔。
2.  **Play (Recurse):** You fight the boss.
    **遊玩（遞迴）：** 你與魔王戰鬥。
3.  **Game Over (Backtrack):** You die (invalid solution). You reload the save file.
    **遊戲結束（回溯）：** 你死了（無效解）。你讀取存檔。
4.  **Try Again:** You try a different weapon (next iteration in loop).
    **再試一次：** 你嘗試不同的武器（迴圈中的下一次迭代）。

In Java Backtracking:
*   `tempList.add()` = Equip Weapon.
*   `backtrack()` = Fight Boss.
*   `tempList.remove()` = Reload Save / Unequip Weapon.

### Visual Anchor (圖像錨點)
Remember the shape of the code:
記住程式碼的形狀：
```text
Function:
  If Win -> Record
  For each Choice:
     Make Choice
     Recurse
     Undo Choice
```
This "Sandwich" structure (Make -> Recurse -> Undo) is the signature of Backtracking.
這種「三明治」結構（做 -> 遞迴 -> 撤銷）是回溯法的標誌。