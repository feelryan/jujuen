# 記憶體洩漏診斷與 Troubleshooting / Memory Leak Diagnostics and Troubleshooting

## Mental model｜心智模型

在 Java 的世界裡，因為有垃圾回收機制（Garbage Collection, GC），我們不會遇到 C/C++ 那種「忘記釋放記憶體」的傳統洩漏。Java 的記憶體洩漏本質上是**「非預期的物件保留」（Unintentional Object Retention）**。

In the Java ecosystem, thanks to Garbage Collection (GC), we don't encounter traditional memory leaks like "forgetting to free memory" seen in C/C++. A Java memory leak is fundamentally **"Unintentional Object Retention"**.

想像 GC 是一個極度保守的清潔工，他只會丟掉「沒有任何人牽著」的垃圾。只要你的程式碼中還有一條**強引用（Strong Reference）**鏈條連接著某個物件，甚至一路連回 **GC Roots**（例如：靜態變數、執行緒的本地變數），GC 就絕對不敢回收它。

Imagine the GC as an extremely conservative cleaner who only throws away trash that "no one is holding onto". As long as there is a **Strong Reference** chain in your code connecting to an object, tracing all the way back to **GC Roots** (e.g., static variables, thread local variables), the GC will absolutely not reclaim it.

診斷記憶體洩漏的核心心智模型，就是**「找尋那條不該存在的引用鏈」**。在分析工具（如 Eclipse MAT）中，你必須區分兩個關鍵概念：
- **Shallow Heap（淺層堆積）**：物件本身佔用的記憶體大小。
- **Retained Heap（保留堆積）**：如果這個物件被回收，連帶能釋放出的總記憶體大小。**這才是抓漏的關鍵指標。**

The core mental model for diagnosing memory leaks is **"finding that reference chain that shouldn't exist"**. When using analysis tools like Eclipse MAT (Memory Analyzer Tool), you must distinguish between two critical concepts:
- **Shallow Heap**: The memory consumed by the object itself.
- **Retained Heap**: The total amount of memory that would be freed if this object were garbage collected. **This is the key metric for leak hunting.**

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 永遠開啟 OOM 自動 Heap Dump / Always Enable Automatic Heap Dump on OOM
不要依賴手動抓取，因為當發生 `OutOfMemoryError` 時，應用程式通常已經崩潰或無回應。在 JVM 啟動參數中加上這兩行是生產環境的鐵律：
Never rely on manual capturing, because when an `OutOfMemoryError` occurs, the application is usually already crashing or unresponsive. Adding these two lines to your JVM startup arguments is an ironclad rule for production:
```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/java/heapdump.hprof
```

### 2. 使用 JCMD 進行活體診斷 / Use JCMD for Live Diagnostics
如果發現 Old Gen 持續攀升，但還沒觸發 OOM，你可以使用 JDK 內建的 `jcmd` 工具手動導出 Heap Dump：
If you notice the Old Gen steadily climbing but OOM hasn't been triggered yet, you can manually export a Heap Dump using the JDK built-in `jcmd` tool:
```bash
# 取得 PID / Get PID
jps -l
# 導出 Heap Dump (建議加上 -all=false 只 dump 存活物件)
# Export Heap Dump (recommend -all=false to dump only live objects)
jcmd <PID> GC.heap_dump /tmp/manual-dump.hprof
```

### 3. MAT 分析三板斧 / The Three-Step MAT Analysis
在 Eclipse MAT 中打開 `.hprof` 檔案後，請遵循以下標準流程：
After opening the `.hprof` file in Eclipse MAT, follow this standard workflow:
1. **Leak Suspects Report（洩漏嫌疑報告）**：MAT 會自動幫你找出佔用 Retained Heap 最大的幾個嫌疑犯。
   **Leak Suspects Report**: MAT automatically identifies the suspects consuming the most Retained Heap.
2. **Dominator Tree（支配樹）**：以 Retained Heap 排序，找出是「誰」把這些龐大的物件圖（Object Graph）給 Keep alive 的。
   **Dominator Tree**: Sorted by Retained Heap, this shows "who" is keeping these massive Object Graphs alive.
3. **Path to GC Roots（通往 GC Roots 的路徑）**：對著嫌疑物件點擊右鍵 -> `Path To GC Roots` -> `exclude all phantom/weak/soft etc. references`，這會精準告訴你是哪一行程式碼（哪個變數）抓著它不放。
   **Path to GC Roots**: Right-click the suspect object -> `Path To GC Roots` -> `exclude all phantom/weak/soft etc. references`. This precisely tells you which line of code (which variable) is holding onto it.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 無邊界的快取（The Infinite Cache）
