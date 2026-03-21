# Chapter 09: Stream Processing and Ecosystem Integration
# 第 9 章：串流處理與生態系整合

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Software Engineer, you are likely familiar with using Kafka as a message bus (Pub/Sub). However, the true power of Kafka emerges when it transitions from a mere transport layer to a **Stream Processing Platform**. This chapter focuses on the "Processing" and "Integration" layers: **Kafka Connect** for code-free integration and **Kafka Streams** for building stateful, distributed applications.

身為資深軟體工程師，您可能已經熟悉將 Kafka 作為訊息匯流排（Pub/Sub）使用。然而，當 Kafka 從單純的傳輸層轉變為**串流處理平台（Stream Processing Platform）**時，其真正的威力才會顯現。本章聚焦於「處理」與「整合」層：用於無程式碼整合的 **Kafka Connect**，以及用於建構有狀態、分散式應用程式的 **Kafka Streams**。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Architect Integration Pipelines**: Distinguish when to use Kafka Connect versus writing custom producers/consumers, and understand the internal architecture of Connect Workers.
    **架構整合管線**：區分何時該使用 Kafka Connect 而非自行撰寫 producer/consumer，並理解 Connect Workers 的內部架構。
2.  **Master the Duality of Streams**: deeply understand the relationship between **KStream** (events) and **KTable** (state), and how to leverage this for event-driven microservices.
    **掌握串流的二元性**：深入理解 **KStream**（事件）與 **KTable**（狀態）之間的關係，以及如何利用此特性建構事件驅動微服務。
3.  **Handle State & Time**: Explain how Kafka Streams manages local state (RocksDB) and fault tolerance (Changelogs), and design robust windowing strategies for time-series data.
    **處理狀態與時間**：解釋 Kafka Streams 如何管理本地狀態（RocksDB）與容錯（Changelogs），並為時間序列資料設計穩健的視窗（Windowing）策略。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Kafka Connect: The Universal Plumbing
### 2.1 Kafka Connect：通用的管線系統

Think of **Kafka Connect** as the standard "adapter pattern" for the Kafka ecosystem. Instead of writing custom code to poll a database or push to S3, you use configuration-based Connectors.
將 **Kafka Connect** 視為 Kafka 生態系中的標準「轉接器模式（Adapter Pattern）」。您不需要撰寫客製化程式碼來輪詢資料庫或推送到 S3，而是使用基於設定檔的 Connectors。

*   **Source Connectors**: Pull data from external systems (e.g., CDC from PostgreSQL) into Kafka topics.
    **Source Connectors**：從外部系統（例如 PostgreSQL 的 CDC）將資料拉取進 Kafka topics。
*   **Sink Connectors**: Push data from Kafka topics into external systems (e.g., Elasticsearch, Snowflake).
    **Sink Connectors**：將資料從 Kafka topics 推送到外部系統（例如 Elasticsearch, Snowflake）。
*   **Mental Model**: Connect is a distributed runtime service (Cluster of Workers) that manages the lifecycle, parallelism, and fault tolerance of these tasks for you.
    **心智模型**：Connect 是一個分散式的執行環境服務（Worker 叢集），它為您管理這些任務的生命週期、平行處理與容錯機制。

### 2.2 Kafka Streams: The Embedded Processing Engine
### 2.2 Kafka Streams：嵌入式處理引擎

Unlike Apache Flink or Spark Streaming which require a separate processing cluster, **Kafka Streams** is a Java/Scala **library**. It runs inside your application instances (e.g., a Spring Boot microservice).
不同於 Apache Flink 或 Spark Streaming 需要獨立的處理叢集，**Kafka Streams** 是一個 Java/Scala **函式庫**。它運行在您的應用程式實例內部（例如 Spring Boot 微服務）。

*   **Stateless Operations**: `filter`, `map` (one record in, one record out). No memory of previous events needed.
    **無狀態操作**：`filter`, `map`（一進一出）。不需要記住先前的事件。
*   **Stateful Operations**: `count`, `aggregate`, `join`. Requires a **State Store** to remember context.
    **有狀態操作**：`count`, `aggregate`, `join`。需要一個 **State Store** 來記住上下文。

### 2.3 The Stream-Table Duality
### 2.3 串流與資料表的二元性

This is the most critical concept for system design in Kafka.
這是 Kafka 系統設計中最關鍵的概念。

*   **KStream (The Log)**: Represents a flow of **events**. Reading a stream means reading the history of changes. (e.g., "Alice sent $5", "Alice sent $10").
    **KStream（日誌）**：代表**事件**的流動。讀取串流意味著讀取變更的歷史。（例如：「Alice 匯了 $5」、「Alice 匯了 $10」）。
