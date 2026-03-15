# Chapter 07: Scaling Strategies: Sharding and Partitioning
# 第七章：擴展性設計：分庫分表與分區

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Scaling a relational database beyond a single node is one of the most critical transition points in a system's lifecycle. It marks the shift from a centralized architecture to a distributed one, introducing significant complexity. This chapter focuses on the "nuclear options" of scaling: Partitioning and Sharding.
將關聯式資料庫擴展到單一節點之外，是系統生命週期中最關鍵的轉折點之一。這標誌著從集中式架構轉向分散式架構，並引入了顯著的複雜性。本章將聚焦於擴展的「核武器選項」：分區（Partitioning）與分片（Sharding，即分庫分表）。

By the end of this chapter, you should be able to:
完成本章後，你應該能夠：

1.  **Distinguish between Partitioning and Sharding**: Understand when to use MySQL's native partitioning versus application-level sharding.
    **區分分區與分片**：理解何時使用 MySQL 原生的分區功能，何時使用應用層級的分庫分表。
2.  **Design a Sharding Strategy**: Select the appropriate Sharding Key to avoid "hotspots" and minimize cross-shard queries.
    **設計分片策略**：選擇合適的分片鍵（Sharding Key）以避免「熱點」問題並最小化跨分片查詢。
3.  **Implement Distributed IDs**: Explain why MySQL `AUTO_INCREMENT` fails in sharded environments and implement alternatives like Snowflake.
    **實作分散式 ID**：解釋為何 MySQL 的 `AUTO_INCREMENT` 在分片環境下會失效，並實作如 Snowflake 等替代方案。
4.  **Handle Distributed Data Challenges**: Propose solutions for cross-shard joins, pagination, and transactions.
    **處理分散式資料挑戰**：針對跨分片 Join、分頁（Pagination）與交易（Transactions）提出解決方案。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Library Analogy
### 2.1 圖書館類比

Imagine a library that has run out of shelf space. You have three ways to solve this:
想像一座圖書館的書架空間已經用完了。你有三種解決方式：

1.  **Partitioning (Local Optimization)**: You keep all books in the *same building*, but you move all books published before 2000 to the basement. The catalog is still central, but the physical storage is segmented on the same property. In MySQL, this is splitting a table into multiple files on the same disk/server (e.g., `RANGE`, `LIST`, `HASH`).
    **分區（Partitioning，本地優化）**：你將所有書保留在*同一棟建築*內，但將 2000 年以前出版的書移到地下室。目錄仍然是集中的，但實體儲存在同一物業內被區隔開來。在 MySQL 中，這代表將一張表拆分為同一磁碟/伺服器上的多個檔案（例如：`RANGE`、`LIST`、`HASH`）。

2.  **Vertical Sharding (Functional Split)**: You build a separate "Science Library" and an "Arts Library" across town. Users looking for science books go to one building; art lovers go to another. This is splitting databases by domain (e.g., `UserDB`, `OrderDB`, `ProductDB`).
    **垂直分庫（Vertical Sharding，功能拆分）**：你在城市的另一端分別建立了「科學圖書館」與「藝術圖書館」。找科學書籍的讀者去一棟樓，藝術愛好者去另一棟。這就是依據領域拆分資料庫（例如：`UserDB`、`OrderDB`、`ProductDB`）。

3.  **Horizontal Sharding (Data Split)**: The "Science Library" is still too full. You build two identical buildings. Building A holds authors A-M; Building B holds authors N-Z. The structure (schema) is identical, but the data is disjoint. This is true Sharding (e.g., `OrderDB_01`, `OrderDB_02`).
    **水平分庫分表（Horizontal Sharding，資料拆分）**： 「科學圖書館」還是太擠了。你蓋了兩棟一模一樣的建築。A 館存放作者 A-M 的書，B 館存放作者 N-Z 的書。結構（Schema）完全相同，但資料是不重疊的。這才是真正的 Sharding（例如：`OrderDB_01`、`OrderDB_02`）。

### 2.2 Key Definitions
### 2.2 關鍵定義

