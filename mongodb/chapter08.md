# Chapter 08: Production Operations and Security
# 第 08 章：生產環境維運與安全性

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In the previous chapters, we focused on schema design, indexing, and aggregation. However, for a Senior Engineer, the job isn't done until the system is secure, observable, and recoverable in production. This chapter shifts focus from "Development" to "Day 2 Operations."
在前幾章中，我們專注於 Schema 設計、索引與聚合查詢。然而，對於資深工程師而言，直到系統在生產環境中具備安全性、可觀測性與可恢復性之前，工作都不算完成。本章將焦點從「開發」轉移至「Day 2 維運」。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Design a Robust Backup Strategy**: Understand the difference between snapshots and oplog-based backups to achieve Point-in-Time Recovery (PITR).
    **設計穩健的備份策略**：理解快照（Snapshot）與基於 Oplog 的備份之間的差異，以實現時間點恢復（PITR）。
2.  **Implement Defense-in-Depth Security**: Configure Network Security (TLS/SSL), Authentication (SCRAM/x.509), and Authorization (RBAC) correctly.
    **實作縱深防禦安全性**：正確配置網路安全（TLS/SSL）、身分驗證（SCRAM/x.509）與授權（RBAC）。
3.  **Master Observability**: Identify key metrics (Tickets, Replication Lag, Oplog Window) that indicate system health beyond simple CPU/RAM usage.
    **掌握可觀測性**：識別關鍵指標（Tickets、Replication Lag、Oplog Window），這些指標比單純的 CPU/RAM 使用率更能反映系統健康狀況。
4.  **Handle Data Encryption**: Explain and implement Encryption at Rest and Client-Side Field Level Encryption (CSFLE) for compliance.
    **處理資料加密**：解釋並實作靜態資料加密（Encryption at Rest）與用戶端欄位級加密（CSFLE）以符合合規需求。

---

## 2. Core Concepts & Mental Models
## 2. 核心觀念與心智模型

### 2.1 The "Defense in Depth" Model
### 2.1 「縱深防禦」模型

Security in MongoDB should be visualized as concentric circles. The outer layer is the **Network** (Firewalls, VPC Peering), the middle layer is **Access Control** (Authentication/Authorization), and the inner layer is **Data Protection** (Encryption).
MongoDB 的安全性應被視覺化為同心圓。外層是**網路**（防火牆、VPC Peering），中層是**存取控制**（身分驗證/授權），內層是**資料保護**（加密）。

*   **Network**: Allow access only from trusted application servers (IP Whitelisting).
    **網路**：僅允許來自受信任應用程式伺服器的存取（IP 白名單）。
*   **Transport**: TLS/SSL is mandatory. No data should travel in plain text.
    **傳輸**：TLS/SSL 是強制性的。任何資料都不應以明文傳輸。
*   **RBAC (Role-Based Access Control)**: Apply the Principle of Least Privilege. An analytics service should not have `write` access to user profiles.
    **RBAC（基於角色的存取控制）**：應用「最小權限原則」。分析服務不應對使用者設定檔擁有 `write` 權限。

### 2.2 Oplog as the Source of Truth for Recovery
### 2.2 Oplog 作為復原的真實來源

For backups, treat the **Oplog (Operations Log)** as a continuous stream of events. A file system snapshot gives you the state at `T0`. The Oplog allows you to replay changes from `T0` to `T1`.
在備份方面，請將 **Oplog（操作日誌）** 視為連續的事件流。檔案系統快照提供 `T0` 時刻的狀態。Oplog 則允許你重播從 `T0` 到 `T1` 的變更。

*   **RPO (Recovery Point Objective)**: How much data can you lose? With continuous oplog backups, RPO can be near-zero.
    **RPO（復原點目標）**：你能容忍遺失多少資料？透過連續的 Oplog 備份，RPO 可以接近零。
*   **RTO (Recovery Time Objective)**: How fast can you restore? Restoring a 1TB snapshot is faster than replaying 1TB of oplogs. A hybrid approach is best.
    **RTO（復原時間目標）**：你能多快完成復原？還原 1TB 的快照比重播 1TB 的 Oplog 快。混合方法通常是最佳解。

### 2.3 Key Metrics: The "Glass Box"
### 2.3 關鍵指標：「透明箱」

