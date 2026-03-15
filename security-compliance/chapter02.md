# 1. 前言與學習目標 (Introduction & Learning Objectives)

在分散式系統與微服務架構中，身份驗證（Authentication, AuthN）與授權（Authorization, AuthZ）是安全性的基石。對於資深工程師而言，挑戰不僅在於「如何實作登入」，而在於如何設計一個既能滿足安全合規要求，又能兼顧效能與開發者體驗（DX）的 IAM（Identity and Access Management）架構。

In distributed systems and microservices architectures, Authentication (AuthN) and Authorization (AuthZ) are the cornerstones of security. For a Senior Engineer, the challenge is not just "how to implement login," but how to design an IAM (Identity and Access Management) architecture that meets security compliance requirements while balancing performance and Developer Experience (DX).

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **清晰區分 AuthN 與 AuthZ 的邊界**：理解為何在現代架構中需將兩者解耦，以及 OAuth 2.0 與 OIDC（OpenID Connect）各自扮演的角色。
    **Clearly distinguish the boundaries between AuthN and AuthZ**: Understand why they must be decoupled in modern architectures, and the respective roles of OAuth 2.0 and OIDC (OpenID Connect).
2.  **評估 Token 機制與 Session 管理的取捨**：能夠在 Stateful Session 與 Stateless JWT 之間做出正確的架構決策，並解決 JWT 的撤銷（Revocation）難題。
    **Evaluate the trade-offs between Token mechanisms and Session management**: Make correct architectural decisions between Stateful Sessions and Stateless JWTs, and solve the JWT revocation challenge.
3.  **設計微服務的授權模型**：比較並實作 RBAC（Role-Based Access Control）與 ABAC（Attribute-Based Access Control），並了解何時引入 OPA（Open Policy Agent）等集中式策略引擎。
    **Design authorization models for microservices**: Compare and implement RBAC (Role-Based Access Control) versus ABAC (Attribute-Based Access Control), and understand when to introduce centralized policy engines like OPA (Open Policy Agent).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 AuthN vs. AuthZ：護照與門禁卡 (Passport vs. Key Card)

最直觀的心智模型是將 **AuthN** 視為「護照檢查」，而將 **AuthZ** 視為「門禁卡權限」。

The most intuitive mental model is to view **AuthN** as a "Passport Check" and **AuthZ** as "Key Card Permissions."

*   **Authentication (AuthN)**: 回答 "Who are you?"（你是誰？）。
    *   *機制*：密碼、MFA、生物辨識、OIDC ID Token。
    *   *Mechanism*: Passwords, MFA, Biometrics, OIDC ID Tokens.
*   **Authorization (AuthZ)**: 回答 "What can you do?"（你能做什麼？）。
    *   *機制*：OAuth Scopes、ACLs、RBAC 角色、ABAC 屬性。
    *   *Mechanism*: OAuth Scopes, ACLs, RBAC roles, ABAC attributes.

> **關鍵區別**：你可能通過了身份驗證（你是員工），但沒有授權（你不能刪除 Production 資料庫）。
> **Key Distinction**: You might be authenticated (you are an employee), but not authorized (you cannot delete the Production database).

## 2.2 OAuth 2.0 與 OIDC 的關係 (The Relationship between OAuth 2.0 and OIDC)

許多資深工程師常混淆這兩者。請記住：**OAuth 2.0 是授權框架，OIDC 是構建在 OAuth 2.0 之上的身份層。**

Many senior engineers confuse these two. Remember: **OAuth 2.0 is an authorization framework, while OIDC is an identity layer built on top of OAuth 2.0.**

*   **OAuth 2.0**: 專注於「委派授權」（Delegated Authorization）。例如：允許第三方 App 存取你的 Google Drive 檔案，而不給它你的 Google 密碼。它的產出是 **Access Token**。
    **OAuth 2.0**: Focuses on "Delegated Authorization." E.g., allowing a third-party app to access your Google Drive files without giving it your Google password. Its output is an **Access Token**.
