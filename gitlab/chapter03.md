# Runner Architecture and Executors
# Runner 架構與執行環境配置

## 1. 前言與學習目標
### Introduction and Learning Objectives

對於資深工程師而言，GitLab Runner 不僅僅是一個安裝在伺服器上的 Binary 檔案，它是整個 CI/CD 系統的算力核心與資源調度器。理解 Runner 的架構對於構建高效、安全且具備成本效益的 DevOps 平台至關重要。
For senior engineers, the GitLab Runner is more than just a binary installed on a server; it is the computational core and resource scheduler of the entire CI/CD system. Understanding Runner architecture is crucial for building efficient, secure, and cost-effective DevOps platforms.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇 Executor**：根據專案需求（如安全性、效能、依賴複雜度），在 Shell, Docker, Kubernetes 等 Executor 之間做出正確的架構決策。
    **Select Executors with Precision**: Make the right architectural decisions between Shell, Docker, and Kubernetes executors based on project requirements (e.g., security, performance, dependency complexity).
2.  **設計自動擴展架構**：規劃 Autoscaling Runners（特別是基於 Kubernetes 或 Cloud Instances），以解決尖峰負載並優化閒置成本。
    **Design Autoscaling Architectures**: Plan Autoscaling Runners (specifically based on Kubernetes or Cloud Instances) to handle peak loads and optimize idle costs.
3.  **強化執行環境安全**：識別 Docker-in-Docker (dind) 的風險，並實作更安全的容器映像檔建置策略（如 Kaniko）。
    **Harden Execution Environments**: Identify the risks of Docker-in-Docker (dind) and implement more secure container image building strategies (such as Kaniko).

---

## 2. 核心觀念與心智模型
### Core Concepts & Mental Model

#### 2.1 The Coordinator-Agent Model (協調者-代理模型)

GitLab CI/CD 的運作基於「輪詢（Polling）」機制，而非伺服器主動推送。
GitLab CI/CD operates on a "Polling" mechanism rather than server-initiated push.

*   **GitLab Server (Coordinator)**: 負責儲存程式碼、管理 Pipeline 狀態與 Job Queue。它不執行實際的 Build Script。
    **GitLab Server (Coordinator)**: Responsible for storing code, managing Pipeline states, and the Job Queue. It does not execute the actual build scripts.
*   **GitLab Runner (Agent)**: 一個獨立的 Process，透過 HTTP(S) 向 Server 詢問：「有工作給我嗎？」如果有，它會領取 Payload，執行後回報結果。
    **GitLab Runner (Agent)**: An independent process that asks the Server via HTTP(S): "Do you have work for me?" If yes, it claims the payload, executes it, and reports the result.

> **Mental Model**: 想像 GitLab Server 是一個餐廳的「訂單系統」，而 Runner 是「廚師」。廚師主動看訂單系統來決定做什麼菜，而不是訂單系統強行控制廚師的手。
> **Mental Model**: Imagine the GitLab Server as a restaurant's "Order System," and the Runner as the "Chef." The Chef actively looks at the order system to decide what to cook, rather than the system physically controlling the Chef's hands.

#### 2.2 Executors: The Runtime Environment (執行環境)

Executor 決定了 Job 具體在哪裡跑。這也是系統設計中最關鍵的選擇。
The Executor determines exactly where the Job runs. This is the most critical choice in system design.

| Executor | Analogy (類比) | Characteristics (特點) | Use Case (適用場景) |
| :--- | :--- | :--- | :--- |
| **Shell** | **Bare Metal** | 直接在 Runner 宿主機執行指令。環境髒亂，無隔離。 <br> Executes commands directly on the Runner host. Messy environment, no isolation. | 部署到該特定機器、執行簡單的 OS 級別任務。 <br> Deploying to that specific machine, simple OS-level tasks. |
| **Docker** | **Virtual Lab** | 每個 Job 啟動一個乾淨的 Container。環境一致，隔離性佳。 <br> Spins up a clean Container for each Job. Consistent environment, good isolation. | 通用 CI/CD，大多數應用程式的標準選擇。 <br> General CI/CD, the standard choice for most applications. |
| **Kubernetes** | **Orchestrated Fleet** | 每個 Job 是一個 Pod。資源動態分配，高度可擴展。 <br> Each Job is a Pod. Dynamic resource allocation, highly scalable. | 企業級規模化環境，需要動態伸縮資源。 <br> Enterprise-scale environments requiring dynamic resource scaling. |

#### 2.3 Tags & Concurrency (標籤與並發)

