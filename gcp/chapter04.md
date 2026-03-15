# 資料儲存與資料庫選型策略
# Data Storage & Database Selection Strategy

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在系統設計面試（System Design Interview）與高併發架構實作中，資料庫的選型往往是決定系統成敗的關鍵。GCP 提供了多樣化的託管資料庫服務，每一種都有其特定的「甜蜜點」與取捨。
In System Design Interviews and high-concurrency architecture implementations, database selection is often the critical factor determining success or failure. GCP offers a diverse range of managed database services, each with its specific "sweet spot" and trade-offs.

完成本章後，身為資深工程師的你應該能夠：
By the end of this chapter, as a Senior Engineer, you should be able to:

1.  **精準映射需求至服務**：根據 ACID 需求、吞吐量（Throughput）、延遲（Latency）與資料規模，在 Cloud SQL, Spanner, Bigtable, Firestore 之間做出正確選擇。
    **Map Requirements to Services:** Accurately select between Cloud SQL, Spanner, Bigtable, and Firestore based on ACID requirements, throughput, latency, and data scale.
2.  **理解 Spanner 的魔力與代價**：解釋 Cloud Spanner 如何利用 TrueTime API 實現全球強一致性（External Consistency），以及何時該避免使用它（成本與延遲考量）。
    **Understand Spanner's Magic & Cost:** Explain how Cloud Spanner uses the TrueTime API to achieve global External Consistency, and when to avoid it (cost and latency considerations).
3.  **掌握 Bigtable 的 Schema 設計**：理解為什麼 Bigtable 的 Row Key 設計決定了效能，並能避免常見的熱點（Hotspotting）問題。
    **Master Bigtable Schema Design:** Understand why Bigtable's Row Key design dictates performance and how to avoid common hotspotting issues.
4.  **區分 OLTP 與高吞吐寫入場景**：清楚界定何時使用 Cloud SQL（垂直擴展限制）與何時必須轉向 Spanner 或 Bigtable（水平擴展）。
    **Distinguish OLTP vs. High-Throughput Write Scenarios:** Clearly define when to use Cloud SQL (vertical scaling limits) versus when to pivot to Spanner or Bigtable (horizontal scaling).

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 選型決策矩陣 (The Selection Matrix)

我們可以將 GCP 的核心資料庫服務視為一個四象限的決策模型，軸線分別為「關聯性/交易 (Relational/Transactional)」與「規模/擴展性 (Scale/Scalability)」。
We can visualize GCP's core database services as a four-quadrant decision model, with axes being "Relational/Transactional" and "Scale/Scalability".

1.  **Cloud SQL (The Reliable Sedan)**
    *   **類比**：標準房車。適合大多數標準旅程，維護容易，但在極端負載下引擎（單機）有極限。
    *   **定義**：全託管的 MySQL/PostgreSQL/SQL Server。
    *   **核心特徵**：強一致性、標準 SQL、單一區域（Regional）高可用、垂直擴展為主（Vertical Scaling）。
    *   **Analogy:** The Standard Sedan. Fits most standard journeys, easy to maintain, but the engine (single node) has limits under extreme loads.
    *   **Definition:** Fully managed MySQL/PostgreSQL/SQL Server.
    *   **Key Traits:** Strong consistency, standard SQL, Regional HA, primarily Vertical Scaling.

2.  **Cloud Spanner (The Bullet Train)**
    *   **類比**：高鐵。極快、準時（一致性）、載客量大（水平擴展），但造價昂貴且軌道（Schema）需要專門鋪設。
    *   **定義**：全球分散式關聯資料庫。
    *   **核心特徵**：水平擴展（Horizontal Scaling）、全球強一致性（Global Strong Consistency）、高達 99.999% SLA。
    *   **Analogy:** The Bullet Train. Extremely fast, punctual (consistent), high capacity (horizontal scaling), but expensive to build and requires specialized tracks (Schema).
    *   **Definition:** Global distributed relational database.
    *   **Key Traits:** Horizontal Scaling, Global Strong Consistency, up to 99.999% SLA.

