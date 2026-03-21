# 系統韌性與容錯設計 / Resilience, Fault Tolerance & Reliability

## Mental model｜心智模型

在微服務架構中，**「故障不是例外，而是常態」(Failure is not an exception, it's the norm)**。

傳統單體架構 (Monolith) 往往追求「如何讓系統不壞掉」；而在微服務中，你的心智模型必須轉變為 **「如何管理故障的擴散範圍 (Blast Radius)」** 與 **「如何優雅地降級 (Graceful Degradation)」**。

想像你的系統是一艘由多個水密隔艙 (Watertight Compartments) 組成的船：
1.  **Isolation (隔離)**：如果一個艙進水（某個服務掛掉），水不應該流進其他艙。
2.  **Fail Fast (快速失敗)**：如果引擎壞了，儀表板應該立刻亮紅燈，而不是讓船長轉動舵輪卻毫無反應（無限等待）。
3.  **Recovery (恢復)**：當破洞修補好後，系統應該能自動偵測並恢復運作，而不是需要人工重啟。

**Core Philosophy:**
> Don't design for "Success". Design for "Partial Failure".
> 不要只為「成功路徑」設計，要為「部分失敗」設計。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Timeouts: The First Line of Defense
**超時機制：第一道防線**

永遠不要依賴預設的 Timeout 設定（通常是無限或過長）。
-   **Connection Timeout**: 建立 TCP 連線的時間。應設得非常短（例如 1-2 秒），因為連不上通常意味著網路不通或對方掛了。
-   **Read/Socket Timeout**: 等待回應的時間。應根據該服務的 P99 延遲來設定。
-   **Rule of Thumb**: 上游服務的 Timeout 必須大於下游服務的 Timeout 總和，否則會導致過早斷開與資源浪費。

### 2. Retries with Exponential Backoff & Jitter
**重試機制：指數退避與隨機抖動**

盲目的重試會導致 **驚群效應 (Thundering Herd Problem)**，徹底打垮已經不穩定的服務。
-   **Idempotency (冪等性)**: 重試的前提是該操作必須是冪等的（例如讀取操作，或帶有 unique ID 的寫入）。
-   **Exponential Backoff**: 等待時間指數增長 (e.g., 100ms, 200ms, 400ms)。
-   **Jitter (隨機抖動)**: 在等待時間中加入隨機值，避免所有客戶端在同一毫秒發起重試。
    -   *Formula*: `wait_time = min(cap, base * 2^attempt) + random_between(0, base)`

### 3. Circuit Breaker
**斷路器：防止級聯故障**

當下游服務持續失敗時，主動切斷請求，直接回傳錯誤或 Fallback，給下游喘息修復的時間。
-   **Closed State**: 正常運作，請求通過。
-   **Open State**: 錯誤率超過閾值 (Threshold)，請求直接被攔截 (Fail Fast)。
-   **Half-Open State**: 經過一段時間後，允許少量請求通過以測試下游是否恢復。若成功則切回 Closed，失敗則回到 Open。

### 4. Bulkhead Pattern
**艙壁模式：資源隔離**

避免一個壞掉的服務耗盡所有系統資源（如 Thread Pool）。
-   **Thread Pool Isolation**: 為呼叫 Service A 和 Service B 分配不同的 Thread Pools。如果 Service A 卡死，只會耗盡它專屬的 Pool，Service B 的呼叫不受影響。
-   **Semaphore Isolation**: 限制對某個依賴服務的併發請求數量 (Concurrency Limit)。

### 5. Fallback Strategies
**降級策略：當失敗發生時該給什麼？**

當 Circuit Breaker 打開或 Timeout 發生時，不要只丟出 `500 Internal Server Error`。
-   **Stubbed Data**: 回傳預設值（例如：推薦系統掛了，回傳「熱門商品」列表）。
-   **Cached Data**: 回傳稍舊的快取資料。
-   **Silent Failure**: 在非關鍵功能（如 Log 收集、非同步通知）中，可以捕獲錯誤並忽略，不影響主流程。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Retry Storm" (重試風暴)
**Description**: 當服務 A 呼叫 B，B 呼叫 C。如果 C 變慢，B 重試 3 次，A 也重試 3 次。
**Result**: C 收到 3 x 3 = 9 次請求。層級越深，請求量呈幾何級數爆炸，直接 DDoS 自己的系統。
**Avoidance**: 限制重試層級，或僅在最上層進行重試；使用 Circuit Breaker 提早阻斷。

### 2. Infinite or Default Timeouts
**Description**: 使用 HTTP Client 時未顯式設定 Timeout。
**Result**: 當下游服務 hang 住時，上游的 Thread 會一直處於 `WAITING` 狀態，最終耗盡 Thread Pool 導致整個服務崩潰 (Cascading Failure)。

### 3. Catch-All Fallbacks without Monitoring
**Description**: 實作了完美的 Fallback（例如回傳空列表），但忘記記錄錯誤 Log 或發送 Alert。
**Result**: 系統看起來運作正常，但實際上某個微服務已經掛了三天，業務資料全是空的或舊的，直到用戶投訴才發現。

### 4. Treating Circuit Breaker as Error Handling
**Description**: 依賴斷路器來處理業務邏輯錯誤（如 400 Bad Request）。
**Result**: 斷路器應該只針對「系統可用性」問題（如 503, Timeout, Network Error）。業務錯誤不應觸發斷路器開啟。

---

## Checklists & workflows｜檢查清單與流程

在將微服務推上 Production 之前，請依據此清單進行 Code Review 與配置檢查：

### Configuration Checklist (配置檢核)
- [ ] **Timeouts**: 所有外部呼叫（DB, API, Cache）是否都設定了明確的 Timeout？
    - [ ] Connect Timeout < 2s?
    - [ ] Read Timeout 是否依據 P99 延遲設定？
- [ ] **Retries**:
    - [ ] 是否僅針對「暫時性錯誤 (Transient Errors)」(e.g., Network glitch, 503) 進行重試？
    - [ ] 是否實作了 Exponential Backoff + Jitter？
    - [ ] 最大重試次數 (Max Attempts) 是否限制在合理範圍（通常 < 3 次）？
- [ ] **Circuit Breaker**:
    - [ ] 是否針對高風險的依賴服務配置了斷路器？
    - [ ] 閾值 (Threshold) 設定是否合理（避免過於敏感導致頻繁誤殺）？
- [ ] **Bulkhead**:
    - [ ] 關鍵路徑是否與非關鍵路徑使用了不同的 Thread Pool 或連接池？

### Decision Workflow: "Should I Retry?" (決策流程)
1.  **Is the error transient?** (Network timeout, 503) -> **Yes**. (If 400/401/403 -> **No**, fail immediately).
2.  **Is the operation idempotent?** (GET request, PUT with ID) -> **Yes**. (If POST create without ID -> **No**, risk of duplicates).
3.  **Am I deep in the call chain?** -> **No**. (If I am a low-level service, let the upstream handle the retry decision).
4.  **Decision**: Apply Retry with Backoff.

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Checkout Service
**情境**：結帳服務 (Checkout Service) 需要呼叫「庫存服務 (Inventory Service)」扣減庫存，以及「積分服務 (Loyalty Service)」計算點數。

#### Problem
大促銷期間，**積分服務** 因為資料庫鎖死而回應極慢（超過 10 秒）。這導致 **結帳服務** 的 Thread Pool 全部被卡在等待積分服務的回應，最終導致使用者無法結帳（即使庫存服務是正常的）。

#### Solution Implementation (Resilience Strategy)

我們對「積分服務」的呼叫實施以下策略：

1.  **Timeout**: 強制設定 1 秒超時。如果積分算不出來，不要讓用戶等。
2.  **Circuit Breaker**: 如果 10 秒內錯誤率 > 50%，斷路器開啟，直接跳過積分計算。
3.  **Fallback**: 當 Timeout 或 Circuit Breaker 開啟時，執行 Fallback 方法 —— 「暫時記錄交易 ID，標記為『待計算積分』，讓結帳流程繼續完成」。
4.  **Bulkhead**: 使用獨立的 Thread Pool 呼叫積分服務。

#### Pseudo-code (Conceptual)

```java
// 使用 Resilience4j 風格的註解

@CircuitBreaker(name = "loyaltyService", fallbackMethod = "fallbackCalculatePoints")
@Bulkhead(name = "loyaltyPool", type = Type.THREADPOOL)
@TimeLimiter(name = "loyaltyTimeout") // Configured to 1s
public PointsResponse calculatePoints(String userId, Order order) {
    // 呼叫遠端積分服務
    return loyaltyClient.calculate(userId, order.getTotal());
}

// Fallback 方法：優雅降級
public PointsResponse fallbackCalculatePoints(String userId, Order order, Throwable t) {
    log.error("Loyalty service unavailable, scheduling async calculation for user: " + userId, t);
    
    // 發送事件到 Message Queue，稍後非同步補算積分
    eventBus.publish(new AsyncPointCalculationEvent(userId, order));
    
    // 回傳 0 分或預設值，確保主流程(結帳)不中斷
    return PointsResponse.pending(); 
}
```

#### Outcome
當積分服務掛掉時，用戶仍然可以順利結帳（體驗無感），只是積分會晚幾分鐘入帳。系統整體可用性 (Availability) 得到保障，未發生級聯故障。