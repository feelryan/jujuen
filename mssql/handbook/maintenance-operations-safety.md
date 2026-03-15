# 維運護理：統計資訊、維護與安全 / Maintenance, Operations & Security Configuration

## Mental model｜心智模型

在深入操作之前，我們需要建立關於 SQL Server 維運的三個核心心智模型：

1.  **優化器是導航系統，統計資訊是地圖 (The Optimizer is the GPS, Statistics are the Map)**
    SQL Server 的 Query Optimizer 依賴「統計資訊（Statistics）」來決定執行計畫。就像 GPS 導航一樣，如果地圖（統計資訊）過期了，導航（優化器）就會帶你走遠路（Table Scan），而不是捷徑（Index Seek）。維護的核心不在於「讓硬碟重組」，而在於「確保優化器擁有最新、最準確的資料分佈情報」。

2.  **熵增定律與碎片化 (Entropy & Fragmentation)**
    資料庫是動態的。隨著 CRUD 操作，資料頁（Data Pages）會產生碎片（Fragmentation）。
    - **邏輯碎片**：資料頁在磁碟上的順序與邏輯順序不一致（增加 IOPS）。
    - **內部碎片**：資料頁留有過多空白空間（浪費記憶體與 Cache）。
    維護工作的本質是對抗熵增，保持資料結構的緊湊性。

3.  **最小權限原則是最後一道防線 (Least Privilege as the Final Line of Defense)**
    不要假設應用程式程式碼是完美的。當 SQL Injection 發生時，應用程式連線帳號的權限決定了攻擊者的破壞半徑。如果該帳號是 `db_owner` 或 `sa`，遊戲就結束了；如果是受限帳號，損害可被控制。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 智慧化索引維護 (Smart Index Maintenance)
不要盲目地每晚重建所有索引。這會導致 Transaction Log 暴漲並浪費資源。
- **採用標準方案**：強烈建議使用社群標準 **Ola Hallengren's Maintenance Solution**，不要自己寫維護 Script。
- **分級策略**：
  - **Fragmentation < 5-10%**：不做任何事。
  - **Fragmentation 10-30%**：執行 `INDEX REORGANIZE`（線上操作，輕量）。
  - **Fragmentation > 30%**：執行 `INDEX REBUILD`（預設離線，企業版可用 `ONLINE=ON`）。

### 2. 統計資訊更新策略 (Statistics Update Strategy)
預設的 `Auto Update Statistics` 對於大表（例如超過 1 億筆）往往反應太慢（觸發門檻約為 20% 變動 + 500 rows）。
- **啟用異步更新**：設定 `AUTO_UPDATE_STATISTICS_ASYNC ON`，避免查詢因為等待統計更新而 Timeout。
- **定期 Full Scan**：對於關鍵大表，安排在離峰時間執行 `UPDATE STATISTICS ... WITH FULLSCAN`。預設的採樣（Sampling）對於資料分佈不均的欄位可能產生誤差。

### 3. 權限隔離模式 (Security Isolation Pattern)
應用程式不應直接存取 Table，或至少不應擁有 DDL 權限。
- **Schema-based Security**：
  建立專屬 Schema（如 `app`），將 Table 放在 `dbo` 或 `data` Schema，Stored Procedures 放在 `app` Schema。
  - 給予 App User 對 `app` Schema 的 `EXECUTE` 權限。
  - 利用 **Ownership Chaining**，讓 SP 存取 Table，但 App User 無法直接 `SELECT/DELETE` Table。
- **Custom Database Roles**：
  建立如 `Role_AppReadWrite` 的角色，只給予必要的 `SELECT, INSERT, UPDATE`，明確拒絕 `TRUNCATE` 或 `DROP`。

### 4. 資料庫完整性檢查 (Integrity Checks)
- **DBCC CHECKDB**：這是不可妥協的。必須定期（每週或每日）執行。
- **備份驗證**：備份檔案本身可能是壞的。加上 `CHECKSUM` 選項進行備份，並定期進行 Restore 測試。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 惡名昭彰的 Shrink Database (The Shrink Demon)
- **Anti-pattern**: 定期執行 `DBCC SHRINKDATABASE` 或 `DBCC SHRINKFILE` 來釋放硬碟空間。
- **Why it's bad**: Shrink 操作會將資料頁搬移到檔案前端，導致**極度嚴重的索引碎片化**（通常瞬間飆升至 98% 以上）。這會讓 CPU 飆高並大幅降低 IO 效能。
- **Correction**: 預先分配足夠空間。只有在刪除大量資料（如封存歷史資料）且**確定空間永遠不會再被使用**時，才執行一次 Shrink，並隨後立即 Rebuild Index。

### 2. 使用 `sa` 或 `db_owner` 作為應用程式連線帳號
- **Anti-pattern**: Connection String 中使用 `User Id=sa;`。
- **Why it's bad**: 違反最小權限原則。一旦被注入，駭客可以開啟 `xp_cmdshell` 控制整台伺服器。
- **Correction**: 建立專用的 App User，僅授予 `db_datareader` 和 `db_datawriter`（或更嚴格的自訂權限）。

### 3. 忽略 Transaction Log 的成長
- **Anti-pattern**: 復原模式設為 `FULL` 但從未進行 Transaction Log Backup。
- **Consequence**: Log 檔（.ldf）會無限制成長直到塞滿硬碟，導致資料庫停止服務。
- **Correction**: 如果不需要 Point-in-time recovery，設為 `SIMPLE`。如果需要 `FULL`，必須設定高頻率的 Log Backup（如每 15 分鐘）。

