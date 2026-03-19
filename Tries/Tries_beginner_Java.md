Here is a comprehensive guide on **Tries (Prefix Trees)**, tailored for a Senior Software Engineer, focusing on the **Beginner** level (foundational structure and basic operations) with **Java** implementation.

這是一份針對 **Trie（字首樹/字典樹）** 的完整教材，專為資深軟體工程師量身打造，聚焦於 **初階（Beginner）** 程度（基礎結構與基本操作），並使用 **Java** 實作。

---

# Module: Tries (Prefix Trees) - Beginner Level

## 1. Learning Goals（學習目標）

*   **Understand the structural difference between Tries and HashMaps.**
    理解 Trie 與 HashMap 在結構上的差異。
*   **Master the implementation of a standard TrieNode and basic operations (Insert, Search, StartsWith).**
    掌握標準 TrieNode 的實作以及基本操作（插入、搜尋、前綴確認）。
*   **Analyze Time and Space Complexity specifically regarding word length ($L$) vs. number of keys ($N$).**
    針對單字長度（$L$）與鍵值數量（$N$）來分析時間與空間複雜度。
*   **Identify scenarios where Tries are the optimal choice (Autocomplete, Spell Checkers).**
    識別 Trie 為最佳解的場景（如自動補全、拼字檢查）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
A Trie (pronounced "try") is a tree-based data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie（讀音同 "try"）是一種基於樹狀的資料結構，用於在字串資料集中高效地儲存與檢索鍵值。

Unlike a binary search tree, nodes in a Trie do not store their associated key.
與二元搜尋樹不同，Trie 中的節點並不直接儲存其對應的鍵值。

Instead, a node's position in the tree defines the key with which it is associated.
取而代之的是，節點在樹中的位置定義了與其關聯的鍵值。

### Intuition（直覺）
Think of a Trie as a **dictionary** or a **file system path**.
將 Trie 想像成一本**字典**或**檔案系統路徑**。

To find "Code", you go to section 'C', then subsection 'o', then 'd', then 'e'.
要尋找 "Code"，你會先去 'C' 區，接著是 'o' 子區，然後是 'd'，最後是 'e'。

Common prefixes are stored only once, saving space for datasets with many shared prefixes.
共同的前綴只會被儲存一次，這對於擁有許多共用前綴的資料集來說能節省空間。

### Complexity（複雜度）
*   **Time Complexity (Insert/Search):** $O(L)$, where $L$ is the length of the string.
    **時間複雜度（插入/搜尋）：** $O(L)$，其中 $L$ 為字串長度。
*   **Space Complexity:** $O(N \times L \times \Sigma)$ in the worst case, where $\Sigma$ is the alphabet size (e.g., 26).
    **空間複雜度：** 最差情況下為 $O(N \times L \times \Sigma)$，其中 $\Sigma$ 是字母集大小（例如 26）。

### When to Use / Not to Use（適用與不適用場景）
*   **Use when:** You need prefix-based lookups (autocomplete), or need to sort strings lexicographically.
    **適用於：** 你需要基於前綴的查詢（自動補全），或需要按字典序排列字串時。
*   **Don't use when:** The dataset is sparse with very few common prefixes (HashMap is more space-efficient), or keys are not strings/sequences.
    **不適用於：** 資料集稀疏且極少共用前綴（此時 HashMap 較省空間），或鍵值並非字串/序列時。

---

## 3. Typical Patterns（典型題型 / 模式）

At the beginner level, most Trie problems revolve around these patterns:
在初階階段，大多數 Trie 問題圍繞著以下模式：

1.  **Standard Implementation:** Build the data structure from scratch.
    **標準實作：** 從頭建構此資料結構。
2.  **Prefix Counting:** Store a counter in each node to know how many words share a prefix.
    **前綴計數：** 在每個節點儲存計數器，以得知有多少單字共用該前綴。
3.  **Boolean Existence:** Checking if a specific word or prefix exists.
    **布林存在性檢查：** 檢查特定單字或前綴是否存在。

---

## 4. Example Walkthrough（範例講解）

### Problem: Implement Trie (Prefix Tree)
**LeetCode 208**

### Problem Restatement（問題重述）
Implement a Trie class that supports `insert`, `search`, and `startsWith` methods.
實作一個 Trie 類別，支援 `insert`（插入）、`search`（搜尋）與 `startsWith`（前綴確認）方法。

### Thought Process（思路）

1.  **Brute Force (List/Set):**
    **暴力解（列表/集合）：**
    Using a `HashSet<String>` gives $O(L)$ for `search` and `insert` (due to hashing), but `startsWith` becomes $O(N \times L)$ because we must iterate all strings.
    使用 `HashSet<String>` 雖然在 `search` 和 `insert` 上能達到 $O(L)$（因為雜湊計算），但 `startsWith` 會變成 $O(N \times L)$，因為必須遍歷所有字串。

2.  **Optimization (Trie):**
    **優化（Trie）：**
    By using a tree structure where each edge represents a character, `startsWith` also becomes $O(L)$.
    透過使用樹狀結構，其中每個邊代表一個字元，`startsWith` 的複雜度也能降至 $O(L)$。

