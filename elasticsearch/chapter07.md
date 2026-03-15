# Chapter 07: Aggregations and Analytics
# 第 7 章：聚合分析與大數據應用

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

ElasticSearch (ES) is not just a search engine; it is a powerful distributed analytics engine. However, unlike simple search queries, aggregations can be extremely memory-intensive. For a Senior Engineer, the challenge is not writing the aggregation DSL, but understanding how it executes across shards and avoiding cluster instability.
ElasticSearch (ES) 不僅僅是搜尋引擎，它也是強大的分散式分析引擎。然而，與單純的搜尋查詢不同，聚合（Aggregations）操作極度消耗記憶體。對於資深工程師而言，挑戰不在於撰寫聚合 DSL，而在於理解它如何在分片（Shards）間執行，並避免造成叢集不穩定。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Analyze Memory Overhead**: Understand the role of **Doc Values**, **Global Ordinals**, and **Fielddata**, and how they impact heap usage during aggregations.
    **分析記憶體開銷**：理解 **Doc Values**、**Global Ordinals** 與 **Fielddata** 的角色，以及它們如何在聚合過程中影響 Heap 使用量。
2.  **Prevent OOM**: Identify "Exploding Buckets" scenarios and apply strategies like `breadth_first` collection mode and the `composite` aggregation to handle high cardinality.
    **預防 OOM**：識別「Bucket 爆炸」場景，並應用 `breadth_first` 收集模式與 `composite` 聚合來處理高基數（High Cardinality）資料。
3.  **Evaluate System Boundaries**: Determine when to use ES for analytics versus offloading to specialized OLAP databases (like ClickHouse or Snowflake).
    **評估系統邊界**：判斷何時該使用 ES 進行分析，何時該將負載卸載至專門的 OLAP 資料庫（如 ClickHouse 或 Snowflake）。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The "Map-Reduce" of Search
### 搜尋引擎中的 "Map-Reduce"

Think of ES Aggregations as a specialized, real-time Map-Reduce framework.
請將 ES 聚合視為一種專用的、即時的 Map-Reduce 框架。

*   **Map Phase (Shard Level)**: Each shard executes the query, filters documents, and builds local aggregation buckets (e.g., counting terms, summing values).
    **Map 階段（分片層級）**：每個分片執行查詢、過濾文件，並建立局部的聚合 Bucket（例如：計算詞頻、數值加總）。
*   **Reduce Phase (Coordinating Node)**: The node receiving the request gathers partial results from all shards, merges the buckets, performs final calculations (like averages or pipeline aggs), and returns the response.
    **Reduce 階段（協調節點）**：接收請求的節點收集所有分片的局部結果，合併 Bucket，執行最終計算（如平均值或 Pipeline 聚合），並回傳回應。

### Buckets vs. Metrics vs. Pipelines
### Bucket、Metric 與 Pipeline

1.  **Bucket Aggregations**: Create sets of documents (like SQL `GROUP BY`). Examples: `terms`, `date_histogram`, `range`.
    **Bucket 聚合**：建立文件集合（類似 SQL 的 `GROUP BY`）。例如：`terms`、`date_histogram`、`range`。
2.  **Metric Aggregations**: Calculate values from documents in a bucket (like SQL `COUNT`, `SUM`, `AVG`). Examples: `stats`, `percentiles`, `cardinality`.
    **Metric 聚合**：針對 Bucket 中的文件計算數值（類似 SQL 的 `COUNT`、`SUM`、`AVG`）。例如：`stats`、`percentiles`、`cardinality`。
3.  **Pipeline Aggregations**: Perform calculations on the output of *other* aggregations (e.g., moving average, derivative).
    **Pipeline 聚合**：針對*其他*聚合的輸出結果進行計算（例如：移動平均、導數）。

### Data Structures: Doc Values vs. Fielddata
### 資料結構：Doc Values 與 Fielddata

This is the most critical concept for performance.
這是效能最關鍵的概念。

*   **Inverted Index**: Maps Terms → Doc IDs. Great for search, terrible for aggregations (requires scanning the whole index to find values for a doc).
    **倒排索引**：映射 Terms → Doc IDs。極適合搜尋，但對聚合極差（需要掃描整個索引才能找到某文件的值）。