3.  **Cloud Bigtable (The Cargo Ship)**
    *   **類比**：巨型貨輪。吞吐量極大，適合搬運海量貨櫃（資料），但轉向（Query 靈活性）不靈活，不適合小額交易。
    *   **定義**：Wide-column NoSQL store (HBase compatible).
    *   **核心特徵**：極高寫入/讀取吞吐量（Millions of TPS）、低延遲（ms 級）、Flat schema、不支援跨行交易。
    *   **Analogy:** The Cargo Ship. Massive throughput, moves huge containers (data), but steering (Query flexibility) is rigid; not for small transactions.
    *   **Definition:** Wide-column NoSQL store (HBase compatible).
    *   **Key Traits:** Extremely high write/read throughput (Millions of TPS), low latency (ms level), Flat schema, no cross-row transactions.

4.  **Firestore (The Smart Fleet)**
    *   **類比**：Uber/外送車隊。靈活、隨叫隨到，適合處理最後一哩路（Mobile/Web App），但不適合長途重載運輸（大型分析或極高頻寫入）。
    *   **定義**：Serverless Document NoSQL.
    *   **核心特徵**：靈活 Schema (JSON)、即時同步 (Real-time sync)、離線支援、適合 App 後端。
    *   **Analogy:** The Smart Fleet (Uber/Delivery). Flexible, on-demand, great for the "last mile" (Mobile/Web App), but not for long-haul heavy transport (heavy analytics or extreme write frequency).
    *   **Definition:** Serverless Document NoSQL.
    *   **Key Traits:** Flexible Schema (JSON), Real-time sync, Offline support, ideal for App backends.

### 2.2 關鍵差異對照 (Key Differentiators)

| Feature | Cloud SQL | Cloud Spanner | Bigtable | Firestore |
| :--- | :--- | :--- | :--- | :--- |
| **Scaling** | Vertical (Read Replicas available) | Horizontal (Unlimited) | Horizontal (Linear) | Horizontal (Auto) |
| **Consistency** | Strong (Regional) | Strong (Global w/ TrueTime) | Eventual (Strong on single row) | Strong |
| **Transactions** | ACID | ACID (Distributed) | Single-row only | ACID (Multi-document) |
| **Use Case** | General Web, ERP, CRM | Global Ledger, Inventory, High Scale SQL | IoT, AdTech, FinTech Data, Time-series | User Profiles, CMS, Mobile Apps |

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在系統設計面試或實際架構規劃中，我們通常採用「多語言持久化（Polyglot Persistence）」策略，而非單一資料庫打天下。
In system design interviews or actual architecture planning, we typically adopt a "Polyglot Persistence" strategy, rather than a "one database fits all" approach.

### 3.1 典型電商系統架構 (Typical E-commerce Architecture)

在一個大型電商系統中，這些服務通常是這樣協作的：
In a large-scale e-commerce system, these services typically collaborate as follows:

1.  **Cloud Spanner**: **庫存與訂單系統 (Inventory & Order System)**
    *   **原因**：需要絕對的強一致性（不能超賣）與高可用性。當黑色星期五流量暴衝時，Spanner 可以無縫水平擴展節點（Nodes），無需分庫分表（Sharding）的痛苦。
    *   **Reason:** Requires absolute strong consistency (no overselling) and high availability. When Black Friday traffic spikes, Spanner can seamlessly scale nodes horizontally without the pain of sharding.

2.  **Cloud SQL**: **內部管理後台 (Internal Admin Dashboard)**
    *   **原因**：資料量相對可控，關聯查詢複雜，且通常不需要全球擴展。成本效益比 Spanner 高。
    *   **Reason:** Data volume is relatively controllable, relational queries are complex, and global scaling is usually not required. More cost-effective than Spanner.

3.  **Firestore**: **使用者購物車與個人設定 (User Cart & Preferences)**
    *   **原因**：資料結構多變（JSON），需要與前端 App 快速同步。Firestore 的 Real-time listener 可以讓使用者在不同裝置間無縫同步購物車狀態。
    *   **Reason:** Variable data structure (JSON), requires fast synchronization with frontend apps. Firestore's real-time listeners allow users to seamlessly sync cart status across devices.

