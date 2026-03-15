# 生產環境維運與變更安全 | Production Ops & Change Safety

## Mental model｜心智模型

在生產環境操作 MySQL，特別是進行 Schema 變更（DDL）時，你應該將其視為 **「替正在跑馬拉松的選手進行心臟移植手術」**。

1.  **Non-Blocking (非阻塞)**：你不能讓選手停下來（Downtime），也不能讓他跑太慢（Performance degradation）。
2.  **Copy-on-Write & Switch (複製與切換)**：大多數安全的變更策略，本質上都是在旁邊建立一個新的、結構正確的「影子表格（Shadow Table）」，將舊資料同步過去，最後在瞬間交換（Atomic Cutover）。
3.  **Safety Net (安全網)**：所有的變更都假設會失敗。備份（Backup）不是為了存檔，而是為了還原（Restore）；Binlog 不是為了同步，而是為了時光倒流（Point-in-Time Recovery）。

**核心原則**：
> **"Availability is King, Consistency is Queen, and Latency is the Prince."**
> 在維運變更中，永遠優先考慮服務的可用性，避免長時間鎖表（Table Lock）或元數據鎖（Metadata Lock）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Online DDL 策略選擇矩陣
並非所有變更都需要外部工具，請依據 MySQL 版本與資料量選擇策略：

*   **MySQL 8.0+ Instant DDL**:
    *   **適用場景**：新增欄位（Add Column）且設為 Default NULL 或常數、修改 ENUM 定義（Append only）。
    *   **優點**：瞬間完成，只修改 Metadata，不重建表格。
    *   **限制**：不能刪除欄位、不能改變欄位順序、不能修改資料型態。
*   **gh-ost (GitHub Online Schema Transitions)**:
    *   **適用場景**：大表（GB~TB 級別）的複雜變更。
    *   **機制**：**Triggerless**。讀取 Binary Log 來同步資料到影子表。
    *   **優點**：對主庫負載影響最小（解耦），可隨時暫停，不產生 Lock 爭用。
    *   **實務首選**：目前業界大流量場景的標準解法。
*   **pt-online-schema-change (Percona Toolkit)**:
    *   **適用場景**：舊版 MySQL 或無法存取 Binlog 的環境。
    *   **機制**：**Trigger-based**。在原表上建立 Trigger 同步寫入。
    *   **缺點**：Trigger 會在每次寫入時增加 Overhead，且發生死鎖（Deadlock）機率較高。

### 2. Point-in-Time Recovery (PITR) 架構
單純的 `mysqldump` 或 Snapshot 是不夠的。
*   **Full Backup**: 每天/每週一次（如 Percona XtraBackup, AWS RDS Snapshot）。
*   **Binlog Retention**: 確保 Binary Log 保留時間（`binlog_expire_logs_seconds`）長於全備份間隔，通常建議保留 7-14 天。
*   **Recovery Path**: 全備份還原 -> 重放 Binlog 到指定時間點（Position/GTID）。

### 3. VIP / DNS 切換與連接排空 (Connection Draining)
在進行主從切換（Failover）或重大維護時：
*   不要直接依賴 IP 硬編碼。
*   使用 **ProxySQL** 或 **HAProxy** 中間層，或 DNS/Virtual IP。
*   **Graceful Shutdown**: 應用程式端應實作重試機制與連接池的 Graceful Shutdown，避免在 DB 切換瞬間產生大量 5xx 錯誤。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Metadata Lock (MDL) Storm
*   **現象**：你以為 `ALTER TABLE` 會很快（例如只是改個 comment），結果卡住，後續所有 `SELECT` 全部堆積，導致 DB 連線數爆滿，服務當機。
*   **原因**：有一個長事務（Long Running Transaction）正在讀寫該表，DDL 為了拿排他鎖（Exclusive Lock）進入等待，而 MySQL 的鎖機制是「寫鎖優先」，導致後面的讀取全部被擋在 DDL 之後。
*   **解法**：執行 DDL 前，務必檢查 `SHOW PROCESSLIST`，殺掉長事務，或設定 `lock_wait_timeout` 為較短時間（如 5秒），拿不到鎖就放棄，不要排隊。

### 2. 忽略 Replication Lag (主從延遲)
*   **現象**：使用工具跑 Online DDL 時，主庫沒事，但從庫（Replica）延遲飆升到數小時。
*   **原因**：DDL 工具回填資料的速度太快，產生大量 Binlog，單執行緒的 Replica SQL Thread 來不及消化。
*   **解法**：使用 `gh-ost` 或 `pt-osc` 時，設定 `--max-lag` 參數。當偵測到 Replica 延遲超過閾值（如 1秒）時，工具會自動暫停寫入，等待追上。

