這裡是一份針對 **Backtracking (回溯法)** 的進階面試教材，專為具備 7–12 年經驗的資深工程師設計。
Here is an advanced interview guide for **Backtracking**, designed for Senior Engineers with 7–12 years of experience.

本教材採用 C++ 撰寫，並特別針對熟悉 Python/TypeScript 的開發者強調記憶體管理與效能優化的細節。
This guide is written in C++, with specific emphasis on memory management and performance optimization details for developers familiar with Python/TypeScript.

---

# Advanced Backtracking Guide (進階回溯法指南)

## 1. Learning Objectives (學習目標)

1.  **掌握狀態空間樹的剪枝技術 (Master Pruning Techniques in State Space Trees)**
    學會如何透過排序、邊界檢查與啟發式方法，儘早終止無效路徑，將 $O(N!)$ 的複雜度降至可接受範圍。
    Learn how to terminate invalid paths early using sorting, boundary checks, and heuristics to reduce $O(N!)$ complexity to an acceptable range.

2.  **區分回溯與動態規劃 (Distinguish Backtracking from Dynamic Programming)**
    理解何時該用純回溯（尋找所有解），何時該結合 Memoization（Top-down DP），以及如何處理重疊子問題。
    Understand when to use pure backtracking (finding all solutions), when to combine it with Memoization (Top-down DP), and how to handle overlapping subproblems.

3.  **精通 C++ 的狀態管理 (Master State Management in C++)**
    針對 Python/TS 背景者，深入理解 C++ 中 `pass-by-reference` 與 `pass-by-value` 在遞迴中的效能差異與狀態還原（undo）機制。
    For those with Python/TS backgrounds, deeply understand the performance differences between `pass-by-reference` and `pass-by-value` in recursion, and the state restoration (undo) mechanism in C++.

4.  **處理高階變體 (Handle Advanced Variations)**
    熟悉 Bitmask 優化狀態表示，以及處理重複元素（Symmetry Breaking）的高級技巧。
    Familiarize yourself with Bitmask optimization for state representation and advanced techniques for handling duplicate elements (Symmetry Breaking).

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
回溯法是一種透過遞迴構建解的演算法，它在狀態空間樹中進行深度優先搜尋 (DFS)。
Backtracking is an algorithmic-technique that builds a solution recursively by performing a Depth-First Search (DFS) on a state space tree.

當發現當前路徑無法導向有效解時，它會取消上一步的變更（Backtrack/Undo）並嘗試其他路徑。
When it determines that the current path cannot lead to a valid solution, it undoes the last change (Backtrack/Undo) and tries other paths.

### Intuition (直覺)
想像你在走迷宮，手裡拿著一條線。
Imagine you are walking through a maze holding a string.
每走到一個分岔口，你選擇一條路並放線；如果是死胡同，你捲回線（Undo）回到分岔口，走另一條路。
At each fork, you choose a path and unspool the string; if it's a dead end, you roll the string back (Undo) to the fork and take another path.

### Complexity (複雜度)
*   **Time:** 通常是階乘級 $O(N!)$ 或指數級 $O(k^N)$。這是 NP-Hard 問題的通解。
    Usually factorial $O(N!)$ or exponential $O(k^N)$. This is the general solution for NP-Hard problems.
*   **Space:** $O(N)$，取決於遞迴深度（Stack depth）。
    $O(N)$, depending on the recursion depth (Stack depth).

### When to Use (適用場景)
*   尋找**所有**可能的解（如 N-Queens, Sudoku）。
    Finding **all** possible solutions (e.g., N-Queens, Sudoku).
*   組合優化問題，且無法使用 Greedy 或 Polynomial-time DP 解決時。
    Combinatorial optimization problems where Greedy or Polynomial-time DP cannot be applied.

---

## 3. Typical Patterns (典型題型 / 模式)

對於資深工程師，我們關注以下三種進階模式：
For Senior Engineers, we focus on these three advanced patterns:

