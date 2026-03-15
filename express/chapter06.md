# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的層次，安全性不再只是「功能完成後補上的檢查清單」，而是從架構設計階段就必須考量的「縱深防禦（Defense in Depth）」策略。Express 作為一個極簡框架，預設並不包含許多安全防護，這意味著開發者必須主動配置中間件（Middleware）來縮減攻擊面。

At the senior engineering level, security is no longer just a "checklist after feature completion," but a "Defense in Depth" strategy considered from the architectural design phase. As a minimalist framework, Express does not include many security defenses by default, which means developers must actively configure middleware to reduce the attack surface.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作全方位的 HTTP 防護**：熟練配置 `helmet`、CORS 與 Rate Limiting，理解每個 Header 背後的安全意涵。
    **Implement comprehensive HTTP protection**: Proficiently configure `helmet`, CORS, and Rate Limiting, understanding the security implications behind each Header.
2.  **防禦 OWASP Top 10 漏洞**：在 Express 層級有效攔截 Injection（SQL/NoSQL）與 XSS 攻擊，並處理 ReDoS（正則表達式阻斷服務）。
    **Defend against OWASP Top 10 vulnerabilities**: Effectively intercept Injection (SQL/NoSQL) and XSS attacks at the Express level, and handle ReDoS (Regular Expression Denial of Service).
3.  **設計安全的認證與授權機制**：深入分析 JWT 與 Session 在分散式系統中的權衡（Trade-offs），並正確實作 Token 儲存策略（HttpOnly Cookies vs LocalStorage）。
    **Design secure Authentication & Authorization mechanisms**: Deeply analyze the trade-offs between JWT and Session in distributed systems, and correctly implement Token storage strategies (HttpOnly Cookies vs LocalStorage).
4.  **優化錯誤處理與日誌脫敏**：確保在 Production 環境中不會洩露 Stack Trace 或敏感資訊，同時保持可觀測性。
    **Optimize error handling and log sanitization**: Ensure that Stack Traces or sensitive information are not leaked in the Production environment while maintaining observability.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 縱深防禦與洋蔥模型 (Defense in Depth & The Onion Model)

將 Express 應用程式視為洋蔥的核心。請求（Request）在觸及核心業務邏輯之前，必須穿過層層的防護中間件。每一層中間件負責過濾特定類型的威脅。如果一層失效，下一層仍能提供保護。

Visualize the Express application as the core of an onion. A Request must pass through layers of protective middleware before touching the core business logic. Each middleware layer is responsible for filtering specific types of threats. If one layer fails, the next layer should still provide protection.

-   **Layer 1: Network/Edge (Outside Express)** - WAF, Load Balancer (DDoS protection, SSL Termination).
-   **Layer 2: HTTP Headers (Helmet)** - 告訴瀏覽器如何表現（防止 Clickjacking, XSS, Sniffing）。
-   **Layer 3: Traffic Control (Rate Limiting)** - 防止暴力破解與資源耗盡。
-   **Layer 4: Input Validation (Joi/Zod)** - 確保資料格式正確，防止 Injection。
-   **Layer 5: Authentication & Authorization** - 識別身分與權限。
-   **Layer 6: Data Access (ORM/Query Builder)** - 參數化查詢，防止 SQL Injection。

## 2.2 JWT vs. Session 的決策模型 (Decision Model: JWT vs. Session)

在資深面試或架構設計中，這是一個經典的權衡問題。

In senior interviews or architectural design, this is a classic trade-off discussion.

| Feature | Session (Stateful) | JWT (Stateless) |
| :--- | :--- | :--- |
| **Storage** | Server-side (Redis/Memcached) | Client-side (Browser) |
| **Scalability** | Requires shared storage (Redis) for horizontal scaling | Naturally scalable (Self-contained) |
| **Revocation** | Easy (Delete from Redis) | Hard (Requires Blacklist/Short Expiry) |
| **Bandwidth** | Low (Send Session ID only) | High (Token contains payload) |
| **Security Risk** | Session Fixation (if not handled) | XSS (if in LocalStorage), CSRF (if in Cookie) |

