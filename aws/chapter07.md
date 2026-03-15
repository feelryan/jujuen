# 1. 前言與學習目標 (Introduction & Learning Objectives)

在高流量與關鍵任務系統中，「系統會失敗」是唯一不變的真理。作為資深工程師，你的職責不再只是防止失敗，而是設計出能優雅地處理失敗的系統。本章將帶你從單純的備份思維，轉向全面的彈性架構設計。

In high-traffic and mission-critical systems, "systems will fail" is the only constant truth. As a Senior Engineer, your responsibility shifts from merely preventing failure to designing systems that handle failure gracefully. This chapter moves you from a simple backup mindset to comprehensive resilient architecture design.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精確定義 RTO 與 RPO**：根據業務需求量化復原時間目標（RTO）與復原點目標（RPO），並據此選擇合適的 AWS 服務。
    **Define RTO & RPO precisely:** Quantify Recovery Time Objective (RTO) and Recovery Point Objective (RPO) based on business needs, and select appropriate AWS services accordingly.
2.  **區分 HA 與 DR 的架構差異**：清楚界定高可用性（High Availability, Multi-AZ）與災難復原（Disaster Recovery, Multi-Region）的實作邊界。
    **Distinguish between HA and DR architectures:** Clearly define the implementation boundaries between High Availability (Multi-AZ) and Disaster Recovery (Multi-Region).
3.  **設計 Active-Active 與 Active-Passive 策略**：評估並實作 Pilot Light、Warm Standby 與 Multi-Region Active-Active 架構，並理解其成本與複雜度權衡。
    **Design Active-Active vs. Active-Passive strategies:** Evaluate and implement Pilot Light, Warm Standby, and Multi-Region Active-Active architectures, understanding their cost and complexity trade-offs.
4.  **解決跨區域資料一致性挑戰**：在分散式系統中處理跨 Region 的資料複製延遲與衝突解決（Conflict Resolution）。
    **Address cross-region data consistency challenges:** Handle cross-region data replication lag and conflict resolution in distributed systems.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 HA vs. DR：範圍與目標 (Scope & Goals)

**直覺類比 (Analogy):**
*   **High Availability (HA)** 就像是飛機有四個引擎。如果一個壞了，其他的可以立刻接手，乘客（使用者）幾乎感覺不到差異。這通常發生在同一個機場（Region）的不同跑道（Availability Zone）之間。
*   **Disaster Recovery (DR)** 就像是整個機場被關閉（例如因颱風）。你需要有計畫地將航班轉降到另一個城市的機場（Different Region）。這通常需要時間，且可能會有部分行程（資料）遺失。

**High Availability (HA)** is like a plane having four engines. If one fails, the others take over immediately, and the passengers (users) barely notice. This typically happens between different runways (Availability Zones) within the same airport (Region).
**Disaster Recovery (DR)** is like the entire airport shutting down (e.g., due to a typhoon). You need a plan to divert flights to an airport in another city (Different Region). This usually takes time and might involve some loss of itinerary (data).

**正規定義 (Formal Definition):**
*   **HA (High Availability):** 目標是最大化正常運作時間（Uptime，如 99.99%）。透過消除單點故障（SPOF）與使用冗餘元件（Redundancy）來達成。在 AWS 中，HA 的標準做法是 **Multi-AZ**。
    **HA (High Availability):** The goal is to maximize uptime (e.g., 99.99%). Achieved by eliminating Single Points of Failure (SPOF) and using redundancy. In AWS, the standard practice for HA is **Multi-AZ**.
*   **DR (Disaster Recovery):** 目標是在災難發生後恢復系統運作。重點在於 RTO（要多久恢復？）與 RPO（能容忍遺失多少資料？）。在 AWS 中，DR 通常涉及 **Multi-Region**。
    **DR (Disaster Recovery):** The goal is to restore system operations after a disaster. The focus is on RTO (How long to recover?) and RPO (How much data loss is tolerable?). In AWS, DR typically involves **Multi-Region**.

## 2.2 RTO 與 RPO (The Metrics that Matter)

這兩個指標決定了架構的成本與複雜度。
These two metrics dictate the cost and complexity of your architecture.

*   **RPO (Recovery Point Objective):** 最大允許資料遺失量（以時間衡量）。
    *   RPO = 0 分鐘：需要同步複製（Synchronous Replication），極高成本與延遲影響。
    *   RPO = 24 小時：每日備份即可。
    **RPO (Recovery Point Objective):** The maximum acceptable data loss (measured in time).
    *   RPO = 0 min: Requires synchronous replication; extremely high cost and latency impact.
    *   RPO = 24 hours: Daily backups suffice.

