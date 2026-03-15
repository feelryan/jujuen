# Chapter 04: Query Optimization and EXPLAIN Analysis
# 第四章：查詢優化與執行計畫分析

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For Senior Engineers, query optimization is not just about "adding an index." It requires a deep understanding of how the MySQL Optimizer calculates costs and chooses an execution plan. This chapter focuses on the transition from "guessing" to "engineering" query performance.
對於資深工程師而言，查詢優化不僅僅是「加個索引」。它需要深入理解 MySQL 優化器（Optimizer）如何計算成本並選擇執行計畫。本章致力於將查詢效能從「猜測」轉變為「工程化」的分析過程。

By the end of this chapter, you should be able to:
完成本章後，你應該能夠：

1.  **Decipher `EXPLAIN` Output**: Interpret critical columns like `type`, `key_len`, `ref`, and `Extra` to identify performance bottlenecks (e.g., Filesort, Temporary Tables).
    **解讀 `EXPLAIN` 輸出**：詮釋 `type`、`key_len`、`ref` 與 `Extra` 等關鍵欄位，以識別效能瓶頸（如 Filesort、臨時表）。
2.  **Understand the Cost Model**: Explain how MySQL decides between a Full Table Scan and an Index Scan based on IO and CPU costs.
    **理解成本模型（Cost Model）**：解釋 MySQL 如何基於 IO 與 CPU 成本，在全表掃描與索引掃描之間做出決策。
3.  **Optimize Complex Queries**: Apply techniques like Index Condition Pushdown (ICP), Covering Indexes, and Deferred Joins to optimize complex `JOIN`s, `GROUP BY`, and Pagination.
    **優化複雜查詢**：應用索引下推（ICP）、覆蓋索引（Covering Index）與延遲關聯（Deferred Join）等技術來優化複雜的 `JOIN`、`GROUP BY` 與分頁查詢。
4.  **Utilize Advanced Tools**: Use `EXPLAIN ANALYZE` (MySQL 8.0+) and Optimizer Trace to debug why the optimizer chose a specific plan.
    **使用進階工具**：利用 `EXPLAIN ANALYZE` (MySQL 8.0+) 與 Optimizer Trace 來除錯優化器為何選擇特定的執行計畫。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Optimizer is a Cost Calculator
### 2.1 優化器是一台成本計算機

**Mental Model:**
Think of the MySQL Optimizer as a travel agent trying to find the cheapest route. It doesn't care about the "shortest distance" (number of rows) directly; it cares about the "total cost" (CPU cycles + Disk I/O).
**心智模型：**
將 MySQL 優化器想像成一個試圖尋找最便宜路線的旅行社代理人。它並不直接關心「最短距離」（行數），而是關心「總成本」（CPU 週期 + 磁碟 I/O）。

*   **Cost = Server Cost (CPU) + Engine Cost (IO)**
*   **Cost = 伺服器成本 (CPU) + 引擎成本 (IO)**

Sometimes, a Full Table Scan (sequential read) is cheaper than an Index Scan (random read) if the index selectivity is poor (e.g., fetching > 20-30% of the table).
有時，如果索引的選擇性很差（例如讀取超過 20-30% 的資料表），全表掃描（順序讀取）會比索引掃描（隨機讀取）更便宜。

### 2.2 The Hierarchy of Access Methods (`type`)
### 2.2 存取方法的層級 (`type`)

In `EXPLAIN`, the `type` column indicates how MySQL finds rows. You must memorize the efficiency hierarchy (best to worst):
在 `EXPLAIN` 中，`type` 欄位指出 MySQL 如何找到資料列。你必須記住這個效率層級（由好到壞）：

1.  **system / const**: Primary Key or Unique Key lookup on a constant (at most 1 row).
    **system / const**：主鍵或唯一鍵的常數查找（最多 1 列）。
2.  **eq_ref**: Join using Primary Key or Unique Key (1 row per join).
    **eq_ref**：使用主鍵或唯一鍵進行關聯（每次關聯 1 列）。
3.  **ref**: Non-unique index lookup or prefix of unique index.
    **ref**：非唯一索引查找或唯一索引的前綴查找。
4.  **range**: Index range scan (e.g., `BETWEEN`, `>`, `<`, `IN`).
    **range**：索引範圍掃描（例如 `BETWEEN`、`>`、`<`、`IN`）。
5.  **index**: Full Index Scan (scanning the entire B+ Tree leaf nodes, usually for Covering Index).
    **index**：全索引掃描（掃描整個 B+ Tree 葉節點，通常用於覆蓋索引）。
6.  **ALL**: Full Table Scan (scanning the Clustered Index / data file).
    **ALL**：全表掃描（掃描聚簇索引 / 資料檔）。

