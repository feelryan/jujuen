# Chapter 01: GitLab 系統架構與組件原理
# Chapter 01: System Architecture and Components

## 1. 前言與學習目標
## 1. Introduction and Learning Goals

GitLab 已經從單純的 Git Repository 管理工具，演變為一個龐大的 DevSecOps 平台。對於資深工程師而言，理解其內部架構不僅是為了維運（Operations），更是為了在 System Design 面試中，能夠回答「如何設計一個大規模代碼託管與 CI/CD 系統」這類高階問題。本章將解構 GitLab 的核心組件及其互動模式。

GitLab has evolved from a simple Git repository management tool into a massive DevSecOps platform. For senior engineers, understanding its internal architecture is not just for operations, but also for tackling high-level System Design interview questions like "How to design a large-scale code hosting and CI/CD system." This chapter deconstructs GitLab's core components and their interaction patterns.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準描述請求流向（Trace Request Flow）：** 說明一個 HTTP/SSH 請求如何穿過 Nginx、Workhorse、Rails 與 Gitaly。
    **Accurately trace request flow:** Explain how an HTTP/SSH request traverses through Nginx, Workhorse, Rails, and Gitaly.
2.  **理解 Gitaly 的設計哲學（Understand Gitaly's Philosophy）：** 解釋為何 GitLab 放棄 NFS 而轉向 RPC 架構（Gitaly），以及這對分散式系統設計的啟示。
    **Understand Gitaly's design philosophy:** Explain why GitLab moved away from NFS to an RPC architecture (Gitaly) and the implications for distributed system design.
3.  **掌握非同步處理機制（Master Asynchronous Processing）：** 分析 Sidekiq 在 GitLab 中的角色，以及如何處理高併發下的 Job 隊列。
    **Master asynchronous processing:** Analyze Sidekiq's role in GitLab and how it handles job queues under high concurrency.
4.  **區分 Runner 的執行模型（Differentiate Runner Execution Models）：** 理解 GitLab Server 與 Runner 之間的 Polling 機制與隔離性設計。
    **Differentiate Runner execution models:** Understand the polling mechanism and isolation design between the GitLab Server and Runners.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

要理解 GitLab 的架構，可以將其視為一個高度特化的**微服務與單體混合架構（Hybrid Microservices/Monolith）**。雖然核心業務邏輯仍集中在 Rails Monolith 中，但關鍵的 I/O 密集型任務已被剝離。

To understand GitLab's architecture, view it as a highly specialized **Hybrid Microservices/Monolith**. While the core business logic remains centralized in the Rails Monolith, critical I/O-intensive tasks have been decoupled.

### 2.1 組件角色類比 (Component Analogy)

想像一個大型物流中心：
Imagine a large logistics hub:

*   **GitLab Workhorse (The Smart Receptionist):**
    *   **角色：** 它是位於 Nginx 之後的第一道防線。它是一個「聰明的反向代理」。
    *   **功能：** 攔截大型文件上傳（LFS、Artifacts）和 Git `git-receive-pack` 請求，避免這些慢速 I/O 阻塞 Rails 主進程。只有輕量的 API 請求和權限驗證會被轉發給 Rails。
    *   **Role:** The first line of defense behind Nginx. It is a "smart reverse proxy."
    *   **Function:** Intercepts large file uploads (LFS, Artifacts) and Git `git-receive-pack` requests to prevent slow I/O from blocking the main Rails processes. Only lightweight API requests and authentication checks are forwarded to Rails.

*   **GitLab Rails (The Brain / Manager):**
    *   **角色：** 核心單體應用（Puma）。
    *   **功能：** 處理權限驗證、資料庫讀寫、UI 渲染、Merge Request 邏輯。它不直接操作磁碟上的 Git 儲存庫，而是發號施令。
    *   **Role:** The core monolith application (Puma).
    *   **Function:** Handles authentication, database R/W, UI rendering, and Merge Request logic. It does not manipulate Git repositories on disk directly; it issues commands.

*   **Gitaly (The Warehouse Keeper):**
    *   **角色：** 專門負責 Git 資料存取的 RPC 服務。
    *   **功能：** 這是 GitLab 架構中最關鍵的轉變。過去 Rails 直接透過 NFS 讀寫 Git 檔案，導致延遲與鎖定問題（Locking issues）。現在，所有 Git 操作都封裝成 gRPC 呼叫發送給 Gitaly。
    *   **Role:** An RPC service dedicated to Git data access.
    *   **Function:** This is the most critical shift in GitLab's architecture. Previously, Rails accessed Git files directly via NFS, causing latency and locking issues. Now, all Git operations are encapsulated as gRPC calls sent to Gitaly.

