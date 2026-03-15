# Declarative Pipeline 實戰模式與語法 / Declarative Pipeline Patterns and Syntax

## Mental model｜心智模型

### Configuration over Code (設定優於程式)
不要將 Declarative Pipeline 視為傳統的程式腳本 (Script)，請將其視為一個 **狀態機的配置檔 (State Machine Configuration)**。
Think of Declarative Pipeline not as a traditional procedural script, but as a **configuration for a state machine**.

- **Structure (結構)**: 你定義的是 pipeline 的骨架（Stages, Steps），而不是控制流（Control Flow）。
- **Scope (作用域)**: 每個 `stage` 都是一個獨立的 context，擁有自己的環境變數、Agent 和條件判斷。
- **Outcome (結果導向)**: 透過 `post` 區塊來處理狀態轉換後的結果（Success, Failure, Aborted），而不是在每個步驟中寫 `try-catch`。

### The Hierarchy (層級結構)
理解層級對於變數範圍 (Scope) 至關重要：
Understanding the hierarchy is crucial for variable scoping:

1.  **Pipeline**: 全局設定 (Global context).
2.  **Agent**: 執行環境 (Where it runs).
3.  **Stages**: 邏輯分組 (Logical grouping).
4.  **Stage**: 單一階段 (Atomic phase).
5.  **Steps**: 具體指令 (Actual commands).
6.  **Post**: 收尾動作 (Cleanup/Notification).

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Clean Conditional" Pattern (乾淨的條件判斷)
不要在 `steps` 或 `script` 區塊中使用 `if-else`。善用 `when` 指令來控制 Stage 的執行。
Avoid `if-else` logic inside `steps` or `script` blocks. Leverage the `when` directive to control stage execution.

*   **Why**: 讓 Pipeline 視覺化圖表能正確反映跳過的階段，且代碼更易讀。
*   **Example**:
    ```groovy
    stage('Deploy to Prod') {
        when {
            allOf {
                branch 'main'
                tag pattern: "v\\d+.\\d+.\\d+", comparator: "REGEXP"
            }
        }
        steps { ... }
    }
    ```

### 2. The "Fail Fast & Clean" Pattern (快速失敗與清理)
使用 `options` 設定超時，並利用 `post` 區塊處理資源清理與通知，而不是在 Shell script 中處理。
Use `options` for timeouts and `post` blocks for resource cleanup and notifications, rather than handling them within Shell scripts.

*   **Pattern**:
    *   `options { timeout(time: 1, unit: 'HOURS') }`: 防止 Job 無限掛起。
    *   `post { always { junit '**/target/*.xml' } }`: 無論成功失敗都收集測試報告。

### 3. Parallel Execution for Feedback Loop (並行執行加速回饋)
將互不依賴的測試、Linting 或靜態分析放入 `parallel` 區塊。
Place independent tests, linting, or static analysis into a `parallel` block.

*   **Benefit**: 顯著減少 CI 等待時間 (Fail fast)。
*   **Tip**: 如果並行數量過多，考慮在 Kubernetes Agent 上動態生成 Pod，避免佔用固定 Agent 的 Executor。

### 4. Environment Variable Scoping (環境變數作用域)
*   **Global**: 定義在頂層 `environment {}`，適用於所有 Stage。
*   **Local**: 定義在 `stage` 內的 `environment {}`，僅該 Stage 可見。
*   **Credentials**: 使用 `credentials('id')` 綁定變數，避免在 log 中洩漏。

### 5. Docker as an Execution Environment (容器化執行環境)
不要依賴 Jenkins Agent 預裝的工具。使用 `agent { docker { ... } }` 確保建置環境的一致性。
Do not rely on tools pre-installed on the Jenkins Agent. Use `agent { docker { ... } }` to ensure build environment consistency.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Script Block" Abuse (濫用 Script 區塊)
*   **Anti-pattern**: 在 Declarative Pipeline 中塞入大量的 `script { ... }` 寫 Groovy 邏輯。
*   **Why it's bad**: 這把 Declarative 變成了難以維護的 Scripted Pipeline，破壞了結構驗證與視覺化功能。
*   **Solution**: 如果邏輯太複雜，請移至 **Shared Library** 或封裝成外部 Shell/Python script。

### 2. Logic inside `sh` Steps (Shell 步驟中的複雜邏輯)
*   **Anti-pattern**:
    ```groovy
    sh """
      if [ -f "file.txt" ]; then
        # 50 lines of logic...
      fi
    """
    ```
