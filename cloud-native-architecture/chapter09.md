# Chapter 09: Cloud-Native Security: Zero Trust & DevSecOps
# 第 9 章：雲原生資安：零信任與 DevSecOps

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In traditional monolithic architectures, security often relied on a "Castle and Moat" strategy—a strong perimeter firewall with a trusted internal network. However, in Cloud-Native environments, workloads are ephemeral, dynamic, and distributed across multiple clusters or clouds. The network perimeter has dissolved, making "Zero Trust" the de facto standard.
在傳統單體架構中，資安往往依賴「城堡與護城河（Castle and Moat）」策略——即強大的邊界防火牆與受信任的內部網路。然而，在雲原生環境中，工作負載（Workloads）是短暫、動態且分佈在多個叢集或雲端的。網路邊界已然消融，使得「零信任（Zero Trust）」成為事實上的標準。

This chapter focuses on integrating security into the application lifecycle (DevSecOps) and enforcing strict identity-based controls. By the end of this chapter, you will be able to:
本章專注於將資安整合至應用程式生命週期（DevSecOps），並實施嚴格的基於身分的控制。完成本章後，你將能夠：

1.  **Implement Zero Trust Principles**: Understand how to shift from IP-based allow-lists to Identity-based policies (using OIDC, SPIFFE/SPIRE, or mTLS).
    **實作零信任原則**：理解如何從基於 IP 的白名單轉向基於身分的策略（使用 OIDC、SPIFFE/SPIRE 或 mTLS）。
2.  **Manage Secrets Dynamically**: Move beyond environment variables and static Kubernetes Secrets to dynamic secret injection using tools like HashiCorp Vault.
    **動態管理機敏資訊**：超越環境變數與靜態 Kubernetes Secrets，使用 HashiCorp Vault 等工具進行動態 Secret 注入。
3.  **Secure the Supply Chain**: Integrate container image scanning, signing (Cosign), and SBOM generation into your CI/CD pipeline.
    **保護供應鏈安全**：將容器映像檔掃描、簽章（Cosign）與 SBOM 生成整合至 CI/CD 流程中。
4.  **Design for Least Privilege**: Apply granular permissions at the Pod/Container level rather than the Node level.
    **設計最小權限原則**：在 Pod/Container 層級而非 Node 層級實施細粒度的權限控制。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Mental Shift: From "Location" to "Identity"
### 2.1 思維轉變：從「位置」到「身分」

**Analogy:**
Think of traditional security like a corporate office building where showing your badge at the front desk gets you access to every room inside.
**Cloud-Native Security (Zero Trust)** is like a high-security hotel. Just because you are in the lobby (the network) doesn't mean you can enter any room. You need a specific key card (Identity/Token) for the elevator, another for your floor, and another for your room. The key card expires every hour (Short-lived credentials).

**類比：**
想像傳統資安就像一棟企業辦公大樓，只要在櫃台出示證件，就能進入內部的所有房間。
**雲原生資安（零信任）** 則像是一間高規格安保的飯店。即使你在大廳（網路內），也不代表你能進入任何房間。你需要特定的房卡（身分/憑證）才能搭電梯、進入樓層與房間。而且這張房卡每小時都會過期（短效憑證）。

### 2.2 Key Definitions
### 2.2 關鍵定義

*   **Zero Trust Architecture (ZTA):**
    A security model that assumes breach and verifies each request as though it originates from an open network. "Never trust, always verify."
    **零信任架構 (ZTA)：**
    一種假設系統已被入侵的資安模型，將每個請求都視為來自開放網路進行驗證。「永不信任，始終驗證。」

*   **DevSecOps:**
    The philosophy of integrating security practices early in the software development lifecycle (Shift Left), rather than treating it as an audit gate at the end.
    **DevSecOps：**
    將資安實踐整合至軟體開發生命週期早期（左移，Shift Left）的哲學，而非將其視為最後的稽核關卡。

*   **Workload Identity:**
    Assigning a distinct identity to a running application (e.g., a Kubernetes ServiceAccount), allowing it to authenticate against other services or cloud APIs without hardcoded credentials.
    **工作負載身分：**
    賦予執行中的應用程式一個獨特身分（例如 Kubernetes ServiceAccount），使其能在不使用硬編碼憑證的情況下，對其他服務或雲端 API 進行驗證。

### 2.3 Identity vs. Network Segmentation
### 2.3 身分 vs. 網路隔離

