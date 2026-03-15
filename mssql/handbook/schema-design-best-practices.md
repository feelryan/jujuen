# 實戰 Schema 設計與資料型別決策 / Schema Design & Data Type Strategy

## Mental model｜心智模型

在 SQL Server 中，Schema 設計不僅僅是繪製 ER Diagram（實體關聯圖），更是**定義資料在硬碟上的物理儲存形狀（Physical Storage Shape）**。

1.  **Clustered Index 是資料本身**：
    在 SQL Server 中，絕大多數表都會有一個 Clustered Index（通常是 Primary Key）。這意味著資料列（Row）是按照這個 Key 的順序物理儲存的。
    *   *Mental Image*: 你的資料不是隨意丟進一個箱子（Heap），而是像圖書館的書一樣，嚴格按照索書號（Clustered Key）排列在書架上。
    *   *Implication*: 選擇 Primary Key 就是決定資料的物理排序方式。錯誤的選擇（如隨機 GUID）會導致書架不斷被拆開重組（Page Splits & Fragmentation）。

2.  **資料寬度決定密度（Data Density）**：
    SQL Server 的最小 I/O 單位是 Page (8KB)。
    *   *Mental Image*: 你的目標是在一個 8KB 的箱子裡塞進盡可能多的 Rows。
    *   *Implication*: 資料型別選得越精準（例如用 `SMALLINT` 代替 `INT`，用 `VARCHAR` 代替 `NVARCHAR`），每個 Page 能存的筆數就越多，I/O 讀取效率就越高，記憶體緩存（Buffer Pool）的利用率也越好。

3.  **防禦性設計（Defensive Design）**：
    資料庫是資料的最後一道防線。應用程式層（App Layer）的驗證可能會被繞過或有 Bug，但資料庫層的 Constraints（約束）是絕對的。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Primary Key 策略：INT vs. GUID
這是 SQL Server 設計中最經典的 Trade-off。

*   **Pattern A: `INT` / `BIGINT` IDENTITY (Surrogate Key)**
    *   **適用情境**：單體應用、需要極致效能、重視儲存空間。
    *   **優點**：只有 4 或 8 bytes，窄且連續，最適合 Clustered Index，極少造成 Page Split。
    *   **缺點**：在分散式系統中難以合併資料，容易被預測（ID 遍歷攻擊）。
*   **Pattern B: `GUID` (UUID)**
    *   **適用情境**：分散式系統、微服務、需要客戶端生成 ID。
    *   **優點**：全球唯一，方便資料合併與遷移，安全性較高。
    *   **致命傷**：標準 GUID (`NEWID()`) 是隨機的。若設為 Clustered Key，會導致嚴重的隨機 I/O 和索引破碎。
    *   **Best Practice**：若必須用 GUID 當 PK，請務必使用 **Sequential GUID**。
        *   Server-side: 使用 `NEWSEQUENTIALID()` 作為預設值。
        *   Client-side: 使用類似 COMB GUID 的演算法生成有序 UUID。

### 2. 資料型別的精準決策 (Right-Sizing)
*   **Unicode 的代價**：
    *   `NVARCHAR` 佔用空間是 `VARCHAR` 的兩倍（2 bytes vs 1 byte）。
    *   **決策**：如果欄位確定只存 ASCII（如 Email, URL, 系統代碼），請堅決使用 `VARCHAR`。如果是人名、評論，則必須用 `NVARCHAR`。
*   **日期時間**：
    *   **棄用** `DATETIME`（精度低，佔 8 bytes）。
    *   **採用** `DATETIME2(n)`（精度可調，佔 6-8 bytes，範圍更廣）。通常 `DATETIME2(0)` 或 `DATETIME2(3)` 已足夠。
*   **字串長度**：
    *   避免濫用 `NVARCHAR(MAX)`。這會阻礙 Index Key 的建立，且可能導致資料被存放到 LOB page（Row-Overflow），增加讀取成本。盡量給出合理的上限，如 `NVARCHAR(200)`。

### 3. 正規化與反正規化的平衡 (Normalization vs. Denormalization)
*   **寫入密集 (OLTP)**：預設遵守 **3NF (第三正規化)**。避免更新異常（Update Anomalies），減少鎖定競爭。
*   **讀取優化**：適度的反正規化是允許的。
    *   **Computed Columns**：例如 `TotalAmount`，可以設為 `PERSISTED`，避免每次查詢都重算。
    *   **冗餘欄位**：在 `Orders` 表中冗餘存儲 `CustomerName`（Snapshot data），確保即使客戶改名，歷史訂單顯示的名稱不變，同時減少 Join。

### 4. NULL 的處理
*   **原則**：盡量定義欄位為 `NOT NULL` 並給予 `DEFAULT` 值。
*   **原因**：SQL 的三值邏輯（True, False, Unknown）會讓查詢變複雜（例如 `NOT IN` 遇到 NULL 會壞掉）。
*   **例外**：真正的「未知」或「不適用」狀態（例如 `TerminationDate` 對於在職與否）才使用 NULL。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Generic Bucket" (EAV Model)
*   **Anti-pattern**：建立一張表包含 `EntityID`, `AttributeName`, `Value`，試圖用來存儲所有東西。
*   **後果**：查詢極其痛苦（無數的 Self-Join），資料型別驗證喪失，效能極差。
*   **修正**：如果屬性真的高度動態，請使用 SQL Server 的 **JSON** 欄位功能，而不是 EAV 表。

