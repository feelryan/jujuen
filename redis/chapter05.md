# Chapter 05: 快取設計模式與常見陷阱
# Chapter 05: Caching Patterns & Common Pitfalls

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，引入 Redis 不僅僅是為了「加速」，更是一場關於**資料一致性（Data Consistency）**與**系統可用性（Availability）**的權衡賽局。本章將超越基礎的 `GET/SET` 操作，深入探討在分散式系統中如何正確實作快取策略。
For senior engineers, introducing Redis is not just about "speedup"; it is a trade-off game involving **Data Consistency** and **Availability**. This chapter goes beyond basic `GET/SET` operations to explore how to correctly implement caching strategies in distributed systems.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇快取模式**：根據讀寫比例與一致性需求，在 Cache-Aside, Write-Through, Write-Back 等策略中做出架構決策。
    **Select caching patterns precisely**: Make architectural decisions among Cache-Aside, Write-Through, and Write-Back strategies based on read/write ratios and consistency requirements.
2.  **解決快取失效風暴**：識別並修復 Cache Penetration（穿透）、Cache Avalanche（雪崩）與 Cache Stampede（擊穿）等高併發問題。
    **Solve cache failure storms**: Identify and fix high-concurrency issues like Cache Penetration, Cache Avalanche, and Cache Stampede.
3.  **處理資料一致性挑戰**：理解並實作「延遲雙刪（Delayed Double Delete）」或「邏輯過期（Logical Expiration）」來降低 DB 與 Cache 不一致的風險。
    **Handle data consistency challenges**: Understand and implement strategies like "Delayed Double Delete" or "Logical Expiration" to minimize inconsistency risks between the DB and Cache.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 快取讀寫策略 (Caching Strategies)
### 2.1 Caching Strategies

在系統設計中，快取與資料庫的互動模式決定了系統的複雜度與一致性級別。
In system design, the interaction pattern between the cache and the database determines the system's complexity and consistency level.

*   **Cache-Aside (Lazy Loading)**:
    *   **定義**：應用程式負責協調。讀取時先查 Cache，沒命中則查 DB 並回寫 Cache；寫入時先更新 DB，再**刪除** Cache。
    *   **Definition**: The application orchestrates the flow. On read, check Cache; if miss, check DB and populate Cache. On write, update DB first, then **delete** the Cache.
    *   **適用場景**：大多數一般用途的 Web 應用（Read-heavy）。
    *   **Use Case**: Most general-purpose web applications (Read-heavy).

*   **Write-Through**:
    *   **定義**：應用程式將 Cache 視為主要資料儲存，Cache 負責同步更新 DB。寫入時同時寫入 Cache 與 DB。
    *   **Definition**: The application treats the Cache as the main data store, and the Cache is responsible for synchronously updating the DB. Writes update both Cache and DB simultaneously.
    *   **適用場景**：需要強一致性且不允許資料遺失，但寫入延遲會較高。
    *   **Use Case**: Scenarios requiring strong consistency and zero data loss, but with higher write latency.

*   **Write-Back (Write-Behind)**:
    *   **定義**：寫入時只更新 Cache 並立即返回，Cache 非同步地（Asynchronously）批次更新 DB。
    *   **Definition**: Writes update only the Cache and return immediately; the Cache asynchronously batch-updates the DB.
    *   **適用場景**：寫入量極大（Write-heavy）的場景，如計數器、日誌聚合，但需承擔 Cache 當機導致資料遺失的風險。
    *   **Use Case**: Extremely write-heavy scenarios like counters or log aggregation, accepting the risk of data loss if the Cache crashes.

### 2.2 快取失效三劍客 (The Trio of Cache Failures)
### 2.2 The Trio of Cache Failures

這三個術語在面試與實務中經常被混淆，需清楚區分：
These three terms are often confused in interviews and practice, so distinct differentiation is required:

1.  **Cache Penetration (穿透)**:
    *   查詢**不存在**的資料。請求穿過 Cache 直接打到 DB，且因資料不存在而無法回寫 Cache，導致每次請求都打擊 DB。
    *   Querying for **non-existent** data. Requests bypass the Cache and hit the DB directly. Since the data doesn't exist, it's never cached, causing every request to hammer the DB.
2.  **Cache Avalanche (雪崩)**:
    *   大量的 Key 在**同一時間過期**，或者 Redis 節點當機。導致瞬間流量全部轉向 DB。
    *   A massive number of keys **expire at the same time**, or a Redis node crashes. This causes instantaneous traffic to shift entirely to the DB.
