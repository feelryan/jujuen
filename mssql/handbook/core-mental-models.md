# 核心運作心智模型：從邏輯到物理 / Core Mental Models: Logical to Physical Processing

## Mental model｜心智模型

要精通 SQL Server，必須打破一般程式語言（如 C#, Java, Python）的「程序式（Procedural）」思維，轉向「宣告式（Declarative）」與「集合（Set-based）」思維。

### 1. 宣告式語言 vs. 執行計畫 (The "What" vs. The "How")
SQL 是一種宣告式語言。你告訴 SQL Server **「你要什麼資料 (What)」**，而不是 **「如何取得資料 (How)」**。
- **Developer's Job**: 定義邏輯需求（Logical Query）。
- **Optimizer's Job**: 決定物理路徑（Physical Execution Plan）。它會根據統計資訊（Statistics）、索引（Indexes）和系統資源，計算出成本最低的執行路徑。
- **Key Insight**: 效能優化的本質，往往是「重寫查詢」或「調整結構」，讓 Optimizer 更容易找到那條最短路徑，而不是強行指定它怎麼走。

### 2. 邏輯處理順序 (Logical Processing Order)
這是開發者最常誤解的模型。雖然你寫 SQL 的順序是 `SELECT ... FROM ... WHERE`，但 SQL Server **理解** 的順序完全不同。

**The River Flow Model (河流過濾模型):**
想像資料像河流一樣流過一系列的閘門，每個階段產生的虛擬資料表（Virtual Table）會傳給下一個階段：

1.  **FROM / JOIN**: 決定資料來源，產生笛卡爾積或連結後的集合。（河流源頭）
2.  **WHERE**: 過濾資料列（Row filtering）。（第一道閘門，越早過濾越好）
3.  **GROUP BY**: 將資料分組。（將水流分流）
4.  **HAVING**: 過濾分組後的資料。（第二道閘門）
5.  **SELECT**: 決定要顯示哪些欄位，處理表達式。（裝瓶）
6.  **DISTINCT**: 去除重複。（過濾重複瓶子）
7.  **ORDER BY**: 排序結果。（最後的陳列擺設）
8.  **TOP / OFFSET-FETCH**: 最終截斷。（只取前幾瓶）

> **Practical Implication**: 這就是為什麼你不能在 `WHERE` 子句中使用 `SELECT` 定義的 Alias（別名），因為在邏輯上，`WHERE` 執行時 `SELECT` 還沒發生。

### 3. 物理執行：集合運算 (Physical Execution: Set-based Operations)
在物理層面，SQL Server 傾向於一次處理「一批」資料，而不是「一筆」資料。
- **Mental Shift**: 避免 "Row-by-Row" (RBAR - Row By Agonizing Row) 的思考模式。迴圈（Cursor/While loop）通常是效能殺手。
- **Cost-Based Optimization**: Optimizer 就像一個精打細算的會計師。如果它認為「全表掃描 (Scan)」比「查索引 (Seek) 再回查 (Lookup)」更便宜（例如要取出的資料量很大），它就會選擇掃描。不要盲目認為「有索引就一定會快」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. SARGable Queries (Search ARGument ABLE)
撰寫「對索引友善」的查詢是連結邏輯與物理的關鍵。
- **Pattern**: 保持欄位原始狀態，不要對欄位進行運算。
- **Good**: `WHERE OrderDate >= '2023-01-01' AND OrderDate < '2023-02-01'`
- **Bad**: `WHERE YEAR(OrderDate) = 2023 AND MONTH(OrderDate) = 1` (這會導致 Index Scan，因為必須計算每一行)。

### 2. The "Filter Early" Principle
利用邏輯順序，儘早減少資料量。
- **Pattern**: 在 `WHERE` 階段就過濾掉大部分資料，而不是留到 `HAVING` 或應用層處理。
- **Practice**: 在 JOIN 之前，如果能先過濾 Table A 的資料，就先過濾（雖然現代 Optimizer 會嘗試做 Predicate Pushdown，但明確寫出來更保險且易讀）。

### 3. CTE & Derived Tables for Logical Scoping
當邏輯複雜時，使用 Common Table Expressions (CTE) 來強制邏輯分層，這有助於人類閱讀，也能讓 Optimizer 理解你的意圖。
- **Pattern**: 先計算 Window Functions (如 `ROW_NUMBER()`)，再在外層進行過濾。
- **Example**:
  ```sql
  ;WITH Ranked AS (
      SELECT *, ROW_NUMBER() OVER(PARTITION BY UserID ORDER BY Date DESC) as rn
      FROM Logins
  )
  SELECT * FROM Ranked WHERE rn = 1; -- 邏輯清晰：先排名，後過濾
  ```

### 4. Parameterization (參數化)
- **Pattern**: 使用 `sp_executesql` 或 ORM 的參數化查詢，而不是字串串接。
- **Why**: 讓 SQL Server 能夠重複使用執行計畫 (Plan Reuse)，減少編譯成本 (Compilation Cost)，並避免 SQL Injection。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Select Star" Trap (`SELECT *`)
- **Pitfall**: 貪圖方便使用 `SELECT *`。
- **Consequence**:
  - **Logical**: 破壞了程式碼的合約（Schema 變更時程式可能崩潰）。
  - **Physical**: 增加了 I/O 負擔（讀取不必要的欄位），可能導致 Covering Index 失效（因為索引沒包含所有欄位，被迫回表查詢 Key Lookup），並增加記憶體授予 (Memory Grant)。

