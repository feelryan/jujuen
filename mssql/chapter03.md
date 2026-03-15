# 1. 前言與學習目標 (Introduction & Learning Objectives)

In the realm of high-scale systems, the database often becomes the primary bottleneck. For a Senior Software Engineer, writing SQL that returns the correct result is merely the baseline; the real value lies in writing queries that remain performant under heavy load and large datasets. This chapter moves beyond syntax to the internal mechanics of the SQL Server Query Optimizer.

在大型系統的領域中，資料庫往往是主要的效能瓶頸。對於資深軟體工程師而言，寫出能回傳正確結果的 SQL 僅是基本功；真正的價值在於寫出在高度負載與海量資料下，仍能保持高效能的查詢。本章將超越語法層面，深入探討 SQL Server 查詢優化器（Query Optimizer）的內部運作機制。

By the end of this chapter, you will be able to:
1.  **Interpret Execution Plans:** Identify critical operators (Seek vs. Scan, Key Lookups, Sorts) and understand their cost implications.
2.  **Master SARGability:** Write "Search ARGument ABLE" queries that effectively utilize indexes, avoiding common pitfalls like functions on columns.
3.  **Diagnose Parameter Sniffing:** Recognize when plan caching backfires and apply appropriate remediation strategies.
4.  **Understand Statistics:** Explain how SQL Server uses histograms to estimate row counts (Cardinality Estimation) and how stale statistics lead to poor plans.

完成本章後，你將能夠：
1.  **解讀執行計畫（Execution Plans）：** 識別關鍵運算子（Seek vs. Scan、Key Lookups、Sorts）並理解其成本意涵。
2.  **掌握 SARGability：** 撰寫具備「可搜尋參數能力（Search ARGument ABLE）」的查詢，有效利用索引，避免諸如對欄位使用函數等常見陷阱。
3.  **診斷參數嗅探（Parameter Sniffing）：** 識別執行計畫快取（Plan Caching）何時會產生反效果，並應用適當的修復策略。
4.  **理解統計資訊（Statistics）：** 解釋 SQL Server 如何利用直方圖（Histograms）來估算資料列數（Cardinality Estimation），以及過期的統計資訊如何導致糟糕的執行計畫。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 The Optimizer as a Cost-Based Engine (優化器作為基於成本的引擎)

Think of the SQL Server Query Optimizer not as a rule-based parser, but as a sophisticated mathematician working under a time limit. It doesn't necessarily find the *best* possible plan; it finds the *good enough* plan with the lowest estimated cost found within a reasonable time. This cost is calculated based on CPU, I/O, and memory usage derived from **Statistics**.

請將 SQL Server 查詢優化器想像成一位在時間限制下工作的精算師，而非單純的規則解析器。它不一定會找出「最完美」的計畫，而是會在合理時間內，找出一個預估成本最低且「足夠好」的計畫。這個成本是根據 **統計資訊（Statistics）** 推導出的 CPU、I/O 與記憶體使用量來計算的。

## 2.2 Scan vs. Seek (掃描與搜尋)

*   **Index Seek:** Analogy: Using the index at the back of a book to find a specific page. It traverses the B-Tree structure directly to the data. This is O(log N) complexity and is generally preferred for high-selectivity queries.
*   **Index Scan / Table Scan:** Analogy: Reading every page of the book to find a word. It reads all leaf-level pages of the index or the heap. This is O(N) complexity.

*   **Index Seek（索引搜尋）：** 類比：使用書後的索引直接翻到特定頁面。它會沿著 B-Tree 結構直接定位資料。這屬於 O(log N) 複雜度，通常是高選擇性（high-selectivity）查詢的首選。
*   **Index Scan / Table Scan（索引掃描 / 資料表掃描）：** 類比：為了找一個詞而閱讀整本書的每一頁。它會讀取索引或堆積（Heap）的所有葉節點頁面。這屬於 O(N) 複雜度。

## 2.3 SARGable (SARGability)

SARGable stands for **S**earch **ARG**ument **ABLE**. A query predicate is SARGable if the engine can use an index seek to retrieve data. If you manipulate the column side of the expression (e.g., `WHERE YEAR(CreateDate) = 2023`), the engine cannot traverse the B-Tree index and must scan every row to compute the function result.

SARGable 代表 **S**earch **ARG**ument **ABLE**（可搜尋參數能力）。如果引擎可以使用索引搜尋（Index Seek）來檢索資料，則該查詢謂詞（predicate）就是 SARGable 的。如果你對表達式的欄位端進行操作（例如：`WHERE YEAR(CreateDate) = 2023`），引擎就無法遍歷 B-Tree 索引，而必須掃描每一列來計算函數結果。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 The "It Works on My Machine" Syndrome (「在我電腦上沒問題」症候群)

