# 生態系整合：Connect 與 Streams 的架構決策 / Ecosystem Integration: Kafka Connect and Streams

## Mental Model｜心智模型

在 Kafka 的生態系中，我們不應僅將其視為一個「訊息隊列 (Message Queue)」，而應視為一個 **「流動資料的中央神經系統」**。在這個系統中，我們面臨兩個核心問題：如何讓資料進出？以及如何處理流動中的資料？

### 1. The "Plumbing" vs. "Processing" Dichotomy
建立架構決策時，請使用以下心智模型區分 **Kafka Connect** 與 **Kafka Streams**：

*   **Kafka Connect 是「管線工程 (Plumbing)」**：
    *   它的職責是 **搬運 (Move)** 與 **適配 (Adapt)**。
    *   它是 **Configuration over Code**（重配置，輕代碼）。
    *   **Mental Image**: 連接水管的轉接頭。你不需要為了把水從水庫接到水龍頭而重新發明水管，你只需要配置好接口。
    *   **Use Case**: 資料庫 (CDC)、S3、Elasticsearch、Snowflake 之間的資料同步。

*   **Kafka Streams 是「大腦邏輯 (Processing)」**：
    *   它的職責是 **轉換 (Transform)**、**聚合 (Aggregate)** 與 **反應 (React)**。
    *   它是 **Library / Code**（嵌入在你的應用程式中）。
    *   **Mental Image**: 濾水器或化學反應槽。水流進來，經過過濾、混合、煮沸（Windowing/Joining），變成咖啡流出去。
    *   **Use Case**: 即時詐欺偵測、動態定價、點擊流分析、ETL 邏輯。

### 2. The Integration Spectrum
決策光譜如下：
`[ Kafka Connect (No code) ]` <---> `[ ksqlDB (SQL) ]` <---> `[ Kafka Streams (DSL/Java) ]` <---> `[ Native Producer/Consumer (Low-level) ]`

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Kafka Connect Patterns

*   **CDC (Change Data Capture) First**:
    *   不要在應用層寫 Dual Write (同時寫 DB 又寫 Kafka)，這會導致資料不一致。
    *   **Pattern**: 使用 **Debezium** Connector 監聽資料庫的 Transaction Log (Binlog/WAL)，將 DB 變更轉為 Event Stream。這是實現 Microservices Data Liberation 的黃金標準。
*   **SMT (Single Message Transforms) for Lightweight Tasks**:
    *   使用 SMT 進行簡單的資料清洗，如：Masking PII (遮蔽個資)、欄位重新命名、過濾特定紀錄。
    *   **Rule of Thumb**: 如果邏輯牽涉到「跨多條訊息」或「外部查詢」，**不要**用 SMT，請轉用 Streams。
*   **Distributed Mode for Production**:
    *   永遠在生產環境使用 **Distributed Mode**。它提供自動的負載平衡 (Rebalancing) 與容錯 (Fault Tolerance)。Standalone 模式僅限於筆電開發測試。

### 2. Kafka Streams Patterns

*   **Co-partitioning for Joins (協同分區)**:
    *   在進行 `join` 操作前，必須確保兩個 Topic 的 **Partition Count 相同** 且 **Partitioning Strategy (Key)** 相同。
    *   **Pattern**: 如果來源不同，先執行 `repartition()` 操作將資料對齊，再進行 Join。
*   **GlobalKTable for Reference Data**:
    *   當你需要將「大流量的主流 (Stream)」與「小流量的靜態表 (Lookup Table)」進行 Join 時（例如：訂單流 join 產品資訊表）。
    *   **Best Practice**: 使用 `GlobalKTable` 載入產品表。它會將該 Topic 的全部資料複製到所有應用實例中，這樣就可以進行 **Non-key Join**，且不需要對主流量進行 Repartition，大幅提升效能。
*   **Interactive Queries (IQ)**:
    *   不要將計算結果寫回 DB 僅為了讓前端查詢。Kafka Streams 的 State Store (RocksDB) 本身就可以被查詢。
    *   **Pattern**: 使用 Interactive Queries 直接透過 REST API 暴露 Streams 內部的狀態（如目前的庫存計數）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "External Lookup" Trap (外部查詢陷阱)
*   **Anti-pattern**: 在 Kafka Streams 的 `map` 或 `transform` 過程中，呼叫外部 REST API 或查詢遠端資料庫。
*   **Why**: 這是效能殺手。Stream 處理速度極快 (e.g., 10k msg/sec)，外部 API 會有 Latency (e.g., 200ms)。這會導致 Backpressure，進而拖垮整個 Consumer Group。
*   **Solution**:
    1.  將外部資料透過 Connect 匯入成 Kafka Topic (KTable/GlobalKTable)，在內部進行 Join。
    2.  若必須呼叫，使用 Async I/O 並加上極短的 Timeout 與 Circuit Breaker，或使用 Sidecar Caching。

