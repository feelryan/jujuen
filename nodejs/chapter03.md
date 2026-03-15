# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Node.js 的記憶體管理往往是一個「平時不可見，出事即災難」的領域。理解 V8 引擎如何回收記憶體（Garbage Collection），以及如何利用 Stream 處理大規模數據，是從「寫出能跑的程式」進階到「建構高吞吐、高穩定系統」的關鍵分水嶺。

For senior engineers, Node.js memory management is often a domain that remains "invisible until disaster strikes." Understanding how the V8 engine reclaims memory (Garbage Collection) and how to leverage Streams for large-scale data processing is the critical watershed moment between "writing code that works" and "architecting high-throughput, highly stable systems."

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深入理解 V8 GC 機制**：解釋 New Space 與 Old Space 的差異，以及 Scavenge 與 Mark-Sweep/Mark-Compact 演算法如何影響應用程式效能。
    **Deeply understand V8 GC mechanisms**: Explain the difference between New Space and Old Space, and how Scavenge and Mark-Sweep/Mark-Compact algorithms impact application performance.
2.  **排查記憶體洩漏 (Memory Leaks)**：熟練使用 Heap Snapshots 與 Chrome DevTools (或類似工具) 定位洩漏源，特別是針對 Closure 與 Event Emitters 造成的隱性洩漏。
    **Debug Memory Leaks**: Proficiently use Heap Snapshots and Chrome DevTools (or similar tools) to pinpoint leak sources, specifically targeting implicit leaks caused by Closures and Event Emitters.
3.  **掌握 Stream 與 Backpressure**：在不爆記憶體的情況下處理 GB 級別的檔案或數據流，並能手動實作 Backpressure 機制以防止系統過載。
    **Master Streams & Backpressure**: Process GB-scale files or data streams without blowing up memory, and manually implement Backpressure mechanisms to prevent system overload.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 V8 記憶體結構 (V8 Memory Structure)

Node.js 的記憶體管理基於 V8 引擎。我們可以將 Heap Memory 想像成一個「分代管理的倉庫」。
Node.js memory management is based on the V8 engine. We can visualize Heap Memory as a "generationally managed warehouse."

*   **New Space (Young Generation)**:
    *   **概念**：存放生命週期短的物件（如函式內的區域變數）。空間小（通常 16MB - 64MB），回收頻繁。
    *   **Concept**: Stores short-lived objects (like local variables within functions). Small space (usually 16MB - 64MB), frequently collected.
    *   **演算法 (Algorithm)**: **Scavenge**. 使用 Cheney 演算法，將存活物件在兩個 Semispace (From-Space, To-Space) 之間複製。速度極快，但受限於空間。
    *   **Algorithm**: **Scavenge**. Uses Cheney's algorithm to copy surviving objects between two Semispaces (From-Space, To-Space). Extremely fast but space-limited.

*   **Old Space (Old Generation)**:
    *   **概念**：存放經歷過多次 Scavenge 仍存活的物件（如全域快取、長期連線 Session）。空間大，回收成本高。
    *   **Concept**: Stores objects that have survived multiple Scavenge cycles (like global caches, long-term connection sessions). Large space, high collection cost.
    *   **演算法 (Algorithm)**: **Mark-Sweep & Mark-Compact**.
        *   *Mark*: 標記所有可達物件 (Reachable objects)。
        *   *Sweep*: 清除未標記的記憶體位址。
        *   *Compact*: 重組記憶體以減少碎片化 (Fragmentation)。這會導致 "Stop-The-World" (雖然 V8 已優化為 Incremental Marking，但仍有 CPU 開銷)。

## 2.2 Stream 與 Backpressure (Stream & Backpressure)

**心智模型：水管與水箱 (The Pipe and Tank Analogy)**
**Mental Model: The Pipe and Tank Analogy**

