# 協議決策指南：REST vs GraphQL vs gRPC / Protocol Decision Guide: REST vs GraphQL vs gRPC

在現代系統架構中，沒有一種協議能夠統治所有場景。資深工程師的價值在於理解「取捨（Trade-offs）」，而非盲目追求新技術。本章節將協助你建立選擇通訊協議的決策框架。

In modern system architecture, no single protocol rules them all. The value of a senior engineer lies in understanding "trade-offs," not blindly chasing new technologies. This chapter helps you build a decision framework for selecting communication protocols.

---

## Mental model｜心智模型

要做出正確決策，請將這三種協議想像成不同的「溝通風格」與「契約形式」：

### 1. The Resource Manager (REST)
- **核心概念**：**資源導向 (Resource-Oriented)**。
- **心智模型**：就像去餐廳點餐，菜單是固定的（預定義的 Endpoints）。你想要「漢堡」和「可樂」，你必須分別指著菜單上的這兩項下單（或者餐廳提供一個套餐）。
- **關鍵字**：Standardization, Caching, Decoupling.
- **適用思維**：當你希望利用 HTTP 原生特性（如 Caching, Status Codes）且客戶端多樣化（瀏覽器、第三方開發者）時。

### 2. The Personal Shopper (GraphQL)
- **核心概念**：**資料圖譜導向 (Graph-Oriented)**。
- **心智模型**：就像聘請一位私人採購。你給他一張詳細清單：「我要漢堡的麵包、不要酸黃瓜，還要一杯半糖的可樂」。他跑一趟就能把你精確需要的東西帶回來，不多也不少。
- **關鍵字**：Flexibility, Client-Driven, Aggregation.
- **適用思維**：當客戶端（通常是 Frontend/Mobile）需要高度靈活的資料獲取，且後端資料模型複雜、關聯多時。

### 3. The Direct Line (gRPC)
- **核心概念**：**動作導向 (Action-Oriented / RPC)**。
- **心智模型**：就像軍隊的無線電通訊。雙方手持一本嚴格的代碼本（Protobuf）。通訊時講求極致效率、短指令、無廢話。如果對方沒有代碼本，就完全聽不懂。
- **關鍵字**：Performance, Strict Contract, Polyglot.
- **適用思維**：當你需要極低延遲的內部服務通訊，且雙方都能共享 Schema 定義時。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 混合架構模式 (The Hybrid Approach / BFF Pattern)
在微服務架構中，最常見的實務是「外圓內方」：
- **對外 (Frontend to Backend)**：使用 **GraphQL** 作為 BFF (Backend for Frontend) 層，聚合資料，提供前端極致體驗。
- **對內 (Service to Service)**：使用 **gRPC** 處理微服務之間的高頻通訊，確保型別安全與效能。
- **公開 API (Public/3rd Party)**：使用 **REST**，因為它對外部開發者最友善，且易於除錯與快取。

### 2. 協議決策矩陣 (Protocol Decision Matrix)

| Feature | REST (OpenAPI) | GraphQL | gRPC (Protobuf) |
| :--- | :--- | :--- | :--- |
| **Data Fetching** | Fixed (Over/Under-fetching risk) | Flexible (Exact fetching) | Fixed (Defined by method) |
| **Performance** | Good (Text/JSON overhead) | Variable (Depends on query complexity) | Excellent (Binary/Protobuf) |
| **Caching** | Excellent (HTTP native) | Hard (Application level required) | Hard (No HTTP caching) |
| **Browser Support** | Native | Library required (Apollo/Relay) | Requires gRPC-Web proxy |
| **Contract** | Loose (JSON Schema optional) | Strong (Typed Schema) | Strict (Protobuf required) |
| **Best For** | Public APIs, Simple CRUD | Complex UI, Mobile Apps | Internal Microservices |

### 3. gRPC 的契約優先開發 (Contract-First Development)
使用 gRPC 時，務必將 `.proto` 檔案視為 source of truth。
- **Pattern**: 建立一個獨立的 git repo 管理所有的 `.proto` 檔案，並透過 CI/CD 自動生成各語言（Go, Java, TS）的 client SDK。這能保證跨團隊的介面一致性。

### 4. GraphQL 的複雜度控制 (Complexity Governance)
GraphQL 賦予客戶端強大權力，但也容易導致 DoS 攻擊（如深層巢狀查詢）。
- **Best Practice**: 實作 Query Depth Limiting（查詢深度限制）與 Query Cost Analysis（查詢成本分析）。配合 **DataLoader** 模式解決 N+1 問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. REST: The "Chatty" Interface (碎嘴介面)
- **Anti-pattern**: 前端為了渲染一個頁面，需要呼叫 `/users/1`, `/users/1/orders`, `/orders/99/items` 等 5-6 個 API。
- **Consequence**: 高延遲，使用者體驗差，行動裝置耗電。
- **Fix**: 針對特定 UI 場景建立聚合 API (Composite Resources) 或轉向 GraphQL。

