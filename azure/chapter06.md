# Chapter 06: High Availability (HA) and Disaster Recovery (DR)
# 第六章：高可用性與災難復原設計

## 1. Introduction & Learning Goals
## 1. 前言與學習目標

High Availability (HA) and Disaster Recovery (DR) are the cornerstones of any enterprise-grade cloud architecture. For a Senior Engineer, the goal is not just to "keep the lights on," but to mathematically quantify uptime (SLA), minimize data loss (RPO), and ensure rapid recovery (RTO) through architectural patterns rather than manual intervention.
高可用性（HA）與災難復原（DR）是任何企業級雲端架構的基石。對於資深工程師而言，目標不僅僅是「讓系統運作」，而是要能透過架構模式而非人工介入，從數學上量化正常運作時間（SLA）、最小化資料遺失（RPO），並確保快速復原（RTO）。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Define and Calculate SLA, RTO, and RPO:** Clearly articulate the business impact of these metrics and map them to technical solutions.
    **定義並計算 SLA、RTO 與 RPO：** 清楚闡述這些指標的商業影響，並將其對應至技術解決方案。
2.  **Design Multi-Region Architectures:** Utilize Azure Availability Zones and Region Pairs to build Active-Passive or Active-Active topologies.
    **設計多區域架構：** 利用 Azure Availability Zones 與 Region Pairs 建構 Active-Passive 或 Active-Active 拓撲。
3.  **Implement Resilience Patterns:** Apply Retry (with exponential backoff) and Circuit Breaker patterns in code to handle transient faults and prevent cascading failures.
    **實作韌性模式：** 在程式碼中應用重試（搭配指數退避）與斷路器模式，以處理暫時性錯誤並防止連鎖故障。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 HA vs. DR: The Plane Analogy
### 2.1 HA 與 DR：飛機類比

*   **High Availability (HA)** is like a twin-engine plane. If one engine fails, the other keeps the plane flying without landing. The goal is **zero downtime** or masking failures from the user. In Azure, this maps to **Availability Zones (AZs)** within a single region.
    **高可用性 (HA)** 就像一架雙引擎飛機。如果其中一個引擎故障，另一個引擎仍能讓飛機繼續飛行而無需降落。目標是**零停機時間**或對使用者隱藏故障。在 Azure 中，這對應到單一區域內的 **可用性區域 (Availability Zones, AZs)**。

*   **Disaster Recovery (DR)** is like the parachute or life raft. The plane has gone down (the entire region is offline). The goal is **survival and recovery**. How fast can you deploy a new plane? How much cargo (data) did you lose? In Azure, this maps to **Region Pairs** (e.g., East US & West US).
    **災難復原 (DR)** 就像降落傘或救生筏。飛機已經墜毀（整個區域離線）。目標是**生存與復原**。你能多快部署一架新飛機？你損失了多少貨物（資料）？在 Azure 中，這對應到 **配對區域 (Region Pairs)**（例如：East US 與 West US）。

### 2.2 RTO & RPO: The Metrics of Failure
### 2.2 RTO 與 RPO：故障的衡量指標

*   **Recovery Time Objective (RTO):** The maximum acceptable duration of downtime. "How long until we are back online?"
    **復原時間目標 (RTO)：** 可接受的最長停機時間。「我們要多久才能恢復上線？」
*   **Recovery Point Objective (RPO):** The maximum acceptable amount of data loss measured in time. "If we restore now, we lose the last X minutes of data."
    **復原點目標 (RPO)：** 以時間衡量的最大可接受資料遺失量。「如果我們現在還原，會遺失過去 X 分鐘的資料。」

### 2.3 Azure Specifics vs. Others
### 2.3 Azure 特性與其他雲端的差異

Unlike AWS where Regions are generally independent meshes, Azure emphasizes **Region Pairs**.
不同於 AWS 的區域通常是獨立的網狀結構，Azure 強調 **配對區域 (Region Pairs)**。

*   **Platform Updates:** Azure serializes platform updates (maintenance) across pairs to ensure only one region in a pair is touched at a time.
    **平台更新：** Azure 會在配對區域間依序進行平台更新（維護），確保同一時間只有配對中的一個區域受到影響。
*   **Data Residency:** Region pairs usually stay within the same geopolitical boundary (except Brazil South) to meet compliance needs.
    **資料駐留：** 為了符合合規需求，配對區域通常位於相同的地緣政治邊界內（Brazil South 除外）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production environment, HA/DR is not a toggle switch; it is a layered design spanning Compute, Data, and Networking.
在生產環境中，HA/DR 不是一個開關，而是跨越運算、資料與網路的分層設計。

### 3.1 The Architecture Layers
### 3.1 架構分層

