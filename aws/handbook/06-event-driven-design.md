# 非同步架構與事件驅動設計 / Asynchronous Architecture & Event-Driven Design

## Mental model｜心智模型

在進入 AWS 具體服務之前，你需要建立正確的「非同步」心智模型。傳統的單體架構或同步 API 呼叫像是「打電話」：你說一句，對方回一句，如果對方不接電話，流程就卡住了。

事件驅動架構（EDA）則像是「傳紙條」或「寄信」：
1.  **時間解耦 (Temporal Decoupling)**：發送者（Producer）不需要知道接收者（Consumer）現在是否有空。發送者只管把事件丟出去，任務就結束了。
2.  **空間解耦 (Spatial Decoupling)**：發送者不需要知道接收者是誰、在哪裡、有幾個。

在 AWS 的世界裡，我們有四種主要的「傳信管道」，請依照以下特徵來記憶：

*   **SQS (Simple Queue Service)**：**緩衝區 (Buffer)**。像是銀行的排隊紅龍。用來削峰填谷 (Load Leveling)，確保下游不會被沖垮。是一對一的（一個訊息通常只被一個 Consumer 處理）。
*   **SNS (Simple Notification Service)**：**大聲公 (Megaphone)**。像是廣播系統。用來做「扇出 (Fan-out)」，一個事件發生，多個系統同時收到通知（例如：發 Email、寫 Log、觸發 Lambda）。
*   **EventBridge**：**智慧路由器 (Smart Router)**。像是郵局的自動分信機。它能根據信封上的內容（JSON payload）決定這封信要給誰。它是現代 EDA 的核心，特別適合複雜的規則路由與 SaaS 整合。
*   **Kinesis Data Streams**：**錄影帶 (Stream)**。像是監視器錄影。資料是連續的流，且**有順序性**，可以隨時「倒帶」重播（Replay）。適合大數據分析與即時監控。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Fan-out Pattern (SNS/EventBridge + SQS)
這是 AWS EDA 中最黃金的組合模式。**永遠不要讓 SNS 或 EventBridge 直接觸發長時間運算的 Worker（如 EC2 或某些 Lambda），中間務必夾一個 SQS。**

*   **Why?** 如果下游掛了或處理變慢，SNS/EventBridge 的重試機制有限，訊息可能會遺失。加上 SQS 可以將訊息持久化保存，讓下游依照自己的步調消化 (Throttling)。
*   **Implementation:** `Producer -> SNS Topic -> SQS Queue -> Lambda/EC2 Consumer`

### 2. Idempotency (冪等性)
在分散式系統中，AWS 承諾的是 "At-least-once delivery"（至少傳送一次）。這意味著你的 Consumer **一定會**收到重複的訊息。

*   **Strategy:**
    *   **Business Key:** 使用訂單 ID、Transaction ID 作為唯一鍵。
    *   **Tracking:** 在處理前，先檢查 DynamoDB 或 Redis 是否已有該 ID 的處理紀錄。
    *   **Atomic Operation:** 使用 `ConditionExpression` (DynamoDB) 確保寫入是原子性的。
    *   *Pseudo-code:*
      ```python
      def handler(event):
          msg_id = event['id']
          if is_processed(msg_id):
              return "Already done"
          
          # Process logic...
          
          mark_as_processed(msg_id)
      ```

### 3. Claim Check Pattern (大型 Payload 處理)
SQS 和 SNS 都有訊息大小限制（通常是 256KB）。如果你要傳送一張圖片或一份大報告，不要把二進位檔塞進訊息裡。

*   **Pattern:**
    1.  把大檔案上傳到 S3。
    2.  S3 回傳一個 Reference (S3 Key / URL)。
    3.  把這個 Reference 放入 SQS/SNS 訊息中傳送。
    4.  Consumer 收到訊息後，拿著 Reference 去 S3 下載檔案處理。

### 4. Dead Letter Queue (DLQ) & Redrive Policy
永遠假設你的程式碼會有 Bug，或者接收到的資料格式會爛掉。

*   **Configuration:** 設定 SQS 的 `maxReceiveCount` (例如 3 次)。
*   **Workflow:** 當 Consumer 處理失敗拋出 Exception，SQS 會自動重試。超過 3 次後，SQS 會把訊息移到另一個專門的 Queue (DLQ)。
*   **Recovery:** 設定 CloudWatch Alarm 監控 DLQ。修復 Bug 後，使用 AWS Console 或 CLI 的 "Start DLQ Redrive" 功能將訊息送回主 Queue 重新處理。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤用 Kinesis 取代 SQS
*   **Pitfall:** 為了「順序性」而全面使用 Kinesis。
*   **Consequence:** Kinesis 的 Shard 管理複雜，Consumer 必須維護 Checkpoint，且擴展性（Scaling）不如 SQS 靈活。除非你需要「嚴格順序」或「重播能力」，否則 SQS FIFO 或 Standard SQS 往往更簡單省錢。

### 2. 分散式單體 (Distributed Monolith)
*   **Pitfall:** 雖然用了 EventBridge，但 Consumer A 處理完直接同步呼叫 Consumer B，且兩者共用同一個資料庫 Schema。
*   **Consequence:** 這只是把 Function Call 變成 Network Call，延遲變高且沒有獲得解耦的好處。真正的解耦應該是 Consumer 擁有自己的資料存儲。