*   **Tags**: 用於將特定類型的 Job 路由到具備特定能力的 Runner（例如：`gpu` tag 路由到有 GPU 的機器）。
    **Tags**: Used to route specific types of Jobs to Runners with specific capabilities (e.g., a `gpu` tag routes to a machine with a GPU).
*   **Concurrency**: 全域設定，決定這個 Runner 實例同時能處理多少個 Job。
    **Concurrency**: A global setting that determines how many Jobs this Runner instance can handle simultaneously.

---

## 3. 實務場景與系統設計視角
### Real-World & System Design View

在 Production 環境中，我們很少使用單機 Shell Runner。資深工程師需要從**平台工程 (Platform Engineering)** 的角度來設計 Runner 架構。
In a Production environment, we rarely use single-machine Shell Runners. Senior engineers need to design Runner architecture from a **Platform Engineering** perspective.

#### 3.1 Shared vs. Specific Runners (共享與專用)

*   **Shared Runners (Instance Level)**: 由平台團隊維護，提供給所有專案使用。通常配置為 Autoscaling Docker/K8s Runners。
    **Shared Runners (Instance Level)**: Maintained by the platform team, available to all projects. Usually configured as Autoscaling Docker/K8s Runners.
    *   *優點 (Pros)*: 資源利用率高，開發者無需維護基礎設施。
    *   *缺點 (Cons)*: 可能會有 "Noisy Neighbor" 問題，安全性隔離要求極高。
*   **Specific Runners (Project/Group Level)**: 專為特定專案配置。
    **Specific Runners (Project/Group Level)**: Configured specifically for a project.
    *   *優點 (Pros)*: 物理隔離，可存取該專案特定的 VPC 資源或硬體（如 iOS Mac Mini, GPU）。
    *   *缺點 (Cons)*: 閒置成本高，維護負擔在專案團隊身上。

#### 3.2 Scalability & Cost Optimization (擴展性與成本優化)

大型團隊面臨的主要挑戰是：白天 commit 頻繁導致排隊，晚上資源閒置浪費錢。
The main challenge for large teams is: frequent commits during the day lead to queuing, while idle resources at night waste money.

*   **Autoscaling with Docker Machine (Legacy but popular)**: Runner Manager 啟動 VM (EC2/GCE) 來跑 Job，跑完銷毀。
    **Autoscaling with Docker Machine (Legacy but popular)**: Runner Manager spins up VMs (EC2/GCE) to run Jobs and destroys them afterwards.
*   **Kubernetes Executor (Modern Standard)**: 利用 K8s 的 Cluster Autoscaler。當 Job Pods 增加，K8s 自動增加 Node。這是目前最推薦的模式。
    **Kubernetes Executor (Modern Standard)**: Leverages K8s Cluster Autoscaler. As Job Pods increase, K8s automatically adds Nodes. This is the currently recommended pattern.

#### 3.3 Security Boundaries (安全邊界)

*   **Untrusted Code**: 若 Runner 執行的是來自 Fork 的 PR 代碼，必須確保它無法存取敏感的 Secrets 或攻擊內網。
    **Untrusted Code**: If the Runner is executing code from a Fork's PR, you must ensure it cannot access sensitive Secrets or attack the internal network.
*   **Privileged Mode**: 盡量避免開啟 Docker 的 `privileged = true`，除非你完全信任該環境。這會允許容器獲得宿主機的 Root 權限。
    **Privileged Mode**: Avoid enabling Docker's `privileged = true` unless you fully trust the environment. This allows the container to gain Root privileges on the host.

---

## 4. 逐步示例：Kubernetes Executor 配置
### Walkthrough / Example: Kubernetes Executor Configuration

#### 場景 (Scenario)
你的團隊正在將 CI/CD 從單台 VM 遷移到 Kubernetes Cluster，目標是支援 50+ 並發 Jobs，並實現資源自動回收。
Your team is migrating CI/CD from a single VM to a Kubernetes Cluster, aiming to support 50+ concurrent Jobs and achieve automatic resource reclamation.

#### 步驟 1: 理解 Helm Chart 配置
#### Step 1: Understanding Helm Chart Configuration

我們使用官方的 GitLab Runner Helm Chart。關鍵在於 `values.yaml` 的配置。
We use the official GitLab Runner Helm Chart. The key lies in the `values.yaml` configuration.

