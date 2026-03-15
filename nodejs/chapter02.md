# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Node.js 的非同步特性不僅僅是會寫 `async/await` 或 `Promise`，而是要深刻理解 Event Loop 的調度機制，以及如何處理 Node.js 最不擅長的 CPU 密集型任務。本章旨在幫助你突破單執行緒的限制，構建高並發且穩定的系統。

For senior engineers, mastering Node.js asynchronous nature goes beyond writing `async/await` or `Promise`. It requires a deep understanding of the Event Loop scheduling mechanisms and how to handle CPU-intensive tasks—Node.js's traditional weakness. This chapter aims to help you break through single-threaded limitations to build high-concurrency, stable systems.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準預測執行順序**：區分 Microtasks (Promise) 與 Macrotasks (Timers, I/O) 的優先級，避免 Event Loop 飢餓 (Starvation)。
    **Predict Execution Order:** Distinguish the priority between Microtasks (Promise) and Macrotasks (Timers, I/O) to avoid Event Loop starvation.
2.  **解決 CPU 瓶頸**：正確判斷何時使用 `Worker Threads` 或是 `Cluster Module` 來處理計算密集型任務。
    **Solve CPU Bottlenecks:** Correctly decide when to use `Worker Threads` versus the `Cluster Module` for compute-intensive tasks.
3.  **優化並發控制**：實作比 `Promise.all` 更穩健的並發限制模式 (Concurrency Limiting)，防止下游服務過載。
    **Optimize Concurrency Control:** Implement robust concurrency limiting patterns (beyond simple `Promise.all`) to prevent overloading downstream services.
4.  **掌握進階 Context 管理**：理解 `AsyncLocalStorage` 在非同步請求鏈路追蹤 (Tracing) 中的應用。
    **Master Advanced Context Management:** Understand the application of `AsyncLocalStorage` in asynchronous request tracing.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Event Loop 的精細模型 (The Granular Model of the Event Loop)

很多工程師只知道「非同步會被放到 Queue 中」，但在資深層級，你需要區分 **Microtask Queue** 與 **Macrotask (Callback) Queue**。

Many engineers simply know that "async tasks go into a Queue." At a senior level, you must distinguish between the **Microtask Queue** and the **Macrotask (Callback) Queue**.

*   **Microtasks (Promise.then, queueMicrotask)**: 優先級最高。在當前操作結束後、下一個 Event Loop 階段開始前**立即執行**。如果 Microtask 隊列無限增長，Event Loop 會被卡死，導致 I/O 無法處理。
    **Microtasks (Promise.then, queueMicrotask):** Highest priority. Executed **immediately** after the current operation completes and before the next Event Loop phase begins. If the Microtask queue grows indefinitely, the Event Loop will hang, preventing I/O processing.
*   **Macrotasks (setTimeout, setImmediate, I/O callbacks)**: 每個 Loop 階段 (Timers, Poll, Check) 執行。
    **Macrotasks (setTimeout, setImmediate, I/O callbacks):** Executed during specific Loop phases (Timers, Poll, Check).

**心智模型類比 (Mental Model Analogy):**
想像你在銀行櫃檯 (Call Stack)。
*   **Microtask** 就像是VIP插隊機制：只要櫃檯一空下來，VIP (Promise callbacks) 就會立刻補上，直到 VIP 處理完，才會叫號。
*   **Macrotask** 才是正常的叫號排隊 (Timers/IO)。
*   **Worker Threads** 則是銀行新開了另一個完全獨立的櫃檯，有自己的辦事員，不影響主櫃檯。

Imagine you are at a bank teller (Call Stack).
*   **Microtasks** are like a VIP cutting-in-line mechanism: as soon as the teller is free, VIPs (Promise callbacks) jump in immediately. Normal numbers are only called after all VIPs are served.
*   **Macrotasks** are the regular ticket queue (Timers/IO).
*   **Worker Threads** are like the bank opening a completely separate counter with its own teller, independent of the main one.

## 2.2 Scaling Strategies: Cluster vs. Worker Threads

這是系統設計中常見的混淆點。
This is a common point of confusion in system design.

