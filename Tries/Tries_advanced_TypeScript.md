# Advanced Data Structures: Tries (Prefix Trees)
# 進階資料結構：Tries（前綴樹）

## 1. Learning Goals（學習目標）

*   **Master the specific complexity model:** Understand why Tries are $O(L)$ (length of key) rather than $O(\log N)$ (number of keys), and when this trade-off is beneficial.
    **掌握特定的複雜度模型：** 理解為何 Tries 是 $O(L)$（鍵長）而非 $O(\log N)$（鍵數量），以及這種權衡何時是有利的。
*   **Handle advanced variations:** Go beyond basic insertion/search to handle Bitwise Tries (XOR problems) and Tries with backtracking (Grid problems).
    **處理進階變體：** 超越基本的插入/搜尋，掌握位元 Tries（XOR 問題）與結合回溯法的 Tries（網格問題）。
*   **Optimize for Memory and Performance:** Learn techniques like path compression (conceptually) and pruning nodes during traversal to prevent TLE (Time Limit Exceeded).
    **優化記憶體與效能：** 學習路徑壓縮（概念上）與遍歷時的節點修剪技術，以防止 TLE（超時）。
*   **Bridge to System Design:** Understand how Tries form the basis of Typeahead/Autocomplete systems and IP routing tables.
    **連結系統設計：** 理解 Tries 如何構成 Typeahead/自動完成系統與 IP 路由表的基礎。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
A Trie is a tree-like data structure used to store a dynamic set of strings where the keys are usually strings.
Trie 是一種樹狀資料結構，用於儲存動態字串集合，其中的鍵通常是字串。
Unlike a binary search tree, no node in the tree stores the key associated with that node; instead, its position in the tree defines the key.
與二元搜尋樹不同，樹中的節點不儲存與該節點關聯的鍵；相反地，它在樹中的位置定義了該鍵。

### Complexity（複雜度）
*   **Time (Search/Insert):** $O(L)$, where $L$ is the length of the string.
    **時間（搜尋/插入）：** $O(L)$，其中 $L$ 是字串長度。
*   **Space:** $O(N \cdot L \cdot \Sigma)$, where $N$ is the number of keys, $L$ is the average length, and $\Sigma$ is the alphabet size (e.g., 26).
    **空間：** $O(N \cdot L \cdot \Sigma)$，其中 $N$ 是鍵的數量，$L$ 是平均長度，$\Sigma$ 是字母表大小（如 26）。

### When to Use (vs. Hash Map)（適用場景）
1.  **Prefix-based queries:** Finding all keys starting with "app".
    **基於前綴的查詢：** 尋找所有以 "app" 開頭的鍵。
2.  **Sorting:** Traversing a Trie yields strings in lexicographical order.
    **排序：** 遍歷 Trie 可按字典序產出字串。
3.  **Bitwise Optimization:** Solving "Maximum XOR of two numbers" problems (treating bits as paths).
    **位元優化：** 解決「兩數最大 XOR」問題（將位元視為路徑）。

### When NOT to Use（不適用場景）
1.  **Random Access:** Hash Maps are generally faster $O(1)$ and more memory-efficient for exact matches if prefixes don't matter.
    **隨機存取：** 如果前綴不重要，Hash Map 通常在精確匹配上更快 $O(1)$ 且更節省記憶體。
2.  **Memory Constraints:** Tries consume significant memory due to child pointers/references, especially in languages with heavy object overhead like Java or Python (and JS/TS).
    **記憶體限制：** Trie 因存儲子節點指標/引用會消耗大量記憶體，特別是在 Java、Python（以及 JS/TS）等物件開銷較大的語言中。

---

## 3. Typical Patterns（典型題型 / 模式）

### A. Standard Prefix Match（標準前綴匹配）
Used for autocomplete systems. Nodes often store metadata (e.g., `frequency` or `isEnd`).
用於自動完成系統。節點通常儲存元數據（如 `frequency` 或 `isEnd`）。

### B. DFS + Trie (Grid Search)（DFS + Trie 網格搜尋）
Used in "Boggle" or "Word Search" games. The Trie allows you to prune the DFS search space immediately if a prefix doesn't exist.
用於 "Boggle" 或 "Word Search" 遊戲。Trie 允許你在前綴不存在時立即修剪 DFS 搜尋空間。

