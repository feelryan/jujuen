# MS-SQL 核心架構與儲存引擎
# Architecture & Storage Engine Internals

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，將 SQL Server 視為黑盒子（Black Box）是效能調優與系統設計的瓶頸。本章將揭開 SQL Server 儲存引擎的內部運作機制，從資料如何在磁碟上物理儲存，到它們如何在記憶體中被處理。
For senior engineers, treating SQL Server as a black box is a bottleneck for performance tuning and system design. This chapter unveils the internal mechanisms of the SQL Server storage engine, from how data is physically stored on disk to how it is processed in memory.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準解釋 I/O 行為**：理解為何 8KB Page 是 I/O 的最小單位，以及這對索引設計與硬體選擇的影響。
    **Explain I/O behavior precisely:** Understand why the 8KB Page is the atomic unit of I/O and its impact on index design and hardware selection.
2.  **掌握 ACID 的底層實作**：透過 WAL (Write-Ahead Logging) 與 Checkpoint 機制，解釋 SQL Server 如何保證 Durability（持久性）與 Performance（效能）的平衡。
    **Master the low-level implementation of ACID:** Explain how SQL Server balances Durability and Performance via WAL (Write-Ahead Logging) and Checkpoint mechanisms.
3.  **區分 Logical vs. Physical Reads**：在閱讀執行計畫與效能計數器時，能透過 Buffer Pool 的運作原理來診斷記憶體壓力。
    **Distinguish Logical vs. Physical Reads:** Diagnose memory pressure by understanding Buffer Pool mechanics when reading execution plans and performance counters.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

要深入 MS-SQL，必須建立正確的「資料階層」與「資料流動」心智模型。
To dive deep into MS-SQL, one must establish a correct mental model of "Data Hierarchy" and "Data Flow."

### 2.1 儲存階層：Page 與 Extent
### 2.1 Storage Hierarchy: Page and Extent

在 MS-SQL 中，資料庫檔案（`.mdf` / `.ndf`）並不是連續的位元組流，而是由 **Pages** 組成的集合。
In MS-SQL, database files (`.mdf` / `.ndf`) are not continuous streams of bytes but collections of **Pages**.

*   **Page (8 KB)**:
    *   **定義**：I/O 的最小原子單位。即使你只讀取 1 個 Row，SQL Server 也會將整個 8KB Page 載入記憶體。
    *   **Definition**: The atomic unit of I/O. Even if you read only 1 Row, SQL Server loads the entire 8KB Page into memory.
    *   **結構**：包含 96 bytes 的 Header、資料列（Data Rows）以及頁尾的 Row Offset Array（用於快速定位 Row）。
    *   **Structure**: Contains a 96-byte Header, Data Rows, and a Row Offset Array at the end (for fast row localization).

*   **Extent (64 KB)**:
    *   **定義**：空間管理的單位。由 8 個連續的 Pages 組成。
    *   **Definition**: The unit of space management. Composed of 8 contiguous Pages.
    *   **類型**：
        *   *Mixed Extent*：由不同物件（Tables/Indexes）共享（通常用於小資料表）。
        *   *Uniform Extent*：由單一物件獨佔。
    *   **Types**:
        *   *Mixed Extent*: Shared by different objects (usually for small tables).
        *   *Uniform Extent*: Owned exclusively by a single object.

