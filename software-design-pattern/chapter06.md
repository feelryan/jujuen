# 1. 前言與學習目標 (Introduction and Learning Objectives)

在單體架構（Monolith）轉向微服務（Microservices）的過程中，我們不再享受單一 Process 內的記憶體共享與 ACID 資料庫交易保證。分散式系統帶來了網路延遲、部分失效（Partial Failure）與資料一致性挑戰。本章將探討資深工程師在設計高可用、高擴充系統時必須掌握的關鍵模式。

In the transition from Monolith to Microservices, we no longer enjoy the luxury of shared memory within a single process or ACID transaction guarantees from a single database. Distributed systems introduce challenges such as network latency, partial failures, and data consistency issues. This chapter explores the key patterns that senior engineers must master to design high-availability and scalable systems.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **駕馭通訊模式**：清楚區分 **API Gateway** 與 **Sidecar** 的職責邊界，並知道何時使用 BFF (Backend for Frontend)。
    **Master Communication Patterns**: Clearly distinguish the responsibilities of **API Gateway** versus **Sidecar**, and know when to apply the BFF (Backend for Frontend) pattern.
2.  **設計韌性系統**：實作 **Circuit Breaker** 與 **Retry** 機制，防止級聯故障（Cascading Failures）。
    **Design Resilient Systems**: Implement **Circuit Breaker** and **Retry** mechanisms to prevent cascading failures.
3.  **解決分散式交易難題**：能夠在 **Saga Pattern**（Choreography vs. Orchestration）與 **2PC** 之間做出正確的架構取捨，處理跨服務資料一致性。
    **Solve Distributed Transaction Challenges**: Make the right architectural trade-offs between the **Saga Pattern** (Choreography vs. Orchestration) and **2PC** to handle cross-service data consistency.
4.  **優化讀寫效能**：理解 **CQRS** 的適用場景及其與 Event Sourcing 的結合，避免過度設計。
    **Optimize Read/Write Performance**: Understand the use cases for **CQRS** and its integration with Event Sourcing, avoiding over-engineering.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 基礎設施與應用邏輯的分離 (Decoupling Infrastructure from Application Logic)

在分散式系統中，我們希望業務邏輯（Business Logic）與網路通訊邏輯（Networking Logic）分離。
In distributed systems, we aim to decouple Business Logic from Networking Logic.

*   **Sidecar Pattern（邊車模式）**：
    想像你騎著一輛摩托車（主應用程式），旁邊掛著一個邊車（Sidecar）。邊車負責處理所有「非業務核心」的任務，如服務發現、mTLS 加密、Metrics 收集等。這就是 Service Mesh（如 Istio, Linkerd）的基礎。
    **Sidecar Pattern**: Imagine riding a motorcycle (the main application) with a sidecar attached. The sidecar handles all "non-core business" tasks, such as service discovery, mTLS encryption, and metrics collection. This is the foundation of Service Mesh (e.g., Istio, Linkerd).

*   **API Gateway（API 閘道器）**：
    這就像是大樓的「接待櫃檯」。外部請求（Client）不直接進入各個辦公室（Microservices），而是先通過櫃檯進行身分驗證、路由分發、流量限制（Rate Limiting）與協定轉換。
    **API Gateway**: This is like the "reception desk" of a building. External requests (Clients) do not go directly to individual offices (Microservices) but first pass through the reception for authentication, routing, rate limiting, and protocol translation.

### 2.2 失敗是常態 (Failure is the Norm)

*   **Circuit Breaker（斷路器）**：
    概念源自電力系統。當某個服務回應過慢或錯誤率過高時，斷路器會「跳閘（Open）」，直接回傳錯誤或預設值，而不是讓請求堆積導致系統崩潰。這是一種「快速失敗（Fail Fast）」的保護機制。
    **Circuit Breaker**: The concept originates from electrical systems. When a service responds too slowly or the error rate is too high, the breaker "trips" (opens), returning an error or a default value immediately instead of letting requests pile up and crash the system. This is a "Fail Fast" protection mechanism.

### 2.3 資料一致性的光譜 (The Spectrum of Data Consistency)

*   **Saga Pattern**：
    將一個跨服務的長交易拆解為一系列本地交易（Local Transactions）。如果中途失敗，則執行一系列「補償交易（Compensating Transactions）」來復原狀態。這是一種「最終一致性（Eventual Consistency）」模型。
    **Saga Pattern**: Breaks a long-running cross-service transaction into a series of local transactions. If a step fails, a sequence of "Compensating Transactions" is executed to undo the changes. This is an "Eventual Consistency" model.

