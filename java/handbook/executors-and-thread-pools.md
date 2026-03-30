# 執行緒池設計與 Executors 實務 / Thread Pool Design and Executors

## Mental model｜心智模型

理解 Java `ThreadPoolExecutor` 最重要的一件事，是打破「任務一多就會馬上建立新執行緒」的迷思。請用「**工廠、排隊區與臨時工**」的心智模型來理解它的運作機制：
The most crucial thing to understand about Java's `ThreadPoolExecutor` is breaking the myth that "new threads are created immediately when tasks increase." Use the mental model of a "**Factory, Waiting Area, and Temp Workers**" to understand its mechanics:

1. **Core Pool Size (正職員工 / Full-time Employees):**
   當任務進來時，優先交給正職員工。如果正職員工都在忙，任務**不會**馬上找臨時工，而是進入排隊區。
   When a task arrives, it's assigned to a full-time employee first. If all are busy, the task does **not** trigger hiring temp workers immediately; instead, it goes to the waiting area.
2. **Work Queue (排隊區 / Waiting Area):**
   這是一個緩衝區。只有當排隊區**完全塞滿**時，工廠才會開始招募臨時工。
   This is a buffer. The factory will only start hiring temp workers when the waiting area is **completely full**.
3. **Maximum Pool Size (加上臨時工的總人數 / Total Capacity including Temps):**
   當排隊區滿了，且總人數還沒達到上限時，才會建立新的執行緒（臨時工）來消化任務。
   When the queue is full and the total number of workers hasn't reached the maximum, new threads (temp workers) are created to process tasks.
4. **Rejection Policy (拒絕策略 / Rejection Policy):**
   如果排隊區滿了，且總人數也達到上限，新來的任務就會被拒絕（例如：請客顧明天再來，或由呼叫者自己處理）。
   If the queue is full and the max capacity is reached, new tasks are rejected (e.g., telling the customer to come back later, or forcing the caller to do the work).

> **💡 核心公式 / Core Formula:**
> 任務提交 -> `corePoolSize` 滿了? -> 塞入 `workQueue` -> `workQueue` 滿了? -> 擴充至 `maximumPoolSize` -> `maximumPoolSize` 滿了? -> 觸發 `RejectedExecutionHandler`。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 永遠自訂 ThreadPoolExecutor / Always Customize ThreadPoolExecutor
在正式環境中，**絕對不要**使用 `Executors.newFixedThreadPool()` 或 `Executors.newCachedThreadPool()`。它們預設使用無上限的佇列（`Integer.MAX_VALUE`）或無上限的執行緒數，極易導致 OutOfMemoryError (OOM) 或 CPU 耗盡。
In production environments, **never** use `Executors.newFixedThreadPool()` or `Executors.newCachedThreadPool()`. They default to unbounded queues (`Integer.MAX_VALUE`) or unbounded thread counts, which easily lead to OutOfMemoryError (OOM) or CPU exhaustion. Instead, explicitly instantiate `ThreadPoolExecutor`.

### 2. 替執行緒命名 / Name Your Threads
使用自訂的 `ThreadFactory` 為執行緒命名（例如 `payment-processor-pool-%d`）。這在查看 Thread Dump 或日誌排查問題時是救命稻草。
Use a custom `ThreadFactory` to name your threads (e.g., `payment-processor-pool-%d`). This is a lifesaver when analyzing Thread Dumps or logs during troubleshooting.

### 3. 根據任務特性設定大小 / Sizing Based on Task Characteristics
- **CPU 密集型 (CPU-bound):** `Pool Size = N (CPU cores) + 1`。多出來的 1 是為了防止缺頁中斷 (Page Fault) 導致的暫停。
- **I/O 密集型 (I/O-bound):** `Pool Size = N * U * (1 + W/C)`。其中 U 是目標 CPU 使用率，W/C 是等待時間 (Wait time) 與計算時間 (Compute time) 的比例。通常 I/O 密集型可以設定較大的執行緒數（如 200-500）。
- **CPU-bound:** `Pool Size = N (CPU cores) + 1`. The extra 1 prevents stalling due to page faults.
- **I/O-bound:** `Pool Size = N * U * (1 + W/C)`, where U is target CPU utilization and W/C is the ratio of Wait time to Compute time. I/O-bound pools can usually be much larger (e.g., 200-500).

