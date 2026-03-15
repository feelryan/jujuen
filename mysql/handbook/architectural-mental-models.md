# 核心架構與心智模型 | Core Architecture & Mental Models

建立對 MySQL (特別是 InnoDB 引擎) 的正確心智模型，是進行效能調優與故障排除的基礎。本章節將揭開 MySQL 的「黑盒子」，解釋邏輯架構、ACID 的實作代價以及 Buffer Pool 的運作機制。

## Mental model｜心智模型

要掌握 MySQL，你不能將其視為一個單一的整體，而應該建立以下三個關鍵的心智模型：

### 1. 雙層架構：大腦與手腳 (The Two-Layer Architecture)
MySQL 由兩層組成，這解釋了為什麼同樣的 SQL 在不同引擎下表現截然不同。

*   **Server Layer (大腦)**：負責連接處理、權限驗證、SQL 解析 (Parser) 與查詢優化 (Optimizer)。它決定「**要做什麼 (What)**」以及「**執行計畫 (Plan)**」。
*   **Storage Engine Layer (手腳)**：負責數據的儲存與提取（如 InnoDB, MyISAM）。它負責「**如何做 (How)**」以及具體的磁碟 I/O 操作。
    *   *Key Insight*: Server 層不管理 Transaction (除了 Binlog)，ACID 特性主要由 InnoDB 引擎層保證。

### 2. 記憶體優先與延遲持久化 (Memory First, Disk Later)
MySQL (InnoDB) 的設計哲學是「假裝自己是個 In-Memory Database」。

*   **Buffer Pool 是核心**：所有的讀寫操作都**必須**先在 Buffer Pool (記憶體) 中完成。如果數據不在記憶體，必須先從磁碟載入。
*   **Dirty Pages (髒頁)**：當你執行 `UPDATE` 時，MySQL 僅修改記憶體中的 Page，標記為「髒頁」。真正的磁碟寫入 (Flush) 是由後台執行緒異步完成的。
*   *Key Insight*: 寫入速度快是因為它寫的是記憶體（和順序寫入的 Log），而不是隨機寫入數據檔。

### 3. WAL (Write-Ahead Logging) 與日誌鐵三角
為了保證上述「記憶體優先」不會因為斷電而遺失數據，MySQL 嚴格遵循 **WAL** 原則：**修改數據前，先寫日誌**。

*   **Redo Log (重做日誌)**：InnoDB 特有。物理日誌。記錄「哪個 Page 改了什麼」。用於 **Crash Recovery** (崩潰恢復)。確保 **Durability (持久性)**。
*   **Undo Log (撤銷日誌)**：InnoDB 特有。邏輯日誌。記錄「如何回滾到修改前」。用於 **Transaction Rollback** 與 **MVCC** (多版本並發控制)。確保 **Atomicity (原子性)**。
*   **Binlog (歸檔日誌)**：Server 層共有。邏輯日誌。記錄 SQL 語句或原始數據變更。用於 **Replication** (主從複製) 與 Point-in-Time Recovery。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Buffer Pool 配置策略
Buffer Pool 是影響 MySQL 效能最關鍵的變數。
*   **Dedicated Server**: 如果機器專門跑 MySQL，將 `innodb_buffer_pool_size` 設為實體記憶體的 **60% - 80%**。
*   **Chunk Size**: 確保 `innodb_buffer_pool_instances` > 1 (通常設為 4 或 8)，以減少多執行緒下的記憶體結構鎖競爭。

### 2. 「雙 1」設定 (The "Double 1" Standard)
在生產環境中，為了保證數據絕對不丟失（ACID 中的 D），標準配置是：
*   `innodb_flush_log_at_trx_commit = 1`: 每次事務提交都強制刷寫 Redo Log 到磁碟。
*   `sync_binlog = 1`: 每次事務提交都強制刷寫 Binlog 到磁碟。
*   *Trade-off*: 這會限制寫入效能（受限於磁碟 IOPS）。如果業務允許極少量數據丟失（如日誌分析系統），可改為 `0` 或 `2` 以獲得數倍的寫入效能提升。

### 3. 預熱機制 (Cache Warming)
重啟 MySQL 後，Buffer Pool 是空的，此時效能極差（因為所有請求都變成 Disk I/O）。
*   **Pattern**: 利用 `innodb_buffer_pool_dump_at_shutdown` 和 `innodb_buffer_pool_load_at_startup`。這會保存記憶體中的熱點 Page 指針，重啟後自動將熱數據加載回記憶體。

### 4. 讀寫分離的延遲認知 (Replication Lag Awareness)
由於 Binlog 是異步（或半同步）傳遞的，讀寫分離架構下，從庫 (Slave) 永遠存在延遲。
*   **Pattern**: 對於「寫後即讀」(Read-your-writes) 的業務場景（如用戶剛修改完個人資料），必須強制讀主庫 (Master)，或使用 Cache 層，而不能依賴從庫。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤解 Query Cache
*   **Anti-pattern**: 依賴 MySQL Query Cache (QC) 來提升效能。
*   **Reality**: QC 在高併發寫入環境下是嚴重的鎖競爭瓶頸。MySQL 8.0 已徹底移除此功能。請依賴應用層 Cache (Redis) 或 ProxySQL。

