# 1. 前言與學習目標 (Introduction and Learning Objectives)

作為一名資深工程師，你已經熟悉 Azure 的個別服務（如 App Service, SQL Database, VM）。然而，在 System Design Interview 或架構師層級的實務中，挑戰在於如何將這些服務組合成一個**高可用、可擴充且成本效益最佳化**的解決方案。本章將重點放在「架構決策」與「權衡（Trade-offs）」。

As a Senior Engineer, you are already familiar with individual Azure services (e.g., App Service, SQL Database, VM). However, in System Design Interviews or at the architect level, the challenge lies in composing these services into a **highly available, scalable, and cost-optimized** solution. This chapter focuses on "architectural decisions" and "trade-offs."

完成本章後，你應該能夠：

By the end of this chapter, you should be able to:

1.  **運用 Azure Well-Architected Framework**：在設計階段評估可靠性（Reliability）、安全性（Security）與成本（Cost）之間的取捨。
    **Apply the Azure Well-Architected Framework**: Evaluate trade-offs between Reliability, Security, and Cost during the design phase.
2.  **設計大規模分散式系統**：針對電商秒殺或影音串流等場景，選用正確的 Azure 模式（如 Queue-Based Load Leveling, CQRS, Geode Pattern）。
    **Design Large-Scale Distributed Systems**: Select the correct Azure patterns (e.g., Queue-Based Load Leveling, CQRS, Geode Pattern) for scenarios like flash sales or video streaming.
3.  **識別架構反模式（Anti-patterns）**：指出既有系統中導致效能瓶頸或成本失控的設計缺陷。
    **Identify Architectural Anti-patterns**: Pinpoint design flaws in existing systems that lead to performance bottlenecks or cost overruns.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在進入案例之前，我們需要建立正確的心智模型，這有助於在數百種 Azure 服務中快速定位。

Before diving into cases, we need to establish the right mental model to quickly navigate through hundreds of Azure services.

### 2.1 Azure Well-Architected Framework (WAF)
這不是單純的 checklist，而是設計時的「校準羅盤」。在面試中，當面試官問「如何優化這個架構？」時，你應立即從以下五個支柱切入：

This is not just a checklist, but a "calibration compass" for design. In an interview, when asked "How would you optimize this architecture?", you should immediately approach it from these five pillars:

*   **Reliability (可靠性)**: 故障復原、HA (High Availability)、DR (Disaster Recovery)。
*   **Security (安全性)**: Identity (Entra ID), Network Security (NSG, Firewall), Data Encryption。
*   **Cost Optimization (成本優化)**: Reserved Instances, Spot VMs, Auto-scaling, Serverless。
*   **Operational Excellence (維運卓越)**: IaC, CI/CD, Observability (Azure Monitor)。
*   **Performance Efficiency (效能效率)**: Caching (Redis), Partitioning (Cosmos DB), CDN。

### 2.2 服務選型的光譜 (The Spectrum of Service Selection)
不要死記硬背服務，而是根據**控制力 vs. 生產力**的光譜來選擇：

Don't memorize services by rote; instead, select them based on the **Control vs. Productivity** spectrum:

*   **IaaS (VMs, VMSS)**: 最高控制力，適合 Legacy Migration (Lift & Shift) 或需要特定 OS Kernel 設定時。
    **IaaS (VMs, VMSS)**: Highest control, suitable for Legacy Migration (Lift & Shift) or when specific OS Kernel settings are required.
*   **PaaS (App Service, Azure SQL)**: 平衡點，適合標準 Web/API 應用，由 Azure 處理 Patching 和 Scaling。
    **PaaS (App Service, Azure SQL)**: Balanced, suitable for standard Web/API apps, with Azure handling Patching and Scaling.
*   **Serverless / FaaS (Azure Functions, Logic Apps)**: 事件驅動（Event-driven），適合黏合服務（Glue code）或突發流量，但在 Cold Start 和執行時長有限制。
    **Serverless / FaaS (Azure Functions, Logic Apps)**: Event-driven, suitable for glue code or burst traffic, but with limitations on Cold Start and execution duration.

