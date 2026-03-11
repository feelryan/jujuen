# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，設計 API 不僅僅是定義 URL 和 JSON 結構，更關乎如何優雅地管理變更（Change Management）與確保邊界安全（Security Perimeter）。在這一章，我們將探討如何讓 API 隨著業務需求演進而不破壞現有的客戶端應用，以及如何在分散式架構中正確實作身分驗證與授權。

As a Senior Engineer, designing an API is more than just defining URLs and JSON structures; it is fundamentally about elegant Change Management and securing the Security Perimeter. In this chapter, we will explore how to evolve APIs alongside business requirements without breaking existing client applications, and how to correctly implement authentication and authorization within a distributed architecture.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **制定版本控制策略**：評估 URI Versioning、Header Versioning 與 Content Negotiation 的優缺點，並根據系統需求選擇最適合的方案。
    **Formulate a versioning strategy**: Evaluate the trade-offs between URI Versioning, Header Versioning, and Content Negotiation, and select the most suitable approach based on system requirements.

2.  **處理破壞性變更（Breaking Changes）**：運用「擴充與收縮」（Expand and Contract）模式，在零停機（Zero Downtime）的前提下進行 API 與資料庫的遷移。
    **Handle breaking changes**: Apply the "Expand and Contract" pattern to perform API and database migrations with Zero Downtime.

3.  **設計安全的 AuthN/AuthZ 架構**：清楚區分 API Gateway 與微服務在 OAuth2/OIDC 流程中的職責，並理解 JWT 與 Opaque Token 的取捨。
    **Design a secure AuthN/AuthZ architecture**: Clearly distinguish the responsibilities of the API Gateway and microservices within OAuth2/OIDC flows, and understand the trade-offs between JWTs and Opaque Tokens.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 API 契約與承諾 (The API Contract & Promise)

API 應被視為一種「契約」（Contract）。當你發布一個 API 版本時，你實際上是對客戶端做出承諾：只要請求符合契約，回應就會符合預期。破壞性變更（Breaking Change）等同於違約。

An API should be viewed as a "Contract." When you release an API version, you are effectively making a promise to the client: as long as the request adheres to the contract, the response will meet expectations. A Breaking Change is equivalent to a breach of contract.

-   **向後相容 (Backward Compatibility)**: 新的程式碼可以接受舊的資料或請求格式。這是 API 演進的黃金法則。
    **Backward Compatibility**: New code can accept old data or request formats. This is the golden rule of API evolution.
-   **向前相容 (Forward Compatibility)**: 舊的程式碼（客戶端）可以優雅地處理（通常是忽略）新的資料欄位。這需要客戶端配合（例如 JSON parser 設定為忽略未知欄位）。
    **Forward Compatibility**: Old code (clients) can gracefully handle (usually by ignoring) new data fields. This requires client cooperation (e.g., JSON parsers configured to ignore unknown properties).

## 2.2 AuthN vs. AuthZ

面試與實務中常混淆這兩個概念。簡單的心智模型如下：
These two concepts are often confused in interviews and practice. A simple mental model is:

-   **Authentication (AuthN - 你是誰?)**: 驗證使用者的身分。類比：飯店櫃檯檢查你的護照並給你房卡。
    **Authentication (AuthN - Who are you?)**: Verifying the user's identity. Analogy: The hotel front desk checks your passport and gives you a key card.
-   **Authorization (AuthZ - 你能做什麼?)**: 驗證使用者是否有權限執行特定動作。類比：電梯讀卡機檢查你的房卡是否能按頂樓總統套房的按鈕。
    **Authorization (AuthZ - What can you do?)**: Verifying if the user has permission to perform a specific action. Analogy: The elevator card reader checks if your key card allows you to press the button for the penthouse suite.

## 2.3 API Gateway 的角色 (The Role of API Gateway)

API Gateway 是系統的「保全兼接待員」（Bouncer & Receptionist）。它負責處理橫切關注點（Cross-cutting Concerns），讓後端服務專注於業務邏輯。

The API Gateway acts as the system's "Bouncer & Receptionist." It handles Cross-cutting Concerns, allowing backend services to focus on business logic.

-   **職責 (Responsibilities)**: SSL Termination, Rate Limiting, AuthN (驗證 Token 簽章), Request Routing, Logging.
-   **非職責 (Non-Responsibilities)**: 複雜的業務邏輯、資料庫交易處理。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 版本控制策略的選擇 (Choosing a Versioning Strategy)

