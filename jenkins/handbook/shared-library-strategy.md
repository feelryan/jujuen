# Shared Libraries 模組化設計策略 / Modular Design with Shared Libraries

## Mental model｜心智模型

### 1. 內部開發者平台 (Internal Developer Platform) 的 SDK
不要將 Shared Library 僅視為「存放共用 Script 的地方」。請將其視為你為公司內部開發團隊提供的 **CI/CD SDK (Software Development Kit)**。
- **Jenkinsfile 是「使用者介面 (UI)」**：開發者只需宣告「做什麼 (What)」（例如：`buildJavaApp()`）。
- **Shared Library 是「實作細節 (How)」**：你封裝了底層的複雜度（Maven 參數、Docker 構建指令、K8s 部署 YAML）。

### 2. 層次化架構 (Layered Architecture)
在設計 Library 時，應區分「膠水層」與「邏輯層」：
- **`vars/` (Global Variables)**：這是 API 層。這裡的 Groovy script (`.groovy`) 透過 `call()` 方法暴露給 Jenkinsfile 使用。它們應該處理流程控制、參數驗證，並呼叫底層邏輯。
- **`src/` (Source Class)**：這是核心邏輯層。使用標準 Groovy Class (`package com.company...`) 撰寫純粹的商業邏輯或工具函式。這裡的程式碼應該盡量與 Jenkins Pipeline 語法解耦，以便於單元測試。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Wrapper Pattern (包裝器模式)
最常見的模式是在 `vars/` 中定義一個高階步驟，將整個 Pipeline 的標準流程（Checkout -> Build -> Test -> Scan -> Deploy）封裝起來。

*   **Why:** 強制執行標準化流程，開發者只需提供極少的配置。
*   **How:**
    ```groovy
    // vars/standardServicePipeline.groovy
    def call(Map config = [:]) {
        pipeline {
            agent any
            stages {
                stage('Build') {
                    steps {
                        script {
                            // 呼叫 src/ 中的邏輯
                            new com.company.BuildUtils().runMaven(config)
                        }
                    }
                }
                // ... 其他標準 Stage
            }
        }
    }
    ```

### 2. Configuration as Map (Map 作為配置物件)
避免在 `call()` 方法中使用過多獨立參數（如 `call(String name, boolean isProd, int retries...)`）。始終使用一個 `Map` 來傳遞參數。

*   **Why:** 提高可讀性，且新增參數時不會破壞現有的 API (Backward Compatibility)。
*   **How:**
    ```groovy
    // Jenkinsfile
    deployApp(env: 'prod', version: '1.2.0', skipTests: true)

    // vars/deployApp.groovy
    def call(Map config) {
        // 設定預設值
        boolean skipTests = config.get('skipTests', false)
        // ...
    }
    ```

### 3. Resource Loading (資源加載)
將非程式碼的資源（如 Kubernetes YAML 模板、Dockerfile 模板、Email HTML 模板）放在 `resources/` 目錄下，並使用 `libraryResource` 讀取。

*   **Why:** 避免將長字串硬寫在 Groovy code 裡，實現邏輯與視圖/配置的分離。
*   **How:** `def yamlTemplate = libraryResource 'k8s/deployment.yaml'`

### 4. Explicit Versioning (明確的版本控制)
永遠不要在生產環境的 Pipeline 中依賴 Shared Library 的 `master` 分支。

*   **Why:** `master` 的變更會立即影響所有 Pipeline，一次錯誤的 commit 可能導致全公司 CI/CD 癱瘓。
*   **Best Practice:** 使用 Git Tag（如 `v1.2`）或穩定的 Branch 指向 Shared Library。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Step" (上帝步驟)
*   **Bad:** 創造一個名為 `common.groovy` 的檔案，裡面塞滿了幾千行互不相關的 helper methods。
*   **Consequence:** 難以維護、難以閱讀、難以測試。
*   **Fix:** 根據功能拆分檔案，例如 `dockerUtils.groovy`, `gitUtils.groovy`, `slackNotifier.groovy`。

### 2. Non-Serializable Code (不可序列化程式碼)
*   **The Trap:** Jenkins Pipeline 使用 CPS (Continuation Passing Style) 來支援暫停與恢復。所有在 Pipeline 執行期間存在的變數都必須實作 `Serializable` 介面。
*   **Symptom:** `java.io.NotSerializableException`。
*   **Fix:**
    *   在 `src/` 中的 Class 必須 `implements Serializable`。
    *   如果使用了不可序列化的第三方物件（如 `java.util.regex.Matcher`），請在 `@NonCPS` 標註的方法中使用，或確保該變數在方法結束前就被銷毀，不要存入全域變數。

### 3. Direct Logic in Jenkinsfile (邏輯洩漏)
*   **Bad:** 在 Jenkinsfile 中寫大量的 `script { ... }` 區塊包含複雜的 if-else 邏輯。
*   **Consequence:** 違反 DRY 原則，邏輯無法被其他專案重用。
*   **Fix:** 一旦發現一段邏輯被複製貼上超過兩次，立即將其重構進 Shared Library。

