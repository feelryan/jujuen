## 1. 前言與學習目標
## 1. Introduction and Learning Objectives

在 Production 環境中，系統效能退化或無預警崩潰是資深工程師最常面臨的挑戰。對於具備多年經驗的 Java 開發者而言，僅僅知道「什麼是 GC」已經不夠；你必須具備系統化的排障（Troubleshooting）能力，能在高壓環境下快速定位 CPU 飆高、Memory Leak 或 P99 延遲突增的根本原因。
In production environments, performance degradation or unexpected crashes are the most common challenges faced by senior engineers. For Java developers with years of experience, simply knowing "what GC is" is no longer sufficient; you must possess systematic troubleshooting skills to quickly identify the root causes of CPU spikes, memory leaks, or P99 latency surges under high pressure.

完成本章後，你應該能做到以下幾點：
After completing this chapter, you should be able to:

*   **精通 JVM 診斷工具鏈**：能在 Production 環境安全地使用 JFR (Java Flight Recorder)、JMC (JDK Mission Control) 與 async-profiler 進行低開銷（Low-overhead）的效能剖析。
    **Master the JVM Diagnostic Toolchain**: Safely use JFR (Java Flight Recorder), JMC (JDK Mission Control), and async-profiler in production for low-overhead performance profiling.
*   **系統化破解 CPU 與 Memory 異常**：掌握從 OS 層級到 JVM Thread/Heap Dump 的標準排查 SOP，精準定位問題程式碼。
    **Systematically Resolve CPU and Memory Anomalies**: Master the standard troubleshooting SOP from the OS level to JVM Thread/Heap Dumps to pinpoint problematic code accurately.
*   **實務級 GC 調校與評估**：理解 G1GC 與 ZGC 的適用場景，並能根據延遲（Latency）與吞吐量（Throughput）需求制定調校策略，而非盲目複製網路上的 JVM 參數。
    **Practical GC Tuning and Evaluation**: Understand the use cases for G1GC and ZGC, and formulate tuning strategies based on latency and throughput requirements, rather than blindly copying JVM flags from the internet.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)
## 2. Core Concepts & Mental Model

### JVM 作為一個「微型作業系統」
### The JVM as a "Micro-Operating System"

要精通線上問題診斷，請將 JVM 視為一個運行在 Host OS 之上的「微型作業系統」。它有自己的記憶體管理（Heap/Metaspace）、執行緒排程（Java Threads mapped to OS Threads）以及監控子系統（JMX/JFR）。當問題發生時，我們必須區分是「Host OS 資源耗盡」還是「JVM 內部資源耗盡」。
To master online diagnostics, treat the JVM as a "micro-operating system" running on top of the Host OS. It has its own memory management (Heap/Metaspace), thread scheduling (Java Threads mapped to OS Threads), and monitoring subsystems (JMX/JFR). When an issue occurs, we must distinguish whether it is "Host OS resource exhaustion" or "JVM internal resource exhaustion."

### 採樣 (Sampling) vs. 插樁 (Instrumentation)
### Sampling vs. Instrumentation

在進行效能剖析（Profiling）時，資深工程師必須理解工具背後的原理，以避免在 Production 環境引發災難：
When profiling performance, senior engineers must understand the principles behind the tools to avoid causing disasters in production:

*   **插樁 (Instrumentation)**：如傳統 APM 或 BTrace，透過修改 Bytecode 插入監控程式碼。優點是精準，缺點是開銷極大（Overhead 高達 10-50%），且可能改變程式行為（Observer Effect）。
    **Instrumentation**: Like traditional APMs or BTrace, it inserts monitoring code by modifying bytecode. The pros are precision, but the cons are massive overhead (10-50%) and potential alteration of program behavior (Observer Effect).
*   **採樣 (Sampling)**：如 JFR 或 async-profiler，以固定頻率（如每 10ms）中斷執行緒並記錄 Stack Trace。優點是開銷極低（通常 < 2%），非常適合 Production 環境。
    **Sampling**: Like JFR or async-profiler, it interrupts threads at a fixed frequency (e.g., every 10ms) to record stack traces. The pros are extremely low overhead (usually < 2%), making it highly suitable for production environments.

### 安全點 (Safepoint) 與 Stop-The-World (STW)
### Safepoint and Stop-The-World (STW)

