# Chapter 06: Replication and High Availability
# 第 06 章：高可用性與複製集機制

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In distributed systems, hardware failure is inevitable. For a Senior Engineer, mastering MongoDB's replication is not just about setting up a cluster; it's about understanding the trade-offs between **Consistency**, **Availability**, and **Latency**. This chapter moves beyond basic configuration to the internal mechanics of the Oplog, the nuances of elections, and how to design for resilience.

在分散式系統中，硬體故障是不可避免的。對於資深工程師而言，掌握 MongoDB 的複製機制不僅僅是架設叢集，更在於理解 **一致性（Consistency）**、**可用性（Availability）** 與 **延遲（Latency）** 之間的權衡。本章將超越基礎配置，深入探討 Oplog 的內部運作、選舉機制的細節，以及如何設計具備韌性的系統。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Explain the Oplog mechanics**: Understand how the Operations Log drives replication and ensures data consistency.
    **解釋 Oplog 機制**：理解操作日誌（Operations Log）如何驅動複製並確保資料一致性。
2.  **Tune Consistency vs. Availability**: Use `Write Concern` and `Read Preference` to satisfy specific business requirements (e.g., strong consistency for payments vs. eventual consistency for analytics).
    **調校一致性與可用性**：利用 `Write Concern` 與 `Read Preference` 來滿足特定業務需求（例如：支付需強一致性，分析可接受最終一致性）。
3.  **Diagnose Replication Lag**: Identify causes of lag and calculate the appropriate Oplog size to prevent full resyncs.
    **診斷複製延遲**：識別延遲成因並計算合適的 Oplog 大小以防止全量重新同步。
4.  **Architect for Failover**: Design client-side logic to handle elections and automatic failover gracefully without downtime.
    **設計故障轉移架構**：設計客戶端邏輯以優雅地處理選舉與自動故障轉移，確保服務不中斷。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Replica Set Architecture
### 2.1 複製集架構

A MongoDB **Replica Set** is a group of `mongod` processes that maintain the same data set. Unlike traditional Master-Slave architectures where slaves are often read-only and manual intervention is required for promotion, MongoDB uses a **Primary-Secondary** model with automated elections.

MongoDB 的 **複製集（Replica Set）** 是一組維護相同資料集的 `mongod` 行程。不同於傳統的主從（Master-Slave）架構（從節點通常唯讀且需人工介入提升），MongoDB 採用具備自動選舉功能的 **Primary-Secondary** 模型。

*   **Primary**: The only member that receives writes. It records all changes in the **Oplog**.
    **Primary（主節點）**：唯一接收寫入的成員。它將所有變更記錄在 **Oplog** 中。
*   **Secondary**: Replicates the Oplog from the Primary (or other Secondaries) and applies the operations to its dataset asynchronously.
    **Secondary（次節點）**：從 Primary（或其他 Secondary）複製 Oplog，並非同步地將操作應用於自身的資料集。
*   **Arbiter**: A voting-only member that holds no data. (Note: Use with caution in production).
    **Arbiter（仲裁節點）**：僅參與投票，不持有資料。（注意：在生產環境中需謹慎使用）。

### 2.2 The Oplog (Operations Log)
### 2.2 操作日誌 (Oplog)

The **Oplog** is the heart of replication. It is a **capped collection** that keeps a rolling record of all operations that modify the data.
**Oplog** 是複製機制的心臟。它是一個 **固定大小集合（Capped Collection）**，保存了所有修改資料的操作之滾動紀錄。

*   **Idempotency**: Oplog entries are idempotent. Applying the same Oplog entry multiple times results in the same state. For example, an `$inc` (increment) operation in a query is translated into a `$set` operation in the Oplog.
    **冪等性（Idempotency）**：Oplog 條目是冪等的。多次應用同一個 Oplog 條目會得到相同的狀態。例如，查詢中的 `$inc`（遞增）操作在 Oplog 中會被轉換為 `$set` 操作。
