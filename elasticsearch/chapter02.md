# Chapter 02: 分散式系統機制與一致性
# Chapter 02: Distributed Mechanisms and Consistency

## 1. 前言與學習目標
## 1. Introduction and Learning Goals

對於資深工程師而言，僅僅知道如何使用 ElasticSearch (ES) API 進行 CRUD 是遠遠不夠的。在系統設計面試或大規模生產環境中，你必須深刻理解 ES 如何處理資料的分散式儲存、故障復原以及一致性保證。本章將深入 ES 的底層機制。

For senior engineers, knowing how to perform CRUD operations via the ElasticSearch (ES) API is far from sufficient. In system design interviews or large-scale production environments, you must deeply understand how ES handles distributed storage, failure recovery, and consistency guarantees. This chapter dives into the underlying mechanisms of ES.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **詳解寫入路徑與資料安全性**：解釋 Translog、Refresh 與 Flush 的運作流程，以及它們如何防止資料遺失。
    **Explain the Write Path and Data Safety**: Describe the workflow of Translog, Refresh, and Flush, and how they prevent data loss.
2.  **掌握分散式共識與 Split-brain 防護**：區分 ES 7.x 之前與之後的 Cluster Coordination 機制差異（Zen Discovery vs. New Cluster Coordination），並理解如何避免 Split-brain。
    **Master Distributed Consensus and Split-brain Protection**: Differentiate the Cluster Coordination mechanisms before and after ES 7.x (Zen Discovery vs. New Cluster Coordination) and understand how to avoid split-brain scenarios.
3.  **設計高可用與一致性策略**：在系統設計中，正確配置 `wait_for_active_shards` 與 Shard/Replica 策略，以平衡效能與資料一致性。
    **Design High Availability and Consistency Strategies**: Correctly configure `wait_for_active_shards` and Shard/Replica strategies in system design to balance performance and data consistency.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 Lucene Index vs. Translog
### 2.1 Lucene Index vs. Translog

**心智模型 (Mental Model)**：
將 ES 的寫入過程想像成「會計記帳」。
- **Translog (Transaction Log)** 就像是「流水帳草稿」。每筆交易發生時，先快速寫在草稿上（循序寫入磁碟，速度快），確保斷電不遺失。
- **Lucene Segment** 就像是「正式歸檔的帳本」。將草稿整理、索引並壓縮成不可變的檔案（隨機寫入與合併，成本高）。

**Mental Model**:
Imagine the ES writing process as "accounting".
- **Translog (Transaction Log)** is like a "rough journal". When a transaction occurs, it's quickly written to the draft (sequential disk write, fast) to ensure no loss on power failure.
- **Lucene Segment** is like the "formal ledger". It organizes, indexes, and compresses the draft into immutable files (random writes and merging, expensive).

**核心機制 (Core Mechanism)**：
ES 是基於 Lucene 的。Lucene 的 `commit` 操作非常昂貴（涉及大量磁碟 I/O）。為了達到 Near Real-Time (NRT) 搜尋並保證資料不遺失，ES 引入了 **Translog**。資料寫入時會同時進入 Memory Buffer 和 Translog。

**Core Mechanism**:
ES is based on Lucene. A Lucene `commit` is very expensive (involving heavy disk I/O). To achieve Near Real-Time (NRT) search and guarantee data durability, ES introduces the **Translog**. Data is written to both the Memory Buffer and the Translog simultaneously.

### 2.2 分散式共識 (Distributed Consensus)
### 2.2 Distributed Consensus

**定義 (Definition)**：
在分散式系統中，節點間必須對「誰是 Master」以及「Cluster State（叢集狀態）」達成一致。

**Definition**:
In a distributed system, nodes must agree on "who is the Master" and the "Cluster State".

- **Pre-7.x (Zen Discovery)**: 類似於一種特殊的兩階段提交，依賴 `minimum_master_nodes` 來防止 Split-brain（腦裂）。配置錯誤極易導致資料不一致。
- **7.x+ (Cluster Coordination)**: 引入了更嚴謹的投票機制（類似 Raft 演算法的變體），移除了手動設定 `minimum_master_nodes` 的需求，讓 Master 選舉更安全。

- **Pre-7.x (Zen Discovery)**: Similar to a specialized two-phase commit, relying on `minimum_master_nodes` to prevent Split-brain. Misconfiguration easily led to data inconsistency.
- **7.x+ (Cluster Coordination)**: Introduced a stricter voting mechanism (a variant similar to the Raft algorithm), removing the need for manual `minimum_master_nodes` configuration, making Master election safer.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 寫入一致性與效能權衡 (Write Consistency vs. Performance Trade-off)
### 3.1 Write Consistency vs. Performance Trade-off

