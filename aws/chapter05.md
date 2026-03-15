# 1. 前言與學習目標 (Introduction & Learning Objectives)

在分散式系統中，快取（Caching）是提升讀取效能最直接的手段，但正如 Phil Karlton 所言：「電腦科學中只有兩件難事：快取失效（Cache Invalidation）與命名。」對於資深工程師而言，挑戰不在於如何「使用」Redis 或 CloudFront，而在於如何設計策略以平衡「資料一致性（Consistency）」與「系統可用性（Availability）」。

In distributed systems, caching is the most direct method to improve read performance. However, as Phil Karlton famously said, "There are only two hard things in Computer Science: cache invalidation and naming things." For senior engineers, the challenge lies not in how to "use" Redis or CloudFront, but in designing strategies that balance "Data Consistency" and "System Availability."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **掌握主流快取模式**：深入理解 Cache-Aside、Write-Through、Write-Behind 與 Write-Around 的適用場景與取捨。
    **Master mainstream caching patterns**: Deeply understand the use cases and trade-offs of Cache-Aside, Write-Through, Write-Behind, and Write-Around.
2.  **解決快取並發問題**：能識別並解決 Thundering Herd（驚群效應）、Cache Penetration（快取穿透）與 Cache Avalanche（快取雪崩）。
    **Solve cache concurrency issues**: Identify and resolve Thundering Herd, Cache Penetration, and Cache Avalanche.
3.  **設計 AWS 快取架構**：整合 CloudFront（Edge Caching）與 ElastiCache（Application Caching）來優化全域延遲。
    **Design AWS caching architectures**: Integrate CloudFront (Edge Caching) and ElastiCache (Application Caching) to optimize global latency.
4.  **處理資料一致性**：在 Eventual Consistency 的前提下，設計可靠的快取失效（Invalidation）機制。
    **Handle data consistency**: Design reliable cache invalidation mechanisms under the premise of Eventual Consistency.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 快取的分層模型 (The Layered Model of Caching)

不要將快取視為單一組件，應將其視為資料流動中的「緩衝層」。在 AWS 架構中，快取通常分為三個層次：
Do not view caching as a single component; view it as "buffer layers" in the data flow. In AWS architecture, caching is typically divided into three layers:

1.  **Client-Side**: Browser/App Cache (控制 HTTP Headers, LocalStorage)。
2.  **Edge-Side**: Amazon CloudFront (CDN)，處理靜態資源與動態內容的邊緣計算。
3.  **Server-Side / Application**: Amazon ElastiCache (Redis/Memcached) 或 DynamoDB DAX，處理資料庫查詢結果或計算密集型物件。

**Mental Model**: 想像一個跨國物流系統。CloudFront 是各地的「區域配送中心」，ElastiCache 是工廠旁的「快速發貨倉」，而 RDS/DynamoDB 則是「中央製造工廠」。越靠近用戶，存取越快，但資料可能越舊（Stale）。

**Mental Model**: Imagine a global logistics system. CloudFront represents "regional distribution centers," ElastiCache is the "quick-dispatch warehouse" next to the factory, and RDS/DynamoDB is the "central manufacturing plant." The closer to the user, the faster the access, but the data might be more stale.

## 2.2 Redis vs. Memcached (ElastiCache)

雖然 AWS 兩者都支援，但在現代系統設計面試與實務中，**Redis** 幾乎是預設選擇，除非有極端的簡單 Key-Value 吞吐量需求且不需要持久化。
Although AWS supports both, **Redis** is almost the default choice in modern system design interviews and practice, unless there is an extreme need for simple Key-Value throughput without persistence.

| Feature | Redis | Memcached |
| :--- | :--- | :--- |
| **Data Structures** | Strings, Hashes, Lists, Sets, Sorted Sets, Bitmaps, HyperLogLogs, Geospatial | Simple Key-Value (Strings) |
| **Persistence** | Yes (RDB snapshots, AOF logs) | No (Purely in-memory) |
| **Replication/HA** | Master-Slave replication, Multi-AZ Auto-Failover | No built-in replication (Client-side sharding) |
| **Advanced Use** | Pub/Sub, Lua Scripting, Streams | Simple caching only |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構模式 (Typical Architecture Patterns)

在設計高流量系統（如電商促銷頁、社群 Feed）時，快取策略決定了系統的上限。
When designing high-traffic systems (e.g., e-commerce flash sales, social feeds), caching strategy determines the system's ceiling.

### Cache-Aside (Lazy Loading)
這是最常見的模式。應用程式代碼負責維護快取與資料庫之間的關係。
This is the most common pattern. The application code is responsible for maintaining the relationship between the cache and the database.

*   **讀取 (Read)**: App 查 Cache -> Miss -> App 查 DB -> App 寫入 Cache -> 回傳。
*   **寫入 (Write)**: App 寫入 DB -> App 刪除 (Invalidate) Cache 或 更新 Cache。
*   **優點**: 只有被請求的資料才會進入快取（節省空間），且對 Cache Failure 有韌性（直接查 DB）。
*   **缺點**: Cache Miss 時延遲較高；容易出現資料不一致（Stale Data）。

