# 訊息佇列與串流處理實戰 / Message Queues & Stream Processing

## Mental model｜心智模型

在 Redis 中處理訊息傳遞（Messaging）時，工程師常會陷入「該用哪個資料結構」的選擇困難。為了做出正確決策，我們需要建立三種不同的心智模型：

### 1. The Radio Broadcast (Pub/Sub)
**廣播電台模型**。發送者（Publisher）發出訊號，當下有在收聽（Subscribe）的人才收得到。
- **特性**：Fire-and-forget（射後不理）。
- **記憶**：無。如果你在廣播時剛好去上廁所（斷線），回來後無法重聽剛才的內容。
- **適用**：即時通知、WebSocket 推播觸發、系統快取失效通知。

### 2. The Conveyor Belt (List)
**輸送帶模型**。生產者將工件放到輸送帶頭（LPUSH），工人從輸送帶尾拿取（RPOP）。
- **特性**：Point-to-Point（點對點）。一個任務通常只被一個 Worker 處理。
- **記憶**：有，但脆弱。任務一旦被拿走（Pop），就從 Redis 中消失。如果 Worker 拿到任務後崩潰，該任務就永久遺失了（除非使用 `RPOPLPUSH` / `LMOVE` 做備份）。
- **適用**：簡單的 Job Queue（如 Sidekiq, Celery 早期實作）、不需要回溯的任務。

### 3. The Append-only Log (Redis Streams)
**唯增日誌模型**（類似 Kafka）。事件被依序寫入一個不可變的日誌中，每個事件都有唯一的 ID（時間戳記）。
- **特性**：Multi-Consumer & Persistence。多個 Consumer 可以讀取同一份日誌；支援 **Consumer Groups**（消費者群組）來分攤工作負載。
- **記憶**：強大。支援 **Acknowledgements (ACK)** 機制，確保訊息被成功處理後才標記完成。支援回溯讀取（Replay）。
- **適用**：事件溯源（Event Sourcing）、可靠的訊息佇列、需要 At-least-once 語意的關鍵業務。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 選型決策矩陣 (Selection Strategy)
在實戰中，請依據以下關鍵問題選擇：
- **需要廣播給多個服務嗎？**
  - 是，且不介意遺失 → **Pub/Sub**
  - 是，且新加入的服務要讀歷史資料 → **Streams**
- **需要確保任務不遺失（Reliability）嗎？**
  - 非常需要 → **Streams** (配合 ACK)
  - 普通，簡單就好 → **List** (配合 RPOPLPUSH/LMOVE)
- **吞吐量與複雜度權衡**
  - 極高吞吐、低延遲、允許掉資料 → **Pub/Sub**
  - 中高吞吐、需要持久化與複雜路由 → **Streams**

### 2. Consumer Groups 與可靠性設計 (Reliability with Streams)
這是 Redis Streams 最強大的模式，用於實作 **At-least-once** 語意。
- **Consumer Group**：讓多個 consumer 共同消費一個 stream，Redis 會追蹤每個訊息被「誰」讀走了，但還沒確認（ACK）。
- **PEL (Pending Entries List)**：這是可靠性的核心。當 consumer讀取訊息但尚未 `XACK` 時，訊息會進入 PEL。
- **Recovery 流程**：
  1. 正常讀取：`XREADGROUP GROUP mygroup consumer1 STREAMS mystream >`
  2. 處理業務邏輯。
  3. 確認完成：`XACK mystream mygroup <message-id>`
  4. **故障恢復**：另一個 process 定期檢查 PEL 中「超時未 ACK」的訊息，使用 `XCLAIM` 或 `XAUTOCLAIM` 接手處理。

### 3. 空間管理與效能優化 (Capping the Stream)
Stream 是唯增的，如果不管理，記憶體會爆掉。
- **Approximate Trimming (`MAXLEN ~`)**：
  - **不要用**：`XADD mystream MAXLEN 1000 ...` (精確修剪極耗效能)
  - **要用**：`XADD mystream MAXLEN ~ 1000 ...` (加上 `~` 表示近似修剪，Redis 會在效能與長度間取得平衡，通常會多保留幾十個節點，但效能好非常多)。
- **定期歸檔**：如果需要永久保存，應由 Consumer 將資料寫入 S3 或 Data Warehouse，Redis 只保留最近 N 天或 N 筆熱資料。

### 4. 避免輪詢 (Blocking Operations)
永遠不要寫 `while(true) { check(); sleep(1); }` 這種迴圈。
- List: 使用 `BLPOP` / `BRPOP`。
- Streams: 使用 `XREAD BLOCK` 或 `XREADGROUP BLOCK`。
- 這能大幅降低 Redis CPU 負載並減少網路延遲。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Forever Pending" Leak (PEL 洩漏)
- **現象**：Stream 的記憶體使用量持續上升，即使設定了 `MAXLEN`。
- **原因**：Consumer 讀取了訊息卻**忘記/失敗執行 `XACK`**。這些訊息會永遠卡在 PEL 中，`MAXLEN` 也不會清除 PEL 中的項目。
- **解法**：確保程式碼有 `finally` 區塊處理 ACK，並實作 Dead Letter Queue 機制處理無法被消化的壞訊息。

