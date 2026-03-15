# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的層級，效能調優不再是依賴直覺的「猜測遊戲」，而是基於數據的「精準手術」。當系統分佈在數百個微服務與容器中時，單純查看 Log 或 CPU 使用率往往無法還原問題全貌。本章將帶領你從傳統的監控（Monitoring）跨越到可觀測性（Observability），掌握定位複雜效能瓶頸的核心技術。

At the Senior Engineer level, performance tuning is no longer a "guessing game" based on intuition, but a "precision surgery" based on data. When a system is distributed across hundreds of microservices and containers, simply looking at logs or CPU usage is often insufficient to reconstruct the full picture. This chapter will guide you from traditional Monitoring to Observability, mastering the core techniques for pinpointing complex performance bottlenecks.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分監控與可觀測性**：理解 Metrics、Logs 與 Traces 三大支柱的協作方式，並知道何時該用哪一種工具。
    **Distinguish between Monitoring and Observability**: Understand how the three pillars—Metrics, Logs, and Traces—collaborate, and know when to use which tool.
2.  **解讀 Flame Graphs**：熟練使用火焰圖分析 CPU 熱點（On-CPU）與等待瓶頸（Off-CPU），快速定位程式碼級別的效能問題。
    **Interpret Flame Graphs**: Proficiently use Flame Graphs to analyze CPU hotspots (On-CPU) and wait bottlenecks (Off-CPU) to quickly pinpoint code-level performance issues.
3.  **實作 Distributed Tracing**：利用 OpenTelemetry 等標準追蹤跨服務請求，識別微服務架構中的延遲傳遞與級聯故障。
    **Implement Distributed Tracing**: Use standards like OpenTelemetry to trace requests across services, identifying latency propagation and cascading failures in microservices architectures.
4.  **設計高信噪比的告警**：建立基於 SLO/SLI 的告警策略，避免「告警疲勞（Alert Fatigue）」，專注於真正影響使用者的症狀。
    **Design High Signal-to-Noise Alerts**: Establish alerting strategies based on SLOs/SLIs to avoid "Alert Fatigue" and focus on symptoms that truly impact users.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 可觀測性的三大支柱 (The Three Pillars of Observability)

許多工程師誤以為「有 Log 和 Dashboard」就是可觀測性。事實上，**監控（Monitoring）** 是告訴你「系統壞了」，而 **可觀測性（Observability）** 是讓你有能力問系統「為什麼壞了」。

Many engineers mistakenly believe that "having Logs and Dashboards" equals observability. In reality, **Monitoring** tells you "the system is broken," whereas **Observability** gives you the ability to ask the system "why it is broken."

我們通常透過三大支柱來建立這種能力：
We typically build this capability through three pillars:

1.  **Metrics (聚合數據)**：
    *   *定義*：一段時間內的數值測量（如 CPU %, QPS, P99 Latency）。
    *   *用途*：發現趨勢、觸發告警。成本低，但缺乏上下文。
    *   *Definition*: Numerical measurements over time (e.g., CPU %, QPS, P99 Latency).
    *   *Usage*: Spotting trends, triggering alerts. Low cost, but lacks context.
2.  **Logs (離散事件)**：
    *   *定義*：帶有時間戳的事件紀錄（如 Error stack trace, Info messages）。
    *   *用途*：了解特定錯誤的細節。成本高，資料量大。
    *   *Definition*: Timestamped event records (e.g., Error stack trace, Info messages).
    *   *Usage*: Understanding details of specific errors. High cost, large data volume.
3.  **Traces (請求路徑)**：
    *   *定義*：單個請求在分佈式系統中傳播的完整生命週期（Spans）。
    *   *用途*：定位服務間的延遲與依賴關係。
    *   *Definition*: The complete lifecycle of a single request propagating through a distributed system (Spans).
    *   *Usage*: Pinpointing latency and dependencies between services.

## 2.2 Profiling 與 Flame Graphs 的心智模型 (Mental Model for Profiling & Flame Graphs)

**Profiling** 是對執行中的程式進行採樣（Sampling）或插樁（Instrumentation），以獲取資源消耗分佈的過程。

