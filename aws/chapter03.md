# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，AWS 網路不僅僅是建立 VPC 和 Security Group。在大型分散式系統或企業級架構中，網路設計直接決定了系統的隔離性（Isolation）、擴充性（Scalability）與跨區域容災能力（Multi-Region DR）。本章將從單一 VPC 跨越到多帳號、多區域的複雜網路拓撲。

For senior engineers, AWS networking is far more than just creating VPCs and Security Groups. In large-scale distributed systems or enterprise architectures, network design dictates system isolation, scalability, and multi-region disaster recovery (DR) capabilities. This chapter moves beyond single VPCs to complex multi-account, multi-region network topologies.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **設計企業級網路拓撲**：理解何時使用 VPC Peering，何時必須轉向 Transit Gateway (TGW) 實作 Hub-and-Spoke 架構。
    **Design Enterprise Network Topologies:** Understand when to use VPC Peering and when to switch to Transit Gateway (TGW) for a Hub-and-Spoke architecture.
2.  **精準選擇流量入口**：根據 OSI 模型（L4 vs L7）、靜態 IP 需求與效能要求，在 ALB、NLB 與 Global Accelerator 之間做出正確的架構決策。
    **Select Traffic Entry Points Precisely:** Make correct architectural decisions between ALB, NLB, and Global Accelerator based on the OSI model (L4 vs L7), static IP requirements, and performance needs.
3.  **規劃混合雲連線**：清楚 Direct Connect (DX) 與 Site-to-Site VPN 的互補關係，以及如何透過 BGP 路由協定管理流量。
    **Plan Hybrid Connectivity:** Clearly understand the complementary relationship between Direct Connect (DX) and Site-to-Site VPN, and how to manage traffic via BGP routing protocols.
4.  **優化網路成本與效能**：識別 NAT Gateway 與跨 AZ 傳輸的成本陷阱，並設計高效的 Data Path。
    **Optimize Network Cost & Performance:** Identify cost pitfalls related to NAT Gateways and cross-AZ transfer, and design efficient data paths.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 VPC 連線演進：Mesh vs. Hub (VPC Connectivity Evolution)

**心智模型**：
將 VPC 想像成獨立的「辦公大樓」。
*   **VPC Peering** 是兩棟大樓之間拉一條專屬光纖。速度快、成本低，但如果你有 100 棟大樓要互連，你會需要拉 $N(N-1)/2$ 條線，維護會變成惡夢（Mesh Topology）。
*   **Transit Gateway (TGW)** 是一個中央轉運站（Hub）。所有大樓都只拉一條線到轉運站，由轉運站決定去哪裡。雖然多了一跳（Hop），但管理複雜度從 $O(N^2)$ 降為 $O(N)$。

**Mental Model:**
Imagine VPCs as independent "office buildings."
*   **VPC Peering** is like laying a dedicated fiber cable between two buildings. It's fast and cheap, but if you have 100 buildings to interconnect, you need $N(N-1)/2$ cables, turning maintenance into a nightmare (Mesh Topology).
*   **Transit Gateway (TGW)** is a central transit hub. All buildings connect only to the hub, which decides where traffic goes. Although it adds a hop, management complexity drops from $O(N^2)$ to $O(N)$.

**關鍵差異 (Key Differences):**
*   **Transitivity (遞移性)**: Peering 不具遞移性（A連B，B連C，A不能透過B連C）。TGW 本生就是為了路由遞移而設計。
*   **Scale**: Peering 適合少量、高頻寬連線；TGW 適合大規模、多帳號架構。

## 2.2 負載平衡與加速器矩陣 (Load Balancing & Accelerator Matrix)

資深工程師不應只會用 ALB。請依照以下維度建立決策矩陣：

Senior engineers shouldn't just default to ALB. Build a decision matrix based on the following dimensions:

| Feature | Application Load Balancer (ALB) | Network Load Balancer (NLB) | AWS Global Accelerator (GA) |
| :--- | :--- | :--- | :--- |
| **OSI Layer** | Layer 7 (HTTP/HTTPS, gRPC) | Layer 4 (TCP/UDP/TLS) | Layer 4 (TCP/UDP) |
| **IP Address** | Dynamic IPs (DNS name only) | **Static Elastic IP** per AZ | **Static Anycast IP** (Global) |
| **Latency** | Medium (Request processing overhead) | Ultra-low (Millions of RPS) | Low (Uses AWS global backbone) |
| **Use Case** | Microservices, Path-based routing, WAF integration | Gaming, Finance, PrivateLink, Non-HTTP protocols | Global user base, Gaming, VoIP, Multi-Region Failover |

