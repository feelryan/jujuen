# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Apache Kafka 的價值不僅在於寫出 Producer/Consumer 程式碼，更在於如何確保其在生產環境下的高可用性（High Availability）、資料耐久性（Durability）與效能穩定性。本章節將焦點從「開發」轉向「維運與架構治理」。

For senior engineers, the value of Apache Kafka lies not just in writing Producer/Consumer code, but in ensuring High Availability, Durability, and Performance Stability in a production environment. This chapter shifts the focus from "Development" to "Operations and Architectural Governance."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精準解讀關鍵指標**：區分雜訊與訊號，針對 Consumer Lag 與 Under-replicated Partitions (URP) 設定合理的警報閾值與自動化回應策略。
    **Interpret key metrics accurately**: Distinguish noise from signals, and set reasonable alert thresholds and automated response strategies for Consumer Lag and Under-replicated Partitions (URP).
2.  **執行容量規劃 (Capacity Planning)**：根據吞吐量（Throughput）、保留策略（Retention）與副本數（Replication Factor），科學地計算所需的 Broker 數量、磁碟大小與網路頻寬。
    **Execute Capacity Planning**: Scientifically calculate the required number of Brokers, disk size, and network bandwidth based on Throughput, Retention policies, and Replication Factor.
3.  **設計跨資料中心架構**：理解 MirrorMaker 2 (MM2) 的工作原理，並能設計 Active-Passive 或 Active-Active 的災難復原（DR）方案。
    **Design multi-datacenter architectures**: Understand how MirrorMaker 2 (MM2) works and design Active-Passive or Active-Active Disaster Recovery (DR) solutions.
4.  **掌握 KRaft 遷移路徑**：理解移除 ZooKeeper (ZK) 的架構優勢，並評估從 ZK 模式遷移至 KRaft 模式的策略與風險。
    **Master the KRaft migration path**: Understand the architectural benefits of removing ZooKeeper (ZK) and evaluate strategies and risks for migrating from ZK mode to KRaft mode.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在深入操作之前，我們需要建立幾個關於 Kafka 維運的核心心智模型。
Before diving into operations, we need to establish a few core mental models regarding Kafka maintenance.

### 2.1 健康指標金字塔 (The Health Metrics Pyramid)

不要監控所有數據，應專注於三個層次：
Do not monitor everything; focus on three layers:

1.  **頂層 (SLA/SLO 破壞者)**：**Consumer Lag**（消費延遲）與 **Request Latency**。這是直接影響業務即時性的指標。
    **Top Layer (SLA/SLO Breakers)**: **Consumer Lag** and **Request Latency**. These are metrics that directly impact business real-time requirements.
2.  **中層 (叢集穩定性)**：**Under-replicated Partitions (URP)**。這是 Kafka 最重要的健康指標。如果 URP > 0，代表叢集處於「降級」狀態，資料冗餘不足，隨時可能遺失資料。
    **Middle Layer (Cluster Stability)**: **Under-replicated Partitions (URP)**. This is the single most important health metric for Kafka. If URP > 0, the cluster is in a "degraded" state, lacking data redundancy, and data loss is a risk.
3.  **底層 (資源飽和度)**：Disk Usage, Network Throughput, CPU (Network Processor/Request Handler Idle %)。
    **Bottom Layer (Resource Saturation)**: Disk Usage, Network Throughput, CPU (Network Processor/Request Handler Idle %).

### 2.2 控制平面演進：ZooKeeper vs. KRaft (Control Plane Evolution)

*   **ZooKeeper Mode**: Kafka 依賴外部系統 (ZK) 來管理 Metadata。這導致了「雙重共識系統」（Two Consensus Systems）的問題，限制了 Partition 的數量上限（通常單一叢集建議 < 200k partitions），且 Controller Failover 較慢。
    **ZooKeeper Mode**: Kafka relies on an external system (ZK) to manage metadata. This creates a "Two Consensus Systems" problem, limiting the maximum number of partitions (usually < 200k per cluster recommended) and causing slower Controller Failover.
*   **KRaft Mode (Kafka Raft)**: Kafka 內建 Raft 共識演算法。Metadata 被視為一個特殊的 Log Topic (`__cluster_metadata`)。這使得 Metadata 的傳播更有效率，Controller Failover 幾乎是瞬間完成，並支援百萬級別的 Partitions。
    **KRaft Mode (Kafka Raft)**: Kafka embeds the Raft consensus algorithm. Metadata is treated as a special Log Topic (`__cluster_metadata`). This makes metadata propagation more efficient, enables near-instant Controller Failover, and supports millions of partitions.

### 2.3 跨叢集複製 (Cross-Cluster Replication)

