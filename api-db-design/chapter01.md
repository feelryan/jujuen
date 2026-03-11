# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的系統設計面試或實務架構決策中，選擇正確的 API 風格（Paradigm）往往是決定系統效能、開發體驗（DX）與可維護性的第一道關卡。我們不再只是問「REST 是什麼」，而是探討「在特定限制下，為什麼 gRPC 比 REST 更適合」，或是「引入 GraphQL 會帶來哪些運維成本」。

In Senior System Design interviews or real-world architectural decisions, selecting the right API paradigm is often the first gatekeeper determining system performance, Developer Experience (DX), and maintainability. We no longer just ask "What is REST," but rather "Why is gRPC a better fit than REST under specific constraints," or "What operational costs does introducing GraphQL entail?"

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精準評估取捨 (Evaluate Trade-offs)**：在 REST, GraphQL, gRPC 與 WebSocket 之間，根據 Payload 大小、延遲需求、客戶端類型（Mobile vs. Backend）做出最佳選擇。
    Make optimal choices between REST, GraphQL, gRPC, and WebSocket based on payload size, latency requirements, and client types (Mobile vs. Backend).
2.  **設計混合架構 (Design Hybrid Architectures)**：理解如何在同一個系統中並存多種協議（例如：BFF 使用 GraphQL，內部微服務使用 gRPC）。
    Understand how to coexist multiple protocols within the same system (e.g., GraphQL for BFF, gRPC for internal microservices).
3.  **識別反模式 (Identify Anti-patterns)**：避免常見的架構陷阱，如在瀏覽器端強行使用 gRPC，或在簡單 CRUD 場景過度工程化使用 GraphQL。
    Avoid common architectural pitfalls, such as forcing gRPC in the browser or over-engineering with GraphQL for simple CRUD scenarios.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要像架構師一樣思考，我們需要建立不同協議的心智模型，而非僅僅記憶語法。
To think like an architect, we need to establish mental models for different protocols, rather than just memorizing syntax.

### 2.1 REST (Representational State Transfer)
*   **Mental Model**: **資源導向 (Resource-Oriented)**。就像瀏覽圖書館的目錄，每一本書都有唯一的編號（URI），你透過標準動詞（GET, POST, PUT, DELETE）來操作這些實體。
    **Mental Model**: **Resource-Oriented**. Like browsing a library catalog, every book has a unique ID (URI), and you manipulate these entities using standard verbs (GET, POST, PUT, DELETE).
*   **Key Trait**: 無狀態（Stateless）、利用 HTTP 語意（Caching, Status Codes）。
    **Key Trait**: Stateless, leverages HTTP semantics (Caching, Status Codes).
*   **Best For**: 公開 API（Public APIs）、簡單的 CRUD 服務、高度依賴 HTTP 快取的場景。
    **Best For**: Public APIs, simple CRUD services, scenarios heavily relying on HTTP caching.

### 2.2 GraphQL
*   **Mental Model**: **資料查詢語言 (Data Query Language)**。就像去自助餐廳，你不必接受固定的套餐（REST endpoint 回傳的固定結構），而是拿著盤子精確挑選你需要的欄位，甚至可以一次請求多個不同來源的菜色。
    **Mental Model**: **Data Query Language**. Like a buffet, you don't have to accept a fixed set meal (fixed structure from a REST endpoint). Instead, you take a plate and pick exactly the fields you need, potentially requesting items from multiple sources in a single go.
*   **Key Trait**: 客戶端驅動（Client-driven）、單一端點（Single Endpoint）、強型別 Schema。
    **Key Trait**: Client-driven, Single Endpoint, Strongly-typed Schema.
*   **Best For**: 前端需求多變的 Mobile/Web App、聚合多個微服務的 BFF (Backend for Frontend)。
    **Best For**: Mobile/Web Apps with rapidly changing frontend requirements, BFF (Backend for Frontend) aggregating multiple microservices.

