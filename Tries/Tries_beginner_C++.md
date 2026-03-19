Here is the comprehensive guide on **Tries (Prefix Trees)**, tailored for a Senior Software Engineer, focusing on the **Beginner** level fundamentals but delivered with the depth expected of a Principal Engineer.

這是一份針對 **Tries (前綴樹)** 的完整教材，專為資深軟體工程師量身打造，重點在於 **初學者（Beginner）** 級別的基礎夯實，但以首席工程師的深度進行講解。

---

# Data Structure Module: Tries (Prefix Trees)
# 資料結構模組：Tries（前綴樹）

## 1. Learning Goals (學習目標)

*   **Understand the internal structure:** Master the N-ary tree structure where edges represent characters and nodes represent states.
    **理解內部結構：** 掌握 N 元樹結構，其中邊代表字元，節點代表狀態。
*   **Master the "Standard Trie" implementation:** Be able to implement `insert`, `search`, and `startsWith` from scratch in C++ within 5 minutes.
    **掌握「標準 Trie」實作：** 能夠在 5 分鐘內用 C++ 從頭實作 `insert`、`search` 和 `startsWith`。
*   **Differentiate from Hash Maps:** articulate why Tries are superior for prefix-based operations despite higher memory overhead.
    **區分與雜湊表（Hash Maps）的差異：** 能清楚說明為何在基於前綴的操作上，Trie 優於雜湊表，儘管其記憶體開銷較大。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Trie is a tree-like data structure used to store a dynamic set of strings where the keys are usually strings.
Trie 是一種樹狀資料結構，用於儲存動態字串集合，其中的鍵通常是字串。

### Intuition (直覺)
Think of a dictionary. To find "Apple", you look for 'A', then within the 'A' section look for 'p', and so on. A Trie physicalizes this path.
想像一本字典。要找 "Apple"，你會先找 'A'，然後在 'A' 的區塊找 'p'，依此類推。Trie 將這條路徑實體化了。

### Complexity Analysis (複雜度分析)
Let $L$ be the length of the word (key).
設 $L$ 為單字（鍵）的長度。

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Insert** | $O(L)$ | $O(L \times \Sigma)$ | $\Sigma$ is alphabet size (e.g., 26). <br> $\Sigma$ 為字母表大小（如 26）。 |
| **Search** | $O(L)$ | $O(1)$ | No extra space needed during search. <br> 搜尋時無需額外空間。 |
| **Prefix Search** | $O(L)$ | $O(1)$ | Much faster than Hash Map's $O(N \times L)$. <br> 遠快於雜湊表的 $O(N \times L)$。 |

### Use Cases (適用場景)
*   **Autocomplete / Typeahead:** Suggesting words starting with user input.
    **自動補全 / 預先輸入：** 建議以使用者輸入為開頭的單字。
*   **Spell Checker:** Verifying if a word exists in a dictionary.
    **拼字檢查：** 驗證單字是否存在於字典中。
*   **IP Routing (Longest Prefix Match):** Matching IP packets to subnets.
    **IP 路由（最長前綴匹配）：** 將 IP 封包匹配到子網域。

### When NOT to use (不適用場景)
*   **Random Data / Floating Points:** Tries are inefficient for non-string or non-sequence data.
    **隨機數據 / 浮點數：** Trie 對於非字串或非序列數據效率低落。
*   **Exact Match Only:** If you never need prefix lookups, a Hash Map ($O(1)$ average) is faster and more space-efficient.
    **僅需精確匹配：** 如果你永遠不需要前綴查詢，雜湊表（平均 $O(1)$）更快且更省空間。

---

## 3. Typical Patterns (典型題型 / 模式)

For the **Beginner** level, we focus on the foundational pattern.
針對 **初學者** 級別，我們專注於基礎模式。

### The Standard Trie (Array-based) / 標準 Trie（基於陣列）
*   **Structure:** Each node contains an array of pointers (size 26 for lowercase English) and a boolean flag.
    **結構：** 每個節點包含一個指標陣列（針對小寫英文為 26 個）和一個布林標記。
*   **Navigation:** Use the ASCII value of characters to index into the array (e.g., `char - 'a'`).
    **導航：** 使用字元的 ASCII 值作為陣列的索引（例如 `char - 'a'`）。

---

## 4. Example Walkthrough (範例講解)

### Problem: Implement Trie (Prefix Tree)
**LeetCode 208**
Implement a trie with `insert`, `search`, and `startsWith` methods.
實作一個包含 `insert`、`search` 和 `startsWith` 方法的 Trie。

### Approach (思路)

