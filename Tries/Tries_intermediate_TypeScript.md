# Data Structure & Algorithms: Tries (Prefix Trees)
# 資料結構與演算法：字典樹（前綴樹）

## 1. Learning Objectives（學習目標）

*   **Master the internal structure of a Trie and its implementation in TypeScript.**
    掌握 Trie 的內部結構及其在 TypeScript 中的實作方式。
*   **Understand the trade-offs between Tries and Hash Maps regarding time and space complexity.**
    理解 Trie 與雜湊表（Hash Maps）在時間與空間複雜度上的權衡。
*   **Identify scenarios requiring prefix-based lookups or bitwise optimizations.**
    識別需要基於前綴查詢或位元運算優化的場景。
*   **Learn to implement DFS/Backtracking on Tries for complex search problems.**
    學習如何在 Trie 上實作深度優先搜尋（DFS）/回溯法以解決複雜搜尋問題。

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）

*   **A Trie is a tree-like data structure used to store a dynamic set of strings where the keys are usually strings.**
    Trie 是一種樹狀資料結構，用於儲存動態字串集合，其中的鍵通常是字串。
*   **Unlike a binary search tree, no node in the tree stores the key associated with that node; instead, its position in the tree defines the key.**
    與二元搜尋樹不同，樹中的節點不儲存與該節點關聯的鍵；相反，其在樹中的位置定義了鍵。
*   **Intuition: Think of a physical dictionary where you look up a word by its first letter, then the second, and so on.**
    直覺：想像一本實體字典，你透過第一個字母查找單字，接著是第二個，依此類推。

### Complexity（複雜度）

*   **Time Complexity (Insert/Search): $O(L)$, where $L$ is the length of the word.**
    時間複雜度（插入/搜尋）：$O(L)$，其中 $L$ 是單字的長度。
*   **Space Complexity: $O(N \cdot L \cdot \Sigma)$, where $N$ is the number of words, $L$ is the average length, and $\Sigma$ is the alphabet size.**
    空間複雜度：$O(N \cdot L \cdot \Sigma)$，其中 $N$ 是單字數量，$L$ 是平均長度，$\Sigma$ 是字母表大小。

### When to Use / Not Use（適用與不適用場景）

*   **Use when: You need efficient prefix lookups (Autocomplete), spell checking, or solving "Maximum XOR" problems.**
    適用場景：你需要高效的前綴查詢（自動完成）、拼字檢查，或解決「最大 XOR」問題時。
*   **Don't use when: The dataset is small, or strings have very little overlap (sparse data), causing high memory overhead compared to a Hash Set.**
    不適用場景：資料集很小，或字串重疊極少（稀疏資料），這會導致比雜湊集合（Hash Set）高出許多的記憶體開銷。

---

## 3. Typical Patterns（典型題型 / 模式）

1.  **Standard Prefix Search (標準前綴搜尋)**
    *   Basic insert, search, and `startsWith` operations.
    *   基礎的插入、搜尋與 `startsWith` 操作。
2.  **Trie + DFS/Backtracking (Trie 結合 DFS/回溯)**
    *   Used in word games (e.g., Boggle) to find all valid words on a board.
    *   用於文字遊戲（如 Boggle）以找出棋盤上所有有效的單字。
3.  **Bitwise Trie (位元 Trie)**
    *   Storing numbers as binary strings (0s and 1s) to solve XOR maximization problems.
    *   將數字儲存為二進位字串（0 與 1），以解決 XOR 最大化問題。
4.  **Optimized Storage (優化儲存)**
    *   Storing metadata (e.g., word frequency, passing count) at each node to speed up queries.
    *   在每個節點儲存元數據（如單字頻率、經過次數）以加速查詢。

---

## 4. Example Walkthrough（範例講解）

### Problem: Implement a Trie (Prefix Tree)
### 問題：實作字典樹（前綴樹）

**Problem Statement:**
Implement a Trie class that supports `insert`, `search`, and `startsWith` methods.
**問題重述：**
實作一個 Trie 類別，支援 `insert`（插入）、`search`（搜尋）與 `startsWith`（前綴確認）方法。

### Approach: Brute Force vs. Optimized
### 思路：暴力解 vs. 最佳解

*   **Brute Force (Using Array/List):**
    *   Store words in an array `string[]`.
    *   將單字儲存在陣列 `string[]` 中。
    *   `search` takes $O(N \cdot L)$ because we iterate through all words and compare characters.
    *   `search` 需要 $O(N \cdot L)$，因為我們必須遍歷所有單字並比較字元。
    *   `startsWith` also takes $O(N \cdot L)$.
    *   `startsWith` 同樣需要 $O(N \cdot L)$。

*   **Optimized (Using Trie):**
    *   Store characters as nodes. Common prefixes share the same path.
    *   將字元儲存為節點。共同的前綴共享相同的路徑。
    *   `search` and `startsWith` take $O(L)$. This is independent of the total number of words $N$.
    *   `search` 與 `startsWith` 僅需 $O(L)$。這與總單字數量 $N$ 無關。

