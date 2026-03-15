# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資料量達到 TB 級別的企業級應用中，單純依賴索引（Indexing）往往已不足以維持系統效能與可維護性。當單一資料表（Table）過大時，備份、索引重組（Index Rebuild）與歷史資料清理（Purging）都會成為運維惡夢。本章將探討 MS-SQL 在大規模資料場景下的核心解法：分區（Partitioning）與檔案群組（Filegroups）管理。

In enterprise applications where data volume reaches the TB scale, relying solely on indexing is often insufficient to maintain system performance and maintainability. When a single table becomes too large, backups, index rebuilds, and historical data purging become operational nightmares. This chapter explores MS-SQL's core solutions for large-scale data scenarios: Partitioning and Filegroups management.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **設計與實作 Table Partitioning**：理解 Partition Function 與 Partition Scheme，並實作「滑動視窗（Sliding Window）」策略來管理時序資料。
    **Design and implement Table Partitioning:** Understand Partition Functions and Partition Schemes, and implement the "Sliding Window" strategy for time-series data.
2.  **優化實體儲存配置（Filegroups）**：利用 Filegroups 將冷熱資料分離（Cold/Hot Data Separation），優化 I/O 效能與備份策略。
    **Optimize physical storage configuration (Filegroups):** Use Filegroups to separate cold and hot data, optimizing I/O performance and backup strategies.
3.  **執行高效資料封存（Archiving）**：使用 `SWITCH PARTITION` 達到 O(1) 時間複雜度的資料封存與刪除，避免大規模 `DELETE` 造成的鎖定（Locking）與交易紀錄（Transaction Log）膨脹。
    **Execute efficient data archiving:** Use `SWITCH PARTITION` to achieve O(1) time complexity for data archiving and deletion, avoiding locking and transaction log bloat caused by massive `DELETE` operations.
4.  **區分 Partitioning 與 Sharding**：清楚解釋垂直擴充（Scale-up）架構下的分區與水平擴充（Scale-out）架構下的分片（Sharding）之差異與適用場景。
    **Distinguish between Partitioning and Sharding:** Clearly explain the differences and use cases between Partitioning in a Scale-up architecture and Sharding in a Scale-out architecture.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

對於資深工程師而言，理解 MS-SQL 的儲存階層是掌握分區策略的關鍵。

For senior engineers, understanding the storage hierarchy of MS-SQL is key to mastering partitioning strategies.

### 2.1 類比：圖書館管理 (Analogy: Library Management)

-   **Heap/Clustered Index (Table)**：這是一本書的內容。如果書太厚（TB 級），翻閱和維護都很困難。
    **Heap/Clustered Index (Table):** This is the content of a book. If the book is too thick (TB scale), reading and maintaining it is difficult.
-   **Filegroups (Physical Storage)**：這是圖書館的「樓層」或「書架區域」。你可以把熱門新書放在一樓門口（快速 SSD），把十年前的舊報紙放在地下室（便宜 HDD）。
    **Filegroups (Physical Storage):** These are the "floors" or "shelf areas" of the library. You can place popular new books at the entrance of the first floor (fast SSD) and ten-year-old newspapers in the basement (cheap HDD).
-   **Partitioning (Logical Separation)**：這是將一本書拆分成多冊（Volume 1, Volume 2...）。雖然邏輯上它還是一部百科全書，但你可以單獨搬運其中一冊。
    **Partitioning (Logical Separation):** This is splitting a book into multiple volumes (Volume 1, Volume 2...). Although logically it is still one encyclopedia, you can move a single volume independently.

### 2.2 核心組件定義 (Key Components Definition)

1.  **Partition Function**：定義「切分規則」。例如：依據 `TransactionDate`，每年切一刀。
    **Partition Function:** Defines the "splitting rules". For example: split by `TransactionDate` every year.
2.  **Partition Scheme**：定義「映射地圖」。將切分後的每一塊（Partition）映射到具體的儲存空間（Filegroup）。
    **Partition Scheme:** Defines the "mapping map". Maps each split chunk (Partition) to a specific storage space (Filegroup).
3.  **Aligned Index**：當索引的分區方式與主表（Base Table）完全一致時，稱為「對齊」。這對於高效的 `SWITCH` 操作至關重要。
    **Aligned Index:** When the index is partitioned exactly the same way as the Base Table, it is called "aligned". This is crucial for efficient `SWITCH` operations.

### 2.3 Partitioning vs. Sharding

