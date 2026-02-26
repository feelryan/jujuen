# Advanced Backtracking: Pruning & State Compression
# 進階回溯法：剪枝與狀態壓縮

## 1. Learning Goals（學習目標）

*   **Master Advanced Pruning Techniques:** Learn how to identify "dead ends" early to drastically reduce the search space.
    **掌握進階剪枝技巧：** 學習如何儘早識別「死胡同」，以大幅縮減搜尋空間。
*   **Implement State Compression (Bitmasking):** Use bits to represent visited states or sets, optimizing both space and time complexity.
    **實作狀態壓縮（位元遮罩）：** 使用位元來表示已訪問的狀態或集合，優化空間與時間複雜度。
*   **Analyze Exponential Complexity:** Accurately estimate time complexity for NP-complete problems and explain trade-offs to interviewers.
    **分析指數級複雜度：** 準確估算 NP 完全問題的時間複雜度，並向面試官解釋權衡取捨。
*   **Differentiate Backtracking from DP:** Understand when memoization turns backtracking into Top-Down Dynamic Programming.
    **區分回溯法與動態規劃：** 理解何時透過記憶化（Memoization）將回溯法轉變為由上而下的動態規劃。

---

## 2. Core Concepts at a Glance（核心觀念速覽）

### Definition（定義）
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time, removing those solutions that fail to satisfy the constraints of the problem at any point of time.
回溯法是一種遞迴演算法技巧，透過一次構建一部分的方式逐步建立解，並在任何時間點發現當前解不符合約束條件時，移除該解（回退）。

### Intuition（直覺）
Think of it as a Depth-First Search (DFS) on a "State Tree" or "Decision Tree".
將其視為在「狀態樹」或「決策樹」上進行的深度優先搜尋（DFS）。
You make a choice, explore recursively, and if it doesn't work, you **undo** (backtrack) the choice and try the next one.
你做出一個選擇，遞迴探索，如果行不通，你**撤銷**（回溯）該選擇並嘗試下一個。

### Complexity（複雜度）
*   **Time:** Generally exponential, $O(b^d)$, where $b$ is the branching factor and $d$ is the depth.
    **時間：** 通常是指數級，$O(b^d)$，其中 $b$ 是分支因子， $d$ 是深度。
*   **Space:** $O(d)$ for the recursion stack.
    **空間：** $O(d)$ 用於遞迴堆疊。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** You need to find **all** solutions, or when the problem is NP-Complete (e.g., Sudoku, N-Queens, TSP) and no polynomial solution exists.
    **適用於：** 你需要找出**所有**解，或者問題屬於 NP 完全問題（如數獨、八皇后、旅行推銷員問題），且不存在多項式時間解法時。
*   **Do NOT Use when:** A greedy approach works, or the problem has optimal substructure and overlapping subproblems (use DP).
    **不適用於：** 貪婪演算法可行，或問題具有最佳子結構與重疊子問題（應使用動態規劃）時。

---

## 3. Typical Patterns / Modes（典型題型 / 模式）

For Senior Engineers, we move beyond simple permutations.
對於資深工程師，我們超越簡單的排列組合。

1.  **Combinatorial Search with Pruning (組合搜尋與剪枝):**
    Finding subsets or partitions that satisfy strict constraints (e.g., Partition to K Equal Sum Subsets).
    尋找滿足嚴格約束條件的子集或劃分（例如：劃分為 K 個等和子集）。
2.  **Grid/Matrix DFS with Backtracking (網格/矩陣 DFS 回溯):**
    Pathfinding with mutable states (e.g., Word Search II, Unique Paths III).
    具有可變狀態的路徑尋找（例如：單字搜尋 II、不同路徑 III）。
3.  **Bitmasking Backtracking (位元遮罩回溯):**
    Using an integer to track used elements instead of a boolean array/set for performance.
    使用整數而非布林陣列/集合來追蹤已使用的元素，以提升效能。

---

## 4. Example Walkthrough（範例講解）

