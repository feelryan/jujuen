# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，資料庫的「並發控制（Concurrency Control）」往往是系統效能與資料正確性之間的決戰點。許多效能問題並非源自 SQL 語法本身，而是來自鎖定（Locking）導致的阻塞（Blocking）或死鎖（Deadlock）。本章旨在協助你從「會寫 Transaction」進階到「能設計高並發交易模型」。

In the career of a Senior Software Engineer, database **Concurrency Control** is often the battleground between system performance and data integrity. Many performance issues stem not from the SQL syntax itself, but from **Blocking** or **Deadlocks** caused by Locking. This chapter aims to help you progress from "writing Transactions" to "designing high-concurrency transaction models."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精準選擇隔離層級**：理解 `READ COMMITTED`、`REPEATABLE READ`、`SERIALIZABLE` 與 `SNAPSHOT` (RCSI) 的底層實作差異與適用場景。
    **Select Isolation Levels precisely**: Understand the underlying implementation differences and use cases for `READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`, and `SNAPSHOT` (RCSI).
2.  **解決死鎖與阻塞**：不只是重啟服務，而是能透過 Extended Events 或 SQL Profiler 分析 Deadlock Graph，並從程式碼邏輯層面根除死鎖。
    **Resolve Deadlocks and Blocking**: Go beyond restarting services; analyze Deadlock Graphs using Extended Events or SQL Profiler and eliminate deadlocks at the code logic level.
3.  **識別 Latch Contention**：區分 Lock（邏輯鎖）與 Latch（記憶體鎖），並理解在高頻交易系統中，Latch Contention 如何成為隱形殺手。
    **Identify Latch Contention**: Distinguish between Locks (logical) and Latches (in-memory), and understand how Latch Contention becomes a silent killer in high-frequency trading systems.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 悲觀鎖 vs. 樂觀鎖 (Pessimistic vs. Optimistic Locking)

MS-SQL 傳統上預設採用**悲觀並發模型（Pessimistic Concurrency Model）**。這就像圖書館只有一本書，當一個人借走（Write Lock）時，其他人連看（Read）都不行，必須排隊等待。

Traditionally, MS-SQL defaults to a **Pessimistic Concurrency Model**. It’s like a library with only one copy of a book; when someone borrows it (Write Lock), no one else can even read it; they must wait in line.

然而，現代雲端應用（如 Azure SQL Database）或其他資料庫（如 PostgreSQL）傾向使用 MVCC（Multi-Version Concurrency Control）。在 MS-SQL 中，這對應到 **RCSI (Read Committed Snapshot Isolation)**。這就像每當有人修改書本時，圖書館會影印一份舊版本的副本給讀者看，讀者永遠不會被寫入者阻塞。

However, modern cloud applications (like Azure SQL Database) or other databases (like PostgreSQL) lean towards MVCC (Multi-Version Concurrency Control). In MS-SQL, this corresponds to **RCSI (Read Committed Snapshot Isolation)**. It’s as if whenever someone modifies the book, the library provides a photocopy of the old version to readers, so readers are never blocked by writers.

## 2.2 鎖定粒度與層級 (Lock Granularity & Hierarchy)

MS-SQL 的鎖定機制是一個階層結構。理解這一點對於優化至關重要：
MS-SQL's locking mechanism is a hierarchical structure. Understanding this is crucial for optimization:

*   **Row (RID/Key)**: 最細粒度，並發度最高，但管理鎖的 CPU/RAM 開銷最大。
    **Row (RID/Key)**: Finest granularity, highest concurrency, but highest CPU/RAM overhead for managing locks.
*   **Page**: 8KB 的資料頁。鎖定一頁會影響該頁面上的所有 Rows。
    **Page**: An 8KB data page. Locking a page affects all Rows on that page.
*   **Table / Object**: 鎖定整張表。開銷最小，但並發度最差。
    **Table / Object**: Locks the entire table. Lowest overhead, but worst concurrency.