### 2.3 gRPC (Google Remote Procedure Call)
*   **Mental Model**: **遠端函式呼叫 (Remote Function Call)**。這就像是在本地呼叫一個函式，但實際執行發生在遠端伺服器。它忽略了 HTTP 的語意（如 verbs），專注於動作（Action）與效能。
    **Mental Model**: **Remote Function Call**. It feels like calling a function locally, but the execution happens on a remote server. It abstracts away HTTP semantics (like verbs) and focuses on Actions and Performance.
*   **Key Trait**: 基於 Protobuf 的二進位傳輸（Binary）、HTTP/2 多路復用（Multiplexing）、嚴格合約（Strict Contract）。
    **Key Trait**: Protobuf-based binary transport, HTTP/2 Multiplexing, Strict Contract.
*   **Best For**: 內部微服務通訊（Service-to-Service）、低延遲與高吞吐量需求、多語言後端環境。
    **Best For**: Internal microservice communication (Service-to-Service), low latency and high throughput requirements, polyglot backend environments.

### 2.4 WebSocket
*   **Mental Model**: **雙向通道 (Bidirectional Tunnel)**。就像打電話，一旦接通（Handshake），雙方都可以隨時說話，不需要每次說話前都重新撥號。
    **Mental Model**: **Bidirectional Tunnel**. Like a phone call; once connected (Handshake), both parties can speak at any time without redialing for each sentence.
*   **Key Trait**: 全雙工（Full-duplex）、持久連線（Persistent Connection）、低開銷（Low overhead per message）。
    **Key Trait**: Full-duplex, Persistent Connection, Low overhead per message.
*   **Best For**: 即時聊天、股票報價、線上遊戲、協作編輯。
    **Best For**: Real-time chat, stock tickers, online gaming, collaborative editing.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，我們很少「只用一種」協議。資深工程師的價值在於懂得如何組合它們。
In large-scale distributed systems, we rarely use "just one" protocol. The value of a Senior Engineer lies in knowing how to combine them.

### 典型混合架構 (Typical Hybrid Architecture)

想像一個類似 Uber 或 DoorDash 的系統：
Imagine a system like Uber or DoorDash:

1.  **Client to Gateway (Public Network):**
    *   **Mobile App -> API Gateway (BFF):** 使用 **GraphQL**。
        *   *理由*：手機網路不穩定，GraphQL 可以減少 Round Trip Times (RTT)，一次拿完訂單詳情、司機位置與預估時間。避免 Over-fetching 節省流量。
        *   *Reason*: Mobile networks are flaky. GraphQL reduces Round Trip Times (RTT), fetching order details, driver location, and ETA in one go. Avoids over-fetching to save bandwidth.
    *   **Live Location Updates:** 使用 **WebSocket** (over MQTT or raw WS)。
        *   *理由*：需要低延遲的雙向推播。
        *   *Reason*: Requires low-latency bidirectional broadcasting.

2.  **Gateway to Internal Services (Private Network):**
    *   **BFF -> Order Service / Payment Service:** 使用 **gRPC**。
        *   *理由*：內部流量巨大，Protobuf 的序列化/反序列化速度比 JSON 快 5-10 倍，且 Payload 更小。強型別合約能防止微服務間的整合錯誤。
        *   *Reason*: Internal traffic is massive. Protobuf serialization/deserialization is 5-10x faster than JSON, with smaller payloads. Strongly-typed contracts prevent integration errors between microservices.

3.  **Third-party Integration:**
    *   **Payment Service -> Stripe/PayPal:** 使用 **REST (Webhooks)**。
        *   *理由*：這是網際網路的通用語言，第三方整合通常提供標準 REST API。
        *   *Reason*: It is the lingua franca of the internet; third-party integrations usually provide standard REST APIs.

### 設計考量矩陣 (Design Consideration Matrix)