### 4. 維護計畫與業務高峰衝突
- **Anti-pattern**: 在報表跑批次的時間點同時執行 Update Statistics。
- **Consequence**: 嚴重的 Blocking 或 Deadlock。
- **Correction**: 繪製系統負載熱圖（Heatmap），將維護視窗安排在真正的低谷期。

---

## Checklists & workflows｜檢查清單與流程

### 🚀 新環境上線前檢查 (Go-Live Checklist)

- [ ] **Instant File Initialization**: 確認 Service Account 有 "Perform Volume Maintenance Tasks" 權限（大幅加速資料檔成長速度）。
- [ ] **TempDB 設定**: TempDB 檔案數量應對應 CPU Core 數（通常建議 4 或 8 個檔案），且大小一致並啟用 Autogrowth。
- [ ] **Max Server Memory**: **絕對不要**留空（預設是吃光所有 RAM）。應保留 4GB~10% 給 OS。
- [ ] **Backup Strategy**:
    - [ ] Full Backup (Weekly/Daily)
    - [ ] Diff Backup (Daily)
    - [ ] Log Backup (Every 5-15 mins)
- [ ] **Maintenance Jobs**: 安裝 Ola Hallengren scripts 並設定 Agent Jobs (Index Optimize, Integrity Check)。
- [ ] **Security**: 停用 `sa` 帳號，確認 App User 權限最小化。

### 🛠 定期維運流程 (Routine Workflow)

1.  **每日晨間檢查**:
    - 檢查 SQL Agent Jobs 是否有失敗（特別是備份與 ETL）。
    - 檢查 Error Log 是否有異常 Severity 錯誤（Severity > 16）。
2.  **每週效能檢視**:
    - 檢查 Top 10 High CPU/IO Queries（是否需要補 Index 或更新 Stats）。
    - 檢查 Index Fragmentation 趨勢（是否維護計畫失效）。
3.  **每月安全審計**:
    - 檢查是否有不明的新增帳號。
    - 檢查 `sysadmin` 角色成員。

---

## Real-world examples｜實戰案例

### 案例一：週一早晨的效能懸崖 (The Monday Morning Cliff)

**情境**：
某電商系統每週日晚上會進行大量資料封存（Delete 舊資料）與匯入（Insert 新商品）。週一早上使用者回報系統極慢。

**診斷**：
大量資料變動導致統計資訊（Statistics）過期，但尚未觸發 Auto Update 門檻。Optimizer 誤以為某個大表只有幾千筆資料，選擇了 Nested Loop Join 而非 Hash Join。

**解決方案 (T-SQL)**：
在週日批次作業結束的最後一步，強制更新關鍵 Table 的統計資訊：

```sql
-- 針對關鍵大表強制更新，並使用 Fullscan 確保準確
UPDATE STATISTICS Sales.Orders WITH FULLSCAN;
UPDATE STATISTICS Sales.OrderDetails WITH FULLSCAN;

-- 或者，針對全庫執行智慧更新 (使用 Ola Hallengren 的 SP)
EXECUTE dbo.IndexOptimize
@Databases = 'USER_DATABASES',
@FragmentationLow = NULL,
@FragmentationMedium = NULL,
@FragmentationHigh = NULL,
@UpdateStatistics = 'ALL',
@OnlyModifiedStatistics = 'Y'; -- 僅更新有變動的
```

### 案例二：權限最小化配置 (Least Privilege Setup)

**情境**：
開發團隊要求 `db_owner` 權限以便 "方便開發"，但這是生產環境。

**解決方案**：
建立一個自訂 Role，允許他們讀寫資料並執行 SP，但不能修改 Table 結構或刪除 Table。

```sql
USE MyDatabase;
GO

-- 1. 建立應用程式專用 Role
CREATE ROLE [App_ReadWrite_Role];
GO

-- 2. 授予基本 CRUD 權限
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [App_ReadWrite_Role];
GRANT EXECUTE ON SCHEMA::dbo TO [App_ReadWrite_Role];

-- 3. 明確拒絕高風險操作 (防呆)
-- 注意：DENY 優先權高於 GRANT
DENY ALTER ON SCHEMA::dbo TO [App_ReadWrite_Role]; -- 禁止修改 Table 結構

-- 4. 建立 User 並加入 Role
CREATE USER [AppUser] FOR LOGIN [AppLogin];
ALTER ROLE [App_ReadWrite_Role] ADD MEMBER [AppUser];
```

### 案例三：Transaction Log 滿載救援

**情境**：
收到告警 `The transaction log for database 'MyDb' is full due to 'LOG_BACKUP'.`

**緊急處理流程**：

1.  **不要 Shrink Log** (當下無效，因為 Log 被佔用)。
2.  **立即執行 Log Backup** (截斷 Log chain，釋放空間)。
    ```sql
    BACKUP LOG [MyDb] TO DISK = 'NUL'; -- 緊急狀況下如果不需保留該段 Log (極端情況)
    -- 正常情況應備份到磁碟：
    BACKUP LOG [MyDb] TO DISK = 'X:\Backups\MyDb_Log_Emergency.trn';
    ```
3.  **檢查是否有長交易 (Long Running Transaction)** 卡住 Log。
    ```sql
    DBCC OPENTRAN; -- 查看最早開啟的交易
    -- 如果有惡意或僵死的 SPID，考慮 KILL
    -- KILL 57;
    ```