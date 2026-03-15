# 常見效能殺手與開發反模式 / Common Performance Killers & Anti-Patterns

## Mental model｜心智模型

在優化 SQL 效能時，最核心的心智模型是理解 **「資料庫引擎如何存取資料」**。想像你在圖書館找書：

1.  **SARGable (Search ARGument ABLE)**：
    *   **Good (Index Seek)**：如果你有書名索引，且你要找「以 'Harry' 開頭的書」，你可以直接跳到 'H' 區塊，這就是 **SARGable**。
    *   **Bad (Index Scan)**：如果你要找「書名**中間**包含 'Potter' 的書」，或者「書名長度等於 10 的書」，索引就失效了。你必須從第一本翻到最後一本。這就是 **Non-SARGable**。
    *   **核心原則**：不要對索引欄位進行運算或函式包裝，讓引擎能直接使用索引樹（B-Tree）進行查找。

2.  **隱式轉型 (Implicit Conversion)**：
    *   這就像你要在英文索引中找一個法文單字。資料庫引擎必須先把索引裡的每一個英文單字「翻譯」成法文，才能進行比對。這會導致索引失效（Scan）並消耗大量 CPU。

3.  **集合思考 vs. 逐行思考 (Set-based vs. Row-by-row)**：
    *   SQL Server 是為集合運算設計的。
    *   **反模式**：使用 Cursor、While 迴圈或純量函式（Scalar UDF）處理每一行資料，就像叫圖書館員一次只拿一本書去櫃檯結帳，效率極低。
    *   **正模式**：一次處理一批資料（Set-based），就像把一車書推去櫃檯一次結帳。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 確保查詢是 SARGable 的
總是將運算移到運算子（Operator）的右側，保持左側（欄位本身）乾淨。

*   **Pattern**: `Column <Operator> Constant/Parameter`
*   **Don't**: `WHERE YEAR(OrderDate) = 2023`
*   **Do**: `WHERE OrderDate >= '2023-01-01' AND OrderDate < '2024-01-01'`

### 2. 嚴格匹配資料型別 (Strict Data Type Matching)
應用程式端傳入的參數型別，必須與資料庫 Schema 定義完全一致。

*   **Pattern**: 如果 DB 欄位是 `VARCHAR(50)`，Dapper/EF Core/ADO.NET 的參數就該是 `AnsiString` 或 `VARCHAR`，絕不能是 `NVARCHAR`（.NET String 預設通常是 Unicode/NVARCHAR）。
*   **Why**: `NVARCHAR` 優先級高於 `VARCHAR`，會導致 SQL Server 將整個 Table 的 `VARCHAR` 索引轉型為 `NVARCHAR` 來比對，造成全表掃描。

### 3. 使用 TVF 或 Inline Logic 取代 Scalar UDF
純量函式（Scalar User-Defined Functions）在舊版 SQL Server (2017 以前) 是效能殺手，因為它會強制執行計畫變成 Serial (單執行緒) 且無法精確估算成本。

*   **Best Practice**: 將邏輯寫成 **Inline Table-Valued Function (iTVF)** 或直接展開在 View/Stored Procedure 中。
*   **Modern Feature**: SQL Server 2019+ 引入了 Scalar UDF Inlining，能自動優化部分場景，但手動優化仍是最穩健的選擇。

### 4. 預防 N+1 查詢 (Eager Loading)
在 ORM (Entity Framework, Hibernate) 中，避免在迴圈內觸發資料庫查詢。

*   **Pattern**: 使用 `.Include()` (EF Core) 或撰寫 SQL `JOIN` 一次抓取所需資料。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Function Wrapper" Trap (函式包裝陷阱)
這是最常見的 Non-SARGable 寫法。只要欄位被函式包住，索引通常即刻失效。

*   ❌ `WHERE ISNULL(PhoneNumber, '') = '123456'` (無法使用索引)
*   ❌ `WHERE LEFT(Name, 3) = 'ABC'` (無法使用索引)
*   ❌ `WHERE DATEDIFF(day, OrderDate, GETDATE()) < 7`
*   ✅ `WHERE PhoneNumber = '123456'` (注意 NULL 處理邏輯需調整)
*   ✅ `WHERE Name LIKE 'ABC%'`
*   ✅ `WHERE OrderDate > DATEADD(day, -7, GETDATE())`

### 2. The "Leading Wildcard" (前置萬用字元)
*   ❌ `LIKE '%Term'` 或 `LIKE '%Term%'`：這迫使引擎檢查每一個節點，因為 B-Tree 是按順序排列的，不知道開頭就無法搜尋。
*   **Mitigation**: 如果業務強烈需求全文檢索，請使用 Full-Text Search 或 ElasticSearch，而非標準 SQL `LIKE`。

### 3. Implicit Conversion (隱式轉型殺手)
最經典的案例發生在 `VARCHAR` 欄位與 `NVARCHAR` 參數之間。
*   **徵兆**: 執行計畫中出現黃色驚嘆號，提示 `Type conversion in expression (CONVERT_IMPLICIT(...))`。
*   **後果**: Index Seek 變成 Index Scan，CPU 飆高。