| Feature | Cluster Module | Worker Threads |
| :--- | :--- | :--- |
| **Isolation** | Process Isolation (獨立記憶體空間) | Thread Isolation (共享記憶體空間透過 `SharedArrayBuffer`) |
| **Overhead** | High (完整的 Node.js 實例副本) | Medium (輕量級，但在 Node 中仍比 OS Thread 重) |
| **Use Case** | **Horizontal Scaling**: 利用多核 CPU 處理 HTTP 請求流量 | **CPU Intensive**: 處理加密、壓縮、圖像處理等阻塞操作 |
| **Communication**| IPC (Inter-Process Communication) | MessageChannel / Shared Memory |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 處理高並發與下游保護 (Handling High Concurrency & Downstream Protection)

在微服務架構中，Node.js 常作為 Gateway 或 Aggregator。當面對突發流量時，簡單的 `Promise.all` 是一把雙面刃。

In a microservices architecture, Node.js often acts as a Gateway or Aggregator. When facing burst traffic, a simple `Promise.all` is a double-edged sword.

*   **Naive Approach**: `await Promise.all(items.map(fetch))`。這會瞬間發出所有請求，可能觸發下游 Rate Limit 或導致 TCP 連接耗盡 (Connection Exhaustion)。
*   **System Design View**: 必須實作 **Bulkhead Pattern** (艙壁模式) 或 **Concurrency Limiter** (如 `p-limit`)。這保證了 Node.js 服務的穩定性，同時保護下游依賴。

*   **Naive Approach**: `await Promise.all(items.map(fetch))`. This fires all requests instantly, potentially triggering downstream Rate Limits or causing TCP Connection Exhaustion.
*   **System Design View**: You must implement the **Bulkhead Pattern** or a **Concurrency Limiter** (like `p-limit`). This ensures the stability of the Node.js service while protecting downstream dependencies.

## 3.2 可觀測性與 Context Propagation (Observability & Context Propagation)

在非同步呼叫鏈中 (例如：Controller -> Service -> DB Access)，如何保持 `Request ID` 或 `User Context`？

In an asynchronous call chain (e.g., Controller -> Service -> DB Access), how do you maintain the `Request ID` or `User Context`?

*   **過去的做法**: 將 context 物件作為參數層層傳遞 (Parameter drilling)。
*   **現代做法**: 使用 `AsyncLocalStorage` (ALS)。這類似於 Java 的 `ThreadLocal`，但在 Event Loop 模型下運作。這對於分散式追蹤 (Distributed Tracing) 至關重要。

*   **Past Approach**: Passing the context object as an argument through every layer (Parameter drilling).
*   **Modern Approach**: Using `AsyncLocalStorage` (ALS). This is similar to Java's `ThreadLocal` but works within the Event Loop model. It is crucial for Distributed Tracing.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：CPU 密集型任務導致的 Event Loop 阻塞
## Case: Event Loop Blocking via CPU-Intensive Task

**背景 (Context)**: 一個 Node.js 服務需要計算大量數據的 Hash (例如 SHA-256) 或生成 PDF 報告。
**Context**: A Node.js service needs to calculate Hashes (e.g., SHA-256) for large datasets or generate PDF reports.

### 4.1 初始方案 (The Naive Solution)

直接在 Main Thread 執行計算。
Executing the calculation directly on the Main Thread.

```javascript
const crypto = require('crypto');

// This blocks the Event Loop! No other requests can be served.
function heavyTaskSync() {
  const start = Date.now();
  while(Date.now() - start < 2000) {
    // Simulate CPU work
  }
  return 'done';
}

app.get('/compute', (req, res) => {
  const result = heavyTaskSync(); // BLOCKS HERE
  res.send(result);
});
```

**問題**: 在這 2 秒內，伺服器對所有其他請求（包括簡單的 Health Check）均無回應。
**Problem**: During these 2 seconds, the server is unresponsive to *all* other requests, including simple Health Checks.

### 4.2 進階方案：Worker Threads (The Advanced Solution)

將計算移至 Worker Thread，保持 Main Thread 負責 I/O 調度。
Offload the calculation to a Worker Thread, keeping the Main Thread free for I/O scheduling.