Don't treat MongoDB as a black box. The internal storage engine (WiredTiger) exposes critical metrics via `serverStatus`.
不要將 MongoDB 視為黑箱。內部的儲存引擎（WiredTiger）透過 `serverStatus` 暴露了關鍵指標。

*   **WiredTiger Tickets**: Think of these as "concurrency tokens". If read/write tickets drop to zero, the database is queuing requests, causing latency spikes.
    **WiredTiger Tickets**：將其視為「並發令牌」。如果讀/寫 Tickets 降至零，資料庫就會開始排隊請求，導致延遲飆升。
*   **Oplog Window**: The time difference between the oldest and newest entry in the oplog. If this is shorter than your backup frequency or maintenance downtime, you lose sync capability.
    **Oplog Window**：Oplog 中最舊與最新條目的時間差。如果此時間短於你的備份頻率或維護停機時間，你將失去同步能力。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Architecture for High Compliance
### 3.1 高合規性架構

In a Fintech or Healthcare system design interview, simply saying "we use a database" is insufficient. You must specify the security posture.
在金融科技或醫療保健系統設計面試中，僅說「我們使用資料庫」是不夠的。你必須明確說明安全態勢。

**Typical Setup:**
**典型設置：**

1.  **Isolation**: MongoDB runs in a private subnet. No public IP.
    **隔離**：MongoDB 運行於私有子網（Private Subnet）。無公網 IP。
2.  **Access**: Application servers connect via PrivateLink or VPC Peering.
    **存取**：應用程式伺服器透過 PrivateLink 或 VPC Peering 連線。
3.  **Encryption**:
    **加密**：
    *   **At Rest**: Disk volume encryption (e.g., AWS EBS encryption) + WiredTiger encryption (using KMIP).
        **靜態**：磁碟區加密（如 AWS EBS 加密）+ WiredTiger 加密（使用 KMIP）。
    *   **In Transit**: TLS 1.2+.
        **傳輸中**：TLS 1.2+。
    *   **Field Level**: PII (Personally Identifiable Information) like SSN or Credit Card numbers are encrypted by the *client driver* before sending to DB (CSFLE). Even the DBA cannot read them.
        **欄位級**：PII（個人識別資訊）如身分證號或信用卡號，在傳送至 DB 前由**用戶端驅動程式**加密（CSFLE）。即便是 DBA 也無法讀取。

### 3.2 Backup Strategy in Production
### 3.2 生產環境備份策略

For a high-traffic system (e.g., 10k writes/sec), `mongodump` is rarely sufficient because it impacts performance and lacks consistency without locking.
對於高流量系統（例如每秒 1 萬次寫入），`mongodump` 通常不足以應付，因為它會影響效能，且若不鎖定資料庫則缺乏一致性。

**Preferred Strategy:**
**首選策略：**

*   **Filesystem Snapshots (LVM / EBS Snapshots)**: Take a snapshot of the underlying storage. It's fast and creates a consistent image if journaling is on.
    **檔案系統快照（LVM / EBS Snapshots）**：對底層儲存進行快照。若開啟了 journaling，這種方式既快又能產生一致的映像檔。
*   **Secondary Node Backup**: Perform backups on a hidden secondary node to avoid impacting the primary's performance.
    **次要節點備份**：在隱藏的次要節點（Hidden Secondary）上執行備份，以避免影響主節點（Primary）的效能。

---

## 4. Walkthrough: Securing and Monitoring a Cluster
## 4. 逐步示例：叢集安全化與監控

### Scenario
### 情境

You are inheriting a legacy MongoDB instance that was set up with default settings. Your task is to secure it and enable proper profiling without killing performance.
你接手了一個使用預設設定建立的舊 MongoDB 實例。你的任務是將其安全化，並在不扼殺效能的前提下啟用適當的分析（Profiling）。

### Step 1: Enabling Access Control (RBAC)
### 步驟 1：啟用存取控制（RBAC）

First, create the administrator before enabling auth.
首先，在啟用驗證前建立管理員。

```javascript
// Connect to the admin database
use admin

// Create a superuser (Do this only once)
db.createUser({
  user: "siteRootAdmin",
  pwd: passwordPrompt(), // Securely prompt for password
  roles: [ { role: "root", db: "admin" } ]
})
```

