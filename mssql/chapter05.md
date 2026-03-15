# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，SQL 不僅僅是用來 CRUD (Create, Read, Update, Delete) 的工具，更是處理複雜資料邏輯、優化應用程式效能的關鍵層。本章節專注於 T-SQL 的進階模式，這些技巧能顯著減少應用程式層（Application Layer）的程式碼複雜度，並提升批次處理的效率。

In the career of a Senior Software Engineer, SQL is more than just a tool for CRUD (Create, Read, Update, Delete); it is a critical layer for handling complex data logic and optimizing application performance. This chapter focuses on advanced T-SQL patterns. These techniques can significantly reduce code complexity in the Application Layer and improve batch processing efficiency.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用 Window Functions 解決複雜分析問題**：如計算移動平均、排名、以及經典的「Gaps and Islands」問題。
    **Solve complex analytical problems using Window Functions**: Such as calculating moving averages, rankings, and the classic "Gaps and Islands" problem.
2.  **掌握遞迴查詢 (Recursive CTE)**：優雅地處理組織架構圖、BOM (Bill of Materials) 等階層式資料。
    **Master Recursive CTEs**: Elegantly handle hierarchical data like organizational charts and BOMs (Bill of Materials).
3.  **評估 MERGE 的使用時機與風險**：理解 `MERGE` 語法的便利性及其在高併發環境下的潛在 Deadlock 風險。
    **Evaluate the timing and risks of MERGE**: Understand the convenience of `MERGE` syntax and its potential deadlock risks in high-concurrency environments.
4.  **高效整合 JSON 資料**：在關聯式資料庫中儲存、查詢與索引 JSON 文件，實現 Hybrid Data Model。
    **Efficiently integrate JSON data**: Store, query, and index JSON documents within a relational database to achieve a Hybrid Data Model.
5.  **優化大量資料寫入 (Bulk Operations)**：理解 Log 寫入最小化與大量資料匯入的最佳實踐。
    **Optimize Bulk Operations**: Understand minimal logging and best practices for bulk data imports.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Window Functions：資料的「滑動視窗」
## 2.1 Window Functions: The "Sliding Window" of Data

**直覺類比**：
想像你在審閱一份 excel 報表。`GROUP BY` 會把多行「摺疊」成一行（例如算總和），你失去了原始資料的細節。而 Window Function 就像是在原始資料旁加了一欄「透視鏡」，它能看到當前這一行「前後左右」的資料（例如：這一行與上一行的差值、這一行在全體中的排名），但**不改變原始行數**。

