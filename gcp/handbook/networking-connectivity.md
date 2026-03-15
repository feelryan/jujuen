# 進階網路架構：Shared VPC 與混合雲連線 / Advanced Networking: Shared VPC & Hybrid Connectivity

## Mental model｜心智模型

在 GCP 的進階網路設計中，你必須將思維從「單一專案的網路設定」轉變為「組織級別的網路治理」。

### 1. 網路即公用設施 (Network as a Utility)
想像 Shared VPC 就像是一棟商業大樓的**水電基礎設施**：
- **Host Project (房東/物業管理)**：負責建設網路管線、對外連線 (VPN/Interconnect)、防火牆規則與 DNS。這是集中管理的控制面。
- **Service Projects (租戶)**：各個業務團隊的專案。他們不需要懂怎麼拉電線，只需要將他們的設備 (VMs, GKE Clusters) 插上房東提供的插座 (Subnets) 即可運作。

### 2. 軸輻式架構 (Hub-and-Spoke Topology)
GCP 的全球網路是軟體定義的 (SDN)。在混合雲情境下，最有效的心智模型是 **Hub-and-Spoke**：
- **Hub (Shared VPC)**：流量的匯聚點，負責與 On-premise 或其他雲端連線。
- **Spoke (Service Projects)**：運算資源的所在。
- **關鍵限制**：VPC Peering 是**不可遞移 (Non-transitive)** 的。A Peer B, B Peer C，A **不能**直接連到 C。這就是為什麼 Shared VPC (讓 A, B, C 都在同一個 VPC 內) 比單純的 Peering Mesh 更適合企業內部架構。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Shared VPC 的權限分離 (IAM Separation of Duties)
這是實作 Shared VPC 的核心價值。
- **Network Admins**：在 Host Project 中管理 Subnets、Firewall Rules、Cloud Router。
- **Service Project Admins**：擁有 `Compute Network User` 角色。他們可以「使用」Subnet 中的 IP，但不能修改 Subnet 的 CIDR 或刪除它。
- **GKE 模式**：針對 GKE，務必在 Host Project 的 Subnet 設定 **Secondary CIDR ranges** (Pod & Service ranges)，並授權 Host Service Agent User 權限給 GKE Service Account。

### 2. Private Google Access (PGA) 與安全性
絕大多數後端服務不應擁有 Public IP。
- **Private Google Access**：務必在所有 Subnet 開啟。這讓沒有 Public IP 的 VM 可以透過 Google 內部骨幹網路存取 Google APIs (如 Cloud Storage, BigQuery, Pub/Sub)，而不需經過 NAT 或 Internet。
- **Private Service Connect (PSC)**：若需存取其他 VPC 的服務 (或 Managed Services 如 MongoDB Atlas)，優先使用 PSC 而非 VPC Peering，以避免 CIDR 衝突與路由表爆炸。

### 3. 混合雲 DNS 解析 (Hybrid DNS Resolution)
當地端 (On-prem) 與雲端 (GCP) 需要互通時，DNS 是常被忽略的一環。
- **Inbound Forwarding**：建立 Cloud DNS Policy (Inbound query forwarding)，讓地端透過 VPN/Interconnect 查詢 GCP 的 Private Zone (如 `*.internal`).
- **Outbound Forwarding**：建立 Cloud DNS Forwarding Zone，將特定網域 (如 `*.corp.example.com`) 的查詢轉送回地端 DNS Server。

### 4. 集中式 Egress 控制 (Centralized Egress)
為了資安合規，通常不允許 Service Project 自行建立 Cloud NAT。
- **Pattern**：在 Host Project 建立一組高可用 (HA) 的 Cloud NAT Gateway。所有 Service Projects 的外網流量都統一由此出口，便於監控與 IP Allow-listing 管理。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Peering Mesh Trap (網狀 Peering 陷阱)
- **Anti-pattern**：試圖透過 VPC Peering 連接所有專案 (A<->B, B<->C, A<->C...)。
- **後果**：管理複雜度呈指數上升，且受限於 Peering 數量上限 (預設 25)。最嚴重的是遇到「不可遞移性」導致路由黑洞。
- **修正**：組織內部使用 Shared VPC；只有在連接「完全獨立的外部組織」或「SaaS 服務」時才使用 VPC Peering。

### 2. CIDR Overlap (IP 網段衝突)
- **Anti-pattern**：在 GCP 開立 VPC 時隨意使用 `10.0.0.0/8` 或 `192.168.0.0/16`，未先確認地端網路規劃。
- **後果**：當未來需要建立 VPN/Interconnect 時，發現 IP 衝突，導致必須重建整個網路或使用極其複雜的 NAT 轉換。
- **修正**：在 Day 1 就建立全域 IP Address Management (IPAM) 表，為 GCP 預留專屬 CIDR Block。

