# 生產維運：監控指標與容量規劃 / Production Operations: Monitoring and Capacity Planning

## Mental model｜心智模型

在維運 Apache Kafka 時，請將叢集視為一個 **「高吞吐量的物流倉儲中心」**，而不僅僅是一條資料管線。

1.  **庫存壓力 (Storage Pressure)**：
    Kafka 是基於磁碟的系統。容量規劃的核心不在於「現在有多少資料」，而在於「進貨速度 (Produce rate) x 保留時間 (Retention) x 副本數 (Replication Factor)」。磁碟填滿是 Kafka 最常見的死因。

2.  **健康指標層級 (Hierarchy of Health)**：
    並非所有指標都同等重要。請建立以下分層思維：
    *   **Level 1 - 叢集存活 (Cluster Liveness)**：`UnderReplicatedPartitions` (URP) 和 `OfflinePartitions`。這代表資料有遺失風險或服務不可用。這是「急診室」等級的指標。
    *   **Level 2 - 服務品質 (Service Quality)**：`Consumer Lag` (消費延遲)。這代表業務邏輯是否跟得上資料產生的速度。這是「門診」等級，通常是應用層問題。
    *   **Level 3 - 基礎設施飽和度 (Infrastructure Saturation)**：CPU, Disk I/O, Network Bandwidth。這是「健檢」等級，用於預測何時需要擴容。

3.  **流動性 (Fluidity)**：
    Kafka 的擴容 (Scaling out) 不是隨插即用的。新增 Broker 就像在倉庫旁蓋了新倉庫，如果沒有搬運工 (Partition Reassignment) 把舊貨物搬過去，新倉庫永遠是空的，舊倉庫依然爆滿。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 關鍵監控指標 (The "Must-Have" Metrics)

不要監控所有 JMX 指標，那會讓你陷入雜訊。專注於以下關鍵訊號：

*   **Cluster Health (叢集健康度)**
    *   `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions`: **目標值為 0**。若 > 0，代表 Follower 跟不上 Leader 或 Broker 當機。
    *   `kafka.controller:type=KafkaController,name=OfflinePartitionsCount`: **必須為 0**。若 > 0，代表該分區完全不可用（無 Leader）。
    *   `kafka.controller:type=KafkaController,name=ActiveControllerCount`: **叢集中必須總和為 1**。若為 0 或 > 1 (腦裂)，叢集將無法運作。

*   **Performance & Throughput (效能與吞吐)**
    *   `kafka.network:type=RequestMetrics,name=TotalTimeMs,request={Produce|FetchConsumer}`: 請求的端到端延遲。
    *   `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec`: 進貨流量（用於容量規劃）。
    *   `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec`: 出貨流量（注意：這通常是 BytesIn 的數倍，取決於消費者數量）。

*   **Consumer Health (消費者健康度)**
    *   `Consumer Lag`: 每個 Partition 的 `LogEndOffset` 減去 `CurrentOffset`。
    *   **Pattern**: 使用 **Burrow** 或 **Kafka Exporter** 監控 Lag，不要只依賴 Consumer 自行回報。關注 **Time Lag** (落後幾秒) 比 Message Lag (落後幾條) 更具業務意義。

### 2. 容量規劃公式 (Capacity Planning Formula)

在採購硬體或設定 Cloud Disk 時，請使用以下公式計算：

*   **磁碟空間 (Disk Space)**:
    $$ \text{Disk Needed} = (\text{Daily Ingestion Rate} \times \text{Retention Days} \times \text{Replication Factor}) \times 1.3 $$
    *   *註：1.3 代表預留 30% 的緩衝空間，用於 Log Compaction 期間的波動或突發流量。*

*   **網路頻寬 (Network Bandwidth)**:
    $$ \text{Network Out} = \text{Ingestion Rate} \times (\text{Replication Factor} - 1 + \text{Number of Consumers}) $$
    *   *註：Kafka 的瓶頸通常先發生在 Network I/O，其次是 Disk I/O，最後才是 CPU。*

