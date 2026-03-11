# 資料庫核心原理與儲存引擎
# Database Internals & Storage Engines

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，資料庫不應只是一個「儲存資料的黑盒子」。在系統設計面試或高併發架構決策中，能夠根據「寫入/讀取模式」選擇正確的儲存引擎（Storage Engine），是區分 Senior 與 Staff 工程師的關鍵能力。
For senior engineers, a database should not just be a "black box for storing data." In system design interviews or high-concurrency architecture decisions, the ability to choose the right storage engine based on "write/read patterns" is a key differentiator between Senior and Staff engineers.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **剖析 B-Tree 與 LSM Tree 的本質差異**：理解為何 MySQL 適合讀多寫少，而 Cassandra/RocksDB 適合寫多讀少。
    **Dissect the fundamental differences between B-Tree and LSM Tree**: Understand why MySQL fits read-heavy workloads, while Cassandra/RocksDB fits write-heavy workloads.
2.  **掌握 Row-oriented 與 Column-oriented 的適用場景**：從磁碟 I/O 與壓縮率的角度，解釋 OLTP 與 OLAP 的效能鴻溝。
    **Master the use cases for Row-oriented vs. Column-oriented**: Explain the performance gap between OLTP and OLAP from the perspectives of Disk I/O and compression ratios.
3.  **評估寫入放大（Write Amplification）與讀取放大（Read Amplification）**：在設計系統時，能預判不同儲存引擎在極端負載下的瓶頸。
    **Evaluate Write Amplification and Read Amplification**: Predict bottlenecks under extreme loads for different storage engines when designing systems.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 B-Tree vs. LSM Tree：隨機寫入 vs. 循序寫入
### 2.1 B-Tree vs. LSM Tree: Random Write vs. Sequential Write

**心智模型（Mental Model）：圖書館 vs. 記帳本**
**Mental Model: The Library vs. The Ledger**

*   **B-Tree (e.g., MySQL InnoDB, PostgreSQL): The Library**
    想像你在管理圖書館。每當有新書（Data）進來，你必須把它放到正確的分類架子（Page/Block）上。如果架子滿了，你需要移動書籍甚至拆分架子（Page Split）。
    Imagine managing a library. Whenever a new book (Data) arrives, you must place it on the correct shelf (Page/Block). If the shelf is full, you need to shift books around or even split the shelf (Page Split).
    *   **優點 (Pros)**：讀取非常快且穩定（O(log N)），因為資料是有序且索引好的。
    *   **缺點 (Cons)**：寫入成本高，因為涉及大量的**隨機 I/O (Random I/O)** 和頁面重組。

*   **LSM Tree (Log-Structured Merge-tree, e.g., Cassandra, RocksDB, LevelDB): The Ledger**
    想像你在記帳。每筆交易發生時，你只是快速地寫在當前的筆記本末尾（Append-only）。你不在乎順序，只求寫得快。稍後有空時，你再把這些散亂的紀錄整理（Compaction）成有序的檔案。
    Imagine keeping a ledger. When a transaction occurs, you simply append it to the end of the current notebook quickly. You don't care about order initially; speed is key. Later, in the background, you reorganize (Compaction) these scattered records into ordered files.
    *   **優點 (Pros)**：寫入極快，將隨機寫入轉換為**循序寫入 (Sequential I/O)**。
    *   **缺點 (Cons)**：讀取可能較慢，因為資料可能分散在不同的檔案（SSTables）中，需要合併查找。

### 2.2 Row-oriented vs. Column-oriented
### 2.2 Row-oriented vs. Column-oriented

**心智模型：名片盒 vs. 屬性清單**
**Mental Model: Rolodex vs. Attribute Lists**

*   **Row-oriented (e.g., MySQL, Postgres)**:
    資料以「行」為單位儲存。就像 CSV 檔案，一行接著一行。
    Data is stored by "row". Like a CSV file, line by line.
    *   `[ID:1, Name:Alice, Age:30], [ID:2, Name:Bob, Age:25]`
    *   **適合 (Best for)**：OLTP (Online Transaction Processing)。需要一次取出某個使用者的所有資訊（SELECT * FROM Users WHERE ID=1）。

