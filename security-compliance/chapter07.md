# 1. 前言與學習目標 (Introduction & Learning Objectives)

在傳統的軟體開發生命週期（SDLC）中，資安往往是上線前的最後一道關卡，這種模式在雲端原生（Cloud Native）的高頻部署環境下已不再適用。DevSecOps 的核心在於「左移（Shift Left）」，將資安控制整合進開發與部署的每一個環節。本章將深入探討如何在 Kubernetes 環境、基礎設施即程式碼（IaC）以及 CI/CD 流程中實踐自動化資安。

In the traditional Software Development Life Cycle (SDLC), security was often the final gate before production. This model is obsolete in Cloud Native environments characterized by high-frequency deployments. The core of DevSecOps is "Shift Left," integrating security controls into every stage of development and deployment. This chapter delves into implementing automated security within Kubernetes environments, Infrastructure as Code (IaC), and CI/CD pipelines.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計安全的 CI/CD 流水線**：在 Build、Test、Deploy 階段整合 SAST、SCA（軟體組成分析）與容器掃描工具。
    **Design a secure CI/CD pipeline**: Integrate SAST, SCA (Software Composition Analysis), and container scanning tools during Build, Test, and Deploy stages.
2.  **掌握雲端原生機密管理（Secrets Management）**：理解為何環境變數不足以應對高安全性需求，並能夠架構基於 HashiCorp Vault 或 Cloud KMS 的動態機密注入方案。
    **Master Cloud Native Secrets Management**: Understand why environment variables are insufficient for high-security needs and architect dynamic secret injection solutions based on HashiCorp Vault or Cloud KMS.
3.  **實作基礎設施即程式碼（IaC）的安全治理**：使用工具（如 Checkov、OPA Gatekeeper）在資源建立前自動攔截不合規的配置。
    **Implement IaC Security Governance**: Use tools (like Checkov, OPA Gatekeeper) to automatically intercept non-compliant configurations before resources are provisioned.
4.  **強化 Kubernetes 執行環境**：理解 Pod Security Standards、Network Policies 以及 Runtime Security（如 Falco）在防禦橫向移動（Lateral Movement）中的角色。
    **Harden Kubernetes Runtime Environments**: Understand the roles of Pod Security Standards, Network Policies, and Runtime Security (e.g., Falco) in defending against lateral movement.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 供應鏈安全與左移 (Supply Chain Security & Shift Left)

**直覺類比**：
想像你在建造一座摩天大樓。傳統資安像是大樓蓋好後，才檢查防火門是否合格；DevSecOps 則是在繪製藍圖（IaC）時就檢查設計規範，在進貨磚塊（Dependencies/Images）時就檢測是否有裂痕。

**Intuitive Analogy**:
Imagine constructing a skyscraper. Traditional security is like checking if fire doors are compliant only after the building is finished. DevSecOps is like checking design codes while drawing the blueprints (IaC) and inspecting bricks (Dependencies/Images) for cracks before they even arrive at the site.

**核心定義**：
- **Shift Left**：將資安測試從 SDLC 的右側（維運/監控）向左側（編碼/建置）移動，越早發現漏洞，修復成本越低。
- **Software Supply Chain**：從程式碼 commit、依賴套件引入、Container Image 建置到最終部署的全過程。攻擊者現在更傾向於攻擊上游（如惡意 npm 套件）而非直接攻擊強固的伺服器。

**Core Definitions**:
- **Shift Left**: Moving security testing from the right side of the SDLC (Operations/Monitoring) to the left (Coding/Building). The earlier vulnerabilities are found, the cheaper they are to fix.
- **Software Supply Chain**: The entire process from code commit, dependency introduction, and container image building to final deployment. Attackers now prefer targeting the upstream (e.g., malicious npm packages) rather than directly attacking hardened servers.

## 2.2 宣告式合規 (Declarative Compliance)

