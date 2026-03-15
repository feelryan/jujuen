# Chapter 09: Compliance, Privacy & Governance (GRC)
# 第 09 章：合規標準、隱私與治理

## 1. Introduction & Learning Goals
## 1. 前言與學習目標

For Senior Engineers, "Compliance" is often viewed as a bureaucratic hurdle, but in reality, it is a critical non-functional requirement that dictates system architecture. Failing to design for compliance (GDPR, PCI-DSS, SOC2) from day one can lead to massive re-engineering costs or legal penalties. This chapter shifts the perspective from "checking boxes" to "architecting for trust and sovereignty."
對於資深工程師而言，「合規（Compliance）」常被視為官僚障礙，但實際上，它是決定系統架構的關鍵非功能性需求。若未能在初期就將合規性（如 GDPR、PCI-DSS、SOC2）納入設計，往往會導致巨大的重構成本或法律懲罰。本章將視角從「勾選檢查表」轉變為「為信任與主權設計架構」。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Map Regulations to Architecture**: Translate legal requirements (GDPR, CCPA, PCI-DSS) into concrete technical decisions like data sharding, encryption strategies, and network isolation.
    **將法規映射至架構**：將法律要求（GDPR、CCPA、PCI-DSS）轉化為具體的技術決策，如資料分片（Sharding）、加密策略與網路隔離。
2.  **Design for Data Sovereignty**: Architect systems that respect Data Residency laws, ensuring user data remains in specific geographic regions (e.g., EU data stays in the EU).
    **設計資料主權架構**：設計符合資料在地化（Data Residency）法規的系統，確保使用者資料保留在特定地理區域（例如：歐盟資料僅留在歐盟）。
3.  **Implement "Right to be Forgotten"**: Design robust mechanisms for PII (Personally Identifiable Information) deletion, including techniques like Crypto-shredding.
    **實作「被遺忘權」**：設計穩健的 PII（個人識別資訊）刪除機制，包含加密銷毀（Crypto-shredding）等技術。
4.  **Understand Auditability (SOC2)**: Build systems that generate evidence for audits automatically, focusing on immutability and access controls.
    **理解可稽核性（SOC2）**：建構能自動產生稽核證據的系統，專注於不可變性（Immutability）與存取控制。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Building Code" Analogy
### 2.1 「建築法規」類比

Think of building a software system like constructing a skyscraper. You can't just focus on aesthetics and speed; you must adhere to zoning laws (Data Residency), fire safety codes (Security Controls), and accessibility standards (Privacy Rights).
將建構軟體系統想像成建造摩天大樓。你不能只關注美觀與速度；你必須遵守分區法規（資料在地化）、消防安全法規（安全控制）以及無障礙標準（隱私權）。

*   **GDPR/CCPA**: These are the "Tenant Rights." They dictate who can enter, what you can record about them, and their right to leave without a trace.
    **GDPR/CCPA**：這些是「租戶權利」。它們規定誰可以進入、你可以記錄關於他們的什麼資訊，以及他們不留痕跡離開的權利。
*   **PCI-DSS**: This is the "Bank Vault Standard." If you store money (or credit card numbers), the walls must be this thick, and cameras must be everywhere.
    **PCI-DSS**：這是「銀行金庫標準」。如果你儲存金錢（或信用卡號），牆壁必須有特定厚度，且監視器必須無所不在。
*   **SOC2**: This is the "Building Inspection Record." It proves that you actually check the fire alarms every month, rather than just saying you do.
    **SOC2**：這是「建築檢查記錄」。它證明你實際上每個月都在檢查火警警報器，而不僅僅是口頭說說。

### 2.2 Key Terminology & Definitions
### 2.2 關鍵術語與定義

*   **PII (Personally Identifiable Information)**: Any data that can identify a specific individual (e.g., email, phone, IP address, device ID). In System Design, PII is "toxic waste"—handle it with extreme care and minimize its spread.
    **PII（個人識別資訊）**：任何能識別特定個人的資料（如 Email、電話、IP 地址、裝置 ID）。在系統設計中，PII 是「有毒廢棄物」——必須極度小心處理並盡量減少其擴散。
