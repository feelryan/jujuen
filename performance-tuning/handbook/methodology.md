# 分析方法論：USE 與 RED 方法 / Analysis Methodology: USE and RED Methods

## Mental model｜心智模型

在效能優化的世界裡，最昂貴的成本不是硬體，而是工程師「猜測問題在哪裡」所花費的時間。要避免「猜測式優化（Guess-driven optimization）」，你需要建立兩套互補的心智模型：**由下而上的資源視角 (USE)** 與 **由上而下的服務視角 (RED)**。

In the world of performance tuning, the most expensive cost is not hardware, but the time engineers spend guessing where the problem lies. To avoid "Guess-driven optimization," you need two complementary mental models: the **Bottom-Up Resource View (USE)** and the **Top-Down Service View (RED)**.

### 1. USE Method (For Resources)
**適用對象：** 硬體資源、作業系統、基礎設施 (CPU, Memory, Disk, Network)。
**核心思想：** 如果系統變慢，一定是某個資源無法滿足需求。
**Analogy:** 就像檢查汽車引擎。油路是否堵塞？轉速是否過高？溫度是否過熱？

- **U**tilization (使用率): 資源忙碌的時間百分比 (e.g., CPU 90%)。
- **S**aturation (飽和度): 有多少工作因為資源忙碌而在排隊 (e.g., Run queue length, Disk wait)。
- **E**rrors (錯誤): 資源層級發生的錯誤 (e.g., Memory OOM, Network packet drops)。

### 2. RED Method (For Services)
**適用對象：** 微服務、API、Request-driven 的應用程式。
**核心思想：** 關注使用者體驗與服務品質，而非底層細節。
**Analogy:** 就像檢查交通狀況。車流量多大？有沒有發生車禍？從 A 到 B 要花多久？

- **R**ate (請求速率): 每秒處理多少請求 (RPS/QPS)。
- **E**rrors (錯誤率): 請求失敗的比率 (HTTP 5xx)。
- **D**uration (持續時間/延遲): 處理請求所需的時間 (Latency Distribution)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Dashboard Strategy: RED First, USE Second
**儀表板策略：先看 RED，再查 USE**

在監控儀表板（Dashboard）的設計上，應遵循「由外而內」的順序：
1.  **Top-level (RED):** 每個 Service 的首頁都應該展示 Rate, Errors, Duration。這告訴你 **"Is the system happy?"**（系統健康嗎？）
2.  **Drill-down (USE):** 當 RED 指標異常（例如 Duration 飆高），再點擊進入查看 Node/Container 層級的 USE 指標。這告訴你 **"Why is it unhappy?"**（為什麼不健康？）

### 2. The "Saturation" Warning Sign
**關注「飽和度」而非僅僅是「使用率」**

很多工程師看到 CPU 100% 就驚慌，但如果 Queue length 是 0，這可能只代表系統正在充分利用資源計算。
*   **Pattern:** 真正的效能殺手通常是 **Saturation (Queueing)**。
*   **Action:** 檢查 Load Average (CPU queue), Disk I/O wait time, Thread Pool active count。一旦出現排隊，延遲（Latency）就會呈指數級上升。

### 3. Latency Distribution over Averages
**使用分佈而非平均值**

在 RED 的 Duration 中，**永遠不要只看平均值 (Average/Mean)**。
*   **Why:** 平均值會掩蓋長尾效應（Long-tail latency）。如果 1% 的請求需要 10 秒，平均值可能看起來還是很快。
*   **Best Practice:** 監控 P50 (中位數), P95, 和 P99。P99 反映了最慢的那批使用者的體驗，通常也是問題最早浮現的地方。

### 4. The "Errors" Priority
**錯誤優先原則**

在 USE 方法中，**Errors** 應該最先被檢查。
*   **Reason:** 資源錯誤（如 Disk Full, OOM Killer, Network Collisions）通常能直接解釋效能問題，且檢查成本最低。
*   **Flow:** Errors -> Saturation -> Utilization.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Streetlight Effect (路燈效應)
**只檢查容易檢查的地方，而不是問題所在的地方。**
*   **Anti-pattern:** 系統變慢了，工程師立刻去檢查 Application Logs 或 Database Slow Query，只因為那裡有現成的工具，卻忽略了可能是 Network Bandwidth 飽和或 Context Switch 過高。
*   **Correction:** 嚴格執行 USE 流程，列出**所有**資源（CPU, Mem, Disk, Net, Bus...）並逐一檢查，不要跳過難以觀測的資源。

