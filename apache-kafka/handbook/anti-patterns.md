# 反模式：常見架構誤區與陷阱 / Anti-Patterns: Common Architectural Mistakes and Pitfalls

## Mental model｜心智模型

在探討反模式之前，我們必須先校準對 Kafka 的根本認知。許多架構錯誤源於將 Kafka 錯誤地投射為「傳統資料庫 (RDBMS)」或「傳統訊息佇列 (Message Queue, 如 RabbitMQ)」。

### The "Dumb Broker, Smart Consumer" Model
Kafka 的核心設計哲學是 **「笨 Broker，聰明 Consumer」**。
- **並非資料庫**：它是一個 **Commit Log (提交日誌)**。它擅長順序寫入與讀取，但不擅長隨機存取 (Random Access) 或複雜查詢 (Complex Query)。
- **並非傳統 MQ**：它不追蹤「哪條訊息被誰讀過了」的細粒度狀態（這是 Consumer 的責任）。訊息被消費後不會立即消失，而是根據保留策略 (Retention Policy) 決定去留。

**正確的心智模型：**
想像 Kafka 是一條高速傳送帶 (Conveyor Belt) 或水管 (Pipe)，而不是一個歸檔櫃 (Filing Cabinet) 或信箱 (Mailbox)。你的設計必須適應「流動 (Streaming)」與「分區 (Partitioning)」的特性，而不是試圖對抗它。

---

## Patterns & best practices｜常見模式與最佳實務

在避免錯誤之前，先確立什麼是「正確的姿勢」。

### 1. 顯式管理 Topic 與配置 (Explicit Topic Management)
- **Pattern**: 永遠在部署前透過 IaC (Terraform/Ansible) 或管理工具顯式建立 Topic，並針對該 Topic 的用途設定 Partition 數量與 Retention。
- **Why**: 依賴預設值通常會導致災難（例如預設 1 個 Partition 導致效能瓶頸，或預設 7 天保留導致磁碟爆滿）。

### 2. 基於領域事件的設計 (Domain Event Driven)
- **Pattern**: Topic 命名應反映業務領域事件（如 `orders.created`, `payments.succeeded`），而非單純的資料表名稱。
- **Why**: 解耦生產者與消費者，讓下游只需關注發生的「事件」，而非上游的資料庫結構。

### 3. 合理的分區策略 (Sensible Partitioning)
- **Pattern**: 根據吞吐量 (Throughput) 目標計算 Partition 數量。通常建議從較小的數量開始（如 3-6），需要時再擴充。
- **Key Strategy**: 使用具有業務意義的 Key（如 `user_id` 或 `order_id`）來確保順序性 (Ordering)，但要小心資料傾斜 (Data Skew)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

這是本章節的核心，盤點那些讓無數團隊深夜加班的「坑」。

### 1. 把 Kafka 當作長期資料庫 (The "Kafka as a Database" Fallacy)
- **誤區**：將 Retention 設定為 `Infinite`，並試圖透過 Kafka Consumer 從頭掃描來查找特定資料，或者依賴 Kafka 儲存所有歷史資料作為唯一 Source of Truth。
- **後果**：
  - **Replay 惡夢**：當需要重播資料時，時間過長導致無法接受的 RTO (Recovery Time Objective)。
  - **缺乏索引**：Kafka 沒有索引，查找特定資料必須 Full Scan，效率極低。
- **修正**：使用 Tiered Storage 將冷資料卸載到 S3，或將資料同步到 Data Lake/Database 進行查詢。Kafka 僅保留近期的熱資料（例如 3-7 天）。

### 2. 把 Kafka 當作工作佇列 (The "Work Queue" Fallacy)
- **誤區**：試圖用 Kafka 實作類似 RabbitMQ 的功能，例如：
  - 希望某條訊息處理失敗後，僅該條訊息「留在佇列」稍後重試，而其他訊息繼續處理。
  - 依賴 Broker 進行複雜的路由 (Routing)。
- **後果**：
  - **Head-of-Line Blocking**：Kafka 的 Offset 是連續的。如果 Consumer 卡在 Offset 100 處理失敗，它無法跳過 100 去提交 101 的 Offset。這會導致整個 Partition 的處理停滯。
- **修正**：使用 **Dead Letter Queue (DLQ)** 模式。處理失敗的訊息寫入另一個 Topic，主流程繼續往下走。不要試圖在 Consumer 內部無限重試。

### 3. 分區數量過多或過少 (Partition Count Misconfiguration)
- **誤區 A (Too Many)**：在小叢集上建立了數萬個 Partitions。
  - **後果**：Broker 端過多的 open file handles；Leader 選舉時間過長，導致 Broker 重啟時長時間不可用。
- **誤區 B (Too Few)**：高吞吐量 Topic 只有 1 個 Partition。
  - **後果**：並發度 (Concurrency) 被鎖死為 1，無法透過增加 Consumer 實例來提升處理速度。

