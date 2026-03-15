# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，資料庫效能優化不應僅止於「加個 Index 試試看」。你需要具備透視資料庫核心機制的能力，從儲存引擎的物理結構到查詢優化器的決策邏輯，精準定位效能瓶頸。

For senior engineers, database performance tuning should not stop at "let's try adding an index." You need the ability to see through the core mechanisms of the database, from the physical structure of storage engines to the decision logic of query optimizers, to pinpoint performance bottlenecks accurately.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分 B-Tree 與 LSM Tree 的適用場景**：理解為何 MySQL/PostgreSQL 適合讀多寫少或強一致性場景，而 Cassandra/RocksDB 適合高吞吐寫入。
    **Distinguish between B-Tree and LSM Tree use cases**: Understand why MySQL/PostgreSQL fit read-heavy or strong consistency scenarios, while Cassandra/RocksDB excel at high-throughput writes.
2.  **解讀 Query Execution Plan**：不只看是否有用到索引，還能分析 `Scan` vs `Seek`、`Filesort`、`Index Merge` 以及 `Join` 演算法（Nested Loop vs Hash Join）的成本。
    **Interpret Query Execution Plans**: Go beyond checking for index usage; analyze the costs of `Scan` vs `Seek`, `Filesort`, `Index Merge`, and `Join` algorithms (Nested Loop vs Hash Join).
3.  **掌握鎖（Locking）與隔離層級（Isolation Levels）的權衡**：解釋 MVCC 如何運作，以及如何在 `REPEATABLE READ` 與 `READ COMMITTED` 之間做選擇以避免 Deadlocks 或 Write Skews。
    **Master the trade-offs of Locking and Isolation Levels**: Explain how MVCC works and how to choose between `REPEATABLE READ` and `READ COMMITTED` to avoid Deadlocks or Write Skews.
4.  **優化深分頁（Deep Pagination）與寬表查詢**：解決 `OFFSET` 在大數據量下的效能殺手問題。
    **Optimize Deep Pagination and Wide Table Queries**: Solve the performance killer issues caused by `OFFSET` on large datasets.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 儲存引擎物理結構：B+ Tree vs. LSM Tree
### Storage Engine Physics: B+ Tree vs. LSM Tree

大多數關聯式資料庫（RDBMS）預設使用 B+ Tree，而許多 NoSQL 或 NewSQL 資料庫使用 LSM Tree。理解底層結構是優化寫入效能的第一步。

Most Relational Database Management Systems (RDBMS) default to B+ Trees, while many NoSQL or NewSQL databases use LSM Trees. Understanding the underlying structure is the first step in optimizing write performance.

*   **B+ Tree (e.g., InnoDB, PostgreSQL)**:
    *   **模型 (Model)**：資料儲存在葉節點（Leaf Nodes），形成有序鏈結串列。適合範圍查詢（Range Query）。
    *   **寫入代價 (Write Cost)**：隨機寫入（Random I/O）。當頁面（Page）滿時會發生分裂（Split），導致較高的寫入放大與磁碟 I/O。
    *   **讀取優勢 (Read Advantage)**：讀取效能極高且穩定，適合 Read-Heavy 系統。
    *   **Model**: Data is stored in leaf nodes, forming an ordered linked list. Ideal for range queries.
    *   **Write Cost**: Random I/O. When a page is full, a split occurs, leading to higher write amplification and disk I/O.
    *   **Read Advantage**: Extremely high and stable read performance, suitable for Read-Heavy systems.

*   **LSM Tree (Log-Structured Merge Tree) (e.g., RocksDB, Cassandra)**:
    *   **模型 (Model)**：所有寫入視為 Append-only Log（順序寫入），先寫入記憶體（MemTable），再 Flush 到磁碟（SSTable）。
    *   **寫入優勢 (Write Advantage)**：極高的寫入吞吐量（Sequential I/O）。
    *   **讀取代價 (Read Cost)**：讀取時可能需要合併多個 SSTable 的結果（Read Amplification），依賴 Bloom Filter 優化。
    *   **Model**: All writes are treated as Append-only Logs (sequential writes), first written to memory (MemTable), then flushed to disk (SSTable).
    *   **Write Advantage**: Extremely high write throughput (Sequential I/O).
    *   **Read Cost**: Reading may require merging results from multiple SSTables (Read Amplification), relying on Bloom Filters for optimization.