*   **OIDC (OpenID Connect)**: 填補了 OAuth 2.0 缺乏「標準化身份資訊」的缺口。它的產出增加了 **ID Token**（通常是 JWT 格式），包含使用者的 Profile 資訊。
    **OIDC (OpenID Connect)**: Fills the gap where OAuth 2.0 lacks "standardized identity information." Its output adds an **ID Token** (usually in JWT format) containing the user's profile information.

## 2.3 授權模型：RBAC vs. ABAC (Authorization Models: RBAC vs. ABAC)

*   **RBAC (Role-Based Access Control)**:
    *   *定義*：權限綁定在「角色」上，使用者被分配角色。
    *   *適用*：大多數 B2B SaaS 系統（Admin, Editor, Viewer）。
    *   *缺點*：當規則變複雜（例如：「只能在上班時間存取」或「只能存取自己建立的資源」）時，會導致「角色爆炸」（Role Explosion）。
    *   *Definition*: Permissions are bound to "Roles," and users are assigned roles.
    *   *Use Case*: Most B2B SaaS systems (Admin, Editor, Viewer).
    *   *Drawback*: When rules get complex (e.g., "access only during work hours" or "access only own resources"), it leads to "Role Explosion."

*   **ABAC (Attribute-Based Access Control)**:
    *   *定義*：基於屬性（User, Resource, Environment）動態計算權限。
    *   *公式*：`If (User.Department == HR) AND (Resource.Type == Salary) AND (Time == OfficeHours) THEN Allow`。
    *   *適用*：高合規性需求、細粒度控制。
    *   *Definition*: Permissions are dynamically calculated based on attributes (User, Resource, Environment).
    *   *Formula*: `If (User.Department == HR) AND (Resource.Type == Salary) AND (Time == OfficeHours) THEN Allow`.
    *   *Use Case*: High compliance requirements, fine-grained control.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在單體架構（Monolith）中，AuthN/AuthZ 通常只是一個 Middleware 與 Session Table。但在微服務架構中，我們面臨「信任傳遞」的問題。

In a monolithic architecture, AuthN/AuthZ is usually just a Middleware and a Session Table. But in a microservices architecture, we face the problem of "Trust Propagation."

## 3.1 架構模式：API Gateway 與 Token 傳遞 (Architecture Pattern: API Gateway & Token Propagation)

在 Production 環境中，標準的設計模式如下：

In a Production environment, the standard design pattern is as follows:

1.  **Client (SPA/Mobile)**: 向 Identity Provider (IdP) 登入，取得 `Access Token` (JWT) 與 `Refresh Token`。
    **Client (SPA/Mobile)**: Logs in to the Identity Provider (IdP), obtaining an `Access Token` (JWT) and a `Refresh Token`.
2.  **API Gateway**:
    *   作為 TLS Termination 點。
    *   驗證 Token 簽章（Signature）與時效（Expiration）。
    *   (Optional) 將 JWT 轉換為內部 User Context Header（如 `X-User-ID`）傳給下游，避免下游服務重複解析 JWT。
    *   Acts as the TLS Termination point.
    *   Validates the Token Signature and Expiration.
    *   (Optional) Translates the JWT into internal User Context Headers (e.g., `X-User-ID`) for downstream services to avoid repetitive JWT parsing.
3.  **Microservices**:
    *   **AuthN**: 信任 Gateway 傳來的 Context 或自行驗證 JWT（零信任架構下推薦自行驗證）。
    *   **AuthZ**: 根據 Context 執行細粒度權限檢查（例如：檢查該 User ID 是否為資源擁有者）。
    *   **AuthN**: Trust the Context from the Gateway or validate the JWT themselves (self-validation is recommended in Zero Trust architectures).
    *   **AuthZ**: Perform fine-grained permission checks based on the Context (e.g., checking if the User ID is the resource owner).

## 3.2 集中式 vs. 分散式 PDP (Centralized vs. Decentralized PDP)

*PDP (Policy Decision Point)* 是決定「是否允許存取」的邏輯組件。

*PDP (Policy Decision Point)* is the logical component that decides "whether access is allowed."

*   **Library 模式 (Decentralized)**: 每個服務引入一個 Auth SDK。
    *   *優點*：效能好（In-process），無網路延遲。
    *   *缺點*：多語言支援困難，策略更新需重新部署服務。
    *   **Library Mode (Decentralized)**: Each service imports an Auth SDK.
    *   *Pros*: High performance (In-process), no network latency.
    *   *Cons*: Difficult to support multiple languages, policy updates require service redeployment.

