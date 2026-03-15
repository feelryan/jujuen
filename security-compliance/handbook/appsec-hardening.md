# 應用程式安全加固與防禦 / Application Security Hardening & Defense

## Mental model｜心智模型

在進行應用程式加固時，工程師不應將安全視為「功能的附加元件」，而應視為資料流動的「過濾管道」。核心心智模型建立在 **"Zero Trust for Input, Context-Aware for Output"（對輸入零信任，對輸出感知情境）** 之上。

### The Fortress Gate Analogy (堡壘閘門比喻)

想像應用程式是一座堡壘，所有的外部資料（HTTP Request、Database Result、Third-party API response）都是試圖進入的訪客。

1.  **邊界防禦 (Perimeter Defense / Secure Headers)**：
    這是護城河與城牆。透過 HTTP Headers 告訴瀏覽器該如何表現，拒絕執行未授權的腳本（CSP），強制使用 HTTPS（HSTS），防止被嵌入惡意 iframe（X-Frame-Options）。
2.  **入口檢查 (Input Validation)**：
    這是城門守衛。只允許持有「通行證」（符合 Schema 定義）的人進入。**預設拒絕所有內容**，只放行已知安全的格式（Allow-listing）。
3.  **內部隔離 (Parameterized Queries / Logic)**：
    進入堡壘後，訪客（資料）不能隨意觸碰機關（程式碼）。資料與指令必須嚴格分離，避免 SQL Injection 或 Command Injection。
4.  **出口偽裝 (Output Encoding)**：
    當資料要被送出堡壘展示給公眾（瀏覽器）時，必須根據展示場合（HTML, JS, CSS）進行適當的包裝與轉義，確保它被視為純文字而非可執行的指令。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Positive Validation Model (正向驗證模式 / Allow-listing)
永遠不要嘗試列舉所有「壞的字元」（Blacklisting），因為攻擊者總能找到繞過的方法（例如使用 Unicode 變體）。
*   **Pattern**: 定義資料的嚴格 Schema（型別、長度、格式、範圍）。
*   **Tools**: 使用成熟的驗證庫，如 `Zod` (TypeScript), `Pydantic` (Python), `Joi`, `Hibernate Validator` (Java)。

### 2. Context-Aware Output Encoding (情境感知輸出編碼)
防禦 XSS 的關鍵在於「資料放在哪裡」。同一個字串在 HTML Body、HTML Attribute 或 JavaScript 變數中需要不同的編碼方式。
*   **Pattern**: 使用現代框架（React, Vue, Angular）的預設資料綁定，它們會自動處理大部分 Context。
*   **Legacy Systems**: 若需手動處理，請使用專門的 Security Library（如 OWASP Java Encoder）而非簡單的字串替換。

### 3. Separation of Data and Code (資料與程式碼分離)
這是防禦 Injection 類攻擊（SQLi, NoSQLi, OS Command Injection）的黃金法則。
*   **Pattern**: **Prepared Statements (預處理語句)**。資料庫驅動程式會將 SQL 模板與參數分開傳送，資料永遠不會被解析為 SQL 指令。
*   **ORM**: 使用 ORM (Entity Framework, TypeORM, Prisma) 通常預設包含了此防護，但需注意避免使用 `raw query` 介面。

### 4. Defense in Depth via Headers (透過標頭的縱深防禦)
HTTP Security Headers 是成本最低但效益極高的防禦層。
*   **CSP (Content Security Policy)**: 限制資源（Script, Style, Image）的載入來源，是防禦 XSS 的最後一道防線。
*   **HSTS**: 強制瀏覽器只透過 HTTPS 連線。
*   **X-Content-Type-Options**: 設定 `nosniff`，防止瀏覽器錯誤猜測檔案類型（MIME Sniffing）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Sanitization" Trap (淨化陷阱)
*   **Anti-pattern**: 試圖「修復」惡意輸入（例如刪除 `<script>` 標籤）。
*   **Why**: 這是非常困難且容易出錯的。攻擊者可以使用 `<img onerror=...>` 或嵌套標籤 `<scr<script>ipt>` 來繞過。
*   **Fix**: **Reject (拒絕)** 不合規的輸入，而不是嘗試清洗它。清洗（Sanitization）通常只用於必須接受 Rich Text（如 HTML 編輯器）的特殊場景，且必須使用專門庫（如 DOMPurify）。

### 2. Client-Side Validation Only (僅依賴前端驗證)
*   **Anti-pattern**: 認為前端表單有檢查 Email 格式就安全了。
*   **Why**: 攻擊者可以輕易透過 `curl` 或 Postman 繞過前端直接打 API。
*   **Fix**: 前端驗證是為了 UX（使用者體驗），後端驗證才是為了 Security（安全）。**後端必須重新驗證所有輸入。**

