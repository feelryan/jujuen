# 寫入效能優化檢核表 / Indexing Performance Optimization Checklist

## Mental model｜心智模型

要優化 Elasticsearch 的寫入效能，必須先理解從「收到請求」到「資料落地」的過程。請將寫入過程想像成一個 **「物流打包系統」**：

1.  **Buffer (暫存區)**：資料進入時，先堆在記憶體（In-memory buffer）中。此時資料還無法被搜尋到。
2.  **Refresh (上架)**：每隔一段時間（預設 1秒），系統將 Buffer 裡的資料寫成一個新的 **Lucene Segment**（檔案片段）。此時資料變成「可被搜尋」，但尚未完全安全落地（還在 OS Cache）。
3.  **Flush & Translog (入庫存檔)**：為了防止斷電遺失，資料同時會寫入 **Translog**。當 Translog 滿了或時間到了，會執行 Flush，將 Segment 真正寫入硬碟（Disk），並清空 Translog。
4.  **Merge (整理倉庫)**：隨著 Segment 越來越多，後台執行緒會將小 Segment 合併成大 Segment，並標記刪除舊資料。

**效能優化的核心權衡 (The Trade-off Triangle)：**

*   **Consistency (資料安全性)**：頻繁 fsync Translog 會拖慢速度。
*   **Real-time Search (即時搜尋)**：頻繁 Refresh 會產生大量小 Segment，消耗 CPU 進行 Merge。
*   **Indexing Speed (寫入速度)**：為了極致速度，我們通常會犧牲一點「搜尋即時性」與「極端狀況下的資料安全性」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 策略性調整 Refresh Interval (Strategic Refresh Interval)
這是提升吞吐量最立竿見影的設定。
*   **Pattern**: 在大量批次寫入（Batch Processing）或初始載入（Initial Load）期間，暫時關閉 Refresh。
*   **Action**: 將 `refresh_interval` 設為 `-1` 或 `30s`（預設是 `1s`）。
*   **Why**: 減少 Lucene Segment 的產生頻率，降低 Merge 壓力。

### 2. 善用 Bulk API 與多執行緒 (Bulk API & Concurrency)
永遠不要單筆寫入。
*   **Pattern**: 客戶端累積一批資料後一次發送。
*   **Sizing**: 建議每個 Bulk Request 大小在 **5MB ~ 15MB** 之間（而非看筆數，因為文件大小不一）。
*   **Concurrency**: 使用多個執行緒或 Process 並行發送 Bulk Request，直到集群 I/O 飽和。

### 3. 寫入期間停用 Replicas (Disable Replicas during Ingest)
*   **Pattern**: 對於全新的 Index，先設 `number_of_replicas: 0`，寫完後再改回原本數量（如 1）。
*   **Why**: 避免寫入時同時將資料複製到其他節點，節省大量的網路與重複索引（Indexing）開銷。寫完後再開啟 Replica，ES 會利用檔案複製（File-based recovery）來同步，速度更快。

### 4. 使用自動生成的 ID (Auto-generated IDs)
*   **Pattern**: 讓 Elasticsearch 自動產生 `_id`，而不是由客戶端指定（除非有強烈的去重需求）。
*   **Why**: 如果指定 ID，ES 必須先檢查該 ID 是否存在（Check for existence）以決定是 Insert 還是 Update。自動生成 ID 則跳過此檢查，直接 Append。

### 5. 優化 Translog 設定 (Tuning Translog)
*   **Pattern**: 將 Translog 的持久化策略設為 `async`。
*   **Config**: `index.translog.durability: async`
*   **Trade-off**: 如果節點當機，可能會遺失最後幾秒（預設 5秒）的資料，但能顯著減少磁碟 IOPS 壓力。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 單筆迴圈寫入 (The Loop-Insert Trap)
*   **Bad Practice**: 在程式碼中使用 `for doc in docs: es.index(doc)`。
*   **Consequence**: 網路來回（RTT）開銷巨大，集群花費大量資源處理 HTTP 連線而非索引資料。

### 2. 過大的 Bulk Request (Oversized Bulks)
*   **Bad Practice**: 一次發送幾百 MB 的 Bulk Request。
*   **Consequence**: 會佔用大量 Heap Memory，導致頻繁的 Garbage Collection (GC)，甚至引發 OutOfMemory 錯誤，反而卡住整個節點。

### 3. 過度複雜的 Mapping (Heavy Mapping)
*   **Bad Practice**: 在高頻寫入的 Index 上使用大量的 `nested` objects 或複雜的 `script` 處理。
*   **Consequence**: 寫入時的 CPU 計算成本過高。如果只是為了存 Log，盡量扁平化（Flatten）資料結構。