**Pitfall**: 使用 `HashMap` 或 `ConcurrentHashMap` 實作快取，卻沒有設定最大容量上限或過期機制（TTL）。
**Pitfall**: Using `HashMap` or `ConcurrentHashMap` to implement a cache without setting a maximum capacity limit or Time-To-Live (TTL) mechanism.
**Consequence**: 隨著時間推移，Map 越來越大，最終撐爆 Old Gen。
**Consequence**: Over time, the Map grows indefinitely, eventually blowing up the Old Gen.
**Fix**: 永遠使用成熟的快取庫（如 Caffeine、Guava Cache），或者在特定情境下使用 `WeakHashMap`。
**Fix**: Always use mature caching libraries (like Caffeine, Guava Cache), or use `WeakHashMap` in specific scenarios.

### 2. ThreadLocal 忘記清理（Uncleaned ThreadLocal in Thread Pools）
**Pitfall**: 在 Web 應用程式（如 Tomcat、Spring Boot）中使用 `ThreadLocal` 儲存使用者上下文，但在 Request 結束時忘記呼叫 `remove()`。
**Pitfall**: Using `ThreadLocal` to store user context in web applications (like Tomcat, Spring Boot), but forgetting to call `remove()` at the end of the request.
**Consequence**: 因為 Web 伺服器使用執行緒池（Thread Pool），執行緒會被重複使用。舊的資料會一直殘留在執行緒上，導致嚴重的記憶體洩漏與潛在的資安越權風險。
**Consequence**: Because web servers use Thread Pools, threads are reused. Old data remains attached to the thread, causing severe memory leaks and potential security cross-talk risks.

### 3. 迷失在 Shallow Heap 中（Getting Lost in Shallow Heap）
**Pitfall**: 在 MAT 的 Histogram 中看到 `byte[]` 或 `java.lang.String` 佔用最多記憶體，就盲目去查字串問題。
**Pitfall**: Seeing `byte[]` or `java.lang.String` consuming the most memory in MAT's Histogram and blindly investigating string issues.
**Consequence**: 浪費時間。幾乎所有 Java 應用的底層資料都是字串和位元組陣列。
**Consequence**: Wasting time. The underlying data of almost all Java applications consists of strings and byte arrays.
**Fix**: 應該關注 **Retained Heap**，找出是哪個「業務物件（Business Object）」或「集合（Collection）」持有了這些海量的字串。
**Fix**: You should focus on the **Retained Heap** to find out which "Business Object" or "Collection" is holding onto these massive amounts of strings.

---

## Checklists & workflows｜檢查清單與流程

當監控系統發出 OOM 警告，或是 GC Overhead 飆高時，請依照此清單行動：
When the monitoring system alerts an OOM, or GC Overhead spikes, follow this checklist:

### Phase 1: 收集與保護現場 / Collection & Preservation
- [ ] 檢查伺服器是否已自動生成 `.hprof` 檔案（確認啟動參數 `-XX:+HeapDumpOnOutOfMemoryError`）。
      Check if the server automatically generated the `.hprof` file (verify the startup argument `-XX:+HeapDumpOnOutOfMemoryError`).
- [ ] 如果應用程式處於假死狀態（CPU 100% 且 GC 頻繁），使用 `jcmd <PID> GC.heap_dump` 手動抓取。
      If the application is in a zombie state (100% CPU with frequent GC), manually capture using `jcmd <PID> GC.heap_dump`.
- [ ] 將 Heap Dump 檔案下載到**本地開發機**進行分析（千萬不要在生產伺服器上跑 MAT，會消耗大量記憶體）。
      Download the Heap Dump file to your **local development machine** for analysis (NEVER run MAT on the production server; it consumes massive memory).

### Phase 2: MAT 分析流程 / MAT Analysis Workflow
- [ ] 開啟 MAT，載入 Dump 檔，選擇 `Leak Suspects Report`。
      Open MAT, load the Dump file, and select `Leak Suspects Report`.
- [ ] 在報告中尋找佔用超過 20%~30% Retained Heap 的單一物件或類別。
      Look for a single object or class consuming more than 20%~30% of the Retained Heap in the report.
