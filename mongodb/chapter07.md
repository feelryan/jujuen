# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單一 Replica Set 架構下，當資料量超過單機儲存上限或寫入吞吐量（Write Throughput）達到瓶頸時，**Sharding（分片）** 是 MongoDB 提供的水平擴展解決方案。然而，Sharding 引入了極高的維運複雜度與架構限制。對於 Senior Engineer 而言，挑戰不在於「如何開啟分片」，而在於「如何設計正確的分片鍵（Shard Key）」以避免效能災難。

In a single Replica Set architecture, when data volume exceeds storage limits or write throughput hits a bottleneck, **Sharding** is the horizontal scaling solution provided by MongoDB. However, Sharding introduces significant operational complexity and architectural constraints. For a Senior Engineer, the challenge is not "how to enable sharding," but "how to design the correct Shard Key" to avoid performance disasters.

完成本章後，你應該能夠：

1.  **評估分片時機**：判斷何時該從 Replica Set 轉向 Sharded Cluster，以及何時該避免過早優化。
    **Evaluate Sharding Timing:** Determine when to transition from a Replica Set to a Sharded Cluster, and when to avoid premature optimization.
2.  **設計 Shard Key**：基於 Cardinality（基數）、Frequency（頻率）與 Monotonicity（單調性）選擇最佳分片鍵。
    **Design Shard Keys:** Select the optimal Shard Key based on Cardinality, Frequency, and Monotonicity.
3.  **解決擴展瓶頸**：理解並處理 Jumbo Chunks、Balancer 延遲與 Hot Shard（熱點分片）問題。
    **Resolve Scaling Bottlenecks:** Understand and handle Jumbo Chunks, Balancer lag, and Hot Shard issues.
4.  **優化查詢路由**：區分 Targeted Queries（定向查詢）與 Scatter-Gather Queries（分散聚合查詢）對效能的影響。
    **Optimize Query Routing:** Distinguish the performance impact between Targeted Queries and Scatter-Gather Queries.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 架構組件 (Architecture Components)

MongoDB 的 Sharded Cluster 由三個核心組件構成，這與傳統關聯式資料庫的分庫分表（Manual Sharding）不同，MongoDB 提供了自動化的路由層。

MongoDB's Sharded Cluster consists of three core components. Unlike manual sharding in traditional RDBMS, MongoDB provides an automated routing layer.

1.  **Mongos (Query Router)**:
    *   應用程式的接入點，本身不儲存資料。它負責解析查詢，根據 Config Server 的 Metadata 將請求路由到正確的 Shard。
    *   The entry point for applications; it stores no data. It parses queries and routes requests to the correct Shard based on metadata from the Config Server.
2.  **Config Servers**:
    *   儲存叢集的 Metadata（哪個 Chunk 屬於哪個 Shard）。這是整個叢集的「大腦」。
    *   Stores cluster metadata (mapping of Chunks to Shards). This is the "brain" of the cluster.
3.  **Shards**:
    *   實際儲存資料的節點（通常是一個 Replica Set）。
    *   The nodes that actually store data (usually a Replica Set).

### 2.2 邏輯概念：Chunk 與 Balancer (Logical Concepts: Chunk & Balancer)

*   **Chunk**: MongoDB 將資料分割成連續的範圍（Range），稱為 Chunk（預設 64MB）。Chunk 是資料遷移的最小單位。
    **Chunk:** MongoDB partitions data into contiguous ranges called Chunks (default 64MB). A Chunk is the atomic unit of data migration.
*   **Balancer**: 一個背景執行緒（運行在 Config Server Primary 上），監控各 Shard 的 Chunk 數量。當分佈不均時，它會自動搬移 Chunk。
    **Balancer:** A background thread (running on the Config Server Primary) that monitors the number of Chunks on each Shard. It automatically migrates Chunks when distribution is uneven.

### 2.3 類比 (Analogy)

想像一個**巨型圖書館**（Database）：
*   **Shards** 是不同的「樓層」，每層樓有自己的管理員（Replica Set）。
*   **Config Server** 是「圖書目錄索引系統」，記錄哪本書在哪層樓的哪個架子上。
*   **Mongos** 是「櫃台接待員」。讀者（Client）不直接跑去樓層找書，而是問接待員，接待員查目錄後告訴你去哪層樓，或者幫你把書拿來。
*   **Shard Key** 是圖書的「分類號」。如果分類號設計得不好（例如全部用出版年份），所有新書都會堆到同一層樓（Hot Shard），導致該層樓爆滿，其他樓層卻很空。

