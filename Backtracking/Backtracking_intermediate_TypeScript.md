# Backtracking: Intermediate Guide for Senior Engineers
# 回溯法：資深工程師的中階指南

## 1. Learning Objectives (學習目標)

1.  **Master the Standard Template:** Internalize the "Choose, Explore, Un-choose" pattern to implement any backtracking solution rapidly.
    **掌握標準模板：** 內化「選擇、探索、取消選擇」的模式，以快速實作任何回溯解決方案。

2.  **State Management & Immutability:** Understand how to manage state references correctly in TypeScript (avoiding the common shallow copy trap).
    **狀態管理與不可變性：** 理解如何在 TypeScript 中正確管理狀態引用（避免常見的淺拷貝陷阱）。

3.  **Pruning Strategies:** Learn to identify invalid branches early to optimize time complexity from "impossible" to "acceptable".
    **剪枝策略：** 學習儘早識別無效分支，將時間複雜度從「不可能」優化為「可接受」。

4.  **Complexity Analysis:** Be able to articulate the Time/Space complexity of exponential algorithms (e.g., $O(N!)$, $O(2^N)$) confidently.
    **複雜度分析：** 能夠自信地闡述指數級演算法（如 $O(N!)$、$O(2^N)$）的時間與空間複雜度。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time.
回溯法是一種遞迴解題的演算法技術，透過一次構建一部分的方式來嘗試建立解決方案。

It removes those solutions that fail to satisfy the constraints of the problem at any point of time (by time, here, is referred to the time elapsed till reaching any level of the search tree).
它會在任何時間點（此處的時間指到達搜尋樹任意層級所經過的過程）移除那些無法滿足問題約束條件的解決方案。

### Intuition (直覺)
Think of it as a Depth-First Search (DFS) on a "State Space Tree".
將其視為在「狀態空間樹」上進行的深度優先搜尋（DFS）。

You walk down a path; if you hit a dead end or a valid solution, you return to the previous junction and try a different path.
你沿著一條路徑走；如果遇到死胡同或找到有效解，就退回到上一個路口並嘗試另一條路徑。

### Complexity (複雜度)
-   **Time:** Usually Exponential ($O(K^N)$) or Factorial ($O(N!)$). It is computationally expensive.
    **時間：** 通常是指數級 ($O(K^N)$) 或階乘級 ($O(N!)$)。計算成本很高。
-   **Space:** $O(N)$ typically, representing the recursion stack depth and the space to hold the current path.
    **空間：** 通常是 $O(N)$，代表遞迴堆疊深度以及儲存當前路徑的空間。

### When to Use (適用場景)
-   Find **all** solutions (e.g., all subsets, all permutations).
    找出 **所有** 解（例如：所有子集、所有排列）。
-   Find **one** valid solution where greedy fails (e.g., Sudoku, N-Queens).
    找出 **一個** 有效解，且貪婪演算法無效時（例如：數獨、八皇后）。
-   Constraint satisfaction problems where $N$ is small (usually $N \le 20$).
    $N$ 很小的約束滿足問題（通常 $N \le 20$）。

### When NOT to Use (不適用場景)
-   Find the **Maximum/Minimum** value (usually Dynamic Programming or Greedy is better).
    尋找 **最大/最小** 值（通常動態規劃或貪婪演算法更好）。
-   Check for simple **Connectivity/Existence** in a graph (BFS/Union-Find is faster).
    檢查圖中的簡單 **連通性/存在性**（BFS/Union-Find 更快）。

---

## 3. Typical Patterns (典型題型 / 模式)

For Senior Engineers, recognize these patterns immediately:
對於資深工程師，應立即識別以下模式：

1.  **Combinatorial Search (組合搜尋):**
    -   Subsets (子集): Choose or not choose current element.
    -   Permutations (排列): Order matters, used array needed.
    -   Combinations (組合): Order doesn't matter, usually $k$ elements.

2.  **String Partitioning (字串分割):**
    -   Cutting a string into valid parts (e.g., Palindrome Partitioning).
    -   將字串切割成有效部分（例如：迴文分割）。

