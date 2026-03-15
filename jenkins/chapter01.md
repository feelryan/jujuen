# 1. 前言與學習目標 (Introduction and Learning Objectives)

作為資深工程師，僅僅知道如何撰寫 `Jenkinsfile` 是不夠的。在大型組織中，Jenkins 往往是一個龐大、有狀態（Stateful）且乘載關鍵任務的單點。本章將帶你深入 Jenkins 的核心架構，理解它如何調度任務、管理資源以及與 JVM 的互動。

As a Senior Engineer, knowing how to write a `Jenkinsfile` is not enough. In large organizations, Jenkins is often a massive, stateful, and mission-critical single point of failure. This chapter will take you deep into Jenkins' core architecture, understanding how it schedules tasks, manages resources, and interacts with the JVM.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準描述 Controller-Agent 架構**：理解為何「在 Master 上建置」是效能殺手，並能設計正確的擴展策略。
    **Accurately describe the Controller-Agent architecture**: Understand why "building on Master" is a performance killer and design the correct scaling strategy.
2.  **診斷系統級瓶頸**：區分是 I/O 瓶頸、CPU 飢餓還是 JVM Heap 記憶體洩漏，並進行相應的調優。
    **Diagnose system-level bottlenecks**: Distinguish between I/O bottlenecks, CPU starvation, or JVM Heap memory leaks, and apply appropriate tuning.
3.  **評估高可用性（HA）方案**：在系統設計面試中，能夠解釋 Jenkins 實現 HA 的困難點（檔案系統依賴）與解決方案。
    **Evaluate High Availability (HA) solutions**: In system design interviews, explain the difficulties of implementing HA in Jenkins (file system dependency) and the solutions.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 The "Brain" and the "Muscle" (大腦與肌肉)

Jenkins 的架構可以類比為一個繁忙的餐廳廚房。
The architecture of Jenkins can be analogized to a busy restaurant kitchen.

-   **Controller (Legacy: Master)**：這是「行政主廚」。他負責接收訂單（Webhooks/Triggers）、安排排程（Queue）、分配工作給廚師（Agents），以及記錄結果。**行政主廚不應該親自切洋蔥**。
    **Controller (Legacy: Master)**: This is the "Executive Chef." They are responsible for taking orders (Webhooks/Triggers), scheduling (Queue), assigning work to cooks (Agents), and recording results. **The Executive Chef should not be chopping onions.**

-   **Agents (Legacy: Slaves/Nodes)**：這是「線上的廚師」。他們負責實際的粗重工作：編譯程式碼、執行測試、打包 Docker image。他們可以是虛擬機、實體機，或是 Kubernetes Pods。
    **Agents (Legacy: Slaves/Nodes)**: These are the "Line Cooks." They do the actual heavy lifting: compiling code, running tests, packaging Docker images. They can be VMs, bare metal, or Kubernetes Pods.

-   **Executors**：這是每個廚師手上的「爐口」。一個 Agent 可以有多個 Executors（並行處理多個 Job），但數量受限於該 Agent 的 CPU/RAM 資源。
    **Executors**: These are the "Burners" available to each cook. An Agent can have multiple Executors (processing multiple Jobs in parallel), but the count is limited by that Agent's CPU/RAM resources.

## 2.2 檔案系統即資料庫 (File System as the Database)

與現代無狀態（Stateless）微服務不同，Jenkins 的核心設計是非常「有狀態」的。
Unlike modern stateless microservices, Jenkins' core design is heavily "stateful."

-   **XML/Config Files**：Jenkins 將幾乎所有配置（Job 定義、建置紀錄、全域設定）都以 XML 檔案形式儲存在 `JENKINS_HOME` 目錄中。
    **XML/Config Files**: Jenkins stores almost all configurations (Job definitions, build history, global settings) as XML files within the `JENKINS_HOME` directory.
-   **Implication**：這意味著 Jenkins 的效能高度依賴磁碟 I/O。如果你的 `JENKINS_HOME` 掛載在慢速的 NFS 上，整個系統都會變慢。
    **Implication**: This means Jenkins' performance is highly dependent on disk I/O. If your `JENKINS_HOME` is mounted on a slow NFS, the entire system will crawl.

