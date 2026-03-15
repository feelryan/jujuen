# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，我們習慣將應用程式容器化、自動化並具備高可用性 (HA)。然而，負責執行這些自動化的 Jenkins 伺服器本身，卻常被視為「寵物 (Pet)」而非「牲畜 (Cattle)」——手動設定、害怕重啟、且缺乏監控。本章的目標是將現代 DevOps 原則應用於 Jenkins 本身，使其具備生產級的韌性。

As senior engineers, we are accustomed to making applications containerized, automated, and highly available (HA). However, the Jenkins server responsible for executing these automations is often treated as a "Pet" rather than "Cattle"—manually configured, terrifying to restart, and lacking monitoring. The goal of this chapter is to apply modern DevOps principles to Jenkins itself, making it production-grade resilient.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作 Configuration as Code (JCasC)**：不再依賴 UI 手動設定，而是將 Jenkins 的系統配置 (System Configuration) 納入版本控制。
    **Implement Configuration as Code (JCasC)**: Move away from manual UI configurations and place Jenkins system configuration under version control.
2.  **設計高可用性 (HA) 與災難復原 (DR) 架構**：理解 OSS Jenkins 與 Enterprise 版本在 HA 上的限制與解法，並制定 RTO/RPO 策略。
    **Design High Availability (HA) and Disaster Recovery (DR) Architectures**: Understand the HA limitations and solutions for OSS Jenkins vs. Enterprise versions, and define RTO/RPO strategies.
3.  **建立可觀測性 (Observability)**：利用 Prometheus 與 Grafana 監控 Jenkins 的健康狀況、佇列長度 (Queue Length) 與節點效能。
    **Establish Observability**: Use Prometheus and Grafana to monitor Jenkins health, queue lengths, and node performance.
4.  **優化維運流程 (Operational Excellence)**：實現 Zero-downtime (或 Near-zero) 的升級與維護策略。
    **Optimize Operational Processes**: Achieve zero-downtime (or near-zero) upgrade and maintenance strategies.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Jenkins 作為「不可變基礎設施」 (Jenkins as Immutable Infrastructure)

傳統上，Jenkins 的狀態 (Jobs, Plugins, Global Config) 全部混雜在 `JENKINS_HOME` 目錄中。這使得遷移或復原變得極其困難。
Traditionally, Jenkins state (Jobs, Plugins, Global Config) is all mixed within the `JENKINS_HOME` directory. This makes migration or recovery extremely difficult.

**心智模型轉變 (Mental Model Shift)**：
我們應將 Jenkins 視為一個**無狀態 (Stateless) 的執行引擎**，其狀態應由外部定義：
We should view Jenkins as a **stateless execution engine**, where its state is defined externally:
*   **Pipeline Logic**: 定義在 Git repo 的 `Jenkinsfile`。
*   **System Config**: 定義在 `jenkins.yaml` (JCasC)。
*   **Build Artifacts**: 儲存在 Artifactory/S3，而非本地磁碟。

## 2.2 單體架構 vs. 水平擴展 (Monolithic Architecture vs. Horizontal Scaling)

這是一個常見的面試陷阱。與現代微服務不同，**OSS Jenkins Controller (Master) 本質上是一個單體 (Monolith)**，無法像 Web Server 那樣簡單地透過 Load Balancer 進行多實例水平擴展 (Active-Active)。
This is a common interview trap. Unlike modern microservices, the **OSS Jenkins Controller (Master) is inherently a monolith**. It cannot be simply horizontally scaled (Active-Active) via a Load Balancer like a web server.

*   **OSS Jenkins**: 依賴 Active-Passive (主備模式) 或快速復原 (K8s Restart) 來達成 HA。
    **OSS Jenkins**: Relies on Active-Passive or fast recovery (K8s Restart) to achieve HA.
