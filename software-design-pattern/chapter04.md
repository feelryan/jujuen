# Chapter 04: Concurrency and Multithreading Patterns
# 第四章：併發與多執行緒模式

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For Senior Engineers, concurrency is no longer just about using `synchronized` keywords or `locks`. It is about architectural patterns that decouple execution from invocation, manage resources efficiently, and ensure system stability under high load. This chapter focuses on patterns that solve structural concurrency problems.
對於資深工程師而言，併發（Concurrency）不再僅僅是使用 `synchronized` 關鍵字或 `locks`。重點在於如何透過架構模式將「執行」與「呼叫」解耦、有效管理資源，並確保系統在高負載下的穩定性。本章專注於解決結構性併發問題的模式。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Master Decoupling Patterns**: Effectively use **Producer-Consumer** and **Active Object** patterns to separate task submission from execution, enabling better flow control and error handling.
    **掌握解耦模式**：有效運用 **Producer-Consumer** 與 **Active Object** 模式將任務提交與執行分離，實現更好的流量控制與錯誤處理。
2.  **Optimize Resource Management**: Understand the internal mechanics of **Thread Pools** to avoid resource exhaustion (OOM) and excessive context switching.
    **優化資源管理**：理解 **Thread Pool** 的內部機制，避免資源耗盡（OOM）與過度的上下文切換（Context Switching）。
3.  **Handle Asynchronous Results**: Leverage **Future/Promise** patterns to compose complex asynchronous workflows without falling into "callback hell."
    **處理非同步結果**：利用 **Future/Promise** 模式來組合複雜的非同步工作流，避免陷入「回呼地獄（Callback Hell）」。
4.  **Design for Thread Safety**: Apply patterns that minimize shared mutable state, reducing the risk of **Race Conditions** and **Deadlocks**.
    **設計執行緒安全**：應用能最小化「共享可變狀態」的模式，降低 **Race Conditions** 與 **Deadlocks** 的風險。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The "Restaurant Kitchen" Analogy
### 「餐廳廚房」類比

To visualize these patterns, imagine a busy high-end restaurant kitchen:
為了具象化這些模式，想像一個繁忙的高級餐廳廚房：

*   **Producer-Consumer**: The Waiters (Producers) place orders on a ticket rail (Queue). The Chefs (Consumers) pick up tickets and cook. The Waiters don't wait in the kitchen; they go back to customers.
    **Producer-Consumer**：服務生（Producers）將點單放在掛單軌（Queue）上。廚師（Consumers）取單並烹飪。服務生不會在廚房空等，而是回到顧客身邊。
*   **Thread Pool**: You have a fixed brigade of 5 Chefs. Regardless of how many orders come in, you don't hire more chefs on the spot (which would cause overcrowding/thrashing). Orders just queue up.
    **Thread Pool**：你有一組固定的 5 位廚師團隊。無論進來多少訂單，你不會當場僱用更多廚師（這會導致擁擠/效能抖動）。訂單只會排隊。
*   **Future/Promise**: When a customer orders a special dish that takes time, the waiter gives them a buzzer. The customer can drink wine (do other work) until the buzzer rings (result is ready).
    **Future/Promise**：當顧客點了一道費時的特製菜，服務生給他們一個取餐呼叫器。顧客可以先喝紅酒（做其他事），直到呼叫器響起（結果準備好了）。
*   **Active Object**: The Head Chef has their own private station. They accept requests via a personal assistant (Proxy) who puts them in a list. The Head Chef processes them one by one strictly sequentially. No one else touches the Head Chef's ingredients (State), guaranteeing safety without shouting "Stop!" (Locks).
    **Active Object**：主廚有自己的私人料理台。他透過私人助理（Proxy）接收請求並放入清單。主廚嚴格地依序逐一處理。沒有人能觸碰主廚的食材（State），這保證了安全性且無需大喊「停！」（Locks）。

### Key Definitions & Distinctions
### 關鍵定義與區別

*   **Concurrency vs. Parallelism**: Concurrency is about dealing with lots of things at once (structure); Parallelism is about doing lots of things at once (execution). These patterns help structure concurrency so parallelism can be exploited safely.
    **併發 vs. 平行**：併發是關於同時「處理」多件事（結構）；平行是關於同時「做」多件事（執行）。這些模式協助建構併發結構，以便安全地利用平行運算。
*   **Blocking vs. Non-blocking**:
    *   **Blocking**: The caller waits until the task is done (e.g., simple function call).
    *   **Non-blocking**: The caller returns immediately, often receiving a `Future` or registering a callback.
    **阻塞 vs. 非阻塞**：
    *   **阻塞**：呼叫者等待直到任務完成（如簡單的函式呼叫）。
    *   **非阻塞**：呼叫者立即返回，通常會收到一個 `Future` 或註冊一個 callback。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In production systems, these patterns are the backbone of scalability and resilience.
