# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，僅僅知道「如何架設 Redis」是不夠的。在 System Design 面試或大規模生產環境中，你需要能夠根據業務需求（如資料量級、讀寫比例、一致性要求）選擇正確的架構模式。本章將深入探討 Redis 的高可用性（High Availability, HA）與水平擴展（Horizontal Scaling）機制。

As a senior engineer, simply knowing "how to set up Redis" is insufficient. In System Design interviews or large-scale production environments, you need to be able to select the correct architectural pattern based on business requirements (e.g., data volume, read/write ratio, consistency requirements). This chapter delves into Redis's High Availability (HA) and Horizontal Scaling mechanisms.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **區分 Sentinel 與 Cluster 的適用場景**：清楚解釋何時該用 Sentinel（HA 導向）以及何時該用 Cluster（分片導向）。
    **Distinguish between Sentinel and Cluster scenarios**: Clearly explain when to use Sentinel (HA-oriented) versus Cluster (Sharding-oriented).
2.  **掌握 Hash Slots 與分片原理**：理解 Redis Cluster 如何透過 16384 個 Hash Slots 實現無中心化的資料分佈。
    **Master Hash Slots and Sharding principles**: Understand how Redis Cluster implements decentralized data distribution via 16384 Hash Slots.
3.  **分析 CAP 定理在 Redis 中的權衡**：理解 Redis 在預設情況下為何無法保證強一致性（Strong Consistency），以及如何透過配置（如 `WAIT` 或 `min-replicas-to-write`）來調整一致性與可用性的天平。
    **Analyze CAP theorem trade-offs in Redis**: Understand why Redis does not guarantee Strong Consistency by default, and how to adjust the balance between consistency and availability via configurations (like `WAIT` or `min-replicas-to-write`).
4.  **處理故障轉移與客戶端重導向**：解釋 `MOVED` 與 `ASK` 錯誤的差異，以及 Client 端如何處理拓撲變更。
    **Handle Failover and Client Redirection**: Explain the difference between `MOVED` and `ASK` errors, and how clients handle topology changes.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Replication vs. Sentinel vs. Cluster

在 Redis 的演進過程中，有三種主要的架構模式，資深工程師必須建立清晰的心智模型來區分它們。

In the evolution of Redis, there are three main architectural patterns that senior engineers must distinguish with a clear mental model.

### Replication (Master-Replica)
*   **模型**：一個 Master 負責寫入，多個 Replicas 負責讀取。
*   **限制**：無法自動故障轉移（Failover）。若 Master 當機，需人工介入。
*   **Model**: One Master handles writes; multiple Replicas handle reads.
*   **Limitation**: No automatic failover. If the Master crashes, manual intervention is required.

### Redis Sentinel (哨兵模式)
*   **模型**：在 Replication 的基礎上，增加了一組「觀察者（Sentinels）」。這是一個**控制平面（Control Plane）**的解決方案。
*   **功能**：監控 Master 狀態，當 Master 失效時，透過共識演算法（Consensus）自動將某個 Replica 晉升為 Master。
*   **限制**：寫入能力仍受限於單一節點（Single Master），無法水平擴展寫入吞吐量。
*   **Model**: Adds a group of "Observers (Sentinels)" on top of Replication. This is a **Control Plane** solution.
*   **Function**: Monitors Master status. When the Master fails, it automatically promotes a Replica to Master via a consensus algorithm.
*   **Limitation**: Write capacity is still limited to a single node (Single Master); cannot horizontally scale write throughput.

### Redis Cluster (叢集模式)
*   **模型**：多主多從（Multi-Master, Multi-Replica）。這是一個**資料平面（Data Plane）**的分片解決方案。
*   **功能**：將資料切分到不同的節點（Sharding），同時具備 Sentinel 的故障轉移能力。
*   **關鍵機制**：**Hash Slots**。
*   **Model**: Multi-Master, Multi-Replica. This is a **Data Plane** sharding solution.
*   **Function**: Splits data across different nodes (Sharding) while possessing Sentinel-like failover capabilities.
*   **Key Mechanism**: **Hash Slots**.

## 2.2 Hash Slots: The Abstraction Layer

Redis Cluster 不使用一致性雜湊（Consistent Hashing），而是引入了 **Hash Slots** 的概念。

Redis Cluster does not use Consistent Hashing; instead, it introduces the concept of **Hash Slots**.