### 4. 忽略 HTTP 429 錯誤 (Ignoring Backpressure)
*   **Bad Practice**: 客戶端收到 `429 Too Many Requests` 時沒有實作指數退避（Exponential Backoff）重試機制，而是持續猛送。
*   **Consequence**: 加重集群負載，導致更多請求失敗，形成惡性循環。

---

## Checklists & workflows｜檢查清單與流程

在高吞吐量寫入任務（如每日數據匯入、Log 遷移）開始前，請依序檢查以下項目：

### Index Settings (索引設定)
- [ ] **Refresh Interval**: 是否已將 `index.refresh_interval` 設為 `-1` 或 `30s`？
- [ ] **Replicas**: 是否已將 `index.number_of_replicas` 設為 `0`？（僅適用於全新資料匯入）
- [ ] **Translog**: 是否接受將 `index.translog.durability` 設為 `async`？（視資料遺失容忍度而定）
- [ ] **Buffer Size**: 確認 `indices.memory.index_buffer_size` 足夠（預設 10% Heap，專用寫入節點可調高至 20%）。

### Client Side (客戶端設定)
- [ ] **Bulk Sizing**: Bulk Request 大小是否控制在 5MB-15MB 之間？
- [ ] **Concurrency**: 是否啟用了多執行緒/多進程寫入？
- [ ] **ID Generation**: 是否使用了 Auto-generated IDs（如果業務邏輯允許）？
- [ ] **Error Handling**: 是否實作了 Retry with Backoff 機制處理 429 錯誤？

### Hardware & OS (硬體與系統)
- [ ] **Storage**: 是否使用 SSD？（HDD 對隨機寫入效能極差）
- [ ] **Swap**: 系統 Swap 是否已完全關閉？（Swap 是效能殺手）

### Post-Ingest Cleanup (寫入後收尾)
- [ ] **Restore Settings**: 恢復 `refresh_interval` (e.g., `1s`) 和 `number_of_replicas`。
- [ ] **Force Merge**: 如果該 Index 寫入後不再修改（Read-only），執行 `_forcemerge` 將 Segment 合併為 1，提升讀取效能。

---

## Real-world examples｜實戰案例

### 案例：歷史 Log 數據的大規模遷移 (Historical Log Migration)

**情境**：你需要將 10TB 的 Log 資料從舊集群遷移到新集群，要求在最短時間內完成。

#### 1. 準備階段：建立優化過的 Template
在開始寫入前，定義一個專門針對高寫入優化的 Index Template。

```json
PUT _index_template/migration_template
{
  "index_patterns": ["logs-migration-*"],
  "template": {
    "settings": {
      "number_of_shards": 6, 
      "number_of_replicas": 0,          // 暫時關閉副本
      "refresh_interval": "-1",         // 暫時關閉刷新
      "index.translog.durability": "async", // 非同步寫入磁碟
      "index.translog.sync_interval": "30s"
    },
    "mappings": {
      "_source": { "enabled": true },
      "dynamic": false  // 關閉動態映射，避免意外欄位爆炸
    }
  }
}
```

#### 2. 執行階段：Python Client 虛擬碼
使用 `parallel_bulk` helper 來處理並發與重試。

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

es = Elasticsearch("http://es-node:9200")

def generate_logs():
    # 模擬讀取大量檔案
    for line in open("huge_log_file.json"):
        yield {
            "_index": "logs-migration-2023",
            "_source": line # 假設 line 已經是 JSON
            # 注意：不指定 _id，讓 ES 自動產生
        }

# 使用 parallel_bulk 自動處理分批與多執行緒
# thread_count: 根據 CPU 核數調整
# chunk_size: 根據單條數據大小調整，目標是讓 payload 約 5-15MB
for success, info in parallel_bulk(es, generate_logs(), thread_count=4, chunk_size=2000):
    if not success:
        print("A document failed:", info)
```

#### 3. 收尾階段：恢復生產設定
資料寫入完畢後，必須將設定改回適合「讀取」與「高可用」的狀態。

```bash
# 1. 恢復 Refresh (讓資料可被搜尋)
PUT /logs-migration-*/_settings
{ "index.refresh_interval": "1s" }

# 2. 恢復副本 (開始複製資料以確保 HA)
PUT /logs-migration-*/_settings
{ "index.number_of_replicas": 1 }

# 3. (選用) 強制合併 Segment，優化長期儲存空間與查詢效能
POST /logs-migration-*/_forcemerge?max_num_segments=1
```