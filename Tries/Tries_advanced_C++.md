Here is the comprehensive guide on **Tries (Prefix Trees)**, tailored for a Senior Software Engineer, focusing on advanced patterns and C++ implementation.

這是一份針對 **Tries（前綴樹）** 的完整指南，專為資深軟體工程師量身打造，著重於進階模式與 C++ 實作。

---

# Advanced Data Structures: Tries (Prefix Trees)
# 進階資料結構：Tries（前綴樹）

## 1. Learning Objectives (學習目標)

1.  **Master the Bitwise Trie for XOR Optimization.**
    掌握用於 XOR 優化的位元前綴樹（Bitwise Trie）。
    *Unlike standard string Tries, Bitwise Tries are a frequent differentiator in Senior-level algorithmic interviews.*
    *不同於標準字串 Trie，位元 Trie 是資深演算法面試中常見的決勝點。*

2.  **Understand Space-Time Trade-offs (Array vs. Map).**
    理解空間與時間的權衡（陣列 vs. 雜湊表）。
    *Analyze when to use `vector<Node*>(26)` for speed versus `unordered_map<char, Node*>` for sparsity.*
    *分析何時為了速度使用 `vector<Node*>(26)`，何時為了稀疏性使用 `unordered_map<char, Node*>`。*

3.  **Integrate Tries with Backtracking (DFS).**
    整合 Trie 與回溯法（DFS）。
    *Solve complex grid search problems (like Boggle) efficiently by pruning search branches early.*
    *透過提早剪枝，高效解決複雜的網格搜尋問題（如 Boggle）。*

4.  **Implement Production-Ready Code in C++.**
    用 C++ 實作可上線等級的程式碼。
    *Focus on memory management (pointers/destructors) and clean encapsulation.*
    *著重於記憶體管理（指標/解構函式）與乾淨的封裝。*

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Trie is a tree-like data structure used to store a dynamic set of strings where the keys are usually strings.
Trie 是一種樹狀資料結構，用於儲存動態字串集合，其中的鍵值通常是字串。

### Intuition (直覺)
Instead of storing the whole string in a node, each node represents a character.
每個節點不儲存完整字串，而是代表一個字元。
The path from the root to a node represents the prefix of a string.
從根節點到某節點的路徑代表字串的前綴。

### Complexity (複雜度)
- **Time (時間):** $O(L)$ for insert/search, where $L$ is the length of the string.
  插入/搜尋皆為 $O(L)$，其中 $L$ 為字串長度。
  *Note: This is often faster than a Hash Map in practice because Hash Map has overhead for hashing and collisions, effectively $O(L)$ as well.*
  *註：實務上這常比雜湊表快，因為雜湊表有雜湊計算與碰撞的開銷，實際上也是 $O(L)$。*
- **Space (空間):** $O(N \times L \times \Sigma)$ in the worst case, where $N$ is the number of keys and $\Sigma$ is the alphabet size.
  最差情況下為 $O(N \times L \times \Sigma)$，其中 $N$ 是鍵的數量，$\Sigma$ 是字母集大小。

### When to Use (適用場景)
1.  **Prefix Matching:** Autocomplete, spell checker, IP routing (Longest Prefix Match).
    **前綴匹配：** 自動完成、拼字檢查、IP 路由（最長前綴匹配）。
2.  **Bitwise Operations:** Finding maximum XOR pair in an array.
    **位元運算：** 在陣列中尋找最大 XOR 對。
3.  **Dictionary Search:** Validating words in a character grid (Word Search II).
    **字典搜尋：** 驗證字元網格中的單字（Word Search II）。

### When NOT to Use (不適用場景)
1.  **Random Access:** If you need to access data by index or arbitrary keys not based on prefixes.
    **隨機存取：** 如果你需要透過索引或非前綴的任意鍵來存取資料。
2.  **Memory Constraints:** Standard Tries can be memory-heavy compared to a well-tuned Hash Map or Bloom Filter if the dataset is sparse.
    **記憶體限制：** 如果資料集很稀疏，標準 Trie 比起調校良好的雜湊表或 Bloom Filter 可能更佔記憶體。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Standard Trie (String Manipulation)
