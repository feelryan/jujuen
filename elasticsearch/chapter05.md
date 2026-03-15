# Chapter 05: Query Performance Tuning and Caching
# 第五章：查詢效能調優與快取機制

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In high-throughput distributed systems, ElasticSearch performance issues often manifest as high P99 latency or CPU spikes during traffic surges. For a Senior Engineer, "it works" is not enough; you must understand *how* it executes. This chapter focuses on the runtime mechanics of search execution, specifically how to leverage contexts and caches to optimize read performance.
在高吞吐量的分散式系統中，ElasticSearch 的效能問題通常表現為高 P99 延遲或流量激增時的 CPU 飆升。對於資深工程師而言，「能跑」是不夠的，你必須理解它「如何」執行。本章將聚焦於搜尋執行的執行期機制（runtime mechanics），特別是如何利用 Context（上下文）與 Cache（快取）來優化讀取效能。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Distinguish and Apply Contexts:** deeply understand the internal execution differences between **Query Context** (scoring) and **Filter Context** (binary yes/no) and how they affect the **Node Query Cache**.
    **區分與應用 Context：** 深入理解 **Query Context**（算分）與 **Filter Context**（二元是非）的內部執行差異，以及它們如何影響 **Node Query Cache**。
2.  **Master Caching Layers:** Explain the specific use cases for **Node Query Cache**, **Shard Request Cache**, and **Field Data Cache**, and how to tune them for specific workloads (e.g., Logging vs. E-commerce).
    **掌握快取分層：** 解釋 **Node Query Cache**、**Shard Request Cache** 與 **Field Data Cache** 的具體使用場景，以及如何針對特定工作負載（如日誌分析 vs. 電商搜尋）進行調優。
3.  **Diagnose with Profile API:** Use the Profile API to dissect slow queries, identifying bottlenecks in Lucene execution phases (rewrite, build_scorer, next_doc).
    **使用 Profile API 診斷：** 使用 Profile API 解剖慢查詢，識別 Lucene 執行階段（rewrite, build_scorer, next_doc）中的瓶頸。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Query Context vs. Filter Context
### 2.1 查詢上下文 vs. 過濾上下文

**The Mental Model:**
Think of **Query Context** as asking "How well does this document match?" (Result is a float score: `_score`).
Think of **Filter Context** as asking "Does this document match?" (Result is a boolean: `Yes/No`).
**心智模型：**
將 **Query Context** 想像成問「這份文件匹配程度如何？」（結果是浮點數分數：`_score`）。
將 **Filter Context** 想像成問「這份文件是否匹配？」（結果是布林值：`Yes/No`）。

*   **Query Context:** Used in `query`, `bool.must`, `bool.should`. It calculates relevance (TF/IDF, BM25). It is **not cached** by default.
    **Query Context：** 用於 `query`、`bool.must`、`bool.should`。它計算相關性（TF/IDF, BM25）。預設**不進行快取**。
*   **Filter Context:** Used in `bool.filter`, `bool.must_not`, `constant_score`. It skips scoring. It produces a "bitset" (a sequence of 0s and 1s) representing matching documents, which is highly cacheable.
    **Filter Context：** 用於 `bool.filter`、`bool.must_not`、`constant_score`。它跳過算分步驟。它會產生一個代表匹配文件的「位元集（bitset）」（0 與 1 的序列），非常適合快取。

### 2.2 The Caching Hierarchy
### 2.2 快取層級結構

ElasticSearch has multiple caches. Confusing them is a common source of optimization failure.
ElasticSearch 擁有多種快取。混淆它們是優化失敗的常見原因。

| Cache Type | Scope | Content | Best For | Invalidation |
| :--- | :--- | :--- | :--- | :--- |
| **Node Query Cache** | Node Level (Shared by shards) | Bitsets (Segment level) for Filter Context. | Reusable filters (e.g., `status:active`, `category:electronics`). | Segment merge or update. |
| **Shard Request Cache** | Shard Level | Full JSON response (local to shard). | Aggregations on static indices (e.g., Dashboards, Time-series). | **Any** refresh (new document indexed). |
| **Field Data Cache** | Node Level | Uninverted index data (Text fields). | Sorting/Aggregating on `text` fields (Rarely used now; prefer `doc_values`). | Memory pressure / LRU. |

