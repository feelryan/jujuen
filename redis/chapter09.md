# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，我們通常很擅長使用 Redis 的 API，但往往在系統規模擴大或流量暴增時，才會意識到「維運配置」與「底層調校」的重要性。Redis 雖然以高效著稱，但它對作業系統（OS）環境極度敏感。錯誤的 Kernel 參數或單個 Big Key 就可能導致整個服務停擺。

As senior engineers, we are often proficient with Redis APIs, but we usually realize the importance of "operational configuration" and "low-level tuning" only when the system scales or traffic spikes. While Redis is known for its high efficiency, it is extremely sensitive to the Operating System (OS) environment. Incorrect Kernel parameters or a single Big Key can bring the entire service to a halt.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **診斷效能瓶頸 (Diagnose Performance Bottlenecks)**：利用 `SLOWLOG`、`LATENCY MONITOR` 與 `LATENCY DOCTOR` 快速定位延遲根源。
2.  **調校 Linux Kernel (Tune Linux Kernel)**：理解並配置 `Transparent Huge Pages (THP)`、`vm.overcommit_memory` 與 `somaxconn`，以避免常見的效能陷阱。
3.  **處理 Big Keys (Handle Big Keys)**：掌握偵測、分析與安全刪除（Lazy Deletion）大鍵的策略，防止阻塞主執行緒。
4.  **實施安全性配置 (Implement Security)**：使用 Redis 6+ 引入的 ACL (Access Control List) 進行細粒度的權限控管，而非僅依賴單一密碼。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Redis 與 OS 的共生關係 (The Symbiosis of Redis and OS)

Redis 的心智模型是一個**極速的單執行緒事件迴圈 (Single-threaded Event Loop)**。想像一位快手收銀員（Redis），他處理結帳的速度極快，但如果店經理（OS）突然關燈（Swap/OOM）或更換收銀機紙捲的方式很笨重（THP 導致的 Copy-on-Write 延遲），收銀員再快也沒用。

The mental model of Redis is a **blazing-fast single-threaded event loop**. Imagine a lightning-fast cashier (Redis). They process checkouts incredibly quickly, but if the store manager (OS) suddenly turns off the lights (Swap/OOM) or changes the receipt paper in a clumsy way (Copy-on-Write latency caused by THP), the cashier's speed becomes irrelevant.

在生產環境中，Redis 的效能不僅取決於你的指令複雜度（Time Complexity），更取決於它與 Linux Kernel 記憶體管理機制的互動。

In a production environment, Redis performance depends not only on your command complexity (Time Complexity) but also on its interaction with the Linux Kernel's memory management mechanisms.

## 2.2 阻塞的代價 (The Cost of Blocking)

由於 Redis 核心是單執行緒的，任何耗時超過 10ms 的操作都可能導致「雪崩效應」。這不僅僅是該指令變慢，而是排在後面的數千個請求都會被擋住。

Since the Redis core is single-threaded, any operation taking longer than 10ms can cause an "avalanche effect." It’s not just that the specific command becomes slow; thousands of requests queued behind it get blocked.

*   **Big Key**: 就像一個顧客推了一輛裝滿 10,000 件商品的購物車，收銀員必須逐一掃描，導致後面隊伍停滯。
*   **Big Key**: It's like a customer pushing a cart with 10,000 items; the cashier has to scan them one by one, stalling the line behind.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構中的維運挑戰 (Operational Challenges in Typical Architectures)

在微服務架構中，Redis 常作為 Shared Cache 或 Session Store。若 Redis 發生抖動（Jitter）：
1.  **API Gateway 層**：可能因 Timeout 而回傳 503。
2.  **DB 層**：Cache Miss 或 Redis 連線失敗會導致流量瞬間打穿到資料庫（Cache Stampede）。