3.  **Data Structure Design:**
    **資料結構設計：**
    We need a `TrieNode`. Since the problem usually implies lowercase English letters, an array `TrieNode[26]` is efficient.
    我們需要一個 `TrieNode`。由於題目通常暗示小寫英文字母，使用陣列 `TrieNode[26]` 是高效的。
    We also need a boolean flag `isEndOfWord` to distinguish between "apple" (word) and "app" (prefix).
    我們還需要一個布林標記 `isEndOfWord` 來區分 "apple"（單字）與 "app"（前綴）。

### Java Reference Solution（Java 參考解）

```java
class Trie {

    // Inner class for the node structure
    // 用於節點結構的內部類別
    private class TrieNode {
        // Array to store children nodes, assuming 'a'-'z'
        // 儲存子節點的陣列，假設範圍為 'a'-'z'
        private TrieNode[] children;
        
        // Flag to mark the end of a valid word
        // 標記有效單字結束的旗標
        private boolean isEndOfWord;

        public TrieNode() {
            this.children = new TrieNode[26];
            this.isEndOfWord = false;
        }
    }

    private TrieNode root;

    public Trie() {
        root = new TrieNode();
    }

    // Inserts a word into the trie.
    // Time: O(L), Space: O(L)
    // 將單字插入 Trie 中。時間：O(L)，空間：O(L)
    public void insert(String word) {
        TrieNode current = root;
        for (char c : word.toCharArray()) {
            int index = c - 'a';
            // If the path doesn't exist, create it
            // 如果路徑不存在，則建立它
            if (current.children[index] == null) {
                current.children[index] = new TrieNode();
            }
            // Move to the next node
            // 移動到下一個節點
            current = current.children[index];
        }
        // Mark the end of the word
        // 標記單字的結尾
        current.isEndOfWord = true;
    }

    // Returns true if the word is in the trie.
    // Time: O(L), Space: O(1)
    // 如果單字在 Trie 中則回傳 true。時間：O(L)，空間：O(1)
    public boolean search(String word) {
        TrieNode node = getNode(word);
        // It must exist AND be marked as an end of a word
        // 節點必須存在，且必須被標記為單字結尾
        return node != null && node.isEndOfWord;
    }

    // Returns true if there is any word in the trie that starts with the given prefix.
    // Time: O(L), Space: O(1)
    // 如果 Trie 中有任何單字以給定前綴開頭，則回傳 true。時間：O(L)，空間：O(1)
    public boolean startsWith(String prefix) {
        TrieNode node = getNode(prefix);
        // As long as the node exists, the prefix exists
        // 只要節點存在，前綴即存在
        return node != null;
    }

    // Helper function to traverse the trie
    // 輔助函式：遍歷 Trie
    private TrieNode getNode(String str) {
        TrieNode current = root;
        for (char c : str.toCharArray()) {
            int index = c - 'a';
            if (current.children[index] == null) {
                return null; // Path broken
            }
            current = current.children[index];
        }
        return current;
    }
}
```

### Error Demonstration & Why（錯誤示範 & 為何錯）

**Wrong Logic:**
```java
public boolean search(String word) {
    TrieNode node = getNode(word);
    return node != null; // WRONG!
}
```
**Why it's wrong:**
If you insert "apple", searching for "app" should return `false` because "app" was never inserted as a standalone word.
**為何錯誤：**
如果你插入 "apple"，搜尋 "app" 應該回傳 `false`，因為 "app" 從未作為獨立單字被插入過。
Without checking `isEndOfWord`, you cannot distinguish a prefix from a complete word.
若不檢查 `isEndOfWord`，你無法區分前綴與完整單字。

---

## 5. Common Pitfalls & Confusing Concepts（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall |
| :--- | :--- |
| **Prefix vs. Word** | **Pitfall:** Returning `true` just because traversal finished. <br> **Fix:** Always check `isEndOfWord` for exact matches. <br> **陷阱：** 僅因遍歷完成就回傳 `true`。<br> **修正：** 精確匹配時務必檢查 `isEndOfWord`。 |
| **Array vs. HashMap** | **Pitfall:** Using `HashMap` for children is flexible but slower and uses more memory for dense data. <br> **Fix:** Use `TrieNode[26]` for fixed alphabets (a-z). Use Map for Unicode. <br> **陷阱：** 使用 `HashMap` 儲存子節點雖然靈活，但在密集資料下較慢且耗記憶體。<br> **修正：** 固定字母集（a-z）使用 `TrieNode[26]`。Unicode 才用 Map。 |
| **Root Handling** | **Pitfall:** Storing a character in the root node. <br> **Fix:** The root should be empty; edges leaving the root represent the first characters. <br> **陷阱：** 在根節點儲存字元。<br> **修正：** 根節點應為空；從根節點出發的邊才代表第一個字元。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）
1.  **Clarify Charset:** "Is the input limited to lowercase English letters 'a'-'z', or should I handle full Unicode?"
    **釐清字元集：** 「輸入是否僅限於小寫英文字母 'a'-'z'，還是我需要處理完整的 Unicode？」
