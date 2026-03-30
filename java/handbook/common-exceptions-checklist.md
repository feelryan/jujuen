# 常見致命異常排查清單 (OOM, CPU 100%) / Fatal Exceptions Troubleshooting Checklist (OOM, CPU 100%)

## Mental model｜心智模型

**致命異常是系統崩潰的「症狀」，而非可以被捕捉處理的「業務邏輯錯誤」。**
當 JVM 拋出 `OutOfMemoryError` (OOM) 或 `StackOverflowError`，或者 CPU 飆升至 100% 且無響應時，意味著 JVM 已經進入了不可靠的狀態。此時的心智模型不應該是「如何 Catch 異常讓程式繼續跑」，而是「如何保留案發現場、讓進程快速死亡（Fail-fast），並透過事後分析找出根本原因」。

**Fatal exceptions are "symptoms" of systemic collapse, not "business logic errors" to be caught and handled.**
When the JVM throws an `OutOfMemoryError` (OOM), `StackOverflowError`, or when CPU spikes to 100% and becomes unresponsive, it means the JVM has entered an unreliable state. The mental model here should not be "how to catch the exception and keep running," but rather "how to preserve the crime scene, let the process fail-fast, and find the root cause through post-mortem analysis."

將 JVM 想像成一架飛機：
- **CPU 100%**：引擎超載空轉（可能是無限迴圈、鎖競爭，或是因為沒有記憶體而瘋狂進行垃圾回收 GC Thrashing）。
- **OutOfMemoryError**：燃料耗盡或貨艙超載（記憶體洩漏、一次載入過多資料）。
- **StackOverflowError**：導航系統陷入無限遞迴的死胡同。

