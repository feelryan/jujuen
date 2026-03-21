# 分散式資料一致性模式 / Distributed Data Consistency Patterns

## Mental model｜心智模型

在單體架構（Monolith）中，我們依賴資料庫的 ACID 交易（Transactions）來保證世界的一致性。但在微服務架構下，資料分散在不同的服務與資料庫中，**跨服務的 ACID 交易（Distributed Transactions / 2PC）通常是效能殺手與可用性惡夢**。

因此，我們必須轉換思維：
**從「強一致性（Strong Consistency）」轉向「最終一致性（Eventual Consistency）」**。

### 核心思維轉變 / Key Mindset Shifts

1.  **接受暫時的不一致 (Embrace the Lag)**：
    系統在 T1 時間點狀態可能不一致，但在 T2 時間點會收斂至一致。你必須設計系統來容忍這個時間差。
    *Instead of "All or Nothing" instantly, think "Eventually Correct".*

2.  **補償取代回滾 (Compensation over Rollback)**：
    在分散式環境中，你無法簡單地 `ROLLBACK` 一個已經跨越網路邊界的請求。你必須執行一個「補償交易（Compensating Transaction）」來抵銷之前的操作（例如：退款以抵銷扣款）。

3.  **業務邏輯決定一致性需求 (Business Logic Dictates Consistency)**：
    並非所有數據都需要即時一致。庫存扣減可能需要較高的一致性，但「推薦系統的用戶標籤」可以容忍數分鐘的延遲。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Saga Pattern：長流程交易管理
Saga 是一組有序的本地交易（Local Transactions）。如果某個步驟失敗，Saga 會執行一系列的補償交易來還原變更。

#### A. Choreography-based Saga (協作式 / 事件驅動)
服務之間透過訂閱事件（Events）來觸發下一步驟。沒有中央協調者。

*   **適用場景**：簡單流程（2-4 個步驟）、參與者較少。
*   **優點**：低耦合、去中心化。
*   **缺點**：流程邏輯分散在各處，難以追蹤完整業務狀態（"Who listens to what?" hell）。

#### B. Orchestration-based Saga (編排式 / 指揮官)
引入一個中央協調者（Orchestrator，通常是一個 State Machine），告訴每個服務該做什麼，並處理失敗與超時。

*   **適用場景**：複雜流程、多個補償步驟、需要清楚的狀態可視化。
*   **優點**：流程邏輯集中，易於監控與測試。
*   **缺點**：協調者可能成為單點瓶頸（如果設計不當），增加了額外的基礎設施複雜度（如使用 AWS Step Functions, Cadence, Temporal）。

### 2. Transactional Outbox Pattern：解決「雙寫」問題
**這是最關鍵但最常被忽略的模式。**
當你需要「寫入資料庫」**並且**「發送事件到 Message Broker」時，如果分開做（Dual Write），其中一個失敗會導致資料不一致。

*   **做法**：
    1.  在同一個 DB Transaction 中，將業務資料寫入 Table，並將事件 payload 寫入一個 `Outbox` Table。
    2.  由一個獨立的 Process（Message Relay）讀取 `Outbox` Table 並發送到 Kafka/RabbitMQ。
    3.  發送成功後刪除或標記 `Outbox` 記錄。
*   **Benefit**: Guarantees "At-Least-Once" delivery.

### 3. Idempotency (冪等性)
由於網路不可靠或 Outbox 模式的重試機制，消費者（Consumer）可能會收到重複的訊息。
*   **實作**：每個寫入操作都必須檢查 `MessageID` 或 `CorrelationID` 是否已經處理過。
*   **Rule**: `f(f(x)) = f(x)`. Retrying a payment request should not charge the user twice.

### 4. CQRS (Command Query Responsibility Segregation)
為了解決跨服務 Join 的困難，將讀寫分離。
*   **Write Model**: 處理複雜的業務邏輯與驗證。
*   **Read Model**: 訂閱 Write Model 發出的事件，建立專門為了查詢優化的 View（可能是 NoSQL 或 ElasticSearch）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Dual Write" Trap (雙寫陷阱)
❌ **Anti-pattern**:
```javascript
await db.save(order);
await kafkaProducer.send('order-created', order); // 如果這裡失敗，DB 已經 commit，系統狀態就不一致了
```
✅ **Fix**: 使用 **Transactional Outbox** 或 **Change Data Capture (CDC)** 工具（如 Debezium）。

