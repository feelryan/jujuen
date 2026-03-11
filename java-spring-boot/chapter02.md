# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，JVM 不應只是一個黑盒子。當 Spring Boot 應用程式在高併發場景下面臨延遲抖動（Latency Jitter）或記憶體溢出（OOM）時，深入理解 JVM 記憶體模型與 GC 機制是解決問題的關鍵。本章旨在提升你對底層運作機制的掌控力。

For senior engineers, the JVM should not be a black box. When a Spring Boot application faces latency jitter or OutOfMemory (OOM) errors under high concurrency, a deep understanding of the JVM Memory Model and GC mechanisms is critical for troubleshooting. This chapter aims to enhance your control over these underlying mechanisms.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇 GC 演算法**：根據業務需求（高吞吐量 vs 低延遲），在 G1、ZGC 或 Parallel GC 之間做出最佳選擇。
    **Select GC algorithms precisely:** Choose the optimal collector (G1, ZGC, or Parallel GC) based on business requirements (High Throughput vs. Low Latency).
2.  **排查記憶體洩漏與效能瓶頸**：利用 Heap Dump 與 Thread Dump 分析工具，定位 Spring Bean 或 ThreadLocal 造成的洩漏。
    **Troubleshoot memory leaks and bottlenecks:** Use Heap Dump and Thread Dump analysis tools to pinpoint leaks caused by Spring Beans or ThreadLocals.
3.  **理解 JIT 優化機制**：解釋 Escape Analysis（逃逸分析）與 Inlining（內聯）如何影響程式碼撰寫風格與效能。
    **Understand JIT optimization:** Explain how Escape Analysis and Inlining affect coding style and performance.
4.  **配置容器化 JVM 參數**：在 Kubernetes 環境中正確設置 Heap Size 與 CPU 限制，避免容器被 OOM Kill。
    **Configure containerized JVM parameters:** Correctly set Heap Size and CPU limits in Kubernetes environments to prevent container OOM Kills.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 JMM 規範 vs. JVM 運行時數據區 (JMM Spec vs. Runtime Data Areas)

很多工程師會混淆「Java 記憶體模型 (JMM)」與「JVM 記憶體結構」。
Many engineers confuse the "Java Memory Model (JMM)" with the "JVM Memory Structure".

*   **JVM 記憶體結構 (Runtime Data Areas)**：這是物理上的記憶體劃分，包含 **Heap** (Young/Old Gen)、**Stack** (Method Frames)、**Metaspace** (Class Metadata) 與 **Code Cache**。
    **JVM Memory Structure (Runtime Data Areas):** This is the physical division of memory, including **Heap** (Young/Old Gen), **Stack** (Method Frames), **Metaspace** (Class Metadata), and **Code Cache**.
*   **Java 記憶體模型 (JMM)**：這是一組抽象的規範，定義了多執行緒環境下變數的**可見性 (Visibility)**、**原子性 (Atomicity)** 與 **有序性 (Ordering)**（例如 `volatile` 與 `happens-before` 規則）。
    **Java Memory Model (JMM):** This is an abstract specification defining variable **Visibility**, **Atomicity**, and **Ordering** in multi-threaded environments (e.g., `volatile` and `happens-before` rules).

**心智模型 (Mental Model)**：
將 **Stack** 想像成執行緒的私有工作檯（存放區域變數、方法呼叫鏈），生命週期短；將 **Heap** 想像成所有執行緒共享的倉庫（存放物件實例），生命週期長且需定期清理（GC）。
**Mental Model:**
Imagine the **Stack** as a thread's private workbench (holding local variables, method call chains), which is short-lived. Imagine the **Heap** as a shared warehouse for all threads (holding object instances), which is long-lived and requires periodic cleaning (GC).

## 2.2 垃圾回收演算法的演進 (Evolution of GC Algorithms)

GC 的核心權衡永遠是：**Throughput（吞吐量）** vs. **Latency（延遲/暫停時間）**。
The core trade-off of GC is always: **Throughput** vs. **Latency (Pause Time)**.

