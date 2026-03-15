# 安全性加固與憑證管理 Checklist / Security Hardening and Credentials Management

## Mental model｜心智模型

在思考 Jenkins 的安全性時，請不要只把它當作一個「跑腳本的工具」，而應將其視為 **「基礎設施的特權閘道 (Privileged Gateway)」**。

Jenkins 通常握有通往你整個軟體供應鏈的鑰匙：原始碼存取權 (Source Code)、雲端平台憑證 (AWS/GCP/Azure Keys)、簽章金鑰 (Signing Keys) 以及生產環境的 SSH Access。一旦 Jenkins 失守，等於整個生產環境淪陷。

建立安全模型時，應遵循以下三個核心原則：

1.  **最小權限原則 (Least Privilege)**：
    *   **User 層級**：開發者不應擁有 Admin 權限，僅能操作特定 Job。
    *   **Job 層級**：Pipeline 不應存取全域憑證，僅能存取該專案所需的憑證。
    *   **Agent 層級**：建置節點 (Agent) 不應擁有 Master (Controller) 的檔案系統存取權。
2.  **隔離執行 (Isolation)**：
    *   Master (Controller) 僅負責調度，**絕對不執行**任何 Build Job。
    *   不同專案的 Build 環境應互相隔離（例如使用 Ephemeral Docker Agents）。
3.  **代碼化與不可變性 (Codification & Immutability)**：
    *   權限設定與憑證管理應盡可能透過代碼 (JCasC) 或外部 Secret Manager 管理，而非手動在 UI 點擊。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 身份驗證與授權 (Authentication & Authorization)
