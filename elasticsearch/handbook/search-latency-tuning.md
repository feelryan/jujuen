# 搜尋延遲調優與 Slow Log 分析 / Search Latency Tuning & Slow Log Analysis

## Mental model｜心智模型

在進行 ElasticSearch (ES) 效能調優時，請建立以下兩個核心觀念：

### 1. "Disk is Lava" (磁碟是岩漿)
ES 的極致效能來自於 **Filesystem Cache (OS Cache)**。Lucene 的索引結構（Segments）是不可變的（Immutable），這對作業系統的快取機制非常友善。
*   **理想狀態**：你的 "Hot Data" 大小 < 機器剩餘記憶體（Heap 以外的 RAM）。此時查詢幾乎是在記憶體中完成，速度極快。
*   **瓶頸狀態**：當資料量遠大於 RAM，OS 必須不斷進行 Page Fault 從磁碟讀取資料。磁碟 I/O 通常是搜尋延遲的最大殺手。

### 2. Scatter-Gather Effect (分散-聚合效應)
ES 的搜尋是分散式的。當你對一個擁有 5 個分片（Shards）的索引進行搜尋時，協調節點（Coordinating Node）必須等待 **所有** 5 個分片都回傳結果後，才能進行排序與合併。
*   **木桶理論**：查詢的總延遲取決於 **最慢** 的那個分片。
*   **推論**：分片過多（Oversharding）會導致協調開銷增加；分片過大則導致單一執行緒處理過久。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Profile API 分析流程 (The Profiling Pattern)
不要猜測為什麼慢，用數據說話。`Profile API` 是你的顯微鏡。

*   **使用方式**：在查詢 Body 中加入 `"profile": true`。
*   **關注點**：
    *   **Query Breakdown**：查看 `create_weight`, `build_scorer`, `next_doc`, `advance` 等階段的耗時。
    *   **Rewrite Time**：如果使用了大量的 Wildcard 或 Prefix 查詢，Rewrite 可能會消耗大量時間。
    *   **Unoptimized Queries**：檢查是否有查詢無法利用 Skip List 或 BKD Tree，導致全表掃描。

### 2. Routing 優化 (Custom Routing)
如果你的業務場景通常是「查詢特定使用者的資料」，請務必使用 `routing`。

*   **Default**：`hash(_id) % num_shards` -> 查詢會廣播到所有分片。
*   **Optimization**：寫入與查詢時指定 `routing=user_id`。
*   **Benefit**：查詢只會命中 1 個分片，大幅減少 CPU 與執行緒開銷，提升併發能力。

### 3. Force Merge 策略 (Segment Optimization)
針對 **唯讀索引（Read-only Indices）**（如日誌、時序資料的舊索引），執行 Force Merge 是提升讀取效能的特效藥。

*   **原理**：刪除的文檔（Deleted docs）在 Merge 前仍佔用空間並參與查詢過濾。Force Merge 可以物理刪除這些文檔並將多個 Segments 合併為 1 個。
*   **操作**：`POST /my-index/_forcemerge?max_num_segments=1`
*   **時機**：在索引不再寫入後（Rollover 之後）立即執行。

### 4. 提升 Filesystem Cache 命中率
*   **欄位縮減**：在 `_source` 中排除不需回傳的大欄位，或設定 `store: false`。
*   **Doc Values Only**：如果某個欄位只用於聚合（Aggregation）不需搜尋，可以關閉 `index: false`，節省倒排索引空間。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 Wildcard 與 Regex (The Leading Wildcard Trap)
*   **Bad Pattern**：`*keyword` 或 `*keyword*`。
*   **Why**：這會導致 ES 必須掃描 Term Dictionary 中的所有詞項，極度消耗 CPU。
*   **Fix**：使用 `ngram` tokenizer 或 `wildcard` 專用欄位類型。

### 2. 深分頁陷阱 (Deep Pagination)
*   **Bad Pattern**：`from: 10000, size: 10`。
*   **Why**：每個分片必須取出前 10010 筆資料，協調節點必須排序 `shards * 10010` 筆資料，最後只丟棄前 10000 筆。記憶體與 CPU 殺手。
*   **Fix**：使用 `search_after` API。

### 3. 腳本查詢 (Script Query)
*   **Bad Pattern**：在 Filter 中使用 Painless script 進行複雜運算。
*   **Why**：Script 無法利用倒排索引與 Cache，必須對每個文檔逐一計算。
*   **Fix**：在 Indexing 階段預先計算好值並存入欄位（Denormalization）。

