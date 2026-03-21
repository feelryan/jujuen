# 高可用性與災難復原策略 / High Availability (HA) & Disaster Recovery (DR) Strategies

## Mental model｜心智模型

### 1. 故障半徑與洋蔥模型 (The Blast Radius & Onion Model)
不要假設 Azure 不會掛掉，而是要理解故障的影響範圍。將基礎設施視為洋蔥般的同心圓：
- **Level 1 - VM/Instance**: 單一虛擬機故障（硬體損壞、OS 更新重啟）。
- **Level 2 - Rack/Datacenter**: 機櫃或單一資料中心故障（電源、冷卻系統失效）。
- **Level 3 - Availability Zone (AZ)**: 整個區域的一個 Zone 失聯（光纖切斷、重大電力事故）。
- **Level 4 - Region**: 整個地區服務中斷（極端天災、大規模網路攻擊）。

**HA (High Availability)** 通常處理 Level 1~3 的故障，目標是業務不中斷；**DR (Disaster Recovery)** 處理 Level 4 的故障，目標是資料保全與異地重建。

### 2. RTO 與 RPO 的權衡 (The RTO/RPO Trade-off)
所有架構決策都源自於對這兩個指標的定義，而非技術本身：
- **RPO (Recovery Point Objective)**: 你能容忍遺失多少資料？（例如：0 秒、15 分鐘、24 小時）
- **RTO (Recovery Time Objective)**: 你能容忍服務停機多久？（例如：0 秒、4 小時、2 天）

> **Mentor Note**: RTO/RPO 趨近於 0，成本趨近於無限大。工程師的職責不是追求「永遠不掛」，而是協助業務方在「成本」與「風險」之間找到平衡點。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 區域內高可用：Availability Zones (AZs)
在同一個 Region 內，利用 AZ 實現資料中心級別的容錯。
- **Compute**: 使用 Virtual Machine Scale Sets (VMSS) 並設定 `Zone Redundant`，或在 AKS 中啟用 Multi-AZ node pools。
- **Storage**: 選擇 `ZRS` (Zone-redundant storage) 而非 `LRS`。
- **Database**: 使用 Azure SQL "Zone Redundant" configuration 或 Cosmos DB 的 Multi-master/Single-master with zone redundancy。

### 2. 跨區域災難復原：Region Pairs & Geographies
利用 Azure 預定義的 **Region Pairs** (如 East US & West US, Southeast Asia & East Asia) 進行異地備援。
- **Active-Active (Hot/Hot)**:
  - 兩個 Region 同時服務流量。
  - **Load Balancer**: 使用 **Azure Front Door** 或 **Traffic Manager** 進行全域流量導向。
  - **Database**: Cosmos DB (Multi-region writes) 或 SQL Database (Active Geo-Replication)。
  - *優點*: RTO/RPO 接近 0。*缺點*: 成本雙倍，需處理資料衝突與最終一致性。
- **Active-Passive (Hot/Warm)**:
  - 主要 Region 服務流量，次要 Region 運行最小規模實例或僅同步資料。
  - 當主要 Region 故障時，擴展次要 Region 並切換流量 (Failover)。
  - **Database**: SQL Auto-failover groups。
- **Active-Passive (Hot/Cold)**:
  - 僅備份資料到異地 (GRS Storage, Azure Backup)。
  - 災難發生時，使用 **Azure Site Recovery (ASR)** 或 IaC 腳本在異地重新部署資源。
  - *優點*: 最便宜。*缺點*: RTO 較長 (數小時至數天)。

### 3. 應用層韌性 (Application Resilience)
HA 不僅是基礎設施的事，程式碼必須具備自我修復能力。
- **Retry Pattern**: 對暫時性故障 (Transient Failures) 進行重試（需搭配 Exponential Backoff）。
- **Circuit Breaker**: 當下游服務持續失敗時，快速失敗 (Fail fast) 以避免耗盡資源。
- **Health Checks**: 提供準確的 `/health` 端點給 Load Balancer，區分 `Liveness` (我還活著嗎) 與 `Readiness` (我可以接客了嗎)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤把備份當 DR (Backup is not DR)
- **陷阱**: 認為有了 Azure Backup 就萬無一失。
- **現實**: 備份只是檔案，DR 是「讓服務重新跑起來的能力」。如果你沒有自動化還原流程，在災難當下人工重建環境通常會失敗（因為人會慌，且文件通常過期）。

