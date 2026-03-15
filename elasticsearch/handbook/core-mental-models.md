# 核心概念與心智模型：搜尋引擎 vs 資料庫 / Core Concepts & Mental Models: Search Engine vs. Database

## Mental model｜心智模型

要駕馭 Elasticsearch (ES)，最重要的一步是**「忘掉 RDBMS 的直覺」**。ES 不是傳統資料庫的替代品，而是一個為了「讀取與搜尋」極度優化的特殊引擎。

### 1. The Inverted Index: The "Index" at the Back of a Book
**倒排索引：書本末頁的索引表**

- **RDBMS (B-Tree)**：像是一本電話簿。如果你知道名字（Primary Key），你可以很快找到電話。但如果你要找「所有住在台北的人」，你需要從頭翻到尾 (Full Table Scan)。
- **Elasticsearch (Inverted Index)**：像是一本教科書末尾的「關鍵字索引」。
    - 它列出了所有出現過的詞（Terms），以及這些詞出現在哪幾頁（Document IDs）。
    - 當你搜尋 "Taipei"，ES 直接查表告訴你 Doc 1, Doc 5, Doc 9 有這個詞，完全不需要掃描整本書。

### 2. Immutability & Segments: Write Once, Read Many
**不可變性與分段：寫入即定案**

在 ES 中，**沒有真正的「修改 (Update)」操作**。
- **Lucene Segments**：ES 的底層儲存單元是 Segment。一旦 Segment 被寫入磁碟，它就是**不可變 (Immutable)** 的。
- **How Update Works**：當你執行 Update API 時，ES 實際上是：
    1. 將舊文件標記為 `.del` (邏輯刪除)。
    2. 寫入一份全新的文件到新的 Segment 中。
    3. 搜尋時會過濾掉 `.del` 的文件。
- **Cost**：頻繁的更新會產生大量碎片 (Segments) 和垃圾資料 (Deleted docs)，導致 CPU 瘋狂進行 Segment Merging（合併並物理刪除舊資料）。**ES 討厭頻繁更新單一欄位（如計數器）。**

### 3. Near Real-Time (NRT): The Buffer Gap
**近即時特性：緩衝區的時間差**

- 資料寫入 ES 後，不會立刻進入磁碟上的 Segment，而是先進入 Memory Buffer。
- 預設每 1 秒鐘，ES 會執行一次 `refresh`，將 Buffer 的資料變成一個可被搜尋的 Segment（此時仍在 File System Cache，未 fsync 到磁碟）。
- **心智模型修正**：你寫入成功的當下（收到 200 OK），該資料**不一定**能被立刻搜尋到。這與 RDBMS 的 ACID 交易可見性完全不同。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. CQRS (Command Query Responsibility Segregation)
**讀寫分離架構**
這是最標準的 ES 整合模式。
- **Write Model (Source of Truth)**：使用 MySQL/PostgreSQL 處理交易、強一致性寫入、關聯約束。
- **Read Model (Search Engine)**：使用 Elasticsearch 提供全文檢索、聚合分析、複雜過濾。
- **Sync**：透過 Application code (Dual write) 或 CDC (Change Data Capture, 如 Debezium) 將資料同步到 ES。

### 2. Denormalization (Flattening Data)
**反正規化（資料扁平化）**
ES 不支援 JOIN（雖然有 Nested/Parent-Child，但效能代價高）。
- **Pattern**：在寫入 ES 前，將關聯資料「攤平」。
- **Example**：不要存 `User ID` 然後指望搜尋時去 Join `User Table`。直接把 `User Name`, `Email` 寫入 `Order Document` 中。
- **Trade-off**：資料冗餘（Redundancy）是為了換取搜尋速度。如果 User 改名，你需要更新所有相關的 Order Documents（或接受歷史訂單保留舊名）。

### 3. Bulk Processing
**批次處理**
- 由於 Inverted Index 的構建成本高昂，單筆寫入 (Index Request) 的 Overhead 很大。
- **Best Practice**：永遠使用 `_bulk` API。累積 5MB~15MB 或 1000~5000 筆資料後一次發送。

### 4. Time-Based Indices for Logs/Events
**基於時間的索引分割**
- 對於 Log 或 Event Data（只增不改），按時間切分 Index（如 `logs-2023-10-25`）。
- **Benefit**：過期資料刪除只需 `DELETE /logs-2023-09-01`（瞬間完成，釋放磁碟），而不是在一個大 Index 裡執行昂貴的 `Delete By Query`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Using ES as the Primary Database
**把 ES 當作主要資料庫**
- **Risk**：雖然 ES 可靠性已提升，但面對 Split-brain (腦裂) 或極端狀況下的資料遺失風險仍高於 RDBMS。且 ES 缺乏 Transaction (Rollback) 機制。
- **Rule**：如果這筆資料丟了會導致財務損失或法律問題，請存在 RDBMS，再同步到 ES。

