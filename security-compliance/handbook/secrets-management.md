# 憑證與機密管理策略 / Secrets Management Strategy

## Mental model｜心智模型

在處理機密資訊（Secrets）時，工程師必須建立一個核心觀念：**機密資訊是「有毒廢棄物（Toxic Waste）」，而非單純的設定檔。**

如果將機密視為普通設定（Configuration），你就會傾向把它們放在 Repo、環境變數或 Docker Image 中，這正是災難的開始。正確的心智模型應包含以下三個維度：

1.  **分離原則 (Separation of Gravity)**：
    *   **Code (程式碼)**：描述邏輯，應該是公開或半公開的。
    *   **Config (設定)**：描述環境差異（如 URL、Port），通常是非機密的。
    *   **Secrets (機密)**：描述身份與權限（如 API Key、DB Password），必須隔離儲存，且**越晚注入越好**。

2.  **生命週期觀點 (Lifecycle View)**：
    *   機密不應該是靜態的「常數」，而是有生命週期的「變數」。
    *   **Creation (生成)** $\rightarrow$ **Distribution (分發)** $\rightarrow$ **Usage (使用)** $\rightarrow$ **Rotation (輪替)** $\rightarrow$ **Revocation (撤銷)**。
    *   如果你的系統無法輕易執行「輪替（Rotation）」，那麼你的機密管理策略就是失敗的。

3.  **零信任存取 (Zero Trust Access)**：
    *   應用程式不應「擁有」機密，而是透過身份「借用」機密。
    *   理想狀態下，應用程式甚至不知道機密是什麼（例如透過 mTLS 或 IAM Role），或者機密在讀取後的幾分鐘內就會過期（Short-lived Secrets）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 集中式機密管理 (Centralized Secrets Management)
不要將機密散落在各個 CI/CD 變數或伺服器檔案中。使用專門的 Vault 服務。
*   **Tools**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager.
*   **Pattern**: 應用程式啟動時，透過自身的 Identity（如 K8s Service Account 或 AWS IAM Role）向 Vault 驗證，換取所需的 DB 密碼或 API Key。

### 2. GitOps 加密策略 (Encrypted Secrets in Git)
如果你實行 GitOps，必須將所有設定納入版控，但絕對不能明碼 commit 機密。
*   **Mozilla SOPS**: 支援 AWS KMS/PGP 加密。開發者 commit 加密後的 YAML 檔案，CI/CD 或 Cluster 內部解密。
*   **Sealed Secrets (Kubernetes)**: 在 Cluster 內部署 Controller，將機密加密成 `SealedSecret` CRD，只有該 Cluster 能解密。

### 3. 動態機密與短時效憑證 (Dynamic Secrets & TTL)
這是最高級別的安全實踐。
*   **How it works**: 應用程式不使用寫死的 DB 密碼。當 App 需要連線 DB 時，它呼叫 Vault；Vault 動態在 DB 建立一個「時效只有 1 小時」的帳號並回傳給 App。
*   **Benefit**: 即使機密洩漏，攻擊者的時間視窗極短，且無法橫向移動（因為權限是針對該次 Session 產生的）。

### 4. 外部機密運算子 (External Secrets Operator, ESO)
在 Kubernetes 環境中的現代標準做法。
*   **Pattern**: 部署 ESO 在 K8s 中。ESO 負責去 AWS Secrets Manager 或 HashiCorp Vault 撈取機密，並同步成 K8s Native Secret。
*   **Advantage**: App 只需要讀取標準的 K8s Secret 環境變數，完全不需要修改程式碼來整合 Vault SDK。

### 5. 偵測與防護 (Pre-commit Hooks & Scanning)
*   **Tools**: `git-secrets`, `talisman`, `gitleaks`.
*   **Practice**: 在 Commit 前（Local）與 Push 後（CI Pipeline）掃描程式碼，確保沒有人手滑把 `AWS_ACCESS_KEY_ID` 寫進去。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Hardcoding Secrets (硬編碼)
*   **Anti-pattern**: `const API_KEY = "sk_live_12345";`
*   **Risk**: 只要有人有 Repo 讀取權限（包括離職員工、外包商），機密就外洩了。即使刪除 commit，git history 依然存在。

### 2. Baking Secrets into Docker Images (燒錄進映像檔)
*   **Anti-pattern**: 在 Dockerfile 中使用 `ENV DB_PASS=password` 或在 build time 複製含有機密的檔案。
*   **Risk**: 任何能 pull image 的人，透過 `docker inspect` 或 `docker history` 就能直接看到機密。
*   **Fix**: 使用 Run-time injection（環境變數或 Volume mount）。

### 3. Logging Secrets (日誌洩漏)
*   **Anti-pattern**: 為了 Debug，印出所有環境變數 `console.log(process.env)` 或在 CI/CD script 中 `set -x`。
*   **Risk**: 機密會被寫入 Log 系統（如 ELK, Datadog），導致 Log 系統成為高風險攻擊目標。
*   **Fix**: 使用 Log Masking/Redaction 工具，並嚴格禁止在 Log 中印出 Config 物件。

