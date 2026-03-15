# Chapter 04: 寫入效能優化與吞吐量
# Chapter 04: Write Performance Optimization

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在處理大規模日誌分析（Log Analytics）或高頻交易數據時，ElasticSearch 的寫入效能往往是系統的第一個瓶頸。對於資深工程師而言，僅僅知道「使用 Bulk API」是不夠的，必須深入理解 Lucene 的 Segment 合併機制、記憶體緩衝區（Buffer）與交易日誌（Translog）的交互作用。
In scenarios involving large-scale log analytics or high-frequency transaction data, ElasticSearch's write performance is often the first bottleneck. For a Senior Software Engineer, simply knowing to "use the Bulk API" is insufficient; one must deeply understand the Lucene segment merge mechanism and the interaction between memory buffers and the transaction log (Translog).

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準調校寫入參數**：理解並調整 `refresh_interval`、`indices.memory.index_buffer_size` 與 `translog` 設定，以換取更高的吞吐量。
    **Tune write parameters precisely**: Understand and adjust `refresh_interval`, `indices.memory.index_buffer_size`, and `translog` settings to trade off for higher throughput.
2.  **設計高併發寫入架構**：在系統設計面試中，能提出包含 Message Queue 緩衝與 Bulk Processor 的架構方案。
    **Design high-concurrency write architectures**: Propose architectural solutions involving Message Queue buffering and Bulk Processors in system design interviews.
3.  **診斷寫入效能瓶頸**：區分瓶頸是來自 CPU（序列化/分析）、I/O（Segment Merge/Flushing）還是記憶體壓力。
    **Diagnose write performance bottlenecks**: Distinguish whether the bottleneck stems from CPU (serialization/analysis), I/O (Segment Merge/Flushing), or memory pressure.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### Indexing Lifecycle: From Buffer to Disk
### 索引生命週期：從緩衝區到磁碟

要優化寫入，必須建立正確的「資料落地」心智模型。ElasticSearch 的寫入並非直接寫入磁碟，而是經過多層緩衝。
To optimize writes, you must build a correct mental model of "data persistence." ElasticSearch does not write directly to disk immediately; instead, data passes through multiple buffering layers.

1.  **Memory Buffer**: 當文件寫入時，首先進入 In-memory buffer。此時資料還無法被搜尋到。
    **Memory Buffer**: When a document is written, it first enters the In-memory buffer. At this stage, the data is not yet searchable.
2.  **Refresh (Buffer → Cache)**: 預設每 1 秒，Buffer 中的資料會被寫入到 Filesystem Cache 形成一個新的 Segment。此時資料變為「可搜尋」（Searchable），但尚未持久化到磁碟。這就是 ES 被稱為「近即時」（Near Real-Time, NRT）的原因。
    **Refresh (Buffer → Cache)**: By default, every 1 second, data in the Buffer is written to the Filesystem Cache to form a new Segment. The data becomes "searchable" but is not yet persisted to disk. This is why ES is called "Near Real-Time" (NRT).
3.  **Translog (Transaction Log)**: 為了防止斷電資料遺失，寫入 Buffer 的同時也會追加寫入 Translog。
    **Translog (Transaction Log)**: To prevent data loss during power failures, data written to the Buffer is simultaneously appended to the Translog.
4.  **Flush (Cache → Disk)**: 當 Translog 過大或達到時間閾值（預設 30 分鐘），會觸發 Flush。此時 Segment 被 `fsync` 到磁碟，Translog 被清空。
    **Flush (Cache → Disk)**: When the Translog gets too large or reaches a time threshold (default 30 minutes), a Flush is triggered. At this point, Segments are `fsync`ed to disk, and the Translog is cleared.

### 類比：圖書館的新書上架
### Analogy: New Book Arrival in a Library

*   **Memory Buffer** 是圖書館員手上的「待處理推車」。書還在車上，讀者找不到（不可搜尋）。
    **Memory Buffer** is the "processing cart" in the librarian's hands. Books are on the cart, and readers cannot find them (not searchable).