Imagine a **Giant Library** (Database):
*   **Shards** are different "floors," each with its own librarians (Replica Set).
*   **Config Server** is the "Card Catalog System," recording which book is on which shelf on which floor.
*   **Mongos** is the "Receptionist." Readers (Clients) don't run to floors directly; they ask the receptionist, who checks the catalog and directs them or retrieves the book.
*   **Shard Key** is the "Call Number." If the call number is poorly designed (e.g., strictly by publication year), all new books will pile up on one floor (Hot Shard), causing congestion while other floors remain empty.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design 面試或實務架構中，引入 Sharding 是一個重大決策（One-way door decision mostly）。

In System Design interviews or production architecture, introducing Sharding is a major decision (mostly a one-way door decision).

### 3.1 何時需要 Sharding？ (When to Shard?)

通常建議在以下情況考慮 Sharding：
It is generally recommended to consider Sharding when:

1.  **RAM 限制 (RAM Constraint)**: Working Set 大小超過單機 RAM，導致頻繁 Disk I/O。
    **RAM Constraint:** The Working Set size exceeds the single node's RAM, causing frequent Disk I/O.
2.  **儲存限制 (Storage Constraint)**: 單一節點資料量接近 2TB - 4TB（備份與復原變得極其困難）。
    **Storage Constraint:** Single node data volume approaches 2TB - 4TB (backup and recovery become extremely difficult).
3.  **寫入瓶頸 (Write Bottleneck)**: 寫入請求超過單一 Primary 的處理能力。
    **Write Bottleneck:** Write requests exceed the capacity of a single Primary.

### 3.2 架構權衡 (Architectural Trade-offs)

*   **優點 (Pros)**: 無限的儲存空間、線性的寫入擴展能力。
    **Pros:** Infinite storage space, linear write scalability.
*   **缺點 (Cons)**:
    *   **維運成本 (Operational Cost)**: 需要管理更多的節點。
    *   **查詢延遲 (Query Latency)**: 跨分片查詢（Scatter-Gather）會有較高的延遲。
    *   **事務限制 (Transaction Limits)**: 雖然 MongoDB 4.2+ 支援跨分片事務（Distributed Transactions），但效能開銷遠高於單機事務。
    *   **Operational Cost:** Requires managing more nodes.
    *   **Query Latency:** Cross-shard queries (Scatter-Gather) have higher latency.
    *   **Transaction Limits:** Although MongoDB 4.2+ supports Distributed Transactions, the performance overhead is significantly higher than single-node transactions.

---

# 4. 逐步示例：訂單系統的 Shard Key 選擇 (Walkthrough: Choosing a Shard Key for an Order System)

### 背景 (Context)
我們正在設計一個高併發的電商訂單系統。
`Orders` collection 結構如下：
We are designing a high-concurrency e-commerce order system.
The `Orders` collection structure is as follows:

```json
{
  "_id": ObjectId("..."),
  "user_id": 12345,
  "order_date": ISODate("2023-10-27T10:00:00Z"),
  "status": "CREATED",
  "total": 100.00
}
```

### 嘗試 1：使用 `_id` 或 `order_date` (Ranged Sharding)
**Naive Approach:** Use `_id` or `order_date`.

*   **想法**: `_id` 是唯一的，且預設有索引。
    **Idea:** `_id` is unique and indexed by default.
*   **問題**: `ObjectId` 和 `order_date` 都是**單調遞增 (Monotonically Increasing)** 的。
    **Problem:** Both `ObjectId` and `order_date` are **Monotonically Increasing**.
*   **結果**:
    *   所有新的寫入都會落在範圍最大的那個 Chunk（Max Chunk）。
    *   這個 Chunk 永遠只會存在於一個 Shard 上。
    *   **結論**: 造成 **Hot Shard**，寫入效能完全沒有擴展，Balancer 忙於搬運舊資料，但新資料永遠打在同一個節點。
    *   **Result:** All new writes fall into the Chunk with the highest range (Max Chunk). This Chunk resides on only one Shard. **Conclusion:** Creates a **Hot Shard**. Write performance does not scale at all. The Balancer is busy moving old data, but new data always hits the same node.

### 嘗試 2：使用 `user_id` (Hashed Sharding)
**Better Approach:** Use `user_id` with Hashed Sharding.

*   **配置**:
    **Configuration:**
    ```javascript
    sh.shardCollection("ecommerce.orders", { user_id: "hashed" })
    ```
*   **機制**: MongoDB 會計算 `user_id` 的雜湊值，並根據雜湊值範圍進行分片。
    **Mechanism:** MongoDB computes the hash of `user_id` and shards based on the hash range.
*   **優點**: 即使 `user_id` 是連續的（如 1001, 1002），雜湊後會分散到不同 Shard。寫入均勻分佈。
    **Pros:** Even if `user_id` is sequential (e.g., 1001, 1002), the hashes will be distributed across different Shards. Writes are evenly distributed.
