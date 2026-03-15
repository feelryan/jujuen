# 核心機制：Event Loop 與 Reactor Pattern / Core Mechanics: Event Loop & Reactor Pattern

## Mental model｜心智模型

要掌握 Node.js，必須先打破「它是單執行緒，所以做不了大事」的迷思。正確的心智模型應該是 **「單執行緒的指揮官，多執行緒的工廠」**。

To master Node.js, you must dispel the myth that "it's single-threaded, so it can't handle heavy loads." The correct mental model is **"A Single-Threaded Commander, Multi-Threaded Factory."**

### 1. 餐廳經理模型 (The Restaurant Manager Analogy)
想像 Node.js 是一個繁忙的餐廳：
- **Main Thread (Event Loop)** 是唯一的 **外場經理**。他負責接單（Request）和送餐（Response）。他動作極快，從不進廚房做菜，也絕不等待。
- **Libuv (Thread Pool / Kernel)** 是 **內場廚房**。這裡有許多廚師（Worker Threads）和自動化設備（OS Kernel Async I/O）。
- **Callback Queue** 是 **出餐口**。當廚房做完菜，會把菜放在這裡，經理看到後會馬上送給客人。

**關鍵點 (Key Takeaway)：**
只要經理（Main Thread）不被某個奧客（CPU Intensive Task）纏住問東問西，這家餐廳的吞吐量（Throughput）就會非常驚人。但如果經理停下來算帳（例如在主執行緒做加密運算或解析巨大 JSON），整家餐廳就會癱瘓。

### 2. 優先級佇列 (The Priority Queues)
Event Loop 並非只有一個佇列，理解執行順序至關重要：
1.  **Call Stack**：當前正在執行的同步程式碼。
2.  **Microtask Queue (VIP 通道)**：`process.nextTick` (最高優先) > `Promise.then/catch`。
    - **注意**：Event Loop 必須清空這裡的所有任務，才會進入下一個階段。
3.  **Macrotask Queue (普通通道)**：`setTimeout`, `setInterval`, `setImmediate`, I/O callbacks。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 卸載重運算 (Offloading CPU-Intensive Tasks)
不要讓 Event Loop 處理繁重的計算。
Don't let the Event Loop handle heavy computations.

- **Pattern**: 使用 Worker Threads 或專用的微服務處理 CPU 密集任務。
- **Example**: 圖片縮放、影片轉檔、大量數據的加密/解密。

```javascript
// Good Practice: Offloading to Worker Thread
const { Worker } = require('worker_threads');

function resizeImageAsync(imageData) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./image-worker.js', { workerData: imageData });
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}
```

### 2. 任務切分 (Partitioning)
如果必須在主執行緒處理較大運算，將其切分為小塊，利用 `setImmediate` 讓出執行權，避免阻塞 I/O。
If you must compute on the main thread, split it into chunks and use `setImmediate` to yield execution, preventing I/O blocking.

```javascript
// Pattern: Chunking execution
function processLargeArray(items) {
  if (items.length === 0) return;

  const chunk = items.splice(0, 1000); // 取出一小部分
  doHeavyStuff(chunk);

  // 讓 Event Loop 有機會去處理 I/O (Poll phase)，然後再回來
  setImmediate(() => processLargeArray(items)); 
}
```

### 3. 正確選擇計時器 (Timer Selection)
- **`setImmediate()`**：用於 I/O callback 之後。保證在當前 Poll 階段結束後立即執行（Check phase）。
- **`process.nextTick()`**：用於「在任何 I/O 或 Timer 之前」需要執行的緊急任務（如錯誤重試前的清理、事件觸發）。**慎用**，因為它會阻塞 I/O。
- **`setTimeout(fn, 0)`**：行為類似 `setImmediate`，但在 I/O 循環中，`setImmediate` 的優先級更明確。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 釋放 Zalgo (Releasing Zalgo)
**定義**：API 有時同步回傳（Sync），有時非同步回傳（Async）。這會導致呼叫者的邏輯出現競態條件（Race Condition）。
**Definition**: An API that returns synchronously sometimes and asynchronously other times. This leads to race conditions in the caller's logic.

- **Bad**:
  ```javascript
  function getData(id, callback) {
    if (cache[id]) {
      callback(cache[id]); // Sync: Zalgo unleashed!
    } else {
      db.get(id, callback); // Async
    }
  }
  ```
- **Fix**: 始終保持非同步。使用 `process.nextTick` 包裹同步回應。
  ```javascript
  if (cache[id]) {
    process.nextTick(() => callback(cache[id]));
  }
  ```

### 2. JSON.parse 的陷阱 (The JSON.parse Trap)
`JSON.parse` 是同步且阻塞的。解析一個 20MB 的 JSON 可能會卡住 Event Loop 數百毫秒，導致伺服器在那段時間無法回應任何請求。
`JSON.parse` is synchronous and blocking. Parsing a 20MB JSON can freeze the Event Loop for hundreds of milliseconds.

