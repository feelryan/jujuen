# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，JavaScript 的非同步模型不僅僅是知道如何使用 `async/await` 或 `setTimeout`。在設計高併發（High Concurrency）系統或處理複雜的前端狀態時，深刻理解 Event Loop 的調度順序是避免效能瓶頸（Performance Bottlenecks）與競爭條件（Race Conditions）的關鍵。

For senior engineers, the JavaScript asynchronous model is about more than just knowing how to use `async/await` or `setTimeout`. When designing high-concurrency systems or handling complex frontend states, a deep understanding of the Event Loop scheduling order is crucial for avoiding performance bottlenecks and race conditions.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準預測執行順序**：在混合使用 `setTimeout`、`Promise`、`process.nextTick` 與 `requestAnimationFrame` 的複雜場景中，準確判斷程式碼的執行順序。
    **Accurately predict execution order**: Correctly determine the execution sequence in complex scenarios mixing `setTimeout`, `Promise`, `process.nextTick`, and `requestAnimationFrame`.
2.  **診斷 Event Loop 阻塞**：識別導致 Event Loop Lag（延遲）的程式碼模式（如大型 JSON 解析或同步計算），並提出優化方案。
    **Diagnose Event Loop blocking**: Identify code patterns that cause Event Loop Lag (such as large JSON parsing or synchronous computations) and propose optimization strategies.
3.  **區分環境差異**：清楚解釋 Node.js 與 瀏覽器（Browser）在 Event Loop 實作上的關鍵差異（特別是 Microtask 的處理時機）。
    **Distinguish environmental differences**: Clearly explain the key differences in Event Loop implementation between Node.js and Browsers (especially regarding Microtask processing timing).
4.  **掌握非同步設計模式**：理解 `Promise` 的內部狀態機轉換，並能手寫 Polyfill 或設計並發控制（Concurrency Control）工具。
    **Master asynchronous design patterns**: Understand the internal state machine transitions of `Promise` and be able to write Polyfills or design concurrency control tools.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 單執行緒與非阻塞 I/O (Single Threaded & Non-blocking I/O)

JavaScript 引擎（如 V8）本身是單執行緒的，這意味著同一時間只能執行一段程式碼。然而，JavaScript 的執行環境（Runtime，如 Browser 或 Node.js）提供了 Web APIs（或 C++ APIs），讓我們能以非阻塞的方式處理 I/O。

The JavaScript engine (like V8) itself is single-threaded, meaning only one piece of code can execute at a time. However, the JavaScript runtime environment (such as the Browser or Node.js) provides Web APIs (or C++ APIs) that allow us to handle I/O in a non-blocking manner.

**心智模型 (Mental Model)**：
想像一家餐廳只有**一位廚師（Call Stack）**。
- **同步任務（Synchronous Tasks）**：像是切菜、擺盤，廚師必須親手立刻做完。
- **非同步任務（Asynchronous Tasks）**：像是烤箱烤雞（Network Request/Timer）。廚師把雞放入烤箱後，就去處理下一張單，不會站在烤箱前等。
- **Event Loop**：這是負責監控的「外場經理」。當烤箱響了（Task 完成），經理會把處理好的雞放入**出餐區（Callback Queue）**。一旦廚師手邊沒事了（Stack Empty），經理就會把出餐區的任務遞給廚師。

**Mental Model**:
Imagine a restaurant with only **one chef (Call Stack)**.
- **Synchronous Tasks**: Like chopping vegetables or plating, the chef must do these immediately and personally.
- **Asynchronous Tasks**: Like roasting a chicken in the oven (Network Request/Timer). The chef puts the chicken in the oven and moves to the next order, not waiting in front of the oven.
- **Event Loop**: This is the "Manager". When the oven dings (Task complete), the manager puts the finished chicken in the **Service Area (Callback Queue)**. Once the chef is idle (Stack Empty), the manager hands the task from the service area to the chef.

## 2.2 Macrotasks vs. Microtasks (宏任務與微任務)

這是資深面試中最常考的細節。並非所有的非同步任務優先級都相同。

This is the most common detail tested in senior interviews. Not all asynchronous tasks have the same priority.

1.  **Macrotasks (Task Queue)**: `setTimeout`, `setInterval`, `setImmediate` (Node), I/O events, UI rendering.
2.  **Microtasks (Job Queue)**: `Promise.then/catch/finally`, `process.nextTick` (Node), `MutationObserver`.

**關鍵規則 (The Golden Rule)**：
**在每一個 Macrotask 執行完畢後，Event Loop 會清空「所有的」Microtasks，然後才進行畫面渲染（Browser）或執行下一個 Macrotask。**

