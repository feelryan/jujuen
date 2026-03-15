# 安全性防護與常見漏洞 / Security Checklist & Common Vulnerabilities

## Mental model｜心智模型

在 JavaScript 生態系中，安全性問題通常源於語言本身的靈活性（Flexibility）以及執行環境（Browser vs. Node.js）的特性。要建立正確的安全心智模型，必須理解以下三個核心觀念：

### 1. Data vs. Code Context (資料與程式碼的邊界)
大多數的注入攻擊（XSS, Command Injection, SQL Injection）本質上都是**執行環境無法區分「開發者寫的程式碼」與「使用者輸入的資料」**。
- **Browser:** 當瀏覽器把使用者輸入的字串當作 HTML 標籤或 JavaScript 解析時（如 `innerHTML`），XSS 就發生了。
- **Node.js:** 當 `eval()` 或 `child_process` 把使用者輸入當作指令執行時，RCE (Remote Code Execution) 就發生了。
- **Mental Model:** 永遠假設所有外部輸入（URL 參數、API 回傳、Form Data）都是「受污染的資料」，必須經過 **Sanitization (消毒)** 或 **Encoding (編碼)** 才能進入「執行環境」。

### 2. Prototype Chain as Shared State (原型鏈即共享狀態)
JavaScript 的原型繼承機制意味著 `Object.prototype` 是一個全域共享的物件。
- 如果攻擊者能修改 `Object.prototype`（即 **Prototype Pollution**），他就能影響應用程式中**所有**物件的行為。這在合併物件（Merge）或解析 JSON 時最常發生。
- **Mental Model:** JavaScript 的物件預設不是封閉的容器，它們連接著全域的根。處理不受信任的物件結構時，必須切斷或檢查這個連結。

### 3. The Supply Chain Risk (供應鏈風險)
現代 JavaScript 開發極度依賴 `npm`。你的程式碼安全性 = 你的程式碼 + `node_modules` 中成千上萬個依賴套件的安全性。
- **Mental Model:** `npm install` 是一個信任行為。任何一個深層依賴被植入惡意程式碼，你的應用程式就等同於門戶大開。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Input Validation & Output Encoding (輸入驗證與輸出編碼)
- **Schema Validation:** 使用 **Zod**, **Joi**, 或 **Ajv** 等函式庫在資料進入系統的第一層（API Endpoint 或 Form Submit）就進行嚴格的型別與格式驗證。不要只檢查「是否存在」，要檢查「是否符合預期結構」。
- **Context-Aware Encoding:** 根據資料輸出的位置（HTML Body, Attribute, JavaScript Variable, CSS）採用不同的編碼策略。

### 2. Defense against XSS (XSS 防禦策略)
- **Content Security Policy (CSP):** 設定 HTTP Header `Content-Security-Policy`。這是防禦 XSS 的最後一道防線，限制瀏覽器只能載入受信任網域的 Script，並禁止 Inline Script。
- **Sanitization Libraries:** 如果必須渲染使用者提供的 HTML（例如 Rich Text Editor），**絕對不要**自己寫 Regex 過濾。請使用經過戰場驗證的庫，如 **DOMPurify**。
- **Framework Built-ins:** 善用 React (`{variable}`), Vue (`{{variable}}`), Angular 預設的自動跳脫（Auto-escaping）功能。

### 3. Preventing Prototype Pollution (防止原型污染)
- **Map over Object:** 當你需要一個 Key-Value 儲存結構且 Key 來自使用者輸入時，優先使用 `new Map()` 而不是 Plain Object `{}`。`Map` 沒有原型鏈污染問題。
- **Object.create(null):** 如果必須用 Object，使用 `const safeObj = Object.create(null)` 建立沒有原型的物件。
- **Freeze Prototypes:** 在應用程式啟動時，使用 `Object.freeze(Object.prototype)`（雖然這可能會破壞某些依賴 polyfill 的舊套件，但在現代開發中是強大的防禦手段）。

### 4. Node.js Security Hardening (Node.js 加固)
- **Helmet:** 使用 `helmet` 中間件自動設定安全的 HTTP Headers (HSTS, X-Frame-Options, X-XSS-Protection 等)。
- **Avoid Blocking Event Loop (ReDoS):** 避免在處理使用者輸入時使用可能導致災難性回溯（Catastrophic Backtracking）的 Regular Expression。使用 `validator.js` 等庫，或使用 `re2` 引擎。
- **Least Privilege:** 不要以 root 身份執行 Node.js process。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Sanitize Everything" Fallacy (試圖過濾所有東西)
- **Anti-pattern:** 試圖寫一個全域的 `cleanInput()` 函式，用 Regex 把 `<script>`, `javascript:`, `on*` 全部取代掉。
- **Why:** 黑名單永遠列不完。攻擊者可以用 `java&#09;script:` 或各種編碼繞過過濾。
- **Fix:** 採用「白名單」策略（只允許安全標籤）或使用標準庫（DOMPurify）。

### 2. Unsafe Object Merging (不安全的物件合併)
- **Anti-pattern:** 使用簡單的遞迴函式來 Deep Merge 兩個物件，卻沒有檢查 Key 是否為 `__proto__`, `constructor`, 或 `prototype`。
- **Why:** 這是 Prototype Pollution 的主要來源。
- **Fix:** 使用 `lodash.merge` (版本需更新) 或在遞迴時明確跳過危險 Key。