許多工程師以為只有 GC 會觸發 STW，這是錯誤的心智模型。JVM 在執行許多全域操作時（如 Heap Dump、Thread Dump、Revoke Biased Locking、JIT Deoptimization），都需要所有執行緒到達「安全點（Safepoint）」才能暫停。如果某個執行緒執行了耗時的迴圈且沒有 Safepoint Polling，會導致整個 JVM 等待，造成嚴重的 P99 延遲。
Many engineers mistakenly believe that only GC triggers STW. This is a flawed mental model. When the JVM performs many global operations (e.g., Heap Dump, Thread Dump, Revoke Biased Locking, JIT Deoptimization), it requires all threads to reach a "Safepoint" before pausing. If a thread executes a time-consuming loop without Safepoint polling, it will cause the entire JVM to wait, resulting in severe P99 latency spikes.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)
## 3. Real-World & System Design View

### 雲原生環境下的診斷挑戰 (Diagnostic Challenges in Cloud-Native Environments)

在 Kubernetes (K8s) 等容器化環境中，Java 應用的 Troubleshooting 變得更加複雜：
In containerized environments like Kubernetes (K8s), troubleshooting Java applications becomes more complex:

1.  **OOMKilled vs. OutOfMemoryError**：當 Pod 消失時，必須釐清是 Linux Kernel 觸發了 `OOMKilled`（通常是 Native Memory 洩漏或 `-Xmx` 設定不當導致超出 Container Limit），還是 JVM 拋出了 `java.lang.OutOfMemoryError`（Heap 空間不足）。
    **OOMKilled vs. OutOfMemoryError**: When a Pod disappears, you must clarify whether the Linux Kernel triggered an `OOMKilled` (usually due to a Native Memory leak or improper `-Xmx` setting exceeding the Container Limit) or the JVM threw a `java.lang.OutOfMemoryError` (Heap space exhausted).
2.  **Liveness Probe 失敗**：長時間的 GC STW 或 Safepoint 延遲，會導致 K8s Liveness Probe 逾時，進而觸發 Pod 重啟。這會掩蓋真正的效能問題，讓工程師誤以為是網路異常。
    **Liveness Probe Failures**: Prolonged GC STW or Safepoint delays can cause K8s Liveness Probes to time out, triggering Pod restarts. This masks the real performance issue, leading engineers to mistakenly suspect network anomalies.

### 架構層面的防禦性設計 (Defensive Design at the Architectural Level)

從系統設計視角來看，我們不能僅依賴 JVM 調校來解決所有問題。必須透過架構設計來隔離風險：
From a system design perspective, we cannot rely solely on JVM tuning to solve all problems. We must isolate risks through architectural design:

*   **Bulkheading (艙壁模式)**：為不同的業務邏輯配置獨立的 Thread Pool，防止單一慢速 API 耗盡所有 Tomcat/Jetty Worker Threads。
    **Bulkheading**: Allocate independent Thread Pools for different business logics to prevent a single slow API from exhausting all Tomcat/Jetty Worker Threads.
*   **Continuous Profiling (持續效能剖析)**：現代架構傾向於在 Production 預設開啟 JFR（透過 `-XX:StartFlightRecording`），並將資料串流至 Datadog 或 Grafana Pyroscope，實現事後溯源（Post-mortem analysis）。
    **Continuous Profiling**: Modern architectures tend to enable JFR by default in production (via `-XX:StartFlightRecording`) and stream the data to Datadog or Grafana Pyroscope, enabling post-mortem analysis.

---

## 4. 逐步示例 (Walkthrough / Example)
## 4. Walkthrough / Example

### 案例一：Production 環境 CPU 100% 飆高排查
### Scenario 1: Troubleshooting 100% CPU Spike in Production

**背景 (Background)**：監控系統發出告警，某個訂單服務的 CPU 使用率突然飆升至 100% 且居高不下。
**Background**: The monitoring system alerts that the CPU usage of an order service has suddenly spiked to 100% and remains high.

**傳統/初階做法 (Naive Approach)**：
直接重啟服務（Restart the service）。這會破壞犯罪現場，導致問題在幾小時後再次發生。
Directly restart the service. This destroys the crime scene, causing the issue to recur a few hours later.