*   **CQRS (Command Query Responsibility Segregation)**：
    將「寫入（Command）」與「讀取（Query）」的模型分開。寫入端優化交易與邏輯，讀取端優化查詢速度（通常透過非正規化 View）。
    **CQRS**: Separates the models for "Writing (Command)" and "Reading (Query)". The write side optimizes for transactions and logic, while the read side optimizes for query speed (often via denormalized views).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 API Gateway vs. Load Balancer vs. Sidecar

在 System Design 面試或實務架構圖中，這三者的位置常被混淆。
In System Design interviews or real-world architecture diagrams, the placement of these three is often confused.

*   **Load Balancer (L4/L7)**：位於最外層，主要負責流量分配與健康檢查。
    **Load Balancer (L4/L7)**: sits at the outermost layer, primarily responsible for traffic distribution and health checks.
*   **API Gateway**：位於 LB 之後，叢集入口。負責 **AuthN/AuthZ**、**Request Aggregation**（將多個內部 API 呼叫合併為一個回應給 Mobile App）、**Rate Limiting**。
    **API Gateway**: sits behind the LB, at the cluster ingress. Responsible for **AuthN/AuthZ**, **Request Aggregation** (combining multiple internal API calls into one response for Mobile Apps), and **Rate Limiting**.
*   **Sidecar**：位於叢集內部（Pod 內）。負責服務間（East-West traffic）的通訊加密、重試邏輯與分散式追蹤（Distributed Tracing）。
    **Sidecar**: sits inside the cluster (within the Pod). Responsible for inter-service (East-West traffic) communication encryption, retry logic, and distributed tracing.

### 3.2 處理大型電商訂單系統 (Handling Large-Scale E-commerce Order Systems)

當你被問到「如何設計一個高併發的搶購系統」時：
When asked "How to design a high-concurrency flash sale system":

1.  **CQRS**：讀取商品詳情（Read）的流量遠大於下單（Write）。使用 CQRS 將讀取導向 Redis 或 ElasticSearch，寫入導向關聯式資料庫，能大幅提升讀取吞吐量。
    **CQRS**: Traffic for reading product details (Read) is far greater than placing orders (Write). Using CQRS to direct reads to Redis or ElasticSearch and writes to a Relational Database can significantly boost read throughput.
2.  **Saga**：下單流程涉及 `Order Service`、`Inventory Service`、`Payment Service`。使用 2PC 會導致資料庫鎖死（Locking）與效能瓶頸。Saga 允許各個服務獨立提交 DB 交易，透過 Message Queue 串聯，提升系統可用性。
    **Saga**: The ordering process involves `Order Service`, `Inventory Service`, and `Payment Service`. Using 2PC would lead to database locking and performance bottlenecks. Saga allows each service to commit DB transactions independently, linked via Message Queues, improving system availability.

---

# 4. 逐步示例：Saga Pattern 實作 (Walkthrough: Implementing Saga Pattern)

### 背景 (Context)
我們有一個旅遊預訂系統。使用者請求「預訂行程」，包含：
1. 預訂機票 (Flight Service)
2. 預訂飯店 (Hotel Service)
3. 扣款 (Payment Service)

We have a travel booking system. A user requests to "Book a Trip", which includes:
1. Book Flight (Flight Service)
2. Book Hotel (Hotel Service)
3. Charge Payment (Payment Service)

### 挑戰 (Challenge)
如果「扣款」失敗，我們必須取消已經預訂成功的機票與飯店。
If "Charge Payment" fails, we must cancel the flight and hotel that were successfully booked.

### 解決方案：Choreography-based Saga (Solution: Choreography-based Saga)
我們使用事件驅動（Event-Driven）的方式，服務之間透過 Message Queue (e.g., Kafka/RabbitMQ) 溝通。

We use an Event-Driven approach where services communicate via a Message Queue (e.g., Kafka/RabbitMQ).

#### Step 1: 定義事件與補償邏輯 (Define Events and Compensation Logic)

每個服務需要處理兩類操作：**Do (執行)** 與 **Compensate (補償/復原)**。
Each service needs to handle two types of operations: **Do (Execute)** and **Compensate (Undo/Revert)**.