將 MirrorMaker 2 視為一個特殊的 **Consumer + Producer** 組合。它從來源叢集讀取，寫入目標叢集，並負責同步 Consumer Offsets 與 ACLs。
Think of MirrorMaker 2 as a specialized **Consumer + Producer** combo. It reads from the source cluster, writes to the target cluster, and is responsible for syncing Consumer Offsets and ACLs.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design 面試或架構規劃中，Kafka 的維運屬性決定了系統的可靠性上限。
In System Design interviews or architectural planning, Kafka's operational attributes determine the system's reliability ceiling.

### 3.1 容量規劃與成本模型 (Capacity Planning & Cost Model)

在設計階段，你必須回答：「我們需要多大的 Kafka？」
During the design phase, you must answer: "How big of a Kafka cluster do we need?"

*   **網路頻寬 (Network Bandwidth)**：通常是第一個瓶頸。
    *   計算公式：`Inbound = Write Throughput * Replication Factor`。
    *   `Outbound = Write Throughput * Number of Consumers`。
    *   *Insight*: 許多雲端供應商對跨 AZ (Availability Zone) 流量收費。Kafka 的高可用性依賴跨 AZ 複製，這是一筆隱形成本。
*   **磁碟空間 (Disk Space)**：
    *   計算公式：`Daily Retention = Daily Ingest * Replication Factor`。
    *   *Insight*: 預留 20-30% 的緩衝空間給 Log Compaction 和重平衡（Rebalancing）期間的數據移動。

*   **Network Bandwidth**: Usually the first bottleneck.
    *   Formula: `Inbound = Write Throughput * Replication Factor`.
    *   `Outbound = Write Throughput * Number of Consumers`.
    *   *Insight*: Many cloud providers charge for cross-AZ (Availability Zone) traffic. Kafka's HA relies on cross-AZ replication, representing a hidden cost.
*   **Disk Space**:
    *   Formula: `Daily Retention = Daily Ingest * Replication Factor`.
    *   *Insight*: Reserve 20-30% buffer space for Log Compaction and data movement during rebalancing.

### 3.2 災難復原架構 (Disaster Recovery Architecture)

在金融或關鍵業務場景，單一 Region 的 Kafka 是不夠的。
In financial or mission-critical scenarios, a single-region Kafka is insufficient.

*   **Active-Passive (Hot-Standby)**:
    *   Producer 寫入主要叢集 (Main)。
    *   MirrorMaker 2 單向複製到備援叢集 (DR)。
    *   Consumer 平時讀取 Main，災難發生時切換至 DR。
    *   *挑戰*：Offset Translation。Main 和 DR 的 offset 數值不同，必須依賴 MM2 的 `RemoteClusterUtils` 或基於時間戳 (Timestamp) 的重置。
*   **Active-Active (Geo-Replication)**:
    *   兩個叢集雙向複製。
    *   *挑戰*：避免循環複製 (Infinite Loops)。MM2 透過在 Header 中加入標記來解決此問題，但在設計 Topic 命名規範時仍需小心（如 `us-east.topicA`, `eu-west.topicA`）。

*   **Active-Passive (Hot-Standby)**:
    *   Producers write to the Main cluster.
    *   MirrorMaker 2 replicates one-way to the DR cluster.
    *   Consumers read from Main normally, switching to DR during a disaster.
    *   *Challenge*: Offset Translation. Offsets differ between Main and DR; reliance on MM2's `RemoteClusterUtils` or timestamp-based reset is required.
*   **Active-Active (Geo-Replication)**:
    *   Bi-directional replication between two clusters.
    *   *Challenge*: Avoiding infinite loops. MM2 solves this by adding tags in Headers, but care is still needed in Topic naming conventions (e.g., `us-east.topicA`, `eu-west.topicA`).

---

# 4. 逐步示例 (Walkthrough / Example)

### 場景：排查生產環境 Consumer Lag 飆升
### Scenario: Troubleshooting Spiking Consumer Lag in Production

**背景 (Context)**:
你的監控系統發出警報：某個核心付款服務的 Consumer Lag 在過去 10 分鐘內從 0 飆升至 500,000。
Your monitoring system triggers an alert: Consumer Lag for a core payment service has spiked from 0 to 500,000 in the last 10 minutes.

#### 步驟 1：確認問題來源 (Identify the Source)
是 Producer 變快了，還是 Consumer 變慢了？
Is the Producer faster, or is the Consumer slower?

*   檢查 **Incoming Byte Rate** (Producer)。如果暴增，這是流量高峰（Scaling issue）。
*   檢查 **Consumer Group Metrics**。如果 Input 正常但 Lag 增加，則是 Consumer 問題。

*   Check **Incoming Byte Rate** (Producer). If it surged, this is a traffic spike (Scaling issue).
*   Check **Consumer Group Metrics**. If Input is normal but Lag is increasing, it's a Consumer issue.