| 快取類型 | 範圍 | 內容 | 適用場景 | 失效時機 |
| :--- | :--- | :--- | :--- | :--- |
| **Node Query Cache** | 節點層級（分片共享） | Filter Context 的 Bitsets（Segment 層級）。 | 可重複使用的過濾條件（如 `status:active`, `category:electronics`）。 | Segment 合併或更新時。 |
| **Shard Request Cache** | 分片層級 | 完整的 JSON 回傳結果（分片局部）。 | 靜態索引上的聚合運算（如儀表板、時間序列資料）。 | **任何** Refresh（有新文件寫入時）。 |

**Key Insight:** The **Node Query Cache** is intelligent. It doesn't cache everything; it tracks usage patterns (frequency) and only caches filters that are used repeatedly on segments with enough documents.
**關鍵洞察：** **Node Query Cache** 是有智慧的。它不會快取所有東西；它會追蹤使用模式（頻率），並且只快取那些在擁有足夠文件數的 Segment 上被重複使用的過濾條件。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 High-Traffic E-commerce Search
### 3.1 高流量電商搜尋

In an e-commerce system, users frequently filter by `brand`, `size`, `color`, and `in_stock`.
在電商系統中，使用者頻繁地根據 `brand`（品牌）、`size`（尺寸）、`color`（顏色）和 `in_stock`（庫存狀態）進行篩選。

*   **Design Choice:** These attributes are finite and repetitive. They must be placed in the `filter` clause.
    **設計決策：** 這些屬性是有限且重複的。它們必須被放置在 `filter` 子句中。
*   **Impact:** This leverages the **Node Query Cache**. Even if the user changes the search keyword (Query Context), the underlying filters (e.g., "Nike" + "Size 10") retrieve pre-computed bitsets, drastically reducing I/O.
    **影響：** 這利用了 **Node Query Cache**。即使使用者改變搜尋關鍵字（Query Context），底層的過濾條件（例如「Nike」+「Size 10」）會檢索預先計算好的 bitsets，大幅減少 I/O。

### 3.2 Analytics Dashboard (ELK Stack)
### 3.2 分析儀表板（ELK Stack）

Consider a Kibana dashboard showing "Last 7 Days Error Counts".
考慮一個顯示「過去 7 天錯誤計數」的 Kibana 儀表板。

*   **Design Choice:** If the index is strictly time-based (e.g., `logs-2023-10-01`) and older indices are read-only, the **Shard Request Cache** becomes powerful.
    **設計決策：** 如果索引是嚴格基於時間的（例如 `logs-2023-10-01`），且舊索引是唯讀的，**Shard Request Cache** 就會變得非常強大。
*   **Impact:** Since older indices do not refresh (no new writes), the aggregation result is cached at the shard level. Repeated page loads hit the cache directly, returning in milliseconds (size `0` search).
    **影響：** 由於舊索引不會 refresh（沒有新寫入），聚合結果會被快取在分片層級。重複的頁面載入會直接命中快取，並在毫秒級回傳（size 為 `0` 的搜尋）。
