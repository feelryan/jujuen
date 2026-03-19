Here is the comprehensive guide on Tries, tailored for a Senior Software Engineer, following your specific constraints.

---

# Interview Masterclass: Tries (Prefix Trees)
# 面試大師班：字典樹 (前綴樹)

**Level:** Intermediate (中級)
**Language:** Java
**Target Audience:** Senior Software Engineer (7-12 YOE)

---

## 1. Learning Goals (學習目標)

*   **Master the internal structure of a Trie and its node composition.**
    掌握 Trie 的內部結構及其節點組成。
*   **Understand the trade-offs between Tries and HashMaps for string operations.**
    理解在字串操作中，Trie 與 HashMap 之間的權衡取捨。
*   **Implement core operations (Insert, Search, StartsWith) and recursive traversal patterns.**
    實作核心操作（插入、搜尋、前綴確認）以及遞迴遍歷模式。
*   **Analyze time and space complexity, specifically regarding alphabet size and word length.**
    分析時間與空間複雜度，特別是關於字母表大小與單字長度的關係。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Trie (pronounced "try") is a tree-based data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie（發音同 "try"）是一種基於樹的資料結構，用於高效地儲存和檢索字串資料集中的鍵。

### Intuition (直覺)
Instead of storing the whole string in a node, each edge represents a character, and nodes represent a state of the prefix.
與其在節點中儲存整個字串，不如讓每條邊代表一個字元，而節點代表前綴的狀態。
Common prefixes are shared, reducing redundant storage for similar words.
共同的前綴被共享，從而減少了相似單字的冗餘儲存。

### Complexity (複雜度)
*   **Time (時間):** $O(L)$ for insert/search, where $L$ is the length of the word.
    插入/搜尋為 $O(L)$，其中 $L$ 是單字長度。
    *Note: This is often faster than a HashMap in practice because HashMaps must compute the hash over $O(L)$ and handle collisions.*
    *註：實務上這通常比 HashMap 快，因為 HashMap 必須在 $O(L)$ 內計算雜湊值並處理碰撞。*
*   **Space (空間):** $O(N \times L \times \Sigma)$ in the worst case, where $\Sigma$ is the alphabet size.
    最差情況下為 $O(N \times L \times \Sigma)$，其中 $\Sigma$ 為字母表大小。

### When to Use (適用場景)
*   **Autocomplete / Typeahead:** Finding all words starting with "app...".
    自動完成 / 預先輸入：尋找所有以 "app..." 開頭的單字。
*   **Spell Checker:** Validating words and suggesting corrections.
    拼字檢查：驗證單字並建議更正。
*   **IP Routing (Longest Prefix Match):** Matching network packets to subnets.
    IP 路由（最長前綴匹配）：將網路封包匹配到子網域。

### When NOT to Use (不適用場景)
*   **Exact match only with random strings:** A HashMap is simpler and more space-efficient if prefix features aren't needed.
    僅需完全匹配且字串隨機：若不需要前綴功能，HashMap 更簡單且空間效率更高。
*   **Floating point numbers or non-discrete data:** Tries rely on discrete alphabets.
    浮點數或非離散資料：Trie 依賴於離散的字母表。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Standard Prefix Search (標準前綴搜尋)**
    *   Direct implementation of `insert`, `search`, and `startsWith`.
    *   直接實作 `insert`、`search` 和 `startsWith`。
2.  **Trie + DFS/Backtracking (Trie 結合深度優先搜尋/回溯)**
    *   Used for "Wildcard Matching" (e.g., `.`) or finding all words in a grid (Boggle game).
    *   用於「萬用字元匹配」（如 `.`）或在網格中尋找所有單字（Boggle 遊戲）。
3.  **Bitwise Trie (位元 Trie)**
    *   Storing binary representations of integers to solve XOR maximization problems.
    *   儲存整數的二進位表示法，以解決 XOR 最大化問題。

---

## 4. Example Walkthrough (範例講解)

### Problem: Design Add and Search Words Data Structure (LeetCode 211)
**問題：設計一個支援新增與搜尋單字的資料結構**

**Problem Statement (問題重述):**
Design a data structure that supports adding new words and finding if a string matches any previously added string.
設計一個資料結構，支援新增單字，並確認字串是否匹配任何先前新增的單字。
The search query may contain the dot character `'.'` to represent any one letter.
搜尋查詢可能包含點字元 `'.'`，代表任何一個字母。

### Approach (思路)

1.  **Brute Force (暴力法):**
    *   Store all words in a `List<String>`. For search, iterate through the list and use Regex or manual comparison.
    *   將所有單字存在 `List<String>` 中。搜尋時，遍歷列表並使用 Regex 或手動比對。
    *   *Drawback:* Search is $O(N \times L)$. Too slow for many queries.
    *   *缺點：* 搜尋時間為 $O(N \times L)$。對大量查詢來說太慢。