### 3. 忽略 Lambda 的並發限制 (Concurrency Limits)
*   **Pitfall:** SQS 累積了 10,000 個訊息，Lambda 觸發器設定不當，導致 Lambda 瞬間啟動 1,000 個 instance。
*   **Consequence:** 下游資料庫（如 RDS）連線數爆滿被打掛。
*   **Fix:** 設定 Lambda 的 `Reserved Concurrency` 或 SQS 的 `Batch Size` 來控制流量。

### 4. 假設 SQS Standard 是先進先出
*   **Pitfall:** 預期 SQS Standard Queue 會嚴格按照發送順序給訊息。
*   **Consequence:** 訂單狀態錯亂（先收到「訂單完成」，才收到「訂單建立」）。
*   **Fix:** 如果順序至關重要，請使用 **SQS FIFO Queue**（注意 TPS 限制較低）或在應用層處理順序邏輯（例如檢查 Timestamp）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 選用哪個服務？
1.  **你需要一對多通知嗎？** (e.g., 訂單成立 -> 庫存, 發票, Email)
    *   Yes -> **SNS** 或 **EventBridge** (接著再接 SQS)
    *   No -> 往下一步
2.  **你需要嚴格的順序性或資料重播 (Replay) 嗎？**
    *   Yes (Replay/Real-time analytics) -> **Kinesis Data Streams**
    *   Yes (Strict Ordering only) -> **SQS FIFO**
    *   No -> **SQS Standard**
3.  **你需要根據訊息內容做複雜路由嗎？** (e.g., source="shopify" 走 A 路線, source="stripe" 走 B 路線)
    *   Yes -> **EventBridge**
    *   No -> **SNS**

### Production Readiness Checklist
- [ ] **DLQ 設定**：所有非同步觸發點（SQS, SNS, Lambda Async Invoke, EventBridge）都配置了 Dead Letter Queue。
- [ ] **冪等性實作**：Consumer 端實作了 Idempotency check，不依賴 "Exactly-once" 的幻想。
- [ ] **逾時設定 (Visibility Timeout)**：SQS 的 Visibility Timeout 必須大於 Lambda/Consumer 的 Timeout 設定（建議至少 6 倍）。
- [ ] **監控告警**：針對 `ApproximateAgeOfOldestMessage` (SQS 延遲) 和 `DLQ 訊息數量` 設定了 CloudWatch Alarm。
- [ ] **加密**：啟用 KMS Encryption (Server-side encryption) 保護敏感訊息。
- [ ] **清理機制**：如果是 Kinesis 或 DynamoDB Streams，確認 Retention Period 設定符合需求（預設 24h，可延長）。

---

## Real-world examples｜實戰案例

### Scenario 1: E-commerce Order Processing (訂單處理)
這是一個經典的 Fan-out + Decoupling 案例。

1.  **User Action**: 使用者點擊「結帳」。
2.  **API Gateway + Lambda**: 接收請求，將訂單寫入 DB (Pending)，並發送事件 `OrderCreated` 到 **EventBridge**。
3.  **EventBridge Rules**:
    *   Rule A: 轉發到 **SQS (InventoryQueue)** -> Lambda (扣庫存)。
    *   Rule B: 轉發到 **SQS (InvoiceQueue)** -> Lambda (開立發票)。
    *   Rule C: 轉發到 **SQS (NotificationQueue)** -> Lambda (發送 Email/SMS)。
4.  **Resilience**: 如果「發票系統」掛了，訊息會堆積在 `InvoiceQueue` 中，不會影響使用者收到「訂單成功」的 Email，也不會影響庫存扣減。

### Scenario 2: Webhook Handling from 3rd Party (第三方回調)
處理 Stripe 或 GitHub 的 Webhook，重點是快速回應與可靠性。

1.  **Ingestion**: API Gateway 接收 Stripe Webhook。
2.  **Buffer**: 直接將 Payload 丟入 **SQS**，並立刻回傳 `200 OK` 給 Stripe（避免 Stripe 認為超時而重試）。
3.  **Process**: 後端 Worker (Lambda/EC2) 從 SQS 拉取訊息，驗證簽章 (Signature)，並處理付款邏輯。
4.  **Error Handling**: 如果處理失敗，訊息進入 DLQ，工程師介入調查 Payload 是否異常。

### Scenario 3: User Clickstream Analytics (使用者行為分析)
需要處理高吞吐量且有順序的資料。

1.  **Collection**: 前端 App SDK 將使用者點擊事件發送到 **Kinesis Data Streams**。
2.  **Partitioning**: 使用 `UserId` 作為 Partition Key，確保同一個使用者的行為都在同一個 Shard 中（保證順序）。
3.  **Processing**: **Kinesis Data Firehose** 將資料批次寫入 S3 (Data Lake)。
4.  **Analytics**: 同時，另一個 Lambda 讀取 Kinesis Stream 進行即時分析（例如偵測異常登入），若發現異常則發送 **SNS** 告警。