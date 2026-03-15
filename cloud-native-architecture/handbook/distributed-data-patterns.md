# 分散式資料一致性與交易管理 / Distributed Data Consistency & Transaction Management

## Mental model｜心智模型

### From ACID to BASE: The Coffee Shop Analogy
在單體架構（Monolithic）中，我們依賴資料庫的 ACID 交易（All-or-Nothing）。但在雲原生架構下，跨服務的 ACID 交易（如 2PC/XA）是效能與可用性的殺手。

請將思維從 **「銀行金庫（Bank Vault）」** 轉變為 **「星巴克點餐流程（Coffee Shop Workflow）」**：

1.  **非同步與最終一致性 (Asynchronous & Eventual Consistency)**：
    收銀員（Order Service）收錢後，會給你一張收據並呼叫吧台（Kitchen Service）。此時你的咖啡還沒做好，但訂單已經成立。這就是 **BASE** (Basically Available, Soft state, Eventual consistency)。
2.  **補償機制 (Compensation)**：
    如果吧台發現牛奶沒了（Inventory Check Failed），他們不會讓時光倒流（Rollback），而是會發動一個「退款」動作（Compensating Transaction）。
3.  **狀態機思維 (State Machine Thinking)**：
    分散式交易不再是一個瞬間的動作，而是一個**長壽命的流程 (Long-lived Process)**。每一個聚合（Aggregate）都應該有一個明確的狀態欄位（如 `PENDING`, `CONFIRMED`, `REJECTED`）。

> **Key Takeaway**: Don't try to force strong consistency across boundaries. Accept the lag, design for failure, and manage state transitions explicitly.
> 不要試圖在邊界之間強求強一致性。接受延遲，為失敗而設計，並明確管理狀態轉換。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Saga Pattern: Orchestration vs. Choreography
Saga 是解決長流程交易的標準解法，分為兩種流派：

*   **編排式 (Orchestration)**：
    *   **How**: 有一個中心的 Orchestrator（如 Temporal, Camunda, AWS Step Functions）指揮每個服務做什麼。
    *   **Use Case**: 複雜的業務流程，涉及超過 4 個以上的服務，需要清楚的狀態可視化。
    *   **Pros**: 流程邏輯集中，容易除錯。
*   **編舞式 (Choreography)**：
    *   **How**: 服務之間透過 Event Bus (Kafka/RabbitMQ) 互相監聽事件。Service A 發出 `OrderCreated`，Service B 聽到後執行扣庫存。
    *   **Use Case**: 簡單的流程（2-3 個服務），希望低耦合。
    *   **Pros**: 沒有單點依賴，服務更獨立。

### 2. Transactional Outbox Pattern (必備模式)
這是最常被忽略但最重要的模式。
**問題**：你的程式碼先寫入 DB，然後發送 Event 到 Kafka。如果寫入 DB 成功但發送 Event 失敗（網路斷線、Process Crash）怎麼辦？資料將不一致。
**解法**：
1.  在同一個 DB Transaction 中，將業務資料與 Event 資料寫入一張 `Outbox` 資料表。
2.  由一個獨立的 Process (Relay) 讀取 `Outbox` 表並發送到 Message Broker。
3.  發送成功後刪除 `Outbox` 紀錄。

### 3. Idempotency (冪等性)
在分散式系統中，網路重試（Retry）是常態。
*   **Rule**: 所有的寫入 API 與 Event Consumer 都必須支援冪等性。
*   **Implementation**: 使用 `idempotency_key` 或業務上的唯一 ID（如 `order_id`）。如果收到重複的 ID，直接回傳上次成功的結果，而不重複執行邏輯。

### 4. CQRS (Command Query Responsibility Segregation)
當寫入模型（Write Model）被拆分到多個微服務後，如何執行「查詢所有訂單詳情」？
*   **Practice**: 建立一個獨立的 Read Model 服務，訂閱各個服務的 Domain Events，將資料聚合到一個適合查詢的資料庫（如 Elasticsearch 或 Denormalized SQL Table）中。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Distributed Transactions over HTTP (REST chain)
*   **Anti-pattern**: Service A 呼叫 Service B，B 呼叫 C，C 呼叫 D。全部同步等待。
*   **Consequence**: 延遲疊加（Latency adds up），可用性驟降（Availability = A% * B% * C% * D%）。任何一個環節斷掉，整個請求失敗且難以回滾。

