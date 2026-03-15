# 資料結構選型與實務應用 / Data Structure Selection & Practical Use Cases

## Mental model｜心智模型

在 Redis 中選擇資料結構時，請拋棄「關聯式資料庫」的思維，轉向 **「存取模式優先 (Access Pattern First)」** 的思考方式。

不要問：「這個資料實體長什麼樣子？」(Data Modeling)
要問：「我需要如何寫入？我需要如何查詢？」(Query Modeling)

Redis 不是單純的 `Map<String, String>` 快取，它是一個 **Server-side Data Structures Server**。你的心智模型應該包含以下三個維度：

1.  **原生操作 (Native Operations)**：該結構是否支援你需要的原子操作？（例如：只更新物件中的某個欄位、原子計數、集合交集）。
2.  **時間複雜度 (Time Complexity)**：Redis 是單執行緒 (Single-threaded) 的。一個 O(N) 的指令如果 N 很大，會阻塞整個 Server，導致所有請求停擺。
3.  **記憶體開銷 (Memory Overhead)**：不同結構在小數據量時會使用壓縮編碼 (ziplist/listpack)，這對記憶體效率至關重要。

### The "Swiss Army Knife" Analogy
- **String**: 萬用刀。簡單、直接，但處理結構化資料時笨重。
- **Hash**: 收納盒。適合物件，節省記憶體，欄位存取快。
- **List**: 輸送帶。FIFO/LIFO，適合佇列。
- **Set/ZSet**: 數學集合與排行榜。處理唯一性與排序。
- **Bitmap/HyperLogLog**: 顯微鏡與統計學。極致壓縮空間，適合大數據統計。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. String vs. Hash：物件儲存的抉擇
**Scenario**: 儲存 User Profile (ID, Name, Age, LoginCount).

- **Pattern A (String + JSON)**: `SET user:1001 '{"name":"Alex", "age":30}'`
  - *Pros*: 讀取整個物件很方便，開發直覺。
  - *Cons*: 更新單一欄位（如 `LoginCount`）需要 Read-Modify-Write，有 Race Condition 風險；序列化/反序列化消耗 Client CPU。
- **Pattern B (Hash)**: `HMSET user:1001 name "Alex" age 30`
  - *Pros*: 可以使用 `HINCRBY` 原子更新計數器；節省記憶體（Redis 對小 Hash 有特殊編碼優化）；只讀取需要的欄位 (`HMGET`) 節省頻寬。
  - ***Verdict**: 除非物件極小且總是全量讀寫，否則優先選擇 **Hash**。*

### 2. List vs. Stream：訊息佇列 (Message Queue)
- **List (`LPUSH` + `BRPOP`)**:
  - *Use Case*: 簡單的 Job Queue，不需要回溯，不需要多個消費者群組 (Consumer Groups)。
  - *Limitation*: 訊息讀後即焚，無法由多個服務重複消費同一條訊息。
- **Stream**:
  - *Use Case*: 完整的 Event Sourcing、Log 收集、類似 Kafka 的 Consumer Group 模型。
  - *Best Practice*: 設定 `MAXLEN` 避免 Stream 無限增長吃光記憶體。

### 3. ZSet (Sorted Set)：不僅僅是排行榜
- **Pattern**: **Time-Series Indexing (時間序列索引)**
  - 將 `Score` 設定為 Timestamp，`Member` 設定為 Event ID。
  - 使用 `ZRANGEBYSCORE` 快速查詢某個時間段內的資料。
- **Pattern**: **Priority Queue (優先級佇列)**
  - `Score` 代表優先級，`BZMPOP` (Redis 7+) 或 `ZPOPMIN` 取出最高優先級任務。

### 4. Big Data Counting: Bitmap & HyperLogLog
- **Bitmap**:
  - *Use Case*: 簽到系統、用戶在線狀態 (Online/Offline)。
  - *Efficiency*: 1 億用戶的 boolean 狀態只需要約 12 MB 記憶體。
  - *Op*: `SETBIT`, `BITCOUNT`, `BITOP` (做 AND/OR 運算)。
- **HyperLogLog**:
  - *Use Case*: 計算網站 UV (Unique Visitors)、搜尋關鍵字數量。
  - *Trade-off*: 佔用極小空間 (固定 12KB)，但有 0.81% 的標準誤差。
  - *Decision*: 如果不需要精確到個位數，絕對優先選 HLL 而非 Set。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Keys" Command Trap (生產環境禁忌)
- **Anti-pattern**: 使用 `KEYS pattern*` 來尋找資料。
- **Why**: `KEYS` 是 O(N) 操作。在含有百萬級 Key 的生產環境執行，會導致 Redis **瞬間凍結 (Block)** 數秒甚至數分鐘。
- **Fix**: 使用 `SCAN` 指令進行游標式迭代 (Cursor-based iteration)。

