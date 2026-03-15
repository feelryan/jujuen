# 1. 前言與學習目標 (Introduction & Learning Goals)

在資深工程師的職涯中，"It works on my machine" 只是起點，真正的挑戰在於如何讓系統在充滿惡意攻擊與高併發流量的生產環境中存活。本章不只探討如何修補漏洞，更著重於將安全性與穩定性內建於系統設計之中。

In the career of a Senior Software Engineer, "It works on my machine" is just the starting point. The real challenge lies in ensuring the system survives in a production environment filled with malicious attacks and high-concurrency traffic. This chapter focuses not just on patching vulnerabilities, but on baking security and stability into the system design itself.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作防禦縱深 (Implement Defense in Depth)**：不僅依賴外部 WAF，能在 Node.js 層級有效防禦 OWASP Top 10（如 Injection, XSS, ReDoS）。
    Implement defense in depth, effectively mitigating OWASP Top 10 vulnerabilities (e.g., Injection, XSS, ReDoS) at the Node.js layer, not just relying on external WAFs.
2.  **設計企業級驗證授權 (Design Enterprise-grade AuthN/AuthZ)**：掌握 JWT 與 Refresh Token Rotation 機制，並理解 OAuth2 在後端的實作細節與安全邊界。
    Master JWT and Refresh Token Rotation mechanisms, and understand the implementation details and security boundaries of OAuth2 in the backend.
3.  **確保服務韌性 (Ensure Service Resilience)**：實作 Rate Limiting 防止濫用，並正確處理 Graceful Shutdown 以達成零停機部署 (Zero Downtime Deployment)。
    Implement Rate Limiting to prevent abuse and correctly handle Graceful Shutdown to achieve Zero Downtime Deployment.
4.  **識別安全反模式 (Identify Security Anti-patterns)**：在 Code Review 中敏銳地發現敏感資料洩漏、錯誤的加密實作或 Event Loop 阻塞風險。
    Keenly spot sensitive data leaks, incorrect encryption implementations, or Event Loop blocking risks during Code Reviews.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 縱深防禦與瑞士起司模型 (Defense in Depth & The Swiss Cheese Model)

安全性不應依賴單一防線。想像每一層防護（防火牆、Nginx、Node.js Middleware、資料庫權限）都是一片有漏洞的起司。我們的目標是堆疊足夠多的層級，使得這些漏洞不會連成一條直線讓攻擊者穿透。

Security should not rely on a single line of defense. Imagine each layer of protection (Firewall, Nginx, Node.js Middleware, Database Permissions) as a slice of Swiss cheese with holes. Our goal is to stack enough layers so that the holes do not align, preventing an attacker from penetrating through.

-   **Network Layer**: VPC, Security Groups.
-   **Gateway Layer**: Rate Limiting, WAF, SSL Termination.
-   **Application Layer (Node.js)**: Input Validation (Zod/Joi), Authentication, Authorization, Sanitization.
-   **Data Layer**: Encryption at rest, Principle of Least Privilege.

### 2.2 信任邊界 (Trust Boundaries)

在 Node.js 應用程式中，任何來自外部的輸入（HTTP Body, Query Params, Headers, Database results from external sources）都應視為「不可信」。

In a Node.js application, any input from the outside (HTTP Body, Query Params, Headers, Database results from external sources) must be treated as "untrusted".

-   **Naive View**: 相信前端傳來的 `user_id` 或 `role`。
    Trusting the `user_id` or `role` sent by the frontend.
-   **Senior View**: 前端可被篡改。必須在後端驗證 Token 簽章 (Signature) 並重新查詢資料庫或快取確認權限。
    The frontend can be tampered with. You must verify the Token signature on the backend and re-query the database or cache to confirm permissions.

### 2.3 可用性即安全性 (Availability is Security)

對於 Node.js 這種單執行緒 (Single-threaded) 事件驅動架構，**Denial of Service (DoS)** 是極大的威脅。安全性不僅是防止資料被竊，還包括防止 Event Loop 被阻塞。

For Node.js's single-threaded, event-driven architecture, **Denial of Service (DoS)** is a massive threat. Security is not just about preventing data theft; it also includes preventing the Event Loop from being blocked.

-   **ReDoS (Regular Expression DoS)**: 惡意的 Regex 輸入可能導致 CPU 飆升至 100%，卡死整個 Process。
    Malicious Regex input can cause CPU usage to spike to 100%, freezing the entire process.