4.  **Bigtable**: **使用者行為歷程與推薦特徵 (User Clickstream & Recommendation Features)**
    *   **原因**：寫入量極大（每一次點擊、滑動都要紀錄），讀取延遲要求低（用於即時推薦）。資料不需要 ACID 交易，但需要極高的吞吐量。
    *   **Reason:** Massive write volume (every click/scroll recorded), low read latency required (for real-time recommendations). ACID transactions are not needed, but extreme throughput is.

### 3.2 對非功能性需求的影響 (Impact on Non-Functional Requirements)

*   **可維護性 (Maintainability)**: Cloud SQL 最容易招募人才；Spanner 減少了 Sharding 的維運負擔；Bigtable 需要專精的 Schema 設計知識。
    **Maintainability:** Cloud SQL is easiest to hire for; Spanner reduces the operational burden of sharding; Bigtable requires specialized schema design knowledge.
*   **成本 (Cost)**: Spanner 與 Bigtable 的起步成本較高（節點費用），適合大規模系統。Cloud SQL 與 Firestore 適合起步，但 Firestore 在讀寫極頻繁時成本會激增。
    **Cost:** Spanner and Bigtable have higher entry costs (node fees), suitable for large-scale systems. Cloud SQL and Firestore are good for starting, but Firestore costs can spike with extremely frequent reads/writes.

---

## 4. 逐步示例：設計全球票務系統
## 4. Walkthrough: Designing a Global Ticketing System

### 背景 (Context)
我們需要設計一個全球演唱會售票系統。
**需求**：
1.  全球使用者同時搶票。
2.  絕對不能超賣（Strict Consistency）。
3.  極高的併發寫入（High Concurrent Writes）。

We need to design a global concert ticketing system.
**Requirements:**
1.  Global users buying tickets simultaneously.
2.  Absolutely no overselling (Strict Consistency).
3.  Extremely high concurrent writes.

### 演進過程 (Evolution)

#### Phase 1: Naive Approach - Cloud SQL
最直覺的選擇是使用 Cloud SQL (PostgreSQL)。
The most intuitive choice is Cloud SQL (PostgreSQL).

*   **做法**：使用 `TRANSACTION ISOLATION LEVEL SERIALIZABLE` 鎖定座位表。
*   **問題**：
    1.  **鎖競爭 (Lock Contention)**：當數萬人同時搶同一個熱門區域的票，DB 會陷入鎖等待，導致 Timeout。
    2.  **地域限制 (Regional Limit)**：Cloud SQL 是 Regional 的，亞洲使用者連線到美國主庫會有高延遲。
*   **Approach:** Use `TRANSACTION ISOLATION LEVEL SERIALIZABLE` to lock the seat table.
*   **Problem:**
    1.  **Lock Contention:** When tens of thousands try to buy tickets in the same hot zone, the DB gets stuck in lock waits, causing timeouts.
    2.  **Regional Limit:** Cloud SQL is regional; Asian users connecting to a US primary will experience high latency.

#### Phase 2: High Throughput Attempt - Bigtable
為了決解效能問題，考慮使用 Bigtable。
To solve performance issues, we consider Bigtable.

*   **做法**：將每個座位設計為一個 Row Key。
*   **問題**：Bigtable 僅支援「單行原子性 (Single-row atomicity)」。如果一個訂單包含多張票（多個 Rows），我們無法保證「要嘛全買到，要嘛全失敗」，除非在應用層實作複雜的兩階段提交（2PC），這極易出錯。
*   **Approach:** Design each seat as a Row Key.
*   **Problem:** Bigtable only supports "Single-row atomicity". If an order includes multiple tickets (multiple rows), we cannot guarantee "all or nothing" without implementing complex Two-Phase Commit (2PC) in the application layer, which is error-prone.

#### Phase 3: The Optimal Solution - Cloud Spanner
最終選擇 Cloud Spanner。
Finally, we choose Cloud Spanner.

*   **做法**：
    1.  建立 Spanner Instance（Multi-region 配置）。
    2.  Schema 設計避免熱點（不要使用序列號作為 Primary Key）。
    3.  利用 Spanner 的分散式交易處理訂單。

*   **Approach:**
    1.  Create a Spanner Instance (Multi-region configuration).
    2.  Schema design to avoid hotspots (Do not use sequential numbers as Primary Keys).
    3.  Use Spanner's distributed transactions to handle orders.

*   **Code Example (Schema Design):**

