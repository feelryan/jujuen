# 建置效能優化與維運管理 / Build Performance Optimization and Maintenance

## Mental model｜心智模型

要掌握 Jenkins 的效能優化，必須建立正確的 **「指揮官與工廠 (Orchestrator vs. Factory)」** 心智模型。

1.  **Master (Controller) 是大腦，不是肌肉**：
    Jenkins Master (Controller) 的職責是調度 (Scheduling)、監控狀態與儲存結果。它不應該消耗 CPU 去編譯程式碼或執行測試。如果 Master 變慢，整個 CI/CD 流程都會癱瘓。
    *   *The Master is the brain, not the muscle. It schedules and monitors. It should never burn CPU cycles compiling code.*

2.  **Pipeline 是流動的，Workspace 是暫時的**：
    每一次的建置 (Build) 應該視為一次獨立的「交易」。Workspace 是為了該次交易而存在的暫存區，交易結束後應視為「有毒廢棄物」或「可拋棄資源」，不應長期囤積。
    *   *Workspaces are ephemeral. Treat them as disposable scratchpads that should be wiped clean after use to prevent disk bloat and side effects.*

3.  **I/O 是最大的瓶頸**：
    Jenkins 的效能問題有 70% 來自磁碟 I/O (Disk I/O) 與網路延遲，而非 CPU。過多的 Log 寫入、巨大的 Artifacts 傳輸、以及未清理的 Workspace 是主要殺手。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. JVM 與 Master 優化 (JVM Tuning & Master Optimization)

Jenkins 是 Java 應用程式，正確的 JVM 設定至關重要。

*   **使用 G1GC**：對於現代 Jenkins 實例（Heap > 4GB），G1GC (Garbage First Garbage Collector) 通常比 ParallelGC 表現更好，能減少長時間的 "Stop-the-world" 停頓。
    *   *Use G1GC for heaps larger than 4GB to minimize pause times.*
*   **Heap Size 設定**：設定 `-Xms` 與 `-Xmx` 為相同數值（例如 `-Xms4g -Xmx4g`），避免 JVM 在執行期間動態調整記憶體大小造成的效能損耗。
*   **停用 Master 建置**：將 Master 節點的 Executors 設為 0。強制所有 Job 都在 Agent 上執行。
    *   *Set executors to 0 on the Master node to force all builds to run on agents.*

### 2. 並行執行與管線優化 (Parallel Execution & Pipeline Efficiency)

利用 Declarative Pipeline 的語法特性來縮短回饋迴圈 (Feedback Loop)。

*   **Parallel Stages**：將互不依賴的步驟（如 Unit Test, Linting, Security Scan）並行處理。
    ```groovy
    stage('Checks') {
        parallel {
            stage('Unit Test') { steps { sh 'mvn test' } }
            stage('Lint') { steps { sh 'npm run lint' } }
        }
    }
    ```
*   **Fail Fast**：在 `parallel` 區塊中使用 `failFast true`，一旦其中一個分支失敗，立即中止其他分支，節省資源。

### 3. 建置歷史與磁碟管理 (Build Rotation & Disk Management)

Jenkins 預設會永久保存所有建置紀錄，這是導致磁碟爆滿的主因。

*   **Build Discarder (Log Rotator)**：在所有 Job 或全域設定中，強制設定「保留策略」。
    *   *Pattern*: 只保留最近 10-20 次建置，或保留 7 天內的紀錄。
    *   *Code*:
        ```groovy
        options {
            buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
        }
        ```
*   **Workspace Cleanup**：在 Pipeline 結束後（Post actions）自動清理 Workspace。這不僅節省空間，還能避免下一次 Build 受到舊檔案污染。
    *   *Use the `cleanWs()` step in the `post { always { ... } }` block.*

### 4. Artifacts 管理策略

*   **不要把 Jenkins 當作儲存庫**：Jenkins 的 `archiveArtifacts` 僅用於「短期」除錯或傳遞。長期的 Binary (jar, war, docker image) 應上傳至 Nexus, Artifactory 或 S3。
*   **Stash vs Archive**：
    *   `stash/unstash`：用於在 **同一個 Pipeline 的不同 Stage/Agent 之間** 傳遞小檔案。
    *   `archiveArtifacts`：用於讓使用者在 UI 下載，或供下游 Job 使用。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fat Master" (肥大的 Master)
*   **Bad Practice**: 在 Master 節點上安裝 Maven, Docker, Node.js 並直接執行建置。
*   **Consequence**: 建置過程的高 I/O 會導致 Jenkins UI 卡頓，甚至造成 Master Crash，影響所有團隊。
*   **Correction**: 使用 Agent 或 Container Agent。

