# Data Structure: Tries (Prefix Trees)
# Level: Intermediate (中階)

## 1. Learning Objectives (學習目標)

1.  **Master the internal structure**: Understand how to implement a Trie using nested Hash Maps (Dictionaries) versus Arrays, and the trade-offs involved.
    **掌握內部結構**：理解如何使用巢狀雜湊表（Dictionaries）與陣列（Arrays）來實作 Trie，以及其中的權衡取捨。
2.  **Optimize for Prefix Operations**: Learn why Tries outperform Hash Tables for prefix-based queries (autocomplete, spell check).
    **優化前綴操作**：學習為何 Trie 在基於前綴的查詢（如自動補全、拼字檢查）上優於雜湊表。
3.  **Combine with DFS/BFS**: Ability to use Tries as an optimization layer for graph traversal problems (e.g., Word Search on a grid).
    **結合 DFS/BFS**：具備將 Trie 作為圖遍歷問題（例如網格上的單字搜尋）優化層的能力。
4.  **Analyze Complexity correctly**: Recognize that complexity depends on the length of the word ($L$), not the number of words ($N$).
    **正確分析複雜度**：認清複雜度取決於單字長度（$L$），而非單字總數（$N$）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Trie is a tree-like data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie 是一種樹狀資料結構，用於在字串資料集中高效地儲存與檢索鍵值。

### Intuition (直覺)
Instead of storing the whole string in a node, we store characters along the path; common prefixes are shared, saving space for dense datasets.
我們不將整個字串儲存在節點中，而是沿著路徑儲存字元；共同的前綴會被共享，這對於密集的資料集能節省空間。

### Complexity (複雜度)
*   **Time (時間)**: $O(L)$ for insert, search, and prefix check, where $L$ is the string length.
    **時間**：插入、搜尋與前綴檢查皆為 $O(L)$，其中 $L$ 為字串長度。
*   **Space (空間)**: $O(N \times L \times \Sigma)$ in the worst case, where $\Sigma$ is the alphabet size (e.g., 26).
    **空間**：最差情況下為 $O(N \times L \times \Sigma)$，其中 $\Sigma$ 是字母集大小（例如 26）。

### Use Cases (適用場景)
*   **Autocomplete / Typeahead**: Suggesting words based on typed prefixes.
    **自動補全 / 預先輸入**：根據已輸入的前綴建議單字。
*   **Spell Checker**: Quickly verifying if a word exists.
    **拼字檢查**：快速驗證單字是否存在。
*   **IP Routing (Longest Prefix Match)**: Matching network packets to routes.
    **IP 路由（最長前綴匹配）**：將網路封包匹配至路由。

### Not Suitable (不適用場景)
*   **Random Access**: If you don't need prefix features, a Hash Map ($O(1)$) is generally faster and simpler.
    **隨機存取**：如果你不需要前綴功能，雜湊表（$O(1)$）通常更快且更簡單。
*   **Memory Constraints**: Tries can consume significant memory due to node overhead if the dataset is sparse.
    **記憶體限制**：如果資料集很稀疏，Trie 可能因節點開銷而消耗大量記憶體。

---

## 3. Typical Patterns (典型題型 / 模式)

1.  **Standard Trie (Insert/Search/StartsWith)**
    **標準 Trie（插入/搜尋/前綴檢查）**
    The foundation for all other patterns.
    所有其他模式的基礎。

2.  **Trie + DFS (Backtracking)**
    **Trie + DFS（回溯法）**
    Used for finding all words in a grid (Boggle game) or generating all words with a given prefix.
    用於在網格中尋找所有單字（Boggle 遊戲）或生成具有特定前綴的所有單字。

3.  **Bitwise Trie (XOR Trie)**
    **位元 Trie（XOR Trie）**
    Storing binary representations of numbers to solve "Maximum XOR" problems. (Advanced but common in Big Tech).
    儲存數字的二進位表示法以解決「最大 XOR」問題。（進階但在大型科技公司常見）。

4.  **Wildcard Matching**
    **萬用字元匹配**
    Searching with `.` representing any character, requiring branching DFS within the Trie.
    搜尋時使用 `.` 代表任意字元，需要在 Trie 內部進行分支 DFS。

---

## 4. Example Walkthrough (範例講解)

### Problem: Implement a Trie with Prefix Search
### 問題：實作具備前綴搜尋功能的 Trie

**Problem Statement:**
Implement a Trie class that supports `insert`, `search` (exact match), and `startsWith` (prefix match).
**問題重述：**
實作一個 Trie 類別，支援 `insert`（插入）、`search`（精確匹配）與 `startsWith`（前綴匹配）。

