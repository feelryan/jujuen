這是一份針對 **Advanced Tries (進階字典樹)** 的面試實戰教材。
This is a battle-ready interview guide for **Advanced Tries**.

內容專為 **Senior Software Engineer (7-12 years exp)** 設計，重點在於從標準字串處理跨越到位元操作（Bitwise Tries）與系統設計應用。
The content is designed for **Senior Software Engineers (7-12 years exp)**, focusing on moving from standard string processing to Bitwise Tries and system design applications.

---

# Advanced Tries (進階字典樹)

## 1. Learning Goals（學習目標）

1.  **超越基礎字串搜尋，掌握位元字典樹（Bitwise Trie）：** 學會利用 Trie 解決 XOR 最大化或子陣列異或問題。
    **Go beyond basic string search and master Bitwise Tries:** Learn to use Tries to solve XOR maximization or subarray XOR problems.
2.  **優化空間複雜度與實作選擇：** 理解何時使用 `HashMap`、固定陣列 (`Node[26]`) 或壓縮路徑（Radix Tree 概念）。
    **Optimize space complexity and implementation choices:** Understand when to use `HashMap`, fixed arrays (`Node[26]`), or path compression (Radix Tree concepts).
3.  **結合回溯法（Backtracking）的高效剪枝：** 在二維網格搜尋（如 Boggle Game）中，利用 Trie 進行極致剪枝。
    **Efficient pruning with Backtracking:** Utilize Tries for extreme pruning in 2D grid searches (like the Boggle Game).
4.  **系統設計視角：** 能夠討論 Trie 在 Typeahead（自動補全）系統中的持久化與序列化挑戰。
    **System Design perspective:** Be able to discuss persistence and serialization challenges of Tries in Typeahead systems.

---

## 2. Core Concepts（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Trie 是一種多元樹（N-ary tree），其節點不直接儲存完整的鍵（Key），而是儲存鍵的「路徑」。
A Trie is an N-ary tree where nodes do not store the full key, but rather the "path" of the key.
對於字串，路徑是字符；對於整數，路徑是二進位位元（0 或 1）。
For strings, the path is characters; for integers, the path is binary bits (0 or 1).

### Complexity（複雜度）
-   **Time:** $O(L)$ for insert/search, where $L$ is the length of the key (or number of bits). Note: It is **independent** of $N$ (number of keys).
    **時間：** 插入/搜尋為 $O(L)$，其中 $L$ 是鍵的長度（或位元數）。注意：這與 $N$（鍵的數量）**無關**。
-   **Space:** $O(N \cdot L \cdot \Sigma)$ in worst case, where $\Sigma$ is the alphabet size.
    **空間：** 最壞情況下為 $O(N \cdot L \cdot \Sigma)$，其中 $\Sigma$ 是字符集大小。

### When to Use (Advanced)（適用場景）
-   **Prefix-based queries:** Autocomplete, IP routing (Longest Prefix Match).
    **基於前綴的查詢：** 自動補全、IP 路由（最長前綴匹配）。
-   **XOR Maximization:** Finding two numbers with max XOR in an array.
    **XOR 最大化：** 在陣列中尋找 XOR 值最大的兩個數字。
-   **Word Search in Grids:** Searching for dictionary words in a 2D board.
    **網格文字搜尋：** 在二維版面上搜尋字典單字。

### When NOT to Use（不適用場景）
-   **Random Access or exact match only:** A Hash Map ($O(1)$) is faster and more space-efficient if prefix features aren't needed.
    **隨機存取或僅需精確匹配：** 如果不需要前綴特性，雜湊表（$O(1)$）更快且更節省空間。
-   **Limited Memory:** Tries have high pointer overhead.
    **記憶體受限：** Trie 具有很高的指標開銷。

---

## 3. Typical Patterns（典型題型 / 模式）

對於資深工程師，面試官通常不會只考「實作一個 Trie」，而是考以下變體：
For senior engineers, interviewers usually won't just ask to "implement a Trie," but rather these variations:

1.  **Bitwise Trie (0/1 Trie):**
    Treat integers as 32-bit binary strings. Used for XOR problems.
    **位元字典樹：** 將整數視為 32 位元二進位字串。用於 XOR 問題。
2.  **Trie + DFS/Backtracking:**
    Used in "Word Search II". The Trie acts as a pruning mechanism to stop DFS early.
    **Trie + 深度優先搜尋/回溯：** 用於「文字搜尋 II」。Trie 作為剪枝機制以提早停止 DFS。
3.  **Augmented Trie (儲存額外資訊):**
    Storing metadata at nodes (e.g., `count` of words passing through, or `top 3 hot searches`) for autocomplete ranking.
    **增強型 Trie：** 在節點儲存元數據（例如：經過此處的單字 `count`，或 `前 3 熱門搜尋`）以用於自動補全排名。

---

## 4. Example Walkthrough（範例講解）

### Problem: Maximum XOR of Two Numbers in an Array
### 問題：陣列中兩個數字的最大異或值

**Problem Statement:**
Given an integer array `nums`, return the maximum result of `nums[i] XOR nums[j]`.
給定一個整數陣列 `nums`，返回 `nums[i] XOR nums[j]` 的最大結果。

**Constraint:** $O(N)$ time complexity is required. Brute force is $O(N^2)$.
**限制：** 需要 $O(N)$ 的時間複雜度。暴力解法是 $O(N^2)$。

### Approach: From Brute Force to Bitwise Trie
### 思路：從暴力法到位元字典樹

1.  **Intuition (直覺):**
    To maximize XOR, for each bit of a number $X$, we want to find another number $Y$ having the **opposite** bit at that position (since $1 \oplus 0 = 1$ and $0 \oplus 1 = 1$).
    為了最大化 XOR，對於數字 $X$ 的每一個位元，我們希望找到另一個數字 $Y$，在該位置擁有**相反**的位元（因為 $1 \oplus 0 = 1$ 且 $0 \oplus 1 = 1$）。

2.  **Greedy Strategy (貪婪策略):**
    We process bits from Most Significant Bit (MSB) to Least Significant Bit (LSB). The higher bits contribute more to the value.
    我們從最高有效位（MSB）處理到最低有效位（LSB）。高位對數值的貢獻更大。

3.  **Trie Structure (Trie 結構):**
    Build a Trie where each node has at most 2 children (0 and 1). Insert all numbers into the Trie.
    建立一個 Trie，每個節點最多有 2 個子節點（0 和 1）。將所有數字插入 Trie。

4.  **Query (查詢):**
    For each number, traverse the Trie. At each step, try to go to the child representing the **opposite bit**. If that path exists, take it (bit becomes 1). If not, take the existing path (bit becomes 0).
    對於每個數字，遍歷 Trie。在每一步，嘗試走向代表**相反位元**的子節點。如果該路徑存在，就走過去（該位元結果為 1）。如果不存在，只能走現有路徑（該位元結果為 0）。

### Java Solution (Advanced)

