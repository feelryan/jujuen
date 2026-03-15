# Chapter 05: Event-Driven Architecture & Big Data Processing
# 第五章：事件驅動架構與大數據處理

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In modern distributed systems, tight coupling between services is a primary bottleneck for scalability. This chapter focuses on decoupling systems using **Pub/Sub** and building robust data processing pipelines with **Dataflow** and **BigQuery**. As a Senior Engineer, you are expected to move beyond simple CRUD applications to designing systems capable of handling massive throughput and real-time analytics.
在現代分散式系統中，服務之間的緊密耦合是擴展性的主要瓶頸。本章專注於利用 **Pub/Sub** 進行系統解耦，並結合 **Dataflow** 與 **BigQuery** 構建穩健的資料處理管線。作為資深工程師，你應具備超越簡單 CRUD 應用程式的能力，轉而設計能夠處理巨量吞吐與即時分析的系統。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Architect for Decoupling**: Use Pub/Sub to implement asynchronous messaging patterns, handling backpressure and ensuring reliability.
    **設計解耦架構**：利用 Pub/Sub 實作非同步訊息模式，處理背壓（Backpressure）並確保可靠性。
2.  **Master Streaming Semantics**: Understand and apply advanced Dataflow concepts like **Windowing**, **Watermarks**, and **Triggers** to handle out-of-order data.
    **掌握串流語意**：理解並應用 **Windowing（視窗）**、**Watermarks（浮水印）** 與 **Triggers（觸發器）** 等進階 Dataflow 概念來處理亂序資料。
3.  **Optimize Data Ingestion**: Design cost-effective and high-performance ingestion paths into BigQuery using the Storage Write API.
    **優化資料寫入**：使用 Storage Write API 設計具成本效益且高效能的 BigQuery 寫入路徑。
4.  **Handle Failure Scenarios**: Implement Dead Letter Queues (DLQ) and exactly-once processing strategies.
    **處理故障場景**：實作死信佇列（DLQ）與「精確一次（Exactly-once）」處理策略。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Global Buffer" Mental Model (Pub/Sub)
### 2.1 「全域緩衝區」心智模型 (Pub/Sub)

Think of **Pub/Sub** not just as a message queue, but as a **global, elastic shock absorber**. Unlike Kafka, which requires partition management and cluster sizing, Pub/Sub is serverless and global.
請將 **Pub/Sub** 不僅視為訊息佇列，而是一個**全域且彈性的避震器**。不同於 Kafka 需要管理分區（Partition）與叢集規模，Pub/Sub 是無伺服器（Serverless）且全域的。

*   **Pub/Sub vs. Kafka**:
    *   **Kafka**: Log-based, ordered within partitions, consumer manages offset (pull model). Great for replayability and high throughput within a region.
    *   **Pub/Sub**: Index-based (mostly), global routing, per-message acknowledgement. Offers "at-least-once" delivery. Order is not guaranteed by default (unless Ordering Keys are used).
*   **Pub/Sub vs. Kafka**:
    *   **Kafka**: 基於日誌（Log-based），分區內有序，消費者管理 offset（拉取模式）。適合區域內的高吞吐量與重播（Replay）。
    *   **Pub/Sub**: 基於索引（Index-based），全域路由，逐條訊息確認（Ack）。提供「至少一次（At-least-once）」傳遞。預設不保證順序（除非使用 Ordering Keys）。

### 2.2 The "Unified Batch & Stream" Model (Dataflow/Apache Beam)
### 2.2 「批次與串流統一」模型 (Dataflow/Apache Beam)

**Dataflow** is the managed service for **Apache Beam**. The core mental model here is that **Batch is just a special case of Streaming** (where the data is bounded).
**Dataflow** 是 **Apache Beam** 的託管服務。這裡的核心心智模型是：**批次處理只是串流處理的一個特例**（即資料是有邊界的）。

*   **Event Time vs. Processing Time**:
    *   **Event Time**: When the event actually happened (e.g., timestamp on a mobile device).
    *   **Processing Time**: When the event arrived at the pipeline.
    *   *Senior Insight*: Distributed systems always have lag. Correctness depends on processing by **Event Time**, while latency depends on **Processing Time**.
*   **事件時間 vs. 處理時間**:
    *   **事件時間 (Event Time)**：事件實際發生的時間（例如行動裝置上的時間戳記）。
    *   **處理時間 (Processing Time)**：事件到達管線的時間。
    *   *資深觀點*：分散式系統總會有延遲。正確性取決於依據**事件時間**處理，而延遲則取決於**處理時間**。

### 2.3 The "Serverless Warehouse" (BigQuery)
### 2.3 「無伺服器倉儲」 (BigQuery)

