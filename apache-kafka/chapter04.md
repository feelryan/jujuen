# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，在設計高吞吐量的分散式系統時，「資料不遺失」（Data Durability）往往是與「系統可用性」（Availability）並列的最高指導原則。Apache Kafka 的副本機制（Replication Protocol）是其保證資料耐久性的核心。本章不只是談設定檔怎麼寫，而是要深入理解 Kafka 如何透過 ISR、HW 與 LEO 來達成資料一致性。

As a Senior Engineer designing high-throughput distributed systems, "Data Durability" is often the highest guiding principle alongside "Availability." Apache Kafka's Replication Protocol is the core mechanism guaranteeing this durability. This chapter goes beyond configuration syntax to provide a deep understanding of how Kafka achieves data consistency through ISR, HW, and LEO.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準解釋 LEO 與 HW 的關係**：理解 Log End Offset 與 High Watermark 如何決定 Consumer 的可見性與資料截斷（Truncation）行為。
    **Precisely explain the relationship between LEO and HW**: Understand how Log End Offset and High Watermark determine consumer visibility and data truncation behavior.
2.  **掌握 ISR 的動態機制**：說明 In-Sync Replicas 是如何判定節點健康狀態，以及它在 Leader Election 中的關鍵角色。
    **Master the dynamic mechanism of ISR**: Explain how In-Sync Replicas determine node health and their critical role in Leader Election.
3.  **設計高可靠配置**：在 `acks=all`、`min.insync.replicas` 與 `unclean.leader.election.enable` 之間做出正確的權衡（Trade-off），以滿足不同的 SLA 要求。
    **Design high-reliability configurations**: Make the right trade-offs between `acks=all`, `min.insync.replicas`, and `unclean.leader.election.enable` to meet different SLA requirements.
4.  **理解 Leader Epoch**：解釋 Kafka 如何利用 Epoch 防止「殭屍 Leader」（Zombie Leader）導致的資料不一致。
    **Understand Leader Epoch**: Explain how Kafka uses Epochs to prevent data inconsistencies caused by "Zombie Leaders."

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要理解 Kafka 的副本機制，我們需要建立一個關於「日誌複製狀態機」（Log Replication State Machine）的心智模型。

To understand Kafka's replication mechanism, we need to build a mental model of a "Log Replication State Machine."

### 2.1 LEO (Log End Offset) vs. HW (High Watermark)

這是 Kafka 副本機制中最基礎的兩個指針。
These are the two most fundamental pointers in Kafka's replication mechanism.

