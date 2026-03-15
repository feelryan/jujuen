# Chapter 05: Network Security & Infrastructure Hardening
# 第五章：網路安全與基礎設施加固

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Network security is the foundation upon which secure applications are built. For a Senior Software Engineer, it is no longer sufficient to rely solely on the DevOps or Security team to configure firewalls. You must understand how data travels from the client to your database and how to secure every hop. This chapter moves beyond basic concepts to focus on defense-in-depth strategies suitable for high-scale, compliance-heavy environments.
網路安全是建構安全應用程式的基石。對於資深軟體工程師而言，僅依賴 DevOps 或資安團隊來設定防火牆已不足夠。您必須了解資料如何從客戶端傳輸至資料庫，以及如何保護這中間的每一個跳躍點（hop）。本章將超越基礎概念，專注於適合大規模、高合規要求環境的縱深防禦（Defense-in-Depth）策略。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Dissect the TLS 1.3 Handshake**: Explain the differences between TLS 1.2 and 1.3, including performance implications (0-RTT) and security enhancements (Forward Secrecy).
    **剖析 TLS 1.3 握手**：解釋 TLS 1.2 與 1.3 的差異，包括效能影響（0-RTT）與安全性增強（前向保密 Forward Secrecy）。
2.  **Design Secure VPC Architectures**: Architect a Virtual Private Cloud (VPC) with public/private subnet segmentation, properly configured NAT Gateways, and strict Network ACLs/Security Groups.
    **設計安全的 VPC 架構**：架構一個具備公有/私有子網段隔離、正確配置 NAT Gateway 以及嚴格網路 ACL/安全群組（Security Groups）的虛擬私有雲。
3.  **Implement DDoS Mitigation Strategies**: Distinguish between Layer 3/4 (Volumetric) and Layer 7 (Application) attacks and apply appropriate mitigation techniques using WAF and Shielding services.
    **實作 DDoS 防禦策略**：區分 Layer 3/4（流量型）與 Layer 7（應用層）攻擊，並利用 WAF 與防護服務應用適當的緩解技術。
4.  **Harden API Gateways**: Configure API Gateways as the first line of defense, implementing throttling, IP whitelisting, and mutual TLS (mTLS).
    **加固 API Gateway**：配置 API Gateway 作為第一道防線，實作流量限制（Throttling）、IP 白名單與雙向 TLS（mTLS）。

---

## 2. Core Concepts & Mental Models
## 2. 核心觀念與心智模型

### 2.1 The Onion Model (Defense in Depth)
### 2.1 洋蔥模型（縱深防禦）

Think of infrastructure security as an onion. If an attacker peels back one layer (e.g., bypasses the WAF), they should immediately face another barrier (e.g., private subnet isolation), and then another (e.g., database authentication). Relying on a single "hard outer shell" (perimeter security) is a failed strategy in modern cloud computing.
請將基礎設施安全視為一顆洋蔥。如果攻擊者剝開了一層（例如繞過了 WAF），他們應該立即面臨另一道障礙（例如私有子網隔離），接著是下一道（例如資料庫驗證）。在現代雲端運算中，依賴單一的「堅硬外殼」（邊界安全）是註定失敗的策略。

### 2.2 TLS Handshake: 1.2 vs. 1.3
### 2.2 TLS 握手：1.2 vs. 1.3

The Transport Layer Security (TLS) handshake is critical for confidentiality and integrity.
傳輸層安全性（TLS）握手對於機密性與完整性至關重要。

*   **TLS 1.2**: Requires two round trips (2-RTT) to establish a connection. It supports older, less secure cipher suites (like RSA key exchange without Forward Secrecy).
    **TLS 1.2**：需要兩次往返（2-RTT）才能建立連線。它支援較舊、較不安全的加密套件（例如不具備前向保密的 RSA 金鑰交換）。
