# 高可用性與叢集架構決策 / High Availability & Clustering Decisions

## Mental model｜心智模型

在深入 Redis 的高可用性（HA）與叢集（Clustering）之前，必須建立一個清晰的心智模型，區分 **「活著（Availability）」** 與 **「擴展（Scalability）」** 這兩個維度。

### 1. The "Scale vs. Uptime" Matrix
Redis 的架構演進並非單一線性，而是為了解決不同問題：
*   **Replication (Master-Replica)**：解決 **讀取擴展 (Read Scalability)** 與 **資料備援 (Data Redundancy)**。但 Master 死掉時需要人工介入。
*   **Sentinel**：解決 **自動故障轉移 (Automated Failover)**。它是 Replication 的「監控與自動化層」，不解決寫入擴展問題。
*   **Redis Cluster**：解決 **寫入擴展 (Write Scalability)** 與 **資料分片 (Sharding)**。它內建了 HA 機制，是分散式儲存的完整解決方案。

### 2. The "Async" Reality
Redis 預設的 Replication 是 **非同步 (Asynchronous)** 的。
*   **Mental Image**：Master 像是演講者，Replicas 是聽眾。演講者說完一句話（寫入成功）就繼續下一句，不會確認每個聽眾是否都聽進去了。
*   **Consequence**：在高可用切換（Failover）的瞬間，可能會遺失少量資料（Acknowledged writes that haven't propagated）。Redis 優先保證效能（Performance），而非強一致性（Strong Consistency）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Architecture Selection Strategy (架構選型策略)

*   **Pattern: Sentinel for Cache/Session (小數據、高可用)**
    *   如果資料量小於單機記憶體上限（例如 < 32GB），且主要瓶頸是「讀取」而非「寫入」。
    *   **做法**：使用 1 Master + 2 Replicas + 3 Sentinels。
    *   **Client**：需支援 Sentinel 協議（能詢問 Sentinel 誰是 Master）。

*   **Pattern: Native Cluster for Large Scale (大數據、高併發)**
    *   當資料量超過單機限制，或寫入量極大。
    *   **做法**：至少 3 Master + 3 Replicas（共 6 節點）。
    *   **Client**：需支援 Cluster Protocol（Smart Client），能快取 Slot Map 並處理 `MOVED`/`ASK` 重導向。

*   **Pattern: Proxy-based Sharding (中間件模式)**
    *   當 Client 端語言不支援複雜的 Cluster 協議，或需要統一管理連線數時。
    *   **做法**：Client -> Proxy (e.g., Twemproxy, Codis, Envoy) -> Redis Instances。
    *   **優點**：對 App 來說就像連線到單機 Redis，Proxy 處理分片邏輯。

### 2. Deployment Topology (部署拓撲)

*   **Odd Number of Sentinels (奇數哨兵)**
    *   Sentinel 依賴 Quorum（法定人數）來決定 Master 是否下線。務必部署奇數個（3 或 5），以避免腦裂（Split-brain）投票平手。
*   **Zone-Awareness (跨可用區部署)**
    *   不要將 Master 和它的 Replica 放在同一台實體機或同一個 Rack。
    *   最佳實務：Master 在 AZ-A，Replica 在 AZ-B，Sentinel 分散在 AZ-A, B, C。

### 3. Data Safety Configuration (資料安全配置)

雖然 Redis 是非同步複製，但可以透過設定提高安全性：
*   `min-replicas-to-write <number>`
*   `min-replicas-max-lag <seconds>`
*   **實務**：設定「至少要有一個 Replica 在 N 秒內有回應，Master 才接受寫入」。這是在 Availability 與 Consistency 之間的權衡（Trade-off）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Split Brain" Scenario (腦裂危機)
*   **情境**：網路分區導致原 Master 與新選出的 Master 同時存在，且 Client 仍寫入舊 Master。
*   **後果**：當網路恢復，舊 Master 降級為 Replica，期間寫入的資料將被新 Master 的資料覆蓋而**永久遺失**。
*   **避雷**：務必配置 `min-replicas-to-write`，讓舊 Master 在失去 Replica 連線時拒絕寫入。

### 2. Multi-Key Operations in Cluster (叢集下的多鍵操作)
*   **情境**：在 Redis Cluster 使用 `MGET`, `MSET`, `Lua Script` 或 `Transactions` 涉及多個 Key。
*   **錯誤**：`CROSSSLOT Keys in request don't hash to the same slot`。
*   **解法**：使用 **Hash Tags**（例如 `{user:100}.profile` 和 `{user:100}.settings`），強迫相關 Key 落入同一個 Slot。

