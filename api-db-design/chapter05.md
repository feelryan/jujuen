# Chapter 05: Database Scalability & Partitioning
# 第五章：資料庫擴展性與分片策略

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In the journey from a Senior Engineer to a Principal level, understanding how to scale a database beyond a single node is a critical milestone. While vertical scaling (adding more CPU/RAM) is the easiest first step, it has a hard ceiling. This chapter focuses on horizontal scaling strategies—specifically Replication and Sharding—which are essential for handling petabytes of data and millions of QPS.

從資深工程師邁向首席工程師的過程中，理解如何將資料庫擴展至單一節點之外是一個關鍵里程碑。雖然垂直擴展（增加 CPU/RAM）是最簡單的第一步，但它有硬體極限。本章專注於水平擴展策略——特別是複製（Replication）與分片（Sharding）——這對於處理 PB 級數據與百萬級 QPS 至關重要。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Distinguish between Replication and Sharding:** Understand when to use Read Replicas for read scalability versus Sharding for write scalability and storage capacity.
    **區分複製與分片：** 理解何時使用讀取副本（Read Replicas）來擴展讀取能力，以及何時使用分片（Sharding）來擴展寫入能力與儲存容量。
2.  **Select the Optimal Shard Key:** Analyze the trade-offs between data locality (avoiding scatter-gather) and hotspot prevention (avoiding the celebrity problem).
    **選擇最佳分片鍵（Shard Key）：** 分析資料局部性（避免分散聚合查詢）與熱點預防（避免名人問題）之間的權衡。
3.  **Implement Consistent Hashing:** Explain the mechanics of Consistent Hashing and Virtual Nodes to minimize data movement during cluster resizing.
    **實作一致性雜湊（Consistent Hashing）：** 解釋一致性雜湊與虛擬節點（Virtual Nodes）的機制，以最小化叢集調整時的資料搬移。
4.  **Design for High Availability:** Discuss Multi-Leader and Leaderless replication strategies and their impact on consistency (CAP theorem).
    **設計高可用性架構：** 探討多主（Multi-Leader）與無主（Leaderless）複製策略及其對一致性的影響（CAP 定理）。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Replication vs. Sharding
### 2.1 複製 vs. 分片

**Mental Model:**
Think of **Replication** as "Xeroxing a book." You have multiple identical copies. This allows many people to read the book simultaneously (High Read Throughput), but if you want to change a page, you must update all copies (Write Complexity).
Think of **Sharding** as "Splitting an encyclopedia into volumes (A-D, E-K, ...)." Each volume is unique. This allows you to store more information than fits in one book (Storage Scale) and have different authors write different volumes simultaneously (High Write Throughput).

**心智模型：**
將 **複製（Replication）** 想像成「影印一本書」。你擁有多份完全相同的副本。這允許許多人同時閱讀（高讀取吞吐量），但如果你想修改某一頁，必須更新所有副本（寫入複雜度）。
將 **分片（Sharding）** 想像成「將百科全書拆分成多冊（A-D, E-K...）」。每一冊都是獨一無二的。這允許你儲存超過單本書容量的資訊（儲存擴展），並讓不同的作者同時撰寫不同的冊子（高寫入吞吐量）。

### 2.2 Replication Strategies
### 2.2 複製策略

*   **Single-Leader (Master-Slave):** All writes go to the Leader; reads can go to Followers. Simplest to reason about but the Leader is a write bottleneck.
    **單主複製（Master-Slave）：** 所有寫入都進入 Leader；讀取可由 Followers 處理。邏輯最簡單，但 Leader 是寫入瓶頸。
*   **Multi-Leader (Master-Master):** Writes can go to multiple nodes (often in different datacenters). Increases write availability but introduces **Write Conflicts** that must be resolved (e.g., Last Write Wins).
    **多主複製（Master-Master）：** 寫入可進入多個節點（通常在不同資料中心）。提高了寫入可用性，但引入了必須解決的 **寫入衝突**（例如：最後寫入者勝）。
*   **Leaderless (Dynamo-style):** Writes are sent to multiple nodes; reads query multiple nodes. Uses **Quorum** ($W + R > N$) to ensure consistency.
    **無主複製（Dynamo 風格）：** 寫入發送至多個節點；讀取查詢多個節點。使用 **法定人數（Quorum）**（$W + R > N$）來確保一致性。

### 2.3 Consistent Hashing
### 2.3 一致性雜湊

**The Problem with Modulo Sharding:**
If you use `hash(key) % N` to assign data to $N$ servers, changing $N$ (adding/removing a server) changes the result for almost all keys, requiring massive data migration.

**模數分片（Modulo Sharding）的問題：**
如果你使用 `hash(key) % N` 將資料分配給 $N$ 台伺服器，當 $N$ 改變（新增/移除伺服器）時，幾乎所有鍵的運算結果都會改變，導致大規模的資料遷移。