### 2. GraphQL: Exposing Database Schema Directly (直接暴露資料庫)
- **Anti-pattern**: 直接將 SQL Table 結構一對一映射成 GraphQL Type。
- **Consequence**: 安全性低，且當資料庫 Schema 變更時，前端直接炸裂（緊耦合）。
- **Fix**: 設計獨立的 API Schema 層，與 DB Schema 解耦。

### 3. gRPC: Using it for Browser Clients without Proxy (瀏覽器直連)
- **Anti-pattern**: 試圖讓瀏覽器直接發送 gRPC 請求。
- **Consequence**: 瀏覽器對 HTTP/2 和 Trailer headers 支援有限，導致實作極其痛苦且不穩定。
- **Fix**: 使用 gRPC-Web 搭配 Envoy Proxy，或者僅在後端服務間使用 gRPC。

### 4. General: Resume-Driven Development (履歷驅動開發)
- **Anti-pattern**: 一個簡單的 CRUD 系統，因為「很潮」而強行使用 gRPC 或 GraphQL。
- **Consequence**: 增加了 Build process 的複雜度（編譯 proto, 設定 Apollo Server），卻沒有獲得實質效益。
- **Fix**: 預設使用 REST。只有當遇到「多來源聚合」或「極致效能」痛點時，才引入其他協議。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow (決策流程樹)

1. **目標受眾是誰？**
   - 第三方開發者 / 公眾 -> **REST** (通用性最高)
   - 內部前端 / Mobile App -> **GraphQL** (開發體驗最佳)
   - 內部微服務 -> **gRPC** (效能最佳)

2. **資料關聯複雜度？**
   - 扁平、單一資源 -> **REST**
   - 樹狀、高度關聯、跨多個 Domain -> **GraphQL**

3. **效能需求？**
   - 需要 HTTP 快取 (CDN) -> **REST**
   - 低延遲、高吞吐量 (Streaming) -> **gRPC**

### Implementation Checklist (實作檢核表)

#### If choosing REST:
- [ ] 是否定義了 OpenAPI (Swagger) 規格？
- [ ] 是否正確使用了 HTTP Verbs (GET, POST, PUT, DELETE)？
- [ ] 是否利用了 HTTP Status Codes 處理錯誤？
- [ ] 是否考慮了 ETag 或 Cache-Control？

#### If choosing GraphQL:
- [ ] 是否實作了 DataLoader 以避免 N+1 查詢？
- [ ] 是否設定了查詢深度限制 (Depth Limit)？
- [ ] Schema 是否以「產品需求」而非「資料庫結構」設計？
- [ ] 是否有權限控管 (Field-level authorization)？

#### If choosing gRPC:
- [ ] 是否建立了統一的 Proto 檔案管理庫？
- [ ] 是否處理了向後相容性 (Field numbering)？
- [ ] 是否設定了 Deadlines/Timeouts (這是 gRPC 的關鍵功能)？
- [ ] 是否配置了 Health Checks？

---

## Real-world examples｜實戰案例

### Scenario A: 電商首頁 Dashboard (E-commerce Dashboard)
**需求**：顯示使用者個人資訊、最近訂單摘要、推薦商品、購物車數量。這些資料分散在 User Service, Order Service, Recommendation Service。
- **Decision**: **GraphQL**。
- **Reasoning**: 若用 REST，前端需發送 4+ 個請求，且會拿到一堆不需要的欄位（如訂單詳細 Log）。GraphQL 允許一次 Query 拿回剛好需要的 JSON 結構。

```graphql
# GraphQL Query Example
query {
  me {
    name
    cartCount
    recentOrders(limit: 3) {
      id
      status
      total
    }
    recommendations {
      productId
      title
      price
    }
  }
}
```

### Scenario B: 支付閘道器內部通訊 (Payment Gateway Internals)
**需求**：Payment Service 需要呼叫 Fraud Detection Service (詐欺偵測) 進行即時驗證。要求極低延遲 (<50ms)，且型別必須嚴格（金額、幣別不能出錯）。
- **Decision**: **gRPC**。
- **Reasoning**: 內部系統，不需要人類可讀的 JSON。Protobuf 的二進位序列化比 JSON 快 5-10 倍，且強型別契約保證了雙方對資料結構的理解一致。

```protobuf
// gRPC Protobuf Example
service FraudService {
  rpc CheckTransaction (TransactionRequest) returns (RiskAssessment);
}

message TransactionRequest {
  string user_id = 1;
  int64 amount_cents = 2; // 使用整數避免浮點數誤差
  string currency = 3;
}
```

### Scenario C: 靜態內容與圖片服務 (Content Delivery API)
**需求**：提供文章內容、圖片網址給全球讀者。讀多寫少。
- **Decision**: **REST**。
- **Reasoning**: 極度依賴 CDN 快取。REST 的 URL 唯一性配合 HTTP Header (`Cache-Control: public, max-age=3600`) 能讓 CDN 直接擋掉 90% 的流量，這是 GraphQL (通常是單一 POST endpoint) 和 gRPC 難以簡單做到的。