# 資料持久化策略與資料庫選型 / Data Persistence Strategy & Database Selection

## Mental model｜心智模型

在 AWS 雲端環境中設計資料持久層時，請拋棄「一個資料庫打天下」(One Size Fits All) 的舊思維。現代雲端架構的核心心智模型是 **Polyglot Persistence（多語言持久化）** 與 **Access Pattern Driven Design（存取模式驅動設計）**。

### 1. 存取模式優先 (Access Patterns First)
不要先設計 Schema（資料表結構），而是先設計 Query（查詢方式）。
- **RDBMS (RDS/Aurora)**：適合「查詢模式不確定」或「需要複雜關聯與強一致性 (ACID)」的場景。你付出的代價是擴展性的天花板與維運成本。
- **NoSQL (DynamoDB)**：適合「查詢模式已知」且「需要極致擴展性」的場景。你付出的代價是設計靈活度的降低（Schema 修改困難）。

### 2. 資料溫度分層 (Data Temperature Tiering)
將資料視為有「溫度」的資產，而非靜態檔案。
- **Hot Data**：毫秒級存取，成本最高 (e.g., ElastiCache, DynamoDB DAX)。
- **Warm Data**：頻繁讀寫，標準成本 (e.g., RDS, DynamoDB Standard, S3 Standard)。
- **Cold Data**：極少存取，主要用於歸檔或合規，成本極低 (e.g., S3 Glacier Deep Archive)。

### 3. 受管服務光譜 (The Managed Service Spectrum)
從 **EC2 自建 DB** (IaaS) 到 **RDS** (PaaS) 再到 **Aurora/DynamoDB** (Serverless/Cloud-Native)。越往右側移動，你管理的基礎設施越少，但對 AWS 特定機制的依賴越深。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. SQL 選型：Amazon Aurora 作為首選
除非你有特殊的 Oracle/SQL Server legacy 需求，否則 **Amazon Aurora** (PostgreSQL/MySQL compatible) 通常是比標準 RDS 更好的選擇。
- **Storage Auto-scaling**：不需要預先配置硬碟大小，自動增長。
- **Aurora Serverless v2**：針對流量波動劇烈（如測試環境或日間/夜間流量差異大）的應用，可實現毫秒級垂直擴展。
- **Read Replicas**：利用 Reader Endpoint 分流讀取流量，減輕 Writer 負擔。

### 2. NoSQL 實戰：DynamoDB 的關鍵決策
- **On-Demand vs. Provisioned**：
  - 新專案或流量不可預測：選 **On-Demand**。
  - 流量穩定且可預測：選 **Provisioned + Auto Scaling**（成本較低）。
- **TTL (Time To Live)**：善用 TTL 自動刪除過期資料（如 Session、暫存 Log），這是免費的「垃圾回收」機制。

### 3. S3 儲存分層策略 (Storage Classes)
不要手動撰寫複雜的 Lifecycle Rules 來計算何時轉移到 Glacier，除非你有非常明確的合規要求。
- **S3 Intelligent-Tiering**：這是目前的最佳實踐。它會自動監控存取模式，將不常存取的物件移至較低成本層級，且**沒有取回費用 (Retrieval Fee)**。這能避免因誤判導致的高額取回成本。

### 4. 資料庫代理 (RDS Proxy)
在 Serverless 架構 (Lambda) 中連接 RDS 時，務必使用 **RDS Proxy**。
- **Connection Pooling**：Lambda 的高併發會瞬間耗盡資料庫連線數 (Max Connections)，Proxy 能有效緩衝並重複利用連線。
- **Failover Efficiency**：Proxy 能將 Failover 時間從數十秒縮短至數秒。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. DynamoDB 的關聯式思維 (Relational Mindset in DynamoDB)
- **Anti-pattern**：在 DynamoDB 中設計多個 Table 並試圖在 Application Code 中進行 JOIN。
- **Consequence**：讀取延遲高，消耗大量 RCU (Read Capacity Units)，成本失控。
- **Correction**：使用 **Single Table Design** 或適當的 Denormalization（反正規化），將常一起讀取的資料放在同一個 Item 或 Partition 中。

### 2. 濫用 `Scan` 操作
- **Anti-pattern**：在 DynamoDB 使用 `Scan` 來尋找特定資料，或者在 SQL 中對非索引欄位進行全表掃描。
- **Consequence**：隨著資料量增長，效能呈線性下降，且 DynamoDB 成本會暴增。
- **Correction**：DynamoDB 必須依賴 `Query` (基於 Partition Key + Sort Key)；若查詢模式改變，應建立 **GSI (Global Secondary Index)**。

### 3. S3 作為高頻資料庫
- **Anti-pattern**：將 S3 當作檔案系統頻繁覆寫同一檔案（例如 log appending）。
- **Consequence**：S3 是 Object Storage，每次修改都是「整檔上傳」，延遲高且 PUT 請求費用驚人。
- **Correction**：使用 Kinesis Firehose 緩衝後批次寫入 S3，或使用 CloudWatch Logs。