```java
class Solution {
    // Inner class for Trie Node
    // Trie 節點內部類別
    private static class TrieNode {
        TrieNode[] children = new TrieNode[2]; // 0 and 1
        
        public TrieNode() {}
    }

    private TrieNode root = new TrieNode();

    // Insert a number into the Trie (31 bits down to 0)
    // 將數字插入 Trie (從第 31 位到第 0 位)
    public void insert(int num) {
        TrieNode node = root;
        for (int i = 31; i >= 0; i--) {
            // Extract the i-th bit
            // 取出第 i 個位元
            int bit = (num >> i) & 1;
            if (node.children[bit] == null) {
                node.children[bit] = new TrieNode();
            }
            node = node.children[bit];
        }
    }

    // Find max XOR for a specific number against the Trie
    // 在 Trie 中尋找與特定數字能產生的最大 XOR 值
    public int getMaxXor(int num) {
        TrieNode node = root;
        int maxXor = 0;
        for (int i = 31; i >= 0; i--) {
            int bit = (num >> i) & 1;
            // We want the opposite bit to maximize XOR (1^0=1, 0^1=1)
            // 我們想要相反的位元來最大化 XOR
            int toggleBit = 1 - bit; 
            
            // If the opposite path exists, go there
            // 如果相反路徑存在，就走那邊
            if (node.children[toggleBit] != null) {
                maxXor = maxXor | (1 << i); // Set the i-th bit to 1 in result
                node = node.children[toggleBit];
            } else {
                // Otherwise, forced to go the same bit path
                // 否則，被迫走相同位元的路徑
                node = node.children[bit];
            }
        }
        return maxXor;
    }

    public int findMaximumXOR(int[] nums) {
        // 1. Build the Trie
        // 1. 建構 Trie
        for (int num : nums) {
            insert(num);
        }

        // 2. Iterate each number to find its max XOR partner
        // 2. 迭代每個數字，尋找其最大 XOR 夥伴
        int maxResult = 0;
        for (int num : nums) {
            maxResult = Math.max(maxResult, getMaxXor(num));
        }
        
        return maxResult;
    }
}
```

### Complexity Analysis（複雜度分析）
-   **Time:** $O(N \cdot 32) \approx O(N)$. We iterate 32 bits for each number.
    **時間：** $O(N \cdot 32) \approx O(N)$。我們對每個數字迭代 32 個位元。
-   **Space:** $O(N \cdot 32)$. In the worst case, we store 32 nodes for each number.
    **空間：** $O(N \cdot 32)$。最壞情況下，我們為每個數字儲存 32 個節點。

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Mistake / Confusion (錯誤/混淆) | Correction (修正) |
| :--- | :--- | :--- |
| **Node Structure** | Using `HashMap<Character, Node>` for everything. <br> 什麼都用 HashMap。 | For fixed charsets (a-z), `Node[26]` is faster and uses less memory. Use Map only for Unicode. <br> 對於固定字符集，陣列更快且省記憶體。僅在 Unicode 時使用 Map。 |
| **Word End** | Forgetting `isEndOfWord` boolean. <br> 忘記標記單字結尾。 | "apple" is in the trie, but if you search "app", it should return false (unless implementing `startsWith`). <br> "apple" 在樹中，但搜尋 "app" 應返回 false（除非是 `startsWith`）。 |
| **Bitwise Loop** | Looping from 0 to 31. <br> 從 0 迴圈到 31。 | **Must loop from 31 down to 0.** Higher bits determine magnitude. Greedy approach fails otherwise. <br> **必須從 31 降序到 0。** 高位決定數值大小，否則貪婪法會失效。 |
| **Space Complexity** | Assuming Trie is always space-efficient. <br> 假設 Trie 總是節省空間。 | Trie can be bloated if strings share no prefixes. It uses more pointers than a Hash Set. <br> 如果字串沒有共同前綴，Trie 會很臃腫。它比 Hash Set 使用更多指標。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Clarification (釐清需求)
-   **Character Set:** "Are we dealing with lowercase English letters only, or full ASCII/Unicode?" (Determines Array vs Map).
    **字符集：** 「我們只處理小寫英文字母，還是完整的 ASCII/Unicode？」（決定用陣列還是 Map）。
-   **Case Sensitivity:** "Is 'Apple' the same as 'apple'?"
    **大小寫敏感：** 「'Apple' 和 'apple' 是一樣的嗎？」

### 2. Whiteboard / Coding Strategy (白板策略)
-   **Define Node Class First:** Always start by defining the `TrieNode` class. It shows you understand OO design and data encapsulation.
    **先定義節點類別：** 總是先定義 `TrieNode`。這顯示你懂物件導向設計與資料封裝。
-   **Modularize:** Separate `insert`, `search`, and `startsWith`. Don't write one giant function.
    **模組化：** 分開撰寫 `insert`、`search` 和 `startsWith`。不要寫成一個巨大的函式。