*   **RTO (Recovery Time Objective):** 最大允許停機時間。
    *   RTO = 0 分鐘：需要 Active-Active 架構與自動故障轉移。
    *   RTO = 4 小時：允許人工介入啟動備援環境。
    **RTO (Recovery Time Objective):** The maximum acceptable downtime.
    *   RTO = 0 min: Requires Active-Active architecture and automatic failover.
    *   RTO = 4 hours: Allows manual intervention to spin up the backup environment.

## 2.3 四種 DR 策略光譜 (The Spectrum of DR Strategies)

從最便宜/最慢 到 最貴/最快：
From cheapest/slowest to most expensive/fastest:

1.  **Backup & Restore:** 資料存 S3，災難時重新建立 Infra。 (RTO: Hours/Days)
2.  **Pilot Light:** 資料庫即時複製到備援 Region，但 App Server 關閉或只有極少量。災難時 scaling up。 (RTO: Tens of minutes)
3.  **Warm Standby:** 備援 Region 有縮小版的完整環境一直在跑。災難時 scaling out。 (RTO: Minutes)
4.  **Multi-Site Active-Active:** 兩個 Region 同時服務流量。 (RTO: Near Zero)

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或實際架構規劃中，HA/DR 是展現資深程度的關鍵。初階工程師只會說 "Put it in S3"，資深工程師會討論 "S3 Cross-Region Replication 的延遲與 Consistency 模型"。

In System Design Interviews or actual architectural planning, HA/DR is key to demonstrating seniority. Junior engineers might just say "Put it in S3," while senior engineers discuss "S3 Cross-Region Replication latency and Consistency models."

## 3.1 各層級的 HA/DR 實作 (Implementation by Layer)

### Compute Layer (EC2 / Containers / Lambda)
*   **HA:** 使用 Auto Scaling Groups (ASG) 跨越多個 AZ。確保 Capacity 足夠應對一個 AZ 倒下的情況。
    **HA:** Use Auto Scaling Groups (ASG) spanning multiple AZs. Ensure sufficient capacity to handle the loss of one AZ.
*   **DR:** 在備援 Region 準備好 AMI 或 Container Images。使用 Infrastructure as Code (Terraform/CloudFormation) 快速在異地重建環境。
    **DR:** Have AMIs or Container Images ready in the backup Region. Use Infrastructure as Code (Terraform/CloudFormation) to rapidly reconstruct the environment remotely.

### Database Layer (RDS / Aurora / DynamoDB)
*   **HA:**
    *   **RDS:** 開啟 Multi-AZ。AWS 會自動處理同步複製與 Failover（DNS 切換）。
    *   **DynamoDB:** 預設即為 Multi-AZ。
    **HA:**
    *   **RDS:** Enable Multi-AZ. AWS handles synchronous replication and failover (DNS switch) automatically.
    *   **DynamoDB:** Multi-AZ by default.
*   **DR:**
    *   **RDS:** 建立 Cross-Region Read Replica（非同步複製）。災難時將 Replica 晉升（Promote）為 Primary。
    *   **DynamoDB:** 使用 Global Tables（Multi-Master / Active-Active）。
    **DR:**
    *   **RDS:** Create Cross-Region Read Replicas (asynchronous replication). Promote the Replica to Primary during a disaster.
    *   **DynamoDB:** Use Global Tables (Multi-Master / Active-Active).

### Storage Layer (S3 / EFS)
*   **HA:** S3 Standard 與 EFS Standard 預設將資料寫入至少 3 個 AZ。
    **HA:** S3 Standard and EFS Standard write data to at least 3 AZs by default.
*   **DR:** 開啟 S3 Cross-Region Replication (CRR)。注意：這是非同步的，且刪除標記（Delete Markers）的複製策略需要小心配置以防人為誤刪。
    **DR:** Enable S3 Cross-Region Replication (CRR). Note: This is asynchronous, and replication strategies for Delete Markers need careful configuration to prevent accidental human deletion.

### Networking / Traffic (Route 53 / Global Accelerator)
*   **The Switch:** Route 53 是 DR 的核心開關。利用 Health Checks 與 Failover Routing Policy 將流量導向健康的 Region。
    **The Switch:** Route 53 is the core switch for DR. Use Health Checks and Failover Routing Policies to direct traffic to a healthy Region.

## 3.2 設計權衡 (Design Trade-offs)

*   **Cost vs. RTO:** Active-Active 最快，但成本是單一 Region 的兩倍以上（因為需要預留冗餘容量）。
    **Cost vs. RTO:** Active-Active is the fastest but costs more than double a single region (due to redundant capacity reservation).