### TypeScript Implementation (Reference Solution)
### TypeScript 參考解

```typescript
/**
 * Represents a node in the Trie.
 * 代表 Trie 中的一個節點。
 */
class TrieNode {
    // Using a Map allows for flexible character sets (Unicode), not just 'a'-'z'.
    // 使用 Map 允許靈活的字元集（Unicode），不僅限於 'a'-'z'。
    children: Map<string, TrieNode>;
    
    // Marks the end of a valid word.
    // 標記一個有效單字的結尾。
    isEndOfWord: boolean;

    constructor() {
        this.children = new Map();
        this.isEndOfWord = false;
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
        let currentNode = this.root;

        for (const char of word) {
            // If the path doesn't exist, create a new node.
            // 如果路徑不存在，建立一個新節點。
            if (!currentNode.children.has(char)) {
                currentNode.children.set(char, new TrieNode());
            }
            // Move to the next node.
            // 移動到下一個節點。
            currentNode = currentNode.children.get(char)!;
        }
        
        // Mark the last node as the end of a word.
        // 將最後一個節點標記為單字結尾。
        currentNode.isEndOfWord = true;
    }

    /**
     * Returns true if the word is in the trie.
     * 如果單字在 Trie 中，返回 true。
     * Time: O(L), Space: O(1)
     */
    search(word: string): boolean {
        const node = this.searchPrefix(word);
        // The node must exist AND it must be marked as an end of a word.
        // 該節點必須存在，且必須被標記為單字結尾。
        return node !== null && node.isEndOfWord;
    }

    /**
     * Returns true if there is any word in the trie that starts with the given prefix.
     * 如果 Trie 中有任何單字以給定前綴開頭，返回 true。
     * Time: O(L), Space: O(1)
     */
    startsWith(prefix: string): boolean {
        const node = this.searchPrefix(prefix);
        // As long as the node exists, the prefix is valid.
        // 只要節點存在，該前綴即為有效。
        return node !== null;
    }

    /**
     * Helper function to traverse the Trie.
     * 遍歷 Trie 的輔助函式。
     */
    private searchPrefix(prefix: string): TrieNode | null {
        let currentNode = this.root;
        
        for (const char of prefix) {
            if (currentNode.children.has(char)) {
                currentNode = currentNode.children.get(char)!;
            } else {
                // Path broken, prefix not found.
                // 路徑中斷，未找到前綴。
                return null;
            }
        }
        
        return currentNode;
    }
}
```

### Common Mistakes & Why They Are Wrong
### 錯誤示範 & 為何錯

**Mistake 1: Forgetting `isEndOfWord`**
**錯誤 1：忘記 `isEndOfWord`**

