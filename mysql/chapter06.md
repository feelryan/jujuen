# 1. 前言與學習目標 (Introduction & Learning Objectives)

在高併發與高可靠性的系統設計中，資料庫往往是最後一道防線，也是最難擴展的瓶頸。對於資深工程師而言，僅僅會設定 Master-Slave 是不夠的；你需要深刻理解複製機制背後的原理，以便在「資料一致性（Consistency）」與「寫入效能（Write Latency）」之間做出正確的權衡。

In high-concurrency and high-reliability system design, the database is often the last line of defense and the hardest bottleneck to scale. For a Senior Engineer, simply knowing how to configure Master-Slave is insufficient; you need a deep understanding of the underlying replication mechanisms to make the right trade-offs between "Data Consistency" and "Write Latency."

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深度解析 Binlog**：理解 Row、Statement 與 Mixed 格式的差異，並知道為何現代架構首選 Row-based replication。
    **Deep Dive into Binlog**: Understand the differences between Row, Statement, and Mixed formats, and know why Row-based replication is the preferred choice for modern architectures.
2.  **掌握 GTID 與 Failover**：解釋 GTID 如何解決傳統基於檔案位置（File Position）複製的痛點，並設計自動化主從切換流程。
    **Master GTID and Failover**: Explain how GTID solves the pain points of traditional file-position-based replication and design automated failover workflows.
3.  **權衡同步機制**：分析非同步複製（Async）與半同步複製（Semi-sync）對 RPO（Recovery Point Objective）與寫入延遲的影響。
    **Trade-off Synchronization Mechanisms**: Analyze the impact of Asynchronous (Async) vs. Semi-synchronous (Semi-sync) replication on RPO (Recovery Point Objective) and write latency.
4.  **解決讀寫分離延遲**：在系統設計面試或實務中，針對「複製延遲（Replication Lag）」提出具體的應用層解決方案。
    **Solve Read-Write Splitting Lag**: Propose concrete application-layer solutions for "Replication Lag" in system design interviews or production environments.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Binlog 的本質 (The Essence of Binlog)

**心智模型**：將 Binlog 視為資料庫的「狀態變更日誌流（Stream of State Changes）」。Slave 並不是在「複製資料表」，而是在「重播（Replay）」Master 發生過的事件。

**Mental Model**: Think of the Binlog as the database's "Stream of State Changes." The Slave is not "copying tables"; it is "replaying" events that occurred on the Master.

MySQL 提供了三種 Binlog 格式，這決定了「事件」如何被記錄：
MySQL provides three Binlog formats, which dictate how "events" are recorded:

| Format | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Statement** | 記錄執行的 SQL 語句 (e.g., `DELETE FROM users WHERE age > 10`)。<br>Logs the executed SQL statements. | Log 檔案極小，節省 I/O。<br>Logs are very small, saving I/O. | **不安全**。若 SQL 包含非確定性函數 (如 `NOW()`, `UUID()`)，主從資料會不一致。<br>**Unsafe**. Data inconsistency occurs if SQL contains non-deterministic functions. |
| **Row** | 記錄每一行資料變更後的具體內容。<br>Logs the specific content of each row after change. | **資料一致性最強**。Slave 不需要重新計算 SQL 邏輯。<br>**Strongest consistency**. Slave doesn't need to recompute SQL logic. | Log 檔案可能很大 (例如 `UPDATE` 全表時，每一行都會產生一條 log)。<br>Logs can be huge (e.g., a full-table `UPDATE` generates a log entry for every row). |
| **Mixed** | 預設使用 Statement，遇到非確定性語句自動切換為 Row。<br>Defaults to Statement, switches to Row for non-deterministic queries. | 折衷方案。<br>A compromise. | 增加了複雜度，除錯較難。<br>Increases complexity, harder to debug. |

> **Senior Tip**: 在現代 Big Tech 環境中，**`binlog_format = ROW`** 是標準配置。因為它不僅保證一致性，還能支援下游的 CDC (Change Data Capture) 工具（如 Debezium）進行資料同步。
> **Senior Tip**: In modern Big Tech environments, **`binlog_format = ROW`** is the standard configuration. It not only ensures consistency but also supports downstream CDC (Change Data Capture) tools (like Debezium) for data synchronization.

