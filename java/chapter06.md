### 1. 前言與學習目標
### 1. Introduction & Learning Objectives

對於具備 7–12 年經驗的資深工程師而言，Spring 已經不是「如何使用 `@Autowired`」的問題，而是「如何駕馭其底層機制以支撐高併發與微服務架構」。在大型企業級系統中，對 Spring IoC/AOP 原理的誤解，往往會導致記憶體洩漏、分散式交易不一致，或是資料庫連線池耗盡等嚴重生產事故。
For a senior engineer with 7–12 years of experience, Spring is no longer about "how to use `@Autowired`", but rather "how to harness its underlying mechanisms to support high concurrency and microservices architectures." In large-scale enterprise systems, misunderstandings of Spring IoC/AOP principles often lead to severe production incidents such as memory leaks, distributed transaction inconsistencies, or database connection pool exhaustion.

完成本章後，你將能夠：
After completing this chapter, you will be able to:
1. **拆解 Spring AOP 與代理機制 (Deconstruct Spring AOP and Proxy Mechanisms)**：精準解釋 JDK Dynamic Proxy 與 CGLIB 的差異，並避開常見的「自我呼叫 (Self-Invocation)」陷阱。
2. **掌控複雜交易邊界 (Master Complex Transaction Boundaries)**：深刻理解 `@Transactional` 的傳播行為 (Propagation) 與隔離級別 (Isolation)，並能在高併發場景下正確配置。
3. **設計微服務分散式交易 (Design Distributed Transactions in Microservices)**：跳脫單體架構思維，運用 Outbox Pattern 與 Saga 模式解決跨服務的資料一致性問題。
4. **優化資料庫連線池 (Optimize Database Connection Pools)**：根據系統負載與硬體規格，科學化地調優 HikariCP，避免連線飢餓 (Connection Starvation) 與死鎖 (Deadlocks)。

---

### 2. 核心觀念與心智模型
### 2. Core Concepts & Mental Model

#### IoC 與 AOP：代理人的洋蔥模型 (IoC & AOP: The Onion Model of Proxies)
Spring 的核心心智模型是「代理 (Proxy)」。當你從 ApplicationContext 取得一個 Bean 時，你拿到的通常不是原始物件，而是一個被 CGLIB 或 JDK Proxy 包裝過的「代理物件」。
The core mental model of Spring is the "Proxy". When you retrieve a Bean from the ApplicationContext, you are usually not getting the raw object, but rather a "proxy object" wrapped by CGLIB or JDK Proxy.

你可以把 AOP 想像成一顆「洋蔥」。原始的業務邏輯在最核心，而 `@Transactional`、`@Cacheable`、`@Async` 等註解，則是一層層包覆在外面的洋蔥皮（Interceptors）。當外部呼叫這個方法時，請求必須由外而內穿透這些洋蔥皮，這就是為什麼**同類別內的自我呼叫 (Self-invocation) 會導致 AOP 失效**——因為你直接在洋蔥內部呼叫，繞過了外層的代理皮。
You can think of AOP as an "onion". The raw business logic is at the core, while annotations like `@Transactional`, `@Cacheable`, and `@Async` are layers of onion skin (Interceptors) wrapping it. When an external call is made to this method, the request must penetrate these skins from the outside in. This is why **self-invocation within the same class causes AOP to fail**—because you are calling directly from inside the onion, bypassing the outer proxy layers.

#### 交易管理：綁定於執行緒的上下文 (Transaction Management: Thread-Bound Context)
Spring 的 `@Transactional` 魔法，本質上是 `AOP` + `ThreadLocal`。
Spring's `@Transactional` magic is essentially `AOP` + `ThreadLocal`.

當進入 `@Transactional` 方法時，Spring 的 TransactionInterceptor 會從 DataSource 取得一個 Connection，關閉 AutoCommit，並將這個 Connection 放入 `ThreadLocal` 中。在此執行緒內的所有 DAO/Repository 操作，都會從 `ThreadLocal` 拿到同一個 Connection。一旦跨越了執行緒（例如在交易內啟動了新 Thread，或呼叫了其他微服務），這個上下文就會斷裂。
When entering a `@Transactional` method, Spring's TransactionInterceptor acquires a Connection from the DataSource, disables AutoCommit, and places this Connection into a `ThreadLocal`. All DAO/Repository operations within this thread will retrieve the exact same Connection from the `ThreadLocal`. Once the thread boundary is crossed (e.g., starting a new Thread within the transaction, or calling another microservice), this context is broken.

