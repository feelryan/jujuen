# Chapter 06: Caching Strategies & Performance Optimization
# 第六章：快取策略與效能優化

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In high-concurrency systems, caching is often the first line of defense for database stability, and indexing is the cornerstone of query performance. For Senior Engineers, the challenge is not just "using a cache," but choosing the right consistency model and preventing catastrophic failures under load.
在高併發系統中，快取（Cache）往往是保護資料庫穩定性的第一道防線，而索引（Indexing）則是查詢效能的基石。對於資深工程師而言，挑戰不在於「使用快取」，而在於選擇正確的一致性模型，並防止系統在負載下發生災難性故障。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Select the appropriate caching pattern** (Cache-Aside, Write-Through, Write-Back) based on read/write ratios and consistency requirements.
    根據讀寫比例與一致性需求，**選擇合適的快取模式**（Cache-Aside, Write-Through, Write-Back）。
2.  **Mitigate advanced caching failures**, specifically Cache Penetration, Cache Breakdown (Stampede), and Cache Avalanche.
    **緩解進階快取失效問題**，特別是快取穿透（Penetration）、快取擊穿（Breakdown/Stampede）與快取雪崩（Avalanche）。
3.  **Optimize Database Indexing** by applying the "Leftmost Prefix Rule," understanding Covering Indexes, and avoiding common indexing anti-patterns.
    **優化資料庫索引**，應用「最左前綴原則（Leftmost Prefix Rule）」，理解覆蓋索引（Covering Index），並避免常見的索引反模式。
4.  **Design for Observability**, knowing what metrics to monitor (Hit Rate, Eviction Rate, Latency) to maintain cache health.
    **設計可觀測性**，了解應監控哪些指標（命中率、驅逐率、延遲）以維持快取健康。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Memory Hierarchy Analogy
### 2.1 記憶體階層類比

Think of your system like a CPU's memory hierarchy. Local Cache (in-memory variable) is L1 cache (fastest, smallest, per-instance). Distributed Cache (Redis/Memcached) is L2/RAM (fast, shared). The Database is the Disk (slow, persistent, source of truth).
將你的系統想像成 CPU 的記憶體階層。本地快取（In-memory 變數）是 L1 快取（最快、最小、單一實體專用）。分散式快取（Redis/Memcached）是 L2/RAM（快速、共享）。資料庫則是硬碟（慢速、持久化、單一真理來源）。

**Key Mental Shift:** Caching is trading **Consistency** (temporarily) and **Memory Cost** for **Latency** and **Throughput**.
**關鍵思維轉變：** 快取本質上是用**一致性**（暫時的）與**記憶體成本**來換取**延遲**與**吞吐量**的優化。

### 2.2 Caching Patterns Definitions
### 2.2 快取模式定義

| Pattern | Description | Best For | Pros/Cons |
| :--- | :--- | :--- | :--- |
| **Cache-Aside (Lazy Loading)** | Application talks to Cache and DB. If cache miss, App reads DB and updates Cache. <br> 應用程式分別與 Cache 和 DB 溝通。若快取未命中，由 App 讀取 DB 並更新 Cache。 | Read-heavy workloads (General purpose). <br> 讀多寫少的場景（通用型）。 | **Pros:** Resilient to cache failure. <br> **Cons:** Potential inconsistency (stale data). |
| **Read/Write-Through** | Application treats Cache as the main data store. Cache module manages DB reads/writes synchronously. <br> 應用程式將 Cache 視為主要資料存儲。Cache 模組同步管理 DB 的讀寫。 | Heavy read/write workloads requiring simpler app logic. <br> 需要簡化應用邏輯的高讀寫場景。 | **Pros:** Clean application code. <br> **Cons:** Higher write latency (2 hops), complex infrastructure setup. |
| **Write-Back (Write-Behind)** | Application writes to Cache. Cache acknowledges immediately and asynchronously writes to DB later. <br> 應用程式寫入 Cache。Cache 立即確認，隨後非同步寫入 DB。 | Write-heavy workloads (e.g., Counters, Analytics). <br> 寫多讀少的場景（如計數器、分析數據）。 | **Pros:** Lowest write latency, high throughput. <br> **Cons:** Data loss risk if cache crashes before flush. |

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production environment, caching is rarely a single layer. It is often a multi-tier architecture designed to protect the database at all costs.
在生產環境中，快取很少是單一層級的。它通常是一個多層架構，旨在不惜一切代價保護資料庫。

