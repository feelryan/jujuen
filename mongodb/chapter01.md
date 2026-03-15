# 1. 前言與學習目標 (Introduction and Learning Objectives)

作為一名資深工程師，僅僅知道如何撰寫 `find()` 或 `aggregate()` 查詢是遠遠不夠的。在處理高併發寫入、資料一致性要求極高的金融或電商場景時，你必須理解 MongoDB 的底層是如何將資料安全地持久化（Persist）到硬碟上。

As a Senior Engineer, knowing how to write `find()` or `aggregate()` queries is far from sufficient. When dealing with high-concurrency writes or scenarios requiring strict data consistency—such as fintech or e-commerce—you must understand how MongoDB fundamentally persists data securely to disk.

本章將帶你深入 MongoDB 的預設儲存引擎 WiredTiger 的核心機制。完成本章後，你將能夠：

This chapter takes you deep into the core mechanisms of MongoDB's default storage engine, WiredTiger. By the end of this chapter, you will be able to:

1.  **解釋資料落盤流程**：清楚描述從應用程式發出寫入請求，到資料進入 Journal、Cache，最終 Flush 到 Data Files 的完整生命週期。
    **Explain the Data Persistence Flow**: Clearly describe the full lifecycle of a write request from the application, through the Journal and Cache, and finally flushing to Data Files.
2.  **調優記憶體配置**：理解 WiredTiger Cache 與 Filesystem Cache 的互動關係，並能針對 Container/Kubernetes 環境正確設定記憶體限制。
    **Tune Memory Configuration**: Understand the interaction between the WiredTiger Cache and the Filesystem Cache, and correctly configure memory limits for Container/Kubernetes environments.
3.  **評估耐久性與效能權衡**：在系統設計時，能根據業務需求在 Write Concern (`j: true`) 與效能之間做出正確的取捨。
    **Evaluate Durability vs. Performance Trade-offs**: Make informed decisions between Write Concern (`j: true`) and performance based on business requirements during system design.
4.  **理解 BSON 底層優勢**：解釋為何 MongoDB 選擇 BSON 而非純文字 JSON，以及這對掃描效能的影響。
    **Understand BSON Internals**: Explain why MongoDB chose BSON over plain text JSON and its impact on scanning performance.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要掌握 MongoDB 的架構，我們需要建立幾個關鍵的心智模型，這與傳統 RDBMS（如 MySQL/PostgreSQL）有相似之處，但細節迥異。

To master MongoDB's architecture, we need to establish several key mental models. These share similarities with traditional RDBMS (like MySQL/PostgreSQL) but differ significantly in details.

### 2.1 WiredTiger Storage Engine (儲存引擎)

WiredTiger 是 MongoDB (自 3.2 版起) 的預設儲存引擎。它採用了 **B-Tree** 結構來儲存資料（雖然也支援 LSM Tree，但 MongoDB 預設使用 B-Tree）。

WiredTiger is the default storage engine for MongoDB (since version 3.2). It uses a **B-Tree** structure to store data (although it supports LSM Trees, MongoDB uses B-Trees by default).

*   **Document-Level Concurrency (文件級併發)**：
    與舊版 MMAPv1 的 Collection-level lock 不同，WiredTiger 支援文件級鎖定。這意味著多個執行緒可以同時寫入同一個 Collection，只要它們修改的是不同的 Document。
    Unlike the old MMAPv1's collection-level lock, WiredTiger supports document-level locking. This means multiple threads can write to the same collection simultaneously, provided they are modifying different documents.

*   **MVCC (Multi-Version Concurrency Control)**：
    WiredTiger 使用 MVCC 來提供讀取一致性。當一個寫入操作開始時，讀取操作仍然可以看到該操作開始前的資料快照（Snapshot）。這避免了讀寫鎖的激烈競爭。
    WiredTiger uses MVCC to provide read consistency. When a write operation begins, read operations can still see a snapshot of the data as it existed before the operation started. This prevents intense contention between read and write locks.