#### 單體交易 vs 分散式交易 (Monolithic vs Distributed Transactions)
在單體架構中，我們依賴資料庫的 ACID 特性（Local Transaction）。但在微服務中（如 Spring Cloud），網路是不可靠的。我們必須將心智模型從 **ACID (強一致性)** 轉換為 **BASE (最終一致性)**。
In a monolithic architecture, we rely on the database's ACID properties (Local Transaction). But in microservices (like Spring Cloud), the network is unreliable. We must shift our mental model from **ACID (Strong Consistency)** to **BASE (Eventual Consistency)**.

---

### 3. 實務場景與系統設計視角
### 3. Real-World & System Design View

在 Production 環境中，Spring 的底層機制直接影響系統的**可靠性 (Reliability)** 與 **效能 (Performance)**。
In a Production environment, Spring's underlying mechanisms directly impact the system's **Reliability** and **Performance**.

**場景：電商結帳系統 (Scenario: E-commerce Checkout System)**
假設一個結帳流程包含：1. 建立訂單 (Create Order) -> 2. 扣減庫存 (Deduct Inventory) -> 3. 呼叫外部金流 (Call Payment Gateway)。
Suppose a checkout process involves: 1. Create Order -> 2. Deduct Inventory -> 3. Call Payment Gateway.

*   **單體架構的災難 (Monolithic Disaster)**：如果資淺工程師將這三個步驟包在同一個 `@Transactional` 中，當外部金流 API 延遲 (Latency) 達到 5 秒時，這個資料庫連線將被佔用 5 秒。在 1000 TPS 的併發下，HikariCP 連線池會瞬間耗盡，導致整個系統崩潰。
    *Monolithic Disaster*: If a junior engineer wraps these three steps in a single `@Transactional`, and the external payment API latency hits 5 seconds, the database connection will be held for 5 seconds. Under 1000 TPS concurrency, the HikariCP connection pool will be exhausted instantly, causing the entire system to crash.
*   **微服務架構的挑戰 (Microservices Challenge)**：如果訂單和庫存是兩個獨立的 Spring Boot 服務，`@Transactional` 無法跨越 HTTP/gRPC 邊界。如果訂單建立成功，但呼叫庫存服務時發生 Network Timeout，就會產生資料不一致（Data Inconsistency）。
    *Microservices Challenge*: If Order and Inventory are two independent Spring Boot services, `@Transactional` cannot cross HTTP/gRPC boundaries. If the order is created successfully but a Network Timeout occurs when calling the inventory service, data inconsistency arises.

**系統設計視角 (System Design Perspective)**：
資深工程師在設計時，會將**資料庫操作與外部 I/O 徹底分離**。資料庫交易應該「越短越好」。對於跨服務的呼叫，則會引入 **Outbox Pattern (發件匣模式)** 結合 Kafka 來保證至少一次 (At-least-once) 的傳遞與最終一致性。
Senior engineers design by **strictly separating database operations from external I/O**. Database transactions should be "as short as possible". For cross-service calls, the **Outbox Pattern** combined with Kafka is introduced to guarantee at-least-once delivery and eventual consistency.

---

### 4. 逐步示例
### 4. Walkthrough / Example

#### 範例一：解決自我呼叫 (Self-Invocation) 與交易失效
#### Example 1: Solving Self-Invocation and Transaction Failure

**問題背景 (Problem Context)**：
在同一個 Service 類別中，非交易方法呼叫了交易方法，導致 `@Transactional` 失效。
In the same Service class, a non-transactional method calls a transactional method, causing `@Transactional` to fail.

```java
@Service
public class OrderService {
    
    // 外部呼叫這個方法 (External call to this method)
    public void processOrder(Order order) {
        // ... some business logic ...
        // 這裡直接呼叫內部方法，繞過了 Spring Proxy！
        // Calling internal method directly here bypasses the Spring Proxy!
        saveOrderToDatabase(order); 
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveOrderToDatabase(Order order) {
        orderRepository.save(order);
        // 如果這裡發生 Exception，將不會 rollback，因為 Transaction 根本沒啟動。
        // If an Exception occurs here, it won't rollback because the Transaction never started.
    }
}
```

**成熟的解決方案 (Mature Solution)**：
雖然可以使用 `AopContext.currentProxy()`，但最符合 Spring 哲學且易於測試的做法是**重構 (Refactoring)** 或 **自我注入 (Self-Injection)**。
While `AopContext.currentProxy()` can be used, the most Spring-idiomatic and testable approach is **Refactoring** or **Self-Injection**.

