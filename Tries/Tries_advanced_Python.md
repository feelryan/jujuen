# Advanced Data Structures: Tries (Prefix Trees)
# 進階資料結構：Tries（字典樹/前綴樹）

## 1. Learning Goals（學習目標）

*   **Master the implementation of Tries beyond basic strings.**
    掌握除了基本字串處理之外的 Trie 實作（例如：Bitwise Tries）。
*   **Understand the space-time trade-offs compared to Hash Maps.**
    理解與雜湊表（Hash Maps）相比的時間與空間權衡。
*   **Solve advanced pattern matching and bitwise optimization problems.**
    解決進階的模式匹配與位元運算優化問題（如 Maximum XOR）。
*   **Optimize Trie memory usage for production-level discussions.**
    針對生產環境討論 Trie 的記憶體優化（如壓縮 Trie 或陣列優化）。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition（定義）
A Trie is a tree-like data structure used to store a dynamic set of strings where the keys are usually strings.
Trie 是一種樹狀資料結構，用於儲存動態字串集合，其鍵值通常是字串。

Unlike a binary search tree, no node in the tree stores the key associated with that node; instead, its position in the tree defines the key.
與二元搜尋樹不同，樹中的節點不直接儲存鍵值；相反地，節點在樹中的位置定義了鍵值。

### Intuition（直覺）
Think of a Trie as a "folder structure" or a dictionary where common prefixes are shared.
將 Trie 想像成「資料夾結構」或一本字典，其中共同的前綴是被共享的。

### Complexity（複雜度）
*   **Time Complexity (Insert/Search):** $O(L)$, where $L$ is the length of the word.
    **時間複雜度（插入/搜尋）：** $O(L)$，其中 $L$ 是單字的長度。
    *   *Note:* This is often faster than a Hash Map in worst-case scenarios ($O(L)$ vs $O(L)$ hashing + collisions), and strictly better for prefix queries.
    *   *註：* 這在最壞情況下通常比 Hash Map 快（$O(L)$ 對比 $O(L)$ 的雜湊計算 + 碰撞處理），且在「前綴查詢」上絕對佔優。
*   **Space Complexity:** $O(N \cdot L \cdot \Sigma)$, where $N$ is the number of words and $\Sigma$ is the alphabet size.
    **空間複雜度：** $O(N \cdot L \cdot \Sigma)$，其中 $N$ 是單字數量，$\Sigma$ 是字母集大小。

### When to Use (and Not)（適用與不適用場景）
*   **Use when:** You need prefix-based lookups (autocomplete), bitwise XOR maximization, or sorting strings.
    **適用：** 需要基於前綴的查找（自動補全）、位元 XOR 最大化運算、或字串排序時。
*   **Do not use when:** The dataset is sparse with very few common prefixes (high space overhead), or simple exact match lookups are sufficient (Hash Map is simpler).
    **不適用：** 資料集稀疏且幾乎沒有共同前綴（空間開銷大），或僅需簡單的精確匹配查找（Hash Map 更簡單）時。

---

## 3. Typical Patterns（典型題型 / 模式）

### 1. Standard Prefix Trie（標準前綴樹）
Used for `startsWith`, autocomplete, and spell checkers.
用於 `startsWith`、自動補全與拼寫檢查。

### 2. Bitwise Trie (Binary Trie)（位元字典樹）
Treats integers as 32-bit binary strings. Used for finding Maximum XOR of two numbers in an array.
將整數視為 32 位元的二進制字串。用於尋找陣列中兩數的最大 XOR 值。

### 3. Trie with Backtracking/DFS（Trie 結合回溯/深度優先搜尋）
Used for searching words in a 2D grid (e.g., Boggle, Word Search II).
用於在二維網格中搜尋單字（例如：Boggle 遊戲、Word Search II）。

### 4. Augmented Trie（增強型 Trie）
Storing additional metadata at nodes (e.g., `count` of words passing through, or `top_k` hot searches) to optimize queries.
在節點儲存額外元數據（例如：經過該節點的單字數量 `count`，或熱門搜尋的 `top_k`）以優化查詢。

---

## 4. Example Walkthrough（範例講解）

### Problem: Maximum XOR of Two Numbers in an Array
### 問題：陣列中兩個數的最大 XOR 值

**Difficulty:** Medium/Hard (Advanced application of Tries)
**難度：** 中等/困難（Trie 的進階應用）

#### Problem Statement（問題重述）
Given an integer array `nums`, return the maximum result of `nums[i] XOR nums[j]`.
給定一個整數陣列 `nums`，回傳 `nums[i] XOR nums[j]` 的最大結果。

#### Thought Process（思路）

**1. Brute Force (暴力解):**
Iterate through all pairs $(i, j)$ and calculate XOR.
遍歷所有數對 $(i, j)$ 並計算 XOR。
*   Complexity: $O(N^2)$. Too slow if $N = 10^5$.
*   複雜度：$O(N^2)$。若 $N = 10^5$ 則太慢。