*   **Data Residency / Sovereignty**: The legal requirement that data must be stored and processed within a specific jurisdiction. This kills the "one global database" pattern.
    **資料在地化 / 主權**：資料必須在特定司法管轄區內儲存與處理的法律要求。這扼殺了「單一全球資料庫」的模式。
*   **Scope Reduction**: The most effective compliance strategy. If a system doesn't touch PII or Credit Card data, it doesn't need to be compliant. We use tokenization and isolation to reduce scope.
    **範圍縮減（Scope Reduction）**：最有效的合規策略。如果系統不接觸 PII 或信用卡資料，就不需要合規。我們使用代幣化（Tokenization）與隔離來縮減範圍。
*   **Crypto-shredding**: A method to "delete" data by deleting the encryption key required to read it. This is essential for backups where physical deletion is impossible.
    **加密銷毀（Crypto-shredding）**：透過刪除讀取資料所需的加密金鑰來「刪除」資料的方法。這對於無法進行物理刪除的備份檔至關重要。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Architecture for Data Residency
### 3.1 資料在地化架構

In a global system, you cannot simply replicate all data everywhere. You must partition data by region.
在全球化系統中，你不能簡單地將所有資料複製到所有地方。你必須按區域對資料進行分區。

*   **Control Plane vs. Data Plane**: Keep the Control Plane (configuration, metadata) global but lean. Keep the Data Plane (customer content, PII) strictly regional.
    **控制平面 vs. 資料平面**：保持控制平面（設定、元資料）全球化但輕量。保持資料平面（客戶內容、PII）嚴格區域化。
*   **Routing**: The ingress layer must route users to their home region based on DNS, GeoIP, or user account metadata *before* accessing sensitive data.
    **路由**：入口層必須在存取敏感資料*之前*，根據 DNS、GeoIP 或使用者帳戶元資料，將使用者路由至其歸屬區域。

### 3.2 The PCI-DSS Architecture (Tokenization)
### 3.2 PCI-DSS 架構（代幣化）

Never store raw credit card numbers (PAN) unless you are a payment processor.
除非你是支付處理商，否則絕不要儲存原始信用卡號（PAN）。

1.  **Frontend**: Uses an iframe or SDK from the Payment Service Provider (Stripe, PayPal). The PAN goes directly from the browser to the PSP.
    **前端**：使用支付服務提供商（Stripe, PayPal）的 iframe 或 SDK。PAN 直接從瀏覽器傳輸到 PSP。
2.  **Backend**: Receives a `token` (e.g., `tok_12345`) representing the card. This token is stored in your DB.
    **後端**：接收代表該卡片的 `token`（例如 `tok_12345`）。此 token 儲存在你的資料庫中。
3.  **Result**: Your backend is "out of scope" for the most rigorous PCI requirements because it never sees the raw data.
    **結果**：你的後端因從未接觸原始資料，從而處於最嚴格 PCI 要求的「範圍之外」。

---

## 4. Walkthrough / Example: Designing a GDPR-Compliant User System
## 4. 逐步示例：設計符合 GDPR 的使用者系統

### Scenario
### 情境

You are designing the user profile system for a global social platform. You must support:
你正在為一個全球社交平台設計使用者個人檔案系統。你必須支援：
1.  **Data Residency**: EU users' PII stays in the EU (Frankfurt); US users in US (N. Virginia).
    **資料在地化**：歐盟使用者的 PII 留在歐盟（法蘭克福）；美國使用者在美國（北維吉尼亞）。
2.  **Right to be Forgotten (RTBF)**: Users can request account deletion. All data must be unrecoverable within 30 days, including backups.
    **被遺忘權（RTBF）**：使用者可要求刪除帳號。所有資料（包含備份）必須在 30 天內無法復原。

### Step 1: Naive Approach (The Anti-pattern)
### 步驟 1：天真做法（反模式）

