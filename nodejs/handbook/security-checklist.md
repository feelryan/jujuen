# 安全性加固實戰清單 / Security Hardening Checklist

在 Node.js 應用程式中，安全性並非單一功能的開關，而是一系列的防禦層級（Defense in Depth）。由於 Node.js 的單執行緒特性（Single-threaded nature），應用層的攻擊（如 ReDoS）不僅會洩漏資料，更可能直接導致整個服務癱瘓（Denial of Service）。本章節提供從程式碼層級到架構層級的實戰加固指南。

---

## Mental model｜心智模型

### 1. 瑞士乳酪模型 (The Swiss Cheese Model)
將安全性視為多層切片乳酪的堆疊。每一層防禦（Input Validation, Headers, Auth, Network）都可能有漏洞（孔洞），但只要這些孔洞沒有連成一線，攻擊者就無法穿透。
- **應用：** 不要只依賴防火牆（WAF），程式碼內部必須假設輸入是惡意的。

### 2. 事件迴圈守門員 (Event Loop Gatekeeper)
Node.js 最大的弱點在於 CPU 密集型任務會阻塞 Event Loop。安全性不僅是防止資料外洩，更是防止「運算資源耗盡」。
- **核心觀念：** 任何未經由 `await` 或 `Stream` 處理的同步運算（如複雜 Regex、大型 JSON parsing），都是潛在的 DoS 攻擊點。

### 3. 零信任輸入 (Zero Trust Input)
所有進入系統的資料（Body, Query, Headers, Cookies, Database results）都應被視為「受污染的（Tainted）」，直到通過驗證為止。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 嚴格的輸入驗證 (Schema-based Validation)
不要手寫 `if (req.body.email)`。使用 Schema 驗證庫來定義資料的「形狀」與「限制」。
- **Tooling:** `Zod` (推薦), `Joi`, `Ajv`.
- **Practice:** 在 Controller 的第一行就進行驗證，失敗直接拋出 400 錯誤。

```javascript
import { z } from 'zod';

const UserSignupSchema = z.object({
  email: z.string().email(),
  // 強制密碼複雜度，避免弱密碼
  password: z.string().min(12).regex(/[A-Z]/).regex(/[0-9]/),
  age: z.number().int().min(18).max(120),
});

// Middleware pattern
const validateInput = (schema) => (req, res, next) => {
  const result = schema.safeParse(req.body);
  if (!result.success) {
    // 永遠不要回傳詳細的內部錯誤結構，只回傳標準化訊息
    return res.status(400).json({ error: 'Invalid input format' });
  }
  next();
};
```

### 2. HTTP Headers 加固 (Security Headers)
瀏覽器依賴 HTTP Headers 來決定是否執行某些腳本或載入資源。
- **Tooling:** `Helmet.js` (Express/Fastify 生態系必備)。
- **Practice:** 預設啟用 Helmet，並針對 CSP (Content Security Policy) 進行微調。

```javascript
import helmet from 'helmet';
// 隱藏 X-Powered-By: Express，減少攻擊者資訊蒐集
app.use(helmet());
```

### 3. 秘密管理 (Secrets Management)
永遠不要將 API Keys、DB Passwords 硬編碼（Hardcode）在程式碼中。
- **Pattern:** 使用 `.env` 檔案配合 `dotenv`，但在生產環境應注入環境變數（Environment Variables）。
- **Best Practice:** 使用 Secret Manager (AWS Secrets Manager, HashiCorp Vault) 在啟動時動態注入。

### 4. 限制請求速率 (Rate Limiting)
防止 Brute-force 攻擊與 DoS。
- **Tooling:** `express-rate-limit`, Redis-based limiters.
- **Strategy:** 針對登入 API 設定嚴格限制（如 5 次/分鐘），一般 API 設定寬鬆限制。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The ReDoS Trap (Regex Denial of Service)
Node.js 的 Regex 引擎在處理某些巢狀量詞（Nested Quantifiers）時，若遇到惡意字串，時間複雜度會變成 O(2^n)，直接卡死 Event Loop。
- **Anti-pattern:** `/(a+)+b/.test('aaaaaaaaaaaaaaaaaaaaa...')`
- **Solution:** 使用 `validator.js` 等經過測試的庫，或使用 `node-re2` (Google 的安全 Regex 引擎 bindings)。避免自幹複雜 Regex 驗證 Email。

### 2. Prototype Pollution (原型污染)
攻擊者透過傳入 `__proto__` 或 `constructor` 屬性的 JSON，修改全域 `Object.prototype`，導致所有物件行為被改變。
- **Anti-pattern:** 遞迴合併物件時未過濾 Key。
- **Solution:** 使用 `Object.create(null)` 建立無原型物件，或使用會防禦此攻擊的庫（如 Lodash 的 `_.merge` 需更新至安全版本）。