## 2.2 查詢優化器與執行計畫 (Query Optimizer & Execution Plan)

SQL 是宣告式語言（Declarative），你告訴 DB「要什麼」，由優化器決定「怎麼拿」。

SQL is a declarative language; you tell the DB "what you want," and the optimizer decides "how to get it."

*   **Cost-Based Optimizer (CBO)**：資料庫根據統計資訊（Statistics，如資料分布、Cardinality）計算各種路徑的成本，選擇最低者。
*   **Mental Model**：想像你在圖書館找書。
    *   **Table Scan**: 從第一架第一本開始逐本檢查。
    *   **Index Seek**: 查目錄卡（Index），直接走到特定書架。
    *   **Key Lookup / Bookmark Lookup (回表)**: 查目錄卡只知道書名，要看內容還得去書架拿書（從 Secondary Index 跳回 Clustered Index）。
*   **Cost-Based Optimizer (CBO)**: The database calculates the cost of various paths based on statistics (e.g., data distribution, cardinality) and selects the lowest one.
*   **Mental Model**: Imagine finding a book in a library.
    *   **Table Scan**: Checking every book one by one from the first shelf.
    *   **Index Seek**: Checking the catalog (Index) and walking directly to a specific shelf.
    *   **Key Lookup / Bookmark Lookup**: The catalog only gives the title; to read the content, you must go to the shelf (jumping from Secondary Index to Clustered Index).

## 2.3 MVCC 與鎖 (MVCC & Locking)

**MVCC (Multi-Version Concurrency Control)** 允許讀寫操作互不阻塞。

**MVCC (Multi-Version Concurrency Control)** allows read and write operations to occur without blocking each other.

*   **概念**：每次更新不直接覆蓋原資料，而是產生新版本（Version）。讀取時根據隔離層級（Isolation Level）決定看到哪個版本（Snapshot）。
*   **關鍵差異**：
    *   **Repeatable Read (RR)**：交易開始時建立 Snapshot，之後都讀這個快照。
    *   **Read Committed (RC)**：每個 Query 執行時建立新的 Snapshot。
*   **Concept**: Updates do not overwrite original data directly but generate a new version. Reads determine which version (Snapshot) to see based on the Isolation Level.
*   **Key Difference**:
    *   **Repeatable Read (RR)**: Creates a Snapshot at the start of the transaction; subsequent reads use this snapshot.
    *   **Read Committed (RC)**: Creates a new Snapshot for each query execution.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或大型專案中，效能優化往往決定了系統的上限（Scalability）。

In system design interviews or large-scale projects, performance tuning often determines the system's scalability ceiling.

## 3.1 讀寫分離與延遲 (Read/Write Splitting & Lag)

*   **架構角色**：Primary DB 處理寫入，多個 Read Replicas 處理讀取。
*   **效能挑戰**：Replication Lag。當 Primary 寫入量大時，Replica 可能落後數秒。
*   **設計決策**：對於「使用者剛修改完個人資料，刷新頁面必須看到最新資料」的場景，必須強制讀取 Primary（Pinning Strategy），或者在 Client 端做暫存。
*   **Architecture Role**: Primary DB handles writes; multiple Read Replicas handle reads.
*   **Performance Challenge**: Replication Lag. When the Primary has high write volume, Replicas may lag by seconds.
*   **Design Decision**: For scenarios like "user just updated profile and must see new data on refresh," you must enforce reading from Primary (Pinning Strategy) or cache on the Client side.

## 3.2 索引對寫入效能的衝擊 (Index Impact on Write Performance)

