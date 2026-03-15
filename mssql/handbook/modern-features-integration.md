# 現代化功能應用：JSON、Columnstore 與整合 / Modern Features: JSON, Columnstore & Integration

## Mental model｜心智模型

在現代 SQL Server 開發中，我們不再將資料庫視為單純的「二維表格儲存庫 (Row Store)」。SQL Server 已經演進為一個 **多模型混合引擎 (Multi-Model Hybrid Engine)**。

要掌握本章節，請建立以下三個核心觀念：

1.  **JSON as a "Flexible Container" (彈性容器)**：
    *   **不要**把 SQL Server 當作 MongoDB 用。
    *   **要**把 JSON 視為關聯式架構中的「擴充包」。核心欄位（Core fields）依然維持強型別（Int, Date, Varchar），但變動性高、結構未定或僅用於傳輸的屬性，則封裝在 JSON 欄位中。這是一種 **Hybrid Relational-Document** 模型。

2.  **Columnstore as "Vertical Scanning" (垂直掃描)**：
    *   傳統 Row Store 像是「逐行閱讀一本書」，適合交易處理（OLTP），因為你通常需要讀寫整行資料（User Profile）。
    *   Columnstore Index 像是「只讀目錄或特定欄位」，適合分析（OLAP）。它將同一欄的資料壓縮在一起，對於 `SUM`, `AVG`, `COUNT` 等聚合運算有數量級的效能提升。

3.  **Temporal Tables as "Built-in Time Travel" (內建時光機)**：
    *   以往我們用 Trigger 或應用層邏輯寫 Log 來追蹤變更。
    *   Temporal Table 是引擎層級的「版本控制」。它自動維護一張「歷史表」，讓你隨時查詢 `AS OF <datetime>` 的資料狀態，將「現在」與「過去」的維度解耦。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. JSON 整合模式 (JSON Integration Patterns)

*   **混合結構模式 (Hybrid Schema)**：
    *   將固定且常用的欄位（如 `OrderID`, `CustomerID`, `OrderDate`）設為實體欄位。
    *   將多樣化的屬性（如 `ProductAttributes`, `CustomSettings`）存為 JSON。
*   **虛擬欄位索引 (Virtual Column Indexing)**：
    *   **Pattern**: JSON 欄位本身無法直接 Index 內部屬性。
    *   **Practice**: 使用 **Computed Column** 提取 JSON 內的值，並對該 Computed Column 建立索引。
    ```sql
    ALTER TABLE SalesOrder
    ADD CustomerRegion AS JSON_VALUE(JsonData, '$.Customer.Region');
    
    CREATE INDEX IX_SalesOrder_Region ON SalesOrder(CustomerRegion);
    ```
*   **API Payload 橋接 (Bridge)**：
    *   使用 `FOR JSON PATH` 直接在 DB 層產生 API 需要的格式，減少 App Server 的序列化負擔。
    *   使用 `OPENJSON` 將前端傳來的 JSON 陣列一次性轉為 Table 進行 Bulk Insert/Update。

### 2. Columnstore 分析模式 (Columnstore Analytics Patterns)

*   **即時營運分析 (Real-time Operational Analytics)**：
    *   **Pattern**: 在高頻交易的 OLTP 表上，建立 **Non-Clustered Columnstore Index (NCCI)**。
    *   **Benefit**: 讓你在不影響交易寫入（透過 Delta Store 機制）的情況下，直接對同一份資料跑報表，不需要 ETL 到 Data Warehouse。
*   **資料歸檔壓縮 (Archive Compression)**：
    *   對於歷史大表（Fact Tables），使用 **Clustered Columnstore Index (CCI)** 取代傳統 B-Tree。通常可獲得 10x 的壓縮率與查詢加速。

### 3. Temporal Tables 稽核模式 (Audit & History Patterns)

*   **全自動稽核 (Zero-Code Audit Trail)**：
    *   取代傳統繁雜的 Trigger。只需宣告 `SYSTEM_VERSIONING = ON`，系統會自動將 `DELETE` 或 `UPDATE` 前的舊資料搬移到 History Table。
*   **漸變維度處理 (SCD Type 2)**：
    *   在 Data Warehousing 情境中，利用 Temporal Table 自動處理 Slowly Changing Dimensions，簡化 ETL 邏輯。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. JSON 濫用 (JSON Misuse)

*   **❌ The "Schemaless" Trap (無架構陷阱)**：
    *   **Anti-pattern**: 為了偷懶不開欄位，把所有資料都塞進一個 `Payload` JSON 欄位。
    *   **Consequence**: 喪失資料型別驗證、Foreign Key 約束失效、查詢效能低落、儲存空間浪費（重複的 Key）。
*   **❌ Filtering on Raw JSON (裸查 JSON)**：
    *   **Anti-pattern**: `WHERE JSON_VALUE(Col, '$.prop') = 'X'` without an index.
    *   **Consequence**: 導致 Full Table Scan，因為 SQL Server 必須 parse 每一行的 JSON 才能比對。務必使用 Computed Column Index。
*   **❌ Massive JSON Documents (巨型 JSON)**：
    *   **Pitfall**: 儲存超過 8KB 甚至 MB 等級的 JSON。
    *   **Consequence**: 造成 LOB (Large Object) page 存取，嚴重拖慢記憶體與 I/O。

### 2. Columnstore 誤區 (Columnstore Missteps)

*   **❌ Small Tables (小表使用)**：
    *   **Pitfall**: 對少於 100 萬筆資料的表使用 Columnstore。
    *   **Consequence**: Columnstore 的啟動成本與 Segment 管理開銷會超過其帶來的效益。小表請用傳統 Row Store。