## 2.3 Remoting Channel

Controller 與 Agent 之間的通訊是透過 Jenkins Remoting 協議進行的（通常基於 TCP 或 SSH 通道）。這不僅僅是傳送指令，它實際上是將 Java Class 序列化後傳送到 Agent 上執行。
Communication between the Controller and Agent happens via the Jenkins Remoting protocol (usually over TCP or SSH tunnels). This isn't just sending commands; it actually involves serializing Java Classes and sending them to the Agent for execution.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，Jenkins 通常被視為 CI/CD Pipeline 的 Orchestrator（編排者）。

In system design interviews or architectural planning, Jenkins is typically viewed as the Orchestrator of the CI/CD Pipeline.

## 3.1 單點故障與水平擴展的限制 (SPOF and Horizontal Scaling Limits)

**場景 (Scenario)**：你的團隊從 50 人擴張到 500 人，單一台 Jenkins Controller 開始變得反應遲鈍。
**Scenario**: Your team grows from 50 to 500 engineers, and the single Jenkins Controller starts becoming sluggish.

-   **問題 (Problem)**：Jenkins Controller 很難像無狀態 Web Server 那樣簡單地透過 Load Balancer 進行水平擴展（Active-Active），因為多個 Controller 無法安全地同時寫入同一個 `JENKINS_HOME`。
    **Problem**: Jenkins Controller is difficult to scale horizontally (Active-Active) like a stateless Web Server behind a Load Balancer, because multiple Controllers cannot safely write to the same `JENKINS_HOME` simultaneously.

-   **解決方案 (Solution)**：
    1.  **垂直擴展 (Vertical Scaling)**：增加 Controller 的 CPU/RAM，並使用高速 SSD。
        **Vertical Scaling**: Increase the Controller's CPU/RAM and use high-speed SSDs.
    2.  **分佈式 Master (Distributed Masters / Sharding)**：根據團隊或專案類型，建立多個獨立的 Jenkins Controllers（例如：`jenkins-mobile`, `jenkins-backend`），上方可能透過 Jenkins Operations Center (CloudBees) 來統一管理。
        **Distributed Masters / Sharding**: Create multiple independent Jenkins Controllers based on teams or project types (e.g., `jenkins-mobile`, `jenkins-backend`), potentially managed by Jenkins Operations Center (CloudBees).

## 3.2 資源隔離與安全性 (Resource Isolation and Security)

**場景 (Scenario)**：你需要為生產環境（Production）部署程式碼，同時也要跑不受信任的 Pull Request 測試。
**Scenario**: You need to deploy code to Production, but also run tests for untrusted Pull Requests.

-   **設計 (Design)**：
    -   **Prod Agents**：擁有部署權限，嚴格限制存取，僅允許 Main branch 的 Job 執行。
        **Prod Agents**: Have deployment permissions, strictly access-controlled, only allow Jobs from the Main branch to run.
    -   **Ephemeral Agents (e.g., K8s Pods)**：用於跑單元測試。每次建置啟動一個新 Pod，結束後銷毀。這確保了環境乾淨且隔離性高。
        **Ephemeral Agents (e.g., K8s Pods)**: Used for running unit tests. Spin up a new Pod for each build, destroy it afterwards. This ensures a clean environment and high isolation.

---

# 4. 逐步示例：診斷 Controller 負載過高 (Walkthrough: Diagnosing High Controller Load)

**背景 (Context)**：
使用者回報 Jenkins UI 回應極慢，甚至出現 502 Errors。監控顯示 Controller CPU 使用率 100%。

**Context**:
Users report that the Jenkins UI is extremely slow, sometimes returning 502 Errors. Monitoring shows the Controller CPU usage is at 100%.

### Step 1: 檢查是否有 Job 在 Controller 上執行 (Check for Jobs running on Controller)

這是最常見的原因。如果 Controller 設定了 executors > 0，開發者可能會不小心將重量級建置跑在 Controller 上。
This is the most common cause. If the Controller has executors > 0, developers might accidentally run heavy builds on the Controller.