### 3. Verbose Error Messages (冗長的錯誤訊息)
*   **Anti-pattern**: 在 API Response 中直接回傳 Database Stack Trace 或詳細的系統錯誤。
*   **Why**: 這洩漏了後端架構資訊（如使用的 DB 版本、Table 名稱），有助於攻擊者構建 Payload。
*   **Fix**: 記錄詳細錯誤到 Log，但回傳給使用者通用的錯誤訊息（如 "Internal Server Error" 或 "Invalid Request"）。

### 4. Misconfigured CSP (錯誤配置的 CSP)
*   **Anti-pattern**: 設定了 CSP 但加上 `unsafe-inline` 或 `unsafe-eval`。
*   **Why**: 這基本上讓 CSP 失效，因為攻擊者通常就是透過 Inline Script 進行 XSS 攻擊。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或開發階段，請對照以下清單：

### Input Validation Checklist
- [ ] **邊界檢查**：是否限制了字串最大長度（防止 DoS）？數值是否在合理範圍？
- [ ] **型別強制**：API 是否拒絕了錯誤的型別（例如預期 JSON 卻收到 XML，或預期 Integer 卻收到 String）？
- [ ] **白名單驗證**：是否使用 Schema Library 驗證所有欄位？（拒絕 unknown fields）。
- [ ] **檔案上傳**：是否檢查了 Magic Bytes 而不僅僅是副檔名？是否重命名了上傳檔案以防止覆蓋或執行？

### Output & Processing Checklist
- [ ] **SQL Injection**：是否所有 DB 查詢都使用了 Parameterized Queries 或 ORM 方法？（搜尋程式碼中的字串串接 `+` 或 `fmt.Sprintf` SQL 語句）。
- [ ] **XSS 防禦**：是否避免使用 `dangerouslySetInnerHTML` (React) 或 `v-html` (Vue)？如果必須使用，是否先經過 `DOMPurify`？
- [ ] **Log Injection**：寫入 Log 前是否移除了換行符號（CRLF），防止 Log Forging？

### Security Headers Checklist (Infrastructure/Middleware Level)
- [ ] `Strict-Transport-Security`: `max-age=63072000; includeSubDomains; preload`
- [ ] `X-Content-Type-Options`: `nosniff`
- [ ] `X-Frame-Options`: `DENY` or `SAMEORIGIN`
- [ ] `Content-Security-Policy`: 至少設定 `default-src 'self'` 並移除 `unsafe-inline`。
- [ ] `Referrer-Policy`: `strict-origin-when-cross-origin`

---

## Real-world examples｜實戰案例

### Example 1: SQL Injection Defense (Node.js)

**❌ Vulnerable Code (Anti-pattern):**
直接將使用者輸入串接到 SQL 字串中。
```javascript
// 攻擊者輸入: ' OR '1'='1
const query = "SELECT * FROM users WHERE username = '" + req.body.username + "'";
db.execute(query); 
// 實際執行: SELECT * FROM users WHERE username = '' OR '1'='1' (Dump all users)
```

**✅ Secure Code (Best Practice):**
使用 Parameterized Query，資料庫驅動會將輸入視為純資料。
```javascript
const query = "SELECT * FROM users WHERE username = ?";
db.execute(query, [req.body.username]);
// 實際執行: 資料庫尋找 username 確實等於 "' OR '1'='1" 的使用者 (找不到)
```

### Example 2: Secure Headers Configuration (Express.js with Helmet)

在 Node.js 專案中，不要手動設定每個 Header，使用 `helmet` 中介軟體是標準做法。

```javascript
const express = require('express');
const helmet = require('helmet');
const app = express();

// ✅ 自動設定大約 15 個安全相關的 Headers
app.use(helmet());

// ✅ 客製化 CSP (進階)
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "trusted-cdn.com"], // 只允許從自己與特定 CDN 載入腳本
      objectSrc: ["'none'"], // 禁止 Flash 等物件
      upgradeInsecureRequests: [], // 強制升級 HTTP 請求到 HTTPS
    },
  })
);
```

### Example 3: Input Validation with Zod (TypeScript)

不要在 Controller 寫一堆 `if (req.body.email) ...`，使用 Schema 宣告式驗證。

```typescript
import { z } from "zod";

// ✅ 定義嚴格的 Schema
const UserSignupSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/), // 白名單 Regex
  email: z.string().email(),
  age: z.number().int().min(18).max(120), // 範圍檢查
  role: z.enum(["user", "admin"]), // 嚴格 Enum
});

// 在 API Handler 中使用
app.post("/signup", (req, res) => {
  const result = UserSignupSchema.safeParse(req.body);
  
  if (!result.success) {
    // ❌ 驗證失敗：回傳 400 與結構化錯誤，但不洩漏系統細節
    return res.status(400).json({ error: "Invalid input data", details: result.error.issues });
  }

  // ✅ 驗證成功：result.data 是型別安全且乾淨的資料
  createUser(result.data);
});
```