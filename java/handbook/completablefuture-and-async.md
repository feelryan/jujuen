# CompletableFuture 與非同步程式設計 / CompletableFuture and Asynchronous Programming

## Mental model｜心智模型

把 `CompletableFuture` 想像成一條**「非同步的工廠輸送帶 (Asynchronous Assembly Line)」**。
在傳統的同步程式設計中，執行緒就像是一個工人，他必須站在機器前面等待零件加工完成（阻塞 Blocking），才能進行下一步。而在 `CompletableFuture` 的世界裡，你是在「定義管線規則」：當 A 機器完成時，自動把結果送到 B 機器；如果 A 機器卡住了（超時），就啟動備用方案 C；如果發生錯誤，就把不良品送到 D 處理區。

Think of `CompletableFuture` as an **"asynchronous assembly line."**
In traditional synchronous programming, a thread is like a worker who must stand in front of a machine and wait for a part to be processed (blocking) before moving to the next step. In the world of `CompletableFuture`, you are "defining pipeline rules": when machine A finishes, automatically send the result to machine B; if machine A gets stuck (timeout), trigger fallback plan C; if an error occurs, send the defective product to handling area D.

核心觀念轉變 / Core Paradigm Shift：
- **從「等待結果」到「註冊回呼」** / **From "Waiting for results" to "Registering callbacks"**: 不要問「任務做完了沒？」，而是告訴系統「做完之後接著做什麼」。
- **資料流驅動** / **Data-flow driven**: 程式碼的結構反映的是資料的流向，而不是執行緒的控制流程。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 永遠為 I/O 任務指定自訂執行緒池 / Always Provide Custom Executors for I/O Tasks
預設的 `CompletableFuture.supplyAsync()` 會使用 `ForkJoinPool.commonPool()`。這個池的大小預設為 CPU 核心數減一，專為 CPU 密集型任務設計。如果你的非同步任務包含呼叫外部 API 或資料庫（I/O 阻塞），會瞬間耗盡 common pool，導致整個 JVM 的其他非同步任務癱瘓。

The default `CompletableFuture.supplyAsync()` uses `ForkJoinPool.commonPool()`. The size of this pool defaults to CPU cores minus one and is designed for CPU-bound tasks. If your async tasks involve calling external APIs or databases (I/O blocking), you will instantly exhaust the common pool, starving all other async tasks across the JVM.

### 2. 區分轉換與攤平 / Distinguish Between Transformation and Flattening
- **`thenApply`**: 類似 Stream 的 `map`。用於同步轉換結果（例如將 JSON 字串轉為 Object）。 / Similar to Stream's `map`. Used for synchronous transformation (e.g., parsing JSON string to Object).
- **`thenCompose`**: 類似 Stream 的 `flatMap`。當你的下一步也是一個會回傳 `CompletableFuture` 的非同步操作時使用，避免產生 `CompletableFuture<CompletableFuture<T>>` 的巢狀結構。 / Similar to Stream's `flatMap`. Use this when your next step also returns a `CompletableFuture` to avoid nested structures like `CompletableFuture<CompletableFuture<T>>`.

### 3. 平行組合任務 / Parallel Task Composition
使用 `thenCombine` 來平行執行兩個毫無相依性的任務，並在兩者都完成時將結果合併。這能大幅降低整體回應時間（取決於最慢的那個任務）。
Use `thenCombine` to execute two independent tasks in parallel and merge their results when both complete. This drastically reduces overall response time (bounded by the slowest task).

### 4. 建立超時與降級機制 (Java 9+) / Establish Timeouts and Fallbacks (Java 9+)
在分散式系統中，無限期等待是致命的。善用 `orTimeout()` 拋出異常，或使用 `completeOnTimeout()` 提供預設值。
In distributed systems, waiting indefinitely is fatal. Leverage `orTimeout()` to throw an exception, or `completeOnTimeout()` to provide a default fallback value.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- ❌ **在管線中途呼叫 `.join()` 或 `.get()` / Calling `.join()` or `.get()` in the middle of a pipeline**
  - **後果 / Consequence**: 這會立刻阻塞當前執行緒，破壞了非同步管線的初衷。 / This immediately blocks the current thread, defeating the entire purpose of the async pipeline.
  - **解法 / Solution**: 一路回傳 `CompletableFuture` 到最外層（例如 Controller 層），讓框架（如 Spring WebFlux 或非同步 Servlet）去處理最終的訂閱，或者只在系統的最邊界呼叫 `.join()`。 / Return the `CompletableFuture` all the way to the top layer (e.g., Controller) and let the framework handle the final subscription, or only call `.join()` at the absolute edge of the system.

- ❌ **吞噬非同步異常 / Swallowing Async Exceptions**
  - **後果 / Consequence**: 如果沒有在管線末端加上 `exceptionally` 或 `handle`，非同步執行緒內拋出的 Exception 會無聲無息地消失，除錯時會毫無頭緒。 / Without `exceptionally` or `handle` at the end of the pipeline, Exceptions thrown inside the async thread will vanish silently, making debugging a nightmare.

- ❌ **ThreadLocal 上下文遺失 / Losing ThreadLocal Context**
  - **後果 / Consequence**: 在非同步執行緒中，無法獲取原執行緒的 `ThreadLocal` 變數（如 Security Context, MDC Logging Trace ID）。 / You cannot access `ThreadLocal` variables (like Security Context, MDC Logging Trace ID) from the original thread inside the async thread.
  - **解法 / Solution**: 使用自訂的 `Executor` 裝飾器 (Decorator) 在任務提交前複製 Context，在任務執行前設定 Context，執行後清除。 / Use a custom `Executor` decorator to copy the context before task submission, set it before execution, and clear it afterward.