```java
@Service
public class OrderService {
    
    // 透過 ObjectProvider 延遲注入自己，避免 Circular Dependency 啟動報錯
    // Lazy inject self via ObjectProvider to avoid Circular Dependency startup errors
    private final ObjectProvider<OrderService> selfProvider;
    private final OrderRepository orderRepository;

    public OrderService(ObjectProvider<OrderService> selfProvider, OrderRepository orderRepository) {
        this.selfProvider = selfProvider;
        this.orderRepository = orderRepository;
    }

    public void processOrder(Order order) {
        // 透過 Proxy 呼叫，確保 AOP 攔截器生效
        // Call via Proxy to ensure AOP interceptors take effect
        selfProvider.getObject().saveOrderToDatabase(order); 
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveOrderToDatabase(Order order) {
        orderRepository.save(order);
    }
}
```

#### 範例二：微服務下的 Outbox Pattern 實作
#### Example 2: Outbox Pattern Implementation in Microservices

**問題背景 (Problem Context)**：
建立訂單後，需要發送 Kafka 訊息通知庫存服務。如果寫入 DB 成功但發送 Kafka 失敗，或者發送 Kafka 成功但 DB Commit 失敗，都會造成嚴重的不一致。
After creating an order, a Kafka message must be sent to notify the inventory service. If DB write succeeds but Kafka publish fails, or Kafka publish succeeds but DB commit fails, it causes severe inconsistency.

**思考步驟 (Thinking Process)**：
1. *Naive Idea*: 先寫 DB，再發 Kafka。如果 Kafka 失敗，丟出 Exception 讓 DB Rollback。（缺點：Kafka 發送很慢，會拉長 DB 交易時間；且如果 Kafka 成功但 DB 在最後 Commit 時發生 Timeout，Kafka 訊息無法撤回）。
   *Naive Idea*: Write DB first, then publish Kafka. If Kafka fails, throw Exception to rollback DB. (Cons: Kafka publish is slow, prolonging DB transaction; if Kafka succeeds but DB times out during final commit, the Kafka message cannot be recalled).
2. *Mature Solution*: **Transactional Outbox**。在同一個本地交易中，將訂單資料寫入 `orders` 表，並將事件資料寫入 `outbox_events` 表。由另一個獨立的 Worker (如 Debezium 或 Spring `@Scheduled`) 負責讀取 `outbox_events` 並發送到 Kafka。
   *Mature Solution*: **Transactional Outbox**. Within the same local transaction, write order data to the `orders` table and event data to the `outbox_events` table. An independent Worker (like Debezium or Spring `@Scheduled`) is responsible for reading `outbox_events` and publishing to Kafka.

```java
@Service
@RequiredArgsConstructor
public class OrderFacade {
    
    private final OrderRepository orderRepository;
    private final OutboxEventRepository outboxEventRepository;
    private final ObjectMapper objectMapper;

    // 這裡保證了 Local ACID：訂單與事件要麼同時成功，要麼同時失敗
    // This guarantees Local ACID: Order and Event either both succeed or both fail
    @Transactional
    public void createOrder(OrderRequest request) {
        // 1. 儲存業務資料 (Save business data)
        Order order = new Order(request);
        orderRepository.save(order);

        // 2. 儲存 Outbox 事件 (Save Outbox event)
        OutboxEvent event = new OutboxEvent();
        event.setAggregateId(order.getId());
        event.setEventType("ORDER_CREATED");
        event.setPayload(objectMapper.writeValueAsString(order));
        event.setStatus(OutboxStatus.PENDING);
        outboxEventRepository.save(event);
    }
}
```
*(註：後續由 Debezium 監聽 DB Binlog，或由 `@Scheduled` 排程撈取 PENDING 狀態的事件發送至 Kafka，實現最終一致性。)*
*(Note: Subsequently, Debezium listens to the DB Binlog, or a `@Scheduled` job fetches PENDING events to publish to Kafka, achieving eventual consistency.)*

---

### 5. 常見錯誤與反模式
### 5. Common Pitfalls & Anti-patterns

#### 1. 在 `@Transactional` 中進行耗時的外部 I/O (Blocking I/O inside `@Transactional`)
*   **錯誤案例 (Pitfall)**：在 DB 交易中呼叫外部 HTTP API 或發送 Email。
    *Pitfall*: Calling an external HTTP API or sending an Email inside a DB transaction.