*   **Refresh** 是將推車上的書放到「新書展示架」（Filesystem Cache）。讀者可以看到了，但這些書還沒歸檔到永久書架，容易被移動。
    **Refresh** is moving books from the cart to the "New Arrivals Shelf" (Filesystem Cache). Readers can see them now, but they aren't filed on the permanent shelves yet and are easily moved.
*   **Flush** 是閉館時將展示架的書正式歸類到「永久書架」（Disk），並更新目錄系統。
    **Flush** is the process at closing time where books from the display shelf are officially filed onto the "Permanent Shelves" (Disk), and the catalog system is updated.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 典型架構：Log Ingestion Pipeline
### Typical Architecture: Log Ingestion Pipeline

在 System Design Interview 或實務中，處理高吞吐量寫入（例如每秒 100k+ logs）的標準模式如下：
In System Design Interviews or practice, the standard pattern for handling high-throughput writes (e.g., 100k+ logs per second) is as follows:

`App Servers` -> `Kafka (Buffer)` -> `Logstash / Vector (Aggregator)` -> `ElasticSearch`

*   **Kafka 的角色**：削峰填谷（Peak Shaving）。ES 的寫入效能受限於 CPU 和 Disk I/O，無法像記憶體資料庫那樣處理瞬間極大流量。Kafka 允許我們積累數據，再以最佳化的批次寫入 ES。
    **Role of Kafka**: Peak Shaving. ES write performance is bound by CPU and Disk I/O; it cannot handle massive instantaneous traffic bursts like an in-memory database. Kafka allows us to accumulate data and then write to ES in optimized batches.
*   **Client 端設計**：不應由 App Server 直接寫入 ES。這會導致連線數過多且難以控制 Bulk Size。應透過 Aggregator 進行批次處理。
    **Client-side Design**: App Servers should not write directly to ES. This leads to excessive connections and difficulty controlling Bulk Size. Writes should be batched via an Aggregator.

### 可靠性與效能的權衡 (Trade-offs)
### Trade-offs: Reliability vs. Performance

*   **Translog Durability**: 預設為 `request`（每次請求都 fsync），保證資料不丟失。若可接受當機時遺失幾秒鐘數據（如 Log 分析），可改為 `async`，大幅提升效能。
    **Translog Durability**: Defaults to `request` (fsync on every request), ensuring no data loss. If losing a few seconds of data during a crash is acceptable (e.g., Log Analytics), switching to `async` significantly boosts performance.
*   **Replica Count**: 在進行大量初始數據導入（Initial Load）時，可暫時將 `number_of_replicas` 設為 0，待寫入完成後再開啟。這能減少一半以上的寫入開銷（CPU & Network）。
    **Replica Count**: During massive Initial Load, you can temporarily set `number_of_replicas` to 0 and enable it after completion. This reduces write overhead (CPU & Network) by more than half.

---

## 4. 逐步示例
## 4. Walkthrough / Example

### 場景：優化一個寫入緩慢的索引任務
### Scenario: Optimizing a Slow Indexing Task

假設我們有一個任務需要將 1000 萬筆商品資料寫入 ES，目前的寫入速度僅有 2000 docs/s，目標是提升至 20,000 docs/s。
Suppose we have a task to index 10 million product records into ES. The current speed is only 2000 docs/s, and the goal is to increase it to 20,000 docs/s.

#### Step 1: 檢查並使用 Bulk API
#### Step 1: Check and Use Bulk API

最常見的錯誤是使用單筆 Index API。
The most common mistake is using the single Index API.

**Naive Approach (Python-like pseudo code):**
```python
# Slow: One HTTP request per document
for doc in documents:
    es.index(index="products", body=doc)
```

**Optimized Approach:**
```python
# Fast: One HTTP request per batch (e.g., 1000-5000 docs)
from elasticsearch.helpers import bulk

# Generator to yield actions
def generate_actions(docs):
    for doc in docs:
        yield {
            "_index": "products",
            "_source": doc
        }

# Bulk size depends on doc size, aim for 5MB-15MB payload per request
bulk(es, generate_actions(documents), chunk_size=2000)
```
*   **Why**: 減少了 HTTP 連線建立、JSON 序列化/反序列化以及網路往返（RTT）的開銷。
    **Why**: Reduces overhead from HTTP connection establishment, JSON serialization/deserialization, and Network Round Trip (RTT).

