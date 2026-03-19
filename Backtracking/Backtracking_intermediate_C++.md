Here is the comprehensive guide on **Backtracking**, tailored for a Senior Software Engineer targeting Big Tech interviews, with C++ as the implementation language.

這是一份針對 **Backtracking (回溯法)** 的完整指南，專為目標鎖定 Big Tech 面試的資深軟體工程師量身打造，並使用 C++ 作為實作語言。

---

# Backtracking Interview Guide (Intermediate)
# 回溯法面試指南（中階）

## 1. Learning Objectives (學習目標)

*   **Master the Standard Template:** Internalize the "Choose, Explore, Un-choose" structure to implement any backtracking solution rapidly.
    **掌握標準模板：** 內化「選擇、探索、取消選擇」的結構，以快速實作任何回溯解決方案。
*   **Pruning Techniques:** Learn how to identify invalid branches early to optimize time complexity significantly.
    **剪枝技巧：** 學習如何儘早識別無效分支，顯著優化時間複雜度。
*   **State Management:** Understand the difference between passing state by value versus by reference in C++, and how it affects memory and correctness.
    **狀態管理：** 理解 C++ 中按值傳遞與按引用傳遞狀態的差異，以及其對記憶體和正確性的影響。
*   **Complexity Analysis:** Be able to articulate the time complexity of combinatorial problems (e.g., $O(N!)$, $O(2^N)$).
    **複雜度分析：** 能夠清晰表達組合問題的時間複雜度（例如 $O(N!)$、$O(2^N)$）。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
Backtracking is an algorithmic-technique for solving problems recursively by trying to build a solution incrementally, one piece at a time, removing those solutions that fail to satisfy the constraints of the problem at any point of time.
回溯法是一種遞迴演算法技巧，透過一次構建一部分的方式逐步嘗試建立解決方案，並在任何時間點若發現當前方案不滿足約束條件，則移除該方案（回退）。

### Intuition (直覺)
Think of it as a Depth-First Search (DFS) on a "State Tree" or "Decision Tree."
將其視為在「狀態樹」或「決策樹」上進行的深度優先搜尋（DFS）。
You walk down a path until you hit a dead end or find a solution, then you return to the previous junction to try a different path.
你沿著一條路徑走，直到遇到死胡同或找到解答，然後返回上一個路口嘗試另一條路徑。

### Complexity (複雜度)
*   **Time:** Often exponential or factorial. Examples: $O(2^N)$ for subsets, $O(N!)$ for permutations.
    **時間：** 通常是指數級或階乘級。例如：子集問題為 $O(2^N)$，排列問題為 $O(N!)$。
*   **Space:** $O(H)$ where $H$ is the height of the recursion tree (stack depth), plus space for the solution.
    **空間：** $O(H)$，其中 $H$ 是遞迴樹的高度（堆疊深度），加上儲存解答的空間。

### When to Use (適用場景)
*   Find **all** solutions (e.g., all permutations, all valid parentheses).
    尋找 **所有** 解答（例如：所有排列、所有合法的括號組合）。
*   Find **one** valid solution under complex constraints (e.g., Sudoku, N-Queens).
    在複雜約束下尋找 **一個** 有效解答（例如：數獨、N 皇后問題）。

### When NOT to Use (不適用場景)
*   Find the **optimal** solution (min/max) where overlapping subproblems exist (Use Dynamic Programming).
    尋找存在重疊子問題的 **最佳** 解（極大/極小值）（應使用動態規劃）。
*   Simple connectivity problems in graphs (Use BFS/DFS or Union-Find).
    圖論中的簡單連通性問題（應使用 BFS/DFS 或 Union-Find）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Combinations / Subsets (組合 / 子集)
*   Order does not matter (`[1, 2]` is same as `[2, 1]`).
    順序不重要（`[1, 2]` 與 `[2, 1]` 視為相同）。
*   **Key:** Use a `start_index` to avoid reusing previous elements and prevent duplicates.
    **關鍵：** 使用 `start_index` 來避免重複使用先前的元素並防止重複組合。