### 2. High Frequency Updates on Counters
**在高頻更新的計數器上使用 ES**
- **Scenario**：用 ES 存文章的 `view_count`，每有人點擊就 Update 一次。
- **Consequence**：產生海量 `.del` 文件，觸發頻繁 Segment Merge，I/O 飆升，拖垮整個 Cluster 的搜尋效能。
- **Solution**：使用 Redis 存計數，每隔一段時間（如 10 分鐘）才同步一次到 ES，或在搜尋時從 Redis 讀取並與 ES 結果合併（Application Side Join）。

### 3. Deep Pagination
**深度分頁**
- **Scenario**：使用者請求第 10,000 頁 (`from: 100000, size: 10`)。
- **Mechanism**：ES 必須在每個 Shard 找出前 100,010 筆資料，匯總到 Coordinator Node 排序後，丟棄前 100,000 筆。這會吃光 Heap Memory。
- **Solution**：限制 `max_result_window` (預設 10,000)。若需匯出大量資料，使用 `search_after` 或 `Scroll API`。

### 4. Mapping Explosion
**Mapping 爆炸**
- **Scenario**：允許使用者自定義欄位，並直接丟入 ES (Dynamic Mapping)。
- **Consequence**：每個不同的 Key 都會產生一個新的 Field Mapping。Cluster State 過大，導致 Master Node 回應變慢甚至 Crash。
- **Fix**：設定 `dynamic: false` 或 `strict`，嚴格控制 Schema。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Do I need Elasticsearch?
**決策流程：我真的需要 ES 嗎？**

- [ ] **資料量級**：資料量是否超過 RDBMS `LIKE %...%` 能負荷的程度（通常 > 百萬級別）？
- [ ] **搜尋需求**：是否需要 Fuzzy Search (模糊搜尋)、Ranking (相關性評分)、Stemming (詞幹分析) 或 Geo-search？
- [ ] **寫入模式**：是否能接受「最終一致性 (Eventual Consistency)」？（寫入後 1 秒才查得到）
- [ ] **更新頻率**：資料是否主要是 Read-heavy 或 Append-only？（如果主要是頻繁 Update，ES 不適合）

### Implementation Checklist
**實作檢核表**

- [ ] **Source of Truth**：確認已有 RDBMS 或 Kafka 作為資料源頭，ES 僅作為 View。
- [ ] **ID Strategy**：是否使用了具有業務意義的 ID (如 UUID 或 DB Primary Key) 作為 ES 的 `_id`？（避免 ES 自動生成 ID，以便於冪等性重試）。
- [ ] **Refresh Interval**：對於寫入量大的 Index，是否將 `refresh_interval` 從預設 `1s` 調大（如 `30s`）以提升寫入吞吐量？
- [ ] **Mapping**：是否已明確定義 Mapping 並且關閉了生產環境的 Dynamic Mapping？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Product Search (電商商品搜尋)

**需求**：使用者搜尋 "iPhone 15"，希望看到相關商品，且價格必須準確。

**Bad Approach (Anti-pattern)**:
- 直接把 ES 當作商品庫。
- 當商家後台改價時，直接 Update ES。
- 庫存扣減時，直接 Update ES。
- **結果**：大促銷時，高併發庫存更新導致 ES 效能低落，搜尋延遲飆高，甚至出現庫存超賣（因為 ES 沒有 Transaction）。

**Good Approach (Best Practice)**:

1.  **Storage**:
    - **MySQL**: 儲存 `products` (id, name, price, stock)。這是 Source of Truth。
    - **Elasticsearch**: 儲存 `products_index` (id, name, description, category, tags)。**注意：不存高頻變動的 `stock`。**

2.  **Indexing Flow**:
    - 商家修改商品描述 -> MySQL Transaction Commit -> 發送 Event 到 Kafka -> Consumer 寫入 ES (`_bulk` upsert)。

3.  **Search Flow (Handling Price/Stock)**:
    - User 搜尋 "iPhone 15"。
    - ES 回傳 Top 20 商品 IDs。
    - Backend 拿著這 20 個 IDs 去 Redis 或 MySQL 查詢最新的「價格」與「庫存狀態」。
    - Backend 組合資料回傳給前端。

**Why this works?**
- 利用 ES 強大的 Inverted Index 處理文字匹配與過濾。
- 避開了 ES 處理高頻更新（庫存/價格）的弱點。
- 確保使用者看到的價格與結帳時一致（因為價格來自 DB/Redis）。