*   **Pull Model**: Secondaries pull data from the Primary. They are not "pushed" to.
    **拉取模型（Pull Model）**：Secondary 主動從 Primary 拉取資料，而非被動接收推送。

### 2.3 Mental Model: The Distributed Journal
### 2.3 心智模型：分散式日誌

Think of the Replica Set as a team of accountants.
將複製集想像成一個會計團隊。

1.  **The Chief Accountant (Primary)** writes every transaction into a main journal (Oplog).
    **首席會計（Primary）** 將每筆交易寫入主日誌（Oplog）。
2.  **Junior Accountants (Secondaries)** constantly peek at the Chief's journal and copy the entries into their own private journals.
    **初級會計（Secondaries）** 不斷查看首席的日誌，並將條目抄寫到自己的私人日誌中。
3.  **Election**: If the Chief falls ill, the Juniors vote. The one with the most up-to-date journal is most likely to be elected as the new Chief.
    **選舉**：如果首席生病了，初級會計們會進行投票。日誌內容最新的人最有可能被選為新任首席。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Consistency vs. Availability (CAP Theorem)
### 3.1 一致性與可用性（CAP 定理）

In the context of the CAP theorem, MongoDB is technically a **CP** (Consistency and Partition Tolerance) system by default when strong consistency is required. However, it offers tunable knobs to behave more like an **AP** system.
在 CAP 定理的脈絡下，當需要強一致性時，MongoDB 預設技術上是一個 **CP**（一致性與分區容錯）系統。然而，它提供了可調整的參數，使其表現得更像 **AP** 系統。

*   **Strong Consistency (CP-like)**:
    *   `Write Concern: { w: "majority" }`
    *   `Read Preference: "primary"`
    *   **Trade-off**: High latency for writes (must wait for ack), potential downtime for writes during elections.
*   **High Availability / Eventual Consistency (AP-like)**:
    *   `Write Concern: { w: 1 }`
    *   `Read Preference: "secondaryPreferred"`
    *   **Trade-off**: Fast writes, but risk of data loss if Primary fails before replicating. Reads may return stale data.

### 3.2 Production Architecture: PSS vs. PSA
### 3.2 生產環境架構：PSS vs. PSA

*   **PSS (Primary-Secondary-Secondary)**: The gold standard. Provides high availability and two copies of data for redundancy. If one node fails, you still have a majority (2/3) to elect a Primary.
    **PSS (Primary-Secondary-Secondary)**：黃金標準。提供高可用性與兩份資料冗餘。若一個節點故障，仍有過半數（2/3）可選出 Primary。
*   **PSA (Primary-Secondary-Arbiter)**: Cost-saving measure. The Arbiter is cheap but introduces risks. If the Secondary fails, the Primary + Arbiter can stay up, but **Write Concern: Majority** issues may arise (data is only on one data node).
    **PSA (Primary-Secondary-Arbiter)**：節省成本的方案。Arbiter 很便宜但引入風險。若 Secondary 故障，Primary + Arbiter 雖可運作，但 **Write Concern: Majority** 可能會出問題（資料僅存在於一個資料節點）。

### 3.3 Client-Side Resilience
### 3.3 客戶端韌性

In a microservices architecture, the application driver handles the complexity of connecting to the Replica Set.
在微服務架構中，應用程式驅動程式（Driver）處理了連接複製集的複雜性。

*   **Seed List**: You provide a list of IPs (e.g., `mongodb://node1,node2,node3/db`). The driver auto-discovers the current Primary.
    **種子清單**：你提供一組 IP 清單（如 `mongodb://node1,node2,node3/db`）。驅動程式會自動探索當前的 Primary。
