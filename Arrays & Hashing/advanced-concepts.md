# Arrays & Hashing（Advanced）TypeScript

> 這份進階版會把你從「會用 Map/Set」推到「會設計 key、會證明不變量、會處理精度/碰撞/邊界」。  
> This advanced version takes you from “can use Map/Set” to “can design keys, prove invariants, and handle precision/collisions/edge cases.”

***

## 1) 學習目標（3–5 點）｜Learning Objectives (3–5)

*   你能在 60–120 秒內把 Arrays & Hashing 題型映射到正確模板（prefix、mod、canonicalization、counting、pair hashing）。  
    You can map arrays & hashing problems to the right template (prefix, mod, canonicalization, counting, pair hashing) within 60–120 seconds.

*   你能設計「穩定且不碰撞」的 key（tuple/向量/分數/多維索引），並清楚說明為什麼安全。  
    You can design stable, collision-resistant keys (tuples/vectors/fractions/multi-d indices) and explain why they’re safe.

*   你能處理「符號與正規化（normalization）」、「溢位與精度」、「更新順序」等高階陷阱。  
    You can handle advanced pitfalls: sign & normalization, overflow/precision, and update ordering.

*   你能把 O(n²) 直覺解法，系統性降到 O(n log n) 或 O(n)，並用不變量說服面試官。  
    You can systematically reduce O(n²) solutions to O(n log n) or O(n) and justify with invariants.

*   你能寫出在 TypeScript/JS 執行環境中可預期效能的實作（Map/Set 選用、避免熱點 allocation）。  
    You can implement performance-predictable solutions in TS/JS (Map/Set choices, avoiding hot-path allocations).

***

## 2) 核心觀念速覽（定義、直覺、複雜度、適用與不適用場景）｜Core Concepts (Definition, Intuition, Complexity, When to Use/Not Use)

### 2.1 Hashing 的本質：把「關係」變成「查表」

**Hashing turns “relationships” into “table lookups.”**

*   \*\*定義：\*\*用 key 的等價類（equivalence class）代表一種狀態或關係，讓查找/更新接近 O(1)。  
    **Definition:** Use a key’s equivalence class to represent a state/relationship so lookup/update is \~O(1).

*   \*\*直覺：\*\*你不是在「找答案」，你是在「維護一個可被查詢的歷史」。  
    **Intuition:** You’re not “searching for answers,” you’re “maintaining a queryable history.”

*   \*\*複雜度：\*\*平均 O(1) 操作，但要注意 key 生成成本常常才是瓶頸（例如排序 key 變 O(L log L)）。  
    **Complexity:** Average O(1) per op, but key-generation cost is often the real bottleneck (e.g., sorting keys becomes O(L log L)).

*   **適用：**  
    **Use when:**
    *   你能定義一個「可正規化」且「可比較」的狀態（prefix sum、prefix mod、斜率、頻率向量）。  
        You can define a “normalizable” and “comparable” state (prefix sum, prefix mod, slope, frequency vector).
    *   你需要計數、多對多配對、快速 membership。  
        You need counting, many-to-many pairing, or fast membership.

*   **不適用/警告：**  
    **Not ideal / warnings:**
    *   你需要全序（sorted order）或範圍查詢時，hash 不是最佳資料結構。  
        If you need total order or range queries, hashing is not ideal.
    *   你無法安全正規化 key（例如浮點斜率）時，必須換表示法（分數化、gcd、BigInt）。  
        If you cannot safely normalize keys (e.g., floating slopes), switch representations (fractions + gcd, BigInt).

***

### 2.2 Advanced Key Design：canonicalization（正規化）> hashing（雜湊）

**Canonicalization matters more than hashing.**

*   \*\*觀念：\*\*在面試中，錯的通常不是 Map，而是 key 的等價判定。  
    **Concept:** In interviews, the bug is rarely Map itself; it’s the equivalence definition of keys.

*   \*\*例子：\*\*斜率要用 `(dy/g, dx/g)` 並統一符號，而不是 `dy/dx` 浮點。  
    **Example:** Slopes should be `(dy/g, dx/g)` with unified sign, not floating `dy/dx`.

*   \*\*例子：\*\*prefix mod 要保證落在 `[0, k-1]`（尤其 JS `%` 對負數會是負的）。  
    **Example:** Prefix modulo must be normalized into `[0, k-1]` (JS `%` yields negative for negatives).