*   **定義**：整個 Cluster 被邏輯劃分為 **16,384** 個槽位。
*   **映射演算法**：`HASH_SLOT = CRC16(key) mod 16384`。
*   **心智模型**：想像一個有 16,384 個格子的巨大置物櫃。每個 Redis 節點（Node）只保管其中一部分格子的鑰匙。當你要存取資料時，先算出格子編號，再去找負責該格子的節點。
*   **Definition**: The entire Cluster is logically divided into **16,384** slots.
*   **Mapping Algorithm**: `HASH_SLOT = CRC16(key) mod 16384`.
*   **Mental Model**: Imagine a giant locker with 16,384 compartments. Each Redis Node holds the keys to only a subset of these compartments. When accessing data, you first calculate the compartment number, then go to the node responsible for that compartment.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design 面試中，選擇哪種架構取決於你的瓶頸（Bottleneck）。

In System Design interviews, choosing the right architecture depends on your bottleneck.

## 3.1 Decision Matrix (決策矩陣)

| Scenario | Recommended Architecture | Reasoning |
| :--- | :--- | :--- |
| **Small Dataset, Read Heavy** | **Sentinel** (1 Master + N Replicas) | 簡單。讀取可以透過增加 Replicas 擴展；寫入量不大，單機足夠。 <br> Simple. Reads scale by adding Replicas; write volume is low enough for a single machine. |
| **Large Dataset (> RAM limit), Write Heavy** | **Redis Cluster** | 需要分片（Sharding）來分散記憶體壓力和寫入負載。 <br> Requires Sharding to distribute memory pressure and write load. |
| **Strict Strong Consistency** | **Avoid Redis** (or use with extreme caution) | Redis 的非同步複製（Async Replication）意味著故障時可能遺失資料。若必須使用，需配置 `WAIT` 指令，但會犧牲效能。 <br> Redis's Async Replication implies potential data loss during failures. If mandatory, configure `WAIT`, but at the cost of performance. |

## 3.2 CAP Theorem in Redis

Redis 在分散式系統中通常被歸類為 **CP** 或 **AP** 的混合體，具體取決於配置，但預設偏向 **AP (Availability & Partition Tolerance)** 帶有最終一致性，但在 Cluster 模式下發生網路分區（Network Partition）時，少數派分區（Minority Partition）將無法寫入，表現出 CP 特徵。

Redis is often categorized as a hybrid of **CP** or **AP** in distributed systems, depending on configuration. By default, it leans towards **AP (Availability & Partition Tolerance)** with eventual consistency. However, in Cluster mode during a Network Partition, the minority partition becomes unwritable, exhibiting CP characteristics.

*   **Asynchronous Replication**: 預設情況下，Master 回覆 Client "OK" 後，才非同步地將資料傳給 Replica。
    *   *Risk*: 如果 Master 在傳輸給 Replica 前崩潰，資料永久遺失。
*   **Asynchronous Replication**: By default, the Master acknowledges "OK" to the Client *before* asynchronously sending data to Replicas.
    *   *Risk*: If the Master crashes before transmitting to Replicas, data is permanently lost.

## 3.3 Client-Side Complexity

使用 Redis Cluster 時，Client 端的複雜度會增加。Client 不能再假設連線到任意節點都能處理所有 Key。

When using Redis Cluster, client-side complexity increases. The Client can no longer assume that connecting to any node allows processing of all Keys.

*   **Smart Clients (e.g., Jedis, Lettuce, Go-redis)**: 這些 Library 會快取 Slot-to-Node 的映射表（Slot Map）。
*   **Redirection**: 當 Client 請求錯誤的節點，Redis 會回傳 `MOVED` 錯誤，Client 需更新映射表並重試。
*   **Smart Clients (e.g., Jedis, Lettuce, Go-redis)**: These libraries cache the Slot-to-Node mapping table (Slot Map).
*   **Redirection**: When a Client requests the wrong node, Redis returns a `MOVED` error, and the Client must update its map and retry.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 處理 Cluster 重導向 (Handling Cluster Redirection)

讓我們看看當 Client 存取 Cluster 時，底層發生了什麼事。這對於理解延遲（Latency）抖動至關重要。

Let's look at what happens under the hood when a Client accesses a Cluster. This is crucial for understanding latency jitter.

### Scenario: Key Access with `MOVED`

假設 Cluster 有 3 個節點：
Assume a Cluster with 3 nodes:
*   Node A (Slots 0-5500)
*   Node B (Slots 5501-11000)
*   Node C (Slots 11001-16383)

**Step 1: Client sends command**
Client (沒有快取或快取過期) 發送 `SET user:100 "data"` 給 **Node A**。
Client (with no cache or stale cache) sends `SET user:100 "data"` to **Node A**.

