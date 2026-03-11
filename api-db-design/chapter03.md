# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Schema 設計不再僅是遵守第三正規化（3NF）或畫出 ER Diagram。在分散式系統與高併發場景下，我們必須在「寫入複雜度」與「讀取延遲」之間做出艱難的取捨。本章將帶領你跨越傳統 RDBMS 的舒適圈，深入 NoSQL 的建模思維。

For senior engineers, schema design is no longer just about adhering to Third Normal Form (3NF) or drawing ER diagrams. In distributed systems and high-concurrency scenarios, we must make difficult trade-offs between "write complexity" and "read latency." This chapter will take you beyond the comfort zone of traditional RDBMS and deep into the modeling mindset of NoSQL.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精準評估正規化與反正規化的時機**：理解何時該打破正規化規則以換取讀取效能，以及隨之而來的資料一致性維護成本。
    **Accurately evaluate when to normalize vs. denormalize**: Understand when to break normalization rules in exchange for read performance, and the associated costs of maintaining data consistency.

2.  **掌握 Access Pattern 驅動的設計方法**：在 NoSQL（特別是 DynamoDB 或 Cassandra）設計中，能夠先定義查詢模式（Access Patterns），再反推資料結構，而非傳統的「先設計資料，再寫 SQL」。
    **Master Access Pattern-driven design**: In NoSQL design (especially DynamoDB or Cassandra), be able to define Access Patterns first and then reverse-engineer the data structure, rather than the traditional "design data first, then write SQL" approach.

3.  **解決 NoSQL 的常見建模挑戰**：處理一對多（1:N）、多對多（M:N）關係，以及解決熱點分區（Hot Partitions）問題。
    **Solve common NoSQL modeling challenges**: Handle one-to-many (1:N) and many-to-many (M:N) relationships, and address hot partition issues.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 資料優先 vs. 查詢優先 (Data-First vs. Query-First)

在關聯式資料庫（RDBMS）中，我們習慣「資料優先」。我們模擬真實世界的實體（Entities）與關係（Relationships），力求減少資料冗餘。查詢（Query）是後來才寫的，資料庫引擎負責優化這些查詢。

In Relational Database Management Systems (RDBMS), we are accustomed to a "Data-First" approach. We model real-world entities and relationships, striving to minimize data redundancy. Queries are written later, and the database engine is responsible for optimizing them.

在 NoSQL（特別是 Key-Value 與 Wide-Column Store）中，我們必須採用「查詢優先」。你必須在設計 Schema 之前，列出所有的讀取路徑。**Schema 是為了滿足特定查詢而「預先組裝」的結果。**

In NoSQL (especially Key-Value and Wide-Column Stores), we must adopt a "Query-First" approach. You must list all read paths before designing the schema. **The schema is the result of "pre-assembling" data to satisfy specific queries.**

> **Analogy (類比)**:
> *   **RDBMS** 像是一間圖書館。書本（資料）按照類別（Table）嚴格分類存放。如果你需要做一份關於「歷史上的經濟危機」的報告，你需要跑好幾個書架（Joins），把不同書裡的資訊拼湊起來。
> *   **NoSQL** 像是一個外帶餐盒店。餐盒（Schema）是根據顧客最常點的套餐（Access Pattern）預先裝好的。如果你點了「雞腿飯」，裡面已經有飯、菜、肉。你不需要分別去飯桶、菜籃和肉櫃取貨。讀取極快，但如果你想把雞腿換成排骨，廚房（寫入端）會比較麻煩。
>
> *   **RDBMS** is like a library. Books (data) are strictly categorized (Tables). If you need to write a report on "Historical Economic Crises," you have to visit multiple shelves (Joins) to piece together information from different books.
> *   **NoSQL** is like a bento box shop. The boxes (Schema) are pre-packed based on the most popular combos (Access Patterns). If you order "Chicken Rice," it already contains rice, veggies, and meat. You don't need to fetch them separately. Reading is extremely fast, but if you want to swap chicken for pork, the kitchen (write side) has more work to do.

## 2.2 讀取放大 vs. 寫入放大 (Read Amplification vs. Write Amplification)

資深工程師在設計 Schema 時，實際上是在這兩者間做權衡：

Senior engineers are essentially trading off between these two when designing schemas:

*   **讀取放大 (Read Amplification)**: 為了獲取邏輯上的一筆資料，需要進行多次物理 I/O 或多次查詢（例如：N+1 Query 問題，或是需要 Join 多張大表）。正規化通常會導致讀取放大。
    **Read Amplification**: To retrieve one logical piece of data, multiple physical I/Os or queries are required (e.g., N+1 Query problem, or Joining multiple large tables). Normalization usually leads to read amplification.

*   **寫入放大 (Write Amplification)**: 為了更新邏輯上的一筆資料，需要更新多個物理儲存位置（例如：反正規化後，更新使用者頭像需要同時更新 User 表、Comment 表、Post 表）。
    **Write Amplification**: To update one logical piece of data, multiple physical storage locations need to be updated (e.g., after denormalization, updating a user avatar requires updating the User table, Comment table, and Post table simultaneously).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 混合持久化 (Polyglot Persistence)

在現代大型系統中，單一資料庫很少能滿足所有需求。我們通常會混合使用：

In modern large-scale systems, a single database rarely suffices. We usually use a mix:

*   **Transactional Data (OLTP)**: 使用 RDBMS (PostgreSQL/MySQL) 處理訂單、支付、帳戶管理。這裡的一致性（ACID）至關重要。
    **Transactional Data (OLTP)**: Use RDBMS (PostgreSQL/MySQL) for orders, payments, and account management. Consistency (ACID) is paramount here.
*   **High-Velocity Data**: 使用 NoSQL (DynamoDB/Cassandra/MongoDB) 處理 Activity Logs、Sensor Data、Social Feeds。這裡需要極高的寫入吞吐量和低延遲讀取。
    **High-Velocity Data**: Use NoSQL (DynamoDB/Cassandra/MongoDB) for Activity Logs, Sensor Data, and Social Feeds. High write throughput and low-latency reads are required here.

## 3.2 CQRS (Command Query Responsibility Segregation)

當讀寫需求極度不平衡時，我們會在架構層級將 Schema 分離：

When read and write requirements are extremely unbalanced, we separate schemas at the architectural level:

*   **Write Model**: 高度正規化的 RDBMS，優化寫入與一致性。
    **Write Model**: Highly normalized RDBMS, optimized for writes and consistency.
*   **Read Model**: 高度反正規化的 NoSQL 或 Search Engine (Elasticsearch)，優化讀取。
    **Read Model**: Highly denormalized NoSQL or Search Engine (Elasticsearch), optimized for reads.
*   **Sync Mechanism**: 透過 CDC (Change Data Capture) 或 Message Queue 非同步同步資料。
    **Sync Mechanism**: Asynchronously sync data via CDC (Change Data Capture) or Message Queue.

---

# 4. 逐步示例 (Walkthrough / Example)

**場景**：設計一個電子商務系統的「訂單歷史查詢」功能。
**Scenario**: Design an "Order History" feature for an e-commerce system.

**Access Pattern**: `getOrdersByUserId(userId)` - 使用者要看到自己過去所有的訂單列表，包含商品名稱與當時價格。
**Access Pattern**: `getOrdersByUserId(userId)` - Users want to see a list of all their past orders, including product names and prices at that time.

### Phase 1: Naive RDBMS (Normalized / 3NF)

最直覺的設計是將資料拆解為 `Users`, `Orders`, `OrderItems`, `Products`。

The most intuitive design is to break data down into `Users`, `Orders`, `OrderItems`, and `Products`.

```sql
-- Schema
TABLE Users (id, name, ...)
TABLE Products (id, name, current_price, ...)
TABLE Orders (id, user_id, created_at, ...)
TABLE OrderItems (order_id, product_id, quantity)

-- Query
SELECT o.id, p.name, p.current_price, oi.quantity
FROM Orders o
JOIN OrderItems oi ON o.id = oi.order_id
JOIN Products p ON oi.product_id = p.id
WHERE o.user_id = ?
```

*   **問題 (Problem)**:
    1.  **歷史價格錯誤**: `Products.current_price` 會隨時間改變，但訂單應該記錄「下單時」的價格。
        **Historical Price Error**: `Products.current_price` changes over time, but the order should record the price "at the time of purchase."
    2.  **效能瓶頸**: 當 `OrderItems` 達到數億行時，Join 的開銷巨大。
        **Performance Bottleneck**: When `OrderItems` reaches hundreds of millions of rows, the overhead of Joins is massive.

### Phase 2: Pragmatic RDBMS (Denormalized)

