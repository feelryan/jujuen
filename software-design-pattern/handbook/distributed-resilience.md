# 分散式系統與韌性設計模式 / Distributed Systems and Resilience Patterns

## Mental model｜心智模型

在單體架構（Monolith）中，函式呼叫（Function Call）通常是決定性的：要嘛成功，要嘛因記憶體不足等嚴重錯誤而崩潰。但在分散式系統中，我們必須切換到 **「機率性思維」（Probabilistic Thinking）**。

### 1. 擁抱「部分失效」 (Embrace Partial Failures)
在微服務或雲端環境中，網路抖動、延遲飆升或某個 Pod 重啟是常態。
- **單體思維**：所有組件都在同一艘船上，船沉了大家一起死。
- **分散式思維**：系統是由一支艦隊組成的，其中一艘船引擎故障不該導致整支艦隊停擺。你必須假設 **「網路是不可靠的」** 且 **「下游服務隨時可能變慢或掛掉」**。

### 2. 最終一致性 vs. 強一致性 (Eventual vs. Strong Consistency)
不要試圖在分散式環境中強求 ACID 的強一致性（這會導致系統極度脆弱且難以擴展）。
- **心法**：將業務流程視為一系列狀態的轉換（State Transitions）。只要確保在合理的時間內，所有服務的狀態最終會同步即可（BASE 理論）。

### 3. 防禦性設計 (Defensive Design)
你的服務不只要處理正確的請求，還要能保護自己不被「隊友」拖垮。
- **比喻**：就像電路系統中的保險絲，當負載過高時，主動斷電是為了防止火災，而不是為了懲罰使用者。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 穩定性模式 (Stability Patterns)

這類模式的目標是防止連鎖故障（Cascading Failures）。

*   **Circuit Breaker（斷路器）**：
    *   **原理**：當下游服務錯誤率超過閾值（例如 50% 請求失敗），斷路器跳轉為 `Open` 狀態，直接拒絕請求並回傳 Fallback，不再浪費資源等待。一段時間後進入 `Half-Open` 試探恢復。
    *   **Best Practice**：不要只監控「錯誤」，還要監控「延遲」。慢回應往往比直接報錯更致命（因為會佔用 Thread Pool）。
*   **Retry with Exponential Backoff & Jitter（指數退避重試與抖動）**：
    *   **原理**：失敗後不要立即重試，也不要固定時間重試。應等待 `base * 2^n + random_jitter` 的時間。
    *   **Why Jitter?**：防止「驚群效應」（Thundering Herd），避免所有客戶端在同一毫秒發起重試，再次打垮剛恢復的服務。
*   **Bulkhead（艙壁模式）**：
    *   **原理**：隔離資源。例如，不要讓「圖片上傳」的 Thread Pool 耗盡影響到「文字搜尋」的功能。將資源池（Connection Pool, Thread Pool）分開。

### 2. 資料一致性模式 (Data Consistency Patterns)

*   **Saga Pattern（Saga 事務）**：
    *   **場景**：跨多個微服務的長事務（Long-running transaction）。
    *   **實作**：
        *   **Choreography（編排式）**：服務間透過 Event Bus 互相監聽事件（Event-Driven）。適合參與者較少、邏輯簡單的場景。
        *   **Orchestration（指揮式）**：由一個中央協調者（Orchestrator）告訴每個服務該做什麼。適合複雜流程。
    *   **關鍵**：每個步驟都必須定義 **補償交易（Compensating Transaction）**。如果步驟 C 失敗，必須執行步驟 B 和 A 的 Undo 邏輯。
*   **CQRS (Command Query Responsibility Segregation)**：
    *   **場景**：寫入邏輯複雜（需驗證），但讀取需求量大且格式多樣。
    *   **實作**：將「寫入模型（Command）」與「讀取模型（Query）」分離。寫入端更新 DB 後，發送事件非同步更新讀取端的 View DB（如 Elasticsearch 或 Redis）。

### 3. 基礎設施模式 (Infrastructure Patterns)

*   **Sidecar Pattern**：
    *   **概念**：將通訊、監控、斷路器等邏輯從應用程式代碼中剝離，放入一個與主程式共生的獨立 Container（如 Envoy Proxy）。
    *   **優勢**：業務工程師專注寫業務邏輯，不需要在每個微服務裡重複寫 Retry/Circuit Breaker 的程式碼（Polyglot 環境下特別有用）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分散式單體 (Distributed Monolith)
*   **症狀**：服務 A 必須等待服務 B 回應才能完成工作，服務 B 又依賴服務 C。呼叫鏈過深。
*   **後果**：延遲疊加，可用性是所有依賴服務可用性的乘積（例如 0.99 * 0.99 * 0.99...），系統極不穩定。
*   **解法**：改用非同步事件驅動（Event-Driven Architecture），或是引入資料快取以減少即時依賴。

### 2. 無限重試風暴 (Retry Storms)
*   **症狀**：設定了預設的 Retry 機制（例如 3 次），但呼叫鏈有 5 層。
*   **後果**：最底層服務的一個失敗，可能導致上游產生 $3^5 = 243$ 次請求，瞬間 DDoS 自己的系統。
*   **解法**：實作 **Retry Budget**（重試預算），限制每個客戶端在單位時間內的總重試比例；或者只在最上層進行重試。