In a production environment, data volume and distribution (Data Skew) differ significantly from development environments. A query that takes 10ms on a dev database with 10,000 rows might take 30 seconds on a production database with 100 million rows. This usually happens because the dev environment often masks non-SARGable queries or poor indexing strategies due to the small dataset fitting entirely in memory.

在正式環境（Production）中，資料量與分佈（Data Skew）與開發環境有顯著差異。一個在只有 1 萬筆資料的開發庫上耗時 10ms 的查詢，在擁有 1 億筆資料的正式庫上可能需要 30 秒。這通常是因為開發環境的小型資料集能完全放入記憶體，從而掩蓋了非 SARGable 查詢或糟糕的索引策略。

## 3.2 CPU Spikes and Parameter Sniffing (CPU 飆升與參數嗅探)

A classic system design issue in MS-SQL is **Parameter Sniffing**. SQL Server compiles a plan based on the first parameter value passed.
*   **Scenario:** You have a status column where 99% of rows are 'Complete' and 1% are 'Pending'.
*   **First Run:** A user queries for 'Pending'. The optimizer chooses an Index Seek (efficient). This plan is cached.
*   **Second Run:** A user queries for 'Complete'. The optimizer reuses the cached 'Index Seek' plan. However, seeking 99% of the table row-by-row (Key Lookup) is disastrously slower than just scanning the table. The server CPU spikes to 100%.

MS-SQL 中一個經典的系統設計問題是 **參數嗅探（Parameter Sniffing）**。SQL Server 會根據第一次傳入的參數值來編譯執行計畫。
*   **情境：** 你有一個狀態欄位，其中 99% 的資料是 'Complete'，1% 是 'Pending'。
*   **第一次執行：** 使用者查詢 'Pending'。優化器選擇 Index Seek（高效）。此計畫被快取。
*   **第二次執行：** 使用者查詢 'Complete'。優化器重複使用快取的 'Index Seek' 計畫。然而，逐列搜尋（Key Lookup）資料表中 99% 的資料，比直接掃描整張表慢得多。伺服器 CPU 瞬間飆升至 100%。

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 Optimizing for SARGability (優化 SARGability)

**Scenario:** We need to find all orders placed in the year 2023. There is an index on `OrderDate`.

**情境：** 我們需要找出 2023 年下的所有訂單。`OrderDate` 欄位上有索引。

### The Naive Approach (Non-SARGable) / 樸素做法（非 SARGable）

```sql
-- Anti-pattern: Function on the column
SELECT OrderID, CustomerID, OrderDate
FROM Sales.Orders
WHERE YEAR(OrderDate) = 2023;
```

**Analysis:**
The execution plan will show an **Index Scan** (or Clustered Index Scan). The engine has to calculate `YEAR(OrderDate)` for every single row in the table to check if it equals 2023. The index order is useless here because the transformed value isn't stored in the B-Tree.

**分析：**
執行計畫會顯示 **Index Scan**（或 Clustered Index Scan）。引擎必須針對資料表中的每一列計算 `YEAR(OrderDate)`，以檢查其是否等於 2023。索引的排序在這裡毫無用處，因為轉換後的數值並未儲存在 B-Tree 中。

### The Optimized Approach (SARGable) / 優化做法（SARGable）

```sql
-- Best Practice: Range query on the raw column
SELECT OrderID, CustomerID, OrderDate
FROM Sales.Orders
WHERE OrderDate >= '2023-01-01'
  AND OrderDate < '2024-01-01';
```

**Analysis:**
The execution plan changes to an **Index Seek**. The optimizer knows the range of 2023 and can jump directly to the first record of 2023 and stop reading at the first record of 2024. This reduces I/O from scanning millions of pages to reading just the relevant few.

**分析：**
執行計畫變為 **Index Seek**。優化器知道 2023 的範圍，因此可以直接跳轉到 2023 的第一筆記錄，並在讀到 2024 的第一筆記錄時停止。這將 I/O 從掃描數百萬頁減少到僅讀取相關的少數幾頁。

## 4.2 Handling Parameter Sniffing (處理參數嗅探)

**Scenario:** A stored procedure `GetOrdersByStatus` is causing intermittent timeouts.

**情境：** 一個預存程序 `GetOrdersByStatus` 導致間歇性的逾時（Timeouts）。

```sql
CREATE PROCEDURE GetOrdersByStatus (@StatusID INT)
AS
BEGIN
    SELECT * FROM Orders WHERE StatusID = @StatusID;
END
```

