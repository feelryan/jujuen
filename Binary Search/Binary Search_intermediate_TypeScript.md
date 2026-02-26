# Binary Search Masterclass (Intermediate)
# 二分搜尋法大師班（中階）

## 1. Learning Objectives（學習目標）

*   **Master the Generalized Template:** Move beyond simple array search to understanding the invariant of the search space (e.g., `[left, right)` vs `[left, right]`).
    **掌握通用模板：** 超越單純的陣列搜尋，理解搜尋空間的不變性（例如 `[left, right)` 對比 `[left, right]`）。
*   **Conquer "Search on Answer":** Learn to recognize problems where the solution space is monotonic, even if the input array is not sorted.
    **征服「對答案進行二分」：** 學會識別解空間具備單調性的問題，即使輸入陣列並未排序。
*   **Handle Boundary Conditions Flawlessly:** Eliminate "off-by-one" errors and infinite loops by standardizing your loop termination logic.
    **完美處理邊界條件：** 透過標準化迴圈終止邏輯，消除「差一錯誤（off-by-one）」與無窮迴圈。
*   **Adapt to Rotated/Modified Arrays:** Solve variations where the monotonicity is broken or segmented.
    **適應旋轉/變形陣列：** 解決單調性被破壞或分段的變體問題。

---

## 2. Core Concepts Overview（核心觀念速覽）

### Definition & Intuition（定義與直覺）
Binary Search is a divide-and-conquer algorithm that locates a target value within a **sorted sequence** or **monotonic function** by repeatedly dividing the search interval in half.
二分搜尋法是一種分治演算法，透過反覆將搜尋區間減半，在**已排序序列**或**單調函數**中定位目標值。

### Complexity（複雜度）
*   **Time Complexity:** $O(\log N)$ — The search space is reduced by half at each step.
    **時間複雜度：** $O(\log N)$ — 每一步驟都將搜尋空間減半。
*   **Space Complexity:** $O(1)$ for iterative implementation; $O(\log N)$ for recursive (stack space).
    **空間複雜度：** 迭代實作為 $O(1)$；遞迴實作為 $O(\log N)$（堆疊空間）。

### When to Use / Not Use（適用與不適用場景）
*   **Use when:** Input is sorted, or you are searching for a threshold in a solution space (e.g., "minimum capacity to satisfy X").
    **適用：** 輸入已排序，或是在解空間中尋找閾值（例如「滿足 X 的最小容量」）。
*   **Do Not Use when:** The data is unsorted and small (sorting takes $O(N \log N)$ which is slower than $O(N)$ scan), or the access time is not $O(1)$ (e.g., Linked Lists).
    **不適用：** 資料未排序且量少（排序需 $O(N \log N)$ 慢於 $O(N)$ 掃描），或存取時間非 $O(1)$（例如鏈結串列）。

---

## 3. Typical Patterns（典型題型 / 模式）

### Pattern A: Standard Index Search
Searching for a specific value in a sorted array.
在已排序陣列中搜尋特定數值。

### Pattern B: Left/Right Boundary (Lower/Upper Bound)
Finding the first or last occurrence of a target, or the insertion point.
尋找目標值的第一次或最後一次出現位置，或插入點。

### Pattern C: Search on Solution Space (The "Min-Max" Pattern)
Instead of searching an array, we search a range of possible answers (e.g., 1 to $10^9$) and use a `check(mid)` function to verify feasibility.
不搜尋陣列，而是搜尋可能的答案範圍（例如 1 到 $10^9$），並使用 `check(mid)` 函數驗證可行性。

### Pattern D: Rotated Sorted Array
Handling arrays that were sorted but then rotated at some pivot.
處理原本已排序但以某個樞紐點旋轉過的陣列。

---

## 4. Example Walkthroughs（範例講解）

### Example 1: Find First and Last Position of Element in Sorted Array
### 範例一：在排序陣列中尋找元素的開始與結束位置

**Problem Statement:** Given an array of integers `nums` sorted in non-decreasing order, find the starting and ending position of a given `target` value.
**問題重述：** 給定一個非遞減排序的整數陣列 `nums`，找出給定 `target` 值的起始與結束位置。

#### Approach: Brute Force → Optimized（思路：暴力 → 優化）

*   **Brute Force:** Scan linearly. Time: $O(N)$.
    **暴力解：** 線性掃描。時間：$O(N)$。
*   **Optimized:** Run Binary Search twice. Once to find the left boundary (first occurrence), once for the right boundary. Time: $O(\log N)$.
    **優化解：** 執行兩次二分搜尋。一次找左邊界（首次出現），一次找右邊界。時間：$O(\log N)$。

#### TypeScript Reference Solution（TypeScript 參考解）

We use a helper function `findBound` to keep the code DRY.
我們使用輔助函數 `findBound` 來保持程式碼簡潔（DRY）。