### 4. 啟用 `auto.create.topics.enable=true` (The Default Config Trap)
- **誤區**：生產環境保留此預設值。
- **後果**：
  - 當工程師打錯 Topic 名稱（如 `oder-events` vs `order-events`）時，Kafka 會默默建立一個新的、通常只有預設 Partition 數量的 Topic。
  - 導致資料流向錯誤的地方，且難以除錯（Consumer 收不到資料，但 Producer 沒報錯）。
- **修正**：在生產環境務必設為 `false`。

### 5. 巨大的單一訊息 (Large Messages)
- **誤區**：試圖透過 Kafka 傳送 10MB+ 的圖片或 PDF 檔案。
- **後果**：
  - 嚴重影響 Broker 吞吐量，增加 GC 壓力，甚至導致 Broker OOM (Out of Memory)。
  - 網路傳輸延遲暴增。
- **修正**：**Claim Check Pattern**。將大檔案上傳至 S3/Blob Storage，僅在 Kafka 訊息中傳遞檔案的 URL (Reference)。

### 6. 忽略 Consumer 的 Rebalance 風暴 (Ignoring Rebalance Storms)
- **誤區**：Consumer 處理邏輯過重，導致 `poll()` 間隔超過 `max.poll.interval.ms`。
- **後果**：Broker 認為 Consumer 已死，觸發 Rebalance。Consumer 完成處理後再次加入，又觸發 Rebalance。系統陷入無限的 Rebalance 迴圈，吞吐量歸零。
- **修正**：優化處理邏輯、減少 `max.poll.records` 或增加 `max.poll.interval.ms`。

---

## Checklists & workflows｜檢查清單與流程

在將新的 Producer/Consumer 或 Topic 推上 Production 之前，請執行此檢查。

### Topic Design Checklist
- [ ] **Retention Policy**: 資料需要保留多久？是基於時間 (Time-based) 還是大小 (Size-based)？是否啟用了 Log Compaction？
- [ ] **Partition Count**: 預估的吞吐量是多少？Partition 數量是否足以支撐未來的擴展（建議至少預留 2 年的成長空間）？
- [ ] **Replication Factor**: 是否至少為 3（以確保高可用性）？`min.insync.replicas` 是否設為 2？
- [ ] **Key Selection**: 是否使用了合適的 Message Key？有無 Hot Partition 風險？

### Producer/Consumer Checklist
- [ ] **Idempotence**: Producer 是否啟用了 `enable.idempotence=true`？
- [ ] **Error Handling**: Consumer 是否實作了 DLQ (Dead Letter Queue) 機制？
- [ ] **Schema Registry**: 是否使用了 Schema Registry (Avro/Protobuf) 來管理資料格式演進？
- [ ] **Blocking Operations**: Consumer 的處理邏輯中是否有外部 API 呼叫？是否有適當的 Timeout 設定以避免 Rebalance？

---

## Real-world examples｜實戰案例

### Case 1: The "Hot Partition" Disaster (熱點分區災難)

**情境**：
一家物聯網 (IoT) 公司收集感測器數據。他們決定使用 `customer_id` 作為 Kafka Message Key，以確保同一個客戶的數據順序。

**問題**：
某個大型企業客戶 (BigCorp) 的設備數量是其他客戶的 1000 倍。
- Partition 0 (負責 BigCorp) 的流入量極大，導致該 Partition 的 Leader Broker CPU 飆高。
- 消費 Partition 0 的 Consumer 處理不及，Lag 持續累積。
- 其他 Partitions 的 Consumers 卻很閒。

**解決方案 (Refactoring)**：
1. **Composite Key**: 改用 `customer_id + sensor_id` 作為 Key。這保留了單一感測器的順序性，但將大客戶的數據打散到不同 Partitions。
2. **Salting (加鹽)**: 如果必須依賴 `customer_id` 全局排序（極少見），則需在 Application Layer 進行 Shuffling，但通常放寬順序要求是更好的選擇。

### Case 2: The "Sync Send" Bottleneck (同步發送瓶頸)

**情境**：
一個訂單系統的開發者為了確保「絕對不掉單」，在 API 處理流程中這樣寫：

```java
// Anti-pattern: Blocking send
Future<RecordMetadata> future = producer.send(record);
RecordMetadata metadata = future.get(); // Waits for ACK
```

**問題**：
這將 Kafka 的非同步高吞吐特性變成了同步阻塞 (Blocking)。API 的 Latency 直接取決於 Kafka 的 Round-trip time。當 Kafka 稍有抖動，API 響應時間暴增，吞吐量極低。

**解決方案**：
使用非同步 Callback 機制，並依賴 `acks=all` 與 `retries` 來保證可靠性，而非在程式碼中阻塞等待。

```java
// Best Practice: Async with Callback
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        // Handle error (log, metric, alert, write to local disk fallback)
        logger.error("Failed to send", exception);
    }
});
```