*   **KTable (The Snapshot)**: Represents the **current state**. It is the projection of the stream at a point in time. (e.g., "Alice's Balance: $15").
    **KTable（快照）**：代表**當前狀態**。它是串流在某個時間點的投影。（例如：「Alice 的餘額：$15」）。

> **Analogy**: A **Stream** is the list of moves in a chess game (e2-e4, e7-e5...). A **Table** is the current board configuration. You can reconstruct the Table by replaying the Stream.
> **類比**：**Stream** 是西洋棋局中的移動列表（e2-e4, e7-e5...）。**Table** 是當前的棋盤佈局。您可以透過重播 Stream 來重建 Table。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Architecture: Where do they fit?
### 3.1 架構：它們位於何處？

In a modern Data Mesh or Event-Driven Architecture:
在現代的 Data Mesh 或事件驅動架構中：

1.  **Ingestion Layer (Kafka Connect)**: Decouples producers from Kafka. For example, using Debezium (CDC) to stream legacy Oracle DB changes into Kafka without modifying the legacy app code.
    **攝取層（Kafka Connect）**：將生產者與 Kafka 解耦。例如，使用 Debezium (CDC) 將舊版 Oracle DB 的變更串流進 Kafka，而無需修改舊版應用程式碼。
2.  **Processing Layer (Kafka Streams)**: Performs business logic. Fraud detection, real-time inventory aggregation, or enriching clickstreams with user profile data.
    **處理層（Kafka Streams）**：執行商業邏輯。詐欺偵測、即時庫存聚合，或將使用者資料豐富化到點擊流中。
3.  **Serving Layer (Kafka Connect / Interactive Queries)**: Sinks aggregated data to a Data Warehouse for BI, or uses **Interactive Queries** to expose the internal state of a Kafka Streams app directly via REST API.
    **服務層（Kafka Connect / Interactive Queries）**：將聚合後的資料 Sink 到資料倉儲以供 BI 使用，或使用 **Interactive Queries** 直接透過 REST API 暴露 Kafka Streams 應用程式的內部狀態。

### 3.2 Scalability & Fault Tolerance
### 3.2 可擴充性與容錯

*   **Consumer Group Protocol**: Both Connect and Streams rely on the Kafka Consumer Group protocol. To scale up processing, you simply add more instances (Workers or App instances). Kafka automatically rebalances partitions among them.
    **Consumer Group 協定**：Connect 與 Streams 皆依賴 Kafka Consumer Group 協定。要擴展處理能力，只需增加更多實例（Workers 或 App 實例）。Kafka 會自動在它們之間重新分配 partitions。
*   **State Reliability**: Stateful operations in Kafka Streams are backed by **RocksDB** (local disk) and a **Changelog Topic** (in Kafka). If an instance crashes, the replacement instance rebuilds its state from the Changelog topic.
    **狀態可靠性**：Kafka Streams 中的有狀態操作由 **RocksDB**（本地磁碟）與 **Changelog Topic**（位於 Kafka 中）支援。若某個實例崩潰，接替的實例會從 Changelog topic 重建其狀態。

---

## 4. Walkthrough / Example: Real-time Campaign Analytics
## 4. 逐步示例：即時行銷活動分析

### Scenario
### 情境
We need to calculate the **total clicks per campaign per hour** in real-time.
我们需要即時計算**每個行銷活動每小時的總點擊數**。

*   **Input**: Topic `ad-clicks` (Key: `userId`, Value: JSON `{ "campaignId": "c1", "ts": 162000... }`)
*   **Output**: Topic `campaign-hourly-stats` (Key: `campaignId`, Value: `count`)

### Step 1: Naive Approach (External DB)
### 步驟 1：直覺做法（外部 DB）
A standard consumer reads `ad-clicks`, queries a Redis/SQL DB for the current count, increments it, and writes it back.
一個標準 consumer 讀取 `ad-clicks`，查詢 Redis/SQL DB 取得當前計數，增加後寫回。

*   **Problem**: Network latency for every event. Race conditions require locking. Database becomes the bottleneck.
    **問題**：每個事件都有網路延遲。競爭條件（Race conditions）需要鎖定機制。資料庫成為瓶頸。

### Step 2: Kafka Streams Solution (Windowed Aggregation)
### 步驟 2：Kafka Streams 解法（視窗聚合）

We use Kafka Streams to handle this in-memory (with RocksDB spillover) and ensure exactly-once semantics.
我們使用 Kafka Streams 在記憶體中處理此問題（並透過 RocksDB 處理溢位），確保 Exactly-Once 語意。

