# Chapter 04: Data Storage Patterns and Consistency Models
# 第四章：資料儲存與強一致性模型

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In distributed system design, data storage is often the primary bottleneck for scalability and availability. As a Senior Engineer, simply knowing "how to write SQL" or "how to upload a file" is insufficient. You must master the trade-offs between consistency, latency, and throughput (CAP Theorem) and apply them to Azure's specific services.

在分散式系統設計中，資料儲存往往是擴充性與可用性的主要瓶頸。作為資深工程師，僅僅知道「如何寫 SQL」或「如何上傳檔案」是不夠的。你必須掌握一致性、延遲與吞吐量之間的權衡（CAP 定理），並將其應用於 Azure 的特定服務中。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Demystify Cosmos DB Consistency Levels**: Explain the precise behavior of the 5 consistency levels and choose the right one for specific business scenarios (e.g., Shopping Cart vs. Financial Ledger).
    **解構 Cosmos DB 一致性級別**：解釋 5 種一致性級別的精確行為，並針對特定商業場景（如購物車 vs. 金融帳本）選擇合適的級別。
2.  **Architect Azure SQL Sharding**: Design a horizontally scalable relational database strategy using Elastic Database tools to handle multi-tenant or high-volume workloads.
    **架構 Azure SQL 分片**：使用 Elastic Database 工具設計水平擴充的關聯式資料庫策略，以處理多租戶或高流量負載。
3.  **Optimize Blob Storage for Big Data**: Implement Lifecycle Management policies and Hierarchical Namespaces (ADLS Gen2) to balance cost and performance for petabyte-scale data.
    **優化大數據的 Blob 儲存**：實作生命週期管理策略與階層式命名空間（ADLS Gen2），以在 PB 級資料規模下平衡成本與效能。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Spectrum of Consistency (Cosmos DB)
### 2.1 一致性的光譜 (Cosmos DB)

In traditional databases, we often think in binary terms: Strong Consistency (ACID) vs. Eventual Consistency (BASE). Azure Cosmos DB breaks this mental model by offering a **tunable spectrum** of 5 levels.
在傳統資料庫中，我們常以二元對立思考：強一致性 (ACID) vs. 最終一致性 (BASE)。Azure Cosmos DB 打破了這個心智模型，提供了 5 個**可調整的光譜**級別。

Think of this as a slider between **Latency/Availability** and **Data Accuracy**:
請將其想像為在 **延遲/可用性** 與 **資料準確性** 之間的滑桿：

1.  **Strong (強一致性)**: Linearizability. Everyone sees the latest write immediately. Highest latency, lowest availability (read/write must acknowledge across regions).
    **Strong**：線性一致性。所有人立即看到最新的寫入。延遲最高，可用性最低（讀寫必須跨區域確認）。
2.  **Bounded Staleness (有限過期)**: "Consistent, but lagged." Reads lag behind writes by a configured time ($K$ seconds) or version count ($T$ updates). Good for dashboards (e.g., stock tickers).
    **Bounded Staleness**：「一致，但有延遲」。讀取落後於寫入一個設定的時間（$K$ 秒）或版本數（$T$ 次更新）。適合儀表板（例如股票報價）。
3.  **Session (工作階段)**: "Read Your Own Writes." Within a single client session, consistency is guaranteed. Other users may see old data briefly. **Default and most common.**
    **Session**：「讀取你自己的寫入」。在單一用戶端工作階段內，保證一致性。其他使用者可能短暫看到舊資料。**預設且最常用。**
4.  **Consistent Prefix (一致前綴)**: No out-of-order updates. You might see old data, but you will never see Update 2 before Update 1.
    **Consistent Prefix**：沒有亂序更新。你可能看到舊資料，但絕不會在看到「更新 1」之前先看到「更新 2」。
5.  **Eventual (最終一致性)**: Lowest latency, highest availability. No ordering guarantees. Data will converge "eventually."
    **Eventual**：最低延遲，最高可用性。無順序保證。資料將「最終」收斂。

