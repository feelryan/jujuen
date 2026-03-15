# 1. 前言與學習目標 (Introduction & Learning Objectives)

在系統設計面試（System Design Interview）與高流量生產環境中，「資料庫如何不掉資料」與「服務如何不中斷」是區分 Senior 與 Staff 工程師的關鍵分水嶺。本章不只討論語法，更聚焦於架構決策。

In System Design Interviews and high-traffic production environments, "how to prevent data loss" and "how to ensure service continuity" are key differentiators between Senior and Staff engineers. This chapter focuses less on syntax and more on architectural decision-making.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準區分 HA 與 DR**：理解 High Availability (HA) 與 Disaster Recovery (DR) 的本質差異，並能根據 RPO (Recovery Point Objective) 與 RTO (Recovery Time Objective) 選擇正確的技術堆疊。
    **Distinguish between HA and DR**: Understand the fundamental differences between High Availability (HA) and Disaster Recovery (DR), and select the correct technology stack based on RPO and RTO.

2.  **掌握 AlwaysOn Availability Groups (AG)**：深入理解 AG 的運作原理（Synchronous vs. Asynchronous commit），以及如何利用它實現讀寫分離（Read-Scale Out）。
    **Master AlwaysOn Availability Groups (AG)**: Deeply understand how AG works (Synchronous vs. Asynchronous commit) and how to leverage it for Read-Scale Out.

3.  **評估架構取捨 (Trade-offs)**：在 Failover Cluster Instances (FCI)、AlwaysOn AG、Log Shipping 與 Replication 之間，針對成本、複雜度與資料一致性進行權衡。
    **Evaluate Architectural Trade-offs**: Weigh the costs, complexity, and data consistency among Failover Cluster Instances (FCI), AlwaysOn AG, Log Shipping, and Replication.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 HA vs. DR：備胎與保險 (Spare Tire vs. Insurance)

最直覺的類比是：**HA 是備胎，DR 是保險理賠。**
The most intuitive analogy is: **HA is a spare tire; DR is an insurance claim.**

-   **High Availability (HA)**：
    -   **目標 (Goal)**：自動化故障轉移，讓使用者幾乎感覺不到中斷。
        Automatic failover so users barely notice the interruption.
    -   **範圍 (Scope)**：通常在同一個資料中心或鄰近的 Availability Zone (AZ)。
        Usually within the same data center or adjacent Availability Zones (AZ).
    -   **關鍵技術 (Key Tech)**：AlwaysOn AG (Sync), FCI.

-   **Disaster Recovery (DR)**：
    -   **目標 (Goal)**：在災難（如地震、機房全毀）發生後，保全資料並在可接受時間內恢復服務。
        Preserve data and restore service within an acceptable time after a catastrophe (e.g., earthquake, total data center loss).
    -   **範圍 (Scope)**：跨地域 (Cross-Region)。
        Cross-Region.
    -   **關鍵技術 (Key Tech)**：AlwaysOn AG (Async), Log Shipping, Geo-Replication.

### 2.2 RPO 與 RTO (The Metrics that Matter)

在設計資料庫架構時，業務端必須定義這兩個指標：
When designing DB architecture, the business side must define these two metrics:

-   **RPO (Recovery Point Objective)**：你能容忍遺失多少資料？（例如：0 秒表示強一致性，15 分鐘表示可接受遺失 15 分鐘前的資料）。
    **RPO**: How much data loss can you tolerate? (e.g., 0 seconds implies strong consistency; 15 minutes means losing data from the last 15 minutes is acceptable).
-   **RTO (Recovery Time Objective)**：你能容忍服務停機多久？（例如：30 秒內自動切換，或 4 小時內手動復原）。
    **RTO**: How long can the service be down? (e.g., automatic failover within 30 seconds, or manual recovery within 4 hours).

### 2.3 AlwaysOn Availability Groups vs. Failover Cluster Instances (FCI)

這是 MS-SQL 中最容易混淆的兩個概念：
This is the most confusing comparison in MS-SQL:

| Feature | Failover Cluster Instances (FCI) | AlwaysOn Availability Groups (AG) |
| :--- | :--- | :--- |
| **Level** | **Instance Level** (整個 SQL Server 實體) | **Database Level** (可選定特定 DB 群組) |
| **Storage** | **Shared Storage** (SAN/SMB) - 單點故障風險 | **Shared Nothing** (各自擁有儲存) - 資料冗餘 |
| **Secondary** | 被動 (Passive)，無法讀取 | 可讀取 (Readable Secondary)，可用於備份 |
| **Cloud Fit** | 較難實作 (需特殊共享儲存服務) | 雲端原生友善 (Cloud-friendly) |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 典型的高可用架構 (Typical HA Architecture)

