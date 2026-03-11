# 1. 前言與學習目標 (Introduction & Learning Objectives)

在傳統的 Spring MVC 架構中，我們習慣了「一個請求對應一個執行緒」（Thread-per-Request）的模型。然而，隨著微服務架構的普及與高併發需求的增加，這種阻塞式（Blocking）模型在處理大量 I/O 等待時，往往會因為執行緒 Context Switch 與記憶體消耗而遇到瓶頸。本章將帶領資深工程師深入 Spring WebFlux 與 Reactive Programming 的核心。

In the traditional Spring MVC architecture, we are accustomed to the "Thread-per-Request" model. However, with the proliferation of microservices and the demand for high concurrency, this blocking model often hits a bottleneck due to thread Context Switching and memory consumption when dealing with extensive I/O waits. This chapter guides senior engineers into the core of Spring WebFlux and Reactive Programming.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分 Blocking 與 Non-blocking 架構的適用場景**：理解何時該堅守 Spring MVC，何時該轉向 Spring WebFlux。
    **Distinguish between Blocking and Non-blocking architectures**: Understand when to stick with Spring MVC and when to switch to Spring WebFlux.
2.  **掌握 Netty Event Loop 與 Reactor 核心模型**：深入理解底層執行緒模型，而不僅僅是會寫 `Mono` 和 `Flux`。
    **Master Netty Event Loop and Reactor Core Models**: Deeply understand the underlying threading model, beyond just writing `Mono` and `Flux`.
3.  **實作並解釋 Backpressure（背壓）機制**：在系統設計面試中，能夠清楚說明如何防止下游服務被上游流量沖垮。
    **Implement and explain Backpressure**: Clearly articulate how to prevent downstream services from being overwhelmed by upstream traffic in system design interviews.
4.  **避免 Reactive Programming 的常見陷阱**：例如在 Event Loop 中執行阻塞操作，或錯誤理解 `publishOn` 與 `subscribeOn`。
    **Avoid common Reactive Programming pitfalls**: Such as executing blocking operations within the Event Loop, or misunderstanding `publishOn` vs. `subscribeOn`.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Servlet Stack vs. Reactive Stack

**直覺類比 (Analogy)**：
想像一家餐廳的運作模式：
*   **Spring MVC (Servlet)**：每桌客人配有一位專屬服務生。服務生點完餐後，會站在廚房門口**發呆等待**直到菜做好，再端給客人。如果客人太多，餐廳必須僱用數千名服務生（Threads），導致管理混亂且成本高昂。
*   **Spring WebFlux (Reactive)**：全餐廳只有幾位「超級服務生」（Event Loop Threads）。服務生點完餐後，將訂單丟進廚房（Callback/Event），立刻轉身去服務下一桌。當菜做好時，廚房發出通知，服務生再回來端菜。極少的人力就能處理極高的吞吐量。

**Intuitive Analogy**:
Imagine the operation of a restaurant:
*   **Spring MVC (Servlet)**: Each table has a dedicated waiter. After taking the order, the waiter stands at the kitchen door **idling and waiting** until the food is ready before serving it. If there are too many customers, the restaurant must hire thousands of waiters (Threads), leading to chaotic management and high costs.
*   **Spring WebFlux (Reactive)**: The restaurant has only a few "super waiters" (Event Loop Threads). After taking an order, the waiter throws it to the kitchen (Callback/Event) and immediately turns to serve the next table. When the food is ready, the kitchen notifies the waiter to serve it. Very few resources handle very high throughput.

### 2.2 Netty Event Loop 模型 (The Netty Event Loop Model)

Spring WebFlux 預設使用 Netty 作為伺服器。其核心是 **Event Loop**。
Spring WebFlux uses Netty as the default server. Its core is the **Event Loop**.

*   **Non-blocking I/O**: 執行緒發起 I/O 請求後不等待，繼續處理其他任務。
*   **Selector**: 監控多個 Channel 的狀態（如連線、讀寫就緒）。
*   **Single Thread (per core)**: 通常 Event Loop 的數量等於 CPU 核心數。這意味著你**絕對不能**在 Event Loop 中執行任何阻塞操作（如 `Thread.sleep` 或 JDBC 查詢），否則整個核心將停擺。