| Feature | Partitioning (MS-SQL Native) | Sharding (Application/Architecture Level) |
| :--- | :--- | :--- |
| **Scope** | 單一實例（Single Instance）內 | 跨多個實例（Multiple Instances） |
| **Data Distribution** | 邏輯分割，共享 CPU/Memory | 物理分割，Shared-Nothing 架構 |
| **Complexity** | DB 層級處理，對 App 透明 | App 層級需實作 Routing Logic |
| **Goal** | 提升管理性（Manageability）與單機效能 | 無限水平擴充（Horizontal Scalability） |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design 面試或架構設計中，MS-SQL Partitioning 通常出現在「資料保留策略（Data Retention）」與「歷史資料查詢優化」的環節。

In System Design interviews or architectural design, MS-SQL Partitioning usually appears in the context of "Data Retention Strategy" and "Historical Data Query Optimization".

### 3.1 典型場景：高頻交易日誌 (Typical Scenario: High-Frequency Transaction Logs)

假設你正在設計一個金融稽核系統，每天產生 50GB 的 Log，需保留 7 年。單一 Table 將成長至 120TB 以上。
Suppose you are designing a financial audit system that generates 50GB of logs daily and needs to be retained for 7 years. A single table will grow to over 120TB.

**設計挑戰 (Design Challenges):**
-   **Delete 效能**：每天執行 `DELETE FROM Logs WHERE Date < 7_years_ago` 會導致巨大的 Transaction Log 寫入，甚至鎖死整張表。
    **Delete Performance:** Running `DELETE FROM Logs WHERE Date < 7_years_ago` daily causes massive Transaction Log writes and can even lock the entire table.
-   **維護視窗**：對 100TB 的表做 Index Rebuild 幾乎是不可能的任務。
    **Maintenance Window:** Performing an Index Rebuild on a 100TB table is practically impossible.

**解決方案架構 (Solution Architecture):**
1.  **Filegroup Tiering**：
    -   `FG_Hot` (SSD): 存放最近 3 個月的資料。
    -   `FG_Warm` (Standard HDD): 存放 3 個月至 1 年的資料。
    -   `FG_Cold` (Cheap Storage/Archive): 存放 1 年以上的資料。
2.  **Partition Elimination**：查詢 `WHERE Date = 'Today'` 時，Query Optimizer 只會掃描 `FG_Hot` 對應的分區，忽略其他 99% 的資料。
3.  **Partition Switching**：刪除舊資料時，不是用 `DELETE`，而是將最舊的 Partition `SWITCH` 到一個空表，然後 `DROP TABLE`。這是 Metadata 操作，瞬間完成。

---

# 4. 逐步示例：滑動視窗策略 (Walkthrough: Sliding Window Strategy)

我們將實作一個基於時間的滑動視窗（Sliding Window），自動管理月度資料。

We will implement a time-based Sliding Window to automatically manage monthly data.

### Step 1: 建立 Filegroups 與 Files (Create Filegroups & Files)

首先，我們需要物理儲存容器。
First, we need physical storage containers.

```sql
-- Add Filegroups
ALTER DATABASE MyDB ADD FILEGROUP FG_2023_Jan;
ALTER DATABASE MyDB ADD FILEGROUP FG_2023_Feb;
-- (In production, you map these to specific .ndf files on disk)
ALTER DATABASE MyDB ADD FILE (NAME = N'F_2023_Jan', FILENAME = N'E:\Data\F_2023_Jan.ndf') TO FILEGROUP FG_2023_Jan;
-- ... repeat for other months
```

### Step 2: 定義 Partition Function (Define Partition Function)

定義邊界值。這裡使用 `RANGE RIGHT`，表示邊界值屬於右側（下一個分區）。
Define boundary values. Here we use `RANGE RIGHT`, meaning the boundary value belongs to the right side (the next partition).

```sql
-- Partition by Month
CREATE PARTITION FUNCTION pf_MonthlyRange (DATETIME)
AS RANGE RIGHT FOR VALUES (
    '2023-01-01', 
    '2023-02-01', 
    '2023-03-01'
);
```

*Mental Check:* `2023-01-01` falls into the 2nd partition (Jan data), anything before is in the 1st (empty/legacy).

### Step 3: 定義 Partition Scheme (Define Partition Scheme)

將 Function 的邏輯分區映射到物理 Filegroups。
Map the logical partitions of the Function to physical Filegroups.

