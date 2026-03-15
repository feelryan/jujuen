# 常見反模式與陷阱 (Anti-Patterns) / Common Anti-Patterns and Pitfalls

## Mental model｜心智模型

要避免 Jenkins 的反模式，首先要建立正確的角色定位。請將 Jenkins 視為 **「指揮家 (Conductor)」** 或 **「調度員 (Dispatcher)」**，而不是 **「苦力 (Worker)」**。

### The "Thin Controller" Philosophy
Jenkins Controller (舊稱 Master) 的核心職責是：
1.  **排程 (Scheduling)**：決定何時執行任務。
2.  **分派 (Dispatching)**：決定由誰（哪個 Agent）執行任務。
3.  **監控 (Monitoring)**：收集執行結果與 Logs。

**它不應該負責：** 編譯程式碼、執行測試、打包 Docker Image 或處理繁重的 I/O 操作。

當你將 Jenkins 視為一個「執行指令的 Shell」而非「流程編排器」時，就會陷入反模式。正確的心智模型應該是：**Pipeline 負責定義「做什麼 (What)」，而具體的實作細節 (How) 應盡量下放給 Agent 環境或外部腳本。**

---

## Patterns & best practices｜常見模式與最佳實務

在討論錯誤之前，我們先確立什麼是「健康」的 Jenkins 實作模式：

### 1. Distributed Builds (Master-Agent Architecture)
- **Pattern**: Controller 的 Executors 數量設為 0。
- **Why**: 確保 Controller 的 CPU/RAM 僅用於協調，不會因為某個 Build 跑 Java Compilation 導致整個 Jenkins UI 卡死或 Crash。

### 2. Logic in Scripts, Not Pipeline
- **Pattern**: `Jenkinsfile` 應該只包含 `sh './build.sh'` 或 `sh 'make test'`，而不是大量的 Groovy 邏輯。
- **Why**: Shell/Python/Make 可以在本地開發環境測試，但 Groovy Pipeline 很難在本地除錯。將邏輯封裝在腳本中，Jenkins 只是呼叫者。

### 3. Ephemeral Agents (Containerized Agents)
- **Pattern**: 使用 Docker 或 Kubernetes Agents，每次 Build 都啟動一個全新的容器，結束後銷毀。
- **Why**: 避免 "Works on my machine" (或 "Works on Agent-1 but fails on Agent-2") 的問題，並解決 Workspace 殘留垃圾導致的磁碟空間不足。

### 4. Configuration as Code (CasC)
- **Pattern**: 所有的 Job 設定來自 `Jenkinsfile` (Pipeline as Code)，所有的系統設定來自 `JCasC` (YAML)。
- **Why**: 避免 UI 手動設定造成的 "Snowflake Server"（無法複製、無法災難復原的伺服器）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是真實世界中最常見的災難性做法，請務必識別並重構。

### 1. The "Heavy Master" (在 Controller 上執行構建)
- **Anti-Pattern**: 直接在 Jenkins Controller 上安裝 Maven, Node.js, Docker，並讓 Build 在 Controller 上執行。
- **Consequences**:
    - **Security Risk**: Build script 可以讀取 Controller 上的所有 Credentials 和系統檔案。
    - **Performance**: 單一 Build 耗盡記憶體會導致整個 Jenkins 重啟，影響所有團隊。
- **Refactoring**: 將 Master 的 Executors 設為 0，強制所有 Job 使用 Agent。

### 2. ClickOps (依賴 UI 設定 Job)
- **Anti-Pattern**: 在 Jenkins UI 點擊 "New Item" -> "Freestyle Project"，並在網頁輸入框中寫 Shell Script。
- **Consequences**:
    - 無法版控 (No Version Control)。
    - 難以 Code Review。
    - 一旦 Jenkins 掛掉，無法快速復原 Job 設定。
- **Refactoring**: 遷移至 Pipeline (`Jenkinsfile`)。如果必須用 UI，請使用 Job DSL Plugin 來生成 Job。

### 3. Abuse of Groovy (濫用 Groovy 腳本)
- **Anti-Pattern**: 在 `Jenkinsfile` 中寫複雜的 `if/else`、迴圈、或是字串解析邏輯。
- **Consequences**:
    - **NonSerializableException**: Jenkins Pipeline 依賴 CPS (Continuation Passing Style) 來支援暫停/恢復。複雜的 Groovy 物件往往無法序列化，導致莫名其妙的錯誤。
    - **Vendor Lock-in**: 你的 Build 邏輯被綁死在 Jenkins 語法上，無法輕易遷移到 GitLab CI 或 GitHub Actions。
- **Refactoring**: 把邏輯移到專案內的 `scripts/` 目錄（如 Python 或 Bash），Pipeline 只負責呼叫。

