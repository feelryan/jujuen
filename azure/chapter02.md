# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，在系統設計面試或架構規劃中，最關鍵的不是列舉出所有 Azure 服務，而是展現「選擇的能力」。本章將超越基礎介紹，專注於 Azure 四大核心運算服務（Virtual Machines, App Service, AKS, Azure Functions）的決策矩陣。

As a Senior Engineer, the key differentiator in system design interviews or architectural planning is not listing every Azure service, but demonstrating the "ability to choose." This chapter moves beyond basic introductions to focus on the decision matrix for Azure's four core compute services: Virtual Machines, App Service, AKS, and Azure Functions.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **建立運算服務決策樹 (Construct a Compute Decision Tree)**：根據業務需求（延遲、吞吐量、狀態管理）與團隊規模，精準選擇 IaaS, PaaS 或 FaaS。
    Construct a precise decision tree for IaaS, PaaS, or FaaS based on business requirements (latency, throughput, state management) and team size.
2.  **評估維運成本與複雜度 (Evaluate Operational Cost & Complexity)**：理解「完全控制權 (Total Control)」與「無伺服器 (Serverless)」之間的 Trade-off，避免過度設計（Over-engineering）。
    Understand the trade-offs between "Total Control" and "Serverless" to avoid over-engineering.
3.  **識別反模式 (Identify Anti-patterns)**：清楚解釋為何不應將長執行緒任務放入 Azure Functions，或何時不該使用 AKS。
    Clearly explain why long-running tasks should not be placed in Azure Functions, or when AKS should be avoided.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在 Azure 中選擇運算服務，本質上是在權衡 **「控制權 (Control)」** 與 **「生產力 (Productivity)」**。我們可以將其視為一個光譜（Spectrum）。

Choosing a compute service in Azure is essentially balancing **"Control"** and **"Productivity"**. We can visualize this as a spectrum.

### The Compute Spectrum (運算光譜)

1.  **Virtual Machines (IaaS)**
    *   **類比 (Analogy)**：自建透天厝。你擁有土地和建築的所有權，可以隨意裝修，但水電維修、保全都要自己負責。
    *   **定義 (Definition)**：提供原始的 OS 環境。適合需要特定 OS kernel 設定、舊系統遷移 (Lift & Shift) 或極度客製化的場景。
    *   **Analogy**: Building your own detached house. You own the land and the building and can renovate as you please, but you are responsible for utilities, maintenance, and security.
    *   **Definition**: Provides a raw OS environment. Suitable for scenarios requiring specific OS kernel settings, legacy system migration (Lift & Shift), or extreme customization.

2.  **Azure Kubernetes Service - AKS (Container PaaS)**
    *   **類比 (Analogy)**：大型社區管理委員會。你住在標準化的公寓（Container）裡，社區有完善的公設和管理規則（Orchestration），適合大規模住戶，但你需要懂複雜的社區規約。
    *   **定義 (Definition)**：託管的 Kubernetes。適合微服務架構、高密度部署、以及需要雲端供應商中立性 (Cloud Agnostic) 的場景。
    *   **Analogy**: A large condominium association. You live in a standardized apartment (Container) with shared amenities and rules (Orchestration). It fits a large scale of residents, but you need to understand complex bylaws.
    *   **Definition**: Managed Kubernetes. Suitable for microservices architectures, high-density deployments, and scenarios requiring cloud-agnosticism.

3.  **App Service (PaaS)**
    *   **類比 (Analogy)**：酒店式公寓。你只需帶著行李（Code/Artifact）入住，清潔、維護、擴建都由管理方處理。
    *   **定義 (Definition)**：全託管的 HTTP 服務。內建 Auto-scaling, SSL, Blue/Green Deployment (Deployment Slots)。適合標準 Web Apps 與 API。
    *   **Analogy**: Serviced apartment. You just check in with your luggage (Code/Artifact); cleaning, maintenance, and expansion are handled by the management.
    *   **Definition**: Fully managed HTTP service. Built-in Auto-scaling, SSL, and Blue/Green Deployment (Deployment Slots). Suitable for standard Web Apps and APIs.

4.  **Azure Functions (FaaS / Serverless)**
    *   **類比 (Analogy)**：計時租用空間（如 Airbnb 或共享會議室）。用完即走，按使用時間付費，不需關心閒置時的維護。
    *   **定義 (Definition)**：事件驅動 (Event-driven) 的運算單元。適合膠水程式碼 (Glue Code)、資料串流處理、排程任務。
    *   **Analogy**: Pay-per-use space (like Airbnb or shared meeting rooms). Use it and leave, pay only for the time used, with no concern for maintenance when idle.
    *   **Definition**: Event-driven compute units. Suitable for glue code, data stream processing, and scheduled tasks.

