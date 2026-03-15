# Chapter 07: Memory Management & Eviction Policies
# 第七章：記憶體管理與淘汰策略

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For a Senior Engineer, Redis is not just a "set it and forget it" cache; it is an in-memory system where resource management is critical. Misunderstanding memory management often leads to production incidents like latency spikes, OOM (Out of Memory) kills, or unexpected data loss.
對於資深工程師而言，Redis 絕非「設定後即置之不理」的快取，而是一個資源管理至關重要的記憶體系統。對記憶體管理的誤解，常導致生產環境發生延遲飆升、OOM（記憶體不足）崩潰或非預期的資料遺失。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Differentiate Expiration from Eviction**: Understand the distinct mechanisms of how Redis handles expired keys (TTL) versus how it reclaims memory when `maxmemory` is reached.
    **區分過期（Expiration）與淘汰（Eviction）**：理解 Redis 如何處理過期鍵（TTL）的機制，與當達到 `maxmemory` 時如何回收記憶體的機制有何不同。
2.  **Explain the Implementation of LRU/LFU**: Describe how Redis approximates LRU and LFU algorithms to balance accuracy with memory overhead.
    **解釋 LRU/LFU 的實作細節**：描述 Redis 如何透過近似演算法來實作 LRU 與 LFU，以在精準度與記憶體開銷之間取得平衡。
3.  **Manage Memory Fragmentation**: Diagnose high `mem_fragmentation_ratio` and apply strategies like Active Defragmentation.
    **管理記憶體碎片**：診斷過高的 `mem_fragmentation_ratio` 並應用主動重組（Active Defragmentation）等策略。
4.  **Optimize Cost & Performance**: Choose the correct `maxmemory-policy` based on specific access patterns (e.g., Long Tail vs. Recency).
    **優化成本與效能**：根據特定的存取模式（例如長尾效應 vs. 近期熱度）選擇正確的 `maxmemory-policy`。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Expiration vs. Eviction
### 2.1 過期（Expiration）與淘汰（Eviction）

It is crucial to separate these two concepts in your mental model:
在心智模型中區分這兩個概念至關重要：

*   **Expiration (TTL)**: "This data is no longer valid after time $T$." It is a logical validity constraint.
    **過期 (TTL)**：「這筆資料在時間 $T$ 之後不再有效。」這是一個邏輯上的有效性約束。
*   **Eviction (Maxmemory)**: "I am out of memory; I must delete something to accept new writes." It is a resource constraint.
    **淘汰 (Maxmemory)**：「記憶體已滿，我必須刪除某些內容以接受新的寫入。」這是一個資源約束。

### 2.2 Key Expiration Strategies: Lazy vs. Active
### 2.2 鍵的過期策略：惰性刪除 vs. 主動刪除

Redis does not use a timer per key (too much CPU overhead). Instead, it combines two strategies:
Redis 不會為每個鍵使用計時器（CPU 開銷過大）。相反，它結合了兩種策略：

1.  **Lazy Freeing (Passive)**: When a client accesses a key, Redis checks if it has expired. If yes, it deletes it and returns `nil`.
    **惰性刪除（被動）**：當客戶端存取某個鍵時，Redis 會檢查它是否已過期。如果是，則刪除該鍵並回傳 `nil`。
2.  **Active Expiration (Periodic)**: Redis runs a background task (default 10 times/sec) that samples keys with TTLs. If the percentage of expired keys in the sample is high, it repeats the cycle.
    **主動過期（週期性）**：Redis 執行一個背景任務（預設每秒 10 次），對設有 TTL 的鍵進行採樣。如果樣本中過期鍵的比例很高，它會重複執行此循環。

### 2.3 Eviction Algorithms: Approximated LRU & LFU
### 2.3 淘汰演算法：近似 LRU 與 LFU

Redis does not implement a strict Doubly Linked List for LRU because the pointer overhead (2 pointers per key) is too expensive.
Redis 並未實作嚴格的雙向鏈結串列（Doubly Linked List）來處理 LRU，因為指標的開銷（每個鍵需要 2 個指標）太過昂貴。

*   **Approximated LRU**: Redis samples a small pool of keys (default 5) and evicts the one with the oldest idle time.
    **近似 LRU**：Redis 會隨機採樣一小池的鍵（預設 5 個），並淘汰其中閒置時間最長的一個。