**2. Optimization Intuition (優化直覺):**
To maximize XOR (e.g., `A ^ B`), for each bit of `A`, we want the corresponding bit of `B` to be opposite (0 vs 1, 1 vs 0).
為了最大化 XOR（例如 `A ^ B`），對於 `A` 的每一個位元，我們希望 `B` 對應的位元是相反的（0 對 1，1 對 0）。
We should prioritize higher significant bits.
我們應該優先考慮高位元。

**3. Trie Approach (Trie 解法):**
Insert all numbers into a Binary Trie (32 levels deep).
將所有數字插入一個二元字典樹（深度 32 層）。
For each number, traverse the Trie attempting to go the "opposite" direction of the current bit to maximize the result.
對於每一個數字，遍歷 Trie 並嘗試往當前位元的「相反」方向走，以最大化結果。

#### Python Solution（Python 參考解）

```python
from typing import List

class TrieNode:
    def __init__(self):
        # Children: '0' -> left, '1' -> right
        # 子節點：'0' -> 左，'1' -> 右
        self.children = {} 

class Solution:
    def findMaximumXOR(self, nums: List[int]) -> int:
        root = TrieNode()
        
        # 1. Build the Trie with binary representation of numbers
        # 1. 使用數字的二進制表示法建構 Trie
        for num in nums:
            node = root
            # Process from most significant bit (31) down to 0
            # 從最高有效位 (31) 處理到 0
            for i in range(31, -1, -1):
                # Check if the i-th bit is set
                # 檢查第 i 位是否為 1
                bit = (num >> i) & 1
                if bit not in node.children:
                    node.children[bit] = TrieNode()
                node = node.children[bit]
        
        max_xor = 0
        
        # 2. Query the Trie for each number to find its "best partner"
        # 2. 為每個數字查詢 Trie，尋找它的「最佳拍檔」
        for num in nums:
            node = root
            current_xor = 0
            for i in range(31, -1, -1):
                bit = (num >> i) & 1
                # We want the opposite bit to maximize XOR (1^0=1, 0^1=1)
                # 我們想要相反的位元來最大化 XOR
                toggled_bit = 1 - bit
                
                # If opposite path exists, go there!
                # 如果相反的路徑存在，就往那邊走！
                if toggled_bit in node.children:
                    # If we go opposite, this bit position contributes 2^i to the XOR result
                    # 如果走相反方向，該位元位置對 XOR 結果貢獻 2^i
                    current_xor |= (1 << i)
                    node = node.children[toggled_bit]
                else:
                    # Must go the same path (XOR result for this bit is 0)
                    # 必須走相同的路徑（該位元的 XOR 結果為 0）
                    node = node.children[bit]
            
            max_xor = max(max_xor, current_xor)
            
        return max_xor

# Complexity Analysis:
# Time: O(N * 32) -> O(N). Each number takes constant 32 steps.
# Space: O(N * 32) -> O(N). In worst case, a binary tree with 32 levels.
# 複雜度分析：
# 時間：O(N * 32) -> O(N)。每個數字花費固定的 32 步。
# 空間：O(N * 32) -> O(N)。最壞情況下，一個 32 層的二元樹。
```

---

## 5. Common Pitfalls & Confusing Concepts（常見陷阱與易混淆概念）

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Space Explosion**<br>(空間爆炸) | **Pitfall:** Assuming Trie is always memory efficient. <br>**Reality:** For random strings with no shared prefixes, a Trie consumes significantly more memory than a Hash Map due to node object overhead (especially in Python).<br>**陷阱：** 假設 Trie 總是節省記憶體。<br>**現實：** 對於沒有共同前綴的隨機字串，由於節點物件的開銷（特別是在 Python 中），Trie 消耗的記憶體遠多於 Hash Map。 |
| **Termination Flag**<br>(終止標記) | **Pitfall:** Forgetting `is_end_of_word`. <br>**Consequence:** Cannot distinguish between "apple" and "app". "app" exists as a prefix but might not be a valid word in the dictionary.<br>**陷阱：** 忘記 `is_end_of_word`。<br>**後果：** 無法區分 "apple" 和 "app"。 "app" 作為前綴存在，但可能不是字典中的有效單字。 |
| **Array vs Map**<br>(陣列 vs 雜湊表) | **Pitfall:** Always using `dict`. <br>**Nuance:** If the alphabet is small (e.g., 'a'-'z'), an array `[None] * 26` is faster and more memory-predictable than a Hash Map, though it handles sparse data poorly.<br>**陷阱：** 總是使用 `dict`。<br>**細節：** 如果字母集很小（如 'a'-'z'），陣列 `[None] * 26` 比 Hash Map 更快且記憶體更可預測，儘管它處理稀疏資料較差。 |

---

## 6. Interview Strategy（面試實戰建議）