2.  **Define Node:** "I will define a `TrieNode` class. Since we are dealing with 'a'-'z', I'll use a fixed-size array for children to optimize access speed."
    **定義節點：** 「我會定義一個 `TrieNode` 類別。既然處理的是 'a'-'z'，我將使用固定大小的陣列來儲存子節點以優化存取速度。」
3.  **Modularize:** "I'll create a helper method `getNode` since both `search` and `startsWith` share the same traversal logic."
    **模組化：** 「我會建立一個輔助方法 `getNode`，因為 `search` 和 `startsWith` 共享相同的遍歷邏輯。」

### Whiteboard Strategy（白板策略）
*   Draw the root as an empty circle.
    將根節點畫成一個空圓圈。
*   Draw edges labeled with characters, not nodes.
    在邊上標註字元，而非節點內。
*   Mark "End of Word" nodes distinctly (e.g., double circle or filled circle).
    清楚標記「單字結尾」的節點（例如雙圈或實心圓）。

### Common Follow-ups（常見追問）
*   **Q:** How to delete a word?
    **問：** 如何刪除一個單字？
    **A:** Recursively traverse. If a node is no longer an end of a word and has no children, prune it to save space.
    **答：** 遞迴遍歷。如果一個節點不再是單字結尾且沒有子節點，則修剪它以節省空間。
*   **Q:** How to optimize space if strings are very long but sparse?
    **問：** 如果字串很長但很稀疏，如何優化空間？
    **A:** Mention **Radix Tree (Compressed Trie)**, where nodes can store strings instead of single characters.
    **答：** 提及 **Radix Tree（壓縮 Trie）**，其中節點可以儲存字串而非單一字元。

---

## 7. Practice Problems（練習題）

### 1. Implement Trie (Prefix Tree) [Easy]
*   **Link:** LeetCode 208
*   **Hint:** The standard implementation covered in the example. Focus on clean code structure.
    **提示：** 範例中涵蓋的標準實作。專注於乾淨的程式碼結構。

### 2. Longest Word in Dictionary [Medium]
*   **Link:** LeetCode 720
*   **Problem:** Find the longest word where every prefix is also a word in the dictionary.
    **問題：** 找出最長的單字，該單字的每個前綴也都必須是字典中的單字。
*   **Hint:** Build the Trie. Perform DFS. Only traverse to a child if `child.isEndOfWord` is true.
    **提示：** 建立 Trie。執行 DFS。只有當 `child.isEndOfWord` 為真時，才遍歷到該子節點。

### 3. Design Add and Search Words Data Structure [Medium]
*   **Link:** LeetCode 211
*   **Problem:** Support searching with `.` as a wildcard (matches any character).
    **問題：** 支援包含 `.` 作為萬用字元（匹配任何字元）的搜尋。
*   **Hint:** When hitting a `.`, you must iterate through **all** non-null children of the current node and recursively search.
    **提示：** 當遇到 `.` 時，必須遍歷當前節點的**所有**非空子節點並進行遞迴搜尋。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Root Initialization:** Did I initialize `root` in the constructor?
    **根節點初始化：** 我是否在建構子中初始化了 `root`？
*   [ ] **Index Calculation:** Am I handling `c - 'a'` correctly? (Watch out for non-lowercase inputs).
    **索引計算：** 我處理 `c - 'a'` 是否正確？（注意非小寫輸入）。
*   [ ] **Null Checks:** Did I check `if (current.children[index] == null)` before accessing?
    **空值檢查：** 存取前我是否檢查了 `if (current.children[index] == null)`？
*   [ ] **End Flag:** Did I set `isEndOfWord = true` at the end of insertion?
    **結束標記：** 我是否在插入結束時設定了 `isEndOfWord = true`？
*   [ ] **Search Logic:** Did I return `node.isEndOfWord` for search, but just `true` (if node exists) for startsWith?
    **搜尋邏輯：** 對於 search 我是否回傳 `node.isEndOfWord`，但對於 startsWith 僅回傳 `true`（若節點存在）？

---

## 9. Mnemonics & Analogies（記憶錨點與類比）

### The Folder Analogy（資料夾類比）
*   **Root:** The `C:/` drive.
    **根：** `C:/` 磁碟機。
*   **Edges:** Folder names (or characters in Trie).
    **邊：** 資料夾名稱（或 Trie 中的字元）。
*   **Nodes:** The folders themselves.
    **節點：** 資料夾本身。
*   **isEndOfWord:** A file inside the folder named "content.txt".
    **isEndOfWord：** 資料夾內一個名為 "content.txt" 的檔案。
*   *Path:* `/u/s/r` exists (prefix), but `/u/s/r` might not contain the target file (not a word).
    *路徑：* `/u/s/r` 存在（前綴），但 `/u/s/r` 可能不包含目標檔案（非單字）。

### Visual Anchor（圖像錨點）
Imagine a **Scrabble board** where words branch off each other. The word "ANT" and "ANY" share the path A -> N, then split at T and Y.
想像一個 **拼字遊戲盤**，單字彼此分支。單字 "ANT" 和 "ANY" 共用路徑 A -> N，然後在 T 和 Y 處分開。