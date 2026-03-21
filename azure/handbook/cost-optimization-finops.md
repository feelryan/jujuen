# 成本優化與 FinOps 策略 / Cost Optimization & FinOps Strategies

## Mental model｜心智模型

在雲端環境中，成本不應僅被視為財務部門的責任，而是工程架構中的核心「非功能性需求 (Non-functional Requirement)」。有效的 FinOps 不是單純的「省錢」，而是追求「單位經濟效益的最大化」。

### 1. The FinOps Lifecycle: Inform, Optimize, Operate
FinOps 是一個持續的迭代過程，而非一次性的專案：
*   **Inform (可視化)**：你無法管理你看不到的東西。首要任務是透過 Tagging (標籤) 與 Cost Analysis 釐清「誰花了錢」以及「錢花在哪」。
*   **Optimize (優化)**：根據數據進行調整。這包括「費率優化」(Rate Optimization，如 RI/Savings Plans) 與「用量優化」(Usage Optimization，如關機、縮編)。
*   **Operate (營運)**：將成本意識融入 DevOps 文化。建立自動化治理 (Governance) 與預算警示，讓工程師對成本負責。

### 2. Variable Cost Model (變動成本模型)
從地端 (On-prem) 的 CapEx (資本支出) 轉向雲端的 OpEx (營運支出) 時，心態需從「預先過度配置以防萬一 (Provision for peak)」轉變為「按需配置並動態調整 (Provision for demand)」。
> **Core Principle**: The most expensive resource is the one you are not using. (最昂貴的資源是你沒在用卻付費的資源。)

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 強制標籤策略 (Enforced Tagging Strategy)
沒有標籤的資源是成本黑洞。
*   **Pattern**: 使用 **Azure Policy** 強制要求在 Resource Group 或 Resource 層級必須包含特定標籤（如 `CostCenter`, `Environment`, `Owner`, `Project`）。
*   **Inheritance**: 設定 Policy 讓資源自動繼承 Resource Group 的標籤，減少人工失誤。

### 2. 承諾折扣分層 (Commitment Discount Layering)
不要全部依賴 Pay-as-you-go (隨用隨付)。
*   **Reserved Instances (RI)**: 適用於 24/7 運行且規格固定的基底負載 (Base load)，如資料庫或核心 VM。通常提供最高折扣。
*   **Azure Savings Plans**: 適用於動態運算需求 (Compute)。比 RI 彈性更高（跨 Region、跨 VM 系列），但折扣略低。
*   **Strategy**: 先購買覆蓋 60-70% 基底負載的 RI/Savings Plan，剩餘波動部分使用 Spot 或 Pay-as-you-go。

### 3. 開發環境的動態開關 (Dev/Test Snoozing)
開發與測試環境不需要 7x24 小時運行。
*   **Pattern**: 使用 **Azure Automation Runbooks** 或 **Logic Apps**，設定在非工作時間（如平日晚上 8 點至早上 8 點，以及週末）自動停止 (Deallocate) VM 與 AKS Clusters。
*   **Impact**: 僅僅是週末關機就能節省約 30% 的運算成本。

### 4. 儲存分層生命週期 (Storage Lifecycle Management)
資料隨著時間推移，存取頻率會下降。
*   **Hot Tier**: 頻繁存取的活躍資料。
*   **Cool Tier**: 至少存放 30 天，存取頻率較低。
*   **Archive Tier**: 至少存放 180 天，極少存取（備份/合規歸檔）。
*   **Automation**: 設定 Azure Blob Storage Lifecycle Management 規則，自動將舊資料降級。

### 5. Spot VM 與無狀態工作負載 (Spot Instances for Stateless Workloads)
對於可中斷、批次處理或無狀態的微服務。
*   **Pattern**: 在 AKS 中設定多個 Node Pools。系統池 (System Pool) 使用標準 VM，使用者池 (User Pool) 針對批次作業或 CI/CD Agents 使用 Spot VM。
*   **Handling Eviction**: 應用程式必須設計為具備容錯能力 (Fault-tolerant) 並能優雅處理中斷訊號。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 殭屍資源 (Zombie Resources / Orphaned Resources)
最常見的浪費來源。
*   **Orphaned Disks**: 刪除 VM 時，預設**不會**刪除關聯的 Managed Disk。這些磁碟會持續計費。
*   **Unattached Public IPs**: 未綁定網卡的靜態 IP。
*   **Empty App Service Plans**: 即使沒有部署 App，App Service Plan 只要存在就會計費。

### 2. 錯誤的規格選型 (Right-sizing based on Specs, not Metrics)
*   **Pitfall**: 依照地端伺服器的規格直接遷移 (Lift & Shift)，例如地端是 16 vCPU，上雲就開 16 vCPU。
*   **Reality**: 雲端硬體通常較新，效能較好；且地端通常嚴重過度配置。應根據實際 CPU/Memory **使用率 (Metrics)** 來調整規格，而非規格表。

