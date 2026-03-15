# CI/CD 生態系整合：Git, Webhooks 與 Artifacts / Ecosystem Integration: Git, Webhooks, and Artifacts

Jenkins 不應該是一座孤島。它的核心價值在於作為「黏著劑 (Glue)」，將原始碼管理 (SCM)、自動化測試與製品儲存庫 (Artifact Repository) 串聯起來。本章節專注於如何優雅地處理這些邊界互動。

## Mental model｜心智模型

要掌握生態系整合，請建立以下的心智模型：

### 1. 事件驅動的工廠流水線 (Event-Driven Assembly Line)
不要將 Jenkins 視為一個「定時去檢查有沒有工作的工人 (Polling)」，而應視為一個「接收訊號即刻反應的自動化產線 (Event-Driven)」。
- **Input (Trigger):** 來自 SCM 的 Webhook 事件（Push, PR Open, Tag）。
- **Process (Build):** Jenkins 根據 `Jenkinsfile` 執行建置。
- **Feedback (Status):** Jenkins 必須**即時**回報狀態給 SCM（例如 GitHub 的 Check runs），讓開發者在 Code Review 介面就能看到結果。
- **Output (Artifact):** 產出的二進位檔（JAR, Docker Image）必須送往專門的倉庫（Nexus/Artifactory/ECR），而不是留在 Jenkins 硬碟裡。

### 2. 「一次建置，多次部署」 (Build Once, Deploy Many)
整合 Artifact Repository 的核心哲學。
- 原始碼只在 Build 階段編譯一次，產出一個不可變的製品 (Immutable Artifact)。
- 後續的測試 (QA)、預備 (Staging)、生產 (Production) 階段，都是提取**同一個**製品進行部署，絕不重新編譯。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 採用 Multibranch Pipeline 與 Organization Folders
在現代 Jenkins 實踐中，手動建立一個個 Job 是過時的。
- **Pattern:** 使用 **Multibranch Pipeline** 或 **GitHub/GitLab Organization Folder**。
- **Why:** Jenkins 會自動掃描儲存庫中的所有分支，發現 `Jenkinsfile` 就自動建立對應的 Pipeline。這讓 CI 配置與程式碼生命週期完全同步（Branch 刪除，Job 自動清理）。

### 2. Webhook 優先於 Polling
- **Pattern:** 在 Git Provider (GitHub/GitLab) 設定 Webhook 指向 Jenkins。
- **Best Practice:** 確保 Webhook 包含 `X-Hub-Signature` 或類似的安全驗證，防止偽造請求。
- **Why:** `Poll SCM` (每分鐘檢查一次) 會對 Git Server 造成巨大且不必要的負載，且延遲較高。

### 3. SCM 狀態回報 (Status Reporting)
- **Pattern:** Pipeline 啟動時立即通知 SCM "Pending"，結束時通知 "Success" 或 "Failure"。
- **Implementation:** 使用 GitHub Branch Source Plugin 或 GitLab Plugin 的內建功能，或者在 `post { }` 區塊中明確呼叫更新狀態的步驟。
- **Value:** 開發者不需要離開 GitHub/GitLab 就能知道 CI 結果，這是 Developer Experience (DX) 的關鍵。

### 4. 製品晉級 (Build Promotion)
- **Pattern:** 將製品上傳至 Artifact Repository 時，區分 `snapshot` (開發版) 與 `release` (正式版)。
- **Flow:**
    1. Feature Branch -> Build -> Upload to `snapshot` repo.
    2. Merge to Main -> Build -> Upload to `staging` repo.
    3. Release Tag -> Promote existing artifact to `release` repo (or retag Docker image).

### 5. 憑證隔離 (Credentials Isolation)
- **Pattern:** 使用 Jenkins Credentials Binding Plugin。
- **Rule:** 絕對不要將 Token 硬編碼在 `Jenkinsfile` 中。
- **Scope:** 確保用於拉取程式碼的 Deploy Key 或 Personal Access Token (PAT) 權限最小化（Read-only）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Polling" Trap (頻繁輪詢)
- **Anti-pattern:** 設定 Jenkins 每分鐘 `H/1 * * * *` 去 `git fetch`。
- **Consequence:** 當專案數量變多，Git Server 會被 DDoS，導致所有人的 `git push/pull` 變慢。
- **Fix:** 嚴格要求使用 Webhook。如果 Jenkins 在防火牆內，請使用 SCM 提供的 Relay 服務或 Jenkins 的 SCM Polling 僅作為 fallback（設定較長間隔，如 15-30 分鐘）。

### 2. Jenkins as an Artifact Store (將 Jenkins 當作檔案伺服器)
- **Anti-pattern:** 過度依賴 `archiveArtifacts` 來儲存大型二進位檔，並讓下游 Job 使用 `Copy Artifact Plugin` 來傳遞檔案。
- **Consequence:** Jenkins Master 磁碟爆炸，備份困難，且無法有效管理版本與權限。
- **Fix:** 使用 Nexus, Artifactory, S3 或 Container Registry。Jenkins 只保留測試報告 (JUnit XML) 和 Logs。

