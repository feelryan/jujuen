# 持久化策略與資料安全性 / Persistence Strategies & Data Safety

## Mental model｜心智模型

在 Redis 的世界裡，持久化（Persistence）並非「開或關」的二元選項，而是一場關於 **效能（Performance）** 與 **資料安全性（Data Safety）** 的權衡賽局。

要理解 Redis 的持久化，請建立以下三個核心觀念：

1.  **快照 vs. 日誌 (Snapshot vs. Log)**：
    *   **RDB (Redis Database)** 就像是「相機拍照」。它在特定時間點紀錄記憶體的完整狀態。優點是還原快（讀照片就好），缺點是如果兩次拍照中間發生火災（當機），這段時間的變化就全丟了。
    *   **AOF (Append Only File)** 就像是「錄影機」或「會計帳本」。它依序記錄每一筆寫入指令。優點是資料掉失率極低，缺點是重播（Replay）所有指令來還原資料非常慢，且檔案通常比 RDB 大。

2.  **Copy-on-Write (CoW) 的代價**：
    *   無論是產生 RDB 還是重寫 AOF，Redis 都會呼叫系統的 `fork()`。這雖然利用 OS 的 CoW 機制避免了記憶體翻倍，但 `fork` 本身會暫停主執行緒（Main Thread）。
    *   **心法**：記憶體越大，`fork` 暫停時間越長。在高併發場景下，這幾百毫秒的暫停可能導致應用程式逾時。

3.  **RPO 與 RTO 的決策矩陣**：
    *   **RPO (Recovery Point Objective)**：你能容忍遺失多少資料？（1 秒？15 分鐘？還是 0？）
    *   **RTO (Recovery Time Objective)**：系統當機後，必須在多久內恢復服務？（1 分鐘？1 小時？）
    *   Redis 4.0+ 的 **混合持久化 (Hybrid Persistence)** 是目前的甜蜜點，試圖同時滿足較佳的 RPO 與 RTO。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 現代標準配置：混合持久化 (Hybrid Persistence)
在 Redis 4.0 之後，最強烈建議的模式是結合 RDB 的快速載入與 AOF 的資料完整性。

*   **配置方式**：開啟 AOF，並啟用 RDB Preamble。
    ```conf
    appendonly yes
    aof-use-rdb-preamble yes
    ```
*   **原理**：AOF 重寫（Rewrite）時，會先將當下的記憶體做成 RDB 快照放在 AOF 檔頭，後續的增量寫入才用 AOF 格式追加。
*   **優勢**：重啟速度極快（RDB 部分），且資料遺失風險低（AOF 部分）。

### 2. RPO/RTO 導向的策略選擇 (Strategy Selection)

| 場景 (Scenario) | 建議策略 (Strategy) | 關鍵配置 (Key Config) | RPO | RTO |
| :--- | :--- | :--- | :--- | :--- |
| **純快取 (Pure Cache)** | **No Persistence** | `save ""` <br> `appendonly no` | N/A | 極快 (空啟動) |
| **一般通用 (General)** | **Hybrid (Default)** | `appendonly yes` <br> `appendfsync everysec` <br> `aof-use-rdb-preamble yes` | < 1 sec | 快 |
| **高寫入/低延遲 (High Write)** | **RDB Only (Optimized)** | `save 900 1` (調整頻率) <br> `appendonly no` | 分鐘級 | 快 |
| **嚴格資料安全 (Strict Safety)** | **AOF Strong** | `appendfsync always` (極慢，慎用) | 趨近 0 | 慢 |

### 3. 將持久化壓力轉移至 Replica (Offload to Replica)
在極高負載的 Master 節點上，為了避免 `fork()` 造成的延遲（Latency Spike）：
*   **Pattern**：關閉 Master 的持久化，只在 Replica（從節點）開啟 AOF/RDB。
*   **風險**：如果 Master 當機並自動重啟（且無持久化檔），它會是空的。此時 Replica 若自動同步，Replica 的資料也會被清空。
*   **防禦**：必須關閉 Master 的自動重啟，或確保架構中有完善的 Failover 機制（如 Sentinel/Cluster）能先將 Replica 升級為 Master。

### 4. 備份不等於持久化 (Backup $\neq$ Persistence)
持久化檔案（dump.rdb / appendonly.aof）保存在本地磁碟，若伺服器硬碟損壞則全毀。
*   **Best Practice**：編寫 Cron Job 或使用雲端備份服務，定期將 RDB 檔案複製到 Object Storage (如 AWS S3, GCS)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤用 `appendfsync always`
*   **陷阱**：為了追求「零遺失」，將 AOF 同步設為 `always`。
*   **後果**：Redis 的效能將受限於磁碟 IOPS，寫入吞吐量暴跌 10~100 倍。
*   **建議**：使用 `everysec`（每秒同步）。這是效能與安全性的最佳平衡點，最多只遺失 1 秒資料。

