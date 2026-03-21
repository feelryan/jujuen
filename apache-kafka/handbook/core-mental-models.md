# 核心思維：分散式日誌與分區模型 / Core Mental Models: Distributed Log and Partitioning

## Mental model｜心智模型

要掌握 Kafka，首先必須「忘掉」傳統 Message Queue (如 RabbitMQ, ActiveMQ) 的概念。Kafka 不是一個佇列，它是一個 **分散式提交日誌 (Distributed Commit Log)**。

### 1. 日誌 vs. 佇列 (The Log vs. The Queue)
- **Queue (佇列)**：像是「信箱」。訊息被取出後就消失了（Popped）。它的重點是「任務分配」。
- **Log (日誌)**：像是「帳本」或「日記」。訊息被寫入後是**持久化**的（Persisted），讀取訊息就像是翻閱日記。多人可以同時讀同一本日記，互不干擾。
- **Implication**：Kafka 的資料不會因為被消費而刪除。這使得 Kafka 能夠支援「重播 (Replay)」和「多重訂閱者 (Multi-subscriber)」模式。

### 2. 分區即並行 (Partition is the Unit of Parallelism)
- 一個 Topic 是一個邏輯概念，物理上它被切分成多個 **Partition (分區)**。
- **並行度公式**：`Max Parallelism <= Number of Partitions`。
- 如果你有 10 個 Partition，你最多只能有 10 個 Consumer 同時並行消費（在同一個 Consumer Group 內）。
- **Mental Image**：想像高速公路的「車道」。Partition 就是車道，Consumer 就是收費站。增加車道才能增加同時通過的車流量。

### 3. 順序的相對論 (Relativity of Ordering)
- **全域順序 (Global Ordering)** 在分散式系統中是昂貴且幾乎不可能的。
- Kafka 保證的是 **分區內的順序 (Partition-level Ordering)**。
- **Key 的作用**：Producer 發送訊息時指定的 Key (如 `user_id`) 決定了訊息會進入哪個 Partition。相同的 Key 永遠進入同一個 Partition，從而保證該 Key 相關事件的嚴格順序。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 語義分區 (Semantic Partitioning / Keying Strategy)
最關鍵的設計決策是：「我該用什麼作為 Key？」
- **Pattern**：使用業務實體 ID (Entity ID) 作為 Key（例如 `OrderID`, `UserID`, `DeviceID`）。
- **Why**：這保證了針對同一實體的所有變更（建立、更新、刪除）都會按順序被同一個 Consumer 處理，避免 Race Condition。
- **Code Snippet**:
  ```java
  // Good: Ensure order for a specific order_id
  producer.send(new ProducerRecord<>("orders", order.getId(), order.toJson()));
  ```

### 2. 吞吐量驅動的分區規劃 (Throughput-Driven Partition Sizing)
不要憑感覺設定 Partition 數量。
- **Formula**：$N_p = \max(T_p/P_p, T_c/C_p)$
  - $N_p$: 需要的 Partition 數量
  - $T_p$: 目標總吞吐量 (Target Throughput)
  - $P_p$: 單一 Producer 寫入單一 Partition 的極限速度
  - $C_p$: 單一 Consumer 處理單一 Partition 的極限速度
- **Rule of Thumb**：通常 Consumer 的處理邏輯（寫 DB、計算）是瓶頸。如果你的 Consumer 每秒能處理 100 條，而你需要每秒處理 10,000 條，你就至少需要 100 個 Partition。

### 3. 黏性分區與批次優化 (Sticky Partitioning for Batching)
當沒有指定 Key 時（不需要順序），Kafka Producer 預設會使用 Sticky Partitioning。
- **Practice**：讓 Producer 在短時間內將訊息填滿同一個 Batch 發送到同一個 Partition，而不是隨機輪詢 (Round-robin)。這能大幅降低延遲並提升壓縮率。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 迷信全域順序 (The Global Ordering Fallacy)
- **Anti-pattern**：系統依賴 Topic 中所有訊息的絕對時間順序，卻又開了多個 Partition。
- **Consequence**：Consumer A 處理 Partition 1 的訊息可能比 Consumer B 處理 Partition 2 的訊息慢，導致跨 Partition 的業務邏輯順序錯亂。
- **Fix**：如果必須全域有序，只能設 1 個 Partition（但會犧牲擴展性），或者重新設計架構以依賴 Key 級別的順序。