**資深工程師的標準 SOP (Senior Engineer's SOP)**：

1.  **找出耗用 CPU 的 OS Thread ID (Find the OS Thread ID consuming CPU)**:
    ```bash
    # 假設 Java PID 為 1234
    # Assume Java PID is 1234
    top -H -p 1234
    ```
    假設發現 OS Thread ID `1250` 佔用了 99% CPU。
    Assume we find OS Thread ID `1250` consuming 99% CPU.

2.  **將十進位 PID 轉為十六進位 (Convert Decimal PID to Hexadecimal)**:
    ```bash
    printf "%x\n" 1250
    # 輸出 (Output): 4e2
    ```

3.  **產生 Thread Dump 並定位程式碼 (Generate Thread Dump and Locate Code)**:
    ```bash
    jstack 1234 > thread_dump.txt
    grep -A 20 "nid=0x4e2" thread_dump.txt
    ```
    此時你可能會看到類似以下的 Stack Trace，精準指出是哪個迴圈或正則表達式導致了 CPU 飆高（例如：Catastrophic Backtracking）。
    At this point, you might see a Stack Trace similar to the following, pinpointing exactly which loop or regular expression caused the CPU spike (e.g., Catastrophic Backtracking).

**現代更佳實踐 (Modern Best Practice)**：
使用 `async-profiler` 直接生成火焰圖（Flame Graph），這在微服務環境下更直覺。
Use `async-profiler` to generate a Flame Graph directly, which is more intuitive in a microservices environment.
```bash
./profiler.sh -d 30 -f cpu_flamegraph.html 1234
```

### 案例二：Memory Leak 與 OOM 診斷
### Scenario 2: Memory Leak and OOM Diagnostics

**背景 (Background)**：系統運行幾天後，記憶體使用量呈現階梯式上升，最終拋出 `java.lang.OutOfMemoryError: Java heap space`。
**Background**: After running for a few days, the system's memory usage shows a step-like increase, eventually throwing `java.lang.OutOfMemoryError: Java heap space`.

**排查步驟 (Troubleshooting Steps)**：

1.  **保留犯罪現場 (Preserve the Crime Scene)**：
    確保啟動參數包含以下設定，讓 JVM 在 OOM 瞬間自動倒出 Heap Dump。
    Ensure the startup parameters include the following settings so the JVM automatically dumps the heap at the exact moment of OOM.
    ```text
    -XX:+HeapDumpOnOutOfMemoryError
    -XX:HeapDumpPath=/var/log/jvm/heapdump.hprof
    ```

2.  **使用 Eclipse MAT 或 JMC 分析 (Analyze with Eclipse MAT or JMC)**：
    *   載入 `heapdump.hprof`。
    *   打開 **Dominator Tree（支配樹）**：這會列出佔用最多 Retained Heap 的物件。
    *   尋找 **GC Roots**：對可疑的巨大集合（如 `HashMap` 或 `ArrayList`）執行 "Path to GC Roots" -> "exclude all phantom/weak/soft etc. references"。
    * Load `heapdump.hprof`.
    * Open the **Dominator Tree**: This lists the objects consuming the most Retained Heap.
    * Find **GC Roots**: For suspicious large collections (like `HashMap` or `ArrayList`), execute "Path to GC Roots" -> "exclude all phantom/weak/soft etc. references".

**常見的實務發現 (Common Practical Findings)**：
通常會發現是 `ThreadLocal` 未正確呼叫 `remove()`，或者是 Cache 實作沒有設定 TTL/Max Size，導致物件被強引用（Strong Reference）綁住，GC 無法回收。
Typically, you will find that `ThreadLocal` did not call `remove()` correctly, or a Cache implementation lacks TTL/Max Size settings, causing objects to be bound by Strong References, making them uncollectible by GC.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)
## 5. Common Pitfalls & Anti-patterns