### C. Bitwise Trie (XOR Trie)（位元 Trie）
Storing integers as 32-bit binary strings. Used to find maximum/minimum XOR pairs in an array.
將整數儲存為 32 位元二進位字串。用於尋找陣列中的最大/最小 XOR 對。

### D. Reverse Trie (Suffix handling)（反向 Trie）
Storing words in reverse order to handle suffix queries (e.g., "Find words ending with 'ing'").
以反向順序儲存單字以處理後綴查詢（例如：「尋找以 'ing' 結尾的單字」）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Word Search II (LeetCode 212) - Hard
**Problem Statement:**
Given an `m x n` board of characters and a list of strings `words`, return all words on the board.
給定一個 `m x n` 的字元網格和一個字串列表 `words`，回傳網格中存在的所有單字。
Each word must be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring.
每個單字必須由順序相鄰儲存格的字母構成，其中相鄰儲存格是指水平或垂直相鄰的儲存格。

### Approach Evolution（思路演進）

#### 1. Brute Force (DFS per Word)（暴力解：對每個單字做 DFS）
Iterate through every word in the list, and for each word, run a DFS on the grid to see if it exists.
遍歷列表中的每個單字，並對每個單字在網格上執行 DFS 以檢查其是否存在。
*   **Complexity:** $O(K \cdot M \cdot N \cdot 4^L)$, where $K$ is number of words.
*   **Verdict:** **TLE (Time Limit Exceeded)**. Repeating the grid traversal for common prefixes (e.g., "apple", "apply") is wasteful.
*   **結論：** **超時**。對共同前綴（如 "apple", "apply"）重複遍歷網格是浪費的。

#### 2. Optimized (Trie + DFS)（優化解：Trie + DFS）
Build a Trie from all `words`. Run DFS on the grid *once*. During DFS, match the current path of characters against the Trie.
從所有 `words` 建構一個 Trie。在網格上執行 *一次* DFS。在 DFS 過程中，將當前的字元路徑與 Trie 進行匹配。
*   If the current character isn't a child of the current Trie node, stop (pruning).
    如果當前字元不是當前 Trie 節點的子節點，則停止（修剪）。
*   **Complexity:** $O(M \cdot N \cdot 4^L)$ in worst case, but practically much faster due to pruning.
    **複雜度：** 最差情況下為 $O(M \cdot N \cdot 4^L)$，但由於修剪，實際上快得多。

#### 3. Further Optimization (Pruning the Trie)（進一步優化：修剪 Trie）
When a word is found, remove it from the Trie (or mark it as found) to avoid adding duplicates to the result set and to prune future search branches that lead to already-found words.
當找到一個單字時，將其從 Trie 中移除（或標記為已找到），以避免將重複項目加入結果集，並修剪通往已找到單字的未來搜尋分支。

### TypeScript Solution (Advanced)

