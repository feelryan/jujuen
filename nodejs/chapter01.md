# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，我們早已習慣使用 `async/await` 和 `Promise` 來處理非同步邏輯。然而，當系統面臨高併發（High Concurrency）瓶頸、不明原因的 CPU 飆升，或是偶發性的延遲（Latency Spikes）時，僅僅會寫 API 是不夠的。你需要具備透視 Node.js Runtime 內部的能力。

As senior engineers, we are already accustomed to using `async/await` and `Promise` to handle asynchronous logic. However, when a system faces high concurrency bottlenecks, unexplained CPU spikes, or sporadic latency spikes, merely knowing how to write APIs is insufficient. You need the ability to look inside the Node.js Runtime.

本章的目標是揭開 Node.js "Single Thread" 的面紗，讓你能夠：

The goal of this chapter is to unveil the "Single Thread" myth of Node.js, enabling you to:

1.  **精準預測執行順序**：在混合使用 `setTimeout`, `setImmediate`, `process.nextTick`, 與 `Promise` 時，能準確判斷程式碼的執行先後。
    **Predict Execution Order Accurately**: Accurately determine the execution sequence when mixing `setTimeout`, `setImmediate`, `process.nextTick`, and `Promise`.
2.  **診斷 Event Loop Lag**：理解 Event Loop 各階段（Phases）的運作機制，從而識別並解決阻塞（Blocking）問題。
    **Diagnose Event Loop Lag**: Understand the mechanisms of Event Loop phases to identify and resolve blocking issues.
3.  **理解 libuv 與 V8 的分工**：區分 JavaScript 執行緒與底層 C++ 執行緒池（Thread Pool）的邊界，這對於調校 I/O 密集型應用至關重要。
    **Understand the Division Between libuv and V8**: Distinguish the boundary between the JavaScript thread and the underlying C++ Thread Pool, which is crucial for tuning I/O-intensive applications.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 架構總覽：V8 與 libuv (Architecture Overview: V8 & libuv)

Node.js 並非單一的技術，而是 V8 引擎與 libuv 函式庫的結合。

Node.js is not a single technology but a combination of the V8 engine and the libuv library.

*   **V8 Engine**: Google 開發的 JavaScript 引擎，負責解析與執行 JS 程式碼。它是單執行緒的（Single Threaded），這意味著同一時間只能執行一段 JS 代碼。
    **V8 Engine**: Developed by Google, it parses and executes JS code. It is single-threaded, meaning only one piece of JS code can run at a time.
*   **libuv**: 一個跨平台的 C 語言函式庫，專注於非同步 I/O。它提供了 Event Loop 機制以及一個由 C++ 維護的 Thread Pool（預設 4 個執行緒）。
    **libuv**: A cross-platform C library focused on asynchronous I/O. It provides the Event Loop mechanism and a C++ maintained Thread Pool (default size of 4).

**心智模型 (Mental Model)**：
想像 Node.js 是一間**餐廳**。
*   **V8 (Main Thread)** 是唯一的**服務生**。他負責接單（接收請求）和上菜（回傳回應），但他不做菜。
*   **libuv (Worker Pool)** 是**廚房**。這裡有多位廚師（Threads）負責處理耗時的任務（如檔案讀寫、加密運算）。
*   **Event Loop** 是**出餐口與排程系統**。服務生不斷檢查這裡是否有做好的菜（Completed I/O callbacks）需要端給客人。

**Mental Model**:
Imagine Node.js as a **Restaurant**.
*   **V8 (Main Thread)** is the single **Waiter**. He takes orders (requests) and serves food (responses), but he doesn't cook.
*   **libuv (Worker Pool)** is the **Kitchen**. There are multiple chefs (Threads) handling time-consuming tasks (like file I/O, crypto operations).
*   **Event Loop** is the **Pass-through Window & Scheduling System**. The waiter constantly checks here for prepared dishes (Completed I/O callbacks) to serve to customers.

## 2.2 Event Loop 的六個階段 (The Six Phases of the Event Loop)

這是資深工程師必須記住的細節。Event Loop 執行時會依序經過以下階段，每個階段都有自己的 Callback Queue（FIFO）。

This is a detail senior engineers must memorize. The Event Loop cycles through the following phases, each having its own Callback Queue (FIFO).

1.  **Timers**: 執行 `setTimeout()` 和 `setInterval()` 的 callback。
    **Timers**: Executes callbacks from `setTimeout()` and `setInterval()`.
