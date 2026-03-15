# Chapter 10: High Availability and Disaster Recovery
# 第 10 章：高可用性架構與災難復原

## 1. Introduction and Learning Objectives
## 1. 前言與學習目標

For a Senior Software Engineer, managing GitLab goes beyond simple installation; it involves ensuring the platform remains resilient under load and recoverable after catastrophic failures. As the "heart" of the DevOps lifecycle, GitLab downtime halts CI/CD pipelines and development velocity. This chapter focuses on scaling GitLab horizontally (HA) and geographically (Geo), alongside robust backup strategies.
對於資深軟體工程師而言，管理 GitLab 不僅僅是安裝軟體，更在於確保平台在負載下保持彈性，並在災難性故障後能夠復原。作為 DevOps 生命週期的「心臟」，GitLab 的停機將導致 CI/CD 流程與開發速度停擺。本章將重點介紹如何水平擴展 GitLab（HA）與地理異地備援（Geo），以及穩健的備份策略。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Distinguish between HA and Geo:** Understand when to use High Availability (for uptime) versus GitLab Geo (for Disaster Recovery and read-scalability).
    **區分 HA 與 Geo：** 理解何時使用高可用性（為了正常運行時間）與 GitLab Geo（為了災難復原與讀取擴展）。
2.  **Architect for Resilience:** Design a GitLab architecture that eliminates Single Points of Failure (SPOF) using components like Gitaly Cluster, Redis Sentinel, and Patroni.
    **設計韌性架構：** 設計一個消除單點故障（SPOF）的 GitLab 架構，運用 Gitaly Cluster、Redis Sentinel 與 Patroni 等組件。
3.  **Implement Disaster Recovery (DR):** Define RPO (Recovery Point Objective) and RTO (Recovery Time Objective) strategies specific to GitLab, including the critical role of `gitlab-secrets.json`.
    **實作災難復原（DR）：** 定義針對 GitLab 的 RPO（復原點目標）與 RTO（復原時間目標）策略，包含 `gitlab-secrets.json` 的關鍵角色。
4.  **Monitor Health:** Utilize GitLab’s built-in Prometheus endpoints to monitor the "Golden Signals" of service health.
    **監控健康狀態：** 利用 GitLab 內建的 Prometheus 端點來監控服務健康的「黃金訊號」。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Mental Model: Franchise vs. HQ
### 2.1 心智模型：連鎖店 vs. 總部

Think of a standard GitLab instance as a **Single Headquarters**. If the HQ loses power, everyone stops working.
將標準的 GitLab 實例想像成**單一總部**。如果總部斷電，所有人都會停止工作。

*   **High Availability (HA)** is like adding backup generators, redundant internet lines, and multiple entrances to that *same* HQ building. It protects against component failures (e.g., a server crash) but not against the building burning down (e.g., data center outage).
    **高可用性（HA）** 就像是為這座*同一個*總部大樓增加備用發電機、冗餘網路線路和多個出入口。它能防止組件故障（如伺服器崩潰），但無法防止大樓燒毀（如資料中心中斷）。

*   **GitLab Geo** is like opening a **Franchise Branch** in another city. The branch receives inventory (code/data) from HQ continuously. If HQ disappears, the Branch can be promoted to become the new HQ. Additionally, local employees can pick up inventory from the Branch faster than driving to HQ.
    **GitLab Geo** 就像在另一個城市開設**加盟分店**。分店會持續從總部接收庫存（程式碼/資料）。如果總部消失，分店可以被升級為新總部。此外，當地員工從分店獲取庫存的速度比開車去總部更快。

### 2.2 Key Definitions
### 2.2 關鍵定義

*   **Gitaly Cluster (Praefect):**
    GitLab's solution for HA Git storage. Unlike NFS (which is deprecated/discouraged for performance), Praefect acts as a router and transaction manager to replicate Git data across multiple Gitaly nodes, ensuring strong consistency.
    GitLab 的 HA Git 儲存解決方案。不同於 NFS（因效能問題已被棄用/不建議使用），Praefect 充當路由器與交易管理器，將 Git 資料複製到多個 Gitaly 節點，確保強一致性。