#### Step 2: 調整索引設定 (Index Settings)
#### Step 2: Adjust Index Settings

在開始寫入前，透過 `PUT /products/_settings` 調整參數。
Before starting the write process, adjust parameters via `PUT /products/_settings`.

```json
{
  "index": {
    "refresh_interval": "30s",  // Default is 1s. This is the biggest win.
    "number_of_replicas": 0,    // Disable replicas during initial load
    "translog": {
      "durability": "async",    // Don't fsync on every request
      "sync_interval": "5s"
    }
  }
}
```

*   **Refresh Interval**: 從 1s 改為 30s（或 -1 暫時關閉）。這減少了 Lucene 建立小 Segment 的頻率，從而減少了後續 Segment Merge 的巨大 I/O 壓力。
    **Refresh Interval**: Changed from 1s to 30s (or -1 to disable temporarily). This reduces the frequency of Lucene creating small segments, thereby reducing the massive I/O pressure of subsequent Segment Merges.
*   **Replicas**: 設為 0。寫入完成後再改回 1，讓 ES 利用傳輸 Segment File 的方式進行復製，比重複執行寫入邏輯快得多。
    **Replicas**: Set to 0. Change back to 1 after writing is done, letting ES replicate by transferring Segment Files, which is much faster than re-executing write logic.

#### Step 3: 客戶端 ID 生成策略
#### Step 3: Client-side ID Generation Strategy

**Bad Practice**: 指定自定義 ID (e.g., DB Primary Key)
**Bad Practice**: Specifying custom IDs (e.g., DB Primary Key)
```json
{ "index": { "_id": "123" } }
```
當你指定 ID 時，ES 必須先檢查該 ID 是否存在（為了更新或版本控制），這涉及磁碟讀取。

**Best Practice**: 使用 ES 自動生成 ID
**Best Practice**: Use ES auto-generated IDs
```json
{ "index": { } }
```
若業務允許，讓 ES 自動生成 ID。ES 會優化這個過程，跳過「檢查是否存在」的步驟，寫入效能可提升約 20%。
If business logic permits, let ES auto-generate IDs. ES optimizes this process, skipping the "check if exists" step, potentially boosting write performance by ~20%.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 1. Bulk Size 設定過大或過小
### 1. Bulk Size Too Large or Too Small

*   **錯誤**：認為 Bulk 越大越好，設定一次傳送 50MB 或 100MB。
    **Pitfall**: Thinking "bigger is better" for Bulk, sending 50MB or 100MB at once.
*   **後果**：可能導致 ES 節點 Heap Memory 壓力過大，觸發頻繁 GC 甚至 OOM（Out of Memory），反而阻塞寫入。
    **Consequence**: Can cause excessive Heap Memory pressure on ES nodes, triggering frequent GC or even OOM (Out of Memory), blocking writes.
*   **建議**：單次 Payload 控制在 5MB - 15MB 之間。從 5MB 開始測試，觀察吞吐量曲線何時變平。
    **Recommendation**: Keep single payload between 5MB - 15MB. Start testing at 5MB and observe when the throughput curve flattens.

### 2. 忽略 Mapping Explosion
### 2. Ignoring Mapping Explosion

*   **錯誤**：寫入大量動態欄位（Dynamic Mapping），例如將使用者自定義的 JSON 直接塞入 ES。
    **Pitfall**: Writing many dynamic fields (Dynamic Mapping), such as dumping user-defined JSON directly into ES.
*   **後果**：Cluster State 變得極大（因為 Mapping 儲存在 Cluster State 中），每次更新 Mapping 都需要同步到所有節點，導致寫入卡頓（Master node bottleneck）。
    **Consequence**: Cluster State becomes huge (since Mapping is stored there). Every Mapping update requires synchronization to all nodes, causing write stalls (Master node bottleneck).
*   **建議**：設定 `dynamic: false` 或 `strict`，並使用 `flattened` 資料型態處理不可預知的結構。
    **Recommendation**: Set `dynamic: false` or `strict`, and use the `flattened` data type for unpredictable structures.

### 3. 使用過多的 Analyzers
### 3. Using Excessive Analyzers