**The Golden Rule**:
**After each Macrotask completes, the Event Loop drains "ALL" Microtasks before performing UI rendering (Browser) or executing the next Macrotask.**

> **注意 (Note)**: 這意味著如果你在 Microtask 中不斷遞迴產生新的 Microtask，將會導致無限迴圈並阻塞 Macrotask（如 UI 更新或 Timer），造成頁面凍結。
>
> **Note**: This means if you recursively generate new Microtasks within a Microtask, you will cause an infinite loop that blocks Macrotasks (like UI updates or Timers), resulting in a frozen page.

## 2.3 Async/Await 的本質 (The Essence of Async/Await)

`async/await` 只是 Generator 與 Promise 的語法糖（Syntactic Sugar）。
`await` 關鍵字後面的表達式會被執行，而 `await` 下方的程式碼本質上都被放入了 `Promise.then()` 的 callback 中，也就是說它們會被視為 **Microtask**。

`async/await` is merely syntactic sugar for Generators and Promises.
The expression following the `await` keyword is executed, and the code *below* the `await` is essentially wrapped into a `Promise.then()` callback, meaning it is treated as a **Microtask**.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 Node.js 高併發服務 (High Concurrency Node.js Services)

在設計 Node.js 後端時，Event Loop 的健康狀況直接決定了系統的 Throughput（吞吐量）與 Latency（延遲）。

When designing Node.js backends, the health of the Event Loop directly dictates the system's Throughput and Latency.

-   **Event Loop Lag**: 這是一個關鍵的可觀測性指標（Observability Metric）。如果 Event Loop Lag 很高，代表有同步程式碼佔用了 CPU 太久。
-   **架構影響**: 由於 JavaScript 是單執行緒，**不要在主執行緒進行 CPU 密集型運算**（如加密、影像處理、極大陣列遍歷）。
-   **解決方案**:
    -   **Worker Threads**: 利用 Node.js 的 Worker Threads 模組處理 CPU 密集任務。
    -   **Offloading**: 將繁重計算卸載到 Serverless Functions (AWS Lambda) 或專門的運算服務。

-   **Event Loop Lag**: This is a critical Observability Metric. High Event Loop Lag indicates that synchronous code is hogging the CPU for too long.
-   **Architectural Impact**: Since JavaScript is single-threaded, **do not perform CPU-intensive operations on the main thread** (e.g., encryption, image processing, traversing massive arrays).
-   **Solutions**:
    -   **Worker Threads**: Use Node.js Worker Threads module for CPU-bound tasks.
    -   **Offloading**: Offload heavy computations to Serverless Functions (AWS Lambda) or dedicated compute services.

## 3.2 批次處理與防抖 (Batching & Debouncing)

利用 Microtask 的特性（在本輪 Call Stack 結束後、下一輪 Macrotask 前執行），我們可以實作高效的批次處理。例如，React 的狀態更新（Batch Update）或是 Vue 的 `nextTick` 機制，都是利用 Microtask 來合併多次 DOM 操作，避免不必要的 Layout Thrashing（佈局抖動）。

Leveraging the nature of Microtasks (executing after the current Call Stack and before the next Macrotask), we can implement efficient batching. For example, React's state Batch Updates or Vue's `nextTick` mechanism utilize Microtasks to coalesce multiple DOM operations, avoiding unnecessary Layout Thrashing.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 經典面試題：預測輸出順序 (Classic Interview Question: Predicting Output)

這是一個經典的題目，用來測試對 Microtask/Macrotask 優先級的理解。

This is a classic question used to test understanding of Microtask/Macrotask priorities.

```javascript
console.log('1: Script Start');

setTimeout(() => {
  console.log('2: setTimeout');
}, 0);

Promise.resolve()
  .then(() => {
    console.log('3: Promise 1');
  })
  .then(() => {
    console.log('4: Promise 2');
  });

async function asyncFunc() {
  console.log('5: Async Start');
  await Promise.resolve(); // Suspends execution, rest goes to Microtask
  console.log('6: Async End');
}

asyncFunc();

console.log('7: Script End');
```

**思考步驟 (Thinking Steps)**:

1.  **同步程式碼 (Sync Code)**:
    -   `'1: Script Start'` 立即執行。
    -   `setTimeout` 被註冊，callback 進入 **Macrotask Queue**。
    -   `Promise.resolve().then(...)` 註冊 callback，進入 **Microtask Queue**。
    -   呼叫 `asyncFunc()`：
        -   `'5: Async Start'` 立即執行。
        -   遇到 `await`，函式暫停，剩下的部分（`'6: Async End'`）被包裝並放入 **Microtask Queue**。
    -   `'7: Script End'` 立即執行。

