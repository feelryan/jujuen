# 生產者實戰：可靠性傳輸與確認機制 / Producer Patterns: Reliability, Acks, and Idempotence

## Mental model｜心智模型

在 Kafka 中，發送訊息並非單純的「射後不理」(Fire-and-forget)，而是一場生產者 (Producer) 與叢集 (Cluster) 之間的**協商 (Negotiation)**。要理解可靠性，必須建立以下兩個核心視角：

### 1. The "Commit" Definition Gap (提交定義的落差)
可靠性的核心在於「什麼時候我們認為訊息算寫入成功了？」。
- **Producer 的視角**：我收到 Broker 的 `ACK` 回應，任務結束。
- **Broker 的視角**：我把資料寫入 Page Cache（尚未 fsync 到硬碟），並複製給了足夠多的 Follower。

**可靠性模型 (Reliability Model)** 是一個滑動桿 (Slider)：
- **左端 (Latency/Throughput)**：只要 Leader 收到就好，甚至不等待回應 (`acks=0/1`)。
- **右端 (Durability)**：必須寫入 Leader 且同步到所有 ISR (In-Sync Replicas) (`acks=all`)。

### 2. The Idempotency Shield (冪等性防護網)
在分散式系統中，網路超時 (Timeout) 是最棘手的狀態——你不知道請求是「沒送到」還是「送到了但回應丟失」。
- **傳統做法**：重試 (Retry) 可能導致重複資料 (Duplicates)。
- **Kafka 冪等性 (Idempotence)**：Producer 會為每條訊息附上 `(ProducerID, SequenceNumber)`。Broker 透過這個標記來識別並丟棄重複的寫入請求，將「至少一次 (At-least-once)」語義自動升級為「精確一次 (Exactly-once) *for a single partition*」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Golden Standard" for Data Integrity (資料完整性黃金配置)
對於金融交易、訂單處理等絕對不能掉資料的場景，請直接套用此模式。這也是 Kafka 3.0+ 預設傾向的配置。

- **Producer Config**:
  - `acks = all` (或 `-1`)：確保 Leader 和 ISR 列表中的所有 Replica 都確認收到。
  - `enable.idempotence = true`：開啟冪等性，自動處理重試造成的重複與順序問題。
  - `retries = Integer.MAX_VALUE`：遇到瞬時錯誤（Transient Errors）時無限重試，直到超時。
  - `max.in.flight.requests.per.connection <= 5`：配合冪等性，確保重試時不會打亂順序。
- **Broker/Topic Config (Critical!)**:
  - `min.insync.replicas = 2` (假設 RF=3)：這是配合 `acks=all` 的關鍵。如果 ISR 數量少於 2，Broker 會拒絕寫入 (`NotEnoughReplicasException`)，而不是默默接受不安全的寫入。

### 2. The "High Throughput" Pattern (高吞吐日誌模式)
適用於應用程式 Log、點擊流 (Clickstream) 等允許極少量資料遺失，但追求極致寫入速度的場景。

- **Producer Config**:
  - `acks = 1`：Leader 寫入記憶體即回傳成功。
  - `compression.type = lz4` or `zstd`：以 CPU 換取網路頻寬與 I/O 效率。
  - `linger.ms = 20` & `batch.size = 32768`：增加批次發送的等待時間與大小，減少網路請求次數。

### 3. Handling Unrecoverable Errors (不可恢復錯誤的處理)
並非所有錯誤都能靠 `retries` 解決（例如 `RecordTooLargeException` 或 Schema 驗證失敗）。
- **Pattern**: 使用 **Callback 機制** 進行死信隊列 (DLQ) 處理。不要在 `send()` 之後直接 `get()` (同步阻塞)，而是在 Callback 中檢查 Exception，將失敗訊息寫入另一個儲存體（如 DB 或專用的 Kafka Error Topic）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Acks=All" False Sense of Security (虛假的安全感)
- **誤區**：設定了 `acks=all` 就以為資料絕對不會掉。
- **真相**：如果 Topic 的 `min.insync.replicas` 預設為 1 (舊版預設)，當 Leader 是唯一的 ISR 時，`acks=all` 等同於 `acks=1`。一旦這台 Leader 當機，資料即遺失。
- **修正**：`acks=all` 必須搭配 `min.insync.replicas >= 2` 使用。

### 2. Disabling Idempotence for "Performance" (為了效能關閉冪等性)
- **誤區**：認為 `enable.idempotence=true` 會大幅降低效能。
- **真相**：在現代 Kafka 版本中，冪等性的效能開銷微乎其微。關閉它反而需要你在應用層處理複雜的去重邏輯。除非你有極端特殊的理由，否則**永遠保持開啟**。

