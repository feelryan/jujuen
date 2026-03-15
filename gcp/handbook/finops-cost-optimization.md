# FinOps：成本優化與帳務管理 / FinOps: Cost Optimization & Billing Management

## Mental model｜心智模型

在 GCP 實踐 FinOps，不應只被視為「省錢 (Cost Cutting)」，而是「讓每一分錢創造最大商業價值 (Unit Economics)」。你需要建立以下三個核心認知：

1.  **雲端帳單是營運指標，而非水電費 (Operational Metric, not Utility Bill)**
    *   不要等到月底才看帳單。成本應視為與 Latency 或 Error Rate 同等重要的即時指標。
    *   **Visibility (可視性)** 是第一步：如果無法將成本歸因到特定的 Team、Service 或 Environment，就無法優化。

2.  **動態採購策略 (Dynamic Procurement)**
    *   GCP 的定價模型是動態的。你需要根據工作負載的特性（Stateful vs. Stateless, Predictable vs. Spiky）選擇不同的付費模式：
        *   **On-demand**: 適合不可預測的短期波動。
        *   **Spot VMs**: 適合可容錯、無狀態的批次處理（最高節省 60-91%）。
        *   **CUDs (Committed Use Discounts)**: 適合穩定的基底負載（Base Load）。

3.  **去中心化的責任制 (Decentralized Accountability)**
    *   工程團隊必須對自己架構的成本負責。DevOps/SRE 的角色是提供工具與數據（Dashboarding），而非單獨承擔「砍預算」的責任。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 標籤策略與成本歸因 (Labeling Strategy & Cost Allocation)
沒有 Label 就沒有 FinOps。所有資源必須強制打上標籤。
*   **必備標籤 (Mandatory Labels)**：
    *   `environment`: `prod`, `staging`, `dev`
    *   `service`: `payment-api`, `data-pipeline`
    *   `owner`: `team-backend`, `team-data`
    *   `cost-center`: `1001` (對應財務部門代碼)
*   **實作方式**：透過 Terraform (`default_labels` in provider) 或 Organization Policy 強制執行。

### 2. 運算資源優化 (Compute Optimization)
*   **GKE 混合節點池 (Mixed Node Pools)**：
    *   **System/Stateful Pods**: 跑在 On-demand 或 CUD 覆蓋的 Standard Node Pool。
    *   **Stateless/Batch Pods**: 跑在 Spot VMs Node Pool，並配置 Cluster Autoscaler。
    *   *Tip*: 使用 `node-termination-handler` 優雅處理 Spot VM 回收。
*   **CUD 階梯式購買 (Laddering CUDs)**：
    *   不要一次買滿 100% 預估用量。
    *   先覆蓋 60-70% 的穩定用量，觀察一季後再疊加新的合約。優先使用 **Flexible CUDs ($/hour spend-based)**，雖然折扣較低但適用於多種 VM Family，避免被特定硬體綁死。

### 3. BigQuery 成本控制 (BigQuery Cost Control)
BigQuery 是最容易產生「意外天價帳單」的服務。
*   **強制分區與叢集 (Partitioning & Clustering)**：對大表強制要求 Partition Filter，減少全表掃描。
*   **配額限制 (Custom Quotas)**：在 Project 或 User 層級設定 `Query usage` 上限 (e.g., 每天最多 10 TB)。
*   **Flex Slots vs. On-demand**：當分析需求平穩且量大時，切換至 Editions (Standard/Enterprise) 可能比 On-demand ($5/TB) 更划算。

### 4. 儲存生命週期 (Storage Lifecycle Management)
*   設定 GCS Bucket 的 Lifecycle Rule：
    *   `> 30 days` -> Nearline
    *   `> 90 days` -> Coldline
    *   `> 365 days` -> Archive
*   *注意*：對於頻繁存取的小檔案，過早轉入 Coldline/Archive 會因為「最小存取費用」反而變貴。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 忽視跨區流量費用 (Ignoring Cross-Zone/Region Egress)
*   **陷阱**：在同一個 Region 內，不同 Zone 之間的 VM 通訊是收費的（Cross-zone egress）。
*   **後果**：高流量的 Kafka/Database Cluster 如果跨 Zone 頻繁同步，網路費可能比 VM 本身還貴。
*   **解法**：盡量讓高頻通訊的服務位於同一 Zone，或評估網路費是否值得換取高可用性 (HA)。

