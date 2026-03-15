# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，面對「資料庫變慢了」這類模糊的投訴，區別新手與專家的關鍵在於：你是依賴猜測與重啟，還是依賴數據與精準診斷。本章將帶你深入 SQL Server 的核心監控機制，建立一套系統化的效能分析方法論。

In the career of a Senior Software Engineer, when facing vague complaints like "the database is slow," the key differentiator between a novice and an expert is whether you rely on guessing and restarting, or on data and precise diagnosis. This chapter will take you deep into SQL Server's core monitoring mechanisms to establish a systematic methodology for performance analysis.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **掌握 Wait Statistics 分析法**：不再只看 CPU 使用率，而是透過 `sys.dm_os_wait_stats` 理解 SQL Server 到底在「等待」什麼（Disk I/O, Network, Lock, CPU）。
    **Master Wait Statistics Analysis**: Move beyond just looking at CPU usage; understand exactly what SQL Server is "waiting" for (Disk I/O, Network, Lock, CPU) using `sys.dm_os_wait_stats`.
2.  **熟練使用關鍵 DMVs**：利用 Dynamic Management Views (如 `sys.dm_exec_requests`, `sys.dm_exec_query_stats`) 快速定位當下正在阻塞系統的具體語法。
    **Proficiently use key DMVs**: Utilize Dynamic Management Views (such as `sys.dm_exec_requests`, `sys.dm_exec_query_stats`) to quickly pinpoint the specific queries currently blocking the system.
3.  **以 Extended Events 取代 Profiler**：學會配置輕量級的 Extended Events (XEvents) 來捕捉生產環境中的異常，避免使用過時且高負載的 SQL Profiler。
    **Replace Profiler with Extended Events**: Learn to configure lightweight Extended Events (XEvents) to capture anomalies in production, avoiding the deprecated and high-overhead SQL Profiler.
4.  **建立監控基準 (Baseline)**：理解如何分辨「正常的高負載」與「異常的效能退化」。
    **Establish Monitoring Baselines**: Understand how to distinguish between "normal high load" and "abnormal performance degradation."

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 The "Life of a Thread" Model (執行緒生命週期模型)

要診斷 SQL Server，必須理解 SQL Server 的排程器（SQLOS Scheduler）。每個請求（Request）在執行時會經歷三種狀態，這也是 **Wait Statistics** 的基礎。

To diagnose SQL Server, you must understand the SQLOS Scheduler. Every request goes through three states during execution, which is the foundation of **Wait Statistics**.

1.  **Running (執行中)**：執行緒正在 CPU 上運算。
    **Running**: The thread is actively computing on the CPU.
2.  **Suspended (暫停/等待)**：執行緒需要資源（如讀取磁碟頁面、等待鎖定釋放），因此讓出 CPU，進入等待清單（Waiter List）。這就是產生 **Wait Type** 的時刻。
    **Suspended**: The thread needs a resource (e.g., reading a disk page, waiting for a lock release), so it yields the CPU and enters the Waiter List. This is when a **Wait Type** is generated.
3.  **Runnable (可執行)**：資源已取得（例如 I/O 完成），執行緒回到佇列（Runnable Queue），等待 CPU 再次排程。
    **Runnable**: The resource is acquired (e.g., I/O complete), and the thread returns to the Runnable Queue, waiting for the CPU to schedule it again.

> **關鍵洞察 (Key Insight)**：
> 如果 `Runnable` 時間很長，代表 CPU 有壓力（CPU Pressure），因為執行緒準備好了卻排不到 CPU。
> 如果 `Suspended` 時間很長，代表外部資源（I/O, Network, Locks）是瓶頸。
>
> **Key Insight**:
> If `Runnable` time is high, it indicates **CPU Pressure**, as threads are ready but cannot get CPU time.
> If `Suspended` time is high, it indicates external resources (I/O, Network, Locks) are the bottleneck.

## 2.2 DMVs vs. Extended Events

-   **DMVs (Dynamic Management Views)**：
    -   *類比*：汽車的儀表板與里程表。
    -   *用途*：查看「當下狀態」（誰在跑？）與「累計數據」（自上次重啟後，哪種等待最多？）。
    -   *Analogy*: Car dashboard and odometer.
    -   *Usage*: Viewing "current state" (who is running?) and "accumulated data" (what wait type is highest since last restart?).