*   **Column-oriented (e.g., Redshift, BigQuery, ClickHouse, Cassandra to some extent)**:
    資料以「列」為單位儲存。所有人的名字存一起，所有人的年齡存一起。
    Data is stored by "column". All names are stored together; all ages are stored together.
    *   `Names: [Alice, Bob], Ages: [30, 25]`
    *   **適合 (Best for)**：OLAP (Online Analytical Processing)。需要計算平均年齡（SELECT AVG(Age) FROM Users）。
    *   **關鍵優勢 (Key Advantage)**：極高的壓縮率（Compression Ratio），因為同一列的資料類型相同，重複性高。

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在系統設計面試或架構規劃中，選擇儲存引擎通常決定了系統的上限。
In system design interviews or architectural planning, the choice of storage engine often dictates the system's ceiling.

### 3.1 場景一：高頻交易訂單系統 (High-Frequency Order System)
### 3.1 Scenario 1: High-Frequency Order System

*   **需求 (Requirements)**：ACID 事務支援、強一致性、根據 OrderID 快速查詢。
*   **選擇 (Choice)**：**B-Tree (MySQL/PostgreSQL)**。
*   **理由 (Reasoning)**：這類系統是典型的 OLTP。讀寫通常針對單一或少量 Rows。B-Tree 提供了穩定的 Lookup 效能，且成熟的 RDBMS 提供了強大的鎖機制與事務隔離。
    This is a typical OLTP workload. Reads and writes usually target single or few rows. B-Tree provides stable lookup performance, and mature RDBMSs offer robust locking mechanisms and transaction isolation.

### 3.2 場景二：使用者行為 Log 收集 (User Activity Logging)
### 3.2 Scenario 2: User Activity Logging

*   **需求 (Requirements)**：極高的寫入吞吐量（Write Throughput）、允許最終一致性、資料量巨大。
*   **選擇 (Choice)**：**LSM Tree (Cassandra/ScyllaDB)**。
*   **理由 (Reasoning)**：Log 資料是 Append-only 的。B-Tree 在大量插入時會因為 Page Splitting 和 Random I/O 導致效能驟降。LSM Tree 利用 MemTable 和 WAL (Write Ahead Log) 將寫入緩衝並順序寫入磁碟，能承受數倍於 B-Tree 的寫入壓力。
    Log data is append-only. B-Trees suffer performance degradation during massive inserts due to Page Splitting and Random I/O. LSM Trees use MemTable and WAL to buffer writes and flush them sequentially to disk, handling write loads several times higher than B-Trees.

### 3.3 場景三：商業智慧報表 (Business Intelligence Dashboard)
### 3.3 Scenario 3: Business Intelligence Dashboard

*   **需求 (Requirements)**：對海量資料進行聚合運算（Sum, Avg, Count）、不需要即時更新。
*   **選擇 (Choice)**：**Columnar Store (ClickHouse/Redshift)**。
*   **理由 (Reasoning)**：分析查詢通常只涉及少數幾個欄位（例如「計算所有訂單的總金額」）。Column-oriented 資料庫只需讀取相關欄位的磁碟區塊，大幅減少 I/O。
    Analytical queries usually involve only a few columns (e.g., "Calculate total amount of all orders"). Column-oriented databases only need to read the disk blocks relevant to those columns, drastically reducing I/O.

---

## 4. 逐步示例：深入 LSM Tree 的讀寫路徑
## 4. Walkthrough / Example: Deep Dive into LSM Tree Read/Write Path

讓我們以一個基於 LSM Tree 的 Key-Value Store（如 RocksDB）為例，看看資料是如何流動的。
Let's take an LSM Tree-based Key-Value Store (like RocksDB) as an example to see how data flows.

### 步驟 1：寫入 (The Write Path)
### Step 1: The Write Path

當系統接收到 `PUT(Key="user:123", Value="data")`：
When the system receives `PUT(Key="user:123", Value="data")`:

1.  **Write Ahead Log (WAL)**: 資料首先被追加寫入到磁碟上的 WAL 檔案。這是為了崩潰恢復（Crash Recovery）。這是一個循序寫入操作，極快。
    Data is first appended to the WAL file on disk. This is for crash recovery. It is a sequential write operation and is extremely fast.