**Profiling** is the process of sampling or instrumenting a running program to obtain the distribution of resource consumption.

將 **Flame Graph（火焰圖）** 想像成對程式執行堆疊（Call Stack）的「人口普查」：
Think of a **Flame Graph** as a "census" of the program's execution stack (Call Stack):

*   **Y 軸（縱軸）**：代表 Stack Depth（呼叫深度）。頂層是正在執行的函數，底層是進入點。
*   **X 軸（橫軸）**：代表 **Sample Count（採樣次數）**，即佔用資源的比例，**而非時間軸**。
*   **寬度**：越寬的區塊（Bar），代表該函數在採樣期間出現的頻率越高（即消耗越多 CPU 或時間）。

*   **Y-axis (Vertical)**: Represents Stack Depth. The top layer is the function currently executing; the bottom is the entry point.
*   **X-axis (Horizontal)**: Represents **Sample Count**, i.e., the proportion of resource usage, **not the timeline**.
*   **Width**: The wider the bar, the more frequently that function appeared during sampling (meaning it consumed more CPU or time).

> **關鍵直覺**：尋找火焰圖中「平頂且寬闊」的板塊（Plateaus）。那代表該函數本身執行很久，且沒有呼叫其他子函數（或子函數被 inline 了），是優化的首要目標。
>
> **Key Intuition**: Look for "flat and wide" plateaus in the Flame Graph. This indicates the function itself ran for a long time without calling other sub-functions (or sub-functions were inlined), making it a primary target for optimization.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計中，可觀測性不是「外掛」的功能，而是必須內建於架構中的 **非功能性需求（NFR）**。

In large-scale system design, observability is not an "add-on" feature but a **Non-Functional Requirement (NFR)** that must be built into the architecture.

## 3.1 架構中的角色 (Role in Architecture)

在典型的微服務架構（如 Kubernetes 環境）中，Observability Stack 通常包含以下組件：

In a typical microservices architecture (e.g., Kubernetes environment), the Observability Stack usually includes the following components:

1.  **Instrumentation Layer (SDK/Agent)**:
    *   應用程式內嵌 OpenTelemetry SDK 或使用 eBPF Agent（非侵入式）。
    *   負責收集 Metrics, Logs, Traces 並注入 Context (TraceID)。
    *   Embed OpenTelemetry SDK in apps or use eBPF Agents (non-intrusive).
    *   Responsible for collecting Metrics, Logs, Traces, and injecting Context (TraceID).

2.  **Collector/Aggregator (Sidecar or DaemonSet)**:
    *   例如 `OTel Collector` 或 `Prometheus Node Exporter`。
    *   負責緩衝、過濾、批次傳送數據，減輕應用程式負擔。
    *   E.g., `OTel Collector` or `Prometheus Node Exporter`.
    *   Responsible for buffering, filtering, and batching data to offload the application.

3.  **Storage & Query Backend**:
    *   Metrics: Prometheus, VictoriaMetrics, Datadog.
    *   Traces: Jaeger, Tempo, Honeycomb.
    *   Logs: ELK Stack (Elasticsearch), Loki.

4.  **Visualization (The "Single Pane of Glass")**:
    *   Grafana 是最常見的選擇，將上述三種數據源整合在同一個 Dashboard。
    *   Grafana is the most common choice, integrating the three data sources above into a single dashboard.

## 3.2 對系統擴充性與穩定性的影響 (Impact on Scalability & Stability)

*   **Overhead Control**: 在 Production 環境開啟 Profiling 或 Tracing 會有效能損耗。資深工程師需懂得設定 **Sampling Rate（採樣率）**（例如：只追蹤 1% 的請求）或使用 **Tail-based Sampling**（只保留發生錯誤或高延遲的 Trace）。
    *   **Overhead Control**: Enabling Profiling or Tracing in Production incurs performance overhead. Senior engineers must know how to set the **Sampling Rate** (e.g., trace only 1% of requests) or use **Tail-based Sampling** (keep only traces with errors or high latency).