### Problem: Partition to K Equal Sum Subsets
### 問題：劃分為 K 個等和子集

**Problem Statement:**
Given an integer array `nums` and an integer `k`, return `true` if it is possible to divide this array into `k` non-empty subsets whose sums are all equal.
給定一個整數陣列 `nums` 和一個整數 `k`，如果可以將此陣列劃分為 `k` 個非空子集，且其和皆相等，則返回 `true`。

**Constraints:** `1 <= k <= nums.length <= 16`, `0 < nums[i] < 10^4`.
**限制條件：** `1 <= k <= nums.length <= 16`，`0 < nums[i] < 10^4`。

---

### Strategy: From Naive to Optimized（思路：從暴力到優化）

#### 1. Naive Approach (暴力法)
Try to put every number into one of the `k` buckets recursively.
遞迴嘗試將每個數字放入 `k` 個桶子中的一個。
*   **Complexity:** $O(k^N)$. With $N=16, k=4$, this is massive.
    **複雜度：** $O(k^N)$。當 $N=16, k=4$ 時，這非常巨大。

#### 2. Optimization Strategy (Senior Level Thinking) (優化策略——資深思維)
We need **Pruning (剪枝)**.
我們需要 **剪枝**。

1.  **Global Pre-check:** If `totalSum % k != 0`, return false immediately.
    **全域預檢查：** 如果 `totalSum % k != 0`，立即返回 false。
2.  **Sorting:** Sort `nums` in **descending** order. Placing larger numbers first triggers failures faster (fail-fast), reducing the search tree.
    **排序：** 將 `nums` 進行**降序**排列。先放置較大的數字能更快觸發失敗（快速失敗），從而縮減搜尋樹。
3.  **Bucket Logic:** Instead of "which bucket does this number go to?", ask "can we fill the current bucket completely?". This changes the perspective to filling one bucket at a time.
    **桶子邏輯：** 不要問「這個數字去哪個桶子？」，而是問「我們能填滿當前這個桶子嗎？」。這將視角轉變為一次填滿一個桶子。
4.  **Used Array (Bitmask):** Since $N \le 16$, we can use a bitmask to track used numbers.
    **使用狀態（位元遮罩）：** 由於 $N \le 16$，我們可以使用位元遮罩來追蹤已使用的數字。

---

### TypeScript Reference Solution（TypeScript 參考解）

