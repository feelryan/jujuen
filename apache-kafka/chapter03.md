# Chapter 03: Consumer Groups and Rebalancing Strategies
# 第三章：消費者群組與重平衡策略

## 1. Introduction & Learning Goals
## 1. 前言與學習目標

For Senior Engineers, understanding how to consume messages is trivial; the real challenge lies in maintaining stability during scaling events and failures. This chapter dives deep into the mechanics of the Consumer Group Protocol, specifically focusing on the "Rebalance" process—often the root cause of latency spikes and throughput drops in production.

對於資深工程師而言，如何消費訊息是基本功；真正的挑戰在於如何在擴展或發生故障時維持系統穩定。本章將深入探討 Consumer Group Protocol 的運作機制，特別聚焦於「重平衡（Rebalance）」過程——這往往是生產環境中延遲飆升與吞吐量下降的根本原因。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Dissect the Rebalance Protocol**: Explain the difference between "Eager Rebalancing" (Stop-the-world) and "Incremental Cooperative Rebalancing."
    **剖析重平衡協定**：解釋「急切重平衡」（Stop-the-world）與「增量協作重平衡」之間的差異。
2.  **Optimize for Availability**: Implement **Static Membership** to avoid unnecessary rebalances during rolling restarts or transient network issues.
    **優化可用性**：實作 **Static Membership**，以避免在滾動重啟（Rolling Restarts）或短暫網路問題時觸發不必要的重平衡。
3.  **Debug Consumer Failures**: Distinguish between `session.timeout.ms` and `max.poll.interval.ms` to correctly diagnose "infinite rebalance loops."
    **除錯消費者故障**：區分 `session.timeout.ms` 與 `max.poll.interval.ms`，以正確診斷「無限重平衡迴圈」問題。
4.  **Tune Partition Assignment**: Select and configure the appropriate `PartitionAssignor` strategy for your specific workload.
    **調校分區分配**：針對特定工作負載選擇並配置合適的 `PartitionAssignor` 策略。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Coordinator & The Leader
### 2.1 協調者與領導者

**Mental Model**: Think of the Consumer Group as a democratic team with a manager (Broker) and a team lead (Client).
**心智模型**：將 Consumer Group 想像成一個擁有經理（Broker）與組長（Client）的民主團隊。

-   **Group Coordinator (Broker Side)**: One of the Kafka brokers acts as the Coordinator. It manages the group state, receives heartbeats, and orchestrates the rebalance. It does *not* decide which consumer gets which partition.
    **Group Coordinator（Broker 端）**：Kafka broker 之一擔任協調者。它管理群組狀態、接收心跳（Heartbeats）並協調重平衡。它**不**決定哪個消費者分配到哪個分區。

-   **Group Leader (Client Side)**: The first consumer to join the group becomes the Leader. The Coordinator sends the list of all members to the Leader. The Leader executes the partition assignment logic (e.g., Range, RoundRobin) locally and sends the plan back to the Coordinator.
    **Group Leader（Client 端）**：第一個加入群組的消費者成為 Leader。協調者會將所有成員名單發送給 Leader。Leader 在本地執行分區分配邏輯（如 Range, RoundRobin），並將分配計畫回傳給協調者。

### 2.2 Eager vs. Cooperative Rebalancing
### 2.2 急切重平衡 vs. 協作重平衡

This is the most critical evolution in Kafka's consumer history.
這是 Kafka 消費者演進史上最關鍵的變革。

-   **Eager Rebalancing (The "Stop-the-World" approach)**:
    When a rebalance starts, *all* consumers must stop fetching data and revoke *all* their assigned partitions. They sit idle while the Leader calculates a new assignment.
    *Analogy*: A fire drill where everyone must leave the building and wait outside before being assigned a new desk, even if 90% of people end up at the same desk.
    **急切重平衡（Stop-the-World 方法）**：
    當重平衡開始時，**所有**消費者必須停止抓取資料並交還**所有**已分配的分區。在 Leader 計算新分配時，它們處於閒置狀態。
    *類比*：就像一場消防演習，所有人必須離開大樓並在外面等待，然後重新分配座位，即使 90% 的人最終會回到原本的座位。

-   **Incremental Cooperative Rebalancing (The Modern Standard)**:
    Consumers only revoke partitions that *must* be moved to another member. They continue processing data for partitions they retain. This minimizes the "stop-the-world" pause.
    *Analogy*: A desk reshuffle where only the people moving departments need to pack up; everyone else keeps working.
    **增量協作重平衡（現代標準）**：
    消費者僅交還那些**必須**移動給其他成員的分區。它們繼續處理保留分區的資料。這將「Stop-the-world」的暫停時間降至最低。
    *類比*：就像調整座位表，只有換部門的人需要打包，其他人繼續工作。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Impact on Latency Sensitive Systems
