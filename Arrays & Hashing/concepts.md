# Arrays & Hashing（中階）TypeScript

***

## 1) 學習目標（3–5 點）｜Learning Objectives (3–5)

*   你能把「陣列 + 雜湊」題的核心套路分類，並在 1–2 分鐘內選對解法方向。  
    You can categorize “arrays + hashing” problems and choose the right approach within 1–2 minutes.

*   你能熟練使用 `Map/Set` 寫出 O(n) 或 O(n log n) 的解法，並避免常見陷阱（例如 key 設計、碰撞式思維錯誤、初始化與更新順序）。  
    You can confidently use `Map/Set` to implement O(n) or O(n log n) solutions and avoid common pitfalls (key design, flawed collision thinking, update order).

*   你能在口述時清楚對比：暴力法 → 優化法 → 最佳法，並用複雜度與不變量（invariant）說服面試官。  
    You can clearly narrate brute-force → optimized → optimal, and justify with complexity and invariants.

*   你能處理「重複元素、負數、零、空陣列、大輸入」等邊界條件，並寫出可測試的 TypeScript 程式。  
    You can handle edge cases (duplicates, negatives, zeros, empty arrays, large inputs) and write testable TypeScript.

***

## 2) 核心觀念速覽（定義、直覺、複雜度、適用與不適用）｜Core Concepts (Definition, Intuition, Complexity, When to Use/Not Use)

### 2.1 雜湊表（Hash Map / Set）

*   \*\*定義：\*\*用 key → value 的結構，理想情況下查找/插入/更新為均攤 O(1)。  
    **Definition:** A key → value structure with amortized O(1) lookup/insert/update in typical cases.

*   \*\*直覺：\*\*把「需要反覆搜尋」變成「一次記錄、之後秒查」。  
    **Intuition:** Turn repeated searching into “record once, query instantly.”

*   \*\*時間複雜度：\*\*均攤 O(1)，整體常見 O(n)。  
    **Time complexity:** Amortized O(1) per operation, commonly O(n) overall.

*   \*\*空間複雜度：\*\*通常 O(n)（取決於存多少 key）。  
    **Space complexity:** Typically O(n), depending on how many keys you store.

*   **適用場景：**  
    **When to use:**
    *   計數（frequency）、去重（dedup）、存在性（membership）。  
        Counting (frequency), deduplication, membership checks.
    *   前綴和（prefix sum）搭配次數表，快速計算子陣列條件。  
        Prefix sums with a frequency map to count subarrays efficiently.
    *   以「某種簽名」做分組（例如 anagram signature）。  
        Grouping by a “signature” (e.g., anagram signature).

*   **不適用/注意：**  
    **Not ideal / watch out:**
    *   需要有序輸出時，雜湊本身不保證順序（TypeScript/JS 的 Map 有插入順序，但不要過度依賴面試假設）。  
        When you need sorted order; hash doesn’t guarantee ordering (JS Map preserves insertion order, but don’t over-assume in interviews).
    *   Key 設計不當會導致錯誤（例如用陣列當 key、或用 join 未處理分隔符歧義）。  
        Bad key design causes bugs (e.g., using arrays as keys, or ambiguous `join` without delimiters).

***

### 2.2 陣列（Arrays）+ 雜湊的典型組合

*   \*\*兩數/多數關係：\*\*用雜湊記錄「我需要的補數」或「已看過的元素」。  
    **2-sum / k-sum relationships:** Use a hash to store “needed complements” or “seen elements.”

*   \*\*子陣列（subarray）條件：\*\*用前綴和把「區間和」轉成「兩個前綴和的差」。  
    **Subarray constraints:** Use prefix sums to convert “range sum” into “difference of two prefix sums.”

*   \*\*滑動視窗（sliding window）＋計數表：\*\*維持視窗內頻率來滿足條件（例如最長不重複子字串）。  
    **Sliding window + counts:** Maintain frequencies in-window to satisfy constraints (e.g., longest substring without repeats).

***

## 3) 典型題型 / 模式｜Typical Patterns / Templates

### 3.1 Frequency Map（頻率表）

*   \*\*用途：\*\*Top K、重複檢測、同構/變位詞、投票/多數元素。  
    **Use cases:** Top K, duplicate detection, isomorphism/anagrams, majority vote variants.

*   \*\*模板思路：\*\*一趟掃描更新 `count[x]++`，必要時搭配堆/桶排序。  
    **Template:** One pass update `count[x]++`, optionally combined with heap/bucket sort.

***

### 3.2 Membership Set（存在性集合）

