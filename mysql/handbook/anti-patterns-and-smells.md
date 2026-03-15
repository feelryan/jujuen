# 常見反模式與效能陷阱 | Common Anti-Patterns & Performance Pitfalls / Common Anti-Patterns & Performance Pitfalls

## Mental model｜心智模型

在優化 MySQL 效能時，最核心的心智模型是 **「資料存取成本比率」 (Data Access Cost Ratio)**。

想像 MySQL 是一位圖書館管理員：
1.  **理想情況 (Index Lookup)**：你給他一個索引號碼，他直接走到特定書架拿出那一本書。
2.  **反模式情況 (Full Table Scan)**：你告訴他「找一本封面是紅色的書」，他必須從第一排書架走到最後一排，把每一本書拿起來看封面。

**關鍵指標：`Rows Examined` vs `Rows Returned`**
- **健康狀態**：掃描行數 (Examined) 與 返回行數 (Returned) 的比例接近 1:1 或 1:10 以內。
- **病態狀態**：為了回傳 10 筆資料，掃描了 100,000 行資料（Ratio 10,000:1）。

所有的反模式（Anti-patterns），本質上都是強迫 MySQL 做了不必要的「翻書」動作，或是讓索引（目錄）失效。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Keyset Pagination (Seek Method)｜游標分頁法
針對「深分頁 (Deep Pagination)」問題的最佳解法。不要使用 `OFFSET` 丟棄前面的資料，而是記住上一頁最後一筆資料的位置（Cursor）。

- **Pattern**: `WHERE id < last_seen_id ORDER BY id DESC LIMIT 20`
- **Why**: 複雜度從 O(N) 降為 O(1) 或 O(log N)，無論翻到第幾頁，速度都一樣快。

### 2. Batch Loading (Application-side Join)｜應用層批次查詢
解決 N+1 問題的標準模式。不要在迴圈中查詢資料庫，而是先收集 ID，一次查回。

- **Pattern**:
    1. 取得所有 `user_ids`。
    2. `SELECT * FROM profiles WHERE user_id IN (1, 2, 3...)`。
    3. 在 Application 記憶體中組裝資料。
- **Why**: 減少 Network Round-trip 是提升應用程式回應速度最有效的方法之一。

### 3. Covering Index Optimization｜覆蓋索引優化
如果查詢只需要索引中的欄位，MySQL 就不需要回頭去查主資料表（回表，Clustered Index Lookup）。

- **Pattern**: 建立索引 `(category, status, id)` 來服務 `SELECT id FROM products WHERE category='A' AND status='active'`。
- **Why**: 將隨機 I/O (Random I/O) 轉變為順序 I/O (Sequential I/O)，極大提升效能。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Implicit Conversion｜隱式型別轉換
這是最隱蔽的「索引殺手」。當查詢條件的資料型別與欄位定義不一致時，MySQL 無法使用索引，會退化成全表掃描 (Full Table Scan)。

- **Bad**: `SELECT * FROM users WHERE phone = 1234567890;` (若 `phone` 是 `VARCHAR`)
- **Consequence**: MySQL 會將字串欄位轉為數字進行比較，導致無法使用 B-Tree 索引。
- **Fix**: 確保傳入參數型別與 Schema 一致，例如使用字串 `'1234567890'`。

### 2. Functions on Indexed Columns｜在索引欄位上使用函數
對索引欄位進行運算或包裝函數，會導致索引失效。

- **Bad**: `WHERE YEAR(created_at) = 2023`
- **Bad**: `WHERE price + 100 > 500`
- **Consequence**: MySQL 必須算出每一行的值才能比較，無法利用 B-Tree 的有序性。
- **Fix**: 將運算移到等號右邊。
    - `WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'`
    - `WHERE price > 400`

### 3. Leading Wildcard Search｜前綴模糊搜尋
B-Tree 索引是按照前綴排序的（類似電話簿）。如果開頭是萬用字元，索引就無效。

- **Bad**: `LIKE '%keyword%'` 或 `LIKE '%keyword'`
- **Consequence**: 全表掃描。
- **Fix**:
    - 僅使用後綴模糊：`LIKE 'keyword%'` (可以使用索引)。
    - 若必須全文檢索，請使用 MySQL Full-Text Index 或外部引擎 (Elasticsearch)。

### 4. The "SELECT *" Habit｜濫用 SELECT *
選取所有欄位看似方便，但在生產環境是大忌。

- **Pitfall**:
    - **Covering Index 失效**：強迫 MySQL 進行回表操作。
    - **頻寬浪費**：若包含 `TEXT` 或 `BLOB` 欄位，會消耗大量 I/O 與網路頻寬。
    - **Schema 耦合**：程式碼依賴隱含的欄位順序或存在。

### 5. Deep Pagination with OFFSET｜深分頁陷阱
`LIMIT 1000000, 10` 意味著 MySQL 必須讀取 1,000,010 行資料，然後丟棄前 1,000,000 行。