### 2.2 The Memory Model: Two Layers of Caching (雙層快取模型)

這是資深工程師最容易混淆的部分。MongoDB 的記憶體使用包含兩大部分：

This is the part most often confused by senior engineers. MongoDB's memory usage consists of two main parts:

1.  **WiredTiger Internal Cache**:
    這是 MongoDB 應用層直接管理的快取，預設大小約為 `(RAM - 1GB) * 50%`。這裡存放未壓縮的原始資料與索引，方便 CPU 快速運算。
    This is the cache directly managed by the MongoDB application layer, defaulting to approximately `(RAM - 1GB) * 50%`. It holds uncompressed raw data and indexes for fast CPU processing.

2.  **Filesystem Cache (OS Cache)**:
    MongoDB 利用作業系統的 Page Cache 來快取壓縮過的資料檔。這使得 MongoDB 能有效利用剩餘的 RAM，而不必自己管理所有的磁碟 I/O 快取。
    MongoDB leverages the operating system's Page Cache to cache compressed data files. This allows MongoDB to effectively utilize the remaining RAM without managing all disk I/O caching itself.

> **Mental Model**: 想像你在圖書館。
> **WiredTiger Cache** 是你的「書桌」，上面放著打開的書（未壓縮資料），隨時可以閱讀。
> **Filesystem Cache** 是離你最近的「書架」，上面放著合起來的書（壓縮資料），拿取比去地下室（Disk）快，但你需要先把它拿到書桌上打開（解壓縮）。
>
> **Mental Model**: Imagine you are in a library.
> The **WiredTiger Cache** is your "desk," holding open books (uncompressed data) ready to read.
> The **Filesystem Cache** is the nearest "bookshelf," holding closed books (compressed data). Retrieving them is faster than going to the basement (Disk), but you must bring them to the desk and open them (decompress) first.

### 2.3 Journaling (預寫式日誌)

Journaling 是 MongoDB 的 Write-Ahead Log (WAL)。在資料真正寫入資料檔（Data Files）之前，變更會先被寫入 Journal。

Journaling is MongoDB's Write-Ahead Log (WAL). Before data is actually written to the Data Files, changes are first written to the Journal.

*   **目的 (Purpose)**：崩潰恢復 (Crash Recovery)。如果 Server 斷電，記憶體中的資料（Dirty Pages）會遺失，但重啟後可以重放 Journal 來恢復資料。
    **Purpose**: Crash Recovery. If the server loses power, data in memory (Dirty Pages) is lost, but the Journal can be replayed upon restart to recover the data.

### 2.4 BSON (Binary JSON)

BSON 不僅僅是二進位的 JSON。它包含額外的型別資訊（如 Date, Binary, ObjectId）與**長度前綴 (Length Prefix)**。

BSON is not just binary JSON. It contains additional type information (like Date, Binary, ObjectId) and a **Length Prefix**.

*   **Traversability (遍歷性)**：由於 BSON 在物件頭部記錄了長度，MongoDB 在掃描時如果不需要讀取某個子文件，可以直接根據長度「跳過」該區塊，而不需要像 JSON Parser 那樣逐字元掃描尋找結尾括號。這對資料庫掃描效能至關重要。
    **Traversability**: Since BSON records the length at the object header, if MongoDB doesn't need to read a sub-document during a scan, it can simply "skip" that block based on the length, rather than scanning character-by-character for a closing brace like a JSON parser. This is crucial for database scan performance.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計中，理解這些內部機制會直接影響你對 **RPO (Recovery Point Objective)** 和 **寫入延遲 (Write Latency)** 的評估。

In system design, understanding these internal mechanisms directly impacts your assessment of **RPO (Recovery Point Objective)** and **Write Latency**.

### 3.1 Checkpoint vs. Journaling 的權衡 (The Trade-off)

在 Production 環境中，資料並不是每次寫入都立即存入 Data Files（`.wt` 檔案）。

In a Production environment, data is not immediately saved to Data Files (`.wt` files) with every write.

