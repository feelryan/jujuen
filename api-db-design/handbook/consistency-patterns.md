# 交易處理與資料一致性模式 / Transaction Handling & Consistency Patterns

在現代系統設計中，資料一致性（Data Consistency）往往是效能與正確性之間的博弈。本章節不談教科書式的 ACID 定義，而是聚焦於：當你的資料跨越了多個資料表、多個資料庫甚至多個微服務時，如何確保它們最終是對齊的。

## Mental model｜心智模型

要掌握一致性模式，你需要轉變看待「交易（Transaction）」的方式：

### 1. 邊界思維：從「鎖定」到「狀態流轉」
- **Monolithic Mindset (ACID):** 依賴資料庫鎖（Locks）。像是在銀行櫃檯，櫃員處理完你的存款前，不接待下一位客人。這在單機資料庫非常有效，但在分散式系統中會導致效能瓶頸。
- **Distributed Mindset (BASE):** 依賴狀態機（State Machine）。像是在星巴克點餐，你付完錢拿到收據（Pending State），咖啡師非同步製作，最後叫號取餐（Final State）。
- **Key Insight:** 在分散式環境下，不要試圖強行鎖住所有資源。相反地，應將業務流程視為一系列**狀態的變更（State Transitions）**，並接受中間可能存在的「暫時不一致」狀態。

### 2. 一致性光譜 (The Consistency Spectrum)
不要將一致性視為「有」或「無」，而是一個光譜：
- **Strong Consistency (強一致性):** 讀取操作總是能讀到最新的寫入（如 RDBMS 的 Serializable Isolation）。
- **Causal Consistency (因果一致性):** 如果事件 A 導致了事件 B，系統保證所有節點都先看到 A 再看到 B。
- **Eventual Consistency (最終一致性):** 系統保證在沒有新的寫入下，最終所有節點資料會一致。這是大多數高併發 API 的選擇。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 本地交易優先 (Local Transaction First)
在拆分服務之前，先問自己：這些資料真的需要分開嗎？
- **Aggregate Pattern (DDD):** 盡量將需要強一致性的資料設計在同一個 Aggregate（聚合）中，並存放在同一個資料庫內。利用單機 DB 的 ACID 特性解決 80% 的一致性問題。

### 2. Transactional Outbox Pattern (交易式發件箱模式)
這是解決「寫入資料庫」與「發送訊息（如 Kafka/RabbitMQ）」原子性問題的黃金標準。
- **問題：** 寫入 DB 成功，但發送 Message Queue 失敗；或是先發 MQ 成功，但 DB Rollback。
- **解法：**
    1. 在同一個 DB Transaction 中，將業務資料寫入 `Orders` 表，並將事件寫入 `Outbox` 表。
    2. 依賴 DB 的 ACID 保證這兩者同時成功或失敗。
    3. 一個獨立的 Relay Process（或 Debezium 等 CDC 工具）讀取 `Outbox` 表並推送到 Message Queue。

### 3. Saga Pattern (長流程交易)
當業務跨越多個服務時（例如：訂單 -> 扣款 -> 扣庫存），使用 Saga 來管理。
- **Choreography (編排式):**
    - 服務間透過事件驅動（Event-driven）。Service A 完成後發出 Event，Service B 監聽並執行。
    - *適用場景：* 參與服務少（2-3 個）、流程簡單。
- **Orchestration (指揮式):**
    - 一個中央協調者（Orchestrator）告訴每個服務該做什麼。
    - *適用場景：* 流程複雜、參與者多、需要詳細的狀態監控。
- **補償交易 (Compensating Transaction):** Saga 的核心不是 Commit，而是 Rollback。你必須為每個步驟寫一個「反向操作」（例如：扣款的反向是退款）。

### 4. 樂觀鎖 (Optimistic Concurrency Control, OCC)
避免長時間鎖定資料庫列（Row）。
- **實作：** 在 Table 中增加 `version` 欄位。
- **邏輯：** `UPDATE table SET val = new_val, version = version + 1 WHERE id = 1 AND version = current_version`。
- 如果受影響行數為 0，表示資料已被其他人修改，此時拋出錯誤讓前端重試。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Two-Phase Commit (2PC/XA) over HTTP
- **陷阱：** 試圖在微服務之間使用分散式交易協議（如 XA）。
- **後果：** 效能極差（同步阻塞），且只要一個服務掛掉，整個交易就會卡住（單點故障擴大化）。
- **建議：** 除非是銀行核心轉帳等極端場景，否則**嚴禁**在 API 層級使用 2PC。

### 2. 忽略冪等性 (Ignoring Idempotency)
- **陷阱：** 認為網路請求只會發送一次。
- **後果：** 在重試機制（Retry）下，導致重複扣款或重複下單。
- **修正：** 所有的寫入 API（尤其是涉及金錢或庫存的）都必須支援冪等性。Client 端生成 `idempotency_key`，Server 端檢查該 Key 是否已處理過。

