# 1. 前言與學習目標 (Introduction & Learning Objectives)

在傳統的 CI/CD 架構中，維護一組靜態的 Build Agents（例如固定的 VM 或實體機）往往是維運的惡夢。這不僅導致資源閒置浪費，還容易發生「環境污染」（Dependency Hell），即前一個 Build 的殘留檔案影響了下一個 Build。本章將探討如何利用 Docker 與 Kubernetes 實現 Jenkins Agent 的動態擴展。

In traditional CI/CD architectures, maintaining a fleet of static Build Agents (e.g., fixed VMs or bare-metal servers) is often an operational nightmare. This not only leads to idle resource waste but also creates "environment pollution" (Dependency Hell), where artifacts from a previous build negatively impact the next one. This chapter explores how to leverage Docker and Kubernetes to achieve dynamic scaling of Jenkins Agents.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計動態擴展架構**：理解並實作 Jenkins Controller 與 Kubernetes Cluster 的整合，實現 Agent 的隨需建立與銷毀。
    **Design Scalable Architectures**: Understand and implement the integration between Jenkins Controller and Kubernetes Cluster to achieve on-demand creation and destruction of agents.
2.  **實作容器化流水線**：撰寫宣告式流水線（Declarative Pipeline），在 Pod 中定義多個容器（Sidecar pattern）來處理複雜的構建任務。
    **Implement Containerized Pipelines**: Write Declarative Pipelines that define multiple containers (Sidecar pattern) within a Pod to handle complex build tasks.
3.  **解決環境隔離問題**：徹底消除不同專案間的依賴衝突，確保每次構建都在乾淨的環境中執行。
    **Solve Environment Isolation**: Completely eliminate dependency conflicts between projects, ensuring every build runs in a pristine environment.
4.  **優化資源利用率**：透過 Resource Requests/Limits 與 Pod Templates，精確控制構建資源成本。
    **Optimize Resource Utilization**: Precisely control build resource costs using Resource Requests/Limits and Pod Templates.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 靜態車隊 vs. 共享乘車 (Static Fleet vs. Ride-Sharing)

將傳統的 Static Agents 想像成公司擁有的「公務車隊」。無論是否有人出差，你都必須支付維護費、停車費；且如果所有人同時要用車，車輛就會不夠用（Queueing）。

Imagine traditional Static Agents as a company-owned "corporate fleet." Regardless of whether anyone is traveling, you must pay for maintenance and parking. Furthermore, if everyone needs a car at the same time, you run out of vehicles (Queueing).

Jenkins 的動態代理（Dynamic Agents）則像是「Uber/Lyft」。當有構建需求時，系統自動叫車（Provision Pod）；任務結束後，車輛離開（Terminate Pod）。你只需為實際行駛的里程付費，且理論上可以同時調用無限輛車（受限於 Cluster Quota）。

Jenkins Dynamic Agents are like "Uber/Lyft." When there is a build request, the system automatically hails a ride (Provisions a Pod); once the task is done, the vehicle leaves (Terminates the Pod). You only pay for the actual distance driven, and theoretically, you can summon an unlimited number of vehicles simultaneously (limited by Cluster Quota).

### 2.2 Pod Template 與 Sidecar 模式 (Pod Template & Sidecar Pattern)

在 Kubernetes 環境中，Jenkins Agent 不再是一個單一的 SSH Server。它通常是一個 **Pod**，其中包含：
In a Kubernetes environment, a Jenkins Agent is no longer a single SSH Server. It is typically a **Pod** containing:

1.  **JNLP (Inbound) Container**: 負責與 Jenkins Controller 通訊，協調指令。
    **JNLP (Inbound) Container**: Responsible for communicating with the Jenkins Controller and orchestrating commands.
2.  **Build Tool Containers**: 實際執行任務的容器（如 Maven, Node.js, Go, Python）。
    **Build Tool Containers**: Containers that actually execute the tasks (e.g., Maven, Node.js, Go, Python).