```typescript
/**
 * Determines if the array can be partitioned into k subsets with equal sum.
 * 判斷陣列是否可以劃分為 k 個等和子集。
 */
function canPartitionKSubsets(nums: number[], k: number): boolean {
    const totalSum = nums.reduce((a, b) => a + b, 0);
    
    // Basic check: if total sum is not divisible by k, impossible.
    // 基本檢查：如果總和不能被 k 整除，則不可能。
    if (totalSum % k !== 0) return false;
    
    const targetSum = totalSum / k;
    
    // Sort descending to facilitate pruning (fail fast).
    // 降序排列以利於剪枝（快速失敗）。
    nums.sort((a, b) => b - a);
    
    // If the largest number is bigger than target, impossible.
    // 如果最大的數字比目標和大，則不可能。
    if (nums[0] > targetSum) return false;

    const n = nums.length;
    // Use a bitmask to represent visited state (1 << 16 is small enough).
    // 使用位元遮罩表示訪問狀態（1 << 16 足夠小）。
    // However, for clarity in this example, we use a boolean array or simple recursion arguments.
    // 但為了本範例的清晰度，我們使用布林陣列或簡單的遞迴參數。
    // Let's stick to the "fill one bucket at a time" approach with a used array.
    // 我們採用「一次填滿一個桶子」的方法搭配 used 陣列。
    const used = new Uint8Array(n); // 0: unused, 1: used

    /**
     * Backtracking function
     * @param kBucket - Number of buckets left to fill (剩餘需要填滿的桶子數量)
     * @param currentBucketSum - Sum of the current bucket being filled (當前正在填充的桶子總和)
     * @param startIndex - Index in nums to start searching from (nums 中開始搜尋的索引)
     */
    const backtrack = (kBucket: number, currentBucketSum: number, startIndex: number): boolean => {
        // Base case: If only 1 bucket is left, the rest of numbers must sum up to target.
        // 基本情況：如果只剩 1 個桶子，剩下的數字總和必然等於目標值。
        // (Because totalSum is fixed and divisible).
        // (因為總和是固定的且可整除)。
        if (kBucket === 1) return true;

        // If current bucket is full, move to the next bucket, reset sum and start index.
        // 如果當前桶子已滿，移動到下一個桶子，重置總和與開始索引。
        if (currentBucketSum === targetSum) {
            return backtrack(kBucket - 1, 0, 0);
        }

        // Try to put numbers into the current bucket.
        // 嘗試將數字放入當前桶子。
        for (let i = startIndex; i < n; i++) {
            // Skip if used or if adding it exceeds target.
            // 如果已使用或加入後超過目標值，則跳過。
            if (used[i] || currentBucketSum + nums[i] > targetSum) continue;

            // Important Pruning: Handle duplicates.
            // 重要剪枝：處理重複元素。
            // If current number is same as previous and previous was not used, skip current.
            // 如果當前數字與前一個相同，且前一個未被使用，則跳過當前數字。
            if (i > 0 && nums[i] === nums[i - 1] && !used[i - 1]) continue;

            // Choose (選擇)
            used[i] = 1;

            // Explore (探索)
            if (backtrack(kBucket, currentBucketSum + nums[i], i + 1)) {
                return true;
            }

            // Un-choose (Backtrack) (取消選擇/回溯)
            used[i] = 0;

            // Advanced Pruning (Optimization):
            // 進階剪枝（優化）：
            
            // 1. If we are at the start of a new bucket (currentBucketSum == 0) and this attempt failed,
            // it means the current number `nums[i]` cannot be part of ANY valid partition solution 
            // starting a new subset. Since we must use every number, we can stop here.
            // 1. 如果我們在一個新桶子的開始（currentBucketSum == 0）且這次嘗試失敗了，
            // 這意味著當前數字 `nums[i]` 無法成為任何有效劃分方案中新子集的起始。
            // 由於我們必須使用每個數字，我們可以就此停止。
            if (currentBucketSum === 0) return false;
        }

        return false;
    };

    return backtrack(k, 0, 0);
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall |
| :--- | :--- |
| **Permutation vs Combination** | **Permutation:** Order matters `[1,2] != [2,1]`. Use `visited` array. <br> **Combination:** Order doesn't matter `[1,2] == [2,1]`. Use `startIndex` to avoid going back. <br> **排列：** 順序重要。使用 `visited` 陣列。<br> **組合：** 順序不重要。使用 `startIndex` 避免回頭。 |
| **Shallow Copy vs Deep Copy** | In JS/TS, pushing an array `path` to `results` stores a reference. <br> **Trap:** `results.push(path)` leads to all empty arrays after backtracking. <br> **Fix:** `results.push([...path])`. <br> **淺拷貝與深拷貝：** 在 JS/TS 中，將陣列 `path` 推入 `results` 儲存的是參考。<br> **陷阱：** `results.push(path)` 會導致回溯後所有陣列變空。<br> **修正：** `results.push([...path])`。 |
| **Loop Scope vs Recursion** | Confusing the loop (iterating choices at *current* level) with recursion (going *deeper*). <br> **迴圈範圍與遞迴：** 混淆迴圈（在*當前*層級遍歷選擇）與遞迴（進入*更深*層級）。 |

---

## 6. Interview Strategy（面試實戰建議）

### Verbal Framework（口條框架）
1.  **State the Space:** "This problem asks for all possibilities/partitions, which suggests a backtracking approach."
    **陳述空間：** 「這個問題要求所有可能性/劃分，這暗示了使用回溯法。」
2.  **Define the State:** "I need to track `currentIndex`, `currentSum`, and `visited` elements."
    **定義狀態：** 「我需要追蹤 `currentIndex`（當前索引）、`currentSum`（當前總和）以及 `visited`（已訪問）元素。」
3.  **Propose Pruning (The Senior Delta):** "A naive DFS is $O(k^N)$. I will optimize by sorting descending and pruning branches where the sum exceeds the target."
    **提出剪枝（資深差異點）：** 「暴力的 DFS 是 $O(k^N)$。我會透過降序排列以及剪除總和超過目標的分支來進行優化。」

### Whiteboard Strategy（白板策略）
*   Write the **Base Case** first. It anchors your logic.
    先寫**基本情況（Base Case）**。這能穩定你的邏輯。
*   Write the **Choose -> Explore -> Unchoose** pattern clearly.
    清晰地寫出 **選擇 -> 探索 -> 取消選擇** 的模式。
*   Separate the `isValid` logic into a helper function if complex.
    如果 `isValid` 邏輯很複雜，將其分離為輔助函式。

---

## 7. Practice Problems（練習題）

### 1. Easy (Warm-up): Generate Parentheses
*   **Goal:** Generate all well-formed parentheses.
    **目標：** 生成所有格式正確的括號組合。
*   **Hint:** Track `open` and `close` counts. Only add `)` if `close < open`.
    **提示：** 追蹤 `open` 和 `close` 的數量。只有當 `close < open` 時才加入 `)`。

### 2. Medium (Standard): Word Search
*   **Goal:** Find if a word exists in a grid.
    **目標：** 在網格中尋找單字是否存在。
*   **Hint:** Mark cells as visited (e.g., with `#`) before recursion and restore them after.
    **提示：** 遞迴前將單元格標記為已訪問（例如使用 `#`），遞迴後恢復。

