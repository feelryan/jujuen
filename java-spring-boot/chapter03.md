# Chapter 03: 進階併發程式設計與虛擬執行緒
# Chapter 03: Advanced Concurrency & Virtual Threads (Project Loom)

## 1. 前言與學習目標
## 1. Introduction & Learning Goals

對於資深工程師而言，併發（Concurrency）不再只是 `synchronized` 或 `Thread` 的基本操作，而是關於如何榨乾 CPU 效能、降低 I/O 等待成本以及維持系統穩定性的核心能力。隨著 Java 21 正式引入虛擬執行緒（Virtual Threads, Project Loom），Java 的併發模型迎來了自 Java 5 (`java.util.concurrent`) 以來最大的變革。

For senior engineers, concurrency is no longer just about basic `synchronized` blocks or `Thread` usage; it is a core competency for maximizing CPU efficiency, minimizing I/O wait costs, and maintaining system stability. With the official introduction of Virtual Threads (Project Loom) in Java 21, Java's concurrency model has undergone its most significant transformation since Java 5 (`java.util.concurrent`).

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深入理解 Java Memory Model (JMM)**：準確解釋 `volatile`、Happens-Before 原則，以及它們如何影響無鎖（Lock-Free）演算法的正確性。
    **Deeply understand the Java Memory Model (JMM):** Accurately explain `volatile`, the Happens-Before principle, and how they affect the correctness of Lock-Free algorithms.
2.  **掌握非同步編排（Async Orchestration）**：熟練使用 `CompletableFuture` 處理複雜的非同步任務依賴與異常處理，並理解其與 Reactive Programming 的取捨。
    **Master Async Orchestration:** Proficiently use `CompletableFuture` to handle complex asynchronous task dependencies and exception handling, and understand the trade-offs with Reactive Programming.
3.  **應用虛擬執行緒（Virtual Threads）**：在 Spring Boot 3.2+ 中正確啟用並調校虛擬執行緒，理解其底層原理（Carrier Threads）以及如何避免 "Pinning" 問題。
    **Apply Virtual Threads:** Correctly enable and tune Virtual Threads in Spring Boot 3.2+, understanding the underlying mechanics (Carrier Threads) and how to avoid the "Pinning" issue.
4.  **評估併發模型的選擇**：在系統設計面試中，能夠針對高吞吐量場景，比較 Thread-per-Request、Asynchronous/Reactive 與 Virtual Threads 的優劣。
    **Evaluate Concurrency Models:** In system design interviews, be able to compare the pros and cons of Thread-per-Request, Asynchronous/Reactive, and Virtual Threads for high-throughput scenarios.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 Java Memory Model (JMM) 與 Happens-Before
### 2.1 Java Memory Model (JMM) & Happens-Before

**直覺類比 (Analogy):**
想像 CPU 的 L1/L2 快取是分散式系統中的「本地節點」，而主記憶體（RAM）是「中央資料庫」。如果沒有適當的同步協定（如 `volatile` 或鎖），本地節點的寫入可能不會立即同步到中央資料庫，或者其他節點讀取到的是過期資料。JMM 就是定義這些同步規則的協定。

**Intuitive Analogy:**
Imagine CPU L1/L2 caches as "local nodes" in a distributed system, and main memory (RAM) as the "central database." Without proper synchronization protocols (like `volatile` or locks), writes from a local node might not sync immediately to the central database, or other nodes might read stale data. The JMM is the protocol defining these synchronization rules.

**關鍵定義 (Key Definition):**
JMM 定義了執行緒與主記憶體之間的抽象關係。核心概念是 **Happens-Before** 關係：如果操作 A happens-before 操作 B，則 A 的結果對 B 可見。
*   **Volatile**: 寫入 `volatile` 變數 happens-before 後續對該變數的讀取（保證可見性，禁止指令重排）。
*   **Monitor Lock**: 解鎖（unlock） happens-before 同一個鎖的加鎖（lock）。

**Key Definition:**
The JMM defines the abstract relationship between threads and main memory. The core concept is the **Happens-Before** relationship: if action A happens-before action B, then the result of A is visible to B.
*   **Volatile**: A write to a `volatile` variable happens-before subsequent reads of that variable (guarantees visibility, prevents instruction reordering).
*   **Monitor Lock**: An unlock on a monitor happens-before every subsequent lock on that monitor.