在 System Design 面試或架構規劃時，沒有絕對正確的版本控制方式，只有最適合的權衡：

In System Design interviews or architectural planning, there is no absolutely correct versioning method, only the most suitable trade-off:

1.  **URI Versioning (`/v1/users`)**:
    -   **Pros**: 直觀、易於除錯、瀏覽器友善、CDN 快取設定簡單。
    -   **Cons**: 破壞了 REST 的「資源恆定」原則（同一個 User 資源不應有多個 URI）。
    -   **Verdict**: **業界最常用**（Stripe, Twitter/X, Google APIs）。實務上最務實的選擇。

2.  **Header Versioning (`Accept: application/vnd.company.v1+json`)**:
    -   **Pros**: 符合 REST 原則，URI 保持乾淨。
    -   **Cons**: 測試較麻煩（無法直接用瀏覽器網址列）、CDN 設定較複雜（需根據 Header Vary）。
    -   **Verdict**: GitHub 使用此方式。適合對 REST 純度有極高要求的團隊。

## 3.2 安全架構：Phantom Token 模式 (Security Architecture: The Phantom Token Pattern)

在微服務架構中，直接將龐大的 JWT 暴露給公網（Public Internet）存在風險（包含 PII 資訊、Token 體積大浪費頻寬）。資深架構師常採用 **Phantom Token** 模式：

In microservices architectures, exposing bulky JWTs directly to the public internet poses risks (containing PII, wasting bandwidth due to size). Senior architects often adopt the **Phantom Token** pattern:

1.  **Client to Gateway**: 客戶端持有 **Opaque Token**（不透明的隨機字串，Reference Token）。體積小，無業務資訊。
    **Client to Gateway**: The client holds an **Opaque Token** (a random string, Reference Token). It is small and contains no business information.
2.  **Gateway Processing**: Gateway 接收 Opaque Token，向 Identity Provider (IdP) 換取（Introspection）包含完整 Claims 的 **JWT**。
    **Gateway Processing**: The Gateway receives the Opaque Token and exchanges it (via Introspection) with the Identity Provider (IdP) for a **JWT** containing full Claims.
3.  **Gateway to Service**: Gateway 將 JWT 附加在 Header 轉發給內部微服務。內部服務無須再呼叫 IdP，只需驗證 JWT 簽章（Stateless）。
    **Gateway to Service**: The Gateway attaches the JWT to the header and forwards it to internal microservices. Internal services do not need to call the IdP again; they only need to verify the JWT signature (Stateless).

這種設計兼顧了外部安全性（可隨時撤銷 Opaque Token）與內部效能（JWT 無狀態驗證）。

This design balances external security (Opaque Tokens can be revoked instantly) and internal performance (JWT stateless verification).

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 處理 Breaking Change：擴充與收縮 (Handling Breaking Changes: Expand and Contract)

假設我們有一個 API `GET /users/{id}`，回傳結構如下，現在需將 `fullName` 拆分為 `firstName` 與 `lastName`。

Suppose we have an API `GET /users/{id}` with the following response structure, and we need to split `fullName` into `firstName` and `lastName`.

**Initial State (v1):**
```json
{
  "id": "123",
  "fullName": "John Doe"
}
```

### Step 1: Expand (Add new fields, Keep old field)
修改資料庫與 API，新增欄位，但在 API 回應中**同時保留**舊欄位。若資料庫已拆分，API 層需負責組裝舊欄位。

Modify the database and API to add the new fields, but **retain** the old field in the API response. If the database is already split, the API layer must be responsible for assembling the old field.

```typescript
// Response DTO
interface UserResponse {
  id: string;
  fullName: string; // Deprecated, but populated
  firstName: string; // New
  lastName: string;  // New
}

// Logic
function mapUser(user: UserEntity): UserResponse {
  return {
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName,
    fullName: `${user.firstName} ${user.lastName}` // Backward compatibility
  };
}
```

### Step 2: Observe & Notify (Deprecation)
在 Response Header 加入 `Deprecation` 或 `Sunset` 資訊，並通知客戶端遷移。監控 Logs，觀察還有誰在使用 `fullName`。

Add `Deprecation` or `Sunset` information to the Response Header and notify clients to migrate. Monitor logs to see who is still using `fullName`.

```http
Warning: 299 - "fullName is deprecated. Use firstName and lastName instead."
```