### 2. 在記憶體緊繃時進行 BGSAVE
*   **陷阱**：Redis 實例佔用了 80% 以上的實體記憶體，此時觸發 BGSAVE。
*   **後果**：Copy-on-Write 需要額外記憶體。若寫入頻繁，OS 可能會因為記憶體不足而觸發 OOM Killer 殺掉 Redis process。
*   **建議**：預留 30-50% 記憶體給 CoW 使用，或設定 `maxmemory` 限制。

### 3. 忽視 `fork` 造成的延遲 (Latency Spikes)
*   **陷阱**：監控圖表顯示每隔一段時間就有規律的延遲尖峰，卻查不出慢查詢（Slowlog）。
*   **原因**：這是 RDB 生成或 AOF Rewrite 時 `fork` 導致的主執行緒阻塞。
*   **診斷**：檢查 `info stats` 中的 `latest_fork_usec`。
*   **解法**：避免在單一實例存儲過大數據（如 > 20GB），改用 Cluster 分片以減少單一實例的 fork 時間。

### 4. 雲端環境的 IOPS 限制
*   **陷阱**：在雲端主機（如 EC2, GCE）使用預設的低階磁碟。
*   **後果**：AOF Rewrite 或 BGSAVE 時吃滿磁碟頻寬，導致正常的讀寫請求被阻塞（Block）。
*   **建議**：確保磁碟吞吐量（Throughput）能滿足「正常寫入 + 持久化寫入」的峰值需求。

---

## Checklists & workflows｜檢查清單與流程

### Persistence Configuration Checklist
在部署到生產環境前，請依序確認：

- [ ] **RPO 需求確認**：業務能否容忍 1 秒的資料遺失？
    - [ ] 能 -> 使用 `appendfsync everysec`。
    - [ ] 不能 -> 考慮應用層雙寫或 `appendfsync always`（需評估效能）。
- [ ] **RTO 需求確認**：資料庫重啟需多快？
    - [ ] 需極快 -> 務必開啟 `aof-use-rdb-preamble yes`。
- [ ] **磁碟空間規劃**：
    - [ ] 預留至少 2 倍於記憶體的磁碟空間（給 AOF Rewrite 與 RDB 暫存使用）。
- [ ] **Rewrite 策略優化**：
    - [ ] 設定 `no-appendfsync-on-rewrite yes`？（若磁碟 I/O 競爭嚴重，這能避免主執行緒阻塞，但代價是 Rewrite 期間若當機可能遺失較多資料）。
- [ ] **監控設置**：
    - [ ] 監控 `rdb_last_bgsave_status` 與 `aof_last_write_status`。
    - [ ] 監控 `latest_fork_usec` 確保 fork 時間在可接受範圍（通常 < 200ms）。

### Disaster Recovery Workflow (簡易版)
當發生資料損壞或誤刪時：

1.  **Stop**: 立即停止應用程式寫入，避免汙染或覆蓋現有資料。
2.  **Assess**: 檢查現有的 AOF 與 RDB 檔案大小與時間戳記。
3.  **Restore Strategy**:
    *   若 AOF 損壞：使用 `redis-check-aof --fix` 工具修復（注意：這會截斷損壞部分）。
    *   若需回滾到特定時間點：不要重啟 Redis（它會自動重寫 AOF）。應使用備份的 RDB 檔案覆蓋，並暫時關閉 AOF (`appendonly no`) 啟動，確認資料無誤後再熱開啟 AOF。

---

## Real-world examples｜實戰案例

### Case 1: The "Hiccup" Every Hour (每小時的卡頓)
**情境**：某電商的購物車服務，工程師發現每到整點附近，API 響應時間就會從 5ms 飆升到 500ms，持續約 1-2 秒。
**診斷**：
*   檢查 Redis Config，發現預設開啟了 RDB `save 3600 1`（一小時內有一筆寫入就存檔）。
*   該 Redis 實例記憶體高達 30GB。
*   執行 `info stats` 發現 `latest_fork_usec` 高達 400,000 (400ms)。
**解決**：
*   **短期**：關閉自動 RDB (`config set save ""`)，依賴 AOF (`everysec`) 進行持久化。
*   **長期**：將該大實例拆分為 Redis Cluster，讓每個分片的記憶體降至 5GB 以下，大幅縮短 fork 時間。

### Case 2: The Infinite Restart (重啟地獄)
**情境**：一個訊息佇列（Message Queue）系統使用 Redis 存儲。某次斷電後，Redis 啟動時卡在 "Loading..." 狀態長達 20 分鐘，導致服務中斷。
**診斷**：
*   配置僅開啟了 AOF (`appendonly yes`)，但**關閉**了混合持久化 (`aof-use-rdb-preamble no`)。
*   AOF 檔案雖然只有 2GB，但包含了數億次的 `LPUSH` 和 `LPOP` 操作記錄。
*   Redis 啟動時必須逐條重播這數億條指令，非常耗時。
**解決**：
*   開啟 `aof-use-rdb-preamble yes`。
*   手動觸發一次 `BGREWRITEAOF`。
*   下次重啟時，Redis 會直接載入 RDB 格式的快照，速度提升至 30 秒內。