### 2. Confusing Utilization with Saturation
**混淆使用率與飽和度。**
*   **Anti-pattern:** 認為 50% CPU 使用率代表系統很健康。
*   **Pitfall:** 如果是單執行緒應用（如 Node.js Event Loop 或 Redis），單核 100% 就已經造成整體服務的 Saturation，即便整機 CPU 看起來只有 10%。

### 3. Ignoring the "Zero" Error Rate
**忽視「零」錯誤率的陷阱。**
*   **Anti-pattern:** 在 RED 方法中，Errors 為 0，Rate 卻突然下降。
*   **Pitfall:** 有時候系統卡死（Deadlock）或網路斷線導致請求根本進不來，這時 Error Rate 可能是 0，但 Rate 會掉到地板。
*   **Correction:** Rate 與 Errors 必須同時解讀。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Performance Incident Response
當收到效能告警時的標準排查流程：

1.  **Assess Impact (RED Method):**
    *   [ ] **Rate:** 流量是否暴增？還是突然歸零？
    *   [ ] **Errors:** 是 5xx 錯誤？還是 Timeout？
    *   [ ] **Duration:** 是整體變慢？還是只有 P99 變慢？
    *   *Decision:* 確定是特定服務問題，還是全域問題。

2.  **Isolate Resource (USE Method):**
    *   針對受影響的節點/容器，依序檢查：
    *   [ ] **Errors:** `dmesg`, `netstat -s`, application crash logs.
    *   [ ] **CPU:** Usage (User/Sys), Saturation (Load Avg, Run Queue).
    *   [ ] **Memory:** Usage (RSS/Cache), Saturation (Swap activity, OOM kills).
    *   [ ] **Disk I/O:** Usage (IOPS/Throughput), Saturation (Wait time, Queue length).
    *   [ ] **Network:** Usage (Bandwidth), Saturation (Dropped packets, Retransmits).

3.  **Correlate & Fix:**
    *   [ ] 將 RED 的時間點與 USE 的異常點對齊。
    *   [ ] 驗證假設（例如：高 Latency 是由 Disk I/O Wait 引起的）。

### Checklist: Implementing Observability
在建置監控系統時的自我檢查：

- [ ] **Coverage:** 每個微服務是否都具備 RED 指標？
- [ ] **Granularity:** USE 指標是否能細分到每個 Container/Pod？
- [ ] **Retention:** 是否保留了足夠長的高解析度數據來分析 P99？(1分鐘的平均值會抹平 1秒鐘的尖峰)。
- [ ] **Alerting:** 告警是否基於症狀 (High Latency/Error Rate) 而非原因 (High CPU)？(避免 Flapping alerts)。

---

## Real-world examples｜實戰案例

### Case 1: The "Mysterious" Slowdown (USE Method Win)
**情境：** 一個 Java API 服務在流量高峰時回應變慢，但 CPU 使用率只有 40%，Memory 也很充足。團隊懷疑是程式碼鎖競爭（Lock Contention）。

**Analysis:**
1.  **Check Errors:** 無明顯 Application Error。
2.  **Check CPU:** 40% 使用率，Load Average 也不高。
3.  **Check Memory:** Heap 充足，GC 正常。
4.  **Check Disk (USE):** 發現 Disk **Saturation** 極高，Write Queue 長度持續 > 10。
5.  **Root Cause:** 雖然 API 本身不寫入硬碟，但同一台機器上的 Log Agent 設定錯誤，正在瘋狂同步寫入 Debug Log，導致 IO resource 耗盡，Block 住了 Java 的某些 I/O 操作。
6.  **Lesson:** 不用 USE 方法全面掃描資源，很容易陷入 Debug 程式碼的死胡同。

### Case 2: The Silent Failure (RED Method Win)
**情境：** 用戶投訴無法結帳，但伺服器 CPU/Memory 全部綠燈，沒有任何資源告警。

**Analysis:**
1.  **Check Rate (RED):** 結帳 API 的 Request Rate 從 500 req/s 掉到 50 req/s。
2.  **Check Errors (RED):** HTTP 500 錯誤率並未上升（因為請求根本沒處理完）。
3.  **Check Duration (RED):** P99 Latency 從 200ms 飆升到 30s (Timeout)。
4.  **Investigation:** 發現是一個第三方支付 Gateway 回應極慢。
5.  **Root Cause:** 應用程式的 Thread Pool 全部卡在等待第三方回應（Saturation at Application Level），導致無法處理新請求。
6.  **Lesson:** 資源層級 (USE) 看起來很健康（因為 CPU 都在 idle 等待），只有服務層級 (RED) 能揭露這種依賴性故障。