```typescript
function searchRange(nums: number[], target: number): number[] {
    // Helper function to find the leftmost or rightmost index
    // 輔助函數：尋找最左或最右的索引
    const findBound = (isFirst: boolean): number => {
        let left = 0;
        let right = nums.length - 1;
        let boundIndex = -1;

        while (left <= right) {
            // Prevent integer overflow (though less common in JS/TS numbers, good practice)
            // 防止整數溢位（雖然在 JS/TS 的 number 型別較少見，但這是好習慣）
            const mid = left + Math.floor((right - left) / 2);

            if (nums[mid] === target) {
                boundIndex = mid; // Record potential answer
                // 記錄潛在答案
                if (isFirst) {
                    right = mid - 1; // Try to find in the left half
                    // 嘗試在左半部尋找
                } else {
                    left = mid + 1;  // Try to find in the right half
                    // 嘗試在右半部尋找
                }
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return boundIndex;
    };

    const first = findBound(true);
    // If target is not found, return [-1, -1] immediately
    // 若找不到目標，立即回傳 [-1, -1]
    if (first === -1) return [-1, -1];
    
    const last = findBound(false);
    
    return [first, last];
}
```

---

### Example 2: Koko Eating Bananas (Search on Answer)
### 範例二：Koko 吃香蕉（對答案進行二分）

**Problem Statement:** Koko loves to eat bananas. There are `n` piles. She has `h` hours. Find the minimum integer `k` (speed) such that she can eat all bananas within `h` hours.
**問題重述：** Koko 愛吃香蕉。有 `n` 堆香蕉。她有 `h` 小時。找出最小整數速度 `k`，使她能在 `h` 小時內吃完所有香蕉。

#### Approach（思路）

*   **Observation:** If Koko can finish with speed `k`, she can definitely finish with speed `k+1`. This monotonicity allows Binary Search.
    **觀察：** 如果 Koko 能以速度 `k` 吃完，她絕對也能以速度 `k+1` 吃完。這種單調性允許我們使用二分搜尋。
*   **Search Space:** The speed `k` ranges from 1 to `max(piles)`.
    **搜尋空間：** 速度 `k` 的範圍從 1 到 `max(piles)`。
*   **Check Function:** Calculate hours needed for a given speed `mid`. If `hours <= h`, try smaller speed (left); otherwise, need more speed (right).
    **檢查函數：** 計算給定速度 `mid` 所需的小時數。若 `hours <= h`，嘗試更小速度（向左）；否則需要更快速度（向右）。

#### TypeScript Reference Solution（TypeScript 參考解）

```typescript
function minEatingSpeed(piles: number[], h: number): number {
    // Determine the search range
    // 決定搜尋範圍
    let left = 1;
    let right = Math.max(...piles);
    let result = right;

    // Check function: Can we finish all piles with speed 'k' in 'h' hours?
    // 檢查函數：能否在 'h' 小時內以速度 'k' 吃完所有堆？
    const canFinish = (k: number): boolean => {
        let hoursNeeded = 0;
        for (const pile of piles) {
            // Equivalent to Math.ceil(pile / k)
            // 等同於 Math.ceil(pile / k)
            hoursNeeded += Math.ceil(pile / k);
        }
        return hoursNeeded <= h;
    };

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);

        if (canFinish(mid)) {
            // If feasible, record it and try to find a smaller valid speed
            // 若可行，記錄下來並嘗試尋找更小的有效速度
            result = mid;
            right = mid - 1;
        } else {
            // If not feasible, we need a faster speed
            // 若不可行，我們需要更快的速度
            left = mid + 1;
        }
    }

    return result;
}
```

---

## 5. Common Pitfalls & Confusions（常見陷阱與易混淆概念）

| Concept | Explanation (解釋) | Common Mistake (常見錯誤) |
| :--- | :--- | :--- |
| **Loop Condition** | `while (left <= right)` vs `while (left < right)` | Using `<` when the search space includes `right`, causing the loop to end before checking the last element. <br> 當搜尋空間包含 `right` 時使用 `<`，導致迴圈在檢查最後一個元素前結束。 |
| **Mid Calculation** | `left + (right - left) / 2` | Using `(left + right) / 2` can cause integer overflow in strictly typed languages (less critical in TS but conceptually wrong). <br> 使用 `(left + right) / 2` 在強型別語言可能導致整數溢位（TS 中較不嚴重但觀念錯誤）。 |
| **Shrinking Range** | `right = mid - 1` vs `right = mid` | If you use `right = mid` in a `while(left <= right)` loop, you will get an infinite loop when `left == mid`. <br> 若在 `while(left <= right)` 迴圈中使用 `right = mid`，當 `left == mid` 時會進入無窮迴圈。 |
| **Floor vs Ceil** | `Math.floor` for division | In Python `//` is floor, but in TS `/` is float division. Forget `Math.floor` leads to non-integer indices. <br> Python 中 `//` 是地板除法，但 TS 中 `/` 是浮點除法。忘記 `Math.floor` 會導致非整數索引。 |

---

## 6. Interview Strategy（面試實戰建議）

