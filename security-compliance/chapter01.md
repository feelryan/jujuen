# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，資安不再只是「修補漏洞」或「設定防火牆」，而是系統架構設計中的核心非功能性需求（Non-functional Requirement）。本章旨在將零散的資安知識系統化，建立能應用於大型分散式系統的防禦思維。

As a Senior Engineer, security is no longer just about "patching vulnerabilities" or "configuring firewalls"; it is a core non-functional requirement in system architecture design. This chapter aims to systematize scattered security knowledge and build a defensive mindset applicable to large-scale distributed systems.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用 CIA Triad 評估取捨**：在系統設計面試或實務中，精準分析安全性、效能與可用性之間的 Trade-off。
    **Apply the CIA Triad for trade-offs**: Accurately analyze the trade-offs between security, performance, and availability during system design interviews or practice.
2.  **設計防禦縱深（Defense in Depth）**：不僅依賴單一防線，而是構建多層次的防禦體系（從網路層到應用層）。
    **Design Defense in Depth**: Build a multi-layered defense system (from network to application layer) rather than relying on a single line of defense.
3.  **實踐零信任（Zero Trust）與最小權限（Least Privilege）**：理解為何「內網不再安全」，並能設計基於身份（Identity-based）的存取控制策略。
    **Implement Zero Trust and Least Privilege**: Understand why "the internal network is no longer safe" and design identity-based access control policies.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 CIA Triad：資安的黃金三角 (The Golden Triangle of Security)

所有資安決策都圍繞著這三個屬性，缺一不可，但往往需要權衡。
All security decisions revolve around these three attributes; they are indispensable but often require trade-offs.

*   **Confidentiality (機密性)**: 確保只有授權的人或系統能存取資料。
    *   *實作手段 (Implementation)*: Encryption (At rest/In transit), Access Control Lists (ACLs).
*   **Integrity (完整性)**: 確保資料未被未授權地竄改。
    *   *實作手段 (Implementation)*: Hashing (SHA-256), Digital Signatures, Checksums.
*   **Availability (可用性)**: 確保授權使用者在需要時能存取系統。
    *   *實作手段 (Implementation)*: Redundancy, DDoS Protection, Load Balancing.

> **Mental Model**: 想像一個銀行保險箱。
> *   **Confidentiality**: 只有你有鑰匙（加密）。
> *   **Integrity**: 保險箱內的物品沒有被替換成石頭（簽章驗證）。
> *   **Availability**: 銀行在營業時間內大門是開的，且保險箱沒有卡住（高可用性）。
>
> **Mental Model**: Imagine a bank safety deposit box.
> *   **Confidentiality**: Only you have the key (Encryption).
> *   **Integrity**: The items inside haven't been swapped for rocks (Signature verification).
> *   **Availability**: The bank is open during business hours, and the box isn't jammed (High Availability).

## 2.2 防禦縱深 (Defense in Depth)

不要相信單一的安全控制。如果攻擊者突破了防火牆，你的資料庫是否有第二層保護？
Do not trust a single security control. If an attacker breaches the firewall, does your database have a second layer of protection?

*   **概念 (Concept)**: 像洋蔥一樣的多層防禦。
    Like an onion, multiple layers of defense.
*   **層次 (Layers)**:
    1.  **Edge**: DDoS mitigation (e.g., Cloudflare, AWS Shield).
    2.  **Network**: VPC, Subnets, Security Groups.
    3.  **Identity**: MFA, IAM Roles.
    4.  **Application**: Input validation, WAF.
    5.  **Data**: Encryption, Backup.

## 2.3 零信任架構 (Zero Trust Architecture)

傳統的「邊界安全模型」（Perimeter Security Model，像城堡與護城河）假設內網是可信的。但在雲端與微服務時代，這個假設已失效。
The traditional "Perimeter Security Model" (like a castle and moat) assumes the internal network is trusted. However, in the era of cloud and microservices, this assumption is obsolete.

*   **核心原則 (Core Principle)**: "Never Trust, Always Verify." (永不信任，始終驗證)。
*   **轉變 (Shift)**: 重點從「網路位置」（Network Location）轉移到「身份與情境」（Identity & Context）。
    The focus shifts from "Network Location" to "Identity & Context".
*   **實踐 (Practice)**: 即使 Service A 呼叫 Service B 且兩者都在同一個 VPC 內，Service B 仍需驗證 Service A 的身份（例如透過 mTLS）。
    Even if Service A calls Service B and both are in the same VPC, Service B must still verify Service A's identity (e.g., via mTLS).

## 2.4 最小權限原則 (Principle of Least Privilege - PoLP)

