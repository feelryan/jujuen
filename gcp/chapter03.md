# 1. 前言與學習目標 (Introduction & Learning Objectives)

本章專注於 GCP 最具差異化優勢的領域：**全球網路 (Global Networking)**。對於資深工程師而言，理解 GCP 如何利用其私有光纖網路來處理流量，是設計高效能、低延遲系統的關鍵。這不僅是配置問題，更是系統架構設計的核心決策。

This chapter focuses on the area where GCP has the most distinct advantage: **Global Networking**. For a Senior Software Engineer, understanding how GCP leverages its private fiber network to handle traffic is key to designing high-performance, low-latency systems. This is not just a configuration issue; it is a core decision in system architecture design.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分 GCP 與其他雲端的 VPC 模型差異**：理解 Global VPC 的本質，以及它如何簡化跨區域 (Cross-region) 架構。
    **Distinguish GCP's VPC model from other clouds**: Understand the nature of Global VPC and how it simplifies cross-region architecture.
2.  **精準選擇負載平衡器 (Load Balancer)**：在 Global vs. Regional、Layer 4 vs. Layer 7、Proxy vs. Pass-through 之間做出正確的架構決策。
    **Select the right Load Balancer with precision**: Make correct architectural decisions between Global vs. Regional, Layer 4 vs. Layer 7, and Proxy vs. Pass-through.
3.  **設計企業級網路拓撲**：掌握 Shared VPC 與 VPC Peering 的使用時機，以及混合雲 (Hybrid Connectivity) 的連接策略。
    **Design enterprise-grade network topologies**: Master the use cases for Shared VPC vs. VPC Peering, and strategies for Hybrid Connectivity.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 全球 VPC (The Global VPC)

**核心概念**：在 AWS 中，VPC 是 Region-bound (綁定區域) 的；但在 GCP 中，VPC 是 **Global (全球性)** 的資源。
**Core Concept**: In AWS, a VPC is Region-bound; however, in GCP, a VPC is a **Global** resource.

**心智模型 (Mental Model)**：
想像傳統網路是一個個被路由器隔開的「孤島辦公室」(AWS 模型)，要互通必須拉專線 (Peering/VPN)。而 GCP 的 VPC 就像是一個 **「全球單一大內網」**。你在東京開一個 Subnet，在紐約開一個 Subnet，它們預設就在同一個私有網路內，可以透過 Private IP 直接互通，流量走的是 Google 的骨幹網路 (Backbone)，不經過公網。

**Mental Model**:
Imagine traditional networking as isolated "island offices" separated by routers (the AWS model), requiring dedicated lines (Peering/VPN) to communicate. GCP's VPC is like a **"single global intranet."** You create a Subnet in Tokyo and another in New York; they are in the same private network by default and can communicate directly via Private IP, with traffic traversing Google's Backbone, not the public internet.

*   **Subnets are Regional**: 子網域是區域性的 (Regional)，但 VPC 是全球性的。
    **Subnets are Regional**: Subnets are regional resources, but the VPC itself is global.
*   **Firewall Rules are Global**: 防火牆規則定義在 VPC 層級，可套用到全球的實例。
    **Firewall Rules are Global**: Firewall rules are defined at the VPC level and can apply to instances globally.

## 2.2 負載平衡決策樹 (Load Balancing Decision Tree)

GCP 的負載平衡器種類繁多，選擇錯誤會導致效能瓶頸或功能缺失。請使用以下決策樹：
GCP offers a wide variety of load balancers, and choosing the wrong one can lead to performance bottlenecks or missing features. Use the following decision tree:

1.  **流量類型 (Traffic Type)**:
    *   **HTTP/HTTPS**: 選擇 Application Load Balancer (L7)。
    *   **TCP/UDP**: 選擇 Network Load Balancer (L4)。
2.  **客戶端位置 (Client Location)**:
    *   **Internet (Global)**: 需要 Anycast IP，單一 IP 服務全球用戶 -> **Global External LB**。
    *   **Specific Region**: 需要保留來源 IP 或符合法規 -> **Regional External LB**。
    *   **Internal (VPC)**: 內部微服務溝通 -> **Internal LB**。

