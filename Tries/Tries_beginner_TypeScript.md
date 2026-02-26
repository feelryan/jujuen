# Module: Tries (Prefix Trees)
# 模組：Tries（字首樹 / 前綴樹）

## 1. Learning Goals (學習目標)

*   **Understand the internal structure of a Trie (N-ary tree).**
    理解 Trie 的內部結構（N 元樹）。
*   **Master the implementation of Insert, Search, and StartsWith operations.**
    掌握插入（Insert）、搜尋（Search）與前綴確認（StartsWith）的操作實作。
*   **Analyze Time and Space Complexity compared to Hash Maps.**
    分析其與雜湊表（Hash Maps）相比的時間與空間複雜度。
*   **Identify scenarios where Tries are superior (e.g., Autocomplete).**
    識別 Trie 優於其他結構的場景（例如：自動補全）。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
A Trie (pronounced "try") is a tree-based data structure used to efficiently store and retrieve keys in a dataset of strings.
Trie（發音同 "try"）是一種基於樹的資料結構，用於高效地儲存與檢索字串資料集中的鍵值。

### Intuition (直覺)
Think of a dictionary or a file system path.
想像一本字典或檔案系統路徑。
Instead of storing "cat" and "car" separately, we store "c" -> "a", then branch off to "t" and "r". Common prefixes are stored only once.
我們不分別儲存 "cat" 和 "car"，而是儲存 "c" -> "a"，然後分支成 "t" 和 "r"。共同的前綴只會被儲存一次。

### Complexity (複雜度)
*   **Time (時間):** $O(L)$ for insert/search, where $L$ is the length of the string.
    插入/搜尋皆為 $O(L)$，其中 $L$ 為字串長度。
    *Note: This is often faster than a Hash Map ($O(L)$) in practice because there are no hash collisions to handle.*
    *註：實務上這通常比雜湊表（$O(L)$）快，因為不需要處理雜湊碰撞。*
*   **Space (空間):** $O(N \times L \times \Sigma)$ in the worst case, where $\Sigma$ is the alphabet size.
    最差情況下為 $O(N \times L \times \Sigma)$，其中 $\Sigma$ 是字母集大小。
    *However, it saves significant space when many strings share prefixes.*
    *然而，當許多字串共用前綴時，它能顯著節省空間。*

### When to Use (適用場景)
*   **Autocomplete / Typeahead:** Suggesting words based on a prefix.
    自動補全 / 預先輸入：根據前綴建議單字。
*   **Spell Checker:** Verifying if a word exists.
    拼字檢查：驗證單字是否存在。
*   **IP Routing (Longest Prefix Match):** Matching network packets.
    IP 路由（最長前綴匹配）：匹配網路封包。

### When NOT to Use (不適用場景)
*   **Generic Key-Value Store:** If keys are random (e.g., UUIDs) with no shared prefixes, a Hash Map is more space-efficient.
    通用鍵值儲存：如果鍵值是隨機的（如 UUID）且無共同前綴，雜湊表在空間上更有效率。

---

## 3. Typical Patterns (典型題型 / 模式)

Even at a beginner level, you must recognize these patterns:
即使在初學階段，你也必須認得這些模式：

1.  **Standard Trie (標準 Trie):**
    Implement `insert`, `search`, `startsWith`.
    實作 `insert`、`search`、`startsWith`。
2.  **Trie with Map/Array (使用 Map 或陣列的 Trie):**
    Using an Array of size 26 for lowercase English letters (speed optimization) vs. using a Map (flexibility).
    使用大小為 26 的陣列處理小寫英文字母（速度優化） vs. 使用 Map（靈活性）。
3.  **Prefix Counting (前綴計數):**
    Storing a `count` variable in each node to know how many words share this prefix.
    在每個節點儲存 `count` 變數，以得知有多少單字共用此前綴。

---

## 4. Example Walkthrough (範例講解)

### Problem: Implement Trie (Prefix Tree)
### 問題：實作 Trie（前綴樹）

**Problem Statement (問題重述):**
Design a data structure that supports adding new words and finding if a string matches any previously added string (whole word or prefix).
設計一個資料結構，支援新增單字，並查詢字串是否匹配先前新增的單字（完整單字或前綴）。

**Approach (思路):**

1.  **Brute Force (List of Strings):**
    *   Store strings in an array `string[]`.
    *   Search is $O(N \times L)$. Too slow.
    *   暴力法（字串陣列）：搜尋速度太慢。

2.  **Optimization (Hash Set):**
    *   Store strings in `Set<string>`.
    *   Exact match is $O(L)$.
    *   **But:** `startsWith` (prefix search) is still slow or requires storing all prefixes.
    *   優化（雜湊集合）：精確匹配很快，但前綴搜尋仍然很慢，或需要儲存所有前綴。

