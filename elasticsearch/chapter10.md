# 1. 前言與學習目標 (Introduction & Learning Goals)

在資深工程師的 System Design 面試或實務架構設計中，ElasticSearch (ES) 往往不是一個獨立存在的組件，而是龐大資料管線（Data Pipeline）中的關鍵一環。本章將跳脫單純的 API 操作，從架構師的視角探討如何將 ES 整合進複雜系統中。

In Senior System Design interviews or real-world architectural design, ElasticSearch (ES) rarely exists in isolation; it is a critical component within a larger data pipeline. This chapter moves beyond basic API operations to explore how to integrate ES into complex systems from an architect's perspective.

完成本章後，你應該能夠：

By the end of this chapter, you should be able to:

1.  **設計高可用搜尋架構 (Design High-Availability Search Architectures)**：區分「寫入密集型（Log Aggregation）」與「讀取密集型（E-commerce Search）」系統的架構差異。
    Distinguish architectural differences between "Write-Heavy (Log Aggregation)" and "Read-Heavy (E-commerce Search)" systems.
2.  **解決資料一致性問題 (Solve Data Consistency Issues)**：清楚解釋並實作 ES 與關聯式資料庫（RDBMS）之間的資料同步策略（如 Dual Write vs. CDC）。
    Clearly explain and implement data synchronization strategies between ES and RDBMS (e.g., Dual Write vs. CDC).
3.  **優化自動完成與建議系統 (Optimize Autocomplete & Suggesters)**：針對 Typeahead/Autocomplete 場景，權衡 Latency 與 Precision 的設計選擇。
    Weigh design choices regarding Latency vs. Precision for Typeahead/Autocomplete scenarios.
4.  **整合訊息佇列 (Integrate Message Queues)**：理解為何在 ES 前端引入 Kafka 是處理 Backpressure 與解耦的標準解法。
    Understand why introducing Kafka in front of ES is the standard solution for handling backpressure and decoupling.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 ES 在系統中的定位：二級索引與唯讀視圖 (Secondary Index & Read-Only View)

在大多數 System Design 場景中（除了 Log Analytics），ES 不應被視為「Source of Truth（唯一真理來源）」。你應該將 ES 視為一個**極其強大的二級索引（Secondary Index）**或是主資料庫的一個**唯讀、去正規化的視圖（Read-Only, Denormalized View）**。

In most System Design scenarios (except Log Analytics), ES should not be treated as the "Source of Truth." You should view ES as an **extremely powerful Secondary Index** or a **Read-Only, Denormalized View** of your primary database.

*   **RDBMS (PostgreSQL/MySQL)**: 負責 ACID 交易、資料正規化、確保資料完整性。
    **RDBMS (PostgreSQL/MySQL)**: Handles ACID transactions, data normalization, and ensures data integrity.
*   **ElasticSearch**: 負責模糊搜尋、全文檢索、聚合分析、地理空間查詢。資料通常是「最終一致（Eventually Consistent）」的。
    **ElasticSearch**: Handles fuzzy search, full-text search, aggregations, and geospatial queries. Data is typically "Eventually Consistent."

## 2.2 寫入與讀取路徑分離 (Separation of Write and Read Paths)

在設計搜尋系統時，心智模型應將「寫入路徑（Indexing Path）」與「讀取路徑（Search Path）」分開思考。

When designing search systems, your mental model should separate the "Indexing Path" from the "Search Path."

*   **Indexing Path**: 關注吞吐量（Throughput）、延遲（Lag）、錯誤處理（DLQ）。
    **Indexing Path**: Focuses on Throughput, Lag, and Error Handling (Dead Letter Queues).
*   **Search Path**: 關注查詢延遲（Latency）、快取（Caching）、相關性（Relevance）。
    **Search Path**: Focuses on Query Latency, Caching, and Relevance.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 場景一：日誌聚合系統 (Log Aggregation System)

這是典型的 **Write-Heavy** 系統。目標是收集分散式服務的 Log，供開發者除錯與監控。

This is a typical **Write-Heavy** system. The goal is to collect logs from distributed services for debugging and monitoring.

*   **架構特點 (Architecture Characteristics)**:
    *   **Buffering**: 使用 Kafka 作為緩衝區，防止流量突波（Spikes）壓垮 ES。
    *   **Time-Series Data**: 使用 Data Streams 或 Index Lifecycle Management (ILM) 自動滾動索引（Hot-Warm-Cold 架構）。
    *   **No Updates**: Log 通常是 Append-only，不需要處理複雜的 Update/Delete 邏輯。