```sql
-- Anti-Pattern: Sequential ID causes hotspotting during inserts
-- CREATE TABLE Tickets (
--   TicketId INT64 NOT NULL, -- 1, 2, 3... all hit the same split
--   EventId INT64,
--   Status STRING(MAX)
-- ) PRIMARY KEY (TicketId);

-- Best Practice: UUID or Bit-reversed sequence
CREATE TABLE Tickets (
  TicketId STRING(36) NOT NULL, -- UUID distributes load across splits
  EventId INT64,
  SeatNumber STRING(10),
  Status STRING(20),
  UserId STRING(36)
) PRIMARY KEY (TicketId);

-- Interleaved Table for Order Details (Data Locality optimization)
CREATE TABLE Orders (
  OrderId STRING(36) NOT NULL,
  UserId STRING(36),
  TotalAmount FLOAT64
) PRIMARY KEY (OrderId);

CREATE TABLE OrderItems (
  OrderId STRING(36) NOT NULL,
  ItemId INT64 NOT NULL,
  TicketId STRING(36),
  Price FLOAT64
) PRIMARY KEY (OrderId, ItemId),
  INTERLEAVE IN PARENT Orders ON DELETE CASCADE;
```

*   **為何可行**：Spanner 自動將資料分片（Splits）並分散到不同節點。UUID 主鍵確保寫入流量均勻分佈，避免單一節點過載。`INTERLEAVE` 讓訂單明細與訂單主檔存在物理上的同一處，加速查詢。
*   **Why it works:** Spanner automatically shards data (Splits) across nodes. UUID primary keys ensure write traffic is evenly distributed, avoiding single-node overload. `INTERLEAVE` keeps order details physically co-located with the order master record, speeding up queries.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 Bigtable Row Key 熱點 (Hotspotting)
*   **錯誤**：使用時間戳記（Timestamp）或連續 ID 作為 Bigtable 的 Row Key 開頭。
    *   `2023-10-27-user1`, `2023-10-27-user2`...
*   **後果**：所有新的寫入都會集中在同一個 Tablet Server，導致該節點過載，而其他節點閒置。效能極差。
*   **修正**：使用 Hashed 值或反轉 ID 作為前綴。
    *   `user1-2023-10-27`, `user2-2023-10-27` (如果查詢模式是依用戶) 或 `reverse_ts-user1`。
*   **Mistake:** Using timestamps or sequential IDs as the start of a Bigtable Row Key.
*   **Consequence:** All new writes hit the same Tablet Server, overloading that node while others sit idle. Performance tanks.
*   **Fix:** Use hashed values or reversed IDs as a prefix.

### 5.2 誤用 Firestore 進行高頻計數 (High-frequency Counters)
*   **錯誤**：在 Firestore 中使用單一 Document 來儲存全站「按讚數」或「瀏覽數」，且每秒更新數百次。
*   **後果**：Firestore 對單一 Document 的寫入限制約為 1 QPS (soft limit) 到數次 QPS。超過會導致爭用與延遲。
*   **修正**：使用 "Distributed Counters"（分散式計數器），將計數分散到 N 個 Sub-documents，讀取時加總。
*   **Mistake:** Using a single Document in Firestore to store global "likes" or "views", updating hundreds of times per second.
*   **Consequence:** Firestore has a write limit of ~1 QPS (soft limit) to a few QPS per single document. Exceeding this causes contention and latency.
*   **Fix:** Use "Distributed Counters", sharding the count across N sub-documents and summing them on read.

### 5.3 在 Cloud SQL 上執行重型分析 (OLAP on OLTP)
*   **錯誤**：直接在 Production 的 Cloud SQL 上跑 `SELECT * FROM Orders GROUP BY ...` 進行年度報表分析。
*   **後果**：消耗大量 CPU/IO，拖慢即時交易使用者的回應速度，甚至導致服務中斷。
*   **修正**：
    1.  使用 Read Replica 進行分析。
    2.  (更好) 將資料同步到 BigQuery 進行 OLAP 分析。
*   **Mistake:** Running heavy `SELECT * FROM Orders GROUP BY ...` directly on the Production Cloud SQL for annual reporting.
*   **Consequence:** Consumes massive CPU/IO, slowing down response times for real-time transactional users, potentially causing outages.
*   **Fix:**
    1.  Use a Read Replica for analytics.
    2.  (Better) Sync data to BigQuery for OLAP analytics.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