### 2. Using List for 1-to-N Broadcasting
- **錯誤做法**：為了讓三個服務都收到訂單通知，維護了三個 List (`orders:serviceA`, `orders:serviceB`...) 並由生產者寫入三次。
- **後果**：缺乏原子性（寫入兩個成功，第三個失敗怎麼辦？），維護困難。
- **解法**：使用 **Redis Streams**，寫入一次，建立三個 Consumer Groups 分別讀取。

### 3. Pub/Sub for Critical Data
- **錯誤做法**：用 Pub/Sub 傳遞「用戶註冊成功」事件以觸發後續流程。
- **後果**：如果 Consumer 服務重啟或網路瞬斷，該事件就憑空消失，導致資料不一致。
- **修正**：關鍵業務流程請務必使用 Streams 或 List。

### 4. Ignoring `XREADGROUP` the `>` ID
- **陷阱**：在使用 Consumer Group 時，搞混 ID 的用法。
- **正確觀念**：
  - 使用特殊 ID `>`：表示「給我**從未被傳遞給任何 consumer** 的新訊息」。
  - 使用具體 ID `0` 或其他：表示「給我**已分配給我但尚未 ACK** 的舊訊息（處理 PEL）」。
- **錯誤**：一直用 `>` 卻不處理 PEL，導致崩潰重啟後，之前的任務遺失（實際上是卡在 PEL 沒人理）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Checklist: Queue vs Stream
- [ ] **Persistence**: 系統崩潰重啟後，未處理的訊息還在嗎？(List/Stream: Yes, Pub/Sub: No)
- [ ] **Fan-out**: 同一個訊息需要被多個不同的下游系統處理嗎？(Stream: Yes, List: No)
- [ ] **Replayability**: 需要重新處理過去幾天的資料嗎？(Stream: Yes, List/PubSub: No)
- [ ] **Complexity**: 團隊能維護 Consumer Group 的狀態與重試機制嗎？(Stream 較複雜)

### Implementation Checklist (Streams)
- [ ] **Trimming Strategy**: 寫入 (`XADD`) 時是否有加上 `MAXLEN ~ <count>`？
- [ ] **Consumer Group Setup**: 部署前是否已預先建立 Group (`XGROUP CREATE`)？注意這通常是一次性操作。
- [ ] **Blocking Read**: 是否使用了 `BLOCK` 參數避免 busy-waiting？
- [ ] **ACK Logic**: 業務邏輯成功後才 `XACK`？還是先 ACK 再處理（At-most-once）？
- [ ] **Crash Recovery**: 是否有背景執行緒或機制定期掃描 PEL (`XAUTOCLAIM`) 處理超時訊息？
- [ ] **Monitoring**: 是否監控 `PEL` 的長度？(過長代表 Consumer 處理極慢或有 Bug)。

---

## Real-world examples｜實戰案例

### Scenario: Reliable Order Processing Pipeline
**情境**：電商系統，使用者下單後，需要扣庫存（Inventory）、發送確認信（Email）、通知大數據分析（Analytics）。

#### 1. Setup (One-time)
```bash
# 建立 Stream 與兩個 Consumer Groups
# Group 1: 核心業務 (庫存與信件)
XGROUP CREATE orders:stream core_services $ MKSTREAM
# Group 2: 數據分析 (可以容忍些微延遲，獨立讀取)
XGROUP CREATE orders:stream analytics_services $
```

#### 2. Producer (Web API)
```python
# 當使用者下單
redis.xadd("orders:stream", {
    "order_id": "1001",
    "user_id": "5566",
    "amount": "2500"
}, maxlen=10000, approximate=True) # 保持 Stream 大小在 10k 左右
```

#### 3. Consumer (Core Worker)
```python
while True:
    # 1. 讀取新訊息 (Block 2秒避免空轉)
    # '>' 表示讀取尚未分配給任何人的新訊息
    entries = redis.xreadgroup("core_services", "worker-1", {"orders:stream": ">"}, block=2000, count=10)

    if not entries:
        # 2. 空閒時，檢查是否有 Crash 的同事留下的爛攤子 (PEL Recovery)
        # 讀取 ID 為 '0'，表示讀取 Pending List
        recover_entries = redis.xreadgroup("core_services", "worker-1", {"orders:stream": "0"}, count=10)
        process_and_ack(recover_entries)
        continue

    # 3. 正常處理
    for stream, messages in entries:
        for message_id, data in messages:
            try:
                decrease_inventory(data)
                send_email(data)
                # 4. 關鍵：確認處理完成
                redis.xack("orders:stream", "core_services", message_id)
            except Exception as e:
                # 記錄錯誤，稍後由 Recovery 機制重試，或移入 Dead Letter Queue
                log_error(e)
```

#### 4. Recovery Strategy (The Safety Net)
在真實生產環境，通常會有一個獨立的 "Janitor" process 或在 worker 中定期執行 `XAUTOCLAIM`：
```text
# 尋找 orders:stream 中，被 core_services 群組讀取，但超過 60秒 (60000ms) 還沒 ACK 的訊息
# 將其擁有權轉移給當前 worker 並重新處理
XAUTOCLAIM orders:stream core_services worker-1 60000 0-0 COUNT 10
```

這個架構確保了：
1. **可靠性**：Worker 崩潰，訊息不會掉，會被其他 Worker 撈回來。
2. **擴展性**：Analytics 服務可以隨時加入讀取歷史資料，完全不影響 Core Services。
3. **效能**：Redis Stream 的寫入效能極高，足以應付大流量訂單。