# 分散式鎖與併發控制 / Distributed Locks & Concurrency Control

## Mental model｜心智模型

在分散式系統中，Redis 因為其單執行緒（Single-threaded）的特性，常被視為「裁判」或「號誌燈」。要掌握 Redis 分散式鎖，你必須建立以下的心智模型：

### 1. 租約模型 (The Lease Model)
不要將鎖視為「永久擁有的權利」，而應視為「**有期限的租約 (Lease)**」。
- **傳統鎖**：執行緒拿到鎖 -> 做事 -> 釋放鎖。如果程式崩潰，鎖永遠不會釋放（Deadlock）。
- **Redis 鎖**：Process 拿到鎖（設定 TTL）-> 做事 -> 釋放鎖。如果程式崩潰，Redis 會在 TTL 到期時自動收回鎖。
- **關鍵認知**：你必須假設「在你的程式碼執行完畢前，鎖可能會過期」。

### 2. 唯一識別證 (Identity Card)
鎖不僅僅是一個 Flag（`IsLocked = true`），它必須包含「**是誰鎖的**」資訊。
- 每個 Client 在加鎖時，必須寫入一個隨機且唯一的 ID（UUID 或 Token）。
- 解鎖時，必須檢查「現在鎖裡面存的 ID 是不是我的」，如果是才能刪除；否則你會誤刪別人的鎖（如果你的鎖剛好過期，別人剛好拿到的話）。

### 3. 原子性是核心 (Atomicity is King)
「檢查鎖是否存在」與「設定鎖」必須是同一動作；「檢查鎖是否屬於我」與「刪除鎖」也必須是同一動作。任何中間的空隙（Gap）都會導致 Race Condition。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 標準加鎖模式 (The Canonical Locking Pattern)
自 Redis 2.6.12 起，不再分開使用 `SETNX` 和 `EXPIRE`。請使用單一原子指令：

```bash
SET resource_name my_random_value NX PX 30000
```
- **NX**: Only set if not exists (互斥性).
- **PX 30000**: Expire after 30000ms (避免 Deadlock).
- **my_random_value**: 你的唯一識別碼 (安全性).

### 2. 安全解鎖模式 (Safe Release with Lua)
解鎖時，**絕對不能**直接使用 `DEL`。必須使用 Lua Script 確保原子性：

```lua
-- KEYS[1] is the lock key
-- ARGV[1] is the my_random_value
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```
這能防止「A 的鎖過期了，B 拿到了鎖，結果 A 做完事把 B 的鎖刪掉」的慘劇。

### 3. 自動續約機制 (Watchdog Pattern)
如果你的業務邏輯執行時間不確定（例如可能跑 5秒，也可能跑 40秒），你不能簡單地把 TTL 設為極大值。
- **Pattern**: 設定一個合理的短 TTL（如 30秒）。
- **Implementation**: 啟動一個背景執行緒（Daemon/Watchdog），每隔一段時間（如 10秒）檢查「如果我還持有鎖，就延長 TTL」。
- **Library**: Java 的 **Redisson** 框架內建此機制，強烈建議不要自己造輪子，直接使用成熟的 Client Library。

### 4. 樂觀鎖 (Optimistic Locking)
對於衝突機率低的場景（如庫存扣減），不一定要用分散式鎖（悲觀鎖）。可以使用 Redis 的 `WATCH` 指令或 Lua Script 進行原子扣減。
- **Lua Approach**: `if current >= need then current = current - need; return OK; else return FAIL; end`

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤用 `SETNX` + `EXPIRE`
**Anti-pattern**:
```python
if redis.setnx(lock_key, 1):
    # 如果在這裡程式崩潰或網路斷線，EXPIRE 沒執行到，鎖將永久存在 (Deadlock)
    redis.expire(lock_key, 10)
```
**Solution**: 務必使用 `SET key value NX PX milliseconds` 原子指令。

### 2. 忽略時鐘漂移與 GC Pauses (The GC Pause Trap)
如果你的 Application 發生 Full GC 停頓了 10 秒，而鎖的 TTL 只有 5 秒：
1. Client A 拿到鎖。
2. Client A 進入 GC 停頓（鎖在 Redis 端過期）。
3. Client B 拿到鎖。
4. Client A 醒來，以為自己還有鎖，繼續寫入資料庫。
**Result**: 資料損毀。
**Mitigation**: 使用 **Fencing Token**。在寫入資料庫時，帶上一個遞增的版本號，資料庫拒絕舊版本號的寫入。

