# Backtracking (Beginner Level)
# 回溯法（初級）

## 1. Learning Objectives（學習目標）

1.  **Understand the "State Space Tree" concept.**
    理解「狀態空間樹」的概念。
    *Visualize the problem as a tree traversal where each node represents a decision.*
    *將問題視覺化為樹狀遍歷，其中每個節點代表一個決策。*

2.  **Master the Standard Backtracking Template.**
    掌握標準的回溯法模板。
    *Internalize the pattern: Choose $\rightarrow$ Explore $\rightarrow$ Un-choose (Backtrack).*
    *內化模式：選擇 $\rightarrow$ 探索 $\rightarrow$ 取消選擇（回溯）。*

3.  **Distinguish between Permutations, Combinations, and Subsets.**
    區分排列、組合與子集。
    *Identify when order matters and when it doesn't to apply the correct logic.*
    *識別順序是否重要，以便應用正確的邏輯。*

4.  **Analyze Factorial and Exponential Time Complexity.**
    分析階乘與指數時間複雜度。
    *Recognize why backtracking is often $O(N!)$ or $O(2^N)$ and accept it as necessary for NP-complete problems.*
    *認清為何回溯法通常是 $O(N!)$ 或 $O(2^N)$，並接受這是 NP 完全問題所必需的。*

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time.
回溯法是一種遞迴演算法技術，透過一次構建一部分的方式來逐步解決問題。
It removes those solutions ("backtracks") that fail to satisfy the constraints of the problem at any point of time.
它會在任何時間點移除（「回溯」）那些無法滿足問題約束條件的解。

### Intuition（直覺）
Imagine you are in a maze. You choose a path and walk until you hit a dead end.
想像你在一個迷宮中。你選擇一條路走，直到遇到死胡同。
Then, you turn back (backtrack) to the last junction and try a different path.
然後，你折返（回溯）到上一個路口，並嘗試另一條路。

### Complexity（複雜度）
*   **Time:** Often $O(N!)$ (Permutations) or $O(2^N)$ (Subsets). It is computationally expensive.
    **時間：** 通常是 $O(N!)$（排列）或 $O(2^N)$（子集）。計算成本很高。
*   **Space:** $O(N)$ for the recursion stack depth.
    **空間：** 遞迴堆疊深度通常為 $O(N)$。

### When to Use（適用場景）
1.  **Find ALL solutions:** e.g., Generate all valid parentheses.
    **尋找所有解：** 例如，生成所有合法的括號組合。
2.  **Combinatorial problems:** Permutations, combinations, subsets.
    **組合問題：** 排列、組合、子集。
3.  **Constraint Satisfaction:** Sudoku, N-Queens.
    **約束滿足問題：** 數獨、八皇后問題。

### When NOT to Use（不適用場景）
1.  **Find the Shortest Path:** BFS is usually better for unweighted graphs.
    **尋找最短路徑：** 對於無權圖，BFS 通常更好。
2.  **Simple Optimization:** If you just need a min/max value, DP or Greedy might be more efficient.
    **簡單最佳化：** 如果你只需要最大/最小值，動態規劃或貪婪演算法可能更有效率。

---

## 3. Typical Patterns（典型題型 / 模式）

For beginners, almost all backtracking problems fit into this pseudo-code template:
對於初學者來說，幾乎所有的回溯問題都符合這個虛擬碼模板：

```typescript
function backtrack(candidate: any[]) {
    // 1. Base Case: Check if we found a solution
    // 1. 基本情況：檢查是否找到解
    if (isSolution(candidate)) {
        output(candidate);
        return;
    }

    // 2. Iterate through all possible next steps
    // 2. 遍歷所有可能的下一步
    for (let nextCandidate of listCandidates()) {
        if (isValid(nextCandidate)) {
            // A. Choose (Place)
            // A. 選擇（放置）
            place(nextCandidate);

            // B. Explore (Recurse)
            // B. 探索（遞迴）
            backtrack(nextCandidate);

            // C. Un-choose (Remove/Backtrack)
            // C. 取消選擇（移除/回溯）
            remove(nextCandidate);
        }
    }
}
```

### Key Variations（主要變體）
1.  **Subsets (子集):** Decision is "include or exclude current element".
    **子集：** 決策是「包含或不包含當前元素」。