在設計高吞吐量的 Log 系統或金融交易紀錄系統時，你需要決定「寫入成功」的定義。

When designing high-throughput logging systems or financial transaction record systems, you need to define what "write success" means.

- **場景 (Scenario)**：你正在設計一個即時訂單搜尋系統。
- **挑戰 (Challenge)**：如果 Primary Shard 寫入成功但 Replica 失敗，隨後 Primary 當機，資料是否會遺失？
- **解決方案 (Solution)**：使用 `wait_for_active_shards` 參數。
    - 預設為 `1` (只要求 Primary 活著)。
    - 設定為 `all` 或 `quorum` (例如 `int( (primary + number_of_replicas) / 2 ) + 1`) 可以強保證一致性，但會降低可用性與寫入速度。

- **Scenario**: You are designing a real-time order search system.
- **Challenge**: If the Primary Shard write succeeds but the Replica fails, and then the Primary crashes, is the data lost?
- **Solution**: Use the `wait_for_active_shards` parameter.
    - Default is `1` (only requires Primary to be active).
    - Setting it to `all` or a `quorum` (e.g., `int( (primary + number_of_replicas) / 2 ) + 1`) guarantees strong consistency but reduces availability and write speed.

### 3.2 Split-brain 的災難 (The Disaster of Split-brain)
### 3.2 The Disaster of Split-brain

**什麼是 Split-brain？**
當網路分區（Network Partition）發生時，一個 Cluster 可能分裂成兩個獨立運作的小 Cluster，各自選出了自己的 Master，並同時接受寫入。當網路恢復時，這兩份資料將難以合併，導致資料永久損壞或遺失。

**What is Split-brain?**
When a network partition occurs, a cluster might split into two independently operating sub-clusters, each electing its own Master and accepting writes simultaneously. When the network recovers, merging these two datasets is incredibly difficult, leading to permanent data corruption or loss.

**系統設計影響 (System Design Impact)**：
在跨 AZ (Availability Zone) 部署 ES 時，必須確保 Master-eligible nodes 的數量與分佈能滿足多數決（Quorum）。
- **設計原則**：永遠保持奇數個 Master-eligible nodes（例如 3 個），並確保任一 AZ 斷線時，剩餘節點仍能組成多數。

**System Design Impact**:
When deploying ES across AZs (Availability Zones), you must ensure the number and distribution of Master-eligible nodes satisfy the Quorum.
- **Design Principle**: Always keep an odd number of Master-eligible nodes (e.g., 3), and ensure that if any AZ goes down, the remaining nodes can still form a majority.

---

## 4. 逐步示例：資料寫入與持久化流程
## 4. Walkthrough: Data Write and Persistence Flow

讓我們深入追蹤一個 Document 寫入請求的生命週期，理解 ES 如何保證資料不丟失。

Let's deeply trace the lifecycle of a Document write request to understand how ES ensures data durability.

### 步驟 1: 協調與路由 (Coordination & Routing)
### Step 1: Coordination & Routing

Client 發送寫入請求到任意節點（Coordinating Node）。該節點根據 Routing 公式確定 Primary Shard 位置：
`shard = hash(routing) % number_of_primary_shards`

The Client sends a write request to any node (Coordinating Node). This node determines the Primary Shard location based on the Routing formula:
`shard = hash(routing) % number_of_primary_shards`

### 步驟 2: Primary Shard 寫入 (Primary Shard Write)
### Step 2: Primary Shard Write

請求到達 Primary Shard 所在的 Data Node。
1.  **寫入 Memory Buffer**：資料被放入記憶體緩衝區。此時資料還**不可被搜尋**。
2.  **寫入 Translog**：同時，操作被追加到 Translog 檔案中（fsync 預設依賴配置，通常是每個請求或每 5 秒）。這是資料持久化的關鍵。

The request arrives at the Data Node hosting the Primary Shard.
1.  **Write to Memory Buffer**: Data is placed in the memory buffer. At this point, the data is **not searchable**.
2.  **Write to Translog**: Simultaneously, the operation is appended to the Translog file (fsync depends on config, usually per request or every 5 seconds). This is key to data durability.

### 步驟 3: Refresh (使資料可搜尋)
### Step 3: Refresh (Making Data Searchable)

