# Data Structure: Tries (Prefix Trees)
# 資料結構：Tries（前綴樹）

## 1. Learning Goals (學習目標)

1.  **Understand the internal structure of a Trie Node.**
    理解 Trie 節點的內部結構（特別是 `children` 映射與 `is_end` 標記）。
2.  **Master the three fundamental operations: Insert, Search, and StartsWith.**
    掌握三個基本操作：插入、搜尋與前綴檢查。
3.  **Analyze the Time and Space Complexity trade-offs compared to Hash Tables.**
    分析與雜湊表（Hash Tables）相比的時間與空間複雜度權衡。
4.  **Implement a production-ready Trie class in Python.**
    用 Python 實作一個具備生產力水準的 Trie 類別。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Definition (定義)
A Trie (pronounced "try") is a tree-based data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie（發音同 "try"）是一種樹狀資料結構，用於高效地儲存與檢索字串資料集中的鍵值。

### Intuition (直覺)
Imagine a dictionary where instead of storing full words, you store characters in a chain; common prefixes share the same path.
想像一本字典，我們不儲存完整的單字，而是將字元串接起來儲存；相同的字首會共用同一條路徑。

### Complexity (複雜度)
*   **Time Complexity (時間複雜度):** $O(L)$ for insert, search, and prefix lookup, where $L$ is the length of the word.
    插入、搜尋與前綴查找皆為 $O(L)$，其中 $L$ 為單字長度。
*   **Space Complexity (空間複雜度):** $O(N \times L \times \Sigma)$, where $N$ is the number of words, $L$ is the average length, and $\Sigma$ is the alphabet size (e.g., 26).
    $O(N \times L \times \Sigma)$，其中 $N$ 是單字數量，$L$ 是平均長度，$\Sigma$ 是字母表大小（例如 26）。

### When to Use (適用場景)
*   **Autocomplete / Typehead:** Finding all words starting with "app".
    自動補全 / 輸入預測：找出所有以 "app" 開頭的單字。
*   **Spell Checker:** Verifying if a word exists in a dictionary.
    拼字檢查：驗證單字是否存在於字典中。
*   **IP Routing (Longest Prefix Match):** Matching network packets to routes.
    IP 路由（最長前綴匹配）：將網路封包匹配到路由路徑。

### When NOT to Use (不適用場景)
*   **General Key-Value Store:** If keys are not strings or share very few prefixes, Hash Tables ($O(1)$) are generally faster and more memory-efficient.
    一般鍵值儲存：如果鍵值不是字串或共用前綴很少，雜湊表（$O(1)$）通常更快且更節省記憶體。

---

## 3. Typical Patterns (典型題型 / 模式)

For a beginner level, we focus on the **Standard Trie Implementation** pattern.
針對初學者程度，我們專注於 **標準 Trie 實作** 模式。

1.  **The Node Structure (節點結構):**
    Each node contains a Hash Map (or Array) pointing to children and a Boolean flag indicating if a word ends there.
    每個節點包含一個指向子節點的雜湊表（或陣列），以及一個布林標記，指示單字是否在此結束。

2.  **Path Traversal (路徑遍歷):**
    Iterate through the characters of the input string, moving down the tree node by node.
    遍歷輸入字串的字元，沿著樹狀結構逐層向下移動。

---

## 4. Example Walkthrough (範例講解)

### Problem: Implement Trie (Prefix Tree)
### 問題：實作 Trie（前綴樹）

**Problem Statement (問題重述):**
Implement a `Trie` class with `insert(word)`, `search(word)`, and `startsWith(prefix)` methods.
實作一個 `Trie` 類別，包含 `insert(word)`、`search(word)` 與 `startsWith(prefix)` 方法。

### Approach (思路)

1.  **Brute Force (暴力法):**
    Use a simple list or set to store words.
    使用簡單的列表或集合來儲存單字。
    *   *Search:* $O(1)$ with Set, but `startsWith` becomes $O(N \times L)$ as we must scan all words.
    *   *搜尋：* 使用 Set 為 $O(1)$，但 `startsWith` 會變成 $O(N \times L)$，因為必須掃描所有單字。