-   **Extended Events (XEvents)**：
    -   *類比*：飛機的黑盒子或針對特定問題的醫療監測儀。
    -   *用途*：捕捉「事件發生瞬間」的詳細資訊（例如：捕捉所有執行超過 5 秒的查詢及其執行計畫）。
    -   *Analogy*: Airplane black box or a targeted medical monitor.
    -   *Usage*: Capturing detailed information "at the moment an event occurs" (e.g., capturing all queries running longer than 5 seconds along with their execution plans).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，資料庫往往是最終的狀態儲存點，也是最難水平擴展的組件。

In large-scale distributed systems, the database is often the final state store and the hardest component to scale horizontally.

## 3.1 可觀測性架構 (Observability Architecture)

在 Production 環境，我們不會隨時盯著 SSMS (SQL Server Management Studio)。通常會建立自動化監控管線：

In a Production environment, we don't stare at SSMS (SQL Server Management Studio) all the time. We typically establish an automated monitoring pipeline:

1.  **Telegraf / Datadog Agent / Prometheus Exporter**：
    -   定期查詢 DMVs（如 `sys.dm_os_wait_stats`, `sys.dm_os_performance_counters`）。
    -   Periodically query DMVs (e.g., `sys.dm_os_wait_stats`, `sys.dm_os_performance_counters`).
2.  **Time Series DB & Dashboard (Grafana)**：
    -   繪製 `Batch Requests/sec` (Throughput) 與 `Average Wait Time` (Latency)。
    -   Visualize `Batch Requests/sec` (Throughput) and `Average Wait Time` (Latency).
3.  **Alerting**：
    -   當 `PAGEIOLATCH_SH`（磁碟讀取等待）突然飆高，或 `LCK_M_IX`（鎖定等待）超過閾值時觸發警報。
    -   Trigger alerts when `PAGEIOLATCH_SH` (disk read wait) spikes or `LCK_M_IX` (lock wait) exceeds thresholds.

## 3.2 效能診斷流程 (Troubleshooting Workflow)

當系統發生 P1 Incident（嚴重故障）時，資深工程師的介入流程通常如下：

When a P1 Incident occurs, the intervention workflow for a Senior Engineer is typically:

1.  **Check Health**：CPU 是滿載還是閒置？（滿載可能是執行計畫不良導致的高運算；閒置但慢通常是 Blocking 或 I/O）。
    **Check Health**: Is CPU pegged or idle? (Pegged often means high computation due to bad plans; idle but slow usually means Blocking or I/O).
2.  **Who is Active**：使用 `sys.dm_exec_requests` 查看當下卡住的 Session。
    **Who is Active**: Use `sys.dm_exec_requests` to see currently stuck sessions.
3.  **Wait Analysis**：確認主要的 Wait Type。
    **Wait Analysis**: Confirm the dominant Wait Type.
4.  **Kill or Fix**：如果是嚴重的 Blocking chain，可能需要殺掉 Head Blocker；如果是參數嗅探 (Parameter Sniffing)，可能需要清除特定 Plan。
    **Kill or Fix**: If it's a severe Blocking chain, you might need to kill the Head Blocker; if it's Parameter Sniffing, you might need to clear a specific Plan.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 案例：系統突然變慢，應用程式 Timeout

**情境 (Context)**：週五下午，電商後台回報大量 Timeout，DB CPU 使用率不高，但連線數飆升。

**Scenario**: Friday afternoon, the e-commerce backend reports massive timeouts. DB CPU usage is not high, but the connection count is spiking.

### Step 1: 診斷當下執行中的請求 (Diagnose Active Requests)

我們需要一個類似 Linux `top` 指令的 SQL 版本。這段程式碼能列出當前正在執行、且非系統內部的請求。

We need a SQL version of the Linux `top` command. This code lists currently executing, non-system requests.

