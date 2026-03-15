# 彈性設計：斷路器、隔艙與重試機制 / Resiliency Design: Circuit Breakers, Bulkheads & Retries

## Mental Model｜心智模型

在雲原生架構中，我們必須接受一個殘酷的事實：**故障不是「如果」會發生，而是「何時」會發生 (Failures are not a matter of *if*, but *when*)。**

傳統單體應用通常假設網路是可靠的，但在分散式系統中，任何一個微服務、資料庫或第三方 API 的延遲與中斷，都可能導致整個系統癱瘓。

對於彈性設計，你應該建立以下心智模型：

1.  **防禦性駕駛 (Defensive Driving)**：不要假設其他服務會準時回應。你的服務必須在依賴方掛掉時，依然能「優雅地」存活或降級，而不是跟著一起崩潰。
2.  **擁抱分區 (Embrace Partitioning)**：想像你的系統是一艘船。如果船身破了一個洞（某個服務故障），**隔艙 (Bulkhead)** 設計能確保只有該艙進水，而不是整艘船沉沒。
3.  **快速失敗 (Fail Fast)**：如果下游已經掛了，不要讓請求在那裡空等 (Hang)，這會耗盡你的 Thread Pool。**斷路器 (Circuit Breaker)** 的作用就是直接拒絕請求，保護自己也保護下游。
4.  **平滑過渡 (Graceful Degradation)**：當無法提供 100% 功能時，提供 80% 的功能（例如：顯示快取資料、隱藏推薦欄位）比直接噴 500 Error 更好。

---

## Patterns & Best Practices｜常見模式與最佳實務

### 1. 智慧重試 (Smart Retries)
重試是雙面刃。盲目的重試會造成「驚群效應」(Thundering Herd)，導致原本就在掙扎的服務徹底被流量打死。

*   **冪等性 (Idempotency)**：**絕對不要**重試非冪等的操作（如：扣款請求）。只有在確定操作安全（如：讀取資料）或設計了冪等機制時才重試。
*   **指數退避與抖動 (Exponential Backoff & Jitter)**：
    *   不要固定每 1 秒重試一次。
    *   應使用 `WaitTime = Base * 2^n + Random_Jitter`。
    *   **Jitter (抖動)** 非常關鍵，它能錯開大量請求同時重試的時間點，避免再次衝擊伺服器。

### 2. 斷路器 (Circuit Breaker)
當錯誤率超過閾值時，暫時切斷對下游的呼叫。

*   **三種狀態**：
    *   **Closed (閉合)**：正常運作，請求通過。
    *   **Open (斷開)**：錯誤率超標，直接回傳錯誤或執行 Fallback，不發送請求給下游。
    *   **Half-Open (半開)**：經過一段時間 (Reset Timeout)，允許少量請求通過以測試下游是否恢復。若成功則切回 Closed，失敗則回到 Open。
*   **實作位置**：
    *   **應用層 (Application Library)**: 如 Java 的 Resilience4j, .NET 的 Polly。優點是控制粒度細，可結合業務邏輯。
    *   **基礎設施層 (Service Mesh)**: 如 Istio, Linkerd。優點是語言無關，統一管理，但無法處理複雜的業務降級邏輯。

### 3. 隔艙模式 (Bulkhead Pattern)
隔離資源，避免單點故障擴散。

*   **執行緒池隔離 (Thread Pool Isolation)**：為不同的下游依賴分配獨立的 Thread Pool。例如，不要讓「產生報表」的慢速請求佔滿了「使用者登入」的執行緒。
*   **信號量隔離 (Semaphore Isolation)**：限制併發請求數量 (Concurrency Limit)。一旦達到上限，立即拒絕多餘請求，無需排隊。

### 4. 逾時控制 (Timeouts)
這是最基礎的防線。

*   **永遠設定 Timeout**：沒有無限等待這回事。
*   **層級遞減**：上游的 Timeout 應該大於下游的 Timeout。例如：Gateway (3s) -> Service A (2s) -> Service B (1s)。否則下游還在處理，上游已經放棄了，浪費資源。

---

## Anti-patterns & Pitfalls｜反模式與踩雷點

### 1. 重試風暴 (Retry Storms)
*   **現象**：Service A 呼叫 Service B 失敗並重試，Service B 呼叫 Service C 失敗也重試。當層級很深時，一個底層故障會導致上層產生指數級的流量放大。
*   **解法**：限制重試次數（通常 1-3 次），並實施 **Circuit Breaker** 中斷重試鏈。

