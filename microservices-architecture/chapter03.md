# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單體架構（Monolithic Architecture）中，ACID 交易（Transactions）是我們理所當然的依賴。然而，當我們轉向微服務架構並採用 **Database-per-service** 模式時，跨服務的資料一致性成為最棘手的挑戰之一。本章旨在幫助資深工程師從「強一致性」思維轉向「最終一致性」思維，並掌握實作分散式交易的具體模式。

In a Monolithic Architecture, ACID transactions are a luxury we often take for granted. However, as we shift to Microservices Architecture and adopt the **Database-per-service** pattern, cross-service data consistency becomes one of the most difficult challenges. This chapter aims to help senior engineers shift their mindset from "Strong Consistency" to "Eventual Consistency" and master specific patterns for implementing distributed transactions.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **清楚解釋為何 2PC (Two-Phase Commit) 在現代微服務中通常是反模式**，並能引用 CAP 定理或 PACELC 進行論證。
    **Clearly explain why 2PC (Two-Phase Commit) is often an anti-pattern in modern microservices**, using the CAP theorem or PACELC for argumentation.
2.  **設計並實作 Saga Pattern**，並能權衡 **Choreography（編排）** 與 **Orchestration（協調）** 的優缺點。
    **Design and implement the Saga Pattern**, weighing the trade-offs between **Choreography** and **Orchestration**.
3.  **理解並應用補償交易（Compensating Transactions）** 來處理業務邏輯失敗，確保系統最終回到一致狀態。
    **Understand and apply Compensating Transactions** to handle business logic failures, ensuring the system eventually returns to a consistent state.
4.  **識別冪等性（Idempotency）的重要性**，並在設計分散式交易時將其作為必要條件。
    **Identify the critical importance of Idempotency** and treat it as a prerequisite when designing distributed transactions.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Database-per-Service 的代價 (The Cost of Database-per-Service)

在微服務中，為了確保服務的鬆耦合（Loose Coupling）與獨立部署能力，我們遵循 **Database-per-service** 原則。這意味著服務 A 不能直接存取服務 B 的資料庫。
In microservices, to ensure loose coupling and independent deployability, we follow the **Database-per-service** principle. This means Service A cannot directly access Service B's database.

*   **直覺類比**：這就像公司裡的兩個不同部門（例如 HR 和 財務）。HR 部門有員工名單，財務部門有薪資帳戶。財務部不能直接翻閱 HR 的實體檔案櫃來修改資料，必須發送正式請求（API/Event），由 HR 部門自行處理。
*   **Intuitive Analogy**: It's like two different departments in a company (e.g., HR and Finance). HR holds employee records, and Finance holds payroll accounts. Finance cannot directly rummage through HR's physical filing cabinets to change data; they must send a formal request (API/Event), which HR processes internally.

這導致了兩個主要問題：
This leads to two main problems:
1.  **無法使用跨庫 JOIN**（這將在下一章 CQRS 討論）。
    **Inability to use cross-database JOINs** (to be discussed in the next chapter on CQRS).
2.  **無法使用單機 ACID 交易**來保證跨服務的操作原子性。
    **Inability to use local ACID transactions** to guarantee atomicity across services.

## 2.2 CAP 定理與 PACELC (CAP Theorem & PACELC)

資深工程師必須超越基礎的 CAP（Consistency, Availability, Partition Tolerance）理解。在分散式系統中，網路分區（P）是必然存在的，因此我們實際上是在 **Availability (A)** 與 **Consistency (C)** 之間做選擇。
Senior engineers must go beyond a basic understanding of CAP (Consistency, Availability, Partition Tolerance). In distributed systems, Partition Tolerance (P) is a given, so we are effectively choosing between **Availability (A)** and **Consistency (C)**.

更精確的模型是 **PACELC**：
A more precise model is **PACELC**:
*   如果有分區（**P**），則在 **A** 與 **C** 之間選擇。
    If there is a partition (**P**), choose between **A** and **C**.
*   如果沒有分區（**E**lse），則在 **L**atency（延遲）與 **C**onsistency（一致性）之間選擇。
    Else (**E**), choose between **L**atency and **C**onsistency.

微服務通常傾向於 **AP** 或 **EL**（低延遲），這意味著我們必須接受 **BASE** 模型：
Microservices usually lean towards **AP** or **EL** (Low Latency), meaning we must accept the **BASE** model:
*   **B**asically **A**vailable
*   **S**oft state
*   **E**ventual consistency

## 2.3 Saga Pattern vs. 2PC

*   **2PC (Two-Phase Commit / XA Transactions):**
    *   **機制**：準備階段（Prepare）鎖定資源 -> 提交階段（Commit）。
    *   **缺點**：同步阻塞（Blocking）、效能差、單點故障風險高（協調者掛掉會導致資源鎖死）。在微服務中極少使用。
    *   **Mechanism**: Prepare phase (locks resources) -> Commit phase.
    *   **Drawbacks**: Synchronous blocking, poor performance, high risk of single point of failure (coordinator failure leads to locked resources). Rarely used in microservices.