為了修正價格問題並減少一次 Join，我們在 `OrderItems` 中進行反正規化。

To fix the price issue and reduce one Join, we denormalize within `OrderItems`.

```sql
TABLE OrderItems (
    order_id,
    product_id,
    quantity,
    unit_price_at_purchase, -- Denormalized: Snapshot of price
    product_name_snapshot   -- Denormalized: Snapshot of name (optional)
)
```

*   **分析 (Analysis)**: 這是 RDBMS 中最常見的模式。雖然冗餘了價格資訊，但這是業務邏輯所必需的（Snapshotting）。
    **Analysis**: This is the most common pattern in RDBMS. Although price info is redundant, it is required by business logic (Snapshotting).

### Phase 3: NoSQL Optimization (DynamoDB / Wide-Column)

假設規模達到 Amazon 等級，我們需要毫秒級延遲。我們採用 **Single Table Design** 或 **Wide-Column** 策略。

Assuming Amazon-scale, we need millisecond latency. We adopt **Single Table Design** or a **Wide-Column** strategy.

**目標**: 一次查詢取出該 User 的所有訂單及詳情，無需 Join。
**Goal**: Retrieve all orders and details for a User in a single query, without Joins.

**Schema Design (DynamoDB style):**

*   **Partition Key (PK)**: `USER#{userId}`
*   **Sort Key (SK)**: `ORDER#{timestamp}`

**Data Structure (Item):**

```json
{
  "PK": "USER#123",
  "SK": "ORDER#2023-10-27T10:00:00",
  "OrderId": "ord_999",
  "TotalAmount": 150.00,
  "OrderStatus": "SHIPPED",
  "Items": [  // Embedding / Denormalization
    { "ProductId": "p_1", "Name": "Mechanical Keyboard", "Price": 100.00, "Qty": 1 },
    { "ProductId": "p_2", "Name": "Mouse", "Price": 50.00, "Qty": 1 }
  ]
}
```

*   **優勢 (Pros)**: `Query(PK="USER#123")` 可以一次循序讀取該用戶所有訂單。時間複雜度僅與結果集大小有關，與總數據量無關。
    **Pros**: `Query(PK="USER#123")` can sequentially read all orders for that user in one go. Time complexity depends only on the result set size, not the total data volume.
*   **劣勢 (Cons)**: 如果需要查詢「所有買過 Mechanical Keyboard 的用戶」，這個 Schema 就完全失效了（需要全表掃描或 GSI）。
    **Cons**: If you need to query "all users who bought a Mechanical Keyboard," this schema fails completely (requires full table scan or GSI).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 NoSQL 中模擬關聯模型 (Relational Modeling in NoSQL)

*   **錯誤描述**: 在 Document DB 中建立 `Users` collection 和 `Orders` collection，然後在應用程式端（Client-side）先查 User，拿到 ID 後再去查 Orders。
    **Description**: Creating `Users` and `Orders` collections in a Document DB, then querying User first in the application (Client-side), getting the ID, and then querying Orders.
*   **為何不好**: 這導致了嚴重的「網路延遲放大」。原本 SQL 一次 Join 能做完的事，現在需要多次網路來回（Network Round Trips）。
    **Why it's bad**: This causes severe "Network Latency Amplification." What SQL could do in one Join now requires multiple Network Round Trips.
*   **修正**: 使用 Embedding（嵌入）或預先聚合（Pre-aggregation）。
    **Fix**: Use Embedding or Pre-aggregation.

## 5.2 無限增長的 Document (Unbounded Document Growth)

*   **錯誤描述**: 在 MongoDB 中將所有 `Comments` 嵌入到單一 `Post` document 中。
    **Description**: Embedding all `Comments` into a single `Post` document in MongoDB.
*   **為何不好**: 當某篇貼文爆紅，評論數萬條時，會觸發 Document Size Limit（如 MongoDB 的 16MB），導致寫入失敗或讀取效能驟降。
    **Why it's bad**: When a post goes viral with tens of thousands of comments, it hits the Document Size Limit (e.g., 16MB in MongoDB), causing write failures or performance degradation.
*   **修正**: 混合模式。前 10 條評論嵌入，其餘評論移至獨立 Collection 並透過 ID 關聯（Bucketing Pattern）。
    **Fix**: Hybrid approach. Embed the first 10 comments, and move the rest to a separate Collection linked by ID (Bucketing Pattern).

## 5.3 忽略熱點分區 (Ignoring Hot Partitions)

