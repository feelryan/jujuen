# 1. 前言與學習目標 (Introduction & Learning Goals)

在高效能系統中，「快」只是基礎；「穩」才是資深工程師的真正考驗。當流量超出預期或下游客戶端故障時，系統必須具備自我保護機制，而非全面崩潰。本章將探討如何透過韌性設計（Resiliency Design）與科學化的容量規劃，確保系統在極端條件下仍能運作。

In high-performance systems, being "fast" is just the baseline; being "stable" is the true test for a Senior Engineer. When traffic exceeds expectations or downstream clients fail, the system must possess self-protection mechanisms rather than collapsing entirely. This chapter explores how to ensure system operation under extreme conditions through Resiliency Design and scientific Capacity Planning.

完成本章後，你應該能夠：

After completing this chapter, you should be able to:

1.  **設計多層防禦機制**：在 Gateway 與 Service 層級實作 Rate Limiting 與 Circuit Breaker，防止級聯故障（Cascading Failure）。
    **Design Multi-layered Defense**: Implement Rate Limiting and Circuit Breakers at the Gateway and Service levels to prevent Cascading Failures.
2.  **制定降級策略（Degradation Strategy）**：區分核心與非核心路徑，在資源不足時犧牲非關鍵功能以保全核心業務。
    **Formulate Degradation Strategies**: Distinguish between critical and non-critical paths, sacrificing non-essential features to preserve core business logic when resources are scarce.
3.  **執行科學化的容量規劃**：運用 Little's Law 與壓力測試（Load Testing）數據，精準預估系統所需的硬體資源（CPU, Memory, IOPS）。
    **Execute Scientific Capacity Planning**: Apply Little's Law and Load Testing data to accurately estimate required hardware resources (CPU, Memory, IOPS).
4.  **識別與解決重試風暴（Retry Storms）**：理解 Backoff 與 Jitter 的重要性，避免修復後的系統瞬間被積壓流量再次擊垮。
    **Identify and Resolve Retry Storms**: Understand the importance of Backoff and Jitter to prevent the recovered system from being overwhelmed again by backlog traffic.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 系統韌性 (System Resilience)
韌性並非指「永不故障」，而是指系統在遭遇故障或壓力時，能夠維持核心功能並快速恢復的能力。
Resilience does not mean "never failing"; it refers to the system's ability to maintain core functionality and recover quickly when encountering failures or stress.

*   **類比 (Analogy)**：汽車的避震器與保險絲。避震器（Rate Limiter）吸收路面顛簸（流量突波）；保險絲（Circuit Breaker）在電流過載時熔斷以保護昂貴的電子元件（資料庫或核心服務）。
    **Analogy**: Shock absorbers and fuses in a car. Shock absorbers (Rate Limiter) absorb road bumps (traffic spikes); fuses (Circuit Breaker) blow when the current overloads to protect expensive electronics (Database or Core Services).

## 2.2 關鍵模式定義 (Key Patterns Definition)

1.  **Rate Limiting (限流)**：
    *   **定義**：控制單位時間內進入系統的請求數量。
    *   **目的**：防止資源耗盡（Starvation），保護系統不被單一用戶或惡意攻擊打垮。
    *   **演算法**：Token Bucket (允許突發), Leaky Bucket (平滑輸出), Fixed/Sliding Window。
    *   **Definition**: Controlling the number of requests entering the system per unit of time.
    *   **Goal**: Prevent resource starvation and protect the system from being overwhelmed by a single user or malicious attacks.
    *   **Algorithms**: Token Bucket (allows bursts), Leaky Bucket (smooths output), Fixed/Sliding Window.

2.  **Circuit Breaker (斷路器)**：
    *   **定義**：當下游服務錯誤率超過閾值時，暫時切斷請求，直接回傳錯誤或 Fallback。
    *   **狀態機**：Closed (正常) → Open (阻斷) → Half-Open (試探恢復)。
    *   **Definition**: Temporarily cutting off requests and returning an error or Fallback immediately when the downstream service error rate exceeds a threshold.
    *   **State Machine**: Closed (Normal) → Open (Blocked) → Half-Open (Probing for recovery).

3.  **Load Shedding vs. Degradation**：
    *   **Load Shedding (負載拋棄)**：主動丟棄多餘的請求（例如回傳 HTTP 503），以保證剩餘請求的處理品質。
    *   **Degradation (降級)**：接受請求，但提供「較低品質」的服務（例如回傳快取舊資料、隱藏推薦欄位）。
    *   **Load Shedding**: Actively dropping excess requests (e.g., returning HTTP 503) to ensure the processing quality of the remaining requests.
    *   **Degradation**: Accepting requests but providing "lower quality" service (e.g., returning stale cached data, hiding recommendation widgets).