### Cloud Provider Mapping (雲端供應商對照)

| Feature | Azure | AWS | GCP |
| :--- | :--- | :--- | :--- |
| **IaaS** | Virtual Machines (VM) | EC2 | Compute Engine (GCE) |
| **Container Orchestration** | AKS | EKS | GKE |
| **Managed Web PaaS** | App Service | Elastic Beanstalk / App Runner | App Engine |
| **Serverless (FaaS)** | Azure Functions | Lambda | Cloud Functions |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或實際架構中，我們通常不會只選一種，而是採用 **混合模式 (Hybrid Approach)**。

In System Design Interviews or actual architectures, we rarely choose just one; instead, we adopt a **Hybrid Approach**.

### 1. The "Lift & Shift" Scenario (舊系統遷移)
*   **情境**：將一個龐大的 .NET Framework 單體應用程式 (Monolith) 搬上雲端。
*   **策略**：
    *   首選 **App Service (Windows Containers)**：如果應用程式可以容器化，這是阻力最小的路徑，立即獲得 Auto-scaling 和 Deployment Slots。
    *   次選 **VM**：如果應用程式依賴特定的 Registry 設定、第三方軟體授權或 GPU 驅動，VM 是唯一解。
*   **Scenario**: Migrating a massive .NET Framework monolith to the cloud.
*   **Strategy**:
    *   **Primary Choice - App Service (Windows Containers)**: If the app can be containerized, this is the path of least resistance, gaining Auto-scaling and Deployment Slots immediately.
    *   **Secondary Choice - VM**: If the app relies on specific Registry settings, third-party software licensing, or GPU drivers, VM is the only solution.

### 2. The Microservices Scenario (微服務架構)
*   **情境**：構建一個高流量的電商平台，包含數十個獨立服務。
*   **策略**：
    *   **AKS**：當服務數量超過 10-15 個，且需要複雜的 Service Mesh (Istio/Linkerd) 或細粒度的資源控制時，AKS 是標準答案。
    *   **Azure Container Apps (ACA)**：如果團隊不想維護 K8s Cluster (Control Plane 升級、Node Pool 管理)，ACA 是基於 K8s 的 Serverless Container 服務，是 AKS 的輕量級替代方案。
*   **Scenario**: Building a high-traffic e-commerce platform with dozens of independent services.
*   **Strategy**:
    *   **AKS**: When the number of services exceeds 10-15, and complex Service Mesh (Istio/Linkerd) or fine-grained resource control is needed, AKS is the standard answer.
    *   **Azure Container Apps (ACA)**: If the team wants to avoid maintaining a K8s Cluster (Control Plane upgrades, Node Pool management), ACA is a Serverless Container service based on K8s, serving as a lightweight alternative to AKS.

### 3. The Event-Driven Glue (事件驅動膠水層)
*   **情境**：使用者上傳圖片後，需要自動縮圖並寫入 Database。
*   **策略**：
    *   **Azure Functions**：這是教科書級的 FaaS 使用場景。利用 `BlobTrigger` 自動觸發，處理完後自動關閉。成本極低且開發速度快。
*   **Scenario**: After a user uploads an image, it needs to be automatically resized and recorded in a Database.
*   **Strategy**:
    *   **Azure Functions**: This is a textbook FaaS use case. Utilize `BlobTrigger` for automatic execution and shutdown upon completion. Extremely low cost and fast development speed.

---

# 4. 逐步示例：決策矩陣演練 (Walkthrough: Decision Matrix Exercise)

讓我們透過一個實際的決策流程，來模擬資深工程師如何評估技術選型。假設我們要建立一個 **「即時庫存查詢 API」**。

Let's simulate how a Senior Engineer evaluates technology selection through a practical decision process. Suppose we are building a **"Real-time Inventory Lookup API"**.

### Phase 1: Requirement Analysis (需求分析)
*   **Latency**: < 100ms (High performance required).
*   **Traffic**: Spiky (Black Friday bursts).
*   **Team**: 3 Developers, limited DevOps experience.

### Phase 2: Evaluating Options (評估選項)

#### Option A: Azure Functions (Consumption Plan)
*   **Pros**: Infinite scaling, zero idle cost.
*   **Cons**: **Cold Start (冷啟動)** issues. For a latency-sensitive API, the initial 2-5 second delay on cold start is unacceptable.
*   **Verdict**: Rejected (unless using Premium Plan to keep warm instances).

