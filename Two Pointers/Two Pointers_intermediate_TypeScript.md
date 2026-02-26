# Two Pointers Interview Guide (Intermediate)
# 雙指針面試實戰指南（中階）

## 1. Learning Objectives (學習目標)

1.  **Identify Optimization Opportunities**: Recognize when to transform a nested loop solution ($O(N^2)$) into a linear solution ($O(N)$) using pointers.
    **識別優化機會**：辨識何時將巢狀迴圈解法（$O(N^2)$）轉化為使用指針的線性解法（$O(N)$）。

2.  **Master Directional Logic**: Understand when to use "Collision Pointers" (moving towards each other) versus "Parallel Pointers" (moving in the same direction).
    **掌握方向邏輯**：理解何時使用「對撞指針」（相向移動）與「平行指針」（同向移動）。

3.  **Handle Edge Cases & Duplicates**: flawlessly implement boundary checks and duplicate skipping, a common failure point for senior candidates.
    **處理邊界與重複值**：完美實作邊界檢查與跳過重複值的邏輯，這是資深候選人常見的失分點。

4.  **Justify Trade-offs**: Articulate why sorting the input first (Time $O(N \log N)$) is acceptable to enable the Two Pointers strategy.
    **論證權衡**：清楚表達為何先對輸入進行排序（時間 $O(N \log N)$）以啟用雙指針策略是可接受的。

---

## 2. Core Concepts (核心觀念速覽)

### Definition (定義)
Two Pointers involves using two references to iterate through a data structure (usually an array or string) to process elements based on their position or value relative to each other.
雙指針涉及使用兩個引用來遍歷資料結構（通常是陣列或字串），根據它們的相對位置或數值來處理元素。

### Intuition (直覺)
Instead of iterating through all possible pairs/subarrays (Brute Force), we use the sorted property or specific logic to "shrink the search space" intelligently.
我們不遍歷所有可能的配對/子陣列（暴力解），而是利用已排序的特性或特定邏輯來智慧地「縮小搜尋空間」。

### Complexity (複雜度)
-   **Time**: Usually $O(N)$. We touch each element at most a constant number of times.
    **時間**：通常為 $O(N)$。我們最多接觸每個元素常數次。
-   **Space**: $O(1)$ auxiliary space (excluding result storage).
    **空間**：$O(1)$ 輔助空間（不包含結果儲存）。

### When to Use (適用場景)
-   **Sorted Arrays**: Finding pairs/triplets that sum to a target.
    **已排序陣列**：尋找總和為目標值的配對/三元組。
-   **String Manipulation**: Palindrome verification, reversing sections.
    **字串操作**：回文驗證、反轉區段。
-   **Optimization**: Reducing $O(N^2)$ logic to $O(N)$.
    **優化**：將 $O(N^2)$ 的邏輯降低至 $O(N)$。

### When NOT to Use (不適用場景)
-   **Unsorted Data where Index Matters**: If sorting destroys necessary original index information (unless you store indices separately).
    **索引重要的未排序資料**：如果排序會破壞必要的原始索引資訊（除非另外儲存索引）。
-   **Non-Linear Structures**: Trees or Graphs (though Two Pointers exists in Linked Lists for cycle detection).
    **非線性結構**：樹或圖（雖然雙指針存在於鏈結串列中用於檢測環）。

---

## 3. Typical Patterns (典型題型 / 模式)

### A. Collision (Opposite Direction) / 對撞（相向移動）
-   **Setup**: One pointer at `0`, one at `n-1`.
    **設定**：一個指針在 `0`，一個在 `n-1`。
-   **Use Case**: Two Sum (sorted), 3Sum, Container With Most Water, Valid Palindrome.
    **案例**：兩數之和（已排序）、三數之和、盛最多水的容器、驗證回文。

### B. Fast & Slow (Tortoise and Hare) / 快慢指針（龜兔賽跑）
-   **Setup**: Both start at `0`, one moves 1 step, the other moves 2 steps (or condition-based).
    **設定**：兩者皆從 `0` 開始，一個走 1 步，另一個走 2 步（或基於條件移動）。
-   **Use Case**: Cycle detection in Linked List, finding the middle node, removing duplicates in-place.
    **案例**：鏈結串列中的環檢測、尋找中間節點、原地移除重複項。

### C. Merge (Parallel Pointers) / 合併（平行指針）
-   **Setup**: Two pointers iterating through two different arrays (or parts of one).
    **設定**：兩個指針遍歷兩個不同的陣列（或同一個陣列的不同部分）。
-   **Use Case**: Merge Sort, Intersection of two sorted arrays.
    **案例**：合併排序、兩個已排序陣列的交集。

---

## 4. Example Walkthrough (範例講解)

### Problem: 3Sum (三數之和)
**Level**: Medium/Intermediate

