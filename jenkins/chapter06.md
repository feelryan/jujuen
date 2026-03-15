# 建置效能優化與除錯
# Build Performance Optimization and Debugging

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，CI/CD 流水線不僅僅是自動化工具，更是開發團隊的「心跳」。緩慢或不穩定的建置會直接拉長 Feedback Loop，導致開發效率低落與 Context Switch 成本增加。本章將超越基礎配置，深入探討如何診斷並解決 Jenkins 效能瓶頸。

For senior engineers, the CI/CD pipeline is not just an automation tool; it is the "heartbeat" of the development team. Slow or unstable builds directly lengthen the Feedback Loop, resulting in reduced development velocity and increased Context Switch costs. This chapter goes beyond basic configuration to dive deep into diagnosing and resolving Jenkins performance bottlenecks.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **識別與量化瓶頸**：利用 Metrics 與 Profiling 工具精準定位是 I/O、CPU、網路還是鎖定（Locking）導致的延遲。
    **Identify and Quantify Bottlenecks:** Use Metrics and Profiling tools to pinpoint whether latency is caused by I/O, CPU, Network, or Locking.
2.  **實作進階快取策略**：在 Ephemeral Agents（如 Kubernetes Pods）中正確實作 Workspace 與 Dependency Caching。
    **Implement Advanced Caching Strategies:** Correctly implement Workspace and Dependency Caching within Ephemeral Agents (e.g., Kubernetes Pods).
3.  **優化 Artifact 管理**：理解 `stash`/`unstash` 與 `archiveArtifacts` 的代價，並設計更高效的資料傳遞機制。
    **Optimize Artifact Management:** Understand the cost of `stash`/`unstash` vs. `archiveArtifacts` and design more efficient data transfer mechanisms.
4.  **除錯分散式建置問題**：解決 Agent 連線不穩、Zombie Processes 以及資源爭奪（Resource Contention）問題。
    **Debug Distributed Build Issues:** Resolve unstable Agent connections, Zombie Processes, and Resource Contention issues.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 構建工廠 vs. 手工坊
### 2.1 Build Factory vs. Craft Workshop

將 Jenkins 視為一座現代化工廠，而非單一工匠的工作台。
Think of Jenkins as a modern factory, not a single craftsman's workbench.

-   **Master (Controller)**：是工廠經理。它負責調度、紀錄日誌、管理配置，但不應該親自鎖螺絲（執行重量級建置）。
    **Master (Controller):** The factory manager. It handles scheduling, logging, and configuration management but should not be tightening screws (executing heavy builds) itself.
-   **Agents (Executors)**：是流水線上的機器手臂。它們應該是可替換的（Fungible）、短暫的（Ephemeral），且具備平行處理能力。
    **Agents (Executors):** The robotic arms on the assembly line. They should be fungible, ephemeral, and capable of parallel processing.

### 2.2 關鍵效能指標 (KPIs)
### 2.2 Key Performance Indicators (KPIs)

在優化前，必須建立正確的心智模型來衡量效能：
Before optimizing, establish the right mental model for measuring performance:

1.  **Queue Time**：任務在隊列中等待可用 Executor 的時間。過長通常意味著資源不足或併發限制過嚴。
    **Queue Time:** Time a job waits in the queue for an available Executor. High values usually indicate insufficient resources or overly strict concurrency limits.
2.  **Build Time**：實際執行的時間。受限於 CPU/Memory、I/O 速度與依賴下載速度。
    **Build Time:** Actual execution time. Constrained by CPU/Memory, I/O speed, and dependency download speed.
3.  **Artifact Transfer Time**：在 Stage 之間或 Master 與 Agent 之間傳輸檔案的時間。這是最常被忽視的隱形殺手。
    **Artifact Transfer Time:** Time spent transferring files between Stages or between Master and Agent. This is the most commonly overlooked silent killer.

### 2.3 垂直擴展 vs. 水平擴展
### 2.3 Vertical vs. Horizontal Scaling

-   **Vertical (Scale Up)**：增加 Master 的 Heap Size 或 CPU。這對於解決 UI 緩慢有效，但無法解決建置吞吐量問題。
    **Vertical (Scale Up):** Increasing the Master's Heap Size or CPU. Effective for sluggish UI but does not solve build throughput issues.
