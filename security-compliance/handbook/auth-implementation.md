# 身份驗證與授權實作指南 / Practical Authentication & Authorization Implementation

## Mental model｜心智模型

在深入程式碼之前，必須先釐清「身份驗證 (Authentication, AuthN)」與「授權 (Authorization, AuthZ)」的邊界，並建立正確的 Token 傳遞心智模型。

### 1. The Hotel Key Card Analogy (飯店房卡類比)
將你的應用程式想像成一間飯店：
- **AuthN (你是誰？)**：你在櫃檯出示身分證 (Credentials)，櫃檯確認無誤後，發給你一張房卡 (Token/Session ID)。
- **AuthZ (你能做什麼？)**：你拿著房卡去刷電梯或房門。房卡系統決定這張卡能不能按頂樓按鈕，或是能不能打開 201 號房。
- **Session vs. JWT**：
  - **Session (Stateful)**：房卡上只有一個編號。門鎖讀取後，必須打電話問櫃檯：「編號 123 的卡片能開這扇門嗎？」(Server-side lookup)。
  - **JWT (Stateless)**：房卡本身寫入了權限資料（並有飯店簽名防偽）。門鎖讀取後，**不需要問櫃檯**，直接看卡片上的資料就知道能不能開門 (Self-contained)。

### 2. The "Zero Trust" Principle (零信任原則)
永遠不要相信客戶端傳來的資料。
- **Frontend's role**：只負責 UI 呈現（隱藏使用者無權點擊的按鈕），這只是為了使用者體驗 (UX)，不是安全性。
- **Backend's role**：必須對**每一個** API 請求進行驗證。不要以為使用者登入後就擁有所有資源的存取權 (防範 IDOR)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 選擇正確的 OAuth2/OIDC 流程 (Flow Selection)
不要再使用 Implicit Flow。根據應用場景選擇標準流程：

| 應用類型 (App Type) | 推薦流程 (Recommended Flow) | 關鍵機制 |
| :--- | :--- | :--- |
| **SPA (React/Vue)** | **Authorization Code Flow with PKCE** | 使用 PKCE (Proof Key for Code Exchange) 防止 Code 攔截，不需 Client Secret。 |
| **Mobile App (iOS/Android)** | **Authorization Code Flow with PKCE** | 同上，搭配 Custom URL Scheme 或 Universal Links。 |
| **Traditional Web (SSR)** | **Authorization Code Flow** | 後端可安全儲存 Client Secret，透過 Back-channel 交換 Token。 |
| **Machine-to-Machine** | **Client Credentials Flow** | 服務對服務溝通，無使用者介入。 |

### 2. JWT vs. Session：決策樹
- **使用 Session (Cookie-based)** 當：
  - 你的前後端部署在同一個網域 (Same Domain)。
  - 你需要即時撤銷使用者權限 (Instant Revocation)（例如：踢除可疑使用者）。
  - 專案規模較小，不想處理複雜的 Token 刷新機制。
- **使用 JWT (Token-based)** 當：
  - 你有微服務架構 (Microservices)，不想每個服務都去查 Redis Session。
  - 前後端分離且跨網域 (Cross-Domain)。
  - 需要行動裝置 App 支援 (Cookie 處理較麻煩)。

### 3. Token 儲存策略 (Storage Strategy)
這是最常被爭論的點，以下是安全優先的建議：
- **瀏覽器端 (Browser)**：
  - **最佳解**：存放在 **`HttpOnly` + `Secure` + `SameSite=Strict` Cookie** 中。這能防止 XSS 攻擊讀取 Token。
  - **次佳解 (僅在無法使用 Cookie 時)**：存放在 LocalStorage，但必須極度強化 XSS 防禦 (CSP, Input Sanitization)。
- **行動端 (Mobile)**：
  - iOS: **Keychain Services**
  - Android: **EncryptedSharedPreferences**

### 4. 權限模型設計 (RBAC vs. ABAC)
- **RBAC (Role-Based Access Control)**：
  - 適用於 90% 的 B2B SaaS。
  - 設計：User -> Role (e.g., Admin, Editor) -> Permission (e.g., `article:create`, `user:delete`)。
  - **實作技巧**：在 Code 裡檢查 Permission (`hasPermission('article:edit')`) 而不是檢查 Role (`isManager()`)，這樣未來調整 Role 定義時不需改 Code。
- **ABAC (Attribute-Based Access Control)**：
  - 適用於複雜邏輯（例如：「只有在上班時間、且 IP 來自公司內網的使用者才能存取」）。
  - 實作通常需要 Policy Engine (如 **OPA - Open Policy Agent**)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. ❌ IDOR (Insecure Direct Object Reference)
這是最常見的授權漏洞。
- **錯誤**：API `/api/orders/999` 只檢查「使用者是否登入」。
- **後果**：使用者 A 登入後，將 ID 改為 999，就能看到使用者 B 的訂單。
- **修正**：必須檢查「當前使用者是否為訂單 999 的擁有者」。

### 2. ❌ 在 JWT 中放入敏感個資
- **錯誤**：在 JWT Payload 中放入 `social_security_number` 或 `password_hash`。
- **後果**：JWT 只是 Base64 編碼，**任何人都能解碼讀取**。
- **修正**：JWT 只放 `sub` (User ID), `exp`, `scope` 等非敏感識別資訊。

