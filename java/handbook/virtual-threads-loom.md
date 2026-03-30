# 虛擬執行緒 (Virtual Threads) 與 Project Loom / Virtual Threads and Project Loom

## Mental model｜心智模型

在 Java 21 之前，Java 的 `Thread` 是直接對應到作業系統的實體執行緒（OS Thread / Platform Thread）。OS 執行緒非常昂貴：建立慢、佔用記憶體大（預設約 1MB），且數量受限（通常幾千個就會讓系統崩潰）。這導致了傳統的 **Thread-per-request（每個請求一個執行緒）** 模型在面對高併發 I/O 時會遇到瓶頸。為了解決這個問題，我們過去被迫轉向複雜的非同步（Asynchronous）或響應式（Reactive）程式設計（如 WebFlux、CompletableFuture）。

Before Java 21, a Java `Thread` was mapped 1:1 to an Operating System thread (Platform Thread). OS threads are expensive: slow to create, memory-heavy (typically ~1MB each), and limited in number (a few thousand can crash a system). This caused the traditional **Thread-per-request** model to bottleneck under high I/O concurrency. To solve this, we were historically forced into complex asynchronous or reactive programming models (e.g., WebFlux, CompletableFuture).

**虛擬執行緒（Virtual Threads）改變了遊戲規則。** 
它們是由 JVM 管理的輕量級執行緒。你可以把它們想像成「乘客」，而 OS 執行緒是「計程車（Carrier Threads）」。
1. 當虛擬執行緒在執行 CPU 運算時，它會「騎乘（Mount）」在一台計程車上。
2. 當虛擬執行緒遇到 **阻塞 I/O（如等待資料庫回應、HTTP 請求、Thread.sleep）** 時，JVM 會自動讓它「下車（Unmount）」，把計程車讓給其他需要的乘客。
3. 當 I/O 完成，虛擬執行緒會重新排隊，等待下一台空閒的計程車繼續執行。

**Virtual Threads change the game.**
They are lightweight threads managed by the JVM. Think of them as "passengers" and OS threads as "taxis" (Carrier Threads).
1. When a virtual thread executes CPU instructions, it is "mounted" on a taxi.
2. When it encounters **blocking I/O (e.g., waiting for a DB, HTTP request, Thread.sleep)**, the JVM automatically "unmounts" it, freeing the taxi for other passengers.
3. When the I/O completes, the virtual thread queues up again for the next available taxi to resume execution.

**核心心智模型 / Core Mental Model:**
- **Cheap and Abundant:** 虛擬執行緒極度便宜，你可以輕易建立數百萬個。 / They are extremely cheap; you can easily create millions of them.
- **Throughput, not Speed:** 它們**不會**讓單一任務跑得更快（不增加 CPU 速度），但能讓伺服器同時處理**更多**等待中的任務（極大化吞吐量）。 / They do **not** make a single task faster (no CPU speedup), but they allow the server to handle **more** waiting tasks concurrently (maximizing throughput).
- **Synchronous is back:** 你可以用簡單、易讀的同步（阻塞）程式碼，達到非同步程式碼的效能。 / You can write simple, readable synchronous (blocking) code and achieve the performance of asynchronous code.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 擁抱 Thread-per-request 模型 / Embrace the Thread-per-request Model
不再需要為了效能把程式碼拆成複雜的 callback 或 reactive chain。直接為每個傳入的任務（HTTP 請求、Kafka 訊息）啟動一個新的虛擬執行緒。
No need to break code into complex callbacks or reactive chains for performance. Simply spawn a new virtual thread for every incoming task (HTTP request, Kafka message).

```java
// Spring Boot 3.2+ 只需要在 application.properties 加入：
// Just add this in application.properties for Spring Boot 3.2+:
// spring.threads.virtual.enabled=true
```

### 2. 使用 Virtual Thread Executor / Use Virtual Thread Executors
當你需要並行處理多個子任務時，使用專門為虛擬執行緒設計的 Executor。
When you need to process multiple sub-tasks concurrently, use the Executor designed for virtual threads.

```java
// 最佳實務：使用 try-with-resources 確保所有虛擬執行緒執行完畢
// Best Practice: Use try-with-resources to ensure all virtual threads complete
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> fetchFromApiA());
    executor.submit(() -> fetchFromApiB());
    // 離開 block 時會自動等待所有任務完成 (Implicit join)
    // Implicitly waits for all tasks to finish upon exiting the block
}
```

