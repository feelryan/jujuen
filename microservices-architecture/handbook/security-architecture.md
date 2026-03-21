# 微服務安全架構與身份管理 / Microservices Security & Identity Management

## Mental model｜心智模型

在單體架構（Monolith）中，安全往往像是「城堡與護城河（Castle and Moat）」：一旦通過了外圍的防火牆與登入驗證，內部組件之間的呼叫通常被視為可信的。

但在微服務架構中，你必須轉變為 **零信任（Zero Trust）** 的思維模式。想像這是一間現代化的大飯店：
1.  **大廳櫃檯（API Gateway）**：檢查你的護照（Authentication），並發給你一張房卡（Token）。
2.  **電梯與走廊（Internal Network）**：即使你進了大廳，也不代表你能去任何樓層。你需要刷卡才能按電梯。
3.  **房門（Service Endpoint）**：每一扇門（微服務）都要再次驗證你的房卡是否有權限進入（Authorization）。
4.  **服務間通訊（mTLS）**：服務員（Service A）要進入房間打掃（Service B），不僅要有權限，雙方還需要穿著制服並互相確認身份，確保不是假冒的服務員。

**核心原則：**
*   **Identity Propagation（身份傳遞）**：使用者的身份必須在服務呼叫鏈中傳遞，而不是在第一個服務就丟失。
*   **Defense in Depth（縱深防禦）**：不要只依賴網路邊界，每一層（Gateway, Service Mesh, App Logic）都要有防護。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. API Gateway as the First Line of Defense (Gateway Offloading)
將繁重的認證邏輯從微服務剝離，移至 API Gateway。
*   **Token Translation**：前端使用不透明令牌（Reference Token / Session ID），Gateway 驗證後轉換為包含 Claims 的 JWT (JSON Web Token) 傳給後端服務。這隱藏了內部結構並減少了傳輸量。
*   **Centralized AuthZ**：在 Gateway 進行粗粒度的授權（例如：是否有 `admin` scope？），微服務內部只做細粒度的商業邏輯授權（例如：這個 UserID 是否擁有這張訂單？）。

### 2. Identity Propagation with JWT
當 Service A 呼叫 Service B 時，**不要**使用 Service A 自己的憑證，而是應該傳遞發起請求的 User Context。
*   **做法**：將 Gateway 驗證過的 JWT 放入 HTTP Header (`Authorization: Bearer <token>`) 向下傳遞。
*   **好處**：Service B 知道「是誰」發起的請求，便於審計（Audit Logging）與權限控管。

### 3. Service-to-Service Authentication (mTLS)
如何確保呼叫 Service B 的真的是 Service A，而不是駭客植入的惡意腳本？
*   **Mutual TLS (mTLS)**：雙向 TLS 驗證。不僅 Server 要給 Client 看憑證，Client 也要出示憑證。
*   **實作建議**：手動管理憑證極其痛苦。建議使用 **Service Mesh (如 Istio, Linkerd)** 自動處理 Sidecar 之間的 mTLS 與憑證輪替（Certificate Rotation）。

### 4. Centralized Policy Engine (OPA)
避免將複雜的權限判斷（如 RBAC, ABAC）寫死在程式碼（Hard-coded）中。
*   **Open Policy Agent (OPA)**：將策略定義為程式碼（Policy as Code, Rego 語言）。
*   **模式**：微服務收到請求 -> 詢問 OPA Sidecar「這個 User 可以對這個 Resource 做 Action 嗎？」 -> OPA 回傳 Allow/Deny。

### 5. Secrets Management
*   **Externalize Secrets**：絕對不要將 API Key 或 DB 密碼 commit 到 Git。
*   **Runtime Injection**：使用 Vault、AWS Secrets Manager 或 K8s Secrets，在 Pod 啟動時掛載為 Volume 或環境變數。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Token" (上帝令牌)
*   **現象**：為了方便，服務間呼叫使用一個擁有所有權限的超級 Token，或者完全略過驗證。
*   **後果**：一旦某個邊緣服務（如日誌服務）被攻破，攻擊者就擁有整個系統的最高權限（Lateral Movement）。
*   **修正**：實施 **Least Privilege（最小權限原則）**，Service A 只能擁有呼叫 Service B 特定 API 的權限。

### 2. Confused Deputy Problem (困惑的代理人)
*   **現象**：使用者 Alice 呼叫 Service A，Service A 需要呼叫 Service B。Service A 使用「Service A 的身份」去呼叫 Service B。
*   **後果**：如果 Service A 被惡意使用者 Bob 操縱，Bob 可能透過 Service A 存取到 Alice 在 Service B 的資料，因為 Service B 只檢查了 Service A 的權限，沒檢查原始發起人是誰。
*   **修正**：務必實作 **On-Behalf-Of (OBO)** 流程或正確傳遞 User JWT。