### 2. Two-Phase Commit (2PC / XA)
*   **Anti-pattern**: 試圖在微服務間使用資料庫層級的 2PC。
*   **Consequence**: 鎖定資源時間過長，嚴重影響吞吐量（Throughput），且不支援現代 Cloud DB (如 DynamoDB, MongoDB Atlas 等多數受管服務對 XA 支援有限或效能極差)。

### 3. Assuming "Happy Path" Only
*   **Anti-pattern**: 實作 Saga 時只寫了正向流程，沒有實作 `Compensating Transaction`（補償邏輯）。
*   **Consequence**: 當庫存扣減失敗時，訂單狀態卡在 `PENDING`，且使用者已經付款，導致嚴重的客訴與資料修復成本。

### 4. Lack of Observability in Transactions
*   **Anti-pattern**: 沒有統一的 `Trace ID` 或 `Correlation ID` 貫穿整個非同步流程。
*   **Consequence**: 當資料不一致發生時，無法跨服務追蹤是哪一個 Event 遺失或處理失敗。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the Consistency Strategy
在設計新功能時，請依序回答：
1.  **能否將相關資料放在同一個服務內？**
    *   Yes -> 使用單機 ACID Transaction (最簡單，推薦)。
    *   No -> 進入下一步。
2.  **業務是否允許短暫的資料不一致？**
    *   No (如即時轉帳顯示餘額) -> 考慮重新劃分服務邊界或使用 2PC (極少見，慎用)。
    *   Yes -> 進入下一步。
3.  **流程是否複雜（>3 步驟）或需要人工介入？**
    *   Yes -> 使用 **Orchestration Saga** (e.g., Temporal)。
    *   No -> 使用 **Choreography Saga** (Event-driven)。

### Implementation Checklist
- [ ] **Idempotency**: 所有的 Consumer 是否都能處理重複的訊息而不產生副作用？
- [ ] **Outbox Pattern**: 是否確保了「本地 DB 寫入」與「訊息發送」的原子性？
- [ ] **Compensation**: 每個「寫入」操作是否都有對應的「復原」操作（Undo/Rollback logic）？
- [ ] **Dead Letter Queue (DLQ)**: 當訊息處理失敗且重試耗盡時，是否有機制儲存這些訊息並發送告警？
- [ ] **Monitoring**: 是否監控了「Saga 流程完成時間」與「Read Model 同步延遲 (Lag)」？
- [ ] **Reconciliation**: 是否有定期的對帳腳本（Reconciliation Job）來修復長期不一致的資料？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Order Placement (Saga - Choreography)

**Goal**: User places an order -> Deduct Inventory -> Charge Payment -> Confirm Order.

#### 1. Happy Path (Event Flow)
1.  **Order Service**: 建立訂單，狀態 `PENDING`。寫入 Outbox，發送 `OrderCreated` 事件。
2.  **Inventory Service**: 收到 `OrderCreated`。
    *   檢查庫存 -> 鎖定庫存。
    *   發送 `InventoryReserved` 事件。
3.  **Payment Service**: 收到 `InventoryReserved` (注意：它不直接聽 Order，而是聽 Inventory，這是 Choreography 的特徵之一，或者也可以都聽 Order，視設計而定)。
    *   執行扣款。
    *   發送 `PaymentSucceeded` 事件。
4.  **Order Service**: 收到 `PaymentSucceeded`。
    *   更新訂單狀態為 `CONFIRMED`。

#### 2. Failure Path (Compensation)
*   **情境**: Payment Service 扣款失敗（餘額不足）。
1.  **Payment Service**: 發送 `PaymentFailed` 事件。
2.  **Inventory Service**: 收到 `PaymentFailed`。
    *   **Compensation**: 解鎖/釋放剛才鎖定的庫存。
    *   發送 `InventoryReleased` 事件。
3.  **Order Service**: 收到 `PaymentFailed`。
    *   更新訂單狀態為 `CANCELLED`。
    *   通知使用者付款失敗。

#### 3. Pseudo-code: Transactional Outbox (SQL)

```sql
BEGIN;

-- 1. 執行業務邏輯
INSERT INTO orders (id, user_id, amount, status) 
VALUES ('ord_123', 'user_999', 100, 'PENDING');

-- 2. 寫入 Outbox (在同一個 Transaction 內)
INSERT INTO outbox (id, aggregate_type, aggregate_id, event_type, payload) 
VALUES (
  uuid_generate_v4(), 
  'ORDER', 
  'ord_123', 
  'OrderCreated', 
  '{"user_id": "user_999", "amount": 100}'
);

COMMIT;
-- 3. 另外有一個獨立的 Message Relay 程式會輪詢 outbox 表並推送到 Kafka
```