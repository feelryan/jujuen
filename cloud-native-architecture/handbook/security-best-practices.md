# 零信任架構與資安最佳實踐 / Zero Trust Architecture & Security Best Practices

## Mental model｜心智模型

在雲原生環境中，傳統的「城堡與護城河（Castle and Moat）」防禦模型已經失效。你不能再假設「內網就是安全的」。

### 1. Identity is the New Perimeter（身份即邊界）
過去我們依賴 IP 位址和防火牆來區分「內部」與「外部」。在 Kubernetes 與微服務架構中，IP 是動態且短暫的。
**新的心智模型是：** 每一個服務請求（Request），無論來自外部還是內部，都必須經過驗證。防禦邊界不再是網路邊緣，而是依附在每一個 Workload（工作負載）的身份上。

### 2. The "Hotel Key Card" Analogy（飯店房卡比喻）
- **傳統架構**：像是一棟只有大門有鎖的透天厝。一旦小偷撬開大門（突破防火牆），他在屋內可以自由移動，進入任何房間（存取任何資料庫）。
- **零信任架構**：像是一間現代化飯店。
    - **Authentication (AuthN)**：你在櫃台登記入住（取得 Token/Certificate）。
    - **Authorization (AuthZ)**：你的房卡只能刷開你住的那間房（Least Privilege）。你不能去刷總統套房，也不能去刷機房。
    - **mTLS**：走廊上的對話都是加密的，且雙方都要出示證件確認身份。
    - **Policy Enforcement**：電梯只能到達你居住的樓層。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Workload Identity & Federation
不要在容器內儲存長效的 Access Keys (如 AWS AK/SK)。
- **Pattern**: 使用 **OIDC Federation**（如 AWS IRSA, GKE Workload Identity, Azure Workload Identity）。
- **How**: 讓 Kubernetes Service Account 與 Cloud IAM Role 綁定。Pod 啟動時，K8s 注入一個短效 Token，Cloud Provider 驗證該 Token 後交換臨時憑證。
- **Benefit**: 憑證自動輪替，無需人工管理 Secret，減少洩漏風險。

### 2. Mutual TLS (mTLS) with Service Mesh
不要在應用程式程式碼中實作加密通訊。
- **Pattern**: 將加密與身份驗證下沈至基礎設施層（Sidecar 或 CNI）。
- **How**: 使用 Linkerd, Istio 或 Cilium。
    - **Encryption**: 所有服務間通訊自動加密。
    - **Identity**: 透過 SPIFFE ID (e.g., `spiffe://cluster.local/ns/default/sa/frontend`) 識別呼叫者，而非 IP。
- **Best Practice**: 設定 `Strict` 模式，拒絕所有非加密連線。

### 3. GitOps-driven Secrets Management
絕對不要將 Secrets 明文寫入 Git，也不要手動 `kubectl apply` Secrets。
- **Pattern**: **External Secrets Operator (ESO)**。
- **How**:
    1. 將真實 Secrets 存在專用管理工具中（AWS Secrets Manager, HashiCorp Vault, Azure Key Vault）。
    2. 在 K8s 中部署 ESO。
    3. 撰寫 `ExternalSecret` CRD (YAML)，宣告「我要從 AWS 讀取 key `db-pass` 並同步到 K8s Secret `my-db-secret`」。
- **Benefit**: Git 中只有「宣告」，沒有「機密」。開發者無需接觸真實密碼。

### 4. Supply Chain Security (Shift Left)
資安不是部署後才做，而是從寫 Code 到 Build Image 都要做。
- **Image Scanning**: 在 CI Pipeline 中整合 Trivy 或 Grype，阻擋含有 Critical CVE 的 Image 推送。
- **Image Signing**: 使用 **Sigstore / Cosign** 對 Image 進行簽章。
- **Admission Control**: 使用 Kyverno 或 OPA Gatekeeper，在 Cluster 內設定策略：「只允許部署經過我方 Private Key 簽章過的 Image」。