### 2. Distributed Transactions (2PC / XA)
❌ **Anti-pattern**: 試圖在微服務間使用 Two-Phase Commit 協議。
*   **後果**：極高的鎖定成本（Locking）、效能低落、單點故障導致整個系統停擺。除非是銀行核心轉帳等極端場景，否則應避免。

### 3. Assuming "Happy Path" Only (忽略補償設計)
❌ **Anti-pattern**: 設計 Saga 時只考慮成功路徑，未定義每個步驟對應的「補償邏輯」。
*   **後果**：當流程在中間失敗，系統留下「髒數據」（如：庫存被扣住但訂單已取消）。

### 4. Synchronous HTTP Chains for Writes (同步 HTTP 鏈式呼叫)
❌ **Anti-pattern**: Service A -> Service B -> Service C (全部同步等待)。
*   **後果**：延遲疊加（Latency accumulation）、可用性降低（Availability = A * B * C）。若 C 失敗，A 如何回滾 B？這會讓一致性極難處理。

---

## Checklists & workflows｜檢查清單與流程

在設計一個跨服務的寫入操作時，請使用此決策樹與清單：

### Decision Workflow: Saga Strategy
1.  **Is the flow simple (<= 3 steps)?**
    *   Yes -> Consider **Choreography** (Events).
    *   No -> Use **Orchestration** (State Machine).
2.  **Does it require ACID-like isolation?**
    *   Yes -> Can you merge these services back into a monolith? Or use Semantic Locking (e.g., `PENDING` state)?
    *   No -> Proceed with Eventual Consistency.

### Implementation Checklist
- [ ] **Idempotency**: 所有接收事件的 Consumer 是否都實作了冪等性檢查？（例如使用 Redis 紀錄已處理的 Event ID）。
- [ ] **Outbox Pattern**: 是否避免了直接在程式碼中同時寫 DB 和發送 Message？
- [ ] **Dead Letter Queue (DLQ)**: 當事件處理失敗且重試耗盡時，是否有 DLQ 機制？是否有監控告警？
- [ ] **Compensation Logic**: 每個會改變狀態的步驟，是否有對應的補償邏輯（Undo）？
- [ ] **Observability**: 是否有 Trace ID 貫穿整個 Saga 流程？能否在 Log 中看到完整的交易路徑？
- [ ] **Timeout Handling**: 如果某個服務沒回應，Saga 是否有超時機制來觸發回滾？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Order Fulfillment (電商訂單履行)

**目標**：使用者下單 -> 扣減庫存 -> 扣款 -> 建立物流單。

#### 1. Orchestration Saga Design (Recommended for this complexity)

我們建立一個 `Order Orchestrator` (Service) 來管理狀態。

1.  **Order Service**: 接收 `CreateOrder` 請求。
    *   Action: 建立訂單，狀態 `PENDING`。
    *   Event: `OrderCreated` (via Outbox).
2.  **Orchestrator**: 監聽 `OrderCreated`，啟動 Saga。
    *   **Step 1**: 發送 `ReserveStock` Command 到 **Inventory Service**。
3.  **Inventory Service**:
    *   Success: 鎖定庫存，回覆 `StockReserved`。
    *   Failure: 回覆 `OutOfStock` -> Orchestrator 觸發 `RejectOrder`。
4.  **Orchestrator**: 收到 `StockReserved`。
    *   **Step 2**: 發送 `ProcessPayment` Command 到 **Payment Service**。
5.  **Payment Service**:
    *   Success: 扣款成功，回覆 `PaymentProcessed`。
    *   Failure: 餘額不足，回覆 `PaymentFailed` -> **Orchestrator 觸發補償流程**：
        *   發送 `ReleaseStock` 到 Inventory Service。
        *   發送 `CancelOrder` 到 Order Service。
6.  **Orchestrator**: 收到 `PaymentProcessed`。
    *   **Step 3**: 發送 `ApproveOrder` 到 Order Service (狀態改為 `CONFIRMED`)。

#### 2. Outbox Table Structure Example

在 **Order Service** 的資料庫中：

```sql
-- Transaction Start
INSERT INTO orders (id, user_id, status, total) VALUES ('ord-123', 'u-1', 'PENDING', 100);

INSERT INTO outbox (id, aggregate_type, aggregate_id, type, payload, created_at)
VALUES (
  uuid(),
  'ORDER',
  'ord-123',
  'OrderCreated',
  '{"orderId": "ord-123", "userId": "u-1", "total": 100}',
  NOW()
);
-- Transaction Commit
```

*之後由一個獨立的 Poller 程式（如 Kafka Connect 或自製 Go/Java Service）讀取 `outbox` table 並發送到 Message Broker。*