**觀念差異**：
在傳統 IT 中，合規往往依賴人工審計文件。在 Cloud Native 中，合規是「程式碼化」的。
- **Policy as Code (PaC)**：將資安規則寫成程式碼（如 Rego 語言），由引擎（如 Open Policy Agent, OPA）自動判斷是否放行。這使得資安審核變成了 CI/CD 中的一個自動化測試案例。

**Concept Difference**:
In traditional IT, compliance often relies on manual audit documentation. In Cloud Native, compliance is "codified."
- **Policy as Code (PaC)**: Writing security rules as code (e.g., Rego language), which are automatically evaluated by an engine (e.g., Open Policy Agent, OPA) to decide whether to proceed. This turns security auditing into an automated test case within CI/CD.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，Security 不應是外掛的組件，而是內嵌於架構圖中的控制流。

In system design interviews or architectural planning, Security should not be an add-on component but a control flow embedded within the architecture diagram.

## 3.1 安全的 CI/CD 流水線架構 (Secure CI/CD Pipeline Architecture)

一個成熟的 DevSecOps Pipeline 通常包含以下檢查點：

A mature DevSecOps Pipeline typically includes the following checkpoints:

1.  **IDE / Pre-commit Hook**:
    - **Linting**: 檢查語法錯誤。
    - **Secret Scanning**: 防止 AWS Keys 或 DB 密碼被 commit 進 git（工具：`git-secrets`, `trufflehog`）。
2.  **Build Stage**:
    - **SCA (Software Composition Analysis)**: 掃描 `package.json` 或 `go.mod` 中的依賴是否有已知 CVE（工具：`Snyk`, `Dependabot`）。
    - **SAST (Static Application Security Testing)**: 靜態分析原始碼中的漏洞（如 SQL Injection 風險）。
3.  **Artifact Creation**:
    - **Container Scanning**: 掃描 Base Image 與 Layers 中的 OS 漏洞（工具：`Trivy`, `Clair`）。
    - **Image Signing**: 使用 Cosign 或 Notary 對映像檔進行簽章，確保部署時的來源可信。
4.  **Deploy Stage (Admission Control)**:
    - **IaC Scanning**: 檢查 Terraform 或 Helm Chart 是否開啟了公開存取、未加密儲存等（工具：`Checkov`, `Terrascan`）。
    - **OPA Gatekeeper / Kyverno**: Kubernetes Admission Controller 攔截不符合 Policy 的部署請求（例如：禁止使用 `latest` tag，禁止 `privileged` 容器）。

## 3.2 機密管理架構 (Secrets Management Architecture)

**場景**：數百個 Microservices 需要存取不同的資料庫與第三方 API。
**挑戰**：
- Key Rotation（金鑰輪替）困難。
- 開發人員可能誤將 `.env` 檔上傳。
- 難以追蹤誰在何時使用了哪個 Key。

**Scenario**: Hundreds of Microservices need access to different databases and third-party APIs.
**Challenges**:
- Key Rotation is difficult.
- Developers might accidentally upload `.env` files.
- Hard to audit who used which key and when.

**解決方案：集中式機密管理 (Centralized Secrets Management)**
使用 HashiCorp Vault 或 AWS Secrets Manager。
- **Dynamic Secrets**: 應用程式請求時，Vault 動態產生一組「短時效」的 DB 帳號密碼。即使洩漏，幾分鐘後也會失效。
- **Identity-Based Access**: 應用程式不持有 Vault Token，而是透過 Kubernetes Service Account (JWT) 向 Vault 驗證身分（Kubernetes Auth Method）。

**Solution: Centralized Secrets Management**
Use HashiCorp Vault or AWS Secrets Manager.
- **Dynamic Secrets**: When an app requests access, Vault dynamically generates a set of "short-lived" DB credentials. Even if leaked, they expire in minutes.
- **Identity-Based Access**: Applications don't hold a Vault Token but authenticate to Vault using their Kubernetes Service Account (JWT) via the Kubernetes Auth Method.

---

# 4. 逐步示例 (Walkthrough / Example)

本節將示範如何從「不安全的 K8s 設定」演進到「整合 Vault 與 OPA 的安全架構」。

