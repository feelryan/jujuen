# 記憶體管理與效能優化 / Memory Management & Performance Optimization

## Mental model｜心智模型

在深入 Redis 記憶體優化之前，你需要建立兩個核心的心智模型：**「冰山模型 (The Iceberg Model)」** 與 **「租約空間 (The Leased Space)」**。

### 1. The Iceberg Model: Data vs. Overhead
很多工程師誤以為 `SET key "value"` 只佔用了 key 和 value 字串本身的 bytes 數。事實上，Redis 是一個複雜的 C 語言結構體集合。
- **水面上的資料**：你實際儲存的 Key 與 Value。
- **水面下的 Overhead**：`redisObject` 結構、dictEntry、記憶體分配器 (jemalloc) 的 metadata、指針 (Pointers)。
- **Insight**：對於極小的資料（如存數百萬個小整數），Overhead 可能比資料本身大好幾倍。優化的關鍵往往在於**減少物件數量**與**利用緊湊編碼 (Compact Encoding)**。

### 2. The Leased Space: Maxmemory & Eviction
不要將 Redis 視為無限的儲存桶，而應視為一個**固定大小的倉庫**。
- 當倉庫滿了（達到 `maxmemory`），你必須決定誰該被踢出去（Eviction Policy）。
- 如果沒有設定規則（`noeviction`），新貨物就進不來（Write errors）。
- **Insight**：記憶體管理是被動的（等到滿了才踢人）也是主動的（透過 TTL 過期）。正確的策略能讓這個倉庫永遠保持「只留最有價值貨物」的狀態。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 利用底層編碼優化 (Encoding Optimization)
Redis 對於「小型的集合類型」會自動採用更緊湊的記憶體編碼（如 `listpack` 或舊版的 `ziplist`），而非標準的 Hash Table 或 Linked List。這能節省高達 10x 的記憶體。

- **Hash as a Compact Object**: 如果你有大量的小物件（例如 User Profile），不要存成 JSON String，改存成 Redis Hash。
- **Tuning Config**: 調整 `redis.conf` 讓更多資料能維持在緊湊編碼狀態：
  ```conf
  # Redis 7.0+ 使用 listpack，舊版為 ziplist
  hash-max-listpack-entries 512  # 欄位數量限制
  hash-max-listpack-value 64     # 欄位值大小限制 (bytes)
  ```
  *Tip: 只有當 Hash 的欄位數與大小都小於設定值時，Redis 才會使用緊湊編碼。一旦超過，就會膨脹成標準 Hash Table 且不可逆（除非重建）。*

### 2. 精準選擇淘汰策略 (Eviction Policies)
根據業務場景選擇正確的 `maxmemory-policy`：

- **Cache 場景 (快取)**：
  - `allkeys-lru`: 最常用的策略。不管有無 TTL，踢掉最久沒被使用的 Key。適合「熱點資料」明顯的場景。
  - `allkeys-lfu`: 踢掉「使用頻率最低」的 Key。適合防止「一次性掃描」污染快取的場景。
- **Store + Cache 混合場景**：
  - `volatile-lru`: 只踢掉**有設定 TTL** 的 Key。這允許你在同一個 Redis 實例中混合存放「必須持久化的資料」與「可被犧牲的快取」。

### 3. 非同步刪除 (Lazy Freeing)
刪除一個幾百 MB 的 Big Key 會導致主執行緒阻塞 (Block)，造成瞬間延遲。
- **Pattern**: 使用 `UNLINK` 代替 `DEL`。`UNLINK` 會將 Key 從 Keyspace 中移除，但記憶體回收會在背景執行緒 (Background Thread) 異步進行。
- **Config**: 開啟 Lazy Freeing 相關設定以防自動淘汰時阻塞：
  ```conf
  lazyfree-lazy-eviction yes
  lazyfree-lazy-expire yes
  ```

### 4. 主動碎片整理 (Active Defragmentation)
當你頻繁更新與刪除不同大小的 Key 時，記憶體碎片 (Fragmentation) 會導致 OS 看到的記憶體佔用遠大於 Redis 實際儲存的資料量 (`used_memory_rss` > `used_memory`)。
- **Pattern**: 在 Redis 4.0+，開啟 `activedefrag`。Redis 會在 CPU 空閒時掃描並搬移資料以釋放連續記憶體頁面歸還給 OS。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Big Key" Monster
**反模式**：在一個 List、Set 或 Hash 中存入數十萬、數百萬個元素，或者存入單個超大的 String (數十 MB)。
- **後果**：
  - **Network Buffer 阻塞**：讀取時塞爆頻寬。
  - **阻塞主執行緒**：刪除或過期時，記憶體回收耗時過長，導致 Redis 卡死（Stop-the-world）。
  - **遷移困難**：在 Cluster 模式下，Big Key 無法被拆分，導致資料傾斜 (Data Skew)。
- **偵測**：使用 `redis-cli --bigkeys` 或 `redis-cli --memkeys` 掃描。