2.  **Optimization (優化 - Trie):**
    *   Use a Trie. Standard characters traverse specific children.
    *   使用 Trie。標準字元遍歷特定的子節點。
    *   When encountering `'.'`, we must check **all** non-null children of the current node (Backtracking/DFS).
    *   當遇到 `'.'` 時，我們必須檢查當前節點的 **所有** 非空子節點（回溯/DFS）。

3.  **Best Solution (最佳解):**
    *   Implement Trie with an Array `TrieNode[26]` for speed (assuming lowercase English).
    *   實作使用陣列 `TrieNode[26]` 的 Trie 以提升速度（假設為小寫英文字母）。
    *   Use a recursive helper function for the search to handle the wildcard logic.
    *   使用遞迴輔助函式來處理搜尋中的萬用字元邏輯。

### Java Reference Solution (Java 參考解)

```java
class WordDictionary {

    // Inner class for the Trie Node
    // Trie 節點的內部類別
    private class TrieNode {
        // Array for 26 lowercase English letters
        // 用於存放 26 個小寫英文字母的陣列
        TrieNode[] children;
        // Flag to mark the end of a word
        // 標記單字結束的旗標
        boolean isEnd;

        public TrieNode() {
            children = new TrieNode[26];
            isEnd = false;
        }
    }

    private TrieNode root;

    public WordDictionary() {
        root = new TrieNode();
    }

    // Adds a word into the data structure.
    // 將單字新增至資料結構中。
    // Time: O(L), Space: O(L)
    public void addWord(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            int index = c - 'a';
            if (node.children[index] == null) {
                node.children[index] = new TrieNode();
            }
            node = node.children[index];
        }
        node.isEnd = true;
    }

    // Returns true if the word is in the data structure.
    // 如果單字存在於資料結構中，則返回 true。
    // Supports '.' as a wildcard.
    // 支援 '.' 作為萬用字元。
    public boolean search(String word) {
        return searchHelper(word, 0, root);
    }

    // Helper function for DFS
    // 用於 DFS 的輔助函式
    // Time: O(26^L) in worst case (all dots), O(L) for exact match
    private boolean searchHelper(String word, int index, TrieNode node) {
        // Base case: if we have processed all characters
        // 基本情況：如果我們已經處理完所有字元
        if (index == word.length()) {
            return node.isEnd;
        }

        char c = word.charAt(index);

        if (c == '.') {
            // If wildcard, try all possible children
            // 如果是萬用字元，嘗試所有可能的子節點
            for (TrieNode child : node.children) {
                if (child != null) {
                    // If any path returns true, propagate it up
                    // 如果任何路徑返回 true，則向上傳遞
                    if (searchHelper(word, index + 1, child)) {
                        return true;
                    }
                }
            }
            return false;
        } else {
            // Standard character match
            // 標準字元匹配
            int charIndex = c - 'a';
            if (node.children[charIndex] == null) {
                return false;
            }
            return searchHelper(word, index + 1, node.children[charIndex]);
        }
    }
}
```

### Common Mistake (錯誤示範)

```java
// Wrong Approach: Iterating children incorrectly for '.'
// 錯誤方法：針對 '.' 錯誤地迭代子節點
if (c == '.') {
    for (int i = 0; i < 26; i++) {
        // MISTAKE: Changing 'node' reference inside the loop breaks backtracking
        // 錯誤：在迴圈內改變 'node' 參考會破壞回溯
        node = node.children[i]; 
        if (searchHelper(word, index + 1, node)) return true;
    }
}
```
**Why it's wrong:** You must pass the child to the recursive call, not modify the current `node` variable, which is needed for subsequent iterations.
**為何錯誤：** 你必須將子節點傳遞給遞迴呼叫，而不是修改當前的 `node` 變數，因為後續的迭代還需要用到它。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Trie (Prefix Tree) | HashMap (HashSet) |
| :--- | :--- | :--- |
| **Primary Use** (主要用途) | Prefix matching, Autocomplete (前綴匹配、自動完成) | Exact lookup (精確查找) |
| **Lookup Time** (查找時間) | $O(L)$ (Deterministic) | $O(L)$ (Avg), $O(L \times N)$ (Worst collisions) |
| **Space Efficiency** (空間效率) | Efficient for shared prefixes (對共享前綴高效) | High overhead per entry (每個條目開銷大) |
| **Implementation** (實作) | Complex (Nodes + Links) (複雜) | Simple (Built-in) (簡單) |

