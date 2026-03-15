# JCasC：Jenkins Configuration as Code 實務 / JCasC: Implementing Jenkins Configuration as Code

## Mental model｜心智模型

要掌握 JCasC，你必須改變對 Jenkins Server 的看法：從「需要細心呵護的寵物 (Pet)」轉變為「隨時可替換的牲畜 (Cattle)」。

### 1. The "Stateless" Controller Philosophy
傳統 Jenkins 管理依賴 UI 點擊，設定散落在 `JENKINS_HOME` 的數百個 XML 檔案中。JCasC 的核心理念是**將設定狀態外部化 (Externalize State)**。
- **Before JCasC**: Jenkins 是一個黑盒子，只有管理員知道裡面點了什麼設定。Server 掛掉時，重建是一場災難。
- **After JCasC**: Jenkins 是一個由 `jenkins.yaml` 驅動的引擎。只要有這個 YAML 檔、Docker Image 和 Secrets，你可以在任何地方瞬間重建出完全一樣的 Jenkins。

### 2. Bootstrapping Sequence
理解 JCasC 的啟動順序至關重要：
1. **Plugin Install**: JCasC 本身只是一個 Plugin。必須先透過 `install-plugins.sh` (Docker) 或其他方式安裝好 JCasC plugin 以及**所有被設定檔參考到的 Plugins**。
2. **Environment Variables**: 載入 Secrets 與環境變數。
3. **Configuration Apply**: JCasC 讀取 YAML，將設定注入到 Jenkins 的 Java Object 中。

> **Mentor Note**: Think of JCasC as the "Constructor" for your Jenkins instance. It runs at startup to set the initial state.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Split Configuration Files (模組化設定)
不要將所有設定塞進單一個巨大的 `jenkins.yaml`。JCasC 支援讀取目錄。
- **Pattern**: 設定 `CASC_JENKINS_CONFIG` 環境變數指向一個資料夾（例如 `/var/jenkins_home/casc_configs/`）。
- **Structure**:
  - `00-system.yaml`: 系統訊息、Executor 數量、全域設定。
  - `10-security.yaml`: 認證 (LDAP/SAML)、授權 (Matrix/RBAC)。
  - `20-credentials.yaml`: 憑證定義（通常引用外部 Secrets）。
  - `30-clouds.yaml`: Kubernetes 或 Docker Agent 設定。
  - `40-tools.yaml`: JDK, Maven, NodeJS 安裝設定。

### 2. Secret Management with Placeholders (機密管理)
絕對不要在 YAML 中明碼寫入密碼。使用 JCasC 的變數替換功能。
- **Pattern**: 使用 `${ENV_VAR_NAME}` 或 `${file:/path/to/secret}` 語法。
- **Implementation**: 結合 Kubernetes Secrets 或 HashiCorp Vault，將密碼掛載為環境變數或檔案，讓 JCasC 讀取。

```yaml
jenkins:
  systemMessage: "Jenkins configured via JCasC"
credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-token"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN_SECRET}" # Read from Env
```

### 3. GitOps Workflow
將 JCasC 設定檔放入 Git Repo 進行版本控制。
- **Pattern**: 修改 Jenkins 設定 = 發送 Pull Request。
- **Benefit**: 你擁有完整的 Audit Log（誰在什麼時候修改了權限？），並且可以輕鬆 Rollback。

### 4. Schema Validation (結構驗證)
在套用之前驗證 YAML 語法。
- **Tool**: 使用 Jenkins CLI 或 Docker 本地啟動測試。
- **Config**: 在 IDE (VS Code) 中設定 JSON Schema 驗證，指向你的 Jenkins instance (`YOUR_JENKINS_URL/configuration-as-code/schema`)，這樣寫 YAML 時會有自動補全和錯誤提示。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "ClickOps" Conflict (UI 與 Code 的衝突)
- **Anti-pattern**: 使用 JCasC 部署後，管理員又手動去 Jenkins UI 修改設定（例如修改了系統訊息）。
- **Consequence**: 下次重啟 Jenkins 時，JCasC 會再次覆蓋 UI 的修改，導致設定 "Drift" 或遺失。
- **Fix**: 安裝 `configuration-as-code-groovy` 或使用權限控管，鎖定 UI 上的特定設定區塊（雖然 JCasC 目前主要依賴「約定」而非強制鎖定，但應建立「UI 為唯讀」的團隊共識）。

