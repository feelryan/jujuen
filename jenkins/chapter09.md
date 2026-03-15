# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師（Senior Engineer）或架構師（Architect）的面試中，「設計一個 CI/CD 系統」是一個經典的 System Design 題目。這不僅考驗你對 Jenkins 內部機制的理解，更測試你如何處理分散式系統中的排程（Scheduling）、資源隔離（Isolation）與高可用性（High Availability）。

In Senior Engineer or Architect interviews, "Design a CI/CD System" is a classic System Design question. It challenges not only your understanding of Jenkins internals but also your ability to handle scheduling, resource isolation, and high availability in a distributed system.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **解構 CI/CD 平台架構**：從單體 Jenkins Master 轉向 Controller-Agent 分離與高可用架構設計。
    **Deconstruct CI/CD Platform Architecture**: Move from a monolithic Jenkins Master mindset to a Controller-Agent separation and High Availability (HA) design.
2.  **解決擴展性瓶頸**：識別 Jenkins 在大規模並發構建（Concurrent Builds）下的效能瓶頸，並提出基於 Kubernetes 或雲端彈性資源的解決方案。
    **Address Scalability Bottlenecks**: Identify performance bottlenecks in Jenkins under massive concurrent builds and propose solutions based on Kubernetes or cloud elastic resources.
3.  **設計多租戶隔離方案**：在 System Design 面試中，針對安全性與資源爭奪問題，提出可行的多租戶（Multi-tenancy）策略。
    **Design Multi-tenancy Isolation**: Propose viable multi-tenancy strategies addressing security and resource contention in System Design interviews.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 類比：中央廚房與外包廚師 (Analogy: Central Kitchen vs. Contract Chefs)

想像一個負責處理成千上萬張訂單的大型餐廳。
Imagine a large restaurant handling thousands of orders.

-   **Jenkins Controller (Master)** 是「行政主廚（Head Chef）」。他不親自切菜或煮湯，而是負責接收訂單（Git Webhooks）、決定流程（Pipeline Logic）、並指派任務給廚師。如果行政主廚倒下，整個廚房就會停擺（SPOF - Single Point of Failure）。
    The **Jenkins Controller (Master)** is the "Head Chef." He doesn't chop vegetables or cook soup himself; instead, he receives orders (Git Webhooks), decides the process (Pipeline Logic), and assigns tasks to cooks. If the Head Chef collapses, the entire kitchen halts (SPOF - Single Point of Failure).

-   **Jenkins Agents (Workers)** 是「約聘廚師（Contract Chefs）」。他們負責實際的髒活累活（Build, Test, Deploy）。在現代架構中，這些廚師應該是「隨叫隨到且用完即丟」的（Ephemeral），就像 Uber 司機一樣，而不是永久駐留在廚房佔用空間。
    **Jenkins Agents (Workers)** are the "Contract Chefs." They do the actual heavy lifting (Build, Test, Deploy). In modern architectures, these chefs should be "on-demand and disposable" (Ephemeral), like Uber drivers, rather than permanently occupying space in the kitchen.

## 2.2 正規定義：分散式任務排程引擎 (Formal Definition: Distributed Task Scheduling Engine)

從系統設計的角度來看，Jenkins 本質上是一個**專門處理有向無環圖（DAG）依賴關係的分散式任務排程器**。
From a system design perspective, Jenkins is essentially a **distributed task scheduler specialized in handling Directed Acyclic Graph (DAG) dependencies**.

它與一般 Job Scheduler（如 Cron 或 Celery）的主要差異在於：
The main differences from a general Job Scheduler (like Cron or Celery) are:

1.  **Context Awareness**: 它需要維護大量的 Context（原始碼版本、Artifacts、測試報告）。
    It needs to maintain significant Context (source code versions, Artifacts, test reports).
2.  **Complex Workflow**: 任務之間有強依賴與狀態傳遞（Stage A 成功才能跑 Stage B）。
    Tasks have strong dependencies and state passing (Stage B runs only if Stage A succeeds).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在設計一個支援千人規模研發團隊的 CI/CD 平台時，我們不能只依賴「安裝一個 Jenkins」這種運維思維，而必須採用架構師視角。
When designing a CI/CD platform for an R&D team of thousands, we cannot rely on the operational mindset of simply "installing Jenkins." We must adopt an architect's perspective.

## 3.1 系統架構中的角色 (Roles in System Architecture)

在 System Design 面試中，你需要畫出以下組件：
In a System Design interview, you need to diagram the following components:

1.  **Event Ingestion (Webhook Handler)**: 接收 GitHub/GitLab 的事件。為了避免 Jenkins Master 被瞬間流量（Thundering Herd）打掛，通常會在此層加入一個 Queue (e.g., Kafka/Redis)。
    Receives events from GitHub/GitLab. To prevent the Jenkins Master from being overwhelmed by traffic spikes (Thundering Herd), a Queue (e.g., Kafka/Redis) is often introduced at this layer.