### 3. ❌ 忽略 Token 撤銷 (Revocation)
- **錯誤**：JWT 有效期設為 30 天，且沒有黑名單機制。
- **後果**：如果使用者手機遺失或 Token 被竊，駭客在 30 天內擁有完全存取權，你無法將其登出。
- **修正**：
  - 使用 **Short-lived Access Token** (e.g., 15 mins) + **Long-lived Refresh Token**。
  - 當需要撤銷時，從資料庫刪除 Refresh Token，駭客最多只能再用 15 分鐘。

### 4. ❌ 錯誤的密碼處理
- **錯誤**：自己寫加密演算法、使用 MD5/SHA1、沒有加 Salt。
- **修正**：直接使用經過驗證的雜湊庫，如 **Argon2id** (首選) 或 **Bcrypt**。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: JWT Storage (Web)
```mermaid
graph TD
    A[需要儲存 Access Token] --> B{有後端控制權?}
    B -- Yes (BFF/Same Domain) --> C[Set-Cookie Header]
    C --> D[HttpOnly + Secure + SameSite]
    B -- No (Public API only) --> E{能接受 XSS 風險?}
    E -- No --> F[實作 BFF (Backend for Frontend) 轉發]
    E -- Yes (不建議) --> G[LocalStorage (需配合嚴格 CSP)]
```

### Pre-flight Checklist (上線前檢查)

- [ ] **Transport Security**: 全站強制 HTTPS (HSTS enabled)。
- [ ] **AuthN**: 登入介面有 Rate Limiting (防止暴力破解)。
- [ ] **AuthN**: 錯誤訊息模糊化 (Generic Error Messages)，不回傳「帳號不存在」或「密碼錯誤」，統一回傳「帳號或密碼無效」。
- [ ] **Session/Token**: Cookie 設定了 `HttpOnly`, `Secure`, `SameSite=Lax/Strict`。
- [ ] **AuthZ**: 關鍵 API (尤其是寫入操作) 都有 IDOR 檢查 (Resource Ownership Check)。
- [ ] **OAuth**: 如果使用 OAuth2，確認 `state` 參數有被驗證 (防止 CSRF)，且使用 PKCE。
- [ ] **Logs**: 確保 Auth 相關 Log **沒有**紀錄 Password、Token 或 PII，但有紀錄 User ID 和 IP。

---

## Real-world examples｜實戰案例

### 1. RBAC 資料庫設計模式 (PostgreSQL 範例)
這是一個標準、可擴展的 RBAC Schema 設計。

```sql
-- 1. Users: 核心使用者表
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL, -- Argon2id hash
  is_active BOOLEAN DEFAULT TRUE
);

-- 2. Roles: 角色定義 (e.g., 'admin', 'editor')
CREATE TABLE roles (
  id INT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT
);

-- 3. Permissions: 細粒度權限 (e.g., 'post:create', 'user:delete')
CREATE TABLE permissions (
  id INT PRIMARY KEY,
  slug VARCHAR(100) UNIQUE NOT NULL, -- 用於程式碼檢查 check(slug)
  description TEXT
);

-- 4. Role-Permission Mapping: 角色擁有什麼權限
CREATE TABLE role_permissions (
  role_id INT REFERENCES roles(id),
  permission_id INT REFERENCES permissions(id),
  PRIMARY KEY (role_id, permission_id)
);

-- 5. User-Role Mapping: 使用者是什麼角色
CREATE TABLE user_roles (
  user_id BIGINT REFERENCES users(id),
  role_id INT REFERENCES roles(id),
  PRIMARY KEY (user_id, role_id)
);
```

### 2. 前端 Axios Interceptor 處理 Token Refresh
這是在 SPA (Single Page Application) 中處理 Access Token 過期 (401) 的標準做法。

```javascript
// pseudo-code for axios interceptor
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 如果收到 401 且不是重試過的請求
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 1. 呼叫 refresh token endpoint (通常帶有 HttpOnly Cookie)
        await axios.post('/api/auth/refresh-token');
        
        // 2. 刷新成功後，重試原本失敗的請求
        return axios(originalRequest);
      } catch (refreshError) {
        // 3. 刷新失敗 (Refresh token 也過期了)，強制登出並導向登入頁
        store.dispatch('auth/logout');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
```

### 3. Middleware 中的權限檢查 (Node.js/Express 範例)
強調 "Check Permission, not Role"。

```javascript
// ✅ Good: 檢查權限 (解耦角色與程式碼)
app.delete('/api/users/:id', 
  requireAuth, 
  requirePermission('user:delete'), // Middleware 檢查 user 是否有此 permission
  UserController.delete
);

// ❌ Bad: 檢查角色 (硬編碼，難以維護)
app.delete('/api/users/:id', 
  requireAuth, 
  (req, res, next) => {
    if (req.user.role === 'admin' || req.user.role === 'superadmin') { // 邏輯散落在各處
        next();
    } else {
        res.status(403).send('Forbidden');
    }
  },
  UserController.delete
);
```