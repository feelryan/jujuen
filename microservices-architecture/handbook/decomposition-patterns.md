# 服務拆分策略與邊界界定 / Decomposition Strategies & Bounded Contexts

## Mental model｜心智模型

在進入微服務架構時，工程師最常犯的錯誤是將「模組化」等同於「微服務化」。服務拆分不僅僅是程式碼的搬移，更是**業務權責（Ownership）與資料主權（Data Sovereignty）的重新劃分**。

### 1. 垂直切分 vs. 水平分層 (Vertical Slicing vs. Horizontal Layering)
傳統單體應用習慣依賴「技術分層」（Controller, Service, DAO）。微服務的拆分必須是「垂直切分」，每一個服務都包含完整的技術堆疊（從 API 到資料庫），並圍繞著特定的**業務能力 (Business Capability)** 構建。

### 2. 語言邊界即服務邊界 (Linguistic Boundaries)
這是 DDD (Domain-Driven Design) 的核心。如何判斷邊界？請傾聽業務專家或不同部門如何使用名詞。
- 如果「商品 (Product)」在行銷部門意味著「SEO 描述與圖片」，而在倉儲部門意味著「貨架位置與重量」，這就是兩個不同的 **Bounded Contexts (界限上下文)**。
- **Rule of Thumb**: 當同一個名詞在不同場景下有完全不同的屬性或行為時，這通常是服務拆分的邊界。

### 3. 認知負載 (Cognitive Load)
服務的大小不應由程式碼行數決定，而應由「一個團隊能否完全理解並掌握該服務的所有邏輯」來決定。如果修改一個功能需要召開跨部門會議來確認影響範圍，該服務可能過大（或耦合過深）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 基於子域拆分 (Decompose by Subdomain)
利用 DDD 的子域概念來決定投資報酬率與拆分優先級：
- **Core Subdomain (核心子域)**: 公司的競爭優勢所在（如：Uber 的配對演算法）。這是最值得投入資源拆分與優化的部分。
- **Supporting Subdomain (支撐子域)**: 業務必須，但非核心競爭力（如：促銷活動管理）。
- **Generic Subdomain (通用子域)**: 行業通用的功能（如：認證、發票）。建議購買 SaaS 或使用開源方案，避免過度客製化拆分。

### 2. 絞殺者模式 (Strangler Fig Pattern)
針對遺留系統 (Legacy System) 的最安全遷移策略。
- **原理**: 不直接重寫舊系統，而是在舊系統周圍建立新服務。
- **實作**: 在前端或 API Gateway 層攔截特定請求，將流量逐步導向新服務。舊功能隨時間推移逐漸「枯死」。
- **優勢**: 降低 Big Bang 重寫的風險，隨時可回滾。

### 3. 服務獨佔資料庫 (Database-per-Service)
這是微服務的黃金法則。
- **原則**: 服務 A **絕對不能**直接存取服務 B 的資料庫表。
- **通訊**: 必須透過 API 呼叫或事件訂閱 (Event Subscription) 來獲取資料。
- **目的**: 確保服務 B 可以自由修改 Schema 而不破壞服務 A。

### 4. 聚合器模式 (Aggregator / BFF Pattern)
當拆分過細導致前端需要發送多次請求時使用。
- 建立一個 Backend for Frontend (BFF) 或 GraphQL 層，負責聚合多個微服務的資料，一次性回傳給客戶端，避免 "Chatty API" 問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分散式單體 (Distributed Monolith)
這是最糟糕的結果。你把單體拆成了多個服務，但它們之間緊密耦合。
- **徵兆**: 服務 A 部署時，服務 B 和 C 也必須一起部署；或者服務 A 掛了，B 和 C 也跟著掛。
- **原因**: 過度依賴同步呼叫 (Synchronous HTTP calls)、共用資料庫、共用程式碼庫 (Shared Libraries) 中包含業務邏輯。

