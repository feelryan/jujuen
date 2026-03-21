# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，雲端網路（Cloud Networking）不僅僅是連通性（Connectivity）的問題，更是安全性、合規性與系統韌性的基石。在 Azure 的環境中，錯誤的網路設計往往是導致日後架構無法擴展或遭遇資安事件的主因。

For senior engineers, Cloud Networking is not just about connectivity; it is the cornerstone of security, compliance, and system resilience. In the Azure environment, poor network design is often the root cause of future scalability issues or security incidents.

完成本章後，你將能夠：

By the end of this chapter, you will be able to:

1.  **設計企業級網路拓樸**：熟練運用 Hub-and-Spoke 架構來集中管理流量與安全性。
    **Design Enterprise-Grade Network Topologies**: Master the Hub-and-Spoke architecture to centralize traffic management and security.
2.  **實作零信任網路存取**：區分 Service Endpoints 與 Private Link 的差異，並正確配置 Private Endpoints 以消除公開存取風險。
    **Implement Zero Trust Network Access**: Distinguish between Service Endpoints and Private Link, and correctly configure Private Endpoints to eliminate public access risks.
3.  **精準選擇流量負載平衡方案**：在 Azure Front Door, Application Gateway, Traffic Manager 與 Load Balancer 之間，根據 L4/L7 需求與全球/區域範圍做出最佳架構決策。
    **Select the Optimal Traffic Load Balancing Solution**: Make architectural decisions between Azure Front Door, Application Gateway, Traffic Manager, and Load Balancer based on L4/L7 requirements and global/regional scope.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Hub-and-Spoke 拓樸 (Hub-and-Spoke Topology)

**心智模型**：想像一個國際機場（Hub）。所有的安檢、海關、指揮塔台（Shared Services）都集中在這裡。各個登機門或衛星航廈（Spokes）負責具體的航班（Workloads），它們之間不直接互通，而是透過機場中心進行轉運與檢查。

**Mental Model**: Imagine an international airport (Hub). All security checks, customs, and control towers (Shared Services) are centralized here. Individual gates or satellite terminals (Spokes) handle specific flights (Workloads); they do not connect directly but route through the central hub for transit and inspection.

-   **Hub VNet**: 託管 Azure Firewall, VPN Gateway, ExpressRoute Gateway 與 Bastion Host。它是進出地端（On-premise）與網際網路的單一入口。
    **Hub VNet**: Hosts Azure Firewall, VPN Gateway, ExpressRoute Gateway, and Bastion Host. It acts as the single point of entry/exit for on-premise and internet traffic.
-   **Spoke VNets**: 託管實際的應用程式與資料庫。透過 VNet Peering 連接至 Hub。
    **Spoke VNets**: Host the actual applications and databases. Connected to the Hub via VNet Peering.

## 2.2 Private Link vs. Service Endpoints

這是面試與實務中最常混淆的概念。

This is one of the most confused concepts in interviews and practice.

-   **Service Endpoints**: 就像是為你的 VNet 開了一條「專用隧道」直達 Azure PaaS 服務（如 SQL, Storage）。流量雖然走 Azure 骨幹網路，但目標資源仍具有 Public IP（儘管防火牆擋住了未授權存取）。
    **Service Endpoints**: Like opening a "dedicated tunnel" from your VNet directly to Azure PaaS services (e.g., SQL, Storage). Traffic stays on the Azure backbone, but the target resource still possesses a Public IP (even if firewalls block unauthorized access).
-   **Private Link (Private Endpoint)**: 將 PaaS 服務「拉進」你的 VNet 內，賦予它一個 **Private IP**。這是一個網路介面（NIC）。這是目前最推薦的安全性做法，因為它能防止資料外洩（Data Exfiltration）並完全關閉 Public Access。
    **Private Link (Private Endpoint)**: "Pulls" the PaaS service into your VNet by assigning it a **Private IP**. It is a Network Interface (NIC). This is the recommended security practice as it prevents data exfiltration and allows completely disabling public access.

## 2.3 負載平衡決策樹 (Load Balancing Decision Tree)

Azure 提供了多種負載平衡器，選擇時需考慮兩個維度：**層級 (Layer)** 與 **範圍 (Scope)**。

Azure provides multiple load balancers. Selection depends on two dimensions: **Layer** and **Scope**.

