# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，API 設計不僅僅是為了讓前後端能夠傳輸資料，更是為了建立一套可演進、可維護且符合業界標準的通訊協議。本章將超越基礎的 CRUD，深入探討 RESTful 架構的成熟度模型、如何優雅地處理版本控制（Versioning），以及在 Express 中實作 Content Negotiation 與 HATEOAS 的實務考量。

In the career of a Senior Software Engineer, API design is not just about enabling data transfer between frontend and backend; it is about establishing a communication protocol that is evolvable, maintainable, and compliant with industry standards. This chapter goes beyond basic CRUD to delve into the Richardson Maturity Model, how to gracefully handle Versioning, and practical considerations for implementing Content Negotiation and HATEOAS in Express.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **評估與提升 API 成熟度**：利用 Richardson Maturity Model (RMM) 檢視現有 API，並理解何時該追求 Level 3 (HATEOAS) 以及何時保持 Level 2 即可。
    **Evaluate and Elevate API Maturity**: Use the Richardson Maturity Model (RMM) to audit existing APIs, understanding when to pursue Level 3 (HATEOAS) and when Level 2 suffices.

2.  **制定版本控制策略**：在 URI Versioning、Header Versioning (Accept Header) 與 Query Parameter Versioning 之間做出符合系統需求的架構決策。
    **Formulate Versioning Strategies**: Make architectural decisions between URI Versioning, Header Versioning (Accept Header), and Query Parameter Versioning based on system requirements.

3.  **實作進階 Express 模式**：在 Express 中實作內容協商（Content Negotiation）與超媒體控制（Hypermedia Controls），提升 API 的自我描述能力。
    **Implement Advanced Express Patterns**: Implement Content Negotiation and Hypermedia Controls in Express to enhance the self-descriptiveness of the API.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Richardson Maturity Model (RMM)
RMM 是衡量 RESTful API 是否真正符合 REST 架構風格的指標。許多自稱為 REST 的 API 實際上只停留在 Level 1 或 Level 2。

RMM is a metric for measuring whether a RESTful API truly conforms to the REST architectural style. Many APIs that claim to be REST actually stop at Level 1 or Level 2.

*   **Level 0: The Swamp of POX (Plain Old XML/JSON)**
    *   使用 HTTP 僅作為傳輸通道（Tunneling），通常只用一個 End-point 和 POST 方法（類似 RPC）。
    *   Using HTTP merely as a transport tunnel, typically using a single endpoint and the POST method (RPC-like).
*   **Level 1: Resources**
    *   引入資源（Resources）概念，每個資源有獨立的 URI（如 `/users/123`），但動詞使用可能仍不規範。
    *   Introduces the concept of Resources, where each resource has a unique URI (e.g., `/users/123`), but verb usage may still be inconsistent.
*   **Level 2: HTTP Verbs**
    *   正確使用 HTTP 動詞（GET, POST, PUT, DELETE, PATCH）與狀態碼（200, 201, 404, 409）。這是大多數現代 "RESTful" API 的實務標準。
    *   Correct usage of HTTP verbs (GET, POST, PUT, DELETE, PATCH) and status codes (200, 201, 404, 409). This is the practical standard for most modern "RESTful" APIs.
*   **Level 3: Hypermedia Controls (HATEOAS)**
    *   API 回應中包含導航鏈接（Links），告訴客戶端接下來可以做什麼（狀態轉換）。這讓 Client 與 Server 的耦合度最低。
    *   API responses include navigational links, telling the client what can be done next (state transitions). This minimizes coupling between Client and Server.

## 2.2 API Versioning Strategies
版本控制是為了處理「破壞性變更」（Breaking Changes）。在 Express 中，我們通常有三種主要實作心智模型：

Versioning is for handling "Breaking Changes." In Express, we typically have three main mental models for implementation:

1.  **URI Path (The Pragmatist's Choice)**: `/api/v1/resource`
    *   **Pros**: 直觀、易於快取、瀏覽器可直接測試。
    *   **Cons**: 破壞了 URI 作為資源唯一識別符的概念（同一個資源有兩個 URI）。
    *   **Pros**: Intuitive, easy to cache, testable directly in browsers.
    *   **Cons**: Violates the concept of URI as a unique resource identifier (one resource has two URIs).

2.  **Custom Header**: `X-API-Version: 1`
    *   **Pros**: URI 保持潔淨。
    *   **Cons**: 快取較複雜（Vary header），不符合標準 HTTP 語意。
    *   **Pros**: Keeps URIs clean.
    *   **Cons**: Caching is more complex (Vary header), not standard HTTP semantics.

3.  **Content Negotiation (The Purist's Choice)**: `Accept: application/vnd.myapi.v1+json`
    *   **Pros**: 最符合 REST 精神，將版本視為資源的一種「表現形式（Representation）」。
    *   **Cons**: 測試與實作最為繁瑣，許多現成工具支援度較低。
    *   **Pros**: Most aligned with REST principles, treating version as a "Representation" of the resource.
    *   **Cons**: Most cumbersome to test and implement; lower support in many off-the-shelf tools.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 API Gateway vs. Application Logic
在大型分散式系統中，版本控制通常不會完全由 Express 應用程式邏輯處理。

In large-scale distributed systems, versioning is rarely handled entirely by the Express application logic.

*   **API Gateway Layer**: 常見做法是在 Gateway (如 Kong, Nginx, AWS API Gateway) 層級識別 `/v1/` 或 `/v2/`，然後將請求路由到不同的 Service Cluster 或同一個 Service 的不同實例。
    **API Gateway Layer**: A common practice is to identify `/v1/` or `/v2/` at the Gateway level (e.g., Kong, Nginx, AWS API Gateway) and then route the request to different Service Clusters or different instances of the same Service.
*   **Express Layer**: 若規模較小或採用 Monolith，Express 則需透過 Router 分離不同版本的 Controller。
    **Express Layer**: If the scale is smaller or a Monolith is used, Express needs to separate Controllers for different versions via Routers.

## 3.2 HATEOAS 的實務取捨 (The Pragmatic HATEOAS)
在 System Design 面試或實務中，盲目追求 Level 3 是危險的。

In System Design interviews or practice, blindly pursuing Level 3 is dangerous.

*   **Internal APIs**: 前端與後端由同一團隊開發時，HATEOAS 往往被視為過度設計（Over-engineering），因為前端已經知道路由規則。
    **Internal APIs**: When frontend and backend are developed by the same team, HATEOAS is often seen as over-engineering because the frontend already knows the routing rules.
*   **Public APIs / Generic Clients**: 若你的 API 是給第三方開發者或通用客戶端（如瀏覽器、爬蟲）使用，HATEOAS 能提供極佳的自我發現能力（Self-discovery）。
    **Public APIs / Generic Clients**: If your API is for third-party developers or generic clients (like browsers, crawlers), HATEOAS provides excellent self-discovery capabilities.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將模擬一個 User API 的演進過程，展示如何從簡單的 REST 設計過渡到支援版本控制與 HATEOAS 的架構。

We will simulate the evolution of a User API, demonstrating how to transition from a simple REST design to an architecture that supports versioning and HATEOAS.

## Scenario: Evolving the User Resource
需求變更：原本的 `name` 欄位需要拆分為 `firstName` 與 `lastName`。這是一個 Breaking Change。

Requirement Change: The original `name` field needs to be split into `firstName` and `lastName`. This is a Breaking Change.

### Step 1: Project Structure for Versioning
為了避免程式碼混亂，我們利用 Express 的 `Router` 來隔離版本。

To avoid code spaghetti, we use Express `Router` to isolate versions.

```javascript
// structure
// src/
//   routes/
//     v1/
//       users.js
//     v2/
//       users.js
//   app.js
```

### Step 2: Implementation (URI Versioning)
這是最常見且工程師最容易理解的方式。

This is the most common approach and easiest for engineers to understand.

```javascript
// src/routes/v1/users.js
const express = require('express');
const router = express.Router();

router.get('/:id', (req, res) => {
  // V1 Logic: Returns full name
  res.json({
    id: req.params.id,
    name: "John Doe",
    email: "john@example.com"
  });
});

module.exports = router;
```

```javascript
// src/routes/v2/users.js
const express = require('express');
const router = express.Router();

// Helper for HATEOAS links
const createLinks = (req, userId) => {
  const baseUrl = `${req.protocol}://${req.get('host')}/api/v2/users/${userId}`;
  return [
    { rel: 'self', method: 'GET', href: baseUrl },
    { rel: 'update', method: 'PUT', href: baseUrl },
    { rel: 'delete', method: 'DELETE', href: baseUrl }
  ];
};

router.get('/:id', (req, res) => {
  // V2 Logic: Split names + HATEOAS
  const userId = req.params.id;
  
  res.json({
    id: userId,
    firstName: "John",
    lastName: "Doe",
    email: "john@example.com",
    // Level 3: Hypermedia Controls
    _links: createLinks(req, userId)
  });
});

module.exports = router;
```

```javascript
// src/app.js
const express = require('express');
const v1Users = require('./routes/v1/users');
const v2Users = require('./routes/v2/users');

const app = express();

// Mounting routers
app.use('/api/v1/users', v1Users);
app.use('/api/v2/users', v2Users);

app.listen(3000, () => console.log('Server running on port 3000'));
```

### Step 3: Advanced - Header Based Versioning (Strategy Pattern)
若不想汙染 URL，我們可以使用 Middleware 根據 Header 動態切換 Handler。

If we don't want to pollute the URL, we can use Middleware to dynamically switch Handlers based on Headers.

```javascript
// src/middleware/versionHandler.js
const versionHandler = (versions) => {
  return (req, res, next) => {
    // Check Accept header or custom header
    // Example: Accept: application/vnd.myapi.v2+json
    const acceptHeader = req.headers['accept'];
    let version = 'v1'; // Default

    if (acceptHeader && acceptHeader.includes('vnd.myapi.v2')) {
      version = 'v2';
    }

    const handler = versions[version];
    if (handler) {
      return handler(req, res, next);
    }
    
    // Fallback or Error
    res.status(406).json({ error: 'Not Acceptable: Unsupported version' });
  };
};

// Usage in route
const userControllerV1 = (req, res) => { /* ... */ };
const userControllerV2 = (req, res) => { /* ... */ };

app.get('/api/users/:id', versionHandler({
  'v1': userControllerV1,
  'v2': userControllerV2
}));
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 The "Breaking Change" Denial
**錯誤 (Pitfall)**: 修改了 API 回傳的 JSON 結構（例如將 `userId` 從 Number 改為 String），但沒有升級版本號。
**Pitfall**: Changing the JSON structure returned by the API (e.g., changing `userId` from Number to String) without bumping the version number.

**後果 (Consequence)**: 依賴強型別的客戶端（如 iOS/Android app 或 gRPC clients）會直接崩潰。
**Consequence**: Strongly-typed clients (like iOS/Android apps or gRPC clients) will crash immediately.

**修正 (Fix)**: 任何破壞向後相容性（Backward Compatibility）的變更，都**必須**引入新版本。新增欄位通常不視為 Breaking Change，但修改或刪除欄位則是。
**Fix**: Any change that breaks Backward Compatibility **must** introduce a new version. Adding fields is usually not considered a Breaking Change, but modifying or deleting fields is.

## 5.2 Versioning by Query Parameter
**錯誤 (Pitfall)**: 使用 `/api/users?version=2`。
**Pitfall**: Using `/api/users?version=2`.

**為何不好 (Why it's bad)**: 雖然技術上可行，但這讓 Cache 機制變得複雜（許多 CDN 或 Proxy 預設會忽略 Query Params 進行快取）。此外，Query Params 應該用於過濾（Filtering）或分頁（Pagination），而非資源定義。
**Why it's bad**: While technically feasible, it complicates caching mechanisms (many CDNs or Proxies ignore Query Params for caching by default). Furthermore, Query Params should be used for Filtering or Pagination, not resource definition.

## 5.3 Fake HATEOAS
**錯誤 (Pitfall)**: 在每個回應都加上 `_links`，但這些連結是寫死的（Hardcoded），且客戶端根本不使用。
**Pitfall**: Adding `_links` to every response, but these links are hardcoded, and the client never uses them.

**觀點 (Perspective)**: 如果你的客戶端是自家開發的 SPA，且邏輯緊密耦合，強行實作 HATEOAS 只會增加 Payload 大小與開發成本，卻無實際效益。**YAGNI (You Aren't Gonna Need It)** 原則適用於此。
**Perspective**: If your client is an in-house SPA with tightly coupled logic, forcing HATEOAS implementation only increases Payload size and development cost without tangible benefits. The **YAGNI** principle applies here.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你會如何選擇 API 版本控制的策略？(URI vs Header)
**How do you choose an API versioning strategy? (URI vs Header)**

*   **高分回答要點 (Key Points)**:
    *   **DX (Developer Experience)**: URI Versioning (`/v1/...`) 最友善，開發者可以直接在瀏覽器看結果，文件也容易編寫。
    *   **REST Purity**: Header Versioning (`Accept`) 最符合語意，保持資源 URI 的唯一性。
    *   **Cache**: URI Versioning 對 CDN 快取最友善。Header Versioning 需要設定 `Vary: Accept` header，否則可能導致快取錯亂。
    *   **結論**: 公開 API (Public API) 傾向 URI Versioning 以降低接入門檻；內部微服務或追求極致架構時可考慮 Header Versioning。

## Q2: 什麼情況下 HTTP 200 OK 是不恰當的？
**When is HTTP 200 OK inappropriate?**

*   **高分回答要點 (Key Points)**:
    *   當操作是「建立」資源時，應回傳 `201 Created`。
    *   當操作是「非同步處理」時（如長任務），應回傳 `202 Accepted`。
    *   **Anti-pattern**: 發生錯誤時回傳 200 OK 但 Body 包含 `{ "error": "Something went wrong" }`。這會導致監控系統無法正確捕捉錯誤率，且讓 HTTP Client 的錯誤處理邏輯變複雜。

## Q3: 如何優雅地棄用 (Deprecate) 舊版 API？
**How do you gracefully deprecate an old API version?**

*   **高分回答要點 (Key Points)**:
    *   **Sunset Header**: 使用標準的 `Sunset` HTTP Header 告知客戶端該 Endpoint 何時會失效。
    *   **Communication**: 提前通知使用者（Email, Dev Portal）。
    *   **Monitoring**: 監控舊版 API 的流量，主動聯繫仍在使用的高流量客戶。
    *   **Brownouts**: 在正式關閉前，進行短暫的「計畫性停機測試」（Brownouts），讓忽略通知的客戶端感知到問題。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **RMM Level 2 是基準**：確保正確使用 HTTP Verbs 與 Status Codes 是資深工程師的基本功。
2.  **Versioning 是必修課**：一旦 API 發布給外部使用，就必須考慮版本控制。URI Versioning 是最實用的選擇。
3.  **HATEOAS 視情境而定**：對於 Public API 或高度解耦的系統很有價值，但對於內部緊密耦合的 App 可能是過度設計。
4.  **Router 隔離**：在 Express 中，利用 Router 模組化不同版本的邏輯，避免 `if-else` 汙染 Controller。
5.  **Content Negotiation**：理解 `Accept` 與 `Content-Type` headers 如何影響資料的表現形式。

## 後續延伸 (Next Steps)
*   **Next Chapter**: 深入探討 **Express 效能優化與快取策略 (Performance Optimization & Caching Strategies)**，學習如何結合 Redis 與 HTTP Caching headers 來提升 API 響應速度。
*   **Action Item**: 檢查你目前專案中的 API，是否混用了 POST 來做查詢？是否在錯誤時回傳了 200？嘗試引入 `express-validator` 來標準化輸入驗證與錯誤回應。