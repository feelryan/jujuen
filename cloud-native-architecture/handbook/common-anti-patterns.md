# 常見陷阱與反模式 / Common Pitfalls & Anti-Patterns

在雲原生架構的旅程中，最危險的不是技術選型錯誤，而是**架構風格與組織能力的不匹配**。許多團隊在擁抱 Microservices 與 Kubernetes 時，往往不自覺地引入了比單體架構（Monolith）更難維護的複雜度。

本章節將剖析那些「看起來很雲原生，實際上是災難」的常見反模式，並提供修正路徑。

---

## Mental model｜心智模型

要避開陷阱，首先要建立正確的雲原生代價評估模型：**複雜度守恆定律 (Conservation of Complexity)**。

當你將單體拆解為微服務時，業務邏輯的複雜度並沒有消失，而是從 **「程式碼內部 (In-process)」** 轉移到了 **「服務之間 (Inter-process / Network)」**。

### 1. 獨立部署性 (Independent Deployability) 是唯一指標
雲原生架構的核心價值在於速度與彈性。如果你必須同時部署 Service A 和 Service B 系統才能運作，那你並沒有獲得微服務的好處，只獲得了分散式系統的痛點（網路延遲、分區錯誤、序列化成本）。

### 2. 耦合度象限 (Coupling Quadrant)
想像一個座標軸：
- **X 軸：** 部署耦合 (Deployment Coupling)
- **Y 軸：** 邏輯/資料耦合 (Logical/Data Coupling)

我們追求的是 **低部署耦合 + 高內聚 (High Cohesion)**。反模式通常發生在我們誤以為拆分了服務（物理隔離），但在邏輯或資料層面上依然緊密糾纏。

---

## Patterns & best practices｜常見模式與最佳實務

在討論反模式之前，先確立什麼是「健康」的狀態。

### 1. 模組化單體優先 (Modular Monolith First)
在網域邊界 (Bounded Context) 不清晰前，先在單體內部透過 Module/Package 進行邏輯隔離，而非物理隔離。
- **Best Practice:** 透過編譯器強制執行邊界檢查（例如 Java 的 ArchUnit 或 Go 的 internal packages），確保模組間沒有循環依賴。

### 2. 資料庫私有化 (Database-per-Service)
每個服務必須擁有自己的資料儲存（可以是同一個實體 DB Server 的不同 Schema/Database）。
- **Pattern:** 其他服務若需存取資料，必須透過 API 或訂閱事件 (Event Sourcing)，絕對禁止跨庫 Join。

### 3. 非同步通訊預設 (Async Communication by Default)
為了避免服務間的連鎖故障 (Cascading Failures)，盡量減少同步的 HTTP/gRPC 請求鏈。
- **Pattern:** 使用 **Event-Driven Architecture (EDA)**。上游服務發出 `OrderCreated` 事件，下游服務自行監聽並處理，而非上游呼叫下游。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

這是本章的核心，請檢視你的系統是否出現以下症狀。

### 1. 分散式單體 (The Distributed Monolith)
這是最常見也最致命的反模式。你擁有了微服務的基礎設施，但服務之間高度依賴。
- **症狀 (Symptoms):**
  - 部署時需要依照特定順序啟動服務（例如：先起 B，再起 A）。
  - 改一個功能需要同時修改 3 個服務的程式碼並一起發布。
  - 系統延遲極高，因為一個請求在後端經過了 10 次同步 RPC 呼叫。
- **後果:** 運維成本激增，開發速度比單體還慢，且除錯極其困難。

### 2. 奈米服務 (Nano-services)
過度拆分，將單一功能或極小的邏輯片段（甚至一個 Function）變成一個獨立服務。
- **症狀 (Symptoms):**
  - 服務只有 CRUD 操作，沒有業務邏輯（Anemic Domain Model）。
  - 為了完成一個簡單業務（如「結帳」），需要在 5-6 個微小服務間來回傳遞資料。
  - **Resume Driven Development (履歷驅動開發):** 拆分理由是「為了用新語言/新框架」而非業務需求。
- **後果:** 效能被網路 I/O 吃光（Serialization/Deserialization overhead），且缺乏交易一致性保障。

### 3. 共享資料庫依賴 (Shared Database / The Integration Database)
多個微服務讀寫同一個資料庫表格，將資料庫作為整合層。
- **症狀 (Symptoms):**
  - Service A 修改了 Table Schema，導致 Service B 和 C 崩潰。
  - 為了效能，Service A 直接去 Join Service B 的 Table。
  - 資料庫成為單點效能瓶頸，且無法針對單一服務進行擴展。