1.  **Traffic Manager / Load Balancer (Entry Point):**
    *   **Global:** **Azure Front Door** or **Traffic Manager**. Uses DNS or Anycast to route traffic to the healthiest region.
    *   **Regional:** **Application Gateway** (L7) or **Azure Load Balancer** (L4). Distributes traffic across Availability Zones.
    *   **全球層級：** **Azure Front Door** 或 **Traffic Manager**。使用 DNS 或 Anycast 將流量導向最健康的區域。
    *   **區域層級：** **Application Gateway** (L7) 或 **Azure Load Balancer** (L4)。將流量分散至各個可用性區域。

2.  **Compute (Stateless):**
    *   Deploy across **Availability Zones (Zone Redundant)**. For AKS, use node pools spread across zones. For App Service, enable Zone Redundancy (requires Premium plan).
    *   部署跨越 **可用性區域 (Zone Redundant)**。對於 AKS，使用跨區域的節點池。對於 App Service，啟用區域備援（需 Premium 方案）。

3.  **Data (Stateful - The Hard Part):**
    *   **Azure SQL Database:** Use **Failover Groups**. Primary in Region A, readable secondary in Region B. Async replication implies RPO > 0.
    *   **Cosmos DB:** Supports **Multi-region Writes**. This enables RPO = 0 and RTO ≈ 0 but requires handling conflict resolution in the application.
    *   **Storage Accounts:** Use **GZRS** (Geo-Zone-Redundant Storage) for HA within primary region + DR in secondary region.
    *   **Azure SQL Database：** 使用 **容錯移轉群組 (Failover Groups)**。主資料庫在區域 A，唯讀副本在區域 B。非同步複寫意味著 RPO > 0。
    *   **Cosmos DB：** 支援 **多區域寫入 (Multi-region Writes)**。這能實現 RPO = 0 與 RTO ≈ 0，但需要在應用程式中處理衝突解決。
    *   **Storage Accounts：** 使用 **GZRS** (Geo-Zone-Redundant Storage) 以在主區域內實現 HA，並在次要區域實現 DR。

### 3.2 Impact on System Properties
### 3.2 對系統屬性的影響

*   **Consistency (一致性):** In a multi-region DR scenario (Active-Passive), you typically sacrifice strong consistency for availability (CAP theorem). You must design for **Eventual Consistency**.
    在多區域 DR 場景（Active-Passive）中，通常為了可用性會犧牲強一致性（CAP 定理）。你必須針對 **最終一致性** 進行設計。
*   **Latency (延遲):** Cross-region replication adds write latency if synchronous (rarely used). Async replication is standard but risks data loss.
    跨區域複寫若採同步方式（少用）會增加寫入延遲。非同步複寫是標準做法，但有資料遺失風險。
*   **Cost (成本):** HA/DR doubles or triples infrastructure cost. A "Pilot Light" DR strategy (minimal resources in secondary region, scaled up only during disaster) helps manage this.
    HA/DR 會使基礎設施成本翻倍或三倍。「引導燈 (Pilot Light)」DR 策略（次要區域僅保留最小資源，災難時才擴展）有助於控制成本。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Resilient HTTP Client
### 情境：具備韌性的 HTTP 用戶端

Imagine your service calls a downstream Inventory API hosted on Azure. Occasionally, the API returns `503 Service Unavailable` or `429 Too Many Requests`.
想像你的服務呼叫一個託管於 Azure 的下游庫存 API。偶爾，該 API 會回傳 `503 Service Unavailable` 或 `429 Too Many Requests`。

#### Step 1: The Naive Approach (Don't do this)
#### 步驟 1：天真的做法（不要這樣做）

```csharp
// Vulnerable to transient failures. One blip causes an exception.
// 容易受到暫時性故障影響。一個小波動就會導致例外。
var response = await _httpClient.GetAsync("https://inventory-api/items/123");
response.EnsureSuccessStatusCode();
```

#### Step 2: Adding Retry with Exponential Backoff
#### 步驟 2：加入指數退避重試

We use the **Polly** library (standard in .NET ecosystem). We want to retry on transient errors (5xx, 408) but NOT on permanent errors (400, 401, 404).
我們使用 **Polly** 函式庫（.NET 生態系統標準）。我們希望針對暫時性錯誤（5xx, 408）重試，但**不要**針對永久性錯誤（400, 401, 404）重試。

#### Step 3: Adding Circuit Breaker
#### 步驟 3：加入斷路器

If the downstream service is down, retrying continuously adds load to a dying system (Anti-pattern). The **Circuit Breaker** detects high failure rates and "opens" the circuit, failing fast without calling the remote service for a duration.
如果下游服務已當機，持續重試只會增加瀕死系統的負載（反模式）。**斷路器 (Circuit Breaker)** 會偵測高失敗率並「斷開」電路，在一段時間內直接回傳失敗而不呼叫遠端服務。