*   **Saga Pattern:**
    *   **機制**：將長交易拆解為一系列的**本地交易（Local Transactions）**。如果某個步驟失敗，則執行一系列**補償交易（Compensating Transactions）**來復原之前的操作。
    *   **優點**：非阻塞、高可用性。
    *   **Mechanism**: Breaks a long transaction into a sequence of **Local Transactions**. If a step fails, a series of **Compensating Transactions** are executed to undo previous operations.
    *   **Benefits**: Non-blocking, high availability.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 電商下單流程 (E-commerce Checkout Flow)

考慮一個經典場景：使用者下訂單。這涉及三個服務：
Consider a classic scenario: User places an order. This involves three services:
1.  **Order Service**: 建立訂單 (Create Order)。
2.  **Inventory Service**: 扣減庫存 (Reserve Stock)。
3.  **Payment Service**: 處理付款 (Process Payment)。

### 設計考量 (Design Considerations)

*   **Happy Path**: Order (Pending) -> Inventory (Reserved) -> Payment (Charged) -> Order (Confirmed).
*   **Failure Path (庫存不足)**: Order (Pending) -> Inventory (Fail). Order Service 必須將訂單標記為 Rejected。
*   **Failure Path (付款失敗)**: Order (Pending) -> Inventory (Reserved) -> Payment (Fail). 系統必須觸發 Inventory Service 的補償邏輯（釋放庫存），然後將 Order 標記為 Cancelled。

## 3.2 對系統品質的影響 (Impact on System Qualities)

*   **可擴充性 (Scalability)**: Saga 使用非同步訊息傳遞（Message Queues），允許服務獨立擴展，不會像 2PC 那樣因為鎖競爭而導致效能瓶頸。
    **Scalability**: Sagas use asynchronous messaging (Message Queues), allowing services to scale independently without the performance bottlenecks caused by lock contention in 2PC.
*   **可觀測性 (Observability)**: 這是最大的痛點。一個業務流程跨越三個服務，如果沒有 **Distributed Tracing (e.g., OpenTelemetry, Jaeger)** 和統一的 **Correlation ID**，Debug 將是惡夢。
    **Observability**: This is the biggest pain point. A business process spans three services; without **Distributed Tracing (e.g., OpenTelemetry, Jaeger)** and a unified **Correlation ID**, debugging becomes a nightmare.
*   **資料一致性 (Data Consistency)**: 系統在執行過程中處於「暫時不一致」狀態。例如，庫存扣了但錢還沒付。UI 設計必須適應這一點（例如顯示「處理中」而非立即顯示「成功」）。
    **Data Consistency**: The system is in a "temporarily inconsistent" state during execution. For example, stock is reserved but payment isn't made. UI design must adapt to this (e.g., showing "Processing" instead of immediate "Success").

---

# 4. 逐步示例 (Walkthrough / Example)

我們將深入探討 **Saga Pattern** 的兩種實作方式：**Choreography (編排)** 與 **Orchestration (協調)**。

We will dive deep into two implementations of the **Saga Pattern**: **Choreography** and **Orchestration**.

## 案例：旅遊訂票系統 (Case: Travel Booking System)
**目標**：同時預訂機票（Flight）與飯店（Hotel）。
**Goal**: Book a Flight and a Hotel simultaneously.

### 方法 A: Choreography (基於事件 / Event-based)

沒有中央協調者，服務之間透過訂閱事件進行互動。
No central coordinator; services interact by subscribing to events.

1.  **Order Service**: 建立訂單，發布 `OrderCreated` 事件。
    **Order Service**: Creates order, publishes `OrderCreated` event.
2.  **Flight Service**: 監聽 `OrderCreated`，預訂機票。
    *   成功：發布 `FlightBooked`。
    *   失敗：發布 `FlightBookingFailed`。
    **Flight Service**: Listens to `OrderCreated`, books flight.
    *   Success: Publishes `FlightBooked`.
    *   Fail: Publishes `FlightBookingFailed`.
3.  **Hotel Service**: 監聽 `FlightBooked`，預訂飯店。
    *   成功：發布 `HotelBooked`。
    *   失敗：發布 `HotelBookingFailed`。
    **Hotel Service**: Listens to `FlightBooked`, books hotel.
    *   Success: Publishes `HotelBooked`.
    *   Fail: Publishes `HotelBookingFailed`.
4.  **Flight Service (Compensating)**: 監聽 `HotelBookingFailed`，執行取消機票操作。
    **Flight Service (Compensating)**: Listens to `HotelBookingFailed`, executes flight cancellation.