- **後果:** 喪失了服務的獨立演化能力，實際上是「資料庫層面的單體」。

### 4. 過度工程化 (Over-engineering)
在流量或團隊規模未達標時，引入 Service Mesh、分散式追蹤、複雜的 CQRS 等技術。
- **症狀 (Symptoms):**
  - 團隊花在維護 Kubernetes YAML 和 Istio Config 的時間比寫業務程式碼還多。
  - 只有 3 個開發者，卻維護了 20 個微服務。
- **後果:** 認知負載 (Cognitive Load) 過重，團隊疲於奔命維護基礎設施。

---

## Checklists & workflows｜檢查清單與流程

在決定拆分服務或審視現有架構時，請使用此清單進行決策。

### 決策樹：我應該拆分這個服務嗎？ (Should I Split?)

1.  **這個功能是否屬於完全不同的業務領域 (Bounded Context)？**
    - [ ] 是 -> 考慮拆分
    - [ ] 否 -> 繼續下一步
2.  **這個模組是否有獨立的擴展需求 (Scaling) 或效能特徵？** (例如：影片轉檔 vs 使用者登入)
    - [ ] 是 -> 考慮拆分
    - [ ] 否 -> 繼續下一步
3.  **這個模組是否有獨立的發布頻率？**
    - [ ] 是 -> 考慮拆分
    - [ ] 否 -> **不要拆分，保持模組化單體**

### 架構健康度檢查清單 (Architecture Health Check)

- [ ] **獨立部署測試：** 我能否單獨部署 Service A，而不需要通知 Service B 的團隊？
- [ ] **資料庫隔離：** 是否有任何服務直接讀取不屬於它的 Table？
- [ ] **同步呼叫深度：** 一個 User Request 的處理路徑中，同步 (Blocking) 的 RPC 呼叫深度是否小於 3 層？
- [ ] **共用程式庫 (Shared Libs)：** 共用 Library 是否僅限於工具類 (Utils/Logging)，而不包含業務邏輯 (Business Logic)？(避免修改共用 Lib 導致全體重構)
- [ ] **失敗隔離：** 當 Service B 掛掉時，Service A 是會跟著掛掉 (500 Error)，還是能降級服務 (Degrade Gracefully)？

---

## Real-world examples｜實戰案例

### 案例一：電商系統的「共享資料庫」陷阱

#### ❌ Bad Practice (Anti-pattern)
- **架構：** `OrderService` 和 `CustomerService` 連接同一個 MySQL DB。
- **情境：** `OrderService` 需要驗證用戶積分。開發者為了方便，直接在 `OrderService` 裡寫 SQL：`SELECT points FROM customer_table WHERE id = ?`。
- **災難：** `CustomerService` 團隊決定重構積分系統，將 `points` 欄位移到新的 `loyalty_table`。上線後，`OrderService` 全部報錯，導致無法下單。這就是典型的**隱性耦合**。

#### ✅ Good Practice (Refactored)
- **架構：** Database-per-service。
- **解法：**
  1. `OrderService` 透過 RPC 呼叫 `CustomerService.getPoints(userId)` (同步，強一致性需求時)。
  2. 或者，`CustomerService` 在積分變動時發布 `CustomerPointsUpdated` 事件，`OrderService` 訂閱並在本地 DB 更新一份 Read Model (非同步，最終一致性)。

### 案例二：過度拆分的「奈米服務」

#### ❌ Bad Practice (Anti-pattern)
- **架構：** 一個簡單的「用戶註冊」流程被拆分為：
  - `ValidationService` (只做 Regex 檢查)
  - `PasswordHashService` (只做雜湊)
  - `UserDbService` (只做 SQL 寫入)
  - `EmailService` (發信)
- **問題：** 註冊一個用戶需要經過 4 次網路跳躍 (Network Hops)。一旦 `PasswordHashService` 網路抖動，整個註冊流程失敗。且 Debug 時需要跨 4 個服務看 Log。

#### ✅ Good Practice (Refactored)
- **架構：** 合併為 `IdentityService`。
- **解法：** 驗證、雜湊、寫庫都是 `IdentityService` 內部的函數呼叫 (In-process calls)。只有 `EmailService` 因為屬於不同領域（通知域）且容許延遲，可以保持獨立或透過 Message Queue 非同步觸發。