1.  **Combinatorial Search with Deduplication (含去重的組合搜尋)**
    *   **Context:** Subsets II, Permutations II.
    *   **Key:** Sort input first. Skip adjacent duplicates at the same recursion level (`if (i > start && nums[i] == nums[i-1]) continue`).
    *   **關鍵：** 先排序輸入。在同一遞迴層級跳過相鄰的重複項。

2.  **Constraint Satisfaction Problems (CSP) with Bitmask (帶位元遮罩的約束滿足問題)**
    *   **Context:** N-Queens, Sudoku, Tiling problems.
    *   **Key:** Use an integer (bitmask) to track visited columns/diagonals instead of HashSets/Arrays for $O(1)$ checks and lower constant factors.
    *   **關鍵：** 使用整數（位元遮罩）來追蹤已訪問的行/對角線，取代 HashSet/Array，以達到 $O(1)$ 檢查並降低常數因子。

3.  **Partitioning Problems (分割問題)**
    *   **Context:** Partition to K Equal Sum Subsets.
    *   **Key:** Requires aggressive pruning (sorting, boundary checks) to pass time limits.
    *   **關鍵：** 需要激進的剪枝（排序、邊界檢查）才能通過時間限制。

---

## 4. Example Walkthrough (範例講解)

### Problem: Partition to K Equal Sum Subsets (LeetCode 698)
**難度：Medium-Hard (Advanced Context)**

**問題重述 (Problem Restatement):**
給定一個整數陣列 `nums` 和一個整數 `k`，請判斷是否能將該陣列分割成 `k` 個非空子集，使得每個子集的總和相等。
Given an integer array `nums` and an integer `k`, return true if it is possible to divide this array into `k` non-empty subsets whose sums are all equal.

### Thought Process (思路)

1.  **Initial Check (初步檢查):**
    總和 `sum(nums)` 必須能被 `k` 整除。如果不能，直接返回 `false`。
    The total sum `sum(nums)` must be divisible by `k`. If not, return `false` immediately.
    目標子集和 `target = sum / k`。
    The target subset sum is `target = sum / k`.

2.  **Brute Force (暴力解):**
    嘗試將每個數字放入 `k` 個桶子（buckets）中的一個。
    Try to put each number into one of the `k` buckets.
    這會導致 $O(k^N)$ 的複雜度，對於 $N=16$ 來說太慢。
    This leads to $O(k^N)$ complexity, which is too slow for $N=16$.

3.  **Optimization (優化 - The Senior Engineer approach):**
    *   **Sort Descending (降序排序):** 先處理大數字。如果大數字無法填滿桶子，我們能更快失敗（Fail Fast）。
        Process larger numbers first. If large numbers cannot fit into buckets, we can fail faster.
    *   **Bucket-centric vs. Number-centric:** 逐個填滿桶子（填滿一個再填下一個）通常比「每個數字選桶子」更容易剪枝。
        Filling buckets one by one (fill one, then move to the next) is usually easier to prune than "choosing a bucket for each number".

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <numeric>
#include <algorithm>
#include <functional>

using namespace std;

