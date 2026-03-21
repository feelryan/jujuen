# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲原生（Cloud-Native）與分散式系統的世界中，「失敗」不是異常，而是常態。網路會抖動、Pod 會重啟、資料庫會發生 Failover。資深工程師與初階工程師最大的區別，在於是否具備「Design for Failure」的思維。本章不討論如何避免失敗，而是討論如何優雅地處理失敗，確保系統在高負載或部分組件故障時，仍能維持運作。

In the world of Cloud-Native and distributed systems, "failure" is not an exception; it is the norm. Networks jitter, Pods restart, and databases failover. The biggest distinction between a senior engineer and a junior one lies in the "Design for Failure" mindset. This chapter does not focus on avoiding failure, but rather on handling it gracefully, ensuring the system remains operational under high load or partial component failure.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **掌握韌性模式（Resilience Patterns）**：深刻理解並實作 Retry（重試）、Circuit Breaker（斷路器）、Bulkhead（艙壁）與 Throttling（限流）。
    **Master Resilience Patterns**: Deeply understand and implement Retry, Circuit Breaker, Bulkhead, and Throttling.
2.  **解決分散式協作問題**：理解 Leader Election（領袖選舉）的必要性及其在 Kubernetes 或微服務架構中的實作策略。
    **Solve Distributed Coordination Problems**: Understand the necessity of Leader Election and its implementation strategies within Kubernetes or microservices architectures.
3.  **權衡一致性與可用性**：在設計高可用系統時，能清楚解釋 Idempotency（冪等性）與 Retry 之間的關鍵依賴。
    **Trade-off between Consistency and Availability**: Clearly explain the critical dependency between Idempotency and Retry when designing high-availability systems.
4.  **避免常見的反模式**：識別並修復如 Retry Storms（重試風暴）或 Cascading Failures（連鎖雪崩）等架構隱患。
    **Avoid Common Anti-patterns**: Identify and fix architectural hazards such as Retry Storms or Cascading Failures.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Design for Failure (為失敗而設計)

傳統單體應用（Monolith）往往依賴單一強大的硬體，而雲原生架構則是由許多不可靠的組件組成的可靠系統。我們的心智模型應從「如何防止組件壞掉」轉變為「當組件壞掉時，系統如何降級（Degrade）而非崩潰」。

Traditional monolithic applications often rely on single, powerful hardware, whereas cloud-native architectures are reliable systems built from many unreliable components. Our mental model must shift from "how to prevent components from breaking" to "how the system degrades rather than crashes when components break."

## 2.2 關鍵模式類比 (Key Pattern Analogies)

為了直觀理解，我們可以使用以下類比：
For intuitive understanding, we can use the following analogies:

*   **Retry (重試)**：
    *   **類比**：打電話給朋友，對方佔線，你過幾秒再撥。
    *   **核心**：針對「暫時性故障（Transient Failures）」有效。
    *   **Analogy**: Calling a friend who is on another line; you dial again after a few seconds.
    *   **Core**: Effective for "Transient Failures."

*   **Circuit Breaker (斷路器)**：
    *   **類比**：家裡的保險絲。當電流過大（錯誤率過高）時，自動跳脫斷電，防止電器燒毀（防止下游服務被壓垮），冷卻後再嘗試閉合。
    *   **核心**：防止系統浪費資源去呼叫一個已經掛掉的服務，並給予該服務恢復的時間（Fail Fast）。
    *   **Analogy**: The fuse in your home. When the current is too high (error rate is too high), it trips to cut power, preventing appliance damage (preventing downstream services from being overwhelmed), and tries to close again after cooling down.
    *   **Core**: Prevents the system from wasting resources calling a dead service and gives that service time to recover (Fail Fast).

*   **Bulkhead (艙壁)**：
    *   **類比**：船艙設計。如果船底破了一個洞，只有該艙進水，船不會沉。
    *   **核心**：資源隔離（Resource Isolation）。例如，不讓一個慢速的 API 耗盡所有的 Thread Pool，導致核心登入功能也無法使用。
    *   **Analogy**: Ship compartment design. If the hull is breached, only that compartment floods; the ship does not sink.
    *   **Core**: Resource Isolation. For example, preventing a slow API from exhausting the entire Thread Pool, which would render the core login function unusable.