**Step 2: Hash Calculation**
Node A 計算 `CRC16("user:100") % 16384`。假設結果是 **12500**。
Node A calculates `CRC16("user:100") % 16384`. Assume the result is **12500**.

**Step 3: Check Slot Ownership**
Node A 發現 Slot 12500 屬於 **Node C**。
Node A sees that Slot 12500 belongs to **Node C**.

**Step 4: MOVED Error**
Node A 回傳錯誤：`-MOVED 12500 192.168.1.3:6379`。
Node A returns error: `-MOVED 12500 192.168.1.3:6379`.

**Step 5: Client Redirect**
Client 解析錯誤，更新內部的 Slot Map (Slot 12500 -> Node C)，然後重新發送命令給 **Node C**。
The Client parses the error, updates its internal Slot Map (Slot 12500 -> Node C), and resends the command to **Node C**.

> **Note**: `ASK` 錯誤與 `MOVED` 不同。`ASK` 發生在 **Resharding（資料遷移）** 過程中。它告訴 Client：「這個 Slot 正在遷移，請**只針對這一次請求**去詢問目標節點，不要更新你的 Slot Map」。
>
> **Note**: The `ASK` error differs from `MOVED`. `ASK` occurs during **Resharding (data migration)**. It tells the Client: "This slot is migrating; please ask the target node **only for this specific request**, but do not update your Slot Map permanently."

## 4.2 Mitigating Data Loss (Configuration Example)

雖然 Redis 不保證強一致性，但我們可以透過配置來降低資料遺失風險。

Although Redis does not guarantee strong consistency, we can mitigate data loss risks through configuration.

```conf
# redis.conf

# 要求至少有 1 個 Replica 寫入成功，Master 才會接受寫入
# Require at least 1 Replica to successfully acknowledge write for Master to accept writes
min-replicas-to-write 1

# Replica 的延遲不能超過 10 秒
# Replica lag must not exceed 10 seconds
min-replicas-max-lag 10
```

**Trade-off**: 如果活躍的 Replica 數量少於 1，Master 將停止接受寫入（變為 Read-only）。這犧牲了可用性（Availability）來換取資料安全性（Consistency）。

**Trade-off**: If the number of active Replicas drops below 1, the Master stops accepting writes (becomes Read-only). This sacrifices Availability for Data Safety (Consistency).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Multi-Key Operations in Cluster
*   **Anti-pattern**: 在 Cluster 模式下直接使用 `MGET key1 key2` 或涉及多個 Key 的 Lua Script。
*   **Issue**: 如果 `key1` 和 `key2` 位於不同的 Slot（且該 Slot 在不同節點），操作會失敗（Cross-slot error）。
*   **Solution**: 使用 **Hash Tags**。例如 `MGET {user:100}.name {user:100}.email`。Redis 只會根據 `{...}` 內的字串計算 Hash，確保它們落在同一個 Slot。
*   **Anti-pattern**: Using `MGET key1 key2` or Lua Scripts involving multiple keys directly in Cluster mode.
*   **Issue**: If `key1` and `key2` reside in different Slots (and those Slots are on different nodes), the operation fails (Cross-slot error).
*   **Solution**: Use **Hash Tags**. E.g., `MGET {user:100}.name {user:100}.email`. Redis only calculates the hash based on the string inside `{...}`, ensuring they land in the same Slot.

## 5.2 Ignoring Client Topology Refresh
*   **Anti-pattern**: 使用不支援 Cluster 的 Client，或關閉了自動拓撲更新功能。
*   **Issue**: 當 Cluster 發生 Failover 或擴容（Scale out）時，Client 持續請求舊節點，導致大量錯誤與延遲。
*   **Solution**: 確保 Client 開啟 `enablePeriodicRefresh` 或 `enableAdaptiveRefreshTriggeredByMoved`（具體參數視 Library 而定）。
*   **Anti-pattern**: Using a non-Cluster-aware Client or disabling automatic topology refresh.
*   **Issue**: When Cluster Failover or Scale-out occurs, the Client keeps requesting old nodes, causing massive errors and latency.
*   **Solution**: Ensure the Client has `enablePeriodicRefresh` or `enableAdaptiveRefreshTriggeredByMoved` enabled (parameters vary by Library).