*   **Architecture**: Single Global DB (e.g., Spanner or Aurora Global) replicating everywhere for low latency.
    **架構**：單一全球資料庫（如 Spanner 或 Aurora Global）複製到各地以降低延遲。
*   **Deletion**: `DELETE FROM users WHERE id = ?`.
    **刪除**：執行 `DELETE FROM users WHERE id = ?`。
*   **Problem**:
    *   **Violation**: EU data is replicated to the US.
    *   **Violation**: Database backups (snapshots) still contain the deleted user's data for months/years. Restoring a backup would resurrect the deleted user (a "Zombie User").
    *   **問題**：
        *   **違規**：歐盟資料被複製到了美國。
        *   **違規**：資料庫備份（快照）仍包含已刪除使用者的資料長達數月/數年。還原備份會讓已刪除的使用者復活（「殭屍使用者」）。

### Step 2: Mature Approach (Sharding + Crypto-shredding)
### 步驟 2：成熟做法（分片 + 加密銷毀）

#### 1. Data Residency via Regional Isolation
#### 1. 透過區域隔離實現資料在地化

We use a "Cell-based Architecture". Each region is a self-contained cell. A global "Directory Service" (storing only non-PII like UserID + Region mapping) directs traffic.
我們使用「基於單元的架構（Cell-based Architecture）」。每個區域是一個獨立的單元。一個全球「目錄服務」（僅儲存非 PII，如 UserID + Region 對應關係）負責導流。

```typescript
// Global Directory Service (Non-PII)
interface UserRouting {
  userId: string; // UUID
  region: 'EU' | 'US' | 'APAC';
  shardId: string;
}

// Regional User Service (Contains PII)
interface UserProfile {
  userId: string;
  email: string; // PII
  address: string; // PII
  preferences: object;
}
```

#### 2. Implementing Crypto-shredding for RTBF
#### 2. 實作加密銷毀以滿足 RTBF

Instead of relying on physical deletion (which is hard in immutable backups/logs), we encrypt each user's PII with a unique key (DEK - Data Encryption Key).
我們不依賴物理刪除（這在不可變的備份/日誌中很難做到），而是用唯一的金鑰（DEK - 資料加密金鑰）加密每個使用者的 PII。

*   **Key Hierarchy**:
    *   **KEK (Key Encryption Key)**: Stored in KMS (e.g., AWS KMS), rotates regularly.
    *   **DEK (Data Encryption Key)**: Unique per user, stored in a separate "Key DB", encrypted by KEK.
    *   **Data**: Encrypted by DEK.
    *   **金鑰層級**：
        *   **KEK（金鑰加密金鑰）**：儲存在 KMS（如 AWS KMS），定期輪替。
        *   **DEK（資料加密金鑰）**：每個使用者唯一，儲存在獨立的「金鑰資料庫」，由 KEK 加密。
        *   **資料**：由 DEK 加密。

*   **Deletion Process**:
    1.  User requests deletion.
    2.  System deletes the user's **DEK** from the Key DB.
    3.  The PII data (in the main DB, in logs, in backups, in data lakes) becomes "ciphertext garbage." It is mathematically impossible to recover without the key.
    *   **刪除流程**：
        1.  使用者請求刪除。
        2.  系統從金鑰資料庫刪除該使用者的 **DEK**。
        3.  PII 資料（無論在主資料庫、日誌、備份或資料湖中）變成了「密文垃圾」。沒有金鑰，數學上無法復原。