3.  **Best Solution (Trie):**
    *   Use a tree where each node represents a character.
    *   Mark the end of a word with a boolean flag.
    *   最佳解（Trie）：使用樹狀結構，每個節點代表一個字元，並用布林值標記單字結尾。

**TypeScript Solution (參考解):**

```typescript
/**
 * TrieNode represents a single character in the tree.
 * TrieNode 代表樹中的單一字元。
 */
class TrieNode {
    // Using a Map allows for flexible character sets (Unicode, etc.)
    // 使用 Map 允許靈活的字元集（如 Unicode 等）
    // For strictly lowercase 'a-z', an Array(26) is faster but less "Senior" friendly for general purpose.
    // 針對嚴格的 'a-z' 小寫字母，Array(26) 較快，但較不符合資深工程師的通用設計思維。
    children: Map<string, TrieNode>;
    isEnd: boolean;

    constructor() {
        this.children = new Map();
        this.isEnd = false;
    }
}

class Trie {
    private root: TrieNode;

    constructor() {
        this.root = new TrieNode();
    }

    /**
     * Inserts a word into the trie.
     * 將單字插入 Trie 中。
     * Time: O(L), Space: O(L)
     */
    insert(word: string): void {
        let node = this.root;
        for (const char of word) {
            // If the path doesn't exist, create it.
            // 如果路徑不存在，則建立它。
            if (!node.children.has(char)) {
                node.children.set(char, new TrieNode());
            }
            // Move to the next node.
            // 移動到下一個節點。
            node = node.children.get(char)!;
        }
        // Mark the end of the word.
        // 標記單字的結尾。
        node.isEnd = true;
    }

    /**
     * Returns true if the word is in the trie.
     * 如果單字存在於 Trie 中，則返回 true。
     * Time: O(L), Space: O(1)
     */
    search(word: string): boolean {
        const node = this.searchNode(word);
        // It must be a valid node AND marked as an end of a word.
        // 必須是有效節點，且被標記為單字結尾。
        return node !== null && node.isEnd;
    }

    /**
     * Returns true if there is any word in the trie that starts with the given prefix.
     * 如果 Trie 中有任何單字以給定前綴開頭，則返回 true。
     * Time: O(L), Space: O(1)
     */
    startsWith(prefix: string): boolean {
        const node = this.searchNode(prefix);
        // As long as the node exists, the prefix exists.
        // 只要節點存在，前綴就存在。
        return node !== null;
    }

    /**
     * Helper function to traverse the tree.
     * 用於遍歷樹的輔助函式。
     */
    private searchNode(str: string): TrieNode | null {
        let node = this.root;
        for (const char of str) {
            if (node.children.has(char)) {
                node = node.children.get(char)!;
            } else {
                return null;
            }
        }
        return node;
    }
}

// Usage Example
const trie = new Trie();
trie.insert("apple");
console.log(trie.search("apple"));   // true
console.log(trie.search("app"));     // false (prefix exists, but not whole word)
console.log(trie.startsWith("app")); // true
trie.insert("app");
console.log(trie.search("app"));     // true
```

**Common Mistake (錯誤示範):**

```typescript
// Mistake: Forgetting 'isEnd'
// 錯誤：忘記 'isEnd' 標記
search(word: string): boolean {
    let node = this.root;
    for (const char of word) {
        if (!node.children.has(char)) return false;
        node = node.children.get(char)!;
    }
    return true; // WRONG! This returns true for "app" even if only "apple" was inserted.
                 // 錯！即使只插入了 "apple"，這也會對 "app" 返回 true。
}
```

---

## 5. Common Pitfalls & Confusing Concepts (常見陷阱與易混淆概念)

| Concept | Explanation & Contrast |
| :--- | :--- |
| **Prefix vs. Word** | Just because you can traverse the path ("a"-"p"-"p") doesn't mean the word "app" exists. Always check `isEnd`. <br> 能走完路徑（"a"-"p"-"p"）不代表單字 "app" 存在。務必檢查 `isEnd`。 |
| **Space Complexity** | Juniors often think Tries use *less* space than Hash Maps. This is only true if words share many prefixes. Otherwise, object overhead makes Tries heavy. <br> 初階工程師常誤以為 Trie 比雜湊表省空間。只有在單字共用大量前綴時才成立，否則物件開銷會使 Trie 很佔空間。 |
| **Map vs. Array[26]** | `Array[26]` is faster and uses less memory for pure English lowercase. `Map` handles Unicode/Emojis but is slower. Clarify requirements. <br> `Array[26]` 對純小寫英文更快且省記憶體。`Map` 能處理 Unicode/Emoji 但較慢。需釐清需求。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (闡述口條框架)
1.  **Clarify Constraints:** "Are the inputs only lowercase English letters? Or full Unicode?"
    釐清限制：「輸入只有小寫英文字母嗎？還是完整的 Unicode？」
