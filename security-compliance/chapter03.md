# 應用程式安全與 OWASP 防禦
# AppSec & OWASP Top 10 Mitigation

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，熟悉 OWASP Top 10 不僅是為了通過面試，更是為了在系統設計階段建立「縱深防禦（Defense in Depth）」的思維。本章不只羅列漏洞定義，更著重於如何在架構層面與程式碼層面實作有效的緩解措施（Mitigation）。
For Senior Engineers, familiarity with the OWASP Top 10 is not just for passing interviews, but for establishing a "Defense in Depth" mindset during the system design phase. This chapter goes beyond listing vulnerability definitions, focusing on implementing effective mitigation strategies at both the architectural and code levels.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **識別與防禦核心漏洞**：精準解釋 SQL Injection、XSS、CSRF 與 SSRF 的成因，並能實作對應的防禦模式（如 Prepared Statements, CSP, Anti-CSRF Tokens）。
    **Identify and Mitigate Core Vulnerabilities**: Accurately explain the root causes of SQL Injection, XSS, CSRF, and SSRF, and implement corresponding defense patterns (e.g., Prepared Statements, CSP, Anti-CSRF Tokens).
2.  **設計安全的輸入與輸出機制**：區分 Input Validation（輸入驗證）與 Output Encoding（輸出編碼）的適用場景，並理解為何「黑名單（Blacklisting）」通常是無效的。
    **Design Secure Input and Output Mechanisms**: Distinguish between the use cases for Input Validation and Output Encoding, and understand why "Blacklisting" is generally ineffective.
3.  **在系統設計面試中應對安全題型**：當面試官要求「設計一個安全的 URL 預覽服務」或「防止資料庫被注入」時，能提出包含網路隔離、權限控管與應用層過濾的完整方案。
    **Handle Security Questions in System Design Interviews**: When asked to "design a secure URL preview service" or "prevent database injection," be able to propose a comprehensive solution involving network isolation, access control, and application-layer filtering.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 信任邊界（Trust Boundary）
### 2.1 The Trust Boundary

最核心的心智模型是「信任邊界」。任何跨越邊界進入系統的數據（來自使用者、第三方 API、甚至內部微服務）都應被視為**不可信（Untrusted）**。
The core mental model is the "Trust Boundary." Any data crossing the boundary into the system (from users, third-party APIs, or even internal microservices) must be treated as **Untrusted**.

*   **直覺類比**：機場安檢。
    *   **Landside (Untrusted)**：任何人都可以進入，攜帶任何物品。
    *   **Security Checkpoint (Validation/Sanitization)**：在此處過濾危險物品。
    *   **Airside (Trusted)**：假設此區域相對安全，但仍需警惕內部威脅。
*   **Analogy**: Airport Security.
    *   **Landside (Untrusted)**: Anyone can enter carrying anything.
    *   **Security Checkpoint (Validation/Sanitization)**: Dangerous items are filtered here.
    *   **Airside (Trusted)**: Assumed relatively safe, but internal threats must still be monitored.

### 2.2 注入與執行環境混淆
### 2.2 Injection & Context Confusion

大多數漏洞（SQLi, XSS, SSRF）的本質都是**「數據被誤認為指令（Data treated as Code）」**。
The essence of most vulnerabilities (SQLi, XSS, SSRF) is **"Data treated as Code."**

*   **SQL Injection**: 使用者輸入的字串被資料庫引擎解析為 SQL 指令。
    **SQL Injection**: User input strings are parsed as SQL commands by the database engine.
*   **XSS (Cross-Site Scripting)**: 使用者輸入的腳本被瀏覽器解析為 JavaScript 並執行。
    **XSS (Cross-Site Scripting)**: User input scripts are parsed as JavaScript by the browser and executed.
*   **SSRF (Server-Side Request Forgery)**: 使用者提供的 URL 被伺服器用來發起內部網路請求。
    **SSRF (Server-Side Request Forgery)**: User-provided URLs are used by the server to initiate internal network requests.

### 2.3 關鍵術語區分
### 2.3 Key Terminology Distinction