*   **Sidecar/Service 模式 (Centralized Logic, Distributed Enforcement)**: 使用 OPA (Open Policy Agent) 作為 Sidecar。
    *   *優點*：策略（Policy）與程式碼（Code）解耦，可熱更新策略。
    *   *缺點*：增加了維運複雜度。
    *   **Sidecar/Service Mode (Centralized Logic, Distributed Enforcement)**: Using OPA (Open Policy Agent) as a Sidecar.
    *   *Pros*: Decouples Policy from Code, allows hot-reloading of policies.
    *   *Cons*: Increases operational complexity.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：設計一個具備「強制登出」功能的 JWT 架構
## Case: Designing a JWT Architecture with "Force Logout" Capability

**背景 (Context)**:
你正在將一個金融服務從 Session-based Monolith 遷移到 Microservices。安全團隊要求必須支援「當偵測到帳號異常時，能立即讓所有 Access Token 失效」。
You are migrating a financial service from a Session-based Monolith to Microservices. The security team requires support for "immediately invalidating all Access Tokens when account anomalies are detected."

**挑戰 (Challenge)**:
JWT 本質是 Stateless 的。一旦簽發，直到過期前都是有效的。如果 Access Token 有效期是 1 小時，駭客竊取後便擁有 1 小時的存取權，伺服器無法單方面撤銷。
JWTs are inherently Stateless. Once issued, they are valid until expiration. If an Access Token is valid for 1 hour, a hacker who steals it has 1 hour of access, and the server cannot unilaterally revoke it.

### 解決方案演進 (Solution Evolution)

#### 步驟 1：短效期 Access Token + Refresh Token (Short-lived Access Token + Refresh Token)
設定 Access Token 有效期極短（例如 5–15 分鐘）。
Set the Access Token expiration to be very short (e.g., 5–15 minutes).

*   **Client**: Access Token 過期後，使用 Refresh Token 向 IdP 換取新的 Access Token。
*   **Server**: 如果要封鎖使用者，只需在 DB/Cache 中撤銷其 Refresh Token。
*   **限制**: 仍有 5–15 分鐘的時間差（Time Window of Vulnerability）。
*   **Client**: When the Access Token expires, use the Refresh Token to exchange for a new Access Token from the IdP.
*   **Server**: To ban a user, simply revoke their Refresh Token in the DB/Cache.
*   **Limitation**: There is still a 5–15 minute time window of vulnerability.

#### 步驟 2：引入 Token Blacklist/Denylist (Introducing Token Blacklist/Denylist)
為了達到「立即」失效，我們必須在 Stateless 中引入一點 State。
To achieve "immediate" invalidation, we must introduce a bit of State into the Statelessness.

*   **機制**: 當使用者登出或被封鎖時，將該 Access Token 的 `jti` (JWT ID) 存入 Redis，並設定 TTL 等於 Token 的剩餘有效期。
*   **驗證流程**: API Gateway 驗證簽章後，額外檢查 Redis：`EXISTS blacklist:{jti}`。
*   **Mechanism**: When a user logs out or is banned, store the Access Token's `jti` (JWT ID) in Redis, setting the TTL equal to the token's remaining validity period.
*   **Validation Flow**: After verifying the signature, the API Gateway additionally checks Redis: `EXISTS blacklist:{jti}`.

#### 程式碼實作概念 (Implementation Concept - Python)

```python
import jwt
import redis
from datetime import datetime

# Redis connection for blacklist
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def validate_token(token_string, secret_key):
    try:
        # 1. Decode and validate signature & expiration (Stateless check)
        payload = jwt.decode(token_string, secret_key, algorithms=["HS256"])
        
        # 2. Check Blacklist (Stateful check)
        jti = payload.get("jti")
        if redis_client.exists(f"blacklist:{jti}"):
            raise Exception("Token has been revoked")
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def revoke_token(token_string, secret_key):
    """
    Called when user logs out or is banned
    """
    try:
        payload = jwt.decode(token_string, secret_key, algorithms=["HS256"])
        jti = payload.get("jti")
        exp_timestamp = payload.get("exp")
        
        # Calculate remaining TTL
        ttl = int(exp_timestamp - datetime.utcnow().timestamp())
        
        if ttl > 0:
            # Add to blacklist with TTL
            redis_client.setex(f"blacklist:{jti}", ttl, "revoked")
            
    except Exception as e:
        print(f"Error revoking token: {e}")
```