### 3. Hard (Advanced): Tiling a Rectangle with the Fewest Squares
*   **Goal:** Cut a `n x m` rectangle into minimum number of squares.
    **目標：** 將 `n x m` 的矩形切割成最少數量的正方形。
*   **Hint:** This is a classic backtracking with **skyline** representation or bitmasking. You try to fill the lowest empty spot with all possible square sizes.
    **提示：** 這是經典的回溯法，使用 **天際線（skyline）** 表示法或位元遮罩。嘗試用所有可能的正方形尺寸填補最低的空缺。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Base Case:** Does the recursion terminate correctly? (e.g., `index === n` or `sum === target`)
    **基本情況：** 遞迴是否正確終止？（例如 `index === n` 或 `sum === target`）
*   [ ] **State Reset:** Did I undo the changes to global/passed-by-reference variables?
    **狀態重置：** 我是否撤銷了對全域變數或傳引用變數的更改？
*   [ ] **Pruning:** Did I add `if (current > target) return` or similar logic?
    **剪枝：** 我是否加入了 `if (current > target) return` 或類似的邏輯？
*   [ ] **Result Copy:** Did I deep copy the solution before adding to the result list?
    **結果複製：** 在加入結果列表前，我是否深拷貝了解答？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Maze Explorer" (迷宮探險家)
Imagine you are in a maze with a ball of string (Ariadne's thread).
想像你在一個迷宮中，拿著一團線（阿里阿德涅之線）。
*   **Choose:** You walk down a path and unwind the string.
    **選擇：** 你走下一條路並放線。
*   **Explore:** You look for the exit.
    **探索：** 你尋找出口。
*   **Backtrack:** Dead end? You walk back, **winding the string back up** (reset state), and try the other path.
    **回溯：** 死胡同？你往回走，**將線捲回去**（重置狀態），然後嘗試另一條路。

### The "Decision Tree" (決策樹)
Visualize the code not as loops, but as a tree growing downwards.
不要將程式碼想像成迴圈，而是想像成一棵向下生長的樹。
*   **Pruning:** Cutting off a dead branch early so you don't waste time climbing down it.
    **剪枝：** 儘早砍掉枯死的樹枝，這樣就不必浪費時間爬下去。