實體（使用者或服務）應僅擁有完成其任務所需的**最小權限**，且僅在**最短時間**內擁有。
Entities (users or services) should possess only the **minimum privileges** necessary to perform their tasks, and only for the **minimum duration**.

*   **VS Root Access**: 避免給予 `Admin` 或 `*` 權限。
    Avoid granting `Admin` or `*` permissions.
*   **Just-in-Time (JIT) Access**: 需要時才申請權限，用完即撤銷。
    Request permissions only when needed, and revoke them immediately after use.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或架構規劃中，Security 通常是一個專門的章節，或者貫穿全場。
In System Design Interviews or architectural planning, Security is usually a dedicated section or woven throughout the discussion.

## 3.1 典型微服務架構中的資安佈局 (Security Layout in Microservices)

1.  **Public Internet -> Load Balancer**:
    *   使用 **WAF (Web Application Firewall)** 過濾 SQL Injection, XSS。
    *   啟用 HTTPS (TLS Termination)。
2.  **Load Balancer -> API Gateway**:
    *   **Authentication (AuthN)**: 驗證 JWT，確認 "Who are you"。
    *   **Rate Limiting**: 防止濫用影響 Availability。
3.  **API Gateway -> Internal Services**:
    *   **Zero Trust**: 使用 **mTLS (Mutual TLS)** 確保服務間通訊加密且雙向驗證身份。
    *   **Authorization (AuthZ)**: 服務層級檢查權限（例如 OPA - Open Policy Agent）。
4.  **Service -> Database**:
    *   **Encryption at Rest**: 硬碟加密。
    *   **IAM Auth**: 使用雲端 IAM token 取代靜態 DB password。

## 3.2 對系統品質的影響 (Impact on System Qualities)

*   **Latency (延遲)**: 加密/解密（TLS handshake）與 Token 驗證會增加 RTT。
    *   *Mitigation*: 使用 TLS 1.3 (0-RTT), Keep-Alive connections, 硬體加速。
*   **Scalability (擴展性)**: 集中式的 Auth 服務（如單一 DB 查 Session）可能成為瓶頸。
    *   *Mitigation*: 使用 Stateless Auth (JWT) 或分散式快取。
*   **Observability (可觀測性)**: 資安事件需要 Audit Logs。
    *   *Requirement*: 必須記錄 "Who did What at When"，且 Logs 本身需防竄改。

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：設計一個「敏感資料處理服務」的存取控制
## Scenario: Designing Access Control for a "Sensitive Data Processing Service"

**背景 (Context)**: 我們有一個後端服務 `PaymentService`，需要讀取儲存在 S3 上的用戶 KYC 文件（敏感個資）。

### Phase 1: Naive Approach (Implicit Trust & Static Keys)

*   **作法**: `PaymentService` 程式碼中寫死了一組 AWS Access Key / Secret Key，該 Key 擁有 `S3:FullAccess`。
*   **Approach**: `PaymentService` has hardcoded AWS Access Key / Secret Key with `S3:FullAccess`.
*   **風險 (Risks)**:
    1.  **Credential Leak**: Code commit 到 Git 就洩漏了。
    2.  **Over-privileged**: 服務可以刪除整個 Bucket，違反 PoLP。
    3.  **No Rotation**: Key 永久有效，一旦洩漏後果嚴重。

### Phase 2: Better Approach (IAM Roles & Environment Variables)

*   **作法**: 將 Key 移出程式碼，改用環境變數。或者在 AWS EC2/EKS 上綁定 IAM Role。
*   **Approach**: Move keys out of code to environment variables, or attach an IAM Role to AWS EC2/EKS.
*   **改進 (Improvement)**: 避免了 Code Leak。
*   **剩餘問題 (Remaining Issues)**: 權限可能還是太寬鬆（例如 `S3:*`）。

### Phase 3: Mature Solution (Least Privilege & Temporary Credentials)

*   **作法**:
    1.  **IAM Role**: 使用 `AssumeRole` 機制獲取短期 Token。
    2.  **Fine-grained Policy**: 僅允許 `GetObject` 且限定特定 Bucket 與 Prefix。