**Action**:
進入 `Manage Jenkins` -> `Nodes`，檢查 `Built-In Node` (Master) 的 Executors 數量。
Go to `Manage Jenkins` -> `Nodes`, check the Executor count for the `Built-In Node` (Master).

**Fix**:
將 Executors 設為 0。強制所有 Job 必須派發到 Agents。
Set Executors to 0. Force all Jobs to be dispatched to Agents.

### Step 2: 分析 JVM Thread Dump (Analyze JVM Thread Dump)

如果沒有 Job 在 Controller 上跑，可能是某個 Plugin 卡住了，或是 Garbage Collection (GC) 風暴。
If no Jobs are running on the Controller, it could be a stuck Plugin or a Garbage Collection (GC) storm.

**Action**:
存取 `https://<jenkins-url>/threadDump`。
Access `https://<jenkins-url>/threadDump`.

**Analysis**:
尋找狀態為 `BLOCKED` 或 `WAITING` 的執行緒。
Look for threads in `BLOCKED` or `WAITING` state.
-   如果是 `hudson.model.Project.save` 相關，表示磁碟 I/O 寫入 XML 遇到瓶頸。
    If related to `hudson.model.Project.save`, it indicates a disk I/O bottleneck writing XML.
-   如果是 GC 執行緒佔用 CPU，則需要調整 JVM Heap。
    If GC threads are hogging CPU, JVM Heap tuning is required.

### Step 3: JVM 調優 (JVM Tuning)

Jenkins 是一個 Java 應用，正確的 JVM 參數至關重要。
Jenkins is a Java application; correct JVM parameters are crucial.

**Naive Approach**:
只設定 `-Xmx` (Max Heap)。
Only setting `-Xmx` (Max Heap).

**Senior Approach**:
啟用 G1GC（對於大記憶體更友善）並設定 Heap Dump 路徑以利後續除錯。
Enable G1GC (friendlier for large memory) and configure Heap Dump path for future debugging.

```bash
# Example JAVA_OPTS
java -Xmx8g -Xms8g \
     -XX:+UseG1GC \
     -XX:+ExplicitGCInvokesConcurrent \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/jenkins/heapdump.hprof \
     -jar jenkins.war
```

*註：將 Xms 與 Xmx 設為相同值可以避免 Heap resizing 帶來的效能震盪。*
*Note: Setting Xms and Xmx to the same value prevents performance jitter caused by Heap resizing.*

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 Controller 上執行建置 (Building on Controller)

-   **錯誤描述**：為了方便，直接使用 Controller 的環境來編譯程式碼。
    **Description**: Using the Controller's environment to compile code for convenience.
-   **為何不好**：編譯是 CPU 和 I/O 密集型操作。這會餓死（Starve）負責調度與 UI 回應的執行緒，導致整個 Jenkins 對所有使用者不可用。
    **Why it's bad**: Compilation is CPU and I/O intensive. It starves the threads responsible for orchestration and UI response, making Jenkins unavailable for all users.
-   **替代方案**：永遠使用 Agent（Static 或 Cloud Agents）。
    **Alternative**: Always use Agents (Static or Cloud Agents).

## 5.2 保存無限的建置歷史 (Keeping Infinite Build History)

-   **錯誤描述**：Job 設定中未勾選 "Discard old builds"。
    **Description**: Not checking "Discard old builds" in Job configuration.
-   **為何不好**：Jenkins 啟動時需要掃描 `JENKINS_HOME`。成千上萬的小檔案會導致啟動時間極長，並拖慢檔案系統效能。
    **Why it's bad**: Jenkins scans `JENKINS_HOME` on startup. Thousands of small files lead to extremely long startup times and degrade file system performance.
-   **替代方案**：強制執行 Log Rotation 策略（例如保留最近 20 次建置）。
    **Alternative**: Enforce a Log Rotation strategy (e.g., keep the last 20 builds).

## 5.3 過度依賴 Groovy Post-initialization Scripts

-   **錯誤描述**：在啟動腳本中寫入大量複雜邏輯來動態產生 Job。
    **Description**: Writing complex logic in startup scripts to dynamically generate Jobs.
