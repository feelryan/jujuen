# 傳輸語義：精確一次 (EOS) 與交易機制 / Delivery Semantics: Exactly-Once and Transactions

## Mental model｜心智模型

要掌握 Kafka 的 Exactly-Once Semantics (EOS)，不能只把它想成「訊息只會傳送一次」，更準確的心智模型應該是 **「原子性批次處理 (Atomic Batch Processing)」** 與 **「狀態機同步 (State Machine Synchronization)」**。

### 1. 從「傳遞」轉向「交易」 (From Delivery to Transaction)
在 At-least-once 模型中，Producer 像是在丟球，只要沒聽到 Consumer 喊「接到了」，它就會一直丟。而在 EOS 模型中，你應該將 Producer 與 Consumer 的互動視為資料庫的 **ACID 交易**。
- **原子性 (Atomicity)**：一組訊息的寫入（Output）與來源訊息的 Offset 提交（Input Commit），要嘛全部成功，要嘛全部失敗。
- **隔離性 (Isolation)**：下游的 Consumer 在交易完成（Committed）之前，不應該看到這些「正在處理中」的訊息。

### 2. 兩個層次的保護 (Two Layers of Protection)
理解 EOS 必須區分兩個層級：
1.  **冪等性生產者 (Idempotent Producer)**：
    -   **Scope**：單一 Producer Session、單一 Partition。
    -   **Mental Image**：像是 TCP 的去重機制。Producer 會給每條訊息編號 (Sequence Number)，Broker 發現重複編號直接丟棄。這是 EOS 的基石。
2.  **交易型 API (Transactional API)**：
    -   **Scope**：跨 Partition、跨 Topic、甚至跨「讀取-處理-寫入」流程。
    -   **Mental Image**：像是分散式系統的 Two-Phase Commit (2PC)。Broker 引入了 Transaction Coordinator 來管理標記 (Markers)，決定這批訊息是「可見的」還是「該被忽略的」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Read-Process-Write 模式 (The Read-Process-Write Pattern)
這是 Kafka Transactions 最核心的應用場景（例如 Kafka Streams 的底層實作）。
- **做法**：將「讀取 Input Topic」、「處理資料」、「寫入 Output Topic」以及「提交 Input Offset」綁定在同一個交易中。
- **關鍵點**：必須使用 `producer.sendOffsetsToTransaction()` 來提交 Offset，而不是傳統的 `consumer.commitSync()`。這樣才能確保「訊息產出」與「Offset 更新」同生共死。

### 2. 消費者隔離級別 (Consumer Isolation Level)
僅僅在 Producer 端開啟交易是不夠的，Consumer 必須配合。
- **設定**：`isolation.level = read_committed`。
- **行為**：Consumer 會暫存 (buffer) 尚未 commit 的訊息，直到看到 Broker 發出的 `COMMIT` 標記才會將訊息交給應用程式。如果看到 `ABORT` 標記，則會直接丟棄該批訊息。
- **預設值陷阱**：預設是 `read_uncommitted`，這意味著即使 Producer 回滾了交易，預設 Consumer 還是會讀到那些髒資料 (Dirty Reads)。

### 3. 穩定的 Transactional ID (Stable Transactional ID)
為了在應用程式重啟後能恢復之前的交易狀態，必須指定一個固定的 ID。
- **設定**：`transactional.id = "payment-service-partition-0"`。
- **最佳實務**：通常會結合應用程式的 ID 與 Partition ID 來生成，確保每個實例 (Instance) 都有獨一無二且持久的 ID。這能觸發 Kafka 的 **Zombie Fencing** 機制——當舊的實例殭屍復活時，Broker 會因為偵測到相同的 ID 已經有新的 Producer 連線，而拒絕舊實例的寫入。

### 4. 僅在必要時使用 (Use Sparingly)
- **Trade-off**：EOS 會增加 Latency（因為 Consumer 必須等待交易標記）並降低 Throughput（約 5-20% 的損耗，視批次大小而定）。
- **建議**：對於日誌收集、監控指標等允許少量重複或遺失的場景，使用 At-least-once 即可。將 EOS 保留給金融帳務、庫存扣減等高敏感業務。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤以為 EOS 能解決「外部系統」的副作用 (The "Side-Effect" Fallacy)
- **錯誤觀念**：認為 Kafka Transaction 可以回滾 (Rollback) 所有的操作，包括發送 Email 或寫入 MySQL。
- **現實**：Kafka 只能保證 **Kafka 內部狀態** 的一致性。如果你在交易過程中呼叫了 REST API 發 Email，然後交易失敗 Abort 了，Email 已經發出去了，Kafka 救不了你。
- **解法**：將外部操作移到 Consumer 端，並確保外部系統具備冪等性 (Idempotency)，或者使用 CDC (Change Data Capture) 模式。

### 2. 交易時間過長 (Long-Running Transactions)
- **現象**：在 `beginTransaction` 和 `commitTransaction` 之間進行了耗時的外部 API 呼叫或複雜運算。
- **後果**：
    1.  阻擋下游 Consumer：`read_committed` 的 Consumer 會卡在「第一條未提交訊息」的 Offset，導致後續已提交的訊息也無法讀取（Head-of-line blocking）。
    2.  交易超時：超過 `transaction.timeout.ms`，Coordinator 會強制 Abort 交易。