每隔 `refresh_interval` (預設 1秒)：
1.  Memory Buffer 中的資料被寫入一個新的 **Lucene Segment**（在 OS Cache 中，尚未 fsync 到磁碟）。
2.  Segment 被打開以供搜尋。
3.  Memory Buffer 清空。
*注意：此時資料可被搜尋，但若斷電，資料僅存在於 Translog 和 OS Cache 中。*

Every `refresh_interval` (default 1s):
1.  Data in the Memory Buffer is written to a new **Lucene Segment** (in OS Cache, not yet fsync-ed to disk).
2.  The Segment is opened for search.
3.  The Memory Buffer is cleared.
*Note: Data is searchable now, but if power fails, data exists only in Translog and OS Cache.*

### 步驟 4: Flush (持久化至磁碟)
### Step 4: Flush (Persisting to Disk)

當 Translog 過大或每隔 30 分鐘：
1.  執行 **Lucene Commit**：將所有 OS Cache 中的 Segments 強制 `fsync` 到實體磁碟。
2.  **清空 Translog**：因為資料已安全落地，舊的 Translog 不再需要。
3.  建立新的 Translog。

When Translog gets too large or every 30 minutes:
1.  Execute **Lucene Commit**: Force `fsync` all Segments in OS Cache to physical disk.
2.  **Truncate Translog**: Since data is safely on disk, the old Translog is no longer needed.
3.  Create a new Translog.

### 步驟 5: 複製 (Replication)
### Step 5: Replication

Primary 寫入成功後，並行發送請求給所有 Replica Shards。一旦所有需要的 Replicas（根據 `wait_for_active_shards`）回應成功，Primary 才會回傳成功給 Client。

After Primary writes successfully, it sends requests to all Replica Shards in parallel. Once the required Replicas (based on `wait_for_active_shards`) acknowledge, the Primary returns success to the Client.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 忽視 `wait_for_active_shards`
### 5.1 Ignoring `wait_for_active_shards`

- **錯誤 (Pitfall)**：使用預設值 `1` 處理關鍵資料。
- **後果 (Consequence)**：當 Cluster 不穩定（例如正在 Rolling Restart）時，Primary 寫入成功但 Replica 未同步。若此時 Primary 硬體故障，該筆資料將永久遺失。
- **建議 (Advice)**：對於不能遺失的資料，設定為 `all` 或至少 `quorum`。

- **Pitfall**: Using the default value `1` for critical data.
- **Consequence**: When the Cluster is unstable (e.g., during a Rolling Restart), the Primary writes successfully but Replicas do not sync. If the Primary hardware fails at this moment, that data is permanently lost.
- **Advice**: For data that cannot be lost, set it to `all` or at least `quorum`.

### 5.2 誤解 Refresh 與 Flush
### 5.2 Misunderstanding Refresh vs. Flush

- **錯誤 (Pitfall)**：為了確保資料「寫入即存檔」，頻繁手動呼叫 `_flush` API。
- **後果 (Consequence)**：產生大量微小的 Lucene Segments，導致頻繁的 Merge 操作，嚴重消耗 CPU 和 I/O，甚至阻塞寫入。
- **建議 (Advice)**：依賴 ES 的自動 Flush 機制。如果需要「寫入即可見」，調整 `refresh_interval`，而不是呼叫 Flush。

- **Pitfall**: Frequently manually calling the `_flush` API to ensure data is "saved immediately".
- **Consequence**: Generates a large number of tiny Lucene Segments, causing frequent Merge operations, severely consuming CPU and I/O, and potentially blocking writes.
- **Advice**: Rely on ES's automatic Flush mechanism. If you need "visible immediately upon write", adjust `refresh_interval` instead of calling Flush.

### 5.3 腦裂配置錯誤 (Legacy Versions)
### 5.3 Split-brain Misconfiguration (Legacy Versions)

- **錯誤 (Pitfall)**：在 ES 6.x 及以下版本，3 個 Master 節點卻將 `discovery.zen.minimum_master_nodes` 設為 1。
- **後果 (Consequence)**：網路閃斷時，產生兩個 Master，資料寫入兩邊，造成資料不一致。
- **建議 (Advice)**：公式永遠是 `(master_eligible_nodes / 2) + 1`。盡快升級至 ES 7.x+ 以利用新的 Cluster Coordination 機制。

- **Pitfall**: In ES 6.x and below, having 3 Master nodes but setting `discovery.zen.minimum_master_nodes` to 1.
- **Consequence**: During a network blip, two Masters are created, data is written to both, causing inconsistency.
- **Advice**: The formula is always `(master_eligible_nodes / 2) + 1`. Upgrade to ES 7.x+ ASAP to leverage the new Cluster Coordination mechanism.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: ES 是如何保證資料在斷電時不遺失的？(How does ES ensure data durability during power loss?)

