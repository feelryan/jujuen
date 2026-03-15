# 資料儲存與資料庫選型指南 / Data Storage & Database Selection Guide

本章節旨在協助工程師穿越 GCP 繁雜的資料庫服務迷霧，根據 CAP 定理（一致性、可用性、分區容錯性）與實際業務需求（讀寫量級、資料結構、全球化部署），做出正確的架構決策。

This chapter guides engineers through the maze of GCP database services, helping you make architectural decisions based on the CAP theorem and actual business requirements (throughput, data structure, global deployment).

---

## Mental Model｜心智模型

在 GCP 上選擇資料庫時，不要只看「我熟悉什麼」，而要看「資料的形狀」與「存取的規模」。請建立以下三個維度的座標系：

When selecting a database on GCP, don't just stick to "what I know." Look at the "shape of the data" and the "scale of access." Establish a coordinate system with these three dimensions:

### 1. 關聯式 vs. 非關聯式 (Relational vs. Non-Relational)
- **SQL (Structured):** 強一致性 (Strong Consistency)、複雜關聯查詢 (Joins)、Schema 固定。
  - *代表服務：* **Cloud SQL**, **Cloud Spanner**.
- **NoSQL (Semi/Unstructured):** 高擴展性 (Scalability)、Schema 靈活、通常為最終一致性 (Eventual Consistency) 或特定條件下的強一致性。
  - *代表服務：* **Firestore**, **Cloud Bigtable**.

### 2. 規模與分佈 (Scale & Distribution)
- **Regional (單一區域):** 適合傳統應用，資料量在 TB 級別以下。
  - *Default:* **Cloud SQL**.
- **Global / Horizontal Scale (全球/水平擴展):** 需要跨區域強一致性，或資料量達到 PB 級別，吞吐量極高。
  - *The "Magic":* **Cloud Spanner** (全球強一致性 SQL).
  - *The "Firehose":* **Cloud Bigtable** (高吞吐寫入 NoSQL).

### 3. CAP 定理在 GCP 的實踐 (CAP in Practice)
- **Cloud SQL:** **CA** (單機/HA) 或 **CP** (發生分區時寫入不可用)。傳統 Master-Slave 架構。
- **Cloud Spanner:** 透過 Google 的 **TrueTime API** (原子鐘)，在實務上打破了 CAP 的限制，同時提供全球級別的 **CP + HA** (外部看起來像 CA)。這是 GCP 的獨門絕技。
- **Cloud Bigtable:** **CP** (著重一致性與分區容錯)，但在單一 Cluster 內提供極高可用性。
- **Firestore:** 預設 **CP** (強一致性)，但在多區域模式下提供極高的可用性保證。

---

## Patterns & Best Practices｜常見模式與最佳實務

### 1. Cloud SQL：適用於通用型應用 (General Purpose)
- **Pattern:** **Auth Proxy Sidecar**.
  - 在 GKE 或 Cloud Run 中，始終使用 Cloud SQL Auth Proxy 連線，避免處理 SSL 憑證與 IP 白名單的痛苦。
- **Best Practice:** 使用 **Private Service Access (Private IP)**，避免資料庫暴露在公網。
- **Best Practice:** 讀寫分離。對於報表類查詢，務必導向 Read Replica，保留 Primary instance 給交易寫入。

### 2. Cloud Spanner：適用於金融級全球應用 (Global Financial Grade)
- **Pattern:** **Interleaved Tables (交錯表)**.
  - 定義 Parent-Child 資料表關係（例如 `Users` -> `Orders`），讓相關資料實體儲存在同一個 Split (節點) 上，大幅提升 Join 效能。
- **Best Practice:** **UUID v4 as Primary Key**.
  - 絕對不要使用連續整數（Sequential ID）或時間戳記作為 Primary Key，這會導致 "Hotspotting"（熱點問題），所有寫入集中在單一節點，導致效能崩潰。

### 3. Firestore：適用於行動/Web 後端與快速開發 (Mobile/Web Backend)
- **Pattern:** **Denormalization (反正規化)**.
  - 為了讀取效能，寧可重複儲存資料。例如在 `Order` document 中直接存一份 `User` 的 snapshot，而不是每次都去讀取 `User` document。
- **Pattern:** **Subcollections**.
  - 利用 Subcollections 隨著 Parent document 自動擴展，避免單一 document 大小超過 1MB 限制。

### 4. Cloud Bigtable：適用於高吞吐時間序列/廣告數據 (High Throughput/IoT)
- **Pattern:** **Tall and Narrow Tables**.
  - 設計極少的 Column Families，但在 Row Key 上做文章。
- **Best Practice:** **Row Key Design**.
  - Row Key 是 Bigtable 效能的靈魂。常見設計為 `[Reverse Timestamp]#[Device ID]` 以確保最新的資料最快被讀取，同時分散寫入壓力。

---

## Anti-patterns & Pitfalls｜反模式與踩雷點

### ❌ 1. 把 Cloud SQL 當作 Oracle RAC 用
- **Anti-pattern:** 期待 Cloud SQL 能像 Oracle RAC 一樣提供多寫入節點 (Multi-Master)。
- **Reality:** Cloud SQL 是單點寫入 (Single Writer)。如果需要水平擴展寫入 (Scale-out Writes)，請遷移至 **Cloud Spanner**。

