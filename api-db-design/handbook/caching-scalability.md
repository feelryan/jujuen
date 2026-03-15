# 快取策略與擴展性設計 / Caching Strategies & Scalability Design

## Mental model｜心智模型

在探討快取與擴展性時，我們不應只將其視為「提升效能」的手段，而應視為 **「資料存取成本的階層管理」 (Tiered Management of Data Access Cost)**。

### 1. 存取階層金字塔 (The Access Hierarchy Pyramid)
想像一個金字塔，越頂端速度越快、容量越小、成本越高；越底層速度越慢、容量越大、成本越低。
- **L1 (In-Memory / Local Cache):** 應用程式記憶體內（如 Guava, Caffeine）。速度最快，但無法跨實體共享。
- **L2 (Distributed Cache):** Redis / Memcached。速度快，可共享，網路 I/O 是主要成本。
- **L3 (Database - Read Replicas):** 硬碟/SSD 存取，透過複製分散讀取壓力。
- **L4 (Database - Primary):** 唯一的寫入真理來源（Source of Truth），最珍貴的資源。

**核心思維：** 你的目標是盡可能在金字塔頂端攔截請求（Intercept），保護底層的 Primary DB 不被流量沖垮。

### 2. 一致性與可用性的權衡 (Consistency vs. Latency Trade-off)
引入快取或讀寫分離，本質上就是 **「用資料的一致性（Staleness）來交換低延遲（Low Latency）」**。
- **Mental Check:** 當你決定 Cache 一筆資料 5 分鐘，你是否允許使用者在 5 分鐘內看到舊資料？如果不允許，快取策略就需要極其複雜的失效機制（Invalidation），或者根本不該快取。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 快取寫入模式 (Caching Write Patterns)

在真實系統中，**Cache-Aside** 是 90% 場景的首選，因為它對 Cache 故障最具有韌性。

*   **Cache-Aside (Lazy Loading):**
    *   **讀取：** App 先查 Cache → Miss → 查 DB → 寫入 Cache → 回傳。
    *   **寫入：** App 寫入 DB → **刪除 (Delete/Invalidate)** Cache。
    *   *Why Delete?* 更新 Cache (Update) 可能導致並發寫入時的 Race Condition（髒資料），直接刪除讓下一次讀取重新載入是最安全的。

*   **Write-Through / Write-Back:**
    *   App 只對 Cache 寫入，由 Cache 組件負責同步到 DB。
    *   *適用場景：* 寫入極度頻繁且允許一定程度資料遺失（Write-Back）的計數器或統計數據。

### 2. 資料庫擴展模式 (Database Scalability Patterns)

*   **讀寫分離 (Read/Write Splitting):**
    *   將 `SELECT` 流量導向 Read Replicas，`INSERT/UPDATE/DELETE` 導向 Primary。
    *   **關鍵挑戰：** 複製延遲 (Replication Lag)。使用者剛修改完個人資料，重新整理卻看到舊的。
    *   **實務解法：** **Pin-to-Master** 策略。當使用者發生寫入行為後，在短時間內（如 2 秒）強制將該使用者的讀取請求導向 Primary，之後再切回 Replicas。

*   **分片 (Sharding):**
    *   當單機寫入或儲存容量達到瓶頸時使用。
    *   **Sharding Key 的選擇：** 這是不可逆的決策。
        *   *Based on ID:* 資料分佈均勻，但範圍查詢（Range Query）困難。
        *   *Based on Time:* 範圍查詢容易，但會造成寫入熱點（Hotspot，所有新資料都寫入同一個 shard）。
    *   **最佳實務：** 除非資料量達到 TB 級別或單表行數破億，否則優先考慮垂直擴展（Scale Up）或歸檔舊資料（Archiving），因為 Sharding 會讓 Join 操作和交易管理（Transaction）變得極度痛苦。

### 3. 防禦性快取設計 (Defensive Caching)

*   **處理快取穿透 (Cache Penetration):** 查詢「不存在的 Key」，導致請求直擊 DB。
    *   *解法：* 將「空結果」也快取起來（設定較短 TTL）或使用 Bloom Filter。
*   **處理快取擊穿 (Cache Breakdown):** 「熱點 Key」過期瞬間，大量並發請求擊垮 DB。
    *   *解法：* 使用 Mutex Lock（互斥鎖），只允許一個 Thread 去 DB 撈資料，其他等待；或使用 Logical Expiration（邏輯過期，背景非同步更新）。
*   **處理快取雪崩 (Cache Avalanche):** 大量 Key 在同一時間過期。
    *   *解法：* 在原本的 TTL 上增加隨機時間（Jitter），例如 `TTL = 600s + random(0-60s)`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Silver Bullet" Cache (快取萬能論)
*   **Anti-pattern:** 遇到效能問題就無腦加 Redis，而不去優化 SQL 查詢或索引。
*   **後果：** 維護了兩套資料模型，系統複雜度倍增，且當快取失效時，DB 依然會死鎖或崩潰。

