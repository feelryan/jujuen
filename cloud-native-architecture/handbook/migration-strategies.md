# 遺留系統遷移策略：絞殺榕模式 / Legacy Migration Strategies: The Strangler Fig Pattern

## Mental model｜心智模型

在處理遺留系統（Legacy System）遷移時，最大的迷思是將其視為一次性的「搬家工程」（Big Bang Migration）。在雲原生架構的語境下，我們應將其視為一種**「有機的代謝過程」**。

### 1. 絞殺榕隱喻 (The Strangler Fig Metaphor)
想像一棵巨大的古樹（單體架構 Monolith），我們不是要將它連根拔起，而是在它周圍種下新的藤蔓（微服務 Microservices）。
- **共生期 (Symbiosis)**：新舊系統同時運行，使用者無感。
- **攔截 (Interception)**：所有的請求必須經過一個統一的「外觀層」（Facade），由它決定流量去往舊樹還是新藤。
- **取代 (Replacement)**：隨著新功能完善，流量逐漸導向新系統。
- **枯萎 (Wither)**：當所有功能都被遷移，舊系統自然停止運作並被移除。

### 2. 資產與負債的轉換 (Asset vs. Liability)
- **Monolith as an Asset**：在遷移初期，單體應用是你的「金礦」，因為它包含了業務邏輯的 Truth 和現有的使用者流量。
- **Monolith as a Liability**：隨著遷移進行，未遷移的單體代碼變成技術債。
- **關鍵心法**：不要為了技術而遷移。遷移的順序應基於 **「變更頻率」 (Rate of Change)** 與 **「業務價值」 (Business Value)**。最常需要修改且價值最高的功能，最優先被絞殺（遷移）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 建立外觀攔截層 (The Facade Interface)
這是實施 Strangler Fig 的先決條件。你必須在 Client 與 Monolith 之間插入一個 Proxy。
- **API Gateway / Reverse Proxy**：使用 Nginx, Kong, Traefik 或 AWS API Gateway。
- **實作方式**：初期將所有流量透傳 (Pass-through) 給 Monolith，接著透過路由規則 (Routing Rules) 逐個 Endpoint 切換到新服務。

### 2. 資料庫遷移策略 (Database Migration Strategies)
代碼遷移容易，資料遷移才是地獄。
- **Shared Database (過渡期)**：新服務暫時連線到舊資料庫。這是反模式，但在遷移初期為了速度可暫時容忍，需設定嚴格的 Deadline 移除。
- **Dual Write (雙寫)**：應用層同時寫入舊 DB 與新 DB。缺點是應用邏輯複雜，容易有資料不一致。
- **Change Data Capture (CDC)**：最佳解。利用 Debezium 等工具監聽舊 DB 的 Binlog，即時同步資料到新 DB。新服務讀取新 DB，寫入操作則視階段而定。

### 3. 影子流量與金絲雀發布 (Shadow Traffic & Canary Release)
不要直接切換 100% 流量。
- **Shadowing**：複製真實流量發送到新服務，但不回傳結果給使用者。用來驗證新服務的效能與正確性（比較新舊回應是否一致）。
- **Canary**：先切換 1% -> 5% -> 20% 的流量，觀察 Error Rate 與 Latency。

### 4. 領域驅動設計 (DDD) 的邊界劃分
- 不要以「技術層」遷移（如先切換 UI，再切換 DB），要以「業務領域 (Bounded Context)」遷移。
- 例如：先遷移「庫存服務」，包含其 API、邏輯與資料庫。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分散式單體 (The Distributed Monolith)
- **症狀**：你拆分了服務，但它們共享同一個資料庫 schema，或者服務間有極度緊密的同步呼叫 (Synchronous Coupling)。
- **後果**：部署新服務仍需停機維護 DB，網路延遲導致效能比單體還差。

### 2. 永不結束的遷移 (The Never-Ending Migration)
- **症狀**：完成了 80% 有趣或高價值的功能，剩下 20% 難搞的邊角料（Reporting, Admin Legacy）沒人想動。
- **後果**：維運成本倍增（同時維護兩套堆疊），Strangler Fig 變成了寄生蟲，吸乾團隊資源。