### 2.3 關鍵差異比較 (Key Differentiators)
*   **Azure Front Door vs. Traffic Manager vs. Application Gateway**:
    *   *Front Door*: Global, Layer 7 (HTTP/S), Anycast protocol, 內建 WAF 與 CDN 功能。適合全球應用。
    *   *Traffic Manager*: Global, DNS-based routing。適合非 HTTP 流量或單純的 Region 導流。
    *   *App Gateway*: Regional, Layer 7, 適合單一區域內的複雜路由與 WAF。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境中，系統設計不僅是畫方塊圖，更是解決「非功能性需求（NFRs）」的過程。

In a Production environment, system design is not just about drawing boxes; it's the process of solving "Non-Functional Requirements (NFRs)."

### 3.1 典型雲原生架構 (Typical Cloud-Native Architecture)
一個具備彈性的大型 Azure 系統通常包含以下層級：

A resilient large-scale Azure system typically includes the following layers:

1.  **Entry Point**: Azure Front Door (Global LB) + WAF (Security)。
2.  **Compute**: Azure Kubernetes Service (AKS) 或 App Service (Microservices)。
3.  **Caching**: Azure Cache for Redis (減輕 DB 壓力)。
4.  **Messaging**: Azure Event Hubs (Ingestion) 或 Service Bus (Enterprise Messaging)。
5.  **Database**: Azure Cosmos DB (Global Scale) 或 Azure SQL Hyperscale。
6.  **Observability**: Azure Monitor + Application Insights。

### 3.2 讀寫分離與數據一致性 (Read/Write Splitting & Data Consistency)
在分散式系統中，CAP 定理是無法迴避的。
*   **Azure SQL**: 利用 Read Replicas 處理讀取流量，主庫處理寫入。
*   **Cosmos DB**: 提供了 5 種一致性級別（從 Strong 到 Eventual），這是面試中的加分題。例如，購物車需要 Session Consistency，而社群動態可能只需要 Eventual Consistency。

In distributed systems, the CAP theorem is unavoidable.
*   **Azure SQL**: Use Read Replicas for read traffic, and the primary for writes.
*   **Cosmos DB**: Offers 5 consistency levels (from Strong to Eventual), which is a bonus point in interviews. For example, a shopping cart needs Session Consistency, while a social feed might only need Eventual Consistency.

---

# 4. 逐步示例：全球電商秒殺系統 (Walkthrough: Global E-commerce Flash Sale System)

### 4.1 問題背景 (Problem Context)
我們需要設計一個行銷活動系統，預計在黑色星期五會有 **100 萬使用者同時在線**，並在幾秒鐘內搶購限量商品。
**挑戰**：資料庫鎖死、伺服器過載、超賣（Overselling）。

We need to design a marketing campaign system expecting **1 million concurrent users** on Black Friday, rushing to buy limited items within seconds.
**Challenges**: Database locks, server overloads, overselling.

### 4.2 演進過程 (Evolution Process)

#### Phase 1: Naive Approach (Direct DB Access)
前端直接呼叫 API，API 直接扣庫存 (SQL `UPDATE`).
*   **結果**: SQL Deadlocks，API Timeout，系統崩潰。
*   **Result**: SQL Deadlocks, API Timeouts, System Crash.

#### Phase 2: Queue-Based Load Leveling (非同步處理)
引入 **Azure Service Bus** 或 **Event Hubs**。
1.  使用者請求進入 API。
2.  API 僅做簡單驗證，將「購買指令」丟入 Queue，立即回傳 HTTP 202 Accepted。
3.  後端 Worker (Azure Functions / AKS) 依據 DB 吞吐量，慢慢消化 Queue 中的訊息。

Introduce **Azure Service Bus** or **Event Hubs**.
1.  User request hits the API.
2.  API performs simple validation, pushes a "Buy Command" to the Queue, and immediately returns HTTP 202 Accepted.
3.  Backend Workers (Azure Functions / AKS) process messages from the Queue at a pace the DB can handle.

#### Phase 3: Redis + Lua Script (極致效能)
為了防止超賣並減少 DB IO，將庫存放入 **Azure Cache for Redis**。
*   使用 Redis `DECR` 指令或 Lua Script 原子性地扣減庫存。
*   只有扣減成功的請求，才非同步寫入 SQL/Cosmos DB 產生訂單。

To prevent overselling and reduce DB IO, store inventory in **Azure Cache for Redis**.
*   Use Redis `DECR` command or Lua Script to atomically decrement inventory.
*   Only requests that successfully decrement are asynchronously written to SQL/Cosmos DB to create orders.

