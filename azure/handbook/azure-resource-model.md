# Azure 資源模型與治理階層 / Azure Resource Manager (ARM) & Governance Hierarchy

## Mental model｜心智模型

要駕馭 Azure，首先必須理解 **Azure Resource Manager (ARM)** 不僅僅是一個管理介面，它是 Azure 的 **控制平面 (Control Plane)** 與 **API Gateway**。

### 1. ARM as the API Layer
無論你使用 Azure Portal、Azure CLI、PowerShell、Terraform 還是 Bicep，所有的請求最終都會轉換為對 ARM API 的 REST 呼叫。
*   **一致性 (Consistency)**：ARM 確保無論透過何種工具，資源的建立、更新與刪除行為都是一致的。
*   **定義檔 (Schema)**：所有資源最終都由 JSON 定義。理解這一點，你就會明白為什麼 Infrastructure as Code (IaC) 是 Azure 的原生語言。

### 2. The Hierarchy of Governance (治理階層)
想像一個企業的組織結構圖，這直接對應到 Azure 的四層架構。正確的對應關係如下：

1.  **Management Groups (管理群組)**：
    *   *Mental Model*: **公司總部與部門 (Corporate & Divisions)**。
    *   *用途*: 用於套用「政策 (Policy)」與「合規性 (Compliance)」。例如：限制全公司只能在特定 Region 開機器。
2.  **Subscriptions (訂用帳戶)**：
    *   *Mental Model*: **成本中心與隔離邊界 (Cost Centers & Blast Radius)**。
    *   *用途*: 這是計費 (Billing)、配額 (Quota) 與安全邊界。不要害怕建立多個 Subscriptions。
3.  **Resource Groups (資源群組)**：
    *   *Mental Model*: **專案容器與生命週期 (Project Container & Lifecycle)**。
    *   *用途*: 這是部署單元。如果資源會「一起出生、一起死亡」，它們就該在同一個 RG。
4.  **Resources (資源)**：
    *   *Mental Model*: **實際資產 (Actual Assets)**。
    *   *用途*: VM, SQL DB, Storage Account 等實體。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Subscription Democratization (訂用帳戶民主化)
不要將所有東西塞進單一 Subscription。
*   **Pattern**: 採用 **Subscription-vending** 模式。
*   **實作**: 依據「環境 (Prod/Non-Prod)」或「工作負載 (Workload)」切割。
    *   `Sub-Corp-Prod`: 生產環境，嚴格的 RBAC 與 Policy。
    *   `Sub-Corp-Dev`: 開發環境，較寬鬆的權限，可能有預算上限 (Budget Cap)。
*   **Why**: 避免觸發 API Rate Limits (Throttling)，隔離安全風險 (Blast Radius)，並讓成本歸屬更清晰。

### 2. Resource Group by Lifecycle (依生命週期分組)
*   **Pattern**: **Lifecycle-aligned Resource Groups**.
*   **實作**: 一個應用程式通常包含 `App-RG` (Web App, Function) 與 `Data-RG` (SQL, Storage) 甚至 `Network-RG` (VNet)。
*   **最佳實務**:
    *   如果是 Stateless 的應用層，部署時常會整組刪除重建，請放在獨立 RG。
    *   如果是 Stateful 的資料層，生命週期較長，請放在另一個 RG 並加上 **Resource Lock**。

### 3. Enterprise-Scale Landing Zones (ESLZ)
*   **Pattern**: 採用微軟官方推薦的 Hub-Spoke 拓撲結構。
*   **實作**:
    *   **Platform Management Group**: 放置 Identity, Connectivity, Management 相關的共用 Subscriptions。
    *   **Landing Zones Management Group**: 放置實際應用程式 (Corp, Online) 的 Subscriptions。
*   **Why**: 讓應用程式團隊專注開發，而網路與身分驗證由平台團隊集中管理。

### 4. Tagging Strategy as a Contract (標籤即合約)
*   **Pattern**: 強制性標籤策略。
*   **實作**: 利用 Azure Policy 強制要求特定 Tag (如 `CostCenter`, `Owner`, `Environment`) 必須存在，否則拒絕部署 (Deny) 或自動補上 (Modify)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Monolithic Subscription" (單體訂用帳戶)
*   **Bad Practice**: 全公司只有一個 "Pay-As-You-Go" Subscription，裡面混雜了 Dev, Test, Prod 以及各種專案。
*   **後果**:
    *   輕易觸發 Azure Resource Quota (例如 vCPU 核心數限制)。
    *   RBAC 權限管理極度複雜，容易導致開發人員誤刪 Prod 資源。
    *   無法精確拆分帳單。