### 2.3 The "Extra" Column: The Devil is in the Details
### 2.3 "Extra" 欄位：魔鬼藏在細節裡

*   **Using index**: Good. Covering Index used. No need to touch the table data (heap).
    **Using index**：好。使用了覆蓋索引。不需要回表讀取資料。
*   **Using index condition**: Good. Index Condition Pushdown (ICP) is active. Filtering happens at the storage engine level.
    **Using index condition**：好。啟用了索引下推（ICP）。過濾發生在存儲引擎層。
*   **Using where**: Neutral/Bad. Filtering happens at the Server layer (after fetching rows from the engine).
    **Using where**：中性/壞。過濾發生在 Server 層（從引擎獲取資料後）。
*   **Using filesort**: Bad. MySQL cannot use an index for sorting and must perform a sort pass (memory or disk).
    **Using filesort**：壞。MySQL 無法利用索引進行排序，必須執行額外的排序過程（記憶體或磁碟）。
*   **Using temporary**: Very Bad. An intermediate table is created (e.g., for `GROUP BY` or `DISTINCT`).
    **Using temporary**：非常壞。建立了一個中間臨時表（例如用於 `GROUP BY` 或 `DISTINCT`）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Impact on Microservices & Latency
### 3.1 對微服務與延遲的影響

In a microservices architecture, a single slow query in a core service (e.g., User Service, Inventory Service) can cause cascading failures (backpressure).
在微服務架構中，核心服務（如用戶服務、庫存服務）中的單一慢查詢可能導致級聯故障（背壓）。

*   **CPU Saturation**: Queries with `type: ALL` or complex `Using filesort` consume excessive CPU, blocking other lightweight queries.
    **CPU 飽和**：`type: ALL` 或複雜 `Using filesort` 的查詢會消耗過多 CPU，阻塞其他輕量級查詢。
*   **Buffer Pool Pollution**: Large scans (Full Table Scan) can evict hot data from the Buffer Pool, degrading the performance of the entire instance.
    **Buffer Pool 污染**：大範圍掃描（全表掃描）可能將熱點資料從 Buffer Pool 中驅逐，導致整個實例的效能下降。

### 3.2 Schema Design vs. Query Optimization
### 3.2 Schema 設計 vs. 查詢優化

Often, query optimization is blocked by poor schema design.
通常，查詢優化會受阻於糟糕的 Schema 設計。

*   **Denormalization**: In high-read scenarios, joining 5+ tables is unsustainable. Denormalizing data (e.g., storing `user_name` in the `orders` table) avoids `JOIN`s and allows simpler index usage.
    **反正規化**：在高讀取場景下，關聯 5 個以上的表是不可持續的。反正規化資料（例如在 `orders` 表中存儲 `user_name`）可避免 `JOIN` 並允許更簡單的索引使用。
*   **Vertical Partitioning**: Moving large text columns (BLOB/TEXT) to a separate table keeps the main table's rows small, allowing more rows to fit in the Buffer Pool and reducing IO for scans.
    **垂直分割**：將大型文字欄位（BLOB/TEXT）移至獨立的表，可保持主表資料列較小，讓更多列能放入 Buffer Pool，並減少掃描時的 IO。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Optimizing a "Top Spenders" Dashboard
### 場景：優化「最高消費用戶」儀表板

**Context:** An E-commerce system needs to display the top 10 users by total spending within a specific date range.
**背景：** 一個電商系統需要顯示在特定日期範圍內，總消費額最高的前 10 名用戶。

