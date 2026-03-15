# 核心思維與儲存引擎機制 / Core Concepts & Storage Engine Internals

本章節不談 CRUD 語法，而是深入 MongoDB 的「大腦」（Document Model）與「心臟」（WiredTiger 儲存引擎）。理解這些底層機制，是做出正確架構決策的前提。

## Mental model｜心智模型

### 1. Data Locality over Normalization (資料局部性優於正規化)
在關聯式資料庫（RDBMS）中，我們習慣將資料拆解（Normalize）以減少冗餘；但在 MongoDB 中，核心思維是 **"Data that is accessed together should be stored together"（一起被讀取的資料，應該存放在一起）**。
- **RDBMS**: 像是將一張發票撕碎，抬頭存一張表、品項存一張表、金額存一張表。讀取時需要 `JOIN` 拼湊。
- **MongoDB**: 像是將整張發票直接歸檔。讀取時一次 I/O 就能拿回完整資訊。
- **BSON**: 這不僅是 JSON 的二進位格式，它支援更多型別（如 Date, Decimal128, ObjectId），且設計上優化了「掃描」與「跳過」欄位的速度。

### 2. WiredTiger: The Memory-First Engine (記憶體優先引擎)
WiredTiger 是 MongoDB 的預設儲存引擎，它的運作邏輯更像是一個 **帶有持久化機制的記憶體資料庫**。
- **Cache**: WiredTiger 預設使用約 50% 的實體 RAM 作為內部快取。如果你的 **Working Set (熱資料 + 索引)** 超過這個大小，效能會因為大量的 Disk Swap (Eviction) 而斷崖式下跌。
- **MVCC (Multi-Version Concurrency Control)**: 讀寫操作互不阻塞。寫入時，WiredTiger 會在記憶體中創造一個新版本的 document，直到 Checkpoint 發生才寫入 Disk。
- **Journaling vs. Checkpoint**:
  - **Journal (WAL)**: 確保斷電不掉資料（預設 100ms 刷盤一次）。
  - **Checkpoint**: 確保資料結構整齊寫入 Data Files（預設 60s 發生一次）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Document Size Management (文件大小管理)
雖然 BSON 上限是 16MB，但實務上應保持 Document 輕量。
- **最佳實務**: 單一 Document 建議控制在 **數 KB 到 數十 KB** 之間。
- **原因**: MongoDB 讀寫的基本單位是 Document。如果你只需要讀取 User 的 `name`，卻讀取了一個包含 5MB 歷史 Log 的 User Document，會造成巨大的 RAM 與 Network 浪費。

### 2. WiredTiger Compression Strategies (壓縮策略選擇)
WiredTiger 支援多種壓縮演算法，應根據資料特性選擇：
- **Snappy (Default)**: 平衡 CPU 使用率與壓縮比。適合大多數通用場景。
- **Zstd**: 較高的 CPU 消耗，但壓縮比極佳。適合 **日誌 (Logs)、歷史歸檔 (Archival Data)** 或 **寫入頻率低但讀取頻率高** 的場景。
- **None**: 如果資料本身已經是壓縮格式（如 JPEG 圖片、加密字串），請關閉壓縮以節省 CPU。

### 3. Schema Validation (模式驗證)
MongoDB 是 "Flexible Schema" 不是 "No Schema"。在生產環境中，應使用 JSON Schema Validation 來鎖定核心欄位。
- **Pattern**: 在 Collection 層級設定 Validation Rules，確保 `price` 永遠是 `decimal`，`email` 必須存在。這能防止應用程式 Bug 寫入髒資料。

### 4. Handling Durability (持久性設定)
理解 Write Concern 對效能與安全性的權衡。
- **`w: 1` (Default)**: 只要 Primary 節點記憶體確認收到即可。快，但若 Primary 在刷盤前掛掉可能掉資料。
- **`w: "majority", j: true`**: 確保資料寫入 Journal 且同步到多數節點。慢，但保證資料不遺失（金融交易必備）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Kitchen Sink" Document (無底洞文件)
- **現象**: 將所有相關資料無限制地嵌入同一個 Document（例如：將所有使用者的「瀏覽紀錄」塞在 User Document 裡的 Array）。
- **後果**:
  - 觸發 **16MB BSON Limit** 導致寫入失敗。
  - 每次更新 Array（如 `push`）都可能導致 Document 移動（若空間不足），引發嚴重的寫入放大（Write Amplification）。
  - **Unbounded Arrays** 是 MongoDB 最常見的效能殺手。

