# 系統設計中的 MongoDB 決策
# MongoDB in System Design Interviews

## 1. 前言與學習目標
## 1. Introduction & Learning Goals

在資深工程師的系統設計面試（System Design Interview）中，選擇資料庫從來不是因為「我熟悉它」，而是因為「它最適合解決當前的瓶頸」。本章不討論基礎語法，而是聚焦於**決策過程（Decision Making）**。我們將探討何時該引入 MongoDB，以及如何在大規模分散式系統中正確定位它。

In System Design Interviews for senior roles, choosing a database is never about "familiarity," but about "suitability for the current bottleneck." This chapter moves beyond basic syntax to focus on **Decision Making**. We will explore when to introduce MongoDB and how to correctly position it within a large-scale distributed system.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準評估 SQL vs NoSQL 的取捨（Evaluate Trade-offs）**：在面試中能夠根據資料模型（Data Model）與存取模式（Access Pattern）有理有據地選擇 MongoDB。
    **Evaluate SQL vs. NoSQL Trade-offs:** Justify the choice of MongoDB based on Data Models and Access Patterns in an interview setting.
2.  **設計 Polyglot Persistence 架構（Architect Polyglot Persistence）**：理解 MongoDB 如何與 RDBMS、Redis 或 Elasticsearch 協同工作。
    **Architect Polyglot Persistence:** Understand how MongoDB collaborates with RDBMS, Redis, or Elasticsearch.
3.  **解決特定高併發場景（Handle High-Concurrency Scenarios）**：針對 IoT 數據流或社群 Feed 流，提出基於 MongoDB 的具體 Schema 設計模式（如 Bucketing 或 Fan-out）。
    **Handle High-Concurrency Scenarios:** Propose specific MongoDB schema design patterns (like Bucketing or Fan-out) for IoT data streams or social feeds.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 資料局部性與存取模式
### 2.1 Data Locality & Access Patterns

**直覺類比**：
關聯式資料庫（RDBMS）像是一本**會計帳簿**，每一筆交易都嚴格正規化（Normalized），要看完整資訊需要翻閱多個表格並拼湊起來。MongoDB 則像是一個**檔案夾（Folder）**，所有相關的文件、發票、備註都夾在一起（Denormalized），拿出來就是完整的資訊。

**Intuitive Analogy:**
An RDBMS is like an **accounting ledger**, where every transaction is strictly normalized; retrieving complete information requires looking up multiple tables and piecing them together. MongoDB is like a **folder**, where all related documents, invoices, and notes are clipped together (Denormalized); retrieving the folder gives you the complete context immediately.

**核心定義**：
在系統設計中，選擇 MongoDB 的核心驅動力通常是**資料局部性（Data Locality）**。當應用程式傾向於一次性讀取整個聚合物件（Aggregate Root），而非頻繁進行複雜的跨表 Join 時，MongoDB 的 Document Model 能顯著降低 I/O 延遲。

**Core Definition:**
In system design, the primary driver for choosing MongoDB is often **Data Locality**. When an application tends to read an entire Aggregate Root at once, rather than frequently performing complex cross-table Joins, MongoDB's Document Model can significantly reduce I/O latency.

### 2.2 ACID vs. BASE 的現代觀點
### 2.2 Modern View on ACID vs. BASE

雖然 MongoDB 自 4.0 起支援多文件 ACID 交易（Multi-document ACID Transactions），但在系統設計面試中，你不應將其視為 RDBMS 的直接替代品。

While MongoDB has supported Multi-document ACID Transactions since version 4.0, you should not treat it as a direct drop-in replacement for an RDBMS in system design interviews.

*   **RDBMS 思維**：預設強一致性，寫入成本較高（鎖定、約束檢查）。
    **RDBMS Mindset:** Strong consistency by default, higher write cost (locking, constraint checking).
*   **MongoDB 思維**：雖然支援 ACID，但設計上傾向於**最終一致性（Eventual Consistency）**與**高可用性（High Availability）**。我們利用 Replica Sets 實現自動故障轉移，並接受在某些讀取偏好（Read Preference）下可能讀到些微過時的資料，以換取讀取吞吐量。
    **MongoDB Mindset:** While ACID is supported, the design leans towards **Eventual Consistency** and **High Availability**. We leverage Replica Sets for automatic failover and accept that, under certain Read Preferences, we might read slightly stale data in exchange for read throughput.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在大型系統架構圖中，MongoDB 通常扮演以下角色：