2.  **清空 Microtasks (Drain Microtasks)**:
    -   Call Stack 空了。Event Loop 檢查 Microtask Queue。
    -   執行 `'3: Promise 1'`。這會產生新的 Microtask (`'4: Promise 2'`) 放入隊列尾端。
    -   執行 `'6: Async End'` (來自 asyncFunc 的後半段)。
    -   執行 `'4: Promise 2'`。

3.  **執行 Macrotasks (Execute Macrotasks)**:
    -   Microtasks 空了。Event Loop 檢查 Macrotask Queue。
    -   執行 `'2: setTimeout'`。

**正確輸出 (Correct Output)**:
`1, 5, 7, 3, 6, 4, 2` (註：3, 6, 4 的順序取決於 Promise 實作與 await 轉換的細微差異，但在現代環境通常是 FIFO)。

**Correct Output**:
`1, 5, 7, 3, 6, 4, 2` (Note: The order of 3, 6, 4 depends on subtle implementation details of Promise and await transpilation, but it is typically FIFO in modern environments).

## 4.2 實務案例：並發控制 (Real-World: Concurrency Control)

在處理大量 API 請求時，我們不能一次發出 1000 個請求（會導致 OOM 或被封鎖）。我們需要一個並發限制器。這展示了如何利用 Promise 控制流程。

When handling a large number of API requests, we cannot fire 1000 requests at once (causing OOM or getting blocked). We need a concurrency limiter. This demonstrates how to use Promises for flow control.

```javascript
async function asyncPool(poolLimit, array, iteratorFn) {
  const ret = []; // Stores all promises
  const executing = []; // Stores currently executing promises

  for (const item of array) {
    // Wrap the iterator function in a promise
    const p = Promise.resolve().then(() => iteratorFn(item));
    ret.push(p);

    if (poolLimit <= array.length) {
      // Create a promise that removes itself from 'executing' when done
      const e = p.then(() => executing.splice(executing.indexOf(e), 1));
      executing.push(e);

      // If pool is full, wait for the fastest one to finish (Promise.race)
      if (executing.length >= poolLimit) {
        await Promise.race(executing);
      }
    }
  }
  return Promise.all(ret);
}
```

**為何這個做法可行？ (Why this works?)**
利用 `await Promise.race(executing)`，我們有效地「暫停」了 `for` 迴圈的推進，直到 `executing` 陣列中有任何一個 Promise 完成並釋出空間。這是利用 Event Loop 非阻塞特性的高階應用。

By using `await Promise.race(executing)`, we effectively "pause" the progress of the `for` loop until any Promise in the `executing` array resolves and frees up a slot. This is an advanced application leveraging the non-blocking nature of the Event Loop.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在迴圈中序列執行 `await` (Serial `await` in Loops)

**錯誤案例 (Anti-pattern)**:
```javascript
// Slow! Requests run one after another
for (const id of userIds) {
  const user = await fetchUser(id);
  results.push(user);
}
```