## 2.2 GTID (Global Transaction ID)

傳統複製依賴 `binlog_file` 和 `binlog_position`，這在 Failover 時極其脆弱（很難精確找出 Slave A 執行到了 Master 的哪個 byte）。

Traditional replication relies on `binlog_file` and `binlog_position`, which is extremely fragile during Failover (it's hard to pinpoint exactly which byte of the Master that Slave A has executed).

GTID 為每個交易賦予全域唯一 ID：`GTID = source_id:transaction_id`。
GTID assigns a globally unique ID to each transaction: `GTID = source_id:transaction_id`.

*   **自動定位 (Auto-positioning)**：Slave 告訴 Master：「我已經執行過這些 GTID，請把剩下的傳給我。」
    **Auto-positioning**: The Slave tells the Master: "I have executed these GTIDs; please send me the rest."
*   **拓撲變更 (Topology Change)**：當 Master 當機，選出新的 Master 後，其他 Slaves 可以無縫切換到新 Master，因為 GTID 在叢集中是通用的。
    **Topology Change**: When the Master crashes and a new Master is elected, other Slaves can seamlessly switch to the new Master because GTIDs are universal across the cluster.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計（System Design）中，MySQL 的複製機制直接影響系統的**可用性 (Availability)** 與 **一致性 (Consistency)**。

In System Design, MySQL's replication mechanism directly impacts the system's **Availability** and **Consistency**.

## 3.1 非同步 vs. 半同步複製 (Async vs. Semi-Sync Replication)

這是面試中關於「資料遺失風險」的關鍵討論點。
This is a key discussion point in interviews regarding "data loss risk."

1.  **Asynchronous Replication (Default)**:
    *   Master 寫入 Binlog 後立即 commit，不等待 Slave。
    *   **Risk**: Master 當機時，尚未傳輸到 Slave 的 Binlog 會遺失 (RPO > 0)。
    *   **Use Case**: 日誌記錄、非核心業務數據。

    *   Master writes to Binlog and commits immediately without waiting for Slave.
    *   **Risk**: If Master crashes, Binlogs not yet transmitted to Slave are lost (RPO > 0).
    *   **Use Case**: Logging, non-core business data.

2.  **Semi-Synchronous Replication**:
    *   Master 寫入 Binlog 後，需等待**至少一個** Slave 收到並寫入 Relay Log (ACK) 後才 commit。
    *   **Trade-off**: 犧牲部分寫入效能（增加網路 RTT），換取更高的資料安全性。
    *   **Use Case**: 支付系統、訂單系統、金融交易。

    *   After writing to Binlog, Master waits for **at least one** Slave to receive and write to Relay Log (ACK) before committing.
    *   **Trade-off**: Sacrifices some write performance (adds network RTT) in exchange for higher data safety.
    *   **Use Case**: Payment systems, order systems, financial transactions.

## 3.2 讀寫分離與過期讀 (Read-Write Splitting & Stale Reads)

在 "Read-Heavy" 的系統中，我們通常會將讀流量導向 Slaves。這引入了著名的 **Replication Lag** 問題。

In "Read-Heavy" systems, we typically direct read traffic to Slaves. This introduces the famous **Replication Lag** problem.

*   **場景 (Scenario)**: 使用者更新個人資料 (Write to Master) -> 立即重新整理頁面 (Read from Slave) -> 看到舊資料。
    **Scenario**: User updates profile (Write to Master) -> Immediately refreshes page (Read from Slave) -> Sees old data.
*   **解決方案 (Solutions)**:
    1.  **強制讀主 (Read from Master)**: 對於關鍵資料（如剛寫入後的讀取），強制路由到 Master。
    2.  **快取標記 (Cache Marker)**: 寫入後在 Redis 設一個 key，讀取時若 key 存在則走 Master。
    3.  **GTID Tracking**: 應用層記錄寫入時的 GTID，讀取時要求 Slave 必須已執行該 GTID（需 Middleware 支援）。

    1.  **Read from Master**: For critical data (e.g., read-after-write), forcibly route to Master.
    2.  **Cache Marker**: Set a key in Redis after write; if key exists during read, route to Master.
    3.  **GTID Tracking**: Application records the GTID at write time; requires the Slave to have executed that GTID before serving the read (requires Middleware support).

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：配置高可靠的半同步複製 (Configuring High-Reliability Semi-Sync)

假設我們正在為一個金融交易系統配置 MySQL，目標是 RPO 趨近於 0。

Suppose we are configuring MySQL for a financial transaction system, aiming for an RPO close to 0.

### Step 1: 啟用 GTID (Enable GTID)

在 `my.cnf` 中配置：
Configure in `my.cnf`:

```ini
[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON
log_bin = mysql-bin
binlog_format = ROW
server_id = 1  # Unique for each node
```

### Step 2: 配置半同步複製 (Configure Semi-Sync)

我們需要安裝 plugin 並啟用參數。
We need to install the plugins and enable parameters.

```sql
-- On Master
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = 1;
SET GLOBAL rpl_semi_sync_master_timeout = 1000; -- 1000ms timeout

-- On Slave
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';
SET GLOBAL rpl_semi_sync_slave_enabled = 1;
```

### Step 3: 關鍵參數 `rpl_semi_sync_master_wait_point`

這是資深工程師必須注意的細節。MySQL 5.7+ 提供了兩種等待點：
This is a detail Senior Engineers must note. MySQL 5.7+ offers two wait points:

1.  **AFTER_SYNC (Recommended)**:
    *   流程：Write Binlog -> **Wait for Slave ACK** -> Commit to Storage Engine -> Return to Client.
    *   優點：若 Master 在等待 ACK 時當機，交易尚未 Commit，Client 收到失敗，Slave 也沒有資料。**資料絕對一致**。
    *   Flow: Write Binlog -> **Wait for Slave ACK** -> Commit to Storage Engine -> Return to Client.
    *   Pros: If Master crashes while waiting for ACK, the transaction isn't committed, Client gets failure, Slave has no data. **Absolute consistency**.

2.  **AFTER_COMMIT (Legacy)**:
    *   流程：Write Binlog -> Commit to Storage Engine -> **Wait for Slave ACK** -> Return to Client.
    *   缺點：若 Master 在等待 ACK 時當機，交易已在 Master Commit，其他 Session 可能讀到該資料（Phantom Read），但 Slave 可能沒收到。Failover 後該資料會憑空消失。
    *   Flow: Write Binlog -> Commit to Storage Engine -> **Wait for Slave ACK** -> Return to Client.
    *   Cons: If Master crashes while waiting for ACK, transaction is committed on Master, other sessions might read it (Phantom Read), but Slave might not have it. Data disappears after Failover.

**最佳實踐 (Best Practice)**:
```sql
SET GLOBAL rpl_semi_sync_master_wait_point = 'AFTER_SYNC';
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略 Binlog 空間管理 (Ignoring Binlog Space Management)
*   **錯誤 (Mistake)**: 開啟了 Binlog 但未設定 `binlog_expire_logs_seconds` (或舊版的 `expire_logs_days`)。
*   **後果 (Consequence)**: 磁碟被 Binlog 塞滿，導致 DB 當機 (Out of Disk Space)。
*   **修正 (Fix)**: 設定合理的過期時間（如 7 天），並監控磁碟使用率。

*   **Mistake**: Enabling Binlog without setting `binlog_expire_logs_seconds` (or the older `expire_logs_days`).
*   **Consequence**: Disk fills up with Binlogs, causing DB crash (Out of Disk Space).
*   **Fix**: Set a reasonable expiration time (e.g., 7 days) and monitor disk usage.

## 5.2 腦裂 (Split-Brain)
*   **錯誤 (Mistake)**: 自動化 Failover 機制配置不當。當網路分區（Network Partition）發生時，舊 Master 仍認為自己是 Master，新 Master 也被提升起來。
*   **後果 (Consequence)**: 兩個 Master 同時接受寫入，導致資料永久分歧，難以修復。
*   **修正 (Fix)**: 使用成熟的工具（如 **Orchestrator**）並配置 Fencing 機制（例如：切換時關閉舊 Master 的 VIP 或將其設為 `read_only=1`）。

*   **Mistake**: Improperly configured automated failover. During a Network Partition, the old Master still thinks it's Master, while a new Master is promoted.
*   **Consequence**: Both Masters accept writes simultaneously, leading to permanent data divergence that is hard to fix.
*   **Fix**: Use mature tools (like **Orchestrator**) and configure Fencing mechanisms (e.g., disable the old Master's VIP or set it to `read_only=1` during switch).

## 5.3 在 Slave 上執行寫入 (Accidental Writes on Slave)
*   **錯誤 (Mistake)**: 應用程式配置錯誤，連線到 Slave 進行寫入；或者 DBA 手動操作時忘記 `set sql_log_bin=0`。
*   **後果 (Consequence)**: 複製中斷，報錯 `Duplicate entry` 或 `Record not found`。
*   **修正 (Fix)**: 在所有 Slave 上強制設定 `read_only = 1` 和 `super_read_only = 1`。

*   **Mistake**: App misconfiguration connecting to Slave for writes; or DBA forgetting `set sql_log_bin=0` during manual ops.
*   **Consequence**: Replication breaks with `Duplicate entry` or `Record not found` errors.
*   **Fix**: Enforce `read_only = 1` and `super_read_only = 1` on all Slaves.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在應用層解決「讀己之寫（Read Your Own Write）」的一致性問題？
**How do you solve the "Read Your Own Write" consistency problem at the application layer?**

*   **高分回答要點 (Key Points)**:
    *   解釋 Replication Lag 的成因。
    *   **Sticky Session / Pinning**: 某個 User 的請求在寫入後的 X 秒內強制路由到 Master。
    *   **Version Monotonicity**: 記錄寫入時的 Log Position 或 GTID，讀取時檢查 Slave 是否已追上該進度（需 Middleware 如 ProxySQL 支援）。
    *   **Business Compromise**: 區分業務場景，非核心業務允許延遲，核心業務讀 Master。

## Q2: 為什麼 MySQL 預設是異步複製？這符合 CAP 定理的哪兩個屬性？
**Why is MySQL Async Replication the default? Which two attributes of the CAP theorem does this align with?**

*   **高分回答要點 (Key Points)**:
    *   預設追求 **Performance** 與 **Availability** (AP)。
    *   Async 複製下，Master 不需要等待網路回應，Throughput 最高。
    *   若改為 Semi-sync 或 Group Replication，則是在向 **Consistency** (CP) 靠攏，犧牲了部分 Latency 和 Availability（當 Slave 全掛時 Master 可能無法寫入）。

## Q3: 描述一次手動的主從切換（Failover）流程，以及如何利用 GTID 簡化它？
**Describe a manual Master-Slave failover process and how GTID simplifies it.**

*   **高分回答要點 (Key Points)**:
    *   **傳統方式**: 需找到 Relay Log 中最後執行的位置，在新 Master 上執行 `CHANGE MASTER TO ... MASTER_LOG_FILE=..., MASTER_LOG_POS=...`。容易出錯。
    *   **GTID 方式**: 只需要 `CHANGE MASTER TO MASTER_HOST='new_host', MASTER_AUTO_POSITION=1`。
    *   Slave 會自動計算缺少哪些 GTID 並請求同步，大幅降低維運風險。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Binlog Format**: 務必使用 **ROW** 格式以確保最大一致性與 CDC 支援。
2.  **GTID**: 是現代 MySQL 架構的基石，徹底解決了 Failover 時的定位難題。
3.  **Semi-Sync**: 透過 `AFTER_SYNC` 機制，在效能與資料安全（RPO=0）之間取得平衡。
4.  **Replication Lag**: 是物理限制，無法完全消除。必須在架構層（Cache, Routing）或業務層（UI 提示）處理。
5.  **High Availability**: 單靠 MySQL 自身無法完成自動 Failover，需搭配 Orchestrator、MHA 或 ProxySQL 等外部工具。

## 後續延伸 (Next Steps)
*   **ProxySQL**: 學習如何使用 ProxySQL 進行透明的讀寫分離與 Query Routing。
*   **MySQL Group Replication (MGR)**: 研究 MySQL 原生的 Paxos-based 高可用方案，對比其與 Semi-sync 的差異。
*   **Sharding**: 當單機寫入達到瓶頸時，如何利用 **Vitess** 進行水平分片（Sharding）。

下一章，我們將探討 **Schema Design 與 Indexing 優化**，這是提升單機查詢效能的最關鍵技能。
In the next chapter, we will explore **Schema Design and Indexing Optimization**, the most critical skill for improving single-node query performance.