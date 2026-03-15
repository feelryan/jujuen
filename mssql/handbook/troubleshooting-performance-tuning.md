# 效能診斷流程與執行計畫分析 / Performance Troubleshooting & Execution Plan Analysis

## Mental model｜心智模型

在處理 SQL Server 效能問題時，必須建立兩個核心的心智模型，以避免「瞎猜」或「隨機嘗試」：

### 1. 時間去哪了？ (Where is the time going?)
每一個 Request 的總執行時間（Duration）只由兩個部分組成：
$$ \text{Duration} = \text{CPU Time} + \text{Wait Time} $$

- **CPU Time (Running)**：SQL Server 正在努力運算（排序、雜湊、掃描記憶體中的頁面）。如果 CPU 高，通常意味著演算法效率低（如全表掃描）或計算量過大。
- **Wait Time (Waiting)**：SQL Server 想要執行但被卡住了。它在等磁碟 I/O（`PAGEIOLATCH`）、等鎖（`LCK_M_*`）、或等記憶體分配（`RESOURCE_SEMAPHORE`）。
- **診斷關鍵**：先判斷是 **CPU 瓶頸** 還是 **等待瓶頸**（Wait Stats），決定排查方向。

### 2. 執行計畫是地圖，不是法律 (The Plan is a Map, not Law)
執行計畫（Execution Plan）是 Query Optimizer 基於「統計資訊（Statistics）」估算出的「成本最低路徑」。
- **Cardinality Estimation (CE)**：這是核心。Optimizer 預估某個步驟會吐出 1 行還是 100 萬行資料。
- **誤差來源**：如果預估是 1 行（於是選用 Nested Loop Join），但實際來了 100 萬行，效能就會崩潰。
- **診斷關鍵**：尋找 **Estimated Rows（預估行數）** 與 **Actual Rows（實際行數）** 之間的巨大差異。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 由上而下的診斷漏斗 (Top-Down Troubleshooting Funnel)
不要一開始就鑽進某個 Query 的細節，除非你確定它就是兇手。
1.  **Instance Level**: 伺服器整體慢嗎？看 `sys.dm_os_wait_stats` 或 Performance Counters。
2.  **Request Level**: 誰現在卡住？使用 `sp_WhoIsActive` (社群標準工具) 或 `sys.dm_exec_requests`。
3.  **Query Level**: 拿到具體的 Query 與 Plan，分析邏輯讀取（Logical Reads）。

### 2. 善用 Query Store (The Flight Recorder)
現代 SQL Server (2016+) 務必開啟 Query Store。它是資料庫的「黑盒子」。
- **Regressed Queries**: Query Store 會自動標記出「昨天很快，今天變慢」的查詢（Plan Regression）。
- **Force Plan**: 如果發現舊的 Plan 比較快，可以直接在 UI 上強制鎖定該 Plan。

### 3. 執行計畫分析三板斧 (The "Big Three" in Execution Plans)
打開執行計畫時，優先檢查這三點：
- **Warnings (黃色驚嘆號)**：
  - **Missing Index**: 提示可能缺索引（參考即可，需評估副作用）。
  - **Implicit Conversion**: 隱式轉型導致無法使用索引（Seek 變 Scan）。
  - **TempDB Spill**: 記憶體不足，資料寫入 TempDB（Sort/Hash Warning），極度影響效能。
- **Thick Arrows (粗線條)**：資料流動量大的路徑。線條越粗，代表資料行數越多。
- **Seek vs. Scan**：
  - **Index Seek**: 精確查找，通常較快。
  - **Index Scan**: 掃描整個索引結構，通常較慢（除非表很小或需要全表數據）。

### 4. 基準測試數據化 (Measure Logical Reads)
不要只憑感覺「好像變快了」。使用 `SET STATISTICS IO, TIME ON`。
- 關注 **Logical Reads**：這是查詢從 Buffer Pool 讀取的 Page 數量。減少 Logical Reads 通常就能減少 CPU 和 I/O。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 忽略參數嗅探 (Ignoring Parameter Sniffing)
- **現象**：User 回報系統慢，但你把 SQL 複製到 SSMS 執行卻飛快。
- **原因**：App 執行時使用的是第一次編譯時針對特定參數（如 `ID=1`）生成的 Plan，但現在傳入的參數（如 `ID=9999`）資料分佈不同，導致該 Plan 效能極差。
- **解法**：檢查 Plan Cache，考慮使用 `OPTION (RECOMPILE)` 或 `OPTIMIZE FOR`。

### 2. 濫用純量函數 (Scalar Functions in Predicates/Select)
- **反模式**：`SELECT * FROM Orders WHERE dbo.FormatDate(OrderDate) = '2023-01-01'`
- **後果**：導致 **RBAR (Row By Row)** 處理，無法批次運算，且通常會阻止並行處理（Parallelism）。這會讓查詢慢 10-100 倍。
- **修正**：改寫為 Inline Table-Valued Function (iTVF) 或直接展開邏輯。

### 3. 看到 Key Lookup 就想消滅 (Blindly Removing Key Lookups)
- **誤區**：Key Lookup 代表使用了非叢集索引但缺欄位，需要回表查資料。有些人會無腦把所有欄位加到 `INCLUDE` 中。
- **風險**：過度寬的索引會佔用大量空間並拖慢 Write/Update 效能。如果 Lookup 次數很少（例如只回表 10 次），是可以接受的。

