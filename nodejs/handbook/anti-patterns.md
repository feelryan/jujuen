# 常見反模式與效能陷阱 / Common Anti-patterns & Performance Pitfalls

在 Node.js 中，由於其單執行緒（Single-threaded）與事件驅動（Event-driven）的特性，許多在多執行緒語言（如 Java 或 Go）中微不足道的寫法，在這裡可能會導致整個伺服器停擺。本章節將剖析那些最容易讓生產環境崩潰的反模式，並提供具體的解決方案。

In Node.js, due to its single-threaded and event-driven nature, coding habits that are trivial in multi-threaded languages can bring a server to a halt. This chapter dissects the anti-patterns most likely to crash production environments and offers concrete solutions.

---

## Mental model｜心智模型

要避免陷阱，首先要建立正確的 **「餐廳服務生模型」（The Waiter Model）**。

### 1. The Single Waiter (單一服務生)
想像一間繁忙的餐廳只有 **一位** 服務生（Event Loop）。
- **Good:** 服務生負責點餐（接收 Request）並把單子交給廚房（System I/O, DB），然後立刻去服務下一桌。
- **Bad (Blocking):** 服務生親自進廚房切菜（CPU Intensive Task）。這時外場所有客人都被晾在一邊，無人回應。

### 2. The Leaky Bucket (漏水的水桶)
Node.js 的記憶體管理依賴 V8 的 Garbage Collection (GC)。
- **Good:** 用完的變數解除參照（Dereference），GC 會回收記憶體。
- **Bad (Memory Leak):** 全域變數、未清理的 Event Listeners 或閉包（Closures）抓著物件不放。這就像餐廳裡的髒盤子永遠不收，最終導致沒有盤子可用（OOM Crash）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Offloading CPU Tasks (卸載 CPU 密集任務)
不要在主執行緒進行繁重的計算。
- **Worker Threads:** 對於加密、圖像處理、壓縮等任務，使用 `worker_threads` 模組。
- **Microservices / Serverless:** 將極度耗資源的任務拆分到獨立的服務中。

### 2. Stream-Based Processing (串流處理)
永遠不要將大檔案完整讀入記憶體。
- **Pattern:** 使用 `pipeline` 或 `.pipe()` 處理資料流。
- **Benefit:** 記憶體佔用量固定（Constant memory usage），不會隨檔案大小暴增。

### 3. Bounded Concurrency (限制併發數)
當需要處理大量非同步任務時（例如批次寫入 DB），不要使用 `Promise.all([...10000_items])`，這會瞬間耗盡資源。
- **Pattern:** 使用 `p-limit` 或 async iterator 實作併發控制（Concurrency Control）。

```javascript
// ✅ Best Practice: Using p-limit to control concurrency
import pLimit from 'p-limit';

const limit = pLimit(5); // Only 5 concurrent tasks
const tasks = items.map(item => limit(() => processItem(item)));
await Promise.all(tasks);
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "JSON Killer" (同步 JSON 解析)
**Description:** `JSON.parse` 和 `JSON.stringify` 是同步且阻塞的（Synchronous & Blocking）。解析一個 10MB 的 JSON 可能會阻塞 Event Loop 數百毫秒。
- **Anti-pattern:** 在 HTTP Handler 中直接解析來自使用者的大型 JSON Payload。
- **Solution:** 使用串流解析庫（如 `JSONStream`）或在 Worker Thread 中解析。

### 2. The `forEach` Async Trap (非同步迴圈陷阱)
**Description:** `Array.prototype.forEach` 不會等待 `async` callback 完成。
- **Pitfall:** 程式碼會直接執行到迴圈後的邏輯，而迴圈內的 DB 操作還在跑，導致 Race Condition 或錯誤的 Response。
- **Solution:** 使用 `for...of` 迴圈或 `Promise.all` + `map`。

```javascript
// ❌ Anti-pattern: This finishes immediately, before DB saves
items.forEach(async (item) => {
  await db.save(item);
});
console.log('Done? No.');

// ✅ Solution: Sequential
for (const item of items) {
  await db.save(item);
}

