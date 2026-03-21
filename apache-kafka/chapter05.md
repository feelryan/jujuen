# 儲存引擎與日誌管理
# Storage Engine and Log Management

## 1. 前言與學習目標 (Introduction & Learning Objectives)

在分散式系統設計中，Apache Kafka 之所以能達成極高的吞吐量（Throughput），其底層的儲存引擎設計居功厥偉。對於資深工程師而言，理解 Kafka 如何將訊息寫入磁碟、如何利用索引快速查找，以及如何管理日誌生命週期，是進行效能調優與容量規劃的關鍵。

In distributed system design, Apache Kafka achieves extremely high throughput largely due to its underlying storage engine design. For senior engineers, understanding how Kafka writes messages to disk, utilizes indexes for fast lookups, and manages log lifecycles is crucial for performance tuning and capacity planning.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **剖析 Segment 檔案結構**：理解 `.log`、`.index` 與 `.timeindex` 的內部關聯與運作機制。
    **Dissect Segment File Structure**: Understand the internal relationships and mechanisms of `.log`, `.index`, and `.timeindex` files.
2.  **解釋稀疏索引（Sparse Indexing）**：說明 Kafka 如何在記憶體消耗與查找速度之間取得平衡。
    **Explain Sparse Indexing**: Describe how Kafka balances memory consumption and lookup speed.
3.  **掌握日誌清理策略（Cleanup Policies）**：區分 `delete` 與 `compact` 的適用場景，並理解 Compaction 的運作原理。
    **Master Log Cleanup Policies**: Distinguish between `delete` and `compact` scenarios and understand the mechanics of Compaction.
4.  **優化磁碟 I/O**：利用 Page Cache 與 Sequential I/O 的特性來優化系統設計。
    **Optimize Disk I/O**: Leverage Page Cache and Sequential I/O characteristics to optimize system design.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Partition 與 Segment 的關係 (The Relationship between Partition and Segment)

**直覺類比 (Analogy)**：
想像 Partition 是一套無限增長的百科全書。為了方便搬運與查閱，我們不會把它印成一本超厚的書，而是分成許多「冊」（Segments）。每一冊都有固定的頁數上限或時間跨度。當最新的一冊寫滿了，我們就封存它，並開始寫新的一冊。

**Intuitive Analogy**:
Imagine a Partition as an infinitely growing encyclopedia. To facilitate handling and reading, we don't print it as one massive book but divide it into many "volumes" (Segments). Each volume has a fixed page limit or time span. When the current volume is full, we seal it and start writing a new one.

**正規定義 (Formal Definition)**：
- **Partition**：邏輯上的日誌單元，對應到 OS 檔案系統中的一個 **目錄（Directory）**。
- **Segment**：Partition 的實體切分。每個 Segment 由一組檔案組成（Data Log, Offset Index, Time Index 等）。任何時刻只有一個 **Active Segment** 負責接收寫入。

**Formal Definition**:
- **Partition**: A logical log unit, corresponding to a **Directory** in the OS file system.
- **Segment**: The physical split of a Partition. Each Segment consists of a set of files (Data Log, Offset Index, Time Index, etc.). At any given time, only one **Active Segment** is responsible for receiving writes.

### 2.2 檔案結構三劍客 (The Trio of File Structure)

在 Kafka 的資料目錄下，你會看到如下的檔案命名規則（檔名代表該 Segment 的 Base Offset）：
In the Kafka data directory, you will see the following file naming convention (filenames represent the Base Offset of that Segment):

1.  **`00000000000000000000.log`**：實際儲存訊息的檔案。訊息按順序追加（Append-only）。
    The file that actually stores messages. Messages are appended sequentially.
2.  **`00000000000000000000.index`**：Offset 索引檔。映射 `Relative Offset` -> `Physical Position`。
    The Offset index file. Maps `Relative Offset` -> `Physical Position`.
3.  **`00000000000000000000.timeindex`**：時間戳索引檔。映射 `Timestamp` -> `Relative Offset`。
    The Timestamp index file. Maps `Timestamp` -> `Relative Offset`.

### 2.3 稀疏索引 (Sparse Indexing)

