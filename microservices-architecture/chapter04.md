# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單體架構（Monolithic）轉向微服務架構（Microservices）的過程中，最大的挑戰往往不是業務邏輯的拆分，而是**網路的不確定性**。在分散式系統中，故障不是「是否會發生」的問題，而是「何時發生」的問題。身為資深工程師，你的目標不再是追求「零故障」，而是設計出能夠「擁抱故障」並自我修復的系統。

In the transition from Monolithic to Microservices architecture, the biggest challenge is often not the separation of business logic, but the **uncertainty of the network**. In distributed systems, failure is not a question of "if," but "when." As a Senior Engineer, your goal is no longer to pursue "zero failure," but to design systems that can "embrace failure" and self-heal.

完成本章後，你應該能夠：

By the end of this chapter, you should be able to:

1.  **區分並正確選用容錯模式**：清楚解釋 Retry、Circuit Breaker、Bulkhead 與 Rate Limiting 的適用場景與差異。
    **Distinguish and select fault tolerance patterns**: Clearly explain the use cases and differences between Retry, Circuit Breaker, Bulkhead, and Rate Limiting.
2.  **防止級聯故障（Cascading Failures）**：設計機制以確保單一服務的延遲或崩潰不會拖垮整個系統。
    **Prevent Cascading Failures**: Design mechanisms to ensure that latency or crashes in a single service do not drag down the entire system.
3.  **實作冪等性與重試策略**：理解在實作 Retry 機制時，如何配合 Idempotency Key 避免資料不一致（如重複扣款）。
    **Implement Idempotency and Retry Strategies**: Understand how to use Idempotency Keys when implementing Retry mechanisms to avoid data inconsistencies (e.g., double charges).
4.  **權衡一致性與可用性**：在系統降級（Degradation）時，如何做出正確的 Trade-off（例如回傳快取資料或預設值）。
    **Trade-off between Consistency and Availability**: How to make the right trade-offs during system degradation (e.g., returning cached data or default values).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 分散式系統的謬誤 (The Fallacies of Distributed Computing)

資深工程師的心智模型必須建立在一個前提上：**網路是不可靠的**。任何跨服務的呼叫（RPC/HTTP）都可能因為網路抖動、對方 GC 暫停、或資源耗盡而失敗。

A Senior Engineer's mental model must be built on one premise: **The network is unreliable**. Any cross-service call (RPC/HTTP) can fail due to network jitter, peer GC pauses, or resource exhaustion.

## 2.2 四大防禦模式 (The Four Defense Patterns)

我們可以將這些模式類比為現實生活中的安全機制：

We can analogize these patterns to real-life safety mechanisms:

1.  **Retry (重試模式)**
    *   **類比**：你打電話給朋友，對方沒接，你過幾秒鐘再打一次。
    *   **適用**：**暫時性故障（Transient Faults）**，如網路瞬間封包遺失、資料庫連線池暫時滿載。
    *   **Analogy**: You call a friend, they don't pick up, so you call again in a few seconds.
    *   **Use Case**: **Transient Faults**, such as momentary packet loss or a temporarily full database connection pool.

2.  **Circuit Breaker (斷路器模式)**
    *   **類比**：家裡的保險絲。當電流過載時，保險絲熔斷，切斷電力以防止電器燒毀或火災。
    *   **適用**：**持續性故障（Persistent Faults）**。當下游服務已掛掉，繼續 Retry 只會加速其死亡（DDoS 自己），此時應直接「斷路」並快速失敗（Fail Fast）。
    *   **Analogy**: The fuse box in your home. When the circuit is overloaded, the fuse blows, cutting off power to prevent appliance damage or fire.
    *   **Use Case**: **Persistent Faults**. When a downstream service is down, continuing to Retry will only accelerate its demise (self-DDoS); instead, you should "trip the breaker" and Fail Fast.

3.  **Bulkhead (艙壁模式)**
    *   **類比**：船艙的隔水設計。如果鐵達尼號的一個艙室進水，隔板應防止水蔓延到其他艙室，確保船不會沉沒。
    *   **適用**：**資源隔離**。防止一個濫用資源的服務（如延遲極高的報表服務）耗盡所有的 Thread Pool 或 Connection Pool，導致核心交易服務也被拖累。
    *   **Analogy**: Watertight compartments in a ship. If one compartment of the Titanic floods, the bulkheads should prevent water from spreading to others, ensuring the ship doesn't sink.
    *   **Use Case**: **Resource Isolation**. Preventing a resource-hogging service (like a high-latency reporting service) from exhausting all Thread Pools or Connection Pools, causing core transaction services to fail.

