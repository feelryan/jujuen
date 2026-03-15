# 1. 前言與學習目標 (Introduction and Learning Goals)

在資深工程師的職涯中，掌握 Docker 指令僅是基礎；真正的挑戰在於如何運用容器設計模式（Container Design Patterns）來解決複雜的分散式系統問題。本章將超越單一容器的視角，探討多容器協作的架構模式，以及如何將傳統應用程式現代化。

In the career of a Senior Software Engineer, mastering Docker commands is merely the baseline; the real challenge lies in applying Container Design Patterns to solve complex distributed system problems. This chapter moves beyond the single-container perspective to explore architectural patterns for multi-container collaboration and how to modernize legacy applications.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用四種核心模式**：精準區分並實作 Sidecar、Ambassador、Adapter 與 Init Container 模式，以解決日誌收集、網路代理與初始化依賴問題。
    **Apply four core patterns**: Accurately distinguish and implement Sidecar, Ambassador, Adapter, and Init Container patterns to solve logging, network proxying, and initialization dependency issues.
2.  **重構 Legacy 系統**：診斷傳統單體應用（Monolith）與 12-Factor App 原則的落差，並設計容器化遷移路徑。
    **Refactor Legacy Systems**: Diagnose gaps between traditional monolithic applications and 12-Factor App principles, and design a containerization migration path.
3.  **解耦關注點（Separation of Concerns）**：在系統設計面試中，展示如何透過容器組合（Container Composition）將業務邏輯與基礎設施邏輯（如監控、安全性）分離。
    **Decouple Separation of Concerns**: Demonstrate in system design interviews how to separate business logic from infrastructure logic (e.g., monitoring, security) through container composition.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 "Pod" 的心智模型 (The Mental Model of a "Pod")

雖然 Docker 本身（在 Swarm 或 Compose 中）沒有 "Pod" 的原生概念，但在架構設計時，我們應借鑑 Kubernetes 的 **Pod** 概念：**一組共享生命週期、網路與儲存資源的容器集合**。這與傳統 VM 時代「一台伺服器跑多個 Process」的概念類似，但現在每個 Process 都有獨立的 Filesystem 與 Environment，僅共享必要的資源。

Although Docker itself (in Swarm or Compose) does not have a native concept of a "Pod," in architectural design, we should borrow the **Pod** concept from Kubernetes: **a group of containers sharing lifecycle, network, and storage resources**. This is similar to the traditional VM era concept of "running multiple processes on one server," but now each process has an independent filesystem and environment, sharing only necessary resources.

## 2.2 四大設計模式 (The Four Major Design Patterns)

我們可以用一個「外交團隊」來類比這些模式：
We can use a "Diplomatic Team" analogy to explain these patterns:

1.  **Sidecar Pattern（邊車模式）**
    *   **定義**：輔助主應用程式容器，擴充功能而不改變主程式碼。
    *   **類比**：摩托車的邊車。主駕駛（App）專注騎車（業務邏輯），邊車乘客（Sidecar）負責導航或攻擊（日誌、同步配置）。
    *   **Definition**: Assists the main application container, extending functionality without changing the main code.
    *   **Analogy**: A motorcycle sidecar. The rider (App) focuses on driving (business logic), while the passenger (Sidecar) handles navigation or combat (logging, config syncing).

2.  **Ambassador Pattern（大使模式）**
    *   **定義**：一種特殊的 Sidecar，專門負責代理（Proxy）與外部世界的連線。
    *   **類比**：外交大使。國家元首（App）不直接與外國交涉，而是透過大使（Ambassador）處理語言翻譯與協議（連線到 Sharded DB、Service Mesh Proxy）。
    *   **Definition**: A specific type of Sidecar dedicated to proxying connections with the outside world.
    *   **Analogy**: A diplomat. The head of state (App) doesn't negotiate directly with foreign countries but uses an Ambassador to handle translation and protocols (connecting to Sharded DB, Service Mesh Proxy).

3.  **Adapter Pattern（轉接器模式）**
    *   **定義**：標準化輸出。將異質的應用程式介面轉換為統一格式供外部系統使用。
    *   **類比**：萬用轉接頭。無論電器（App）的插頭形狀為何，轉接頭（Adapter）都將其轉為標準插座格式（統一監控 Metrics 格式）。
    *   **Definition**: Standardizes output. Transforms heterogeneous application interfaces into a unified format for external systems.
    *   **Analogy**: A universal power adapter. Regardless of the appliance's (App) plug shape, the Adapter converts it to a standard socket format (unifying monitoring metrics formats).