### 2. Ignoring `maxmemory`
**反模式**：在生產環境不設定 `maxmemory`。
- **後果**：Redis 會吃到機器所有的 RAM，最後觸發 OS 的 **OOM Killer (Out Of Memory Killer)**，導致 Redis 行程直接被殺掉。
- **修正**：務必設定 `maxmemory`（建議保留 20-30% 系統記憶體給 OS 和 Redis 自身的 Overhead/COW）。

### 3. The "Keys-LRU" Trap
**反模式**：誤以為 `volatile-lru` 會刪除所有舊資料。
- **陷阱**：如果你寫入資料時忘記帶上 TTL，且策略是 `volatile-*`，當記憶體滿時，Redis **不會** 刪除這些沒有 TTL 的資料，最終導致 OOM 錯誤 (`OOM command not allowed...`)。

### 4. High Fragmentation Ratio Panic
**反模式**：看到 `mem_fragmentation_ratio` 高就重啟 Redis。
- **陷阱**：如果 ratio < 1.0，代表使用了 Swap，這才是效能殺手。如果 ratio > 1.5，代表碎片多。重啟雖然有用，但會導致 Cache 預熱歸零。應優先嘗試 `memory purge` (手動觸發 jemalloc 清理) 或調整 `activedefrag`。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Operations Checklist
- [ ] **Maxmemory Safety**: 確認 `maxmemory` 已設定，且預留了足夠緩衝區給 Copy-on-Write (BGSAVE 時使用)。
- [ ] **Eviction Policy**: 確認 `maxmemory-policy` 符合業務邏輯（是全快取還是混合模式？）。
- [ ] **Big Keys Check**: 定期執行 `redis-cli --bigkeys -i 0.1` (使用 `-i` 避免掃描時阻塞) 檢查是否有異常增長的 Key。
- [ ] **Fragmentation Monitor**: 監控 `INFO memory` 中的 `mem_fragmentation_ratio`。
  - `> 1.5`: 需要關注碎片整理。
  - `< 1.0`: 危險！系統正在使用 Swap，效能會崩跌。
- [ ] **Lazy Freeing**: 確認程式碼中使用 `UNLINK` 而非 `DEL` 處理大型資料；確認 `lazyfree` 相關配置已開啟。

### Decision Tree: Handling Memory Alerts
1. **收到記憶體告警 (Memory High Usage)**
   - 檢查 `used_memory` vs `maxmemory`。
   - **Case A: 快滿了 (Close to maxmemory)**
     - 檢查 Eviction Policy 是否生效？
     - 是否有大量 Key 沒有設定 TTL？
     - 是否有 Big Keys 佔據大量空間？
   - **Case B: RSS 異常高 (High RSS, low used_memory)**
     - 這是碎片化問題。
     - 執行 `MEMORY PURGE`。
     - 檢查 `activedefrag` 配置。

---

## Real-world examples｜實戰案例

### Case 1: Optimizing User Tags (Set vs. IntSet)
**情境**：你需要儲存 1000 萬個使用者的「標籤 ID (Tag IDs)」。每個使用者約有 5-10 個 Tags，Tag ID 是純數字。

- **Naive Approach**: 使用標準 Set。
  - `SADD user:1001:tags 501 502 503`
  - 當 Tag ID 超過 `set-max-intset-entries` (預設 512) 或包含非數字時，Redis 使用 Hashtable 編碼。
  - **Memory Usage**: 高。

- **Optimized Approach**: 利用 IntSet。
  - 確保 Tag ID 都在整數範圍內。
  - 確保每個 Set 的元素數量控制在 512 以內。
  - **Result**: Redis 會使用 `IntSet` (整數陣列) 儲存，記憶體佔用量可能只有 Hashtable 的 **1/10**。

### Case 2: The "Thundering Herd" on OOM
**情境**：一個電商網站在大促銷時 Redis 突然崩潰。
- **Root Cause**:
  1.  `maxmemory` 設定為 8GB。
  2.  實際資料量達到 7.5GB。
  3.  系統觸發自動備份 (BGSAVE)。
  4.  Linux 的 `fork()` 機制產生子行程。
  5.  因為寫入量大 (Heavy Write Load)，Copy-on-Write 機制導致記憶體頁面大量複製。
  6.  總記憶體需求瞬間超過實體 RAM，觸發 OOM Killer 殺掉 Redis 主行程。
- **Solution**:
  - 將 `maxmemory` 調降至 6GB (預留更多空間給 COW)。
  - 設定 `/proc/sys/vm/overcommit_memory = 1` (告訴 Linux 核心允許分配所有的實體記憶體，不要過於保守拒絕 fork)。

### Case 3: Deleting a List with 5 Million Items
**情境**：你需要刪除一個用來做 Log Buffer 的 List key，裡面累積了 500 萬條 log。
- **Bad Practice**: `DEL app:logs`
  - 結果：Redis 停止回應約 2-5 秒（視 CPU 而定），所有線上請求 timeout。
- **Best Practice**: `UNLINK app:logs`
  - 結果：Redis 立即回傳 OK。背景執行緒慢慢回收記憶體，線上服務不受影響。