**注意**：Global Accelerator 不是 Load Balancer，它是一個網路層的服務，將使用者的流量從最接近的 Edge Location 導入 AWS 骨幹網路（Backbone），避開公共網際網路的擁塞，最終導向 ALB 或 NLB。

**Note:** Global Accelerator is not a Load Balancer; it is a networking service that ingests user traffic at the nearest Edge Location onto the AWS Backbone, bypassing public internet congestion, and ultimately directing it to an ALB or NLB.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 混合雲與多帳號架構 (Hybrid Cloud & Multi-Account Architecture)

在 Production 環境中，通常採用 **Landing Zone** 模式。你會看到一個專門的 `Network Account`，裡面部署 Transit Gateway。

In production environments, a **Landing Zone** pattern is typically used. You will see a dedicated `Network Account` where the Transit Gateway is deployed.

*   **Shared Services VPC**: 放置 CI/CD 工具、AD 伺服器或安全掃描工具。
*   **Egress VPC**: 集中管理對外流量（透過 NAT Gateway 或 Firewall Appliance），便於資安監控與成本控制。
*   **Direct Connect (DX)**: 連接 On-premise 資料中心。DX Gateway 會掛載到 TGW 上，讓地端網路能存取所有連接到 TGW 的 VPC。

*   **Shared Services VPC**: Hosts CI/CD tools, AD servers, or security scanning tools.
*   **Egress VPC**: Centralizes outbound traffic (via NAT Gateway or Firewall Appliance) for easier security monitoring and cost control.
*   **Direct Connect (DX)**: Connects to on-premise data centers. A DX Gateway attaches to the TGW, allowing on-prem network access to all VPCs connected to the TGW.

## 3.2 跨區域容災與流量管理 (Multi-Region DR & Traffic Management)

當系統需要 Active-Active 多區域部署時，DNS (Route 53) 是第一道防線，但 **Global Accelerator (GA)** 提供了更快的收斂速度（Failover）。

When a system requires an Active-Active multi-region deployment, DNS (Route 53) is the first line of defense, but **Global Accelerator (GA)** offers faster convergence (Failover).

*   **Scenario**: 一個全球金融交易平台。
*   **Design**: 使用 GA 提供兩個靜態 Anycast IP 給客戶端。GA 後端設定為 `us-east-1` 的 NLB 和 `eu-central-1` 的 NLB。
*   **Benefit**: 如果 `us-east-1` 發生區域性故障，GA 會在幾秒內自動將流量導向 `eu-central-1`，且客戶端無需更改 IP 或等待 DNS TTL 過期。

*   **Scenario**: A global financial trading platform.
*   **Design**: Use GA to provide two static Anycast IPs to clients. The GA backends are configured as the NLB in `us-east-1` and the NLB in `eu-central-1`.
*   **Benefit**: If `us-east-1` suffers a regional outage, GA automatically reroutes traffic to `eu-central-1` within seconds, without clients needing to change IPs or wait for DNS TTL expiration.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：構建高可用性、低延遲的全球 API 入口 (Building a HA, Low-Latency Global API Entry)

### 背景 (Context)
你需要為一個即時競價系統（Real-time Bidding, RTB）設計網路入口。
需求：
1.  全球客戶端連線。
2.  極低延遲（Latency sensitive）。
3.  需要固定的 IP 白名單（客戶端防火牆要求）。
4.  後端服務部署在 EKS 上。

### 思考步驟 (Thinking Process)

**Step 1: Naive Approach - Route 53 + ALB**
*   使用 Route 53 Latency Routing 指向不同 Region 的 ALB。
*   **問題 (Issue)**: ALB IP 會變動，無法滿足「固定 IP 白名單」需求。DNS Failover 依賴 TTL，切換速度可能長達數分鐘。