### Write-Through
應用程式將資料寫入快取，快取負責同步寫入資料庫（或由 App 同時寫入兩者，視實作而定）。
The application writes data to the cache, and the cache is responsible for synchronously writing to the database (or the App writes to both simultaneously, depending on implementation).

*   **優點**: 快取內資料永遠是最新的；讀取效能穩定。
*   **缺點**: 寫入延遲較高（需等兩邊都完成）；不常用的資料也會佔用快取空間。

## 3.2 AWS 實務考量 (AWS Practical Considerations)

在 AWS 環境中，資深工程師需考慮以下維度：
In an AWS environment, senior engineers need to consider the following dimensions:

1.  **Global Data Consistency**: 若使用 DynamoDB Global Tables，需注意跨 Region 的複製延遲（Replication Lag）。若在此之上加了 Redis，必須接受短暫的資料不一致。
    **Global Data Consistency**: If using DynamoDB Global Tables, be aware of cross-region replication lag. If adding Redis on top, you must accept transient data inconsistency.
2.  **ElastiCache Cluster Mode**:
    *   **Disabled**: 單一 Shard，適合讀多寫少，透過 Read Replicas 擴展讀取。
    *   **Enabled**: 資料分片（Sharding），適合寫入量大或資料量超過單機記憶體限制（如 > 100GB）。
3.  **CloudFront Behaviors**: 利用 Query String Forwarding 或 Cookie Forwarding 來精細控制邊緣快取，避免「千人一面」的問題。

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：解決「驚群效應 (Thundering Herd)」
## Scenario: Solving the "Thundering Herd" Problem

**背景 (Context)**:
一個熱門新聞 API，某個 Key (`news:top_stories`) 過期瞬間，數千個併發請求同時發現 Cache Miss，同時打向資料庫，導致 DB CPU 飆升甚至當機。
A popular news API. The moment a key (`news:top_stories`) expires, thousands of concurrent requests discover a Cache Miss simultaneously and hit the database, causing DB CPU to spike or even crash.

### 階段 1: Naive Cache-Aside (有問題的實作)
### Phase 1: Naive Cache-Aside (Problematic Implementation)

```python
def get_top_stories():
    # 嘗試從 Redis 讀取
    data = redis.get("news:top_stories")
    if data:
        return deserialize(data)
    
    # Cache Miss: 危險區域！高併發時這裡會有數千個請求同時執行
    # Cache Miss: Danger Zone! Thousands of requests execute here concurrently
    data = db.query("SELECT * FROM stories...")
    
    # 寫回快取，TTL 60秒
    redis.setex("news:top_stories", 60, serialize(data))
    return data
```

### 階段 2: 使用分佈式鎖 (Distributed Lock)
### Phase 2: Using Distributed Lock

利用 Redis 的原子操作（Atomic Operations）確保只有一個請求去查 DB，其他請求等待。
Use Redis atomic operations to ensure only one request queries the DB, while others wait.

```python
import time

def get_top_stories_safe():
    cache_key = "news:top_stories"
    data = redis.get(cache_key)
    if data:
        return deserialize(data)
    
    # 嘗試獲取鎖 (Try to acquire lock)
    # nx=True (Only set if not exists), ex=5 (Lock expires in 5s to prevent deadlocks)
    lock_acquired = redis.set("lock:" + cache_key, "1", nx=True, ex=5)
    
    if lock_acquired:
        try:
            # 我是選中的執行緒，負責查 DB
            data = db.query("SELECT * FROM stories...")
            redis.setex(cache_key, 60, serialize(data))
            return data
        finally:
            # 釋放鎖 (Release lock)
            redis.delete("lock:" + cache_key)
    else:
        # 未獲取鎖，稍作等待後重試 (Wait and retry)
        time.sleep(0.1)
        return get_top_stories_safe()
```

### 階段 3: 邏輯過期 (Logical Expiration / Probabilistic Early Recomputation)
### Phase 3: Logical Expiration / Probabilistic Early Recomputation

鎖機制會增加延遲。另一種資深做法是：**不要讓 Key 真的從 Redis 消失**。
Locking adds latency. Another senior approach is: **Never let the key actually expire from Redis**.

1.  Redis TTL 設為「永久」或很長的時間。
2.  在 Value 內部存一個 `expire_at` timestamp。
3.  讀取時，若發現 `now > expire_at`，回傳舊資料，但**非同步**觸發一個背景任務去更新快取。