### 2. Treating MongoDB like SQL (把 Mongo 當 SQL 用)
- **現象**: 過度正規化，將資料拆得極散，然後在應用層或使用 `$lookup` (Aggregation) 進行大量關聯。
- **後果**: `$lookup` 在分散式環境（Sharding）下效能極差，且無法利用 Data Locality 優勢。
- **修正**: 優先考慮 **Embedding (嵌入)**，僅在資料量大或多對多關係時使用 **Referencing (引用)**。

### 3. Ignoring Data Types (忽視資料型別)
- **現象**: 用 `String` 存日期，用 `Double` 存金額。
- **後果**:
  - `String` 日期無法進行範圍查詢與時間聚合。
  - `Double` 會有浮點數精度問題（0.1 + 0.2 != 0.3）。
- **修正**: 金額務必使用 **`Decimal128`**，日期使用 **`ISODate`**。

### 4. Oversized Working Set (過大的工作集)
- **現象**: 查詢模式隨機，導致頻繁存取冷資料，或者索引建立過多導致索引總大於 RAM。
- **後果**: WiredTiger 頻繁進行 Page Eviction（將記憶體頁面換出到磁碟），CPU 飆高且 I/O Wait 暴增。

---

## Checklists & workflows｜檢查清單與流程

在設計 Schema 或進行 Code Review 時，請使用以下清單檢查：

### Schema Design Review Checklist
- [ ] **Cardinality Check (基數檢查)**: 嵌入的 Array 是否有上限？如果是「無限增長」的資料（如 Log, Comments），是否已改為 Reference 模式？
- [ ] **Size Check**: 預估 Document 最大會長到多大？是否遠小於 16MB（建議 < 1MB）？
- [ ] **Read/Write Ratio**: 此 Collection 是讀多寫少（適合 Embedding）還是寫多讀少（適合拆分）？
- [ ] **Data Types**: 金額欄位是否使用了 `Decimal128`？日期是否為 `Date` 物件？
- [ ] **Atomicity**: 需要原子性更新的欄位，是否都在同一個 Document 內？（MongoDB 僅保證單一 Document 的原子性，除非使用 Transaction）。

### Performance Tuning Workflow (WiredTiger)
1. **Check Cache Usage**: 使用 `db.serverStatus().wiredTiger.cache` 查看 `bytes currently in the cache`。如果接近配置上限（預設 RAM 的 50% - 1GB），需考慮擴容或優化索引。
2. **Monitor Eviction**: 觀察 `pages read into cache` 與 `pages written from cache`。如果這兩個數值持續很高，代表 Working Set 超出記憶體。
3. **IOPS Check**: 雲端環境下，確認 Disk IOPS 是否觸頂。WiredTiger 在 Checkpoint 期間會產生大量 I/O。

---

## Real-world examples｜實戰案例

### Scenario A: E-commerce Product Catalog (電商商品目錄)

**Bad Approach (SQL Style):**
建立 `Products`, `ProductAttributes`, `ProductVariants`, `ProductPrices` 四個 Collections，讀取一個商品詳情頁需要 `$lookup` 三次。

**Good Approach (Document Model):**
利用 **Polymorphic Pattern** 與 **Attribute Pattern**。

```json
// One document serves the entire Product Detail Page (PDP)
{
  "_id": "prod_12345",
  "name": "Wireless Headphones",
  "brand": "AudioTech",
  "price": { "amount": 299.99, "currency": "USD" }, // Decimal128 implied
  "specs": [ // Attribute Pattern for easy indexing
    { "k": "color", "v": "black" },
    { "k": "battery_life", "v": "20h" },
    { "k": "bluetooth", "v": "5.0" }
  ],
  "variants": [ // Embedding manageable variants
    { "sku": "WH-BLK", "stock": 50 },
    { "sku": "WH-WHT", "stock": 12 }
  ]
}
```
*優勢：一次 `findOne` 讀取完畢，WiredTiger 快取效率極高。*

### Scenario B: High-Volume Sensor Data (IoT 高頻寫入)

**Problem:** 每一秒鐘有 10,000 個感測器寫入數據。若每個數據都存成一個 Document，索引會過大，且壓縮率低。

**Solution (Bucket Pattern):**
將一分鐘內的數據「桶裝」到一個 Document 中。

```json
{
  "sensor_id": "s_999",
  "start_time": ISODate("2023-10-27T10:00:00Z"),
  "end_time": ISODate("2023-10-27T10:01:00Z"),
  "measurements": [
    { "ts": 1000, "temp": 23.5 },
    { "ts": 2000, "temp": 23.6 },
    // ... up to 60 entries
    { "ts": 60000, "temp": 24.0 }
  ],
  "sum_temp": 1415.2, // Pre-aggregated data
  "count": 60
}
```
*優勢：大幅減少 Index 數量（從 60 個 entry 變成 1 個 entry），提升 WiredTiger 壓縮效率（相似數據在一起），並利於歷史數據歸檔。*