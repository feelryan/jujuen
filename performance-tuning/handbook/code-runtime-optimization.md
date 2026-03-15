# 程式碼層級與 Runtime 優化 / Code-Level and Runtime Optimization

## Mental model｜心智模型

在深入程式碼優化之前，必須建立正確的成本模型（Cost Model）。現代軟體效能不僅取決於演算法的時間複雜度（Big O），更深受 **硬體架構（Hardware Architecture）** 與 **執行環境（Runtime Environment）** 的影響。

### 1. 機械同理心 (Mechanical Sympathy)
不要把電腦當作抽象的數學計算機，而要理解它是一台物理機器。
- **CPU Cache is King**: 存取 L1 Cache 與存取主記憶體（RAM）的速度差異可達 100 倍。資料結構的「空間局部性（Data Locality）」往往比理論上的指令數更重要。這也是為什麼在現代硬體上，連續記憶體的 Array 往往比 Linked List 快得多。
- **Context Switch Cost**: 執行緒切換或系統呼叫（Syscall）是昂貴的。

### 2. Runtime 的隱形成本
你的程式碼並非直接在 CPU 上跑，中間隔著 Compiler、Interpreter 或 Virtual Machine (JVM, V8, CLR)。
- **GC Pressure (GC 壓力)**: 記憶體配置（Allocation）通常很快，但回收（Garbage Collection）很貴。在高頻率迴圈中產生大量短命物件（Short-lived objects）會導致 CPU 週期浪費在 GC 上，造成 "Stop-the-world" 延遲。
- **JIT Warm-up**: 在 Java 或 JavaScript 中，程式碼需要執行多次才會被 JIT 編譯器優化成高效的 Machine Code。

### 3. The 90/10 Rule (Hot Path)
90% 的執行時間花在 10% 的程式碼上。這 10% 被稱為 **Hot Path（熱點路徑）**。
- **優化策略**: 找出 Hot Path 並極致優化，對於 Cold Path（冷路徑，如啟動設定、錯誤處理）則優先保持可讀性。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 記憶體管理與減少配置 (Memory Management & Allocation Reduction)
- **Object Pooling (物件池)**: 對於創建成本高或使用頻率極高的物件（如 DB Connections, Threads, Large Buffers），使用 Pool 重複利用，避免反覆的 `new` 和 GC。
- **Pre-sizing Collections**: 在建立 List 或 Map 時，如果預知大小，請直接指定 capacity（例如 `new ArrayList(10000)`）。這能避免動態擴容（Resizing）帶來的陣列複製成本。
- **Stack Allocation over Heap**: 在支援的語言（如 Go, C++, Rust, C# `struct`）中，盡量讓短暫的小物件配置在 Stack 上，而非 Heap，以減輕 GC 負擔。

### 2. 資料結構與存取優化 (Data Structures & Access Patterns)
- **Cache-Friendly Structures**: 優先使用連續記憶體結構（Arrays, Slices, Vectors）。避免指標跳躍（Pointer Chasing）導致的 Cache Miss。
- **Short-Circuit Evaluation**: 在複雜的 boolean 判斷中，將「最可能發生」或「運算成本最低」的條件放在最前面。
- **Hash vs. Tree**: 雖然 Hash Map 是 O(1)，但在資料量小（例如 < 100 items）時，簡單的 Array 迭代掃描可能因為 Cache locality 而更快。

### 3. 迴圈與邏輯優化 (Loop & Logic Optimization)
- **Loop Invariant Code Motion**: 將迴圈內「不會改變的計算」移到迴圈外。
  - *Bad*: `for (i=0; i < list.size(); i++) { process(data * Math.PI); }`
  - *Good*: `const factor = Math.PI; const len = list.size(); for (i=0; i < len; i++) { process(data * factor); }`
- **Branch Prediction**: CPU 喜歡可預測的指令流。在處理大量資料時，如果 `if-else` 的結果隨機跳動，會破壞 CPU 的分支預測。有時先將資料排序（Sorting）再處理，反而能提升整體速度。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Premature Optimization (過早優化)
- **Trap**: 在沒有 Profiling 數據佐證的情況下，為了「感覺會比較快」而寫出晦澀難懂的程式碼。
- **Consequence**: 程式碼難以維護，且往往優化了非瓶頸區域（Non-hot path），對整體效能毫無幫助。

### 2. String Concatenation in Loops (迴圈中的字串串接)
- **Trap**: 在 Java, C#, Python 等語言中使用 `s += "data"` 在迴圈中串接字串。
- **Why**: 字串通常是不可變（Immutable）的。這會導致每次迭代都創建一個新的字串物件並複製舊內容，產生 O(N^2) 的時間複雜度與大量記憶體垃圾。
- **Fix**: 使用 `StringBuilder`, `StringBuffer`, `strings.Builder` 或 Array Join。

