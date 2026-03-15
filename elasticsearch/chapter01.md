# Chapter 01: Internals and Core Architecture
# 第 01 章：底層原理與核心架構

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Engineer, treating ElasticSearch (ES) as a "black box" search engine is no longer sufficient. To optimize for high throughput, low latency, and cost-efficiency, you must understand how data is stored, indexed, and retrieved on disk. This chapter peels back the layers of Lucene to explain the physical layout of your data.
作為一名資深工程師，僅將 ElasticSearch (ES) 視為一個「黑盒」搜尋引擎已不足夠。為了優化高吞吐量、低延遲與成本效益，你必須理解資料是如何在磁碟上被儲存、索引與檢索的。本章將揭開 Lucene 的面紗，解釋資料的物理佈局。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Explain the "Near Real-Time" (NRT) architecture**: Distinguish the critical differences between `refresh`, `flush`, and `translog`, and how they impact data visibility and durability.
    **解釋「近即時」（NRT）架構**：區分 `refresh`、`flush` 與 `translog` 的關鍵差異，以及它們如何影響資料的可見性與持久性。
2.  **Master Data Structures**: articulate why **Inverted Indices** are used for search while **Doc Values** are used for sorting/aggregating, and the performance implications of each.
    **掌握資料結構**：清楚說明為何 **Inverted Indices** 用於搜尋，而 **Doc Values** 用於排序/聚合，以及兩者的效能影響。
3.  **Understand Segment Immutability**: Analyze how the "write-once" nature of Lucene segments affects update/delete costs and the necessity of segment merging.
    **理解 Segment 的不可變性**：分析 Lucene Segment「寫入一次」的特性如何影響更新/刪除的成本，以及 Segment Merging 的必要性。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

To understand ElasticSearch, you must understand Apache Lucene. ElasticSearch is essentially a distributed system that manages Lucene instances (Shards).
要理解 ElasticSearch，必須先理解 Apache Lucene。ElasticSearch 本質上是一個管理 Lucene 實例（Shards）的散佈式系統。

### 2.1 The Lucene Segment (The Unit of Storage)
### 2.1 Lucene Segment（儲存單位）

**Mental Model**: Think of a **Shard** not as a single file, but as a directory of many mini-indices called **Segments**. A Segment is an **immutable** container of data.
**心智模型**：不要將 **Shard** 視為單一檔案，而應視為包含許多小型索引（稱為 **Segments**）的目錄。Segment 是一個**不可變**的資料容器。

*   **Immutability**: Once a segment is written to disk, it is never modified.
    **不可變性**：一旦 Segment 被寫入磁碟，就永遠不會被修改。
*   **Deletes**: Deleting a document doesn't remove it immediately. It just marks it as "deleted" in a separate `.del` file.
    **刪除**：刪除文件不會立即移除它，只是在獨立的 `.del` 檔案中將其標記為「已刪除」。
*   **Updates**: An update is actually an atomic **Delete** followed by an **Index** (create) operation.
    **更新**：更新操作實際上是一個原子的 **刪除** 動作，緊接著一個 **索引**（建立）動作。

### 2.2 Inverted Index vs. Doc Values
### 2.2 倒排索引 vs. Doc Values

This is the most critical distinction for query performance.
這是查詢效能中最關鍵的區別。

| Feature | Inverted Index (倒排索引) | Doc Values (正排索引 / 列式儲存) |
| :--- | :--- | :--- |
| **Primary Use** | Full-text Search (Filtering) | Sorting, Aggregations, Scripting |
| **Structure** | Term $\to$ List of Doc IDs | Doc ID $\to$ Value |
| **Analogy** | The "Index" at the back of a book. | An Excel column or SQL Columnar Store. |
| **Format** | Optimized for finding documents containing specific words. | Optimized for sequential access to values across many documents. |

**Why do we need both?**
The Inverted Index is excellent for answering "Which documents contain 'Apple'?", but terrible for answering "What is the average price of all documents found?". Accessing the value of a field via the Inverted Index requires random disk access, which is slow. **Doc Values** solve this by storing data in a column-oriented fashion, friendly to OS file system caching.

