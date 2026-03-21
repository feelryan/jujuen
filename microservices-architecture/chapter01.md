# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，最困難的決定往往不是「如何構建微服務」，而是「如何正確地拆分」以及「何時不該拆分」。本章將超越基礎定義，深入探討如何利用領域驅動設計（DDD）來劃分服務邊界，這是避免系統演變成「分散式大泥球（Distributed Monolith）」的關鍵。

In a Senior Software Engineer's career, the hardest decision is often not "how to build microservices," but "how to decompose correctly" and "when not to." This chapter goes beyond basic definitions to explore how to leverage Domain-Driven Design (DDD) for defining service boundaries—the key to preventing your system from devolving into a "Distributed Monolith."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **運用 Bounded Context 劃分邊界**：能夠識別業務領域中的語言歧義，並以此定義微服務的邏輯邊界，而非僅依據技術層（如 UI/DB）拆分。
    **Define boundaries using Bounded Contexts**: Identify linguistic ambiguities in the business domain to define logical service boundaries, rather than splitting solely by technical layers (e.g., UI/DB).

2.  **評估拆分策略的權衡（Trade-offs）**：在 System Design 面試或架構會議中，能清晰論述 Monolith 與 Microservices 在資料一致性、部署獨立性與維運複雜度上的取捨。
    **Evaluate decomposition trade-offs**: Articulate the trade-offs between Monolith and Microservices regarding data consistency, deployment independence, and operational complexity during System Design interviews or architecture reviews.

3.  **識別並重構反模式**：能一眼看出「共用資料庫（Shared Database）」與「實體服務（Entity Services）」等常見陷阱，並提出基於「扼殺者模式（Strangler Fig Pattern）」的遷移計畫。
    **Identify and refactor anti-patterns**: Spot common pitfalls like "Shared Database" and "Entity Services," and propose migration plans based on the "Strangler Fig Pattern."

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 領域驅動設計與通用語言 (DDD & Ubiquitous Language)

**心智模型**：將微服務視為一個個獨立運作的「子公司」，而非同一間大辦公室裡的不同「職能部門」。每個子公司（微服務）都有自己的帳本（資料庫）和術語定義。

**Mental Model**: Treat microservices as autonomous "subsidiaries" rather than different "functional departments" in a large open-plan office. Each subsidiary (microservice) has its own ledger (database) and definition of terms.

在 DDD 中，最重要的概念是 **Bounded Context（邊界上下文）**。同一個名詞在不同的 Context 下有不同的意義。
In DDD, the most critical concept is the **Bounded Context**. The same noun can have different meanings in different contexts.

*   **Context A (E-commerce / Sales)**: `Product` 關注的是價格、描述、圖片。
*   **Context B (Inventory / Warehouse)**: `Product` 關注的是重量、尺寸、貨架位置、SKU。

**關鍵差異**：初階工程師傾向建立一個包含所有屬性的巨大 `Product` Class；資深工程師則會建立兩個獨立的模型，分別存在於不同的服務中，僅透過 ID 關聯。
**Key Difference**: Junior engineers tend to create a massive `Product` class containing all attributes; Senior engineers create two independent models residing in separate services, linked only by ID.

### 2.2 業務能力 vs. 技術層 (Business Capabilities vs. Technical Layers)

**定義**：微服務應圍繞「業務能力（Business Capability）」組織，而非技術層。
**Definition**: Microservices should be organized around "Business Capabilities," not technical layers.

*   **錯誤拆分 (Wrong)**: UI Service, Logic Service, Database Service. (這是分散式的單體，變更通常需要跨服務協調)。
*   **正確拆分 (Right)**: Order Service, Shipping Service, User Profile Service. (這是垂直切分，包含該領域的 UI、Logic 與 DB)。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與 System Design 面試中，拆分策略直接決定了系統的 **Availability（可用性）** 與 **Maintainability（可維護性）**。

In production environments and System Design interviews, decomposition strategies directly dictate the system's **Availability** and **Maintainability**.

### 3.1 康威定律的體現 (Manifestation of Conway's Law)
系統設計往往會複製組織的溝通結構。如果你希望服務解耦，團隊結構必須先解耦（例如：Two-pizza teams 負責端到端的服務）。
System design often copies the organization's communication structure. If you want decoupled services, your team structure must be decoupled first (e.g., Two-pizza teams owning services end-to-end).