### 3.1 Multi-Level Caching Architecture
### 3.1 多級快取架構

1.  **Client/Browser:** HTTP Caching (Headers: `Cache-Control`, `ETag`).
    **客戶端/瀏覽器：** HTTP 快取。
2.  **CDN (Content Delivery Network):** Static assets and cached API responses at the edge.
    **CDN：** 邊緣節點的靜態資源與 API 回應快取。
3.  **Local Cache (In-Process):** Libraries like Guava (Java) or simple Maps (Go/Node). Extremely fast but creates consistency issues between service replicas.
    **本地快取（行程內）：** 如 Guava (Java) 或簡單的 Map (Go/Node)。極快，但會導致服務副本間的一致性問題。
4.  **Distributed Cache:** Redis or Memcached. The shared state for all service instances.
    **分散式快取：** Redis 或 Memcached。所有服務實例的共享狀態。

### 3.2 Impact on System Properties
### 3.2 對系統特性的影響

*   **Availability:** Caching absorbs traffic spikes. If the cache goes down, the DB might be crushed (see *Cache Avalanche*).
    **可用性：** 快取吸收流量峰值。如果快取掛掉，DB 可能會被壓垮（參見*快取雪崩*）。
*   **Consistency:** The hardest part. Using `TTL` (Time-To-Live) provides "Eventual Consistency." For strict consistency, you must invalidate the cache on DB writes.
    **一致性：** 最困難的部分。使用 `TTL`（存活時間）提供「最終一致性」。若需嚴格一致性，必須在寫入 DB 時讓快取失效（Invalidate）。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: The "Hot Product" Inventory Problem
### 場景：「熱門商品」庫存問題

Imagine an E-commerce system during a flash sale. Thousands of users request the details of `Product_ID: 123` simultaneously.
想像一個電商系統在進行快閃特賣。成千上萬的使用者同時請求 `Product_ID: 123` 的詳細資訊。

#### Evolution 1: Naive Cache-Aside
#### 演進 1：樸素的 Cache-Aside

```python
def get_product(product_id):
    # 1. Check Cache
    data = redis.get(f"product:{product_id}")
    if data:
        return data
    
    # 2. If miss, read DB
    data = db.query(f"SELECT * FROM products WHERE id = {product_id}")
    
    # 3. Update Cache
    redis.set(f"product:{product_id}", data, ttl=300)
    return data
```

**Issue:** **Cache Breakdown (Stampede)**. If the key expires at `t=0`, and 10,000 requests arrive at `t=0.01`, all 10,000 will miss the cache and hit the DB simultaneously.
**問題：** **快取擊穿（Stampede）**。如果 Key 在 `t=0` 過期，而 10,000 個請求在 `t=0.01` 到達，這 10,000 個請求都會未命中快取並同時衝擊 DB。

#### Evolution 2: Mutex Locking (The Senior Solution)
#### 演進 2：互斥鎖（資深解法）

We allow only *one* thread to rebuild the cache. Others wait or return stale data.
我們只允許*一個*執行緒去重建快取。其他的等待或返回舊資料。

```python
import time

def get_product_robust(product_id):
    key = f"product:{product_id}"
    data = redis.get(key)
    
    if data:
        return data
        
    # Cache Miss: Try to acquire a lock
    lock_key = f"lock:product:{product_id}"
    # setnx (SET if Not eXists) acts as a lock
    if redis.set(lock_key, "1", nx=True, ex=5): 
        try:
            # I am the chosen one. Fetch from DB.
            data = db.query(f"SELECT * FROM products WHERE id = {product_id}")
            
            # Handle "Cache Penetration" (Data doesn't exist in DB)
            if not data:
                # Cache a null value with short TTL
                redis.set(key, "NULL", ttl=60) 
            else:
                redis.set(key, data, ttl=300)
        finally:
            redis.delete(lock_key) # Release lock
    else:
        # Lock is held by someone else. Wait and retry.
        time.sleep(0.1)
        return get_product_robust(product_id)
        
    return data
```