### Narration Framework（口條框架）
1.  **Identify the Prefix Property:** "Since we are dealing with multiple strings and need to query based on prefixes/patterns, a Trie is a strong candidate."
    **識別前綴特性：** 「由於我們正在處理多個字串，且需要基於前綴或模式進行查詢，Trie 是一個很有力的候選方案。」
2.  **Discuss Trade-offs Early:** "A Trie gives us $O(L)$ lookup, but I'm mindful of the space complexity. If the dataset is huge, we might need a compressed Trie or disk-based solution."
    **儘早討論權衡：** 「Trie 提供 $O(L)$ 的查找速度，但我注意到空間複雜度。如果資料集巨大，我們可能需要壓縮 Trie 或基於磁碟的解決方案。」

### Whiteboard Strategy（白板策略）
*   **Define the Node Class First:** Don't just use nested dictionaries inline. Defining a `class TrieNode` shows architectural maturity.
    **先定義節點類別：** 不要只使用巢狀字典。定義 `class TrieNode` 展現架構成熟度。
*   **Visualize the Path:** Draw a small tree (root -> c -> a -> t) to help the interviewer follow your traversal logic.
    **視覺化路徑：** 畫一棵小樹（root -> c -> a -> t）來幫助面試官跟隨你的遍歷邏輯。

### Common Follow-ups（常見追問）
*   **Q:** How to optimize space?
    **A:** Use **Radix Tree (Patricia Trie)** to compress single-child chains (e.g., compress `t-e-s-t` into one node if no branching).
    **答：** 使用 **Radix Tree（Patricia Trie）** 來壓縮單子節點鏈（例如：若無分支，將 `t-e-s-t` 壓縮為一個節點）。
*   **Q:** How to handle concurrency?
    **A:** Read-Write locks, or Copy-on-Write for high-read scenarios.
    **答：** 讀寫鎖，或針對高讀取場景使用 Copy-on-Write。

---

## 7. Practice Problems（練習題）

### 1. Easy: Implement Trie (Prefix Tree)
*   **Goal:** Boilerplate mastery.
*   **Hint:** Focus on clean class structure (`insert`, `search`, `startsWith`).
*   **目標：** 掌握樣板程式碼。
*   **提示：** 專注於乾淨的類別結構（`insert`, `search`, `startsWith`）。

### 2. Medium: Design Search Autocomplete System
*   **Goal:** Augmenting Trie nodes.
*   **Hint:** Store the `Top 3` hot sentences directly in each Trie node to avoid traversing the entire subtree during a query.
*   **目標：** 增強 Trie 節點。
*   **提示：** 在每個 Trie 節點直接儲存 `Top 3` 熱門句子，以避免查詢時遍歷整個子樹。

### 3. Hard: Word Search II (LeetCode 212)
*   **Goal:** Combining DFS/Backtracking with Trie.
*   **Hint:** Instead of searching for each word in the grid (Time Limit Exceeded), put all words into a Trie and traverse the grid *once*, pruning paths that don't exist in the Trie.
*   **目標：** 結合 DFS/回溯法與 Trie。
*   **提示：** 不要對網格中的每個單字進行搜尋（會超時），而是將所有單字放入 Trie，然後遍歷網格 *一次*，修剪掉 Trie 中不存在的路徑。

---

## 8. Quick Checklists（快速檢核表）

### Self-Review during Interview（面試自我審查）
*   [ ] **Root Initialization:** Did I create a dummy root node?
    **Root 初始化：** 我是否建立了一個虛擬根節點？
*   [ ] **End Flag:** Did I mark `self.is_end = True` when inserting a word?
    **結束標記：** 插入單字時，我是否標記了 `self.is_end = True`？
*   [ ] **Character Mapping:** Am I using `ord(char) - ord('a')` for arrays or just `char` for Hash Maps?
    **字元映射：** 我是使用 `ord(char) - ord('a')`（陣列）還是直接使用 `char`（Hash Map）？
*   [ ] **Return Value:** Does `startsWith` return `True` even if `is_end` is `False`? (It should).
    **回傳值：** 即使 `is_end` 為 `False`，`startsWith` 是否回傳 `True`？（應該要回傳 True）。

---

## 9. Memory Anchors（記憶錨點）

### The "Autocomplete" Mental Model（「自動補全」心智模型）
Imagine typing on your phone.
想像在手機上打字。
*   Type "A": The phone goes to node "A".
*   Type "P": Moves to child "P".
*   Type "P": Moves to child "P".
*   The phone sees a list of suggestions stored at this node ("Apple", "App").
*   手機看到儲存在該節點的建議列表（"Apple", "App"）。

### The "Router" Analogy（「路由器」類比）
For Bitwise Tries, imagine an IP router matching the longest prefix of an IP address (0s and 1s) to decide where to send a packet.
對於位元 Trie，想像一個 IP 路由器匹配 IP 位址的最長前綴（0 和 1），以決定將封包發送到哪裡。