*   **Consistency vs. Latency:** 跨 Region 幾乎都依賴非同步複製（Asynchronous Replication）。如果強求強一致性（Strong Consistency），會導致巨大的寫入延遲（物理光速限制）。
    **Consistency vs. Latency:** Cross-region almost always relies on asynchronous replication. Enforcing strong consistency introduces massive write latency (limited by the speed of light).

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境：全球電商訂單系統 (Scenario: Global E-commerce Order System)
**目標：** 即使 `us-east-1` 完全癱瘓，系統仍能在 15 分鐘內於 `us-west-2` 恢復運作，且資料遺失不超過 5 分鐘。
**Goal:** Even if `us-east-1` goes down completely, the system must recover in `us-west-2` within 15 minutes, with no more than 5 minutes of data loss.

*   **RTO:** 15 mins
*   **RPO:** 5 mins
*   **Strategy:** Warm Standby

### Step 1: 資料層設置 (Data Layer Setup)

我們不能等到災難發生才搬資料。
We cannot wait for the disaster to move data.

1.  **RDS (PostgreSQL):** 在 Primary Region (`us-east-1`) 運行 Multi-AZ RDS。
2.  **Replication:** 建立一個 Read Replica 在 `us-west-2`。
    *   *Why?* 這是非同步複製，延遲通常在秒級，滿足 RPO < 5 mins。
3.  **S3:** 對於靜態資源（圖片、發票 PDF），開啟 CRR 到 `us-west-2` 的 Bucket。

### Step 2: 運算層設置 (Compute Layer Setup)

使用 "Warm Standby" 策略。
Using the "Warm Standby" strategy.

1.  **Primary Region:** ASG 運行 100 台機器。
2.  **DR Region:** ASG 設置 Min=2, Max=100。
    *   *Why?* 保持少量機器運行（Warm），確保應用程式配置正確且能連上本地的 Read Replica DB。這比 "Pilot Light"（機器全關）更快，但比 "Active-Active" 便宜。

### Step 3: 流量切換配置 (Traffic Switch Configuration)

使用 Route 53 進行 DNS Failover。
Use Route 53 for DNS Failover.

```json
// Route 53 Record Set (Conceptual)
{
  "Name": "api.myshop.com",
  "Type": "A",
  "SetIdentifier": "Primary",
  "Weight": 100, // Or Failover Policy: PRIMARY
  "Region": "us-east-1",
  "HealthCheckId": "hc-12345", // Checks /health endpoint in us-east-1
  "AliasTarget": { "DNSName": "alb-us-east-1..." }
},
{
  "Name": "api.myshop.com",
  "Type": "A",
  "SetIdentifier": "Secondary",
  "Weight": 0, // Or Failover Policy: SECONDARY
  "Region": "us-west-2",
  "AliasTarget": { "DNSName": "alb-us-west-2..." }
}
```

### Step 4: 災難發生時的流程 (Failover Procedure)

當 `us-east-1` 斷線：
When `us-east-1` goes offline:

1.  **Detection:** Route 53 Health Check 失敗。
2.  **Traffic Shift:** Route 53 自動將 DNS 解析轉向 `us-west-2`。但此時 DB 還是 Read-only。
3.  **DB Promotion (Automation/Manual):**
    *   呼叫 RDS API: `promote-read-replica` 將 `us-west-2` 的 DB 升級為獨立 Primary。
    *   更新 App Config 指向新的 Primary DB Endpoint（如果沒有使用 CNAME 抽象化）。
4.  **Scaling:** `us-west-2` 的 ASG 偵測到流量暴增（CPU 上升），觸發 Scale Out 從 2 台擴展到 100 台。

**實務考量 (Practical Note):** 步驟 3 通常建議「人工確認後執行」或「高度成熟的自動化」，以避免 False Positive 導致的腦裂（Split-brain）。
**Practical Note:** Step 3 is usually recommended to be "manually confirmed" or handled by "highly mature automation" to avoid Split-brain scenarios caused by False Positives.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 誤以為 Multi-AZ 就是 DR (Confusing Multi-AZ with DR)
*   **錯誤 (Pitfall):** 認為開了 RDS Multi-AZ 就萬無一失。
*   **後果 (Consequence):** Multi-AZ 只能防護單一資料中心故障。如果駭客刪除資料、或是整個 Region 停電（極少見但發生過），Multi-AZ 完全無效，因為刪除指令會同步複製到 Standby。
*   **修正 (Fix):** DR 需要 **離線備份 (AWS Backup)** 或 **跨區域複製 (Cross-Region Replication)**。

## 5.2 忽略 Service Quotas (Ignoring Service Quotas in DR Region)
*   **錯誤 (Pitfall):** 在 Primary Region 有 1000 個 vCPU 的 Quota，但在 DR Region 預設只有 32 個 vCPU。
*   **後果 (Consequence):** 災難發生時，Auto Scaling Group 無法啟動足夠的實例，系統雖然切換過去了但立刻被流量打掛。
*   **修正 (Fix):** 定期在 DR Region 申請並檢查 Service Quotas。

