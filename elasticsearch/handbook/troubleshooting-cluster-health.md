# 集群健康診斷與故障排除流程 / Cluster Health Diagnosis & Troubleshooting Workflow

## Mental model｜心智模型

在處理 Elasticsearch (ES) 故障時，建立正確的心智模型能避免恐慌並加速定位問題。請將 ES 集群想像成一個 **「分散式倉儲物流系統」**：

1.  **紅綠燈機制 (The Traffic Light System)**：
    *   **Green (綠燈)**：運作完美。所有的主貨物（Primary Shards）和備份貨物（Replica Shards）都已就位。
    *   **Yellow (黃燈)**：功能正常，但風險升高。所有的主貨物都在，但部分備份貨物遺失或無法分配。這意味著**資料完整性沒問題，但高可用性（HA）受損**。如果此時再壞一個節點，可能會遺失資料。
    *   **Red (紅燈)**：服務部分中斷。至少有一個主貨物（Primary Shard）遺失。這意味著**部分資料無法被搜尋或寫入**。

2.  **分片分配決策者 (The Allocator)**：
    *   ES 有一個內部排程器（Allocator），負責決定貨物（Shards）該放在哪個倉庫（Node）。
    *   當集群變紅或黃時，通常是因為 Allocator **「想分配但無法分配」**。你的任務不是去「修好」分片，而是去**詢問 Allocator 為什麼它無法分配**，並排除該障礙（如：磁碟滿了、節點離線、版本不匹配）。

3.  **腦裂預防 (Split-brain Prevention)**：
    *   想像兩個倉儲管理員同時發號施令，資料會錯亂。ES 透過 Quorum（法定人數）機制確保只有一個 Master。在舊版是 `minimum_master_nodes`，新版（7.x+）則是自動化的 Voting Configuration。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 Allocation Explain API (黃金準則)
不要猜測為什麼分片未分配，直接問 ES。這是排查問題的第一步。
```json
GET /_cluster/allocation/explain
```
這個 API 會告訴你具體的錯誤原因（例如：`DISK_THRESHOLD_EXCEEDED` 或 `MAX_RETRIES_REACHED`）。

### 2. 區分 Master 與 Data Nodes
在生產環境（Production）中，**務必**將 Master 節點與 Data 節點分離。
*   **Dedicated Master Nodes**：只負責集群狀態維護，不存資料、不處理查詢。這能防止因 heavy query 導致 OOM (Out of Memory)，進而讓整個集群崩潰。
*   **Data Nodes**：專注於 CRUD 與搜尋。

### 3. 設定磁碟水位線 (Disk Watermarks)
ES 會根據磁碟剩餘空間採取保護措施：
*   **Low watermark (85%)**: 停止分配新分片到該節點。
*   **High watermark (90%)**: 開始將分片遷移出該節點。
*   **Flood stage (95%)**: 強制將索引設為 `read_only_allow_delete`，這是最常見的寫入被拒原因。

### 4. 監控 Heap Memory 與 GC
Heap Usage 超過 75% 且頻繁發生 Long GC 是危險訊號。
*   **Pattern**: 設定 JVM Heap Size 為實體記憶體的 50%（但不超過 32GB 以保留 Compressed Oops）。
*   **Circuit Breakers**: 確保 Circuit Breaker 設定正確，防止單一巨大查詢沖垮節點。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目重啟節點 (Blind Restarts)
*   **錯誤行為**：看到集群變紅，立刻重啟所有節點。
*   **後果**：重啟期間，ES 會試圖重新平衡（Rebalance）分片，導致大量的網路 I/O 和磁碟 I/O，這通常會讓原本就脆弱的集群雪上加霜（Thundering Herd Problem）。
*   **修正**：先診斷，且在維護期間應先暫停分片分配（Disable Allocation）。

### 2. 忽視 Yellow 狀態 (Ignoring Yellow State)
*   **錯誤行為**：「反正搜尋還能用，Yellow 沒關係。」
*   **後果**：Yellow 代表你失去了冗餘（Redundancy）。此時若發生硬體故障，Yellow 會直接變成 Red，並伴隨永久性資料遺失。

### 3. 刪除索引作為修復手段 (Panic Deletion)
*   **錯誤行為**：看到 Unassigned Shards 就直接刪除對應索引。
*   **後果**：這確實能讓集群變綠，但你永久遺失了資料。除非確認資料可再生或已損壞無法修復，否則不應輕易刪除。

