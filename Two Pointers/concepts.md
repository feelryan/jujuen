# Two Pointers（中階）｜TypeScript

> 聚焦在「雙指針」的可解條件、正確性不變量、以及面試時怎麼把直覺講成可證明的策略。  
> This module focuses on two-pointers solvability conditions, correctness invariants, and how to present intuition as a provable strategy in interviews.

***

## 1) 學習目標（3–5 點）｜Learning Objectives (3–5)

*   你能辨識哪些題目「真的適合」Two Pointers，哪些其實需要 Sliding Window、Hashing 或排序。  
    You can recognize which problems truly fit two pointers and which actually require sliding window, hashing, or sorting.

*   你能用不變量（invariant）說清楚指針移動的正當性，避免「看起來對」但其實漏解。  
    You can justify pointer moves with invariants to avoid “seems right” solutions that miss cases.

*   你能熟練掌握三種常見雙指針模式：左右夾逼、快慢指針、分割/原地覆寫。  
    You can master three common patterns: left-right convergence, fast-slow pointers, and partition/in-place overwrite.

*   你能在 TypeScript 中寫出高品質實作（邊界、溢位/索引安全、可讀性與測試友好）。  
    You can write high-quality TypeScript implementations (edge cases, index safety, readability, testability).

***

## 2) 核心觀念速覽（定義、直覺、複雜度、適用與不適用場景）｜Core Concepts (Definition, Intuition, Complexity, When to Use/Not Use)

### 2.1 Two Pointers 的定義｜Definition of Two Pointers

*   \*\*定義：\*\*用兩個索引在同一個序列上移動，以維持某種不變量或逐步縮小搜尋空間。  
    **Definition:** Use two indices moving over the same sequence to maintain an invariant or shrink the search space.

*   \*\*直覺：\*\*當你能在「移動一個端點」後，保證某些候選答案不再需要考慮時，雙指針就會有效。  
    **Intuition:** Two pointers work when moving an endpoint lets you safely discard a set of candidates.

### 2.2 複雜度｜Complexity

*   \*\*時間複雜度：\*\*多數模板能做到 O(n)，因為每個指針最多走過序列一次。  
    **Time complexity:** Many templates achieve O(n) because each pointer advances at most n steps.

*   \*\*空間複雜度：\*\*通常 O(1)，因為只用常數額外變數。  
    **Space complexity:** Usually O(1) due to constant extra state.

### 2.3 什麼情況適用｜When It Applies

*   \*\*有序或可單調推進：\*\*輸入已排序，或你可以排序後仍保留題意（例如找和、找差、找配對）。  
    **Sorted or monotonic progress:** Input is sorted, or you can sort without breaking semantics (sum/diff/pairing problems).

*   \*\*可證明的淘汰規則：\*\*移動左或右指針能保證某些組合不可能更好。  
    **Provable elimination rule:** Moving left/right can be proven to discard impossible or suboptimal candidates.

*   \*\*原地處理：\*\*移除元素、去重、分割、壓縮、穩定/不穩定覆寫。  
    **In-place processing:** Removal, dedup, partition, compression via overwrite.

### 2.4 什麼情況不適用｜When It Does NOT Apply

*   \*\*條件不單調：\*\*如果移動指針不會讓條件「更接近」或「更遠離」目標，通常不能用左右夾逼。  
    **Non-monotonic conditions:** If pointer moves don’t monotonically approach/retreat from a target, left-right convergence often fails.

*   \*\*需要全局狀態：\*\*例如需要記住大量歷史（頻率、最早位置）時，往往需要 Hash Map 或其他結構。  
    **Needs global history:** When you must remember extensive history (frequencies, earliest indices), hashing or other structures are needed.

***

## 3) 典型題型 / 模式｜Typical Patterns / Templates

### 3.1 左右夾逼（Left-Right Convergence）

*   \*\*特徵：\*\*常見於排序陣列或「最大/最小」目標（例如最大面積、最接近目標）。  
    **Signature:** Common in sorted arrays or max/min objectives (max area, closest target).

*   \*\*不變量：\*\*每次移動一端都不會丟失最優解，因為被淘汰的端點不可能再產生更好結果。  
    **Invariant:** Each move does not lose the optimum because the discarded endpoint cannot produce a better result.

### 3.2 快慢指針（Fast-Slow Pointers）

*   \*\*特徵：\*\*用於去重、移除、壓縮、或偵測循環（linked list / function iteration）。  
    **Signature:** Used for dedup/removal/compression, or cycle detection.