4.  **Init Container（初始化容器）**
    *   **定義**：在主應用啟動前執行，完成任務後即終止。
    *   **類比**：場地佈置組。在會議（App）開始前，先排好椅子、測試麥克風（DB Migration、等待依賴服務上線），做完就離場。
    *   **Definition**: Runs before the main application starts and terminates upon completion.
    *   **Analogy**: The venue setup crew. Before the conference (App) starts, they arrange chairs and test microphones (DB Migration, waiting for dependencies), then leave.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與 System Design 面試中，這些模式解決了 **Cross-cutting Concerns（橫切關注點）** 的問題。

In production environments and system design interviews, these patterns solve the problem of **Cross-cutting Concerns**.

## 3.1 Legacy 系統容器化 (Containerizing Legacy Systems)

當你需要將一個無法修改程式碼（或修改成本極高）的 Legacy App 搬上雲端時：
When you need to migrate a Legacy App to the cloud where code modification is impossible (or too costly):

*   **日誌問題 (Logging)**: Legacy App 寫入本地檔案 `/var/log/app.log`。
    *   *Solution*: 使用 **Sidecar** 運行 Filebeat 或 Fluentd，掛載同一個 Volume，讀取日誌並轉發至 ELK/Splunk。這符合 12-Factor App 的 "Treat logs as event streams"。
*   **配置問題 (Configuration)**: Legacy App 依賴固定的設定檔格式。
    *   *Solution*: 使用 **Init Container** 根據環境變數（Env Vars）動態生成該設定檔，再啟動主程式。

## 3.2 服務網格與安全性 (Service Mesh & Security)

在微服務架構中，我們不希望每個服務都實作 mTLS、Retries 或 Circuit Breaking。
In a microservices architecture, we don't want every service to implement mTLS, Retries, or Circuit Breaking.

*   **Ambassador/Sidecar**: Envoy Proxy 或 Istio Sidecar 就是典型的應用。主程式只管 `localhost:8080` 通訊，Sidecar 負責加密流量並路由到正確的下游服務。
    *   **Ambassador/Sidecar**: Envoy Proxy or Istio Sidecar are classic examples. The main app only communicates with `localhost:8080`, while the Sidecar handles traffic encryption and routing to the correct downstream service.

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境：Legacy Python App 的現代化改造
## Scenario: Modernizing a Legacy Python App

**背景 (Background)**:
你有一個舊的 Python 應用，它只會將日誌寫入 `/logs/app.log`，並且啟動時需要等待 MySQL 資料庫完全就緒，否則會崩潰。你需要將其容器化並部署，且不能修改 Python 原始碼。

You have an old Python application that only writes logs to `/logs/app.log` and crashes if the MySQL database is not fully ready upon startup. You need to containerize and deploy it without modifying the Python source code.

### 步驟 1: 定義 Init Container 處理依賴 (Step 1: Define Init Container for Dependencies)

我們使用一個輕量級的容器來檢查 DB 連線。
We use a lightweight container to check the DB connection.

### 步驟 2: 定義 Sidecar 處理日誌 (Step 2: Define Sidecar for Logging)

我們使用 `busybox` (模擬 log agent) 來 `tail -f` 共享的日誌檔案，將其導向標準輸出 (stdout)，以便 Docker Daemon 收集。
We use `busybox` (simulating a log agent) to `tail -f` the shared log file, directing it to standard output (stdout) for the Docker Daemon to collect.

### 實作配置 (Implementation Config)

以下是 `docker-compose.yml` 的實作範例：
Here is an implementation example using `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # 模擬的 Legacy App
  legacy-app:
    image: python:3.9-slim
    # 模擬寫入日誌到檔案的行為
    command: sh -c "while true; do echo 'App processing...' >> /var/log/myapp/app.log; sleep 2; done"
    volumes:
      - app-logs:/var/log/myapp
    depends_on:
      db-check:
        condition: service_completed_successfully

  # Pattern: Init Container
  # 確保 DB 真的準備好 (TCP level check)
  db-check:
    image: busybox
    command: sh -c "echo 'Waiting for DB...'; sleep 5; echo 'DB is up!'"
    # 在真實場景中，這裡會使用 nc -z db 3306 迴圈檢查

  # Pattern: Sidecar (Adapter/Log Forwarder)
  # 將檔案日誌轉換為 Docker 標準輸出流
  log-sidecar:
    image: busybox
    volumes:
      - app-logs:/var/log/myapp
    # 讀取共享 Volume 中的檔案並輸出到 stdout
    command: sh -c "tail -f /var/log/myapp/app.log"
    depends_on:
      - legacy-app

volumes:
  app-logs:
```

