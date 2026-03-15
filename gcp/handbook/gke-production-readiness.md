# GKE 生產環境就緒清單 (Production Readiness) / GKE Production Readiness Checklist

## Mental model｜心智模型

在將 GKE (Google Kubernetes Engine) 推向生產環境前，必須從「管理伺服器」的思維轉變為「管理資源池與合約」的思維。

1.  **動態艦隊 vs. 靜態堡壘 (Dynamic Fleet vs. Static Fortress)**：
    不要將 Node 視為永久存在的伺服器。GKE 的 Node 是可隨時被替換、擴展或縮減的「消耗品」。你的架構必須容忍 Node 隨時消失（Preemptible/Spot instances 或升級時）。
2.  **控制平面即服務 (Control Plane as a Service)**：
    GKE 幫你管理了 Master Node (Control Plane)，但這不代表它是無限強大的黑盒子。你必須理解它的 SLA (Regional vs. Zonal) 以及它與 Worker Node 之間的網路通訊模式。
3.  **VPC-native 是現代標準**：
    早期的 GKE 使用 Routes-based 網路，但現代 GKE 生產環境應將 Pod 視為 VPC 網路的一等公民 (First-class citizen)。這意味著 Pod IP 是 VPC 子網段的一部分 (Alias IPs)，而非覆蓋網路 (Overlay)，這對於效能與混合雲連線至關重要。

## Patterns & best practices｜常見模式與最佳實務

### 1. 叢集架構與網路 (Cluster Architecture & Networking)
-   **VPC-native Clusters (Alias IPs)**：
    -   **Why**: 這是目前的預設且建議模式。它移除了 Docker bridge 的封包封裝開銷，並允許 Pod IP 直接被 VPC 內的防火牆規則或 Cloud Router (Interconnect/VPN) 識別。
    -   **Practice**: 規劃 Secondary CIDR ranges 給 Pods 和 Services 使用，避免 IP 耗盡。
-   **Private Clusters (私有叢集)**：
    -   **Why**: 節點不應擁有 Public IP。這能大幅減少攻擊面。
    -   **Practice**: 設定 `enable_private_nodes = true`。若需存取外部網路，透過 Cloud NAT 處理。
-   **Regional Clusters (區域叢集)**：
    -   **Why**: 為了高可用性 (HA)。Regional cluster 會在三個 Zone 部署 Control Plane 和 Nodes。即使單一 Zone 故障，叢集仍能運作且可被管理。
    -   **Trade-off**: Control Plane 費用較高（但在生產環境這是必要的保險）。

### 2. 彈性擴展與資源管理 (Scaling & Resource Management)
-   **Cluster Autoscaler (CA) + Node Auto-provisioning (NAP)**：
    -   **Pattern**: 設定多個 Node Pools (例如：一般用途、高記憶體、GPU)，並啟用 CA。
    -   **NAP**: 對於不可預測的工作負載，啟用 Node Auto-provisioning，讓 GKE 自動決定最佳的機器型號並建立新的 Node Pool。
-   **Workload Identity**：
    -   **Must-do**: **絕對不要**將 Service Account Key (JSON files) 掛載到 Pod 中。
    -   **Practice**: 使用 Workload Identity 將 K8s ServiceAccount (KSA) 與 Google Service Account (GSA) 綁定。這是存取 GCS、BigQuery 或 Cloud SQL 最安全的方式。

### 3. 維運與升級 (Operations & Upgrades)
-   **Release Channels & Maintenance Windows**：
    -   **Pattern**: 生產環境使用 `Stable` channel，開發環境使用 `Regular` 或 `Rapid`。
    -   **Config**: 設定維護視窗 (Maintenance Windows) 和排除視窗 (Exclusions)，確保升級不會發生在業務高峰期（例如黑色星期五）。
-   **Dataplane V2**：
    -   **Practice**: 新叢集建議啟用 Dataplane V2 (基於 eBPF)，它整合了網路策略 (Network Policy) 執行與可觀測性，無需額外安裝 Calico。

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 安全性地雷 (Security Risks)
-   **使用預設 Service Account**：
    -   **Anti-pattern**: 讓 Node 使用專案預設的 Compute Engine Service Account。
    -   **Risk**: 預設 SA 通常擁有 `Editor` 權限。如果容器被攻破，攻擊者將擁有整個 GCP 專案的控制權。
    -   **Fix**: 建立最小權限 (Least Privilege) 的專案級 Service Account 給 Node Pool 使用。
-   **開放 Control Plane 公網存取**：
    -   **Anti-pattern**: 允許 `0.0.0.0/0` 存取 Master Endpoint。
    -   **Fix**: 啟用 "Master Authorized Networks"，只允許公司 VPN IP 或特定跳板機 IP 存取 `kubectl`。

### 2. 資源配置錯誤 (Resource Misconfiguration)
-   **忽略 Requests/Limits**：
    -   **Anti-pattern**: 部署沒有設定 CPU/Memory requests 與 limits 的 Pod。
    -   **Consequence**: 導致 "Noisy Neighbor" 問題，關鍵服務被餓死；或者 Cluster Autoscaler 無法正確觸發（因為它依賴 Requests 計算）。
