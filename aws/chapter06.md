# Chapter 06: Asynchronous Architecture & Event-Driven Design
# 第六章：非同步架構與事件驅動設計

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In modern distributed systems, synchronous communication (like HTTP REST calls) often becomes a bottleneck for scalability and reliability. As a Senior Engineer, mastering asynchronous patterns is crucial for building resilient systems that can handle traffic spikes and partial failures without cascading crashes. This chapter focuses on the AWS ecosystem's core messaging services: SQS, SNS, Kinesis, and EventBridge.

在現代分散式系統中，同步通訊（如 HTTP REST 呼叫）往往成為擴展性與可靠性的瓶頸。作為資深工程師，掌握非同步模式對於建構具備彈性的系統至關重要，這能確保系統在流量激增或部分故障時，不會發生連鎖崩潰。本章將聚焦於 AWS 生態系中的核心訊息服務：SQS、SNS、Kinesis 與 EventBridge。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Select the Right Service**: Definitively choose between SQS, SNS, Kinesis, and EventBridge based on requirements like ordering, throughput, and routing complexity.
    **精準選型**：根據順序性、吞吐量與路由複雜度等需求，在 SQS、SNS、Kinesis 與 EventBridge 之間做出明確選擇。
2.  **Implement Decoupling Patterns**: Apply patterns like "Fan-out" and "Queue-based Load Leveling" to protect downstream services.
    **實作解耦模式**：應用「扇出（Fan-out）」與「佇列負載調節（Queue-based Load Leveling）」等模式來保護下游服務。
3.  **Handle Failures Gracefully**: Design robust error handling mechanisms using Dead Letter Queues (DLQ) and Redrive Policies.
    **優雅處理故障**：利用死信佇列（DLQ）與重驅策略（Redrive Policy）設計強健的錯誤處理機制。
4.  **Guarantee Idempotency**: Understand why AWS messaging services guarantee "at-least-once" delivery and how to handle duplicates in your application logic.
    **確保冪等性**：理解為何 AWS 訊息服務保證「至少傳送一次（at-least-once）」，並學會如何在應用程式邏輯中處理重複訊息。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Synchronous vs. Asynchronous
### 2.1 同步 vs. 非同步

**Mental Model**: Think of a **Synchronous** call as a phone call. You speak, and you must wait on the line for the other person to respond. If they don't answer, you hang up (timeout). **Asynchronous** communication is like sending an email or a Slack message. You send it and move on to other tasks. The recipient processes it when they are ready.

**心智模型**：將 **同步（Synchronous）** 呼叫想像成打電話。你說話後，必須在線上等待對方回應。如果對方不接，你就掛斷（timeout）。**非同步（Asynchronous）** 通訊則像寄電子郵件或傳 Slack 訊息。你發送後即可繼續處理其他工作，接收者會在方便時處理該訊息。

### 2.2 The AWS Messaging Quartet
### 2.2 AWS 訊息服務四重奏

To navigate AWS messaging, map the services to these distinct roles:
要在 AWS 訊息服務中導航，請將這些服務對應到以下角色：

1.  **Amazon SQS (Simple Queue Service)**:
    *   **Role**: The Buffer / Load Leveler.
    *   **Model**: Point-to-Point (1:1). Producers push, Consumers **pull**.
    *   **Key Trait**: Decouples the speed of the producer from the consumer.
    *   **角色**：緩衝區 / 負載調節器。
    *   **模型**：點對點（1:1）。生產者推送，消費者 **拉取（Pull）**。
    *   **關鍵特質**：解耦生產者與消費者的處理速度。

2.  **Amazon SNS (Simple Notification Service)**:
    *   **Role**: The Megaphone / Broadcaster.
    *   **Model**: Publish/Subscribe (1:N). Producers publish, SNS **pushes** to subscribers.
    *   **Key Trait**: High throughput, simple filtering, connects to SQS/Lambda/HTTP/SMS.
    *   **角色**：擴音器 / 廣播者。
    *   **模型**：發布/訂閱（1:N）。生產者發布，SNS **推送（Push）** 給訂閱者。
    *   **關鍵特質**：高吞吐量，簡單過濾，可連接 SQS/Lambda/HTTP/SMS。