#### 步驟 2：深入 Consumer 分析 (Deep Dive into Consumer)
假設 Producer 流量正常。我們懷疑 Consumer 處理變慢。
Assume Producer traffic is normal. We suspect the Consumer processing has slowed down.

*   **Rebalancing Storm**: 檢查 log 是否有頻繁的 "Rebalancing"。
    *   *原因*：某個 Consumer 實例崩潰或處理超時 (`max.poll.interval.ms`)，導致 Group Coordinator 不斷踢出成員並觸發重平衡，期間無法消費。
*   **Processing Latency**: 檢查單條訊息處理時間。
    *   *原因*：下游資料庫鎖死、外部 API 延遲增加。

*   **Rebalancing Storm**: Check logs for frequent "Rebalancing".
    *   *Cause*: A Consumer instance crashed or timed out (`max.poll.interval.ms`), causing the Group Coordinator to repeatedly kick members and trigger rebalances, stopping consumption during the process.
*   **Processing Latency**: Check single message processing time.
    *   *Cause*: Downstream database locks, increased external API latency.

#### 步驟 3：解決方案 (Solution)

**短期修復 (Short-term Fix)**:
如果下游 DB 正常，但 Consumer 處理不過來：
If the downstream DB is fine but Consumers can't keep up:

1.  增加 Consumer Instance 數量（直到等於 Partition 數量）。
    Increase Consumer Instances (up to the number of Partitions).
2.  若已達上限，暫時調整 Consumer 設定以減少每次 Poll 的負擔，避免 Timeout：
    If capped, temporarily adjust Consumer config to reduce the load per Poll and avoid Timeouts:

```properties
# 減少每次拉取的最大記錄數，讓 Consumer 有更多時間處理
# Reduce max records per poll to give Consumer more time to process
max.poll.records=100

# 增加處理超時時間，避免被誤判為死亡
# Increase processing timeout to avoid being falsely marked as dead
max.poll.interval.ms=600000 
```

**長期優化 (Long-term Optimization)**:
如果單一 Partition 的量太大，Consumer 已經跟不上，需要增加 Parallelism。
If the volume per Partition is too high and the Consumer can't keep up, Parallelism must be increased.

*   **Parallel Consumer Pattern**: 在 Consumer 內部使用 Thread Pool 處理訊息（需注意 Offset 提交順序）。
*   **擴充 Partitions**: 增加 Topic Partition 數量（注意：這會破壞 Key-ordering，除非重新 Hash 既有數據）。

*   **Parallel Consumer Pattern**: Use a Thread Pool inside the Consumer to process messages (careful with Offset commit order).
*   **Expand Partitions**: Increase the number of Topic Partitions (Note: This breaks Key-ordering unless existing data is re-hashed).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 忽略 Under-replicated Partitions (URP)
### 5.1 Ignoring Under-replicated Partitions (URP)

*   **錯誤 (Pitfall)**：將 URP 視為「警告」而非「緊急」。
    Treating URP as a "Warning" instead of "Critical".
*   **後果 (Consequence)**：當 URP > 0 時，意味著至少有一個 Replica 落後或離線。如果此時 Leader Broker 發生故障，且 `min.insync.replicas` 設定嚴格，Producer 將無法寫入（Availability loss）；若設定寬鬆，則可能發生資料遺失（Data loss）。
    When URP > 0, at least one Replica is lagging or offline. If the Leader Broker fails now, and `min.insync.replicas` is strict, Producers cannot write (Availability loss); if loose, Data loss may occur.
*   **修正 (Fix)**：URP 警報應直接發送至 PagerDuty/On-call 手機。排查通常涉及 Disk I/O 瓶頸或網路問題。
    URP alerts should go straight to PagerDuty/On-call. Troubleshooting usually involves Disk I/O bottlenecks or network issues.

### 5.2 預設的 Log Retention 設定
### 5.2 Default Log Retention Settings

*   **錯誤 (Pitfall)**：使用預設的 `log.retention.hours=168` (7天) 而未計算磁碟容量。
    Using the default `log.retention.hours=168` (7 days) without calculating disk capacity.
*   **後果 (Consequence)**：當流量突增時，磁碟被撐爆，Broker 崩潰，導致級聯效應 (Cascading Failure)。
    When traffic spikes, disks fill up, Brokers crash, leading to Cascading Failure.
*   **修正 (Fix)**：根據磁碟大小設定 `log.retention.bytes` 作為硬限制，時間限制僅作為次要條件。
    Set `log.retention.bytes` based on disk size as a hard limit, using time limits only as a secondary condition.

### 5.3 濫用 Partitions (Over-partitioning)
### 5.3 Over-partitioning

*   **錯誤 (Pitfall)**：為了「未來的擴充性」創建了數千個 Partition 的 Topic，或在 ZK 模式下單一叢集擁有超過 20 萬個 Partitions。
    Creating Topics with thousands of partitions for "future scalability," or having >200k partitions in a single ZK-mode cluster.
