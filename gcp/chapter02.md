# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，選擇運算服務（Compute Services）不再只是「如何部署程式碼」，而是關於**營運成本（TCO）**、**維運複雜度（Operational Complexity）**與**系統靈活性（Flexibility）**之間的權衡。本章將超越基礎操作，從架構師視角剖析 GCP 的運算光譜。

As a Senior Engineer, choosing Compute Services is no longer just about "how to deploy code"; it's a trade-off between **Total Cost of Ownership (TCO)**, **Operational Complexity**, and **System Flexibility**. This chapter goes beyond basic operations to analyze the GCP compute spectrum from an architect's perspective.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選型**：在 GCE、GKE (Standard/Autopilot)、Cloud Run 與 App Engine 之間，根據流量特徵與團隊規模做出最佳架構決策。
    **Select with Precision**: Make optimal architectural decisions among GCE, GKE (Standard/Autopilot), Cloud Run, and App Engine based on traffic patterns and team size.
2.  **評估成本效益**：理解不同服務的定價模型（如 Committed Use Discounts vs. Pay-per-use），並能計算大規模部署下的成本差異。
    **Evaluate Cost-Efficiency**: Understand pricing models (e.g., Committed Use Discounts vs. Pay-per-use) and calculate cost differences for large-scale deployments.
3.  **掌握現代化路徑**：設計從 Legacy Monolith 遷移至 Container 或 Serverless 的漸進式策略，避免過度工程化（Over-engineering）。
    **Master Modernization Paths**: Design progressive strategies for migrating Legacy Monoliths to Containers or Serverless, avoiding over-engineering.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 運算抽象光譜 (The Compute Abstraction Spectrum)

請建立一個從「控制力最強」到「管理最少」的光譜模型。
Establish a spectrum model ranging from "Maximum Control" to "Minimum Management".

| Service | Category | Abstraction Level | AWS Equivalent | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Compute Engine (GCE)** | IaaS | Low (Hardware/OS) | EC2 | Legacy apps, Databases, Custom Kernels, High-performance computing (HPC). |
| **GKE Standard** | CaaS / Orchestration | Medium (Cluster/Node) | EKS (Self-managed nodes) | Complex microservices, Stateful workloads, Service Mesh needs. |
| **GKE Autopilot** | CaaS / Managed | Medium-High (Pod) | EKS Fargate | K8s best practices enforced by Google, reduced ops overhead. |
| **Cloud Run** | Serverless Container | High (Request/Container) | AWS App Runner / Lambda (Container) | Stateless HTTP/Event-driven services, rapid scaling, scale-to-zero. |
| **App Engine (GAE)** | PaaS | High (Source Code) | Elastic Beanstalk | Quick web apps, integrated ecosystem (though losing ground to Cloud Run). |

### 關鍵差異 (Key Differentiators)

1.  **GKE Standard vs. Autopilot**:
    - **Standard**: 你管理 Node Pools。你可以 SSH 進入節點，安裝自定義驅動，但需負責 OS patch 和 Bin-packing（資源裝箱最佳化）。
    - **Autopilot**: Google 管理 Node。你只需定義 Pod 規格，按 Pod 資源付費。適合不想處理底層基礎設施但需要 K8s API 的團隊。
    - **Standard**: You manage Node Pools. You can SSH into nodes and install custom drivers, but you are responsible for OS patches and Bin-packing.
    - **Autopilot**: Google manages Nodes. You define Pod specs and pay per Pod resource. Ideal for teams wanting K8s APIs without infrastructure hassle.

2.  **Cloud Run vs. GKE**:
    - Cloud Run 是基於 **Knative** 的 Serverless 實作。它專注於「請求驅動（Request-driven）」的無狀態容器。
    - Cloud Run 啟動極快（毫秒級），GKE 擴展節點較慢（分鐘級）。
    - Cloud Run is a Serverless implementation based on **Knative**. It focuses on "Request-driven" stateless containers.
    - Cloud Run scales extremely fast (milliseconds), whereas GKE node scaling is slower (minutes).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計中，我們很少只選擇單一服務，而是採用**混合運算策略（Hybrid Compute Strategy）**。
In large-scale system design, we rarely choose a single service; instead, we adopt a **Hybrid Compute Strategy**.

## 3.1 典型架構模式 (Typical Architecture Patterns)

### 模式 A：現代化微服務 (Modern Microservices)
- **Frontend / BFF (Backend for Frontend)**: 部署於 **Cloud Run**。
  - 原因：流量波動大，需要快速擴縮（Scale-out），且通常無狀態。
  - Reason: High traffic fluctuation, requires rapid scale-out, and is typically stateless.
- **Core Business Logic**: 部署於 **GKE**。
  - 原因：服務間通訊頻繁（gRPC），需要細粒度的流量控制（Istio/Traffic Director），或有長連線需求（WebSockets）。
  - Reason: Frequent inter-service communication (gRPC), requires fine-grained traffic control (Istio/Traffic Director), or long-lived connections (WebSockets).