**Step 2: Better Approach - NLB + EKS**
*   在每個 Region 使用 NLB，因為 NLB 支援每個 AZ 一個靜態 IP。
*   **問題 (Issue)**: 雖然解決了 IP 問題，但跨國流量走公共網際網路（Public Internet），延遲不穩定（Jitter）。

**Step 3: Mature Solution - Global Accelerator + NLB + EKS**
*   **Global Accelerator**: 提供 2 個全球靜態 Anycast IP。
*   **Backbone**: 流量從 Edge Location 進入 AWS 骨幹網路，直達目標 Region。
*   **NLB**: 作為 GA 的 Endpoint，處理 TCP 連線並轉發給 EKS Nodes。
*   **Ingress Controller**: 使用 AWS Load Balancer Controller，將 NLB 目標指向 Pods (IP mode) 以減少 hop。

### 架構配置示意 (Architecture Configuration View)

雖然這裡不寫完整的 Terraform，但關鍵的邏輯配置如下：

```hcl
# 1. Global Accelerator
resource "aws_globalaccelerator_accelerator" "rtb_ga" {
  name            = "rtb-global-entry"
  ip_address_type = "IPV4"
  enabled         = true
}

# 2. Listener (TCP for Performance)
resource "aws_globalaccelerator_listener" "rtb_listener" {
  accelerator_arn = aws_globalaccelerator_accelerator.rtb_ga.id
  protocol        = "TCP"
  port_range {
    from_port = 80
    to_port   = 80
  }
}

# 3. Endpoint Group (Region: us-east-1)
resource "aws_globalaccelerator_endpoint_group" "us_east_1" {
  listener_arn = aws_globalaccelerator_listener.rtb_listener.id
  endpoint_group_region = "us-east-1"

  # Traffic Dial: Can be used for Blue/Green or Canary
  traffic_dial_percentage = 100 

  endpoint_configuration {
    endpoint_id = aws_lb.nlb_us_east_1.arn
    weight      = 128
  }
}

# 4. Endpoint Group (Region: eu-central-1)
# ... similar config for failover region ...
```

**為何這個做法可行？**
*   **Anycast IP**: 解決了客戶端防火牆白名單問題。
*   **AWS Backbone**: 解決了跨國網路延遲不穩定的問題。
*   **NLB**: 提供了極高的 Throughput 處理能力。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 CIDR 重疊 (Overlapping CIDRs)
**錯誤描述**: 在規劃 VPC 時，隨意使用 `10.0.0.0/16` 作為預設值。當公司併購或需要與合作夥伴建立 VPN/Peering 時，發現 IP 衝突。
**後果**: 路由無法建立，必須使用複雜的 NAT (Private NAT Gateway) 甚至重建 VPC。
**最佳實踐**: 使用 IPAM (IP Address Manager) 統一規劃。預留足夠的空間，並避免使用常見的預設網段。

**Description**: Using `10.0.0.0/16` as a default for all VPCs. When a merger happens or VPN/Peering is needed, IP conflicts arise.
**Consequence**: Routing fails, requiring complex NAT workarounds or VPC reconstruction.
**Best Practice**: Use IPAM to plan centrally. Avoid common default ranges.

## 5.2 誤用 ALB 處理突發流量 (Misusing ALB for Spiky Traffic)
**錯誤描述**: 在會有瞬間巨量流量（如秒殺活動）的場景使用未暖機（Pre-warming）的 ALB。
**後果**: ALB 是透過 DNS 擴展的，擴展速度可能跟不上流量暴衝，導致 503 Service Unavailable。
**最佳實踐**: 對於極端突發流量，使用 NLB（能承受瞬間百萬級連線）或提前申請 ALB Pre-warming。

**Description**: Using a standard ALB for flash-sale events without pre-warming.
**Consequence**: ALB scales via DNS updates, which might be too slow for sudden spikes, causing 503 errors.
**Best Practice**: Use NLB for extreme spikes or request ALB Pre-warming from AWS Support.

## 5.3 忽略跨 AZ 傳輸成本 (Ignoring Cross-AZ Data Transfer Costs)
**錯誤描述**: 應用程式頻繁呼叫另一個 AZ 的資料庫或服務，或者 NAT Gateway 與 EC2 位於不同 AZ。
**後果**: AWS 內部跨 AZ 流量是要收費的。對於高吞吐系統，這筆費用可能比運算資源還貴。
**最佳實踐**: 盡量保持流量在同一 AZ 內（Availability Zone Affinity）。

