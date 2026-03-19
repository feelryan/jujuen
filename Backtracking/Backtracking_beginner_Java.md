Here is a comprehensive guide to **Backtracking**, tailored for a Senior Software Engineer (Python/TS background) looking to master Java for interviews. This guide focuses on the **Beginner** level of Backtracking, establishing the foundational mental models and templates.

這是一份針對 **回溯法 (Backtracking)** 的完整教材，專為熟悉 Python/TS 的資深軟體工程師（Senior Software Engineer）設計，旨在協助您掌握 Java 面試實戰。本指南專注於 **初學者（Beginner）** 難度，重點在於建立穩固的心智模型與標準解題模板。

---

# Backtracking: The Art of Controlled Brute Force
# 回溯法：受控的暴力搜索藝術

## 1. Learning Goals (學習目標)

*   **Understand the "State Space Tree" concept:** Visualize the problem as a tree where every edge is a decision.
    **理解「狀態空間樹」概念：** 將問題視覺化為一棵樹，其中每一條邊代表一個決策。
*   **Master the Standard Template:** Internalize the `Choose -> Explore -> Un-choose` pattern.
    **掌握標準模板：** 內化「選擇 -> 探索 -> 撤銷選擇」的模式。
*   **Handle Java References Correctly:** Avoid the common pitfall of storing mutable list references in the result set.
    **正確處理 Java 參照：** 避免將可變列表（Mutable List）的參照直接存入結果集的常見陷阱。
*   **Differentiate Permutations vs. Combinations:** Know when to use a `start` index and when to use a `visited` array.
    **區分排列與組合：** 知道何時該使用 `start` 索引，何時該使用 `visited` 陣列。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Backtracking is a general algorithm for finding all (or some) solutions to some computational problems, notably constraint satisfaction problems, that incrementally builds candidates to the solutions.
回溯法是一種通用演算法，用於尋找計算問題的所有（或部分）解，特別是約束滿足問題，它透過逐步建構候選解來運作。

It abandons a candidate ("backtracks") as soon as it determines that the candidate cannot possibly be completed to a valid solution.
一旦確定某個候選解無法完成為有效解，它就會立即放棄該候選解（「回溯」）。

### Intuition (直覺)
Think of it as walking through a maze.
把它想像成走迷宮。
You choose a path; if it leads to a dead end, you return to the previous junction and try a different path.
你選擇一條路徑；如果它通向死胡同，你退回到上一個路口並嘗試另一條路徑。

### Complexity (複雜度)
*   **Time:** Usually Exponential ($O(2^N)$) or Factorial ($O(N!)$). It is essentially an optimized brute force.
    **時間：** 通常是指數級 ($O(2^N)$) 或階乘級 ($O(N!)$)。它本質上是一種優化的暴力搜索。
*   **Space:** $O(N)$ for the recursion stack, where $N$ is the depth of the decision tree.
    **空間：** $O(N)$ 用於遞迴堆疊，其中 $N$ 是決策樹的深度。

### When to Use (適用場景)
*   Find **all** solutions (e.g., all subsets, all permutations).
    尋找 **所有** 解（例如：所有子集、所有排列）。
*   Constraint Satisfaction (e.g., Sudoku, N-Queens).
    約束滿足問題（例如：數獨、八皇后）。

### When NOT to Use (不適用場景)
*   Find the **shortest/min/max** path/value (Usually BFS or DP is better).
    尋找 **最短/最小/最大** 路徑或數值（通常 BFS 或 DP 更好）。
*   Connectivity problems (Union-Find or simple DFS/BFS).
    連通性問題（使用 Union-Find 或簡單的 DFS/BFS）。

---

## 3. Typical Patterns (典型題型 / 模式)

For beginners, most backtracking problems fall into two categories based on how we traverse the candidates.
對於初學者來說，大多數回溯問題根據我們遍歷候選解的方式分為兩類。

### Pattern A: Combinations / Subsets (組合 / 子集)
*   **Order does not matter:** `[1, 2]` is the same as `[2, 1]`.
    **順序不重要：** `[1, 2]` 與 `[2, 1]` 視為相同。
*   **Mechanism:** Use a `start` index to ensure we only move forward in the input array to avoid duplicates.
    **機制：** 使用 `start` 索引確保我們在輸入陣列中只向前移動，以避免重複。

### Pattern B: Permutations (排列)
*   **Order matters:** `[1, 2]` is different from `[2, 1]`.
    **順序重要：** `[1, 2]` 與 `[2, 1]` 視為不同。
*   **Mechanism:** Iterate through all elements every time, but use a `visited` array (or check existence) to skip used elements.
    **機制：** 每次都遍歷所有元素，但使用 `visited` 陣列（或檢查是否存在）來跳過已使用的元素。

---

## 4. Example Walkthrough (範例講解)