**關鍵差異 (Key Differentiator)**:
**Global External Application Load Balancer (GCLB)** 是基於 **Maglev** 和 **Andromeda** 構建的軟體定義負載平衡器。它使用 **Anycast IP**，這意味著全球只有一個 VIP (Virtual IP)。用戶請求會進入離他們最近的 Google Edge Point of Presence (PoP)，然後透過 Google 骨幹網路直達後端。這與 DNS Load Balancing (依賴 DNS 解析不同 IP) 有本質區別。

**Key Differentiator**:
The **Global External Application Load Balancer (GCLB)** is a software-defined load balancer built on **Maglev** and **Andromeda**. It uses an **Anycast IP**, meaning there is a single VIP (Virtual IP) worldwide. User requests enter the Google Edge Point of Presence (PoP) closest to them and travel via Google's backbone to the backend. This is fundamentally different from DNS Load Balancing (which relies on DNS resolving to different IPs).

## 2.3 Shared VPC vs. VPC Peering

*   **Shared VPC**: 適用於「組織架構」。一個 Host Project 管理網路，多個 Service Projects 使用網路。**具有傳遞性 (Transitive)**，且權限管理集中。
    **Shared VPC**: Best for "Organizational Structure." One Host Project manages the network, and multiple Service Projects use it. It is **transitive** and centralizes permission management.
*   **VPC Peering**: 適用於「跨組織/跨服務」連接。兩個獨立 VPC 互連。**不具傳遞性 (Non-transitive)** (A 連 B，B 連 C，A 不能連 C)。
    **VPC Peering**: Best for "Cross-Organization/Cross-Service" connectivity. Connects two independent VPCs. It is **non-transitive** (If A connects to B, and B connects to C, A cannot connect to C).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 場景：全球低延遲 API (Global Low-Latency API)

**架構設計 (Architecture Design)**:
在系統設計面試或實務中，如果需求是「全球用戶存取，低延遲，高可用」，標準答案通常涉及 **Premium Tier Network** 加上 **Global External Application Load Balancer**。

**Architecture Design**:
In system design interviews or practice, if the requirement is "Global user access, low latency, high availability," the standard answer usually involves **Premium Tier Network** combined with a **Global External Application Load Balancer**.

*   **流程 (Flow)**: User -> Nearest Edge PoP (SSL Termination happens here!) -> Google Backbone -> Backend Instance (closest to user).
*   **優勢 (Benefits)**:
    1.  **SSL Offloading at Edge**: SSL 握手在邊緣節點完成，大幅減少 RTT (Round Trip Time)。
        **SSL Offloading at Edge**: SSL handshake completes at the edge node, significantly reducing RTT (Round Trip Time).
    2.  **Single Anycast IP**: 不需要複雜的 DNS Geo-routing 策略，DNS 快取問題被消除。
        **Single Anycast IP**: Eliminates the need for complex DNS Geo-routing strategies and removes DNS caching issues.
    3.  **Cross-Region Failover**: 如果某個區域的後端掛了，LB 會自動將流量導向次近的健康區域，無需更改 DNS。
        **Cross-Region Failover**: If backends in a region fail, the LB automatically redirects traffic to the next closest healthy region without DNS changes.

## 3.2 混合雲連接策略 (Hybrid Connectivity Strategy)

**決策矩陣 (Decision Matrix)**:

| Feature | Cloud VPN (HA) | Cloud Interconnect (Partner/Dedicated) |
| :--- | :--- | :--- |
| **SLA** | 99.99% (HA) | 99.9% - 99.99% |
| **Bandwidth** | Up to 3 Gbps per tunnel | 50 Mbps - 100 Gbps |
| **Cost** | Low (Internet traffic) | High (Physical connection) |
| **Security** | IPsec Encrypted (Public Internet) | Private Line (Unencrypted by default*) |
| **Use Case** | Backup, Low throughput, Quick setup | High throughput, Data migration, Strict latency |