| Service | OSI Layer | Scope | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Azure Front Door** | Layer 7 (HTTP/S) | Global | 全球應用加速、WAF、跨區域災難復原 (Global acceleration, WAF, Cross-region DR) |
| **Traffic Manager** | DNS Based | Global | 非 HTTP 協定的全球路由 (Non-HTTP global routing) |
| **Application Gateway** | Layer 7 (HTTP/S) | Regional | 區域性 Web 流量、WAF、SSL 卸載、AKS Ingress (Regional Web traffic, WAF, SSL offloading, AKS Ingress) |
| **Azure Load Balancer** | Layer 4 (TCP/UDP) | Regional | 高效能低延遲 TCP/UDP 分流、NVA 高可用性 (High-performance low-latency TCP/UDP, NVA HA) |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在設計一個高可用性且符合 PCI-DSS 或 HIPAA 標準的系統時，網路架構通常如下：

When designing a high-availability system compliant with PCI-DSS or HIPAA, the network architecture typically looks like this:

## 3.1 全球入口與邊緣安全 (Global Entry & Edge Security)
系統最前端使用 **Azure Front Door**。它不僅將使用者導向最近的區域（Region），還負責在邊緣（Edge）阻擋 DDoS 攻擊與 SQL Injection（透過 WAF Policies）。這減輕了後端伺服器的負載。

The system front-end uses **Azure Front Door**. It not only routes users to the nearest Region but also blocks DDoS attacks and SQL Injection at the Edge (via WAF Policies). This offloads the burden from backend servers.

## 3.2 區域性流量管理 (Regional Traffic Management)
流量進入特定 Region 的 VNet 後，由 **Application Gateway** 接手。
*   **Design Choice**: 如果使用 AKS (Kubernetes)，通常會配置 AGIC (Application Gateway Ingress Controller)，讓 App Gateway 直接作為 K8s 的 Ingress，減少一層跳躍。
*   **Design Choice**: 啟用 End-to-End SSL 加密（從 Front Door 到 App Gateway 再到 Pod），滿足零信任原則。

Once traffic enters a specific Region's VNet, **Application Gateway** takes over.
*   **Design Choice**: If using AKS (Kubernetes), AGIC (Application Gateway Ingress Controller) is often configured, allowing App Gateway to serve directly as the K8s Ingress, eliminating an extra hop.
*   **Design Choice**: Enable End-to-End SSL encryption (from Front Door to App Gateway to Pod) to meet Zero Trust principles.

## 3.3 資料庫與內部通訊 (Database & Internal Communication)
後端服務（Backend API）存取 Azure SQL 或 Cosmos DB 時，**絕對不通過 Public Internet**。
*   **Implementation**: 使用 **Private Link**。
*   **Impact**: 資料庫防火牆僅允許來自該 VNet subnet 的 Private IP 連線。即便資料庫憑證洩漏，攻擊者若無法進入 VNet 內部網路，也無法存取資料。

Backend services (Backend APIs) accessing Azure SQL or Cosmos DB **never traverse the Public Internet**.
*   **Implementation**: Use **Private Link**.
*   **Impact**: The database firewall only allows connections from the Private IP within the VNet subnet. Even if credentials are leaked, attackers cannot access the data without breaching the internal VNet network.

---

# 4. 逐步示例：Private Link DNS 解析難題 (Walkthrough: The Private Link DNS Conundrum)

### 背景 (Context)
你正在將一個單體應用遷移至 Azure App Service，並連接 Azure SQL Database。為了安全，你啟用了 Private Endpoint 並關閉了 SQL 的 Public Network Access。

You are migrating a monolithic application to Azure App Service, connecting to an Azure SQL Database. For security, you enabled Private Endpoint and disabled the SQL Public Network Access.

### 問題 (Problem)
應用程式報錯：`Connection Refused` 或 `Timeout`。但在 VNet 內的 VM 使用 `nslookup` 查詢 SQL Server 的 FQDN (`mydb.database.windows.net`)，卻仍然解析到 Public IP。

The application throws errors: `Connection Refused` or `Timeout`. However, when using `nslookup` on the SQL Server FQDN (`mydb.database.windows.net`) from a VM inside the VNet, it still resolves to a Public IP.

### 思考步驟與解決方案 (Steps & Solution)

1.  **理解 DNS 解析鏈 (Understand the DNS Chain)**:
    Azure 的 Public DNS 依然將 `mydb.database.windows.net` 指向 Public IP。你需要覆寫這個行為，但僅限於你的 VNet 內部。

    Azure's Public DNS still points `mydb.database.windows.net` to a Public IP. You need to override this behavior, but only within your VNet.

