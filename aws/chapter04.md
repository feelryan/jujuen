# 1. 前言與學習目標 (Introduction & Learning Objectives)

在系統設計（System Design）面試與高併發實務中，「資料庫選型」往往是決定系統上限的關鍵。資深工程師不應只停留在 "SQL vs NoSQL" 的粗淺二分法，而必須深入理解 AWS 託管服務（Managed Services）底層的儲存架構、一致性模型與擴展限制。

In System Design interviews and high-concurrency production scenarios, "Database Selection" is often the critical factor determining the system's ceiling. Senior engineers should not stop at the superficial dichotomy of "SQL vs NoSQL," but must deeply understand the underlying storage architecture, consistency models, and scaling limitations of AWS Managed Services.

完成本章後，你將能夠：

By the end of this chapter, you will be able to:

1.  **精準評估 RDS/Aurora 與 DynamoDB 的取捨**：基於讀寫模式（Access Patterns）、資料關聯度與擴展需求，做出合乎成本效益的架構決策。
    **Accurately evaluate trade-offs between RDS/Aurora and DynamoDB:** Make cost-effective architectural decisions based on Access Patterns, data relational complexity, and scaling requirements.
2.  **掌握 Polyglot Persistence（多語言持久化）策略**：理解何時該引入 TimeStream（時序）、Neptune（圖形）等專用資料庫，避免「一支槌子敲所有釘子」。
    **Master Polyglot Persistence strategies:** Understand when to introduce specialized databases like TimeStream (time-series) or Neptune (graph), avoiding the "everything looks like a nail" anti-pattern.
3.  **在面試中展現架構深度**：能夠解釋 Aurora 的 Log-Structured Storage 如何解決傳統 MySQL 的瓶頸，以及 DynamoDB 的 Partitioning 機制如何影響熱點（Hot Partition）問題。
    **Demonstrate architectural depth in interviews:** Explain how Aurora's Log-Structured Storage solves traditional MySQL bottlenecks, and how DynamoDB's Partitioning mechanism affects Hot Partition issues.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 關聯式資料庫的雲端進化：Aurora vs. Traditional RDS
## (Cloud Evolution of RDBMS: Aurora vs. Traditional RDS)

傳統 RDS（如標準 MySQL on EBS）受限於單機 I/O 瓶頸與同步複製的延遲。**Amazon Aurora** 的核心心智模型是「將運算（Compute）與儲存（Storage）徹底分離」。

Traditional RDS (like standard MySQL on EBS) is limited by single-instance I/O bottlenecks and synchronous replication latency. The core mental model of **Amazon Aurora** is the "complete separation of Compute and Storage."

-   **The Log is the Database**: Aurora 不像傳統 DB 需要寫入 Data Pages 到磁碟，它主要寫入 Redo Logs。這大幅減少了網路 I/O。
    **The Log is the Database**: Unlike traditional DBs that need to write Data Pages to disk, Aurora primarily writes Redo Logs. This drastically reduces network I/O.
-   **Quorum Model**: 資料被複製成 6 份並分散在 3 個 AZ。寫入只需 4/6 成功，讀取只需 3/6 確認。這保證了極高的可用性與容錯能力。
    **Quorum Model**: Data is replicated 6 ways across 3 AZs. Writes require 4/6 success; reads require 3/6 confirmation. This guarantees extremely high availability and fault tolerance.

## 2.2 NoSQL 的極致擴展：DynamoDB
## (Extreme Scaling of NoSQL: DynamoDB)

DynamoDB 的心智模型是「分散式雜湊表（Distributed Hash Table）」。它不關心資料之間的「關係（Relations）」，只關心如何透過 **Partition Key (PK)** 快速定位資料所在的實體節點。

The mental model for DynamoDB is a "Distributed Hash Table." It does not care about "Relations" between data, but only about how to quickly locate the physical node containing the data via the **Partition Key (PK)**.

-   **Access Pattern Driven**: 在 SQL 中，我們先設計 Schema 再寫 Query；在 DynamoDB 中，我們先確定 Query（Access Patterns）再設計 Schema。
    **Access Pattern Driven**: In SQL, we design the Schema first, then write Queries; in DynamoDB, we define Queries (Access Patterns) first, then design the Schema.
-   **Predictable Performance**: 無論資料量是 1 GB 還是 100 TB，只要沒有熱點（Hot Key），透過 PK 讀取的時間複雜度皆為 O(1)。
    **Predictable Performance**: Whether the data size is 1 GB or 100 TB, as long as there are no Hot Keys, the time complexity for reading via PK remains O(1).

## 2.3 專用資料庫 (Purpose-Built Databases)

當通用資料庫的 schema 設計變得極度彆扭或效能低落時，應考慮專用資料庫：

