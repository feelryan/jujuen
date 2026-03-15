# 常見反模式與設計陷阱 / Common Anti-patterns & Design Pitfalls

## Mental model｜心智模型

要避開 Redis 的陷阱，必須先理解它的核心運作機制。請將 Redis 想像成一位 **「動作極快、但只有一雙手」的櫃檯結帳員**（Single-threaded Event Loop）。

1.  **單執行緒的代價（The Cost of Single Thread）**：
    Redis 處理指令是序列化（Sequential）的。如果某個指令需要花 1 秒鐘（例如讀取一個超大 Key），這 1 秒鐘內，後面排隊的 10,000 個請求全部會被卡住（Blocked）。
    > **Rule of Thumb**: Redis 的效能瓶頸通常不在 CPU 計算（除非濫用 Lua 腳本），而在於 **網路頻寬（Network Bandwidth）** 與 **指令阻塞（Command Blocking）**。

2.  **記憶體即金錢（Memory is Money）**：
    Redis 是 In-memory database。不像硬碟便宜，記憶體昂貴且有限。將 Redis 當作「無限容量的垃圾桶」是架構崩壞的開始。

3.  **非關聯式思考（No Relations, No Joins）**：
    Redis 是 Key-Value Store。不要試圖在 Redis 中透過應用層邏輯硬做 SQL `JOIN`，或者依賴複雜的 Key 命名規則來模擬 `WHERE` 查詢。資料應該是 **「為讀取而設計」（Designed for Access）**，而非為實體關係而設計。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 迭代讀取模式 (Iterative Access Pattern)
-   **Context**: 需要遍歷大量 Keys 或集合中的元素。
-   **Solution**: 絕對禁止使用 `KEYS *` 或 `SMEMBERS` (針對大集合)。
-   **Practice**: 使用 `SCAN`, `SSCAN`, `HSCAN`, `ZSCAN` 系列指令。這些指令像分頁一樣，每次只回傳少量元素，不會阻塞 Main Thread。

### 2. 大鍵拆分與壓縮 (Big Key Sharding & Compression)
-   **Context**: 需要儲存一個很大的物件（如 5MB 的 JSON）或包含百萬成員的 Hash/Set。
-   **Solution**:
    -   **拆分 (Sharding)**: 將 `big_hash` 拆分為 `big_hash:1`, `big_hash:2`... 分散到不同的 Slots 或單純減小單一 Key 的大小。
    -   **壓縮 (Compression)**: 文字型資料（JSON/XML）在寫入前先用 Snappy/Gzip 壓縮，讀出後再解壓。通常能減少 50%~80% 記憶體並節省頻寬。

### 3. 多級快取策略 (Multilevel Caching for Hot Keys)
-   **Context**: 某個 Key（如「熱門商品詳情」）每秒被讀取數萬次（Hot Key），導致單一 Redis Node 網卡打滿。
-   **Solution**: **Local Cache (In-process) + Redis**。
    -   在 Application Server 端（如 JVM Guava Cache 或 Go-cache）加上一層極短 TTL（例如 1~3 秒）的本地快取。這能擋掉 90% 以上到達 Redis 的流量。

### 4. 異質資料儲存 (Polyglot Persistence)
-   **Context**: 資料量大且需要複雜查詢，但開發者習慣性全塞進 Redis。
-   **Solution**: Redis 僅存「ID 列表」或「熱資料」。
    -   將完整資料存在 MySQL/DynamoDB/Elasticsearch。
    -   Redis 只存 `User:123:RecentViewedIDs` (List of IDs)，拿到 ID 後再去主要資料庫撈詳情（或由主要資料庫負責索引）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `KEYS` Command Abuse (濫用 KEYS 指令)
-   **Anti-pattern**: 在生產環境使用 `KEYS user:*` 來計算用戶數或查找特定 Key。
-   **Consequence**: `KEYS` 是 O(N) 操作。當 Key 總數達到百萬級別，這個指令會導致 Redis 凍結數秒甚至數分鐘，期間所有服務請求 timeout，甚至引發 Cluster Failover。
-   **Fix**: 永遠封鎖（Rename）生產環境的 `KEYS` 指令。使用 `SCAN` 或建立額外的 `Set` 來維護索引。

### 2. The Big Key Problem (大鍵問題)
-   **Anti-pattern**:
    -   一個 String Key 存了 10MB 的 HTML。
    -   一個 Hash Key 存了 1,000,000 個 Fields。
    -   一個 List 存了無上限的 Log，從未 Trim。
-   **Consequence**:
    -   **網路阻塞**: 讀取一次就佔滿頻寬。
    -   **刪除阻塞**: 刪除一個 Big Key (DEL) 需要釋放大量記憶體，會阻塞 Main Thread（除非使用 Lazy Free `UNLINK`）。
    -   **遷移失敗**: 在 Cluster 模式下，Big Key 無法順利遷移，導致資料傾斜（Data Skew）。