### 4.3 架構設計圖 (Architecture Description)

```text
[User] -> [Azure Front Door (WAF)] 
       -> [Azure Kubernetes Service (API Gateway)]
       -> [Azure Cache for Redis (Inventory Check)] --(Success)--> [Azure Service Bus (Order Queue)]
                                                                         |
                                                                         v
                                                                 [Azure Functions (Order Processor)]
                                                                         |
                                                                         v
                                                                 [Azure Cosmos DB (Order History)]
```

### 4.4 關鍵代碼邏輯 (Key Logic Snippet)
*Cosmos DB SDK (C#) - Handling Consistency & Throughput*

```csharp
// 在高併發寫入時，我們可能選擇較弱的一致性以換取低延遲與高可用
// In high-concurrency writes, we might choose weaker consistency for low latency and high availability

CosmosClientOptions options = new CosmosClientOptions()
{
    ConsistencyLevel = ConsistencyLevel.Session, // 適合使用者讀取自己的訂單 (Suitable for users reading their own orders)
    ApplicationRegion = Regions.EastUS // 寫入主區域 (Write to primary region)
};

// 使用 Partition Key 優化查詢與寫入
// Use Partition Key to optimize queries and writes
Container container = database.GetContainer("Orders");
await container.CreateItemAsync(order, new PartitionKey(order.UserId));
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 資料庫分區錯誤 (Improper Database Partitioning)
*   **錯誤**: 在 Cosmos DB 中選擇了 Cardinality（基數）太小的 Partition Key（例如 `Status`，只有 "Active", "Completed" 幾種）。
*   **後果**: 產生 "Hot Partition"，導致單一分區的 RU (Request Units) 耗盡，引發 `429 Too Many Requests`，即使總體 RU 足夠。
*   **修正**: 選擇高基數且存取均勻的 Key，如 `UserId` 或 `DeviceId`。

*   **Mistake**: Choosing a Partition Key with low cardinality in Cosmos DB (e.g., `Status`, which only has "Active", "Completed").
*   **Consequence**: Creates a "Hot Partition," exhausting RUs (Request Units) on a single partition, triggering `429 Too Many Requests` even if total RUs are sufficient.
*   **Fix**: Choose a high-cardinality key with even access patterns, like `UserId` or `DeviceId`.

### 5.2 誤用訊息服務 (Misusing Messaging Services)
*   **錯誤**: 使用 **Azure Service Bus** 傳輸大量即時遙測數據（Telemetry Data）。
*   **後果**: 吞吐量受限，成本過高。Service Bus 設計用於高價值、交易型訊息（Enterprise Messaging）。
*   **修正**: 改用 **Azure Event Hubs**，它專為大流量串流數據（Streaming）設計，支援 Partitioning 與 Batching。

*   **Mistake**: Using **Azure Service Bus** to transmit massive amounts of real-time telemetry data.
*   **Consequence**: Throughput bottlenecks and high costs. Service Bus is designed for high-value, transactional messaging (Enterprise Messaging).
*   **Fix**: Switch to **Azure Event Hubs**, which is designed for high-throughput streaming data, supporting Partitioning and Batching.

### 5.3 忽略出口流量成本 (Ignoring Egress Costs)
*   **錯誤**: 跨區域（Cross-Region）頻繁傳輸大量數據，或未透過 CDN 直接從 Blob Storage 提供靜態內容。
*   **後果**: 月底帳單爆炸。
*   **修正**: 盡量將 Compute 與 Data 放在同一 Region；使用 Azure Front Door / CDN 快取靜態資源。

*   **Mistake**: Frequent large data transfers across regions, or serving static content directly from Blob Storage without a CDN.
*   **Consequence**: Bill shock at the end of the month.
*   **Fix**: Keep Compute and Data in the same Region whenever possible; use Azure Front Door / CDN to cache static resources.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何設計一個跨區域的高可用架構 (Multi-Region HA Architecture)？
*   **切入點**: 主動-主動 (Active-Active) vs. 主動-被動 (Active-Passive)。
*   **高分回答要點**:
    *   前端使用 **Azure Front Door** 進行流量導引與 Health Probe。
    *   資料層使用 **Cosmos DB (Multi-master writes)** 或 **Azure SQL (Failover Groups)**。
    *   考慮 **RPO (Recovery Point Objective)** 與 **RTO (Recovery Time Objective)** 的需求差異。
    *   提到 **Data Residency** (法規要求數據不能離開特定國家) 的限制。

*   **Hook**: Active-Active vs. Active-Passive.
*   **Key Points for High Score**:
    *   Use **Azure Front Door** for traffic routing and Health Probes at the frontend.
    *   Use **Cosmos DB (Multi-master writes)** or **Azure SQL (Failover Groups)** at the data layer.
    *   Consider the trade-offs between **RPO** and **RTO**.
    *   Mention **Data Residency** constraints (compliance requiring data to stay within specific countries).

### Q2: 在 Azure 中，如何處理「分散式交易 (Distributed Transactions)」？
*   **切入點**: 避免 2PC (Two-Phase Commit)，改用 Saga Pattern。
*   **高分回答要點**:
    *   解釋為何在雲端環境 2PC 效能差且不可靠。
    *   描述 **Saga Pattern**：透過一系列本地交易 (Local Transactions) + 訊息驅動 (Event-driven) 來完成。
    *   使用 **Azure Logic Apps** 或 **Durable Functions** 作為 Orchestrator 來管理狀態與補償交易 (Compensating Transactions)。

*   **Hook**: Avoid 2PC, use Saga Pattern.
*   **Key Points for High Score**:
    *   Explain why 2PC performs poorly and is unreliable in cloud environments.
    *   Describe the **Saga Pattern**: Achieved through a series of Local Transactions + Event-driven messaging.
    *   Use **Azure Logic Apps** or **Durable Functions** as an Orchestrator to manage state and Compensating Transactions.

### Q3: 如何將單體應用 (Monolith) 遷移至 Azure Microservices？
*   **切入點**: Strangler Fig Pattern (絞殺榕模式)。
*   **高分回答要點**:
    *   不要試圖一次性重寫 (Big Bang rewrite)。
    *   在單體前架設 **Azure API Management (APIM)** 或 **App Gateway**。
    *   逐步將特定功能（如「搜尋」、「使用者資料」）剝離為獨立的 Microservice (AKS/Functions)。
    *   利用 APIM 的路由規則，將流量漸進式切換到新服務。

*   **Hook**: Strangler Fig Pattern.
*   **Key Points for High Score**:
    *   Avoid a Big Bang rewrite.
    *   Place **Azure API Management (APIM)** or **App Gateway** in front of the monolith.
    *   Gradually peel off specific features (e.g., "Search", "User Profile") into independent Microservices (AKS/Functions).
    *   Use APIM routing rules to progressively switch traffic to the new services.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章記憶錨點 (Key Takeaways)
1.  **WAF 是核心**: 設計任何系統時，隨時檢視 Reliability, Security, Cost, Operations, Performance。
2.  **非同步解耦**: 使用 Queue (Service Bus) 或 Stream (Event Hubs) 來緩衝突發流量，保護資料庫。
3.  **全域流量管理**: Azure Front Door 是 Layer 7 全球路由的首選。
4.  **資料庫選擇**: 了解 SQL (關聯式) 與 Cosmos DB (NoSQL) 的適用場景及一致性模型。
5.  **快取策略**: Redis 是提升讀取效能與保護後端的關鍵。

1.  **WAF is Core**: Always review Reliability, Security, Cost, Operations, and Performance when designing any system.
2.  **Async Decoupling**: Use Queues (Service Bus) or Streams (Event Hubs) to buffer burst traffic and protect the database.
3.  **Global Traffic Management**: Azure Front Door is the go-to choice for Layer 7 global routing.
4.  **Database Selection**: Understand the use cases and consistency models for SQL (Relational) vs. Cosmos DB (NoSQL).
5.  **Caching Strategy**: Redis is key to improving read performance and protecting the backend.

### 後續延伸 (Next Steps)
*   **Infrastructure as Code (IaC)**: 學習如何使用 **Terraform** 或 **Azure Bicep** 來自動化部署上述架構（Chapter 11 將深入探討）。
*   **Security Deep Dive**: 研究 **Managed Identity** 與 **Key Vault** 的整合，實現無密碼存取 (Passwordless access)。
*   **Observability**: 實作 Distributed Tracing，將 Front Door, APIM, AKS, 與 SQL 的 Log 串聯起來。