*   *Code:* Returning `true` just because the loop finished in `search`.
*   *Why:* If you insert "apple", searching for "app" should return `false` (it's a prefix, not a whole word). Without `isEndOfWord`, "app" would return `true`.
*   *程式碼：* 僅因為迴圈結束就在 `search` 中返回 `true`。
*   *原因：* 如果你插入 "apple"，搜尋 "app" 應該返回 `false`（它是前綴，不是完整單字）。若沒有 `isEndOfWord`，"app" 會被誤判為 `true`。

**Mistake 2: Using `Array(26)` for generic inputs**
**錯誤 2：對通用輸入使用 `Array(26)`**

*   *Why:* While `Array(26)` is slightly faster for strictly lowercase English letters, it fails for Unicode or special characters. For a Senior role, prefer `Map` or `Object` unless constraints strictly specify 'a'-'z'.
*   *原因：* 雖然 `Array(26)` 對於嚴格的小寫英文字母稍快，但它無法處理 Unicode 或特殊字元。對於資深職位，除非限制嚴格指定 'a'-'z'，否則應優先使用 `Map` 或 `Object`。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation & Contrast |
| :--- | :--- |
| **Trie vs. HashMap** | **HashMap** provides $O(1)$ lookup but cannot efficiently find words with a specific prefix. **Trie** is $O(L)$ but excels at prefix operations. <br> **HashMap** 提供 $O(1)$ 查詢，但無法高效找出具特定前綴的單字。**Trie** 是 $O(L)$ 但擅長前綴操作。 |
| **Node vs. Edge** | Conceptually, the character is on the **edge** (link), not the node. The node represents the state *after* traversing that character. <br> 概念上，字元位於**邊**（連結）上，而非節點。節點代表遍歷該字元*後*的狀態。 |
| **Space Overhead** | Tries can be memory-heavy due to many pointers/references. A "Compressed Trie" (Radix Tree) collapses single-child chains to save space. <br> Trie 因大量指標/引用可能佔用大量記憶體。「壓縮 Trie」（Radix Tree）透過摺疊單一子節點鏈來節省空間。 |

---

## 6. Interview Strategy（面試實戰建議）

### Communication Framework（口條框架）

1.  **Clarify Constraints:** "Is the input limited to lowercase English letters, or should I handle full Unicode?" (This decides Array vs. Map).
    **釐清限制：**「輸入僅限於小寫英文字母，還是我應該處理完整的 Unicode？」（這決定了使用 Array 還是 Map）。
2.  **Define Interface:** "I will define a `TrieNode` class to encapsulate the children and the end-of-word flag."
    **定義介面：**「我將定義一個 `TrieNode` 類別來封裝子節點與單字結尾標記。」
3.  **Discuss Complexity:** "Search time will be proportional to the word length, not the dataset size."
    **討論複雜度：**「搜尋時間將與單字長度成正比，而非資料集大小。」

### Whiteboard Strategy（白板策略）

*   **Draw the Tree:** Draw a root node, then arrows labeled with characters ('c', 'a', 't') leading to nodes. Circle the node after 't' to show `isEnd = true`.
    **畫出樹狀圖：** 畫一個根節點，然後畫出標有字元（'c', 'a', 't'）的箭頭指向節點。將 't' 之後的節點圈起來表示 `isEnd = true`。
*   **Trace the Path:** When explaining `search("cat")`, physically trace the edges with your finger/marker.
    **追蹤路徑：** 解釋 `search("cat")` 時，用手指/筆實際追蹤邊的路徑。

### Common Follow-ups（常見追問）

*   **Q: How to delete a word?**
    *   *A:* Recursively go down. When coming back up, delete nodes if they have no other children and are not end-of-words for other strings.
    *   *答：* 遞迴向下。回溯時，如果節點沒有其他子節點且不是其他字串的結尾，則刪除該節點。
*   **Q: How to optimize space?**
    *   *A:* Use a Radix Tree (Patricia Trie) or use a single array with bit manipulation if the alphabet is small.
    *   *答：* 使用 Radix Tree（Patricia Trie），或者若字母表很小，使用單一陣列配合位元操作。

---

## 7. Practice Problems（練習題）

### 1. Easy: Longest Common Prefix (LeetCode 14)
*   **Prompt:** Find the longest common prefix string amongst an array of strings.
    **題目：** 在字串陣列中找出最長的共同前綴字串。
*   **Hint:** Can be done without Trie, but building a Trie and traversing until a node has >1 children or isEndOfWord is a great exercise.
    **提示：** 可以不用 Trie 完成，但建立 Trie 並遍歷直到節點有 >1 個子節點或是單字結尾，是很好的練習。

### 2. Medium: Design Add and Search Words Data Structure (LeetCode 211)
*   **Prompt:** Support `.` as a wildcard matching any character.
    **題目：** 支援 `.` 作為匹配任何字元的萬用字元。
*   **Hint:** Use DFS. If char is `.`, iterate through all children of the current node recursively.
    **提示：** 使用 DFS。如果字元是 `.`，遞迴遍歷當前節點的所有子節點。

### 3. Hard: Word Search II (LeetCode 212)
*   **Prompt:** Find all words from a dictionary in a 2D board of characters.
    **題目：** 在二維字元棋盤中找出字典裡的所有單字。
*   **Hint:** Build a Trie from the dictionary. Run DFS (Backtracking) on the board, pruning the search if the current path is not in the Trie. **Critical optimization:** Remove the word from Trie after finding it to avoid duplicates and useless searching.
    **提示：** 從字典建立 Trie。在棋盤上執行 DFS（回溯），如果當前路徑不在 Trie 中則剪枝。**關鍵優化：** 找到單字後將其從 Trie 中移除，以避免重複與無效搜尋。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Class Structure:** Did I separate `TrieNode` and `Trie` logic?
    **類別結構：** 我是否分離了 `TrieNode` 與 `Trie` 的邏輯？
*   [ ] **End of Word:** Did I set `isEndOfWord = true` at the end of insertion?
    **單字結尾：** 我是否在插入結束時設定了 `isEndOfWord = true`？
*   [ ] **Return Values:** Does `search` return `false` if the path ends but `isEndOfWord` is false?
    **回傳值：** 如果路徑結束但 `isEndOfWord` 為 false，`search` 是否回傳 `false`？
*   [ ] **Null Checks:** Did I handle cases where `children.get(char)` returns undefined?
    **Null 檢查：** 我是否處理了 `children.get(char)` 回傳 undefined 的情況？
*   [ ] **Complexity:** Is my loop dependent on word length ($L$), not array size ($N$)?
    **複雜度：** 我的迴圈是否取決於單字長度 ($L$)，而非陣列大小 ($N$)？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

*   **The "Folder Structure" Analogy:**
    **「資料夾結構」類比：**
    *   Think of the word `/usr/bin/vim`.
    *   Root -> `usr` -> `bin` -> `vim`.
    *   Searching for `/usr/bin` works (prefix).
    *   Files are the "End of Word" markers.
    *   想像路徑 `/usr/bin/vim`。根 -> `usr` -> `bin` -> `vim`。搜尋 `/usr/bin` 是有效的（前綴）。檔案則是「單字結尾」的標記。

*   **Visual Anchor:**
    **視覺錨點：**
    *   Imagine a tree where edges are labeled with letters. The word is spelled out by walking down the branches.
    *   想像一棵樹，邊上標有字母。沿著樹枝向下走即可拼出單字。