| Feature | REST | GraphQL | gRPC | WebSocket |
| :--- | :--- | :--- | :--- | :--- |
| **Coupling** | Loose (HATEOAS ideal) | Tight (Schema dependent) | Tight (Stub dependent) | Loose (Message based) |
| **Cacheability** | High (HTTP standard) | Low (Needs complexity) | Low (No HTTP cache) | N/A |
| **Discoverability**| High (Swagger/OpenAPI)| High (Introspection) | Medium (Proto files) | Low |
| **Performance** | Medium (Text/JSON) | Medium (Processing overhead)| High (Binary) | High (Real-time) |

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例：設計一個電商訂單詳情頁面 (Designing an E-commerce Order Detail Page)

**背景 (Context)**：我們需要顯示訂單資訊，包含：訂單狀態、商品列表（來自 Product Service）、物流進度（來自 Shipping Service）、發票資訊（來自 Billing Service）。
**Context**: We need to display order information, including: Order Status, Item List (from Product Service), Shipping Progress (from Shipping Service), and Invoice Info (from Billing Service).

#### Phase 1: Naive REST Approach (Chatty Interfaces)

前端分別呼叫三個 API：
The frontend calls three separate APIs:
1.  `GET /orders/123`
2.  `GET /shipping/123`
3.  `GET /billing/123`

*   **問題 (Problem)**：
    *   **Under-fetching**: 為了拿商品圖片，可能還需要根據 Order 回傳的 IDs 再去呼叫 `GET /products/{id}` (N+1 問題)。
    *   **Latency**: 瀏覽器有併發連線限制，且行動網路建立連線成本高。
    *   **Problem**:
        *   **Under-fetching**: To get product images, we might need to call `GET /products/{id}` based on IDs returned by the Order service (N+1 problem).
        *   **Latency**: Browsers have concurrent connection limits, and connection establishment costs are high on mobile networks.

#### Phase 2: Optimized with GraphQL (BFF Pattern)

我們引入一個 GraphQL 層作為 BFF。
We introduce a GraphQL layer as a BFF.

**Schema Definition:**
```graphql
type Order {
  id: ID!
  status: String
  items: [Product]
  shipping: ShippingInfo
  invoice: Invoice
}

type Product {
  name: String
  imageUrl: String
  # price is omitted if not needed for this view
}
```

**Query:**
```graphql
query {
  order(id: "123") {
    status
    items {
      name
      imageUrl
    }
    shipping {
      estimatedDelivery
    }
  }
}
```

*   **優勢 (Advantage)**：單一請求，精確獲取所需資料。後端 Resolver 負責併發呼叫下游服務。
    **Advantage**: Single request, fetching exactly what's needed. Backend resolvers handle concurrent calls to downstream services.

#### Phase 3: Internal Communication with gRPC

GraphQL Resolver 如何拿到資料？它透過 gRPC 呼叫內部的微服務。
How does the GraphQL Resolver get the data? It calls internal microservices via gRPC.

**Protobuf Definition (Internal):**
```protobuf
// product.proto
service ProductService {
  rpc GetProducts (GetProductsRequest) returns (GetProductsResponse);
}

message Product {
  string id = 1;
  string name = 2;
  double price = 3; // Strict types
  // ... heavy details
}
```

*   **實作細節 (Implementation Detail)**：
    GraphQL Server (Node.js/Go) 收到請求後，並行發起 gRPC calls (`Promise.all` or Go routines) 給 Order, Shipping, Product services。
    *   gRPC 使用 HTTP/2 連線池，復用連線，延遲極低。
    *   Protobuf 解析極快，節省 CPU。
    GraphQL Server (Node.js/Go) receives the request and initiates parallel gRPC calls (`Promise.all` or Go routines) to Order, Shipping, and Product services.
    *   gRPC uses HTTP/2 connection pooling, reusing connections for very low latency.
    *   Protobuf parsing is extremely fast, saving CPU.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在瀏覽器直接使用 gRPC (gRPC in the Browser)
*   **錯誤 (Pitfall)**：試圖讓 Web 前端直接透過 gRPC 連線後端。
    **Pitfall**: Trying to connect the Web frontend directly to the backend via gRPC.