在面試中，這些問題能展現你對 GCP 資料庫的深度理解：
In an interview, these questions demonstrate your deep understanding of GCP databases:

### Q1: "我們現有的 MySQL 分庫分表（Sharding）維護成本太高，遷移到 Spanner 值得嗎？"
### Q1: "Our current MySQL sharding maintenance cost is too high. Is migrating to Spanner worth it?"

*   **高分回答要點 (Key Points for a High Score):**
    *   **成本分析**：Spanner 的運算節點昂貴（每小時計費），需對比 MySQL 的維運人力成本 + 停機風險成本。
    *   **延遲考量**：Spanner 的寫入延遲（因 Paxos 跨區同步）通常高於單機 MySQL。應用程式能否接受稍高的 Latency？
    *   **SQL 相容性**：雖然 Spanner 支援 PostgreSQL Interface，但並非 100% 相容，Stored Procedures 或特定 Trigger 可能需要重寫。
    *   **結論**：如果業務需要全球擴展且強一致性，且預算允許，Spanner 是首選；若只是單一區域流量大，升級 Cloud SQL Enterprise Plus 或許更划算。

### Q2: "如何設計一個儲存 IoT 傳感器數據的系統，每秒寫入 50,000 筆資料？"
### Q2: "How would you design a system to store IoT sensor data with 50,000 writes per second?"

*   **高分回答要點 (Key Points for a High Score):**
    *   **選型**：首選 Bigtable。Cloud SQL 無法承受此持續寫入量；Spanner 成本過高且非必要（IoT 數據通常不需要跨行交易）。
    *   **Row Key 設計**：`[SensorID]#[ReverseTimestamp]`。這樣可以讓針對特定 Sensor 的查詢很快（連續掃描），同時避免單調時間戳造成的熱點（如果 SensorID 分佈夠廣）。
    *   **資料生命週期**：設定 Garbage Collection (GC) policy，自動刪除超過 1 年的舊資料以節省成本。

### Q3: "Firestore 與 Bigtable 都是 NoSQL，我該如何選擇？"
### Q3: "Firestore and Bigtable are both NoSQL. How do I choose?"

*   **高分回答要點 (Key Points for a High Score):**
    *   **維度 1：查詢模式**。Firestore 支援多個欄位的索引與查詢（Where X=1 AND Y=2）；Bigtable 基本上只能靠 Row Key 查詢（Key-Value lookup or Range scan）。
    *   **維度 2：資料量與吞吐**。Bigtable 是為了 PB 級資料與百萬級 TPS 設計的；Firestore 適合 GB/TB 級與 App 端的靈活開發。
    *   **維度 3：客戶端**。Firestore 直接支援 Mobile/Web SDK (Serverless)；Bigtable 通常需要一層 Backend Server。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Cloud SQL**: 傳統應用、關聯資料、單一區域、垂直擴展。 (The Sedan)
2.  **Cloud Spanner**: 全球應用、強一致性、水平擴展、金融級交易。 (The Bullet Train)
3.  **Bigtable**: 海量寫入、時間序列/IoT、Flat Schema、Row Key 設計是關鍵。 (The Cargo Ship)
4.  **Firestore**: 快速開發、Mobile/Web App、靈活 JSON、即時同步。 (The Smart Fleet)
5.  **Spanner 的 TrueTime**: 讓分散式資料庫擁有外部一致性（External Consistency），是 Google 的獨門絕技。
6.  **反模式警示**: 避免在 Bigtable 使用連續 ID/時間戳當 Key；避免在 Firestore 單點高頻寫入。

### 後續延伸 (Next Steps)
*   **Next Chapter**: 既然資料存下來了，如何加速讀取？下一章將探討 **Caching Strategy & Memorystore**（Redis/Memcached 在 GCP 的應用）。
*   **Action Item**: 試著在 GCP Console 開一台最小的 Spanner Instance（注意成本，用完即刪），體驗一下它的 Web UI 查詢與 Schema 定義，並嘗試用 `gcloud` 指令調整節點數量，感受「一鍵擴展」的威力。