# 效能分析與除錯工程 / Performance Profiling & Debugging Engineering

## Mental model｜心智模型

### 1. The Detective & The Black Box (偵探與黑盒子)
Node.js 應用程式在運行時往往像一個黑盒子。除錯與效能分析的本質，是**將內部狀態視覺化 (Visualizing Internal State)**。
- **Debugging (除錯)**：是為了找出「邏輯錯誤」或「非預期行為」。你通常在尋找「為什麼這個變數是 `null`？」
- **Profiling (效能分析)**：是為了找出「資源瓶頸」。你通常在尋找「為什麼這個請求花了 200ms？」或是「為什麼記憶體只升不降？」

### 2. The Event Loop as a Heartbeat (事件迴圈即心跳)
在 Node.js 中，效能分析的核心幾乎總是圍繞著 **Event Loop**。
- **CPU Profiling**：是在測量「誰佔用了主執行緒 (Main Thread) 太久」，導致心跳暫停。
- **Memory Profiling**：是在測量「哪些物件被長期持有 (Retained)」，導致垃圾回收 (GC) 變得頻繁且昂貴，進而拖慢心跳。

### 3. Sampling vs. Instrumentation (採樣與插樁)
- **Sampling (採樣)**：像拍快照。每隔幾毫秒看一次 CPU 在做什麼。優點是開銷小 (Low Overhead)，適合生產環境分析。
- **Instrumentation (插樁)**：像錄影。記錄每一個函數的進入與退出。資訊最完整但開銷巨大，通常只在開發環境使用。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "3-Snapshot" Technique for Memory Leaks
**三快照技術**是定位記憶體洩漏的黃金標準。
- **Pattern**:
    1.  啟動應用程式，讓它達到穩定狀態 (Warm-up)。
    2.  執行 **GC** (如果工具允許)，並拍攝 **Snapshot 1** (Baseline)。
    3.  執行疑似導致洩漏的操作 (例如發送 100 個 Request)。
    4.  執行 **GC**，拍攝 **Snapshot 2** (Target)。
    5.  重複步驟 3。
    6.  執行 **GC**，拍攝 **Snapshot 3** (Final)。
- **Analysis**: 比較 Snapshot 1 與 Snapshot 3。如果物件在 Snapshot 3 中存在，且在操作期間被分配，則極有可能是洩漏源。重點觀察 **Retained Size** (保留大小) 而非 Shallow Size。

### 2. Flame Graphs for CPU Bottlenecks
**火焰圖**是分析 CPU 密集型任務的最佳工具。
- **X 軸**：代表時間 (Time) 或樣本分佈。越寬代表該函數佔用 CPU 時間越長。
- **Y 軸**：代表呼叫堆疊 (Call Stack) 深度。
- **Best Practice**: 尋找 **"Flat Tops" (平頂)**。如果一個函數在圖表頂端且非常寬，表示它正在執行繁重的同步運算 (Synchronous Calculation)，阻塞了 Event Loop。

### 3. Using `Node Clinic` Suite
不要只依賴 `console.log` 或原始的 V8 profiler。使用專門的工具套件能大幅縮短分析時間。
- **`clinic doctor`**: 第一步診斷。它會告訴你問題是 CPU、I/O 還是 Event Loop Delay。
- **`clinic flame`**: 針對 CPU 問題生成火焰圖。
- **`clinic bubbleprof`**: 針對非同步延遲 (Async Latency) 視覺化，找出哪裡在等待 I/O。

### 4. Production Profiling with Inspector
在生產環境中，你可以安全地開啟 Inspector，但**不要**預設開啟。
- **Pattern**: 使用 `SIGUSR1` 信號來動態開啟 Debugger。
  ```bash
  # 傳送信號給 process 以開啟 inspector
  kill -USR1 <pid>
  # 完成後關閉 (視 Node 版本與實作而定，通常需重啟或透過程式碼關閉)
  ```
- 或者使用輕量級的 APM (如 Datadog, New Relic) 進行 Continuous Profiling。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `console.log` Debugging in High Throughput
在高併發路徑 (Hot Path) 中使用 `console.log` 是效能殺手。
- **Why**: `console.log` 在 Node.js 中通常是同步的 (寫入 stdout/stderr)。大量日誌會直接阻塞 Event Loop。
- **Avoid**: 使用 `debug` 模組或非同步的 Logger (如 `pino`)，並在效能測試時關閉 Debug level logs。

### 2. Confusing "Heap Used" with "RSS"
- **Pitfall**: 看到 OS 報告的記憶體 (RSS - Resident Set Size) 很高就認為是 Memory Leak。
- **Reality**: V8 引擎非常懶惰。如果系統記憶體充足，它不會急著把釋放的記憶體還給 OS。
- **Action**: 始終查看 **Heap Used**。如果 Heap Used 穩定但 RSS 很高，通常不是應用程式層面的洩漏。