**Table Structure (Simplified):**
**資料表結構（簡化）：**

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2),
    created_at DATETIME,
    KEY idx_user (user_id),
    KEY idx_date (created_at)
);
```

### 4.1 The Naive Approach
### 4.1 直觀的做法

```sql
SELECT user_id, SUM(amount) as total_spent
FROM orders
WHERE created_at BETWEEN '2023-01-01' AND '2023-01-31'
GROUP BY user_id
ORDER BY total_spent DESC
LIMIT 10;
```

**Analysis (EXPLAIN):**
**分析 (EXPLAIN)：**

*   **type**: `range` (on `idx_date`).
*   **Extra**: `Using index condition; Using temporary; Using filesort`.
*   **Problem**: MySQL uses `idx_date` to filter rows. However, it must create a **temporary table** to group by `user_id` and then perform a **filesort** to order by the calculated `total_spent`. If the date range covers 1 million rows, this is extremely slow.
*   **問題**：MySQL 使用 `idx_date` 過濾資料。然而，它必須建立**臨時表**來依 `user_id` 分組，然後執行**文件排序**來依計算出的 `total_spent` 排序。如果日期範圍涵蓋 100 萬筆資料，這會非常慢。

### 4.2 Optimization Attempt 1: Covering Index
### 4.2 優化嘗試 1：覆蓋索引

We create a composite index to cover the `WHERE` and `GROUP BY` clauses, and include the `amount` to avoid accessing the table heap.
我們建立一個複合索引來覆蓋 `WHERE` 和 `GROUP BY` 子句，並包含 `amount` 以避免回表讀取。

```sql
ALTER TABLE orders ADD INDEX idx_date_user_amount (created_at, user_id, amount);
```

**Result:**
**結果：**
*   **Extra**: `Using where; Using index; Using temporary; Using filesort`.
*   **Improvement**: We avoided the table lookup (Random IO), which is huge. However, `Using temporary` and `filesort` remain because we are grouping by `user_id` but the index is sorted by `created_at` first.
*   **改進**：我們避免了回表（隨機 IO），這是巨大的進步。然而，`Using temporary` 和 `filesort` 仍然存在，因為我們依 `user_id` 分組，但索引是先依 `created_at` 排序的。

### 4.3 Optimization Attempt 2: Summary Table (System Design Solution)
### 4.3 優化嘗試 2：匯總表（系統設計解法）

For heavy aggregation queries, real-time calculation is often the bottleneck.
對於重度聚合查詢，即時計算通常是瓶頸。

**Solution:** Create a summary table `daily_user_stats` updated via ETL or events.
**解法：** 建立一個匯總表 `daily_user_stats`，透過 ETL 或事件更新。

```sql
CREATE TABLE daily_user_stats (
    day DATE,
    user_id INT,
    total_amount DECIMAL(10, 2),
    PRIMARY KEY (day, user_id)
);
```

Now the query scans significantly fewer rows.
現在查詢掃描的行數顯著減少。

### 4.4 Optimization Attempt 3: Deferred Join (for Pagination)
### 4.4 優化嘗試 3：延遲關聯（用於分頁）

If we need to join the `users` table to get names:
如果我們需要關聯 `users` 表來獲取姓名：

**Bad:**
```sql
SELECT u.name, o.amount
FROM orders o
JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC
LIMIT 100000, 10;
```
This fetches 100,010 rows, joins them all with `users`, sorts them, and discards the first 100,000.
這會抓取 100,010 列，全部與 `users` 關聯，排序，然後丟棄前 100,000 列。

**Good (Deferred Join):**
**好（延遲關聯）：**
```sql
SELECT u.name, o.amount
FROM (
    SELECT id FROM orders
    ORDER BY created_at DESC
    LIMIT 100000, 10
) as sub
JOIN orders o ON sub.id = o.id
JOIN users u ON o.user_id = u.id;
```
This uses the index on `orders` to find the 10 IDs first (Covering Index), and *then* performs the join only for those 10 rows.
這利用 `orders` 上的索引先找到 10 個 ID（覆蓋索引），*然後*只針對這 10 列執行關聯。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Functions on Indexed Columns
### 5.1 在索引欄位上使用函數

**Anti-pattern:**
**反模式：**
```sql
SELECT * FROM users WHERE YEAR(created_at) = 2023;
```
**Why it's bad:** This destroys the B-Tree search capability. MySQL must perform a Full Index Scan or Full Table Scan because the index stores the raw date, not the result of `YEAR()`.
**為何不好：** 這破壞了 B-Tree 的搜尋能力。MySQL 必須執行全索引掃描或全表掃描，因為索引存儲的是原始日期，而不是 `YEAR()` 的結果。

**Fix:**
**修正：**
```sql
SELECT * FROM users WHERE created_at BETWEEN '2023-01-01' AND '2023-12-31';
```

### 5.2 The `OR` Trap
### 5.2 `OR` 的陷阱

**Anti-pattern:**
**反模式：**
```sql
SELECT * FROM users WHERE email = '...' OR phone = '...';
```
**Why it's bad:** Even if both columns have indexes, MySQL often abandons them for a full scan unless it uses "Index Merge" (which is rarely efficient).
**為何不好：** 即使兩個欄位都有索引，MySQL 通常會放棄它們而進行全表掃描，除非它使用「索引合併」（Index Merge，這通常效率不高）。

**Fix:** Use `UNION ALL`.
**修正：** 使用 `UNION ALL`。
```sql
SELECT * FROM users WHERE email = '...'
UNION ALL
SELECT * FROM users WHERE phone = '...';
```

### 5.3 Ignoring `rows` vs. `filtered`
### 5.3 忽略 `rows` 與 `filtered`

**Pitfall:** Seeing `type: ref` and thinking the query is optimized.
**陷阱：** 看到 `type: ref` 就認為查詢已優化。

**Scenario:**
**場景：**
*   `rows`: 10,000
*   `filtered`: 1.00%
*   `Extra`: `Using where`

**Meaning:** MySQL read 10,000 rows from the engine, but the Server layer discarded 99% of them. This is a waste of IO and CPU. You need a better composite index to push the filter down to the engine.
**意義：** MySQL 從引擎讀取了 10,000 列，但 Server 層丟棄了 99%。這是 IO 和 CPU 的浪費。你需要一個更好的複合索引將過濾條件下推至引擎層。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How does MySQL choose between multiple indexes?
### Q1: MySQL 如何在多個索引之間做出選擇？

*   **Key Points:**
    *   Explain the **Cost Model** (IO cost + CPU cost).
    *   Mention **Statistics** (Cardinality). MySQL estimates the number of rows (using random dives into index pages).
    *   Discuss `Optimizer Trace` as a way to verify the decision process.
    *   Mention `FORCE INDEX` as a last resort but warn about its brittleness.
*   **回答要點：**
    *   解釋 **成本模型**（IO 成本 + CPU 成本）。
    *   提及 **統計資訊**（基數 Cardinality）。MySQL 估計行數（通過隨機探測索引頁面）。
    *   討論 `Optimizer Trace` 作為驗證決策過程的方法。
    *   提及 `FORCE INDEX` 作為最後手段，但需警告其脆弱性。

### Q2: Explain "Index Condition Pushdown" (ICP).
### Q2: 解釋「索引下推」（ICP）。

*   **Key Points:**
    *   Before ICP (MySQL < 5.6), if an index covered part of the `WHERE` clause, the engine fetched the row, and the Server layer checked the rest.
    *   With ICP, the engine checks *all* indexable parts of the `WHERE` clause before fetching the table row.
    *   Reduces **IO operations** (fewer table lookups).
    *   Identified by `Using index condition` in `EXPLAIN`.
*   **回答要點：**
    *   在 ICP 之前（MySQL < 5.6），如果索引覆蓋了部分 `WHERE` 子句，引擎會取出該列，由 Server 層檢查剩餘條件。
    *   有了 ICP，引擎在取出資料列之前會檢查 *所有* 可索引的 `WHERE` 條件。
    *   減少 **IO 操作**（更少的回表）。
    *   在 `EXPLAIN` 中以 `Using index condition` 識別。

### Q3: How do you optimize deep pagination (e.g., Page 10,000)?
### Q3: 你如何優化深度分頁（例如第 10,000 頁）？

*   **Key Points:**
    *   Problem: `OFFSET` scans and discards rows.
    *   Solution 1: **Keyset Pagination** (Seek Method). `WHERE id > last_seen_id LIMIT 10`. Fast but no random page access.
    *   Solution 2: **Deferred Join**. Select IDs via covering index first, then join full rows.
*   **回答要點：**
    *   問題：`OFFSET` 會掃描並丟棄資料列。
    *   解法 1：**Keyset 分頁**（Seek Method）。`WHERE id > last_seen_id LIMIT 10`。快速但無法隨機跳頁。
    *   解法 2：**延遲關聯**。先透過覆蓋索引選出 ID，再關聯完整資料列。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Cost is King**: The optimizer minimizes estimated IO and CPU cost, not necessarily time or logic.
    **成本為王**：優化器最小化預估的 IO 與 CPU 成本，不一定是時間或邏輯。
2.  **Explain `type`**: Memorize `const > eq_ref > ref > range > index > ALL`.
    **解讀 `type`**：熟記 `const > eq_ref > ref > range > index > ALL`。
3.  **Covering Index**: The most powerful optimization technique to avoid random disk IO.
    **覆蓋索引**：避免隨機磁碟 IO 最強大的優化技術。
4.  **Watch the `Extra`**: `Using filesort` and `Using temporary` are major red flags for high-concurrency queries.
    **關注 `Extra`**：`Using filesort` 與 `Using temporary` 是高併發查詢的主要警訊。
5.  **Filtered Matters**: A low `filtered` percentage suggests you need a better index to filter data at the engine level.
    **Filtered 很重要**：低的 `filtered` 百分比暗示你需要更好的索引在引擎層過濾資料。

### Next Steps
### 後續延伸

*   **Next Chapter**: `Transactions and Locks` (Chapter 05). Now that queries are fast, we must ensure they are safe and concurrent.
    **下一章**：`交易與鎖`（Chapter 05）。既然查詢變快了，我們必須確保它們是安全且可併發的。
*   **Practice**: Take a slow query from your production Slow Query Log, run `EXPLAIN ANALYZE` on it, and try to improve the execution plan.
    **實作**：從你的生產環境慢查詢日誌中挑選一個查詢，對其執行 `EXPLAIN ANALYZE`，並嘗試改進執行計畫。