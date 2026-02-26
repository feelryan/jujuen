# Module: Arrays & Hashing (Beginner Level)
# 模組：陣列與雜湊（初階）

## 1. Learning Objectives (學習目標)

*   **Master the Space-Time Trade-off:** Understand how to utilize extra space (Hash Maps/Sets) to reduce time complexity from $O(n^2)$ to $O(n)$.
    **掌握空間換取時間的權衡：** 理解如何利用額外空間（雜湊表/集合）將時間複雜度從 $O(n^2)$ 降低至 $O(n)$。
*   **Proficiency with TypeScript Collections:** Gain deep familiarity with TypeScript's `Array`, `Map`, and `Set` APIs, including their internal performance characteristics.
    **精通 TypeScript 集合操作：** 深入熟悉 TypeScript 的 `Array`、`Map` 與 `Set` API，包含其內部的效能特性。
*   **Identify Hashing Patterns:** Recognize problems that require frequency counting, duplicate detection, or rapid lookups.
    **識別雜湊模式：** 辨識需要頻率計數、重複檢測或快速查找的問題。
*   **Handle Edge Cases:** Develop a reflex for checking empty arrays, single elements, and collision scenarios.
    **處理邊界情況：** 培養檢查空陣列、單一元素及雜湊碰撞場景的直覺。

---

## 2. Core Concepts Overview (核心觀念速覽)

### Arrays (陣列)
*   **Definition:** A collection of elements stored in contiguous memory locations.
    **定義：** 存儲在連續記憶體位置的元素集合。
*   **Intuition:** Like a row of numbered mailboxes; if you know the index, you can find the content instantly.
    **直覺：** 就像一排有編號的信箱；如果你知道索引，就能瞬間找到內容。
*   **Complexity (Time):** Access $O(1)$, Search $O(n)$, Insert/Delete $O(n)$ (due to shifting).
    **複雜度（時間）：** 存取 $O(1)$，搜尋 $O(n)$，插入/刪除 $O(n)$（因為需要移動元素）。
*   **Best For:** Random access, simple iteration, managing ordered data.
    **適用於：** 隨機存取、簡單迭代、管理有序數據。

### Hashing (Hash Map / Hash Set) (雜湊)
*   **Definition:** A data structure that maps keys to values using a hash function to compute an index.
    **定義：** 一種資料結構，利用雜湊函數計算索引，將鍵（Key）映射到值（Value）。
*   **Intuition:** Like a library index card system; you look up a book title (Key) to find its shelf location (Value) without walking every aisle.
    **直覺：** 就像圖書館的索引卡系統；你查書名（Key）來找到書架位置（Value），而不用走遍每一條走道。
*   **Complexity (Time):** Average Access/Insert/Delete $O(1)$. Worst case $O(n)$ (collisions).
    **複雜度（時間）：** 平均存取/插入/刪除 $O(1)$。最差情況 $O(n)$（發生碰撞）。
*   **Best For:** Fast lookups, counting frequencies, checking existence.
    **適用於：** 快速查找、頻率計數、檢查存在性。
*   **Not Suitable For:** Finding the closest element, range queries, or sorted data retrieval (unless using a specialized structure like a TreeMap).
    **不適用於：** 尋找最近元素、範圍查詢或排序數據檢索（除非使用如 TreeMap 等特殊結構）。

---

## 3. Typical Patterns (典型題型 / 模式)

For the "Beginner" level in Arrays & Hashing, focus on these three patterns:
針對 Arrays & Hashing 的「初階」程度，請專注於以下三種模式：

1.  **Existence Check / Deduplication (Set):**
    Using a `Set` to check if an element has appeared before.
    **存在性檢查 / 去重（Set）：** 使用 `Set` 來檢查元素是否曾經出現過。
2.  **Frequency Counting (Map):**
    Using a `Map` (or Object) to count how many times each element appears.
    **頻率計數（Map）：** 使用 `Map`（或物件）來計算每個元素出現的次數。
3.  **Complement Search (Map):**
    Storing `target - current_value` to find pairs that sum to a target.
    **補數搜尋（Map）：** 儲存 `target - current_value` 以尋找總和為目標值的配對。

---

## 4. Example Walkthrough (範例講解)

