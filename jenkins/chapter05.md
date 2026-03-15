# 1. 前言與學習目標 (Introduction and Learning Objectives)

在 CI/CD 的世界中，Jenkins 往往掌握著通往生產環境（Production）的鑰匙。對於資深工程師而言，Jenkins 不僅僅是一個任務排程器，它是一個高價值的攻擊目標。一旦 Jenkins 被攻破，攻擊者即可透過 pipeline 注入惡意程式碼（供應鏈攻擊）或竊取雲端憑證。本章將超越基本的安裝與設定，深入探討企業級的安全性治理。

In the world of CI/CD, Jenkins often holds the keys to the production environment. For a Senior Software Engineer, Jenkins is not just a task scheduler; it is a high-value attack target. Once Jenkins is compromised, attackers can inject malicious code via pipelines (supply chain attacks) or steal cloud credentials. This chapter goes beyond basic installation and configuration to dive deep into enterprise-grade security governance.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計分層級的 RBAC 策略**：利用 Role-Based Authorization Strategy 與 Folder isolation，實現最小權限原則（Least Privilege）。
    **Design tiered RBAC strategies**: Implement the Principle of Least Privilege using Role-Based Authorization Strategy and Folder isolation.
2.  **實作外部化 Secret Management**：不再依賴 Jenkins 內建的 credentials store，而是整合 HashiCorp Vault 或 AWS Secrets Manager。
    **Implement externalized Secret Management**: Move away from relying solely on Jenkins' internal credentials store by integrating with HashiCorp Vault or AWS Secrets Manager.
3.  **防禦供應鏈攻擊（Supply Chain Attacks）**：理解如何透過 Ephemeral Agents（短暫代理節點）與 Script Security 來隔離建置環境。
    **Mitigate Supply Chain Attacks**: Understand how to isolate build environments using Ephemeral Agents and Script Security.
4.  **建立審計與合規機制**：確保所有的配置變更與 Pipeline 執行都有跡可循（Audit Trail）。
    **Establish audit and compliance mechanisms**: Ensure that all configuration changes and Pipeline executions are traceable (Audit Trail).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Jenkins 作為「銀行金庫」 (Jenkins as the "Bank Vault")

請將 Jenkins 視為銀行的金庫，而非僅僅是工廠的流水線。它儲存了原始碼的讀取權限、Artifact 的簽章金鑰，以及部署到 Kubernetes 或 AWS 的 Admin 憑證。
Think of Jenkins as a bank vault, not just a factory assembly line. It stores read access to source code, signing keys for artifacts, and Admin credentials for deploying to Kubernetes or AWS.

-   **Authentication (AuthN)**：確認「你是誰」。在企業環境中，這通常外包給 LDAP, Active Directory, 或 OIDC/SAML (如 Okta, Google Workspace)。
    **Authentication (AuthN)**: Verifying "who you are." In enterprise environments, this is usually offloaded to LDAP, Active Directory, or OIDC/SAML (e.g., Okta, Google Workspace).
-   **Authorization (AuthZ)**：確認「你能做什麼」。這是 Jenkins 內部的 RBAC 核心，決定誰能 Trigger build、誰能 Configure Job、誰能讀取 Script Approval。
    **Authorization (AuthZ)**: Verifying "what you can do." This is the core of Jenkins internal RBAC, determining who can trigger builds, configure jobs, or read Script Approvals.

## 2.2 權限隔離模型 (Permission Isolation Model)

與雲端平台（如 AWS IAM）相比，Jenkins 的權限模型歷史較為悠久且複雜。
Compared to cloud platforms (like AWS IAM), Jenkins' permission model is older and more complex.

| Concept | Jenkins Implementation | AWS Analogy |
| :--- | :--- | :--- |
| **Global Security** | `Configure Global Security` | IAM Account Settings |
| **User/Group** | Users provided by Realm (LDAP/Unix/Internal) | IAM Users / Federated Users |
| **Role/Policy** | **Role-based Authorization Strategy Plugin** | IAM Policies |
| **Scope Boundary** | **Folders / Multibranch Pipelines** | Resource Groups / Tags |
| **Secrets** | Credentials Binding / External Secrets | AWS Secrets Manager / Parameter Store |