## 3.2 場景二：電商商品搜尋 (E-commerce Search)

這是典型的 **Read-Heavy** 系統。目標是讓使用者快速找到商品，並支援過濾（Filtering）與排序（Sorting）。

This is a typical **Read-Heavy** system. The goal is to allow users to find products quickly, supporting filtering and sorting.

*   **架構特點 (Architecture Characteristics)**:
    *   **Denormalization**: 將關聯資料（如 Brand, Category, Reviews Summary）攤平（Flatten）存入 ES Document，避免 Join。
    *   **Synchronization**: 需處理 RDBMS 到 ES 的同步延遲。
    *   **Relevance Tuning**: 需結合商業邏輯（如庫存狀態、利潤率）調整評分（Function Score）。

---

# 4. 逐步示例：設計電商搜尋同步機制 (Walkthrough: Designing E-commerce Search Sync)

**問題背景**：我們有一個大型電商網站，商品資料存在 MySQL。當商家更新商品資訊（價格、描述）時，ES 必須盡快反映變更。

**Problem Context**: We have a large e-commerce site where product data lives in MySQL. When a merchant updates product info (price, description), ES must reflect these changes as soon as possible.

### 階段一：同步寫入 (Naive Approach: Synchronous Dual Write)

最直覺的做法是在應用層代碼中，更新 DB 後立即更新 ES。

The most intuitive approach is to update ES immediately after updating the DB within the application code.

```python
def update_product(product_id, data):
    db.execute("UPDATE products SET ...", data) # Transaction start
    es.index(index="products", id=product_id, body=data) # Network call
    db.commit() # Transaction commit
```

*   **為何不可行 (Why it fails)**:
    *   **雙重寫入問題 (Dual Write Problem)**: 如果 DB 成功但 ES 失敗（或反之），資料將不一致。
    *   **效能瓶頸 (Performance Bottleneck)**: ES 的寫入延遲會拖慢主要的 API 回應時間。
    *   **耦合 (Coupling)**: 業務邏輯與搜尋邏輯緊密耦合。

### 階段二：非同步佇列 (Better Approach: Async Queue)

將更新事件發送到 Message Queue (e.g., RabbitMQ/Kafka)，由 Worker 非同步寫入 ES。

Send update events to a Message Queue (e.g., RabbitMQ/Kafka), and have a Worker write to ES asynchronously.

*   **優點**: 解耦、API 回應快。
*   **缺點**: 應用層仍需負責發送事件。如果應用程式崩潰導致事件未發送，資料仍會不一致。

### 階段三：變更資料擷取 (Mature Solution: CDC with Debezium & Kafka)

這是 Big Tech 的標準做法。我們不依賴應用層發送事件，而是直接監聽資料庫的 Transaction Log (MySQL Binlog)。

This is the standard approach in Big Tech. Instead of relying on the application layer to send events, we listen directly to the database's Transaction Log (MySQL Binlog).

**架構流程 (Architecture Flow)**:
1.  **Source**: MySQL (Products Table).
2.  **CDC Connector**: Debezium (running on Kafka Connect) reads MySQL Binlog.
3.  **Message Bus**: Kafka Topic (`db.products.changes`).
4.  **Consumer/Sink**: Logstash or a Custom Go/Java Consumer reads from Kafka.
5.  **Transformation**: Consumer fetches extra data (e.g., joins Category names) to create a "Denormalized Document."
6.  **Destination**: ElasticSearch.

**為何這是最佳解 (Why this is robust)**:
*   **At-least-once delivery**: Kafka 確保訊息不丟失。
*   **Ordering**: Kafka Partition 確保同一 Product ID 的變更順序正確。
*   **Decoupling**: 搜尋團隊不需要去改動核心交易服務的程式碼。
*   **Backpressure**: 如果 ES 變慢，Consumer 可以暫停消費，不會影響主資料庫。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 把 ES 當作關聯式資料庫 (Treating ES like a Relational DB)
*   **錯誤 (Pitfall)**: 試圖在 ES 中頻繁使用 `Nested` 物件或 `Join` 欄位來模擬 SQL 的 Join，或者依賴 ES 的 Script 進行複雜的更新邏輯。
*   **後果 (Consequence)**: 查詢效能極差，記憶體消耗巨大。
*   **修正 (Fix)**: **Denormalize (去正規化)**。在寫入 ES 前，將資料「攤平」。以空間換取時間。