| Feature | Traditional Network Security | Cloud-Native Zero Trust |
| :--- | :--- | :--- |
| **Trust Anchor (信任錨點)** | IP Address / Network Zone (VLAN) | Identity (ServiceAccount, JWT, x509) |
| **Enforcement Point (執行點)** | Firewall / VPN Gateway | Sidecar Proxy / Ingress / Application Code |
| **Credential Lifespan (憑證壽命)** | Long-lived (Static Keys) | Ephemeral (Rotated hourly/daily) |
| **Traffic Encryption (流量加密)** | Often plain text inside perimeter | End-to-End Encryption (mTLS) |

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production Cloud-Native environment, security is layered (Defense in Depth). As a Senior Engineer, you must design systems where the compromise of one component does not lead to a total system collapse.

在生產級的雲原生環境中，資安是分層的（縱深防禦）。作為資深工程師，你必須設計出「單一組件受駭不會導致系統全面崩潰」的架構。

### 3.1 The "4C's" of Cloud-Native Security
### 3.1 雲原生資安的「4C」層次

1.  **Cloud**: IAM roles, VPCs, Security Groups. (Infrastructure layer)
    **雲端**：IAM 角色、VPC、安全群組。（基礎設施層）
2.  **Cluster**: Kubernetes RBAC, Network Policies, Admission Controllers (OPA/Gatekeeper).
    **叢集**：Kubernetes RBAC、網路策略、准入控制器（OPA/Gatekeeper）。
3.  **Container**: Image scanning, minimal base images (Distroless), runtime security (Falco).
    **容器**：映像檔掃描、最小化基底映像檔（Distroless）、執行時安全（Falco）。
4.  **Code**: Static analysis (SAST), dependency checks, dynamic secrets.
    **程式碼**：靜態分析（SAST）、依賴項檢查、動態 Secret。

### 3.2 Dynamic Secrets Architecture (Vault Integration)
### 3.2 動態 Secret 架構（Vault 整合）

Instead of storing database passwords in Kubernetes Secrets (which are just base64 encoded strings), we use a centralized Secret Manager (e.g., HashiCorp Vault).

我們不將資料庫密碼儲存在 Kubernetes Secrets（那只是 base64 編碼的字串）中，而是使用集中式的 Secret Manager（如 HashiCorp Vault）。

**Workflow:**
1.  **Auth**: The Pod starts. The Vault Agent Sidecar authenticates with Vault using the Pod's Kubernetes ServiceAccount (JWT).
2.  **Verify**: Vault verifies the JWT against the Kubernetes API Server.
3.  **Issue**: If authorized, Vault generates a *dynamic*, short-lived database credential (creating a temporary user in the DB).
4.  **Inject**: The Agent writes these credentials to a shared memory volume (`/vault/secrets/config`).
5.  **Rotate**: When the lease expires, Vault rotates the password automatically; the app re-reads the file.

**工作流程：**
1.  **驗證**：Pod 啟動。Vault Agent Sidecar 使用 Pod 的 Kubernetes ServiceAccount (JWT) 向 Vault 進行驗證。
2.  **查核**：Vault 向 Kubernetes API Server 查核該 JWT 的有效性。
3.  **發行**：若授權通過，Vault 生成一組 *動態*、短效的資料庫憑證（在 DB 中建立臨時使用者）。
4.  **注入**：Agent 將憑證寫入共享記憶體卷（`/vault/secrets/config`）。
5.  **輪替**：當租約到期，Vault 自動輪替密碼；應用程式重新讀取檔案。

---

## 4. Walkthrough: Securing a Microservice with Zero Trust
## 4. 逐步示例：以零信任保護微服務

### Scenario
### 情境
We have a `Payment Service` that needs to access a PostgreSQL database. We want to avoid hardcoding passwords and ensure the image is free of vulnerabilities.

我們有一個 `Payment Service` 需要存取 PostgreSQL 資料庫。我們希望避免硬編碼密碼，並確保映像檔沒有漏洞。

### Step 1: Supply Chain Security (CI Phase)
### 步驟 1：供應鏈安全（CI 階段）

Before deployment, we scan and sign the image.

部署前，我們先掃描並簽署映像檔。

```yaml
# GitHub Actions / GitLab CI Snippet
steps:
  - name: Build Image
    run: docker build -t my-registry/payment-service:v1 .

  - name: Scan for Vulnerabilities (Trivy)
    run: trivy image --severity HIGH,CRITICAL --exit-code 1 my-registry/payment-service:v1
    # Fails pipeline if critical CVEs are found
    # 若發現嚴重 CVE 則中斷 pipeline

  - name: Sign Image (Cosign)
    run: cosign sign --key cosign.key my-registry/payment-service:v1
    # Ensures provenance: "We built this, not a hacker."
    # 確保來源：「這是我們建置的，不是駭客。」
```

### Step 2: Dynamic Secrets Injection (CD/Runtime Phase)
### 步驟 2：動態 Secret 注入（CD/執行階段）

We use HashiCorp Vault's Agent Injector to inject database credentials. The application reads from `localhost` file path, unaware of Vault.

