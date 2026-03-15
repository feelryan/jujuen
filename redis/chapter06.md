# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單體架構（Monolithic Architecture）中，我們習慣使用語言層級的鎖（如 Java 的 `synchronized` 或 Go 的 `sync.Mutex`）來控制併發。然而，當系統擴展為分散式架構時，這些本地鎖將無法跨越 Process 或機器的邊界。Redis 因其高效能與原子性操作，成為實作分散式鎖（Distributed Lock）最熱門的選擇之一。

In monolithic architectures, we are accustomed to using language-level locks (such as Java's `synchronized` or Go's `sync.Mutex`) to control concurrency. However, when the system scales to a distributed architecture, these local locks cannot cross process or machine boundaries. Redis, due to its high performance and atomic operations, has become one of the most popular choices for implementing distributed locks.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **正確實作單節點 Redis 鎖**：掌握 `SET resource_name my_random_value NX PX 30000` 模式，並理解為何舊式的 `SETNX` + `EXPIRE` 是危險的。
    **Correctly implement a single-node Redis lock**: Master the `SET resource_name my_random_value NX PX 30000` pattern and understand why the legacy `SETNX` + `EXPIRE` approach is dangerous.
2.  **使用 Lua Script 保證解鎖安全性**：確保「解鈴還須繫鈴人」，防止 A 客戶端誤刪 B 客戶端的鎖。
    **Use Lua Scripts for safe unlocking**: Ensure "only the owner can release the lock" to prevent Client A from accidentally deleting Client B's lock.
3.  **理解 Redlock 演算法與爭議**：知道在 Redis Cluster 或多主節點環境下如何達成共識，以及該演算法的侷限性（如時鐘漂移問題）。
    **Understand the Redlock algorithm and its controversies**: Know how consensus is achieved in Redis Cluster or multi-master environments, and the limitations of the algorithm (e.g., clock drift issues).
4.  **掌握 Fencing Tokens 機制**：解決因 GC Pause 或網路延遲導致鎖過期後，舊請求破壞資料一致性的問題。
    **Master the Fencing Tokens mechanism**: Solve data consistency issues caused by "zombie" requests modifying data after their lock has expired due to GC pauses or network latency.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 互斥性與死鎖 (Mutual Exclusion & Deadlock Freedom)

分散式鎖的核心目標與 OS 的 Mutex 相同：在同一時間，只有一個客戶端能持有資源。但在分散式環境中，我們必須額外考慮 **Liveness (活性)**。如果持有鎖的客戶端崩潰（Crash），鎖必須能自動釋放，否則將導致全系統死鎖。這通常透過 **TTL (Time-To-Live)** 或 **Lease (租約)** 機制來實現。

The core goal of a distributed lock is the same as an OS Mutex: only one client can hold the resource at a time. However, in a distributed environment, we must additionally consider **Liveness**. If the client holding the lock crashes, the lock must be released automatically; otherwise, it will cause a system-wide deadlock. This is typically implemented via a **TTL (Time-To-Live)** or **Lease** mechanism.

### 2.2 安全性 (Safety)

安全性意味著「互斥性」必須被嚴格遵守。最常見的違規場景是：客戶端 A 取得鎖 -> A 執行過久導致鎖過期 -> 客戶端 B 取得鎖 -> A 執行完畢並刪除了 B 的鎖。這破壞了鎖的排他性。

Safety means that "Mutual Exclusion" must be strictly observed. The most common violation scenario is: Client A acquires the lock -> A runs too long, causing the lock to expire -> Client B acquires the lock -> A finishes and deletes B's lock. This breaks the exclusivity of the lock.

### 2.3 Redis vs. ZooKeeper/Etcd

- **Redis (AP/CP 混合特性)**：
    - 優點：極致效能，實作簡單，適合高併發且對「極端情況下的一致性」要求不那麼嚴苛的場景。
    - 缺點：在主從切換（Failover）時可能會遺失鎖（因為 Replication 是非同步的）。
- **ZooKeeper/Etcd (CP 系統)**：
    - 優點：強一致性，透過 Raft/ZAB 協議保證鎖不會遺失。支援 Session 與 Watch 機制。
    - 缺點：效能較 Redis 低，客戶端實作複雜。

- **Redis (Mixed AP/CP characteristics)**:
    - Pros: Extreme performance, simple implementation, suitable for high concurrency scenarios where "strict consistency in extreme edge cases" is negotiable.
    - Cons: Locks might be lost during failover (since replication is asynchronous).
- **ZooKeeper/Etcd (CP Systems)**:
    - Pros: Strong consistency; Raft/ZAB protocols ensure locks are never lost. Supports Session and Watch mechanisms.
    - Cons: Lower performance than Redis, complex client implementation.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 避免重複執行 (Preventing Duplicate Execution)

