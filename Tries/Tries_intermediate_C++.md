Here is the complete interview preparation guide for **Tries (Prefix Trees)**, tailored for a Senior Software Engineer, focusing on the **Intermediate** level with **C++** implementation.

---

# Interview Masterclass: Tries (Prefix Trees)
# 面試大師班：Trie（前綴樹）

**Role:** Principal Software Engineer & Interviewer (Big Tech)
**Level:** Intermediate
**Language:** C++

---

## 1. Learning Goals（學習目標）

1.  **Understand the internal structure:** Master the node composition (children pointers + end-of-word flag) and memory management in C++.
    **理解內部結構：** 掌握節點組成（子節點指針 + 單詞結束標記）以及 C++ 中的記憶體管理。
2.  **Optimize for specific constraints:** Know when to use an Array (`Node*[26]`) versus a Hash Map (`unordered_map`) for children.
    **針對特定限制進行優化：** 知道何時該使用陣列（`Node*[26]`）與雜湊表（`unordered_map`）來儲存子節點。
3.  **Combine with DFS/Backtracking:** Learn to traverse the Trie for wildcard matching or autocomplete scenarios.
    **結合 DFS/回溯法：** 學習如何遍歷 Trie 以處理萬用字元匹配或自動補全場景。
4.  **Analyze Complexity accurately:** Articulate why Trie operations are $O(L)$ (length of word) and not dependent on the dataset size $N$.
    **精準分析複雜度：** 能夠清楚說明為何 Trie 操作是 $O(L)$（單詞長度），而與資料集大小 $N$ 無關。

---

## 2. Core Concepts（核心觀念速覽）

### Definition（定義）
A Trie (pronounced "try") is a tree-based data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie（發音同 "try"）是一種基於樹的資料結構，用於高效地儲存和檢索字串資料集中的鍵。

### Intuition（直覺）
Instead of storing whole strings in a list or hash map, we store characters as nodes.
我們不將完整字串儲存在列表或雜湊表中，而是將字元儲存為節點。

Common prefixes are shared among different keys, reducing redundant storage logically (though pointer overhead exists).
不同的鍵共享相同的前綴，這在邏輯上減少了冗餘儲存（儘管存在指針的額外開銷）。

### Complexity（複雜度）
-   **Time (Insert/Search/StartsWith):** $O(L)$, where $L$ is the length of the string.
    **時間（插入/搜尋/前綴檢查）：** $O(L)$，其中 $L$ 是字串長度。
-   **Space:** $O(A \cdot K \cdot N)$ in the worst case, where $A$ is alphabet size, $K$ is average length, $N$ is number of words.
    **空間：** 最壞情況下為 $O(A \cdot K \cdot N)$，其中 $A$ 是字母集大小，$K$ 是平均長度，$N$ 是單詞數量。

### When to Use / Not Use（適用與不適用場景）
-   **Use when:** You need prefix-based lookups (autocomplete), spell checking, or sorting strings bit-by-bit.
    **適用：** 當你需要基於前綴的查找（自動補全）、拼字檢查或逐位元排序字串時。
-   **Do NOT use when:** The character set is huge (e.g., full Unicode) and sparse, causing memory bloat; or when simple exact match ($O(1)$ Hash Map) suffices.
    **不適用：** 當字元集巨大（如完整 Unicode）且稀疏，導致記憶體膨脹時；或當簡單的精確匹配（$O(1)$ 雜湊表）就足夠時。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Standard Implementation:** `insert`, `search`, `startsWith`.
    **標準實作：** `insert`（插入）、`search`（搜尋）、`startsWith`（前綴確認）。
2.  **Wildcard Matching (DFS):** Searching with `.` representing any character.
    **萬用字元匹配（DFS）：** 搜尋時使用 `.` 代表任意字元。
3.  **Autocomplete / Recommendation:** Storing frequency or priority at nodes to return "Top K" suggestions.
    **自動補全 / 推薦：** 在節點儲存頻率或優先級，以返回「前 K 個」建議。
4.  **Word Search on Grid:** Combining Trie with backtracking on a 2D board (e.g., Boggle game).
    **網格單詞搜尋：** 將 Trie 與二維版面上的回溯法結合（例如 Boggle 遊戲）。

---

## 4. Example Walkthrough（範例講解）

### Problem: Design Add and Search Words Data Structure (LeetCode 211)
**問題：設計一個支援「添加」與「搜尋」單詞的資料結構**

**Problem Statement:**
Design a data structure that supports adding new words and finding if a string matches any previously added string. The search string may contain dots `.` where a dot can be matched with any letter.
設計一個資料結構，支援添加新單詞，並查找字串是否匹配任何先前添加的單詞。搜尋字串可能包含點 `.`，其中點可以匹配任何字母。