在現代的大型系統設計中，我們通常採用 **AlwaysOn Availability Groups** 搭配 **Listener**。
In modern large-scale system design, we typically use **AlwaysOn Availability Groups** paired with a **Listener**.

**架構圖概念 (Conceptual Architecture):**

```mermaid
[Application Layer]
       |
(Connect via Listener DNS)
       |
       v
[ Load Balancer / VIP ]
       |
   +---+---+
   |       |
[Primary] [Secondary]
 (R/W)     (Read-Only)
   |         |
[Storage] [Storage]
```

-   **Listener**：應用程式只需連線到一個虛擬 IP/DNS，不需要知道現在哪一台 Server 是 Primary。
    **Listener**: The application connects to a single Virtual IP/DNS and doesn't need to know which server is currently the Primary.
-   **Read-Only Routing**：透過設定 Application Intent = ReadOnly，連線字串可以自動被導向 Secondary Replica，減輕 Primary 的負載。
    **Read-Only Routing**: By setting Application Intent = ReadOnly, connection strings can be automatically routed to the Secondary Replica, offloading the Primary.

### 3.2 雲端環境的對應 (Cloud Mapping)

如果你使用雲端託管服務（如 AWS RDS for SQL Server 或 Azure SQL Database）：
If you use cloud managed services (like AWS RDS for SQL Server or Azure SQL Database):

-   **Multi-AZ (AWS) / Business Critical (Azure)**：背後通常就是實作了類似 AlwaysOn AG 的同步複製機制。
    **Multi-AZ (AWS) / Business Critical (Azure)**: Under the hood, they typically implement a synchronous replication mechanism similar to AlwaysOn AG.
-   **Read Replicas**：對應到 AlwaysOn 的 Async Secondary。
    **Read Replicas**: Corresponds to AlwaysOn Async Secondary.

### 3.3 對應用程式的影響 (Impact on Applications)

-   **Retry Logic (重試機制)**：Failover 發生時，現有的連線會斷開。應用程式必須具備 robust 的重試邏輯（Exponential Backoff）。
    **Retry Logic**: When failover occurs, existing connections drop. Applications must have robust retry logic (Exponential Backoff).
-   **Latency (延遲)**：若設定為 **Synchronous Commit**，每一筆 Write Transaction 都必須等 Secondary 確認寫入 Log 後才算完成。這會增加寫入延遲，需在設計時考量網路頻寬。
    **Latency**: If set to **Synchronous Commit**, every Write Transaction must wait for the Secondary to acknowledge the Log write. This adds write latency and requires network bandwidth consideration during design.

---

# 4. 逐步示例：設計金融級帳務系統 (Walkthrough: Designing a Financial Ledger System)

### 背景 (Context)
你需要為一個跨國銀行設計核心帳務資料庫。
**需求 (Requirements)**：
1.  **RPO = 0**：任何情況下不能遺失交易紀錄。
2.  **RTO < 1 min**：主機當機需在 1 分鐘內恢復。
3.  **DR**：若主機房遭遇地震，需在異地重啟服務（容許少量資料遺失或延遲）。

You need to design a core ledger database for a multinational bank.
**Requirements**:
1.  **RPO = 0**: Zero data loss under any circumstances.
2.  **RTO < 1 min**: Recover within 1 minute if the host crashes.
3.  **DR**: If the main data center is hit by an earthquake, restart service in a remote location (minor data loss or delay is acceptable).

### 演進步驟 (Evolution Steps)

#### Step 1: 選擇技術 (Selecting Technology)
由於需要 RPO = 0 且不依賴共享儲存（避免 SAN 單點故障），我們選擇 **AlwaysOn Availability Groups**。
Since we need RPO = 0 and want to avoid shared storage (to prevent SAN SPOF), we choose **AlwaysOn Availability Groups**.

#### Step 2: 定義拓撲 (Defining Topology)

我們設計一個 3-Node 架構：
We design a 3-Node architecture:

1.  **Node A (Primary, DC 1)**
2.  **Node B (Secondary, DC 1)**: 設定為 **Synchronous Commit** + **Automatic Failover**。
    Set to **Synchronous Commit** + **Automatic Failover**.