### 3. 缺乏狀態的可觀測性 (Blind State)
- **陷阱：** 在最終一致性模型中，UI 只有「成功」或「失敗」，沒有「處理中」。
- **後果：** 使用者困惑，重複點擊按鈕。
- **修正：** API 應回傳明確的狀態（如 `status: PENDING`），並提供查詢 API 或 WebSocket 推送最終結果。

### 4. 只有正向流程 (Happy Path Only)
- **陷阱：** 寫 Saga 時只寫了 `execute()` 邏輯，沒寫 `compensate()` 邏輯。
- **後果：** 一旦中間步驟失敗，系統留下髒資料（如：錢扣了但訂單沒成立），需要人工介入修復。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 選擇哪種一致性模式？

1. **資料是否在同一個 DB？**
   - [Yes] -> 使用 **Local ACID Transaction**。
   - [No] -> 進入下一步。

2. **是否容許短暫的不一致（數秒至數分鐘）？**
   - [No] (如：即時庫存搶購) -> 考慮 **Redis Lua Script** 或 **Distributed Lock** (慎用)，或重新設計聚合邊界。
   - [Yes] -> 進入下一步。

3. **流程是否涉及多個微服務寫入？**
   - [Yes] -> 使用 **Saga Pattern**。
     - 簡單流程 -> **Choreography** (Events)。
     - 複雜流程 -> **Orchestration** (State Machine)。

### Implementation Checklist (實作檢核表)

- [ ] **冪等性設計：** 接收端是否能處理重複收到的同一則訊息（Message/Event）而不產生副作用？
- [ ] **Outbox 模式：** 是否確保了「業務操作」與「發送事件」的原子性？
- [ ] **補償機制：** 對於 Saga 的每一步，是否都實作了對應的 `Compensate` 邏輯？
- [ ] **死信隊列 (DLQ)：** 當訊息處理失敗且重試耗盡時，是否有機制儲存這些訊息以供人工排查？
- [ ] **逾時處理：** 如果某個服務遲遲沒有回應，Saga 是否有 Timeout 機制來觸發回滾？
- [ ] **前端適配：** API 文件是否清楚說明了「非同步處理」的行為（例如回傳 `202 Accepted` 而非 `200 OK`）？

---

## Real-world examples｜實戰案例

### 案例：電商下單流程 (Order Fulfillment)

這是一個典型的分散式交易場景，涉及 `Order Service` (訂單)、`Payment Service` (支付)、`Inventory Service` (庫存)。

#### 1. 採用 Saga Orchestration (指揮模式)

我們定義一個 `OrderSagaOrchestrator` 來管理狀態。

**流程步驟 (Happy Path):**
1. **API Request:** 用戶結帳。
2. **Order Service:** 建立訂單，狀態設為 `PENDING`。啟動 Saga。
3. **Saga:** 發送 `ReserveCredit` 指令給 Payment Service。
4. **Payment Service:** 預扣款項成功。回覆 `CreditReserved`。
5. **Saga:** 發送 `ReserveStock` 指令給 Inventory Service。
6. **Inventory Service:** 扣減庫存成功。回覆 `StockReserved`。
7. **Saga:** 流程完成。發送 `ApproveOrder` 給 Order Service。
8. **Order Service:** 訂單狀態更新為 `CONFIRMED`。

#### 2. 異常處理與補償 (Failure Path)

假設在第 6 步，**Inventory Service 回覆 `OutOfStock` (庫存不足)**。

**補償流程:**
1. **Saga:** 收到庫存失敗，觸發 Rollback 流程。
2. **Saga:** 發送 `RefundCredit` (補償指令) 給 Payment Service。
3. **Payment Service:** 執行退款/取消預授權。回覆 `CreditRefunded`。
4. **Saga:** 發送 `RejectOrder` 給 Order Service。
5. **Order Service:** 訂單狀態更新為 `CANCELLED`，並記錄失敗原因。

#### 3. 虛擬碼示例 (Transactional Outbox)

在 Order Service 中，如何安全地發送事件：

```sql
-- ❌ Anti-pattern: 應用程式碼先 commit DB，再呼叫 Kafka SDK
-- 如果 Kafka 斷線，DB 已 commit，事件卻丟失了。

-- ✅ Best Practice: Outbox Pattern
BEGIN;

-- 1. 寫入業務資料
INSERT INTO orders (id, user_id, status, amount) 
VALUES ('ord_123', 'user_99', 'PENDING', 100);

-- 2. 寫入事件到同一個 DB 的 outbox table
INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) 
VALUES ('Order', 'ord_123', 'OrderCreated', '{"amount": 100, ...}');

COMMIT;

-- 3. 獨立的 Message Relay (如 Debezium 或 Polling Worker) 
-- 會讀取 outbox_events 並發送到 Kafka。
-- 即使 App Crash，只要 DB 寫入成功，事件最終一定會發送。
```