*   \*\*用途：\*\*Longest consecutive sequence、去重後判斷、快速查詢。  
    **Use cases:** Longest consecutive sequence, dedup + checks, fast membership queries.

*   \*\*模板思路：\*\*先放 Set，再用 O(1) membership 連續延伸或判斷。  
    **Template:** Put items into a Set, then extend/check in O(1).

***

### 3.3 Prefix Sum + Hash（前綴和 + 雜湊）

*   \*\*用途：\*\*Subarray sum equals K、子陣列數量、0/1 陣列平衡問題。  
    **Use cases:** Subarray sum equals K, counting subarrays, balancing 0/1 arrays.

*   \*\*不變量：\*\*若 `prefix[j] - prefix[i] = k`，則存在 `prefix[i] = prefix[j] - k`。  
    **Invariant:** If `prefix[j] - prefix[i] = k`, then `prefix[i] = prefix[j] - k` must exist.

***

### 3.4 Sliding Window + Hash（滑動視窗 + 雜湊）

*   \*\*用途：\*\*最長/最短滿足條件子陣列、字元頻率匹配（anagram in string）。  
    **Use cases:** Longest/shortest window meeting constraints, frequency matching.

*   \*\*關鍵：\*\*視窗擴張/收縮的條件要單調可調整（否則不是標準 sliding window）。  
    **Key:** The condition must be maintainable with monotonic expand/shrink adjustments.

***

## 4) 範例講解｜Worked Examples

***

## 範例 1：Subarray Sum Equals K（子陣列和為 K 的個數）

### 4.1 問題重述｜Restatement

*   \*\*題目：\*\*給定整數陣列 `nums` 與整數 `k`，回傳總共有多少個「連續子陣列」的和等於 `k`。  
    **Problem:** Given an integer array `nums` and integer `k`, return the number of **contiguous subarrays** whose sum equals `k`.

*   \*\*重點：\*\*子陣列必須連續，且元素可包含負數。  
    **Key:** Subarrays must be contiguous, and numbers can be negative.

***

### 4.2 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(n²) 或 O(n³)）

*   \*\*作法：\*\*枚舉所有起點 i 與終點 j，計算 `sum(nums[i..j])` 看是否等於 k。  
    **Approach:** Enumerate all (i, j) and compute `sum(nums[i..j])` to compare with k.

*   \*\*複雜度：\*\*若每次重新算和是 O(n)，總共 O(n³)；用累加可降到 O(n²)。  
    **Complexity:** O(n³) if summing each range from scratch; O(n²) if you accumulate as you expand j.

*   \*\*問題：\*\*n 一大就超時。  
    **Issue:** Times out for large n.

#### 優化（Prefix Sum 陣列 + O(1) 區間和，但仍要枚舉 i, j）

*   \*\*作法：\*\*先建 prefix sum：`P[t] = nums[0..t-1]`，則區間和 `sum(i..j) = P[j+1]-P[i]`。  
    **Approach:** Build prefix sums `P[t]=sum(nums[0..t-1])`, then `sum(i..j)=P[j+1]-P[i]`.

*   \*\*複雜度：\*\*仍需枚舉 O(n²) 對 (i, j)。  
    **Complexity:** Still O(n²) pairs to check.

#### 最佳（Prefix Sum + HashMap 計數，O(n)）

*   \*\*核心轉換：\*\*我們在位置 j 有 `prefix = P[j+1]`，要找 `P[i] = prefix - k` 出現過幾次。  
    **Key transform:** At position j with prefix `P[j+1]=prefix`, we need how many times `P[i]=prefix-k` occurred.

*   \*\*方法：\*\*用 `Map<prefixSum, frequency>` 記錄每個 prefixSum 出現次數。  
    **Method:** Use a `Map<prefixSum, frequency>` to count occurrences.

*   **初始化：**`map.set(0, 1)` 表示空前綴（在 index=-1）出現一次，能處理從 0 開始的子陣列。  
    **Initialization:** `map.set(0, 1)` represents an empty prefix once, enabling subarrays starting at index 0.

***

### 4.3 時間/空間複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n)，每個元素做 O(1) Map 操作。  
    **Time:** O(n), one pass with O(1) map ops.

*   \*\*空間：\*\*O(n)，最壞每個 prefixSum 都不同。  
    **Space:** O(n), worst case all prefix sums are distinct.

*   **邊界：**  
    **Edges:**
    *   `nums` 為空 → 回傳 0。  
        Empty array → return 0.
    *   `k` 為 0，且含 0/負數 → 仍可正常計數。  
        `k=0` with zeros/negatives → still works.
    *   大數值 → 注意 JS number 是浮點，但整數安全範圍內通常 OK（面試多假設 32-bit int）。  
        Large values → JS uses floating-point numbers; usually fine within safe integer (interviews often assume 32-bit ints).

