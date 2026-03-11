# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲端原生架構（Cloud-Native Architecture）的旅程中，最困難的往往不是技術選型（Kubernetes vs. Serverless），而是如何正確地劃分系統邊界。錯誤的拆分會導致「分散式單體（Distributed Monolith）」，這比傳統單體更難維護且效能更差。本章將結合領域驅動設計（DDD）與絞殺榕模式（Strangler Fig Pattern），探討如何安全且有效地拆解系統。

In the journey of Cloud-Native Architecture, the most challenging part is often not the technology selection (Kubernetes vs. Serverless), but how to correctly define system boundaries. Incorrect decomposition leads to a "Distributed Monolith," which is harder to maintain and performs worse than a traditional monolith. This chapter combines Domain-Driven Design (DDD) and the Strangler Fig Pattern to explore how to decompose systems safely and effectively.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用 DDD 界限上下文（Bounded Contexts）**：識別業務領域邊界，而非僅僅依據資料表或技術層級來拆分服務。
    **Apply DDD Bounded Contexts**: Identify business domain boundaries instead of decomposing services solely based on database tables or technical layers.
2.  **實作 Strangler Fig Pattern**：制定從單體架構逐步遷移至微服務的具體路徑，確保遷移過程中的業務連續性。
    **Implement the Strangler Fig Pattern**: Formulate a concrete path to migrate from a monolith to microservices incrementally, ensuring business continuity during the process.
3.  **識別並避免分散式單體**：理解高耦合（Coupling）帶來的延遲與維護成本，並學會使用非同步通訊或資料複製來解耦。
    **Identify and Avoid Distributed Monoliths**: Understand the latency and maintenance costs caused by high coupling, and learn to decouple using asynchronous communication or data replication.
4.  **處理跨服務資料一致性**：在拆分資料庫時，能夠針對 Foreign Key 依賴與交易需求提出合理的解決方案（如 Saga 或 Eventual Consistency）。
    **Handle Cross-Service Data Consistency**: Propose reasonable solutions for Foreign Key dependencies and transaction requirements (such as Saga or Eventual Consistency) when splitting databases.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 領域驅動設計與界限上下文 (DDD & Bounded Contexts)

**直覺類比**：想像一家大型跨國公司。同樣是「客戶（Customer）」這個詞，在「銷售部門」眼裡代表潛在的營收機會（Lead/Opportunity）；而在「物流部門」眼裡則代表收貨地址與聯絡人（Shipping Info）。這兩個部門雖然都處理「客戶」，但關注的屬性與行為截然不同。這兩個部門就是不同的「界限上下文」。

**Intuitive Analogy**: Imagine a large multinational corporation. The term "Customer" means something different to the "Sales Department" (a potential revenue opportunity/lead) than it does to the "Logistics Department" (shipping address and contact info). Although both deal with "Customers," their focus on attributes and behaviors is distinct. These two departments represent different "Bounded Contexts."

**正規定義**：
-   **Bounded Context（界限上下文）**：是特定領域模型適用的邊界。微服務的邊界應當與 Bounded Context 對齊，而非與資料庫表對齊。
-   **Context Map（上下文對應圖）**：定義不同上下文之間的關係（如 Shared Kernel, Customer/Supplier, Anti-Corruption Layer）。

**Formal Definition**:
-   **Bounded Context**: The boundary within which a specific domain model applies. Microservice boundaries should align with Bounded Contexts, not necessarily with database tables.
-   **Context Map**: Defines the relationships between different contexts (e.g., Shared Kernel, Customer/Supplier, Anti-Corruption Layer).

### 2.2 絞殺榕模式 (Strangler Fig Pattern)

**概念**：這是一種遷移策略，源自於榕樹種子落在宿主樹上，根系逐漸向下包圍宿主，最終取代宿主。在軟體中，這意味著在舊系統周圍建立新服務，逐步攔截流量，直到舊系統不再被需要。

**Concept**: A migration strategy inspired by fig seeds landing on a host tree, sending roots down to envelop and eventually replace the host. In software, this means building new services around the legacy system, gradually intercepting traffic until the legacy system is no longer needed.

### 2.3 服務粒度：微服務 vs. 奈米服務 (Service Granularity: Microservices vs. Nanoservices)