*   **Stream**: 就像水管，數據是流動的，不需要一次全部裝進水箱（記憶體）。
    **Stream**: Like a pipe, data flows through it; you don't need to fit it all into the tank (memory) at once.
*   **Backpressure (背壓)**: 這是流體力學的概念。當出水口（Writable Stream，如寫入硬碟）比進水口（Readable Stream，如讀取網路請求）慢時，水管會積壓。如果沒有機制告訴進水口「慢一點」，系統就會崩潰（OOM）。
    **Backpressure**: A concept from fluid dynamics. When the drain (Writable Stream, e.g., writing to disk) is slower than the faucet (Readable Stream, e.g., reading network requests), pressure builds up. Without a mechanism to tell the source to "slow down," the system crashes (OOM).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，Node.js 常被用作 BFF (Backend for Frontend) 或 I/O 密集型的微服務。記憶體管理直接影響**成本 (Cost)** 與 **可用性 (Availability)**。

In large distributed systems, Node.js is often used as a BFF (Backend for Frontend) or an I/O-intensive microservice. Memory management directly impacts **Cost** and **Availability**.

## 3.1 典型場景 (Typical Scenarios)

1.  **ETL / 檔案處理服務 (File Processing Service)**:
    *   使用者上傳 2GB 的 CSV 進行匯入。
    *   **錯誤做法**：`fs.readFile` 全部讀入 RAM。導致 Concurrent requests 增加時，Pod 頻繁 OOM 重啟。
    *   **正確做法**：使用 `Stream` 逐行讀取、轉換、寫入 DB。記憶體使用量維持在 50MB 以內，與檔案大小無關。
    *   **User uploads a 2GB CSV for import.**
    *   **Wrong Approach**: `fs.readFile` loads everything into RAM. Causes frequent OOM restarts as concurrent requests increase.
    *   **Right Approach**: Use `Stream` to read line-by-line, transform, and write to DB. Memory usage stays under 50MB, independent of file size.

2.  **高併發長連線 (High Concurrency Long-lived Connections)**:
    *   WebSocket Server 或 Push Notification Service。
    *   每個連線物件若佔用過多 Closure 變數未釋放，會導致 Old Space 迅速填滿，觸發頻繁的 Full GC，造成 CPU 飆高與 Latency 抖動。
    *   WebSocket Server or Push Notification Service.
    *   If each connection object retains too many Closure variables without release, Old Space fills up quickly, triggering frequent Full GC, causing CPU spikes and Latency jitter.

## 3.2 對系統設計的影響 (Impact on System Design)

*   **可擴充性 (Scalability)**: 良好的 Stream 處理意味著單一 Node.js 實例可以處理吞吐量遠大於其 RAM 的任務，減少所需的 Container 數量。
    **Scalability**: Good Stream handling means a single Node.js instance can process throughput far larger than its RAM, reducing the number of Containers needed.
*   **可觀測性 (Observability)**: 必須監控 `process.memoryUsage().heapUsed` 和 `heapTotal`。若 Heap Used 呈現鋸齒狀上升且底部不斷墊高（Sawtooth pattern with rising floor），即為 Memory Leak 徵兆。
    **Observability**: Must monitor `process.memoryUsage().heapUsed` and `heapTotal`. If Heap Used shows a sawtooth pattern with a rising floor, it's a sign of a Memory Leak.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 實戰：排查 Memory Leak (Scenario: Hunting a Memory Leak)

假設我們有一個 API，每次請求都會稍微增加記憶體，最終導致 Crash。

Suppose we have an API where every request slightly increases memory usage, eventually leading to a crash.

### 1. 問題程式碼 (The Problematic Code)

