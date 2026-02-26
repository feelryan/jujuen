# Module: Arrays & Hashing (Beginner Level)
# 模組：陣列與雜湊（初階）

## 1. Learning Goals (學習目標)

1.  **Master the trade-off between Time and Space Complexity using Hash Maps.**
    掌握使用雜湊表（Hash Maps）在時間與空間複雜度之間的權衡。
2.  **Understand the memory layout of Arrays versus Hash Tables.**
    理解陣列與雜湊表在記憶體配置上的差異。
3.  **Implement frequency counting and existence checks in $O(1)$ average time.**
    實作平均時間複雜度為 $O(1)$ 的頻率計數與存在性檢查。
4.  **Recognize patterns where sorting simplifies the problem vs. where hashing is superior.**
    辨識何時「排序」能簡化問題，以及何時「雜湊」更為優越的模式。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
*   **Array:** A collection of items stored at contiguous memory locations.
    **陣列：** 儲存於連續記憶體位置的項目集合。
*   **Hash Map (Dictionary in Python):** A structure that maps keys to values using a hash function for direct addressing.
    **雜湊表（Python 中的字典）：** 利用雜湊函數將鍵（Key）映射到值（Value）以進行直接定址的結構。

### Intuition (直覺)
*   **Array:** Think of a bookshelf with numbered slots; great if you know the number (index), slow if you are looking for a specific book title (value).
    **陣列：** 想像一個有編號插槽的書架；如果你知道編號（索引）則非常快，但如果你在找特定書名（值）則很慢。
*   **Hash Map:** Think of a library index card system; you look up the title (key) and instantly find its location (value).
    **雜湊表：** 想像圖書館的索引卡系統；你查詢書名（鍵），然後立即找到它的位置（值）。

### Complexity (複雜度)

| Operation | Array (Unsorted) | Array (Sorted) | Hash Map (Average) | Hash Map (Worst) |
| :--- | :--- | :--- | :--- | :--- |
| **Access (Index)** | $O(1)$ | $O(1)$ | N/A | N/A |
| **Search (Value)** | $O(n)$ | $O(\log n)$ | $O(1)$ | $O(n)$ |
| **Insert/Delete** | $O(n)$ | $O(n)$ | $O(1)$ | $O(n)$ |

### When to Use (適用場景)
*   **Arrays:** When memory is tight, data is fixed-size, or sequential processing is required (cache locality).
    **陣列：** 當記憶體吃緊、資料大小固定，或需要循序處理（快取局部性）時。
*   **Hash Maps:** When you need fast lookups, counting frequencies, or mapping relationships.
    **雜湊表：** 當你需要快速查找、計算頻率或映射關係時。

---

## 3. Typical Patterns (典型題型 / 模式)

Even at a beginner level, recognizing these patterns is crucial for Senior Engineers to solve problems efficiently.
即使在初階程度，辨識這些模式對於資深工程師高效解題至關重要。

1.  **Frequency Map / Counter:**
    Using a hash map to count occurrences of elements.
    **頻率表 / 計數器：** 使用雜湊表來計算元素的出現次數。
2.  **Two-Pass / One-Pass Hash Table:**
    Storing seen elements to find a complement (e.g., Two Sum).
    **雙遍歷 / 單遍歷雜湊表：** 儲存已見過的元素以尋找補數（例如：兩數之和）。
3.  **Anagram Grouping:**
    Using sorted strings or character counts as keys to group similar items.
    **異位構詞分組：** 使用排序後的字串或字元計數作為鍵，將相似項目分組。

---

## 4. Example Walkthrough (範例講解)

### Problem: Two Sum (兩數之和)
**Problem Statement:** Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
**問題重述：** 給定一個整數陣列 `nums` 和一個整數 `target`，回傳兩個數字的索引，使它們相加等於 `target`。

### Approach (思路)

1.  **Brute Force (暴力解):**
    Loop through each element $i$ and check every other element $j$ to see if `nums[i] + nums[j] == target`.
    遍歷每個元素 $i$，並檢查所有其他元素 $j$，看 `nums[i] + nums[j] == target` 是否成立。
    *   *Complexity:* Time $O(n^2)$, Space $O(1)$.