***

### 2.3 TS/JS 實務注意：Map/Set 與數值語義

**Practical TS/JS notes: Map/Set and numeric semantics.**

*   \*\*Map key 的等價：\*\*使用 SameValueZero（`NaN` 等於 `NaN`，`-0` 視為 `0`）。  
    **Map key equality:** Uses SameValueZero (`NaN` equals `NaN`, `-0` treated as `0`).

*   **數字精度：**`number` 是 IEEE-754 double，安全整數範圍是 `±(2^53-1)`。  
    **Numeric precision:** `number` is IEEE-754 double; safe integers are within `±(2^53-1)`.

*   \*\*BigInt：\*\*當 key 或累加可能超出安全整數時，考慮 BigInt（但不要混用 number 與 BigInt）。  
    **BigInt:** Use BigInt when sums/keys may exceed safe integers (but don’t mix number and BigInt).

*   \*\*效能：\*\*避免在熱迴圈中生成大量短字串 key（可以用 pair packing 或較少 allocation 的序列化）。  
    **Performance:** Avoid creating many short string keys in hot loops (use pair packing or lower-allocation serialization).

***

## 3) 典型題型 / 模式｜Typical Patterns / Templates

### 3.1 Prefix Sum + Frequency（前綴和 + 次數表）

*   \*\*適用：\*\*subarray count、等和/差值條件、2D submatrix 壓縮到 1D。  
    **Use cases:** subarray counting, sum/difference constraints, 2D submatrix reduced to 1D.

*   **不變量：**`prefix[j] - prefix[i] = target` ↔ `prefix[i] = prefix[j] - target`。  
    **Invariant:** `prefix[j] - prefix[i] = target` ↔ `prefix[i] = prefix[j] - target`.

***

### 3.2 Prefix Mod + Frequency（前綴模數 + 次數表）

*   \*\*適用：\*\*subarray sum divisible by k、同餘類配對、平衡轉換（0/1 → -1/+1）。  
    **Use cases:** subarray sums divisible by k, congruence pairing, balance transforms (0/1 → -1/+1).

*   **不變量：**`(prefix[j] - prefix[i]) % k == 0` ↔ `prefix[j] % k == prefix[i] % k`。  
    **Invariant:** `(prefix[j] - prefix[i]) % k == 0` ↔ `prefix[j] % k == prefix[i] % k`.

*   \*\*高階陷阱：\*\*負數 mod 正規化（`((x % k) + k) % k`）。  
    **Advanced pitfall:** Normalize negative mod via `((x % k) + k) % k`.

***

### 3.3 Canonicalization Keys（正規化 key）

*   \*\*適用：\*\*斜率/方向向量、比例、分組（anagram signature 的進階版）。  
    **Use cases:** slopes/direction vectors, ratios, grouping (advanced anagram signatures).

*   **技術：**`gcd` 約分、統一符號、固定格式序列化（如 `dy#dx`）。  
    **Techniques:** Reduce by `gcd`, unify sign, fixed-format serialization (e.g., `dy#dx`).

***

### 3.4 Pair / Tuple Hashing（對/多元組 hashing）

*   \*\*適用：\*\*兩個維度的狀態（row/col、(i,j)、(a,b) pair）。  
    **Use cases:** Two-dimensional states (row/col, (i,j), (a,b) pairs).

*   **策略：**  
    **Strategies:**
    *   字串序列化（簡單但 allocation 多）。  
        String serialization (simple but allocation-heavy).
    *   64-bit packing（需 BigInt 或自訂分離避免碰撞）。  
        64-bit packing (requires BigInt or careful separation to avoid collisions).

***

### 3.5 Coordinate Compression + Hash（座標壓縮 + 雜湊）

*   \*\*適用：\*\*值域大但相對順序重要的情境（離散化後再用 array/bit 等結構）。  
    **Use cases:** Huge value ranges where relative order matters (discretize then use arrays/BIT/etc.).

*   \*\*面試加分：\*\*你能說清楚「壓縮不改變比較結果」與「空間從 O(U) 變 O(n)」。  
    **Interview bonus:** You can explain “compression preserves ordering” and “space drops from O(U) to O(n).”

***