3.  **Cache Stampede / Hotspot Invalid (擊穿)**:
    *   **單一**熱點 Key（Hot Key）過期，但在重建快取完成前，大量併發請求同時打入 DB。
    *   A **single** hot key expires, but before the cache is rebuilt, a large volume of concurrent requests hit the DB simultaneously.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 一致性難題：刪除 vs 更新 (The Consistency Dilemma: Delete vs. Update)
### 3.1 The Consistency Dilemma: Delete vs. Update

在 Cache-Aside 模式中，為什麼標準做法是「更新 DB 後**刪除** Cache」，而不是「更新 DB 後**更新** Cache」？
In the Cache-Aside pattern, why is the standard practice to "update DB then **delete** Cache" rather than "update DB then **update** Cache"?

*   **Race Condition（競態條件）**: 如果有兩個併發寫入請求 A 和 B。A 先更新 DB，B 後更新 DB；但可能發生 B 先更新 Cache，A 後更新 Cache。這會導致 Cache 存的是舊值（髒資料）。
    **Race Condition**: If there are two concurrent write requests, A and B. A updates DB first, B updates DB later; however, it's possible that B updates the Cache first, and A updates the Cache later. This results in the Cache holding an old value (dirty data).
*   **資源浪費 (Resource Waste)**: 如果該資料寫多讀少，頻繁計算並更新 Cache 是無效功，不如等到有人讀取時再計算（Lazy Loading）。
    **Resource Waste**: If the data is write-heavy and read-rarely, frequently calculating and updating the Cache is wasted effort. It's better to wait until someone reads it to calculate (Lazy Loading).

### 3.2 系統擴展性影響 (Impact on Scalability)
### 3.2 Impact on Scalability

在微服務架構中，Redis 通常作為 Shared State 或 Sidecar 存在。
In microservices architecture, Redis usually exists as Shared State or a Sidecar.

*   **DB 保護傘**: 設計良好的快取層能吸收 90% 以上的讀流量。若設計不當（如發生雪崩），DB 會瞬間崩潰，導致連鎖反應（Cascading Failure）。
    **DB Umbrella**: A well-designed cache layer can absorb over 90% of read traffic. If poorly designed (e.g., Avalanche occurs), the DB can crash instantly, causing a Cascading Failure.
*   **延遲與抖動**: 引入 Cache 會降低平均延遲，但需注意 P99 延遲。當 Cache Miss 或發生 Stampede 時，該次請求的延遲會顯著增加（Cache 查詢時間 + DB 查詢時間 + 回寫時間）。
    **Latency and Jitter**: Introducing Cache lowers average latency, but watch out for P99 latency. When a Cache Miss or Stampede occurs, the latency for that request increases significantly (Cache query time + DB query time + Write-back time).

---

## 4. 逐步示例：解決 Cache Stampede (擊穿)
## 4. Walkthrough: Solving Cache Stampede

### 場景 (Scenario)
### Scenario

你負責一個電商平台的「秒殺商品詳情頁」。該商品的 Key (`product:12345`) 是極熱點資料（QPS 10,000+）。當該 Key 過期時，若 10,000 個請求同時發現 Cache Miss，它們會同時查詢 DB，導致 DB CPU 飆升。
You are responsible for a "Flash Sale Product Detail Page" on an e-commerce platform. The product Key (`product:12345`) is extremely hot data (QPS 10,000+). When this Key expires, if 10,000 requests simultaneously encounter a Cache Miss, they will all query the DB at once, causing the DB CPU to spike.

### 解決方案演進 (Solution Evolution)
### Solution Evolution

#### 1. Naive Approach (Cache-Aside)
最直覺的寫法，但在高併發下會失敗。
The most intuitive approach, but fails under high concurrency.

```python
def get_product(product_id):
    key = f"product:{product_id}"
    data = redis.get(key)
    if data:
        return data
    
    # DANGER ZONE: 10,000 threads can enter here simultaneously
    data = db.query(product_id)
    redis.setex(key, 3600, data)
    return data
```

#### 2. Mutex Lock (互斥鎖)
利用 Redis 的 `SETNX` 或類似機制，保證只有一個執行緒去重建快取，其他執行緒等待。
Use Redis `SETNX` or similar mechanisms to ensure only one thread rebuilds the cache, while others wait.