#### Implementation (C# / .NET 8+)
#### 實作 (C# / .NET 8+)

Using `Microsoft.Extensions.Http.Resilience`:
使用 `Microsoft.Extensions.Http.Resilience`：

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Http.Resilience;
using Polly;

public void ConfigureServices(IServiceCollection services)
{
    services.AddHttpClient("InventoryClient", client => 
    {
        client.BaseAddress = new Uri("https://inventory-api/");
    })
    .AddStandardResilienceHandler(options => 
    {
        // 1. Retry Strategy (重試策略)
        options.Retry.MaxRetryAttempts = 3;
        options.Retry.BackoffType = DelayBackoffType.Exponential;
        options.Retry.UseJitter = true; // Crucial to prevent Thundering Herd (防止驚群效應的關鍵)
        
        // 2. Circuit Breaker Strategy (斷路器策略)
        // If 50% of requests fail within 10s, break the circuit for 5s.
        // 如果 10 秒內有 50% 的請求失敗，則斷路 5 秒。
        options.CircuitBreaker.SamplingDuration = TimeSpan.FromSeconds(10);
        options.CircuitBreaker.FailureRatio = 0.5; 
        options.CircuitBreaker.MinimumThroughput = 10;
        options.CircuitBreaker.BreakDuration = TimeSpan.FromSeconds(5);
        
        // 3. Timeout (Individual Request) (單一請求逾時)
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(2);
        
        // 4. Total Request Timeout (Including retries) (總請求逾時，包含重試)
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(10);
    });
}
```

**Why this works:**
*   **Jitter:** Randomizes retry intervals so all clients don't hit the recovering service at the exact same millisecond.
*   **Circuit Breaker:** Gives the downstream system "breathing room" to recover.
**為何有效：**
*   **Jitter（抖動）：** 隨機化重試間隔，避免所有用戶端在完全相同的毫秒撞擊正在復原的服務。
*   **Circuit Breaker（斷路器）：** 給予下游系統「喘息空間」以進行復原。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Retry Everything" Trap
### 5.1 「重試所有錯誤」的陷阱

*   **Mistake:** Configuring retries for HTTP 400 (Bad Request), 401 (Unauthorized), or 404 (Not Found).
    **錯誤：** 針對 HTTP 400、401 或 404 設定重試。
*   **Impact:** Wasted cycles and increased latency. These errors are usually logical and won't be fixed by retrying.
    **影響：** 浪費運算週期並增加延遲。這些錯誤通常是邏輯性的，重試並無法修復。
*   **Solution:** Only retry on **Transient Faults** (Network glitches, 500, 502, 503, 504, 429).
    **解法：** 僅針對 **暫時性故障**（網路瞬斷、500、502、503、504、429）進行重試。

### 5.2 Ignoring the "Thundering Herd"
### 5.2 忽視「驚群效應 (Thundering Herd)」

*   **Mistake:** Using fixed retry intervals (e.g., exactly 2 seconds).
    **錯誤：** 使用固定的重試間隔（例如：固定 2 秒）。
*   **Impact:** If a service outage affects 10,000 clients, they will all retry simultaneously when the service comes back up, immediately crashing it again.
    **影響：** 如果服務中斷影響了 10,000 個用戶端，當服務恢復時，它們會同時重試，導致服務立即再次崩潰。
*   **Solution:** Always introduce **Jitter** (randomness) to the backoff strategy.
    **解法：** 務必在退避策略中加入 **Jitter（隨機抖動）**。

### 5.3 Cold DR Sites
### 5.3 冷 DR 站點

*   **Mistake:** Designing a Passive region but never deploying code to it until a disaster strikes.
    **錯誤：** 設計了被動區域，但在災難發生前從未部署程式碼。
*   **Impact:** Configuration drift. When you finally failover, the IaC scripts fail, or the database schema is outdated.
    **影響：** 設定漂移 (Configuration drift)。當你最終進行容錯移轉時，IaC 腳本失敗，或資料庫結構過時。
*   **Solution:** Use **Active-Passive (Pilot Light)** where the secondary region receives deployments via CI/CD pipelines just like the primary, even if the compute count is scaled to zero or one.
    **解法：** 使用 **Active-Passive (Pilot Light)**，讓次要區域像主要區域一樣透過 CI/CD 接收部署，即使運算實體數量縮減至零或一。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a system to achieve 99.99% (Four Nines) availability on Azure?
### Q1: 你會如何在 Azure 上設計一個達到 99.99% (四個九) 可用性的系統？

*   **Key Points:**
    *   **SLA Math:** Explain that composite SLA is the product of component SLAs. (e.g., App Service 99.95% * SQL 99.99% < 99.95%). To get higher, you need parallel redundancy.
    *   **Architecture:** Must use **Region Pairs**. A single region (even with Multi-AZ) often caps at 99.95% or 99.99% depending on the service.
    *   **Global Load Balancing:** Mention Azure Front Door to route between regions.
    *   **關鍵要點：**
    *   **SLA 數學：** 解釋複合 SLA 是各元件 SLA 的乘積（例如：App Service 99.95% * SQL 99.99% < 99.95%）。要獲得更高可用性，需要並行備援。
    *   **架構：** 必須使用 **Region Pairs**。單一區域（即使有多 AZ）通常上限為 99.95% 或 99.99%，視服務而定。
    *   **全球負載平衡：** 提及使用 Azure Front Door 在區域間導流。

### Q2: What is the difference between Azure SQL Active Geo-Replication and Failover Groups? When to use which?
### Q2: Azure SQL 的 Active Geo-Replication 與 Failover Groups 有何不同？何時使用哪一個？

*   **Key Points:**
    *   **Abstraction:** Failover Groups provide a single read-write listener endpoint (`rw.database.windows.net`). You don't need to change connection strings in your app during failover.
    *   **Granularity:** Geo-Replication is per-database; Failover Groups manage a group of databases ensuring they failover together.
    *   **Recommendation:** Use Failover Groups for ease of management and automatic failover capability.
    *   **關鍵要點：**
    *   **抽象層：** Failover Groups 提供單一讀寫接聽端點 (`rw.database.windows.net`)。容錯移轉時無需更改應用程式的連線字串。
    *   **顆粒度：** Geo-Replication 是針對單一資料庫；Failover Groups 管理一組資料庫，確保它們一起移轉。
    *   **建議：** 為了管理方便與自動移轉能力，優先使用 Failover Groups。

### Q3: In a microservices architecture, how do you prevent a failure in Service A from taking down Service B and C?
### Q3: 在微服務架構中，如何防止 Service A 的故障導致 Service B 和 C 一併當機？

*   **Key Points:**
    *   **Bulkhead Pattern:** Isolate resources (thread pools, connections) so one heavy consumer doesn't starve others.
    *   **Circuit Breaker:** Fail fast.
    *   **Asynchronous Messaging:** Use Azure Service Bus or Event Grid to decouple services. If consumer is down, messages queue up instead of crashing the producer.
    *   **關鍵要點：**
    *   **艙壁模式 (Bulkhead Pattern)：** 隔離資源（執行緒池、連線），避免單一高負載消耗者餓死其他服務。
    *   **斷路器 (Circuit Breaker)：** 快速失敗。
    *   **非同步訊息傳遞：** 使用 Azure Service Bus 或 Event Grid 解耦服務。如果消費者當機，訊息會排隊而非導致生產者崩潰。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **HA is for uptime (Availability Zones); DR is for survival (Region Pairs).**
    **HA 為了正常運作（可用性區域）；DR 為了生存（配對區域）。**
2.  **SLA is a math problem.** Parallel components increase availability; serial components decrease it.
    **SLA 是數學問題。** 並聯元件增加可用性；串聯元件降低可用性。
3.  **Transient Faults require Retries + Jitter.** Permanent faults do not.
    **暫時性故障需要重試 + 抖動 (Jitter)。** 永久性故障則不需要。
4.  **Circuit Breakers** protect your system from cascading failures and give dependencies time to recover.
    **斷路器** 保護系統免受連鎖故障影響，並給予依賴服務復原的時間。
5.  **Data is the hardest part of DR.** Understand the trade-off between RPO (data loss) and latency (sync vs async replication).
    **資料是 DR 最困難的部分。** 理解 RPO（資料遺失）與延遲（同步 vs 非同步複寫）之間的權衡。

### Next Steps
### 後續延伸

*   **Action:** Review your current project's `HttpClient` or database connection logic. Add resilience policies using standard libraries.
    **行動：** 檢視你目前專案的 `HttpClient` 或資料庫連線邏輯。使用標準函式庫加入韌性策略。
*   **Action:** Calculate the theoretical SLA of your current production workload. Is it aligned with business expectations?
    **行動：** 計算你目前生產環境工作負載的理論 SLA。它是否符合商業預期？
*   **Next Chapter Preview:** Now that we have a resilient architecture, how do we know when it breaks? The next chapter covers **Observability & Monitoring** (Azure Monitor, Application Insights, Distributed Tracing).
    **下一章預告：** 既然我們有了具備韌性的架構，我們如何知道它何時壞掉？下一章將探討 **可觀測性與監控**（Azure Monitor, Application Insights, Distributed Tracing）。