### 3.1 對延遲敏感系統的影響

In a microservices architecture, a "Stop-the-world" rebalance directly impacts P99 latency.
在微服務架構中，「Stop-the-world」重平衡會直接衝擊 P99 延遲。

-   **Scenario**: You have a consumer group with 50 instances processing payment events.
-   **Event**: You deploy a new version (rolling restart).
-   **Consequence (Eager)**: As each instance restarts, it triggers a rebalance. With 50 instances, the group might be in a constant state of rebalancing for minutes, causing a massive backlog (lag).
-   **Consequence (Cooperative)**: The group remains stable. Only the partitions belonging to the restarting node are reassigned.

-   **情境**：你有一個包含 50 個實例的消費者群組正在處理支付事件。
-   **事件**：你部署新版本（滾動重啟）。
-   **後果（Eager）**：每當一個實例重啟，就會觸發重平衡。50 個實例可能導致群組在數分鐘內處於持續重平衡狀態，造成大量積壓（Lag）。
-   **後果（Cooperative）**：群組保持穩定。只有屬於重啟節點的分區會被重新分配。

### 3.2 Static Membership in Kubernetes
### 3.2 Kubernetes 中的靜態成員資格 (Static Membership)

In containerized environments (K8s), pods are ephemeral. By default, when a pod restarts, it gets a new `member.id`. The Coordinator sees this as "Old member left, New member joined," triggering two rebalances.
在容器化環境（K8s）中，Pod 是短暫的。預設情況下，當 Pod 重啟時，它會獲得一個新的 `member.id`。協調者將其視為「舊成員離開，新成員加入」，從而觸發兩次重平衡。

**Static Membership** (`group.instance.id`) allows the Coordinator to recognize the returning consumer as the "same" member. If it returns within the `session.timeout.ms`, no rebalance is triggered at all.
**靜態成員資格**（`group.instance.id`）允許協調者識別回歸的消費者為「同一個」成員。如果它在 `session.timeout.ms` 內返回，則完全不會觸發重平衡。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Configuring a Robust Consumer for Rolling Upgrades
### 情境：為滾動升級配置穩健的消費者

We want to configure a Kafka Consumer running on Kubernetes that minimizes disruption during deployments.
我們希望配置一個運行在 Kubernetes 上的 Kafka Consumer，以將部署期間的干擾降至最低。

#### Step 1: Enable Static Membership
#### 步驟 1：啟用靜態成員資格

We need to assign a unique ID to each consumer instance that persists across restarts. In Kubernetes, `StatefulSet` provides stable hostnames (e.g., `app-0`, `app-1`), which are perfect for this.
我們需要為每個消費者實例分配一個在重啟後仍然存在的唯一 ID。在 Kubernetes 中，`StatefulSet` 提供了穩定的主機名稱（如 `app-0`, `app-1`），非常適合此用途。

```java
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "payment-processor-group");

// Key Configuration for Static Membership
// 靜態成員資格的關鍵配置
// In K8s, this could be passed via ENV variable from metadata.name
props.put(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, System.getenv("POD_NAME")); 
```

#### Step 2: Tune Timeouts for Static Membership
#### 步驟 2：為靜態成員資格調整超時設定

With static membership, we want the Coordinator to wait for the pod to restart before reassigning its partitions. The default `session.timeout.ms` (often 10s or 45s) might be too short for a pod restart.
使用靜態成員資格時，我們希望協調者在重新分配分區之前等待 Pod 重啟。預設的 `session.timeout.ms`（通常是 10 秒或 45 秒）對於 Pod 重啟來說可能太短。

```java
// Increase session timeout to allow for pod restart (e.g., 2 minutes)
// 增加 session timeout 以允許 Pod 重啟（例如 2 分鐘）
props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, "120000"); 

// Heartbeat must be frequent enough (usually 1/3 of session timeout is safe, but standard is 3s)
// 心跳必須足夠頻繁（通常 session timeout 的 1/3 是安全的，但標準是 3 秒）
props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, "3000");
```

#### Step 3: Use Cooperative Rebalancing Strategy
#### 步驟 3：使用協作重平衡策略

Ensure we are using the `CooperativeStickyAssignor`. Since Kafka 2.4/3.0, this is often the default, but explicit configuration is safer.
確保我們使用的是 `CooperativeStickyAssignor`。自 Kafka 2.4/3.0 起，這通常是預設值，但顯式配置更安全。

```java
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    org.apache.kafka.clients.consumer.CooperativeStickyAssignor.class.getName());
```

#### Why this works?
#### 為何這樣有效？