### B. Permutations (排列)
*   Order matters (`[1, 2]` is different from `[2, 1]`).
    順序重要（`[1, 2]` 與 `[2, 1]` 視為不同）。
*   **Key:** Use a `visited` array or swap elements to track usage.
    **關鍵：** 使用 `visited` 陣列或交換元素來追蹤使用情況。

### C. Grid Traversal (網格遍歷)
*   Searching for patterns in a 2D grid (e.g., Word Search).
    在二維網格中搜尋模式（例如：單詞搜尋）。
*   **Key:** Mark current cell as visited before recursion and unmark it after (backtracking).
    **關鍵：** 遞迴前將當前格子標記為已訪問，遞迴後取消標記（回溯）。

### D. Constraint Satisfaction (約束滿足)
*   Placing items under strict rules (e.g., N-Queens, Sudoku).
    在嚴格規則下放置項目（例如：N 皇后、數獨）。
*   **Key:** `isValid()` function is the core logic for pruning.
    **關鍵：** `isValid()` 函數是剪枝的核心邏輯。

---

## 4. Example Walkthrough (範例講解)

### Problem: Combination Sum (LeetCode 39)
**Problem Statement:** Given an array of **distinct** integers `candidates` and a target integer `target`, return a list of all **unique combinations** of `candidates` where the chosen numbers sum to `target`. You may choose the same number an unlimited number of times.
**問題重述：** 給定一個由 **相異** 整數組成的陣列 `candidates` 和一個目標整數 `target`，回傳所有 `candidates` 中數字總和等於 `target` 的 **唯一組合**。你可以無限次選擇同一個數字。

### Thought Process (思路)

1.  **Brute Force / Intuition:** We can decide for every number: "Take it" or "Don't take it". Since we can reuse numbers, if we "Take it", we stay at the same index.
    **暴力法 / 直覺：** 對於每個數字，我們可以決定：「選它」或「不選它」。由於可以重複使用數字，如果我們「選它」，我們停留在當前索引。
2.  **Optimization (Pruning):** If the current sum exceeds `target`, stop immediately. If we sort the array first, we can stop even earlier in the loop.
    **優化（剪枝）：** 如果當前總和超過 `target`，立即停止。如果我們先對陣列排序，甚至可以在迴圈中更早停止。
3.  **Base Case:** `target == 0` (Found a solution), `target < 0` (Fail).
    **基本情況：** `target == 0`（找到解答），`target < 0`（失敗）。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>

using namespace std;

class Solution {
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> result;
        vector<int> currentPath;
        
        // Sorting helps with pruning (though not strictly necessary for correctness, it speeds up).
        // 排序有助於剪枝（雖然對正確性非絕對必要，但能加速）。
        sort(candidates.begin(), candidates.end());
        
        backtrack(candidates, target, 0, currentPath, result);
        return result;
    }