> **類比 (Analogy)**：
> 想像圖書館（Disk）。
> *   **Row**: 書中的一句話。
> *   **Page**: 書的一頁（你不能只撕下一句話，必須翻開整頁）。
> *   **Extent**: 書架上的一格（管理書籍存放的最小區塊）。
>
> **Analogy**:
> Imagine a library (Disk).
> *   **Row**: A sentence in a book.
> *   **Page**: A page in the book (you can't tear out just a sentence; you must open the whole page).
> *   **Extent**: A shelf section (the smallest block for managing book storage).

### 2.2 記憶體緩衝：Buffer Pool
### 2.2 Memory Buffering: Buffer Pool

SQL Server 幾乎不在磁碟上直接操作資料。所有讀寫都發生在記憶體中的 **Buffer Pool**。
SQL Server rarely manipulates data directly on disk. All reads and writes happen in the in-memory **Buffer Pool**.

*   **Clean Page**: 記憶體中的 Page 與磁碟上的內容一致。
    **Clean Page**: The Page in memory is identical to the content on disk.
*   **Dirty Page**: 記憶體中的 Page 已被修改，但尚未寫回磁碟資料檔（`.mdf`）。
    **Dirty Page**: The Page in memory has been modified but not yet written back to the disk data file (`.mdf`).

### 2.3 交易日誌與 WAL (Write-Ahead Logging)
### 2.3 Transaction Log & WAL (Write-Ahead Logging)

這是保證 ACID 中 **Durability** 的關鍵。
This is the key to guaranteeing **Durability** in ACID.

*   **規則**：在任何資料變更（Dirty Page）被寫入磁碟資料檔之前，描述該變更的日誌記錄（Log Record）必須先被寫入磁碟的交易日誌檔（`.ldf`）。
*   **Rule**: Before any data change (Dirty Page) is written to the disk data file, the log record describing that change must be written to the disk transaction log file (`.ldf`).
*   **目的**：如果系統崩潰，SQL Server 重啟時可以重播（Redo）日誌來恢復已提交的交易，或復原（Undo）未提交的交易。
*   **Purpose**: If the system crashes, SQL Server can replay (Redo) the log to recover committed transactions or rollback (Undo) uncommitted ones upon restart.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

理解上述架構對於設計高吞吐量系統至關重要。
Understanding the above architecture is crucial for designing high-throughput systems.

### 3.1 I/O 子系統的隔離設計
### 3.1 I/O Subsystem Isolation Design

在 Production 環境設計儲存架構時，我們通常將 Data Files (`.mdf`) 與 Log Files (`.ldf`) 放在不同的實體磁碟上。
When designing storage architecture in Production, we typically place Data Files (`.mdf`) and Log Files (`.ldf`) on different physical disks.

*   **Log File Pattern**: 主要是 **Sequential Write**（順序寫入）。寫入速度直接影響 Transaction Latency。
    *   *Requirement*: 需要極低延遲的寫入能力（Low Latency Write）。
*   **Data File Pattern**: 主要是 **Random Read/Write**（隨機讀寫）。Checkpoints 和查詢會導致隨機 I/O。
    *   *Requirement*: 需要高 IOPS（如 NVMe SSD）。

*   **Log File Pattern**: Primarily **Sequential Write**. Write speed directly impacts Transaction Latency.
    *   *Requirement*: Needs extremely low latency write capability.
*   **Data File Pattern**: Primarily **Random Read/Write**. Checkpoints and queries cause random I/O.
    *   *Requirement*: Needs high IOPS (e.g., NVMe SSD).

### 3.2 記憶體壓力指標：Page Life Expectancy (PLE)
### 3.2 Memory Pressure Metric: Page Life Expectancy (PLE)

當系統變慢時，資深工程師會檢查 PLE。
When the system slows down, senior engineers check PLE.

*   **意義**：一個 Page 在被移出 Buffer Pool 之前，平均能在記憶體中存活多久（秒）。
*   **Meaning**: How long (in seconds) a Page survives in memory on average before being evicted from the Buffer Pool.
*   **設計影響**：如果 PLE 過低（例如 < 300秒），代表 Buffer Pool 發生劇烈的 **Page Thrashing**（頁面抖動），系統正忙於頻繁地進行磁碟 I/O。這通常意味著需要更多 RAM 或優化查詢以減少 Logical Reads。
*   **Design Impact**: If PLE is too low (e.g., < 300 seconds), it indicates severe **Page Thrashing** in the Buffer Pool, and the system is busy with frequent disk I/O. This usually implies a need for more RAM or query optimization to reduce Logical Reads.

---

## 4. 逐步示例：一個 UPDATE 的生命週期
## 4. Walkthrough: The Lifecycle of an UPDATE

讓我們跟蹤一個簡單的 `UPDATE Users SET Age = 30 WHERE ID = 1` 查詢，看看資料如何在各個組件間流動。
Let's trace a simple `UPDATE Users SET Age = 30 WHERE ID = 1` query to see how data flows between components.

### 步驟 1：讀取 Page 到 Buffer Pool (Logical vs Physical Read)
### Step 1: Read Page into Buffer Pool (Logical vs Physical Read)

SQL Server 首先在 Buffer Pool 中尋找包含 `ID = 1` 的 Page。
SQL Server first looks for the Page containing `ID = 1` in the Buffer Pool.

*   **Scenario A (Cache Hit)**: Page 已在記憶體中。這是一個 **Logical Read**。速度極快。
*   **Scenario B (Cache Miss)**: Page 不在記憶體中。SQL Server 發出 **Physical Read**，將 8KB Page 從磁碟複製到 Buffer Pool。
*   **Scenario A (Cache Hit)**: The Page is already in memory. This is a **Logical Read**. Extremely fast.
*   **Scenario B (Cache Miss)**: The Page is not in memory. SQL Server issues a **Physical Read**, copying the 8KB Page from disk to the Buffer Pool.

### 步驟 2：修改與日誌寫入 (WAL)
### Step 2: Modification & Log Write (WAL)

1.  SQL Server 在 Buffer Pool 中修改該 Page。現在這個 Page 變成了 **Dirty Page**。
    SQL Server modifies the Page in the Buffer Pool. This Page is now a **Dirty Page**.
2.  **關鍵步驟**：在交易 Commit 之前，SQL Server 生成一條 Log Record（描述從 Age=29 變為 30），並將其同步寫入磁碟上的 Transaction Log (`.ldf`)。
    **Critical Step**: Before the transaction commits, SQL Server generates a Log Record (describing the change from Age=29 to 30) and synchronously writes it to the Transaction Log on disk (`.ldf`).
3.  一旦 Log 寫入成功，SQL Server 向客戶端回傳 "Success"。
    Once the Log write is successful, SQL Server returns "Success" to the client.

*注意：此時，磁碟上的 Data File (`.mdf`) 中的資料仍然是舊的（Age=29）！*
*Note: At this point, the data in the Data File (`.mdf`) on disk is still old (Age=29)!*

### 步驟 3：Checkpoint (非同步寫入)
### Step 3: Checkpoint (Asynchronous Write)

這是一個背景程序（Background Process），通常每分鐘觸發一次，或在記憶體壓力大時觸發。
This is a background process, typically triggered every minute or under memory pressure.

1.  Checkpoint 掃描 Buffer Pool 中的 Dirty Pages。
    Checkpoint scans for Dirty Pages in the Buffer Pool.
2.  將這些 Dirty Pages 寫入磁碟上的 Data File (`.mdf`)。
    Writes these Dirty Pages to the Data File (`.mdf`) on disk.
3.  標記 Transaction Log 中的相關部分為可截斷（如果是在 Simple Recovery Model 下）。
    Marks the relevant part of the Transaction Log as truncatable (if in Simple Recovery Model).

### 程式碼驗證 (Code Verification)

身為資深工程師，我們可以使用未公開指令 `DBCC PAGE` 來查看 Page 的內部狀態（僅供學習與除錯，勿在 Production 濫用）。
As senior engineers, we can use the undocumented command `DBCC PAGE` to inspect the internal state of a Page (for learning and debugging only, do not abuse in Production).

```sql
-- 1. Find the Page ID for a specific row
-- 1. 找出特定資料列所在的 Page ID
SELECT sys.fn_PhysLocFormatter(%%physloc%%) AS [File:Page:Slot], *
FROM Users
WHERE ID = 1;
-- Output Example: (1:145:2) -> FileID 1, PageID 145, Slot 2

-- 2. Enable trace flag to see DBCC output in console
-- 2. 啟用追蹤旗標以在控制台查看 DBCC 輸出
DBCC TRACEON(3604);

-- 3. Inspect the page header and content
-- 3. 檢查頁面標頭與內容
-- Syntax: DBCC PAGE (DatabaseName, FileID, PageID, OutputStyle)
DBCC PAGE ('MyDatabase', 1, 145, 3);
```

在輸出中，你會看到 `m_lsn` (Log Sequence Number)。每次 Page 被修改，這個 LSN 都會更新，連結到對應的 Transaction Log。
In the output, you will see `m_lsn` (Log Sequence Number). Every time the Page is modified, this LSN updates, linking to the corresponding Transaction Log.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 誤解 "Committed" 的物理意義
### 5.1 Misunderstanding the Physical Meaning of "Committed"

*   **錯誤觀念**：認為 `COMMIT` 成功後，資料就已經寫入 `.mdf` 檔案了。
    **Misconception**: Thinking that after a successful `COMMIT`, data is already written to the `.mdf` file.
*   **後果**：在進行災難復原規劃或硬體斷電測試時，低估了 Transaction Log 的重要性。若 Log 損壞且 Data File 尚未 Checkpoint，資料將永久遺失。
    **Consequence**: Underestimating the importance of the Transaction Log during disaster recovery planning or power-loss testing. If the Log is corrupted and the Data File hasn't been Checkpointed, data is permanently lost.

### 5.2 忽視 Page Splits（頁面分割）
### 5.2 Ignoring Page Splits

*   **情境**：在 Clustered Index 中插入非順序鍵值（如 GUID），或更新變長欄位（VARCHAR）導致 Row 變大。
    **Scenario**: Inserting non-sequential keys (like GUIDs) into a Clustered Index, or updating variable-length columns (VARCHAR) causing the Row to grow.
*   **問題**：當一個 Page 滿了（8KB），SQL Server 必須分配新 Page 並移動一半資料。這會導致：
    1.  大量的 Log 生成（記錄資料移動）。
    2.  Logical Fragmentation（邏輯碎片），導致讀取效能下降。
    **Issue**: When a Page is full (8KB), SQL Server must allocate a new Page and move half the data. This causes:
    1.  Massive Log generation (logging the data movement).
    2.  Logical Fragmentation, degrading read performance.
*   **最佳實踐**：使用 `FILLFACTOR` 預留 Page 空間，或避免使用隨機 GUID 作為 Clustered Key。
    **Best Practice**: Use `FILLFACTOR` to reserve Page space, or avoid using random GUIDs as Clustered Keys.

### 5.3 儲存快照備份的陷阱
### 5.3 The Pitfall of Storage Snapshot Backups

*   **錯誤**：依賴 VM 層級或 SAN 層級的快照，但沒有使用支援 VSS (Volume Shadow Copy Service) 的工具。
    **Mistake**: Relying on VM-level or SAN-level snapshots without using VSS (Volume Shadow Copy Service) aware tools.
*   **後果**：由於 Memory 中的 Dirty Pages 尚未寫入 Disk，且 Log 與 Data 寫入時間點不一致，直接快照可能導致資料庫處於「Torn Page」或毀損狀態，無法掛載。
    **Consequence**: Since Dirty Pages in Memory are not yet written to Disk, and Log/Data write timings are inconsistent, a direct snapshot can result in a "Torn Page" or corrupted database state that cannot be mounted.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 為什麼 SQL Server 需要 Transaction Log？為什麼不直接寫入 Data File？
### Q1: Why does SQL Server need a Transaction Log? Why not write directly to the Data File?

*   **高分回答要點**：
    *   **Performance**: Log 是 Sequential Write（快），Data File 寫入通常是 Random Write（慢）。WAL 機制讓 `COMMIT` 只需等待 Log 寫入，大幅降低 Latency。
    *   **Atomicity & Durability**: Log 允許在 Crash Recovery 時進行 Redo（重做已提交但在記憶體中遺失的變更）與 Undo（回滾未提交的變更）。
*   **Key Points for High Score**:
    *   **Performance**: Log is Sequential Write (fast), while Data File writes are often Random Write (slow). The WAL mechanism ensures `COMMIT` only waits for the Log write, significantly reducing Latency.
    *   **Atomicity & Durability**: The Log allows Redo (replaying committed changes lost in memory) and Undo (rolling back uncommitted changes) during Crash Recovery.

### Q2: 什麼是 Checkpoint？如果我將 Checkpoint 間隔設得非常長，會有什麼影響？
### Q2: What is a Checkpoint? What happens if I set the Checkpoint interval to be very long?

*   **高分回答要點**：
    *   Checkpoint 是將 Dirty Pages 寫入 Data File 的過程。
    *   **優點**：減少運行時的 Disk I/O 寫入頻率（因為多次更新同一 Page 只需寫入一次）。
    *   **缺點**：增加 **Recovery Time (RTO)**。因為 Crash 後需要 Redo 的 Log 量變大，資料庫重啟變慢。同時可能導致 Buffer Pool 累積過多 Dirty Pages，最終引發 I/O Storm。
*   **Key Points for High Score**:
    *   Checkpoint is the process of flushing Dirty Pages to the Data File.
    *   **Pros**: Reduces runtime Disk I/O write frequency (multiple updates to the same Page only require one write).
    *   **Cons**: Increases **Recovery Time (RTO)**. Since the amount of Log to Redo after a crash increases, database restart becomes slower. It may also cause Dirty Pages to accumulate in the Buffer Pool, eventually triggering an I/O Storm.

### Q3: 解釋 Logical Reads 與 Physical Reads 的差異，以及如何利用它們優化查詢。
### Q3: Explain the difference between Logical Reads and Physical Reads, and how to use them for query optimization.

*   **高分回答要點**：
    *   Logical Read 是從 Buffer Pool 讀取 Page；Physical Read 是從 Disk 讀取。
    *   **優化目標**：主要應減少 **Logical Reads**。因為減少了 Logical Reads，自然就減少了 Buffer Pool 的壓力與 CPU 消耗，進而降低 Physical Reads 的機率。
    *   如果 Logical Reads 很低但 Physical Reads 很高，說明記憶體不足（Server Memory Pressure）。
*   **Key Points for High Score**:
    *   Logical Read is reading a Page from the Buffer Pool; Physical Read is reading from Disk.
    *   **Optimization Goal**: Primarily focus on reducing **Logical Reads**. Reducing Logical Reads naturally reduces Buffer Pool pressure and CPU consumption, thereby lowering the probability of Physical Reads.
    *   If Logical Reads are low but Physical Reads are high, it indicates insufficient memory (Server Memory Pressure).

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 重點回顧 (Key Takeaways)
1.  **8KB Page** 是 SQL Server 的核心貨幣。所有 I/O、記憶體管理皆以此為單位。
2.  **WAL (Write-Ahead Logging)** 確保了資料不遺失 (Durability) 並優化了寫入效能 (Sequential I/O)。
3.  **Buffer Pool** 是效能關鍵。查詢優化本質上是在減少讀取 Buffer Pool Pages 的次數 (Logical Reads)。
4.  **Checkpoint** 非同步地將 Dirty Pages 寫入磁碟，平衡了 I/O 負載與復原時間 (RTO)。
5.  **Log File** 與 **Data File** 具有截然不同的 I/O 特性，應在硬體層級進行隔離。

### 下一步 (Next Steps)
理解了資料如何儲存在 Page 中之後，下一章我們將探討 **Index Structure & B-Tree Internals**（索引結構與 B-Tree 內部機制）。我們將學習 SQL Server 如何將這些 8KB Pages 組織成 B-Tree，以實現 $O(\log N)$ 的快速查找，以及 Clustered Index 與 Non-Clustered Index 在物理結構上的具體差異。

After understanding how data is stored in Pages, in the next chapter, we will explore **Index Structure & B-Tree Internals**. We will learn how SQL Server organizes these 8KB Pages into B-Trees to achieve $O(\log N)$ fast lookups, and the specific physical structural differences between Clustered and Non-Clustered Indexes.