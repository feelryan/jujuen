# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單體架構（Monolithic Architecture）中，安全性往往集中在單一入口（Gatekeeper）；但在微服務架構中，攻擊面（Attack Surface）隨著服務數量的增加而顯著擴大。對於資深工程師而言，挑戰不僅在於如何驗證使用者（Authentication），更在於如何在零信任（Zero Trust）環境下，安全地管理服務與服務之間的通訊（Service-to-Service Communication）。

In a monolithic architecture, security is often centralized at a single gatekeeper; however, in a microservices architecture, the attack surface expands significantly as the number of services grows. For senior engineers, the challenge lies not only in authenticating users (Authentication) but also in securely managing Service-to-Service Communication within a Zero Trust environment.

完成本章後，你將能夠：

By the end of this chapter, you will be able to:

1.  **設計端到端的身份傳遞機制**：理解並實作如何在微服務鏈路中安全地傳遞 User Context（如 JWT Propagation）。
    **Design end-to-end identity propagation**: Understand and implement secure passing of User Context (e.g., JWT Propagation) across microservice chains.
2.  **實踐零信任架構（Zero Trust）**：運用 mTLS 與 SPIFFE/SPIRE 標準來確保服務間的身份驗證與加密。
    **Implement Zero Trust Architecture**: Utilize mTLS and SPIFFE/SPIRE standards to ensure service-to-service authentication and encryption.
3.  **區分並實作 AuthN 與 AuthZ**：清楚界定 API Gateway、Identity Provider (IdP) 與個別微服務在認證（AuthN）與授權（AuthZ）上的職責邊界。
    **Distinguish and implement AuthN vs. AuthZ**: Clearly define the responsibility boundaries for Authentication (AuthN) and Authorization (AuthZ) among the API Gateway, Identity Provider (IdP), and individual microservices.
4.  **解決 Token 撤銷與效能問題**：掌握 JWT 的緩存策略、JWKS 驗證流程以及 Token Revocation 的實務解法。
    **Solve Token revocation and performance issues**: Master JWT caching strategies, JWKS validation flows, and practical solutions for Token Revocation.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 城堡與飯店模型 (The Castle vs. The Hotel Model)

-   **單體架構像是一座城堡（The Castle）**：
    只要你通過了護城河與城門（Login），你在城堡內部通常是受信任的，可以自由訪問大部分房間（Function Calls）。
    **Monolithic Architecture is like a Castle**: Once you pass the moat and the main gate (Login), you are generally trusted inside the castle and can freely access most rooms (Function Calls).

-   **微服務架構像是一間現代化飯店（The Hotel）**：
    進入大廳（API Gateway）只是第一步。要進入電梯、健身房或你的房間（Individual Services），你每次都需要刷房卡（Token/Certificate）。飯店員工（Other Services）進入你的房間打掃也需要特定的授權卡。這就是**深度防禦（Defense in Depth）**。
    **Microservices Architecture is like a Modern Hotel**: Entering the lobby (API Gateway) is just the first step. To access the elevator, the gym, or your room (Individual Services), you need to swipe your keycard (Token/Certificate) every time. Hotel staff (Other Services) also need specific authorization cards to enter your room for cleaning. This is **Defense in Depth**.

### 2.2 關鍵術語對照 (Key Terminology Mapping)

| Concept | Definition | Microservices Context |
| :--- | :--- | :--- |
| **Identity Provider (IdP)** | 負責發行與管理身份的權威中心 (e.g., Auth0, Keycloak)。 | 簽發 JWT，作為所有服務信任的根源 (Root of Trust)。 |
| **OAuth2 / OIDC** | 授權與認證的標準協議。 | 前端與 Gateway 溝通的標準；OIDC 提供身份資訊 (ID Token)，OAuth2 提供授權 (Access Token)。 |
| **JWT (JSON Web Token)** | 包含簽名與 Claims 的無狀態 Token。 | 在服務間傳遞 User Context 的主要載體。 |
| **mTLS (Mutual TLS)** | 雙向 TLS 驗證，客戶端與伺服器互驗憑證。 | 確保「服務 A」真的是「服務 A」，並加密傳輸內容。 |
| **OPA (Open Policy Agent)** | 通用的策略引擎 (Policy Engine)。 | 將授權邏輯 (AuthZ) 從程式碼中抽離，以 Code 形式定義 Policy。 |

### 2.3 邊界安全性 vs. 零信任 (Edge Security vs. Zero Trust)