*   **Sidekiq (The Back-office Workers):**
    *   **角色：** 背景任務處理器。
    *   **功能：** 處理發送 Email、觸發 CI Pipeline、更新快取等非同步任務。依賴 Redis 作為 Job Queue。
    *   **Role:** Background task processor.
    *   **Function:** Handles asynchronous tasks like sending emails, triggering CI pipelines, and updating caches. Relies on Redis as a Job Queue.

*   **GitLab Runner (The External Contractors):**
    *   **角色：** 執行 CI/CD Job 的代理程式。
    *   **功能：** 它們通常運行在獨立的機器或 K8s Pod 中，透過 API 向 GitLab Server 詢問（Polling）是否有工作要做。
    *   **Role:** Agents that execute CI/CD jobs.
    *   **Function:** They usually run on separate machines or K8s Pods, polling the GitLab Server via API to check for pending work.

### 2.2 關鍵差異：Gitaly vs. NFS
### 2.2 Key Distinction: Gitaly vs. NFS

在 System Design 面試中，這是一個經典的「存儲層演進」案例。
In System Design interviews, this is a classic "storage layer evolution" case.

| Feature | NFS (Legacy / Anti-pattern) | Gitaly (Modern Architecture) |
| :--- | :--- | :--- |
| **Access Pattern** | System calls (`open`, `read`) over network | gRPC calls (Structured Data) |
| **Latency** | High (Chatty protocol, metadata lookups) | Low (Optimized, batched operations) |
| **Caching** | OS Page Cache (Hard to control) | Application-level Cache |
| **Scalability** | Hard (File locking issues) | High (Sharding via Praefect) |

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

在 Production 環境或設計類似系統時，我們關注的是**可擴展性（Scalability）**與**隔離性（Isolation）**。

In a production environment or when designing similar systems, we focus on **Scalability** and **Isolation**.

### 3.1 請求處理架構 (Request Processing Architecture)

當我們設計一個高流量的 Git 託管服務時，必須避免單點故障與資源爭奪。

When designing a high-traffic Git hosting service, we must avoid single points of failure and resource contention.

```mermaid
graph TD
    User[User / Git Client] --> LB[Load Balancer]
    LB --> Nginx
    Nginx --> Workhorse
    
    subgraph "Application Layer"
        Workhorse -- "Large File / Git Data" --> Gitaly
        Workhorse -- "Auth / API / UI" --> Rails[Rails (Puma)]
        Rails -- "Async Jobs" --> Redis
        Redis --> Sidekiq
    end

    subgraph "Data Layer"
        Rails --> DB[(PostgreSQL)]
        Rails -- "gRPC" --> Gitaly
        Gitaly --> Disk[(Git Data)]
    end
```

*(注意：上圖為概念性文字描述，實際 Workhorse 處理 Git 請求時，會先問 Rails 權限，再與 Gitaly 建立連線)*
*(Note: The above is a conceptual description. In reality, when Workhorse handles Git requests, it first asks Rails for authorization, then establishes a connection with Gitaly.)*

### 3.2 設計考量 (Design Considerations)

1.  **Workhorse 的必要性 (The Necessity of Workhorse):**
    *   Ruby (Rails) 處理 I/O 的成本很高（GIL 限制，記憶體消耗大）。
    *   Workhorse (Go 語言編寫) 利用 `sendfile` 等系統呼叫高效處理靜態檔與 Git 封包傳輸，讓 Rails 專注於業務邏輯。
    *   Ruby (Rails) has high costs for handling I/O (GIL limitations, high memory consumption).
    *   Workhorse (written in Go) uses system calls like `sendfile` to efficiently handle static files and Git packet transmission, allowing Rails to focus on business logic.

2.  **Gitaly 的分片與高可用 (Sharding & HA with Gitaly):**
    *   單一 Gitaly 節點有磁碟上限。
    *   **Praefect** 是 Gitaly 的 Proxy 與 Router，負責將 Repository 分片（Sharding）到不同的 Gitaly 節點，並管理複本（Replication）以實現 HA。這在設計分散式存儲系統時是標準模式。
    *   A single Gitaly node has disk limits.
    *   **Praefect** acts as a proxy and router for Gitaly, responsible for sharding repositories across different Gitaly nodes and managing replication for HA. This is a standard pattern in designing distributed storage systems.

---

## 4. 逐步示例：Git Push 的生命週期
## 4. Walkthrough: Lifecycle of a Git Push

讓我們深入一個 `git push` 操作，這是系統中最複雜且資源密集的流程之一。
Let's dive into a `git push` operation, one of the most complex and resource-intensive flows in the system.

### 步驟 1: 連線與驗證 (Connection & Auth)
### Step 1: Connection & Auth