#### Option B: AKS
*   **Pros**: High density, full control.
*   **Cons**: **Operational Overhead (維運負擔)**. For a team of 3 with limited DevOps skills, managing a K8s cluster is a distraction from business logic.
*   **Verdict**: Rejected (Over-engineering).

#### Option C: App Service (Premium Plan)
*   **Pros**: Always-on instances (no cold start), built-in auto-scaling rules (scale out based on CPU/Memory), easy integration with Azure DevOps/GitHub Actions.
*   **Cons**: Higher base cost than Functions Consumption plan.
*   **Verdict**: **Selected**. It balances performance reliability with operational simplicity.

### Phase 3: Implementation Strategy (實作策略)

在決定使用 App Service 後，我們需要配置 **App Service Plan**。

After deciding on App Service, we need to configure the **App Service Plan**.

```hcl
# Terraform Example: Defining the Compute Strategy
resource "azurerm_service_plan" "inventory_plan" {
  name                = "asp-inventory-prod"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  
  # SKU Selection Strategy:
  # Standard (S1) for Dev/Test
  # PremiumV3 (P1v3) for Prod (Better CPU/Memory ratio, faster scaling)
  sku_name = "P1v3" 
}

resource "azurerm_linux_web_app" "inventory_api" {
  name                = "app-inventory-api-prod"
  service_plan_id     = azurerm_service_plan.inventory_plan.id
  
  # Enabling Always On to prevent idle timeouts (Crucial for latency)
  site_config {
    always_on = true 
    
    # Auto-scaling rules would be defined in a separate resource (azurerm_monitor_autoscale_setting)
  }
}
```

**Key Takeaway**: 
這裡選擇 `P1v3` 而不是 `Standard`，是因為 Premium V3 支援更快的擴展速度與 VNet Integration，這對於生產環境連接內網資料庫至關重要。

**Key Takeaway**:
We chose `P1v3` over `Standard` because Premium V3 supports faster scaling speeds and VNet Integration, which is crucial for connecting to internal databases in a production environment.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 1. Resume Driven Development (簡歷驅動開發 - 濫用 AKS)
*   **錯誤 (Pitfall)**：團隊只有 5 人，卻為了「跟上潮流」強行使用 AKS 部署簡單的 CRUD App。
*   **後果 (Consequence)**：花在維護 Cluster、升級版本、除錯 Ingress Controller 的時間比寫業務邏輯還多。
*   **修正 (Fix)**：使用 **App Service for Containers** 或 **Azure Container Apps**。它們支援容器，但隱藏了 K8s 的複雜性。
*   **Pitfall**: A team of 5 forcing AKS for a simple CRUD App just to "keep up with trends."
*   **Consequence**: More time spent maintaining the cluster, upgrading versions, and debugging Ingress Controllers than writing business logic.
*   **Fix**: Use **App Service for Containers** or **Azure Container Apps**. They support containers but abstract away K8s complexity.

### 2. Treating Functions as Long-Running Jobs (將 Functions 當作長任務)
*   **錯誤 (Pitfall)**：在 Azure Functions 中執行超過 5-10 分鐘的 ETL 任務。
*   **後果 (Consequence)**：Functions (Consumption Plan) 有硬性 Timeout (預設 5 分鐘，最多 10 分鐘)。任務會被強制中斷，導致資料不一致。
*   **修正 (Fix)**：將長任務移至 **Azure Logic Apps**、**WebJobs** (on App Service) 或 **Azure Batch**。
*   **Pitfall**: Running ETL tasks exceeding 5-10 minutes in Azure Functions.
*   **Consequence**: Functions (Consumption Plan) have a hard timeout (default 5 mins, max 10 mins). Tasks will be forcibly terminated, leading to data inconsistency.
*   **Fix**: Move long-running tasks to **Azure Logic Apps**, **WebJobs** (on App Service), or **Azure Batch**.

### 3. Ignoring "Plan Density" in App Service (忽視 App Service Plan 密度)
*   **錯誤 (Pitfall)**：在同一個 App Service Plan 中塞入過多 Web Apps。
*   **後果 (Consequence)**：App Service Plan 定義了底層 VM 的資源（CPU/RAM）。所有 Apps 共享這些資源，導致 "Noisy Neighbor" 效應，某個 App 流量暴衝會拖慢其他所有 Apps。
*   **修正 (Fix)**：監控 CPU/Memory 指標，適時拆分 Plan，將高流量應用獨立部署。
*   **Pitfall**: Cramming too many Web Apps into a single App Service Plan.
*   **Consequence**: The App Service Plan defines the underlying VM resources (CPU/RAM). All Apps share these resources, leading to the "Noisy Neighbor" effect where one traffic spike slows down all other Apps.
*   **Fix**: Monitor CPU/Memory metrics, split Plans appropriately, and deploy high-traffic applications independently.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試候選人，或在團隊內部進行技術評審。

