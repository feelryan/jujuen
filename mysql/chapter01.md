# MySQL 架構與儲存引擎核心
# Architecture and Storage Engine Internals

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，將 MySQL 視為一個「黑盒子」已不足以應對高併發與高可靠性的系統需求。本章旨在解構 MySQL 的內部運作機制，特別是 InnoDB 儲存引擎的核心設計。
For senior engineers, treating MySQL as a "black box" is no longer sufficient for handling high-concurrency and high-reliability system requirements. This chapter aims to deconstruct the internal mechanisms of MySQL, with a specific focus on the core design of the InnoDB storage engine.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分 Server Layer 與 Storage Engine Layer**：理解 SQL 解析、優化與資料檢索的職責邊界。
    **Distinguish between Server Layer and Storage Engine Layer**: Understand the boundaries of responsibility for SQL parsing, optimization, and data retrieval.
2.  **掌握 InnoDB 的記憶體架構**：深入理解 Buffer Pool 如何管理 Page，以及它對效能的決定性影響。
    **Master InnoDB's Memory Architecture**: Deeply understand how the Buffer Pool manages pages and its decisive impact on performance.
3.  **解釋 ACID 的底層實作**：透過 Redo Log、Undo Log 與 WAL (Write-Ahead Logging) 機制，解釋交易如何保證原子性與持久性。
    **Explain the low-level implementation of ACID**: Explain how transactions guarantee Atomicity and Durability through Redo Log, Undo Log, and the WAL (Write-Ahead Logging) mechanism.
4.  **理解 Crash Recovery 流程**：描述 Doublewrite Buffer 與 Redo Log 如何防止資料損毀與部分寫入 (Partial Page Write)。
    **Understand the Crash Recovery Process**: Describe how the Doublewrite Buffer and Redo Log prevent data corruption and partial page writes.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 邏輯架構：Server Layer vs. Storage Engine
### 2.1 Logical Architecture: Server Layer vs. Storage Engine

MySQL 最顯著的特徵是其「可插拔式儲存引擎架構」(Pluggable Storage Engine Architecture)。我們可以將其類比為「餐廳的前台與廚房」。
The most distinctive feature of MySQL is its "Pluggable Storage Engine Architecture." We can analogize this to "the Front of House vs. the Kitchen in a restaurant."

*   **Server Layer (前台/Front of House)**:
    *   負責與客戶溝通 (Connection Handling)、理解訂單 (Parser)、決定最佳出餐順序 (Optimizer) 以及快取管理 (Query Cache, deprecated in 8.0)。
    *   **關鍵點**：所有跨引擎的功能（如 Stored Procedures, Triggers, Views, Binlog）都在這一層。
    *   Handles communication with clients (Connection Handling), understands orders (Parser), decides the best sequence for serving (Optimizer), and manages caching (Query Cache, deprecated in 8.0).
    *   **Key Point**: All cross-engine features (e.g., Stored Procedures, Triggers, Views, Binlog) reside in this layer.

*   **Storage Engine Layer (廚房/Kitchen)**:
    *   負責實際的資料存取。Server Layer 透過 API 指揮引擎「給我下一行資料」，而引擎負責與磁碟或記憶體互動。
    *   **關鍵點**：InnoDB 是目前的預設與主流，負責交易處理、鎖定與崩潰恢復。
    *   Responsible for actual data access. The Server Layer instructs the engine via API to "fetch the next row," and the engine handles interactions with disk or memory.
    *   **Key Point**: InnoDB is the current default and standard, handling transaction processing, locking, and crash recovery.

### 2.2 InnoDB 記憶體結構：Buffer Pool
### 2.2 InnoDB Memory Structure: Buffer Pool

不要將 Buffer Pool 僅僅視為一個 Cache。在 InnoDB 的心智模型中，**Buffer Pool 是資料的主要操作區，磁碟 (Disk) 只是備份**。
Do not view the Buffer Pool merely as a cache. In the InnoDB mental model, **the Buffer Pool is the primary workspace for data, and the disk is just the backup.**

*   **Page**: InnoDB 與磁碟互動的最小單位（預設 16KB）。
*   **Dirty Page**: 記憶體中已被修改但尚未寫入磁碟的 Page。
*   **Page**: The smallest unit of interaction between InnoDB and the disk (default 16KB).
*   **Dirty Page**: A page in memory that has been modified but not yet written to the disk.