When schema design in general-purpose databases becomes extremely awkward or performance degrades, consider purpose-built databases:

-   **Amazon Neptune (Graph)**: 解決「朋友的朋友的朋友」這類遞迴查詢（Recursive Queries）。在 SQL 中這是昂貴的 Self-Join，在 Graph DB 中是高效的指標遍歷。
    **Amazon Neptune (Graph)**: Solves recursive queries like "friends of friends of friends." In SQL, this is an expensive Self-Join; in a Graph DB, it's efficient pointer traversal.
-   **Amazon Timestream (Time Series)**: 針對 IoT 或 DevOps 監控數據。特點是寫入量極大、資料不可變（Immutable）、且查詢常涉及時間區間聚合（Window Aggregation）。
    **Amazon Timestream (Time Series)**: Targeted at IoT or DevOps monitoring data. Characterized by massive write volume, immutable data, and queries often involving time-window aggregation.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，我們通常採用 **Polyglot Persistence（多語言持久化）**。以下是一個典型的電商或社交平台架構決策矩陣。

In large-scale distributed systems, we typically adopt **Polyglot Persistence**. Below is a typical architectural decision matrix for an e-commerce or social platform.

## 3.1 架構決策矩陣 (Architectural Decision Matrix)

| Component | Requirement | Recommended Service | Rationale (System Design Justification) |
| :--- | :--- | :--- | :--- |
| **User Profile / Auth** | Structured data, moderate scale, high consistency. | **Aurora (PostgreSQL)** | 關聯性強（User -> Roles -> Permissions），且需要 ACID 保證。Aurora 提供比 RDS 更快的 Failover。<br>Strong relationships, requires ACID guarantees. Aurora offers faster failover than standard RDS. |
| **Shopping Cart / Session** | High throughput, ephemeral, key-value access. | **DynamoDB** | 購物車是典型的 Key-Value 存取。DynamoDB 的 TTL 功能可自動清理過期 Session。<br>Carts are typical Key-Value access. DynamoDB's TTL feature automatically cleans up expired sessions. |
| **Order History** | Transactional integrity, complex reporting queries. | **Aurora** | 訂單狀態流轉嚴格依賴 Transaction。報表查詢需要 SQL 的 JOIN 能力。<br>Order state transitions strictly rely on Transactions. Reporting requires SQL JOIN capabilities. |
| **Product Catalog** | High read, low write, flexible attributes. | **DynamoDB (or DocumentDB)** | 商品屬性差異大（衣服 vs 電器），NoSQL 的 Schema-less 特性適合。讀取量大可透過 DAX 加速。<br>Product attributes vary widely; NoSQL's schema-less nature fits. High reads can be accelerated via DAX. |
| **Social Graph / Recommendations** | "Who bought also bought", "Mutual friends". | **Neptune** | 關聯查詢深度超過 2 層時，SQL 效能會指數級下降。<br>SQL performance degrades exponentially when relationship query depth exceeds 2 levels. |
| **Clickstream / Audit Logs** | High volume write, time-based queries. | **Timestream / S3 + Athena** | 寫入吞吐量是瓶頸。近期熱資料用 Timestream，長期冷資料存 S3 並用 Athena 查詢。<br>Write throughput is the bottleneck. Use Timestream for recent hot data, S3 + Athena for long-term cold data. |

## 3.2 CQRS (Command Query Responsibility Segregation) 模式

在 System Design 面試中，若被問及「如何同時滿足高併發寫入與複雜搜尋需求？」，標準答案通常涉及 CQRS：

In System Design interviews, if asked "How to handle both high-concurrency writes and complex search requirements?", the standard answer often involves CQRS:

1.  **Write Side**: 應用程式寫入 **DynamoDB**（優化寫入效能與可用性）。
    **Write Side**: Application writes to **DynamoDB** (optimized for write performance and availability).
2.  **Stream**: 啟用 **DynamoDB Streams** 捕捉變更。
    **Stream**: Enable **DynamoDB Streams** to capture changes.
3.  **Process**: 透過 **Lambda** 處理串流資料。
    **Process**: Process stream data via **Lambda**.
4.  **Read Side**: 將資料同步至 **OpenSearch**（全文檢索）或 **Aurora**（複雜報表）。
    **Read Side**: Sync data to **OpenSearch** (full-text search) or **Aurora** (complex reporting).

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：設計一個高併發的「按讚」系統 (Designing a High-Concurrency "Likes" System)

**背景 (Context)**：社群平台，熱門貼文可能在短時間內收到數百萬個讚。
**目標 (Goal)**：準確計數，低延遲，不遺失數據。

### 階段 1：Naive SQL Approach (Anti-pattern for Scale)

最直覺的做法是在 RDS 中更新計數器。

