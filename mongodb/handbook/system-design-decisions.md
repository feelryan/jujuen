# 系統設計決策與技術整合 / System Design Decisions & Integration

## Mental model｜心智模型

在系統設計中，MongoDB 不應僅被視為「關聯式資料庫的替代品」或「因為不想寫 SQL 所以用的資料庫」。要正確評估 MongoDB 的適用場景，你需要建立以下的心智模型：

### 1. "Data that is accessed together, stays together" (存取局部性)
在 RDBMS (SQL) 中，我們傾向將資料拆解（正規化）以減少冗餘；在 MongoDB 中，核心哲學是**為了讀取效能而設計 (Design for Read Performance)**。
- **SQL 思維**：資料該如何被「乾淨」地儲存？(Write-optimized / Normalized)
- **MongoDB 思維**：應用程式如何「使用」這些資料？(Read-optimized / Denormalized)
- **決策關鍵**：如果你的 UI 畫面需要一次撈出 User Profile + Recent Orders + Preferences，在 SQL 中你需要 3 個 Table join；在 MongoDB 中，這應該是一個 Document。

### 2. The "Document" as a Flexible Container (文件即容器)
將 Document 視為一個自帶結構的物件（Self-describing object）。它介於 Key-Value Store (Redis) 與 Table (SQL) 之間。
- 它比 SQL 靈活：允許 Polymorphism (多型)，同一 Collection 內的不同 Document 可以有不同欄位（例如電商的「商品屬性」）。
- 它比 Redis 強大：支援 Secondary Indexes 和複雜的 Aggregation Pipeline。

### 3. Polyglot Persistence (混合持久化)
現代架構很少「一庫打天下」。MongoDB 經常扮演「操作型資料儲存 (Operational Datastore)」的角色，位於高併發寫入的前線，而將複雜分析交給 Data Warehouse，搜尋交給 Search Engine。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Product Catalog" Pattern (多樣化屬性處理)
這是 MongoDB 最強勢的戰場。當實體（Entity）具有高度變動或多樣化的屬性時。
- **情境**：電商系統，賣衣服（有尺寸、顏色）也賣筆電（有 CPU、RAM、螢幕解析度）。
- **SQL 痛點**：通常需要 Entity-Attribute-Value (EAV) 模式或大量的 Nullable columns，查詢痛苦且效能差。
- **MongoDB 做法**：利用 Schema-less 特性，將不同屬性存於 `attributes` 子文件中，並建立 Wildcard Index 支援查詢。

### 2. High-Volume Event Logging / IoT (高頻寫入緩衝)
- **情境**：使用者行為 Log、感測器數據、遊戲戰鬥紀錄。
- **實作**：使用 **Time Series Collections** 或 **Bucket Pattern**。
- **整合模式**：MongoDB 作為寫入緩衝區 (Write Buffer)，因為它對 Insert 的吞吐量通常優於傳統 RDBMS（特別是 Sharding 後）。資料過期後可透過 TTL (Time-To-Live) index 自動清除，或歸檔至 S3/Data Lake。

### 3. CQRS Implementation (讀寫分離架構)
- **情境**：系統寫入邏輯複雜（需強交易 ACID，適合 SQL），但讀取需求極高且多變（適合 NoSQL）。
- **實作**：
    1. **Command Side (Write)**: 使用 PostgreSQL 處理核心交易（如訂單狀態流轉）。
    2. **Sync**: 透過 CDC (Change Data Capture) 工具（如 Debezium）或應用層 Event Bus，監聽 SQL 變更。
    3. **Query Side (Read)**: 將資料同步到 MongoDB，並預先 Join 好（Denormalization），供前端 API 快速讀取。

### 4. Search Engine Integration (與 Elasticsearch 整合)
雖然 MongoDB 有 Atlas Search (基於 Lucene)，但若自建架構：
- **模式**：MongoDB 是 Source of Truth (SoT)，Elasticsearch (ES) 是搜尋索引。
- **同步機制**：利用 **MongoDB Change Streams** 監聽 `insert/update/delete` 事件，即時同步至 ES。
- **邊界**：簡單的 `regex` 或 `text search` 用 MongoDB 即可；需要 Fuzzy search、Scoring、Faceting 時才引入 ES。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Replicating RDBMS Schema (把 Mongo 當 SQL 用)
- **現象**：將 SQL 表一對一遷移到 Collection，然後在 Application 層或使用 `$lookup` (Aggregation) 進行大量的 Join。
- **後果**：失去了 Document Model 的讀取優勢，且 `$lookup` 在分散式環境（Sharding）下效能極差。
- **修正**：識別存取模式，將 1:1 或 1:Few 的關係內嵌 (Embed) 到父文件中。

### 2. The "Unbounded Array" Trap (無限增長陣列)
- **現象**：在 User document 中放一個 `logs: []` 陣列，每次有動作就 `$push`。
- **後果**：
    1. 觸發 MongoDB **16MB Document Size Limit**。
    2. 導致頻繁的 Document 移動（如果儲存空間不足），造成寫入效能抖動。
- **修正**：使用 **Subset Pattern** (只存最近 10 筆)，舊資料移至獨立 Collection；或直接使用 Bucket Pattern。

