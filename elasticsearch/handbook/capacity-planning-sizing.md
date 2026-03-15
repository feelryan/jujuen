# 容量規劃與分片策略 / Capacity Planning & Sharding Strategies

## Mental model｜心智模型

在進行 ElasticSearch (ES) 的容量規劃時，請放棄「資料庫表格」的思維，轉而建立以下三個核心的心智模型：

### 1. Shard 是資源消耗的最小單位 (The Unit of Cost)
每一個 Shard 本質上就是一個完整的 Lucene Index。
- **Memory Overhead**：不管 Shard 裡面有沒有資料，它都會佔用 Heap Memory（維護 FST, Term Dictionary 等）。
- **Concurrency**：Shard 是並行運算的單元。查詢時，ES 會在所有相關的 Shard 上並行搜尋。
- **Trade-off**：
  - **Shard 太多** = Cluster State 過大，Master Node 負擔重，Heap 耗盡 (OOM)。
  - **Shard 太大** = 故障恢復 (Recovery) 極慢，Rebalance 困難，單一執行緒搜尋效能瓶頸。

### 2. 資料有溫度 (Data Temperature)
並非所有資料都需要相同的硬體資源。
- **Hot (熱)**：正在寫入、頻繁查詢。需要最快的 NVMe SSD 和高 CPU。
- **Warm (溫)**：不再寫入、查詢頻率降低。可使用較便宜的 SSD。
- **Cold/Frozen (冷/凍)**：極少查詢、僅供合規存檔。可使用 HDD 或 Object Storage (Searchable Snapshots)。

### 3. 倒排索引的不可變性 (Immutability)
ES 的資料寫入後（形成 Segment），原則上是不修改的。更新文件其實是「標記刪除舊的 + 寫入新的」。
- 這意味著 **Merge (合併)** 操作非常消耗 I/O 和 CPU。
- 容量規劃必須預留 15% - 20% 的磁碟空間給 Merge 操作與作業系統，切勿塞滿。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Shard Sizing 黃金法則 (The 10GB-50GB Rule)
這是業界最通用的經驗法則，雖然不是絕對，但能避免 90% 的問題。
- **搜尋類 (Search-heavy)**：單一 Shard 建議 **10GB - 30GB**。
  - 理由：較小的 Shard 搜尋速度較快，且更容易在節點間平衡。
- **日誌類 (Log/Time-series)**：單一 Shard 建議 **30GB - 50GB**。
  - 理由：日誌通常寫入量大，稍微大一點的 Shard 可以減少 Cluster 的總 Shard 數量，降低 Metadata 壓力。

### 2. 使用 ILM + Rollover 而非固定時間切分
**Anti-pattern**: 按天切分索引 (`logs-2023-10-01`)。
**Best Practice**: 使用 **Index Lifecycle Management (ILM)** 搭配 **Rollover**。
- **為什麼？** 週日的日誌量可能只有週一的 10%。按天切分會導致 Shard 大小極度不均。
- **怎麼做？** 設定策略：當索引達到 50GB **或** 經過 30 天時，自動滾動產生新索引。這樣能保證每個 Shard 的大小均勻。

### 3. Hot-Warm Architecture 實作
利用 Node Attributes 將硬體分層。
- **Tagging Nodes**: 在 `elasticsearch.yml` 設定 `node.attr.data: hot` 或 `warm`。
- **ILM Policy**:
  - **Hot Phase**: 寫入與近期查詢。Priority 高。
  - **Warm Phase**: Rollover 後，將 `index.routing.allocation.require.data` 設為 `warm`，並執行 **Force Merge** (將 segment 縮減為 1，大幅提升讀取效能)。
  - **Delete Phase**: 超過保留期限自動刪除。

### 4. 節點與 Heap 的比例 (The Heap:Storage Ratio)
- 一般建議 Heap Size 不要超過 30-31GB (Compressed OOPs limit)。
- **Search Nodes**: 記憶體吃重，建議 1:16 (1GB Heap : 16GB Disk)。
- **Log/Warm Nodes**: 儲存吃重，建議 1:48 到 1:96 (1GB Heap : 96GB Disk)。
- **Shard Count Limit**: 每個節點的 Shard 數量建議控制在 **每 GB Heap < 20 個 Shard**。例如 30GB Heap 的節點，Shard 總數不應超過 600。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Default 5 Shards" Trap (預設陷阱)
- **情境**：舊版 ES 預設建立 5 個 Primary Shards。
- **後果**：如果你有一堆小索引（例如每天幾 MB 的 metrics），你會產生數千個幾乎空的 Shard。
- **徵兆**：Cluster State Update 變慢，Master Node CPU 飆高，重啟 ES 需要數小時。
- **修正**：小索引設為 `number_of_shards: 1`，或者改用 Data Stream 讓 ES 自動管理。

### 2. Oversharding (過度分片)
- **錯誤觀念**：「Shard 越多，速度越快。」
- **事實**：對於單次查詢，這可能是對的（並行度高）。但對於高併發查詢，過多的 Shard 會導致 CPU Context Switch 爆炸，且每個 Search Request 都要彙總所有 Shard 的結果（Coordinator Node 壓力大）。