### 2. 忽略跨區流量成本 (Ignoring Egress Costs)
- **陷阱**: 設計了 Active-Active 架構，卻沒計算 Region 之間的資料同步流量費。
- **現實**: 跨 Region 的資料傳輸（Data Transfer Out）是要收費的。頻繁的資料同步可能導致帳單暴增。

### 3. 硬編碼依賴 (Hardcoded Dependencies)
- **陷阱**: 在程式碼或設定檔中寫死特定 Region 的 IP 或 Endpoint（例如 `db-prod-eastus.database.windows.net`）。
- **現實**: Failover 到 West US 時，程式仍嘗試連線到已掛掉的 East US 資料庫。應使用 CNAME 或 Failover Group Listener (如 `db-prod.database.windows.net`)。

### 4. 狀態相依的應用層 (Stateful App Tier)
- **陷阱**: 在 Web Server 本地磁碟儲存 Session 或上傳的檔案。
- **現實**: 當 VM 故障轉移或擴展時，使用者 Session 遺失。應使用 Redis (Azure Cache for Redis) 存 Session，Blob Storage 存檔案。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the right strategy
1. **Is data loss acceptable?**
   - Yes (hours): Use **Backup/Restore (Cold DR)**.
   - No (seconds/minutes): Go to step 2.
2. **Is downtime acceptable?**
   - Yes (minutes/hours): Use **Active-Passive (Warm DR)** with ASR or Pilot Light.
   - No (near zero): Use **Active-Active (Hot DR)**.
3. **Budget constraints?**
   - Tight: Stick to **Multi-AZ** within one region + **GRS Backup**.
   - Flexible: **Multi-Region**.

### Pre-flight Checklist (Before Go-Live)
- [ ] **SLA Alignment**: 確認所選 Azure 服務的複合 SLA 是否高於業務承諾的 SLA (e.g., App Service 99.95% * SQL DB 99.99% ≈ 99.94%)。
- [ ] **Zone Redundancy**: 確認所有支援的服務 (VM, AKS, SQL, Storage) 都已啟用 Availability Zones。
- [ ] **Failover Test**: 實際上執行過一次 Failover 演練（不只是紙上談兵）。
- [ ] **IaC Readiness**: 基礎設施是否完全代碼化？能否用 Terraform/Bicep 在另一個 Region 快速重建無狀態資源？
- [ ] **Quotas Check**: 確認 DR Region 的 vCPU Quota 足夠支撐 Failover 後的負載。

---

## Real-world examples｜實戰案例

### Scenario A: Mission-Critical Banking App (RTO < 5min, RPO < 1min)
*High Cost, Maximum Resilience*

- **Traffic Entry**: Azure Front Door (Global Load Balancing).
- **Compute**: AKS Clusters deployed in `East US` and `West US` (Region Pair).
  - Both regions active, serving traffic.
- **Database**: Azure SQL Database with **Active Geo-Replication**.
  - Read-Scale enabled: Read traffic routed to local region replicas.
  - Write traffic routed to Primary region.
- **Failover Flow**:
  1. Front Door detects `East US` health probe failure.
  2. Front Door routes all traffic to `West US`.
  3. Automation triggers SQL Failover to promote `West US` to Primary.
  4. App connects to DB via Failover Group Listener (no config change needed).

### Scenario B: Internal Reporting Tool (RTO < 4h, RPO < 24h)
*Cost Optimized, Sufficient Resilience*

- **Traffic Entry**: Application Gateway (Regional).
- **Compute**: App Service (Standard Plan) in `Southeast Asia`.
- **Database**: Azure SQL Database (Standard Tier).
- **Storage**: Azure Storage Account with **GRS** (Geo-Redundant Storage).
- **DR Strategy**:
  - **Backup**: Database performs automated geo-backups.
  - **Recovery**:
    - Use **Azure Site Recovery** or **Bicep scripts** to spin up App Service in `East Asia` only when disaster strikes.
    - Restore Database from GRS backup to the new region.
    - Update DNS CNAME to point to the new region's endpoint.