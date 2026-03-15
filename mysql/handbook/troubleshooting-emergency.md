# 故障排除與緊急應變 | Troubleshooting & Emergency Response / Troubleshooting & Emergency Response

## Mental model｜心智模型

在面對 MySQL 生產環境故障時，最重要是區分 **「資源耗盡 (Resource Saturation)」** 與 **「資源爭用 (Resource Contention)」**。

1.  **急診室檢傷分類 (Triage Protocol)**：
    *   **止血 (Stop the bleeding)**：優先恢復服務可用性（Availability），例如 Kill 掉導致 Deadlock 的連線，或是重啟服務（最後手段），而不是當下立刻追求完美的 Root Cause Analysis。
    *   **保留現場 (Preserve the crime scene)**：在重啟或 Kill 之前，盡可能快照當下的狀態（Processlist, InnoDB Status），否則重啟後證據全失。

2.  **資源視角 (The USE Method)**：
    *   **CPU 飆高**：通常意味著 **效率低下的查詢 (Inefficient Queries)**，例如全表掃描 (Full Table Scan) 或記憶體內排序。
    *   **IO 飆高**：通常意味著 **Buffer Pool 命中率低** 或 **寫入量過大** (Checkpoint lag)。
    *   **連線數爆滿 (Connection Storm)**：通常是 **應用程式層的連線洩漏 (Leak)** 或 **資料庫鎖等待 (Lock Wait)** 導致連線積壓，而非單純流量太大。

3.  **鎖視角 (Locking View)**：
    *   資料庫看起來「卡住」不動，CPU 使用率卻很低？這通常是 **鎖爭用 (Lock Contention)**。一個長事務 (Long Transaction) 持有了鎖，導致後續數百個請求排隊等待 (Queueing)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 快速診斷三板斧 (The Diagnostic Trinity)
在緊急狀況下，不要漫無目的地猜測，依序執行以下檢查：

*   **Who is running?**
    使用 `SHOW PROCESSLIST` 或更現代的 `SELECT * FROM sys.session` 查看當前活躍的連線。
*   **What is blocking?**
    使用 `SELECT * FROM sys.innodb_lock_waits` 快速找出誰鎖住了誰。
*   **What is the engine doing?**
    使用 `SHOW ENGINE INNODB STATUS` 查看深層的 Deadlock 資訊與 Buffer Pool 狀態。

### 2. Connection Storm 應對模式
當發生 `Too many connections` 錯誤時：
*   **區分 Sleep vs Active**：如果大部分是 `Sleep`，這是應用程式 Connection Pool 設定不當或未釋放連線。如果大部分是 `Query`，則是資料庫處理過慢導致堆積。
*   **緊急保留通道**：MySQL 8.0+ 支援 `admin_port`，即使主埠口滿載，管理員仍可透過此埠口登入進行維護。
*   **使用 `pt-kill`**：Percona Toolkit 的 `pt-kill` 是自動化殺掉超時查詢或特定特徵查詢的神器，比手動 Kill 安全且快速。

### 3. 慢查詢分析 (Slow Query Analysis)
*   **不要只看單條 SQL**：單條慢查詢可能只是受害者（被別人鎖住）。
*   **聚合分析**：使用 `pt-query-digest` 分析 Slow Query Log，關注 **Execution Time / Call Count**（平均執行時間）與 **Rows Examined vs Rows Sent**（掃描行數效率）。
*   **Performance Schema**：利用 `sys.statement_analysis` 視圖，這是即時且低開銷的效能分析來源。