BigQuery separates **Compute** (Dremel engine) from **Storage** (Colossus). This allows you to stream data in (via Storage Write API) without affecting query performance.
BigQuery 將**運算**（Dremel 引擎）與**儲存**（Colossus）分離。這允許你在不影響查詢效能的情況下，將資料串流寫入（透過 Storage Write API）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Typical Architecture: The "Kappa" Pipeline
### 典型架構：「Kappa」管線

In a production environment, you will often see the following pattern for telemetry, logs, or user activity tracking:
在生產環境中，針對遙測、日誌或使用者活動追蹤，你經常會看到以下模式：

`Client/Source -> Cloud Load Balancer -> Ingestion Service -> Pub/Sub -> Dataflow -> BigQuery`

1.  **Ingestion**: Decouples the producer from the consumer. If Dataflow updates or crashes, Pub/Sub retains messages (up to 7 days).
    **攝取**：將生產者與消費者解耦。如果 Dataflow 更新或崩潰，Pub/Sub 會保留訊息（最長 7 天）。
2.  **Processing (Dataflow)**: Handles deduplication, windowed aggregation (e.g., "count clicks per minute"), and enrichment (joining with side inputs like User Profile).
    **處理 (Dataflow)**：處理去重複、視窗聚合（例如「每分鐘點擊數」）以及資料豐富化（與 User Profile 等 Side Inputs 進行 Join）。
3.  **Storage (BigQuery)**: Serves as the sink for analytics. Partitioned by ingestion time or event time for cost efficiency.
    **儲存 (BigQuery)**：作為分析的終點。依據攝取時間或事件時間進行分區（Partitioning），以提升成本效益。

### Impact on Non-Functional Requirements
### 對非功能性需求的影響

*   **Scalability**: Pub/Sub scales to millions of ops/sec automatically. Dataflow enables **Streaming Engine** and **Horizontal Autoscaling** to handle spikes.
    **擴展性**：Pub/Sub 可自動擴展至每秒數百萬次操作。Dataflow 啟用 **Streaming Engine** 與 **水平自動擴展** 來應對流量尖峰。
*   **Observability**: Key metrics include "Pub/Sub Unacked Messages" (Backpressure indicator) and "System Lag" (Dataflow freshness).
    **可觀測性**：關鍵指標包括「Pub/Sub 未確認訊息數」（背壓指標）與「系統延遲」（Dataflow 資料新鮮度）。
*   **Reliability**: Handling "Poison Pills" (malformed messages) via Dead Letter Queues prevents pipeline stalling.
    **可靠性**：透過死信佇列（DLQ）處理「毒藥丸（Poison Pills，格式錯誤的訊息）」，防止管線停滯。

---

## 4. Walkthrough / Example: Real-Time Analytics Pipeline
## 4. 逐步示例：即時分析管線

### Scenario
### 情境

You need to build a system to count "Video Views" in real-time. Events arrive from mobile apps globally. Network issues cause some events to arrive late.
你需要構建一個系統來即時計算「影片觀看數」。事件來自全球的行動應用程式。網路問題會導致部分事件延遲到達。

### Step 1: The Naive Approach (Direct Insert)
### 步驟 1：天真做法（直接寫入）

Apps send HTTP requests directly to a backend that inserts into a SQL database.
App 直接發送 HTTP 請求到後端，後端直接寫入 SQL 資料庫。

*   *Failure Mode*: During a viral event, the DB locks up. Latency spikes. Data is lost if the backend crashes.
*   *失敗模式*：在病毒式傳播事件期間，資料庫鎖死。延遲飆升。若後端崩潰，資料將會遺失。

### Step 2: Decoupling with Pub/Sub
### 步驟 2：使用 Pub/Sub 解耦

Apps send data to a regional endpoint, which publishes to a global Pub/Sub topic.
App 將資料發送到區域端點，端點將資料發佈到全域 Pub/Sub 主題。

*   *Improvement*: The backend can now process at its own pace.
*   *改進*：後端現在可以依照自己的步調處理資料。

### Step 3: Handling Late Data with Dataflow (The Senior Solution)
### 步驟 3：使用 Dataflow 處理延遲資料（資深解法）

We use Apache Beam (Dataflow) to aggregate views by 1-minute windows based on **Event Time**.
我們使用 Apache Beam (Dataflow) 根據**事件時間**以 1 分鐘為視窗聚合觀看數。