**The Solution:**
**Consistent Hashing** maps both data and servers onto a circular ring (0 to $2^{32}-1$). A key is assigned to the first server encountered moving clockwise. Adding a node only affects the data between the new node and its predecessor.

**解決方案：**
**一致性雜湊** 將資料與伺服器都映射到一個環狀空間（0 到 $2^{32}-1$）。一個鍵會被分配給順時針方向遇到的第一台伺服器。新增節點只會影響該新節點與其前一個節點之間的資料。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 When to Shard?
### 3.1 何時進行分片？

In a production environment, Sharding is a complexity multiplier. You should generally exhaust other options first:
1.  **Optimization:** Indexing, query tuning, schema optimization.
2.  **Caching:** Redis/Memcached to offload reads.
3.  **Vertical Scaling:** Upgrading AWS RDS instance types.
4.  **Read Replicas:** Offloading read traffic.

Only when you hit **Write Bottlenecks**, **Storage Limits** (e.g., > 2-4 TB per node), or **Connection Limits** should you consider sharding.

在生產環境中，分片會成倍增加複雜度。通常你應該先用盡其他選項：
1.  **最佳化：** 索引、查詢調校、Schema 最佳化。
2.  **快取：** 使用 Redis/Memcached 分擔讀取。
3.  **垂直擴展：** 升級 AWS RDS 實例等級。
4.  **讀取副本：** 分擔讀取流量。

只有當你遇到 **寫入瓶頸**、**儲存限制**（例如單節點 > 2-4 TB）或 **連線數限制** 時，才應考慮分片。

### 3.2 The Impact on ACID
### 3.2 對 ACID 的影響

Sharding often breaks ACID guarantees across partitions:
*   **Atomicity:** Transactions spanning multiple shards (Distributed Transactions) require complex protocols like Two-Phase Commit (2PC), which kills performance.
*   **Consistency:** Foreign keys usually cannot be enforced across shards.
*   **Isolation:** Global serialization is extremely difficult.

System Design often shifts towards **Eventual Consistency** (BASE) when sharding is introduced.

分片通常會破壞跨分區的 ACID 保證：
*   **原子性（Atomicity）：** 跨多個分片的交易（分散式交易）需要像兩階段提交（2PC）這樣複雜的協議，這會嚴重損害效能。
*   **一致性（Consistency）：** 外鍵約束通常無法跨分片強制執行。
*   **隔離性（Isolation）：** 全域序列化極其困難。

當引入分片時，系統設計通常會轉向 **最終一致性**（BASE）。

---

## 4. Walkthrough: Designing a Sharded Order System
## 4. 逐步示例：設計一個分片訂單系統

### Scenario
### 情境
You are designing the backend for a large e-commerce platform. The `Orders` table has reached 5TB, and write latency is spiking during flash sales. We need to shard the database.

你正在為一個大型電商平台設計後端。`Orders` 資料表已達到 5TB，且在快閃特賣期間寫入延遲飆升。我們需要對資料庫進行分片。

### Step 1: Choosing the Shard Key
### 步驟 1：選擇分片鍵

This is the most critical decision. Let's evaluate two candidates: `order_id` vs. `user_id`.

這是最關鍵的決定。讓我們評估兩個候選者：`order_id` 與 `user_id`。

#### Option A: Shard by `order_id`
*   **Strategy:** `hash(order_id) % NumberOfShards`
*   **Pros:** Even distribution of data and write load. No hotspots.
*   **Cons:** To fetch "All orders for User A", you must query **all shards** (Scatter-Gather). This is expensive and has high latency.

#### 選項 A：按 `order_id` 分片
*   **策略：** `hash(order_id) % 分片數量`
*   **優點：** 資料與寫入負載分佈均勻。無熱點。
*   **缺點：** 若要獲取「使用者 A 的所有訂單」，必須查詢 **所有分片**（分散聚合 Scatter-Gather）。這成本高昂且延遲高。

#### Option B: Shard by `user_id`
*   **Strategy:** `hash(user_id) % NumberOfShards`
*   **Pros:** **Data Locality**. All orders for User A are on the same shard. Fetching order history is fast (single shard query).
*   **Cons:** **Data Skew**. Some users buy much more than others. A "Whale" user might fill up a shard.

**Decision:** For an e-commerce order history, read patterns are usually "Show me MY orders". Therefore, **Option B (`user_id`)** is generally preferred, provided we handle potential hotspots.

#### 選項 B：按 `user_id` 分片
*   **策略：** `hash(user_id) % 分片數量`
*   **優點：** **資料局部性**。使用者 A 的所有訂單都在同一個分片上。獲取訂單歷史很快（單一分片查詢）。
*   **缺點：** **資料傾斜**。某些使用者買得比別人多得多。一個「大戶」使用者可能會塞滿一個分片。

