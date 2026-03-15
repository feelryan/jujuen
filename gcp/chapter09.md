# 1. 前言與學習目標 (Introduction & Learning Objectives)

在高階系統設計中，讓系統「跑起來」只是第一步，讓系統在極端故障下「活下去」才是資深工程師的價值所在。本章聚焦於 GCP 環境下的高可用性（High Availability, HA）與災難復原（Disaster Recovery, DR）。這不僅是技術堆疊的選擇，更是對商業風險（RTO/RPO）與成本（FinOps）的權衡藝術。

In high-level system design, getting the system "running" is just the first step; ensuring it "survives" extreme failures is where a Senior Engineer proves their worth. This chapter focuses on High Availability (HA) and Disaster Recovery (DR) within the GCP environment. This is not merely about technology stack selection, but the art of balancing business risks (RTO/RPO) and costs (FinOps).

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精確定義與量化可靠性指標**：理解並能向 Stakeholders 解釋 RTO（復原時間目標）、RPO（復原點目標）與 SLA 的關係。
    **Precisely define and quantify reliability metrics**: Understand and explain the relationship between RTO (Recovery Time Objective), RPO (Recovery Point Objective), and SLA to stakeholders.
2.  **設計多區域（Multi-region）架構**：利用 GCP 獨有的 Global VPC 與 Global Load Balancing 構建 Active-Active 或 Active-Passive 架構。
    **Design Multi-region architectures**: Leverage GCP's unique Global VPC and Global Load Balancing to build Active-Active or Active-Passive architectures.
3.  **實施 FinOps 成本優化**：在追求高可用性的同時，識別昂貴的跨區流量與閒置資源，並提出分級的 DR 策略以節省預算。
    **Implement FinOps cost optimization**: While pursuing high availability, identify expensive cross-region traffic and idle resources, and propose tiered DR strategies to save budget.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 HA vs. DR：故障半徑的差異 (The Difference in Blast Radius)

很多工程師會混淆 HA 與 DR。請建立以下心智模型：
Many engineers confuse HA with DR. Establish the following mental model:

*   **High Availability (HA)**：目標是**消除單點故障（SPOF）**。通常處理的是「區域性（Zonal）」故障（如單一機房斷電、硬體損壞）。在 GCP 中，這意味著跨 Zone 部署（Regional Resources）。HA 是自動化的，使用者通常無感。
    **High Availability (HA)**: The goal is to **eliminate Single Points of Failure (SPOF)**. It typically handles "Zonal" failures (e.g., single datacenter power outage, hardware failure). In GCP, this means cross-Zone deployment (Regional Resources). HA is automated and usually transparent to users.
*   **Disaster Recovery (DR)**：目標是**業務連續性（Business Continuity）**。處理的是「廣域（Regional）」故障（如地震、海底電纜切斷、整個 GCP Region 下線）。DR 往往涉及跨 Region 的資料複製與流量切換，可能需要人工介入或複雜的自動化流程。
    **Disaster Recovery (DR)**: The goal is **Business Continuity**. It handles "Regional" failures (e.g., earthquakes, cut submarine cables, entire GCP Region outage). DR often involves cross-Region data replication and traffic shifting, potentially requiring manual intervention or complex automation.

## 2.2 RTO 與 RPO (RTO & RPO)

這是設計 DR 策略的數學基礎：
These are the mathematical foundations for designing DR strategies:

*   **RPO (Recovery Point Objective)**: **你能容忍遺失多少資料？**（時間維度）。若 RPO = 0，代表資料必須同步複製（Synchronous Replication），這會帶來寫入延遲（Latency）與可用性風險（CAP 定理）。
    **RPO (Recovery Point Objective)**: **How much data loss can you tolerate?** (Time dimension). If RPO = 0, data must be synchronously replicated, which introduces write latency and availability risks (CAP Theorem).
*   **RTO (Recovery Time Objective)**: **系統能停機多久？** 若 RTO < 1 分鐘，通常需要熱備援（Hot Standby / Active-Active）；若 RTO = 24 小時，則備份還原（Backup & Restore）可能就足夠且更便宜。
    **RTO (Recovery Time Objective)**: **How long can the system be down?** If RTO < 1 minute, you typically need Hot Standby / Active-Active; if RTO = 24 hours, Backup & Restore might be sufficient and cheaper.

