# Two Pointers（Advanced）｜TypeScript

> 這份進階版會強調「可解條件」與「可證明的淘汰規則」，並涵蓋去重、計數、與多層指針（k-sum / partition / two-pointer DP-like）的面試常見變形。  
> This advanced version emphasizes “solvability conditions” and “provable elimination rules,” and covers common interview variants: dedup, counting, and multi-layer pointers (k-sum / partition / two-pointer DP-like).

***

## 1) 學習目標（3–5 點）｜Learning Objectives (3–5)

*   你能在 1–2 分鐘內判斷題目是否具備「單調性」或「可淘汰性」，從而選擇 Two Pointers、Sliding Window 或 Hashing。  
    You can decide within 1–2 minutes whether a problem has “monotonicity” or “eliminability,” and choose two pointers vs sliding window vs hashing.

*   你能用不變量（invariant）與反證法（proof by contradiction）解釋「為什麼要移動哪一端」。  
    You can justify “which end to move and why” using invariants and proof by contradiction.

*   你能熟練處理進階去重（dedup）與計數（counting）型 two pointers，避免漏解與重複解。  
    You can handle advanced dedup and counting variants without missing solutions or producing duplicates.

*   你能寫出低 bug 的 TypeScript 實作，包含邊界、重複值策略、以及 O(1) 空間的原地操作。  
    You can implement low-bug TypeScript solutions with edge handling, duplicate strategies, and O(1) extra space in-place operations.

*   你能回答常見 follow-up：回傳索引/內容、列出所有解、改成最小/最大、或處理大數與溢位語義。  
    You can answer common follow-ups: return indices/content, list all solutions, switch to min/max, or handle big-number/overflow semantics.

***

## 2) 核心觀念速覽（定義、直覺、複雜度、適用與不適用場景）｜Core Concepts (Definition, Intuition, Complexity, When to Use/Not Use)

### 2.1 Two Pointers 的本質：用「可淘汰性」換「線性掃描」

Two pointers’ essence: trade “eliminability” for “linear scanning.”

*   \*\*定義：\*\*同時維護兩個（或多個）位置指標，使每次移動都能排除一批不可能或不再需要的候選。  
    **Definition:** Maintain two (or more) positional indices where each move discards a class of impossible or unnecessary candidates.

*   \*\*直覺：\*\*只要你能保證「移動一步」後，某些組合永遠不可能更好或不可能成解，你就能做到 O(n)。  
    **Intuition:** If a one-step move can guarantee certain combinations can never improve or never become solutions, you can reach O(n).

*   \*\*時間複雜度：\*\*典型是 O(n) 或 O(n²)（例如 3Sum：外層 O(n) 固定一點，內層 two pointers O(n)）。  
    **Time complexity:** Typically O(n) or O(n²) (e.g., 3Sum: O(n) anchors × O(n) two pointers).

*   \*\*空間複雜度：\*\*通常 O(1) 額外空間（不含輸出）。  
    **Space complexity:** Usually O(1) extra space (excluding output).

### 2.2 何時成立：單調性（Monotonicity）與等價類（Equivalence class）

When it works: monotonicity and equivalence classes.

*   \*\*單調性：\*\*排序後，指針移動會讓目標函數（sum/diff/width）可預期地變大或變小。  
    **Monotonicity:** After sorting, pointer moves change the objective (sum/diff/width) predictably up or down.

*   \*\*等價類：\*\*去重題需要你把「相同值」視為同一類，並制定跳過策略以避免重複答案。  
    **Equivalence class:** Dedup problems treat identical values as the same class and require skip rules to avoid duplicate answers.

### 2.3 常見不適用：非單調 + 需要全局記憶

Common non-fit: non-monotonic + needs global memory.

*   \*\*非單調條件：\*\*例如含負數且想用「固定窗口」控制 sum，通常不是 two pointers 而是 prefix/hash 或其他結構。  
    **Non-monotonic condition:** With negatives, trying to control sum via a fixed window is usually not two pointers but prefix/hash or other structures.

*   \*\*全局最早/最晚資訊：\*\*例如要記錄「最早出現位置」或「頻率」，常需要 Map。  
    **Global earliest/latest info:** If you must track earliest occurrences or frequencies, a Map is often required.