**標準 Trie（字串操作）**
- Operations: `insert`, `search`, `startsWith`.
- Optimization: Store a boolean `isEnd` or a counter `passCount` at each node.
- 優化：在每個節點儲存布林值 `isEnd` 或計數器 `passCount`。

### B. Bitwise Trie (XOR Problems)
**位元 Trie（XOR 問題）**
- Treat integers as 32-bit binary strings.
- 把整數視為 32 位元的二進位字串。
- Tree height is fixed at 32 (or 31).
- 樹的高度固定為 32（或 31）。
- **Greedy Strategy:** To maximize XOR, try to go to the opposite bit branch (0 vs 1) at each step.
- **貪婪策略：** 為了最大化 XOR，每一步都嘗試走相反的位元分支（0 對 1）。

### C. Trie + DFS (Backtracking)
**Trie + DFS（回溯法）**
- Used for searching words in a 2D grid.
- 用於在二維網格中搜尋單字。
- The Trie acts as a pruning mechanism: if the current prefix doesn't exist in the Trie, stop DFS immediately.
- Trie 作為剪枝機制：如果當前前綴不存在於 Trie 中，立即停止 DFS。

---

## 4. Example Walkthrough (範例講解)

### Problem: Maximum XOR of Two Numbers in an Array
### 問題：陣列中兩個數字的最大 XOR 值

**Level:** Advanced (Hard)
**Source:** LeetCode 421

#### Problem Statement (問題重述)
Given an integer array `nums`, return the maximum result of `nums[i] XOR nums[j]`.
給定一個整數陣列 `nums`，回傳 `nums[i] XOR nums[j]` 的最大值。

#### Approach (思路)

1.  **Brute Force (暴力法):**
    - Double loop to check every pair.
    - 雙重迴圈檢查每一對。
    - Time: $O(N^2)$. Too slow for $N=10^5$.
    - 時間：$O(N^2)$。對於 $N=10^5$ 太慢。

2.  **Optimization with Trie (Trie 優化):**
    - Insert all numbers into a binary Trie (MSB to LSB).
    - 將所有數字插入二進位 Trie（從最高有效位到最低有效位）。
    - For each number `x`, find the "best match" `y` in the Trie that maximizes `x ^ y`.
    - 對於每個數字 `x`，在 Trie 中找到「最佳匹配」`y`，使得 `x ^ y` 最大。
    - **Key Insight:** If the current bit of `x` is `b`, we want the corresponding bit of `y` to be `1-b` (opposite) to make the XOR result `1`.
    - **關鍵洞察：** 如果 `x` 的當前位元是 `b`，我們希望 `y` 的對應位元是 `1-b`（相反），這樣 XOR 結果才會是 `1`。

3.  **Complexity (複雜度):**
    - Time: $O(N \times 32)$ $\approx O(N)$.
    - Space: $O(N \times 32)$.

#### C++ Solution (C++ 參考解)

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

// Trie Node definition
// Trie 節點定義
struct TrieNode {
    // Array to store children: index 0 for bit '0', index 1 for bit '1'
    // 儲存子節點的陣列：索引 0 代表位元 '0'，索引 1 代表位元 '1'
    TrieNode* children[2];
    
    TrieNode() {
        children[0] = nullptr;
        children[1] = nullptr;
    }
};

class Solution {
private:
    TrieNode* root;

    // Helper: Insert a number into the Trie
    // 輔助函式：將數字插入 Trie
    void insert(int num) {
        TrieNode* node = root;
        // Iterate from 31st bit down to 0 (32-bit integer)
        // 從第 31 位元迭代到 0（32 位元整數）
        for (int i = 31; i >= 0; i--) {
            // Extract the i-th bit
            // 取出第 i 個位元
            int bit = (num >> i) & 1;
            if (!node->children[bit]) {
                node->children[bit] = new TrieNode();
            }
            node = node->children[bit];
        }
    }