### ❌ 2. 在 Spanner 中使用單調遞增主鍵 (Monotonically Increasing Keys)
- **Anti-pattern:** 使用 `AUTO_INCREMENT` 或當前時間戳作為 PK。
- **Consequence:** 這是 Spanner 的頭號殺手。會導致所有寫入流量打在同一個 Split 上，系統無法水平擴展。
- **Fix:** 使用 UUID 或對 Key 進行 Bit-reverse。

### ❌ 3. 把 Bigtable 當作關聯式資料庫
- **Anti-pattern:** 嘗試在 Bigtable 上執行複雜的 SQL Join 或二級索引查詢。
- **Reality:** Bigtable 是一個 Key-Value store。如果你需要複雜查詢，請使用 BigQuery (分析) 或 Spanner (交易)。

### ❌ 4. Firestore 的索引爆炸 (Index Explosion)
- **Anti-pattern:** 對所有欄位都開啟自動索引，且頻繁寫入。
- **Consequence:** Firestore 的收費包含「索引寫入次數」。過多的索引會導致寫入成本暴增，且可能觸發單一 Document 的每秒寫入限制。
- **Fix:** 使用 `Exemptions` 排除不需要查詢的欄位索引。

---

## Checklists & Workflows｜檢查清單與流程

使用此決策樹來選擇正確的儲存服務：

Use this decision tree to select the right storage service:

### 選型決策清單 (Selection Checklist)

- [ ] **Q1: 資料是否高度結構化 (Structured) 且需要 ACID 交易？**
  - [ ] **Yes:** 進入 Q2。
  - [ ] **No:** 進入 Q3。

- [ ] **Q2: (SQL Path) 資料量是否 > 10TB 或需要全球水平擴展寫入？**
  - [ ] **Yes:** 選擇 **Cloud Spanner**。
    - *Check:* 預算是否充足？(Spanner 成本較高)。
    - *Check:* Schema 設計是否避免了熱點？
  - [ ] **No:** 選擇 **Cloud SQL** (PostgreSQL/MySQL)。
    - *Check:* 是否需要 HA？
    - *Check:* 是否設定了 Private IP？

- [ ] **Q3: (NoSQL Path) 資料是否為關聯性低的寬表 (Wide-column) 或時間序列，且寫入量極大 (> 10k QPS)？**
  - [ ] **Yes:** 選擇 **Cloud Bigtable**。
    - *Check:* 應用程式是否能接受不支援 ACID 交易？
    - *Check:* Row Key 設計是否經過驗證？
  - [ ] **No:** 進入 Q4。

- [ ] **Q4: (Document Path) 是否為行動/Web App 後端，需要即時同步 (Real-time updates) 與離線支援？**
  - [ ] **Yes:** 選擇 **Firestore**。
    - *Check:* 查詢模式是否符合 Firestore 的限制？
  - [ ] **No:** 考慮 **Cloud Storage** (如果是檔案/Blob) 或 **BigQuery** (如果是純分析倉儲)。

---

## Real-world Examples｜實戰案例

### Scenario A: 全球多人線上遊戲 (Global MMO Game)
- **需求:** 全球玩家資料同步、極高寫入頻率、低延遲、道具交易不可出錯。
- **架構:**
  - **Player Inventory & Currency:** 使用 **Cloud Spanner**。利用其全球強一致性確保玩家在跨區伺服器移動時，金幣與道具不會消失或複製。
  - **Game Telemetry/Logs:** 使用 **Cloud Bigtable**。每秒寫入數百萬條玩家行為日誌，供後續分析。
  - **Static Assets:** 使用 **Cloud Storage** 搭配 Cloud CDN。

### Scenario B: 電商平台 (E-commerce Platform)
- **需求:** 促銷期間流量暴衝、訂單不能掉、商品目錄讀取量大。
- **架構:**
  - **Product Catalog:** 使用 **Firestore**。利用其高併發讀取能力與彈性 Schema (不同商品屬性不同)。
  - **Order Management:** 使用 **Cloud SQL (PostgreSQL)**。傳統且穩定的交易處理，配合 Read Replica 處理後台報表查詢。
  - **Recommendation Engine:** 將 Cloud SQL 與 Firestore 資料匯入 **BigQuery** 進行分析，計算出推薦清單後寫回 Firestore 供前端快速讀取。

### Scenario C: 物聯網感測器平台 (IoT Sensor Platform)
- **需求:** 數百萬個感測器每秒回報溫度/濕度，需要保留歷史數據。
- **架構:**
  - **Raw Data Ingestion:** 使用 **Cloud Pub/Sub** 緩衝流量 -> Dataflow -> **Cloud Bigtable**。
  - **Row Key Design:** `[Region_Code]#[Reverse_Timestamp]#[Sensor_ID]`。這樣設計可以讓最新的資料排在一起方便查詢，同時利用 Region Code 分散寫入壓力。
  - **Dashboard:** 使用 BigQuery 讀取 Bigtable 的資料 (透過 BigQuery Bigtable federation) 進行聚合分析。