**為何不好 (Why it's bad)**:
這會強迫非同步操作變成「序列（Sequential）」執行，浪費了並行處理的能力，大幅增加總執行時間。

This forces asynchronous operations to execute "sequentially," wasting the capability for parallel processing and significantly increasing total execution time.

**修正方案 (Better Approach)**:
使用 `Promise.all` 進行並行處理（Parallelism）。
Use `Promise.all` for parallelism.
```javascript
const promises = userIds.map(id => fetchUser(id));
const results = await Promise.all(promises);
```

## 5.2 混用 Callback 與 Promise (Mixing Callbacks and Promises)

**錯誤案例 (Anti-pattern)**:
```javascript
function getData(callback) {
  fetch('/api').then(res => {
    callback(null, res);
  }).catch(err => {
    // If callback throws, who catches it?
    callback(err); 
  });
}
```

**為何不好 (Why it's bad)**:
如果 `callback` 內部拋出錯誤，這個錯誤會被 Promise 的 `catch` 再次捕捉（如果 callback 在 then 裡面被呼叫），或者變成 Unhandled Exception，導致流程難以預測且難以除錯。

If `callback` throws an error internally, that error might be caught again by the Promise's `catch` (if called within then), or become an Unhandled Exception, making the flow unpredictable and hard to debug.

## 5.3 餓死 Macrotask (Starving Macrotasks)

**錯誤案例 (Anti-pattern)**:
```javascript
function processHugeData() {
  return Promise.resolve().then(() => {
    // Heavy computation
    doSomething(); 
    // Recursively schedule next microtask
    return processHugeData(); 
  });
}
```

**為何不好 (Why it's bad)**:
由於 Microtasks 會在下一個 Macrotask 之前**完全清空**，這種遞迴的 Microtask 會完全佔用 Event Loop，導致 `setTimeout`、點擊事件或 I/O callback 永遠無法執行（Starvation）。

Since Microtasks are **completely drained** before the next Macrotask, this recursive Microtask pattern will monopolize the Event Loop, causing `setTimeout`, click events, or I/O callbacks to never execute (Starvation).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: Node.js 的 `process.nextTick` 與 `setImmediate` 有何不同？
**Q1: What is the difference between `process.nextTick` and `setImmediate` in Node.js?**

*   **高分回答要點 (Key Points)**:
    *   `process.nextTick` 實際上不是 Event Loop 的一部分，它有一個獨立的 `nextTickQueue`。它會在當前操作完成後、**任何**其他 Event Loop 階段（包含 Microtasks）之前立即執行。優先級最高。
    *   `setImmediate` 屬於 Event Loop 的 `Check` 階段，通常在 I/O 階段之後執行。
    *   使用 `nextTick` 需謹慎，容易造成 I/O Starvation。

*   **Key Points**:
    *   `process.nextTick` is technically not part of the Event Loop; it has its own `nextTickQueue`. It runs immediately after the current operation completes and before **any** other Event Loop phase (including Microtasks). It has the highest priority.
    *   `setImmediate` belongs to the `Check` phase of the Event Loop, typically running after the I/O phase.
    *   Use `nextTick` with caution as it can easily cause I/O Starvation.

## Q2: 如何在不使用 Worker Threads 的情況下，避免大型運算阻塞 Event Loop？
**Q2: How can you avoid blocking the Event Loop with heavy computations without using Worker Threads?**

*   **高分回答要點 (Key Points)**:
    *   **Partitioning (分割)**: 將大型運算拆解成多個小塊（Chunks）。
    *   **Scheduling (排程)**: 使用 `setImmediate` (Node) 或 `setTimeout` (Browser) 在處理完每個小塊後讓出控制權（Yielding to the Event Loop）。這允許 Event Loop 在處理下一個小塊前，有機會處理其他 I/O 或渲染任務。

*   **Key Points**:
    *   **Partitioning**: Break the heavy computation into smaller chunks.
    *   **Scheduling**: Use `setImmediate` (Node) or `setTimeout` (Browser) to yield control after processing each chunk. This allows the Event Loop to handle other I/O or rendering tasks before processing the next chunk.

## Q3: 為什麼 `setTimeout(fn, 0)` 不保證在 0ms 後執行？
**Q3: Why is `setTimeout(fn, 0)` not guaranteed to execute after 0ms?**

*   **高分回答要點 (Key Points)**:
    *   **Minimum Delay**: 瀏覽器規範通常有最小延遲（如 4ms，特別是在巢狀計時器中）。
    *   **Call Stack Occupancy**: 必須等待 Call Stack 清空。
    *   **Microtask Queue**: 必須等待所有 Microtasks 執行完畢。
    *   因此，`setTimeout` 指定的是「最小延遲時間」，而非「確切執行時間」。

*   **Key Points**:
    *   **Minimum Delay**: Browser specs often mandate a minimum delay (e.g., 4ms, especially for nested timers).
    *   **Call Stack Occupancy**: It must wait for the Call Stack to clear.
    *   **Microtask Queue**: It must wait for all Microtasks to drain.
    *   Therefore, `setTimeout` specifies the "minimum delay", not the "exact execution time".

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Call Stack First**: 同步程式碼永遠最先執行。
2.  **Micro > Macro**: Microtasks (`Promise`, `nextTick`) 優先級高於 Macrotasks (`setTimeout`, I/O)。
3.  **Run to Completion**: 單個 Task 一旦開始執行，除非遇到 `await` 或結束，否則不會被中斷。
4.  **Drain the Queue**: Microtask Queue 會在每個 Macrotask 結束後被**清空**，這可能導致阻塞。
5.  **Node vs Browser**: 現代 Node.js (v11+) 的行為已與瀏覽器趨於一致，但在 `nextTick` 和 `setImmediate` 上仍有特殊機制。

## 後續延伸 (Next Steps)
-   **深入 V8 引擎**: 研究 V8 的 Garbage Collection (GC) 機制，了解非同步物件如何被回收。
-   **Reactive Programming**: 學習 RxJS，這是基於 Event Loop 與 Observer Pattern 的進階非同步處理庫。
-   **下一章預告**: **Chapter 03: Memory Management & Performance Profiling** (記憶體管理與效能分析)。