**Key Pitfall:** Using `Map<Character, TrieNode>` vs `TrieNode[26]`.
**關鍵陷阱：** 使用 `Map<Character, TrieNode>` 對比 `TrieNode[26]`。
*   **Array:** Faster access, less memory overhead *if* dense, but fixed alphabet size.
    **陣列：** 存取較快，若資料密集則記憶體開銷較小，但字母表大小固定。
*   **Map:** Flexible alphabet (Unicode), saves space for sparse nodes, but higher constant time overhead.
    **Map：** 字母表靈活（Unicode），稀疏節點節省空間，但常數時間開銷較高。

---

## 6. Interview Strategy (面試實戰建議)

### Clarification (釐清需求)
*   "What is the character set? Only lowercase 'a'-'z', or full Unicode?"
    「字元集是什麼？只有小寫 'a'-'z'，還是完整的 Unicode？」
    *(This decides Array vs. Map implementation).*
    *（這決定了使用陣列還是 Map 實作）。*

### Whiteboard Strategy (白板策略)
1.  **Define the Node Class first:** Don't start writing logic until you define `TrieNode`.
    **先定義 Node 類別：** 在定義 `TrieNode` 之前，不要開始寫邏輯。
2.  **Modularize:** Write `insert` first. It's the easiest and warms you up.
    **模組化：** 先寫 `insert`。這是最簡單的，可以讓你熱身。
3.  **Follow-up Prep:** Be ready to discuss how to delete a word (requires post-order traversal to prune empty nodes).
    **準備追問：** 準備好討論如何刪除單字（需要後序遍歷來修剪空節點）。

### Narrative (口條框架)
"I will use a Trie to optimize for prefix lookups. Each node will represent a character. I'll use a boolean flag `isEnd` to distinguish between a prefix and a complete word."
「我將使用 Trie 來優化前綴查找。每個節點代表一個字元。我會使用一個布林旗標 `isEnd` 來區分前綴和完整的單字。」

---

## 7. Exercises (練習題)

### 1. Easy: Longest Common Prefix (最長共同前綴)
*   **Hint:** Insert all words into a Trie. Traverse from root; stop when a node has more than 1 child or `isEnd` is true.
*   **提示：** 將所有單字插入 Trie。從根節點遍歷；當節點有超過 1 個子節點或 `isEnd` 為真時停止。

### 2. Medium: Implement Trie (Prefix Tree) (實作 Trie)
*   **Hint:** The standard implementation. Focus on clean code and handling `null` checks.
*   **提示：** 標準實作。專注於乾淨的程式碼和處理 `null` 檢查。

### 3. Hard: Word Search II (單字搜尋 II)
*   **Hint:** Given a board of characters and a list of words, find all words in the board. Build a Trie from the word list, then DFS on the board matching against the Trie.
*   **提示：** 給定一個字元棋盤和一個單字列表，找出棋盤上的所有單字。從單字列表建立 Trie，然後在棋盤上進行 DFS 並與 Trie 進行匹配。
*   *Optimization:* Remove the word from Trie after finding it to avoid duplicates.
*   *優化：* 找到單字後將其從 Trie 中移除以避免重複。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Root Initialization:** Did you initialize `root` in the constructor?
    **根節點初始化：** 你有在建構函式中初始化 `root` 嗎？
*   [ ] **End of Word:** Did you set `isEnd = true` at the end of insertion?
    **單字結束：** 你有在插入結束時設定 `isEnd = true` 嗎？
*   [ ] **Character Mapping:** Are you handling `c - 'a'` correctly? What if the input contains special characters?
    **字元映射：** 你是否正確處理了 `c - 'a'`？如果輸入包含特殊字元怎麼辦？
*   [ ] **Return Value:** Does `search` return `node.isEnd`, while `startsWith` returns `true` just by reaching the node?
    **回傳值：** `search` 是否回傳 `node.isEnd`，而 `startsWith` 只要到達節點就回傳 `true`？

---

## 9. Memory Anchors (記憶錨點)

### The "Folder Structure" Analogy (「資料夾結構」類比)
Imagine a file system.
想像一個檔案系統。
*   **Root:** The `C:/` drive.
    **根：** `C:/` 磁碟機。
*   **Edges:** Folder names (characters).
    **邊：** 資料夾名稱（字元）。
*   **Nodes:** The folders themselves.
    **節點：** 資料夾本身。
*   **isEnd:** A file inside the folder named "content.txt" indicating a valid word ends here.
    **isEnd：** 資料夾內一個名為 "content.txt" 的檔案，表示一個有效的單字在此結束。

To find "apple", you open folder `a` -> `p` -> `p` -> `l` -> `e`. If folder `e` exists and has the content file, the word exists.
要尋找 "apple"，你打開資料夾 `a` -> `p` -> `p` -> `l` -> `e`。如果資料夾 `e` 存在且包含內容檔案，則單字存在。