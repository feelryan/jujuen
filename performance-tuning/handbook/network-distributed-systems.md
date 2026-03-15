# 網路 I/O 與分散式系統效能 / Network I/O and Distributed System Performance

## Mental model｜心智模型

在單機程式中，函式呼叫（Function Call）的成本極低，我們往往視為理所當然。但在分散式系統中，每一次跨服務的呼叫都是一次「長途運輸」。要掌握網路效能，你必須打破「網路是可靠的」與「延遲為零」的幻想。

### 1. The Cost of Transport (運輸成本模型)
將網路請求想像成**物流運輸**，而不僅僅是資料傳輸：
- **Serialization (包裝/序列化)**：將記憶體中的物件轉換成位元組（Bytes）。就像把傢俱拆解裝箱，這需要消耗 CPU。
- **Transmission (運輸/傳輸)**：位元組在光纖或銅線中移動。這受限於頻寬（Bandwidth）和物理距離（Propagation Delay）。
- **Deserialization (拆箱/反序列化)**：接收端將位元組還原成物件。這同樣消耗 CPU。

**效能公式：**
$$ \text{Total Latency} = \text{Serialization} + \text{Queueing} + \text{Network Flight Time} + \text{Processing} + \text{Deserialization} $$

### 2. Bandwidth vs. Latency (頻寬與延遲)
- **頻寬 (Bandwidth)** 是水管的粗細（單位時間能過多少水）。
- **延遲 (Latency)** 是水流從一端流到另一端需要的時間。
- **誤區**：增加頻寬通常無法降低延遲（除非你的瓶頸是頻寬飽和）。優化網路 I/O 往往是在對抗物理距離與封包處理次數，而不僅僅是加大頻寬。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Protocol Selection: HTTP/JSON vs. gRPC/Protobuf
選擇通訊協定是效能優化的第一步。
- **External/Public APIs (HTTP + JSON)**:
  - **Pros**: Human-readable, 廣泛支援, 易於除錯。
  - **Cons**: 序列化/反序列化慢，Payload 體積大（重複的 Key 名稱）。
  - **Best Practice**: 對外服務或前端通訊使用。
- **Internal/Microservices (gRPC + Protobuf)**:
  - **Pros**: Binary 格式極小，序列化速度快（比 JSON 快 5-10 倍），強型別。
  - **Cons**: 需要 IDL (Proto files)，不易肉眼除錯。
  - **Best Practice**: 內部服務間的高頻通訊首選。

### 2. Connection Management (連線管理)
建立 TCP/TLS 連線是非常昂貴的操作（3-way handshake, TLS handshake）。
- **Connection Pooling (連線池)**: 永遠不要為每個請求建立新連線。重用現有的連線（Keep-Alive）。
- **Persistent Connections**: 確保 HTTP/1.1 的 `Connection: keep-alive` 或使用 HTTP/2 的 Multiplexing（多工複用）。

### 3. Data Efficiency (資料效率)
- **Filtering (欄位過濾)**: 實作 GraphQL 或類似 `?fields=id,name` 的機制，只傳輸需要的資料。
- **Compression (壓縮)**: 對於大於 1KB 的 Payload，啟用 Gzip 或 Brotli。這是用 CPU 時間換取網路傳輸時間的典型交易（Trade-off）。
- **Batching (批次處理)**: 將 10 個小的 API 呼叫合併成 1 個大的呼叫，減少 RTT (Round Trip Time) 的總和。

### 4. Load Balancing Strategies (負載平衡策略)
- **Round Robin**: 簡單，但可能導致請求堆積在處理慢的節點上。
- **Least Connections / Least Response Time**: 較佳選擇。將流量導向當前最閒置或回應最快的節點。
- **Client-side Load Balancing (e.g., gRPC lookaside)**: 消除中間的 Proxy hop，直接由客戶端選擇目標節點，減少延遲。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Chatty" Interface (碎嘴介面)
最常見的效能殺手。前端或呼叫端需要發送多次請求才能完成一個邏輯操作。
- **Scenario**: 取得 User ID -> 取得 User Profile -> 取得 User Orders。
- **Impact**: 延遲隨著請求次數線性疊加。
- **Fix**: 使用 **Backend-for-Frontend (BFF)** 模式或 Aggregation API，一次取回所有資料。

### 2. The N+1 Problem over Network
在資料庫層常見，但在微服務間更致命。
- **Scenario**: 取得列表（1次呼叫），然後對列表中的每一項去呼叫另一個服務獲取詳情（N次呼叫）。
- **Impact**: 網路風暴，極高的延遲。
- **Fix**: 實作 `GetByIds(list_of_ids)` 類型的批次接口。