```typescript
class PiiService {
  async saveUser(userId: string, data: any) {
    // 1. Generate or retrieve DEK for this user
    const dek = await this.keyManagementService.getOrCreateDEK(userId);
    
    // 2. Encrypt sensitive fields
    const encryptedData = this.crypto.encrypt(data, dek);
    
    // 3. Store encrypted data
    await this.db.save(userId, encryptedData);
  }

  async deleteUser(userId: string) {
    // Soft delete data record (for operational consistency)
    await this.db.softDelete(userId);
    
    // HARD delete the key (Crypto-shredding)
    // This makes all historical backups of this user unreadable immediately.
    await this.keyManagementService.destroyDEK(userId);
  }
}
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Logging PII (The Silent Killer)
### 5.1 記錄 PII（隱形殺手）

*   **The Mistake**: Developers log full request objects for debugging: `logger.info("Request payload:", request.body)`.
    **錯誤**：開發者為了除錯記錄完整的請求物件：`logger.info("Request payload:", request.body)`。
*   **Why it's bad**: Logs are often stored in less secure storage (e.g., Elasticsearch, S3) with broader access. PII in logs violates GDPR/PCI.
    **為何不好**：日誌通常儲存在安全性較低的儲存空間（如 Elasticsearch, S3），且存取權限較廣。日誌中的 PII 違反 GDPR/PCI。
*   **Solution**: Implement PII stripping/masking middleware *before* logging. Use structured logging and explicitly allow-list fields.
    **解法**：在記錄*之前*實作 PII 剝離/遮罩的中介軟體。使用結構化日誌並明確設定允許欄位白名單。

### 5.2 "Encryption at Rest" False Security
### 5.2 「靜態加密」的虛假安全感

*   **The Mistake**: Enabling "Encryption at Rest" on the database (e.g., AWS RDS TDE) and claiming compliance.
    **錯誤**：啟用資料庫的「靜態加密」（如 AWS RDS TDE）並宣稱合規。
*   **Why it's bad**: This protects against someone stealing the physical hard drive. It does *not* protect against a compromised application or a malicious admin with DB access, as the DB engine transparently decrypts data.
    **為何不好**：這只能防止有人偷走實體硬碟。它*無法*防禦被入侵的應用程式或擁有資料庫權限的惡意管理員，因為資料庫引擎會透明地解密資料。
*   **Solution**: Application-Level Encryption (ALE) for highly sensitive fields (like SSN, Credit Card). Only the app has the keys.
    **解法**：針對高度敏感欄位（如身分證號、信用卡）採用應用層加密（ALE）。只有應用程式擁有金鑰。

### 5.3 Ignoring "Zombie Data" in Analytics
### 5.3 忽略分析中的「殭屍資料」

*   **The Mistake**: Deleting users from the production DB but forgetting the Data Warehouse (Snowflake/BigQuery) or Data Lake.
    **錯誤**：從生產資料庫刪除使用者，但忘記了資料倉儲（Snowflake/BigQuery）或資料湖。
*   **Why it's bad**: GDPR applies to *all* copies.
    **為何不好**：GDPR 適用於*所有*副本。
*   **Solution**: Propagate deletion events (via Kafka/CDC) to downstream analytical systems. Or rely on Crypto-shredding (if the warehouse also stores encrypted data, which is harder for analytics).
    **解法**：將刪除事件（透過 Kafka/CDC）傳播到下游分析系統。或者依賴加密銷毀（如果倉儲也儲存加密資料，但這會增加分析難度）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a system to handle "Right to be Forgotten" in a microservices architecture with 50+ services?
### Q1: 在擁有 50+ 個服務的微服務架構中，你會如何設計處理「被遺忘權」的系統？

*   **Key Points**:
    *   **Orchestration**: Need a central "Privacy Service" to publish "DeleteUser" events.
    *   **Async Processing**: Use a message queue (Kafka/SQS). Services subscribe to the topic and clean their own DBs.
    *   **Idempotency**: Deletion requests might be retried; handling must be idempotent.
    *   **Verification**: How do we know it's done? Services should ack/callback.
    *   **Crypto-shredding**: Mention this as the ultimate fallback for backups.
    *   **重點**：
        *   **編排**：需要一個中央「隱私服務」來發布「刪除使用者」事件。
        *   **非同步處理**：使用訊息佇列（Kafka/SQS）。各服務訂閱該主題並清理自己的資料庫。
        *   **冪等性**：刪除請求可能會重試；處理必須是冪等的。
        *   **驗證**：我們如何知道已完成？服務應該回傳確認（ack/callback）。
        *   **加密銷毀**：提及這是備份處理的終極手段。

### Q2: We need to store user SSNs (Social Security Numbers). How do we secure them?
### Q2: 我們需要儲存使用者的 SSN（社會安全碼）。我們該如何保護它們？

*   **Key Points**:
    *   **Encryption**: Application-Level Encryption (ALE) is mandatory. DB admins should see ciphertext.
    *   **Key Management**: Use a KMS. Rotate keys.
    *   **Access Control**: Separate the "SSN Vault" service. Only specific authorized services can call it. Audit every access.
    *   **Masking**: UI should never show full SSN by default (show last 4 digits).
    *   **重點**：
        *   **加密**：必須採用應用層加密（ALE）。資料庫管理員應該只看到密文。
        *   **金鑰管理**：使用 KMS。輪替金鑰。
        *   **存取控制**：分離出「SSN 金庫」服務。只有特定授權服務能呼叫它。稽核每一次存取。
        *   **遮罩**：UI 預設絕不顯示完整 SSN（只顯示後 4 碼）。

### Q3: Explain the difference between SOC2 Type 1 and Type 2 to a Product Manager.
### Q3: 向產品經理（PM）解釋 SOC2 Type 1 與 Type 2 的差異。

*   **Key Points**:
    *   **Type 1**: A snapshot in time. "Do we have a design for the lock on the door?" (Design suitability).
    *   **Type 2**: A period of time (usually 6-12 months). "Did we actually keep the door locked every single day for the past year?" (Operating effectiveness).
    *   **Impact**: Type 2 requires continuous monitoring and evidence collection (automation is key).
    *   **重點**：
        *   **Type 1**：時間點的快照。「我們是否有門鎖的設計？」（設計適用性）。
        *   **Type 2**：一段時間（通常 6-12 個月）。「過去一年我們是否真的每天都鎖門？」（執行有效性）。
        *   **影響**：Type 2 需要持續監控與證據收集（自動化是關鍵）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Compliance is Architecture**: It dictates where data lives (Residency) and how it is accessed (Isolation).
    **合規即架構**：它決定了資料儲存在哪裡（在地化）以及如何被存取（隔離）。
2.  **Scope Reduction**: The best way to secure data is not to have it. Use Tokenization for PCI and specialized Vault services for PII.
    **範圍縮減**：保護資料最好的方法就是不要擁有它。對 PCI 使用代幣化，對 PII 使用專門的金庫服務。
3.  **Crypto-shredding**: The only viable way to ensure "Right to be Forgotten" across immutable backups and logs.
    **加密銷毀**：在不可變備份與日誌中確保「被遺忘權」的唯一可行方法。
4.  **Least Privilege & Auditing**: SOC2 is about proving that access is restricted and monitored. Logs must be immutable.
    **最小權限與稽核**：SOC2 關於證明存取受到限制與監控。日誌必須是不可變的。
5.  **Application-Level Encryption**: Essential for highly sensitive data; database-level encryption is insufficient against internal threats.
    **應用層加密**：對高度敏感資料至關重要；資料庫層級加密不足以防禦內部威脅。

### Next Steps
### 後續延伸

*   **Deep Dive**: Study **Envelope Encryption** (using KEK to encrypt DEK) in AWS KMS or Google Cloud KMS.
    **深入研究**：研讀 AWS KMS 或 Google Cloud KMS 中的**信封加密（Envelope Encryption）**（使用 KEK 加密 DEK）。
*   **Practice**: Implement a simple "PII Vault" service that encrypts data before writing to a database using a local key, then try to rotate that key.
    **實作**：實作一個簡單的「PII 金庫」服務，在寫入資料庫前使用本地金鑰加密資料，然後嘗試輪替該金鑰。
*   **Next Chapter**: **Identity & Access Management (IAM)** - Moving from protecting data to authenticating users and services (OAuth2, OIDC, RBAC/ABAC).
    **下一章**：**身分與存取管理（IAM）** —— 從保護資料轉向驗證使用者與服務（OAuth2, OIDC, RBAC/ABAC）。