### Problem: Subsets (LeetCode 78)
**Problem Statement:** Given an integer array `nums` of unique elements, return all possible subsets (the power set).
**問題重述：** 給定一個包含唯一元素的整數陣列 `nums`，返回所有可能的子集（冪集）。

### Thought Process (思路)

1.  **Naive Approach (Iterative):** Start with an empty set `[]`. For each number in `nums`, add it to all existing sets.
    **暴力法（迭代）：** 從空集 `[]` 開始。對於 `nums` 中的每個數字，將其加入到所有現有的集合中。
2.  **Backtracking Approach:** We view this as a decision tree. For each number, we have two choices: **include it** or **exclude it**.
    **回溯法思路：** 我們將其視為決策樹。對於每個數字，我們有兩個選擇：**包含它** 或 **不包含它**。
3.  **Optimization:** Since we need *all* subsets, we don't prune branches here. We just traverse the tree.
    **優化：** 由於我們需要 *所有* 子集，這裡不做剪枝。我們只是遍歷整棵樹。

### Java Reference Solution (Java 參考解)

```java
import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        // Start backtracking from index 0 with an empty path
        // 從索引 0 開始回溯，路徑為空
        backtrack(result, new ArrayList<>(), nums, 0);
        return result;
    }

    private void backtrack(List<List<Integer>> result, List<Integer> path, int[] nums, int start) {
        // Goal: Add the current path to the result
        // 目標：將當前路徑加入結果集
        // CRITICAL: We must create a deep copy (new ArrayList), otherwise we store a reference to 'path' which keeps changing.
        // 關鍵：必須建立深拷貝 (new ArrayList)，否則我們存入的是 'path' 的參照，它會不斷改變。
        result.add(new ArrayList<>(path));

        // Choice: Iterate through the remaining numbers
        // 選擇：遍歷剩餘的數字
        for (int i = start; i < nums.length; i++) {
            // 1. Choose (Make a move)
            // 1. 選擇（採取行動）
            path.add(nums[i]);

            // 2. Explore (Recurse)
            // Pass 'i + 1' not 'start + 1' to move forward
            // 2. 探索（遞迴）
            // 傳入 'i + 1' 而非 'start + 1' 以向前移動
            backtrack(result, path, nums, i + 1);

            // 3. Un-choose (Backtrack/Undo)
            // Remove the last element added to return to previous state
            // 3. 撤銷選擇（回溯/復原）
            // 移除最後加入的元素以回到上一個狀態
            path.remove(path.size() - 1);
        }
    }
}
```

### Complexity (複雜度)
*   **Time:** $O(N \times 2^N)$. There are $2^N$ subsets, and copying each subset takes $O(N)$ on average.
    **時間：** $O(N \times 2^N)$。共有 $2^N$ 個子集，複製每個子集平均需要 $O(N)$。
*   **Space:** $O(N)$ for recursion stack depth.
    **空間：** $O(N)$ 用於遞迴堆疊深度。

### Error Demonstration (錯誤示範)