## 2.3 容量規劃 (Capacity Planning) 與 Little's Law
容量規劃的核心公式是 **Little's Law**：
The core formula for Capacity Planning is **Little's Law**:

$$ L = \lambda \times W $$

*   $L$ (Concurrency): 系統中同時處理的請求數 (System Capacity / In-flight requests).
*   $\lambda$ (Throughput): 吞吐量 (Requests per second, RPS/QPS).
*   $W$ (Latency): 平均處理時間 (Average response time).

**Insight**: 如果你的系統目標是支撐 10,000 QPS，且平均 Latency 為 0.2 秒，那麼你的系統必須能夠同時維持 $10,000 \times 0.2 = 2,000$ 個併發連線/執行緒。這直接決定了 Thread Pool Size 或 Connection Pool Size 的設定。
**Insight**: If your system goal is to support 10,000 QPS and the average Latency is 0.2 seconds, your system must be able to maintain $10,000 \times 0.2 = 2,000$ concurrent connections/threads. This directly dictates the settings for Thread Pool Size or Connection Pool Size.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，防禦機制是分層部署的（Defense in Depth）。
In large-scale distributed systems, defense mechanisms are deployed in layers (Defense in Depth).

## 3.1 架構中的防禦層級 (Defense Layers in Architecture)

1.  **Edge / Load Balancer (L7)**:
    *   **功能**：針對 IP 或 User ID 進行粗粒度的 Rate Limiting。
    *   **目的**：阻擋 DDoS 攻擊或爬蟲。
    *   **Function**: Coarse-grained Rate Limiting based on IP or User ID.
    *   **Goal**: Block DDoS attacks or scrapers.

2.  **API Gateway**:
    *   **功能**：針對 API Route 或 Client App ID 進行細粒度限流；實作全域的 Token Bucket。
    *   **目的**：確保不同業務線的公平性（Fairness）。
    *   **Function**: Fine-grained limiting based on API Route or Client App ID; implementing global Token Bucket.
    *   **Goal**: Ensure fairness across different business lines.

3.  **Service Mesh / Internal RPC**:
    *   **功能**：Circuit Breaker, Retry (with Backoff), Timeout。
    *   **目的**：防止某個微服務的故障擴散到整個系統（Cascading Failure）。
    *   **Function**: Circuit Breaker, Retry (with Backoff), Timeout.
    *   **Goal**: Prevent the failure of a single microservice from spreading to the entire system (Cascading Failure).

4.  **Database / Cache**:
    *   **功能**：Connection Pool 限制, Max Concurrency 設定。
    *   **目的**：保護最底層的資料一致性與持久性。
    *   **Function**: Connection Pool limits, Max Concurrency settings.
    *   **Goal**: Protect the lowest level of data consistency and durability.

## 3.2 系統設計視角 (System Design Perspective)

在面試或設計時，不僅要說出「我會加 Rate Limiter」，更要說明 **「在哪裡加」** 以及 **「狀態存在哪裡」**：
In interviews or design phases, it's not enough to say "I'll add a Rate Limiter"; you must explain **"where to add it"** and **"where the state is stored"**:

*   **單機限流 (Local Limiting)**：使用 Guava RateLimiter 或 Semaphore。優點是極快、無網路開銷；缺點是無法控制整個 Cluster 的總量。
    **Local Limiting**: Using Guava RateLimiter or Semaphore. Pros: extremely fast, no network overhead; Cons: cannot control the total volume of the entire Cluster.
*   **分散式限流 (Distributed Limiting)**：使用 Redis + Lua Script。優點是精準控制全域流量；缺點是增加了 Redis 的依賴與 Latency。通常採用 **Batching** (例如每 10 個請求同步一次 Redis) 來平衡精準度與效能。
    **Distributed Limiting**: Using Redis + Lua Script. Pros: precise control of global traffic; Cons: adds dependency on Redis and Latency. Usually adopts **Batching** (e.g., sync with Redis every 10 requests) to balance precision and performance.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：電商秒殺系統 (E-commerce Flash Sale System)
**背景**：一個促銷活動，預計流量會在 1 秒內從 100 QPS 飆升至 50,000 QPS。後端依賴 Inventory Service (庫存) 與 Payment Service (金流)。
**Scenario**: A promotional event where traffic is expected to spike from 100 QPS to 50,000 QPS within 1 second. The backend depends on Inventory Service and Payment Service.

### Step 1: 容量預估 (Capacity Estimation)
假設每個請求處理時間 (Latency) 為 50ms。
Assuming each request processing time (Latency) is 50ms.