### 2. 實體服務 (Entity Services / Anemic Services)
依照資料表來建立服務，例如 `OrderService`, `CustomerService`, `ProductService`，且只提供 CRUD 操作。
- **問題**: 這是「貧血模型 (Anemic Domain Model)」的架構版。業務邏輯會散落在各個呼叫方，導致邏輯重複與不一致。
- **修正**: 應轉向「基於行為」的服務，例如 `OrderingService` (處理下單流程), `OnboardingService` (處理開戶流程)。

### 3. 透過資料庫整合 (Integration via Database)
多個服務連線到同一個 Database Schema。
- **後果**: 資料庫成為巨大的耦合點。任何 Schema 變更都會牽一髮動全身，導致無法獨立部署，且資料庫鎖定 (Locking) 競爭激烈。

### 4. 奈米服務 (Nanoservices)
拆分過細，一個服務只做一件事（例如一個函數）。
- **代價**: 網路延遲、序列化成本、維運複雜度遠超過服務帶來的價值。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Should I split this? (我該拆分這個嗎？)

1.  **Isolate Data First**: 能否先將相關的資料表從主庫中邏輯隔離（例如移到獨立的 Schema）？如果不行的話，拆分服務是不可能的。
2.  **Identify Dependencies**: 檢查該模組有多少 Inbound/Outbound 依賴。依賴越少，越容易拆分。
3.  **Define Interface**: 定義清晰的 API 契約。
4.  **Migrate Code**: 移動程式碼。
5.  **Migrate Data**: 移動資料（最困難的一步）。

### Operational Checklist (實戰檢核表)

- [ ] **獨立部署能力**: 我是否可以在不通知其他團隊的情況下，安全地部署這個服務？
- [ ] **資料私有化**: 該服務是否擁有自己的資料庫（或獨立 Schema），且沒有其他服務直接連線該 DB？
- [ ] **事務邊界 (Transaction Boundary)**: 拆分後，原本的 ACID 事務是否需要轉變為最終一致性 (Saga/Eventual Consistency)？業務方是否接受？
- [ ] **替換性**: 如果這個服務爛掉了，我是否能在兩週內重寫它？（服務規模檢視）
- [ ] **無循環依賴**: 服務之間是否存在 A -> B -> C -> A 的呼叫循環？
- [ ] **日誌聚合**: 拆分後，我是否有唯一的 Trace ID 可以追蹤跨服務請求？

---

## Real-world examples｜實戰案例

### 案例：電子商務系統中的「使用者」拆分

在單體架構中，我們通常會有一個巨大的 `Users` 表格。但在微服務與 DDD 視角下，這個「使用者」應該被拆解到不同的 Context 中。

#### ❌ Anti-pattern: 通用 User Service
建立一個 `UserService`，包含 `username`, `password`, `email`, `address`, `preferences`, `credit_card`, `order_history`。所有服務都呼叫它。
*   **結果**: 變成瓶頸，修改困難，個資與非敏感資料混雜。

#### ✅ Best Practice: 依上下文拆分 (Decomposition by Context)

1.  **Identity & Access Context (Identity Service)**
    *   **關注點**: 認證與授權。
    *   **Data**: `User_ID`, `Username`, `PasswordHash`, `Roles`.
    *   **行為**: Login, Verify Token.

2.  **Sales Context (Customer Service)**
    *   **關注點**: 銷售與客戶關係。
    *   **Data**: `Customer_ID` (linked to User_ID), `LoyaltyPoints`, `CustomerLevel`.
    *   **行為**: Upgrade Tier, Apply Discount.

3.  **Shipping Context (Fulfillment Service)**
    *   **關注點**: 物流配送。
    *   **Data**: `Recipient_ID`, `ShippingAddress`, `ContactPhone`.
    *   **行為**: Validate Address, Calculate Shipping Cost.

**關鍵點**:
- 系統中沒有一個「上帝物件」代表使用者。
- 各服務透過 ID (`User_ID`) 關聯，但資料實體是物理隔離的。
- `Shipping Service` 不需要知道使用者的 `Password` 或 `LoyaltyPoints`，這體現了**最小權限原則**與**高內聚**。