### 3. Profiling with "Debug Mode" Enabled
- **Pitfall**: 在進行效能測試 (Benchmark) 時，掛載了 Debugger 或開啟了 `NODE_ENV=development`。
- **Consequence**: 數據完全失真。Debugger 會關閉許多 V8 的優化 (Optimizations)，且 `development` 模式下的 Framework (如 Express) 會有多餘的檢查與日誌。

### 4. Exposing Inspector to Public Internet
- **Security Risk**: 啟動時使用 `--inspect=0.0.0.0:9229` 在公有雲環境是非常危險的。
- **Consequence**: 攻擊者可以連接 Inspector，執行任意程式碼 (RCE)。
- **Fix**: 始終綁定到 `127.0.0.1`，並透過 SSH Tunnel 連接。

---

## Checklists & workflows｜檢查清單與流程

### Performance Issue Triage Workflow (效能問題分流流程)

1.  **Symptom Check (症狀確認)**:
    - [ ] CPU 使用率飆高？ -> 可能是同步運算阻塞 (Crypto, JSON.parse, Regex)。
    - [ ] 記憶體持續上升？ -> 可能是 Memory Leak。
    - [ ] CPU 低但回應慢？ -> 可能是外部 I/O 等待 (DB, API) 或 Event Loop 阻塞。

2.  **Environment Setup (環境準備)**:
    - [ ] 確保 `NODE_ENV=production`。
    - [ ] 確保沒有多餘的 `console.log`。
    - [ ] 如果是 Memory 問題，確保 `--max-old-space-size` 設定正確。

3.  **Profiling Execution (執行分析)**:
    - [ ] **CPU**: 使用 `node --prof` 或 `clinic flame` 錄製 30秒+ 的負載期間。
    - [ ] **Memory**: 使用 Chrome DevTools 連接，錄製 Allocation Timeline 或 Heap Snapshots。
    - [ ] **Lag**: 使用 `perf_hooks` 監控 Event Loop Lag。

### Debugging Checklist (除錯清單)

- [ ] **Source Maps**: 是否已啟用 Source Maps？(否則堆疊追蹤會指向編譯後的 JS)。
- [ ] **Async Context**: 是否使用了 `AsyncLocalStorage` 或相關追蹤機制來關聯 Log？
- [ ] **Uncaught Exceptions**: 是否有監聽 `uncaughtException` 和 `unhandledRejection`？(不要讓它們靜默失敗)。
- [ ] **Dependencies**: 最近是否升級了原生模組 (Native Modules)？(常見的 Segfault 來源)。

---

## Real-world examples｜實戰案例

### Example 1: The "JSON.parse" Blocker (CPU 瓶頸)

**Scenario**: 一個 API server 每隔幾分鐘就會完全無回應 2 秒鐘，但 CPU 瞬間飆到 100%。

**Investigation**:
1.  使用 `clinic flame` 進行採樣。
2.  **Flame Graph** 顯示一個非常寬的平頂 (Plateau)，對應到 `JSON.parse`。
3.  **Root Cause**: 程式碼中有一行 `const data = JSON.parse(fs.readFileSync(largeFile))`。當檔案變大 (例如 50MB) 時，解析 JSON 是同步且耗時的操作，完全卡死 Event Loop。

**Fix**: 使用 Stream 解析 (如 `JSONStream`) 或將解析工作移至 Worker Thread。

### Example 2: The Closure Leak (記憶體洩漏)

**Scenario**: 伺服器運行 3 天後 OOM (Out of Memory) 崩潰。

**Investigation**:
1.  使用 Chrome DevTools 進行 **3-Snapshot** 分析。
2.  比較 Snapshot 1 和 3，發現 `EventListener` 的數量持續增加。
3.  查看 Retainers (持有者)，發現每個 Request 都對一個全域的 `EventEmitter` 註冊了監聽器，但在 Request 結束時**忘記 `removeListener`**。

**Code Snippet (The Bug)**:
```javascript
// Anti-pattern
const globalBus = new EventEmitter();

app.get('/data', (req, res) => {
  // 每次請求都建立一個新的閉包並掛載，卻從未移除
  globalBus.on('update', () => {
    console.log('Update received for', req.id); // req 被閉包持有，無法 GC
  });
  res.send('ok');
});
```

### Example 3: The "External" Memory Mystery (Buffer 洩漏)

**Scenario**: Heap Used 很低 (50MB)，但 Process RSS 佔用了 1GB，最終導致 Container 被 Kill。

**Investigation**:
1.  Heap Snapshot 顯示 JS 物件很少。
2.  懷疑是 **Buffer** 或 **Native Module**。
3.  檢查程式碼發現使用了大量的 `Buffer.allocUnsafe` 處理圖片，但沒有正確釋放引用。
4.  在 Node.js 中，Buffer 的記憶體分配是在 V8 Heap 之外 (Off-heap)，但在 Heap Snapshot 中會顯示為 `ArrayBuffer` 或 `External`。

**Fix**: 確保不再需要的 Buffer 引用被設為 `null`，或者檢查使用的 Image Processing Library 是否有 Memory Leak 報告。