**Key Improvements:**
**關鍵改進：**
1.  **Mutex Lock:** Prevents the "Thundering Herd."
    **互斥鎖：** 防止「驚群效應」。
2.  **Null Object Pattern:** Solves **Cache Penetration** (users querying non-existent IDs to bypass cache and attack DB).
    **空物件模式：** 解決**快取穿透**（使用者查詢不存在的 ID 以繞過快取攻擊 DB）。

#### Database Indexing Optimization
#### 資料庫索引優化

Assuming the query is: `SELECT * FROM orders WHERE user_id = 123 AND status = 'PAID' AND created_at > '2023-01-01'`.
假設查詢為：`SELECT * FROM orders WHERE user_id = 123 AND status = 'PAID' AND created_at > '2023-01-01'`。

*   **Bad Index:** Three separate indexes on `user_id`, `status`, `created_at`. The DB engine has to merge them (slow) or pick one.
    **糟糕的索引：** 在 `user_id`、`status`、`created_at` 上建立三個獨立索引。DB 引擎必須合併它們（慢）或只選一個。
*   **Good Index (Composite):** `INDEX (user_id, status, created_at)`.
    **好的索引（複合）：** `INDEX (user_id, status, created_at)`。
*   **Why?** The **Leftmost Prefix Rule**. The B+ Tree is sorted by `user_id` first, then `status`, then `created_at`.
    **為什麼？** **最左前綴原則**。B+ Tree 首先按 `user_id` 排序，然後是 `status`，最後是 `created_at`。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Update Cache" Trap
### 5.1 「直接更新快取」陷阱

*   **Anti-pattern:** Updating the cache value directly after a DB write (`db.write(); cache.set();`).
    **反模式：** 在 DB 寫入後直接更新快取值（`db.write(); cache.set();`）。
*   **Why it's bad:** Race conditions. If two threads write concurrently, Thread A might write DB, Thread B writes DB, Thread B updates Cache, Thread A updates Cache. Result: Cache has old data (A), DB has new data (B).
    **為何不好：** 競爭條件（Race conditions）。若兩個執行緒併發寫入，執行緒 A 寫入 DB，執行緒 B 寫入 DB，執行緒 B 更新 Cache，執行緒 A 更新 Cache。結果：Cache 是舊資料 (A)，DB 是新資料 (B)。
*   **Solution:** **Cache Invalidation** (`db.write(); cache.delete();`). It is safer to force a re-read than to overwrite with potentially wrong data.
    **解法：** **刪除快取**（`db.write(); cache.delete();`）。強制重讀比覆蓋潛在的錯誤資料更安全。

### 5.2 Ignoring Cache Avalanche
### 5.2 忽視快取雪崩

*   **Anti-pattern:** Setting the same TTL (e.g., 1 hour) for all keys loaded at startup.
    **反模式：** 為啟動時載入的所有 Key 設定相同的 TTL（例如 1 小時）。
*   **Why it's bad:** At T+1 hour, all keys expire simultaneously. DB spikes to 100% CPU.
    **為何不好：** 在 T+1 小時，所有 Key 同時過期。DB CPU 飆升至 100%。
*   **Solution:** Add **Jitter** (Randomness) to TTL. `TTL = 3600 + random(0, 300)`.
    **解法：** 在 TTL 加入**抖動**（隨機性）。`TTL = 3600 + random(0, 300)`。

### 5.3 Indexing Every Column
### 5.3 對每個欄位建立索引

*   **Anti-pattern:** Adding indexes to every column "just in case."
    **反模式：** 為了「以防萬一」對每個欄位都加索引。
*   **Why it's bad:** Every `INSERT/UPDATE/DELETE` requires updating the B+ Trees of all indexes. This kills write performance and increases disk usage.
    **為何不好：** 每次 `INSERT/UPDATE/DELETE` 都需要更新所有索引的 B+ Tree。這會扼殺寫入效能並增加磁碟用量。