*   **Sharding Key (Partition Key)**: The column used to determine which shard a row belongs to. Choosing this is the most irreversible decision in the design.
    **分片鍵**：用於決定一筆資料屬於哪個分片的欄位。選擇分片鍵是設計中最不可逆的決策。
*   **Routing Strategy**: The algorithm mapping the key to a database. Common strategies are `Hash(Key) % N` (Modulo) or `Range(Key)` (e.g., Time-based).
    **路由策略**：將 Key 映射到資料庫的演算法。常見策略有 `Hash(Key) % N`（取模）或 `Range(Key)`（例如基於時間）。
*   **Snowflake ID**: A 64-bit integer structure composed of a timestamp, machine ID, and sequence number, ensuring unique, roughly sortable IDs across a distributed system without coordination.
    **Snowflake ID**：一種 64 位元的整數結構，由時間戳記、機器 ID 和序列號組成，確保在分散式系統中無需協調即可生成唯一且大致可排序的 ID。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 When to Shard?
### 3.1 何時進行分片？

In a production environment, sharding is an operational burden. It should be the last resort after tuning queries, adding indexes, caching (Redis), and Read/Write splitting.
在生產環境中，分片是一種維運負擔。它應該是在優化查詢、增加索引、快取（Redis）以及讀寫分離之後的最後手段。

**Rule of Thumb for Sharding:**
**分片的經驗法則：**
*   **Data Volume**: Single table exceeds 20-50 million rows or 1TB+ size (depending on row width).
    **資料量**：單表超過 2000-5000 萬筆資料或 1TB+ 大小（取決於單列寬度）。
*   **Write Throughput**: Write QPS consistently exceeds what a single master can handle (e.g., > 3k-5k heavy writes/sec).
    **寫入吞吐量**：寫入 QPS 持續超過單一 Master 能處理的上限（例如：> 3k-5k 重度寫入/秒）。
*   **Rebuild Time**: Backup/Restore or DDL operations take unacceptably long (e.g., days).
    **重建時間**：備份/還原或 DDL 操作耗時過長，令人無法接受（例如：數天）。

### 3.2 Architecture Impact
### 3.2 架構影響

Introducing sharding changes the topology of your data layer:
引入分片會改變資料層的拓撲結構：

*   **Middleware Pattern**: Applications connect to a proxy (e.g., ProxySQL, ShardingSphere-Proxy) that looks like a single MySQL instance but routes queries behind the scenes.
    **Middleware 模式**：應用程式連接到一個代理（如 ProxySQL, ShardingSphere-Proxy），它看起來像單一 MySQL 實例，但在幕後進行查詢路由。
*   **Client-Side Pattern**: The application code (using libraries like ShardingJDBC or custom logic) calculates the shard ID and connects directly to the specific DB instance. This reduces latency but couples infrastructure logic with business code.
    **Client-Side 模式**：應用程式碼（使用 ShardingJDBC 等函式庫或自定義邏輯）計算分片 ID 並直接連接到特定的 DB 實例。這降低了延遲，但將基礎設施邏輯與業務代碼耦合。

---

## 4. Walkthrough: Scaling an Order System
## 4. 逐步示例：擴展訂單系統

### Scenario
### 情境

You are designing for an e-commerce platform. The `orders` table has hit 100 million rows. Queries are slowing down, and DDL changes lock the table for hours. We need to shard.
你正在為一個電商平台進行設計。`orders` 表已經達到 1 億筆資料。查詢變慢，且 DDL 變更會鎖表數小時。我們需要進行分片。

### Step 1: Choosing the Sharding Key
### 第一步：選擇分片鍵

This is the most critical step. We have two main candidates: `order_id` and `user_id`.
這是最關鍵的一步。我們有兩個主要候選者：`order_id` 和 `user_id`。

*   **Option A: Shard by `order_id`**
    *   *Pros*: Even data distribution.
    *   *Cons*: A user wants to see "My Orders". This query (`SELECT * FROM orders WHERE user_id = ?`) does not contain the `order_id`. The system must query **ALL** shards (Scatter-Gather), which kills performance.