*   **Server Selection Timeout**: Critical setting. How long should the app wait during an election before throwing an error? (Default is usually 30s, which might be too long for user-facing APIs).
    **伺服器選擇超時**：關鍵設定。應用程式在選舉期間應等待多久才拋出錯誤？（預設通常是 30 秒，對面向使用者的 API 來說可能太長）。

---

## 4. Walkthrough: Configuring Durability & Handling Failover
## 4. 逐步示例：配置持久性與處理故障轉移

### Scenario: Financial Transaction System
### 情境：金融交易系統

We are building a wallet service. Losing a deposit record is unacceptable. We need to ensure that once the system says "Success," the data survives a Primary crash.
我們正在建構一個錢包服務。遺失存款紀錄是不可接受的。我們必須確保一旦系統回應「成功」，該資料在 Primary 崩潰後仍能存活。

### Step 1: The Naive Approach (Default)
### 步驟 1：天真做法（預設值）

```javascript
// Default Write Concern (w: 1)
// Only waits for the Primary to acknowledge the write in memory.
await db.collection('transactions').insertOne({
  userId: "user_123",
  amount: 100,
  currency: "USD"
});
```
*   **Risk**: If the Primary crashes 1ms after acknowledging but *before* replicating to Secondaries, the data is lost forever during failover (Rollback).
*   **風險**：若 Primary 在確認寫入後、複製到 Secondary *之前* 的 1 毫秒內崩潰，該資料將在故障轉移期間永久遺失（回滾）。

### Step 2: The Senior Approach (Write Concern Majority)
### 步驟 2：資深做法（Write Concern Majority）

We modify the write concern to ensure the data is written to the **journal** of a **majority** of nodes.
我們修改寫入關注設定，確保資料被寫入**過半數**節點的 **journal** 中。

```javascript
// Strong Durability
const writeResult = await db.collection('transactions').insertOne(
  {
    userId: "user_123",
    amount: 100,
    currency: "USD"
  },
  {
    writeConcern: {
      w: "majority",   // Wait for majority of voting members
      j: true,         // Wait for on-disk journal sync
      wtimeout: 5000   // Don't wait forever
    }
  }
);
```

### Step 3: Handling `wtimeout`
### 步驟 3：處理 `wtimeout`

If `wtimeout` occurs, the write *might* have succeeded on the Primary but failed to replicate in time.
如果發生 `wtimeout`，寫入*可能*在 Primary 上成功了，但未能及時複製。

**Decision Logic (Pseudo-code):**
**決策邏輯（虛擬碼）：**
```python
try:
    insert_transaction(data, write_concern="majority")
except WriteConcernError as e:
    # The data IS on the Primary, but not on Secondaries yet.
    # Do NOT retry immediately if idempotency isn't guaranteed.
    # Alert monitoring: "Replication Lag High"
    log_warning("Write successful but replication timed out")
    return "Pending Confirmation" 
except ConnectionError:
    # Network issue or Election in progress
    # Safe to retry if idempotent
    retry_operation()
```

### Step 4: Read Preference for Scalability?
### 步驟 4：利用 Read Preference 擴展？

A common request is to offload reads to Secondaries.
一個常見的需求是將讀取分流至 Secondary。

```javascript
// Reading from Secondary
// Risk: Replication lag means user might not see their deposit immediately.
const balance = await db.collection('balances')
  .withReadPreference('secondaryPreferred') 
  .findOne({ userId: "user_123" });
```
*   **Design Decision**: For a wallet balance, use `primary`. For "Transaction History" (which is immutable and less time-sensitive), `secondaryPreferred` might be acceptable *if* the UI handles potential lag.
*   **設計決策**：對於錢包餘額，應使用 `primary`。對於「交易歷史」（不可變且時間敏感度較低），若 UI 能處理潛在延遲，`secondaryPreferred` 可能是可接受的。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Even Number of Nodes" Trap
### 5.1 「偶數節點」陷阱

*   **Anti-pattern**: Deploying a 2-node or 4-node Replica Set without an Arbiter.
    **反模式**：部署 2 個或 4 個節點的複製集而沒有 Arbiter。
