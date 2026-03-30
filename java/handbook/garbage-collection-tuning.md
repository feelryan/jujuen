# 垃圾回收機制 (GC) 與調校實務 / Garbage Collection Mechanisms and Tuning

## Mental model｜心智模型

理解 JVM 垃圾回收機制，首先要拋棄「完美 GC」的幻想。在實務上，GC 是一個關於**權衡 (Trade-offs)** 的工程問題。
To understand JVM Garbage Collection, first abandon the illusion of a "perfect GC." In practice, GC is an engineering problem about **trade-offs**.

請記住 **GC 不可能三角 (The GC Iron Triangle)**：
Remember **The GC Iron Triangle**:
1. **吞吐量 (Throughput)**：應用程式執行業務邏輯的時間比例（非 GC 停頓時間）。 / The percentage of time the application spends running business logic (not paused for GC).
2. **延遲/停頓時間 (Latency / Pause Time)**：GC 執行時導致應用程式暫停的時間長度（Stop-The-World, STW）。 / The duration the application is paused while GC runs (Stop-The-World, STW).
3. **記憶體足跡 (Memory Footprint)**：JVM 運行所需的總記憶體量。 / The total memory required by the JVM to run.

**現代 GC 的演進 (Evolution of Modern GCs)：**
- **G1 (Garbage-First)**：Java 9 起的預設收集器。它將 Heap 切分成多個 Region，透過預測模型來達成「軟性」的停頓時間目標（預設 200ms）。**定位：吞吐量與延遲的良好平衡。**
  **G1 (Garbage-First)**: The default collector since Java 9. It divides the Heap into Regions and uses a predictive model to meet a "soft" pause time target (default 200ms). **Positioning: A good balance between throughput and latency.**
- **ZGC (Z Garbage Collector)**：Java 15 轉正，Java 21 引入分代 (Generational) ZGC。透過 Colored Pointers 與 Load Barriers 達成幾乎所有階段的併發執行。停頓時間通常小於 1ms，且不隨 Heap 大小增加。**定位：極致的超低延遲，但可能犧牲少許吞吐量或需要更多 CPU 資源。**
  **ZGC (Z Garbage Collector)**: Production-ready in Java 15, Generational ZGC introduced in Java 21. Achieves concurrent execution in almost all phases via Colored Pointers and Load Barriers. Pause times are typically <1ms and do not increase with Heap size. **Positioning: Ultra-low latency, but may sacrifice some throughput or require more CPU resources.**

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 依據 SLA 選擇合適的收集器 / Choose the Right Collector Based on SLA
- **預設選 G1**：對於 80% 的微服務與一般應用，G1 的開箱即用效能已經足夠。
  **Default to G1**: For 80% of microservices and general applications, G1's out-of-the-box performance is sufficient.
- **嚴格延遲要求選 ZGC**：如果你的應用是金融交易系統、即時競價 (RTB) 或對 P99 延遲極度敏感的 API，請切換至 ZGC（建議使用 JDK 17，最好是 JDK 21+）。
  **Choose ZGC for strict latency**: If your app is a financial trading system, Real-Time Bidding (RTB), or an API highly sensitive to P99 latency, switch to ZGC (recommend JDK 17, ideally JDK 21+).

### 2. 鎖定 Heap 大小以避免擴容開銷 / Lock Heap Size to Avoid Resizing Overhead
在正式環境中，永遠將初始 Heap (`-Xms`) 與最大 Heap (`-Xmx`) 設為相同大小。這能避免 JVM 在運行期間動態調整 Heap 大小所帶來的效能抖動與延遲。
In production, always set the initial Heap (`-Xms`) and maximum Heap (`-Xmx`) to the same size. This prevents performance jitter and latency caused by the JVM dynamically resizing the Heap during runtime.

### 3. 宣告你的目標，讓 JVM 自己努力 / Declare Your Goals, Let the JVM Do the Work
現代 GC 非常聰明。對於 G1，你應該設定目標，而不是微調內部參數。
Modern GCs are smart. For G1, you should set targets rather than micro-managing internal parameters.
- **Do**: `-XX:MaxGCPauseMillis=100` (告訴 G1 你期望的停頓時間 / Tell G1 your desired pause time).
- **Don't**: 手動設定 `-XX:NewRatio` 或 `-XX:SurvivorRatio`，這會破壞 G1 的自適應預測機制。 / Manually setting `-XX:NewRatio` or `-XX:SurvivorRatio`, which breaks G1's adaptive predictability.