### 3. Client Misconfiguration (客戶端配置錯誤)
*   **Sentinel 模式**：Client 連線字串寫死 Redis IP，而不是 Sentinel IP。導致 Failover 發生時，App 仍然嘗試連線已掛掉的舊 Master。
*   **Cluster 模式**：Client 沒有開啟 `follow_redirects` 或快取 Slot Map 更新不及時，導致大量的 `MOVED` 錯誤，拖慢效能。

### 4. Full Sync Storm (全量同步風暴)
*   **情境**：主節點重啟或網路瞬斷後，多個 Replicas 同時發起 Full Resynchronization (RDB snapshot transfer)。
*   **後果**：Master CPU/IO 飆高，甚至導致 Master 再次崩潰（OOM）。
*   **避雷**：錯開 Replica 的啟動時間；確保 `repl-backlog-size` 足夠大，增加 Partial Sync 成功的機率。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the Right Architecture
1.  **資料量是否大於單機 RAM (e.g., > 32GB)?**
    *   Yes -> **Redis Cluster**
    *   No -> 下一題
2.  **寫入 QPS 是否極高 (e.g., > 100k writes/sec)?**
    *   Yes -> **Redis Cluster**
    *   No -> 下一題
3.  **是否需要自動故障轉移 (High Availability)?**
    *   Yes -> **Sentinel**
    *   No -> **Standalone** (or Master-Replica for backup only)

### Pre-Production Checklist (上線前檢查)
- [ ] **Topology**: Sentinel 數量為奇數，且分佈在不同實體機/AZ。
- [ ] **Network**: 確保 Sentinel 之間、Sentinel 與 Redis 之間的 Port (預設 26379) 互通。
- [ ] **Client**: 應用程式使用的 Library 支援所選模式（Sentinel 或 Cluster），並已配置正確的 Timeout。
- [ ] **Persistence**: Master 的持久化策略（RDB/AOF）是否已根據 Failover 需求調整？（建議 Master 至少開 RDB，避免重啟後空資料同步給 Replica 導致資料全清）。
- [ ] **Failover Test**: 在 Staging 環境實際拔掉 Master 網路線，觀察：
    - [ ] Sentinel 是否偵測到 SDOWN/ODOWN？
    - [ ] 多少秒內完成切換？
    - [ ] App 是否自動重連到新 Master？

---

## Real-world examples｜實戰案例

### Case 1: The "Session Store" (Sentinel Pattern)
**場景**：一個電商網站的 User Session 儲存。
*   **需求**：高可用（不能讓使用者登出），資料量約 5GB，讀多寫少。
*   **架構**：
    *   3 台 Redis 伺服器：1 Master, 2 Replicas。
    *   3 個 Sentinel Process（可以與 Redis 同機，但建議獨立）。
*   **Client (Node.js/ioredis)**：
    ```javascript
    const redis = new Redis({
      sentinels: [
        { host: '10.0.0.1', port: 26379 },
        { host: '10.0.0.2', port: 26379 },
        { host: '10.0.0.3', port: 26379 }
      ],
      name: 'mymaster', // Sentinel 監控群組名稱
      role: 'master'    // 連線到 Master 進行讀寫
    });
    ```
*   **Lesson**：開發者不需要知道當下誰是 Master，Library 會自動詢問 Sentinel 並處理重連。

### Case 2: The "Global Rate Limiter" (Cluster Pattern with Hash Tags)
**場景**：一個 API Gateway 需要對每個 API Key 進行限流（Rate Limiting）。
*   **需求**：極高的寫入吞吐量（計數器），資料分散在多個節點。
*   **問題**：需要原子性地執行 `INCR` 和 `EXPIRE`，或者使用 Lua Script。
*   **挑戰**：在 Cluster 模式下，Lua Script 操作的 Key 必須在同一個 Slot。
*   **實作**：
    *   Key 設計：`rate_limit:{apiKey}:count`。
    *   利用 `{}` (Hash Tag) 確保分片邏輯只看 `apiKey`。
    *   即使後面的 `:count` 或其他後綴不同，只要 `{apiKey}` 相同，就會被 Hash 到同一個 Slot，允許 Lua Script 執行。

### Case 3: The "Legacy App Migration" (Proxy Pattern)
**場景**：舊的 PHP 應用程式使用極舊的 Redis Client，不支援 Cluster 協議，但資料量暴增需要分片。
*   **解法**：部署 **Twemproxy (Nutcracker)** 或 **Envoy** 作為 Sidecar/Gateway。
*   **架構**：
    *   PHP App -> Localhost:6379 (其實是 Envoy)。
    *   Envoy -> Redis Cluster (後端多個節點)。
*   **優點**：程式碼完全不用改，由 Proxy 負責計算 Hash 並路由到正確的後端 Redis 節點。