*   **Throttling / Rate Limiting (限流)**：
    *   **類比**：高速公路匝道的紅綠燈控制（Ramp Metering）。
    *   **核心**：保護伺服器不被過量請求壓垮（Backpressure）。
    *   **Analogy**: Ramp metering lights on highway on-ramps.
    *   **Core**: Protecting the server from being overwhelmed by excessive requests (Backpressure).

*   **Leader Election (領袖選舉)**：
    *   **類比**：一群人開會，必須選出一位主席來發言，避免大家同時說話（Race Condition）。
    *   **核心**：確保在分散式環境中，同一時間只有一個實例執行特定任務（如排程 Job、寫入共享資源）。
    *   **Analogy**: A group meeting where a chairperson must be elected to speak, preventing everyone from talking at once (Race Condition).
    *   **Core**: Ensuring that only one instance performs a specific task (e.g., scheduled jobs, writing to shared resources) at a time in a distributed environment.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或實際架構規劃中，這些模式通常位於 **API Gateway**、**Service Mesh (Sidecar)** 或 **Application Client Library** 層級。

In System Design Interviews or actual architectural planning, these patterns are typically located at the **API Gateway**, **Service Mesh (Sidecar)**, or **Application Client Library** level.

## 3.1 典型架構位置 (Typical Architectural Placement)

1.  **Client-Side Resilience (客戶端韌性)**：
    *   由呼叫方（Caller）實作 Retry 與 Circuit Breaker。這是最靈活的，因為 Caller 最清楚業務邏輯是否允許重試（例如：讀取操作可重試，非冪等的寫入操作需謹慎）。
    *   Implemented by the Caller. This is the most flexible because the Caller knows best whether the business logic permits retries (e.g., read operations are retryable; non-idempotent write operations require caution).

