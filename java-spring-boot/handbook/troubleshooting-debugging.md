# 生產環境故障排除與除錯流程 / Production Troubleshooting & Debugging Workflow

## Mental model｜心智模型

在生產環境（Production）進行除錯與開發環境截然不同。你無法隨意暫停程式（Debug Breakpoint）、無法隨意重啟，且必須在有限的資訊下迅速決策。

建立正確的心智模型是成功的關鍵：

1.  **犯罪現場調查員 (CSI) 模式**：
    *   **保存現場 (Preserve Evidence)**：在重啟應用程式或採取緩解措施前，必須先收集證據（Logs, Thread Dumps, Heap Dumps）。一旦重啟，記憶體與執行緒狀態將永遠消失。
    *   **黑盒子與 X 光 (Black Box vs. X-Ray)**：應用程式是黑盒子，Logs 是它說的話，Metrics 是它的生命徵象（心跳、血壓），而 Dumps（Heap/Thread）則是 X 光片，能透視內部結構。
2.  **資源瓶頸三角 (The Resource Triangle)**：
    *   大多數效能或穩定性問題最終都會歸結為三個維度之一：**CPU**（計算過載或無窮迴圈）、**Memory**（洩漏或配置不足）、**IO**（資料庫鎖定、網路延遲或磁碟滿載）。
3.  **分層剝洋蔥 (The Onion Layering)**：
    *   問題是發生在 **Infrastructure** (K8s/Docker)? **JVM** (GC/JIT)? **Framework** (Spring Context)? 還是 **Business Logic**? 由外而內排查。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 自動化現場保存 (Automated Evidence Collection)
不要依賴人工在發生事故時手動抓取 Dump，通常那時候已經太遲了。
*   **OOM 自動 Dump**：在 JVM 啟動參數中務必加入：
    `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/app/heap-dump.hprof`
*   **OOM Killer 防護**：在容器化環境（Docker/K8s）中，確保 JVM 的 MaxRAMPercentage 設定正確，避免 JVM 還沒 OOM 就先被 Linux OOM Killer 殺掉（這樣不會產生 Heap Dump）。

### 2. 執行緒分析標準動作 (Thread Dump Analysis)
當 CPU 飆高或請求卡住（Hang）時，Thread Dump 是唯一解藥。
*   **使用 Spring Boot Actuator**：如果應用程式還活著，優先使用 `/actuator/threaddump` 獲取快照。
*   **使用 `jcmd` (JDK Native)**：如果 Actuator 無回應，進入容器使用 `jcmd <pid> Thread.print`。
*   **分析重點**：
    *   尋找 `BLOCKED` 狀態的執行緒（通常暗示 Deadlock 或鎖競爭）。
    *   尋找 `RUNNABLE` 但 Stack Trace 深陷在同一業務邏輯的執行緒（暗示無窮迴圈或高運算）。
    *   **Waiting for DB Connection**：大量執行緒停在 `HikariDataSource.getConnection`，代表 DB Pool 耗盡。

### 3. 記憶體洩漏排查 (Memory Leak Hunting)
*   **Shallow vs. Retained Heap**：分析 Heap Dump 時（使用 Eclipse MAT 或 VisualVM），關注 **Retained Heap**（該物件及其引用的所有物件釋放後能回收的大小），而非 Shallow Heap。
*   **Dominator Tree**：找出佔用記憶體最大的物件群（The "Big Fish"）。
*   **GC Roots**：追蹤是誰「抓著」這些物件不放。常見兇手：`static` 變數、未清理的 `ThreadLocal`、無上限的 `Cache`。

### 4. 啟動緩慢排查 (Slow Startup Troubleshooting)
*   **Spring Boot Startup Actuator**：使用 Spring Boot 3+ 的 Startup tracking 功能。
    *   依賴：`spring-boot-starter-actuator`
    *   配置：開啟 Buffering `SpringApplication.setApplicationStartup(new BufferingApplicationStartup(2048));`
    *   分析：打 `/actuator/startup` API，查看哪個 Bean 初始化耗時最久。
*   **Lazy Initialization**：對於非核心路徑的 Bean，考慮 `spring.main.lazy-initialization=true`（需謹慎評估副作用）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 膝反射式重啟 (The "Reflexive Restart")
*   **反模式**：遇到問題第一反應是 `kubectl delete pod` 或重啟服務。
*   **後果**：雖然服務暫時恢復，但 Root Cause 被掩蓋，Heap Dump 和 Thread 狀態丟失，問題必定會再次發生（通常在半夜）。
*   **修正**：先執行 Script 抓取 Dump，再重啟。

### 2. 生產環境開啟 DEBUG Log (Global DEBUG Logging)
*   **反模式**：為了查錯，將 root logger level 設為 DEBUG。
*   **後果**：Log 檔案瞬間爆炸，Disk I/O 飆升，導致應用程式變慢甚至崩潰（Heisenbug：觀測行為改變了系統行為）。
*   **修正**：使用 Spring Boot Admin 或 Actuator 動態調整 **特定 Package** 的 Log Level (`/actuator/loggers/{name}`)。

### 3. 誤判 "Used Memory" (Misinterpreting Memory Usage)
*   **反模式**：看到 OS 層面（如 `top` 指令）記憶體佔用高就認為是 Heap Leak。
*   **後果**：花時間分析 Heap 卻找不到問題。
*   **修正**：區分 **Heap Memory** 與 **Non-Heap Memory** (Metaspace, Direct Buffers, Code Cache, Thread Stacks)。使用 `Native Memory Tracking (NMT)` 排查堆外記憶體洩漏。