### 4. Catch-all Queries (萬能查詢條件)
試圖用一個查詢解決所有過濾組合。
*   ❌ `WHERE (@Name IS NULL OR Name = @Name) AND (@Age IS NULL OR Age = @Age)`
*   **Pitfall**: 這會導致 **Parameter Sniffing** 問題。第一次執行時若 `@Name` 是 NULL，SQL Server 會產生全表掃描的計畫；下次若傳入具體名字，它仍沿用全表掃描計畫，效能極差。
*   **Fix**: 使用 `OPTION (RECOMPILE)` 或動態 SQL (Dynamic SQL) 針對不同條件組生成專屬語句。

### 5. Abuse of SELECT * (濫用 SELECT *)
*   **Pitfall**: 撈取不需要的欄位（特別是大欄位如 `VARCHAR(MAX)` 或 `XML`）會增加 IO 負擔，並導致 **Covering Index** (覆蓋索引) 失效，迫使引擎進行 **Key Lookup** (回表)。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist (開發階段)
- [ ] **SARGable Check**: `WHERE` 和 `JOIN` 子句中的欄位是否乾淨（無函式包裝）？
- [ ] **Data Type Check**: 應用程式傳入的參數型別（String vs WString, Int vs Long）是否與 Table Schema 完全一致？
- [ ] **Wildcard Check**: 是否避免了 `LIKE '%...` 的寫法？
- [ ] **Loop Check**: 是否在程式碼迴圈中呼叫資料庫 (N+1 問題)？
- [ ] **Column Check**: `SELECT` 清單是否只列出了需要的欄位，而非 `*`？

### Troubleshooting Workflow (診斷階段)
當遇到慢查詢時，請依序檢查：

1.  **取得執行計畫 (Execution Plan)**：
    *   觀察是否有 **Index Scan** 或 **Table Scan** 出現在預期應該是 **Index Seek** 的地方。
2.  **檢查 Predicate (述詞)**：
    *   在 Scan 的運算子屬性中，查看 `Predicate`。是否包含 `CONVERT_IMPLICIT`？如果是，這是型別不匹配。
3.  **檢查 Residual Predicate (殘留述詞)**：
    *   如果由 Seek 變成了 Scan，檢查是否因為欄位被函式包覆導致無法 Seek。
4.  **檢查 IO 統計**：
    *   `SET STATISTICS IO ON`。如果 `Logical Reads` 異常高，通常代表掃描了過多資料頁。

---

## Real-world examples｜實戰案例

### Case 1: The "Year" Report (Non-SARGable vs SARGable)

**Scenario**: 撈取 2023 年的所有訂單。`OrderDate` 上有索引。

**❌ Anti-Pattern (Index Scan)**:
```sql
-- 引擎必須計算每一行的 YEAR(OrderDate) 才能比對，索引失效。
SELECT OrderID, Total
FROM Sales.Orders
WHERE YEAR(OrderDate) = 2023; 
```

**✅ Best Practice (Index Seek)**:
```sql
-- 轉換為範圍查詢，引擎可以直接 Seek 到 2023-01-01 的位置並讀取到 2024-01-01 停止。
SELECT OrderID, Total
FROM Sales.Orders
WHERE OrderDate >= '2023-01-01' 
  AND OrderDate < '2024-01-01';
```

### Case 2: The Silent Killer (Implicit Conversion)

**Scenario**: `NationalIDNumber` 欄位定義為 `VARCHAR(15)`，但應用程式使用 .NET 預設字串 (Unicode)。

**❌ Anti-Pattern (C# / Dapper)**:
```csharp
// Dapper 預設將 string 視為 NVARCHAR
string myId = "12345"; 
connection.Query("SELECT * FROM Employees WHERE NationalIDNumber = @Id", new { Id = myId });
```
*SQL Server 視角*: `WHERE CONVERT(NVARCHAR(15), NationalIDNumber) = @Id` -> **Index Scan**。

**✅ Best Practice**:
```csharp
// 明確指定 AnsiString
connection.Query("SELECT * FROM Employees WHERE NationalIDNumber = @Id", 
    new { Id = new DbString { Value = myId, IsAnsi = true, IsFixedLength = false } });
```
*SQL Server 視角*: `WHERE NationalIDNumber = @Id` -> **Index Seek**。

### Case 3: The N+1 Problem

**Scenario**: 顯示使用者列表及其最新訂單。

**❌ Anti-Pattern (Application Loop)**:
```csharp
var users = db.GetUsers(); // Query 1
foreach (var user in users) {
    // Query 2...N+1: 迴圈每跑一次就敲一次 DB
    user.LastOrder = db.GetLastOrderForUser(user.Id); 
}
```

**✅ Best Practice (JOIN / Set-based)**:
```sql
-- Query 1: 一次撈完
SELECT u.Name, o.OrderDate, o.Total
FROM Users u
OUTER APPLY (
    SELECT TOP 1 OrderDate, Total 
    FROM Orders 
    WHERE UserId = u.Id 
    ORDER BY OrderDate DESC
) o;
```