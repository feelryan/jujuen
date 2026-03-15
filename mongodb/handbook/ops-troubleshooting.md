# 生產環境維運與故障排除 / Production Ops & Troubleshooting

在開發環境中，MongoDB 只需要「能跑」；但在生產環境中，它必須「能活」。本章節專注於如何讓 MongoDB 在高併發、大數據量下保持健康，以及當災難發生時如何快速止血與復原。

---

## Mental model｜心智模型

要掌握 MongoDB 的維運，必須建立以下兩個核心視角：

### 1. The "Working Set" Intuition (工作集直覺)
MongoDB 的效能極度依賴記憶體（RAM）。WiredTiger 引擎會盡可能將數據與索引載入 Cache。
- **健康狀態**：你的 **Working Set**（熱數據 + 索引）完全裝在 RAM 裡。
- **亞健康狀態**：部分熱數據需要頻繁從 Disk 讀取（Disk I/O 上升，Latency 增加）。
- **崩潰邊緣**：記憶體抖動（Thrashing），Disk I/O 滿載，CPU 等待 I/O，系統回應停滯。
> **Mental Model**: 想像 RAM 是一個有限的桌面，Disk 是一個巨大的檔案櫃。維運的目標是確保「當下正在用的文件」都在桌面上，而不是頻繁轉身去翻櫃子。

### 2. The "Ticket" Economy (票券經濟學)
WiredTiger 使用 **Read/Write Tickets** 來控制併發（Concurrency）。
- 預設通常有 128 個 Read Tickets 和 128 個 Write Tickets。
- 每一個正在執行的操作都需要一張「票」。
- **雪崩效應（Avalanche）**：當查詢變慢（例如缺少索引），票券被長時間佔用，後續請求拿不到票進入 Queue，導致 Application Server 連線數暴增，最終拖垮整個資料庫。
> **Mental Model**: 想像 MongoDB 是一個只有 128 個座位的餐廳。如果客人（Query）吃得太慢（Slow Query），外面排隊的人（Queued Operations）就會塞爆街道。解決方案不是擴大餐廳（加 CPU），而是讓客人吃快一點（優化索引）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Visibility & Monitoring Strategy (可觀測性策略)
不要只看 CPU 和 Memory。MongoDB 特有的關鍵指標：
- **Replication Lag (複製延遲)**：Secondary 落後 Primary 多久？超過 10 秒即需警報。
- **Opcounters**：Command/Query/Insert/Update/Delete 的速率。突然歸零或暴增都代表異常。
- **Connections**：連線數突然飆高通常是「症狀」而非「病因」（通常是因為 DB 鎖死導致 App 連線堆積）。
- **WiredTiger Cache Dirty %**：如果 Dirty Cache 超過 20% 且降不下來，代表 Disk I/O 寫入跟不上。
- **Tickets Available**：若 Read/Write Tickets 掉到 0，系統已處於鎖死狀態。

### 2. Backup & Recovery (備份與還原)
- **Point-in-Time Recovery (PITR)**：
  - 生產環境僅依賴 `mongodump` 是不夠的（因為它是邏輯備份，恢復慢）。
  - **Pattern**：使用 Filesystem Snapshots (如 AWS EBS Snapshot) + Oplog 備份，實現「時間點還原」。
- **Hidden Node Backup**：
  - **Pattern**：建立一個 `priority: 0` 且 `hidden: true` 的 Secondary 節點專門用於備份。
  - 這樣做備份時的 I/O 負載完全不會影響線上服務。

### 3. Rolling Maintenance (滾動式維護)
即使 MongoDB 4.4+ 支援更友善的 Index Build，但在大規模集群中，最佳實務仍是：
1.  在 Secondary 節點建立索引。
2.  將該 Secondary 升級為 Primary（Stepdown）。
3.  在原本的 Primary（現在是 Secondary）建立索引。
4.  **目的**：確保 Primary 永遠不會因為維護操作而效能下降。

### 4. Security Hardening (安全性強化)
- **Network Binding**：永遠設定 `bindIp`，不要綁定 `0.0.0.0` 除非有防火牆嚴格控制。
- **Role-Based Access Control (RBAC)**：
  - 不要使用 root 帳號連線應用程式。
  - 為每個 Microservice 建立獨立的 User，並僅授予 `readWrite` 權限至特定 Database。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Transparent Huge Pages" (THP) Trap
- **Anti-pattern**：在 Linux 上直接安裝 MongoDB 而未關閉 THP。
- **後果**：WiredTiger 引擎與 THP 相性極差，會導致記憶體使用效率低落與 CPU 飆高。
- **修正**：務必在 OS 層級 Disable THP。

### 2. "Kill -9" Panic
- **Anti-pattern**：當 DB 無回應時，直接 `kill -9 <pid>`。
- **後果**：可能導致 WiredTiger 資料損毀（雖然有 Journaling，但風險仍在），且重啟後的復原（Replay Oplog/Journal）時間會非常長。
- **修正**：使用 `kill -2` (SIGINT) 或 `kill -15` (SIGTERM)，讓 MongoDB 優雅關閉並 Flush 數據。

### 3. Unbounded Arrays (無限增長的陣列)
- **Anti-pattern**：Schema 設計中包含無限增長的 Array（如 Log、Comments），且沒有設限。
- **後果**：Document 超過 16MB 限制；更糟的是，每次更新該 Document 都需要搬移硬碟位置（如果空間不足），導致嚴重的 Write Amplification。