*   **Solution:** Index only based on actual query patterns (WHERE, ORDER BY, GROUP BY).
    **解法：** 僅根據實際查詢模式（WHERE, ORDER BY, GROUP BY）建立索引。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you ensure consistency between Redis and MySQL?
### Q1: 你如何確保 Redis 與 MySQL 之間的一致性？

*   **Key Points:**
    *   Explain **Cache-Aside** with **Delete on Write** (Cache Invalidation).
    *   Discuss the edge case: DB updated, but Cache deletion fails.
    *   **Advanced Answer:** Use **Binlog Parsing** (e.g., Canal, Debezium) to asynchronously delete/update cache. This decouples the app from cache consistency logic and ensures eventual consistency even if the app crashes.
*   **得分要點：**
    *   解釋搭配**寫入時刪除**（Cache Invalidation）的 **Cache-Aside** 模式。
    *   討論邊界情況：DB 更新成功，但 Cache 刪除失敗。
    *   **高分回答：** 使用 **Binlog 解析**（如 Canal, Debezium）來非同步刪除/更新快取。這將應用程式與快取一致性邏輯解耦，並確保即使應用程式崩潰也能達到最終一致性。

### Q2: Why is `SELECT *` bad for performance, even with an index?
### Q2: 為什麼 `SELECT *` 對效能不好，即使有索引？

*   **Key Points:**
    *   It prevents **Covering Index** usage. If you select fields not in the index, the DB must perform a **Key Lookup / Bookmark Lookup** (回表) to fetch the full row from the clustered index (primary storage).
    *   Increases network bandwidth and memory usage.
*   **得分要點：**
    *   它阻礙了**覆蓋索引**（Covering Index）的使用。如果你選取的欄位不在索引中，DB 必須執行**回表**（Key Lookup）操作，從叢集索引（主要存儲）中抓取完整資料列。
    *   增加網路頻寬與記憶體使用量。

### Q3: Design a system to handle millions of "Likes" per second.
### Q3: 設計一個每秒處理數百萬次「按讚」的系統。

*   **Key Points:**
    *   Direct DB writes will fail.
    *   Use **Write-Back** strategy. Accumulate counts in Redis (atomic `INCR`).
    *   Persist to DB periodically (e.g., every 10 seconds) or when a threshold is reached.
    *   Address the risk of data loss (acceptable for "Likes", not acceptable for "Payments").
*   **得分要點：**
    *   直接寫入 DB 會失敗。
    *   使用 **Write-Back** 策略。在 Redis 中累積計數（原子操作 `INCR`）。
    *   週期性（如每 10 秒）或達到閾值時持久化到 DB。
    *   說明資料遺失的風險（對「按讚」可接受，對「支付」不可接受）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap (記憶錨點)
*   **Cache-Aside** is the default standard; prefer **Deleting** cache over Updating it.
    **Cache-Aside** 是預設標準；優先選擇**刪除**快取而非更新它。
*   **Stampede (Breakdown)** happens when a hot key expires; fix with **Mutex Locks**.
    **擊穿（Stampede）** 發生在熱點 Key 過期時；用**互斥鎖**解決。
*   **Penetration** is querying non-existent data; fix with **Bloom Filters** or **Caching Null**.
    **穿透（Penetration）** 是查詢不存在的資料；用**布隆過濾器**或**快取空值**解決。
*   **Avalanche** is mass expiration; fix with **TTL Jitter**.
    **雪崩（Avalanche）** 是大規模過期；用 **TTL 抖動**解決。
*   **Leftmost Prefix Rule** is critical for Composite Indexes.
    **最左前綴原則**對複合索引至關重要。

### Next Steps (後續延伸)
*   **Database Sharding & Partitioning:** Now that you've optimized a single node, how do you scale horizontally? (Chapter 07).
    **資料庫分片與分區：** 既然優化了單一節點，該如何水平擴展？（第七章）。
*   **Distributed Consensus:** Deep dive into how Redis Sentinel or Cluster maintains consistency (Raft/Gossip protocols).
    **分散式共識：** 深入研究 Redis Sentinel 或 Cluster 如何維持一致性（Raft/Gossip 協定）。