*   **Doc Values**: Maps Doc IDs → Values. Columnar storage on disk, loaded into OS cache. Used by most fields (keyword, numeric, date) for sorting and aggregations. **Fast and memory-efficient.**
    **Doc Values**：映射 Doc IDs → Values。磁碟上的欄式儲存（Columnar Storage），會載入 OS cache。大多數欄位（keyword, numeric, date）用於排序與聚合。**快速且節省記憶體**。
*   **Fielddata**: An in-memory structure created on the fly for `text` fields (which don't have Doc Values by default). **Extremely expensive and a common cause of OOM.**
    **Fielddata**：針對 `text` 欄位（預設沒有 Doc Values）動態建立的記憶體內結構。**極度昂貴，是 OOM 的常見元兇。**

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Typical Architecture Role
### 典型架構角色

In a large-scale system, ES often serves as the **"Hot/Warm Analytics Layer"**:
在大型系統中，ES 通常擔任 **「熱/溫資料分析層」**：

*   **User-Facing Dashboards**: Providing near real-time stats (e.g., "Sales in the last hour").
    **使用者儀表板**：提供近即時統計（例如：「過去一小時的銷售額」）。
*   **Observability (Logs/Metrics)**: The backbone of the ELK/EFK stack.
    **可觀測性（Logs/Metrics）**：ELK/EFK stack 的骨幹。
*   **Search Relevance Tuning**: Aggregating user clicks to re-rank search results.
    **搜尋關聯性調校**：聚合使用者點擊行為來重新排序搜尋結果。

### Scalability & Trade-offs
### 可擴充性與權衡

When designing for analytics in ES, consider these trade-offs:
在 ES 中設計分析功能時，需考慮以下權衡：

1.  **Precision vs. Speed (Approximation)**:
    **精確度 vs. 速度（近似演算法）**：
    Aggregations like `cardinality` (distinct count) and `percentiles` use probabilistic algorithms (HyperLogLog++, T-Digest). They are fast and use fixed memory but are not 100% accurate on large datasets.
    像 `cardinality`（去重計數）和 `percentiles`（百分位數）這類聚合使用的是機率演算法（HyperLogLog++, T-Digest）。它們速度快且記憶體佔用固定，但在大數據集上並非 100% 精確。

2.  **Deep Pagination Problem**:
    **深度分頁問題**：
    Just as you shouldn't use `from/size` for deep search paging, you shouldn't use standard `terms` aggregation to retrieve "the top 10,000 categories". Use **Composite Aggregation** for iterating over large buckets.
    就像你不應使用 `from/size` 進行深度搜尋分頁一樣，你不應使用標準的 `terms` 聚合來檢索「前 10,000 個分類」。應使用 **Composite Aggregation** 來迭代大量的 Bucket。

3.  **Coordinator Node Bottleneck**:
    **協調節點瓶頸**：
    If you request a massive aggregation (e.g., nested buckets with high cardinality), the coordinating node must hold the merged result in memory. This can crash the node even if data nodes are fine.
    如果你請求一個巨大的聚合（例如：高基數的巢狀 Bucket），協調節點必須將合併後的結果保留在記憶體中。即使資料節點運作正常，這也可能導致協調節點崩潰。

---

## 4. Walkthrough: Handling High Cardinality Aggregations
## 4. 逐步示例：處理高基數聚合

### Scenario
### 情境

You are building a fraud detection dashboard. You need to find the "Top 100 User IPs" that have accessed the most distinct endpoints in the last hour. The index has 500 million documents.
你正在建構一個詐欺偵測儀表板。你需要找出過去一小時內存取最多不同端點（Endpoints）的「前 100 個使用者 IP」。該索引有 5 億筆文件。

### Naive Approach (The Danger Zone)
### 直覺做法（危險區）

```json
GET /access_logs/_search
{
  "size": 0,
  "aggs": {
    "top_ips": {
      "terms": {
        "field": "client_ip",
        "size": 100
      },
      "aggs": {
        "distinct_endpoints": {
          "cardinality": {
            "field": "endpoint"
          }
        }
      }
    }
  }
}
```

**Why this might fail:**
**為何這可能會失敗：**
If `client_ip` has high cardinality (millions of unique IPs), ES builds buckets for *all* IPs on each shard before pruning them to the top 100. This creates massive memory pressure.
如果 `client_ip` 具有高基數（數百萬個唯一 IP），ES 會在每個分片上為 *所有* IP 建立 Bucket，然後才修剪至前 100 個。這會產生巨大的記憶體壓力。

### Refined Approach: Breadth-First & Filtering
### 優化做法：廣度優先與過濾

To optimize, we change the collection mode and perhaps filter the data first.
為了優化，我們改變收集模式，並可能先過濾資料。

```json
GET /access_logs/_search
{
  "size": 0,
  "query": {
    "range": {
      "timestamp": { "gte": "now-1h" }
    }
  },
  "aggs": {
    "top_ips": {
      "terms": {
        "field": "client_ip",
        "size": 100,
        "collect_mode": "breadth_first",  // Optimization
        "execution_hint": "map"           // Optional hint
      },
      "aggs": {
        "distinct_endpoints": {
          "cardinality": {
            "field": "endpoint"
          }
        }
      }
    }
  }
}
```

**Key Changes & Analysis:**
**關鍵變更與分析：**

1.  **`collect_mode: "breadth_first"`**:
    *   **Default (`depth_first`)**: Builds the full tree of buckets (IPs + sub-aggs) before pruning.
        **預設 (`depth_first`)**：在修剪之前建立完整的 Bucket 樹（IP + 子聚合）。
    *   **Breadth-First**: Calculates the top-level buckets (IPs) first, prunes them to the top N, and *only then* executes the sub-aggregation (`cardinality`) for those top N buckets. This drastically reduces memory usage for high-cardinality nested aggs.
        **廣度優先**：先計算頂層 Bucket（IP），將其修剪至前 N 個，*然後才*針對這前 N 個 Bucket 執行子聚合（`cardinality`）。這大幅降低了高基數巢狀聚合的記憶體使用。

2.  **Execution Hint**:
    *   `map` uses map-based aggregation instead of global ordinals. Sometimes faster for very high cardinality fields where global ordinals building is too slow.
        `map` 使用基於 map 的聚合而非 global ordinals。在 global ordinals 建構過慢的極高基數欄位場景中，有時會更快。

### Alternative: Composite Aggregation (For Exporting)
### 替代方案：Composite Aggregation（用於匯出）

If you need *all* IPs, not just top 100, standard `terms` will fail or return inaccurate counts (due to shard-level approximation). Use `composite`:
如果你需要 *所有* IP，而不僅是前 100 名，標準的 `terms` 會失敗或回傳不準確的計數（因為分片層級的近似計算）。請使用 `composite`：

```json
GET /access_logs/_search
{
  "size": 0,
  "aggs": {
    "all_ips": {
      "composite": {
        "size": 1000,
        "sources": [
          { "ip": { "terms": { "field": "client_ip" } } }
        ]
      }
    }
  }
}
```
*Use the `after_key` returned in the response to fetch the next page.*
*使用回應中回傳的 `after_key` 來獲取下一頁。*

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. Enabling Fielddata on Text Fields
### 1. 在 Text 欄位上啟用 Fielddata

*   **Anti-pattern**: Setting `"fielddata": true` in mapping to allow aggregation on a `text` field (e.g., product description).
    **反模式**：在 Mapping 中設定 `"fielddata": true` 以允許對 `text` 欄位（如產品描述）進行聚合。
*   **Why it's bad**: It loads the entire inverted index into heap memory. It can easily trigger OOM and crash the node.
    **為何不好**：這會將整個倒排索引載入 Heap 記憶體。極易觸發 OOM 並導致節點崩潰。
*   **Solution**: Use a `keyword` sub-field (multi-field) for aggregations.
    **解法**：使用 `keyword` 子欄位（Multi-field）進行聚合。

### 2. Ignoring `doc_count_error_upper_bound`
### 2. 忽略 `doc_count_error_upper_bound`

*   **Anti-pattern**: Assuming `terms` aggregation counts are 100% accurate in a distributed system.
    **反模式**：假設分散式系統中的 `terms` 聚合計數是 100% 準確的。
*   **Why it's bad**: Shards return their top N terms. If a term is low-frequency in one shard (not in top N) but high in others, it might be undercounted or missed entirely in the final reduction.
    **為何不好**：分片回傳它們的前 N 個 Terms。如果某個 Term 在某分片中頻率低（未進入前 N 名），但在其他分片很高，它在最終合併時可能會被低估或完全遺漏。
*   **Solution**: Check `doc_count_error_upper_bound` in the response. Increase `shard_size` to improve accuracy at the cost of performance.
    **解法**：檢查回應中的 `doc_count_error_upper_bound`。增加 `shard_size` 以犧牲效能為代價來提高準確度。

### 3. Deeply Nested Aggregations
### 3. 過度巢狀的聚合

*   **Anti-pattern**: Nesting 3+ levels of bucket aggregations (e.g., Country -> City -> User -> Date).
    **反模式**：巢狀 3 層以上的 Bucket 聚合（例如：國家 -> 城市 -> 使用者 -> 日期）。
*   **Why it's bad**: Combinatorial explosion. $10 \times 10 \times 100 \times 50$ buckets = 500,000 buckets created in memory.
    **為何不好**：組合爆炸。$10 \times 10 \times 100 \times 50$ 個 Bucket = 在記憶體中建立 500,000 個 Bucket。
*   **Solution**: Restructure data or perform multiple shallower queries.
    **解法**：重構資料結構或執行多次較淺層的查詢。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How does ElasticSearch handle aggregations on high-cardinality fields, and what are the risks?
### Q1: ElasticSearch 如何處理高基數欄位的聚合，有哪些風險？

*   **Key Points**:
    *   Explain **Global Ordinals**: ES builds a mapping of Term $\leftrightarrow$ Global Ordinal to speed up lookups. Building this on-the-fly for high cardinality fields causes latency spikes.
    *   **Memory Pressure**: Mention the "Exploding Buckets" problem.
    *   **Solutions**: `composite` aggregation for pagination, `breadth_first` mode, or increasing `refresh_interval` to avoid rebuilding global ordinals too often.

### Q2: When would you choose ElasticSearch aggregations over a dedicated OLAP DB like ClickHouse?
### Q2: 你何時會選擇 ElasticSearch 聚合，而非專用的 OLAP 資料庫（如 ClickHouse）？

*   **Key Points**:
    *   **ES Wins**: When you need **Search + Analytics** combined (e.g., "Show me analytics for documents containing this specific phrase"). When the dataset is moderate or unstructured (JSON).
    *   **ClickHouse Wins**: Pure structured data analytics, massive scale (PB level), complex SQL joins required, or when cost/resource efficiency is the priority (columnar compression is usually better in OLAP DBs).

### Q3: Explain the difference between `cardinality` aggregation and a precise distinct count.
### Q3: 請解釋 `cardinality` 聚合與精確去重計數（Distinct Count）的差異。

*   **Key Points**:
    *   `cardinality` uses **HyperLogLog++**. It trades accuracy for memory efficiency (hashes values into registers).
    *   Precise counts require storing all unique values in a Set, which scales linearly with unique count (O(N) memory), whereas HLL++ is effectively O(1) memory (configurable precision threshold).
    *   In distributed systems, precise distinct counts are prohibitively expensive.

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Doc Values are King**: Ensure aggregations run on fields with Doc Values (keyword, numeric), not analyzed text.
2.  **Memory Awareness**: Be wary of high cardinality fields. Use `breadth_first` for nested aggs and `composite` for large result sets.
3.  **Approximation**: Understand that `terms` counts and `cardinality` are approximate in a distributed environment. Tune `shard_size` and precision thresholds accordingly.
4.  **Circuit Breakers**: ES has circuit breakers (e.g., `indices.breaker.request.limit`) to prevent OOM. Monitor these metrics.
5.  **Global Ordinals**: Understand their cost on refresh and query time for high-cardinality fields.

### Next Steps
### 後續延伸

*   **Chapter 08: Cluster Scaling & Tuning**: Now that you know how to stress the cluster with aggregations, learn how to scale the cluster (Shard allocation, Hot/Warm architecture) to handle the load.
    **第 8 章：叢集擴展與調校**：既然你已經知道如何用聚合給叢集施壓，接下來學習如何擴展叢集（分片配置、熱/溫架構）來承載這些負載。
*   **Action Item**: Review your current slow aggregation queries. Check if any are running on `text` fields or if `breadth_first` could optimize them.
    **行動項目**：檢視你目前緩慢的聚合查詢。檢查是否有任何查詢運行在 `text` 欄位上，或是否能透過 `breadth_first` 進行優化。