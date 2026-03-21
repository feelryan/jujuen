# 故障排除：常見事故與災難復原 Checklist / Troubleshooting: Common Incidents and Disaster Recovery

## Mental Model｜心智模型

在對 Apache Kafka 進行故障排除時，不能僅將其視為一個黑盒子佇列。你必須建立 **「流動管道與背壓 (Flow Pipeline & Backpressure)」** 的心智模型。

1.  **管道視角 (The Pipeline View)**：
    問題通常發生在三個階段之一：
    *   **Inflow (Producer)**：水龍頭開太大（流量暴增）或水管接頭漏水（Network/Acks issues）。
    *   **Storage (Broker)**：水槽滿了（Disk Full）、水槽破了（Replica down）或水管堵塞（Request Handler Pool full）。
    *   **Outflow (Consumer)**：排水孔太小（Processing slow）、排水管卡住（Poison Pill/Stuck）或頻繁更換排水管（Rebalancing storm）。

2.  **症狀 vs. 根因 (Symptom vs. Root Cause)**：
    *   **Consumer Lag (消費延遲)** 通常是「發燒」的症狀，而不是病因。病因可能是生產端流量激增（正常業務）、Broker 磁碟 I/O 瓶頸（硬體限制），或是 Consumer 處理邏輯死鎖（程式碼 Bug）。
    *   **Rebalancing (重平衡)** 是 Kafka 的自我修復機制，但頻繁的重平衡（Stop-the-world）則是系統不穩定的訊號。

3.  **災難復原 (DR) 的核心是「RPO 與 RTO」**：
    *   Kafka 的 DR 策略通常依賴 **跨叢集複製 (Cluster Linking / MirrorMaker 2)**。
    *   思考模型：當主叢集 (Primary) 燒毀時，你的備援叢集 (Secondary) 的 Offset 是多少？Consumer 切換過去後會重複消費多少資料？

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Consumer Lag 排查模式 (Lag Investigation Pattern)
當 Lag 發生時，採用 **"Divide and Conquer"** 策略：
*   **確認生產速率 (Check Ingestion Rate)**：如果是 Producer 突然發送大量數據，這是 Capacity Planning 問題，需要擴展 Consumer Group。
*   **確認單一分區延遲 (Check Partition Skew)**：如果只有某幾個 Partition Lag 很高，通常是 **Data Skew (資料傾斜)**，即某個 Key (如熱門 User ID) 集中在特定分區。
*   **確認處理時間 (Check Processing Time)**：如果所有 Partition 都慢，檢查 Consumer 的 GC log、外部 API 呼叫延遲 (Database/HTTP timeouts)。

### 2. 磁碟滿載處理模式 (Disk Full Handling Pattern)
Broker 磁碟滿載是 P0 級事故。
*   **短期緩解 (Short-term)**：
    *   縮短 `log.retention.hours` 或 `log.retention.bytes`（注意：這會刪除舊資料）。
    *   如果有多個 log dir，且分佈不均，可使用工具 (如 `kafka-reassign-partitions`) 將 Partition 移動到其他 Broker。
*   **長期解法 (Long-term)**：啟用 Tiered Storage (分層儲存)，將舊資料卸載到 S3/GCS，讓 Broker 本地只保留熱數據。

### 3. 毒丸訊息處理 (Poison Pill Handling)
當 Consumer 讀到一條無法解析或導致 Crash 的訊息（Poison Pill），會導致無限迴圈（讀取 -> Crash -> 重啟 -> 讀取同一條）。
*   **Pattern**：實作 **Dead Letter Queue (DLQ)**。
*   **實作**：在 `try-catch` 區塊中捕獲不可恢復的錯誤，將該訊息發送到專門的 `error-topic`，並提交 Offset 讓 Consumer 繼續前進。

