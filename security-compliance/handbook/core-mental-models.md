# 資安核心思維與心智模型 / Core Security Mental Models & Principles

在深入程式碼與工具之前，資安最重要的是「思維方式」。資安不是一個可以「完成」的功能，而是一種持續的風險管理過程。本章節將協助你建立正確的資安直覺，讓你在架構設計與寫作程式碼時，能自然地做出安全的決策。

Security is not a feature you "finish"; it is a continuous process of risk management. This chapter helps you build the right security intuition.

---

## Mental model｜心智模型

### 1. 攻擊者的經濟學 (The Economics of Attacks)
不要試圖打造「絕對無法被駭」的系統（那是不存在的），你的目標是**提高攻擊成本，使其高於攻擊獲利**。
- **Cost > Value**: 如果攻擊你的網站需要花費 100 萬美元的資源，但只能竊取價值 1 萬美元的資料，理性的攻擊者就會放棄。
- **Low Hanging Fruit**: 攻擊者通常會尋找最容易下手的目標。不要成為網路上最容易被攻破的那個。

### 2. 瑞士起司模型 (The Swiss Cheese Model / Defense in Depth)
沒有任何單一防禦層是完美的（就像起司上有洞）。**縱深防禦 (Defense in Depth)** 的概念是將多層防禦疊加，使得一層的漏洞被另一層擋下。
- **Layering**: WAF -> Load Balancer -> Auth Service -> App Logic -> Database ACL -> OS Security.
- 只要光線（攻擊）穿不過所有起司的洞，系統就是安全的。

### 3. 零信任架構 (Zero Trust: "Never Trust, Always Verify")
傳統的「城堡與護城河」（Castle-and-Moat）模型認為內網是安全的，這在現代雲端架構中是錯誤的。
- **Identity is the new perimeter**: 邊界不再是防火牆，而是「身份」。
- **Assume Breach**: 假設內網已經有駭客潛伏。服務對服務（Service-to-Service）的呼叫也必須驗證身份與權限。

### 4. CIA 三角的權衡 (The CIA Triad Trade-offs)
資安決策往往是在以下三者間做取捨，你需要根據業務需求決定優先級：
- **Confidentiality (機密性)**: 只有授權者能讀取 (e.g., Encryption, ACLs)。
- **Integrity (完整性)**: 資料未被篡改 (e.g., Digital Signatures, Checksums)。
- **Availability (可用性)**: 授權者隨時能使用 (e.g., DDoS protection, Redundancy)。
> *實戰註記：過度追求機密性（例如極其複雜的 MFA 流程）往往會傷害可用性（UX）。資安工程師的工作是找到那個平衡點。*

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 最小權限原則 (Principle of Least Privilege - PoLP)
給予實體（使用者、程式、服務）執行任務所需的**最小**權限，並且只在**最短**的時間內有效。
- **Default Deny**: 預設狀態應為「拒絕所有存取」，而非「允許所有」。
- **Granular Scopes**: API Token 不應擁有 `admin` 權限，而應僅有 `read:profile` 或 `write:orders`。

### 2. 安全左移 (Shift Left Security)
將資安檢測從開發週期的末端（上線前滲透測試）移至開端（設計與編碼階段）。
- **Design Review**: 在畫架構圖時就進行威脅建模 (Threat Modeling)。
- **SAST/SCA**: 在 CI/CD Pipeline 中自動掃描程式碼漏洞與依賴套件風險。

### 3. 失敗時保持安全 (Fail Securely / Fail Closed)
當系統發生錯誤或崩潰時，狀態應該是「拒絕存取」而非「開放存取」。
- **Example**: 如果身份驗證服務掛了，API Gateway 應該回傳 `500` 或 `403`，絕對不能讓 Request 直接通過 (Fail Open)。
- **Exception Handling**: 錯誤訊息不應洩露堆疊追蹤 (Stack Trace) 或資料庫結構給終端用戶。

### 4. 職責分離 (Separation of Duties - SoD)
關鍵操作不應由單一角色或帳號獨自完成。
- **Dev vs. Ops**: 開發人員不應擁有生產環境資料庫的直接寫入權限。
- **Multi-party Authorization**: 敏感操作（如刪除備份）需要兩人以上的批准。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 隱匿式安全 (Security through Obscurity)
**誤區**：認為把 Admin URL 改成 `/super-secret-admin-v2` 或者使用自創的混淆演算法就能安全。
- **現實**：攻擊者使用自動化掃描器，幾秒鐘就能找到隱藏路徑。
- **修正**：系統的安全性應依賴於數學證明（密碼學）與堅固的架構，即使原始碼公開也應該是安全的（Kerckhoffs's principle）。