### 2. Blindly Copying "Export Configuration" (盲目複製匯出檔)
- **Anti-pattern**: 直接使用 JCasC 頁面的 "Export" 按鈕產生的 YAML 當作 source of truth。
- **Pitfall**: 匯出的 YAML 通常非常冗長，包含許多預設值 (Defaults) 和不必要的雜訊。
- **Fix**: 只撰寫你「明確需要修改」的設定。保持 YAML 精簡。

### 3. Missing Plugin Dependencies (忽略插件依賴)
- **Anti-pattern**: 在 JCasC 設定了 Kubernetes Cloud，但 Docker Image 裡根本沒安裝 `kubernetes` plugin。
- **Consequence**: Jenkins 啟動失敗，拋出 `ClassNotFoundException` 或 Config Apply 錯誤。
- **Fix**: JCasC **不會** 自動幫你安裝 Plugin。請確保 `plugins.txt` (Docker) 與 `jenkins.yaml` (JCasC) 同步維護。

### 4. Hardcoding Sensitive Data (硬編碼敏感資料)
- **Anti-pattern**: `password: "superSecret123"` 直接寫在 YAML 裡並 push 到 Git。
- **Consequence**: 安全漏洞。一旦進入 Git History，就必須視為已洩漏並輪替憑證。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Adding a New Configuration
1. **Local Test**: 在本地 Docker 環境掛載新的 YAML 進行測試。
2. **Schema Check**: 確認 YAML 結構符合當前安裝的 Plugin 版本。
3. **PR & Review**: 提交 Git PR，同事審核設定變更。
4. **Deploy**: Merge 後觸發 CD Pipeline 更新 Jenkins (重啟或 Reload)。

### Implementation Checklist
- [ ] **Plugin Consistency**: 確認 `jenkins.yaml` 用到的功能，對應的 Plugin 是否已列在安裝清單中？
- [ ] **Secrets Handling**: 所有敏感資訊是否都已替換為 `${VAR}` 變數？
- [ ] **Volume Strategy**: 決定是否掛載 `JENKINS_HOME`。
    - *進階策略*：如果 JCasC 覆蓋率達 100%，你甚至可以不持久化 `config.xml`，只持久化 `jobs/` 和 `builds/`。
- [ ] **Startup Logs**: 檢查 Jenkins 啟動 Log，搜尋 `Configuration as Code` 關鍵字，確認 "Configuration loaded from ..." 且無錯誤堆疊 (Stack trace)。
- [ ] **Reload Strategy**: 知道如何不重啟 Jenkins 也能套用設定（透過 UI 的 "Reload Configuration" 或 HTTP POST `/configuration-as-code/reload`）。

---

## Real-world examples｜實戰案例

### Example 1: Defining Kubernetes Agents (K8s 雲端設定)
這是最常見的 JCasC 應用場景：定義動態 Agent。

```yaml
jenkins:
  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins"
        jenkinsUrl: "http://jenkins-service:8080"
        jenkinsTunnel: "jenkins-agent:50000"
        templates:
          - name: "maven-agent"
            label: "maven"
            yaml: |
              spec:
                containers:
                  - name: jnlp
                    image: "jenkins/inbound-agent:latest"
                  - name: maven
                    image: "maven:3.8.6-openjdk-11"
                    command: ["cat"]
                    tty: true
```

### Example 2: Security & Authorization (Matrix Auth)
設定權限矩陣，讓 Admin 擁有所有權限，開發者只有讀取與建置權限。

```yaml
jenkins:
  authorizationStrategy:
    projectMatrix:
      permissions:
        - "Overall/Administer:admin_user"
        - "Overall/Read:authenticated"
        - "Job/Build:authenticated"
        - "Job/Read:authenticated"
        - "Job/Workspace:authenticated"
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin_user"
          password: "${ADMIN_PASSWORD}" # Secret from Env
```

### Example 3: Global Shared Libraries (共用函式庫)
自動設定 Pipeline Shared Library，省去手動設定的麻煩。

```yaml
unclassified:
  globalLibraries:
    libraries:
      - name: "my-shared-library"
        defaultVersion: "main"
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/my-org/jenkins-shared-lib.git"
                credentialsId: "github-token"
```