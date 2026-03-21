# 效能調校：吞吐量與延遲的權衡 / Performance Tuning: Throughput vs. Latency Trade-offs

## Mental model｜心智模型

在 Kafka 的效能世界中，**吞吐量 (Throughput)** 與 **延遲 (Latency)** 往往是一場零和遊戲，但並非總是絕對對立。理解它們的關係需要建立以下的心智模型：

### 1. 公車 vs. 計程車模型 (The Bus vs. Taxi Analogy)
- **高吞吐量 (High Throughput)** 就像**公車**。公車會等待乘客坐滿（Batching）才發車。雖然第一位上車的乘客需要等待（增加了延遲），但單次運送的人數多，平均每人的運輸成本（CPU/Network overhead）最低。
- **低延遲 (Low Latency)** 就像**計程車**。乘客一上車就立刻出發。雖然第一時間到達目的地，但道路上會充滿車輛，導致擁塞，且單位運輸成本極高。

### 2. 批次處理視窗 (The Batching Window)
Kafka 的效能核心在於 **Micro-batching**。
- **Producer 端**：我們在記憶體中累積多少數據才發送？(`batch.size`, `linger.ms`)
- **Broker 端**：寫入磁碟時，Page Cache 何時 flush？
- **Consumer 端**：一次拉取多少數據？(`fetch.min.bytes`)

**關鍵思維**：調校的目標不是「消除延遲」，而是找到**業務可接受的最大延遲（SLA）**，在此限制下最大化吞吐量。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優化高吞吐量場景 (Optimizing for High Throughput)
適用於：日誌收集、資料倉儲入庫、離線分析 (Log Aggregation, Data Warehousing, Offline Analytics)。

*   **Producer Batching Strategy**:
    *   **增加 `batch.size`**：預設值通常太小（16KB）。建議提升至 `64KB`、`128KB` 甚至更高，減少網路請求次數。
    *   **增加 `linger.ms`**：給予 Producer 緩衝時間來填滿 Batch。設定 `10ms` - `100ms` 可以顯著提升吞吐量。
    *   **啟用壓縮 (Compression)**：使用 `compression.type=lz4` 或 `zstd`。這會增加 CPU 負載但大幅減少網路頻寬與磁碟 I/O。
*   **Consumer Tuning**:
    *   增加 `fetch.min.bytes`：告訴 Broker「除非累積了 X bytes 的資料，否則別回傳給我」，減少空轉請求。

### 2. 優化低延遲場景 (Optimizing for Low Latency)
適用於：即時詐欺偵測、即時通訊、高頻交易 (Fraud Detection, Real-time Messaging, HFT)。

*   **Producer Strategy**:
    *   **`linger.ms=0` (或極低值)**：確保訊息產生後立即發送。
    *   **`acks` 的權衡**：`acks=1` (Leader only) 比 `acks=all` 快，但有遺失風險。若必須 `acks=all`，請確保 `min.insync.replicas` 配置得當以避免過度等待。
*   **Broker & Infrastructure**:
    *   **SSD 是必須的**：雖然 Kafka 依賴順序寫入，但在高併發與隨機讀取（追趕進度）時，SSD 的 IOPS 至關重要。
    *   **Page Cache**：確保 OS 有足夠的 RAM 作為 Page Cache。不要將 JVM Heap 設定得過大（建議 Heap 佔 RAM 的 50% 以下，剩下的給 OS）。

### 3. JVM 與 OS 層級優化 (JVM & OS Tuning)
*   **Garbage Collection**: 使用 **G1GC** 或 **ZGC** (Java 11/17+)。長時間的 Stop-the-world (STW) 是造成 P99 延遲飆高的元兇。
*   **File Descriptors**: Kafka Broker 會開啟大量連線與檔案，確保 `ulimit -n` 至少為 `100,000`。
*   **Swappiness**: 設定 `vm.swappiness=1`。絕對避免 Broker 記憶體被 Swap 到磁碟，這會導致效能崩潰。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 同步發送的陷阱 (The Synchronous Send Trap)
最常見的效能殺手是在 Producer 端使用同步發送。
*   ❌ **Anti-pattern**: `producer.send(record).get()`
*   這會強迫每一條訊息都經歷完整的 Round-trip time (RTT)，將吞吐量限制在 `1 / RTT`，完全破壞了 Kafka 的 Batching 機制。

### 2. 過多的分區 (Excessive Partitions)
*   雖然 Partition 是平行處理的單位，但**不是越多越好**。
*   過多的 Partitions 會導致：
    *   Broker 重啟時大量的 Leader Election（導致長時間不可用）。
    *   Producer 端記憶體碎片化（每個 Partition 都要一個 Buffer）。
    *   增加 End-to-end 延遲。