### 3. 忽略資料傳輸費用 (Ignoring Data Egress Costs)
*   **Pitfall**: 跨 Region 或跨 Zone 的流量通常需要付費。
*   **Anti-pattern**: 應用程式與資料庫部署在不同 Region，導致產生鉅額的 Bandwidth 費用且延遲增加。

### 4. 購買 RI 後卻閒置 (Buying RI and Forgetting)
*   **Pitfall**: 購買了 RI，但後來更改了 VM 系列（例如從 D 系列換到 E 系列）或 Region，導致 RI 沒有匹配到任何資源而浪費。
*   **Fix**: 定期檢查 RI Utilization 報告。

---

## Checklists & workflows｜檢查清單與流程

### Weekly/Monthly Cost Governance Checklist

- [ ] **Review Azure Advisor (檢視 Azure 顧問)**
    - [ ] 檢查 "Cost" 分類下的建議（如 Right-sizing, RI 購買建議）。
- [ ] **Identify Orphaned Resources (識別孤兒資源)**
    - [ ] 執行腳本尋找 `ManagedBy` 屬性為空的 Disks。
    - [ ] 檢查未關聯的 Public IPs 與 NICs。
- [ ] **Analyze Budget Alerts (分析預算警示)**
    - [ ] 確認目前花費是否符合預測 (Forecast)。
    - [ ] 若有異常突波 (Spike)，鑽取 (Drill down) 到特定 Resource Group 或 Service。
- [ ] **Check Reservation Utilization (檢查預留實體使用率)**
    - [ ] 確保 RI 使用率維持在 95% 以上。若低於此數值，考慮交換 (Exchange) 或調整架構。
- [ ] **Review Storage Access Tiers (檢視儲存存取層級)**
    - [ ] 確認是否有大量資料滯留在 Hot Tier 但未被存取。

### Decision Tree: New Resource Provisioning
當團隊需要開新資源時的決策流程：

1.  **Is it temporary?** (是暫時的嗎？)
    *   Yes -> 使用 Spot VM 或 Dev/Test Pricing (若適用)。設定自動刪除日期。
    *   No -> 進入下一步。
2.  **Is the workload predictable?** (負載可預測嗎？)
    *   Yes -> 評估購買 Reserved Instances (RI)。
    *   No -> 考慮 Azure Savings Plan 或 Auto-scaling (VMSS/AKS)。
3.  **Can it use PaaS/Serverless?** (能用 PaaS 嗎？)
    *   Yes -> 優先選用 (如 Azure Functions, SQL Elastic Pools) 以降低管理成本與閒置成本。
    *   No -> 使用 IaaS VM，但必須設定 Auto-shutdown (若非 24/7)。

---

## Real-world examples｜實戰案例

### Example 1: Finding Orphaned Disks with Azure CLI
這是一個經典的 FinOps 腳本，用於找出刪除 VM 後被遺忘的磁碟。

```bash
# 列出所有沒有被 VM 連結的 Managed Disks (Orphaned Disks)
# 這些磁碟每個月都在燒錢，且通常無人使用
az disk list --query "[?managedBy==null].[id, name, resourceGroup, diskSizeGb, sku.name]" \
  --output table

# Action: 確認後，刪除這些磁碟或將其備份到 Blob Storage (更便宜) 後刪除。
```

### Example 2: AKS Cost Optimization with Spot Node Pools
在 Kubernetes 環境中混合使用標準節點與 Spot 節點。

```yaml
# AKS Node Pool configuration snippet
# User Pool for Batch Jobs using Spot Instances
apiVersion: agentpool.microsoft.com/v1
kind: AgentPool
metadata:
  name: batchpool
spec:
  mode: User
  osType: Linux
  vmSize: Standard_D4s_v3
  scaleSetPriority: Spot  # 關鍵設定：使用 Spot 實體
  spotMaxPrice: -1        # -1 表示願意支付至隨用隨付價格上限，不因價格波動被踢，只因容量不足被踢
  enableAutoScaling: true
  minCount: 0             # 沒工作時縮減到 0
  maxCount: 10
  nodeLabels:
    workload: batch
    cost: spot
  nodeTaints:
    - key: "sku"
      value: "spot"
      effect: "NoSchedule" # 防止關鍵 Pod 誤排程到此節點
```

### Example 3: SQL Elastic Pools for SaaS
**情境**：一家 SaaS 公司為每個客戶提供獨立的 SQL Database。
**問題**：每個客戶的使用高峰不同，若為每個 DB 單獨購買高規格 DTU/vCore，成本極高且大部分時間閒置。
**解法**：使用 **SQL Elastic Pools**。
*   將數百個 DB 放入同一個 Pool。
*   資源由 Pool 共享。
*   **結果**：只要所有客戶不同時達到高峰，成本可降低 50% 以上，且單一客戶在高峰時可獲取 Pool 中的大量資源。