1.  **Parallel GC**: 吞吐量優先。適合後台批次處理任務。STW (Stop-The-World) 時間較長。
    **Parallel GC:** Throughput-first. Suitable for background batch processing. Longer STW (Stop-The-World) times.
2.  **CMS (Concurrent Mark Sweep)**: *已棄用*。追求低延遲，但有記憶體碎片化問題。
    **CMS (Concurrent Mark Sweep):** *Deprecated*. Aimed for low latency but suffered from memory fragmentation.
3.  **G1 (Garbage-First)**: 平衡型。將 Heap 切分為多個 Region，可預測暫停時間。是 JDK 8 (後期) 到 JDK 17+ 的主流預設。
    **G1 (Garbage-First):** Balanced. Divides Heap into multiple Regions, offering predictable pause times. The mainstream default from JDK 8 (later versions) to JDK 17+.
4.  **ZGC / Shenandoah**: 極低延遲 (< 1ms)。透過 Colored Pointers 或 Load Barriers 實現並發整理。適合超大 Heap (TB 級) 或對延遲極敏感的服務。
    **ZGC / Shenandoah:** Ultra-low latency (< 1ms). Achieves concurrent compaction via Colored Pointers or Load Barriers. Suitable for massive Heaps (TB scale) or highly latency-sensitive services.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 微服務架構中的 JVM 調校 (JVM Tuning in Microservices)

在 Kubernetes 環境中，Spring Boot 應用通常運行在資源受限的容器內（例如 2GB RAM, 1 CPU）。
In a Kubernetes environment, Spring Boot applications often run inside resource-constrained containers (e.g., 2GB RAM, 1 CPU).

*   **Container Awareness**: 必須開啟 `-XX:+UseContainerSupport`（JDK 10+ 預設開啟），否則 JVM 可能會讀取到宿主機（Host）的記憶體大小，導致錯誤計算 Heap Size 而被 OOM Kill。
    **Container Awareness:** Must enable `-XX:+UseContainerSupport` (default in JDK 10+); otherwise, the JVM might read the Host's memory size, leading to miscalculated Heap Size and OOM Kills.
*   **MaxRAMPercentage**: 建議使用 `-XX:MaxRAMPercentage=75.0` 而非寫死 `-Xmx`。這樣當調整 K8s `resources.limits.memory` 時，JVM 會自動適配。
    **MaxRAMPercentage:** It is recommended to use `-XX:MaxRAMPercentage=75.0` instead of hardcoding `-Xmx`. This allows the JVM to adapt automatically when K8s `resources.limits.memory` changes.

## 3.2 高併發 API Gateway (High Concurrency API Gateway)

對於承載大量請求的 Gateway 服務（如 Spring Cloud Gateway）：
For Gateway services handling massive requests (e.g., Spring Cloud Gateway):

*   **物件生命週期極短**：大量的 Request/Response 物件在 Young Gen 快速生滅。
    **Extremely short object lifecycle:** Massive amounts of Request/Response objects are created and destroyed quickly in the Young Gen.
*   **調校策略**：應適度放大 Young Gen 比例，避免物件過早晉升（Premature Promotion）到 Old Gen，減少 Full GC 頻率。
    **Tuning Strategy:** Moderately increase the Young Gen ratio to prevent objects from Premature Promotion to the Old Gen, reducing Full GC frequency.

---

# 4. 逐步示例：排查記憶體洩漏 (Walkthrough: Troubleshooting Memory Leak)

## 4.1 問題背景 (Scenario)

一個 Spring Boot 電商訂單服務，在運行 3 天後，回應時間逐漸變慢，最終拋出 `java.lang.OutOfMemoryError: Java heap space`。重啟後恢復，但 3 天後復發。
A Spring Boot e-commerce order service slows down gradually after running for 3 days, eventually throwing `java.lang.OutOfMemoryError: Java heap space`. It recovers after a restart but recurs after another 3 days.