Next, create a service user with least privilege for your application.
接著，為你的應用程式建立一個具備最小權限的服務使用者。

```javascript
use ecommerce_db

db.createUser({
  user: "app_service",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "ecommerce_db" },
    // Only allow index creation if strictly necessary, otherwise handle via migration scripts
    // 僅在絕對必要時允許建立索引，否則應透過遷移腳本處理
  ]
})
```

### Step 2: Configuration Hardening (`mongod.conf`)
### 步驟 2：配置強化（`mongod.conf`）

Modify the configuration file to enforce security and bind to private interfaces.
修改設定檔以強制執行安全性並綁定至私有介面。

```yaml
net:
  port: 27017
  bindIp: 10.0.1.5,127.0.0.1  # Bind to private IP only, never 0.0.0.0
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem

security:
  authorization: enabled
  # keyFile is required for replica set authentication
  # keyFile 是複本集內部驗證所必需的
  keyFile: /etc/mongodb/keyfile 

operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100 # Log operations slower than 100ms
  rateLimit: 100         # (Optional) Sample 100% of slow ops, avoid log spam if system is overloaded
```

### Step 3: Monitoring Critical Metrics
### 步驟 3：監控關鍵指標

In production, you would use tools like Datadog or MongoDB Atlas Charts. Here is how you check the "Tickets" manually via shell, which reflects the load on the storage engine.
在生產環境中，你會使用 Datadog 或 MongoDB Atlas Charts 等工具。以下是如何透過 Shell 手動檢查「Tickets」，這反映了儲存引擎的負載。