### 3. 磁碟空間估算錯誤
*   **現象**：執行 Online DDL 到 90% 時，磁碟滿了（Disk Full），DB Crash。
*   **原因**：Online DDL 本質是 Copy Table。如果你有一個 500GB 的表，變更期間你至少需要額外 500GB + Binlog 空間。
*   **解法**：變更前檢查 `Disk Free Space > Table Size * 2`。

### 4. 在尖峰時刻直接執行 `DROP INDEX` 或 `ADD INDEX`
*   即使是 Online DDL，建立索引仍極耗 CPU 和 IO。在 QPS 高峰期執行會導致回應變慢。

---

## Checklists & workflows｜檢查清單與流程

### Pre-Change Checklist (變更前檢查)

- [ ] **Disk Space**: 剩餘空間是否大於目標 Table Size 的 2 倍？
- [ ] **Workload**: 當前是否為業務離峰時間？CPU/IO Util 是否低於 50%？
- [ ] **Long Transactions**: 檢查 `information_schema.INNODB_TRX`，確認無長事務執行中。
- [ ] **Replication**: 檢查 `Seconds_Behind_Master` (或 `Seconds_Behind_Source`) 是否為 0。
- [ ] **Tool Config**: 若使用 `gh-ost`/`pt-osc`，是否設定了 `--max-lag` 與 `--chunk-size`？
- [ ] **Dry Run**: 是否已在 Staging 環境演練過完全相同的 DDL？
- [ ] **Backup**: 確認最近一次備份成功，且 Binlog 連續。

### Emergency Response (緊急應變)

- [ ] **Kill DDL**: 若發現服務異常，第一時間 `Ctrl+C` 停止 DDL 工具，或在 DB 內 `KILL <ddl_process_id>`。
- [ ] **Check MDL**: 若 DDL 被殺掉後 DB 仍卡住，檢查是否有殘留的 Metadata Lock 等待。
- [ ] **Rollback**: 若資料已損壞，啟動 PITR 流程（需預先寫好 SOP）。

---

## Real-world examples｜實戰案例

### Case 1: 使用 gh-ost 安全地為 1TB 表格新增欄位

**情境**：User 表有 1TB，需要新增 `preferred_language` 欄位。直接 `ALTER` 會鎖表數小時。

**Recommended Command (gh-ost)**:
```bash
gh-ost \
  --max-load=Threads_running=25 \
  --critical-load=Threads_running=1000 \
  --chunk-size=1000 \
  --max-lag-millis=1500 \
  --conf=/etc/mysql/debian.cnf \
  --host=127.0.0.1 \
  --database=prod_db \
  --table=users \
  --alter="ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'" \
  --switch-to-rbr \
  --cut-over=default \
  --exact-rowcount \
  --execute
```

**關鍵參數解析**：
*   `--max-load`: 當 DB 並發執行緒超過 25 時，暫停遷移。
*   `--max-lag-millis`: 當 Replica 延遲超過 1.5 秒時，暫停遷移（保護讀取流量）。
*   `--switch-to-rbr`: 確保 Binlog 格式正確。
*   `--execute`: 真正執行（否則只是 Dry Run）。

### Case 2: 誤刪資料的 PITR 救援流程

**情境**：工程師在 `14:00` 誤執行了 `DELETE FROM orders` 且忘了加 `WHERE`。

**救援 SOP**:
1.  **Stop**: 停止應用寫入（避免更多資料混入）。
2.  **Locate**: 找出誤刪操作在 Binlog 中的具體位置（Position/GTID）。
    ```sql
    -- 使用 mysqlbinlog 查找 DELETE 語句的時間點
    mysqlbinlog --start-datetime="2023-10-27 13:55:00" mysql-bin.000123 | grep -i "DELETE FROM orders"
    ```
3.  **Restore Base**: 找回最近一次全備份（例如 `02:00` 的 Snapshot）並還原到一台**新機器**。
4.  **Replay Binlog**: 重放 `02:00` 到 `13:59:59` (誤刪前一刻) 的 Binlog。
    ```bash
    mysqlbinlog --start-datetime="2023-10-27 02:00:00" \
                --stop-datetime="2023-10-27 13:59:59" \
                mysql-bin.000123 | mysql -u root -p
    ```
5.  **Verify & Switch**: 驗證資料回來了，將應用程式連線切換到新機器。