**Problem:**
If the plan is compiled for a rare status (Seek), it hurts the common status (Scan preferred). If compiled for a common status (Scan), it hurts the rare status (Seek preferred).

**問題：**
如果計畫是針對稀有狀態編譯的（Seek），它會拖累常見狀態的查詢（Scan 較佳）。如果針對常見狀態編譯（Scan），它會拖累稀有狀態的查詢（Seek 較佳）。

**Solution A: OPTION (RECOMPILE)**
Forces a new plan for every execution. Good if the query is not run thousands of times per second (compilation CPU cost).

**解法 A：OPTION (RECOMPILE)**
強制每次執行都產生新計畫。如果該查詢每秒執行次數不高（考量編譯的 CPU 成本），這是不錯的選擇。

```sql
SELECT * FROM Orders WHERE StatusID = @StatusID
OPTION (RECOMPILE);
```

**Solution B: Optimize for Unknown**
Uses the average distribution statistics instead of the specific parameter value.

**解法 B：Optimize for Unknown**
使用平均分佈統計資訊，而非特定的參數值。

```sql
SELECT * FROM Orders WHERE StatusID = @StatusID
OPTION (OPTIMIZE FOR UNKNOWN);
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Implicit Conversion (隱式轉換)

**Pitfall:** Comparing different data types, forcing SQL Server to convert one side.
**Example:** `VARCHAR` column compared to `NVARCHAR` parameter.

**錯誤：** 比較不同的資料型別，迫使 SQL Server 轉換其中一邊。
**範例：** `VARCHAR` 欄位與 `NVARCHAR` 參數進行比較。

```sql
-- Assuming PhoneNumber is VARCHAR(20)
-- @PhoneParam is NVARCHAR(20) (default in many ORMs like .NET)
SELECT * FROM Customers WHERE PhoneNumber = @PhoneParam;
```

**Why it's bad:** SQL Server has to convert the `PhoneNumber` column to `NVARCHAR` (higher precedence) for every row. This breaks SARGability (Scan instead of Seek) and consumes CPU.
**Fix:** Ensure parameter types match column types exactly in your application code or cast the parameter, not the column.

**為何不好：** SQL Server 必須將每一列的 `PhoneNumber` 欄位轉換為 `NVARCHAR`（優先權較高）。這會破壞 SARGability（導致 Scan 而非 Seek）並消耗 CPU。
**修正：** 確保應用程式碼中的參數型別與欄位型別完全一致，或者轉換參數而非欄位。

## 5.2 Ignoring Key Lookups (RID Lookup) (忽略鍵值查找)

**Pitfall:** `SELECT *` combined with a non-clustered index that doesn't cover all columns.

**錯誤：** `SELECT *` 配合一個未包含所有欄位的非叢集索引（Non-clustered Index）。

**Why it's bad:** The engine seeks the index to find the row, but then has to jump back to the Clustered Index (the actual table) to get the remaining columns (Key Lookup). If you retrieve many rows, this random I/O is slower than a full table scan.
**Fix:** Use **Covering Indexes** (INCLUDE clause) or select only necessary columns.

**為何不好：** 引擎透過索引搜尋找到該列，但隨後必須跳回叢集索引（實際的資料表）去抓取剩餘的欄位（Key Lookup）。如果你檢索許多列，這種隨機 I/O 比全表掃描還慢。
**修正：** 使用 **覆蓋索引（Covering Indexes，INCLUDE 子句）**，或只選取必要的欄位。

## 5.3 Leading Wildcards (前導萬用字元)

**Pitfall:** `LIKE '%term%'`

**錯誤：** `LIKE '%term%'`

**Why it's bad:** Just like you can't find a word in a dictionary if you only know it *ends* with "ing", SQL Server cannot use the index B-Tree order. It must scan.
**Fix:** Remove the leading wildcard if possible (`'term%'`) or use Full-Text Search / Elasticsearch for complex text search requirements.

**為何不好：** 就像如果你只知道一個字是以 "ing" *結尾*，你無法在字典中快速找到它一樣，SQL Server 無法利用索引的 B-Tree 排序。它必須進行掃描。
**修正：** 盡可能移除前導萬用字元（`'term%'`），或針對複雜文字搜尋需求改用全文檢索（Full-Text Search）/ Elasticsearch。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 Debugging Slow Queries
**Question:** "A query that has been running fast for months suddenly times out today. No code changes were deployed. How do you troubleshoot?"

**提問：** 「一個跑了好幾個月都很快的查詢，今天突然逾時了。沒有部署任何程式碼變更。你會如何排查？」

**Key Points to Cover:**
*   **Parameter Sniffing:** Did the plan cache get evicted and recompiled with an atypical parameter?
*   **Statistics:** Are the stats stale? Did a large data load happen recently?
*   **Blocking:** Is there a lock chain blocking this query?
*   **Resource Contention:** Is the server under heavy load (IO/CPU) from another process?

**高分回答要點：**
*   **參數嗅探：** 執行計畫快取是否被清除，並用非典型的參數重新編譯了？
*   **統計資訊：** 統計資訊是否過期？最近是否發生了大量資料寫入？
*   **阻塞（Blocking）：** 是否有鎖鏈（Lock chain）阻塞了這個查詢？
*   **資源競爭：** 伺服器是否正承受來自其他程序的重度負載（IO/CPU）？

## 6.2 Index Seek vs. Scan
**Question:** "Is an Index Seek always better than an Index Scan? Why or why not?"

**提問：** 「Index Seek 永遠比 Index Scan 好嗎？為什麼？」

**Key Points to Cover:**
*   **Tipping Point:** No. If you are retrieving a large percentage of the table (e.g., > 30%), a Scan (sequential I/O) is often faster than a Seek + Key Lookup (random I/O).
*   **Selectivity:** Seeks are best for high selectivity (few rows). Scans are acceptable for aggregations over the whole table.

**高分回答要點：**
*   **臨界點（Tipping Point）：** 不。如果你要檢索資料表很大比例的資料（例如 > 30%），Scan（循序 I/O）通常比 Seek + Key Lookup（隨機 I/O）更快。
*   **選擇性（Selectivity）：** Seek 最適合高選擇性（回傳少數列）的情況。Scan 對於全表聚合運算來說是可以接受的。

## 6.3 ORM & Dynamic SQL
**Question:** "How do ORMs (like Entity Framework or Hibernate) typically cause performance issues related to execution plans?"

**提問：** 「ORM（如 Entity Framework 或 Hibernate）通常如何導致與執行計畫相關的效能問題？」

**Key Points to Cover:**
*   **N+1 Problem:** Executing one query per row instead of a JOIN.
*   **Implicit Conversion:** Sending Unicode parameters (`NVARCHAR`) for non-Unicode columns.
*   **Over-fetching:** `SELECT *` behavior leading to unnecessary Key Lookups.

**高分回答要點：**
*   **N+1 問題：** 每一列執行一次查詢，而不是使用 JOIN。
*   **隱式轉換：** 針對非 Unicode 欄位傳送 Unicode 參數（`NVARCHAR`）。
*   **過度抓取（Over-fetching）：** `SELECT *` 的行為導致不必要的 Key Lookups。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## Summary (小結)
1.  **Execution Plan is the Map:** Always verify, don't guess. Look for Scans where you expect Seeks.
2.  **SARGability is King:** Avoid functions on columns (`WHERE FUNC(col) = val`). Keep columns clean.
3.  **Data Types Matter:** Implicit conversion prevents index usage. Match your parameter types.
4.  **Parameter Sniffing:** Be aware that "one plan fits all" fails when data distribution is skewed. Use `OPTION (RECOMPILE)` judiciously.
5.  **Statistics:** The optimizer relies on them. Outdated stats = Bad plans.

1.  **執行計畫是地圖：** 永遠要驗證，不要猜測。在預期看到 Seek 的地方尋找是否有 Scan。
2.  **SARGability 至上：** 避免對欄位使用函數（`WHERE FUNC(col) = val`）。保持欄位原始狀態。
3.  **資料型別很重要：** 隱式轉換會阻礙索引使用。請匹配你的參數型別。
4.  **參數嗅探：** 要意識到當資料分佈不均時，「一個計畫適用所有情況」會失效。明智地使用 `OPTION (RECOMPILE)`。
5.  **統計資訊：** 優化器依賴它們。過期的統計資訊 = 糟糕的計畫。

## Next Steps (後續延伸)
*   **Deep Dive into Indexes:** Learn about Clustered vs. Non-Clustered, Include Columns, and Filtered Indexes.
*   **Concurrency:** Move to **Chapter 04: Locking, Blocking, and Isolation Levels** to understand how your optimized queries interact with other transactions.
*   **Tools:** Practice using `SET STATISTICS IO ON` and Query Store to monitor performance over time.

*   **深入索引：** 學習叢集與非叢集索引、包含欄位（Include Columns）與篩選索引（Filtered Indexes）。
*   **並發性（Concurrency）：** 進入 **Chapter 04: 鎖定、阻塞與隔離層級**，了解你優化後的查詢如何與其他交易互動。
*   **工具：** 練習使用 `SET STATISTICS IO ON` 與 Query Store 來監控長期的效能表現。