- **Bad**: `LIMIT 1000000, 10`
- **Consequence**: 越往後翻頁，查詢越慢，對 DB IOPS 造成巨大壓力。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或部署前，請使用此清單檢查 SQL 變更：

### Code Review Checklist
- [ ] **EXPLAIN Check**: 是否對所有關鍵查詢執行過 `EXPLAIN`？`type` 是否為 `ALL` (Full Table Scan)？
- [ ] **Type Matching**: `WHERE` 子句中的變數型別，是否與 DB Schema 定義完全一致（避免隱式轉型）？
- [ ] **No Functions on Left**: 是否有對欄位進行函數運算？（如 `DATE(col)` 或 `LOWER(col)`）
- [ ] **Wildcard Placement**: `LIKE` 查詢是否將 `%` 放在了最前面？
- [ ] **Loop Query**: 是否在 `for` / `foreach` 迴圈中執行 SQL 查詢？（N+1 detection）
- [ ] **Pagination Strategy**: 如果資料量可能超過 10 萬筆，是否避免了 `OFFSET` 分頁？
- [ ] **Column Selection**: 是否明確指定了需要的欄位，而不是 `SELECT *`？

### Troubleshooting Workflow (當查詢變慢時)
1.  **Identify**: 開啟 Slow Query Log 或使用監控工具 (PMM, Datadog) 抓出慢查詢。
2.  **Analyze**: 執行 `EXPLAIN FORMAT=JSON <query>`。
3.  **Check Key Usage**: 查看 `key` 欄位是否為 `NULL`？`key_len` 是否符合預期？
4.  **Check Rows**: 比較 `rows` (估計掃描行數) 與實際結果行數。
5.  **Optimize**:
    - 添加或修改索引。
    - 重寫 SQL (移除函數、改寫分頁)。
    - 調整應用層邏輯 (Caching, Batching)。

---

## Real-world examples｜實戰案例

### Example 1: The Silent Killer - Implicit Conversion (隱式轉型)

**Scenario**: 使用者登入系統，透過手機號碼查詢。
**Schema**: `phone_number` is `VARCHAR(20)`, Indexed.

**❌ Anti-pattern Code (Python/ORM example)**:
```python
# 傳入了整數 (Integer)，但資料庫欄位是字串
db.execute("SELECT * FROM users WHERE phone_number = %s", (912345678,))
```
**Result**:
MySQL 必須將 DB 裡的每一行 `phone_number` 字串轉成數字來跟 `912345678` 比對。
- `EXPLAIN type`: **ALL** (Full Table Scan)
- `key`: **NULL**

**✅ Best Practice**:
```python
# 強制轉型為字串 (String)
db.execute("SELECT * FROM users WHERE phone_number = %s", ("912345678",))
```
**Result**:
- `EXPLAIN type`: **ref** or **const**
- `key`: `idx_phone_number`

### Example 2: Deep Pagination Optimization (深分頁優化)

**Scenario**: 後台管理系統，需要匯出第 10,000 頁的訂單記錄。

**❌ Anti-pattern (OFFSET)**:
```sql
SELECT * FROM orders 
WHERE status = 'completed'
ORDER BY id ASC 
LIMIT 100000, 20;
```
**Execution**: MySQL 讀取 100,020 行索引與資料，丟掉前 10 萬行。耗時可能超過 2-5 秒。

**✅ Best Practice (Keyset / Seek Method)**:
假設前端或上一頁請求回傳了最後一筆 ID 為 `450000`。

```sql
SELECT * FROM orders 
WHERE status = 'completed' 
  AND id > 450000 
ORDER BY id ASC 
LIMIT 20;
```
**Execution**: MySQL 直接跳到 ID 450000 的位置，只讀取 20 行。耗時 < 10ms。

### Example 3: N+1 Query Problem (N+1 問題)

**Scenario**: 顯示文章列表及其作者名稱。

**❌ Anti-pattern**:
```python
posts = db.query("SELECT * FROM posts LIMIT 10")
for post in posts:
    # 每一篇文章都觸發一次額外的查詢
    author = db.query("SELECT * FROM users WHERE id = %s", (post.author_id,))
    print(post.title, author.name)
```
**Total Queries**: 1 (List) + 10 (Authors) = 11 Queries.

**✅ Best Practice (Eager Loading / IN clause)**:
```python
posts = db.query("SELECT * FROM posts LIMIT 10")
author_ids = [p.author_id for p in posts]

# 一次查回所有作者
authors = db.query("SELECT * FROM users WHERE id IN %s", (author_ids,))

# 在 Application 層做 Map 組合
author_map = {a.id: a for a in authors}
for post in posts:
    print(post.title, author_map[post.author_id].name)
```
**Total Queries**: 1 + 1 = 2 Queries.