**決定：** 對於電商訂單歷史，讀取模式通常是「顯示我的訂單」。因此，**選項 B（`user_id`）** 通常較佳，前提是我們能處理潛在的熱點問題。

### Step 2: Implementing Consistent Hashing (Conceptual Code)
### 步驟 2：實作一致性雜湊（概念程式碼）

To handle adding/removing database nodes without full downtime, we use a Hash Ring with Virtual Nodes.

為了在不完全停機的情況下處理資料庫節點的新增/移除，我們使用帶有虛擬節點的雜湊環。

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        # replicas = Virtual Nodes per physical node
        # replicas = 每個實體節點對應的虛擬節點數
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # Use MD5 or MurmurHash for better distribution than built-in hash()
        # 使用 MD5 或 MurmurHash 以獲得比內建 hash() 更好的分佈
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key):
        if not self.ring:
            return None
        
        hash_val = self._hash(key)
        # Find the first node clockwise (binary search)
        # 順時針尋找第一個節點（二分搜尋）
        idx = bisect.bisect(self.sorted_keys, hash_val)
        
        # Wrap around to the beginning if we hit the end
        # 如果到達末端，則繞回起點
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]

# Usage
ch = ConsistentHash(nodes=["DB_Shard_A", "DB_Shard_B", "DB_Shard_C"])
user_id = "user_12345"
target_shard = ch.get_node(user_id)
print(f"User {user_id} goes to {target_shard}")
```

### Why Virtual Nodes?
### 為何需要虛擬節點？
Without virtual nodes, removing one node (out of 3) dumps 33% of the load onto just *one* neighbor. With virtual nodes (e.g., 100 per server), the load of the removed node is split across the remaining nodes roughly evenly.

如果沒有虛擬節點，移除一個節點（共 3 個）會將 33% 的負載全部倒給 *一個* 鄰居。有了虛擬節點（例如每台伺服器 100 個），移除節點的負載會大致均勻地分散給剩餘的節點。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Timestamp" Shard Key Trap
### 5.1 「時間戳」分片鍵陷阱

**Anti-pattern:** Sharding by `created_at` or a monotonically increasing ID.
**Why it fails:** All new writes go to the *last* shard (the "today" shard). This creates a massive **Write Hotspot**. The other shards sit idle for writes.
**Better Approach:** Use a high-cardinality key like `user_id` or `uuid` for distribution, or use a composite key if time-range queries are strictly required.

**反模式：** 根據 `created_at` 或單調遞增的 ID 進行分片。
**為何失敗：** 所有新寫入都會進入 *最後一個* 分片（「今天」的分片）。這會造成巨大的 **寫入熱點**。其他分片在寫入方面則閒置。
**較佳做法：** 使用高基數（High-cardinality）的鍵如 `user_id` 或 `uuid` 進行分佈，或者如果嚴格需要時間範圍查詢，則使用複合鍵。

### 5.2 The Celebrity Problem (Hot Partition)
### 5.2 名人問題（熱分區）

**Anti-pattern:** Assuming uniform distribution based on `user_id` without handling outliers (e.g., Justin Bieber on Twitter/Instagram).
**Why it fails:** A single key with millions of followers/activities can overwhelm the shard it lives on.
**Better Approach:**
1.  Isolate celebrity data to dedicated hardware.
2.  Add a suffix to the shard key for celebrities (e.g., `user_id_1`, `user_id_2`) to spread their data across multiple shards.

**反模式：** 假設基於 `user_id` 的分佈是均勻的，而未處理極端值（例如 Twitter/Instagram 上的 Justin Bieber）。
**為何失敗：** 單一擁有數百萬追蹤者/活動的鍵可能會壓垮它所在的分片。
**較佳做法：**
1.  將名人資料隔離至專用硬體。
2.  為名人的分片鍵加上後綴（例如 `user_id_1`, `user_id_2`），將其資料分散至多個分片。

### 5.3 Cross-Shard Joins
### 5.3 跨分片關聯（Joins）

**Anti-pattern:** Designing a schema that relies on `JOIN`s between tables that reside on different shards.
**Why it fails:** Database engines cannot perform efficient joins across network boundaries. You end up doing joins in the application layer (fetching huge datasets into memory), which is slow and memory-intensive.
**Better Approach:**
1.  **Denormalization:** Duplicate necessary data into the shard so joins aren't needed.
2.  **Global Tables:** Replicate small, static tables (like `Categories` or `Countries`) to *every* shard.

**反模式：** 設計依賴於位於不同分片之資料表間 `JOIN` 的架構。
**為何失敗：** 資料庫引擎無法跨網路邊界執行高效的關聯。你最終必須在應用層執行關聯（將大量資料集拉入記憶體），這既緩慢又消耗記憶體。
**較佳做法：**
1.  **反正規化（Denormalization）：** 將必要資料複製到分片中，從而不需要關聯。
2.  **全域資料表（Global Tables）：** 將小型、靜態的資料表（如 `Categories` 或 `Countries`）複製到 *每個* 分片。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you migrate a live monolithic database to a sharded architecture with Zero Downtime?
### Q1: 如何在零停機的情況下將線上單體資料庫遷移至分片架構？

**Key Points to Cover:**
*   **Dual Writes (雙寫):** Modify the application to write to *both* the old DB and the new Sharded DBs (new DB writes can be async or sync).
*   **Backfill (回填):** Run a background script to copy historical data from Old to New.
*   **Verification (驗證):** Compare data consistency between Old and New.
*   **Read Switch (切換讀取):** Gradually route read traffic to the New DBs (canary release).
*   **Write Switch (切換寫入):** Stop writing to Old DB, make New DB the source of truth.

**高分回答要點：**
*   **雙寫：** 修改應用程式以寫入 *舊 DB* 和 *新分片 DB*（新 DB 寫入可以是異步或同步）。
*   **回填：** 執行背景腳本將歷史資料從舊 DB 複製到新 DB。
*   **驗證：** 比較舊與新 DB 之間的資料一致性。
*   **切換讀取：** 逐步將讀取流量導向新 DB（金絲雀發布）。
*   **切換寫入：** 停止寫入舊 DB，讓新 DB 成為唯一真理來源（Source of Truth）。

### Q2: In a Leaderless (Dynamo-style) system, how do you handle conflicts?
### Q2: 在無主（Dynamo 風格）系統中，如何處理衝突？

**Key Points to Cover:**
*   **Read Repair:** When a client reads data and detects inconsistency (via version vectors or timestamps), it writes the correct version back to the stale nodes.
*   **Anti-Entropy (Merkle Trees):** Background processes compare data hashes between nodes to detect and fix inconsistencies.
*   **Vector Clocks:** Using logical clocks to detect causality and identify concurrent writes, allowing the client (or app logic) to resolve the conflict.

**高分回答要點：**
*   **讀取修復（Read Repair）：** 當客戶端讀取資料並偵測到不一致（透過版本向量或時間戳）時，將正確版本寫回過時節點。
*   **反熵（Merkle Trees）：** 背景程序比較節點間的資料雜湊值，以偵測並修復不一致。
*   **向量時鐘（Vector Clocks）：** 使用邏輯時鐘來偵測因果關係並識別並發寫入，允許客戶端（或應用邏輯）解決衝突。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
1.  **Replication vs. Sharding:** Replication = Read Scale & Availability. Sharding = Write Scale & Storage.
    **複製 vs. 分片：** 複製 = 讀取擴展與可用性。分片 = 寫入擴展與儲存。
2.  **Shard Key is Destiny:** Choosing the wrong shard key leads to unbalanced loads or expensive scatter-gather queries. `user_id` is often best for consumer apps.
    **分片鍵決定命運：** 選擇錯誤的分片鍵會導致負載不均或昂貴的分散聚合查詢。對於消費者應用，`user_id` 通常是最佳選擇。
3.  **Consistent Hashing:** Essential for elastic scaling. Use Virtual Nodes to ensure even distribution when nodes change.
    **一致性雜湊：** 彈性擴展的關鍵。使用虛擬節點確保節點變動時的分佈均勻。
4.  **No Free Lunch:** Sharding introduces complexity (no cross-shard joins, no global transactions). Avoid it until necessary.
    **天下沒有白吃的午餐：** 分片引入了複雜性（無跨分片關聯、無全域交易）。非必要時應避免使用。
5.  **CAP Theorem:** In distributed databases, you usually trade Consistency for Availability (AP) or vice versa (CP) in the presence of Partitions.
    **CAP 定理：** 在分散式資料庫中，面對分區（Partition）時，通常需要在一致性（Consistency）與可用性（Availability）之間做取捨。

### Next Steps (後續延伸)
*   **Study Distributed Transactions:** Deep dive into Two-Phase Commit (2PC) vs. Sagas pattern. (Next Chapter Material).
    **研讀分散式交易：** 深入探討兩階段提交（2PC）與 Saga 模式。（下一章素材）。
*   **Explore NoSQL Sharding:** Look at how Cassandra (Partition Key + Clustering Key) or MongoDB handles sharding automatically.
    **探索 NoSQL 分片：** 研究 Cassandra（分區鍵 + 叢集鍵）或 MongoDB 如何自動處理分片。
*   **Practice:** Implement a simple Consistent Hashing ring in your favorite language and simulate adding/removing nodes.
    **實作練習：** 使用你熟悉的語言實作一個簡單的一致性雜湊環，並模擬新增/移除節點。