### 2.3 日誌系統：WAL (Write-Ahead Logging)
### 2.3 The Log Ecosystem: WAL (Write-Ahead Logging)

為了效能，我們修改資料時只修改記憶體 (Buffer Pool) 並寫入 Log，而不是每次都寫入 Data File。
For performance, when modifying data, we only modify the memory (Buffer Pool) and write to the Log, rather than writing to the Data File every time.

1.  **Redo Log (InnoDB 特有)**:
    *   **物理日誌 (Physical Log)**：記錄「在某個 Page 上做了什麼修改」。
    *   **循環寫入**：固定大小，用完即覆蓋（Checkpoints）。
    *   **目的**：Crash-safe。即使資料庫崩潰，重啟後也能依據 Redo Log 恢復未寫入磁碟的資料。
    *   **Physical Log**: Records "what modification was made on a specific Page."
    *   **Circular Write**: Fixed size, overwrites when full (Checkpoints).
    *   **Purpose**: Crash-safe. Even if the DB crashes, it can recover data not yet written to disk based on the Redo Log upon restart.

2.  **Undo Log (InnoDB 特有)**:
    *   **邏輯日誌 (Logical Log)**：記錄如何「撤銷」修改（例如：INSERT 的反向是 DELETE）。
    *   **目的**：交易 Rollback 與 MVCC (Multi-Version Concurrency Control)。
    *   **Logical Log**: Records how to "undo" a modification (e.g., the reverse of INSERT is DELETE).
    *   **Purpose**: Transaction Rollback and MVCC.

3.  **Binlog (Server Layer)**:
    *   **邏輯日誌 (Logical Log)**：記錄 SQL 語句或資料列的變更。
    *   **追加寫入**：不會覆蓋，保留歷史全貌。
    *   **目的**：主從複製 (Replication) 與時間點恢復 (Point-in-Time Recovery)。
    *   **Logical Log**: Records SQL statements or row changes.
    *   **Append-only**: Does not overwrite; preserves full history.
    *   **Purpose**: Replication and Point-in-Time Recovery (PITR).

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 寫入密集型系統的 I/O 優化
### 3.1 I/O Optimization in Write-Intensive Systems

在設計高吞吐量的寫入系統（如訂單系統、Log 收集）時，理解 **WAL** 至關重要。
When designing high-throughput write systems (e.g., order systems, log collection), understanding **WAL** is crucial.

*   **隨機 I/O vs. 順序 I/O (Random vs. Sequential I/O)**:
    *   直接修改 `.ibd` 檔案通常涉及隨機 I/O（磁頭跳轉），速度慢。
    *   寫入 Redo Log 是順序 I/O，速度極快。
    *   **設計啟示**：這就是為什麼 MySQL 能夠支援高併發寫入。確保你的儲存設備對順序寫入有良好支援。
    *   Directly modifying `.ibd` files usually involves random I/O (disk head seeking), which is slow.
    *   Writing to the Redo Log is sequential I/O, which is extremely fast.
    *   **Design Insight**: This is why MySQL can support high-concurrency writes. Ensure your storage infrastructure supports sequential writes well.

### 3.2 兩階段提交 (Two-Phase Commit, 2PC)
### 3.2 Two-Phase Commit (2PC)

在分散式系統設計中，我們常討論 2PC。MySQL 內部為了保證 **Binlog** (用於 Replica) 與 **Redo Log** (用於 Crash Recovery) 的一致性，也實作了內部的 2PC。
In distributed system design, we often discuss 2PC. Internally, MySQL implements an internal 2PC to ensure consistency between the **Binlog** (used for Replicas) and the **Redo Log** (used for Crash Recovery).

*   **如果不一致的後果**：
    *   若 Redo Log 寫入但 Binlog 失敗：主庫有資料，從庫 (Replica) 遺失資料。
    *   若 Binlog 寫入但 Redo Log 失敗：主庫崩潰恢復後資料消失，但從庫卻多出了這筆資料。
*   **Consequences of Inconsistency**:
    *   If Redo Log is written but Binlog fails: Primary has data, Replica misses data.
    *   If Binlog is written but Redo Log fails: Primary loses data after crash recovery, but Replica has extra data.

---

## 4. 逐步示例：一條 Update 語句的生命週期
## 4. Walkthrough: The Lifecycle of an Update Statement