1. **盲目複製 GC 參數 (Cargo-Cult GC Tuning)**
   * **錯誤 (Pitfall)**：從網路上抄襲一堆 `-XX:NewRatio`, `-XX:SurvivorRatio`, `-XX:MaxTenuringThreshold` 參數到 Java 11/17 的 Production 環境。
     **Pitfall**: Copy-pasting a bunch of `-XX:NewRatio`, `-XX:SurvivorRatio`, `-XX:MaxTenuringThreshold` flags from the internet into a Java 11/17 production environment.
   * **為何不好 (Why it's bad)**：現代 GC（如 G1GC）是自適應的（Ergonomics）。過度手動指定年輕代大小會破壞 G1GC 自動調整 Pause Time 的能力。
     **Why it's bad**: Modern GCs (like G1GC) are adaptive (Ergonomics). Over-specifying young generation sizes manually destroys G1GC's ability to automatically adjust for Pause Time.
   * **較佳方案 (Better Alternative)**：對於 G1GC，通常只需設定 `-Xms`, `-Xmx` 以及 `-XX:MaxGCPauseMillis`（目標暫停時間），讓 JVM 自己尋找最佳平衡。
     **Better Alternative**: For G1GC, usually, you only need to set `-Xms`, `-Xmx`, and `-XX:MaxGCPauseMillis` (target pause time), letting the JVM find the optimal balance itself.

2. **忽略 Native Memory 洩漏 (Ignoring Native Memory Leaks)**
   * **錯誤 (Pitfall)**：看到 K8s Pod OOMKilled，就不斷調大 `-Xmx`。
     **Pitfall**: Continuously increasing `-Xmx` upon seeing K8s Pod OOMKilled.
   * **為何不好 (Why it's bad)**：如果洩漏發生在 DirectByteBuffer（如 Netty 處理網路 I/O）或 JNI 呼叫，調大 Heap 反而會壓縮作業系統留給 Native Memory 的空間，導致 Pod 更快被 Killed。
     **Why it's bad**: If the leak occurs in DirectByteBuffer (e.g., Netty handling network I/O) or JNI calls, increasing the Heap actually compresses the space left by the OS for Native Memory, causing the Pod to be killed even faster.
   * **較佳方案 (Better Alternative)**：開啟 NMT (Native Memory Tracking) `-XX:NativeMemoryTracking=detail`，並使用 `jcmd <pid> VM.native_memory` 來追蹤非 Heap 區的記憶體增長。
     **Better Alternative**: Enable NMT (Native Memory Tracking) with `-XX:NativeMemoryTracking=detail`, and use `jcmd <pid> VM.native_memory` to track non-heap memory growth.

3. **濫用 `System.gc()` (Abusing `System.gc()`)**
   * **錯誤 (Pitfall)**：在程式碼中手動呼叫 `System.gc()` 試圖釋放記憶體。
     **Pitfall**: Manually calling `System.gc()` in the code in an attempt to free memory.
   * **為何不好 (Why it's bad)**：這會觸發 Full GC（嚴重的 STW），導致系統吞吐量暴跌。
     **Why it's bad**: This triggers a Full GC (severe STW), causing system throughput to plummet.
   * **較佳方案 (Better Alternative)**：信任 JVM 的記憶體管理。若有必要防範第三方套件濫用，可加上 `-XX:+DisableExplicitGC` 啟動參數。
     **Better Alternative**: Trust the JVM's memory management. If necessary to prevent abuse by third-party libraries, add the `-XX:+DisableExplicitGC` startup flag.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)
## 6. Interview & Discussion Hooks

作為 Senior Engineer，在 System Design 或 Troubleshooting 面試中，你可能會遇到以下問題：
As a Senior Engineer, you might encounter the following questions in System Design or Troubleshooting interviews:

*   **Q1: 在 Kubernetes 環境下，Pod 頻繁發生重啟，你如何判斷是 OOMKilled 還是 JVM OutOfMemoryError？**
    **Q1: In a Kubernetes environment, Pods are restarting frequently. How do you determine if it's an OOMKilled or a JVM OutOfMemoryError?**
    *   **高分回答要點 (Key points for a high score)**：
        1. 檢查 `kubectl describe pod` 查看 Exit Code（137 通常代表 OOMKilled）。
        2. 檢查 JVM 日誌是否有 `java.lang.OutOfMemoryError`。
        3. 說明 K8s OOMKilled 是因為 Container 總記憶體超出 Limit，通常與 Native Memory (NMT)、Metaspace 或 `-Xmx` 設定過大有關；而 JVM OOM 是 Heap 內部空間不足。
        1. Check `kubectl describe pod` for the Exit Code (137 usually indicates OOMKilled).
        2. Check JVM logs for `java.lang.OutOfMemoryError`.
        3. Explain that K8s OOMKilled is due to total container memory exceeding the Limit, often related to Native Memory (NMT), Metaspace, or an oversized `-Xmx`; whereas JVM OOM is a lack of space inside the Heap.

*   **Q2: 系統的 P99 延遲偶爾會出現長達數秒的突增，但 CPU 和 Memory 使用率都很正常，你會如何排查？**
    **Q2: The system's P99 latency occasionally spikes to several seconds, but CPU and Memory usage are normal. How would you investigate?**
    *   **高分回答要點 (Key points for a high score)**：
        1. 懷疑是 JVM Pause（STW）導致。
        2. 檢查 GC Log，確認是否有過長的 Young GC 或 Full GC。
        3. 如果 GC 時間正常，則懷疑是 Safepoint 延遲（Time to Safepoint）。透過 `-Xlog:safepoint` 或 JFR 分析是否有執行緒長時間無法進入 Safepoint（例如 Counted Loop 缺少 Safepoint Polling）。
        1. Suspect JVM Pauses (STW) as the cause.
        2. Check GC Logs to confirm if there are excessively long Young GCs or Full GCs.
        3. If GC times are normal, suspect Safepoint delays (Time to Safepoint). Use `-Xlog:safepoint` or JFR to analyze if any thread took too long to reach a Safepoint (e.g., Counted Loops lacking Safepoint Polling).

*   **Q3: 在 Java 17/21 中，你會如何選擇 G1GC 與 ZGC？**
    **Q3: In Java 17/21, how do you choose between G1GC and ZGC?**
    *   **高分回答要點 (Key points for a high score)**：
        1. **G1GC** 是預設且泛用的選擇，著重於 Throughput 與 Latency 的平衡，適合多數微服務與批次處理。
        2. **ZGC** 是超低延遲（Sub-millisecond pause times）的垃圾回收器。如果業務是高頻交易（HFT）、大型 Caching Server 或對 P99/P999 延遲極度敏感的系統，且願意犧牲一點點 Throughput，則選擇 ZGC。
        1. **G1GC** is the default and general-purpose choice, focusing on the balance between Throughput and Latency, suitable for most microservices and batch processing.
        2. **ZGC** is an ultra-low latency (sub-millisecond pause times) garbage collector. If the business is High-Frequency Trading (HFT), a large Caching Server, or a system extremely sensitive to P99/P999 latency, and is willing to sacrifice a bit of Throughput, then choose ZGC.

---

## 7. 小結與後續延伸 (Summary & Next Steps)
## 7. Summary & Next Steps

**本章記憶錨點 (Key Takeaways)**：
*   **工具選擇 (Tool Selection)**：Production 環境剖析首選 JFR 與 async-profiler（採樣機制，低開銷）；避免使用 BTrace 等高開銷插樁工具。
*   **CPU 排障 (CPU Troubleshooting)**：熟記 `top -H` -> Hex PID -> `jstack` 的黃金法則，或直接使用火焰圖。
*   **Memory 排障 (Memory Troubleshooting)**：務必配置 `-XX:+HeapDumpOnOutOfMemoryError`。分析時善用 Dominator Tree 尋找 GC Roots。
*   **Native Memory (非 Heap 記憶體)**：K8s OOMKilled 通常與 Native Memory 有關，請使用 NMT (Native Memory Tracking) 進行追蹤。
*   **GC 調校理念 (GC Tuning Philosophy)**：現代 GC 依賴 Ergonomics，優先設定目標（如 `-XX:MaxGCPauseMillis`），避免過度微調底層參數。

**後續延伸 (Next Steps)**：
*   **實作演練 (Hands-on Practice)**：在本地端寫一個包含 `ThreadLocal` 洩漏的 Spring Boot 應用，限制 `-Xmx128m`，實際產出 Heap Dump 並用 Eclipse MAT 找出洩漏點。
    **Hands-on Practice**: Write a Spring Boot app with a `ThreadLocal` leak locally, limit `-Xmx128m`, generate a Heap Dump, and use Eclipse MAT to find the leak.
*   **探索進階 JVM 參數 (Explore Advanced JVM Flags)**：研究 Java 21 引入的 Generational ZGC，了解其如何同時改善吞吐量與延遲。
    **Explore Advanced JVM Flags**: Research the Generational ZGC introduced in Java 21 to understand how it improves both throughput and latency simultaneously.