*   **Checkpoint**: WiredTiger 預設每 **60 秒**（或當 Journal 達到 2GB）執行一次 Checkpoint。Checkpoint 會將記憶體中的 Dirty Pages 寫入 Data Files 並同步到磁碟。
    **Checkpoint**: WiredTiger performs a Checkpoint every **60 seconds** (or when the Journal reaches 2GB) by default. A Checkpoint writes Dirty Pages from memory to Data Files and syncs them to disk.
*   **Journal**: 為了填補這 60 秒的空窗期，Journal 預設每 **100ms** 寫入磁碟一次（如果設定 `j: true` 則會隨每次寫入強制刷盤）。
    **Journal**: To fill this 60-second gap, the Journal writes to disk every **100ms** by default (or forces a flush on every write if `j: true` is set).

**System Design Decision**:
如果你的系統不能容忍 100ms 的資料遺失（例如支付系統），你必須在 Application Client 端設定 Write Concern `{ w: "majority", j: true }`。這會導致寫入延遲增加，因為必須等待磁碟 I/O，但保證了 durability。

**System Design Decision**:
If your system cannot tolerate 100ms of data loss (e.g., a payment system), you must set the Write Concern `{ w: "majority", j: true }` on the Application Client side. This increases write latency because it must wait for disk I/O, but it guarantees durability.

### 3.2 容器化環境的記憶體限制 (Memory Limits in Containerized Environments)

在 Kubernetes 或 Docker 中部署 MongoDB 時，常見的一個嚴重錯誤是沒有限制 WiredTiger Cache。

When deploying MongoDB in Kubernetes or Docker, a common critical mistake is failing to limit the WiredTiger Cache.

*   **情境 (Scenario)**：你給 Pod 限制了 4GB RAM。MongoDB 預設會看 Host 的 RAM（假設 Node 有 64GB）。WiredTiger 會嘗試佔用 `(64 - 1) * 0.5 = 31.5GB` 的記憶體。
    **Scenario**: You limit the Pod to 4GB RAM. MongoDB defaults to looking at the Host's RAM (assume the Node has 64GB). WiredTiger will attempt to claim `(64 - 1) * 0.5 = 31.5GB` of memory.
*   **後果 (Consequence)**：OOM Killer 會殺死 MongoDB 程序，導致 Pod 不斷重啟。
    **Consequence**: The OOM Killer will terminate the MongoDB process, causing the Pod to restart loop.
*   **解決方案 (Solution)**：必須明確設定 `storage.wiredTiger.engineConfig.cacheSizeGB`。
    **Solution**: You must explicitly set `storage.wiredTiger.engineConfig.cacheSizeGB`.

---

# 4. 逐步示例：寫入操作的生命週期 (Walkthrough: Lifecycle of a Write Operation)

讓我們追蹤一個簡單的寫入操作：`db.users.insertOne({ name: "Alice" })`，看看底層發生了什麼。

Let's trace a simple write operation: `db.users.insertOne({ name: "Alice" })`, and see what happens under the hood.

### Step 1: Request & Parsing
應用程式發送 BSON 封包。MongoDB 網路層接收並解析指令。
The application sends a BSON packet. The MongoDB network layer receives and parses the command.

### Step 2: WiredTiger Cache (Memory)
資料首先被寫入 **WiredTiger Cache**。此時資料是「髒的 (Dirty)」，尚未存入磁碟。
The data is first written to the **WiredTiger Cache**. At this point, the data is "Dirty" and has not yet been saved to disk.
*   *Latency*: 微秒級 (Microseconds)。
*   *Durability*: 無 (None)。若此時斷電，資料遺失。

### Step 3: Journal Buffer -> Journal File (Disk)
同時，這個操作被寫入記憶體中的 Journal Buffer。
Simultaneously, this operation is written to the Journal Buffer in memory.
*   **Case A (Default)**: 每 100ms，Buffer 被 flush 到磁碟上的 Journal file。
    **Case A (Default)**: Every 100ms, the Buffer is flushed to the Journal file on disk.