在生產環境系統中，這些模式是擴展性與韌性的骨幹。

### 1. Message Queues & Event Streaming (Producer-Consumer)
### 1. 訊息佇列與事件串流 (Producer-Consumer)
*   **Context**: Systems like Kafka, RabbitMQ, or AWS SQS are essentially distributed implementations of the Producer-Consumer pattern.
*   **Design View**: It decouples the rate of production (traffic spikes) from consumption (worker processing speed). It provides **Backpressure** handling—if the queue fills up, producers must slow down or drop requests, preventing the consumers from crashing.
*   **情境**：像 Kafka、RabbitMQ 或 AWS SQS 這些系統，本質上就是 Producer-Consumer 模式的分散式實作。
*   **設計視角**：它將生產速率（流量尖峰）與消費速率（Worker 處理速度）解耦。它提供了 **背壓（Backpressure）** 處理——如果佇列滿了，生產者必須減速或丟棄請求，防止消費者崩潰。

### 2. Web Servers & Application Containers (Thread Pool)
### 2. Web 伺服器與應用程式容器 (Thread Pool)
*   **Context**: Tomcat, Jetty, or gRPC servers use thread pools to handle incoming HTTP requests.
*   **Design View**: Instead of `new Thread()` per request (which risks OS thread limits and high memory usage), a bounded pool reuses threads. This acts as a **Bulkhead** pattern; if the pool is exhausted, new requests are queued or rejected fast, protecting the server from OOM.
*   **情境**：Tomcat、Jetty 或 gRPC 伺服器使用執行緒池來處理傳入的 HTTP 請求。
*   **設計視角**：與其對每個請求執行 `new Thread()`（這有觸發 OS 執行緒限制與高記憶體使用量的風險），有界限的池（Bounded Pool）能重複使用執行緒。這充當了 **艙壁（Bulkhead）** 模式；如果池耗盡，新請求會被排隊或快速拒絕，保護伺服器免於 OOM。

### 3. Asynchronous APIs & Microservices Aggregation (Future/Promise)
### 3. 非同步 API 與微服務聚合 (Future/Promise)
*   **Context**: An API Gateway calling 3 downstream services (User, Order, Inventory) simultaneously.
*   **Design View**: Using Futures (e.g., `CompletableFuture` in Java, `Promise` in JS), the gateway triggers all 3 calls in parallel and waits for `allOrAny`. This reduces total latency from `Sum(T1, T2, T3)` to `Max(T1, T2, T3)`.
*   **情境**：一個 API Gateway 同時呼叫 3 個下游服務（使用者、訂單、庫存）。
*   **設計視角**：使用 Futures（例如 Java 的 `CompletableFuture`，JS 的 `Promise`），Gateway 平行觸發所有 3 個呼叫並等待 `allOrAny`。這將總延遲從 `Sum(T1, T2, T3)` 降低到 `Max(T1, T2, T3)`。

---

## 4. Walkthrough: The Active Object Pattern
## 4. 逐步示例：Active Object 模式

### Problem Context
### 問題背景
Imagine a legacy logging component or a hardware driver that is **not thread-safe**. Multiple threads in your web application need to write logs/commands to it.
想像一個遺留的日誌組件或硬體驅動程式，它**不是執行緒安全的**。你的 Web 應用程式中有多個執行緒需要對其寫入日誌或指令。

*   **Naive Approach**: Add `synchronized` to every method.
    *   *Issue*: High contention. Threads block each other, reducing throughput significantly.
*   **naive 作法**：在每個方法上加上 `synchronized`。
    *   *問題*：高度競爭。執行緒互相阻塞，顯著降低吞吐量。

### Solution: Active Object
### 解法：Active Object
We convert the method calls into **messages** (objects), put them in a queue, and have a single dedicated thread process them. The client gets a `Future` representing the pending result.
我們將方法呼叫轉換為 **訊息**（物件），放入佇列，並由單一專屬執行緒來處理它們。客戶端會得到一個代表待定結果的 `Future`。

### Implementation Structure (Java-like Concept)
### 實作結構（類 Java 概念）

1.  **Proxy**: Exposed to clients, looks like a normal object.
2.  **MethodRequest**: Encapsulates the method call, arguments, and the Future.
3.  **Scheduler/Queue**: Holds the requests.
4.  **Servant**: The actual worker (running on its own thread).

