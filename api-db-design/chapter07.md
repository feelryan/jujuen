# 1. 前言與學習目標 (Introduction & Learning Objectives)

在分散式系統中，失敗不是「是否會發生」的問題，而是「何時發生」的問題。對於資深工程師而言，設計 API 時不僅要考慮功能實現，更必須假設網路會超時、下游服務會掛掉、以及客戶端會因為恐慌而發動 DDoS 般的重試攻擊。本章將探討如何透過設計模式來構建具備韌性（Resilience）的系統。

In distributed systems, failure is not a question of "if," but "when." For a Senior Engineer, designing an API requires more than just implementing functionality; you must assume that networks will time out, downstream services will fail, and clients will launch DDoS-like retry storms out of panic. This chapter explores how to build resilient systems using specific design patterns.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **實作強健的冪等性（Idempotency）機制**：理解如何在 `POST` 或非安全（Non-safe）操作中，利用 Idempotency Keys 防止重複扣款或重複建立資源。
    **Implement robust Idempotency mechanisms**: Understand how to use Idempotency Keys in `POST` or non-safe operations to prevent double charges or duplicate resource creation.
2.  **設計多層次的流量控制（Rate Limiting）**：區分單機與分散式限流策略，並能解釋 Token Bucket 與 Sliding Window 演算法的取捨。
    **Design multi-layered Rate Limiting**: Distinguish between local and distributed rate limiting strategies, and explain the trade-offs between Token Bucket and Sliding Window algorithms.
3.  **應用斷路器（Circuit Breaker）與艙壁（Bulkhead）模式**：防止單點故障演變成導致整個系統崩潰的級聯故障（Cascading Failures）。
    **Apply Circuit Breaker and Bulkhead patterns**: Prevent single points of failure from escalating into cascading failures that crash the entire system.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 冪等性 (Idempotency)
**定義**：數學上定義為 $f(f(x)) = f(x)$。在 API 設計中，意味著對同一資源進行一次或多次相同的請求，其**副作用（Side Effects）**與結果狀態必須完全一致。
**Definition**: Mathematically defined as $f(f(x)) = f(x)$. In API design, it means that making the same request to a resource once or multiple times must result in the exact same **side effects** and state.

**心智模型**：想像一個電梯按鈕。無論你按一次還是狂按十次「5 樓」，電梯都只會執行一次「去 5 樓」的指令，而不會嘗試去 50 樓。
**Mental Model**: Think of an elevator button. Whether you press "5th Floor" once or ten times, the elevator only executes the command "Go to 5th Floor" once; it doesn't try to go to the 50th floor.

### 2.2 限流 (Rate Limiting)
**定義**：控制網路流量進入或離開網路介面控制器的速率。
**Definition**: Controlling the rate of traffic sent or received by a network interface controller.

**心智模型**：夜店的保鏢（Bouncer）。不管外面排隊的人有多少，保鏢只允許每分鐘進去固定數量的人，或者當裡面滿了就拒絕進入，保護內部環境不被擠爆。
**Mental Model**: The Bouncer at a club. No matter how long the line outside is, the bouncer only allows a fixed number of people in per minute, or refuses entry when capacity is reached, protecting the internal environment from overcrowding.

### 2.3 斷路器 (Circuit Breaker)
**定義**：一種軟體設計模式，用於偵測故障並防止應用程式反覆嘗試執行註定會失敗的操作。
**Definition**: A software design pattern used to detect failures and prevent the application from repeatedly trying to execute an operation that's doomed to fail.

**心智模型**：家裡的保險絲。當電流過載（錯誤率過高）時，保險絲熔斷（Open State），切斷電路以保護電器。過一段時間後，你可以嘗試重置（Half-Open State），若正常則恢復供電（Closed State）。
**Mental Model**: The fuse in your home. When the current overloads (error rate spikes), the fuse blows (Open State), cutting the circuit to protect appliances. After a while, you can try to reset it (Half-Open State); if stable, power is restored (Closed State).