```javascript
const express = require('express');
const app = express();

// 模擬一個全域快取，這是最常見的洩漏源
// Simulating a global cache, the most common source of leaks
const leakyCache = [];

app.get('/leak', (req, res) => {
  // 每次請求都創建一個大物件
  // Creating a large object on every request
  const largeObject = new Array(100000).fill('x');
  
  // 錯誤：將請求相關的資料推入全域陣列，且從未清理
  // MISTAKE: Pushing request-specific data to a global array without cleanup
  leakyCache.push({
    id: Date.now(),
    data: largeObject // Retained in Old Space
  });

  res.send('Leaked!');
});

app.listen(3000);
```

### 2. 排查步驟 (Debugging Steps)

1.  **重現 (Reproduce)**: 使用 `autocannon` 或 `Apache Bench` 對 `/leak` 進行壓力測試。
    **Reproduce**: Use `autocannon` or `Apache Bench` to stress test `/leak`.
2.  **觀察 (Observe)**: 啟動 Node 時加上 `--inspect` 參數。打開 Chrome `chrome://inspect`。
    **Observe**: Start Node with the `--inspect` flag. Open Chrome `chrome://inspect`.
3.  **快照 (Snapshot)**:
    *   在壓測前拍一張 **Heap Snapshot (Snapshot 1)**。
    *   壓測進行中拍一張 **Heap Snapshot (Snapshot 2)**。
    *   壓測結束後（手動觸發 GC 後）拍一張 **Heap Snapshot (Snapshot 3)**。
    *   Take a **Heap Snapshot (Snapshot 1)** before stress testing.
    *   Take a **Heap Snapshot (Snapshot 2)** during stress testing.
    *   Take a **Heap Snapshot (Snapshot 3)** after stress testing (and manually triggering GC).
4.  **比較 (Comparison)**:
    *   選擇 Snapshot 3，視圖切換為 "Comparison"，對比 Snapshot 1。
    *   Select Snapshot 3, switch view to "Comparison", and compare with Snapshot 1.
    *   按 **Delta** 排序。你會看到 `(array)` 或 `Object` 的數量大幅增加。
    *   Sort by **Delta**. You will see a massive increase in `(array)` or `Object`.
    *   展開該物件，查看 **Retainers** (誰引用了它)。你會發現 `leakyCache` 變數引用了這些物件。
    *   Expand the object and check **Retainers** (who is referencing it). You will find the `leakyCache` variable referencing these objects.

## 4.2 實戰：Stream 與 Backpressure 處理 (Scenario: Handling Stream & Backpressure)

目標：複製一個大檔案，但寫入速度慢於讀取速度（模擬網路傳輸）。

Goal: Copy a large file, but the write speed is slower than the read speed (simulating network transmission).

### 1. Naive Solution (Bad)

```javascript
// 這不是真正的 Stream 處理，只是把 Stream 當 Event Emitter 用
// This is not true Stream handling, just using Stream as an Event Emitter
readStream.on('data', (chunk) => {
  // 如果 writeStream 來不及寫入，記憶體會暴增
  // If writeStream cannot keep up, memory explodes
  writeStream.write(chunk); 
});
```

### 2. Robust Solution (Good)

最簡單的方式是使用 `.pipe()`，它內部自動處理了 Backpressure。但為了理解原理，我們看如何手動實作：

The simplest way is to use `.pipe()`, which handles Backpressure internally. But to understand the principle, let's see how to implement it manually:

```javascript
const fs = require('fs');

const readStream = fs.createReadStream('huge-file.txt');
const writeStream = fs.createWriteStream('output.txt');

readStream.on('data', (chunk) => {
  // write() 回傳 false 代表內部 buffer 已滿 (HighWaterMark reached)
  // write() returns false if the internal buffer is full (HighWaterMark reached)
  const canContinue = writeStream.write(chunk);
  
  if (!canContinue) {
    console.log('Backpressure detected! Pausing read stream.');
    // 暫停讀取，防止記憶體積壓
    // Pause reading to prevent memory buildup
    readStream.pause();
  }
});

// 當 writeStream 的 buffer 清空後，會觸發 'drain' 事件
// When writeStream's buffer drains, it emits the 'drain' event
writeStream.on('drain', () => {
  console.log('Buffer drained. Resuming read stream.');
  // 恢復讀取
  // Resume reading
  readStream.resume();
});

readStream.on('end', () => {
  writeStream.end();
});
```