### 2. Implicit Conversions (隱式轉型)
- **Pitfall**: 比較不同資料型別，例如 `VARCHAR` 欄位與 `NVARCHAR` 參數比較。
- **Consequence**: SQL Server 必須將欄位轉型以符合參數優先級，這會導致 **Index Scan**（無法使用索引搜尋）並增加 CPU 消耗。
- **Detection**: 在執行計畫中尋找帶有驚嘆號的黃色警告。

### 3. Procedural Logic in SQL (濫用 Cursor/Loop)
- **Pitfall**: 把 SQL 當作 C# 寫，用 `WHILE` 迴圈逐筆處理資料。
- **Consequence**: 阻礙 SQL Server 使用並行處理 (Parallelism) 和批次運算優勢，效能通常比 Set-based 寫法慢 10-100 倍。

### 4. Non-Deterministic Functions in Predicates
- **Pitfall**: 在 `WHERE` 中使用 `NEWID()` 或過度複雜的自訂函數 (UDF)。
- **Consequence**: 純量函數 (Scalar UDF) 經常會導致執行計畫變成序列執行 (Serial execution)，並嚴重誤判成本估算 (Cardinality Estimation)。

---

## Checklists & workflows｜檢查清單與流程

### Query Design Checklist (設計階段檢查)
- [ ] **SARGability**: 我的 `WHERE` 和 `JOIN` 條件是否對索引友善？有沒有對欄位進行函數運算？
- [ ] **Data Types**: 傳入的參數型別是否與資料表欄位型別完全一致？
- [ ] **Selectivity**: 我是否只選取了需要的欄位（No `SELECT *`）？
- [ ] **Set-based**: 我是否避免了不必要的 Cursor 或 Loop？
- [ ] **Logical Order**: `WHERE` 子句是否使用了尚未定義的 Alias？（如果有，改用 CTE 或 Derived Table）。

### Performance Troubleshooting Workflow (效能除錯流程)
當一個查詢變慢時，依照「邏輯 -> 物理」順序檢查：

1.  **Logical Check**:
    - 查詢邏輯是否合理？是否撈取了過多不必要的資料列？
    - 是否有 Cartesian Product (漏掉 JOIN 條件)？
2.  **Statistics Check**:
    - 統計資訊是否過期？(Optimizer 依據錯誤資訊做決策)
    - `SET STATISTICS IO ON`: 實際讀取的 Page 數是否遠高於預期？
3.  **Execution Plan Check**:
    - **Scan vs. Seek**: 是否在大表上發生了 Table Scan？
    - **Key Lookups**: 是否頻繁回表？(考慮 Covering Index)
    - **Warnings**: 有沒有隱式轉型或記憶體不足的警告？
    - **Actual vs. Estimated**: 預估行數與實際行數差異是否巨大？(通常暗示統計資訊問題或複雜的 Parameter Sniffing)。

---

## Real-world examples｜實戰案例

### Case 1: The "Alias in WHERE" Error (邏輯順序誤區)

**Scenario**: 開發者想過濾計算後的欄位。

```sql
-- ❌ 錯誤寫法：會報錯 "Invalid column name 'Total'"
SELECT OrderID, (Quantity * UnitPrice) AS Total
FROM OrderDetails
WHERE Total > 1000;
```

**Why**: 根據邏輯順序，`WHERE` 在 `SELECT` 之前執行，此時 `Total` 還不存在。

**✅ 修正寫法 (Option A: 重複表達式)**:
```sql
SELECT OrderID, (Quantity * UnitPrice) AS Total
FROM OrderDetails
WHERE (Quantity * UnitPrice) > 1000;
```

**✅ 修正寫法 (Option B: 使用 CTE - 推薦)**:
```sql
;WITH Calculated AS (
    SELECT OrderID, (Quantity * UnitPrice) AS Total
    FROM OrderDetails
)
SELECT * FROM Calculated WHERE Total > 1000;
```

### Case 2: The Implicit Conversion Killer (物理執行陷阱)

**Scenario**: `PhoneNumber` 欄位是 `VARCHAR(20)` (有索引)，但應用程式傳入 `NVARCHAR` (Unicode)。

```sql
-- ❌ 隱式轉型：導致 Index Scan
-- @PhoneParam is NVARCHAR(20)
SELECT * FROM Customers WHERE PhoneNumber = @PhoneParam;
```

**Analysis**:
- SQL Server 的型別優先級中，`NVARCHAR` > `VARCHAR`。
- 資料庫被迫將每一行的 `PhoneNumber` 轉成 `NVARCHAR` 來跟參數比對。
- 結果：無法使用 Index Seek，必須讀取整張表。

**✅ 修正寫法**:
確保應用程式端傳入的參數型別是 `AnsiString` / `VARCHAR`，或者在 SQL 中明確轉型參數（而非欄位）：

```sql
-- 強制將參數轉為 VARCHAR，恢復 SARGability
SELECT * FROM Customers WHERE PhoneNumber = CAST(@PhoneParam AS VARCHAR(20));
```