*   \*\*不變量：\*\*慢指針維持「已處理區間」的正確內容，快指針負責掃描。  
    **Invariant:** Slow pointer maintains a correct processed prefix while fast scans ahead.

### 3.3 分割/覆寫（Partition / Overwrite In-place）

*   \*\*特徵：\*\*把元素依規則分到左區/右區（例如移除特定值、奇偶分割）。  
    **Signature:** Partition elements into left/right regions (remove value, parity partition).

*   \*\*注意：\*\*若要求穩定（stable），覆寫方式不同於 swap 分割。  
    **Note:** Stable requirements change the approach versus swap-based partition.

***

## 4) 範例講解｜Worked Examples 

***

## 範例 1：Two Sum II（輸入為排序陣列）｜Two Sum II (Sorted Input)

### 4.1 問題重述｜Restatement

*   \*\*題目：\*\*給定一個已排序的整數陣列 `numbers` 與目標值 `target`，回傳兩個數字的 1-based 索引，使得它們相加等於 `target`。  
    **Problem:** Given a sorted integer array `numbers` and a target, return 1-based indices of two numbers that add up to `target`.

*   \*\*條件：\*\*假設一定恰有一組解，且不能重複使用同一個元素。  
    **Constraint:** Assume exactly one solution exists, and you cannot reuse the same element.

### 4.2 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(n²)）

*   \*\*作法：\*\*枚舉所有 `(i, j)`，檢查 `numbers[i] + numbers[j] == target`。  
    **Approach:** Enumerate all pairs `(i, j)` and check if the sum equals target.

*   \*\*缺點：\*\*在 n 大時會超時。  
    **Downside:** Times out for large n.

#### 優化（對每個 i 二分搜尋，O(n log n)）

*   \*\*作法：\*\*固定 i，對 `target - numbers[i]` 在右側做二分搜尋。  
    **Approach:** Fix i and binary-search for `target - numbers[i]` on the right.

*   \*\*缺點：\*\*仍不是線性，且面試通常期待 O(n) two pointers。  
    **Downside:** Still not linear, and interviews usually expect O(n) two pointers.

#### 最佳（左右夾逼，O(n)）

*   \*\*關鍵單調性：\*\*陣列排序使得當 sum 太大時移動右指針會讓 sum 變小。  
    **Key monotonicity:** Sorted order means if sum is too large, moving right pointer left decreases sum.

*   **策略：**`l=0, r=n-1`，若 `numbers[l]+numbers[r] < target` 則 `l++`，若大於則 `r--`。  
    **Strategy:** Start `l=0, r=n-1`; if sum < target then `l++`, if sum > target then `r--`.

### 4.3 複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n)，每個指針最多走 n 步。  
    **Time:** O(n), each pointer moves at most n steps.

*   \*\*空間：\*\*O(1)。  
    **Space:** O(1).

*   \*\*邊界：\*\*重複值、負數、target 在極值時仍成立。  
    **Edges:** Works with duplicates, negatives, and extreme targets.

### 4.4 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤：\*\*在 sum < target 時卻移動 `r--`，或在 sum > target 時移動 `l++`。  
    **Mistake:** Decreasing `r` when sum < target, or increasing `l` when sum > target.

*   \*\*為何錯：\*\*這會讓 sum 朝錯誤方向移動，導致跳過解或陷入死循環。  
    **Why wrong:** This moves sum in the wrong direction, causing missed solutions or infinite loops.

### 4.5 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * Two Sum II - Input array is sorted
 * 兩數之和 II - 輸入陣列已排序
 *
 * 回傳 1-based indices
 * Return 1-based indices
 */
