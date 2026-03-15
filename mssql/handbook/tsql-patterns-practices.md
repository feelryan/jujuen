# 高效 T-SQL 開發模式與最佳實踐 / Efficient T-SQL Patterns & Best Practices

## Mental model｜心智模型

### 1. 集合導向思考 (Set-based Thinking)
在 T-SQL 中，最核心的心智轉換是從 **「程序式 (Procedural)」** 轉向 **「宣告式 (Declarative)」**。
- **Procedural (Loop/Cursor):** 像寫 C# 或 Java 一樣，思考「我要先拿第一行，做運算，再拿下一行...」。這是 SQL Server 的效能殺手。
- **Set-based (Declarative):** 思考「我要的結果集具備什麼特徵？」、「我要如何定義這個集合？」。你告訴 SQL Server **"What to do"**，讓 Query Optimizer 決定 **"How to do it"**。

> **Analogy:**
> 想像你在切菜。
> - **Cursor:** 你拿一把刀，一根一根紅蘿蔔切（Row-by-row）。
> - **Set-based:** 你擁有一台工業級雷射切割機，設定好參數，一次切斷所有紅蘿蔔（All-at-once）。

### 2. 邏輯執行順序 (Logical Query Processing)
寫 SQL 時，你的書寫順序是 `SELECT -> FROM -> WHERE`，但 SQL Server 的邏輯執行順序完全不同。理解這一點能幫助你明白為什麼 `WHERE` 不能用 `SELECT` 裡的 Alias。

1.  **FROM / JOIN** (決定資料來源)
2.  **WHERE** (過濾原始資料列)
3.  **GROUP BY** (分組)
4.  **HAVING** (過濾分組後的資料)
5.  **SELECT** (決定輸出欄位、計算表達式、Window Functions)
6.  **DISTINCT** (去重)
7.  **ORDER BY** (排序)
8.  **TOP / OFFSET-FETCH** (分頁或限制數量)

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 Window Functions 取代 Self-Joins
處理「排名」、「累計」、「前後列比較」或「分組取 Top N」時，Window Functions 是現代 T-SQL 的首選。

- **情境 (Scenario):** 找出每個部門薪水最高的員工。
- **Old School:** 使用 Subquery 做 `GROUP BY` 再 Join 回原表。
- **Best Practice:** 使用 `ROW_NUMBER()` 或 `RANK()`。

```sql
-- Pattern: Top N per Group
WITH RankedEmployees AS (
    SELECT 
        DeptID, Name, Salary,
        ROW_NUMBER() OVER(PARTITION BY DeptID ORDER BY Salary DESC) as Rn
    FROM Employees
)
SELECT * FROM RankedEmployees WHERE Rn = 1;
```

### 2. CTEs (Common Table Expressions) 提升可讀性
當查詢邏輯複雜，充滿巢狀 Subqueries 時，使用 CTE 將邏輯「線性化」。

- **Modular Logic:** 將複雜邏輯拆解成多個 CTE 步驟（Step 1: Filter, Step 2: Aggregate, Step 3: Join）。
- **Recursive CTE:** 處理階層資料（如組織圖、BOM 表）的標準解法。

> **注意：** CTE 只是語法糖（Syntax Sugar），通常不會被 Materialized（除非在極端優化情境下），它就像一個一次性的 View。

### 3. APPLY 運算子的強大威力
`CROSS APPLY` 和 `OUTER APPLY` 是 T-SQL 的隱藏寶石，類似於 "For Each Row" 的 Join。

- **情境 A：解析複雜資料**
  當你需要對 Table A 的每一行，呼叫一個 Table-Valued Function (TVF) 或解析 JSON/XML 時。
- **情境 B：Top N per Row**
  當你需要針對每一行主表資料，關聯子表中的「最新 3 筆」紀錄。

```sql
-- Pattern: Join with Top N logic inside
SELECT C.CustomerName, O.OrderDate, O.Amount
FROM Customers C
CROSS APPLY (
    SELECT TOP 3 * 
    FROM Orders O 
    WHERE O.CustomerID = C.CustomerID 
    ORDER BY O.OrderDate DESC
) O;
```

### 4. SARGable Queries (Search ARGument ABLE)
確保你的 `WHERE` 條件能利用索引。**永遠不要在 Table Column 上套用函數**進行比較。

- **Bad:** `WHERE YEAR(OrderDate) = 2023` (導致 Index Scan，無法利用索引 Seek)
- **Good:** `WHERE OrderDate >= '2023-01-01' AND OrderDate < '2024-01-01'` (允許 Index Seek)

### 5. 存在性檢查 (Existence Check)
檢查資料是否存在時，使用 `EXISTS` 或 `NOT EXISTS`，通常比 `IN` 或 `COUNT(*) > 0` 更高效且安全（特別是處理 NULL 值時）。