### 3. Rebuilding for Environment (為不同環境重新建置)
- **Anti-pattern:** 在 QA 環境部署時重新執行 `mvn clean package`，在 Prod 時又執行一次。
- **Consequence:** 你無法保證 QA 測過的程式碼產出物與 Prod 運行的完全一致（可能依賴套件版本在期間變動了）。
- **Fix:** 嚴格遵守 "Build Once"，後續環境只做 "Deploy"。

### 4. Git Checkout Confusion (淺層複製的陷阱)
- **Pitfall:** 預設的 `checkout scm` 行為可能不包含完整的 commit history。
- **Consequence:** 如果你的 Pipeline 腳本依賴 `git describe` 來產生版號，或者需要分析 Change Log 來決定是否部署，Shallow Clone 可能會失敗。
- **Fix:** 在 Checkout 步驟明確設定 `fetchDepth` 或 extension behaviors。

---

## Checklists & workflows｜檢查清單與流程

在整合新專案至 Jenkins 時，請依序檢查：

### Integration Setup Checklist
- [ ] **Webhook 設定**：Git Repo 是否已設定 Webhook 指向 `https://<jenkins-url>/github-webhook/` (或對應路徑)？
- [ ] **防火牆/網路**：Git Server 能否連線到 Jenkins？如果不行，是否有中繼機制？
- [ ] **權限驗證**：Jenkins 是否擁有唯讀 (Read-only) 的 Git 存取權？(建議使用 App 或 Deploy Key，而非個人帳號)。
- [ ] **自動掃描**：Multibranch Pipeline 是否能正確偵測到所有分支？
- [ ] **狀態回寫**：觸發建置後，Git Commit 旁是否出現黃點 (Pending) 與綠勾 (Success)？

### Artifact Management Checklist
- [ ] **版本策略**：產出的 Artifact 是否包含唯一識別碼（如 `1.0.0-build.123` 或 Git SHA）？避免使用 `latest` 覆蓋。
- [ ] **清理策略**：Artifact Repository 是否設定了 Retention Policy（例如 Snapshot 只留 30 天）？
- [ ] **來源追溯**：Artifact 的 Metadata 中是否包含 Jenkins Build URL 或 Git Commit SHA？

---

## Real-world examples｜實戰案例

### Scenario: GitHub PR Flow with Docker Artifacts
這是一個標準的現代化流程：GitHub PR 觸發 -> 執行測試 -> 回報狀態 -> Merge 後建置 Image -> 推送至 Registry。

#### `Jenkinsfile` (Declarative)

```groovy
pipeline {
    agent any
    
    // 定義全域工具與變數
    environment {
        // 使用 Jenkins 憑證庫中的 ID
        DOCKER_CREDS = credentials('docker-registry-creds')
        REPO_URL = 'my-docker-registry.com/my-app'
        // 使用 Git Commit Short SHA 作為 Tag
        IMAGE_TAG = "${env.BUILD_NUMBER}-${sh(script:'git rev-parse --short HEAD', returnStdout: true).trim()}"
    }

    stages {
        stage('Checkout & Init') {
            steps {
                // Multibranch Pipeline 預設會自動 checkout，但這裡演示如何自訂
                checkout scm
                script {
                    // 設定當前 Build 的顯示名稱，方便在 Jenkins UI 辨識
                    currentBuild.displayName = "#${env.BUILD_NUMBER} - ${env.BRANCH_NAME}"
                }
            }
        }

        stage('Test & Build') {
            steps {
                // 模擬單元測試
                sh './mvnw test' 
            }
            post {
                always {
                    // 收集測試報告，這是 Jenkins 擅長的部分
                    junit 'target/surefire-reports/*.xml'
                }
            }
        }

        // 僅在 Main 分支或 Tag 時執行 Artifact 推送
        stage('Build & Push Image') {
            when {
                anyOf {
                    branch 'main'
                    tag '*'
                }
            }
            steps {
                script {
                    docker.withRegistry('https://my-docker-registry.com', 'docker-registry-creds') {
                        def appImage = docker.build("${REPO_URL}:${IMAGE_TAG}")
                        appImage.push()
                        appImage.push("latest") // Optional
                    }
                }
            }
        }
    }

    post {
        // 處理 Git 狀態回報 (若未使用 GitHub Branch Source Plugin 自動處理)
        failure {
            // 通知 Slack 或 Email
            echo 'Pipeline failed. Notification sent.'
        }
        success {
            echo 'Pipeline succeeded.'
        }
    }
}
```

### Key Takeaways from Example:
1.  **Dynamic Versioning:** 使用 `BUILD_NUMBER` + `Git SHA` 確保製品版本唯一性。
2.  **Conditional Execution:** 使用 `when { branch 'main' }` 區分 PR 檢查與正式建置。PR 階段只跑測試，不推 Artifact，節省儲存空間與時間。
3.  **Credential Binding:** 透過 `docker.withRegistry` 安全地使用憑證，不暴露密碼。