Kafka 不會為「每一條」訊息建立索引，而是採用 **稀疏索引**。它每隔一定數量的位元組（由 `log.index.interval.bytes` 控制，預設 4KB）才在 Index 檔中寫入一個條目。

Kafka does not create an index for *every* message; instead, it uses **Sparse Indexing**. It writes an entry to the Index file only after a certain amount of bytes (controlled by `log.index.interval.bytes`, default 4KB).

-   **優點 (Pros)**：大幅減少索引檔大小，使其能常駐於 RAM (Page Cache) 中。
    **Pros**: Significantly reduces index file size, allowing it to reside in RAM (Page Cache).
-   **代價 (Trade-off)**：查找時無法直接命中，需先找到「最接近且小於目標 Offset」的位置，再從該位置掃描 `.log` 檔。
    **Trade-off**: Lookups are not direct hits; one must find the "closest position less than the target Offset" and then scan the `.log` file from there.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 循序 I/O 與 Page Cache (Sequential I/O and Page Cache)

在系統設計面試或 Production 環境中，常被問到：「為什麼 Kafka 用磁碟還能這麼快？」

In system design interviews or production environments, a common question is: "Why is Kafka so fast despite using disk storage?"

**關鍵設計 (Key Design)**：
Kafka 依賴 OS 的 **Page Cache** 而非 JVM Heap 來快取資料。
Kafka relies on the OS **Page Cache** rather than the JVM Heap to cache data.

-   **Write Path**: Kafka 寫入時直接 Append 到檔案尾端（Sequential Write）。OS 會先寫入 Page Cache，並由背景執行緒（pdflush/flush）非同步刷入磁碟。這避免了隨機 I/O 的高延遲。
    **Write Path**: Kafka appends directly to the end of the file (Sequential Write). The OS writes to the Page Cache first, and background threads (pdflush/flush) asynchronously flush to disk. This avoids the high latency of random I/O.
-   **Read Path**: 當 Consumer 讀取近期資料時，資料極大機率還在 Page Cache 中，這時讀取完全是記憶體操作，無需觸碰實體磁碟。
    **Read Path**: When consumers read recent data, it is highly likely still in the Page Cache, making the read purely a memory operation without touching the physical disk.

### 3.2 Log Compaction 的應用場景 (Use Cases for Log Compaction)

並非所有 Topic 都適合預設的 `delete` 策略（基於時間或大小刪除）。

Not all topics are suitable for the default `delete` policy (deletion based on time or size).

-   **場景 (Scenario)**：Database Change Log (CDC)、應用程式狀態恢復 (Application State Recovery)。
-   **需求 (Requirement)**：我們只關心某個 Key 的「最新值」，舊值可以丟棄。
    We only care about the "latest value" for a given Key; old values can be discarded.
-   **設計影響 (Design Impact)**：使用 `cleanup.policy=compact` 可以確保 Consumer 在重啟後，只需讀取每個 Key 的最新狀態，大幅縮短恢復時間（Restore Time）。

---

## 4. 逐步示例 (Walkthrough / Example)

### 4.1 訊息查找流程 (Message Lookup Process)

假設 Consumer 請求讀取 Offset `368` 的訊息。
Suppose a Consumer requests to read the message at Offset `368`.

**步驟 1：定位 Segment (Locate Segment)**
Broker 在記憶體中維護一個 `ConcurrentSkipListMap`，儲存每個 Segment 的 Base Offset。
The Broker maintains a `ConcurrentSkipListMap` in memory, storing the Base Offset of each Segment.
-   Segment A: Base Offset 0
-   Segment B: Base Offset 300
-   Segment C: Base Offset 600
-   **結果**：目標在 Segment B (300 <= 368 < 600)。

**步驟 2：查找 Index 檔 (Search Index File)**
讀取 Segment B 的 `.index` 檔。這是一個排序好的陣列，使用 **二分搜尋法 (Binary Search)**。
Read Segment B's `.index` file. This is a sorted array, so **Binary Search** is used.
-   Index Entry 1: Offset 300 -> Position 0
-   Index Entry 2: Offset 350 -> Position 1024
-   Index Entry 3: Offset 400 -> Position 2048
-   **結果**：找到小於等於 368 的最大 Offset 是 `350`，對應物理位置 `1024`。
    **Result**: The largest Offset less than or equal to 368 is `350`, corresponding to physical position `1024`.

