# 生產環境維運與故障排除 / Production Operations & Troubleshooting

## Mental model｜心智模型

在維運 Redis 時，必須時刻謹記其核心架構特徵：**單執行緒事件迴圈 (Single-threaded Event Loop)**。

可以將 Redis 想像成一個**極高速的單窗口售票處**：
1.  **排隊機制**：所有請求（Command）都在同一個隊列中排隊。
2.  **序列處理**：一次只能處理一個請求。
3.  **阻塞效應**：如果某個請求處理時間過長（例如處理大 Key 或執行 O(N) 複雜度指令），後面的所有請求都會被卡住，導致系統整體的 Latency 飆升。

因此，故障排除的核心思維通常圍繞在兩個維度：
*   **CPU/Latency**：是否有「胖子（Slow Command）」堵住了門口？
*   **Memory**：記憶體是否洩漏、碎片化（Fragmentation）過高，或觸發了 Swap（這對 Redis 是致命的）？

To operate Redis effectively, adopt the **Single-threaded Event Loop** mental model. Imagine a high-speed toll booth with only one lane. If one car (command) stalls, the entire highway stops. Troubleshooting revolves around identifying what is blocking the lane (Latency) and ensuring the toll booth has enough resources (Memory) without swapping to disk.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 監控黃金指標 (Golden Signals for Redis)
不要只看 CPU 使用率，必須監控以下特定指標：
*   **`instantaneous_ops_per_sec`**: 吞吐量 (Throughput)。
*   **`used_memory_rss` vs `used_memory`**: 觀察 `mem_fragmentation_ratio`。如果 > 1.5 代表碎片化嚴重；如果 < 1 代表可能發生了 Swap。
*   **`evicted_keys`**: 如果此數值持續增加，代表記憶體不足，正在依賴 Eviction Policy 刪除資料。
*   **`rejected_connections`**: 達到 `maxclients` 上限，應用程式可能連不上。
*   **`latest_fork_usec`**: RDB/AOF rewrite 時 Fork 子進程的耗時，過長會導致主執行緒阻塞。

### 2. 善用內建診斷工具 (Built-in Diagnostic Tools)
Redis 本身提供了強大的自我診斷指令，這是排查問題的第一步：
*   **Slowlog**: 設定 `slowlog-log-slower-than 10000` (10ms) 甚至更低，並定期檢查 `SLOWLOG GET` 找出效能殺手。
*   **Latency Doctor**: 使用 `LATENCY DOCTOR` 指令，Redis 會自動分析延遲峰值並給出人類可讀的建議報告。
*   **Memory Doctor**: 使用 `MEMORY DOCTOR` 快速診斷記憶體問題。
*   **Watchdog**: 在極端情況下（Redis Crash），啟用 Watchdog 可以捕捉 stack trace。

### 3. Linux 核心參數調優 (Kernel Tuning)
Redis 在生產環境非常依賴 OS 設定，未調優的 Linux 會導致效能低落或數據遺失：
*   **Disable THP (Transparent Huge Pages)**: 這是最常見的效能殺手。務必執行 `echo never > /sys/kernel/mm/transparent_hugepage/enabled`。
*   **Overcommit Memory**: 設定 `vm.overcommit_memory = 1`，避免 Fork 時因為申請不到記憶體而導致備份失敗（BGSAVE error）。
*   **TCP Backlog**: 增加 `net.core.somaxconn`，避免高併發連線時被 OS 拒絕。

### 4. 安全的備份與還原策略 (Safe Backup & Restore)
*   **RDB vs AOF**: 生產環境建議混合使用（RDB 做快照，AOF 做增量）。
*   **Off-site Backup**: 不要只依賴本地檔案，定期將 RDB 檔傳送到 S3 或異地儲存。
*   **Restore Drill**: 每季至少演練一次還原流程，確保備份檔是有效的，且你知道還原需要多久（RDB 載入速度通常比 AOF 快）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 使用 `KEYS *` 指令 (The `KEYS` Command)
*   **Anti-pattern**: 在生產環境使用 `KEYS pattern` 來搜尋 Key。
*   **Consequence**: 這是 O(N) 操作。在單執行緒模型下，當 Key 數量達百萬級時，這會導致 Redis 凍結數秒甚至數分鐘，期間所有服務不可用。
*   **Solution**: 使用 `SCAN` 指令進行游標式迭代，或在應用層維護索引。

### 2. 忽視 Big Keys (Ignoring Big Keys)
*   **Anti-pattern**: 儲存超大的 Hash、List 或 Set（例如一個 Key 內有 100 萬個元素）。
*   **Consequence**: 讀取、刪除這些 Key 時會造成長時間阻塞。刪除一個 1GB 的 Key 等同於同步釋放 1GB 記憶體，會卡住主執行緒。
*   **Solution**: 使用 `redis-cli --bigkeys` 定期掃描。刪除時使用 `UNLINK`（非同步刪除）代替 `DEL`。