**worker.js**:
```javascript
const { parentPort, workerData } = require('worker_threads');

// Perform CPU intensive task
function heavyTask(data) {
  // Imagine complex calculation here
  return `Processed ${data}`;
}

const result = heavyTask(workerData);
parentPort.postMessage(result);
```

**main.js**:
```javascript
const { Worker } = require('worker_threads');
const path = require('path');

function runService(workerData) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(path.join(__dirname, './worker.js'), { workerData });
    
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}

app.get('/compute', async (req, res) => {
  try {
    // Main thread is NOT blocked. It just waits for the Promise.
    const result = await runService('some data'); 
    res.send(result);
  } catch (err) {
    res.status(500).send(err.message);
  }
});
```

### 4.3 實務考量 (Practical Considerations)

*   **Worker Pool**: 建立 Worker 的開銷很高 (Script parsing, V8 context creation)。在 Production 環境中，**必須**使用 Worker Pool (如 `piscina` 或自行實作) 來重複利用 Worker。
*   **Serialization Cost**: 傳遞給 Worker 的數據需要被複製 (Structured Clone Algorithm)。如果數據量極大 (如 100MB 的 Buffer)，應考慮使用 `SharedArrayBuffer` 或 `Transferable Objects` 來避免複製開銷。

*   **Worker Pool**: Creating a Worker is expensive (Script parsing, V8 context creation). In Production, you **must** use a Worker Pool (like `piscina` or a custom implementation) to reuse workers.
*   **Serialization Cost**: Data passed to Workers is copied (Structured Clone Algorithm). If the data is huge (e.g., 100MB Buffer), consider using `SharedArrayBuffer` or `Transferable Objects` to avoid copying overhead.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 混用 Promise 與 Callback (The "Zalgo" Anti-pattern)

有些程式碼路徑是同步回傳，有些是非同步。這會導致不可預測的執行順序。

Some code paths return synchronously, while others return asynchronously. This leads to unpredictable execution order.

*   **Bad**:
    ```javascript
    function getData(key, callback) {
      if (cache[key]) {
        callback(cache[key]); // Sync execution
      } else {
        db.get(key, callback); // Async execution
      }
    }
    ```
*   **Fix**: 始終保持非同步。使用 `process.nextTick()` 或直接回傳 `Promise.resolve()`。
*   **Fix**: Always stay asynchronous. Use `process.nextTick()` or simply return `Promise.resolve()`.

## 5.2 誤用 Promise.all 處理互不相關的邏輯 (Misusing Promise.all for Unrelated Logic)

*   **Pitfall**: 使用 `Promise.all([taskA, taskB])`。如果 `taskA` 失敗，`taskB` 的結果也會被丟棄（儘管它可能成功了）。
*   **Pitfall**: Using `Promise.all([taskA, taskB])`. If `taskA` fails, the result of `taskB` is discarded (even if it succeeded).
*   **Better**: 對於互不依賴的並行任務，使用 `Promise.allSettled()`，然後分別檢查每個結果的 `status`。
*   **Better**: For independent parallel tasks, use `Promise.allSettled()`, then inspect the `status` of each result individually.

## 5.3 在 Request Handler 中建立未管理的 Promise (Unmanaged Promises in Handlers)

*   **Pitfall**: 觸發一個非同步操作但不 `await` 它，也不 `catch` 錯誤（Fire-and-forget）。
*   **Pitfall**: Triggering an async operation without `await`-ing it or `catch`-ing errors (Fire-and-forget).
    ```javascript
    app.post('/log', (req, res) => {
      saveLogToS3(req.body); // No await, no catch
      res.send('OK');
    });
    ```
*   **Consequence**: 如果 `saveLogToS3` 拋出錯誤，可能會導致 `UnhandledPromiseRejection`，在舊版 Node.js 會印出警告，在新版可能會導致 Process Crash。
*   **Consequence**: If `saveLogToS3` throws, it causes an `UnhandledPromiseRejection`. This prints a warning in older Node versions but may crash the process in newer ones.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請解釋 Node.js 的 Event Loop 階段，以及 `process.nextTick` 與 `setImmediate` 的區別？
## Q1: Explain the Node.js Event Loop phases and the difference between `process.nextTick` and `setImmediate`.