```typescript
class TrieNode {
    // Using a Map for flexibility, or an array[26] for strict performance constraints
    // 使用 Map 增加彈性，或使用 array[26] 以符合嚴格的效能限制
    children: Map<string, TrieNode> = new Map();
    word: string | null = null; // Store the full word at the leaf for easier access // 在葉節點儲存完整單字以便存取
}

class Solution {
    // Directions for grid traversal: up, right, down, left
    // 網格遍歷的方向：上、右、下、左
    private directions = [[-1, 0], [0, 1], [1, 0], [0, -1]];
    private result: string[] = [];

    public findWords(board: string[][], words: string[]): string[] {
        // 1. Build the Trie
        // 1. 建構 Trie
        const root = new TrieNode();
        for (const word of words) {
            let node = root;
            for (const char of word) {
                if (!node.children.has(char)) {
                    node.children.set(char, new TrieNode());
                }
                node = node.children.get(char)!;
            }
            node.word = word; // Mark end of word // 標記單字結尾
        }

        this.result = [];
        const m = board.length;
        const n = board[0].length;

        // 2. DFS on every cell
        // 2. 對每個儲存格執行 DFS
        for (let i = 0; i < m; i++) {
            for (let j = 0; j < n; j++) {
                if (root.children.has(board[i][j])) {
                    this.dfs(board, i, j, root);
                }
            }
        }

        return this.result;
    }

    private dfs(board: string[][], row: number, col: number, parent: TrieNode): void {
        const char = board[row][col];
        const currNode = parent.children.get(char)!;

        // Check if a word ends here
        // 檢查是否有單字在此結束
        if (currNode.word !== null) {
            this.result.push(currNode.word);
            currNode.word = null; // De-duplicate: Ensure we don't add the same word twice // 去重：確保不重複加入相同單字
            
            // Optimization: Pruning leaf nodes could happen here to speed up, 
            // but simply nullifying the word is sufficient for correctness.
            // 優化：在此處修剪葉節點可以加速，但僅將 word 設為 null 已足以保證正確性。
        }

        // Backtracking Logic
        // 回溯邏輯
        board[row][col] = '#'; // Mark as visited // 標記為已訪問

        for (const [dx, dy] of this.directions) {
            const newRow = row + dx;
            const newCol = col + dy;

            if (
                newRow >= 0 && newRow < board.length &&
                newCol >= 0 && newCol < board[0].length &&
                board[newRow][newCol] !== '#' &&
                currNode.children.has(board[newRow][newCol])
            ) {
                this.dfs(board, newRow, newCol, currNode);
            }
        }

        board[row][col] = char; // Restore (Backtrack) // 還原（回溯）
        
        // Advanced Optimization: Leaf Pruning
        // If the current node has no children after traversal, remove it from parent.
        // 進階優化：葉節點修剪
        // 如果遍歷後當前節點沒有子節點，將其從父節點移除。
        if (currNode.children.size === 0) {
            parent.children.delete(char);
        }
    }
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Confusion | Correction / Best Practice |
| :--- | :--- | :--- |
| **Space Complexity** | Thinking Trie is always space-efficient because it shares prefixes. <br> 認為 Trie 總是節省空間，因為它共享前綴。 | **Correction:** Pointers/References are expensive. For sparse datasets with long unique suffixes, Tries can bloat memory. <br> **修正：** 指標/引用很昂貴。對於具有長唯一後綴的稀疏資料集，Trie 會消耗大量記憶體。 |
| **Termination** | Forgetting `isEnd` or `word` flag. <br> 忘記 `isEnd` 或 `word` 標記。 | "apple" exists, but searching for "app" should return false (unless "app" was also inserted). Always check the flag. <br> "apple" 存在，但搜尋 "app" 應回傳 false（除非 "app" 也被插入）。務必檢查標記。 |
| **Map vs Array** | Using `Map` for everything. <br> 什麼都用 `Map`。 | If the charset is fixed (e.g., lowercase 'a'-'z'), `Array(26)` is significantly faster and uses less memory than `Map` or `Object`. <br> 如果字元集固定（如小寫 'a'-'z'），`Array(26)` 比 `Map` 或 `Object` 快得多且更省記憶體。 |
| **Deletion** | Thinking deletion is just `isEnd = false`. <br> 認為刪除只是 `isEnd = false`。 | While correct logically, it leaves "zombie nodes". True deletion requires recursive pruning of nodes with no other children. <br> 雖然邏輯正確，但會留下「殭屍節點」。真正的刪除需要遞迴修剪沒有其他子節點的節點。 |

---

## 6. Interview Strategy（面試實戰建議）

### Articulation Framework（口條框架）
1.  **Identify the fit:** "Since we need to search for prefixes/patterns dynamically, a Trie is a strong candidate over a Hash Map."
    **確認適用性：** 「由於我們需要動態搜尋前綴/模式，Trie 是比 Hash Map 更強的候選方案。」
2.  **Define the Node:** Clearly state what your `TrieNode` contains (`children`, `isEnd`, maybe `count`).
    **定義節點：** 清楚說明你的 `TrieNode` 包含什麼（`children`、`isEnd`，或許還有 `count`）。
3.  **Discuss Trade-offs:** proactively mention space complexity. "The trade-off here is memory usage, but it gives us $O(L)$ lookup time."
    **討論權衡：** 主動提及空間複雜度。「這裡的權衡是記憶體使用量，但它提供了 $O(L)$ 的查詢時間。」

### Whiteboard Strategy（白板策略）
*   **Draw the Tree:** Draw a small Trie with "cat", "car", "do". Visually show where the `isEnd` flag is.
    **畫出樹狀圖：** 畫一個包含 "cat"、"car"、"do" 的小 Trie。視覺化展示 `isEnd` 標記的位置。
*   **Modularize:** Write `insert` and `search` as separate helper methods inside the class, keeping the main logic clean.
    **模組化：** 將 `insert` 和 `search` 寫成類別內的獨立輔助方法，保持主邏輯整潔。

### Common Follow-ups（常見追問）
*   **Q:** How to optimize space if branches are long but have no branching? (e.g., "internet", "interview")
    **問：** 如果分支很長但沒有分岔（例如 "internet", "interview"），如何優化空間？
    *   **A:** **Radix Tree (Patricia Trie)**. Compress single-child paths into a single node (e.g., store "inter" in one node).
    *   **答：** **基數樹（Patricia Trie）**。將單子節點路徑壓縮為一個節點（例如，將 "inter" 存儲在一個節點中）。
*   **Q:** How to handle a huge dataset that doesn't fit in memory?
    **問：** 如何處理無法放入記憶體的巨大資料集？
    *   **A:** Database sharding based on prefixes, or disk-based B-Trees/LSM Trees (though these drift away from pure Tries).
    *   **答：** 基於前綴的資料庫分片，或基於磁碟的 B-Trees/LSM Trees（雖然這偏離了純 Tries）。

---

## 7. Practice Problems（練習題）

### 1. Easy/Intermediate: Implement Trie (Prefix Tree)
*   **Goal:** Build the standard class with `insert`, `search`, `startsWith`.
*   **Hint:** Use `Map<char, Node>` or `Object`. Don't forget the boolean flag.
*   **目標：** 建立包含 `insert`、`search`、`startsWith` 的標準類別。
*   **提示：** 使用 `Map<char, Node>` 或 `Object`。別忘了布林標記。

### 2. Intermediate: Design Search Autocomplete System (LeetCode 642)
*   **Goal:** Store "hot" sentences. Return top 3 historical sentences with the same prefix.
*   **Hint:** Store a list of "Top 3" results at **each node** to avoid traversing down to leaves every time. This trades space for time (Caching).
*   **目標：** 儲存「熱門」句子。回傳具有相同前綴的前 3 個歷史句子。
*   **提示：** 在 **每個節點** 儲存「前 3 名」結果列表，以避免每次都遍歷到葉節點。這是以空間換取時間（快取）。

### 3. Advanced: Maximum XOR of Two Numbers in an Array (LeetCode 421)
*   **Goal:** Find `max(nums[i] ^ nums[j])` in $O(N)$.
*   **Hint:** Build a **Binary Trie** (depth 31 or 32). For each number, try to traverse the path that represents the *opposite* bit (0->1, 1->0) to maximize the result.
*   **目標：** 在 $O(N)$ 內找到 `max(nums[i] ^ nums[j])`。
*   **提示：** 建立一個 **二元 Trie**（深度 31 或 32）。對於每個數字，嘗試遍歷代表 *相反* 位元（0->1, 1->0）的路徑以最大化結果。

---

## 8. Quick Checklists（快速檢核表）

### Debugging / Self-Review
*   [ ] Did I handle the empty string case? (Usually root node represents empty prefix).
    我是否處理了空字串的情況？（通常根節點代表空前綴）。
*   [ ] Did I mark `isEnd = true` at the end of insertion?
    我是否在插入結束時標記了 `isEnd = true`？
*   [ ] If using DFS/Backtracking, did I restore the state (backtrack) correctly?
    如果使用 DFS/回溯，我是否正確還原了狀態（回溯）？
*   [ ] Is my complexity strictly related to Key Length ($L$), not Total Keys ($N$)?
    我的複雜度是否嚴格與鍵長 ($L$) 相關，而非總鍵數 ($N$)？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The Dictionary (字典):**
    You don't scan every word in the dictionary to find "Apple". You flip to 'A', then 'p', then 'p'. The path you take *is* the word.
    你不會掃描字典裡的每個字來找 "Apple"。你會翻到 'A'，然後 'p'，再 'p'。你走過的路徑 *就是* 那個字。

*   **Folder Structure (資料夾結構):**
    `/home/user/docs` and `/home/user/downloads`.
    `/home/user` is the shared prefix node. You don't store "home" twice.
    `/home/user` 是共享的前綴節點。你不會儲存 "home" 兩次。

*   **Bitwise Trie as a Decision Tree (位元 Trie 作為決策樹):**
    Imagine a game where you want to go Left (0) or Right (1). To get the maximum difference (XOR), if the opponent goes Left, you *want* to go Right. The Trie tells you if a "Right" path exists.
    想像一個遊戲，你要往左 (0) 或往右 (1)。為了得到最大差異 (XOR)，如果對手往左，你會 *想要* 往右。Trie 會告訴你「往右」的路徑是否存在。