*   **User:** 執行 `git push origin master`。
*   **Nginx:** 接收請求，轉發給 Workhorse。
*   **Workhorse:** 攔截請求。它不直接處理 Git 數據，而是先向 Rails 發送一個 `pre-receive` 的 API 請求進行驗證（Authentication & Authorization）。
*   **User:** Executes `git push origin master`.
*   **Nginx:** Receives the request, forwards to Workhorse.
*   **Workhorse:** Intercepts the request. It doesn't handle Git data directly yet; it sends a `pre-receive` API request to Rails for Authentication & Authorization.

### 步驟 2: 建立通道 (Establishing Tunnel)
### Step 2: Establishing Tunnel

*   **Rails:** 驗證通過後，告訴 Workhorse：「這個 Repo 在 Gitaly 節點 A，這是存取 Token」。
*   **Workhorse:** 與 Gitaly 節點 A 建立連線，並將 User 的 Git 數據流（Stream）直接 pipe 給 Gitaly。**注意：這裡的數據流不經過 Rails。**
*   **Rails:** Upon successful auth, tells Workhorse: "This repo is on Gitaly Node A, here is the access token."
*   **Workhorse:** Establishes a connection with Gitaly Node A and pipes the user's Git data stream directly to Gitaly. **Note: The data stream does not pass through Rails.**

### 步驟 3: Gitaly 寫入與 Hooks (Gitaly Write & Hooks)
### Step 3: Gitaly Write & Hooks

*   **Gitaly:** 接收數據，執行 `git-receive-pack`。
*   **Hooks:** 在寫入完成前，Gitaly 會回頭呼叫 Rails 的內部 API (Internal API) 來執行 Server-side Hooks（例如檢查 Protected Branches）。
*   **Gitaly:** Receives data, executes `git-receive-pack`.
*   **Hooks:** Before finalizing the write, Gitaly calls back to Rails' Internal API to execute Server-side Hooks (e.g., checking Protected Branches).

### 步驟 4: 後續處理 (Post-Processing)
### Step 4: Post-Processing

*   **Gitaly:** 寫入成功，回傳狀態給 Workhorse -> User。
*   **Rails:** 收到更新通知，將「更新 Cache」、「觸發 CI Pipeline」、「發送 Email」等任務推送到 Redis。
*   **Sidekiq:** 從 Redis 取出任務並非同步執行。
*   **Gitaly:** Write successful, returns status to Workhorse -> User.
*   **Rails:** Receives update notification, pushes tasks like "Update Cache," "Trigger CI Pipeline," and "Send Email" to Redis.
*   **Sidekiq:** Picks up tasks from Redis and executes them asynchronously.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 誤用 NFS 作為主要存儲 (Misusing NFS as Primary Storage)
*   **錯誤描述：** 在大規模部署中，仍嘗試使用 NFS 掛載 Git 數據目錄給多個應用節點。
*   **後果：** 高延遲（High Latency）與「鄰居干擾（Noisy Neighbor）」效應嚴重。Git 的許多操作需要快速遍歷大量小文件，NFS 的元數據查找開銷會拖垮效能。
*   **Description:** Trying to use NFS to mount Git data directories for multiple application nodes in a large-scale deployment.
*   **Consequence:** High latency and severe "Noisy Neighbor" effects. Many Git operations require traversing many small files quickly; NFS metadata lookup overhead kills performance.
*   **Solution:** 必須遷移至 **Gitaly Cluster (Praefect)**。
*   **Solution:** Must migrate to **Gitaly Cluster (Praefect)**.

### 5.2 Sidekiq 隊列未分流 (Unpartitioned Sidekiq Queues)
*   **錯誤描述：** 所有背景任務（CI 觸發、郵件、高優先級的 Merge 操作）都混在同一個 Sidekiq 實例或隊列中處理。
*   **後果：** 當 CI Pipeline 大量觸發時，會阻塞「發送密碼重置郵件」等高優先級任務，導致使用者體驗下降。
*   **Description:** Mixing all background tasks (CI triggers, emails, high-priority merge operations) in the same Sidekiq instance or queue.
*   **Consequence:** A burst of CI pipeline triggers can block high-priority tasks like "send password reset email," degrading user experience.
*   **Solution:** 配置 Sidekiq Routing，將 `pipeline_processing` 與 `mailers` 分配到不同的 Process Group 或優先級隊列。
*   **Solution:** Configure Sidekiq Routing to assign `pipeline_processing` and `mailers` to different Process Groups or priority queues.

### 5.3 忽略 Runner 的快取機制 (Ignoring Runner Caching)
*   **錯誤描述：** 每次 CI Job 都重新下載所有依賴（Dependencies）。
*   **後果：** 浪費頻寬與時間，增加 GitLab Server/MinIO 的負載。
*   **Description:** Re-downloading all dependencies for every CI Job.
*   **Consequence:** Wastes bandwidth and time, increasing load on GitLab Server/MinIO.
*   **Solution:** 正確配置 Distributed Cache (S3/GCS) 與 Docker Layer Caching。
*   **Solution:** Properly configure Distributed Cache (S3/GCS) and Docker Layer Caching.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

