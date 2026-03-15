# API 與資料庫安全防護 / Security Essentials for APIs & Databases

## Mental model｜心智模型

在設計 API 與資料庫的安全架構時，請拋棄「外殼堅硬、內部柔軟」的城堡思維。現代架構需要的是 **縱深防禦 (Defense in Depth)** 與 **零信任 (Zero Trust)** 的思維模型。

想像你的請求是一個穿越層層關卡的旅客：

1.  **The Gate (API Gateway/WAF):** 這裡過濾掉明顯的惡意流量（DDoS、已知的惡意 IP）。
2.  **The Reception (Authentication - AuthN):** 確認「你是誰」。這不是資料庫的責任，通常由 Identity Provider (IdP) 或 Middleware 處理。
3.  **The Guard (Authorization - AuthZ):** 確認「你能做什麼」。這是最常被忽略的一環，**驗證了身分不代表有權限存取特定資源**。
4.  **The Vault (Database):** 資料庫本身不應信任應用程式傳來的 SQL 字串，且資料在靜態儲存（At Rest）與傳輸中（In Transit）都必須加密。

**核心原則：**
> **"Never Trust, Always Verify."**
> 所有的輸入（Input）都是有罪的，直到被證明無辜（Validated）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 身份驗證與授權 (AuthN & AuthZ)
*   **Token-Based Authentication:** 使用 **JWT (JSON Web Tokens)** 進行無狀態驗證，但務必設定短效期（Short-lived access tokens）並搭配 Refresh Token 機制。
*   **Resource-Based Authorization:** 不要只檢查 `ROLE=ADMIN`。必須實作 **Object Level Authorization**。
    *   *Pattern:* `can(user, 'read', resource)`。在存取 DB 前，先檢查該 User ID 是否為該 Resource 的 Owner。
*   **Standardize Headers:** 統一使用 `Authorization: Bearer <token>` header，避免將 token 放在 URL query parameter 中（會被記錄在 Server Logs 裡）。

### 2. 資料庫防護 (Database Protection)
*   **Prepared Statements (Parameterization):** 這是防禦 **SQL Injection** 的唯一黃金標準。永遠不要使用字串串接來組裝 SQL。
    *   *Good:* `SELECT * FROM users WHERE id = ?` (DB 引擎預編譯，資料被視為單純數值)
    *   *Bad:* `SELECT * FROM users WHERE id = ` + inputId
*   **Principle of Least Privilege (最小權限原則):**
    *   應用程式連接 DB 的帳號 **不應該** 是 `root` 或 `sa`。
    *   如果 API 只需要讀取，使用僅有 `SELECT` 權限的 DB User。
    *   針對 Migration (DDL) 與 Runtime (DML) 使用不同的 DB 帳號。

### 3. 資料加密與脫敏 (Encryption & Masking)
*   **Encryption at Rest:** 啟用資料庫層級的加密（如 AWS RDS Encrypted, PostgreSQL TDE）。
*   **Encryption in Transit:** 強制所有 DB 連線與 API 呼叫使用 **TLS 1.2+ (HTTPS)**。
*   **Sensitive Data Handling:**
    *   **Passwords:** 使用強雜湊演算法（Argon2id 或 bcrypt），絕對不可明碼儲存。
    *   **PII (個資):** 身份證、信用卡號應在應用層加密後再寫入 DB，或使用 Tokenization 服務。

### 4. 輸入驗證 (Input Validation)
*   **Schema Validation:** 在 Controller 層使用強型別 Schema 驗證庫（如 Zod, Joi, Pydantic）。
*   **Allow-list over Block-list:** 定義「什麼是被允許的」（如：Email 格式、UUID 格式），而不是嘗試過濾「什麼是壞的」。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Broken Object Level Authorization (BOLA / IDOR)
這是 **OWASP API Top 10 #1** 的漏洞。
*   **現象：** 攻擊者將 API URL 中的 ID 從 `123` 改為 `124`，就能看到別人的訂單。
*   **錯誤思維：** 「使用者已經登入了，所以他是安全的。」
*   **修正：** 必須在查詢資料庫時加上 `AND user_id = current_user.id` 的過濾條件。

### 2. Mass Assignment (大量賦值)
*   **現象：** 直接將前端傳來的 JSON 物件綁定到資料庫模型。
*   **風險：** 攻擊者在 Payload 中偷加 `{"role": "admin", "balance": 999999}`，若後端未過濾欄位，會直接寫入 DB。
*   **修正：** 使用 DTO (Data Transfer Object) 或明確定義可寫入的欄位白名單。

### 3. Verbose Error Messages (過於詳細的錯誤訊息)
*   **現象：** API 回傳 `500 Internal Server Error` 時，包含了完整的 Stack Trace 或 SQL 錯誤訊息。
*   **風險：** 洩漏了 DB 結構、使用的框架版本，給攻擊者提供了入侵地圖。
*   **修正：** Production 環境統一回傳通用錯誤訊息（如 "An unexpected error occurred"），詳細 Log 僅記錄在伺服器端。