最常見的用途是防止 Cron Job 或排程任務在多台機器上同時執行。例如，每天凌晨結算報表，我們只希望其中一台 Worker 執行。此時 Redis 鎖充當 **Leader Election** 的輕量級實作。

The most common use case is preventing Cron Jobs or scheduled tasks from running simultaneously on multiple machines. For example, when generating daily settlement reports at midnight, we want only one Worker to execute. Here, the Redis lock acts as a lightweight implementation of **Leader Election**.

### 3.2 庫存扣減與搶購 (Inventory Deduction & Flash Sales)

在電商搶購（Flash Sale）場景中，為了防止超賣（Overselling），必須序列化對熱門商品的庫存檢查與扣減。雖然資料庫層級有 Row Lock，但在高流量下，直接打 DB 會導致連線數耗盡。Redis 分散式鎖可作為 DB 前的第一道防線（儘管更進階的做法是直接在 Redis 內做原子扣減，不使用鎖）。

In e-commerce flash sale scenarios, to prevent overselling, inventory checks and deductions for hot items must be serialized. While databases have Row Locks, hitting the DB directly under high traffic can exhaust connections. Redis distributed locks serve as the first line of defense before the DB (although a more advanced approach is to perform atomic deductions directly within Redis without explicit locks).

### 3.3 冪等性控制 (Idempotency Control)

當上游服務（如 Payment Gateway）重試呼叫時，分散式鎖可以配合冪等 Key（Idempotency Key），確保同一筆交易只被處理一次。

When upstream services (like a Payment Gateway) retry calls, distributed locks can work with an Idempotency Key to ensure a transaction is processed only once.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將從最直覺但錯誤的寫法，演進到工業級的標準寫法。
We will evolve from the most intuitive but incorrect approach to the industry-standard implementation.

### Phase 1: The Naive Approach (Wrong)

```bash
# Client A tries to get lock
SETNX lock:product:101 true
# Returns 1 (Success)

# Client A sets a timeout to prevent deadlock
EXPIRE lock:product:101 10
```

**為什麼這是錯的？ (Why is this wrong?)**
`SETNX` 和 `EXPIRE` 是兩個獨立的指令。如果 Client A 在執行完 `SETNX` 後，但在 `EXPIRE` 之前崩潰（Crash），這個鎖將永遠沒有過期時間，導致死鎖（Deadlock）。這不具備**原子性（Atomicity）**。

`SETNX` and `EXPIRE` are two separate commands. If Client A crashes after executing `SETNX` but before `EXPIRE`, the lock will never have an expiration time, resulting in a deadlock. This lacks **Atomicity**.

### Phase 2: The Correct Single-Instance Implementation

從 Redis 2.6.12 開始，`SET` 指令支援擴充參數，能一次完成上述操作。
Since Redis 2.6.12, the `SET` command supports extended arguments to complete the above operations in one go.

```bash
# SET key value [NX|XX] [EX seconds | PX milliseconds]
SET lock:product:101 "random_token_xyz" NX PX 30000
```

- `NX`: Only set if the key does not exist (互斥性).
- `PX 30000`: Set expiration to 30,000 milliseconds (安全性/活性).
- `"random_token_xyz"`: 這非常重要！我們必須存入一個**唯一的隨機字串**（UUID 或 Client ID），用於解鎖時驗證身分。

- `NX`: Only set if the key does not exist (Mutual Exclusion).
- `PX 30000`: Set expiration to 30,000 milliseconds (Safety/Liveness).
- `"random_token_xyz"`: This is crucial! We must store a **unique random string** (UUID or Client ID) to verify identity when unlocking.

### Phase 3: Safe Unlocking with Lua

解鎖時，不能直接使用 `DEL`。因為如果鎖已經過期並被 Client B 搶走，Client A 直接 `DEL` 會誤刪 Client B 的鎖。我們必須遵循：「檢查 Value 是否是我的 -> 如果是，刪除；否則，忽略」。這需要 Lua Script 保證原子性。

When unlocking, you cannot simply use `DEL`. If the lock has expired and been acquired by Client B, Client A directly calling `DEL` would accidentally delete Client B's lock. We must follow: "Check if the Value belongs to me -> If yes, delete; otherwise, ignore." This requires a Lua Script to ensure atomicity.