傳統思維依賴 **Perimeter Security**（邊界安全），認為內網是安全的。但在微服務與雲原生環境中，IP 是動態的，網路邊界是模糊的。
Traditional thinking relies on **Perimeter Security**, assuming the internal network is safe. However, in microservices and cloud-native environments, IPs are dynamic, and network boundaries are blurred.

**Zero Trust** 的核心原則是：**"Never Trust, Always Verify."**
The core principle of **Zero Trust** is: **"Never Trust, Always Verify."**
這意味著每一個 Request，無論來自外部使用者還是內部服務，都必須經過驗證、加密與授權。
This means every request, whether from an external user or an internal service, must be authenticated, encrypted, and authorized.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境的系統設計中，安全性通常分為三個層次來處理：

In production system design, security is typically handled at three layers:

### 3.1 Edge Layer (API Gateway / Ingress)
-   **職責 (Role)**：TLS Termination、將 Public Token (Opaque/Reference Token) 轉換為 Internal Token (JWT)、初步的 Rate Limiting 與黑名單過濾。
-   **設計考量 (Design Consideration)**：Gateway 是第一道防線，通常會在此處與 IdP 互動，驗證使用者的 `Access Token`。為了隱藏內部結構，對外可能使用不含個資的 Reference Token，對內則置換為包含 Claims 的 JWT。
-   **Role**: TLS Termination, exchanging Public Tokens (Opaque/Reference Tokens) for Internal Tokens (JWT), initial Rate Limiting, and Blacklist filtering.
-   **Design Consideration**: The Gateway is the first line of defense, usually interacting with the IdP here to validate the user's `Access Token`. To hide internal structure, Reference Tokens (without PII) might be used externally, exchanged for Claims-rich JWTs internally.

### 3.2 Service Mesh / Network Layer (Sidecar)
-   **職責 (Role)**：負責服務間的 mTLS 加密與身份識別（Service Identity）。
-   **設計考量 (Design Consideration)**：開發者不應在業務代碼中處理憑證交換。使用 Istio 或 Linkerd 等 Service Mesh，透過 Sidecar Proxy 自動處理 mTLS，對應用程式透明。
-   **Role**: Handles mTLS encryption and Service Identity between services.
-   **Design Consideration**: Developers should not handle certificate exchange in business code. Use a Service Mesh like Istio or Linkerd to handle mTLS automatically via Sidecar Proxies, making it transparent to the application.

### 3.3 Application Layer (Microservice)
-   **職責 (Role)**：細粒度的授權 (Fine-grained AuthZ)。
-   **設計考量 (Design Consideration)**：服務接收到 Request 後，需要檢查：
    1.  **JWT Signature**：Token 是否由受信任的 IdP 簽發？（透過 JWKS）
    2.  **Scopes/Roles**：該使用者是否有權執行此操作？（e.g., `write:orders`）
    3.  **Resource Ownership**：該使用者是否擁有這筆資料？（e.g., User 123 cannot delete User 456's order）。