### 2. Abusing Connect for ETL (濫用 Connect 做 ETL)
*   **Anti-pattern**: 試圖透過撰寫極其複雜的 SMT (Single Message Transform) 來完成商業邏輯。
*   **Why**: SMT 難以除錯、難以測試，且會拖慢 Connector 的吞吐量。
*   **Solution**: Connect 只負責「搬運」和「格式轉換」。複雜邏輯請交給 Kafka Streams 或 ksqlDB 處理完後，再寫入目標 Topic 供 Sink Connector 使用。

### 3. Ignoring Schema Registry (忽視 Schema 管理)
*   **Anti-pattern**: 在 Connect 或 Streams 中使用純 JSON 或 String，沒有 Schema 約束。
*   **Why**: 當上游 DB 欄位變更時，下游的 Sink Connector 或 Stream App 會直接崩潰 (Poison Pill)。
*   **Solution**: 強制使用 Avro, Protobuf 或 JSON Schema，並搭配 Schema Registry 進行相容性檢查。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Connect vs. Streams vs. Client
在引入新組件前，請依序回答：

1.  **資料源/目的地是標準系統嗎？** (DB, S3, ES, MQ)
    *   Yes -> **Kafka Connect** (優先尋找 Confluent Hub 上的 Verified Connector)。
    *   No -> 考慮自行開發 Connector (若需重複使用) 或使用 Native Client。
2.  **需要進行狀態運算嗎？** (Windowing, Aggregation, Join)
    *   Yes -> **Kafka Streams**。
3.  **邏輯是否僅為簡單過濾或單條訊息轉換？**
    *   Yes -> **Kafka Connect SMT** (若在搬運過程中) 或 **ksqlDB** (若需快速驗證)。
4.  **是否需要 Ad-hoc 探索性查詢？**
    *   Yes -> **ksqlDB**。

### Production Readiness Checklist

#### Kafka Connect
- [ ] **Error Handling**: 是否配置了 Dead Letter Queue (DLQ)？ (`errors.deadletterqueue.topic.name`)
- [ ] **Offsets**: 是否備份了 Connect Offsets Topic？(這是 Connector 的狀態核心)
- [ ] **Monitoring**: 是否監控了 Consumer Lag 以及 Connector Status (Running/Failed)？
- [ ] **Idempotence**: Sink Connector 是否支援等冪寫入？(避免重試導致資料重複)

#### Kafka Streams
- [ ] **State Store**: 是否配置了足夠的磁碟空間給 RocksDB？
- [ ] **Changelog Topics**: 內部生成的 Changelog Topic 是否配置了 `compact` 清理策略？
- [ ] **Reset Tool**: 是否準備好 `kafka-streams-application-reset` 的操作流程以應對災難復原？
- [ ] **Grace Period**: Window 操作是否設定了合理的 Grace Period 以處理遲到資料？

---

## Real-world examples｜實戰案例

### Scenario 1: Legacy Database to Search Index (The "Sidecar" Pattern)
**情境**：一個老舊的 MySQL 單體應用，需要將商品資料同步到 Elasticsearch 以提供全文搜尋，但不能修改遺留程式碼。

**Architecture**:
1.  **Source**: 使用 **Debezium MySQL Connector** 監聽 Binlog。
    *   *Config*: `snapshot.mode=initial` (全量+增量)。
2.  **Process**: 資料庫中的資料是正規化的 (Normalized)，但 ES 需要反正規化 (Denormalized) 的寬表。
    *   使用 **Kafka Streams** 訂閱 `products`, `categories`, `brands` topics。
    *   將 `categories` 和 `brands` 轉為 `GlobalKTable`。
    *   將 `products` stream 與這兩張表 Join，生成一個包含完整資訊的 JSON 物件。
    *   輸出到 `enriched-products` topic。
3.  **Sink**: 使用 **Elasticsearch Sink Connector**。
    *   訂閱 `enriched-products`。
    *   *Config*: `batch.size=2000` (批次寫入提升效能)。

### Scenario 2: Real-time Fraud Detection (Stateful Processing)
**情境**：銀行需要在刷卡當下，判斷該用戶是否在 5 分鐘內於不同國家進行了交易。

**Architecture**:
1.  **Input**: `transactions` topic (Key: UserID).
2.  **Logic (Kafka Streams)**:
    *   定義一個 Session Window 或 Sliding Window (Size: 5 min)。
    *   `groupByKey()` (依用戶分組)。
    *   `aggregate()`: 收集該視窗內的交易地點 (Location)。
    *   **Rule**: 如果 `Set<Location>.size() > 1` 且地點物理距離過遠 -> 觸發 Alert。
3.  **Output**: `fraud-alerts` topic。
4.  **Action**: 一個簡單的 Consumer 訂閱 `fraud-alerts` 並發送簡訊/鎖卡。

**Key Takeaway**: 這種「基於時間窗口的跨事件關聯」是 Kafka Streams 的強項，若用傳統 DB 查詢或 Stateless Consumer 實作會極其複雜且低效。