### Problem: Two Sum (兩數之和)
**Problem Statement:**
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
給定一個整數陣列 `nums` 和一個整數 `target`，返回兩個數字的索引，使它們相加等於 `target`。

**Assumption:** Exactly one solution exists, and you may not use the same element twice.
**假設：** 恰好存在一個解，且不可重複使用同一個元素。

---

### Phase 1: Brute Force (暴力解)
**Idea:** Iterate through every pair of numbers to see if they sum to the target.
**思路：** 迭代每一對數字，檢查它們的總和是否為目標值。

*   **Time:** $O(n^2)$ — Nested loops.
*   **Space:** $O(1)$ — No extra structures.

```typescript
function twoSumBrute(nums: number[], target: number): number[] {
    // Iterate through the first number
    // 迭代第一個數字
    for (let i = 0; i < nums.length; i++) {
        // Iterate through the second number, starting from i + 1
        // 迭代第二個數字，從 i + 1 開始
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}
```

---

### Phase 2: Optimal Solution (最佳解 - Hash Map)
**Idea:** Instead of scanning for the second number repeatedly, we store the numbers we've seen so far in a Hash Map (Value -> Index). For each number `x`, we check if `target - x` exists in the map.
**思路：** 與其重複掃描第二個數字，我們將目前見過的數字儲存在雜湊表（數值 -> 索引）中。對於每個數字 `x`，我們檢查 `target - x` 是否存在於表中。

*   **Time:** $O(n)$ — We traverse the list containing $n$ elements only once.
*   **Space:** $O(n)$ — The map stores up to $n$ elements.

**TypeScript Solution:**

```typescript
function twoSum(nums: number[], target: number): number[] {
    // Create a Map to store the number and its index: { number: index }
    // 建立一個 Map 來儲存數字及其索引：{ 數值: 索引 }
    const prevMap = new Map<number, number>();

    for (let i = 0; i < nums.length; i++) {
        const currentNum = nums[i];
        const diff = target - currentNum;

        // Check if the difference (complement) is already in the map
        // 檢查差值（補數）是否已經在 map 中
        if (prevMap.has(diff)) {
            // If found, return the index of the diff and the current index
            // 如果找到，返回差值的索引與當前索引
            return [prevMap.get(diff)!, i];
        }

        // Store the current number and its index for future lookups
        // 儲存當前數字及其索引以供未來查找
        prevMap.set(currentNum, i);
    }

    // Should not reach here based on problem constraints
    // 根據題目限制，程式不應執行到此處
    return [];
}
```

**Why this is better:**
For a Senior Engineer, the trade-off is clear: we sacrifice memory ($O(n)$ space) to gain significant speed ($O(n)$ time). In real-world web services, CPU time (latency) is often more expensive than RAM.
**為何這比較好：**
對於資深工程師來說，這個權衡很明顯：我們犧牲記憶體（$O(n)$ 空間）來換取顯著的速度提升（$O(n)$ 時間）。在現實世界的 Web 服務中，CPU 時間（延遲）通常比 RAM 更昂貴。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept (概念) | Pitfall / Confusion (陷阱 / 混淆點) | Clarification (釐清) |
| :--- | :--- | :--- |
| **Map vs Object** | Using JS `Object` `{}` for hashing keys. <br> 使用 JS `Object` `{}` 作為雜湊鍵。 | `Object` keys are always strings (or Symbols). `Map` allows any type of key and performs better in frequent add/remove scenarios. <br> `Object` 的鍵永遠是字串（或 Symbol）。`Map` 允許任何類型的鍵，且在頻繁增刪的場景下效能較佳。 |
| **Array.includes()** | Using `.includes()` inside a loop. <br> 在迴圈中使用 `.includes()`。 | `.includes()` is $O(n)$. Inside a loop, it makes the total complexity $O(n^2)$. Use a `Set` for $O(1)$ lookups. <br> `.includes()` 是 $O(n)$。在迴圈中使用會使總複雜度變為 $O(n^2)$。應使用 `Set` 進行 $O(1)$ 查找。 |
| **Collision Handling** | Assuming Hash Map is always $O(1)$. <br> 假設雜湊表永遠是 $O(1)$。 | In worst-case (many collisions), it degrades to $O(n)$. Although rare in interviews, acknowledge this possibility. <br> 在最差情況（大量碰撞）下，會退化為 $O(n)$。雖然面試中少見，但應承認此可能性。 |