In large-scale system architecture diagrams, MongoDB typically plays the following roles:

### 3.1 Polyglot Persistence（多語言持久化）
### 3.1 Polyglot Persistence

在微服務架構中，我們很少只用一種資料庫。MongoDB 常與其他元件搭配：

In microservices architectures, we rarely use just one database. MongoDB often pairs with other components:

*   **Transactional Core (RDBMS)**: 處理金流、訂單狀態機（Order State Machine）。
    **Transactional Core (RDBMS):** Handles payments, Order State Machines.
*   **Operational Data Store (MongoDB)**: 儲存產品目錄（Product Catalog）、使用者設定檔（User Profiles）、內容管理系統（CMS）資料。這些資料結構多變，且讀取頻率遠高於寫入。
    **Operational Data Store (MongoDB):** Stores Product Catalogs, User Profiles, and CMS data. These data structures vary and are read much more frequently than they are written.
*   **Search Engine (Elasticsearch)**: MongoDB 雖然有 Atlas Search，但在地端或舊架構中，常將 MongoDB 的資料同步到 ES 進行全文檢索。
    **Search Engine (Elasticsearch):** While MongoDB has Atlas Search, in on-prem or legacy architectures, data is often synced from MongoDB to ES for full-text search.

### 3.2 CQRS 架構中的 Read Database
### 3.2 Read Database in CQRS Architecture

在 CQRS（Command Query Responsibility Segregation）模式中：
*   **Write Side**: 可能使用 RDBMS 確保嚴格的正規化與約束。
*   **Read Side**: 透過事件驅動（如 Kafka/CDC）將資料同步到 MongoDB。
*   **優勢**: MongoDB 儲存的是**預先聚合（Pre-aggregated）**的 View，前端查詢時無需 Join，直接回傳 JSON，極大提升查詢效能。

In the CQRS (Command Query Responsibility Segregation) pattern:
*   **Write Side:** May use an RDBMS to ensure strict normalization and constraints.
*   **Read Side:** Data is synced to MongoDB via event-driven mechanisms (e.g., Kafka/CDC).
*   **Advantage:** MongoDB stores **Pre-aggregated** Views. Frontend queries require no Joins and return JSON directly, drastically improving query performance.

---

## 4. 逐步示例：IoT 時間序列數據與社群 Feed
## 4. Walkthrough: IoT Time-Series Data & Social Feed

### 案例一：IoT 傳感器數據（Bucketing Pattern）
### Scenario 1: IoT Sensor Data (Bucketing Pattern)

**背景**：
你需要設計一個系統，接收數百萬個 IoT 裝置每分鐘回傳的溫度與狀態數據。
**Background:**
You need to design a system to ingest temperature and status data sent every minute from millions of IoT devices.

**Naive Approach (Anti-pattern)**:
為每一筆讀數建立一個 Document。
Create a Document for every single reading.

```json
// Bad Design
{
  "_id": "unique_id_1",
  "sensor_id": "sensor_A",
  "timestamp": "2023-10-01T10:00:00Z",
  "temp": 23.5
}
```
*   **缺點**：索引過大（Index Size Explodes），儲存空間浪費（重複儲存 `sensor_id` 等欄位）。
*   **Drawback:** Index size explodes, storage waste (repeating `sensor_id` fields).

**Mature Solution (Bucketing)**:
按「小時」或「天」將數據聚合到單一 Document。
Aggregate data into a single Document by "hour" or "day".

```json
// Good Design (Bucketing)
{
  "_id": "sensor_A_20231001_10", // sensor + date + hour
  "sensor_id": "sensor_A",
  "date": "2023-10-01",
  "hour": 10,
  "readings": [
    { "min": 0, "temp": 23.5 },
    { "min": 1, "temp": 23.6 },
    ...
  ],
  "sum_temp": 1400, // Pre-computed for averages
  "count": 60
}
```

*   **Why it works**:
    1.  **索引效率**：索引數量減少 60 倍（假設每分鐘一筆，一小時一桶）。
        **Index Efficiency:** Reduces index entries by 60x (assuming 1 reading/min, bucketed by hour).
    2.  **查詢優化**：讀取「過去一小時的數據」只需讀取 1 個 Document，利用順序 I/O。
        **Query Optimization:** Fetching "last hour's data" requires reading only 1 Document, utilizing sequential I/O.
    3.  **預計算**：寫入時順便更新 `sum_temp` 與 `count`，讓讀取平均值變為 O(1)。
        **Pre-computation:** Updating `sum_temp` and `count` on write makes reading averages O(1).

