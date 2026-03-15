# 安全架構設計模式 / Security Architecture Patterns

## Mental model｜心智模型

在現代分佈式系統中，安全不再是單一的「邊界防護」（Perimeter Security），而是必須深入到架構的每一個環節。理解安全架構時，請建立以下兩個核心思維：

### 1. 縱深防禦 (Defense in Depth) 與 瑞士起司模型
不要依賴單一的防火牆或 API Gateway。想像安全措施是一層層的瑞士起司，每一層都有漏洞（孔洞），但只要將不同層疊加，就能擋住穿透的威脅。
- **Layer 1 (Edge):** DDoS 防護、WAF。
- **Layer 2 (Gateway):** 身份驗證 (AuthN)、速率限制 (Rate Limiting)。
- **Layer 3 (Service):** 服務間授權 (AuthZ)、商業邏輯驗證。
- **Layer 4 (Data):** 加密儲存、備份。

### 2. 零信任架構 (Zero Trust)
**"Never Trust, Always Verify."**
過去的思維是「內網即安全」（Hard shell, soft center），現在的思維是假設內網已經被攻破。
- **Identity-based:** 服務之間的通訊不認 IP，只認身份（Identity），通常透過 mTLS 憑證實現。
- **Least Privilege:** 服務 A 只能呼叫服務 B 的特定 API，且必須有明確的 Policy 定義。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. API Gateway as the "Grand Entry"
**API Gateway 作為統一的安全切入點**
API Gateway 不僅是路由，更是第一道安全防線。
- **Offloading (卸載):** 將 SSL Termination、CORS 處理、基礎 AuthN (驗證 Token 簽章) 統一在 Gateway 處理，減輕後端微服務負擔。
- **Rate Limiting:** 針對 IP 或 User ID 進行限流，防止暴力破解或 DoS。
- **Input Sanitization:** 在入口處過濾明顯的惡意 Payload (如 SQL Injection 特徵)。

### 2. BFF (Backend for Frontend) Pattern for Security
**為不同前端定製的安全層**
當你有 Web、Mobile App、Third-party Client 時，不要讓它們共用同一個安全邏輯。
- **Token Handling:**
  - **Web:** 瀏覽器不應直接持有 Access Token。BFF 負責與瀏覽器交換 `HttpOnly` + `Secure` Cookie，並在 BFF 層將 Cookie 轉換為 JWT (Bearer Token) 發送給後端服務。這能有效防禦 XSS 竊取 Token。
  - **Mobile:** 可以直接持有 Token，但需搭配 Certificate Pinning。
- **Data Minimization:** BFF 只回傳該前端介面需要的資料，減少資料外洩風險（避免 "Over-fetching" 導致敏感欄位洩漏）。

### 3. Service Mesh & mTLS (Mutual TLS)
**服務間的加密與身份驗證**
在微服務架構中，如何確保 Service A 呼叫 Service B 是合法的？
- **Encryption in Transit:** 透過 Sidecar (如 Envoy) 自動處理流量加密，開發者無需在程式碼中實作 SSL。
- **Strong Identity:** 每個服務實例啟動時獲取短效期憑證 (SVID)，通訊時雙向驗證。
- **Traffic Splitting & Shadowing:** 安全地進行灰度發布，降低新版本引入安全漏洞的影響範圍。

### 4. Sidecar Pattern for Policy Enforcement (OPA)
**將授權邏輯抽離**
不要將複雜的 RBAC/ABAC 邏輯寫死在業務程式碼中。
- 使用 **Open Policy Agent (OPA)** 作為 Sidecar。
- 業務服務收到請求時，詢問 Sidecar：「這個 User 可以對這個 Resource 做這個 Action 嗎？」
- 優點：安全策略 (Policy) 可以獨立於程式碼進行版控、部署和熱更新。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Soft Center" (內網裸奔)
- **現象：** 認為過了 API Gateway 就是安全區域，內部服務之間使用 HTTP 明文傳輸，且沒有再次驗證身份。
- **後果：** 一旦攻擊者攻破任一服務（如 SSRF 漏洞），就能在內網橫向移動，隨意呼叫其他敏感服務。

### 2. Logic Coupling (安全邏輯與業務邏輯耦合)
- **現象：** 在每個 Controller/Handler 裡面寫 `if (user.role == 'admin') ...`。
- **後果：** 難以稽核，容易遺漏，且當安全需求變更（例如新增 'super-admin'）時，需要修改大量程式碼並重新部署。