*   **GitLab Geo:**
    A feature for **Disaster Recovery (DR)** and **Geographically Distributed Teams**. It creates read-only mirrors (Secondary sites) of the GitLab instance.
    **災難復原（DR）** 與 **地理分散團隊** 的功能。它會建立 GitLab 實例的唯讀鏡像（Secondary sites）。
    *   **Primary Site:** Read/Write.
    *   **Secondary Site:** Read-only (but supports "proxying" write requests to Primary). Accelerates `git clone`/`git pull`.

*   **Split Brain:**
    A state in a clustered environment where nodes lose connectivity and independently decide they are the "master," leading to data corruption. GitLab uses Consul and Patroni to manage leader election and prevent this.
    叢集環境中的一種狀態，節點失去連線並各自判定自己是「主節點」，導致資料損毀。GitLab 使用 Consul 與 Patroni 來管理領導者選舉並防止此情況。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production environment, specifically for organizations with 2,000+ users, a single-node installation (`omnibus-gitlab` on one VM) is insufficient. You must transition to a **Reference Architecture**.
在生產環境中，特別是針對 2,000 名以上使用者的組織，單節點安裝（單一 VM 上的 `omnibus-gitlab`）是不夠的。你必須轉移至**參考架構（Reference Architecture）**。

### 3.1 Architecture Components
### 3.1 架構組件

A robust GitLab HA design decouples stateful and stateless services:
一個穩健的 GitLab HA 設計會將有狀態（Stateful）與無狀態（Stateless）服務解耦：

1.  **Load Balancer (Stateless):** NGINX/HAProxy distributing traffic to Rails nodes.
    **負載平衡器（無狀態）：** NGINX/HAProxy 將流量分發至 Rails 節點。
2.  **Application Nodes (Stateless):** Running Puma (Web) and Sidekiq (Background Jobs). These can be scaled horizontally easily.
    **應用程式節點（無狀態）：** 運行 Puma（Web）與 Sidekiq（背景作業）。這些可以輕鬆地水平擴展。
3.  **PostgreSQL (Stateful):** Managed by **Patroni** for HA and automatic failover. This is the source of truth for metadata (users, issues, MRs).
    **PostgreSQL（有狀態）：** 由 **Patroni** 管理 HA 與自動故障轉移。這是元資料（使用者、議題、MR）的真理來源。
4.  **Redis (Stateful):** Used for caching and job queues. Requires **Redis Sentinel** for HA.
    **Redis（有狀態）：** 用於快取與作業佇列。需要 **Redis Sentinel** 來實現 HA。
5.  **Gitaly Cluster (Stateful):** Stores the actual `.git` data. This is often the bottleneck in monolithic setups.
    **Gitaly Cluster（有狀態）：** 儲存實際的 `.git` 資料。這通常是單體架構中的瓶頸。
6.  **Object Storage (Stateful):** S3/GCS/MinIO for artifacts, uploads, LFS, and container registry images.
    **物件儲存（有狀態）：** S3/GCS/MinIO 用於儲存產出物（artifacts）、上傳檔案、LFS 與容器儲存庫映像檔。

### 3.2 Impact on System Attributes
### 3.2 對系統屬性的影響

*   **Scalability:** You can scale Web/Sidekiq nodes independently based on CPU/Memory usage.
    **可擴充性：** 你可以根據 CPU/記憶體使用量獨立擴展 Web/Sidekiq 節點。
*   **Observability:** Distributed systems are harder to debug. Centralized logging (ELK/Splunk) and metrics (Prometheus/Grafana) become mandatory, not optional.
    **可觀測性：** 分散式系統較難除錯。集中式日誌（ELK/Splunk）與指標（Prometheus/Grafana）變成強制性需求，而非選配。
*   **Consistency:** Geo uses **PostgreSQL streaming replication** for database data and a specialized **Geo Log Cursor** to replay events for Git data and files.
    **一致性：** Geo 使用 **PostgreSQL 串流複製** 來處理資料庫資料，並使用專門的 **Geo Log Cursor** 來重播 Git 資料與檔案的事件。