*   **LFU (Least Frequently Used)**: Introduced in Redis 4.0. It uses a probabilistic counter (Morris Counter) stored in the 24-bit LRU field of the Redis Object to track access frequency.
    **LFU（最不常使用）**：於 Redis 4.0 引入。它利用儲存在 Redis 物件 24-bit LRU 欄位中的機率計數器（Morris Counter）來追蹤存取頻率。

### 2.4 Memory Fragmentation
### 2.4 記憶體碎片化

`used_memory` is what Redis allocated. `used_memory_rss` is what the OS allocated to the Redis process.
`used_memory` 是 Redis 實際分配的量。`used_memory_rss` 是作業系統分配給 Redis 行程的量。

$$ \text{Fragmentation Ratio} = \frac{\text{used\_memory\_rss}}{\text{used\_memory}} $$

*   **Ratio > 1.0**: Fragmentation exists. (e.g., 1.5 means 33% of memory is wasted).
    **比率 > 1.0**：存在碎片。（例如 1.5 表示 33% 的記憶體被浪費）。
*   **Ratio < 1.0**: Redis is swapped out to disk. **This is catastrophic for performance.**
    **比率 < 1.0**：Redis 被 Swap 到磁碟。**這對效能是毀滅性的。**

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Choosing the Right Policy for the Workload
### 3.1 針對工作負載選擇正確的策略

In a production system design, the choice of `maxmemory-policy` dictates how your cache degrades under pressure.
在生產系統設計中，`maxmemory-policy` 的選擇決定了你的快取在壓力下如何降級。

| Policy | Use Case | System Design Impact |
| :--- | :--- | :--- |
| **noeviction** | DB / Persistent Store | Writes fail when full. Ensures data consistency but risks availability. <br> **noeviction**：資料庫 / 持久化儲存。滿載時寫入失敗。確保資料一致性但有可用性風險。 |
| **allkeys-lru** | General Caching | Good for "Recency" patterns (e.g., news feed, social media). Most common default. <br> **allkeys-lru**：一般快取。適合「近期熱度」模式（如動態消息、社群媒體）。最常見的預設值。 |
| **allkeys-lfu** | Access Power Law | Better for items that should stick around despite not being accessed *recently* (e.g., homepage content). <br> **allkeys-lfu**：存取冪次定律。適合那些即使「近期」未被存取也應保留的項目（如首頁內容）。 |
| **volatile-lru** | Mixed Workload | Only evicts keys with TTL. Useful if you store both cache (with TTL) and persistent data (no TTL) in the same instance. <br> **volatile-lru**：混合工作負載。只淘汰有 TTL 的鍵。適用於同一實例中同時儲存快取（有 TTL）與持久資料（無 TTL）的情況。 |

### 3.2 The "Latency Spike" Phenomenon
### 3.2 「延遲尖峰」現象

When Redis hits `maxmemory`, every write command triggers the eviction loop. If Redis has to evict multiple keys to free up enough space for a large write, the write latency increases significantly.
當 Redis 達到 `maxmemory` 時，每一個寫入指令都會觸發淘汰循環。如果 Redis 必須淘汰多個鍵才能為一個大型寫入釋放足夠空間，寫入延遲將顯著增加。

**Design Implication**: Monitor `evicted_keys` metric. If it's constantly high, your cache is thrashing (capacity too small for the working set).
**設計意涵**：監控 `evicted_keys` 指標。如果該指標持續居高不下，代表快取正在劇烈震盪（Thrashing，容量小於工作集）。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: The "Memory Leak" Investigation
### 情境：「記憶體洩漏」調查

**Background**: A team reports that their Redis instance memory usage keeps growing until OOM, even though they set a TTL on every key.
**背景**：某團隊回報他們的 Redis 實例記憶體使用量持續增長直到 OOM，即使他們對每個鍵都設定了 TTL。

#### Step 1: Verify Configuration
#### 步驟 1：驗證設定

Check if `maxmemory` is actually set. By default (on 64-bit systems), it might be 0 (unlimited).
檢查是否實際設定了 `maxmemory`。預設情況下（在 64 位元系統上），它可能是 0（無限制）。

```bash
redis-cli CONFIG GET maxmemory
# Output: 0 (Unlimited - Dangerous!)
```

**Action**: Set a limit (e.g., 75% of physical RAM).
**行動**：設定上限（例如實體 RAM 的 75%）。

#### Step 2: Analyze Fragmentation
#### 步驟 2：分析碎片化

Suppose `maxmemory` is set, but the OS still kills Redis. Check `INFO memory`:
假設 `maxmemory` 已設定，但 OS 仍然殺掉 Redis。檢查 `INFO memory`：