- **高分回答要點 (Key Points)**：
    1.  提到 **Translog**：資料寫入 Memory Buffer 時同步寫入 Translog。
    2.  解釋 **fsync**：Translog 的 `fsync` 策略（預設 `request` 級別持久化）。
    3.  區分 **Refresh** 與 **Flush**：Refresh 只是讓資料可搜尋（仍在 Cache），Flush 才是真正的 Lucene Commit（落盤並清空 Translog）。
    4.  若 Translog 損壞，ES 如何透過 Replica 恢復。

- **Key Points**:
    1.  Mention **Translog**: Data is written to Translog synchronously when written to Memory Buffer.
    2.  Explain **fsync**: Translog's `fsync` strategy (default is `request` level persistence).
    3.  Distinguish **Refresh** vs. **Flush**: Refresh only makes data searchable (still in Cache), Flush is the real Lucene Commit (disk sync and clears Translog).
    4.  How ES recovers via Replicas if Translog is corrupted.

### Q2: 為什麼 ES 被稱為 "Near Real-Time" (NRT) 而不是 "Real-Time"？(Why is ES called "Near Real-Time" (NRT) instead of "Real-Time"?)

- **高分回答要點 (Key Points)**：
    1.  解釋 `refresh_interval` 機制（預設 1 秒）。
    2.  說明 Lucene Segment 的不可變性（Immutable）：重新打開一個 Segment 代價雖比 Commit 小，但仍非零成本。
    3.  權衡：為了寫入吞吐量（Throughput），我們延遲了搜尋的可見性（Visibility）。

- **Key Points**:
    1.  Explain the `refresh_interval` mechanism (default 1s).
    2.  Explain Lucene Segment immutability: Re-opening a segment is cheaper than a Commit but still has non-zero cost.
    3.  Trade-off: We delay search visibility to gain write throughput.

### Q3: 在分散式環境下，ES 如何處理併發寫入衝突？(How does ES handle concurrent write conflicts in a distributed environment?)

- **高分回答要點 (Key Points)**：
    1.  **Optimistic Concurrency Control (OCC)**：樂觀鎖。
    2.  使用 `_seq_no` (Sequence Number) 和 `_primary_term`。
    3.  舊版本使用 `_version`。
    4.  當寫入請求攜帶的序列號小於目前儲存的序列號時，ES 會拒絕寫入並拋出 `VersionConflictEngineException`。

- **Key Points**:
    1.  **Optimistic Concurrency Control (OCC)**.
    2.  Uses `_seq_no` (Sequence Number) and `_primary_term`.
    3.  Older versions used `_version`.
    4.  When a write request carries a sequence number lower than the currently stored one, ES rejects the write with a `VersionConflictEngineException`.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Translog** 是資料安全的最後一道防線，填補了 Memory Buffer 到 Lucene Commit 之間的空窗期。
2.  **Refresh** (預設 1s) 決定搜尋可見性；**Flush** 決定資料落盤與 Translog 清理。
3.  **Split-brain** 在舊版 ES 是常見災難，新版透過 Raft-like 演算法解決，但在架構設計（跨 AZ）時仍需注意 Quorum。
4.  **wait_for_active_shards** 是在寫入效能與資料一致性之間做取捨的關鍵參數。
5.  **Immutable Segments** 是 Lucene 的核心，這解釋了為什麼 Update 其實是 Delete + Insert，以及為什麼 Merge 是必要的。

### 後續延伸 (Next Steps)
- **Next Chapter**: 深入探討 **Indexing Performance & Sharding Strategy**。既然知道了寫入機制，下一步是如何優化寫入速度以及如何規劃 Shard 數量以避免 "Oversharding"。
- **Action Item**: 檢查你目前生產環境的 `refresh_interval` 設定。如果是大量批次寫入（Bulk Indexing），嘗試將其暫時設為 `-1` 或 `30s`，觀察效能提升。

- **Next Chapter**: Deep dive into **Indexing Performance & Sharding Strategy**. Now that you know the write mechanism, the next step is optimizing write speed and planning Shard counts to avoid "Oversharding".
- **Action Item**: Check the `refresh_interval` setting in your current production environment. If you are doing heavy Bulk Indexing, try temporarily setting it to `-1` or `30s` and observe the performance gain.