**心智模型**：
-   **Monolith**：高內聚（Cohesion），但高耦合（Coupling）。部署牽一髮動全身。
-   **Microservice**：適度內聚，低耦合。一個服務由一個「Two-pizza team」維護。
-   **Nanoservice**：反模式。粒度過細（例如每個 Function 一個服務），導致維運開銷（Overhead）遠大於業務價值。

**Mental Model**:
-   **Monolith**: High cohesion, but high coupling. Deployment affects everything.
-   **Microservice**: Moderate cohesion, low coupling. Maintained by a "Two-pizza team."
-   **Nanoservice**: Anti-pattern. Too granular (e.g., one service per function), resulting in operational overhead that far exceeds business value.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與系統設計面試中，拆分策略直接決定了系統的**可維護性 (Maintainability)** 與 **可用性 (Availability)**。

In production environments and system design interviews, the decomposition strategy directly determines the system's **Maintainability** and **Availability**.

### 3.1 典型架構角色 (Typical Architecture Roles)

當我們開始拆分單體時，架構通常會演變為：

When we start decomposing a monolith, the architecture typically evolves into:

1.  **API Gateway / Load Balancer**: 負責流量路由。它需要具備智慧路由能力，將特定 URL 路徑（如 `/api/v1/orders`）導向新服務，而將其餘流量導向舊單體。
    **API Gateway / Load Balancer**: Responsible for traffic routing. It needs intelligent routing capabilities to direct specific URL paths (e.g., `/api/v1/orders`) to new services while directing the rest to the legacy monolith.
2.  **The Glue Code (Anti-Corruption Layer)**: 在新舊系統之間轉換資料格式的適配層，防止舊系統的糟糕設計汙染新服務。
    **The Glue Code (Anti-Corruption Layer)**: An adapter layer that translates data formats between new and old systems, preventing the legacy system's poor design from polluting the new services.
3.  **CDC (Change Data Capture) Pipeline**: 用於將舊資料庫的變更即時同步到新服務的資料庫，確保雙寫（Dual Write）或遷移期間的資料一致性。
    **CDC (Change Data Capture) Pipeline**: Used to synchronize changes from the legacy database to the new service's database in real-time, ensuring data consistency during dual-write or migration phases.

### 3.2 對非功能性需求的影響 (Impact on Non-Functional Requirements)

-   **可擴充性 (Scalability)**：我們可以獨立擴展「熱點服務」（如秒殺系統中的 Inventory Service），而不需複製整個龐大的單體。
    **Scalability**: We can independently scale "hot services" (like the Inventory Service in a flash sale system) without replicating the entire massive monolith.
-   **容錯性 (Resilience)**：透過 **Bulkhead Pattern（艙壁模式）**，當「推薦服務」掛掉時，不會影響核心的「結帳流程」。但在分散式單體中，一個同步呼叫的失敗可能導致連鎖崩潰。
    **Resilience**: Through the **Bulkhead Pattern**, if the "Recommendation Service" fails, it won't affect the core "Checkout Flow." However, in a distributed monolith, a failure in a synchronous call can lead to cascading failures.

---

# 4. 逐步示例：拆解電子商務訂單模組 (Walkthrough: Decomposing E-commerce Order Module)

假設我們有一個基於 Java/Spring 或 Node.js 的單體電商系統，目標是將「訂單管理 (Order Management)」拆分為獨立微服務。

Assume we have a monolithic E-commerce system based on Java/Spring or Node.js. The goal is to extract "Order Management" into an independent microservice.

### Step 1: 識別接縫 (Identify the Seams)

首先，我們不看程式碼，而是看資料。找出 `orders`、`order_items` 表格與其他表格（如 `users`、`products`）的關聯。
**挑戰**：`orders` 表格通常有 `user_id` 作為 Foreign Key。在單體中，我們習慣用 `JOIN` 查詢來獲取用戶詳情。

First, we look at the data, not just the code. Identify the relationships between `orders`, `order_items` tables, and others (like `users`, `products`).
**Challenge**: The `orders` table usually has `user_id` as a Foreign Key. In a monolith, we are used to using `JOIN` queries to fetch user details.

### Step 2: 定義服務邊界與 API (Define Boundaries & API)

新服務 `OrderService` 不應直接存取 `users` 表。它應該只儲存 `user_id`，並在需要詳情時呼叫 `UserService`（或依賴資料複製）。

The new `OrderService` should not directly access the `users` table. It should only store `user_id` and call `UserService` (or rely on data replication) when details are needed.