3.  **Node C (Secondary, DC 2 - DR Site)**: 設定為 **Asynchronous Commit** + **Manual Failover**。
    Set to **Asynchronous Commit** + **Manual Failover**.

#### Step 3: 實作細節與 T-SQL 邏輯 (Implementation Details)

雖不需手寫完整 DDL，但需理解關鍵設定：
While you don't need to write full DDL, understand the key settings:

```sql
-- 概念代碼 (Conceptual Code)
CREATE AVAILABILITY GROUP [AG_Financial_Ledger]
WITH (AUTOMATED_BACKUP_PREFERENCE = SECONDARY)
FOR DATABASE [LedgerDB]
REPLICA ON
N'NodeA' WITH (
    ENDPOINT_URL = 'TCP://NodeA:5022',
    AVAILABILITY_MODE = SYNCHRONOUS_COMMIT, -- 確保 RPO = 0 (Ensures RPO = 0)
    FAILOVER_MODE = AUTOMATIC               -- 確保 RTO < 1 min (Ensures RTO < 1 min)
),
N'NodeB' WITH (
    ENDPOINT_URL = 'TCP://NodeB:5022',
    AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
    FAILOVER_MODE = AUTOMATIC
),
N'NodeC' WITH (
    ENDPOINT_URL = 'TCP://NodeC:5022',
    AVAILABILITY_MODE = ASYNCHRONOUS_COMMIT, -- 避免跨地域延遲拖慢寫入 (Avoid cross-region latency slowing writes)
    FAILOVER_MODE = MANUAL
);
```

#### Step 4: 處理 Quorum (仲裁)
在 2 個節點的情況下，如果網路中斷（Split-brain），誰是老大？我們需要配置 **File Share Witness** 或 **Cloud Witness** 來確保 Cluster 的仲裁機制正常運作，避免雙主（Split-brain）導致資料損毀。
In a 2-node scenario, if the network cuts (Split-brain), who is the leader? We need to configure a **File Share Witness** or **Cloud Witness** to ensure the Cluster quorum works correctly, preventing Split-brain data corruption.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 誤用 Replication 作為 HA 方案 (Misusing Replication for HA)
-   **錯誤 (Pitfall)**：使用 Transactional Replication 來做高可用性切換。
    Using Transactional Replication for high availability failover.