*註：Interconnect 可疊加 MACsec 或 HA VPN over Interconnect 進行加密。*
*Note: Interconnect can layer MACsec or HA VPN over Interconnect for encryption.*

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 案例：配置具有 Cloud Armor 的全球負載平衡器
## 4.1 Case: Configuring a Global Load Balancer with Cloud Armor

假設我們有一個部署在 `us-central1` 和 `asia-east1` 的微服務，我們希望透過單一 IP 暴露服務，並防禦 SQL Injection 攻擊。

Suppose we have a microservice deployed in `us-central1` and `asia-east1`. We want to expose the service via a single IP and protect it against SQL Injection attacks.

### 步驟 1: 定義 Instance Groups (Backends)
### Step 1: Define Instance Groups (Backends)

首先，我們需要將 VM 放入 Managed Instance Groups (MIGs)。這是 LB 的後端單位。

First, we need to place VMs into Managed Instance Groups (MIGs). These are the backend units for the LB.

### 步驟 2: 配置 Global External Application LB (Terraform 視角)
### Step 2: Configure Global External Application LB (Terraform View)

這是一個簡化的 Terraform 結構，展示各組件的關係：
This is a simplified Terraform structure showing the relationship between components:

```hcl
# 1. Global Static IP (Anycast VIP)
resource "google_compute_global_address" "default" {
  name = "global-lb-ip"
}

# 2. Backend Service (The Logic)
resource "google_compute_backend_service" "default" {
  name        = "my-backend-service"
  protocol    = "HTTP"
  timeout_sec = 10

  # Attach Instance Groups from different regions
  backend {
    group = google_compute_region_instance_group_manager.us_mig.instance_group
  }
  backend {
    group = google_compute_region_instance_group_manager.asia_mig.instance_group
  }

  # Link Security Policy (Cloud Armor)
  security_policy = google_compute_security_policy.policy.name
  
  health_checks = [google_compute_health_check.default.id]
}

# 3. URL Map (Routing Rules)
resource "google_compute_url_map" "default" {
  name            = "url-map"
  default_service = google_compute_backend_service.default.id
}

# 4. Target HTTP Proxy
resource "google_compute_target_http_proxy" "default" {
  name    = "http-proxy"
  url_map = google_compute_url_map.default.id
}

# 5. Global Forwarding Rule (The Entry Point)
resource "google_compute_global_forwarding_rule" "default" {
  name       = "forwarding-rule"
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.default.address
}
```

### 步驟 3: 流量導向邏輯 (Traffic Steering Logic)
### Step 3: Traffic Steering Logic

當一個來自台灣的用戶訪問 `global-lb-ip`：
1.  請求進入 Google 位於台北的 Edge PoP。
2.  LB 檢查 `asia-east1` MIG 的容量與健康狀態。
3.  若健康，流量走內網直達 `asia-east1`。
4.  若 `asia-east1` 全掛，流量自動走內網導向 `us-central1` (雖然延遲增加，但服務不中斷)。

When a user from Taiwan accesses `global-lb-ip`:
1.  The request enters Google's Edge PoP in Taipei.
2.  The LB checks the capacity and health of the `asia-east1` MIG.
3.  If healthy, traffic travels via the internal network directly to `asia-east1`.
4.  If `asia-east1` is fully down, traffic is automatically routed via the internal network to `us-central1` (latency increases, but service remains available).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 誤用 Regional LB 處理全球流量 (Misusing Regional LB for Global Traffic)

**反模式**：在每個 Region 建立一個 Regional LB，然後利用 DNS (如 Route53 或 Cloud DNS) 做 Geo-routing。
**Anti-pattern**: Creating a Regional LB in each region and then using DNS (like Route53 or Cloud DNS) for Geo-routing.

**為何不好**：
*   **DNS 快取 (DNS Caching)**：當某區故障時，客戶端的 DNS 快取可能導致數分鐘的服務不可用。
*   **管理複雜度**：需要維護多個 LB IP 和複雜的 DNS 記錄。
*   **SSL 管理**：需要在多個區域管理憑證 (除非使用 Certificate Manager)。