*   **Why it's bad**: In a 2-node set, if one dies, the remaining one has 50% of votes, not a *majority* (>50%). It will step down to Secondary. The cluster becomes read-only.
    **為何不好**：在 2 節點集合中，若一個掛掉，剩餘那個只有 50% 票數，未達 *過半數*（>50%）。它會降級為 Secondary，導致叢集變為唯讀。
*   **Solution**: Always maintain an odd number of voting members (e.g., 3 data nodes, or 2 data + 1 arbiter).
    **解法**：始終維持奇數個投票成員（例如 3 個資料節點，或 2 資料 + 1 仲裁）。

### 5.2 Oplog Window Too Small
### 5.2 Oplog 視窗過小

*   **Anti-pattern**: Default Oplog size on a write-heavy system.
    **反模式**：在寫入密集的系統上使用預設 Oplog 大小。
*   **Why it's bad**: If a Secondary goes down for maintenance for 1 hour, but the Oplog only holds 30 minutes of operations, the Secondary cannot catch up incrementally. It enters **Initial Sync** (deletes all data and reclones from scratch), killing network bandwidth and IO.
    **為何不好**：若 Secondary 因維護停機 1 小時，但 Oplog 僅保留 30 分鐘的操作紀錄，Secondary 將無法進行增量同步。它會進入 **Initial Sync（初始化同步）**（刪除所有資料並從頭複製），這會耗盡網路頻寬與 IO。
*   **Solution**: Monitor `Replication Oplog Window` metric. Size it to cover at least 24 hours of peak write traffic.
    **解法**：監控 `Replication Oplog Window` 指標。將其大小設定為至少能覆蓋 24 小時的峰值寫入流量。

### 5.3 Reading from Secondaries for "Real-time" Data
### 5.3 讀取 Secondary 獲取「即時」資料

*   **Anti-pattern**: Using `secondary` read preference to scale read throughput for user profiles or settings.
    **反模式**：使用 `secondary` 讀取偏好來擴展使用者設定檔或設定的讀取吞吐量。
*   **Why it's bad**: "Read-your-own-writes" consistency is violated. A user updates their profile, reloads the page, and sees the old profile because the read hit a lagging Secondary.
    **為何不好**：違反了「讀取自己寫入（Read-your-own-writes）」的一致性。使用者更新設定檔，重整頁面，卻看到舊資料，因為讀取請求打到了有延遲的 Secondary。
*   **Solution**: Use `primary` for interactive user data. Use Secondaries for analytics, reporting, or batch jobs.
    **解法**：互動式使用者資料請用 `primary`。Secondary 用於分析、報表或批次作業。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How does MongoDB handle a Primary failure? What happens to the application?
### Q1: MongoDB 如何處理 Primary 故障？應用程式會發生什麼事？

*   **Key Points**:
    *   **Detection**: Heartbeats fail.
    *   **Election**: Remaining nodes vote. Requires majority (n/2 + 1).
    *   **Time**: Takes 2-10 seconds (tunable via `electionTimeoutMillis`).
    *   **App Impact**: Writes fail during election. Reads may fail or succeed (if `secondaryPreferred`). Drivers buffer or throw errors depending on config.
    *   **Rollback**: If the old Primary had writes that weren't replicated, they are rolled back to a file when it rejoins as a Secondary.
*   **高分要點**：
    *   **偵測**：心跳（Heartbeats）失敗。
    *   **選舉**：剩餘節點投票。需過半數（n/2 + 1）。
    *   **時間**：耗時 2-10 秒（可透過 `electionTimeoutMillis` 調整）。
    *   **應用影響**：選舉期間寫入失敗。讀取可能失敗或成功（若設為 `secondaryPreferred`）。驅動程式依設定會緩衝請求或拋出錯誤。
    *   **回滾**：若舊 Primary 有未複製的寫入，當它以 Secondary 身分重新加入時，這些寫入會被回滾並存檔。

