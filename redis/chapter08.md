# Chapter 08: Messaging & Stream Processing
# 第八章：訊息傳遞與串流處理

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

While Redis is primarily known as a caching layer, its capabilities as a message broker are powerful tools in a Senior Engineer's arsenal. This chapter moves beyond simple caching to explore how Redis handles asynchronous communication. We will dissect the fundamental differences between the "Fire-and-Forget" model of Pub/Sub and the "Log-based" persistence model of Redis Streams.

雖然 Redis 主要以快取層聞名，但它作為訊息代理（Message Broker）的能力是資深工程師軍火庫中的強大工具。本章將超越單純的快取應用，深入探討 Redis 如何處理非同步通訊。我們將剖析 Pub/Sub 的「射後不理（Fire-and-Forget）」模式與 Redis Streams 的「日誌型（Log-based）」持久化模式之間的根本差異。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Distinguish clearly between Redis Pub/Sub and Redis Streams:** Understand when to use ephemeral broadcasting versus durable, replayable logs.
    **清晰區分 Redis Pub/Sub 與 Redis Streams：** 理解何時使用短暫的廣播，何時使用持久且可重播的日誌。
2.  **Implement Consumer Groups:** Design scalable worker patterns using Redis Streams to distribute load and handle failures (ACKs).
    **實作 Consumer Groups：** 使用 Redis Streams 設計可擴展的 Worker 模式，以分散負載並處理故障（ACK 機制）。
3.  **Evaluate Redis vs. Dedicated Brokers (Kafka/RabbitMQ):** Articulate the trade-offs regarding latency, durability, and complexity in a System Design interview context.
    **評估 Redis 與專用 Broker（Kafka/RabbitMQ）的差異：** 在系統設計面試的情境中，闡述關於延遲、持久性與複雜度的權衡。
4.  **Avoid Memory Pitfalls:** Manage memory usage effectively using `MAXLEN` and understanding Output Buffer Limits.
    **避免記憶體陷阱：** 透過 `MAXLEN` 與理解 Output Buffer Limits 來有效地管理記憶體使用。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

To master messaging in Redis, you must build two distinct mental models.
要精通 Redis 中的訊息傳遞，你必須建立兩個截然不同的心智模型。

### 2.1 Pub/Sub: The Radio Station (Fire-and-Forget)
### 2.1 Pub/Sub：廣播電台（射後不理）

Think of **Pub/Sub** like a live radio broadcast. If you are tuned in (subscribed) when the song plays, you hear it. If your radio is off (client disconnected) or you tune in late, you miss the content forever. There is no history.
將 **Pub/Sub** 想像成現場廣播電台。如果你在歌曲播放時正在收聽（訂閱），你就能聽到。如果你的收音機關閉（客戶端斷線）或你晚點才加入，你會永遠錯過該內容。它沒有歷史紀錄。

*   **Topology:** Many-to-Many fan-out.
*   **Storage:** None. Messages are pushed to sockets immediately.
*   **Key Characteristic:** Ephemeral. Low latency, but zero durability guarantee.
*   **拓撲結構：** 多對多扇出（Fan-out）。
*   **儲存：** 無。訊息會立即推送到 socket。
*   **關鍵特徵：** 短暫性。低延遲，但零持久性保證。

### 2.2 Redis Streams: The Append-Only Log (Kafka-lite)
### 2.2 Redis Streams：僅附加日誌（輕量版 Kafka）

Think of **Redis Streams** like a WhatsApp group chat or a commit log. Messages are appended to a timeline. Even if you go offline, the messages are stored. You can read from the beginning, read only new messages, or read as a group.
將 **Redis Streams** 想像成 WhatsApp 群組聊天或 Commit Log。訊息被附加到時間軸上。即使你離線，訊息仍被儲存。你可以從頭讀取、只讀取新訊息，或作為一個群組來讀取。

