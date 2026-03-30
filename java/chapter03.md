## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在現代後端架構中，高併發處理能力是區分中階與資深工程師的分水嶺。對於具備 7–12 年經驗的 Java 開發者而言，僅僅知道如何建立執行緒或使用 `synchronized` 已經不夠。你需要深刻理解 JVM 層級的鎖機制、執行緒池的底層設計，以及如何根據 I/O 或 CPU 密集型場景選擇最適合的非同步模型。
In modern backend architectures, high-concurrency processing capability is the watershed that separates mid-level from senior engineers. For Java developers with 7–12 years of experience, merely knowing how to create a thread or use `synchronized` is no longer sufficient. You need a profound understanding of JVM-level lock mechanisms, the underlying design of thread pools, and how to choose the most appropriate asynchronous model based on I/O-bound or CPU-bound scenarios.

完成本章後，你將能夠：
After completing this chapter, you will be able to:

*   **精準配置執行緒池**：不再依賴 `Executors` 的預設工廠方法，而是能根據 Little's Law 與系統負載，設計具備背壓（Backpressure）與適當拒絕策略的 `ThreadPoolExecutor`。
    **Precisely tune thread pools**: Stop relying on the default factory methods of `Executors`, and instead design a `ThreadPoolExecutor` with backpressure and appropriate rejection policies based on Little's Law and system load.
*   **剖析 J.U.C 底層機制**：透徹理解 AQS (AbstractQueuedSynchronizer) 與 CAS (Compare-And-Swap)，並能在實務中正確選擇 `ReentrantLock`、`StampedLock` 或無鎖資料結構。
    **Dissect J.U.C internals**: Thoroughly understand AQS (AbstractQueuedSynchronizer) and CAS (Compare-And-Swap), and correctly choose between `ReentrantLock`, `StampedLock`, or lock-free data structures in practice.
*   **掌握現代 Java 非同步典範轉移**：從 `CompletableFuture` 的管線化設計、Reactive Programming 的響應式流，過渡到 Java 21 Project Loom（虛擬執行緒）的結構化並發（Structured Concurrency）。
    **Master modern Java async paradigm shifts**: Transition from the pipelined design of `CompletableFuture` and reactive streams of Reactive Programming, to Structured Concurrency with Java 21's Project Loom (Virtual Threads).

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 鎖機制與 AQS (Locks and AQS)
在 Java 中，處理共享狀態的心智模型可以類比為「交通管制」。`synchronized` 是 JVM 提供的隱式紅綠燈，而 `java.util.concurrent.locks` 則是開發者手動控制的交警。J.U.C 鎖的核心基石是 **AQS (AbstractQueuedSynchronizer)**。AQS 本質上是一個依賴 CAS 操作來維護狀態（`state`）的 FIFO 雙向佇列。
In Java, the mental model for handling shared state can be likened to "traffic control". `synchronized` is an implicit traffic light provided by the JVM, while `java.util.concurrent.locks` are traffic cops manually controlled by developers. The cornerstone of J.U.C locks is **AQS (AbstractQueuedSynchronizer)**. AQS is essentially a FIFO doubly-linked list that relies on CAS operations to maintain a synchronization state (`state`).

*   **ReentrantLock vs. synchronized**: 在 Java 1.6 鎖優化（偏向鎖、輕量級鎖）之後，兩者在低競爭下的效能差異不大。但 `ReentrantLock` 提供了公平鎖（Fairness）、可中斷獲取（Interruptibility）與超時機制，適合高競爭且需要精細控制的場景。
    **ReentrantLock vs. synchronized**: After Java 1.6 lock optimizations (biased locking, lightweight locking), their performance difference in low-contention scenarios is negligible. However, `ReentrantLock` provides fairness, interruptibility, and timeout mechanisms, making it suitable for high-contention scenarios requiring fine-grained control.
*   **StampedLock**: 針對讀多寫少的極端場景，`StampedLock` 提供了「樂觀讀（Optimistic Read）」。它不阻塞寫入，而是在讀取後驗證戳記（Stamp），大幅降低了讀寫鎖（`ReadWriteLock`）中的寫入飢餓（Writer Starvation）問題。
    **StampedLock**: For extreme read-heavy scenarios, `StampedLock` offers an "Optimistic Read". It does not block writes, but instead validates a stamp after reading, drastically reducing the writer starvation problem found in `ReadWriteLock`.

