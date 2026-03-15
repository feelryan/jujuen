# 進階網路架構與流量管理 / Advanced Networking & Traffic Management

## Mental model｜心智模型

在 AWS 環境中，網路不再是單純的「插線與交換器」，而是**軟體定義的邊界與路由策略 (Software-Defined Boundaries & Routing Policies)**。要掌握進階網路，你需要建立以下三個層次的心智模型：

1.  **The Island Model (孤島模型 - Isolation)**：
    預設情況下，每個 VPC 都是一座孤島。你的首要任務不是「連接」，而是定義「邊界」。思考網路設計時，先問「誰**不應該**進來」，而非「誰可以進來」。
    *   *Key Concept*: VPCs are isolation boundaries. Subnets are routing boundaries. Security Groups are instance firewalls.

2.  **The Hub & Spoke (樞紐與輻射 - Connectivity)**：
    隨著帳號與 VPC 數量增加，點對點的 Peering 會變成維護地獄（Full mesh problem）。現代架構傾向於使用 Transit Gateway (TGW) 作為中央樞紐，統一管理跨 VPC 與 On-premise 的流量。
    *   *Key Concept*: Centralize complexity (TGW), distribute resources (VPC Spoke).

3.  **Traffic as a Managed Service (流量即服務 - Application Networking)**：
    不要把 Load Balancer 僅視為分流器。ALB/NLB 是應用程式的前門，負責處理 SSL Offloading、身份驗證 (OIDC)、以及與 WAF 的整合。
    *   *Key Concept*: Offload "undifferentiated heavy lifting" (crypto, routing rules) to the load balancer.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Hub-and-Spoke Topology with Transit Gateway
**適用場景**：多帳號架構、混合雲連線、需要中央流量檢測 (Inspection)。

*   **實作重點**：
    *   使用 **AWS Transit Gateway (TGW)** 連接多個 VPC 與 VPN/Direct Connect。
    *   **Route Table Segmentation**：在 TGW 內建立不同的 Route Table（例如：Prod, Dev, Shared-Services）。Dev VPC 可以連到 Shared-Services，但不能連到 Prod。
    *   **Centralized Egress**：建立一個專門的 "Egress VPC"，所有對外 Internet 流量都經過這裡的 NAT Gateway 或 Firewall Appliance，便於統一監控與節省 NAT 費用。

### 2. PrivateLink for Internal Service Exposure
**適用場景**：SaaS 服務提供商、或大型企業內部跨部門服務呼叫（避免 CIDR 重疊）。

*   **實作重點**：
    *   使用 **VPC Endpoint Services (PrivateLink)** 將你的服務暴露給其他 VPC。
    *   **優勢**：Consumer VPC 與 Provider VPC 的 IP CIDR 可以重疊（Overlapping CIDR），因為流量是透過 AWS 骨幹網路 NAT 轉換的。
    *   **安全性**：流量完全不經過 Public Internet，且 Consumer 需要被 Whitelist 才能連線。

### 3. The "Swiss Cheese" Security Model (Micro-segmentation)
**適用場景**：任何生產環境，特別是微服務架構。

*   **實作重點**：
    *   **Security Group Chaining**：不要在 Security Group (SG) 規則中寫死 IP。例如，DB SG 的 Inbound 規則應該是 `Source: App-SG-ID`，而不是 `10.0.1.0/24`。這允許資源動態擴展而無需更新防火牆規則。
    *   **NACL as a Safety Net**：NACL 是 Stateless 的，主要用於「明確拒絕」特定惡意 IP 或作為子網級別的粗粒度控制，日常維運主要依賴 SG。

### 4. Load Balancing Strategy: ALB vs. NLB
**決策依據**：

*   **Application Load Balancer (ALB)**:
    *   Layer 7 (HTTP/HTTPS, gRPC)。
    *   功能：Path-based routing (`/api` vs `/web`), Host-based routing, WAF 整合, OIDC 登入整合。
    *   *Best Practice*: 用於大多數 Web 應用與微服務 API Gateway。
*   **Network Load Balancer (NLB)**:
    *   Layer 4 (TCP/UDP/TLS)。
    *   功能：極低延遲、每秒數百萬請求、**Static IP (Elastic IP)** 支援。
    *   *Best Practice*: 用於資料庫前端、需要固定 IP 的服務、或非 HTTP 協定。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Flat Network" Trap (扁平網路陷阱)
*   **Bad Practice**: 將所有資源（Web, App, DB）都放在同一個 Public Subnet，只靠 Security Group 防護。
*   **Consequence**: 一旦開發者誤開 SG 規則（如 `0.0.0.0/0`），資料庫直接暴露在公網。
*   **Correction**: 嚴格遵守 **Public / Private / Isolated** 三層子網架構。資料庫永遠在 Isolated Subnet（無 Internet Route）。

### 2. NAT Gateway Cost Shock (NAT 閘道費用震撼)
*   **Bad Practice**: 在 Private Subnet 的 EC2 大量存取 S3 或 DynamoDB，流量全部經過 NAT Gateway。
*   **Consequence**: NAT Gateway 既收「小時費」也收「流量處理費」，大流量下帳單驚人。
*   **Correction**: 務必配置 **VPC Gateway Endpoints** (S3 & DynamoDB)。這是免費的，且流量走 AWS 內網，速度更快更安全。