**心智模型**：資料庫引擎會自動進行 **Lock Escalation（鎖升級）**。當一個交易持有的 Row Locks 超過閾值（通常是 5000 個），系統為了節省記憶體，會強制將鎖升級為 Table Lock，這往往是系統突然變慢的主因。

**Mental Model**: The database engine automatically performs **Lock Escalation**. When a transaction holds more Row Locks than a threshold (usually 5,000), the system forces an upgrade to a Table Lock to save memory, which is often the main reason for sudden system slowdowns.

## 2.3 隔離層級光譜 (The Isolation Level Spectrum)

由寬鬆到嚴格（並發度由高到低）：
From lenient to strict (Concurrency from high to low):

1.  **Read Uncommitted**: 允許 Dirty Read（讀到未 Commit 的資料）。極快但不安全。
    **Read Uncommitted**: Allows Dirty Reads (reading uncommitted data). Extremely fast but unsafe.
2.  **Read Committed (Default)**: 讀取時會被寫入鎖阻塞。避免 Dirty Read，但可能發生 Non-repeatable Read。
    **Read Committed (Default)**: Reads are blocked by write locks. Avoids Dirty Reads but allows Non-repeatable Reads.
3.  **Repeatable Read**: 交易內多次讀取同一筆資料結果一致。會持續持有 Shared Lock 直到交易結束。
    **Repeatable Read**: Multiple reads of the same data within a transaction yield the same result. Holds Shared Locks until the transaction ends.
4.  **Serializable**: 最嚴格。透過 Range Locks 防止 Phantom Read（幻讀，即交易期間有新資料插入）。
    **Serializable**: Strictest. Uses Range Locks to prevent Phantom Reads (new data inserted during the transaction).
5.  **Snapshot / RCSI**: 使用 TempDB 儲存版本鏈，讀寫不互鎖。
    **Snapshot / RCSI**: Uses TempDB to store version chains; readers and writers do not block each other.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 高並發搶票/庫存系統 (High-Concurrency Ticketing/Inventory System)

在設計秒殺或搶票系統時，資料庫是最大的瓶頸。
When designing flash-sale or ticketing systems, the database is the biggest bottleneck.

*   **問題 (Problem)**: 多個使用者同時購買同一商品（Hot Row）。
    Multiple users buying the same item (Hot Row) simultaneously.
*   **設計決策 (Design Decision)**:
    *   若使用預設的 `READ COMMITTED`，大量的 `SELECT` 查詢會被 `UPDATE` 阻塞，導致連線池（Connection Pool）耗盡。
        If using the default `READ COMMITTED`, massive `SELECT` queries will be blocked by `UPDATE`, causing Connection Pool exhaustion.
    *   **Solution**: 啟用 **RCSI**。讓讀取庫存的操作（Read）不被扣減庫存的操作（Write）阻塞，大幅提升吞吐量（Throughput）。
        **Solution**: Enable **RCSI**. Allow inventory reads to proceed without being blocked by inventory deductions (Writes), significantly boosting throughput.

## 3.2 報表與分析查詢 (Reporting & Analytics Queries)

在 OLTP 系統上執行長時間的報表查詢是危險的。
Running long-running reporting queries on an OLTP system is dangerous.

*   **影響 (Impact)**: 報表查詢可能會在大量資料列上持有 Shared Locks，這會阻止正常的業務寫入（如使用者註冊、訂單建立），導致系統停擺。
    **Impact**: Reporting queries might hold Shared Locks on massive rows, blocking normal business writes (like user registration, order creation) and causing system downtime.
