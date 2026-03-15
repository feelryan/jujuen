# 常見陷阱與反模式 / Common Pitfalls & Anti-patterns

在 Elasticsearch (ES) 的使用旅程中，最嚴重的效能問題往往源自於將其視為傳統關聯式資料庫 (RDBMS) 的錯誤心智模型。本章節將盤點那些「初學者必踩」以及「系統規模化後才浮現」的架構陷阱，並提供修正方案。

---

## Mental model｜心智模型

### 1. 搜尋引擎非關聯式資料庫 (Search Engine != RDBMS)
Elasticsearch 的核心是 **Inverted Index (倒排索引)**，它是為了「讀取與搜尋」極致優化的，而非為了「寫入與關聯」設計。
- **RDBMS**: 像是一個井然有序的檔案櫃，擅長精確更新、交易一致性 (ACID) 與節省空間 (Normalization)。
- **Elasticsearch**: 像是一本書後的「索引頁」，擅長快速找到關鍵字出現的位置，但更新成本高（Segment Merge），且空間換取時間 (Denormalization)。

### 2. 分散式代價 (Distributed Cost)
ES 是天生的分散式系統。當你發出一個查詢時，這個請求通常需要被廣播到所有相關的分片 (Shards)，然後在協調節點 (Coordinating Node) 進行彙總 (Scatter-Gather)。
- **Anti-pattern 思維**: 認為查詢成本隨資料量線性增加。
- **Correct Model**: 查詢成本與「分片數量」及「需要彙總的資料量 (Deep Pagination)」高度相關。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 分頁策略：捨棄 `from/size`，擁抱 `search_after`
針對深度分頁 (Deep Pagination)，不要使用 SQL 思維的 Offset/Limit。
- **Pattern**: 使用 **`search_after`** 進行游標式分頁 (Cursor-based pagination)。
- **Why**: `from: 10000, size: 10` 意味著每個分片都要排序前 10,010 筆資料，傳回給協調節點後再重新排序拋棄前 10,000 筆。這會耗盡 CPU 與記憶體。

### 2. 分片管理：生命週期管理 (ILM)
不要手動建立每日索引 (e.g., `logs-2023-10-01`) 卻不管理它們的大小。
- **Pattern**: 使用 **Index Lifecycle Management (ILM)** 搭配 **Rollover API**。
- **Best Practice**: 讓分片大小決定何時滾動新索引，而非時間。目標是讓每個分片保持在 **10GB ~ 50GB** 之間。

### 3. 資料源頭：ES 是「視圖」而非「真相」
- **Pattern**: **Source of Truth (SoT)** 應保留在 RDBMS (Postgres/MySQL) 或 Event Log (Kafka) 中。ES 僅作為「唯讀的搜尋視圖」。
- **Why**: ES 在網路分區或節點崩潰時可能會發生資料遺失或 Split-brain，且缺乏跨文件的交易機制。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Deep Pagination" Trap (深度分頁陷阱)
- **Anti-pattern**: 允許使用者跳頁到第 10,000 頁，或使用 `from` + `size` 匯出大量資料。
- **Consequence**: `OOM (Out of Memory)` 錯誤，集群回應變慢甚至卡死。
- **Fix**:
  - 前端 UI 改為 "Load More" (無限捲動)。
  - 若需全量匯出資料，使用 **Scroll API** (但在 ES 7+ 建議使用 Point in Time + `search_after`)。

### 2. The "Oversharding" Problem (分片過多)
- **Anti-pattern**: 每個索引只有幾百 MB，卻設定了 5 個主分片 (Primary Shards)；或者隨著時間累積了數萬個小索引。
- **Consequence**: 每個分片都會消耗 Heap Memory 來維護 Lucene 的內部結構。過多小分片會導致 Cluster State 巨大，Master 節點不堪重負，且搜尋延遲增加。
- **Fix**: 使用 `_shrink` API 合併索引，並調整 Template 設定 `number_of_shards: 1` 給小資料量的索引。