### 2. 資料傾斜 (Data Skew / Hot Partitions)
- **Anti-pattern**：選用了一個分佈極不均勻的 Key。例如，以「國家」為 Key，結果 80% 的流量都來自 "US"，導致對應的 Partition 爆滿，負責該 Partition 的 Consumer 落後 (Lag)，而其他 Consumer 閒置。
- **Fix**：
  - 避免使用低基數 (Low Cardinality) 的 Key。
  - 如果必須處理大戶 (Hot Key)，考慮在應用層進行 "Salting"（例如 `US_1`, `US_2`...）。

### 3. 過度分區 (Over-Partitioning)
- **Anti-pattern**：為了「未來擴充」預先開了 10,000 個 Partition，但流量很小。
- **Consequence**：
  - Broker 端需要打開大量檔案句柄 (File Handles)。
  - 增加端到端延遲（Replication 負擔）。
  - Leader Election 在 Broker 當機時會花費更長時間，導致可用性下降。
- **Guideline**：單一 Broker 的 Partition 總數建議控制在 2,000 - 4,000 以內（視硬體而定）。

---

## Checklists & workflows｜檢查清單與流程

### Partition Count Calculator Decision Tree
在建立新 Topic 前，請執行此流程：

- [ ] **Step 1: 順序需求評估**
    - [ ] 是否需要嚴格順序？
        - 是 → 必須指定 Key。
        - 否 → Key 設為 null，利用 Sticky Partitioning 提升效能。
    - [ ] 順序是全域的還是局部的？
        - 全域 → Partition Count = 1 (警告：效能瓶頸)。
        - 局部 (Per User/Device) → Partition Count > 1，Key = Entity ID。

- [ ] **Step 2: 容量規劃**
    - [ ] 預估未來 1-2 年的峰值吞吐量 (MB/s 或 MSG/s)。
    - [ ] 測試單一 Consumer 的處理極限 (Consumer Lag 測試)。
    - [ ] 計算：`目標吞吐量 / 單一 Consumer 速率` = `最小 Partition 數`。
    - [ ] 加上緩衝 (通常建議 x 1.5 或 x 2)。

- [ ] **Step 3: 留存策略 (Retention)**
    - [ ] 這些資料是 Log (時間到了就刪) 還是 State (最新的才重要)？
        - Log → 設定 `retention.ms` 或 `retention.bytes`。
        - State → 開啟 Log Compaction (`cleanup.policy=compact`)。

---

## Real-world examples｜實戰案例

### Case 1: 電商訂單狀態流 (E-commerce Order Stream)
**情境**：你需要處理訂單的生命週期（建立 -> 付款 -> 出貨 -> 完成）。
- **Requirement**：同一個訂單的狀態變更必須嚴格有序。不能先處理「出貨」再處理「付款」。
- **Design**：
  - **Topic**: `order-events`
  - **Partition Count**: 30 (基於預估吞吐量)。
  - **Key**: `order_id` (這是關鍵！)。
  - **Payload**: 包含狀態變更的完整資訊。
- **Why**: 確保 `order_id: 1001` 的所有事件都在 Partition 5，由同一個 Consumer 依序讀取。

### Case 2: 大規模 IoT 遙測數據 (High Volume IoT Telemetry)
**情境**：百萬台智慧電表每分鐘回傳電壓數據，用於計算區域總負載。
- **Requirement**：單一電表的順序不重要（或者可以在應用層透過 Timestamp 排序），重點是極高的寫入與讀取吞吐量。
- **Design**：
  - **Topic**: `meter-readings`
  - **Partition Count**: 200 (為了極高的並行寫入)。
  - **Key**: `null` (隨機/Sticky)。
- **Why**: 如果用 `meter_id` 當 Key，可能會因為某些區域電表密集導致 Data Skew。且此處只需聚合計算，不需要嚴格順序，使用 `null` key 可以讓 Broker 平均分配資料，達到最大吞吐量。