*   **TLS 1.3**: Reduces the handshake to one round trip (1-RTT) and supports 0-RTT for resumed sessions. It removes obsolete algorithms (SHA-1, RC4, DES) and enforces Perfect Forward Secrecy (PFS), meaning if the server's private key is stolen later, past sessions cannot be decrypted.
    **TLS 1.3**：將握手減少至一次往返（1-RTT），並支援恢復連線時的 0-RTT。它移除了過時的演算法（SHA-1, RC4, DES）並強制執行完全前向保密（PFS），這意味著即使伺服器的私鑰日後被竊，過去的連線紀錄也無法被解密。

### 2.3 Stateful vs. Stateless Filtering
### 2.3 有狀態 vs. 無狀態過濾

Understanding the difference between **Security Groups** (Stateful) and **Network ACLs** (Stateless) is vital for cloud networking (AWS/GCP/Azure).
理解 **安全群組 Security Groups**（有狀態）與 **網路 ACLs**（無狀態）之間的差異對於雲端網路（AWS/GCP/Azure）至關重要。

| Feature | Security Groups (Stateful) | Network ACLs (Stateless) |
| :--- | :--- | :--- |
| **Mental Model** | Like a bouncer at a club door. If he lets you in, he remembers you and lets you out. | Like a passport checkpoint. You get checked entering, and you get checked again leaving. |
| **Behavior** | Return traffic is automatically allowed. | Return traffic must be explicitly allowed (ephemeral ports). |
| **Scope** | Applied at the **Instance/ENI** level. | Applied at the **Subnet** level. |
| **Rule Type** | Allow rules only (usually). | Allow and Deny rules. |

| 特性 | Security Groups (有狀態) | Network ACLs (無狀態) |
| :--- | :--- | :--- |
| **心智模型** | 像夜店門口的保鏢。如果他讓你進去，他會認得你並讓你出來。 | 像護照檢查站。進去要檢查，出來還要再檢查一次。 |
| **行為** | 自動允許回傳流量。 | 必須明確允許回傳流量（針對臨時埠口）。 |
| **範圍** | 套用於 **實例/網卡（ENI）** 層級。 | 套用於 **子網段（Subnet）** 層級。 |
| **規則類型** | 通常只有「允許」規則。 | 包含「允許」與「拒絕」規則。 |

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 The "Zero Trust" Network Architecture
### 3.1 「零信任」網路架構

In a traditional system design interview, you might draw a box for "Internal Network" and assume it's safe. In a Senior-level design, you assume the internal network is hostile.
在傳統的系統設計面試中，您可能會畫一個框框代表「內部網路」並假設它是安全的。但在資深層級的設計中，您必須假設內部網路是充滿威脅的。

**Typical Production Flow:**
**典型的生產環境流程：**

1.  **Edge Layer**: Cloudflare / AWS CloudFront / AWS Shield. Handles DDoS absorption and caches static content.
    **邊緣層**：Cloudflare / AWS CloudFront / AWS Shield。處理 DDoS 吸收並快取靜態內容。
2.  **Ingress Layer**: Public Load Balancer (ALB) in a Public Subnet. Terminates public TLS.
    **入口層**：位於公有子網段的公有負載平衡器（ALB）。終止公開的 TLS 連線。
3.  **Gateway Layer**: API Gateway / Ingress Controller. Inspects JWTs, enforces rate limits.
    **閘道層**：API Gateway / Ingress Controller。檢查 JWT，執行速率限制。
4.  **Application Layer**: Microservices in Private Subnets. They accept traffic *only* from the Load Balancer's Security Group.
    **應用層**：位於私有子網段的微服務。它們*僅*接受來自負載平衡器安全群組的流量。
5.  **Data Layer**: Databases in Isolated Subnets. No internet access (Egress via NAT Gateway only if necessary for patches).
    **資料層**：位於隔離子網段的資料庫。無網際網路存取權（僅在需要更新補丁時透過 NAT Gateway 輸出流量）。

### 3.2 Impact on Observability & Latency
### 3.2 對可觀測性與延遲的影響

*   **Latency**: Enabling mTLS (Mutual TLS) between microservices adds CPU overhead and latency due to handshakes. Using keep-alive connections and TLS 1.3 helps mitigate this.
    **延遲**：在微服務之間啟用 mTLS（雙向 TLS）會因握手而增加 CPU 開銷與延遲。使用 Keep-alive 連線與 TLS 1.3 有助於緩解此問題。
