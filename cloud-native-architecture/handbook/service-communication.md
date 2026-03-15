# 服務通訊協定選型與 API 設計 / Service Communication Protocols & API Design

## Mental Model｜心智模型

在雲原生架構中，服務通訊不僅僅是資料傳輸的技術選擇，更是**系統耦合度 (Coupling)** 與**邊界定義 (Boundary Definition)** 的具體展現。

要建立正確的心智模型，請將通訊視為兩個維度的決策：

1.  **邊界維度 (Boundary Dimension)：**
    *   **North-South Traffic (外部對內)**：面對不可控的客戶端（瀏覽器、Mobile App）。重點在於**相容性**、**可探索性**與**頻寬優化**。
    *   **East-West Traffic (內部服務間)**：面對受控的內部服務。重點在於**效能**、**型別安全**與**低延遲**。

2.  **時間維度 (Temporal Dimension)：**
    *   **Synchronous (同步)**：像打電話。雙方必須同時在線，即時獲得回應。適用於讀取資料 (Query)。缺點是容易產生連鎖故障 (Cascading Failure)。
    *   **Asynchronous (非同步)**：像發 Email 或 Slack。發送後不需等待，接收方有空再處理。適用於寫入操作或觸發副作用 (Command/Event)。優點是解耦與削峰填谷 (Load Leveling)。

**核心原則 (Core Principle)**：
> **"Smart Endpoints and Dumb Pipes"**
> 網路層（Pipes）應該單純負責傳輸，邏輯處理應留在服務端點（Endpoints）。但在選擇協定時，應根據「誰是消費者」來決定合約的嚴謹程度。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 協定選型矩陣 (Protocol Selection Matrix)

不要試圖用一種協定解決所有問題 (No Silver Bullet)。

| 特性 | REST (HTTP/1.1 & JSON) | gRPC (HTTP/2 & Protobuf) | GraphQL |
| :--- | :--- | :--- | :--- |
| **最佳場景** | 公共 API、簡單 CRUD、第三方整合 | 內部微服務通訊 (East-West)、高效能串流 | 前端聚合資料 (BFF)、行動端網路優化 |
| **優勢** | 生態系成熟、快取容易、人類可讀 | **強型別契約**、二進位傳輸極快、支援雙向串流 | **避免 Over-fetching/Under-fetching**、單一端點 |
| **劣勢** | 效能較差 (Text based)、無強型別約束 | 瀏覽器支援度需轉譯 (gRPC-Web)、除錯需工具 | 複雜度高、快取困難、容易寫出效能殺手查詢 |
| **決策建議** | **預設選項**，除非有特殊需求 | **後端服務間通訊的首選** | **複雜前端/Mobile App 的首選** |

### 2. 同步與非同步的混合策略 (Hybrid Sync/Async)

在微服務中，**「讀寫分離」**的通訊模式是保持系統彈性的關鍵：

*   **Queries (讀取) → Synchronous (REST/gRPC)**
    *   當使用者需要立即看到結果（如：查詢訂單詳情），使用同步呼叫。
    *   *Pattern:* 使用 **API Gateway** 或 **BFF (Backend for Frontend)** 聚合多個服務的同步回應。

*   **Commands (寫入/狀態變更) → Asynchronous (Message Queue/Event Bus)**
    *   當操作涉及多個服務的狀態變更（如：結帳 = 扣款 + 扣庫存 + 寄信），盡量使用非同步事件。
    *   *Pattern:* **Transactional Outbox Pattern**。先將事件寫入本地 DB，再由獨立 Process 發送到 Kafka/RabbitMQ，確保資料一致性。

### 3. API 設計優先 (Contract-First Design)

*   **OpenAPI (Swagger) / Protobuf IDL**：在寫任何程式碼之前，先定義介面。這份文件就是服務間的「法律合約」。
*   **Idempotency (冪等性)**：所有的寫入 API (POST/PUT/PATCH) 都必須設計為冪等的。
    *   *Practice:* 客戶端產生 `Idempotency-Key` (UUID)，伺服器端檢查此 Key 是否已處理過。這是解決網路超時重試導致重複扣款的唯一解法。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分散式單體 (The Distributed Monolith)
*   **現象**：服務 A 呼叫 B，B 呼叫 C，C 呼叫 D。這是一個同步的 HTTP 呼叫鏈。
*   **後果**：延遲疊加 (Latency adds up)，且任何一個環節失敗，整個請求就失敗。可用性大幅降低。
*   **解法**：引入非同步通訊，或使用 **Data Replication** (服務 A 訂閱 C 的資料變更，保存一份唯讀副本在本地，避免即時查詢)。

### 2. 共享資料庫作為通訊 (Shared Database Integration)
*   **現象**：服務 A 直接讀寫服務 B 的資料庫，而不是透過 API。
*   **後果**：服務 B 無法修改 Schema，因為會弄壞服務 A。兩個服務緊密耦合。
*   **解法**：資料庫私有化 (Database per Service)，僅透過 API 或 Event 存取資料。

