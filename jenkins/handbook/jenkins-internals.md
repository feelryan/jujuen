# 核心架構與運作機制：Master 與 Agent / Core Architecture: Master, Agents, and Remoting

## Mental model｜心智模型

要駕馭 Jenkins，首先必須摒棄「單機軟體」的思維，轉而建立分散式的「指揮官與工兵」模型。

To master Jenkins, you must abandon the "standalone software" mindset and adopt a distributed "Commander and Worker" model.

### 1. Brain vs. Muscle (大腦與肌肉)
- **Jenkins Controller (Master)**：這是大腦。它負責調度 (Scheduling)、監控 (Monitoring)、權限管理 (Security)、以及儲存組態 (Configuration)。它**不應該**負責搬運重物（編譯程式碼、執行測試）。
- **Jenkins Agents (Nodes)**：這是肌肉。它們是實際執行 `sh`, `bat`, `docker run` 的地方。Agent 應該是可拋棄的 (Disposable) 且專注於單一任務。

### 2. The Remoting Channel (通訊管道)
Master 與 Agent 之間的連線不僅僅是 TCP Socket，它是一條 **Remoting Channel**。
- 這條管道不僅傳送指令，還傳送 ClassLoader 請求、檔案串流 (File streams) 和環境變數。
- **關鍵認知**：這條管道很脆弱且頻寬有限。如果你的 Build 過程產生大量 Log 或在 Master/Agent 間傳輸巨大 Artifacts，這條管道會阻塞，導致 Master 無回應 (Unresponsive)。

### 3. Executors (執行緒插槽)
Executor 不是機器，而是機器上的「併發插槽 (Concurrency Slots)」。
- 一個 Agent 有 4 個 Executors，代表它能同時跑 4 個 Job。
- **Mental Shift**：不要以「這台機器有多強」來設定 Executor 數量，而應以「這台機器的 I/O 和記憶體能支撐幾個並行任務」來設定。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "No Executors on Master" Rule (Master 零執行緒原則)
這是最重要的一條規則。
- **做法**：將 Master 節點的 `# of executors` 設定為 `0`。
- **原因**：防止 User 的 Build Script 意外消耗 Master 的 CPU/RAM，或透過 Build 存取 Master 的檔案系統（造成安全漏洞）。
- **例外**：僅保留極少量（如 1 個）Executor 專門用於輕量級的備份任務或驗證，並透過 Label 嚴格限制存取。

### 2. Label-Based Routing (基於標籤的路由)
不要在 Pipeline 中寫死 Agent 的名稱。
- **Pattern**：給 Agent 貼上功能性標籤，如 `linux`, `docker`, `high-mem`, `gpu-enabled`。
- **Code**：
  ```groovy
  // Good
  agent { label 'linux && java17' }
  
  // Bad
  agent { label 'slave-node-01' }
  ```
- **Benefit**：這讓你可以隨時更換底層機器而不必修改 Jenkinsfile。

### 3. Connection Protocols: SSH vs. JNLP
- **Linux/Unix Agents**：優先使用 **SSH (Launch agents via SSH)**。這是由 Master 主動連線，管理最方便，不需要在 Agent 上安裝額外的 Java Web Start 服務。
- **Windows Agents / Behind NAT**：使用 **Inbound TCP Agent (JNLP)**。這是由 Agent 主動連回 Master。建議搭配將 Agent 安裝為 Windows Service 以確保重開機後自動連線。

### 4. "Exclusive" Usage Mode (專用模式)
- **設定**：將 Agent 的 Usage 設定為 *"Only build jobs with label expressions matching this node"*。
- **目的**：防止 Jenkins 隨意將不相關的 Job 塞到這台特殊的機器上（例如，不要讓普通的 Unit Test 佔用昂貴的 Mac Build 機器）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Heavy Logic in Master Groovy (在 Master 執行過重邏輯)
- **Pitfall**：在 Pipeline 的 `script {}` 區塊中寫複雜的 Groovy 運算（如解析超大 JSON、遍歷大量檔案）。
- **Consequence**：這些 Groovy 程式碼是在 **Master 的 JVM** 上執行的，而非 Agent。這會導致 Master CPU 飆高，卡住 UI 和調度。
- **Fix**：將邏輯移入 Shell script 或 Python script，讓 Agent 去執行。

### 2. Stashing/Unstashing Large Files (傳輸大檔案)
- **Pitfall**：使用 `stash` 和 `unstash` 在不同 Stage 之間傳遞幾百 MB 的編譯產物。
- **Consequence**：`stash` 會將檔案透過 Remoting Channel 傳回 Master 儲存，再傳給下一個 Agent。這會塞爆 Master 的網路與儲存。
- **Fix**：使用外部儲存（S3, Artifactory, Nexus）或 Shared Workspace（如果是在同一台機器）。