### 2.2 Platform Threads vs. Virtual Threads
### 2.2 Platform Threads vs. Virtual Threads

**心智模型 (Mental Model):**

*   **Platform Threads (OS Threads):** 就像是「專車接送」。每個 Java 執行緒直接對應一個作業系統核心執行緒（1:1）。創建昂貴，數量受限（通常數千個），Context Switch 開銷大。
*   **Virtual Threads (Project Loom):** 就像是「共享叫車（Uber Pool）」。大量的虛擬執行緒（M）共享少量的平台執行緒（N，稱為 Carrier Threads）。當虛擬執行緒執行 Blocking I/O 時，它會被掛起（unmounted），Carrier Thread 則立即去執行其他虛擬執行緒。

**Mental Model:**

*   **Platform Threads (OS Threads):** Like a "private chauffeur." Each Java thread maps directly to an OS kernel thread (1:1). Expensive to create, limited in number (usually thousands), and high context switch overhead.
*   **Virtual Threads (Project Loom):** Like a "ride-share (Uber Pool)." A massive number of virtual threads (M) share a small number of platform threads (N, called Carrier Threads). When a virtual thread performs Blocking I/O, it is unmounted, and the Carrier Thread immediately moves to execute another virtual thread.

**差異對照 (Comparison):**

| Feature | Platform Threads | Virtual Threads |
| :--- | :--- | :--- |
| **Mapping** | 1:1 with OS Threads | M:N (Many to few OS Threads) |
| **Cost** | ~1MB stack, slow startup | ~Bytes/KB stack, instant startup |
| **Blocking Cost** | Blocks the OS thread | Unmounts from Carrier (OS thread stays busy) |
| **Use Case** | CPU-bound tasks, Long-lived | I/O-bound tasks, High-concurrency "Thread-per-request" |

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 高併發 I/O 密集型服務 (High Concurrency I/O Bound Services)
### 3.1 High Concurrency I/O Bound Services

在微服務架構中，API Gateway 或 Aggregator Service 通常需要同時呼叫多個下游服務。

In a microservices architecture, an API Gateway or Aggregator Service often needs to call multiple downstream services simultaneously.

*   **傳統做法 (Traditional Approach):** 使用執行緒池（Thread Pool）。但若下游回應慢，執行緒池很快會耗盡（Thread Starvation），導致整個服務不可用。
*   **Reactive 做法 (WebFlux/Netty):** 使用非阻塞 I/O。效能極高，但程式碼複雜（Callback Hell 或 Operator Chain），除錯困難（Stack trace 不連續）。
*   **Virtual Threads 做法:** 回歸 **"Thread-per-Request"** 模型。程式碼寫起來像同步（Blocking），但底層是非阻塞。既保留了可讀性，又獲得了 Reactive 的吞吐量。

*   **Traditional Approach:** Use a Thread Pool. However, if downstream services are slow, the pool is quickly exhausted (Thread Starvation), rendering the entire service unavailable.
*   **Reactive Approach (WebFlux/Netty):** Use non-blocking I/O. Extremely high performance, but complex code (Callback Hell or Operator Chains) and difficult debugging (disjointed stack traces).
*   **Virtual Threads Approach:** Return to the **"Thread-per-Request"** model. Code is written in a synchronous (blocking) style, but it is non-blocking under the hood. This retains readability while achieving Reactive-level throughput.

### 3.2 對可觀測性與除錯的影響
### 3.2 Impact on Observability & Debugging

*   **Traceability:** Virtual Threads 讓 Stack Trace 恢復完整且有意義，這對 SRE 和開發者排查問題至關重要。
*   **Profiling:** 傳統的 CPU Profiler 可能還未完全適應數百萬個執行緒的視圖，需要使用支援 Java 21+ 的工具（如 JFR - Java Flight Recorder）。

*   **Traceability:** Virtual Threads restore complete and meaningful stack traces, which is crucial for SREs and developers troubleshooting issues.
*   **Profiling:** Traditional CPU profilers might not yet be fully adapted to visualize millions of threads; tools supporting Java 21+ (like JFR - Java Flight Recorder) are required.

---

## 4. 逐步示例：從 CompletableFuture 到 Virtual Threads
## 4. Walkthrough / Example: From CompletableFuture to Virtual Threads