*   **MTTR (Mean Time To Recovery)**: 強大的可觀測性直接降低 MTTR。當 PagerDuty 響起時，你不需要 SSH 進機器 grep logs，而是點開 Trace 連結直接看到是哪一個 SQL Query 卡住了。
    *   **MTTR**: Strong observability directly reduces MTTR. When PagerDuty rings, you don't need to SSH into machines and grep logs; instead, you click a Trace link and see exactly which SQL Query got stuck.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 案例一：使用 Flame Graph 分析 CPU 飆高 (Scenario 1: Analyzing CPU Spike with Flame Graph)

**背景 (Context)**:
一個影像處理服務（Image Processing Service）在負載增加時，CPU 使用率飆升至 95%，導致吞吐量下降。

**Context**:
An Image Processing Service sees CPU usage spike to 95% under load, causing throughput to drop.

**步驟 1：獲取 Profile (Step 1: Capture Profile)**
假設使用 Go 語言，我們可以透過 `pprof` 獲取 30 秒的 CPU profile。

Assume we are using Go, we can capture a 30-second CPU profile via `pprof`.

```bash
# Fetch profile from the live service
curl -o cpu.prof "http://localhost:6060/debug/pprof/profile?seconds=30"

# Visualize using pprof tool (web interface)
go tool pprof -http=:8080 cpu.prof
```

**步驟 2：分析火焰圖 (Step 2: Analyze the Flame Graph)**
打開 Web UI 的 Flame Graph 視圖。你看到了一個非常寬的板塊（Wide Bar）。

Open the Flame Graph view in the Web UI. You see a very wide bar.

*   **觀察 (Observation)**: `github.com/org/service/image.Resize` 佔用了 60% 的寬度。
*   **深入 (Drill-down)**: 在該函數上方，發現大量的 `runtime.mallocgc` 和 `runtime.scanobject`。
*   **推論 (Deduction)**: 這不僅是計算密集，還引發了大量的 **GC Pressure（垃圾回收壓力）**。這意味著該函數在迴圈中創建了過多短暫物件。

*   **Observation**: `github.com/org/service/image.Resize` occupies 60% of the width.
*   **Drill-down**: Above this function, you see massive `runtime.mallocgc` and `runtime.scanobject`.
*   **Deduction**: This isn't just compute-intensive; it's triggering massive **GC Pressure**. This implies the function is creating too many short-lived objects inside a loop.

**步驟 3：優化 (Step 3: Optimization)**
*   **Naive Fix**: 增加 CPU 核心數（Vertical Scaling）。這治標不治本。
*   **Senior Fix**: 重構程式碼，使用 `sync.Pool` 重用 buffer，減少記憶體分配。
*   **驗證**: 再次 Profile，發現 `mallocgc` 的寬度顯著縮小，總體 CPU 使用率下降。

*   **Naive Fix**: Increase CPU cores (Vertical Scaling). This treats the symptom, not the root cause.
*   **Senior Fix**: Refactor code to use `sync.Pool` to reuse buffers, reducing memory allocation.
*   **Verification**: Profile again; the width of `mallocgc` shrinks significantly, and overall CPU usage drops.

## 4.2 案例二：利用 Distributed Tracing 定位長尾延遲 (Scenario 2: Pinpointing Tail Latency with Distributed Tracing)

**背景 (Context)**:
使用者抱怨 "Checkout" API 偶爾需要 3 秒鐘，但平均只需 200ms。

**Context**:
Users complain that the "Checkout" API occasionally takes 3 seconds, while the average is only 200ms.

**步驟 1：查看 Trace (Step 1: Inspect Trace)**
在 Jaeger/Tempo 中搜尋 `duration > 2s` 的 Trace。找到一個 Trace ID。

Search for traces with `duration > 2s` in Jaeger/Tempo. Find a Trace ID.

**步驟 2：視覺化瀑布圖 (Step 2: Visualize Waterfall)**
Trace 顯示如下結構：

The Trace shows the following structure:

```text
|-- Checkout Service (Total: 3.1s)
    |-- Auth Service (20ms)
    |-- Inventory Service (50ms)
    |-- Payment Service (3.0s) !!!
        |-- External Bank API (2.9s)
```

**步驟 3：分析瓶頸 (Step 3: Analyze Bottleneck)**
問題出在 `Payment Service` 呼叫外部銀行 API 時。
但 `Payment Service` 的 Log 顯示它有設定 `timeout = 5s`。

The issue lies in the `Payment Service` calling the External Bank API.
However, `Payment Service` logs show it has a `timeout = 5s`.

**思考 (Thinking)**:
為什麼偶爾會慢？Trace 的 Tags 顯示這筆請求發生在每天的特定時段。
進一步檢查 Metrics，發現該時段 External Bank API 的可用性下降。

**Thinking**:
Why is it slow occasionally? Trace Tags show this request happens at a specific time of day.
Checking Metrics further, we see the External Bank API availability drops during that time.

**解決方案 (Solution)**:
*   實作 **Circuit Breaker (斷路器)**：當外部服務回應過慢時，快速失敗（Fail Fast）或切換到備用 Provider，而不是讓使用者乾等 3 秒。
*   Implement **Circuit Breaker**: When the external service is too slow, Fail Fast or switch to a backup provider instead of letting the user wait for 3 seconds.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 High Cardinality Metrics (高基數指標)
*   **錯誤 (Mistake)**: 在 Prometheus 的 Label 中放入 `UserID`, `Email`, `UUID` 或 `URL path` (包含 ID)。
    *   e.g., `http_requests_total{path="/api/users/12345"}`
*   **後果 (Consequence)**: 產生數百萬條獨立的時間序列（Time Series），導致 TSDB 記憶體爆炸，查詢超時，甚至拖垮監控系統。
*   **修正 (Fix)**: 將動態部分正規化。
    *   e.g., `http_requests_total{path="/api/users/:id"}`
    *   若需要追蹤特定 User，請使用 Logs 或 Traces，而非 Metrics。

*   **Mistake**: Putting `UserID`, `Email`, `UUID`, or `URL path` (with IDs) in Prometheus Labels.
*   **Consequence**: Generates millions of unique Time Series, causing TSDB memory explosion, query timeouts, or even crashing the monitoring system.
*   **Fix**: Normalize dynamic parts. Use Logs or Traces if you need to track specific users, not Metrics.

## 5.2 告警疲勞 (Alert Fatigue)
*   **錯誤 (Mistake)**: 對所有資源指標設定告警（CPU > 80%, Memory > 70%）。
*   **後果 (Consequence)**: 手機整天響，工程師習慣性忽略。當真正的故障發生時，沒人注意。
*   **修正 (Fix)**: 遵循 **Golden Signals** (Latency, Traffic, Errors, Saturation)。
    *   告警應基於 **Symptom (症狀)**（如：Error Rate > 1%），而非 **Cause (原因)**（如：CPU 高）。CPU 高但服務正常回應時，不需要半夜叫醒工程師。

*   **Mistake**: Alerting on all resource metrics (CPU > 80%, Memory > 70%).
*   **Consequence**: Phones buzz all day, engineers habitually ignore them. When a real failure happens, no one notices.
*   **Fix**: Follow **Golden Signals**. Alert on **Symptoms** (e.g., Error Rate > 1%), not **Causes** (e.g., High CPU). If CPU is high but the service is responding correctly, don't wake the engineer up at night.

## 5.3 忽略 Off-CPU Profiling
*   **錯誤 (Mistake)**: 只關注 CPU Profiling，卻無法解釋為什麼程式 CPU 很低但回應很慢。
*   **後果 (Consequence)**: 無法偵測 Lock Contention（鎖競爭）、I/O 等待或 Context Switch 問題。
*   **修正 (Fix)**: 使用 **Off-CPU Analysis** 或 **Wall-clock Profiling** 來查看執行緒在「等待」什麼。