*   **場景**：一個高頻寫入的 Log Table 或 Audit Table。
*   **權衡**：每增加一個 Secondary Index，插入資料時就需要多一次 B+ Tree 的維護（隨機 I/O）。
*   **優化策略**：
    1.  減少不必要的索引。
    2.  使用 **Covering Index**（覆蓋索引）來滿足多種查詢需求，而非建立多個單欄索引。
    3.  考慮將歷史資料歸檔（Archiving）或分區（Partitioning），減小 B+ Tree 深度。
*   **Scenario**: A high-frequency write Log Table or Audit Table.
*   **Trade-off**: Every additional Secondary Index requires an extra B+ Tree maintenance operation (Random I/O) during insertion.
*   **Optimization Strategy**:
    1.  Reduce unnecessary indexes.
    2.  Use **Covering Indexes** to satisfy multiple query needs instead of creating multiple single-column indexes.
    3.  Consider archiving historical data or Partitioning to reduce B+ Tree depth.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：優化電商訂單查詢 (Optimizing E-commerce Order Query)

### 背景 (Context)
我們有一個 `orders` 表，包含 5000 萬筆資料。
We have an `orders` table with 50 million records.

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    status VARCHAR(20), -- 'PENDING', 'PAID', 'SHIPPED', 'CANCELLED'
    created_at DATETIME,
    amount DECIMAL(10, 2),
    ...
);
```

需求：查詢某個使用者最近的「已完成」訂單。
Requirement: Query a user's most recent "completed" orders.

```sql
SELECT id, status, amount, created_at
FROM orders
WHERE user_id = 12345 AND status = 'PAID'
ORDER BY created_at DESC
LIMIT 10;
```

### 階段 1：Naive Indexing
假設我們只有 `INDEX(user_id)`。

Suppose we only have `INDEX(user_id)`.

*   **Execution Plan**:
    1.  DB 使用索引找到 `user_id = 12345` 的所有 rows（假設有 1000 筆）。
    2.  **回表 (Clustered Index Lookup)**：讀取這 1000 筆的完整資料列。
    3.  **Filter**: 在記憶體中過濾 `status = 'PAID'`。
    4.  **Filesort**: 在記憶體中對結果按 `created_at` 排序。
*   **問題**：`Filesort` 是 CPU 密集操作，且回表次數過多。

*   **Execution Plan**:
    1.  DB uses the index to find all rows where `user_id = 12345` (assume 1000 rows).
    2.  **Clustered Index Lookup**: Reads the full data rows for these 1000 entries.
    3.  **Filter**: Filters `status = 'PAID'` in memory.
    4.  **Filesort**: Sorts the results by `created_at` in memory.
*   **Problem**: `Filesort` is CPU-intensive, and there are too many lookups.

### 階段 2：Composite Index (遵循最左前綴原則)
建立索引：`INDEX(user_id, status, created_at)`。

Create index: `INDEX(user_id, status, created_at)`.

*   **改進 (Improvement)**：
    *   索引順序完全符合 `WHERE` + `ORDER BY`。
    *   DB 可以直接在索引樹上定位到 `user_id=12345` 且 `status='PAID'` 的區段。
    *   因為索引已經按 `created_at` 排序，DB 只需要反向掃描前 10 筆即可，**消除 Filesort**。
*   **Improvement**:
    *   The index order perfectly matches `WHERE` + `ORDER BY`.
    *   DB can locate the section for `user_id=12345` and `status='PAID'` directly on the index tree.
    *   Since the index is already sorted by `created_at`, the DB only needs to reverse scan the first 10 entries, **eliminating Filesort**.

### 階段 3：Covering Index (極致優化)
如果查詢需要 `amount`，目前的索引不包含此欄位，仍需回表 10 次。
若查詢頻率極高，我們可以將 `amount` 加入索引：`INDEX(user_id, status, created_at, amount)`。

If the query needs `amount`, the current index doesn't contain this field, still requiring 10 lookups.
If the query frequency is extremely high, we can add `amount` to the index: `INDEX(user_id, status, created_at, amount)`.

*   **結果**：**Using index** (MySQL 用語)。查詢所需的所有資料都在 B+ Tree 的節點中，完全不需要讀取 Data Page。
*   **代價**：索引變大，佔用更多記憶體與磁碟空間。
*   **Result**: **Using index** (MySQL terminology). All data required for the query is in the B+ Tree nodes, requiring zero reads of Data Pages.
*   **Cost**: The index becomes larger, consuming more memory and disk space.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 索引基數 (Cardinality) 陷阱
### The Cardinality Pitfall

*   **錯誤**：對 `gender` (Male/Female) 或 `is_active` (True/False) 這種低基數欄位單獨建立索引。
*   **為何不好**：如果一個索引過濾後仍剩下 50% 的資料，優化器通常會放棄索引直接做 Full Table Scan，因為順序讀取比大量的隨機回表（Random Seek）更快。
*   **Mistake**: Creating a standalone index on low-cardinality fields like `gender` (Male/Female) or `is_active` (True/False).
*   **Why it's bad**: If an index filter still leaves 50% of the data, the optimizer will often abandon the index and do a Full Table Scan, as sequential reads are faster than massive random lookups (Random Seeks).

## 5.2 隱式轉型導致索引失效
### Implicit Casting Killing Indexes

*   **錯誤**：`SELECT * FROM users WHERE phone_number = 987654321;` (欄位定義為 `VARCHAR`)。
*   **為何不好**：DB 會將欄位轉型為數字進行比較：`CAST(phone_number AS INT) = ...`。這導致無法使用 B-Tree 索引（因為函數作用在欄位上），退化為 Full Table Scan。
*   **修正**：確保輸入型別與欄位型別一致：`WHERE phone_number = '987654321'`.
*   **Mistake**: `SELECT * FROM users WHERE phone_number = 987654321;` (Column defined as `VARCHAR`).
*   **Why it's bad**: The DB casts the column to a number for comparison: `CAST(phone_number AS INT) = ...`. This prevents the use of the B-Tree index (since a function is applied to the column), degrading to a Full Table Scan.
*   **Fix**: Ensure input type matches column type: `WHERE phone_number = '987654321'`.

## 5.3 深分頁 (Deep Pagination)
### Deep Pagination

*   **錯誤**：`SELECT * FROM logs LIMIT 1000000, 10;`
*   **為何不好**：DB 必須讀取前 1,000,010 筆資料，拋棄前 100 萬筆，只回傳最後 10 筆。這會導致大量的 I/O 和 CPU 浪費。
*   **修正 (Keyset Pagination / Seek Method)**：
    使用上一次查詢的最後一個 ID 作為起點：
    `SELECT * FROM logs WHERE id > 1000000 LIMIT 10;`
*   **Mistake**: `SELECT * FROM logs LIMIT 1000000, 10;`
*   **Why it's bad**: The DB must read the first 1,000,010 records, discard the first 1 million, and return only the last 10. This causes massive I/O and CPU waste.
*   **Fix (Keyset Pagination / Seek Method)**:
    Use the last ID from the previous query as the starting point:
    `SELECT * FROM logs WHERE id > 1000000 LIMIT 10;`

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 解釋 Clustered Index 與 Secondary Index 的區別，以及這對查詢效能的影響？
### Explain the difference between Clustered Index and Secondary Index, and how it affects query performance?

*   **高分回答要點**：
    *   **結構差異**：Clustered Index 的葉節點儲存完整的 Row Data（通常是 Primary Key）；Secondary Index 的葉節點儲存索引鍵值 + Primary Key。
    *   **回表 (Lookup)**：查詢 Secondary Index 若需要非索引欄位，必須拿 PK 再去查 Clustered Index，產生額外 I/O。
    *   **Covering Index**：若 Secondary Index 包含所有查詢欄位，則無需回表，效能最佳。
*   **Key Points for High Score**:
    *   **Structural Difference**: Clustered Index leaf nodes store the full Row Data (usually Primary Key); Secondary Index leaf nodes store the index key + Primary Key.
    *   **Lookup**: Querying a Secondary Index for non-indexed columns requires taking the PK to query the Clustered Index again, generating extra I/O.
    *   **Covering Index**: If the Secondary Index contains all query columns, no lookup is needed, yielding optimal performance.

## Q2: 在高併發環境下，如何避免 Deadlock？
### How to avoid Deadlocks in a high-concurrency environment?

*   **高分回答要點**：
    *   **固定順序**：確保所有交易以相同的順序存取資源（例如：總是先鎖 Table A 再鎖 Table B，或按 ID 排序後鎖定）。
    *   **縮短事務**：保持 Transaction 簡短，避免在事務中進行長時間的網路呼叫。
    *   **隔離層級**：若業務允許，從 `REPEATABLE READ` 降級為 `READ COMMITTED` 可減少 Gap Lock 的使用，降低鎖衝突機率。
*   **Key Points for High Score**:
    *   **Fixed Order**: Ensure all transactions access resources in the same order (e.g., always lock Table A then Table B, or lock by sorted ID).
    *   **Short Transactions**: Keep transactions short; avoid long network calls within a transaction.
    *   **Isolation Level**: If business logic permits, downgrading from `REPEATABLE READ` to `READ COMMITTED` reduces the use of Gap Locks, lowering lock conflict probability.

## Q3: 為什麼 `SELECT COUNT(*)` 在 InnoDB 中比 MyISAM 慢？
### Why is `SELECT COUNT(*)` slower in InnoDB than in MyISAM?

*   **高分回答要點**：
    *   **MyISAM**：儲存了精確的 Row Count，讀取是 O(1)。但不支援 Transaction。
    *   **InnoDB**：支援 MVCC，不同 Transaction 看到的行數可能不同，因此必須即時掃描 B-Tree 來計算對當前 Transaction 可見的行數。
    *   **優化**：在 InnoDB 中，優化器會嘗試使用最小的 Secondary Index 來掃描以節省 I/O，而不是掃描巨大的 Clustered Index。
*   **Key Points for High Score**:
    *   **MyISAM**: Stores an exact Row Count; reading is O(1). But it doesn't support Transactions.
    *   **InnoDB**: Supports MVCC; different transactions may see different row counts, so it must scan the B-Tree in real-time to count rows visible to the current transaction.
    *   **Optimization**: In InnoDB, the optimizer attempts to scan the smallest Secondary Index to save I/O, rather than scanning the massive Clustered Index.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **物理結構決定特性**：B+ Tree 適合讀多與範圍查；LSM Tree 適合寫多（Log ingestion）。
2.  **索引不是越多越好**：每個索引都會拖慢寫入；追求 **Covering Index** 以消除回表。
3.  **最左前綴 (Leftmost Prefix)**：複合索引必須從最左邊開始匹配，跳過中間欄位會導致索引部分失效。
4.  **執行計畫 (Explain)**：養成在寫複雜 SQL 前先 `EXPLAIN` 的習慣，關注 `type` (ALL vs ref vs range) 與 `Extra` (Using filesort, Using temporary)。
5.  **隔離層級的代價**：`SERIALIZABLE` 最安全但最慢；`RC` 併發度高但有幻讀風險；了解你的預設值（通常是 `RR` 或 `RC`）。

## 後續延伸 (Next Steps)
*   **進階實作**：使用 `EXPLAIN ANALYZE` (Postgres) 或 `EXPLAIN FORMAT=JSON` (MySQL) 分析真實查詢成本。
*   **下一章預告**：當單機資料庫優化到極限後，我們將進入 **Chapter 05: Caching Strategies & Patterns**，探討如何利用 Redis/Memcached 進一步卸載資料庫壓力。

*   **Advanced Practice**: Use `EXPLAIN ANALYZE` (Postgres) or `EXPLAIN FORMAT=JSON` (MySQL) to analyze real query costs.
*   **Next Chapter**: Once single-node database tuning reaches its limit, we will move to **Chapter 05: Caching Strategies & Patterns**, exploring how to leverage Redis/Memcached to further offload database pressure.