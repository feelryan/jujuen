# 資料庫與搜尋引擎 / Data & Search Engines | Data & Search Engines

## 1. 目標與範圍 | Goal & Scope
- 展示您在處理大規模數據檢索（百萬級商品）與資料建模的能力。
  - Demonstrate your ability to handle large-scale data retrieval (millions of products) and data modeling.
- 比較並證明在不同場景下選擇 SQL（MySQL）、NoSQL（MongoDB）或搜尋引擎（ElasticSearch）的決策邏輯。
  - Compare and justify the decision logic for choosing SQL (MySQL), NoSQL (MongoDB), or search engines (ElasticSearch) in different scenarios.
- 討論效能優化策略，包括索引設計與 Redis 快取機制。
  - Discuss performance optimization strategies, including index design and Redis caching mechanisms.

## 2. 簡短開場稿 | Opening Script

**30-60 Seconds Summary:**
「在資料層面的設計上，我擁有結合關聯式資料庫與搜尋引擎的實戰經驗。在 **USTOSHOP**，我負責為數百萬件商品導入 **ElasticSearch**，實現了支援全文檢索與鄰近查詢的高效搜尋功能。在 **Hiveel**，我專注於 **MySQL** 的正規化設計（EER diagrams）與查詢優化，確保車輛搜尋引擎的後端效能。此外，我也熟悉使用 **Redis** 進行快取以減輕資料庫負載。我習慣根據資料的一致性需求（ACID）與讀寫比例來選擇最適合的技術堆疊。」

"In terms of data layer design, I have practical experience combining relational databases with search engines. At **USTOSHOP**, I implemented **ElasticSearch** for millions of products, enabling high-performance search with full-text and proximity queries. At **Hiveel**, I focused on **MySQL** normalization (EER diagrams) and query optimization to ensure the backend performance of the vehicle search engine. I am also familiar with using **Redis** for caching to reduce database load. I typically choose the tech stack based on data consistency requirements (ACID) and read/write ratios."

## 3. 關鍵故事與成就 | Key Stories & Achievements

### 故事一：ElasticSearch 百萬級商品索引 (USTOSHOP)
**Story 1: ElasticSearch Indexing for Millions of Products (USTOSHOP)**

- **情境 (Situation):** 電商平台擁有數百萬件商品，傳統 SQL `LIKE` 查詢速度過慢且無法處理模糊搜尋。
  - The e-commerce platform hosted millions of products; traditional SQL `LIKE` queries were too slow and couldn't handle fuzzy search.
- **任務 (Task):** 建立一個高效能的搜尋微服務，支援多欄位與全文檢索。
  - Build a high-performance search microservice supporting multi-field and full-text retrieval.
- **行動 (Action):**
  - 使用 **ElasticSearch** 建立倒排索引（Inverted Index），針對標題、描述與屬性進行多欄位索引（Multi-field indexing）。
    - Used **ElasticSearch** to build inverted indexes, implementing multi-field indexing for titles, descriptions, and attributes.
  - 實作鄰近查詢（Proximity Queries）以提升搜尋結果的相關性。
    - Implemented proximity queries to improve the relevance of search results.
  - 透過 Node.js 與 Spring Boot 建構 API 來串接搜尋請求。
    - Built APIs using Node.js and Spring Boot to handle search requests.
- **結果 (Result):** 成功實現秒級回應的搜尋體驗，顯著提升了使用者的商品查找效率。
  - Successfully achieved sub-second response times, significantly improving user efficiency in finding products.

### 故事二：MySQL 優化與資料建模 (Hiveel)
**Story 2: MySQL Optimization & Data Modeling (Hiveel)**

- **情境 (Situation):** 二手車交易平台需要處理複雜的車輛篩選條件，且需確保交易資料的一致性。
  - A used car trading platform needed to handle complex vehicle filtering criteria while ensuring transactional data consistency.
- **任務 (Task):** 設計可靠的資料庫架構並優化後端查詢效能。
  - Design a reliable database schema and optimize backend query performance.
- **行動 (Action):**
  - 使用 **EER Diagrams** 進行關聯式資料庫建模，確保資料正規化。
    - Used **EER Diagrams** for relational database modeling to ensure data normalization.
  - 針對高頻查詢欄位（如車型、年份、價格）建立複合索引（Composite Indexes）。
    - Created composite indexes for high-frequency query fields (e.g., model, year, price).
  - 結合 **MyBatis** 進行 SQL 調優，避免 N+1 查詢問題。
    - Combined **MyBatis** for SQL tuning to avoid N+1 query issues.
- **結果 (Result):** 提升了後端 API 的穩定性與回應速度，並確保了資料完整性。
  - Improved backend API stability and response speed while ensuring data integrity.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

### Q1: 你何時會選擇 MongoDB 而非 MySQL？
**Q1: When would you choose MongoDB over MySQL?**

- **回答角度:** 結構靈活性 vs. 交易一致性。
  - **Angle:** Schema flexibility vs. Transactional consistency.
- **建議回答:**
  - 「如果資料結構高度變動（如醫療影像的非結構化 metadata 或 Audit Logs），且讀寫量大但不需要嚴格的跨表 Transaction，我會選 MongoDB。但如果是訂單或支付系統（如我在 USTOSHOP 的經驗），需要強一致性（ACID），我一定會選 MySQL。」
  - "If the data structure is highly volatile (like unstructured metadata for medical images or Audit Logs) and requires high throughput without strict cross-table transactions, I'd choose MongoDB. However, for order or payment systems (like my experience at USTOSHOP), where strong consistency (ACID) is mandatory, I would definitely choose MySQL."