*   **Observability**: Encrypted traffic (End-to-End Encryption) makes passive network sniffing impossible. You must rely on Service Mesh sidecars (e.g., Istio, Envoy) or application logs to visualize traffic flows.
    **可觀測性**：加密流量（端對端加密）使得被動網路監聽變得不可能。您必須依賴 Service Mesh sidecar（如 Istio, Envoy）或應用程式日誌來視覺化流量流向。

---

## 4. Walkthrough: Hardening a Fintech API
## 4. 逐步示例：加固金融科技 API

### Scenario
### 情境

You are designing the infrastructure for a payment processing service. It must be PCI-DSS compliant. The naive approach puts everything in a default VPC with public IPs for easy debugging. We need to harden this.
您正在為一個支付處理服務設計基礎設施。該服務必須符合 PCI-DSS 合規要求。天真的做法是將所有東西放在預設 VPC 中，並配置公有 IP 以方便除錯。我們需要對此進行加固。

### Step 1: VPC Segmentation (Network Layer)
### 步驟 1：VPC 分割（網路層）

Instead of one subnet, we create three tiers across multiple Availability Zones (AZs):
我們不使用單一子網段，而是在多個可用區域（AZs）建立三層架構：

*   **Public Tier**: Only for NAT Gateways and Application Load Balancers (ALB).
    **公有層**：僅供 NAT Gateway 與應用負載平衡器（ALB）使用。
*   **Private App Tier**: For API containers (ECS/Kubernetes nodes). Route table points to NAT Gateway for outbound internet (e.g., to call 3rd party banks).
    **私有應用層**：供 API 容器（ECS/Kubernetes 節點）使用。路由表指向 NAT Gateway 以進行對外連線（例如呼叫第三方銀行）。
*   **Private Data Tier**: For RDS/PostgreSQL. No route to the internet.
    **私有資料層**：供 RDS/PostgreSQL 使用。完全沒有通往網際網路的路由。

### Step 2: Security Group Chaining (Transport Layer)
### 步驟 2：安全群組鏈接（傳輸層）

We do not use IP ranges (CIDRs) for internal rules. We use **Source Security Group IDs**.
我們不使用 IP 範圍（CIDRs）來設定內部規則。我們使用 **來源安全群組 ID**。

*   `sg-load-balancer`: Ingress 443 from `0.0.0.0/0`.
*   `sg-app`: Ingress 8080 **ONLY** from `sg-load-balancer`.
*   `sg-db`: Ingress 5432 **ONLY** from `sg-app`.

*   `sg-load-balancer`: 允許來自 `0.0.0.0/0` 的 443 埠流量。
*   `sg-app`: **僅**允許來自 `sg-load-balancer` 的 8080 埠流量。
*   `sg-db`: **僅**允許來自 `sg-app` 的 5432 埠流量。

### Step 3: Infrastructure as Code (Terraform Example)
### 步驟 3：基礎設施即程式碼（Terraform 範例）

Here is how a Senior Engineer defines a restrictive Security Group in Terraform. Note the explicit Egress rule.
這是一位資深工程師如何在 Terraform 中定義嚴格的安全群組。請注意明確的 Egress（輸出）規則。

```hcl
resource "aws_security_group" "payment_api" {
  name        = "payment-api-sg"
  description = "Security group for Payment API instances"
  vpc_id      = module.vpc.vpc_id

  # Ingress: Allow traffic ONLY from the Load Balancer
  # 入口：僅允許來自負載平衡器的流量
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id] # Reference by ID, not IP
  }

  # Egress: Restrict outbound traffic.
  # Do not use 0.0.0.0/0 unless necessary.
  # Example: Allow HTTPS to specific 3rd party payment gateway IPs (simplified here)
  # 出口：限制外發流量。除非必要，不要使用 0.0.0.0/0。
  # 範例：允許 HTTPS 連線至特定第三方支付閘道 IP（此處簡化示意）
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"] # Whitelisted Bank API CIDR
  }
}
```