- **Pattern:** `IF EXISTS (SELECT 1 FROM Table WHERE ...) BEGIN ... END`

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Scalar User-Defined Functions (Scalar UDFs)
這是 T-SQL 中最常見的效能殺手。
- **問題：** Scalar UDF 會強迫查詢引擎切換到 "Row-by-row" 模式，並且通常會阻止並行處理 (Parallelism)。
- **解法：** 改用 Inline Table-Valued Functions (iTVF) 或直接將邏輯寫入查詢中。

### 2. RBAR (Row By Agonizing Row)
- **現象：** 使用 Cursor 或 While Loop 逐行更新資料。
- **後果：** 鎖定時間長、Transaction Log 暴增、極慢。
- **解法：** 重構為 Set-based UPDATE/INSERT。

### 3. `SELECT *`
- **問題：** 
  1. 增加不必要的 Network I/O。
  2. 導致 Covering Index 失效（因為多選了索引沒包含的欄位，觸發 Key Lookup）。
  3. 當 Schema 變更時，應用程式容易崩潰。
- **解法：** 明確列出需要的欄位。

### 4. 濫用 CTE 進行重複計算
- **陷阱：** 如果你在主查詢中多次引用同一個 CTE，SQL Server **會重新執行該 CTE 的邏輯多次**。
- **解法：** 如果 CTE 計算成本很高且需多次使用，請先將結果存入 Temp Table (`#Temp`)。

### 5. 隱式型別轉換 (Implicit Conversion)
- **現象：** `WHERE VarcharColumn = N'String'` (比較 VARCHAR 與 NVARCHAR)。
- **後果：** 為了比較，SQL Server 必須轉換欄位型別，導致索引失效 (Index Scan)。
- **解法：** 確保變數型別與欄位型別一致。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist
在提交 PR 或部署 SQL 腳本前，請檢查：

- [ ] **SARGable:** `WHERE` 和 `JOIN` 條件中的欄位是否乾淨（無函數包覆）？
- [ ] **No `SELECT *`:** 是否只選取了必要的欄位？
- [ ] **No Scalar UDFs:** 是否避免了在 `SELECT` 或 `WHERE` 中使用純量函數？
- [ ] **Set-based:** 是否消除了不必要的 Cursor 或 Loop？
- [ ] **NOLOCK (Caution):** 如果使用了 `WITH (NOLOCK)`，是否清楚 Dirty Read 的風險？（在金融或高準確度場景應避免）。
- [ ] **Transaction:** 修改資料的操作是否包在 `BEGIN TRAN ... COMMIT/ROLLBACK` 中，並有 `TRY...CATCH` 錯誤處理？

### Performance Tuning Workflow (Simplified)
當遇到慢查詢時：

1. **檢查執行計畫 (Execution Plan):** 是否有 Index Scan？是否有 Key Lookup？
2. **檢查 Warnings:** 是否有 Implicit Conversion 或 Missing Index 提示？
3. **檢查 I/O:** `SET STATISTICS IO ON`。Logical Reads 是否過高？
4. **重構邏輯:** 能否用 Window Function 或 `APPLY` 簡化 Query？

---

## Real-world examples｜實戰案例

### Case 1: 資料去重 (Deduplication)
**需求：** 資料表中有重複的 Log，需刪除舊的，只保留最新的一筆（依據 `LogDate`）。

```sql
-- 使用 CTE 搭配 Window Function 進行刪除
-- 這是非常經典且高效的模式，直接對 CTE 執行 DELETE
WITH Duplicates AS (
    SELECT 
        LogID, 
        LogDate,
        ROW_NUMBER() OVER(
            PARTITION BY UserID, ActionType  -- 定義什麼算「重複」
            ORDER BY LogDate DESC            -- 定義保留「哪一個」(最新的)
        ) AS Rn
    FROM UserLogs
)
DELETE FROM Duplicates
WHERE Rn > 1; -- 刪除排名第 1 以外的所有資料
```

### Case 2: 計算移動平均 (Moving Average)
**需求：** 計算股票每日的 7 日移動平均價格。

```sql
SELECT 
    Symbol,
    TradeDate,
    ClosePrice,
    AVG(ClosePrice) OVER(
        PARTITION BY Symbol 
        ORDER BY TradeDate
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW -- 定義 Window Frame
    ) AS MovingAvg7Day
FROM StockPrices;
```

### Case 3: 比較前後期資料 (YoY, MoM)
**需求：** 比較本月營收與上個月營收的成長率。

```sql
WITH MonthlySales AS (
    SELECT 
        Year = YEAR(OrderDate),
        Month = MONTH(OrderDate),
        TotalAmount = SUM(Amount)
    FROM Orders
    GROUP BY YEAR(OrderDate), MONTH(OrderDate)
)
SELECT 
    Year, Month, TotalAmount,
    -- 取得同一組排序的前一列資料
    PrevMonthAmount = LAG(TotalAmount, 1, 0) OVER(ORDER BY Year, Month),
    GrowthRate = CASE 
        WHEN LAG(TotalAmount, 1, 0) OVER(ORDER BY Year, Month) = 0 THEN 0
        ELSE (TotalAmount * 1.0 / LAG(TotalAmount, 1, 0) OVER(ORDER BY Year, Month)) - 1 
    END
FROM MonthlySales;
```