2.  **Optimal Solution (最佳解 - Trie):**
    Build a tree where the root represents an empty string, and edges represent characters.
    建立一棵樹，根節點代表空字串，邊代表字元。
    *   `insert`: Create nodes if they don't exist.
    *   `insert`：如果節點不存在則建立。
    *   `search`: Traverse. If we hit a dead end or `is_end` is False, return False.
    *   `search`：遍歷。如果遇到死路或 `is_end` 為 False，則回傳 False。
    *   `startsWith`: Traverse. If we can process the whole prefix without hitting a dead end, return True.
    *   `startsWith`：遍歷。如果能處理完整個前綴且未遇死路，則回傳 True。

### Python Reference Solution (Python 參考解)

```python
class TrieNode:
    def __init__(self):
        # Using a dictionary for children allows flexibility for any unicode character.
        # 使用字典儲存子節點，允許對任何 Unicode 字元保持彈性。
        # Alternatively, use [None] * 26 for strictly lowercase English letters.
        # 或者，針對嚴格的小寫英文字母，可以使用 [None] * 26。
        self.children = {} 
        
        # Flag to mark the end of a valid word.
        # 用於標記有效單字結束的旗標。
        self.is_end_of_word = False

class Trie:

    def __init__(self):
        # Initialize the root node.
        # 初始化根節點。
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Inserts a word into the trie.
        將單字插入 Trie 中。
        Time: O(L), Space: O(L)
        """
        node = self.root
        for char in word:
            # If the character is not in children, create a new node.
            # 如果字元不在子節點中，建立一個新節點。
            if char not in node.children:
                node.children[char] = TrieNode()
            # Move to the child node.
            # 移動到子節點。
            node = node.children[char]
        
        # Mark the end of the word.
        # 標記單字的結尾。
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """
        Returns True if the word is in the trie.
        如果單字在 Trie 中，回傳 True。
        Time: O(L), Space: O(1)
        """
        node = self.root
        for char in word:
            if char not in node.children:
                # Character path does not exist.
                # 字元路徑不存在。
                return False
            node = node.children[char]
        
        # Check if the last node is actually marked as the end of a word.
        # 檢查最後一個節點是否確實被標記為單字的結尾。
        return node.is_end_of_word

    def startsWith(self, prefix: str) -> bool:
        """
        Returns True if there is any word in the trie that starts with the given prefix.
        如果 Trie 中有任何單字以給定前綴開頭，回傳 True。
        Time: O(L), Space: O(1)
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        
        # If we successfully traversed the prefix, it exists.
        # 如果我們成功遍歷了前綴，則表示它存在。
        return True
```

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱 / 混淆) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Search vs. StartsWith** | Returning `True` in `search` just because the path exists. <br> 僅因路徑存在就在 `search` 中回傳 `True`。 | `search` requires `node.is_end == True`. `startsWith` only requires the path to exist. <br> `search` 需要 `node.is_end == True`。`startsWith` 只需要路徑存在。 |
| **Node Storage** | Thinking the character is stored *inside* the node. <br> 誤以為字元儲存於節點 *內部*。 | The character is technically the "key" to the edge/link. The node represents the state *after* consuming that char. <br> 字元技術上是邊/連結的「鍵」。節點代表消耗該字元 *之後* 的狀態。 |
| **Space Complexity** | Underestimating memory usage. <br> 低估記憶體使用量。 | Tries can be memory-heavy compared to a Set if words don't share prefixes. <br> 如果單字不共用前綴，Trie 的記憶體消耗可能比 Set 大得多。 |

---

## 6. Interview Strategy (面試實戰建議)

### Articulation Framework (口條框架)
1.  **Define the Node:** "I will define a `TrieNode` class containing a hash map for children and a boolean flag."
    **定義節點：**「我將定義一個 `TrieNode` 類別，包含用於子節點的雜湊表和一個布林旗標。」
2.  **Explain the Root:** "The Trie is initialized with a dummy root node."
    **解釋根節點：**「Trie 使用一個虛擬根節點進行初始化。」
3.  **Walkthrough Logic:** "For insertion, I'll traverse down, creating nodes as needed. For search, I'll return `False` if a link is missing."
    **解釋邏輯：**「對於插入，我會向下遍歷，按需建立節點。對於搜尋，如果缺少連結，我會回傳 `False`。」

