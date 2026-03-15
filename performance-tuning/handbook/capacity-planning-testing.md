# 容量規劃與負載測試 / Capacity Planning and Load Testing

## Mental model｜心智模型

在進行容量規劃與負載測試時，資深工程師不應只關注「伺服器會不會掛掉」，而應建立以下的心智模型：

### 1. 系統是非線性的 (Non-linearity)
系統效能很少是線性成長的。當負載增加 2 倍，資源消耗可能增加 2 倍，但一旦跨過某個 **膝點 (Knee Point)**——通常是資源飽和（如 CPU 100%、DB Connection Pool 耗盡）或鎖競爭急劇上升時，延遲會呈指數級飆升，吞吐量反而會下降。
> **Mental Image**: 想像高速公路。車流量在達到飽和點之前，車速維持穩定；一旦超過飽和點，車速會瞬間降至接近零，形成塞車（Congestion Collapse）。

### 2. 容量是「在特定 SLO 下」的最大吞吐量
"Capacity" is not just "Max Throughput".
容量的定義必須包含品質約束。如果系統每秒能處理 10,000 個請求，但錯誤率達 50% 或延遲達 10 秒，這不叫容量，這叫故障。
> **Formula**: `Capacity = Max Throughput @ (Latency < X ms && Error Rate < Y%)`

### 3. 木桶效應與短板 (The Bottleneck Principle)
系統的整體容量取決於最弱的那個環節（Bottleneck）。可能是資料庫的 IOPS、外部 API 的 Rate Limit、或是應用程式內的某個 Global Lock。負載測試的本質就是**尋找並移動瓶頸**的過程。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 定義明確的 SLO/SLA (Service Level Objectives)
在測試前，必須先定義什麼是「合格」。
- **Latency SLO**: 例如 `p99 < 500ms`（99% 的請求需在 500ms 內完成）。
- **Error Budget**: 允許的失敗率（例如 0.1%）。
- **Saturation**: 資源使用率上限（例如 CPU < 70%，預留緩衝給突發流量）。

### 2. 分層次的測試策略 (Tiered Testing Strategy)
不要只做一種測試，應針對不同目的設計場景：
- **Load Testing (負載測試)**: 模擬預期的峰值流量 (Peak Traffic)，驗證系統能否達標。
- **Stress Testing (壓力測試)**: 不斷加壓直到系統崩潰，目的是找到 **Breaking Point** 和瓶頸所在，並觀察系統能否自動恢復 (Recoverability)。
- **Soak/Endurance Testing (浸泡測試)**: 長時間（如 24h+）維持一定負載，檢測 Memory Leaks 或資源回收問題。
- **Spike Testing (尖峰測試)**: 模擬瞬間流量暴衝（如秒殺活動），測試 Auto-scaling 的反應速度。

### 3. 降級與熔斷策略 (Degradation & Circuit Breaking)
當負載超過容量時，系統應該「優雅地降級」而非「全盤崩潰」。
- **Load Shedding**: 主動丟棄多餘請求（回傳 HTTP 503），保護核心服務。
- **Feature Toggles**: 在高負載時關閉非核心功能（如推薦系統、複雜報表），只保留核心路徑（如結帳、登入）。
- **Circuit Breaker**: 當下游服務變慢時，快速失敗，避免 Thread Pool 被卡死。

### 4. 測試環境擬真度 (Environment Parity)
- **Data Volume**: 資料庫必須有與生產環境同量級的數據（Data Cardinality 會影響索引效率）。
- **Infrastructure**: 盡量使用與 Production 相同的規格，或者透過比例換算（但要注意非線性問題）。
- **Network Latency**: 測試環境若在內網，需模擬真實用戶的網路延遲。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 協調遺漏 (Coordinated Omission)
這是最常見且致命的壓測工具陷阱。
- **現象**: 傳統壓測工具（如簡單的 JMeter 設定）通常是「發送請求 -> 等待回應 -> 發送下一個」。如果伺服器變慢，工具發送請求的頻率也會變慢。
- **後果**: 測試報告顯示「吞吐量下降，但延遲還好」，實際上真實用戶的請求已經在排隊（Queueing），真實延遲比報告高得多。
- **解法**: 使用支援非同步發送或能修正 Coordinated Omission 的工具（如 Gatling, k6, wrk2），確保請求是按照預定頻率發出，不論伺服器是否回應。