2.  **Control Plane (Orchestrator)**: 負責解析 Jenkinsfile，管理 Queue，並向 Resource Manager 請求計算資源。
    Responsible for parsing the Jenkinsfile, managing the Queue, and requesting compute resources from the Resource Manager.
3.  **Data Plane (Execution Environment)**: 實際執行構建的環境。最佳實踐是使用 Kubernetes Pods 或 AWS EC2 Spot Instances。
    The environment where the build actually executes. Best practice involves using Kubernetes Pods or AWS EC2 Spot Instances.
4.  **Artifact Repository**: 存放建置產物（Binary, Docker Images）。Jenkins 不應作為檔案伺服器。
    Stores build outputs (Binaries, Docker Images). Jenkins should not act as a file server.

## 3.2 可擴充性與可靠性 (Scalability & Reliability)

-   **Vertical Scalability (Scale Up)**: Jenkins Master 是著名的記憶體怪獸。對於單體 Master，增加 RAM 是最簡單的短期解法，但有上限。
    **Vertical Scalability (Scale Up)**: The Jenkins Master is a notorious memory hog. For a monolithic Master, adding RAM is the simplest short-term fix, but it has a ceiling.
-   **Horizontal Scalability (Scale Down)**:
    -   **Agents**: 容易水平擴展。
        **Agents**: Easy to scale horizontally.
    -   **Masters**: 困難。Jenkins 傳統上不支援 Active-Active 高可用模式（除非使用 CloudBees 等企業版特定功能）。常見的設計模式是 **Sharding**（分片），即為不同的團隊或專案群組建置獨立的 Jenkins Master。
        **Masters**: Difficult. Jenkins traditionally does not support Active-Active HA (unless using enterprise features like CloudBees). The common design pattern is **Sharding**, creating independent Jenkins Masters for different teams or project groups.

---

# 4. 逐步示例：設計企業級 CI/CD 平台 (Walkthrough: Designing an Enterprise CI/CD Platform)

**情境 (Scenario)**:
你需要為一家擁有 1,000 名工程師的公司設計 CI/CD 系統。每天有 5,000 次 Commits，高峰期會有 500 個並發構建（Concurrent Builds）。
You need to design a CI/CD system for a company with 1,000 engineers. There are 5,000 commits daily, with 500 concurrent builds at peak times.

### Step 1: 需求分析 (Requirements Analysis)

-   **Functional**: 支援 Git Webhook 觸發、Pipeline 定義（Code）、儲存 Logs 與 Artifacts。
    **Functional**: Support Git Webhook triggers, Pipeline definitions (as Code), and storage of Logs and Artifacts.
-   **Non-Functional**:
    -   **High Availability**: Master 故障時，服務需在 5 分鐘內恢復。
        **High Availability**: Service must recover within 5 minutes if the Master fails.
    -   **Isolation**: Team A 的構建不應耗盡 Team B 的資源或讀取其 Secrets。
        **Isolation**: Team A's build should not exhaust Team B's resources or read their Secrets.
    -   **Scalability**: 支援高峰期彈性擴容。
        **Scalability**: Support elastic scaling during peak hours.

### Step 2: 架構設計演進 (Architecture Evolution)

#### Phase 1: Naive Approach (單體架構 / Monolithic)
一個巨大的 Jenkins Master，所有構建都在 Master 節點上執行。
A massive Jenkins Master where all builds execute on the Master node.

*   **Why it fails**: 安全性極差（構建腳本可讀取 Master 檔案系統）；資源競爭導致 UI 卡頓；單點故障。
    **Why it fails**: Poor security (build scripts can read the Master file system); resource contention causes UI lag; Single Point of Failure.

#### Phase 2: Master-Agent Separation (標準架構 / Standard)
一個 Master 連接多個固定 VM Agents。
One Master connected to multiple fixed VM Agents.

*   **Pros**: 解決了安全性與 UI 卡頓問題。
    **Pros**: Solves security and UI lag issues.
*   **Cons**: 資源浪費（閒置時 VM 仍在計費）；維護成本高（需定期更新 Agent OS/Tools）；佇列積壓（Queue backlog）時無法快速擴容。
    **Cons**: Wasted resources (VMs billable even when idle); high maintenance (regular Agent OS/Tools updates required); inability to scale fast during queue backlogs.

#### Phase 3: Containerized & Ephemeral (現代架構 / Modern Design)

這是你在面試中應提出的目標架構。
This is the target architecture you should propose in an interview.

1.  **Orchestrator**: Jenkins Master 部署在 K8s StatefulSet 中，掛載 PVC (Persistent Volume) 儲存設定 XML。
    **Orchestrator**: Jenkins Master deployed in a K8s StatefulSet, mounting a PVC (Persistent Volume) to store configuration XMLs.
