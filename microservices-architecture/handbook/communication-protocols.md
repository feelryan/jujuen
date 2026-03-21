# 服務間通訊模式與協議決策 / Inter-service Communication Patterns & Protocols

## Mental model｜心智模型

在微服務架構中，選擇通訊協議不僅僅是技術選型（REST vs gRPC），更是對 **「耦合（Coupling）」** 與 **「可用性（Availability）」** 的權衡。

請建立以下的心智模型：

1.  **電話 vs. 電子郵件 (Phone Call vs. Email)**：
    *   **同步通訊 (Synchronous, e.g., REST/gRPC)** 就像打電話。你需要對方當下有空接聽（Available），且雙方必須同時在線。如果對方不接，你的流程就卡住了（Blocking）。這造成了 **時間耦合 (Temporal Coupling)**。
    *   **非同步通訊 (Asynchronous, e.g., RabbitMQ/Kafka)** 就像寄 Email。你寄出後就可以去做別的事，對方有空時會處理。這解除了時間耦合，提高了系統的整體韌性。

2.  **聰明的端點，單純的管線 (Smart Endpoints, Dumb Pipes)**：
    *   不要在通訊機制（Pipe）中加入過多業務邏輯（如 ESB 時代的做法）。保持傳輸層單純，將路由與處理邏輯放在服務（Endpoint）內部。

3.  **網路是不可靠的 (The Network is Unreliable)**：
    *   永遠假設網路會斷、封包會掉、請求會超時。所有的通訊設計都必須包含「重試（Retry）」、「逾時（Timeout）」與「斷路器（Circuit Breaker）」機制。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 決策矩陣：同步 vs. 非同步 (Decision Matrix: Sync vs. Async)

*   **使用同步 (REST/gRPC) 的時機**：
    *   **外部請求 (External Request)**：前端 UI 等待回應。
    *   **簡單查詢 (Simple Query)**：需要即時取得最新資料，且該資料由單一服務擁有。
    *   **強一致性需求**：操作必須立即確認成功或失敗。
*   **使用非同步 (Messaging) 的時機**：
    *   **狀態變更 (State Change)**：如「建立訂單」後觸發的「扣庫存」、「寄信」、「通知物流」。
    *   **削峰填谷 (Load Leveling)**：當請求量大於處理能力時（如搶購活動），先寫入 Queue。
    *   **解耦服務**：發送者不需要知道誰會消費這則訊息。

### 2. 協議選擇 (Protocol Selection)

*   **REST (JSON/HTTP)**：
    *   *Pros*: 通用性高、除錯容易（人類可讀）、生態系成熟。
    *   *Cons*: 傳輸體積大（JSON verbose）、序列化效能較差。
    *   *Best Practice*: 用於對外 API (Public API) 或服務間的非頻繁通訊。
*   **gRPC (Protobuf/HTTP2)**：
    *   *Pros*: 極高效能、強型別契約 (Strict Contract)、支援雙向串流。
    *   *Cons*: 瀏覽器支援度有限（需 gRPC-Web）、除錯需特定工具。
    *   *Best Practice*: 用於內部服務間的高頻通訊 (Internal Service-to-Service)。

### 3. 冪等性設計 (Idempotency Design)

這是分散式通訊中最關鍵的實務。由於網路不穩導致的重試（Retry），服務 **必須** 能處理重複的請求而不產生副作用。

*   **實作方式**：
    *   **Idempotency Key**：Client 端生成唯一的 UUID（如 `X-Request-ID` 或 `Idempotency-Key`），隨請求發送。
    *   **Deduplication Table**：Server 端收到請求先查表（Redis 或 DB），若 Key 已存在且處理過，直接回傳上次的結果，不執行業務邏輯。
    *   **At-Least-Once Delivery**：Message Queue 通常保證「至少送達一次」，因此 Consumer 務必實作冪等性。

### 4. Transactional Outbox Pattern

解決「寫入資料庫」與「發送訊息」無法原子化（Atomic）的問題。

*   **問題**：訂單存入 DB 成功，但發送 Message 到 Broker 失敗（或反之）。
*   **解法**：
    1.  在同一個 DB Transaction 中，將業務資料與「待發送訊息 (Outbox Event)」寫入同一資料庫。
    2.  由另一個獨立 Process (Message Relay) 讀取 Outbox 表，發送到 Message Broker。
    3.  發送成功後刪除 Outbox 紀錄。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分散式單體 (Distributed Monolith)
*   **現象**：服務 A 呼叫 B，B 呼叫 C，C 呼叫 D。這是一條長長的同步呼叫鏈 (Sync Chain)。
*   **後果**：
    *   **延遲疊加 (Latency Addition)**：總延遲 = A+B+C+D。
    *   **可用性降低**：任何一個環節掛掉，整個請求失敗。
*   **修正**：改用 Event-Driven 架構，A 發出事件，B、C、D 訂閱並平行處理。