2.  **Define Node Structure:** "I will define a `TrieNode` class. Since we are dealing with standard ASCII, I can use an array, but for production-grade TS, I prefer a Map for readability."
    定義節點結構：「我會定義一個 `TrieNode` 類別。既然處理標準 ASCII，我可以用陣列，但為了生產級 TS 程式碼，我傾向用 Map 以提升可讀性。」
3.  **Explain the Trade-off:** "I'm choosing a Trie over a Hash Set because we need efficient prefix lookups."
    解釋權衡：「我選擇 Trie 而非 Hash Set，是因為我們需要高效的前綴查詢。」

### Whiteboard Strategy (白板策略)
*   Draw the root as an empty circle.
    畫一個空圓圈作為根節點。
*   Draw "cat" and "car". Show the split at 'c' -> 'a'.
    畫出 "cat" 和 "car"。展示在 'c' -> 'a' 之後的分岔。
*   Color/mark the nodes 't' and 'r' to indicate `isEnd = true`.
    將節點 't' 和 'r' 塗色或標記，以表示 `isEnd = true`。

### Common Follow-ups (常見追問)
*   **Q:** How to delete a word?
    **A:** We need to recursively remove nodes bottom-up, but only if they have no other children and are not end-nodes for another word.
    **問：** 如何刪除單字？
    **答：** 我們需要由下而上遞迴移除節點，但前提是該節點沒有其他子節點，且不是另一個單字的結尾。
*   **Q:** How to optimize space?
    **A:** Use a **Radix Tree** (Compressed Trie) where nodes can store strings ("app" -> "le") instead of single chars.
    **問：** 如何優化空間？
    **答：** 使用 **Radix Tree**（壓縮 Trie），節點可以儲存字串（"app" -> "le"）而非單一字元。

---

## 7. Practice Problems (練習題)

### 1. Implement Trie (Prefix Tree) (Easy/Medium)
*   **Goal:** Write the class from scratch without looking.
    目標：不看講義，從頭寫出類別。
*   **Hint:** Remember `isEnd`.
    提示：記得 `isEnd`。

### 2. Design Add and Search Words Data Structure (Medium)
*   **Goal:** Support `.` as a wildcard (e.g., search "b.d" matches "bad", "bed").
    目標：支援 `.` 作為萬用字元（例如：搜尋 "b.d" 匹配 "bad"、"bed"）。
*   **Hint:** Use DFS/Recursion when you hit a `.`, checking all children.
    提示：遇到 `.` 時使用 DFS/遞迴，檢查所有子節點。

### 3. Longest Common Prefix (Easy - but solve with Trie)
*   **Goal:** Find the longest string that is a prefix of all strings in an array.
    目標：找出陣列中所有字串的最長共同前綴。
*   **Hint:** Insert all words. Traverse from root until you find a node with more than 1 child or `isEnd` is true.
    提示：插入所有單字。從根節點開始遍歷，直到遇到一個擁有超過 1 個子節點的節點，或是 `isEnd` 為真。

---

## 8. Quick Checklists (快速檢核表)

Use this before submitting your code:
提交程式碼前請使用此表：

*   [ ] **Root Initialization:** Did I initialize `root` in the constructor?
    **根節點初始化：** 我有在建構子中初始化 `root` 嗎？
*   [ ] **End of Word:** Did I set `isEnd = true` after the loop in `insert`?
    **單字結尾：** 我有在 `insert` 的迴圈結束後設定 `isEnd = true` 嗎？
*   [ ] **Return Logic:** Does `search` return `node.isEnd` while `startsWith` returns `true` (if node exists)?
    **回傳邏輯：** `search` 是否回傳 `node.isEnd`，而 `startsWith` 是否回傳 `true`（若節點存在）？
*   [ ] **Null Checks:** Did I handle the case where a child does not exist (return false/null)?
    **Null 檢查：** 我有處理子節點不存在的情況嗎（回傳 false/null）？

---

## 9. Mnemonics & Analogies (記憶錨點與類比)

### The "Folder Structure" Analogy (「資料夾結構」類比)
*   **Root:** The `C:/` drive.
    **根節點：** `C:/` 磁碟機。
*   **Edges:** Folder names (or characters).
    **邊：** 資料夾名稱（或字元）。
*   **Nodes:** The folders themselves.
    **節點：** 資料夾本身。
*   **isEnd:** A file inside the folder named `file_exists.txt`.
    **isEnd：** 資料夾內一個名為 `file_exists.txt` 的檔案。

> If you have folders `/usr/bin` and `/usr/lib`:
> You don't create `/usr` twice. You enter `/usr`, then choose `bin` or `lib`.
> 如果你有 `/usr/bin` 和 `/usr/lib`：
> 你不會建立 `/usr` 兩次。你會進入 `/usr`，然後選擇 `bin` 或 `lib`。

### Visual Anchor (圖像錨點)
Visualize the word **"TRIE"** as **"TREE" + "RETRIEVAL"**.
將單字 **"TRIE"** 視覺化為 **"TREE"（樹） + "RETRIEVAL"（檢索）**。