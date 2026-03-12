# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，安全性不再只是「寫出沒有 bug 的程式碼」，而是關於「設計具有防禦縱深（Defense in Depth）的架構」。JavaScript 作為 Web 的核心語言，其靈活性（如 Prototype chain）與瀏覽器的執行環境（DOM access）使其成為攻擊者的主要目標。本章不只討論語法層面的修補，更著重於瀏覽器安全模型的理解與系統設計層面的防禦。

For senior engineers, security is no longer just about "writing bug-free code"; it is about "designing architectures with Defense in Depth." As the core language of the Web, JavaScript's flexibility (e.g., Prototype chain) and its browser execution environment (DOM access) make it a primary target for attackers. This chapter focuses not only on syntax-level patches but also on understanding the browser security model and defense at the system design level.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **深入理解瀏覽器安全模型**：清楚解釋 Same-Origin Policy (SOP) 的運作機制及其例外（CORS）。
    **Deeply understand the browser security model:** Clearly explain the mechanism of the Same-Origin Policy (SOP) and its exceptions (CORS).
2.  **識別並防禦 JS 特有攻擊**：不僅是 XSS 與 CSRF，還包括 Prototype Pollution 與 Supply Chain Attacks。
    **Identify and defend against JS-specific attacks:** Not just XSS and CSRF, but also Prototype Pollution and Supply Chain Attacks.
3.  **設計安全的狀態管理機制**：在 System Design 面試中，針對 JWT vs. Session Cookies 的儲存與傳輸做出正確的資安權衡。
    **Design secure state management mechanisms:** Make correct security trade-offs regarding the storage and transmission of JWT vs. Session Cookies in System Design interviews.
4.  **實作 Content Security Policy (CSP)**：理解如何配置 CSP 來作為 XSS 的最後一道防線。
    **Implement Content Security Policy (CSP):** Understand how to configure CSP as the last line of defense against XSS.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 瀏覽器即監獄 (The Browser as a Jail)

將瀏覽器想像成一個充滿不同「囚犯（Scripts）」的監獄。每個囚犯都來自不同的幫派（Origin）。
Imagine the browser as a jail filled with different "prisoners" (Scripts). Each prisoner belongs to a different gang (Origin).

-   **Same-Origin Policy (SOP)**：這是監獄的鐵律。來自 A 幫派的囚犯不能隨意觸碰 B 幫派的資源（DOM, Cookie, LocalStorage）。
    **Same-Origin Policy (SOP):** This is the iron rule of the jail. Prisoners from Gang A cannot arbitrarily touch the resources (DOM, Cookie, LocalStorage) of Gang B.
    -   **Origin 定義**：`Protocol` + `Host` + `Port` 必須完全相同。
    -   **Definition of Origin:** `Protocol` + `Host` + `Port` must be identical.

-   **Content Security Policy (CSP)**：這是獄警發給囚犯的「許可清單」。它規定囚犯只能跟誰說話（發送請求）、只能吃哪裡的食物（加載 Script）。
    **Content Security Policy (CSP):** This is the "allowlist" given to prisoners by the guards. It dictates whom the prisoners can talk to (send requests) and where they can eat food from (load scripts).

## 2.2 常見攻擊向量 (Common Attack Vectors)

### XSS (Cross-Site Scripting)
攻擊者將惡意腳本注入到受害者的瀏覽器中執行。
Attackers inject malicious scripts to be executed in the victim's browser.

*   **Stored XSS**: 惡意腳本存於 DB，讀取時執行（如留言板）。
    **Stored XSS:** Malicious script stored in DB, executed upon retrieval (e.g., comment section).
*   **Reflected XSS**: 惡意腳本在 URL 參數中，伺服器反射回瀏覽器執行。
    **Reflected XSS:** Malicious script in URL parameters, reflected by the server to the browser for execution.
*   **DOM-based XSS**: 完全在 Client 端發生，JS 讀取惡意輸入並寫入 DOM。
    **DOM-based XSS:** Happens entirely on the Client side; JS reads malicious input and writes to the DOM.