### 3. 盲目信任 Redlock
Redlock 演算法是為了處理 Redis Cluster / Sentinel 架構下的 Failover 鎖丟失問題（Master 掛掉，鎖還沒同步到 Slave）。
- **Pitfall**: Redlock 實作複雜且依賴系統時鐘，對於極度要求強一致性（Strong Consistency）的場景（如金融帳務），Redis 可能不是最佳選擇。
- **Recommendation**: 對於大多數業務，單機 Redis 鎖或帶有 Watchdog 的 Redisson 已足夠。若需絕對正確性，考慮使用 ZooKeeper 或 Etcd。

### 4. 忙碌等待 (Busy Waiting)
當拿不到鎖時，無限迴圈 `while(true)` 瘋狂重試。
- **Consequence**: Redis CPU 飆高。
- **Solution**: 使用 **Exponential Backoff**（指數退避）與 **Jitter**（隨機延遲），或使用 Redis Pub/Sub 機制通知鎖釋放。

---

## Checklists & workflows｜檢查清單與流程

在實作 Redis 分散式鎖之前，請依序檢查以下項目：

### Phase 1: 設計決策 (Design Decisions)
- [ ] **必要性檢查**：真的需要分散式鎖嗎？能否透過資料庫的 Row Lock 或 Redis 原子操作（`INCR` / Lua）解決？
- [ ] **容錯需求**：如果 Redis 掛了，系統應該「Fail Open」（允許操作，風險是併發衝突）還是「Fail Closed」（拒絕操作，犧牲可用性）？
- [ ] **一致性級別**：是否涉及金錢交易？如果是，請再三考慮是否改用 ZooKeeper/Etcd 或資料庫唯一索引。

### Phase 2: 實作檢查 (Implementation Checklist)
- [ ] **互斥性 (Mutually Exclusive)**：是否使用了 `NX` 參數？
- [ ] **避免死鎖 (Deadlock Free)**：是否設定了合理的 `TTL`（PX/EX）？
- [ ] **解鎖安全性**：是否使用 Lua Script 驗證 `Value`（Owner ID）後才刪除？
- [ ] **擁有者標識**：Value 是否為 UUID 或足夠隨機的字串？
- [ ] **逾時處理**：是否考慮了業務邏輯執行時間超過 TTL 的情況？（是否需要 Watchdog？）

### Phase 3: 維運與監控 (Ops & Monitoring)
- [ ] **Timeout 設定**：Client 連線 Redis 的 Timeout 是否設定得夠短？
- [ ] **Metrics**：是否有監控「鎖競爭失敗率」與「鎖持有時間」？

---

## Real-world examples｜實戰案例

### Scenario: 防止定時任務重複執行 (Cron Job Deduplication)
**情境**：你有 5 台 API Server，每小時要執行一次「產生報表」的任務。如果不加控制，5 台機器會同時跑，浪費資源且可能重複寄信。

**Workflow**:
1. **Trigger**: 5 台機器同時被 Cron 觸發。
2. **Acquire Lock**:
   ```python
   # Key 包含時間戳記，確保每個小時是不同的鎖
   lock_key = f"report_job_lock_{current_hour}"
   token = uuid.uuid4().hex
   # 嘗試拿鎖，TTL 設為 5 分鐘 (預期任務 1 分鐘跑完)
   is_locked = redis.set(lock_key, token, nx=True, px=300000)
   ```
3. **Decision**:
   - 如果 `is_locked == True`: 我是 Leader，開始執行報表生成。
   - 如果 `is_locked == False`: 別人正在跑，我直接 Return (Skip)。
4. **Execution & Release**:
   - 執行完畢後，使用 Lua Script 釋放鎖（雖然有 TTL 當保險，但主動釋放是好習慣，方便重試）。

### Scenario: 搶購/秒殺系統 (Flash Sale Inventory)
**情境**：熱門商品限量 100 個，瞬間湧入 10,000 個請求。

**Anti-pattern (Read-Modify-Write)**:
1. Get `stock` from Redis.
2. If `stock > 0`, `stock - 1`.
3. Set `stock` back.
*(在高併發下會發生 Race Condition，導致超賣)*

**Best Practice (Lua Scripting)**:
與其用分散式鎖鎖住整個商品 Key（導致序列化處理，效能差），不如將邏輯封裝在 Lua 中原子執行：

```lua
-- KEYS[1]: inventory_key
-- ARGV[1]: qty_to_buy
local stock = tonumber(redis.call("get", KEYS[1]))
if stock >= tonumber(ARGV[1]) then
    redis.call("decrby", KEYS[1], ARGV[1])
    return 1 -- Success
else
    return 0 -- Fail
end
```
**優勢**：
- **原子性**：Redis 保證 Lua script 執行期間不會插入其他指令。
- **效能**：減少網路 RTT，且不需要 Client 端複雜的鎖等待邏輯。