```python
# Pseudo-code for Apache Beam Pipeline
import apache_beam as beam
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime

# 1. Read from Pub/Sub (Reading attributes for Event Timestamp)
# 1. 從 Pub/Sub 讀取（讀取屬性以獲取事件時間戳記）
events = (
    p | 'ReadPubSub' >> beam.io.ReadFromPubSub(
        subscription=input_subscription,
        timestamp_attribute='event_timestamp' # Critical for Event Time
    )
)

# 2. Windowing Strategy
# 2. 視窗策略
windowed_counts = (
    events
    | 'Window' >> beam.WindowInto(
        FixedWindows(60), # 1-minute windows
        # Trigger: Emit results when watermark passes, 
        # but also emit early updates every 10 seconds for real-time dashboards
        # 觸發器：當浮水印通過時發送結果，但也每 10 秒發送早期更新以供即時儀表板使用
        trigger=AfterWatermark(
            early=AfterProcessingTime(10),
            late=AfterProcessingTime(10)
        ),
        allowed_lateness=300, # Wait up to 5 mins for late data / 等待最多 5 分鐘的延遲資料
        accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING
    )
    | 'Count' >> beam.CombineGlobally(beam.combiners.CountCombineFn()).without_defaults()
)

# 3. Write to BigQuery
# 3. 寫入 BigQuery
windowed_counts | 'WriteBQ' >> beam.io.WriteToBigQuery(
    table_spec,
    method='STORAGE_WRITE_API' # High throughput method / 高吞吐量方法
)
```

### Why this works?
### 為何這行得通？

1.  **Watermarks**: Dataflow tracks the "watermark" (heuristic of input time). It knows when to "close" a window.
    **浮水印**：Dataflow 追蹤「浮水印」（輸入時間的啟發式推算）。它知道何時該「關閉」視窗。
2.  **Triggers**: We get early results (low latency) and final correct results (high consistency).
    **觸發器**：我們能獲得早期結果（低延遲）與最終正確結果（高一致性）。
3.  **Backpressure**: If BigQuery slows down, Dataflow stops pulling from Pub/Sub. Pub/Sub buffers the data.
    **背壓**：如果 BigQuery 變慢，Dataflow 會停止從 Pub/Sub 拉取。Pub/Sub 會緩衝資料。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Ignoring `ack_deadline` in Pub/Sub
### 5.1 忽略 Pub/Sub 中的 `ack_deadline`

*   **Anti-pattern**: Setting a short acknowledgment deadline for a long-running process.
    **反模式**：為長時間執行的程序設定過短的確認截止時間（ack deadline）。
*   **Consequence**: Pub/Sub thinks the worker failed and redelivers the message. Your system processes the same event multiple times (duplicates), wasting resources.
    **後果**：Pub/Sub 認為 worker 失敗並重新傳遞訊息。你的系統會多次處理同一事件（重複），浪費資源。
*   **Solution**: Extend the deadline dynamically or optimize processing time. Ensure idempotency.
    **解法**：動態延長截止時間或優化處理時間。確保冪等性（Idempotency）。

### 5.2 The "Hot Key" Problem in Dataflow
### 5.2 Dataflow 中的「熱點 Key」問題

*   **Anti-pattern**: Grouping data by a key that has uneven distribution (e.g., `user_id` where one user has 1M events vs 10 for others).
    **反模式**：使用分佈不均的 Key 進行分組（例如 `user_id`，某個使用者有 100 萬個事件，而其他人只有 10 個）。
*   **Consequence**: One worker gets overloaded while others sit idle. The pipeline slows down to the speed of the slowest worker.
    **後果**：一個 worker 過載，而其他 worker 閒置。管線速度被最慢的 worker 拖累。
*   **Solution**: Enable `Fanout` in aggregations or add a random salt to the key for partial aggregation.
    **解法**：在聚合時啟用 `Fanout`，或在 Key 中加入隨機鹽（Salt）進行部分聚合。

### 5.3 Using `Streaming Inserts` instead of `Storage Write API`
### 5.3 使用 `Streaming Inserts` 而非 `Storage Write API`

*   **Anti-pattern**: Using the legacy `tabledata.insertAll` API for high-volume ingestion.
    **反模式**：使用舊版的 `tabledata.insertAll` API 進行大量資料寫入。
*   **Consequence**: Higher costs (charged per GB ingested) and lower throughput limits.
    **後果**：成本較高（按寫入 GB 收費）且吞吐量限制較低。
*   **Solution**: Use the **BigQuery Storage Write API**. It's cheaper (often 50% less) and supports exactly-once semantics with stream offsets.
    **解法**：使用 **BigQuery Storage Write API**。它更便宜（通常節省 50%）並支援基於串流 offset 的精確一次語意。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle duplicate messages in a Pub/Sub + Dataflow pipeline?
### Q1: 你如何在 Pub/Sub + Dataflow 管線中處理重複訊息？