### 4. 艙壁模式 (Bulkhead Pattern)
不要讓所有任務共用同一個全域執行緒池。將不同業務邏輯（如寄送 Email、資料庫查詢、外部 API 呼叫）隔離到不同的執行緒池，避免某個慢速服務拖垮整個系統。
Do not share a single global thread pool for all tasks. Isolate different business logic (e.g., sending emails, DB queries, external API calls) into separate thread pools to prevent a slow service from bringing down the entire system.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 吞噬異常 (Swallowing Exceptions)
**Pitfall:** 使用 `submit()` 提交任務時，如果內部拋出 `RuntimeException`，日誌裡完全看不到錯誤，除非你呼叫了 `Future.get()`。
**Pitfall:** When submitting tasks via `submit()`, if a `RuntimeException` is thrown internally, it won't appear in the logs unless you call `Future.get()`.
**Fix:** 在 `Runnable` 內部使用 `try-catch` 包覆全部邏輯，或改用 `execute()` 搭配自訂的 `UncaughtExceptionHandler`。
**Fix:** Wrap the entire logic inside the `Runnable` with a `try-catch` block, or use `execute()` combined with a custom `UncaughtExceptionHandler`.

### 2. 執行緒池死結 (Thread Pool Deadlock / Thread Starvation)
**Pitfall:** 父任務在執行緒池中執行，並提交了子任務到**同一個執行緒池**，然後呼叫 `future.get()` 等待子任務完成。如果父任務佔滿了所有核心執行緒，子任務將永遠在佇列中等待，導致死結。
**Pitfall:** A parent task runs in a thread pool, submits a child task to the **same pool**, and calls `future.get()` to wait for it. If parent tasks exhaust all core threads, child tasks will wait in the queue forever, causing a deadlock.
**Fix:** 絕對不要在同一個執行緒池中等待另一個任務的結果。父子任務應使用不同的執行緒池。
**Fix:** Never wait for the result of another task in the same thread pool. Use separate thread pools for parent and child tasks.

### 3. ThreadLocal 記憶體洩漏 (ThreadLocal Leaks)
**Pitfall:** 在任務中設定了 `ThreadLocal`，但任務結束時忘記清理。因為執行緒會被重複使用，下一個任務可能會讀到上一個任務的髒資料，甚至導致記憶體洩漏。
**Pitfall:** Setting a `ThreadLocal` in a task but forgetting to clean it up when the task finishes. Since threads are reused, the next task might read dirty data from the previous task, or it may cause memory leaks.
**Fix:** 永遠在 `finally` 區塊中呼叫 `ThreadLocal.remove()`。
**Fix:** Always call `ThreadLocal.remove()` in a `finally` block.

---

## Checklists & workflows｜檢查清單與流程

- [ ] **是否避免了 `Executors` 工廠方法？** 我是否明確使用了 `new ThreadPoolExecutor(...)`？ / Did I avoid `Executors` factory methods and explicitly use `new ThreadPoolExecutor(...)`?
- [ ] **佇列是否有界限？** 我是否使用了 `ArrayBlockingQueue` 或指定容量的 `LinkedBlockingQueue`？ / Is the queue bounded? Did I use `ArrayBlockingQueue` or a capacity-limited `LinkedBlockingQueue`?
- [ ] **執行緒是否命名？** 我是否提供了自訂的 `ThreadFactory` 來標識業務用途？ / Are threads named? Did I provide a custom `ThreadFactory` to identify the business purpose?
- [ ] **拒絕策略是否明確？** 當負載過高時，我是選擇 `CallerRunsPolicy`、`AbortPolicy` 還是自訂記錄日誌？ / Is the rejection policy explicit? Did I choose `CallerRunsPolicy`, `AbortPolicy`, or custom logging for high-load scenarios?
- [ ] **是否實作了優雅關閉 (Graceful Shutdown)？** 應用程式關閉時，是否呼叫了 `shutdown()` 並搭配 `awaitTermination()` 等待任務完成？ / Is graceful shutdown implemented? On app shutdown, do I call `shutdown()` and use `awaitTermination()` to wait for tasks to finish?
- [ ] **異常是否被妥善處理？** 任務內的未捕獲異常是否會被記錄到日誌中？ / Are exceptions handled properly? Are uncaught exceptions within tasks logged?