    // Helper: Find maximum XOR for a specific number
    // 輔助函式：為特定數字尋找最大 XOR
    int getMaxXor(int num) {
        TrieNode* node = root;
        int maxVal = 0;
        for (int i = 31; i >= 0; i--) {
            int bit = (num >> i) & 1;
            // We desire the opposite bit to maximize XOR (1^0 = 1, 0^1 = 1)
            // 我們渴望相反的位元以最大化 XOR（1^0 = 1, 0^1 = 1）
            if (node->children[1 - bit]) {
                maxVal |= (1 << i); // Set the i-th bit of result to 1
                                    // 將結果的第 i 個位元設為 1
                node = node->children[1 - bit];
            } else {
                // If opposite not available, forced to go same path (XOR result 0)
                // 如果相反位元不存在，被迫走相同路徑（XOR 結果為 0）
                node = node->children[bit];
            }
        }
        return maxVal;
    }

public:
    int findMaximumXOR(vector<int>& nums) {
        root = new TrieNode();
        
        // Build the Trie
        // 建構 Trie
        for (int num : nums) {
            insert(num);
        }
        
        int maxResult = 0;
        // Query for each number
        // 對每個數字進行查詢
        for (int num : nums) {
            maxResult = max(maxResult, getMaxXor(num));
        }
        
        // Note: In a real interview, discuss memory cleanup (destructor)
        // 註：在實際面試中，請討論記憶體清理（解構函式）
        return maxResult;
    }
};
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Contrast (解釋與對比) |
| :--- | :--- |
| **Trie vs. Hash Map** | **Hash Map:** $O(L)$ average, but unpredictable collisions and no prefix logic.<br>**Trie:** Guaranteed $O(L)$, supports ordered iteration and prefix queries.<br>**雜湊表：** 平均 $O(L)$，但有不可預測的碰撞且無前綴邏輯。<br>**Trie：** 保證 $O(L)$，支援有序迭代與前綴查詢。 |
| **Memory Leak (C++)** | In C++, simply creating `new TrieNode()` without deleting causes leaks.<br>**Fix:** Use `unique_ptr` or implement a recursive destructor.<br>在 C++ 中，僅 `new TrieNode()` 而不刪除會導致洩漏。<br>**解法：** 使用 `unique_ptr` 或實作遞迴解構函式。 |
| **Array vs. Map Nodes** | **Array (`next[26]`):** Faster access, more memory (sparse nodes waste space).<br>**Map (`map<char, Node*>`):** Slower access, saves memory for sparse trees.<br>**陣列：** 存取較快，較耗記憶體（稀疏節點浪費空間）。<br>**Map：** 存取較慢，節省稀疏樹的記憶體。 |
| **Termination Flag** | Forgetting `isEnd` means you can't distinguish between "apple" and "app".<br>忘記 `isEnd` 意味著你無法區分 "apple" 和 "app"。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (口條框架)
1.  **Identify the pattern:** "This problem involves prefix matching / XOR maximization, which suggests a Trie structure."
    **識別模式：** 「這個問題涉及前綴匹配 / XOR 最大化，這暗示了 Trie 結構。」
2.  **Define the Node:** "I'll start by defining a `TrieNode` struct. Since inputs are lowercase English letters, a fixed array of size 26 is optimal for time complexity."
    **定義節點：** 「我會先定義 `TrieNode` 結構。由於輸入是小寫英文字母，大小為 26 的固定陣列對時間複雜度最優。」
3.  **Implement Insert:** "Insertion is straightforward, traversing down and creating nodes as needed."
    **實作插入：** 「插入很直觀，向下遍歷並視需要建立節點。」
4.  **Implement Logic:** "Now for the core logic (search/XOR)..."
    **實作邏輯：** 「現在進入核心邏輯（搜尋/XOR）...」

### Whiteboard Strategy (白板策略)
- **Draw the Tree:** Quickly sketch a root with 'a', 'b' branches to visualize the path.
  **畫出樹：** 快速畫出根節點與 'a', 'b' 分支以視覺化路徑。
- **Keep Node Simple:** Don't over-engineer the class. A `struct` is fine for algorithms.
  **保持節點簡單：** 不要過度設計類別。對於演算法題，`struct` 就足夠了。

