# 常見反模式與架構陷阱 / Common Anti-patterns & Architectural Pitfalls

微服務架構並非銀彈，若在錯誤的邊界劃分或通訊模式下實作，往往會產生比單體架構（Monolith）更難維護的「分散式災難」。本章節將揭露那些披著微服務外衣的架構陷阱，並提供修正路線。

---

## Mental model｜心智模型

在探討反模式之前，我們必須建立一個核心觀念：**「物理上的分離不等於邏輯上的解耦」（Physical separation $\neq$ Logical decoupling）。**

許多團隊誤以為將程式碼部署到不同的 Docker 容器就是微服務，這是最大的誤區。請運用以下心智模型來審視架構：

1.  **耦合成本槓桿（Coupling Cost Leverage）**：
    *   在單體架構中，模組間的耦合（Coupling）成本較低（Function call 很快，Refactor 容易）。
    *   在微服務中，耦合成本會被**網路延遲**、**分散式交易**與**部署協調**放大 10 倍以上。
    *   **核心思維**：微服務的本質是用「維運的複雜度」來交換「開發的敏捷性」。如果你得到了維運的痛苦，卻沒換來獨立部署的敏捷，那你極有可能陷入了反模式。

2.  **服務自主性光譜（Autonomy Spectrum）**：
    *   一個健康的微服務應該像一個「獨立的小型新創公司」，擁有自己的資料庫、邏輯與對外接口。
    *   反模式通常發生在服務變成了「部門裡的螺絲釘」，沒有其他服務的指令或資料就無法運作。

---

## Patterns & best practices｜常見模式與最佳實務

為了對抗反模式，以下是業界驗證過的「解毒劑」模式：

### 1. Database-per-Service (服務獨有資料庫)
*   **對抗**：Shared Database (共享資料庫)。
*   **實作**：每個微服務必須擁有自己的 Private Schema 或 Database 實例。其他服務若需存取資料，只能透過 API 或訂閱事件（Event）。
*   **Trade-off**：雖然解決了耦合，但帶來了跨服務查詢與資料一致性的挑戰（需引入 Saga Pattern 或 CQRS）。

### 2. Backend for Frontend (BFF) / API Gateway
*   **對抗**：Chatty I/O (過度頻繁的通訊) 與洩漏內部細節。
*   **實作**：針對不同的客戶端（Web, Mobile, IoT）建立專屬的聚合層，一次 Request 取回所有資料，避免客戶端對多個微服務發起「瀑布式呼叫」。

### 3. Asynchronous Communication by Default (預設非同步)
*   **對抗**：Distributed Monolith (分散式單體) 與 Temporal Coupling (時間耦合)。
*   **實作**：盡量使用 Message Broker (如 Kafka, RabbitMQ) 進行服務間溝通。只有在需要即時回應的查詢（Query）時才使用 REST/gRPC。

### 4. Service Template / Chassis (服務底座)
*   **對抗**：Snowflake Services (雪花服務 - 每個服務長得都不一樣)。
*   **實作**：建立標準化的 Boilerplate，統一處理 Logging, Metrics, Tracing, Security 與 Error Handling，避免每個微服務的維運標準不一。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

這是本章節的核心，請檢視你的系統是否出現以下症狀：

### 1. The Distributed Monolith (分散式單體)
這是最致命且最常見的反模式。
*   **症狀**：
    *   **Lock-step Deployment**：為了部署服務 A 的新功能，必須同時部署服務 B 和 C。
    *   **High Latency**：一個前端請求在後端觸發了 10 個以上的同步 RPC/HTTP 呼叫。
    *   **Cascading Failures**：服務 C 掛了，導致服務 B 報錯，最後服務 A 也無法運作。
*   **根本原因**：服務邊界劃分錯誤（高內聚低耦合原則失效），或者過度依賴同步通訊。
*   **修正**：重新劃分 Bounded Context，改用 Event-Driven Architecture 解除依賴。

### 2. The Shared Database (共享資料庫)
*   **症狀**：多個微服務連接到同一個資料庫，甚至 Join 對方的 Table。
*   **後果**：
    *   **Schema Coupling**：服務 A 修改了 Table 欄位，導致服務 B 崩潰。
    *   **Performance Bottleneck**：無法針對特定服務優化資料庫（如選擇 NoSQL 或 Cache），因為大家綁在一起。
*   **修正**：堅守 Database-per-Service。若需共用資料，透過 Data Replication (CDC) 或 API Composition。

### 3. Nano-services (奈米服務)
*   **症狀**：服務過度細分，例如建立一個只負責「驗證 Email 格式」的獨立服務。
*   **後果**：
    *   **Overhead Explosion**：序列化/反序列化與網路傳輸的資源消耗大於業務邏輯本身。
    *   **Ops Nightmare**：要監控和部署數百個只有幾行程式碼的服務。