2.  **Permutations (排列):** Decision is "pick an unused element for this position".
    **排列：** 決策是「為此位置挑選一個未使用的元素」。
3.  **Combinations (組合):** Similar to subsets, but often with a fixed size $k$.
    **組合：** 類似子集，但通常有固定大小 $k$。

---

## 4. Example Walkthrough（範例講解）

### Problem: Permutations (LeetCode 46)
**Problem Statement:** Given an array `nums` of distinct integers, return *all the possible permutations*.
**問題重述：** 給定一個包含相異整數的陣列 `nums`，回傳*所有可能的排列*。

### Approach（思路）

1.  **Brute Force / Intuition:**
    **暴力 / 直覺：**
    We need to fill $N$ slots. For the first slot, we have $N$ choices. For the second, $N-1$, and so on.
    我們需要填滿 $N$ 個空位。第一個空位有 $N$ 種選擇。第二個有 $N-1$ 種，依此類推。

2.  **Optimization (Pruning):**
    **優化（剪枝）：**
    Since numbers are distinct, we just need to track which numbers are already used in the current path to avoid duplicates.
    由於數字是相異的，我們只需要追蹤當前路徑中已經使用了哪些數字，以避免重複。

3.  **Complexity:**
    **複雜度：**
    *   Time: $O(N \times N!)$. There are $N!$ permutations, and copying the array takes $O(N)$.
        時間：$O(N \times N!)$。有 $N!$ 種排列，複製陣列需要 $O(N)$。
    *   Space: $O(N)$ for recursion stack.
        空間：$O(N)$ 用於遞迴堆疊。

### Bad Implementation (Mistake)
**錯誤示範：**
Forgetting to "backtrack" (pop the element) causes the array to grow indefinitely or contain wrong states.
忘記「回溯」（移除元素）會導致陣列無限增長或包含錯誤的狀態。

### TypeScript Solution (Reference)
**TypeScript 參考解：**