### 3. Ignoring Replica Cost (忽略副本成本)
- **誤區**：計算容量時只算原始資料大小。
- **事實**：`number_of_replicas: 1` 代表儲存空間需求直接 **x2**。
- **建議**：
  - Hot Data: 至少 1 Replica (HA + Read Throughput)。
  - Cold Data: 可以考慮 0 Replica (如果可從備份恢復或使用 Searchable Snapshots) 以節省成本。

### 4. 磁碟塞太滿 (Disk Watermark)
- **地雷**：認為 1TB 硬碟可以存 1TB 資料。
- **機制**：ES 有 Low/High/Flood-stage watermarks。
  - 達到 85% (Low)：停止分配新 Shard 到該節點。
  - 達到 90% (High)：嘗試將 Shard 搬離該節點。
  - 達到 95% (Flood-stage)：**強制設為 Read-only**，寫入會直接報錯。

---

## Checklists & workflows｜檢查清單與流程

### Capacity Planning Workflow (容量估算流程)

1.  **估算原始資料量 (Source Data)**
    - [ ] 每日日誌量 / 總文件大小？ (e.g., 100GB/day)
    - [ ] 保留時間 (Retention)？ (e.g., 30 days)

2.  **計算索引後膨脹係數 (Indexing Overhead)**
    - [ ] Source (JSON) + Indexing (Inverted Index, Doc Values) ≈ 原始大小 * 1.1 ~ 1.3 (視 mapping 複雜度而定)。
    - [ ] 加上 Replica： (原始大小 * 1.2) * (1 + Replica數)。

3.  **決定 Shard 策略**
    - [ ] 總儲存需求 / 目標 Shard Size (30-50GB) = Primary Shard 總數。
    - [ ] 是否使用 ILM Rollover？(強烈建議使用)

4.  **硬體需求回推**
    - [ ] 總 Shard 數 / 20 = 所需最小 Heap 總量 (GB)。
    - [ ] 總儲存需求 / 0.8 (預留 20% 緩衝) = 所需磁碟空間。

### Health Check (健康檢查)

- [ ] **Shard Size Check**: 是否有超過 60GB 的巨大 Shard？或大量小於 100MB 的微型 Shard？
- [ ] **Shard Count Check**: `GET _cluster/health` 顯示的 `active_shards` 是否過多？(單節點 > 600?)
- [ ] **Heap Usage**: 節點 Heap 長期是否低於 75%？(長期高於 85% 是危險訊號)
- [ ] **Segment Count**: Warm 節點上的舊索引是否已執行 Force Merge (`max_num_segments=1`)？

---

## Real-world examples｜實戰案例

### Case 1: High-Volume Log Aggregation (日誌分析)
**情境**：每日產生 500GB 的 Application Logs，需保留 14 天，主要用於除錯（最近 3 天最常查）。

**Design**:
- **Architecture**: Hot-Warm。
- **ILM Policy**:
  - **Hot**: Rollover 當 Shard 達 50GB 或 索引達 24小時。Replica = 1。
  - **Warm**: 3 天後移動到 Warm nodes，執行 Force Merge (segments=1)，Replica 降為 0 (若可接受風險) 或維持 1。
  - **Delete**: 14 天後刪除。
- **Sizing Calculation**:
  - Daily Data on Disk: 500GB * 1.2 (overhead) * 2 (1 replica) = 1.2TB / day。
  - Total Storage: 1.2TB * 14 days = 16.8TB。
  - Hot Nodes: 需處理寫入 I/O，配置 NVMe SSD。
  - Warm Nodes: 儲存大量唯讀資料，配置大容量 HDD/SATA SSD。

### Case 2: E-Commerce Product Search (電商商品搜尋)
**情境**：商品總數 1,000 萬件，資料量約 20GB，極少變動，但讀取併發極高 (High QPS)。

**Design**:
- **Strategy**: **Over-replication** (以空間換取讀取效能)。
- **Shard Setup**:
  - 資料量 20GB -> 1 個 Primary Shard 就夠了 (符合 <30GB 原則)。
  - 不要切成 5 個 Shard，那會降低查詢效率。
- **Replicas**:
  - 設為 3 或 5 (視節點數而定)，讓每個 Data Node 都有完整的資料副本。
  - 這樣查詢可以完全在地化 (Local read)，且能負載平衡到所有節點。
- **Optimization**:
  - 定期 (如每天凌晨) 對索引執行 Force Merge，確保最佳讀取效能。

### Case 3: The "Too Many Shards" Disaster (反面教材)
**情境**：某團隊為每個客戶建立一個獨立索引，共有 5,000 個客戶。每個客戶每天資料量僅 1MB。預設 1 Primary + 1 Replica。

**Result**:
- Shard 總數：5,000 * 2 = 10,000 Shards。
- 總資料量：僅 5GB。
- **後果**：Cluster 崩潰。Master 節點無法處理 Cluster State 更新。Heap 被 Shard metadata 吃光。
- **Fix**:
  - 改用單一索引 `customers-logs`，並在 Document 中增加 `customer_id` 欄位。
  - 使用 `Routing` 功能確保特定客戶的查詢只路由到特定 Shard (可選)。
  - Shard 數量降為 1 Primary + 1 Replica，系統恢復健康。