### 2.4 艙壁模式 (Bulkhead Pattern)
**定義**：將應用程式的元素隔離成池（Pools），以便如果其中一個失敗，其他的仍能繼續運作。
**Definition**: Isolating elements of an application into pools so that if one fails, the others will continue to function.

**心智模型**：船艙設計。如果船體破了一個洞，只有該艙室會進水，防水門關閉後，整艘船不會沉沒。在軟體中，這通常意味著為不同的服務依賴分配獨立的 Thread Pool 或 Connection Pool。
**Mental Model**: Ship compartments. If the hull is breached, only that specific compartment floods. Watertight doors close, ensuring the ship doesn't sink. In software, this usually means allocating separate Thread Pools or Connection Pools for different service dependencies.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境中，這些模式通常分佈在架構的不同層級：

In a production environment, these patterns are typically distributed across different layers of the architecture:

1.  **API Gateway / Load Balancer 層**：
    *   **Rate Limiting** 通常在此實作，以保護後端服務免受 DDoS 攻擊或單一租戶（Tenant）的資源濫用。
    *   **Rate Limiting** is usually implemented here to protect backend services from DDoS attacks or resource abuse by a single tenant.

2.  **Service Mesh / Sidecar (e.g., Envoy, Istio) 層**：
    *   **Circuit Breaker** 和 **Bulkhead** 越來越常下放到基礎設施層。這讓應用程式碼保持乾淨，不需要在每個微服務中重複實作重試與斷路邏輯。
    *   **Circuit Breaker** and **Bulkhead** are increasingly offloaded to the infrastructure layer. This keeps application code clean, avoiding the need to reimplement retry and breaking logic in every microservice.

3.  **Application Logic 層**：
    *   **Idempotency** 必須在業務邏輯層實作。因為只有業務邏輯知道什麼構成了「重複請求」（例如：利用 `Idempotency-Key` header 加上資料庫的唯一性約束）。
    *   **Idempotency** must be implemented in the business logic layer. Only the business logic knows what constitutes a "duplicate request" (e.g., using an `Idempotency-Key` header combined with database uniqueness constraints).

### 對系統屬性的影響 (Impact on System Attributes)

*   **可用性 (Availability)**：斷路器與限流雖然會拒絕部分請求，但能防止系統全面崩潰（Total Outage），從而提升整體的可用性。
    *   **Availability**: While Circuit Breakers and Rate Limiters reject some requests, they prevent total system outages, thereby increasing overall availability.
*   **一致性 (Consistency)**：冪等性是確保資料在網路重試（Network Retries）下保持一致的關鍵。沒有冪等性，分散式交易極易產生髒數據。
    *   **Consistency**: Idempotency is key to ensuring data consistency under network retries. Without it, distributed transactions are prone to dirty data.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 實作冪等性 (Implementing Idempotency)

**場景**：一個支付 API `POST /v1/charges`。如果客戶端因為 timeout 沒有收到回應，它會重試。如果沒有冪等性，使用者會被扣款兩次。

**Scenario**: A payment API `POST /v1/charges`. If the client doesn't receive a response due to a timeout, it retries. Without idempotency, the user gets charged twice.

### 步驟 1：定義 Idempotency Key
客戶端在 Header 中帶入一個唯一的 Key（通常是 UUID v4）。
The client includes a unique Key (usually UUID v4) in the Header.

```http
POST /v1/charges
Idempotency-Key: 8e9c5f20-1d8a-4c2e-8f1b-5d9a2c3e4f5a
...
```

### 步驟 2：伺服器端邏輯 (Server-Side Logic)
我們需要一個能夠處理並行請求（Concurrency）的儲存機制，通常使用 Redis 或支援 ACID 的資料庫。

We need a storage mechanism capable of handling concurrency, typically Redis or an ACID-compliant database.

**Python-like Pseudo Code:**