### 3. 錯誤訊息洩漏 (Verbose Error Leaking)
在生產環境將完整的 `err.stack` 回傳給前端。這會暴露檔案路徑、使用的模組版本與程式邏輯。
- **Fix:** 實作全域 Error Handler，區分 `Production` 與 `Development` 模式。

### 4. 依賴地獄中的惡意軟體 (Supply Chain Attacks)
NPM 生態系龐大，惡意套件可能偽裝成常用庫（Typosquatting）。
- **Fix:** CI/CD 流程中加入 `npm audit` 或 `snyk test`。鎖定 `package-lock.json`。

---

## Checklists & workflows｜檢查清單與流程

在部署到 Production 之前，請執行以下檢查：

### 🛡️ Application Level
- [ ] **Input Validation:** 所有 API endpoint 是否都經過 Schema 驗證？
- [ ] **Injection Prevention:** 是否使用 ORM 或 Parameterized Queries 防止 SQL Injection？
- [ ] **Security Headers:** 是否已啟用 `Helmet`？HSTS 是否開啟？
- [ ] **Error Handling:** 確認 API 不會回傳 Stack Trace 給客戶端。
- [ ] **Rate Limiting:** 公開 API 與登入介面是否已設定速率限制？
- [ ] **Compression:** 是否使用反向代理（Nginx/Cloudflare）處理 Gzip/Brotli 而非 Node.js 本身（避免 BREACH 攻擊與 CPU 消耗）？

### 📦 Dependencies & Code
- [ ] **Vulnerability Scan:** 執行過 `npm audit` 或 `snyk` 掃描嗎？
- [ ] **Secrets:** 確認沒有 `.env` 或密碼被 commit 到 Git repo。
- [ ] **Linter:** 是否啟用 `eslint-plugin-security` 來靜態分析潛在風險？
- [ ] **Regex Check:** 是否檢查過自定義 Regex 存在 ReDoS 風險？

### ⚙️ Infrastructure & Runtime
- [ ] **User Privileges:** Node.js process 是否以 **非 root** 權限執行？
- [ ] **Cookie Security:** Session Cookie 是否設定了 `HttpOnly`, `Secure`, `SameSite=Strict`？
- [ ] **Logging:** 是否有遮蔽敏感資訊（PII, Passwords）的 Log 機制？

---

## Real-world examples｜實戰案例

### 案例一：防止 NoSQL Injection (MongoDB)

**情境：** 攻擊者試圖繞過登入驗證。
**Vulnerable Code:**
```javascript
// 如果 req.body.password 傳入 { "$gt": "" } (MongoDB query operator)
// 查詢變成：找一個使用者，其密碼 "大於" 空字串（總是為真）
app.post('/login', async (req, res) => {
  const user = await db.users.findOne({
    username: req.body.username,
    password: req.body.password // 直接傳入物件
  });
  if (user) { /* Login Success */ }
});
```

**Secure Pattern:**
強制轉型為字串，或使用 Sanitization。
```javascript
app.post('/login', async (req, res) => {
  // 1. 使用 Zod/Joi 確保 password 只能是 string
  // 2. 顯式轉型
  const password = String(req.body.password);
  
  const user = await db.users.findOne({
    username: req.body.username,
    password: password
  });
  // ... verify hash ...
});
```

### 案例二：Prototype Pollution 攻擊

**情境：** 系統有一個功能允許使用者更新設定，使用遞迴合併。
**Payload:**
```json
{
  "theme": "dark",
  "__proto__": {
    "isAdmin": true
  }
}
```
**後果：** 如果合併邏輯不安全，之後在系統中建立的任何空物件 `const user = {}`，存取 `user.isAdmin` 都會變成 `true`，導致權限提升。

**防禦：**
```javascript
// 使用安全的 merge function
import { merge } from 'lodash'; // 確保版本是最新的

// 或者在處理輸入時過濾危險 Key
const safeMerge = (target, source) => {
  for (let key in source) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    // ... merge logic
  }
  return target;
};
```

### 案例三：NPM Supply Chain Attack (惡意腳本)

**情境：** 開發者安裝了一個名為 `cross-env-s` (惡意模仿 `cross-env`) 的套件。該套件在 `postinstall` script 中包含將環境變數（含 AWS Key）上傳到駭客伺服器的程式碼。

**防禦流程：**
1.  安裝時使用 `--ignore-scripts` 防止自動執行。
2.  在 CI Pipeline 中設定 `npm audit --audit-level=high`，若有高風險漏洞則 Build Fail。
3.  使用 `npm ci` 而非 `npm install` 確保安裝的是 `package-lock.json` 中鎖定的確切版本。