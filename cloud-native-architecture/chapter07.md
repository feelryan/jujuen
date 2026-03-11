# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲端原生架構中，失敗不僅是可能的，更是必然的。分散式系統的複雜性意味著網路延遲、節點崩潰或第三方服務中斷隨時可能發生。本章的目標不是教你如何「避免」失敗，而是如何設計出能夠「優雅失敗」並具備自我修復能力的系統。

In Cloud-Native architecture, failure is not just possible; it is inevitable. The complexity of distributed systems means that network latency, node crashes, or third-party service outages can happen at any time. The goal of this chapter is not to teach you how to "avoid" failure, but how to design systems that "fail gracefully" and possess self-healing capabilities.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作關鍵容錯模式**：熟練運用 Circuit Breaker（斷路器）、Bulkhead（艙壁）與 Rate Limiting（限流）來防止級聯故障（Cascading Failures）。
    **Implement Key Fault Tolerance Patterns**: Proficiently apply Circuit Breaker, Bulkhead, and Rate Limiting to prevent cascading failures.
2.  **區分重試策略的優劣**：理解何時該重試（Retry），以及如何利用 Exponential Backoff（指數退避）與 Jitter（抖動）避免「重試風暴」（Retry Storms）。
    **Distinguish Retry Strategies**: Understand when to retry and how to use Exponential Backoff and Jitter to avoid "Retry Storms."
3.  **設計降級機制（Fallback）**：在主要服務不可用時，提供有損但可用的使用者體驗。
    **Design Fallback Mechanisms**: Provide a degraded but usable user experience when primary services are unavailable.
4.  **理解混沌工程（Chaos Engineering）價值**：知道如何在生產或預發布環境中引入受控故障，以驗證系統的強韌度。
    **Understand the Value of Chaos Engineering**: Know how to introduce controlled failures in production or staging environments to validate system resilience.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 斷路器 (Circuit Breaker)
**類比**：家中的保險絲。當電流過載時，保險絲熔斷，切斷電路以保護電器不被燒毀。
**Analogy**: The fuse in your home. When the current overloads, the fuse blows, cutting the circuit to protect appliances from burning out.

**定義**：在軟體中，斷路器監控對遠端服務的呼叫。當失敗率超過閾值時，斷路器會「跳閘（Open）」，立即拒絕後續請求，而不再等待超時。這給了下游系統喘息與恢復的時間。
**Definition**: In software, a Circuit Breaker monitors calls to remote services. When the failure rate exceeds a threshold, the breaker "trips" (opens), immediately rejecting subsequent requests without waiting for timeouts. This gives the downstream system time to breathe and recover.

**狀態機 (State Machine)**：
*   **Closed**: 正常狀態，請求通過。 (Normal state, requests pass through.)
*   **Open**: 故障狀態，請求直接失敗。 (Failure state, requests fail immediately.)
*   **Half-Open**: 嘗試恢復狀態，允許少量請求通過以測試下游是否恢復。 (Recovery attempt state, allows limited requests to test if downstream has recovered.)

### 2.2 艙壁模式 (Bulkhead Pattern)
**類比**：船艦的防水隔艙。如果船體破了一個洞，水只會淹沒該隔艙，而不會導致整艘船沉沒。
**Analogy**: Watertight compartments in a ship. If the hull is breached, water only floods that specific compartment, preventing the entire ship from sinking.

**定義**：隔離應用程式的資源（如執行緒池、連線池）。例如，將「使用者登入」與「報表生成」使用不同的執行緒池。若報表服務卡死，不會耗盡登入服務的資源。
**Definition**: Isolating application resources (such as thread pools or connection pools). For example, using different thread pools for "User Login" and "Report Generation." If the reporting service hangs, it won't exhaust the resources needed for login.