*   **錯誤描述**: 在 DynamoDB 中使用 `Date` (e.g., `2023-10-27`) 作為 Partition Key 來儲存 Log。
    **Description**: Using `Date` (e.g., `2023-10-27`) as the Partition Key in DynamoDB to store logs.
*   **為何不好**: 所有的寫入流量都會集中在「當天」的這個 Partition，導致該分區被 Throttled，而其他分區閒置。這無法利用分散式資料庫的水平擴展能力。
    **Why it's bad**: All write traffic concentrates on the "current day" partition, causing throttling on that partition while others sit idle. This fails to leverage the horizontal scaling of distributed databases.
*   **修正**: 使用 Write Sharding（例如 `Date + RandomSuffix`）或選擇更分散的 Key（如 `UserID`）。
    **Fix**: Use Write Sharding (e.g., `Date + RandomSuffix`) or choose a higher cardinality Key (like `UserID`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題旨在測試候選人對於「取捨」的理解，而非單純的技術名詞解釋。
These questions are designed to test the candidate's understanding of "trade-offs," not just definitions.

## Q1: "我們需要設計一個類似 Instagram 的 Feed 系統。你會如何設計 Schema？"
**"We need to design an Instagram-like Feed system. How would you design the schema?"**

*   **高分回答要點 (Key Points)**:
    *   **Push vs. Pull Model**: 討論「寫入時扇出 (Fan-out on Write)」與「讀取時扇出 (Fan-out on Read)」的差異。
    *   **Schema 選擇**: 對於名人（百萬粉絲），使用 Pull Model（讀取時聚合）；對於普通用戶，使用 Push Model（寫入時預先寫入 Feed Table）。
    *   **NoSQL Modeling**: 說明如何使用 `(UserId, Timestamp)` 作為複合鍵來優化 Feed 的分頁讀取。

## Q2: "什麼時候你會選擇 Postgres 的 JSONB 欄位，而不是直接使用 MongoDB？"
**"When would you choose Postgres JSONB columns over using MongoDB directly?"**

*   **高分回答要點 (Key Points)**:
    *   **交易需求 (Transactional Needs)**: 當系統大部分資料是關聯式的，且需要強 ACID 保證，但只有少部分屬性是動態的（例如產品規格表）。
    *   **維運複雜度 (Operational Complexity)**: 避免為了單一功能引入新的資料庫技術堆疊（Tech Stack）。
    *   **查詢能力**: Postgres 的 JSONB 索引功能已經非常強大，足以應付中等規模的 Document 查詢需求。

## Q3: "在高度反正規化的 NoSQL 設計中，如何處理資料更新的一致性？"
**"In a highly denormalized NoSQL design, how do you handle data consistency during updates?"**

*   **高分回答要點 (Key Points)**:
    *   **接受最終一致性 (Eventual Consistency)**: 說明這是一個 Feature 而不是 Bug。
    *   **技術手段**: 使用 Database Triggers (如 DynamoDB Streams) 觸發 Lambda 函數，背景非同步更新所有冗餘資料。
    *   **修復策略**: 實作「讀取修復 (Read Repair)」或定期的背景掃描與修復 Job。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Access Pattern is King**: 在 NoSQL 中，不知道查詢模式就無法設計 Schema。
2.  **Normalization is a Spectrum**: 正規化不是非黑即白。在 RDBMS 中適度反正規化（Snapshotting, JSON columns）是實務常態。
3.  **Read vs. Write Trade-off**: 優化讀取通常意味著增加寫入複雜度（反正規化）；優化寫入通常意味著增加讀取複雜度（正規化/Joins）。
4.  **Avoid Distributed Joins**: 在大規模系統中，應盡量避免跨庫或跨分區的 Join，改用資料冗餘或應用層聚合。
5.  **Hot Partitions Kill Scale**: 選擇 Partition Key 時，必須確保資料與流量的均勻分佈。

## 後續延伸 (Next Steps)

*   **實作練習**: 嘗試使用 DynamoDB Workbench 模擬一個「Uber 行程記錄」的 Schema 設計。
*   **延伸閱讀**: 閱讀下一章關於 **Database Sharding & Partitioning Strategies**，深入了解當單表數據量突破 TB 級別時的處理策略。
*   **進階主題**: 研究 **CAP Theorem** 與 **PACELC Theorem**，從理論層面理解為什麼我們需要做這些取捨。