*   **Structure:** A Radix Tree acting as an append-only log.
*   **Consumer Groups:** Similar to Kafka Consumer Groups. Allows a pool of workers to consume a stream cooperatively; each message is delivered to only one consumer within the group.
*   **Key Characteristic:** Durable (in memory/disk), Replayable, Supports Acknowledgements (ACK).
*   **結構：** 一個作為僅附加日誌（Append-only log）的 Radix Tree。
*   **Consumer Groups：** 類似 Kafka 的 Consumer Groups。允許一組 Worker 協作消費同一個串流；每條訊息只會傳遞給群組中的一個消費者。
*   **關鍵特徵：** 持久（在記憶體/硬碟）、可重播、支援確認機制（ACK）。

### 2.3 Comparison Table
### 2.3 對照表

| Feature | Pub/Sub | Redis Streams |
| :--- | :--- | :--- |
| **Delivery Semantics** | At-most-once (Fire & Forget) | At-least-once (with ACKs) |
| **Persistence** | None | Yes (Configurable retention) |
| **Fan-out** | Native (All subscribers get copy) | Supported (Multiple Consumer Groups) |
| **Blocking Operations** | `SUBSCRIBE` (Blocking) | `XREAD` / `XREADGROUP` (Blocking) |
| **Memory Cost** | Low (Buffer only) | High (Stores data) |

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a distributed system, choosing the right tool prevents architectural bottlenecks.
在分散式系統中，選擇正確的工具可以避免架構瓶頸。

### 3.1 Scenario: Real-time WebSocket Notifications
### 3.1 場景：即時 WebSocket 通知

**Use Case:** A live sports score app needs to push updates to millions of connected clients.
**案例：** 一個即時體育比分 App 需要推送更新給數百萬個連線的客戶端。

*   **Choice:** **Redis Pub/Sub**.
*   **Reasoning:**
    *   **Speed:** We need sub-millisecond fan-out.
    *   **Ephemerality:** If a user disconnects, they will likely fetch the full state via REST API upon reconnection. We don't need Redis to store the history of every goal scored 5 minutes ago.
    *   **Architecture:** Backend services publish to a channel; WebSocket servers subscribe and forward to frontend clients.
*   **選擇：** **Redis Pub/Sub**。
*   **理由：**
    *   **速度：** 我們需要亞毫秒級的扇出能力。
    *   **短暫性：** 如果使用者斷線，他們重新連線時通常會透過 REST API 獲取完整狀態。我們不需要 Redis 儲存 5 分鐘前進球的歷史紀錄。
    *   **架構：** 後端服務發布到頻道；WebSocket 伺服器訂閱並轉發給前端客戶端。

### 3.2 Scenario: Asynchronous Job Processing
### 3.2 場景：非同步任務處理

**Use Case:** An e-commerce system generating PDF invoices after checkout.
**案例：** 一個電子商務系統在結帳後生成 PDF 發票。

*   **Choice:** **Redis Streams**.
*   **Reasoning:**
    *   **Reliability:** We cannot lose the "Generate Invoice" event if the worker crashes.
    *   **Consumer Groups:** We want 5 workers to process invoices in parallel. Pub/Sub would send the same invoice to all 5 workers (duplicate work).
    *   **Recovery:** If a worker dies while processing, the message remains in the `Pending Entries List (PEL)` and can be claimed by another worker.
*   **選擇：** **Redis Streams**。
*   **理由：**
    *   **可靠性：** 如果 Worker 崩潰，我們不能遺失「生成發票」的事件。
    *   **Consumer Groups：** 我們希望 5 個 Worker 平行處理發票。Pub/Sub 會將同一張發票發送給所有 5 個 Worker（重複工作）。
    *   **恢復：** 如果 Worker 在處理時掛掉，訊息會保留在 `Pending Entries List (PEL)` 中，並可被另一個 Worker 接手。

### 3.3 System Design: Redis vs. Kafka
### 3.3 系統設計：Redis vs. Kafka

In interviews, you might be asked: *"Why use Redis Streams instead of Kafka?"*
在面試中，你可能會被問到：*「為什麼使用 Redis Streams 而不是 Kafka？」*

*   **Use Redis Streams when:**
    *   You already use Redis (simpler stack).
    *   Latency is critical (in-memory is faster than disk).
    *   Data volume is manageable (limited by RAM).
    *   Retention is short (e.g., keep logs for 3 days).