### Q2: 在 ElasticSearch 中，你是如何處理資料同步的？
**Q2: How did you handle data synchronization in ElasticSearch?**

- **回答角度:** 雙寫（Double Write）vs. 非同步更新（Async Update）。
  - **Angle:** Double Write vs. Async Update.
- **建議回答:**
  - 「我們將 MySQL 視為 Source of Truth。當商品更新時，透過應用層發送事件（或使用 Logstash/CDC 工具）非同步更新 ElasticSearch。雖然會有短暫的最終一致性（Eventual Consistency）延遲，但這對搜尋體驗通常是可接受的。」
  - "We treated MySQL as the Source of Truth. When a product was updated, we triggered an async update to ElasticSearch via the application layer (or tools like Logstash/CDC). While there is a brief latency due to eventual consistency, this is usually acceptable for search UX."

### Q3: 你如何使用 Redis 進行優化？
**Q3: How do you use Redis for optimization?**

- **回答角度:** 快取策略與失效機制。
  - **Angle:** Caching strategy and eviction mechanisms.
- **建議回答:**
  - 「我主要將 Redis 用於快取『讀多寫少』的熱點資料（如首頁推薦商品或使用者 Session）。我會設定 TTL（Time-to-Live）並採用 Cache-Aside 模式：先讀快取，沒有再讀 DB 並回寫快取，以減輕 MySQL 的負載。」
  - "I primarily use Redis to cache 'read-heavy, write-rarely' hot data (like homepage recommendations or user sessions). I set a TTL (Time-to-Live) and use the Cache-Aside pattern: read the cache first; if missing, read the DB and populate the cache, reducing the load on MySQL."

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts

若面試官深入技術細節，請準備好討論以下主題：
If the interviewer digs deeper, be prepared to discuss:

1.  **倒排索引原理 (Inverted Index):**
    - 解釋 ElasticSearch 如何透過 Tokenization 和 Term Index 快速找到文件，對比 SQL 的 B-Tree 索引。
    - Explain how ElasticSearch uses Tokenization and Term Index to find documents quickly, contrasting it with SQL's B-Tree index.
2.  **資料庫正規化 vs. 反正規化 (Normalization vs. Denormalization):**
    - 討論在 MySQL 中正規化以減少冗餘，但在 ElasticSearch 或 MongoDB 中為了讀取效能而進行反正規化（Denormalization）的權衡。
    - Discuss normalizing in MySQL to reduce redundancy versus denormalizing in ElasticSearch or MongoDB for read performance trade-offs.
3.  **分散式系統挑戰 (Distributed Challenges):**
    - 既然有 GCP 經驗，可能會被問到資料庫的 Sharding（分片）或 Replication（複寫）策略，以及如何處理 Split-brain（腦裂）問題。
    - Given your GCP experience, you might be asked about DB Sharding or Replication strategies, and how to handle Split-brain issues.

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **陷阱 (Pitfall):** 把 ElasticSearch 當作主要資料庫使用。
  - Using ElasticSearch as the primary database.
- **糾正 (Correction):** 強調 ES 可能會有資料遺失風險或 Split-brain 問題，應始終保留 SQL/NoSQL 作為 Source of Truth。
  - Emphasize that ES can have data loss risks or split-brain issues; always keep SQL/NoSQL as the Source of Truth.

- **陷阱 (Pitfall):** 忽略「最終一致性」帶來的 UX 問題。
  - Ignoring UX issues caused by "Eventual Consistency".
- **糾正 (Correction):** 承認更新後搜尋結果可能有延遲，並說明如何透過 UI 提示或強制重新整理來緩解。
  - Acknowledge that search results might lag after an update, and explain how to mitigate this via UI cues or forced refreshes.

- **陷阱 (Pitfall):** 過度索引 (Over-indexing)。
  - Over-indexing.
- **糾正 (Correction):** 說明索引雖然加速讀取但會拖慢寫入，應只針對查詢頻率高的欄位建立索引。
  - Explain that while indexes speed up reads, they slow down writes; indexes should only be created for frequently queried fields.

## 7. 收尾與反問 | Closing & Questions for Interviewer

**收尾 (Closing):**
「總結來說，我能夠根據業務需求（如 USTOSHOP 的搜尋速度或 Hiveel 的交易完整性）選擇正確的資料庫工具，並透過 Redis 快取與索引優化來確保系統在高負載下的穩定性。」
"In summary, I can choose the right database tools based on business needs (like search speed at USTOSHOP or transactional integrity at Hiveel) and ensure system stability under high load through Redis caching and index optimization."

**反問 (Questions):**
1. 「貴團隊目前在資料庫層面遇到的最大效能瓶頸是什麼？是讀取還是寫入？」
   - "What is the biggest performance bottleneck your team currently faces at the database layer? Is it read-heavy or write-heavy?"
2. 「針對搜尋功能，你們目前是依賴資料庫的原生查詢，還是已經導入了像 ElasticSearch 這樣的專用引擎？」
   - "For search functionality, do you currently rely on native database queries, or have you implemented a dedicated engine like ElasticSearch?"