*   **架構解法 (Architecture Solution)**:
    *   **Read Replicas**: 將報表導流至唯讀複本。
        **Read Replicas**: Route reporting traffic to read-only replicas.
    *   **Snapshot Isolation**: 若必須在 Primary 執行，強制報表使用 `SET TRANSACTION ISOLATION LEVEL SNAPSHOT`，確保它讀取的是交易開始當下的快照，完全不申請鎖。
        **Snapshot Isolation**: If running on Primary is mandatory, force the report to use `SET TRANSACTION ISOLATION LEVEL SNAPSHOT`, ensuring it reads a snapshot from the start of the transaction without acquiring locks.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：轉帳死鎖與解決方案 (Scenario: Transfer Deadlock & Solution)

### 背景 (Context)
我們有兩個帳戶 A 和 B。交易 1 要從 A 轉到 B，交易 2 同時要從 B 轉到 A。
We have two accounts, A and B. Transaction 1 wants to transfer from A to B, while Transaction 2 wants to transfer from B to A simultaneously.

### Naive Approach (The Deadlock Trap)

```sql
-- Transaction 1
BEGIN TRAN;
    UPDATE Accounts SET Balance = Balance - 100 WHERE Id = 1; -- Locks Row A
    WAITFOR DELAY '00:00:05'; -- Simulating processing time
    UPDATE Accounts SET Balance = Balance + 100 WHERE Id = 2; -- Tries to Lock Row B (Blocked by T2)
COMMIT TRAN;

-- Transaction 2
BEGIN TRAN;
    UPDATE Accounts SET Balance = Balance - 100 WHERE Id = 2; -- Locks Row B
    WAITFOR DELAY '00:00:05';
    UPDATE Accounts SET Balance = Balance + 100 WHERE Id = 1; -- Tries to Lock Row A (Blocked by T1)
COMMIT TRAN;
```

**結果**：SQL Server 的 Deadlock Monitor 會偵測到循環等待（Circular Wait），並隨機犧牲其中一個交易（Kill Process），拋出 Error 1205。
**Result**: SQL Server's Deadlock Monitor detects the Circular Wait and randomly sacrifices one transaction (Kill Process), throwing Error 1205.

### 成熟的解決方案 (Mature Solutions)

#### 方法一：固定存取順序 (Canonical Ordering)
在應用層或 Stored Procedure 中，強制總是按照 ID 從小到大（或從大到小）的順序鎖定資源。
In the application layer or Stored Procedure, enforce locking resources in a consistent order (e.g., by ID ascending).

```csharp
// Pseudo-code logic
var firstId = Math.Min(fromId, toId);
var secondId = Math.Max(fromId, toId);

// Always lock firstId then secondId
Lock(firstId);
Lock(secondId);
```

#### 方法二：轉換鎖定意圖 (Update Locks / UPDLOCK)
如果邏輯是「先讀後寫」，常見死鎖原因是兩個交易都先取得了 Shared Lock (S)，然後同時試圖升級為 Exclusive Lock (X)。
If the logic is "Read then Write", a common deadlock cause is two transactions both acquiring a Shared Lock (S) and then simultaneously trying to upgrade to an Exclusive Lock (X).

```sql
-- Bad Pattern: Read then Write
BEGIN TRAN
  SELECT Balance FROM Accounts WHERE Id = 1; -- Holds S Lock
  -- ... logic ...
  UPDATE Accounts ... -- Needs X Lock. If another transaction also holds S, deadlock occurs.
COMMIT

-- Good Pattern: Use UPDLOCK
BEGIN TRAN
  -- Acquires U Lock immediately. U locks are compatible with S, but NOT with other U locks.
  -- This serializes the intent to update.
  SELECT Balance FROM Accounts WITH (UPDLOCK) WHERE Id = 1; 
  UPDATE Accounts ...
COMMIT
```

**為何有效？** `UPDLOCK` 宣告了「我稍後要修改這筆資料」。同一時間只有一個交易能對同一資源持有 `UPDLOCK`，從而避免了轉換死鎖（Conversion Deadlock）。
**Why it works?** `UPDLOCK` declares "I intend to modify this data later." Only one transaction can hold a `UPDLOCK` on a resource at a time, preventing Conversion Deadlocks.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `NOLOCK` (Abusing `NOLOCK`)