-   **Sync Operations**: 在請求處理中使用同步加密函式 (如 `pbkdf2Sync`) 會導致所有請求停擺。
    Using synchronous crypto functions (like `pbkdf2Sync`) during request handling will stall all requests.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，Node.js 服務通常位於 Load Balancer 之後，資料庫之前。

In large-scale distributed systems, Node.js services typically sit behind a Load Balancer and in front of a Database.

### 3.1 驗證與授權架構 (AuthN & AuthZ Architecture)

-   **Gateway/Edge**: 初步過濾 (DDoS protection, IP Blacklisting)。
-   **Auth Service (Identity Provider)**: 負責簽發 Token (JWT)。這通常是一個獨立的 Node.js 服務或第三方 (Auth0, Cognito)。
-   **Business Logic Service**: 負責驗證 Token (Verify Signature) 並檢查 Scope/Role。
    *   *Design Choice*: 使用 **JWT (Stateless)** 以利水平擴展，但需搭配 **Redis** 實作 Token Blacklist 或 Refresh Token Rotation 以解決「無法即時撤銷」的問題。
    *   *Design Choice*: Use **JWT (Stateless)** for horizontal scalability, but pair it with **Redis** to implement Token Blacklists or Refresh Token Rotation to solve the "immediate revocation" problem.

### 3.2 生產環境配置 (Production Configuration)

資深工程師需確保應用程式具備「優雅」的生命週期管理：

Senior engineers must ensure the application has "graceful" lifecycle management:

1.  **Graceful Shutdown**: 當 Kubernetes 或是 Auto-scaler 決定縮減 Pod 時，Node.js process 會收到 `SIGTERM`。此時應停止接收新連線，處理完現有請求，並關閉 DB 連線，最後才退出。
    When Kubernetes or an Auto-scaler decides to scale down a Pod, the Node.js process receives a `SIGTERM`. It should stop accepting new connections, finish existing requests, close DB connections, and only then exit.
2.  **Secret Management**: 絕對禁止將 API Key 或 DB Password 硬編碼 (Hard-code)。應使用 Environment Variables，並結合 Vault 或 AWS Secrets Manager 在啟動時注入。
    Never hard-code API Keys or DB Passwords. Use Environment Variables, combined with Vault or AWS Secrets Manager, injected at runtime.

---

# 4. 逐步示例 (Walkthrough / Example)

### 4.1 實作安全的 JWT Refresh Token 機制 (Secure JWT Refresh Token Mechanism)

單純發發一個長效的 JWT 是不安全的。我們採用 **Short-lived Access Token + Long-lived Refresh Token** 模式。

Issuing a single long-lived JWT is insecure. We adopt the **Short-lived Access Token + Long-lived Refresh Token** pattern.

**關鍵策略 (Key Strategy):**
- **Access Token**: 存活 15 分鐘，放在 Memory 或非 HttpOnly Cookie (若需前端讀取)。
- **Refresh Token**: 存活 7 天，**必須**放在 `HttpOnly; Secure; SameSite=Strict` Cookie 中，防止 XSS 竊取。
- **Rotation**: 每次使用 Refresh Token 換取新 Access Token 時，同時更換新的 Refresh Token。