### Common Follow-ups (常見追問)
- **Q:** How to optimize space if the strings contain full Unicode?
  **問：** 如果字串包含完整的 Unicode，如何優化空間？
  **A:** Use `unordered_map<char, TrieNode*>` instead of a fixed array.
  **答：** 使用 `unordered_map<char, TrieNode*>` 代替固定陣列。
- **Q:** How to handle deletion?
  **問：** 如何處理刪除？
  **A:** Need a post-order traversal (recursion) to delete nodes that are no longer part of any key (reference counting helps).
  **答：** 需要後序遍歷（遞迴）來刪除不再屬於任何鍵的節點（引用計數會有幫助）。

---

## 7. Practice Problems (練習題)

### 1. Implement Trie II (Prefix Count) - Intermediate
**題目：** 實作 Trie II（前綴計數）- 中等
**Goal:** Implement `insert`, `countWordsEqualTo`, `countWordsStartingWith`, `erase`.
**目標：** 實作插入、計算相等單字數、計算以前綴開頭的單字數、刪除。
**Hint:** Add `int prefixCount` and `int wordCount` to each node.
**提示：** 在每個節點增加 `int prefixCount` 和 `int wordCount`。

### 2. Word Search II - Advanced
**題目：** 單字搜尋 II - 進階
**Goal:** Find all words from a dictionary in a 2D board.
**目標：** 在二維棋盤中找出字典裡的所有單字。
**Hint:** Build Trie from dictionary -> DFS on board. **Optimization:** Remove the word from Trie after finding it to avoid duplicates and prune search.
**提示：** 從字典建構 Trie -> 在棋盤上 DFS。**優化：** 找到單字後將其從 Trie 中移除，以避免重複並剪枝。

### 3. Maximum Genetic Difference Query - Hard
**題目：** 最大基因差異查詢 - 困難
**Goal:** Queries asking for max XOR in a specific path of a tree.
**目標：** 查詢樹中特定路徑上的最大 XOR。
**Hint:** Offline queries + DFS + Bitwise Trie. Add numbers to Trie as you enter a node, remove as you exit (Backtracking).
**提示：** 離線查詢 + DFS + 位元 Trie。進入節點時將數字加入 Trie，離開時移除（回溯法）。

---

## 8. Checklists (快速檢核表)

### Self-Review (自我審查)
- [ ] Did I handle the root node correctly (it should be empty)?
  我是否正確處理根節點（它應該是空的）？
- [ ] Did I mark the end of the word (`isEnd = true`)?
  我是否標記了單字結尾（`isEnd = true`）？
- [ ] **Complexity:** Is my loop $O(L)$ or $O(32)$?
  **複雜度：** 我的迴圈是 $O(L)$ 還是 $O(32)$？
- [ ] **Bounds:** Did I calculate array index `c - 'a'` correctly?
  **邊界：** 我計算陣列索引 `c - 'a'` 是否正確？

### Debugging (除錯)
- [ ] If getting SegFault: Check `if (!node->children[index])` before accessing.
  如果發生 SegFault：存取前檢查 `if (!node->children[index])`。
- [ ] If output is wrong: Check if you are traversing the Trie from Root every time.
  如果輸出錯誤：檢查你是否每次都從 Root 開始遍歷。

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Folder Structure" Analogy (「資料夾結構」類比)
- Imagine a file system.
  想像一個檔案系統。
- **Root** is `/`.
  **根** 是 `/`。
- **Edges** are folder names (characters).
  **邊** 是資料夾名稱（字元）。
- **Nodes** are the folders themselves.
  **節點** 是資料夾本身。
- **isEnd** is a file named `file.txt` inside that folder, indicating a valid path ends here.
  **isEnd** 是資料夾內一個名為 `file.txt` 的檔案，表示有效路徑在此結束。

### The "Router" Analogy (Bitwise Trie) (「路由器」類比)
- For Bitwise Tries, think of a network router matching IP addresses.
  對於位元 Trie，想像網路路由器匹配 IP 位址。
- It looks at bits one by one: `0` go left, `1` go right.
  它逐位查看：`0` 向左走，`1` 向右走。
- To maximize difference (XOR), always try to take the "other" road.
  為了最大化差異（XOR），總是嘗試走「另一條」路。