### 執行緒池與任務調度 (Thread Pools and Task Scheduling)
將執行緒池視為一個「工廠生產線」。核心執行緒（Core Threads）是全職員工，工作佇列（Work Queue）是待處理訂單的緩衝區，最大執行緒（Max Threads）則是臨時雇員。
Think of a thread pool as a "factory production line". Core threads are full-time employees, the work queue is the buffer for pending orders, and max threads are temporary contractors.

資深工程師的心智模型不應只是「把任務丟進去」，而是要思考：**當系統過載時，緩衝區滿了，臨時雇員也滿了，工廠該如何拒絕新訂單（Rejection Policy）？**
A senior engineer's mental model shouldn't just be "throw tasks into it", but rather: **When the system is overloaded, the buffer is full, and temporary contractors are maxed out, how should the factory reject new orders (Rejection Policy)?**

### 典範轉移：從 Callback 到 Virtual Threads (Paradigm Shift: From Callbacks to Virtual Threads)
*   **CompletableFuture**: 採用 Monadic（單子）設計，解決了 Callback Hell。心智模型是「組裝管線（Pipeline）」，資料在不同的階段中非同步流動。
    **CompletableFuture**: Adopts a Monadic design to solve Callback Hell. The mental model is "assembling a pipeline", where data flows asynchronously through different stages.
*   **Reactive Programming (Reactor/RxJava)**: 引入了「背壓（Backpressure）」概念。心智模型是「水庫與水管」，下游消費者可以告訴上游生產者放慢速度。
    **Reactive Programming (Reactor/RxJava)**: Introduces the concept of "Backpressure". The mental model is "reservoirs and pipes", where downstream consumers can tell upstream producers to slow down.
*   **Project Loom (Virtual Threads)**: Java 21 的重大革命。心智模型回歸到最簡單的「一個請求一個執行緒（Thread-per-request）」。虛擬執行緒由 JVM 調度，在遇到 I/O 阻塞時會自動讓出底層的 Carrier Thread（OS 執行緒），讓非同步程式碼寫起來就像同步程式碼一樣直覺。
    **Project Loom (Virtual Threads)**: A major revolution in Java 21. The mental model reverts to the simplest "Thread-per-request". Virtual threads are scheduled by the JVM and automatically yield the underlying Carrier Thread (OS thread) upon I/O blocking, making asynchronous code as intuitive to write as synchronous code.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在 Production 環境中，並行處理的設計直接影響系統的**可用性（Availability）**與**彈性（Resilience）**。
In a production environment, the design of concurrency directly impacts the system's **Availability** and **Resilience**.

### 艙壁模式 (Bulkhead Pattern)
在微服務架構的 API Gateway 或 BFF（Backend for Frontend）中，我們經常需要呼叫多個下游服務。如果所有呼叫共用同一個執行緒池，一個緩慢的下游服務（例如推薦系統）就會耗盡所有執行緒，導致核心服務（例如訂單系統）也無法回應。
In an API Gateway or BFF (Backend for Frontend) of a microservices architecture, we often need to call multiple downstream services. If all calls share the same thread pool, a slow downstream service (e.g., recommendation system) will exhaust all threads, causing core services (e.g., order system) to become unresponsive.
*   **設計實踐**：為不同的下游服務配置獨立的執行緒池（Thread Pool Isolation）。這就是系統設計中的艙壁模式。
    **Design Practice**: Configure independent thread pools for different downstream services (Thread Pool Isolation). This is the Bulkhead pattern in system design.