```lua
-- unlock.lua
-- KEYS[1]: lock key
-- ARGV[1]: the random token generated by the client

if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

**Complexity Analysis:**
- Time Complexity: O(1) for both locking and unlocking.
- Space Complexity: O(1) per lock (small string key-value).

### Phase 4: The Redlock Algorithm (Multi-Master)

如果你的 Redis 是單點（Single Instance），上述做法就足夠了。但如果 Master 掛了，Slave 尚未同步到鎖資訊就升級為 Master，鎖就會遺失。為了在分散式環境提供更高可靠性，Redis 作者提出了 **Redlock**。

If your Redis is a single instance, the above approach is sufficient. However, if the Master fails and a Slave is promoted before syncing the lock information, the lock is lost. To provide higher reliability in distributed environments, the author of Redis proposed **Redlock**.

**基本邏輯 (Basic Logic):**
1.  客戶端取得當前時間。
2.  依序向 N 個 Redis Master 節點（通常是 5 個）請求鎖。
3.  如果能從 N/2 + 1 個節點（過半數）成功取得鎖，且耗時小於鎖的有效期，則視為成功。

**Basic Logic:**
1.  Client gets the current time.
2.  Sequentially requests the lock from N Redis Master nodes (usually 5).
3.  If the lock is successfully acquired from N/2 + 1 nodes (majority) and the elapsed time is less than the lock validity period, it is considered successful.

**爭議與現狀 (Controversy & Status):**
分散式系統專家 Martin Kleppmann 曾質疑 Redlock 在依賴「系統時鐘（System Clock）」上的脆弱性。如果節點時鐘發生跳躍（Clock Jump），Redlock 的安全性可能失效。
*結論：對於大多數業務（如防止重複發信），Redlock 足夠好；但對於金融級強一致性需求，建議使用 ZooKeeper 或 Etcd。*

Distributed systems expert Martin Kleppmann questioned Redlock's vulnerability regarding its reliance on "System Clocks". If a node's clock jumps, Redlock's safety guarantees might fail.
*Verdict: For most business cases (like preventing duplicate emails), Redlock is good enough; but for financial-grade strong consistency, ZooKeeper or Etcd is recommended.*

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 忽略 "Stop-the-World" GC (Ignoring Stop-the-World GC)

**情境**：Client A 取得鎖（TTL 10s），執行程式碼。程式碼執行到一半發生 Full GC，暫停了 15s。此時鎖在 Redis 中過期，Client B 取得鎖。GC 結束後，Client A 繼續執行，導致兩個客戶端同時操作資源。

**Scenario**: Client A acquires a lock (TTL 10s) and executes code. Halfway through, a Full GC occurs, pausing the process for 15s. The lock expires in Redis, and Client B acquires it. After GC ends, Client A resumes execution, resulting in two clients manipulating the resource simultaneously.

**解決方案 (Solution): Fencing Tokens**
這是一個資料庫層面的防護。
1.  每次取得鎖時，Redis 回傳一個遞增的數字（Token）。
2.  Client A 拿到 Token = 33。
3.  Client B（在 A 過期後）拿到 Token = 34。
4.  當寫入 DB 時，DB 檢查 `UPDATE table SET val=... WHERE id=... AND current_token < 33`。
5.  如果 DB 已經看過 34，則拒絕 33 的寫入。

**Solution: Fencing Tokens**
This is a database-level protection.
1.  Every time a lock is acquired, Redis returns an incrementing number (Token).
2.  Client A gets Token = 33.
3.  Client B (after A expires) gets Token = 34.
4.  When writing to the DB, the DB checks `UPDATE table SET val=... WHERE id=... AND current_token < 33`.
5.  If the DB has already seen 34, it rejects the write from 33.

### 5.2 鎖的粒度過大 (Lock Granularity Too Coarse)

**錯誤**：`SET lock:order NX`。這會鎖住所有訂單的處理，導致系統變成序列化執行，吞吐量驟降。
**修正**：鎖應該細化到具體資源，如 `SET lock:order:12345 NX`。

**Mistake**: `SET lock:order NX`. This locks the processing of *all* orders, causing the system to execute serially and throughput to plummet.
**Correction**: Locks should be granular to the specific resource, e.g., `SET lock:order:12345 NX`.

### 5.3 沒有實作 Watchdog (No Watchdog Implementation)

**問題**：預估業務邏輯需 5 秒，設定 TTL 10 秒。但偶爾網路延遲或邏輯複雜導致執行了 12 秒，鎖提前釋放。
**解決方案**：使用成熟的 Client Library（如 Java 的 **Redisson**）。它有一個 "Watchdog" 機制，當客戶端還活著且持有鎖時，會在背景自動延長鎖的 TTL（Renew Lease）。

**Problem**: Business logic is estimated to take 5s, so TTL is set to 10s. However, occasional network lag or complexity causes it to run for 12s, releasing the lock prematurely.
**Solution**: Use a mature Client Library (like **Redisson** for Java). It has a "Watchdog" mechanism that automatically extends the lock's TTL (Renews the Lease) in the background as long as the client is alive and holds the lock.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如果 Redis Master 在鎖同步到 Slave 之前掛了，會發生什麼事？你怎麼解決？
**What happens if the Redis Master dies before the lock is synced to the Slave? How do you solve it?**

*   **回答要點**：
    *   承認這是 Redis Sentinel/Cluster 架構下的已知問題（Failover 導致鎖遺失）。
    *   如果業務允許偶爾的 Race Condition（如重複發送通知），可以接受。
    *   如果業務要求強一致性（如金流），應提出 **Redlock**（多節點共識）作為改善方案，或直接建議切換到 **ZooKeeper/Etcd**。
    *   展示對 CAP 定理的理解：Redis 傾向 AP，ZK 傾向 CP。

*   **Key Points**:
    *   Acknowledge this is a known issue in Redis Sentinel/Cluster architectures (Failover leads to lock loss).
    *   If the business tolerates occasional race conditions (e.g., duplicate notifications), it's acceptable.
    *   If strict consistency is required (e.g., finance), propose **Redlock** (multi-node consensus) as an improvement, or suggest switching to **ZooKeeper/Etcd**.
    *   Demonstrate understanding of the CAP theorem: Redis leans towards AP, ZK leans towards CP.

### Q2: 如何實作一個可重入鎖（Reentrant Lock）？
**How do you implement a Reentrant Lock?**

*   **回答要點**：
    *   解釋可重入性：同一個 Thread/Process 可以多次進入同一把鎖。
    *   Redis 的 String 結構不夠用，需要使用 **Hash** 結構。
    *   Key: `lock_name`
    *   Field: `client_id` (UUID)
    *   Value: `counter` (計數器)
    *   加鎖時：如果 Field 存在且是自己，Counter + 1；否則 NX 創建。
    *   解鎖時：Counter - 1；如果 Counter 為 0 則刪除 Key。
    *   這必須透過 Lua Script 達成原子性。

*   **Key Points**:
    *   Explain reentrancy: The same Thread/Process can enter the same lock multiple times.
    *   Redis String structure is insufficient; use a **Hash** structure.
    *   Key: `lock_name`, Field: `client_id` (UUID), Value: `counter`.
    *   Lock: If Field exists and is self, Counter + 1; otherwise create with NX.
    *   Unlock: Counter - 1; if Counter becomes 0, delete the Key.
    *   This must be done via Lua Script for atomicity.

### Q3: 什麼是 Fencing Token？為什麼我們需要它？
**What is a Fencing Token? Why do we need it?**

*   **回答要點**：
    *   它是用來解決 "Process Pauses" (如 GC) 導致鎖過期後，舊的 Process 復活並破壞資料的問題。
    *   這是一個單調遞增的數字。
    *   儲存層（Database）需要檢查 Token 的單調性，拒絕舊 Token 的寫入。
    *   這是從「依賴時間（不可靠）」轉向「依賴因果關係（可靠）」的設計。

*   **Key Points**:
    *   It solves the issue where "Process Pauses" (like GC) cause a lock to expire, and the old process "wakes up" and corrupts data.
    *   It is a monotonically increasing number.
    *   The storage layer (Database) needs to check the monotonicity of the Token and reject writes with old Tokens.
    *   This is a design shift from "relying on time (unreliable)" to "relying on causality (reliable)".

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### Key Takeaways
1.  **Atomic Command**: 永遠使用 `SET ... NX PX ...`，不要分開寫 `SETNX` 和 `EXPIRE`。
2.  **Owner Validation**: 解鎖必須檢查擁有者，使用 Lua Script 確保 `GET` 和 `DEL` 的原子性。
3.  **Watchdog**: 對於執行時間不確定的任務，需要自動續約機制（Renew Lease）。
4.  **Redlock**: 在多 Master 環境下提供較高的可靠性，但並非絕對安全（受時鐘影響）。
5.  **Fencing**: 對於極度敏感的資料寫入，Redis 鎖僅是優化，DB 層的 Fencing Token 或是 CAS (Compare-And-Swap) 才是最後防線。

### Next Steps
- **實作練習**：使用你熟悉的語言（Go/Java/Python）手寫一個包含 Lua 解鎖腳本的 Redis Lock Client。
- **延伸閱讀**：閱讀 Martin Kleppmann 關於 Redlock 的分析文章 "How to do distributed locking"。
- **下一章預告**：**Chapter 07: Redis Streams & Message Queues** - 學習如何使用 Redis 實作高效能的訊息佇列與事件驅動架構。