2.  **MemTable**: 資料隨後被寫入記憶體中的 MemTable（通常是一個 SkipList 或平衡樹）。此時寫入操作即視為成功。
    Data is then written to the in-memory MemTable (usually a SkipList or balanced tree). The write is considered successful at this point.

### 步驟 2：刷盤 (Flush to Disk)
### Step 2: Flush to Disk

當 MemTable 達到一定大小（例如 128MB）：
When the MemTable reaches a certain size (e.g., 128MB):

1.  MemTable 變為不可變（Immutable MemTable）。
    The MemTable becomes immutable.
2.  內容被 Flush 到磁碟，成為一個 **SSTable (Sorted String Table)**。這是一個 Level 0 (L0) 的檔案。
    The content is flushed to disk, becoming an **SSTable (Sorted String Table)**. This is a Level 0 (L0) file.
3.  **注意**：SSTable 內部的 Key 是有序的，但不同的 SSTable 之間 Key 範圍可能重疊（僅限 L0）。
    **Note**: Keys inside an SSTable are sorted, but key ranges may overlap between different SSTables (L0 only).

### 步驟 3：讀取 (The Read Path)
### Step 3: The Read Path

當系統接收到 `GET(Key="user:123")`：
When the system receives `GET(Key="user:123")`:

1.  **Check MemTable**: 先查記憶體，若有直接返回。
    Check memory first; return immediately if found.
2.  **Check SSTables**: 若記憶體沒有，則需從新到舊查找磁碟上的 SSTables。
    If not in memory, search SSTables on disk from newest to oldest.
    *   *效能隱憂 (Performance Concern)*：如果 L0 有 10 個檔案，可能需要讀 10 次磁碟。
    *   *優化 (Optimization)*：**Bloom Filter**。每個 SSTable 都有一個 Bloom Filter，能快速判斷「這個 Key **絕對不在** 這裡」或「**可能在** 這裡」，大幅減少無效的磁碟讀取。
    *   *Optimization*: **Bloom Filter**. Each SSTable has a Bloom Filter, which can quickly determine if "this Key is **definitely not** here" or "**might be** here," drastically reducing unnecessary disk reads.

### 步驟 4：壓縮 (Compaction)
### Step 4: Compaction

為了避免 SSTable 數量無限增長並清理被刪除的資料（Tombstones）：
To prevent the number of SSTables from growing infinitely and to clean up deleted data (Tombstones):

*   背景執行緒會選取數個 SSTables，將它們合併排序（Merge Sort），生成新的、更大的 SSTable，並丟棄舊檔。
    Background threads select several SSTables, merge-sort them, generate a new, larger SSTable, and discard the old ones.
*   這就是 **LSM (Log-Structured Merge)** 名稱的由來。
    This is the origin of the name **LSM (Log-Structured Merge)**.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 在 B-Tree 資料庫使用 UUID 作為 Primary Key
### 5.1 Using UUID as Primary Key in B-Tree Databases

