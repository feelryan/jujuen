# 生產環境安全性檢核表 / Production Security Checklist

在 Express 生態系中，安全性並非「開箱即用」（Out-of-the-box）的功能。相較於 Rails 或 Django 等 Batteries-included 框架，Express 的極簡主義意味著你需要手動配置大部分的安全防護層。本章節提供一份在將 Express 應用部署到生產環境前，必須執行的安全性檢核與實作指南。

In the Express ecosystem, security is not "out-of-the-box". Unlike batteries-included frameworks like Rails or Django, Express's minimalism means you must manually configure most security layers. This chapter provides a mandatory checklist and implementation guide before deploying your Express application to production.

---

## Mental model｜心智模型

### 1. 洋蔥式防禦（The Onion Defense / Defense in Depth）
不要依賴單一的安全措施。將 Express 的安全性視為「洋蔥模型」，請求在觸及核心商業邏輯前，必須通過層層過濾：
1.  **Network Layer**: Firewall, Load Balancer (AWS WAF, Nginx).
2.  **Application Entry**: Rate Limiting, CORS.
3.  **HTTP Headers**: Helmet (Security Headers).
4.  **Input Processing**: Body Parsing limits, Validation (Zod/Joi), Sanitization.
5.  **Data Layer**: ORM/ODM sanitization (preventing Injection).

### 2. 最小權限與零信任（Least Privilege & Zero Trust）
預設情況下，Express 對請求是「信任」的。你的心智模型應該轉變為「預設不信任」：
- 不信任來源（Strict CORS）。
- 不信任輸入（Strict Validation）。
- 不信任依賴套件（Audit Dependencies）。
- 不洩露資訊（No Stack Traces in Prod）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 強化 HTTP Headers (Hardening HTTP Headers)
使用 `helmet` 是 Express 專案的標準配備。它會自動設定多個關鍵的 HTTP Headers 來防禦常見攻擊（如 XSS, Clickjacking）。

```javascript
const helmet = require('helmet');

// 基本配置，適用於大多數 REST API
app.use(helmet());

// 如果你需要更嚴格的 Content Security Policy (CSP)
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "trusted-cdn.com"],
    },
  })
);
```

### 2. 嚴格的 CORS 策略 (Strict CORS Policy)
永遠不要在生產環境使用 `origin: '*'`。必須明確白名單允許的網域。

```javascript
const cors = require('cors');

const whitelist = ['https://api.myapp.com', 'https://admin.myapp.com'];
const corsOptions = {
  origin: function (origin, callback) {
    // 允許沒有 origin 的請求（如 mobile apps 或 curl）需視專案需求而定
    if (whitelist.indexOf(origin) !== -1 || !origin) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true, // 如果涉及 Cookies
};

app.use(cors(corsOptions));
```

### 3. 速率限制 (Rate Limiting)
防止暴力破解（Brute Force）與 DoS 攻擊。對於登入路由（Login routes）應設定更嚴格的限制。

```javascript
const rateLimit = require('express-rate-limit');

// 全局限制
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分鐘
  max: 100, // 每個 IP 限制 100 個請求
  message: 'Too many requests from this IP, please try again later.'
});

// 登入限制（更嚴格）
const authLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 小時
  max: 5, // 每個 IP 只能嘗試 5 次
  message: 'Too many login attempts, please try again after an hour.'
});

app.use('/api/', globalLimiter);
app.use('/api/auth/login', authLimiter);
```

### 4. 防止參數污染 (HPP - HTTP Parameter Pollution)
攻擊者可能會發送重複的 query parameters 來混淆應用程式邏輯。使用 `hpp` middleware 來防禦。

```javascript
const hpp = require('hpp');
app.use(hpp()); 
// ?sort=asc&sort=desc -> req.query.sort 將只會是 'desc' (最後一個)
```

### 5. 錯誤處理不洩露資訊 (Secure Error Handling)
在生產環境中，絕對不能將 Stack Trace 回傳給客戶端。