*   **Mistake**: Focusing only on CPU Profiling, failing to explain why the app has low CPU but slow response.
*   **Consequence**: Inability to detect Lock Contention, I/O waits, or Context Switch issues.
*   **Fix**: Use **Off-CPU Analysis** or **Wall-clock Profiling** to see what threads are "waiting" for.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 設計題：如何監控一個高併發系統？
**Q: "我們有一個百萬級 QPS 的 API Gateway，你會如何設計它的可觀測性架構？特別是如何處理海量數據？"**

**高分回答要點 (Key Points for a High Score)**:
1.  **採樣策略 (Sampling Strategy)**: 不能記錄所有 Trace。提出 **Head-based Sampling** (隨機 0.1%) vs **Tail-based Sampling** (保留所有 Error/Slow trace，這需要特殊的 Collector 緩衝)。
2.  **指標聚合 (Metrics Aggregation)**: 在 Sidecar 或 Agent 層級做預聚合（Pre-aggregation），減少送往 Prometheus 的數據點。
3.  **分層儲存 (Tiered Storage)**: 近期數據存熱區（SSD/Memory），歷史數據存冷區（S3/GCS）。
4.  **基數控制 (Cardinality Control)**: 強調會嚴格審查 Label 的設計。

## 6.2 實作題：CPU vs Latency
**Q: "如果一個服務的 Latency 很高，但 CPU 使用率很低，可能的原因是什麼？你會用什麼工具排查？"**

**高分回答要點 (Key Points for a High Score)**:
1.  **原因**: I/O Blocking (DB, Network), Lock Contention (Mutex), Thread Starvation (執行緒池滿了), 或是頻繁的 Context Switch。
2.  **工具**:
    *   **Trace**: 查看 Span 是卡在本地處理還是等待下游。
    *   **Off-CPU Profiler**: 查看執行緒在 `futex` (鎖) 或 `read/write` (IO) 上花費的時間。
    *   **Metrics**: 檢查 Thread Pool 飽和度、DB 連線池狀態。

## 6.3 觀念題：Push vs Pull
**Q: "Prometheus (Pull) 與 Datadog/NewRelic (Push) 模式有什麼區別？在什麼場景下你會選擇哪一種？"**

**高分回答要點 (Key Points for a High Score)**:
1.  **Pull (Prometheus)**: 服務端簡單（只需暴露 HTTP endpoint），監控端控制抓取頻率。適合長時間運行的服務，容易檢測「服務掛掉」（因為抓不到數據）。
2.  **Push (Telegraf/Datadog)**: 適合短生命週期的 Job (Batch jobs, Serverless)，因為它們可能在 Pull 到來之前就結束了。
3.  **混合**: 現代架構通常混用（例如透過 Push Gateway 讓 Batch Job 支援 Pull 模式）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 7.1 重點回顧 (Key Takeaways)
1.  **Observability != Monitoring**: 監控告訴你狀態，可觀測性幫助你除錯。
2.  **Golden Signals**: 專注於 Latency, Traffic, Errors, Saturation 四大黃金指標。
3.  **Flame Graphs**: 寬度代表資源消耗。尋找「平頂」進行優化。區分 On-CPU (計算慢) 與 Off-CPU (等待慢)。
4.  **Distributed Tracing**: 是微服務除錯的靈魂，必須解決 Context Propagation 的問題。
5.  **Cardinality Matters**: 永遠不要在 Metrics Label 中放入無限增長的 ID。

## 7.2 後續延伸 (Next Steps)
*   **Advanced Profiling**: 學習使用 **eBPF** 工具（如 BCC tools, Pixie）進行內核級別的觀測，無需修改程式碼即可看到 TCP 重傳、磁碟 I/O 延遲等細節。
*   **Next Chapter**: 進入資料庫層面的調優，學習如何分析 Query Plan 與 Indexing 策略（這通常是 Latency 的最大來源）。

*   **Advanced Profiling**: Learn to use **eBPF** tools (like BCC tools, Pixie) for kernel-level observability, allowing you to see TCP retransmissions, Disk I/O latency, etc., without code changes.
*   **Next Chapter**: Dive into Database Tuning, learning how to analyze Query Plans and Indexing strategies (often the biggest source of Latency).