**資深觀點**：在微服務架構中，通常傾向使用 JWT 以減少對中心化 Session Store 的依賴，但必須搭配 **HttpOnly Cookie** 與 **Short-lived Access Token + Refresh Token** 模式來平衡安全性與撤銷（Revocation）需求。

**Senior Perspective**: In microservices architectures, JWT is often preferred to reduce dependency on a centralized Session Store. However, it must be paired with **HttpOnly Cookies** and a **Short-lived Access Token + Refresh Token** pattern to balance security and revocation requirements.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構中的安全職責 (Security Responsibilities in Typical Architecture)

在 Production 環境中，Express 很少直接面對公網（Public Internet）。通常前方會有 Nginx、AWS ALB 或 Cloudflare。

In a Production environment, Express rarely faces the Public Internet directly. Usually, there is Nginx, AWS ALB, or Cloudflare in front of it.

1.  **Reverse Proxy / Load Balancer**:
    -   負責 SSL/TLS Termination（Express 通常只處理 HTTP）。
    -   過濾惡意 IP 與基本的 DDoS 防護。
    -   **Express Config**: 必須設定 `app.set('trust proxy', 1)`，否則 `req.ip` 與 `req.protocol` 會抓到 Load Balancer 的內網 IP，導致 Rate Limiter 失效或 Cookie `secure` 屬性判斷錯誤。
    -   **Express Config**: Must set `app.set('trust proxy', 1)`; otherwise, `req.ip` and `req.protocol` will capture the Load Balancer's internal IP, causing Rate Limiter failure or incorrect Cookie `secure` attribute evaluation.

2.  **API Gateway**:
    -   處理統一的 Authentication（驗證 Token 簽名），Express 服務則專注於 Authorization（驗證權限 scope）。
    -   Handles unified Authentication (verifying Token signatures), while Express services focus on Authorization (verifying permission scopes).

## 3.2 效能與安全的權衡 (Performance vs. Security Trade-offs)

-   **Bcrypt Cost Factor**: 密碼雜湊（Hashing）是 CPU 密集型操作。Cost factor 越高越安全，但會阻塞 Event Loop。
    -   *Solution*: 將 Hashing 工作放入 Worker Threads 或獨立的 Auth Service，避免拖慢主 API 的吞吐量。
-   **Validation Overhead**: 過度複雜的 Input Validation schema（特別是巢狀物件或複雜 Regex）會增加 Latency。
    -   *Solution*: Fail fast。將輕量級檢查（如長度限制）放在重量級檢查（如 DB 查詢驗證）之前。

---

# 4. 逐步示例 (Walkthrough / Example)

我們將構建一個經過強化的 Express 應用程式骨架，整合 Helmet, Rate Limiting, CORS 以及安全的錯誤處理。

We will build a hardened Express application skeleton, integrating Helmet, Rate Limiting, CORS, and secure error handling.

## 4.1 基礎設置與依賴 (Setup & Dependencies)

```javascript
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');
const hpp = require('hpp'); // HTTP Parameter Pollution
const { cleanEnv, str, num } = require('envalid'); // Environment validation

// 1. Validate Env Vars (Fail fast if secrets are missing)
const env = cleanEnv(process.env, {
  NODE_ENV: str({ choices: ['development', 'production'] }),
  PORT: num({ default: 3000 }),
  CORS_ORIGIN: str(),
});

const app = express();
```

## 4.2 應用安全中間件 (Applying Security Middleware)

這是關鍵的防護層配置。請注意順序：安全 Header -> 流量控制 -> Body Parsing -> 邏輯。

This is the critical protection layer configuration. Note the order: Security Headers -> Traffic Control -> Body Parsing -> Logic.

```javascript
// 2. Security Headers (Helmet)
// Sets various HTTP headers like X-Content-Type-Options, X-Frame-Options, etc.
app.use(helmet());

// 3. CORS Policy
// Explicitly define allowed origins. Do NOT use '*' in production for sensitive APIs.
app.use(cors({
  origin: env.CORS_ORIGIN, // e.g., 'https://my-app.com'
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true, // Allow cookies to be sent
}));

// 4. Rate Limiting
// Limit repeated requests to public APIs and/or endpoints such as password reset.
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  message: 'Too many requests from this IP, please try again after 15 minutes',
});
// Apply to all requests (or apply selectively to /auth routes)
app.use(limiter);

// 5. Body Parsing & Parameter Pollution
app.use(express.json({ limit: '10kb' })); // Limit body size to prevent DoS
app.use(hpp()); // Prevent HTTP Parameter Pollution (e.g. ?sort=asc&sort=desc)

// 6. Trust Proxy (Crucial if behind Nginx/AWS ALB)
if (env.NODE_ENV === 'production') {
  app.set('trust proxy', 1); 
}
```