- **Data Stores / Legacy**: 部署於 **GCE** 或 Managed Services。
  - 原因：自建資料庫（如 Cassandra/Elasticsearch）或需特定 OS 授權的舊系統。
  - Reason: Self-hosted databases (e.g., Cassandra/Elasticsearch) or legacy systems requiring specific OS licenses.

## 3.2 決策矩陣 (Decision Matrix)

當你在 System Design Interview 或架構會議中被問到選型時，可參考以下維度：
When asked about selection during a System Design Interview or architecture meeting, refer to these dimensions:

1.  **Is it HTTP/Event driven?**
    - Yes $\rightarrow$ Cloud Run.
    - No (e.g., Background worker, Custom Protocol) $\rightarrow$ GKE or GCE.
2.  **Do you need GPU or specific Hardware?**
    - Yes $\rightarrow$ GCE or GKE (Cloud Run now supports GPU but with limitations).
3.  **Is Ops Team size small?**
    - Yes $\rightarrow$ Cloud Run or GKE Autopilot.
    - No $\rightarrow$ GKE Standard (for cost optimization via bin-packing).
4.  **Scale to Zero required?**
    - Yes $\rightarrow$ Cloud Run.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：從單體到 Serverless 的遷移 (Scenario: Migrating Monolith to Serverless)

**背景 (Context)**:
一家電商公司擁有一個基於 Java Spring Boot 的單體應用，目前運行在地端 VM 上。流量在促銷期間會暴增 10 倍。
An e-commerce company has a Java Spring Boot monolith running on on-premise VMs. Traffic spikes 10x during promotions.

### 階段 1：容器化與 Cloud Run (Phase 1: Containerization & Cloud Run)

最初的想法是直接將 Spring Boot 應用容器化並部署到 Cloud Run。
The initial thought is to containerize the Spring Boot app directly and deploy it to Cloud Run.

**挑戰 (Challenge)**:
Spring Boot 啟動時間較慢（Cold Start ~10-20s），且應用內包含「背景排程任務（Scheduled Tasks）」。
Spring Boot has a slow startup time (Cold Start ~10-20s), and the app contains internal "Scheduled Tasks".

**解決方案 (Solution)**:
1.  **優化啟動時間**：啟用 Cloud Run 的 `min-instances` 設為 1，避免冷啟動影響首位用戶。
2.  **分離背景任務**：Cloud Run 會在請求處理完畢後節流 CPU（CPU throttling）。背景任務必須移出。

```yaml
# cloudbuild.yaml snippet (Conceptual)
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/my-project/monolith', '.']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'monolith-service'
      - '--image=gcr.io/my-project/monolith'
      - '--min-instances=1'  # Mitigate cold start
      - '--cpu-boost'        # Faster startup
```

### 階段 2：架構拆分 (Phase 2: Architectural Split)

為了更佳的擴展性，我們將系統拆分：
For better scalability, we split the system:

1.  **Web Service**: 繼續留在 **Cloud Run**，處理 HTTP 請求。
2.  **Worker**: 使用 **Cloud Run Jobs** 或 **GKE** 處理非同步任務。
3.  **Database**: 遷移至 **Cloud SQL**，使用 Private Service Connect 連線。

**為何這樣做可行？ (Why this works?)**
Cloud Run 負責承載突發流量（Burst traffic），因為它擴展速度遠快於 GKE 的 Cluster Autoscaler。背景任務使用 Cloud Run Jobs 則避免了 HTTP timeout 的限制。
Cloud Run handles burst traffic because it scales much faster than GKE's Cluster Autoscaler. Using Cloud Run Jobs for background tasks avoids HTTP timeout limitations.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽視 Cloud Run 的並發設定 (Ignoring Cloud Run Concurrency)
**錯誤 (Pitfall)**: 將 Cloud Run 的 `concurrency` (max requests per container) 設為預設值（80），但應用程式是單執行緒（如 Node.js）或記憶體密集型。
**Pitfall**: Leaving Cloud Run `concurrency` at default (80), while the app is single-threaded (e.g., Node.js) or memory-intensive.

**後果 (Consequence)**: 請求延遲增加（Latency spike）或 OOM（Out of Memory）。
**Consequence**: Latency spikes or OOM errors.

**修正 (Fix)**: 根據負載測試調整 `concurrency`。對於 CPU 密集型應用，可能需要設為 1。
**Fix**: Tune `concurrency` based on load testing. For CPU-intensive apps, it might need to be set to 1.

## 5.2 在 GKE Autopilot 上執行 DaemonSets (Running DaemonSets on GKE Autopilot)
**錯誤 (Pitfall)**: 試圖在 Autopilot 上像在 Standard 一樣廣泛使用 DaemonSets 來搜集 Logs 或監控。
**Pitfall**: Trying to use DaemonSets extensively on Autopilot for logging/monitoring, just like in Standard.