export function twoSumSorted(numbers: number[], target: number): [number, number] {
  let l = 0;                    // 左指針 / left pointer
  let r = numbers.length - 1;   // 右指針 / right pointer

  while (l < r) {
    const sum = numbers[l] + numbers[r]; // 目前和 / current sum

    if (sum === target) {
      // 轉成 1-based / convert to 1-based
      return [l + 1, r + 1];
    }

    if (sum < target) {
      // 和太小，增加左邊讓和變大
      // Sum too small; move left pointer right to increase sum
      l++;
    } else {
      // 和太大，減少右邊讓和變小
      // Sum too large; move right pointer left to decrease sum
      r--;
    }
  }

  // 題目保證有解，理論上不會到這裡
  // Problem guarantees a solution; should not reach here
  throw new Error("No solution");
}
```

***

## 範例 2：Container With Most Water（盛最多水的容器）｜Container With Most Water

### 4.6 問題重述｜Restatement

*   \*\*題目：\*\*給定非負整數陣列 `height`，第 i 根線高度為 `height[i]`，選兩根線與 x 軸形成容器，求最大可盛水量。  
    **Problem:** Given a non-negative integer array `height`, choose two lines to form a container with the x-axis and return the maximum water area.

*   **面積公式：**`area = min(height[l], height[r]) * (r - l)`。  
    **Area formula:** `area = min(height[l], height[r]) * (r - l)`.

### 4.7 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(n²)）

*   \*\*作法：\*\*枚舉所有 `(l, r)` 計算面積取最大。  
    **Approach:** Enumerate all pairs `(l, r)` and take the max area.

*   \*\*缺點：\*\*n 大會超時。  
    **Downside:** Too slow for large n.

#### 最佳（左右夾逼，O(n)）

*   \*\*關鍵淘汰規則：\*\*每一步移動「較短的那根」才可能提升 `min(height[l], height[r])`。  
    **Key elimination rule:** Move the shorter line, because only that can increase the limiting height.

*   \*\*直覺證明：\*\*若你移動較高的那根，寬度變小且短板不變，面積不可能更大。  
    **Proof intuition:** If you move the taller line, width shrinks while the limiting height stays, so area cannot improve.

### 4.8 複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n)。  
    **Time:** O(n).

*   \*\*空間：\*\*O(1)。  
    **Space:** O(1).

*   \*\*邊界：\*\*高度為 0、全部相同高度、單調遞增/遞減都要正確。  
    **Edges:** Handle zeros, all equal heights, monotonic increasing/decreasing arrays.

### 4.9 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤：\*\*每次都移動較高的那根，理由是「保留較短的不動」。  
    **Mistake:** Always move the taller line, thinking “keep the shorter one.”

*   \*\*為何錯：\*\*短板限制了面積上限，不提升短板只會縮小寬度。  
    **Why wrong:** The shorter line caps the area; without raising the cap, shrinking width can’t help.

### 4.10 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * Container With Most Water
 * 盛最多水的容器
 */
export function maxArea(height: number[]): number {
  let l = 0;                    // 左指針 / left pointer
  let r = height.length - 1;    // 右指針 / right pointer
  let best = 0;                 // 最佳面積 / best area

  while (l < r) {
    const h = Math.min(height[l], height[r]); // 短板高度 / limiting height
    const w = r - l;                          // 寬度 / width
    best = Math.max(best, h * w);             // 更新答案 / update answer

    // 移動短板，才可能提升 limiting height
    // Move the shorter side to possibly increase limiting height
    if (height[l] <= height[r]) {
      l++;
    } else {
      r--;
    }
  }

  return best;
}
```

***

## 5) 常見陷阱與易混淆概念（對比表述）｜Common Pitfalls & Confusions (Contrast)

*   \*\*Two Pointers vs Sliding Window：\*\*Two pointers 是「淘汰候選」，Sliding window 是「維持可調條件的窗口」。  
    **Two pointers vs Sliding Window:** Two pointers “eliminate candidates,” while sliding window “maintains an adjustable validity window.”

*   \*\*排序是否允許：\*\*若題目要求保留原索引或原相對順序，排序可能破壞語義。  
    **Is sorting allowed:** If original indices/order matters, sorting can break semantics.

*   \*\*移動哪一端的依據：\*\*不要靠直覺亂動，必須能說出單調性或淘汰證明。  
    **Which end to move:** Don’t move by gut feeling; articulate monotonicity or an elimination proof.

*   **Off-by-one：**`while (l < r)` 與更新答案的先後，常造成漏算最後一個候選。  
    **Off-by-one:** `while (l < r)` and update ordering often cause missing the last candidate.

***

## 6) 面試實戰建議：闡述口條框架、白板策略、常見 follow-up｜Interview Playbook

### 6.1 口條框架（60–120 秒可用）｜Verbal Framework (60–120s)

*   **先說可解條件：**「因為排序/單調性成立，所以我能移動某端並淘汰一批候選」。  
    **State solvability:** “Because sorting/monotonicity holds, moving an end safely eliminates candidates.”

*   **再說不變量：**「目前最佳答案已考慮所有被掃過的端點組合，且被丟棄的端點不可能產生更好解」。  
    **State invariant:** “Best so far accounts for scanned pairs, and discarded endpoints can’t yield a better solution.”

*   **最後說複雜度：**「每個指針最多走 n 次，所以是 O(n)」。  
    **Close with complexity:** “Each pointer moves at most n times, so O(n).”

### 6.2 白板策略｜Whiteboard Strategy

*   **先寫移動規則，再寫迴圈骨架。**  
    **Write move rules before the loop skeleton.**

