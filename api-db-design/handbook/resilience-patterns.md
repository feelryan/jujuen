# 韌性設計：冪等性、限流與重試 / Resilience Patterns: Idempotency, Rate Limiting & Retries

## Mental model｜心智模型

在分散式系統與微服務架構中，**「網路不可靠」是唯一不變的真理**。韌性設計（Resilience Design）的核心不在於「防止故障發生」，而在於「當故障發生時，系統如何優雅地應對並自我恢復」。

我們可以將這三個模式想像成一家熱門咖啡廳的運作機制：

1.  **Idempotency (冪等性)**：像是**訂單編號**。如果你因為店裡太吵而對店員喊了兩次「我要一杯拿鐵」，店員看到是同一個訂單編號，就知道這只是重複的請求，不會收你兩次錢，也不會做兩杯咖啡給你。
2.  **Rate Limiting (限流)**：像是**門口的人流管制**。咖啡機每分鐘只能做 5 杯咖啡，如果同時湧入 100 人，店員會請大家排隊或稍後再來，以防止機器過熱或店員崩潰。
3.  **Retries & Circuit Breaker (重試與斷路器)**：像是**機器故障處理**。
    *   **Retry**：按鈕沒反應，你可能會等幾秒再按一次（Exponential Backoff）。
    *   **Circuit Breaker**：如果機器冒煙了（持續錯誤），店長會直接掛上「維修中」的牌子（Open Circuit），暫停接單，直到修好為止，避免浪費大家時間並保護機器。

**The Core Philosophy:**
Design for failure. Assume the network will lag, the database will lock, and the client will double-click. Your API must handle these gracefully without corrupting data or cascading failures.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Idempotency Implementation (冪等性實作)

對於任何會改變系統狀態的操作（尤其是 `POST`、`PATCH`），必須實作冪等性，確保 `f(f(x)) = f(x)`。

*   **Idempotency Keys**: 要求 Client 在 Header 帶入唯一識別碼（如 UUID v4）。
    *   Header example: `Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000`
*   **Storage Strategy**: 使用 Redis 或資料庫的 Unique Constraint 來儲存 Key 與處理結果。
    *   *Key Expiry*: 設定合理的 TTL（例如 24-48 小時），不需要永久儲存。
*   **Atomic Check-and-Set**:
    1.  接收請求。
    2.  檢查 Key 是否存在？
        *   若存在且處理中 -> 回傳 `409 Conflict` 或 `202 Accepted`。
        *   若存在且已完成 -> 直接回傳上次的 cached response。
    3.  若不存在 -> 鎖定 Key -> 執行業務邏輯 -> 儲存結果 -> 釋放鎖定。

### 2. Rate Limiting Strategies (限流策略)

保護後端資源不被耗盡，通常在 API Gateway 或 Middleware 層實作。

*   **Algorithms**:
    *   **Token Bucket (權杖桶)**: 允許突發流量（Bursty traffic）。適合一般 API。
    *   **Leaky Bucket (漏桶)**: 強制平滑輸出速率。適合寫入資料庫或呼叫第三方嚴格 API 的場景。
    *   **Fixed Window vs. Sliding Window**: 務必使用 **Sliding Window (滑動視窗)**，避免在視窗邊界發生「雙倍流量」的臨界點問題。
*   **Granularity (粒度)**:
    *   Global (保護整個服務)。
    *   Per User/Tenant (公平性原則)。
    *   Per Endpoint (針對高成本 API 特別限制)。
*   **Response Headers**: 明確告知 Client 當前狀態。
    *   `X-RateLimit-Limit`: 總額度。
    *   `X-RateLimit-Remaining`: 剩餘額度。
    *   `X-RateLimit-Reset`: 重置時間（Unix timestamp）。
    *   `Retry-After`: 當回傳 `429 Too Many Requests` 時，告知需等待秒數。

### 3. Retries & Circuit Breakers (重試與斷路器)

*   **Exponential Backoff with Jitter (指數退避加抖動)**:
    *   不要立即重試，也不要固定時間重試。
    *   Formula: `wait_time = min(cap, base * 2^attempt) + random_jitter`
    *   **Jitter** 非常重要，它能防止所有 Client 在同一時間發起重試（Thundering Herd Problem）。
*   **Circuit Breaker States**:
    *   **Closed**: 正常運作。
    *   **Open**: 錯誤率超過閾值，直接拒絕請求（Fail fast），不呼叫後端。
    *   **Half-Open**: 過一段時間後，放行少量請求測試服務是否恢復。
*   **Idempotency Awareness**: 只有在確認操作是冪等的情況下（或 GET 請求），才由系統自動重試；否則應由 Client 決定。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Blind Retry" Storm (盲目重試風暴)
*   **Mistake**: Client 遇到任何錯誤（包含 `400 Bad Request` 或 `401 Unauthorized`）都進行重試。
*   **Consequence**: 永遠不會成功的請求塞滿了頻寬與 Server 資源。
*   **Fix**: 只針對 `503 Service Unavailable`、`429 Too Many Requests` 或網路超時進行重試。