1.  **Pod Restart**: `app-0` goes down.
2.  **Coordinator**: Does *not* trigger rebalance immediately because `group.instance.id=app-0` is known and `session.timeout.ms` (120s) hasn't passed.
3.  **Pod Returns**: `app-0` comes back up, connects with `group.instance.id=app-0`.
4.  **Result**: It resumes consuming its previous partitions. **Zero rebalances occurred.**
5.  **Fallback**: If `app-0` takes > 120s, the Coordinator finally triggers a rebalance.

1.  **Pod 重啟**：`app-0` 停止運作。
2.  **協調者**：**不會**立即觸發重平衡，因為 `group.instance.id=app-0` 是已知的，且 `session.timeout.ms` (120s) 尚未過期。
3.  **Pod 回歸**：`app-0` 重新啟動，並使用 `group.instance.id=app-0` 連線。
4.  **結果**：它繼續消費先前的分區。**發生了零次重平衡。**
5.  **備案**：如果 `app-0` 花費超過 120 秒，協調者最終會觸發重平衡。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Infinite Rebalance" Loop
### 5.1 「無限重平衡」迴圈

-   **Anti-pattern**: Performing heavy processing (e.g., DB writes, external API calls) inside the poll loop that exceeds `max.poll.interval.ms`.
-   **Mechanism**: The consumer background thread sends heartbeats fine (keeping the session alive), but the main thread is stuck processing. If `poll()` isn't called within `max.poll.interval.ms`, the client proactively leaves the group, thinking the application logic is hung.
-   **Fix**:
    1.  Increase `max.poll.interval.ms`.
    2.  Reduce `max.poll.records` to process fewer messages per batch.
    3.  Move processing to a separate thread pool (with caution regarding commit offsets).

-   **反模式**：在 poll 迴圈中執行繁重的處理（如 DB 寫入、外部 API 呼叫），時間超過 `max.poll.interval.ms`。
-   **機制**：消費者的背景執行緒正常發送心跳（保持 session 存活），但主執行緒卡在處理邏輯中。如果 `poll()` 未在 `max.poll.interval.ms` 內被呼叫，客戶端會認為應用程式邏輯卡死，主動離開群組。
-   **修正**：
    1.  增加 `max.poll.interval.ms`。
    2.  減少 `max.poll.records` 以降低每批次處理的訊息量。
    3.  將處理移至獨立的執行緒池（需注意 commit offset 的處理）。

### 5.2 Misunderstanding `session.timeout.ms`
### 5.2 誤解 `session.timeout.ms`

-   **Pitfall**: Setting `session.timeout.ms` extremely high (e.g., 30 minutes) without Static Membership.
-   **Consequence**: If a consumer hard-crashes (no graceful shutdown), the Coordinator waits 30 minutes before realizing the consumer is dead. During this time, partitions assigned to the dead consumer are **not processed** (lag piles up).
-   **Best Practice**: Keep `session.timeout.ms` relatively low (e.g., 10-45s) for dynamic groups to detect failures quickly. Only increase it if using Static Membership.

-   **陷阱**：在未使用靜態成員資格的情況下，將 `session.timeout.ms` 設定得極高（例如 30 分鐘）。
-   **後果**：如果消費者硬崩潰（未優雅關機），協調者會等待 30 分鐘才意識到該消費者已死。在此期間，分配給該死掉消費者的分區**不會被處理**（Lag 堆積）。
-   **最佳實踐**：對於動態群組，保持 `session.timeout.ms` 相對較低（如 10-45 秒）以快速偵測故障。只有在使用靜態成員資格時才增加它。

### 5.3 Blocking the Heartbeat Thread (Legacy Clients)
### 5.3 阻塞心跳執行緒（舊版客戶端）

-   **Note**: In very old Kafka clients (< 0.10.1), heartbeat and poll happened on the same thread. Long processing stopped heartbeats.
-   **Status**: Modern clients use a background thread for heartbeats. However, CPU starvation (e.g., massive GC pauses) can still block the background thread, causing session timeouts. Monitor GC logs if you see unexplained rebalances.

-   **注意**：在非常舊的 Kafka 客戶端（< 0.10.1），心跳與 poll 發生在同一執行緒。長時間處理會停止心跳。
-   **現況**：現代客戶端使用背景執行緒發送心跳。然而，CPU 資源耗盡（例如大規模 GC 暫停）仍可能阻塞背景執行緒，導致 session timeout。若看到無法解釋的重平衡，請監控 GC log。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle a "poison pill" message that crashes the consumer application?
### Q1: 你如何處理導致消費者應用程式崩潰的「毒丸（Poison Pill）」訊息？

-   **Key Points**:
    -   If the app crashes, restarts, reads the same message, and crashes again, it causes an infinite loop.
    -   **Solution**: Use a `Dead Letter Queue (DLQ)`. Wrap processing in a try-catch block. If processing fails repeatedly, commit the offset but produce the failed message to a DLQ topic for manual inspection.
    -   **Advanced**: Explain "Blocking Retry" vs "Non-blocking Retry" topics.