*   **錯誤描述**: 為了追求效能，在所有 SELECT 語句後加上 `WITH (NOLOCK)`。
    **Description**: Adding `WITH (NOLOCK)` to all SELECT statements in pursuit of performance.
*   **為何不好**:
    *   **Dirty Reads**: 你會讀到未提交的資料（例如轉帳轉了一半的金額）。
        **Dirty Reads**: You will read uncommitted data (e.g., a partial transfer amount).
    *   **Index Corruption Scans**: 在極端情況下（Page Split 時），`NOLOCK` 可能導致查詢漏讀資料或重複讀取同一行兩次，甚至因掃描到正在移動的 Page 而報錯。
        **Index Corruption Scans**: In extreme cases (during Page Splits), `NOLOCK` can cause queries to miss rows or read the same row twice, or even fail due to scanning a moving Page.
*   **替代方案**: 使用 **RCSI** (Read Committed Snapshot Isolation)。它提供無阻塞讀取，且保證讀到的是 Committed Data。
    **Alternative**: Use **RCSI**. It provides non-blocking reads while guaranteeing Committed Data.

## 5.2 忽略 Latch Contention (Ignoring Latch Contention)

*   **錯誤描述**: 系統 CPU 飆高，但 Disk I/O 很低，且沒有明顯的 Blocking 鏈。工程師以為是 Query 太慢，不斷加 Index。
    **Description**: System CPU spikes, but Disk I/O is low, and there are no obvious Blocking chains. Engineers assume queries are slow and keep adding indexes.
*   **根本原因**: 這是 **Latch Contention**（記憶體頁面的輕量級鎖競爭）。常見於：
    *   **Last Page Insert Contention**: 多個執行緒同時 Insert 到由 `IDENTITY` 或 `Sequence` 當 PK 的表，導致都在爭搶最後一個 Data Page 的 Latch。
    *   **TempDB Contention**: 大量建立/銷毀暫存表。
*   **解決方案**:
    *   對於 Insert 熱點：使用 Hash Partitioning 或改用 GUID (雖有 fragmentation 代價) 分散寫入點。
    *   對於 TempDB：增加 TempDB 的資料檔數量（通常建議等於 CPU Core 數）。

## 5.3 交易範圍過大 (Scope of Transaction too large)

*   **錯誤描述**: 在 `BEGIN TRAN` 和 `COMMIT` 之間包含了非 DB 操作（如 API Call、寄信、複雜計算）。
    **Description**: Including non-DB operations (API calls, emails, complex calculations) between `BEGIN TRAN` and `COMMIT`.
*   **為何不好**: 鎖定資源的時間被不必要地拉長，大幅增加 Deadlock 機率與 Blocking 時間。
    **Why it's bad**: Lock holding time is unnecessarily extended, drastically increasing Deadlock probability and Blocking duration.
*   **修正**: 盡可能縮短交易範圍，只包含必要的 DB 操作。
    **Fix**: Minimize transaction scope to include only essential DB operations.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請解釋 RCSI (Read Committed Snapshot) 與 Snapshot Isolation 的區別？
**Explain the difference between RCSI and Snapshot Isolation?**

*   **高分回答要點**:
    *   兩者都使用 TempDB 的版本鏈來避免讀寫阻塞。
    *   **RCSI (Statement Level)**: 每個 `SELECT` 語句讀取的是「該語句開始時」的最新 Commit 版本。適合大多數現有應用遷移，不需要改 Code。
    *   **Snapshot (Transaction Level)**: 整個交易讀取的是「交易開始時」的資料快照。如果在交易期間資料被別人改了，Commit 時會拋出 Update Conflict 錯誤。
    *   **Key Point**: RCSI 犧牲了一點一致性（同一個交易內兩次 Select 可能不同）換取較少的衝突；Snapshot 提供最高一致性但需要處理衝突重試邏輯。