### 分析 (Analysis)

1.  **解耦 (Decoupling)**: `legacy-app` 不需要知道 Docker 或是 logging driver 的存在，它只需照舊寫檔案。
    **Decoupling**: The `legacy-app` doesn't need to know about Docker or logging drivers; it just writes to files as usual.
2.  **生命週期 (Lifecycle)**: `db-check` 確保了啟動順序的正確性（比單純的 `depends_on` 更可靠，因為它可以執行邏輯檢查）。
    **Lifecycle**: `db-check` ensures the correct startup order (more reliable than simple `depends_on` because it can run logical checks).
3.  **可觀測性 (Observability)**: `log-sidecar` 讓 `docker logs log-sidecar` 可以直接看到應用日誌，符合雲原生標準。
    **Observability**: `log-sidecar` allows `docker logs log-sidecar` to directly view application logs, complying with cloud-native standards.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 胖容器 (The Fat Container / "God Container")

*   **錯誤描述**：在同一個 Dockerfile 中安裝 Supervisor 或 Systemd，並同時啟動 Nginx、App、Cron 和 Log Agent。
*   **為何不好**：違反單一職責原則（Single Responsibility Principle）。難以擴展（Scale），難以除錯（如果容器掛了，是因為 App 還是 Cron？），且破壞了容器的輕量級優勢。
*   **正確做法**：將 Log Agent 拆分為 Sidecar，Cron 拆分為獨立的 CronJob 容器或使用 K8s CronJob。

*   **Description**: Installing Supervisor or Systemd in a single Dockerfile and starting Nginx, App, Cron, and Log Agent simultaneously.
*   **Why it's bad**: Violates the Single Responsibility Principle. Hard to scale, hard to debug (if the container dies, was it the App or Cron?), and destroys the lightweight advantage of containers.
*   **Correction**: Split the Log Agent into a Sidecar, and Cron into a separate CronJob container or use K8s CronJob.

## 5.2 忽視 Sidecar 的生命週期 (Ignoring Sidecar Lifecycle)

*   **錯誤描述**：主應用程式崩潰重啟，但 Sidecar 仍在運行，導致舊的 Sidecar 佔用資源或鎖定檔案；或者主應用程式結束（如 Batch Job），Sidecar 卻不結束，導致 Task 永遠顯示 "Running"。
*   **為何不好**：資源洩漏，CI/CD Pipeline 卡住。
*   **正確做法**：在 Kubernetes 中有 Job 相關設定可處理；在純 Docker 中，需編寫腳本讓 Sidecar 監控主 Process，或共享 Process Namespace 讓 Sidecar 能感知主 Process 死亡。

*   **Description**: The main app crashes and restarts, but the Sidecar keeps running, causing resource hogging or file locks; or the main app finishes (e.g., Batch Job), but the Sidecar doesn't exit, causing the Task to stay "Running" forever.
*   **Why it's bad**: Resource leaks, stuck CI/CD pipelines.
*   **Correction**: Kubernetes has Job settings for this; in pure Docker, script the Sidecar to monitor the main process, or share the Process Namespace so the Sidecar can detect the main process death.

## 5.3 在 Init Container 中執行過久的操作 (Long-running Init Containers)

*   **錯誤描述**：在 Init Container 中執行大型資料庫 Schema Migration 或資料備份。
*   **為何不好**：會阻斷主應用啟動，導致部署超時（Deployment Timeout）或服務長時間不可用。
*   **正確做法**：Init Container 僅做快速檢查或輕量設定。大型 Migration 應透過獨立的 Job 或 Pipeline 步驟執行。

*   **Description**: Performing large database schema migrations or backups inside an Init Container.
*   **Why it's bad**: Blocks the main app startup, causing deployment timeouts or extended service unavailability.
*   **Correction**: Init Containers should only perform quick checks or lightweight setup. Large migrations should be executed via separate Jobs or Pipeline steps.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你會選擇將功能（如 Logging）做成 Library 還是 Sidecar？
## Q1: Would you choose to implement functionality (like Logging) as a Library or a Sidecar?

