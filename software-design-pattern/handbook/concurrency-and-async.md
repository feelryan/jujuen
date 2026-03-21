# 併發處理與非同步模式 / Concurrency and Asynchronous Patterns

## Mental model｜心智模型

在處理併發（Concurrency）與非同步（Asynchrony）時，工程師常陷入「多開幾個 Thread 就會變快」的誤區。要正確應用此模式，請建立以下心智模型：

### 1. 廚房與廚師模型 (The Kitchen Metaphor)
- **Concurrency (併發)**：是一個邏輯概念。就像一位廚師同時處理燉湯、切菜和烤箱裡的披薩。他並沒有同時做這三件事（手只有一雙），但他透過「切換上下文（Context Switching）」讓這三件事都在推進。
- **Parallelism (平行)**：是物理概念。廚房裡有三位廚師，同時在切菜。這需要硬體支援（多核心 CPU）。
- **Asynchronous (非同步)**：是流程控制。廚師把披薩放入烤箱後，設定計時器，然後轉身去切菜，而不是盯著烤箱發呆（Non-blocking）。

### 2. 資源競爭與隔離 (Resource Contention vs. Isolation)
併發最困難的不是「如何讓程式跑起來」，而是「如何讓它們不打架」。
- **Shared Mutable State is the Root of All Evil**：多個執行緒同時讀寫同一個變數（共享可變狀態），就像多個廚師搶同一把刀，遲早會受傷（Race Condition）。
- **Isolation First**：最好的併發設計不是「加上完美的鎖（Locking）」，而是「根本不需要鎖」。透過 **Immutable Objects** 或 **Message Passing**（如 Actor Model），讓每個執行單元只處理自己的資料。

---

## Patterns & best practices｜常見模式與最佳實務

在真實專案中，我們很少直接操作原生的 Threads，而是使用以下高階模式：

### 1. Producer-Consumer Pattern (生產者-消費者模式)
這是解耦系統吞吐量差異的黃金標準。
- **應用場景**：日誌寫入、發送 Email、高併發訂單處理。
- **實作重點**：使用 **Blocking Queue** 作為緩衝區。生產者只管把任務丟進 Queue，消費者依照自己的能力從 Queue 取出處理。
- **Backpressure (背壓)**：當 Queue 滿了怎麼辦？必須定義策略（拒絕新請求、丟棄舊請求、或阻塞生產者），防止系統崩潰。

### 2. Future / Promise & Async/Await
現代語言處理非同步的標準介面，避免 Callback Hell。
- **概念**：Future 是一張「取貨單」，代表一個未來會完成的運算結果。
- **最佳實務**：
    - **CompletableFuture / Promise.all**：善用組合器（Combinators）來並行發送多個獨立的請求（Scatter-Gather），最後再聚合結果，大幅降低 Latency。
    - **Always handle errors**：非同步的錯誤容易被吞掉（Swallowed exceptions），務必在 Promise chain 末端或 try-catch block 中處理異常。

### 3. Thread Pool Pattern (執行緒池)
執行緒的建立與銷毀成本極高，必須重複利用。
- **原則**：永遠不要在 Request 處理邏輯中 `new Thread()`。
- **隔離策略 (Bulkheading)**：不要讓所有任務共用同一個 Pool。例如，將「CPU 密集型任務」與「IO 密集型任務」的 Thread Pool 分開，避免 IO 阻塞導致 CPU 運算停擺。

### 4. Immutable Object (不可變物件)
最廉價的 Thread-safe 實作。
- **定義**：物件一旦建立，其狀態就不能改變（所有欄位 final/readonly）。
- **優勢**：多個執行緒讀取同一個 Immutable Object 永遠不需要加鎖，完全消除了 Race Condition 的可能性。
- **實作**：在 Java 中使用 `Record`，在 C# 使用 `record`，或使用 Builder Pattern 確保建構後不可變。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fire and Forget" Trap (射後不理陷阱)
- **現象**：啟動一個非同步任務（如發送通知），但不追蹤其結果或例外。
- **後果**：當任務失敗時，系統毫無感知，Log 裡找不到錯誤，導致資料不一致或靜默失敗（Silent Failure）。
- **修正**：至少要掛載一個 Error Handler 或 Log 紀錄。

