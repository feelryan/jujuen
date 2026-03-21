# 企業級網路拓撲與連接模式 / Enterprise Network Topology & Connectivity Patterns

## Mental model｜心智模型

在 Azure 中設計網路時，請放棄傳統地端機房「只要線接通就能連」的思維。在雲端，網路設計即是 **資安邊界（Security Boundary）** 與 **流量治理（Traffic Governance）** 的具體實現。

將企業級網路想像成一個 **現代化的國際機場**：

1.  **Hub (轉運中心)**：這是機場的安檢大廳與塔台。所有進出外部（Internet/On-premise）的流量，以及跨區域的流量，原則上都應該經過這裡進行檢查（Firewall）、路由（Gateway）與監控。
2.  **Spoke (登機門/區域)**：這是各個具體的 Workload（應用程式、資料庫）。它們彼此隔離，不應該直接「翻牆」互通，必須經過 Hub 的調度或明確授權的 Peering。
3.  **Private Link (專屬通道)**：這是 VIP 專屬通道。讓 PaaS 服務（如 SQL DB, Storage）不再暴露於公網大廳，而是直接將一個「私有入口」拉進你的 VNet 內部，只有持有票券（權限）且在內網的人才能存取。

**核心原則**：
*   **Centralize Control, Decentralize Resources**: 集中管理連接性與安全性，但分散部署資源。
*   **Identity over IP**: 雖然我們在談網路，但在 Azure 中，身分（Identity）往往比 IP 規則更靈活且安全（例如使用 Managed Identity 存取 Private Endpoint）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Hub-and-Spoke Topology (軸輻式拓撲)
這是 Azure 企業架構的黃金標準。
*   **Hub VNet**: 託管共享服務。
    *   **Azure Firewall / NVA**: 中央流量過濾。
    *   **VPN / ExpressRoute Gateway**: 連接 On-premise 的唯一出口。
    *   **Azure Bastion**: 安全的運維通道。
    *   **Shared DNS Resolvers**: 處理混合雲 DNS 解析。
*   **Spoke VNets**: 託管業務負載。
    *   透過 **VNet Peering** 連接至 Hub。
    *   Spoke 之間預設不互通（除非需要，且通常建議透過 Hub NVA 轉送以進行檢測）。

### 2. Private Link vs. Service Endpoints
這是最常被混淆的決策點，現代架構優先選擇 **Private Link**。

| Feature | Private Link (Private Endpoint) | Service Endpoints |
| :--- | :--- | :--- |
| **IP Address** | **Private IP** (在你的 VNet 內) | Public IP (但在 Azure 骨幹網路內路由) |
| **On-prem Access** | **Supported** (透過 VPN/ER 直接連) | Not directly supported (需透過 Proxy) |
| **Data Exfiltration** | **Low Risk** (僅對應特定資源實例) | Higher Risk (預設開放該服務的所有資源，需配合 Policy) |
| **Complexity** | High (需處理 DNS 解析) | Low (路由表自動生效) |
| **Cost** | 付費 (每小時 + 流量) | 免費 |
| **Recommendation** | **Default Choice** (特別是生產環境) | 僅用於成本敏感或特定大流量場景 (如大數據 ETL) |

### 3. Micro-segmentation with NSGs & ASGs
不要只依賴 Subnet 隔離。
*   **NSG (Network Security Group)**: 這是你的防火牆規則。
*   **ASG (Application Security Group)**: 這是你的「標籤」。
*   **Pattern**: 避免在 NSG 規則中寫死 IP (e.g., `10.0.1.5` allow to `10.0.2.4`)。
*   **Better**: 建立 ASG `asg-web` 和 `asg-db`。在 NSG 規則設定：Source `asg-web` allow to Destination `asg-db` on port 1433。這樣即使機器擴展或 IP 變動，規則依然有效。

### 4. Forced Tunneling & UDR (強制通道與使用者定義路由)
*   為了確保所有外網流量都經過 Firewall 檢查，必須在 Spoke Subnet 套用 **UDR (User Defined Route)**。
*   **Rule**: `0.0.0.0/0` -> Next Hop: `Virtual Appliance` (Hub Firewall IP)。
*   **注意**: 某些 PaaS 服務（如 Databricks, App Service Environment）對 UDR 有特殊要求，需查閱文檔。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Mesh Topology (網狀拓撲)
*   **Bad**: 為了方便，將所有 Spoke VNet 彼此兩兩 Peering。
*   **Consequence**: 路由表失控，資安邊界消失，且達到 Peering 數量上限。一旦發生橫向移動攻擊（Lateral Movement），無法在中央點截斷。

### 2. Overlapping CIDR Blocks (網段重疊)
*   **Bad**: 在規劃 VNet 時隨意使用 `10.0.0.0/16`，未考慮 On-premise 或其他 VNet 的網段。
*   **Consequence**: 這是最難修復的技術債。一旦網段重疊，Peering 將無法建立，必須重建整個網路或使用複雜的 NAT 解決方案。

### 3. Management via Public IP (透過公網 IP 管理)
*   **Bad**: 為了 RDP/SSH 方便，給 VM 掛載 Public IP 並在 NSG 開放 3389/22。
*   **Consequence**: 這是勒索軟體的最愛。
*   **Fix**: 使用 **Azure Bastion** 或透過 VPN 內網連線。