*   **修正**：回歸 Domain-Driven Design (DDD)。服務大小應以「聚合 (Aggregate)」或「子域 (Sub-domain)」為邊界，而非單一功能函數。

### 4. Reach-in Reporting (直接伸手的報表)
*   **症狀**：報表系統或 BI 工具直接連線到各個微服務的生產資料庫進行 SQL Join。
*   **後果**：鎖表導致生產環境效能下降；微服務內部 Schema 無法重構（因為會打破報表）。
*   **修正**：實作 Data Lake 或 Data Warehouse，透過 ETL 或 Event Streaming 將資料同步到專門的分析資料庫。

### 5. Common Code Library Trap (共用程式庫陷阱)
*   **症狀**：將大量的業務邏輯（Domain Logic）放在一個 Shared Jar/DLL 中，所有微服務都依賴它。
*   **後果**：修改共用庫的一行程式碼，需要重新測試並部署所有微服務（回到單體架構的缺點）。
*   **修正**：Shared Library 僅限於「工具性質」（如 StringUtils, Logging Wrapper），絕不包含「業務邏輯」。業務邏輯若重複，寧可容許 Duplication 或抽取為獨立服務。

---

## Checklists & workflows｜檢查清單與流程

在決定拆分服務或審視現有架構時，請使用此清單進行自我診斷。

### Architecture Health Check (架構健康度檢查)

- [ ] **獨立部署測試**：我能否部署這個服務，而不需通知其他團隊或同步部署其他服務？
- [ ] **資料主權檢查**：是否有其他服務直接讀寫我的資料庫表格？(如果是，請打叉)
- [ ] **通訊模式檢視**：在核心的使用者路徑（Critical Path）上，是否超過 3 層的同步 HTTP 呼叫？(如 A->B->C->D，若是，風險極高)
- [ ] **共用庫檢視**：我的 Shared Library 是否包含了業務規則（例如：訂單折扣計算邏輯）？(若是，請移除)
- [ ] **交易一致性**：我是否試圖在跨服務操作中使用分散式交易（2PC/XA）？(應盡量避免，改用 Saga/最終一致性)

### Service Splitting Decision Flow (服務拆分決策流)

當你想將一個功能拆分為新服務時：

1.  **它是否代表一個完整的業務領域（Business Domain）？**
    *   No -> 它是實作細節，保留在原服務。
    *   Yes -> 繼續。
2.  **它是否需要獨立的資料儲存？**
    *   No -> 考慮是否只是模組化即可。
    *   Yes -> 繼續。
3.  **拆分後，服務間的通訊頻率是否過高（Chatty）？**
    *   Yes -> 邊界劃分可能錯誤，考慮合併。
    *   No -> **這可能是一個合理的微服務候選者。**

---

## Real-world examples｜實戰案例

### Case 1: The E-commerce "User Table" Trap (電商使用者資料陷阱)

**情境**：
一個電商系統，擁有 `Order Service` (訂單) 與 `User Service` (會員)。開發初期為了方便，兩個服務共用同一個 MySQL 資料庫。

**發生問題**：
會員團隊為了配合 GDPR 法規，將 `users` 表格中的 `address` 欄位加密並拆分成 `address_id`。
週五下午部署後，`Order Service` 全面崩潰，因為訂單結帳 SQL 依賴原本的明文 `address` 欄位。全站停止交易 2 小時。

**修正方案 (Refactoring)**：
1.  **隔離**：`Order Service` 建立自己的資料庫。
2.  **同步**：當 `User Service` 更新會員資料時，發送 `UserUpdated` 事件。
3.  **冗餘**：`Order Service` 訂閱該事件，並在自己的資料庫中儲存一份「下單所需的會員快照 (Snapshot)」。
4.  **結果**：`User Service` 可任意修改內部結構，`Order Service` 依賴的是公開的 Event Contract，而非資料庫 Schema。

### Case 2: The "Get Product" Waterfall (取得商品資訊的瀑布流)

**情境**：
手機 App 首頁需要顯示商品卡片（含價格、庫存、評價、基本資訊）。
後端拆分為 `Price Service`, `Inventory Service`, `Review Service`, `Catalog Service`。

**反模式實作**：
手機 App 發送請求給 `Catalog` 取得 ID，然後手機端再分別發送 3 個 HTTP 請求給其他服務。若首頁有 10 個商品，手機端瞬間發出 30+ 個請求。使用者感到 App 極度卡頓，手機發燙。

**修正方案 (BFF Pattern)**：
1.  引入 **GraphQL Gateway** 或 **BFF (Backend for Frontend)**。
2.  手機 App 只發送一個 Query 給 BFF。
3.  BFF 在內網（低延遲環境）並行呼叫上述 4 個微服務，組裝資料後一次回傳給手機。
4.  **結果**：網路來回次數 (RTT) 從 30+ 降為 1，使用者體驗大幅提升。