## 4.3 安全的路由與驗證 (Secure Routes & Validation)

使用 `Joi` 或 `Zod` 進行嚴格的輸入驗證。永遠不要信任 `req.body`。

Use `Joi` or `Zod` for strict input validation. Never trust `req.body`.

```javascript
const Joi = require('joi');

// Schema definition
const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).max(128).required(), // Max length prevents hashing DoS
});

app.post('/api/v1/login', async (req, res, next) => {
  try {
    // Input Validation
    const { error, value } = loginSchema.validate(req.body);
    if (error) {
      // Don't return the raw Joi error to client in prod (info leakage)
      const err = new Error('Invalid input data');
      err.status = 400;
      throw err;
    }

    // ... Authentication Logic (Check DB, Compare Password) ...
    
    // Secure Cookie Setting (for JWT)
    res.cookie('token', 'jwt_payload_here', {
      httpOnly: true, // Prevent XSS access
      secure: env.NODE_ENV === 'production', // HTTPS only
      sameSite: 'strict', // CSRF protection
      maxAge: 3600000 // 1 hour
    });

    res.json({ success: true, user: { email: value.email } });
  } catch (err) {
    next(err);
  }
});
```

## 4.4 集中式錯誤處理 (Centralized Error Handling)

防止 Stack Trace 洩露給客戶端。

Prevent Stack Trace leakage to the client.