### 2. Local Rate Limiting in Distributed Systems (分散式系統中的本地限流)
*   **Mistake**: 在多台 Server 的記憶體中分別計算 Rate Limit。
*   **Consequence**: 總流量限制不準確（N 台機器 = N 倍流量），且無法應對負載平衡不均的情況。
*   **Fix**: 使用 Redis 等集中式儲存來計數（Distributed Rate Limiting）。

### 3. Generating Idempotency Keys on Server (Server 端產生冪等 Key)
*   **Mistake**: Server 收到請求後自己產生 UUID 作為 Key。
*   **Consequence**: 如果 Request 在到達 Server 前就斷線，Client 重試時 Server 會視為新請求，導致重複執行。
*   **Fix**: Key 必須由 **Client** 產生並隨 Request 發送。

### 4. Cascading Failures without Circuit Breakers (缺乏斷路器的連鎖效應)
*   **Mistake**: 服務 A 呼叫服務 B，B 變慢，A 的 Thread pool 被卡住等待 B，導致 A 也變慢，最終拖垮整個系統。
*   **Consequence**: 單點故障擴散成全面癱瘓。
*   **Fix**: 設定 Timeouts 並實作 Circuit Breaker。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Handling a Request

1.  **Rate Limit Check**: 是否超過配額？
    *   Yes -> Return `429` + `Retry-After`.
2.  **Idempotency Check** (For unsafe methods): Header 是否有 `Idempotency-Key`？
    *   No -> Return `400 Bad Request`.
    *   Yes -> Check storage. 已處理過？ -> Return cached response.
3.  **Processing**: 執行業務邏輯。
    *   External Call Fails? -> Check Circuit Breaker -> Retry logic (if transient).
4.  **Completion**: 儲存結果與 Idempotency Key -> Return `200/201`.

### Implementation Checklist

- [ ] **Idempotency**:
    - [ ] 所有非唯讀 API (POST/PATCH/PUT) 是否支援 `Idempotency-Key`？
    - [ ] Key 的儲存是否有 TTL（避免無限增長）？
    - [ ] 是否處理了並發請求（Concurrent Requests）的 Race Condition（例如使用 Redis `SETNX`）？
- [ ] **Rate Limiting**:
    - [ ] 是否針對不同層級（IP, User, API Key）設定了限制？
    - [ ] 是否正確回傳了 `Retry-After` Header？
    - [ ] 是否使用了 Sliding Window 算法？
- [ ] **Resilience**:
    - [ ] Retry 邏輯是否包含了 **Jitter**（隨機抖動）？
    - [ ] 是否設定了明確的 Timeout（連線超時與讀取超時）？
    - [ ] 針對關鍵依賴服務（Database, 3rd Party API）是否配置了 Circuit Breaker？

---

## Real-world examples｜實戰案例

### Example 1: Payment API with Idempotency (Redis Lua Script)

在支付場景中，防止重複扣款是最高優先級。使用 Lua Script 確保「檢查」與「鎖定」是原子操作（Atomic）。

```lua
-- Input: key, value (status), expiry_seconds
local key = KEYS[1]
local value = ARGV[1]
local ttl = ARGV[2]

-- Check if key exists
if redis.call("EXISTS", key) == 1 then
    -- Return existing result
    return redis.call("GET", key)
else
    -- Set key with "PROCESSING" status and TTL
    redis.call("SET", key, value, "EX", ttl)
    return nil -- Signal to proceed with payment
end
```

**Flow:**
1. Client sends `POST /charge` with `Idempotency-Key: uuid-123`.
2. API runs Lua script.
3. If returns `nil`: Process payment -> Update Redis key with final JSON response.
4. If returns data: Return that data immediately (Client receives same response as the first time).

### Example 2: Exponential Backoff with Jitter (Python Pseudo-code)

這是一個在呼叫不穩定下游服務時的重試邏輯。

```python
import time
import random

def call_unreliable_service_with_retry(max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return make_network_request()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise e # Give up
            
            # Exponential Backoff: 1, 2, 4...
            sleep_time = base_delay * (2 ** attempt)
            
            # Add Jitter: +/- 10% random variation
            # 這能避免所有失敗的請求在同一毫秒同時重試
            jitter = sleep_time * 0.1 * random.uniform(-1, 1)
            total_sleep = sleep_time + jitter
            
            print(f"Retry {attempt + 1} in {total_sleep:.2f}s...")
            time.sleep(total_sleep)
```

### Example 3: Circuit Breaker Configuration (Resilience4j style)

配置斷路器以保護資料庫不被慢查詢拖垮。

*   **FailureRateThreshold**: 50% (如果 50% 的請求失敗，打開斷路器)
*   **WaitDurationInOpenState**: 10s (斷路器打開後，等待 10 秒才進入 Half-Open 狀態嘗試恢復)
*   **PermittedNumberOfCallsInHalfOpenState**: 3 (在 Half-Open 狀態下，只允許 3 個請求通過測試)
*   **SlidingWindowSize**: 10 (只看最近 10 個請求來計算失敗率)

**Scenario**: 資料庫 CPU 飆高，查詢超時。Circuit Breaker 偵測到錯誤率上升 -> 狀態轉為 **OPEN** -> API 直接回傳 `503 Service Unavailable` (不再送請求給 DB) -> DB 獲得喘息機會恢復 -> 10秒後 -> **HALF-OPEN** -> 測試請求成功 -> **CLOSED** -> 恢復正常服務。