# 查詢優化與 EXPLAIN 分析 | Query Optimization & EXPLAIN Analysis

## Mental model｜心智模型

要掌握查詢優化，必須理解 MySQL 的 **Cost-Based Optimizer (CBO，基於成本的優化器)** 是如何運作的。優化不是魔法，而是協助優化器找到「成本最低」的路徑。

### 1. The Funnel Strategy (漏斗策略)
想像查詢執行是一個漏斗。你的目標是在漏斗的最上層（資料存取階段）就過濾掉絕大多數的資料，只讓極少數的資料流向漏斗下層（排序、分組、回傳）。
*   **Access (存取)**: 如何找到資料？（全表掃描 vs 索引查找）。這是優化的第一戰場。
*   **Filter (過濾)**: 找到資料後，有多少比例符合條件？
*   **Process (處理)**: 排序 (`ORDER BY`)、分組 (`GROUP BY`)。如果在記憶體或磁碟中做這些事（`Using filesort` / `Using temporary`），成本極高。

### 2. The Library Analogy (圖書館比喻)
*   **Clustered Index (Primary Key)**: 書架上實際排列的書籍。
*   **Secondary Index**: 圖書館的分類卡片櫃。卡片上有書名和位置（PK）。
*   **Covering Index**: 你要查的資訊（例如書名、作者）直接寫在卡片上，你根本**不需要**走到書架前拿書（回表，Table lookup）。這是最高效的查詢。
*   **Filesort**: 把書架上的書全部丟到地上，然後人工重新排列。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Decoding `EXPLAIN` Output (解讀 EXPLAIN)
不要只看有沒有用索引，要看 `type` 和 `Extra`。

#### The `type` Hierarchy (由快到慢)
目標應鎖定在 `range` 以上。
1.  **`system` / `const`**: 只有一行匹配（PK 或 Unique Key 查找）。**最快**。
2.  **`eq_ref`**: Join 時，被驅動表使用 PK 或 Unique Key。
3.  **`ref`**: 使用非唯一索引（Non-Unique Index）。
4.  **`range`**: 索引範圍掃描（`>`, `<`, `BETWEEN`, `IN`）。**這是大多數查詢應達到的標準**。
5.  **`index`**: 全索引掃描 (Full Index Scan)。雖然比全表掃描快（因為索引比較小），但仍然很慢。通常發生在 `COUNT(*)` 或排序時。
6.  **`ALL`**: 全表掃描 (Full Table Scan)。**效能殺手**，除非表非常小。

#### The Critical `Extra` Information
*   **`Using index` (Good)**: 覆蓋索引 (Covering Index)。不需要回表讀取資料行，效能極佳。
*   **`Using where` (Neutral/Bad)**: 存儲引擎讀出資料後，Server 層還需要再次過濾。暗示索引過濾性不足。
*   **`Using filesort` (Bad)**: 無法利用索引順序進行排序，需要額外的排序緩衝區。應透過複合索引解決。
*   **`Using temporary` (Very Bad)**: 需要建立臨時表來處理查詢（常見於 `GROUP BY` 或 `DISTINCT`）。

### 2. Optimizing Pagination (分頁優化)
傳統的 `LIMIT offset, N` 在 `offset` 很大時會極慢，因為 MySQL 必須讀取 `offset + N` 筆資料然後丟棄前 `offset` 筆。

*   **Pattern**: **Keyset Pagination (Seek Method)**
    *   *Bad*: `SELECT * FROM logs LIMIT 1000000, 10`
    *   *Good*: `SELECT * FROM logs WHERE id > 1000000 LIMIT 10` (利用上次查詢的最後一個 ID)。

### 3. `EXPLAIN ANALYZE` (MySQL 8.0+)
傳統 `EXPLAIN` 只是「估算」成本。MySQL 8.0 引入了 `EXPLAIN ANALYZE`，它會**實際執行** SQL 並測量時間。
*   **Use case**: 當 `EXPLAIN` 說會用索引，但查詢還是很慢時，用 `ANALYZE` 查看實際花費時間是在 Scanning 階段還是在 Returning rows 階段。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Function on Column" Trap (對欄位使用函數)
這是最常見導致索引失效的原因（Non-SARGable queries）。
*   **Anti-pattern**: `WHERE YEAR(created_at) = 2023`
    *   MySQL 必須對每一行計算 `YEAR()`，無法使用索引樹導航。
*   **Fix**: `WHERE created_at BETWEEN '2023-01-01' AND '2023-12-31 23:59:59'`

### 2. Implicit Type Conversion (隱式型別轉換)
*   **Anti-pattern**: `SELECT * FROM users WHERE phone_number = 912345678`
    *   如果 `phone_number` 是 `VARCHAR`，但輸入是 `INT`，MySQL 會把欄位轉成數字來比較，導致全表掃描。
*   **Fix**: 確保比較雙方的型別一致：`WHERE phone_number = '912345678'`