我們使用 HashiCorp Vault 的 Agent Injector 來注入資料庫憑證。應用程式從 `localhost` 檔案路徑讀取，完全不需要知道 Vault 的存在。

**Deployment Manifest (`deployment.yaml`):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  template:
    metadata:
      annotations:
        # Enable Vault Agent Injection
        # 啟用 Vault Agent 注入
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "payment-service-role"
        
        # Configure the secret template
        # 設定 Secret 模板
        vault.hashicorp.com/agent-inject-secret-db-creds: "database/creds/payment-db-role"
        vault.hashicorp.com/agent-inject-template-db-creds: |
          {{- with secret "database/creds/payment-db-role" -}}
          postgres://{{ .Data.username }}:{{ .Data.password }}@postgres-primary:5432/payment_db
          {{- end -}}
    spec:
      serviceAccountName: payment-service-sa
      containers:
        - name: app
          image: my-registry/payment-service:v1
          # App reads connection string from this file
          # 應用程式從此檔案讀取連線字串
          env:
            - name: DB_CONNECTION_FILE
              value: /vault/secrets/db-creds
```

### Step 3: Network Policy (Cluster Layer)
### 步驟 3：網路策略（叢集層）

Even with identity, we restrict network flow. Only the `payment-service` can talk to `postgres`.

即使有了身分驗證，我們仍需限制網路流量。只有 `payment-service` 可以與 `postgres` 通訊。

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-payment-to-db
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: payment-service
      ports:
        - protocol: TCP
          port: 5432
```

### Why this works?
### 為何這樣做有效？
1.  **No Long-lived Secrets**: If an attacker steals the DB password, it expires automatically (e.g., in 1 hour).
2.  **Identity Provenance**: The image is signed; Kubernetes won't run unsigned images (if Policy Controller is enforced).
3.  **Least Privilege**: Network Policy prevents lateral movement if another pod is compromised.

1.  **無長效 Secret**：如果攻擊者竊取了資料庫密碼，它會自動過期（例如 1 小時後）。
2.  **身分來源證明**：映像檔已簽署；Kubernetes 不會執行未簽署的映像檔（若強制執行 Policy Controller）。
3.  **最小權限**：若其他 Pod 被入侵，網路策略可防止橫向移動。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Storing Secrets in Environment Variables
### 5.1 將 Secret 儲存在環境變數中

*   **Anti-pattern**: `value: "super-secret-password"` or even `valueFrom: secretKeyRef` mapped to ENV.
*   **Why it's bad**: Environment variables are often logged by crash reporting tools, visible in `docker inspect`, and accessible to any process (including sub-processes) running in the container.
*   **Solution**: Mount secrets as files (tmpfs volumes) or use Secret Store CSI Driver / Vault Agent.
*   **反模式**：直接寫 `value: "super-secret-password"` 或即使是用 `valueFrom: secretKeyRef` 映射到 ENV。
*   **為何不好**：環境變數常被崩潰報告工具記錄，在 `docker inspect` 中可見，且容器內的所有行程（包含子行程）皆可存取。
*   **解法**：將 Secret 掛載為檔案（tmpfs volumes）或使用 Secret Store CSI Driver / Vault Agent。

### 5.2 The "Root" Container
### 5.2 使用 Root 權限的容器

*   **Anti-pattern**: Running containers as `root` (User ID 0).
*   **Why it's bad**: If the container runtime has a vulnerability, a root process inside the container can break out and gain root access to the host node.
*   **Solution**: Use `securityContext` to enforce `runAsNonRoot: true` and `runAsUser: 1000`.
*   **反模式**：以 `root`（User ID 0）執行容器。
*   **為何不好**：若容器執行環境有漏洞，容器內的 root 行程可能逃逸並取得宿主節點的 root 權限。
*   **解法**：使用 `securityContext` 強制設定 `runAsNonRoot: true` 與 `runAsUser: 1000`。

### 5.3 Ignoring Egress Traffic
### 5.3 忽略出口流量（Egress）

*   **Anti-pattern**: Locking down Ingress but allowing all Egress (`0.0.0.0/0`).
*   **Why it's bad**: If an attacker injects a crypto-miner or tries to exfiltrate data, they need outbound access. Open egress makes this easy.
*   **Solution**: Whitelist external APIs (e.g., Stripe, AWS S3) using Network Policies or an Egress Gateway.
*   **反模式**：鎖定 Ingress 但允許所有 Egress (`0.0.0.0/0`)。
*   **為何不好**：若攻擊者植入挖礦程式或試圖外洩資料，他們需要對外連線。開放的 Egress 讓這變得容易。
*   **解法**：使用網路策略或 Egress Gateway 白名單化外部 API（如 Stripe, AWS S3）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a system to handle a "Leaked Database Credential" incident automatically?
### Q1: 你會如何設計一個系統來自動處理「資料庫憑證洩漏」事件？