*   **Target QPS**: 50,000
*   **Required Concurrency (Little's Law)**: $50,000 \times 0.05s = 2,500$ threads/connections.
*   **Decision**: 單台 Server (e.g., Tomcat default 200 threads) 無法支撐。若每台能處理 500 連線，至少需要 5 台 Application Servers。資料庫連線池也需對應擴充或使用 Proxy (如 PgBouncer)。
*   **Decision**: A single server (e.g., Tomcat default 200 threads) cannot support this. If each server handles 500 connections, at least 5 Application Servers are needed. Database connection pools must also be scaled or use a Proxy (like PgBouncer).

### Step 2: 實作分散式 Rate Limiter (Distributed Rate Limiter Implementation)
我們使用 Redis 與 Lua Script 來實作 Token Bucket，確保原子性（Atomicity）並減少網路往返。
We use Redis and Lua Script to implement a Token Bucket, ensuring Atomicity and reducing network round-trips.

**Redis Lua Script (Conceptual):**

```lua
-- keys[1]: rate_limit_key (e.g., "rate_limit:seckill:v1")
-- argv[1]: capacity (bucket size)
-- argv[2]: tokens_per_sec (refill rate)
-- argv[3]: now_timestamp (current time in seconds)
-- argv[4]: requested_tokens (usually 1)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Get current bucket state
local last_tokens = tonumber(redis.call("hget", key, "tokens"))
local last_refill_time = tonumber(redis.call("hget", key, "last_refill_time"))

if last_tokens == nil then
    last_tokens = capacity
    last_refill_time = now
end

-- Refill tokens based on time passed
local delta = math.max(0, now - last_refill_time)
local filled_tokens = math.min(capacity, last_tokens + (delta * rate))

local allowed = false
if filled_tokens >= requested then
    allowed = true
    filled_tokens = filled_tokens - requested
end

-- Update state
redis.call("hset", key, "tokens", filled_tokens)
redis.call("hset", key, "last_refill_time", now)
-- Set expiry to avoid garbage data accumulation
redis.call("expire", key, math.ceil(capacity/rate) * 2)

return allowed
```

**分析 (Analysis)**：
*   **時間複雜度**：$O(1)$。
*   **原子性**：Redis 保證 Lua script 執行期間不會被其他指令插入，避免 Race Condition。
*   **Time Complexity**: $O(1)$.
*   **Atomicity**: Redis ensures the Lua script execution is not interrupted by other commands, preventing Race Conditions.

### Step 3: 配置 Circuit Breaker & Fallback
當 Inventory Service 因流量過大開始 Timeout 時，我們不希望 Application Server 的 Thread 被卡住等待。
When the Inventory Service starts timing out due to high traffic, we don't want the Application Server's threads to be stuck waiting.

**虛擬配置 (Pseudo-configuration):**

```yaml
circuitBreaker:
  failureRateThreshold: 50%        # If 50% requests fail
  waitDurationInOpenState: 5s      # Wait 5s before trying again (Half-Open)
  slidingWindowSize: 10            # Check last 10 requests
  fallbackMethod: "getApproximateStock"

fallbackMethod "getApproximateStock":
  # Return cached stock count (might be slightly stale)
  # Or return a generic "High traffic, please retry" message
  return redis.get("inventory:cache:" + itemId)
```

**為何有效？**：這釋放了上游資源，讓 Application 能繼續服務其他請求（如瀏覽商品），而不是全部卡死在「確認庫存」這個動作上。
**Why it works?**: This releases upstream resources, allowing the Application to continue serving other requests (like browsing items) instead of getting stuck on the "Check Inventory" action.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 重試風暴 (Retry Storms)
*   **錯誤描述**：當服務暫時不可用（回傳 503 或 Timeout），客戶端立即重試。若有 1000 個客戶端同時重試，服務剛重啟就會再次被瞬間流量打掛。
*   **Description**: When a service is temporarily unavailable (returns 503 or Timeout), clients retry immediately. If 1000 clients retry simultaneously, the service gets overwhelmed again the moment it restarts.
*   **解決方案**：
    1.  **Exponential Backoff**: 等待時間指數增長 (1s, 2s, 4s, 8s)。
    2.  **Jitter (隨機抖動)**: 在等待時間中加入隨機值，避免所有客戶端在同一時刻發起重試 (Synchronization)。
*   **Solution**:
    1.  **Exponential Backoff**: Wait time increases exponentially (1s, 2s, 4s, 8s).
    2.  **Jitter**: Add a random value to the wait time to prevent all clients from retrying at the exact same moment (Synchronization).

## 5.2 混淆 Timeout 設定 (Confusing Timeout Settings)
*   **錯誤描述**：將 DB Timeout 設定得比 API Gateway Timeout 還長。
*   **Description**: Setting the DB Timeout longer than the API Gateway Timeout.
*   **後果**：Gateway 已經放棄並回傳錯誤給使用者，但後端 DB 還在辛苦執行查詢，浪費資源。
*   **Consequence**: The Gateway has already given up and returned an error to the user, but the backend DB is still working hard on the query, wasting resources.
*   **最佳實踐**：Timeout 應由外而內遞減。Gateway (5s) -> App (3s) -> DB (1s)。
*   **Best Practice**: Timeouts should decrease from the outside in. Gateway (5s) -> App (3s) -> DB (1s).

## 5.3 在 Production 進行無隔離的壓力測試
*   **錯誤描述**：直接對 Production 環境發動 Load Test，導致真實用戶受影響，甚至寫入髒資料。
*   **Description**: Running Load Tests directly against the Production environment, affecting real users or even writing dirty data.
*   **解決方案**：
    *   使用獨立的 Staging 環境（規格需與 Prod 等比例）。
    *   若必須在 Prod 測試（如全鏈路壓測），必須使用特殊的 **Test Flag / Shadow Traffic**，並確保測試資料寫入隔離的 Shadow Table 或帶有特殊標記，以便事後清理。
*   **Solution**:
    *   Use an isolated Staging environment (specs proportional to Prod).
    *   If testing in Prod is necessary (e.g., Full-link Stress Testing), use special **Test Flags / Shadow Traffic**, and ensure test data is written to isolated Shadow Tables or marked for cleanup.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何設計一個能夠處理百萬級 QPS 的全域限流器？
**How to design a global rate limiter capable of handling million-level QPS?**

*   **回答要點 (Key Points)**：
    *   **不能** 僅依賴單一 Redis 實例（網路頻寬與 CPU 會成為瓶頸）。
    *   **分層策略 (Tiered Strategy)**：
        1.  **Local Cache**: 在每個 Application Instance 記憶體中預扣一部分 Token（例如每秒 100 個）。
        2.  **Batch Sync**: 每隔幾秒或累積一定請求後，非同步地與 Redis 同步餘額。
    *   **Trade-off**: 犧牲了「絕對精確性」（可能會稍微超賣），換取了「極致效能」與「低延遲」。這就是 **Eventual Consistency** 在限流中的應用。

## Q2: 什麼是「Thundering Herd」效應？如何解決？
**What is the "Thundering Herd" effect? How to solve it?**

*   **回答要點 (Key Points)**：
    *   **定義**：當大量行程/執行緒同時被喚醒去爭搶同一個資源（如 Cache 失效瞬間，所有請求同時打向 DB）。
    *   **解決方案**：
        1.  **Cache Aside with Locking**: 只有拿到 Lock 的執行緒去重建 Cache，其他等待。
        2.  **Probabilistic Early Expiration**: 在 Cache 過期前，以一定機率提前主動更新。
        3.  **Request Coalescing (Singleflight)**: 在記憶體中將相同 Key 的請求合併為一個發送給下游。

## Q3: 你的系統如何決定 Circuit Breaker 的閾值？
**How does your system determine the thresholds for Circuit Breakers?**

*   **回答要點 (Key Points)**：
    *   不是憑感覺猜測。
    *   **Baseline Testing**: 先在正常負載下測量 P99 Latency 與 Error Rate。
    *   **Stress Testing**: 逐步加壓，觀察系統在什麼時候吞吐量開始下降（Inflection Point）。
    *   **設定原則**: 閾值應設定在 Inflection Point 之前，例如 P99 Latency 飆升到平時的 2 倍，或 Error Rate 超過 5-10%。需持續監控並動態調整。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **Fail Fast**: 透過 Timeout 與 Circuit Breaker 快速失敗，避免資源被無效請求佔用。
2.  **Degrade Gracefully**: 系統過載時，優先保住核心業務（如下單），犧牲次要功能（如評論、推薦）。
3.  **Protect Layers**: 限流應由外而內（Gateway -> App -> DB），每一層都要有保護機制。
4.  **Math Matters**: 使用 Little's Law ($L = \lambda W$) 來科學計算 Thread Pool 與 Connection Pool 的大小。
5.  **Respect Backoff**: 重試機制必須配合 Exponential Backoff 與 Jitter，防止二次傷害。

## 後續延伸 (Next Steps)
*   **實作練習**: 使用 Resilience4j (Java) 或 Go-resiliency (Go) 為現有專案加入 Circuit Breaker。
*   **進階閱讀**: 深入研究 **Service Mesh (Istio/Linkerd)** 如何在基礎設施層統一處理 Retry 與 Circuit Breaking，將這些邏輯從 Application Code 中剝離。
*   **下一章預告**: 當應用層韌性足夠後，瓶頸通常會轉移到資料庫。下一章將探討 **Database Performance Tuning & Indexing Strategy**。