讓我們追蹤一條 SQL 語句的執行流程，看看上述組件如何協作。
Let's trace the execution flow of a SQL statement to see how the above components collaborate.

**Scenario**:
```sql
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
```

### Step 1: Server Layer 處理 (Processing)
1.  **Connection**: 應用程式建立連線。
2.  **Parser/Analyzer**: 驗證語法，確認 `accounts` 表存在。
3.  **Optimizer**: 決定使用 `id` 主鍵索引進行查詢。
4.  **Executor**: 呼叫 InnoDB 引擎介面取資料。

### Step 2: Storage Engine (InnoDB) 讀取 (Reading)
1.  InnoDB 檢查 Buffer Pool 是否有 `id=1` 的 Page。
2.  若無，從磁碟載入該 Page 到 Buffer Pool。
3.  InnoDB 對該行加鎖 (Row Lock)。

### Step 3: 寫入與日誌 (Writing & Logging)
1.  **Undo Log**: 寫入舊值 (balance 原始值)，以便 Rollback。
2.  **Memory Update**: 在 Buffer Pool 中更新該 Page (此時 Page 變為 Dirty)。
3.  **Redo Log (Prepare)**: 將修改寫入 Redo Log，並標記狀態為 `prepare`。

### Step 4: 提交 (Commit - Internal 2PC)
1.  **Binlog Write**: Server Layer 將 SQL 邏輯寫入 Binlog，並呼叫 `fsync` 持久化。
2.  **Redo Log (Commit)**: InnoDB 將 Redo Log 狀態改為 `commit`。
3.  **Return**: 交易完成，返回成功給客戶端。
4.  **IO Thread**: 後續由後台執行緒擇機將 Dirty Page 刷入磁碟 (Flush)。

**Why this works?**
如果在 Step 4.1 之後、4.2 之前崩潰：重啟後，MySQL 檢查 Redo Log 發現是 `prepare` 狀態，會去檢查 Binlog。若 Binlog 完整，則提交交易；否則回滾。這保證了主從一致性。
**Why this works?**
If a crash occurs after Step 4.1 but before 4.2: Upon restart, MySQL checks the Redo Log and finds the `prepare` state, then checks the Binlog. If the Binlog is complete, it commits the transaction; otherwise, it rolls back. This guarantees Primary-Replica consistency.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 忽視 "Double 1" 設定 (Ignoring "Double 1" Settings)
*   **Anti-pattern**: 為了追求極致寫入效能，將 `innodb_flush_log_at_trx_commit` 設為 0 或 2，且 `sync_binlog` 設為 0。
*   **Risk**: 在 Server Crash 或 OS Crash 時，可能遺失最近 1 秒甚至更多的交易資料。這對於金融或訂單系統是不可接受的。
*   **Best Practice**: 對於核心業務，堅持 `innodb_flush_log_at_trx_commit=1` 和 `sync_binlog=1`。這被稱為「雙 1 設定」，保證 ACID 的 D (Durability)。
*   **Anti-pattern**: Setting `innodb_flush_log_at_trx_commit` to 0 or 2, and `sync_binlog` to 0 for extreme write performance.
*   **Risk**: In the event of a Server or OS Crash, recent transaction data (1 second or more) may be lost. This is unacceptable for financial or order systems.
*   **Best Practice**: For core business logic, insist on `innodb_flush_log_at_trx_commit=1` and `sync_binlog=1`. This is known as the "Double 1 Setting," guaranteeing the 'D' (Durability) in ACID.

### 5.2 誤解 Buffer Pool 大小 (Misunderstanding Buffer Pool Size)
*   **Anti-pattern**: 在專用 DB Server 上只給 Buffer Pool 分配預設值 (128MB)，或者分配過大導致 OS Swapping。
*   **Correction**: 在專用機器上，通常建議將實體記憶體的 60%-75% 分配給 `innodb_buffer_pool_size`。必須留空間給 OS 本身以及每個 Connection 的 Thread Stack。
*   **Anti-pattern**: Allocating only the default value (128MB) to the Buffer Pool on a dedicated DB server, or allocating too much, causing OS Swapping.
*   **Correction**: On a dedicated machine, it is generally recommended to allocate 60%-75% of physical memory to `innodb_buffer_pool_size`. Space must be reserved for the OS itself and the Thread Stack for each connection.