### 4. 過度分片 (Oversharding)
*   **錯誤行為**：幾 KB 的日誌索引也開 5 個 Primary + 1 個 Replica。
*   **後果**：每個分片都會消耗 Heap Memory。過多小分片是導致 Cluster State Update 緩慢和 OOM 的主因。
*   **原則**：單一分片大小建議在 10GB - 50GB 之間。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 緊急事故處理流程 (The "Red/Yellow" Protocol)

當集群狀態異常時，請依序執行以下步驟：

- [ ] **Step 1: 確認健康狀態與受影響範圍**
    ```bash
    GET _cluster/health
    GET _cat/indices?v&health=red  # 找出哪些索引壞了
    ```
- [ ] **Step 2: 找出未分配的分片 (Unassigned Shards)**
    ```bash
    GET _cat/shards?h=index,shard,prirep,state,unassigned.reason | grep UNASSIGNED
    ```
- [ ] **Step 3: 詢問原因 (Root Cause Analysis)**
    ```bash
    GET _cluster/allocation/explain
    ```
    *   *常見原因 A: `NODE_LEFT`* -> 檢查是否有節點離線或當機。
    *   *常見原因 B: `DISK_THRESHOLD_EXCEEDED`* -> 磁碟滿了。
    *   *常見原因 C: `ALLOCATION_FAILED` (Max Retries)* -> 分片損壞或恢復失敗次數過多。
- [ ] **Step 4: 採取行動**
    *   若磁碟滿：清理舊資料或擴容，並解鎖唯讀狀態（見下方案例）。
    *   若重試次數達上限：手動執行 `_cluster/reroute` retry。
    *   若節點離線：重啟節點（確保 Heap 設定正確）。

### 🛠 安全重啟/維護流程 (Safe Rolling Restart)

在進行升級或硬體維護時，必須遵循此流程以避免不必要的 I/O 風暴：

- [ ] **1. 停止分片分配 (Disable Allocation)**
    ```json
    PUT _cluster/settings
    {
      "transient": {
        "cluster.routing.allocation.enable": "primaries"
      }
    }
    ```
    *(這告訴 ES：如果節點暫時消失，不要急著複製資料)*
- [ ] **2. 執行同步 flush (Synced Flush)** (舊版 ES 建議，新版自動處理但手動更保險)
    ```bash
    POST _flush/synced
    ```
- [ ] **3. 重啟單一節點**
- [ ] **4. 確認節點加入集群**
    ```bash
    GET _cat/nodes
    ```
- [ ] **5. 恢復分片分配 (Re-enable Allocation)**
    ```json
    PUT _cluster/settings
    {
      "transient": {
        "cluster.routing.allocation.enable": "all"
      }
    }
    ```
- [ ] **6. 等待集群變綠 (Green)**，再進行下一個節點。

---

## Real-world examples｜實戰案例

### Case 1: 磁碟爆滿導致的 "Flood Stage" 鎖死

**情境**：監控系統發出警報，應用程式噴錯 `403 Forbidden`，錯誤訊息包含 `cluster_block_exception [FORBIDDEN/12/index read-only / allow delete (api)]`。

**診斷**：
1.  執行 `GET _cat/allocation?v` 發現某個節點磁碟使用率超過 95%。
2.  ES 自動觸發 Flood Stage 保護機制，將所有該節點上的索引設為唯讀。

**解決方案**：
1.  **清理空間**：刪除舊的 Log 索引或擴充磁碟容量。
2.  **解鎖索引**：即使空間清出來了，ES **不會自動**解鎖，必須手動執行：
    ```json
    PUT _all/_settings
    {
      "index.blocks.read_only_allow_delete": null
    }
    ```

### Case 2: 節點短暫斷線後的 Unassigned Shards

**情境**：一個 Data Node 因為 OOM 崩潰，重啟後回到了集群，但集群狀態一直是 Yellow，有幾個分片處於 `UNASSIGNED`。

**診斷**：
1.  執行 `GET _cluster/allocation/explain`。
2.  回應顯示：`"unassigned_info": { "reason": "ALLOCATION_FAILED", "failed_attempts": 5 }`。
3.  這表示 ES 嘗試恢復該分片 5 次都失敗了（可能因為 Translog 損壞或其他 IO 錯誤），為了保護集群，它停止了嘗試。

**解決方案**：
強制 ES 重試分配（Reroute Retry）：
```json
POST /_cluster/reroute?retry_failed=true
```
如果重試無效，且該分片是 Replica，可以考慮先將 Replica 數設為 0 再設回 1，強制重新複製（注意網路頻寬）。