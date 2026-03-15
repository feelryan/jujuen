# 快取策略與資料一致性 / Caching Strategies & Data Consistency

## Mental model｜心智模型

在 AWS 環境中設計快取時，不要只把它當作「加速器」，而應將其視為**「用準確性換取延遲與成本的交易系統」 (Trading accuracy for latency and cost)**。

我們通常採用 **多層防禦 (Layered Defense)** 的心智模型來思考快取架構：

1.  **Edge Layer (CloudFront)**: 最接近使用者，延遲最低，適合靜態資源或讀多寫少的內容。這裡的快取命中 (Cache Hit) 最便宜且最快。
2.  **Application Layer (ElastiCache / DAX)**: 位於應用程式與資料庫之間，用於減輕 DB 負載，處理複雜查詢結果或 Session 狀態。
3.  **Database Layer**: 真實的資料來源 (Source of Truth)。

### 核心權衡 (Key Trade-offs)
- **Staleness (資料陳舊度)**: 你能容忍使用者看到多久以前的資料？
- **TTL (Time To Live)**: 資料應該存活多久？太短導致 DB 壓力大，太長導致資料不一致。
- **Eviction (驅逐策略)**: 當記憶體滿了，誰該離開？

> **The "Hardest Problem" Rule**: "There are only two hard things in Computer Science: cache invalidation and naming things." —— 在 AWS 中，我們盡量透過 **TTL** 和 **Versioning (版本號)** 來規避主動 Invalidation (清除快取) 的複雜度。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. CloudFront (CDN) 策略

*   **Cache-Control Headers 是王道**: 不要依賴 CloudFront console 的預設 TTL，應由 Origin (你的 Server/S3) 發送正確的 `Cache-Control: max-age=3600` header。這讓應用程式擁有控制權。
*   **Versioning over Invalidation (版本號勝於清除)**:
    *   *Best Practice*: 更新 CSS/JS 時，將檔名改為 `app.v2.js` 或 `app.js?v=hash`。這能確保使用者立即看到新版，且無需付費呼叫 CloudFront Invalidation API。
*   **Origin Shield**: 在多區域 (Multi-Region) 架構下，啟用 CloudFront Origin Shield 可以減少回源 (Origin Fetch) 的次數，避免多個 Edge locations 同時轟炸你的後端。

### 2. ElastiCache (Redis/Memcached) 存取模式

*   **Cache-Aside (Lazy Loading)**:
    *   這是最通用的模式。App 先讀 Cache，沒命中 (Miss) 則讀 DB 並回寫 Cache。
    *   *優點*: 只快取被請求的資料，節省記憶體。
    *   *缺點*: Cache Miss 時延遲較高 (3次網路來回)。
*   **Write-Through**:
    *   寫入 DB 時同步更新 Cache。
    *   *優點*: 資料一致性高，讀取永遠是 Hit。
    *   *缺點*: 寫入延遲增加，且會快取很多從未被讀取的資料 (浪費記憶體)。
*   **Russian Doll Caching (俄羅斯娃娃快取)**:
    *   針對複雜頁面，將快取分層：`Page Cache` -> `Fragment Cache` (如 Sidebar, Header) -> `Object Cache` (User Model)。這允許部分頁面更新而無需廢棄整個頁面快取。

### 3. 應對並發問題 (Concurrency Handling)

*   **Thundering Herd / Cache Stampede (驚群效應)**:
    *   當一個熱門 Key (Hot Key) 過期時，數千個請求同時發現 Miss 並同時打向 DB。
    *   *解法 A (Locking)*: 第一個發現 Miss 的 Process 取得分佈式鎖 (Redis Lock) 去更新 DB，其他 Process 等待或回傳舊值。
    *   *解法 B (Probabilistic Early Expiration)*: 在 TTL 到期前的一段隨機時間內，機率性地提早重算快取 (X-Fetch 演算法)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

*   **❌ The "Invalidation" Trap (過度依賴清除 API)**:
    *   頻繁呼叫 CloudFront Invalidation API 不僅昂貴（超過免費額度後計費），而且生效時間非即時。
    *   *修正*: 使用檔案版本號 (Versioning) 或較短的 TTL。
*   **❌ Caching Private Data on Public Edges (在邊緣快取私密資料)**:
    *   錯誤配置 CloudFront 導致 User A 的個人資料 (Profile) 被快取並顯示給 User B。
    *   *修正*: 對於私密內容，使用 `Cache-Control: private` 或 `no-store`，並正確設定 `Vary: Cookie` 或 `Authorization` header，或者根本不要在 CDN 快取動態 HTML。
