# 快取設計模式與常見難題 / Caching Patterns & Common Challenges

## Mental model｜心智模型

在引入 Redis 作為快取層之前，必須建立正確的心智模型：**快取是用「一致性」換取「效能」的借貸行為 (Trading consistency for performance)。**

1.  **快取不是資料庫 (Cache is not the Source of Truth)**：
    除非你將 Redis 用作主要資料儲存（Primary Store），否則快取中的資料隨時可能遺失、過期或與資料庫不一致。你的程式碼必須永遠假設 `Cache Miss` 是常態，並具備回源（Fallback to DB）的能力。

2.  **讀寫不對稱性 (Read/Write Asymmetry)**：
    - **讀取 (Read)**：我們希望盡可能命中快取（High Cache Hit Ratio）。
    - **寫入 (Write)**：寫入時的首要任務是確保資料庫正確，其次才是處理快取。**不要試圖在寫入時「更新」快取，而是應該「刪除」快取**（這是避免髒讀最簡單有效的策略）。

3.  **防禦性設計 (Defensive Design)**：
    快取層是系統的防彈背心。如果這層背心失效（雪崩、擊穿），流量會直接打穿資料庫導致系統癱瘓。因此，設計快取時不只是在設計「如何存」，更是在設計「當快取失效時，系統如何存活」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Cache-Aside Pattern (旁路快取模式) - *The Industry Standard*

這是最適合 Redis 的通用模式。應用程式直接與 Cache 和 DB 對話。

*   **讀取流程 (Read Flow)**:
    1.  App 查詢 Redis。
    2.  Hit: 回傳資料。
    3.  Miss: App 查詢 DB -> 將結果寫入 Redis (Set) -> 回傳資料。
*   **寫入流程 (Write Flow)**:
    1.  App 更新 DB。
    2.  App **刪除 (Delete)** Redis 中的對應 Key。
    *   *Why Delete?* 併發寫入時，若採用「更新 Cache」策略，容易因執行順序導致 Cache 存留舊資料。刪除是冪等且安全的，下次讀取時自然會重建最新的 Cache。

### 2. Handling Cache Penetration (解決快取穿透)

**問題**：惡意或大量查詢「資料庫中不存在的 Key」（如 ID = -1）。這些請求會直接穿透 Redis 打在 DB 上。
**解法**：
*   **Cache Null Values**: 當 DB 查不到資料時，仍在 Redis 寫入一個 `null` 或特殊標記，並設定較短的 TTL（如 5 分鐘）。
*   **Bloom Filter**: 在存取 Redis 前，先用 Bloom Filter 判斷該 Key 是否「可能存在」。若 Bloom Filter 說不存在，則直接攔截。

### 3. Handling Cache Avalanche (解決快取雪崩)

**問題**：大量 Key 在同一時間過期，或者 Redis 節點當機，導致瞬間流量全部壓向 DB。
**解法**：
*   **Randomize TTL (亂數過期時間)**: 設定 TTL 時，加上一個隨機值（Jitter）。例如：原定 1 小時過期，實際設定為 `3600s + random(0, 300s)`。
*   **High Availability**: 使用 Redis Sentinel 或 Cluster 模式確保 Redis 本身的高可用。

### 4. Handling Cache Breakdown / Hotspot Invalid (解決快取擊穿)

**問題**：某個 **熱點 Key (Hot Key)**（如熱門新聞、促銷商品）過期瞬間，成千上萬的併發請求同時發現 Cache Miss，同時回源查詢 DB 並試圖回寫 Cache。
**解法**：
*   **Mutex Lock (互斥鎖)**: 在 Cache Miss 後，先嘗試獲取分佈式鎖（`SETNX`）。
    *   拿到鎖的 Thread：去查 DB 並回寫 Cache。
    *   沒拿到鎖的 Thread：Sleep 一小段時間後重試（此時 Cache 應該已經有了）。
*   **Logical Expiration (邏輯過期)**: 不設定 Redis 的 TTL，而是將過期時間寫在 Value 內容裡。讀取時若發現邏輯過期，回傳舊資料，並非同步啟動一個 Thread 去更新資料。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 更新資料庫後「更新」快取 (Update Cache on Write)
- **Bad**: `DB.update(data)` -> `Redis.set(key, data)`
- **Why**: 在高併發下，兩個執行緒 A 和 B 同時寫入。A 先更新 DB，B 後更新 DB；但可能 B 先更新 Redis，A 後更新 Redis。結果：DB 是 B 的新資料，Redis 卻是 A 的舊資料（Dirty Cache）。
- **Fix**: 永遠使用 **Delete** Cache 策略。