-   **為何不好**：難以測試、難以版控，且會延長啟動時間。
    **Why it's bad**: Hard to test, hard to version control, and extends startup time.
-   **替代方案**：使用 Configuration as Code (JCasC) plugin。
    **Alternative**: Use the Configuration as Code (JCasC) plugin.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何設計 Jenkins 的高可用性（High Availability）架構？
**How would you design a High Availability (HA) architecture for Jenkins?**

*   **Key Points**:
    *   承認 Jenkins 本身是 Stateful 的難點。
        Acknowledge the difficulty of Jenkins being Stateful.
    *   提到 **Active-Passive (Cold/Warm Standby)**：使用共享儲存（如 AWS EFS）掛載 `JENKINS_HOME`，當主節點掛掉時，Auto Scaling Group 啟動新節點掛載同一硬碟。
        Mention **Active-Passive (Cold/Warm Standby)**: Use shared storage (like AWS EFS) to mount `JENKINS_HOME`. When the primary node fails, an Auto Scaling Group spins up a new node mounting the same drive.
    *   提到 **CloudBees CI (Enterprise)**：他們實作了 Active-Active HA（透過特殊的 Clustering 技術），這是開源版做不到的。
        Mention **CloudBees CI (Enterprise)**: They implement Active-Active HA (via proprietary clustering technology), which the open-source version cannot do.

## Q2: 當 Jenkins 變慢時，你的除錯流程是什麼？
**What is your debugging workflow when Jenkins becomes slow?**

*   **Key Points**:
    *   **Metrics First**: 查看 CPU, Memory, Disk I/O, Heap usage。
        **Metrics First**: Check CPU, Memory, Disk I/O, Heap usage.
    *   **Thread Dump**: 檢查是否有 Deadlock 或長時間運行的同步操作。
        **Thread Dump**: Check for Deadlocks or long-running synchronous operations.
    *   **Access Logs**: 檢查是否有 API 濫用（例如某個 Script 每秒輪詢 Jenkins API 100 次）。
        **Access Logs**: Check for API abuse (e.g., a script polling the Jenkins API 100 times per second).

## Q3: 比較 Jenkins Agent 的連線模式：JNLP (Inbound) vs SSH (Outbound)。
**Compare Jenkins Agent connection modes: JNLP (Inbound) vs SSH (Outbound).**

*   **Key Points**:
    *   **SSH (Outbound)**：Controller 主動連線 Agent。優點是管理集中，防火牆只需開 Agent 的 22 port。適合固定伺服器。
        **SSH (Outbound)**: Controller initiates connection to Agent. Pros: Centralized management, firewall only needs port 22 on Agent. Good for static servers.
    *   **JNLP/WebSocket (Inbound)**：Agent 主動連線 Controller。適合 Kubernetes Pods 或位於 NAT/防火牆後的機器（Controller 連不到它們，但它們連得到 Controller）。
        **JNLP/WebSocket (Inbound)**: Agent initiates connection to Controller. Good for Kubernetes Pods or machines behind NAT/Firewalls (Controller can't reach them, but they can reach the Controller).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Controller is for Orchestration**: Controller 負責指揮，Agent 負責幹活。永遠將 Controller 的 executors 設為 0。
2.  **Stateful Nature**: Jenkins 的狀態存在檔案系統中 (`JENKINS_HOME`)，這決定了它的擴展瓶頸與備份策略。
3.  **JVM Tuning**: 對於大型實例，G1GC 與 Heap Dump 設定是必須的。
4.  **Remoting**: 理解 Agent 如何透過 JNLP 或 SSH 與 Controller 溝通，有助於網路除錯。
5.  **Isolation**: 使用 Ephemeral Agents (如 Docker/K8s) 來保持環境乾淨並提高並發能力。

### 後續延伸 (Next Steps)
理解了架構之後，下一步我們將探討如何「優雅地」告訴 Jenkins 該做什麼。下一章將深入 **Pipeline as Code**，學習如何撰寫可維護、模組化的 Groovy Pipelines。

Having understood the architecture, the next step is to explore how to "gracefully" tell Jenkins what to do. The next chapter will dive into **Pipeline as Code**, learning how to write maintainable, modular Groovy Pipelines.