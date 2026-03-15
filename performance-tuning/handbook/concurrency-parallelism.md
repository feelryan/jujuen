# 並發模型與鎖的競爭 / Concurrency Models and Lock Contention

## Mental model｜心智模型

在效能優化的世界裡，並發（Concurrency）與平行（Parallelism）是提升吞吐量的雙面刃。理解它們的關鍵在於意識到 **「協作的成本（Cost of Coordination）」**。

### 1. 廚房類比 (The Kitchen Analogy)
- **Concurrency (並發)**：一個廚師同時處理切菜、煮湯和煎牛排。他需要不斷切換注意力（Context Switching），如果切換太頻繁，效率反而下降。
- **Parallelism (平行)**：三個廚師同時在廚房工作。雖然人手多了，但如果只有一把菜刀（Shared Resource/Lock），大家還是要排隊（Contention）。

### 2. 資源競爭模型 (Resource Contention Model)
當多個執行緒（Threads）試圖存取同一塊記憶體或資源時，效能瓶頸通常發生在三個層次：
1.  **CPU 排程層 (Scheduling)**：過多的執行緒導致 CPU 花費大量時間在保存與恢復現場（Context Switching），而非執行業務邏輯。
2.  **鎖競爭層 (Lock Contention)**：執行緒進入「阻塞（Blocked）」或「自旋（Spinning）」狀態等待鎖釋放，這段時間是純粹的浪費（Wait Time）。
3.  **硬體快取層 (Hardware Cache)**：即使沒有顯式的鎖，多核心同時修改相鄰記憶體位置會導致 CPU Cache Line 失效（False Sharing），引發隱形的效能崩跌。

> **Core Principle**: The goal is to maximize **useful work** by minimizing **wait time** and **coordination overhead**.
> 核心原則：最大化「有效工作時間」，最小化「等待時間」與「協作開銷」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 縮小鎖的範圍 (Reduce Lock Granularity)
不要鎖住整個物件或方法，只鎖住真正需要保護的「臨界區（Critical Section）」。
- **Lock Striping (鎖分段)**：像 `ConcurrentHashMap` 一樣，將資料分段，不同的 Key 落入不同的段（Segment），只鎖該段而非全表。
- **Copy-On-Write (寫時複製)**：對於讀多寫少的場景（如設定檔、白名單），寫入時複製一份新資料，讀取時完全無鎖。

### 2. 無鎖程式設計 (Lock-Free Programming)
利用 CPU 指令集提供的原子操作（Atomic Operations）來替代重量級鎖。
- **CAS (Compare-And-Swap)**：適用於計數器、狀態標記。例如 Java 的 `AtomicInteger` 或 Go 的 `atomic` package。
- **Accumulators / Adders**：在高競爭下，單一 Atomic 變數也會成為瓶頸。使用 `LongAdder` (Java) 或類似機制，讓每個 CPU core 維護局部計數，讀取時再加總。

### 3. I/O 模型選擇 (I/O Models)
- **Thread-per-Request (Blocking I/O)**：傳統模式，簡單但無法擴展。當連線數達到數千時，Context Switching 會吃光 CPU。
- **Event Loop / Reactor Pattern (Non-blocking I/O)**：如 Node.js, Netty, Go (Goroutines + Netpoller)。少量執行緒處理大量連線。
  - **Best Practice**: 將 I/O 等待與 CPU 計算分離。I/O 交給 Event Loop，耗時的 CPU 計算交給 Worker Thread Pool。

### 4. 避免 False Sharing (Padding)
當兩個無關的變數剛好位於同一個 CPU Cache Line（通常是 64 bytes）時，Core A 修改變數 X 會導致 Core B 的變數 Y 快取失效。
- **Solution**: 使用 Cache Line Padding（填充無用位元組）將頻繁修改的變數隔開。
- **Language Support**: Java (`@Contended`), C++ (`alignas`).

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Hot Lock" (熱點鎖)
- **現象**：所有執行緒都在爭搶同一個全域鎖（Global Lock）。
- **後果**：系統並行度降為 1（甚至更差，因為還有排隊開銷）。增加 CPU 核心數完全無法提升效能（Amdahl's Law 的極端體現）。
- **識別**：Profiling 工具顯示大量時間花在 `futex` (Linux), `monitor entry` (Java), 或 `mutex_lock`。

### 2. Blocking the Event Loop (阻塞事件迴圈)
- **現象**：在 Node.js 或 Netty 的 I/O 執行緒中執行了耗時計算（如加密、大 JSON 解析）或同步 I/O。
- **後果**：整個系統對所有請求失去響應，Heartbeat 超時，造成雪崩效應。
- **警語**：Don't block the main thread!