### 2.3 混沌工程 (Chaos Engineering)
**心智模型**：與其等待駭客或自然災害來測試你的系統，不如自己動手「注射」故障。這是一種主動防禦的思維。
**Mental Model**: Instead of waiting for hackers or natural disasters to test your system, you "inject" failures yourself. It is a proactive defense mindset.

**關鍵差異**：測試（Testing）是驗證「已知」的邏輯；混沌工程是探索「未知」的系統行為。
**Key Difference**: Testing validates "known" logic; Chaos Engineering explores "unknown" system behaviors.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在資深工程師的系統設計中，Resiliency 不是「選配」，而是架構的核心屬性。

In senior-level system design, Resiliency is not an "option," but a core architectural attribute.

### 3.1 基礎設施層 vs. 應用層 (Infrastructure vs. Application Layer)
現代 Cloud-Native 架構通常混合使用 Service Mesh（如 Istio, Linkerd）與應用程式庫（如 Resilience4j, Polly, Go-kit）來實作容錯。

Modern Cloud-Native architectures often mix Service Mesh (e.g., Istio, Linkerd) and application libraries (e.g., Resilience4j, Polly, Go-kit) to implement fault tolerance.

*   **Service Mesh (Sidecar)**: 擅長處理語言無關的網路層面容錯，如重試、超時、斷路器。對應用程式透明。
    *   **Service Mesh (Sidecar)**: Good at language-agnostic network-level fault tolerance, such as retries, timeouts, and circuit breakers. Transparent to the application.
*   **Application Library**: 擅長處理業務邏輯相關的降級（Fallback）。例如：當推薦服務失敗時，程式碼決定回傳「熱門商品」列表。Sidecar 無法輕易做到這點。
    *   **Application Library**: Good at business-logic-related fallbacks. For example: when the recommendation service fails, the code decides to return a "Trending Products" list. A sidecar cannot easily achieve this.

### 3.2 避免級聯故障 (Preventing Cascading Failures)
在微服務架構中，一個服務的延遲（Latency）比完全停機（Downtime）更可怕。延遲會導致上游服務的執行緒池（Thread Pool）被佔滿，最終導致整個系統癱瘓（Domino Effect）。

In a microservices architecture, latency in one service is often scarier than complete downtime. Latency causes upstream service thread pools to fill up, eventually paralyzing the entire system (Domino Effect).

**設計決策 (Design Decision)**：
*   **Fail Fast**: 如果無法在 500ms 內得到回應，與其等待 30 秒後超時，不如立即報錯。
    **Fail Fast**: If a response cannot be obtained within 500ms, it is better to error out immediately rather than waiting 30 seconds for a timeout.
*   **Shed Load**: 當負載過高時，主動丟棄低優先級的請求（Load Shedding），保住核心業務。
    **Shed Load**: When load is too high, proactively drop low-priority requests (Load Shedding) to save core business functions.

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)
我們正在設計一個 **電商結帳服務 (Checkout Service)**。它依賴一個外部的 **庫存服務 (Inventory Service)**。庫存服務是老舊系統，偶爾會回應極慢或隨機 503 錯誤。

We are designing an **E-commerce Checkout Service**. It relies on an external **Inventory Service**. The Inventory Service is a legacy system that occasionally responds very slowly or throws random 503 errors.

### 階段 1：Naive Approach (脆弱的設計)
直接使用 HTTP Client 呼叫。

Phase 1: Naive Approach (Fragile Design) - Direct HTTP Client call.

```java
// Bad Practice: No timeout, no protection
public boolean checkInventory(String productId) {
    // If inventory-service hangs, this thread hangs forever.
    return httpClient.get("http://inventory-service/items/" + productId);
}
```
*   **問題**：若庫存服務卡住，結帳服務的執行緒會被耗盡，導致無法處理其他請求（甚至是與庫存無關的請求）。
*   **Problem**: If the inventory service hangs, the checkout service's threads will be exhausted, rendering it unable to handle other requests (even those unrelated to inventory).