2.  **Optimization (優化 - Using Hash Map):**
    Instead of scanning for the second number, we check if `target - current_number` exists in our history (hash map).
    與其掃描尋找第二個數字，不如檢查 `target - current_number` 是否存在於我們的歷史紀錄（雜湊表）中。
    *   *Complexity:* Time $O(n)$, Space $O(n)$.

### Python Solution (Python 參考解)

```python
from typing import List, Dict, Optional

def two_sum(nums: List[int], target: int) -> Optional[List[int]]:
    # Initialize a hash map to store value -> index mapping
    # 初始化一個雜湊表來儲存 數值 -> 索引 的映射
    prev_map: Dict[int, int] = {} 

    for i, n in enumerate(nums):
        # Calculate the difference needed to reach the target
        # 計算達到目標值所需的差值
        diff = target - n
        
        # Check if the difference is already in the map
        # 檢查該差值是否已經在雜湊表中
        if diff in prev_map:
            # If found, return the index of the difference and current index
            # 如果找到，回傳該差值的索引與當前索引
            return [prev_map[diff], i]
        
        # Store the current number and its index
        # 儲存當前數字及其索引
        prev_map[n] = i
        
    return None # Should not happen based on problem constraints
```

### Common Mistake (錯誤示範)
**Mistake:** Using a list `index()` method inside a loop.
**錯誤：** 在迴圈內使用列表的 `index()` 方法。

```python
# BAD PRACTICE (效能不佳)
for i, n in enumerate(nums):
    diff = target - n
    if diff in nums: # This is O(n) scan! (這是 O(n) 的掃描！)
        return [i, nums.index(diff)] # Total Time: O(n^2)
```
*   **Why it's wrong:** `in` operator on a list is $O(n)$, making the total complexity $O(n^2)$, same as brute force.
    **為何錯誤：** 在列表上使用 `in` 運算子是 $O(n)$，這使得總複雜度變為 $O(n^2)$，與暴力解相同。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept | Explanation & Pitfall (解釋與陷阱) |
| :--- | :--- |
| **Hash Collisions**<br>(雜湊碰撞) | **Concept:** Two keys map to the same hash.<br>**Pitfall:** Assuming $O(1)$ is guaranteed. In worst cases (e.g., bad hash function), it degrades to $O(n)$.<br>**觀念：** 兩個鍵映射到相同的雜湊值。<br>**陷阱：** 假設 $O(1)$ 是保證的。在最壞情況下（如糟糕的雜湊函數），會退化為 $O(n)$。 |
| **Mutable Keys**<br>(可變鍵) | **Pitfall:** In Python, lists cannot be dict keys because they are mutable. Use `tuple` instead.<br>**陷阱：** 在 Python 中，列表不能作為字典的鍵，因為它們是可變的。請改用 `tuple`。 |
| **Duplicate Handling**<br>(重複處理) | **Pitfall:** Forgetting that a Hash Map overwrites values for the same key. If you need to store multiple indices for the same number, map to a list of indices.<br>**陷阱：** 忘記雜湊表會覆蓋相同鍵的值。如果需要儲存同一個數字的多個索引，應映射到索引列表。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **Clarify Constraints:** "Are the arrays sorted? Can there be duplicates? What is the range of values?"
    **釐清限制：** 「陣列是否已排序？會有重複值嗎？數值的範圍是多少？」
2.  **State the Trade-off:** "I can save space by sorting ($O(1)$ space), or save time by hashing ($O(n)$ space)."
    **說明權衡：** 「我可以透過排序節省空間（$O(1)$ 空間），或透過雜湊節省時間（$O(n)$ 空間）。」
3.  **Dry Run:** Before coding, walk through a small example (e.g., `[2, 7, 11, 15]`, target `9`) to verify logic.
    **模擬執行：** 寫程式碼前，先用一個小範例（如 `[2, 7, 11, 15]`，目標 `9`）來驗證邏輯。