3.  **Amazon Kinesis Data Streams**:
    *   **Role**: The Time-Series Recorder.
    *   **Model**: Stream Processing. Real-time data ingestion.
    *   **Key Trait**: **Ordered** (within a shard), replayable (data persists for X days), supports multiple consumers reading the same stream at different positions.
    *   **角色**：時間序列記錄器。
    *   **模型**：串流處理。即時資料攝取。
    *   **關鍵特質**：**有序**（在分片 Shard 內），可重播（資料保留 X 天），支援多個消費者在不同位置讀取同一串流。

4.  **Amazon EventBridge**:
    *   **Role**: The Smart Router / Enterprise Service Bus.
    *   **Model**: Event Bus.
    *   **Key Trait**: Complex content-based routing, schema registry, deep integration with SaaS (Salesforce, Zendesk) and AWS services.
    *   **角色**：智慧路由器 / 企業服務匯流排。
    *   **模型**：事件匯流排（Event Bus）。
    *   **關鍵特質**：複雜的內容路由，Schema Registry，與 SaaS（Salesforce, Zendesk）及 AWS 服務深度整合。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production environment, you rarely use these services in isolation. They are the glue that holds microservices together.
在 Production 環境中，你很少單獨使用這些服務。它們是將微服務黏合在一起的膠水。

### 3.1 The "Fan-out" Pattern (SNS + SQS)
### 3.1 「扇出」模式（SNS + SQS）

**Scenario**: An e-commerce system where a user places an order.
**Architecture**:
1.  Order Service publishes an `OrderCreated` event to an **SNS Topic**.
2.  Multiple **SQS Queues** subscribe to this topic:
    *   `FulfillmentQueue` (for the warehouse system).
    *   `EmailQueue` (for sending confirmation emails).
    *   `AnalyticsQueue` (for data warehousing).

**Why this matters**:
*   **Reliability**: If the Email service goes down, the `EmailQueue` accumulates messages. The Warehouse service continues unaffected. No data is lost.
*   **Extensibility**: Adding a new "Loyalty Points Service" simply requires adding a new queue and subscription. No code changes in the Order Service.

**場景**：電子商務系統中，使用者下訂單。
**架構**：
1.  訂單服務發布一個 `OrderCreated` 事件到 **SNS Topic**。
2.  多個 **SQS Queues** 訂閱此主題：
    *   `FulfillmentQueue`（給倉儲系統）。
    *   `EmailQueue`（給發送確認信系統）。
    *   `AnalyticsQueue`（給資料倉儲）。

**重要性**：
*   **可靠性**：如果 Email 服務掛掉，`EmailQueue` 會累積訊息。倉儲服務不受影響繼續運作。資料不會遺失。
*   **可擴充性**：若要新增「會員點數服務」，只需新增一個 Queue 並訂閱即可。訂單服務的程式碼完全無需修改。

### 3.2 EventBridge for Cross-Account/SaaS Integration
### 3.2 EventBridge 用於跨帳號/SaaS 整合

**Scenario**: A compliance system needs to react when a specific AWS resource is modified in any AWS account within the organization, or when a ticket is updated in Zendesk.
**Design**: Use EventBridge. It has a default bus for AWS events (like `EC2 Instance State-change`) and supports partner event sources (SaaS). Its rule engine allows filtering JSON payloads (e.g., `{"detail": {"state": ["terminated"]}}`) without writing Lambda code to filter.

**場景**：合規系統需要在組織內任何 AWS 帳號修改特定資源時，或當 Zendesk 工單更新時做出反應。
**設計**：使用 EventBridge。它擁有預設的 Bus 處理 AWS 事件（如 `EC2 Instance State-change`），並支援合作夥伴事件來源（SaaS）。其規則引擎允許過濾 JSON payload（例如 `{"detail": {"state": ["terminated"]}}`），而無需撰寫 Lambda 程式碼來過濾。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Video Transcoding System
### 場景：影片轉檔系統