```text
used_memory_human: 10.00G
used_memory_rss_human: 15.00G
mem_fragmentation_ratio: 1.5
```

**Analysis**: Redis thinks it's using 10GB, but it occupies 15GB. The 5GB gap is fragmentation. The eviction policy only looks at `used_memory`, so it won't trigger until Redis logically hits the limit, by which time RSS might blow up the server.
**分析**：Redis 認為它使用了 10GB，但實際上佔用了 15GB。這 5GB 的差距是碎片。淘汰策略只看 `used_memory`，所以直到 Redis 邏輯上達到上限前都不會觸發，屆時 RSS 可能已經撐爆伺服器。

#### Step 3: Enable Active Defragmentation
#### 步驟 3：啟用主動重組

Since Redis 4.0, we can defrag online (with Jemalloc).
自 Redis 4.0 起，我們可以線上進行重組（需配合 Jemalloc）。

```bash
redis-cli CONFIG SET activedefrag yes
redis-cli CONFIG SET active-defrag-ignore-bytes 100mb
redis-cli CONFIG SET active-defrag-threshold-lower 10
```

*   **Why feasible?** It compacts memory by moving data to contiguous blocks.
    **為何可行？** 它透過將資料移動到連續區塊來壓縮記憶體。
*   **Trade-off**: It consumes CPU. Monitor CPU usage during defrag.
    **權衡**：這會消耗 CPU。需監控重組期間的 CPU 使用率。

#### Step 4: Tuning the Eviction Policy
#### 步驟 4：調整淘汰策略

If the app relies on session data (with TTL) but also stores permanent config (no TTL), using `allkeys-lru` is dangerous because it might delete the config.
如果應用程式依賴 Session 資料（有 TTL）但也儲存永久設定（無 TTL），使用 `allkeys-lru` 是危險的，因為它可能會刪除設定。

**Solution**: Switch to `volatile-lru`.
**解法**：切換至 `volatile-lru`。