## 4.2 排查步驟 (Troubleshooting Steps)

### Step 1: 獲取現場證據 (Capture Evidence)
設定 JVM 參數，確保下次崩潰時自動生成 Dump：
Set JVM parameters to ensure a Dump is automatically generated upon the next crash:
`-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/dumps/`

或者在服務變慢但尚未崩潰時，手動觸發：
Or manually trigger it when the service slows down but hasn't crashed yet:
`jmap -dump:live,format=b,file=heap.bin <pid>`

### Step 2: 使用 MAT 分析 (Analyze with MAT)
使用 Eclipse Memory Analyzer Tool (MAT) 開啟 `heap.bin`。
Open `heap.bin` using Eclipse Memory Analyzer Tool (MAT).

*   **Dominator Tree**: 查看佔用記憶體最大的物件。
    **Dominator Tree:** Check for objects consuming the most memory.
*   **Path to GC Roots**: 找出是誰引用了這些物件，導致它們無法被回收。
    **Path to GC Roots:** Identify who is referencing these objects, preventing them from being collected.

### Step 3: 發現問題 (Identify the Issue)
發現大量的 `OrderContext` 物件被一個 `static final Map<String, UserSession>` 持有。
Found massive `OrderContext` objects held by a `static final Map<String, UserSession>`.

*   **原因**：開發者試圖實作一個簡單的 Cache，但沒有實作過期機制（Eviction Policy）。這是一個經典的記憶體洩漏。
    **Root Cause:** The developer tried to implement a simple Cache but failed to implement an Eviction Policy. This is a classic memory leak.

### Step 4: 修復方案 (Solution)
**Naive Solution**: 手動寫排程清理 Map。 (容易出錯且非執行緒安全)
**Naive Solution:** Manually write a scheduler to clean the Map. (Error-prone and not thread-safe)

**Mature Solution**: 使用 Caffeine Cache 或 Guava Cache，並設定 `expireAfterWrite`。
**Mature Solution:** Use Caffeine Cache or Guava Cache and set `expireAfterWrite`.