## 4) 範例講解（至少 1–2 題）｜Worked Examples (at least 1–2)

***

## 範例 1：Subarray Sums Divisible by K（子陣列和可被 K 整除的個數）

### 4.1 問題重述｜Restatement

*   \*\*題目：\*\*給定整數陣列 `nums` 與整數 `k`（k ≠ 0），回傳有多少個連續子陣列的總和可以被 `k` 整除。  
    **Problem:** Given an integer array `nums` and integer `k` (k ≠ 0), return the number of contiguous subarrays whose sum is divisible by `k`.

*   \*\*關鍵：\*\*陣列可能有負數，因此不能直接套 monotonic sliding window。  
    **Key:** The array may contain negatives, so monotonic sliding window doesn’t apply.

***

### 4.2 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(n²)）

*   \*\*作法：\*\*枚舉所有 (i, j) 並計算區間和，判斷 `sum % k == 0`。  
    **Approach:** Enumerate all (i, j), compute range sum, check `sum % k == 0`.

*   \*\*瓶頸：\*\*O(n²) 在 n=1e5 會爆炸。  
    **Bottleneck:** O(n²) blows up at n=1e5.

#### 最佳（Prefix Mod + Frequency，O(n)）

*   \*\*轉換：\*\*令 `P[t]` 為前 t 個元素和，則區間和 `P[j] - P[i]` 可被 k 整除 ⇔ `P[j] % k == P[i] % k`。  
    **Transform:** Let `P[t]` be sum of first t elements; `P[j] - P[i]` divisible by k ⇔ `P[j] % k == P[i] % k`.

*   \*\*策略：\*\*一趟掃描，維護「每個餘數 r 出現次數」。  
    **Strategy:** One pass, maintain frequency of each remainder r.

*   \*\*計數：\*\*當前餘數為 r 時，答案增加 `freq[r]`（因為之前同餘的前綴都能配對）。  
    **Counting:** If current remainder is r, add `freq[r]` because all previous same remainders form valid pairs.

*   **初始化：**`freq[0] = 1` 代表空前綴的餘數為 0。  
    **Initialization:** `freq[0] = 1` represents empty prefix remainder 0.

***

### 4.3 複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n)，每個元素 O(1) 更新。  
    **Time:** O(n), O(1) update per element.

*   \*\*空間：\*\*O(k) 或 O(min(n, k))（若用 Map 存出現過的餘數）。  
    **Space:** O(k) or O(min(n, k)) (if using Map for seen remainders).

*   **邊界：**  
    **Edges:**
    *   `k` 可能很大（例如 1e9），用 Map 比開 array 更合理。  
        If `k` can be huge (e.g., 1e9), Map is better than allocating an array.
    *   `nums` 含負數時，必須正規化餘數到 `[0, k-1]`。  
        With negatives, you must normalize remainder into `[0, k-1]`.

***

### 4.4 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤 1：\*\*直接用 `rem = prefix % k`，不處理負數。  
    **Mistake 1:** Using `rem = prefix % k` directly without handling negatives.

*   \*\*為何錯：\*\*在 JS/TS 中 `-1 % 5 === -1`，同餘類會被拆成不同 key，導致少算。  
    **Why wrong:** In JS/TS, `-1 % 5 === -1`, so congruent classes split into different keys and you undercount.

*   \*\*錯誤 2：\*\*忘記初始化 `freq[0]=1`。  
    **Mistake 2:** Forgetting `freq[0]=1`.

*   \*\*為何錯：\*\*會漏掉從索引 0 開始、整段就能被 k 整除的子陣列。  
    **Why wrong:** You miss subarrays starting at index 0 whose sum is divisible by k.

***

### 4.5 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
/**
 * 子陣列和可被 K 整除的個數
 * Count subarrays whose sum is divisible by k
 *
 * 關鍵：prefix mod 的同餘配對
 * Key: pair equal remainders of prefix sums
 */