*   **❌ No TTL / Infinite TTL (無期限快取)**:
    *   認為「我會手動清除」而設定無限期 TTL 是災難的開始。這會導致記憶體洩漏 (Memory Leak) 和永久性的資料不一致。
    *   *修正*: **永遠** 設定一個 TTL，即使是 30 天也好。
*   **❌ Using Keys/Scan in Production (在生產環境遍歷)**:
    *   在 Redis 中使用 `KEYS *` 指令會導致單執行緒的 Redis 阻塞 (Block)，造成全站停擺。
    *   *修正*: 使用 `SCAN` 指令，或在架構設計時避免需要遍歷 Key 的需求。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 該用哪種快取？
1.  **是靜態檔案 (圖片, CSS, JS)?** -> **CloudFront (S3 Origin)**
2.  **是公開的 API GET 回應?** -> **CloudFront (Custom Origin) + TTL**
3.  **是私有的 User Session?** -> **ElastiCache (Redis)**
4.  **是複雜的 DB Query 結果?** -> **ElastiCache (Redis) - Cache-Aside**
5.  **需要極致微秒級讀取 (Microsecond)?** -> **DAX (DynamoDB Accelerator) 或 Local In-Memory**

### Pre-launch Checklist (上線前檢查)

- [ ] **TTL Strategy**: 所有快取層級 (CDN, Redis) 是否都設定了合理的預設 TTL？
- [ ] **Eviction Policy**: Redis 的 `maxmemory-policy` 是否設定正確？（通常推薦 `volatile-lru` 或 `allkeys-lru`）。
- [ ] **Security**: ElastiCache 是否置於 Private Subnet？Security Group 是否只允許 App Server 存取？是否啟用 Encryption at Rest/In Transit？
- [ ] **Failover**: 若 Redis 掛掉，App 是否能降級 (Degrade) 直接讀取 DB 而不崩潰？
- [ ] **Key Naming**: Redis Key 是否有統一的前綴 (Namespace)，例如 `service:user:123`，以便管理？
- [ ] **Stampede Protection**: 針對極高流量的 Endpoint，是否實作了 Lock 或 Soft Expiry 機制？

---

## Real-world examples｜實戰案例

### Case 1: 解決 Cache Stampede (Redis 分佈式鎖模式)

場景：首頁顯示「熱門商品排行榜」，該計算非常消耗 DB 資源，TTL 設定為 5 分鐘。

```python
# Pseudo-code for Cache-Aside with Locking
def get_leaderboard():
    key = "home:leaderboard"
    data = redis.get(key)
    
    if data:
        return data

    # Cache Miss: 嘗試獲取鎖，避免 1000 個 request 同時打 DB
    # set_nx (Set if Not Exists) with 5 sec timeout
    lock_acquired = redis.set(f"{key}:lock", "1", nx=True, ex=5)
    
    if lock_acquired:
        try:
            # 我是搶到鎖的幸運兒，負責去 DB 撈資料
            data = db.query_heavy_leaderboard()
            redis.set(key, data, ex=300) # TTL 5 mins
            return data
        finally:
            redis.delete(f"{key}:lock")
    else:
        # 沒搶到鎖，代表別人正在算。
        # 策略 A: 等待 0.1 秒後重試 (Spin lock)
        # 策略 B: 回傳舊資料 (如果架構支援 Soft TTL)
        time.sleep(0.1)
        return get_leaderboard()
```

### Case 2: CloudFront 動靜分離與版本控制

場景：React/Vue SPA 應用程式部署。

*   **S3 Bucket**: 存放 `index.html`, `app.v123.js`, `style.v123.css`。
*   **CloudFront Behaviors**:
    *   `/api/*` -> **ALB (Application Load Balancer)**: `TTL=0` (或根據 API 性質設定短 TTL)，轉發 Authorization Header。
    *   `/*.js`, `/*.css`, `/images/*` -> **S3**: `TTL=1 year`。因為檔名包含 Hash/Version，內容永遠不會變，瀏覽器可永久快取。
    *   `/index.html` -> **S3**: `TTL=0` (Must-Revalidate)。確保使用者每次重新整理都能拿到最新的 `index.html` (其中包含指向最新 js/css 的連結)。

### Case 3: Redis 作為 Session Store 與 Rate Limiter

場景：防止惡意使用者刷 API。

*   **Pattern**: 使用 Redis 的 `INCR` (原子加法) 與 `EXPIRE`。
*   **Logic**:
    *   Key: `ratelimit:{user_ip}:{current_minute}`
    *   每次 Request -> `redis.incr(key)`
    *   如果是第一次 (值為 1) -> `redis.expire(key, 60)`
    *   如果值 > 100 -> 回傳 HTTP 429 Too Many Requests。
*   **為何用 Redis**: 速度極快，且 `INCR` 操作是 Atomic 的，不用擔心 Race Condition。