### Whiteboard Strategy (白板策略)
*   Draw a small tree for the words "cat", "car", "dog".
    畫一棵包含 "cat"、"car"、"dog" 的小樹。
*   Visually mark the "end of word" nodes (e.g., with a star or double circle).
    視覺化標記「單字結尾」的節點（例如用星星或雙圈）。

### Common Follow-ups (常見追問)
*   **Q:** How to optimize space if we only use a-z?
    **問：** 如果只使用 a-z，如何優化空間？
    *   **A:** Use an array of size 26 instead of a hash map.
    *   **答：** 使用大小為 26 的陣列代替雜湊表。
*   **Q:** How to implement delete?
    **問：** 如何實作刪除？
    *   **A:** Recursively delete nodes bottom-up if they have no other children and are not end-of-word for another word.
    *   **答：** 如果節點沒有其他子節點且不是其他單字的結尾，則由下而上遞迴刪除節點。

---

## 7. Practice Problems (練習題)

### 1. Implement Trie (Prefix Tree) [Easy/Beginner]
*   **Goal:** Write the standard class without looking at the reference.
    **目標：** 在不看參考解答的情況下寫出標準類別。
*   **Hint:** Remember the `is_end` flag.
    **提示：** 記得 `is_end` 旗標。

### 2. Longest Common Prefix [Easy/Intermediate]
*   **Problem:** Find the longest string that is a prefix of all strings in an array.
    **問題：** 找出陣列中所有字串的最長共同前綴字串。
*   **Hint with Trie:** Insert all words. Traverse from root until you hit a node with multiple children or `is_end` is True.
    **Trie 思路提示：** 插入所有單字。從根節點遍歷，直到遇到有多個子節點的節點或 `is_end` 為 True。

### 3. Design Add and Search Words Data Structure [Intermediate]
*   **Problem:** Support `.` as a wildcard character (matches any letter).
    **問題：** 支援 `.` 作為萬用字元（匹配任何字母）。
*   **Hint:** Use DFS/Recursion. When `.` is met, iterate through all children of the current node.
    **提示：** 使用 DFS/遞迴。當遇到 `.` 時，遍歷當前節點的所有子節點。

---

## 8. Quick Checklists (快速檢核表)

### Self-Review (自我審查)
*   [ ] Did I initialize `root` in the constructor?
    我是否在建構函式中初始化了 `root`？
*   [ ] Did I handle the case where the word to search is longer than the path in the Trie?
    我是否處理了搜尋單字比 Trie 中路徑更長的情況？
*   [ ] Is my `search` method checking `is_end_of_word` at the end?
    我的 `search` 方法最後是否檢查了 `is_end_of_word`？

### Complexity Check (複雜度確認)
*   [ ] Time: Is every operation $O(L)$?
    時間：每個操作是否都是 $O(L)$？
*   [ ] Space: Did I acknowledge the overhead of the Hash Map/Array references?
    空間：我是否認知到雜湊表/陣列參考的額外開銷？

---

## 9. Memory Anchors & Analogies (記憶錨點與類比)

### The Folder System (資料夾系統)
*   **Visual:** Think of your file system.
    **視覺化：** 想想你的檔案系統。
*   **Analogy:**
    *   Root is `/`.
    *   `insert("home")` creates folder `h` -> `o` -> `m` -> `e`.
    *   `insert("host")` reuses `h` -> `o`, then branches to `s` -> `t`.
    *   `is_end` is like a file named "content.txt" inside the folder, proving a valid word ends there.
    *   根節點是 `/`。
    *   `insert("home")` 建立資料夾 `h` -> `o` -> `m` -> `e`。
    *   `insert("host")` 重用 `h` -> `o`，然後分支出 `s` -> `t`。
    *   `is_end` 就像資料夾內的 "content.txt" 檔案，證明一個有效的單字在此結束。

### The Autocomplete Dropdown (自動補全選單)
*   **Concept:** Every time you type a letter, you walk one step deeper into the Trie. The subtree below you contains all possible suggestions.
    **概念：** 每當你輸入一個字母，你就往 Trie 深處走一步。你下方的子樹包含所有可能的建議。