### 2. Blocking in an Async Context (在非同步環境中阻塞)
- **現象**：在 Node.js 的 Event Loop 或 Java 的 CompletableFuture 中呼叫 `Thread.sleep()` 或同步的 JDBC 查詢。
- **後果**：單一執行緒被卡死，導致整個應用程式對所有請求失去回應（Thread Starvation）。
- **修正**：在非同步流程中，必須一路非同步到底（Async all the way down），或將阻塞操作丟到專屬的 Worker Thread Pool。

### 3. Oversized Critical Sections (過大的臨界區)
- **現象**：為了安全，將整個方法加上 `synchronized` 或 Lock。
- **後果**：併發變成了序列化執行（Serialization），效能退化成單執行緒，甚至更慢（因為還有 Context Switch 的開銷）。
- **修正**：鎖的範圍（Scope）越小越好，只鎖住真正會發生競爭的那一行代碼。

### 4. Deadlock by Design (設計導致的死鎖)
- **現象**：Thread A 持有鎖 1 等待鎖 2，Thread B 持有鎖 2 等待鎖 1。
- **修正**：
    - 確保所有執行緒獲取鎖的順序一致。
    - 使用 `tryLock` 配合 Timeout 機制，獲取失敗則釋放資源並重試。

---

## Checklists & workflows｜檢查清單與流程

在設計併發功能或 Code Review 時，請使用此清單：

### Design Phase Checklist
- [ ] **必要性檢查**：真的需要併發嗎？單執行緒是否已經足夠快？（避免過度設計）
- [ ] **狀態隔離**：是否有多個執行緒會修改同一個變數？能否改為 Immutable 或 Thread-local？
- [ ] **Pool 配置**：是否為此類任務配置了獨立的 Thread Pool？Pool Size 設定是否合理（CPU 核心數 vs. IO 等待時間）？
- [ ] **背壓策略**：當請求量超過處理能力時，系統會發生什麼事？（OOM? Timeout? Reject?）

### Implementation & Review Checklist
- [ ] **Timeouts**：所有的 Blocking 操作（DB, API call, Lock wait）是否都設定了 Timeout？
- [ ] **Exception Handling**：非同步任務內的 Exception 是否被 Catch 並記錄？
- [ ] **Thread Safety**：使用的集合類別（Collections）是 Thread-safe 的嗎？（例如使用 `ConcurrentHashMap` 而非 `HashMap`）
- [ ] **Clean up**：Thread Pool 或 Executor Service 在應用程式關閉時，是否有正確 shutdown？

---

## Real-world examples｜實戰案例

### Scenario 1: Aggregating Data from Multiple APIs (資料聚合)
**情境**：你需要構建一個 Dashboard，同時顯示「使用者資料」、「訂單紀錄」和「推薦商品」。這三個資料來自不同的微服務。

**Bad Practice (Sequential/Blocking):**
```python
# 總耗時 = T(User) + T(Order) + T(Rec)
user = api.getUser(id)
orders = api.getOrders(id)
recommendations = api.getRecommendations(id)
return aggregate(user, orders, recommendations)
```

**Best Practice (Async/Scatter-Gather):**
```javascript
// 總耗時 = Max(T(User), T(Order), T(Rec))
// 使用 Promise.all 平行發出請求
const [user, orders, recommendations] = await Promise.all([
  api.getUser(id),
  api.getOrders(id),
  api.getRecommendations(id)
]);
return aggregate(user, orders, recommendations);
```

### Scenario 2: High-Volume Log Processing (高流量日誌處理)
**情境**：Web Server 需要將每個 Request 的詳細資訊寫入資料庫，但寫入 DB 速度慢，直接寫會拖慢 API 回應速度。

**Pattern Application: Producer-Consumer**

1.  **Producer (Web Controller)**:
    - 接收 Request。
    - 將 Log Data 封裝成 Immutable Object。
    - 嘗試放入 `BlockingQueue` (設定容量上限，例如 10,000)。
    - 如果 Queue 滿了，選擇「丟棄 Log」或「降級寫入檔案」，確保不影響主流程回應使用者。

2.  **Consumer (Background Worker)**:
    - 獨立的 Thread (或 Thread Pool) 啟動時運行。
    - 迴圈從 `BlockingQueue` 中 `take()` 資料。
    - 累積一定數量（Batch，例如 100 筆）或每隔一段時間（例如 1 秒），執行一次 DB 批量寫入（Batch Insert）。

**效益**：
- **解耦**：API 回應時間不再受 DB 寫入效能影響。
- **削峰填谷**：即使流量瞬間暴衝，Queue 能暫存請求，讓 Consumer 以穩定的速度寫入 DB。