### 3. 用 Semaphore 取代 Thread Pool 來限制資源 / Use Semaphores instead of Thread Pools for Resource Limiting
過去我們用執行緒池（Thread Pool）的大小來限制對資料庫或外部 API 的併發請求數。現在虛擬執行緒不該被池化，因此我們應該改用 `Semaphore` 來限制「併發存取量」。
In the past, we used Thread Pool sizes to limit concurrent requests to databases or external APIs. Since virtual threads should never be pooled, we must use `Semaphore` to limit "concurrent access" instead.

```java
// 限制最多 50 個虛擬執行緒同時打這個 API
// Limit to max 50 virtual threads hitting this API concurrently
private final Semaphore rateLimiter = new Semaphore(50);

public void callFragileApi() throws InterruptedException {
    rateLimiter.acquire();
    try {
        // 執行阻塞的 HTTP 呼叫 / Perform blocking HTTP call
    } finally {
        rateLimiter.release();
    }
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 反模式 1：池化虛擬執行緒 / Anti-pattern 1: Pooling Virtual Threads
**千萬不要把虛擬執行緒放進 Thread Pool！** 它們的設計是「用完即丟」的。池化它們不僅沒有好處，反而會浪費記憶體並破壞其設計初衷。
**Never put virtual threads in a Thread Pool!** They are designed to be disposable. Pooling them offers no benefits, wastes memory, and defeats their purpose.
*   **Wrong:** `Executors.newFixedThreadPool(100, Thread.ofVirtual().factory())`
*   **Right:** `Executors.newVirtualThreadPerTaskExecutor()`

### ❌ 反模式 2：用於 CPU 密集型任務 / Anti-pattern 2: Using them for CPU-bound tasks
虛擬執行緒只有在「阻塞（Blocking）」時才會讓出底層資源。如果你用它來做影像處理或複雜演算法（無 I/O），它會霸佔 Carrier Thread，導致其他虛擬執行緒餓死（Starvation）。
Virtual threads only yield underlying resources when they "block". If you use them for image processing or complex algorithms (no I/O), they will hog the Carrier Thread, causing starvation for other virtual threads.
*   **Fix:** 將 CPU 密集型任務交給傳統的 `ForkJoinPool` 或固定的 Platform Thread Pool。 / Offload CPU-bound tasks to a traditional `ForkJoinPool` or a fixed Platform Thread Pool.

### 💣 踩雷點 3：Carrier Thread Pinning (釘選效應) / Pitfall 3: Carrier Thread Pinning
這是 Java 21 最容易踩的雷。當虛擬執行緒在 `synchronized` 區塊內，或呼叫 JNI (Native code) 時發生阻塞，它會被「釘（Pinned）」在 Carrier Thread 上無法下車。這會導致底層 OS 執行緒被耗盡，系統效能崩潰。
This is the biggest trap in Java 21. When a virtual thread blocks inside a `synchronized` block or while calling JNI (Native code), it gets "pinned" to the Carrier Thread and cannot unmount. This exhausts the underlying OS threads and crashes system performance.
*   **Fix:** 將 `synchronized` 替換為 `ReentrantLock`。 / Replace `synchronized` with `ReentrantLock`.

```java
// ❌ 容易導致 Pinning (如果 doBlockingIO 很久)
// ❌ Prone to Pinning (if doBlockingIO takes long)
public synchronized void process() {
    doBlockingIO(); 
}