```javascript
// Error Handling Middleware (Must be the last middleware)
app.use((err, req, res, next) => {
  const statusCode = err.status || 500;
  
  // Log the full error on server side
  console.error(`[Error] ${req.method} ${req.url}:`, err);

  // Send sanitized response to client
  res.status(statusCode).json({
    success: false,
    message: statusCode === 500 ? 'Internal Server Error' : err.message,
    // Only show stack in development
    stack: env.NODE_ENV === 'development' ? err.stack : undefined,
  });
});
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 將 JWT 儲存在 LocalStorage (Storing JWT in LocalStorage)

-   **錯誤描述**：前端將後端回傳的 JWT 存入 `localStorage` 或 `sessionStorage`。
    **Description**: Frontend stores the JWT returned by the backend in `localStorage` or `sessionStorage`.
-   **為何不好**：任何能夠在該頁面執行 JavaScript 的第三方腳本（透過 XSS 漏洞注入）都可以讀取 Token，導致帳戶被完全接管。
    **Why it's bad**: Any third-party script running on that page (injected via XSS vulnerability) can read the Token, leading to full account takeover.
-   **最佳實踐**：使用 `httpOnly`、`secure`、`SameSite=Strict` 的 Cookie 儲存 Token。這樣 JS 無法讀取，大幅降低 XSS 造成的損害。

## 5.2 忽略 ReDoS (Ignoring ReDoS)

-   **錯誤描述**：使用低效的正則表達式來驗證使用者輸入（例如 `/(a+)+b/`）。
    **Description**: Using inefficient regular expressions to validate user input (e.g., `/(a+)+b/`).
-   **為何不好**：攻擊者可以發送精心構造的字串，導致 Event Loop 被卡死數秒甚至數分鐘，造成服務拒絕（DoS）。
    **Why it's bad**: Attackers can send crafted strings that cause the Event Loop to hang for seconds or minutes, causing Denial of Service (DoS).
-   **最佳實踐**：使用 `validator.js` 或 `zod` 等經過測試的庫，避免手寫複雜 Regex。使用 `safe-regex` 工具檢測模式。

## 5.3 錯誤訊息洩露 (Verbose Error Leakage)

-   **錯誤描述**：直接將 `err.message` 或 SQL 錯誤回傳給前端。
    **Description**: Returning `err.message` or SQL errors directly to the frontend.
-   **為何不好**：這會暴露資料庫結構（Table 名稱、欄位）、使用的框架版本或檔案路徑，協助攻擊者尋找漏洞。
    **Why it's bad**: This exposes database structure (table names, columns), framework versions, or file paths, aiding attackers in finding vulnerabilities.
-   **最佳實踐**：Production 環境一律回傳通用錯誤訊息（如 "An unexpected error occurred"），並附上一個 Request ID 供內部查 Log 使用。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 JWT vs Session in Microservices

**Q: 在微服務架構下，你會選擇 JWT 還是 Session？如何處理登出（Logout）問題？**
**Q: In a microservices architecture, would you choose JWT or Session? How do you handle the Logout problem?**

-   **高分回答要點**：
    -   **選擇**：傾向 JWT，因為它是 Stateless，不需要所有微服務都去存取同一個 Redis（減少延遲與耦合）。
    -   **缺點**：JWT 難以即時撤銷（Revocation）。
    -   **解決方案**：
        1.  **Short-lived Access Token** (e.g., 15 min) + **Refresh Token** (stored in DB/Redis)。
        2.  登出時，只將 Refresh Token 從 DB 移除或加入黑名單。
        3.  Access Token 過期後，前端嘗試刷新失敗，強制登出。這將「不可撤銷期」縮短為 15 分鐘。

## 6.2 CSRF 防護策略

**Q: 如果我們使用 Cookie 儲存 Token，如何防禦 CSRF 攻擊？**
**Q: If we use Cookies to store Tokens, how do we defend against CSRF attacks?**

-   **高分回答要點**：
    -   解釋 CSRF 機制：惡意網站利用使用者的瀏覽器自動攜帶 Cookie 的特性發送請求。
    -   **防禦 1 (Modern)**：設定 Cookie 的 `SameSite` 屬性為 `Strict` 或 `Lax`。這能阻擋大部分跨站請求攜帶 Cookie。
    -   **防禦 2 (Defense in Depth)**：使用 Double Submit Cookie 或 CSRF Token（如 `csurf` middleware），要求請求除了 Cookie 外，還要在 Header 中帶一個隨機 Token。

## 6.3 處理 Node.js 的 Event Loop 阻塞

**Q: 攻擊者發送了一個極大的 JSON Payload，導致 Server 無回應，如何排查與修復？**
**Q: An attacker sends a massive JSON Payload, causing the Server to become unresponsive. How do you troubleshoot and fix it?**

-   **高分回答要點**：
    -   **排查**：監控 Event Loop Lag。確認是否因 `JSON.parse` 解析過大字串導致 CPU 飆升。
    -   **修復**：在 `express.json()` 中設定 `limit`（如 `10kb`）。
    -   **延伸**：如果是複雜計算（如密碼雜湊），應移至 Worker Threads 或 Task Queue。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 7.1 記憶錨點 (Key Takeaways)

1.  **Helmet is Mandatory**: 永遠使用 `helmet()` 作為第一個中間件來設定安全的 HTTP Headers。
2.  **Validate Inputs**: 使用 Joi/Zod 嚴格驗證所有輸入，這是防禦 Injection 的第一道防線。
3.  **Stateless Auth**: 優先考慮 JWT + HttpOnly Cookie，並理解 Refresh Token 流程以解決撤銷問題。
4.  **Rate Limiting**: 必須配置速率限制以防止暴力破解與 DoS。
5.  **Hide Secrets**: 確保錯誤處理不會洩露 Stack Trace，並使用 `envalid` 確保環境變數正確加載。
6.  **Trust Proxy**: 在反向代理（Nginx/LB）後方時，務必設定 `app.set('trust proxy', 1)`。

## 7.2 後續延伸 (Next Steps)

-   **Advanced Monitoring**: 學習如何整合 APM (Application Performance Monitoring) 如 Datadog 或 New Relic 來監控安全事件。
-   **Next Chapter**: 進入 **Chapter 07: 效能優化與快取策略 (Performance Optimization & Caching Strategies)**，探討如何在確保安全的前提下，利用 Redis 與 CDN 提升 Express 效能。