*   **後果 (Consequence)**：
    1.  **高延遲**：Replication 需要更多的線程與資源。
    2.  **慢速復原**：Broker 重啟時，Controller 需要加載大量 Metadata，導致長時間不可用。
*   **Consequence**:
    1.  **High Latency**: Replication requires more threads and resources.
    2.  **Slow Recovery**: Upon Broker restart, the Controller needs to load massive metadata, causing prolonged unavailability.
*   **修正 (Fix)**：每個 Broker 的 Partition 數建議控制在 2,000–4,000 以內（ZK 模式）。KRaft 模式下可適度放寬，但仍需謹慎。
    Limit partitions per Broker to 2,000–4,000 (ZK mode). KRaft mode allows more, but caution is still advised.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何設計 Kafka 叢集的容量規劃？如果流量預計翻倍，你會怎麼做？
### Q1: How do you approach Capacity Planning for a Kafka cluster? If traffic is expected to double, what would you do?

*   **高分回答要點 (Key Points)**：
    *   **維度拆解**：不只看儲存 (Storage)，更要看吞吐 (Throughput - Network/IOPS)。
    *   **瓶頸識別**：指出網路頻寬通常是第一個瓶頸（特別是跨 AZ 複製時）。
    *   **擴展策略**：
        *   **Vertical Scaling (Scale Up)**：升級 Disk IOPS 或網卡（容易但有上限）。
        *   **Horizontal Scaling (Scale Out)**：增加 Broker。
    *   **Reassignment**: 強調增加 Broker 後，必須執行 **Partition Reassignment** 才能將負載分攤到新機器上（這是面試官常挖的坑，很多候選人以為加機器會自動平衡）。
    *   **Reassignment**: Emphasize that after adding Brokers, **Partition Reassignment** must be executed to distribute load to new machines (a common trap; many candidates think adding machines automatically balances load).

### Q2: 解釋 Kafka 的 "Unclean Leader Election" 及其權衡。
### Q2: Explain Kafka's "Unclean Leader Election" and its trade-offs.

*   **高分回答要點 (Key Points)**：
    *   **定義**：當 Leader 掛掉，且 ISR (In-Sync Replicas) 中沒有存活副本時，是否允許一個「非同步（落後）」的副本成為 Leader。
    *   **權衡 (The Trade-off)**：這是經典的 CAP 定理應用 (Availability vs. Consistency)。
        *   `unclean.leader.election.enable=true`：優先保證可用性 (Availability)，但會遺失數據 (Data Loss)。
        *   `unclean.leader.election.enable=false` (Default)：優先保證一致性 (Consistency)，但 Partition 會離線直到原 Leader 恢復。
    *   **實務建議**：支付/帳務系統選 `false`，日誌/點擊流系統可考慮 `true`。

### Q3: 為什麼 Kafka 要從 ZooKeeper 遷移到 KRaft？這對維運有什麼具體影響？
### Q3: Why is Kafka migrating from ZooKeeper to KRaft? What is the specific operational impact?

*   **高分回答要點 (Key Points)**：
    *   **架構簡化**：單一二進位檔 (Just Kafka)，不再需要維護兩套系統。
    *   **Scalability**：Metadata 儲存在 Log 中而非記憶體/ZK 節點，突破 Partition 數量限制。
    *   **復原速度**：Controller Failover 不需要從 ZK 讀取全量狀態，只需加載最新的 Metadata Log 片段，速度極快。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 重點摘要 (Key Takeaways)
1.  **URP 是王道**：Under-replicated Partitions 是判斷叢集健康與否的首要指標。
2.  **Lag 是訊號**：Consumer Lag 飆升時，先區分是 Producer 暴量還是 Consumer 故障。
3.  **容量規劃需計算**：網路頻寬往往比磁碟空間更早耗盡；擴容後必須手動執行 Partition Reassignment。
4.  **MM2 用於 DR**：MirrorMaker 2 解決了舊版 MM 的許多問題，是實作跨資料中心災難復原的標準工具。
5.  **擁抱 KRaft**：KRaft 移除了 ZK 依賴，提升了 Metadata 處理效能與叢集可擴展性，是未來的標準模式。

### 後續延伸 (Next Steps)
*   **Security**: 學習 Kafka 的安全機制（SASL/SCRAM, mTLS, ACLs）。這通常是生產環境維運的下一大痛點。
*   **Kafka Connect**: 深入研究如何將 Kafka 與外部系統（S3, Elasticsearch, Postgres）無縫整合。
*   **Stream Processing**: 從單純的 Pub/Sub 進階到使用 **Kafka Streams** 或 **Flink** 進行有狀態的即時運算。