-   **原因 (Why it's bad)**：Replication 的設計初衷是資料分發（Data Distribution），其 Schema 修改困難、故障轉移需大量手動介入、且容易因衝突而中斷。
    Replication is designed for Data Distribution. Schema changes are difficult, failover requires significant manual intervention, and it breaks easily due to conflicts.
-   **解法 (Solution)**：HA 請使用 AlwaysOn AG 或 FCI。

### 5.2 忽略 Log Growth (Ignoring Log Growth)
-   **錯誤 (Pitfall)**：Secondary 節點斷線或暫停同步，Primary 的 Transaction Log 無限增長，導致磁碟爆滿。
    Secondary node disconnects or pauses sync; Primary's Transaction Log grows indefinitely, filling the disk.
-   **原因 (Why it's bad)**：在 AG 中，Primary 的 Log 必須等到傳送至 Secondary 並硬碟落地後才能截斷（Truncate）。
    In AG, the Primary's Log cannot be truncated until it is shipped and hardened on the Secondary.
-   **解法 (Solution)**：設定監控警報，當 `log_reuse_wait_desc` 為 `AVAILABILITY_REPLICA` 時立即通知。

### 5.3 遺漏非資料庫物件 (Missing Non-Database Objects)
-   **錯誤 (Pitfall)**：Failover 後，應用程式報錯 "Login failed" 或 SQL Agent Job 沒跑。
    After failover, the app reports "Login failed" or SQL Agent Jobs don't run.
-   **原因 (Why it's bad)**：AlwaysOn AG 只複製 **User Databases**。Logins (Server level)、Jobs、Linked Servers 不會自動同步。
    AlwaysOn AG only replicates **User Databases**. Logins (Server level), Jobs, and Linked Servers do not sync automatically.
-   **解法 (Solution)**：使用 PowerShell 腳本或 Contained Database (部分解決 Login 問題) 來同步 Server Level Objects。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: "我們系統寫入量極大，開啟 Synchronous Commit 後效能下降明顯，如何解？"
**"Our system has heavy write volume. Performance dropped significantly after enabling Synchronous Commit. How to solve?"**

-   **高分回答要點 (Key Points)**：
    1.  **確認瓶頸**：是網路頻寬（Network Bandwidth）不足，還是 Secondary 的 IOPS 跟不上？
        **Identify Bottleneck**: Is it Network Bandwidth or Secondary IOPS?
    2.  **降級策略**：如果業務允許，改為 Asynchronous Commit（犧牲 RPO 換取效能）。
        **Downgrade Strategy**: If business permits, switch to Asynchronous Commit (trade RPO for performance).
    3.  **優化 Log**：檢查 Transaction Log 的寫入效率（VLF fragmentation, Disk speed）。
        **Optimize Log**: Check Transaction Log write efficiency.
    4.  **架構分離**：將讀取流量完全導向 Read-Only Replica，確保 Primary 專注於寫入。
        **Architecture Separation**: Route all read traffic to Read-Only Replicas so Primary focuses on writes.

### Q2: "AlwaysOn AG 與 Log Shipping 有什麼區別？為什麼現在還有人用 Log Shipping？"
**"What's the difference between AlwaysOn AG and Log Shipping? Why do people still use Log Shipping?"**

-   **高分回答要點 (Key Points)**：
    1.  **即時性**：AG 是 Transaction 層級（近乎即時）；Log Shipping 是 File 層級（依賴備份頻率，有延遲）。
        **Real-time**: AG is Transaction level (near real-time); Log Shipping is File level (depends on backup frequency, has lag).
    2.  **人為錯誤防護**：Log Shipping 可以設定「延遲還原」（Delayed Apply），例如延遲 2 小時。如果有人誤刪資料表 (DROP TABLE)，在 AG 會瞬間同步刪除，但在 Log Shipping 的備份端還有機會救回。
        **Human Error Protection**: Log Shipping can be set with "Delayed Apply" (e.g., 2 hours). If someone drops a table, AG syncs it instantly, but Log Shipping gives you a window to recover.
    3.  **成本與授權**：Log Shipping 支援 Standard Edition 且設定簡單，適合低成本 DR。
        **Cost & Licensing**: Log Shipping supports Standard Edition and is simple, suitable for low-cost DR.

### Q3: "如何實現 Zero Downtime Deployment (零停機部署) 的 Schema Change？"
**"How to achieve Zero Downtime Deployment for Schema Changes?"**

-   **高分回答要點 (Key Points)**：
    1.  **向後相容 (Backward Compatibility)**：新增欄位通常安全，刪除或改名欄位必須分階段（Expand and Contract pattern）。
        **Backward Compatibility**: Adding columns is usually safe; deleting/renaming requires phases (Expand and Contract pattern).
    2.  **AG 的角色**：雖然 AG 提供 HA，但 Schema Change 會同步鎖定。對於大表修改，可能需要使用 `ONLINE = ON` 選項。
        **Role of AG**: While AG provides HA, Schema Changes sync locks. Large table changes might need `ONLINE = ON`.
    3.  **進階技巧**：在極端要求下，可能需要打破 AG 同步，先升級 Secondary，Failover，再升級原 Primary（Rolling Upgrade），但这通常用於版本升級而非單純 Schema Change。
        **Advanced**: For extreme requirements, you might break AG sync, upgrade Secondary, Failover, then upgrade original Primary (Rolling Upgrade), usually for version upgrades rather than simple Schema Changes.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **HA $\neq$ DR**：HA 為了服務不中斷（Sync, Local），DR 為了災難復原（Async, Remote）。
2.  **RPO & RTO**：架構設計的依據。RPO=0 必選 Sync Commit。
3.  **AlwaysOn AG**：現代 MS-SQL 的首選 HA/DR 方案，支援讀寫分離與無共享儲存。
4.  **Quorum**：Cluster 存活的關鍵，務必配置 Witness。
5.  **Log Management**：AG 依賴 Log 傳輸，監控 Log Growth 至關重要。
6.  **Server Objects**：Login 與 Job 不會自動同步，需額外自動化處理。

### 後續延伸 (Next Steps)
-   **實作 (Practice)**：在 Docker 或雲端 VM 中搭建一個 2-Node AlwaysOn AG Cluster。
-   **進階閱讀 (Read)**：深入研究 **Distributed Availability Groups**，這是跨 OS (Windows to Linux) 或跨 Cluster 遷移與 DR 的進階技術。
-   **下一章預告 (Next Chapter)**：**Chapter 08: 鎖定、阻塞與死鎖分析 (Locking, Blocking & Deadlocks)** —— 當 HA 架構準備好後，如何解決內部的 Concurrency 問題。