class Solution {
public:
    bool canPartitionKSubsets(vector<int>& nums, int k) {
        int totalSum = accumulate(nums.begin(), nums.end(), 0);
        
        // 邊界條件：總和必須能被 k 整除
        // Boundary condition: Total sum must be divisible by k
        if (k <= 0 || totalSum % k != 0) return false;
        
        int target = totalSum / k;
        
        // 優化 1：降序排序，這對於剪枝至關重要
        // Optimization 1: Sort descending, crucial for pruning
        sort(nums.rbegin(), nums.rend());
        
        // 如果最大的數字已經超過目標值，直接失敗
        // If the largest number exceeds the target, fail immediately
        if (nums[0] > target) return false;

        // 使用 vector<bool> 來追蹤元素是否已被使用
        // Use vector<bool> to track if an element has been used
        // Note: vector<bool> is a specialized template in C++, space efficient but be careful with references.
        vector<bool> visited(nums.size(), false);
        
        return backtrack(nums, visited, k, 0, 0, target);
    }

private:
    /**
     * @param k: 剩餘需要填滿的桶子數量 (Remaining buckets to fill)
     * @param currentSum: 當前桶子的累積和 (Current accumulated sum of the bucket)
     * @param startIdx: 搜尋的起始索引，避免重複計算 (Search start index to avoid redundant computation)
     */
    bool backtrack(const vector<int>& nums, vector<bool>& visited, int k, int currentSum, int startIdx, int target) {
        // Base Case: 如果只剩下 1 個桶子，且之前的都填滿了，最後一個一定能填滿（數學性質）
        // Base Case: If only 1 bucket remains and others are filled, the last one fits (mathematical property)
        if (k == 1) return true;
        
        // 如果當前桶子已滿，遞迴處理下一個桶子 (k-1)，重置 currentSum 和 startIdx
        // If current bucket is full, recurse for the next bucket (k-1), reset currentSum and startIdx
        if (currentSum == target) {
            return backtrack(nums, visited, k - 1, 0, 0, target);
        }
        
        for (int i = startIdx; i < nums.size(); ++i) {
            // 剪枝：如果已使用，或加上當前數字超過目標，跳過
            // Pruning: If used, or adding current number exceeds target, skip
            if (visited[i] || currentSum + nums[i] > target) continue;
            
            // 做選擇 (Make move)
            visited[i] = true;
            
            // 遞迴 (Recurse)
            if (backtrack(nums, visited, k, currentSum + nums[i], i + 1, target)) {
                return true;
            }
            
            // 撤銷選擇 (Backtrack / Undo)
            visited[i] = false;
            
            // 優化 2：如果當前桶子是空的，且放入 nums[i] 後失敗了，那麼放入任何其他同樣大小的數字也會失敗（或者因為它是第一個，如果不選它也無法構成解），直接剪枝。
            // Optimization 2: If current bucket is empty and putting nums[i] fails, then no need to try other numbers for this empty bucket state.
            if (currentSum == 0) return false;
        }
        
        return false;
    }
};
```

### Complexity Analysis (複雜度分析)
*   **Time:** $O(k \cdot 2^N)$。最壞情況下仍是指數級，但排序與剪枝大幅減少了實際執行時間。
    $O(k \cdot 2^N)$. Still exponential in the worst case, but sorting and pruning significantly reduce actual runtime.
*   **Space:** $O(N)$。用於遞迴堆疊與 `visited` 陣列。
    $O(N)$. For recursion stack and the `visited` array.

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Python/TS Behavior | C++ Behavior & Pitfall |
| :--- | :--- | :--- |
| **State Passing** | List/Object are references by default. Need explicit copy (slicing/spread) to isolate states. | **Critical:** Passing `vector` by value copies the whole array ($O(N)$ cost). **Always pass by reference (`vector<int>&`)** and manually undo changes. |
| **Backtracking Logic** | `path + [x]` creates a new list (implicit copy). | `path.push_back(x)` modifies in-place. You **must** `path.pop_back()` after recursion returns. |
| **Mutable Defaults** | Python's mutable default arg trap. | C++ doesn't have this specific trap, but static variables in functions are dangerous in interviews. |
| **Visited Set** | `set` is hash-based ($O(1)$). | `std::set` is Tree-based ($O(\log N)$). Use `std::unordered_set` or `vector<bool>`/`bitset` for $O(1)$. |

**Senior Tip:**
在 C++ 面試中，忘記寫 `&` (reference) 導致的 TLE (Time Limit Exceeded) 是非常常見的失敗原因。
In C++ interviews, forgetting the `&` (reference), leading to TLE (Time Limit Exceeded), is a very common reason for failure.

---

## 6. Interview Strategy (面試實戰建議)

### Verbal Framework (口條框架)
1.  **Define the State (定義狀態):**
    "I will use a backtracking function that tracks `currentIndex` and `currentPath`."
    「我將使用一個回溯函數，追蹤『當前索引』與『當前路徑』。」

2.  **Discuss the Tree (討論樹狀結構):**
    "At each step, we have `N` branches. The depth is `M`. Without pruning, the complexity is..."
    「每一步我們有 `N` 個分支，深度為 `M`。若不剪枝，複雜度為...」

3.  **Propose Pruning (提出剪枝):**
    "Since we need unique combinations, I will sort the input to handle duplicates easily."
    「因為我們需要唯一的組合，我會先排序輸入以便處理重複項。」

### Whiteboard Strategy (白板策略)
*   **Template First:** 先寫出回溯的骨架（Base case, Loop, Choose, Recurse, Un-choose）。
    Write the backtracking skeleton first (Base case, Loop, Choose, Recurse, Un-choose).
*   **Helper Function:** 將主要邏輯放在 `solve()` 或 `backtrack()` 私有函數中，保持主函數乾淨。
    Keep the main logic in a private `solve()` or `backtrack()` helper function to keep the main function clean.

### Common Follow-ups
*   "Can you do this iteratively?" (Stack simulation).
    「你能用迭代方式實作嗎？」（使用 Stack 模擬）。
*   "What if the input is too large?" (Discuss heuristics, randomized restart, or approximation).
    「如果輸入太大怎麼辦？」（討論啟發式算法、隨機重啟或近似解）。

---

## 7. Practice Problems (練習題)

### 1. Easy/Intermediate: Combination Sum (LeetCode 39)
*   **Hint:** 允許重複選擇同一元素。
    Allow repeated selection of the same element.
*   **Key:** `backtrack(start_index)` -> pass `i` (not `i+1`) to next recursion.
*   **關鍵：** 遞迴時傳入 `i` 而非 `i+1`。

### 2. Intermediate: Generate Parentheses (LeetCode 22)
*   **Hint:** 追蹤 `open` 和 `close` 的數量。
    Track the count of `open` and `close` parentheses.
*   **Constraint:** `open < n` to add `(`, `close < open` to add `)`.
*   **約束：** `open < n` 可加 `(`，`close < open` 可加 `)`。

### 3. Advanced: N-Queens II (LeetCode 52) - Bitmask Optimization
*   **Hint:** 不要儲存整個棋盤。使用三個整數（位元遮罩）分別代表：列、主對角線、副對角線。
    Do not store the whole board. Use three integers (bitmasks) to represent: columns, main diagonals, and anti-diagonals.
*   **Logic:** `(cols | diag1 | diag2)` indicates occupied positions.
*   **邏輯：** `(cols | diag1 | diag2)` 表示被佔用的位置。

---

## 8. Quick Checklists (快速檢核表)

在寫完程式碼後，請在腦中快速掃描：
After coding, quickly scan this list mentally:

- [ ] **Base Case:** 遞迴有終止條件嗎？ (Does recursion have a termination condition?)
- [ ] **State Restoration:** 所有的 `push_back` 都有對應的 `pop_back` 嗎？ (Does every `push_back` have a corresponding `pop_back`?)
- [ ] **Reference:** 傳遞大物件（vector/string）時是否使用了 `&`？ (Did you use `&` when passing large objects?)
- [ ] **Return Value:** 如果只需要找到**一個**解，是否在遞迴返回 `true` 時立即回傳？ (If only **one** solution is needed, do you return immediately when recursion returns `true`?)
- [ ] **Pruning:** 是否處理了明顯無效的情況？ (Did you handle obviously invalid cases?)

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The "Dr. Strange" Analogy (奇異博士類比)
回溯法就像奇異博士在《復仇者聯盟：無限之戰》中查看 14,000,605 種未來。
Backtracking is like Dr. Strange viewing 14,000,605 futures in "Avengers: Infinity War".
*   **State:** 時間線上的某個時刻 (A moment in the timeline).
*   **Recursion:** 進入一個可能的未來 (Entering a possible future).
*   **Pruning:** 看到薩諾斯贏了，立即停止該時間線的觀察 (Seeing Thanos win and immediately stopping that timeline observation).
*   **Backtracking:** 回到當下，嘗試另一個決定 (Returning to the present to try a different decision).

### Visual Anchor (圖像錨點)
記住 **"Do -> Recurse -> Undo"** 三明治結構。
Remember the **"Do -> Recurse -> Undo"** sandwich structure.
*   上層麵包：`visited[i] = true;`
*   內餡：`backtrack(...);`
*   下層麵包：`visited[i] = false;`