```java
// WRONG: Storing the reference
// 錯誤：儲存參照
result.add(path); 
// Outcome: You will end up with a list of empty lists [[], [], ... []] because 'path' is cleared at the end of recursion.
// 結果：你最終會得到一堆空列表 [[], [], ... []]，因為 'path' 在遞迴結束時被清空了。
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation | Java Specific Pitfall |
| :--- | :--- | :--- |
| **Mutable References** | Modifying the `path` object affects all recursive calls sharing it. <br> 修改 `path` 物件會影響所有共用它的遞迴呼叫。 | Forgetting `new ArrayList<>(path)` when adding to result. <br> 加入結果時忘記 `new ArrayList<>(path)`。 |
| **Loop Bounds** | `i = start` vs `i = 0`. <br> `i = start` 對比 `i = 0`。 | Use `i = start` for Combinations (no duplicates). Use `i = 0` + `visited` for Permutations. <br> 組合問題用 `i = start`（無重複）。排列問題用 `i = 0` 加上 `visited`。 |
| **Backtracking Step** | Removing the last element. <br> 移除最後一個元素。 | Forgetting `path.remove(path.size() - 1)`. The path will grow indefinitely. <br> 忘記 `path.remove(...)`。路徑會無限增長。 |
| **Base Case** | When to stop recursion. <br> 何時停止遞迴。 | In "Subsets", every node is a solution, so no explicit return is needed inside the loop. In others (e.g., Permutations), you stop when `path.size() == nums.length`. <br> 在「子集」問題中，每個節點都是解，所以迴圈內不需要顯式返回。在其他問題（如排列）中，當 `path.size() == nums.length` 時停止。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Identify:** "This asks for all possibilities, which suggests a backtracking approach."
    **識別：** 「這題要求所有可能性，這暗示了解法是回溯法。」
2.  **Define State:** "I will maintain a `path` list representing the current subset and a `start` index to handle duplicates."
    **定義狀態：** 「我會維護一個 `path` 列表代表當前子集，以及一個 `start` 索引來處理重複。」
3.  **Draw the Tree:** Quickly sketch the first 2 levels of the recursion tree on the whiteboard.
    **畫樹：** 在白板上快速畫出遞迴樹的前兩層。

### Whiteboard Strategy (白板策略)
*   Write the `backtrack` helper function signature first. It clarifies what state you need to pass.
    先寫下 `backtrack` 輔助函式的簽名。這能釐清你需要傳遞什麼狀態。
*   Use generic names like `path`, `res`, `visited` to make code readable.
    使用通用的變數名稱如 `path`, `res`, `visited` 來增加程式碼可讀性。

### Common Follow-up (常見追問)
*   **Q:** "How to handle duplicates in the input (e.g., `[1, 2, 2]`)?"
    **問：** 「如何處理輸入中的重複元素（例如 `[1, 2, 2]`）？」
*   **A:** "Sort the input first, then inside the loop, skip if `i > start && nums[i] == nums[i-1]`."
    **答：** 「先對輸入排序，然後在迴圈內，如果 `i > start && nums[i] == nums[i-1]` 則跳過。」

---

## 7. Practice Problems (練習題)

### 1. Easy: Letter Combinations of a Phone Number (LeetCode 17)
*   **Hint:** Map digits to string (e.g., '2' -> "abc"). Loop through the characters of the current digit.
    **提示：** 將數字映射到字串（如 '2' -> "abc"）。遍歷當前數字對應的字元。
*   **Key:** No `start` index needed for the loop, but an index to track which digit in the input string we are processing.
    **關鍵：** 迴圈不需要 `start` 索引，但需要一個索引來追蹤正在處理輸入字串的哪一個數字。

### 2. Medium: Permutations (LeetCode 46)
*   **Hint:** Order matters. Loop from `0` to `n-1` every time.
    **提示：** 順序很重要。每次都從 `0` 迴圈到 `n-1`。
*   **Key:** Use `path.contains(nums[i])` (slow) or a `boolean[] visited` array (fast) to avoid reusing elements.
    **關鍵：** 使用 `path.contains(nums[i])`（較慢）或 `boolean[] visited` 陣列（較快）來避免重複使用元素。

### 3. Medium/Hard: Combination Sum (LeetCode 39)
*   **Hint:** You can reuse the same number unlimited times.
    **提示：** 你可以無限次重複使用同一個數字。
*   **Key:** When recursing, pass `i` instead of `i + 1` as the `start` index. Base case is `target == 0` (found) or `target < 0` (exceeded).
    **關鍵：** 遞迴時，傳入 `i` 而不是 `i + 1` 作為 `start` 索引。基本情況是 `target == 0`（找到）或 `target < 0`（超過）。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interviews or debugging:
在模擬面試或除錯時使用此表：

- [ ] **Copy Result:** Did I write `res.add(new ArrayList<>(path))`?
    **複製結果：** 我是否寫了 `res.add(new ArrayList<>(path))`？
- [ ] **Backtrack Step:** Did I remove the last element after the recursive call?
    **回溯步驟：** 我是否在遞迴呼叫後移除了最後一個元素？
- [ ] **Base Case:** Does the recursion terminate correctly?
    **基本情況：** 遞迴是否正確終止？
- [ ] **Loop Range:** Is it `int i = start` (Combinations) or `int i = 0` (Permutations)?
    **迴圈範圍：** 是 `int i = start`（組合）還是 `int i = 0`（排列）？
- [ ] **Duplicate Handling:** If input has duplicates, did I sort and prune?
    **重複處理：** 如果輸入有重複，我是否排序並剪枝了？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Ctrl+Z" Analogy (Ctrl+Z 類比)
Backtracking is essentially typing a document.
回溯法本質上就像打文件。
1.  Type a character (Make a choice / `path.add`).
    打一個字（做選擇 / `path.add`）。
2.  Check if it looks good (Explore / `backtrack`).
    檢查看起來是否正確（探索 / `backtrack`）。
3.  **Ctrl+Z** (Undo / `path.remove`).
    **Ctrl+Z**（復原 / `path.remove`）。

### The "Snapshot" Analogy (快照類比)
When you add `path` to `result`, imagine you are taking a **Polaroid photo** (Snapshot/Deep Copy) of your current arrangement. If you don't take a photo, you are just handing the interviewer the physical objects, which you will rearrange later.
當你將 `path` 加入 `result` 時，想像你正在為當前的排列拍一張 **拍立得**（快照/深拷貝）。如果你不拍照，你只是把實體物件交給面試官，而你稍後還會重新排列這些物件。