1.  **Brute Force (List/Hash Map):**
    *   Using a `List<String>` makes search $O(N \times L)$.
    *   Using a `HashSet<String>` makes search $O(L)$, but `startsWith` requires scanning all keys ($O(N \times L)$), which is inefficient.
    *   **暴力解（列表/雜湊表）：** 使用 `List` 讓搜尋變 $O(N \times L)$。使用 `HashSet` 讓搜尋變 $O(L)$，但 `startsWith` 需要掃描所有鍵，效率低落。

2.  **Optimization (Trie):**
    *   Share common prefixes to save space and time.
    *   Search time depends only on word length $L$, not total words $N$.
    *   **優化（Trie）：** 共用相同前綴以節省空間與時間。搜尋時間僅取決於單字長度 $L$，而非總單字數 $N$。

### C++ Reference Solution (C++ 參考解)

```cpp
#include <vector>
#include <string>

using namespace std;

// Trie Node Definition
// Trie 節點定義
struct TrieNode {
    // Array to store links to children nodes (for 'a'-'z')
    // 儲存指向子節點連結的陣列（針對 'a'-'z'）
    TrieNode* children[26];
    
    // Flag to indicate if a word ends at this node
    // 標記是否有單字在此節點結束
    bool isEndOfWord;

    // Constructor
    // 建構子
    TrieNode() {
        isEndOfWord = false;
        // Initialize all children to nullptr
        // 將所有子節點初始化為 nullptr
        for (int i = 0; i < 26; i++) {
            children[i] = nullptr;
        }
    }
};

class Trie {
private:
    TrieNode* root;

public:
    // Initialize your data structure here.
    // 在此初始化您的資料結構。
    Trie() {
        root = new TrieNode();
    }

    /** Inserts a word into the trie. */
    /** 將一個單字插入 trie。 */
    // Time: O(L), Space: O(L)
    void insert(string word) {
        TrieNode* curr = root;
        for (char c : word) {
            int index = c - 'a'; // Map char to 0-25 index / 將字元映射到 0-25 索引
            if (curr->children[index] == nullptr) {
                curr->children[index] = new TrieNode();
            }
            curr = curr->children[index];
        }
        // Mark the end of the word
        // 標記單字結束
        curr->isEndOfWord = true;
    }

    /** Returns if the word is in the trie. */
    /** 如果單字在 trie 中則返回 true。 */
    // Time: O(L), Space: O(1)
    bool search(string word) {
        TrieNode* curr = root;
        for (char c : word) {
            int index = c - 'a';
            if (curr->children[index] == nullptr) {
                return false; // Path doesn't exist / 路徑不存在
            }
            curr = curr->children[index];
        }
        // Check if it's actually marked as a complete word
        // 檢查是否確實標記為完整單字
        return curr->isEndOfWord;
    }

    /** Returns if there is any word in the trie that starts with the given prefix. */
    /** 如果 trie 中有任何單字以給定前綴開頭，則返回 true。 */
    // Time: O(L), Space: O(1)
    bool startsWith(string prefix) {
        TrieNode* curr = root;
        for (char c : prefix) {
            int index = c - 'a';
            if (curr->children[index] == nullptr) {
                return false;
            }
            curr = curr->children[index];
        }
        return true; // Prefix exists / 前綴存在
    }
    
    // Destructor to prevent memory leaks (Optional for interviews but good practice)
    // 解構子以防止記憶體洩漏（面試時可選，但為良好習慣）
    // Note: Implementing a recursive delete helper is recommended here.
};
```

### Common Mistakes (錯誤示範)

*   **Mistake:** Forgetting `isEndOfWord` flag.
    *   *Why it's wrong:* Without this, you cannot distinguish between "apple" and "app". If you insert "apple", `search("app")` should return `false` (it's a prefix, not a word), but `startsWith("app")` returns `true`.
    *   **錯誤：** 忘記 `isEndOfWord` 標記。
    *   *為何錯：* 沒有這個標記，無法區分 "apple" 和 "app"。如果你插入 "apple"，`search("app")` 應返回 `false`（它是前綴，不是單字），但 `startsWith("app")` 應返回 `true`。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation (解釋) |
| :--- | :--- |
| **Trie vs. Radix Tree** | A Trie stores one character per node. A Radix Tree (Compact Trie) compresses chains of single-child nodes into edges with strings (e.g., "app" -> "le"). <br> Trie 每個節點存一個字元。Radix Tree（壓縮 Trie）將單子節點鏈壓縮為帶有字串的邊。 |
| **Array vs. Hash Map Nodes** | `children[26]` is fast but wastes space if sparse. `unordered_map<char, Node*>` saves space but has higher constant time overhead. <br> `children[26]` 速度快但稀疏時浪費空間。`unordered_map` 省空間但常數時間開銷較高。 |
| **Memory Limit Exceeded** | Tries consume significant memory due to pointers. Be mindful of constraints ($10^5$ words is fine, $10^7$ might crash). <br> 由於指標，Trie 消耗大量記憶體。注意限制（$10^5$ 單字沒問題，$10^7$ 可能會崩潰）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Narrative Framework (口條框架)
1.  **Clarify Charset:** "Does the input consist only of lowercase English letters 'a'-'z'? Or should we handle full ASCII/Unicode?" (This decides array size vs. Map).
    **釐清字元集：** 「輸入是否僅包含小寫英文字母 'a'-'z'？還是我們需要處理完整的 ASCII/Unicode？」（這決定了陣列大小或使用 Map）。