### 4. The "One Key to Rule Them All" (共用金鑰)
*   **Anti-pattern**: 所有微服務共用同一個 DB `root` 帳號，或同一個 AWS Access Key。
*   **Risk**: 違反最小權限原則（Least Privilege）。一旦洩漏，無法確定是哪個服務流出的，且必須重置所有服務的連線。

### 5. Unencrypted State Files (未加密的狀態檔)
*   **Anti-pattern**: Terraform 的 `tfstate` 檔案包含明碼的 DB 密碼，卻儲存在未加密的 S3 Bucket 或本地。
*   **Fix**: 啟用 Remote State Encryption。

---

## Checklists & workflows｜檢查清單與流程

### Developer Workflow (開發者日常)
- [ ] **Local Environment**: 本地開發使用 `.env` 檔案，並確保 `.env` 已加入 `.gitignore`。
- [ ] **No Hardcoding**: 檢查程式碼中沒有任何寫死的 Credential 字串。
- [ ] **Pre-commit**: 安裝並啟用 `pre-commit` hooks (如 gitleaks) 以防止意外提交。

### Architecture & DevOps (架構與維運)
- [ ] **Storage**: 確認所有 Production 機密都儲存在專用的 Secret Manager (Vault/AWS SM)，而非 CI/CD 變數設定中。
- [ ] **Injection**: 確認機密是在 Runtime (Pod 啟動時) 注入，而非 Build time。
- [ ] **Least Privilege**: 每個服務是否擁有獨立的 Service Account/Role？是否僅開放了必要的權限？
- [ ] **Audit Logs**: 是否開啟了 Secret Manager 的存取日誌？(誰在什麼時候讀取了這個機密？)
- [ ] **Rotation Policy**: 是否定義了機密輪替策略？(例如：每 90 天自動輪替 DB 密碼)。

### Emergency Response (緊急應變)
- [ ] **Revocation Plan**: 如果現在某個 API Key 洩漏，我們能在 5 分鐘內撤銷並發布新 Key 嗎？
- [ ] **Impact Analysis**: 我們知道這個 Key 被哪些服務使用嗎？

---

## Real-world examples｜實戰案例

### Scenario 1: Kubernetes with External Secrets Operator (ESO)

這是目前 Cloud Native 環境中最推薦的實作模式，結合了雲端託管的安全與 K8s 的便利性。

**架構圖解：**
`AWS Secrets Manager` (Source) $\leftarrow$ `ESO Controller` (Sync) $\rightarrow$ `K8s Secret` (Target) $\rightarrow$ `Pod` (Env Var)

**實作步驟 (Pseudo-YAML):**

1.  **定義 SecretStore (告訴 K8s 如何連接 AWS):**
    ```yaml
    apiVersion: external-secrets.io/v1beta1
    kind: SecretStore
    metadata:
      name: aws-backend
    spec:
      provider:
        aws:
          service: SecretsManager
          region: us-east-1
          auth:
            jwt:
              serviceAccountRef:
                name: my-service-account # 使用 IRSA (IAM Roles for Service Accounts)
    ```

2.  **定義 ExternalSecret (告訴 K8s 要同步哪個 Secret):**
    ```yaml
    apiVersion: external-secrets.io/v1beta1
    kind: ExternalSecret
    metadata:
      name: db-credentials
    spec:
      refreshInterval: 1h           # 每小時同步一次，支援自動輪替
      secretStoreRef:
        name: aws-backend
        kind: SecretStore
      target:
        name: my-app-db-secret      # 最終在 K8s 裡生成的 Secret 名稱
      data:
        - secretKey: username
          remoteRef:
            key: prod/db/mysql      # AWS 裡的 Secret Name
            property: username
        - secretKey: password
          remoteRef:
            key: prod/db/mysql
            property: password
    ```

3.  **App 使用 (標準 K8s 方式):**
    ```yaml
    env:
      - name: DB_USER
        valueFrom:
          secretKeyRef:
            name: my-app-db-secret
            key: username
    ```

### Scenario 2: GitOps with SOPS (Mozilla SOPS)

適用於需要將機密與程式碼一同版控，但又不能洩漏的場景。

**Workflow:**

1.  **加密**: 開發者在本地撰寫 `secrets.yaml` (明碼)，執行 `sops -e -i secrets.yaml`。
    *   SOPS 會呼叫 AWS KMS 或使用 PGP Key 將檔案內容加密，但保留 Key (如 `db_password`) 為明碼，只加密 Value。
2.  **提交**: 將加密後的 `secrets.yaml` 推送到 Git Repo。
3.  **解密**:
    *   FluxCD 或 ArgoCD 在 Cluster 內拉取 Git Repo。
    *   透過 Cluster 內的解密金鑰 (KMS 權限或 GPG Private Key) 自動解密並 Apply 到 Cluster 中。

**加密後的檔案範例 (Safe to commit):**
```yaml
apiVersion: v1
kind: Secret
metadata:
    name: my-secret
stringData:
    api_key: ENC[AES256_GCM,data:JK2...==] # 只有這部分被加密
sops:
    kms:
        - arn: arn:aws:kms:us-east-1:1234567890:key/xxxx
    # ... metadata about encryption ...
```