## 2.3 GCP 的獨特優勢：Global Resources (GCP's Unique Advantage)

與 AWS 不同，GCP 的網路基礎設施是全球性的。
Unlike AWS, GCP's network infrastructure is global.

*   **Global VPC**: 一個 VPC 可以跨越多個 Regions。這簡化了跨區通訊的複雜度（不需要像 AWS 那樣配置繁瑣的 VPC Peering 或 Transit Gateway）。
    **Global VPC**: A single VPC can span multiple Regions. This simplifies cross-region communication complexity (no need for cumbersome VPC Peering or Transit Gateways like in AWS).
*   **Global Load Balancer (GCLB)**: 使用 Anycast IP，單一 IP 即可將流量導向全球最近的 Region。這是實現 Multi-region Active-Active 架構的神器。
    **Global Load Balancer (GCLB)**: Uses Anycast IP, allowing a single IP to route traffic to the nearest Region globally. This is a superpower for implementing Multi-region Active-Active architectures.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與 System Design 面試中，我們通常將 DR 策略分為三個層級（Tiered Strategy），以平衡成本與風險。

In Production environments and System Design interviews, we typically categorize DR strategies into three tiers to balance cost and risk.

## 3.1 Tier 1: Hot / Active-Active (關鍵業務 Critical Path)

*   **場景 (Scenario)**: 支付網關、核心帳務系統、即時競價廣告。
    **Scenario**: Payment gateways, core ledgers, real-time bidding ads.
*   **架構 (Architecture)**:
    *   **Compute**: GKE Clusters 或 Cloud Run 部署在多個 Regions (e.g., `asia-east1`, `us-central1`)。
    *   **Network**: Global External HTTPS Load Balancer 前端接收流量，根據延遲或權重分發。
    *   **Data**: Cloud Spanner (Multi-region configuration) 提供強一致性與 99.999% SLA。
*   **FinOps**: 極其昂貴。計算資源需全時運轉，Spanner 節點成本高，且跨區資料傳輸（Egress）費用可觀。
    **FinOps**: Extremely expensive. Compute resources run 24/7, Spanner nodes are costly, and cross-region data transfer (Egress) fees are significant.

## 3.2 Tier 2: Warm / Active-Passive (重要業務 Important Business)

*   **場景 (Scenario)**: 使用者設定檔、訂單歷史查詢、內部管理後台。
    **Scenario**: User profiles, order history lookup, internal admin dashboards.
*   **架構 (Architecture)**:
    *   **Data**: Cloud SQL (PostgreSQL/MySQL) 在主 Region 運作，並配置 **Cross-Region Read Replica**。
    *   **Compute**: 備用 Region 的 GKE/VM 保持最小規模（Pilot Light）或僅在故障時透過 Auto Scaling 啟動。
*   **RTO/RPO**: RPO 取決於 Replication lag (通常 < 1s)；RTO 取決於 Promote Replica 的時間 (數分鐘)。
    **RTO/RPO**: RPO depends on Replication lag (usually < 1s); RTO depends on the time to Promote Replica (minutes).

## 3.3 Tier 3: Cold / Backup & Restore (非關鍵業務 Non-Critical)

*   **場景 (Scenario)**: 報表生成、批次處理作業、開發測試環境。
    **Scenario**: Report generation, batch processing jobs, dev/test environments.
*   **架構 (Architecture)**:
    *   **Data**: 定期 Snapshot 並儲存於 Multi-region GCS Bucket。
    *   **Compute**: 災難發生時，使用 IaC (Terraform) 在新 Region 重建基礎設施。
*   **FinOps**: 最便宜。平時無運算成本，僅支付儲存費用。
    **FinOps**: Cheapest. No compute costs during normal times, only storage fees.

---

# 4. 逐步示例：設計一個具備 DR 能力的訂單系統 (Walkthrough: Designing a DR-Capable Order System)

### 背景 (Context)
我們有一個電子商務訂單服務，目前部署在 `asia-east1` (Taiwan)。業務要求：若台灣機房全毀，系統需在 15 分鐘內於 `asia-northeast1` (Tokyo) 恢復服務 (RTO < 15m)，且資料遺失不超過 1 分鐘 (RPO < 1m)。