在面試中，這些問題可以用來評估候選人對 CI/CD 平台架構的深度理解。

In interviews, these questions can be used to assess a candidate's deep understanding of CI/CD platform architecture.

### Q1: 如果要設計一個 GitHub Clone，你會如何處理「大文件上傳」與「Git 操作」造成的 Web Server 阻塞問題？
### Q1: If designing a GitHub Clone, how would you handle Web Server blocking caused by "Large File Uploads" and "Git Operations"?

*   **高分回答要點：**
    *   提到 **Smart Reverse Proxy** 模式（類似 GitLab Workhorse）。
    *   解釋 **Request Handoff** 機制：Web Server (Rails) 只做權限驗證，驗證後將流量直接導向存儲層或 Object Storage。
    *   提到使用 `sendfile` 避免將文件讀入 Application Memory。
*   **Key Points:**
    *   Mention the **Smart Reverse Proxy** pattern (like GitLab Workhorse).
    *   Explain the **Request Handoff** mechanism: The Web Server (Rails) only handles auth, then redirects traffic directly to the storage layer or Object Storage.
    *   Mention using `sendfile` to avoid reading files into Application Memory.

### Q2: 為什麼 GitLab 的 Runner 採用 Polling（輪詢）模式而不是 Server Push？
### Q2: Why do GitLab Runners use a Polling model instead of Server Push?

*   **高分回答要點：**
    *   **安全性 (Security)：** Runner 通常位於防火牆內或私有網路，Server 無法主動連線。Polling 允許 Runner 單向發起連線。
    *   **解耦 (Decoupling)：** Server 不需要維護 Runner 的狀態機，只需維護 Job Queue。
    *   **背壓 (Backpressure)：** Runner 可以根據自身負載決定何時請求新任務，避免被 Server 壓垮。
*   **Key Points:**
    *   **Security:** Runners are often behind firewalls or in private networks; the Server cannot initiate connections. Polling allows one-way connection initiation.
    *   **Decoupling:** The Server doesn't need to maintain the Runner's state machine, just the Job Queue.
    *   **Backpressure:** Runners can decide when to request new tasks based on their own load, preventing being overwhelmed by the Server.

### Q3: Gitaly 如何解決 NFS 的「鎖定（Locking）」問題？
### Q3: How does Gitaly solve the "Locking" issues of NFS?

*   **高分回答要點：**
    *   NFS 的文件鎖在網路不穩定時可能殘留（Stale Locks）。
    *   Gitaly 將 Git 操作序列化（Serialize）為本地進程調用。所有的寫入操作由 Gitaly 進程控制，它在本地文件系統上管理鎖，而不是依賴網路協議層的鎖。
*   **Key Points:**
    *   NFS file locks can become stale during network instability.
    *   Gitaly serializes Git operations as local process calls. All write operations are controlled by the Gitaly process, which manages locks on the local filesystem rather than relying on network protocol locks.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Workhorse** 是流量守門員，卸載了 Rails 的重型 I/O 負擔。
2.  **Gitaly** 是 Git 存儲的 RPC 介面，解決了 NFS 的延遲與擴展性瓶頸。
3.  **Sidekiq** 負責所有非同步任務，是系統響應速度的關鍵。
4.  **Runner** 透過 Polling 機制獲取任務，實現了 Server 與 Execution Environment 的安全隔離。
5.  **Praefect** 為 Gitaly 提供了分片（Sharding）與高可用（HA）能力。

### 下一步 (Next Steps)
*   **延伸閱讀：** 研究 GitLab 的 **Database Load Balancing** 機制，了解 Rails 如何在多個 PostgreSQL Read Replicas 之間分配查詢。
*   **實作建議：** 嘗試架設一個包含 Gitaly Cluster (Praefect) 的 GitLab 實例，並模擬 Gitaly 節點故障，觀察系統如何 Failover。
*   **下一章預告：** 我們將探討 **GitLab CI/CD Pipelines Deep Dive**，深入 `.gitlab-ci.yml` 的解析邏輯與 DAG（有向無環圖）的執行原理。

*   **Further Reading:** Research GitLab's **Database Load Balancing** mechanism to understand how Rails distributes queries across multiple PostgreSQL Read Replicas.
*   **Practical Suggestion:** Try setting up a GitLab instance with Gitaly Cluster (Praefect), simulate a Gitaly node failure, and observe how the system fails over.
*   **Next Chapter:** We will explore **GitLab CI/CD Pipelines Deep Dive**, digging into the parsing logic of `.gitlab-ci.yml` and the execution principles of DAGs (Directed Acyclic Graphs).