Think of the JVM as an airplane:
- **CPU 100%**: The engine is redlining and spinning uselessly (could be an infinite loop, lock contention, or GC thrashing because it's out of memory).
- **OutOfMemoryError**: Out of fuel or the cargo hold is overloaded (memory leaks, loading too much data at once).
- **StackOverflowError**: The navigation system is stuck in an infinitely recursive dead end.

---

## Patterns & best practices｜常見模式與最佳實務

- **自動保留案發現場 (Automated Scene Preservation)**
  永遠在正式環境的 JVM 啟動參數中加上 `-XX:+HeapDumpOnOutOfMemoryError` 與 `-XX:HeapDumpPath=...`。在容器化環境（如 Kubernetes）中，確保 Dump 檔案寫入到持久化儲存（Persistent Volume），否則 Pod 重啟後現場就會消失。
  Always include `-XX:+HeapDumpOnOutOfMemoryError` and `-XX:HeapDumpPath=...` in your production JVM arguments. In containerized environments (like Kubernetes), ensure the dump file is written to a Persistent Volume; otherwise, the scene will be lost when the Pod restarts.

- **區分 CPU 飆高的真實原因 (Distinguish the True Cause of High CPU)**
  CPU 100% 通常有兩種極端情況：一是「真的在做密集運算」（如正則表達式回溯、無限迴圈），二是「記憶體快耗盡，GC 執行緒瘋狂運轉試圖回收記憶體卻徒勞無功」（GC Thrashing）。先看記憶體與 GC 監控，再看 CPU。
  100% CPU usually stems from two extremes: one is "actually doing intensive computation" (e.g., regex backtracking, infinite loops), and the other is "memory is almost exhausted, and GC threads are running frantically trying to reclaim memory to no avail" (GC Thrashing). Always check memory and GC metrics before diving into CPU analysis.

- **優雅降級與超載保護 (Graceful Degradation and Overload Protection)**
  使用斷路器（Circuit Breakers）和超時機制（Timeouts）。如果資料庫查詢變慢，不要讓執行緒池被耗盡，這會導致後續請求堆積並引發 OOM。
  Use Circuit Breakers and Timeouts. If a database query slows down, don't let the thread pool drain entirely, which causes subsequent requests to pile up and trigger an OOM.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **捕捉 Throwable 或 Error (Catching `Throwable` or `Error`)**
  **[Anti-pattern]** 寫出 `catch (Throwable t)` 或 `catch (OutOfMemoryError e)`，然後在 catch 區塊裡嘗試印出日誌並繼續執行。
  **[Pitfall]** 當 OOM 發生時，JVM 連建立字串或寫入日誌所需的記憶體可能都沒有了。捕捉 Error 會掩蓋致命問題，導致應用程式處於「殭屍狀態」（Zombie State），既無法服務請求，也不會觸發外部監控的重啟機制。
  **[Anti-pattern]** Writing `catch (Throwable t)` or `catch (OutOfMemoryError e)` and trying to log it and continue execution.
  **[Pitfall]** When OOM occurs, the JVM might not even have enough memory to allocate strings or write logs. Catching `Error` masks fatal issues, leaving the application in a "Zombie State" where it cannot serve requests but won't trigger external restart mechanisms.

- **盲目重啟而不排查 (Blind Restarts Without Investigation)**
  **[Anti-pattern]** 遇到服務無回應，直接手動重啟 Pod 或 Server，認為「重啟治百病」。
  **[Pitfall]** 記憶體洩漏通常是緩慢累積的，重啟只是將炸彈的倒數計時器歸零。沒有 Heap Dump 或 Thread Dump，你將永遠無法修復根本原因。
  **[Anti-pattern]** Manually restarting the Pod or Server when the service is unresponsive, believing "restarting fixes everything."
  **[Pitfall]** Memory leaks usually accumulate slowly; restarting merely resets the bomb's timer. Without a Heap Dump or Thread Dump, you will never fix the root cause.

- **無分頁的全表掃描 (Unpaginated Full Table Scans)**
  **[Anti-pattern]** `List<User> users = userRepository.findAll();` 
  **[Pitfall]** 在開發環境資料量小沒問題，上正式環境資料庫有百萬筆紀錄時，瞬間就會把 Heap 記憶體撐爆，引發 `OutOfMemoryError: Java heap space`。
  **[Anti-pattern]** `List<User> users = userRepository.findAll();`
  **[Pitfall]** Works fine in dev with small data, but in production with millions of records, it will instantly blow up the Heap memory, triggering `OutOfMemoryError: Java heap space`.

---

## Checklists & workflows｜檢查清單與流程

### 🚨 CPU 100% 排查流程 (CPU 100% Troubleshooting Workflow)

- [ ] **Step 1: 確認是否為 GC 導致 (Check if caused by GC)**
  - 檢查監控面板（Grafana/Prometheus）上的 JVM GC 暫停時間與頻率。
  - 如果 GC 頻繁且記憶體使用率接近 100%，請轉移至 OOM 排查流程。
  - Check JVM GC pause times and frequency on monitoring dashboards.
  - If GC is frequent and memory usage is near 100%, switch to the OOM workflow.
- [ ] **Step 2: 找出耗用 CPU 的執行緒 (Identify the CPU-hogging thread)**
  - 執行 `top` 找出高 CPU 的 Java PID。 (Run `top` to find the Java PID).
  - 執行 `top -H -p <PID>` 找出該進程內最耗 CPU 的執行緒 ID (TID)。 (Run `top -H -p <PID>` to find the highest CPU thread ID).
  - 將 TID 轉換為十六進制：`printf "%x\n" <TID>`。 (Convert TID to hex).
- [ ] **Step 3: 擷取並分析 Thread Dump (Capture and analyze Thread Dump)**
  - 執行 `jstack <PID> > threaddump.txt`。 (Run `jstack`).
  - 在 `threaddump.txt` 中搜尋剛才轉換的十六進制 TID（例如 `nid=0x1a2b`）。
  - 觀察該執行緒的 Stack Trace，定位到具體的業務程式碼行數。
  - Search for the hex TID in the dump. Look at the stack trace to pinpoint the exact line of business code.

### 🚨 OutOfMemoryError 排查清單 (OOM Troubleshooting Checklist)

- [ ] **確認 OOM 的具體類型 (Identify the specific OOM type)**
  - `Java heap space`：物件太多或太大。 (Too many or too large objects).
  - `GC overhead limit exceeded`：98% 的時間在做 GC，但只回收了不到 2% 的記憶體（通常是記憶體洩漏的前兆）。 (98% time doing GC, recovering < 2% memory).
  - `Metaspace`：載入了過多 Class（常見於動態代理、反射濫用、熱部署）。 (Too many classes loaded).
  - `unable to create new native thread`：執行緒建立過多，或 OS 的 `ulimit` 限制太低。 (Too many threads or OS `ulimit` too low).
  - `Direct buffer memory`：NIO (如 Netty) 使用的堆外記憶體耗盡。 (Off-heap memory used by NIO exhausted).
- [ ] **取得 Heap Dump (Obtain Heap Dump)**
  - 確認是否有自動生成的 `.hprof` 檔案。 (Check for auto-generated `.hprof` file).
  - 若進程還活著，手動執行：`jcmd <PID> GC.heap_dump /path/to/dump.hprof`。
- [ ] **使用工具分析 (Analyze using tools)**
  - 將 Dump 匯入 Eclipse MAT (Memory Analyzer Tool) 或 VisualVM。 (Import dump into Eclipse MAT or VisualVM).
  - 查看 **Leak Suspects Report**（洩漏嫌疑報告）。
  - 透過 **Dominator Tree** 找出佔用記憶體最大的物件，並追蹤其 **GC Roots**，找出是哪個類別持有了這些物件導致無法回收。 (Use Dominator Tree to find the largest objects and trace their GC Roots to see what is holding them).

---

## Real-world examples｜實戰案例

### Case 1: 經典的「CPU 100%」定位 (Classic "CPU 100%" Pinpointing)

**情境 (Scenario)：** 
線上 API 突然無響應，CPU 警報顯示 100%。
Production API suddenly becomes unresponsive, CPU alert shows 100%.

**排查實戰 (Troubleshooting in action)：**
1. 透過 `top` 發現 PID `12345` 的 Java 進程 CPU 佔用 300% (多核)。
2. 執行 `top -H -p 12345`，發現 TID `12350` 佔用了 99% CPU。
3. 將 12350 轉十六進制：`printf "%x\n" 12350` 得到 `303e`。
4. 執行 `jstack 12345 | grep -A 20 "0x303e"`，得到以下輸出：

```text
"http-nio-8080-exec-5" #35 daemon prio=5 os_prio=0 tid=0x00007f8c14002000 nid=0x303e runnable [0x00007f8c45678000]
   java.lang.Thread.State: RUNNABLE
        at java.util.regex.Pattern$Loop.match(Pattern.java:4785)
        at java.util.regex.Matcher.match(Matcher.java:1270)
        at java.util.regex.Matcher.matches(Matcher.java:604)
        at com.company.utils.RegexUtil.validateInput(RegexUtil.java:25)
        // ...
```

**結論 (Conclusion)：** 
這是一個典型的**正則表達式災難性回溯 (Catastrophic Backtracking)**。開發者寫了一個效能極差的正則表達式（例如 `(a+)+$`），當遇到特定的惡意字串時，匹配引擎陷入了近乎無限的運算。修復方式是優化正則表達式或設定匹配超時。
This is a classic **Catastrophic Backtracking** in regular expressions. A poorly written regex (e.g., `(a+)+$`) encountered a specific malicious string, causing the engine to enter near-infinite computation. The fix is to optimize the regex or set a matching timeout.

### Case 2: Lombok 導致的 StackOverflowError (StackOverflowError caused by Lombok)

**情境 (Scenario)：** 
使用 Spring Data JPA 時，呼叫 `userRepository.findById()` 突然拋出 `StackOverflowError` 導致 JVM 崩潰。
When using Spring Data JPA, calling `userRepository.findById()` suddenly throws `StackOverflowError` and crashes the JVM.

**程式碼 (Code)：**
```java
@Data // Anti-pattern here!
@Entity
public class User {
    @Id private Long id;
    @OneToMany(mappedBy = "user")
    private List<Order> orders;
}

@Data // Anti-pattern here!
@Entity
public class Order {
    @Id private Long id;
    @ManyToOne
    private User user;
}
```

**根本原因 (Root Cause)：**
Lombok 的 `@Data` 會自動生成 `toString()`, `equals()`, 和 `hashCode()`。在雙向關聯 (Bidirectional relationship) 中，`User.toString()` 會呼叫 `Order.toString()`，而 `Order.toString()` 又會呼叫 `User.toString()`，形成無限遞迴，最終撐爆 Thread Stack。
Lombok's `@Data` automatically generates `toString()`, `equals()`, and `hashCode()`. In a bidirectional relationship, `User.toString()` calls `Order.toString()`, which calls `User.toString()` again, creating an infinite recursion that eventually blows up the Thread Stack.

**解決方案 (Solution)：**
在 JPA Entity 中**永遠不要**使用 `@Data` 或 `@EqualsAndHashCode`。請明確使用 `@Getter` 和 `@Setter`，並手動實作不包含關聯物件的 `toString()`，或者在關聯欄位上加上 `@ToString.Exclude`。
**Never** use `@Data` or `@EqualsAndHashCode` on JPA Entities. Use `@Getter` and `@Setter` explicitly, and manually implement `toString()` excluding associated objects, or use `@ToString.Exclude` on the relationship fields.