### 3. CIDR Planning Failure (IP 規劃失敗)
*   **Bad Practice**: 每個 VPC 都使用預設的 `172.31.0.0/16` 或隨意設定 `10.0.0.0/16`。
*   **Consequence**: 當未來需要 VPC Peering 或連接公司 VPN 時，發生 IP 衝突 (Overlapping CIDRs)，導致無法路由，必須重建整個網路。
*   **Correction**: 企業級環境應由中央 IT 統一分配 CIDR Block。預留足夠空間，且避免使用常見家用網段（如 `192.168.0.0/24`）。

### 4. Ignoring Cross-AZ Data Transfer Costs
*   **Bad Practice**: 應用程式頻繁呼叫另一個 AZ 的服務（例如 App 在 AZ-a，DB Master 在 AZ-b）。
*   **Consequence**: AWS 收取跨 AZ 流量費。
*   **Correction**: 啟用 **Availability Zone Affinity**，盡量讓流量在同一個 AZ 內處理。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Connectivity Debugging (連線除錯流程)
當 Service A 無法連線到 Service B 時，請依序檢查：

1.  **DNS Resolution**:
    *   [ ] 在 Service A 上執行 `dig` 或 `nslookup`，確認 Service B 的 Domain 是否解析出正確的 Private IP。
2.  **Security Groups (Stateful)**:
    *   [ ] 檢查 **Service B** 的 Inbound SG：是否允許來自 Service A (IP 或 SG ID) 的 Port？
    *   [ ] 檢查 **Service A** 的 Outbound SG：通常預設全開，但若有鎖定，是否允許出去？
3.  **NACLs (Stateless)**:
    *   [ ] 檢查 A 與 B 所在 Subnet 的 NACL。
    *   [ ] **關鍵陷阱**：NACL 是 Stateless 的，必須同時檢查 Inbound 和 Outbound。回程流量 (Ephemeral Ports 1024-65535) 是否被允許？
4.  **Route Tables**:
    *   [ ] 檢查 Subnet Route Table。是否有路由指向目標（Local, Peering connection, TGW, or NAT）？
5.  **Reachability Analyzer**:
    *   [ ] 如果以上都看不出問題，使用 AWS Console 的 **VPC Reachability Analyzer**。建立一個從 Source 到 Destination 的分析路徑，它會告訴你被哪個元件擋住。

### Checklist: Production Network Readiness
上線前請確認：

*   [ ] **CIDR**: VPC CIDR 不與 On-premise 或其他 VPC 衝突。
*   [ ] **Subnets**: 至少跨越 2 個 AZ (High Availability)。
*   [ ] **Routing**: Private Subnets 的路由表正確指向 NAT Gateway (若需外網) 或 TGW。
*   [ ] **Endpoints**: S3 與 DynamoDB Gateway Endpoints 已配置。
*   [ ] **Flow Logs**: VPC Flow Logs 已啟用並發送到 S3 或 CloudWatch Logs（用於除錯與資安審計）。
*   [ ] **Security**: 沒有任何 Security Group 開放 `0.0.0.0/0` 到 SSH (22) 或 RDP (3389)。應使用 SSM Session Manager。

---

## Real-world examples｜實戰案例

### Example 1: Secure Microservices with PrivateLink
**情境**：你負責維護一個核心「使用者認證服務 (Auth Service)」，公司內其他 10 個產品團隊（位於不同的 AWS 帳號）都需要呼叫你的 API。

**解決方案**：
1.  在你的 Auth VPC 前端建立一個 **NLB** (Network Load Balancer)。
2.  建立 **VPC Endpoint Service** 並指向該 NLB。
3.  將 Service Name 提供給其他團隊。
4.  其他團隊在各自的 VPC 建立 **Interface Endpoint**。
5.  **結果**：其他團隊像呼叫本地 IP 一樣呼叫你的服務，流量不走公網，且你不需擔心他們使用什麼 IP 網段（解決 CIDR 衝突問題）。

### Example 2: Cost-Optimized Egress Architecture
**情境**：系統包含 50 個 EC2 instances，每天需下載大量外部資料，NAT Gateway 費用過高。

**解決方案**：
1.  分析流量發現 80% 是從 S3 下載資料，20% 是去第三方 API。
2.  **Action A**: 設定 S3 Gateway Endpoint。這部分流量立即變為免費且更快速。
3.  **Action B**: 針對剩餘的 20% 流量，若非高可用關鍵路徑，考慮架設一台小型 NAT Instance (EC2) 取代 Managed NAT Gateway（僅適用於開發環境或非關鍵負載，生產環境仍建議 Managed NAT GW 以確保 HA）。

### Example 3: Debugging the "Black Hole"
**情境**：應用程式偶爾連線 Timeout，但重試又會成功。

**排查過程**：
1.  檢查 CloudWatch Metrics，發現 ALB 拋出 504 Gateway Timeout。
2.  檢查 Backend Target Group，發現某個 AZ 的 Instance 顯示 Unhealthy。
3.  深入檢查該 AZ 的 Subnet NACL，發現有人為了阻擋某個攻擊 IP，誤設了 Deny Rule，卻忘記 NACL 規則是按順序執行的 (Rule Number ordering)，導致回程流量被截斷。
4.  **Lesson**: 網路問題往往是「設定變更」造成的。啟用 AWS Config 記錄配置變更歷史至關重要。