-   **Horizontal (Scale Out)**：增加 Agent 數量。這是解決 Queue Time 的主要手段，但需配合良好的 Master-Agent 通訊架構。
    **Horizontal (Scale Out):** Increasing the number of Agents. This is the primary method to resolve Queue Time but requires a robust Master-Agent communication architecture.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 Kubernetes Native Build Architecture
### 3.1 Kubernetes Native Build Architecture

在現代 Big Tech 環境中，我們極少使用靜態 VM 作為 Agents。標準架構是 **Jenkins on Kubernetes**。
In modern Big Tech environments, we rarely use static VMs as Agents. The standard architecture is **Jenkins on Kubernetes**.

-   **設計**：每個 Build 啟動一個 Pod，Pod 內包含多個 Container（如 Maven, Node, Docker-in-Docker）。
    **Design:** Each Build spins up a Pod containing multiple Containers (e.g., Maven, Node, Docker-in-Docker).
-   **挑戰**：每次都是全新的環境（Cold Start），導致依賴套件（Dependencies）需重新下載。
    **Challenge:** Every environment is fresh (Cold Start), requiring dependencies to be re-downloaded.
-   **解法**：使用 Persistent Volume Claims (PVC) 掛載到 Pod 的特定路徑（如 `/root/.m2` 或 `/root/.npm`）作為全域快取。
    **Solution:** Use Persistent Volume Claims (PVC) mounted to specific paths in the Pod (e.g., `/root/.m2` or `/root/.npm`) as a global cache.

### 3.2 Master 負載保護
### 3.2 Master Load Protection

系統設計上，必須防止 "Thundering Herd"（驚群效應）癱瘓 Master。
From a system design perspective, you must prevent a "Thundering Herd" from paralyzing the Master.

-   **限制**：嚴格限制 Master 節點的 Executors 數量為 0。
    **Constraint:** Strictly limit the number of Executors on the Master node to 0.
-   **Offloading**：所有的 Git checkout、Artifact archiving、Log processing 都會消耗 Master 的資源（Network/Disk IO）。應盡量在 Agent 端完成預處理。
    **Offloading:** All Git checkouts, Artifact archiving, and Log processing consume Master resources (Network/Disk IO). Pre-processing should be done on the Agent side as much as possible.

---

## 4. 逐步示例：優化一個緩慢的 Java Pipeline
## 4. Walkthrough / Example: Optimizing a Slow Java Pipeline

### 情境 (Scenario)
### Scenario

一個基於 Maven 的 Spring Boot 專案，建置時間長達 25 分鐘。開發者抱怨每次改一行 code 都要等很久。
A Maven-based Spring Boot project takes 25 minutes to build. Developers complain that changing a single line of code requires a long wait.

### 步驟 1：分析瓶頸 (Analyze Bottlenecks)
### Step 1: Analyze Bottlenecks

我們安裝 "Build Time Trend" 或檢視 Pipeline Steps 視圖。發現：
We install "Build Time Trend" or view the Pipeline Steps. We discover:
-   `mvn clean install`: 15 mins (大部分在下載 jar 檔)。
    `mvn clean install`: 15 mins (mostly downloading jars).
-   `Test Execution`: 8 mins (循序執行)。
    `Test Execution`: 8 mins (sequential execution).
-   `Docker Build & Push`: 2 mins.

### 步驟 2：解決依賴下載問題 (Fix Dependency Downloads)
### Step 2: Fix Dependency Downloads

**Naive Approach:** 每次都用乾淨的 Docker image。
**Naive Approach:** Use a clean Docker image every time.