```yaml
# values.yaml snippet

gitlabUrl: "https://gitlab.example.com/"
runnerRegistrationToken: "s3cr3t-t0k3n"

# Runner Configuration
concurrent: 50  # Max jobs this runner manager can spawn globally
checkInterval: 3 # Polling interval in seconds

runners:
  config: |
    [[runners]]
      [runners.kubernetes]
        namespace = "gitlab-runner-jobs"
        image = "ubuntu:20.04"
        
        # Resource Limits are crucial for K8s Autoscaling to work
        cpu_request = "500m"
        cpu_limit = "2"
        memory_request = "512Mi"
        memory_limit = "4Gi"
        
        # Service Account for the Job Pods (permissions)
        service_account = "default"
        
        # Optimization: Use node affinity to run jobs on specific node pools
        [runners.kubernetes.node_selector]
          "workload_type" = "ci-jobs"
```

#### 步驟 2: 資源請求與限制 (Resources Requests & Limits)
#### Step 2: Resource Requests & Limits

**為何重要？** 如果不設定 `cpu_request`，K8s Scheduler 無法正確計算節點壓力，Cluster Autoscaler 就不會觸發新增節點，導致 Job 處於 Pending 狀態。
**Why it matters?** If `cpu_request` is not set, the K8s Scheduler cannot correctly calculate node pressure, and the Cluster Autoscaler will not trigger node addition, leaving Jobs in a Pending state.

#### 步驟 3: 處理 Docker Build (The "Docker-in-Docker" Problem)
#### Step 3: Handling Docker Build (The "Docker-in-Docker" Problem)

在 K8s 中構建 Docker Image 有兩種主流方式：
There are two mainstream ways to build Docker Images in K8s:

1.  **Docker-in-Docker (dind)**: 需要 `privileged` 模式。
    **Docker-in-Docker (dind)**: Requires `privileged` mode.
    ```yaml
    # Not recommended for shared environments due to security
    [runners.kubernetes]
      privileged = true
    ```