### 3. Overusing Transactions (過度依賴多文件交易)
- **現象**：雖然 MongoDB 4.0+ 支援 Multi-document ACID Transactions，但開發者將其作為預設操作，就像在 SQL 中一樣。
- **後果**：交易會鎖定資源，大幅降低吞吐量，並增加死鎖風險。MongoDB 的原子性 (Atomicity) 是基於 **單一 Document** 的。
- **修正**：重新設計 Schema，讓一次商業操作盡量落在單一 Document 的更新上，僅在跨 Collection 的關鍵資金操作使用 Transaction。

### 4. Using MongoDB for Graph Problems (圖形關係錯用)
- **現象**：試圖在 MongoDB 中實作「朋友的朋友的朋友」這類社交網路查詢。
- **後果**：需要多次 Query 或極度複雜的 Aggregation，效能低落。
- **修正**：這類高度連結的資料應使用 Graph Database (如 Neo4j)。

---

## Checklists & workflows｜檢查清單與流程

在決定是否引入 MongoDB 或如何整合時，請使用此決策樹與檢查清單：

### Decision Matrix: SQL vs. MongoDB

- [ ] **資料結構變動頻率？**
    - 高 (Schema 經常變，不同客戶欄位不同) -> **MongoDB**
    - 低 (結構穩定，如會計帳目) -> **SQL**
- [ ] **資料間的關係？**
    - 階層式 (Hierarchical / Nested) -> **MongoDB**
    - 網狀/高度關聯 (Highly Relational) -> **SQL**
- [ ] **擴展性需求？**
    - 需要水平擴展 (Sharding) 至 TB/PB 級 -> **MongoDB** (原生支援較佳)
    - 垂直擴展為主 -> **SQL**
- [ ] **一致性需求？**
    - 跨多表的強一致性是絕對必要 -> **SQL**
    - 最終一致性 (Eventual Consistency) 可接受，或單一 Document 原子性足夠 -> **MongoDB**

### Integration Workflow (整合流程)

1. **定義 Source of Truth (SoT)**：
   - [ ] 確定哪個資料庫擁有資料的「黃金版本」。通常涉及金流選 SQL，涉及內容/Log 選 Mongo。
2. **規劃同步策略 (若混合使用)**：
   - [ ] 實時性需求？(高：Change Streams / 應用層雙寫；低：ETL 排程)
   - [ ] 失敗重試機制？(Dead Letter Queue)
3. **驗證 16MB 限制**：
   - [ ] 評估所有含有 Array 的 Document，在極端情況下是否會爆掉？
4. **索引策略預演**：
   - [ ] 查詢模式是否包含多欄位過濾？(Compound Index)
   - [ ] 是否需要排序？(索引順序很重要)

---

## Real-world examples｜實戰案例

### Case 1: Content Management System (CMS) / Headless CMS
**情境**：企業需要一個靈活的 CMS 來管理文章、頁面配置和多媒體。
- **挑戰**：每個頁面的 Layout 不同，有的有 Slider，有的有 Video Block，欄位完全動態。
- **設計決策**：
    - 使用 MongoDB 儲存 Page Content。
    - Schema 設計採用 **Polymorphic Pattern**。
    - `content_blocks` 陣列中存放不同類型的物件 (`type: 'video'`, `type: 'text'`)。
- **整合**：前端 (React/Vue) 直接根據 `type` 渲染對應 Component，無需後端做複雜轉換。

### Case 2: Mobile Game User Profile (高併發讀寫)
**情境**：即時戰略遊戲，玩家擁有背包、英雄、任務進度。
**Schema Design (Pseudo-JSON)**:
```json
{
  "_id": "user_123",
  "username": "DragonSlayer",
  "stats": { "level": 50, "xp": 9999 },
  "inventory": [ // 頻繁讀寫，且總是跟著 User 一起被讀取
    { "item_id": "sword_epic", "durability": 100 },
    { "item_id": "potion_hp", "count": 5 }
  ],
  "active_quests": [ ... ]
}
```
- **決策關鍵**：**Data Locality**。玩家登入時，Server 只需要 **1 次讀取** 就能拿到所有需要的資料。若用 SQL，可能需要 Join `users`, `inventory`, `quests`, `stats` 四張表。
- **整合邊界**：雖然 User Profile 在 Mongo，但「好友關係」可能存在 Graph DB 或 Redis Set 中；「排行榜」則由 Redis Sorted Set 處理。

### Case 3: E-commerce Order History (Archiving & Analytics)
**情境**：訂單成立時需強交易 (SQL)，但使用者查詢「歷史訂單」只需唯讀且量大。
- **架構**：
    1. **Order Service (SQL)**: 處理下單、扣款、庫存扣減 (ACID)。
    2. **Sync Worker**: 監聽 SQL Binlog，將完成的訂單轉換為 Document 寫入 MongoDB。
    3. **History Service (MongoDB)**:
       - Document 結構包含該訂單當下的商品快照 (Snapshot)，避免商品改名或改價影響歷史紀錄。
       - 支援靈活的查詢（如：「找出所有買過 '藍色' 商品的訂單」）。
- **優勢**：減輕 Transaction DB 的負載，並提供更靈活的查詢能力給前端。