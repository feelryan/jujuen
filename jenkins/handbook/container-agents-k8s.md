# 容器化構建環境：Docker 與 Kubernetes Agents / Containerized Builds: Docker and Kubernetes Agents

## Mental model｜心智模型

要掌握容器化 Agents，必須從 **「寵物 (Pets)」思維轉向「牲畜 (Cattle)」思維**，或者更精確地說，轉向 **「即用即丟的無菌室 (Disposable Clean Rooms)」**。

### 1. 從靜態伺服器到動態資源池 (Static to Dynamic)
- **傳統模式 (Static Agents)**：你擁有一排固定的 VM 或實體機（Build Servers）。你需要維護上面的 JDK 版本、Node.js 版本，並擔心 A 專案的依賴會污染 B 專案。它們是長期運行的，容易累積「數位淤泥 (Digital Sludge)」。
- **容器模式 (Ephemeral Agents)**：Jenkins Master 不再擁有固定的工人。當任務來臨時，它向 Kubernetes Cluster 申請一個全新的 Pod。這個 Pod 裡包含了這次構建所需的精確工具（例如：特定版本的 Go + Docker CLI）。任務結束後，Pod 直接銷毀，不留痕跡。

### 2. Sidecar 模式 (The Sidecar Pattern)
在 Kubernetes Agent 中，Jenkins 使用一種特殊的 Pod 結構：
- **JNLP Container (The Coordinator)**：這是 Jenkins 的「通訊員」，負責與 Master 保持連線、傳輸 Log 和 Artifacts。
- **Tool Containers (The Workers)**：掛載在同一個 Pod 中的其他容器（如 Maven, Python, Docker）。
- **共享空間**：所有容器共享同一個 Network namespace 和 Workspace volume。這意味著你在 Tool Container 裡 `mvn clean package` 產生的檔案，JNLP Container 可以直接讀取並回傳給 Master。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 定義 Pod Templates 於代碼中 (Define Pod Templates in Code)
不要在 Jenkins UI (`Manage Jenkins` -> `Clouds`) 中手動設定 Pod Templates。這難以版控且難以維護。
- **Pattern**: 使用 Declarative Pipeline 的 `agent { kubernetes { ... } }` 語法，將 YAML 定義直接寫在 `Jenkinsfile` 裡，或是引用專案中的 `.yaml` 檔案。這實現了 **Infrastructure as Code**。

### 2. 依賴快取策略 (Dependency Caching Strategy)
容器化構建最大的痛點是「每次都要重新下載依賴 (The Internet Download Penalty)」。
- **Best Practice**: 使用 **Persistent Volume Claim (PVC)** 掛載到容器內的依賴目錄（如 `/root/.m2` 或 `/home/jenkins/.npm`）。
- **Alternative**: 如果 PVC 管理困難，至少配置內網的 Proxy Repository (如 Nexus/Artifactory) 並在容器環境變數中指向它。

### 3. 避免 "Kitchen Sink" 映像檔 (Avoid "Kitchen Sink" Images)
不要試圖建立一個包含所有工具（Java + Node + Python + Go...）的巨大 Docker Image。
- **Pattern**: 採用 **Multi-Container Pods**。需要 Java 就拉 OpenJDK image，需要 Node 就拉 Node image。這讓你的構建環境極度輕量且靈活。

### 4. 資源配額與限制 (Resource Requests and Limits)
Kubernetes 是一個資源調度器，如果你不告訴它你需要多少資源，它可能會將你的 Pod 塞進一個已經過載的 Node。
- **Best Practice**: 永遠設定 `resources.requests` (保證資源) 和 `resources.limits` (防止失控)。這能避免構建過程中發生隨機的 JVM Crash 或 OOMKilled。

### 5. 構建 Docker 映像檔的方案 (Building Docker inside K8s)
在 K8s 裡面 build Docker image 是一個經典難題。
- **Pattern A (Kaniko)**: Google 推出的工具，不需要 Docker daemon 即可構建 Image，安全性較高（推薦）。
- **Pattern B (Docker-out-of-Docker)**: 將 Host 的 `/var/run/docker.sock` 掛載進 Pod。簡單粗暴，但有資安風險（容器取得 Host root 權限）。僅在受信任的集群中使用。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Docker-in-Docker (DinD) 的濫用
- **Anti-pattern**: 在 Pod 內部運行一個獨立的 Docker Daemon (`privileged: true`)。
- **Why**: 這需要特權模式，會導致嚴重的安全漏洞，且容易遇到檔案系統 (OverlayFS on OverlayFS) 的效能與相容性問題。
- **Fix**: 優先使用 Kaniko，或退而求其次使用 Docker-out-of-Docker (Mount socket)。

### 2. 忽視容器啟動時間 (Ignoring Spin-up Time)
- **Pitfall**: 每個 Job 都要等待拉取 Image 和啟動 Pod，導致原本 10 秒的單元測試變成了 2 分鐘（1m50s 在啟動環境）。
- **Fix**: 確保你的 K8s Node 預先拉取了常用 Base Images (Image Pull Policy: `IfNotPresent`)，或者針對極高頻的小任務，保留少量的靜態 VM Agent。