```sql
-- 查詢當前正在執行的 Requests 及其等待狀態
-- Query currently executing Requests and their wait stats
SELECT
    r.session_id,
    r.status,
    r.start_time,
    r.command,
    -- 關鍵：正在等什麼？ (Key: What are we waiting for?)
    r.wait_type,
    r.wait_time,
    r.last_wait_type,
    -- 誰擋住了我？ (Who is blocking me?)
    r.blocking_session_id,
    -- 正在執行的 SQL 文字 (The executing SQL text)
    t.text AS sql_text,
    -- 執行計畫 (Execution Plan - XML)
    p.query_plan,
    r.cpu_time,
    r.total_elapsed_time
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
OUTER APPLY sys.dm_exec_query_plan(r.plan_handle) p
WHERE r.session_id > 50 -- 過濾系統 Session (Filter system sessions)
  AND r.session_id <> @@SPID -- 排除自己 (Exclude self)
ORDER BY r.total_elapsed_time DESC;
```

### Step 2: 分析結果 (Analyze Results)

假設結果顯示多個 Session 的 `wait_type` 為 `LCK_M_IX` 或 `LCK_M_X`，且 `blocking_session_id` 指向 Session 72。

Suppose the results show multiple sessions with `wait_type` as `LCK_M_IX` or `LCK_M_X`, and `blocking_session_id` points to Session 72.

-   **Session 72** 的狀態可能是 `Running` 或 `Suspended`。
-   如果 Session 72 正在執行一個大範圍的 `UPDATE` 且沒有適當的索引，它可能會鎖住整張表。

### Step 3: 深入 Wait Stats (Deep Dive into Wait Stats)

如果當下沒有明顯阻塞，但整體感覺「卡卡的」，我們檢查累積的 Wait Stats。

If there is no obvious blocking at the moment, but the system feels "sluggish," we check accumulated Wait Stats.

```sql
-- 查詢系統累積的前 10 大等待類型
-- Query top 10 accumulated wait types
SELECT TOP 10
    wait_type,
    wait_time_ms / 1000.0 AS wait_time_sec,
    waiting_tasks_count,
    -- 平均每次等待時間 (Average wait time per occurrence)
    (wait_time_ms - signal_wait_time_ms) / NULLIF(waiting_tasks_count, 0) AS avg_resource_wait_ms,
    -- Signal Wait 代表 CPU 排程延遲 (Signal Wait represents CPU scheduling delay)
    signal_wait_time_ms / NULLIF(waiting_tasks_count, 0) AS avg_signal_wait_ms
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN (
    -- 排除雜訊與背景行程等待 (Exclude noise and background process waits)
    'CLR_SEMAPHORE', 'LAZYWRITER_SLEEP', 'RESOURCE_QUEUE',
    'SLEEP_TASK', 'SLEEP_SYSTEMTASK', 'SQLTRACE_BUFFER_FLUSH', 'WAITFOR'
)
ORDER BY wait_time_ms DESC;
```

**解讀 (Interpretation)**：
-   **PAGEIOLATCH_SH**: 磁碟讀取瓶頸。檢查記憶體是否不足（Buffer Pool 抖動）或查詢是否做了全表掃描（Table Scan）。
    **PAGEIOLATCH_SH**: Disk read bottleneck. Check if memory is insufficient (Buffer Pool thrashing) or if queries are doing Table Scans.
-   **CXPACKET**: 平行處理等待。通常伴隨 `CXCONSUMER`。若過高，可能需要調整 `MAXDOP` (Max Degree of Parallelism) 或優化查詢計畫。
    **CXPACKET**: Parallelism wait. Often accompanies `CXCONSUMER`. If too high, may need to adjust `MAXDOP` or optimize query plans.
-   **WRITELOG**: Transaction Log 寫入慢。檢查磁碟寫入效能。
    **WRITELOG**: Slow Transaction Log writes. Check disk write performance.

### Step 4: 設定 Extended Events 捕捉慢查詢 (Set up XEvents for Slow Queries)

為了捕捉偶發的慢查詢，我們建立一個 XEvent Session。

To capture sporadic slow queries, we create an XEvent Session.