2.  **Private DNS Zone 的角色 (The Role of Private DNS Zone)**:
    當你建立 Private Endpoint 時，Azure 會建立一個 CNAME 紀錄，將 `mydb.database.windows.net` 指向 `mydb.privatelink.database.windows.net`。
    你需要在 Azure 中建立一個 **Private DNS Zone**，名稱必須精確為 `privatelink.database.windows.net`。

    When you create a Private Endpoint, Azure creates a CNAME record pointing `mydb.database.windows.net` to `mydb.privatelink.database.windows.net`.
    You need to create a **Private DNS Zone** in Azure, named exactly `privatelink.database.windows.net`.

3.  **連結 VNet (Link the VNet)**:
    建立 Zone 之後，必須透過 **Virtual Network Link** 將此 DNS Zone 連結到你的應用程式所在的 VNet。

    After creating the Zone, you must link this DNS Zone to the VNet where your application resides via a **Virtual Network Link**.

4.  **驗證 (Verification)**:
    再次於 VNet 內執行 `nslookup mydb.database.windows.net`。
    *   **Before**: Resolves to `104.x.x.x` (Public)
    *   **After**: Resolves to `10.0.1.5` (Private IP)

### 程式碼/配置示例 (Configuration Example)

這是一個常見的 Terraform 設定片段，用於處理上述邏輯：

Here is a common Terraform snippet handling the logic above:

```hcl
# 1. The Private Endpoint
resource "azurerm_private_endpoint" "sql_pe" {
  name                = "pe-sql-db"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.endpoint_subnet.id

  private_service_connection {
    name                           = "psc-sql"
    private_connection_resource_id = azurerm_mssql_server.sql.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }

  # Critical: Connect to Private DNS Zone Group
  private_dns_zone_group {
    name                 = "pdzg-sql"
    private_dns_zone_ids = [azurerm_private_dns_zone.sql_dns.id]
  }
}

# 2. The Private DNS Zone
resource "azurerm_private_dns_zone" "sql_dns" {
  name                = "privatelink.database.windows.net"
  resource_group_name = azurerm_resource_group.rg.name
}

# 3. Linking DNS Zone to VNet
resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link" {
  name                  = "vnet-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.sql_dns.name
  virtual_network_id    = azurerm_virtual_network.main_vnet.id
}
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略 SNAT Port Exhaustion (Ignoring SNAT Port Exhaustion)
-   **錯誤 (Mistake)**: 在高流量場景下，後端 VM 直接透過 Azure Load Balancer 或預設出站存取（Default Outbound Access）連接外部 API。
-   **後果 (Consequence)**: 當併發連線數過高，SNAT ports 耗盡，導致外部連線失敗。
-   **修正 (Fix)**: 使用 **NAT Gateway** 綁定 Subnet。NAT Gateway 提供更大量的 SNAT ports 且管理更簡單，優於 Load Balancer 的 Outbound Rules。

-   **Mistake**: In high-traffic scenarios, backend VMs connect to external APIs directly via Azure Load Balancer or Default Outbound Access.
-   **Consequence**: When concurrent connections spike, SNAT ports are exhausted, causing external connection failures.
-   **Fix**: Use **NAT Gateway** attached to the Subnet. NAT Gateway provides a larger pool of SNAT ports and simpler management compared to Load Balancer Outbound Rules.

## 5.2 誤用 Peering 處理重疊 IP (Misusing Peering with Overlapping IPs)
-   **錯誤 (Mistake)**: 企業併購或混合雲場景中，試圖 Peer 兩個 IP 範圍重疊（Overlapping Address Space）的 VNet。
-   **後果 (Consequence)**: Peering 建立失敗或路由錯亂。
-   **修正 (Fix)**: 在中間引入一個 NAT VNet 或使用 Azure Private Link Service 來隱藏真實 IP，進行位址轉換。

-   **Mistake**: Attempting to Peer two VNets with Overlapping Address Spaces during M&A or hybrid cloud scenarios.
-   **Consequence**: Peering failure or routing chaos.
-   **Fix**: Introduce an intermediate NAT VNet or use Azure Private Link Service to mask real IPs and perform address translation.

## 5.3 僅依賴 NSG 而忽略 Application Gateway WAF (Relying Solely on NSG, Ignoring WAF)
-   **錯誤 (Mistake)**: 認為 Network Security Group (NSG) 限制了 Port 443 就足夠安全。
-   **後果 (Consequence)**: NSG 是 L4 防火牆，無法阻擋 SQL Injection、XSS 或惡意 Bot 流量。
-   **修正 (Fix)**: 對於公開 Web 服務，必須配置 Application Gateway (WAF_v2 Tier) 或 Front Door，並開啟 Prevention Mode。

-   **Mistake**: Believing that restricting Port 443 via Network Security Group (NSG) is sufficient.
-   **Consequence**: NSG is an L4 firewall and cannot block SQL Injection, XSS, or malicious bot traffic.
-   **Fix**: For public Web services, you must configure Application Gateway (WAF_v2 Tier) or Front Door and enable Prevention Mode.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請比較 Azure Front Door 與 Azure Application Gateway，你會如何選擇？
**How do you compare Azure Front Door and Azure Application Gateway? How would you choose?**

*   **高分回答要點 (Key Points)**:
    *   **Scope**: Front Door 是 Global (跨 Region)，App Gateway 是 Regional。
    *   **Protocol**: 兩者都是 L7 (HTTP/S)。若需非 HTTP 的 Global Routing，需改用 Traffic Manager。
    *   **Source IP**: Front Door 透過 Anycast 接入，App Gateway 位於特定 VNet。
    *   **Use Case**: 若需跨區 DR 或加速全球用戶訪問 -> Front Door。若需控制 VNet 內部的微服務路由或 AKS Ingress -> App Gateway。
    *   **Combination**: 常見架構是 Front Door (Global entry) -> App Gateway (Regional ingress)。

## Q2: 在 Hub-and-Spoke 架構中，Spoke A 的 VM 如何與 Spoke B 的 VM 通訊？
**In a Hub-and-Spoke architecture, how does a VM in Spoke A communicate with a VM in Spoke B?**

*   **高分回答要點 (Key Points)**:
    *   預設情況下，Spoke 之間是不通的（Non-transitive peering）。
    *   **方法一 (NVA/Firewall)**: 在 Hub VNet 部署 Azure Firewall 或 NVA，並在 Spokes 設定 Route Table (UDR) 將流量導向 Hub。
    *   **方法二 (Direct Peering)**: 直接建立 Spoke A 到 Spoke B 的 Peering（會變成 Mesh 拓樸，管理複雜度增加，通常不推薦除非有極高頻寬需求）。
    *   **面試官加分題**: 提到 "Gateway Transit" 選項在 VPN Gateway 場景下的應用。

## Q3: 為什麼有了 Private Link 還需要 Azure Firewall？
**Why do we still need Azure Firewall if we have Private Link?**

*   **高分回答要點 (Key Points)**:
    *   **Private Link** 負責的是「入站 (Inbound)」到 PaaS 服務的安全（私有化存取）。
    *   **Azure Firewall** 負責的是「出站 (Outbound)」流量過濾（防止資料外洩到惡意網站）以及 VNet 之間的流量檢查（East-West traffic inspection）。
    *   兩者是互補的：Private Link 保護資料庫端點，Firewall 保護運算資源與整體網路邊界。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Hub-and-Spoke** 是 Azure 網路架構的黃金標準，利於集中管理與安全性。
2.  **Private Link** 優於 Service Endpoints，因為它將 PaaS 服務帶入你的私有 IP 空間。
3.  **DNS 解析** 是 Private Link 實作中最容易失敗的環節，務必熟悉 Private DNS Zones 的配置。
4.  **L7 vs L4**: Web 流量用 App Gateway/Front Door；非 HTTP 或單純 TCP/UDP 吞吐量需求用 Azure Load Balancer。
5.  **SNAT**: 出站流量大時，優先考慮 NAT Gateway 而非 Load Balancer。

### 後續延伸 (Next Steps)
*   **Infrastructure as Code (IaC)**: 嘗試使用 Terraform 或 Bicep 模組化部署上述的 Hub-and-Spoke 網路與 Private DNS Zone。
*   **Hybrid Connectivity**: 深入研究 **ExpressRoute** 與 **VPN Gateway** 的共存 (Co-existence) 配置，這在大型企業混合雲中非常常見。
*   **Next Chapter**: 進入 **Chapter 04: 身分驗證與授權 (Identity and Access Management)**，學習如何將網路安全與 Azure AD (Entra ID) 結合。