*   **Non-blocking I/O**: The thread initiates an I/O request and continues processing other tasks without waiting.
*   **Selector**: Monitors the status of multiple Channels (e.g., connect, read/write ready).
*   **Single Thread (per core)**: Typically, the number of Event Loops equals the number of CPU cores. This means you **must never** execute any blocking operation (like `Thread.sleep` or JDBC query) inside the Event Loop; otherwise, the entire core halts.

### 2.3 Project Reactor: Mono & Flux

這是 Java 對 Reactive Streams 規範的實作：
This is Java's implementation of the Reactive Streams specification:

*   **Mono<T>**: 代表 0 或 1 個元素的異步序列（類似 `Optional<T>` 但具時間維度）。
    **Mono<T>**: Represents an asynchronous sequence of 0 or 1 element (similar to `Optional<T>` but with a time dimension).
*   **Flux<T>**: 代表 0 到 N 個元素的異步序列（類似 `Stream<T>` 或 `List<T>`）。
    **Flux<T>**: Represents an asynchronous sequence of 0 to N elements (similar to `Stream<T>` or `List<T>`).

### 2.4 Backpressure (背壓)

這是 Reactive Streams 最重要的特性。傳統 Push 模型是上游拼命推資料，下游來不及處理就 OOM（Out of Memory）。Reactive Pull 模型允許下游（Subscriber）告訴上游（Publisher）：「我現在只能處理 10 筆資料，請給我 10 筆」。

This is the most critical feature of Reactive Streams. In the traditional Push model, the upstream pushes data aggressively, causing OOM (Out of Memory) if the downstream cannot keep up. The Reactive Pull model allows the downstream (Subscriber) to tell the upstream (Publisher): "I can only handle 10 records right now, please give me 10."

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 典型應用場景 (Typical Use Cases)

在系統設計中，選擇 WebFlux 通常是為了**高吞吐量（High Throughput）**與**高延遲 I/O（High Latency I/O）**的場景，而非為了降低單一請求的延遲（Latency）。

In system design, choosing WebFlux is usually for **High Throughput** and **High Latency I/O** scenarios, not for reducing the latency of a single request.

1.  **API Gateway (e.g., Spring Cloud Gateway)**:
    *   需要維持成千上萬個長連線，且主要工作是路由請求（I/O bound）。WebFlux 能以極低的記憶體佔用處理大量併發。
    *   Needs to maintain thousands of long-lived connections, and the main job is routing requests (I/O bound). WebFlux handles massive concurrency with a very low memory footprint.

2.  **Real-time Data Ingestion / Streaming**:
    *   處理來自 IoT 設備或 Log 收集器的高頻數據流。
    *   Handling high-frequency data streams from IoT devices or log collectors.

3.  **Aggregator Services (BFF - Backend for Frontend)**:
    *   同時呼叫多個下游微服務並聚合結果。Reactive 的 `zip` 或 `merge` 操作能優雅地處理並行請求與錯誤處理。
    *   Calling multiple downstream microservices simultaneously and aggregating results. Reactive `zip` or `merge` operations elegantly handle parallel requests and error handling.

### 3.2 架構權衡 (Architectural Trade-offs)

| Feature | Spring MVC (Blocking) | Spring WebFlux (Non-blocking) |
| :--- | :--- | :--- |
| **Learning Curve** | Low (Imperative logic is natural) | High (Functional, Declarative, Async mind-shift) |
| **Debugging** | Easy (Stack traces are readable) | Hard (Stack traces are fragmented across threads) |
| **Database Support** | Mature (JDBC, JPA, Hibernate) | Evolving (R2DBC is newer, less ecosystem support) |
| **Ideal For** | CRUD apps, CPU-bound tasks, Legacy | Gateways, Streaming, High-concurrency I/O |

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)
我們需要設計一個 User Dashboard API，它需要同時從三個不同的微服務獲取資料：
1.  User Profile Service (50ms)
2.  Order History Service (200ms)
3.  Recommendation Service (150ms)

We need to design a User Dashboard API that fetches data from three different microservices simultaneously:
1.  User Profile Service (50ms)
2.  Order History Service (200ms)
3.  Recommendation Service (150ms)

### 4.1 Naive Approach (Blocking / Sequential)

如果使用傳統阻塞方式，總耗時將是 50 + 200 + 150 = 400ms。
If using the traditional blocking approach, the total time would be 50 + 200 + 150 = 400ms.

```java
// Conceptual Blocking Code
User user = userRepo.findById(id); // blocks
List<Order> orders = orderClient.getOrders(id); // blocks
List<Product> recs = recommendationClient.getRecs(id); // blocks
return new Dashboard(user, orders, recs);
```