### 4. 忽視 Stop-The-World (STW)
*   **反模式**：應用程式間歇性卡頓，卻在 Thread Dump 中看不出鎖競爭。
*   **後果**：誤以為是網路問題或 DB 慢。
*   **修正**：檢查 GC Log。Full GC 導致的 STW 會暫停所有應用程式執行緒。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 CPU 飆高排查流程 (High CPU Workflow)

- [ ] **Step 1: 定位 PID**
    - 使用 `top` 或 `docker stats` 確認是 Java Process 佔用 CPU。
- [ ] **Step 2: 定位 Thread ID (TID)**
    - Linux: `top -H -p <pid>` 找出佔用 CPU 最高的執行緒 ID。
    - 轉換 TID 為 16 進位：`printf "%x\n" <tid>` (例如 100 -> 0x64)。
- [ ] **Step 3: 抓取 Thread Dump**
    - `jcmd <pid> Thread.print > thread_dump.txt` 或 `kill -3 <pid>` (輸出至 stdout)。
- [ ] **Step 4: 對應分析**
    - 在 `thread_dump.txt` 中搜尋 `nid=0x64` (步驟 2 的結果)。
    - 查看該執行緒的 Stack Trace。是正在做複雜計算？Regex？還是 JSON 序列化？

### 🚨 OutOfMemoryError (OOM) 處理清單

- [ ] **Step 1: 確認 OOM 類型**
    - `Java heap space`: Heap 滿了（洩漏或配置過小）。
    - `Metaspace`: 載入太多 Classes（常見於動態代理濫用）。
    - `GC overhead limit exceeded`: CPU 都在做 GC 且回收極少記憶體。
    - `Direct buffer memory`: NIO/Netty 堆外記憶體不足。
- [ ] **Step 2: 取得 Heap Dump**
    - 是否有自動生成的 `.hprof` 檔案？
    - 若無，且 Process 還在，手動執行 `jmap -dump:format=b,file=heap.hprof <pid>`。
- [ ] **Step 3: 使用工具分析 (Eclipse MAT / VisualVM)**
    - 開啟 Histogram，看哪個 Class 實例數量異常。
    - 執行 "Leak Suspects Report"。
    - 檢查 Dominator Tree，找出佔用記憶體最大的物件。
- [ ] **Step 4: 程式碼修正**
    - 修正 Collection 無限增長問題。
    - 調整 JVM Heap Size (`-Xmx`)。

### 🐢 應用程式啟動失敗/緩慢檢核

- [ ] **Dependency Hell**: 是否有 `NoSuchMethodError` 或 `ClassNotFoundException`？檢查 Maven/Gradle 依賴樹 (`mvn dependency:tree`) 是否有版本衝突。
- [ ] **Port Conflict**: 錯誤訊息 `Web server failed to start. Port 8080 was already in use`。檢查是否有舊的 Process 未關閉。
- [ ] **Bean Creation Exception**: 閱讀 Stack Trace 最底層的 `Caused by`。通常是 `@Autowired` 失敗或設定檔屬性缺失。
- [ ] **Slow Startup**:
    - 資料庫連線是否超時？（防火牆/VPN 問題）。
    - 是否在 `@PostConstruct` 做了耗時操作（如載入大檔案、打外部 API）？
    - 是否掃描了過多不必要的 Package (`@ComponentScan`)？

---

## Real-world examples｜實戰案例

### Case 1: The "Silent Killer" (ThreadLocal Leak)

**情境**：應用程式運作一週後，頻繁發生 OOM 重啟。Heap Dump 顯示有大量 `Tomcat-exec` 執行緒持有巨大的 `Map` 物件。

**分析**：
開發者在處理 Request 時使用了 `ThreadLocal` 來暫存使用者 Context 資訊，但在 Request 結束後（`finally` block 或 Filter 中）**忘記呼叫 `remove()`**。
由於 Tomcat 使用 Thread Pool，執行緒不會被銷毀，ThreadLocal 中的物件就一直累積，最終導致 Memory Leak。

**Code Fix**:
```java
// Anti-pattern
public void process(User user) {
    UserContextHolder.set(user);
    service.doLogic();
    // Missing remove()!
}

// Best Practice
public void process(User user) {
    try {
        UserContextHolder.set(user);
        service.doLogic();
    } finally {
        // Must clean up
        UserContextHolder.remove();
    }
}
```

### Case 2: The "Frozen App" (Database Pool Exhaustion)

**情境**：系統突然無回應，CPU 使用率極低，但 Log 停止輸出。

**分析**：
Thread Dump 顯示數百個執行緒處於 `WAITING` 狀態，Stack Trace 停在：
`com.zaxxer.hikari.pool.HikariPool.getConnection`。
這表示 DB Connection Pool 已經被借光了，所有新進請求都在排隊等待連線釋放。

**Root Cause**:
某個慢查詢（Slow Query）佔用連線超過 30 秒，或者某段程式碼開啟了 Transaction 但在執行外部 HTTP 請求（耗時長），導致連線長時間不歸還。

**Action**:
1.  檢查 DB 端的鎖定情況與慢查詢日誌。
2.  優化程式碼：將耗時的外部 API 呼叫移出 `@Transactional` 範圍。

### Case 3: The "CPU Spike" (Regex Catastrophe)

**情境**：某個 API 只要被呼叫，CPU 就會瞬間飆到 100%，導致其他服務變慢。

**分析**：
透過 `top -H` 抓到 TID，轉 Hex 後在 Thread Dump 發現該執行緒卡在 `java.util.regex.Pattern$Loop.match`。

**Root Cause**:
使用了效能極差的正則表達式（ReDoS 攻擊風險），例如 `(a+)+b` 匹配大量 `aaaa...` 字串。

**Action**:
優化 Regex，或設定 Regex 執行的 timeout 機制。