*   **❌ Frequent Updates/Deletes (頻繁修改)**：
    *   **Pitfall**: 在高頻更新的表上使用 **Clustered** Columnstore Index。
    *   **Consequence**: Columnstore 的 Update 其實是 Delete + Insert，會產生大量碎片（Fragmentation）與 Tuple Mover 的背景負載。
*   **❌ `SELECT *` (全欄位查詢)**：
    *   **Pitfall**: 對 Columnstore 表執行 `SELECT *`。
    *   **Consequence**: 引擎必須將所有分開儲存的 Column 重新組裝（Materialization），效能甚至比 Row Store 差。

### 3. Temporal Tables 隱憂 (Temporal Concerns)

*   **❌ Uncontrolled History Growth (歷史資料暴漲)**：
    *   **Pitfall**: 開啟 Versioning 但未設定 Retention Policy。
    *   **Consequence**: History Table 無限增長，吃光硬碟空間。
*   **❌ Schema Changes (架構變更困難)**：
    *   **Pitfall**: 直接修改主表結構。
    *   **Consequence**: 必須先關閉 Versioning 才能修改 Schema，然後再重新開啟，部署流程較繁瑣。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: JSON vs. Relational vs. Columnstore

1.  **資料結構是否高度變動？**
    *   Yes → 使用 **JSON** (存於 `NVARCHAR(MAX)`).
    *   No → 繼續下一步。
2.  **查詢模式是否為「掃描大量資料列、只取少數欄位、做聚合運算」？**
    *   Yes (e.g., Reports, Analytics) → 考慮 **Columnstore Index**.
    *   No (e.g., Lookup by ID, transactional update) → 使用傳統 **Row Store (B-Tree)**.
3.  **是否需要追蹤資料變更歷史或「回到過去」查詢？**
    *   Yes → 啟用 **Temporal Tables**.

### Implementation Checklist

#### JSON Setup
- [ ] **驗證**：使用 `ISJSON` 檢查約束 (Check Constraint) 確保資料格式正確。
- [ ] **索引**：針對 `WHERE` 子句中常用的 JSON 屬性建立 Computed Column + Index。
- [ ] **輸出**：API 輸出層是否使用了 `FOR JSON PATH` 以減少應用層轉換成本？

#### Columnstore Setup
- [ ] **資料量評估**：目標資料表是否超過 100 萬筆？
- [ ] **寫入模式**：是否為 Batch Insert？（單次 Insert < 102,400 筆會進入 Delta Store，影響壓縮率）。
- [ ] **維護**：是否安排了 `REORGANIZE` 排程以合併 Delta Store 與清除已刪除的 Bitmap？

#### Temporal Table Setup
- [ ] **索引**：History Table 是否在 `(EndOfPeriod, StartOfPeriod)` 上建立了 Clustered Index？（預設會建，但需確認）。
- [ ] **保留策略**：是否設定了 `HISTORY_RETENTION_PERIOD` (e.g., `6 MONTHS`)？

---

## Real-world examples｜實戰案例

### Scenario 1: E-commerce Product Catalog (Hybrid JSON)

**情境**：電商系統，商品有共通欄位（名稱、價格），但不同類別有完全不同的規格（衣服有尺寸顏色，電腦有 CPU/RAM）。

```sql
CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY,
    Name NVARCHAR(200),
    Price DECIMAL(10,2),
    CategoryID INT,
    -- 彈性屬性存這裡
    Attributes NVARCHAR(MAX), 
    CONSTRAINT [chk_json] CHECK (ISJSON(Attributes)=1)
);

-- 為了快速搜尋顏色，建立虛擬欄位索引
ALTER TABLE Products
ADD Color AS JSON_VALUE(Attributes, '$.Color');

CREATE INDEX IX_Products_Color ON Products(Color);

-- 查詢紅色商品，效能等同於實體欄位
SELECT Name, Price 
FROM Products 
WHERE Color = 'Red';
```

### Scenario 2: High-Speed Logging & Analytics (Columnstore)

**情境**：IoT 裝置每秒傳送大量 Log，需要保留並快速產出「每日平均溫度」報表。

```sql
CREATE TABLE DeviceLogs (
    LogID BIGINT IDENTITY,
    DeviceID INT,
    LogTime DATETIME2,
    Temperature FLOAT,
    Humidity FLOAT
    -- 其他 20 個欄位...
);

-- 建立 Clustered Columnstore Index 進行極致壓縮與分析加速
CREATE CLUSTERED COLUMNSTORE INDEX CCI_DeviceLogs ON DeviceLogs;

-- 此查詢將以 Batch Mode 執行，極快
SELECT DeviceID, AVG(Temperature) 
FROM DeviceLogs
WHERE LogTime > DATEADD(day, -7, GETDATE())
GROUP BY DeviceID;
```

### Scenario 3: Sensitive Configuration Management (Temporal)

**情境**：金融系統的費率設定表，必須知道「誰」在「什麼時候」改了費率，且必須能還原到上個月的費率計算報表。

```sql
CREATE TABLE ExchangeRates (
    CurrencyCode CHAR(3) PRIMARY KEY,
    Rate DECIMAL(18, 6),
    LastModifiedBy NVARCHAR(50),
    
    -- Temporal 必備欄位
    SysStartTime DATETIME2 GENERATED ALWAYS AS ROW START,
    SysEndTime DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (SysStartTime, SysEndTime)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.ExchangeRatesHistory));

-- 查詢上個月底當下的匯率（Time Travel）
SELECT * 
FROM ExchangeRates 
FOR SYSTEM_TIME AS OF '2023-10-31 23:59:59'
WHERE CurrencyCode = 'USD';
```