### CSRF (Cross-Site Request Forgery)
攻擊者利用使用者「已登入的身分（Cookie）」，在使用者不知情下向伺服器發送請求。
Attackers exploit the user's "authenticated identity (Cookie)" to send requests to the server without the user's knowledge.

> **Mental Model 差異**：XSS 是「偷你的鑰匙進你家（執行代碼）」；CSRF 是「騙你把鑰匙交給快遞員去開你家的門（利用現有憑證）」。
> **Mental Model Difference:** XSS is "stealing your keys to enter your house (executing code)"; CSRF is "tricking you into giving your keys to a courier to open your door (exploiting existing credentials)."

### Prototype Pollution
JavaScript 特有的攻擊。攻擊者透過修改 `Object.prototype`，導致所有物件都繼承惡意屬性，可能導致 DoS 或 RCE（遠端代碼執行）。
A JavaScript-specific attack. Attackers modify `Object.prototype`, causing all objects to inherit malicious properties, potentially leading to DoS or RCE (Remote Code Execution).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，安全性不是單點功能，而是分層防禦（Defense in Depth）。

In large-scale distributed systems, security is not a single feature but Defense in Depth.

## 3.1 身份驗證儲存策略 (Auth Storage Strategy)

在 System Design 面試中，常被問到：「Token 應該存哪裡？」
In System Design interviews, a common question is: "Where should tokens be stored?"

| Storage | Vulnerability | Mitigation |
| :--- | :--- | :--- |
| **LocalStorage / SessionStorage** | **High XSS Risk**. Any JS running on the page can read `localStorage`. | Requires strict XSS prevention. Not recommended for sensitive tokens (Refresh Tokens). |
| **Cookie (Standard)** | **CSRF Risk**. JS can read it if `HttpOnly` is false. | Use CSRF Tokens. |
| **Cookie (HttpOnly + Secure + SameSite)** | **Low Risk**. JS cannot read it (mitigates XSS theft). `SameSite=Strict` mitigates CSRF. | **Best Practice for Web Apps**. |

**設計決策 (Design Decision):**
對於 Web 應用，優先使用 `HttpOnly` Cookie 儲存 Access/Refresh Token。這能有效防止 XSS 攻擊者直接竊取 Token（雖然他們仍可透過 XSS 發起請求，但無法將 Token 傳送到外部伺服器）。

For Web applications, prioritize using `HttpOnly` Cookies to store Access/Refresh Tokens. This effectively prevents XSS attackers from directly stealing the Token (although they can still initiate requests via XSS, they cannot exfiltrate the Token to an external server).

## 3.2 CSP 的生產環境部署 (CSP in Production)

在實務中，直接開啟嚴格的 CSP 會導致大量功能損壞。正確的導入流程如下：
In practice, enabling strict CSP directly breaks many features. The correct adoption process is:

1.  **Report-Only Mode**: 設定 `Content-Security-Policy-Report-Only` header。瀏覽器會回報違規但不阻擋執行。
    **Report-Only Mode:** Set the `Content-Security-Policy-Report-Only` header. Browsers report violations but do not block execution.
2.  **Log Collection**: 將報告發送到後端（如 ELK stack 或 Sentry），分析誤報與潛在攻擊。
    **Log Collection:** Send reports to the backend (e.g., ELK stack or Sentry) to analyze false positives and potential attacks.
3.  **Enforcement**: 逐步修正程式碼後，切換為 `Content-Security-Policy` 進行阻擋。
    **Enforcement:** After incrementally fixing the code, switch to `Content-Security-Policy` to block violations.

---

# 4. 逐步示例：Prototype Pollution (Walkthrough: Prototype Pollution)

這是一個資深工程師必須懂，但中階工程師常忽略的 JS 特性漏洞。
This is a vulnerability that senior engineers must understand, but mid-level engineers often overlook.