*   **CloudBees CI (Enterprise)**: 提供了 High Availability 模式，允許 Controller 叢集化，但這涉及複雜的分散式鎖定機制。
    **CloudBees CI (Enterprise)**: Offers High Availability modes allowing Controller clustering, but this involves complex distributed locking mechanisms.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，當被問及「如何設計一個支援千人開發團隊的 CI/CD 平台」時，Jenkins 的維運架構是核心考點。
In system design interviews or architectural planning, when asked "How to design a CI/CD platform supporting a 1000-person development team," the operational architecture of Jenkins is a key evaluation point.

## 3.1 典型的高可用架構 (Typical High Availability Architecture)

對於大多數使用 OSS Jenkins 的資深團隊，推薦的架構如下：
For most senior teams using OSS Jenkins, the recommended architecture is as follows:

1.  **Orchestrator**: Kubernetes (EKS/GKE)。
2.  **Controller**: 運行在 Pod 中，掛載 Persistent Volume (PV) 儲存 `JENKINS_HOME`。
3.  **Agents**: 動態生成的 Ephemeral Pods (用完即丟)，承擔所有構建負載。
4.  **Configuration**: 透過 Kubernetes ConfigMap 掛載 `jenkins.yaml` (JCasC)。
5.  **Storage**: 建置產物 (Artifacts) 直接上傳至 S3/GCS，不留存在 Controller。

## 3.2 可觀測性設計 (Observability Design)

如果 Jenkins 變慢，是因為 CPU 不夠？還是等待 Executor 的佇列太長？
If Jenkins slows down, is it due to insufficient CPU? Or is the queue waiting for executors too long?

*   **Metrics (Prometheus)**:
    *   `jenkins_queue_size_value`: 等待中的 Job 數量 (關鍵瓶頸指標)。
    *   `jenkins_executor_count_value`: 正在運行的 Agent 數量。
    *   `vm_cpu_load`: Controller 的負載 (若過高，UI 會卡頓)。
*   **Logs (ELK/Splunk)**: 集中收集 Master Log 與 Build Log，方便追蹤錯誤。

---

# 4. 逐步示例 (Walkthrough / Example)

本節將演示如何使用 **Jenkins Configuration as Code (JCasC)** 來取代手動 UI 設定，這是達成快速災難復原 (DR) 的基石。
This section demonstrates how to use **Jenkins Configuration as Code (JCasC)** to replace manual UI configuration, which is the cornerstone of rapid Disaster Recovery (DR).

## 4.1 問題背景 (Scenario)

你的團隊需要將 Jenkins 遷移到新的 Kubernetes Cluster。目前的 Jenkins 是多年來透過 UI 手動點擊設定的 (ClickOps)，沒人記得具體安裝了哪些 Plugin 或設定了哪些 Credential。
Your team needs to migrate Jenkins to a new Kubernetes Cluster. The current Jenkins was configured manually via UI over the years (ClickOps), and no one remembers exactly which plugins were installed or what credentials were set.

## 4.2 解決方案：JCasC (Solution: JCasC)

我們使用 `configuration-as-code` plugin，透過 YAML 檔定義系統狀態。
We use the `configuration-as-code` plugin to define the system state via a YAML file.

### Step 1: 安裝 Plugin 與匯出配置 (Install Plugin & Export Config)
在現有 Jenkins 安裝 Configuration as Code plugin，並使用 "Export Configuration" 功能取得目前的 YAML 作為基底（注意：匯出的 YAML 通常需要清理）。
Install the Configuration as Code plugin on the existing Jenkins and use the "Export Configuration" feature to get the current YAML as a baseline (Note: the exported YAML usually needs cleaning).

### Step 2: 撰寫 `jenkins.yaml` (Authoring `jenkins.yaml`)

以下是一個生產環境等級的配置範例，包含安全性與雲端 Agent 設定：
Here is a production-grade configuration example, including security and cloud agent settings:

```yaml
jenkins:
  systemMessage: "Managed by JCasC - Do not edit manually."
  numExecutors: 0 # Controller should not run builds (Security Best Practice)
  mode: EXCLUSIVE
  scmCheckoutRetryCount: 2
  
  # Security: Define Authorization Strategy
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false

  # Security: Define Security Realm (e.g., LDAP or local for demo)
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${ADMIN_PASSWORD}" # Loaded from Environment Variable

tool:
  git:
    installations:
      - name: "Default"
        home: "git"

# Cloud Agent Configuration (Kubernetes)
clouds:
  - kubernetes:
      name: "kubernetes"
      serverUrl: "https://kubernetes.default"
      namespace: "jenkins-agents"
      jenkinsUrl: "http://jenkins-service:8080"
      templates:
        - name: "golang-agent"
          label: "golang"
          containers:
            - name: "jnlp"
              image: "jenkins/inbound-agent:latest"
            - name: "golang"
              image: "golang:1.19"
              command: "cat"
              ttyEnabled: true
```

### Step 3: 部署與驗證 (Deploy & Verify)

在 Kubernetes Deployment 中，將此檔案掛載並設置環境變數：
In the Kubernetes Deployment, mount this file and set the environment variable:

```yaml
env:
  - name: CASC_JENKINS_CONFIG
    value: "/var/jenkins_home/casc_configs/jenkins.yaml"
  - name: ADMIN_PASSWORD
    valueFrom:
      secretKeyRef:
        name: jenkins-secrets
        key: admin-password
```

**為何這個做法可行？ (Why this works?)**
*   **可重現性 (Reproducibility)**: 任何新的 Jenkins 實例讀取此 YAML 後，行為將完全一致。
*   **安全性 (Security)**: 敏感資訊 (Secrets) 透過環境變數注入，不寫死在配置中。
*   **版本控制 (Version Control)**: 系統配置的變更可以透過 Pull Request 進行審查 (Audit)。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 Controller 上執行構建 (Building on the Controller)

*   **錯誤描述**: 將 `numExecutors` 設定為非 0，讓 Controller 直接執行 Job。
    **Description**: Setting `numExecutors` to non-zero, allowing the Controller to execute Jobs directly.
*   **為何不好**: 構建過程消耗大量 CPU/IO，會導致 Controller UI 無回應，甚至造成 Split-brain 或資料損毀。
    **Why it's bad**: Build processes consume heavy CPU/IO, causing the Controller UI to become unresponsive, potentially leading to split-brain or data corruption.
*   **修正**: 強制 `numExecutors: 0`，並將所有 Job 派發給 Agent。
    **Fix**: Enforce `numExecutors: 0` and delegate all Jobs to Agents.

## 5.2 忽視 Plugin 版本依賴 (Ignoring Plugin Dependencies)

*   **錯誤描述**: JCasC 檔案依賴特定 Plugin 功能，但 Docker Image 卻安裝了不相容的 Plugin 版本 (Plugin Hell)。
    **Description**: The JCasC file relies on specific plugin features, but the Docker Image has incompatible plugin versions installed (Plugin Hell).
*   **為何不好**: Jenkins 啟動失敗，且難以除錯。
    **Why it's bad**: Jenkins fails to start, and debugging is difficult.
*   **修正**: 使用 `plugins.txt` 嚴格鎖定 Plugin 版本，並在 CI 階段預先建置包含 Plugin 的 Custom Docker Image。
    **Fix**: Use `plugins.txt` to strictly pin plugin versions and pre-build a Custom Docker Image containing plugins during the CI stage.

## 5.3 備份策略過於粗糙 (Naive Backup Strategy)

*   **錯誤描述**: 僅使用 `cp` 或 `rsync` 複製運行中的 `JENKINS_HOME`。
    **Description**: Simply using `cp` or `rsync` to copy a running `JENKINS_HOME`.
*   **為何不好**: 檔案可能處於鎖定或不一致狀態，導致還原失敗。
    **Why it's bad**: Files might be locked or in an inconsistent state, leading to restore failures.