*   **Why it's bad**: 難以除錯、難以閱讀、無法重用。
*   **Solution**: 將邏輯寫入專案 repo 中的 `./scripts/build.sh`，Pipeline 只負責呼叫。

### 3. Hardcoding Paths or Credentials (硬編碼路徑或憑證)
*   **Anti-pattern**: `sh 'docker login -u user -p password'` 或 `/home/jenkins/tools/...`。
*   **Solution**: 使用 Jenkins Credentials Binding 和 `tool` 指令（或 Docker agent）。

### 4. Ignoring the `agent none` (忽略 Agent None)
*   **Pitfall**: 在頂層定義 `agent any`，但實際上只有部分 Stage 需要重型資源。
*   **Best Practice**: 頂層使用 `agent none`，並在具體的 Stage 中定義需要的 Agent（如 `agent { label 'linux' }`），節省資源。

---

## Checklists & workflows｜檢查清單與流程

在提交 `Jenkinsfile` 之前，請執行以下檢查：
Before committing your `Jenkinsfile`, run through this checklist:

### Structure & Syntax (結構與語法)
- [ ] **Linter Check**: 是否已使用 Jenkins Linter (VS Code plugin 或 CLI) 驗證語法？
- [ ] **Agent Definition**: 是否明確指定了 Agent？(避免使用 `agent any` 除非是簡單專案)。
- [ ] **Options**: 是否設定了 `timeout` 與 `buildDiscarder` (避免硬碟塞滿)？

### Logic & Flow (邏輯與流程)
- [ ] **Conditionals**: 是否使用 `when` 取代了 `script { if (...) }`？
- [ ] **Parallelism**: 是否有機會並行執行測試以縮短時間？
- [ ] **Secrets**: 確認沒有明文密碼，且使用了 `environment { MY_CREDS = credentials('...') }`。

### Feedback & Cleanup (回饋與清理)
- [ ] **Post Actions**: 是否設定了 `post { failure { ... } }` 發送通知 (Slack/Email)？
- [ ] **Artifacts**: 是否使用 `archiveArtifacts` 保存產出物？
- [ ] **Test Reports**: 是否使用 `junit` 或 `publishHTML` 收集報告？

---

## Real-world examples｜實戰案例

### Scenario: The Standard Containerized CI/CD Pipeline
這是一個典型的微服務 Pipeline：使用 Docker 作為建置環境、並行測試、條件式部署，以及完善的錯誤處理。

```groovy
pipeline {
    agent none // Don't allocate a node yet
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds() // Prevent race conditions
    }

    environment {
        // Global variables
        APP_NAME = "my-service"
        REGISTRY = "docker.io/myorg"
        CI_CREDENTIALS = credentials('ci-user-creds') 
    }

    stages {
        stage('Setup & Checkout') {
            agent any
            steps {
                checkout scm
                echo "Building branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & Test') {
            // Use a specific Docker image for building
            agent {
                docker { 
                    image 'maven:3.8-openjdk-11' 
                    args '-v /root/.m2:/root/.m2' // Cache maven dependencies
                }
            }
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Quality Checks') {
            agent { docker { image 'maven:3.8-openjdk-11' } }
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'mvn test'
                    }
                }
                stage('Static Analysis') {
                    steps {
                        sh 'mvn sonar:sonar' // Example
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                // Only build image on main branch or tags
                anyOf {
                    branch 'main'
                    tag pattern: "v*", comparator: "GLOB"
                }
            }
            agent any
            steps {
                script {
                    // Using script block only when strictly necessary (e.g., dynamic variable assignment)
                    def imageTag = env.TAG_NAME ?: env.BUILD_NUMBER
                    sh "docker build -t ${REGISTRY}/${APP_NAME}:${imageTag} ."
                    
                    withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh "docker login -u $USER -p $PASS"
                        sh "docker push ${REGISTRY}/${APP_NAME}:${imageTag}"
                    }
                }
            }
        }
    }

    post {
        always {
            // Always collect test results
            junit '**/target/surefire-reports/*.xml'
            cleanWs() // Clean workspace to save disk space
        }
        success {
            echo "Pipeline succeeded! Artifacts are ready."
            // slackSend channel: '#ci-cd', color: 'good', message: "Build ${env.BUILD_NUMBER} Passed"
        }
        failure {
            echo "Pipeline failed. Please check logs."
            // slackSend channel: '#ci-cd', color: 'danger', message: "Build ${env.BUILD_NUMBER} Failed"
        }
    }
}
```