- **修正**：保持交易範圍小且快。

### 3. 混用 Transactional 與 Non-Transactional Producer
- **風險**：如果多個 Producer 寫入同一個 Topic，有些用交易，有些不用，且 Consumer 設定為 `read_committed`。
- **結果**：Consumer 雖然能正常讀取非交易訊息，但這會讓除錯變得極度複雜。如果非交易 Producer 送出了重複訊息，EOS 的保證就會在該 Topic 上破功（因為 Consumer 還是會讀到那些重複的非交易訊息）。

### 4. 忽略 `__transaction_state` 的可用性
- **風險**：Kafka 使用內部的 `__transaction_state` topic 來儲存交易狀態。如果 Broker 叢集的 `min.insync.replicas` 設定不當，導致這個內部 topic 不可用，所有交易都會失敗。

---

## Checklists & workflows｜檢查清單與流程

### EOS Implementation Checklist

#### Producer Configuration
- [ ] `enable.idempotence` 設為 `true`（Kafka 3.0+ 預設為 true，但顯式設定較保險）。
- [ ] `transactional.id` 已設定，且保證跨重啟後一致（Unique per producer instance）。
- [ ] `acks` 必須設為 `all` (或 `-1`)。
- [ ] `retries` 設為大於 0 的值（建議 `Integer.MAX_VALUE`）。

#### Consumer Configuration
- [ ] `isolation.level` 設為 `read_committed`。
- [ ] `enable.auto.commit` 設為 `false`（必須由 Producer 交易來控制 Offset 提交，或手動精確控制）。

#### Code Logic (Read-Process-Write)
- [ ] 是否在 `try-catch` 區塊中正確處理 `ProducerFencedException`？（這代表有新的實例接手了，當前實例應停止）。
- [ ] 是否使用 `producer.sendOffsetsToTransaction(...)` 而非 `consumer.commitSync()`？
- [ ] 交易範圍內是否包含「不可逆的外部副作用」？（若有，需移除）。

#### Monitoring & Ops
- [ ] 監控 `kafka.producer:type=producer-metrics,name=record-error-rate`。
- [ ] 監控 Transaction Coordinator 的錯誤率。
- [ ] 觀察 Consumer 的 `Last Stable Offset (LSO)` 與 `High Watermark` 的差距（差距過大代表有卡住的長交易）。

---

## Real-world examples｜實戰案例

### 案例：銀行轉帳處理 (Bank Transfer Stream)

假設我們有一個 `transfers-input` topic，需要經過驗證後寫入 `transfers-validated` topic。

#### ❌ 錯誤做法 (At-least-once, 可能導致重複轉帳)

```java
// 傳統做法：可能在 send 成功後，commit 失敗，導致重啟後重複處理
while (true) {
    ConsumerRecords records = consumer.poll(Duration.ofMillis(100));
    for (Record record : records) {
        process(record); // 業務邏輯
        producer.send(new ProducerRecord("transfers-validated", ...));
    }
    consumer.commitSync(); // 如果這裡掛掉，上面的 send 已經出去了，重啟會再送一次
}
```

#### ✅ 正確做法 (Exactly-Once / Transactional)

```java
// 初始化
producer.initTransactions();

while (true) {
    ConsumerRecords records = consumer.poll(Duration.ofMillis(100));
    if (records.isEmpty()) continue;

    try {
        // 1. 開啟交易
        producer.beginTransaction();

        for (ConsumerRecord record : records) {
            // 2. 業務處理與發送訊息
            ValidationResult result = validateTransfer(record.value());
            producer.send(new ProducerRecord("transfers-validated", record.key(), result));
        }

        // 3. 關鍵步驟：將 Input 的 Offset 提交綁定到同一個交易中
        // 計算要提交的 offsets (通常是 current position + 1)
        Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
        for (TopicPartition partition : records.partitions()) {
            List<ConsumerRecord> partitionRecords = records.records(partition);
            long lastOffset = partitionRecords.get(partitionRecords.size() - 1).offset();
            offsetsToCommit.put(partition, new OffsetAndMetadata(lastOffset + 1));
        }

        // 提交 Offset 給 Transaction Coordinator
        producer.sendOffsetsToTransaction(offsetsToCommit, consumer.groupMetadata());

        // 4. 提交交易 (原子性：訊息發送 + Offset 提交 同時生效)
        producer.commitTransaction();

    } catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException e) {
        // 致命錯誤，無法恢復，必須關閉應用程式
        e.printStackTrace();
        producer.close();
        break;
    } catch (KafkaException e) {
        // 可恢復錯誤，回滾交易，下次 loop 重試
        producer.abortTransaction();
    }
}
```

### 關鍵決策點 (Decision Tree)

1.  **是否涉及「讀 Kafka -> 寫 Kafka」？**
    -   Yes -> 考慮使用 Kafka Transactions (EOS)。
    -   No (例如讀 Kafka -> 寫 HTTP/DB) -> Kafka Transactions 無法保證端到端 EOS，需依賴 DB 交易或等冪設計。

2.  **是否能容忍偶爾的重複資料？**
    -   Yes (日誌、點擊流) -> 使用預設 At-least-once，效能較好。
    -   No (金流、庫存) -> 開啟 EOS，並接受輕微的效能損耗。