### 4. Ignoring "w: majority"
- **Anti-pattern**：寫入時只用預設 `w: 1`，且未監控 Replication Lag。
- **後果**：當 Primary 突然宕機，尚未複製到 Secondary 的數據將永久遺失（Rollback）。

---

## Checklists & workflows｜檢查清單與流程

### 🚀 Go-Live Checklist (上線前檢查)

- [ ] **OS Settings**: Transparent Huge Pages (THP) 已關閉。
- [ ] **OS Settings**: `ulimit` (Open files, Processes) 已調高 (建議 soft/hard limit 64000+)。
- [ ] **Network**: `bindIp` 設定正確，Security Group/Firewall 僅允許 Application Server IP。
- [ ] **Replication**: 至少 3 個節點 (PSS: Primary-Secondary-Secondary) 以確保 HA。
- [ ] **Storage**: 使用 XFS 檔案系統 (WiredTiger 建議)，且 Data 與 Log 分離至不同 Disk (若追求極致效能)。
- [ ] **Security**: 啟用 Authentication (`security.authorization: enabled`)，並停用 HTTP interface。
- [ ] **Backup**: 驗證備份機制有效，並**實際演練過一次 Restore**。

### 🚑 Slow Query Troubleshooting Workflow (慢查詢排查流程)

當系統變慢時，請依照此決策樹行動：

1.  **Check Hardware Saturation (檢查硬體飽和度)**:
    - CPU 滿載？ -> 可能是 Missing Index 導致全表掃描 (COLLSCAN) 或 Aggregation 計算量過大。
    - Disk I/O 滿載？ -> Working Set 超出 RAM，正在頻繁 Swap/Page fault。

2.  **Identify the Operation (鎖定兇手)**:
    - 執行 `db.currentOp({ "secs_running": { "$gt": 3 } })` 找出執行超過 3 秒的操作。
    - 關注 `op` (query/update), `ns` (namespace), `planSummary` (COLLSCAN 是警訊)。

3.  **Immediate Mitigation (緊急止血)**:
    - 如果某個 Query 正在拖垮 DB，果斷執行 `db.killOp(<opid>)`。
    - **注意**：不要 Kill 正在進行的 `index build` 或系統內部操作。

4.  **Root Cause Analysis (根因分析)**:
    - 開啟 Profiler: `db.setProfilingLevel(1, { slowms: 100 })`。
    - 使用 `explain()` 分析該查詢。
    - 補上 Index 或重構查詢邏輯。

---

## Real-world examples｜實戰案例

### Case 1: The "Sort" Memory Limit Explosion
**情境**：電商網站在大促時，後台訂單列表突然無法讀取，DB CPU 飆高。
**診斷**：
- Log 顯示錯誤：`Executor error during find command :: caused by :: Sort operation used more than 33554432 bytes of RAM`.
- 開發者下了一個 `db.orders.find({}).sort({ createdAt: -1 })` 但 `createdAt` 欄位**沒有索引**。
**機制**：MongoDB 在沒有索引的情況下排序，必須將所有結果載入記憶體排序，預設上限 32MB（舊版）或 100MB（新版）。一旦超過就會報錯或轉存 Disk (若允許)，導致極慢。
**解決**：
1.  緊急建立索引 `db.orders.createIndex({ createdAt: -1 })`。
2.  若無法立即建索引，暫時限制查詢範圍（如只查最近一小時）。

### Case 2: Connection Storm due to Lock Contention
**情境**：API Server 回報 "Connection Timed Out"，DB 連線數從 500 飆升到 5000+。
**診斷**：
- 直覺認為是流量太大，於是重啟 Application Server。
- 結果重啟後，連線數瞬間又飆滿，DB 依然無回應。
- 檢查 `db.serverStatus().wiredTiger.concurrentTransactions`，發現 `read` tickets 剩餘為 0。
**原因**：某個慢查詢佔用了所有 Read Tickets。Application Server 的 Connection Pool 因為拿不到 DB 回應，不斷建立新連線嘗試重試（Retry Storm）。
**解決**：
1.  **不是**增加 `maxIncomingConnections`。
2.  找出並 Kill 掉佔用 Tickets 的慢查詢。
3.  調整 Application 端 Connection Pool 設定，設定合理的 `maxPoolSize` 和 `connectTimeoutMS`，避免無限重試。

### Case 3: Oplog Window Too Short
**情境**：每週日凌晨進行大量批次刪除（Housekeeping），結果導致 Secondary 節點進入 `RECOVERING` 狀態，無法同步。
**診斷**：
- 執行 `rs.printReplicationInfo()` 發現 Oplog window（Oplog 能保存的時間長度）只有 1 小時。
- 批次刪除操作產生了大量的 Oplog entries。
- Secondary 處理速度較慢，落後超過 1 小時，原本需要的 Oplog 已經在 Primary 上被覆蓋了。
**解決**：
- **短期**：該 Secondary 必須重新執行 Initial Sync（全量同步）。
- **長期**：擴大 Oplog Size（MongoDB 4.0+ 可線上調整 `db.adminCommand({replSetResizeOplog: 1, size: <newSize>})`），確保 Window 至少能涵蓋 24-48 小時的操作量。