### 4.1 問題背景 (Scenario)
你正在開發一個能夠合併使用者設定檔的函式 `mergeConfig(target, input)`，常見於處理 JSON payload。

You are developing a function `mergeConfig(target, input)` to merge user configurations, commonly seen when handling JSON payloads.

### 4.2 Naive Implementation (Vulnerable)

```javascript
// 遞迴合併物件 (Recursive merge)
function merge(target, source) {
  for (let key in source) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) {
        target[key] = {};
      }
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

### 4.3 The Attack (攻擊手法)

攻擊者傳送一個精心設計的 JSON：
An attacker sends a crafted JSON:

```javascript
const maliciousPayload = JSON.parse('{"__proto__": {"isAdmin": true}}');

const config = {};
merge(config, maliciousPayload);

const user = {};
console.log(user.isAdmin); // true! 污染成功 (Pollution successful)
```

**發生了什麼？ (What happened?)**
因為 `config["__proto__"]` 實際上指向了 `Object.prototype`。當我們執行 `target[key] = source[key]` 時，我們實際上是在全域的 `Object.prototype` 上新增了 `isAdmin: true`。系統中所有後續建立的物件，若沒有自己的 `isAdmin` 屬性，都會向上查找到這個值。

Because `config["__proto__"]` actually points to `Object.prototype`. When we execute `target[key] = source[key]`, we are actually adding `isAdmin: true` to the global `Object.prototype`. All subsequently created objects in the system, if they don't have their own `isAdmin` property, will look up the prototype chain and find this value.

### 4.4 The Fix (修正方案)

**方法 A：阻擋危險 Key (Block Dangerous Keys)**

```javascript
function safeMerge(target, source) {
  for (let key in source) {
    // 檢查是否為危險 key (Check for dangerous keys)
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    // ... rest of the logic
  }
}
```

**方法 B：使用無 Prototype 的物件 (Use Prototype-less Objects)**
如果 `target` 是用 `Object.create(null)` 建立的，它就沒有 `__proto__`，攻擊無效。

If `target` is created using `Object.create(null)`, it has no `__proto__`, rendering the attack ineffective.

**方法 C：使用 Map (Use Map)**
在可能的情況下，使用 `Map` 代替 `Object` 儲存鍵值對，因為 `Map` 不受 Prototype Pollution 影響。

Where possible, use `Map` instead of `Object` to store key-value pairs, as `Map` is immune to Prototype Pollution.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 過度依賴前端驗證 (Over-reliance on Frontend Validation)
*   **錯誤 (Pitfall)**: 在 React/Vue 表單中做驗證，後端直接信任輸入。
    **Pitfall:** Validating in React/Vue forms and the backend trusting the input directly.
*   **後果 (Consequence)**: 攻擊者可以用 `curl` 或 Postman 繞過前端直接打 API。
    **Consequence:** Attackers can bypass the frontend using `curl` or Postman to hit the API directly.
*   **修正 (Fix)**: 前端驗證是為了 UX，後端驗證與 Sanitization 才是為了安全。
    **Fix:** Frontend validation is for UX; backend validation and sanitization are for security.

## 5.2 錯誤使用 `dangerouslySetInnerHTML`
*   **錯誤 (Pitfall)**: 直接將 API 回傳的 HTML 字串渲染到 React 的 `dangerouslySetInnerHTML` (或 Vue 的 `v-html`)。
    **Pitfall:** Rendering HTML strings returned from an API directly into React's `dangerouslySetInnerHTML` (or Vue's `v-html`).
*   **修正 (Fix)**: 必須先經過 Sanitizer (如 `DOMPurify`) 處理。
    **Fix:** Must be processed by a Sanitizer (e.g., `DOMPurify`) first.

```javascript
import DOMPurify from 'dompurify';