### 3. 聊天式介面 (Chatty Interface / N+1 Problem)
*   **現象**：前端為了顯示一個畫面，需要呼叫 10 次 API (例如：先拿 User ID，再拿 Orders，再拿 Order Details)。
*   **後果**：行動端體驗極差，延遲高。
*   **解法**：使用 **GraphQL** 或專門的 **BFF (Backend for Frontend)** 來聚合請求，一次 Round-trip 拿回所有資料。

### 4. 破壞性變更 (Breaking Changes)
*   **現象**：修改了 API 回傳欄位的名稱或型別，導致舊版 App 直接 Crash。
*   **解法**：
    *   **加法原則**：只新增欄位，不刪除/修改舊欄位。
    *   **明確版本號**：URL (`/v1/users`) 或 Header (`Accept-Version: v1`) 版本控制。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Protocol Selection (協定選擇決策樹)

1.  **通訊發生在哪裡？**
    *   **瀏覽器/App 到 後端** → 進入步驟 2。
    *   **後端服務 到 後端服務** → 進入步驟 3。

2.  **前端需求是什麼？**
    *   資料結構複雜、層級深、不同頁面需要不同欄位組合 → **GraphQL**
    *   標準資源操作、需利用 HTTP Caching、團隊熟悉度優先 → **REST**
    *   需要即時雙向通訊 (如聊天室) → **WebSocket**

3.  **後端服務間的需求是什麼？**
    *   極致效能、低延遲、強型別約束 → **gRPC**
    *   需要解耦、處理突發流量、最終一致性即可 → **Async Messaging (Kafka/RabbitMQ)**
    *   簡單整合、除錯方便、非效能敏感路徑 → **REST**

### API Production Readiness Checklist (上線前檢查清單)

- [ ] **Timeouts**: 所有外部呼叫是否都設定了合理的 Timeout？(預設無限等待是災難)
- [ ] **Retries**: 是否實作了帶有 **Exponential Backoff (指數退避)** 與 **Jitter (隨機抖動)** 的重試機制？
- [ ] **Idempotency**: 寫入介面是否支援冪等性 Key？
- [ ] **Pagination**: 列表介面是否強制分頁？(避免一次回傳 10 萬筆資料撐爆記憶體)
- [ ] **Error Handling**: 錯誤訊息是否標準化？(不要直接把 Stack Trace 吐給使用者)
- [ ] **Observability**: 每個 Request 是否帶有 `Trace ID` 並會傳遞給下游服務？

---

## Real-world examples｜實戰案例

### 案例：電子商務下單流程 (E-commerce Order Placement)

此案例展示如何混合使用 REST/GraphQL、gRPC 與 Async Messaging。

#### 1. 前端通訊 (North-South)
*   **Client (Mobile App)** 發送請求給 **BFF (Backend for Frontend)**。
*   **Protocol**: `GraphQL` (Mutation: `createOrder`)。
*   **理由**: App 一次傳送訂單資訊，並希望回傳剛建立的訂單摘要與預估運送時間，GraphQL 可以在一次請求中完成。

#### 2. 服務聚合與同步檢查 (Sync Internal)
*   **BFF** 收到請求，需要確認庫存與用戶狀態。
*   **BFF** → **Inventory Service** (CheckStock)
*   **BFF** → **User Service** (ValidateUser)
*   **Protocol**: `gRPC`。
*   **理由**: 內部高頻呼叫，需要低延遲與強型別保證。若庫存不足，需立即報錯回傳給使用者 (Synchronous feedback)。

#### 3. 核心交易與非同步解耦 (Async Internal)
*   確認無誤後，**Order Service** 建立訂單並寫入資料庫。
*   **Order Service** 發送 `OrderCreated` 事件到 **Kafka**。
*   **Protocol**: `Async Messaging (Kafka)`。
*   **理由**: 下單後的「寄送確認信」、「通知倉儲出貨」、「更新推薦系統」等動作，不需要卡住使用者的回應時間，且允許稍微延遲處理。

#### 4. 處理副作用 (Event Consumers)
*   **Notification Service** 訂閱 `OrderCreated` → 發送 Email。
*   **Shipping Service** 訂閱 `OrderCreated` → 產生物流單。
*   **Data Warehouse** 訂閱 `OrderCreated` → 儲存分析數據。

#### Pseudo-code: gRPC Definition (Protobuf)

```protobuf
// order_service.proto
syntax = "proto3";

package ecommerce.order;

service OrderService {
  // 內部服務呼叫使用 gRPC
  rpc CreateOrder (CreateOrderRequest) returns (CreateOrderResponse);
}

message CreateOrderRequest {
  string user_id = 1;
  repeated OrderItem items = 2;
  // 冪等性 Key，防止重試導致重複下單
  string idempotency_key = 3; 
}

message OrderItem {
  string product_id = 1;
  int32 quantity = 2;
}
```

這個架構確保了使用者體驗的即時性（同步檢查），同時保證了後端系統的擴展性與容錯能力（非同步處理後續任務）。