#### Problem Statement (問題重述)
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`. The solution set must not contain duplicate triplets.
給定一個整數陣列 `nums`，回傳所有滿足 `i != j`、`i != k` 且 `j != k` 以及 `nums[i] + nums[j] + nums[k] == 0` 的三元組 `[nums[i], nums[j], nums[k]]`。解集中不得包含重複的三元組。

#### Thought Process (思路)

1.  **Brute Force (暴力解)**:
    -   Three nested loops.
    -   三層巢狀迴圈。
    -   Complexity: $O(N^3)$. Too slow for $N=3000$.
    -   複雜度：$O(N^3)$。對於 $N=3000$ 來說太慢。

2.  **Optimization (優化)**:
    -   If we sort the array, we can fix one number (`nums[i]`) and use **Two Pointers** to find the other two numbers that sum to `-nums[i]`.
    -   如果我們對陣列進行排序，我們可以固定一個數字（`nums[i]`），並使用 **雙指針** 尋找另外兩個數字，使其總和為 `-nums[i]`。
    -   This reduces the problem to $N \times O(N) = O(N^2)$.
    -   這將問題簡化為 $N \times O(N) = O(N^2)$。

3.  **Handling Duplicates (處理重複值)**:
    -   Crucial for Senior candidates. We must skip identical values for both the fixed number and the pointers to avoid duplicate triplets.
    -   這對資深候選人至關重要。我們必須跳過固定數字與指針遇到的相同數值，以避免重複的三元組。

#### TypeScript Solution (參考解)

```typescript
function threeSum(nums: number[]): number[][] {
    const result: number[][] = [];
    // 1. Sort the array to enable Two Pointers logic
    // 1. 對陣列進行排序以啟用雙指針邏輯
    nums.sort((a, b) => a - b);

    for (let i = 0; i < nums.length - 2; i++) {
        // Optimization: If the smallest number is > 0, sum can never be 0
        // 優化：如果最小的數字大於 0，總和永遠不可能為 0
        if (nums[i] > 0) break;

        // Skip duplicates for the fixed number 'i'
        // 跳過固定數字 'i' 的重複值
        if (i > 0 && nums[i] === nums[i - 1]) continue;

        let left = i + 1;
        let right = nums.length - 1;

        while (left < right) {
            const sum = nums[i] + nums[left] + nums[right];

            if (sum === 0) {
                result.push([nums[i], nums[left], nums[right]]);

                // Skip duplicates for 'left' pointer
                // 跳過 'left' 指針的重複值
                while (left < right && nums[left] === nums[left + 1]) {
                    left++;
                }
                // Skip duplicates for 'right' pointer
                // 跳過 'right' 指針的重複值
                while (left < right && nums[right] === nums[right - 1]) {
                    right--;
                }

                // Move pointers inward after finding a valid match
                // 找到有效配對後，將指針向內移動
                left++;
                right--;
            } else if (sum < 0) {
                // Sum is too small, need larger number -> move left forward
                // 總和太小，需要更大的數字 -> 左指針前進
                left++;
            } else {
                // Sum is too big, need smaller number -> move right backward
                // 總和太大，需要更小的數字 -> 右指針後退
                right--;
            }
        }
    }

    return result;
}
```

#### Complexity & Edge Cases (複雜度與邊界條件)
-   **Time**: $O(N^2)$ (Sorting is $O(N \log N)$, loops are $O(N^2)$).
    **時間**：$O(N^2)$（排序為 $O(N \log N)$，迴圈為 $O(N^2)$）。
-   **Space**: $O(1)$ or $O(\log N)$ depending on sorting implementation (ignoring output array).
    **空間**：$O(1)$ 或 $O(\log N)$，取決於排序實作（忽略輸出陣列）。
-   **Error Example**: Not skipping duplicates (`nums[i] == nums[i-1]`) results in duplicate triplets in the output.
    **錯誤示範**：未跳過重複值（`nums[i] == nums[i-1]`）會導致輸出中包含重複的三元組。

---

## 5. Common Pitfalls & Confusions (常見陷阱與易混淆概念)

| Concept / Mistake | Explanation (解釋) |
| :--- | :--- |
| **Two Pointers vs Sliding Window** | **Two Pointers**: Usually focuses on finding a pair or specific elements (often collision). <br> **Sliding Window**: Focuses on a continuous subarray range (usually same direction). <br> **雙指針**：通常專注於尋找配對或特定元素（常為對撞）。<br> **滑動視窗**：專注於連續的子陣列範圍（常為同向）。 |
| **While Loop Condition** | `left < right` vs `left <= right`. <br> Use `<` if `left` and `right` cannot be the same element (e.g., 3Sum). <br> Use `<=` if the middle element needs processing (e.g., Binary Search). <br> `left < right` 對比 `left <= right`。<br> 若 `left` 與 `right` 不能是同一元素（如 3Sum），使用 `<`。<br> 若中間元素需要處理（如二分搜尋），使用 `<=`。 |
| **Index Out of Bounds** | When doing `nums[left+1]` inside a loop, ensure `left < right` check exists to prevent overflow. <br> 當在迴圈內執行 `nums[left+1]` 時，確保存在 `left < right` 檢查以防止溢位。 |
| **Premature Optimization** | Trying to use Two Pointers on unsorted arrays without realizing sorting changes indices (bad for "return original indices" problems). <br> 試圖在未排序陣列上使用雙指針，卻未意識到排序會改變索引（不適用於「回傳原始索引」的問題）。 |

---

## 6. Interview Strategy (面試實戰建議)

### Communication Framework (口條框架)
1.  **State the Brute Force**: "The naive approach is nested loops, giving us $O(N^2)$."
    **陳述暴力解**：「樸素的方法是巢狀迴圈，這會給出 $O(N^2)$。」
2.  **Propose Optimization**: "Since we are looking for a pair/triplet, if we sort the array, we can use the Two Pointers technique to reduce complexity."
    **提出優化**：「既然我們在尋找配對/三元組，如果我們對陣列排序，就能使用雙指針技術來降低複雜度。」
3.  **Define Invariants**: "I will maintain a `left` pointer at the start and `right` at the end."
    **定義不變數**：「我會維護一個在開頭的 `left` 指針和一個在結尾的 `right` 指針。」

### Whiteboard Strategy (白板策略)
-   **Draw an Example**: Write `[-1, 0, 1, 2, -1, -4]` and sort it manually on the board first.
    **畫出範例**：寫下 `[-1, 0, 1, 2, -1, -4]` 並先在白板上手動排序。
-   **Trace the Pointers**: Use arrows (`↑`) to show where `L` and `R` are moving.
    **追蹤指針**：使用箭頭（`↑`）顯示 `L` 和 `R` 的移動位置。

### Common Follow-up (常見追問)
-   "What if the array is too large to fit in memory?" (External Sort + Pointers).
    「如果陣列太大無法放入記憶體怎麼辦？」（外部排序 + 指針）。
-   "Can you do this without sorting?" (Hash Map approach, trade Space for Time).
    「你能不排序做這個嗎？」（雜湊表方法，以空間換取時間）。

---

## 7. Practice Problems (練習題)

### 1. Easy: Valid Palindrome II
-   **Task**: Given a string, return true if it can be palindrome after deleting **at most one** character.
    **任務**：給定一個字串，若刪除**至多一個**字元後能成為回文，則回傳 true。
-   **Hint**: Standard collision pointers. If mismatch, try skipping left OR skipping right.
    **提示**：標準對撞指針。若不匹配，嘗試跳過左邊或跳過右邊。

### 2. Medium: Container With Most Water (Classic)
-   **Task**: Find two lines that together with the x-axis form a container, such that the container contains the most water.
    **任務**：找出兩條線，使其與 x 軸共同構成的容器能容納最多的水。
-   **Hint**: Start widest (0, n-1). Move the pointer of the **shorter** line inward (Greedy).
    **提示**：從最寬處開始（0, n-1）。將**較短**那條線的指針向內移動（貪婪演算法）。

### 3. Hard: Trapping Rain Water
-   **Task**: Compute how much water can be trapped after raining.
    **任務**：計算下雨後能攔截多少水。
-   **Hint**: Use `left_max` and `right_max`. Move the pointer with the smaller max value. This optimizes the DP space from $O(N)$ to $O(1)$.
    **提示**：使用 `left_max` 與 `right_max`。移動擁有較小最大值的那個指針。這將 DP 的空間複雜度從 $O(N)$ 優化至 $O(1)$。

---

## 8. Quick Checklists (快速檢核表)

-   [ ] **Sorted?**: Did I sort the input? (Or is it already sorted?)
    **已排序？**：我是否對輸入進行了排序？（或者它已經是排序好的？）
-   [ ] **Termination**: Is the while loop condition correct (`<` vs `<=`)?
    **終止條件**：While 迴圈條件是否正確（`<` 對比 `<=`）？
-   [ ] **Movement**: Do I always move at least one pointer in every iteration (avoid infinite loop)?
    **移動**：我是否在每次迭代中都至少移動了一個指針（避免無窮迴圈）？
-   [ ] **Duplicates**: Did I handle duplicate values if the problem requires unique results?
    **重複值**：如果題目要求唯一結果，我是否處理了重複數值？
-   [ ] **Bounds**: Are `left` and `right` initialized correctly (`0` and `length-1`)?
    **邊界**：`left` 和 `right` 是否正確初始化（`0` 和 `length-1`）？

---

## 9. Memory Anchors (記憶錨點)

-   **The Curtains Analogy (窗簾比喻)**:
    Imagine closing curtains. You grab both ends (left and right) and walk towards the center. This is **Collision Pointers**.
    想像拉上窗簾。你抓住兩端（左和右）並走向中間。這就是**對撞指針**。

-   **The Tortoise and Hare (龜兔賽跑)**:
    One moves fast, one moves slow. If they meet, there is a cycle (loop). This is **Fast & Slow Pointers**.
    一個跑得快，一個跑得慢。如果他們相遇，就代表有環（迴圈）。這就是**快慢指針**。

-   **The Adjustable Wrench (活動扳手)**:
    In "Container With Most Water", you are adjusting the width of the wrench to find the optimal grip. You tighten (move inward) from the side that is "weakest" (shortest height).
    在「盛最多水的容器」中，你在調整扳手的寬度以找到最佳握持。你從「最弱」（高度最短）的一側收緊（向內移動）。