```sql
CREATE PARTITION SCHEME ps_MonthlyScheme
AS PARTITION pf_MonthlyRange
TO (
    [PRIMARY],     -- Partition 1 (Before 2023-01-01)
    [FG_2023_Jan], -- Partition 2 (Jan Data)
    [FG_2023_Feb], -- Partition 3 (Feb Data)
    [FG_2023_Mar]  -- Partition 4 (Mar Data and beyond, until next split)
);
```

### Step 4: 建立分區表 (Create Partitioned Table)

**關鍵點**：Clustered Index 必須包含 Partition Key (`LogDate`)。
**Critical Point:** The Clustered Index *must* include the Partition Key (`LogDate`).

```sql
CREATE TABLE AuditLogs (
    LogID INT IDENTITY(1,1),
    LogDate DATETIME NOT NULL,
    Message NVARCHAR(MAX),
    -- Constraint: Partition Key must be part of PK/Clustered Index
    CONSTRAINT PK_AuditLogs PRIMARY KEY CLUSTERED (LogDate, LogID)
) ON ps_MonthlyScheme(LogDate);
```

### Step 5: 秒級封存資料 (Archive Data in Seconds)

當 2023年1月的資料過期，我們想將其移出。
When data from Jan 2023 expires, we want to move it out.

1.  建立一個結構完全相同（包含 Index, Constraints），但在一般 Filegroup 上的空表（Staging Table）。
    Create an empty Staging Table with identical structure (including Index, Constraints) but on a regular Filegroup.
2.  執行 Switch。
    Execute Switch.