### Whiteboard Strategy (白板策略)
*   **Variable Naming:** Use `num_to_index` instead of `map` or `d`. Clear naming shows seniority.
    **變數命名：** 使用 `num_to_index` 而非 `map` 或 `d`。清晰的命名展現資深度。
*   **Edge Cases:** Explicitly write a comment or check for empty inputs.
    **邊界情況：** 明確寫下註解或檢查空輸入。

### Common Follow-up (常見追問)
*   **Q:** "What if the array is too large to fit in memory?"
    **問：** 「如果陣列大到無法放入記憶體怎麼辦？」
*   **A:** Discuss external sort or loading chunks of data; hashing might not work if the map gets too big.
    **答：** 討論外部排序或分塊載入資料；如果雜湊表變得太大，雜湊法可能無法運作。

---

## 7. Practice Problems (練習題)

### 1. Easy: Contains Duplicate (存在重複元素)
*   **Prompt:** Given an integer array `nums`, return `true` if any value appears at least twice.
    **題目：** 給定一個整數陣列 `nums`，如果任何數值出現至少兩次，回傳 `true`。
*   **Hint:** Compare the length of the list vs. the length of a set.
    **提示：** 比較列表的長度與集合（Set）的長度。
*   **Key Idea:** `len(nums) != len(set(nums))`

### 2. Medium: Group Anagrams (異位構詞分組)
*   **Prompt:** Given an array of strings, group the anagrams together. (e.g., "eat", "tea" -> ["eat", "tea"])
    **題目：** 給定一個字串陣列，將異位構詞分組在一起。（例如："eat", "tea" -> ["eat", "tea"]）
*   **Hint:** What is the common signature of anagrams? (Sorted string or char count tuple).
    **提示：** 異位構詞的共同特徵是什麼？（排序後的字串或字元計數元組）。
*   **Key Idea:** Map `tuple(sorted(s))` -> `list of strings`.

### 3. Hard (for this level): Longest Consecutive Sequence (最長連續序列)
*   **Prompt:** Given an unsorted array, find the length of the longest consecutive elements sequence. Must be $O(n)$.
    **題目：** 給定一個未排序陣列，找出最長連續元素序列的長度。必須是 $O(n)$。
*   **Hint:** Put all numbers in a Set. Iterate through the set, but only start counting if `num - 1` is NOT in the set (start of a sequence).
    **提示：** 將所有數字放入集合。遍歷集合，但只有在 `num - 1` 不在集合中時才開始計數（序列的起點）。
*   **Key Idea:** Efficiently identifying the start of a sequence prevents $O(n^2)$.

---

## 8. Checklists (快速檢核表)

Use this before submitting your code or finishing the interview.
在提交程式碼或結束面試前使用此表。

- [ ] **Empty Input:** Did I handle `[]` or `None`?
    **空輸入：** 我是否處理了 `[]` 或 `None`？
- [ ] **Complexity:** Is my solution definitely $O(n)$ or $O(n \log n)$? Did I accidentally use an $O(n)$ operation inside a loop?
    **複雜度：** 我的解法確定是 $O(n)$ 或 $O(n \log n)$ 嗎？我是否不小心在迴圈內使用了 $O(n)$ 的操作？
- [ ] **Key Errors:** Did I try to use a mutable object (list) as a dictionary key?
    **鍵值錯誤：** 我是否嘗試使用可變物件（列表）作為字典的鍵？
- [ ] **Return Type:** Did I return the *indices* or the *values* as requested?
    **回傳類型：** 我是否依照要求回傳了 *索引* 或 *數值*？

---

## 9. Memory Anchors (記憶錨點)

*   **The Locker Room (Arrays):**
    You have a specific locker number (Index). You walk straight to it.
    **更衣室（陣列）：** 你有一個特定的置物櫃號碼（索引）。你直接走向它。
*   **The Valet Parking (Hash Maps):**
    You give a ticket (Key), and the valet brings your specific car (Value). You don't know where it's parked, but you get it instantly.
    **代客泊車（雜湊表）：** 你給出一張票（鍵），泊車員把你的車（值）開過來。你不知道車停在哪裡，但你立刻就能拿到它。