這運用了 **Sidecar 模式**。所有容器共享同一個 Network Namespace 和 Volume（通常是 `emptyDir`），因此 `maven` 容器編譯出的檔案，`docker` 容器可以直接讀取並打包。

This utilizes the **Sidecar Pattern**. All containers share the same Network Namespace and Volume (usually `emptyDir`), so files compiled by a `maven` container can be directly read and packaged by a `docker` container.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 架構設計 (Architectural Design)

在大型企業級部署中，Jenkins Controller 通常不執行任何 Job，只負責調度。

In large-scale enterprise deployments, the Jenkins Controller typically does not execute any jobs; it only handles scheduling.

*   **Controller**: 部署在 K8s 中（StatefulSet）或獨立 VM。負責儲存組態、歷史紀錄與 Web UI。
    **Controller**: Deployed in K8s (StatefulSet) or a standalone VM. Responsible for storing configuration, history, and the Web UI.
*   **Kubernetes Cloud Plugin**: 連接 Controller 與 K8s API Server 的橋樑。
    **Kubernetes Cloud Plugin**: The bridge connecting the Controller and the K8s API Server.
*   **Ephemeral Agents**: 每次 Build 觸發時，Plugin 呼叫 K8s API 建立 Pod。Build 結束後 Pod 銷毀。
    **Ephemeral Agents**: Every time a build is triggered, the Plugin calls the K8s API to create a Pod. The Pod is destroyed after the build finishes.

### 3.2 對系統品質的影響 (Impact on System Qualities)

*   **可擴充性 (Scalability)**:
    *   **High**: 只要 K8s Cluster 有資源，Jenkins 就能無限水平擴展 Agent。解決了週五下午發版高峰期的排隊問題。
    *   **High**: As long as the K8s Cluster has resources, Jenkins can horizontally scale agents indefinitely. This solves the queuing problem during Friday afternoon release peaks.
*   **可靠性與隔離性 (Reliability & Isolation)**:
    *   每個 Build 都在全新的 Container 中執行，徹底避免了「上一個專案留下的全域變數或暫存檔導致測試失敗」的問題。
    *   Every build runs in a brand-new container, completely avoiding failures caused by "global variables or temp files left by the previous project."
*   **安全性 (Security)**:
    *   Agent 存活時間極短，減少了攻擊面。可以使用 K8s Service Account 限制 Agent 的權限（例如只能存取特定的 Namespace 或 Secret）。
    *   Agents are short-lived, reducing the attack surface. K8s Service Accounts can be used to restrict Agent privileges (e.g., access only to specific Namespaces or Secrets).

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)

我們有一個 Java + React 的全端專案。傳統做法是在一台 VM 上同時安裝 JDK 17, Node.js 18, Maven 3.8。但另一個舊專案需要 JDK 8 和 Node.js 14。在同一台 VM 上管理這些版本非常痛苦。

We have a full-stack project using Java + React. The traditional approach is to install JDK 17, Node.js 18, and Maven 3.8 on a single VM. However, another legacy project requires JDK 8 and Node.js 14. Managing these versions on the same VM is painful.

我們將使用 Jenkins Kubernetes Plugin 來解決此問題。

We will use the Jenkins Kubernetes Plugin to solve this.

### 解決方案：Kubernetes Pod Template (Solution: Kubernetes Pod Template)

我們不在 Jenkins 全域設定中定義 Agent，而是直接在 `Jenkinsfile` 中定義所需的執行環境（Pipeline as Code）。

Instead of defining agents in the Jenkins global configuration, we define the required execution environment directly in the `Jenkinsfile` (Pipeline as Code).

#### Jenkinsfile