### 4.2 Mature Solution (Reactive / Parallel)

使用 WebFlux 的 `Mono.zip` 並行執行，總耗時將取決於最慢的服務（約 200ms）。這不僅提升了回應速度，更重要的是，在等待期間，執行緒被釋放去處理其他請求。

Using WebFlux's `Mono.zip` for parallel execution, the total time depends on the slowest service (approx. 200ms). This not only improves response speed but, more importantly, releases the thread to handle other requests during the wait.

```java
@Service
public class DashboardService {

    private final WebClient userClient;
    private final WebClient orderClient;
    private final WebClient recommendationClient;

    // Constructor injection omitted

    public Mono<DashboardDTO> getDashboard(String userId) {
        
        Mono<UserDTO> userMono = userClient.get()
            .uri("/users/{id}", userId)
            .retrieve()
            .bodyToMono(UserDTO.class)
            .subscribeOn(Schedulers.boundedElastic()); // Optional: if client is blocking

        Mono<List<OrderDTO>> ordersMono = orderClient.get()
            .uri("/orders/{id}", userId)
            .retrieve()
            .bodyToMono(new ParameterizedTypeReference<List<OrderDTO>>() {})
            .onErrorReturn(Collections.emptyList()); // Fallback: empty list on error

        Mono<List<RecDTO>> recsMono = recommendationClient.get()
            .uri("/recs/{id}", userId)
            .retrieve()
            .bodyToMono(new ParameterizedTypeReference<List<RecDTO>>() {});

        // Combine results
        return Mono.zip(userMono, ordersMono, recsMono)
            .map(tuple -> {
                UserDTO user = tuple.getT1();
                List<OrderDTO> orders = tuple.getT2();
                List<RecDTO> recs = tuple.getT3();
                return new DashboardDTO(user, orders, recs);
            });
    }
}
```

### 4.3 關鍵細節 (Key Details)

1.  **`Mono.zip`**: 等待所有 Mono 完成。如果其中一個發出 Error，整個 zip 會立即失敗（Fail-fast）。
    **`Mono.zip`**: Waits for all Monos to complete. If one emits an Error, the entire zip fails immediately (Fail-fast).
2.  **`onErrorReturn`**: 提供了優雅降級（Graceful Degradation）。如果訂單服務掛了，我們仍然可以回傳 User 和 Recommendations，而不是 500 錯誤。
    **`onErrorReturn`**: Provides Graceful Degradation. If the order service is down, we can still return User and Recommendations instead of a 500 error.
3.  **複雜度 (Complexity)**: 空間複雜度極低，因為不需要為每個請求保留 Stack memory。
    **Complexity**: Space complexity is extremely low because there is no need to reserve Stack memory for each request.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 Blocking the Event Loop (阻塞事件迴圈)

這是最致命的錯誤。如果你在 Reactor 流程中呼叫了阻塞的 JDBC、`Thread.sleep` 或進行大量 CPU 運算，你會卡死負責處理成千上萬請求的 Event Loop thread。

This is the most fatal error. If you call blocking JDBC, `Thread.sleep`, or perform heavy CPU computations within a Reactor flow, you will freeze the Event Loop thread responsible for handling thousands of requests.

*   **Bad**:
    ```java
    return Mono.fromSupplier(() -> {
        // DANGEROUS: Blocking call in Event Loop
        return jpaRepository.findById(id); 
    });
    ```
*   **Good**: 使用 `subscribeOn` 將阻塞操作卸載到專用的 Thread Pool，或改用 R2DBC。
    **Good**: Use `subscribeOn` to offload blocking operations to a dedicated Thread Pool, or switch to R2DBC.
    ```java
    return Mono.fromCallable(() -> jpaRepository.findById(id))
               .subscribeOn(Schedulers.boundedElastic());
    ```

### 5.2 The "Nothing Happens" Pitfall

Reactive Streams 是**惰性（Lazy）**的。如果你定義了一個複雜的 Flux 流程但沒有 `subscribe`（無論是手動 subscribe 或由 Spring WebFlux 框架幫你 subscribe），這段程式碼永遠不會執行。

Reactive Streams are **Lazy**. If you define a complex Flux flow but do not `subscribe` (either manually or letting the Spring WebFlux framework do it for you), the code will never execute.

