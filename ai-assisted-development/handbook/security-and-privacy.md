# 安全性、隱私保護與合規檢核 / Security, Privacy, and Compliance Checks

在 AI 輔助開發的過程中，安全性不再只是最後的測試階段，而是必須貫穿在「提示詞輸入前」到「代碼合併後」的每一個環節。AI 工具極大化了生產力，但也同時極大化了敏感資料外洩與引入安全漏洞的風險。

## Mental model｜心智模型

### 1. The "Public Forum" Principle（公開論壇原則）
將你與 AI (ChatGPT, Claude, Copilot) 的對話視窗，想像成是一個 **公開的 Stack Overflow 貼文**。
- **Rule of Thumb**: 如果你不敢把這段程式碼或 Log 貼在 Stack Overflow 上，就不要貼給 AI。
- **Implication**: 任何 API Key、密碼、客戶真實個資 (PII) 或公司核心演算法機密，都必須在「輸入前」被過濾或替換。

### 2. The "Untrusted Intern" Mindset（不受信任的實習生心態）
將 AI 視為一位 **極具熱情但缺乏安全意識的資淺實習生**。
- **Behavior**: 它會為了讓程式碼「能跑」，而傾向使用最簡單的解法（例如關閉 SSL 驗證、使用硬編碼憑證、忽略 Input Validation）。
- **Responsibility**: 你是資深導師，你的責任不是「複製貼上」，而是「審查 (Audit)」與「修正 (Harden)」它產出的代碼。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Input Sanitization & Context Control（輸入脫敏與上下文控制）
在將資料餵給 AI 之前，必須進行「消毒」。

- **使用佔位符 (Placeholders)**：將敏感資訊替換為通用標籤。
  - *Bad*: `Authorization: Bearer eyJhbGciOi...`
  - *Good*: `Authorization: Bearer <JWT_TOKEN_PLACEHOLDER>`
- **配置 `.copilotignore` 或類似設定**：
  - 如果使用 IDE 內建的 AI 助手，確保專案根目錄有設定忽略檔案，排除 `.env`、憑證檔、以及含有敏感商業邏輯的目錄，防止 AI 自動讀取這些上下文。

### 2. Security-First Prompting（安全優先的提示工程）
在 Prompt 中顯式要求安全性，能顯著降低漏洞代碼的機率。

- **Pattern**: "Generate code for [task] following **OWASP Top 10 security guidelines**. Ensure inputs are validated and secrets are loaded from environment variables."
- **Pattern**: "Write a unit test that specifically targets **edge cases and security vulnerabilities** (e.g., SQL injection, XSS) for this function."

### 3. Supply Chain Verification（供應鏈驗證）
AI 經常會「幻覺 (Hallucinate)」出不存在的套件名稱，或是推薦過時、有漏洞的函式庫。

- **Verify Existence**: 在執行 `npm install` or `pip install` 之前，務必去官方 Registry 確認該套件存在且由可信維護者管理（防止 Typosquatting 攻擊）。
- **Version Check**: 檢查 AI 建議的版本是否為最新的穩定版（LTS）。

### 4. Automated Compliance Scanning（自動化合規掃描）
不要依賴肉眼檢查 AI 是否抄襲了 GPL 代碼或引入了漏洞。

- **SAST/Secret Scanning**: 在 CI/CD 流程中強制執行靜態應用程式安全測試 (SAST) 和機密掃描 (Secret Scanning)。
- **License Compliance**: 使用工具（如 FOSSA, Black Duck）確保 AI 生成的代碼片段沒有違反專案的授權規範（雖然現代 AI 廠商聲稱有過濾，但法律風險仍在）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ The "Paste-All" Trap（全選複製陷阱）
- **描述**：為了解決 Bug，直接將包含 DB 連線字串、AWS Keys 或客戶真實 Email 的 Log 檔整段貼給 AI。
- **後果**：你的敏感資料可能被 AI 模型訓練（若未關閉訓練選項），或儲存在第三方伺服器的歷史紀錄中。

### ❌ Blindly Trusting "Happy Path" Code（盲信快樂路徑代碼）
- **描述**：AI 生成的代碼通常預設「使用者輸入是完美的」。例如，生成的 SQL 查詢直接拼接字串，或生成的檔案上傳功能未檢查副檔名。
- **後果**：引入 SQL Injection、RCE (Remote Code Execution) 等嚴重漏洞。