*   **Trade-off:** If you are actively writing to an index (e.g., today's logs), the Shard Request Cache invalidates on every refresh (default 1s), making it useless for real-time dashboards unless you increase `refresh_interval`.
    **權衡：** 如果你正頻繁寫入某個索引（例如今天的日誌），Shard Request Cache 會在每次 refresh 時失效（預設 1 秒），這使得它對即時儀表板幾乎無用，除非你增加 `refresh_interval`。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Optimizing a Slow Log Search
### 場景：優化緩慢的日誌搜尋

**Background:** A developer complains that searching for "error" logs for a specific `customer_id` within a time range is taking 2+ seconds.
**背景：** 一位開發者抱怨在特定時間範圍內搜尋某個 `customer_id` 的 "error" 日誌需要 2 秒以上。

**Naive Query (Anti-pattern):**
**天真的查詢（反模式）：**

```json
GET /logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "message": "error exception" } },
        { "term": { "customer_id": "12345" } },
        { "range": { "@timestamp": { "gte": "now-1h" } } }
      ]
    }
  }
}
```

**Problem:** Every clause is in `must`. ES calculates a score for `customer_id` and `@timestamp`, which is meaningless. It prevents caching.
**問題：** 每個子句都在 `must` 中。ES 會為 `customer_id` 和 `@timestamp` 計算分數，這毫無意義。這也阻止了快取機制。

**Optimized Query:**
**優化後的查詢：**

```json
GET /logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "message": "error exception" } } // Keep scoring for text relevance
      ],
      "filter": [
        { "term": { "customer_id": "12345" } },       // Binary Yes/No, Cacheable
        { "range": { "@timestamp": { "gte": "now-1h" } } } // Binary Yes/No
      ]
    }
  }
}
```

**Why it's better:**
1.  `customer_id` filter is likely reused across many queries. It will be cached in the **Node Query Cache**.
2.  `@timestamp` range is now a filter. While ranges involving `now` are harder to cache (since `now` moves), ES optimizes ranges efficiently in Lucene (BKD trees).
3.  Scoring is restricted only to the `message` field.

**為何更好：**
1.  `customer_id` 過濾條件很可能在多個查詢中重複使用。它將被快取在 **Node Query Cache** 中。
2.  `@timestamp` 範圍現在是一個過濾器。雖然涉及 `now` 的範圍較難快取（因為 `now` 會變動），但 ES 在 Lucene 層級（BKD trees）對範圍查詢有高效優化。
3.  算分僅限於 `message` 欄位。

### Diagnosing with Profile API
### 使用 Profile API 診斷

To prove the improvement, we use the Profile API.
為了證明效能提升，我們使用 Profile API。

```json
GET /logs/_search
{
  "profile": true,
  "query": { ... }
}
```

**Response Analysis (Simplified):**
**回應分析（簡化）：**

```json
"profile": {
  "shards": [
    {
      "searches": [
        {
          "query": [
            {
              "type": "BooleanQuery",
              "description": "message:error message:exception",
              "time_in_nanos": 15000000,
              "breakdown": {
                "score": 500000,
                "build_scorer": 12000000, 
                "next_doc": 2000000
              }
            }
          ]
        }
      ]
    }
  ]
}
```

**Key Metrics to Watch:**
**觀察重點指標：**
*   **time_in_nanos:** Total time spent.
    **time_in_nanos：** 總花費時間。
*   **build_scorer:** Time spent creating the scorer for the segment. High values here often indicate expensive queries (like heavy regex or script queries).
    **build_scorer：** 為 Segment 建立評分器所花費的時間。此處數值過高通常表示查詢代價昂貴（如繁重的 Regex 或 Script 查詢）。
*   **next_doc:** Time spent iterating to the next matching document. High values suggest the filter is not skipping documents efficiently.
    **next_doc:** 迭代至下一個匹配文件所花費的時間。數值過高暗示過濾器未能有效地跳過文件。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Caching High Cardinality Fields
### 5.1 快取高基數（High Cardinality）欄位

*   **Anti-pattern:** Filtering on a field with millions of unique values (e.g., `transaction_id`, `user_session_token`) expecting it to be cached.
    **反模式：** 對擁有數百萬個唯一值的欄位（如 `transaction_id`、`user_session_token`）進行過濾，並期望它被快取。
*   **Consequence:** The **Node Query Cache** fills up with bitsets that are rarely reused, causing cache thrashing (evicting useful filters).
    **後果：** **Node Query Cache** 被那些極少重複使用的 bitsets 填滿，導致快取抖動（Cache Thrashing），將有用的過濾器驅逐出去。
*   **Solution:** ES is smart enough not to cache these if frequency is low, but be mindful. Do not force caching on ID lookups.
    **解法：** ES 足夠聰明，若頻率低則不會快取，但仍需注意。不要強迫對 ID 查找進行快取。

### 5.2 Timestamp Ranges with `now`
### 5.2 使用 `now` 的時間戳範圍

*   **Anti-pattern:** `range: { "timestamp": { "gt": "now-1h" } }`.
    **反模式：** `range: { "timestamp": { "gt": "now-1h" } }`。
*   **Why:** `now` changes every millisecond. This prevents the query from being identical to a previous one, bypassing the cache.
    **原因：** `now` 每一毫秒都在改變。這使得查詢無法與前一次完全相同，從而繞過快取。
*   **Solution:** Round the date in your application code (e.g., to the minute) or use ES date rounding: `now-1h/m`. This allows caching for 1 minute.
    **解法：** 在應用程式代碼中對時間進行捨入（例如取至分鐘），或使用 ES 的日期捨入：`now-1h/m`。這允許快取維持 1 分鐘。

### 5.3 Deep Pagination
### 5.3 深度分頁

*   **Anti-pattern:** Using `from: 10000, size: 10`.
    **反模式：** 使用 `from: 10000, size: 10`。
*   **Why:** ES must fetch 10,010 documents from *every* shard, sort them in memory, and discard 10,000. This kills CPU and memory.
    **原因：** ES 必須從*每個*分片獲取 10,010 份文件，在記憶體中排序，然後丟棄 10,000 份。這會耗盡 CPU 和記憶體。
*   **Solution:** Use `search_after` for infinite scroll or deep iteration.
    **解法：** 使用 `search_after` 來實作無限捲動或深度迭代。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### 6.1 Design Question: Optimizing Dashboard Latency
### 6.1 設計題：優化儀表板延遲

**Question:** "We have a Kibana dashboard that queries the last 24 hours of logs. It's slow and causes high load on the cluster every time users refresh. How do you optimize this?"
**問題：** 「我們有一個查詢過去 24 小時日誌的 Kibana 儀表板。它很慢，且每次使用者重新整理都會對叢集造成高負載。你會如何優化？」

**Key Points for a High-Score Answer:**
**高分回答要點：**
1.  **Filter Context:** Ensure all non-text queries are filters.
    **Filter Context：** 確保所有非文字查詢都是過濾器。
2.  **Date Rounding:** Suggest changing `now-24h` to `now-24h/m` to enable Node Query Caching for the range filter.
    **日期捨入：** 建議將 `now-24h` 改為 `now-24h/m`，以啟用範圍過濾器的 Node Query Cache。
3.  **Shard Request Cache:** Explain that if the index is actively receiving data, `refresh_interval` limits the effectiveness of the Request Cache. Suggest increasing `refresh_interval` (e.g., from 1s to 30s) if real-time strictness is negotiable, allowing the Request Cache to serve hits for 30s.
    **Shard Request Cache：** 解釋若索引正頻繁接收資料，`refresh_interval` 會限制 Request Cache 的效能。建議增加 `refresh_interval`（例如從 1s 增至 30s），若即時性要求可協商，這能讓 Request Cache 在 30 秒內提供服務。

### 6.2 Technical Deep Dive: Filter Internals
### 6.2 技術深究：Filter 內部機制

**Question:** "Explain how ElasticSearch caches a filter. Is it cached per query or per index?"
**問題：** 「解釋 ElasticSearch 如何快取一個 Filter。它是針對每個查詢快取，還是針對每個索引？」

**Key Points:**
**要點：**
*   It's cached per **Segment**, not per index or query.
    它是針對 **Segment** 進行快取，而非索引或查詢。
*   It uses a **Roaring Bitmap** (or bitset) to represent matches efficiently.
    它使用 **Roaring Bitmap**（或 bitset）來高效表示匹配結果。
*   It is only cached if the segment has enough documents (usually > 10k or 3% of total) and the filter is used frequently (history tracking).
    只有當 Segment 擁有足夠文件（通常 > 10k 或佔總數 3%）且該過濾器被頻繁使用（歷史追蹤）時，才會被快取。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (Memory Anchors)
### 關鍵記憶點（記憶錨點）

1.  **Filter vs. Query:** Always use `filter` for binary (yes/no) logic; use `query` only for relevance scoring.
    **Filter vs. Query：** 二元（是/否）邏輯一律使用 `filter`；僅在需要相關性評分時使用 `query`。
2.  **Node Query Cache:** Caches bitsets for filters on a per-segment basis. Great for repetitive parameters (Category, Status).
    **Node Query Cache：** 針對每個 Segment 快取過濾器的 bitsets。極適合重複性參數（類別、狀態）。
3.  **Shard Request Cache:** Caches the full JSON result. Invalidated on **any** refresh. Great for static indices or low-refresh scenarios.
    **Shard Request Cache：** 快取完整的 JSON 結果。**任何** refresh 都會使其失效。極適合靜態索引或低更新頻率場景。
4.  **Date Rounding:** Use `/m` or `/h` with `now` to make time ranges cacheable.
    **日期捨入：** 在 `now` 使用 `/m` 或 `/h` 讓時間範圍可被快取。
5.  **Profile API:** The "Explain Plan" of ES. Look at `time_in_nanos` and `breakdown` to find the culprit.
    **Profile API：** ES 的「執行計畫解釋」。查看 `time_in_nanos` 與 `breakdown` 來找出罪魁禍首。

### Next Steps
### 後續延伸

*   **Practice:** Take a slow query from your production logs and run it with `profile: true`. Identify if the slowness comes from `build_scorer` (complex query) or `next_doc` (poor filtering).
    **實作：** 從你的 Production 日誌中找出一個慢查詢，並加上 `profile: true` 執行。辨識慢的原因是來自 `build_scorer`（複雜查詢）還是 `next_doc`（過濾效果差）。
*   **Next Chapter:** We will move from reading to writing. **Chapter 06: Indexing Performance & Capacity Planning** will cover how to tune bulk indexing, refresh intervals, and shard sizing for massive ingestion.
    **下一章：** 我們將從讀取轉向寫入。**第六章：索引效能與容量規劃** 將涵蓋如何針對大量資料寫入調優 Bulk Indexing、Refresh Intervals 以及 Shard Sizing。