### 1. Verbal Framework (口條框架)
*   **Identify Monotonicity:** "Since the array is sorted (or the solution space is monotonic), I can optimize the search from $O(N)$ to $O(\log N)$ using Binary Search."
    **識別單調性：** 「由於陣列已排序（或解空間具單調性），我可以使用二分搜尋法將搜尋從 $O(N)$ 優化至 $O(\log N)$。」
*   **Define Invariant:** "I will define my search space as `[left, right]`, inclusive on both ends."
    **定義不變性：** 「我將定義我的搜尋空間為 `[left, right]`，雙端皆包含。」

### 2. Whiteboard Strategy (白板策略)
*   **Write the Template First:** Quickly write the `while`, `mid`, and `if/else` structure. This buys you thinking time for the specific logic.
    **先寫模板：** 快速寫下 `while`、`mid` 和 `if/else` 結構。這能為你爭取思考具體邏輯的時間。
*   **Trace with 2 Elements:** Always dry run your code with a 2-element array (e.g., `[1, 3]` searching for `0`, `2`, `4`) to verify termination logic.
    **用 2 個元素追蹤：** 務必使用 2 個元素的陣列（例如 `[1, 3]` 搜尋 `0`, `2`, `4`）來演練程式碼，驗證終止邏輯。

### 3. Common Follow-ups (常見追問)
*   "What if the array contains duplicates?" (Affects strict inequality checks).
    「如果陣列包含重複值怎麼辦？」（影響嚴格不等式的檢查）。
*   "What if the array is too large to fit in memory?" (Distributed search or external storage indexing).
    「如果陣列大到無法放入記憶體怎麼辦？」（分散式搜尋或外部儲存索引）。

---

## 7. Practice Problems（練習題）

### 1. Easy: Search Insert Position (LeetCode 35)
*   **Hint:** Standard binary search. If not found, `left` will be the insertion index.
    **提示：** 標準二分搜尋。若未找到，`left` 即為插入索引。
*   **Focus:** Return value when target is missing.
    **重點：** 當目標缺失時的回傳值。

### 2. Medium: Search in Rotated Sorted Array (LeetCode 33)
*   **Hint:** Determine which half is sorted (left or right) by comparing `nums[left]` and `nums[mid]`. Then check if target lies within that sorted half.
    **提示：** 透過比較 `nums[left]` 與 `nums[mid]` 判斷哪一半是有序的（左或右）。接著檢查目標是否位於該有序半部內。
*   **Focus:** Handling the inflection point.
    **重點：** 處理轉折點。

### 3. Hard: Split Array Largest Sum (LeetCode 410)
*   **Hint:** Search on Answer. The range is `[max(nums), sum(nums)]`. Use a greedy approach for the `check` function.
    **提示：** 對答案進行二分。範圍是 `[max(nums), sum(nums)]`。`check` 函數使用貪婪法。
*   **Focus:** Identifying that this is a Binary Search problem despite looking like DP.
    **重點：** 識別出這是二分搜尋問題，儘管它看起來像動態規劃。

---

## 8. Quick Checklists（快速檢核表）

*   [ ] **Sortedness:** Is the input sorted? If not, can I search the *answer*?
    **排序性：** 輸入是否已排序？若否，我能搜尋*答案*嗎？
*   [ ] **Loop Termination:** Did I use `<=`, and do `left` and `right` update as `mid + 1` / `mid - 1`?
    **迴圈終止：** 我是否使用了 `<=`，且 `left` 與 `right` 是否更新為 `mid + 1` / `mid - 1`？
*   [ ] **Integer Division:** Did I use `Math.floor()`?
    **整數除法：** 我是否使用了 `Math.floor()`？
*   [ ] **Corner Cases:** Empty array? Array with 1 element? Target smaller/larger than all elements?
    **邊界情況：** 空陣列？單元素陣列？目標小於/大於所有元素？

---

## 9. Memory Anchors & Analogies（記憶錨點與類比）

### The Dictionary Game (字典遊戲)
Imagine finding a word in a physical dictionary. You open the middle. Is the word before or after? You discard the other half entirely.
想像在實體字典中找一個單字。你翻開中間。單字在前面還是後面？你完全捨棄另一半。

### The True/False Boundary (真/假邊界)
For "Search on Answer" problems, visualize the search space as a series of booleans: `[F, F, F, T, T, T]`.
對於「對答案二分」的問題，將搜尋空間視覺化為一系列布林值：`[F, F, F, T, T, T]`。
*   You are looking for the **first T**.
    你在尋找**第一個 T**。
*   If `check(mid)` is `F`, you must move right (`left = mid + 1`).
    若 `check(mid)` 為 `F`，必須向右移（`left = mid + 1`）。
*   If `check(mid)` is `T`, this is a candidate, but there might be a better one to the left (`right = mid - 1`, save `mid`).
    若 `check(mid)` 為 `T`，這是一個候選，但左邊可能有更好的（`right = mid - 1`，暫存 `mid`）。