### 2. 隱式轉型 (Implicit Conversion) 殺手
*   **Anti-pattern**：資料庫欄位定義為 `VARCHAR`，但應用程式（如 .NET Entity Framework）預設傳入 `NVARCHAR` 參數。
*   **後果**：SQL Server 為了比較兩者，必須將整個 Table 的欄位轉型（Convert_Implicit），導致 **Index Scan** 而非 Seek，CPU 飆高。
*   **修正**：確保 App 端傳入的參數型別與 DB Schema 完全一致。

### 3. 缺乏外鍵約束 (Missing Foreign Keys)
*   **Anti-pattern**：為了「方便開發」或「效能迷思」，不在資料庫層級建立 Foreign Key，只靠程式碼邏輯維護關聯。
*   **後果**：產生孤兒資料（Orphaned Rows），資料一致性崩壞。
*   **修正**：除非是極高併發的 Sharding 環境，否則 FK 是必須的。FK 對讀取效能無影響，對寫入的影響通常可忽略。

### 4. 濫用 GUID 作為 Clustered Index
*   **Anti-pattern**：使用 `NEWID()` 生成的主鍵作為 Clustered Index。
*   **後果**：**Page Splits**。當新資料插入到 Page 中間而非末尾時，SQL Server 必須移動一半的資料到新 Page。這會造成磁碟 I/O 暴增和嚴重的碎片化（Fragmentation）。

---

## Checklists & workflows｜檢查清單與流程

### Schema Design Checklist
在建立新 Table 或修改 Schema 時，請逐一確認：

- [ ] **Primary Key 選擇**：
    - 是否盡可能窄（Narrow）？
    - 是否單調遞增（Monotonic increasing）以優化寫入？
    - 若使用 GUID，是否已改用 `NEWSEQUENTIALID()` 或非叢集索引（Non-Clustered PK）？
- [ ] **資料型別審查**：
    - 是否使用了正確的字串型別（ASCII 用 `VARCHAR`, Unicode 用 `NVARCHAR`）？
    - 是否避免了不必要的 `MAX` 長度？
    - 日期是否使用了 `DATETIME2`？
    - 金錢是否使用了 `DECIMAL` 而非 `FLOAT`（避免精度遺失）？
- [ ] **NULLability**：
    - 該欄位真的需要 NULL 嗎？能否用 Default Value（如 0 或空字串）代替？
- [ ] **約束 (Constraints)**：
    - 是否建立了 Foreign Keys 確保關聯完整性？
    - 是否有 Check Constraints 處理業務邏輯（例如 `EndDate >= StartDate`）？
- [ ] **索引相容性**：
    - 欄位型別是否與應用程式 ORM 的預設對應一致，以避免隱式轉型？

---

## Real-world examples｜實戰案例

### Case 1: 電商訂單主表 (The "Right" Way)

```sql
CREATE TABLE Sales.Orders (
    -- 使用 BIGINT IDENTITY 作為 Clustered PK，確保寫入效能與儲存緊湊
    OrderID BIGINT IDENTITY(1,1) NOT NULL,
    
    -- 若需對外暴露不連續 ID，可另加一個 GUID 欄位並建 Unique Non-Clustered Index
    PublicOrderToken UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    
    -- 使用 DATETIME2(3) 節省空間並獲得毫秒精度
    OrderDate DATETIME2(3) NOT NULL DEFAULT SYSDATETIME(),
    
    -- 金額使用 DECIMAL 避免浮點數誤差
    TotalAmount DECIMAL(19, 4) NOT NULL DEFAULT 0,
    
    -- 狀態碼使用 TINYINT (0-255) 足夠且極省空間
    OrderStatusID TINYINT NOT NULL,
    
    -- 記錄當下客戶資訊（反正規化），避免客戶改名影響歷史訂單
    CustomerSnapshotName NVARCHAR(100) NOT NULL,
    
    -- 設定 Primary Key (Clustered)
    CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (OrderID),
    
    -- 確保資料完整性的 FK
    CONSTRAINT FK_Orders_OrderStatus FOREIGN KEY (OrderStatusID) 
        REFERENCES Sales.OrderStatus(StatusID),
        
    -- 業務邏輯防禦：金額不能為負
    CONSTRAINT CK_Orders_TotalAmount CHECK (TotalAmount >= 0)
);

-- 為 Public Token 建立索引以供查詢
CREATE UNIQUE NONCLUSTERED INDEX IX_Orders_PublicToken 
ON Sales.Orders(PublicOrderToken);
```

### Case 2: 常見錯誤示範 (The "Wrong" Way)

```sql
/* 
反模式警告：
1. 使用隨機 GUID 作為 Clustered PK -> 導致碎片化。
2. 使用 NVARCHAR(MAX) -> 導致資料可能存於 LOB pages，效能差。
3. 使用 FLOAT 存金額 -> 計算會出現 19.9999999999 誤差。
4. 無 FK 約束 -> 資料容易壞掉。
*/
CREATE TABLE Sales.BadOrders (
    OrderID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(), -- ❌ Clustered Index 惡夢
    OrderDate DATETIME, -- ❌ 舊型別
    TotalAmount FLOAT, -- ❌ 精度風險
    CustomerName NVARCHAR(MAX), -- ❌ 過度浪費空間
    Status INT -- ❌ 無 FK，意義不明
);
```