### 3. Broker 擴容與資料重平衡 (Scaling & Rebalancing)

*   **Throttle Reassignment**: 在執行 Partition Reassignment (將資料搬移至新 Broker) 時，務必設定頻寬限制 (`--throttle`)。
    *   *原因*：若不限制，Kafka 會試圖用最大頻寬複製資料，導致生產者和消費者的請求被阻塞 (Network Saturation)，引發線上故障。
*   **Topic-Based Strategy**: 不要試圖一次重平衡整個叢集。按 Topic 優先級分批進行。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 忽略 Page Cache 的重要性 (Ignoring Page Cache)
*   **Anti-pattern**: 給 Kafka Broker 分配超大的 JVM Heap (例如 64GB+)，認為這樣效能更好。
*   **Reality**: Kafka 依賴 OS Page Cache 來加速讀寫。Heap 只需要夠用 (通常 6GB-10GB 足矣)，剩下的記憶體應全部留給 OS 做 Page Cache。
*   **Consequence**: Heap 太大導致 GC 停頓過久；Page Cache 太小導致頻繁讀取磁碟，效能低落。

### 2. 只有 Lag 數值，沒有趨勢 (Lag Value without Trend)
*   **Anti-pattern**: 設定警報規則為 "Lag > 10,000 就叫醒我"。
*   **Reality**: 批次處理 (Batch processing) 或重啟應用時，Lag 瞬間飆高是正常的。
*   **Better approach**: 監控 Lag 的**斜率**。如果 Lag 持續增加且沒有下降趨勢，才需要介入。

### 3. 盲目的擴容 (Blind Scaling)
*   **Anti-pattern**: 看到 CPU 飆高或磁碟快滿了，直接加入新的 Broker 節點，然後就以為沒事了。
*   **Pitfall**: 新加入的 Broker 預設是空的，不會自動分擔現有的負載。
*   **Fix**: 必須執行 `kafka-reassign-partitions` 將熱點 Partition 移動到新節點。

### 4. 預設的 Log Retention 設定 (Default Retention)
*   **Anti-pattern**: 使用預設的 `log.retention.hours=168` (7天) 而未根據磁碟大小調整。
*   **Pitfall**: 突發流量可能在幾小時內塞滿磁碟，導致 Broker 當機。
*   **Fix**: 設定 `log.retention.bytes` 作為最後一道防線，確保即使流量暴增，舊資料會先被刪除以保全磁碟空間。

---

## Checklists & workflows｜檢查清單與流程

### Daily/Weekly Health Check (日常健檢)

- [ ] **檢查 URP (Under Replicated Partitions)**：確認數值是否為 0。若不為 0，檢查特定 Broker 的網路或磁碟負載。
- [ ] **檢查磁碟使用率偏斜 (Disk Skew)**：確認是否有單一 Broker 的磁碟使用率遠高於其他節點（這代表 Partition 分配不均）。
- [ ] **檢查 Controller Logs**：搜尋 `ERROR` 或 `WARN`，特別是頻繁的 Leader Election。
- [ ] **驗證 Consumer Lag**：確認關鍵業務 Group 的 Lag 是否在預期 SLA 內。

### SOP: Adding a New Broker (擴容標準作業程序)

1.  **Provision**: 準備新機器，確保 OS 設定 (File Descriptors, Swapiness) 與現有 Broker 一致。
2.  **Install & Configure**: 安裝 Kafka，設定 `broker.id` (新 ID) 與 `zookeeper.connect`。
3.  **Start**: 啟動 Kafka Service。
4.  **Verify**: 檢查 Logs 確認成功加入 Cluster。
5.  **Rebalance (Crucial)**:
    *   產生候選計畫：使用 `kafka-reassign-partitions --generate`。
    *   **審查計畫**：不要盲目套用，移除不需要移動的 Partition 以減少開銷。
    *   執行遷移：使用 `kafka-reassign-partitions --execute` 並加上 `--throttle` (例如 50MB/s)。