This section demonstrates the evolution from an "insecure K8s configuration" to a "secure architecture integrated with Vault and OPA."

## 4.1 階段一：Naive Approach (Anti-pattern)

開發者直接將資料庫密碼寫在 Kubernetes Deployment 的環境變數中。

The developer directly hardcodes the database password into the Kubernetes Deployment environment variables.

```yaml
# deployment.yaml (INSECURE)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest
        env:
        - name: DB_PASSWORD
          value: "SuperSecret123!" # ❌ Hardcoded secret
        securityContext:
          privileged: true # ❌ Excessive permission
```

**風險 (Risks)**：
1.  密碼明文暴露在 YAML 中，所有能讀取 git repo 的人都能看到。
2.  `privileged: true` 讓容器擁有宿主機 Root 權限，一旦被攻破，整台 Node 淪陷。
3.  使用 `latest` tag，無法保證映像檔內容的一致性與可追溯性。

1.  Password exposed in plaintext YAML; anyone with git access can see it.
2.  `privileged: true` gives the container Root access to the host; if compromised, the entire Node is lost.
3.  Using `latest` tag guarantees neither consistency nor traceability of the image content.

## 4.2 階段二：使用 K8s Secrets (Better, but not Best)

將密碼移至 Kubernetes Secret 物件。

Move the password to a Kubernetes Secret object.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: U3VwZXJTZWNyZXQxMjMh # Base64 encoded, NOT encrypted
```

**改進與不足 (Pros & Cons)**：
- ✅ 程式碼中不再有明文密碼。
- ⚠️ Base64 只是編碼不是加密。如果 ETCD 沒有加密，或者 RBAC 設定過寬（開發者有權限 `kubectl get secrets`），密碼依然會洩漏。
- ⚠️ 靜態密碼，輪替困難。

- ✅ No plaintext passwords in the code.
- ⚠️ Base64 is encoding, not encryption. If ETCD is not encrypted, or RBAC is too loose (developers can `kubectl get secrets`), the password can still leak.
- ⚠️ Static passwords are hard to rotate.

## 4.3 階段三：Vault Agent Injector & OPA (Enterprise Grade)

**目標**：應用程式啟動時，自動注入 Vault 中的密碼，並且透過 Policy 禁止不安全配置。

**Goal**: Automatically inject secrets from Vault when the application starts, and block insecure configurations via Policy.

### Step 1: OPA Policy (Rego) to block privileged containers
定義一個 Rego 規則，禁止 `privileged` 模式。

Define a Rego rule to block `privileged` mode.

```rego
package k8s.admission

deny[msg] {
  input.request.kind.kind == "Pod"
  input.request.object.spec.containers[_].securityContext.privileged == true
  msg := "Privileged containers are not allowed!"
}
```

### Step 2: Deployment with Vault Annotations
在 Deployment 中加入 Annotation，指示 Vault Agent Sidecar 注入機密。

Add Annotations to the Deployment to instruct the Vault Agent Sidecar to inject secrets.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        # Enable Vault Agent Injection
        vault.hashicorp.com/agent-inject: "true"
        # Which role to use for authentication
        vault.hashicorp.com/role: "my-app-role"
        # Where to read the secret from in Vault
        vault.hashicorp.com/agent-inject-secret-db-creds: "database/creds/my-app-role"
        # Template to format the secret file
        vault.hashicorp.com/agent-inject-template-db-creds: |
          {{- with secret "database/creds/my-app-role" -}}
          export DB_USERNAME="{{ .Data.username }}"
          export DB_PASSWORD="{{ .Data.password }}"
          {{- end -}}
    spec:
      serviceAccountName: my-app-sa
      containers:
      - name: app
        image: my-app:v1.0.2
        # App reads secrets from /vault/secrets/db-creds
        # No environment variables for secrets!
```