export function subarraysDivByK(nums: number[], k: number): number {
  // remainder -> frequency
  // 餘數 -> 出現次數
  const freq = new Map<number, number>();

  // 空前綴 (prefix = 0) 的餘數為 0，先出現一次
  // Empty prefix (prefix = 0) has remainder 0, seen once
  freq.set(0, 1);

  let prefix = 0;
  let ans = 0;

  for (const x of nums) {
    prefix += x;

    // 正規化餘數到 [0, k-1]
    // Normalize remainder into [0, k-1]
    const rem = ((prefix % k) + k) % k;

    // 之前相同 rem 的前綴都能與目前前綴形成可整除的區間
    // All previous same remainders pair with current to form divisible ranges
    ans += freq.get(rem) ?? 0;

    // 更新頻率
    // Update frequency
    freq.set(rem, (freq.get(rem) ?? 0) + 1);
  }

  return ans;
}
```

***

## 範例 2：Max Points on a Line（同一直線最多點數）— 斜率 key 設計（Advanced Canonicalization）

### 4.6 問題重述｜Restatement

*   \*\*題目：\*\*給定平面點集合 `points[i] = [x, y]`，求同一直線上的最多點數。  
    **Problem:** Given `points[i] = [x, y]` on a plane, return the maximum number of points that lie on the same straight line.

*   \*\*關鍵：\*\*不能用浮點斜率當 key，必須用分數正規化（dy/dx）。  
    **Key:** You cannot key by floating slope; you must normalize dy/dx as a reduced fraction.

***

### 4.7 思路：暴力 → 優化 → 最佳解｜Brute → Optimized → Optimal

#### 暴力（O(n³)）

*   \*\*作法：\*\*枚舉任兩點定一條線，再掃過所有點檢查是否在同線。  
    **Approach:** Choose any two points to define a line, then scan all points to test collinearity.

*   \*\*瓶頸：\*\*O(n³) 太慢。  
    **Bottleneck:** O(n³) is too slow.

#### 最佳（固定一個 anchor，對所有其他點算 slope，O(n²)）

*   \*\*策略：\*\*對每個 anchor 點 i，計算 i 到 j 的方向（dy, dx），用 hash 計數同方向出現次數。  
    **Strategy:** For each anchor point i, compute direction (dy, dx) to every other point j and count equal directions via hashing.

*   \*\*為何可行：\*\*同一直線上、以同一 anchor 為起點的其他點，方向（斜率）必相同。  
    **Why it works:** Points collinear with the same anchor share the same slope/direction from that anchor.

*   \*\*難點：\*\*方向需要 canonicalization：  
    **Hard part:** Directions require canonicalization:
    *   `(dy, dx)` 要用 `gcd(|dy|, |dx|)` 約分。  
        Reduce `(dy, dx)` by `gcd(|dy|, |dx|)`.
    *   統一符號：讓 `dx > 0`，或若 `dx == 0` 則令 `dy = 1` 表示垂直線。  
        Unify sign: enforce `dx > 0`, or if `dx == 0` set `dy = 1` to represent vertical.
    *   水平線：`dy == 0` 則令 `dx = 1` 表示水平線。  
        Horizontal: if `dy == 0`, set `dx = 1`.

*   \*\*重複點：\*\*若有完全相同點（duplicate points），要額外計數 `duplicates`。  
    **Duplicates:** If identical points exist, count them separately as `duplicates`.

***

### 4.8 複雜度與邊界｜Complexities & Edge Cases

*   \*\*時間：\*\*O(n²)；對每個 anchor 建一個 map，掃描其餘點。  
    **Time:** O(n²); for each anchor, build a map while scanning other points.

*   \*\*空間：\*\*O(n)；單次 anchor map 最多存 n 種 slope key。  
    **Space:** O(n); per anchor, slope map holds up to n keys.

*   **邊界：**  
    **Edges:**
    *   所有點相同 → 答案是 n。  
        All points identical → answer is n.
    *   垂直/水平線與符號統一。  
        Vertical/horizontal lines and sign unification.
    *   座標可能大，但 dy/dx 仍在安全整數範圍內通常 OK（若題目允許到 1e9，差值到 2e9 仍安全）。  
        Coordinates may be large, but dy/dx typically stays in safe integer range (e.g., up to 2e9 diffs for 1e9 coords).

***

### 4.9 錯誤示範 & 為何錯｜Incorrect Attempt & Why It’s Wrong

*   \*\*錯誤 1：\*\*用浮點 `dy/dx` 當 key。  
    **Mistake 1:** Using floating `dy/dx` as key.

*   \*\*為何錯：\*\*浮點誤差會讓同一斜率變成不同值（尤其 dy/dx 不能精準表示時）。  
    **Why wrong:** Floating precision splits equal slopes into slightly different values, breaking grouping.

*   \*\*錯誤 2：\*\*沒有統一符號，導致 `(1, -1)` 與 `(-1, 1)` 被當作不同斜率。  
    **Mistake 2:** Not unifying sign, so `(1, -1)` and `(-1, 1)` are treated differently.

*   \*\*為何錯：\*\*它們代表同一條直線的同一斜率。  
    **Why wrong:** They represent the same slope/line.

*   \*\*錯誤 3：\*\*忽略 duplicates。  
    **Mistake 3:** Ignoring duplicate points.

*   \*\*為何錯：\*\*duplicates 應該加到任何斜率計數上，否則答案偏小。  
    **Why wrong:** Duplicates should be added to every slope count for that anchor; otherwise you undercount.

***

### 4.10 TypeScript 參考解（雙語註解）｜Reference Solution (TypeScript, bilingual comments)

```ts
type Point = [number, number];