// Safe
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(dirtyHTML) }} />
```

## 5.3 誤解 SameSite Cookie 屬性
*   **錯誤 (Pitfall)**: 以為 `SameSite=None` 只是為了解決跨域問題，卻忘了加上 `Secure`。
    **Pitfall:** Thinking `SameSite=None` is just for solving cross-origin issues, but forgetting to add `Secure`.
*   **修正 (Fix)**: 現代瀏覽器強制規定，若 `SameSite=None`，必須同時設定 `Secure` (HTTPS)。建議預設使用 `SameSite=Lax` 或 `Strict`。
    **Fix:** Modern browsers enforce that if `SameSite=None`, `Secure` (HTTPS) must also be set. Default to `SameSite=Lax` or `Strict` is recommended.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試候選人，或在團隊 Code Review 時發起討論。
These questions can be used to interview candidates or initiate discussions during team Code Reviews.

## Q1: "我們應該將 JWT 存在 LocalStorage 還是 Cookie？請分析優缺點。"
**"Should we store JWT in LocalStorage or Cookies? Analyze the pros and cons."**

*   **高分回答要點 (Key Points for High Score)**:
    *   **LocalStorage**: 易受 XSS 攻擊（JS 可讀取）。優點是方便前端處理，且無 CSRF 問題（因為不會自動隨請求發送）。
    *   **Cookie (HttpOnly)**: 防止 XSS 竊取 Token。缺點是易受 CSRF 攻擊，需搭配 `SameSite` 屬性或 CSRF Token。
    *   **結論**: 推薦 `HttpOnly` + `Secure` + `SameSite=Strict/Lax` Cookie，這是目前最安全的 Web 實踐。

## Q2: "請解釋什麼是 Prototype Pollution，以及如何在 Node.js 服務中防範它？"
**"Explain what Prototype Pollution is and how to prevent it in a Node.js service."**

*   **高分回答要點 (Key Points for High Score)**:
    *   解釋 JS 原型鏈機制與 `__proto__` 的危險性。
    *   提到這常發生在 `merge` 或 `clone` 遞迴函式中。
    *   防範：使用 `Object.create(null)`、凍結原型 `Object.freeze(Object.prototype)`、或使用經過資安稽核的 library (如 lodash 最新版)。

## Q3: "如果我們的網站允許使用者上傳 SVG 圖片，會有什麼安全風險？"
**"If our website allows users to upload SVG images, what are the security risks?"**

*   **高分回答要點 (Key Points for High Score)**:
    *   SVG 是 XML 格式，可以內嵌 `<script>` 標籤。
    *   若直接在瀏覽器顯示使用者上傳的 SVG，可能觸發 Stored XSS。
    *   解決方案：使用 CSP `object-src 'none'`，或在伺服器端使用工具（如 `svg-purge`）清洗 SVG 內容，或強制以 `Content-Disposition: attachment` 下載而非預覽。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Never Trust Input**: 所有的輸入（URL, Body, Headers, DB data）都應視為不可信，必須進行 Validation 與 Sanitization。
2.  **SOP is the Baseline**: 理解 Same-Origin Policy 是瀏覽器的基礎，CORS 是放寬限制的機制，而非安全功能。
3.  **CSP is Defense-in-Depth**: CSP 不能取代 Sanitization，但能作為防止 XSS 執行的最後防線。
4.  **HttpOnly Cookies**: 儲存敏感 Token 的首選，能大幅降低 XSS 的影響力。
5.  **Prototype Pollution**: JS 特有的隱蔽殺手，處理物件合併時務必小心 `__proto__`。

## 後續延伸 (Next Steps)
*   **實作 (Practice)**: 在你的專案中導入 `DOMPurify` 或設定基本的 CSP Header。
*   **閱讀 (Read)**: 深入研究 [OWASP Top 10](https://owasp.org/www-project-top-ten/) 中與 JavaScript 相關的項目。
*   **下一章 (Next Chapter)**: **JavaScript 效能優化 (Performance Optimization)** —— 探討 Event Loop 阻塞、Memory Leaks 與 Critical Rendering Path。