*   **Use Kafka when:**
    *   Retention is massive (Terabytes of history).
    *   Throughput is extremely high (millions of msgs/sec).
    *   Strict ordering guarantees across partitions are complex.
*   **使用 Redis Streams 的時機：**
    *   你已經在使用 Redis（技術堆疊較簡單）。
    *   延遲至關重要（記憶體比硬碟快）。
    *   資料量可控（受限於 RAM）。
    *   保留期較短（例如：保留 3 天的日誌）。
*   **使用 Kafka 的時機：**
    *   保留量巨大（TB 級別的歷史紀錄）。
    *   吞吐量極高（每秒數百萬條訊息）。
    *   跨分區的嚴格順序保證很複雜。

---

## 4. Walkthrough: Implementing a Robust Job Queue
## 4. 逐步示例：實作一個穩健的任務佇列

Let's implement a reliable job queue using Redis Streams. We will simulate a Producer adding jobs and a Consumer Group processing them.
讓我們使用 Redis Streams 實作一個可靠的任務佇列。我們將模擬 Producer 新增任務以及 Consumer Group 處理它們。

### Step 1: Producer adds a job (XADD)
### 步驟 1：Producer 新增任務 (XADD)

The producer adds an event to the stream `invoice_events`.
Producer 將一個事件新增到 `invoice_events` 串流中。

```bash
# XADD key ID field value [field value ...]
# * means auto-generate ID (timestamp-sequence)
XADD invoice_events * order_id 1001 user_id 55
```

*Result:* Returns the ID, e.g., `1693300000000-0`.
*結果：* 回傳 ID，例如 `1693300000000-0`。

### Step 2: Setup Consumer Group (XGROUP)
### 步驟 2：設定 Consumer Group (XGROUP)

This is usually a one-time setup. We create a group named `workers` reading from the beginning (`0`).
這通常是一次性的設定。我們建立一個名為 `workers` 的群組，從頭（`0`）開始讀取。

```bash
# XGROUP CREATE key groupname id [MKSTREAM]
XGROUP CREATE invoice_events workers 0 MKSTREAM
```

### Step 3: Consumer reads and locks message (XREADGROUP)
### 步驟 3：Consumer 讀取並鎖定訊息 (XREADGROUP)

Worker A asks for new messages. The `>` symbol means "give me messages never delivered to other consumers in this group".
Worker A 請求新訊息。`>` 符號代表「給我那些尚未傳遞給此群組中其他消費者的訊息」。

```bash
# XREADGROUP GROUP group consumer [COUNT n] [BLOCK ms] STREAMS key id
XREADGROUP GROUP workers worker_a COUNT 1 BLOCK 2000 STREAMS invoice_events >
```

*   **Mechanism:** Redis moves the message to the **Pending Entries List (PEL)** for `worker_a`. No other worker can get this specific message now.
*   **機制：** Redis 將該訊息移至 `worker_a` 的 **Pending Entries List (PEL)**。現在其他 Worker 無法取得這條特定訊息。

### Step 4: Processing & Acknowledgment (XACK)
### 步驟 4：處理與確認 (XACK)

Worker A processes the invoice. Upon success, it must acknowledge.
Worker A 處理發票。成功後，它必須發送確認。

```bash
# XACK key group id
XACK invoice_events workers 1693300000000-0
```

*   **Effect:** The message is removed from the PEL. It is considered "done".
*   **效果：** 訊息從 PEL 中移除。它被視為「已完成」。

### Step 5: Handling Failures (Claiming Pending Messages)
### 步驟 5：處理故障（認領待處理訊息）

If Worker A crashes *before* `XACK`, the message stays in PEL forever. Worker B needs to find these "stuck" messages.
如果 Worker A 在 `XACK` *之前* 崩潰，訊息會永遠留在 PEL 中。Worker B 需要找出這些「卡住」的訊息。

1.  **Check Pending:** `XPENDING invoice_events workers`
2.  **Claim:** `XCLAIM invoice_events workers worker_b 10000 1693300000000-0`
    *   (Claims the message if it has been idle for 10000ms).