```java
// Pseudo-code for Saga Steps

// 1. Flight Service
class FlightService {
    public void onEvent(OrderCreatedEvent event) {
        try {
            bookFlight(event.orderId);
            publish(new FlightBookedEvent(event.orderId));
        } catch (Exception e) {
            publish(new FlightBookingFailedEvent(event.orderId));
        }
    }

    public void onEvent(TripBookingFailedEvent event) {
        // Compensation Logic
        cancelFlight(event.orderId);
        log.info("Flight cancelled for order " + event.orderId);
    }
}

// 2. Hotel Service
class HotelService {
    public void onEvent(FlightBookedEvent event) {
        try {
            bookHotel(event.orderId);
            publish(new HotelBookedEvent(event.orderId));
        } catch (Exception e) {
            // Trigger compensation for previous steps
            publish(new TripBookingFailedEvent(event.orderId, "Hotel Failed"));
        }
    }
    
    public void onEvent(TripBookingFailedEvent event) {
        // Only compensate if we actually booked a hotel
        if (hasBooking(event.orderId)) {
            cancelHotel(event.orderId);
        }
    }
}

// 3. Payment Service
class PaymentService {
    public void onEvent(HotelBookedEvent event) {
        try {
            chargeCustomer(event.orderId);
            publish(new TripConfirmedEvent(event.orderId)); // Success!
        } catch (InsufficientFundsException e) {
            // Trigger global compensation
            publish(new TripBookingFailedEvent(event.orderId, "Payment Failed"));
        }
    }
}
```

### 關鍵細節 (Key Details)

1.  **Idempotency (冪等性)**：
    由於網路重試（Retry），`bookFlight` 可能被呼叫多次。必須確保多次呼叫不會導致重複訂票。通常透過在 DB 中檢查 `transaction_id` 來實現。
    **Idempotency**: Due to network retries, `bookFlight` might be called multiple times. You must ensure that multiple calls do not result in duplicate bookings. This is usually implemented by checking a `transaction_id` in the DB.