### 4. 啟用統一日誌紀錄 / Enable Unified JVM Logging
沒有日誌就無法調校。從 Java 9 開始，使用 `-Xlog` 取代舊版的 `-XX:+PrintGCDetails`。
You cannot tune without logs. Since Java 9, use `-Xlog` instead of the legacy `-XX:+PrintGCDetails`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 複製貼上祖傳的 JVM 參數 / Copy-pasting Ancestral JVM Flags
**Pitfall**: 在 Java 17 專案中看到 `-XX:+UseConcMarkSweepGC` 或一堆 CMS 專用的微調參數。
**Pitfall**: Seeing `-XX:+UseConcMarkSweepGC` or a bunch of CMS-specific tuning flags in a Java 17 project.
**Consequence**: CMS 已經被移除。舊參數會導致 JVM 無法啟動，或者干擾現代 GC 的運作。永遠從最少的參數開始，有證據才加參數。
**Consequence**: CMS has been removed. Old flags will cause the JVM to fail to start or interfere with modern GCs. Always start with minimal flags and add them only when you have evidence.

### 2. 容器環境下的記憶體盲區 / Memory Blindness in Container Environments
**Pitfall**: 在 Docker/Kubernetes 中設定了 `-Xmx4G`，但 Pod 的記憶體限制也是 `4Gi`。
**Pitfall**: Setting `-Xmx4G` in Docker/Kubernetes, while the Pod's memory limit is also `4Gi`.
**Consequence**: JVM 除了 Heap 之外，還需要 Native Memory (Metaspace, Threads, Code Cache)。這會導致 Linux 內核觸發 **OOMKilled**。
**Consequence**: The JVM needs Native Memory (Metaspace, Threads, Code Cache) in addition to the Heap. This will trigger the Linux kernel's **OOMKilled**.
**Fix**: 使用 `-XX:MaxRAMPercentage=75.0` 讓 JVM 自動感知容器限制。 / Use `-XX:MaxRAMPercentage=75.0` to let the JVM automatically sense container limits.

### 3. 試圖用 GC 調校解決記憶體洩漏 / Trying to Fix Memory Leaks with GC Tuning
**Pitfall**: 發現頻繁 Full GC 或 `OutOfMemoryError`，第一反應是調大 `-Xmx` 或換 GC 演算法。
**Pitfall**: Encountering frequent Full GCs or `OutOfMemoryError`, and the first reaction is to increase `-Xmx` or change the GC algorithm.
**Consequence**: 如果程式碼有 Memory Leak，調大 Heap 只是延後死亡時間，且會讓 Full GC 的停頓時間變得更長。如果 Full GC 後記憶體使用量依然居高不下，請去抓 Heap Dump 分析程式碼，而不是調 GC。
**Consequence**: If there is a memory leak in the code, increasing the Heap only delays the inevitable crash and makes Full GC pause times even longer. If memory usage remains high after a Full GC, capture a Heap Dump and analyze the code, don't tune the GC.

---

## Checklists & workflows｜檢查清單與流程

當你面臨疑似 GC 造成的效能問題時，請遵循以下流程：
When facing performance issues suspected to be caused by GC, follow this workflow:

- [ ] **Step 1: 驗證是否真的是 GC 問題 / Verify if it's actually a GC issue**
  - 檢查監控指標 (Prometheus/Grafana) 或 GC Log。
  - GC 停頓時間是否真的超過了 SLA？(例如 P99 延遲飆高時，是否剛好發生了長暫停的 GC？)
  - *Check monitoring metrics or GC Logs. Did GC pause times actually breach the SLA? (e.g., when P99 latency spiked, was there a long GC pause at the exact same time?)*
- [ ] **Step 2: 排除記憶體洩漏 / Rule out Memory Leaks**
  - 觀察 GC 後的 Heap 使用量趨勢。如果呈現不斷上升的階梯狀，請停止調校 GC，轉向 Memory Leak 診斷 (使用 Eclipse MAT 或 JFR)。
  - *Observe the Heap usage trend after GCs. If it shows a continuously rising staircase pattern, stop GC tuning and switch to Memory Leak diagnostics (using Eclipse MAT or JFR).*
- [ ] **Step 3: 檢查容器與作業系統限制 / Check Container and OS limits**
  - 確認應用程式沒有被 Kubernetes OOMKilled (Exit Code 137)。
  - *Ensure the application is not being OOMKilled by Kubernetes (Exit Code 137).*