```javascript
// authController.js (Simplified)
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// 模擬 DB
const userDB = new Map(); 
const refreshTokensDB = new Map(); // In production, use Redis

const ACCESS_TOKEN_SECRET = process.env.ACCESS_TOKEN_SECRET;
const REFRESH_TOKEN_SECRET = process.env.REFRESH_TOKEN_SECRET;

function generateTokens(user) {
  const accessToken = jwt.sign({ id: user.id, role: user.role }, ACCESS_TOKEN_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ id: user.id }, REFRESH_TOKEN_SECRET, { expiresIn: '7d' });
  return { accessToken, refreshToken };
}

// Login Handler
exports.login = async (req, res) => {
  // ... validate user credentials ...
  const user = { id: '123', role: 'admin' };
  
  const { accessToken, refreshToken } = generateTokens(user);

  // Store Refresh Token with Family ID for rotation tracking (Advanced)
  refreshTokensDB.set(refreshToken, { userId: user.id, isValid: true });

  // Security Best Practice: Refresh Token in HttpOnly Cookie
  res.cookie('jwt_refresh', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // HTTPS only
    sameSite: 'Strict', // Prevent CSRF
    maxAge: 7 * 24 * 60 * 60 * 1000
  });

  res.json({ accessToken });
};

// Refresh Handler (Token Rotation)
exports.refreshToken = async (req, res) => {
  const incomingRefreshToken = req.cookies.jwt_refresh;
  if (!incomingRefreshToken) return res.sendStatus(401);

  // Check reuse detection (Security Critical)
  const storedToken = refreshTokensDB.get(incomingRefreshToken);
  if (!storedToken) {
     // Possible token theft! Invalidate all tokens for this user family.
     // await revokeAllUserTokens(decoded.id); 
     return res.sendStatus(403);
  }

  try {
    const decoded = jwt.verify(incomingRefreshToken, REFRESH_TOKEN_SECRET);
    
    // Rotate: Invalidate old, issue new
    refreshTokensDB.delete(incomingRefreshToken);
    
    const newTokens = generateTokens({ id: decoded.id, role: 'user' }); // Fetch real user role from DB
    refreshTokensDB.set(newTokens.refreshToken, { userId: decoded.id, isValid: true });

    res.cookie('jwt_refresh', newTokens.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'Strict',
      maxAge: 7 * 24 * 60 * 60 * 1000
    });

    res.json({ accessToken: newTokens.accessToken });
  } catch (err) {
    return res.sendStatus(403);
  }
};
```

### 4.2 Graceful Shutdown 實作 (Implementing Graceful Shutdown)

這段程式碼確保在部署新版本時，舊的 Pod 不會直接斷開正在連線的使用者。

This code ensures that during a new version deployment, the old Pod does not abruptly disconnect active users.