### 虛擬執行緒對架構的影響 (Impact of Virtual Threads on Architecture)
在 Project Loom 之前，為了達到高吞吐量，架構師通常會選擇 WebFlux (Netty) 等 Reactive 框架。但 Reactive 程式碼具有傳染性（Contagious），且難以除錯（Stacktrace 斷裂）。
Before Project Loom, to achieve high throughput, architects typically chose Reactive frameworks like WebFlux (Netty). However, Reactive code is contagious and hard to debug (broken stacktraces).
*   **設計實踐**：隨著 Java 21 的普及，對於單純的 I/O 密集型微服務，我們可以直接使用傳統的 Spring Boot (Tomcat) 搭配 Virtual Threads。這極大地降低了系統維護成本，同時保持了與 Reactive 相當的吞吐量。
    **Design Practice**: With the popularization of Java 21, for purely I/O-bound microservices, we can directly use traditional Spring Boot (Tomcat) with Virtual Threads. This drastically reduces system maintenance costs while maintaining throughput comparable to Reactive approaches.

---

## 4. 逐步示例
## 4. Walkthrough / Example

### 場景：BFF 聚合多個微服務資料
### Scenario: BFF Aggregating Data from Multiple Microservices

假設我們需要實作一個 `getUserDashboard` API，它必須同時獲取使用者基本資料（User Profile）、最近訂單（Recent Orders）以及推薦商品（Recommendations）。
Suppose we need to implement a `getUserDashboard` API, which must concurrently fetch the User Profile, Recent Orders, and Recommendations.

#### 方案一：使用 CompletableFuture (Java 8+)
#### Approach 1: Using CompletableFuture (Java 8+)

這是目前最常見的非同步聚合方式。我們需要自定義執行緒池以避免使用預設的 `ForkJoinPool.commonPool()`。
This is currently the most common asynchronous aggregation method. We need to customize the thread pool to avoid using the default `ForkJoinPool.commonPool()`.

```java
import java.util.concurrent.*;

public class DashboardService {
    // 1. Define a dedicated thread pool (Bulkhead pattern)
    // 1. 定義專屬執行緒池（艙壁模式）
    private final ExecutorService bffThreadPool = new ThreadPoolExecutor(
        10, 50, 60L, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(100),
        new ThreadPoolExecutor.CallerRunsPolicy() // Backpressure mechanism / 背壓機制
    );

    public DashboardResponse getUserDashboard(String userId) {
        // 2. Launch async tasks
        // 2. 發起非同步任務
        CompletableFuture<UserProfile> profileFuture = CompletableFuture.supplyAsync(
            () -> fetchUserProfile(userId), bffThreadPool);
            
        CompletableFuture<List<Order>> ordersFuture = CompletableFuture.supplyAsync(
            () -> fetchRecentOrders(userId), bffThreadPool);
            
        CompletableFuture<List<Recommendation>> recsFuture = CompletableFuture.supplyAsync(
            () -> fetchRecommendations(userId), bffThreadPool)
            .exceptionally(ex -> {
                // Fallback for non-critical data
                // 非關鍵資料的降級處理
                return Collections.emptyList(); 
            });

        // 3. Wait for all to complete and aggregate
        // 3. 等待全部完成並聚合
        return CompletableFuture.allOf(profileFuture, ordersFuture, recsFuture)
            .thenApply(v -> new DashboardResponse(
                profileFuture.join(), 
                ordersFuture.join(), 
                recsFuture.join()
            )).join();
    }
    
    // Mock methods omitted...
}
```
*   **複雜度分析 (Complexity)**: 時間複雜度為 $O(\max(T_1, T_2, T_3))$，其中 $T$ 為各個 API 的響應時間。
    **Complexity**: Time complexity is $O(\max(T_1, T_2, T_3))$, where $T$ is the response time of each API.
*   **邊界條件 (Edge Cases)**: 如果 `fetchRecommendations` 發生超時，`exceptionally` 提供了優雅降級（Graceful Degradation），確保核心資料仍能返回。
    **Edge Cases**: If `fetchRecommendations` times out, `exceptionally` provides graceful degradation, ensuring core data is still returned.

#### 方案二：使用 Project Loom 的結構化並發 (Java 21+)
#### Approach 2: Using Project Loom's Structured Concurrency (Java 21+)

使用虛擬執行緒與 `StructuredTaskScope`，程式碼回歸同步風格，且生命週期管理更加嚴謹。
Using Virtual Threads and `StructuredTaskScope`, the code reverts to a synchronous style, and lifecycle management becomes much stricter.