### 背景 (Context)
我們需要實作一個 `ProductAggregator`，從三個不同的微服務獲取資料：
1.  `ProductInfo` (50ms)
2.  `Pricing` (30ms)
3.  `Inventory` (80ms)

We need to implement a `ProductAggregator` that fetches data from three different microservices:
1.  `ProductInfo` (50ms)
2.  `Pricing` (30ms)
3.  `Inventory` (80ms)

### 方案 A: CompletableFuture (Java 8+)
### Solution A: CompletableFuture (Java 8+)

這是 Java 8 到 Java 17 之間的標準高效做法。

This is the standard high-performance approach between Java 8 and Java 17.

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AsyncAggregator {
    // Custom Thread Pool is mandatory for Platform Threads to avoid starvation
    private final ExecutorService executor = Executors.newFixedThreadPool(200);

    public ProductDTO aggregate(String productId) {
        var infoFuture = CompletableFuture.supplyAsync(() -> fetchInfo(productId), executor);
        var priceFuture = CompletableFuture.supplyAsync(() -> fetchPrice(productId), executor);
        var stockFuture = CompletableFuture.supplyAsync(() -> fetchStock(productId), executor);

        // Combine all
        return CompletableFuture.allOf(infoFuture, priceFuture, stockFuture)
                .thenApply(v -> new ProductDTO(
                        infoFuture.join(),
                        priceFuture.join(),
                        stockFuture.join()
                ))
                .join(); // Blocking here, but main thread waits for async tasks
    }
    
    // Mock methods...
}
```

**缺點 (Drawbacks):**
*   需要管理 `ExecutorService` 大小。
*   鏈式調用（Chaining）在處理複雜邏輯（如：如果 Price 失敗則使用預設值，但如果 Inventory 失敗則拋出異常）時會變得很髒。

**Drawbacks:**
*   Requires managing `ExecutorService` size.
*   Chaining becomes messy with complex logic (e.g., if Price fails use default, but if Inventory fails throw exception).

### 方案 B: Virtual Threads (Java 21+ / Spring Boot 3.2+)
### Solution B: Virtual Threads (Java 21+ / Spring Boot 3.2+)

在 Spring Boot 3.2 中，只需在 `application.properties` 設定 `spring.threads.virtual.enabled=true`，Tomcat 就會使用虛擬執行緒處理請求。但在手動併發控制時，我們使用 `Structured Concurrency` (Preview) 或 `Executors.newVirtualThreadPerTaskExecutor()`。

In Spring Boot 3.2, simply setting `spring.threads.virtual.enabled=true` in `application.properties` makes Tomcat use virtual threads for requests. However, for manual concurrency control, we use `Structured Concurrency` (Preview) or `Executors.newVirtualThreadPerTaskExecutor()`.

```java
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class VirtualThreadAggregator {

    // No need to pool Virtual Threads. Create a new executor per request or use a shared one that spawns new threads.
    // Note: In Java 21, this executor creates a new virtual thread for every task.
    private final ExecutorService vExecutor = Executors.newVirtualThreadPerTaskExecutor();

    public ProductDTO aggregate(String productId) {
        try (var scope = new java.util.concurrent.StructuredTaskScope.ShutdownOnFailure()) {
            // Java 21 Preview Feature: Structured Concurrency
            // If not enabled, use vExecutor.submit() and standard Future.get()
            
            var infoTask = scope.fork(() -> fetchInfo(productId));
            var priceTask = scope.fork(() -> fetchPrice(productId));
            var stockTask = scope.fork(() -> fetchStock(productId));

            scope.join();           // Wait for all
            scope.throwIfFailed();  // Propagate exception if any failed

            return new ProductDTO(infoTask.get(), priceTask.get(), stockTask.get());
        } catch (Exception e) {
            throw new RuntimeException("Aggregation failed", e);
        }
    }
}
```

**優勢 (Advantages):**
*   **Imperative Style:** 寫起來像同步程式碼，邏輯清晰。
*   **No Pooling:** 不需要猜測 Thread Pool 大小。
*   **Cheap Blocking:** `scope.join()` 不會阻塞 OS 執行緒。

**Advantages:**
*   **Imperative Style:** Written like synchronous code, logic is clear.
*   **No Pooling:** No need to guess Thread Pool size.
*   **Cheap Blocking:** `scope.join()` does not block the OS thread.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 虛擬執行緒釘選 (Virtual Thread Pinning)
### 5.1 Virtual Thread Pinning

**錯誤描述 (Error Description):**
當虛擬執行緒在執行 `synchronized` 區塊或呼叫 Native Method (JNI) 時，它會被 "Pin" 在 Carrier Thread 上。如果在 `synchronized` 區塊內進行 Blocking I/O，就會連同 Carrier Thread 一起阻塞，導致吞吐量急劇下降。

**Error Description:**
When a virtual thread executes a `synchronized` block or calls a Native Method (JNI), it gets "pinned" to the Carrier Thread. If Blocking I/O is performed inside a `synchronized` block, the Carrier Thread is also blocked, causing throughput to plummet.

**解決方案 (Solution):**
*   將 `synchronized` 替換為 `ReentrantLock`。`ReentrantLock` 允許虛擬執行緒在等待鎖時卸載（Unmount）。
*   使用 `-Djdk.tracePinnedThreads=short` 參數來檢測 Pinning。

**Solution:**
*   Replace `synchronized` with `ReentrantLock`. `ReentrantLock` allows the virtual thread to unmount while waiting for the lock.
*   Use the `-Djdk.tracePinnedThreads=short` flag to detect Pinning.

### 5.2 池化虛擬執行緒 (Pooling Virtual Threads)
### 5.2 Pooling Virtual Threads

**錯誤描述 (Error Description):**
習慣性地使用 `Executors.newFixedThreadPool(10)` 來管理虛擬執行緒。

**Error Description:**
Habitually using `Executors.newFixedThreadPool(10)` to manage virtual threads.

**為何不好 (Why it's bad):**
虛擬執行緒的設計初衷是「用完即丟」（Disposable）。池化它們不僅沒有好處，反而增加了管理的開銷。永遠使用 `newVirtualThreadPerTaskExecutor` 或直接 `Thread.startVirtualThread`。

**Why it's bad:**
Virtual threads are designed to be "disposable." Pooling them provides no benefit and adds management overhead. Always use `newVirtualThreadPerTaskExecutor` or `Thread.startVirtualThread` directly.

### 5.3 在 ThreadLocal 中存儲大量數據
### 5.3 Storing Large Data in ThreadLocal

**錯誤描述 (Error Description):**
在 Thread-per-Request 模型中，習慣在 `ThreadLocal` 放很多 Context 物件。

**Error Description:**
In the Thread-per-Request model, habitually putting many Context objects into `ThreadLocal`.

**為何不好 (Why it's bad):**
當執行緒數量從 200 暴增到 100,000 時，每個執行緒攜帶的大型 `ThreadLocal` Map 會導致 Heap Memory 爆炸（Memory Bloat）。Java 21 引入了 `ScopedValues` (Preview) 作為更輕量的替代方案。

**Why it's bad:**
When the thread count explodes from 200 to 100,000, large `ThreadLocal` maps carried by each thread will cause Heap Memory explosion (Memory Bloat). Java 21 introduces `ScopedValues` (Preview) as a lighter alternative.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 既然有了 Virtual Threads，我們還需要 Reactive Programming (如 Spring WebFlux) 嗎？
### Q1: Now that we have Virtual Threads, do we still need Reactive Programming (e.g., Spring WebFlux)?

**高分回答要點 (Key Points for a High Score):**
*   **大部分情況不需要：** 對於典型的 CRUD 和微服務聚合，Virtual Threads 提供了 Reactive 的吞吐量但保留了同步程式碼的簡單性，是更好的選擇。
*   **特定場景仍需要：** 如果涉及複雜的資料流處理（Streaming）、Backpressure（背壓）控制，Reactive Streams (Project Reactor) 的 Operator 仍然非常強大且適用。Virtual Threads 解決的是 I/O Blocking，不是資料流邏輯。

**Key Points for a High Score:**
*   **Mostly No:** For typical CRUD and microservice aggregation, Virtual Threads offer Reactive throughput with the simplicity of synchronous code, making them the better choice.
*   **Specific Cases Yes:** If complex data streaming or Backpressure control is involved, Reactive Streams (Project Reactor) operators are still very powerful and applicable. Virtual Threads solve I/O blocking, not data flow logic.

### Q2: 請解釋 Double-Checked Locking Singleton 為何需要 `volatile`？
### Q2: Please explain why Double-Checked Locking Singleton requires `volatile`?

**高分回答要點 (Key Points for a High Score):**
*   **指令重排 (Instruction Reordering):** `instance = new Singleton()` 不是原子操作。它分為三步：1. 分配記憶體，2. 初始化物件，3. 將 reference 指向記憶體。
*   **問題：** 如果沒有 `volatile`，CPU 可能重排為 1 -> 3 -> 2。另一個執行緒可能在步驟 3 完成但步驟 2 未完成時，拿到一個非 null 但未初始化的物件，導致崩潰。
*   **Volatile 作用：** 禁止這種重排，確保初始化完成 happens-before reference 被賦值。

**Key Points for a High Score:**
*   **Instruction Reordering:** `instance = new Singleton()` is not atomic. It involves three steps: 1. Allocate memory, 2. Initialize object, 3. Point reference to memory.
*   **The Issue:** Without `volatile`, the CPU might reorder to 1 -> 3 -> 2. Another thread might see a non-null but uninitialized object after step 3 but before step 2, causing a crash.
*   **Role of Volatile:** Prevents this reordering, ensuring initialization happens-before the reference assignment.

### Q3: 如何將現有的 Spring Boot 應用遷移到 Virtual Threads？有什麼風險？
### Q3: How do you migrate an existing Spring Boot application to Virtual Threads? What are the risks?

**高分回答要點 (Key Points for a High Score):**
*   **步驟：** 升級至 Java 21 和 Spring Boot 3.2+，啟用 `spring.threads.virtual.enabled=true`。
*   **風險 1 (Pinning):** 檢查依賴庫（如舊版 JDBC driver 或 XML parser）是否在 `synchronized` 塊中做 I/O。
*   **風險 2 (ThreadLocal):** 檢查是否有濫用 ThreadLocal 導致的記憶體洩漏或膨脹。
*   **風險 3 (Limiting):** 以前依賴 Thread Pool 大小作為隱式的 Rate Limiter（限流），現在執行緒無限多，可能壓垮下游資料庫。需要顯式增加 Rate Limiter（如 Resilience4j）。

**Key Points for a High Score:**
*   **Steps:** Upgrade to Java 21 and Spring Boot 3.2+, enable `spring.threads.virtual.enabled=true`.
*   **Risk 1 (Pinning):** Check dependencies (like old JDBC drivers or XML parsers) for I/O inside `synchronized` blocks.
*   **Risk 2 (ThreadLocal):** Check for memory leaks or bloat caused by ThreadLocal misuse.
*   **Risk 3 (Limiting):** Previously, Thread Pool size acted as an implicit Rate Limiter. Now with unlimited threads, you might overwhelm downstream databases. Explicit Rate Limiters (e.g., Resilience4j) are needed.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **JMM 是基礎**：理解 Happens-Before 是撰寫正確併發程式的前提。
2.  **Virtual Threads 是革命**：它讓 Java 回歸 "One Thread per Request" 的簡單模型，同時擁有 Reactive 的高效能。
3.  **Pinning 是殺手**：在 Virtual Threads 中避免使用 `synchronized` 包裹 I/O 操作，改用 `ReentrantLock`。
4.  **不要池化虛擬執行緒**：它們是輕量級、用完即丟的資源。
5.  **CompletableFuture 仍有用**：在 Java 21 以前的代碼庫或需要複雜 Future 組合時，它仍是主力。

### 後續延伸 (Next Steps)
*   **實作練習**：使用 Spring Boot 3.2+ 建立一個高併發服務，並使用 `jcmd` 或 JFR 觀察 Virtual Threads 的運作與 Pinning 狀況。
*   **下一章預告**：深入探討 **JVM 效能調校與 GC 機制 (JVM Tuning & Garbage Collection)**。高併發意味著更高的物件分配率，這對 GC 是巨大的考驗。

*   **Practical Exercise:** Build a high-concurrency service using Spring Boot 3.2+ and use `jcmd` or JFR to observe Virtual Thread behavior and Pinning events.
*   **Next Chapter:** Deep dive into **JVM Tuning & Garbage Collection**. High concurrency implies higher object allocation rates, which poses a significant challenge to the GC.