In a microservices architecture, Redis often serves as a Shared Cache or Session Store. If Redis experiences jitter:
1.  **API Gateway Layer**: May return 503s due to timeouts.
2.  **DB Layer**: Cache misses or Redis connection failures can cause traffic to instantly hammer the database (Cache Stampede).

## 3.2 可觀測性設計 (Design for Observability)

資深工程師在設計階段就應考慮：
Senior engineers should consider the following during the design phase:

*   **監控指標 (Metrics)**：不僅僅是 CPU 和 Memory，更要監控 `instantaneous_ops_per_sec`、`rejected_connections`、`evicted_keys` 以及 `keyspace_misses`。
*   **自動化警報 (Alerting)**：針對 `latest_fork_usec` 設定警報。若 RDB/AOF rewrite 的 fork 時間過長，代表系統處於不穩定狀態。

*   **Metrics**: Not just CPU and Memory, but also `instantaneous_ops_per_sec`, `rejected_connections`, `evicted_keys`, and `keyspace_misses`.
*   **Alerting**: Set alerts for `latest_fork_usec`. If the fork time for RDB/AOF rewrite is too long, the system is in an unstable state.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 案例一：診斷神秘的延遲尖峰 (Case 1: Diagnosing Mysterious Latency Spikes)

**情境 (Scenario)**：
你的監控系統顯示 Redis 每隔幾小時會出現 500ms+ 的延遲，但 CPU 使用率並不高。

Your monitoring system shows that Redis experiences 500ms+ latency spikes every few hours, but CPU usage remains low.

**步驟 1：啟用並檢查 Slowlog (Step 1: Enable and Check Slowlog)**
首先確認是否有慢查詢。

First, check for slow queries.

```bash
# 設定閾值為 10ms (10000 microseconds)，保留最近 500 筆
CONFIG SET slowlog-log-slower-than 10000
CONFIG SET slowlog-max-len 500

# 檢查
SLOWLOG GET 10
```

如果 Slowlog 是空的，代表問題不在指令本身（如 `KEYS *`），而是在系統層面。

If the Slowlog is empty, the problem is not with the commands themselves (like `KEYS *`), but at the system level.

**步驟 2：使用 Latency Doctor (Step 2: Use Latency Doctor)**
Redis 內建了一個強大的診斷工具。

Redis has a powerful built-in diagnostic tool.

```bash
LATENCY DOCTOR
```

**輸出範例 (Output Example)**：
```text
Dave, I have observed latency spikes because of 'command'.
...
I detected a 520ms latency spike caused by the operating system transparent huge pages (THP).
Please disable THP...
```

**步驟 3：Kernel 調校 - 關閉 THP (Step 3: Kernel Tuning - Disable THP)**
**原因**：Linux 的 Transparent Huge Pages (THP) 會將記憶體分頁從 4KB 變為 2MB。當 Redis 進行 BGSAVE (fork) 時，Copy-on-Write 機制需要複製記憶體頁面。複製 2MB 的頁面比 4KB 慢得多，導致主執行緒阻塞。

**Reason**: Linux's Transparent Huge Pages (THP) changes memory pages from 4KB to 2MB. When Redis performs BGSAVE (fork), the Copy-on-Write mechanism needs to duplicate memory pages. Copying a 2MB page is significantly slower than a 4KB page, causing the main thread to block.

**解決方案 (Solution)**：
```bash
# 暫時生效 (Temporary)
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# 永久生效 (Permanent - add to /etc/rc.local or systemd unit)
# 確保在 Redis 啟動前執行
```

## 4.2 案例二：安全處理 Big Keys (Case 2: Safely Handling Big Keys)

**情境 (Scenario)**：
你需要刪除一個包含 500 萬個欄位的 Hash Key `user:logs:archive`。直接執行 `DEL` 會導致 Redis 阻塞數秒。

You need to delete a Hash Key `user:logs:archive` containing 5 million fields. Executing `DEL` directly will block Redis for several seconds.

