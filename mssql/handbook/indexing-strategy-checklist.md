# 索引設計策略與實戰 Checklist / Indexing Strategy & Practical Checklist

## Mental model｜心智模型

在深入語法之前，你需要建立正確的索引運作心智模型。不要只把索引當作「加速器」，請將其視為**「為了讀取效能而犧牲寫入效能的冗餘資料結構」**。

### 1. 索引的本質是「排序後的副本」 (Sorted Copy)
- **Clustered Index (CI)**：就是資料表本身。資料在硬碟上的物理排序依據。每個表只能有一個（通常是 PK）。
- **Non-Clustered Index (NCI)**：這是另外建立的 B-Tree 結構。葉子節點 (Leaf Nodes) 包含索引鍵值 (Key) 以及指向主資料的指標 (Row Locator/Clustered Key)。
- **Trade-off**：每當你 `INSERT`, `UPDATE`, `DELETE` 時，SQL Server 必須同步維護所有相關的 NCI。索引越多，寫入越慢。

### 2. 覆蓋索引 (Covering Index) 是終極目標
- **Key Lookup (Bookmark Lookup)**：當 NCI 找到了你要的 Row，但索引內沒有包含查詢所需的其他欄位（例如 `SELECT *`），資料庫必須跳回 CI 去抓取完整資料。這是一個昂貴的隨機 I/O 操作。
- **Covering**：如果 NCI 的葉子節點已經包含了查詢所需的所有欄位（透過 `INCLUDE`），資料庫就不需要回查 CI。這能帶來巨大的效能提升。

### 3. 選擇性 (Selectivity) 與 臨界點 (Tipping Point)
- 如果一個索引的過濾條件會回傳資料表中 30% 以上的資料（例如性別欄位），SQL Server 最佳化器通常會選擇直接 **Table Scan** 而忽略索引。因為隨機讀取索引再回查資料的成本，比順序讀取整張表還高。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 INCLUDE 子句 (The "Covering" Pattern)
不要把所有欄位都放在 Index Key (B-Tree 的導航鍵) 中，這會讓 B-Tree 變大且維護昂貴。
- **Key Columns (`ON`)**：放在 `WHERE`, `JOIN`, `ORDER BY` 中的欄位。
- **Included Columns (`INCLUDE`)**：只在 `SELECT` 列表顯示，但不參與過濾的欄位。

```sql
-- Pattern: Covering Index
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
ON dbo.Orders (CustomerId, OrderDate) -- 用於搜尋與排序 (B-Tree nodes)
INCLUDE (TotalAmount, Status);        -- 僅存於葉節點，用於滿足 SELECT (Payload)
```

### 2. 最左前綴原則 (Leftmost Prefix Rule)
複合索引 (Composite Index) 的順序至關重要。索引 `(A, B, C)` 就像電話簿先按姓、再按名排序。
- 它可以支援搜尋 `A`。
- 它可以支援搜尋 `A` AND `B`。
- 它**無法**有效支援只搜尋 `B` 或 `C` 的查詢。

### 3. 針對稀疏狀態使用篩選索引 (Filtered Indexes)
如果你的資料表很大，但查詢通常只關心「未結案」或「異常」的資料（佔總量少數），請使用 `WHERE` 子句建立索引。這能大幅減少索引大小與維護成本。

```sql
-- Pattern: Filtered Index for Queues or Soft Deletes
CREATE NONCLUSTERED INDEX IX_Orders_Pending
ON dbo.Orders (OrderDate)
INCLUDE (TotalAmount, CustomerId)
WHERE Status = 'Pending'; -- 只索引待處理訂單
```

### 4. Foreign Keys 務必建立索引
SQL Server 不會自動為 FK 建立索引。如果在 `JOIN` 時 FK 沒有索引，或者在刪除 Parent 表資料時，可能會導致 Child 表發生 Table Scan 甚至鎖表。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. SARGable 殺手：對欄位進行函數運算
**Anti-pattern**: 在 `WHERE` 子句中對欄位進行運算，會導致索引失效（變成 Scan）。
- ❌ `WHERE YEAR(OrderDate) = 2023` (無法使用 OrderDate 索引)
- ✅ `WHERE OrderDate >= '2023-01-01' AND OrderDate < '2024-01-01'` (SARGable)

### 2. 隱式轉型 (Implicit Conversion)
**Anti-pattern**: 資料型別不匹配。最常見的是 `VARCHAR` vs `NVARCHAR`。
- 如果欄位是 `VARCHAR`，但查詢傳入 `NVARCHAR` (例如 .NET 的 String 預設是 Unicode)，SQL Server 會將欄位轉型以匹配參數，這會導致索引掃描 (Index Scan) 而非搜尋 (Index Seek)。