### 2. 忽視長事務 (Long-lived Transactions)
*   **Pitfall**: 開啟事務後，進行耗時的運算或外部 API 呼叫，遲遲不 Commit。
*   **Consequence**: 這會導致 **Undo Log** 無法清理 (Purge)，造成 ibdata1 檔案無限膨脹，並拖慢所有查詢的 MVCC 版本判斷。

### 3. 混淆 Delete 與磁碟空間釋放
*   **Pitfall**: 執行 `DELETE FROM table` 後，發現磁碟空間沒有減少。
*   **Reality**: `DELETE` 只是在 B+Tree 頁面上打上「已刪除」標記。空間會被重複利用，但不會立即退還給作業系統。
*   **Fix**: 需要執行 `OPTIMIZE TABLE` (會鎖表重建模) 或使用 `gh-ost` / `pt-online-schema-change` 來回收物理空間。

### 4. 錯誤的 IO 容量評估
*   **Pitfall**: 在雲端環境使用低 IOPS 的磁碟（如 AWS gp2 小容量）跑高併發資料庫。
*   **Reality**: 當 Redo Log 寫入速度超過磁碟能力，或 Checkpoint 跟不上髒頁產生速度時，MySQL 會觸發「Furious Flushing」(瘋狂刷髒)，導致系統瞬間卡死。

---

## Checklists & workflows｜檢查清單與流程

### New Instance Architecture Checklist (新實例架構檢查)
在將 MySQL 投入生產環境前，請檢查以下架構參數：

- [ ] **Engine Verification**: 確認預設引擎為 `InnoDB`，且沒有意外建立的 `MyISAM` 資料表。
- [ ] **Memory Sizing**: `innodb_buffer_pool_size` 是否已設為 RAM 的 60-80%？
- [ ] **Log File Size**: `innodb_log_file_size` (Redo Log) 是否足夠大？(建議至少能容納 1 小時的寫入量，通常 1GB - 4GB)。
- [ ] **Durability**: 確認 `sync_binlog` 和 `innodb_flush_log_at_trx_commit` 的值符合業務對數據安全的要求。
- [ ] **Character Set**: 確認 Server 與 Database 層級皆使用 `utf8mb4`。
- [ ] **IO Capacity**: 確認 `innodb_io_capacity` 設定符合底層磁碟的 IOPS 能力。

### Performance Bottleneck Decision Tree (效能瓶頸判斷樹)
當資料庫變慢時，依據架構心智模型快速定位：

1.  **CPU 高嗎？**
    *   **Yes**: 通常是 Server Layer 問題。檢查慢查詢 (Slow Query)、索引缺失、或掃描行數過多。
    *   **No**: 進入 I/O 檢查。
2.  **Disk I/O 高嗎？**
    *   **Yes (Reads)**: Buffer Pool Hit Rate 過低。記憶體不足或全表掃描 (Full Table Scan) 把熱數據擠出去了。
    *   **Yes (Writes)**: Redo Log 太小導致頻繁 Checkpoint，或磁碟 IOPS 瓶頸。
3.  **CPU 和 I/O 都不高，但 Query 很慢？**
    *   **Locking**: 檢查 Row Lock (InnoDB) 或 Metadata Lock (Server Layer)。
    *   **Network**: 檢查應用程式與 DB 間的延遲。

---

## Real-world examples｜實戰案例

### 案例 1：更新語句的生命週期 (The Lifecycle of an UPDATE)
理解一條 SQL `UPDATE users SET age = 30 WHERE id = 1;` 是如何在架構中流動的：

1.  **Server Layer**:
    *   解析器驗證 SQL 語法。
    *   優化器決定使用 `PRIMARY KEY (id)` 索引。
    *   執行器呼叫 InnoDB 引擎介面。
2.  **InnoDB Layer (Memory)**:
    *   檢查 `id=1` 的 Page 是否在 Buffer Pool？若否，從磁碟讀入。
    *   **寫 Undo Log**: 將 `age` 舊值寫入 Undo Log (為了回滾)。
    *   **更新記憶體**: 修改 Buffer Pool 中的 Page (變為髒頁)。
    *   **寫 Redo Log**: 將「Page X 偏移量 Y 改為 30」寫入 Redo Log Buffer。
3.  **Commit 階段 (Persistence)**:
    *   **Prepare**: Redo Log 刷入磁碟 (狀態為 Prepare)。
    *   **Binlog**: Server 層將 SQL/變更寫入 Binlog 並刷入磁碟。
    *   **Commit**: 在 Redo Log 標記 Commit。
    *   *此時，數據已安全，但主數據檔 (.ibd) 尚未修改。*
4.  **Checkpoint (Background)**:
    *   後台執行緒稍後將 Buffer Pool 的髒頁寫入 `.ibd` 檔案。

### 案例 2：崩潰恢復的代價 (The Cost of Crash Recovery)
**情境**: 一台寫入量極大的 MySQL 伺服器意外斷電。重啟後，DB 狀態顯示 "Starting"，且持續了 10 分鐘無法連線。
**原因**: `innodb_log_file_size` 設得很大 (例如 10GB)，且斷電前有大量髒頁未刷入磁碟。
**機制**: MySQL 重啟時，InnoDB 必須讀取 Redo Log，將所有未寫入磁碟的變更「重做 (Redo)」一遍到記憶體，然後掃描 Undo Log 決定哪些未提交事務需要「回滾」。
**Lesson**: Redo Log 越大，寫入效能越好（Checkpoint 頻率低），但崩潰恢復時間越長。這是一個典型的架構 Trade-off。