4.  **Rate Limiting (限流模式)**
    *   **類比**：熱門夜店門口的保全，控制進入的人數。
    *   **適用**：**保護服務不過載**。針對 API 呼叫頻率進行限制，確保系統在負載能力範圍內運作。
    *   **Analogy**: The bouncer at a popular nightclub controlling the number of people entering.
    *   **Use Case**: **Protecting services from overload**. Limiting the frequency of API calls to ensure the system operates within its capacity.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或實際架構規劃中，你需要決定這些模式「放在哪裡」。通常有兩個主要位置：

In System Design Interviews or actual architecture planning, you need to decide "where" to place these patterns. There are typically two main locations:

## 3.1 Client-Side Resilience (呼叫端韌性)
*   **位置**：在 Microservice A 呼叫 Microservice B 的程式碼中（或 SDK）。
*   **模式**：**Circuit Breaker**, **Retry**, **Bulkhead**。
*   **責任**：保護**自己**（Caller）不被下游的緩慢或故障拖垮。例如，如果 Payment Service 變慢，Checkout Service 的執行緒不應全部卡在等待回應上。
*   **Location**: Inside the code (or SDK) where Microservice A calls Microservice B.
*   **Patterns**: **Circuit Breaker**, **Retry**, **Bulkhead**.
*   **Responsibility**: Protect **yourself** (the Caller) from being dragged down by downstream slowness or failure. For example, if the Payment Service slows down, the Checkout Service's threads should not all be stuck waiting for a response.

## 3.2 Server-Side Resilience (服務端韌性)
*   **位置**：在 Microservice B 的入口處，或其前方的 API Gateway / Load Balancer。
*   **模式**：**Rate Limiting**, **Bulkhead** (Queue management)。
*   **責任**：保護**自己**（Callee）不被上游的突發流量（Traffic Spike）沖垮。
*   **Location**: At the entry point of Microservice B, or at the API Gateway / Load Balancer in front of it.
*   **Patterns**: **Rate Limiting**, **Bulkhead** (Queue management).
*   **Responsibility**: Protect **yourself** (the Callee) from being overwhelmed by upstream Traffic Spikes.

## 3.3 Service Mesh (Sidecar Pattern)
在現代架構（如 Kubernetes + Istio/Linkerd）中，這些邏輯常被移出應用程式碼，放入 **Sidecar Proxy**。
*   **優點**：語言無關（Polyglot）、統一配置、開發者專注業務邏輯。
*   **缺點**：除錯複雜度增加，對於需要精細控制的業務邏輯（如特定錯誤碼才 Retry），可能仍需在應用層處理。

In modern architectures (like Kubernetes + Istio/Linkerd), logic is often moved out of application code into a **Sidecar Proxy**.
*   **Pros**: Language agnostic (Polyglot), unified configuration, developers focus on business logic.
*   **Cons**: Increased debugging complexity. For business logic requiring fine-grained control (e.g., Retry only on specific error codes), application-layer handling might still be necessary.

---

# 4. 逐步示例 (Walkthrough / Example)

我們以一個 **E-commerce Checkout Service** 呼叫 **Inventory Service**（庫存服務）扣減庫存為例。

Let's take an **E-commerce Checkout Service** calling an **Inventory Service** to deduct inventory as an example.

## 4.1 階段一：天真的實作 (The Naive Implementation)

```java
// Pseudo-code: Naive approach
public void checkout(String orderId) {
    // 1. Call Inventory Service
    // 如果 Inventory Service 沒有回應，這裡會一直 block 直到 TCP timeout (預設可能很長)
    // If Inventory Service doesn't respond, this blocks until TCP timeout (default can be long)
    inventoryClient.deduct(orderId);
    
    // 2. Process Payment...
}
```

**問題**：如果 Inventory Service 變慢（回應需 30秒），Checkout Service 的所有 Thread 都會卡住等待，導致 Checkout Service 也無法回應其他請求（Cascading Failure）。

**Problem**: If the Inventory Service slows down (taking 30s to respond), all threads in the Checkout Service will get stuck waiting, causing the Checkout Service to become unresponsive to other requests (Cascading Failure).

## 4.2 階段二：引入 Timeouts 與 Retries (Introducing Timeouts & Retries)

```java
// Pseudo-code: Timeout + Retry
public void checkout(String orderId) {
    int retries = 3;
    while (retries > 0) {
        try {
            // 設定 2秒 Timeout
            // Set 2s Timeout
            inventoryClient.deduct(orderId, timeout=2000ms);
            return;
        } catch (TimeoutException e) {
            retries--;
            if (retries == 0) throw e;
            // 立即重試 (Immediate Retry)
        }
    }
}
```

**問題**：
1.  **Thundering Herd (驚群效應)**：如果 Inventory Service 只是暫時過載，立即重試會產生更多流量，徹底打垮它。
2.  **非冪等風險**：如果第一次請求其實成功了（只是回應超時），重試會導致庫存扣兩次。