2.  **Compute**: 使用 `Kubernetes Plugin`。當 Job 啟動時，動態生成一個 Pod 作為 Agent。Job 結束，Pod 銷毀。
    **Compute**: Use the `Kubernetes Plugin`. When a Job starts, dynamically spin up a Pod as an Agent. When the Job ends, the Pod is destroyed.
3.  **Storage Offloading**:
    -   **Logs**: 串流至 Elasticsearch/Splunk，不存於 Master Disk。
        **Logs**: Stream to Elasticsearch/Splunk, do not store on Master Disk.
    -   **Artifacts**: 上傳至 S3/Artifactory，Master 只存連結。
        **Artifacts**: Upload to S3/Artifactory, Master only stores links.

### Step 3: 處理「驚群效應」與 Master 瓶頸 (Handling Thundering Herd & Master Bottleneck)

如果 1,000 個 Webhooks 同時到達，Jenkins Master 的 HTTP 線程池會耗盡。
If 1,000 Webhooks arrive simultaneously, the Jenkins Master's HTTP thread pool will be exhausted.

**Solution**:
引入一個輕量級的中介層（Middleware），例如基於 Go/Node.js 的 Webhook Receiver。
Introduce a lightweight middleware, such as a Webhook Receiver based on Go/Node.js.

```text
[GitHub] -> [Webhook Receiver (Scale Set)] -> [Message Queue (Kafka)] -> [Jenkins Consumer] -> [Jenkins Master]
```

1.  **Webhook Receiver**: 驗證 Signature，過濾無效請求（如 `[skip ci]`），將有效事件推入 Kafka。
    **Webhook Receiver**: Validates signatures, filters invalid requests (e.g., `[skip ci]`), and pushes valid events to Kafka.
2.  **Jenkins Consumer**: 根據 Master 的負載狀況，慢慢將任務餵給 Jenkins（Rate Limiting）。
    **Jenkins Consumer**: Feeds tasks to Jenkins slowly based on the Master's load status (Rate Limiting).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 Master 上儲存 Build Logs (Storing Build Logs on Master)
-   **Anti-pattern**: 依賴 Jenkins 預設行為，將所有 Console Output 存為 Master 磁碟上的小檔案。
    **Anti-pattern**: Relying on Jenkins' default behavior to store all Console Output as small files on the Master disk.
-   **Consequence**: Inode 耗盡，磁碟 I/O 成為瓶頸，導致 Master UI 無回應。
    **Consequence**: Inode exhaustion, disk I/O becomes a bottleneck, causing the Master UI to become unresponsive.
-   **Better Approach**: 使用 External Logging Plugins（如 CloudWatch Logs, ELK stack）將 Log 寫入外部系統。
    **Better Approach**: Use External Logging Plugins (e.g., CloudWatch Logs, ELK stack) to write logs to external systems.

## 5.2 複雜的 Groovy 邏輯 (Complex Groovy Logic in Pipelines)
-   **Anti-pattern**: 在 `Jenkinsfile` 中撰寫數百行的 Groovy 程式碼來處理複雜運算或 API 呼叫。
    **Anti-pattern**: Writing hundreds of lines of Groovy code in `Jenkinsfile` to handle complex calculations or API calls.
-   **Consequence**: 這些 Groovy 程式碼是在 Master 的 JVM 上執行的（CPS 轉換），極度消耗 Master CPU 與記憶體。
    **Consequence**: This Groovy code runs on the Master's JVM (CPS transformation), heavily consuming Master CPU and memory.
-   **Better Approach**: 將邏輯封裝在 Python/Bash script 或 Docker Image 中，Pipeline 只負責呼叫 `sh './script.py'`。這將負載轉移到了 Agent。
    **Better Approach**: Encapsulate logic in Python/Bash scripts or Docker Images; the Pipeline only calls `sh './script.py'`. This offloads the burden to the Agent.

## 5.3 忽略插件管理 (Ignoring Plugin Management)
-   **Anti-pattern**: 安裝過多插件，且未鎖定版本。
    **Anti-pattern**: Installing too many plugins without version locking.
-   **Consequence**: "Dependency Hell"，系統升級時崩潰，且增加攻擊面（Attack Surface）。
    **Consequence**: "Dependency Hell," system crashes during upgrades, and increased Attack Surface.
-   **Better Approach**: 使用 "Configuration as Code" (JCasC) 並建立一個經過審核的 "Golden Image" Docker 映像檔，包含預先安裝好的插件列表。
    **Better Approach**: Use "Configuration as Code" (JCasC) and build a vetted "Golden Image" Docker image containing a pre-installed list of plugins.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