***

## 3) 典型題型 / 模式（進階）｜Typical Patterns / Templates (Advanced)

### 3.1 Sorted + Converging（排序後左右夾逼）

*   \*\*用途：\*\*Two Sum II、3Sum/4Sum 的內層、Closest Sum。  
    **Use cases:** Two Sum II, inner loop of 3Sum/4Sum, closest-sum variants.

*   \*\*核心：\*\*sum 與指針的關係單調，因此可以用 `< target` 移左或 `> target` 移右來淘汰。  
    **Core:** Sum changes monotonically with pointer movement, enabling elimination rules.

### 3.2 K-Sum with Dedup（k-sum + 去重）

*   \*\*用途：\*\*3Sum / 4Sum / kSum（常見 follow-up）。  
    **Use cases:** 3Sum / 4Sum / generalized kSum (common follow-up).

*   \*\*關鍵：\*\*去重必須在「固定 anchor」與「內層 l/r」兩個層級都做。  
    **Key:** Dedup must happen at both the anchor level and the inner l/r level.

### 3.3 Two-Pointer “State Compression”（雙指針狀態壓縮）

*   \*\*用途：\*\*Trapping Rain Water（左右最大值狀態）、Partition（0/1/2 分割）、In-place remove。  
    **Use cases:** Trapping Rain Water (left/right maxima state), partition (0/1/2), in-place removal.

*   \*\*關鍵：\*\*雖然是 two pointers，但其實是在維護兩個方向的「足夠狀態」以做局部決策。  
    **Key:** It’s still two pointers, but you maintain sufficient directional state for local decisions.

### 3.4 Fast-Slow with Invariants（快慢指針不變量）

*   \*\*用途：\*\*Remove duplicates / remove element / stable compaction、Linked list cycle（如有）。  
    **Use cases:** Remove duplicates/element/stable compaction, linked-list cycle (if applicable).

*   \*\*不變量：\*\*slow 左側區域永遠是「已完成且正確的輸出形狀」。  
    **Invariant:** Region left of slow is always the correct finalized output shape.

***

## 4) 範例講解｜Worked Examples

***

# 範例 1：3Sum（找出所有不重複三元組使和為 0）｜3Sum (All unique triplets summing to 0)

## 4.1 問題重述（雙語）｜Restatement (Bilingual)

*   \*\*題目：\*\*給定整數陣列 `nums`，找出所有不重複的三元組 `[a,b,c]` 使 `a+b+c=0`。  
    **Problem:** Given an integer array `nums`, find all unique triplets `[a,b,c]` such that `a+b+c=0`.

*   \*\*要求：\*\*答案中不得包含重複三元組，三元組內元素的順序不重要。  
    **Requirement:** The result must not contain duplicate triplets, and order within a triplet does not matter.

## 4.2 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

### 暴力（O(n³)）

*   \*\*作法：\*\*三層迴圈枚舉 `(i,j,k)` 並檢查是否為 0，然後用 Set 去重。  
    **Approach:** Triple loop over `(i,j,k)` and check sum, then dedup via a Set.

*   \*\*問題：\*\*O(n³) 太慢，且去重成本高且容易寫出碰撞/序列化 bug。  
    **Issue:** O(n³) is too slow, and dedup adds cost and bug risk (collisions/serialization).

### 優化（排序 + 固定 i + two pointers，O(n²)）

*   \*\*關鍵：\*\*排序後，對固定的 `i`，內層是標準 two-sum in sorted array。  
    **Key:** After sorting, for a fixed `i`, the inner loop becomes classic two-sum on a sorted array.

*   \*\*策略：\*\*固定 `i`，令 `l=i+1, r=n-1`，比較 `nums[i]+nums[l]+nums[r]` 與 0。  
    **Strategy:** Fix `i`, set `l=i+1, r=n-1`, compare `nums[i]+nums[l]+nums[r]` with 0.

*   \*\*去重：\*\*若 `nums[i]` 與前一個相同則跳過，找到解後也要跳過 `l` 與 `r` 的重複值。  
    **Dedup:** Skip `i` if `nums[i]` equals previous; after finding a solution, also skip duplicate values at `l` and `r`.