**Problem**: Users upload raw videos (100MB - 2GB). We need to convert them to 1080p, 720p, and generate a thumbnail.
**問題**：使用者上傳原始影片（100MB - 2GB）。我們需要將其轉檔為 1080p、720p 並產生縮圖。

#### Phase 1: Naive Approach (Synchronous)
#### 第一階段：天真做法（同步）

User uploads to API Server -> API Server runs `ffmpeg` locally -> Returns response.
使用者上傳至 API Server -> API Server 本地執行 `ffmpeg` -> 回傳回應。

*   **Failure**: Long processing time leads to HTTP timeouts. High CPU usage blocks other users.
*   **失敗點**：處理時間過長導致 HTTP timeout。高 CPU 使用率阻塞其他使用者。

#### Phase 2: Async with S3 Triggers (Lambda)
#### 第二階段：S3 觸發非同步（Lambda）

User uploads to S3 -> S3 Event Notification triggers Lambda.
使用者上傳至 S3 -> S3 事件通知觸發 Lambda。

*   **Limitation**: If 1,000 users upload at once, 1,000 Lambdas fire. You might hit account concurrency limits, throttling other critical functions. Retries are limited.
*   **限制**：若 1,000 人同時上傳，會觸發 1,000 個 Lambda。可能觸發帳號並發限制（Concurrency Limit），導致其他關鍵功能被節流（Throttling）。重試機制有限。

#### Phase 3: Robust Architecture (SQS + Lambda + DLQ)
#### 第三階段：強健架構（SQS + Lambda + DLQ）

**Flow**:
1.  User uploads to S3.
2.  S3 sends event to **SQS Queue**.
3.  **Lambda** polls SQS (with batch size).
4.  If processing fails 3 times, move message to **Dead Letter Queue (DLQ)**.

**流程**：
1.  使用者上傳至 S3。
2.  S3 發送事件至 **SQS Queue**。
3.  **Lambda** 輪詢 SQS（設定批次大小）。
4.  若處理失敗 3 次，將訊息移至 **死信佇列（DLQ）**。

**Why this works**:
*   **Backpressure**: You can control the Lambda concurrency (e.g., set `Reserved Concurrency` to 50). The queue buffers the surge.
*   **Visibility Timeout**: If a worker crashes mid-process, the message becomes visible again after the timeout for another worker to pick up.

**為何有效**：
*   **背壓（Backpressure）**：你可以控制 Lambda 的並發數（例如設定 `Reserved Concurrency` 為 50）。佇列會緩衝突波。
*   **能見度逾時（Visibility Timeout）**：若 Worker 在處理中途崩潰，訊息在逾時後會再次對其他 Worker 可見，得以被重新處理。

#### Code Snippet: Idempotent Consumer Logic (Python)
#### 程式碼片段：冪等消費者邏輯（Python）

Even with SQS, standard queues provide "at-least-once" delivery. Your code must handle duplicates.
即使使用 SQS，標準佇列提供的是「至少傳送一次」的保證。你的程式碼必須處理重複訊息。