在面試中，你可以利用這些問題來展示你的資深程度：
In an interview, you can use these questions to demonstrate your seniority:

## Q1: 如何實現 Jenkins 的高可用性（HA）？
**How do you implement High Availability (HA) for Jenkins?**

-   **Key Points**:
    -   承認 Jenkins 開源版是 Stateful 的，原生不支援 Active-Active。
        Acknowledge that Jenkins OSS is stateful and does not natively support Active-Active.
    -   提出 **Active-Passive** 方案：使用 K8s Deployment (Replicas=1) + PVC。當 Pod 掛掉，K8s 會在另一節點重啟並掛載同一 PVC。
        Propose an **Active-Passive** solution: Use K8s Deployment (Replicas=1) + PVC. When the Pod dies, K8s restarts it on another node mounting the same PVC.
    -   提及 **Configuration as Code (JCasC)**：即使儲存損壞，也能從 Git 快速重建 Master 設定。
        Mention **Configuration as Code (JCasC)**: Even if storage is corrupted, Master configuration can be quickly rebuilt from Git.

## Q2: 如何處理不同團隊間的依賴與隔離？
**How do you handle dependencies and isolation between different teams?**

-   **Key Points**:
    -   **Resource Isolation**: 使用 K8s Namespaces 區分 Agents。
        **Resource Isolation**: Use K8s Namespaces to segregate Agents.
    -   **Network Isolation**: 使用 Network Policies 防止測試中的惡意程式碼攻擊內部網路。
        **Network Isolation**: Use Network Policies to prevent malicious code in tests from attacking the internal network.
    -   **Controller Sharding**: 對於超大型組織，不要試圖用一個 Master 統治所有，而是提供 "Jenkins as a Service"，為每個部門自動佈建獨立的 Master。
        **Controller Sharding**: For very large organizations, don't try to rule them all with one Master. Instead, provide "Jenkins as a Service," automatically provisioning independent Masters for each department.

## Q3: 為什麼選擇 Jenkins 而不是 GitHub Actions 或 GitLab CI？
**Why choose Jenkins over GitHub Actions or GitLab CI?**

-   **Key Points**:
    -   **Flexibility**: Jenkins 擁有最強大的插件生態系，適合整合 Legacy 系統或高度客製化的流程。
        **Flexibility**: Jenkins has the most powerful plugin ecosystem, suitable for integrating Legacy systems or highly customized workflows.
    -   **Data Sovereignty**: 對於金融/政府單位，完全的地端（On-premise）控制與網路隔離是必須的。
        **Data Sovereignty**: For finance/government sectors, complete on-premise control and network isolation are mandatory.
    -   **Cost**: 在極大規模下，自建 K8s Agents 的成本通常低於 SaaS CI 的 per-minute 計費。
        **Cost**: At massive scale, the cost of self-hosted K8s Agents is often lower than SaaS CI per-minute billing.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Master is the Brain, not the Muscle**: 永遠將繁重的運算（Builds, Scripts）卸載到 Agents。
    **Master is the Brain, not the Muscle**: Always offload heavy computation (Builds, Scripts) to Agents.
2.  **Ephemeral Agents**: 擁抱容器化、短生命週期的 Agents 以提升資源利用率與隔離性。
    **Ephemeral Agents**: Embrace containerized, short-lived Agents to improve resource utilization and isolation.
3.  **State Externalization**: 盡可能將 Log、Artifacts、Configuration 移出 Master 的檔案系統。
    **State Externalization**: Move Logs, Artifacts, and Configuration out of the Master's file system whenever possible.
4.  **Sharding Strategy**: 當單一 Master 達到垂直擴展上限時，按團隊或專案進行分片（Sharding）。
    **Sharding Strategy**: When a single Master hits its vertical scaling limit, shard by team or project.
5.  **Middleware for Scaling**: 在 Webhook 與 Jenkins 之間引入 Queue 來削峰填谷。
    **Middleware for Scaling**: Introduce a Queue between Webhooks and Jenkins to smooth out traffic spikes.

## 後續延伸 (Next Steps)
-   **Advanced Security**: 研究如何整合 HashiCorp Vault 來管理 Jenkins Credentials，實現動態 Secrets。
    **Advanced Security**: Research how to integrate HashiCorp Vault to manage Jenkins Credentials for dynamic secrets.
-   **Observability**: 實作 Prometheus + Grafana 監控 Jenkins JVM Metrics 與 Build Queue Latency。
    **Observability**: Implement Prometheus + Grafana to monitor Jenkins JVM Metrics and Build Queue Latency.
-   **Next Chapter**: 進入 **Chapter 10: Pipeline as Code Patterns**，深入探討如何編寫可重用、模組化的 Shared Libraries。
    **Next Chapter**: Move to **Chapter 10: Pipeline as Code Patterns** to dive deep into writing reusable, modular Shared Libraries.