### 3. Mapping Explosion (映射爆炸)
- **Anti-pattern**: 允許完全的 Dynamic Mapping，並寫入具有隨機 Key 的 JSON 物件 (例如將 HTTP Headers 或 User Tags 直接展平寫入)。
- **Consequence**: `Limit of total fields [1000] has been exceeded`。過多的欄位會導致 Cluster State 更新極慢，甚至讓集群崩潰。
- **Fix**: 設定 `dynamic: false` 或 `strict`，對於不可預測的欄位使用 `flattened` 數據類型。

### 4. Leading Wildcard Queries (前綴萬用字元)
- **Anti-pattern**: 使用 `*keyword` (例如 `*123`) 進行搜尋。
- **Consequence**: 這會強制 ES 掃描倒排索引中的**每一個** Term，效能極差。
- **Fix**: 使用 `ngram` tokenizer 或 `reverse` token filter 在索引階段處理，將「搜尋時間成本」轉移到「索引時間與空間成本」。

### 5. ES as Primary Storage (將 ES 當作主資料庫)
- **Anti-pattern**: 業務邏輯直接讀寫 ES，沒有其他資料備份。
- **Consequence**: 當 Mapping 需要變更（Breaking Change）時，無法重建索引 (Reindex)；資料損壞時無法復原。

---

## Checklists & workflows｜檢查清單與流程

在將應用程式推向生產環境前，請執行以下檢查：

### Architecture & Schema Check
- [ ] **Source of Truth**: 確認 ES 資料可從其他持久化儲存（RDBMS/S3/Kafka）完全重建。
- [ ] **Mapping Settings**: 是否已將 `dynamic` 設為 `false` 或 `strict`？是否已檢查欄位總數預估不會超過 1000？
- [ ] **Sharding Strategy**: 預估資料總量，規劃分片數，確保單一分片大小在 10GB-50GB 區間。
- [ ] **ID Generation**: 是否使用自定義 ID (如 DB Primary Key) 以便於去重 (Idempotency)？還是依賴 ES 自動生成 ID (寫入較快但無法防重)？

### Query Performance Check
- [ ] **Pagination**: 檢查程式碼中是否有 `from` 超過 10,000 的可能性？是否已實作 `search_after`？
- [ ] **Wildcards**: 確保沒有 `*value` 形式的查詢。
- [ ] **Aggregations**: 對於高基數 (High Cardinality) 欄位的聚合（如 User ID），是否已評估記憶體衝擊？

---

## Real-world examples｜實戰案例

### Case 1: The "Export to Excel" Crash
**情境**: 一個後台管理系統允許管理者匯出所有訂單紀錄。開發者直接使用 `size: 10000` 迴圈呼叫 API。
**問題**: 當訂單量超過 50 萬筆，且多人同時匯出時，ES 節點頻繁發生 Full GC，導致集群無回應。
**解決方案 (Pseudo-code)**:

```python
# BAD: Using from/size loop
# for i in range(0, total, 1000):
#     es.search(from=i, size=1000, ...)

# GOOD: Using Point In Time (PIT) + search_after
pit = es.open_point_in_time(index="orders", keep_alive="1m")
search_after = None

while True:
    body = {
        "size": 1000,
        "query": {"match_all": {}},
        "pit": {"id": pit['id'], "keep_alive": "1m"},
        "sort": [{"timestamp": "asc"}]
    }
    if search_after:
        body["search_after"] = search_after

    response = es.search(body=body)
    hits = response['hits']['hits']
    if not hits:
        break
    
    process_batch(hits)
    search_after = hits[-1]['sort'] # Update cursor

es.close_point_in_time(id=pit['id'])
```

### Case 2: The Log Stash "Oversharding"
**情境**: 一家新創公司使用 Logstash 按日建立索引 `logs-2024-01-01`。初期每天 Log 只有 100MB，但預設設定了 `number_of_shards: 5`。
**問題**: 運行一年後，集群擁有 `365 * 5 = 1825` 個分片，但總資料量僅 30GB。Cluster State 巨大，重啟節點需要數十分鐘。
**解決方案**:
1. **Immediate**: 使用 Reindex API 將舊的按日索引合併為按月索引 (e.g., `logs-2024-01`)。
2. **Long-term**: 設定 ILM Policy。
   - **Hot Phase**: 當索引超過 30GB 或 30 天時 Rollover。
   - **Warm Phase**: 將舊索引 Force Merge 為 1 個 segment，並將分片數縮減 (Shrink) 為 1。