### 階段 2：引入 Circuit Breaker 與 Bulkhead (Resilient Design)
我們使用 `Resilience4j` (Java) 或類似概念來保護系統。

Phase 2: Introducing Circuit Breaker & Bulkhead (Resilient Design) - Using `Resilience4j` (Java) or similar concepts.

```java
// Configuration (Conceptual)
CircuitBreakerConfig circuitConfig = CircuitBreakerConfig.custom()
    .failureRateThreshold(50) // If 50% requests fail
    .waitDurationInOpenState(Duration.ofMillis(10000)) // Wait 10s before trying again
    .slidingWindowSize(10) // Look at last 10 requests
    .build();

BulkheadConfig bulkheadConfig = BulkheadConfig.custom()
    .maxConcurrentCalls(20) // Only 20 concurrent threads allowed for Inventory
    .maxWaitDuration(Duration.ofMillis(1)) // Fail fast if pool is full
    .build();

// Decorating the call
@CircuitBreaker(name = "inventory", fallbackMethod = "fallbackInventory")
@Bulkhead(name = "inventory")
public boolean checkInventory(String productId) {
    return httpClient.get("http://inventory-service/items/" + productId);
}

// Fallback logic (Graceful Degradation)
public boolean fallbackInventory(String productId, Throwable t) {
    logger.warn("Inventory service failed: {}, assuming in stock for VIPs", t.getMessage());
    // Business Decision: Allow purchase, reconcile later? Or deny?
    // Here we might return 'true' but flag for manual review.
    return true; 
}
```

### 思考步驟 (Thinking Process)
1.  **隔離 (Isolation)**：`Bulkhead` 限制了同時呼叫庫存服務的併發數為 20。即使庫存服務變慢，最多只會佔用 20 個執行緒，結帳服務的其他部分不受影響。
    **Isolation**: `Bulkhead` limits concurrent calls to the inventory service to 20. Even if the inventory service slows down, it consumes at most 20 threads, leaving the rest of the checkout service unaffected.
2.  **快速失敗 (Fail Fast)**：當錯誤率達到 50% 時，`Circuit Breaker` 開啟。後續請求不再發送網路呼叫，直接執行 `fallbackInventory`。
    **Fail Fast**: When the error rate hits 50%, the `Circuit Breaker` opens. Subsequent requests skip the network call and execute `fallbackInventory` directly.
3.  **降級 (Fallback)**：定義了當系統不可用時的業務行為。這比單純丟出 `500 Internal Server Error` 給使用者要好得多。
    **Fallback**: Defines the business behavior when the system is unavailable. This is much better than simply throwing a `500 Internal Server Error` to the user.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 重試風暴 (Retry Storms)
**錯誤描述**：當服務 A 呼叫服務 B 失敗時，立即重試 3 次。如果服務 B 是因為過載而失敗，服務 A 的重試會讓流量瞬間翻倍，導致服務 B 死得更徹底。
**Description**: When Service A fails to call Service B, it retries 3 times immediately. If Service B failed due to overload, Service A's retries will instantly double the traffic, causing Service B to crash even harder.

**解決方案**：
*   **Exponential Backoff**: 每次重試等待時間加倍 (1s, 2s, 4s...)。
*   **Jitter (抖動)**: 在等待時間中加入隨機值，避免所有客戶端同時重試 (Thundering Herd)。
**Solution**:
*   **Exponential Backoff**: Double the wait time after each retry (1s, 2s, 4s...).
*   **Jitter**: Add a random value to the wait time to prevent all clients from retrying simultaneously (Thundering Herd).

### 5.2 共享艙壁 (Shared Bulkhead)
**錯誤描述**：在整個應用程式中只使用一個全域的執行緒池來處理所有外部 API 呼叫。
**Description**: Using a single global thread pool for all external API calls across the entire application.

