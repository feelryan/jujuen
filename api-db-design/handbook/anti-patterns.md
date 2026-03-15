# 常見反模式與設計陷阱 / Common Anti-Patterns & Design Pitfalls

## Mental model｜心智模型

### The "Short-Term Gain, Long-Term Pain" Curve
反模式（Anti-patterns）通常不是因為工程師「不懂」而產生的，而是因為它們在初期看起來像是**捷徑**。
Anti-patterns often don't arise from ignorance, but because they look like **shortcuts** initially.

在 API 與資料庫設計中，你需要建立一個核心觀念：**「耦合度（Coupling）」與「顆粒度（Granularity）」的平衡**。反模式通常發生在我們為了方便，打破了邊界（Boundaries），導致系統變得僵化。

想像你的系統架構像是一個有機體：
1.  **God Objects (上帝物件)**：像是過度肥胖的器官，承擔了過多職責，一旦生病（修改），全身受害。
2.  **Chatty Interfaces (碎嘴介面)**：像是神經系統過度敏感，做一個小動作需要來回傳遞成千上萬次訊號（Network Calls），導致延遲。
3.  **Distributed Monolith (分散式大泥球)**：像是連體嬰，表面上是兩個個體（Microservices），但共用同一個心臟（Shared Database），無法獨立生存。

**The Golden Rule:**
> **"Do not expose your internal data model as your external contract."**
> **「不要將內部的資料模型直接暴露為外部合約。」**

---

## Patterns & best practices｜常見模式與最佳實務

在討論反模式之前，我們先定義什麼是「健康的模式」。這些是針對反模式的解藥（Refactoring Strategies）。

### 1. Backend for Frontend (BFF) & Composite UI
**解決：Chatty Interfaces / Over-fetching**
不要讓客戶端發起 20 個 API 請求來渲染一個畫面。
-   **Pattern**: 建立一個聚合層（Aggregation Layer）或使用 GraphQL，根據 UI 需求組裝資料。
-   **Benefit**: 將複雜度留在 Server 端，減少網路往返（Round-trips）。

### 2. DTOs & Mappers (Data Transfer Objects)
**解決：Leaky Abstractions / God Objects**
資料庫實體（Entity）與 API 回傳物件（Resource）必須分離。
-   **Pattern**: 定義明確的 API Schema（如 OpenAPI/Protobuf），並使用 Mapper 將 DB Entity 轉換為 API Response。
-   **Benefit**: 當你修改 DB 欄位名稱時，不會導致成千上萬的 Mobile App 崩潰。

### 3. Database per Service (Private Tables)
**解決：Distributed Monolith (Shared Database)**
每個微服務或模組應該擁有自己的資料存儲（或至少是獨立的 Schema/Tables）。
-   **Pattern**: 服務 A 不能直接 `JOIN` 服務 B 的 Table。必須透過 API 呼叫或事件（Event）來獲取資料。
-   **Benefit**: 服務可以獨立部署、獨立擴展，且 Schema 變更不會意外破壞其他服務。

### 4. Pagination & Filtering by Default
**解決：Unbounded Result Sets**
永遠假設資料會增長到百萬筆。
-   **Pattern**: 所有列表型 API 強制實作 `limit`, `offset` (或 Cursor-based pagination)。
-   **Benefit**: 保護資料庫不被單一查詢拖垮（OOM）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是實務上最容易踩到的地雷，請務必在 Code Review 中攔截它們。

### 1. The God Object (上帝物件)
**Description**: 一個 API 端點回傳了「所有相關資訊」。例如 `GET /users/1` 回傳了使用者的基本資料、所有訂單歷史、付款紀錄、甚至登入 Log。
**Why it's bad**:
-   **Performance**: 查詢極慢，序列化（Serialization）耗時。
-   **Coupling**: 不需要訂單資訊的頁面也被迫下載這些資料（Over-fetching）。
-   **Security**: 容易不小心洩漏敏感資訊（如 `password_hash` 或 `internal_flags`）。

### 2. Chatty I/O (N+1 Problem over HTTP)
**Description**: 客戶端先呼叫 `GET /products` 拿到 20 個 ID，然後跑一個迴圈呼叫 20 次 `GET /products/{id}` 來拿詳細資訊。
**Why it's bad**:
-   **Latency**: 網路延遲是最大的效能殺手。Mobile 用戶在 4G/5G 環境下體驗極差。
-   **Server Load**: 伺服器瞬間承受高併發請求，容易被 DDoS。

### 3. The Distributed Monolith (Shared Database)
**Description**: 兩個標榜「微服務」的系統，直接連線到同一個資料庫，甚至互相修改對方的 Table。
**Why it's bad**:
-   **Locking**: 服務 A 的長交易鎖住了 Table，導致服務 B Time out。
-   **Integration Hell**: 服務 A 修改了 schema，服務 B 毫無預警地掛掉。
-   **No Autonomy**: 無法獨立升級資料庫版本或遷移技術堆疊。