### 2. 信任客戶端輸入 (Trusting Client Input)
**誤區**：認為前端已經做了 Form Validation，後端就不需要檢查。
- **現實**：攻擊者可以繞過瀏覽器，直接用 `curl` 或 Postman 發送惡意 Payload（SQL Injection, XSS）。
- **修正**：**Never Trust the Client**. 後端必須對所有輸入進行驗證 (Validation) 與消毒 (Sanitization)。

### 3. 自行發明密碼學 (Rolling Your Own Crypto)
**誤區**：覺得現有的 AES/RSA 太慢或太複雜，自己寫一個 XOR 加密演算法。
- **現實**：自製加密演算法通常充滿漏洞，極易被破解。
- **修正**：使用經過時間驗證的標準庫 (e.g., `libsodium`, `bcrypt`, `Argon2`)。

### 4. 忽略供應鏈風險 (Ignoring Supply Chain Risks)
**誤區**：只關注自己的程式碼，卻隨意引入幾百個 npm/pip 套件。
- **現實**：現代攻擊常發生在第三方套件中 (e.g., Log4j, event-stream)。
- **修正**：定期更新依賴、使用 SCA 工具、鎖定版本 (Lockfiles)。

---

## Checklists & workflows｜檢查清單與流程

在進行系統設計或 Code Review 時，請使用此清單自我檢視：

### Design Phase Decision Tree
- [ ] **資料分級 (Data Classification)**: 系統處理的資料敏感度為何？(Public / Internal / Confidential / Restricted)
- [ ] **攻擊面分析 (Attack Surface)**: 哪些接口是對外暴露的？能否減少暴露點（例如透過 VPN 或 Private Subnet）？
- [ ] **身份邊界 (Identity Boundary)**: 誰可以存取？我們如何驗證他們？(AuthN & AuthZ)

### Implementation Checklist (The "Mental Linter")
- [ ] **Input Validation**: 所有來自外部的資料（URL params, Body, Headers, DB results）是否都視為不可信？
- [ ] **Output Encoding**: 輸出到瀏覽器前是否已轉義 (Escaped) 以防止 XSS？
- [ ] **Authorization Check**: 每一行存取資料的程式碼，是否都檢查了 `current_user` 是否有權限存取 `target_resource`？(防止 IDOR)
- [ ] **Secrets Management**: 程式碼中是否包含 Hardcoded 的 API Key 或密碼？(應使用環境變數或 Secrets Manager)
- [ ] **Logging**: 是否記錄了足夠的資安事件（登入失敗、權限拒絕），且**沒有**記錄敏感資料（如密碼明文、PII）？

---

## Real-world examples｜實戰案例

### Case 1: The "Internal" Admin Dashboard
**情境**：開發團隊建立了一個後台管理系統，認為「只有辦公室 IP 能連線」，所以登入機制寫得很簡單。
- **Anti-pattern**: 依賴網路邊界 (Firewall/IP Whitelist) 作為唯一防禦。
- **Risk**: 一旦攻擊者透過釣魚郵件入侵員工電腦（進入內網），或偽造 IP，後台即門戶大開。
- **Better Approach (Zero Trust)**:
  1. 即使在內網，仍強制要求 SSO 登入 + MFA (Multi-Factor Authentication)。
  2. 實作 RBAC (Role-Based Access Control)，客服人員不能執行「刪除使用者」的操作。
  3. 所有敏感操作皆寫入 Audit Log。

### Case 2: File Upload Feature
**情境**：使用者可以上傳大頭貼。
- **Naive Implementation**: 檢查檔名是否以 `.jpg` 結尾，然後直接存入 Web Server 的 `/uploads` 資料夾。
- **Attack Vector**: 攻擊者上傳名為 `hack.php.jpg` 或偽造 Header 的 Webshell script。如果 Web Server 配置不當，可能會執行該腳本。
- **Defense in Depth Implementation**:
  1. **Validation**: 不只檢查副檔名，檢查檔案的 Magic Bytes (File Signature) 確認真的是圖片。
  2. **Sanitization**: 重命名檔案 (e.g., UUID.jpg)，去除原始檔名中的特殊字元。
  3. **Isolation**: 不要存放在 Web Server 本地，上傳到 S3 Bucket，並設定 Bucket Policy 禁止執行腳本。
  4. **Processing**: 使用圖片處理庫重新壓縮圖片 (Re-encoding)，這通常能破壞隱藏在圖片中的惡意 Payload。