**運作流程 (Workflow)**：
1.  **Admission**: 當 Deployment 提交時，OPA 檢查是否包含 `privileged: true`。若有，拒絕請求。
2.  **Mutation**: Vault Injector (Mutating Webhook) 偵測到 annotation，自動在 Pod 中插入一個 `vault-agent` sidecar 容器。
3.  **Authentication**: `vault-agent` 使用 Pod 的 Service Account Token 向 Vault Server 驗證身分。
4.  **Injection**: 驗證通過後，Vault 產生動態 DB 帳號，Agent 將其寫入 Pod 內的共享記憶體 Volume (`/vault/secrets/db-creds`)。
5.  **Rotation**: 當 Lease 到期，Agent 自動更新檔案，並可發送訊號讓 App 重讀設定（SIGHUP）。

**Workflow**:
1.  **Admission**: When Deployment is submitted, OPA checks for `privileged: true`. If present, the request is denied.
2.  **Mutation**: Vault Injector (Mutating Webhook) detects annotations and automatically inserts a `vault-agent` sidecar container into the Pod.
3.  **Authentication**: `vault-agent` authenticates to the Vault Server using the Pod's Service Account Token.
4.  **Injection**: Upon successful auth, Vault generates dynamic DB credentials. The Agent writes them to a shared memory volume inside the Pod (`/vault/secrets/db-creds`).
5.  **Rotation**: When the lease expires, the Agent automatically updates the file and can signal the App to reload configurations (SIGHUP).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽視 Egress Traffic 管控 (Ignoring Egress Traffic Control)
**錯誤描述**：只設定了 Ingress 防火牆（誰可以連進來），但允許 Pod 連線到網際網路上的任意位置。
**為何不好**：如果攻擊者成功在容器內執行程式碼（RCE），他們可以輕鬆下載惡意軟體或將資料外傳（Data Exfiltration）。
**最佳實踐**：使用 Kubernetes Network Policies 實施「預設拒絕（Default Deny）」的 Egress 策略，只允許連線到必要的 DNS、DB 和 API 端點。

**Error Description**: Only configuring Ingress firewalls (who can connect in) but allowing Pods to connect anywhere on the internet.
**Why it's bad**: If an attacker achieves Remote Code Execution (RCE) inside a container, they can easily download malware or exfiltrate data.
**Best Practice**: Use Kubernetes Network Policies to implement a "Default Deny" Egress strategy, allowing connections only to necessary DNS, DB, and API endpoints.

## 5.2 在 Docker Image 中使用 `USER root` (Running as Root)
**錯誤描述**：容器預設以 root 使用者執行。
**為何不好**：雖然容器有隔離，但 root 權限增加了容器逃逸（Container Escape）後的風險。
**最佳實踐**：在 Dockerfile 中建立非特權使用者（如 `appuser`），並使用 `USER appuser` 指令切換。同時在 K8s SecurityContext 設定 `runAsNonRoot: true`。

**Error Description**: Containers running as the root user by default.
**Why it's bad**: Although containers are isolated, root privileges increase the risk impact after a Container Escape.
**Best Practice**: Create a non-privileged user (e.g., `appuser`) in the Dockerfile and switch using the `USER appuser` directive. Also, set `runAsNonRoot: true` in the K8s SecurityContext.

## 5.3 依賴混淆攻擊 (Dependency Confusion)
**錯誤描述**：公司內部使用了私有 npm/pip 套件名稱，但沒有在公有 Registry 註冊佔位符。
**為何不好**：攻擊者可以在公有 Registry 上傳同名的惡意套件並標註更高的版本號。套件管理工具可能會優先下載公有的惡意版本。
**最佳實踐**：使用 Scoped Packages（如 `@mycompany/utils`），並在 Artifactory/Nexus 設定嚴格的上游優先順序。

**Error Description**: Using private npm/pip package names internally without registering placeholders on public registries.
**Why it's bad**: Attackers can upload a malicious package with the same name and a higher version number to the public registry. Package managers might prioritize downloading the public malicious version.
**Best Practice**: Use Scoped Packages (e.g., `@mycompany/utils`) and configure strict upstream priorities in Artifactory/Nexus.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你會如何設計一個安全的 Multi-tenant Kubernetes Cluster？
**How would you design a secure Multi-tenant Kubernetes Cluster?**

