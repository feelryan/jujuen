# 交易處理、鎖定與並發控制實務 / Transactions, Locking & Concurrency Control

## Mental model｜心智模型

在 MS-SQL 中處理並發（Concurrency）問題時，你需要建立以下三個核心觀念：

### 1. 鎖定管理器是交通警察 (Lock Manager as Traffic Cop)
MS-SQL 的預設行為是**悲觀鎖定（Pessimistic Locking）**。
- **Readers block Writers, Writers block Readers**：在預設的 `READ COMMITTED` 下，讀取資料會申請 Shared Lock (S)，寫入資料會申請 Exclusive Lock (X)。這兩者互斥。
- **想像成圖書館**：有人正在讀這本書（S Lock），你就不能拿去塗改（X Lock）；有人正在塗改這本書（X Lock），你就不能拿來看（S Lock）。

### 2. Blocking vs. Deadlock (塞車 vs. 對撞)
這兩個名詞常被混淆，但在維運上有巨大差異：
- **Blocking (阻塞)**：是「塞車」。A 拿了鎖，B 需要等待 A 釋放。這會導致效能變慢，但只要 A 釋放，B 就能繼續。這是正常的資料庫行為，只是需要優化等待時間。
- **Deadlock (死結)**：是「對撞僵局」。A 等 B，B 等 A，誰也不讓誰。SQL Server 會介入擔任「殺手」，強制犧牲（Rollback）其中一個 Transaction（Victim），讓另一個通過。這是**錯誤 (Error)**，應用程式必須處理並重試。

### 3. MVCC 與 RCSI (平行時空的讀取)
現代 MS-SQL 開發建議採用 **RCSI (Read Committed Snapshot Isolation)**。
- 啟用後，寫入者依然會鎖定（X Lock），但讀取者不再申請 S Lock，而是讀取資料修改前的「版本快照（Snapshot）」。
- **心智模型轉變**：Readers don't block Writers, Writers don't block Readers。這讓 MS-SQL 的行為更像 Oracle 或 PostgreSQL。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先啟用 RCSI (Read Committed Snapshot Isolation)
除非你有特殊的 Legacy 系統包袱，否則新專案應預設開啟 RCSI。這能解決 80% 的 Blocking 問題，並減少死結機率。

```sql
-- 啟用 RCSI (需獨佔連線)
ALTER DATABASE [YourDB] SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
```

### 2. 標準交易處理樣板 (The Standard Transaction Template)
在 T-SQL 中撰寫交易時，請務必遵循 `SET XACT_ABORT ON` 與 `TRY...CATCH` 模式。這能確保當發生 Timeout 或嚴重錯誤時，交易會確實 Rollback，避免「孤兒交易（Orphaned Transactions）」鎖死系統。

```sql
SET XACT_ABORT ON; -- 發生嚴重錯誤時自動 Rollback，最安全的保險

BEGIN TRY
    BEGIN TRANSACTION;

    -- 你的業務邏輯 (Business Logic)
    UPDATE Inventory SET Qty = Qty - 1 WHERE ProductID = 101;
    INSERT INTO AuditLog (Msg) VALUES ('Sold item 101');

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    -- 檢查是否有活躍的交易需要 Rollback
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    -- 拋出錯誤資訊給 Application
    THROW; 
END CATCH;
```

### 3. 交易範圍最小化 (Keep Transactions Short)
- **黃金法則**：交易內只做資料庫操作。
- **嚴禁**：在 `BEGIN TRAN` 和 `COMMIT` 之間呼叫外部 API、發送 Email、或等待使用者輸入。這些操作的不確定性會導致鎖定時間無限延長。

### 4. 索引設計即鎖定設計 (Indexing is Locking Strategy)
鎖定是發生在資源上的（Row, Page, Table）。
- 如果你的 `UPDATE/DELETE` 條件沒有命中索引，SQL Server 可能會退化成 **Table Scan**，進而導致 **Table Lock**。
- **Best Practice**：確保所有 `UPDATE` 和 `DELETE` 語句的 `WHERE` 子句都有高選擇性的索引支援。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 `NOLOCK` (The NOLOCK Addiction)
許多開發者遇到效能問題就加 `WITH (NOLOCK)`。
- **風險**：這不僅是讀到「髒資料（Dirty Read）」，在 Page Split 發生時，還可能導致讀取到重複資料或遺漏資料，甚至導致查詢報錯。
- **解法**：使用 RCSI 代替 `NOLOCK`。RCSI 提供一致性的快照讀取，且不阻塞寫入。

### 2. 巢狀交易的誤解 (Nested Transactions Illusion)
MS-SQL 的巢狀交易是「假的」。
- 內層的 `COMMIT TRANSACTION` 只是將 `@@TRANCOUNT` 減 1，**並不會真正持久化資料**。
- 只有最外層的 `COMMIT` 才會真正寫入 Log。
- **陷阱**：內層的 `ROLLBACK` 會直接把**所有**層級（包含最外層）全部回滾。這常導致外層程式碼誤以為交易還在進行中。