### 2. Large Key / Big Key (巨型鍵值)
- **Definition**: 一個 String Value 超過 10KB，或者一個 Hash/Set/ZSet/List 包含超過 5000 個元素。
- **Impact**:
  - **Network**: 讀取時阻塞網路頻寬。
  - **Blocking**: 刪除 (`DEL`) 一個大 Key 時，主執行緒會卡住進行記憶體回收。
- **Fix**:
  - 拆分 Key (Sharding)。
  - 使用 `UNLINK` (非同步刪除) 代替 `DEL`。
  - 對於 List/Set，定期修剪 (`LTRIM`, `ZREMRANGEBYRANK`)。

### 3. O(N) Complexity Ignorance (忽視複雜度)
- **Pitfall**: 在大型 Set 上執行 `SMEMBERS`，或在大型 List 上執行 `LRANGE 0 -1`。
- **Result**: 隨著資料增長，系統效能急劇下降。
- **Fix**: 始終限制回傳數量 (Limit)，或改用 `SSCAN` / `ZSCAN`。

### 4. Using List as a Set (用 List 當 Set)
- **Anti-pattern**: 在 List 中使用 `LREM` 來確保唯一性，或者在應用層檢查是否存在再插入。
- **Why**: List 的搜尋是 O(N)，當 List 變長，檢查「是否存在」的成本極高。
- **Fix**: 如果需要唯一性，請直接使用 Set。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the Right Structure
在決定使用哪個結構時，請依序回答以下問題：

1.  **資料是否需要排序？**
    - 是，且依插入順序：**List**
    - 是，且依權重/時間/數值：**Sorted Set (ZSet)**
    - 否：繼續。
2.  **資料是否需要唯一性 (Unique)？**
    - 是，且需要精確值：**Set**
    - 是，但容許少量誤差且資料量極大 (Count distinct)：**HyperLogLog**
    - 否：繼續。
3.  **資料是否為結構化物件 (Object with fields)？**
    - 是，且需要操作單一欄位：**Hash**
    - 是，但總是整存整取：**String (JSON)**
4.  **是否為布林值陣列或連續 ID 的狀態？**
    - 是：**Bitmap**
5.  **是否為事件流或日誌？**
    - 是：**Stream**

### Implementation Checklist
- [ ] **Big O Check**: 我是否使用了 O(N) 指令？如果是，N 的最大預估值是多少？
- [ ] **Key Naming**: Key 的命名是否具備可讀性且不過長？(e.g., `user:1001:cart` vs `u:1001:c`)
- [ ] **Expiration**: 這個資料是否需要 TTL (Time To Live)？如果沒有 TTL，記憶體是否會無限增長？
- [ ] **Atomicity**: 是否有多個指令需要一起執行？如果是，是否使用了 Lua Script 或 Transaction (`MULTI`/`EXEC`)？
- [ ] **Memory Efficiency**: 對於大量小物件，是否考慮了 Hash 的 ziplist 設定？

---

## Real-world examples｜實戰案例

### Case 1: Rate Limiter (限流器)
**Requirement**: 限制每個 API Key 每分鐘最多呼叫 60 次。

**Approach A (Naive String)**:
```redis
INCR api_limit:{apiKey}:{minute_timestamp}
EXPIRE api_limit:{apiKey}:{minute_timestamp} 60
```
*適合簡單場景，但在時間窗口邊界會有突發流量問題。*

**Approach B (Sliding Window with ZSet)**:
```redis
# 1. Add current request timestamp
ZADD limiter:{apiKey} {current_timestamp} {request_id}
# 2. Remove old requests (outside window)
ZREMRANGEBYSCORE limiter:{apiKey} 0 {current_timestamp - 60s}
# 3. Count requests in window
ZCARD limiter:{apiKey}
# If count > 60, reject.
```
*精確控制滑動視窗，但記憶體消耗較高（存了所有請求的 ID）。*

### Case 2: E-commerce Cart (購物車)
**Requirement**: 使用者加入商品、修改數量、顯示購物車列表。

**Structure**: **Hash**
`Key`: `cart:{userId}`
`Field`: `{productId}`
`Value`: `{quantity}`

```redis
# Add/Update item
HSET cart:1001 "prod:5566" 2

# Increment quantity
HINCRBY cart:1001 "prod:5566" 1

# Get total items count (unique products)
HLEN cart:1001

# Get all items for display
HGETALL cart:1001

# Remove item
HDEL cart:1001 "prod:5566"
```

### Case 3: Geo-fencing (附近的人/店家)
**Requirement**: 找出使用者半徑 5km 內的咖啡廳。

**Structure**: **Geo (based on ZSet)**
Redis 的 Geo 其實是將經緯度編碼為 GeoHash 後存入 ZSet。

```redis
# Add locations
GEOADD places 121.5645 25.0339 "Taipei101"
GEOADD places 121.5600 25.0400 "CityHall"

# Find nearby (Radius 5km)
GEOSEARCH places FROMMEMBER "Taipei101" BYRADIUS 5 km ASC
```
*優勢：極快，無需在資料庫進行複雜的空間計算。*