```python
def create_charge(request):
    key = request.headers.get('Idempotency-Key')
    
    # 1. Check if key exists in storage (e.g., Redis or a dedicated DB table)
    # 1. 檢查 Key 是否存在於儲存中
    cached_response = idempotency_store.get(key)
    if cached_response:
        return cached_response # Return the previous result immediately

    # 2. Acquire a lock to prevent race conditions (Double submit at the exact same time)
    # 2. 獲取鎖以防止競態條件（同一時間的重複提交）
    if not idempotency_store.lock(key):
        raise ConflictError("Request currently processing")

    try:
        # 3. Perform the actual business logic (e.g., call Stripe/PayPal)
        # 3. 執行實際業務邏輯
        charge_result = payment_gateway.charge(request.body)
        
        # 4. Save the result associated with the key
        # 4. 儲存結果並與 Key 關聯
        response = build_response(charge_result)
        idempotency_store.save(key, response, ttl=24*60*60) # Keep for 24 hours
        
        return response
    except Exception as e:
        # Handle failure, potentially allow retry by removing lock/key depending on error type
        raise e
    finally:
        idempotency_store.unlock(key)
```

**關鍵點 (Key Takeaways)**:
*   **原子性 (Atomicity)**：檢查 Key 和寫入 Key 的過程必須考慮併發。使用 Redis 的 `SETNX` 或資料庫的 Unique Constraint。
*   **鎖定期間 (Lock Duration)**：如果處理過程崩潰，鎖必須會過期（TTL），否則該 Key 永遠無法重試。

## 4.2 斷路器狀態機 (Circuit Breaker State Machine)

**場景**：你的 API 依賴一個外部庫存服務。該服務回應變慢，導致你的 Thread Pool 被耗盡。

**Scenario**: Your API depends on an external Inventory Service. That service becomes slow, causing your Thread Pool to be exhausted.

**邏輯流程 (Logic Flow)**:

1.  **Closed (正常)**：請求直接通過。統計失敗率。如果 `失敗次數 / 總請求數 > 閾值` (e.g., 50%)，切換到 Open。
    **Closed (Normal)**: Requests pass through. Failure rate is monitored. If `failures / total_requests > threshold` (e.g., 50%), switch to Open.
2.  **Open (熔斷)**：所有請求立即失敗（Fail Fast），回傳 503 Service Unavailable，不呼叫下游。啟動一個計時器（e.g., 30秒）。
    **Open (Tripped)**: All requests fail immediately (Fail Fast), returning 503 Service Unavailable without calling downstream. A timer starts (e.g., 30s).
3.  **Half-Open (測試)**：計時器到期後，允許**有限數量**的請求通過（e.g., 1 個）。
    *   如果成功：切換回 **Closed**。
    *   如果失敗：切換回 **Open** 並重置計時器。
    **Half-Open (Test)**: After the timer expires, allow a **limited number** of requests through (e.g., 1).
    *   If successful: Switch back to **Closed**.
    *   If failed: Switch back to **Open** and reset the timer.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 錯誤的冪等鍵範圍 (Incorrect Idempotency Key Scope)
*   **錯誤**：使用 Request Body 的 Hash 作為冪等鍵。
*   **Pitfall**: Using the hash of the Request Body as the idempotency key.
*   **為何不好**：如果使用者真的想發送兩筆一模一樣的訂單（例如買兩張相同的禮物卡），Hash 會一樣，導致第二筆被擋下。
*   **Why it's bad**: If a user genuinely intends to send two identical orders (e.g., buying two identical gift cards), the hash will be the same, blocking the second request.
*   **修正**：由客戶端生成隨機 UUID 作為 Key，代表「這是一次特定的操作意圖」。
*   **Fix**: Client generates a random UUID as the Key, representing "this specific intent of operation."

### 5.2 本地限流在分散式環境失效 (Local Rate Limiting in Distributed Environments)
*   **錯誤**：在每個 API Server 實體記憶體（In-Memory）中實作 Rate Limiter。
*   **Pitfall**: Implementing Rate Limiter in the in-memory of each API Server instance.
*   **為何不好**：當你有 10 台伺服器，限制每秒 100 次請求。實際上總容量變成了 1000 次。且負載平衡不均時，某些用戶會被誤殺，某些則能突破限制。
*   **Why it's bad**: If you have 10 servers and limit 100 req/sec. The actual total capacity becomes 1000. Also, with uneven load balancing, some users get blocked prematurely while others bypass the limit.
*   **修正**：使用 Redis 等集中式儲存來實作分散式 Rate Limiter（如 Redis + Lua script 實作 Token Bucket）。
*   **Fix**: Use centralized storage like Redis to implement a Distributed Rate Limiter (e.g., Redis + Lua script for Token Bucket).