-   **Role**: Fine-grained Authorization (AuthZ).
-   **Design Consideration**: Upon receiving a request, the service needs to check:
    1.  **JWT Signature**: Was the token signed by a trusted IdP? (via JWKS)
    2.  **Scopes/Roles**: Does the user have permission to perform this action? (e.g., `write:orders`)
    3.  **Resource Ownership**: Does the user own this data? (e.g., User 123 cannot delete User 456's order).

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例：Token Propagation 與 mTLS 在訂單系統中的應用
### Scenario: Token Propagation and mTLS in an Order System

**背景 (Context)**：
使用者透過 Mobile App 發起「建立訂單」請求。請求經過 API Gateway，轉發給 `Order Service`，`Order Service` 需要同步呼叫 `Inventory Service` 扣減庫存。

**Context**:
A user initiates a "Create Order" request via a Mobile App. The request goes through the API Gateway, is forwarded to the `Order Service`, which then needs to synchronously call the `Inventory Service` to deduct stock.

#### Step 1: 初始請求與 Gateway 處理 (Initial Request & Gateway)

使用者發送帶有 OAuth2 Access Token 的請求。
The user sends a request with an OAuth2 Access Token.

```http
POST /orders
Authorization: Bearer <Opaque_Token_From_Client>
```

**Gateway 行為**：
1.  呼叫 IdP (e.g., Redis/Database check) 驗證 Opaque Token。
2.  換取一個短時效的 **Stateless JWT**，內含 `sub: user_123`, `roles: [customer]`, `scopes: [order:write]`。
3.  將 JWT 放入 Header 轉發給 `Order Service`。

**Gateway Action**:
1.  Calls IdP (e.g., Redis/Database check) to validate the Opaque Token.
2.  Exchanges it for a short-lived **Stateless JWT** containing `sub: user_123`, `roles: [customer]`, `scopes: [order:write]`.
3.  Injects the JWT into the Header and forwards it to the `Order Service`.

#### Step 2: 服務間通訊 - mTLS (Service-to-Service - mTLS)

當 Gateway 連線到 `Order Service`，以及 `Order Service` 連線到 `Inventory Service` 時，連線層級由 mTLS 保護。

When the Gateway connects to the `Order Service`, and the `Order Service` connects to the `Inventory Service`, the connection layer is protected by mTLS.

*   **Identity**: `spiffe://my-cluster/ns/default/sa/order-service`
*   **Verification**: Sidecar (Envoy) 驗證對方的 X.509 憑證。如果憑證無效，連線直接被拒絕 (TCP Reset)。

#### Step 3: 身份傳遞與授權 (Identity Propagation & AuthZ)

`Order Service` 需要呼叫 `Inventory Service`。這裡有一個常見的設計決策：**我們應該傳遞誰的身份？**

`Order Service` needs to call `Inventory Service`. Here lies a common design decision: **Whose identity should we propagate?**

*   **Option A (User Identity)**: 傳遞原始使用者的 JWT。
*   **Option B (Service Identity)**: 使用 Client Credentials Flow 獲取 `Order Service` 自己的 Token。
*   **Best Practice (Hybrid)**: **Token Relay**。傳遞使用者的 JWT（為了審計與資源歸屬），同時底層 mTLS 確保了呼叫者是 `Order Service`。

**Inventory Service 的檢查邏輯 (Pseudo-code)**:

```java
// InventoryController.java

public void deductStock(@RequestHeader("Authorization") String authHeader) {
    // 1. Validate JWT (AuthN)
    // Usually handled by a Filter/Middleware utilizing JWKS
    Jwt token = jwtValidator.validate(authHeader); 
    
    // 2. Check Scopes (AuthZ - Coarse Grained)
    if (!token.getScopes().contains("inventory:write")) {
        throw new ForbiddenException("Token missing scope inventory:write");
    }

    // 3. Business Logic AuthZ (Fine Grained)
    // Ensure the user is active, or specific business rules
    // Note: We also implicitly trust the Caller (Order Service) due to mTLS 
    // or Network Policies allowing Order -> Inventory traffic.
    
    inventoryManager.deduct(item, quantity);
}
```

#### 為什麼這樣做可行？ (Why this works?)
-   **可追溯性 (Traceability)**：`Inventory Service` 的 Log 會記錄是 `user_123` 發起的扣庫存操作，而不是泛泛的 `order-service`。
-   **安全性 (Security)**：即使駭客攻破了 `Order Service`，如果沒有合法使用者的 JWT，他也無法隨意操作 `Inventory Service` 的某些 User-Specific API。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 上帝 Token (The God Token)
-   **錯誤 (Pitfall)**：為了方便服務間溝通，創建一個永不過期且擁有 `admin` 權限的 Token，所有微服務都共用這個 Token 來呼叫彼此。
-   **影響 (Impact)**：一旦任何一個微服務被入侵，攻擊者就獲得了整個系統的超級權限。
-   **修正 (Fix)**：使用 **Least Privilege** 原則。服務間應使用專屬的 Service Account，或僅傳遞具有最小必要 Scope 的 User JWT。

### 5.2 同步驗證的效能陷阱 (The Synchronous Validation Trap)
-   **錯誤 (Pitfall)**：微服務每次收到 Request，都透過 HTTP 呼叫 IdP (e.g., `/oauth/introspect`) 來驗證 Token 有效性。
-   **影響 (Impact)**：造成巨大的延遲（Latency）與 IdP 的單點故障風險。
-   **修正 (Fix)**：使用 **JWT + JWKS (JSON Web Key Set)**。微服務在啟動時（或定期）快取 IdP 的 Public Key，在本地進行簽名驗證（CPU bound, fast），無需網路呼叫。

### 5.3 混淆 AuthN 與 AuthZ (Mixing AuthN and AuthZ)
-   **錯誤 (Pitfall)**：在每個微服務的業務邏輯中寫死「如果是 User A，則允許...」。
-   **影響 (Impact)**：授權邏輯分散，難以稽核與變更。
-   **修正 (Fix)**：
    -   **AuthN**：由 Gateway 或 Sidecar 統一處理。
    -   **AuthZ**：使用 **OPA (Open Policy Agent)** 或類似的 Policy Engine，將授權規則抽離成設定檔（Policy-as-Code）。

### 5.4 忽略內部網路加密 (Ignoring Internal Encryption)
-   **錯誤 (Pitfall)**：認為 VPC 內部是安全的，服務間使用 HTTP 明文傳輸。
-   **影響 (Impact)**：內部惡意員工或被攻陷的容器可以輕易進行中間人攻擊 (MITM) 或封包側錄 (Sniffing)。
-   **修正 (Fix)**：全面實施 mTLS。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在微服務中，如何處理 JWT 的撤銷 (Revocation)？JWT 不是無狀態的嗎？
**How do you handle JWT revocation in microservices? Isn't JWT stateless?**

*   **高分回答要點 (Key Points)**：
    *   承認 JWT 本質是無狀態的，一旦簽發，在過期前都有效。
    *   **短時效 (Short TTL)**：將 Access Token 時效設短（e.g., 5-15 分鐘），依賴 Refresh Token 來獲取新 Token。撤銷時只需撤銷 Refresh Token。
    *   **Distributed Caching (Blacklist)**：對於緊急撤銷，將 Token ID (JTI) 放入 Redis 黑名單，Gateway 或 Sidecar 檢查時會比對。
    *   **Push Events**：IdP 發送 Webhook 通知各服務（較複雜，較少用）。

### Q2: 比較 "Pass-by-Value" (JWT) 與 "Pass-by-Reference" (Opaque Token) 在微服務內部的優缺點。
**Compare "Pass-by-Value" (JWT) vs. "Pass-by-Reference" (Opaque Token) within microservices.**

*   **高分回答要點 (Key Points)**：
    *   **JWT (Value)**：優點是自包含 (Self-contained)，服務無需查 DB 即可知曉使用者資訊，效能好，擴展性高。缺點是 Token 體積大，且無法立即撤銷。
    *   **Opaque (Reference)**：優點是安全性高（不暴露資訊）、可立即撤銷。缺點是每次都需要回查 IdP/DB，產生 "Chatty" 通訊，延遲高。
    *   **最佳實踐**：Gateway 對外使用 Opaque，Gateway 對內轉換成 JWT (Phantom Token Pattern)。

### Q3: 什麼是 "Confused Deputy" 問題？在微服務中如何防範？
**What is the "Confused Deputy" problem? How to prevent it in microservices?**

*   **高分回答要點 (Key Points)**：
    *   **定義**：一個擁有高權限的服務（Deputy）被惡意使用者誘導，去執行該使用者本無權執行的操作。例如：使用者 A 呼叫 Image Service，Image Service 有權讀取所有 S3 Bucket，使用者 A 誘導它讀取使用者 B 的照片。
    *   **防範**：必須傳遞 User Context (JWT)。Image Service 不應僅憑「我是 Image Service」就執行讀取，而應檢查「發起請求的 User ID 是否有權讀取該資源」。這就是為什麼 Service Identity (mTLS) 與 User Identity (JWT) 必須並存。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)
1.  **Zero Trust** 是微服務安全的黃金標準：預設不信任任何網路流量。
2.  **Gateway 是轉換樞紐**：對外使用 Opaque Token，對內轉換為 JWT 以提升效能。
3.  **mTLS + JWT**：mTLS 解決「你是哪個服務」的問題，JWT 解決「你是哪個使用者」的問題。兩者缺一不可。
4.  **Local Validation**：使用 JWKS 在本地驗證 Token 簽名，避免頻繁呼叫 IdP。
5.  **Policy as Code**：考慮引入 OPA 將複雜的授權邏輯從業務代碼中解耦。

### 後續延伸 (Next Steps)
-   **實作**：在 Kubernetes 環境中部署 Istio，並觀察 Sidecar 如何自動處理 mTLS。
-   **進階閱讀**：研究 **OAuth 2.0 Token Exchange (RFC 8693)**，這是處理微服務鏈式呼叫中身份轉換的標準協議。
-   **下一章預告**：**Chapter 08: Observability & Distributed Tracing**。安全性事件發生時，如果沒有完整的 Tracing，你將無法追蹤攻擊路徑。我們將探討如何結合 Security Logs 與 Tracing。