1.  **檢查待處理：** `XPENDING invoice_events workers`
2.  **認領：** `XCLAIM invoice_events workers worker_b 10000 1693300000000-0`
    *   （如果訊息閒置超過 10000ms，則認領該訊息）。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Unbounded Streams (Memory Leak)
### 5.1 無限制的串流（記憶體洩漏）

*   **Anti-pattern:** Using `XADD` without limiting the stream size.
*   **Issue:** Redis is in-memory. If you never delete old messages, you will eventually hit `maxmemory` and crash the instance or trigger eviction policies that might delete keys randomly.
*   **Solution:** Use `XADD ... MAXLEN ~ 10000`. The `~` allows Redis to trim approximately, which is more efficient than exact trimming.
*   **反模式：** 使用 `XADD` 時未限制串流大小。
*   **問題：** Redis 是基於記憶體的。如果你從不刪除舊訊息，最終會達到 `maxmemory` 上限，導致實例崩潰或觸發驅逐策略（可能會隨機刪除 Key）。
*   **解法：** 使用 `XADD ... MAXLEN ~ 10000`。`~` 允許 Redis 進行近似修剪，這比精確修剪更有效率。

### 5.2 Pub/Sub Slow Consumers
### 5.2 Pub/Sub 慢速消費者

*   **Anti-pattern:** A subscriber processes messages slower than the publisher sends them.
*   **Issue:** Redis buffers messages for the subscriber in the **Output Buffer**. If this buffer grows too large, Redis will forcibly disconnect the client to protect itself (controlled by `client-output-buffer-limit pubsub`).
*   **Solution:** Offload processing to a background thread or use Redis Streams (which allows consumers to pull at their own pace).
*   **反模式：** 訂閱者處理訊息的速度慢於發布者發送的速度。
*   **問題：** Redis 會在 **Output Buffer** 中為訂閱者緩衝訊息。如果此緩衝區變得太大，Redis 會強制斷開客戶端連線以自我保護（由 `client-output-buffer-limit pubsub` 控制）。
*   **解法：** 將處理工作卸載到背景執行緒，或改用 Redis Streams（允許消費者以自己的步調拉取資料）。

### 5.3 Forgetting the PEL (Zombie Messages)
### 5.3 遺忘 PEL（殭屍訊息）

*   **Anti-pattern:** Using Consumer Groups but never implementing a "reaper" process to check `XPENDING`.
*   **Issue:** If consumers crash, messages remain in the "Pending" state forever, consuming memory and never being processed.
*   **Solution:** Implement a background loop or a separate "recovery worker" that periodically scans `XPENDING` and claims idle messages.
*   **反模式：** 使用 Consumer Groups 但從未實作「收割（Reaper）」程序來檢查 `XPENDING`。
*   **問題：** 如果消費者崩潰，訊息將永遠保持在「Pending」狀態，佔用記憶體且永遠不會被處理。
*   **解法：** 實作一個背景迴圈或獨立的「恢復 Worker」，定期掃描 `XPENDING` 並認領閒置訊息。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### 6.1 Design a News Feed System
### 6.1 設計動態消息系統（News Feed）

*   **Question:** "How would you use Redis to build a 'User Timeline' feature (like Twitter/Instagram)?"
*   **Key Points:**
    *   **Fan-out on Write:** When a user posts, push the Post ID to the Redis Stream/List of all followers.
    *   **Hybrid Approach:** Use Redis for the "active" feed (last 100 items) and a database (Cassandra/Postgres) for history.
    *   **Why Streams?** Efficient memory usage (listpack encoding) and ability to store metadata (timestamp) natively compared to simple Lists.
*   **問題：** 「你會如何使用 Redis 構建『使用者時間軸』功能（像 Twitter/Instagram）？」
*   **高分要點：**
    *   **寫入時扇出（Fan-out on Write）：** 當使用者發文時，將貼文 ID 推送到所有追蹤者的 Redis Stream/List 中。
    *   **混合方法：** 使用 Redis 處理「活躍」動態（最後 100 則），並使用資料庫（Cassandra/Postgres）儲存歷史紀錄。
    *   **為何選 Streams？** 相較於簡單的 List，Streams 的記憶體使用效率更高（listpack 編碼），且能原生儲存中繼資料（時間戳）。