### 4. 災難復原架構 (Disaster Recovery Architecture)
*   **Active-Passive (主備模式)**：
    *   Primary Cluster 負責讀寫。
    *   使用 MirrorMaker 2 (MM2) 或 Confluent Replicator 單向同步到 Secondary Cluster。
    *   **關鍵點**：Offset Translation (Offset 轉換)。因為 Source 和 Target 的 Offset 可能不同，切換時需依賴 MM2 的 `checkpoint` 機制來重置 Consumer Offset。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 暴力刪除 Log 檔案 (Manually Deleting Log Files)
*   **Anti-pattern**：磁碟滿了，維運人員直接 `rm -rf /var/lib/kafka/data/topic-0/*`。
*   **後果**：Broker 會 Crash，因為 index 檔案與實際資料不一致，重啟後可能導致資料損壞或長時間的 Log Recovery。
*   **正確做法**：調整 Retention Policy 讓 Kafka 自己刪除，或使用 `kafka-delete-records.sh` (Admin API)。

### 2. 盲目增加 Partition (Blindly Increasing Partitions)
*   **Anti-pattern**：遇到效能問題就無腦增加 Partition。
*   **後果**：增加 Partition 會增加 Broker 的檔案控制代碼 (File Descriptors) 消耗，並增加 Leader Election 的時間（降低可用性）。且 Partition 數量 **只能增不能減**。
*   **正確做法**：先確認是否為 Consumer 處理邏輯過慢，能否透過優化程式碼或增加 `max.poll.records` 解決。

### 3. 忽略 `min.insync.replicas` 進行維護 (Ignoring ISR during Maintenance)
*   **Anti-pattern**：在 Rolling Restart 或升級時，沒有監控 ISR (In-Sync Replicas)。
*   **後果**：如果 `min.insync.replicas=2` 且此時只有 2 個 Replica 在線，重啟其中一台會導致 Producer 無法寫入 (`NOT_ENOUGH_REPLICAS`)，造成服務中斷。

### 4. Consumer 的 "Stop-the-World" 重平衡 (Frequent Rebalancing)
*   **Anti-pattern**：Consumer 頻繁加入/退出 Group，導致所有 Consumer 暫停消費等待重分配。
*   **常見原因**：`max.poll.interval.ms` 設太短，處理單批資料超時，被 Coordinator 踢出群組。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 Incident Response: Consumer Lag Spiking (消費延遲激增)

- [ ] **Scope Impact (確認範圍)**：是單一 Consumer Group 落後，還是所有 Group 都慢？(前者是 App 問題，後者是 Cluster 問題)。
- [ ] **Check Producer Rate (檢查生產速率)**：
    - [ ] 檢查 `MessagesInPerSec` 指標。是否有流量尖峰？
- [ ] **Check Consumer Health (檢查消費者健康)**：
    - [ ] Consumer 是否頻繁 Rebalance？(檢查 Log 中的 `RebalanceInProgress` 或 `JoinGroup`)。
    - [ ] 是否有 Error Log？(Deserialization Error, Timeout)。
    - [ ] 檢查 `max.poll.interval.ms` 是否小於批次處理時間？
- [ ] **Check Broker Performance (檢查 Broker 效能)**：
    - [ ] Disk I/O Wait 是否過高？
    - [ ] Network Throughput 是否飽和？
- [ ] **Action (行動)**：
    - [ ] 若是流量尖峰：擴展 Consumer 實例 (直到等於 Partition 數)。
    - [ ] 若是處理過慢：暫時減少 `max.poll.records` 以避免 Timeout。
    - [ ] 若是積壓嚴重需緊急處理：考慮啟動臨時 Consumer Group 只讀取最新資料 (Reset Offset to Latest)，舊資料由另一組 Consumer 慢慢消化 (或捨棄)。

### 💾 Incident Response: Broker Disk Full (磁碟滿載)

- [ ] **Identify Top Topics (找出佔用最大的 Topic)**：
    - [ ] 執行 `du -h --max-depth=1 /var/lib/kafka/data | sort -hr`。
- [ ] **Verify Retention (驗證保留策略)**：
    - [ ] 檢查該 Topic 的 `retention.ms` 和 `retention.bytes`。