---

## Real-world examples｜實戰案例

以下是一個在正式環境中安全、健壯的 `ThreadPoolExecutor` 實作範例，包含了命名、有界佇列、拒絕策略與優雅關閉：
Below is an example of a safe and robust `ThreadPoolExecutor` implementation for production, including naming, bounded queues, rejection policies, and graceful shutdown:

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ResilientThreadPoolFactory {

    public static ThreadPoolExecutor createPaymentProcessorPool() {
        // 1. 定義核心參數 / Define core parameters
        int corePoolSize = 10;
        int maxPoolSize = 50;
        long keepAliveTime = 60L;
        
        // 2. 有界佇列：最多允許 500 個任務排隊 / Bounded queue: max 500 tasks in waiting area
        BlockingQueue<Runnable> workQueue = new ArrayBlockingQueue<>(500);

        // 3. 自訂執行緒工廠：為執行緒命名並設定為守護執行緒 (可選) 
        // Custom ThreadFactory: Name threads and set as daemon (optional)
        ThreadFactory threadFactory = new ThreadFactory() {
            private final AtomicInteger counter = new AtomicInteger(1);
            @Override
            public Thread newThread(Runnable r) {
                Thread t = new Thread(r, "payment-pool-worker-" + counter.getAndIncrement());
                // 確保未捕獲的異常被記錄 / Ensure uncaught exceptions are logged
                t.setUncaughtExceptionHandler((thread, ex) -> {
                    System.err.println("Uncaught exception in thread " + thread.getName() + ": " + ex.getMessage());
                });
                return t;
            }
        };

        // 4. 拒絕策略：當佇列滿且達到 maxPoolSize 時的處理方式
        // Rejection Policy: How to handle when queue is full and maxPoolSize is reached
        // CallerRunsPolicy: 由提交任務的執行緒（通常是 Tomcat/主執行緒）自己執行，產生背壓 (Backpressure)
        RejectedExecutionHandler rejectionHandler = new ThreadPoolExecutor.CallerRunsPolicy();

        // 5. 建立 ThreadPoolExecutor / Create ThreadPoolExecutor
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
                corePoolSize,
                maxPoolSize,
                keepAliveTime,
                TimeUnit.SECONDS,
                workQueue,
                threadFactory,
                rejectionHandler
        );

        // 允許核心執行緒在閒置時被回收 (視業務需求而定)
        // Allow core threads to time out if idle (depends on business needs)
        executor.allowCoreThreadTimeOut(true);

        return executor;
    }

    // 優雅關閉的標準流程 / Standard workflow for Graceful Shutdown
    public static void shutdownGracefully(ExecutorService executor) {
        executor.shutdown(); // 拒絕新任務 / Reject new tasks
        try {
            // 等待現有任務完成 / Wait for existing tasks to finish
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow(); // 強制取消執行中的任務 / Force cancel running tasks
                // 再次等待 / Wait again
                if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                    System.err.println("Pool did not terminate");
                }
            }
        } catch (InterruptedException ie) {
            executor.shutdownNow();
            Thread.currentThread().interrupt(); // 保留中斷狀態 / Preserve interrupt status
        }
    }
}
```