```sql
-- 1. Create Staging Table (Must be on the same Filegroup as the partition being switched)
CREATE TABLE AuditLogs_Staging (
    LogID INT IDENTITY(1,1),
    LogDate DATETIME NOT NULL,
    Message NVARCHAR(MAX),
    CONSTRAINT PK_AuditLogs_Staging PRIMARY KEY CLUSTERED (LogDate, LogID)
) ON [FG_2023_Jan]; -- Crucial: Must match the source partition's filegroup

-- 2. Switch Partition 2 (Jan Data) to Staging
ALTER TABLE AuditLogs SWITCH PARTITION 2 TO AuditLogs_Staging;

-- 3. Now AuditLogs Partition 2 is empty. AuditLogs_Staging has the data.
-- You can now DROP AuditLogs_Staging or back it up leisurely.
DROP TABLE AuditLogs_Staging;
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 索引未對齊 (Non-Aligned Indexes)
-   **錯誤 (Mistake)**：在分區表上建立了沒有包含 Partition Key 的 Unique Index 或 Non-Clustered Index，且沒有指定 `ON PartitionScheme`。
    **Mistake:** Creating a Unique Index or Non-Clustered Index on a partitioned table without including the Partition Key, and not specifying `ON PartitionScheme`.
-   **後果 (Consequence)**：MS-SQL 會建立 Global Index。當你嘗試 `SWITCH PARTITION` 時會失敗，因為這需要重建整個 Global Index，導致操作變慢且阻塞。
    **Consequence:** MS-SQL creates a Global Index. When you try to `SWITCH PARTITION`, it fails or becomes slow/blocking because the entire Global Index needs to be updated.
-   **修正 (Fix)**：確保所有 Index 都是 Partition Aligned（包含 Partition Key 並建立在相同的 Scheme 上）。
    **Fix:** Ensure all indexes are Partition Aligned (include the Partition Key and created on the same Scheme).

### 5.2 選擇錯誤的 Partition Key (Wrong Partition Key)
-   **錯誤 (Mistake)**：依據 `Date` 分區，但查詢幾乎都是 `WHERE UserID = 123`。
    **Mistake:** Partitioning by `Date`, but queries are almost always `WHERE UserID = 123`.
-   **後果 (Consequence)**：查詢無法進行 Partition Elimination，必須掃描所有分區（Scatter-Gather），效能比不分區還差（因為有 CPU overhead）。
    **Consequence:** Queries cannot perform Partition Elimination and must scan all partitions (Scatter-Gather), resulting in worse performance than non-partitioned tables (due to CPU overhead).

### 5.3 過度分區 (Over-Partitioning)
-   **錯誤 (Mistake)**：為了極致細分，每天甚至每小時建立一個 Partition，導致單表有數千個 Partitions。
    **Mistake:** Creating a partition every day or even every hour for extreme granularity, resulting in thousands of partitions for a single table.
-   **後果 (Consequence)**：Query Optimizer 在編譯執行計畫時需要評估太多 Metadata，導致 Compile Time 暴增；且跨多個分區的查詢效能會下降。建議分區數控制在數百以內。
    **Consequence:** The Query Optimizer needs to evaluate too much metadata during plan compilation, causing Compile Time to skyrocket; queries spanning multiple partitions will degrade. It is recommended to keep partitions within the hundreds.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在既有的 5TB 單一 Table 上導入 Partitioning，你會如何規劃遷移？
**How would you plan the migration to introduce Partitioning on an existing 5TB single table?**

*   **高分回答要點 (Key Points):**
    *   **Downtime 考量**：直接 `CREATE CLUSTERED INDEX ... ON Scheme` 會鎖表並重寫所有資料，需評估維護視窗。
    *   **線上遷移技巧**：若是 Enterprise Edition，可使用 `ONLINE = ON`（但在切換最終 metadata 時仍有短暫 lock）。
    *   **替代方案**：建立新的 Partitioned Table，雙寫（Dual Write）或使用 CDC/Replication 同步資料，最後切換應用程式指向（Rename Table）。
    *   **Storage 準備**：確保 Disk I/O 足夠支撐大規模資料搬移。

### Q2: 為什麼 Primary Key 必須包含 Partition Key？這對業務邏輯有什麼限制？
**Why must the Primary Key include the Partition Key? What constraints does this impose on business logic?**

*   **高分回答要點 (Key Points):**
    *   **技術原因**：Partitioning 是物理儲存層面的分割。若 PK 不含 Partition Key，DB 無法保證全域唯一性（Global Uniqueness），除非建立昂貴的 Global Index（這會破壞 Partitioning 的維護優勢）。
    *   **業務限制**：原本單純的 `ID` 主鍵可能變成複合主鍵 `(ID, Date)`。這意味著應用程式在 `UPDATE` 或 `GET` 單筆資料時，最好也能提供 `Date`，否則 DB 仍需掃描所有分區來找那個 ID。

### Q3: Partitioning 能提升查詢效能嗎？
**Does Partitioning improve query performance?**

*   **高分回答要點 (Key Points):**
    *   **不一定 (It depends)**。Partitioning 的主要目的是 **管理性 (Manageability)**（備份、刪除、載入）。
    *   **提升的情況**：查詢條件包含 Partition Key，觸發 **Partition Elimination**，大幅減少 I/O。
    *   **下降的情況**：查詢不含 Partition Key，需掃描所有分區；或 Join 操作變得更複雜（跨分區 Join）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **管理優於效能**：Partitioning 首要解決的是 TB 級資料的維護問題（備份、刪除），其次才是特定查詢的 I/O 優化。
    **Management over Performance:** Partitioning primarily solves maintenance issues for TB-scale data (backup, delete), and secondarily optimizes I/O for specific queries.
2.  **Filegroups 是基礎**：透過 Filegroups 將 I/O 負載隔離或分層（Tiering），是實體設計的關鍵。
    **Filegroups are fundamental:** Isolating or tiering I/O load via Filegroups is key to physical design.
3.  **Switch 是 O(1)**：利用 `SWITCH PARTITION` 進行資料封存與載入，是處理大數據最優雅的方式。
    **Switch is O(1):** Using `SWITCH PARTITION` for data archiving and loading is the most elegant way to handle big data.
4.  **對齊索引 (Alignment)**：所有的 Index 最好都與 Table 使用相同的 Partition Scheme，避免 Global Index 帶來的維護地獄。
    **Aligned Indexes:** All indexes should ideally use the same Partition Scheme as the Table to avoid the maintenance hell of Global Indexes.
5.  **PK 限制**：分區表的 Unique Constraint / PK 必須包含 Partition Column。
    **PK Constraint:** The Unique Constraint / PK of a partitioned table must include the Partition Column.

### 後續延伸 (Next Steps)
-   **Columnstore Indexes**：對於資料倉儲（Data Warehouse）場景，結合 Partitioning 與 Columnstore Index 可以達到極致的壓縮率與聚合查詢效能。
    **Columnstore Indexes:** For Data Warehouse scenarios, combining Partitioning with Columnstore Index can achieve extreme compression rates and aggregation query performance.
-   **Next Chapter**: 進入 **Chapter 07: Query Optimization & Execution Plans**，深入探討如何閱讀執行計畫，確認 Partition Elimination 是否如預期發生。
    **Next Chapter:** Proceed to **Chapter 07: Query Optimization & Execution Plans** to dive deep into reading execution plans and verifying if Partition Elimination is occurring as expected.