**Pros:** 簡單，低耦合。
**Cons:** 流程隱晦（分散在各處），容易形成循環依賴（Cyclic dependencies），難以追蹤複雜流程。

### 方法 B: Orchestration (基於命令 / Command-based) - *Recommended for Complex Flows*

引入一個 **Saga Orchestrator**（通常是一個 State Machine），明確控制流程。
Introduce a **Saga Orchestrator** (usually a State Machine) that explicitly controls the flow.

#### Pseudo-code Implementation (Orchestrator Logic)

```java
public class TravelSagaOrchestrator {

    private final FlightClient flightClient;
    private final HotelClient hotelClient;
    private final OrderRepository orderRepository;

    // Triggered by "Create Trip" request
    public void handleBookTrip(String orderId, TripDetails details) {
        // Step 1: Local Transaction - Initialize Saga State
        SagaState state = orderRepository.createSagaState(orderId, "STARTED");

        try {
            // Step 2: Invoke Flight Service (Command)
            // Note: Ideally async via Request/Reply channels
            FlightResult flightRes = flightClient.bookFlight(details.flightInfo());
            
            if (flightRes.isSuccess()) {
                state.update("FLIGHT_BOOKED");
            } else {
                throw new SagaException("Flight booking failed");
            }

            // Step 3: Invoke Hotel Service (Command)
            HotelResult hotelRes = hotelClient.bookHotel(details.hotelInfo());
            
            if (hotelRes.isSuccess()) {
                state.update("COMPLETED");
                // All good!
            } else {
                // Hotel failed, trigger compensation for Flight
                throw new SagaException("Hotel booking failed");
            }

        } catch (SagaException e) {
            compensate(state, e);
        }
    }

    private void compensate(SagaState state, Exception reason) {
        state.update("COMPENSATING");
        
        if (state.hasStepCompleted("FLIGHT_BOOKED")) {
            // Compensating Transaction
            // Ideally idempotent and with retry logic
            flightClient.cancelFlight(state.getOrderId());
        }
        
        state.update("FAILED");
    }
}
```

**關鍵細節 (Key Details):**
1.  **State Persistence**: Orchestrator 必須將狀態（State）持久化到資料庫。如果 Orchestrator 當機，重啟後必須能從 DB 恢復並繼續執行（Forward Recovery）或回滾（Backward Recovery）。
    **State Persistence**: The Orchestrator must persist the state to a database. If the Orchestrator crashes, it must be able to recover from the DB upon restart and continue execution (Forward Recovery) or rollback (Backward Recovery).
2.  **Idempotency**: `cancelFlight()` 可能會被呼叫多次（例如網路超時重試），Flight Service 必須保證重複呼叫不會產生副作用。
    **Idempotency**: `cancelFlight()` might be called multiple times (e.g., network timeout retries). The Flight Service must ensure that repeated calls do not cause side effects.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽視冪等性 (Ignoring Idempotency)
*   **錯誤案例**：在重試機制中，如果 `deductMoney()` 介面不是冪等的，網路抖動可能導致使用者被扣款兩次。
    **Scenario**: In a retry mechanism, if the `deductMoney()` interface is not idempotent, network jitter could cause the user to be charged twice.
*   **後果**：資料嚴重錯誤，財務損失。
    **Consequence**: Severe data corruption, financial loss.
*   **修正**：所有參與 Saga 的服務介面（特別是寫入和補償操作）都必須實作冪等性（通常透過 unique Request ID / Deduplication table）。
    **Fix**: All service interfaces participating in a Saga (especially write and compensation operations) must implement idempotency (usually via unique Request ID / Deduplication table).

## 5.2 同步 HTTP 鏈式調用 (Synchronous HTTP Chaining)
*   **錯誤案例**：Service A 呼叫 B，B 呼叫 C，C 呼叫 D，全部使用同步 HTTP 等待回應。
    **Scenario**: Service A calls B, B calls C, C calls D, all using synchronous HTTP waiting for responses.
*   **後果**：延遲疊加（Latency adds up），可用性大幅降低（任何一個環節斷掉，整個鏈條失敗），且容易發生分散式死鎖或資源耗盡。這不是 Saga，這是分散式單體。
    **Consequence**: Latency adds up, availability drops significantly (if any link breaks, the whole chain fails), and it's prone to distributed deadlocks or resource exhaustion. This is not a Saga; it's a Distributed Monolith.
*   **修正**：使用 Message Queue / Event Bus 進行非同步通訊。
    **Fix**: Use Message Queue / Event Bus for asynchronous communication.

## 5.3 缺乏補償邏輯的「樂觀」設計 ("Optimistic" Design without Compensation)
*   **錯誤案例**：開發者假設 API 呼叫「幾乎總是成功」，只寫了 Happy Path，對於失敗僅記錄 Log 而未觸發自動回滾。
    **Scenario**: Developers assume API calls "almost always succeed," writing only the Happy Path, and merely logging failures without triggering automatic rollback.