### 2. The "Database" Jenkins (把 Jenkins 當資料庫)
*   **Bad Practice**: 保留數千個歷史建置紀錄，或者 `archive` 數 GB 的檔案。
*   **Consequence**: Jenkins 啟動變慢（因為要載入大量 XML metadata），備份困難，磁碟空間迅速耗盡。
*   **Correction**: 設定積極的 `buildDiscarder` 策略。

### 3. Heavy Groovy Logic (過重的 Groovy 邏輯)
*   **Bad Practice**: 在 `Jenkinsfile` 中撰寫複雜的 Groovy 運算（如複雜的迴圈、字串解析、HTTP 請求）。
*   **Consequence**: Jenkins Pipeline 依賴 CPS (Continuation Passing Style) 轉換，複雜的 Groovy 程式碼會消耗大量 Master CPU 且執行緩慢。
*   **Correction**: 將複雜邏輯封裝到 Shell Script (`.sh`) 或 Python Script 中，Pipeline 僅負責呼叫。
    *   *Offload complex logic to shell scripts or external tools. Keep the pipeline script simple.*

### 4. Sleeping Wait (睡眠等待)
*   **Bad Practice**: 使用 `sleep 60` 等待某個服務啟動。
*   **Consequence**: 浪費 Executor Slot 資源。
*   **Correction**: 使用 `timeout` 搭配 `waitUntil` 或健康檢查端點 (Health Check Endpoint) 進行主動偵測。

---

## Checklists & workflows｜檢查清單與流程

### 🚀 Performance Tuning Checklist (維運端)

- [ ] **JVM Settings**: 確認已設定 `-Xms` = `-Xmx`，且已啟用 G1GC (若 Heap > 4GB)。
- [ ] **Master Executors**: 確認 Master 節點的 Executor 數量為 0。
- [ ] **Disk Monitoring**: 設定磁碟空間監控與警報（建議剩餘空間 < 20% 發送警報）。
- [ ] **Plugin Audit**: 移除未使用的 Plugin（Plugin 越多，Master 記憶體負擔越重）。
- [ ] **Global Build Discarder**: (若有安裝相關 Plugin) 設定全域預設的建置保留策略，防止個別專案忘記設定。

### 🛠 Pipeline Optimization Checklist (開發端)

- [ ] **Build Rotation**: `Jenkinsfile` 中是否包含 `buildDiscarder`？
- [ ] **Cleanup**: 是否在 `post { always { ... } }` 中執行 `cleanWs()`？
- [ ] **Parallelism**: 是否將可並行的測試或掃描放入 `parallel` 區塊？
- [ ] **Timeout**: 是否為每個 Stage 設定合理的 `timeout`，避免卡死的 Process 佔用資源？
- [ ] **Offloading**: 複雜邏輯是否已移至 Shell/Python script？

---

## Real-world examples｜實戰案例

### Example 1: 高效能的 Pipeline 範本 (Optimized Pipeline Template)

這是一個整合了清理、逾時設定、並行執行與建置保留的最佳實務範本。

```groovy
pipeline {
    agent { label 'linux-docker-node' } // 使用專用 Agent

    // 1. 維運策略：保留最近 10 次建置，且設定全域逾時防止卡死
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
        timeout(time: 1, unit: 'HOURS') 
        disableConcurrentBuilds() // 避免同一個 Branch 同時搶資源
        timestamps() // Log 加上時間戳記以便除錯效能
    }

    stages {
        stage('Build & Check') {
            // 2. 效能策略：並行執行互不干擾的任務
            parallel {
                stage('Compile') {
                    steps {
                        sh './mvnw clean package -DskipTests'
                    }
                }
                stage('Static Analysis') {
                    steps {
                        sh './mvnw sonar:sonar'
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                // 3. 避免在 Pipeline 寫複雜 Groovy，直接呼叫 Script
                sh './scripts/run_tests.sh'
            }
        }
    }

    post {
        // 4. 清理策略：無論成功失敗，都要清理 Workspace
        always {
            cleanWs()
        }
        success {
            archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
        }
    }
}
```

### Example 2: 解決 "Jenkins UI 卡頓" 的除錯流程

**情境**：開發者抱怨 Jenkins 網頁開啟很慢，且 Job 經常在 "Waiting for executor" 狀態卡很久，但 Agent 其實很閒。

**診斷步驟**：
1.  **檢查 Master 負載**：發現 Master CPU 飆高。
2.  **查看 Thread Dump**：發現大量 Thread 卡在 `CpsGroovyShell`。
3.  **定位問題 Job**：發現某個 Shared Library 在 Pipeline 中使用了巢狀的 `for` 迴圈處理數萬行的 Log 字串解析。
4.  **解決方案**：
    *   將字串解析邏輯改寫為 Python script (`parse_log.py`)。
    *   Pipeline 改為 `sh 'python3 parse_log.py'`。
    *   **結果**：Master CPU 降回正常水平，UI 恢復流暢。