### Step 4: Layer 7 Defense (WAF)
### 步驟 4：Layer 7 防禦（WAF）

Deploy a Web Application Firewall (WAF) on the ALB.
在 ALB 上部署 Web 應用程式防火牆（WAF）。

*   **Rate Limiting**: Block IPs making > 2000 requests/5 mins.
    **速率限制**：封鎖 5 分鐘內請求超過 2000 次的 IP。
*   **Managed Rules**: Enable AWS/Cloudflare Managed Rules for "SQL Injection" and "Common Vulnerabilities".
    **託管規則**：啟用 AWS/Cloudflare 針對「SQL 注入」與「常見漏洞」的託管規則。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Termination Gap"
### 5.1 「終止間隙」

*   **Anti-pattern**: Terminating TLS at the Load Balancer and sending unencrypted HTTP traffic to the backend services inside the VPC (`ALB (HTTPS) -> EC2 (HTTP)`).
    **反模式**：在負載平衡器終止 TLS，並將未加密的 HTTP 流量傳送至 VPC 內的後端服務（`ALB (HTTPS) -> EC2 (HTTP)`）。
*   **Why it's bad**: While the VPC provides isolation, a compromised instance inside the network can sniff all internal traffic (Zero Trust violation). Compliance standards (PCI-DSS) often require encryption in transit *everywhere*.
    **為何不好**：雖然 VPC 提供了隔離，但網路內若有一個實例被攻陷，攻擊者就能監聽所有內部流量（違反零信任原則）。合規標準（如 PCI-DSS）通常要求*無處不在*的傳輸加密。
*   **Solution**: Re-encrypt traffic at the ALB or use End-to-End encryption with mTLS.
    **解法**：在 ALB 重新加密流量，或使用 mTLS 進行端對端加密。

### 5.2 Ignoring Egress Filtering
### 5.2 忽視出口過濾

*   **Anti-pattern**: Locking down Ingress (incoming) rules tightly but leaving Egress (outgoing) rules as `Allow All 0.0.0.0/0`.
    **反模式**：嚴格鎖定 Ingress（傳入）規則，但將 Egress（傳出）規則留為 `Allow All 0.0.0.0/0`。
*   **Why it's bad**: If an attacker executes Remote Code Execution (RCE) on your server, they can easily download malware or exfiltrate your database to their own server.
    **為何不好**：如果攻擊者在您的伺服器上執行了遠端程式碼執行（RCE），他們可以輕易下載惡意軟體或將您的資料庫外洩至他們自己的伺服器。
*   **Solution**: Whitelist outbound domains/IPs or route traffic through an Egress Proxy/Firewall.
    **解法**：將外發網域/IP 列入白名單，或將流量路由經過 Egress Proxy/防火牆。

### 5.3 Misunderstanding DDoS Protection
### 5.3 誤解 DDoS 防護

*   **Anti-pattern**: Assuming autoscaling will handle a DDoS attack.
    **反模式**：假設自動擴展（Autoscaling）可以處理 DDoS 攻擊。
*   **Why it's bad**: Autoscaling takes time (minutes) to react. A massive volumetric attack will overwhelm your load balancers or exhaust your budget (Wallet-DDoS) before scaling helps. Also, scaling doesn't stop application-layer attacks (e.g., complex search queries).
    **為何不好**：自動擴展需要時間（數分鐘）反應。巨大的流量攻擊會在擴展生效前壓垮您的負載平衡器或耗盡您的預算（荷包型 DDoS）。此外，擴展無法阻止應用層攻擊（例如複雜的搜尋查詢）。
*   **Solution**: Use Edge protection (CloudFront/Shield) to drop traffic *before* it hits your VPC.
    **解法**：使用邊緣防護（CloudFront/Shield）在流量進入 VPC *之前*就將其丟棄。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Question 1: Designing for Compliance
### 問題 1：為合規性而設計
**"We need to deploy a service that handles PII (Personally Identifiable Information). How would you design the network topology to ensure maximum security?"**
**「我們需要部署一個處理 PII（個人識別資訊）的服務。你會如何設計網路拓撲以確保最大程度的安全性？」**

