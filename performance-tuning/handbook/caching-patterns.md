# 快取策略與常見陷阱 / Caching Strategies and Common Pitfalls

## Mental model｜心智模型

在引入快取之前，必須建立正確的心智模型：**快取是「借用」記憶體空間來換取時間（CPU 計算或 I/O 等待）的策略，它本質上是一種妥協。**

### 1. 空間換時間與資料一致性的權衡 (Space-Time Trade-off & Consistency)
快取不是免費的午餐。當你將資料複製一份到快取層（如 Redis, Memcached）時，你立刻引入了兩個新問題：
1.  **資料同步延遲（Staleness）：** 快取中的資料永遠是 Source of Truth (Database) 的「過去式」。你必須定義系統能容忍多久的「最終一致性」。
2.  **維運複雜度（Complexity）：** 你現在需要維護兩個資料存儲的狀態。

### 2. 快取命中率公式 (The Hit Rate Equation)
效能優化的目標是降低平均延遲（Average Latency）。
$$ Latency_{avg} = (HitRate \times Latency_{cache}) + ((1 - HitRate) \times Latency_{db}) $$

如果 **Hit Rate** 過低，或者 **Cache Latency** 因為網路/序列化問題變高，引入快取反而會讓系統變慢（因為多了一次無效的網路來回）。

### 3. 多層級防禦 (Defense in Depth)
不要只把快取看作單一層。現代架構通常包含：
*   **L1: Local Cache (In-memory):** 如 Guava, Caffeine。速度極快但與實例綁定，易造成各實例資料不一致。
*   **L2: Remote Cache (Distributed):** 如 Redis, Memcached。共用狀態，網路 I/O 是成本。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 讀取模式 (Read Patterns)

#### Cache-Aside (Lazy Loading) —— **業界標準**
應用程式負責協調資料庫與快取。
*   **流程：** App 查 Cache $\rightarrow$ Miss $\rightarrow$ App 查 DB $\rightarrow$ App 寫入 Cache $\rightarrow$ 回傳。
*   **適用：** 讀多寫少（Read-heavy），資料對即時性要求不極端嚴格。
*   **優點：** 只有被請求的資料才會進入快取（節省空間）；Cache 掛掉時系統仍可運作（雖然 DB 壓力會大增）。

#### Read-Through
應用程式只對 Cache 說話，Cache 負責去 DB 撈資料（如果 Miss）。
*   **適用：** 使用特定 Framework 或 Library 封裝時（如 Spring Cache）。
*   **優點：** 程式碼乾淨，關注點分離。

### 2. 寫入模式 (Write Patterns)

#### Write-Around
寫入時直接寫 DB，不更新 Cache（讓 Cache 自然過期或被刪除）。
*   **適用：** 寫入後極少被立即讀取的資料（避免 Cache 汙染）。

#### Write-Through
寫入時同時更新 DB 和 Cache（通常由 Cache Library 處理）。
*   **優點：** Cache 內永遠是最新資料，讀取效能穩定。
*   **缺點：** 寫入延遲較高（需等兩邊都寫完）。

#### Write-Behind (Write-Back)
先寫入 Cache，非同步（Asynchronous）批次寫入 DB。
*   **適用：** 高頻寫入場景（如計數器、Log）。
*   **風險：** 如果 Cache 節點當機，會**遺失資料**。

### 3. 解決特定難題的模式

#### 解決 Cache Penetration (快取穿透)
查詢「根本不存在」的 Key，導致每次都穿透到 DB。
*   **解法 A (Cache Null):** 即使 DB 查不到，也將 `null` 寫入 Cache 並設定較短 TTL (如 5 分鐘)。
*   **解法 B (Bloom Filter):** 在存取 Cache 前先用 Bloom Filter 判斷 Key 是否可能存在，若不存在直接回絕。

#### 解決 Cache Stampede / Breakdown (快取擊穿)
一個「熱點 Key」過期瞬間，大量併發請求同時打向 DB。
*   **解法 A (Mutex Lock):** 第一個發現過期的 Thread 取得鎖去 DB 撈資料，其他 Thread 等待或重試。
*   **解法 B (Logical Expiration / Soft TTL):** 在 Value 內包含一個邏輯過期時間。若發現邏輯過期，回傳舊資料，並非同步啟動一個 Thread 去更新 Cache。

#### 解決 Cache Avalanche (快取雪崩)
大量 Key 在同一時間集體過期，導致 DB 瞬時壓力過大。
*   **解法：** 設定 TTL 時加上隨機值（Random Jitter）。例如：`TTL = 10 min + random(0-60s)`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Delete vs. Update" Debate (刪除還是更新？)
在 Cache-Aside 模式下，當資料變更時，應該更新 Cache 還是刪除 Cache？
*   **反模式：** 嘗試在寫入 DB 時「更新」Cache。這容易導致 Race Condition（兩個併發寫入導致 Cache 存了舊值）。
*   **最佳實務：** **先寫 DB，再刪除 Cache (Delete Cache)**。讓下一次讀取重新載入最新值。
    *   *進階雷點：* 「先刪 Cache 再寫 DB」也是錯的，因為在寫入 DB 完成前，另一個讀取請求可能又把舊資料載入 Cache 了。
    *   *最終一致性解法：* 使用 **Cache Double Deletion** 或 **Canal** 監聽 Binlog 非同步刪除。