*   **錯誤描述 (The Mistake)**：使用完全隨機的 UUID (v4) 作為 MySQL InnoDB 的主鍵。
*   **為何不好 (Why it's bad)**：
    *   B-Tree 依賴 Key 的順序來聚集資料（Clustered Index）。
    *   隨機 ID 導致新資料被插入到 B-Tree 的隨機位置（Random Page），引發頻繁的 **Page Splitting** 和 **Dirty Page Flush**。
    *   這會導致 Buffer Pool 命中率下降，I/O 暴增。
*   **解決方案 (Solution)**：使用 `AUTO_INCREMENT` ID 或有序的 UUID (如 UUID v7 / Snowflake ID)。

### 5.2 忽視 LSM Tree 的空間放大與寫入放大
### 5.2 Ignoring Space and Write Amplification in LSM Trees

*   **錯誤描述 (The Mistake)**：在寫入極度頻繁且 Update/Delete 很多的情境下，沒有調整 Compaction 策略。
*   **為何不好 (Why it's bad)**：
    *   LSM 的更新和刪除其實是寫入一條新紀錄（Update 是新值，Delete 是 Tombstone）。
    *   如果 Compaction 跟不上寫入速度，磁碟空間會被舊資料佔滿（空間放大）。
    *   讀取效能會因為需要掃描太多 SSTable 而急劇下降。
*   **解決方案 (Solution)**：監控 Compaction 延遲，根據負載選擇合適的 Compaction Strategy (e.g., Leveled vs. Tiered)。

### 5.3 誤用 Columnar DB 進行高併發點查詢
### 5.3 Misusing Columnar DB for High-Concurrency Point Lookups

*   **錯誤描述 (The Mistake)**：使用 ClickHouse 或 Redshift 作為使用者面向的 API 後端（例如 `GET /user/:id`）。
*   **為何不好 (Why it's bad)**：
    *   Columnar DB 為了讀取一行資料，需要打開多個檔案（每個 Column 一個檔案）並重新組裝。
    *   對於單行讀取，其延遲（Latency）遠高於 Row-oriented DB。
*   **解決方案 (Solution)**：架構分離。OLTP 用 MySQL/Postgres，OLAP 用 ClickHouse，中間透過 ETL 同步。

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 為什麼 Kafka 或 Cassandra 的寫入速度比 MySQL 快這麼多？
### Q1: Why is writing to Kafka or Cassandra so much faster than MySQL?

*   **高分回答要點 (Key Points)**：
    *   **I/O 模式**：區分 Sequential I/O (LSM/Log) 與 Random I/O (B-Tree)。機械硬碟與 SSD 對循序寫入的友善度。
    *   **結構差異**：LSM 寫入只需 Append WAL 和更新記憶體；B-Tree 可能需要讀取 Page、修改、處理 Split。
    *   **代價**：提到 Read Penalty（讀取較慢）和 Compaction 帶來的 CPU/IO 抖動。

### Q2: 在設計一個 Time-Series Database (TSDB) 時，你會選擇哪種儲存模型？
### Q2: When designing a Time-Series Database (TSDB), which storage model would you choose?

*   **高分回答要點 (Key Points)**：
    *   **LSM Tree** 是首選。時間序列資料通常是 Append-only，且寫入量巨大。
    *   **Columnar** 也是選項（如 InfluxDB 的某些實作），因為通常會針對某個 Metric（Column）做聚合。
    *   **資料保留 (Retention)**：討論如何高效刪除舊資料（LSM 可以直接 Drop 整個舊的 SSTable 檔案，比 B-Tree 逐行刪除快得多）。

### Q3: 什麼是寫入放大 (Write Amplification)？它如何影響 SSD 壽命與效能？
### Q3: What is Write Amplification? How does it affect SSD lifespan and performance?

*   **高分回答要點 (Key Points)**：
    *   **定義**：應用程式寫入 1MB 資料，導致磁碟實際發生 >1MB 的寫入。
    *   **B-Tree**：修改 Page 中一個 Byte 卻要重寫整個 4KB/16KB Page (Double Write Buffer)。
    *   **LSM**：資料在不同 Level 之間 Compaction 時被反覆讀寫多次。
    *   **影響**：消耗 SSD 的 P/E cycles（壽命），並佔用 I/O 頻寬影響前景查詢。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **B-Tree** = Read Optimized, Random Write (Update-in-place). 標準 RDBMS。
2.  **LSM Tree** = Write Optimized, Sequential Write (Append-only). NoSQL / NewSQL。
3.  **Row-oriented** = OLTP, 適合存取完整實體。
4.  **Column-oriented** = OLAP, 適合聚合分析與高壓縮。
5.  **I/O Physics** = 循序 I/O 永遠快於隨機 I/O，這是所有儲存引擎優化的物理基礎。
6.  **Immutable** = LSM 的核心特性，寫入後不修改，只透過 Compaction 合併。

### 後續延伸 (Next Steps)
*   **實作 (Practice)**：嘗試在本地運行 RocksDB，觀察其 Compaction log。
*   **閱讀 (Reading)**：深入了解 "Database Isolation Levels" (Chapter 03)，這與儲存引擎的並發控制（MVCC）息息相關。
*   **架構 (Architecture)**：研究 "CAP Theorem" 在分散式資料庫（如 Cassandra vs. HBase）中的取捨。