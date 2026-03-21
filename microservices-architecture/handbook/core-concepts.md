# 分散式系統核心思維與挑戰 / Core Concepts & Distributed System Challenges

## Mental model｜心智模型

在進入微服務架構之前，最關鍵的不是技術選型，而是思維模式的轉變。你必須從「單一記憶體空間的確定性」轉向「網路通訊的不確定性」。

### 1. 函數呼叫 vs. 網路呼叫 (In-process Call vs. Remote Call)
在單體 (Monolith) 中，模組 A 呼叫模組 B 是一個記憶體內的函數跳轉，成功率接近 100%，延遲極低。在微服務中，這變成了網路請求。
*   **The Fallacy (謬誤):** 網路是可靠的、延遲是零、頻寬是無限的。
*   **The Reality (現實):** 網路會中斷、封包會丟失、服務會暫時不可用。
*   **Mindset:** 每一次跨服務呼叫都必須假設它**可能會失敗**，並且必須設計好「失敗後該怎麼辦」。

### 2. CAP 定理的實戰解讀 (CAP in Practice)
不要把 CAP 當作「三選二」的理論題。在分散式系統中，**P (Partition Tolerance, 分區容錯性)** 是不可妥協的物理現實（網路一定會分區）。你真正的選擇是在發生網路分區（故障）時：
*   **CP (Consistency priority):** 為了保證資料一致，暫停服務（報錯或等待）。適用於銀行轉帳、庫存扣減。
*   **AP (Availability priority):** 為了保證服務可用，回傳舊資料或暫存寫入，稍後再同步。適用於社群動態、商品評論。

### 3. 複雜度守恆定律 (Conservation of Complexity)
微服務不會消除複雜度，只是將複雜度從「程式碼邏輯 (Codebase)」轉移到了「基礎設施與互動 (Infrastructure & Interaction)」。
*   **Monolith:** 複雜在於 Class 之間的耦合與龐大的 Context。
*   **Microservices:** 複雜在於服務發現、分散式追蹤、網路延遲與資料一致性。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Design for Failure (為失敗而設計)
既然網路不可靠，系統必須具備自我修復或降級的能力。
*   **Graceful Degradation (優雅降級):** 當「推薦服務」掛掉時，電商首頁不該顯示 500 Error，而是顯示「熱門商品」或「預設清單」。
*   **Timeouts & Retries (超時與重試):** 永遠不要無限期等待回應。設定合理的 Timeout，並在安全的情況下（如讀取操作）進行 Retry。

### 2. Idempotency (冪等性設計)
由於網路重試 (Retry) 機制的存在，服務端必須保證「同樣的請求執行一次與執行多次的結果是一樣的」。
*   **Implementation:** 使用 Unique Request ID (如 UUID) 來追蹤請求，若資料庫中已存在該 ID 的處理紀錄，則直接回傳之前的結果，不重複執行業務邏輯。

### 3. Eventual Consistency (最終一致性)
放棄 ACID 的強一致性執念，改擁抱 BASE (Basically Available, Soft state, Eventual consistency)。
*   **Pattern:** 使用事件驅動 (Event-driven) 架構。服務 A 完成操作後發送 Event，服務 B 訂閱並非同步更新資料。
*   **Trade-off:** 使用者可能在幾秒鐘內看到舊資料，但系統吞吐量與可用性大幅提升。

### 4. Smart Endpoints and Dumb Pipes
*   **Core Principle:** 業務邏輯應包含在微服務（Endpoints）中，而非依賴複雜的中介軟體（ESB）。訊息佇列（Pipes）應該只負責傳遞訊息，不處理業務路由或轉換。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Distributed Monolith (分散式單體)
這是最常見且最痛苦的失敗模式。
*   **Symptom:** 你把單體拆成了幾個服務，但它們之間高度耦合。部署服務 A 必須同時部署服務 B；服務 A 掛了，服務 B 也無法運作。
*   **Root Cause:** 透過同步 HTTP 呼叫過度依賴其他服務的內部資料，缺乏邊界上下文 (Bounded Context) 的隔離。
*   **Consequence:** 獲得了微服務的網路延遲與維運成本，卻沒得到微服務的獨立部署與擴充優勢。