### 3. Workspace 權限地獄 (Workspace Permission Hell)
- **Pitfall**: 構建失敗，出現 `Permission denied`。這是因為 Container 預設使用 root，但 Jenkins Agent 預設使用 `jenkins (uid: 1000)`，或者掛載的 Volume 權限不對。
- **Fix**: 在 Pod Template 中明確指定 `securityContext`，確保 `runAsUser` 與 `fsGroup` 一致。

### 4. 殭屍 Pods (Zombie Pods)
- **Pitfall**: Jenkins Master 重啟或網路中斷後，K8s 上殘留了大量 orphaned build pods 佔用資源。
- **Fix**: 調整 Kubernetes Plugin 的 `Active Deadline Seconds`，並確保 Jenkins Service Account 有權限刪除 Pods。定期執行清理腳本。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Implementation Checklist
在設計一個新的 Kubernetes-based Pipeline 時，請檢查：

- [ ] **Image Selection**: 是否使用了官方或受信任的輕量級 Image (如 `alpine` based)？
- [ ] **Resource Limits**: 是否定義了 CPU 和 Memory 的 `requests` 與 `limits`？
- [ ] **Timeout**: 是否設定了 `timeout`？防止 Agent 卡死佔用 Cluster 資源。
- [ ] **Caching**: 是否掛載了 PVC 來快取 Maven/NPM/Gradle 依賴？
- [ ] **Security**: 是否避免使用 `privileged: true` (除非絕對必要)？
- [ ] **Service Account**: 該 Namespace 的 Service Account 是否有權限建立/刪除 Pods？

### Debugging Workflow (當 Agent 啟動失敗時)
1. **檢查 Jenkins Log**: 查看 Master 的 System Log，尋找 Kubernetes Plugin 的錯誤訊息。
2. **檢查 K8s Events**: 使用 `kubectl get events -n <namespace>` 查看是否有調度失敗 (Insufficient cpu/memory) 或 Image Pull Error。
3. **保留現場**: 在 Pipeline 中暫時加入 `sleep 3600` 或配置 `yamlMergeStrategy`，防止 Pod 失敗後立即被刪除，以便使用 `kubectl logs` 或 `kubectl exec` 進入除錯。

---

## Real-world examples｜實戰案例

### 案例 1：標準的多容器協作 (Polyglot Build)
這是一個典型的場景：前端使用 Node.js，後端使用 Java，最後打包成 Docker Image。

```groovy
pipeline {
    agent {
        kubernetes {
            // 使用 yaml 定義 Pod，比 Groovy DSL 更直觀且易於複製貼上
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    some-label: some-value
spec:
  containers:
  # 1. Golang 容器，用於編譯後端
  - name: golang
    image: golang:1.20-alpine
    command: ['cat']
    tty: true
    resources:
      limits:
        memory: "1Gi"
        cpu: "500m"
  # 2. Node 容器，用於編譯前端
  - name: nodejs
    image: node:18-alpine
    command: ['cat']
    tty: true
  # 3. Kaniko 容器，用於構建 Docker Image (無特權模式)
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ['cat']
    tty: true
    volumeMounts:
      - name: kaniko-secret
        mountPath: /kaniko/.docker
  volumes:
  - name: kaniko-secret
    secret:
      secretName: docker-registry-creds
'''
        }
    }
    stages {
        stage('Backend Build') {
            steps {
                container('golang') {
                    sh 'go build -o app main.go'
                }
            }
        }
        stage('Frontend Build') {
            steps {
                container('nodejs') {
                    sh 'npm install && npm run build'
                }
            }
        }
        stage('Docker Build & Push') {
            steps {
                container('kaniko') {
                    sh '/kaniko/executor --context `pwd` --destination myregistry.com/my-app:latest'
                }
            }
        }
    }
}
```

### 案例 2：解決依賴快取 (Solving Dependency Caching)
利用 PVC 避免每次重新下載 Internet。

```yaml
# 在 Pod Template 的 volumes 部分加入
volumes:
  - name: maven-repo
    persistentVolumeClaim:
      claimName: maven-repo-pvc

# 在 Container 的 volumeMounts 部分加入
volumeMounts:
  - name: maven-repo
    mountPath: /root/.m2/repository
```

**決策樹 (Decision Tree) - 選擇哪種 Agent 模式？**
1. **需要極高的啟動速度 (< 5s)？** -> 考慮靜態 VM 或長期運行的 Container。
2. **需要特殊的硬體 (GPU/Mac M1)？** -> 使用靜態 Agent (SSH 連線)。
3. **一般用途、需要隔離性、高併發？** -> **Kubernetes Ephemeral Agents (本章節推薦)**。
4. **需要構建 Windows Container？** -> 確保 K8s Cluster 支援 Windows Node，否則回退到 VM。