*   **Case B (j: true)**: MongoDB 強制立即執行 `fsync`，將 Journal 寫入磁碟，然後才回傳 "OK" 給 Client。
    **Case B (j: true)**: MongoDB forces an immediate `fsync`, writing the Journal to disk before returning "OK" to the Client.

### Step 4: Checkpoint (Disk - Data Files)
每 60 秒，WiredTiger 執行 Checkpoint。
Every 60 seconds, WiredTiger performs a Checkpoint.
1.  將 Cache 中的 Dirty Pages 整理。
    Organizes Dirty Pages in the Cache.
2.  寫入 `.wt` 資料檔。
    Writes to `.wt` data files.
3.  執行 `fsync` 確保資料落盤。
    Executes `fsync` to ensure data is on disk.
4.  一旦 Checkpoint 完成，對應的舊 Journal log 就可以被修剪（刪除或封存）。
    Once the Checkpoint is complete, the corresponding old Journal logs can be pruned (deleted or archived).

### 程式碼與配置示例 (Code & Config Example)

若要觀察或調整此行為，我們通常在 `mongod.conf` 或啟動參數中設定：

To observe or adjust this behavior, we typically configure `mongod.conf` or startup parameters:

```yaml
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
    # commitIntervalMs: 100 # Default is 100ms. Lowering this increases I/O load but reduces data loss window.
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2 # Explicitly set for container environments (e.g., if container limit is 4GB)
```

在 Client 端程式碼 (Node.js 範例) 控制耐久性：

Controlling durability in Client-side code (Node.js example):