## 2.3 信任邊界 (Trust Boundaries)

在系統設計上，必須區分 **Controller (Master)** 與 **Agent** 的信任邊界。
In system design, you must distinguish the trust boundaries between the **Controller (Master)** and the **Agent**.

-   **Controller**: 擁有最高權限，負責調度與儲存配置。**絕對不應在 Controller 上執行任何 Build Job**。
    **Controller**: Holds the highest privileges, responsible for orchestration and configuration storage. **Never run any Build Jobs on the Controller.**
-   **Agent**: 執行實際指令的地方。應視為「不可信」或「低信任」區域，且最好是短暫存在（Ephemeral）的。
    **Agent**: Where actual commands are executed. Should be treated as an "untrusted" or "low-trust" zone, and ideally, should be ephemeral.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 企業級安全架構 (Enterprise Security Architecture)

在大型組織中，Jenkins 安全架構通常涉及以下組件的協作：
In large organizations, Jenkins security architecture typically involves the collaboration of the following components:

1.  **Identity Provider (IdP)**: 透過 SAML 2.0 或 OIDC 處理單一登入 (SSO)。Jenkins 不儲存密碼。
    **Identity Provider (IdP)**: Handles Single Sign-On (SSO) via SAML 2.0 or OIDC. Jenkins does not store passwords.
2.  **Secret Store**: 使用 HashiCorp Vault 或 Cloud Provider 的 Secret Manager。Jenkins 僅在 Runtime 透過 AppRole 或 IAM Role 獲取短暫憑證。
    **Secret Store**: Uses HashiCorp Vault or a Cloud Provider's Secret Manager. Jenkins only retrieves ephemeral credentials at runtime via AppRole or IAM Role.
3.  **Network Segmentation**: Jenkins Controller 位於私有子網（Private Subnet），僅透過 Load Balancer 暴露 HTTPS 端口，並限制 Source IP。
    **Network Segmentation**: The Jenkins Controller resides in a Private Subnet, exposing only the HTTPS port via a Load Balancer, with restricted Source IP.

## 3.2 供應鏈攻擊防護 (Defense Against Supply Chain Attacks)

SolarWinds 事件教會我們：CI/CD 管道本身被植入惡意程式碼是毀滅性的。
The SolarWinds incident taught us: Malicious code injected into the CI/CD pipeline itself is devastating.

-   **Code Review for Pipelines**: `Jenkinsfile` 必須像應用程式代碼一樣經過 Code Review（利用 Multibranch Pipeline 與 SCM 的 Pull Request 機制）。
    **Code Review for Pipelines**: `Jenkinsfile` must undergo Code Review just like application code (leveraging Multibranch Pipeline and SCM Pull Request mechanisms).
-   **Checksum Verification**: 下載的工具（如 Maven wrapper, Gradle, npm packages）必須校驗 checksum，防止下載到被竄改的依賴。
    **Checksum Verification**: Downloaded tools (e.g., Maven wrapper, Gradle, npm packages) must have their checksums verified to prevent downloading tampered dependencies.

---

# 4. 逐步示例：從內建憑證到 Vault 整合 (Walkthrough: From Built-in Credentials to Vault Integration)

## 4.1 場景背景 (Scenario Context)

假設你正在維護一個 Fintech 系統的 CI/CD。目前所有的 AWS Keys 和 Database Passwords 都儲存在 Jenkins 內建的 Credentials Store 中。安全團隊要求：
1. 憑證必須定期輪替（Rotate）。
2. Jenkins 管理員不應能直接查看明文密碼。
3. 必須有存取紀錄。

Suppose you are maintaining the CI/CD for a Fintech system. Currently, all AWS Keys and Database Passwords are stored in Jenkins' built-in Credentials Store. The security team mandates:
1. Credentials must be rotated regularly.
2. Jenkins admins should not be able to view plaintext passwords directly.
3. Access logs must be available.

## 4.2 解決方案演進 (Solution Evolution)

### Phase 1: Naive Approach (Jenkins Internal Store)

最常見的做法是使用 Jenkins 的 "Secret Text" 或 "Username with Password"。
The most common approach is using Jenkins' "Secret Text" or "Username with Password".