*   **用一行反證支持移動端點的正確性。**  
    **Use a one-line contradiction argument to justify pointer moves.**

### 6.3 常見 Follow-up｜Common Follow-ups

*   \*\*若要回傳實際 pair/區間而非數值：\*\*你需要同時保存索引或在找到最佳時記錄端點。  
    **If returning the actual pair/range:** Store indices or record endpoints when updating best.

*   \*\*若輸入未排序但允許排序：\*\*回答排序後做 two pointers 並提及索引回推或存原索引。  
    **If input unsorted but sortable:** Sort then two pointers, and mention index mapping/back-reference.

***

## 7) 練習題（3 題：易/中/難）｜Practice (Easy/Medium/Hard)

### 7.1 易：Valid Palindrome（有效回文）

*   \*\*題目：\*\*忽略非字母數字並忽略大小寫，判斷字串是否為回文。  
    **Problem:** Ignore non-alphanumerics and case, check if the string is a palindrome.

*   \*\*提示：\*\*左右指針向內移動，跳過不需要比較的字元。  
    **Hint:** Use left/right pointers inward, skipping irrelevant characters.

*   \*\*標準解思路：\*\*每一步都做局部比較，若不等立即返回 false。  
    **Solution idea:** Compare locally at each step; mismatch returns false immediately.

### 7.2 中：Remove Duplicates from Sorted Array（移除排序陣列重複）

*   \*\*題目：\*\*原地移除重複並回傳新長度，前 k 個元素為去重結果。  
    **Problem:** Remove duplicates in-place and return new length; first k elements are the dedup result.

*   \*\*提示：\*\*快慢指針，慢指針指向下一個可寫入位置。  
    **Hint:** Fast-slow pointers; slow points to next write position.

*   \*\*標準解思路：\*\*fast 掃描到新值就寫到 slow 並 slow++。  
    **Solution idea:** When fast sees a new value, write it to slow then slow++.

### 7.3 難：3Sum（找三數和為 0）

*   \*\*題目：\*\*找出所有不重複的三元組使其和為 0。  
    **Problem:** Find all unique triplets that sum to 0.

*   \*\*提示：\*\*先排序，固定 i，剩下用左右指針找 two-sum，並小心跳過重複。  
    **Hint:** Sort, fix i, then do two-sum with two pointers; carefully skip duplicates.

*   \*\*標準解思路：\*\*排序後 two pointers 才有單調性可淘汰候選。  
    **Solution idea:** Sorting enables monotonic elimination with two pointers.

***

## 8) 快速檢核表（Checklists）：自我審查/Debug/複雜度確認｜Quick Checklists

### 8.1 正確性自查｜Correctness Self-check

*   我是否能用一句話說出「為什麼移動左/右不會漏掉最優解」。  
    Can I explain in one sentence why moving left/right won’t miss the optimum.

*   我是否在每次移動前或移動後都更新了答案，且順序合理。  
    Did I update the answer at the right time with a sensible ordering.

*   我是否處理了重複值與跳過策略（例如 3Sum 的去重）。  
    Did I handle duplicates and skipping logic (e.g., dedup in 3Sum).

### 8.2 邊界與索引｜Edges & Indices

*   `while (l < r)` 與 `l <= r` 的使用是否符合題意。  
    Did I choose `while (l < r)` vs `l <= r` correctly for the problem.

*   空陣列、單元素、兩元素是否正確處理。  
    Did I handle empty/size-1/size-2 inputs correctly.

### 8.3 複雜度確認｜Complexity Sanity-check

*   每個指針是否只單向前進或後退，確保總步數 O(n)。  
    Does each pointer move monotonically, ensuring total steps O(n).

***

## 9) 記憶錨點與類比（用圖像或比喻）｜Memory Anchors & Analogies

*   \*\*左右夾逼像「兩個人從走廊兩端往中間找人」：\*\*每一步都排除一整段不可能的房間。  
    **Left-right convergence is like two people searching a hallway from both ends:** each step eliminates a whole segment of impossible rooms.

*   \*\*Container 題像「短板效應」：\*\*水位永遠被較短的木板限制，所以只能嘗試換掉短的那一塊。  
    **Container problem is “the shortest stave effect”:** water level is capped by the shorter plank, so you must try replacing the shorter one.

*   \*\*快慢指針像「掃描與寫入分工」：\*\*快指針找下一個可用值，慢指針負責把結果排整齊。  
    **Fast-slow pointers split “scan vs write”:** fast finds the next valid item, slow writes the compacted result.

***