3.  **Grid Traversal with State (帶狀態的網格遍歷):**
    -   Word Search (finding a path in a grid).
    -   Flood fill variants requiring backtracking (visiting and un-visiting).
    -   文字搜尋（在網格中尋找路徑）。
    -   需要回溯的 Flood fill 變體（訪問與取消訪問）。

4.  **Constraint Satisfaction (約束滿足):**
    -   Sudoku, N-Queens. Placing items such that no rules are broken.
    -   數獨、八皇后。在不違反規則的情況下放置項目。

---

## 4. Example Walkthrough (範例講解)

### Problem: Combination Sum (LeetCode 39)
**Problem Statement:**
Given an array of **distinct** integers `candidates` and a target integer `target`, return a list of all **unique combinations** of `candidates` where the chosen numbers sum to `target`. You may choose the same number an unlimited number of times.
給定一個由 **相異** 整數組成的陣列 `candidates` 和一個目標整數 `target`，回傳所有 `candidates` 中數字總和為 `target` 的 **唯一組合** 列表。你可以無限次選擇同一個數字。

---

### Thought Process (思路)

1.  **Brute Force (暴力法):**
    Generate all possible subsets (with repetition). If sum equals target, add to result.
    生成所有可能的子集（包含重複選取）。如果總和等於目標值，則加入結果。
    *Issue:* Infinite recursion if we don't handle the sum exceeding target.
    *問題：* 如果不處理總和超過目標值的情況，會導致無限遞迴。

2.  **Optimization (優化 - Pruning):**
    Sort the candidates first. If the current sum plus the current candidate exceeds the target, stop exploring that branch (break the loop).
    先將候選數字排序。如果當前總和加上當前候選數字超過目標值，停止探索該分支（跳出迴圈）。

3.  **Decision Tree (決策樹):**
    At each step, we can decide to include `candidates[i]`. Since we can reuse elements, the next recursive call starts from index `i`. If we move to `i+1`, we define that we will never use `candidates[i]` again in this branch (to avoid duplicates like `[2,3]` and `[3,2]`).
    在每一步，我們可以決定包含 `candidates[i]`。因為可以重複使用元素，下一個遞迴呼叫從索引 `i` 開始。如果我們移動到 `i+1`，則定義在該分支中不再使用 `candidates[i]`（以避免重複，如 `[2,3]` 和 `[3,2]`）。

---

### TypeScript Reference Solution (TypeScript 參考解)

```typescript
function combinationSum(candidates: number[], target: number): number[][] {
    const result: number[][] = [];
    
    // Optimization: Sorting helps us prune the tree early.
    // 優化：排序幫助我們提早修剪決策樹。
    candidates.sort((a, b) => a - b);

    /**
     * Backtracking function
     * @param remaining - The remaining value needed to reach target
     * @param startIdx - The current index in candidates to consider (avoids duplicates)
     * @param path - The current combination being built
     */
    function backtrack(remaining: number, startIdx: number, path: number[]): void {
        // Base Case 1: Valid solution found
        // 基本情況 1：找到有效解
        if (remaining === 0) {
            // CRITICAL: Push a copy of the path, not the reference!
            // 關鍵：推入路徑的副本，而非引用！
            result.push([...path]);
            return;
        }

        // Iterate through candidates starting from startIdx
        // 從 startIdx 開始遍歷候選數字
        for (let i = startIdx; i < candidates.length; i++) {
            const currentVal = candidates[i];

            // Pruning: Since array is sorted, if currentVal > remaining, 
            // all subsequent values will also be too large.
            // 剪枝：由於陣列已排序，若 currentVal > remaining，
            // 則後續所有數值也都太大。
            if (currentVal > remaining) {
                break;
            }

            // 1. Choose (選擇)
            path.push(currentVal);

            // 2. Explore (探索)
            // Note: We pass 'i' not 'i + 1' because we can reuse the same element.
            // 注意：我們傳入 'i' 而非 'i + 1'，因為我們可以重複使用相同元素。
            backtrack(remaining - currentVal, i, path);

            // 3. Un-choose (Backtrack) (取消選擇/回溯)
            path.pop();
        }
    }

    backtrack(target, 0, []);
    return result;
}
```