---

## 4. Walkthrough: Configuring GitLab Geo
## 4. 逐步示例：設定 GitLab Geo

### Scenario
### 情境

Your company has a Primary site in **AWS us-east-1** and a large engineering team in **London**. The London team complains about slow `git clone` speeds (latency). Management also requires a Disaster Recovery (DR) site in a different region.
你的公司在 **AWS us-east-1** 有一個主站點（Primary），並且在 **倫敦** 有一個大型工程團隊。倫敦團隊抱怨 `git clone` 速度太慢（延遲）。管理層也要求在不同區域建立災難復原（DR）站點。

**Solution:** Implement GitLab Geo with a Secondary site in **AWS eu-west-2**.
**解決方案：** 在 **AWS eu-west-2** 建立一個 Secondary 站點來實作 GitLab Geo。

### Step 1: Prerequisites & Database Replication
### 步驟 1：先決條件與資料庫複製

Both sites must run the **exact same version** of GitLab. The Secondary site's database must be a read-replica of the Primary.
兩個站點必須運行**完全相同版本**的 GitLab。Secondary 站點的資料庫必須是 Primary 的唯讀複本（Read-replica）。

*On Primary (gitlab.rb):*
*在 Primary (gitlab.rb):*

```ruby
# /etc/gitlab/gitlab.rb
geo_primary_role['enable'] = true
postgresql['listen_address'] = '0.0.0.0' # Allow external connections
postgresql['sql_user_password'] = 'MD5_HASH_OF_PASSWORD'
postgresql['max_replication_slots'] = 10 # Reserve slots for secondaries
```

*On Secondary (gitlab.rb):*
*在 Secondary (gitlab.rb):*

```ruby
# /etc/gitlab/gitlab.rb
geo_secondary_role['enable'] = true
postgresql['enable'] = true
postgresql['sql_user_password'] = 'MD5_HASH_OF_PASSWORD'
# Configure connection to Primary DB
gitlab_rails['db_host'] = 'PRIMARY_DB_IP'
gitlab_rails['db_password'] = 'PLAINTEXT_PASSWORD'
```

### Step 2: Establish Trust (Secrets)
### 步驟 2：建立信任（Secrets）

This is the most critical step. The Secondary needs to decrypt data from the Primary. You must copy the `/etc/gitlab/gitlab-secrets.json` and SSH host keys from Primary to Secondary.
這是最關鍵的一步。Secondary 需要解密來自 Primary 的資料。你必須將 `/etc/gitlab/gitlab-secrets.json` 和 SSH 主機金鑰從 Primary 複製到 Secondary。

```bash
# On Secondary
# Backup original secrets
cp /etc/gitlab/gitlab-secrets.json /etc/gitlab/gitlab-secrets.json.bak

# Replace with Primary's secrets
scp user@primary_ip:/etc/gitlab/gitlab-secrets.json /etc/gitlab/
```

### Step 3: Add Secondary Site in UI
### 步驟 3：在 UI 中新增 Secondary 站點

1.  Go to **Admin Area > Geo > Sites**.
    前往 **Admin Area > Geo > Sites**。
2.  Add the Primary site (if not already there).
    新增 Primary 站點（若尚未存在）。
3.  Add the Secondary site using its internal URL and name.
    使用 Secondary 的內部 URL 與名稱來新增它。

### Step 4: Replication Verification
### 步驟 4：複製驗證

Once configured, the Secondary will start "backfilling" data.
設定完成後，Secondary 將開始「回填（backfilling）」資料。

*   **Database:** Replicates instantly via PostgreSQL streaming.
    **資料庫：** 透過 PostgreSQL 串流即時複製。
*   **Git Data:** The Geo Log Cursor on the Secondary watches for events and triggers synchronization.
    **Git 資料：** Secondary 上的 Geo Log Cursor 會監控事件並觸發同步。

You can monitor the status on the Geo Dashboard. It shows "Sync Status" for Repositories, LFS objects, and Uploads.
你可以在 Geo Dashboard 上監控狀態。它會顯示 Repositories、LFS 物件與上傳檔案的「同步狀態」。