**步驟 3：掃描 Log 檔 (Scan Log File)**
Broker 從 `.log` 檔的 Position `1024` 開始順序讀取。
The Broker starts reading sequentially from Position `1024` of the `.log` file.
-   讀取 Offset 350... 不是
-   讀取 Offset 351... 不是
-   ...
-   讀取 Offset 368 -> **命中 (Hit)**。

**步驟 4：Zero-Copy 傳輸 (Zero-Copy Transfer)**
找到訊息後，Broker 使用 `sendfile` (Linux syscall) 直接將資料從 Page Cache 複製到 NIC Buffer，不經過 User Space。
After finding the message, the Broker uses `sendfile` (Linux syscall) to copy data directly from the Page Cache to the NIC Buffer, bypassing User Space.

### 4.2 Log Compaction 運作機制 (Log Compaction Mechanics)

```properties
# Server Properties
log.cleaner.enable=true
log.cleanup.policy=compact
log.cleaner.min.cleanable.ratio=0.5
```

**視覺化 (Visualization)**：
Log 被分為兩部分：**Head** (Active Segment, 未清理) 與 **Tail** (已清理)。
The Log is divided into two parts: **Head** (Active Segment, uncleaned) and **Tail** (cleaned).

1.  **Dirty Section**: 隨著 Active Segment 關閉，它們進入 "Dirty" 區域。
    As Active Segments close, they enter the "Dirty" section.
2.  **Cleaner Thread**: 當 Dirty Ratio 超過閾值（預設 0.5），Cleaner Thread 啟動。
    When the Dirty Ratio exceeds the threshold (default 0.5), the Cleaner Thread starts.
3.  **Map Phase**: 建立一個 HashMap (Key -> Latest Offset)。這需要記憶體 (`log.cleaner.dedupe.buffer.size`)。
    Builds a HashMap (Key -> Latest Offset). This requires memory (`log.cleaner.dedupe.buffer.size`).
4.  **Reduce Phase**: 重新複製 Log Segment，只保留那些 Offset 等於 Map 中最新 Offset 的訊息。
    Recopies the Log Segments, keeping only those messages whose Offset matches the latest Offset in the Map.
5.  **Swap**: 舊的 Segments 被刪除，替換為 Compact 後的新 Segment。
    Old Segments are deleted and replaced by the new Compacted Segment.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 忽略 File Descriptor 限制 (Ignoring File Descriptor Limits)

-   **錯誤 (Mistake)**：在單一 Broker 上建立了數千個 Topic，且每個 Topic 有多個 Partition。
    Creating thousands of Topics on a single Broker, with multiple Partitions per Topic.
-   **後果 (Consequence)**：每個 Partition 至少有 3 個檔案 (.log, .index, .timeindex)。若 Segment 切分過細（`log.segment.bytes` 太小），檔案數量會爆炸，導致 `Too many open files` 錯誤，甚至 Broker 當機。
    Each Partition has at least 3 files. If Segments are too small (`log.segment.bytes` is too small), the file count explodes, leading to `Too many open files` errors or Broker crashes.
-   **修正 (Fix)**：合理規劃 Partition 數量，並監控 OS 的 `ulimit -n`。
    Plan Partition counts reasonably and monitor the OS `ulimit -n`.

### 5.2 誤用 Compaction 於 Event Stream (Misusing Compaction for Event Streams)

-   **錯誤 (Mistake)**：對紀錄「使用者點擊流 (Clickstream)」的 Topic 開啟 Compaction。
    Enabling Compaction on a Topic recording "User Clickstreams".
-   **後果 (Consequence)**：點擊流通常沒有唯一的 Key (或 Key 重複率低)，且我們需要完整的歷史軌跡。Compaction 會消耗大量 CPU 與 I/O 進行無意義的清理，甚至導致資料遺失（如果 Key 重複）。
    Clickstreams usually lack unique Keys (or have low duplication), and we need the full history. Compaction consumes significant CPU and I/O for pointless cleaning and may cause data loss (if Keys duplicate).
-   **修正 (Fix)**：對 Event Stream 使用 `delete` policy。
    Use the `delete` policy for Event Streams.