// ✅ Solution: Parallel
await Promise.all(items.map(item => db.save(item)));
```

### 3. Promise Constructor Anti-pattern (Promise 建構式濫用)
**Description:** 將已經是 Promise 的東西再包一層 `new Promise`，這被稱為 "Deferred anti-pattern"。
- **Pitfall:** 錯誤處理變得複雜，且容易遺失 Error bubble。
- **Solution:** 直接回傳 Promise 或使用 async/await。

```javascript
// ❌ Anti-pattern
function getData() {
  return new Promise((resolve, reject) => {
    db.query().then(res => resolve(res)).catch(err => reject(err));
  });
}

// ✅ Solution
function getData() {
  return db.query();
}
```

### 4. Unbounded Cache (無上限快取)
**Description:** 使用原生 `Map` 或 `Object` 作為快取，但沒有實作清理機制。
- **Pitfall:** 隨著時間推移，記憶體只增不減，最終導致 Heap Out of Memory。
- **Solution:** 使用 `lru-cache` 庫或外部快取（Redis）。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist (程式碼審查清單)
在發布到生產環境前，請檢查以下項目：

- [ ] **Event Loop Blocking:** 是否有同步的 `fs` 操作（如 `fs.readFileSync`）或大型 `JSON` 操作？
- [ ] **Async Flow:** 是否在 `forEach` 中使用了 `await`？（應改為 `for...of` 或 `Promise.all`）
- [ ] **Error Handling:** 所有的 Promise 是否都有 `.catch()` 或在 `try/catch` 區塊中？
- [ ] **Memory Leaks:** 是否移除了不再使用的 Event Emitter 監聽器（`removeListener`）？
- [ ] **Timers:** `setInterval` 是否有對應的 `clearInterval` 機制？
- [ ] **Dependencies:** 是否引入了過於肥大的同步 Library？

### Performance Debugging Workflow (效能除錯流程)
當服務變慢時，請依照此流程排查：

1.  **Monitor Event Loop Lag:** 使用 `perf_hooks` 或 APM 工具監控 Event Loop 延遲。如果延遲高，代表有 CPU 阻塞任務。
2.  **Profile CPU:** 使用 `node --prof` 或 `0x` 生成火焰圖（Flamegraph），找出佔用 CPU 的函數。
3.  **Analyze Memory:** 若記憶體異常，使用 Chrome DevTools 連接 Node.js (`node --inspect`) 抓取 Heap Snapshot 進行對比。
4.  **Check I/O:** 檢查是否有大量的 DB 查詢未加索引，或外部 API 呼叫超時未設定 Timeout。

---

## Real-world examples｜實戰案例

### Case 1: The "Frozen" Server (加密運算阻塞)
**情境：** 一個登入 API 在高併發時導致所有其他 API Timeout。
**原因：** 密碼雜湊運算（如 `pbkdf2` 或 `bcrypt`）是 CPU 密集型操作。預設的 Thread Pool 大小（UV_THREADPOOL_SIZE=4）不足以應付大量並發登入。

**❌ Bad Code:**
```javascript
// 預設情況下，這會佔用 Libuv 的 Thread Pool，
// 如果同時有 4 個請求，第 5 個就會被阻塞等待
app.post('/login', (req, res) => {
  const hash = crypto.pbkdf2Sync(password, salt, ...); // SYNC BLOCKING!
  // ...
});
```

**✅ Fix:**
1. 使用非同步版本 `pbkdf2`（Offload to Thread Pool）。
2. 調整 `UV_THREADPOOL_SIZE` 環境變數（例如設為 CPU 核心數）。
3. 最佳解：將認證服務拆分為獨立的 Microservice。

### Case 2: The "Slow Leak" (閉包記憶體洩漏)
**情境：** 伺服器每隔三天就會 Crash，重啟後正常。
**原因：** 在全域陣列中儲存了 Request 物件，原本只想做簡單的 logging，但忘記限制長度。

**❌ Bad Code:**
```javascript
const requestLogs = []; // Global variable

app.use((req, res, next) => {
  // req 物件包含大量資訊（Headers, Body, Socket reference...）
  // 即使請求結束，因為被 requestLogs 引用，GC 無法回收
  requestLogs.push(req); 
  next();
});
```

**✅ Fix:**
1. 只儲存必要的資訊（如 URL, Method, Timestamp）。
2. 使用外部 Logging 系統（ELK, Datadog），不要存在記憶體內。
3. 若必須存，使用 `WeakMap` 或固定長度的資料結構（Circular Buffer）。