---

## 6. Interview Strategy (面試實戰建議)

**1. Clarify Constraints (釐清限制)**
*   "Are the numbers sorted?" (If yes, Two Pointers might be better than Hashing).
    「數字有排序嗎？」（若是，雙指針可能比雜湊更好）。
*   "Can the array contain duplicates?"
    「陣列可能包含重複值嗎？」
*   "What is the range of the numbers?" (If small, an array might replace a Map).
    「數字的範圍是多少？」（若範圍小，陣列可能取代 Map）。

**2. Whiteboard Strategy (白板策略)**
*   Draw the array.
    畫出陣列。
*   Write the target value.
    寫下目標值。
*   Simulate the iteration: "Index 0 is 2, I need 7. Is 7 in my map? No. Add {2:0}..."
    模擬迭代：「索引 0 是 2，我需要 7。7 在我的 map 裡嗎？沒有。加入 {2:0}...」

**3. Follow-up Preparation (追問準備)**
*   **Q:** What if the array is too large to fit in memory?
    **問：** 如果陣列大到無法放入記憶體怎麼辦？
*   **A:** Discuss external sort or processing in chunks (sharding based on hash).
    **答：** 討論外部排序或分塊處理（基於雜湊的分片）。

---

## 7. Practice Problems (練習題)

### Level: Easy (簡單)
**Problem:** **Contains Duplicate** (LeetCode 217)
**Hint:** Use a `Set` to track seen elements. If `set.has(current)`, return true.
**提示：** 使用 `Set` 追蹤看過的元素。如果 `set.has(current)`，返回 true。

### Level: Medium (中等) - *Recommended for this module*
**Problem:** **Group Anagrams** (LeetCode 49)
**Problem:** Given an array of strings, group the anagrams together.
**題目：** 給定一個字串陣列，將變位詞（Anagrams）分組。
**Hint:** Sort each string to use as a key, OR use a character count array (e.g., "1#0#2...") as a key in a Hash Map.
**提示：** 將每個字串排序作為鍵，或使用字元計數陣列（如 "1#0#2..."）作為雜湊表中的鍵。

### Level: Hard (困難) - *Stretch Goal*
**Problem:** **Longest Consecutive Sequence** (LeetCode 128)
**Hint:** Put all numbers in a `Set`. Iterate through the set. If `num - 1` does not exist, `num` is the start of a sequence. Count upwards.
**提示：** 將所有數字放入 `Set`。迭代集合。如果 `num - 1` 不存在，則 `num` 是序列的起點。向上計數。

---

## 8. Quick Checklists (快速檢核表)

Use this before submitting your code or saying "I'm done".
在提交程式碼或說「我完成了」之前，請使用此表。

*   [ ] **Empty Input:** Did I handle `[]` or `null`?
    **空輸入：** 我是否處理了 `[]` 或 `null`？
*   [ ] **Uniqueness:** Did I confuse values with indices in my Map?
    **唯一性：** 我是否在 Map 中混淆了數值與索引？
*   [ ] **Return Type:** Does the function return indices, booleans, or the values themselves?
    **返回類型：** 函式是返回索引、布林值，還是數值本身？
*   [ ] **Complexity:** Is my solution strictly $O(n)$ or did I accidentally put a loop inside a loop (e.g., `indexOf` inside `for`)?
    **複雜度：** 我的解法是嚴格的 $O(n)$ 嗎？還是我不小心在迴圈內放了另一個迴圈（例如 `for` 裡面用 `indexOf`）？

---

## 9. Memory Anchors (記憶錨點)

*   **The "Hotel Front Desk" (Hash Map):**
    Imagine a hotel front desk. You give them a room number (Key), and they give you the keycard (Value). You don't knock on every door to find your room.
    **「飯店櫃台」（雜湊表）：**
    想像飯店櫃台。你給他們房號（Key），他們給你房卡（Value）。你不需要敲每一扇門來找房間。

*   **The "Security Checkpoint" (Set):**
    A security guard with a list of banned IDs. He only cares **if** you are on the list (True/False), not where you are sitting or how many times you entered.
    **「安檢站」（集合）：**
    拿著禁止名單的保全。他只在乎你 **是否** 在名單上（True/False），不在乎你坐在哪裡或進入了幾次。