**分析 (Analysis)**:
這個混合方案（Hybrid Approach）在效能與安全性之間取得了平衡。大多數請求只需 CPU 運算（驗證簽章），只有需要高安全性的操作或 Gateway 層才去查 Redis。Redis 的負載僅限於「被撤銷且尚未過期」的 Token，數量遠小於所有活躍 Session。
This Hybrid Approach balances performance and security. Most requests only require CPU computation (signature verification). Only high-security operations or the Gateway layer need to check Redis. The load on Redis is limited to "revoked but not yet expired" tokens, which is far smaller than all active sessions.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 誤用 Access Token 作為 ID Token (Confusing Access Token with ID Token)
*   **錯誤**: 前端解碼 Access Token 來顯示使用者名稱或 Email。
*   **原因**: Access Token 的格式對 Client 來說應該是「不透明的（Opaque）」。雖然它常是 JWT，但標準並未強制。且 Access Token 是給 Resource Server 看的，內容可能隨時改變。
*   **正確**: 應該使用 OIDC 的 `ID Token` 來獲取使用者資訊，或呼叫 `/userinfo` endpoint。
*   **Mistake**: The frontend decodes the Access Token to display the username or email.
*   **Reason**: The format of the Access Token should be "Opaque" to the Client. Although it is often a JWT, the standard does not mandate it. Moreover, the Access Token is meant for the Resource Server, and its content may change.
*   **Correction**: Use the OIDC `ID Token` to get user information, or call the `/userinfo` endpoint.

## 5.2 上帝 Token (The "God Token")
*   **錯誤**: 在 JWT Payload 中塞入過多資料（如使用者的完整權限列表、群組資訊、偏好設定），導致 Header 過大（超過 HTTP Header 限制），且頻寬浪費。
*   **後果**: 增加每個 Request 的延遲；若權限變更，Token 無法即時反映。
*   **正確**: Token 僅包含 Identity (Sub) 與核心 Scopes。細粒度權限應由後端服務根據 ID 查詢或快取。
*   **Mistake**: Stuffing too much data into the JWT Payload (e.g., full permission lists, group info, preferences), causing bloated Headers (exceeding HTTP limits) and wasted bandwidth.
*   **Consequence**: Increases latency for every request; if permissions change, the Token cannot reflect them immediately.
*   **Correction**: The Token should only contain Identity (Sub) and core Scopes. Fine-grained permissions should be queried or cached by backend services based on the ID.

## 5.3 在業務邏輯中硬編碼授權 (Hardcoding AuthZ in Business Logic)
*   **錯誤**: `if (user.role == 'admin' || user.id == post.owner_id) { ... }` 散落在各個 Controller 中。
*   **後果**: 難以稽核（Audit），難以修改策略，容易遺漏檢查。
*   **正確**: 使用裝飾器（Decorators）、Middleware 或集中式策略引擎（如 OPA）。例如 `@RequirePermission('post:edit')`。
*   **Mistake**: `if (user.role == 'admin' || user.id == post.owner_id) { ... }` scattered across various Controllers.
*   **Consequence**: Hard to audit, hard to modify policies, easy to miss checks.
*   **Correction**: Use Decorators, Middleware, or centralized policy engines (like OPA). E.g., `@RequirePermission('post:edit')`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如果你的系統需要處理 B2B 客戶，每個客戶有自定義的角色權限，你會選擇 RBAC 還是 ABAC？
## Q1: If your system needs to handle B2B clients, and each client has custom role permissions, would you choose RBAC or ABAC?