These questions can be used to interview candidates or conduct technical reviews within the team.

### Q1: "How do you handle 'Cold Starts' in a serverless architecture?"
*   **高分回答要點 (Key Points)**：
    1.  解釋 Cold Start 的成因（平台需要分配資源、下載代碼、啟動 Runtime）。
    2.  **語言選擇**：C# / Java 通常比 Node.js / Python 啟動慢（JIT 編譯）。
    3.  **解決方案**：
        *   使用 **Premium Plan** (Pre-warmed instances)。
        *   定期發送 "Ping" 請求（雖是 Hack，但常見）。
        *   將關鍵路徑（Critical Path）移至 App Service，非關鍵路徑保留在 Functions。
*   **Key Points**:
    1.  Explain the cause (platform provisioning, code download, runtime startup).
    2.  **Language Choice**: C# / Java are generally slower than Node.js / Python (JIT compilation).
    3.  **Solutions**:
        *   Use **Premium Plan** (Pre-warmed instances).
        *   Periodic "Ping" requests (a hack, but common).
        *   Move critical paths to App Service, keep non-critical paths on Functions.

### Q2: "When would you choose VM over App Service/AKS in 2024?"
*   **高分回答要點 (Key Points)**：
    1.  **Legacy Dependencies**：依賴特定 OS 版本、COM 元件、GAC (Global Assembly Cache)。
    2.  **Stateful Protocols**：非 HTTP/gRPC 的協議，或需要極度客製化的 TCP/UDP 行為。
    3.  **Database Hosting**：雖然推薦 Managed SQL，但有時為了成本或特殊 DB 引擎（如舊版 Oracle），需自建 DB on VM。
    4.  **Hybrid Connectivity**：某些特殊的 VPN Gateway 或網路代理設置可能需要 VM 層級的控制。
*   **Key Points**:
    1.  **Legacy Dependencies**: Specific OS versions, COM components, GAC.
    2.  **Stateful Protocols**: Non-HTTP/gRPC protocols, or highly customized TCP/UDP behavior.
    3.  **Database Hosting**: While Managed SQL is recommended, sometimes self-hosting DB on VM is needed for cost or specific engines (e.g., legacy Oracle).
    4.  **Hybrid Connectivity**: Specific VPN Gateway or network proxy setups might require VM-level control.

### Q3: "Design a scaling strategy for a flash-sale event."
*   **高分回答要點 (Key Points)**：
    1.  **Predictive Scaling**：如果知道活動時間，提前擴展（Pre-scale）App Service Plan 或 AKS Node Pool，不要依賴 Reactive Auto-scaling（反應太慢）。
    2.  **Queue-Based Load Leveling**：前端 API 只負責接收請求並丟入 **Service Bus** 或 **Event Hubs**，後端 Worker 慢慢消化，避免資料庫被打掛。
    3.  **CDN & Caching**：在運算層之前擋掉 90% 的靜態流量。
*   **Key Points**:
    1.  **Predictive Scaling**: If the event time is known, Pre-scale the App Service Plan or AKS Node Pool. Do not rely on Reactive Auto-scaling (too slow).
    2.  **Queue-Based Load Leveling**: Frontend APIs only accept requests and push to **Service Bus** or **Event Hubs**; backend workers process at their own pace to protect the database.
    3.  **CDN & Caching**: Offload 90% of static traffic before it hits the compute layer.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### Summary (記憶錨點)
1.  **VM** 是最後手段 (Last Resort)，僅用於極度客製化或 Legacy 遷移。
2.  **App Service** 是大多數 Web 應用的預設首選 (Default Choice)，平衡了控制與便利。
3.  **AKS** 適合大規模微服務，但需評估團隊的 K8s 維運能力 (Ops Capability)。
4.  **Azure Functions** 優秀於事件驅動任務，但要注意 Cold Start 和 Execution Timeout。
5.  **Hybrid is King**：一個成熟的系統通常會同時包含 App Service (API), AKS (Core Services), 和 Functions (Background Jobs)。

### Next Steps (下一步)
決定了運算服務後，下一個挑戰是如何讓它們安全地互相通訊。下一章我們將探討 **Azure Networking**，重點包含 **Virtual Networks (VNet)**, **Private Link**, 與 **API Management** 的整合。

After deciding on compute services, the next challenge is secure communication. In the next chapter, we will explore **Azure Networking**, focusing on **Virtual Networks (VNet)**, **Private Link**, and integration with **API Management**.