**為什麼兩者都需要？**
倒排索引非常擅長回答「哪些文件包含 'Apple'？」，但對於回答「找到的所有文件的平均價格是多少？」則表現極差。透過倒排索引存取欄位值需要隨機磁碟存取，速度很慢。**Doc Values** 透過列式儲存解決了這個問題，對作業系統的檔案系統快取非常友善。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production system design, understanding these internals dictates how you tune for **Write Heavy** vs. **Read Heavy** workloads.
在生產環境的系統設計中，理解這些內部原理決定了你如何針對 **寫入密集型** 與 **讀取密集型** 的工作負載進行調校。

### 3.1 The "Near Real-Time" Trade-off
### 3.1 「近即時」的權衡

In system design interviews, candidates often claim ES is "Real-Time." It is not. It is **Near Real-Time (NRT)**.
在系統設計面試中，候選人常聲稱 ES 是「即時的」。它不是。它是**近即時（NRT）**。

*   **Latency Gap**: There is a gap (default 1 second) between when data is indexed and when it is searchable. This is controlled by the `refresh_interval`.
    **延遲缺口**：資料被索引與資料可被搜尋之間存在時間差（預設 1 秒）。這由 `refresh_interval` 控制。
*   **Throughput Impact**: Setting `refresh_interval` to `-1` or `30s` during bulk indexing can increase write throughput by 20–50% because it reduces the overhead of creating new Lucene segments.
    **吞吐量影響**：在大量索引期間將 `refresh_interval` 設為 `-1` 或 `30s`，可以提升 20–50% 的寫入吞吐量，因為這減少了建立新 Lucene Segment 的開銷。

### 3.2 Reliability & The Translog
### 3.2 可靠性與 Translog

If ES crashes, memory buffers are lost. To prevent data loss, ES uses a **Write Ahead Log (WAL)** called the **Translog**.
如果 ES 崩潰，記憶體緩衝區的資料會遺失。為了防止資料遺失，ES 使用**預寫式日誌（WAL）**，稱為 **Translog**。

*   **Synchronous vs. Asynchronous**: By default, the translog is `fsync`ed to disk after every request (`index.translog.durability: request`). This guarantees durability but limits IOPS.
    **同步 vs. 非同步**：預設情況下，Translog 會在每次請求後 `fsync` 到磁碟（`index.translog.durability: request`）。這保證了持久性，但限制了 IOPS。
*   **Design Decision**: For non-critical log data (e.g., trace logs where losing 5 seconds of data is acceptable), switching to `async` can significantly boost performance.
    **設計決策**：對於非關鍵日誌資料（例如：可以接受遺失 5 秒資料的追蹤日誌），切換到 `async` 可以顯著提升效能。

---

## 4. Walkthrough: The Life of a Write Operation
## 4. 逐步示例：寫入操作的生命週期

Let's trace a document from ingestion to persistence. This flow is crucial for debugging performance issues.
讓我們追蹤一份文件從攝入到持久化的過程。這個流程對於除錯效能問題至關重要。

### Scenario: Indexing a Log Entry
### 情境：索引一條日誌

1.  **Write to Memory Buffer & Translog**
    **寫入記憶體緩衝區與 Translog**
    *   The document is written to an in-memory buffer (not searchable yet).
    *   Simultaneously, it is appended to the `translog` on disk (for crash recovery).
    *   文件被寫入記憶體緩衝區（此時尚未可被搜尋）。
    *   同時，它被追加到磁碟上的 `translog`（用於崩潰恢復）。

