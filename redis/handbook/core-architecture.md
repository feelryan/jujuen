# 核心架構與執行模型心法 / Core Architecture & Execution Model

## Mental Model｜心智模型

要駕馭 Redis，首先必須打破對「單執行緒（Single-threaded）」的表面理解，並建立正確的 **I/O Multiplexing（多路復用）** 心智模型。

### 1. 超級收銀員模型 (The Super Cashier Analogy)
想像 Redis 是一位 **動作極快、但只有一個人** 的超級收銀員。
- **單執行緒 (Single-threaded)**：同時只能處理一位客人的結帳（執行一個指令）。
- **非阻塞 I/O (Non-blocking I/O)**：收銀員不會等客人掏錢包（網路傳輸），而是先去服務下一位準備好的客人。一旦客人錢準備好了（資料到達），收銀員會立刻回來處理。
- **後果**：如果有一位客人買了 100 萬件商品（執行了 `KEYS *` 或讀取 Big Key），收銀員就會被卡住，後面所有排隊的客人都會停滯（Latency Spike）。

### 2. Redis 6.0+ 的演進：I/O Threads
現代 Redis (6.0+) 引入了多執行緒來處理網路 I/O (Read Query/Write Response)，但 **指令執行 (Command Execution) 仍然是單執行緒的**。
- **Mental Shift**：不要因為 Redis 6.0 支援多執行緒就認為可以隨意執行慢查詢。核心邏輯依然是序列化的，Thread Safety 不需要鎖，但效能瓶頸依然在於「單一指令的執行時間」。

### 3. 效能瓶頸光譜
在 Redis 的架構下，瓶頸通常依序出現在：
1.  **Network Bandwidth/Latency** (最常見：RTT 是最大殺手)
2.  **Memory Latency** (記憶體存取速度)
3.  **CPU** (通常只有在大量計算如加密、Lua 腳本或高頻率小指令時才會滿載)

---

## Patterns & Best Practices｜常見模式與最佳實務

### 1. 善用 Pipelining 減少 RTT (Round Trip Time)
Redis 的處理速度往往快於網路傳輸。
- **Pattern**：將多個指令打包發送，一次接收所有回應。
- **Why**：避免「發送 -> 等待 -> 執行 -> 回傳 -> 等待」的 Ping-Pong 效應。
- **Code Snippet**:
  ```python
  # Bad: 100ms latency if RTT is 10ms
  for i in range(10):
      redis.set(f"key:{i}", "value")

  # Good: ~10ms latency total
  pipe = redis.pipeline()
  for i in range(10):
      pipe.set(f"key:{i}", "value")
  pipe.execute()
  ```

### 2. 時間複雜度意識 (Time Complexity Awareness)
由於核心是單執行緒，你必須對每個指令的 Big O notation 有絕對的敏感度。
- **Best Practice**：
  - 優先使用 $O(1)$ 指令：`GET`, `SET`, `LPUSH`, `RPOP`, `HGET`.
  - 小心使用 $O(N)$ 指令：`LREM`, `SMEMBERS`, `HGETALL` (當 N 很大時)。
  - 絕對禁止在生產環境主庫使用 $O(N)$ 且 N 為全量資料的指令：`KEYS *`, `FLUSHALL`.

### 3. 使用 Lua Script 實現原子性 (Atomicity)
當你需要「讀取 -> 計算 -> 寫入」且不希望中間被插入其他指令時。
- **Pattern**：將邏輯封裝在 Lua script 中。
- **Benefit**：減少網路往返，且保證原子性（Redis 會將整個 Script 視為單一指令執行）。
- **Warning**：Lua script 執行時間必須極短，否則會阻塞整個 Server。

### 4. Lazy Freeing (非同步刪除)
刪除一個幾百 MB 的 Big Key 會導致主執行緒卡頓。
- **Best Practice**：
  - 使用 `UNLINK` 代替 `DEL`（Redis 4.0+）。`UNLINK` 會在背景執行緒回收記憶體。
  - 設定 `lazyfree-lazy-eviction` 等參數，讓被驅逐的 Key 也在背景刪除。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Big Key" Trap (大 Key 陷阱)
這是最常見的效能殺手。一個 Key 包含 100 萬個元素的 Hash，或者一個 50MB 的 String。
- **後果**：
  - **網路阻塞**：讀取時瞬間塞滿網路頻寬。
  - **主執行緒阻塞**：刪除或序列化該 Key 時，CPU 被佔用，導致 Heartbeat 超時，甚至引發 HA 切換（Failover）。
- **識別**：使用 `redis-cli --bigkeys` 掃描。

### 2. 濫用 `KEYS *` 進行查詢
開發者常在 Debug 或功能實作時使用 `KEYS pattern*` 來尋找資料。
- **Pitfall**：這是一個 $O(N)$ 操作，N 是資料庫中 Key 的總數。在百萬級 Key 的生產環境下，這會導致 Redis 凍結數秒甚至更久。
- **Solution**：使用 `SCAN` 指令（Cursor-based iteration）分批迭代，雖然總時間可能更長，但不會阻塞 Server。