### 2. 靜默失敗 (Silent Failures)
*   **現象**：在 Fallback 方法中捕捉了 Exception，回傳了空值 (Null) 或預設值，但**沒有記錄 Log 或發送監控指標**。
*   **後果**：系統看起來在運作，但資料可能是錯的，且維運人員完全不知道發生了故障，直到客戶投訴。
*   **解法**：Fallback 必須伴隨可觀測性 (Observability) 的 Alert 或 Log。

### 3. 配置混亂 (Configuration Chaos)
*   **現象**：Timeout 設定比 Circuit Breaker 的觸發時間還長；或者 Retry 的間隔總和超過了上游的 Timeout。
*   **後果**：斷路器永遠不會打開，或者上游總是先 Timeout，導致重試無效。

### 4. 分散式單體 (Distributed Monolith)
*   **現象**：過度依賴同步 (Synchronous) HTTP 呼叫。Service A 必須等 B，B 必須等 C。
*   **後果**：再好的斷路器也救不了緊密耦合的延遲。
*   **解法**：在適當的時候改用 **非同步訊息佇列 (Async Messaging/Event-Driven)**。

---

## Checklists & Workflows｜檢查清單與流程

在將服務部署到 Production 之前，請使用此清單進行審查：

### Configuration Review (配置審查)
- [ ] **Timeouts**: 所有對外呼叫（DB, API, Cache）是否都設定了明確的 Timeout？
- [ ] **Retry Policy**: 重試是否僅限於「暫時性錯誤」(Network glitch, 503) 而非「永久性錯誤」(400, 401, 404)？
- [ ] **Backoff**: 重試是否啟用了 Exponential Backoff 與 Jitter？
- [ ] **Circuit Breaker**: 是否針對高風險依賴配置了斷路器？閾值是否合理（例如：50% 失敗率持續 10 秒）？
- [ ] **Bulkhead**: 是否為關鍵路徑（如登入、支付）保留了獨立的資源池？

### Fallback Strategy (降級策略)
- [ ] **Fallback Logic**: 當斷路器打開時，系統行為是什麼？
    - [ ] 回傳快取資料 (Stale data)？
    - [ ] 回傳預設值？
    - [ ] 僅關閉非核心功能（如推薦商品）？
    - [ ] 回傳友善的錯誤訊息？
- [ ] **Observability**: Fallback 觸發時，是否有對應的 Metric (Counter) 增加？

### Decision Tree: Which strategy to use?
1.  **是網路抖動嗎？** -> 使用 **Retry** (帶 Backoff)。
2.  **服務徹底掛了嗎？** -> 使用 **Circuit Breaker** (快速失敗)。
3.  **服務變慢了嗎？** -> 使用 **Timeout** (防止卡死)。
4.  **某個依賴正在拖垮整個系統？** -> 使用 **Bulkhead** (資源隔離)。

---

## Real-world Examples｜實戰案例

### 案例：電商產品詳情頁 (Product Detail Page)

**場景**：
`Product Service` 需要呼叫 `Inventory Service` (庫存) 和 `Recommendation Service` (推薦)。

**問題**：
大促銷期間，`Recommendation Service` 因為負載過高回應極慢（超過 5 秒），導致 `Product Service` 的執行緒全部卡在等待推薦結果，最終導致使用者連產品基本資訊都看不到。

**解決方案實作 (Pseudo-code / Config Concept)**：

1.  **套用 Bulkhead 與 Timeout**：
    將呼叫推薦服務的連線限制在獨立的池中，並設定嚴格的 Timeout。

    ```yaml
    # Resilience Configuration Concept
    dependency: recommendation-service
      timeout: 500ms  # 超過 500ms 直接放棄，不值得等待
      bulkhead:
        max_concurrent_calls: 20 # 最多只允許 20 個併發請求，避免耗盡資源
    ```

2.  **套用 Circuit Breaker 與 Fallback**：
    如果推薦服務持續失敗，直接切斷。

    ```java
    // Java pseudo-code using Resilience4j style annotations
    @CircuitBreaker(name = "recommendation", fallbackMethod = "fallbackRecommendations")
    public List<Product> getRecommendations(String userId) {
        return remoteRecommendationClient.fetch(userId);
    }

    // Fallback 方法：優雅降級
    public List<Product> fallbackRecommendations(String userId, Throwable t) {
        log.warn("Recommendation service unavailable, returning empty list. Error: {}", t.getMessage());
        // 策略 A: 回傳空清單 (前端會隱藏該區塊)
        return Collections.emptyList(); 
        // 策略 B: 回傳熱門商品快取 (Generic fallback)
        // return cache.get("top_selling_products");
    }
    ```

**結果**：
當 `Recommendation Service` 掛掉時，使用者依然能秒開產品頁面（看到價格、庫存、描述），只是下方少了「猜你喜歡」區塊。系統整體可用性 (Availability) 得到保障，營收未受嚴重影響。