### 2.2 Sharding vs. Partitioning (Azure SQL)
### 2.2 分片與分割 (Azure SQL)

*   **Vertical Scaling (Scale-up)**: Increasing CPU/RAM. Easy but has a hard ceiling.
    **垂直擴充 (Scale-up)**：增加 CPU/RAM。簡單但有硬上限。
*   **Horizontal Scaling (Sharding)**: Splitting data across multiple independent databases (shards) based on a **Sharding Key** (e.g., CustomerId).
    **水平擴充 (Sharding)**：根據 **分片鍵 (Sharding Key)**（例如 CustomerId）將資料拆分到多個獨立的資料庫（分片）中。

**Mental Model**: Think of Sharding like a library. Instead of building one giant room (Scale-up), you build multiple rooms (Shards). You need a directory (Shard Map Manager) to know which room holds books for authors A-M and which holds N-Z.
**心智模型**：將分片想像成圖書館。與其建造一個巨大的房間 (Scale-up)，不如建造多個房間 (Shards)。你需要一個目錄 (Shard Map Manager) 來知道哪個房間存放作者 A-M 的書，哪個存放 N-Z 的書。

### 2.3 Blob Storage Tiering & Hierarchy
### 2.3 Blob 儲存分層與階層結構

Blob Storage is not just a "disk in the cloud." It is an object store optimized for different access patterns:
Blob Storage 不僅僅是「雲端硬碟」。它是針對不同存取模式優化的物件儲存：

*   **Hot**: Frequent access (API backends).
    **Hot**：頻繁存取（API 後端）。
*   **Cool**: Infrequent access (Backups, older logs). stored for at least 30 days.
    **Cool**：不常存取（備份、舊 Log）。至少儲存 30 天。
*   **Archive**: Rare access (Compliance data). High retrieval latency (hours), lowest cost.
    **Archive**：極少存取（合規資料）。取回延遲高（數小時），成本最低。

**Key Concept**: **Hierarchical Namespace (HNS)** turns the flat object storage (virtual folders) into a real file system structure, essential for Hadoop/Spark analytics performance.
**關鍵概念**：**階層式命名空間 (HNS)** 將扁平的物件儲存（虛擬資料夾）轉變為真實的檔案系統結構，這對 Hadoop/Spark 分析效能至關重要。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Global E-commerce Platform (Cosmos DB)
### 3.1 全球電子商務平台 (Cosmos DB)

In a system design interview for a global shopping site:
在全球購物網站的系統設計面試中：

*   **Product Catalog**: Use **Eventual Consistency**. It's okay if a price update takes 2 seconds to propagate from US-East to Asia-East. Speed is priority.
    **產品目錄**：使用 **最終一致性 (Eventual)**。價格更新從美東傳播到亞東花 2 秒是可以接受的。速度優先。
*   **Shopping Cart**: Use **Session Consistency**. The user must see the item they just added. Other users don't care what's in my cart.
    **購物車**：使用 **工作階段一致性 (Session)**。使用者必須看到他們剛加入的商品。其他使用者不在乎我的購物車裡有什麼。
*   **Inventory/Checkout**: Requires **Strong Consistency** (or careful transactional patterns) to prevent selling the same item twice.
    **庫存/結帳**：需要 **強一致性 (Strong)**（或謹慎的交易模式）以防止超賣。

### 3.2 Multi-Tenant SaaS (Azure SQL Sharding)
### 3.2 多租戶 SaaS (Azure SQL 分片)

For a B2B SaaS application serving thousands of companies:
對於服務數千家公司的 B2B SaaS 應用程式：

*   **Isolation**: Sharding by `TenantID` ensures that a heavy query from Tenant A does not impact the performance of Tenant B (Noisy Neighbor problem).
    **隔離性**：依 `TenantID` 進行分片可確保租戶 A 的繁重查詢不會影響租戶 B 的效能（吵雜鄰居問題）。