*   **Key Points**:
    *   **Short TTL**: Mention that with dynamic secrets (Vault), the window of opportunity is small (e.g., 15 mins).
    *   **Revocation**: Explain how to use the Vault API to immediately revoke a specific lease or all leases for a role.
    *   **Kill Switch**: Ability to rotate the root database credentials if the leakage is systemic.
    *   **Detection**: Audit logs showing unusual access patterns (e.g., access from an unknown IP).
*   **高分要點**：
    *   **短 TTL**：提及使用動態 Secret (Vault) 時，攻擊窗口很小（例如 15 分鐘）。
    *   **撤銷 (Revocation)**：解釋如何使用 Vault API 立即撤銷特定租約或某個角色的所有租約。
    *   **緊急開關 (Kill Switch)**：若洩漏是系統性的，具備輪替資料庫 Root 憑證的能力。
    *   **偵測**：顯示異常存取模式的稽核日誌（例如來自未知 IP 的存取）。

### Q2: Explain the difference between "Service Mesh mTLS" and "Application Level Encryption". When do you need which?
### Q2: 請解釋「Service Mesh mTLS」與「應用層加密」的差異。何時需要哪一種？

*   **Key Points**:
    *   **mTLS (Infrastructure Layer)**: Encrypts data in transit between services. Handles authentication (is Service A allowed to call Service B?). Transparent to the app.
    *   **App Level (Data Layer)**: Encrypts the payload itself (e.g., PGP, JWE). Necessary if the data must remain encrypted *at rest* in intermediate queues (like Kafka) or logs, or if the TLS termination point is not trusted.
    *   **Verdict**: mTLS is the baseline for Zero Trust; App Level is for highly sensitive data (PII/PCI).
*   **高分要點**：
    *   **mTLS（基礎設施層）**：加密服務間的傳輸中資料。處理驗證（Service A 是否允許呼叫 Service B？）。對應用程式透明。
    *   **應用層（資料層）**：加密 Payload 本身（如 PGP, JWE）。若資料在中間佇列（如 Kafka）或日誌中需保持*靜態*加密，或 TLS 終止點不受信任時必需。
    *   **結論**：mTLS 是零信任的基準；應用層加密用於高度敏感資料（PII/PCI）。

### Q3: How do you secure the "Build" phase in a containerized environment?
### Q3: 你如何在容器化環境中保護「建置（Build）」階段？

*   **Key Points**:
    *   **Distroless/Minimal Images**: Reduce attack surface.
    *   **SBOM (Software Bill of Materials)**: Knowing exactly what packages are inside.
    *   **Image Signing**: Using Cosign/Notary to ensure integrity.
    *   **No Secrets in Build Args**: Never pass credentials as `ARG` in Dockerfile.
*   **高分要點**：
    *   **Distroless/最小化映像檔**：減少攻擊面。
    *   **SBOM（軟體物料清單）**：確切知道內部包含哪些套件。
    *   **映像檔簽章**：使用 Cosign/Notary 確保完整性。
    *   **Build Args 中無 Secret**：絕不在 Dockerfile 中透過 `ARG` 傳遞憑證。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap
### 重點回顧
1.  **Identity is the Perimeter**: Firewalls are secondary; authentication (Who are you?) and authorization (What can you do?) are primary.
    **身分即邊界**：防火牆是次要的；驗證（你是誰？）與授權（你能做什麼？）才是主要的。
2.  **Shift Security Left**: Scan images, check dependencies, and lint configs *before* code hits the cluster.
    **資安左移**：在程式碼進入叢集*之前*，掃描映像檔、檢查依賴項並 Lint 設定檔。
3.  **Ephemeral Secrets**: Static passwords are a liability. Use dynamic injection (Vault) to rotate credentials frequently.
    **短效 Secret**：靜態密碼是負債。使用動態注入（Vault）頻繁輪替憑證。
4.  **Least Privilege**: Grant permissions explicitly via RBAC and Network Policies. Default to deny.
    **最小權限**：透過 RBAC 與網路策略明確授予權限。預設為拒絕。

### Next Steps
### 後續延伸
*   **Explore**: Implement **Open Policy Agent (OPA)** to write policy-as-code (e.g., "No LoadBalancer services allowed in dev namespace").
    **探索**：實作 **Open Policy Agent (OPA)** 來撰寫「策略即程式碼」（例如：「dev 命名空間不允許 LoadBalancer 服務」）。
*   **Next Chapter**: Move on to **Chapter 10: Observability & Reliability** to learn how to monitor these security events and debug distributed systems.
    **下一章**：進入 **第 10 章：可觀測性與可靠性**，學習如何監控這些資安事件並對分散式系統進行除錯。