### 2. 把資料庫當作 Queue (Database as a Queue)
*   **現象**：多個服務輪詢 (Polling) 同一個資料庫表來溝通。
*   **後果**：資料庫鎖定競爭嚴重，效能低落，且難以擴展。
*   **修正**：使用真正的 Message Broker (RabbitMQ, Kafka, SQS)。

### 3. 缺乏契約管理 (Lack of Contract Management)
*   **現象**：Producer 修改了訊息格式（例如改欄位名），導致所有 Consumers 崩潰。
*   **修正**：
    *   使用 **Schema Registry** (如 Confluent Schema Registry)。
    *   遵守 **Consumer-Driven Contracts (CDC)** 測試。
    *   Protocol Buffers 的向後相容性設計。

### 4. 忽略訊息順序 (Ignoring Message Ordering)
*   **現象**：假設「訂單建立」一定比「訂單付款」先到。但在分散式系統中，訊息可能會亂序到達。
*   **修正**：
    *   設計不依賴順序的狀態機。
    *   若必須依賴順序，使用 Kafka 的 Partition Key 確保同一 ID 的訊息進入同一 Partition。

---

## Checklists & workflows｜檢查清單與流程

在設計新的服務間通訊時，請依序檢查：

### 決策流程 (Decision Workflow)

1.  **[ ] 互動性質**：這是「查詢 (Query)」還是「命令 (Command)」？
    *   Query -> 優先考慮 Sync (REST/gRPC)。
    *   Command -> 優先考慮 Async (Messaging)。
2.  **[ ] 容錯需求**：如果接收方掛了，發送方能否接受失敗？
    *   不能接受（必須最終成功） -> 使用 Message Queue + Retry。
    *   可以接受（直接回報錯誤給用戶） -> 使用 Sync + Circuit Breaker。

### 實作檢查清單 (Implementation Checklist)

- [ ] **Timeout 設定**：所有同步呼叫是否都設定了合理的 Timeout？（避免無限等待耗盡 Thread Pool）。
- [ ] **Retry 策略**：是否設定了 Exponential Backoff（指數退避）？避免瞬間流量打死剛重啟的服務。
- [ ] **Circuit Breaker**：是否配置了斷路器？（如 Resilience4j 或 Service Mesh 設定）。
- [ ] **Idempotency**：接收端是否處理了重複訊息？（DB Unique Constraint 或 Redis Key）。
- [ ] **Dead Letter Queue (DLQ)**：無法處理的訊息是否有地方去？有監控告警嗎？
- [ ] **Payload Size**：訊息體積是否過大？（大檔案請傳 S3 Link，不要傳 Base64）。
- [ ] **Tracing**：是否傳遞了 `Trace ID` (OpenTelemetry) 以便追蹤跨服務請求？

---

## Real-world examples｜實戰案例

### 案例：電商下單流程 (E-commerce Checkout)

#### ❌ 錯誤設計：全同步鏈條 (The Sync Trap)
```text
User -> [Order Service]
           |-> (Sync HTTP) -> [Inventory Service] (扣庫存)
           |-> (Sync HTTP) -> [Payment Service] (扣款)
           |-> (Sync HTTP) -> [Notification Service] (寄信)
```
*   **問題**：Email 服務掛掉導致訂單失敗；或者 Email 服務回應慢，導致使用者卡在 Loading 畫面。

#### ✅ 建議設計：混合模式 (Hybrid Approach)

1.  **同步階段 (Validation & Reservation)**
    *   User 呼叫 `Order Service`。
    *   `Order Service` 同步呼叫 `Inventory Service` 檢查並**預佔**庫存（確保有貨）。
    *   回應 User：「訂單處理中」。

2.  **非同步階段 (Fulfillment & Side Effects)**
    *   `Order Service` 發出 `OrderCreated` 事件到 Kafka。
    *   **Consumer A (Payment)**: 監聽事件 -> 執行扣款。
    *   **Consumer B (Notification)**: 監聽事件 -> 寄送確認信。
    *   **Consumer C (Analytics)**: 監聽事件 -> 更新銷售報表。

#### Code Snippet: 冪等性處理 (Python Pseudo-code)

```python
# Async Consumer handling "Deduct Money"
def handle_payment_event(event):
    order_id = event.get("order_id")
    
    # 1. Check Idempotency (Have we processed this?)
    if redis.exists(f"processed_payment:{order_id}"):
        logger.info(f"Skipping duplicate event for order {order_id}")
        return

    try:
        # 2. Business Logic
        payment_gateway.charge(event.amount)
        
        # 3. Mark as processed (Atomic if possible, or use DB transaction)
        redis.set(f"processed_payment:{order_id}", "true", ex=86400) # Expire in 1 day
        
    except Exception as e:
        # 4. Error Handling -> Retry or DLQ
        raise e 
```