/**
 * 同一直線最多點數
 * Max points on a line
 *
 * 核心：對每個 anchor，用 slope(direction) 做 hash 計數
 * Core: for each anchor, hash-count slopes/directions
 */
export function maxPointsOnLine(points: Point[]): number {
  const n = points.length;
  if (n <= 2) return n;

  let best = 2;

  for (let i = 0; i < n; i++) {
    const slopes = new Map<string, number>();

    let duplicates = 0; // 與 anchor 相同的點 / points identical to anchor
    let localBest = 0;  // 不含 duplicates 的最佳斜率計數 / best slope count excluding duplicates

    const [x1, y1] = points[i];

    for (let j = i + 1; j < n; j++) {
      const [x2, y2] = points[j];
      let dx = x2 - x1;
      let dy = y2 - y1;

      // 處理重複點
      // Handle duplicate points
      if (dx === 0 && dy === 0) {
        duplicates++;
        continue;
      }

      // 正規化方向向量 (dy, dx)
      // Canonicalize direction vector (dy, dx)
      const g = gcd(Math.abs(dy), Math.abs(dx));
      dy /= g;
      dx /= g;

      // 統一符號：讓 dx > 0
      // Unify sign: enforce dx > 0
      if (dx < 0) {
        dx = -dx;
        dy = -dy;
      }

      // 垂直線：dx == 0，統一成 dy = 1
      // Vertical line: dx == 0, normalize to dy = 1
      if (dx === 0) {
        dy = 1;
      }

      // 水平線：dy == 0，統一成 dx = 1
      // Horizontal line: dy == 0, normalize to dx = 1
      if (dy === 0) {
        dx = 1;
      }

      // 序列化成 key（避免浮點）
      // Serialize into a key (avoid floats)
      const key = `${dy}#${dx}`;

      const count = (slopes.get(key) ?? 0) + 1;
      slopes.set(key, count);

      localBest = Math.max(localBest, count);
    }

    // +1 是 anchor 自己，+duplicates 是重複點
    // +1 for the anchor itself, +duplicates for identical points
    best = Math.max(best, localBest + duplicates + 1);
  }

  return best;
}

/**
 * 最大公因數（歐幾里得算法）
 * Greatest common divisor (Euclidean algorithm)
 */