### 4. Security Misconfiguration
*   **現象：** 將 API Keys、DB 密碼 Hardcode 在程式碼中並推送到 Git。
*   **修正：** 使用環境變數（`.env`）或 Secret Management Service (AWS Secrets Manager, HashiCorp Vault)。

---

## Checklists & workflows｜檢查清單與流程

### Development Phase Checklist
- [ ] **Injection 防護**：所有資料庫查詢皆使用 ORM 的參數化查詢或 Prepared Statements。
- [ ] **AuthZ 檢查**：每一個 API Endpoint 都驗證了 `current_user` 是否有權限存取該 `resource_id` (防禦 BOLA)。
- [ ] **Input Validation**：所有輸入參數（Body, Query, Params）都有嚴格的型別與格式驗證。
- [ ] **Mass Assignment 防護**：寫入資料庫前，明確過濾了不可由使用者修改的欄位（如 `is_admin`, `created_at`）。
- [ ] **Rate Limiting**：針對登入、註冊等敏感接口實作了速率限制（防止暴力破解）。

### Code Review / Pre-deployment Checklist
- [ ] **Secrets Scan**：確認沒有 API Key 或密碼被 commit 到版控系統（使用工具如 `trufflehog` 或 `git-secrets`）。
- [ ] **Dependency Scan**：檢查 `package.json` 或 `go.mod` 中的依賴套件是否有已知漏洞（使用 `npm audit`, `Snyk`, `Dependabot`）。
- [ ] **Error Handling**：確認全域錯誤處理器（Global Error Handler）在 Production 模式下隱藏了 Stack Trace。
- [ ] **Logging**：確認 Log 中沒有印出敏感資訊（如密碼、Token、PII）。

---

## Real-world examples｜實戰案例

### 案例 1：防禦 BOLA (Broken Object Level Authorization)

**❌ Vulnerable Code (Node.js/Express 範例):**
攻擊者只要更改 `req.params.id` 即可存取任意訂單。

```javascript
app.get('/api/orders/:id', authMiddleware, async (req, res) => {
  // 錯誤：只依賴 URL ID 查詢，未檢查該訂單是否屬於當前使用者
  const order = await db.query('SELECT * FROM orders WHERE id = $1', [req.params.id]);
  
  if (!order) return res.status(404).json({ error: 'Order not found' });
  res.json(order);
});
```

**✅ Secure Code:**
強制加入擁有權檢查。

```javascript
app.get('/api/orders/:id', authMiddleware, async (req, res) => {
  const userId = req.user.id; // 從 Auth Token 解析出的 User ID
  const orderId = req.params.id;

  // 正確：查詢條件同時包含 ID 與 UserID
  const order = await db.query(
    'SELECT * FROM orders WHERE id = $1 AND user_id = $2', 
    [orderId, userId]
  );
  
  if (!order) return res.status(404).json({ error: 'Order not found' }); // 即使存在但非本人，也回傳 404 避免洩漏存在性
  res.json(order);
});
```

### 案例 2：防止 SQL Injection 與 Mass Assignment

**❌ Vulnerable Code:**

```javascript
// 假設 body 為 { "username": "admin", "password": "' OR '1'='1" }
const query = `SELECT * FROM users WHERE username = '${req.body.username}' AND password = '${req.body.password}'`;
// 這會導致 SQL Injection
```

**✅ Secure Code (使用 ORM 與 DTO):**

```typescript
// 1. 定義 DTO (Data Transfer Object) 限制輸入欄位
class UpdateProfileDto {
  @IsString()
  @Length(2, 50)
  displayName: string;
  
  // 注意：這裡不包含 role 或 balance 等敏感欄位
}

// 2. Controller 實作
async updateProfile(user: User, body: UpdateProfileDto) {
  // ORM 自動處理 Parameterization，防止 SQL Injection
  // 只更新 DTO 中定義的欄位，防止 Mass Assignment
  return await userRepository.update({ id: user.id }, {
    displayName: body.displayName
  });
}
```

### 案例 3：敏感資料處理 (PII)

**情境：** 需要儲存使用者的身分證字號 (National ID)，以便後續客服查詢，但不能明碼儲存。

**解決方案：**
1.  **Application Layer Encryption:** 在寫入 DB 前，使用 AES-256-GCM 加密。
2.  **Key Management:** 加密金鑰（DEK）由 KMS (Key Management Service) 管理，不放在 code 裡。

```sql
-- 資料庫中看到的樣子 (無法直接閱讀)
| id | name  | national_id_encrypted          | national_id_hash (用於搜尋) |
|----|-------|--------------------------------|---------------------------|
| 1  | Alice | 0x1a2b3c... (AES Encrypted)    | sha256(ID + Salt)         |
```

*註：若需要「精確搜尋」加密欄位，通常會另外儲存一個 `Blind Index` (Hash 值)，搜尋時比對 Hash，讀取時解密 Encrypted 欄位。*