### 2. Shared Database (共享資料庫)
多個微服務直接讀寫同一個資料庫 Schema。
*   **Why it's bad:** 這打破了服務的封裝性。一旦你需要修改資料表結構，所有相關的微服務都要修改並重新部署。
*   **Correction:** 每個微服務應擁有自己的資料庫（Database-per-service）。若需存取他人資料，請透過 API 或 Event。

### 3. Resume-Driven Development (履歷驅動開發)
在團隊規模很小（< 10 人）、業務邏輯尚不清晰、流量極低的情況下強行上微服務。
*   **Reality Check:** 單體架構 (Modular Monolith) 通常能支撐到相當大的規模。微服務是為了解決「組織擴張導致的協作效率降低」或「極端擴展性需求」，而非為了技術而技術。

---

## Checklists & workflows｜檢查清單與流程

在決定拆分服務或設計分散式互動時，請使用此清單進行自我檢核：

### Decision Framework: To Microservice or Not?
- [ ] **組織規模：** 團隊是否大到單體架構導致開發衝突頻繁？（通常 > 20-30 人才需考慮）
- [ ] **業務邊界：** 我們是否清楚該領域的 Bounded Context？（若業務還在頻繁變動，請保持單體）
- [ ] **維運能力：** 團隊是否具備自動化部署、容器編排 (K8s)、集中式 Log 與監控的能力？

### Design Checklist for a New Service
- [ ] **獨立性 (Autonomy):** 這個服務是否能獨立部署而不影響其他服務？
- [ ] **資料擁有權 (Data Ownership):** 這個服務是否擁有自己的私有資料存儲？
- [ ] **故障隔離 (Fault Isolation):** 如果這個服務依賴的下游服務掛了，它有 Fallback 方案嗎？
- [ ] **冪等性 (Idempotency):** 所有的寫入 (Write) API 是否都支援冪等操作？
- [ ] **可觀測性 (Observability):** 是否已實作 Correlation ID 以便在分散式 Log 中追蹤請求？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Order Creation (電商下單)

#### ❌ The Monolith Mindset (Distributed Monolith Approach)
1.  Frontend 呼叫 `Order Service`。
2.  `Order Service` 開啟一個分散式交易 (Two-Phase Commit, 2PC)。
3.  `Order Service` 同步 HTTP 呼叫 `Inventory Service` 扣庫存。
4.  `Order Service` 同步 HTTP 呼叫 `Payment Service` 扣款。
5.  若任一步驟失敗或超時，整個交易 Rollback。
*   **問題：** 系統極度脆弱。若 `Payment Service` 變慢，整個下單流程卡死，資料庫連線池耗盡，導致全站崩潰。

#### ✅ The Microservices Mindset (Event-Driven & Eventual Consistency)
1.  Frontend 呼叫 `Order Service`。
2.  `Order Service` 建立訂單，狀態設為 `PENDING`，並寫入本地 DB。
3.  `Order Service` 發送 `OrderCreated` 事件到 Message Queue。
4.  **非同步處理：**
    *   `Inventory Service` 訂閱事件 -> 嘗試扣庫存 -> 發送 `InventoryReserved` 或 `OutOfStock` 事件。
    *   `Payment Service` 訂閱事件 -> 嘗試扣款 -> 發送 `PaymentSucceeded` 或 `PaymentFailed` 事件。
5.  `Order Service` 根據回傳的事件更新訂單狀態為 `CONFIRMED` 或觸發補償流程 (Saga Pattern) 取消訂單。
*   **優勢：** 下單介面回應極快（只需寫入本地 DB）。即使支付系統維護中，使用者仍可下單，系統會稍後重試扣款。

### Code Concept: Handling Network Uncertainty

**Bad Practice (Assuming reliability):**
```javascript
// 如果 network 失敗，程式直接拋出 exception，使用者看到 500
const response = await httpClient.post('http://inventory-service/deduct', { itemId });
return response.data;
```

**Good Practice (Defensive coding):**
```javascript
try {
  // 設定 Timeout
  const response = await httpClient.post('http://inventory-service/deduct', { itemId }, { timeout: 2000 });
  return response.data;
} catch (error) {
  if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
    // 網路問題：重試或放入 Queue 稍後處理
    logger.warn('Inventory service unreachable, queuing for retry...');
    await retryQueue.add({ itemId, action: 'deduct' });
    return { status: 'pending_confirmation' }; // 告知使用者稍後確認
  }
  // 業務邏輯錯誤（如庫存不足）：直接回傳失敗
  throw error;
}
```