**Why it's bad**:
*   **DNS Caching**: When a region fails, client-side DNS caching can cause minutes of service unavailability.
*   **Management Complexity**: Requires maintaining multiple LB IPs and complex DNS records.
*   **SSL Management**: Requires managing certificates in multiple regions (unless using Certificate Manager).

**修正**：使用 **Global External Application Load Balancer**，單一 IP，秒級故障轉移。
**Correction**: Use **Global External Application Load Balancer** for a single IP and second-level failover.

## 5.2 忽視跨區流量費用 (Ignoring Inter-region Traffic Costs)

**反模式**：架構設計上，App Server 在 Region A，但頻繁呼叫 Region B 的 Database，認為都在 VPC 內所以沒關係。
**Anti-pattern**: Architecting so that an App Server in Region A frequently calls a Database in Region B, assuming it's fine because they are in the same VPC.

**為何不好**：GCP 的 VPC 雖然連通方便，但 **跨區域流量 (Egress between regions)** 是要收費的，且延遲較高。
**Why it's bad**: While GCP's VPC connectivity is convenient, **Egress between regions** is billable and incurs higher latency.

**修正**：盡量保持資料在地化 (Data Locality)。App 與 DB 應部署在同一 Region，跨區僅用於備份或非同步複製。
**Correction**: Strive for Data Locality. App and DB should be deployed in the same Region; cross-region should be used only for backups or asynchronous replication.

## 5.3 混淆 Network Tier (Standard vs. Premium)
## 5.3 Confusing Network Tiers (Standard vs. Premium)

**反模式**：為了省錢，將 Global LB 的 Network Tier 設為 Standard。
**Anti-pattern**: Setting the Network Tier of a Global LB to Standard to save money.

**為何不好**：Global LB **必須** 使用 Premium Tier。Standard Tier 只能用於 Regional 資源，且流量會走公網 (Public Internet) 直到接近目標 Region，失去 Google 骨幹網的優勢。
**Why it's bad**: Global LBs **must** use Premium Tier. Standard Tier can only be used for Regional resources, and traffic traverses the Public Internet until it gets close to the destination Region, losing the advantage of Google's backbone.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在不使用 VPN 的情況下，安全地管理只有 Private IP 的 VM？
## Q1: How do you securely manage VMs with only Private IPs without using a VPN?

*   **關鍵字**: Identity-Aware Proxy (IAP), TCP Forwarding.
*   **高分回答**:
    *   不應該給 VM Public IP 僅為了 SSH/RDP。
    *   使用 **IAP for TCP forwarding**。
    *   流量流程：User -> Internet -> Google IAP (AuthN/AuthZ check) -> Tunnel -> VM (Private IP)。
    *   優點：無需 Bastion Host，整合 IAM 權限控制，具備 Context-aware access (如限制來源 IP 或設備狀態)。

*   **Keywords**: Identity-Aware Proxy (IAP), TCP Forwarding.
*   **High-scoring Answer**:
    *   Do not assign Public IPs to VMs just for SSH/RDP.
    *   Use **IAP for TCP forwarding**.
    *   Traffic Flow: User -> Internet -> Google IAP (AuthN/AuthZ check) -> Tunnel -> VM (Private IP).
    *   Benefits: No Bastion Host needed, integrated IAM permission control, supports Context-aware access (e.g., restricting source IP or device state).

## Q2: 請比較 GCP Global LB 與 AWS CloudFront + ALB 的架構差異。
## Q2: Compare the architectural differences between GCP Global LB and AWS CloudFront + ALB.

*   **關鍵字**: Anycast IP vs. DNS based CDN, Pop integration.
*   **高分回答**:
    *   AWS 通常使用 CloudFront (CDN) 作為全球入口，後端接 Regional ALB。這是兩層架構。
    *   GCP 的 Global LB 本身就具備類似 CDN 的邊緣接入能力 (Premium Tier)，且使用 Anycast IP。
    *   GCP 架構更扁平，LB 直接管理全球後端；AWS 則需要透過 CloudFront 聚合不同 Region 的 ALB。
    *   GCP 的冷啟動 (Cold start) 和全球傳播 (Global propagation) 設定通常比 DNS 變更更快生效。