2.  **Service Mesh (e.g., Istio/Envoy)**：
    *   將 Retry、Timeout、Circuit Breaking 下沉到基礎設施層。
    *   **優點**：語言無關（Polyglot），業務代碼乾淨。
    *   **缺點**：對業務邏輯缺乏感知（例如：它不知道某個 HTTP 500 是否真的可以重試）。
    *   Offloads Retry, Timeout, and Circuit Breaking to the infrastructure layer.
    *   **Pros**: Language agnostic (Polyglot), cleaner business code.
    *   **Cons**: Lack of business logic awareness (e.g., it doesn't know if a specific HTTP 500 is genuinely retryable).

## 3.2 對非功能性需求的影響 (Impact on Non-Functional Requirements)

*   **Availability (可用性)**：顯著提升。短暫的網路波動不會導致使用者請求失敗。
    **Availability**: Significantly improved. Transient network blips do not cause user requests to fail.
*   **Latency (延遲)**：
    *   **Retry** 會增加 P99 Latency（尾部延遲），因為失敗的請求需要多次嘗試。
    *   **Circuit Breaker** 有助於控制 Latency，因為它會快速失敗（Fail Fast），避免客戶端無限期等待超時。
    *   **Retry** increases P99 Latency (tail latency) because failed requests require multiple attempts.
    *   **Circuit Breaker** helps control Latency by failing fast, preventing clients from waiting indefinitely for timeouts.
*   **Consistency (一致性)**：
    *   Leader Election 是強一致性（Strong Consistency）的關鍵。
    *   Retry 機制必須配合 **Idempotency Key** 使用，否則會導致資料不一致（如重複扣款）。
    *   Leader Election is key to Strong Consistency.
    *   Retry mechanisms must be used with an **Idempotency Key**; otherwise, data inconsistency (e.g., double charging) will occur.

---

# 4. 逐步示例：指數退避重試與抖動 (Walkthrough: Exponential Backoff with Jitter)

## 4.1 問題背景 (Scenario)

假設你正在設計一個訂單服務，需要呼叫下游的「庫存服務」來扣減庫存。庫存服務偶爾會因為高併發而回應 HTTP 503 (Service Unavailable) 或 429 (Too Many Requests)。

Suppose you are designing an Order Service that needs to call a downstream "Inventory Service" to deduct inventory. The Inventory Service occasionally responds with HTTP 503 (Service Unavailable) or 429 (Too Many Requests) due to high concurrency.

## 4.2 Naive Approach (天真的做法)

最簡單的做法是立即重試。

The simplest approach is to retry immediately.

```java
// BAD PRACTICE: Immediate Retry
int maxRetries = 3;
for (int i = 0; i < maxRetries; i++) {
    try {
        return inventoryService.deduct(itemId);
    } catch (ServiceUnavailableException e) {
        // Immediately loop again
        if (i == maxRetries - 1) throw e;
    }
}
```

**問題 (Problem)**：如果庫存服務已經過載，立即重試只會加劇負載，導致服務徹底崩潰。這被稱為「Thundering Herd Problem（驚群效應/羊群效應）」。
**Problem**: If the Inventory Service is already overloaded, immediate retries will only exacerbate the load, causing the service to crash completely. This is known as the "Thundering Herd Problem."

## 4.3 Mature Solution: Exponential Backoff + Jitter (成熟解法)

我們引入兩個概念：
1.  **Exponential Backoff (指數退避)**：等待時間隨次數指數增長 (1s, 2s, 4s...)。
2.  **Jitter (抖動)**：在等待時間中加入隨機值，避免所有客戶端在同一時刻發起重試（同步重試）。

We introduce two concepts:
1.  **Exponential Backoff**: Wait time grows exponentially with attempts (1s, 2s, 4s...).
2.  **Jitter**: Add a random value to the wait time to prevent all clients from retrying at the exact same moment (synchronized retries).

```java
// BETTER PRACTICE: Exponential Backoff with Jitter
public void callWithRetry() {
    int maxRetries = 5;
    long baseDelay = 100; // milliseconds
    long maxDelay = 2000; // cap the delay

    for (int attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            inventoryService.deduct(itemId);
            return; // Success
        } catch (ServiceUnavailableException e) {
            if (attempt == maxRetries) throw e;

            // 1. Calculate Exponential Backoff
            long delay = (long) (baseDelay * Math.pow(2, attempt));
            
            // 2. Apply Cap (Max Delay)
            delay = Math.min(delay, maxDelay);

            // 3. Add Jitter (Randomness)
            // Full Jitter strategy: random between 0 and calculated delay
            long jitteredDelay = (long) (Math.random() * delay);

            try {
                Thread.sleep(jitteredDelay);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(ie);
            }
        }
    }
}
```

### 為何這樣做有效？ (Why it works?)
*   **指數退避**給了下游服務喘息的空間。
*   **Jitter** 打散了重試流量，將尖峰削平（Smoothing the spikes）。
*   **Exponential Backoff** gives the downstream service room to breathe.
*   **Jitter** disperses the retry traffic, smoothing the spikes.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Retry Storms (重試風暴)

**描述**：Service A 呼叫 Service B，Service B 呼叫 Service C。如果 C 故障，B 重試 3 次，A 也重試 3 次。結果 C 會收到 $3 \times 3 = 9$ 次請求。如果呼叫鏈更深，請求量會呈幾何級數爆炸。
**Description**: Service A calls Service B, and Service B calls Service C. If C fails, B retries 3 times, and A also retries 3 times. As a result, C receives $3 \times 3 = 9$ requests. If the call chain is deeper, the request volume explodes geometrically.

**解法 (Solution)**：
*   **Circuit Breaker**：當 B 發現 C 失敗率高時，直接熔斷，不再重試。
*   **Retry Budget**：在整個呼叫鏈路中傳遞一個「重試預算」Token，用完即止。
*   **Solution**:
    *   **Circuit Breaker**: When B detects a high failure rate from C, it trips the breaker and stops retrying.
    *   **Retry Budget**: Pass a "retry budget" token along the call chain; stop when exhausted.

## 5.2 Bulkhead Misconfiguration (艙壁配置錯誤)

**描述**：使用 Thread Pool 隔離，但將 Pool Size 設定過大。
**Description**: Using Thread Pool isolation but setting the Pool Size too large.

**為何不好**：如果 Pool 太大，當服務變慢時，太多的執行緒會被阻塞（Blocked），導致 Context Switch 過高，消耗過多記憶體，反而拖垮整台機器，失去了隔離的意義。
**Why it's bad**: If the pool is too large, too many threads become blocked when the service slows down, leading to excessive Context Switching and memory consumption, which drags down the entire machine, defeating the purpose of isolation.

## 5.3 DIY Leader Election (自製領袖選舉)

**描述**：試圖用資料庫的一個 `status=LOCKED` 欄位來實作 Leader Election，卻沒有處理好 TTL（Time To Live）或原子性操作。
**Description**: Trying to implement Leader Election using a `status=LOCKED` field in a database without properly handling TTL (Time To Live) or atomic operations.

**為何不好**：如果 Leader 當機且沒有釋放鎖（也沒有 TTL），整個系統將永遠沒有 Leader（Deadlock）。應使用成熟的方案如 Kubernetes Leases, Redis Redlock, 或 ZooKeeper/Etcd。
**Why it's bad**: If the Leader crashes without releasing the lock (and there is no TTL), the entire system will be leaderless forever (Deadlock). Use mature solutions like Kubernetes Leases, Redis Redlock, or ZooKeeper/Etcd.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於檢視候選人是否具備資深工程師的經驗與判斷力。
These questions can be used to assess whether a candidate possesses the experience and judgment of a senior engineer.

## 6.1 Question: 如何在分散式系統中設計一個 Rate Limiter？
**How would you design a Rate Limiter in a distributed system?**

*   **高分回答要點 (Key Points)**：
    *   **演算法**：提及 Token Bucket（令牌桶）或 Leaky Bucket（漏桶）。
    *   **儲存**：使用 Redis (Lua script) 進行原子計數。
    *   **粒度**：區分 Global Rate Limit vs Local Rate Limit（單機限流）。
    *   **Race Condition**：說明如何處理併發讀寫（Read-Modify-Write）問題。

## 6.2 Question: 什麼時候**不應該**使用 Retry？
**When should you **NOT** use Retry?**

*   **高分回答要點 (Key Points)**：
    *   **非冪等操作 (Non-idempotent operations)**：如轉帳、下單，除非有去重機制。
    *   **Client Error (4xx)**：如 400 Bad Request, 401 Unauthorized，重試無意義。
    *   **對延遲極度敏感的場景**：與其重試導致超時，不如直接回傳 Fallback 值或 Cached Data。
    *   **Circuit Breaker Open**：當斷路器已開啟，重試只是浪費資源。

## 6.3 Question: 請解釋 Bulkhead 模式如何防止連鎖故障？
**Explain how the Bulkhead pattern prevents cascading failures.**

*   **高分回答要點 (Key Points)**：
    *   **資源隔離**：強調隔離的是 Thread Pools, Connection Pools 或 Semaphores。
    *   **故障遏制**：說明當一個依賴服務（Dependency）回應變慢或卡死時，只有對應的 Pool 會被耗盡，系統的其他部分（如 Health Check API、其他業務功能）仍有資源可用，保持響應。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 7.1 記憶錨點 (Key Takeaways)

1.  **Failures are inevitable**: 系統設計的目標是 Resilience（韌性），而非完美的 Reliability（可靠性）。
2.  **Retry needs Backoff & Jitter**: 永遠不要使用緊湊的迴圈重試，這會導致 Thundering Herd。
3.  **Circuit Breaker protects the system**: 讓系統快速失敗（Fail Fast），給予下游恢復時間。
4.  **Bulkhead isolates faults**: 不要讓一個壞掉的組件拖垮整艘船。
5.  **Idempotency is mandatory for Retry**: 沒有冪等性，重試就是災難。
6.  **Leader Election requires TTL**: 防止死鎖是分散式鎖的核心考量。

## 7.2 後續延伸 (Next Steps)

*   **實作練習**：使用 Java 的 **Resilience4j** 或 Go 的 **go-resilience** 庫，在一個微服務 Demo 中實作上述模式。
*   **延伸閱讀**：下一章將探討 **Observability & Tracing**（可觀測性與追蹤）。如果你實作了 Retry 和 Circuit Breaker，卻沒有監控它們何時觸發，那麼系統發生問題時你將一無所知。
*   **Implementation Practice**: Use Java's **Resilience4j** or Go's **go-resilience** library to implement the above patterns in a microservice demo.
*   **Further Reading**: The next chapter will explore **Observability & Tracing**. If you implement Retry and Circuit Breaker but don't monitor when they trigger, you will be blind when issues occur.