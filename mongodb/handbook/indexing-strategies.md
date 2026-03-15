# 索引策略與查詢優化 / Indexing Strategies & Query Optimization

## Mental model｜心智模型

在 MongoDB 中，索引不僅僅是「加速查詢」的工具，它是**資料庫引擎遍歷資料的路徑圖 (Traversing Roadmap)**。

### 1. 字典查找模型 (The Dictionary Analogy)
想像你要在一本厚重的字典中找出「所有以 'S' 開頭，且長度大於 5 的單字，並按字母順序排列」。
- **無索引 (Collection Scan)**：你必須從第一頁讀到最後一頁，檢查每一個字。這是 $O(N)$。
- **有索引 (Index Scan)**：你直接翻到 'S' 的章節（Equality），因為字典已經排好序了（Sort），你依序往下讀，直到遇到不符合長度條件的為止（Range）。這是 $O(\log N)$。

### 2. 成本階梯 (The Cost Ladder)
優化查詢的核心在於降低「操作成本」。請記住這個成本階梯：
1.  **Index Only (Covered Query)**：最快。只讀索引，完全不碰硬碟上的文件（Document）。
2.  **Index Scan + Fetch**：普通。透過索引找到位置，然後去硬碟抓取完整文件。
3.  **Collection Scan**：最慢。暴力掃描全表。

**優化的目標**：盡量讓查詢停留在 Level 1，避免 Level 3。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The ESR Rule (Equality, Sort, Range)
這是設計複合索引 (Compound Index) 的黃金法則。當你有多個查詢條件時，索引欄位的順序應遵循：

1.  **Equality (精確匹配)**：放在索引最前面。例如 `status: "active"`。這能最快縮小搜尋範圍。
2.  **Sort (排序)**：放在中間。這決定了索引的物理排序。如果查詢需要排序，索引必須提供這個順序，否則 MongoDB 必須在記憶體中進行昂貴的排序（Blocking Sort）。
3.  **Range (範圍)**：放在最後。例如 `price > 100` 或 `date < now()`。一旦進入範圍查詢，索引後的順序就無法保證了，因此 Range 必須在 Sort 之後。

> **實戰口訣**：先過濾相等的，再處理排序，最後才切分範圍。

### 2. 覆蓋查詢 (Covered Queries)
如果一個索引包含了查詢所需的**所有欄位**（包含過濾條件與回傳欄位），MongoDB 就不需要去讀取實際的文件（Fetch）。
- **Pattern**: 使用 `projection` 排除不需要的欄位，特別是 `_id`（除非 `_id` 在索引中）。
- **Benefit**: 效能提升極大，因為索引通常比文件小得多，且常駐記憶體。

### 3. 索引前綴利用 (Index Prefixing)
你不需要為每個查詢建立獨立索引。複合索引 `{ a: 1, b: 1, c: 1 }` 可以支援查詢：
- `{ a: 1 }`
- `{ a: 1, b: 1 }`
- `{ a: 1, b: 1, c: 1 }`
- **注意**：它**不支援**只查詢 `{ b: 1 }` 或 `{ c: 1 }`。

### 4. 部分索引 (Partial Indexes)
只對符合特定條件的文件建立索引，以節省記憶體與硬碟空間。
- **Pattern**: `db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { email: { $exists: true } } })`
- **Use Case**: 軟刪除（Soft Delete）系統中，只對 `deleted_at: null` 的活躍資料建立索引。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 忽略記憶體排序限制 (In-memory Sort Limit)
如果查詢包含排序，但沒有對應的索引（或索引順序不符），MongoDB 會嘗試在記憶體中排序。如果資料量超過 100MB（預設限制），查詢會直接報錯失敗。
- **Pitfall**: 開發環境資料少沒事，上線後資料變多直接炸開。

### 2. 索引過多 (Over-indexing)
- **代價**: 每次 `INSERT`, `UPDATE`, `DELETE` 都需要更新相關索引。索引越多，寫入效能越差。
- **Rule of Thumb**: 盡量控制單一 Collection 的索引數量在 5 個以內，除非讀寫比極高。