*   **高分回答要點 (Key Points)**:
    *   提到主要階段：Timers, Poll (I/O), Check, Close callbacks。
    *   解釋 `process.nextTick` 不是 Event Loop 的一部分，而是發生在當前操作完成後、任何階段繼續之前（優先級高於 Promise）。
    *   解釋 `setImmediate` 設計用於在 Poll 階段結束後的 Check 階段執行。
    *   **加分項**: 提到 Microtask Queue 的 Starvation 風險。

*   **Key Points**:
    *   Mention main phases: Timers, Poll (I/O), Check, Close callbacks.
    *   Explain that `process.nextTick` is technically not part of the Event Loop phases but fires after the current operation and before the loop continues (Priority > Promise).
    *   Explain that `setImmediate` runs in the Check phase, immediately after the Poll phase.
    *   **Bonus**: Mention the risk of Microtask Queue Starvation.

## Q2: 你如何在 Node.js 中處理 CPU 密集型任務？
## Q2: How do you handle CPU-intensive tasks in Node.js?

*   **高分回答要點 (Key Points)**:
    *   承認 Node.js 單執行緒不適合 CPU 任務。
    *   方案比較：
        1.  **Worker Threads**: 最優解，共享記憶體，開銷比 Process 低。
        2.  **Child Process / Cluster**: 隔離性好但開銷大，適合執行外部 binary。
        3.  **Offloading**: 將任務推送到 Message Queue (RabbitMQ/SQS)，由專門的 Worker Service (可能是 Python/Go) 處理。
    *   實務細節：提到 Worker Pool 的重要性。

*   **Key Points**:
    *   Acknowledge Node.js single-threaded nature is bad for CPU tasks.
    *   Compare solutions:
        1.  **Worker Threads**: Best for JS execution, shared memory, lower overhead than processes.
        2.  **Child Process / Cluster**: Good isolation but high overhead, good for external binaries.
        3.  **Offloading**: Push to a Message Queue (RabbitMQ/SQS) and handle via a dedicated Worker Service (maybe in Python/Go).
    *   Practical detail: Mention the necessity of a Worker Pool.

## Q3: 什麼是 Backpressure？在 Node.js Streams 或 Async Iterator 中如何處理？
## Q3: What is Backpressure? How is it handled in Node.js Streams or Async Iterators?

*   **高分回答要點 (Key Points)**:
    *   定義：生產者速度快於消費者速度，導致記憶體堆積。
    *   機制：Stream 的 `write()` 回傳 `false` 時應暫停寫入，監聽 `drain` 事件恢復。
    *   現代解法：使用 `pipeline` (自動處理) 或 Async Iterators (`for await...of`)，它們天然支援 Backpressure。

*   **Key Points**:
    *   Definition: Producer is faster than Consumer, causing memory buildup.
    *   Mechanism: When Stream `write()` returns `false`, pause writing and listen for `drain` event.
    *   Modern Solution: Use `pipeline` (handles it automatically) or Async Iterators (`for await...of`), which support Backpressure natively.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Microtasks vs Macrotasks**: 理解 Promise (`then`) 會插隊，而 `setTimeout` 會排隊。
2.  **Worker Threads**: 是解決 Node.js CPU 瓶頸的標準解法，但務必配合 **Worker Pool** 使用。
3.  **Cluster Module**: 主要用於多核擴展 (Horizontal Scaling)，與 Worker Threads (CPU Task Offloading) 用途不同。
4.  **AsyncLocalStorage**: 是實現 Request Tracing 和 Context Propagation 的現代標準。
5.  **Concurrency Control**: 在高並發場景下，永遠不要裸用 `Promise.all` 處理大量請求，請使用 `p-limit` 或類似機制。

## 後續延伸 (Next Steps)
*   **Streams & Buffers**: 既然掌握了非同步與並發，下一步應深入學習如何高效處理大文件與數據流 (Chapter 03)。
*   **Performance Profiling**: 學習使用 Chrome DevTools 或 `clinic.js` 來視覺化 Event Loop 延遲與 Memory Leaks。
*   **Libuv Internals**: 閱讀關於 Libuv Thread Pool 的運作原理，了解 File System 與 DNS 操作是如何在底層實現非同步的。