```typescript
function permute(nums: number[]): number[][] {
    const result: number[][] = [];
    
    // Track used numbers to avoid duplicates in a single permutation
    // 追蹤已使用的數字，以避免在單一排列中重複
    const used = new Array(nums.length).fill(false);

    /**
     * Helper function for recursion
     * 遞迴輔助函式
     * @param currentPath The permutation being built (正在構建的排列)
     */
    function backtrack(currentPath: number[]) {
        // Base Case: If the path length equals nums length, we have a complete permutation
        // 基本情況：如果路徑長度等於 nums 長度，我們就得到了一個完整的排列
        if (currentPath.length === nums.length) {
            // CRITICAL: Push a copy, not the reference!
            // 關鍵：推入副本，而不是參照！
            result.push([...currentPath]); 
            return;
        }

        for (let i = 0; i < nums.length; i++) {
            // Skip if this number is already used in the current branch
            // 如果此數字在當前分支已使用，則跳過
            if (used[i]) continue;

            // 1. Choose (選擇)
            used[i] = true;
            currentPath.push(nums[i]);

            // 2. Explore (探索)
            backtrack(currentPath);

            // 3. Un-choose / Backtrack (取消選擇 / 回溯)
            // Reset state for the next iteration
            // 重置狀態以進行下一次迭代
            currentPath.pop();
            used[i] = false;
        }
    }

    backtrack([]);
    return result;
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Description (描述) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Reference vs Copy** | Pushing `currentPath` to `result`. <br> 將 `currentPath` 推入 `result`。 | Pushing the reference `result.push(path)`. All entries in result become empty `[]` because you backtrack on the same object. <br> 推入參照 `result.push(path)`。結果中的所有項目都會變成空的 `[]`，因為你在同一個物件上回溯。 |
| **Start Index** | Using `start` index in loop. <br> 在迴圈中使用 `start` 索引。 | Using `start` index for Permutations (wrong) vs Combinations (correct). Permutations always scan from 0; Combinations scan from `start`. <br> 在排列中使用 `start`（錯）vs 在組合中使用（對）。排列總是從 0 開始掃描；組合從 `start` 開始。 |
| **Base Case** | When to stop recursion. <br> 何時停止遞迴。 | Returning too early or forgetting to return, causing stack overflow. <br> 太早返回或忘記返回，導致堆疊溢位。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Verbal Framework (口條框架)
*   **Start with the Tree:** "I'm thinking of this as a state-space tree problem."
    **從樹開始：** 「我將這視為一個狀態空間樹的問題。」
*   **Define Choices:** "At each step, my choice is to pick a number that hasn't been used yet."
    **定義選擇：** 「在每一步，我的選擇是挑選一個尚未被使用的數字。」
*   **Define Constraints:** "The constraint is that numbers must be distinct."
    **定義約束：** 「約束條件是數字必須是相異的。」

### 2. Whiteboard Strategy (白板策略)
*   Draw a small tree for `nums = [1, 2, 3]`.
    畫一個 `nums = [1, 2, 3]` 的小樹。
*   Write `Choose`, `Recurse`, `Backtrack` explicitly as comments before coding.
    在寫程式碼之前，明確地將 `Choose`、`Recurse`、`Backtrack` 寫成註解。

### 3. Common Follow-ups (常見追問)
*   *Q: What if the input contains duplicates?* (e.g., `[1, 1, 2]`)
    *問：如果輸入包含重複項目怎麼辦？*
    *A: We need to sort the array first and add a condition to skip adjacent duplicates.*
    *答：我們需要先排序陣列，並加入條件跳過相鄰的重複項。*

---

## 7. Exercises（練習題）

### Level: Easy (Subsets)
**Problem:** Given unique integers `nums`, return all possible subsets.
**問題：** 給定相異整數 `nums`，回傳所有可能的子集。
*   **Hint:** For every number, you have two choices: include it or exclude it.
    **提示：** 對於每個數字，你有兩個選擇：包含它或不包含它。
*   **Key Logic:** `index + 1` recursion.

### Level: Medium (Combination Sum)
**Problem:** Given distinct integers `candidates` and a target, find all unique combinations that sum to target. Numbers can be chosen unlimited times.
**問題：** 給定相異整數 `candidates` 和一個目標值，找出總和為目標值的所有唯一組合。數字可以被無限次選取。
*   **Hint:** Since we can reuse numbers, the recursive call should pass `i` (current index), not `i + 1`.
    **提示：** 由於我們可以重複使用數字，遞迴呼叫應該傳遞 `i`（當前索引），而不是 `i + 1`。

### Level: Medium/Hard (Word Search)
**Problem:** Given an `m x n` grid of characters and a string `word`, return true if `word` exists in the grid.
**問題：** 給定一個 `m x n` 的字元網格和一個字串 `word`，如果 `word` 存在於網格中則回傳 true。
*   **Hint:** This is 2D backtracking (DFS on grid). Mark cells as visited temporarily.
    **提示：** 這是二維回溯（網格上的 DFS）。暫時將儲存格標記為已訪問。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Base Case:** Does the recursion terminate correctly?
    **基本情況：** 遞迴是否正確終止？
*   [ ] **State Reset:** Did I `pop()` or revert changes after the recursive call?
    **狀態重置：** 我是否在遞迴呼叫後 `pop()` 或還原了變更？
*   [ ] **Deep Copy:** Did I push `[...path]` instead of `path`?
    **深拷貝：** 我是否推入了 `[...path]` 而不是 `path`？
*   [ ] **Duplicates:** Did I handle duplicates if the problem requires unique results?
    **重複項：** 如果問題要求唯一結果，我是否處理了重複項？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Ctrl+Z" Analogy (Ctrl+Z 類比)
Think of Backtracking as typing a document.
將回溯法想像成打文件。
1.  **Type a character** (Make a choice / `push`).
    **打一個字**（做出選擇 / `push`）。
2.  **Check if it makes sense** (Validate).
    **檢查是否合理**（驗證）。
3.  **Keep typing** (Recurse).
    **繼續打字**（遞迴）。
4.  **Realize it's wrong, hit Ctrl+Z** (Backtrack / `pop`).
    **發現錯了，按 Ctrl+Z**（回溯 / `pop`）。

### The "Universal Template" Image (萬用模板圖像)
Visualize a sandwich:
想像一個三明治：
*   **Top Bun:** `path.push(val)` (Choose)
    **上層麵包：** `path.push(val)`（選擇）
*   **Meat:** `backtrack(...)` (Explore)
    **肉：** `backtrack(...)`（探索）
*   **Bottom Bun:** `path.pop()` (Un-choose)
    **下層麵包：** `path.pop()`（取消選擇）

You cannot have the sandwich without both buns!
沒有這兩層麵包，三明治就不成立！