*   **高分回答要點 (Key Points for a High Score)**:
    *   **權衡 (Trade-off)**: Library 效能較好（In-process），但與語言耦合（Coupled），升級需重新編譯所有服務。
    *   **Sidecar 優勢**: 語言無關（Language Agnostic），基礎設施團隊可獨立升級 Sidecar 而不需業務團隊介入（Decoupling）。
    *   **情境**: 對於多語言（Polyglot）環境或 Service Mesh，Sidecar 是首選；對於極致低延遲需求，Library 可能更好。
    *   **Trade-off**: Libraries have better performance (In-process) but are coupled to the language; upgrades require recompiling all services.
    *   **Sidecar Advantage**: Language Agnostic; infrastructure teams can upgrade Sidecars independently without business team intervention (Decoupling).
    *   **Context**: For Polyglot environments or Service Mesh, Sidecar is preferred; for ultra-low latency requirements, a Library might be better.

## Q2: 如何將一個不符合 12-Factor 的 Legacy App 容器化？
## Q2: How do you containerize a Legacy App that doesn't comply with 12-Factor App principles?

*   **高分回答要點 (Key Points for a High Score)**:
    *   **Config**: 使用 Entrypoint script 或 Init Container 將環境變數（Env Vars）注入/覆寫到舊的 Config 檔案中。
    *   **Logs**: 使用 Sidecar (`tail -f`) 將檔案日誌轉發到 Stdout，或使用 Volume Mount 讓外部 Agent 收集。
    *   **State**: 識別並移出所有本地狀態（Local State）到外部儲存（Redis/S3/DB），確保容器是 Stateless 的。
    *   **Config**: Use Entrypoint scripts or Init Containers to inject/overwrite Environment Variables into old Config files.
    *   **Logs**: Use a Sidecar (`tail -f`) to forward file logs to Stdout, or use Volume Mounts for external agents to collect.
    *   **State**: Identify and move all Local State to external storage (Redis/S3/DB) to ensure the container is Stateless.

## Q3: 什麼是 Ambassador Pattern？它與標準的反向代理有何不同？
## Q3: What is the Ambassador Pattern? How does it differ from a standard Reverse Proxy?

*   **高分回答要點 (Key Points for a High Score)**:
    *   **位置**: 反向代理（如 Nginx Ingress）通常位於系統邊緣；Ambassador 位於 **Pod 內部**（Localhost）。
    *   **目的**: 讓主應用程式以為它在連線 Localhost，實際上 Ambassador 處理了複雜的服務發現、斷路器（Circuit Breaking）或資料庫分片（Sharding）邏輯。
    *   **Location**: Reverse Proxies (like Nginx Ingress) usually sit at the system edge; an Ambassador sits **inside the Pod** (Localhost).
    *   **Purpose**: Allows the main app to think it's connecting to Localhost, while the Ambassador actually handles complex service discovery, circuit breaking, or database sharding logic.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Pod Mental Model**: 即使在 Docker Compose 中，也要以「一組容器共享資源」的思維來設計服務。
2.  **Sidecar**: 擴充功能（Logging, Monitoring）而不修改主程式。
3.  **Ambassador**: 代理外部連線，隱藏網路複雜度。
4.  **Adapter**: 標準化輸出介面。
5.  **Init Container**: 處理啟動前的依賴檢查與環境準備。
6.  **12-Factor Adaptation**: 利用這些模式填補 Legacy App 與雲原生標準之間的鴻溝。

## 下一步 (Next Steps)

*   **延伸閱讀**: 深入研究 **Kubernetes** 的 Pod 設計，這是這些模式的原生棲息地。
*   **實作練習**: 嘗試使用 `docker-compose` 實作一個帶有 Prometheus Exporter Sidecar 的 Web Service。
*   **下一章預告**: 我們將探討 **Docker Security & Best Practices**，學習如何掃描映像檔漏洞、管理 Secrets 以及實作最小權限原則（Least Privilege）。

*   **Further Reading**: Dive deep into **Kubernetes** Pod design, the native habitat of these patterns.
*   **Practical Exercise**: Try implementing a Web Service with a Prometheus Exporter Sidecar using `docker-compose`.
*   **Next Chapter**: We will explore **Docker Security & Best Practices**, learning how to scan image vulnerabilities, manage Secrets, and implement Least Privilege.