*   **後果**：系統累積大量「殭屍資料」（如已扣庫存但未付款的訂單），需要人工介入修復。
    **Consequence**: The system accumulates a lot of "zombie data" (e.g., reserved stock for unpaid orders), requiring manual intervention to fix.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你如何在微服務中處理分散式交易？(How do you handle distributed transactions in microservices?)

*   **高分回答要點 (Key Points for High Score)**:
    1.  首先承認分散式交易的成本，並說明應儘量透過**聚合設計（Aggregate Design）**避免跨服務交易（即調整服務邊界）。
        Acknowledge the cost of distributed transactions first, and state that cross-service transactions should be avoided where possible via **Aggregate Design** (adjusting service boundaries).
    2.  如果無法避免，解釋 **Saga Pattern**。
        If unavoidable, explain the **Saga Pattern**.
    3.  比較 **Choreography** (適合簡單流程) 與 **Orchestration** (適合複雜流程，如訂單系統)。
        Compare **Choreography** (good for simple flows) vs. **Orchestration** (good for complex flows, like order systems).
    4.  強調 **最終一致性 (Eventual Consistency)** 和 **補償交易 (Compensating Transactions)** 的概念。
        Emphasize the concepts of **Eventual Consistency** and **Compensating Transactions**.

## Q2: 如果補償交易（Compensating Transaction）也失敗了怎麼辦？(What if the compensating transaction also fails?)

*   **高分回答要點 (Key Points for High Score)**:
    1.  **重試 (Retry)**：補償操作必須是冪等的，因此可以無限重試直到成功。
        **Retry**: Compensation operations must be idempotent, so they can be retried indefinitely until successful.
    2.  **人工介入 (Manual Intervention)**：如果重試多次仍失敗（例如業務規則改變或嚴重 Bug），系統應將該筆交易送入 "Dead Letter Queue" 或 "Manual Review Table"，通知營運人員手動退款或修復數據。
        **Manual Intervention**: If retries fail repeatedly (e.g., business rule change or critical bug), the system should send the transaction to a "Dead Letter Queue" or "Manual Review Table" to notify operations staff for manual refund or data fix.
    3.  **監控 (Monitoring)**：這是極端情況，必須有高優先級的 Alert。
        **Monitoring**: This is an edge case and must have high-priority alerts.

## Q3: 為什麼不直接使用 Two-Phase Commit (2PC/XA)？(Why not just use Two-Phase Commit?)

*   **高分回答要點 (Key Points for High Score)**:
    1.  **可用性 (Availability)**：CAP 定理限制。2PC 是阻塞協議，協調者當機時參與者會鎖住資源，導致系統不可用。
        **Availability**: CAP theorem constraints. 2PC is a blocking protocol; if the coordinator crashes, participants lock resources, rendering the system unavailable.
    2.  **效能 (Performance)**：微服務跨越網路，延遲不可控，持有鎖的時間過長會拖垮吞吐量（Throughput）。
        **Performance**: Microservices span networks with uncontrollable latency; holding locks for too long kills throughput.
    3.  **技術異質性 (Tech Heterogeneity)**：現代微服務可能混用 SQL、NoSQL、Message Queues，並非所有組件都支援 XA 標準。
        **Tech Heterogeneity**: Modern microservices might mix SQL, NoSQL, and Message Queues; not all components support the XA standard.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **Database-per-service** 是微服務的基石，但也移除了 ACID 的便利性。
2.  **Saga Pattern** 是解決分散式交易的標準方案，分為 **Choreography** (事件驅動) 與 **Orchestration** (中心指揮)。
3.  **Orchestration** 更適合複雜業務邏輯，雖然耦合度稍高，但可控性與可觀測性更好。
4.  **冪等性 (Idempotency)** 是實作 Saga 與重試機制的先決條件。
5.  **補償交易** 必須被設計為「最終會成功」或「轉交人工處理」。
6.  從 **ACID** 轉向 **BASE**，接受資料在短時間內的不一致。

## 後續延伸 (Next Steps)
解決了「寫入」的一致性問題後，我們面臨另一個挑戰：**如何跨服務查詢資料？**（例如：查詢「所有包含某商品的訂單」，但訂單在 Order Service，商品詳情在 Product Service）。

下一章將探討 **CQRS (Command Query Responsibility Segregation)** 與 **API Composition**，這是解決分散式資料查詢的關鍵模式。

Having solved the consistency of "writes," we face another challenge: **How to query data across services?** (e.g., Query "all orders containing a specific product," where orders are in the Order Service and product details are in the Product Service).

The next chapter will explore **CQRS (Command Query Responsibility Segregation)** and **API Composition**, which are key patterns for solving distributed data querying.