### 3. The Hot Key Problem (熱鍵問題)
-   **Anti-pattern**: 所有客戶端同時頻繁讀寫同一個 Key（例如全站設定 config、秒殺庫存）。
-   **Consequence**: 流量集中在單一 Redis Node，該節點 CPU/頻寬過載，而其他節點閒置。Cluster 擴容也無法解決（因為 Key 只能落在一個 Slot）。

### 4. Redis as a Relational DB (把 Redis 當關聯式資料庫)
-   **Anti-pattern**:
    -   設計 `User` Hash, `Order` Hash，然後在 Client 端拉出所有資料自己寫迴圈做 Join。
    -   依賴多個 Key 的事務一致性，卻沒有使用 Lua Script 或 `MULTI/EXEC`，導致資料邏輯損壞。
-   **Consequence**: 網路來回次數（RTT）過高，效能極差，且資料一致性難以維護。

### 5. Ignoring TTL (忽略過期時間)
-   **Anti-pattern**: 寫入快取資料卻不設定 TTL (Time To Live)。
-   **Consequence**: 隨著時間推移，無用的垃圾資料佔滿記憶體，觸發 `maxmemory-policy` (如 LRU 驅逐)，導致真正需要的熱資料被踢出，Cache Miss Rate 飆升。

---

## Checklists & workflows｜檢查清單與流程

在設計或 Code Review 階段，請使用此清單自我檢查：

### Design & Development Phase
- [ ] **複雜度檢查**: 我使用的指令是 O(1) 還是 O(N)？如果是 O(N)，N 的預期最大值是多少？
- [ ] **大鍵預防**: 寫入的 Value 是否可能超過 10KB？如果是，是否考慮壓縮？集合類型的元素數量是否有上限（Cap）？
- [ ] **熱鍵預防**: 這個 Key 是否會被高頻存取？是否需要 Local Cache？
- [ ] **TTL 設定**: 這筆資料需要永久保存嗎？如果不是，是否設定了合理的 TTL？
- [ ] **Key 命名規範**: Key 是否包含業務前綴（如 `app:user:123`）以避免衝突並易於管理？

### Troubleshooting & Maintenance Phase
- [ ] **Big Keys Analysis**: 定期執行 `redis-cli --bigkeys` 掃描潛在的大鍵。
- [ ] **Slow Log Monitoring**: 檢查 `slowlog get 10`，是否有執行時間超過 10ms 的指令？
- [ ] **Memory Fragmentation**: 檢查 `info memory` 中的 `mem_fragmentation_ratio`，是否需要重啟或優化。
- [ ] **Network Saturation**: 監控網卡流量，是否接近頻寬上限？

---

## Real-world examples｜實戰案例

### Case 1: The "Online Users" Outage (線上用戶列表導致的當機)
-   **Scenario**: 開發者為了在後台顯示「目前所有線上用戶」，使用 `KEYS session:*` 撈出所有 Key，然後計算數量。
-   **Failure**: 上線初期沒問題，當同時在線人數突破 50 萬時，後台管理員按了一次「重新整理」，Redis 直接卡死 5 秒，導致前台所有用戶登入失敗，購物車結帳 timeout。
-   **Fix**:
    1.  緊急處置：停用後台該功能。
    2.  架構修正：改用一個 Redis `HyperLogLog` 來估算線上人數（如果不需要精確名單）；或使用一個 `ZSET` (Score=Timestamp) 儲存活躍用戶 ID，並定期移除舊資料。

### Case 2: The "Social Follower" Big Key (名人粉絲列表大鍵)
-   **Scenario**: 社交 App 使用 `SET` 儲存用戶的粉絲列表 `followers:{userId}`。
-   **Failure**: 普通用戶沒問題，但當某位巨星加入並擁有 1000 萬粉絲時，該 `SET` 佔用數百 MB。每次有人關注/取消關注該巨星，或者系統嘗試讀取該列表進行推播，都會造成顯著延遲，甚至導致 Cluster 資料遷移失敗。
-   **Fix**:
    1.  **拆分 (Sharding)**: 將粉絲列表拆分為 `followers:{userId}:1`, `followers:{userId}:2`...
    2.  **業務取捨**: 對於超大 V 用戶，不直接從 Redis 讀取完整列表，改為讀取 MySQL 並分頁，或只在 Redis 快取「最新 1000 位粉絲」。

### Case 3: The "Global Config" Hot Key (全域設定熱鍵)
-   **Scenario**: 所有的 Microservices 在處理每個 Request 時，都會去 Redis 讀取一個 `sys:config` 的 Hash Key 來確認功能開關。
-   **Failure**: 大促銷期間，QPS 飆升至 20 萬，單一 Redis 節點 CPU 100%，網路頻寬打滿，但其他 Redis 節點很閒。
-   **Fix**:
    1.  **Local Cache**: 在 Service 內部使用記憶體快取該設定，TTL 設為 5 秒。
    2.  **Pub/Sub 更新**: 當設定變更時，透過 Redis Pub/Sub 通知各 Service 清除本地快取，達到近乎即時的一致性，同時消除 99.9% 的 Redis 讀取壓力。