### 5.3 斷路器缺乏 Fallback (Circuit Breaker without Fallback)
*   **錯誤**：斷路器打開後直接噴 500 錯誤給使用者。
*   **Pitfall**: Returning a raw 500 error to the user when the circuit is open.
*   **為何不好**：使用者體驗極差。
*   **Why it's bad**: Terrible user experience.
*   **修正**：實作優雅降級（Graceful Degradation）。例如，推薦系統掛了，改為回傳「熱門商品」快取列表，而不是錯誤頁面。
*   **Fix**: Implement Graceful Degradation. For example, if the recommendation system is down, return a cached list of "Trending Products" instead of an error page.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請設計一個分散式 Rate Limiter，你會如何處理 Race Condition？
**Design a Distributed Rate Limiter. How would you handle Race Conditions?**

*   **高分回答要點**：
    *   提到簡單的 "Get-Check-Increment" 在併發下會失敗。
    *   解決方案 1：Redis `INCR` (Atomic) + `EXPIRE` (適用於固定窗口)。
    *   解決方案 2：Redis Lua Script (將讀取與寫入打包成原子操作)，適用於 Token Bucket 或 Sliding Window Log。
    *   討論 Sliding Window Log (精確但耗記憶體) vs Fixed Window (有邊界突發流量問題) 的取捨。

### Q2: 在微服務架構中，如果下游服務響應緩慢，除了 Timeout，你還會做什麼保護措施？
**In a microservices architecture, if a downstream service is slow, what protection measures would you take besides Timeouts?**

*   **高分回答要點**：
    *   **Circuit Breaker**：快速失敗，避免佔用連線資源。
    *   **Bulkhead**：隔離 Thread Pool，確保 A 服務慢不會導致 B 服務也無法回應（例如 Tomcat 線程全卡在等待 A）。
    *   **Load Shedding**：當系統負載過高時，主動丟棄優先級低的請求。

### Q3: 冪等性實作中，如果「業務執行成功」但「儲存回應結果」失敗了（例如 Redis 掛了），該怎麼辦？
**In an idempotency implementation, what happens if the "business logic succeeds" but "saving the response" fails (e.g., Redis goes down)?**

*   **高分回答要點**：
    *   這是一個經典的雙寫一致性問題（Dual Write Problem）。
    *   如果無法使用分散式交易（2PC），通常傾向於「寧可重做也不要遺失」。
    *   但更好的解法是依賴資料庫的 Transaction：將業務數據寫入與冪等鍵記錄放在同一個 DB Transaction 中（Outbox Pattern 的變體）。
    *   或者，確保業務操作本身是可重入的（Re-entrant），即使沒存到 Cache，下次重試時檢查業務狀態（如訂單狀態為 PAID）也能回傳正確結果。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Idempotency Key** 是處理網路超時與重試的標準解法，必須由 Client 生成。
2.  **Rate Limiting** 保護系統不被流量淹沒；**Circuit Breaker** 保護系統不被下游故障拖垮。
3.  **Bulkhead** 透過資源隔離，防止局部故障擴散成全域災難。
4.  **Fail Fast**（快速失敗）優於讓請求無限期等待（Hanging）。
5.  所有的韌性設計都伴隨著複雜度（Redis 依賴、狀態管理），需權衡引入成本。

### 後續延伸 (Next Steps)
*   **實作練習**：使用 Redis Lua Script 寫一個 Sliding Window Rate Limiter。
*   **延伸閱讀**：研究 **Saga Pattern**，了解在分散式交易中如何處理補償交易（Compensating Transactions），這是冪等性的進階應用。
*   **下一章預告**：我們將探討 **Database Sharding & Partitioning**，解決單一資料庫的寫入瓶頸問題。