```groovy
// Jenkinsfile (Declarative)
pipeline {
    agent any
    environment {
        // 缺點：憑證儲存在 Jenkins master disk 上（雖然有加密），
        // 且任何有權限修改 Pipeline 的人都可以 echo 出來（如果沒被 mask）。
        // Downside: Credentials stored on Jenkins master disk (encrypted),
        // and anyone who can modify the Pipeline can echo them (if not masked).
        AWS_CREDS = credentials('my-aws-creds-id')
    }
    stages {
        stage('Deploy') {
            steps {
                sh 'aws s3 cp artifact.zip s3://my-bucket --region us-east-1'
            }
        }
    }
}
```

### Phase 2: Best Practice (HashiCorp Vault Integration)

我們將憑證移至 HashiCorp Vault，並使用 `hashicorp-vault-plugin`。Jenkins 透過 AppRole 進行驗證，只在 Job 執行期間獲取 Secret。
We move credentials to HashiCorp Vault and use the `hashicorp-vault-plugin`. Jenkins authenticates via AppRole and retrieves the secret only during Job execution.

**優勢 (Advantages):**
- **Centralized Management**: 密碼輪替在 Vault 進行，Jenkins 無需修改。
- **Audit Logs**: Vault 會記錄 Jenkins 何時讀取了哪個 Secret。
- **Dynamic Secrets**: 可以生成 "Time-to-live" (TTL) 很短的動態資料庫帳號。

**實作代碼 (Implementation Code):**

```groovy
pipeline {
    agent { label 'linux-node' }
    
    stages {
        stage('Retrieve Secrets') {
            steps {
                // 使用 Vault Plugin 讀取路徑 secret/data/production/db
                // Use Vault Plugin to read path secret/data/production/db
                withVault(configuration: [timeout: 60, vaultUrl: 'https://vault.example.com'],
                          vaultCredentialId: 'jenkins-approle-auth', // Jenkins 自身的 Auth
                          vaultSecrets: [[path: 'secret/data/production/db', 
                                          secretValues: [
                                            [envVar: 'DB_USER', vaultKey: 'username'],
                                            [envVar: 'DB_PASS', vaultKey: 'password']
                                          ]]]) {
                    
                    // 在此區塊內，DB_USER 與 DB_PASS 為環境變數
                    // Inside this block, DB_USER and DB_PASS are environment variables
                    sh 'echo "Deploying with user: $DB_USER"' // Jenkins 會自動 mask 敏感資訊
                    sh './deploy-script.sh'
                }
            }
        }
    }
}
```

**複雜度分析 (Complexity Analysis):**
- **Setup**: 需要額外維護 Vault 基礎設施或使用 Cloud Service。
- **Latency**: 每次 Build 需額外網路請求至 Vault，增加少許 latency，但換來極高的安全性。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 Controller 上執行構建 (Building on Controller)

-   **錯誤描述**: 將 Jenkins Controller 的 `# of executors` 設定大於 0，並讓 Job 在 master 上跑。
    **Description**: Setting `# of executors` on the Jenkins Controller to greater than 0 and running Jobs on the master.
-   **為何不好**:
    1.  **安全性**: Build script 可以存取 Controller 的檔案系統（包括 `JENKINS_HOME` 下的 `secrets/`、`credentials.xml`）。
    2.  **穩定性**: 重型 Build 會耗盡 Controller 的 CPU/RAM，導致 UI 無回應甚至 Crash。
-   **最佳實踐**: 將 Controller 的 executors 設為 0。強制所有 Job 派發到 Agent。

## 5.2 濫用 Admin 權限 (The "Admin for All" Syndrome)

-   **錯誤描述**: 為了方便，給予開發者 "Administer" 權限，或者開啟 "Allow anonymous read access"。
    **Description**: Granting developers "Administer" privileges for convenience, or enabling "Allow anonymous read access".
-   **為何不好**: 任何誤操作都可能刪除所有 Job 或更改全域安全設定。Anonymous read 可能洩露原始碼結構或日誌中的敏感資訊。
-   **最佳實踐**: 使用 **Role-Based Authorization Strategy**。
    -   **Admin**: 僅限 DevOps Core Team。
    -   **Developer**: 僅限特定 Folder 的 Read/Build/Configure 權限。
    -   **Read-only**: 針對 Auditor 或 PM。