### 3. 忽視事務一致性 (Ignoring Transactional Consistency)
- **症狀**：在單體中依賴 ACID Transaction 的操作，被拆分到兩個服務中，卻沒有實作 Saga Pattern 或最終一致性機制。
- **後果**：資料損壞，訂單建立了但庫存沒扣。

### 4. 一次性重寫 (The Big Bang Rewrite)
- **症狀**：團隊決定「暫停新功能開發，閉關六個月重寫系統」。
- **後果**：幾乎總是失敗。市場需求會變，六個月後的新系統上線即過時，且充滿未經測試的 Bug。

---

## Checklists & workflows｜檢查清單與流程

### Decision Framework: Should we strangle this?
- [ ] 該模組是否具有高變更頻率？(High Churn Rate)
- [ ] 該模組是否有效能瓶頸，且單體架構無法單獨擴展？
- [ ] 我們是否清楚該模組的資料邊界 (Data Ownership)？

### Migration Workflow (Step-by-Step)

#### Phase 1: Preparation (準備)
- [ ] **Setup Facade**: 部署 API Gateway/Proxy，確認所有流量都經過此處。
- [ ] **Identify Seams**: 透過靜態代碼分析或依賴圖，找出單體中耦合度最低的邊界（Seams）。
- [ ] **Baseline Metrics**: 記錄舊模組的 Response Time, Error Rate, Throughput。

#### Phase 2: Implementation (實作)
- [ ] **Build New Service**: 使用雲原生技術堆疊 (Containers/K8s/Serverless) 建立新服務。
- [ ] **Backfill Data**: 遷移歷史資料到新服務的資料庫。
- [ ] **Sync Mechanism**: 建立 CDC 或同步機制，確保新舊資料庫同步。

#### Phase 3: Cutover (切換)
- [ ] **Deploy & Shadow**: 部署新服務，開啟影子流量 (Shadow Traffic) 進行比對驗證。
- [ ] **Canary Release**: 在 Gateway 層調整路由權重，引入 1% 真實流量。
- [ ] **Monitor**: 觀察 Log 與 Metrics，若有異常立即 rollback (只需改路由設定)。
- [ ] **Full Switch**: 逐步增加至 100% 流量。

#### Phase 4: Cleanup (清理)
- [ ] **Decommission**: 移除單體中對應的舊代碼（Dead Code Elimination）。
- [ ] **Archive Data**: 備份並移除舊資料庫中的相關 Table。

---

## Real-world examples｜實戰案例

### 案例：電子商務系統的「使用者評論」模組遷移

**背景**：
一個基於 Java/Tomcat 的龐大單體電商系統。行銷團隊希望增加「評論附圖/影片」功能，但單體架構難以擴展儲存與處理多媒體，且部署風險高。

**遷移架構設計**：

1.  **Facade Layer (Nginx)**:
    配置 Nginx 作為反向代理。
    ```nginx
    # nginx.conf snippet
    upstream legacy_monolith { server 10.0.1.10:8080; }
    upstream new_review_service { server 10.0.2.20:3000; }

    server {
        listen 80;
        
        # 預設流量走舊單體
        location / {
            proxy_pass http://legacy_monolith;
        }

        # 攔截評論 API，導向新服務 (Golang + S3)
        location /api/v1/reviews {
            # Canary logic can be implemented here or via Ingress Controller
            proxy_pass http://new_review_service; 
        }
    }
    ```

2.  **Data Strategy (CDC)**:
    - **Old DB**: MySQL (Monolith)
    - **New DB**: MongoDB (Review Service, for flexible schema)
    - **Sync**: 使用 Debezium 監聽 MySQL 的 `reviews` table，將變更推送到 Kafka，新服務消費 Kafka 訊息寫入 MongoDB。

3.  **Execution**:
    - **Day 1**: 新的 Review Service 上線，只處理 `GET /reviews` (讀取)。寫入操作 (`POST`) 仍走單體，透過 CDC 同步到 MongoDB。
    - **Day 14**: 驗證讀取無誤。
    - **Day 15**: 切換 `POST /reviews` 到新服務。停止 CDC 同步（或反向同步以防 Rollback）。
    - **Day 30**: 移除單體中的 Review 相關 Java Class 與 JSP 頁面。

**結果**：
- 評論服務獨立擴展，不影響結帳流程。
- 新功能（圖片上傳）僅需更新新服務，部署時間從 1 小時縮短為 5 分鐘。