**Problems**:
1.  **Thundering Herd**: If the Inventory Service is temporarily overloaded, immediate retries will generate more traffic, crushing it completely.
2.  **Non-Idempotent Risk**: If the first request actually succeeded (but the response timed out), retrying will cause double inventory deduction.

## 4.3 階段三：成熟的方案 (The Mature Solution)

結合 **Circuit Breaker**, **Exponential Backoff** (指數退避), **Jitter** (隨機抖動) 與 **Bulkhead**。

Combining **Circuit Breaker**, **Exponential Backoff**, **Jitter**, and **Bulkhead**.

```java
// Pseudo-code using a Resilience Library (e.g., Resilience4j)

// 1. 定義 Bulkhead: 限制同時只能有 20 個 thread 呼叫 Inventory
// 1. Define Bulkhead: Limit to max 20 concurrent threads calling Inventory
@Bulkhead(name = "inventory", type = THREADPOOL, maxConcurrentCalls = 20)
// 2. 定義 Circuit Breaker: 失敗率超過 50% 則斷路
// 2. Define Circuit Breaker: Trip if failure rate > 50%
@CircuitBreaker(name = "inventory", fallbackMethod = "fallbackInventory")
// 3. 定義 Retry: 指數退避 + Jitter
// 3. Define Retry: Exponential Backoff + Jitter
@Retry(name = "inventory", backoff = "exponential", jitter = 0.5)
public void checkout(String orderId) {
    // 確保操作是冪等的 (Idempotent)
    // Ensure operation is Idempotent
    inventoryClient.deduct(orderId, requestId=UUID.randomUUID()); 
}

public void fallbackInventory(String orderId, Throwable t) {
    // 降級策略：
    // 1. 記錄錯誤
    // 2. 回傳 "庫存檢查稍後處理" 或放入 Queue 非同步處理
    // Degradation Strategy:
    // 1. Log error
    // 2. Return "Inventory check pending" or push to Queue for async processing
    log.error("Inventory service unavailable", t);
    queueForLaterProcessing(orderId);
}
```

### 關鍵技術細節 (Key Technical Details)

*   **Exponential Backoff**: 等待時間依序為 100ms, 200ms, 400ms... 讓系統有喘息空間。
*   **Jitter**: 在等待時間加上隨機值（例如 200ms ± 50ms），防止所有客戶端在同一毫秒發起重試（避免同步衝擊）。
*   **State Transition**: Circuit Breaker 狀態：`CLOSED` (正常) -> `OPEN` (斷路，直接報錯) -> `HALF-OPEN` (放行少量請求測試是否恢復)。

*   **Exponential Backoff**: Wait times sequence: 100ms, 200ms, 400ms... giving the system breathing room.
*   **Jitter**: Adding a random value to the wait time (e.g., 200ms ± 50ms) prevents all clients from retrying at the exact same millisecond (avoiding synchronization shock).
*   **State Transition**: Circuit Breaker states: `CLOSED` (Normal) -> `OPEN` (Tripped, fail immediately) -> `HALF-OPEN` (Allow few requests to test recovery).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 盲目重試 (Blind Retries)
*   **錯誤**：對所有錯誤都進行 Retry（例如 400 Bad Request 或 403 Forbidden）。
*   **後果**：浪費資源。只有 **Transient Errors**（如 503 Service Unavailable, Network Timeout, 429 Too Many Requests）才值得重試。
*   **Mistake**: Retrying on all errors (e.g., 400 Bad Request or 403 Forbidden).
*   **Consequence**: Wasted resources. Only **Transient Errors** (e.g., 503 Service Unavailable, Network Timeout, 429 Too Many Requests) are worth retrying.

## 5.2 缺乏冪等性 (Lack of Idempotency)
*   **錯誤**：在沒有 `idempotency-key` 的情況下重試寫入操作（POST/PUT）。
*   **後果**：資料損毀（重複訂單、重複扣款）。
*   **修正**：Server 端必須實作去重邏輯（Deduplication logic），Client 端重試時必須帶上相同的 Request ID。
*   **Mistake**: Retrying write operations (POST/PUT) without an `idempotency-key`.
*   **Consequence**: Data corruption (duplicate orders, double charges).
*   **Correction**: Server side must implement deduplication logic; Client must send the same Request ID during retries.

## 5.3 預設超時過長 (Excessive Default Timeouts)
*   **錯誤**：使用 HTTP Client 的預設 Timeout（通常是無限或 60秒）。
*   **後果**：當下游服務掛掉時，上游服務的 Thread Pool 迅速被佔滿，導致整個系統癱瘓。
*   **修正**：根據 P99 Latency 設定合理的 Timeout（例如：若 P99 是 200ms，Timeout 可設為 500ms-1s）。
*   **Mistake**: Using the default Timeout of HTTP Clients (often infinite or 60s).
*   **Consequence**: When a downstream service fails, the upstream service's Thread Pool fills up rapidly, paralyzing the entire system.
*   **Correction**: Set reasonable Timeouts based on P99 Latency (e.g., if P99 is 200ms, set Timeout to 500ms-1s).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於檢視候選人或同事對於系統韌性的深度理解。