The most intuitive approach is updating a counter in RDS.

```sql
-- Transaction start
SELECT count FROM likes WHERE post_id = '123' FOR UPDATE;
UPDATE likes SET count = count + 1 WHERE post_id = '123';
-- Transaction commit
```

*   **問題 (Problem)**：`FOR UPDATE` 會鎖住該行（Row Lock）。當成千上萬個請求同時競爭同一把鎖，資料庫會因 Lock Contention 而癱瘓。
    **Problem**: `FOR UPDATE` locks the row. When thousands of requests compete for the same lock, the database halts due to Lock Contention.

### 階段 2：DynamoDB Atomic Counters (Better)

利用 DynamoDB 的原子更新功能。

Leveraging DynamoDB's atomic update capability.

```javascript
const params = {
  TableName: 'Posts',
  Key: { 'PostID': '123' },
  UpdateExpression: 'SET like_count = like_count + :incr',
  ExpressionAttributeValues: { ':incr': 1 }
};
await docClient.update(params).promise();
```

*   **優勢 (Pros)**：不需要鎖定，DynamoDB 在分區層級處理寫入。
    **Pros**: No locking required; DynamoDB handles writes at the partition level.
*   **限制 (Cons)**：單一 Partition 的寫入上限約為 1000 WCU (Writes/sec)。對於超級熱門貼文（如名人貼文），這仍然不夠。
    **Cons**: The write limit for a single Partition is about 1000 WCU (Writes/sec). For viral posts (e.g., celebrities), this is still insufficient.

### 階段 3：Write Aggregation / Sharding (Senior Solution)

為了突破單一 Partition 的限制，我們需要分散寫入壓力。

To break the single-partition limit, we need to distribute the write pressure.

**策略 A：Redis Buffer (Write-Back)**
先寫入 Redis，每隔 N 秒將累積的計數一次性寫入 DB。
*Trade-off*: Redis 當機可能遺失少量數據（Eventual Consistency）。

**Strategy A: Redis Buffer (Write-Back)**
Write to Redis first, then flush accumulated counts to DB every N seconds.
*Trade-off*: Redis crash might lose a small amount of data (Eventual Consistency).

**策略 B：DynamoDB Write Sharding**
將計數器分散到 N 個子項目中。

**Strategy B: DynamoDB Write Sharding**
Split the counter into N sub-items.

1.  **Schema Design**:
    *   PK: `PostID#123`
    *   SK: `Counter#0` ... `Counter#9` (Randomly pick 0-9 to write)
2.  **Write**: 隨機選擇一個 SK 進行 `ADD 1`。
    **Write**: Randomly select an SK to `ADD 1`.
3.  **Read**: 讀取該 PostID 下所有 `Counter#*` 並加總。
    **Read**: Read all `Counter#*` under that PostID and sum them up.

```javascript
// Write Logic (Simplified)
const shardId = Math.floor(Math.random() * 10);
const params = {
    TableName: 'PostLikes',
    Key: { 
        'PostID': 'post_123',
        'ShardID': `shard_${shardId}` // Distribute heat
    },
    UpdateExpression: 'ADD likes :inc',
    ExpressionAttributeValues: { ':inc': 1 }
};
```

*   **結果 (Result)**：寫入吞吐量提升 N 倍。這是處理「熱點問題（Hot Partition）」的標準解法。
    **Result**: Write throughput increases N-fold. This is the standard solution for handling "Hot Partition" issues.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 DynamoDB 上硬套關聯模型 (Relational Modeling on DynamoDB)

*   **錯誤 (Mistake)**：設計多個 Table（Users, Orders, Products），然後在 Application Code 裡面做 Join。
    **Mistake**: Designing multiple Tables (Users, Orders, Products) and then performing Joins in the Application Code.
*   **後果 (Consequence)**：產生 "N+1 Query" 問題，延遲極高，浪費 RCU（Read Capacity Units）。
    **Consequence**: Creates "N+1 Query" issues, extremely high latency, and wastes RCUs.
*   **修正 (Fix)**：使用 **Single Table Design**，利用 Partition Key 和 Sort Key 的組合來預先 Join 資料（Pre-joining data via item collections）。

## 5.2 誤用 Aurora Serverless 於持續高負載 (Misusing Aurora Serverless for Sustained High Load)

*   **錯誤 (Mistake)**：為了省錢，在生產環境的持續高流量核心服務使用 Aurora Serverless v1 (舊版) 或配置不當的 v2。
    **Mistake**: Using Aurora Serverless v1 (legacy) or improperly configured v2 for sustained high-traffic core services in production to save money.