*   **修正**: 使用支援 Filesystem Snapshot 的儲存層 (如 AWS EBS Snapshot)，或使用專門的 Backup Plugin 在靜默模式下備份。
    **Fix**: Use a storage layer that supports Filesystem Snapshots (e.g., AWS EBS Snapshot), or use a dedicated Backup Plugin to backup in quiet mode.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題旨在測試候選人對 Jenkins 架構極限與維運細節的理解。
These questions are designed to test the candidate's understanding of Jenkins architectural limits and operational details.

## Q1: 如何實現 Jenkins 的 Zero-downtime 升級？
**How do you achieve Zero-downtime upgrades for Jenkins?**

*   **高分回答要點 (Key Points)**:
    *   承認 OSS Jenkins Controller 是單點 (SPOF)，真正的 Zero-downtime 很難 (除非使用 CloudBees HA)。
    *   提出 **Rolling Update 策略**：先讓 Controller 進入 "Quiet Mode" (停止接受新 Job)，等待當前 Job 完成。
    *   如果使用 Kubernetes，利用 `Readiness Probe` 確保新版 Pod 完全啟動後才切換流量。
    *   強調 Agent 與 Controller 版本相容性的重要性。

## Q2: 請設計一個 Jenkins 的災難復原 (DR) 方案，RPO < 15分鐘。
**Design a Disaster Recovery (DR) plan for Jenkins with RPO < 15 minutes.**

*   **高分回答要點 (Key Points)**:
    *   **Configuration**: JCasC 存於 Git，隨時可重新部署 (RPO ≈ 0 for config)。
    *   **Data (Build History)**: `JENKINS_HOME` 的主要數據是 Job History。使用定時 EBS Snapshots (每 10 分鐘) 或將 Build Logs 即時串流至外部 Log 系統 (ELK/S3)。
    *   **Artifacts**: 絕對不依賴 Jenkins 備份，產物必須即時上傳 Artifactory/S3。
    *   **Infrastructure**: 使用 Terraform/Helm 快速在異地 Region 重建 Cluster。

## Q3: 當 Jenkins 佇列堵塞 (Queue Jam) 時，你會如何排查與解決？
**How do you troubleshoot and resolve a Jenkins Queue Jam?**

*   **高分回答要點 (Key Points)**:
    *   **監控**: 檢查 Prometheus `jenkins_queue_size` 指標。
    *   **資源**: 檢查 Kubernetes Cluster 是否有足夠資源啟動新 Agent Pod。
    *   **標籤 (Labels)**: 檢查 Job 是否指定了不存在或錯誤的 Agent Label。
    *   **並發限制**: 檢查 Global 或 Job 層級是否設定了 `Throttle Concurrent Builds`。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Treat Jenkins as Cattle**: 透過 JCasC (`jenkins.yaml`) 實現配置即代碼，拒絕手動 ClickOps。
2.  **Controller is Fragile**: 保持 Controller 輕量化，禁止在 Controller 執行構建 (`numExecutors: 0`)。
3.  **Ephemeral Agents**: 優先使用 Kubernetes 或 Cloud Agents，用完即丟，確保環境乾淨且易於擴展。
4.  **Observability**: 必須監控 Queue Size 與 Executor Count，這是判斷系統健康與擴展需求的關鍵指標。
5.  **Disaster Recovery**: 備份策略需區分「配置」(Git)、「數據」(Snapshots) 與「產物」(S3)。

## 後續延伸 (Next Steps)
*   **Chapter 09**: **Jenkins 安全性最佳實踐 (Security Best Practices)** - 深入探討 RBAC、Credential 管理與安全掃描整合。
*   **延伸閱讀**: 研究 **Jenkins X** 或 **Tekton**，了解下一代 Cloud-Native CI/CD 是如何徹底拋棄 Controller 單體架構的。