### 4. 依賴「估計」執行計畫 (Relying on Estimated Plan Only)
- **陷阱**：在 SSMS 按 "Display Estimated Execution Plan" 看到的只是「理論」。
- **現實**：實際執行時可能因為變數、Temp 表或並行度改變而產生完全不同的「實際」計畫。務必查看 **Actual Execution Plan**。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 緊急排查流程 (Live Troubleshooting)

當系統正在變慢時：

- [ ] **執行 `sp_WhoIsActive`** (或查詢 `sys.dm_exec_requests`)
    - 檢查 `wait_info`：是 `LCK` (鎖定)? `PAGEIOLATCH` (磁碟)? `SOS_SCHEDULER_YIELD` (CPU)?
    - 檢查 `tempdb_allocations`：是否有 Query 正在爆吃 TempDB？
- [ ] **檢查 Blocking Chain**
    - 找出 `blocking_session_id` 的源頭（Head Blocker）。
- [ ] **檢查正在執行的 SQL**
    - 取得 `sql_text` 和 `query_plan`。

### 🔍 慢查詢分析流程 (Post-mortem Analysis)

針對特定的慢 SQL：

- [ ] **開啟統計資訊**
    - `SET STATISTICS IO ON; SET STATISTICS TIME ON;`
- [ ] **取得 Actual Execution Plan**
    - 比較 **Estimated Number of Rows** vs. **Actual Number of Rows**。
    - 差異超過 10 倍？ -> 統計資訊過期 (Update Statistics) 或 查詢邏輯太複雜。
- [ ] **檢查 Predicates (SARGability)**
    - 是否有 `WHERE LEFT(Col, 1) = 'A'` 這種寫法？ -> 改為 `WHERE Col LIKE 'A%'` 以利用索引。
    - 是否發生 **Implicit Conversion** (例如 `VARCHAR` 欄位與 `NVARCHAR` 參數比較)?
- [ ] **檢查索引使用**
    - 是 Scan 還是 Seek？
    - 是否有 **Key Lookup** 且佔比很高（Output List 很大）？ -> 考慮 Covering Index (Include columns)。
- [ ] **檢查 Wait Stats (針對該 Query)**
    - 在執行計畫的屬性中查看 `WaitStats`，確認瓶頸是 I/O 還是 CPU。

---

## Real-world examples｜實戰案例

### Case 1: 隱式轉型殺手 (The Implicit Conversion Killer)

**情境**：`PhoneNumber` 欄位是 `VARCHAR(20)`，但應用程式框架（如 .NET Entity Framework）預設傳入 `NVARCHAR` 參數。

```sql
-- Anti-pattern: Implicit Conversion
-- @Phone is NVARCHAR(20)
SELECT * FROM Customers WHERE PhoneNumber = @Phone;
```

**執行計畫分析**：
- 你會看到一個 **Index Scan** 而不是 Seek。
- 執行計畫的 `SELECT` 運算子上會有黃色驚嘆號警告：`Type conversion in expression (CONVERT_IMPLICIT(...))`。
- **原因**：SQL Server 必須把整張表的 `PhoneNumber` 轉成 `NVARCHAR` 才能跟參數比對，導致索引失效。

**修正**：
1. 修改 App 程式碼，明確指定參數型別為 `AnsiString` / `VARCHAR`。
2. 或修改資料庫 Schema，將欄位改為 `NVARCHAR` (如果業務允許)。

### Case 2: 參數嗅探與計畫快取 (Parameter Sniffing)

**情境**：查詢訂單狀態。99% 的訂單是 'Closed'，只有 1% 是 'Open'。

```sql
CREATE PROCEDURE GetOrdersByStatus (@Status INT)
AS
SELECT * FROM Orders WHERE StatusID = @Status;
```

1. 第一次執行傳入 `@Status = 'Open'` (1% 資料)。Optimizer 選擇 **Index Seek + Key Lookup** (因為行數少，回表快)。
2. 這個 Plan 被 Cache 住。
3. 第二次執行傳入 `@Status = 'Closed'` (99% 資料)。重用上面的 Plan。
4. **災難**：對 99% 的資料做 Key Lookup 是極慢的（不如直接全表 Scan）。

**修正**：

```sql
-- Solution A: Recompile every time (CPU cost higher, but safe)
SELECT * FROM Orders WHERE StatusID = @Status OPTION (RECOMPILE);

-- Solution B: Optimize for the common case (or average)
SELECT * FROM Orders WHERE StatusID = @Status OPTION (OPTIMIZE FOR UNKNOWN);
```

### Case 3: 消除 Key Lookup (Eliminating Key Lookup)

**情境**：查詢頻率極高，每次都要回表 (Key Lookup)。

```sql
-- Index exists on (UserID)
-- Query:
SELECT UserID, UserName, Email FROM Users WHERE UserID = 123;
```

**分析**：
- 索引只有 `UserID`。
- 查詢需要 `UserName` 和 `Email`。
- 執行計畫：`Index Seek (IX_UserID)` -> `Key Lookup (Clustered)`。

**修正 (Covering Index)**：

```sql
CREATE NONCLUSTERED INDEX IX_Users_UserID_Includes
ON Users (UserID)
INCLUDE (UserName, Email); -- 把需要的欄位放在葉子節點
```

**結果**：執行計畫變為單純的 **Index Seek**，邏輯讀取量大幅下降。