*   **後果 (Consequence)**：Scaling 速度可能跟不上突發流量（v1），或者費用比 Provisioned Instance 更昂貴（v2 在持續負載下通常較貴）。
    **Consequence**: Scaling speed might lag behind traffic spikes (v1), or costs exceed Provisioned Instances (v2 is often pricier under sustained load).
*   **修正 (Fix)**：對於基載（Base Load）穩定的系統，使用 Provisioned Instances + Reserved Instances 節省成本。Serverless 適合開發環境或極度不穩定的工作負載。

## 5.3 忽略 DynamoDB 的強一致性成本 (Ignoring DynamoDB Strong Consistency Costs)

*   **錯誤 (Mistake)**：預設所有讀取都開啟 `ConsistentRead: true`。
    **Mistake**: Defaulting all reads to `ConsistentRead: true`.
*   **後果 (Consequence)**：讀取成本（RCU）加倍，且可用性略低於 Eventual Consistency。
    **Consequence**: Read costs (RCU) double, and availability is slightly lower than Eventual Consistency.
*   **修正 (Fix)**：只在絕對必要時（如扣庫存後立即讀取餘額）使用強一致性。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何選擇 Aurora 與 RDS PostgreSQL？
## (How to choose between Aurora and RDS PostgreSQL?)

*   **高分回答要點 (Key Points)**：
    *   **Storage Architecture**: 強調 Aurora 的儲存層是共享且自動擴展的，與 Compute 節點分離；RDS 依賴 EBS。
    *   **Replication Lag**: Aurora Replica 共享儲存，Lag 通常 < 10ms；RDS Read Replica 需透過 Binlog 重放，Lag 可能較高。
    *   **Failover**: Aurora Failover 通常 < 30s（因為不需要資料同步）；RDS 需要 DNS 傳播與資料恢復，通常 60s+。
    *   **Cost**: Aurora 較貴，適合 Tier-1 服務；RDS 適合成本敏感或標準工作負載。

## Q2: 什麼是 DynamoDB 的 Hot Partition 問題？如何解決？
## (What is the DynamoDB Hot Partition issue and how to solve it?)

*   **高分回答要點 (Key Points)**：
    *   **Definition**: 當過多請求集中在單一 Partition Key（如 `PostID`），超過了單一分區的物理限制（3000 RCU / 1000 WCU）。
    *   **Solution 1 (Write Sharding)**: 如同上述範例，在 PK 後面加上隨機後綴（Suffix）。
    *   **Solution 2 (Caching)**: 使用 DAX 或 ElastiCache 緩存熱點讀取。
    *   **Solution 3 (GSI)**: 注意 GSI 也會有熱點問題，寫入主表時需同步更新 GSI，若 GSI 節流會導致主表寫入失敗。

## Q3: 在微服務架構中，如何處理跨資料庫的 Transaction？
## (How to handle cross-database Transactions in Microservices?)

*   **高分回答要點 (Key Points)**：
    *   **Avoid Distributed Transactions (2PC)**: 盡量避免 Two-Phase Commit，因為效能差且鎖定資源。
    *   **Saga Pattern**: 使用 Saga 模式（Choreography 或 Orchestration）。
    *   **AWS Implementation**: 使用 **AWS Step Functions** 作為 Orchestrator，協調各個服務的 DynamoDB/Aurora 操作。若某步驟失敗，執行補償交易（Compensating Transaction）來回滾狀態。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)

1.  **Aurora** 將運算與儲存分離，提供比傳統 RDS 更高的可用性與更快的 Failover。
2.  **DynamoDB** 是基於 Hash 的 NoSQL，效能可預測，但 Schema 設計必須由 **Access Pattern** 驅動。
3.  **Polyglot Persistence** 是常態：用 Aurora 處理關聯數據，DynamoDB 處理高併發 KV，TimeStream 處理 Log/Metrics。
4.  **Write Sharding** 是解決 DynamoDB 熱點寫入的關鍵技巧。
5.  **CQRS** 模式能有效解決「寫入優化」與「複雜查詢」之間的衝突。

## 後續延伸 (Next Steps)

*   **Next Chapter**: 既然掌握了資料庫，下一步是**快取策略（Caching Strategies）**。如何利用 ElastiCache (Redis/Memcached) 或 DynamoDB DAX 來保護你的資料庫層？
    **Next Chapter**: Now that you've mastered databases, the next step is **Caching Strategies**. How to use ElastiCache (Redis/Memcached) or DynamoDB DAX to protect your database layer?
*   **Action Item**: 試著在 AWS Console 中建立一個 DynamoDB 表，並開啟 "CloudWatch Contributor Insights"，觀察並模擬 Hot Key 的產生與監控。
    **Action Item**: Try creating a DynamoDB table in the AWS Console, enable "CloudWatch Contributor Insights," and observe/simulate the generation and monitoring of Hot Keys.