*   **為何不好 (Why it's bad)**：這會導致資料庫連線被長時間佔用。在高併發下，HikariCP 連線池會迅速耗盡 (Connection Pool Exhaustion)，導致整個服務無法回應任何 DB 請求。
    *Why it's bad*: This causes the database connection to be held for a long time. Under high concurrency, the HikariCP connection pool will be exhausted rapidly, rendering the entire service unable to respond to any DB requests.
*   **較佳方案 (Better Alternative)**：將外部 I/O 移出交易邊界之外，或者使用非同步事件驅動 (Event-driven) 的方式處理外部呼叫。
    *Better Alternative*: Move external I/O outside the transaction boundary, or use an asynchronous event-driven approach to handle external calls.

#### 2. 吞噬 Exception 導致 Rollback 失敗 (Swallowing Exceptions preventing Rollback)
*   **錯誤案例 (Pitfall)**：在 `@Transactional` 方法內使用 `try-catch` 捕獲了 Exception，但沒有重新丟出 (rethrow)。
    *Pitfall*: Using `try-catch` inside a `@Transactional` method to catch an Exception without rethrowing it.
*   **為何不好 (Why it's bad)**：Spring 的 TransactionInterceptor 預設只會在捕獲到 `RuntimeException` 或 `Error` 時觸發 Rollback。如果你 catch 了例外卻沒有 throw，Spring 會認為方法成功執行，進而 Commit 交易，導致髒資料。
    *Why it's bad*: Spring's TransactionInterceptor by default only triggers a Rollback when it catches a `RuntimeException` or `Error`. If you catch the exception but don't throw it, Spring assumes the method executed successfully and commits the transaction, leading to dirty data.
*   **較佳方案 (Better Alternative)**：如果必須 catch，請在 catch block 中手動標記 rollback：`TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();`，或拋出自定義的 RuntimeException。
    *Better Alternative*: If you must catch, manually mark for rollback in the catch block: `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();`, or throw a custom RuntimeException.

#### 3. 濫用 `REQUIRES_NEW` 導致死鎖 (Overusing `REQUIRES_NEW` leading to Deadlocks)
*   **錯誤案例 (Pitfall)**：在一個已經開啟交易的方法中，迴圈呼叫另一個標註為 `@Transactional(propagation = Propagation.REQUIRES_NEW)` 的方法。
    *Pitfall*: In a method that has already started a transaction, calling another method annotated with `@Transactional(propagation = Propagation.REQUIRES_NEW)` inside a loop.
*   **為何不好 (Why it's bad)**：`REQUIRES_NEW` 會暫停當前交易，並從連線池中**獲取一個全新的連線**。這意味著同一個 Thread 同時佔用了 2 個 DB 連線。如果連線池大小為 10，只要有 10 個併發請求，就會耗盡 20 個連線，極易引發連線池層級的死鎖 (Pool-level Deadlock)。
    *Why it's bad*: `REQUIRES_NEW` suspends the current transaction and **acquires a brand new connection** from the pool. This means the same Thread holds 2 DB connections simultaneously. If the pool size is 10, just 10 concurrent requests will demand 20 connections, easily causing a pool-level deadlock.

---

### 6. 面試與實務問答切入點
### 6. Interview & Discussion Hooks

*   **Q1: Spring 如何解決 Bean 的循環依賴 (Circular Dependency)？為什麼建構子注入 (Constructor Injection) 無法被解決？**
    *   **Q1: How does Spring resolve Bean Circular Dependencies? Why can't Constructor Injection be resolved?**
    *   **高分回答要點 (Key points for a high-scoring answer)**：
        *   提到「三級快取 (Three-level Cache)」機制：`singletonObjects`, `earlySingletonObjects`, `singletonFactories`。
        *   解釋 Spring 透過提前暴露 ObjectFactory 來提供尚未完全初始化的 Bean 參照。
        *   指出建構子注入在實例化 (Instantiation) 階段就需要依賴項，此時 Bean 尚未建立，無法放入快取，因此必然拋出 `BeanCurrentlyInCreationException`。

*   **Q2: 你的 `@Transactional` 方法拋出了 `SQLException`，但資料卻沒有 Rollback，可能的原因有哪些？**
    *   **Q2: Your `@Transactional` method threw an `SQLException`, but the data didn't rollback. What are the possible reasons?**
    *   **高分回答要點 (Key points for a high-scoring answer)**：
        *   `SQLException` 是 Checked Exception，Spring 預設只對 Unchecked Exception (RuntimeException) rollback。解法是設定 `@Transactional(rollbackFor = Exception.class)`。
        *   發生了 Self-invocation，繞過了 Proxy。
        *   方法不是 `public` 的 (在 Spring AOP 預設行為下失效)。
        *   資料庫引擎本身不支援交易 (例如 MySQL 的 MyISAM 引擎)。

*   **Q3: 如何決定 HikariCP 連線池的大小 (Pool Size)？越大越好嗎？**
    *   **Q3: How do you determine the HikariCP Pool Size? Is bigger always better?**
    *   **高分回答要點 (Key points for a high-scoring answer)**：
        *   絕對不是越大越好。過大的連線池會導致資料庫伺服器花費大量資源在 Context Switching 上。
        *   引用 PostgreSQL 官方建議公式：`connections = ((core_count * 2) + effective_spindle_count)`。
        *   說明實務上通常從較小的值 (如預設的 10) 開始，並透過壓測 (Load Testing) 與監控 (Metrics) 來動態調整。

*   **Q4: 在 Spring Cloud 微服務中，你會選擇 2PC (Two-Phase Commit) 還是 Saga 模式來處理跨服務交易？為什麼？**
    *   **Q4: In Spring Cloud microservices, would you choose 2PC (Two-Phase Commit) or Saga pattern for cross-service transactions? Why?**
    *   **高分回答要點 (Key points for a high-scoring answer)**：
        *   強烈反對在微服務中使用 2PC (如 Seata AT 模式的某些場景)，因為它會長時間鎖定資源，嚴重影響系統吞吐量 (Throughput) 與可用性 (Availability)。
        *   選擇 Saga 模式 (Choreography 或 Orchestration)，透過非同步事件驅動，並實作補償交易 (Compensating Transactions) 來達到最終一致性。

---

### 7. 小結與後續延伸
### 7. Summary & Next Steps

**記憶錨點 (Memory Anchors)**：
1. **Proxy is Everything**: Spring AOP 與 Transaction 的核心是代理模式。理解「洋蔥模型」就能避開 90% 的配置失效問題。
   *Proxy is Everything*: The core of Spring AOP and Transaction is the proxy pattern. Understanding the "onion model" avoids 90% of configuration failure issues.
2. **ThreadLocal Context**: 交易上下文綁定於執行緒。跨執行緒或跨服務時，交易必然斷裂。
   *ThreadLocal Context*: Transaction context is bound to the thread. Transactions inevitably break when crossing threads or services.
3. **Keep Transactions Short**: 絕對不要在 `@Transactional` 中進行網路 I/O 或耗時運算，保護你的資料庫連線池。
   *Keep Transactions Short*: Never perform network I/O or time-consuming computations inside `@Transactional` to protect your database connection pool.
4. **Outbox for Microservices**: 跨服務的資料一致性，請放棄分散式鎖與 2PC，擁抱 Transactional Outbox 與最終一致性。
   *Outbox for Microservices*: For cross-service data consistency, abandon distributed locks and 2PC; embrace Transactional Outbox and eventual consistency.
5. **Math over Guessing**: HikariCP 的調優需要基於 CPU 核心數與硬碟 I/O 的數學計算與壓測，而非盲目加大數值。
   *Math over Guessing*: HikariCP tuning requires mathematical calculation and load testing based on CPU cores and disk I/O, not blindly increasing numbers.

**後續延伸 (Next Steps)**：
*   **Reactive Spring (Project Reactor)**：當系統面臨極高併發且 I/O 密集時，傳統的 Thread-per-request 模型將成為瓶頸。下一步可探索 Spring WebFlux，了解在非同步非阻塞 (Non-blocking) 架構下，如何處理沒有 `ThreadLocal` 支援的交易管理 (如 R2DBC)。
    *Reactive Spring (Project Reactor)*: When the system faces extremely high concurrency and is I/O intensive, the traditional Thread-per-request model becomes a bottleneck. Next, explore Spring WebFlux to understand how to handle transaction management without `ThreadLocal` support (like R2DBC) in an asynchronous, non-blocking architecture.
*   **Cloud Native Spring**：研究 Spring Native 與 GraalVM，探討如何將 Spring Boot 應用編譯為 Native Image，大幅降低啟動時間與記憶體消耗，以適應 Kubernetes 與 Serverless 環境。
    *Cloud Native Spring*: Study Spring Native and GraalVM to explore compiling Spring Boot applications into Native Images, drastically reducing startup time and memory consumption to suit Kubernetes and Serverless environments.