```javascript
// High Durability: Wait for journal write
// 高耐久性：等待日誌寫入
await db.collection('payments').insertOne(
  { amount: 100, currency: "USD" },
  { writeConcern: { w: "majority", j: true } }
);

// High Performance: Acknowledge only memory write (risk of 100ms data loss)
// 高效能：僅確認記憶體寫入（有 100ms 資料遺失風險）
await db.collection('logs').insertOne(
  { event: "click" },
  { writeConcern: { w: 1, j: false } }
);
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 誤解 Working Set Size (WSS)
**錯誤 (Pitfall)**：認為只要資料庫總大小 (Total Data Size) 超過 RAM，效能就會崩潰。
**Mistake**: Thinking that performance will crash as soon as the Total Data Size exceeds RAM.

**分析 (Analysis)**：MongoDB 的效能主要取決於 **Working Set** (熱資料 + 索引)。只要熱資料和索引能放進 RAM，效能通常很好。
**Analysis**: MongoDB performance depends mainly on the **Working Set** (hot data + indexes). As long as hot data and indexes fit in RAM, performance is usually good.

**反模式 (Anti-pattern)**：設計了隨機存取極大的 Schema（例如使用 UUID 作為 `_id` 且無序寫入），導致索引無法常駐記憶體，引發頻繁的 Page Faults。
**Anti-pattern**: Designing a schema with widely random access (e.g., using UUIDs as `_id` with unordered writes), causing indexes to be evicted from memory frequently, triggering frequent Page Faults.

### 5.2 關閉 Journaling 以提升效能
**錯誤 (Pitfall)**：在 Production 環境設定 `storage.journal.enabled: false`。
**Mistake**: Setting `storage.journal.enabled: false` in a Production environment.

**分析 (Analysis)**：雖然這能提升寫入吞吐量，但一旦發生非正常關機（斷電、Crash），WiredTiger 的資料檔可能會損壞且**無法修復**。Journaling 不僅是為了救回資料，更是為了保證資料庫結構的一致性。
**Analysis**: While this increases write throughput, in the event of an unclean shutdown (power loss, crash), WiredTiger data files may become corrupted and **unrecoverable**. Journaling is not just for recovering data; it ensures the structural consistency of the database.

### 5.3 忽略 NUMA 架構
**錯誤 (Pitfall)**：在多 CPU 插槽的伺服器上直接運行 MongoDB，未關閉 NUMA (Non-Uniform Memory Access)。
**Mistake**: Running MongoDB directly on multi-socket servers without disabling NUMA.

**後果 (Consequence)**：MongoDB 可能在某個 CPU Node 的記憶體用盡時變慢，即使其他 Node 還有記憶體。應始終使用 `numactl --interleave=all` 啟動 mongod。
**Consequence**: MongoDB might slow down when one CPU Node's memory is exhausted, even if other Nodes have free memory. Always start mongod with `numactl --interleave=all`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試資深候選人，或在團隊內部進行架構審查。

These questions can be used to interview senior candidates or during internal architectural reviews.

### Q1: MongoDB 的 Checkpoint 機制是 60 秒一次，如果在這期間 Server Crash，資料會遺失嗎？
**Q1: MongoDB's Checkpoint mechanism runs every 60 seconds. If the server crashes during this interval, is data lost?**

*   **關鍵點 (Key Points)**：
    *   不會全部遺失（取決於 Journal 配置）。
    *   解釋 Journaling 的角色：它記錄了 Checkpoint 之間的所有操作。
    *   重啟時，MongoDB 會讀取上一次 Checkpoint 的資料，然後重放 (Replay) Journal 中的日誌來恢復狀態。
    *   資料遺失窗口最多是 Journal flush interval (預設 100ms)，若 `j:true` 則為 0。

### Q2: 為什麼 MongoDB 寫入大量資料時，記憶體使用率看起來沒有「爆滿」，但 `free -m` 顯示可用記憶體很少？
**Q2: Why does `free -m` show very little available memory when MongoDB is writing a lot of data, even if MongoDB's internal cache usage doesn't look "full"?**

*   **關鍵點 (Key Points)**：
    *   區分 **WiredTiger Cache** 與 **Filesystem Cache**。
    *   Linux 會將未使用的 RAM 用作 Page Cache (Buffer/Cache) 來加速磁碟 I/O。
    *   這是正常且健康的現象。只要 application 需要記憶體，OS 會自動回收 Page Cache。

### Q3: 比較 B-Tree (WiredTiger 預設) 與 LSM Tree (如 Cassandra/RocksDB) 在寫入密集場景下的差異。
**Q3: Compare B-Tree (WiredTiger default) vs. LSM Tree (e.g., Cassandra/RocksDB) in write-intensive scenarios.**

*   **關鍵點 (Key Points)**：
    *   B-Tree 適合讀多寫少或讀寫平衡。寫入時需要維護樹結構，隨機寫入可能導致大量的 Disk Seek (如果記憶體放不下索引)。
    *   LSM Tree (Log-Structured Merge-tree) 將隨機寫入轉換為順序寫入 (Append only)，寫入效能極高，但讀取時可能需要合併多個層級的資料 (Read amplification)。
    *   MongoDB 選擇 B-Tree 是為了保持強大的查詢與索引功能（如 Range Query, Secondary Indexes）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點摘要 (Key Takeaways)
1.  **WiredTiger** 使用文件級鎖定 (Document-Level Locking) 與 MVCC，大幅提升了併發效能。
2.  **記憶體架構** 分為 WiredTiger Internal Cache (未壓縮) 與 Filesystem Cache (壓縮)，在容器化環境需明確限制 Cache Size。
3.  **Journaling** 是資料耐久性的基石，填補了 Checkpoint (60s) 之間的空窗期。
4.  **Checkpoint** 將記憶體髒頁同步到磁碟資料檔，縮短了崩潰恢復所需的時間。
5.  **Write Concern** (`j: true`) 允許開發者在效能與資料安全性之間做細粒度的權衡。

### 下一步 (Next Steps)
理解了資料如何儲存後，下一步我們需要探討如何快速找到這些資料。
Now that we understand how data is stored, the next step is to explore how to find that data efficiently.

*   **Chapter 02: Indexing Strategies & Performance Tuning (索引策略與效能調優)**
    *   深入 B-Tree 索引結構。
    *   複合索引 (Compound Index) 的 ESR 規則。
    *   Covered Queries 與 Execution Plan 分析。