*   **缺點**: 如果查詢條件不包含 `user_id`（例如 `db.orders.find({order_date: ...})`），Mongos 必須查詢**所有** Shard 並合併結果（Scatter-Gather），效率較差。
    **Cons:** If the query does not include `user_id` (e.g., `db.orders.find({order_date: ...})`), Mongos must query **all** Shards and merge the results (Scatter-Gather), which is less efficient.

### 嘗試 3：複合分片鍵 (Compound Sharding / Zone Sharding)
**Advanced Approach:** Compound Sharding / Zone Sharding.

*   **場景**: 我們希望寫入分散，但又希望同一地區的訂單在一起以優化讀取。
    **Scenario:** We want distributed writes, but also want orders from the same region to be co-located to optimize reads.
*   **Key**: `{ region: 1, _id: 1 }`
*   **分析**:
    *   如果 `region` 的基數（Cardinality）很低（例如只有 "US", "EU", "AP"），這會導致 **Jumbo Chunks**，因為單一 region 的資料量可能超過 Chunk 上限且無法分割（因為 `region` 值相同）。
    *   **修正**: `{ region: 1, user_id: "hashed" }` 可能是更好的選擇，或者使用 Zone Sharding 將特定範圍綁定到特定 Shard。
    *   **Analysis:** If the cardinality of `region` is low (e.g., only "US", "EU", "AP"), this leads to **Jumbo Chunks**, as data for a single region might exceed the Chunk limit and cannot be split (since the `region` value is identical). **Fix:** `{ region: 1, user_id: "hashed" }` might be better, or use Zone Sharding to bind specific ranges to specific Shards.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 選擇低基數 (Low Cardinality) 的 Shard Key
**Choosing a Low Cardinality Shard Key**

*   **錯誤**: 使用 `status` (只有 "active", "inactive") 或 `country` (只有少數幾個) 作為 Shard Key。
    **Mistake:** Using `status` (only "active", "inactive") or `country` (only a few) as the Shard Key.
*   **後果**: **Jumbo Chunks**。當一個 Key 值對應的資料量超過 Chunk Size (64MB)，MongoDB 無法分割該 Chunk（因為 Key 值都一樣）。這會導致該 Chunk 無法遷移，造成資料分佈嚴重不均。
    **Consequence:** **Jumbo Chunks**. When data for a single Key value exceeds the Chunk Size (64MB), MongoDB cannot split that Chunk (since the Key values are identical). This makes the Chunk immovable, causing severe data imbalance.
*   **解法**: 增加 Key 的維度，例如 `{ country: 1, user_id: 1 }`。
    **Solution:** Increase the dimensions of the Key, e.g., `{ country: 1, user_id: 1 }`.

### 5.2 依賴 Scatter-Gather 查詢
**Relying on Scatter-Gather Queries**

*   **錯誤**: 在分片叢集中，頻繁執行不帶 Shard Key 的查詢。
    **Mistake:** Frequently executing queries without the Shard Key in a sharded cluster.
*   **後果**: 每個查詢都會廣播到所有 Shard。隨著 Shard 數量增加，查詢延遲會線性增加，且會消耗所有 Shard 的 CPU/IO。
    **Consequence:** Every query is broadcast to all Shards. As the number of Shards increases, query latency increases linearly, and it consumes CPU/IO on all Shards.
*   **解法**: 應用程式設計必須配合 Shard Key，確保 90% 以上的查詢是 **Targeted Query**（帶有 Shard Key）。
    **Solution:** Application design must align with the Shard Key, ensuring >90% of queries are **Targeted Queries** (include the Shard Key).

### 5.3 過晚分片 (Sharding Too Late)
**Sharding Too Late**

*   **錯誤**: 等到磁碟已滿 90% 或 CPU 100% 時才開始啟用 Sharding。
    **Mistake:** Waiting until disk is 90% full or CPU is at 100% to enable Sharding.
*   **後果**: Sharding 初始化需要大量的資料平衡（Chunk Migration），這會產生極高的 I/O 負載。在系統已經過載的情況下進行 Migration，通常會導致系統崩潰。
    **Consequence:** Sharding initialization requires massive data balancing (Chunk Migration), generating very high I/O load. Performing Migration on an already overloaded system often leads to system collapse.
*   **Rule of Thumb**: 在資源使用率達到 60%-70% 時就應該開始規劃並實施 Sharding。
    **Rule of Thumb:** Plan and implement Sharding when resource usage hits 60%-70%.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何為「IoT 感測器數據」選擇 Shard Key？
**How would you choose a Shard Key for "IoT Sensor Data"?**

*   **情境**: 寫入量極大，查詢通常是「某個設備最近一小時的數據」。
    **Scenario:** Massive write volume; queries are usually "data for a specific device in the last hour."