- [ ] 開啟 `Dominator Tree`，展開最大的節點，觀察其內部結構（通常會看到某個 `ArrayList` 或 `ConcurrentHashMap`）。
      Open the `Dominator Tree`, expand the largest node, and observe its internal structure (you'll usually see an `ArrayList` or `ConcurrentHashMap`).
- [ ] 對該節點執行 `Path To GC Roots` -> `exclude all phantom/weak/soft etc. references`。
      Execute `Path To GC Roots` -> `exclude all phantom/weak/soft etc. references` on that node.
- [ ] 記錄下 GC Root 的確切類別與變數名稱（例如：`com.example.service.OrderService.failedOrdersCache`）。
      Note the exact class and variable name of the GC Root (e.g., `com.example.service.OrderService.failedOrdersCache`).

### Phase 3: 修復與驗證 / Fix & Verification
- [ ] 檢視對應的程式碼，確認為何該物件沒有被移除。
      Review the corresponding code to confirm why the object wasn't removed.
- [ ] 修正程式碼（加入清理邏輯、改用 WeakReference、或使用具備 TTL 的 Cache）。
      Fix the code (add cleanup logic, switch to WeakReference, or use a Cache with TTL).
- [ ] 在本地端使用壓測工具（如 JMeter 或 K6）重現情境，並使用 VisualVM 或 JConsole 確認 Old Gen 呈現健康的鋸齒狀回收曲線。
      Reproduce the scenario locally using load testing tools (like JMeter or K6), and use VisualVM or JConsole to verify that the Old Gen shows a healthy sawtooth recovery curve.

---

## Real-world examples｜實戰案例

### 案例：未註銷的監聽器（The Lapsed Listener Problem）
這是一個極度常見的企業級應用記憶體洩漏場景。開發者實作了一個事件發布/訂閱機制，但忘記在物件銷毀時取消註冊。
This is an extremely common memory leak scenario in enterprise applications. The developer implemented an event publish/subscribe mechanism but forgot to unregister when the object was destroyed.

**❌ 錯誤示範 (Anti-pattern):**
```java
public class EventManager {
    // 靜態集合作為 GC Root，生命週期與應用程式一樣長
    // Static collection acts as a GC Root, lifecycle is as long as the application
    private static final List<EventListener> listeners = new ArrayList<>();

    public static void register(EventListener listener) {
        listeners.add(listener);
    }
}

public class UserSession implements EventListener {
    private byte[] sessionData = new byte[1024 * 1024]; // 1MB data

    public UserSession() {
        // 註冊了，但從未取消註冊！
        // Registered, but never unregistered!
        EventManager.register(this); 
    }
    
    @Override
    public void onEvent(Event e) { /* ... */ }
}
```
**MAT 診斷結果 / MAT Diagnostic Result:**
在 MAT 的 Dominator Tree 中，你會看到 `EventManager.listeners` 佔用了 90% 的 Retained Heap。展開後發現裡面塞滿了數以萬計的 `UserSession` 物件。因為 `EventManager` 是 static 的（GC Root），導致所有 `UserSession` 都無法被回收。
In MAT's Dominator Tree, you will see `EventManager.listeners` consuming 90% of the Retained Heap. Expanding it reveals tens of thousands of `UserSession` objects. Because `EventManager` is static (a GC Root), none of the `UserSession` objects can be garbage collected.

**✅ 修復方案 (Best Practice):**
方案 A：在 `UserSession` 結束生命週期時，明確呼叫 `EventManager.unregister(this)`。
方案 B：使用 `WeakReference` 來儲存 Listeners，讓 GC 能夠自動介入。
Option A: Explicitly call `EventManager.unregister(this)` when the `UserSession` ends its lifecycle.
Option B: Use `WeakReference` to store Listeners, allowing the GC to intervene automatically.

```java
public class EventManager {
    // 使用 WeakHashMap 的 Key 來儲存 Weak Reference
    // Using WeakHashMap's Key to store Weak References
    private static final Set<EventListener> listeners = 
        Collections.newSetFromMap(new WeakHashMap<>());

    public static void register(EventListener listener) {
        listeners.add(listener);
    }
}
```
*註：改用 `WeakHashMap` 後，當 `UserSession` 在其他地方不再被強引用時，GC 發生時就會自動將其從 `listeners` 集合中剔除，完美解決記憶體洩漏。*
*Note: By switching to `WeakHashMap`, when `UserSession` is no longer strongly referenced elsewhere, the GC will automatically remove it from the `listeners` collection during the next cycle, perfectly solving the memory leak.*