---

## Checklists & workflows｜檢查清單與流程

- [ ] **執行緒池檢查 / Executor Check**: 我是否為所有涉及 I/O (HTTP, DB) 的 `CompletableFuture` 顯式傳入了自訂的 `Executor`？ / Did I explicitly pass a custom `Executor` to all `CompletableFuture`s involving I/O (HTTP, DB)?
- [ ] **超時控制 / Timeout Control**: 每個外部依賴的非同步呼叫，是否都加上了 `.orTimeout()` 或 `.completeOnTimeout()`？ / Does every async call to an external dependency have `.orTimeout()` or `.completeOnTimeout()` applied?
- [ ] **異常處理 / Exception Handling**: 管線的最後是否掛載了 `.exceptionally()` 或 `.handle()` 來記錄錯誤或提供 Fallback？ / Is `.exceptionally()` or `.handle()` attached at the end of the pipeline to log errors or provide a fallback?
- [ ] **無阻塞驗證 / Non-blocking Verification**: 檢查管線鏈中（`thenApply`, `thenAccept` 內）是否隱藏了會阻塞執行緒的同步呼叫（如 `Thread.sleep` 或同步的 HTTP 請求）？如果有，應改用 `thenCompose` 串接非同步版本。 / Are there any hidden blocking calls inside the pipeline chain? If so, replace them with async versions using `thenCompose`.
- [ ] **資源釋放 / Resource Cleanup**: 如果非同步任務涉及資源操作（如檔案、連線），是否在 `.whenComplete()` 中確保資源被正確關閉（類似 `finally` 區塊）？ / If the async task involves resources, are they properly closed in `.whenComplete()` (similar to a `finally` block)?

---

## Real-world examples｜實戰案例

### 情境：電商儀表板資料聚合 / Scenario: E-commerce Dashboard Data Aggregation
我們需要同時獲取「使用者基本資料」與「使用者的最新訂單」。這兩個 API 互不相依，我們希望平行獲取以節省時間。如果訂單 API 超時，我們容忍回傳空列表；如果發生任何未預期異常，必須記錄並回傳預設的錯誤 DTO。

We need to fetch "User Profile" and "User's Latest Orders" concurrently. These two APIs are independent, and we want to fetch them in parallel to save time. If the Orders API times out, we tolerate returning an empty list. If any unexpected exception occurs, we must log it and return a default Error DTO.

```java
import java.util.concurrent.*;
import java.time.Duration;

public class DashboardService {
    
    // 1. 建立專用的 I/O 執行緒池 / Create a dedicated thread pool for I/O tasks
    private final Executor ioExecutor = Executors.newFixedThreadPool(20);

    public CompletableFuture<DashboardDTO> getDashboardData(String userId) {
        
        // 任務 A：獲取使用者資料 (非同步)
        // Task A: Fetch user profile (Async)
        CompletableFuture<UserProfile> profileFuture = CompletableFuture.supplyAsync(
            () -> fetchUserProfile(userId), 
            ioExecutor
        );

        // 任務 B：獲取訂單清單 (非同步) + 超時降級處理
        // Task B: Fetch orders (Async) + Timeout fallback
        CompletableFuture<List<Order>> ordersFuture = CompletableFuture.supplyAsync(
            () -> fetchUserOrders(userId), 
            ioExecutor
        ).completeOnTimeout(Collections.emptyList(), 2, TimeUnit.SECONDS); // 2秒超時回傳空列表 / Return empty list on 2s timeout

        // 2. 平行組合任務 A 與 B / Combine Task A and B in parallel
        return profileFuture.thenCombine(ordersFuture, (profile, orders) -> {
            // 當兩個任務都完成時，組裝結果 / Assemble result when both complete
            return new DashboardDTO(profile, orders);
        })
        // 3. 全局異常處理 / Global Exception Handling
        .exceptionally(ex -> {
            // 記錄錯誤並回傳降級的 DTO / Log error and return fallback DTO
            log.error("Failed to aggregate dashboard data for user: {}", userId, ex);
            return DashboardDTO.errorFallback();
        });
    }

    // --- Mock methods for illustration ---
    private UserProfile fetchUserProfile(String userId) {
        // 模擬 HTTP 呼叫 / Simulate HTTP call
        return new UserProfile(userId, "John Doe");
    }

    private List<Order> fetchUserOrders(String userId) {
        // 模擬可能很慢的 DB 查詢 / Simulate potentially slow DB query
        return List.of(new Order("ORD-123"), new Order("ORD-456"));
    }
}
```

### 關鍵設計解析 / Key Design Breakdown:
1. **`ioExecutor`**: 避免使用 `commonPool`，確保 I/O 延遲不會拖垮整個應用程式。 / Avoids `commonPool`, ensuring I/O latency doesn't bring down the whole application.
2. **`completeOnTimeout`**: 實踐了「優雅降級 (Graceful Degradation)」，即使訂單服務緩慢，使用者依然能看到基本資料。 / Implements "Graceful Degradation"; even if the order service is slow, the user still sees their profile.
3. **`thenCombine`**: 宣告式地表達了「等待兩者完成後合併」，底層自動處理了執行緒同步與非阻塞等待。 / Declaratively expresses "wait for both then merge", automatically handling thread synchronization and non-blocking wait under the hood.