## 5.3 忽略 Plugin 安全性 (Ignoring Plugin Security)

-   **錯誤描述**: 安裝了數百個 Plugin 且從不更新，或者安裝已停止維護的 Plugin。
    **Description**: Installing hundreds of plugins and never updating them, or installing unmaintained plugins.
-   **為何不好**: Jenkins Plugin 是最常見的攻擊向量（Attack Vector）。舊版 Plugin 常含有已知漏洞（CVE）。
-   **最佳實踐**: 定期查看 "Plugin Manager" 的警告。使用 "Jenkins Health Advisor"。精簡 Plugin 數量，只安裝必要的。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 Q: 如何在 Jenkins 中實現「最小權限原則」(Least Privilege)?

**高分回答要點 (Key Points for a High-Score Answer):**
1.  **Infrastructure Level**: Controller 與 Agents 分離。Agent 僅擁有執行該 Job 所需的最小 IAM Role/權限。
2.  **Application Level (RBAC)**: 使用 Role-based Strategy 或 Folder-based authorization。開發團隊 A 只能看到 Folder A。
3.  **Pipeline Level**: 使用 `Script Security` (Groovy Sandbox) 限制 Pipeline 能呼叫的 Java API。
4.  **Secrets**: 僅將 Secret 注入到需要的 Stage，而非整個 Pipeline 全域。

## 6.2 Q: 如果 Jenkins Controller 被攻破，我們該如何限制損害範圍 (Blast Radius)?

**高分回答要點 (Key Points for a High-Score Answer):**
1.  **Network Isolation**: Controller 無法直接連線到 Production Server（應透過 Agent 或 CD 工具如 ArgoCD）。
2.  **Secret Encryption**: 即使拿到 `credentials.xml`，如果沒有 master key (hudson.util.Secret) 也無法解密（雖然駭客拿到 shell 通常也能拿到 key，所以重點是外部化 Secret）。
3.  **External Secrets**: 如果使用 Vault，駭客只能拿到短暫的 Token，我們可以立即在 Vault 端 Revoke，而無需重置所有系統密碼。
4.  **Immutable Logs**: 透過 Log shipping (如 Splunk/ELK) 將日誌即時送出，確保攻擊者無法抹除痕跡。

## 6.3 Q: 你會如何設計一個安全的 Jenkins Agent 架構？

**高分回答要點 (Key Points for a High-Score Answer):**
1.  **Ephemeral (短暫性)**: 使用 Kubernetes Pod 或 AWS Spot Instances 作為 Agent。每次 Build 啟動一個全新的環境，Build 完即銷毀。這避免了惡意程式殘留或環境污染。
2.  **No Root**: Agent 容器不應以 root 用戶運行。
3.  **Network Policy**: Agent 只能連線到必要的依賴庫（如 Artifactory, GitHub）和部署目標，禁止任意對外連線。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 7.1 本章記憶錨點 (Key Takeaways)

-   **Controller is Sacred**: Controller 僅負責調度，絕對不執行 Build。
-   **Externalize Secrets**: 盡量不要將 Secret 永久儲存在 Jenkins 內部，改用 Vault 或 Cloud Secret Manager。
-   **RBAC is Mandatory**: 善用 Folder 與 Role Strategy 隔離不同團隊的權限。
-   **Ephemeral Agents**: 使用容器化的短暫 Agent 來減少攻擊面並確保環境一致性。
-   **Audit Everything**: 確保所有的配置變更與 Job 執行都有日誌紀錄。

## 7.2 後續延伸 (Next Steps)

-   **Next Chapter**: `Jenkins Observability & Monitoring` (可觀測性與監控)。學習如何監控 Jenkins 的健康狀況、Queue 長度以及建立 Alert。
-   **Action Item**: 檢查你目前的 Jenkins 實例：
    1. 是否有在 Master 上執行的 Job？
    2. 是否有超過 3 個月未使用的 Admin 帳號？
    3. 嘗試設定一個從 HashiCorp Vault (Dev mode) 讀取密鑰的 Pipeline。