```java
KStream<String, AdClick> clicks = builder.stream("ad-clicks", Consumed.with(Serdes.String(), adClickSerde));

// 1. Rekey by CampaignId (Partitioning implies network shuffle)
// 1. 根據 CampaignId 重新設定 Key（分區意味著網路 Shuffle）
KStream<String, AdClick> clicksByCampaign = clicks
    .selectKey((userId, click) -> click.getCampaignId()); 

// 2. Group and Window
// 2. 分組與視窗化
KTable<Windowed<String>, Long> hourlyCounts = clicksByCampaign
    .groupByKey() // Prepare for aggregation
    .windowedBy(TimeWindows.of(Duration.ofHours(1)).advanceBy(Duration.ofMinutes(10))) // Hopping Window
    .count(Materialized.as("hourly-clicks-store")); // State Store Name

// 3. Output to topic
// 3. 輸出到 topic
hourlyCounts
    .toStream()
    .map((windowedKey, count) -> KeyValue.pair(
        windowedKey.key() + "@" + windowedKey.window().start(), 
        count
    ))
    .to("campaign-hourly-stats", Produced.with(Serdes.String(), Serdes.Long()));
```

### Analysis
### 分析

1.  **`selectKey`**: Changes the key from `userId` to `campaignId`. This triggers a **repartition** phase because all clicks for "Campaign A" must end up on the same partition to be counted correctly.
    **`selectKey`**：將 key 從 `userId` 變更為 `campaignId`。這會觸發 **repartition** 階段，因為所有「Campaign A」的點擊必須進入同一個 partition 才能被正確計數。
2.  **`windowedBy`**: We use a **Hopping Window** (1 hour size, 10 min advance). This means we get an update every 10 minutes for the last hour's data.
    **`windowedBy`**：我們使用 **Hopping Window**（大小 1 小時，前進 10 分鐘）。這意味著我們每 10 分鐘會收到過去一小時資料的更新。
3.  **`count`**: This is stateful. Kafka Streams maintains a local RocksDB instance. It only emits updates downstream, not the full history.
    **`count`**：這是有狀態的。Kafka Streams 維護一個本地 RocksDB 實例。它只向下游發送更新，而非完整歷史。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Database Join" Trap
### 5.1 「資料庫 Join」陷阱
*   **Anti-pattern**: Doing a REST call or DB query inside a `map` or `filter` function in Kafka Streams.
    **反模式**：在 Kafka Streams 的 `map` 或 `filter` 函數中執行 REST 呼叫或 DB 查詢。
*   **Why it's bad**: Stream processing is designed for high throughput (thousands of events/sec). A 10ms DB latency kills throughput. It also creates backpressure that can crash the stream.
    **為何不好**：串流處理是為高吞吐量設計的（每秒數千事件）。10ms 的 DB 延遲會扼殺吞吐量。這也會產生可能導致串流崩潰的背壓（Backpressure）。
*   **Solution**: Use CDC to stream the DB table into a topic, then use a **KTable-KStream Join**. Bring the data to the code, not the code to the data.
    **解法**：使用 CDC 將 DB 資料表串流到 topic，然後使用 **KTable-KStream Join**。將資料帶到程式碼端，而非程式碼去存取資料。

### 5.2 Ignoring Changelog Topic Size
### 5.2 忽略 Changelog Topic 的大小
*   **Anti-pattern**: Storing massive objects or infinite history in a KTable without compaction configuration.
    **反模式**：在未設定 Compaction 的情況下，於 KTable 中儲存巨大物件或無限的歷史記錄。
*   **Why it's bad**: State recovery time increases linearly with changelog size. If an instance restarts, it might take hours to replay the log.
    **為何不好**：狀態恢復時間與 Changelog 大小成線性正比。若實例重啟，可能需要數小時來重播日誌。
*   **Solution**: Ensure the underlying topics for KTables are **Log Compacted**. Tune RocksDB memory usage.
    **解法**：確保 KTable 底層的 topics 設定為 **Log Compacted**。調整 RocksDB 的記憶體使用量。

### 5.3 Misunderstanding Window Grace Periods
### 5.3 誤解視窗寬限期（Grace Periods）
*   **Anti-pattern**: Assuming data always arrives in order.
    **反模式**：假設資料總是依序到達。
*   **Why it's bad**: Network delays happen. If you don't set a `grace` period, late-arriving data might be dropped silently or create a new window unexpectedly.
    **為何不好**：網路延遲時常發生。若未設定 `grace` 期間，遲到的資料可能會被靜默丟棄，或意外建立一個新視窗。