- **Pitfall**: 在 API endpoint 中直接解析使用者上傳的大型 JSON。
- **Solution**: 使用 Stream 解析庫（如 `JSONStream`）或將解析工作移至 Worker Thread。

### 3. Microtask Starvation (餓死 Event Loop)
無限遞迴呼叫 `process.nextTick` 會導致 Event Loop 永遠無法進入下一個階段（如 I/O 處理），導致伺服器看起來像當機，但 CPU 卻是滿載。
Recursively calling `process.nextTick` prevents the Event Loop from ever reaching the next phase (like I/O), causing the server to hang while CPU usage spikes.

- **Bad**:
  ```javascript
  function loop() {
    process.nextTick(loop); // Event Loop will never handle I/O
  }
  ```
- **Better**: 使用 `setImmediate(loop)`，這允許 Event Loop 在遞迴之間處理 I/O。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或效能調優時，請使用此清單：

### Code Review Checklist
- [ ] **同步操作檢查**：是否在 Hot Path (高頻率路徑) 中使用了 `fs.readFileSync` 或 `crypto.pbkdf2Sync`？
- [ ] **大物件處理**：是否有 `JSON.parse` 或 `JSON.stringify` 處理潛在的大型 Payload？
- [ ] **Zalgo Check**：Callback 或 Promise 的執行順序是否一致（永遠是非同步）？
- [ ] **Regex 安全**：Regex 是否存在 ReDoS 風險（指數級回溯）？這會直接卡死 Event Loop。
- [ ] **Promise 錯誤**：所有的 Promise 是否都有 `.catch` 或回傳給呼叫者？未處理的 Promise Rejection 在新版 Node 中會導致 Process Crash。

### Event Loop Lag Detection Workflow
如何判斷 Event Loop 是否被阻塞？

1.  **監控**：使用 `perf_hooks` 或 APM 工具（如 Datadog, New Relic）監控 `eventLoopLag` 指標。
2.  **閾值**：如果 Lag 持續超過 100ms，表示有同步任務在阻塞。
3.  **診斷**：
    - 使用 Node.js 內建 Profiler: `node --prof app.js`
    - 分析生成的 `isolate-0x...log`，找出佔用 CPU 時間最長的同步函數。

---

## Real-world examples｜實戰案例

### Case 1: 突然變慢的 API (The Sudden Latency Spike)

**情境**：一個電商網站在促銷期間，首頁 API 偶爾會 Timeout，但資料庫負載很低。
**原因**：工程師在首頁 API 的邏輯中加入了一段程式碼，用來計算使用者購物車內商品的「複雜折扣」。這個計算涉及多層迴圈，並且是同步執行的。當購物車商品很多時，計算耗時超過 200ms。
**後果**：這 200ms 內，Node.js 無法處理任何其他使用者的請求（連簡單的 Health Check 都會失敗）。

**修正 (Refactoring)**：

```javascript
// Before (Blocking)
app.get('/cart/total', (req, res) => {
  const total = calculateComplexDiscountSync(req.user.cart); // Blocks for 200ms+
  res.json({ total });
});

// After (Non-blocking via setImmediate partitioning or Worker)
// 這裡展示簡單的 setImmediate 切分概念 (Partitioning)
function calculateDiscountAsync(cart, callback) {
  let total = 0;
  let i = 0;
  function processChunk() {
    const start = Date.now();
    // 每次只算 10ms，然後讓出 CPU
    while (i < cart.length && Date.now() - start < 10) {
      total += heavyMath(cart[i]);
      i++;
    }
    if (i < cart.length) {
      setImmediate(processChunk); // 讓 Event Loop 去呼吸一下
    } else {
      callback(total);
    }
  }
  processChunk();
}
```

### Case 2: 檔案上傳伺服器 (The File Upload Service)

**情境**：使用者上傳 CSV 檔案，伺服器讀取內容並寫入 DB。
**錯誤做法**：將整個檔案 `fs.readFile` 到記憶體，然後 split 字串。
**後果**：當 100 人同時上傳 50MB 檔案，記憶體瞬間爆滿 (OOM)，且 GC (Garbage Collection) 頻繁觸發導致 Event Loop 卡頓。

**正確做法 (Streams + Reactor Pattern)**：
利用 Node.js 的 Stream 機制，將讀取 (Readable) 與寫入 (Writable) 串接。這正是 Reactor Pattern 的精隨——有資料流進來才處理，不佔用額外記憶體。

```javascript
const fs = require('fs');
const csv = require('csv-parser');

// 記憶體使用量極低，且不會阻塞 Event Loop
fs.createReadStream('huge-data.csv')
  .pipe(csv())
  .on('data', (row) => {
    // 處理單行資料
  })
  .on('end', () => {
    console.log('CSV processed successfully');
  });
```