```java
// 1. The Interface (What clients see)
interface ImageProcessor {
    Future<String> processImage(String path);
}

// 2. The Active Object Implementation
class ActiveImageProcessor implements ImageProcessor {
    private final BlockingQueue<Runnable> dispatchQueue = new LinkedBlockingQueue<>();
    
    public ActiveImageProcessor() {
        // The "Servant" Thread
        new Thread(() -> {
            while (true) {
                try {
                    dispatchQueue.take().run();
                } catch (InterruptedException e) { break; }
            }
        }).start();
    }

    // Proxy Method
    @Override
    public Future<String> processImage(String path) {
        CompletableFuture<String> future = new CompletableFuture<>();
        
        // Encapsulate call into an object (Command/MethodRequest)
        dispatchQueue.offer(() -> {
            try {
                // Actual heavy logic (The Servant logic)
                String result = heavyProcessing(path); 
                future.complete(result);
            } catch (Exception e) {
                future.completeExceptionally(e);
            }
        });
        
        return future; // Return immediately (Non-blocking)
    }

    private String heavyProcessing(String path) {
        // Simulating complex, non-thread-safe logic
        return "Processed: " + path;
    }
}
```

### Why this works?
### 為何這有效？
*   **Serialization**: The `heavyProcessing` logic is guaranteed to run sequentially. No locks needed inside `heavyProcessing`.
*   **Non-blocking Clients**: Clients submit requests and move on.
*   **Complexity**: Space complexity is O(N) where N is the queue size. Time complexity depends on the processing speed vs. arrival rate.
*   **序列化**：`heavyProcessing` 邏輯保證依序執行。`heavyProcessing` 內部不需要鎖。
*   **非阻塞客戶端**：客戶端提交請求後即可繼續執行。
*   **複雜度**：空間複雜度為 O(N)，N 為佇列大小。時間複雜度取決於處理速度與到達速率的對比。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. Unbounded Thread Pools (CachedThreadPool)
### 1. 無界限執行緒池 (CachedThreadPool)
*   **Anti-pattern**: Using `Executors.newCachedThreadPool()` in a high-load service.
*   **Why**: It creates a new thread for every task if no thread is idle. Under a spike, this can spawn thousands of threads, leading to **Thrashing** (excessive context switching) and eventually `OutOfMemoryError`.
*   **Solution**: Use `FixedThreadPool` or strictly configure `ThreadPoolExecutor` with a bounded queue and a rejection policy.
*   **反模式**：在高負載服務中使用 `Executors.newCachedThreadPool()`。
*   **原因**：如果沒有閒置執行緒，它會為每個任務建立新執行緒。在流量尖峰下，這可能產生數千個執行緒，導致 **Thrashing**（過度上下文切換），最終引發 `OutOfMemoryError`。
*   **解法**：使用 `FixedThreadPool` 或嚴格配置帶有界限佇列與拒絕策略的 `ThreadPoolExecutor`。

### 2. Swallow InterruptedException
### 2. 吞掉 InterruptedException
*   **Anti-pattern**: Catching `InterruptedException` and doing nothing (or just logging it).
*   **Why**: This breaks the thread lifecycle management. The upper-level control (like a shutdown hook) cannot stop the thread gracefully.
*   **Solution**: Either re-throw it or set the interrupt flag again (`Thread.currentThread().interrupt()`).
*   **反模式**：捕捉 `InterruptedException` 卻什麼都不做（或只記錄 log）。
*   **原因**：這破壞了執行緒生命週期管理。上層控制（如關機鉤子）無法優雅地停止該執行緒。
*   **解法**：重新拋出該異常，或再次設定中斷標記（`Thread.currentThread().interrupt()`）。

### 3. Deadlock by Nested Locks
### 3. 巢狀鎖導致的死結
*   **Anti-pattern**: Acquiring Lock A, then trying to acquire Lock B inside, while another thread holds B and tries to acquire A.
*   **Why**: Circular dependency causes the application to hang indefinitely.
*   **Solution**:
    *   Always acquire locks in a consistent global order.
    *   Use `tryLock` with timeouts.
    *   Prefer higher-level concurrency utilities (like `ConcurrentHashMap` or `BlockingQueue`) over manual locking.
*   **反模式**：取得鎖 A，然後在內部試圖取得鎖 B，而另一個執行緒持有 B 並試圖取得 A。
*   **原因**：循環依賴導致應用程式無限期卡住。
*   **解法**：
    *   總是依照一致的全域順序取得鎖。
    *   使用帶有超時機制的 `tryLock`。
    *   優先使用高階併發工具（如 `ConcurrentHashMap` 或 `BlockingQueue`）而非手動鎖。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you implement a Producer-Consumer pattern with backpressure in a single JVM?