-   **SNAT 耗盡**：
    -   **Anti-pattern**: 大量 Pod 透過單一 Public IP 連線外部 API。
    -   **Fix**: 使用 Cloud NAT 並適當配置每個 VM 的最小連接埠數量。

### 3. 可用性陷阱 (Availability Traps)
-   **缺乏 Pod Disruption Budgets (PDB)**：
    -   **Pitfall**: 當 GKE 進行節點升級時，一次性排空 (Drain) 太多 Pod，導致服務中斷。
    -   **Fix**: 設定 PDB，確保在維護期間至少有 N% 的 Pod 是可用的。
-   **依賴本機儲存 (Local Disk)**：
    -   **Pitfall**: 假設 Pod 重啟後資料還在 Node 上。
    -   **Fix**: 使用 Persistent Volumes (PV) 搭配 Regional Persistent Disks 以確保跨 Zone 的資料可用性。

## Checklists & workflows｜檢查清單與流程

在將服務推上 Production 前，請逐一核對以下項目：

### Infrastructure & Networking
- [ ] **VPC-native**: 確認叢集已啟用 VPC-native (Alias IP)。
- [ ] **Private Cluster**: 確認 Nodes 沒有 Public IP，且出站流量透過 Cloud NAT。
- [ ] **Regional Control Plane**: 生產環境已選用 Regional Cluster。
- [ ] **Authorized Networks**: Master Endpoint 僅限特定 CIDR 存取。
- [ ] **Maintenance Window**: 已設定維護視窗，避開業務高峰。

### Security & IAM
- [ ] **Least Privilege Node SA**: Node Pool 使用自定義的 Service Account（非 Default Compute SA）。
- [ ] **Workload Identity**: 已啟用並配置給需要存取 GCP API 的 Pod。
- [ ] **Shielded Nodes**: 已啟用 Shielded GKE Nodes (Secure Boot, Integrity Monitoring)。
- [ ] **Network Policy**: (選用) 是否已定義 Namespace 間的隔離策略？

### Workload Configuration
- [ ] **Resource Requests/Limits**: 所有容器都設定了合理的 CPU/Memory 請求與限制。
- [ ] **Liveness & Readiness Probes**: 應用程式已配置健康檢查，避免流量導向未就緒的 Pod。
- [ ] **Pod Disruption Budget (PDB)**: 已設定 PDB 以保護升級時的可用性。
- [ ] **Pod Anti-Affinity**: (選用) 設定反親和性，避免所有 Pod 擠在同一台 Node 或同一個 Zone。

### Observability
- [ ] **Cloud Logging/Monitoring**: 確認系統與應用日誌已正確送至 Cloud Logging。
- [ ] **Prometheus**: (若使用) 確認 Managed Service for Prometheus 或自行架設的收集器運作正常。

## Real-world examples｜實戰案例

### 案例：高流量電商網站的 GKE 設定

**情境**：一個需要應對「雙11」瞬間高流量的電商平台。

**架構決策**：

1.  **Node Pools 設計**：
    -   `default-pool`: 執行 kube-system 元件，使用 `e2-standard`。
    -   `app-pool`: 執行核心應用，啟用 **Cluster Autoscaler**，範圍 3 ~ 50 nodes。使用 `c2-standard` (Compute Optimized) 以獲得更佳的 CPU 效能。
    -   `batch-pool`: 執行背景報表任務，使用 **Spot Instances (Preemptible)** 以節省成本，並容忍中斷。

2.  **Terraform 實作片段 (Infrastructure as Code)**：

```hcl
resource "google_container_cluster" "primary" {
  name     = "prod-ecommerce-cluster"
  location = "asia-east1" # Regional cluster

  # 啟用 VPC-native
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods-range"
    services_secondary_range_name = "services-range"
  }

  # 私有叢集設定
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false # 允許透過公網存取 Master (需搭配 Authorized Networks)
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # 安全性：限制 Master 存取
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "203.0.113.0/24"
      display_name = "Office VPN"
    }
  }

  # 啟用 Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

resource "google_container_node_pool" "app_pool" {
  name       = "app-pool"
  cluster    = google_container_cluster.primary.id
  location   = "asia-east1"
  
  autoscaling {
    min_node_count = 3
    max_node_count = 50
  }

  node_config {
    machine_type = "c2-standard-4"
    
    # 關鍵：使用自定義 SA，而非預設 SA
    service_account = google_service_account.gke_node_sa.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    
    # 安全性增強
    shielded_instance_config {
      enable_secure_boot = true
    }
  }
}
```

3.  **HPA (Horizontal Pod Autoscaler) 策略**：
    不只依賴 CPU，而是使用 **Custom Metrics (External Metrics)**。例如，根據 Cloud Pub/Sub 的 `num_undelivered_messages` 或 Load Balancer 的 `request_count` 來觸發擴展，確保在 CPU 飆高前就先擴展 Pod 數量。