**Trade-off**: 用戶可能看到幾秒鐘的舊資料，但系統吞吐量極其穩定，完全避免了 Thundering Herd。
**Trade-off**: Users might see stale data for a few seconds, but system throughput is extremely stable, completely avoiding the Thundering Herd.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 快取穿透 (Cache Penetration)
*   **描述**: 惡意用戶不斷查詢「不存在的 Key」（如 id=-1）。Cache 查不到，DB 也查不到，導致請求每次都穿透到 DB。
*   **Description**: Malicious users constantly query "non-existent Keys" (e.g., id=-1). Cache misses, DB misses, causing every request to penetrate to the DB.
*   **Solution**:
    *   **Cache Null Object**: 將「不存在」的結果也快取起來（TTL 設短一點）。
    *   **Bloom Filter**: 在快取層之前加一個 Bloom Filter，快速判斷 Key 是否可能存在。

## 5.2 快取雪崩 (Cache Avalanche)
*   **描述**: 大量 Key 設了相同的 TTL，導致它們在同一時間集體過期，DB 瞬間承受巨大壓力。
*   **Description**: A large number of keys are set with the same TTL, causing them to expire collectively at the same time, putting immense pressure on the DB instantly.
*   **Solution**:
    *   **Jitter (隨機抖動)**: 設定 TTL 時加上隨機值（例如 `TTL = 60s + random(0-10s)`）。

## 5.3 誤用 Redis 做為主要資料庫 (Misusing Redis as Primary DB)
*   **描述**: 過度依賴 Redis 的持久化，而沒有將資料寫入 RDS/DynamoDB。
*   **Description**: Over-relying on Redis persistence without writing data to RDS/DynamoDB.
*   **Why it's bad**: Redis 的 RDB/AOF 在極端崩潰下仍可能遺失資料；且記憶體成本遠高於磁碟。
*   **Correction**: Redis 應視為 Ephemeral（短暫的），資料必須有 Durable 的 Source of Truth。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何保證 Cache 與 DB 的資料一致性？
## Q1: How do you ensure data consistency between Cache and DB?

**高分回答要點 (Key Points for High Score)**:
*   承認**強一致性 (Strong Consistency)** 在分散式快取中極難達成，通常追求 **最終一致性 (Eventual Consistency)**。
*   討論 **Cache-Aside** 的寫入順序：先更新 DB，再**刪除 (Delete)** Cache（而非更新 Cache）。
    *   *為什麼刪除比更新好？* 避免兩個並發寫入導致 Cache 存了舊值（Race Condition）。
*   提及 **Delayed Double Delete**：為了處理 DB 主從延遲，可以在刪除 Cache 後，過幾秒再刪除一次。
*   進階：使用 **CDC (Change Data Capture)** 如 AWS DMS 或 DynamoDB Streams，監聽 DB 變更日誌來非同步更新/刪除快取。

## Q2: 設計一個 Global Leaderboard (排行榜)，要求即時性高。
## Q2: Design a Global Leaderboard requiring high real-time performance.

**高分回答要點**:
*   直接使用 **Redis Sorted Sets (ZSET)**。
*   操作：`ZADD` 更新分數，`ZREVRANGE` 取得前 N 名。
*   架構：使用 **ElastiCache for Redis with Global Datastore** 進行跨 Region 複製。
*   邊界條件：若用戶量極大，可能需要對 Key 進行 Sharding（如 `leaderboard_level1`, `leaderboard_level2`），或者使用 Write-Behind 策略彙總分數後再寫入。

## Q3: 什麼時候該用 CloudFront 什麼時候該用 ElastiCache？
## Q3: When should you use CloudFront vs. ElastiCache?

**高分回答要點**:
*   **CloudFront**: 針對 HTTP Response。適合靜態資源（圖片、JS）或公開的、對每個人都一樣的 API 回應（Public Content）。靠近用戶，減少網路延遲。
*   **ElastiCache**: 針對 Application Data Objects。適合私有資料（User Profile）、計算結果、Session Store、或需要複雜資料結構操作的場景。位於 VPC 內部，減少 DB 負載。
*   **混合使用**: API Gateway + Lambda 架構中，常同時使用兩者（CloudFront 快取 API 回應，Lambda 內部讀取 ElastiCache）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **Cache-Aside** 是最通用的模式，記住「先更 DB，後刪 Cache」。
2.  **Thundering Herd** 需透過 Locking 或 Logical Expiration 解決，否則擴展性會受限。
3.  **Redis** 不僅是 KV Store，善用 Sorted Sets、Hashes 等結構可簡化應用邏輯。
4.  **AWS ElastiCache** 的 Cluster Mode 與 Global Datastore 是大規模系統的基石。
5.  **TTL + Jitter** 是防止 Cache Avalanche 的簡單有效手段。

## 下一步 (Next Steps)
*   **延伸閱讀**: 深入研究 **Redis Persistence (RDB vs AOF)** 的底層機制，這在除錯 Redis 重啟資料遺失時非常重要。
*   **實作練習**: 在 AWS 上建立一個 Lambda 函數，透過 VPC Endpoint 連接 ElastiCache，並實作一個帶有 Distributed Lock 的計數器。
*   **下一章預告**: 掌握了快取後，我們將探討如何處理寫入瓶頸與非同步處理——**訊息佇列與事件驅動架構 (SQS, SNS, Kinesis)**。