**Naive Approach (Dangerous)**:
```bash
DEL user:logs:archive
# Result: Redis stops responding for 3-5 seconds.
```

**Better Approach (Redis 4.0+): UNLINK**
`UNLINK` 是非阻塞刪除（Non-blocking delete）。它會將 Key 從 Keyspace 中移除（O(1)），真正的記憶體釋放會在背景執行緒中異步進行。

`UNLINK` is a non-blocking delete. It removes the Key from the Keyspace (O(1)), and the actual memory reclamation happens asynchronously in a background thread.

```bash
UNLINK user:logs:archive
# Result: Returns immediately. Memory is reclaimed in the background.
```

**Legacy Approach (Redis < 4.0) or Analysis**:
如果你需要掃描並逐步刪除（或你的 Redis 版本很舊），使用 `HSCAN`。

If you need to scan and delete incrementally (or your Redis version is old), use `HSCAN`.

```python
import redis

r = redis.Redis(host='localhost', port=6379)
key = 'user:logs:archive'
cursor = '0'

while cursor != 0:
    # 每次掃描 1000 個欄位 (Scan 1000 fields at a time)
    cursor, data = r.hscan(key, cursor=cursor, count=1000)
    if data:
        fields = data.keys()
        # 逐步刪除 (Delete incrementally)
        r.hdel(key, *fields)
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略 `vm.overcommit_memory = 1` (Ignoring `vm.overcommit_memory = 1`)

*   **錯誤描述**：保留 Linux 預設值 `0`。
*   **後果**：當 Redis 執行 BGSAVE 時，需要 `fork()` 一個子程序。雖然 Copy-on-Write 讓物理記憶體不需要翻倍，但虛擬記憶體空間需要。如果 OS 判斷記憶體不足，會拒絕 fork 或觸發 OOM Killer 殺死 Redis。
*   **正確做法**：設定 `sysctl vm.overcommit_memory=1`，告訴 Linux 核心「不管怎樣，允許記憶體分配」。

*   **Description**: Keeping the Linux default value `0`.
*   **Consequence**: When Redis performs BGSAVE, it needs to `fork()` a child process. Although Copy-on-Write prevents physical memory doubling, virtual memory space is required. If the OS judges memory is insufficient, it will refuse the fork or trigger the OOM Killer to kill Redis.
*   **Best Practice**: Set `sysctl vm.overcommit_memory=1` to tell the Linux kernel "always allow memory allocation."

## 5.2 在生產環境使用 `KEYS *` (Using `KEYS *` in Production)

*   **錯誤描述**：為了 debug 或統計，直接執行 `KEYS pattern*`。
*   **後果**：`KEYS` 是 O(N) 操作。如果資料庫有千萬級別的 Key，這會導致 Redis 鎖死數秒至數分鐘。
*   **正確做法**：使用 `SCAN` 指令，它是基於游標（Cursor）的迭代器，不會阻塞主執行緒。

*   **Description**: Executing `KEYS pattern*` directly for debugging or statistics.
*   **Consequence**: `KEYS` is an O(N) operation. If the database has millions of keys, this will lock Redis for seconds to minutes.
*   **Best Practice**: Use the `SCAN` command, which is a cursor-based iterator that does not block the main thread.

## 5.3 忽視 TCP Backlog (`somaxconn`) (Ignoring TCP Backlog)

*   **錯誤描述**：Redis 的 `tcp-backlog` 設定很高（預設 511），但 Linux 系統層級的 `net.core.somaxconn` 預設僅為 128。
*   **後果**：在高併發連線請求下，Redis 佇列會被 OS 截斷，導致客戶端連線超時或重試風暴。
*   **正確做法**：確保 `sysctl net.core.somaxconn` >= Redis 的 `tcp-backlog` 設定（建議設為 1024 或更高）。

*   **Description**: Redis `tcp-backlog` is set high (default 511), but the Linux system-level `net.core.somaxconn` defaults to only 128.
*   **Consequence**: Under high concurrency connection requests, the Redis queue gets truncated by the OS, causing client connection timeouts or retry storms.
*   **Best Practice**: Ensure `sysctl net.core.somaxconn` >= Redis `tcp-backlog` setting (recommended 1024 or higher).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在不影響線上服務的情況下，找出並刪除 Redis 中的 Big Keys？
**How to identify and delete Big Keys in Redis without impacting live services?**

*   **高分回答要點 (Key Points)**：
    1.  **偵測 (Detection)**：不能用 `KEYS *`。應使用 `redis-cli --bigkeys`（掃描統計）或 `redis-cli --scan | xargs ...` 配合 `MEMORY USAGE`（Redis 4.0+）。也可以解析 RDB 檔案（離線分析，完全不影響線上）。
    2.  **刪除 (Deletion)**：使用 `UNLINK` 取代 `DEL` 進行異步釋放。如果是舊版本，則需自行寫 script 使用 `HSCAN`/`SSCAN`/`ZSCAN` 分批刪除元素。
    3.  **預防 (Prevention)**：討論如何在應用層限制大小，或在 Proxy 層攔截。

## Q2: Redis 報錯 "MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk." 這是什麼原因？如何解決？
**Redis throws "MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk." What causes this and how to fix it?**

*   **高分回答要點 (Key Points)**：
    1.  **直接原因**：BGSAVE 失敗。通常是因為 `fork()` 失敗。
    2.  **根本原因**：記憶體不足且 `vm.overcommit_memory` 設為 0（啟發式）或 2（嚴格限制）。Linux 拒絕了記憶體分配請求。
    3.  **解決方案**：
        *   短期：`config set stop-writes-on-bgsave-error no`（讓寫入繼續，但有資料遺失風險）。
        *   長期：修正 `vm.overcommit_memory = 1`，並檢查是否需要增加 Swap 或物理記憶體。

## Q3: 請解釋 Redis ACL (Access Control List) 如何改善安全性，對比舊版的 `requirepass` 有何不同？
**Explain how Redis ACL (Access Control List) improves security compared to the old `requirepass` method.**

*   **高分回答要點 (Key Points)**：
    1.  **舊版限制**：`requirepass` 只有一個全域密碼，獲得權限即獲得所有權限（包含 `FLUSHALL`）。
    2.  **ACL 優勢 (Redis 6+)**：
        *   **User Separation**：可以建立多個使用者。
        *   **Command Limiting**：可以限制特定使用者只能執行特定指令（例如：只讀使用者不能執行 `SET` 或 `CONFIG`）。
        *   **Key Pattern Limiting**：可以限制使用者只能存取特定 pattern 的 Key（例如：`app:cache:*`）。
    3.  **實務應用**：為監控系統建立一個僅能執行 `INFO` 和 `PING` 的帳號。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **Latency is King**：善用 `SLOWLOG` 和 `LATENCY DOCTOR`；Redis 慢通常是因為被阻塞，而非 CPU 運算慢。
2.  **Kernel Matters**：務必檢查 `THP` (Disable)、`vm.overcommit_memory` (Set to 1) 和 `somaxconn`。
3.  **Delete Responsibly**：永遠使用 `UNLINK` 處理大鍵；永遠使用 `SCAN` 代替 `KEYS`。
4.  **Security**：從單一密碼升級到 ACL，實施最小權限原則。
5.  **Persistence Cost**：理解 `fork()` 對記憶體和延遲的影響（Copy-on-Write）。

## 後續延伸 (Next Steps)
*   **High Availability (HA)**：掌握了單機調校後，下一步應學習 **Redis Sentinel** 與 **Redis Cluster** 的架構與故障轉移機制（Failover）。
*   **Persistence Deep Dive**：深入研究 RDB 與 AOF 的內部格式與 rewrite 機制，這對資料復原至關重要。

*(Next Chapter: Redis High Availability & Clustering)*