### 3.2 資料庫設計視角 (Database Design Perspective)
這是最常被挑戰的點。在 Monolith 中，我們習慣用 `JOIN` 查詢跨表資料。在 Microservices 架構下，必須嚴格遵守 **Database-per-Service** 原則。
This is the most frequently challenged point. In a Monolith, we rely on `JOIN`s for cross-table data. In Microservices architecture, the **Database-per-Service** principle must be strictly adhered to.

*   **Impact**: 強一致性（ACID）轉變為最終一致性（Eventual Consistency/BASE）。
*   **Design**: 跨服務查詢需透過 API Composition 或 CQRS（Command Query Responsibility Segregation）。

### 3.3 典型架構圖描述 (Typical Architecture Description)
一個成熟的拆分架構通常包含：
A mature decomposed architecture typically includes:

1.  **API Gateway / BFF**: 負責路由與聚合，隱藏後端拆分細節。
2.  **Domain Services**: 核心業務邏輯（如 Order Service），擁有獨立 DB。
3.  **Anti-Corruption Layer (ACL)**: 當新服務需與 Legacy Monolith 溝通時，透過 ACL 轉換模型，防止 Legacy 的髒模型污染新服務。

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例背景 (Scenario)
我們有一個單體電商系統（Legacy Monolith），包含使用者管理、商品目錄、訂單處理與庫存管理。隨著流量增長，庫存系統在高併發下成為瓶頸，且業務團隊希望頻繁更新庫存邏輯，不影響訂單系統。

We have a legacy e-commerce monolith containing User Management, Product Catalog, Order Processing, and Inventory Management. As traffic grows, the inventory system becomes a bottleneck under high concurrency, and the business team wants to update inventory logic frequently without affecting the order system.

### 步驟 1：識別 Bounded Context (Identify Bounded Contexts)
我們發現 `Item` 這個概念在「訂單」與「庫存」中有歧義。

We discover that the concept of `Item` is ambiguous between "Order" and "Inventory."

*   **Order Context**: 關心 `price`, `discount`, `productName`.
*   **Inventory Context**: 關心 `stockCount`, `warehouseLocation`, `restockThreshold`.

### 步驟 2：定義資料擁有權 (Define Data Ownership)
**Naive Approach (Anti-pattern)**:
直接把程式碼拆成兩個專案，但仍然連線到同一個 `e_commerce_db`。
Simply splitting the code into two projects but still connecting to the same `e_commerce_db`.

**Mature Solution**:
將庫存相關的資料表（Inventory Tables）遷移到獨立的資料庫 `inventory_db`。

Migrate inventory-related tables to a separate database `inventory_db`.

### 步驟 3：處理跨服務溝通 (Handle Cross-Service Communication)
當使用者下單時，Order Service 需要扣庫存。

When a user places an order, the Order Service needs to deduct inventory.

```java
// Pseudo-code: Order Service (Inside Order Context)

public class OrderService {
    // 依賴的是介面，而非另一個服務的具體實作
    // Dependency is on an interface, not the implementation of another service
    private final InventoryClient inventoryClient; 

    public void placeOrder(OrderRequest request) {
        // 1. Create Order (Local Transaction)
        Order order = orderRepository.save(new Order(request));

        // 2. Call Inventory Service (RPC / REST)
        // 注意：這裡沒有 DB Transaction 跨越兩個服務
        // Note: No DB transaction spans across two services
        boolean reserved = inventoryClient.reserveStock(
            request.getProductId(), 
            request.getQuantity()
        );

        if (!reserved) {
            // 3. Compensating Action (if synchronous)
            order.setStatus(OrderStatus.FAILED);
            orderRepository.save(order);
            throw new OutOfStockException();
        }
    }
}
```

### 步驟 4：扼殺者模式 (Strangler Fig Pattern)
不要一次重寫整個系統。
1.  在 Monolith 前面加一個 Proxy (API Gateway)。
2.  將 `/api/inventory` 的流量導向新的 Inventory Microservice。
3.  其他流量繼續導向 Monolith。
4.  逐步搬遷，直到 Monolith 消失或縮小。

Do not rewrite the whole system at once.
1. Place a Proxy (API Gateway) in front of the Monolith.
2. Route `/api/inventory` traffic to the new Inventory Microservice.
3. Continue routing other traffic to the Monolith.
4. Gradually migrate until the Monolith disappears or shrinks.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 分散式大泥球 (The Distributed Monolith)
**描述**：服務拆分了，但它們緊密耦合，必須一起部署，且頻繁進行同步呼叫。
**Description**: Services are split, but they are tightly coupled, must be deployed together, and make frequent synchronous calls.
**為何不好**：你獲得了微服務的所有缺點（延遲、複雜度），卻沒得到優點（獨立部署、彈性）。
**Why it's bad**: You get all the downsides of microservices (latency, complexity) without the benefits (independent deployment, resilience).