2.  **Refresh (The "NRT" Step)**
    **Refresh（NRT 步驟）**
    *   Every 1 second (default), the buffer is committed to a new **Segment**.
    *   The segment is opened for search.
    *   The in-memory buffer is cleared.
    *   *Note: The data is now searchable, but not yet fully persisted (fsync'ed) to the main data store, though it is safe in the translog.*
    *   每 1 秒（預設），緩衝區被提交為一個新的 **Segment**。
    *   該 Segment 開放供搜尋。
    *   記憶體緩衝區被清空。
    *   *注意：資料現在可被搜尋，但尚未完全持久化（fsync）到主資料儲存區，儘管它在 translog 中是安全的。*

3.  **Flush (The Persistence Step)**
    **Flush（持久化步驟）**
    *   When the translog gets too big or after a specific time (default 30 mins), a **Flush** occurs.
    *   All segments in the file system cache are `fsync`ed to disk.
    *   The translog is cleared/truncated.
    *   當 translog 過大或經過特定時間（預設 30 分鐘）後，會觸發 **Flush**。
    *   檔案系統快取中的所有 Segment 被 `fsync` 到磁碟。
    *   Translog 被清空/截斷。

4.  **Merge (The Housekeeping Step)**
    **Merge（整理步驟）**
    *   Over time, many small segments accumulate.
    *   Background threads merge them into larger segments and physically remove deleted documents.
    *   隨著時間推移，會累積許多小 Segment。
    *   背景執行緒將它們合併為較大的 Segment，並物理移除被標記刪除的文件。

### Code/Config Example: Optimizing for Bulk Load
### 程式碼/配置範例：針對大量載入進行優化

If you are backfilling 100GB of data, the default settings will cause too many small segments and frequent merges.
如果你正在回填 100GB 的資料，預設設定會導致過多的小 Segment 和頻繁的合併。

```json
PUT /my-index-001/_settings
{
  "index": {
    "refresh_interval": "-1",          // Stop refreshing during bulk load
    "number_of_replicas": 0,           // Disable replicas to save network/disk IO
    "translog.durability": "async"     // Fsync less frequently
  }
}
```

*After loading is complete:*
*載入完成後：*

```json
PUT /my-index-001/_settings
{
  "index": {
    "refresh_interval": "1s",
    "number_of_replicas": 1
  }
}
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Deep Paging (The `from` + `size` Trap)
### 5.1 深度分頁（`from` + `size` 陷阱）

*   **Anti-pattern**: Using `from=10000, size=10` to get the 10,001st record.
    **反模式**：使用 `from=10000, size=10` 來取得第 10,001 筆記錄。
*   **Why it's bad**: ES is distributed. To get results 10,000 to 10,010, **each shard** must fetch its top 10,010 results and send them to the coordinating node. The coordinating node then sorts `number_of_shards * 10,010` documents in memory. This kills the heap.
    **為何不好**：ES 是分散式的。為了取得第 10,000 到 10,010 筆結果，**每個 Shard** 必須取出它的前 10,010 筆結果並傳送給協調節點（Coordinating Node）。協調節點接著必須在記憶體中排序 `number_of_shards * 10,010` 份文件。這會耗盡 Heap 記憶體。
*   **Solution**: Use **`search_after`** (cursor-based pagination) or Scroll API (for batch processing, not user requests).
    **解決方案**：使用 **`search_after`**（基於游標的分頁）或 Scroll API（用於批次處理，而非使用者請求）。

### 5.2 High Cardinality in Aggregations
### 5.2 聚合中的高基數（High Cardinality）

*   **Anti-pattern**: Aggregating on a field with millions of unique values (e.g., User IDs, IP addresses) without proper planning.
    **反模式**：在沒有適當規劃的情況下，對擁有數百萬個唯一值的欄位（如 User ID、IP 位址）進行聚合。
*   **Why it's bad**: This can cause "Global Ordinals" to be built on the heap, leading to OutOfMemory (OOM) errors or massive GC pauses.
    **為何不好**：這會導致在 Heap 上建立「全域序數（Global Ordinals）」，引發記憶體不足（OOM）錯誤或巨大的 GC 停頓。
*   **Solution**: Use `composite` aggregations for pagination or ensure sufficient off-heap memory if using Doc Values heavily.
    **解決方案**：使用 `composite` 聚合進行分頁，或者如果大量使用 Doc Values，請確保有足夠的堆外記憶體（Off-heap memory）。

### 5.3 Frequent Updates on Immutable Segments
### 5.3 在不可變 Segment 上頻繁更新

*   **Anti-pattern**: Using ES as a primary database for rapidly changing counters (e.g., "view count" updated every second).
    **反模式**：將 ES 作為主要資料庫，用於快速變動的計數器（例如：每秒更新的「瀏覽次數」）。
*   **Why it's bad**: Every update creates a new document and marks the old one as deleted. This bloats the index with `.del` files and triggers aggressive segment merging, consuming CPU/IO.
    **為何不好**：每次更新都會建立新文件並將舊文件標記為刪除。這會讓索引充斥著 `.del` 檔案，並觸發激進的 Segment Merging，消耗大量 CPU/IO。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How does ElasticSearch achieve Near Real-Time search?
### Q1: ElasticSearch 如何實現近即時（NRT）搜尋？

*   **Key Points**:
    *   Explain the lifecycle: Buffer $\to$ Refresh $\to$ Segment (OS Cache) $\to$ Searchable.
    *   Mention that `fsync` (Flush) is NOT required for searchability, only for durability.
    *   Discuss `refresh_interval`.
*   **關鍵要點**：
    *   解釋生命週期：Buffer $\to$ Refresh $\to$ Segment (OS Cache) $\to$ Searchable。
    *   提及 `fsync` (Flush) 對於「可搜尋性」並非必要，僅對「持久性」必要。
    *   討論 `refresh_interval`。

### Q2: Why are updates in ElasticSearch expensive?
### Q2: 為什麼 ElasticSearch 中的更新操作很昂貴？

*   **Key Points**:
    *   Segments are immutable.
    *   Update = Delete (soft) + Index (new).
    *   Deleted documents still occupy disk space and are processed during search (then filtered out) until a Merge operation cleans them up.
*   **關鍵要點**：
    *   Segment 是不可變的。
    *   更新 = 刪除（軟刪除）+ 索引（新增）。
    *   被刪除的文件仍佔用磁碟空間，且在搜尋時仍會被處理（然後被過濾掉），直到 Merge 操作將其清除。

### Q3: Design a logging system for 1TB/day logs. How do you tune ES?
### Q3: 為每天 1TB 的日誌設計一個系統。你會如何調校 ES？

*   **Key Points**:
    *   **Write Optimization**: Increase `refresh_interval` (e.g., 30s), use `async` translog, bulk API.
    *   **Architecture**: Hot-Warm-Cold architecture (Keep active logs on SSD, move older logs to HDD).
    *   **Rollover**: Use Index Lifecycle Management (ILM) to roll over indices based on size/age.
*   **關鍵要點**：
    *   **寫入優化**：增加 `refresh_interval`（如 30s），使用 `async` translog，使用 Bulk API。
    *   **架構**：Hot-Warm-Cold 架構（活躍日誌存 SSD，舊日誌移至 HDD）。
    *   **Rollover**：使用索引生命週期管理（ILM）根據大小/時間滾動索引。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Segments are Immutable**: This simplifies concurrency and caching but makes updates expensive.
    **Segment 是不可變的**：這簡化了並發與快取，但使更新變得昂貴。
2.  **Inverted Index vs. Doc Values**: Know which structure powers your query (Search vs. Sort/Agg).
    **倒排索引 vs. Doc Values**：了解哪種結構支援你的查詢（搜尋 vs. 排序/聚合）。
3.  **Refresh vs. Flush**: Refresh makes data visible (Searchable); Flush makes data persistent (On Disk).
    **Refresh vs. Flush**：Refresh 使資料可見（可搜尋）；Flush 使資料持久化（存入磁碟）。
4.  **Translog**: The safety net that bridges the gap between memory buffer and disk persistence.
    **Translog**：連接記憶體緩衝區與磁碟持久化之間的安全網。
5.  **Merge**: The background process that keeps the number of segments manageable and reclaims space from deleted docs.
    **Merge**：背景程序，用於將 Segment 數量維持在可管理範圍，並回收被刪除文件佔用的空間。

### Next Steps
### 後續延伸

*   **Chapter 02**: **Distributed Model & Consensus** (Nodes, Shards, Replica, and Zen Discovery).
    **第 02 章**：**分散式模型與共識**（Nodes, Shards, Replica 與 Zen Discovery）。
*   **Action Item**: Check the `refresh_interval` and `translog` settings in your current production clusters. Are they at defaults? Why?
    **行動項目**：檢查你目前生產環境叢集中的 `refresh_interval` 與 `translog` 設定。它們是預設值嗎？為什麼？