*   **錯誤**：在不需要全文檢索的欄位（如 ID、Enum、Tags）上使用標準分詞器。
    **Pitfall**: Using standard tokenizers on fields that don't need full-text search (e.g., IDs, Enums, Tags).
*   **後果**：CPU 花費大量時間在 Tokenization 和 Filter 上，成為寫入瓶頸。
    **Consequence**: CPU spends significant time on Tokenization and Filtering, becoming the write bottleneck.
*   **建議**：對於精確值，務必使用 `keyword` type。
    **Recommendation**: Always use the `keyword` type for exact values.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 在高併發寫入時，ES 叢集出現 `429 Too Many Requests`，你會如何處理？
### Q1: During high-concurrency writes, the ES cluster returns `429 Too Many Requests`. How would you handle this?

*   **高分回答要點**：
    **Key Points for a High Score**:
    *   **識別原因**：說明 429 通常來自 Thread Pool (write queue) 滿載。
    *   **短期解法**：Client 端必須實作 **Exponential Backoff**（指數退避）重試機制。
    *   **架構解法**：引入 Kafka 作為 Buffer。
    *   **參數調優**：檢查 `refresh_interval` 是否過短？是否正在發生大規模 Segment Merge？
    *   **硬體層面**：檢查是否 IOPS 達瓶頸（I/O Wait 高）。

### Q2: 為什麼 ES 的寫入是 "Near Real-Time" 而不是 "Real-Time"？這對系統設計有什麼影響？
### Q2: Why is ES writing "Near Real-Time" instead of "Real-Time"? What impact does this have on system design?

*   **高分回答要點**：
    **Key Points for a High Score**:
    *   **機制解釋**：解釋 `refresh` 操作將 Buffer 轉為 Segment 的時間差（預設 1s）。
    *   **效能權衡**：說明為了寫入吞吐量，我們犧牲了立即可見性（Visibility）。
    *   **設計影響**：設計系統時，不能假設「寫入成功後立刻讀取」（Read-your-own-writes）會成功。如果業務強烈依賴強一致性（如庫存扣減），ES 不適合作為 Source of Truth，應查 DB。

### Q3: 使用自定義 ID (Custom ID) 與自動生成 ID (Auto-generated ID) 在效能上有何差異？
### Q3: What is the performance difference between using Custom IDs and Auto-generated IDs?

*   **高分回答要點**：
    **Key Points for a High Score**:
    *   **Lucene 運作**：Custom ID 寫入時，Lucene 必須檢查該 ID 是否已存在於任何 Segment 中（Bloom Filter 加速，但仍有開銷），以決定是 Create 還是 Update。
    *   **Auto ID 優勢**：Auto ID 被視為 Append-only，跳過檢查步驟，寫入速度更快。
    *   **情境選擇**：如果是 Log 數據，絕對使用 Auto ID；如果是同步 DB 數據，為了去重（Idempotency），必須使用 Custom ID（通常是 DB PK），但要接受效能折損。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 重點回顧 (Key Takeaways)
1.  **Bulk Processing**: 始終使用 Bulk API，單次 Payload 控制在 5-15 MB。
2.  **Refresh Interval**: 高寫入時將其調大（30s+）或關閉，這是提升吞吐量最有效的單一設定。
3.  **Translog Strategy**: 對於允許少量數據遺失的場景，使用 `async` durability。
4.  **Buffer & Cache**: 理解 Memory Buffer -> Filesystem Cache (Refresh) -> Disk (Flush) 的流程。
5.  **ID Generation**: 優先使用 Auto-generated ID 以避免版本檢查開銷。
6.  **Architecture**: 使用 Kafka/Queue 進行削峰填谷，保護 ES 不被瞬間流量壓垮。

### 下一步 (Next Steps)
*   **延伸閱讀**：深入了解 Lucene 的 **Merge Policy**（TieredMergePolicy），這決定了 Segment 如何合併，直接影響長期寫入效能與磁碟空間效率。
*   **下一章預告**：掌握了寫入優化後，下一章我們將探討 **Chapter 05: Search Performance Optimization (搜尋效能優化)**，分析 Caching 機制與 Query Profiling。