We have an e-commerce order service currently deployed in `asia-east1` (Taiwan). Business requirement: If the Taiwan datacenter is completely destroyed, the system must recover in `asia-northeast1` (Tokyo) within 15 minutes (RTO < 15m), with data loss not exceeding 1 minute (RPO < 1m).

### 步驟 1: 資料層改造 (Step 1: Data Layer Transformation)

單一 Cloud SQL 無法滿足 Region 級別的故障轉移。我們需要建立跨區複本。

A single Cloud SQL instance cannot handle Region-level failover. We need to establish a cross-region replica.

```hcl
# Terraform 示意 (Simplified)
resource "google_sql_database_instance" "primary" {
  name             = "order-db-primary"
  region           = "asia-east1"
  database_version = "POSTGRES_14"
  settings {
    tier              = "db-custom-4-16384"
    availability_type = "REGIONAL" # HA within the region
    backup_configuration {
      enabled = true
      binary_log_enabled = true # Required for replication
    }
  }
}

resource "google_sql_database_instance" "dr_replica" {
  name                 = "order-db-dr-replica"
  region               = "asia-northeast1" # DR Region
  database_version     = "POSTGRES_14"
  master_instance_name = google_sql_database_instance.primary.name
  
  # Replica configuration
  settings {
    tier = "db-custom-4-16384" 
  }
}
```

### 步驟 2: 流量入口改造 (Step 2: Traffic Entry Transformation)

將 Regional Load Balancer 升級為 **Global External Application Load Balancer**。

Upgrade the Regional Load Balancer to a **Global External Application Load Balancer**.

*   配置兩個 Backend Services：一個指向 `asia-east1` 的 Instance Group，另一個指向 `asia-northeast1`。
*   利用 **Cloud Armor** 與 **Health Checks**。平時 `asia-northeast1` 的應用程式可能處於縮編狀態（0 或 1 個實例），或者 Health Check 設為不健康（如果不想接流量）。

### 步驟 3: 災難復原流程 (Step 3: Disaster Recovery Procedure)

當 `asia-east1` 發生災難時，自動或手動執行以下流程：

When a disaster occurs in `asia-east1`, execute the following process (automatically or manually):

1.  **Promote DR Replica**: 將東京的 Read Replica 提升為 Primary Instance。
    **Promote DR Replica**: Promote the Read Replica in Tokyo to be the Primary Instance.
    `gcloud sql instances promote order-db-dr-replica`
2.  **Update Config**: 更新應用程式配置（Secret Manager），將 DB Endpoint 指向新的 Primary。
    **Update Config**: Update application configuration (Secret Manager) to point the DB Endpoint to the new Primary.
3.  **Scale Up Compute**: 擴展東京區的 GKE/Cloud Run 實例數量以承接全量流量。
    **Scale Up Compute**: Scale up GKE/Cloud Run instances in Tokyo to handle full traffic load.
4.  **DNS/LB Switch**: Global LB 會自動偵測到台灣區 Health Check 失敗，將流量導向東京。
    **DNS/LB Switch**: The Global LB will automatically detect the health check failure in Taiwan and route traffic to Tokyo.

### FinOps 分析 (FinOps Analysis)

*   **Cost**: 我們支付了額外的一個 DB 實例費用 + 跨區複製流量費。
*   **Optimization**: 為了省錢，東京的 Replica 可以使用較小的機器規格（Tier），但在 Promote 之後需立即 Resize 到生產規格（注意 Resize 會有短暫 downtime）。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 依賴 IP 而非 DNS (Relying on IPs instead of DNS)
*   **錯誤 (Pitfall)**: 在設定檔中寫死 Primary DB 的 IP 地址。
*   **後果 (Consequence)**: DR 切換後，新 DB 的 IP 會改變，導致需要重新部署應用程式代碼或重啟服務，延長 RTO。
*   **修正 (Fix)**: 使用 Private Service Connect 或 Internal DNS，並在切換時更新 DNS 指向，或使用 Proxy 層（如 PgBouncer）。

## 5.2 忽視 Split-Brain (Ignoring Split-Brain)
*   **錯誤 (Pitfall)**: 在網路分區（Network Partition）發生時，自動化腳本誤判 Primary 掛了，自動提升 Secondary，結果原 Primary 其實還活著且能接收部分寫入。
*   **後果 (Consequence)**: 兩個資料庫同時寫入，資料不一致，修復極其困難。
*   **修正 (Fix)**: 對於強一致性要求高的系統，使用 Cloud Spanner（Paxos 協議保證）或在自動切換邏輯中加入嚴格的 Quorum 機制 / 人工確認按鈕。