### 4. Ignoring Unit Tests (忽略單元測試)
*   **Bad:** 透過「修改 -> Commit -> 觸發 Jenkins -> 失敗 -> 重來」的循環來開發 Library。
*   **Consequence:** 開發效率極低，且容易引入 Regression。
*   **Fix:** 使用 **Jenkins Pipeline Unit** 框架在本地撰寫 Groovy 單元測試。

---

## Checklists & workflows｜檢查清單與流程

### Development Workflow (開發流程)
1.  **Local Dev**: 在本地 IDE (IntelliJ IDEA + Groovy plugin) 開發。
2.  **Unit Test**: 執行 `mvn test` 或 `gradle test` (使用 Jenkins Pipeline Unit) 驗證邏輯。
3.  **Branching**: 推送至 feature branch (例如 `feature/new-docker-logic`)。
4.  **Integration Test**: 建立一個專門的 "Test Pipeline" Job，將 Library 指向該 feature branch 進行真實環境測試。
5.  **Release**: Merge 回 master，並打上 Git Tag (例如 `v2.1.0`)。

### Code Review Checklist (代碼審查清單)
- [ ] **API 設計**: `call` 方法是否接受 `Map`？參數是否有合理的預設值？
- [ ] **CPS 相容性**: 是否引入了不可序列化的物件？是否正確使用了 `@NonCPS`？
- [ ] **依賴管理**: 是否依賴了特定的 Jenkins Plugin？如果是，是否已在文件中註明？
- [ ] **錯誤處理**: 當指令執行失敗時（如 shell exit code != 0），是否有 `try-catch` 或明確的報錯訊息？
- [ ] **資源釋放**: 是否有使用 `wrap([$class: 'AnsiColorBuildWrapper'])` 或類似的 block 結構，確保資源正確關閉？
- [ ] **日誌記錄**: 關鍵步驟是否有 `echo` 或 `log.info` 輸出，方便除錯？

---

## Real-world examples｜實戰案例

### 案例：標準化微服務構建 (Standard Microservice Build)

我們希望所有 Java 微服務都遵循：Checkout -> Unit Test -> SonarQube -> Build Docker -> Push Registry。

#### 1. 目錄結構 (Directory Structure)
```text
(root)
+- src/
|   +- com/
|       +- mycorp/
|           +- DockerUtils.groovy  (負責 Docker 指令封裝)
+- vars/
|   +- buildJavaService.groovy     (對外暴露的 Step)
+- resources/
|   +- sonar-project.properties    (Sonar 設定模板)
```

#### 2. 實作 API (`vars/buildJavaService.groovy`)
```groovy
// vars/buildJavaService.groovy
import com.mycorp.DockerUtils

def call(Map config = [:]) {
    // 參數預設值處理
    String imageName = config.get('imageName', "my-app")
    boolean runSonar = config.get('runSonar', true)
    
    pipeline {
        agent any
        stages {
            stage('Checkout') {
                steps { checkout scm }
            }
            stage('Test') {
                steps { sh './mvnw test' }
            }
            stage('Quality Gate') {
                when { expression { return runSonar } }
                steps {
                    // 載入資源檔
                    writeFile file: 'sonar-project.properties', 
                              text: libraryResource('sonar-project.properties')
                    sh './mvnw sonar:sonar'
                }
            }
            stage('Docker Build') {
                steps {
                    script {
                        // 使用 src/ 中的 Class 處理複雜邏輯
                        def docker = new DockerUtils(this)
                        docker.buildAndPush(imageName, env.BUILD_NUMBER)
                    }
                }
            }
        }
    }
}
```

#### 3. 使用者呼叫 (`Jenkinsfile`)
開發者只需要寫極少的程式碼：

```groovy
@Library('my-shared-lib@v2.0') _

buildJavaService(
    imageName: 'payment-service',
    runSonar: true
)
```

### 案例：決策樹 (Decision Tree for Logic Placement)

當你在寫 Code 時，該放在哪裡？

1.  **這是單個專案特有的邏輯嗎？**
    *   Yes -> 寫在該專案的 `Jenkinsfile` 裡。
    *   No -> 繼續。
2.  **這是一個完整的 Pipeline 流程 (End-to-End) 嗎？**
    *   Yes -> 寫在 `vars/myStandardPipeline.groovy` (Wrapper Pattern)。
    *   No -> 繼續。
3.  **這是一個簡單的工具指令 (如發送 Slack) 嗎？**
    *   Yes -> 寫在 `vars/sendSlack.groovy`。
    *   No -> 繼續。
4.  **這是否涉及複雜的資料處理、運算或物件導向設計？**
    *   Yes -> 寫在 `src/com/company/MyLogic.groovy`，並在 `vars/` 中呼叫它。