### Step 5: Disaster Recovery (Failover)
### 步驟 5：災難復原（故障轉移）

If Primary fails:
如果 Primary 故障：

1.  **Assessment:** Verify Primary is truly down.
    **評估：** 確認 Primary 真的已當機。
2.  **Promotion:** Run the promotion command on the Secondary.
    **升級：** 在 Secondary 上執行升級指令。

```bash
# On Secondary Node
gitlab-ctl geo promote
```

This command promotes the read-only database to read-write and reconfigures the GitLab instance to accept write traffic.
此指令會將唯讀資料庫升級為讀寫模式，並重新設定 GitLab 實例以接受寫入流量。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "RAID is Backup" Fallacy
### 5.1 「RAID 即備份」的謬誤

*   **Anti-pattern:** Relying solely on HA (Gitaly Cluster, PostgreSQL HA) or disk redundancy (RAID/Snapshots) as a backup strategy.
    **反模式：** 僅依賴 HA（Gitaly Cluster、PostgreSQL HA）或磁碟冗餘（RAID/快照）作為備份策略。
*   **Why it's bad:** HA replicates *errors* instantly. If a user accidentally deletes a repository or a `DROP TABLE` command runs, that deletion is replicated to all nodes immediately.
    **為何不好：** HA 會即時複製*錯誤*。如果使用者不小心刪除了一個儲存庫或執行了 `DROP TABLE` 指令，該刪除操作會立即複製到所有節點。
*   **Solution:** You need **cold backups** (snapshots stored in S3/Tape) with a defined retention policy to restore from a point in time.
    **解決方案：** 你需要具有定義保留策略的 **冷備份（cold backups）**（儲存在 S3/磁帶中的快照），以便從特定時間點還原。

### 5.2 Losing `gitlab-secrets.json`
### 5.2 遺失 `gitlab-secrets.json`

*   **Anti-pattern:** Backing up the database (`dump.sql`) but forgetting the secrets file.
    **反模式：** 備份了資料庫（`dump.sql`）卻忘記備份 secrets 檔案。
*   **Why it's bad:** GitLab encrypts sensitive data (CI variables, 2FA secrets, integration tokens) in the DB using keys in this file. Without it, your restored DB is useless; you cannot decrypt anything.
    **為何不好：** GitLab 使用此檔案中的金鑰將敏感資料（CI 變數、2FA 密鑰、整合權杖）加密儲存在資料庫中。沒有它，還原後的資料庫毫無用處；你無法解密任何內容。
*   **Solution:** Treat `gitlab-secrets.json` as the most critical asset. Back it up securely and separately.
    **解決方案：** 將 `gitlab-secrets.json` 視為最關鍵的資產。安全且分開地備份它。

### 5.3 NFS for Gitaly
### 5.3 使用 NFS 作為 Gitaly 儲存

*   **Anti-pattern:** Mounting NFS shares for Gitaly storage in high-traffic environments.
    **反模式：** 在高流量環境中掛載 NFS 分享區作為 Gitaly 儲存。
*   **Why it's bad:** Git operations are I/O intensive and metadata-heavy. NFS introduces latency (network round-trips) that causes high CPU wait times and "slower than local" performance.
    **為何不好：** Git 操作是 I/O 密集且元資料繁重的。NFS 會引入延遲（網路往返），導致高 CPU 等待時間以及「比本機慢」的效能。
*   **Solution:** Use **Gitaly Cluster** (Praefect) or block storage (EBS/Persistent Disk) directly attached to Gitaly nodes.
    **解決方案：** 使用 **Gitaly Cluster** (Praefect) 或直接掛載在 Gitaly 節點上的區塊儲存（EBS/Persistent Disk）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a Zero-Downtime Upgrade strategy for a GitLab instance serving 5,000 users?
### Q1: 你會如何為服務 5,000 名使用者的 GitLab 實例設計零停機升級（Zero-Downtime Upgrade）策略？