### 2. Grouping by Resource Type (依技術類型分組)
*   **Bad Practice**: 建立 `Network-RG` (放所有 VNet), `Compute-RG` (放所有 VM), `Database-RG` (放所有 SQL)。
*   **後果**: 違背了生命週期管理。當你要刪除 "Project A" 時，你必須去三個不同的 RG 裡挑出屬於 Project A 的資源，這極易出錯且難以自動化。

### 3. Nesting Resource Groups (巢狀資源群組)
*   **Pitfall**: 試圖在 Resource Group 裡面再建立 Resource Group。
*   **現實**: Azure **不支援** 巢狀 RG。RG 是扁平的。如果你需要層級，請使用 Tags 或回頭檢視 Subscription/Management Group 的設計。

### 4. Ignoring Region Consistency (忽略區域一致性)
*   **Pitfall**: Resource Group 在 `East US`，但裡面的資源在 `West US`。
*   **後果**: 雖然技術上可行，但如果 `East US` 的控制平面掛了，你可能無法管理位於 `West US` 的資源（即使資源本身還在運行）。
*   **建議**: 盡量讓 RG 與其內部資源位於同一 Region。

---

## Checklists & workflows｜檢查清單與流程

### 資源命名與組織檢核表 (Naming & Organization Checklist)

在建立新專案或環境時，請執行以下檢核：

- [ ] **Naming Convention**: 是否遵循 `[Resource]-[App]-[Env]-[Region]` 格式？(例如: `st-myapp-prod-japaneast`)
- [ ] **Region Selection**: 是否已確認資料居留權 (Data Residency) 與延遲需求選擇正確 Region？
- [ ] **Resource Grouping**: 這些資源是否具有相同的生命週期？(會一起部署/刪除嗎？)
- [ ] **Tagging**: 是否已套用最少必要標籤？
    - `Environment` (e.g., Production, Dev)
    - `CostCenter` (e.g., IT-101)
    - `Owner` (e.g., team-backend)
    - `ManagedBy` (e.g., Terraform, Manual)
- [ ] **Locks**: 生產環境的 Stateful 資源 (DB, Storage) 是否已加上 `CanNotDelete` 鎖？

### 訂用帳戶申請決策樹 (Subscription Decision Tree)

當新需求出現時，判斷是否需要新 Subscription：

1.  **是全新的業務單位 (Business Unit) 嗎？** -> `Yes: New Subscription`
2.  **是完全不同的環境 (Prod vs Dev) 嗎？** -> `Yes: New Subscription` (強烈建議)
3.  **是否預期會消耗大量 Quota (如數千個 vCPU)？** -> `Yes: New Subscription`
4.  **是否需要完全獨立的 IAM 權限模型？** -> `Yes: New Subscription`
5.  **如果以上皆非** -> 使用現有 Subscription 中的新 Resource Group。

---

## Real-world examples｜實戰案例

### Scenario: Scaling a SaaS Startup
一家 SaaS 新創公司從單體架構轉向微服務，並準備進行 SOC2 合規認證。

#### Before (Anti-Pattern)
*   **Subscription**: `MyStartup-Azure` (單一訂閱)
*   **Resource Groups**:
    *   `All-VMs` (包含 Prod 和 Dev 的 VM)
    *   `Databases`
    *   `Network`
*   **Pain Point**: 開發人員某次測試 Terraform script 時，意外刪除了生產環境的 VNet Peering，導致服務中斷。

#### After (Best Practice - Hub & Spoke)

採用 Management Group 與多 Subscription 架構：

```text
Root Management Group (MyStartup)
├── Platform (MG)
│   ├── Identity-Sub (AD Connect, Bastion)
│   └── Connectivity-Sub (ExpressRoute, Firewall, VPN Gateway)
├── Landing Zones (MG)
│   ├── Online-Prod-Sub
│   │   ├── rg-payment-api-prod-je (Japan East)
│   │   └── rg-frontend-prod-je
│   └── Online-Dev-Sub
│       ├── rg-payment-api-dev-je
│       └── rg-frontend-dev-je
└── Sandbox (MG)
    └── Playground-Sub (每位開發者有權限在此實驗，預算上限 $50/mo)
```

#### Implementation Details
1.  **Policy**: 在 `Online-Prod-Sub` 層級套用 Policy，禁止建立 Public IP (除了特定的 Load Balancer)，強制所有流量經過 Firewall。
2.  **RBAC**: 開發團隊在 `Online-Dev-Sub` 擁有 `Contributor` 權限，但在 `Online-Prod-Sub` 只有 `Reader` 權限（部署透過 CI/CD Service Principal 進行）。
3.  **Cost**: 財務部門可以清楚看到 `Online-Dev-Sub` 的費用，並要求團隊在非上班時間自動關閉 Dev 機器。