### ❌ The "Hallucinated Package" Attack Vector（幻覺套件攻擊向量）
- **描述**：AI 建議使用 `import fast-xml-parser-secure`（虛構名稱），開發者未經查證直接安裝，結果剛好有駭客註冊了這個名字的惡意套件。
- **後果**：供應鏈攻擊，專案被植入後門。

### ❌ Ignoring IP Policy（忽略智財權策略）
- **描述**：在公司明確禁止將核心 IP 上傳至公有 AI 服務的情況下，仍使用 ChatGPT 處理公司獨有的演算法。
- **後果**：違反公司合規政策，甚至導致商業機密喪失法律保護。

---

## Checklists & workflows｜檢查清單與流程

### 🛡️ Pre-Prompt Checklist (Before you ask AI)
在按下 Enter 發送 Prompt 之前：

- [ ] **Secrets Check**: 檢查 Prompt 中是否包含 API Keys、密碼、Token 或連線字串？（應替換為 `<SECRET>`）。
- [ ] **PII Check**: 檢查是否包含真實姓名、電話、Email 或身分證號？（應替換為假資料 `John Doe`）。
- [ ] **Context Check**: 如果使用 IDE 插件，確認當前開啟的檔案不包含機密商業邏輯（或已加入 `.copilotignore`）。
- [ ] **Policy Check**: 確認使用的 AI 工具符合公司的資料隱私政策（例如：是否已開啟 Enterprise Mode / Data Privacy Mode）。

### 🔍 Post-Generation Checklist (Before you commit)
在接受並 Commit AI 生成的代碼之前：

- [ ] **Vulnerability Scan**: 該代碼是否通過了 IDE 的 Linter 和 SAST 掃描？
- [ ] **Input Validation**: 該函式是否驗證了所有輸入參數？（AI 常忽略這點）。
- [ ] **Dependency Audit**: 引入的新套件是否真實存在？版本是否安全？授權是否相容（如非 GPL）？
- [ ] **Secret Management**: 代碼是否從環境變數 (Environment Variables) 讀取設定，而不是硬編碼？
- [ ] **Understanding**: **我是否完全理解這段代碼的每一行在做什麼？**（永遠不要 Commit 你看不懂的代碼）。

---

## Real-world examples｜實戰案例

### Scenario 1: Preventing Secret Leakage (防止機密外洩)

**❌ Dangerous Prompt:**
> "I can't connect to my database. Here is my config code, help me fix it:
> `const db = new Client({ user: 'admin', pass: 'SuperSecret123', host: '192.168.1.5' });`"

**✅ Secure Prompt:**
> "I can't connect to my database. My client configuration uses environment variables like below. Help me debug the connection logic:
> `const db = new Client({ user: process.env.DB_USER, pass: process.env.DB_PASS, host: process.env.DB_HOST });`"

---

### Scenario 2: Fixing Insecure AI Code (修正不安全的 AI 代碼)

**🤖 AI Generated Code (Vulnerable to SQLi):**
```javascript
// User asks for a function to get user by ID
function getUser(userId) {
  // ⚠️ DANGER: String concatenation allows SQL Injection
  const query = "SELECT * FROM users WHERE id = " + userId;
  return db.execute(query);
}
```

**👨‍💻 Developer Refactoring (Security Hardening):**
*開發者介入，將其轉換為 Parameterized Query*

```javascript
function getUser(userId) {
  // ✅ FIX: Use parameterized queries
  const query = "SELECT * FROM users WHERE id = ?";
  return db.execute(query, [userId]);
}
```

---

### Scenario 3: Privacy-Preserving Debugging (保護隱私的除錯)

**Context**: 你有一個包含客戶個資的 JSON Log 報錯。

**Workflow**:
1.  **Original Log**: `{"error": "Invalid format", "user": "alice@example.com", "credit_card": "4111-2222-3333-4444"}`
2.  **Sanitization Action**: 使用簡單的 regex 或手動替換。
3.  **Sanitized Input for AI**:
    > "Analyze this error log structure. The sensitive data has been masked:
    > `{"error": "Invalid format", "user": "<EMAIL_MASKED>", "credit_card": "<CC_MASKED>"}`.
    > What could cause the 'Invalid format' error regarding the JSON schema?"