### 5.2 共用資料庫 (Shared Database)
**描述**：多個服務讀寫同一個 Schema。
**Description**: Multiple services reading/writing to the same Schema.
**為何不好**：資料庫成為隱藏的耦合點。修改 Table 結構會導致不知名的服務崩潰。無法針對特定服務優化 DB 選型（如 SQL vs NoSQL）。
**Why it's bad**: The database becomes a hidden coupling point. Changing table structure breaks unknown services. Prevents optimizing DB choice per service (e.g., SQL vs NoSQL).

### 5.3 實體服務 (Entity Services)
**描述**：建立 `OrderService`, `ProductService`, `CustomerService` 僅僅是為了對資料庫做 CRUD，沒有業務邏輯。
**Description**: Creating `OrderService`, `ProductService`, `CustomerService` solely to perform CRUD on the database, with no business logic.
**為何不好**：這將導致「貧血模型（Anemic Domain Model）」。業務邏輯會散落在上層的 Orchestrator 中，導致大量的跨服務呼叫（Chatty I/O）。
**Why it's bad**: This leads to an "Anemic Domain Model." Business logic gets scattered in upper-layer orchestrators, causing excessive cross-service calls (Chatty I/O).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何決定何時將一個功能從 Monolith 拆分為 Microservice？
**How do you decide when to extract a feature from a Monolith into a Microservice?**

*   **高分回答要點**：
    *   **變更頻率 (Rate of Change)**: 該模組是否比系統其他部分演進得更快？
    *   **資源需求 (Resource Requirements)**: 是否需要獨立擴展（例如：影像處理需要 GPU，而 CRUD 只需要 CPU）？
    *   **團隊邊界 (Team Boundaries)**: 是否有一個獨立團隊負責該領域？
    *   **避免過早優化**: 強調 "Monolith First" 策略，直到複雜度證明拆分的必要性。

### Q2: 如果兩個服務需要共享資料（例如 User ID 和 Basic Info），你會怎麼設計？
**If two services need to share data (e.g., User ID and Basic Info), how would you design it?**

*   **高分回答要點**：
    *   **拒絕 Shared DB**。
    *   **資料複製 (Data Duplication)**: 下游服務只儲存它需要的欄位副本（例如 Order Service 存一份 User 的 `name` 和 `shipping_address`）。
    *   **事件驅動同步 (Event-Driven Synchronization)**: 當 User Service 更新資料時，發出 `UserUpdated` 事件，其他服務訂閱並更新本地副本。
    *   **接受最終一致性**。

### Q3: 什麼是扼殺者模式（Strangler Fig Pattern），它解決了什麼問題？
**What is the Strangler Fig Pattern, and what problem does it solve?**

*   **高分回答要點**：
    *   解決 "Big Bang Rewrite" 的高風險問題。
    *   透過攔截呼叫（Interception）逐步替換舊系統功能。
    *   允許新舊系統共存，降低遷移風險，並能快速回滾。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點 (Key Takeaways)
1.  **Bounded Context 是核心**：依據語言邊界而非技術層來拆分服務。
2.  **Database per Service**：這是微服務架構不可妥協的原則，以確保鬆耦合。
3.  **避免分散式單體**：如果兩個服務必須同時部署，它們就不應該被分開。
4.  **Strangler Fig Pattern**：是遷移 Legacy 系統最穩健的策略。
5.  **接受資料冗餘**：為了服務的自主性，適度的資料複製是可以接受的。

### 後續延伸 (Next Steps)
一旦服務被拆分，它們之間的通訊就成為新的挑戰。下一章我們將探討：
Once services are decomposed, communication between them becomes the new challenge. In the next chapter, we will explore:

*   **同步 vs 非同步通訊 (Synchronous vs. Asynchronous Communication)**
*   **REST/gRPC vs. Message Queues (Kafka/RabbitMQ)**
*   **如何處理分散式交易 (Saga Pattern)**

建議讀者嘗試在現有專案中，畫出目前的 Context Map，並標記出哪些區域存在「語言歧義」或「不當耦合」。
Readers are encouraged to draw a Context Map of their current project and identify areas with "linguistic ambiguity" or "improper coupling."