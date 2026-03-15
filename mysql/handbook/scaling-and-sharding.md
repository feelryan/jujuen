# 擴展性設計：讀寫分離與分庫分表 | Scaling: Read/Write Splitting & Sharding

## Mental Model｜心智模型

在考慮 MySQL 的擴展性時，我們必須從「單機思維」轉向「分散式系統思維」。這不僅僅是增加機器，而是權衡 **Consistency (一致性)** 與 **Availability (可用性)** 的過程。

### 1. The "Kitchen Brigade" Analogy (廚房分工模型)
*   **Single Instance (單機)**：一位全能主廚負責所有點餐（Write）和出餐（Read）。當客人變多，主廚會崩潰。
*   **Read/Write Splitting (讀寫分離)**：
    *   **Master (主廚)**：專注於處理新的訂單（INSERT/UPDATE/DELETE）。
    *   **Slaves/Replicas (二廚/學徒)**：負責將主廚做好的半成品擺盤出餐（SELECT）。
    *   **Replication Lag (延遲)**：主廚做完動作後，學徒模仿需要時間。如果客人剛點完菜（Write）立刻問學徒「我的菜呢？」（Read），學徒可能還不知道這道菜的存在。這就是 **Stale Read (過期讀取)**。
*   **Sharding (分庫分表)**：
    *   當一家餐廳（單一資料庫）塞不下所有食材和客人時，你開了分店。
    *   **Sharding Key (切分鍵)**：這是門口的帶位員。他決定哪位客人（Data）該去哪家分店（Shard）。如果帶位員規則設計錯誤，某家分店會爆滿（Hotspot），其他分店卻沒人。

### 2. The Complexity Tax (複雜度稅)
擴展不是免費的。引入讀寫分離會帶來**數據延遲**問題；引入分庫分表會導致**跨庫 Join 失效**與**分散式交易**難題。**Scale Up (垂直擴展/升級硬體) 永遠優先於 Scale Out (水平擴展)**，直到物理極限或成本效益反轉。

---

## Patterns & best practices｜常見模式與最佳實務

### Read/Write Splitting Patterns (讀寫分離模式)

1.  **Read-Your-Own-Writes (Session Consistency)**
    *   **問題**：使用者更新個人資料後重新整理，卻看到舊資料（因為讀到了尚未同步的 Slave）。
    *   **解法**：在 Application Layer 或 Proxy 層實作路由邏輯。
        *   若該 Session 剛發生過 Write 操作，強制在接下來的 N 秒內（或透過 GTID 追蹤）將該 User 的 Read 請求路由至 Master。
        *   其他無關使用者的 Read 請求繼續走 Slaves。

2.  **Middleware vs. Application-Side Routing**
    *   **ProxySQL / MaxScale**：對應用程式透明，由 Proxy 負責路由與負載平衡。適合運維團隊強大的場景。
    *   **Application-Side (e.g., ShardingSphere-JDBC, Custom Logic)**：由程式碼決定連線。優點是靈活且無額外網路跳躍（Hop），缺點是侵入程式碼。

### Sharding Patterns (分庫分表模式)

1.  **Sharding Key Selection (切分鍵選擇)**
    *   **High Cardinality (高基數)**：選擇能將數據均勻打散的欄位（如 `user_id`）。
    *   **Query Isolation (查詢隔離)**：90% 的查詢應該只落在單一 Shard 上。
    *   **Bad Idea**: 使用 `status` 或 `timestamp` 作為主要 Sharding Key（除非是 Time-series data），容易造成 Write Hotspot。

2.  **Routing Strategies (路由策略)**
    *   **Hash-based (`user_id % N`)**：數據分佈最均勻，但擴容（Resharding）時需要大規模數據遷移（Consistent Hashing 可緩解但複雜）。
    *   **Range-based (`user_id` 1-10000 in Shard A)**：擴容簡單（加新 Range 即可），但容易產生熱點（Hotspot），例如新註冊用戶都在最新的 Shard。
    *   **Directory-based (Lookup Table)**：建立一個索引表記錄 `ID -> Shard` 的對應關係。靈活但多一次查詢開銷。

3.  **Broadcasting & Binding Tables (廣播表與綁定表)**
    *   **Broadcasting**：對於資料量小且變動少的表（如 `dictionaries`, `configurations`），在每個 Shard 都複製一份，避免跨庫 Join。
    *   **Binding (Gene)**：如果 `orders` 表依 `order_id` 分片，你想用 `user_id` 查訂單會變成全庫掃描。
        *   **Best Practice**: 在 `order_id` 生成時嵌入 `user_id` 的特徵（Gene），或者強制 `orders` 也用 `user_id` 作為 Sharding Key（Data Locality）。

4.  **Global ID Generation (全域唯一 ID)**
    *   分庫後不能再依賴單機的 `AUTO_INCREMENT`。
    *   使用 **Snowflake Algorithm** (Twitter) 或 **UUID** (注意 UUID 對索引效能的影響，建議用 Ordered UUID)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Premature Sharding (過早分庫分表)
*   **現象**：資料量才幾百萬行，QPS 也不高，就開始設計複雜的分庫架構。
*   **後果**：開發效率暴跌，Join 變得很難寫，運維成本激增。
*   **建議**：先做索引優化 -> 緩存 (Redis) -> 讀寫分離 -> 歸檔歷史數據 (Archiving) -> 最後才考慮 Sharding。