### Complexity Analysis (複雜度分析)
-   **Time:** $O(N^{\frac{T}{M}})$, where $N$ is the number of candidates, $T$ is the target, and $M$ is the minimum value in candidates. This is a loose upper bound representing the height of the tree.
    **時間：** $O(N^{\frac{T}{M}})$，其中 $N$ 是候選數數量，$T$ 是目標值，$M$ 是候選數中的最小值。這是一個代表樹高度的寬鬆上界。
-   **Space:** $O(\frac{T}{M})$ for the recursion stack (longest path).
    **空間：** $O(\frac{T}{M})$ 用於遞迴堆疊（最長路徑）。

---

### Error Demonstration (錯誤示範)

```typescript
// WRONG: Handling References Incorrectly
// 錯誤：不正確地處理引用

if (remaining === 0) {
    result.push(path); // Bug: Pushes reference to 'path'
    // By the end of the algorithm, 'path' will be empty due to popping.
    // Result will look like [[], [], []].
    // Bug：推入 'path' 的引用。
    // 演算法結束時，'path' 因 pop 操作會變為空。
    // 結果會變成 [[], [], []]。
    return;
}
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Description & Pitfall (描述與陷阱) |
| :--- | :--- |
| **Permutation vs Combination** | Permutation: `[1,2]` $\neq$ `[2,1]` (Order matters). Combination: `[1,2]` == `[2,1]` (Order irrelevant). <br> **Trap:** For combinations, always pass `startIdx` to avoid going backwards. <br> 排列：順序重要。組合：順序無關。**陷阱：** 處理組合時，務必傳遞 `startIdx` 以避免回頭選取。 |
| **Mutable vs Immutable State** | Passing a new array `[...path, val]` in recursion is cleaner but slower ($O(N)$ copy per step). Pushing/Popping on a single `path` is faster ($O(1)$) but requires careful cleanup. <br> **Senior Tip:** Use Push/Pop for performance, but remember to copy when saving result. <br> 在遞迴中傳遞新陣列較乾淨但較慢。在單一 `path` 上 Push/Pop 較快但需小心清理。**資深建議：** 為了效能使用 Push/Pop，但記得在儲存結果時進行拷貝。 |
| **Pruning vs Base Case** | Base case stops recursion when a condition is met. Pruning prevents the recursion from even happening if it's known to be invalid. <br> **Impact:** Pruning is the difference between TLE (Time Limit Exceeded) and Accepted. <br> Base case 在條件滿足時停止遞迴。剪枝則是在已知無效時阻止遞迴發生。**影響：** 剪枝是 TLE 與通過的關鍵差異。 |

---

## 6. Interview Strategy (面試實戰建議)

### 1. Communication Framework (口條框架)
-   **Identify:** "This looks like a combinatorial problem where we need to explore all valid states. I'll use backtracking."
    **識別：** 「這看起來像是一個組合問題，我們需要探索所有有效狀態。我將使用回溯法。」
-   **Define State:** "My state needs to track the `currentIndex` and the `currentPath`."
    **定義狀態：** 「我的狀態需要追蹤 `currentIndex` 和 `currentPath`。」
-   **Discuss Constraints:** "Since $N$ is small (e.g., 20), an exponential solution is acceptable."
    **討論約束：** 「由於 $N$ 很小（例如 20），指數級解法是可以接受的。」

### 2. Whiteboard Strategy (白板策略)
-   **Draw the Tree:** Draw a small decision tree for a trivial input (e.g., `candidates=[2,3], target=5`).
    **畫出樹狀圖：** 為簡單的輸入畫出一個小的決策樹（例如 `candidates=[2,3], target=5`）。
-   **Visualize Backtracking:** Physically draw an arrow going back up the tree when a path fails or succeeds.
    **視覺化回溯：** 當路徑失敗或成功時，畫出一個向上的箭頭表示回溯。

### 3. Common Follow-ups (常見追問)
-   *Q: How to handle duplicates in the input?* (A: Sort and skip `nums[i] == nums[i-1]`).
    *問：如何處理輸入中的重複項？*（答：排序並跳過 `nums[i] == nums[i-1]`）。
-   *Q: Can you do this iteratively?* (A: Yes, using an explicit Stack, though it's more complex to manage state).
    *問：你能用迭代方式實作嗎？*（答：可以，使用顯式 Stack，但狀態管理較複雜）。

---

## 7. Practice Problems (練習題)

### Easy: Subsets (LeetCode 78)
-   **Hint:** For every element, you have two choices: include it or exclude it.
    **提示：** 對於每個元素，你有兩個選擇：包含它或排除它。
-   **Key Logic:** `dfs(i + 1, path)` (exclude) vs `path.push(nums[i]); dfs(i + 1, path); path.pop()` (include).

### Intermediate: Generate Parentheses (LeetCode 22)
-   **Hint:** Track `open` count and `close` count.
    **提示：** 追蹤 `open`（左括號）數量和 `close`（右括號）數量。
-   **Constraint:** Can only add `(` if `open < n`. Can only add `)` if `close < open`.
    **約束：** 只有當 `open < n` 時才能加 `(`。只有當 `close < open` 時才能加 `)`。

### Hard: N-Queens (LeetCode 51)
-   **Hint:** Use three sets to track attacks: `cols`, `diag1` (row - col), `diag2` (row + col).
    **提示：** 使用三個集合來追蹤攻擊：`cols`（列）、`diag1`（行減列）、`diag2`（行加列）。
-   **Optimization:** This turns an $O(N)$ check into $O(1)$ check for valid placement.
    **優化：** 這將有效性檢查從 $O(N)$ 轉變為 $O(1)$。

---

## 8. Quick Checklists (快速檢核表)

Before you say "I'm done":
在你說「我寫完了」之前：

- [ ] **Base Case:** Does the recursion terminate correctly? (e.g., index out of bounds, target reached).
    **基本情況：** 遞迴是否正確終止？（例如：索引越界、達到目標）。
- [ ] **State Restoration:** Did I `pop()` after the recursive call?
    **狀態還原：** 我是否在遞迴呼叫後執行了 `pop()`？
- [ ] **Deep Copy:** Did I push `[...path]` instead of `path` to the result?
    **深拷貝：** 我是否將 `[...path]` 而非 `path` 推入結果？
- [ ] **Pruning:** Did I sort the input or add conditions to skip unnecessary branches?
    **剪枝：** 我是否對輸入進行排序或添加條件以跳過不必要的分支？
- [ ] **Duplicates:** Did I handle duplicate inputs if required? (Usually `i > start && nums[i] == nums[i-1]`).
    **重複項：** 如果需要，我是否處理了重複輸入？（通常是 `i > start && nums[i] == nums[i-1]`）。

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Save Point" Analogy (存檔點類比)
Imagine playing a video game.
想像在玩電子遊戲。
1.  **Save Game (Push):** Before entering a dangerous dungeon, you save your state.
    **存檔（Push）：** 在進入危險地牢前，你儲存狀態。
2.  **Explore (Recurse):** You fight through the dungeon.
    **探索（Recurse）：** 你在地牢中戰鬥。
3.  **Load Game (Pop):** If you die (invalid state) or beat the boss (solution found), you reload the save to try a different path or collect other items.
    **讀檔（Pop）：** 如果你死了（無效狀態）或打敗了魔王（找到解），你重新讀取存檔以嘗試不同路徑或收集其他物品。

### Visual Anchor (視覺錨點)
**"The Claw" (夾娃娃機):**
The claw goes down (recursion deepens), grabs something (adds to path), comes back up (backtracks/pops), and moves to the next position (next iteration).
爪子向下（遞迴加深），抓取東西（加入路徑），回到上方（回溯/彈出），然後移動到下一個位置（下一次迭代）。