### 2. Serialization Bloat (序列化膨脹)
*   **陷阱：** 直接使用語言原生的序列化（如 Java Serialization）或未經壓縮的 JSON 儲存大物件。
*   **後果：** 網路頻寬被吃光，Redis CPU 飆高（序列化/反序列化成本），Latency 增加。
*   **建議：** 使用 Protobuf, MsgPack 或 Snappy/LZ4 壓縮後的 Binary。

### 3. Storing Huge Collections (儲存超大集合)
*   **陷阱：** 在 Redis List/Hash 中儲存數萬筆資料（如「某用戶的所有粉絲 ID」）。
*   **後果：** 讀取該 Key 會阻塞 Redis (Single-threaded)，造成全站卡頓。
*   **建議：** 拆分 Key (Sharding)，或只存部分熱資料，或改用專門的 Search Engine。

### 4. Ignoring Keyspace Visibility (忽視 Key 命名空間)
*   **陷阱：** 使用 `user:123` 這種過於簡單的 Key。
*   **後果：** 不同業務線衝突，或者難以進行 Cache 清理/分析。
*   **建議：** 規範命名 `app:module:entity:id:version` (e.g., `shop:inventory:product:101:v2`).

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Do I need caching?
1.  **Is the data read-heavy?** (Yes $\rightarrow$ Continue)
2.  **Is the data tolerable to staleness?** (Yes $\rightarrow$ Continue)
3.  **Is the computation/query expensive?** (Yes $\rightarrow$ Cache it; No $\rightarrow$ Don't optimize prematurely)

### Implementation Checklist
- [ ] **Key Naming Strategy:** 是否有統一的前綴？是否包含版本號？
- [ ] **TTL Strategy:** 是否設定了過期時間？是否加上了 Random Jitter 防止雪崩？
- [ ] **Eviction Policy:** Redis 的 `maxmemory-policy` 設定為何？(通常 `allkeys-lru` 或 `volatile-lru`)。
- [ ] **Consistency Plan:** 寫入時如何讓 Cache 失效？(Delete vs Update)。是否需要 Transaction 支援？
- [ ] **Penetration Defense:** 是否處理了 Null Value 的快取？
- [ ] **Serialization:** 物件大小是否超過 10KB？如果是，是否使用了壓縮？
- [ ] **Observability:** 是否監控了 Hit Rate, Miss Rate, Eviction Count, Network Bandwidth？

### Troubleshooting Workflow (當快取變慢時)
1.  **Check Network:** 頻寬是否飽和？(可能是 Value 太大)
2.  **Check CPU:** 是否有高複雜度指令 (如 `KEYS`, `HGETALL` on large hash)？
3.  **Check Hit Rate:** 命中率是否突然下降？(可能是雪崩或部署後 Cold Start)
4.  **Check Evictions:** 是否因為記憶體滿了導致頻繁驅逐熱資料？

---

## Real-world examples｜實戰案例

### Case 1: The "Hot Product" Flash Sale (秒殺活動)
**情境：** iPhone 新機開賣，百萬人同時刷新商品頁面。
**問題：** 典型的 Cache Stampede。商品詳情 Cache 過期瞬間，DB 被打掛。
**解決方案：**
1.  **Logical Expiration:** Cache 內存儲物件 `{ data: {...}, expireAt: 12:00:00 }`，實際 Redis TTL 設為 12:05:00。
2.  **Code Logic:**
    ```python
    data = cache.get(key)
    if data.expireAt < now():
        if try_lock(lock_key):
            # 只有一個線程去 DB 更新，並延長 expireAt
            async_update_cache(key)
        # 其他線程直接返回舊資料 (Stale data is better than no data)
    return data.data
    ```

### Case 2: User Permissions (權限驗證)
**情境：** 每個 API Call 都要驗證 User 權限，DB 壓力大。
**問題：** 權限變更不頻繁，但要求即時生效（撤銷權限要馬上停用）。
**解決方案：**
1.  使用 **Cache-Aside** 讀取權限。
2.  當管理員修改權限時，發送 **Pub/Sub** 訊息或寫入 **Message Queue**。
3.  所有 App 實例訂閱該 Channel，收到變更通知後，清除 Local Cache (L1) 並刪除 Remote Cache (L2)。

### Case 3: The "Crawling Bot" Attack (爬蟲攻擊)
**情境：** 競爭對手爬蟲大量請求不存在的 Product ID (e.g., id=-1, id=9999999)。
**問題：** Cache Penetration，Cache 沒用，DB CPU 100%。
**解決方案：**
1.  **Input Validation:** 在 Controller 層直接擋掉負數 ID。
2.  **Cache Null:**
    ```java
    Product p = db.find(id);
    if (p == null) {
        cache.set(id, NullObject, 60_SECONDS); // 短 TTL
    } else {
        cache.set(id, p, 1_HOUR);
    }
    ```
3.  **Bloom Filter:** 在 Redis 前面擋一層 Bloom Filter，過濾掉絕大多數不可能存在的 ID。