*   **Compliance**: Some customers (e.g., in Germany) require data residency. Sharding allows you to place specific shards in specific Azure regions.
    **合規性**：某些客戶（例如德國）要求資料在地化。分片允許你將特定分片放置在特定的 Azure 區域。

### 3.3 Data Lake for Logs/Analytics (Blob Storage)
### 3.3 用於日誌/分析的資料湖 (Blob Storage)

*   **Cost Optimization**: A system generating 1TB of logs daily.
    **成本優化**：一個每天產生 1TB Log 的系統。
    *   Day 0-30: **Hot Tier** (For real-time debugging/Dashboards).
        第 0-30 天：**Hot Tier**（用於即時除錯/儀表板）。
    *   Day 31-90: **Cool Tier** (For monthly trend analysis).
        第 31-90 天：**Cool Tier**（用於月度趨勢分析）。
    *   Day 90+: **Archive Tier** (For audit/compliance).
        第 90 天後：**Archive Tier**（用於稽核/合規）。
*   **Implementation**: Use **Lifecycle Management Rules** (JSON based) to automate this transition.
    **實作**：使用 **生命週期管理規則** (基於 JSON) 來自動化此轉換。

---

## 4. Walkthrough: Scaling a Global Chat App
## 4. 逐步示例：擴展全球聊天應用程式

### Scenario
### 情境
You are designing the storage layer for a chat application (like WhatsApp) targeting 10M DAU globally.
你正在為一個目標全球 1000 萬日活躍用戶 (DAU) 的聊天應用程式（如 WhatsApp）設計儲存層。

### Step 1: Naive Approach (Single SQL)
### 步驟 1：天真做法 (單一 SQL)
*   **Design**: A single Azure SQL Database in `East US`.
*   **Problem**: Users in `Japan` experience high latency (200ms+). Database locks up during peak hours.
*   **設計**：在 `East US` 使用單一 Azure SQL 資料庫。
*   **問題**：`Japan` 的使用者面臨高延遲 (200ms+)。資料庫在尖峰時段鎖死。

### Step 2: Geo-Replication with Cosmos DB (Strong Consistency)
### 步驟 2：使用 Cosmos DB 進行地理複寫 (強一致性)
*   **Design**: Migrate to Cosmos DB. Enable multi-region writes. Set consistency to **Strong** to ensure everyone sees messages instantly.
*   **Problem**: Write latency skyrockets. To commit a write in Japan, Cosmos DB must wait for acknowledgement from US and Europe. This violates the availability requirement.
*   **設計**：遷移至 Cosmos DB。啟用多區域寫入。將一致性設為 **Strong** 以確保所有人立即看到訊息。
*   **問題**：寫入延遲飆升。要在日本提交寫入，Cosmos DB 必須等待美國和歐洲的確認。這違反了可用性需求。

### Step 3: Optimal Solution (Session Consistency + Partitioning)
### 步驟 3：最佳解法 (工作階段一致性 + 分割)

*   **Consistency**: Switch to **Session Consistency**.
    *   *Why?* User A sends a message. User A must see it immediately (Read Your Own Writes). User B (recipient) can see it 500ms later; that is acceptable for chat.
    *   **一致性**：切換至 **Session Consistency**。
    *   *原因？* 使用者 A 發送訊息。使用者 A 必須立即看到它（讀取自己的寫入）。使用者 B（接收者）晚 500ms 看到是可以接受的。

*   **Partitioning**: Choose `ConversationID` as the Partition Key.
    *   *Why?* All messages for a specific chat reside on the same physical partition, optimizing queries like "Get last 50 messages."
    *   **分割**：選擇 `ConversationID` 作為分割鍵 (Partition Key)。
    *   *原因？* 特定聊天的所有訊息都駐留在同一個實體分區上，優化了諸如「取得最近 50 條訊息」之類的查詢。