### 6.2 At-Most-Once vs. At-Least-Once
### 6.2 至多一次 vs. 至少一次

*   **Question:** "In what scenario is data loss acceptable in a messaging system? How does Redis handle this?"
*   **Key Points:**
    *   **Acceptable:** Metrics collection, logging, live chat presence, real-time stock prices (where old data is useless). -> Use **Pub/Sub**.
    *   **Unacceptable:** Financial transactions, order processing. -> Use **Streams** with ACKs and AOF persistence (fsync every sec or always).
*   **問題：** 「在訊息系統中，什麼場景下資料遺失是可以接受的？Redis 如何處理這個問題？」
*   **高分要點：**
    *   **可接受：** 指標收集、日誌記錄、即時聊天在線狀態、即時股價（舊資料無用）。-> 使用 **Pub/Sub**。
    *   **不可接受：** 金融交易、訂單處理。-> 使用 **Streams** 搭配 ACK 與 AOF 持久化（每秒 fsync 或總是 fsync）。

### 6.3 Handling "Poison Pill" Messages
### 6.3 處理「毒丸（Poison Pill）」訊息

*   **Question:** "A specific message crashes your consumer every time it's read. How do you handle this in Redis Streams?"
*   **Key Points:**
    *   Redis tracks `delivery_count` in `XPENDING`.
    *   If `delivery_count` > threshold (e.g., 5), the worker should `XACK` it (to remove from queue) and push it to a separate "Dead Letter Queue" (DLQ) stream for manual inspection.
*   **問題：** 「有一條特定訊息每次被讀取時都會導致消費者崩潰。你在 Redis Streams 中如何處理？」
*   **高分要點：**
    *   Redis 在 `XPENDING` 中會追蹤 `delivery_count`（傳遞次數）。
    *   如果 `delivery_count` > 閾值（例如 5），Worker 應該對其執行 `XACK`（從佇列移除），並將其推送到獨立的「死信佇列（DLQ）」Stream 以供人工檢查。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Pub/Sub is for Broadcasting:** Use it for ephemeral, real-time events where history doesn't matter (e.g., WebSocket triggers).
    **Pub/Sub 用於廣播：** 用於歷史紀錄不重要的短暫即時事件（例如 WebSocket 觸發器）。
2.  **Streams are for Logs:** Use them for durable, sequential data processing (e.g., Job Queues, Event Sourcing).
    **Streams 用於日誌：** 用於持久、順序性的資料處理（例如任務佇列、事件溯源）。
3.  **Consumer Groups Scale Reads:** They allow multiple workers to process a single stream in parallel without duplication.
    **Consumer Groups 擴展讀取：** 它們允許數個 Worker 平行處理單一串流且不重複。
4.  **Memory Management is Crucial:** Always use `MAXLEN` with Streams and monitor `client-output-buffer` for Pub/Sub.
    **記憶體管理至關重要：** 在 Streams 中務必使用 `MAXLEN`，並在 Pub/Sub 中監控 `client-output-buffer`。
5.  **ACK Mechanism:** Streams require explicit `XACK`. Without it, the PEL grows indefinitely.
    **ACK 機制：** Streams 需要明確的 `XACK`。沒有它，PEL 會無限增長。

### Next Steps
### 後續延伸

*   **High Availability:** How do Streams behave during a failover? Read about **Redis Sentinel** and **Redis Cluster** replication implications.
    **高可用性：** Streams 在故障轉移時表現如何？閱讀關於 **Redis Sentinel** 與 **Redis Cluster** 複製機制的影響。
*   **Advanced Processing:** Explore **Redis Gears** or **Lua Scripting** to filter or transform stream messages directly on the server before sending them to consumers.
    **進階處理：** 探索 **Redis Gears** 或 **Lua Scripting**，在將訊息發送給消費者之前，直接在伺服器端過濾或轉換串流訊息。