6.  **Monitor**: 監控遷移進度與網路頻寬。
7.  **Finalize**: 遷移完成後，移除 throttle 設定 (`--verify`)。

### SOP: Emergency Disk Cleanup (磁碟爆滿緊急處理)

當 Broker 磁碟剩餘空間 < 5% 時：

1.  **Identify**: 找出佔用空間最大的 Topic。
2.  **Shorten Retention**: 動態修改該 Topic 的保留時間（不需重啟 Broker）。
    ```bash
    # 將保留時間暫時改為 12 小時
    kafka-configs --zookeeper <zk> --entity-type topics --entity-name <topic_name> --alter --add-config retention.ms=43200000
    ```
3.  **Wait**: 等待 Log Cleaner 執行刪除 (通常幾分鐘內生效)。
4.  **Restore**: 空間釋放後，逐步恢復原本的 Retention 設定，並規劃擴容。

---

## Real-world examples｜實戰案例

### Case 1: The "Noisy Neighbor" (吵鬧的鄰居)

**情境**：
生產環境中，一個關鍵的支付服務 (Payment Service) 突然出現高延遲 (Latency Spike)。檢查該服務的 Consumer Lag 正在堆積。

**調查**：
1.  查看 Kafka Broker 的 `BytesInPerSec`，發現整體流量暴增。
2.  檢查 `Disk Utilization`，發現 I/O wait 極高。
3.  進一步分析，發現另一個分析團隊剛上線了一個新的 Log Collector，正在瘋狂寫入大量的 Debug Logs 到同一個 Kafka Cluster。

**解決方案**：
*   **短期**：對 Log Collector 的 Topic 設定 Quota (限流)。
    ```bash
    kafka-configs --zookeeper <zk> --entity-type clients --entity-name <client-id> --alter --add-config producer_byte_rate=1048576
    ```
*   **長期**：實施 **物理隔離** 或 **I/O 隔離**。將高吞吐量的 Log 收集與低延遲的交易資料分開至不同的磁碟或 Cluster。

### Case 2: The Rebalance Storm (重平衡風暴)

**情境**：
維運團隊在上班時間進行 Broker 擴容。執行 `kafka-reassign-partitions` 後，整個 Cluster 的回應時間變慢，導致多個 Consumer Group 發生 Rebalance，甚至斷線。

**原因**：
團隊忘記設定 `--throttle`。Kafka 試圖以網卡最大速度複製數 TB 的資料，耗盡了網路頻寬。Follower 無法及時向 Leader 發送 Fetch Request，導致 ISR (In-Sync Replicas) 頻繁變動，觸發 Zookeeper 更新，進而拖慢 Controller。

**教訓**：
永遠在重平衡時設定速限。
`kafka-reassign-partitions --execute --reassignment-json-file move.json --throttle 50000000` (限制為 50MB/s)。

### Case 3: The "Stuck" Consumer (卡住的消費者)

**情境**：
監控儀表板顯示某個 Consumer Group 的 Lag 持續上升，但該服務的 CPU 使用率很低，且沒有 Error Log。

**診斷**：
這不是 Kafka 的問題，而是 Consumer 邏輯問題。
*   檢查 Consumer 的處理邏輯，發現某個特定的 Message 觸發了程式碼中的 Infinite Loop 或極長的 Timeout (例如呼叫外部 API 超時)。
*   因為 Consumer 只有在處理完當前訊息後才會 commit offset 並拉取下一批，所以看起來像是「卡住了」。

**解決方案**：
*   設定合理的 `max.poll.interval.ms`。
*   在 Consumer 邏輯中加入 Circuit Breaker (斷路器) 機制，避免單一訊息卡死整個 Partition 的消費。