**高分回答要點 (Key Points for a High Score)**：
1.  **Isolation (隔離)**：使用 Namespaces 進行邏輯隔離，配合 Network Policies 禁止跨 Namespace 通訊。
2.  **Resource Quotas (資源配額)**：防止單一 Tenant 耗盡 Cluster 資源（CPU/Memory/Pod count）。
3.  **RBAC (權限控制)**：嚴格限制誰能存取哪個 Namespace，避免使用 ClusterAdmin。
4.  **Policy Enforcement (策略強制)**：使用 OPA Gatekeeper 強制執行 Pod Security Standards（如禁止 HostPath mount）。
5.  **Node Isolation (節點隔離)**：針對高敏感 Tenant，使用 `Taints & Tolerations` 或 `RuntimeClass` (如 gVisor/Kata Containers) 將其調度到專屬節點或沙箱容器中。

## Q2: 如果在 CI/CD 掃描中發現一個依賴套件有 Critical Vulnerability，但沒有 Patch 可用，你會怎麼處理？
**If a CI/CD scan reveals a Critical Vulnerability in a dependency, but no patch is available, how do you handle it?**

**高分回答要點 (Key Points for a High Score)**：
1.  **Assess Impact (評估影響)**：確認該漏洞是否真的被應用程式觸發（Reachability Analysis）。例如，漏洞在函數 A，但我們只用了函數 B。
2.  **Mitigation (緩解措施)**：如果無法升級，是否能在 WAF 層、Network Policy 層或 App 設定層進行阻擋？
3.  **Acceptance Process (風險接受流程)**：如果確認風險可控或業務優先，需要走正式的「風險接受（Risk Acceptance）」簽核流程，設定到期日（SLA），暫時在掃描工具中 Suppress 該警報。
4.  **Monitor (監控)**：加強 Runtime 監控，關注是否有針對該漏洞的攻擊嘗試。

## Q3: 請解釋 "Immutable Infrastructure" 對資安的益處是什麼？
**Please explain the security benefits of "Immutable Infrastructure".**

**高分回答要點 (Key Points for a High Score)**：
1.  **Eliminates Configuration Drift (消除配置漂移)**：防止伺服器因長期維運而產生未知的設定變更或殘留檔案。
2.  **Simplified Forensics (簡化鑑識)**：如果發現異常，可以確信不是因為「上次修補丁留下的副作用」。任何與 Image 不符的變更都可能是入侵跡象。
3.  **Faster Patching (快速修補)**：不需登入機器逐一打 Patch，而是直接替換整個 Image/Node，確保所有實例狀態一致。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點回顧 (Key Takeaways)
1.  **Shift Left**：資安不是最後的關卡，而是從 Code Commit 到 Deploy 的每一步都要自動化檢測（SAST, SCA, IaC Scan）。
2.  **Secrets Management**：永遠不要在 Git 或 Env Vars 中儲存機密。使用 Vault 等工具實現「動態機密」與「身分驗證注入」。
3.  **Policy as Code**：使用 OPA/Kyverno 將資安政策程式碼化，在 Admission 階段攔截不合規的資源。
4.  **Least Privilege**：在 K8s 中，預設拒絕網路流量（Network Policy），預設禁止特權容器（SecurityContext），預設使用非 Root 用戶。
5.  **Supply Chain Security**：確保 Image 來源可信（Signing）且依賴套件無漏洞。

## 後續延伸 (Next Steps)
- **進階閱讀**：研究 **Service Mesh (Istio/Linkerd)** 如何透過 mTLS 實現零信任網路架構（Zero Trust Network）。
- **動手實作**：在你的 K8s cluster 中安裝 **Falco**，嘗試觸發一個「Shell in Container」的事件，並觀察 Falco 的警報日誌。
- **下一章預告**：我們將探討 **Observability & Reliability**，這對於偵測資安事件與系統異常至關重要。