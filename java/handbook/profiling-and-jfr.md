# 效能分析與 JDK Flight Recorder (JFR) / Profiling and JDK Flight Recorder (JFR)

## Mental model｜心智模型

將 JFR 想像成飛機的**「黑盒子」（Black Box）**。它深深嵌入在 JVM 內部，以極低的開銷（通常小於 1-2%）持續記錄應用程式的運行狀態（CPU、記憶體、鎖、GC、I/O 等）。與傳統的採樣或插樁（Instrumentation）效能分析工具不同，JFR 是專為 Production 環境設計的。
> Think of JFR as the **"black box"** of an airplane. It is deeply embedded within the JVM, continuously recording the application's state (CPU, memory, locks, GC, I/O, etc.) with incredibly low overhead (typically < 1-2%). Unlike traditional sampling or instrumenting profilers, JFR is explicitly designed for Production environments.

JDK Mission Control (JMC) 則是解讀這個黑盒子的**「儀表板」**。JFR 負責在背景默默「收集」，而當系統發生異常（如 CPU 飆高、記憶體洩漏、延遲突增）時，我們將 JFR 資料傾印（Dump）出來，交由 JMC 進行「視覺化與分析」。
> JDK Mission Control (JMC) is the **"dashboard"** used to decode this black box. JFR handles the silent "collection" in the background. When anomalies occur (e.g., CPU spikes, memory leaks, latency surges), we dump the JFR data and feed it into JMC for "visualization and analysis."

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 在 Production 環境預設啟用持續記錄 / Enable Continuous Recording in Production by Default
不要等到出問題才開啟 Profiler。在啟動參數中配置 JFR，保留最近一段時間或一定大小的記錄檔。當系統崩潰時，你可以獲得崩潰前的寶貴數據。
> Do not wait until a problem occurs to start a profiler. Configure JFR in your startup arguments to keep a rolling buffer of recent history based on time or size. When the system crashes, you will have invaluable pre-crash data.

```bash
# Java 11+ 建議的啟動參數 / Recommended JVM args for Java 11+
java -XX:StartFlightRecording=disk=true,maxage=1d,maxsize=1G,dumponexit=true,filename=/var/log/app/crash.jfr -jar app.jar
```

### 2. 使用 `jcmd` 進行動態管理 / Dynamic Management via `jcmd`
在不停機的情況下，你可以透過 `jcmd` 工具隨時啟動、停止或傾印 JFR 記錄。
> You can start, stop, or dump JFR recordings on the fly without downtime using the `jcmd` tool.

```bash
# 找出 Java 行程 ID / Find Java PID
jcmd

# 將目前的 JFR 記錄傾印出來分析 / Dump current JFR recording for analysis
jcmd <PID> JFR.dump filename=/tmp/investigation.jfr path-to-gc-roots=true
```

### 3. 建立自訂 JFR 事件 (Custom JFR Events) / Create Custom JFR Events
JFR 不僅能記錄 JVM 系統事件，你還可以繼承 `jdk.jfr.Event` 來記錄業務邏輯（例如：特定的外部 API 呼叫、複雜的定價計算）。這比寫 Log 效能更好，且能與 JVM 底層事件在同一條時間線上關聯分析。
> JFR isn't just for JVM system events. You can extend `jdk.jfr.Event` to record business logic (e.g., specific external API calls, complex pricing calculations). This is much more performant than logging and allows you to correlate business events with underlying JVM events on the same timeline.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 在 Production 使用 `settings=profile` / Using `settings=profile` in Production
JFR 有兩種內建設定檔：`default`（開銷 < 2%）與 `profile`（開銷約 2-5% 或更高）。在 Production 環境長期運行時，若誤用 `profile` 會收集過多詳細的 Method Sampling 與 Exception 資料，拖慢系統效能。
> **Pitfall:** JFR has two built-in configurations: `default` (overhead < 2%) and `profile` (overhead ~2-5%+). Running `profile` continuously in production collects excessive method sampling and exception data, degrading system performance. Stick to `default` for continuous recording.

### ❌ 將 JFR 視為 Metrics 或 Logs 的替代品 / Treating JFR as a Replacement for Metrics or Logs
JFR 的資料格式是二進位的，且需要手動或透過工具 Dump 出來分析。它不適合用來做「即時告警（Real-time Alerting）」或「分散式追蹤（Distributed Tracing）」。
> **Pitfall:** JFR data is binary and requires dumping for analysis. It is not suited for "Real-time Alerting" or "Distributed Tracing." Use Prometheus/Grafana for metrics, ELK for logs, and JFR strictly for deep-dive performance troubleshooting.

### ❌ 忽略磁碟空間管理 / Ignoring Disk Space Management
如果啟動 JFR 時沒有設定 `maxsize` 或 `maxage`，JFR 的暫存檔可能會無限制增長，最終導致伺服器磁碟爆滿 (`No space left on device`)。
> **Pitfall:** If you start JFR without setting `maxsize` or `maxage`, the JFR temporary files can grow indefinitely, eventually causing the server disk to fill up (`No space left on device`). Always set bounds.

---

## Checklists & workflows｜檢查清單與流程

當面對未知的效能瓶頸時，請遵循以下 JFR 排查標準流程：
> Follow this standard JFR troubleshooting workflow when facing unknown performance bottlenecks:

- [ ] **Data Collection (資料收集)**
  - [ ] 確認目標 JVM 已啟用 JFR (或透過 `jcmd <PID> JFR.start` 立即開啟)。 / Verify JFR is enabled on the target JVM (or start it immediately via `jcmd <PID> JFR.start`).
  - [ ] 在效能問題發生的當下，執行 `jcmd <PID> JFR.dump filename=issue.jfr`。 / Execute `jcmd <PID> JFR.dump filename=issue.jfr` while the performance issue is occurring.
- [ ] **JMC Analysis: Automated Results (JMC 分析：自動化結果)**
  - [ ] 在 JMC 打開 `.jfr` 檔案，首先查看 **Automated Analysis Results (自動分析結果)** 頁籤，JMC 會以紅/黃燈標示最可能的問題（如記憶體壓力、執行緒阻塞）。 / Open the `.jfr` file in JMC and first check the **Automated Analysis Results** tab. JMC highlights the most probable issues (e.g., memory pressure, thread blocking) with red/yellow indicators.
- [ ] **JMC Analysis: CPU & Hotspots (JMC 分析：CPU 與熱點)**
  - [ ] 進入 **Method Profiling** 頁籤，查看哪個方法佔用了最多的 CPU Sample。 / Go to the **Method Profiling** tab to see which methods consume the most CPU samples.
- [ ] **JMC Analysis: Memory & GC (JMC 分析：記憶體與垃圾回收)**
  - [ ] 進入 **Memory -> Garbage Collections** 頁籤，檢查 GC 暫停時間 (Pause Times) 是否過長。 / Go to the **Memory -> Garbage Collections** tab to check if GC pause times are excessively long.
  - [ ] 進入 **Memory -> Allocations** 頁籤，找出產生最多短命物件 (Short-lived objects) 的程式碼位置 (TLAB allocations)。 / Go to the **Memory -> Allocations** tab to find the code locations generating the most short-lived objects (TLAB allocations).
- [ ] **JMC Analysis: Threads & Locks (JMC 分析：執行緒與鎖)**
  - [ ] 進入 **Threads -> Lock Instances** 頁籤，檢查是否有特定 Monitor 造成大量執行緒等待 (Contention)。 / Go to the **Threads -> Lock Instances** tab to check if a specific Monitor is causing massive thread waiting (Contention).

---

## Real-world examples｜實戰案例

### 案例一：診斷隱蔽的鎖競爭 (Diagnosing Hidden Lock Contention)
**情境 / Scenario:** 
系統 CPU 使用率極低（< 10%），但 API 回應時間卻異常緩慢。
> System CPU usage is extremely low (< 10%), but API response times are abnormally slow.

**JFR 排查過程 / JFR Troubleshooting:**
1. Dump 出 JFR 檔案並載入 JMC。 / Dump the JFR file and load it into JMC.
2. 導航至 `Threads -> Lock Instances`。 / Navigate to `Threads -> Lock Instances`.
3. 發現 `java.util.Hashtable` 的 `put` 方法產生了極長的 Blocked Time。 / Discovered that the `put` method of a `java.util.Hashtable` generated extremely long Blocked Times.
4. **解決方案 / Solution:** 將遺留程式碼中的 `Hashtable` 替換為 `ConcurrentHashMap`，消除全局鎖，API 延遲瞬間恢復正常。 / Replaced the legacy `Hashtable` with `ConcurrentHashMap` to eliminate the global lock, and API latency instantly returned to normal.

### 案例二：實作自訂業務事件 (Implementing Custom Business Events)
**情境 / Scenario:** 
我們想知道某個第三方金流 API 的呼叫耗時，並且希望這個耗時能跟 JVM 的 GC 暫停時間放在同一個圖表對比，以釐清「慢是因為網路，還是因為剛好遇到 GC」。
> We want to track the latency of a third-party payment API call and compare it on the same chart as JVM GC pause times, to clarify "is it slow because of the network, or because a GC happened at the same time?"

**實作程式碼 / Implementation Code:**

```java
import jdk.jfr.Event;
import jdk.jfr.Label;
import jdk.jfr.Category;
import jdk.jfr.Description;

// 1. 定義事件 / Define the Event
@Category({"Business", "Payment"})
@Label("Payment API Call")
@Description("Records the latency and details of external payment gateway calls")
public class PaymentApiEvent extends Event {
    @Label("Transaction ID")
    String transactionId;

    @Label("Gateway Name")
    String gatewayName;
    
    @Label("Response Code")
    int responseCode;
}

// 2. 在業務邏輯中使用 / Use it in business logic
public void processPayment(String txId) {
    PaymentApiEvent event = new PaymentApiEvent();
    event.transactionId = txId;
    event.gatewayName = "Stripe";
    
    event.begin(); // 開始計時 / Start timing
    try {
        // ... 呼叫外部 API 的邏輯 / External API call logic ...
        event.responseCode = 200;
    } catch (Exception e) {
        event.responseCode = 500;
        throw e;
    } finally {
        event.commit(); // 結束計時並寫入 JFR / Stop timing and write to JFR
    }
}
```
*優勢 / Advantage:* 這些事件會以二進位格式寫入 Thread-local buffer，開銷極低。在 JMC 中，你可以直接看到 `Payment API Call` 事件，並與同一時間點的 `Garbage Collection` 事件重疊比對。 / *These events are written to thread-local buffers in binary format with negligible overhead. In JMC, you can view the `Payment API Call` events directly and overlay them with `Garbage Collection` events occurring at the exact same time.*