```bash
redis-cli CONFIG SET maxmemory-policy volatile-lru
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The `volatile-lru` Trap
### 5.1 `volatile-lru` 的陷阱

*   **Anti-pattern**: Setting `maxmemory-policy` to `volatile-lru` but filling Redis with keys that have **no TTL**.
    **反模式**：將 `maxmemory-policy` 設為 `volatile-lru`，但填入 Redis 的鍵都沒有設定 **TTL**。
*   **Consequence**: When memory is full, Redis cannot find any key to evict (since none have TTL). It behaves like `noeviction` and returns OOM errors for writes.
    **後果**：當記憶體已滿，Redis 找不到任何可淘汰的鍵（因為都沒有 TTL）。它的行為會變得像 `noeviction`，並對寫入回傳 OOM 錯誤。
*   **Fix**: Ensure all keys have TTLs, or use `allkeys-lru`.
    **修正**：確保所有鍵都有 TTL，或改用 `allkeys-lru`。

### 5.2 Ignoring the "Big Key" Impact on Eviction
### 5.2 忽視「大鍵（Big Key）」對淘汰的影響

*   **Anti-pattern**: Storing massive Hashes or Lists (e.g., 500MB per key).
    **反模式**：儲存巨大的 Hash 或 List（例如每個鍵 500MB）。
*   **Consequence**: When Redis decides to evict one of these keys, the `DEL` operation is synchronous (unless `lazyfree-lazy-eviction` is enabled). This blocks the main thread for hundreds of milliseconds.
    **後果**：當 Redis 決定淘汰這些鍵之一時，`DEL` 操作是同步的（除非啟用了 `lazyfree-lazy-eviction`）。這會阻塞主執行緒數百毫秒。
*   **Fix**: Break down big keys; Enable `lazyfree-lazy-eviction yes`.
    **修正**：拆分大鍵；啟用 `lazyfree-lazy-eviction yes`。

### 5.3 Assuming Expired Keys are Gone Instantly
### 5.3 假設過期鍵會瞬間消失

*   **Anti-pattern**: Relying on keyspace notifications for exact timing triggers, or assuming memory is freed exactly at TTL.
    **反模式**：依賴鍵空間通知（Keyspace Notifications）作為精確的時間觸發器，或假設記憶體會在 TTL 到期時精確釋放。
*   **Consequence**: Keys might persist until accessed or sampled. If you have millions of keys expiring at the same second (thundering herd), the active expiration loop might block the CPU.
    **後果**：鍵可能會一直存在，直到被存取或採樣到。如果你有數百萬個鍵在同一秒過期（驚群效應），主動過期循環可能會阻塞 CPU。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you implement an LRU cache if you couldn't use a Linked List?
### Q1: 如果不能使用鏈結串列，你會如何實作 LRU 快取？

*   **Context**: Testing understanding of Redis's approximation.
    **情境**：測試對 Redis 近似演算法的理解。
*   **Key Points**:
    *   Explain the memory overhead of pointers in a strict LRU.
    *   Describe the "Sampling" approach: Pick $N$ random keys, evict the one with the oldest access time (stored in the object header).
    *   Mention that increasing sample size ($N=10$) improves accuracy but costs CPU.
    *   **高分要點**：解釋嚴格 LRU 中指標的記憶體開銷；描述「採樣」方法（隨機選 N 個鍵，淘汰標頭中存取時間最早的）；提及增加樣本數（N=10）可提高準確度但消耗 CPU。

### Q2: Why does Redis sometimes return OOM errors even if `maxmemory` is not reached in the OS monitoring tools?
### Q2: 為什麼即使 OS 監控工具顯示未達 `maxmemory`，Redis 有時仍會回傳 OOM 錯誤？

*   **Context**: Debugging production issues.
    **情境**：生產環境除錯。
*   **Key Points**:
    *   Distinguish between Redis's logical `used_memory` (which triggers eviction) and the OS's view.
    *   However, the question is usually the reverse (OS sees high usage, Redis sees low).
    *   If Redis throws OOM *internally*, it strictly means `used_memory` > `maxmemory`.
    *   If the *OS* kills Redis, it's because `used_memory_rss` (fragmentation) exceeded physical limits.
    *   **Clarification**: If the user means "Why does Redis block writes?", it could be `volatile-lru` with no volatile keys.
    *   **高分要點**：區分 Redis 邏輯上的 `used_memory` 與 OS 的視角；如果 Redis 內部拋出 OOM，代表 `used_memory` > `maxmemory`；如果 OS 殺掉 Redis，是因為 `used_memory_rss`（碎片）超過實體限制；若是指「為何 Redis 拒絕寫入」，可能是 `volatile-lru` 策略下沒有可淘汰的鍵。

### Q3: Compare `allkeys-lru` vs. `allkeys-lfu`. When would you choose one over the other?
### Q3: 比較 `allkeys-lru` 與 `allkeys-lfu`。你會在何時選擇其中之一？

*   **Key Points**:
    *   **LRU**: Assumes "recently accessed" = "likely to be accessed again". Good for temporal locality (news, trends). Vulnerable to one-off scans (a scan replaces hot data with cold data).
    *   **LFU**: Tracks frequency. Good for "stable hot" data (e.g., dictionary definitions, homepage assets). Resistant to scans.
    *   **Implementation**: LFU requires decay (otherwise counts only go up).
    *   **高分要點**：LRU 假設「近期存取」=「可能再次存取」，適合時間局部性（新聞、趨勢），但易受一次性掃描影響；LFU 追蹤頻率，適合「穩定熱點」資料，抗掃描；LFU 實作需要衰減機制。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap
### 重點回顧

1.  **Memory is finite**: Always set `maxmemory` in production.
    **記憶體有限**：生產環境務必設定 `maxmemory`。
2.  **Policies matter**: Use `allkeys-lru` for general caching, `volatile-lru` only if mixing persistent/cache data.
    **策略很重要**：一般快取使用 `allkeys-lru`，混合持久/快取資料才用 `volatile-lru`。
3.  **Approximation**: Redis LRU/LFU are sampled, not strict. This saves memory.
    **近似演算法**：Redis LRU/LFU 是採樣的，非嚴格的。這節省了記憶體。
4.  **Fragmentation**: Monitor `mem_fragmentation_ratio`. Use `activedefrag` if > 1.5.
    **碎片化**：監控 `mem_fragmentation_ratio`。若 > 1.5 則使用 `activedefrag`。
5.  **Lazy Free**: Enable lazy eviction to prevent blocking on big key deletions.
    **惰性釋放**：啟用 lazy eviction 以防止刪除大鍵時發生阻塞。

### Next Steps
### 後續延伸

Now that you understand how Redis manages memory in RAM, the next logical step is to understand how it ensures data survives a restart.
既然你已了解 Redis 如何在 RAM 中管理記憶體，下一步合理的學習方向是了解它如何確保資料在重啟後倖存。

*   **Next Chapter**: **Persistence (RDB & AOF)** - How to balance durability with performance.
    **下一章**：**持久化 (RDB & AOF)** — 如何在持久性與效能之間取得平衡。