*   **原因 (Why)**：瀏覽器對 HTTP/2 的控制權限不足（無法直接存取 HTTP/2 frames），需要 `gRPC-Web` 代理，這增加了架構複雜度且失去了部分 gRPC 的效能優勢。
    **Why**: Browsers have insufficient control over HTTP/2 (cannot directly access HTTP/2 frames), requiring a `gRPC-Web` proxy. This adds architectural complexity and negates some of gRPC's performance benefits.
*   **解法 (Solution)**：前端使用 REST 或 GraphQL，在 Gateway 層轉換為 gRPC 進入內網。
    **Solution**: Use REST or GraphQL for the frontend, and translate to gRPC at the Gateway layer for the internal network.

### 5.2 GraphQL 的 N+1 查詢災難 (GraphQL N+1 Query Disaster)
*   **錯誤 (Pitfall)**：在 GraphQL Resolver 中直接寫資料庫查詢，沒有做 Batching。
    **Pitfall**: Writing database queries directly in GraphQL Resolvers without Batching.
*   **情境 (Scenario)**：查詢 10 個訂單，每個訂單都要查 User 資訊。結果導致 1 次查詢訂單 + 10 次查詢 User = 11 次 DB calls。
    **Scenario**: Querying 10 orders, each requiring User info. Result: 1 query for orders + 10 queries for users = 11 DB calls.
*   **解法 (Solution)**：使用 **DataLoader** 模式。將 ID 收集起來，在下一個 event loop tick 用 `SELECT * FROM users WHERE id IN (...)` 一次查完。
    **Solution**: Use the **DataLoader** pattern. Collect IDs and fetch them all at once in the next event loop tick using `SELECT * FROM users WHERE id IN (...)`.

### 5.3 濫用 WebSocket 傳輸狀態 (Stateful WebSocket Abuse)
*   **錯誤 (Pitfall)**：將所有 API 請求都透過 WebSocket 傳送，只因為「已經建立了連線」。
    **Pitfall**: Sending all API requests via WebSocket just because "the connection is already established."
*   **原因 (Why)**：WebSocket 是有狀態的（Stateful），難以水平擴展（Load Balancing 困難，連線斷掉需要複雜的重連邏輯），且無法利用 CDN 或 HTTP Cache。
    **Why**: WebSockets are Stateful, making horizontal scaling difficult (Load Balancing is tricky, disconnection requires complex reconnection logic), and they cannot leverage CDNs or HTTP Caching.
*   **解法 (Solution)**：混合使用。讀取資料用 REST/GraphQL，只有「伺服器主動推播」才用 WebSocket。
    **Solution**: Hybrid approach. Use REST/GraphQL for data fetching, and use WebSocket only for "Server-Initiated Push."

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於自我檢測或面試他人，重點在於「為什麼」而非「如何」。
These questions can be used for self-assessment or interviewing others, focusing on "Why" rather than "How."

### Q1: 你會如何為一個「即時多人協作文件編輯器」（如 Google Docs）選擇通訊協議？
**How would you choose communication protocols for a "Real-time Collaborative Document Editor" (like Google Docs)?**

*   **高分回答要點 (Key Points)**：
    *   **Operational Transformation (OT) / CRDTs** 需要極低延遲與順序保證 -> **WebSocket** 是核心。
    *   **Initial Load**: 打開文件時，不需要透過 WebSocket 慢慢拉，應該用 **REST/GraphQL** 快速載入 Snapshot。
    *   **Save/Export**: 背景存檔可以用 REST，因為不需要即時性，且具備等冪性（Idempotency）。
    *   **Key Points**:
        *   **Operational Transformation (OT) / CRDTs** require ultra-low latency and ordering guarantees -> **WebSocket** is core.
        *   **Initial Load**: When opening a doc, don't stream it slowly via WebSocket; use **REST/GraphQL** to load the Snapshot quickly.
        *   **Save/Export**: Background saving can use REST as it doesn't require real-time traits and benefits from Idempotency.

### Q2: 為什麼很多大型科技公司內部從 REST 遷移到 gRPC？這帶來了什麼挑戰？
**Why do many Big Tech companies migrate internally from REST to gRPC? What challenges does this introduce?**