## 4.3 複雜度與邊界條件｜Complexities & Edge Cases

*   \*\*時間：\*\*排序 O(n log n) + 外層 O(n) × 內層 O(n) = O(n²)。  
    **Time:** Sort O(n log n) + O(n) anchors × O(n) inner scan = O(n²).

*   \*\*空間：\*\*O(1) 額外空間（不含輸出），排序視實作可能有額外空間。  
    **Space:** O(1) extra (excluding output), sorting may use additional space depending on implementation.

*   \*\*邊界：\*\*全正或全負可早停，並且要正確處理大量重複元素（如全 0）。  
    **Edges:** Can early-stop for all-positive/all-negative, and must handle heavy duplicates (e.g., all zeros).

## 4.4 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤 1：\*\*只跳過 `i` 的重複值，但找到解後不跳過 `l/r` 的重複值。  
    **Mistake 1:** Dedup only at `i` but not at `l/r` after a match.

*   \*\*為何錯：\*\*你會產生重複三元組，因為同一個 `i` 會對應多個相同的 `l/r` 值組合。  
    **Why wrong:** You’ll emit duplicate triplets because the same `i` pairs with repeated `l/r` values.

*   \*\*錯誤 2：\*\*在 `sum < 0` 時移動 `r--` 或在 `sum > 0` 時移動 `l++`。  
    **Mistake 2:** Moving `r--` when `sum < 0`, or moving `l++` when `sum > 0`.

*   \*\*為何錯：\*\*排序下 sum 與指針移動具單調性，反向移動會把 sum 推離目標並漏掉解。  
    **Why wrong:** In a sorted array, sum changes monotonically; wrong-direction moves push sum away and miss solutions.

## 4.5 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * 3Sum：找出所有不重複的三元組使和為 0
 * 3Sum: find all unique triplets that sum to 0
 */