*   **選項 A：依 `order_id` 分片**
    *   *優點*：資料分佈均勻。
    *   *缺點*：使用者想查看「我的訂單」。此查詢 (`SELECT * FROM orders WHERE user_id = ?`) 不包含 `order_id`。系統必須查詢 **所有** 分片（Scatter-Gather），這會嚴重拖垮效能。

*   **Option B: Shard by `user_id`**
    *   *Pros*: All orders for User A are in the same shard. "My Orders" is a single-shard query (efficient).
    *   *Cons*: Data might be uneven if some users are "whales" (unlikely for standard e-commerce).
*   **選項 B：依 `user_id` 分片**
    *   *優點*：使用者 A 的所有訂單都在同一個分片中。「我的訂單」是單分片查詢（高效）。
    *   *缺點*：如果某些使用者是「大戶」，資料可能會分佈不均（在標準電商中較少見）。

**Decision**: We choose **`user_id`** as the Sharding Key.
**決策**：我們選擇 **`user_id`** 作為分片鍵。

### Step 2: Handling the "Merchant View" Problem
### 第二步：處理「商家視角」問題

We optimized for buyers (`user_id`), but now merchants want to see "My Sales". A merchant's orders are scattered across all shards because they sell to different users.
我們針對買家（`user_id`）進行了優化，但現在商家想查看「我的銷售紀錄」。商家的訂單分散在所有分片中，因為他們賣給不同的使用者。

**Solution: The Index Table (Mapping Table) or Dual Write**
**解決方案：索引表（映射表）或雙寫**

We create a separate mapping table or use a search engine (Elasticsearch).
我們建立一個獨立的映射表，或使用搜尋引擎（Elasticsearch）。

1.  **Primary Storage (OLTP)**: Sharded by `user_id`. Source of Truth.
    **主儲存（OLTP）**：依 `user_id` 分片。作為單一事實來源（Source of Truth）。
2.  **Secondary Index**: A table `merchant_orders (merchant_id, order_id, user_id)` sharded by `merchant_id`.
    **次級索引**：一張依 `merchant_id` 分片的表 `merchant_orders (merchant_id, order_id, user_id)`。
3.  **Flow**: When an order is created, write to the User Shard. Then (async via message queue) write to the Merchant Shard or Elasticsearch.
    **流程**：建立訂單時，寫入 User 分片。然後（透過訊息佇列非同步）寫入 Merchant 分片或 Elasticsearch。

### Step 3: Distributed ID Generation (Snowflake)
### 第三步：分散式 ID 生成（Snowflake）

We cannot use `AUTO_INCREMENT` because `Shard A` and `Shard B` would both generate `order_id = 101`. We need global uniqueness.
我們不能使用 `AUTO_INCREMENT`，因為 `Shard A` 和 `Shard B` 都會生成 `order_id = 101`。我們需要全域唯一性。

**Why not UUID?**
UUID is 128-bit and random. In MySQL InnoDB (B+ Tree), inserting random primary keys causes massive **page splitting** and fragmentation, killing write performance.
**為何不用 UUID？**
UUID 是 128 位元且隨機的。在 MySQL InnoDB（B+ Tree）中，插入隨機的主鍵會導致大量的 **頁分裂（Page Splitting）** 和碎片化，嚴重扼殺寫入效能。

**Implementation: Twitter Snowflake**
**實作：Twitter Snowflake**

Structure (64-bit Long):
結構（64 位元 Long）：
*   1 bit: Unused (sign bit).
*   41 bits: Timestamp (milliseconds). ~69 years.
*   10 bits: Machine ID (Data Center + Worker ID).
*   12 bits: Sequence number (per millisecond).

```java
// Conceptual Code (Java-like)
public synchronized long nextId() {
    long timestamp = timeGen();
    
    if (timestamp < lastTimestamp) {
        throw new RuntimeException("Clock moved backwards!");
    }

    if (lastTimestamp == timestamp) {
        // Same millisecond, increment sequence
        sequence = (sequence + 1) & sequenceMask;
        if (sequence == 0) {
            timestamp = tilNextMillis(lastTimestamp);
        }
    } else {
        // New millisecond, reset sequence
        sequence = 0;
    }

    lastTimestamp = timestamp;

    return ((timestamp - twepoch) << timestampLeftShift) |
           (datacenterId << datacenterIdShift) |
           (workerId << workerIdShift) |
           sequence;
}
```