-   **整合 SSO**：不要使用 Jenkins 內建的 User Database。應整合 LDAP, Active Directory, GitHub OAuth 或 SAML (Okta/OneLogin)。
-   **Role-Based Strategy**：使用 [Role-based Authorization Strategy](https://plugins.jenkins.io/role-strategy/) 或 [Matrix Authorization Strategy](https://plugins.jenkins.io/matrix-auth/) 插件。
    -   建立明確的角色：`Admin`, `Developer` (僅能 Build/Cancel), `Viewer` (僅能 Read)。
    -   利用 **Folder-based Authorization** 將不同團隊的專案隔開。

### 2. 憑證管理 (Credentials Management)
-   **Scope your Credentials**：
    -   **Global**：僅限 System Admin 使用（如 Agent 連線憑證、備份儲存桶金鑰）。
    -   **Folder/Job Level**：專案特定的 Deploy Key 或 API Token 應限制在該 Folder 內，避免被其他專案的 Pipeline 盜用。
-   **Credentials Binding Plugin**：
    -   這是注入秘密的標準做法。它會將憑證設為環境變數，並在 Console Log 中自動遮罩 (Masking)。
-   **External Secret Managers**：
    -   對於大型企業，建議不將 Secret 儲存在 Jenkins Master 磁碟中，而是透過 Plugin 即時從 HashiCorp Vault, AWS Secrets Manager 或 CyberArk 讀取。

### 3. Script Security & Sandbox
-   **Groovy Sandbox**：預設開啟。Pipeline 腳本在受限的 Sandbox 中執行，防止任意執行 Java API（如 `System.exit()` 或讀取 Master 檔案系統）。
-   **Trusted Shared Libraries**：
    -   如果需要執行高權限操作（如複雜的 File IO），應將程式碼封裝在 **Global Shared Library** 中，並經過 Code Review。Shared Library 的程式碼在 Sandbox 之外執行，被視為「受信任的」。

### 4. 網路與系統層級防護
-   **CSRF Protection**：務必開啟 "Prevent Cross Site Request Forgery exploits"（預設已開啟，不可關閉）。
-   **Reverse Proxy with HTTPS**：Jenkins 本身不應直接暴露在 Internet。應透過 Nginx/Apache 或 Load Balancer 處理 SSL Termination，並限制來源 IP (Allowlist)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Build on Master" Trap (在 Master 上執行建置)
-   **Bad Practice**：為了方便，直接讓 Jenkins Master 節點執行 Shell Script 或編譯程式碼。
-   **Risk**：惡意或錯誤的腳本（如 `rm -rf /` 或高負載編譯）會導致 Master 當機，甚至讓攻擊者直接取得 Master 的 `JENKINS_HOME` 存取權（包含所有 secrets.xml）。
-   **Solution**：將 `# of executors` 在 Master 上設為 `0`。強制所有 Job 都在 Agent 上執行。

### 2. Hardcoding Secrets (硬編碼憑證)
-   **Bad Practice**：在 `Jenkinsfile` 或 Shell script 中直接寫 `password = "123456"`。
-   **Risk**：憑證會隨原始碼進版控 (Git)，且會在 Console Log 中以明文顯示。
-   **Solution**：使用 `credentials()` helper 或 `withCredentials` block。

### 3. Printing Secrets to Console (在 Log 中印出憑證)
-   **Bad Practice**：使用 `sh 'echo $MY_PASSWORD'` 來除錯。
-   **Risk**：雖然 Jenkins 會嘗試遮罩 (Masking) 已知的憑證字串（顯示為 `****`），但如果憑證經過 Base64 編碼或 JSON 格式化後再印出，遮罩機制就會失效。
-   **Solution**：嚴格禁止在 Shell 中 echo 任何敏感變數。

### 4. The "Admin for Everyone" (濫發管理員權限)
-   **Bad Practice**：因為懶得設定細緻的權限，給予開發者 "Administer" 權限。
-   **Risk**：開發者可以安裝惡意 Plugin、修改 Script Approval 清單、甚至解密系統內的所有憑證。

---

## Checklists & workflows｜檢查清單與流程

### Security Hardening Checklist (安全性加固清單)

#### System Level (系統層級)
- [ ] **Executors on Master = 0**：確認 Master 節點不執行任何 Job。
- [ ] **HTTPS Only**：透過 Reverse Proxy 強制重導向 HTTP 至 HTTPS。
- [ ] **CSRF Protection**：確認 "Crumb Issuer" (CSRF 防護) 已啟用。
- [ ] **Agent Isolation**：確認 Agent 使用獨立的 User 執行，且無法 SSH 回 Master。
- [ ] **JCasC Implementation**：權限與系統設定透過 Code 管理，禁止手動修改。

#### Authentication & Authorization (認證與授權)
- [ ] **Disable "Sign up"**：關閉 "Allow users to sign up" 選項。
- [ ] **Matrix/Role Strategy**：確認沒有使用 "Logged-in users can do anything"。
- [ ] **Anonymous Read Access Disabled**：除非是開源公開專案，否則禁止匿名讀取。
- [ ] **Audit Trail**：安裝 Audit Trail Plugin，記錄誰修改了 Job 設定或登入系統。

#### Pipeline & Credentials (流程與憑證)
- [ ] **No Hardcoded Secrets**：掃描 Jenkinsfile 確認無明文密碼。
- [ ] **Credential Scoping**：檢查 Global Credentials 是否包含不必要的專案級憑證。
- [ ] **Script Approval**：檢查 "In-process Script Approval" 清單，移除不再需要的簽核項目。
- [ ] **Workspace Cleanup**：確保 Pipeline 結束後執行 `cleanWs()`，避免敏感檔案殘留在 Agent 硬碟。

---

## Real-world examples｜實戰案例

### Example 1: 安全地注入憑證 (Secure Credential Injection)

**❌ 錯誤示範 (Anti-Pattern)：**
直接在環境變數區塊使用明文，或試圖用 shell echo。

```groovy
pipeline {
    agent any
    environment {
        // 危險！這會被記錄在 Git 歷史中
        AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE" 
    }
    stages {
        stage('Deploy') {
            steps {
                // 危險！如果 Jenkins 遮罩失敗，這會暴露密碼
                sh 'echo "Deploying with key: $AWS_ACCESS_KEY"' 
            }
        }
    }
}
```

**✅ 最佳實踐 (Best Practice)：**
使用 `withCredentials` 區塊。這能確保變數只在該區塊的 Scope 內有效，且自動處理遮罩。

```groovy
pipeline {
    agent { label 'docker-agent' } // 不在 Master 執行
    stages {
        stage('Deploy to AWS') {
            steps {
                // 使用 Credentials Binding Plugin
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-prod-deploy-user', 
                        usernameVariable: 'AWS_ACCESS_KEY_ID', 
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    // 在此區塊內，變數有效且會被遮罩
                    // 即使 sh 腳本出錯印出變數，Log 也只會顯示 ****
                    sh '''
                        aws s3 cp ./build s3://my-bucket/ --recursive
                    '''
                }
            }
        }
    }
    post {
        always {
            cleanWs() // 清理 Workspace，防止憑證殘留
        }
    }
}
```

### Example 2: 權限隔離架構 (RBAC Architecture)

在大型組織中，通常會結合 **Folder** 與 **Role-Based Strategy**：

1.  **資料夾結構**：
    *   `/Mobile-App-Team/`
    *   `/Backend-API-Team/`
2.  **角色設定 (Roles)**：
    *   `Global:Admin` -> 系統管理員 (全權)。
    *   `Global:Read` -> 所有員工 (僅能登入與讀取公共資訊)。
    *   `Project:Mobile-Dev` -> 針對 `/Mobile-App-Team/.*` 擁有 Build/Configure 權限。
    *   `Project:Backend-Dev` -> 針對 `/Backend-API-Team/.*` 擁有 Build/Configure 權限。
3.  **憑證隔離**：
    *   Mobile 的 Signing Key 存放在 `/Mobile-App-Team` 資料夾的 Credentials Store。
    *   Backend Team 的 Pipeline 即使嘗試讀取該 ID，也會因為 Scope 限制而失敗。