2.  **Pending Callbacks**: 執行延遲到下一個迴圈迭代的 I/O callback（通常是系統級錯誤，如 TCP socket 錯誤）。
    **Pending Callbacks**: Executes I/O callbacks deferred to the next loop iteration (usually system-level errors, like TCP socket errors).
3.  **Idle, Prepare**: 僅供內部使用。
    **Idle, Prepare**: Used internally only.
4.  **Poll**: 檢索新的 I/O 事件；執行與 I/O 相關的 callback（除了 timers, close callbacks, setImmediate 之外幾乎都在這）。這是 Node.js 最常停留的階段。
    **Poll**: Retrieve new I/O events; execute I/O related callbacks (almost everything except timers, close callbacks, and setImmediate). This is where Node.js spends most of its time.
5.  **Check**: 執行 `setImmediate()` 的 callback。
    **Check**: Executes `setImmediate()` callbacks.
6.  **Close Callbacks**: 執行關閉資源的 callback，例如 `socket.on('close', ...)`。
    **Close Callbacks**: Executes close callbacks, e.g., `socket.on('close', ...)`.

## 2.3 微任務與巨集任務 (Microtasks vs. Macrotasks)

這是在上述階段之外的另一個維度。

This is another dimension outside the phases mentioned above.

*   **Macrotasks (巨集任務)**: 上述各個階段 Queue 中的 callback（如 `setTimeout`, I/O callback）。
    **Macrotasks**: Callbacks in the queues of the phases mentioned above (e.g., `setTimeout`, I/O callbacks).
*   **Microtasks (微任務)**: 包含 `process.nextTick` 和 `Promise` (then/catch/finally)。
    **Microtasks**: Includes `process.nextTick` and `Promise` (then/catch/finally).

**關鍵規則 (Critical Rule)**：
Microtasks 的優先級**高於** Event Loop 的各個階段。每當一個階段完成，或者甚至在某些操作之間，Node.js 會清空 Microtask Queue。其中，`process.nextTick` 優先級又高於 `Promise`。

**Critical Rule**:
Microtasks have **higher** priority than the Event Loop phases. Whenever a phase completes, or even between certain operations, Node.js drains the Microtask Queue. Within this, `process.nextTick` has higher priority than `Promise`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 為什麼這對 System Design 很重要？ (Why is this crucial for System Design?)

在設計高吞吐量（High Throughput）系統時，Node.js 常被用作 **BFF (Backend for Frontend)** 或 **API Gateway**。

When designing high-throughput systems, Node.js is often used as a **BFF (Backend for Frontend)** or **API Gateway**.

*   **優勢 (Pros)**: 由於 Event Loop 的非阻塞特性，Node.js 能以極低的記憶體消耗處理數萬個併發連線（Concurrent Connections），只要這些連線主要是在等待 I/O（Wait time）。
    **Pros**: Due to the non-blocking nature of the Event Loop, Node.js can handle tens of thousands of concurrent connections with very low memory footprint, provided these connections are mostly waiting for I/O.
*   **風險 (Cons)**: 如果你在 Main Thread 執行了 CPU 密集型任務（例如：複雜的 JSON parsing、大迴圈計算、同步加密），整個 Event Loop 就會停擺。這就是所謂的 **Event Loop Blocking**。
    **Cons**: If you execute CPU-intensive tasks (e.g., complex JSON parsing, large loop calculations, synchronous crypto) on the Main Thread, the entire Event Loop halts. This is known as **Event Loop Blocking**.

## 3.2 可觀測性指標：Event Loop Lag (Observability Metric: Event Loop Lag)

在 Production 環境中，CPU 使用率低並不代表系統健康。如果 Event Loop Lag 很高，代表 callback 堆積嚴重，使用者感受到的延遲會很高。

In a production environment, low CPU usage does not guarantee system health. If Event Loop Lag is high, it means callbacks are piling up, and the latency perceived by users will be high.

*   **監控重點**: 使用 APM 工具（如 Datadog, New Relic）或 `perf_hooks` 監控 Event Loop Lag。
    **Monitoring Focus**: Use APM tools (like Datadog, New Relic) or `perf_hooks` to monitor Event Loop Lag.
*   **健康標準**: 一般建議 Lag 應保持在 10ms–20ms 以下。如果持續超過 100ms，系統就需要優化或擴容。
    **Health Standard**: It is generally recommended to keep Lag under 10ms–20ms. If it consistently exceeds 100ms, the system needs optimization or scaling.

---

# 4. 逐步示例 (Walkthrough / Example)

讓我們透過一段程式碼來驗證執行順序，這是面試與除錯的經典場景。

Let's verify the execution order through a piece of code, a classic scenario for interviews and debugging.