### 3. 濫用 GUID 作為 Clustered Index
**Anti-pattern**: 使用 `NEWID()` 產生的隨機 GUID 作為 PK (Clustered Index)。
- **後果**：導致嚴重的 **Page Fragmentation** (頁面破碎)。因為隨機 GUID 會導致資料被插入到 B-Tree 的隨機位置，造成頻繁的 Page Split。
- **修正**：改用 `INT IDENTITY` 或 `NEWSEQUENTIALID()`，或將 GUID 設為 Non-Clustered PK。

### 4. 索引過度設計 (Over-Indexing)
**Anti-pattern**: 為每個欄位都建立單獨的索引。
- SQL Server 很難有效地合併多個單欄位索引。通常一個精心設計的複合索引 (Composite Index) 遠勝過三個單欄位索引。且過多索引會拖慢 `INSERT`/`UPDATE`。

---

## Checklists & workflows｜檢查清單與流程

### Index Design Decision Tree (索引設計決策樹)

在建立新索引前，請依序檢查：

- [ ] **SARGable Check**: 我的查詢語法是否乾淨？有沒有對欄位做函數運算？
- [ ] **Duplicate Check**: 是否已經存在類似的索引？(例如已有 `(A, B)`，就不需要 `(A)`)。
- [ ] **Selectivity Check**: 這個欄位的重複值多嗎？(性別、布林值通常不適合單獨索引，除非用 Filtered Index)。
- [ ] **Covering Check**: 查詢是否頻繁觸發 Key Lookup？是否需要 `INCLUDE` 額外欄位以達成 Covering？
- [ ] **Write Impact**: 這個表寫入頻率高嗎？如果是高頻寫入表 (Log, Audit)，索引數量應保持最低。

### Maintenance & Review Workflow (維護流程)

- [ ] **Missing Index DMVs**: 定期檢查 `sys.dm_db_missing_index_details`，但不要盲目照做（SQL Server 的建議通常很貪婪）。
- [ ] **Unused Index Cleanup**: 定期檢查 `sys.dm_db_index_usage_stats`。如果一個索引只有 `user_updates` 但沒有 `user_seeks/scans`，代表它只在拖累寫入效能，**刪掉它**。
- [ ] **Fragmentation**: 對於高變動的表，定期執行 `REORGANIZE` (線上輕量) 或 `REBUILD` (重組)。

---

## Real-world examples｜實戰案例

### Case 1: The "Soft Delete" Trap (軟刪除陷阱)

**情境**：
一個擁有 1000 萬筆資料的 `Users` 表，大部分查詢都有 `WHERE IsDeleted = 0`。開發者在 `IsDeleted` 上建了索引。

**問題**：
`IsDeleted = 0` 的資料佔了 99%。這個索引毫無選擇性 (Non-selective)，SQL Server 甚至不會用它，或者用了反而更慢。

**解決方案**：
不要索引 `IsDeleted`。反之，建立 **Filtered Index** 排除已刪除資料，或者將 `IsDeleted = 0` 作為其他索引的 Filter 條件。

```sql
-- 針對 Email 搜尋，但只針對未刪除的用戶建立索引
CREATE UNIQUE NONCLUSTERED INDEX IX_Users_Email
ON dbo.Users (Email)
WHERE IsDeleted = 0;
```
*效益：索引更小，搜尋更快，且自動保證未刪除用戶的 Email 唯一性。*

### Case 2: The "Dashboard Query" Optimization (儀表板查詢優化)

**情境**：
電商後台首頁需要顯示：「最近 7 天的訂單總金額，按地區分組」。
查詢：`SELECT Region, SUM(Total) FROM Orders WHERE OrderDate > @Date GROUP BY Region`

**原始索引**：
`IX_Orders_OrderDate` (只有 OrderDate)。

**執行計畫分析**：
SQL Server 使用 `IX_Orders_OrderDate` 找到範圍內的 Row，但必須回到 Clustered Index 去抓取 `Region` 和 `Total` (Key Lookup)。如果最近 7 天訂單量大，這會變成 Random I/O 風暴。

**優化索引**：
```sql
CREATE NONCLUSTERED INDEX IX_Orders_OrderDate_Covering
ON dbo.Orders (OrderDate)       -- 1. 用於過濾範圍 (Range Scan)
INCLUDE (Region, Total);        -- 2. 用於計算，無需回查 (Covering)
```
*注意：不要把 `Region` 放在 Key 的第一位，因為查詢條件是 `OrderDate` 範圍。範圍查詢的欄位通常放在 Key 的最後，或是依賴 `INCLUDE`。*