### Q2: Explain "Chain Replication" and its impact.
### Q2: 解釋「鏈式複製（Chain Replication）」及其影響。

*   **Key Points**:
    *   By default, Secondaries may sync from other Secondaries (closer in network latency) rather than the Primary.
    *   **Pros**: Reduces load on Primary.
    *   **Cons**: Increases replication lag.
    *   **Control**: Can be disabled via `settings.chainingAllowed`.
*   **高分要點**：
    *   預設情況下，Secondary 可能會從其他 Secondary（網路延遲較低者）同步，而非從 Primary。
    *   **優點**：減輕 Primary 負載。
    *   **缺點**：增加複製延遲。
    *   **控制**：可透過 `settings.chainingAllowed` 禁用。

### Q3: Why is `w:majority` slower? How does it work internally?
### Q3: 為什麼 `w:majority` 比較慢？它內部是如何運作的？

*   **Key Points**:
    *   The Primary writes to its own journal/memory.
    *   It waits for the Oplog entry to propagate to `floor(n/2)` Secondaries.
    *   It waits for acknowledgments from those Secondaries.
    *   Only then does it respond "Success" to the client.
    *   **Latency**: Round-trip time (RTT) to the slowest necessary Secondary determines the speed.
*   **高分要點**：
    *   Primary 寫入自身的 journal/記憶體。
    *   它等待 Oplog 條目傳播至 `floor(n/2)` 個 Secondary。
    *   它等待這些 Secondary 的確認回應。
    *   直到那時才向客戶端回應「成功」。
    *   **延遲**：往返時間（RTT）取決於所需的最慢 Secondary。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap
### 重點回顧

1.  **Replica Set** is the foundation of High Availability in MongoDB, relying on automatic elections and the **Oplog**.
    **複製集** 是 MongoDB 高可用性的基礎，依賴自動選舉與 **Oplog**。
2.  **Oplog** is a capped collection; sizing it correctly is vital to prevent sync failures (Initial Sync).
    **Oplog** 是固定大小集合；正確設定其大小對於防止同步失敗（初始化同步）至關重要。
3.  **Write Concern (`w`)** controls Durability vs. Latency. `w:majority` prevents data rollbacks.
    **Write Concern (`w`)** 控制持久性與延遲的權衡。`w:majority` 可防止資料回滾。
4.  **Read Preference** controls Consistency vs. Read Scalability. Avoid `secondary` reads for flows requiring strong consistency.
    **Read Preference** 控制一致性與讀取擴展性的權衡。需強一致性的流程應避免讀取 `secondary`。
5.  **Odd Voting Members**: Always ensure an odd number of votes to prevent split-brain scenarios.
    **奇數投票成員**：始終確保奇數票數以防止腦裂（Split-brain）情境。

### Next Steps
### 後續延伸

*   **Read**: Deep dive into **Sharding** (Chapter 07). While Replication scales availability, Sharding scales storage and write throughput.
    **閱讀**：深入研讀 **分片（Sharding）**（第 07 章）。複製集擴展了可用性，而分片則擴展了儲存空間與寫入吞吐量。
*   **Practice**: Set up a local 3-node Replica Set using Docker. Kill the Primary and observe the election logs and client driver behavior.
    **實作**：使用 Docker 架設本地端的 3 節點複製集。強制關閉 Primary，觀察選舉日誌與客戶端驅動程式的行為。
*   **Advanced**: Investigate **Linearizable Reads** (`readConcern: "linearizable"`) and how it guarantees you are reading from a *current* Primary (avoiding stale reads during network partitions).
    **進階**：研究 **線性化讀取（Linearizable Reads）**（`readConcern: "linearizable"`）及其如何保證你讀取的是 *當前* 的 Primary（避免網路分區時的過期讀取）。