### 4. Leaky Abstractions (洩漏的抽象)
**Description**: API 的錯誤訊息直接回傳 `SQL Integrity Constraint Violation Exception`，或者 API 的欄位名稱直接對應 DB 的 `is_deleted_flg` (包含匈牙利命名法)。
**Why it's bad**:
-   **Security**: 駭客可以透過錯誤訊息推測資料庫結構（SQL Injection 前兆）。
-   **Tight Coupling**: 你的 API 介面被 DB 實作綁架，無法重構。

### 5. Ignoring Idempotency (忽略冪等性)
**Description**: POST 請求（如付款、建立訂單）沒有設計防止重複提交的機制。
**Why it's bad**:
-   **Data Integrity**: 用戶網路不穩重試，導致被扣款兩次。
-   **User Trust**: 這是最嚴重的商業邏輯錯誤之一。

---

## Checklists & workflows｜檢查清單與流程

在設計 API 或 Schema Review 時，請使用此清單：

### Design Review Checklist
- [ ] **Payload Size Check**: 單一 API Response 是否超過 1MB？如果是，是否包含了非必要欄位？(Avoid God Object)
- [ ] **Network Calls Check**: 完成一個核心 UI 功能（如結帳頁），客戶端是否需要發送超過 3 個同步請求？(Avoid Chatty Interface)
- [ ] **Database Isolation**: 是否有其他服務直接依賴我的 Table？如果有，請改為提供 API 或發送 Domain Events。(Avoid Shared DB)
- [ ] **Abstraction Check**: JSON 欄位名稱是否是 `camelCase` (標準 API 風格) 而非 `snake_case` (DB 風格)？是否隱藏了內部 ID？
- [ ] **N+1 Prevention**: 在 ORM 層級，是否使用了 Eager Loading (`Include`, `Populate`) 或 Batch Loading (`DataLoader`)？
- [ ] **Error Handling**: 錯誤回應是否為標準化的 Error Code（如 `ORDER_NOT_FOUND`），而非原始 Exception Stack Trace？

### Decision Tree: "Should I split this API?"
1.  **Is the response > 100KB?**
    *   Yes -> Split into summary/detail endpoints or use GraphQL.
2.  **Do 80% of clients ignore 50% of the fields?**
    *   Yes -> Separate the rarely used fields into a sub-resource (e.g., `GET /users/1/audit-logs`).
3.  **Does calculating one field require a slow 3rd-party call?**
    *   Yes -> Remove that field from the main list API. Make it loaded on demand.

---

## Real-world examples｜實戰案例

### Case Study 1: The "User Profile" Trap (God Object)

**❌ Bad Design (Anti-pattern):**
`GET /api/v1/users/me`
```json
{
  "id": 123,
  "name": "Alice",
  "preferences": { ... }, // 1KB
  "orders": [ ... ],      // 50KB - 包含過去 5 年所有訂單
  "logs": [ ... ]         // 200KB - 包含所有登入紀錄
}
```
*後果*：每次用戶打開 App 首頁，都要下載 250KB 資料，DB 要做 3 次 heavy join。App 啟動慢，DB CPU 飆高。

**✅ Better Design:**
`GET /api/v1/users/me` (只回傳核心資料)
```json
{
  "id": 123,
  "name": "Alice",
  "links": {
    "orders": "/api/v1/users/me/orders",
    "logs": "/api/v1/users/me/logs"
  }
}
```
*改進*：首頁載入極快。若用戶點擊「歷史訂單」，再呼叫 `/orders` API (Lazy Loading)。

---

### Case Study 2: The "Shared Database" Nightmare

**Scenario**:
-   **Service A (Auth)**: Manages `users` table.
-   **Service B (Order)**: Directly joins `users` table to get email for receipts.

**The Incident**:
Service A 的團隊決定重構，將 `email` 欄位移到新的 `user_contacts` table。
他們更新了 Service A 的程式碼並部署。

**The Crash**:
Service B 瞬間全掛，因為它的 SQL `SELECT email FROM users ...` 失敗了（欄位不存在）。
Service B 的團隊正在睡覺，被 PagerDuty 叫醒，發現無法修復，因為他們沒有 Service A 的權限去讀新 Table。

**✅ Fix**:
Service B 應該只存 `user_id`。當需要 email 時：
1.  呼叫 Service A 的 `GET /users/:id` (RPC/HTTP)。
2.  或者，Service A 發出 `UserEmailUpdated` 事件，Service B 訂閱並更新自己本地的 cache table (Eventual Consistency)。