*   **Validation (驗證)**: 檢查數據是否符合預期格式（例如：Email 格式、整數範圍）。這是在入口處做的。
    **Validation**: Checking if data conforms to expected formats (e.g., Email format, integer range). This is done at the entry point.
*   **Sanitization (淨化)**: 移除或替換危險字符（例如：移除 `<script>` 標籤）。這具有破壞性，需謹慎使用。
    **Sanitization**: Removing or replacing dangerous characters (e.g., stripping `<script>` tags). This is destructive and should be used with caution.
*   **Encoding/Escaping (編碼/跳脫)**: 將特殊字符轉換為安全形式（例如：`<` 轉為 `&lt;`），使其在特定環境（HTML, SQL）中僅被視為數據。這是防禦的最後一道防線。
    **Encoding/Escaping**: Converting special characters into safe forms (e.g., `<` to `&lt;`), ensuring they are treated only as data in a specific context (HTML, SQL). This is the last line of defense.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在大型分散式系統中，應用程式安全不是單點防禦，而是分層架構。
In large-scale distributed systems, application security is not a single point of defense but a layered architecture.

### 3.1 架構層級防禦
### 3.1 Architectural Defense

1.  **Edge / WAF (Web Application Firewall)**:
    *   **角色**：第一道防線，過濾常見的攻擊特徵（如 SQLi 掃描、惡意 User-Agent）。
    *   **限制**：無法理解複雜的業務邏輯漏洞（如 IDOR - Insecure Direct Object References）。
    *   **Role**: First line of defense, filtering common attack signatures (e.g., SQLi scans, malicious User-Agents).
    *   **Limitation**: Cannot understand complex business logic vulnerabilities (e.g., IDOR).

2.  **API Gateway**:
    *   **角色**：負責 Rate Limiting（防止 DoS/暴力破解）、驗證 Auth Token。
    *   **Role**: Responsible for Rate Limiting (preventing DoS/Brute Force) and verifying Auth Tokens.

3.  **Application Layer (Microservices)**:
    *   **角色**：Input Validation（強型別檢查）、Context-aware Output Encoding。
    *   **Role**: Input Validation (strong typing), Context-aware Output Encoding.

4.  **Data Layer**:
    *   **角色**：使用 Prepared Statements，實施 Least Privilege（最小權限原則）。
    *   **Role**: Using Prepared Statements, enforcing Least Privilege.

### 3.2 對系統屬性的影響
### 3.2 Impact on System Attributes