### 2. 暖機不足 (Cold Start Bias)
- **現象**: 測試一開始就打入全量負載，導致大量 Timeout。
- **原因**: JVM 未 JIT 編譯、Connection Pool 未建立、Cache 是空的。
- **解法**: 實施 **Ramp-up** 階段，讓系統預熱（Warm-up）後再測量數據。

### 3. 忽視寫入路徑 (Read-Heavy Bias)
- **現象**: 只測試讀取（GET），忽略寫入（POST/PUT）。
- **風險**: 寫入通常涉及鎖（Locking）、交易（Transaction）和磁碟 I/O，往往是真正的瓶頸所在。

### 4. 測試隔離性差 (Noisy Neighbors)
- **現象**: 在共享環境（Shared Environment）做壓測，結果受其他團隊或服務影響而不準確。
- **解法**: 盡可能在獨立環境測試，或在夜間低峰期進行（若必須在 Prod 測）。

---

## Checklists & workflows｜檢查清單與流程

### Phase 1: Planning & Design (規劃階段)
- [ ] **定義目標**: 這次測試是為了驗證 SLO、尋找極限、還是重現 Bug？
- [ ] **量化指標**: 預期的 RPS (Requests Per Second) 是多少？目前的 Prod 峰值是多少？預計成長倍數？
- [ ] **建立模型**: 繪製關鍵路徑（Critical Path），識別外部依賴（3rd party APIs, DB, Cache）。
- [ ] **數據準備**: 準備足夠的測試帳號、商品數據，避免所有請求都打同一個 ID (Hotspot)。

### Phase 2: Execution (執行階段)
- [ ] **確認監控**: 確保 APM (Application Performance Monitoring)、DB Metrics、Host Metrics 都已開啟且粒度足夠。
- [ ] **清理環境**: 重置 Cache 或標記測試數據，避免污染。
- [ ] **執行 Ramp-up**: 緩慢增加負載，觀察系統線性行為。
- [ ] **執行 Peak Load**: 維持目標負載，觀察延遲分佈 (p50, p95, p99)。
- [ ] **執行 Overload**: 超過目標負載，觀察降級機制是否啟動。

### Phase 3: Analysis (分析階段)
- [ ] **檢查瓶頸**:
    - CPU 是否飽和？（User vs System time）
    - 記憶體是否頻繁 GC？
    - DB 連線數是否用盡？
    - 網路頻寬是否打滿？
- [ ] **驗證錯誤率**: HTTP 5xx 的比例是否在允許範圍內？
- [ ] **撰寫報告**: 包含測試場景、結果摘要、瓶頸分析、優化建議。

---

## Real-world examples｜實戰案例

### Case 1: 電商大促銷的容量規劃 (E-commerce Flash Sale)

**情境**: 雙 11 活動，預計流量是平日的 10 倍。
- **挑戰**: 瀏覽商品（讀）與下單（寫）比例劇烈變化。瞬間流量會導致 DB 鎖競爭。
- **策略**:
    1.  **讀寫分離**: 確保商品詳情頁走 Cache 或 Read Replicas。
    2.  **非同步下單**: 使用 Message Queue (Kafka/RabbitMQ) 緩衝下單請求，前端顯示「排隊中」，後端依據 DB 處理能力慢慢消化。
    3.  **壓測設計**:
        - 場景 A (瀏覽): 高併發讀取，驗證 CDN 和 Redis 命中率。
        - 場景 B (搶購): 高併發寫入，驗證 MQ 的堆積速度與 Consumer 的處理上限。
        - **關鍵發現**: 壓測發現 Inventory Service 在扣庫存時因 Row Lock 導致 DB CPU 飆高。
    4.  **優化**: 實作 Redis Lua Script 預扣庫存，減少直接 DB 交易。

### Case 2: 記憶體洩漏的幽靈 (The Slow Memory Leak)

**情境**: 一個新上線的微服務，在負載測試 1 小時內表現完美，但在 Production 運行 2 天後會 OOM (Out of Memory) 重啟。
- **問題**: 標準 Load Test 時間太短，無法抓出緩慢的 Memory Leak。
- **策略**: 執行 **Soak Testing (浸泡測試)**。
    - 以 50% 的峰值負載，持續運行 24 小時。
    - 配合 Profiler (如 Java VisualVM, Go pprof) 觀察 Heap Usage 趨勢。
- **結果**: 發現某個 Log Library 在特定 Error 發生時會將 Context 物件放入一個未清理的 List 中。
- **Lesson**: 容量規劃不只是看 RPS，還要看「持續運行的穩定性」。