*   **Code Example (C# SDK)**:
    **程式碼範例 (C# SDK)**：

```csharp
// Configuring Cosmos Client with Session Consistency
// 設定具備工作階段一致性的 Cosmos Client
CosmosClientOptions options = new CosmosClientOptions()
{
    ConsistencyLevel = ConsistencyLevel.Session, // Default, but explicit is better
    ApplicationRegion = Regions.EastUS2
};

using CosmosClient client = new CosmosClient(endpoint, key, options);
Container container = client.GetContainer("ChatDB", "Messages");

// Writing a message (Partition Key: ConversationId)
// 寫入訊息 (分割鍵: ConversationId)
ChatMsg newMessage = new ChatMsg 
{ 
    id = Guid.NewGuid().ToString(), 
    ConversationId = "chat_room_123", 
    Sender = "Alice", 
    Content = "Hello World" 
};

// High performance write
// 高效能寫入
ItemResponse<ChatMsg> response = await container.CreateItemAsync<ChatMsg>(
    newMessage, 
    new PartitionKey(newMessage.ConversationId)
);

Console.WriteLine($"Consumed RUs: {response.RequestCharge}");
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Strong Consistency" Safety Blanket
### 5.1 「強一致性」的安全毯
*   **Anti-pattern**: Developers fear data loss or inconsistency, so they default to **Strong Consistency** for everything.
*   **Impact**: Costs double (read quorum required), and latency increases significantly. Availability drops (if one region is down, writes may fail).
*   **Correction**: Default to **Session**. Only use Strong if business logic explicitly demands global linearizability (rare).
*   **反模式**：開發者擔心資料遺失或不一致，因此對所有事物預設使用 **強一致性**。
*   **影響**：成本加倍（需要讀取法定人數），延遲顯著增加。可用性下降（如果一個區域當機，寫入可能會失敗）。
*   **修正**：預設使用 **Session**。只有在商業邏輯明確要求全球線性一致性時才使用 Strong（罕見）。

### 5.2 Cross-Shard Queries in SQL
### 5.2 SQL 中的跨分片查詢
*   **Anti-pattern**: Designing a sharded architecture but frequently running queries that need to join data from Shard A and Shard B (e.g., "Find all users across all tenants who logged in today").
*   **Impact**: The "Fan-out" query performance is terrible and kills the Shard Map Manager or the application layer doing the aggregation.
*   **Correction**: Replicate common reference data (like Zip Codes or Product Categories) to all shards. Use a separate Data Warehouse (Synapse/Fabric) for cross-shard analytics.
*   **反模式**：設計了分片架構，但頻繁執行需要 Join 分片 A 和分片 B 資料的查詢（例如「找出所有租戶中今天登入的所有使用者」）。
*   **影響**：「扇出 (Fan-out)」查詢效能極差，並且會拖垮 Shard Map Manager 或執行聚合的應用程式層。
*   **修正**：將通用參考資料（如郵遞區號或產品類別）複製到所有分片。使用獨立的資料倉儲 (Synapse/Fabric) 進行跨分片分析。

### 5.3 Ignoring Blob Lifecycle Management
### 5.3 忽略 Blob 生命週期管理
*   **Anti-pattern**: Storing terabytes of backup data in the **Hot** tier indefinitely.
*   **Impact**: Massive, unnecessary monthly bills.
*   **Correction**: Configure automated policies to move data to Cool after 30 days and Archive after 180 days.
*   **反模式**：將 TB 級的備份資料無限期儲存在 **Hot** 層。
*   **影響**：巨額且不必要的每月帳單。
*   **修正**：設定自動化策略，在 30 天後將資料移至 Cool，180 天後移至 Archive。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: "How would you choose the Partition Key for a Cosmos DB container storing IoT telemetry data?"
### Q1：「你會如何為儲存 IoT 遙測資料的 Cosmos DB 容器選擇分割鍵 (Partition Key)？」

*   **Key Points**:
    *   **Cardinality**: High cardinality is needed (many unique keys). `DeviceId` is good; `Date` is bad (creates "Hot Partitions" where all writes go to one partition today).
    *   **Query Patterns**: If queries are mostly "Give me data for Device X", then `DeviceId` is perfect. If queries are "Give me all alerts in Region Y", `DeviceId` might cause cross-partition queries (expensive).
    *   **Synthetic Keys**: Mention combining keys (e.g., `DeviceId_Month`) to prevent a single logical partition from exceeding the 20GB limit if data volume is huge.
*   **關鍵點**：
    *   **基數 (Cardinality)**：需要高基數（許多唯一鍵）。`DeviceId` 很好；`Date` 很糟（會造成「熱分區」，即今天的所有寫入都集中在一個分區）。
    *   **查詢模式**：如果查詢主要是「給我裝置 X 的資料」，那麼 `DeviceId` 很完美。如果查詢是「給我區域 Y 的所有警報」，`DeviceId` 可能導致跨分區查詢（昂貴）。
    *   **合成鍵 (Synthetic Keys)**：若資料量巨大，提及組合鍵（例如 `DeviceId_Month`）以防止單一邏輯分區超過 20GB 上限。

### Q2: "We have a multi-tenant SQL database that is hitting CPU limits. How do we scale without rewriting the entire app?"
### Q2：「我們有一個多租戶 SQL 資料庫正面臨 CPU 上限。我們如何在不重寫整個應用程式的情況下進行擴充？」

*   **Key Points**:
    *   **Vertical first**: Can we just upgrade the SKU (vCores)? (Quickest fix).
    *   **Read Replicas**: Offload reporting queries to a Read Replica.
    *   **Sharding (Elastic Database)**: If scale is massive, introduce sharding by TenantID. Discuss the complexity of managing the **Shard Map**.
    *   **Elastic Pools**: If the issue is unpredictable usage spikes across tenants, moving databases into an Elastic Pool shares resources efficiently.
*   **關鍵點**：
    *   **垂直優先**：我們能直接升級 SKU (vCores) 嗎？（最快的修復）。
    *   **讀取複本**：將報表查詢卸載到讀取複本 (Read Replica)。
    *   **分片 (Elastic Database)**：如果規模巨大，引入依 TenantID 分片。討論管理 **Shard Map** 的複雜性。
    *   **彈性集區 (Elastic Pools)**：如果問題是各租戶間不可預測的使用量尖峰，將資料庫移入彈性集區可有效共享資源。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary (記憶錨點)
1.  **5 Consistency Levels**: Strong (Slowest/Correct) -> Bounded Staleness -> Session (Default) -> Consistent Prefix -> Eventual (Fastest).
2.  **Trade-offs**: You cannot have low latency and strong consistency simultaneously across global regions (CAP Theorem).
3.  **Sharding**: Horizontal scaling for SQL. Requires a Sharding Key and a Shard Map Manager. Avoid cross-shard queries.
4.  **Blob Tiers**: Hot (Active), Cool (30d+), Archive (180d+, offline). Use Lifecycle Management to automate.
5.  **ADLS Gen2**: Adds Hierarchical Namespace (folders) to Blob Storage for Big Data analytics performance.

### Next Steps (後續延伸)
*   **Deep Dive**: Implement a "Change Feed" processor in Cosmos DB to trigger Azure Functions (Event-Driven Architecture).
*   **Next Chapter**: We will explore **Serverless Compute & Event-Driven Patterns** (Functions, Event Grid, Service Bus) to connect these storage layers.
*   **深入研究**：在 Cosmos DB 中實作 "Change Feed" 處理器以觸發 Azure Functions（事件驅動架構）。
*   **下一章**：我們將探討 **Serverless 計算與事件驅動模式**（Functions, Event Grid, Service Bus）來串聯這些儲存層。