**Description**: Apps frequently calling DBs in another AZ, or NAT Gateway being in a different AZ than the EC2 instances.
**Consequence**: Cross-AZ traffic incurs charges. For high-throughput systems, this can exceed compute costs.
**Best Practice**: Maintain Availability Zone Affinity where possible.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在不使用 Public Internet 的情況下，讓兩個不同 AWS 帳號的 VPC 安全通訊？
**How do you enable secure communication between VPCs in two different AWS accounts without using the public internet?**

*   **高分回答要點**:
    *   提及 **VPC Peering** (適合簡單、非遞移場景)。
    *   提及 **Transit Gateway** (適合多 VPC、Hub-and-Spoke 架構)。
    *   提及 **PrivateLink (VPC Endpoint Services)** (適合單向服務暴露，特別是 SaaS 模式，不需要互通整個 CIDR，解決 IP 衝突問題)。
    *   比較 Peering (低延遲) 與 TGW (易管理) 的取捨。

## Q2: 請解釋 Global Accelerator 與 CloudFront 的區別，以及你會如何選擇？
**Explain the difference between Global Accelerator and CloudFront. How do you choose?**

*   **高分回答要點**:
    *   **Protocol**: CloudFront 主要針對 HTTP/S (L7)；GA 支援 TCP/UDP (L4)。
    *   **Caching**: CloudFront 有快取內容；GA 沒有快取，只做路由加速。
    *   **IP**: GA 提供靜態 Anycast IP；CloudFront 提供動態 IP (雖然現在有 Dedicated IP 選項，但 GA 是原生設計)。
    *   **場景**: 需要快取靜態資源或影片串流選 CloudFront；需要加速動態 API、遊戲 UDP 封包或非 HTTP 協定選 GA。

## Q3: 我們有一個地端資料中心透過 Direct Connect 連線到 AWS。最近發現上傳大檔案到 S3 很慢，可能原因是什麼？
**We have an on-prem data center connected to AWS via Direct Connect. Uploading large files to S3 is slow. What could be the reasons?**

*   **高分回答要點**:
    *   **Public VIF vs Private VIF**: S3 是 Public Service，如果只設了 Private VIF 連 VPC，流量可能繞路或走了 VPN。應使用 Public VIF 或 VPC Endpoint for S3。
    *   **MTU (Maximum Transmission Unit)**: Jumbo Frames (9001 bytes) 是否在整條路徑上都支援？如果中間有設備不支援導致分片 (Fragmentation)，效能會大降。
    *   **TCP Window Size**: 高頻寬延遲乘積 (BDP) 網路需要調整 TCP Window Size。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **TGW is the Hub**: 在多帳號/多 VPC 環境，Transit Gateway 是標準的路由樞紐，取代了複雜的 Peering Mesh。
2.  **Layer 4 vs Layer 7**: 選擇負載平衡器時，先看協定與效能需求。NLB 為了極致效能與靜態 IP；ALB 為了應用層路由與 WAF。
3.  **Global Accelerator**: 是解決跨國延遲與 IP 白名單的神器，它利用 AWS 骨幹網路繞過公共網路的擁塞。
4.  **Hybrid Connectivity**: Direct Connect 提供穩定頻寬，但需要時間佈建；VPN 可作為備援或快速啟動方案。
5.  **IP Planning**: 永遠不要假設 `10.0.0.0/16` 是安全的，CIDR 規劃是網路架構的基石。

## 後續延伸 (Next Steps)
*   **Security**: 深入研究 AWS Network Firewall 與 AWS WAF，如何在 TGW 架構中實作「東西向流量（East-West Traffic）」的深度封包檢測（DPI）。
*   **PrivateLink**: 學習如何設計基於 PrivateLink 的內部 SaaS 架構，這在微服務與跨組織合作中非常熱門。
*   **Infrastructure as Code**: 嘗試用 Terraform 模組化你的網路架構（VPC + TGW + VPN），這是資深工程師的必備技能。

**(End of Chapter 03)**