**複雜度分析 (Complexity Analysis)**:
*   **空間複雜度 (Space Complexity)**: O(1)。記憶體使用量固定在 `highWaterMark` (預設 64KB) 附近，與檔案大小無關。
    **Space Complexity**: O(1). Memory usage is capped around `highWaterMark` (default 64KB), independent of file size.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用全域變數作為快取 (Abusing Global Variables as Cache)
*   **錯誤 (Pitfall)**: 使用 `const cache = {}` 儲存資料，卻沒有實作 TTL (Time-To-Live) 或大小限制。
    **Pitfall**: Using `const cache = {}` to store data without implementing TTL (Time-To-Live) or size limits.
*   **後果 (Consequence)**: 隨著時間推移，Old Space 被填滿，導致 OOM。
    **Consequence**: Over time, Old Space fills up, leading to OOM.
*   **解法 (Solution)**: 使用 `lru-cache` 等庫，或將快取移至外部服務 (Redis)。
    **Solution**: Use libraries like `lru-cache`, or move caching to an external service (Redis).

## 5.2 Closure 造成的隱性洩漏 (Implicit Leaks via Closures)
*   **錯誤 (Pitfall)**: 在 Closure 中意外引用了父層的大物件，即使該大物件不再被需要。
    **Pitfall**: Accidentally referencing a large parent object inside a Closure, even if that large object is no longer needed.
*   **範例 (Example)**:
    ```javascript
    const hugeData = new Array(1000000).join('*');
    // 這個 callback 引用了 hugeData，導致它無法被 GC
    // This callback references hugeData, preventing it from being GC'd
    setInterval(() => {
      console.log(hugeData.length); 
    }, 1000);
    ```

## 5.3 忽略 Event Emitter 的清理 (Ignoring Event Emitter Cleanup)
*   **錯誤 (Pitfall)**: 在 SPA (Single Page App) 的 SSR 端或長連線服務中，不斷對同一個 Singleton 物件 `on('event', fn)` 但從未 `off`。
    **Pitfall**: In SSR for SPAs or long-lived connection services, repeatedly calling `on('event', fn)` on a Singleton object but never calling `off`.
*   **後果 (Consequence)**: `listeners` 陣列無限增長。Node.js 預設超過 10 個 listener 會警告，但開發者常忽略。
    **Consequence**: The `listeners` array grows infinitely. Node.js warns after 10 listeners by default, but developers often ignore it.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試 Senior 候選人，或在團隊 Code Review 時討論。

These questions can be used to interview Senior candidates or during team Code Reviews.

## Q1: 請解釋 Node.js 中 `Buffer` 與 V8 Heap 的關係？
**Please explain the relationship between `Buffer` and V8 Heap in Node.js?**

*   **高分回答要點 (Key Points)**:
    *   `Buffer` 實例本身（JavaScript 物件殼層）在 V8 Heap 中。
    *   但實際儲存數據的記憶體是 **Off-Heap** (C++ 層面的記憶體)，不佔用 V8 的 Heap Size Limit。
    *   這意味著你可以操作比 `old_space_size` 更大的 Buffer，但仍需注意物理記憶體限制。
    *   *The `Buffer` instance itself (the JS object shell) is in the V8 Heap.*
    *   *But the actual memory storing data is **Off-Heap** (C++ level memory) and does not count towards the V8 Heap Size Limit.*
    *   *This means you can manipulate Buffers larger than `old_space_size`, but you still need to be aware of physical RAM limits.*

## Q2: 你如何在 Production 環境中監控並診斷 Memory Leak？
**How do you monitor and diagnose Memory Leaks in a Production environment?**