This generates IDs that are **k-ordered** (roughly sorted by time), keeping the B+ Tree happy.
這會生成 **k-ordered**（大致按時間排序）的 ID，讓 B+ Tree 保持高效。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Cross-Shard Join" Trap
### 5.1 「跨分片 Join」陷阱

*   **Anti-pattern**: Trying to `JOIN` the `orders` table (Shard 1) with the `users` table (Shard 2) in a single SQL query via middleware.
    **反模式**：試圖透過 Middleware 在單個 SQL 查詢中將 `orders` 表（分片 1）與 `users` 表（分片 2）進行 `JOIN`。
*   **Why it's bad**: The middleware has to pull data from both shards into memory and perform the join there. This consumes massive bandwidth and memory, often leading to OOM (Out of Memory).
    **為何不好**：Middleware 必須將兩個分片的資料拉到記憶體中並在那裡執行 Join。這會消耗大量頻寬與記憶體，常導致 OOM（記憶體不足）。
*   **Solution**:
    1.  **Global Tables**: Replicate small tables (like `currency_codes`) to every shard.
    2.  **App-side Join**: Query `orders`, get `user_ids`, then query `users` (IN clause).
    **解決方案**：
    1.  **全域表（廣播表）**：將小表（如 `currency_codes`）複製到每個分片。
    2.  **應用層 Join**：先查詢 `orders`，取得 `user_ids`，再查詢 `users`（使用 IN 子句）。

### 5.2 Sharding by Date (for Real-time Writes)
### 5.2 依日期分片（針對即時寫入）

*   **Anti-pattern**: Creating tables like `orders_2023_10`, `orders_2023_11`.
    **反模式**：建立如 `orders_2023_10`、`orders_2023_11` 的表。
*   **Why it's bad**: This creates a **Write Hotspot**. In October, *only* the October shard takes writes. The other 11 shards are idle. You aren't scaling write throughput; you are just managing storage.
    **為何不好**：這會造成 **寫入熱點**。在十月，*只有* 十月的分片在承受寫入。其他 11 個分片是閒置的。你並沒有擴展寫入吞吐量，只是在管理儲存空間。
*   **Exception**: Acceptable for archival/logging data where write throughput isn't the bottleneck, but retention is.
    **例外**：對於歸檔/日誌資料是可接受的，因為寫入吞吐量不是瓶頸，保留策略才是。

### 5.3 Modulo Sharding without Virtual Nodes
### 5.3 沒有虛擬節點的取模分片

*   **Anti-pattern**: `Hash(key) % 4`. Later, you need to scale to 5 shards. `Hash(key) % 5` changes the location of almost all data.
    **反模式**：使用 `Hash(key) % 4`。之後你需要擴展到 5 個分片。`Hash(key) % 5` 會改變幾乎所有資料的位置。
*   **Solution**:
    1.  **Fixed Power of 2**: Start with logical shards (e.g., 1024 tables) mapped to physical servers. When scaling, move existing tables, don't rehash rows.
    2.  **Consistent Hashing**: Minimizes data movement during resizing.
    **解決方案**：
    1.  **固定 2 的冪次**：一開始就建立邏輯分片（例如 1024 張表）映射到實體伺服器。擴展時，移動現有的表，而不是重新 Hash 資料列。
    2.  **一致性雜湊**：最小化擴容時的資料移動。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle pagination (LIMIT/OFFSET) across shards?
### Q1: 你如何處理跨分片的分頁（LIMIT/OFFSET）？