## Q2: 如何排查 Production 環境的 Deadlock？
**How do you troubleshoot Deadlocks in Production?**

*   **高分回答要點**:
    *   **被動監控**: 不能只看 Error Log。要啟用 **Extended Events (XEvents)** 中的 `xml_deadlock_report`。
    *   **分析 Graph**: 讀取 XML Deadlock Graph，找出 Victim 和 Winner。
    *   **關鍵資訊**: 識別是哪個 Resource（Key lock, Page lock）以及哪兩段 SQL。
    *   **解決策略**: 檢查 Access Order 是否一致？是否缺少 Index 導致 Table Scan（鎖定範圍過大）？是否需要 `UPDLOCK`？

## Q3: 什麼是 Phantom Read？哪種 Isolation Level 可以防止它？
**What is a Phantom Read? Which Isolation Level prevents it?**

*   **高分回答要點**:
    *   **定義**: 在同一個交易內，兩次執行相同的範圍查詢（Range Query），第二次發現多出了「幽靈」般的資料（別人新 Insert 的）。
    *   **防止**: `SERIALIZABLE` 層級。
    *   **機制**: 透過 **Key-Range Locks**，不僅鎖住現有資料，還鎖住索引鍵之間的「間隙（Gap）」，防止其他交易插入新資料到該範圍內。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **鎖定是雙面刃**：保護資料一致性的同時，是效能與擴展性的最大殺手。
    **Locking is a double-edged sword**: While protecting data consistency, it is the biggest killer of performance and scalability.
2.  **預設不一定最好**：傳統的 `READ COMMITTED` 會導致讀寫互斥。現代系統應優先考慮啟用 **RCSI**。
    **Defaults aren't always best**: Traditional `READ COMMITTED` causes read/write blocking. Modern systems should prioritize enabling **RCSI**.
3.  **粒度決定並發**：Row Lock 並發高但開銷大；Table Lock 開銷小但並發低。小心 Lock Escalation。
    **Granularity determines concurrency**: Row Locks have high concurrency but high overhead; Table Locks have low overhead but low concurrency. Beware of Lock Escalation.
4.  **死鎖是邏輯問題**：死鎖通常源自存取順序不一致或鎖轉換（S -> X）。使用 `UPDLOCK` 或固定順序來解決。
    **Deadlocks are logic problems**: They usually stem from inconsistent access order or lock conversion (S -> X). Use `UPDLOCK` or canonical ordering to fix.
5.  **Latch vs Lock**：Lock 保護交易邏輯，Latch 保護記憶體結構。高 CPU 低 I/O 往往是 Latch Contention。
    **Latch vs Lock**: Locks protect transaction logic; Latches protect memory structures. High CPU with low I/O often indicates Latch Contention.

## 下一步 (Next Steps)
*   **延伸閱讀**: 深入研究 **Extended Events**，學習如何捕捉長時間執行的鎖定與 Deadlock Graph。
    **Further Reading**: Dive deep into **Extended Events** to learn how to capture long-running locks and Deadlock Graphs.
*   **實作練習**: 在開發環境模擬 Deadlock，並嘗試使用 `SET DEADLOCK_PRIORITY` 與 `UPDLOCK` 解決它。
    **Hands-on**: Simulate a Deadlock in a dev environment and try to resolve it using `SET DEADLOCK_PRIORITY` and `UPDLOCK`.
*   **下一章預告**: 既然鎖定與索引（Index）息息相關（鎖是加在索引鍵上的），下一章我們將探討 **Advanced Indexing Strategies (Covering, Filtered & Columnstore)**。
    **Next Chapter**: Since locking is intrinsically linked to Indexing (locks are placed on index keys), the next chapter will explore **Advanced Indexing Strategies (Covering, Filtered & Columnstore)**.