### 3. Context Switching Storm (上下文切換風暴)
- **現象**：執行緒數量遠大於 CPU 核心數（例如 4 核 CPU 開了 2000 個活躍執行緒）。
- **後果**：`sys` CPU 使用率飆高，`usr` CPU 低，Load Average 極高但產出低。
- **誤區**：以為開越多執行緒跑得越快。

### 4. Double-Checked Locking without Volatile
- **現象**：在 Singleton 模式中試圖優化鎖，但忽略了指令重排序（Instruction Reordering）。
- **後果**：其他執行緒可能讀到「初始化了一半」的物件，導致崩潰或邏輯錯誤。

---

## Checklists & workflows｜檢查清單與流程

在進行並發優化或 Code Review 時，請使用此清單：

### Phase 1: Design & Code Review
- [ ] **必要性檢查**：真的需要共用狀態嗎？能否透過 Message Passing (Actor Model, Channels) 來避免共享記憶體？
- [ ] **鎖的範圍**：`synchronized` 或 `Lock` 區塊內是否包含了 I/O 操作或耗時計算？（必須移出！）
- [ ] **不可變性**：共用物件是否可以設計為 Immutable？（Immutable 物件天生 Thread-safe）。
- [ ] **原子性**：是否錯誤地將「檢查」與「執行」分開了？（例如 `if (!map.containsKey(k)) map.put(k, v)` 在並發下是不安全的，應使用 `putIfAbsent`）。

### Phase 2: Runtime Tuning & Diagnosis
- [ ] **觀察 Context Switches (CS)**：
  - 使用 `vmstat 1` 或 `pidstat -w`。
  - CS 是否超過 `10,000 ~ 100,000 / sec` (視 CPU 核心數而定)？如果是，執行緒可能太多。
- [ ] **觀察鎖競爭 (Lock Contention)**：
  - Java: JFR (Java Flight Recorder) 或 `jstack` 尋找 `BLOCKED` 狀態。
  - C/C++: `perf lock` 或 eBPF 工具。
  - Database: 檢查 `Row Lock Waits`。
- [ ] **觀察 CPU 模式**：
  - `sys` 高於 `usr`？可能過度陷入 Kernel mode (Syscalls, Context Switches)。
  - `si` / `hi` (Soft/Hard Interrupts) 過高？網路封包處理瓶頸。

---

## Real-world examples｜實戰案例

### Case 1: The Global Counter Bottleneck (全域計數器瓶頸)

**Scenario**: 一個高流量的 API Gateway 需要統計請求總數。
**Bad Practice**: 使用全域 `mutex` 保護一個 `int` 變數。
```go
// Anti-pattern
var mu sync.Mutex
var count int64

func Inc() {
    mu.Lock()
    count++ // 這裡變成單行道，所有 goroutine 排隊
    mu.Unlock()
}
```
**Optimization**:
1.  **Level 1**: 使用 Atomic (CAS)。 `atomic.AddInt64(&count, 1)`。這解決了鎖的開銷，但在極高並發下，多個 CPU core 會爭奪該變數的 Cache Line (Cache Coherency traffic)。
2.  **Level 2 (Best)**: 使用 **LongAdder** (Java) 或 **Sharded Counters**。每個 Thread/CPU 維護自己的計數器，讀取時才加總。

### Case 2: False Sharing in High-Performance Queue (佇列中的偽共享)

**Scenario**: 實作一個 Ring Buffer (如 Disruptor Pattern) 用於執行緒間通訊。
**Problem**: `Head` (讀指標) 和 `Tail` (寫指標) 定義在同一個 Struct 中，且緊鄰排列。
```c
struct RingBuffer {
    long head; // Modified by Consumer
    long tail; // Modified by Producer
    // ... data
};
```
**Analysis**: 當 Consumer 更新 `head` 時，包含 `tail` 的 Cache Line 也會失效。Producer 想要讀取/更新 `tail` 時必須重新從記憶體載入，導致 "Ping-pong" 效應。
**Optimization**: Padding。
```c
struct RingBuffer {
    long head;
    char padding1[56]; // 填充至 64 bytes (Cache Line size)
    long tail;
    char padding2[56];
};
```

### Case 3: Async I/O with unintended Blocking (非同步 I/O 中的意外阻塞)

**Scenario**: 一個基於 Netty 的 Web Server 吞吐量上不去，Latency 忽高忽低。
**Investigation**: 使用 Profiler 發現 Event Loop Thread 偶爾會停頓 50ms。
**Root Cause**: 開發者在 callback 中直接呼叫了 `BCrypt.hashpw()` (密碼雜湊，故意設計得很慢) 或者呼叫了 JDBC (Blocking Driver)。
**Fix**:
1.  將 `BCrypt` 運算丟給專用的 `WorkerThreadPool`。
2.  將 JDBC 換成 R2DBC (Reactive Driver) 或同樣丟給專門處理 DB 的 Thread Pool，確保 Event Loop 永遠只處理「通知」而非「等待」。