*   **Keywords**: Anycast IP vs. DNS based CDN, Pop integration.
*   **High-scoring Answer**:
    *   AWS typically uses CloudFront (CDN) as the global entry point, backed by Regional ALBs. This is a two-tier architecture.
    *   GCP's Global LB inherently possesses CDN-like edge access capabilities (Premium Tier) and uses Anycast IP.
    *   GCP's architecture is flatter, with the LB directly managing global backends; AWS requires CloudFront to aggregate ALBs from different regions.
    *   GCP's cold start and global propagation of settings are generally faster than DNS changes.

## Q3: 什麼是 Private Service Connect (PSC)？它解決了什麼問題？
## Q3: What is Private Service Connect (PSC)? What problem does it solve?

*   **關鍵字**: Service Consumer/Producer, No VPC Peering, IP overlap.
*   **高分回答**:
    *   PSC 允許從自己的 VPC 私有地存取 Google APIs 或其他 VPC 的服務 (SaaS)。
    *   解決了 **VPC Peering 的痛點**：Peering 需要無重疊 CIDR (IP Overlap issue) 且具有傳遞性限制。
    *   PSC 是單向的 (Unidirectional)，更安全，且不需要協調 IP 地址規劃。

*   **Keywords**: Service Consumer/Producer, No VPC Peering, IP overlap.
*   **High-scoring Answer**:
    *   PSC allows private access to Google APIs or services in other VPCs (SaaS) from your own VPC.
    *   It solves **VPC Peering pain points**: Peering requires non-overlapping CIDR blocks and has transitivity limitations.
    *   PSC is unidirectional, more secure, and does not require coordinated IP address planning.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點回顧 (Key Takeaways)

1.  **VPC is Global**: GCP 的 VPC 是全球性的，Subnet 是區域性的。這簡化了跨區通訊。
    **VPC is Global**: GCP's VPC is global, and Subnets are regional. This simplifies cross-region communication.
2.  **Anycast IP**: Global External LB 使用單一 Anycast IP 服務全球，提供比 DNS LB 更快的故障轉移與更低的延遲。
    **Anycast IP**: Global External LB uses a single Anycast IP to serve the world, offering faster failover and lower latency than DNS LB.
3.  **Shared VPC**: 企業級環境中，使用 Shared VPC 來分離網路管理 (Host Project) 與服務部署 (Service Project)。
    **Shared VPC**: In enterprise environments, use Shared VPC to separate network management (Host Project) from service deployment (Service Project).
4.  **Hybrid Connectivity**: 根據 SLA 和頻寬需求選擇 Cloud VPN (HA) 或 Cloud Interconnect。
    **Hybrid Connectivity**: Choose Cloud VPN (HA) or Cloud Interconnect based on SLA and bandwidth requirements.
5.  **Security at Edge**: 利用 Global LB 整合 Cloud Armor 與 SSL Offloading，將攻擊與負載擋在 Google 網路邊緣。
    **Security at Edge**: Leverage Global LB integration with Cloud Armor and SSL Offloading to stop attacks and load at the edge of Google's network.

## 下一步 (Next Steps)

掌握了網路流量如何進入與流動後，下一章我們將探討如何保護這些資源。
Now that you master how traffic enters and flows, in the next chapter we will explore how to secure these resources.

*   **Next Chapter**: `chapter04` - **IAM 與安全性最佳實踐 (IAM & Security Best Practices)**。
*   **延伸閱讀**: 閱讀 Google SRE Book 中關於 Load Balancing 的章節 (Maglev, Andromeda)，深入了解底層原理。
    **Further Reading**: Read the Load Balancing chapters in the Google SRE Book (Maglev, Andromeda) for a deep dive into the underlying principles.