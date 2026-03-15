# 威脅建模與風險評估
# Threat Modeling & Risk Assessment

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，安全性不應僅是資安團隊的責任，而是系統設計階段就必須考量的核心要素。威脅建模（Threat Modeling）是將「安全性左移（Shift Left）」的具體實踐。完成本章後，你將能夠：

For senior engineers, security is not solely the responsibility of the InfoSec team; it is a core element that must be considered during the system design phase. Threat Modeling is the practical implementation of "Shifting Left." Upon completing this chapter, you will be able to:

1.  **系統化識別威脅**：運用 **STRIDE** 模型，在架構設計階段就能找出潛在的攻擊向量，而非等到程式碼寫完才修補。
    **Systematically Identify Threats**: Apply the **STRIDE** model to pinpoint potential attack vectors during the architectural design phase, rather than patching vulnerabilities after the code is written.
2.  **量化風險優先級**：使用 **DREAD** 或類似評分機制，評估漏洞的嚴重性，以便在工程資源有限的情況下做出正確的取捨（Trade-off）。
    **Quantify Risk Priority**: Use **DREAD** or similar scoring mechanisms to assess the severity of vulnerabilities, enabling correct trade-offs given limited engineering resources.
3.  **定義信任邊界（Trust Boundaries）**：在分散式系統或微服務架構中，精確劃分信任區域，並針對跨越邊界的資料流設計防禦措施。
    **Define Trust Boundaries**: Accurately delineate trust zones within distributed systems or microservices architectures, and design defenses for data flows crossing these boundaries.
4.  **產出可執行的緩解策略**：不僅僅是發現問題，還能針對不同威脅提出具體的緩解控制（Mitigation Controls）。
    **Produce Actionable Mitigation Strategies**: Go beyond discovery to propose specific mitigation controls for identified threats.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 什麼是威脅建模？ (What is Threat Modeling?)

威脅建模可以類比為「建築藍圖審查」。在蓋房子之前，你會檢查藍圖：哪裡容易被入侵？窗戶是否太脆弱？防火牆是否足夠？在軟體工程中，這是對系統架構、資料流和信任邊界的結構化分析。

Threat modeling can be analogized to a "blueprint review" in construction. Before building a house, you inspect the blueprints: Where are the entry points for intruders? Are the windows too fragile? Is the firewall sufficient? In software engineering, this is a structured analysis of system architecture, data flows, and trust boundaries.

### 2.2 關鍵模型：STRIDE (The Key Model: STRIDE)

STRIDE 是由 Microsoft 開發的最經典威脅分類模型，幫助工程師不遺漏任何面向：

STRIDE is the classic threat classification model developed by Microsoft, helping engineers ensure no aspect is overlooked:

| Acronym | Threat (威脅) | Definition (定義) | Security Property (對應的安全屬性) |
| :--- | :--- | :--- | :--- |
| **S** | **Spoofing** (欺騙/偽冒) | 假冒另一個使用者或組件 (Pretending to be something or someone other than yourself). | **Authentication** (驗證) |
| **T** | **Tampering** (竄改) | 修改磁碟、記憶體或網路傳輸中的資料 (Modifying data on disk, memory, or network). | **Integrity** (完整性) |
| **R** | **Repudiation** (抵賴) | 聲稱沒有執行某項操作，且系統無法證明其執行過 (Claiming you didn't do something). | **Non-repudiation** (不可否認性) |
| **I** | **Information Disclosure** (資訊洩露) | 將資訊暴露給未授權的個人 (Exposing information to individuals not authorized to see it). | **Confidentiality** (機密性) |
| **D** | **Denial of Service** (拒絕服務) | 耗盡資源導致服務不可用 (Denying service to valid users). | **Availability** (可用性) |
| **E** | **Elevation of Privilege** (權限提升) | 獲得比預期更高的權限 (Gaining capabilities without proper authorization). | **Authorization** (授權) |

### 2.3 風險評分：DREAD (Risk Scoring: DREAD)

一旦識別出威脅，我們使用 DREAD 來計算分數（通常 1-10 分），決定修復順序：

Once threats are identified, we use DREAD to calculate a score (usually 1-10) to determine the fix order:

*   **D**amage Potential (潛在損害): 攻擊成功會造成多大傷害？
*   **R**eproducibility (再現性): 攻擊有多容易重現？
*   **E**xploitability (利用難度): 發動攻擊需要多高的技術或成本？
*   **A**ffected Users (受影響用戶): 有多少用戶會受害？
*   **D**iscoverability (發現難度): 這個漏洞有多容易被發現？

*(註：現代實務中，Discoverability 常被忽略，因為我們假設「隱匿即安全 Security by Obscurity」是不可靠的。)*

*(Note: In modern practice, Discoverability is often omitted because assuming "Security by Obscurity" is unreliable.)*

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 系統設計面試中的應用 (Application in System Design Interviews)

在 System Design Interview 中，當面試官問到「如何保證系統安全？」時，不要只回答 "Use HTTPS" 或 "Encrypt DB"。資深工程師應該畫出 **資料流圖 (Data Flow Diagram, DFD)** 並標示 **信任邊界 (Trust Boundaries)**。

In a System Design Interview, when asked "How do you secure the system?", do not just answer "Use HTTPS" or "Encrypt DB." A senior engineer should sketch a **Data Flow Diagram (DFD)** and mark the **Trust Boundaries**.

*   **信任邊界 (Trust Boundary)**: 這是不同信任級別區域之間的界線。例如，公網 (Public Internet) 與你的 VPC 之間，或者 API Gateway 與內部微服務之間。
*   **Trust Boundary**: This is the line between areas of different trust levels. For example, between the Public Internet and your VPC, or between an API Gateway and internal microservices.

### 3.2 架構圖中的威脅視角 (Threat Perspective in Architecture)

想像一個典型的電商架構：
`Client App` -> `Load Balancer` -> `API Gateway` -> `Order Service` -> `Database`

Imagine a typical e-commerce architecture:
`Client App` -> `Load Balancer` -> `API Gateway` -> `Order Service` -> `Database`

*   **Client -> LB**: 這是最危險的邊界。
    *   *Threat*: Man-in-the-Middle (Tampering/Info Disclosure).
    *   *Mitigation*: TLS 1.3, Certificate Pinning.
*   **API Gateway**: 這是身份驗證的守門員。
    *   *Threat*: Spoofing (Fake JWT), DoS.
    *   *Mitigation*: JWT Signature Verification, Rate Limiting.
*   **Order Service -> Database**: 這是內部信任區，但仍需防禦。
    *   *Threat*: SQL Injection (Tampering), Insider Threat (Info Disclosure).
    *   *Mitigation*: ORM/Prepared Statements, Encryption at Rest, Least Privilege Access.

---

## 4. 逐步示例：微服務 API 的威脅建模
## 4. Walkthrough / Example: Threat Modeling a Microservice API

### 背景 (Background)
我們正在設計一個「用戶積分轉帳服務 (Point Transfer Service)」。用戶可以將積分轉給另一個用戶。
We are designing a "Point Transfer Service." Users can transfer points to another user.

### 步驟 1：繪製資料流與信任邊界 (Step 1: Draw Data Flow & Trust Boundaries)

```text
[User Browser] --(Internet)--> || [API Gateway] --(VPC)--> [Transfer Service] --(VPC)--> [DB]
                               ||
                       (Trust Boundary 1)
```

### 步驟 2：應用 STRIDE 分析 (Step 2: Apply STRIDE Analysis)

我們針對 `API Gateway` 到 `Transfer Service` 這一段進行分析：

We analyze the segment from `API Gateway` to `Transfer Service`:

#### 1. Spoofing (欺騙)
*   **Threat**: 攻擊者重放一個舊的轉帳請求 (Replay Attack)，或者偽造一個帶有他人 User ID 的請求。
    **Threat**: An attacker replays an old transfer request (Replay Attack) or forges a request with someone else's User ID.
*   **Mitigation**:
    *   使用短期有效的 Access Token (JWT)。
    *   在請求中加入 `nonce` 或 timestamp 防止重放。
    *   服務端嚴格校驗 Token 中的 `sub` (subject) 是否有權操作該帳戶。

#### 2. Tampering (竄改)
*   **Threat**: 攻擊者攔截請求，將轉帳金額從 100 改為 10000。
    **Threat**: An attacker intercepts the request and changes the transfer amount from 100 to 10000.
*   **Mitigation**:
    *   強制使用 HTTPS (TLS 1.2+)。
    *   對關鍵交易資料進行數位簽章 (Digital Signature) 驗證（如 HMAC）。

#### 3. Repudiation (抵賴)
*   **Threat**: 用戶轉帳後聲稱自己沒做，要求退款。
    **Threat**: A user transfers points but claims they didn't do it, demanding a refund.
*   **Mitigation**:
    *   **Audit Logs (審計日誌)**：記錄所有交易的 Source IP, Timestamp, User ID, Transaction ID。
    *   日誌需寫入 WORM (Write Once Read Many) 存儲介質，防止管理員竄改。

#### 4. Information Disclosure (資訊洩露)
*   **Threat**: 錯誤訊息 (Error Message) 洩露了資料庫結構或用戶餘額。
    **Threat**: Error messages leak database structure or user balances.
*   **Mitigation**:
    *   統一錯誤處理 (Generic Error Handling)。
    *   不要在 HTTP Response 中回傳 Stack Trace。

#### 5. Denial of Service (拒絕服務)
*   **Threat**: 惡意腳本發送大量轉帳請求，耗盡 DB 連線池。
    **Threat**: Malicious scripts send massive transfer requests, exhausting the DB connection pool.
*   **Mitigation**:
    *   在 API Gateway 層實施 Rate Limiting (e.g., Token Bucket algorithm)。
    *   在 Service 層實施 Circuit Breaker。

#### 6. Elevation of Privilege (權限提升)
*   **Threat**: 普通用戶嘗試呼叫 `/admin/refund` 接口。
    **Threat**: A regular user tries to call the `/admin/refund` endpoint.
*   **Mitigation**:
    *   Role-Based Access Control (RBAC)。
    *   API Gateway 檢查 Scope/Role claim。

### 步驟 3：DREAD 評分範例 (Step 3: DREAD Scoring Example)

假設我們發現「API 沒有 Rate Limiting」這個漏洞：

Suppose we identify the vulnerability "API lacks Rate Limiting":

*   **Damage**: 8 (服務可能完全癱瘓)
*   **Reproducibility**: 10 (寫個 script 就能重現)
*   **Exploitability**: 10 (不需要特殊工具)
*   **Affected Users**: 9 (所有用戶無法使用)
*   **Discoverability**: 10 (非常容易被發現)
*   **Total**: 47/50 -> **Critical Priority (極高優先級)**

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 分析癱瘓 (Analysis Paralysis)
*   **錯誤 (Pitfall)**: 試圖找出每一個理論上存在的威脅，導致文檔過於龐大且無法執行。
    **Mistake**: Trying to find every theoretically possible threat, resulting in documentation that is too massive and unactionable.
*   **修正 (Fix)**: 專注於高風險、高可能性的威脅。使用「時間限制 (Time-boxing)」來控制建模會議的時間。

### 5.2 忽略內部威脅 (Ignoring Insider Threats)
*   **錯誤 (Pitfall)**: 認為「防火牆內是安全的」，因此微服務之間沒有驗證 (Zero Trust violation)。
    **Mistake**: Assuming "it's safe behind the firewall," leading to no authentication between microservices (Zero Trust violation).
*   **修正 (Fix)**: 假設內部網路已被入侵。服務間通訊應使用 mTLS 或 Service Mesh 進行驗證。

### 5.3 威脅建模與開發脫節 (Disconnect between Modeling and Dev)
*   **錯誤 (Pitfall)**: 威脅建模是一次性的文檔作業，開發人員寫程式時根本不看。
    **Mistake**: Threat modeling is a one-time documentation exercise; developers don't look at it when coding.
*   **修正 (Fix)**: 將威脅緩解措施轉化為 Jira/Ticket 中的具體驗收標準 (Acceptance Criteria)。

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 你如何在現有的單體架構 (Monolith) 中引入威脅建模？
### Q1: How would you introduce threat modeling into an existing monolith architecture?

*   **高分回答要點 (Key Points)**:
    *   不要試圖一次分析整個系統。
    *   **以功能為導向 (Feature-based)**：從新功能或變更最大的模組開始。
    *   **識別關鍵資產 (Identify High-Value Assets)**：先保護 PII (個人身份資訊) 和支付模組。
    *   強調 **Trust Boundaries** 的重新定義，特別是當單體開始拆分出 API 時。

### Q2: 如果業務需求緊急，必須上線一個 DREAD 分數很高的功能，你會怎麼做？
### Q2: If business needs are urgent and a feature with a high DREAD score must be released, what do you do?

*   **高分回答要點 (Key Points)**:
    *   展現 **Risk Management** 思維，而非單純的技術拒絕。
    *   提出 **補償性控制 (Compensating Controls)**：例如，如果無法修復 SQL Injection 漏洞（極端假設），是否可以暫時開啟高強度的 WAF (Web Application Firewall) 規則？或者加強監控與人工審核？
    *   明確記錄 **Risk Acceptance**，由業務負責人簽字承擔風險，並設定修復期限 (SLA)。

### Q3: 請解釋 CSRF (Cross-Site Request Forgery) 屬於 STRIDE 的哪一類？如何防禦？
### Q3: Explain which category of STRIDE CSRF falls into and how to defend against it.

*   **高分回答要點 (Key Points)**:
    *   CSRF 主要屬於 **Spoofing** (偽冒用戶意圖) 和 **Elevation of Privilege** (利用用戶權限)。
    *   防禦：使用 Anti-CSRF Token、檢查 `Referer`/`Origin` header、設定 Cookie 的 `SameSite` 屬性。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 本章重點 (Key Takeaways)
1.  **Shift Left**: 威脅建模應在設計階段進行，修復成本最低。
2.  **STRIDE**: 是識別威脅的標準框架 (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege)。
3.  **Trust Boundaries**: 畫出架構圖中的信任邊界是分析的第一步。
4.  **DREAD**: 用於量化風險，幫助團隊決定優先級。
5.  **Mitigation**: 每個威脅都必須有對應的緩解措施、轉移風險或接受風險。

### 後續延伸 (Next Steps)
*   **自動化工具**: 學習如何將威脅建模工具 (如 Microsoft Threat Modeling Tool 或 OWASP Threat Dragon) 整合進 CI/CD 流程。
*   **下一章預告**: 了解了如何識別威脅後，下一章我們將探討 **`Cryptography & Key Management` (密碼學與金鑰管理)**，這是實作緩解措施（如防竄改、防洩露）的基石。