### 3. 允許 Swap (Allowing Swap)
*   **Anti-pattern**: 沒有設定 `maxmemory`，或者 OS 的 Swap 設定不當。
*   **Consequence**: Redis 是基於記憶體的資料庫，一旦發生 Swap，效能會從微秒級（μs）掉到毫秒級（ms）甚至秒級，基本上等同於服務當機。
*   **Solution**: 嚴格設定 `maxmemory`，並確保 OS 層級盡量不使用 Swap (`vm.swappiness` 設為極低值)。

### 4. 連線風暴 (Connection Storms)
*   **Anti-pattern**: 應用程式沒有使用 Connection Pool，或者在 Redis 重啟/網路抖動後，所有客戶端同時發起重連。
*   **Consequence**: CPU 飆高處理握手，導致正常請求無法處理。
*   **Solution**: 強制使用連線池（Connection Pooling），並實作 Exponential Backoff（指數退避）重連機制。

---

## Checklists & workflows｜檢查清單與流程

### Deployment Checklist (上線前檢查)

- [ ] **Memory Limit**: `maxmemory` 已設定（建議保留 20-30% 實體記憶體給 OS 與 Fork 使用）。
- [ ] **Eviction Policy**: 確認 `maxmemory-policy` 符合業務需求（如 `allkeys-lru` 或 `volatile-lru`）。
- [ ] **Kernel Tuning**: THP 已關閉 (`never`)，`vm.overcommit_memory = 1`。
- [ ] **Security**: `requirepass` 已設定，危險指令（`FLUSHALL`, `KEYS`, `CONFIG`）已透過 `rename-command` 禁用或改名。
- [ ] **Persistence**: RDB/AOF 策略已定，且確認磁碟 I/O 足夠。
- [ ] **Slowlog**: `slowlog-log-slower-than` 已設定（建議 1000-10000 微秒）。

### Troubleshooting Workflow (故障排查流程)

當發生 Latency 飆高或連線逾時，請依序執行：

1.  **Check Liveness**: `redis-cli ping` 能通嗎？回應時間多少？
    *   *Tool*: `redis-cli --latency` (即時監控延遲)。
2.  **Check Slowlog**: 是否有特定指令卡住？
    *   *Command*: `SLOWLOG GET 10`。
3.  **Check Resources**:
    *   記憶體：`INFO memory` (看 `mem_fragmentation_ratio`, `evicted_keys`)。
    *   CPU：`top` (看是 sys 高還是 user 高？sys 高可能是頻繁 IO 或 Swap)。
    *   網路：`netstat` / `ss` (看是否有大量 `TIME_WAIT` 或 `CLOSE_WAIT`)。
4.  **Check Clients**: 是否有異常連線？
    *   *Command*: `CLIENT LIST` (尋找 `omem` 很大的連線，代表 Output Buffer 堆積)。
5.  **Check Logs**: 查看 Redis Log，尋找 "OOM", "Background save error", "Can't save in background" 等關鍵字。

---

## Real-world examples｜實戰案例

### Case 1: The "Mysterious" Timeout (O(N) Command Issue)
**情境**：每週五下午 2 點，API 延遲突然飆升，Redis CPU 100%，持續 30 秒後恢復。
**排查**：
1.  查看監控，發現 `instantaneous_ops_per_sec` 在該時段沒有顯著增加，但 Latency 極高。
2.  執行 `SLOWLOG GET`，發現大量 `KEYS user_*` 指令。
3.  **原因**：某個 Cron Job 腳本為了統計用戶數，直接跑了 `KEYS` 指令。
4.  **解決**：修改腳本改用 `SCAN`，並在 Redis Config 中將 `KEYS` 指令 rename 掉，防止再次發生。

### Case 2: OOM & Copy-on-Write (Memory Issue)
**情境**：Redis 實體記憶體 16GB，`maxmemory` 設為 12GB。某次觸發 BGSAVE（RDB 備份）時，Redis 突然被 OS 的 OOM Killer 殺掉。
**排查**：
1.  系統 Log (`dmesg`) 顯示 Redis process 被 kill。
2.  分析原因：Redis 使用了 12GB，當 BGSAVE 發生時，會 `fork()` 一個子進程。
3.  雖然 Linux 有 Copy-on-Write (CoW) 機制，但如果寫入流量很大，CoW 會導致記憶體使用量激增（最壞情況需 24GB）。
4.  **解決**：
    *   調降 `maxmemory` 至 8-10GB，預留更多緩衝給 CoW。
    *   啟用 `vm.overcommit_memory = 1` 確保 fork 不會因為申請不到虛擬記憶體而失敗（雖然不能防止 OOM，但能避免 fork 失敗）。

### Case 3: Network Buffer Overflow (Client Issue)
**情境**：Master 節點運作正常，但某個 Slave 節點不斷斷線重連，導致全量同步（Full Resync）反覆發生，頻寬被吃滿。
**排查**：
1.  查看 Master 的 Log，顯示 `Client scheduled to be closed...`。
2.  檢查 `client-output-buffer-limit` 設定。
3.  **原因**：Slave 同步速度慢於 Master 寫入速度，導致 Master 為該 Slave 保留的 Output Buffer 溢出（超過預設限制），Master 主動斷開連線。
4.  **解決**：增加 `client-output-buffer-limit slave` 的限制值，或優化 Slave 的網路頻寬/磁碟效能。