2.  **Define Node Struct:** Write the `struct` first. It shows you understand the building blocks.
    **定義節點結構：** 先寫 `struct`。這顯示你理解基本構成。
3.  **Draw the Tree:** On the whiteboard, draw `root -> 'c' -> 'a' -> 't' (end)` to visualize.
    **畫出樹狀圖：** 在白板上畫出 `root -> 'c' -> 'a' -> 't' (end)` 以視覺化。

### Common Follow-ups (常見追問)
*   **Q:** How to optimize space if the strings are very sparse?
    **問：** 如果字串非常稀疏，如何優化空間？
    *   **A:** Use a Hash Map inside the node instead of a fixed array, or mention Radix Tree (Compressed Trie).
    *   **答：** 在節點內使用雜湊表代替固定陣列，或提及 Radix Tree（壓縮 Trie）。
*   **Q:** How to implement `delete(word)`?
    **問：** 如何實作 `delete(word)`？
    *   **A:** We need a recursive approach (bottom-up) to remove nodes only if they have no other children and are not end-of-word for another string.
    *   **答：** 我們需要遞迴方法（由下而上），僅在節點沒有其他子節點且非其他字串結尾時移除節點。

---

## 7. Practice Problems (練習題)

### 1. Implement Trie (Prefix Tree) [Easy]
*   **Goal:** Write the standard class without looking at reference.
    **目標：** 不看參考資料寫出標準類別。
*   **Hint:** Focus on the `isEnd` boolean.
    **提示：** 專注於 `isEnd` 布林值。

### 2. Design Add and Search Words Data Structure [Medium]
*   **Goal:** Handle wildcard `.` character.
    **目標：** 處理萬用字元 `.`。
*   **Hint:** When you see `.`, you must use recursion (DFS) to check **all** non-null children at that level.
    **提示：** 當看到 `.` 時，必須使用遞迴（DFS）檢查該層級 **所有** 非空子節點。

### 3. Longest Common Prefix [Easy/Medium]
*   **Goal:** Find the longest string that is a prefix of all strings.
    **目標：** 找出是所有字串前綴的最長字串。
*   **Hint:** Insert all words into Trie. Traverse from root while `count(children) == 1` and `!isEnd`.
    **提示：** 將所有單字插入 Trie。從根節點遍歷，條件為 `子節點數 == 1` 且 `!isEnd`。

---

## 8. Quick Checklists (快速檢核表)

*   [ ] **Initialization:** Did I set `isEndOfWord = false` and `children` to `nullptr` in the constructor?
    **初始化：** 我是否在建構子中將 `isEndOfWord` 設為 `false` 並將 `children` 設為 `nullptr`？
*   [ ] **Index Mapping:** Am I correctly doing `char - 'a'`? What if the input has 'A'?
    **索引映射：** 我是否正確執行 `char - 'a'`？如果輸入有 'A' 怎麼辦？
*   [ ] **Null Check:** Before accessing `curr->children[index]`, did I check if it exists?
    **空值檢查：** 在存取 `curr->children[index]` 之前，我是否檢查它是否存在？
*   [ ] **Return Value:** For `search`, do I return `curr->isEndOfWord`? For `startsWith`, do I return `true`?
    **返回值：** 對於 `search`，我是否返回 `curr->isEndOfWord`？對於 `startsWith`，我是否返回 `true`？

---

## 9. Memory Anchors (記憶錨點)

*   **Visual Analogy:** Think of a **File System Folder Structure**.
    **視覺類比：** 想像一個 **檔案系統資料夾結構**。
    *   Root is `/`.
    *   Folder `u` -> Folder `s` -> Folder `r` (Path: `/usr`).
    *   `isEndOfWord` is like a file named "file" existing in that folder.
    *   根目錄是 `/`。資料夾 `u` -> 資料夾 `s` -> 資料夾 `r`（路徑：`/usr`）。`isEndOfWord` 就像該資料夾中存在一個名為 "file" 的檔案。

*   **Code Mnemonics:** "Walk down the tree."
    **程式碼口訣：** 「順著樹往下走。」
    *   Loop char -> Calculate Index -> Check Null -> Move Pointer.
    *   迴圈字元 -> 計算索引 -> 檢查空值 -> 移動指標。