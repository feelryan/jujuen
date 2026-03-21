# 運算服務選型決策矩陣 / Compute Services Decision Matrix

## Mental model｜心智模型

在 Azure 上選擇運算服務（Compute Services）時，不要只看「技術流行度」，而應基於 **「抽象化層級 (Level of Abstraction)」** 與 **「控制權 vs. 生產力 (Control vs. Productivity)」** 的權衡。

我們可以將主要的運算服務想像成一個光譜，從左到右，你管理的底層越少，開發速度越快，但對環境的客製化控制力越低。

### The "Unit of Scaling" Model (擴展單位模型)

理解選型的關鍵在於：**你的應用程式是以什麼單位進行擴展的？**

1.  **Virtual Machines (IaaS):** 單位是 **OS (作業系統)**。你需要管理 Patching、Networking、Middleware。
    *   *Mental Image:* 租了一台空伺服器，你擁有 Root 權限，但也擁有維護責任。
2.  **Azure Kubernetes Service (AKS):** 單位是 **Cluster & Pod**。你管理 K8s API 和節點池 (Node Pools)，Azure 管理 Control Plane。
    *   *Mental Image:* 管理一個由貨櫃組成的自動化艦隊，極度強大但也極度複雜。
3.  **Azure App Service (PaaS):** 單位是 **App (應用程式)**。你只管 Code 或 Container，Azure 處理 Load Balancing 和 OS。
    *   *Mental Image:* 託管網站的豪華公寓，有管理員幫你處理水電和保全，你只需入住。
4.  **Azure Container Apps (ACA):** 單位是 **Container Revision**。基於 K8s 但隱藏了複雜度，專注於微服務與 KEDA 自動擴展。
    *   *Mental Image:* Serverless 的容器艦隊，不需要懂 `kubectl` 也能跑微服務。
5.  **Azure Functions (Serverless):** 單位是 **Function (函式/事件)**。有事件發生才執行，以毫秒計費。
    *   *Mental Image:* 隨叫隨到的臨時工，做完事就消失，完全不用管伺服器在哪。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Decision Matrix (選型矩陣)

在實戰中，我們通常依據以下維度進行快速篩選：

| Feature | **Virtual Machines** | **AKS (Kubernetes)** | **App Service (Web Apps)** | **Container Apps (ACA)** | **Azure Functions** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Use Case** | Legacy apps, specific OS needs, DB hosting | Complex Microservices, full orchestration control | Monolithic Web Apps, Simple APIs | Microservices without K8s overhead, Event-driven containers | Event-driven processing, Glue code, Short tasks |
| **Ops Effort** | High (OS Patching, Backup) | High (Cluster upgrades, Securing YAMLs) | Low (Managed Platform) | Low/Medium (Serverless Containers) | Very Low (Code only) |
| **Scaling Speed** | Slow (Minutes) | Medium (Seconds/Minutes) | Medium (Scale out rules) | Fast (KEDA based, supports scale to zero) | Instant (Event-driven) |
| **Cost Model** | Pay for provisioned capacity (24/7) | Pay for Nodes (VMs) running 24/7 | Pay for App Service Plan (Dedicated) | Consumption (Pay per use) or Dedicated | Consumption (Pay per exec) or Premium Plan |
| **Networking** | Full VNET control | Advanced (CNI, Network Policy) | VNET Integration (Outbound), Private Endpoint (Inbound) | VNET Integration (Dedicated subnet) | VNET Integration (Premium/Dedicated only) |

### 2. Common Architecture Patterns (常見架構模式)

*   **Lift & Shift (搬遷上雲):**
    *   優先考慮 **App Service** (如果是 Web/API)。
    *   如果依賴特定 OS 元件、Registry 機碼或第三方軟體安裝，則退回到 **VM**。
*   **Modern Cloud-Native (現代化雲原生):**
    *   **Azure Container Apps (ACA)** 是目前的 "Sweet Spot"。它適合大多數不需要直接操作 Kubernetes API 的微服務場景。
    *   只有當你需要 Service Mesh (Istio/Linkerd) 的深度客製化、或是混合雲/多雲策略時，才選擇 **AKS**。
*   **Event-Driven Glue (事件驅動膠水層):**
    *   使用 **Azure Functions** 處理 Queue 訊息、Blob 上傳觸發、定時排程。
    *   *Best Practice:* 保持 Function 輕量、無狀態 (Stateless)。

### 3. Cost Optimization Patterns (成本優化模式)

*   **Dev/Test Environments:** 使用 App Service 的 B-series (Basic) 或 Free tier；AKS 使用 User Node Pool 的 Spot Instances。
*   **Reserved Instances (RI):** 對於 VM、App Service (Premium V3)、AKS Nodes，購買 1 或 3 年預留實例可節省 30-50%。
*   **Scale to Zero:** 利用 Azure Functions (Consumption) 或 Container Apps 的 Scale to Zero 特性，在無流量時不付費。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Resume Driven Development (履歷驅動開發 - 濫用 K8s)
*   **Anti-pattern:** 團隊只有 3 個人，維護一個簡單的 CRUD API，卻堅持使用 AKS，只因為 "Kubernetes 很潮"。
*   **Consequence:** 團隊 50% 的時間花在升級 Cluster、除錯 Ingress Controller 和設定 Helm Chart，而不是開發業務功能。
*   **Correction:** 使用 **App Service for Containers** 或 **Container Apps**。

