# 水平擴展與分片策略 / Sharding & Horizontal Scaling

## Mental model｜心智模型

要理解 MongoDB 的 Sharding，請想像一個**圖書館系統**的擴建過程：

1.  **Single Replica Set (單一圖書館)**：
    *   所有的書都在一棟建築裡。
    *   **瓶頸**：書架滿了（Storage）、管理員忙不過來（CPU/RAM）、門口大排長龍（Network Bandwidth）。
    *   **垂直擴展 (Vertical Scaling)**：把圖書館蓋得更高、聘請更強壯的管理員。這有物理極限。

2.  **Sharding (分館系統)**：
    *   你決定蓋多個分館（**Shards**）。
    *   你需要一個總目錄中心（**Config Servers**），記錄哪本書在哪個分館。
    *   你需要多個櫃台接待員（**Mongos**），讀者把請求給接待員，接待員查目錄後，去正確的分館拿書。

### 核心組件 (Key Components)

*   **Mongos (The Router)**：應用程式的單一入口。它不存資料，只負責將請求「路由」到正確的 Shard。對 App 來說，Sharding 是透明的。
*   **Config Servers (The Brain)**：儲存 Cluster 的 Metadata（哪個 Chunk 在哪個 Shard）。如果它掛了，Cluster 就變成唯讀或無法運作。
*   **Shards (The Storage)**：實際儲存資料的 Replica Set。
*   **Shard Key (The Logic)**：決定資料如何分配的規則。這是 Sharding 成功與否的**唯一關鍵**。

### Chunk & Balancing
資料被切分成 **Chunks**（預設 64MB）。當某個 Shard 的 Chunk 太多時，**Balancer** 會在背景將 Chunk 搬移（Migration）到其他 Shard。這是一個昂貴的 IO 操作。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 選擇 Shard Key 的三大策略 (Shard Key Strategies)

選擇 Shard Key 是不可逆的（在舊版中），且直接決定效能。

*   **Ranged Sharding (範圍分片)**
    *   **機制**：基於 Shard Key 的值將資料切分為連續範圍（如 `A-M`, `N-Z`）。
    *   **優點**：對範圍查詢（Range Query）極度優化（如 `find({age: {$gt: 20, $lt: 30}})`），因為 `mongos` 知道只需查詢特定 Shard。
    *   **缺點**：若 Key 是單調遞增（Monotonic，如 Timestamp, ObjectId），所有新寫入都會集中在最後一個 Chunk（**Hotspot**），導致單點瓶頸。

*   **Hashed Sharding (雜湊分片)**
    *   **機制**：對 Shard Key 計算 Hash 值後分片。
    *   **優點**：極佳的寫入分佈（Write Distribution），即使 Key 是單調遞增的，Hash 後也會隨機散佈，避免 Hotspot。
    *   **缺點**：範圍查詢效能極差（Scatter-Gather），因為 `mongos` 必須詢問所有 Shards。

*   **Zoned / Tag-aware Sharding (區域分片)**
    *   **機制**：將特定 Shard 標記為特定用途（如 "US-East", "High-Performance"）。
    *   **場景**：
        *   **Data Locality**：將歐洲用戶資料存在歐洲 Shard（GDPR 合規）。
        *   **Tiered Storage**：近期資料存在 SSD Shard，舊資料存在 HDD Shard。

### 2. 高基數與低頻率 (High Cardinality & Low Frequency)

好的 Shard Key 必須具備：
*   **High Cardinality (高基數)**：有很多不同的值（如 `user_id`, `device_id`）。如果選 `gender`（只有男/女），你最多只能分兩個 Shard，且無法平衡巨大的 Chunk。
*   **Low Frequency (低頻率)**：單一 Key 值的出現頻率不能太高。如果某個 `user_id` 有 1000 萬筆訂單，這個 User 的資料會形成 **Jumbo Chunk**，無法被分割或搬移。

### 3. 預先分片 (Pre-splitting)

如果是全新的大流量 Collection，不要依賴 MongoDB 自動 Balancing。
*   **Pattern**：在寫入資料前，手動建立空的 Chunks 並分配到各個 Shard。
*   **Why**：避免一開始所有資料都寫入 Shard 0，直到 Balancer 介入才開始搬移（這時通常已經塞爆了）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Too Late" Sharding (太晚分片)
*   **現象**：等到 Disk 使用率達到 90% 或 RAM 已經完全不足時才開始啟用 Sharding。
*   **後果**：Sharding 初始化和 Chunk Migration 需要大量的 IO 和 CPU。在系統已經過載的情況下進行 Migration，會導致整個 Cluster 崩潰（Death Spiral）。
*   **建議**：在容量達到 60-70% 時就該開始規劃 Sharding。