## 5.3 硬編碼依賴 (Hardcoded Dependencies)
*   **錯誤 (Pitfall):** 程式碼中寫死 `us-east-1` 的 S3 Bucket 名稱或 ARN。
*   **後果 (Consequence):** 即使服務在 DR Region 跑起來，嘗試存取 S3 時仍會連回原本故障的 Region（導致失敗）或因跨 Region 傳輸產生高額費用。
*   **修正 (Fix):** 使用環境變數注入 Region 依賴，或使用相對路徑/動態解析。

## 5.4 薛丁格的備份 (Schrödinger's Backup)
*   **錯誤 (Pitfall):** 有備份機制，但從未演練過還原。
*   **後果 (Consequence):** 真正災難發生時，才發現備份檔案損壞、加密金鑰遺失（KMS Key 是 Region bound 的！），或還原時間長達 3 天（RTO 失敗）。
*   **修正 (Fix):** 定期執行 Game Days（災難演練），實際測試還原流程。確保 KMS Key 在 DR Region 也有複本或對應的 Key。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在 Active-Active 架構中處理資料衝突？
**How do you handle data conflicts in an Active-Active architecture?**

*   **高分回答要點 (Key Points):**
    *   承認**物理限制**：跨 Region 無法做強一致性（除非接受極高延遲）。
    *   **Last Writer Wins (LWW):** 最簡單，依賴精確的時間戳記（但需注意時鐘偏差）。
    *   **CRDTs (Conflict-free Replicated Data Types):** 提及 DynamoDB Global Tables 使用類似機制。
    *   **業務邏輯分區 (Sharding by User/Region):** 這是最實用的解法。讓特定使用者的寫入總是導向同一個 Region，只在該 Region 掛掉時才 Failover。這樣將 Active-Active 降級為多個 Active-Passive 的組合，避免衝突。

## Q2: 請解釋 Pilot Light 和 Warm Standby 的區別，你會如何選擇？
**Explain the difference between Pilot Light and Warm Standby. How would you choose?**

*   **高分回答要點 (Key Points):**
    *   **核心差異：** Pilot Light 的 App Server 是「關閉」的（或只有 DB 活著）；Warm Standby 的 App Server 是「運作中但縮編的」。
    *   **RTO 影響：** Pilot Light 需要時間開機、暖機、拉 Image，RTO 較長；Warm Standby 只要 Scale out，RTO 較短。
    *   **選擇依據：** 預算 vs. 業務緊急度。如果是內部報表系統，Pilot Light 足矣；如果是核心交易系統，至少 Warm Standby。

## Q3: 在使用 S3 Cross-Region Replication 時，有哪些安全與成本考量？
**What are the security and cost considerations when using S3 Cross-Region Replication?**

*   **高分回答要點 (Key Points):**
    *   **成本：** 除了存儲費用翻倍，還需支付 **Data Transfer Out** 的流量費（這是隱形殺手）。
    *   **安全：** 來源 Bucket 和目標 Bucket 的 KMS Key 不同。需要確保目標 Region 的 IAM Role 有權限解密來源資料並用目標 Region 的 Key 加密寫入。
    *   **防護：** 必須在兩個 Bucket 都開啟 Versioning。建議開啟 MFA Delete 以防惡意刪除同步。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **HA $\neq$ DR**: HA 是針對 AZ 失效（同步、自動）；DR 是針對 Region 失效（通常非同步、需決策）。
2.  **RTO/RPO 決定架構**: 不要盲目追求 RTO=0，那非常昂貴。根據業務價值定價。
3.  **Route 53 是切換器**: DNS Failover 是跨 Region 切換的最常見入口。
4.  **資料有重力 (Data Gravity)**: Compute 容易搬移，Data 搬移很難。DR 的核心在於資料複製策略（RDS Read Replicas, DynamoDB Global Tables, S3 CRR）。
5.  **KMS 是 Region Bound**: 跨 Region 複製加密資料時，務必處理好金鑰管理。

## 後續延伸 (Next Steps)
*   **實作 (Action):** 在 AWS Console 中建立一個 RDS，並練習建立跨 Region 的 Read Replica。觀察 Promotion 的過程。
*   **閱讀 (Read):** 閱讀 AWS Well-Architected Framework 中的 "Reliability Pillar"。
*   **下一章預告 (Next Chapter):** 既然談到了高可用與流量切換，下一章我們將深入 **AWS Networking & VPC Design**，探討如何構建安全且高效的網路基底來支撐這些架構。