### 3. Bloated Payload (過度膨脹的負載)
- **Scenario**: 為了顯示使用者名稱，卻回傳了包含地址、歷史訂單、設定等幾百 KB 的 JSON。
- **Impact**: 浪費頻寬，增加序列化 CPU 開銷，增加 GC 壓力。

### 4. Synchronous Chaining (同步鏈式呼叫)
- **Scenario**: Service A 呼叫 B，B 呼叫 C，C 呼叫 D。
- **Impact**: 延遲是所有服務的總和。任何一個環節卡住，整個請求就 Timeout。
- **Fix**: 改用 **Event-Driven Architecture (EDA)** 或非同步訊息佇列（Message Queue）。

### 5. Ignoring Serialization Cost
- **Scenario**: 在高吞吐系統中使用基於文字的格式（如 XML 或未優化的 JSON）。
- **Impact**: CPU 耗盡在字串解析上，而非業務邏輯。

---

## Checklists & workflows｜檢查清單與流程

在設計或優化分散式系統效能時，請使用此清單：

### Phase 1: Design & Protocol (設計階段)
- [ ] **協定選擇**：內部高頻通訊是否已考慮 gRPC/Thrift？若用 JSON，是否移除了不必要的欄位？
- [ ] **通訊模式**：是否可以將同步請求改為非同步（Message Queue）？
- [ ] **Payload 大小**：預估的 Payload 是否過大？是否需要分頁（Pagination）或壓縮？

### Phase 2: Implementation (實作階段)
- [ ] **Connection Pooling**：是否已設定連線池？Max Idle Connections 是否足夠？
- [ ] **Timeouts**：是否為所有網路呼叫設定了合理的 Timeout？（避免無限等待）
- [ ] **Retries**：重試機制是否包含 **Exponential Backoff**（指數退避）與 **Jitter**（隨機抖動）？（避免驚群效應 Thundering Herd）
- [ ] **Circuit Breaker**：是否實作了斷路器以防止級聯故障（Cascading Failures）？

### Phase 3: Observability (可觀測性)
- [ ] **Tracing**：是否導入 Distributed Tracing (如 OpenTelemetry/Jaeger) 來視覺化跨服務的延遲？
- [ ] **Metrics**：是否監控了網路 I/O 的飽和度、錯誤率與延遲（RED Method）？

---

## Real-world examples｜實戰案例

### Case 1: The "10-Second" Dashboard (N+1 網路呼叫)
**情境**：一個電商後台儀表板，載入需要 10 秒。
- **分析**：
  - 開啟 Network Tab 發現前端發出了 50+ 個請求。
  - 主 API 回傳了 50 筆訂單 ID。
  - 前端隨後對每筆訂單發起 `/api/order/{id}` 請求以獲取客戶名稱。
- **優化**：
  - **解法**：建立一個聚合 API `/api/orders/summary`，在後端一次撈取並組裝好資料。
  - **結果**：請求數從 51 降為 1，載入時間從 10s 降至 300ms。

### Case 2: The CPU-Bound Gateway (JSON Serialization Overhead)
**情境**：API Gateway 在流量高峰時 CPU 飆升至 100%，但網路頻寬未滿。
- **分析**：
  - 使用 Profiling 工具 (pprof) 發現 CPU 主要消耗在 `json.Marshal` 和 `json.Unmarshal`。
  - 內部微服務間全部使用龐大的 JSON 進行通訊。
- **優化**：
  - **解法**：將內部服務間的通訊從 HTTP/JSON 遷移至 gRPC/Protobuf。
  - **結果**：序列化 CPU 開銷降低 60%，Gateway 吞吐量提升 2 倍。

### Case 3: The Connection Storm (連線池設定錯誤)
**情境**：某個服務在重啟後，資料庫瞬間崩潰，連線數爆滿。
- **分析**：
  - 該服務使用 Serverless 架構，每個 Request 啟動一個 Function 實例。
  - 每個實例都嘗試建立一個新的 DB 連線，且沒有重用。
  - 流量進來時，瞬間產生數千個 `SYN` 封包。
- **優化**：
  - **解法**：引入 **RDS Proxy** 或在應用層實作全域的 Connection Pooling，限制最大連線數。
  - **結果**：資料庫連線數穩定在設定值，不再隨流量線性暴增。