**Policy Example (JSON):**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"  // Only Read, no Delete/List
            ],
            "Resource": "arn:aws:s3:::kyc-documents-bucket/verified/*", // Specific path
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "true" // Enforce HTTPS
                }
            }
        }
    ]
}
```

*   **為何可行 (Why it works)**:
    *   **PoLP**: 即使駭客控制了 `PaymentService`，也無法刪除文件或讀取其他 Bucket。
    *   **Encryption in Transit**: 強制 HTTPS。
    *   **Audit**: 透過 CloudTrail 可以追蹤具體是哪個 Role Session ID 存取了資料。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Security by Obscurity (隱匿式安全)
*   **錯誤 (Pitfall)**: 把 Admin API 放在 `/super-secret-admin-v1/` 路徑下，而不加強驗證，認為沒人猜得到。
    Putting Admin APIs under `/super-secret-admin-v1/` without strong auth, assuming no one will guess it.
*   **後果 (Consequence)**: 透過 Log 分析、Brute force 或內部洩漏，路徑很容易曝光。
*   **修正 (Fix)**: 所有的 Endpoint 都必須經過標準的 AuthN/AuthZ 流程。

## 5.2 Hardcoding Secrets (硬編碼機密)
*   **錯誤 (Pitfall)**: 為了方便測試，將 API Key 或 DB Password 寫在 code 裡。
    Writing API Keys or DB Passwords in code for testing convenience.
*   **後果 (Consequence)**: 即使刪除了，Git History 裡還有。
*   **修正 (Fix)**: 使用 Secrets Manager (e.g., AWS Secrets Manager, HashiCorp Vault) 並在 Runtime 注入。

## 5.3 Default Allow (預設允許)
*   **錯誤 (Pitfall)**: 防火牆或 Security Group 設定為 `Allow 0.0.0.0/0`，想說之後再縮限。
    Setting Firewalls or Security Groups to `Allow 0.0.0.0/0`, thinking "I'll restrict it later".
*   **後果 (Consequence)**: 往往會忘記修改，導致服務直接暴露在公網。
*   **修正 (Fix)**: **Default Deny**。先全擋，再逐一開放需要的 IP/Port。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於自我檢測或面試他人，重點在於展現「縱深防禦」的思維。

## Q1: 如果我們要儲存使用者的信用卡號（PCI-DSS 範圍），你會如何設計儲存架構？
**How would you design the storage architecture if we need to store user credit card numbers (PCI-DSS scope)?**

*   **高分回答要點 (Key Points)**:
    *   **Tokenization**: 盡量不存明碼，改用 Payment Gateway 提供的 Token。
    *   **Encryption at Rest**: 若必須存，使用 **Envelope Encryption (信封加密)**。資料用 Data Key 加密，Data Key 用 Master Key (KMS) 加密。
    *   **Access Control**: 只有極少數服務能存取 Master Key。
    *   **Audit**: 嚴格記錄誰何時解密了資料。

## Q2: 在 Microservices 架構中，如何防止一個被攻陷的服務 (Compromised Service) 攻擊其他服務？
**In a Microservices architecture, how do you prevent a compromised service from attacking others?**

*   **高分回答要點 (Key Points)**:
    *   **Zero Trust / mTLS**: 服務間必須雙向驗證，不能只靠 IP 白名單。
    *   **Network Segmentation**: 將不同敏感度的服務放在不同 Subnet/VPC。
    *   **Least Privilege**: 該服務的 IAM Role 不應有權限呼叫無關的 API。
    *   **Rate Limiting**: 內部服務也要有 Rate Limit，防止被當作 DoS 攻擊發起點。

## Q3: 什麼是 "Shift Left" Security？在 CI/CD 中如何實踐？
**What is "Shift Left" Security? How do you implement it in CI/CD?**

*   **高分回答要點 (Key Points)**:
    *   **定義**: 將資安測試從開發週期的末端（部署前）移到早期（開發與 Build 階段）。
    *   **實踐**:
        *   **SAST (Static Application Security Testing)**: 在 Code Review 前掃描程式碼漏洞。
        *   **Dependency Scanning**: 自動檢查 npm/pip 套件是否有已知 CVE。
        *   **Secret Scanning**: Git commit hook 檢查是否有 Key 寫在 code 裡。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Recap)
1.  **CIA Triad**: 機密性、完整性、可用性是資安的基石。
2.  **Defense in Depth**: 像洋蔥一樣多層防禦，假設單層防禦終將失效。
3.  **Zero Trust**: 內網不再可信，身份 (Identity) 是新的邊界。
4.  **Least Privilege**: 給予最小權限、最短時間。
5.  **Security is a Trade-off**: 安全性通常會換取效能或便利性，資深工程師需懂得權衡。

## 下一步 (Next Steps)
建立好資安思維後，下一章我們將深入探討 **Authentication & Authorization (身份驗證與授權)**。
After establishing a security mindset, the next chapter will dive deep into **Authentication & Authorization**.

*   **預習關鍵字**: OAuth 2.0, OIDC (OpenID Connect), JWT (JSON Web Token), RBAC vs ABAC.