```sql
-- 快速找出最消耗資源的 Top 10 SQL
SELECT query, exec_count, avg_latency, rows_sent_avg, rows_examined_avg 
FROM sys.statement_analysis 
ORDER BY avg_latency DESC 
LIMIT 10;
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目重啟 (Blind Restart)
*   **陷阱**：遇到問題第一反應是 `systemctl restart mysqld`。
*   **後果**：Buffer Pool 被清空（導致重啟後效能更差，即 Cold Cache），且所有鎖等待與執行緒狀態的現場資訊遺失，無法追查根因。

### 2. 忽略 `Kill` 的代價
*   **陷阱**：對正在進行大量寫入（如 `ALTER TABLE` 或大批次 `UPDATE`）的連線執行 `KILL`。
*   **後果**：MySQL 必須執行 **Rollback** 操作，這可能比讓它執行完還要久，且期間可能會佔用大量資源。

### 3. 依賴 GUI 工具進行緊急排查
*   **陷阱**：在網路擁塞或資料庫高負載時，依賴 Workbench / Navicat 等重型 GUI 工具。
*   **後果**：GUI 工具本身可能發送額外的 metadata 查詢加重負載，且連線可能逾時。**請熟練 CLI 指令。**

### 4. 錯誤解讀 CPU 100%
*   **陷阱**：看到 CPU 100% 就認為要升級硬體。
*   **後果**：通常是一條缺少索引的 SQL 導致。硬體升級只能暫時緩解，無法解決 O(N) 的掃描問題。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 Emergency Response Workflow (緊急應變流程)

#### Phase 1: Assessment (評估現狀)
- [ ] **能不能連線？**
    - 若不能：檢查 Server 是否存活、Port 是否被防火牆擋住、是否 `Too many connections`。
    - 若能：進入 Phase 2。
- [ ] **系統負載 (Load Average) 如何？**
    - 高 CPU：重點查 Slow Query。
    - 高 IO Wait：重點查 Checkpoint、Redo Log、大量寫入。
    - 低資源使用但回應慢：重點查 Locks。

#### Phase 2: Diagnosis & Mitigation (診斷與緩解)

**情境 A：CPU 飆高 (High CPU)**
- [ ] 執行 `SHOW FULL PROCESSLIST`，尋找 `State` 為 `Sending data` 或 `Creating sort index` 的長時間查詢。
- [ ] 若發現特定 SQL 重複出現且執行時間長：
    - [ ] **Action**: 暫時 Kill 掉該 Query (使用 `CALL sys.ps_thread_id(CONNECTION_ID);` 配合 `KILL`)。
    - [ ] **Action**: 檢查該 SQL 的 `EXPLAIN` 執行計畫，確認是否缺少索引。

**情境 B：連線數爆滿 (Connection Spike)**
- [ ] 執行 `SELECT COMMAND, COUNT(*) FROM information_schema.processlist GROUP BY COMMAND;`
- [ ] 若大量 `Sleep`：
    - [ ] **Action**: 調整應用程式 Connection Pool 設定，或臨時調降 `wait_timeout` 回收閒置連線。
- [ ] 若大量 `Query` 且狀態為 `Locked`：
    - [ ] **Action**: 找出持有鎖的源頭 (Blocker)。

**情境 C：鎖等待 (Lock Wait / Deadlock)**
- [ ] 查詢 `sys.innodb_lock_waits`：
    ```sql
    SELECT waiting_pid, waiting_query, blocking_pid, blocking_query 
    FROM sys.innodb_lock_waits;
    ```
- [ ] **Action**: Kill 掉 `blocking_pid` (持有鎖的那個連線)。

#### Phase 3: Post-Mortem (事後分析)
- [ ] 匯出 Slow Query Log 並使用 `pt-query-digest` 分析。
- [ ] 檢查 Error Log (`/var/log/mysqld.log`) 是否有硬體錯誤或 Crash 紀錄。
- [ ] 檢討是否需要添加索引或調整 Schema。

---

## Real-world examples｜實戰案例

### Case 1: The "Death by Missing Index" (索引缺失導致 CPU 100%)

**症狀**：
週五下午，監控顯示 DB CPU 突然飆升至 99%，應用程式回應逾時 (504 Gateway Time-out)。

**排查**：
1.  登入 MySQL CLI，執行 `SHOW PROCESSLIST;`。
2.  發現數十個 `SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC` 正在執行，狀態為 `Using filesort`。
3.  檢查 Schema，發現 `orders` 表有 500 萬筆資料，但 `status` 欄位沒有索引。

**處置**：
1.  **止血**：手動 Kill 掉執行超過 30 秒的查詢。
2.  **修復**：緊急執行 `CREATE INDEX idx_status_created ON orders(status, created_at);` (注意：MySQL 8.0+ 支援 Online DDL，但高負載下仍需謹慎，建議使用 `pt-online-schema-change` 或 `gh-ost`，若緊急且表不大可直接執行)。
3.  **結果**：CPU 降回 10%。

### Case 2: The "Metadata Lock" Pile-up (元數據鎖風暴)

**症狀**：
網站完全卡死，所有與 `users` 表相關的查詢都處於 `Waiting for table metadata lock` 狀態。

**排查**：
1.  執行 `SHOW PROCESSLIST` 看到大量查詢卡在 Metadata Lock。
2.  這通常是因為有人在執行 DDL (如 `ALTER TABLE`)，或者有一個長事務查詢了該表後一直沒 Commit，接著另一個連線試圖修改表結構或 Truncate。
3.  使用 `SELECT * FROM sys.schema_table_lock_waits` 找到源頭。
4.  發現一位開發者在 Production 環境開啟了一個 Transaction 查詢資料，然後去吃午餐了，沒有 Commit/Rollback。

**處置**：
1.  **止血**：Kill 掉該開發者的閒置連線 (Sleep 狀態但持有 Transaction)。
2.  **結果**：後方排隊的數百個查詢瞬間釋放並執行完畢。

### Case 3: The Connection Leak (連線洩漏)

**症狀**：
應用程式報錯 `Too many connections`，重啟應用程式後恢復，但 1 小時後再次發生。

**排查**：
1.  DBA 透過 Admin Port 登入。
2.  查詢 Processlist，發現 2000 個連線中有 1950 個處於 `Sleep` 狀態，且 `Time` (閒置時間) 都在增加。
3.  這表示應用程式開啟了連線卻沒有正確 `Close()` 或歸還給 Pool。

**處置**：
1.  **止血**：臨時將全域 `wait_timeout` 從預設的 28800 (8小時) 改為 300 (5分鐘)。
    ```sql
    SET GLOBAL wait_timeout = 300;
    SET GLOBAL interactive_timeout = 300;
    ```
2.  **根治**：通知開發團隊修復程式碼中的 `finally { conn.close(); }` 邏輯或 Connection Pool 設定。