2.  **Orchestration vs. Choreography**：
    上述範例是 **Choreography**（去中心化，服務監聽彼此的事件）。對於更複雜的流程（超過 4-5 個步驟），建議使用 **Orchestrator**（中心化指揮，如 AWS Step Functions 或 Temporal.io），由一個協調者明確呼叫每個步驟與補償，避免流程邏輯散落在各處難以追蹤。
    **Orchestration vs. Choreography**: The example above is **Choreography** (decentralized, services listen to each other's events). For more complex flows (more than 4-5 steps), an **Orchestrator** (centralized coordinator, like AWS Step Functions or Temporal.io) is recommended. The orchestrator explicitly calls each step and compensation, preventing flow logic from being scattered and hard to trace.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 分散式單體 (The Distributed Monolith)
*   **錯誤 (Pitfall)**：雖然拆分了微服務，但服務間透過同步 HTTP 呼叫緊密耦合。Service A 呼叫 B，B 呼叫 C，C 呼叫 D。
    **Pitfall**: Even though microservices are split, they are tightly coupled via synchronous HTTP calls. Service A calls B, B calls C, C calls D.
*   **後果 (Consequence)**：延遲疊加（Latency adds up），且任何一個服務掛掉，整個鏈條都會失敗。可用性比單體還差。
    **Consequence**: Latency adds up, and if any service fails, the entire chain fails. Availability becomes worse than the monolith.
*   **修正 (Fix)**：引入 **Circuit Breaker** 防止雪崩，並盡量改用 **Async Messaging**（非同步訊息）來解耦。
    **Fix**: Introduce **Circuit Breaker** to prevent avalanches, and switch to **Async Messaging** where possible to decouple.

### 5.2 濫用 CQRS (Overusing CQRS)
*   **錯誤 (Pitfall)**：對簡單的 CRUD 系統（如內部 Admin 後台）使用 CQRS。
    **Pitfall**: Using CQRS for simple CRUD systems (like an internal Admin dashboard).
*   **後果 (Consequence)**：增加了維護兩個模型（Read/Write）的複雜度，且必須處理資料同步延遲（Replication Lag）帶來的 UI 顯示問題。
    **Consequence**: Increases the complexity of maintaining two models (Read/Write) and requires handling UI issues caused by data synchronization latency (Replication Lag).
*   **修正 (Fix)**：只有在讀寫比例懸殊（如 1000:1）或讀寫模型差異極大時才使用 CQRS。
    **Fix**: Only use CQRS when the read/write ratio is extreme (e.g., 1000:1) or when the read and write models diverge significantly.

### 5.3 缺乏冪等性的重試 (Retries without Idempotency)
*   **錯誤 (Pitfall)**：配置了自動重試（Retry），但 API 介面不是冪等的。
    **Pitfall**: Configuring automatic retries, but the API interface is not idempotent.
*   **後果 (Consequence)**：在網路超時的情況下，可能導致使用者被扣款兩次或收到兩件商品。
    **Consequence**: In case of network timeouts, this can lead to users being charged twice or receiving duplicate items.
*   **修正 (Fix)**：所有寫入操作必須支援冪等性（Idempotency Keys）。
    **Fix**: All write operations must support Idempotency Keys.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在微服務架構中，如果一個下游客戶端（Downstream Service）回應很慢，你會如何設計保護機制？
**In a microservices architecture, if a downstream service is responding slowly, how would you design a protection mechanism?**

*   **高分回答要點 (Key Points)**：
    1.  **Timeouts**：設定合理的超時時間，避免佔用 Thread/Connection 資源。
    2.  **Circuit Breaker**：監控錯誤率或回應時間，達到閾值後開啟斷路器，直接回傳 Fallback 或 Error，給下游恢復時間。
    3.  **Bulkhead Pattern**：隔離資源（如 Thread Pool），確保 Service A 的故障不會耗盡 Service B 的資源，影響其他功能。
    4.  **Idempotent Retry**：如果錯誤是暫時性的（Transient），進行帶有 Exponential Backoff 的重試。

### Q2: 比較 Saga Pattern 與 Two-Phase Commit (2PC/XA)，你會如何選擇？
**Compare Saga Pattern vs. Two-Phase Commit (2PC/XA). How would you choose?**

*   **高分回答要點 (Key Points)**：
    1.  **Consistency vs. Availability**：2PC 提供強一致性（ACID），但會鎖定資源，效能差且可用性低（CAP 定理中的 CP）。Saga 提供最終一致性（BASE），效能好且可用性高（AP）。
    2.  **適用場景**：銀行核心轉帳可能需要 2PC（或同一 DB 內的 Transaction）；電商下單、旅遊預訂等長流程業務適合 Saga。
    3.  **複雜度**：Saga 需要開發者編寫補償邏輯（Compensating Logic），開發成本較高。

### Q3: 什麼是 API Gateway 的 "Backend for Frontend" (BFF) 模式？解決了什麼問題？
**What is the "Backend for Frontend" (BFF) pattern in API Gateway? What problem does it solve?**

*   **高分回答要點 (Key Points)**：
    1.  **問題**：Desktop Web, Mobile App, IoT 設備對資料的需求不同（例如 Mobile 螢幕小，不需要完整資料，且希望減少 HTTP Round-trip）。
    2.  **解法**：為每一種 Client 建立專屬的 Gateway/Adapter。
    3.  **優勢**：解耦了前端與後端服務，前端團隊可以自主優化 API 聚合邏輯，而不需修改後端微服務。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **API Gateway** 是對外的門面（Auth, Rate Limit, Aggregation）；**Sidecar** 是對內的管家（mTLS, Retry, Tracing）。
2.  **Circuit Breaker** 是防止級聯故障的必備保險絲。
3.  **Saga Pattern** 透過「補償交易」來解決跨服務的資料一致性，取代了效能低下的 2PC。
4.  **CQRS** 透過分離讀寫模型來優化高併發讀取，但增加了系統複雜度與延遲。
5.  **冪等性（Idempotency）** 是分散式系統中實作重試（Retry）機制的前提條件。

### 後續延伸 (Next Steps)
*   **實作**：嘗試使用 **Temporal.io** 或 **AWS Step Functions** 實作一個 Orchestration Saga。
*   **閱讀**：深入研究 **Observability**（可觀測性），了解如何在分散式環境中使用 OpenTelemetry 追蹤跨服務的 Request (Trace ID propagation)，這是 Debug 分散式系統的關鍵技能（對應下一章節）。
*   **Implementation**: Try implementing an Orchestration Saga using **Temporal.io** or **AWS Step Functions**.
*   **Reading**: Dive deeper into **Observability**. Learn how to use OpenTelemetry to trace requests across services (Trace ID propagation) in a distributed environment. This is a critical skill for debugging distributed systems (corresponding to the next chapter).