### 3. Hairpinning (髮夾彎呼叫)
*   **現象**：內部 Service A 要呼叫 Service B，卻繞出去打 Public API Gateway 的外部網址。
*   **後果**：增加延遲、增加對外暴露面、複雜化防火牆設定。
*   **修正**：內部服務應透過 Service Discovery 直接進行內部通訊（East-West Traffic）。

### 4. Chatty Auth (喋喋不休的驗證)
*   **現象**：每個微服務在收到請求時，都向 Identity Provider (IdP, 如 Keycloak/Auth0) 發送 HTTP 請求驗證 Token 有效性。
*   **後果**：IdP 被打掛，系統延遲極高。
*   **修正**：使用 **Stateless JWT** + **JWKS (JSON Web Key Set)** 本地驗證簽名。只在必要時（如 Token 撤銷檢查）才查詢中央快取。

---

## Checklists & workflows｜檢查清單與流程

### Security Design Review Checklist (設計階段)
- [ ] **邊界定義**：是否清楚定義了哪些服務直接暴露給 Public Internet？（這些服務需要最嚴格的 WAF 與 Rate Limiting）。
- [ ] **資料分級**：是否標記了哪些服務處理 PII (個人識別資訊) 或敏感財務數據？
- [ ] **通訊加密**：是否所有服務間通訊（包含 DB 連線）都強制啟用 TLS？
- [ ] **身份傳遞**：架構圖中是否規劃了 User Identity 如何在服務鏈中傳遞？

### Implementation & Deployment Checklist (實作與部署階段)
- [ ] **Dependency Scanning**：CI/CD Pipeline 是否包含 SCA (Software Composition Analysis) 掃描以偵測依賴套件漏洞？
- [ ] **Container Security**：是否使用 Distroless 或最小化 Base Image？是否以非 root 用戶執行 Container？
- [ ] **Secrets Handling**：
    - [ ] 程式碼中沒有 Hardcode 密碼。
    - [ ] 環境變數不包含明文密碼（應使用 Secret Reference）。
- [ ] **Token Validation**：
    - [ ] 驗證 JWT 簽名 (Signature)。
    - [ ] 驗證 `exp` (過期時間)。
    - [ ] 驗證 `iss` (發行者) 與 `aud` (接收者)。
- [ ] **Observability**：安全相關事件（登入失敗、權限拒絕）是否輸出結構化日誌並送往 SIEM 或監控平台？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Order Creation (電商下單流程)

**Context**: 使用者點擊「結帳」，前端呼叫 `POST /orders`。

#### 1. Ingress / API Gateway Layer
*   **Action**: Gateway 攔截請求。
*   **Security Check**:
    *   驗證 Cookie 中的 Session ID。
    *   向 Redis 或 IdP 交換取得短效期的 **Signed JWT (Access Token)**。
    *   檢查 JWT 中的 Scope 是否包含 `order:write`。
    *   **Rate Limiting**: 限制該 IP 每分鐘只能下單 5 次。
*   **Forward**: 將 JWT 放入 `Authorization` Header，轉發給 `Order Service`。

#### 2. Service Layer (Order Service)
*   **Action**: 接收請求，準備寫入資料庫。
*   **Security Check (Local)**:
    *   使用 Public Key (from JWKS) 驗證 JWT 簽名（不呼叫 IdP）。
    *   解析 JWT 中的 `sub` (UserID)，確認訂單歸屬。
*   **Internal Call**: 需要扣庫存，呼叫 `Inventory Service`。
*   **Identity Propagation**:
    *   `Order Service` 建立一個新的 HTTP Request 呼叫 `Inventory Service`。
    *   **關鍵點**：將剛才收到的 User JWT 複製到新 Request 的 Header 中。
    *   **mTLS**: 透過 Sidecar (Envoy) 自動加密連線，`Inventory Service` 確信連線來自 `Order Service`。

#### 3. Data Layer (Inventory Service)
*   **Action**: 扣減庫存。
*   **Audit Log**: 記錄「User X 透過 Order Service 扣減了商品 Y 的庫存」。如果沒有傳遞 User JWT，這裡只能記錄「Order Service 扣了庫存」，無法追溯到具體使用者。

#### 4. Secret Rotation (Vault Example)
*   `Order Service` 需要連線 PostgreSQL。
*   Pod 啟動時，Init Container 向 HashiCorp Vault 請求 DB Credentials。
*   Vault 動態生成一組 `user_order_service_xyz` / `password_123` (有效期 1 小時)。
*   應用程式讀取 `/etc/secrets/db-creds` 連線。
*   1 小時後，Vault 自動撤銷舊密碼並生成新密碼（應用程式需支援熱重載或重啟）。