***

### 4.4 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤 1：\*\*把 `map` 存成「是否出現過」而不是「出現次數」。  
    **Mistake 1:** Storing only “seen or not” instead of frequency.

*   \*\*為何錯：\*\*同一個 prefixSum 可能出現多次，會對應多個不同 i，少算答案。  
    **Why wrong:** The same prefix sum can occur multiple times, yielding multiple valid starts i; you undercount.

*   \*\*錯誤 2：\*\*更新 map 的順序錯誤（先加當前 prefix 再查）。  
    **Mistake 2:** Wrong update order (add current prefix before querying).

*   \*\*為何錯：\*\*會把長度為 0 的子陣列或同一位置錯誤納入（視情況造成多算）。  
    **Why wrong:** You may accidentally count invalid zero-length ranges or same-index artifacts, overcounting in some cases.

***

### 4.5 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * 子陣列和為 K 的個數
 * Count the number of subarrays whose sum equals k
 */
export function subarraySumEqualsK(nums: number[], k: number): number {
  // prefixSum -> frequency
  // 前綴和 -> 出現次數
  const freq = new Map<number, number>();

  // 空前綴和為 0，出現 1 次
  // Empty prefix sum 0 occurs once
  freq.set(0, 1);

  let prefix = 0; // 目前前綴和 / current prefix sum
  let ans = 0;    // 答案計數 / answer count

  for (const x of nums) {
    // 更新前綴和
    // Update running prefix sum
    prefix += x;

    // 需要找之前有多少個 prefix = (currentPrefix - k)
    // We need how many previous prefixes equal (currentPrefix - k)
    const need = prefix - k;

    // 若存在，代表有那麼多個起點 i 讓區間和為 k
    // If present, that many start indices i make a subarray sum k
    ans += freq.get(need) ?? 0;

    // 最後再把目前 prefix 記錄進 freq（順序很重要）
    // Record current prefix after querying (order matters)
    freq.set(prefix, (freq.get(prefix) ?? 0) + 1);
  }

  return ans;
}
```

***

## 範例 2：Group Anagrams（分組變位詞）

### 4.6 問題重述｜Restatement

*   \*\*題目：\*\*給定字串陣列 `strs`，把所有互為變位詞（anagrams）的字串分到同一組。  
    **Problem:** Given an array of strings `strs`, group strings that are anagrams into the same group.

*   \*\*重點：\*\*相同字母、相同次數、順序不重要。  
    **Key:** Same letters with same counts; order doesn’t matter.

***

### 4.7 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(m² \* L log L)）

*   \*\*作法：\*\*兩兩比較字串是否互為變位詞（排序或計數比較）。  
    **Approach:** Compare each pair; check anagram via sorting or counting.

*   \*\*問題：\*\*兩兩比對成本高。  
    **Issue:** Quadratic comparisons are expensive.

#### 優化/最佳（雜湊分組：signature 作為 key）

*   \*\*核心：\*\*把每個字串轉成「可比較的簽名」當作 key。  
    **Core:** Convert each string into a comparable “signature” used as hash key.

*   **常見簽名法：**  
    **Common signatures:**
    *   **排序後字串**：`"eat" -> "aet"`（每個字串 O(L log L)）。  
        **Sorted string:** `"eat" -> "aet"` (O(L log L) per string).
    *   **26 字母頻率向量**：`[1,0,0,...]`（每個字串 O(L)）。  
        **26-letter frequency vector:** `[1,0,0,...]` (O(L) per string).

*   \*\*中階建議：\*\*英文小寫限定時，用頻率向量更快、更穩。  
    **Intermediate recommendation:** For lowercase English, frequency-vector is faster and robust.

***

### 4.8 複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n \* L)（計數法），n 字串數，L 平均長度。  
    **Time:** O(n \* L) with counting, where n=#strings, L=avg length.

*   \*\*空間：\*\*O(n \* L)（輸出）＋ O(n)（map keys）。  
    **Space:** O(n \* L) output + O(n) map keys.

*   **邊界：**  
    **Edges:**
    *   空字串 `""` 要能被正確分組。  
        Empty strings must be grouped correctly.
    *   若包含非小寫英文字母，要改用通用計數（例如 Map\<char, count>）或排序法。  
        If not limited to lowercase letters, use generic counting (Map) or sorting.

***

### 4.9 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤：\*\*用 `counts.join('')` 當 key，沒加分隔符。  
    **Mistake:** Using `counts.join('')` as key without delimiters.

*   \*\*為何錯：\*\*例如 `[1,11]` 與 `[11,1]` 都可能變成 `"111"` 造成碰撞。  
    **Why wrong:** E.g., `[1,11]` and `[11,1]` can both become `"111"`, causing collisions.

*   \*\*正確：\*\*用分隔符 `'#'` 或固定格式序列化。  
    **Correct:** Add a delimiter like `'#'` or use a fixed serialization format.

***

### 4.10 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * 分組變位詞
 * Group anagrams together
 *
 * 假設輸入為小寫英文字母 a-z
 * Assume input strings are lowercase a-z
 */
export function groupAnagrams(strs: string[]): string[][] {
  const groups = new Map<string, string[]>();

  for (const s of strs) {
    // 26 個字母頻率
    // 26-letter frequency
    const counts = new Array<number>(26).fill(0);

    for (let i = 0; i < s.length; i++) {
      const code = s.charCodeAt(i) - 97; // 'a' = 97
      counts[code]++;
    }

    // 用分隔符避免 key 碰撞
    // Use delimiter to avoid key collisions
    const key = counts.join("#");

    // 放入對應群組
    // Append to the corresponding group
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(s);
  }

  // 回傳所有群組
  // Return all grouped arrays
  return Array.from(groups.values());
}
```