function gcd(a: number, b: number): number {
  while (b !== 0) {
    const t = a % b;
    a = b;
    b = t;
  }
  return a === 0 ? 1 : a; // 防止除以 0 / prevent division by 0
}
```

***

## 5) 常見陷阱與易混淆概念（對比表述）｜Common Pitfalls & Confusions (Contrast)

*   \*\*「hashing」vs「canonicalization」：\*\*多數錯誤不是 Map 壞掉，而是 key 的等價規則錯。  
    **“Hashing” vs “Canonicalization”:** Most bugs aren’t Map failing; they’re wrong equivalence rules for keys.

*   \*\*浮點 key（danger）vs 分數 key（safe）：\*\*斜率、比例、方向一律用 gcd 約分與符號統一。  
    **Float keys (danger) vs fraction keys (safe):** Slopes/ratios/directions should use gcd reduction + sign normalization.

*   \*\*Set membership（只問在不在）vs Map frequency（要數量）：\*\*計數題幾乎都要 frequency。  
    **Set membership vs Map frequency:** Counting problems almost always need frequencies.

*   \*\*先查再更新 vs 先更新再查：\*\*prefix 類問題大多是「先查歷史，再把當前寫入歷史」。  
    **Query-before-update vs update-before-query:** Prefix problems usually “query history first, then write current into history.”

*   \*\*字串 key（簡單）vs 低 allocation key（快）：\*\*熱點迴圈大量建字串會慢，能用更少 allocation 的格式就用。  
    **String keys (simple) vs low-allocation keys (fast):** Creating many strings in hot loops is slow; reduce allocations when needed.

*   \*\*JS `%` 對負數：\*\*必須正規化到 `[0, k-1]`，否則同餘被拆散。  
    **JS `%` for negatives:** Must normalize to `[0, k-1]` or congruence classes split.

***

## 6) 面試實戰建議：闡述口條框架、白板策略、常見 follow-up｜Interview Playbook

### 6.1 口條框架（適合 advanced 題）

*   **(1) 先定義等價關係：**「什麼狀態算同一類？」（餘數相同、方向相同、簽名相同）。  
    **(1) Define equivalence first:** “Which states are equivalent?” (same remainder, same direction, same signature).

*   \*\*(2) 說明不變量：\*\*用一行公式把配對條件說清楚（例如 `Pj%k==Pi%k`）。  
    **(2) State the invariant:** One formula that nails pairing (e.g., `Pj%k==Pi%k`).

*   \*\*(3) 講 key 正規化：\*\*負數 mod、gcd 約分、符號統一、duplicates。  
    **(3) Explain key canonicalization:** Negative mod, gcd reduction, sign normalization, duplicates.

*   \*\*(4) 給複雜度與最壞情況：\*\*時間 O(n) / O(n²)，空間 O(k) / O(n)。  
    **(4) Complexity + worst-case:** Time O(n)/O(n²), space O(k)/O(n).

*   \*\*(5) 交代 TS/JS 細節：\*\*number 精度、Map key 等價、避免熱點 allocation。  
    **(5) TS/JS specifics:** number precision, Map key equality, avoid hot-path allocations.

***

### 6.2 白板策略（讓面試官「覺得你很穩」）

*   **先寫 canonicalization 函式，再寫主迴圈。**  
    **Write canonicalization helpers before the main loop.**

*   **把更新順序寫成模板：**`ans += freq[key]; freq[key]++` 或 `query → add → update`。  
    **Use a template order:** `ans += freq[key]; freq[key]++` i.e., `query → add → update`.

*   **用 1–2 個反例快速證明你為何不用浮點。**  
    **Use 1–2 counterexamples to justify avoiding floats.**

***

### 6.3 常見 Follow-up（加分回答方向）

*   \*\*Follow-up：\*\*若要回傳「其中一條線」或「那條線上的點集合」怎麼做？  
    **Follow-up:** If asked to return one line or the set of points on it, what changes?

    *   \*\*做法：\*\*在 slope map 裡存 `count + representative indices` 或另存 parent pointers。  
        **Approach:** Store `count + representative indices` in the slope map or keep parent pointers.

*   \*\*Follow-up：\*\*若 points 很多，O(n²) 不夠怎麼辦？  
    **Follow-up:** If n is huge and O(n²) is too slow?

    *   \*\*回答：\*\*一般此題理論下界接近 O(n²)；若要近似可用 randomized sampling 或早停策略，但要清楚 trade-off。  
        **Answer:** Theoretical/typical solutions are \~O(n²); for approximation consider randomized sampling or early stopping with clear trade-offs.

*   \*\*Follow-up：\*\*prefix 類題若數值可能超過 `2^53-1`？  
    **Follow-up:** What if prefix sums exceed `2^53-1`?

    *   \*\*回答：\*\*改用 BigInt 累加與 BigInt key（或在語言允許下用 64-bit int）。  
        **Answer:** Use BigInt for accumulation and as Map key (or 64-bit ints in other languages).

***

## 7) 練習題（3 題：易/中/難）｜Practice (Easy/Medium/Hard)

### 7.1 易：Contiguous Array（0 和 1 數量相同的最長子陣列）

*   \*\*題目：\*\*給定只含 0/1 的陣列，求 0 和 1 數量相同的最長連續子陣列長度。  
    **Problem:** Given a binary array, return the longest contiguous subarray with equal number of 0s and 1s.

*   \*\*提示：\*\*把 0 當 -1，問題變成「前綴和相同的最遠距離」。  
    **Hint:** Treat 0 as -1; it becomes “farthest distance with equal prefix sum.”

*   \*\*標準解思路：\*\*Map 存 prefixSum 的最早 index，遇到同 prefixSum 更新答案。  
    **Solution idea:** Map prefixSum → earliest index; when repeated, update max length.

***

### 7.2 中：Subarrays with Exactly K Distinct（剛好 K 種不同數的子陣列數量）

*   \*\*題目：\*\*回傳恰好包含 K 種不同整數的子陣列數量。  
    **Problem:** Count subarrays that contain exactly K distinct integers.

*   **提示：**`exactly(K) = atMost(K) - atMost(K-1)`。  
    **Hint:** `exactly(K) = atMost(K) - atMost(K-1)`.

*   \*\*標準解思路：\*\*用 sliding window + frequency Map 實作 `atMost(K)`。  
    **Solution idea:** Implement `atMost(K)` using sliding window + frequency Map.

***

### 7.3 難：Count Submatrices Sum to Target（矩陣子矩形和為 target 的數量）

*   \*\*題目：\*\*給定 2D 矩陣，計算有多少個子矩形的和等於 target。  
    **Problem:** Given a 2D matrix, count submatrices whose sum equals target.

*   \*\*提示：\*\*固定上/下邊界，把列壓縮成 1D，然後用 prefix sum + hash 計數。  
    **Hint:** Fix top/bottom rows, compress columns into 1D, then apply prefix sum + hash counting.

*   \*\*標準解思路：\*\*雙層枚舉 row boundaries O(R²)，每次用 O(C) 的 subarray sum count。  
    **Solution idea:** Enumerate row boundaries O(R²); each boundary uses O(C) subarray-sum counting.

***

## 8) 快速檢核表（Checklists）：自我審查/Debug/複雜度確認｜Quick Checklists

### 8.1 Key 設計檢核（Advanced）

*   我是否定義了正確的等價關係（同餘、同方向、同簽名）？  
    Did I define the correct equivalence relation (congruence, direction, signature)?

*   key 是否需要正規化（負數 mod、gcd 約分、符號統一、0 特例）？  
    Does the key need normalization (negative mod, gcd reduction, sign unification, zero cases)?

*   key 是否可能碰撞（字串 join 無分隔、可變長序列化、浮點）？  
    Can keys collide (join without delimiter, variable-length serialization, floats)?

### 8.2 更新順序檢核（Prefix 類必看）

*   我是否遵循 `query history → add to ans → update history` 的順序？  
    Did I follow `query history → add to ans → update history`?

*   我是否做了正確初始化（例如 freq\[0]=1、earliestIndex\[prefix]=0/-1）？  
    Did I initialize correctly (e.g., freq\[0]=1, earliestIndex\[prefix]=0/-1)?

### 8.3 複雜度與實務檢核（TS/JS）

*   我是否在熱點迴圈大量建立字串/陣列造成 GC 壓力？  
    Am I creating many strings/arrays in hot loops causing GC pressure?

*   若有可能超過安全整數，我是否需要 BigInt？  
    If values may exceed safe integers, do I need BigInt?

***

## 9) 記憶錨點與類比（用圖像或比喻）｜Memory Anchors & Analogies

*   \*\*Prefix Mod 像「時鐘」：\*\*走了很多步不重要，重要的是你現在指向哪個刻度（同餘刻度能配對）。  
    **Prefix Mod is like a “clock”:** Total steps don’t matter; the current tick matters (same tick pairs).

*   **Slope Canonicalization 像「分數約分」：**`2/4` 和 `1/2` 其實一樣，必須先約分才不會被誤判成不同。  
    **Slope canonicalization is like “reducing fractions”:** `2/4` equals `1/2`; reduce first to avoid false differences.

*   \*\*Hash Map 像「事件簿」：\*\*你不是回頭找每個事件，而是先把事件分類記帳，之後查帳就知道有幾筆。  
    **Hash Map is like a “ledger”:** You don’t reread all events; you classify and record so queries are instant.

***