**後果 (Consequence)**: Autopilot 限制了對節點的存取權限，許多依賴 HostPath 或特權模式的 DaemonSets 無法運作。
**Consequence**: Autopilot restricts node access; many DaemonSets relying on HostPath or privileged mode will fail.

**修正 (Fix)**: 使用 Sidecar 模式，或依賴 GCP 原生整合的 Cloud Logging/Monitoring。
**Fix**: Use the Sidecar pattern or rely on GCP's native Cloud Logging/Monitoring integration.

## 5.3 為了「未來擴充」而過早使用 GKE (Premature GKE Adoption)
**錯誤 (Pitfall)**: 團隊只有 3 人，卻為了「未來可能需要 Service Mesh」而搭建了一套複雜的 GKE Standard 環境。
**Pitfall**: A team of 3 sets up a complex GKE Standard environment just for "potential future Service Mesh needs."

**後果 (Consequence)**: 80% 的時間花在升級 Cluster、修復憑證與調整 Node Pool，而非開發業務功能。
**Consequence**: 80% of time is spent upgrading clusters, fixing certs, and tuning Node Pools, rather than developing features.

**修正 (Fix)**: 從 Cloud Run 開始。它現在支援 VPC Access、Sidecars 和 Traffic splitting，足以應付大多數中型系統。
**Fix**: Start with Cloud Run. It now supports VPC Access, Sidecars, and Traffic splitting, sufficient for most mid-sized systems.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: GKE Autopilot 與 Cloud Run 都是 Serverless 概念，你會如何選擇？
**GKE Autopilot and Cloud Run are both "Serverless" concepts. How do you choose between them?**

*   **高分回答要點 (Key Points)**:
    *   **API 兼容性**: 需要完整的 Kubernetes API（如 CRDs, StatefulSets, Jobs, Namespaces）選 GKE Autopilot。
    *   **計費模型**: Cloud Run 是 Request-based（閒置不計費，除非設 min-instance）；Autopilot 是 Pod Resource-based（Pod 活著就計費）。
    *   **通訊協議**: Cloud Run 主要是 HTTP/gRPC (Request/Response)；GKE 支援更廣泛的 TCP/UDP 協議與複雜的 Service Mesh 拓撲。

## Q2: 如何設計一個能應付「秒殺（Flash Sale）」活動的運算架構？
**How would you design a compute architecture for a "Flash Sale" event?**

*   **高分回答要點 (Key Points)**:
    *   **預熱 (Pre-warming)**: GKE 擴展節點需要時間（分鐘級）。若用 GKE，需提前調整 HPA 或手動擴容。
    *   **Cloud Run 優勢**: Cloud Run 的擴展速度極快（秒級千個實例），更適合不可預測的突發流量。
    *   **混合策略**: 靜態資源走 CDN，動態請求走 Cloud Run，資料庫層需搭配 Redis 緩存與 Cloud SQL 的 Connection Pooling。

## Q3: 在 GKE 中，Standard 模式比 Autopilot 模式更省錢的情況是什麼？
**In GKE, when is Standard mode cheaper than Autopilot mode?**

*   **高分回答要點 (Key Points)**:
    *   **Bin-packing**: Autopilot 會對 Pod 資源有一定的緩衝與計費進位。如果你能極度優化 Bin-packing（將節點塞滿），Standard 的單位成本較低。
    *   **Spot Instances**: 雖然兩者都支援 Spot，但在 Standard 中你可以更靈活地控制 Spot Node Pools 的混合策略，承擔較高的被中斷風險以換取更低成本。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **GCE** 是最後手段（Last Resort），僅用於 Legacy、DB 或特殊核心需求。
2.  **Cloud Run** 是大多數無狀態 Web 應用的**預設首選（Default Choice）**，兼具開發速度與維運簡便性。
3.  **GKE Autopilot** 填補了 K8s 與 Serverless 間的鴻溝，適合需要 K8s 生態但不想管 Node 的團隊。
4.  **成本與控制成反比**：越高的抽象層（Cloud Run）通常單位資源單價較高，但節省了巨大的人力維運成本。
5.  **冷啟動（Cold Start）** 是 Serverless 的主要敵人，善用 `min-instances` 與 `CPU boost`。

## 後續延伸 (Next Steps)
- **Next Chapter**: 既然搞定了運算，下一步必須處理**網路與流量管理**。
- **Action Item**: 嘗試使用 Terraform 撰寫一個包含 Cloud Run 與 Cloud SQL (via Private Service Connect) 的完整模組。
- **Recommended Reading**: Google SRE Book 中關於 "Capacity Planning" 的章節，深入理解擴展背後的數學原理。