### 3. Ignoring Clock Synchronization (忽略時鐘同步)
- **Pitfall**：Master 與 Agent 的系統時間不一致。
- **Consequence**：導致 SCM Checkout 失敗、Build 紀錄時間錯亂，甚至造成 Remoting 協定錯誤。
- **Fix**：所有節點必須啟用 NTP 自動校時。

### 4. The "Fat" Static Agent (巨型靜態 Agent)
- **Pitfall**：維護幾台裝滿所有工具（Java, Node, Python, Go, Ruby...）的「巨無霸」Agent。
- **Consequence**：工具版本衝突地獄 (Dependency Hell)，且難以複製環境。
- **Fix**：轉向 **Containerized Agents** (Docker/K8s)，讓環境隨 Code 定義。

---

## Checklists & workflows｜檢查清單與流程

### New Agent Setup Checklist (新增節點檢查清單)

- [ ] **Security**: Is the connection encrypted? (SSH keys setup correctly?)
  - **安全性**：連線是否加密？（SSH Key 是否配置正確？）
- [ ] **Isolation**: Is the workspace root separated from system paths?
  - **隔離性**：Workspace 根目錄是否與系統路徑分開？（建議 `/var/jenkins/workspace`）
- [ ] **Tools**: Are Git and Java (JRE) installed and in the `$PATH`?
  - **工具**：Git 與 Java (JRE) 是否已安裝且在環境變數中？
- [ ] **Limits**: Have you set reasonable disk space thresholds for automatic cleanup?
  - **限制**：是否設定了合理的磁碟空間閾值以觸發自動清理？
- [ ] **Labels**: Are functional labels applied? (e.g., `frontend`, `backend`)
  - **標籤**：是否已套用功能性標籤？
- [ ] **Executors**: Is the executor count matching CPU cores (or slightly less)?
  - **執行緒**：Executor 數量是否匹配 CPU 核心數（或略少）？

### Troubleshooting "Agent Offline" Workflow (Agent 離線排查流程)

1.  **Check Disk Space**: Agent 磁碟滿了嗎？這是最常見原因（Jenkins 會主動斷開磁碟不足的節點）。
2.  **Check Java Process**: Agent 上的 `java -jar agent.jar` 還在跑嗎？
3.  **Check Network**: Master 能 `ping` 或 `ssh` 到 Agent 嗎？防火牆規則有變動嗎？
4.  **Check Logs**: 查看 Master 上的 System Log (`Manage Jenkins -> System Log -> All Jenkins Logs`)，搜尋該節點名稱的錯誤訊息。
5.  **Check Version**: Master 升級後，Agent 的 `agent.jar` 是否版本過舊？（通常會自動更新，但有時會失敗）。

---

## Real-world examples｜實戰案例

### Scenario: The Hybrid Build Farm (混合式建置農場)

一間公司同時開發 iOS App 與 Backend API。

**Infrastructure Design:**

1.  **Master (Controller)**:
    - 部署在 Linux VM 上。
    - `# of Executors`: **0**.
    - 職責：只負責 Webhook 接收、Pipeline 調度、LDAP 認證。

2.  **Agent Group A (Linux / Docker)**:
    - 3 台 Linux VM，安裝 Docker。
    - Labels: `docker`, `linux`.
    - Usage: Exclusive.
    - 任務：執行 Backend Java/Go 建置，跑 Docker 化的 Unit Tests。

3.  **Agent Group B (Mac mini)**:
    - 2 台 Mac mini，實體機。
    - Labels: `ios`, `xcode`, `mac`.
    - Usage: Exclusive.
    - 連線方式：SSH (Master -> Mac)。
    - 任務：專門跑 Xcode Build 與 Signing。

**Pipeline Implementation (Jenkinsfile):**

```groovy
pipeline {
    agent none // Do not allocate a node by default

    stages {
        stage('Backend Build') {
            agent { label 'docker && linux' } // Routes to Group A
            steps {
                sh 'mvn clean package'
            }
        }

        stage('iOS Build') {
            agent { label 'ios && xcode' } // Routes to Group B
            when { branch 'master' }
            steps {
                sh 'xcodebuild ...'
            }
        }
        
        stage('Deploy Approval') {
            agent none // No executor needed for waiting
            steps {
                input 'Deploy to Production?'
            }
        }
    }
}
```

**Key Takeaway**: 透過精確的 Label 與 Agent 設定，實現了資源的最佳化配置，避免了 iOS Build 佔用 Linux 資源，也保護了 Master 的穩定性。