```python
import time
import uuid

def get_product_safe(product_id):
    key = f"product:{product_id}"
    data = redis.get(key)
    if data:
        return data
    
    # Lock key specifically for rebuilding cache
    lock_key = f"lock:product:{product_id}"
    unique_id = str(uuid.uuid4())
    
    # Try to acquire lock (set if not exists, expire in 5s to prevent deadlock)
    if redis.set(lock_key, unique_id, nx=True, ex=5):
        try:
            # Double check (someone might have just finished rebuilding)
            data = redis.get(key)
            if data:
                return data
            
            # Rebuild from DB
            data = db.query(product_id)
            redis.setex(key, 3600, data)
            return data
        finally:
            # Release lock (Lua script is safer, simplified here)
            if redis.get(lock_key) == unique_id:
                redis.delete(lock_key)
    else:
        # Failed to acquire lock, wait and retry
        time.sleep(0.1)
        return get_product_safe(product_id)
```

*   **Trade-off**: 雖然保護了 DB，但並發請求會被阻塞（Blocking），導致使用者端延遲增加。
*   **Trade-off**: While it protects the DB, concurrent requests are blocked, increasing client-side latency.

#### 3. Logical Expiration (邏輯過期 / Soft TTL)
不依賴 Redis 的 TTL 讓資料真正消失。而是在 Value 內部存儲一個「邏輯過期時間」。
Do not rely on Redis TTL to make data actually disappear. Instead, store a "logical expiration time" inside the Value.

*   **邏輯**: 
    1. 查詢 Redis，發現資料存在但「邏輯上」已過期。
    2. 返回舊資料給使用者（保證可用性）。
    3. 非同步（Asynchronously）啟動一個執行緒去更新 DB 並重設 Redis。
*   **Logic**:
    1. Query Redis, find data exists but is "logically" expired.
    2. Return the stale data to the user (ensuring availability).
    3. Asynchronously start a thread to update the DB and reset Redis.

這通常是 Big Tech 處理極熱點資料的首選方案，因為它實現了 **Zero Downtime**。
This is often the preferred solution in Big Tech for extremely hot data because it achieves **Zero Downtime**.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 缺乏隨機性的過期時間 (Lack of Jitter in TTL)
### 5.1 Lack of Jitter in TTL

*   **錯誤**: 設定固定 TTL（例如所有商品快取都在 1 小時後過期）。
*   **Mistake**: Setting a fixed TTL (e.g., all product caches expire in exactly 1 hour).
*   **後果**: 導致 **Cache Avalanche**。週期性地出現 DB 負載尖峰。
*   **Consequence**: Causes **Cache Avalanche**. Periodic spikes in DB load occur.
*   **修正**: `TTL = Base_Time + random(0, 300) seconds`。
*   **Fix**: `TTL = Base_Time + random(0, 300) seconds`.

### 5.2 忽視 Bloom Filter 的必要性 (Ignoring Bloom Filters)
### 5.2 Ignoring Bloom Filters

*   **錯誤**: 面對惡意攻擊（查詢大量不存在的 ID），僅依賴簡單的 `get -> db query`。
*   **Mistake**: Facing malicious attacks (querying massive non-existent IDs), relying only on simple `get -> db query`.
*   **後果**: **Cache Penetration**。DB 被無效請求打掛。
*   **Consequence**: **Cache Penetration**. The DB is overwhelmed by invalid requests.
*   **修正**: 在查詢 Redis 前，先過一層 Bloom Filter。若 Bloom Filter 說不存在，則直接返回，不查 DB。
*   **Fix**: Pass through a Bloom Filter before querying Redis. If the Bloom Filter says it doesn't exist, return immediately without checking the DB.

### 5.3 先刪 Cache 再更新 DB (Delete Cache Before Updating DB)
### 5.3 Delete Cache Before Updating DB

*   **錯誤**: 為了「確保」新資料被讀取，先刪除 Cache，再執行 DB Update。
*   **Mistake**: To "ensure" new data is read, delete the Cache first, then execute the DB Update.
*   **後果**: 在刪除 Cache 後、DB 更新完成前的這段時間，讀請求會把 DB 中的**舊資料**重新載入 Cache。這導致 Cache 長時間保持髒資料。
*   **Consequence**: During the interval after deleting the Cache and before the DB update completes, read requests will reload **old data** from the DB into the Cache. This causes the Cache to hold dirty data for a long time.
*   **修正**: 始終採用 **Cache-Aside (Update DB -> Delete Cache)**，配合延遲雙刪（Delayed Double Delete）處理極端一致性需求。
*   **Fix**: Always use **Cache-Aside (Update DB -> Delete Cache)**, potentially with Delayed Double Delete for extreme consistency needs.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 在 Cache-Aside 模式下，如果「更新 DB 成功」但「刪除 Cache 失敗」怎麼辦？
### Q1: In Cache-Aside pattern, what if "Update DB succeeds" but "Delete Cache fails"?