```python
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DEDUPLICATION_TABLE'])

def process_message(record):
    message_id = record['messageId']
    video_id = record['body']['video_id']
    
    # 1. Check if already processed (Idempotency Check)
    # 1. 檢查是否已處理（冪等性檢查）
    if is_processed(message_id):
        print(f"Message {message_id} already processed. Skipping.")
        return

    try:
        # 2. Perform the heavy lifting
        # 2. 執行繁重工作
        transcode_video(video_id)
        
        # 3. Mark as processed
        # 3. 標記為已處理
        mark_as_processed(message_id)
        
    except Exception as e:
        # Let SQS retry logic handle this (don't catch and swallow unless necessary)
        # 讓 SQS 重試邏輯處理（除非必要，否則不要捕獲並吞掉錯誤）
        raise e

def is_processed(msg_id):
    resp = table.get_item(Key={'message_id': msg_id})
    return 'Item' in resp

def mark_as_processed(msg_id):
    # Use conditional write to prevent race conditions if needed
    # 若需要，使用條件寫入防止競爭條件
    table.put_item(Item={'message_id': msg_id, 'status': 'COMPLETED'})
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Overusing FIFO Queues
### 5.1 過度使用 FIFO 佇列

*   **Pitfall**: Using SQS FIFO queues by default because "order matters."
*   **Why it's bad**: FIFO queues have lower throughput limits (300/s or 3000/s with batching) compared to Standard queues (unlimited). They also cost more.
*   **Better Way**: Only use FIFO if causal ordering is strictly required (e.g., debit before credit). Often, you can design the system to be order-independent or handle ordering at the database level (using timestamps/versions).
*   **錯誤**：預設使用 SQS FIFO 佇列，只因為覺得「順序很重要」。
*   **壞處**：FIFO 佇列的吞吐量限制（300/s，批次可達 3000/s）遠低於標準佇列（無限）。且費用較高。
*   **解法**：僅在嚴格需要因果順序時使用（例如先扣款再入帳）。通常，你可以將系統設計為與順序無關，或在資料庫層級處理順序（使用時間戳/版本號）。

### 5.2 The "Large Payload" Trap
### 5.2 「巨大 Payload」陷阱

*   **Pitfall**: Sending base64 encoded images or large JSON blobs (>256KB) directly in SQS/SNS.
*   **Why it's bad**: Hits the service limit (256KB).
*   **Better Way**: **Claim Check Pattern**. Store the large payload in S3, and pass the S3 Object Key (reference) in the message body.
*   **錯誤**：直接在 SQS/SNS 中發送 base64 編碼的圖片或大型 JSON (>256KB)。
*   **壞處**：觸發服務限制（256KB）。
*   **解法**：**取物單模式（Claim Check Pattern）**。將大型 Payload 存入 S3，並在訊息內容中傳遞 S3 Object Key（參考指標）。

### 5.3 Ignoring Kinesis Iterator Age
### 5.3 忽略 Kinesis Iterator Age

*   **Pitfall**: Setting up Kinesis but not monitoring `IteratorAgeMilliseconds`.
*   **Why it's bad**: If your consumer is slower than the ingestion rate, the iterator age grows. If it exceeds the retention period (default 24h), data is lost forever.
*   **Better Way**: Scale consumers (increase shards + parallel processing) or optimize processing logic when Iterator Age spikes.
*   **錯誤**：設定了 Kinesis 但未監控 `IteratorAgeMilliseconds`。
*   **壞處**：若消費者處理速度慢於攝取速度，Iterator Age 會增加。一旦超過保留期限（預設 24 小時），資料將永久遺失。
*   **解法**：當 Iterator Age 飆升時，擴展消費者（增加 Shards + 平行處理）或優化處理邏輯。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: When would you choose Kinesis Data Streams over SQS?
### Q1: 你何時會選擇 Kinesis Data Streams 而非 SQS？

*   **Key Points**:
    *   **Routing**: SQS is for "Job Queues" (dispatch work to a worker). Kinesis is for "Data Ingestion/Analytics".
    *   **Consumption**: SQS deletes messages after processing (destructive). Kinesis allows multiple consumers to read the same stream independently (replayable).
    *   **Ordering**: Kinesis guarantees order within a shard. SQS Standard does not.
*   **關鍵點**：
    *   **路由**：SQS 用於「工作佇列」（分派工作給 Worker）。Kinesis 用於「資料攝取/分析」。
    *   **消費**：SQS 處理後刪除訊息（破壞性）。Kinesis 允許數個消費者獨立讀取同一串流（可重播）。
    *   **順序**：Kinesis 保證分片（Shard）內的順序。SQS 標準佇列則不保證。

### Q2: How do you handle a "Poison Pill" message in an SQS-Lambda architecture?
### Q2: 在 SQS-Lambda 架構中，你如何處理「毒丸（Poison Pill）」訊息？

*   **Key Points**:
    *   Define "Poison Pill": A message that crashes the consumer every time it's read.
    *   **Mechanism**: Use `maxReceiveCount` in the Redrive Policy.
    *   **Process**: After X failed attempts, SQS moves the message to a DLQ.
    *   **Recovery**: Set up an alarm on the DLQ depth. Investigate the message manually or fix the bug, then use "DLQ Redrive" to move it back to the source queue.
*   **關鍵點**：
    *   定義「毒丸」：每次讀取都會導致消費者崩潰的訊息。
    *   **機制**：使用重驅策略（Redrive Policy）中的 `maxReceiveCount`。
    *   **流程**：失敗 X 次後，SQS 將訊息移至 DLQ。
    *   **復原**：對 DLQ 深度設定警報。手動調查訊息或修復 Bug，然後使用「DLQ Redrive」將其移回來源佇列。

### Q3: Explain the difference between SNS and EventBridge.
### Q3: 請解釋 SNS 與 EventBridge 的差異。

*   **Key Points**:
    *   **SNS**: High throughput, low latency, simple "fan-out". Good for broadcasting to many subscribers (Email, SQS, SMS).
    *   **EventBridge**: Richer content filtering (rules), schema registry, third-party SaaS integration, scheduled events (cron). It's the modern choice for "Event Bus" architectures.
*   **關鍵點**：
    *   **SNS**：高吞吐量，低延遲，簡單的「扇出」。適合廣播給大量訂閱者（Email, SQS, SMS）。
    *   **EventBridge**：更豐富的內容過濾（規則），Schema Registry，第三方 SaaS 整合，排程事件（Cron）。它是「事件匯流排」架構的現代化選擇。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
1.  **Decoupling is King**: Use SQS to buffer bursts and protect downstream DBs/Services.
    **解耦為王**：使用 SQS 緩衝突波並保護下游資料庫/服務。
2.  **Fan-out Pattern**: SNS + SQS allows you to add new features without touching existing stable code.
    **扇出模式**：SNS + SQS 讓你在不觸碰現有穩定程式碼的情況下新增功能。
3.  **Idempotency**: Always assume messages will be delivered more than once. Handle duplicates at the application level.
    **冪等性**：永遠假設訊息會被傳送多次。在應用程式層級處理重複。
4.  **DLQ is Mandatory**: Never deploy an async system without a Dead Letter Queue strategy.
    **DLQ 是必須的**：永遠不要在沒有死信佇列策略的情況下部署非同步系統。
5.  **EventBridge for Logic, SNS for Volume**: Use EventBridge for complex routing rules; use SNS for high-volume broadcasting.
    **EventBridge 處理邏輯，SNS 處理量體**：複雜路由規則用 EventBridge；高量體廣播用 SNS。

### Next Steps (後續延伸)
*   **Study**: Deep dive into **AWS Lambda** execution models (Event Source Mapping) to understand how it polls SQS/Kinesis under the hood. (Next Chapter)
*   **Practice**: Implement the "Claim Check Pattern" using S3 and SQS with a Lambda trigger.
*   **Advanced**: Explore **Amazon MSK (Managed Kafka)** if you need Kinesis-like streaming but are already invested in the Kafka ecosystem.

*   **學習**：深入研究 **AWS Lambda** 執行模型（Event Source Mapping），了解其底層如何輪詢 SQS/Kinesis。（下一章）
*   **實作**：使用 S3 與 SQS 配合 Lambda 觸發器，實作「取物單模式（Claim Check Pattern）」。
*   **進階**：若你需要類 Kinesis 的串流功能但已投入 Kafka 生態系，探索 **Amazon MSK (Managed Kafka)**。