### Approach（思路）

1.  **Brute Force:** Store all words in a `vector<string>`. Search requires iterating through all words and checking character by character. Time: $O(N \cdot L)$. Too slow.
    **暴力解：** 將所有單詞存入 `vector<string>`。搜尋需要遍歷所有單詞並逐字元檢查。時間：$O(N \cdot L)$。太慢。

2.  **Optimization (Trie):** Since we need to handle prefixes and character-by-character matching, a Trie is natural.
    **優化（Trie）：** 由於我們需要處理前綴和逐字元匹配，Trie 是自然的選擇。
    -   **Insert:** Standard Trie insertion.
        **插入：** 標準 Trie 插入。
    -   **Search:** Standard traversal, but when we hit a `.`, we must branch out and check **all** valid children of the current node (Backtracking/DFS).
        **搜尋：** 標準遍歷，但當遇到 `.` 時，我們必須分支並檢查當前節點的**所有**有效子節點（回溯/DFS）。

### C++ Reference Solution（C++ 參考解）

```cpp
#include <vector>
#include <string>
#include <iostream>

using namespace std;

// Definition of the Trie Node
// Trie 節點的定義
struct TrieNode {
    // Array for 26 lowercase English letters
    // 用於儲存 26 個小寫英文字母的陣列
    TrieNode* children[26];
    bool isEnd;

    TrieNode() {
        isEnd = false;
        // Initialize pointers to nullptr
        // 將指針初始化為 nullptr
        for (int i = 0; i < 26; i++) {
            children[i] = nullptr;
        }
    }

    // Destructor to prevent memory leaks (Good for interviews)
    // 解構子以防止記憶體洩漏（面試加分項）
    ~TrieNode() {
        for (int i = 0; i < 26; i++) {
            if (children[i]) delete children[i];
        }
    }
};

class WordDictionary {
private:
    TrieNode* root;

public:
    WordDictionary() {
        root = new TrieNode();
    }
    
    // Destructor for the class
    // 類別的解構子
    ~WordDictionary() {
        delete root;
    }

    // Adds a word into the data structure.
    // 將單詞添加到資料結構中。
    // Time: O(L), Space: O(L)
    void addWord(string word) {
        TrieNode* node = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!node->children[idx]) {
                node->children[idx] = new TrieNode();
            }
            node = node->children[idx];
        }
        node->isEnd = true;
    }

    // Returns true if the word is in the data structure.
    // 如果單詞在資料結構中，則返回 true。
    // Supports '.' as a wildcard.
    // 支援 '.' 作為萬用字元。
    bool search(string word) {
        return searchHelper(word, 0, root);
    }

private:
    // Helper function for DFS
    // 用於 DFS 的輔助函式
    // Time: Worst case O(26^L) if all are dots, usually much faster.
    // 時間：最壞情況若全為點則為 O(26^L)，通常快得多。
    bool searchHelper(const string& word, int index, TrieNode* node) {
        // Base case: reached end of the search string
        // 基本情況：到達搜尋字串的末尾
        if (index == word.length()) {
            return node->isEnd;
        }

        char c = word[index];

        if (c == '.') {
            // If dot, try all possible children
            // 如果是點，嘗試所有可能的子節點
            for (int i = 0; i < 26; i++) {
                if (node->children[i] && searchHelper(word, index + 1, node->children[i])) {
                    return true;
                }
            }
            return false;
        } else {
            // Standard match
            // 標準匹配
            int idx = c - 'a';
            if (!node->children[idx]) return false;
            return searchHelper(word, index + 1, node->children[idx]);
        }
    }
};
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Confusion (錯誤/混淆) | Correction (修正) |
| :--- | :--- | :--- |
| **Node Deletion** | Forgetting to delete nodes in C++, causing memory leaks. <br> 在 C++ 中忘記刪除節點，導致記憶體洩漏。 | Implement a destructor or use `unique_ptr` (though raw pointers are often preferred in interviews for simplicity). <br> 實作解構子或使用 `unique_ptr`（儘管面試中為求簡潔常偏好原始指針）。 |
| **isEnd Flag** | Assuming a node existing means the word exists. <br> 假設節點存在就代表單詞存在。 | Always check `node->isEnd` to confirm it's a valid word, not just a prefix. <br> 務必檢查 `node->isEnd` 以確認這是有效單詞，而不僅僅是前綴。 |
| **Array vs Map** | Using `map` for fixed alphabets (a-z). <br> 對於固定字母集（a-z）使用 `map`。 | Use `vector` or array `Node*[26]` for $O(1)$ access and better cache locality. Use `map` only for sparse/large char sets. <br> 使用 `vector` 或陣列 `Node*[26]` 以獲得 $O(1)$ 存取和更好的快取局部性。僅在稀疏/大字元集時使用 `map`。 |
| **Root Handling** | Storing a character in the root node. <br> 在根節點中儲存字元。 | The root should be empty; characters are defined by the edges (indices) leading to nodes. <br> 根節點應為空；字元是由通往節點的邊（索引）定義的。 |

---

## 6. Interview Strategy（面試實戰建議）

### Clarification Phase（釐清階段）
-   **Ask:** "What is the character set? Only lowercase 'a'-'z'?"
    **提問：** 「字元集是什麼？只有小寫 'a'-'z' 嗎？」
    *Why:* Determines array size (26) vs Hash Map.
    *原因：* 決定陣列大小（26）還是使用雜湊表。
-   **Ask:** "Do we need to support deletion?"
    **提問：** 「我們需要支援刪除功能嗎？」
    *Why:* Deletion logic is tricky (requires pruning empty branches).
    *原因：* 刪除邏輯較複雜（需要修剪空分支）。

### Whiteboard Strategy（白板策略）
1.  **Draw the Node Struct first:** This shows you understand the building blocks.
    **先畫出節點結構：** 這顯示你理解基本構成。
2.  **Visualize the Path:** Draw `root -> 'c' -> 'a' -> 't' (isEnd)`.
    **視覺化路徑：** 畫出 `root -> 'c' -> 'a' -> 't' (isEnd)`。
3.  **Modularize:** Write `search` and `insert` as separate methods. If implementing wildcard, separate the DFS helper.
    **模組化：** 將 `search` 和 `insert` 寫成獨立方法。如果實作萬用字元，將 DFS 輔助函式分開。

### Common Follow-ups（常見追問）
-   **Q:** How to optimize space if words are very sparse?
    **問：** 如果單詞非常稀疏，如何優化空間？
    **A:** Use a Compressed Trie (Radix Tree) or ternary search tree.
    **答：** 使用壓縮 Trie（Radix Tree）或三元搜尋樹。
-   **Q:** How to handle Unicode?
    **問：** 如何處理 Unicode？
    **A:** Use `unordered_map<char, TrieNode*>` instead of an array.
    **答：** 使用 `unordered_map<char, TrieNode*>` 代替陣列。

---

## 7. Practice Problems（練習題）

### 1. Easy: Implement Trie (Prefix Tree)
-   **Task:** Basic Insert, Search, StartsWith.
-   **Hint:** Focus on clean class design.
-   **LeetCode:** 208

### 2. Intermediate: Design Add and Search Words Data Structure
-   **Task:** Handle `.` wildcard.
-   **Hint:** Use DFS/Recursion when `.` is encountered.
-   **LeetCode:** 211 (Covered in example)

### 3. Intermediate/Hard: Word Search II
-   **Task:** Find all words from a dictionary in a 2D board.
-   **Hint:** Build a Trie from the dictionary first. Then DFS on the board, checking against the Trie to prune invalid paths early.
-   **LeetCode:** 212

---

## 8. Quick Checklists（快速檢核表）

**Self-Review during Interview:**
-   [ ] **Base Case:** Did I handle the empty string (if applicable)?
    **基本情況：** 我是否處理了空字串（若適用）？
-   [ ] **Null Checks:** Did I check if `node->children[i]` is null before traversing?
    **空值檢查：** 遍歷前我是否檢查了 `node->children[i]` 是否為空？
-   [ ] **Memory:** Did I allocate new nodes on the heap? (In C++, stack nodes will vanish).
    **記憶體：** 我是否在堆積（heap）上分配新節點？（在 C++ 中，堆疊節點會消失）。
-   [ ] **Return Value:** For `search`, did I return `node->isEnd`? For `startsWith`, did I just return `true`?
    **返回值：** 對於 `search`，我是否返回了 `node->isEnd`？對於 `startsWith`，我是否直接返回 `true`？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Dictionary Analogy（字典類比）
Imagine a physical dictionary. You don't scan every word to find "Apple".
想像一本實體字典。你不會掃描每一個字來找 "Apple"。
-   You open the tab **'A'** (Root's child).
    你打開標籤 **'A'**（根節點的子節點）。
-   Then you look for the section **'P'** within 'A'.
    然後你在 'A' 裡面找 **'P'** 區塊。
-   This is exactly how a Trie pointer traversal works.
    這正是 Trie 指針遍歷的運作方式。

### The File System Analogy（檔案系統類比）
-   `/home/user/docs`
-   `/home/user/music`
-   **Root** is `/`. **Nodes** are folders.
    **根**是 `/`。**節點**是資料夾。
-   "home" and "user" are shared prefixes. You don't create separate hard drives for every path.
    "home" 和 "user" 是共享前綴。你不會為每個路徑建立獨立的硬碟。