- [ ] **Mitigation (緩解措施)**：
    - [ ] **Option A (推薦)**：針對該 Topic 動態下修 Retention：
      `kafka-configs.sh --alter --entity-type topics --entity-name <topic> --add-config retention.ms=3600000` (改為 1 小時)。
    - [ ] **Option B**：擴充 Disk Volume (如果是雲端環境)。
    - [ ] **Option C**：將部分 Partition 搬移到較空的 Broker (`kafka-reassign-partitions.sh`)。

### 🌪 Disaster Recovery: Failover to Secondary Cluster (災難切換)

- [ ] **Decision (決策)**：確認 Primary Cluster 已不可逆地損壞或將長時間停機。
- [ ] **Stop Producers (停止生產者)**：防止資料寫入黑洞或造成 Split-brain。
- [ ] **Verify Sync Status (驗證同步狀態)**：
    - [ ] 檢查 MirrorMaker 2 的 Lag。
- [ ] **Switch Consumers (切換消費者)**：
    - [ ] 停止 Primary 的 Consumers。
    - [ ] 啟動 Secondary 的 Consumers。
    - [ ] **Critical**: 重置 Offset。使用 MM2 的 `checkpoint` topic 或根據時間戳記 (`offsetsForTimes`) 找到對應的 Offset。
- [ ] **Switch Producers (切換生產者)**：
    - [ ] 更新 Producer Config 指向 Secondary Cluster Bootstrap Servers。
    - [ ] 重啟 Producer。

---

## Real-world examples｜實戰案例

### Case 1: The "Hot Partition" Issue (資料傾斜導致的單點延遲)

**情境**：
一個電商系統使用 Kafka 傳輸訂單狀態。某天發現 Consumer Group 的 Lag 總體不高，但處理速度變慢，且某些訂單嚴重延遲。

**排查**：
1.  檢查 Consumer Metrics，發現 `partition-5` 的 Lag 遠高於其他分區。
2.  檢查 Producer 端的 Key 分配策略。發現 Key 使用了 `MerchantID` (商家 ID)。
3.  當天剛好有一位「超級商家」進行大促銷，產生了 80% 的訂單。
4.  因為 Key 相同，所有該商家的訂單都堆積在 `partition-5`，導致負責該分區的 Consumer 處理不完，而其他 Consumer 很閒。

**解決方案**：
*   **短期**：增加負責 `partition-5` 的 Consumer 的資源 (CPU/Memory)。
*   **長期**：更改 Partition Key 策略。例如改用 `OrderID` (隨機性高) 作為 Key，或是使用 `MerchantID + RandomSuffix` (雖然這會犧牲同一商家的全域順序性，但在該場景下只需保證單一訂單的順序性即可)。

### Case 2: The "Zombie" Consumer (Rebalance Storm)

**情境**：
生產環境的 Consumer Group 每隔 5 分鐘就停止消費一次，吞吐量極不穩定。

**排查**：
1.  查看 Broker Log，發現頻繁出現 `Generation matches, but member is not in group`。
2.  查看 Consumer Log，發現處理一批資料 (Batch) 的平均時間約為 4.8 分鐘。
3.  檢查設定：`max.poll.interval.ms` 預設為 5 分鐘 (300000ms)。
4.  **原因**：當某次 DB 寫入稍慢，處理時間超過 5 分鐘，Consumer 沒有在規定時間內呼叫下一次 `poll()`。Coordinator 判定該 Consumer 已死，將其踢出並觸發 Rebalance。
5.  Consumer 完成處理後嘗試提交 Offset，發現自己已被踢出，於是重新加入 Group -> 再次觸發 Rebalance。

**解決方案**：
*   **調優**：減少 `max.poll.records` (例如從 500 降到 100)，確保單批次處理能在 5 分鐘內完成。
*   **設定**：適度增加 `max.poll.interval.ms` (例如改為 10 分鐘)，給予容錯空間。