### 3. 忽視連線建立成本 (Connection Churn)
頻繁地 `Open Connection -> Command -> Close Connection`。
- **Pitfall**：TCP Handshake 和 Redis Auth 消耗 CPU 和時間。
- **Solution**：使用 **Connection Pooling** (連線池)。保持長連線 (Keep-alive)。

### 4. 在主執行緒做繁重計算
- **Pitfall**：在 Lua Script 中跑複雜的迴圈，或對極大的 Set 做 `SINTER` (交集) / `SUNION` (聯集)。
- **Solution**：將計算邏輯移至 Application Layer，Redis 只負責存取資料；或是在 Application 端先做部分過濾。

---

## Checklists & Workflows｜檢查清單與流程

### Day-to-Day Development Checklist
- [ ] **複雜度檢查**：我使用的指令是 $O(1)$ 還是 $O(N)$？如果是 $O(N)$，N 的最大預估值是多少？
- [ ] **Big Key 預防**：寫入的 Value 是否有邊界限制？（例如：List 長度是否限制？String 大小是否限制？）
- [ ] **Pipeline 評估**：是否有連續執行的指令可以合併為 Pipeline？
- [ ] **原子性需求**：是否有多個指令需要原子性執行？是否考慮了 Lua Script？
- [ ] **刪除策略**：刪除大量資料或大物件時，是否使用了 `UNLINK`？

### Performance Troubleshooting Workflow (當 Redis 變慢時)
1.  **Check Slowlog**:
    - 執行 `SLOWLOG GET 10`。
    - *判定*：如果有指令耗時超過 10ms，這通常是兇手（因為這只是執行時間，不含排隊）。
2.  **Check Latency**:
    - 執行 `redis-cli --latency` 觀察即時延遲。
3.  **Check CPU Usage**:
    - 如果 CPU 100% 且 Slowlog 有複雜指令 -> 優化指令。
    - 如果 CPU 100% 但 Slowlog 空空 -> 可能是極高併發的小指令，或網路 I/O 瓶頸（考慮 Redis 6+ I/O threads）。
4.  **Check Network**:
    - 檢查 `CLIENT LIST` 中的 `omem` (Output Buffer Memory)。如果有 Client 的 Output Buffer 很大，代表該 Client 讀取了大量資料（Big Key）且處理不及。
5.  **Check Persistence**:
    - 是否正在進行 `BGSAVE` 或 AOF Rewrite？Fork process 時可能會造成短暫延遲。

---

## Real-world Examples｜實戰案例

### Case 1: The "Mysterious" Timeout (隱形殺手 Big Key)
**情境**：某個電商網站在促銷活動期間，Redis 偶爾會出現 500ms 的 Timeout，導致結帳失敗，但 CPU 使用率並不高。
**分析**：
- 檢查 `SLOWLOG` 發現沒有特別慢的指令。
- 檢查網路流量，發現偶爾有巨大的 Outbound 流量尖峰。
- **原因**：有一個 `HGETALL` 指令讀取了一個儲存 "全站熱門商品列表" 的 Hash Key，該 Key 內含 5 萬個欄位。雖然指令執行本身不算極慢，但**序列化與網路傳輸**塞爆了單執行緒的 Output Buffer 處理能力。
**解法**：將該 Big Key 拆分為多個小 Keys (Sharding)，或僅使用 `HMGET` 讀取需要的欄位，而非全量拉取。

### Case 2: The Cron Job Disaster (誤用 KEYS)
**情境**：每天凌晨 3 點，監控系統會發出 Redis Latency 警報，持續約 10 秒。
**分析**：
- 團隊新上線了一個清理過期 Session 的排程。
- 程式碼中使用了 `keys("session:*")` 來找出所有 Session key 進行刪除。
- 隨著用戶量增長，Key 總數達到千萬級別，`KEYS` 指令直接卡死 Main Thread。
**解法**：改用 `SCAN` 指令配合 `UNLINK` 進行分批迭代刪除。

### Case 3: High Throughput Optimization (Pipeline)
**情境**：一個廣告追蹤系統需要每秒寫入 5 萬筆 Tracking Data 到 Redis。單機測試時發現 QPS 卡在 1 萬左右上不去。
**分析**：
- 每個 Tracking Event 都是一次獨立的 `RPUSH` 請求。
- 應用程式與 Redis 之間的 RTT 為 0.5ms。理論極限 QPS = 1s / 0.5ms = 2000 (單連線)。即使開多個連線，Context Switch 也變成了瓶頸。
**解法**：
- 在 Application 端實作 Buffer，每累積 100 筆或每 100ms 觸發一次寫入。
- 使用 Redis Pipeline 一次發送 100 個 `RPUSH`。
- **結果**：QPS 提升至 10 萬+，且 CPU 使用率反而下降（減少了 System Call 次數）。