**Intuitive Analogy**:
Imagine you are reviewing an Excel report. `GROUP BY` collapses multiple rows into one (e.g., calculating a sum), causing you to lose the details of the original data. A Window Function is like adding a "lens" column next to the original data. It allows you to see data "around" the current row (e.g., the difference between this row and the previous one, or this row's rank within the whole), but **without changing the original number of rows**.

**關鍵語法 (Key Syntax)**:
`Function() OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN ...)`

## 2.2 Recursive CTE：自我參照的迴圈
## 2.2 Recursive CTE: Self-Referencing Loops

**直覺類比**：
這就像是一個 `while` 迴圈或遞迴函數。你定義一個「起點」（Anchor Member），然後定義「如何從上一層找到下一層」（Recursive Member），直到找不到資料為止。

**Intuitive Analogy**:
This is like a `while` loop or a recursive function. You define a "starting point" (Anchor Member) and then define "how to find the next layer from the previous one" (Recursive Member) until no more data is found.

## 2.3 JSON in SQL：結構與彈性的橋樑
## 2.3 JSON in SQL: A Bridge Between Structure and Flexibility

**心智模型**：
不要將 SQL Server 視為單純的表格儲存。在現代架構中，它經常扮演「強型別資料」與「弱型別 Payload」的轉換器。利用 `OPENJSON` 將 JSON 轉為 Table，或用 `FOR JSON` 將 Table 轉為 API 回傳格式，能減少 Backend Code 的 mapping 成本。

**Mental Model**:
Do not view SQL Server merely as tabular storage. In modern architectures, it often acts as a converter between "strongly-typed data" and "weakly-typed payloads." Using `OPENJSON` to convert JSON to Tables, or `FOR JSON` to convert Tables to API response formats, can reduce mapping costs in the Backend Code.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 複雜報表與即時儀表板 (Complex Reporting & Real-time Dashboards)

在系統設計中，為了效能，我們常需避免將大量原始資料拉回 Application Server 進行運算。
In system design, to ensure performance, we often need to avoid pulling large amounts of raw data back to the Application Server for processing.

-   **場景**：計算使用者的「連續登入天數」或「過去 7 天的移動平均消費」。
-   **Scenario**: Calculating a user's "consecutive login days" or "7-day moving average spending".
-   **影響**：使用 Window Functions 可在資料庫層級完成 O(N log N) 的排序與計算，大幅減少網路傳輸量 (Network I/O) 與 App Server 的記憶體壓力。
-   **Impact**: Using Window Functions allows O(N log N) sorting and calculation at the database level, significantly reducing Network I/O and memory pressure on the App Server.

## 3.2 階層式權限與組織管理 (Hierarchical Permissions & Org Management)

-   **場景**：RBAC (Role-Based Access Control) 系統中，查詢某個角色繼承的所有權限，或是查詢某個經理下轄的所有員工（包含下屬的下屬）。
-   **Scenario**: In an RBAC system, querying all permissions inherited by a role, or querying all employees under a manager (including subordinates of subordinates).
-   **設計決策**：雖然 NoSQL (Graph DB) 擅長此類查詢，但在關聯式資料庫為主體的系統中，引入額外的 Graph DB 維護成本過高。Recursive CTE 是標準且高效的解決方案。
-   **Design Decision**: While NoSQL (Graph DB) excels at such queries, introducing an additional Graph DB in a relational-centric system incurs high maintenance costs. Recursive CTE is the standard and efficient solution.

## 3.3 高吞吐量資料同步 (High-Throughput Data Sync)

-   **場景**：每晚從 Data Warehouse 或第三方 API 同步百萬筆產品庫存。
-   **Scenario**: Syncing millions of product inventory records nightly from a Data Warehouse or third-party API.
-   **反模式**：使用 ORM 逐筆 `INSERT` 或 `UPDATE`。
-   **Anti-pattern**: Using an ORM to `INSERT` or `UPDATE` row by row.
-   **最佳實踐**：使用 `SqlBulkCopy` (C#) 或 T-SQL `BULK INSERT` 先寫入 Staging Table，再透過 `MERGE` 或 Set-based SQL 批次更新至 Main Table。
-   **Best Practice**: Use `SqlBulkCopy` (C#) or T-SQL `BULK INSERT` to write to a Staging Table first, then use `MERGE` or Set-based SQL to batch update the Main Table.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 解決 "Gaps and Islands" 問題 (Solving "Gaps and Islands")

**背景 (Context)**：
我們有一個 `UserLogins` 表，記錄使用者登入日期。我們需要找出每個使用者「連續登入」的區間（Islands）。這是面試與實務中極為經典的題目。

**Context**:
We have a `UserLogins` table recording user login dates. We need to identify the "consecutive login" periods (Islands) for each user. This is a classic problem in both interviews and practice.

**資料 (Data)**:
User A logins: `2023-01-01`, `2023-01-02`, `2023-01-03` (Streak 1), `2023-01-05`, `2023-01-06` (Streak 2).

**思考步驟 (Thinking Steps)**:
1.  如果日期是連續的，那麼 `LoginDate` 減去 `RowNumber` 應該會得到一個「恆定」的基準日期。
2.  如果中間有斷層（Gap），這個基準日期就會改變。
3.  根據這個基準日期分組 (Group By)，就能抓出連續區間。

1.  If dates are consecutive, then `LoginDate` minus `RowNumber` should yield a "constant" base date.
2.  If there is a gap, this base date will shift.
3.  Grouping by this base date allows us to identify consecutive intervals.

**程式碼 (Code)**:

```sql
WITH RankedLogins AS (
    SELECT 
        UserId,
        LoginDate,
        -- Generate a sequential number for each user's logins ordered by date
        ROW_NUMBER() OVER (PARTITION BY UserId ORDER BY LoginDate) as rn
    FROM UserLogins
),
GroupedLogins AS (
    SELECT 
        UserId,
        LoginDate,
        -- Magic happens here: Date - RowNumber = Constant for consecutive dates
        DATEADD(day, -rn, LoginDate) as GroupId
    FROM RankedLogins
)
SELECT 
    UserId,
    MIN(LoginDate) as StartDate,
    MAX(LoginDate) as EndDate,
    COUNT(*) as ConsecutiveDays
FROM GroupedLogins
GROUP BY UserId, GroupId
ORDER BY UserId, StartDate;
```

**複雜度分析 (Complexity Analysis)**:
-   **Time**: O(N log N) 主要消耗在 `ROW_NUMBER()` 的排序上。
-   **Space**: O(N) 用於儲存 CTE 的中間結果。

## 4.2 JSON 資料處理與索引 (JSON Processing & Indexing)

**背景 (Context)**：
電商系統中，產品屬性（顏色、尺寸、材質）千變萬化，我們決定用 JSON 欄位 `Attributes` 儲存，避免 EAV (Entity-Attribute-Value) 模式的效能惡夢。但我們需要高效查詢「所有紅色產品」。

**Context**:
In an e-commerce system, product attributes (color, size, material) vary wildly. We decide to store them in a JSON column `Attributes` to avoid the performance nightmare of the EAV (Entity-Attribute-Value) pattern. However, we need to efficiently query "all red products".

**Naive Approach**:
`WHERE JSON_VALUE(Attributes, '$.color') = 'Red'`
*缺點 (Drawback)*: 無法使用索引，導致 Full Table Scan。
*Drawback*: Cannot use indexes, resulting in a Full Table Scan.

**Optimized Approach (Computed Column + Index)**:

```sql
-- 1. Add a computed column based on the JSON property
ALTER TABLE Products
ADD Color AS CAST(JSON_VALUE(Attributes, '$.color') AS NVARCHAR(50));

-- 2. Index the computed column
CREATE INDEX IX_Products_Color ON Products(Color);

-- 3. Query (SQL Server optimizer will automatically pick up the index)
SELECT * FROM Products WHERE JSON_VALUE(Attributes, '$.color') = 'Red';
-- OR simply
SELECT * FROM Products WHERE Color = 'Red';
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 MERGE 的併發死鎖 (Concurrency Deadlocks with MERGE)

-   **錯誤案例 (Pitfall)**：在高併發的 OLTP 系統中（例如每秒數百次交易），直接使用 `MERGE` 語句進行 Upsert (Update if exists, Insert if not)。
-   **Pitfall**: Using `MERGE` statements directly for Upserts (Update if exists, Insert if not) in a high-concurrency OLTP system (e.g., hundreds of transactions per second).
-   **原因 (Why)**：`MERGE` 在某些情況下對 Index 的鎖定機制較為激進，且不是原子性的（在極端 Race Condition 下可能報錯 Primary Key Violation 或 Deadlock）。
-   **Why**: `MERGE` can have aggressive locking mechanisms on indexes and is not strictly atomic in terms of concurrency (it can throw Primary Key Violation or Deadlock errors under extreme Race Conditions).
-   **替代方案 (Alternative)**：
    1.  使用 `UPDLOCK, SERIALIZABLE` hint 的傳統 `IF EXISTS ... UPDATE ELSE INSERT` 模式。
    2.  或者先嘗試 `UPDATE`，若 `@@ROWCOUNT = 0` 則 `INSERT`（需處理例外）。
    3.  對於大量批次處理（ETL），`MERGE` 仍然是好選擇，但在 OLTP 需謹慎。

## 5.2 濫用遞迴 CTE (Abusing Recursive CTE)

-   **錯誤案例 (Pitfall)**：在沒有 `MAXRECURSION` 限制的情況下遍歷可能存在循環參照（Circular Reference）的圖形結構。
-   **Pitfall**: Traversing a graph structure that may contain Circular References without a `MAXRECURSION` limit.
-   **後果 (Consequence)**：無限迴圈導致資料庫資源耗盡。
-   **Consequence**: Infinite loops leading to database resource exhaustion.
-   **修正 (Fix)**：始終設定 `OPTION (MAXRECURSION n)`，並在遞迴邏輯中加入路徑檢查以防止循環。

## 5.3 Window Functions 的排序成本 (Sorting Cost of Window Functions)

-   **錯誤案例 (Pitfall)**：在超大資料表上頻繁使用 `OVER (PARTITION BY A ORDER BY B)`，卻沒有對應的索引 `(A, B)`。
-   **Pitfall**: Frequently using `OVER (PARTITION BY A ORDER BY B)` on very large tables without a corresponding index `(A, B)`.
-   **後果 (Consequence)**：每次查詢都會觸發昂貴的 Sort 操作，導致 CPU 飆高。
-   **Consequence**: Every query triggers an expensive Sort operation, causing CPU spikes.
-   **修正 (Fix)**：建立 POC (Partition, Order, Covering) 索引以支援 Window Function。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請比較 `RANK()`, `DENSE_RANK()`, 與 `ROW_NUMBER()` 的差異？
## Q1: Compare `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`.

-   **高分回答要點 (Key Points)**：
    -   **ROW_NUMBER**: 強制唯一，即使數值相同也會給出 1, 2, 3。常用於分頁或去重。
    -   **RANK**: 數值相同排名相同，但會跳號（例如 1, 1, 3）。
    -   **DENSE_RANK**: 數值相同排名相同，不跳號（例如 1, 1, 2）。常用於「找出前 N 名」且包含並列者的情境。
    -   *加分題*：提到這些函數在 Deterministic (確定性) 上的差異（若 ORDER BY 欄位不唯一，ROW_NUMBER 的結果可能在不同執行次數變動，除非加 Secondary Sort Key）。

## Q2: 在 SQL Server 中處理 JSON 資料，與使用 NoSQL (如 MongoDB) 有何權衡？
## Q2: What are the trade-offs between processing JSON in SQL Server vs. using a NoSQL DB (like MongoDB)?

-   **高分回答要點 (Key Points)**：
    -   **優點 (Pros)**：ACID 交易保證、Join 能力、單一基礎設施維護成本低。適合「大部分結構化，少部分彈性」的資料。
    -   **缺點 (Cons)**：寫入效能通常不如針對 Document 優化的 NoSQL；Schema 變更雖靈活但索引管理（Computed Columns）仍需謹慎。
    -   **結論**：若 JSON 只是 Payload 或輔助屬性，SQL Server 足矣；若資料完全無 Schema 且讀寫量極大，則考慮 NoSQL。

## Q3: 如何設計一個高效率的「最新狀態」查詢系統？（例如：查詢每位使用者的最後一筆訂單）
## Q3: How to design an efficient "Latest Status" query system? (e.g., Query the last order for every user)

-   **高分回答要點 (Key Points)**：
    -   **方法 A**: `ROW_NUMBER() OVER (PARTITION BY UserID ORDER BY OrderDate DESC) = 1`。這是標準解法，但在全表掃描時效能中等。
    -   **方法 B**: `CROSS APPLY`。先選出 Distinct Users，再對每個 User `TOP 1` 查訂單。當 User 數量少但訂單極多時，效能通常優於 Window Function。
    -   **方法 C**: Materialized View (Indexed View) 或另外維護一張 `UserLastOrder` 表（以空間換時間），適合極高頻讀取的場景。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點回顧 (Key Takeaways)
1.  **Window Functions** 是解決跨行計算與分析型查詢的神器，能避免複雜的 Self-Join。
2.  **Recursive CTE** 讓處理階層式資料（樹狀結構）變得標準化且易讀。
3.  **JSON 支援** 賦予了 SQL Server 處理半結構化資料的能力，配合 **Computed Column Index** 可兼顧查詢效能。
4.  **MERGE** 語法強大但有併發陷阱，OLTP 環境中需謹慎使用。
5.  **Bulk Operations** 應盡量減少 Log 寫入並批次處理，而非逐筆操作。

## 下一步 (Next Steps)
掌握了進階查詢模式後，下一步應深入探討如何讓這些查詢跑得更快。建議進入 **Chapter 06: Performance Tuning & Internals**，學習 Execution Plan 分析、Index 深入優化（Clustered vs Non-Clustered, Include Columns）以及鎖定機制（Locking & Blocking）。

After mastering advanced query patterns, the next step is to learn how to make these queries run faster. It is recommended to proceed to **Chapter 06: Performance Tuning & Internals**, covering Execution Plan analysis, deep Index optimization (Clustered vs Non-Clustered, Include Columns), and Locking & Blocking mechanisms.