### 4. Misunderstanding Private Link DNS (DNS 解析地獄)
*   **Pitfall**: 建立了 Private Endpoint，但在 NSlookup 時仍解析到 Public IP。
*   **Reason**: Azure 內的服務預設解析公網 DNS。
*   **Fix**: 必須設定 **Private DNS Zone** 並連結到 VNet，或者在自建 DNS Server 上設定 Forwarder。這是實作 Private Link 最常卡關的地方。

---

## Checklists & workflows｜檢查清單與流程

### Network Planning Checklist (網路規劃檢核)
- [ ] **CIDR Allocation**: 確保 VNet 網段不與 On-premise 及其他環境（Dev/Test/Prod）重疊。
- [ ] **Subnet Sizing**: 預留足夠的 IP。注意 Azure 每個 Subnet 會保留 5 個 IP。
    - *GatewaySubnet*: 至少 `/27`。
    - *AzureFirewallSubnet*: 至少 `/26`。
    - *PrivateLinkSubnet*: 專門放 Private Endpoints 的子網（建議做法）。
- [ ] **Hub Design**: 決定是否使用 Azure Virtual WAN (適合大規模、多區域) 還是傳統 Hub VNet。

### Security & Connectivity Workflow (連接性實作流程)
1.  **建立 VNet & Peering**: 
    - [ ] 建立 Hub 與 Spoke。
    - [ ] 設定 Peering (注意勾選 `Use Remote Gateway` / `Allow Gateway Transit`)。
2.  **設定 NSG/ASG**:
    - [ ] 拒絕所有預設入站流量，僅開放白名單。
    - [ ] 使用 ASG 定義業務邏輯分組。
3.  **部署 Private Link (若適用)**:
    - [ ] 關閉 PaaS 服務的 Public Access。
    - [ ] 建立 Private Endpoint。
    - [ ] **關鍵步驟**: 設定 Private DNS Zone (e.g., `privatelink.database.windows.net`) 並 Link 到 Hub & Spoke VNet。
4.  **路由控制 (UDR)**:
    - [ ] 建立 Route Table。
    - [ ] 設定 `0.0.0.0/0` 指向 Firewall (若需過濾外網)。
    - [ ] 關聯至 Spoke Subnets。
5.  **驗證**:
    - [ ] 使用 Network Watcher 的 "IP Flow Verify" 測試 NSG。
    - [ ] 使用 "Next Hop" 工具驗證 UDR 路徑。

---

## Real-world examples｜實戰案例

### Scenario: Secure Web App with On-prem DB Access
**情境**：一個企業內部的 Web App (App Service)，需要存取 Azure SQL Database，並且需要連線回地端 (On-premise) 的 Legacy API。

#### Architecture Design (架構設計)

1.  **Hub VNet**:
    *   部署 **VPN Gateway** 連接 On-premise。
    *   部署 **Azure DNS Private Resolver** (或自建 DNS VM) 以解析地端 Hostname。
2.  **Spoke VNet (Web)**:
    *   **App Service VNet Integration**: 將 Web App 注入到 `snet-integration` 子網，使其能存取內網資源。
    *   **Route Table**: 設定路由，將往地端網段 (e.g., `192.168.0.0/16`) 的流量指向 Hub 的 VPN Gateway (Next Hop type: Virtual Network Gateway)。
3.  **Spoke VNet (Data) / 或同一 Spoke 的不同 Subnet**:
    *   **Azure SQL**: 關閉 "Allow Azure services and resources to access this server"。
    *   **Private Endpoint**: 建立在 `snet-private-link`，取得 IP `10.1.2.5`。
4.  **DNS Flow**:
    *   Web App 查詢 `sqlserver.database.windows.net`。
    *   Azure DNS 看到關聯的 Private DNS Zone `privatelink.database.windows.net`。
    *   回傳 A Record `10.1.2.5`。
    *   流量完全走在 Microsoft Backbone，不經過公網。

#### Pseudo-IaC (Terraform Concept)

```hcl
# 定義 Hub 與 Spoke 的 Peering
resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                      = "spoke-to-hub"
  resource_group_name       = azurerm_resource_group.spoke.name
  virtual_network_name      = azurerm_virtual_network.spoke.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
  allow_forwarded_traffic   = true
  use_remote_gateways       = true # 關鍵：讓 Spoke 能用 Hub 的 VPN
}

# 強制流量經過 Firewall 的 UDR
resource "azurerm_route_table" "spoke_udr" {
  name = "rt-spoke-default"
  # ...
  route {
    name                   = "default-route-to-firewall"
    address_prefix         = "0.0.0.0/0"
    next_hop_type          = "VirtualAppliance"
    next_hop_in_ip_address = "10.0.1.4" # Firewall Private IP
  }
}
```

### Troubleshooting Tip: "It works locally but fails in Azure"
**症狀**: 開發者本機連 SQL 沒問題 (因為開了 Public IP 白名單)，但部署到 App Service 後連不上。
**原因**: App Service 透過 VNet Integration 出去時，走的是內網 IP，但 DNS 解析可能還是在解 Public IP，或者 NSG 擋住了內網流量。
**解法**: 檢查 `nameresolver.exe` (在 Kudu console) 確認 DNS 解析結果是否為 Private IP。檢查 SQL Server 的 Firewall 設定是否允許了 VNet 的網段。