### 3. Follow-up Questions (常見追問)
-   **Q: How to optimize space?**
    **A:** Mention **Radix Tree (Patricia Trie)** where nodes with single children are merged (e.g., 't' -> 'e' -> 'a' becomes a single node "tea").
    **問：如何優化空間？**
    **答：** 提及 **基數樹 (Radix Tree)**，將單一子節點合併（例如 't' -> 'e' -> 'a' 合併為一個節點 "tea"）。
-   **Q: How to handle deletion?**
    **A:** Need to recursively delete nodes. Only delete a node if it has no children AND is not an end of another word.
    **問：如何處理刪除？**
    **答：** 需要遞迴刪除。只有當節點沒有子節點**且**不是另一個單字的結尾時才刪除。

---

## 7. Practice Problems（練習題）

### Level 1: Easy (Warm-up)
**Problem:** Implement Trie (Prefix Tree) (LeetCode 208)
**Hint:** Standard implementation. Use `TrieNode` class with `boolean isEnd` and `TrieNode[] children`.
**提示：** 標準實作。使用包含 `boolean isEnd` 和 `TrieNode[] children` 的 `TrieNode` 類別。

### Level 2: Intermediate (Must Do)
**Problem:** Design Search Autocomplete System (LeetCode 642)
**Hint:** Store `frequency` in nodes. Maintain a list of "hot" words at each node or perform a DFS traversal upon query to find top K.
**提示：** 在節點中儲存 `頻率`。在每個節點維護「熱門」單字列表，或在查詢時執行 DFS 遍歷以找到前 K 個。

### Level 3: Advanced (Differentiation)
**Problem:** Word Search II (LeetCode 212)
**Hint:** Given a 2D board and a list of words, find all words.
**Strategy:** Build a Trie from the list of words. DFS on the board. **Crucial optimization:** Remove the word from Trie (pruning) once found to avoid re-finding it and speed up future searches.
**策略：** 將單字列表建成 Trie。在版面上進行 DFS。**關鍵優化：** 一旦找到單字，就從 Trie 中移除（剪枝），以避免重複尋找並加速後續搜尋。

---

## 8. Quick Checklists（快速檢核表）

在使用 Trie 解決問題時，請自我檢查：
When solving problems with Tries, check yourself:

- [ ] **Root Initialization:** Did I initialize the `root` node in the constructor?
    **根節點初始化：** 我是否在建構子中初始化了 `root` 節點？
- [ ] **Pointer Movement:** Did I move the pointer `node = node.children[index]` inside the loop? (Common bug: infinite loop or staying at root).
    **指標移動：** 我是否在迴圈內移動了指標 `node = node.children[index]`？（常見 Bug：無窮迴圈或停在根節點）。
- [ ] **End Flag:** Did I set `isEnd = true` at the end of insertion?
    **結尾標記：** 我是否在插入結束時設定了 `isEnd = true`？
- [ ] **Bit Manipulation:** For bitwise tries, am I using `1 << i` correctly for reconstruction?
    **位元操作：** 對於位元 Trie，我是否正確使用了 `1 << i` 來重建數值？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The "Dictionary" Analogy (字典類比)
Imagine a physical dictionary. You don't scan every word to find "Apple".
想像一本實體字典。你不會掃描每個單字來找 "Apple"。
1.  You flip to section **A**. (Root -> child 'A')
    你翻到 **A** 區。（根 -> 子節點 'A'）
2.  Then section **P**. (Node 'A' -> child 'P')
    然後是 **P** 區。（節點 'A' -> 子節點 'P'）
3.  Then **P**, **L**, **E**.
    接著是 **P**、**L**、**E**。
4.  The definition is at the node 'E'. (The `isEndOfWord` flag).
    定義就在節點 'E'。（`isEndOfWord` 標記）。

### Visual Anchor: The File System (檔案系統)
`/usr/bin/java`
-   Root `/`
-   Folder `usr`
-   Folder `bin`
-   File `java` (End of path)
Trie is essentially a folder structure where folder names are characters/bits.
Trie 本質上就是一個資料夾結構，其中資料夾名稱是字符或位元。