*   **高分回答要點**:
    *   **陷阱**: 不能只用 `timestamp`（會導致 Hot Shard）。
    *   **陷阱**: 不能只用 `device_id`（如果某個設備發送頻率極高，會導致單一 Shard 熱點；且查詢時間範圍時效率不佳）。
    *   **推薦**: 複合鍵 `{ device_id: 1, timestamp: 1 }`。
        *   `device_id` 確保同一設備資料在一起（利於查詢）。
        *   如果 `device_id` 是單調的（如 UUID），需考慮 Hashed Sharding `{ device_id: "hashed" }` 以分散寫入。
        *   或者使用 `{ sensor_group: 1, timestamp: 1 }` 配合 Zone Sharding。
    *   **Key Points:** Avoid pure `timestamp` (Hot Shard). Avoid pure `device_id` (potential hotspots if one device is chatty). Recommend Compound Key `{ device_id: 1, timestamp: 1 }`. This keeps device data together (good for reads). If `device_id` causes hotspots, consider `{ device_id: "hashed" }`.

### Q2: 什麼是 Jumbo Chunk？如何處理它？
**What is a Jumbo Chunk, and how do you handle it?**

*   **定義**: 一個 Chunk 的大小超過了設定上限（預設 64MB），且因為其中所有文件的 Shard Key 值都相同（或無法找到分割點），導致無法被 Split。
    **Definition:** A Chunk that exceeds the configured limit (default 64MB) and cannot be split because all documents within it have the same Shard Key value (or no split point can be found).
*   **影響**: Balancer 無法搬移 Jumbo Chunk，導致某些 Shard 數據量遠大於其他 Shard。
    **Impact:** The Balancer cannot move Jumbo Chunks, causing some Shards to hold significantly more data than others.
*   **處理**:
    1.  **短期**: `sh.splitAt()` 手動分割（如果 Key 值不完全相同）。
    2.  **長期**: 修改 Shard Key（Refine Shard Key），增加更細粒度的欄位（例如從 `country` 改為 `country + city`）。注意：MongoDB 4.2 之前無法修改 Shard Key，4.2+ 支援 Refine Shard Key。
    **Handling:** 1. **Short-term:** `sh.splitAt()` manually (if Key values aren't identical). 2. **Long-term:** Refine the Shard Key by adding a more granular field (e.g., change `country` to `country + city`). Note: Shard Key modification was not possible before 4.2; 4.2+ supports Refine Shard Key.

### Q3: Sharding 對 ACID 事務的影響？
**Impact of Sharding on ACID Transactions?**

*   **回答**:
    *   單一 Shard 內的事務效能與 Replica Set 無異。
    *   **跨 Shard 事務 (Cross-Shard Transactions)**：MongoDB 4.2+ 支援，使用 Two-Phase Commit (2PC)。
    *   **代價**: 網路延遲增加，鎖定時間變長，吞吐量顯著下降。
    *   **設計原則**: 盡量讓事務發生在單一 Shard 內（透過正確的 Shard Key 設計將相關數據路由到同一 Shard）。
    **Answer:** Single-Shard transactions perform like Replica Sets. **Cross-Shard Transactions:** Supported in 4.2+ via Two-Phase Commit (2PC). **Cost:** Increased network latency, longer lock times, significantly reduced throughput. **Design Principle:** Keep transactions within a single Shard whenever possible (by routing related data to the same Shard via Shard Key design).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Shard Key 是生殺大權**: 決定了寫入分佈（Write Distribution）與查詢路由（Query Routing）。
2.  **三大原則**: 選擇 Shard Key 時需考量 **Cardinality** (夠多值)、**Frequency** (分佈均勻)、**Monotonicity** (避免單調遞增)。
3.  **Ranged vs. Hashed**: Ranged 適合範圍查詢但易產生熱點；Hashed 適合均勻寫入但範圍查詢效能差。
4.  **Mongos & Config Server**: 理解 Router 與 Metadata 儲存的角色，它們是叢集運作的基礎。
5.  **避免 Scatter-Gather**: 應用層查詢應盡量包含 Shard Key。
6.  **Jumbo Chunk 是惡夢**: 避免低基數欄位作為分片鍵。

### 後續延伸 (Next Steps)
*   **Chapter 08: Indexing & Performance Tuning**: Sharding 解決了擴展問題，但單一節點的查詢效能仍依賴索引。下一步將深入探討 ESR Rule、Covered Queries 與執行計畫分析。
    **Chapter 08: Indexing & Performance Tuning:** Sharding solves scaling, but single-node query performance still relies on indexing. Next, we dive into the ESR Rule, Covered Queries, and Execution Plan analysis.
*   **實作練習**: 使用 Docker Compose 架設一個包含 2 個 Shard、1 個 Config Server Replica Set、1 個 Mongos 的本地叢集，並模擬寫入大量數據觀察 Chunk Migration。
    **Practical Exercise:** Use Docker Compose to set up a local cluster with 2 Shards, 1 Config Server Replica Set, and 1 Mongos. Simulate massive data writes and observe Chunk Migration.