**Naive Approach (Bad)**:
```typescript
// In OrderService
async function getOrderDetails(orderId) {
  const order = await db.orders.find(orderId);
  // Synchronous HTTP call over network - Dangerous coupling!
  const user = await httpClient.get(`http://monolith/users/${order.userId}`);
  return { ...order, user };
}
```

**Better Approach (CQRS / Data Replication)**:
`OrderService` 訂閱 `UserUpdated` 事件，並在本地保留一份最小化的 User 副本（例如只存 `id`, `name`, `email`）。這樣讀取時無需跨服務呼叫。

`OrderService` subscribes to `UserUpdated` events and keeps a minimal local replica of the User (e.g., only `id`, `name`, `email`). This way, reads do not require cross-service calls.

### Step 3: 實施 Strangler Fig (Implement Strangler Fig)

我們使用 API Gateway 進行流量切換。

We use an API Gateway for traffic switching.

1.  **Deploy New Service**: 部署 `OrderService`，但暫不接管寫入流量。
    **Deploy New Service**: Deploy `OrderService`, but do not take over write traffic yet.
2.  **Shadow Traffic / Dark Launch**: 將生產環境的請求異步複製一份給 `OrderService`，驗證其邏輯與效能，但不回傳結果給用戶。
    **Shadow Traffic / Dark Launch**: Asynchronously copy production requests to `OrderService` to verify logic and performance, without returning results to the user.
3.  **Canary Release (Read)**: 將 1% 的讀取流量導向新服務。
    **Canary Release (Read)**: Route 1% of read traffic to the new service.
4.  **Migrate Writes (The Hardest Part)**:
    -   方案 A：雙寫（Dual Write）。應用程式同時寫入舊 DB 與新 DB。缺點是容易不一致。
    -   方案 B：資料庫同步。寫入舊 DB，透過 CDC (e.g., Debezium) 同步到新 DB。切換時，短暫停機或設為 Read-only，確認同步完成後，將 Gateway 指向新服務。

    -   **Option A: Dual Write**. The application writes to both the old DB and the new DB. The downside is potential inconsistency.
    -   **Option B: Database Sync**. Write to the old DB and sync to the new DB via CDC (e.g., Debezium). During the switch, briefly pause or set to Read-only, confirm sync is complete, then point the Gateway to the new service.

### Step 4: 清理 (Cleanup)

一旦流量 100% 轉移且穩定運行，移除單體中的 `Order` 相關程式碼與資料表。

Once traffic is 100% migrated and stable, remove the `Order` related code and tables from the monolith.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 分散式單體 (The Distributed Monolith)

**描述**：你拆分了服務，但服務之間充滿了同步的 HTTP/gRPC 呼叫。服務 A 為了完成請求，必須呼叫服務 B，B 又呼叫 C。
**後果**：延遲疊加（Latency adds up）、可用性降低（Availability = A * B * C）、部署必須協調順序。
**修正**：改用**事件驅動架構（Event-Driven Architecture）**，讓服務依賴本地資料或快取，減少執行時的外部依賴。

**Description**: You split the services, but they are full of synchronous HTTP/gRPC calls. Service A must call Service B, which calls Service C, to fulfill a request.
**Consequences**: Latency adds up, availability decreases (Availability = A * B * C), and deployments must be coordinated.
**Fix**: Switch to **Event-Driven Architecture**, letting services rely on local data or caches to reduce runtime external dependencies.

### 5.2 共享資料庫 (Shared Database)

**描述**：多個微服務連線到同一個實體資料庫，甚至存取相同的 Table。
**後果**：這不是微服務。任何 Schema 變更都會破壞其他服務；無法獨立擴展資料庫資源；鎖競爭（Lock Contention）。
**修正**：**Database-per-Service**。如果需要共享資料，透過 API 或事件流（Event Stream）傳遞。

**Description**: Multiple microservices connect to the same physical database, or even access the same tables.
**Consequences**: This is not microservices. Any Schema change breaks other services; database resources cannot be scaled independently; Lock Contention.
**Fix**: **Database-per-Service**. If data needs to be shared, pass it via APIs or Event Streams.

### 5.3 忽略報告與分析需求 (Ignoring Reporting & Analytics)

**描述**：拆分資料庫後，原本簡單的 `JOIN` 報表查詢變得不可能執行。
**後果**：業務端無法獲取報表，或者工程師在應用層做低效的 In-memory JOIN。
**修正**：在架構設計初期就引入 **Data Warehouse** 或 **Data Lake**，透過 ETL/ELT 將各個微服務的資料匯總到分析專用資料庫。

**Description**: After splitting the database, originally simple `JOIN` report queries become impossible to execute.
**Consequences**: The business side cannot get reports, or engineers perform inefficient In-memory JOINs at the application layer.
**Fix**: Introduce a **Data Warehouse** or **Data Lake** early in the architecture design, aggregating data from various microservices into an analytics-specific database via ETL/ELT.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: "我們有一個巨大的單體系統，想要遷移到微服務，你建議怎麼開始？"
**"We have a massive monolith and want to migrate to microservices. How would you suggest we start?"**

**高分回答要點 (Key Points for a High Score)**：
1.  **不要 Big Bang Rewrite**：強調風險，提倡 Strangler Fig Pattern。
2.  **以業務價值為導向**：優先拆分變更頻率高、需要獨立擴展或技術異構的模組（例如需要用 Python 做 AI 推薦的模組）。
3.  **定義邊界**：提及 DDD Bounded Context，強調資料庫拆分比程式碼拆分更重要且更難。
4.  **基礎設施先行**：在拆分前，先建立 CI/CD、Logging、Tracing (OpenTelemetry) 等可觀測性基礎設施。

**Key Points**:
1.  **No Big Bang Rewrite**: Emphasize risk, advocate for the Strangler Fig Pattern.
2.  **Business Value Driven**: Prioritize modules that change frequently, need independent scaling, or require heterogeneous technology (e.g., an AI recommendation module needing Python).
3.  **Define Boundaries**: Mention DDD Bounded Contexts, emphasizing that database splitting is more critical and difficult than code splitting.
4.  **Infrastructure First**: Establish observability infrastructure like CI/CD, Logging, and Tracing (OpenTelemetry) before splitting.

### Q2: "拆分後，原本的資料庫 Transaction (ACID) 怎麼辦？"
**"After splitting, what happens to the original database transactions (ACID)?"**

**高分回答要點 (Key Points for a High Score)**：
1.  **承認失去 ACID**：跨服務無法維持強一致性（Strong Consistency）。
2.  **最終一致性 (Eventual Consistency)**：這是 Cloud-Native 的常態。
3.  **Saga Pattern**：解釋 Choreography（基於事件）與 Orchestration（基於指揮器）兩種 Saga 模式來處理長流程交易。
4.  **補償交易 (Compensating Transaction)**：如果步驟 B 失敗，必須觸發回滾邏輯來撤銷步驟 A 的操作。

**Key Points**:
1.  **Acknowledge Loss of ACID**: Strong consistency cannot be maintained across services.
2.  **Eventual Consistency**: This is the norm in Cloud-Native.
3.  **Saga Pattern**: Explain Choreography (event-based) and Orchestration (orchestrator-based) Saga patterns for handling long-running transactions.
4.  **Compensating Transaction**: If step B fails, rollback logic must be triggered to undo step A's operation.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點 (Key Takeaways)
1.  **邊界優先 (Boundaries First)**：使用 DDD 界限上下文來指導拆分，而非技術層級。
2.  **資料庫是核心 (Database is Core)**：如果資料庫沒拆開，就不是真正的微服務。Database-per-service 是黃金法則。
3.  **絞殺榕模式 (Strangler Fig)**：是降低遷移風險的最佳實踐，利用 API Gateway 逐步切換流量。
4.  **避免分散式單體 (Avoid Distributed Monolith)**：減少同步呼叫，善用非同步事件與資料複製。
5.  **接受最終一致性 (Embrace Eventual Consistency)**：這是換取高可用性與可擴充性的必要代價。

### 後續延伸 (Next Steps)
-   **Next Chapter**: 深入探討 **微服務通訊模式 (Microservices Communication Patterns)**。比較 REST, gRPC, 與 GraphQL 的適用場景，以及 Message Queue (Kafka/RabbitMQ) 的進階應用。
-   **Action Item**: 檢視你當前的專案，找出一個「上帝類別 (God Class)」或「巨型表格」，嘗試畫出它的 Context Map，看看它是否跨越了多個業務領域。

-   **Next Chapter**: Deep dive into **Microservices Communication Patterns**. Compare use cases for REST, gRPC, and GraphQL, and advanced applications of Message Queues (Kafka/RabbitMQ).
-   **Action Item**: Review your current project, identify a "God Class" or "Giant Table," and try to draw its Context Map to see if it spans multiple business domains.