```javascript
// Error Handling Middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  
  res.status(statusCode).json({
    status: 'error',
    message: err.message, // 確保 message 也是經過過濾的，不含敏感資訊
    // 僅在開發環境回傳 stack
    stack: process.env.NODE_ENV === 'production' ? '🥞' : err.stack,
  });
});
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 洩露 `X-Powered-By` Header
**Anti-pattern**: 讓駭客知道你使用的是 Express，這有助於他們針對特定版本的漏洞進行攻擊。
**Fix**: 使用 `app.disable('x-powered-by')` 或直接使用 `helmet`（它會自動移除）。

### 2. 使用預設的 Cookie Session 名稱
**Anti-pattern**: 使用預設的 `connect.sid` 作為 session cookie 名稱。
**Fix**: 更改為通用的名稱（如 `id`, `session`），增加攻擊者識別框架的難度。

### 3. 盲目信任 `req.body` 進行資料庫查詢
**Anti-pattern**: 直接將 `req.body` 傳入 MongoDB/NoSQL 查詢。
**Risk**: NoSQL Injection。如果攻擊者傳送 `{"email": {"$gt": ""}}`，可能會繞過密碼驗證。
**Fix**: 使用 `express-mongo-sanitize` 或在 Validation 層（如 Zod/Joi）嚴格定義型別。

### 4. 在程式碼中硬編碼 Secrets
**Anti-pattern**: API Keys, DB Passwords 直接寫在 `.js` 檔中。
**Fix**: 使用 `dotenv` 並確保 `.env` 在 `.gitignore` 中。生產環境應透過 CI/CD pipeline 或 Secret Manager 注入環境變數。

### 5. 忽略 Body Payload 大小限制
**Anti-pattern**: 未設定 body parser 的 limit。
**Risk**: 攻擊者發送超大 JSON 導致 Server Out of Memory (DoS)。
**Fix**: `app.use(express.json({ limit: '10kb' }));`

---

## Checklists & workflows｜檢查清單與流程

在部署到 Production 之前，請逐一勾選以下項目：

### Infrastructure & Configuration
- [ ] **NODE_ENV**: 確保環境變數設定為 `production` (這會開啟 Express 內部的效能優化與錯誤頁面隱藏)。
- [ ] **Secrets Management**: 所有敏感資訊（DB URL, JWT Secret, API Keys）皆透過環境變數注入，無 Hardcode。
- [ ] **Port Exposure**: 應用程式不直接監聽 Port 80/443，而是透過 Reverse Proxy (Nginx/AWS ALB) 轉發。
- [ ] **TLS/SSL**: 確保僅透過 HTTPS 提供服務，並設定 HSTS header。

### Middleware Hardening
- [ ] **Helmet**: 已啟用 `helmet()`。
- [ ] **CORS**: 已配置白名單，且未啟用 `origin: '*'`。
- [ ] **Rate Limiting**: 已針對 API 路由啟用 `express-rate-limit`。
- [ ] **Body Parser**: 已設定 `limit` (如 `10kb`) 防止大封包攻擊。
- [ ] **Compression**: 使用 `compression` middleware (注意：若遭受 BREACH 攻擊風險，需謹慎評估，通常建議在 Nginx 層做 gzip)。

### Data & Logic
- [ ] **Input Validation**: 所有輸入路由皆有 Schema Validation (Zod/Joi/Express-Validator)。
- [ ] **Sanitization**: 針對 NoSQL Injection (如 `express-mongo-sanitize`) 與 XSS 進行了過濾。
- [ ] **Error Handling**: 確保全域錯誤處理器 **不** 回傳 Stack Trace。
- [ ] **Logging**: 使用 `winston` 或 `pino` 記錄日誌，並確保日誌中 **不包含** 敏感資訊（如密碼、信用卡號）。

### Dependencies
- [ ] **Vulnerability Scan**: 執行 `npm audit` 或 `yarn audit` 檢查依賴套件漏洞。
- [ ] **Unused Packages**: 移除未使用的 dependencies。

---

## Real-world examples｜實戰案例

### 案例：安全的 Express App 初始化 (Secure App Bootstrap)

這是一個整合了上述概念的 `app.js` 範本，可直接用於生產環境的基礎配置。

```javascript
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const mongoSanitize = require('express-mongo-sanitize');
const hpp = require('hpp');
const xss = require('xss-clean'); // 注意：現代前端框架通常已處理 XSS，後端視需求添加

const app = express();

// 1. Set Security HTTP Headers
app.use(helmet());

// 2. Limit Request Size (Body Parser)
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true, limit: '10kb' }));

// 3. Data Sanitization against NoSQL query injection
app.use(mongoSanitize());

// 4. Data Sanitization against XSS
app.use(xss());

// 5. Prevent Parameter Pollution
app.use(hpp());

// 6. Rate Limiting
const limiter = rateLimit({
  max: 100,
  windowMs: 15 * 60 * 1000,
  message: 'Too many requests from this IP, please try again in 15 minutes!'
});
app.use('/api', limiter);

// 7. CORS Setup
app.use(cors({
  origin: process.env.CLIENT_URL || 'https://my-production-app.com',
  credentials: true
}));

// Routes
// app.use('/api/v1/users', userRouter);

// Global Error Handler
app.use((err, req, res, next) => {
  console.error(err); // Log to centralized logging system (e.g., CloudWatch, Datadog)
  res.status(err.statusCode || 500).json({
    status: 'error',
    message: process.env.NODE_ENV === 'production' 
      ? 'Something went wrong' 
      : err.message
  });
});

module.exports = app;
```

### 決策樹：我需要哪種 Rate Limiting？

- **公開 API (Public API)**?
    - ➝ 使用 IP-based Rate Limiting (防止 DoS)。
- **使用者登入後的操作 (Authenticated Actions)**?
    - ➝ 使用 User ID-based Rate Limiting (防止單一帳號濫用資源)。
- **敏感操作 (Login/Reset Password)**?
    - ➝ 使用極嚴格的 IP + Route 限制 (例如 5 次失敗後鎖定 1 小時)。
- **分散式系統 (Microservices/Cluster)**?
    - ➝ 不要使用 `express-rate-limit` 的預設 Memory Store。
    - ➝ 必須改用 **Redis Store** 來在多個實例間共享計數器。