### 3. Blocking the Event Loop (阻塞事件迴圈)
- **Context**: Node.js, Browser JS, Python Asyncio 等單執行緒環境。
- **Trap**: 在 Async 函式中執行 CPU 密集型運算（如加密、大圖處理、複雜 JSON 解析）。
- **Consequence**: 整個服務對所有請求失去回應（Latency Spike）。
- **Fix**: 將 CPU 密集任務移至 Worker Threads 或背景 Queue 處理。

### 4. Hidden Boxing/Unboxing (隱式裝箱/拆箱)
- **Trap**: 在強型別語言（Java, C#）中，頻繁將 Primitive type (int) 轉換為 Wrapper Object (Integer) 放入集合中。
- **Consequence**: 額外的記憶體配置與間接存取開銷。

---

## Checklists & workflows｜檢查清單與流程

在進行程式碼層級優化時，請遵循以下決策流程與檢查清單：

### Optimization Workflow (優化流程)
1.  **Measure**: 使用 Profiler (e.g., pprof, JProfiler, Chrome DevTools) 捕捉基準線。
2.  **Identify**: 鎖定消耗最多 CPU 或 Memory 的 Hot Path。
3.  **Hypothesize**: 提出優化假設（例如：減少某個迴圈內的物件配置）。
4.  **Implement**: 修改程式碼。
5.  **Verify**: 再次 Benchmark，確認效能提升且無副作用（Regression）。

### Code Review Checklist for Performance
- [ ] **Hot Path Check**: 這段程式碼是否位於高頻迴圈或核心請求路徑中？
- [ ] **Complexity Check**: 這裡是否有隱藏的 O(N^2) 操作？（例如在迴圈中呼叫 `List.contains` 或 `Array.indexOf`）。
- [ ] **Memory Check**: 是否在迴圈內 `new` 了不必要的物件？是否可以使用 Static 變數或 Object Pool？
- [ ] **IO Check**: 是否在迴圈內進行 Database Query 或 Network Call？（這是效能殺手，應改為 Batch 處理）。
- [ ] **Log Check**: 在 Hot Path 上的 Log 是否有先判斷 Level？
  - *Bad*: `log.debug("User " + json.stringify(user))` (即使 log level 是 INFO，字串處理仍會執行)
  - *Good*: `if (log.isDebugEnabled()) ...`
- [ ] **Concurrency**: 是否使用了過粗顆粒度的鎖（Coarse-grained lock）導致競爭？

---

## Real-world examples｜實戰案例

### Case 1: The "N+1" Query Problem in Code (Not just DB)
**Scenario**: 一個電商系統在計算購物車總金額，需要呼叫外部服務取得匯率。

**Anti-pattern (Slow)**:
```python
# 每次迭代都發起一次網路請求或重算
def calculate_total(cart_items):
    total = 0
    for item in cart_items:
        rate = get_exchange_rate("USD") # <--- 昂貴操作在迴圈內
        total += item.price * rate
    return total
```

**Optimized**:
```python
# Hoisting: 將昂貴操作移出迴圈
def calculate_total(cart_items):
    rate = get_exchange_rate("USD") # <--- 只做一次
    total = 0
    for item in cart_items:
        total += item.price * rate
    return total
```

### Case 2: Reducing GC Pressure in High-Frequency Trading
**Scenario**: 一個金融交易系統每秒處理數萬筆 Order。

**Problem**: 系統每幾分鐘就會出現幾百毫秒的延遲（Latency Spike）。
**Analysis**: Profiling 顯示 `java.util.Date` 和 `String` 的配置佔據了 60% 的記憶體流量。原來是 Log 格式化時不斷創建新物件。

**Optimization**:
1.  將 `new Date()` 改為重用 mutable 的 Timestamp holder 或使用 `long` 傳遞時間。
2.  使用 `StringBuilder` 重用 Buffer 來格式化 Log 訊息，而不是每次都 `String.format`。
3.  結果：GC 頻率降低 80%，P99 延遲恢復平穩。

### Case 3: Data Locality (Row-major vs Column-major)
**Scenario**: 影像處理或矩陣運算。

**Concept**: 記憶體是線性的。二維陣列 `arr[row][col]` 在記憶體中通常是逐列儲存的。

**Comparison**:
- **Fast**: `for (r=0; r<R; r++) { for (c=0; c<C; c++) { sum += arr[r][c]; } }`
  - 順序存取，Cache hit rate 高。
- **Slow**: `for (c=0; c<C; c++) { for (r=0; r<R; r++) { sum += arr[r][c]; } }`
  - 跳躍存取（Stride access），導致頻繁 Cache miss。
- **Impact**: 在大矩陣運算中，這種簡單的迴圈順序交換可能帶來 2~10 倍的效能差異。