-   **高分回答要點**：
    -   如果應用程式崩潰、重啟、讀取同一訊息並再次崩潰，會導致無限迴圈。
    -   **解法**：使用 `死信隊列 (DLQ)`。將處理邏輯包在 try-catch區塊中。若重複失敗，提交 offset 但將失敗訊息發送到 DLQ topic 以供人工檢查。
    -   **進階**：解釋「阻塞重試」與「非阻塞重試」topic 的差異。

### Q2: Explain the difference between `max.poll.interval.ms` and `session.timeout.ms`. Why do we need both?
### Q2: 請解釋 `max.poll.interval.ms` 與 `session.timeout.ms` 的差異。為什麼我們兩者都需要？

-   **Key Points**:
    -   `session.timeout.ms`: Detects **network/machine failures** (hard crash). Managed by the background heartbeat thread.
    -   `max.poll.interval.ms`: Detects **application logic issues** (stuck processing, livelock). Managed by the main poll thread.
    -   We need both to distinguish between a consumer that is disconnected vs. a consumer that is connected but hung.

-   **高分回答要點**：
    -   `session.timeout.ms`：偵測**網路/機器故障**（硬崩潰）。由背景心跳執行緒管理。
    -   `max.poll.interval.ms`：偵測**應用程式邏輯問題**（處理卡住、活鎖）。由主 poll 執行緒管理。
    -   我們需要兩者來區分「斷線的消費者」與「連線中但卡死的消費者」。

### Q3: In a high-throughput system, rebalancing takes too long. How do you debug and fix it?
### Q3: 在高吞吐量系統中，重平衡耗時過長。你會如何除錯並修復？

-   **Key Points**:
    -   **Check Strategy**: Are we using Eager Rebalancing? Switch to `CooperativeStickyAssignor`.
    -   **Check Commit Logic**: Are we committing offsets synchronously (`commitSync`) during rebalance revocation? This slows down the "join" phase.
    -   **Check Member Count**: Is the group too large? (Hundreds of consumers).
    -   **Logs**: Look for "JoinGroup" and "SyncGroup" duration in broker logs.

-   **高分回答要點**：
    -   **檢查策略**：是否使用急切重平衡？切換至 `CooperativeStickyAssignor`。
    -   **檢查提交邏輯**：是否在重平衡撤銷期間同步提交 offset（`commitSync`）？這會拖慢「加入」階段。
    -   **檢查成員數量**：群組是否過大？（數百個消費者）。
    -   **日誌**：查看 broker log 中的 "JoinGroup" 與 "SyncGroup" 持續時間。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Coordinator & Leader**: The Broker coordinates; the Client (Leader) decides the assignment.
2.  **Stop-the-world is optional**: Modern Kafka uses **Incremental Cooperative Rebalancing** to eliminate global pauses.
3.  **Static Membership**: Use `group.instance.id` to prevent rebalances during transient failures or rolling restarts.
4.  **Timeout Tuning**:
    -   `session.timeout.ms`: For network/crash detection.
    -   `max.poll.interval.ms`: For processing logic stall detection.
5.  **Assignors**: Prefer `CooperativeStickyAssignor` for stateful or high-availability workloads.

1.  **協調者與領導者**：Broker 負責協調；Client（Leader）決定分配。
2.  **Stop-the-world 是可選的**：現代 Kafka 使用**增量協作重平衡**來消除全域暫停。
3.  **靜態成員資格**：使用 `group.instance.id` 來防止短暫故障或滾動重啟期間的重平衡。
4.  **超時調校**：
    -   `session.timeout.ms`：用於網路/崩潰偵測。
    -   `max.poll.interval.ms`：用於處理邏輯停滯偵測。
5.  **分配器**：對於有狀態或高可用性工作負載，優先選擇 `CooperativeStickyAssignor`。

### Next Steps
### 後續延伸

Now that you can maintain a stable consumer group, the next challenge is ensuring data integrity and handling scale.
既然你已能維持穩定的消費者群組，下一個挑戰是確保資料完整性並處理規模擴展。

-   **Next Chapter**: **Delivery Semantics & Transactions** (At-least-once vs. Exactly-once).
-   **Action Item**: Check your current production configurations. Are you using the default `RangeAssignor`? Do you have `group.instance.id` configured for your K8s deployments?

-   **下一章**：**交付語義與交易**（At-least-once vs. Exactly-once）。
-   **行動項目**：檢查你目前的生產環境配置。你是否在使用預設的 `RangeAssignor`？你的 K8s 部署是否配置了 `group.instance.id`？