***

## 5) 常見陷阱與易混淆概念（對比表述）｜Common Pitfalls & Confusions (Contrast)

> 依你的資深程度，我用「對比」方式讓你快速掃雷。  
> Given your seniority, here are contrastive “quick minesweep” notes.

*   \*\*Set vs Map：\*\*Set 用於存在性，Map 用於 key→值（如計數、索引）。  
    **Set vs Map:** Set for membership; Map for key→value (counts, indices).

*   \*\*「只記 seen」vs「記 frequency」：\*\*計數題（subarray count、duplicate count）幾乎都要 frequency。  
    **Seen-only vs frequency:** Counting problems almost always require frequencies.

*   \*\*prefix sum 初始化 `0:1`：\*\*缺了會漏算從 index 0 開始的區間。  
    **Prefix init `0:1`:** Without it, you miss subarrays starting at index 0.

*   \*\*Sliding window 不是萬能：\*\*有負數時，視窗條件通常不單調，不能硬套雙指針。  
    **Sliding window isn’t universal:** With negatives, conditions often aren’t monotonic, so two-pointers may fail.

*   **Key 序列化：**`join` 一定要 delimiter，或使用固定寬度/JSON（但要注意效能）。  
    **Key serialization:** `join` needs delimiter, or fixed-width/JSON (mind performance).

***

## 6) 面試實戰建議：口條框架、白板策略、常見 follow-up｜Interview Playbook

### 6.1 口條框架（建議 60–120 秒）

*   \*\*(1) 重述問題 + 釐清限制：\*\*是否有負數？要回傳數量還是索引？資料量級？  
    **(1) Restate + constraints:** Negatives? Return count or indices? Input size?

*   \*\*(2) 提出暴力與瓶頸：\*\*O(n²) 枚舉會超時。  
    **(2) Brute force + bottleneck:** O(n²) enumeration is too slow.

*   \*\*(3) 引出關鍵轉換與不變量：\*\*prefix 差 / signature key / membership。  
    **(3) Key transform + invariant:** prefix difference / signature keys / membership.

*   \*\*(4) 給出複雜度：\*\*時間 O(n)，空間 O(n)。  
    **(4) Complexity:** Time O(n), space O(n).

*   \*\*(5) 點出 edge cases：\*\*空、重複、負數、初始化順序。  
    **(5) Edge cases:** empty, duplicates, negatives, init/order.

### 6.2 白板/手寫策略（資深加分點）

*   先寫「不變量」再寫碼，面試官會更信服。  
    Write the invariant before code; it increases credibility.

*   把 map 更新順序寫成三行固定模板（查 → 累加答案 → 更新 freq）。  
    Use a fixed 3-line template (query → add to answer → update freq).

### 6.3 常見 Follow-up

*   若要回傳「任一組 subarray 的起訖索引」怎麼做？  
    If asked to return one subarray’s indices, how would you do it?
    *   用 map 存 prefixSum → earliest index（或存所有 index）。  
        Store prefixSum → earliest index (or all indices).

*   若要找「最短/最長符合條件子陣列」呢？  
    What about shortest/longest subarray meeting a condition?
    *   可能需要單調隊列、二分、或不同轉換（視題意）。  
        You may need monotonic deque, binary search, or a different transform.

***