## 4.1 程式碼挑戰 (The Code Challenge)

```javascript
const fs = require('fs');

console.log('1. Start');

// Macrotask: Timer
setTimeout(() => {
  console.log('2. setTimeout 0ms');
}, 0);

// Macrotask: Check Phase
setImmediate(() => {
  console.log('3. setImmediate');
});

// Microtask: Promise
Promise.resolve().then(() => {
  console.log('4. Promise');
});

// Microtask: nextTick
process.nextTick(() => {
  console.log('5. nextTick');
});

// I/O Operation
fs.readFile(__filename, () => {
  console.log('6. File Read I/O');
  
  // Nested Timer
  setTimeout(() => {
    console.log('7. Inner setTimeout');
  }, 0);
  
  // Nested Immediate
  setImmediate(() => {
    console.log('8. Inner setImmediate');
  });
  
  // Nested nextTick
  process.nextTick(() => {
    console.log('9. Inner nextTick');
  });
});

console.log('10. End');
```

## 4.2 執行結果與分析 (Execution Result & Analysis)

**預期輸出 (Expected Output):**

```text
1. Start
10. End
5. nextTick
4. Promise
2. setTimeout 0ms
3. setImmediate
6. File Read I/O
9. Inner nextTick
8. Inner setImmediate
7. Inner setTimeout
```