### Q1: 你如何在單一 JVM 內實作帶有背壓（Backpressure）的 Producer-Consumer 模式？
*   **Key Points**:
    *   Use a **Bounded Blocking Queue** (e.g., `ArrayBlockingQueue`).
    *   Explain `put()` (blocks if full) vs `offer()` (returns false/throws).
    *   Discuss handling the "Queue Full" scenario: Block the producer (natural backpressure), drop the message, or throw an exception.
*   **高分要點**：
    *   使用 **有界阻塞佇列**（如 `ArrayBlockingQueue`）。
    *   解釋 `put()`（滿時阻塞）與 `offer()`（回傳 false/拋出異常）的差異。
    *   討論處理「佇列已滿」的情境：阻塞生產者（自然背壓）、丟棄訊息，或拋出異常。

### Q2: Why is `ThreadLocal` considered a double-edged sword?
### Q2: 為什麼 `ThreadLocal` 被視為雙面刃？
*   **Key Points**:
    *   **Pro**: Provides thread confinement, useful for passing context (User ID, Transaction ID) without polluting method signatures.
    *   **Con**: In Thread Pools, threads are reused. If `ThreadLocal` is not cleaned up (`remove()`), the next request on the same thread might read stale data (Data Leakage) or cause Memory Leaks (since the value is strongly referenced by the thread).
*   **高分要點**：
    *   **優點**：提供執行緒封閉性，適合傳遞上下文（User ID, Transaction ID）而不污染方法簽名。
    *   **缺點**：在 Thread Pool 中，執行緒會被重複使用。若未清除 `ThreadLocal`（`remove()`），同一執行緒上的下一個請求可能會讀到舊資料（資料洩漏）或導致記憶體洩漏（因為數值被執行緒強引用）。

### Q3: How do you debug a "Race Condition" that only happens in production?
### Q3: 你如何除錯一個只在生產環境發生的 "Race Condition"？
*   **Key Points**:
    *   Acknowledge that reproducing it locally is hard.
    *   **Logs/Metrics**: Check for invariants violation logs.
    *   **Code Review**: Look for shared mutable state not guarded by locks or atomic references.
    *   **Tools**: Mention tools like Java Flight Recorder or static analysis tools (FindBugs/SpotBugs).
    *   **Fix**: Move towards immutable objects or atomic classes (`AtomicInteger`) instead of complex locking.
*   **高分要點**：
    *   承認在本地重現很困難。
    *   **Logs/Metrics**：檢查違反不變性（invariants）的日誌。
    *   **Code Review**：尋找未被鎖或原子引用保護的共享可變狀態。
    *   **工具**：提及 Java Flight Recorder 或靜態分析工具（FindBugs/SpotBugs）。
    *   **修復**：轉向不可變物件（Immutable Objects）或原子類別（`AtomicInteger`），而非複雜的鎖。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary (記憶錨點)
### 小結 (記憶錨點)
1.  **Decouple with Queues**: Use Producer-Consumer to separate work submission from processing.
    **用佇列解耦**：使用 Producer-Consumer 將工作提交與處理分離。
2.  **Bound Resources**: Always use bounded Thread Pools and Queues to prevent OOM.
    **限制資源**：總是使用有界限的 Thread Pools 與 Queues 以防止 OOM。
3.  **Active Object**: A powerful pattern to serialize access to non-thread-safe resources without explicit locking in business logic.
    **Active Object**：一個強大的模式，無需在商業邏輯中顯式加鎖，即可序列化對非執行緒安全資源的存取。
4.  **Async Composition**: Use Futures/Promises to handle latency and dependencies efficiently.
    **非同步組合**：使用 Futures/Promises 有效處理延遲與依賴關係。
5.  **Immutability**: The best synchronization is no synchronization. Prefer immutable state.
    **不可變性**：最好的同步就是不需要同步。優先使用不可變狀態。

### Next Steps
### 後續延伸
*   **Study**: **Reactor Pattern** and **Event Loop** (Chapter 05 context). Understanding how Node.js or Netty handles concurrency with a single thread.
    **研讀**：**Reactor Pattern** 與 **Event Loop**（第五章範疇）。理解 Node.js 或 Netty 如何用單執行緒處理併發。
*   **Practice**: Implement a simple "Rate Limiter" using the Token Bucket algorithm (a variation of Producer-Consumer).
    **實作**：使用 Token Bucket 演算法（Producer-Consumer 的變體）實作一個簡單的「速率限制器（Rate Limiter）」。
*   **Deep Dive**: Read about "Java Memory Model (JMM)" or the equivalent in your primary language to understand `volatile` and visibility guarantees.
    **深入**：閱讀「Java Memory Model (JMM)」或你主要語言的對應概念，理解 `volatile` 與可見性保證。