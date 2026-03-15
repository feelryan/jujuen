# Schema 設計與索引優化實戰 / Practical Schema Design & Indexing Strategies

## Mental model｜心智模型

在深入 SQL 指令之前，我們需要建立正確的資料庫設計心智模型。Schema 設計不是單純的「畫出 ER Diagram」，而是對「資料存取模式（Access Patterns）」的預測與權衡。

### 1. 存取模式決定結構 (Access Patterns Drive Structure)
不要只根據實體（Entities）的關係來設計 Schema，要根據**應用程式如何讀寫這些資料**來設計。
- **Write-Heavy (寫入密集)**：傾向高度正規化 (Normalization)，減少寫入時的鎖定與資料冗餘，寫入快但讀取時需要 Join。
- **Read-Heavy (讀取密集)**：傾向適度反正規化 (Denormalization)，用空間換取時間，減少 Join，讀取快但寫入時需維護多份資料一致性。

### 2. 索引是「有序的副本」 (Indexes are Sorted Redundancy)
索引不是魔法，它本質上是**另一張排序過的表**。
- **Trade-off**：每增加一個索引，讀取查詢（SELECT）變快，但寫入操作（INSERT/UPDATE/DELETE）變慢（因為要同時更新主表和索引表）。
- **Cost**：索引佔用磁碟空間與記憶體（Buffer Pool）。

### 3. B-Tree 的電話簿法則 (The Phonebook Analogy)
大多數關聯式資料庫預設使用 B-Tree 索引。想像一本電話簿是按 `[姓氏, 名字]` 排序的：
- 找「姓王」的人很快（Range Scan）。
- 找「姓王且名大明」的人很快。
- **但是**，找「名大明」的人（忽略姓氏）非常慢，因為你必須翻完整本電話簿（Full Table Scan）。這就是 **最左前綴原則 (Leftmost Prefix Rule)**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Primary Key 選擇策略：UUID vs Auto-Increment vs TSID
這是最常見的爭論，現代系統建議採用 **混合策略**。

| 策略 | 優點 (Pros) | 缺點 (Cons) | 最佳使用場景 |
| :--- | :--- | :--- | :--- |
| **Auto-Increment (Integer/BigInt)** | 佔用空間小、插入效能最高（順序寫入）、對 B-Tree 友善。 | **安全性風險**（容易被遍歷爬取）、分庫分表（Sharding）時 ID 衝突難處理。 | 內部關聯表、不需要對外暴露 ID 的表。 |
| **Random UUID (v4)** | 全局唯一、適合分散式系統、客戶端可生成。 | **效能殺手**。無序性導致 Clustered Index 頻繁發生 Page Splits（頁分裂），造成磁碟碎片與 IO 浪費。 | **絕對不要**用作 Clustered Primary Key。 |
| **Time-Sorted ID (UUID v7 / ULID / TSID)** | **推薦方案**。結合了 UUID 的唯一性與時間的順序性。 | 實作稍微複雜（需 Library 支援），空間比 Int 大。 | **現代分散式系統的預設首選**。 |

### 2. 反正規化模式 (Denormalization Patterns)
當 `JOIN` 成為效能瓶頸時，有策略地違反正規化原則。

- **Parent-Child Summary**：在 Parent 表（如 `posts`）增加一個 `comments_count` 欄位，避免每次列表顯示都要 `COUNT(*)`。
- **Snapshotting (快照)**：在 `orders` 表中直接儲存下單當下的 `product_price` 和 `shipping_address`，而不是只存 ID 關聯回去。這不僅是為了效能，更是為了**業務正確性**（因為商品價格與地址未來可能變更）。

### 3. 索引設計黃金法則
- **覆蓋索引 (Covering Index)**：
  如果你的查詢是 `SELECT name, age FROM users WHERE age = 30`，建立一個 `(age, name)` 的複合索引。資料庫可以直接從索引樹中拿到資料，完全不需要回查主表（Heap），效能提升巨大。
- **複合索引順序 (Composite Index Order)**：
  將**區分度（Cardinality）最高**或**最常用於等值查詢（Equality）**的欄位放在最左邊。
  - 查詢：`WHERE status = 'active' AND user_id = 12345`
  - 索引建議：`INDEX(user_id, status)` 優於 `INDEX(status, user_id)`，因為 `user_id` 能過濾掉更多資料。

### 4. Partial Indexes (部分索引)
如果你的表有 1000 萬筆資料，但查詢只關心 `status = 'pending'` 的 1 萬筆任務：
- **Do**: `CREATE INDEX idx_pending_tasks ON tasks (created_at) WHERE status = 'pending';`
- **Benefit**: 索引體積極小，維護成本低，查詢速度極快。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Kitchen Sink" Index (大雜燴索引)
- **Bad**: 為了涵蓋所有查詢，建立了一個包含 5-6 個欄位的巨大索引，或者對每個欄位都單獨建索引。
- **Consequence**: 寫入效能崩潰，資料庫優化器（Optimizer）可能因為選擇太多而選錯索引。

### 2. 隱式轉型殺手 (Implicit Casting)
- **Bad**: 欄位是 `VARCHAR`，查詢卻用 `WHERE phone_number = 911` (數字)。
- **Consequence**: 資料庫必須將每一行的字串轉成數字才能比較，導致 **索引失效 (Full Table Scan)**。
- **Fix**: 始終確保查詢參數類型與 Schema 定義一致。