*   **高分回答要點**:
    *   指出單純的 RBAC 不夠用，因為「角色」是客戶自定義的，不是系統寫死的。
    *   提出 **Hierarchical RBAC** 或 **RBAC + ABAC 混合模型**。
    *   解釋資料庫 Schema 設計：`Permissions` (原子權限) -> `CustomRoles` (客戶定義) -> `Users`。
    *   提到 **Tenant Isolation**（租戶隔離）在授權檢查中的重要性。
*   **Key Points for High Score**:
    *   Point out that simple RBAC is insufficient because "Roles" are defined by the client, not hardcoded by the system.
    *   Propose **Hierarchical RBAC** or a **Hybrid RBAC + ABAC model**.
    *   Explain Database Schema design: `Permissions` (Atomic) -> `CustomRoles` (Client Defined) -> `Users`.
    *   Mention the importance of **Tenant Isolation** in authorization checks.

## Q2: 請比較 JWT 與 Session Cookies 在安全性上的優劣。
## Q2: Please compare the security pros and cons of JWT vs. Session Cookies.

*   **高分回答要點**:
    *   **XSS**: 兩者都可能受 XSS 影響，但如果 JWT 存在 `localStorage`，更容易被竊取。Cookie 若設定 `HttpOnly` 則較難被 JS 讀取。
    *   **CSRF**: Cookie 天生易受 CSRF 攻擊（需配合 SameSite 或 CSRF Token 防禦）；JWT 若放在 Header (`Authorization: Bearer`) 則天然免疫 CSRF。
    *   **Revocation**: Session Cookie 容易撤銷（Server 刪除 Session 即可）；JWT 難撤銷（需 Blacklist）。
*   **Key Points for High Score**:
    *   **XSS**: Both are vulnerable, but if JWT is stored in `localStorage`, it's easier to steal. Cookies with `HttpOnly` are harder for JS to read.
    *   **CSRF**: Cookies are inherently vulnerable to CSRF (require SameSite or CSRF Token); JWTs in Headers (`Authorization: Bearer`) are immune to CSRF.
    *   **Revocation**: Session Cookies are easy to revoke (Server deletes Session); JWTs are hard to revoke (require Blacklist).

## Q3: 什麼是 Google Zanzibar？它解決了什麼問題？
## Q3: What is Google Zanzibar? What problem does it solve?

*   **高分回答要點**:
    *   Zanzibar 是 Google 的全球一致性授權系統（Global Consistent Authorization System）。
    *   它解決了 **ReBAC (Relationship-Based Access Control)** 問題，特別是像 Google Drive 這種大量「分享」、「繼承」與「巢狀群組」的場景。
    *   核心是將權限視為圖（Graph）遍歷問題，並利用 Spanner 資料庫保證一致性。
    *   開源實作參考：OpenFGA, SpiceDB。
*   **Key Points for High Score**:
    *   Zanzibar is Google's Global Consistent Authorization System.
    *   It solves **ReBAC (Relationship-Based Access Control)** problems, especially for scenarios like Google Drive with massive "sharing," "inheritance," and "nested groups."
    *   The core idea is treating authorization as a Graph traversal problem and using Spanner DB for consistency.
    *   Open Source implementations: OpenFGA, SpiceDB.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **AuthN != AuthZ**: 驗證是檢查身份，授權是檢查權限。OAuth 2.0 用於授權，OIDC 用於身份驗證。
2.  **Stateless 的代價**: JWT 帶來了擴展性，但犧牲了即時撤銷的能力。使用 Short-lived Token + Refresh Token + Blacklist 是標準解法。
3.  **Gateway Pattern**: 在 Gateway 統一處理 AuthN，下游微服務專注於 AuthZ。
4.  **Decouple Policy**: 盡量將授權邏輯從業務代碼中抽離（如使用 OPA 或 Middleware）。
5.  **Token Security**: 不要將敏感數據放入 JWT Payload，並始終驗證簽章與 `aud` / `iss`。

## 後續延伸 (Next Steps)
*   **實作練習**: 使用 Keycloak 或 Auth0 搭建一個 OIDC Provider，並實作一個保護的 API。
*   **進階閱讀**: 研究 **Google Zanzibar** 論文，了解大規模 ACL 系統的設計。
*   **下一章預告**: `Infrastructure Security` (Chapter 03) — 我們將探討 mTLS、Secrets Management (Vault) 與雲端安全設定。