## 5.2 深分頁陷阱 (The Deep Pagination Trap)
*   **錯誤 (Pitfall)**: 使用 `from: 10000, size: 10` 來實作分頁。
*   **後果 (Consequence)**: ES 必須在每個 Shard 載入前 10010 筆資料，排序後再丟棄前 10000 筆。這會導致 CPU 飆升甚至 OOM (Out of Memory)。
*   **修正 (Fix)**:
    *   對於淺分頁（前 10 頁）：使用 `from` + `size`。
    *   對於深分頁或無限捲動（Infinite Scroll）：使用 `search_after` API。

## 5.3 Mapping Explosion (Mapping 爆炸)
*   **錯誤 (Pitfall)**: 允許使用者輸入任意 JSON 鍵值對，並開啟 Dynamic Mapping。
*   **後果 (Consequence)**: 如果使用者輸入了 1000 個不同的 Key，Cluster State 會變得極大，導致整個 Cluster 卡死。
*   **修正 (Fix)**: 設定 `dynamic: false` 或 `strict`。對於不可預測的欄位，使用 `flattened` 資料類型。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何設計一個即時建議（Autocomplete/Typeahead）系統？
**How would you design a real-time Autocomplete/Typeahead system?**

*   **高分回答要點 (Key Points)**:
    *   **Data Structure**: 討論 `Edge N-gram` tokenizer vs. `Completion Suggester` (FST based)。
    *   **Latency**: 強調 Autocomplete 對延遲極其敏感 (< 50ms)。
    *   **Optimization**:
        *   將 Autocomplete 獨立成一個輕量級的 Index。
        *   只存必要的欄位 (Suggestion Text, Weight, ID)。
        *   使用 `Fuzzy query` 處理拼寫錯誤（Typo Tolerance）。
    *   **Ranking**: 根據熱門度（Search Volume）預先計算權重。

## Q2: 在高併發寫入下，ES 出現 `RejectedExecutionException` 該怎麼辦？
**How do you handle `RejectedExecutionException` in ES under high write concurrency?**

*   **高分回答要點 (Key Points)**:
    *   **Root Cause**: 寫入 Queue 滿了，Thread Pool 耗盡。
    *   **Immediate Mitigation**: 在 Client 端 (e.g., Kafka Consumer) 實作 **Exponential Backoff** 重試機制。
    *   **Long-term Fix**:
        *   檢查 `refresh_interval`（預設 1s，寫入密集時可調大至 30s）。
        *   增加 Node 或 Shard 數量（Horizontal Scaling）。
        *   檢查是否由耗資源的 Mapping 或 Script 導致。

## Q3: 如何處理資料庫與 ES 的資料不一致？
**How do you handle data inconsistency between the Database and ES?**

*   **高分回答要點 (Key Points)**:
    *   承認「最終一致性」是常態。
    *   **Reconciliation (對帳)**: 定期跑一個 Batch Job，掃描 DB 與 ES 的資料指紋（Checksum/Timestamp），修復不一致的記錄。
    *   **Version Control**: 使用 `external` versioning (基於 DB 的 `updated_at` 或 version number) 防止舊資料覆蓋新資料（Out-of-order updates）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **ES is a View**: ES 是 DB 的唯讀視圖，不是 Source of Truth（Log 除外）。
2.  **CDC Pipeline**: 使用 Kafka + Debezium 是實現 DB 到 ES 同步最穩健的架構。
3.  **Denormalization**: 為了讀取效能，寫入前必須將資料攤平，避免在 Query Time 做 Join。
4.  **Write vs. Read**: 清楚區分 Indexing Path (Throughput) 與 Search Path (Latency) 的優化目標。
5.  **Avoid Deep Paging**: 使用 `search_after` 替代深層的 `from/size`。

## 後續延伸 (Next Steps)
*   **進階效能調校 (Advanced Performance Tuning)**: 深入研究 Segment Merging, Caching (Node Query Cache vs. Shard Request Cache)。
*   **叢集維運 (Cluster Operations)**: 學習 Cross-Cluster Replication (CCR) 與 Snapshot/Restore 策略。
*   **下一章預告**: 我們將探討 **ElasticSearch 的內部原理 (Internals)**，包括 Lucene Segment 的不可變性與倒排索引的物理結構。