```java
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Subtask;

public class ModernDashboardService {

    public DashboardResponse getUserDashboard(String userId) throws InterruptedException {
        // StructuredTaskScope ensures all child threads are terminated if the scope exits
        // StructuredTaskScope 確保如果作用域退出，所有子執行緒都會被終止
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            
            // Fork virtual threads for each task
            // 為每個任務 Fork 虛擬執行緒
            Subtask<UserProfile> profileTask = scope.fork(() -> fetchUserProfile(userId));
            Subtask<List<Order>> ordersTask = scope.fork(() -> fetchRecentOrders(userId));
            Subtask<List<Recommendation>> recsTask = scope.fork(() -> {
                try {
                    return fetchRecommendations(userId);
                } catch (Exception e) {
                    return Collections.emptyList(); // Fallback / 降級
                }
            });

            // Wait for all tasks to complete or fail
            // 等待所有任務完成或失敗
            scope.join();
            // Propagate exception if any critical task failed
            // 如果有任何關鍵任務失敗，則拋出異常
            scope.throwIfFailed(); 

            // Aggregate results directly
            // 直接聚合結果
            return new DashboardResponse(
                profileTask.get(),
                ordersTask.get(),
                recsTask.get()
            );
        } catch (ExecutionException e) {
            throw new RuntimeException("Failed to fetch dashboard data", e);
        }
    }
}
```
*   **為何在實務中更好？ (Why is this better in practice?)**: 沒有 Callback，沒有複雜的 `join()` 邏輯。如果 `getUserDashboard` 被中斷，`StructuredTaskScope` 會自動取消所有尚未完成的子虛擬執行緒，完美解決了執行緒洩漏（Thread Leak）的問題。
    **Why is this better in practice?**: No callbacks, no complex `join()` logic. If `getUserDashboard` is interrupted, `StructuredTaskScope` automatically cancels all pending child virtual threads, perfectly solving thread leak issues.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 1. 濫用 `Executors` 工廠方法 (Abusing `Executors` Factory Methods)
*   **錯誤案例 (Pitfall)**: 使用 `Executors.newFixedThreadPool(10)` 或 `newCachedThreadPool()`。
    **Pitfall**: Using `Executors.newFixedThreadPool(10)` or `newCachedThreadPool()`.