### 3. Default VPC Usage (使用預設 VPC)
- **Anti-pattern**：在生產環境使用 GCP 預設建立的 `default` VPC。
- **後果**：`default` VPC 預設包含過於寬鬆的防火牆規則 (SSH/RDP open to 0.0.0.0/0 雖有 tag 但易誤用)，且 Subnet 遍布全球，浪費 IP 空間且難以管理邊界。
- **修正**：永遠刪除 `default` VPC，建立 Custom Mode VPC。

### 4. Firewall Rule Explosion (防火牆規則爆炸)
- **Anti-pattern**：依賴 IP 地址來寫防火牆規則 (例如：Allow `10.1.2.3` to `10.1.2.4`)。
- **後果**：當 VM 重啟或擴展時，規則失效。規則數量迅速達到 Quota 上限。
- **修正**：使用 **Network Tags** 或 **Service Accounts** 作為防火牆的 Source/Target。例如：Allow from tag `frontend` to tag `backend` on port `5432`。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Connectivity Selection
1. **需要連線到哪裡？**
   - **Google APIs (GCS, BQ)** -> 使用 `Private Google Access`。
   - **On-premise (地端)** -> 繼續下一步。
   - **其他 VPC** -> 同組織用 `Shared VPC`，不同組織用 `Peering` 或 `PSC`。
2. **On-premise 頻寬與 SLA 需求？**
   - **< 3 Gbps, 可接受 Internet 波動** -> 使用 `HA VPN`。
   - **> 10 Gbps, 需要專線 SLA** -> 使用 `Dedicated Interconnect`。
   - **需要 SLA 但頻寬需求低** -> 使用 `Partner Interconnect`。

### Shared VPC Setup Checklist
- [ ] **IPAM Planning**: 確認 Host Project 的 CIDR 與地端不衝突。
- [ ] **Enable API**: 在 Host Project 開啟 `Compute Engine API`。
- [ ] **Designate Host**: 在 Organization/Folder 層級將該專案設為 Host Project。
- [ ] **Attach Service Projects**: 將業務專案 Attach 到 Host Project。
- [ ] **IAM Configuration**:
    - [ ] 賦予 Service Project Admins `compute.networkUser` 角色 (針對特定 Subnet)。
    - [ ] 若使用 GKE，賦予 GKE Service Account `Kubernetes Engine Host Service Agent User` 角色。
- [ ] **Firewall Baseline**: 設定 `deny-all-ingress` 作為最低優先級規則，再逐一開啟 `allow`。
- [ ] **Connectivity Test**: 使用 GCP Network Intelligence Center 的 Connectivity Tests 驗證 Service Project VM 到 On-prem 的連通性。

---

## Real-world examples｜實戰案例

### Scenario: The "Landing Zone" for a Fintech Company
一家金融科技公司需要將核心交易系統搬遷至 GCP，要求高安全性與地端連線。

#### Architecture Design
1.  **Host Project (`net-hub-prod`)**:
    *   **VPC**: `vpc-prod-shared` (Custom mode).
    *   **Subnets**:
        *   `sb-app-asia-east1` (10.10.0.0/24) - 供應用程式使用。
        *   `sb-data-asia-east1` (10.10.1.0/24) - 供資料庫使用 (Private Service Connect endpoint)。
        *   `sb-gke-asia-east1` (10.10.2.0/23) - 包含 Secondary Ranges 供 Pods/Services 使用。
    *   **Connectivity**: 兩條 HA VPN Tunnels 連接至地端 Cisco Routers，啟用 BGP 動態路由。
    *   **NAT**: Cloud NAT 設定於 `asia-east1`，允許所有 Subnet 出網。

2.  **Service Project A (`app-trading-prod`)**:
    *   部署 GKE Cluster (Private Cluster)。
    *   GKE Nodes 位於 Host Project 的 `sb-gke-asia-east1`。
    *   開發團隊擁有此專案的 `Container Admin`，但無法更改 VPC 設定。

3.  **Service Project B (`data-warehouse-prod`)**:
    *   部署 Cloud SQL (Private IP)。
    *   透過 Private Service Access (PSA) 連接至 Host VPC。

#### Troubleshooting Example (Terraform snippet)
*問題：GKE 建立失敗，錯誤訊息顯示無法分配 IP。*
*診斷：Shared VPC 的 Secondary Range 在 Terraform 中未正確參照。*

**Correct Terraform Pattern:**
```hcl
# In Service Project Terraform
resource "google_container_cluster" "primary" {
  name     = "trading-cluster"
  location = "asia-east1"
  project  = "app-trading-prod"
  
  # 關鍵：參照 Host Project 的網路資源
  network    = "projects/net-hub-prod/global/networks/vpc-prod-shared"
  subnetwork = "projects/net-hub-prod/regions/asia-east1/subnetworks/sb-gke-asia-east1"

  ip_allocation_policy {
    # 必須精確對應 Host Project Subnet 中定義的 Secondary Range 名稱
    cluster_secondary_range_name  = "pods-range"
    services_secondary_range_name = "services-range"
  }
  
  # ... other configs
}
```