*(註：第 2 點與第 3 點的順序在 Main Module 中是不保證的，但在 I/O callback 內部是固定的。稍後解釋。)*
*(Note: The order of #2 and #3 is not guaranteed in the Main Module, but is deterministic inside an I/O callback. Explained below.)*

**逐步解析 (Step-by-Step Breakdown):**

1.  **Sync Code**: `1. Start` 和 `10. End` 是同步執行的，首先被印出。
    **Sync Code**: `1. Start` and `10. End` are executed synchronously and printed first.

2.  **Microtasks Phase**: 同步代碼執行完畢後，V8 檢查 Microtask Queue。
    **Microtasks Phase**: After sync code finishes, V8 checks the Microtask Queue.
    *   `process.nextTick` 優先級最高 -> `5. nextTick`。
    *   接著是 Promise -> `4. Promise`。

3.  **Event Loop Start**: 進入 Loop。
    **Event Loop Start**: Enters the Loop.
    *   **Timers Phase**: 檢查是否有過期的 Timer。`setTimeout(..., 0)` 通常已過期 -> `2. setTimeout 0ms`。
    *   **Poll Phase**: 檢查 I/O。此時 `fs.readFile` 可能還沒完成（取決於硬碟速度）。如果沒完成，Loop 繼續往下。
    *   **Check Phase**: 執行 `3. setImmediate`。

    *(注意：在 Main Module 中，Timer 和 Check 的順序取決於 Process 啟動的效能雜訊，有時 `setImmediate` 會先跑。但在 I/O callback 內，`setImmediate` 總是先於 `setTimeout`。)*
    *(Note: In the Main Module, the order of Timer and Check depends on process startup performance noise; sometimes `setImmediate` runs first. However, inside an I/O callback, `setImmediate` always runs before `setTimeout`.)*

4.  **I/O Callback Execution**: 當檔案讀取完成，Event Loop 在 **Poll Phase** 執行 `fs.readFile` 的 callback -> `6. File Read I/O`。
    **I/O Callback Execution**: When file reading completes, the Event Loop executes the `fs.readFile` callback in the **Poll Phase** -> `6. File Read I/O`.

5.  **Inside I/O Callback**:
    *   註冊了 Inner Timer, Inner Immediate, Inner nextTick。
    *   Callback 結束後，立刻清空 Microtasks -> `9. Inner nextTick`。
    *   **關鍵點 (Key Point)**: 目前處於 **Poll Phase**。Poll 結束後，下一個階段是 **Check Phase**。
    *   因此，`8. Inner setImmediate` 必定先執行。
    *   下一輪 Loop 回到 **Timers Phase**，才執行 `7. Inner setTimeout`。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `process.nextTick` 導致 I/O 飢餓 (Starvation by `process.nextTick`)

**錯誤案例 (Anti-pattern)**:
遞迴調用 `process.nextTick`。

**Anti-pattern**:
Recursively calling `process.nextTick`.

```javascript
function compute() {
  // ... heavy logic ...
  process.nextTick(compute); // DANGER
}
compute();
```

**後果 (Consequence)**:
由於 `nextTick` 會在進入下一個 Event Loop 階段前被清空，如果不斷產生新的 `nextTick`，Event Loop 將永遠無法進入 **Poll Phase** 處理 I/O。伺服器將無法回應任何請求。

**Consequence**:
Since `nextTick` is drained before entering the next Event Loop phase, if new `nextTick` tasks are continuously generated, the Event Loop will never enter the **Poll Phase** to handle I/O. The server will become unresponsive.

**修正 (Fix)**:
使用 `setImmediate`，它允許 Event Loop 跑完一圈（包含 I/O）後再執行下一次任務。

**Fix**:
Use `setImmediate`, which allows the Event Loop to complete a full cycle (including I/O) before executing the next task.

## 5.2 執行緒池耗盡 (Thread Pool Exhaustion)

**錯誤案例 (Anti-pattern)**:
預設 libuv Thread Pool 大小為 4。如果你同時發起 10 個涉及 DNS 查詢（`dns.lookup`）或檔案操作的請求，其中 4 個慢速請求會阻塞剩下的 6 個請求，即使那 6 個請求很快。

**Anti-pattern**:
The default libuv Thread Pool size is 4. If you initiate 10 requests involving DNS lookups (`dns.lookup`) or file operations simultaneously, 4 slow requests will block the remaining 6, even if those 6 are fast.

**修正 (Fix)**:
在啟動應用程式時，透過環境變數調整 Pool Size：`UV_THREADPOOL_SIZE=64 node app.js`。這對於大量使用 `crypto` (pbkdf2) 或 `fs` 的應用特別重要。

**Fix**:
Adjust the Pool Size via environment variables when starting the app: `UV_THREADPOOL_SIZE=64 node app.js`. This is especially important for apps heavily using `crypto` (pbkdf2) or `fs`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試 Senior 候選人，或在團隊內進行技術分享。

These questions can be used to interview Senior candidates or for technical sharing within the team.

## Q1: `setImmediate` 與 `setTimeout(() => {}, 0)` 有何不同？
**Q1: What is the difference between `setImmediate` and `setTimeout(() => {}, 0)`?**

*   **高分回答要點**:
    *   **階段不同**: `setTimeout` 在 Timers 階段；`setImmediate` 在 Check 階段。
    *   **I/O 上下文**: 在 I/O callback 中（如 `fs.readFile`），`setImmediate` 總是比 `setTimeout` 先執行，因為 Poll 階段之後緊接著是 Check 階段。
    *   **非 I/O 上下文**: 在主模組（Main Module）中，兩者順序不確定（受 process 啟動效能影響）。

## Q2: Node.js 是單執行緒的，那它是如何處理併發檔案讀取的？
**Q2: Since Node.js is single-threaded, how does it handle concurrent file reads?**

*   **高分回答要點**:
    *   區分 **Main Thread (V8)** 與 **Thread Pool (libuv)**。
    *   JS 執行緒只負責發起調用。
    *   實際的檔案系統操作（File System Operations）是由 libuv 分派給 C++ Thread Pool 中的執行緒去做的（因為 `fs` API 是阻塞的 OS call）。
    *   完成後，libuv 將 callback 放回 Event Loop 的 Poll Queue 等待 Main Thread 執行。

## Q3: 如何在不使用 Cluster 模組的情況下，避免單一重型請求卡死整個 Node.js 伺服器？
**Q3: How do you prevent a single heavy request from freezing the entire Node.js server without using the Cluster module?**

*   **高分回答要點**:
    *   **Partitioning (切分)**: 將大任務切分成小塊，使用 `setImmediate` 在每塊處理完後釋放控制權給 Event Loop。
    *   **Offloading (卸載)**: 使用 `Worker Threads`（Node.js v10+）將 CPU 密集型任務移出 Main Thread。
    *   **區別**: Cluster 是多 Process（記憶體不共享），Worker Threads 是多 Thread（記憶體共享，更輕量）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **V8 vs libuv**: V8 跑 JS，libuv 跑 I/O 和 Event Loop。
2.  **Phase Order**: Timers -> Pending -> Poll -> Check -> Close。
3.  **Microtasks Priority**: `process.nextTick` > `Promise` > Event Loop Phases。
4.  **Poll to Check**: 在 I/O callback 內，`setImmediate` 永遠快於 `setTimeout`。
5.  **Blocking**: 不要阻塞 Main Thread，善用 `UV_THREADPOOL_SIZE` 和 Worker Threads。

## 後續延伸 (Next Steps)
*   **Chapter 02**: **Streams & Buffers**。既然理解了非同步原理，下一步應學習如何高效處理資料流，避免將整個檔案載入記憶體（Memory Pressure）。
*   **Action Item**: 在你的專案中加入 Event Loop Lag 的監控，觀察系統在高負載下的表現。