### 4. 忽略 Slow Log 的警告
*   **Pitfall**：只看監控儀表板的平均延遲，忽略了 P99 延遲與 Slow Log。
*   **Why**：少數的慢查詢（如惡意攻擊或錯誤用法）可能拖垮整個 Thread Pool，導致正常查詢被 Reject。

---

## Checklists & workflows｜檢查清單與流程

### Performance Tuning Workflow (調優工作流)

1.  **Identify (識別)**：透過 Kibana Monitoring 或 Slow Log 找出慢查詢語句。
2.  **Profile (剖析)**：使用 `Profile API` 拆解查詢各階段耗時。
3.  **Simplify (簡化)**：移除不必要的查詢條件，隔離出問題的子查詢。
4.  **Optimize (優化)**：調整 Mapping、重寫 Query 或調整硬體資源。

### Optimization Checklist (優化檢核表)

- [ ] **Slow Log 設定**：是否已開啟 Slow Log？(建議：`query_warn_threshold: 500ms`, `fetch_warn_threshold: 200ms`)
- [ ] **Swap 設定**：伺服器的 Swap 是否已完全關閉？(`bootstrap.memory_lock: true`)
- [ ] **Heap Size**：Heap 是否設定為 RAM 的 50%（且不超過 32GB）？留一半給 Filesystem Cache。
- [ ] **Force Merge**：舊的時序索引是否已 Merge 為 `max_num_segments=1`？
- [ ] **Stopwords**：是否過濾了高頻無意義詞（Stopwords）以減少倒排索引大小？
- [ ] **Keyword vs Text**：不需要全文檢索的欄位是否設為 `keyword`？
- [ ] **Date Rounding**：Range query 是否使用了 `now/m` 而非 `now` 以利用 Query Cache？

---

## Real-world examples｜實戰案例

### Case 1: The "Slow Log" Analysis
**情境**：電商網站搜尋突然變慢，Slow Log 顯示大量查詢超過 1 秒。

**Log 範例**：
```json
{
  "type": "index_search_slowlog",
  "timestamp": "2023-10-27T10:00:00.123Z",
  "level": "WARN",
  "component": "i.s.s.query",
  "cluster.name": "prod-es",
  "node.name": "node-1",
  "index": "products",
  "took": "1.2s",
  "took_millis": 1200,
  "source": "{\"query\":{\"bool\":{\"filter\":[{\"script\":{\"script\":\"doc['price'].value * doc['discount'].value > 100\"}}]}}}"
}
```

**分析與解決**：
1.  **發現問題**：Log 顯示使用了 `script` 進行價格計算過濾。這是全表掃描操作。
2.  **解決方案**：
    *   修改 Mapping，新增一個 `final_price` 欄位。
    *   在寫入時計算 `price * discount` 並存入 `final_price`。
    *   查詢改為 `range` query: `{"range": {"final_price": {"gt": 100}}}`。
3.  **結果**：查詢時間從 1.2s 降至 10ms。

### Case 2: Routing for Multi-tenant SaaS
**情境**：一個 SaaS 平台為 5000 家公司提供日誌搜尋，所有資料存在同一個大 Index，查詢延遲隨著資料量線性增長。

**優化前**：
*   Query: `GET /logs/_search?q=company_id:123 AND level:ERROR`
*   ES 行為：掃描所有 Shards，過濾出 `company_id:123`。

**優化後**：
*   Indexing: `PUT /logs/_doc/1?routing=123`
*   Query: `GET /logs/_search?routing=123&q=level:ERROR`
*   ES 行為：直接定位到該公司資料所在的單一 Shard。

### Case 3: Profile API Debugging
**情境**：一個看似簡單的 `Term Query` 卻異常緩慢。

**Profile API Output (Simplified)**:
```json
"profile": {
  "shards": [
    {
      "searches": [
        {
          "query": [
            {
              "type": "TermQuery",
              "description": "status:active",
              "time_in_nanos": 500000,
              "breakdown": {
                 "score": 0,
                 "build_scorer_count": 0,
                 "match_count": 0,
                 "create_weight": 1000,
                 "next_doc": 0,
                 "advance": 0
              }
            }
          ]
        }
      ]
    }
  ]
}
```
**分析**：如果 `time_in_nanos` 很高但 `match_count` 很低，且系統 I/O wait 很高，這通常意味著 **Cold Cache**。資料不在記憶體中，ES 正在等待磁碟讀取。
**對策**：增加節點記憶體，或使用 `index.store.preload` 預熱關鍵檔案。