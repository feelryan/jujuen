# 核心概念與心智模型：吞吐量、延遲與飽和度 / Core Concepts: Throughput, Latency, and Saturation

在深入任何工具或程式碼優化之前，我們必須建立正確的物理觀。效能問題通常不是「程式碼寫得慢」，而是系統資源分配與排隊理論（Queuing Theory）的體現。本章節將幫助你建立直覺，理解為什麼系統會在某個負載點突然崩潰，以及如何在速度（Latency）與量級（Throughput）之間做取捨。

## Mental model｜心智模型

### 1. The Performance Knee (效能拐點)
不要將系統想像成一條無限寬的直線高速公路。系統更像是一個**超市收銀台**。
- **Linear Zone (線性區)**：當顧客（Request）很少時，增加顧客並不會顯著增加等待時間。此時 Throughput 隨負載線性上升，Latency 保持平穩。
- **The Knee (拐點)**：當資源（CPU、I/O、Thread Pool）接近飽和（Saturation）時，隊伍開始形成。
- **Exponential Zone (指數區)**：一旦超過拐點，每增加一個 Request，Latency 會呈**指數級**飆升，而 Throughput 卻可能因 Context Switch 或資源爭奪而下降（Thrashing）。

> **Key Takeaway**: 效能優化的目標通常是**推遲拐點的到來**，或者在到達拐點時優雅降級（Graceful Degradation），而不是試圖消除物理限制。

### 2. Little's Law in Practice (利特爾定律實戰版)
雖然這是排隊理論公式，但在工程上它描述了**並發（Concurrency）**、**吞吐量（Throughput）**與**延遲（Latency）**的鐵三角關係：

$$ L = \lambda \times W $$

- **$L$ (Concurrency/Queue Size)**: 系統中正在處理加上排隊中的請求總數。
- **$\lambda$ (Throughput)**: 每秒處理的請求數 (RPS)。
- **$W$ (Latency)**: 請求停留在系統中的平均時間。

**直覺理解**：如果你希望在 Latency ($W$) 不變的情況下將 Throughput ($\lambda$) 翻倍，你必須準備兩倍的並發處理能力 ($L$)（例如兩倍的 Thread 或 Connection）。如果 $L$ 被限制住了（例如 DB Connection Pool 滿了），增加 $\lambda$ 只會導致 $W$ 暴增。

### 3. Amdahl's Law (阿姆達爾定律與並行極限)
不要盲目相信「加機器」或「多開 Thread」能解決所有問題。系統的加速極限受限於**不可平行化（Serial）**的部分。
- 如果程式中有 50% 的時間必須序列執行（例如搶同一把鎖、寫入同一個 Log 檔），無論你加多少 CPU，最高加速比永遠不會超過 2 倍。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Stop looking at Averages (拒絕平均值)
平均值（Average/Mean）是效能監控中最大的謊言。它會掩蓋極端值。
- **Pattern**: 使用 **Percentiles (百分位數)**。
    - **P50 (Median)**: 一般用戶的體驗。
    - **P95 / P99 (Tail Latency)**: 系統中最慢的那 1% 用戶體驗。這通常代表了系統的「長尾效應」，也是飽和度問題最先浮現的地方。
- **Why**: 一個 P99 飆高的系統，可能導致上游服務發生連鎖超時（Cascading Failure）。

### 2. Throughput vs. Latency Trade-off (批次與即時的取捨)
這是一個零和遊戲，你很難同時優化兩者。
- **Batching (批次處理)**: 累積 10 個 Request 一起送給 DB。
    - *優點*: 減少 I/O overhead，顯著提升 **Throughput**。
    - *缺點*: 第一個 Request 必須等待第十個到達才能處理，增加了 **Latency**。
- **Streaming/Real-time**: 來一個處理一個。
    - *優點*: 最低 **Latency**。
    - *缺點*: Context switch 與 I/O overhead 高，**Throughput** 上限較低。