private:
    void backtrack(const vector<int>& candidates, int remain, int start, 
                   vector<int>& currentPath, vector<vector<int>>& result) {
        
        // Base Case 1: Goal reached
        // 基本情況 1：達成目標
        if (remain == 0) {
            result.push_back(currentPath); // Make a deep copy of the path (複製當前路徑)
            return;
        }
        
        // Base Case 2: Exceeded target (Pruning logic handled in loop usually, but good for safety)
        // 基本情況 2：超過目標（剪枝邏輯通常在迴圈中處理，但此處為安全起見）
        if (remain < 0) {
            return;
        }

        // Iterate through candidates starting from 'start' to avoid duplicates in combinations
        // 從 'start' 開始遍歷候選者，以避免組合中的重複
        for (int i = start; i < candidates.size(); ++i) {
            
            // Pruning: If current number is already greater than remainder, no need to proceed
            // 剪枝：如果當前數字已經大於剩餘值，則無需繼續
            if (candidates[i] > remain) break; 

            // 1. Choose (選擇)
            currentPath.push_back(candidates[i]);
            
            // 2. Explore (探索)
            // Note: We pass 'i' not 'i + 1' because we can reuse the same element
            // 注意：我們傳遞 'i' 而非 'i + 1'，因為我們可以重複使用相同元素
            backtrack(candidates, remain - candidates[i], i, currentPath, result);
            
            // 3. Un-choose / Backtrack (取消選擇 / 回溯)
            currentPath.pop_back();
        }
    }
};
```

### Common Mistake Example (錯誤示範)

```cpp
// ERROR: Missing the "Un-choose" step
// 錯誤：缺少「取消選擇」步驟
for (int i = start; i < candidates.size(); ++i) {
    currentPath.push_back(candidates[i]);
    backtrack(candidates, remain - candidates[i], i, currentPath, result);
    // currentPath.pop_back(); // <--- FORGOT THIS! (忘記這行！)
}
```
**Why it's wrong:** The `currentPath` keeps growing indefinitely. When the recursion returns, the state is dirty, affecting subsequent branches.
**為何錯誤：** `currentPath` 會無限增長。當遞迴返回時，狀態已被污染，影響後續的分支。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Permutation vs. Combination** | **Permutation:** Order matters (`[1,2] != [2,1]`). Start loop from `0`, use `visited` array.<br>**Combination:** Order irrelevant (`[1,2] == [2,1]`). Start loop from `start_index`.<br>**排列：** 順序重要。迴圈從 `0` 開始，使用 `visited` 陣列。<br>**組合：** 順序無關。迴圈從 `start_index` 開始。 |
| **Mutable vs. Immutable State** | In Python, lists are references. In C++, `vector` is passed by value unless `&` is used.<br>**Pitfall:** Passing `vector` by value in C++ recursion is $O(N)$ copy cost per call. Always pass by `const reference` (`const vector<int>&`) and maintain a single `currentPath` buffer.<br>**可變與不可變狀態：** C++ 中 `vector` 除非使用 `&` 否則是按值傳遞。<br>**陷阱：** 遞迴中按值傳遞 `vector` 會導致每次呼叫產生 $O(N)$ 複製成本。務必使用 `const reference` 並維護單一 `currentPath` 緩衝區。 |
| **Pruning vs. Base Case** | **Base Case:** Stops recursion when a condition is met (valid or invalid).<br>**Pruning:** Prevents entering a recursive call entirely if it's known to be invalid.<br>**基本情況：** 滿足條件時停止遞迴。<br>**剪枝：** 若已知無效，則完全阻止進入遞迴呼叫。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Define the State:** "I will model this as a state-space tree where each node represents..."
    **定義狀態：** 「我會將此建模為狀態空間樹，其中每個節點代表……」
2.  **Define the Choices:** "At each step, our choices are..."
    **定義選擇：** 「在每一步，我們的選擇是……」
3.  **Define Constraints (Pruning):** "We can prune the search if..."
    **定義約束（剪枝）：** 「如果……我們可以剪枝搜尋。」
4.  **Complexity:** "Since we are generating subsets/permutations, the worst-case time complexity is..."
    **複雜度：** 「由於我們正在生成子集/排列，最壞情況下的時間複雜度是……」

### Whiteboard Strategy (白板策略)
*   Write the **Template Skeleton** first (`result`, `path`, `backtrack` function). This buys you thinking time and shows structure.
    先寫下 **模板骨架**（`result`、`path`、`backtrack` 函數）。這能爭取思考時間並展現結構。
*   Use helper functions like `isValid()` to keep the main logic clean.
    使用如 `isValid()` 的輔助函數來保持主邏輯清晰。

### Common Follow-ups (常見追問)
*   "How would you handle duplicates in the input?" (Answer: Sort first + skip adjacent duplicates).
    「你會如何處理輸入中的重複項？」（答：先排序 + 跳過相鄰的重複項）。
*   "Can you do this iteratively?" (Answer: Yes, using an explicit Stack, but it's more complex to manage state).
    「你能用迭代方式實作嗎？」（答：可以，使用顯式堆疊，但狀態管理更複雜）。

---

## 7. Practice Problems (練習題)

### Level 1: Subsets (Easy/Intermediate)
**Problem:** Given unique integers, return all possible subsets.
**問題：** 給定唯一整數，回傳所有可能的子集。
*   **Hint:** For each number, you have two choices: include it or exclude it.
*   **提示：** 對於每個數字，你有兩個選擇：包含它或排除它。
*   **Focus:** Correctly managing the `start_index`.
*   **重點：** 正確管理 `start_index`。

### Level 2: Word Search (Intermediate)
**Problem:** Check if a word exists in a 2D grid of characters (moving adjacent cells).
**問題：** 檢查單詞是否存在於二維字元網格中（移動至相鄰格子）。
*   **Hint:** This is Graph DFS + Backtracking. Mark cells as `#` to denote visited, then restore original char after returning.
*   **提示：** 這是圖論 DFS + 回溯。將格子標記為 `#` 表示已訪問，返回後恢復原始字元。
*   **Focus:** Boundary checks and state restoration.
*   **重點：** 邊界檢查與狀態恢復。