### 5.3 索引檔損壞導致重啟緩慢 (Corrupted Index Causing Slow Restarts)

-   **錯誤 (Mistake)**：非正常關機（硬體斷電、kill -9）。
    Unclean shutdown (power failure, kill -9).
-   **後果 (Consequence)**：Index 檔可能與 Log 檔不一致。Broker 重啟時檢測到損壞，會強制從 Log 檔重建 Index（Sanity Check & Recovery），這是一個極度耗時的 I/O 操作，導致 Broker 數小時無法上線。
    The Index file may become inconsistent with the Log file. Upon restart, the Broker detects corruption and forces a rebuild of the Index from the Log (Sanity Check & Recovery), an extremely I/O-intensive operation that keeps the Broker offline for hours.
-   **修正 (Fix)**：確保 `log.flush.scheduler.interval.ms` 設定合理（雖然 Kafka 建議依賴 OS，但在極端可靠性需求下需權衡），並總是使用 `SIGTERM` 進行優雅關機。
    Ensure `log.flush.scheduler.interval.ms` is reasonable (though Kafka suggests relying on the OS, trade-offs exist for extreme reliability), and always use `SIGTERM` for graceful shutdowns.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如果 Consumer 想要根據時間戳記（Timestamp）回溯資料，Kafka 內部是如何執行的？
**If a Consumer wants to rewind data based on a Timestamp, how does Kafka execute this internally?**

-   **高分回答要點 (Key Points)**：
    1.  提到 `TimeIndex` 檔案：映射 Timestamp -> Relative Offset。
    2.  流程：先查 `TimeIndex` 找到對應的 Offset -> 再拿這個 Offset 去查 `Index` 檔案 -> 找到物理位置 (Position) -> 讀取 Log。
    3.  提到二分搜尋 (Binary Search) 的複雜度。
    4.  提到精確度問題：因為是稀疏索引，找到的 Offset 可能是目標時間點「附近」的，需要往下掃描驗證。

### Q2: 為什麼 Kafka 的索引檔（Index）要設計成固定大小（預設 10MB）並預先分配？
**Why are Kafka Index files designed to be fixed-size (default 10MB) and pre-allocated?**

-   **高分回答要點 (Key Points)**：
    1.  **Memory Mapping (mmap)**：固定大小的檔案更有利於 OS 進行 mmap 操作，提升讀寫效能。
    2.  **避免頻繁擴容**：如果是動態增長，OS 需要不斷尋找新的磁碟區塊，容易產生碎片。
    3.  **Rolling**：當 Index 寫滿時，會觸發 Log Segment 的 Rolling，即使 Log 檔本身還沒滿。

### Q3: Log Compaction 會影響 Broker 的讀寫效能嗎？如何控制？
**Does Log Compaction affect Broker read/write performance? How to control it?**

-   **高分回答要點 (Key Points)**：
    1.  會影響。Cleaner Thread 需要讀取 Log、建立 Hash Map (CPU/RAM)、並寫入新 Segment (Disk I/O)。
    2.  **控制手段**：
        -   `log.cleaner.threads`：控制並發清理的執行緒數量。
        -   `log.cleaner.io.max.bytes.per.second`：限制清理過程的 I/O 頻寬，避免搶佔正常生產與消費的資源（Throttling）。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Partition = Directory, Segment = Files**：Segment 是物理儲存的最小管理單元。
2.  **Sparse Index**：Kafka 使用稀疏索引來節省記憶體，以時間/CPU 換取空間。
3.  **Sequential I/O is King**：Kafka 的高效能建立在 Append-only log 與 Page Cache 之上。
4.  **Zero-Copy**：讀取路徑利用 `sendfile` 減少 Context Switch 與 CPU Copy。
5.  **Compaction != Deletion**：Compaction 是為了保留 Key 的最新狀態，適用於 K-V 類型的資料。

### 後續延伸 (Next Steps)
-   **進階閱讀**：研究 Kafka 的 **Tiered Storage (分層儲存)**，了解如何將舊的 Log Segments 卸載到 S3/GCS 以降低成本。
-   **下一章預告**：**Chapter 06 - Kafka 的高可用與複製機制 (High Availability & Replication Protocol)**。我們將探討 ISR、Controller 選舉與 Leader Epoch。