**Optimized Approach:** 掛載 Volume 快取。
**Optimized Approach:** Mount Volume Cache.

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: maven
                image: maven:3.8-openjdk-11
                command: ['cat']
                tty: true
                volumeMounts:
                - name: m2-cache
                  mountPath: /root/.m2/repository
              volumes:
              - name: m2-cache
                persistentVolumeClaim:
                  claimName: jenkins-mvn-cache-pvc
            '''
        }
    }
    stages {
        stage('Build') {
            steps {
                container('maven') {
                    // -o: offline mode (optional, if you are sure cache is warm)
                    // -T 1C: Use 1 thread per CPU core
                    sh 'mvn -T 1C clean install -DskipTests' 
                }
            }
        }
    }
}
```

*結果：Build 階段從 15 分鐘降至 3 分鐘。*
*Result: Build stage drops from 15 minutes to 3 minutes.*

### 步驟 3：平行化測試 (Parallelize Tests)
### Step 3: Parallelize Tests

利用 Jenkins 的 `parallel` 語法拆分測試套件。
Use Jenkins `parallel` syntax to split test suites.

```groovy
stage('Test') {
    parallel {
        stage('Unit Tests') {
            steps { container('maven') { sh 'mvn test -Dtest=*Unit*' } }
        }
        stage('Integration Tests') {
            steps { container('maven') { sh 'mvn test -Dtest=*IT' } }
        }
    }
}
```

*注意：需確保測試之間無資料庫狀態依賴。*
*Note: Ensure there are no database state dependencies between tests.*

### 步驟 4：優化 Artifact 傳輸 (Optimize Artifact Transfer)
### Step 4: Optimize Artifact Transfer

**問題**：很多團隊習慣在 Build stage `stash` 整個 `target/` 目錄，然後在 Docker stage `unstash`。這會導致大量網路 I/O 經過 Master。
**Issue:** Many teams habitually `stash` the entire `target/` directory in the Build stage, then `unstash` it in the Docker stage. This causes massive network I/O through the Master.

**優化**：
**Optimization:**
1.  如果 Agent 是同一個 Pod (Multi-container)，利用共享 workspace (`/home/jenkins/agent`)，不需要 stash/unstash。
    If the Agent is the same Pod (Multi-container), use the shared workspace (`/home/jenkins/agent`), no stash/unstash needed.
2.  若必須跨節點，只 stash 最終的 `.jar` 檔，而非整個 `target/`。
    If crossing nodes is necessary, only stash the final `.jar` file, not the entire `target/`.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 濫用 `stash` / `unstash` 傳輸大檔
### 5.1 Abusing `stash` / `unstash` for Large Files

-   **錯誤**：用 `stash` 傳輸幾百 MB 的 Docker Image tarball 或 `node_modules`。
    **Mistake:** Using `stash` to transfer hundreds of MBs of Docker Image tarballs or `node_modules`.
-   **後果**：Master 的 Heap Memory 暴增（因為 stash 會經過 Master），甚至導致 Master OOM (Out of Memory) 當機。
    **Consequence:** Master Heap Memory spikes (as stash passes through Master), potentially causing Master OOM (Out of Memory) crashes.
-   **修正**：使用外部儲存（如 S3, Artifactory）作為中介，或在同一 Agent 內完成相關步驟。
    **Fix:** Use external storage (like S3, Artifactory) as an intermediary, or complete related steps within the same Agent.

### 5.2 在 Master 上執行 `git checkout`
### 5.2 Running `git checkout` on Master

-   **錯誤**：在 Pipeline 定義中未指定 `agent`，或在 `agent none` 區塊外直接寫 Groovy code 操作檔案。
    **Mistake:** Not specifying an `agent` in the Pipeline definition, or writing Groovy code to manipulate files directly outside of an `agent none` block.
-   **後果**：Master 的 `.jenkins/workspace` 塞滿，磁碟 I/O 變慢。
    **Consequence:** Master's `.jenkins/workspace` fills up, slowing down disk I/O.
-   **修正**：始終確保重量級操作在 `agent { ... }` 區塊內執行。
    **Fix:** Always ensure heavy operations run inside an `agent { ... }` block.

### 5.3 忽視 Zombie Processes
### 5.3 Ignoring Zombie Processes

-   **錯誤**：Shell script 啟動了背景程序（如 `npm start &`）但在 Pipeline 結束時未殺死。
    **Mistake:** Shell scripts start background processes (e.g., `npm start &`) but fail to kill them when the Pipeline ends.
-   **後果**：Agent 節點記憶體洩漏，後續建置變慢或失敗。
    **Consequence:** Agent node memory leaks, causing subsequent builds to slow down or fail.
-   **修正**：使用 `timeout` 包裹指令，或在 Kubernetes 中利用 Pod 銷毀機制自動清理。
    **Fix:** Wrap commands with `timeout`, or rely on the Pod destruction mechanism in Kubernetes for automatic cleanup.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 我們的 Jenkins Master 每天下午都會變得很慢甚至無回應，你會如何排查？
### Q1: Our Jenkins Master becomes very slow or unresponsive every afternoon. How would you troubleshoot this?

-   **高分回答要點**：
    **Key Points for a High Score:**
    1.  **Metrics First**：檢查 JVM Metrics (Heap usage, GC activity) 與 CPU Load。
        **Metrics First:** Check JVM Metrics (Heap usage, GC activity) and CPU Load.
    2.  **Thread Dump**：分析是否有大量線程卡在 Disk I/O 或等待 Agent 連線。
        **Thread Dump:** Analyze if many threads are stuck on Disk I/O or waiting for Agent connections.
    3.  **Build Storm**：檢查是否有 Cron Job 同時觸發大量建置（Thundering Herd）。
        **Build Storm:** Check for Cron Jobs triggering massive concurrent builds (Thundering Herd).
    4.  **Disk I/O**：檢查 Master 是否正在處理大量的 Build Logs 或 Artifacts 寫入。
        **Disk I/O:** Check if the Master is handling massive Build Logs or Artifacts writes.

### Q2: 在 Microservices 架構下，如何設計 CI 以避免重複建置未修改的服務？
### Q2: In a Microservices architecture, how do you design CI to avoid rebuilding unmodified services?

-   **高分回答要點**：
    **Key Points for a High Score:**
    1.  **Change Detection**：使用 `git diff` 檢測本次 commit 影響的目錄。
        **Change Detection:** Use `git diff` to detect directories affected by the current commit.
    2.  **Build Graph**：如果是 Monorepo，使用工具（如 Bazel, Gradle Enterprise, Nx）來管理依賴圖，只建置受影響節點。
        **Build Graph:** If it's a Monorepo, use tools (like Bazel, Gradle Enterprise, Nx) to manage the dependency graph and build only affected nodes.
    3.  **Artifact Caching**：如果 Binary 已存在於 Artifactory 且 Hash 相同，則跳過建置直接下載。
        **Artifact Caching:** If the Binary exists in Artifactory with the same Hash, skip the build and download directly.

### Q3: 比較 Jenkins Shared Libraries 與 Docker Images 作為共用邏輯的優缺點？
### Q3: Compare Jenkins Shared Libraries vs. Docker Images for sharing logic. What are the pros and cons?

-   **高分回答要點**：
    **Key Points for a High Score:**
    -   **Shared Libraries (Groovy)**：
        -   *Pros*: 深度整合 Jenkins API，靈活控制流程。
        -   *Cons*: 在 Master 上執行（Sandbox 限制），效能差，難以單元測試。
    -   **Docker Images (Tools)**：
        -   *Pros*: 環境隔離，可在 Local 測試，不消耗 Master CPU。
        -   *Cons*: 只能封裝 CLI 工具，無法控制 Pipeline 流程邏輯。
    -   *結論*：流程控制用 Library，複雜運算/工具封裝用 Docker。
    -   *Conclusion*: Use Libraries for flow control, Docker for complex computation/tool encapsulation.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
### Key Takeaways

1.  **Master 是大腦，不是肌肉**：永遠不要在 Master 上執行建置。
    **Master is the brain, not the muscle:** Never run builds on the Master.
2.  **快取是效能之王**：在 Ephemeral Agents 中，正確掛載 PVC 或 Host Volume 對於依賴快取至關重要。
    **Caching is King:** In Ephemeral Agents, correctly mounting PVCs or Host Volumes is crucial for dependency caching.
3.  **減少 Master I/O**：避免 `stash` 大檔，減少 Log 輸出量。
    **Reduce Master I/O:** Avoid `stash`ing large files, reduce Log output volume.
4.  **平行化與資源隔離**：善用 `parallel` stages 與 Kubernetes Pods 的資源限制（Requests/Limits）。
    **Parallelism & Isolation:** Leverage `parallel` stages and Kubernetes Pod resource constraints (Requests/Limits).
5.  **可觀測性**：沒有 Metrics 就無法優化。監控 Queue Time 與 Build Duration。
    **Observability:** You can't optimize what you don't measure. Monitor Queue Time and Build Duration.

### 後續延伸 (Next Steps)
### Next Steps

-   **下一章**：將探討 **Jenkins Security & Governance**（安全性與治理），學習如何保護 Credentials、實作 RBAC 以及稽核 Pipeline。
    **Next Chapter:** We will explore **Jenkins Security & Governance**, learning how to protect Credentials, implement RBAC, and audit Pipelines.
-   **延伸閱讀**：研究 **Gradle Build Cache** 或 **Bazel** 的遠端快取機制，這是在大型 Monorepo 中進一步提升效能的關鍵技術。
    **Further Reading:** Research **Gradle Build Cache** or **Bazel** remote caching mechanisms, which are key technologies for further performance gains in large Monorepos.