### Step 3: Contract (Remove old field in v2)
當確認流量極低或達到 Sunset 日期後，推出 v2 API 移除該欄位，或者在 v1 中正式移除（視合約嚴格程度而定）。

Once traffic is confirmed to be minimal or the Sunset date is reached, roll out v2 API removing the field, or formally remove it in v1 (depending on contract strictness).

## 4.2 實作 JWT 驗證 Middleware (Implementing JWT Validation Middleware)

這是一個在 API Gateway 或 Service 層級常見的驗證邏輯（Node.js/Express 範例）。

This is a common validation logic at the API Gateway or Service level (Node.js/Express example).

```typescript
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';

// 1. Setup JWKS client (fetch public keys from IdP like Auth0/Cognito)
const client = jwksClient({
  jwksUri: 'https://my-auth-server/.well-known/jwks.json'
});

function getKey(header, callback) {
  client.getSigningKey(header.kid, (err, key) => {
    const signingKey = key.getPublicKey();
    callback(null, signingKey);
  });
}

// 2. Middleware
export const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Missing or invalid token' });
  }

  const token = authHeader.split(' ')[1];

  // Verify: Signature, Expiration, Audience, Issuer
  jwt.verify(token, getKey, {
    audience: 'https://api.myapp.com',
    issuer: 'https://auth.myapp.com/'
  }, (err, decoded) => {
    if (err) {
      // Differentiate between expired and invalid for debugging (but maybe not for client)
      console.error('Token verification failed:', err.message);
      return res.status(401).json({ message: 'Invalid token' });
    }

    // Attach user context (Claims) to request for downstream logic
    req.user = {
      id: decoded.sub,
      roles: decoded['https://myapp.com/roles'] || [],
      scope: decoded.scope
    };
    
    next();
  });
};
```

**Key Takeaway**: 永遠不要只解碼（decode）JWT，一定要驗證（verify）簽章與 Claims（exp, iss, aud）。
**Key Takeaway**: Never just decode a JWT; always verify the signature and Claims (exp, iss, aud).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 God Object Gateway (上帝物件閘道器)

-   **錯誤 (Pitfall)**: 在 API Gateway 中編寫大量業務邏輯（如資料聚合、複雜轉換）。
    **Pitfall**: Writing extensive business logic (e.g., data aggregation, complex transformations) within the API Gateway.
-   **後果 (Consequence)**: Gateway 變成單體瓶頸（Monolithic Bottleneck），難以測試與部署。一旦 Gateway 掛掉，全站癱瘓。
    **Consequence**: The Gateway becomes a Monolithic Bottleneck, difficult to test and deploy. If the Gateway goes down, the entire site is paralyzed.
-   **解法 (Solution)**: Gateway 應保持輕量（Routing, Auth, Rate Limiting）。若需聚合資料，使用 **BFF (Backend for Frontend)** 模式或 GraphQL Aggregation Layer。
    **Solution**: Keep the Gateway lightweight (Routing, Auth, Rate Limiting). If data aggregation is needed, use the **BFF (Backend for Frontend)** pattern or a GraphQL Aggregation Layer.

## 5.2 濫用 JWT 儲存 Session 資料 (Abusing JWT for Session Data)

-   **錯誤 (Pitfall)**: 將大量使用者偏好設定、購物車內容塞入 JWT payload。
    **Pitfall**: Stuffing user preferences, shopping cart contents, etc., into the JWT payload.
-   **後果 (Consequence)**: 
    1.  Header 過大，超過 HTTP 限制或增加延遲。
    2.  資料過期問題：JWT 一旦簽發，內容即不可變。若使用者更新了偏好，舊 Token 內的資料就是錯的。
    **Consequence**:
    1.  Headers become too large, exceeding HTTP limits or increasing latency.
    2.  Stale data issues: Once a JWT is signed, its content is immutable. If the user updates preferences, the data in the old Token is incorrect.
-   **解法 (Solution)**: JWT 只存身分識別（ID）與核心權限（Roles/Scopes）。其他資料請查詢 Database 或 Cache。
    **Solution**: Store only identity (ID) and core permissions (Roles/Scopes) in the JWT. Query the Database or Cache for other data.

## 5.3 混淆 401 與 403 (Confusing 401 vs 403)

-   **錯誤 (Pitfall)**: 當使用者權限不足時回傳 401 Unauthorized。
    **Pitfall**: Returning 401 Unauthorized when the user lacks sufficient permissions.