*   **Key Points**:
    *   **Subnet Isolation**: Separate Data, App, and Public layers.
    *   **Encryption**: TLS 1.2+ in transit (internal & external), AES-256 at rest.
    *   **Access Control**: Least privilege Security Groups (referencing IDs, not IPs).
    *   **Audit**: VPC Flow Logs enabled and sent to a tamper-proof bucket.
    *   **Egress Control**: No direct internet access for PII stores.

### Question 2: TLS Deep Dive
### 問題 2：TLS 深入探討
**"Explain the handshake process of HTTPS. How does TLS 1.3 improve upon 1.2, and are there any security risks associated with the performance improvements?"**
**「請解釋 HTTPS 的握手過程。TLS 1.3 如何改進 1.2？這些效能改進是否伴隨著任何安全風險？」**

*   **Key Points**:
    *   **1.3 Improvements**: 1-RTT handshake (faster), removal of weak ciphers (safer), mandatory Perfect Forward Secrecy.
    *   **Risk**: Mention **0-RTT (Zero Round Trip Time)** resumption. It allows replay attacks if not handled correctly by the application (idempotency is key). This shows senior-level depth.

### Question 3: Mitigating a Layer 7 Attack
### 問題 3：緩解 Layer 7 攻擊
**"Our monitoring shows a spike in 500 errors and high CPU usage, but overall bandwidth usage is normal. It looks like a botnet is hitting our search endpoint. How do you respond?"**
**「監控顯示 500 錯誤激增且 CPU 使用率極高，但整體頻寬使用量正常。看起來像是有殭屍網路正在攻擊我們的搜尋端點。你會如何應對？」**

*   **Key Points**:
    *   **Diagnosis**: Identify it as a Layer 7 (App) DDoS, not Layer 3/4.
    *   **Immediate Action**: Enable WAF Rate Limiting rules.
    *   **Analysis**: Analyze logs (User-Agent, Source IP, Request Pattern).
    *   **Mitigation**: Challenge suspicious traffic (CAPTCHA), implement exponential backoff, or block specific patterns (e.g., requests with empty Referer).

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
*   **Defense in Depth**: Never rely on a single firewall. Use WAF -> ALB -> Security Group -> NACL -> App Auth.
    **縱深防禦**：絕不依賴單一防火牆。採用 WAF -> ALB -> 安全群組 -> NACL -> 應用程式驗證。
*   **TLS 1.3**: The standard for modern security. Provides 1-RTT speed and Perfect Forward Secrecy. Be aware of 0-RTT replay risks.
    **TLS 1.3**：現代安全標準。提供 1-RTT 速度與完全前向保密。需注意 0-RTT 重放風險。
*   **Least Privilege Networking**: Security Groups should reference *other Security Groups*, not IP ranges (`0.0.0.0/0`), especially for internal traffic.
    **最小權限網路**：安全群組應參照*其他安全群組*，而非 IP 範圍（`0.0.0.0/0`），特別是針對內部流量。
*   **Egress Matters**: Filter outgoing traffic to prevent data exfiltration and C&C (Command & Control) communication.
    **出口管制很重要**：過濾外發流量以防止資料外洩與 C&C（命令與控制）通訊。
*   **Edge Security**: Stop DDoS at the edge (CloudFront/CDN), not at your database.
    **邊緣安全**：在邊緣（CloudFront/CDN）阻擋 DDoS，而不是在你的資料庫層。

### Next Steps (後續延伸)
*   **Authentication & Authorization (Chapter 06)**: Now that the network is secure, how do we ensure the *user* is who they say they are? (OAuth2, OIDC, RBAC).
    **身分驗證與授權（第 06 章）**：既然網路已安全，我們如何確保*使用者*的身分屬實？（OAuth2, OIDC, RBAC）。
*   **Secret Management**: Learn how to manage the TLS certificates and database credentials securely using Vault or AWS Secrets Manager.
    **機密管理**：學習如何使用 Vault 或 AWS Secrets Manager 安全地管理 TLS 憑證與資料庫憑證。