### 2. The "Cross-Shard Join" Trap (跨庫關聯陷阱)
*   **現象**：在 Application 中試圖 Join 分散在不同實體庫的表。
*   **後果**：通常需要在記憶體中做聚合，極度消耗 App Server 資源且延遲高。
*   **建議**：
    *   **Denormalization (反正規化)**：將需要的欄位冗餘到同一張表。
    *   **Application-side Join**：分兩次查詢，先查 A 拿到 IDs，再查 B (`WHERE id IN (...)`)。

### 3. Ignoring Replication Lag in Business Logic (忽略業務邏輯中的延遲)
*   **現象**：庫存扣減後，立刻讀取庫存顯示給前端，結果顯示「庫存未扣」。
*   **後果**：超賣（Overselling）或使用者困惑。
*   **建議**：關鍵業務數據（如庫存、餘額）**永遠走 Master**，或者使用 Cache 作為計數器。

### 4. Resharding Nightmare (擴容惡夢)
*   **現象**：使用 `id % 2` 分了兩個庫，滿了之後想變 3 個庫。
*   **後果**：幾乎 100% 的數據都需要移動，且遷移過程中難以保證數據一致性。
*   **建議**：一開始就切分足夠多的 **Logical Shards (邏輯分片)**（例如 1024 個），初期將它們映射到少量 **Physical Nodes (實體節點)**。擴容時只需搬移邏輯分片，無需重新計算 Hash。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Do I need Sharding? (我需要分庫分表嗎？)
- [ ] **單表數據量**：是否超過 2000 萬行 (或 50GB+) 且索引優化已無效？
- [ ] **寫入瓶頸**：Master 的 CPU/IO 是否長期處於 80%+，且無法透過升級硬體解決？
- [ ] **業務拆分**：是否已經嘗試過垂直拆分（Vertical Partitioning，將不同業務模組拆到不同 DB）？
- [ ] **歷史歸檔**：是否可以將 6 個月前的數據移至 Cold Storage (e.g., S3, Data Warehouse)？
- [ ] **結論**：如果以上皆 "Yes" 或 "Done"，才開始規劃 Sharding。

### Zero-Downtime Migration Workflow (無停機遷移流程)
這是最安全的「分庫分表」或「資料庫切換」實作模式：

1.  **Dual Write (雙寫)**：
    *   修改程式碼，同時寫入 Old DB 與 New Sharded DB。
    *   以 Old DB 為準，New DB 寫入失敗僅 Log 不報錯（Async 寫入佳）。
2.  **Backfill (回填歷史數據)**：
    *   啟動背景程式，將 Old DB 的歷史數據遷移到 New DB。
    *   如果 New DB 已有該筆資料（由 Dual Write 產生），則跳過或依時間戳更新。
3.  **Verification (數據校驗)**：
    *   跑腳本比對兩邊數據的一致性。
4.  **Switch Reads (切換讀取)**：
    *   使用 Feature Flag，灰度切換部分流量讀取 New DB。
    *   觀察延遲與錯誤率。
5.  **Switch Writes (切換寫入)**：
    *   停止 Dual Write，全面切換到 New DB。
    *   (Optional) 反向雙寫回 Old DB 以便 Rollback。

---

## Real-world examples｜實戰案例

### Example 1: Handling Replication Lag with "Sticky Session"
*情境：使用者修改個人頭像後，回到首頁看到的還是舊頭像。*

**Bad Code:**
```python
# User updates profile
db.master.execute("UPDATE users SET avatar = 'new.jpg' WHERE id = 1")
# Redirect to home
return redirect('/home')

# /home controller
user = db.slave.query("SELECT * FROM users WHERE id = 1") 
# Result: avatar is still 'old.jpg' due to lag
```

**Better Pattern (Pseudo-code):**
```python
# User updates profile
db.master.execute("UPDATE users SET avatar = 'new.jpg' WHERE id = 1")
# Set a cache key indicating this user just wrote data
cache.set(f"user_wrote:{user_id}", value=True, ttl=5) 

# /home controller
if cache.get(f"user_wrote:{user_id}"):
    # Force read from Master
    user = db.master.query("SELECT * FROM users WHERE id = 1")
else:
    # Safe to read from Slave
    user = db.slave.query("SELECT * FROM users WHERE id = 1")
```

### Example 2: The "Gene" Strategy for Order Sharding
*情境：訂單表 `orders` 已經按照 `order_id` 分庫，但現在需要查詢「某個 User 的所有訂單」。*

*   **問題**：如果 `order_id` 是隨機或單純自增，`SELECT * FROM orders WHERE user_id = 123` 需要查詢所有 Shards 並聚合，效能極差。
*   **解法**：在生成 `order_id` 時，將 `user_id` 的後幾位（例如後 4 bits 或 hash 值）嵌入 `order_id` 中。

**ID Structure (64-bit Snowflake-like):**
`[Timestamp (41 bits)] - [Machine ID (10 bits)] - [User ID Gene (6 bits)] - [Sequence (7 bits)]`

**Routing Logic:**
```javascript
// Function to determine which shard an order belongs to
function getShardId(orderId) {
    // Extract the gene directly from orderId
    const userGene = extractGene(orderId); 
    return userGene % TOTAL_SHARDS;
}

// Function to determine which shard a USER's orders are in
function getShardIdByUserId(userId) {
    // Calculate the same gene from userId
    const userGene = userId % 64; 
    return userGene % TOTAL_SHARDS;
}
```
*結果：無論是依 `order_id` 查單筆訂單，還是依 `user_id` 查列表，都會路由到同一個 Shard，避免了 Cross-shard query。*