### 3. Load Shedding & Backpressure (負載卸載與背壓)
當系統達到飽和度（Saturation > 80-90%）時，繼續接受請求是自殺行為。
- **Pattern**: 實作 **Fast Failure**。當 Queue 滿了或 CPU 過高，直接回傳 `503 Service Unavailable` 或 `429 Too Many Requests`。
- **Benefit**: 讓系統有喘息空間來處理當前的請求，避免進入 Thrashing（系統忙於切換任務而無法完成任何任務）狀態。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "100% Utilization" Myth (資源滿載誤區)
很多管理者認為買了伺服器就要跑到 CPU 100% 才划算。
- **Pitfall**: 對於線上服務（Online Service），CPU 超過 70-80% 通常意味著延遲將開始指數上升。
- **Consequence**: 缺乏 **Headroom (緩衝空間)** 來應對突發流量（Bursts）。一旦流量微增，系統直接卡死。

### 2. Premature Optimization on Non-Bottlenecks (非瓶頸的過早優化)
花一週時間將一個佔總執行時間 1% 的函式優化了 10 倍。
- **Pitfall**: 忽略了 Amdahl's Law。
- **Correction**: 永遠先做 Profiling。如果 DB Query 佔了 90% 的時間，優化 Java/Go 程式碼的 CPU 運算幾乎沒有意義。

### 3. Hidden Queues (隱藏的隊列)
你以為系統是同步的，但其實它在排隊。
- **Pitfall**: TCP Backlog、OS Disk Buffer、DB Connection Pool、ExecutorService 的 LinkedBlockingQueue。
- **Symptom**: 應用程式顯示處理時間很快，但 Client 端感覺非常慢。中間的差值就是花在「隱藏隊列」中的時間。

---

## Checklists & workflows｜檢查清單與流程

在進行效能調優或容量規劃時，請依序檢查以下項目：

### Phase 1: Define Goals (定義目標)
- [ ] **優化目標是什麼？** 是要更高的 RPS (Throughput) 還是更低的 Response Time (Latency)？
- [ ] **SLA/SLO 是多少？** 例如：P99 Latency < 200ms @ 10,000 RPS。沒有數字就無法優化。

### Phase 2: Baseline & Observability (基準與觀測)
- [ ] **是否已配置 Percentile 監控？** (P50, P90, P99)
- [ ] **是否測量了 Saturation？** (CPU Load, Memory Usage, Disk I/O, Network Bandwidth)
- [ ] **是否識別出主要瓶頸資源？** (是 CPU bound 還是 I/O bound？)

### Phase 3: Analysis (分析)
- [ ] **應用 Little's Law 驗證：** 目前的 Concurrency 是否符合 Throughput * Latency？如果不符，是否有隱藏的 Queue？
- [ ] **檢查 Amdahl's Law 限制：** 序列化操作（如 Global Lock、單一 DB 寫入點）佔比多少？
- [ ] **檢查拐點 (Knee)：** 進行壓力測試，找出 Latency 開始非線性增長的 RPS 閾值。

---

## Real-world examples｜實戰案例

### Case 1: The "Slow" API that wasn't CPU bound
**情境**：一個電商的結帳 API，TPS 卡在 500 上不去，但 CPU 使用率只有 10%。加機器也沒用。
**分析**：
- 這是典型的 **High Latency, Low CPU** (I/O Bound) 狀況。
- 檢查 **Saturation**：發現 DB Connection Pool 長期處於 "Exhausted" 狀態，等待獲取連線的 Thread 排得長長的。
- **Little's Law 應用**：$L$ (Connection Pool Size) 是固定的。因為 DB 寫入慢 ($W$ 很大)，導致 $\lambda$ (Throughput) 被 $L$ 限制住了。
- **解法**：優化 SQL 減少 $W$，或是增大 Pool Size (需考慮 DB 承受力)，或是改為非同步寫入 (Queue-based)。

### Case 2: The Microservice Chain Reaction
**情境**：Service A 呼叫 Service B。Service B 的 P50 延遲很穩，但 P99 偶爾飆高。Service A 卻頻繁 Timeout。
**分析**：
- Service B 的 P99 飆高是因為 Java GC Pause 或某個 Cache Miss。
- Service A 設定了固定的 Timeout。當 Service B 發生 P99 延遲時，Service A 的 Thread 被卡住等待。
- 隨著請求湧入，Service A 的 Thread Pool 瞬間**飽和 (Saturated)**，導致後續所有請求（即使是原本很快的請求）都在 Service A 的 Queue 中排隊。
- **解法**：在 Service A 實作 **Circuit Breaker (斷路器)** 與 **Bulkhead (艙壁模式)**，防止少數慢請求拖垮整個 Thread Pool。