*   **Rule of Thumb**: 單一 Broker 的 Partition 總數建議控制在 4,000 以內，整個 Cluster 不超過 200,000（視硬體而定）。

### 3. 預設配置直接上線 (Running on Defaults)
*   Kafka 的預設配置是為了「通用性」與「相容性」，而非「高效能」。
*   例如：預設的 `num.network.threads` 或 `num.io.threads` 在高核心數的機器上可能過低。

### 4. 忽略網路頻寬飽和 (Ignoring Network Saturation)
*   如果你的 `compression.type=none` 且流量巨大，網卡 (NIC) 往往比 CPU 或 Disk 先成為瓶頸。監控網路頻寬使用率是調校的第一步。

---

## Checklists & workflows｜檢查清單與流程

在進行效能調校前，請依序執行以下檢查：

### Phase 1: Baseline & Goals (基準與目標)
- [ ] **定義目標**：我是要優化 Throughput (MB/s) 還是 Latency (ms)？
- [ ] **建立基準 (Baseline)**：在目前的配置下，量測 P99 Latency 與 Max Throughput。
- [ ] **確認硬體瓶頸**：使用 `top`, `iostat`, `sar` 檢查是 CPU、Disk I/O 還是 Network 飽和？

### Phase 2: Producer Tuning (生產者調校)
- [ ] **Batch Size**：若目標是吞吐量，嘗試將 `batch.size` 設為 `32KB` 或 `64KB`。
- [ ] **Linger Time**：若 `batch.size` 從未填滿，增加 `linger.ms` (例如 5-10ms)。
- [ ] **Compression**：啟用 `lz4` 或 `zstd` 並觀察 CPU 使用率變化。
- [ ] **Buffer Memory**：確保 `buffer.memory` 足夠大，避免 `BufferExhaustedException` 或阻塞。

### Phase 3: Broker & Consumer Tuning (伺服器與消費者調校)
- [ ] **Replica Fetchers**：若 Follower 追不上 Leader，增加 `num.replica.fetchers`。
- [ ] **Disk Throughput**：確保 `log.dirs` 分散在不同的實體磁碟（若使用 HDD）。
- [ ] **Consumer Fetch**：調整 `fetch.min.bytes` 與 `fetch.max.wait.ms` 以平衡輪詢效率。
- [ ] **OS Tuning**：檢查 `vm.swappiness` 是否已設為 1，`ulimit` 是否足夠。

---

## Real-world examples｜實戰案例

### Scenario A: 日誌聚合平台 (Log Aggregation - ELK Stack)
**情境**：每天需處理 TB 級別的應用程式日誌，延遲 5 秒內都可接受，重點是不掉資料且吞吐量大。

**Configuration Strategy**:
```properties
# Producer Config
# 犧牲一點延遲，換取極致的吞吐量與壓縮比
batch.size=131072        # 128KB
linger.ms=50             # 等待 50ms 湊滿 Batch
compression.type=zstd    # 高壓縮比，節省頻寬與儲存
acks=1                   # 日誌允許極少量遺失，換取寫入速度 (視業務而定)

# Consumer Config
fetch.min.bytes=1048576  # 1MB, 累積多一點再回傳
```

### Scenario B: 支付交易通知 (Payment Notification)
**情境**：使用者付款後，必須在 500ms 內收到通知。流量平穩，但對延遲極度敏感。

**Configuration Strategy**:
```properties
# Producer Config
# 盡快發送，不要等待
batch.size=16384         # 預設值或更小，避免記憶體浪費
linger.ms=0              # 立即發送
compression.type=lz4     # 快速壓縮，低 CPU overhead
acks=all                 # 金融數據不能掉，必須強一致性

# Broker Config
# 確保資料安全性與快速寫入
min.insync.replicas=2
num.io.threads=8         # 增加 IO 執行緒以應對頻繁的小寫入
```

### Decision Tree for Tuning (調校決策樹)

```text
START
  |
  +-- Is Latency Critical? (< 100ms)
  |     |
  |     +-- YES: Set linger.ms=0, compression=lz4/none, check GC pauses.
  |     |
  |     +-- NO: Go to Throughput Optimization.
  |
  +-- Is Throughput Critical? (High Volume)
        |
        +-- YES: Increase batch.size (64k+), linger.ms (10ms+), compression=zstd/lz4.
        |        Check Network Bandwidth & Disk I/O.
        |
        +-- NO: Default configs might be fine. Monitor resource usage.
```