## 5.3 只有備份，沒有演練 (Backups without Drills)
*   **錯誤 (Pitfall)**: 認為有了 Snapshot 和 Terraform 就萬無一失，從未實際演練過復原。
*   **後果 (Consequence)**: 災難發生時，發現 IAM 權限不足、KMS Key 無法跨區解密，或復原時間遠超預期。
*   **修正 (Fix)**: 定期執行 **Game Days** (DiRT - Disaster Recovery Testing)。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何為一個全球性的銀行帳務系統設計架構，要求 RPO = 0？
**How would you design an architecture for a global banking ledger system requiring RPO = 0?**

*   **高分回答要點 (Key Points)**:
    *   **承認物理限制**: RPO=0 意味著同步寫入，這會受光速限制影響延遲。
    *   **解決方案**: 推薦使用 **Cloud Spanner**。它是 GCP 唯一能提供跨 Region 同步複製且具備強一致性（External Consistency）的資料庫。
    *   **架構細節**: 設定 Multi-region Spanner Instance（如 `nam-eur-asia1`），利用 TrueTime API 解決分散式時鐘問題。
    *   **Trade-off**: 寫入延遲較高，成本極高。非核心交易資料（如 Log）可降級使用 BigQuery 或 Cloud SQL 異步複製。

## Q2: 在 Active-Active 架構中，如何處理雙寫衝突（Write Conflicts）？
**In an Active-Active architecture, how do you handle write conflicts?**

*   **高分回答要點 (Key Points)**:
    *   **避免雙寫**: 最好的策略是避免衝突。利用 Global LB 的 **Geo-routing** 或 User ID Sharding，確保特定使用者的寫入總是導向同一個 Region。
    *   **衝突解決策略**: 如果必須多點寫入（如協作編輯），需引入 CRDTs (Conflict-free Replicated Data Types) 或 Last-Write-Wins (LWW) 策略（但 LWW 會丟資料）。
    *   **資料庫選擇**: 使用支援 Multi-master 的資料庫（如 Spanner, Firestore in Datastore mode）或 NoSQL (Cassandra/Bigtable) 並在應用層處理最終一致性。

## Q3: 如何在不大幅增加預算的情況下，將單區系統升級為具備 DR 能力？
**How to upgrade a single-region system to be DR-capable without significantly increasing the budget?**

*   **高分回答要點 (Key Points)**:
    *   **Pilot Light 策略**: 在 DR Region 建立資料庫複本（這是主要成本），但 Compute 資源保持為 0 或極小（使用 Cloud Run 或 GKE Autopilot）。
    *   **GCS 複製**: 對於靜態資源，開啟 GCS 的 Multi-region 或 Dual-region bucket，成本增加有限但可靠性大增。
    *   **IaC**: 準備好完整的 Terraform 腳本，確保在災難時能快速佈建資源，而不是讓資源閒置空轉（Cold Standby）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **HA != DR**: HA 針對 Zone 故障（自動），DR 針對 Region 故障（通常需計畫）。
2.  **RTO/RPO 決定架構**: 不要盲目追求 Active-Active，先看業務能容忍多少停機時間與資料遺失。
3.  **GCP Global Network**: 善用 Global VPC 與 Global Load Balancer，這是 GCP 相較於其他雲端的最大優勢。
4.  **Spanner vs. Cloud SQL**: RPO=0 選 Spanner；RPO>0 且預算有限選 Cloud SQL Cross-Region Replica。
5.  **FinOps**: DR 是昂貴的保險。區分業務等級（Tier 1/2/3），為不同等級配置不同的 DR 策略以優化成本。

## 後續延伸 (Next Steps)
*   **Next Chapter**: 進入 **Chapter 10: Observability & SRE Practices**。一旦建立了複雜的多區架構，你需要更強大的監控（Cloud Monitoring）、日誌（Cloud Logging）與追蹤（Cloud Trace）能力來診斷跨區延遲與故障。
*   **Action Item**: 在你的開發環境中，試著建立一個 Cloud SQL 的 Cross-Region Replica，並手動執行一次 Promote 操作，觀察應用程式斷線多久（測量實際 RTO）。