### 2. 殭屍資源 (Zombie Resources)
*   **Unattached Persistent Disks**：刪除 VM 時忘了勾選「同時刪除 Boot Disk」，導致磁碟持續計費。
*   **Unused Static IPs**：GCP 對「未綁定」的靜態 IP 收費比「已綁定」的還高（為了懲罰囤積 IP）。
*   **Abandoned Load Balancers**：Forwarding Rules 即使沒流量也會收基本費。

### 3. 盲目購買 CUD (Blind CUD Commitment)
*   **陷阱**：為了折扣鎖定 3 年 N1 機器，結果一年後 GCP 推出性價比更高的 N2D 或 T2A (Arm)。
*   **解法**：除非架構極度穩定，否則優先考慮 1 年期合約，或使用 Flexible CUDs。

### 4. BigQuery `SELECT *`
*   **陷阱**：開發者習慣性 `SELECT *`，即使使用了 `LIMIT 10`，BigQuery 仍會掃描所有欄位（Columnar Storage 特性）。
*   **解法**：Code Review 時嚴格檢查 SQL，或使用 `dbt` 等工具規範模型。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Compute Purchasing Strategy
1.  **Is the workload stateful?**
    *   Yes -> On-demand or CUD.
    *   No -> Can it tolerate interruption?
        *   Yes -> **Spot VMs**.
        *   No -> On-demand or CUD.
2.  **Is the usage predictable (24/7)?**
    *   Yes -> Apply **Committed Use Discounts (CUD)** covering ~70% of baseline.
    *   No -> Rely on **Sustained Use Discounts (SUD)** (automatic).

### Weekly FinOps Checklist (週檢核清單)
- [ ] **Review Billing Anomalies**: 檢查 GCP Billing Console 的 "Cost trend" 是否有異常突波。
- [ ] **Check Recommender API**: 查看 GCP 自動生成的 "Idle VM" 或 "Rightsizing" 建議。
- [ ] **Identify Unattached Disks**: 執行腳本掃描孤兒磁碟。
- [ ] **Verify Budget Alerts**: 確認預算警報（50%, 90%, 100%）設定是否正確，通知管道（Slack/Email）是否暢通。

### Monthly Optimization Workflow (月優化流程)
- [ ] **CUD Utilization Analysis**: 承諾的使用折扣利用率是否低於 95%？如果是，暫停購買新合約。
- [ ] **BigQuery Top Spenders**: 找出花費最高的前 10 個 Query，進行 SQL 優化。
- [ ] **Label Compliance Audit**: 掃描未標記 Label 的資源並通知負責人。

---

## Real-world examples｜實戰案例

### Case 1: 自動化清理孤兒磁碟 (Automated Cleanup of Orphaned Disks)
許多團隊在刪除 GKE Cluster 或 VM 後，遺留了大量的 PD (Persistent Disks)。

**Solution Pattern**:
建立一個 Cloud Scheduler + Cloud Functions (Go/Python)。
```python
# Pseudo-code logic
def cleanup_disks(request):
    disks = list_all_disks(project_id)
    for disk in disks:
        if disk.users is None: # No VM attached
            age = get_disk_age(disk)
            if age > 7_days:
                snapshot_disk(disk) # Safety backup
                delete_disk(disk)
                log_savings(disk.size_gb)
```

### Case 2: BigQuery 成本護欄 (BigQuery Cost Guardrails)
某數據團隊發現實習生不小心跑了一個 Query 掃描了 50TB 的數據，導致單次查詢成本高達 $250 USD。

**Solution Pattern**:
1.  **Dry Run Check**: 在 CI/CD 或 Query 工具中，執行 Dry Run 預估 Bytes Processed。
2.  **Max Bytes Billed**: 在 Client Library 設定限制。

```go
// Go Example: 設定單次查詢最大預算
q := client.Query("SELECT * FROM `huge_table` WHERE ...")
q.MaxBytesBilled = 10 * 1024 * 1024 * 1024 // Limit to 10 GB
// 如果 Query 預估超過 10GB，會直接報錯失敗，不會產生費用
```

### Case 3: GKE 的 "Night Mode" (GKE Night Mode for Dev/Staging)
開發環境在非上班時間（晚上、週末）通常是閒置的。

**Solution Pattern**:
使用 **Kube-downscaler** 或 Cloud Scheduler 調整 Node Pool 大小。
*   **平日 20:00**: 將 Dev Cluster 的 Deployment replicas 縮減為 0 (或 1)。
*   **平日 08:00**: 恢復 replicas 數量。
*   **結果**: 開發環境運算成本直接減少約 60% (108小時閒置 / 168小時總時數)。