```java
// Replaced static Map with Caffeine
Cache<String, UserSession> sessionCache = Caffeine.newBuilder()
    .expireAfterWrite(10, TimeUnit.MINUTES)
    .maximumSize(10_000)
    .build();
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `System.gc()` (Abusing `System.gc()`)

*   **錯誤描述**：在程式碼中顯式呼叫 `System.gc()`。
    **Description:** Explicitly calling `System.gc()` in the code.
*   **為何不好**：這會建議 JVM 進行 Full GC，通常會觸發長時間的 STW，嚴重影響效能。現代 JVM 懂得何時該 GC。
    **Why it's bad:** This suggests the JVM perform a Full GC, usually triggering a long STW, severely impacting performance. Modern JVMs know when to GC.
*   **最佳實踐**：使用 `-XX:+DisableExplicitGC` 參數禁用它，並信任 GC 演算法。
    **Best Practice:** Use `-XX:+DisableExplicitGC` to disable it and trust the GC algorithm.

## 5.2 忽視 String 去重與 Interning (Ignoring String Deduplication & Interning)

*   **錯誤描述**：在處理大量重複字串（如 JSON key、XML tag）時，產生了海量 String 實例。
    **Description:** Creating massive String instances when processing large amounts of repetitive strings (e.g., JSON keys, XML tags).
*   **為何不好**：佔用大量 Heap 空間。
    **Why it's bad:** Consumes significant Heap space.
*   **最佳實踐**：
    1.  對於 G1GC，開啟 `-XX:+UseStringDeduplication`（JVM 會自動去重底層 char[]）。
    2.  謹慎使用 `String.intern()`，因為 String Pool 位於 Heap 中，過大也會導致效能問題。
    **Best Practice:**
    1.  For G1GC, enable `-XX:+UseStringDeduplication` (JVM automatically deduplicates underlying char[]).
    2.  Use `String.intern()` cautiously, as the String Pool resides in the Heap; making it too large can also cause performance issues.

## 5.3 ThreadLocal 洩漏 (ThreadLocal Leaks)

*   **錯誤描述**：在 Thread Pool 環境（如 Tomcat 執行緒）中使用 `ThreadLocal`，但在請求結束後忘記呼叫 `remove()`。
    **Description:** Using `ThreadLocal` in a Thread Pool environment (e.g., Tomcat threads) but forgetting to call `remove()` after the request ends.
*   **為何不好**：執行緒是被重複使用的，舊的 `ThreadLocal` 值會一直存在，導致記憶體洩漏甚至業務邏輯錯誤（讀到別人的資料）。
    **Why it's bad:** Threads are reused; old `ThreadLocal` values persist, leading to memory leaks or even business logic errors (reading someone else's data).
*   **最佳實踐**：務必在 `finally` 區塊中呼叫 `threadLocal.remove()`。
    **Best Practice:** Always call `threadLocal.remove()` in the `finally` block.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何決定 Spring Boot 應用程式的 Heap Size？
**How do you determine the Heap Size for a Spring Boot application?**

*   **高分回答要點 (Key Points)**：
    *   **Baseline**: 透過壓力測試（Load Testing）觀察穩定狀態下的 Live Data Size（Full GC 後的老年代大小）。
    *   **Rule of Thumb**: 通常建議 Heap Size 設為 Live Data Size 的 3-4 倍。
    *   **Container**: 預留一部分記憶體給 Non-Heap（Metaspace, Code Cache, Thread Stacks, Direct Buffers）以及 OS 本身，避免容器 OOM。通常 `-Xmx` 設為容器限制的 70%-80%。

## Q2: G1 GC 的 "Region" 概念解決了什麼問題？
**What problem does the "Region" concept in G1 GC solve?**

*   **高分回答要點 (Key Points)**：
    *   解決了 CMS 在大記憶體下碎片化的問題。
    *   G1 不再物理隔離 Eden/Survivor/Old，而是將 Heap 切分為許多 Region。
    *   這允許 G1 預測暫停時間（Pause Prediction Model），只回收垃圾最多的 Region（Garbage-First），從而在大 Heap 下也能保持可控的延遲。

## Q3: 什麼是 JIT 的 "Escape Analysis"（逃逸分析）？
**What is JIT's "Escape Analysis"?**

*   **高分回答要點 (Key Points)**：
    *   JIT 編譯器會分析一個物件的作用域是否逃出了方法體（例如被 return 或賦值給 static 變數）。
    *   如果沒有逃逸，JIT 可以進行 **Stack Allocation**（在 Stack 上分配物件，隨方法結束自動銷毀，無需 GC）或 **Scalar Replacement**（將物件拆解為純量變數，直接放在暫存器中）。
    *   這大幅減少了 Heap 的分配壓力和 GC 頻率。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **JMM vs JVM**: 區分規範（Visibility/Atomicity）與實作（Heap/Stack）。
2.  **GC 選擇**: Web 服務首選 G1（JDK 8+）或 ZGC（JDK 17+ 低延遲場景）；批次處理選 Parallel。
3.  **容器化**: 務必使用 `-XX:MaxRAMPercentage` 與 `-XX:+UseContainerSupport`。
4.  **排查工具**: 熟練使用 `jmap`, `jstack`, `jcmd` 以及 MAT 進行分析。
5.  **洩漏防範**: 注意 `static` 集合類、`ThreadLocal` 清理以及未關閉的 I/O 資源。

## 後續延伸 (Next Steps)
*   **Chapter 03**: **Java Concurrency & Multithreading**
    *   既然理解了記憶體模型，下一步是深入探討如何安全地操作這些共享記憶體。我們將討論 `CompletableFuture`、Virtual Threads (Project Loom) 以及高階鎖機制。
    *   Now that you understand the memory model, the next step is to dive into safely manipulating this shared memory. We will discuss `CompletableFuture`, Virtual Threads (Project Loom), and advanced locking mechanisms.