### 2. 先刪快取，再寫資料庫 (Delete Cache before DB Write)
- **Bad**: `Redis.del(key)` -> `DB.update(data)`
- **Why**: 刪除快取後，DB 更新完成前，另一個讀取請求進來，發現 Cache Miss，讀到 DB 舊資料並寫回 Cache。結果：Cache 裡永遠是舊資料。
- **Fix**: **Cache Aside (先寫 DB，再刪 Cache)**。若要求極高一致性，可採用 **Delayed Double Delete**（先刪 -> 寫 DB -> 等待 500ms -> 再刪一次）。

### 3. 無上限的 Keys 與無 TTL (Unbounded Keys & No TTL)
- **Bad**: 依賴 LRU (Least Recently Used) 機制來清除舊資料，而不主動設定 TTL。
- **Why**: 雖然 Redis 有 Eviction Policy，但這會讓記憶體長期處於滿載狀態，增加延遲與 OOM 風險。
- **Fix**: 所有的 Cache Key 都應該有一個合理的 TTL。

### 4. 驚群效應 (Thundering Herd)
- **Bad**: 系統重啟或冷啟動時，Cache 是空的，所有流量直接打 DB。
- **Fix**: 實作 **Cache Warming (預熱)** 機制，在服務上線前預先載入熱點資料。

---

## Checklists & workflows｜檢查清單與流程

在實作 Redis 快取層時，請依序檢查以下項目：

### Implementation Checklist
- [ ] **Key Naming**: 是否使用了具備 namespace 的命名規範？(e.g., `app:user:123:profile`)
- [ ] **TTL Strategy**: 是否為每個 `SET` 操作都設定了過期時間？
- [ ] **Jitter**: 對於批量寫入的 Cache，是否加入了隨機過期時間以避免雪崩？
- [ ] **Null Handling**: 是否處理了 DB 回傳 Empty 的情況（Cache Null）以避免穿透？
- [ ] **Serialization**: 序列化格式（JSON, Protobuf, MsgPack）是否考慮了空間效率與反序列化成本？

### Code Review Questions
- [ ] **Write Path**: 寫入資料庫後，是否有正確執行 `DEL` 操作？
- [ ] **Concurrency**: 對於極度熱門的 Key，是否有實作 Mutex Lock 機制防止擊穿？
- [ ] **Size**: 存入 Value 的大小是否合理？（避免 Big Key，如超過 10KB 的 JSON blob 需檢討）。

---

## Real-world examples｜實戰案例

### Scenario: High-Traffic Product Detail Page (熱門商品詳情頁)

這是一個典型的「讀多寫少」且面臨「擊穿風險」的場景。

#### 1. 解決擊穿 (Breakdown) 的 Pseudo-code

```python
def get_product_details(product_id):
    cache_key = f"product:{product_id}"
    
    # 1. Try to get from Cache
    data = redis.get(cache_key)
    if data:
        # Check for "Logical Expiry" if using that pattern
        return deserialize(data)
        
    # 2. Cache Miss - Apply Mutex Lock to prevent Thundering Herd
    lock_key = f"lock:product:{product_id}"
    # Try to acquire lock with a 5-second timeout
    if redis.set(lock_key, "1", nx=True, ex=5):
        try:
            # 3. Fetch from DB (Source of Truth)
            data = db.query("SELECT * FROM products WHERE id = ?", product_id)
            
            # 4. Handle Penetration (Data not found)
            if not data:
                # Cache "null" for 5 minutes
                redis.set(cache_key, "null", ex=300)
                return None
            
            # 5. Write to Cache with Random TTL (Avoid Avalanche)
            # Base TTL 1 hour + Random 0-10 mins
            ttl = 3600 + random.randint(0, 600)
            redis.set(cache_key, serialize(data), ex=ttl)
            
            return data
        finally:
            # 6. Release Lock
            redis.delete(lock_key)
    else:
        # Failed to get lock: Wait and retry (Spin lock)
        time.sleep(0.1)
        return get_product_details(product_id)
```

### Scenario: User Profile Update (使用者資料更新)

標準的 Cache-Aside 寫入策略。

```python
def update_user_profile(user_id, new_data):
    # 1. Update Database First
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, new_data)
    
    # 2. Delete Cache (Do not update it directly)
    # Even if delete fails, the cache will eventually expire (TTL fallback)
    # For critical consistency, consider retrying the delete or using a message queue.
    redis.delete(f"user:{user_id}")
```