### 5. Distroless & Immutable Containers
- **Pattern**: 使用 **Distroless** 映像檔（不包含 Shell, Package Manager）。
- **How**: 攻擊者即使入侵了應用程式，也無法執行 `sh` 或 `apt-get install` 下載惡意軟體。
- **Configuration**: 設定 `securityContext`:
    - `readOnlyRootFilesystem: true`
    - `runAsNonRoot: true`
    - `allowPrivilegeEscalation: false`

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Mode" Service Account
- **Anti-pattern**: 給予 Default Service Account 寬鬆的 RBAC 權限（如 `cluster-admin` 或全 Namespace 讀寫），並讓所有 Pod 共用它。
- **Consequence**: 只要一個 Pod 被攻破，攻擊者就能控制整個 Cluster。
- **Fix**: 每個微服務應有獨立的 Service Account，並綁定最小權限的 Role。

### 2. Secrets as Environment Variables
- **Anti-pattern**: 將密碼透過 `env` 注入容器。
- **Risk**: 環境變數容易洩漏（透過 `ps` 指令、Crash Dump、Log 輸出或監控工具 Dashboard）。
- **Fix**: 將 Secrets 掛載為 **Volume (Files)**。應用程式從檔案讀取密碼。檔案不會隨意出現在 Log 中。

### 3. Ignoring Egress Traffic (只防進不防出)
- **Anti-pattern**: 防火牆只擋 Ingress，允許 Pod 隨意連線到網際網路。
- **Risk**: 當 Pod 被植入挖礦程式或 C&C (Command & Control) 軟體時，它可以自由下載惡意 Payload 或外傳資料。
- **Fix**: 使用 **Network Policies** (Default Deny All Egress)，只白名單允許連線的外部 DNS (如 S3, Stripe API)。

### 4. "Baked-in" Configuration
- **Anti-pattern**: 將設定檔或憑證直接 `COPY` 進 Docker Image。
- **Risk**: 任何能拉取 Image 的人都能看到憑證；更換憑證需要重新 Build Image。

---

## Checklists & workflows｜檢查清單與流程

### Developer Workflow: Before Merge
- [ ] **Secret Scan**: 是否已執行 `gitleaks` 或類似工具，確保無 Hardcoded Secrets？
- [ ] **Dependency Scan**: `package.json` / `go.mod` 是否包含已知漏洞的依賴庫？
- [ ] **Non-Root**: Dockerfile 是否指定了 `USER` 指令（非 root）？

### CI/CD Pipeline Workflow
- [ ] **Image Scan**: 建置後是否執行了 Trivy/Clair 掃描？
- [ ] **Sign Image**: 是否使用 Cosign 對 Image 進行簽章？
- [ ] **Manifest Check**: 是否使用 `kube-linter` 或 `datree` 檢查 K8s YAML 的 Security Context 配置？

### Production Readiness Checklist (Cluster Level)
- [ ] **Network Policy**: 是否每個 Namespace 都有 "Default Deny" 的網路策略？
- [ ] **mTLS**: 是否已在 Mesh 層級強制開啟 mTLS？
- [ ] **Audit Logs**: 是否開啟了 Kubernetes Audit Logs 並轉發至不可篡改的儲存區？
- [ ] **Admission Controller**: 是否部署了 OPA/Kyverno 來強制執行 Pod Security Standards (PSS)？

---

## Real-world examples｜實戰案例

### Example 1: Secure Configuration with External Secrets
這是一個典型的「GitOps 友善」機密管理配置。我們不提交 Secret，只提交「如何取得 Secret 的定義」。

```yaml
# 1. 定義 Secret 來源 (e.g., AWS Secrets Manager)
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-backend-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: my-service-account # 綁定 IRSA

---
# 2. 定義要同步的 Secret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-backend-store
    kind: SecretStore
  target:
    name: db-secret-k8s # 最終在 K8s 裡生成的 Secret 名稱
  data:
  - secretKey: username
    remoteRef:
      key: prod/db/creds
      property: username
  - secretKey: password
    remoteRef:
      key: prod/db/creds
      property: password
```

### Example 2: Network Policy (The "Firewall" for Pods)
這是一個最基礎但也最重要的防禦：**預設拒絕所有流量，只開放特定白名單**。

```yaml
# 1. 預設拒絕該 Namespace 所有 Ingress (入站) 流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress

---
# 2. 只允許 'frontend' 呼叫 'backend'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Example 3: Pod Security Context (Hardening)
這是你在 Deployment YAML 中應該看到的標準配置。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
      containers:
      - name: app
        image: my-company/app:1.0.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true # 強制唯讀，防止惡意寫入
          capabilities:
            drop:
            - ALL # 移除所有 Linux Capabilities
            add:
            - NET_BIND_SERVICE # 僅視需要添加
```