export function threeSum(nums: number[]): number[][] {
  // 先排序以啟用 two pointers 的單調性
  // Sort first to enable two-pointer monotonicity
  nums.sort((a, b) => a - b);

  const res: number[][] = [];
  const n = nums.length;

  for (let i = 0; i < n; i++) {
    // 若 nums[i] > 0，因為排序，後面都 >= nums[i]，三數和不可能為 0
    // If nums[i] > 0, then all later numbers are >= nums[i], sum cannot be 0
    if (nums[i] > 0) break;

    // 去重：同一個 anchor 值只處理一次
    // Dedup: process each anchor value once
    if (i > 0 && nums[i] === nums[i - 1]) continue;

    let l = i + 1;      // 左指針 / left pointer
    let r = n - 1;      // 右指針 / right pointer

    while (l < r) {
      const sum = nums[i] + nums[l] + nums[r]; // 目前三數和 / current triplet sum

      if (sum === 0) {
        // 找到一組解
        // Found a solution
        res.push([nums[i], nums[l], nums[r]]);

        // 找到解後，跳過 l 的重複值
        // After a match, skip duplicates on l
        const leftVal = nums[l];
        while (l < r && nums[l] === leftVal) l++;

        // 找到解後，跳過 r 的重複值
        // After a match, skip duplicates on r
        const rightVal = nums[r];
        while (l < r && nums[r] === rightVal) r--;

      } else if (sum < 0) {
        // 和太小，需要變大，移動 l++
        // Sum too small; increase it by moving l++
        l++;
      } else {
        // 和太大，需要變小，移動 r--
        // Sum too large; decrease it by moving r--
        r--;
      }
    }
  }

  return res;
}
```

***

# 範例 2：Trapping Rain Water（接雨水）｜Trapping Rain Water

> 這題表面是 two pointers，但本質是「雙向狀態壓縮」，非常常見於進階面試。  
> This looks like two pointers, but it’s really “two-sided state compression,” and it’s a frequent advanced interview question.

## 4.6 問題重述（雙語）｜Restatement (Bilingual)

*   \*\*題目：\*\*給定高度陣列 `height`，每格寬度為 1，計算下雨後能接到多少水。  
    **Problem:** Given an elevation map `height` with unit width bars, compute how much water it can trap after raining.

*   \*\*關鍵：\*\*每個位置能接水量取決於左側最高與右側最高的較小值。  
    **Key:** Water at position depends on the minimum of left-max and right-max.

## 4.7 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

### 暴力（O(n²)）

*   \*\*作法：\*\*對每個位置 i，掃描左側最大值與右側最大值，再累加 `min(lmax,rmax)-height[i]`。  
    **Approach:** For each i, scan left max and right max, then add `min(lmax,rmax)-height[i]`.

*   \*\*問題：\*\*每個 i 都掃左右會變成 O(n²)。  
    **Issue:** Scanning both sides for each i is O(n²).

### 優化（DP 預處理，O(n) 空間）

*   \*\*作法：\*\*先算 `leftMax[i]` 與 `rightMax[i]`，再一趟累加。  
    **Approach:** Precompute `leftMax[i]` and `rightMax[i]`, then accumulate in one pass.

*   \*\*缺點：\*\*需要 O(n) 額外空間，面試常追問能否 O(1)。  
    **Downside:** Uses O(n) extra space, and interviews often ask for O(1).

### 最佳（Two pointers + two maxima，O(1) 空間）

*   \*\*核心不變量：\*\*若 `leftMax <= rightMax`，則左邊位置的接水量只取決於 `leftMax`，與右邊更遠處無關。  
    **Core invariant:** If `leftMax <= rightMax`, water on the left side is determined solely by `leftMax`, independent of farther right.

*   \*\*策略：\*\*維護 `l,r,leftMax,rightMax`，每次處理較小的一側並向內移動。  
    **Strategy:** Maintain `l,r,leftMax,rightMax`, process the smaller side each step and move inward.

## 4.8 複雜度與邊界條件｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n)，每個指針走一次。  
    **Time:** O(n), each pointer moves once.

*   \*\*空間：\*\*O(1) 額外空間。  
    **Space:** O(1) extra space.

*   \*\*邊界：\*\*陣列長度 < 3 時必為 0，並且要正確處理平台（flat）與多個凹槽。  
    **Edges:** Length < 3 yields 0, and handle flat plateaus and multiple basins.

## 4.9 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤：\*\*每一步只比較 `height[l]` 與 `height[r]` 而不維護 `leftMax/rightMax`。  
    **Mistake:** Comparing only `height[l]` vs `height[r]` without tracking `leftMax/rightMax`.

*   \*\*為何錯：\*\*接水取決於「歷史最高邊界」，只看當前高度會在平台與內凹時算錯。  
    **Why wrong:** Trapped water depends on historical maxima; current heights alone fail on plateaus and basins.

## 4.10 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * Trapping Rain Water
 * 接雨水
 *
 * O(n) time, O(1) extra space
 * 時間 O(n)，額外空間 O(1)
 */
export function trap(height: number[]): number {
  const n = height.length;
  if (n < 3) return 0; // 少於 3 根柱子無法形成容器 / fewer than 3 bars cannot trap

  let l = 0;           // 左指針 / left pointer
  let r = n - 1;       // 右指針 / right pointer
  let leftMax = 0;     // 左側最高 / max to the left
  let rightMax = 0;    // 右側最高 / max to the right
  let water = 0;       // 總接水量 / total water

  while (l < r) {
    // 維護左右最高
    // Maintain side maxima
    leftMax = Math.max(leftMax, height[l]);
    rightMax = Math.max(rightMax, height[r]);

    // 若左側邊界較小，則左側的水量由 leftMax 決定
    // If left boundary is smaller, left side water is determined by leftMax
    if (leftMax <= rightMax) {
      water += leftMax - height[l]; // 此處一定非負 / non-negative here
      l++;
    } else {
      // 若右側邊界較小，則右側的水量由 rightMax 決定
      // If right boundary is smaller, right side water is determined by rightMax
      water += rightMax - height[r]; // 此處一定非負 / non-negative here
      r--;
    }
  }

  return water;
}
```

***

## 5) 常見陷阱與易混淆概念（對比表述）｜Common Pitfalls & Confusions (Contrast)

*   \*\*「排序後 two pointers」vs「不排序 two pointers」：\*\*大多數和/差配對需要排序才能保證單調性。  
    **“Sorted two pointers” vs “unsorted two pointers”:** Most sum/diff pairing requires sorting to guarantee monotonicity.