```sql
-- 建立 XEvent Session 捕捉超過 5 秒的 RPC 和 SQL Batch
-- Create XEvent Session to capture RPC and SQL Batch > 5 seconds
CREATE EVENT SESSION [CaptureSlowQueries] ON SERVER
ADD EVENT sqlserver.rpc_completed(
    WHERE (duration > 5000000) -- Microseconds (5 sec)
),
ADD EVENT sqlserver.sql_batch_completed(
    WHERE (duration > 5000000)
)
ADD TARGET package0.event_file(
    SET filename=N'C:\Log\SlowQueries.xel'
)
WITH (MAX_DISPATCH_LATENCY = 5 SECONDS);
GO

-- 啟動 Session (Start Session)
ALTER EVENT SESSION [CaptureSlowQueries] ON SERVER STATE = START;
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 Production 使用 SQL Profiler (Using SQL Profiler in Production)

-   **錯誤 (Pitfall)**：習慣性開啟 SQL Profiler GUI 連接 Production Server 進行側錄。
    **Pitfall**: Habitually opening SQL Profiler GUI connected to Production Server for tracing.
-   **後果 (Consequence)**：Profiler 是一個極高消耗的工具（Client-side rendering），可能導致伺服器效能進一步惡化，甚至當機。
    **Consequence**: Profiler is a very high-overhead tool (client-side rendering) that can further degrade server performance or even crash it.
-   **修正 (Fix)**：使用 **Extended Events** 或 **Server-side Trace**。XEvents 引擎直接整合在 SQLOS 中，效能損耗極低。
    **Fix**: Use **Extended Events** or **Server-side Trace**. The XEvents engine is integrated directly into SQLOS with minimal performance overhead.

## 5.2 看到 `CXPACKET` 就將 MAXDOP 設為 1 (Setting MAXDOP to 1 upon seeing `CXPACKET`)

-   **錯誤 (Pitfall)**：發現 `CXPACKET` 是最高的 Wait Type，直接將全域 `MAXDOP` 設為 1（禁用平行處理）。
    **Pitfall**: Seeing `CXPACKET` as the top Wait Type and immediately setting global `MAXDOP` to 1 (disabling parallelism).
-   **後果 (Consequence)**：雖然消除了等待，但也扼殺了大型報表或分析型查詢的效能。`CXPACKET` 只是代表查詢正在使用多核心，不一定是壞事。
    **Consequence**: While it eliminates the wait, it kills performance for large reports or analytical queries. `CXPACKET` just means queries are using multiple cores; it's not inherently bad.
-   **修正 (Fix)**：檢查 `Cost Threshold for Parallelism`（預設值 5 太低，建議調至 50+）。針對特定查詢優化，而非全域禁用。
    **Fix**: Check `Cost Threshold for Parallelism` (default 5 is too low, suggest 50+). Optimize specific queries rather than disabling globally.

## 5.3 忽略 Signal Wait Time (Ignoring Signal Wait Time)

-   **錯誤 (Pitfall)**：只看 `wait_time_ms`，忽略 `signal_wait_time_ms`。
    **Pitfall**: Looking only at `wait_time_ms` and ignoring `signal_wait_time_ms`.
-   **原因 (Why)**：`Wait Time` = `Resource Wait` + `Signal Wait`。
    -   `Resource Wait`: 等待 I/O 或鎖。
    -   `Signal Wait`: 資源好了，但在 CPU 佇列排隊的時間。
    **Why**: `Wait Time` = `Resource Wait` + `Signal Wait`.
    -   `Resource Wait`: Waiting for I/O or locks.
    -   `Signal Wait`: Resource ready, but waiting in CPU queue.
-   **修正 (Fix)**：如果 `Signal Wait` 佔總等待時間比例很高（例如 > 20%），這明確指向 **CPU 壓力**，加記憶體或 SSD 沒用，需要優化高 CPU 消耗的查詢或增加 CPU 核心。
    **Fix**: If `Signal Wait` is a high percentage of total wait time (e.g., > 20%), this clearly points to **CPU Pressure**. Adding RAM or SSDs won't help; you need to optimize high-CPU queries or add CPU cores.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何區分資料庫變慢是因為 I/O 瓶頸還是 CPU 瓶頸？
**How do you distinguish if a database slowdown is due to I/O bottlenecks or CPU bottlenecks?**

-   **高分回答要點 (Key Points)**：
    -   提及 `sys.dm_os_wait_stats`。
    -   **I/O Bound**: 主要 Wait Types 為 `PAGEIOLATCH_*` (讀取) 或 `WRITELOG` (寫入)。
    -   **CPU Bound**: 主要 Wait Types 為 `SOS_SCHEDULER_YIELD`，或者 `Signal Wait Time` 佔比較高。
    -   提及檢查執行計畫，高 CPU 通常來自於大量的 Logical Reads（即使在記憶體中）或複雜運算。

## Q2: 生產環境發生嚴重的 Parameter Sniffing 導致效能驟降，你會如何處理？
**Severe Parameter Sniffing causes performance degradation in Production. How do you handle it?**

-   **高分回答要點 (Key Points)**：
    -   **短期止血 (Immediate)**：找出該查詢的 `Plan Handle`，使用 `DBCC FREEPROCCACHE (plan_handle)` 清除特定計畫，讓 SQL Server 重新編譯。
    -   **中期 (Medium)**：在 SQL 語句加入 `OPTION (RECOMPILE)` 或 `OPTION (OPTIMIZE FOR UNKNOWN)`（需改 Code）。
    -   **長期 (Long)**：啟用 Query Store，強制固定一個穩定的執行計畫 (Force Plan)。

## Q3: 請解釋 `sys.dm_exec_requests` 與 `sys.dm_exec_sessions` 的區別。
**Explain the difference between `sys.dm_exec_requests` and `sys.dm_exec_sessions`.**

-   **高分回答要點 (Key Points)**：
    -   `sys.dm_exec_sessions` 列出所有連接到 DB 的連線（包含閒置的）。
    -   `sys.dm_exec_requests` 只列出**當前正在執行**（Active）的請求。
    -   Troubleshooting 時通常先看 Requests 找瓶頸，再回頭看 Sessions 找來源資訊（如 Login Name, Host Name）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)

1.  **Wait Stats 是聽診器**：透過 `sys.dm_os_wait_stats` 理解資料庫在「等什麼」，是效能調優的起點。
    **Wait Stats are the Stethoscope**: Understanding what the database is "waiting for" via `sys.dm_os_wait_stats` is the starting point for tuning.
2.  **即時監控靠 Requests**：`sys.dm_exec_requests` 結合 `sys.dm_exec_sql_text` 是即時抓出「兇手」的最快方法。
    **Real-time Monitoring via Requests**: `sys.dm_exec_requests` combined with `sys.dm_exec_sql_text` is the fastest way to catch the "culprit" in real-time.
3.  **告別 Profiler**：全面轉向 Extended Events (XEvents) 進行低負載的詳細追蹤。
    **Goodbye Profiler**: Fully transition to Extended Events (XEvents) for low-overhead, detailed tracing.
4.  **區分 Resource vs. Signal Wait**：這能幫助你判斷是資源不足（I/O, Lock）還是 CPU 排程壓力。
    **Distinguish Resource vs. Signal Wait**: This helps you determine if it's resource starvation (I/O, Lock) or CPU scheduling pressure.
5.  **Blocking 是常見殺手**：學會追蹤 `blocking_session_id` 並理解 Lock Chain。
    **Blocking is a Common Killer**: Learn to trace `blocking_session_id` and understand the Lock Chain.

## 後續延伸 (Next Steps)

-   **Query Store (查詢存放區)**：這是現代 SQL Server (2016+) 的「飛行記錄器」。下一階段應學習如何利用 Query Store 進行歷史效能回溯與 Plan Regression 分析。
    **Query Store**: This is the "flight recorder" for modern SQL Server (2016+). The next step is to learn how to use Query Store for historical performance regression analysis.
-   **Index Tuning (索引調優)**：監控只是發現問題，解決問題往往需要調整索引。建議深入研究 Clustered vs. Non-Clustered Index 及 Include Columns 的策略。
    **Index Tuning**: Monitoring only finds the problem; solving it often requires index adjustments. Dive deep into Clustered vs. Non-Clustered Indexes and Include Columns strategies.