*   **Anti-pattern**:
    ```java
    public void doSomething() {
        userRepository.save(user); // Returns Mono<User>, but nothing happens!
    }
    ```
*   **Fix**: 確保方法回傳 Mono/Flux 並串接起來，讓最上層的 Controller 或 Subscriber 觸發它。
    **Fix**: Ensure the method returns Mono/Flux and chain them, letting the top-level Controller or Subscriber trigger it.

### 5.3 FlatMap vs Map Confusion

*   **`map`**: 用於同步轉換（1-to-1），例如將 String 轉為 Integer。
    **`map`**: Used for synchronous transformation (1-to-1), e.g., converting a String to an Integer.
*   **`flatMap`**: 用於異步轉換（1-to-N or 1-to-Mono），例如拿到 User ID 後去呼叫另一個 Service 回傳 `Mono<Details>`。如果你在 `map` 裡回傳 Mono，你會得到 `Mono<Mono<T>>`，這通常不是你要的。
    **`flatMap`**: Used for asynchronous transformation (1-to-N or 1-to-Mono), e.g., getting a User ID and then calling another Service that returns `Mono<Details>`. If you return a Mono inside `map`, you get `Mono<Mono<T>>`, which is usually not what you want.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在什麼情況下你會強烈建議**不要**使用 Spring WebFlux？
**When would you strongly advise AGAINST using Spring WebFlux?**

*   **高分回答要點 (Key Points)**:
    1.  **團隊技能落差**：Reactive 的除錯與思維模式轉換成本極高，若團隊不熟悉，維護成本會大於效能紅利。
    2.  **JDBC 依賴**：若專案重度依賴 JPA/Hibernate 且無法遷移到 R2DBC，WebFlux 的優勢會被 Thread Pool 的 Context Switch 抵消。
    3.  **CPU Bound 任務**：WebFlux 適合 I/O Bound。若是影像處理或加密運算，Event Loop 會被阻塞，反而不如傳統 Thread Pool 模型。

### Q2: 請解釋 `subscribeOn` 與 `publishOn` 的區別。
**Please explain the difference between `subscribeOn` and `publishOn`.**

*   **高分回答要點 (Key Points)**:
    1.  **`subscribeOn`**: 影響**源頭（Source）**的執行緒。無論在鏈式調用的哪裡宣告，它決定了 `subscribe()` 發生的當下，資料產生的源頭在哪個執行緒執行（常用於將阻塞 I/O 移至 Elastic Scheduler）。
    2.  **`publishOn`**: 影響**後續（Downstream）**運算子的執行緒。它像是一個切換閥，之後的操作都會跑到指定的 Scheduler 上執行。

### Q3: 什麼是 Backpressure？Spring WebFlux 底層如何實現它？
**What is Backpressure? How does Spring WebFlux implement it under the hood?**

*   **高分回答要點 (Key Points)**:
    1.  Backpressure 是下游通知上游「我能處理多少資料」的機制。
    2.  在 Reactive Streams 規範中，透過 `Subscription.request(long n)` 方法實現。
    3.  Netty 層面透過 TCP 的 Window Size 進行流量控制，Reactor 層面則透過 Operator（如 `limitRate`, `onBackpressureBuffer`）來管理應用層的流速。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點 (Key Takeaways)
1.  **Event Loop is King**: WebFlux 依賴少量的執行緒處理大量併發，**絕對禁止阻塞** Event Loop。
2.  **Reactive is Lazy**: 所有的 Operator 只是建構管線，直到 `subscribe` 發生前都不會執行。
3.  **Backpressure**: 保護系統不被流量沖垮的關鍵機制，由消費者控制生產者的速度。
4.  **Mono/Flux**: `Mono` 是 0-1 (Scalar)，`Flux` 是 0-N (Vector/Stream)。
5.  **Use Case**: 適用於 Gateway、高併發聚合服務；不適用於傳統 CRUD 或 CPU 密集型應用。

### 後續延伸 (Next Steps)
*   **R2DBC**: 深入研究 Reactive Relational Database Connectivity，解決 DB 層的阻塞問題。
*   **RSocket**: 學習比 HTTP 更高效的二進位 Reactive 協定，適用於微服務內部通訊。
*   **Testing**: 使用 `StepVerifier` 撰寫 Reactive 單元測試（下一章的潛在主題）。
*   **Observability**: 研究如何在異步環境下使用 Micrometer 與 Distributed Tracing (Zipkin/Jaeger) 追蹤請求。