### 3. Misunderstanding `retries` vs. `delivery.timeout.ms`
- **誤區**：設定 `retries=3`。
- **真相**：在現代 Kafka Producer 中，`retries` 次數通常設為無限大，我們更傾向控制 `delivery.timeout.ms` (預設 2 分鐘)。這表示「在 2 分鐘內盡力重試」，比單純設定次數更能應對長時間的網路抖動。

### 4. Blocking the Producer (阻塞生產者)
- **誤區**：`producer.send(record).get()`。
- **後果**：將非同步的 Kafka 強制變為同步，吞吐量會暴跌 100 倍以上。僅在除錯或極低頻率的關鍵設定發送時使用。

---

## Checklists & workflows｜檢查清單與流程

### Reliability Configuration Checklist (可靠性配置檢查表)

在部署到生產環境前，請確認以下設定：

- [ ] **Acks 設定**：業務是否容許資料遺失？
    - 不能遺失 $\rightarrow$ `acks=all`
    - 可容忍少量 $\rightarrow$ `acks=1`
- [ ] **Broker 配合**：若 `acks=all`，Topic 的 `min.insync.replicas` 是否設為 `2` (針對 RF=3)？
- [ ] **冪等性**：`enable.idempotence` 是否為 `true`？
- [ ] **重試策略**：`delivery.timeout.ms` 是否足以覆蓋一次 Leader Election 的時間（通常建議 > 30s）？
- [ ] **順序性**：若需要保序，`max.in.flight.requests.per.connection` 是否 $\le 5$ (開啟冪等性時) 或 $= 1$ (未開啟時)？

### Producer Error Handling Workflow (錯誤處理決策樹)

當 `Callback` 收到 Exception 時：

1. **是 Retriable Exception?** (如 `NetworkException`, `NotEnoughReplicas`)
   - *Action*: 通常 Producer 會自動重試。如果到了 Callback 階段通常代表 `delivery.timeout.ms` 已耗盡。
   - *Decision*: 記錄 Log $\rightarrow$ 寫入 Local Backup/DLQ $\rightarrow$ Alert。
2. **是 Data/Config Exception?** (如 `RecordTooLarge`, `SerializationException`)
   - *Action*: 重試無效。
   - *Decision*: 立即移入 Dead Letter Queue (DLQ) $\rightarrow$ 修正程式或資料 $\rightarrow$ 重新發送。

---

## Real-world examples｜實戰案例

### Example 1: The "Financial Grade" Producer (Java)
這是一個標準的、高可靠性的生產者配置片段。

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092,broker2:9092");

// Reliability Settings
props.put(ProducerConfig.ACKS_CONFIG, "all"); // Wait for all ISR
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true"); // No dups, ordered
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE); 

// Timeouts
props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000); // 2 mins total budget
props.put(ProducerConfig.LINGER_MS_CONFIG, 5); // Slight delay for better batching

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// Sending with Callback
ProducerRecord<String, String> record = new ProducerRecord<>("payments-topic", orderId, paymentData);

producer.send(record, (metadata, exception) -> {
    if (exception == null) {
        // Success: Update local DB status to 'SENT'
        logger.info("Payment sent. Offset: " + metadata.offset());
    } else {
        // Failure: Critical Alert & DLQ Logic
        logger.error("Data loss risk! Failed to send payment: " + orderId, exception);
        saveToDeadLetterQueue(orderId, paymentData, exception);
    }
});
```

### Example 2: Infrastructure Setup for Reliability
僅設定 Producer 是不夠的，這是對應的 Topic 建立指令（確保 `min.insync.replicas` 生效）：

```bash
# 建立一個高可靠 Topic
# Replication Factor = 3 (3份副本)
# min.insync.replicas = 2 (至少寫入2份才算成功)

kafka-topics.sh --bootstrap-server broker:9092 --create \
  --topic payments-topic \
  --partitions 6 \
  --replication-factor 3 \
  --config min.insync.replicas=2
```

### Example 3: Handling `NotEnoughReplicasException`
當你收到這個錯誤，代表 Cluster 當下的健康 Broker 數量不足以滿足你的可靠性要求。

**情境**：正在進行 OS Patching，同時重啟了 2 台 Brokers (Cluster size = 3, RF = 3, min.insync = 2)。
**現象**：Producer 拋出 `NotEnoughReplicasException`。
**處置**：
1. **短期**：Producer 的 `retries` 機制會持續嘗試，直到 Broker 恢復或超時。
2. **長期**：檢討維運流程，確保 Rolling Restart 每次只重啟一台，且等待 ISR 恢復後再進行下一台。