### 2. Long TTLs without Invalidation (長 TTL 卻無失效機制)
*   **Anti-pattern:** 設定很長的過期時間（如 24 小時），但資料更新時沒有主動清除快取。
*   **後果：** 使用者體驗極差，客服收到大量「我看不到修改」的投訴。

### 3. Caching Sensitive Data improperly (不當快取敏感資料)
*   **Anti-pattern:** 將包含 PII (個人識別資訊) 或權限特定的資料快取在共用的 Key 中（例如 `GET /users/profile` 卻沒有包含 User ID 在 Cache Key）。
*   **後果：** 使用者 A 登入後看到了使用者 B 的快取資料（嚴重資安事故）。

### 4. Premature Sharding (過早分片)
*   **Anti-pattern:** 專案初期為了「未來擴展性」直接設計分片架構。
*   **後果：** 開發速度變慢，跨分片查詢（Cross-shard Join）效能低落，運維成本高昂。

---

## Checklists & workflows｜檢查清單與流程

### Cache Implementation Checklist (快取實作檢核表)

- [ ] **Key Naming Strategy:** 是否使用了具備命名空間的 Key？(e.g., `app:v1:user:123:profile`)
- [ ] **TTL Policy:** 是否為每個 Key 設定了合理的過期時間？絕對禁止無限期的 Key（除非是靜態設定檔）。
- [ ] **Eviction Policy:** Redis 的記憶體滿了怎麼辦？（確認設定了 `allkeys-lru` 或 `volatile-lru`）。
- [ ] **Serialization:** 儲存格式是否高效？（推薦 Protobuf 或 MsgPack，避免肥大的 JSON 若非必要）。
- [ ] **Fallback:** 當 Cache Server 掛掉時，系統會崩潰還是降級（Degrade）直接查 DB？
- [ ] **Security:** Cache 中是否包含未加密的敏感資訊？

### Scalability Decision Workflow (擴展決策流程)

1.  **DB CPU/Memory 飆高？**
    *   $\rightarrow$ 檢查 Slow Query 與 Index (索引優化)。
    *   $\rightarrow$ 檢查是否可以引入 Cache (減少讀取)。
2.  **讀取流量依然過大？**
    *   $\rightarrow$ 垂直擴展 (Upgrade Hardware)。
    *   $\rightarrow$ 建立 Read Replicas (讀寫分離)。
3.  **寫入流量過大或儲存空間不足？**
    *   $\rightarrow$ 垂直擴展 (Upgrade Hardware)。
    *   $\rightarrow$ 資料歸檔 (Archive old data)。
    *   $\rightarrow$ **最後手段：** 資料庫分片 (Sharding)。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Celebrity Tweet" (熱點問題)
**情境：** 一位擁有千萬粉絲的名人發了一則貼文，瞬間湧入百萬次讀取。
**問題：** 即使有 Cache，當該 Key 過期（Expired）的瞬間，數千個請求同時發現 Cache Miss，同時打向 DB（Thundering Herd / Cache Breakdown）。

**解決方案 (Pseudo-code):**
使用 **Mutex Lock (互斥鎖)** 確保只有一個請求去重建快取。

```python
def get_tweet(tweet_id):
    cache_key = f"tweet:{tweet_id}"
    data = redis.get(cache_key)
    
    if data:
        return data
        
    # Cache Miss
    # 嘗試獲取分佈式鎖，設定較短的 timeout 防止死鎖
    if redis.set(f"lock:{tweet_id}", "1", nx=True, ex=5):
        try:
            # 只有拿到鎖的請求去查 DB
            data = db.query("SELECT * FROM tweets WHERE id = ?", tweet_id)
            # 重建快取，並加上隨機 Jitter 防止雪崩
            redis.set(cache_key, data, ex=300 + random(0, 60)) 
        finally:
            redis.delete(f"lock:{tweet_id}")
    else:
        # 沒拿到鎖的請求，稍微睡一下再重試讀取 Cache
        sleep(0.1)
        return get_tweet(tweet_id)
        
    return data
```

### Scenario 2: E-commerce Inventory (庫存扣減)
**情境：** 秒殺活動，商品庫存不能超賣，但讀取量極大。
**問題：** 直接讀 DB 太慢，讀 Cache 又怕資料不一致導致超賣。

**解決方案：**
1.  **Redis Lua Script:** 將庫存預熱（Pre-warm）載入 Redis。
2.  **Atomic Decrement:** 所有的扣減操作先在 Redis 進行（`DECR` 指令是原子的）。
3.  **Async Sync:** Redis 扣減成功後，發送訊息到 Message Queue，非同步更新 DB 庫存。
4.  **補償機制:** 若 DB 更新失敗，需有回補流程。

> **注意：** 這種模式下，Redis 成為了短期內的 Source of Truth，需確保 Redis 的持久化（AOF/RDB）策略足夠強健。