*   \*\*「去重位置」：\*\*3Sum 必須同時在 `i` 層與 `l/r` 層去重，少一層就會重複。  
    **“Where to dedup”:** 3Sum must dedup at both the `i` level and `l/r` level; missing either causes duplicates.

*   \*\*「移動端點」的理由：\*\*不應說「感覺要移動短的」，而要說「移動哪端能淘汰不可能更優的一批候選」。  
    **Reasoning for moves:** Don’t say “it feels like moving the shorter,” say “moving this side eliminates a provably non-better set.”

*   \*\*「two pointers」vs「sliding window」：\*\*sliding window 的可行性需要條件對窗口擴縮具可維護性（通常是單調）。  
    **Two pointers vs sliding window:** Sliding window requires a maintainable condition under expand/shrink (often monotonic).

*   \*\*TS 細節：\*\*排序要用 comparator，否則會做字典序排序而出錯。  
    **TS detail:** You must provide a numeric comparator for sort, otherwise lexicographic sort breaks correctness.

***

## 6) 面試實戰建議：闡述口條框架、白板策略、常見 follow-up｜Interview Playbook

### 6.1 口條框架（Advanced 版本）｜Verbal Framework (Advanced)

*   **(1) 宣告可解條件：**「我先排序，讓 sum 隨指針移動具單調性，因此能淘汰候選」。  
    **(1) State solvability:** “I sort first so sums change monotonically with pointer moves, enabling elimination.”

*   **(2) 寫出不變量：**「在固定 i 下，l 向右只會增大 sum，r 向左只會減小 sum」。  
    **(2) State invariant:** “With fixed i, moving l right increases sum, moving r left decreases sum.”

*   **(3) 去重規則：**「相同值視為同一等價類，固定點與內層都跳過重複」。  
    **(3) Dedup rule:** “Treat equal values as one equivalence class; skip duplicates at anchor and inner pointers.”

*   **(4) 複雜度：**「排序 O(n log n)，主迴圈 O(n²)，空間 O(1)（不含輸出）」。  
    **(4) Complexity:** “Sort O(n log n), main loop O(n²), space O(1) excluding output.”

### 6.2 白板策略（少 bug 的寫法）｜Whiteboard Strategy (Low-bug)

*   **先寫去重範本：**`if (i>0 && a[i]==a[i-1]) continue;` 以及 match 後跳過 `l/r` 重複。  
    **Write dedup templates first:** Anchor skip and post-match l/r skipping.

*   \*\*先更新答案再移動：\*\*像 trap 題先更新 `leftMax/rightMax`，再基於不變量計算水量。  
    **Update state before moving:** For trap, update maxima before computing and moving.

### 6.3 常見 Follow-up（加分回答）｜Common Follow-ups (Bonus)

*   \*\*Follow-up：\*\*3Sum 若改成 target（非 0）？  
    **Follow-up:** What if 3Sum targets an arbitrary value, not 0?
    *   \*\*答法：\*\*把比較改成與 target，其他不變。  
        **Answer:** Compare against target; everything else stays the same.

*   \*\*Follow-up：\*\*要回傳索引而不是值？  
    **Follow-up:** Return indices instead of values?
    *   \*\*答法：\*\*排序時保留原索引（pair `(value, index)`），並注意去重語義會變複雜。  
        **Answer:** Sort pairs `(value, index)` and note dedup semantics become trickier.

*   \*\*Follow-up：\*\*Trapping Rain Water 要輸出每格水量？  
    **Follow-up:** Output per-position water amounts?
    *   \*\*答法：\*\*需額外陣列記錄或改用 DP 預處理，空間變 O(n)。  
        **Answer:** Use an extra array or DP precompute, raising space to O(n).

***

## 7) 練習題（3 題：易/中/難）｜Practice (Easy/Medium/Hard)

### 7.1 易：Valid Palindrome II（最多刪一個字元成回文）

*   \*\*題目：\*\*判斷字串是否能透過刪除最多一個字元變成回文。  
    **Problem:** Check if a string can become a palindrome by deleting at most one character.