### 3. Regex 開頭模糊查詢
- **Anti-pattern**: `/abc/` (contains) 或 `/abc$/` (ends with)。這無法使用 B-Tree 索引的優勢，會導致全索引掃描或全表掃描。
- **Fix**: 只有 `/^abc/` (starts with) 才能有效利用索引。

### 4. 陣列欄位索引爆炸 (Multikey Index Explosion)
對陣列欄位建立索引時，MongoDB 會為陣列中的每個元素建立一個索引項目。如果一個文件中有兩個陣列欄位都被索引，索引大小會呈幾何級數增長。

### 5. 否定查詢 (Negation Inefficiency)
`$ne` (not equal) 通常無法有效利用索引，因為它本質上是「除了這個之外的所有東西」，往往導致掃描範圍過大。

---

## Checklists & workflows｜檢查清單與流程

### Performance Tuning Workflow
1.  開啟 Profiler 或檢查慢查詢日誌 (Slow Query Log)。
2.  鎖定耗時最長的查詢語句。
3.  使用 `explain("executionStats")` 分析 Query Plan。
4.  應用 ESR 法則調整索引。
5.  驗證優化結果。

### Optimization Checklist
- [ ] **ESR Compliance**: 我的複合索引是否遵循 Equality -> Sort -> Range 的順序？
- [ ] **Scan Ratio**: 檢查 `totalKeysExamined` 與 `nReturned` 的比例。理想是 1:1。如果比例很高（例如掃描 1000 個 key 只回傳 1 個 doc），代表索引效率低。
- [ ] **No Collection Scan**: 確認 `stage` 不是 `COLLSCAN`。
- [ ] **Covered Query**: 如果可能，確認 `totalDocsExamined` 為 0。
- [ ] **Sort Stage**: 確認沒有 `SORT` stage（代表使用了索引排序），而是 `IXSCAN`。
- [ ] **Index Size**: 確認索引大小是否能放入 RAM (`db.collection.totalIndexSize()`)。

---

## Real-world examples｜實戰案例

### 情境：電商訂單查詢系統
**需求**：後台管理員想要查詢「狀態為已付款 (PAID)」，且「金額大於 1000 元」的訂單，並按照「下單時間」從新到舊排序。

**Query**:
```javascript
db.orders.find({
  status: "PAID",
  total: { $gt: 1000 }
}).sort({ createdAt: -1 })
```

#### ❌ 錯誤的索引策略
- **Index A**: `{ createdAt: -1 }`
  - **後果**: 雖然排序很快，但 MongoDB 必須掃描所有訂單，然後一個個檢查 `status` 和 `total`。效率低。
- **Index B**: `{ status: 1, total: 1, createdAt: -1 }` (ER-S)
  - **後果**: 這是 SQL 思維的陷阱。雖然過濾了 `status` 和 `total`，但因為 `total` 是範圍查詢，索引的物理順序被打亂，無法用於 `createdAt` 的排序。MongoDB 必須在記憶體中重新排序。

#### ✅ 正確的索引策略 (ESR)
- **Index**: `{ status: 1, createdAt: -1, total: 1 }`
  - **E (Equality)**: `status`。先鎖定 "PAID" 的區塊。
  - **S (Sort)**: `createdAt`。在 "PAID" 區塊內，資料已經按時間排好了。
  - **R (Range)**: `total`。我們依序讀取索引，檢查 `total` 是否大於 1000。
  - **結果**: 不需要額外的 Sort 階段，掃描效率最高。

#### 分析 `explain()` 輸出範例
```json
"executionStats": {
  "nReturned": 50,
  "totalKeysExamined": 55,  // 接近 nReturned，這是健康的
  "totalDocsExamined": 50,  // 沒有多餘的抓取
  "executionStages": {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",    // 使用了索引掃描
      "keyPattern": {
        "status": 1,
        "createdAt": -1,
        "total": 1
      }
    }
  }
}
```