*   **為何不好 (Why it's bad)**: `newFixedThreadPool` 底層使用無界佇列（`LinkedBlockingQueue`，容量為 `Integer.MAX_VALUE`）。在突發流量下，任務會無限堆積在記憶體中，最終導致 `OutOfMemoryError` (OOM)。`newCachedThreadPool` 則會無限建立執行緒，導致 CPU 資源耗盡。
    **Why it's bad**: `newFixedThreadPool` uses an unbounded queue (`LinkedBlockingQueue` with capacity `Integer.MAX_VALUE`) under the hood. During traffic spikes, tasks will queue up indefinitely in memory, eventually causing an `OutOfMemoryError` (OOM). `newCachedThreadPool` creates threads infinitely, leading to CPU exhaustion.
*   **較佳方案 (Better Alternative)**: 始終手動實例化 `ThreadPoolExecutor`，明確指定核心數、最大數、有界佇列（Bounded Queue）大小以及拒絕策略（如 `CallerRunsPolicy`）。
    **Better Alternative**: Always manually instantiate `ThreadPoolExecutor`, explicitly specifying core size, max size, bounded queue size, and a rejection policy (e.g., `CallerRunsPolicy`).

### 2. 在預設的 ForkJoinPool 中執行阻塞 I/O (Blocking I/O in Default ForkJoinPool)
*   **錯誤案例 (Pitfall)**: 在 `CompletableFuture.supplyAsync()` 中不指定執行緒池，直接執行 HTTP 請求或 DB 查詢。
    **Pitfall**: Executing HTTP requests or DB queries directly in `CompletableFuture.supplyAsync()` without specifying a custom thread pool.
*   **為何不好 (Why it's bad)**: 預設會使用 `ForkJoinPool.commonPool()`，其執行緒數等於 CPU 核心數減一。一個慢查詢就會阻塞整個 JVM 內所有共用此池的非同步任務（包含並行流 `parallelStream`）。
    **Why it's bad**: It defaults to `ForkJoinPool.commonPool()`, where the thread count equals CPU cores minus one. A single slow query will block all async tasks in the JVM sharing this pool (including `parallelStream`).
*   **較佳方案 (Better Alternative)**: 為 I/O 密集型任務提供自定義的執行緒池。
    **Better Alternative**: Provide a customized thread pool for I/O-bound tasks.

### 3. ThreadLocal 在執行緒池中的記憶體洩漏 (ThreadLocal Memory Leaks in Thread Pools)
*   **錯誤案例 (Pitfall)**: 在 Web 請求攔截器中設置 `ThreadLocal`（如 User Context），但在請求結束時忘記呼叫 `remove()`。
    **Pitfall**: Setting a `ThreadLocal` (e.g., User Context) in a web request interceptor but forgetting to call `remove()` at the end of the request.
*   **為何不好 (Why it's bad)**: 由於 Tomcat 等 Web 容器使用執行緒池，執行緒會被重複利用。上一個使用者的敏感資料可能會殘留在執行緒中，被下一個使用者讀取，造成嚴重的安全漏洞與記憶體洩漏。
    **Why it's bad**: Because web containers like Tomcat use thread pools, threads are reused. The previous user's sensitive data might remain in the thread and be read by the next user, causing severe security vulnerabilities and memory leaks.
*   **較佳方案 (Better Alternative)**: 始終在 `finally` 區塊中呼叫 `ThreadLocal.remove()`。在 Java 21 中，可考慮使用 `ScopedValue` 來替代 `ThreadLocal`。
    **Better Alternative**: Always call `ThreadLocal.remove()` in a `finally` block. In Java 21, consider using `ScopedValue` as a replacement for `ThreadLocal`.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

作為資深工程師，面試時不僅要給出答案，還要展現對底層原理與系統權衡的理解。
As a senior engineer, in interviews, you must not only provide answers but also demonstrate an understanding of underlying principles and system trade-offs.

*   **Q1: 如何決定執行緒池的大小？ (How do you determine the size of a thread pool?)**
    *   **高分回答要點**: 區分 CPU 密集型與 I/O 密集型任務。CPU 密集型通常設為 $N_{cpu} + 1$。I/O 密集型需考量阻塞時間與計算時間的比例，公式為 $N_{cpu} \times U_{cpu} \times (1 + \frac{W}{C})$（W: Wait time, C: Compute time）。接著強調，理論公式只是起點，實務上必須依賴壓力測試與動態調整（Dynamic Thread Pool Tuning）。
    *   **Key points for high score**: Distinguish between CPU-bound and I/O-bound tasks. CPU-bound is typically $N_{cpu} + 1$. I/O-bound requires considering the ratio of wait time to compute time, using the formula $N_{cpu} \times U_{cpu} \times (1 + \frac{W}{C})$. Then emphasize that theoretical formulas are just a starting point; in practice, you must rely on stress testing and Dynamic Thread Pool Tuning.

*   **Q2: 請解釋 ReentrantLock 是如何實現可重入性的？AQS 在其中扮演什麼角色？ (Explain how ReentrantLock implements reentrancy? What role does AQS play?)**
    *   **高分回答要點**: 說明 `ReentrantLock` 內部持有當前獲得鎖的執行緒參考。當同一個執行緒再次請求鎖時，只需將 AQS 的 `state` 變數加 1，釋放時減 1，直到 `state` 為 0 才真正釋放鎖。AQS 負責維護等待鎖的執行緒佇列（FIFO），並透過 CAS 確保 `state` 修改的原子性。
    *   **Key points for high score**: Explain that `ReentrantLock` internally holds a reference to the thread that currently owns the lock. When the same thread requests the lock again, it simply increments the AQS `state` variable by 1, and decrements it upon release, truly releasing the lock only when `state` reaches 0. AQS is responsible for maintaining the queue of threads waiting for the lock (FIFO) and ensuring the atomicity of `state` modifications via CAS.

*   **Q3: 在大型單體系統中，如果遇到嚴重的執行緒阻塞導致吞吐量下降，你會如何排查與解決？ (In a large monolith, if you encounter severe thread blocking causing a drop in throughput, how would you troubleshoot and resolve it?)**
    *   **高分回答要點**:
        1.  **觀測 (Observe)**: 使用 `jstack` 導出 Thread Dump，或透過 APM 工具（如 Datadog, SkyWalking）尋找處於 `BLOCKED` 或 `WAITING` 狀態的執行緒。
        2.  **定位 (Locate)**: 找出阻塞根源（如慢 SQL、外部 API 超時、分散式鎖死鎖）。
        3.  **解決 (Resolve)**: 導入超時機制、斷路器（Circuit Breaker）、艙壁模式隔離執行緒池。如果是 I/O 瓶頸，評估升級至 Java 21 使用 Virtual Threads 來提升併發處理能力。
    *   **Key points for high score**:
        1. **Observe**: Use `jstack` to export a Thread Dump, or use APM tools (like Datadog, SkyWalking) to find threads in `BLOCKED` or `WAITING` states.
        2. **Locate**: Identify the root cause (e.g., slow SQL, external API timeout, distributed lock deadlock).
        3. **Resolve**: Introduce timeout mechanisms, Circuit Breakers, and Bulkhead pattern for thread pool isolation. If it's an I/O bottleneck, evaluate upgrading to Java 21 to use Virtual Threads to boost concurrency capacity.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

**記憶錨點 (Key Takeaways):**
*   **AQS 是基石 (AQS is the cornerstone)**: 掌握 AQS 的 `state` 與 FIFO 佇列機制，就能看透 `ReentrantLock`, `Semaphore`, `CountDownLatch` 的底層邏輯。
    **AQS is the cornerstone**: Mastering AQS's `state` and FIFO queue mechanism allows you to see through the underlying logic of `ReentrantLock`, `Semaphore`, and `CountDownLatch`.
*   **拒絕預設執行緒池 (Reject default thread pools)**: 永遠自定義 `ThreadPoolExecutor`，設定有界佇列與明確的拒絕策略，防止 OOM。
    **Reject default thread pools**: Always customize `ThreadPoolExecutor`, set bounded queues and explicit rejection policies to prevent OOM.
*   **艙壁模式 (Bulkhead Pattern)**: 針對不同的外部依賴使用獨立的執行緒池，避免單點故障拖垮全局。
    **Bulkhead Pattern**: Use independent thread pools for different external dependencies to prevent a single point of failure from dragging down the whole system.
*   **CompletableFuture 避免阻塞 (CompletableFuture avoids blocking)**: 絕不在預設的 `commonPool` 中執行 I/O 阻塞操作。
    **CompletableFuture avoids blocking**: Never execute I/O blocking operations in the default `commonPool`.
*   **Loom 改變遊戲規則 (Loom changes the game)**: Java 21 的 Virtual Threads 讓「同步寫法、非同步效能」成為現實，大幅簡化了高併發 I/O 應用的開發心智負擔。
    **Loom changes the game**: Java 21's Virtual Threads make "synchronous coding, asynchronous performance" a reality, drastically simplifying the cognitive load of developing high-concurrency I/O applications.

**後續延伸 (Next Steps):**
*   **JVM 效能調優 (JVM Performance Tuning)**: 高併發必然伴隨高頻率的物件創建。下一步應深入理解 Garbage Collection (G1, ZGC) 如何影響延遲，這將在後續的 JVM 章節探討。
    **JVM Performance Tuning**: High concurrency inevitably comes with high-frequency object creation. The next step is to deeply understand how Garbage Collection (G1, ZGC) impacts latency, which will be explored in subsequent JVM chapters.
*   **分散式並行控制 (Distributed Concurrency Control)**: 當系統從單體走向微服務，單機的 `ReentrantLock` 將不再適用。可以延伸學習基於 Redis (Redisson) 或 ZooKeeper 的分散式鎖設計。
    **Distributed Concurrency Control**: As systems move from monoliths to microservices, single-node `ReentrantLock` will no longer apply. Extend your learning to distributed lock designs based on Redis (Redisson) or ZooKeeper.