### Level 3: N-Queens (Hard)
**Problem:** Place N queens on an NxN chessboard so no two queens attack each other.
**問題：** 在 NxN 棋盤上放置 N 個皇后，使得沒有兩個皇后互相攻擊。
*   **Hint:** Use three sets/arrays to track columns, diagonals (`row-col`), and anti-diagonals (`row+col`).
*   **提示：** 使用三個集合/陣列來追蹤列、對角線 (`row-col`) 和反對角線 (`row+col`)。
*   **Focus:** Efficient `isValid` checking ($O(1)$ instead of $O(N)$).
*   **重點：** 高效的 `isValid` 檢查（$O(1)$ 而非 $O(N)$）。

---

## 8. Quick Checklists (快速檢核表)

Use this during your mock interview or self-review:
在模擬面試或自我審查時使用此表：

- [ ] **Base Case:** Does the recursion terminate? (Are you checking bounds/target?)
    **基本情況：** 遞迴會終止嗎？（是否檢查了邊界/目標？）
- [ ] **State Restoration:** Do you `pop_back()` or reset the `visited` flag after the recursive call?
    **狀態恢復：** 遞迴呼叫後是否有 `pop_back()` 或重置 `visited` 標誌？
- [ ] **References:** Are you passing `result` and `path` by reference (`&`)?
    **引用：** 是否按引用 (`&`) 傳遞 `result` 和 `path`？
- [ ] **Duplicates:** If inputs have duplicates, did you sort and add `if (i > start && nums[i] == nums[i-1]) continue;`?
    **重複項：** 如果輸入有重複，是否排序並添加了去重邏輯？
- [ ] **Return Value:** Should the helper function return `void` (find all) or `bool` (find one)?
    **回傳值：** 輔助函數應該回傳 `void`（找所有）還是 `bool`（找一個）？

---

## 9. Memory Anchors (記憶錨點)

### The "Save Point" Analogy (「存檔點」類比)
Imagine playing a video game.
想像在玩電子遊戲。
1.  **Save Game (Push State):** Before entering a boss room (recursive call), you save.
    **存檔（推入狀態）：** 進入魔王房間（遞迴呼叫）前，你存檔。
2.  **Play (Explore):** You fight the boss.
    **遊玩（探索）：** 你與魔王戰鬥。
3.  **Load Game (Pop State):** If you die (invalid path) or win and want to try a different difficulty, you reload the save to restore the world exactly as it was.
    **讀檔（彈出狀態）：** 如果你死了（無效路徑）或贏了但想嘗試不同難度，你讀取存檔，將世界恢復到原本的樣子。

### Visualizing the Template (視覺化模板)

```text
      [Root]
     /      \
  (Do)      (Do)    <-- 1. Choose (加入)
   /          \
[Child]     [Child] <-- 2. Recurse (遞迴)
   |           |
(Undo)      (Undo)  <-- 3. Un-choose (撤銷)
```