```groovy
pipeline {
    agent {
        kubernetes {
            // 定義 Pod 的 YAML 結構
            // Define the YAML structure of the Pod
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    some-label: some-value
spec:
  containers:
    # 1. Java/Maven Container
    - name: maven
      image: maven:3.8.6-openjdk-11
      command:
        - cat
      tty: true
      resources:
        requests:
          memory: "512Mi"
          cpu: "500m"
        limits:
          memory: "1024Mi"
          cpu: "1000m"
      
    # 2. Node.js Container
    - name: nodejs
      image: node:18-alpine
      command:
        - cat
      tty: true
  
  # 3. 預設的 JNLP Agent 會自動被注入
  # The default JNLP Agent will be automatically injected
'''
        }
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Backend') {
            steps {
                container('maven') {
                    // 在 maven 容器中執行
                    // Execute inside the maven container
                    sh 'mvn -version'
                    sh 'mvn clean package -DskipTests'
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                container('nodejs') {
                    // 在 nodejs 容器中執行
                    // Execute inside the nodejs container
                    sh 'node -v'
                    sh 'npm install && npm run build'
                }
            }
        }
        
        stage('Integration') {
            steps {
                // 驗證產出物是否存在 (所有容器共享 Workspace)
                // Verify artifacts exist (Workspace is shared across containers)
                sh 'ls -l target/'
                sh 'ls -l build/'
            }
        }
    }
}
```

### 關鍵細節 (Key Details)

1.  **`command: - cat` & `tty: true`**: 這是為了讓容器啟動後保持運行狀態（Keep-alive），否則像 Maven 這種工具執行完就會退出，導致 Pod 崩潰。Jenkins 會透過 `kubectl exec` 進入容器執行指令。
    **`command: - cat` & `tty: true`**: This is to keep the container running (Keep-alive) after startup. Otherwise, tools like Maven would exit after execution, causing the Pod to crash. Jenkins uses `kubectl exec` to enter the container and run commands.
2.  **共享 Workspace**: Kubernetes Plugin 預設會掛載一個 `emptyDir` Volume 到所有容器的 `/home/jenkins/agent`。因此，`maven` 階段產生的 `.jar` 檔，後續階段依然看得到。
    **Shared Workspace**: The Kubernetes Plugin defaults to mounting an `emptyDir` Volume to `/home/jenkins/agent` in all containers. Therefore, `.jar` files generated in the `maven` stage are visible in subsequent stages.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 Docker-in-Docker (DinD) (Abusing Docker-in-Docker)

*   **錯誤 (Mistake)**: 為了在 Pipeline 中建立 Docker Image，在 Pod 中以 Privileged 模式執行 Docker Daemon。
    **Mistake**: Running Docker Daemon in Privileged mode inside the Pod to build Docker Images within the Pipeline.
*   **後果 (Consequence)**: 極大的安全風險（Root 權限逃逸），且可能導致外層 Node 的檔案系統損壞。
    **Consequence**: Huge security risk (Root privilege escalation) and potential corruption of the outer Node's filesystem.
*   **較佳解法 (Better Solution)**:
    1.  **Docker-outside-of-Docker (DooD)**: 掛載宿主機的 `/var/run/docker.sock`（需注意權限）。
        **Docker-outside-of-Docker (DooD)**: Mount the host's `/var/run/docker.sock` (mind the permissions).
    2.  **Kaniko / Buildah**: 使用不需要 Daemon 的構建工具（Daemonless build tools），這是目前 K8s 原生環境的最佳實踐。
        **Kaniko / Buildah**: Use daemonless build tools, which is the current best practice for K8s-native environments.

### 5.2 忽略資源限制 (Ignoring Resource Limits)

*   **錯誤 (Mistake)**: 在 Pod Template 中未設定 `resources.requests` 和 `limits`。
    **Mistake**: Not setting `resources.requests` and `limits` in the Pod Template.
*   **後果 (Consequence)**: 某個 Build 佔用過多記憶體導致 Node OOM (Out Of Memory)，殺死該 Node 上其他正常的 Pods（Noisy Neighbor problem）。
    **Consequence**: A single build consumes too much memory, causing Node OOM (Out Of Memory) and killing other healthy Pods on that Node (Noisy Neighbor problem).

### 5.3 映像檔過大 (Bloated Images)

*   **錯誤 (Mistake)**: 建立一個包含所有工具（Java, Node, Python, Go...）的 "Mega-Agent" Image，大小高達 5GB。
    **Mistake**: Creating a "Mega-Agent" Image containing all tools (Java, Node, Python, Go...) that is 5GB in size.