*   **關鍵點 (Key Points)**:
    *   這會導致資料不一致（DB 是新的，Cache 是舊的）。
    *   **重試機制 (Retry Mechanism)**: 將刪除 Cache 的指令放入 Message Queue（如 Kafka/RabbitMQ）進行非同步重試。
    *   **Binlog 訂閱 (Binlog Subscription)**: 使用 Canal 等工具監聽 MySQL Binlog，由獨立服務負責解析 Binlog 並刪除 Redis Key。這是解耦且可靠性最高的做法。
    *   **TTL 兜底**: 設定合理的過期時間，確保不一致只是暫時的（Eventual Consistency）。
*   **Key Points**:
    *   This leads to data inconsistency (DB is new, Cache is old).
    *   **Retry Mechanism**: Put the delete command into a Message Queue (e.g., Kafka/RabbitMQ) for asynchronous retries.
    *   **Binlog Subscription**: Use tools like Canal to listen to MySQL Binlog, with a standalone service parsing the Binlog and deleting the Redis Key. This is the most decoupled and reliable approach.
    *   **TTL Fallback**: Set a reasonable expiration time to ensure inconsistency is only temporary (Eventual Consistency).

### Q2: 如何設計一個能抵擋百萬級 QPS 穿透攻擊的系統？
### Q2: How to design a system that withstands a million-QPS penetration attack?

*   **關鍵點 (Key Points)**:
    *   **Bloom Filter / Cuckoo Filter**: 記憶體效率高，能快速判斷「絕對不存在」。
    *   **Caching Null Values**: 如果查詢結果為空，也將這個「空結果」存入 Redis（設定較短 TTL，如 5 分鐘），防止重複打 DB。
    *   **Rate Limiting**: 在 Gateway 層針對 IP 或 User ID 進行限流。
*   **Key Points**:
    *   **Bloom Filter / Cuckoo Filter**: High memory efficiency, quickly determines "definitely does not exist".
    *   **Caching Null Values**: If the query result is empty, cache this "empty result" in Redis (with a short TTL, e.g., 5 minutes) to prevent repeated DB hits.
    *   **Rate Limiting**: Implement rate limiting at the Gateway layer based on IP or User ID.

### Q3: 什麼時候你不會選擇使用 Redis 快取？
### Q3: When would you choose NOT to use Redis caching?

*   **關鍵點 (Key Points)**:
    *   **資料即時性要求極高**: 金融交易餘額，不能容忍任何毫秒級的不一致。
    *   **查詢模式複雜**: 依賴複雜 SQL Join 或 Ad-hoc 查詢，難以定義 Key。
    *   **寫多讀少**: 資料寫入頻率遠高於讀取，快取命中率極低，維護 Cache 成本大於收益。
*   **Key Points**:
    *   **Extreme Real-time Requirements**: Financial transaction balances where no millisecond-level inconsistency is tolerated.
    *   **Complex Query Patterns**: Reliance on complex SQL Joins or Ad-hoc queries where Keys are hard to define.
    *   **Write-Heavy, Read-Rarely**: Data write frequency far exceeds reads; cache hit rate is low, and the cost of maintaining the Cache outweighs the benefits.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Cache-Aside** 是最通用的模式：先讀 Cache，Miss 讀 DB；先寫 DB，再**刪除** Cache。
2.  **Penetration (穿透)** 解法：Bloom Filter + Cache Null Object。
3.  **Avalanche (雪崩)** 解法：TTL + Random Jitter (隨機值)。
4.  **Stampede (擊穿)** 解法：Mutex Lock 或 Logical Expiration (Soft TTL)。
5.  **一致性保證**：依賴 Eventual Consistency，若需強一致性，請考慮 Binlog 非同步刪除或延遲雙刪。

### 建議後續閱讀 (Next Steps)
*   **Redis Cluster & High Availability**: 學習 Sentinel 與 Cluster 模式，了解當 Redis 節點本身故障時的 Failover 機制（對應 Chapter 06）。
*   **Distributed Locks**: 深入研究 Redlock 演算法及其爭議，了解在分散式環境下如何正確實作鎖。