### 案例二：社群動態牆（Fan-out on Write）
### Scenario 2: Social Media Feed (Fan-out on Write)

**背景**：
設計類似 Instagram 的 Feed，使用者打開 App 要立刻看到追蹤對象的最新貼文。
**Background:**
Design an Instagram-like Feed where users see the latest posts from people they follow immediately upon opening the App.

**System Design Decision**:
*   **Pull Model (Read-heavy)**: 用戶讀取時才去查詢所有追蹤者的貼文並排序。這在 SQL 中是昂貴的 `JOIN` + `ORDER BY`。
    **Pull Model (Read-heavy):** Query and sort all followees' posts when the user reads. This is an expensive `JOIN` + `ORDER BY` in SQL.
*   **Push Model (Write-heavy with MongoDB)**: 當大 V（Influencer）發文時，將貼文 ID 寫入所有粉絲的 `Timeline` Document 中。
    **Push Model (Write-heavy with MongoDB):** When an Influencer posts, push the Post ID to the `Timeline` Document of all followers.

```json
// User's Timeline Document
{
  "user_id": "user_123",
  "timeline_posts": [
    { "post_id": "p_999", "author": "star_A", "ts": 1696150000 },
    { "post_id": "p_888", "author": "friend_B", "ts": 1696149000 }
    // Capped array, keep latest 200
  ]
}
```

*   **為何選 MongoDB**：MongoDB 支援對 Array 的原子操作（`$push`, `$slice`），非常適合維護這種固定長度的 Feed 列表。讀取 Feed 變成了單一 Key-Value 查詢（O(1)）。
*   **Why MongoDB:** MongoDB supports atomic operations on Arrays (`$push`, `$slice`), making it ideal for maintaining such fixed-length feed lists. Reading the feed becomes a single Key-Value query (O(1)).

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 無限制的陣列增長（Unbounded Arrays）
### 5.1 Unbounded Arrays

*   **錯誤描述**：在 Document 中嵌入一個會無限增長的 Array，例如 `comments: []`。
    **Description:** Embedding an infinitely growing Array in a Document, e.g., `comments: []`.
*   **後果**：
    1.  **16MB 限制**：MongoDB 單一 Document 最大限制為 16MB。
        **16MB Limit:** MongoDB has a hard limit of 16MB per Document.
    2.  **移動開銷**：Document 變大導致需要重新分配磁碟空間（Document Moves），影響效能。
        **Movement Overhead:** Growing documents may require reallocation on disk (Document Moves), impacting performance.
*   **修正**：使用 **Subset Pattern**（只存最新的 10 則留言），其餘留言移至獨立的 Collection 並透過 `post_id` 關聯。
    **Fix:** Use the **Subset Pattern** (store only the latest 10 comments), and move the rest to a separate Collection linked by `post_id`.

### 5.2 過度使用 `$lookup`（Excessive `$lookup`）
### 5.2 Excessive `$lookup`

*   **錯誤描述**：試圖在 MongoDB 中完全複製 SQL 的正規化模式，並在應用層或聚合管道（Aggregation Pipeline）中大量使用 `$lookup`。
    **Description:** Trying to replicate SQL normalization patterns in MongoDB and heavily using `$lookup` in the application layer or Aggregation Pipeline.
*   **後果**：分散式系統中的 Join 效能極差，且難以 Sharding。
    **Consequence:** Joins in distributed systems perform poorly and are difficult to shard.
*   **修正**：**反正規化（Denormalization）**。適度冗餘資料（例如在訂單中直接儲存當下的產品名稱與價格，而非只存 `product_id`）。
    **Fix:** **Denormalization**. Duplicate data appropriately (e.g., store the product name and price snapshot directly in the Order, not just `product_id`).

### 5.3 忽略 Shard Key 的選擇
### 5.3 Ignoring Shard Key Selection

*   **錯誤描述**：選擇單調遞增的欄位（如 Timestamp 或 ObjectId）作為 Shard Key。
    **Description:** Choosing a monotonically increasing field (like Timestamp or ObjectId) as the Shard Key.
*   **後果**：所有新的寫入都集中在最後一個 Shard（Hot Shard），導致寫入無法水平擴展。
    **Consequence:** All new writes target the last Shard (Hot Shard), preventing horizontal write scaling.