### 3. Passing Raw User Context Blindly
- **現象：** Gateway 驗證完 Token 後，直接把 User Object 序列化傳給後端，後端完全信任該物件。
- **風險：** 如果中間某個服務被竄改，它可以偽造 User Context 欺騙下游服務。應傳遞簽名過的 Token (Internal JWT) 或透過 mTLS 確保呼叫鏈可信。

### 4. DIY Cryptography in Gateway
- **現象：** 自己刻 Gateway 邏輯來處理加密或複雜的 Auth 流程。
- **建議：** 使用成熟的解決方案 (Kong, Nginx, Istio, AWS API Gateway)。**Don't roll your own crypto, don't roll your own gateway core.**

---

## Checklists & workflows｜檢查清單與流程

在設計系統架構或進行 Code Review 時，請使用此清單：

### Architecture Review Checklist
- [ ] **邊界防護：** 是否所有外部流量都強制經過 API Gateway？是否有配置 WAF？
- [ ] **通訊加密：**
  - [ ] 外部到內部 (Ingress) 是否強制 HTTPS？
  - [ ] 內部服務之間 (East-West) 是否啟用 mTLS 或至少有傳輸加密？
- [ ] **身份驗證 (AuthN)：**
  - [ ] 是否在 Gateway 層就擋下無效 Token？
  - [ ] Web 前端是否避免了直接存取 Access Token (使用 BFF/Cookie 模式)？
- [ ] **授權控制 (AuthZ)：**
  - [ ] 服務間呼叫是否有白名單限制 (Service A 只能呼叫 Service B)？
  - [ ] 是否實作了最小權限原則 (Least Privilege)？
- [ ] **機密管理：** 服務是否從 Vault/Secrets Manager 讀取憑證，而非硬編碼或環境變數明文？

### Decision Tree: Where to put logic?
1. **Is it about validating the token signature?** -> API Gateway.
2. **Is it about converting Cookie to Token?** -> BFF.
3. **Is it about "Can User X buy Item Y"?** -> Domain Service (Business Logic) or OPA Sidecar.
4. **Is it about protecting against SQLi/XSS?** -> WAF (Edge) AND Input Validation (Service).

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Checkout Flow (Secure Implementation)

這是一個典型的電商結帳流程，展示各個組件如何協同工作以確保安全。

#### Architecture Components
1.  **Client:** Single Page Application (SPA).
2.  **BFF:** Node.js Express server.
3.  **Gateway:** Kong / Nginx.
4.  **Service:** Order Service (Go), Inventory Service (Java).
5.  **Infra:** Kubernetes with Istio (Service Mesh).

#### The Flow
1.  **Request:** User clicks "Checkout". Browser sends `POST /checkout` to **BFF**.
    *   *Security:* Request carries an `HttpOnly` Session Cookie. No JWT in LocalStorage.
2.  **Translation (BFF):** BFF validates the session, retrieves the associated Access Token (JWT) from Redis, and attaches it as `Authorization: Bearer <token>` header.
3.  **Routing (Gateway):** Request hits **API Gateway**.
    *   *Security:* Gateway verifies JWT signature (stateless check) and checks Rate Limits.
4.  **Service-to-Service (Mesh):** Gateway forwards to **Order Service**.
    *   *Security:* Traffic is encrypted via mTLS (Envoy sidecars). Order Service knows request came from Gateway because of the mTLS certificate identity.
5.  **Authorization (Sidecar/Service):** **Order Service** needs to check if User owns the cart.
    *   *Security:* Extracts UserID from JWT. Checks DB. (Or consults OPA: `allow if input.user_id == input.resource.owner_id`).
6.  **Downstream Call:** Order Service calls **Inventory Service** to deduct stock.
    *   *Security:* **Inventory Service** checks its mTLS policy: "Only Order Service can call `deduct_stock` endpoint". If Payment Service tries to call it, it's denied.

#### Pseudo-Configuration (Istio AuthorizationPolicy)
這段設定檔展示了如何強制執行「只有 Order Service 可以存取 Inventory Service」的零信任策略。

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: inventory-service-policy
  namespace: prod
spec:
  selector:
    matchLabels:
      app: inventory-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/order-service-account"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/stock/deduct"]
```