-   **定義 (Definition)**:
    -   **401 Unauthorized**: "I don't know who you are." (Authentication failed).
    -   **403 Forbidden**: "I know who you are, but you can't do this." (Authorization failed).
-   **影響 (Impact)**: 前端無法區分是該「跳轉登入頁面」（401）還是「顯示權限不足錯誤訊息」（403）。
    **Impact**: The frontend cannot distinguish whether to "redirect to the login page" (401) or "show an insufficient permissions error message" (403).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何處理 JWT 的即時撤銷（Revocation）問題？
**How do you handle immediate revocation of JWTs?**

*   **情境**: JWT 是無狀態的（Stateless），一旦發出，在過期前都有效。如果使用者手機遺失或被盜號，如何讓 Token 立即失效？
    **Scenario**: JWTs are stateless; once issued, they are valid until expiration. If a user loses their phone or is hacked, how do you invalidate the Token immediately?
*   **高分回答要點 (Key Points)**:
    1.  **Short Lived Access Token**: 設定極短的過期時間（如 5-15 分鐘），配合 Long Lived Refresh Token。
    2.  **Deny List (Blacklist)**: 在 Cache (Redis) 中維護一份「已撤銷的 JTI (JWT ID)」清單，Gateway 驗證時多查一次 Cache（犧牲一點無狀態特性換取安全）。
    3.  **Version/Generation ID**: 在 User DB 和 JWT Claims 中都存一個 `token_version`。驗證時比對，若使用者登出或改密碼，增加 DB 中的 version，舊 Token 即失效。

## Q2: 在微服務架構中，Rate Limiting 應該放在哪裡？
**Where should Rate Limiting be placed in a microservices architecture?**

*   **高分回答要點 (Key Points)**:
    1.  **Global/Gateway Level**: 防止 DDoS，保護整個系統入口。通常基於 IP 或 API Key。
    2.  **Service Level**: 保護特定微服務不被壓垮（例如某個重運算的 Report Service）。
    3.  **演算法**: 提及 Token Bucket 或 Leaky Bucket。
    4.  **分散式挑戰**: 提到使用 Redis (Lua script) 來同步分散式 Gateway 節點間的計數器，避免 Race Condition。

## Q3: 什麼時候該為 API 引入新的版本（v2）？
**When should you introduce a new version (v2) for an API?**

*   **高分回答要點 (Key Points)**:
    1.  **Breaking Changes**: 只有在無法維持向後相容時才升版。新增欄位不應升版。
    2.  **語義改變**: 即使欄位名稱沒變，但欄位的意義或單位改變了（例如距離從 miles 變 km）。
    3.  **資源結構重構**: 資源之間的關係發生根本變化。
    4.  **避免過度版本化**: 解釋為何頻繁升版會造成維護地獄（Documentation rot, Backporting fixes）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **API 是契約**：任何變更都應優先考慮向後相容性（Backward Compatibility）。
    **API is a Contract**: Any change should prioritize Backward Compatibility.
2.  **擴充與收縮 (Expand & Contract)**：是處理資料庫與 API 遷移的標準零停機模式。
    **Expand & Contract**: The standard zero-downtime pattern for database and API migrations.
3.  **AuthN vs AuthZ**：Gateway 處理 AuthN（驗證 Token），微服務處理 AuthZ（基於 Claims 的權限判斷）。
    **AuthN vs AuthZ**: The Gateway handles AuthN (validating Tokens), while microservices handle AuthZ (Claims-based permission logic).
4.  **JWT 安全**：驗證簽章、檢查過期時間、不要放入敏感資料、考慮撤銷機制。
    **JWT Security**: Verify signatures, check expiration, do not include sensitive data, and consider revocation mechanisms.
5.  **Gateway 職責**：專注於橫切關注點（Routing, Throttling, Security），避免包含業務邏輯。
    **Gateway Responsibilities**: Focus on cross-cutting concerns (Routing, Throttling, Security) and avoid business logic.

## 後續延伸 (Next Steps)

-   **Next Chapter**: **API Performance & Caching**。學習 HTTP Caching (ETag, Cache-Control)、GraphQL 的 N+1 問題優化，以及 DB Indexing 策略。
-   **Action Item**: 檢視你目前的專案，是否有暴露過多資訊在 JWT 中？你的 API 是否有明確的 Deprecation Policy？嘗試實作一個簡單的 Rate Limiter Middleware。