*   **修正**：使用雜湊分片（Hashed Sharding）或複合分片鍵（Compound Shard Key）來確保寫入均勻分佈。
    **Fix:** Use Hashed Sharding or a Compound Shard Key to ensure writes are evenly distributed.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

在面試中，你可以利用以下問題展示資深深度：
In an interview, use the following questions to demonstrate senior-level depth:

### Q1: "我們應該在什麼時候選擇 MongoDB 而非 PostgreSQL？"
### Q1: "When should we choose MongoDB over PostgreSQL?"

*   **高分回答要點**：
    *   **Schema 靈活性**：當業務需求變動極快，且欄位結構不固定（如多樣化的產品屬性）時。
    *   **寫入吞吐量**：當需要極高的寫入速度，且可以容忍最終一致性時（利用 MongoDB 的 Sharding 架構）。
    *   **開發速度**：當資料本身就是 JSON 結構，且應用程式邏輯與資料庫模型高度對應時（Impedance Mismatch 低）。
    *   **反面論述**：若系統涉及複雜的財務交易、嚴格的關聯約束，PostgreSQL 是更好選擇。
*   **Key Points for a High Score:**
    *   **Schema Flexibility:** When business requirements change rapidly and field structures are fluid (e.g., diverse product attributes).
    *   **Write Throughput:** When extremely high write speed is needed, and eventual consistency is tolerable (leveraging MongoDB's Sharding architecture).
    *   **Development Velocity:** When data is natively JSON and there is low Impedance Mismatch between app logic and the DB model.
    *   **Counter-argument:** If the system involves complex financial transactions or strict relational constraints, PostgreSQL is the better choice.

### Q2: "如何設計一個全球部署的 MongoDB 架構以符合 GDPR？"
### Q2: "How do you design a globally deployed MongoDB architecture to comply with GDPR?"

*   **高分回答要點**：
    *   提及 **Zone Sharding (Tag-aware Sharding)**。
    *   說明如何將特定區域（如 EU）的資料限制在位於歐洲資料中心的 Shard 上。
    *   這展示了你對 MongoDB 進階運維與法規合規性的理解。
*   **Key Points for a High Score:**
    *   Mention **Zone Sharding (Tag-aware Sharding)**.
    *   Explain how to pin data from specific regions (e.g., EU) to Shards located in European data centers.
    *   This demonstrates understanding of advanced MongoDB operations and regulatory compliance.

### Q3: "MongoDB 的 Write Concern `w:1` 與 `w:majority` 在系統設計上有何權衡？"
### Q3: "What are the trade-offs between Write Concern `w:1` and `w:majority` in system design?"

*   **高分回答要點**：
    *   `w:1`：低延遲，但若 Primary 節點在複製前崩潰，可能遺失資料。適用於日誌、非關鍵數據。
    *   `w:majority`：較高延遲（需等待多數節點確認），但保證資料持久性與一致性。適用於使用者資料、訂單。
    *   資深觀點：應根據 API 的 SLA 需求動態調整 Write Concern。
*   **Key Points for a High Score:**
    *   `w:1`: Low latency, but potential data loss if Primary crashes before replication. Suitable for logs, non-critical data.
    *   `w:majority`: Higher latency (waits for majority ack), but guarantees durability and consistency. Suitable for user data, orders.
    *   Senior View: Write Concern should be adjusted dynamically based on the API's SLA requirements.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 本章記憶錨點 (Key Takeaways)
1.  **資料局部性（Locality）**：MongoDB 的優勢在於將相關資料存在一起，減少 I/O。
2.  **Schema Design**：NoSQL 不代表 No Design。Bucketing 和 Subset Pattern 是必備技能。
3.  **Polyglot Persistence**：MongoDB 常作為 Operational Data Store 或 Read View，而非唯一的資料庫。
4.  **Sharding 策略**：錯誤的 Shard Key 會毀掉效能；避免單調遞增鍵造成的 Hotspots。
5.  **Denormalization**：為了讀取效能，適度的資料冗餘是可接受且必要的。

### 建議後續閱讀 (Next Steps)
*   **Next Chapter**: 深入探討 **MongoDB Indexing & Performance Tuning**（索引優化與執行計畫分析），這是 Production 環境中最常遇到的實戰問題。
*   **Practice**: 嘗試設計一個 URL Shortener 或 Pastebin 系統，並比較使用 MongoDB 與 Redis/Cassandra 的差異。