*   \*\*提示：\*\*遇到不相等時，嘗試跳過左或跳過右並各做一次回文檢查。  
    **Hint:** On mismatch, try skipping left or skipping right once and validate palindrome.

*   \*\*標準解思路：\*\*two pointers + 一次分支檢查，總 O(n)。  
    **Solution idea:** Two pointers with at most one branch check, total O(n).

### 7.2 中：Remove Duplicates from Sorted Array II（每個元素最多保留兩次）

*   \*\*題目：\*\*排序陣列原地去重，但允許每個值最多出現兩次。  
    **Problem:** In-place dedup on a sorted array, allowing each value to appear at most twice.

*   \*\*提示：\*\*快慢指針，slow 指向下一個可寫位置，並檢查 `nums[slow-2]`。  
    **Hint:** Fast-slow pointers; slow is next write slot; compare against `nums[slow-2]`.

*   \*\*標準解思路：\*\*若當前值不等於 `nums[slow-2]` 就寫入。  
    **Solution idea:** Write current value if it differs from `nums[slow-2]`.

### 7.3 難：4Sum（去重 + two pointers 內核）

*   \*\*題目：\*\*找出所有不重複四元組使和為 target。  
    **Problem:** Find all unique quadruplets summing to target.

*   \*\*提示：\*\*排序後固定兩層 anchor，再用 two pointers 做內層 two-sum，並在每層做 dedup。  
    **Hint:** Sort, fix two anchors, then two pointers for inner two-sum, dedup at each level.

*   \*\*標準解思路：\*\*時間 O(n³)，但能靠剪枝（最小/最大可能和）提早跳出。  
    **Solution idea:** O(n³) with pruning via min/max possible sums.

***

## 8) 快速檢核表（Checklists）：自我審查/Debug/複雜度確認｜Quick Checklists

### 8.1 Two Pointers 可行性檢核｜Feasibility Checklist

*   我是否有單調性或可證明的淘汰規則。  
    Do I have monotonicity or a provable elimination rule?

*   我是否需要全局頻率或最早位置資訊而其實應用 Map。  
    Do I actually need global frequency/earliest info requiring a Map?

### 8.2 去重檢核（k-sum 必看）｜Dedup Checklist (k-sum must)

*   anchor 層是否跳過 `nums[i]==nums[i-1]`。  
    Did I skip duplicate anchors via `nums[i]==nums[i-1]`?

*   match 後是否分別跳過 l 重複與 r 重複。  
    After a match, did I skip duplicates for both l and r?

*   去重是否會造成漏解（例如跳過太早或跳過不該跳的值）。  
    Does my dedup accidentally skip valid solutions (skipping too aggressively)?

### 8.3 索引與狀態更新檢核｜Index & State Update Checklist

*   迴圈條件是否正確使用 `l < r`，並避免死循環。  
    Did I use `l < r` correctly and avoid infinite loops?

*   狀態是否先更新再計算（如 trap 的 leftMax/rightMax）。  
    Did I update state before computing (e.g., trap maxima)?

### 8.4 複雜度確認｜Complexity Sanity-check

*   每個指針是否只朝單方向移動，保證總步數線性。  
    Do pointers move only in one direction, ensuring linear total steps?

*   k-sum 是否是 O(n^(k-1)) 的預期，並有合理剪枝。  
    Is complexity aligned with O(n^(k-1)) for k-sum with reasonable pruning?

***

## 9) 記憶錨點與類比（用圖像或比喻）｜Memory Anchors & Analogies

*   \*\*Two pointers 像「在排序名單上夾逼找組合」：\*\*太小就把左端往右推，太大就把右端往左推。  
    **Two pointers is like “squeezing a sorted list to find combinations”:** too small push left inward, too big pull right inward.

*   \*\*3Sum 的去重像「同一張臉只記一次」：\*\*同一個數值代表同一等價類，遇到重複就跳過避免重複報案。  
    **3Sum dedup is like “record each face once”:** same value is one equivalence class; skip repeats to avoid duplicate reports.

*   \*\*Trapping Rain Water 像「兩側堤防的最低水位」：\*\*哪邊堤防較低，那邊的水位就已經被決定了。  
    **Trapping Rain Water is like “the lower levee sets the waterline”:** the lower boundary side’s water is already determined.

***