*   **Performance**: 過度的 Sanitization 或複雜的 WAF 規則可能增加 Latency。應盡量利用框架內建的高效機制（如 React 的自動 Escaping）。
    **Performance**: Excessive Sanitization or complex WAF rules can increase latency. Leverage efficient built-in framework mechanisms (like React's automatic escaping) whenever possible.
*   **Observability**: 安全異常（如大量的 403 Forbidden 或 SQL 語法錯誤）必須被 Log 並觸發 Alert。這是檢測攻擊正在進行的關鍵。
    **Observability**: Security anomalies (e.g., spikes in 403 Forbidden or SQL syntax errors) must be logged and trigger alerts. This is key to detecting ongoing attacks.

---

## 4. 逐步示例
## 4. Walkthrough / Example

### 案例一：防禦 SQL Injection (SQLi)
### Case 1: Mitigating SQL Injection (SQLi)

#### 背景 (Context)
一個使用者登入功能，接收 `username` 與 `password`。
A user login feature receiving `username` and `password`.

#### Naive Approach (Vulnerable)
直接字串串接。這在 20 年前很常見，但現在仍會出現在動態構建複雜查詢的 legacy code 中。
Direct string concatenation. Common 20 years ago, but still appears in legacy code that dynamically builds complex queries.

```python
# VULNERABLE CODE - DO NOT USE
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
# If user_input is:  ' OR '1'='1
# Query becomes: SELECT * FROM users WHERE username = '' OR '1'='1'
```

#### Mature Solution (Prepared Statements)
使用參數化查詢（Parameterized Queries）。
Using Parameterized Queries.

```python
# SECURE CODE (Python DB-API style)
sql = "SELECT * FROM users WHERE username = %s"
cursor.execute(sql, (user_input,))
```

*   **為何有效？** 資料庫將 SQL 模板與數據分開傳送。資料庫引擎會先編譯 SQL 結構（AST），然後將 `user_input` 視為純粹的字面值（Literal），無論裡面包含什麼引號或關鍵字，都不會改變語法結構。
*   **Why it works?** The database receives the SQL template and data separately. The DB engine compiles the SQL structure (AST) first, then treats `user_input` strictly as a literal value. No matter what quotes or keywords it contains, the syntax structure remains unchanged.

#### 進階思考：ORM 是萬靈丹嗎？
#### Deep Dive: Are ORMs a Silver Bullet?

大多時候是，但仍有例外。例如在 Hibernate/JPA 或 Django 中使用「原生 SQL 片段」時。
Mostly yes, but there are exceptions. For example, when using "raw SQL fragments" in Hibernate/JPA or Django.

```python
# Django Example - Potential Vulnerability in Raw SQL
# VULNERABLE if using format strings
User.objects.raw("SELECT * FROM auth_user WHERE username = '%s'" % username)

# SECURE
User.objects.raw("SELECT * FROM auth_user WHERE username = %s", [username])
```

---

### 案例二：防禦 Server-Side Request Forgery (SSRF)
### Case 2: Mitigating Server-Side Request Forgery (SSRF)

#### 背景 (Context)
系統有一個功能：「輸入圖片 URL，伺服器下載並產生縮圖」。
System feature: "Input an image URL, server downloads it and generates a thumbnail."

#### 攻擊場景 (Attack Scenario)
攻擊者輸入雲端環境的 Metadata URL（例如 AWS EC2）：`http://169.254.169.254/latest/meta-data/iam/security-credentials/`。
伺服器若無防護，會下載此內容並回傳給攻擊者，導致 AWS Credential 洩漏。
Attacker inputs a cloud metadata URL (e.g., AWS EC2): `http://169.254.169.254/latest/meta-data/iam/security-credentials/`.
If unprotected, the server downloads this content and returns it to the attacker, leaking AWS Credentials.

#### 防禦步驟 (Mitigation Steps)

1.  **Input Validation (Allowlisting)**:
    限制 URL 必須以 `https://` 開頭，且域名必須在白名單內（如果業務允許）。
    Restrict URLs to start with `https://` and ensure the domain is in an allowlist (if business logic permits).

2.  **Network Layer Defense (Egress Filtering)**:
    這是最有效的。在 VPC 或防火牆層級，禁止應用伺服器對內網 IP（如 `10.0.0.0/8`, `192.168.0.0/16`, `127.0.0.1`）以及 Metadata IP（`169.254.169.254`）發起請求。
    This is the most effective. At the VPC or firewall level, block the application server from initiating requests to internal IPs (e.g., `10.0.0.0/8`, `192.168.0.0/16`, `127.0.0.1`) and Metadata IPs (`169.254.169.254`).

3.  **Application Logic**:
    解析 DNS 後檢查 IP 是否為私有地址（注意 DNS Rebinding 攻擊）。
    Resolve DNS and check if the IP is a private address (beware of DNS Rebinding attacks).

```python
# Pseudo-code for SSRF Check
import socket
from urllib.parse import urlparse

def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return False
    
    hostname = parsed.hostname
    ip_address = socket.gethostbyname(hostname) # Warning: Vulnerable to DNS Rebinding race condition
    
    if is_private_ip(ip_address): # Check against 10.x, 192.168.x, 127.x, 169.254.x
        return False
        
    return True
```

*   **資深觀點**：上述程式碼有 **TOCTOU (Time-of-Check to Time-of-Use)** 漏洞。攻擊者可以在 `gethostbyname` 和實際 `requests.get` 之間快速變更 DNS 指向。最佳解法是配置專用的 HTTP Client，禁用 Redirect，並在網路層（Network Layer）阻擋內網流量。
*   **Senior View**: The code above has a **TOCTOU (Time-of-Check to Time-of-Use)** vulnerability. An attacker can change the DNS record between `gethostbyname` and the actual `requests.get`. The best solution is to configure a dedicated HTTP Client, disable Redirects, and block internal traffic at the Network Layer.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 依賴黑名單 (Relying on Blacklisting)
*   **錯誤**：試圖過濾 `<script>`, `javascript:`, `OR 1=1` 等關鍵字。
*   **Pitfall**: Trying to filter keywords like `<script>`, `javascript:`, `OR 1=1`.
*   **為何不好**：攻擊者總能找到繞過方法（例如大小寫混合 `<ScRiPt>`, URL 編碼 `%3Cscript%3E`, 或利用其他標籤 `<img onerror=...>`）。
*   **Why it's bad**: Attackers can always find bypasses (e.g., mixed case `<ScRiPt>`, URL encoding `%3Cscript%3E`, or using other tags `<img onerror=...>`).
*   **修正**：使用**白名單（Allowlisting）**驗證輸入格式，並使用**上下文相關編碼（Context-aware Encoding）**輸出。
*   **Fix**: Use **Allowlisting** for input validation and **Context-aware Encoding** for output.

### 5.2 混淆 CSRF Token 與 SameSite Cookie
### 5.2 Confusing CSRF Tokens with SameSite Cookies
*   **錯誤**：認為設定了 Cookie `SameSite=Strict` 就不需要 CSRF Token。
*   **Pitfall**: Thinking setting Cookie `SameSite=Strict` eliminates the need for CSRF Tokens.
*   **為何不好**：雖然 `SameSite` 很有用，但舊版瀏覽器不支援，且在某些跨子域（Subdomain）場景下可能不足。
*   **Why it's bad**: While `SameSite` is useful, legacy browsers don't support it, and it might be insufficient in certain cross-subdomain scenarios.
*   **修正**：採取縱深防禦。同時使用 `SameSite` Cookie 屬性 **以及** Anti-CSRF Token（如 Double Submit Cookie 模式）。
*   **Fix**: Defense in Depth. Use both `SameSite` cookie attributes **AND** Anti-CSRF Tokens (e.g., Double Submit Cookie pattern).

### 5.3 在前端做安全驗證
### 5.3 Security Validation on Frontend
*   **錯誤**：僅在 React/Vue 表單中限制輸入長度或格式，後端直接信任。
*   **Pitfall**: Limiting input length or format only in React/Vue forms, with the backend trusting it blindly.
*   **為何不好**：攻擊者可以使用 `curl` 或 Postman 直接打 API，繞過所有前端限制。
*   **Why it's bad**: Attackers can use `curl` or Postman to hit the API directly, bypassing all frontend restrictions.
*   **修正**：前端驗證是為了 UX（使用者體驗），後端驗證才是為了 Security（安全）。**後端必須重新驗證所有輸入**。
*   **Fix**: Frontend validation is for UX; Backend validation is for Security. **The backend must re-validate all inputs.**

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 如果要在一個 Legacy System 中修復 XSS 漏洞，你會如何制定策略？
### Q1: How would you strategize fixing XSS vulnerabilities in a Legacy System?

*   **高分回答要點**：
    *   **短期（止血）**：在 WAF 層開啟 XSS 過濾規則；在關鍵頁面啟用 CSP (Content Security Policy) 設為 Report-Only 模式以收集攻擊數據。
    *   **中期（重構）**：引入自動 Escaping 的模板引擎（如 React 或現代 Server-side template），逐步替換手動拼接 HTML 的程式碼。
    *   **長期（文化）**：建立 CI/CD 中的 SAST (Static Application Security Testing) 掃描。
*   **Key Points**:
    *   **Short-term (Stop the bleeding)**: Enable XSS filtering rules at the WAF level; enable CSP (Content Security Policy) in Report-Only mode on critical pages to gather attack data.
    *   **Mid-term (Refactor)**: Introduce template engines with auto-escaping (like React or modern server-side templates) to replace manual HTML concatenation.
    *   **Long-term (Culture)**: Implement SAST (Static Application Security Testing) in the CI/CD pipeline.

### Q2: 請解釋 CSRF 的原理，以及為什麼 SPA (Single Page Application) 架構下通常使用 JWT 放在 Header 比較不容易受 CSRF 攻擊？
### Q2: Explain CSRF, and why storing JWTs in Headers in an SPA architecture is generally less susceptible to CSRF?

*   **高分回答要點**：
    *   **原理**：CSRF 利用瀏覽器「自動攜帶 Cookie」的特性，誘使使用者在已登入狀態下執行非自願操作。
    *   **Header vs Cookie**：瀏覽器不會自動將 LocalStorage 中的 JWT 放入 Request Header 發送給跨站請求。攻擊者無法強迫瀏覽器加上自定義 Header（如 `Authorization: Bearer ...`），除非有 XSS 漏洞配合。
    *   **權衡**：雖然防了 CSRF，但將 Token 存於 LocalStorage 容易被 XSS 竊取。最安全的做法通常是 `HttpOnly` Cookie 搭配 CSRF Token。
*   **Key Points**:
    *   **Mechanism**: CSRF exploits the browser's behavior of "automatically sending Cookies," tricking authenticated users into performing unwanted actions.
    *   **Header vs Cookie**: Browsers do not automatically attach JWTs from LocalStorage to headers for cross-site requests. Attackers cannot force the browser to add custom headers (like `Authorization: Bearer ...`) without an accompanying XSS vulnerability.
    *   **Trade-off**: While this prevents CSRF, storing tokens in LocalStorage makes them vulnerable to XSS theft. The most secure approach is often `HttpOnly` Cookies paired with CSRF Tokens.

### Q3: 在設計一個 Webhook 系統時，如何防止 SSRF？
### Q3: How do you prevent SSRF when designing a Webhook system?

*   **高分回答要點**：
    *   強調**網路層隔離**（將負責發送 Webhook 的 Worker 放在無法存取內網的專用 Subnet）。
    *   應用層實作 **Allowlist**（只允許特定的 Port 和 Protocol）。
    *   禁止 **Redirect** 跟隨。
    *   設定極短的 **Timeout** 以防止 DoS。
*   **Key Points**:
    *   Emphasize **Network Layer Isolation** (place Webhook workers in a dedicated subnet with no internal access).
    *   Implement **Allowlisting** at the application layer (restrict Ports and Protocols).
    *   Disable **Redirect** following.
    *   Set very short **Timeouts** to prevent DoS.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Trust Boundary**: 永遠不要信任來自客戶端的數據，無論是 Header、Body 還是 URL 參數。
    **Trust Boundary**: Never trust data from the client, whether it's Headers, Body, or URL parameters.
2.  **Injection**: 發生在「數據被誤認為程式碼」時。解法是將兩者明確分離（如 Prepared Statements）。
    **Injection**: Occurs when "Data is mistaken for Code." The solution is to strictly separate them (e.g., Prepared Statements).
3.  **XSS**: 輸出編碼（Output Encoding）是關鍵。根據上下文（HTML Body, Attribute, JS）選擇正確的編碼方式。
    **XSS**: Output Encoding is key. Choose the correct encoding based on context (HTML Body, Attribute, JS).
4.  **SSRF**: 雲端時代的重大威脅。最佳防禦是在網路層（VPC/Firewall）阻擋對內網與 Metadata Service 的存取。
    **SSRF**: A major threat in the cloud era. Best defense is blocking access to internal networks and Metadata Services at the Network Layer (VPC/Firewall).
5.  **Defense in Depth**: WAF + API Gateway + App Validation + DB Constraints。單一層防護終將失效。
    **Defense in Depth**: WAF + API Gateway + App Validation + DB Constraints. Single-layer protection will eventually fail.

### 後續延伸 (Next Steps)
*   **Next Chapter**: 學習 **Authentication & Authorization (OAuth2, OIDC, RBAC)**，了解如何管理「誰可以進入系統」以及「他們能做什麼」。
*   **Action Item**: 在你的專案中檢查是否使用了 ORM 的 `raw()` 或 `nativeQuery` 功能，並確認是否使用了參數化查詢。
*   **Next Chapter**: Study **Authentication & Authorization (OAuth2, OIDC, RBAC)** to understand how to manage "who can enter" and "what they can do."
*   **Action Item**: Audit your project for usage of ORM `raw()` or `nativeQuery` functions and verify that parameterized queries are being used.