### Approach (思路)

1.  **Brute Force (List/Set)**:
    **暴力解（列表/集合）**：
    *   Using a `Set` gives $O(1)$ exact search, but `startsWith` requires iterating through all words ($O(N \times L)$). This is inefficient for autocomplete.
    *   使用 `Set` 可提供 $O(1)$ 的精確搜尋，但 `startsWith` 需要遍歷所有單字（$O(N \times L)$）。這對自動補全來說效率低落。

2.  **Optimal Solution (Trie)**:
    **最佳解（Trie）**：
    *   Create a `TrieNode` class containing a hash map for children and a boolean flag `is_end`.
    *   建立一個 `TrieNode` 類別，包含用於子節點的雜湊表以及一個布林標記 `is_end`。
    *   Traverse down the tree character by character.
    *   逐字元向下遍歷樹狀結構。

### Python Reference Solution (Python 參考解)

```python
class TrieNode:
    def __init__(self):
        # Using a dictionary for dynamic space allocation (vs fixed array size 26)
        # 使用字典進行動態空間分配（相較於固定大小為 26 的陣列）
        self.children = {} 
        # Mark if this node represents the end of a complete word
        # 標記此節點是否代表一個完整單字的結尾
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        # Initialize with a dummy root node
        # 初始化一個虛擬根節點
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Inserts a word into the trie.
        Time: O(L), Space: O(L)
        """
        node = self.root
        for char in word:
            # If char not present, create a new node
            # 若字元不存在，建立新節點
            if char not in node.children:
                node.children[char] = TrieNode()
            # Move to the child node
            # 移動至子節點
            node = node.children[char]
        
        # Mark the end of the word
        # 標記單字結束
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """
        Returns True if the word is in the trie.
        Time: O(L), Space: O(1)
        """
        node = self._find_node(word)
        # Must exist AND be marked as an end of a word
        # 節點必須存在 且 被標記為單字結尾
        return node is not None and node.is_end_of_word

    def startsWith(self, prefix: str) -> bool:
        """
        Returns True if there is any word in the trie that starts with the given prefix.
        Time: O(L), Space: O(1)
        """
        node = self._find_node(prefix)
        # As long as the node exists, the prefix exists
        # 只要節點存在，前綴即存在
        return node is not None

    def _find_node(self, prefix: str) -> TrieNode:
        """
        Helper function to traverse to the last node of a prefix.
        輔助函式：遍歷至前綴的最後一個節點。
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

### Common Mistakes (錯誤示範 & 為何錯)

*   **Mistake**: Forgetting `is_end_of_word`.
    **錯誤**：忘記 `is_end_of_word` 標記。
    *   *Why*: Without this, you cannot distinguish between "apple" (inserted) and "app" (prefix only).
    *   *原因*：沒有這個標記，你無法區分 "apple"（已插入）和 "app"（僅為前綴）。
*   **Mistake**: Using `[None] * 26` for every node when the character set is large (e.g., Unicode).
    **錯誤**：當字元集很大（如 Unicode）時，對每個節點使用 `[None] * 26`。
    *   *Why*: This wastes huge memory. Use `dict` (Hash Map) for flexibility unless strictly limited to 'a'-'z'.
    *   *原因*：這會浪費大量記憶體。除非嚴格限制在 'a'-'z'，否則應使用 `dict`（雜湊表）以保持彈性。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Trie (字首樹) | Hash Map (雜湊表) | Distinction (區別) |
| :--- | :--- | :--- | :--- |
| **Search Time** (搜尋時間) | $O(L)$ | $O(1)$ (Avg) | Hash Map is faster for exact match; Trie is consistent. <br> 雜湊表精確匹配較快；Trie 表現一致。 |
| **Prefix Search** (前綴搜尋) | $O(L)$ | $O(N \times L)$ | Trie is designed for this; Hash Map fails here. <br> Trie 專為此設計；雜湊表在此失效。 |
| **Space Efficiency** (空間效率) | High overhead for unique suffixes | Efficient | Trie saves space only if many words share prefixes. <br> 只有在許多單字共享前綴時，Trie 才能節省空間。 |
| **Collision** (碰撞) | Impossible | Possible | Tries have no collisions. <br> Trie 不會有碰撞問題。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints**: "Is the input limited to lowercase English letters? Or full ASCII/Unicode?" (Affects array vs. dict choice).
    **釐清限制**：「輸入僅限於小寫英文字母嗎？還是包含 ASCII/Unicode？」（影響陣列與字典的選擇）。
2.  **Define Node Structure**: "I will define a `TrieNode` class first to encapsulate the children and the end-of-word flag."
    **定義節點結構**：「我會先定義一個 `TrieNode` 類別，用來封裝子節點與單字結尾標記。」
3.  **Discuss Trade-offs**: "I'm using a HashMap for children nodes to handle potential sparse data efficiently, though an array might be slightly faster for dense 'a-z' data."
    **討論權衡**：「我使用 HashMap 來儲存子節點，以有效處理潛在的稀疏資料，雖然對於密集的 'a-z' 資料，陣列可能稍快一些。」

### Whiteboard Strategy (白板策略)
*   Draw the root as an empty circle.
    畫一個空圓圈作為根節點。
*   Draw edges labeled with characters, not nodes.
    在邊上標註字元，而非節點內。
*   Color or double-circle the nodes that have `is_end = True`.
    將 `is_end = True` 的節點塗色或畫雙圈。

### Common Follow-ups (常見追問)
*   **Delete a word**: "How would you implement delete?" (Need to prune nodes bottom-up only if they have no other children).
    **刪除單字**：「你會如何實作刪除？」（需要由下而上修剪節點，且僅在該節點無其他子節點時修剪）。
*   **Memory Optimization**: "How to reduce space?" (Mention **Radix Tree / Patricia Trie** which compresses single-child paths).
    **記憶體優化**：「如何減少空間？」（提及 **Radix Tree / Patricia Trie**，它會壓縮單一子節點的路徑）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Longest Common Prefix
**Brief**: Find the longest common prefix string amongst an array of strings.
**簡述**：在字串陣列中找出最長的共同前綴字串。
*   **Hint**: Insert all words into a Trie. Traverse from root until a node has >1 children or `is_end` is True.
*   **提示**：將所有單字插入 Trie。從根節點開始遍歷，直到某個節點擁有 >1 個子節點或 `is_end` 為真。

### 2. Medium: Design Add and Search Words Data Structure (LeetCode 211)
**Brief**: Support `.` as a wildcard character matching any letter.
**簡述**：支援 `.` 作為匹配任意字母的萬用字元。
*   **Hint**: When `.` is encountered, use DFS to check **all** children of the current node.
*   **提示**：遇到 `.` 時，使用 DFS 檢查當前節點的 **所有** 子節點。

### 3. Hard: Word Search II (LeetCode 212)
**Brief**: Find all words from a dictionary that exist in a 2D board of characters.
**簡述**：找出字典中所有存在於二維字元網格上的單字。
*   **Hint**: Build a Trie from the dictionary. DFS on the board. Prune the search immediately if the current path is not in the Trie. **Crucial Optimization**: Remove the word from Trie after finding it to avoid duplicates and speed up.
*   **提示**：根據字典建立 Trie。在網格上進行 DFS。若當前路徑不在 Trie 中，立即剪枝。**關鍵優化**：找到單字後將其從 Trie 中移除，以避免重複並加速。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Root Handling**: Did I initialize `root` correctly (usually empty)?
    **根節點處理**：我是否正確初始化 `root`（通常為空）？
*   [ ] **End Flag**: Did I set `is_end = True` after the loop in insert?
    **結束標記**：我是否在插入迴圈結束後設定 `is_end = True`？
*   [ ] **Return Logic**: In search, did I return `node.is_end`? In startsWith, did I return `True` just because node exists?
    **回傳邏輯**：在搜尋時，我是否回傳 `node.is_end`？在前綴檢查時，我是否僅因節點存在就回傳 `True`？
*   [ ] **Complexity**: Did I mention $O(L)$ instead of $O(N)$?
    **複雜度**：我是否提到 $O(L)$ 而非 $O(N)$？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

*   **Analogy**: **Predictive Text / Dictionary**.
    **類比**：**預測輸入 / 字典**。
    Think of a physical dictionary. To find "Apple", you find the section 'A', then 'p', then 'p'... You don't scan every word in the book.
    想像一本實體字典。要找 "Apple"，你會先找 'A' 區，接著 'p'，再 'p'... 你不會掃描書中的每一個字。

*   **Visual Anchor**: **Folder Structure**.
    **視覺錨點**：**資料夾結構**。
    `/home/user/docs` vs `/home/user/downloads`.
    `/home/user/` is the shared prefix node.
    `/home/user/` 是共享的前綴節點。