### 2. Monotonic Shard Key (單調遞增鍵陷阱)
*   **現象**：使用 `_id` (ObjectId) 或 `created_at` 作為 **Ranged Sharding** 的 Key。
*   **後果**：**Insert Hotspot**。所有新的寫入都發生在「數值最大」的那個 Chunk（位於單一 Shard 上），其他 Shards 在寫入時閒置，完全失去了水平擴展寫入能力的意義。
*   **修正**：改用 Hashed Sharding，或使用複合鍵（Compound Key）。

### 3. Scatter-Gather Queries (廣播式查詢)
*   **現象**：查詢條件中**不包含** Shard Key。
*   **後果**：`mongos` 必須將查詢發送到**每一個** Shard，並等待所有 Shard 回傳結果後再合併。這會增加延遲並消耗所有 Shard 的連線數與資源。
*   **原則**：關鍵的 Operational Query 必須包含 Shard Key。

### 4. Jumbo Chunks (巨型區塊)
*   **現象**：某個 Shard Key 的值對應的資料量超過了 Chunk Size（預設 64MB）。
*   **後果**：MongoDB 無法分割只有單一 Key 值的 Chunk。這個 Chunk 會變成不可搬移的巨獸，導致該 Shard 資料量永遠比別人多，無法平衡。
*   **原因**：Shard Key 基數太低（Low Cardinality）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Do I need Sharding?
- [ ] **Dataset Size**: 資料量是否超過單機 Disk 上限？或是 Working Set (Indexes + Hot Data) 超過單機 RAM？(通常 > 2TB 或 RAM 不足時考慮)
- [ ] **Throughput**: 單機的寫入 IOPS 是否已達瓶頸？
- [ ] **High Availability**: 僅為了 HA？(如果是，請用 Replica Set，不需要 Sharding)。
- [ ] **Complexity**: 團隊是否有能力維護 Sharded Cluster？(複雜度是 Replica Set 的 3 倍以上)。

### Shard Key Selection Checklist
在決定 Shard Key `K` 之前，請驗證：

- [ ] **Cardinality**: `K` 的不重複值數量是否夠多？(至少要大於 Shard 數量的 100 倍以上)。
- [ ] **Write Distribution**: 寫入是否均勻分佈在不同的 `K` 值上？(避免單調遞增)。
- [ ] **Query Isolation**: 最頻繁、最關鍵的查詢是否包含 `K`？(避免 Scatter-Gather)。
- [ ] **Chunk Size**: 單一 `K` 值擁有的資料大小是否永遠小於 64MB？

### Operational Workflow: Adding a Shard
1.  **Provision**: 準備新的 Replica Set 機器。
2.  **Connect**: 確保新 Shard 與 Config Servers 和 Mongos 的網路通暢。
3.  **Add**: 在 `mongos` 執行 `sh.addShard()`。
4.  **Monitor**: 監控 Balancer 開始搬移 Chunk。**注意**：這會增加 Disk IO，請避開高峰時段或調整 Balancer Window。

---

## Real-world examples｜實戰案例

### Case 1: IoT Sensor Data (寫入密集型)
*   **情境**：數百萬個感測器每分鐘上傳數據。主要查詢是「查詢某裝置最近一小時的數據」。
*   **Bad Practice**：使用 `timestamp` 做 Ranged Sharding。
    *   *結果*：所有寫入都打在最後一個 Shard，寫入效能卡死。
*   **Good Practice**：使用 **Compound Key** `{ device_id: 1, timestamp: 1 }`。
    *   *結果*：`device_id` 確保資料分散在不同 Shard；`timestamp` 確保同一個裝置的資料在磁碟上盡量連續（優化讀取）。
    *   *注意*：如果單一 `device_id` 資料量過大，考慮改用 Hashed Sharding on `device_id`。

### Case 2: Multi-tenant SaaS (多租戶系統)
*   **情境**：B2B 應用，服務多個企業客戶（Tenants）。
*   **Strategy**：使用 `tenant_id` 作為 Shard Key。
*   **應用 Tag-aware Sharding**：
    *   客戶 A 是付費大戶，要求高性能 -> 將 SSD Shards 標記為 `tier: "gold"`，並將客戶 A 的 `tenant_id` 綁定到這些 Shards。
    *   客戶 B 要求資料留在德國 -> 將位於法蘭克福的 Shards 標記為 `region: "DE"`，綁定客戶 B。

### Case 3: User Profiles (隨機讀寫)
*   **情境**：使用者資料，通常透過 `user_id` 查詢。
*   **Strategy**：**Hashed Sharding** on `user_id`。
    *   `{ user_id: "hashed" }`
*   **Reason**：User ID 可能是循序產生的（Auto-increment），使用 Hash 可以確保使用者資料均勻散落在 Cluster 中，且查詢時通常是精確匹配（Exact Match），效率極高。