### 3. Leading Wildcard Search
- **Bad**: `WHERE name LIKE '%john%'`。
- **Consequence**: B-Tree 無法處理開頭是通配符的查詢，必定全表掃描。
- **Fix**: 改用 Full-Text Search (如 PostgreSQL `tsvector` 或 Elasticsearch)，或僅使用後綴通配符 `LIKE 'john%'`。

### 4. 使用 JSON 欄位逃避 Schema 設計
- **Bad**: 把大量核心業務邏輯欄位塞進 `JSON/JSONB` 欄位，然後試圖在裡面做複雜過濾。
- **Consequence**: 雖然現代 DB 支援 JSON 索引，但效能與儲存成本通常高於標準欄位，且失去了強型別約束。
- **Rule**: JSON 欄位應用於「屬性不固定」或「僅供讀取展示」的資料，而非核心查詢條件。

---

## Checklists & workflows｜檢查清單與流程

### Schema Design Checklist (設計階段)
- [ ] **PK Strategy**: 是否已評估 ID 生成策略？(對外公開用 UUIDv7/HashID，對內用 Int/BigInt)。
- [ ] **Data Types**: 是否使用了最合適的型別？(例如：枚舉狀態用 `ENUM` 或 `TinyInt` 而非 `VARCHAR`；金額用 `DECIMAL` 而非 `FLOAT`)。
- [ ] **Nullability**: 欄位是否真的需要 `NULL`？(NULL 會增加索引複雜度，盡量設 `NOT NULL` 並給預設值)。
- [ ] **Foreign Keys**: 所有外鍵欄位是否都已建立索引？(防止 Join 效能低落與死鎖)。
- [ ] **Concurrency**: 是否需要 `version` 欄位來處理樂觀鎖 (Optimistic Locking)？

### Index Optimization Workflow (優化階段)
1. **Identify**: 開啟 Slow Query Log，找出執行時間 > 200ms 的查詢。
2. **Analyze**: 對該查詢執行 `EXPLAIN (ANALYZE, BUFFERS)` (PostgreSQL) 或 `EXPLAIN FORMAT=JSON` (MySQL)。
3. **Check Scan Type**:
   - 看到 `Seq Scan` / `ALL` (全表掃描)？ -> 檢查 `WHERE` 條件是否缺索引。
   - 看到 `Filesort` / `Temporary`？ -> 檢查 `ORDER BY` 是否能利用索引排序。
4. **Verify Cardinality**: 索引欄位的區分度是否足夠高？(例如在 `gender` 欄位建 B-Tree 索引通常沒用)。
5. **Test**: 在 Staging 環境建立索引並重跑 `EXPLAIN`，確認 Cost 降低且真的用到了索引。

---

## Real-world examples｜實戰案例

### Case 1: E-commerce Order List Optimization (反正規化應用)
**情境**：使用者要看自己的歷史訂單列表，包含「訂單號、總金額、第一項商品名稱、下單時間」。
**原始設計**：
- `orders` (id, user_id, created_at)
- `order_items` (order_id, product_name, price)
- **問題**：列表頁需要 `JOIN` 並 `GROUP BY` 取第一筆商品，資料量大時極慢。

**優化設計**：
- 在 `orders` 表增加冗餘欄位：`first_product_name`, `total_amount`。
- 寫入訂單時計算好填入。
- **結果**：查詢變成單表 `SELECT * FROM orders WHERE user_id = ?`，速度提升 10 倍以上。

### Case 2: The "UUID v4" Trap (PK 選擇)
**情境**：一個高頻寫入的 Log 系統，使用標準 UUID (v4) 作為 Primary Key。
**問題**：隨著資料量超過 Buffer Pool 大小，INSERT IOPS 飆升，CPU 等待 IO 時間過長。
**原因**：UUID v4 是隨機的，新插入的資料會隨機散落在 B-Tree 的各個 Leaf Page，導致大量的 Random Disk I/O 和 Page Splits。
**解決**：
- 改用 **UUID v7** (時間排序的 UUID)。
- 資料寫入變為「類順序寫入 (Append-mostly)」，Page Split 大幅減少，Buffer Pool 命中率提升。

### Case 3: Composite Index for Filtering & Sorting (索引順序)
**情境**：API 需求是「查詢某部門(dept_id)最近加入的員工，按入職日(joined_at)倒序排列」。
**查詢**：`SELECT * FROM employees WHERE dept_id = 5 ORDER BY joined_at DESC LIMIT 10;`

**錯誤嘗試**：
- Index A: `(joined_at)` -> 資料庫可以快速排序，但要掃描所有部門。
- Index B: `(dept_id)` -> 資料庫可以快速過濾部門，但剩下的資料需要 `Filesort` (記憶體內排序)。

**最佳實踐**：
- Index C: `(dept_id, joined_at)`
- **原理**：B-Tree 先按 `dept_id` 聚在一起，在相同的 `dept_id` 內部，資料已經按 `joined_at` 排好序了。資料庫可以直接定位到該部門的最後一筆，往回讀 10 筆即可，完全不需要額外排序。