*   **Key Points**:
    *   Acknowledge that Pub/Sub is "at-least-once".
    *   **Dataflow side**: Dataflow provides "exactly-once" processing semantics by using checkpointing and deduping against internal state (for a certain time window).
    *   **Sink side**: If writing to an external API (non-idempotent), duplicates can still happen. If writing to BigQuery, use deterministic IDs to deduplicate downstream or use Storage Write API streams.
*   **回答要點**：
    *   承認 Pub/Sub 是「至少一次（at-least-once）」傳遞。
    *   **Dataflow 端**：Dataflow 透過 Checkpoint 與內部狀態去重（在特定時間視窗內），提供「精確一次（exactly-once）」處理語意。
    *   **接收端（Sink）**：若寫入外部 API（非冪等），仍可能發生重複。若寫入 BigQuery，可使用確定性 ID 在下游去重，或使用 Storage Write API streams。

### Q2: Explain the difference between Watermark and Allowed Lateness. When is data dropped?
### Q2: 解釋 Watermark（浮水印）與 Allowed Lateness（允許延遲）的差異。資料何時會被丟棄？

*   **Key Points**:
    *   **Watermark**: System's guess that "no data older than time X will arrive". Triggers the main window result.
    *   **Allowed Lateness**: A grace period *after* the watermark passes. Data arriving here triggers a "Late Firing" (correction).
    *   **Dropped**: Data arriving *after* Watermark + Allowed Lateness is dropped (unless directed to a side output/DLQ).
*   **回答要點**：
    *   **Watermark**：系統推測「不會再有早於時間 X 的資料到達」。觸發主視窗結果。
    *   **Allowed Lateness**：浮水印通過*後*的寬限期。在此期間到達的資料會觸發「延遲觸發（Late Firing）」（修正結果）。
    *   **丟棄**：晚於「Watermark + Allowed Lateness」到達的資料會被丟棄（除非導向 Side Output/DLQ）。

### Q3: We need strict ordering for events (e.g., bank transactions). Pub/Sub doesn't guarantee order. What do we do?
### Q3: 我們需要嚴格的事件順序（例如銀行交易）。Pub/Sub 不保證順序。該怎麼做？

*   **Key Points**:
    *   Use **Pub/Sub Ordering Keys**. Messages with the same key are delivered in order to the same subscriber.
    *   Trade-off: Limits parallelism (processed sequentially per key).
    *   Alternative: Reorder in Dataflow using stateful processing (complex and memory-intensive).
*   **回答要點**：
    *   使用 **Pub/Sub Ordering Keys**。具有相同 Key 的訊息會依序傳遞給同一個訂閱者。
    *   權衡：限制了平行處理能力（每個 Key 必須循序處理）。
    *   替代方案：在 Dataflow 中使用有狀態處理（Stateful Processing）進行重新排序（複雜且消耗記憶體）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
### 關鍵摘要

1.  **Pub/Sub is the Buffer**: Use it to decouple services and absorb traffic spikes.
    **Pub/Sub 是緩衝區**：用它來解耦服務並吸收流量尖峰。
2.  **Dataflow Unifies Batch/Stream**: Design pipelines assuming data is infinite; batch is just a bounded stream.
    **Dataflow 統一批次/串流**：設計管線時假設資料是無限的；批次只是有邊界的串流。
3.  **Time Matters**: Distinguish between **Event Time** (correctness) and **Processing Time** (latency). Use Watermarks to manage this.
    **時間很重要**：區分**事件時間**（正確性）與**處理時間**（延遲）。使用 Watermarks 來管理。
4.  **Storage Write API**: The modern standard for BigQuery ingestion (cheaper, exactly-once support).
    **Storage Write API**：BigQuery 寫入的現代標準（更便宜、支援精確一次）。
5.  **Handling Failures**: Always implement Dead Letter Queues (DLQ) for unprocessable messages to avoid blocking the pipeline.
    **處理故障**：務必為無法處理的訊息實作死信佇列（DLQ），以免阻塞管線。

### Next Steps
### 後續延伸

*   **Advanced Dataflow**: Study **Stateful Processing** in Apache Beam for complex event patterns (e.g., "Alert if 3 failures in 5 minutes").
    **進階 Dataflow**：研究 Apache Beam 中的**有狀態處理（Stateful Processing）**，以應對複雜事件模式（例如「5 分鐘內失敗 3 次則發出警報」）。
*   **Cost Optimization**: Deep dive into BigQuery **Flex Slots** and Dataflow **Prime** for cost management.
    **成本優化**：深入研究 BigQuery **Flex Slots** 與 Dataflow **Prime** 以進行成本管理。
*   **Next Chapter Preview**: We will explore **GKE & Service Mesh**, moving from data pipelines to microservices orchestration.
    **下一章預告**：我們將探討 **GKE 與 Service Mesh**，從資料管線轉向微服務編排。