*   **後果 (Consequence)**: 每次拉取 Image 時間過長，拖慢 Build 啟動速度，且增加網路頻寬成本。
    **Consequence**: Excessive image pull times slow down build startup and increase network bandwidth costs.
*   **較佳解法 (Better Solution)**: 使用 Sidecar 模式組合多個輕量級官方 Image（如範例所示）。
    **Better Solution**: Use the Sidecar pattern to combine multiple lightweight official images (as shown in the example).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 當 Jenkins Build Queue 暴增到數千個 Pending Jobs 時，你會如何排查與優化？
**How would you troubleshoot and optimize when the Jenkins Build Queue spikes to thousands of pending jobs?**

*   **高分回答要點 (Key Points)**:
    *   **Controller 瓶頸**: 檢查 Jenkins Controller 的 CPU/Memory，因為它負責協調所有 Remoting 連線。
    *   **K8s Cluster 容量**: 檢查 K8s 是否有足夠的 Node 資源（CPU/Mem）來調度新的 Pods (Pending state reason)。
    *   **Limit concurrency**: 是否設定了全域併發限制？
    *   **架構分離**: 建議將 Controller 與 Agent 徹底分離，甚至採用多個 Controller (Jenkins Operation Center) 進行分流。

### Q2: 在 Kubernetes Agent 中，Workspace 的持久化如何處理？如果 Pod 崩潰，Log 和 Artifacts 還在嗎？
**How is Workspace persistence handled in Kubernetes Agents? If the Pod crashes, are Logs and Artifacts still available?**

*   **高分回答要點 (Key Points)**:
    *   預設使用 `emptyDir`，Pod 銷毀或崩潰後資料即遺失。
    *   **Logs**: Jenkins Controller 會即時串流 Log，所以 Console Output 通常會保留在 Controller 端。
    *   **Artifacts**: 必須在 Pipeline 結束前使用 `archiveArtifacts` 或上傳至 S3/Artifactory。
    *   **Debugging**: 若需除錯，可在 Pipeline 加入 `sleep` 或配置 `retries`，或使用 PVC (Persistent Volume Claim) 來掛載持久儲存（但不建議用於高併發場景，因為 ReadWriteMany 效能差）。

### Q3: 如何在不給予 Privileged 權限的情況下，在 K8s Jenkins Agent 中構建 Docker Image？
**How do you build Docker Images in a K8s Jenkins Agent without granting Privileged access?**

*   **高分回答要點 (Key Points)**:
    *   明確指出 **Kaniko** 是 Google 推薦的方案，它在 User space 執行構建，不需要 Docker Daemon。
    *   解釋 Kaniko 的運作原理（Snapshotting filesystem changes）。
    *   提及替代方案如 Buildah 或 Podman。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點 (Key Takeaways)

1.  **動態代理 (Dynamic Provisioning)**: 使用 K8s Plugin 取代靜態 VM，實現資源彈性與成本優化。
2.  **Pod Template**: 在 `Jenkinsfile` 中定義 Agent 架構，實現 Infrastructure as Code。
3.  **Sidecar Pattern**: 利用多容器協同工作（如 Maven + Node），保持 Image 輕量化與職責單一。
4.  **隔離性 (Isolation)**: 容器化確保了每次構建環境的一致性與乾淨。
5.  **安全性 (Security)**: 避免 DinD，採用 Kaniko 等現代化構建工具，並限制 Pod 資源。

### 後續延伸 (Next Steps)

*   **Chapter 05**: **Pipeline as Code 進階模式 (Advanced Pipeline as Code)** - 學習如何將上述的 Pod Template 封裝進 **Shared Libraries**，讓數百個專案共用標準化的構建環境配置，減少重複程式碼。
    **Chapter 05**: **Advanced Pipeline as Code** - Learn how to encapsulate the Pod Templates discussed above into **Shared Libraries**, allowing hundreds of projects to share standardized build environment configurations and reduce code duplication.