### 3. Blindly Trusting JWT Content (盲目信任 JWT 內容)
- **Anti-pattern:** 在前端解碼 JWT (JSON Web Token) 並直接根據 payload 中的 `isAdmin: true` 來決定顯示管理員介面，卻沒有在後端 API 再次驗證。
- **Why:** 前端的驗證只是為了 UX，後端必須永遠驗證 Signature 和權限。
- **Pitfall:** 設定 JWT `alg: none` 攻擊（雖然現代庫已修復，但實作時仍需注意）。

### 4. Using `eval()` or `new Function()`
- **Anti-pattern:** 為了動態執行邏輯或解析非標準 JSON 而使用 `eval()`。
- **Why:** 這是最危險的 JavaScript 操作，等同於把執行權限交給字串內容。
- **Fix:** 幾乎所有 `eval` 的使用場景都有更安全的替代方案（如 `JSON.parse`, `Map` 查找, 或沙箱環境 `vm2` - 需注意 `vm2` 也有歷史漏洞，建議使用 `isolated-vm`）。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或發布前，請對照以下清單：

### Frontend Security (Browser)
- [ ] **XSS:** 是否避免使用 `innerHTML`, `outerHTML`, `v-html`, `dangerouslySetInnerHTML`？若必須使用，是否經過 `DOMPurify.sanitize()`？
- [ ] **CSP:** 是否已配置 `Content-Security-Policy` Header？是否移除了 `unsafe-inline` 和 `unsafe-eval`？
- [ ] **Dependencies:** 是否檢查了第三方 Script (GTM, Ads) 的來源？
- [ ] **Storage:** 敏感資訊（Token, PII）是否避免存放在 `localStorage`？（建議使用 `HttpOnly` `Secure` Cookies 以防 XSS 竊取）。
- [ ] **Links:** 所有 `target="_blank"` 的連結是否加上了 `rel="noopener noreferrer"`？

### Backend Security (Node.js)
- [ ] **Injection:** 資料庫查詢是否使用 Parameterized Queries (ORM 通常預設支援)？避免字串串接 SQL。
- [ ] **Prototype Pollution:** 是否檢查了所有 Deep Merge 或 Object Assign 的邏輯？是否使用了 `Object.freeze(Object.prototype)` 或 Schema Validation？
- [ ] **ReDoS:** Regex 是否經過測試（如使用 regex101 或 safe-regex 工具）以避免 ReDoS 攻擊？
- [ ] **Dependencies:** 是否執行了 `npm audit`？CI/CD 流程中是否有自動化漏洞掃描（如 Snyk, Dependabot）？
- [ ] **Error Handling:** 是否確保錯誤訊息（Stack Trace）不會洩漏給終端使用者？
- [ ] **Rate Limiting:** 是否對 API 實施了 Rate Limiting (如 `express-rate-limit`) 以防 Brute Force 或 DDoS？

---

## Real-world examples｜實戰案例

### 1. Prototype Pollution Attack (原型污染攻擊)

**Vulnerable Code (常見的遞迴合併):**
```javascript
const merge = (target, source) => {
  for (const key in source) {
    if (typeof target[key] === 'object' && typeof source[key] === 'object') {
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
};

// 攻擊者輸入的 JSON payload
const payload = JSON.parse('{"__proto__": {"isAdmin": true}}');
const user = {};

merge(user, payload);

// 災難發生：現在所有新物件都預設擁有 isAdmin = true
const guest = {};
console.log(guest.isAdmin); // true (應該是 undefined)
```

**Secure Fix:**
```javascript
const merge = (target, source) => {
  for (const key in source) {
    // 1. 阻擋危險的 Key
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    // ... 其餘邏輯
  }
  return target;
};
// 或者使用 Object.create(null) 建立無原型物件
```

### 2. DOM XSS via URL Fragment (DOM 型 XSS)

**Vulnerable Code:**
開發者想把 URL hash 中的內容顯示在頁面上。
```javascript
// URL: https://example.com#<img src=x onerror=alert(1)>
const hash = decodeURIComponent(window.location.hash.slice(1));
// 直接插入 HTML
document.getElementById('welcome-msg').innerHTML = hash; 
```

**Secure Fix:**
```javascript
import DOMPurify from 'dompurify';

const hash = decodeURIComponent(window.location.hash.slice(1));
// 使用 DOMPurify 清洗
document.getElementById('welcome-msg').innerHTML = DOMPurify.sanitize(hash);

// 或者，如果不需要 HTML 標籤，只使用 textContent
document.getElementById('welcome-msg').textContent = hash;
```

### 3. ReDoS (Regular Expression Denial of Service)

**Vulnerable Code:**
用來驗證 Email 或特定格式的 Regex，若包含重複的 group `(a+)+`，容易導致災難性回溯。
```javascript
// 試圖匹配 "AAAAAAAAAAAAA!"，但在最後一個字元不匹配時，
// 引擎會嘗試所有可能的 A 的組合，導致 CPU 飆升 100% 並卡死 Event Loop。
const unsafeRegex = /^([a-zA-Z0-9]+\s?)+$/; 
const input = "A".repeat(10000) + "!"; 
unsafeRegex.test(input); // Node.js process hangs
```

**Secure Fix:**
- 使用 `validator` 庫。
- 避免巢狀量詞（Nested Quantifiers）。
- 使用 `re2` (Google 的安全 Regex 引擎) 的 Node.js binding，它保證線性時間複雜度。