**後果**：一個次要功能的外部服務（如「發送 Email」）變慢，會耗盡全域執行緒池，導致核心功能（如「結帳」）無法執行。
**Consequence**: If a secondary external service (like "Send Email") slows down, it exhausts the global thread pool, preventing core functions (like "Checkout") from executing.

### 5.3 降級邏輯本身也會失敗 (Fallback that Fails)
**錯誤描述**：Fallback 邏輯中包含了複雜的網路呼叫或資料庫查詢。
**Description**: The fallback logic itself contains complex network calls or database queries.

**最佳實務**：Fallback 應該盡可能簡單，最好是計算型邏輯或回傳靜態預設值（Static Default）。如果 Fallback 也失敗，系統就真的無藥可救了。
**Best Practice**: Fallbacks should be as simple as possible, preferably computational logic or returning a static default. If the fallback also fails, the system is truly helpless.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何在 Service Mesh (如 Istio) 與 Application Code (如 Resilience4j) 之間做選擇？
**How do you choose between Service Mesh (e.g., Istio) and Application Code (e.g., Resilience4j)?**

*   **高分回答要點**：
    *   **關注點分離**：Service Mesh 適合處理通用的網路彈性（重試、超時、斷路器），這讓維運團隊可以統一管理配置，無需修改程式碼。
    *   **業務感知**：Application Code 適合處理「需要業務上下文」的邏輯，特別是 **Fallback**（降級）與 **Bulkhead**（執行緒隔離）。Mesh 無法知道當 DB 失敗時該回傳什麼預設值。
    *   **混合策略**：通常建議在 Mesh 層做基礎防護，在 Code 層做精細的業務降級。

### Q2: 請解釋 Rate Limiting 的不同層級及其適用場景？
**Explain the different levels of Rate Limiting and their use cases.**

*   **高分回答要點**：
    *   **Gateway Level (Global)**: 保護整個系統入口，防止 DDoS 或單一用戶濫用。通常使用 Redis Token Bucket 演算法。
    *   **Service Level (Local/Sidecar)**: 保護單一微服務不被上游打垮。
    *   **Resource Level**: 針對特定昂貴 API（如「匯出 5 年報表」）進行嚴格限流。
    *   **區分**：強調「保護自己（Server-side Rate Limiting）」與「保護下游（Client-side Throttling）」的區別。

### Q3: 如果你要在生產環境引入 Chaos Engineering，你會怎麼開始？
**If you were to introduce Chaos Engineering in production, how would you start?**

*   **高分回答要點**：
    *   **最小爆炸半徑 (Blast Radius)**：從非關鍵服務（Non-critical path）或一小部分流量（Canary）開始。
    *   **可觀測性 (Observability)**：必須先有完善的監控。如果你看不見系統崩潰，就不能做混沌實驗。
    *   **終止開關 (Kill Switch)**：必須能一鍵停止實驗，讓系統瞬間恢復正常。
    *   **Game Day**: 定期舉行演練，而不僅僅是自動化執行。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Fail Fast**: 不要讓請求無限期等待；快速失敗能釋放資源。
2.  **Circuit Breaker**: 防止對已經故障的服務持續呼叫，給予系統恢復時間。
3.  **Bulkhead**: 資源隔離，防止單點故障拖垮整個系統（鐵達尼號原則）。
4.  **Idempotency (冪等性)**: 為了安全地重試（Retry），API 必須設計為冪等的。
5.  **Chaos Engineering**: 這是驗證 Resiliency 設計是否有效的唯一真理。

### 後續延伸 (Next Steps)
*   **實作**：在你的專案中引入 Chaos Mesh 或 Gremlin，嘗試弄掛一個 Pod，看系統是否如預期運作。
*   **閱讀**：下一章將探討 **可觀測性 (Observability)**。因為沒有 Tracing 和 Metrics，你無法知道 Circuit Breaker 何時開啟，也無法分析故障的根因。
    *   *Next Chapter Preview: Observability (Tracing, Metrics, Logging).*