2.  **Kaniko (Google's solution)**: 不需要 Daemon，不需要 Root，更安全。
    **Kaniko (Google's solution)**: Daemonless, rootless, more secure.
    
    *In your `.gitlab-ci.yml`:*
    ```yaml
    build:
      stage: build
      image:
        name: gcr.io/kaniko-project/executor:debug
        entrypoint: [""]
      script:
        - /kaniko/executor --context $CI_PROJECT_DIR --dockerfile $CI_PROJECT_DIR/Dockerfile --destination $IMAGE_TAG
    ```

#### 實務分析 (Practical Analysis)
使用 Kaniko 雖然稍微慢一點（因為沒有 Layer Cache Daemon），但它消除了給予 Runner `privileged` 權限的需求，這在多租戶（Multi-tenant）叢集中是安全合規的關鍵。
While Kaniko is slightly slower (due to the lack of a Layer Cache Daemon), it eliminates the need to grant `privileged` access to the Runner, which is key to security compliance in multi-tenant clusters.

---

## 5. 常見錯誤與反模式
### Common Pitfalls & Anti-patterns

#### 5.1 The "Shell Executor" Trap (Shell Executor 陷阱)
*   **錯誤 (Pitfall)**: 在生產環境的 CI Server 上使用 Shell Executor 來跑 `npm install` 或 `docker build`。
    **Pitfall**: Using Shell Executor on a production CI Server to run `npm install` or `docker build`.
*   **後果 (Consequence)**: 不同專案的依賴衝突（Project A 需要 Node 14，Project B 需要 Node 18）；殘留檔案塞滿磁碟；安全性極低（Job 可以讀取 `~/.ssh`）。
    **Consequence**: Dependency conflicts between projects (Project A needs Node 14, Project B needs Node 18); residual files filling up the disk; extremely low security (Jobs can read `~/.ssh`).
*   **修正 (Fix)**: 始終優先使用 Docker 或 Kubernetes Executor。

#### 5.2 Ignoring Cache Distributed Storage (忽略快取的分散式儲存)
*   **錯誤 (Pitfall)**: 在 Autoscaling 環境中，依賴本地路徑做 Cache。
    **Pitfall**: Relying on local paths for Cache in an Autoscaling environment.
*   **後果 (Consequence)**: 當 Job A 在 Runner 1 執行，Job B 在 Runner 2 執行，Cache 無法共享，導致每次都要重新下載依賴，拖慢速度並增加頻寬成本。
    **Consequence**: When Job A runs on Runner 1 and Job B on Runner 2, the Cache cannot be shared, causing dependencies to be re-downloaded every time, slowing down speed and increasing bandwidth costs.
*   **修正 (Fix)**: 配置 S3 / GCS / MinIO 作為 Runner 的 Distributed Cache Backend。
    **Fix**: Configure S3 / GCS / MinIO as the Distributed Cache Backend for the Runner.

#### 5.3 Infinite Job Timeout (無限的 Job 超時)
*   **錯誤 (Pitfall)**: 沒有設定合理的 Job Timeout。
    **Pitfall**: Not setting a reasonable Job Timeout.
*   **後果 (Consequence)**: 一個卡住的 Job（例如等待 User Input 或死鎖）會佔用 Concurrency Slot 數小時甚至數天，導致其他 Job 排隊。
    **Consequence**: A stuck Job (e.g., waiting for User Input or deadlocked) will occupy a Concurrency Slot for hours or even days, causing other Jobs to queue.
*   **修正 (Fix)**: 在 Project 或 Runner 層級設定 Default Timeout（例如 60 分鐘）。

---

## 6. 面試與實務問答切入點
### Interview & Discussion Hooks

在面試或技術討論中，這些問題能展現你對 GitLab 架構的深度理解：
In interviews or technical discussions, these questions demonstrate your deep understanding of GitLab architecture:

#### Q1: 如何為一個擁有 500 名開發者的組織設計 CI/CD 基礎設施？
#### Q1: How would you design the CI/CD infrastructure for an organization with 500 developers?

*   **高分回答要點 (Key Points)**:
    *   **分層策略**: 設立一組強大的 Shared Runners (K8s based) 處理 80% 的通用任務。
    *   **特殊需求**: 為 iOS/Android 或 ML 團隊設立帶有特定標籤 (Tags) 的 Specific Runners。
    *   **彈性擴展**: 強調使用 Spot Instances (AWS) 或 Preemptible Nodes (GCP) 搭配 K8s Autoscaler 來降低成本。
    *   **快取策略**: 必須提到使用 S3/GCS 做全域 Cache。

#### Q2: 在 Kubernetes Executor 中，如何解決 Docker Build 的安全性問題？
#### Q2: How do you address the security concerns of Docker Build within a Kubernetes Executor?

*   **高分回答要點 (Key Points)**:
    *   解釋 **Docker-in-Docker (dind)** 需要 `privileged` 模式的風險（Host Root Access）。
    *   提出替代方案：**Kaniko** (無 Daemon, User Space 構建) 或 **Buildah**。
    *   如果必須用 dind，討論如何透過 PSP (Pod Security Policies) 或 OPA Gatekeeper 限制其影響範圍。

#### Q3: Runner 突然停止處理作業，你會如何排查 (Troubleshoot)？
#### Q3: A Runner suddenly stops processing jobs. How would you troubleshoot?

*   **高分回答要點 (Key Points)**:
    *   **檢查連線**: Runner 是否能 `curl` 到 GitLab Server？(DNS, Firewall)。
    *   **檢查 Logs**: `journalctl -u gitlab-runner` 或 K8s Pod logs。是否有 "System panic" 或 "403 Forbidden"。
    *   **資源面**: 磁碟是否滿了？(Docker Prune 未執行)。
    *   **狀態面**: Runner 是否被 Pause 了？Token 是否過期？

---

## 7. 小結與後續延伸
### Summary & Next Steps

#### 重點回顧 (Key Takeaways)
1.  **Runner 是 Agent**: 它主動輪詢 Server，而非被動接收。
    **Runner is an Agent**: It actively polls the Server, rather than passively receiving.
2.  **Executor 選擇**: Docker 是標準，Kubernetes 是規模化首選，Shell 僅限特殊用途。
    **Executor Choice**: Docker is the standard, Kubernetes is the choice for scale, Shell is for special use cases only.
3.  **Autoscaling**: 利用 K8s 或 Cloud Instances 來平衡效能與成本，避免靜態資源浪費。
    **Autoscaling**: Leverage K8s or Cloud Instances to balance performance and cost, avoiding static resource waste.
4.  **Security**: 避免在共享 Runner 上使用 `privileged` 模式，善用 Kaniko 進行容器構建。
    **Security**: Avoid `privileged` mode on shared Runners; leverage Kaniko for container builds.
5.  **Cache**: 在分散式架構中，必須配置 Object Storage (S3/GCS) 作為 Cache Backend。
    **Cache**: In a distributed architecture, Object Storage (S3/GCS) must be configured as the Cache Backend.

#### 後續延伸 (Next Steps)
掌握了 Runner 的架構後，下一章我們將深入探討 **Pipeline 的語法與優化 (Pipeline Syntax & Optimization)**，學習如何編寫高效的 `.gitlab-ci.yml`，利用 DAG (Directed Acyclic Graph) 加速構建流程。
Having mastered Runner architecture, the next chapter will dive into **Pipeline Syntax & Optimization**, learning how to write efficient `.gitlab-ci.yml` files and utilizing DAGs (Directed Acyclic Graphs) to accelerate build processes.