## 7) 練習題（3 題：易/中/難）｜Practice (Easy/Medium/Hard)

### 7.1 易：Contains Duplicate（是否有重複）

*   \*\*題目：\*\*給定整數陣列，若任一數字出現至少兩次回傳 true。  
    **Problem:** Return true if any value appears at least twice.

*   \*\*提示：\*\*用 Set，掃描時若已存在就返回。  
    **Hint:** Use a Set; if seen, return early.

*   \*\*標準解思路：\*\*Set membership，時間 O(n)、空間 O(n)。  
    **Solution idea:** Set membership; O(n) time, O(n) space.

***

### 7.2 中：Top K Frequent Elements（前 K 常見元素）

*   \*\*題目：\*\*回傳出現頻率最高的 k 個元素。  
    **Problem:** Return the k most frequent elements.

*   \*\*提示：\*\*先 frequency map，再用桶排序（bucket）或最小堆（min-heap）。  
    **Hint:** Build frequency map, then bucket sort or min-heap.

*   **標準解思路：**  
    **Solution idea:**
    *   Map 計數 O(n)。  
        Count with Map O(n).
    *   桶排序：頻率範圍 1..n，建 buckets\[f] 放元素，反向取 k 個。  
        Bucket: freq in 1..n, buckets\[f] holds elements, iterate descending to take k.

***

### 7.3 難：Longest Consecutive Sequence（最長連續序列）

*   \*\*題目：\*\*找出最長的連續整數序列長度（不要求在原陣列連續）。  
    **Problem:** Find the length of the longest consecutive integer sequence (not necessarily contiguous in array).

*   \*\*提示：\*\*用 Set；只從「序列起點」開始延伸（x-1 不在 Set 才是起點）。  
    **Hint:** Use a Set; only expand from sequence starts (where x-1 is not in Set).

*   **標準解思路：**  
    **Solution idea:**
    *   先全部放入 Set。  
        Put all into a Set.
    *   對每個 x，若 x-1 不在 Set，從 x 開始 while x+1 在 Set 延伸並更新答案。  
        For each x, if x-1 not in Set, expand while x+1 in Set and update best.
    *   每個元素最多被延伸一次，總時間 O(n)。  
        Each element is expanded at most once, total O(n).

***

## 8) 快速檢核表（Checklists）｜Self-check / Debug / Complexity

### 8.1 解題前（Problem framing）

*   我是否確認是 **subarray（連續）** 還是 **subsequence（不連續）**？  
    Did I confirm whether it’s a **subarray (contiguous)** or **subsequence (non-contiguous)**?

*   我是否確認輸入是否包含負數（影響 sliding window 可行性）？  
    Did I confirm whether negatives exist (affects sliding window viability)?

*   我是否需要回傳 count / indices / actual groups？  
    Do I need to return count / indices / actual groups?

### 8.2 寫碼中（Implementation）

*   Map 的更新順序是否正確（先查再更新 vs 先更新再查）？  
    Is the Map update order correct (query-before-update vs update-before-query)?

*   key 是否會碰撞（序列化 delimiter、有無歧義）？  
    Can keys collide (delimiter, ambiguity)?

*   是否處理空輸入與單元素？  
    Did I handle empty and single-element inputs?

### 8.3 寫完後（Complexity sanity）

*   時間是否真的一趟或兩趟掃描（O(n) / O(n log n)）？  
    Is runtime truly one/two passes (O(n) / O(n log n))?

*   空間是否合理（O(n)）且沒有不必要的大物件複製？  
    Is space reasonable (O(n)) without unnecessary large copies?

***

## 9) 記憶錨點與類比（圖像/比喻）｜Memory Anchors & Analogies

*   \*\*Hash Map 像「通訊錄」：\*\*你不用每次翻遍全班找人，只要用名字（key）直接找到電話（value）。  
    **Hash Map is like a “phonebook”:** You don’t scan everyone; you look up by name (key) to get the number (value).

*   \*\*Prefix Sum 像「里程表」：\*\*從起點到每個點的累積里程記下來，兩點距離就是里程表差值。  
    **Prefix Sum is like an “odometer”:** Record cumulative distance; distance between two points is the difference.

*   \*\*Frequency Map 像「點名簿」：\*\*每看到一個人就蓋一次章，最後一看章數就知道出現次數。  
    **Frequency Map is like a “stamp sheet”:** Each occurrence stamps once; total stamps equal frequency.

*   \*\*Set 像「門禁名單」：\*\*想知道某人是否在名單上，一刷就知道（O(1)）。  
    **Set is like an “access list”:** Check membership instantly (O(1)).

***