These questions can be used to gauge a candidate's or colleague's depth of understanding regarding system resilience.

## Q1: 請解釋為什麼我們需要 Jitter？它解決了什麼問題？
**Why do we need Jitter? What problem does it solve?**

*   **高分回答要點**：
    *   提到 **Thundering Herd (驚群效應)**。
    *   解釋如果沒有 Jitter，當服務恢復時，所有處於 Backoff 狀態的 Clients 會在同一時刻發起重試，再次打垮服務。
    *   Jitter 將流量「平滑化（Smooth out）」。
*   **Key Points**:
    *   Mention **Thundering Herd**.
    *   Explain that without Jitter, when a service recovers, all clients in Backoff state will retry at the exact same moment, crashing the service again.
    *   Jitter "smooths out" the traffic.

## Q2: Circuit Breaker 的 `HALF-OPEN` 狀態有什麼作用？
**What is the purpose of the `HALF-OPEN` state in a Circuit Breaker?**

*   **高分回答要點**：
    *   它是自我修復（Self-healing）的關鍵。
    *   系統不能永遠保持 `OPEN`，也不能直接切回 `CLOSED`（風險太大）。
    *   `HALF-OPEN` 允許有限的流量通過（Probe/Canary requests），驗證下游是否真的恢復了。若成功則 `CLOSED`，若失敗則退回 `OPEN`。
*   **Key Points**:
    *   It is key to **Self-healing**.
    *   The system cannot stay `OPEN` forever, nor can it switch back to `CLOSED` immediately (too risky).
    *   `HALF-OPEN` allows limited traffic (Probe/Canary requests) to verify if the downstream has truly recovered. If successful, go `CLOSED`; if failed, revert to `OPEN`.

## Q3: 在微服務中，應該由 Caller 做 Retry 還是 Callee 做 Retry？
**In microservices, should the Caller perform the Retry or the Callee?**

*   **高分回答要點**：
    *   通常由 **Caller** (Client-side) 發起 Retry，因為只有 Caller 知道請求是否失敗（網路斷在 Request 還是 Response 階段）。
    *   Callee (Server-side) 內部重試通常用於它依賴的下游（如 DB 連線失敗），但不應對 Client 的請求進行長時間的內部重試循環，以免 Client 端 Timeout。
*   **Key Points**:
    *   Usually initiated by the **Caller** (Client-side), as only the Caller knows if the request failed (did the network break during Request or Response?).
    *   Callee (Server-side) internal retries are typically for its own dependencies (e.g., DB connection failure), but it should not perform long internal retry loops for Client requests to avoid Client-side Timeouts.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **Fail Fast**: 使用 Circuit Breaker 避免無意義的等待，防止級聯故障。
2.  **Retry Smart**: 僅對暫時性故障重試，並務必搭配 **Exponential Backoff** 與 **Jitter**。
3.  **Idempotency is King**: 重試機制必須建立在冪等操作之上，否則會導致資料災難。
4.  **Bulkhead Isolation**: 不要讓一個壞掉的服務耗盡整個系統的 Thread Pool。
5.  **Degrade Gracefully**: 當服務不可用時，提供備用方案（Fallback）比直接報錯更能提升使用者體驗。

1.  **Fail Fast**: Use Circuit Breakers to avoid meaningless waiting and prevent cascading failures.
2.  **Retry Smart**: Only retry on transient faults, and always pair with **Exponential Backoff** and **Jitter**.
3.  **Idempotency is King**: Retry mechanisms must be built on idempotent operations; otherwise, data disasters will ensue.
4.  **Bulkhead Isolation**: Don't let one broken service exhaust the entire system's Thread Pool.
5.  **Degrade Gracefully**: When a service is unavailable, providing a Fallback is better for UX than throwing a raw error.

## 後續延伸 (Next Steps)
*   **Next Chapter**: **Distributed Tracing & Observability** (分散式追蹤與可觀測性)。
    *   *理由*：當你實作了 Circuit Breaker 和 Retry 後，你需要透過 Tracing (如 OpenTelemetry/Jaeger) 來視覺化這些機制是否按預期運作，以及定位延遲發生的確切位置。
    *   *Reason*: Once you implement Circuit Breakers and Retries, you need Tracing (e.g., OpenTelemetry/Jaeger) to visualize if these mechanisms are working as expected and to pinpoint exactly where latency is occurring.