// ✅ 虛擬執行緒友善的做法
// ✅ Virtual Thread friendly approach
private final ReentrantLock lock = new ReentrantLock();
public void process() {
    lock.lock();
    try {
        doBlockingIO();
    } finally {
        lock.unlock();
    }
}
```

### 💣 踩雷點 4：肥大的 ThreadLocal / Pitfall 4: Bloated ThreadLocal
以前你可能只有 200 個執行緒，每個執行緒的 `ThreadLocal` 存個 1MB 資料沒問題。現在你有 1,000,000 個虛擬執行緒，同樣的做法會立刻導致 `OutOfMemoryError`。
Previously, you might have 200 threads, and storing 1MB in `ThreadLocal` per thread was fine. Now, with 1,000,000 virtual threads, the same approach will instantly cause an `OutOfMemoryError`.
*   **Fix:** 盡量減少 `ThreadLocal` 的使用，或關注未來的 `ScopedValue` (Java 21 Preview) 特性。 / Minimize `ThreadLocal` usage, or look into the upcoming `ScopedValue` (Java 21 Preview) feature.

---

## Checklists & workflows｜檢查清單與流程

在將現有專案遷移至虛擬執行緒，或設計新架構時，請使用此清單：
Use this checklist when migrating an existing project to virtual threads or designing a new architecture:

- [ ] **我已經確認應用程式是 I/O 密集型 (I/O-bound)。** (如果是 CPU 密集型，虛擬執行緒沒有幫助)。
      **I have verified the application is I/O-bound.** (If it's CPU-bound, virtual threads won't help).
- [ ] **我已經移除了所有對虛擬執行緒的池化 (Pooling) 機制。** 改用 `newVirtualThreadPerTaskExecutor()`。
      **I have removed all pooling mechanisms for virtual threads.** Switched to `newVirtualThreadPerTaskExecutor()`.
- [ ] **我已經檢查了程式碼中的 `synchronized` 區塊。** 確保裡面沒有長時間的阻塞 I/O，否則已替換為 `ReentrantLock`。
      **I have audited `synchronized` blocks in the code.** Ensured no long-blocking I/O occurs inside them, otherwise replaced with `ReentrantLock`.
- [ ] **我已經加上 JVM 啟動參數來監控 Pinning 問題。** (測試環境必備：`-Djdk.tracePinnedThreads=full`)。
      **I have added JVM startup flags to monitor Pinning.** (Essential for testing environments: `-Djdk.tracePinnedThreads=full`).
- [ ] **我已經審查了 `ThreadLocal` 的大小。** 確保沒有在 ThreadLocal 中快取大型物件 (如 Jackson ObjectMapper、大型 Buffer)。
      **I have reviewed `ThreadLocal` sizes.** Ensured no large objects (e.g., Jackson ObjectMapper, large buffers) are cached in ThreadLocal.
- [ ] **我已經使用 `Semaphore` 替換了依賴 Thread Pool Size 的限流機制。**
      **I have replaced rate-limiting mechanisms that relied on Thread Pool size with `Semaphore`.**

---

## Real-world examples｜實戰案例

### 情境：微服務資料聚合 (Microservice Data Aggregation)
假設我們需要處理一個使用者的請求，該請求必須同時呼叫三個外部服務（User Profile, Order History, Recommendations），並將結果合併。
**Scenario:** Suppose we need to process a user request that must simultaneously call three external services (User Profile, Order History, Recommendations) and aggregate the results.

**過去的做法 (CompletableFuture)：** 程式碼難以閱讀，且 Exception 處理複雜。
**Past Approach (CompletableFuture):** Hard to read, complex exception handling.

**現代 Java 21 虛擬執行緒做法 / Modern Java 21 Virtual Thread Approach:**

```java
public UserDashboard getDashboardData(String userId) throws InterruptedException, ExecutionException {
    // 建立一個會為每個任務產生新虛擬執行緒的 Executor
    // Create an Executor that spawns a new virtual thread for each task
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        
        // 提交任務 (非同步啟動)
        // Submit tasks (starts asynchronously)
        Future<UserProfile> profileFuture = executor.submit(() -> userService.getProfile(userId));
        Future<List<Order>> ordersFuture = executor.submit(() -> orderService.getOrders(userId));
        Future<List<Item>> recsFuture = executor.submit(() -> recService.getRecommendations(userId));
        
        // 同步等待結果 (這會阻塞當前的虛擬執行緒，但非常廉價，不會阻塞 OS 執行緒！)
        // Synchronously wait for results (This blocks the current virtual thread, but it's cheap and doesn't block the OS thread!)
        UserProfile profile = profileFuture.get();
        List<Order> orders = ordersFuture.get();
        List<Item> recs = recsFuture.get();
        
        return new UserDashboard(profile, orders, recs);
        
    } // try-with-resources 結束時，會確保所有未完成的執行緒被正確處理
      // At the end of try-with-resources, it ensures all pending threads are handled properly
}
```

**架構影響 / Architectural Impact:**
在 Spring Boot 3.2+ 中，只要開啟虛擬執行緒，Tomcat 就會為每個進來的 HTTP 請求分配一個虛擬執行緒。當上述程式碼執行到 `.get()` 等待外部 API 回應時，該虛擬執行緒會被掛起（Unmounted），底層的 OS 執行緒立刻被釋放去接聽下一個使用者的 HTTP 請求。這使得原本只能承受 500 併發的伺服器，在不增加硬體的情況下，輕鬆承受 10,000+ 的併發連線。
In Spring Boot 3.2+, once virtual threads are enabled, Tomcat assigns a virtual thread to every incoming HTTP request. When the code above hits `.get()` and waits for external APIs, the virtual thread is unmounted. The underlying OS thread is immediately freed to accept the next user's HTTP request. This allows a server that previously bottlenecked at 500 concurrent connections to easily handle 10,000+ concurrent connections without additional hardware.