### 5.3 關閉 Doublewrite Buffer (Disabling Doublewrite Buffer)
*   **Context**: InnoDB Page 是 16KB，但檔案系統 Page 通常是 4KB。寫入時若斷電，可能只寫了前 4KB (Partial Page Write)。
*   **Anti-pattern**: 為了效能關閉 Doublewrite Buffer。
*   **Correction**: 除非你使用支援原子寫入 (Atomic Write) 的高階儲存系統 (如某些 Fusion-IO 硬體或 ZFS 特定配置)，否則**永遠不要關閉** Doublewrite Buffer。它是防止資料庫物理損毀的最後一道防線。
*   **Context**: An InnoDB Page is 16KB, but filesystem pages are typically 4KB. If power is lost during a write, only the first 4KB might be written (Partial Page Write).
*   **Anti-pattern**: Disabling Doublewrite Buffer for performance.
*   **Correction**: Unless you are using high-end storage systems that support Atomic Writes (e.g., certain Fusion-IO hardware or specific ZFS configurations), **never disable** the Doublewrite Buffer. It is the last line of defense against physical database corruption.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: Redo Log 和 Binlog 有什麼本質區別？為什麼需要兩個 Log？
### Q1: What is the fundamental difference between Redo Log and Binlog? Why do we need both?

*   **Key Points**:
    *   **層級不同**：Redo 是 InnoDB 層（物理）；Binlog 是 Server 層（邏輯）。
    *   **內容不同**：Redo 記錄「Page X 修改了什麼」；Binlog 記錄「SQL 語句」或「Row data」。
    *   **寫入方式**：Redo 是循環寫入；Binlog 是追加寫入。
    *   **用途**：Redo 用於 Crash Recovery；Binlog 用於 Replication 和 PITR。
    *   **歷史原因**：MySQL 先有 Binlog，後來引入 InnoDB 才有了 Redo Log。

### Q2: 什麼是 Partial Page Write？MySQL 如何解決這個問題？
### Q2: What is a Partial Page Write? How does MySQL solve this problem?

*   **Key Points**:
    *   解釋 Page Size 不匹配 (16KB vs 4KB) 導致的寫入中斷風險。
    *   解釋 **Doublewrite Buffer**：在寫入真正的 Data File 之前，先順序寫入到 System Tablespace 的 Doublewrite 區域。
    *   恢復流程：若崩潰，InnoDB 檢查 Doublewrite Buffer 與 Data File。若 Data File 損毀，從 Doublewrite Buffer 還原；若 Doublewrite 損毀但 Data File 完好，則丟棄 Doublewrite 內容並重做 Redo Log。

### Q3: 描述一下 MySQL 的 Crash Recovery 流程。
### Q3: Describe the Crash Recovery process in MySQL.

*   **Key Points**:
    1.  啟動時，InnoDB 檢測到上次非正常關閉。
    2.  應用 **Redo Log**：將所有已寫入 Log 但未 Flush 到磁碟的 Page 重做一遍 (Redo)，讓記憶體回到崩潰前狀態。
    3.  處理 **Undo Log**：檢查所有未 Commit 的交易，執行 Rollback，保證原子性。
    4.  如果是 2PC 階段崩潰，需檢查 Binlog 完整性來決定 Commit 或 Rollback。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 重點回顧 (Key Takeaways)
1.  **架構分離**：Server Layer 處理 SQL 邏輯，Storage Engine (InnoDB) 處理資料存儲與交易。
2.  **Buffer Pool**：是資料庫的核心運作區，不僅僅是 Cache。
3.  **WAL (Write-Ahead Logging)**：先寫 Log 再寫 Disk，將隨機 I/O 轉為順序 I/O，提升效能並保證 ACID。
4.  **Redo vs Binlog**：物理日誌保證 Crash Safe，邏輯日誌保證 Replication。
5.  **Doublewrite Buffer**：解決硬體與軟體 Page Size 不一致導致的資料損毀問題。

### 下一步 (Next Steps)
理解了資料如何被「安全地儲存」後，下一章我們將探討資料如何被「快速地檢索」。
Now that we understand how data is "safely stored," in the next chapter, we will explore how data is "quickly retrieved."

*   **Chapter 02**: **Indexing and B+ Tree Internals (索引與 B+ Tree 核心)**
    *   B+ Tree 的結構優勢。
    *   Clustered Index vs. Secondary Index。
    *   Covering Index 與 Index Merge 優化。