*   **Context**: `SELECT * FROM orders ORDER BY time LIMIT 10 OFFSET 10000`.
*   **The Problem**: You cannot simply ask each shard for `LIMIT 10 OFFSET 10000`. You might miss the global top records.
*   **High-Score Answer**:
    *   **Naive**: Fetch `OFFSET + LIMIT` from *every* shard, sort in memory, and discard. Very expensive for deep pagination.
    *   **Optimization**:
        1.  **Forbid Deep Pagination**: Use "Seek Method" (where ID > last_seen_id) instead of OFFSET.
        2.  **Secondary Index**: Use a dedicated search engine (Elasticsearch) for complex queries/pagination, using MySQL only for key-based lookups.
*   **情境**：`SELECT * FROM orders ORDER BY time LIMIT 10 OFFSET 10000`。
*   **問題**：你不能簡單地對每個分片要求 `LIMIT 10 OFFSET 10000`。你可能會漏掉全域的頂部紀錄。
*   **高分回答**：
    *   **直觀解法**：從 *每個* 分片抓取 `OFFSET + LIMIT`，在記憶體中排序，然後丟棄多餘資料。這對深度分頁來說非常昂貴。
    *   **優化方案**：
        1.  **禁止深度分頁**：使用「Seek Method」（where ID > last_seen_id）來取代 OFFSET。
        2.  **次級索引**：使用專用的搜尋引擎（Elasticsearch）來處理複雜查詢/分頁，MySQL 僅用於基於 Key 的查找。

### Q2: How do you migrate from a single DB to a sharded DB with zero downtime?
### Q2: 如何在零停機的情況下從單一資料庫遷移到分片資料庫？

*   **High-Score Answer**:
    1.  **Dual Write (Application)**: Modify code to write to *both* Old DB and New Sharded DB. Read from Old.
    2.  **Backfill**: Run a script to copy historical data from Old to New (handling duplicates/updates carefully).
    3.  **Verification**: Compare data consistency between Old and New continuously.
    4.  **Switch Reads**: Config flag to start reading from New DB.
    5.  **Stop Dual Write**: Once stable, stop writing to Old DB.
*   **高分回答**：
    1.  **雙寫（應用層）**：修改程式碼以同時寫入 *舊 DB* 與 *新分片 DB*。從舊 DB 讀取。
    2.  **回填**：執行腳本將歷史資料從舊 DB 複製到新 DB（小心處理重複/更新）。
    3.  **驗證**：持續比對舊與新 DB 之間的資料一致性。
    4.  **切換讀取**：透過設定開關開始從新 DB 讀取。
    5.  **停止雙寫**：一旦穩定，停止寫入舊 DB。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
*   **Sharding is a last resort**: Optimize queries, indexes, and caching first.
    **分片是最後手段**：先優化查詢、索引和快取。
*   **Sharding Key is King**: It determines data distribution and query performance. `user_id` is usually better than `date` for OLTP.
    **分片鍵是王道**：它決定了資料分佈與查詢效能。對於 OLTP，`user_id` 通常優於 `date`。
*   **Snowflake over UUID**: Use time-ordered distributed IDs to prevent B+ Tree fragmentation.
    **Snowflake 勝過 UUID**：使用依時間排序的分散式 ID 以防止 B+ Tree 碎片化。
*   **No Distributed Joins**: Perform joins in the application layer or use data redundancy (broadcasting tables).
    **禁止分散式 Join**：在應用層執行 Join 或使用資料冗餘（廣播表）。
*   **Merchant vs. User View**: Solve multi-dimensional queries using Mapping Tables or heterogeneous indexing (MySQL + Elasticsearch).
    **商家 vs. 使用者視角**：使用映射表或異質索引（MySQL + Elasticsearch）解決多維度查詢。

### Next Steps (後續延伸)
*   **Replication & High Availability**: Now that data is sharded, how do we ensure each shard doesn't become a single point of failure? (See Chapter 08).
    **複製與高可用性**：現在資料已經分片，我們如何確保每個分片不會成為單點故障？（參見第八章）。
*   **Distributed Transactions**: Deep dive into 2PC (Two-Phase Commit) vs. Saga pattern for consistency across shards.
    **分散式交易**：深入研究 2PC（兩階段提交）與 Saga 模式，以解決跨分片的一致性問題。