*   **Key Points to Cover:**
    *   **Architecture:** Must be a multi-node setup (Reference Architecture).
    *   **Process:** Upgrade one node at a time (Rolling Update).
    *   **Database:** Mention "Post-deployment migrations". GitLab separates migrations into regular (safe to run while old code is running) and post-deployment (run after all nodes are upgraded).
    *   **Load Balancer:** Remove the node from the LB pool before upgrading, then add it back.
    *   **Gitaly:** Praefect handles Gitaly node upgrades without downtime if replication factor >= 2.

### Q2: Explain the difference between RPO and RTO in the context of GitLab Geo.
### Q2: 請在 GitLab Geo 的情境下解釋 RPO 與 RTO 的差異。

*   **Key Points to Cover:**
    *   **RPO (Recovery Point Objective):** How much data can we afford to lose? With Geo, RPO is determined by **replication lag**. If the DB lag is 100MB or 1 minute, failing over means losing that last minute of data.
    *   **RTO (Recovery Time Objective):** How long does it take to get back online? Geo minimizes RTO to minutes (time to run `gitlab-ctl geo promote` and switch DNS). Restoring from cold backup takes hours (high RTO).

### Q3: We are seeing intermittent 500 errors on GitLab. How do you debug?
### Q3: 我們在 GitLab 上看到間歇性的 500 錯誤。你會如何除錯？

*   **Key Points to Cover:**
    *   **Logs:** Check `production_json.log` (Rails) and `api_json.log`. Look for `correlation_id` to trace requests across services.
    *   **Metrics:** Check Prometheus/Grafana. Look for spikes in CPU, Memory, or DB connection pool saturation.
    *   **Gitaly:** Check `gitaly_json.log`. Is a specific shard or node slow?
    *   **Architecture:** Is it a "Noisy Neighbor" problem? (e.g., one CI runner consuming all resources).

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **HA != DR:** High Availability keeps you running if a server fails; Disaster Recovery (Geo) saves you if the data center fails.
    **HA != DR：** 高可用性讓你在伺服器故障時持續運作；災難復原（Geo）則在資料中心故障時拯救你。
2.  **State is Hard:** Scaling stateless web nodes is easy. Scaling stateful components (PostgreSQL, Redis, Gitaly) requires specialized tools (Patroni, Sentinel, Praefect).
    **狀態處理很難：** 擴展無狀態 Web 節點很容易。擴展有狀態組件（PostgreSQL、Redis、Gitaly）需要專門的工具（Patroni、Sentinel、Praefect）。
3.  **Secrets are Vital:** Never lose `gitlab-secrets.json`. It is the key to your data kingdom.
    **Secrets 至關重要：** 絕不要遺失 `gitlab-secrets.json`。它是你資料王國的鑰匙。
4.  **Geo Mechanics:** Geo uses DB streaming replication + a Log Cursor to synchronize data. It enables read-only scaling and DR.
    **Geo 機制：** Geo 使用資料庫串流複製 + Log Cursor 來同步資料。它實現了唯讀擴展與 DR。
5.  **Observability:** Use the `correlation_id` in logs to trace requests across the distributed architecture.
    **可觀測性：** 使用日誌中的 `correlation_id` 來追蹤跨分散式架構的請求。

### Next Steps
### 後續延伸

*   **Practice:** Set up a local GitLab Geo instance using two VMs (or Docker Compose mimicking two sites). Try to "break" the primary and promote the secondary.
    **實作：** 使用兩個 VM（或模擬兩個站點的 Docker Compose）建立本地 GitLab Geo 實例。嘗試「弄壞」Primary 並升級 Secondary。
*   **Deep Dive:** Explore **GitLab Performance Tool (GPT)** to load test your architecture.
    **深入研究：** 探索 **GitLab Performance Tool (GPT)** 來對你的架構進行負載測試。
*   **Next Chapter:** Move on to **Security & Compliance** (DevSecOps), learning how to secure the pipeline and manage vulnerabilities at scale.
    **下一章：** 進入 **安全性與合規性**（DevSecOps），學習如何保護管線並大規模管理漏洞。