### 4. Plugin Hoarding (插件囤積症)
- **Anti-Pattern**: 為了解決一個小問題就安裝一個 Plugin（例如：為了讀取 JSON 安裝一個插件，為了發 Slack 又裝一個）。
- **Consequences**:
    - **Dependency Hell**: 插件之間版本衝突。
    - **Security Holes**: 許多冷門插件多年未維護，充滿漏洞。
    - **Slow Startup**: Jenkins 啟動時間隨插件數量指數增長。
- **Refactoring**: 優先使用 Shell Script + Docker Image 解決問題（例如用 `jq` 處理 JSON，用 `curl` 發送通知），而非依賴插件。

### 5. Shared Library Over-engineering (過度設計的共用庫)
- **Anti-Pattern**: 建立一個龐大的 Shared Library，試圖把所有公司的 Build 邏輯抽象化成一行 `buildEverything()`。
- **Consequences**: 變成 "Black Box"，開發者不知道底層發生了什麼，且 Shared Library 的變更會瞬間影響所有專案（Blast Radius 太大）。
- **Refactoring**: Shared Library 應提供「工具」而非「魔法」。保持 Library 輕量化。

---

## Checklists & workflows｜檢查清單與流程

在進行 Jenkins 維護或 Code Review 時，請使用此清單：

### Architecture Health Check
- [ ] **Controller Isolation**: Master node 的 executors 是否設定為 `0`？
- [ ] **Agent Usage**: 是否所有 Job 都明確指定了 `agent { label '...' }` 或 `agent { docker ... }`？
- [ ] **Disk Space**: 是否設定了 Log Rotation 和 Workspace Cleanup 策略？

### Pipeline Code Review (Jenkinsfile)
- [ ] **No Complex Logic**: 是否有超過 10 行的 Groovy 邏輯區塊？（若有，請要求移至 Shell Script）。
- [ ] **Secrets Management**: 是否使用了 `withCredentials` 或 `credentials()` helper？（嚴禁將密碼硬編碼或直接 `echo` 環境變數）。
- [ ] **Timeout**: 每個 `stage` 或整個 `pipeline` 是否設定了 `timeout`？（防止僵屍行程卡住 Executor）。
- [ ] **Clean Workspace**: Pipeline 結束後（`post { always { ... } }`）是否執行了 `cleanWs()`？

### Security & Maintenance
- [ ] **Plugin Audit**: 過去 3 個月內是否檢查過 "Plugin Manager" 的警告與更新？
- [ ] **Backup**: 是否有自動化備份 `$JENKINS_HOME`（排除 `workspace` 與 `builds`）的機制？

---

## Real-world examples｜實戰案例

### Case 1: The "NonSerializableException" Trap
**情境**: 開發者試圖在 Pipeline 中解析 API 回傳的 JSON。

**❌ Anti-Pattern (Groovy in Pipeline):**
```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Check Status') {
            steps {
                script {
                    def response = new URL("http://api.example.com/status").getText()
                    def json = new groovy.json.JsonSlurper().parseText(response) // 這裡容易觸發序列化錯誤
                    if (json.status == 'FAIL') {
                        error "System is down"
                    }
                }
            }
        }
    }
}
```
*問題：`JsonSlurper` 產生的物件在 Pipeline CPS 轉換過程中經常導致序列化失敗，且邏輯難以在本地測試。*

**✅ Best Practice (Shell + jq):**
```groovy
// Jenkinsfile
pipeline {
    agent { docker { image 'alpine:latest' } } // 確保有 curl 和 jq
    stages {
        stage('Check Status') {
            steps {
                sh '''
                    apk add --no-cache curl jq
                    STATUS=$(curl -s http://api.example.com/status | jq -r '.status')
                    if [ "$STATUS" == "FAIL" ]; then
                        echo "System is down"
                        exit 1
                    fi
                '''
            }
        }
    }
}
```
*優點：使用標準 Linux 工具，穩定、可移植、不會炸掉 Jenkins 的記憶體。*

---

### Case 2: The "Works on My Machine" Build
**情境**: 專案依賴特定版本的 Node.js (v14)，但 Agent 上安裝的是 v16。

**❌ Anti-Pattern (Global Tool Configuration):**
依賴 Jenkins 管理員手動在 Agent 上安裝 Node.js v14，並在 Global Tool Configuration 設定路徑。
*後果：當需要升級到 v18 時，需要運維人員逐台 Agent 更新，且不同專案會打架。*

**✅ Best Practice (Docker Agent):**
```groovy
// Jenkinsfile
pipeline {
    agent {
        docker { 
            image 'node:14-alpine' 
            args '-u root'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'npm install && npm run build'
            }
        }
    }
}
```
*優點：環境跟隨程式碼 (Configuration as Code)。專案 A 用 Node 14，專案 B 用 Node 18，互不干擾，且不需要管理員介入。*