```javascript
// server.js
const express = require('express');
const app = express();
const server = app.listen(3000);

// 模擬長連線處理
app.get('/long-process', (req, res) => {
  setTimeout(() => res.send('Done'), 5000);
});

async function gracefulShutdown(signal) {
  console.log(`Received ${signal}. Starting graceful shutdown...`);
  
  // 1. Stop accepting new connections
  server.close(async () => {
    console.log('HTTP server closed.');
    
    try {
      // 2. Close Database Connections
      // await db.disconnect();
      console.log('Database connections closed.');
      
      // 3. Close Redis/Message Queue connections
      // await redisClient.quit();
      
      console.log('Graceful shutdown complete.');
      process.exit(0);
    } catch (err) {
      console.error('Error during shutdown', err);
      process.exit(1);
    }
  });

  // Force shutdown after timeout (e.g., 10s) if connections hang
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
}

// Listen for termination signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 錯誤的 Error Handling 導致資訊洩漏 (Leaking Info via Error Handling)

-   **Anti-pattern**: 直接將 `err.stack` 或 `err.message` 回傳給前端。
    Sending `err.stack` or `err.message` directly to the frontend.
-   **Risk**: 攻擊者可藉此得知你的檔案結構、使用的 Library 版本，甚至資料庫 Schema。
    Attackers can learn your file structure, library versions, or even database schema.
-   **Solution**: 使用全域 Error Handler，在 Production 僅回傳通用訊息 (如 "Internal Server Error")，詳細 Log 留給後端監控系統 (如 ELK, Datadog)。
    Use a global Error Handler that returns generic messages (e.g., "Internal Server Error") in Production, while logging details to backend monitoring systems (e.g., ELK, Datadog).

### 5.2 忽略 NPM 依賴風險 (Ignoring NPM Dependency Risks)

-   **Anti-pattern**: 盲目相信 `npm install`，從不稽核 `package-lock.json`。
    Blindly trusting `npm install` and never auditing `package-lock.json`.
-   **Risk**: Supply Chain Attacks (如惡意程式碼被注入到常用套件中)。
    Supply Chain Attacks (e.g., malicious code injected into popular packages).
-   **Solution**: 在 CI/CD 流程中整合 `npm audit` 或 `snyk`。鎖定版本 (Pin versions)。

### 5.3 在 Node.js 中進行 CPU 密集型加密 (CPU-intensive Crypto in Node.js)

-   **Anti-pattern**: 在 Request Handler 中使用同步的 `crypto.pbkdf2Sync` 或純 JS 實作的加密演算法。
    Using synchronous `crypto.pbkdf2Sync` or pure JS crypto implementations inside a Request Handler.
-   **Risk**: Event Loop 阻塞，導致單一請求卡死數千個併發請求。
    Event Loop blocking, causing a single request to freeze thousands of concurrent requests.
-   **Solution**: 使用非同步版本 (`await crypto.pbkdf2(...)`)，這會利用 libuv 的 Thread Pool，或將加密工作卸載到獨立的 Microservice/Worker。
    Use asynchronous versions (`await crypto.pbkdf2(...)`), which utilize libuv's Thread Pool, or offload crypto work to a separate Microservice/Worker.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何在 Node.js 應用程式中防禦 ReDoS (Regular Expression Denial of Service)？
**How do you defend against ReDoS in a Node.js application?**

-   **高分回答要點 (Key Points)**:
    -   解釋 Node.js 是單執行緒，Regex 運算是同步的，複雜的 Backtracking 會阻塞 Event Loop。
    -   **避免使用易受攻擊的 Regex**: 避免嵌套的 Quantifiers (如 `(a+)+`)。
    -   **使用工具檢測**: 使用 `safe-regex` 或 ESLint plugin 檢查。
    -   **使用非原生 Regex Engine**: 如 `node-re2` (Google's RE2)，它保證線性時間複雜度，不會發生災難性回溯。
    -   **Input Validation**: 限制輸入字串長度。

### Q2: 比較 JWT 與 Session-based Authentication 的優缺點，你會如何選擇？
**Compare JWT vs. Session-based Authentication. How would you choose?**

-   **高分回答要點 (Key Points)**:
    -   **Stateless vs. Stateful**: JWT 不需要 Server 存狀態，適合 Microservices；Session 需要 Redis/DB 支援。
    -   **Revocation (撤銷)**: Session 容易撤銷 (刪除 Redis key 即可)；JWT 難以撤銷，需依賴 Expiration 或 Blacklist (這又變回 Stateful)。
    -   **Bandwidth**: JWT 通常較大，影響傳輸流量。
    -   **結論**: B2B 或 Server-to-Server 優先選 JWT；對安全性要求極高且需即時踢人的 B2C 應用 (如網銀) 考慮 Session 或 Short-lived JWT + Rotation。

### Q3: 什麼是 Cross-Site Request Forgery (CSRF)？在前後端分離架構下 (SPA + API) 如何防禦？
**What is CSRF? How do you defend against it in a decoupled architecture (SPA + API)?**

-   **高分回答要點 (Key Points)**:
    -   **原理**: 利用瀏覽器自動攜帶 Cookie 的特性，誘使使用者在已登入狀態下對目標網站發送請求。
    -   **防禦 1 (Modern)**: 使用 `SameSite=Strict` 或 `Lax` Cookie 屬性。這是最有效的現代防禦。
    -   **防禦 2 (Classic)**: Double Submit Cookie 或 CSRF Token (Synchronizer Token Pattern)。前端讀取 Cookie 中的 Token，並放入 Header 傳回，後端比對兩者。
    -   **注意**: 如果不使用 Cookie 存 Token (例如存 localStorage)，則天生免疫 CSRF，但易受 XSS 攻擊。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **OWASP Top 10**: 始終驗證輸入 (Zod/Joi)，防範 Injection 與 XSS。
2.  **JWT Security**: Access Token 短效，Refresh Token 長效且存於 HttpOnly Cookie，並實作 Rotation。
3.  **Availability**: Node.js 怕阻塞。避免同步 IO 與 ReDoS。使用 Rate Limiting (如 `express-rate-limit` + Redis)。
4.  **Production Ready**: 實作 Graceful Shutdown (`SIGTERM`)，確保零停機部署。
5.  **Headers**: 使用 Helmet 設定安全的 HTTP Headers (HSTS, CSP, NoSniff)。
6.  **Secrets**: 永遠不要 Commit 密鑰，使用 ENV 與 Secret Manager。

### 後續延伸 (Next Steps)

-   **進階監控 (Advanced Observability)**: 學習如何將安全日誌整合至 ELK 或 Datadog，並設定異常警報 (Alerting)。
-   **容器安全 (Container Security)**: 延伸閱讀 Docker/Kubernetes 的安全最佳實踐 (Non-root user, Read-only filesystem)，這將在 DevOps 章節深入探討。
-   **效能優化 (Performance)**: 安全性措施 (如加密、驗證) 會帶來效能開銷，下一章可探討如何透過 Profiling 與 Caching 優化 Node.js 效能。