*   **高分回答要點 (Key Points)**：
    *   **優點**: 效能（Binary vs Text）、強型別合約（減少「我以為這個欄位是 string」的錯誤）、Code Generation（自動產生 Client SDK）。
    *   **挑戰**: 可讀性差（無法用 `curl` 或瀏覽器直接除錯，需 `grpcurl`）、Load Balancing 複雜（HTTP/2 的長連線特性導致 L4 LB 失效，需要 L7 LB 或 Client-side LB）。
    *   **Key Points**:
        *   **Pros**: Performance (Binary vs. Text), Strong Contracts (reduces "I thought this field was a string" errors), Code Generation (automatic Client SDKs).
        *   **Cons**: Poor readability (cannot debug directly with `curl` or browser, need `grpcurl`), Complex Load Balancing (HTTP/2 persistent connections make L4 LB ineffective, requiring L7 LB or Client-side LB).

### Q3: 什麼時候你 *不會* 選擇 GraphQL？
**When would you *NOT* choose GraphQL?**

*   **高分回答要點 (Key Points)**：
    *   **簡單服務**: 只有幾個 Endpoint，引入 GraphQL 增加了 Runtime 複雜度。
    *   **檔案上傳**: GraphQL 原生對 Binary/Multipart 支援不如 REST 成熟。
    *   **安全性考量**: 複雜的查詢可能導致 DoS 攻擊（需實作 Query Depth Limit / Complexity Analysis）。
    *   **HTTP Cache**: 如果系統極度依賴 HTTP 層級的快取（如 Varnish/CDN），GraphQL 預設的 POST 請求會讓這變得困難。
    *   **Key Points**:
        *   **Simple Services**: Only a few endpoints; GraphQL adds unnecessary runtime complexity.
        *   **File Uploads**: GraphQL's native support for Binary/Multipart is less mature than REST.
        *   **Security**: Complex queries can lead to DoS attacks (requires implementing Query Depth Limit / Complexity Analysis).
        *   **HTTP Cache**: If the system relies heavily on HTTP-level caching (e.g., Varnish/CDN), GraphQL's default POST requests make this difficult.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **REST** 是通用語言，適合公開 API 與簡單資源操作，善用 HTTP 快取。
    **REST** is the lingua franca, suitable for public APIs and simple resource manipulation, leveraging HTTP caching.
2.  **GraphQL** 是資料聚合器，適合解決 Client 端靈活性與 Over-fetching，常作為 BFF。
    **GraphQL** is a data aggregator, solving Client flexibility and Over-fetching, often used as a BFF.
3.  **gRPC** 是效能怪獸，適合內部微服務通訊，強型別與 Code Gen 是大型團隊的救星。
    **gRPC** is a performance beast, suitable for internal microservices; strong typing and Code Gen are lifesavers for large teams.
4.  **WebSocket** 是專用通道，僅在需要雙向、低延遲推播時使用，不要濫用。
    **WebSocket** is a specialized tunnel; use only for bidirectional, low-latency push scenarios. Do not abuse.
5.  **混合架構** 是常態：External REST/GraphQL + Internal gRPC + Specific WebSocket。
    **Hybrid Architecture** is the norm: External REST/GraphQL + Internal gRPC + Specific WebSocket.

### 後續延伸 (Next Steps)
掌握了 API 協議後，下一步我們將深入資料儲存層的設計，這通常是 API 效能的瓶頸所在。
Having mastered API protocols, the next step is to dive into Data Storage Layer design, which is often the bottleneck for API performance.

*   **Next Chapter**: `Schema Design & Database Selection` (SQL vs. NoSQL, Normalization vs. Denormalization).
*   **Action Item**: 嘗試在你的專案中，將一個頻繁呼叫且 Payload 大的 REST API，改寫為 GraphQL 或 gRPC，並測量其 Latency 變化。
    **Action Item**: Try refactoring a frequent, heavy-payload REST API in your project to GraphQL or gRPC, and measure the Latency change.