### 3. 忽略冪等性 (Ignoring Idempotency)
*   **症狀**：在 Retry 或 Saga 補償機制中，沒有檢查該操作是否已經執行過。
*   **後果**：使用者被扣款兩次，或庫存被錯誤扣除。
*   **解法**：所有具備副作用（Side-effect）的 API 都必須支援冪等性（Idempotency Key）。

### 4. 濫用分散式鎖 (Overusing Distributed Locks)
*   **症狀**：為了強一致性，頻繁使用 Redis/Zookeeper 鎖定資源。
*   **後果**：效能瓶頸，且一旦鎖服務異常或持有鎖的服務崩潰（且未釋放），會導致死鎖。
*   **解法**：盡量使用樂觀鎖（Optimistic Locking, version number）或透過 Partitioning 讓同一資源只由單一執行緒處理。

---

## Checklists & workflows｜檢查清單與流程

在設計或 Code Review 分散式功能時，請使用此清單：

### Resilience Checklist (韌性檢核)
- [ ] **Timeouts**: 是否設定了明確的 Connect Timeout 與 Read Timeout？（預設值通常是無限，這很危險）
- [ ] **Fallback**: 當依賴服務失敗時，有無預設值、快取資料或友善的錯誤訊息？
- [ ] **Idempotency**: 重試這個寫入操作是否安全？有無 `idempotency-key` 機制？
- [ ] **Bulkhead**: 是否隔離了關鍵路徑與非關鍵路徑的資源？
- [ ] **Logging**: 是否有 `Trace ID` 貫穿整個呼叫鏈，以便追蹤跨服務錯誤？

### Saga / Transaction Decision Tree (事務決策樹)
1. **是否真的需要跨服務事務？**
   - No -> 單一服務內完成，或允許資料短暫不一致。
   - Yes -> 繼續。
2. **是否需要即時回應使用者結果？**
   - Yes -> 考慮 **Orchestration Saga**（由 API Gateway 或 Order Service 協調），並盡量減少同步等待步驟。
   - No -> 使用 **Choreography Saga**（事件驅動），讓服務自行監聽處理。
3. **是否有無法回滾（Undo）的步驟（如發送 Email、觸發外部銀行轉帳）？**
   - Yes -> 將該步驟放在 Saga 的 **最後一步** 執行。

---

## Real-world examples｜實戰案例

### 案例：電商下單流程 (E-commerce Checkout)

**情境**：使用者點擊「結帳」，系統需扣減庫存、扣款、建立訂單、通知物流。

#### 1. 錯誤的設計 (Sync Chain)
```text
User -> [Order Service] --(HTTP)--> [Inventory Service] --(HTTP)--> [Payment Service]
```
*   **問題**：若 Payment Service 回應慢，Inventory Service 的 DB 連線會被卡住（等待 HTTP 回應），Order Service 的 Thread 也會被卡住。Payment 掛掉，全站無法下單。

#### 2. 韌性設計 (Resilience & Saga)

**Step 1: 建立訂單 (Pending)**
User 呼叫 Order Service，建立狀態為 `PENDING` 的訂單。立即回傳 `Order ID` 給 User（前端顯示「處理中」）。

**Step 2: 扣減庫存 (Saga Step 1)**
Order Service 發送 `OrderCreated` 事件。
- **Inventory Service** 收到事件 -> 嘗試扣庫存。
- **Success**: 發送 `InventoryReserved` 事件。
- **Fail**: 發送 `InventoryFailed` 事件 -> Order Service 收到後將訂單改為 `FAILED` 並通知用戶。

**Step 3: 扣款 (Saga Step 2)**
Payment Service 監聽 `InventoryReserved` 事件。
- **Action**: 呼叫金流 API。
- **Resilience**: 這裡加上 **Circuit Breaker**。若金流閘道器掛了，暫停呼叫並將請求放入 Dead Letter Queue (DLQ) 稍後人工處理或自動重試，而不是讓系統崩潰。
- **Success**: 發送 `PaymentSucceeded`。
- **Fail**: 發送 `PaymentFailed` -> **補償交易啟動**：Inventory Service 監聽到此事件，執行「補回庫存」操作；Order Service 將訂單取消。

**Step 4: CQRS 讀取優化**
使用者想看「歷史訂單」時，不直接查詢 Order Service 的主 DB（可能正在忙著寫入），而是查詢同步後的 Read-Only DB (e.g., Elasticsearch)，即使有 1-2 秒延遲也是可接受的。

```python
# Pseudo-code: Circuit Breaker usage
def call_payment_gateway(order_id, amount):
    try:
        # 使用斷路器包裹外部呼叫
        result = circuit_breaker.execute(
            lambda: http_client.post("/charge", json={"id": order_id, "amt": amount})
        )
        return result
    except CircuitBreakerOpenException:
        # 斷路器已開，直接執行 Fallback
        log.warn("Payment gateway is down, queuing for later retry")
        queue_for_retry(order_id)
        return {"status": "PROCESSING_DELAYED"}
    except Exception as e:
        # 其他錯誤
        log.error(f"Payment failed: {e}")
        raise e
```