## 5.3 Hot Shard (Hot Slot) Problem
*   **Anti-pattern**: 設計 Key 時未考慮分佈均勻性，導致某個 Slot 承載了極端巨大的流量（例如將所有使用者的 Global Counter 放在同一個 Key）。
*   **Issue**: 即使你有 100 個節點，效能瓶頸仍卡在那個 Hot Key 所在的單一節點上。
*   **Solution**: 避免 Big Keys；對於高頻存取的 Key 進行應用層拆分（Sharding at Application Level）。
*   **Anti-pattern**: Designing Keys without considering distribution uniformity, causing a specific Slot to bear extreme traffic (e.g., putting a Global Counter for all users in one Key).
*   **Issue**: Even with 100 nodes, the performance bottleneck remains on the single node holding that Hot Key.
*   **Solution**: Avoid Big Keys; perform application-level sharding for high-frequency access Keys.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: Redis Cluster 為什麼固定是 16384 個 Slots？
**Why does Redis Cluster use fixed 16384 Slots?**

*   **Key Points**:
    *   **Message Size**: Redis 節點間透過 Gossip 協議交換資訊（Ping/Pong）。Slot 的 bitmap 會包含在 Header 中。16384 bits = 2KB，這是一個在頻寬與細粒度之間的折衷。如果是 65536 個 Slots，Header 會太大，浪費頻寬。
    *   **CRC16**: CRC16 演算法產生的雜湊值是 16bit (65536)，但作者認為 16384 對於最大 1000 個節點的 Cluster 來說已經足夠平衡負載。
    *   **Message Size**: Redis nodes exchange info via Gossip protocol (Ping/Pong). The Slot bitmap is included in the Header. 16384 bits = 2KB, a trade-off between bandwidth and granularity. If it were 65536 Slots, the Header would be too large, wasting bandwidth.
    *   **CRC16**: The CRC16 algorithm produces a 16-bit hash (65536), but the author deemed 16384 sufficient for load balancing a Cluster of up to 1000 nodes.

## Q2: 發生 Network Partition 時，Redis Cluster 如何運作？
**How does Redis Cluster behave during a Network Partition?**

*   **Key Points**:
    *   **Majority Side**: 如果分區擁有「過半數的主節點（Majority of Masters）」，且每個 Slot 都有可用的節點，Cluster 經過短暫的 Failover 後可恢復服務。
    *   **Minority Side**: 少數派分區的節點會檢測到自己無法聯繫多數派，會停止接受寫入（防止腦裂 Split Brain 導致的資料不一致）。
    *   **Majority Side**: If the partition holds the "Majority of Masters" and every Slot has an available node, the Cluster resumes service after a brief Failover.
    *   **Minority Side**: Nodes in the minority partition detect they cannot contact the majority and stop accepting writes (to prevent data inconsistency caused by Split Brain).

## Q3: 什麼是 Redis 的腦裂（Split Brain）？如何預防？
**What is Redis Split Brain? How to prevent it?**

*   **Key Points**:
    *   **Scenario**: Sentinel/Cluster 認為 Master A 掛了，選出 Master B。但實際上 Master A 只是網路卡頓，Client 仍連著 Master A 寫入資料。當網路恢復，Master A 被降級為 Replica，這段時間寫入 Master A 的資料會被 Master B 的新資料覆蓋（遺失）。
    *   **Prevention**: 設定 `min-replicas-to-write 1`。當 Master A 發現自己連不上 Replica（Ack 逾時），就會拒絕寫入，從而減少資料遺失的窗口。
    *   **Scenario**: Sentinel/Cluster thinks Master A is down and elects Master B. However, Master A is just lagging network-wise, and Clients are still writing to Master A. When the network recovers, Master A is demoted to Replica, and data written to Master A during this time is overwritten (lost) by Master B's new data.
    *   **Prevention**: Set `min-replicas-to-write 1`. When Master A detects it cannot connect to Replicas (Ack timeout), it refuses writes, reducing the data loss window.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## Key Takeaways
1.  **Replication is Async**: Redis 預設不保證強一致性，故障轉移可能導致資料遺失。
2.  **Sentinel vs. Cluster**: Sentinel 用於高可用（HA），Cluster 用於高可用 + 分片（Sharding）。
3.  **Hash Slots (16384)**: Cluster 資料分佈的核心，Client 需處理 `MOVED` 重導向。
4.  **Hash Tags `{...}`**: 強制多個 Key 落在同一個 Slot 的唯一方法，是實現 Multi-key 操作的關鍵。
5.  **CAP Trade-off**: 透過 `min-replicas-to-write` 可以在 AP 與 CP 之間進行微調。

## Next Steps
*   **Persistence (Chapter 05)**: 既然知道記憶體內的資料可能遺失，下一章將深入探討 **RDB** 與 **AOF** 的持久化機制，以及如何在效能與資料耐久性（Durability）之間做取捨。
*   **Persistence (Chapter 05)**: Now that we know in-memory data can be lost, the next chapter delves into **RDB** and **AOF** persistence mechanisms, and how to trade off between performance and data durability.