*   **高分回答要點 (Key Points)**:
    *   **監控 (Monitoring)**: 使用 Prometheus/Datadog 監控 `process.memoryUsage()`。關注 RSS vs HeapUsed。
    *   **診斷 (Diagnosis)**: 不要在 Prod 直接做 Full Heap Snapshot（會暫停服務）。
    *   使用 `heapdump` 或 `v8-profiler` 在流量低谷時採樣。
    *   或者使用 **Heap Sampling** (Allocation Profile)，這比 Full Snapshot 輕量很多，能看出哪類物件分配最快。
    *   *Monitoring: Use Prometheus/Datadog to track `process.memoryUsage()`. Focus on RSS vs HeapUsed.*
    *   *Diagnosis: Don't take a Full Heap Snapshot directly in Prod (it pauses the service).*
    *   *Use `heapdump` or `v8-profiler` to sample during low traffic.*
    *   *Or use **Heap Sampling** (Allocation Profile), which is much lighter than a Full Snapshot and shows which objects are allocated most rapidly.*

## Q3: 什麼是 Backpressure？在 Node.js 中若忽略它會發生什麼？
**What is Backpressure? What happens if you ignore it in Node.js?**

*   **高分回答要點 (Key Points)**:
    *   Backpressure 是數據流控機制。
    *   忽略它會導致數據在記憶體中無限積壓（Buffering），直到 OOM。
    *   正確處理方式是監聽 `drain` 事件或使用 `pipe`/`pipeline`。
    *   *Backpressure is a data flow control mechanism.*
    *   *Ignoring it causes data to buffer infinitely in memory until OOM.*
    *   *The correct way to handle it is listening to the `drain` event or using `pipe`/`pipeline`.*

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **V8 GC**: 區分 **New Space** (Scavenge, 快) 與 **Old Space** (Mark-Sweep, 慢)。盡量讓物件在 New Space 就消亡。
    **V8 GC**: Distinguish between **New Space** (Scavenge, fast) and **Old Space** (Mark-Sweep, slow). Try to let objects die in New Space.
2.  **Heap Snapshots**: 排查洩漏的黃金標準。重點看 **Retainers** 和 **Comparison** 視圖。
    **Heap Snapshots**: The gold standard for debugging leaks. Focus on **Retainers** and **Comparison** views.
3.  **Streams**: 處理大數據的核心。永遠優先選擇 Stream 而非將整個檔案讀入記憶體。
    **Streams**: The core of big data processing. Always prefer Streams over loading entire files into memory.
4.  **Backpressure**: 這是 Stream 不會爆記憶體的關鍵。理解 `write()` 回傳 `false` 與 `drain` 事件的機制。
    **Backpressure**: This is the key to Streams not blowing up memory. Understand the mechanism of `write()` returning `false` and the `drain` event.
5.  **Off-Heap Memory**: Buffer 和某些 C++ Addon 使用的記憶體不在 V8 Heap 內，但仍消耗系統資源。
    **Off-Heap Memory**: Memory used by Buffers and some C++ Addons is not inside the V8 Heap but still consumes system resources.

## 後續延伸 (Next Steps)

*   **進階效能分析**: 學習使用 `0x` 或 `clinic.js` (Clinic Doctor/Flame) 進行 CPU Flamegraph 分析，找出 Event Loop 阻塞點。
    **Advanced Profiling**: Learn to use `0x` or `clinic.js` (Clinic Doctor/Flame) for CPU Flamegraph analysis to find Event Loop blockers.
*   **Worker Threads**: 當單執行緒的 Node.js 遇到 CPU 密集型任務（如影像處理、加密運算）時，如何利用 Worker Threads 分擔負載，避免阻塞主執行緒。
    **Worker Threads**: How to use Worker Threads to offload CPU-intensive tasks (like image processing, encryption) when single-threaded Node.js hits its limit, avoiding main thread blockage.