*   **LEO (Log End Offset)**:
    *   **定義**：日誌中下一條訊息將要寫入的位置（即最後一條訊息的 Offset + 1）。每個副本（Leader 和 Follower）都有自己的 LEO。
    *   **Definition**: The position where the next message will be written in the log (i.e., the last message's Offset + 1). Every replica (Leader and Follower) has its own LEO.
    *   **意義**：代表該節點「寫入」了多少資料，但不代表這些資料是「安全」的。
    *   **Significance**: Represents how much data the node has "written," but does not imply the data is "safe."

*   **HW (High Watermark)**:
    *   **定義**：ISR 中所有副本的 LEO 的最小值（即所有同步副本都已擁有的訊息位置）。
    *   **Definition**: The minimum LEO among all replicas in the ISR (i.e., the message position possessed by all in-sync replicas).
    *   **意義**：HW 之前的資料被認為是「已提交」（Committed）的。**Consumer 只能讀取到 HW 之前的訊息**。
    *   **Significance**: Data before the HW is considered "Committed." **Consumers can only read messages up to the HW.**

> **Mental Model**: 想像一個多人協作的 Google Doc。LEO 是你正在打字的光標位置，而 HW 是「存檔點」。只有在所有協作者（ISR）都同步到了某個段落後，存檔點才會推進，讀者（Consumer）才看得到這段內容。
>
> **Mental Model**: Imagine a collaborative Google Doc. LEO is your typing cursor position, while HW is the "Save Point." Only when all collaborators (ISR) have synced up to a certain paragraph does the save point advance, making that content visible to readers (Consumers).

### 2.2 ISR (In-Sync Replicas)

ISR 是一組動態維護的副本集合，包含 Leader 本身以及所有「跟得上」Leader 的 Follower。
ISR is a dynamically maintained set of replicas, including the Leader itself and all Followers that are "keeping up" with the Leader.

*   **判定標準 (Criteria)**: 透過 `replica.lag.time.max.ms` 參數控制。如果 Follower 在這段時間內沒有向 Leader 發送 Fetch 請求或無法追上 LEO，就會被踢出 ISR。
*   **Criteria**: Controlled by the `replica.lag.time.max.ms` parameter. If a Follower does not send a Fetch request or cannot catch up to the LEO within this timeframe, it is kicked out of the ISR.
*   **關鍵作用 (Critical Role)**: 只有 ISR 中的成員才有資格參與 Leader Election（除非開啟 `unclean` 選舉）。
*   **Critical Role**: Only members in the ISR are eligible to participate in Leader Election (unless `unclean` election is enabled).

### 2.3 Leader Epoch

為了解決舊版 Kafka 僅依賴 HW 可能導致的資料遺失或不一致（如截斷錯誤），引入了 Leader Epoch。
To solve data loss or inconsistency issues (like truncation errors) caused by relying solely on HW in older Kafka versions, Leader Epoch was introduced.

*   **定義**：一對值 `(Epoch, StartOffset)`。每次 Leader 變更，Epoch 加 1。
*   **Definition**: A pair of values `(Epoch, StartOffset)`. Every time the Leader changes, the Epoch increments by 1.
*   **作用**：當 Follower 重新加入或 Leader 切換時，透過 Epoch 來準確判斷日誌應該從哪裡截斷，而不是單純依賴不可靠的 HW。
*   **Function**: When a Follower rejoins or a Leader switch occurs, the Epoch is used to accurately determine where the log should be truncated, rather than relying on the unreliable HW.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或 Production 架構規劃中，Kafka 的副本機制直接決定了系統的 **RPO (Recovery Point Objective)** 和 **可用性 (Availability)**。

In system design interviews or production architecture planning, Kafka's replication mechanism directly dictates the system's **RPO (Recovery Point Objective)** and **Availability**.

### 3.1 耐久性 vs. 延遲的權衡 (Durability vs. Latency Trade-off)

在金融交易或稽核日誌（Audit Log）場景中，我們通常要求「零資料遺失」。這需要 Producer 設定 `acks=all`。
In financial transactions or Audit Log scenarios, we typically require "zero data loss." This necessitates the Producer setting `acks=all`.

*   **流程**：Producer -> Leader (Write LEO) -> Followers (Fetch & Write LEO) -> Leader (Update HW) -> Ack to Producer.
*   **Process**: Producer -> Leader (Write LEO) -> Followers (Fetch & Write LEO) -> Leader (Update HW) -> Ack to Producer.
*   **代價**：延遲（Latency）會增加，因為必須等待 ISR 中所有副本確認。
*   **Cost**: Latency increases because the system must wait for acknowledgments from all replicas in the ISR.

### 3.2 最小同步副本 (Min In-Sync Replicas)

單純設定 `acks=all` 並不保證資料絕對安全。如果 ISR 只剩下 Leader 一個節點，`acks=all` 就退化成了 `acks=1`。
Simply setting `acks=all` does not guarantee absolute data safety. If the ISR shrinks to just the Leader, `acks=all` degrades to `acks=1`.

*   **設計模式**：必須配合 Broker 端（或 Topic 層級）的 `min.insync.replicas` 參數。
*   **Design Pattern**: Must be paired with the Broker-side (or Topic-level) parameter `min.insync.replicas`.
*   **典型配置 (Typical Config)**:
    *   `replication.factor = 3`
    *   `min.insync.replicas = 2`
    *   `acks = all`
*   **結果**：允許 1 個節點故障而不影響寫入；若 2 個節點故障，Producer 會收到 `NotEnoughReplicasException`，此時系統選擇「拒絕寫入（犧牲可用性）」來「保護一致性」。
*   **Result**: Allows 1 node failure without impacting writes; if 2 nodes fail, the Producer receives `NotEnoughReplicasException`. The system chooses to "reject writes (sacrifice availability)" to "protect consistency."

### 3.3 跨可用區部署 (Multi-AZ Deployment)

為了容忍機房級別的故障，副本應分散在不同的 Availability Zones (AZ)。
To tolerate data center-level failures, replicas should be distributed across different Availability Zones (AZ).

*   **Rack Awareness**: 設定 `broker.rack` 參數，Kafka 會盡量將同一個 Partition 的副本分配到不同的 Rack/AZ。
*   **Rack Awareness**: By configuring the `broker.rack` parameter, Kafka attempts to distribute replicas of the same Partition across different Racks/AZs.

---

# 4. 逐步示例 (Walkthrough / Example)

讓我們透過一個具體的寫入流程，觀察 LEO 與 HW 的變化。
Let's observe the changes in LEO and HW through a concrete write process.

### 情境 (Scenario)
*   **Topic**: `payments`
*   **Partition**: 0
*   **Replicas**: Broker A (Leader), Broker B (Follower), Broker C (Follower)
*   **Current State**: HW = 5, LEO = 5 (All synced).

### 步驟 1: Producer 寫入訊息 M6 (Step 1: Producer writes message M6)
Producer 發送 M6，要求 `acks=all`。
The Producer sends M6, requesting `acks=all`.

*   **Broker A (Leader)**:
    *   寫入本地 Log。
    *   Writes to local Log.
    *   `LEO` 更新為 6。
    *   `LEO` updates to 6.
    *   `HW` 暫時維持 5 (因為 B 和 C 還沒拿到)。
    *   `HW` remains at 5 temporarily (since B and C haven't received it yet).

### 步驟 2: Follower Fetch (Step 2: Follower Fetch)
Broker B 和 Broker C 發送 Fetch Request 給 Leader。
Broker B and Broker C send Fetch Requests to the Leader.

*   **Broker A (Leader)**:
    *   回傳 M6 給 B 和 C。
    *   Returns M6 to B and C.
    *   Leader 知道 B 和 C 想要讀取 Offset 6，推斷它們目前的 LEO 還是 5。
    *   The Leader knows B and C want to read Offset 6, inferring their current LEO is still 5.

### 步驟 3: Follower 寫入與再次 Fetch (Step 3: Follower Write & Next Fetch)
Broker B 和 C 收到 M6 並寫入磁碟。
Broker B and C receive M6 and write it to disk.

*   **Broker B & C**:
    *   `LEO` 更新為 6。
    *   `LEO` updates to 6.
    *   再次發送 Fetch Request (攜帶 `fetchOffset=6`) 給 Leader。
    *   Send another Fetch Request (carrying `fetchOffset=6`) to the Leader.

### 步驟 4: HW 更新與 Ack (Step 4: HW Update & Ack)
Leader 收到新的 Fetch Request，發現 ISR 中所有副本（A, B, C）的 LEO 都至少是 6。
The Leader receives the new Fetch Requests and sees that the LEO of all replicas in the ISR (A, B, C) is at least 6.

*   **Broker A (Leader)**:
    *   `HW` 更新為 6。
    *   `HW` updates to 6.
    *   向 Producer 回傳 ACK。
    *   Returns ACK to the Producer.
    *   在下一次 Fetch Response 中，將新的 HW 6 告訴 B 和 C。
    *   In the next Fetch Response, informs B and C of the new HW 6.

### 程式碼與配置示例 (Code & Config Example)

```java
// Producer Configuration for Strong Durability
Properties props = new Properties();
props.put("bootstrap.servers", "broker1:9092,broker2:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

// 1. Ensure data is written to all ISR members
props.put("acks", "all"); 

// 2. Retries are critical for transient failures
props.put("retries", Integer.MAX_VALUE); 
props.put("enable.idempotence", "true"); // Ensures exactly-once per partition

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
```

**Broker Side Configuration (`server.properties`):**
```properties
# 3. Minimum replicas required to acknowledge a write with acks=all
min.insync.replicas=2

# 4. Prevent data loss by disabling unclean election
unclean.leader.election.enable=false
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 誤以為 `acks=all` 就萬無一失 (Assuming `acks=all` is Bulletproof)
*   **錯誤 (Pitfall)**: 設定了 `acks=all` 但保持預設的 `min.insync.replicas=1`。
*   **Why**: 如果 ISR 縮減到只剩 Leader 一台，`acks=all` 實際上只寫入了 Leader 就返回成功。若此時 Leader 硬碟損壞，資料將永久遺失。
*   **Correction**: 必須強制設定 `min.insync.replicas >= 2` (當 RF=3 時)。

### 5.2 開啟 Unclean Leader Election (Enabling Unclean Leader Election)
*   **錯誤 (Pitfall)**: 為了追求極致的可用性，將 `unclean.leader.election.enable` 設為 `true`。
*   **Why**: 這允許不在 ISR 中的落後副本（Lagging Replica）成為 Leader。這會導致新 Leader 沒有舊 Leader 的部分資料，且當舊 Leader 恢復後，其多出的資料會被截斷（Log Truncation），造成嚴重的資料遺失與不一致。
*   **Correction**: 除非是對於資料遺失完全不敏感的日誌收集場景，否則生產環境應設為 `false`。

### 5.3 忽略 Consumer 的 `isolation.level` (Ignoring Consumer `isolation.level`)
*   **錯誤 (Pitfall)**: 在使用 Transactional Producer 時，Consumer 仍使用預設的 `read_uncommitted`。
*   **Why**: 雖然這與副本機制不完全相同，但概念類似。Consumer 可能會讀到尚未完全 Commit（或最終 Abort）的 Transaction 訊息。
*   **Correction**: 若涉及 Transaction，Consumer 應設為 `read_committed`，這會讓 Consumer 僅讀取到 LSO (Last Stable Offset) 之前的訊息。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋為什麼 Kafka 需要 High Watermark (HW)？如果 Consumer 直接讀取到 LEO 會發生什麼事？
**Explain why Kafka needs a High Watermark (HW). What would happen if Consumers read up to the LEO directly?**

*   **高分回答要點 (Key Points)**:
    *   **資料一致性 (Consistency)**: HW 確保 Consumer 讀到的資料已經複製到 ISR 中的多數節點。
    *   **防止髒讀 (Prevent Dirty Reads)**: 如果讀到 LEO，該訊息可能尚未複製到 Follower。若 Leader 此時崩潰，新 Leader 可能沒有這條訊息，導致 Consumer 讀到了一條「消失」的訊息（Phantom Read）。
    *   **截斷機制 (Truncation)**: HW 協助 Follower 判斷哪些資料是安全的，哪些在同步過程中可能需要截斷。

### Q2: 在 `replication.factor=3` 且 `min.insync.replicas=2` 的情況下，我們最多能容忍幾台 Broker 故障？
**With `replication.factor=3` and `min.insync.replicas=2`, how many Broker failures can we tolerate?**

*   **高分回答要點 (Key Points)**:
    *   **寫入可用性 (Write Availability)**: 只能容忍 **1** 台故障。因為 3 - 1 = 2，剛好滿足 `min.insync.replicas`。若故障 2 台，剩下 1 台 < 2，Producer 會收到 Exception。
    *   **讀取可用性 (Read Availability)**: 可以容忍 **2** 台故障。只要有 1 台存活，Consumer 依然可以讀取已 Commit 的資料。
    *   **區分讀寫 (Distinguish Read/Write)**: 面試時要明確區分是對「寫入」還是「讀取」的影響。

### Q3: 什麼是 Leader Epoch？它解決了什麼 HW 無法解決的問題？
**What is Leader Epoch? What problem does it solve that HW cannot?**

*   **高分回答要點 (Key Points)**:
    *   **HW 的缺陷 (HW Limitation)**: HW 的更新是異步的，可能會有延遲。在舊版 Kafka 中，若 Follower 依賴 HW 進行日誌截斷，可能會誤刪資料或導致資料不一致。
    *   **Epoch 機制 (Epoch Mechanism)**: 透過 `(Epoch, StartOffset)`，Follower 可以向 Leader 詢問「在這個 Epoch 中你的 Log 結尾在哪裡」，從而精確判定該保留或截斷哪些 Log，避免資料遺失。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **LEO vs HW**: LEO 是寫入進度，HW 是可消費（安全）進度。
2.  **ISR**: 只有 ISR 中的副本有資格選為 Leader，且決定了 HW 的推進。
3.  **Durability Formula**: `acks=all` + `min.insync.replicas > 1` + `unclean.leader.election.enable=false`。
4.  **Availability Trade-off**: 提高 `min.insync.replicas` 會降低寫入可用性（更容易因節點故障而拒寫）。
5.  **Leader Epoch**: 解決副本間資料一致性與截斷問題的現代機制，比單純依賴 HW 更可靠。

### 後續延伸 (Next Steps)
*   **Next Chapter**: 掌握了資料如何安全儲存後，下一章將探討 **Consumer Groups & Rebalancing**，了解 Consumer 如何協作以及在 Broker 變動時如何維持消費穩定性。
*   **Advanced Topic**: 研究 Kafka 的 **Transactions (Exactly-Once Semantics)**，這是在副本機制之上，進一步保證跨 Partition 寫入原子性的功能。