### 2. The "Serverless" Monolith (Serverless 巨石)
*   **Anti-pattern:** 將整個龐大的 Web API 塞進一個 Azure Function App，啟動時間超過 10 秒。
*   **Consequence:** 嚴重的 **Cold Start (冷啟動)** 問題導致使用者體驗極差；Timeout 限制 (預設 5-10 分鐘) 導致長任務失敗。
*   **Correction:** 將長任務移至 Durable Functions 或背景 Worker；API 服務改用 App Service/ACA。

### 3. Ignoring Network Constraints (忽視網路限制)
*   **Anti-pattern:** 假設 Serverless (Functions/Logic Apps) 可以直接存取 VNET 內的 SQL Database 或 On-premise 資源。
*   **Consequence:** 部署後發現連線失敗。
*   **Correction:** 必須使用 **Premium Plan** 或 **App Service Environment (ASE)** 才能具備 VNET Integration 功能。Consumption Plan 預設無法存取內網資源。

### 4. "Pet" VMs in the Cloud (雲端寵物)
*   **Anti-pattern:** 手動登入 VM 安裝軟體，沒有任何自動化腳本 (IaC)。
*   **Consequence:** 當 VM 掛掉時，無法重建；無法擴展 (Scale-out)。
*   **Correction:** 使用 **VM Scale Sets (VMSS)** 搭配 Custom Script Extension 或 Packer 映像檔；或是盡早容器化。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree Workflow (選型決策樹)

請依照順序回答以下問題，以決定適合的服務：

1.  **Is it a legacy app requiring full OS control (e.g., install .exe, modify registry)?**
    *   Yes -> **Virtual Machine**
    *   No -> Go to 2.

2.  **Is the workload purely Event-Driven (e.g., process file upload, queue trigger) and short-lived?**
    *   Yes -> **Azure Functions**
    *   No -> Go to 3.

3.  **Is it a standard Web Application / API (HTTP based)?**
    *   Yes -> **App Service** (Start here, it's the easiest).
    *   No (or need Microservices) -> Go to 4.

4.  **Is the application containerized?**
    *   Yes -> Go to 5.
    *   No -> Containerize it first, or use App Service (Code).

5.  **Do you need full control over Kubernetes API (CRDs, Service Mesh, specific DaemonSets)?**
    *   Yes -> **Azure Kubernetes Service (AKS)**
    *   No (I just want to run containers and scale based on HTTP/Events) -> **Azure Container Apps (ACA)**

### Technical Readiness Checklist (技術準備度檢查表)

- [ ] **Statelessness:** 應用程式是否無狀態？(如果依賴本地 Session/File System，擴展會有問題)。
- [ ] **Networking:** 是否需要存取 Private VNET 資源 (DB, Redis)？(影響 SKU 選擇，如 Function Premium vs Consumption)。
- [ ] **Observability:** 是否已整合 Application Insights？(PaaS/Serverless 除錯極度依賴 Log)。
- [ ] **Cost Awareness:** 是否計算過 24/7 運行的成本？(App Service Plan 是租整台機器，沒流量也要付錢)。
- [ ] **Deployment:** 是否有 CI/CD Pipeline？(不要使用 FTP 或手動上傳 zip 部署)。

---

## Real-world examples｜實戰案例

### Scenario A: The Marketing Campaign Site (行銷活動網站)
*   **Context:** 短期活動，流量預期會有爆發 (Spike)，活動結束後流量歸零。
*   **Selection:** **Azure Container Apps** or **Azure Functions**.
*   **Reasoning:** 需要能夠快速從 0 擴展到 100 實例 (KEDA scaling)，且活動結束後自動縮減至 0 以節省成本。App Service 的擴展速度可能不夠快且需要預付費用。

### Scenario B: Enterprise Internal ERP Extension (企業內部 ERP 擴充)
*   **Context:** 傳統 .NET Framework 應用，連線地端 SQL Server，團隊熟悉 IIS。
*   **Selection:** **App Service (Windows Container or Code)** with **VNET Integration**.
*   **Reasoning:** 團隊不需要學習 K8s。VNET Integration 允許安全連線回地端 (On-premise) 透過 VPN/ExpressRoute。PaaS 處理了大部分 Windows Patching 工作。

### Scenario C: High-Frequency Trading Data Processor (高頻交易資料處理)
*   **Context:** 數百個微服務，極度複雜的服務間通訊，需要自定義 Network Policies 和 Sidecar 監控。
*   **Selection:** **Azure Kubernetes Service (AKS)**.
*   **Reasoning:** 這裡的複雜度證明了引入 K8s 的合理性。需要 K8s 生態系的豐富工具 (Helm, Istio, Prometheus) 來管理大規模叢集。

### Scenario D: Daily Report Generator (日報表產生器)
*   **Context:** 每天凌晨 2 點執行一次，讀取 DB 產生 PDF 並寄送 Email，執行時間約 15 分鐘。
*   **Selection:** **Azure Functions (Premium/Dedicated)** or **Container Apps Jobs**.
*   **Reasoning:** 雖然是事件驅動，但 Consumption Plan 有 10 分鐘執行上限風險。使用 Premium Plan 或 ACA Jobs 可以處理長時間運行的背景任務，且不用維護一台 24 小時開機的 VM。