```javascript
// Check WiredTiger status
var status = db.serverStatus().wiredTiger

// Concurrent Read/Write Tickets
print("Read Tickets Available: " + status.concurrentTransactions.read.available)
print("Write Tickets Available: " + status.concurrentTransactions.write.available)

// If 'available' is near 0, the DB is saturated.
// 如果 'available' 接近 0，表示資料庫已飽和。
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Root" Application User
### 5.1 「Root」權限的應用程式使用者

*   **Bad Pattern**: Using the `root` or `dbAdmin` role for the backend application connection string.
    **不良模式**：在後端應用程式連線字串中使用 `root` 或 `dbAdmin` 角色。
*   **Why**: If the application is compromised (e.g., SQL/NoSQL Injection), the attacker can drop databases, wipe users, or access other tenants' data.
    **原因**：如果應用程式遭入侵（例如 SQL/NoSQL 資料隱碼攻擊），攻擊者可以刪除資料庫、清除使用者或存取其他租戶的資料。
*   **Solution**: Create custom roles that strictly limit actions (e.g., `find`, `insert`, `update` only).
    **解法**：建立嚴格限制動作的自訂角色（例如僅限 `find`、`insert`、`update`）。

### 5.2 Ignoring the Oplog Window Size
### 5.2 忽視 Oplog Window 大小

*   **Bad Pattern**: Keeping the default oplog size (usually 5% of disk) without monitoring the time window.
    **不良模式**：保持預設的 Oplog 大小（通常是磁碟的 5%）而不監控時間視窗。
*   **Why**: If you have a massive data import or update job, the oplog can rotate faster than your secondary nodes can replicate. This causes secondaries to fall into "RECOVERING" state and requires a full initial sync (painful for large DBs).
    **原因**：如果你有大量的資料匯入或更新作業，Oplog 的輪替速度可能快於次要節點的複製速度。這會導致次要節點進入「RECOVERING」狀態，並需要執行完整的初始同步（對大型 DB 來說非常痛苦）。
*   **Solution**: Monitor `rs.printReplicationInfo()` and ensure the window covers at least 24 hours or your longest maintenance window.
    **解法**：監控 `rs.printReplicationInfo()` 並確保視窗至少涵蓋 24 小時或你最長的維護視窗。

### 5.3 Backups on the Same Disk
### 5.3 備份在同一顆磁碟上

*   **Bad Pattern**: Running `mongodump` and saving the output to the same EBS volume where `/data/db` resides.
    **不良模式**：執行 `mongodump` 並將輸出儲存在與 `/data/db` 相同的 EBS 卷上。
*   **Why**: If the volume fails or gets corrupted, you lose both the live data and the backup.
    **原因**：如果該磁碟卷故障或損壞，你會同時失去即時資料與備份。
*   **Solution**: Stream backups to S3/GCS or use snapshot services that store data independently.
    **解法**：將備份串流至 S3/GCS，或使用獨立儲存資料的快照服務。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you handle a situation where a developer accidentally dropped a critical collection in Production 1 hour ago?
### Q1: 你會如何處理開發人員在 1 小時前不小心在生產環境刪除了一個關鍵 Collection 的情況？

*   **Key Points**:
    *   **Detection**: Acknowledge the incident.
    *   **Stop the Bleeding**: Ensure no further automated scripts are running that might depend on that data.
    *   **Point-in-Time Recovery (PITR)**: Explain that standard snapshots are too old (maybe last night). You need to restore the last snapshot + replay Oplog up to `timestamp = crash_time - 1 second`.
    *   **Process**: Restore to a *new* temporary cluster, verify data, then export/import the missing collection back to prod (or switch traffic if full DB restore is faster/safer).
    *   **Prevention**: Discuss `delayed` replica set members (e.g., a node that is always 1 hour behind) as a safety net.

### Q2: We are seeing occasional timeouts in our application, but CPU and RAM on MongoDB are fine. What could be the cause?
### Q2: 我們的應用程式偶爾會出現逾時，但 MongoDB 的 CPU 和 RAM 都很正常。原因可能是什麼？

*   **Key Points**:
    *   **I/O Wait**: Check disk IOPS and throughput limits (e.g., AWS GP2/GP3 bursting credits exhausted).
    *   **WiredTiger Tickets**: Check if read/write tickets are exhausted due to concurrency contention.
    *   **Locking**: Is there a specific collection lock or document locking issue?
    *   **Network**: Is there packet loss or bandwidth saturation?
    *   **Connection Pool**: Is the application opening too many connections (connection storm) or blocking on a full pool?

### Q3: How do we ensure GDPR compliance for user data in MongoDB?
### Q3: 我們如何確保 MongoDB 中的使用者資料符合 GDPR 規範？

*   **Key Points**:
    *   **Encryption at Rest**: Basic requirement.
    *   **Right to be Forgotten**: Design schema so user data is isolated or easily deletable.
    *   **CSFLE (Client-Side Field Level Encryption)**: This is the "High Score" answer. Encrypt sensitive fields (email, phone) with a key specific to the user (or a master key). If you delete the key, the data becomes "crypto-shredded" (unreadable), effectively fulfilling the deletion request without scrubbing backups.
    *   **Audit Logs**: Enable auditing to track who accessed PII data.

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Security is layered**: Network (VPC/TLS) -> Auth (RBAC) -> Data (Encryption).
    **安全性是分層的**：網路（VPC/TLS） -> 驗證（RBAC） -> 資料（加密）。
2.  **Backups need Oplogs**: Snapshots provide the base; Oplogs provide the precision for Point-in-Time Recovery.
    **備份需要 Oplog**：快照提供基礎；Oplog 提供時間點恢復的精確度。
3.  **Monitor "Tickets"**: CPU is not the only metric. WiredTiger tickets and Replication Lag are critical health indicators.
    **監控 "Tickets"**：CPU 不是唯一指標。WiredTiger tickets 與 Replication Lag 是關鍵的健康指標。
4.  **Least Privilege**: Never use root for applications. Use custom roles.
    **最小權限**：絕不要讓應用程式使用 root。請使用自訂角色。
5.  **Oplog Window**: Ensure your replication window is large enough to handle maintenance and traffic spikes.
    **Oplog Window**：確保你的複製視窗夠大，足以應付維護與流量高峰。

### Next Steps
### 後續延伸

Now that your production environment is secure and observable, the next challenge is scaling beyond a single replica set.
既然你的生產環境已經安全且可觀測，下一個挑戰就是擴展到單一複本集之外。

*   **Next Chapter**: `chapter09` - **Sharding Strategies and Architecture** (分片策略與架構).
*   **Action Item**: Check the `oplogSizeMB` and current window on your production database using `rs.printReplicationInfo()`.
    **行動項目**：使用 `rs.printReplicationInfo()` 檢查你生產環境資料庫的 `oplogSizeMB` 與當前視窗大小。