### 3. `SELECT *` Abuse (濫用 SELECT *)
*   **Pitfall**: 即使你有完美的索引 `(status, created_at)`，如果你 `SELECT *`，MySQL 發現需要讀取其他欄位（如 `description`），可能會判斷「回表成本太高」而放棄使用索引，直接全表掃描。
*   **Fix**: 只選取需要的欄位，增加使用 **Covering Index** 的機會。

### 4. Leading Wildcard `LIKE` (前綴模糊查詢)
*   **Anti-pattern**: `WHERE name LIKE '%john'`
    *   B-Tree 索引是依賴前綴排序的，前面是通配符無法使用索引。
*   **Fix**: 考慮使用 Full-Text Search 或 ElasticSearch；如果是後綴匹配需求，可考慮存儲反轉字串。

---

## Checklists & workflows｜檢查清單與流程

### Optimization Workflow (優化流程)
1.  **Identify**: 透過 Slow Query Log 或監控工具 (PMM, Datadog) 抓出慢查詢。
2.  **Analyze**: 使用 `EXPLAIN` (或 `EXPLAIN ANALYZE`) 查看執行計畫。
3.  **Hypothesize**: 判斷瓶頸是 I/O (掃描太多行) 還是 CPU (排序/計算)。
4.  **Optimize**: 修改 SQL 寫法或調整索引。
5.  **Verify**: 再次執行 `EXPLAIN` 確認 `rows` 減少或 `type` 變好。

### Code Review Checklist (代碼審查清單)
- [ ] **SARGable**: `WHERE` 子句中的欄位是否乾淨（沒有被函數包裹）？
- [ ] **Index Usage**: `EXPLAIN` 的 `type` 是否至少是 `range` 或 `ref`？
- [ ] **Rows Examined**: `rows` (掃描行數) 與實際回傳行數的比例是否合理？（理想是 1:1 到 10:1，如果是 10000:1 代表過濾效率極差）。
- [ ] **No Filesort**: 是否避免了 `Using filesort`？（特別是高併發查詢）。
- [ ] **Data Types**: `JOIN` 的欄位型別與編碼 (Collation) 是否完全一致？
- [ ] **Deterministic**: `ORDER BY` 是否包含唯一鍵？（避免分頁時資料跳動）。

---

## Real-world examples｜實戰案例

### Scenario 1: Eliminating `Using filesort` with Composite Index
**情境**: 查詢某個用戶最近的訂單。
**Schema**: `orders (id, user_id, created_at, total)`
**Index**: `idx_user (user_id)`

**Bad Query**:
```sql
SELECT id, total FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10;
```
**EXPLAIN Analysis**:
*   `type`: `ref` (使用了 `idx_user`)
*   `Extra`: `Using index condition; Using filesort`
*   **問題**: 雖然快速找到了 `user_id=123` 的訂單，但 MySQL 必須將這些訂單載入記憶體重新依 `created_at` 排序。

**Optimization**:
建立複合索引 `idx_user_date (user_id, created_at)`。

**Result**:
*   `Extra`: `Using where` (甚至可能 `Backward index scan`)。
*   **原理**: 索引中，`user_id=123` 的資料已經按照 `created_at` 排好序了。MySQL 直接讀取最後 10 筆即可，無需排序。

---

### Scenario 2: Optimizing `OR` Conditions
**情境**: 找出狀態為 'PENDING' **或者** 創建時間在昨天的訂單。

**Bad Query**:
```sql
SELECT * FROM orders WHERE status = 'PENDING' OR created_at > '2023-10-01';
```
**Analysis**:
*   即使 `status` 和 `created_at` 都有索引，MySQL 通常很難同時利用兩個索引（除非觸發 Index Merge，但效率不穩）。通常會退化成全表掃描。

**Optimization (Rewrite to UNION)**:
```sql
SELECT * FROM orders WHERE status = 'PENDING'
UNION
SELECT * FROM orders WHERE created_at > '2023-10-01';
```
**原理**: 將一個複雜查詢拆成兩個簡單查詢。每個查詢都能完美利用各自的索引 (`idx_status` 和 `idx_created_at`)。`UNION` 會自動去重（如果不需要去重，用 `UNION ALL` 更快）。

---

### Scenario 3: The "Derived Table" Optimization for Deep Pagination
**情境**: 表非常大，需要跳到第 100 萬頁。

**Bad Query**:
```sql
-- 掃描 1,000,010 行，丟棄前 1,000,000 行，回表讀取 10 行所有欄位
SELECT * FROM users ORDER BY created_at LIMIT 1000000, 10;
```

**Optimization (Late Row Lookups)**:
```sql
SELECT t1.*
FROM users t1
JOIN (
    -- 只在索引樹上掃描 id，不回表，速度快很多
    SELECT id FROM users ORDER BY created_at LIMIT 1000000, 10
) t2 ON t1.id = t2.id;
```
**原理**:
1.  子查詢 (Derived Table) 利用 `Covering Index` (假設 `created_at` 有索引) 快速找到目標的 10 個 `id`。
2.  外層查詢只需要根據這 10 個 `id` 回表讀取完整資料。
3.  大幅減少了隨機 I/O (Random I/O) 的次數。