### 3. 應用程式端的「長交易」
在 C# / Java 程式碼中開啟 Transaction Scope，然後進行大量運算或迴圈處理資料庫。
- **後果**：資料庫連線與鎖定被長時間佔用。
- **修正**：先在記憶體中準備好資料，開啟交易，快速批次寫入，立即提交。

### 4. 忽略 Deadlock 重試邏輯
死結是並發系統的自然現象（特別是在高負載下）。
- **反模式**：把 Deadlock 當成一般 Exception 記錄 Log 然後報錯給使用者。
- **修正**：在 Application Layer (如 Entity Framework, Dapper) 實作 Retry Policy（例如 Polly），遇到 Error 1205 (Deadlock Victim) 時自動重試。

---

## Checklists & workflows｜檢查清單與流程

### Transaction Design Checklist (交易設計檢查表)
- [ ] **設定檢查**：開頭是否加上了 `SET XACT_ABORT ON`？
- [ ] **錯誤處理**：是否使用了 `BEGIN TRY...CATCH` 包覆，並在 CATCH 區塊正確 `ROLLBACK`？
- [ ] **範圍檢查**：交易區塊內是否**沒有**外部 API 呼叫或長時間運算？
- [ ] **索引支援**：`UPDATE/DELETE` 語句是否能使用索引 Seek？（避免 Table Lock）
- [ ] **順序一致性**：如果有多個 Table 需要修改，是否在所有 Stored Procedure 中都依照**相同的順序**存取 Table？（例如永遠先鎖 Table A，再鎖 Table B，可大幅減少死結）。

### Deadlock Troubleshooting Workflow (死結排查流程)
1. **捕捉**：使用 Extended Events (XEvents) 監控 `xml_deadlock_report` 事件。
2. **分析圖形**：
   - 找出 **Victim**（被殺掉的那個）與 **Survivor**。
   - 觀察 **Resource List**：爭奪的是 Key Lock (Row) 還是 Object Lock (Table)？
   - 觀察 **Process List**：是哪兩句 SQL 在互咬？
3. **解決方案決策樹**：
   - 是讀寫互咬？ -> **啟用 RCSI**。
   - 是寫寫互咬？ -> **檢查存取順序** 或 **縮短交易時間**。
   - 是因為缺索引導致鎖定範圍太大？ -> **建立索引**。

---

## Real-world examples｜實戰案例

### 案例 1：訂單庫存扣減 (正確的重試與鎖定)

在高並發的電商搶購場景，單純的 `UPDATE` 容易發生死結或超賣。

**Bad Practice (Race Condition):**
```sql
-- 讀取庫存 (此時沒鎖，或是 Shared Lock)
SELECT Qty FROM Product WHERE Id = 1;
-- 應用程式判斷 Qty > 0
-- 寫入 (此時才要 Exclusive Lock，容易被其他同時讀取的人覆蓋或死結)
UPDATE Product SET Qty = Qty - 1 WHERE Id = 1;
```

**Good Practice (Update Lock Hint or Atomic Update):**

```sql
SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRAN;
    
    -- 方法 A: 原子性更新 (Atomic Update) 並檢查 RowCount
    UPDATE Product 
    SET Qty = Qty - 1 
    WHERE Id = @ProductId AND Qty > 0; -- 確保庫存足夠才扣

    IF @@ROWCOUNT = 0
    BEGIN
        -- 庫存不足或產品不存在
        THROW 51000, 'Out of stock', 1;
    END

    -- 寫入訂單
    INSERT INTO Orders (...) VALUES (...);

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRAN;
    THROW;
END CATCH;
```

### 案例 2：報表查詢導致系統卡死 (Blocking Chains)

**情境**：行銷部門在上班時間執行一個超大範圍的銷售報表查詢。
**現象**：前台結帳系統開始轉圈圈（Time out）。
**原因**：報表查詢預設使用 Shared Locks，鎖住了數百萬行訂單資料。前台的新訂單寫入（需要 X Lock）被阻塞。
**解決**：
1. **短期**：Kill 掉報表 Session。
2. **中期**：報表查詢加上 `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` (如果容許些微誤差) 或使用 Read Only Replica。
3. **長期 (最佳解)**：資料庫啟用 **RCSI**。報表查詢讀取快照，完全不影響前台寫入。

### 案例 3：死結分析 (Key Lookup Deadlock)

**情境**：
- Transaction A: `UPDATE Users SET LastLogin = GetDate() WHERE Id = 10` (持有 Clustered Index Lock)
- Transaction B: `SELECT * FROM Users WHERE Email = 'a@b.com'` (持有 Non-Clustered Index Lock，正要回查 Clustered Index)

**死結原因**：
- A 持有 Clustered Index，想更新 Non-Clustered Index (Email)。
- B 持有 Non-Clustered Index (Email)，想回查 Clustered Index (Key Lookup) 拿其他欄位。
- 兩者互卡。

**解法**：
- 將 B 需要的欄位加入 Non-Clustered Index (Using `INCLUDE` columns)，消除 Key Lookup，讓 B 不需要去碰 Clustered Index。