### 4. 忽視資料一致性模型 (Ignoring Consistency Models)
- **Pitfall**：假設 Read Replica 或 DynamoDB 預設讀取是即時一致的。
- **Reality**：
  - RDS Read Replica 是 **Eventual Consistency (最終一致性)**，可能有毫秒到秒級延遲。
  - DynamoDB 預設也是 Eventual Consistent Read（成本是 Strong Consistent 的一半）。
- **Correction**：在關鍵交易路徑（如扣款後查詢餘額），必須強制使用 Writer Endpoint 或 DynamoDB 的 `ConsistentRead: true`。

---

## Checklists & workflows｜檢查清單與流程

### 決策樹：資料庫選型 (Selection Decision Tree)

1. **資料結構是否高度結構化且關聯複雜？**
   - [Yes] -> 需要 ACID 交易嗎？
     - [Yes] -> **Amazon Aurora / RDS**
     - [No] -> 考慮 **DynamoDB** (透過 Single Table Design)
   - [No] -> 資料是 JSON 文件嗎？
     - [Yes] -> **Amazon DocumentDB** 或 **DynamoDB**
     - [No] -> 是 Key-Value 簡單存取嗎？ -> **DynamoDB**

2. **資料量與擴展性需求？**
   - 資料量 > 10 TB 且需要水平無限擴展？ -> **DynamoDB** (or Cassandra on EC2)
   - 流量是否會有季節性暴衝 (Spiky)？ -> **Aurora Serverless** 或 **DynamoDB On-Demand**

3. **資料是否為二進位大型物件 (Blob/File)？**
   - [Yes] -> **Amazon S3** (metadata 可存於 DynamoDB/RDS)

### 上線前檢查清單 (Production Readiness Checklist)

- [ ] **備份策略**：RDS/Aurora 是否開啟 Automated Backups？DynamoDB 是否開啟 PITR (Point-in-Time Recovery)？
- [ ] **高可用性 (HA)**：RDS 是否開啟 **Multi-AZ**？(生產環境必備)
- [ ] **安全性**：
  - [ ] 是否啟用 **Encryption at Rest** (KMS)？
  - [ ] 是否強制使用 SSL/TLS 連線？
  - [ ] 應用程式是否透過 **IAM Role** 存取 (而非硬編碼 Access Keys)？
- [ ] **監控**：
  - [ ] 是否設定 CloudWatch Alarm 監控 `CPUUtilization`, `FreeStorageSpace`, 或 DynamoDB `ThrottledRequests`？
- [ ] **成本**：
  - [ ] S3 Bucket 是否啟用了 **Intelligent-Tiering** 或適當的 Lifecycle Policy？
  - [ ] 非生產環境的 RDS 是否設定了下班時間自動關機 (Instance Scheduler)？

---

## Real-world examples｜實戰案例

### 案例 1：電商訂單系統 (Hybrid Approach)
**情境**：需要處理高併發下單，確保庫存準確，並保留歷史訂單供查詢。

- **Transactional DB (Hot)**: 使用 **Amazon Aurora (PostgreSQL)**。
  - 處理訂單建立、庫存扣減（ACID 交易）。
  - 使用 Writer Endpoint 寫入，Reader Endpoint 供後台報表查詢。
- **History Archive (Cold)**: 使用 **S3**。
  - 訂單完成 1 年後，將資料匯出為 Parquet 格式存入 S3。
  - 使用 **Amazon Athena** 直接對 S3 數據進行歷史分析（無需將資料倒回 DB）。
- **Session Cart (Ephemeral)**: 使用 **DynamoDB** 或 **ElastiCache (Redis)**。
  - 儲存購物車暫存資料，設定 TTL 為 7 天，自動清除未結帳的廢棄購物車。

### 案例 2：IoT 設備數據收集 (Write-Heavy)
**情境**：數百萬個感測器每分鐘上傳數據，寫入量極大，讀取通常是特定時間範圍。

- **Ingestion**: IoT Core -> Kinesis Data Firehose。
- **Storage**:
  - **Raw Data**: Firehose 直接批次寫入 **S3** (依 `YYYY/MM/DD/HH` 分區)。
  - **Hot Query**: 同時寫入 **DynamoDB** (Partition Key: `DeviceID`, Sort Key: `Timestamp`) 供即時儀表板查詢最新狀態。
- **Cost Optimization**: DynamoDB 設定 TTL 為 30 天（只保留熱數據），S3 設定 Lifecycle Policy 在 90 天後轉入 Glacier Deep Archive。

### 案例 3：Serverless API 後端
**情境**：使用 API Gateway + Lambda 建構的 REST API。

- **Anti-pattern**: Lambda 直接連線 RDS MySQL。
  - *結果*：行銷活動導致流量暴衝，Lambda 實體暴增至 1000 個，耗盡 RDS 的 `max_connections`，導致資料庫拒絕服務。
- **Solution**: 引入 **RDS Proxy**。
  - Lambda 連線至 Proxy Endpoint。
  - Proxy 維護與 RDS 的長連線池 (Connection Pool)。
  - 即使 Lambda 擴展至數千個，對 DB 的實際連線數仍保持在安全範圍內。