*   **Solution**: Explicitly define `windowedBy(...).grace(Duration.ofMinutes(5))`.
    **解法**：明確定義 `windowedBy(...).grace(Duration.ofMinutes(5))`。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a system to join a high-velocity stream (Clickstream) with a large, slowly changing table (User Metadata)?
### Q1: 你會如何設計一個系統，將高速串流（點擊流）與一個巨大且緩慢變動的資料表（使用者 Metadata）進行 Join？

*   **Key Points**:
    *   **KStream-KTable Join**: Requires co-partitioning (both topics must have same number of partitions and same partitioning key).
        **KStream-KTable Join**：需要協同分區（Co-partitioning，兩個 topics 必須有相同數量的 partitions 與相同的 partitioning key）。
    *   **GlobalKTable**: If the User table is not co-partitioned or re-partitioning is too expensive. GlobalKTable replicates the *entire* table to every application instance.
        **GlobalKTable**：如果使用者資料表未協同分區，或重新分區成本過高。GlobalKTable 會將*整個*資料表複製到每個應用程式實例。
    *   **Trade-off**: GlobalKTable increases local storage/network load (broadcast) but removes the need for re-partitioning the clickstream.
        **權衡**：GlobalKTable 增加了本地儲存/網路負載（廣播），但免除了重新分區點擊流的需求。

### Q2: Explain "Exactly-Once Semantics" (EOS) in Kafka Streams. How is it achieved?
### Q2: 解釋 Kafka Streams 中的「Exactly-Once Semantics」(EOS)。它是如何達成的？

*   **Key Points**:
    *   It's not magic; it uses **Transactions**.
        這不是魔法；它使用了 **Transactions**。
    *   The consumption (offset commit), processing (state store update via changelog), and production (output topic) are wrapped in a single atomic transaction.
        消費（offset commit）、處理（透過 changelog 更新 state store）與生產（output topic）被包裹在單一原子交易中。
    *   Requires `processing.guarantee="exactly_once_v2"`.
        需要設定 `processing.guarantee="exactly_once_v2"`。

### Q3: Why prefer Kafka Connect over writing a custom Python script to dump data to S3?
### Q3: 為什麼優先選擇 Kafka Connect，而不是寫一個客製化的 Python 腳本將資料 Dump 到 S3？

*   **Key Points**:
    *   **Offset Management**: Connect handles offset tracking automatically.
        **Offset 管理**：Connect 自動處理 offset 追蹤。
    *   **Parallelism**: Connect can spawn multiple tasks across workers based on partition count.
        **平行處理**：Connect 可根據 partition 數量在 workers 之間生成多個 tasks。
    *   **Schema Evolution**: Integration with Schema Registry to handle data format changes.
        **Schema 演進**：與 Schema Registry 整合以處理資料格式變更。
    *   **Standardization**: Configuration vs. Code maintenance.
        **標準化**：設定檔 vs. 程式碼維護。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
*   **Connect vs. Streams**: Connect is for moving data (In/Out); Streams is for transforming data (Processing).
    **Connect vs. Streams**：Connect 用於移動資料（進/出）；Streams 用於轉換資料（處理）。
*   **Stream-Table Duality**: Stream = History (Insert); Table = State (Upsert).
    **串流-資料表二元性**：Stream = 歷史（Insert）；Table = 狀態（Upsert）。
*   **State Management**: Kafka Streams uses RocksDB locally + Changelog topics remotely for fault tolerance.
    **狀態管理**：Kafka Streams 使用本地 RocksDB + 遠端 Changelog topics 進行容錯。
*   **Co-partitioning**: Essential for standard Joins. Data with the same key must be on the same partition.
    **協同分區**：標準 Joins 的必要條件。相同 Key 的資料必須位於相同的 partition。
*   **Windowing**: Requires understanding of Event Time vs. Processing Time and Grace Periods.
    **視窗化**：需要理解事件時間（Event Time）vs. 處理時間（Processing Time）以及寬限期（Grace Periods）。

### Next Steps (下一步)
*   **Advanced**: Explore **Kafka Streams Interactive Queries** to query the state store directly (turning Kafka into a database).
    **進階**：探索 **Kafka Streams Interactive Queries** 以直接查詢 state store（將 Kafka 變為資料庫）。
*   **Next Chapter**: Proceed to **Chapter 10: Observability and Operations** to learn how to monitor consumer lag, rebalancing storms, and RocksDB metrics.
    **下一章**：前往 **第 10 章：可觀測性與維運**，學習如何監控 Consumer Lag、Rebalancing 風暴與 RocksDB 指標。