- [ ] **Step 4: 收集並分析 GC Log / Collect and Analyze GC Logs**
  - 將 GC Log 匯入工具 (如 GCeasy.io) 進行視覺化分析。
  - 確認是哪種階段耗時最長 (例如：是 G1 的 Evacuation Pause，還是 Concurrent Mark 週期太晚啟動？)
  - *Import GC Logs into tools (like GCeasy.io) for visual analysis. Identify which phase takes the longest (e.g., is it G1's Evacuation Pause, or did the Concurrent Mark cycle start too late?)*
- [ ] **Step 5: 最小化參數調整與驗證 / Minimal Parameter Adjustment and Verification**
  - 每次只調整 1 到 2 個參數，部署到 Staging 環境進行壓測 (Load Testing)，對比調整前後的吞吐量與延遲。
  - *Adjust only 1 or 2 parameters at a time, deploy to a Staging environment for load testing, and compare throughput and latency before and after the change.*

---

## Real-world examples｜實戰案例

### Example 1: 現代微服務的標準啟動參數 (G1 in Kubernetes)
這是在 Kubernetes 環境下運行 Java 17+ 微服務最推薦的「安全牌」配置。
This is the most recommended "safe bet" configuration for running Java 17+ microservices in a Kubernetes environment.

```bash
java \
  -XX:+UseG1GC \
  # 讓 JVM 使用容器限制的 75% 記憶體作為 Heap，保留 25% 給 Native Memory
  # Let JVM use 75% of container limit for Heap, leaving 25% for Native Memory
  -XX:InitialRAMPercentage=75.0 \
  -XX:MaxRAMPercentage=75.0 \
  # 告訴 G1 盡量將停頓時間控制在 100ms 內 (預設為 200ms)
  # Tell G1 to try keeping pause times under 100ms (default is 200ms)
  -XX:MaxGCPauseMillis=100 \
  # 輸出 GC 日誌到檔案，包含時間戳記，並設定檔案輪轉 (Log Rotation)
  # Output GC logs to file with timestamps, and configure log rotation
  -Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=10M \
  # 發生 OOM 時自動產生 Heap Dump 以供事後調查
  # Automatically generate a Heap Dump on OOM for post-mortem investigation
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/ \
  -jar my-microservice.jar
```

### Example 2: 超低延遲服務配置 (Generational ZGC)
如果你的服務是即時報價系統，無法忍受超過 5ms 的延遲，在 JDK 21+ 下請使用分代 ZGC。
If your service is a real-time quoting system that cannot tolerate delays over 5ms, use Generational ZGC on JDK 21+.

```bash
java \
  # 啟用 ZGC / Enable ZGC
  -XX:+UseZGC \
  # 在 JDK 21 中啟用分代 ZGC (大幅降低 CPU 開銷與分配停頓)
  # Enable Generational ZGC in JDK 21 (significantly reduces CPU overhead and allocation stalls)
  -XX:+ZGenerational \
  -Xms8G -Xmx8G \
  # ZGC 不需要設定 MaxGCPauseMillis，因為它的設計目標就是 <1ms
  # ZGC doesn't need MaxGCPauseMillis because its design goal is <1ms
  -Xlog:gc*:file=/var/log/app/gc-zgc.log:time \
  -jar low-latency-trading.jar
```

### Example 3: 讀懂 G1 GC Log 片段 / Reading a G1 GC Log Snippet
當你打開 GC Log，你可能會看到類似這樣的行：
When you open a GC Log, you might see lines like this:

```text
[info][gc] GC(123) Pause Young (Normal) (G1 Evacuation Pause) 1024M->400M(2048M) 45.123ms
```

**工程師的解讀 (Engineer's Interpretation)：**
- `GC(123)`: 這是 JVM 啟動以來的第 123 次 GC。 / *This is the 123rd GC since JVM startup.*
- `Pause Young (Normal)`: 這是一次年輕代 GC，應用程式被暫停了 (STW)。 / *This is a Young generation GC, the application was paused (STW).*
- `1024M->400M(2048M)`: GC 前 Heap 使用了 1024M，GC 後剩下 400M（回收了 624M）。Heap 的總大小是 2048M。 / *Heap usage was 1024M before GC, 400M after (reclaimed 624M). Total Heap capacity is 2048M.*
- `45.123ms`: **這就是你的延遲 (Latency)**。應用程式停頓了約 45 毫秒。如果你的 `-XX:MaxGCPauseMillis` 設為 50ms，那 G1 表現得很好。 / ***This is your latency***. *The application paused for ~45ms. If your `-XX:MaxGCPauseMillis` is 50ms, G1 is doing a great job.*