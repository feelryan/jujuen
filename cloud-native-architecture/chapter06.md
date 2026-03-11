# 1. 前言與學習目標 (Introduction & Learning Objectives)

在單體式架構（Monolithic Architecture）中，資料一致性通常依賴關聯式資料庫的 ACID 交易（Transactions）。然而，當我們轉向雲原生與微服務架構時，資料被分散在不同的服務與資料庫中，傳統的 ACID 難以適用。本章將探討如何在分散式環境下權衡可用性與一致性。

In a monolithic architecture, data consistency typically relies on the ACID transactions of relational databases. However, as we shift to Cloud-Native and microservices architectures, data is scattered across different services and databases, making traditional ACID difficult to apply. This chapter explores how to balance availability and consistency in a distributed environment.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **正確運用 CAP 定理與 PACELC**：不再只是背誦定義，而是能根據業務需求（如支付 vs. 社交動態）決定選擇強一致性（Strong Consistency）還是最終一致性（Eventual Consistency）。
    **Apply CAP Theorem and PACELC correctly**: Move beyond rote memorization to deciding between Strong Consistency and Eventual Consistency based on business needs (e.g., payments vs. social feeds).
2.  **設計與實作 Saga 模式**：理解協同式（Choreography）與編排式（Orchestration）的差異，並能設計補償事務（Compensating Transactions）來處理失敗。
    **Design and implement the Saga Pattern**: Understand the difference between Choreography and Orchestration, and design Compensating Transactions to handle failures.
3.  **評估 CQRS 的適用性**：知道何時應該將讀寫分離，以及如何處理隨之而來的資料同步延遲問題。
    **Evaluate the applicability of CQRS**: Know when to separate reads from writes and how to handle the resulting data synchronization latency.
4.  **解決「雙寫問題」（Dual Write Problem）**：掌握 Transactional Outbox Pattern，確保資料庫更新與訊息發送的原子性。
    **Solve the "Dual Write Problem"**: Master the Transactional Outbox Pattern to ensure atomicity between database updates and message publishing.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 從 ACID 到 BASE (From ACID to BASE)

在雲原生架構中，我們的心智模型必須從「單一巨大的鎖」轉變為「一系列的狀態轉換」。

In Cloud-Native architecture, our mental model must shift from "one giant lock" to "a series of state transitions."

-   **ACID (Atomicity, Consistency, Isolation, Durability)**：適用於單一資料庫。它保證交易要麼全做，要麼全不做，且當下即時一致。
    **ACID**: Applies to a single database. It guarantees that a transaction is either fully completed or not at all, with immediate consistency.
-   **BASE (Basically Available, Soft state, Eventual consistency)**：適用於分散式系統。我們接受系統在短時間內狀態不一致，但保證最終會達到一致狀態。
    **BASE**: Applies to distributed systems. We accept that the system may be inconsistent for a short period but guarantee it will eventually reach a consistent state.

> **類比 (Analogy)**：
> ACID 就像是「一手交錢，一手交貨」，雙方必須同時在場，交易才能完成。
> BASE 就像是「網購」，你下單（狀態改變），倉庫出貨（非同步），最後快遞送到你手中（最終一致）。中間會有時間差，但系統保證你最終會收到貨或退款。
>
> **Analogy**:
> ACID is like a "cash on delivery" exchange; both parties must be present simultaneously for the transaction to complete.
> BASE is like "online shopping"; you place an order (state change), the warehouse ships it (asynchronous), and finally, the courier delivers it (eventual consistency). There is a time lag, but the system guarantees you eventually get the item or a refund.

## 2.2 CAP 定理的現代解讀 (Modern Interpretation of CAP Theorem)

CAP（Consistency, Availability, Partition Tolerance）指出這三者最多只能同時滿足兩者。但在雲端環境（Cloud Environment）中，網路分區（Partition）是不可避免的常態（例如光纖被挖斷、交換機故障）。

CAP states that you can only have two out of Consistency, Availability, and Partition Tolerance. However, in a Cloud Environment, Partition Tolerance is an unavoidable reality (e.g., fiber cuts, switch failures).

因此，真正的選擇只有 **CP** 或 **AP**：
Therefore, the real choice is only between **CP** and **AP**:

-   **CP (Consistency over Availability)**：發生網路分區時，拒絕服務以保護資料正確性。例如：銀行轉帳核心系統。
    **CP**: Refuse service to protect data correctness during a partition. E.g., Core banking transfer systems.
-   **AP (Availability over Consistency)**：發生網路分區時，繼續提供服務，但可能讀到舊資料。例如：Facebook 的按讚數、Amazon 的購物車（允許衝突，稍後解決）。
    **AP**: Continue service during a partition, potentially returning stale data. E.g., Facebook likes, Amazon shopping cart (allow conflicts, resolve later).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 跨微服務的業務流程 (Cross-Microservice Business Processes)

在 Production 環境中，一個簡單的「購買」動作可能橫跨多個服務：
In a production environment, a simple "buy" action might span multiple services:

1.  **Order Service**: 建立訂單。 (Create Order)
2.  **Inventory Service**: 扣減庫存。 (Deduct Inventory)
3.  **Payment Service**: 執行扣款。 (Process Payment)
4.  **Shipping Service**: 安排物流。 (Schedule Shipping)

### 為什麼不能用 2PC (Two-Phase Commit)?
### Why not use 2PC (Two-Phase Commit)?

雖然 XA/2PC 協議提供強一致性，但在雲原生環境中極少使用，原因如下：
Although XA/2PC protocols offer strong consistency, they are rarely used in Cloud-Native environments because:

-   **效能殺手 (Performance Killer)**：所有參與者必須鎖定資源直到協調者（Coordinator）完成提交。這會造成嚴重的鎖競爭（Lock Contention）。
    **Performance Killer**: All participants must lock resources until the Coordinator commits. This causes severe lock contention.
-   **單點故障 (SPOF)**：協調者掛了，所有服務都會卡住。
    **SPOF**: If the coordinator fails, all services hang.
-   **不支援異質系統 (No Support for Heterogeneous Systems)**：你無法對外部 API（如 Stripe, Twilio）執行 2PC。
    **No Support for Heterogeneous Systems**: You cannot perform 2PC against external APIs (e.g., Stripe, Twilio).

## 3.2 系統設計決策 (System Design Decisions)

在設計時，資深工程師會依據「業務容錯度」來選擇模式：
When designing, senior engineers choose patterns based on "business tolerance":

-   **高價值、低頻率 (High Value, Low Frequency)**：如資金結算，可考慮使用具有強一致性保證的專用資料庫或分散式鎖，甚至犧牲部分可用性。
    **High Value, Low Frequency**: Like financial settlement, consider specialized databases with strong consistency guarantees or distributed locks, potentially sacrificing some availability.
-   **高併發、使用者體驗優先 (High Concurrency, UX First)**：如電商下單，使用 **Saga Pattern** 搭配 **Eventual Consistency**。先讓使用者下單成功，若庫存不足再發送 Email 取消訂單並退款（補償機制）。
    **High Concurrency, UX First**: Like e-commerce checkout, use the **Saga Pattern** with **Eventual Consistency**. Let the user order first; if inventory is out, send an email to cancel and refund (compensation mechanism).

---

# 4. 逐步示例：實作 Saga 模式 (Walkthrough: Implementing Saga Pattern)

假設我們要實作一個「旅遊預訂系統」，包含機票（Flight）與飯店（Hotel）。

Let's implement a "Travel Booking System" involving Flights and Hotels.

### 4.1 挑戰 (The Challenge)

我們需要同時預訂機票和飯店。如果機票預訂成功但飯店滿了，我們必須取消機票（回滾）。
We need to book both flight and hotel. If the flight is booked but the hotel is full, we must cancel the flight (rollback).

### 4.2 方案 A：協同式 Saga (Choreography-based Saga)

服務之間透過事件（Events）互相溝通，沒有中央指揮者。
Services communicate via Events without a central commander.

**流程 (Flow):**
1.  `Order Service` 建立訂單 -> 發布 `OrderCreated` 事件。
2.  `Flight Service` 監聽 `OrderCreated` -> 預訂機票 -> 發布 `FlightBooked`。
3.  `Hotel Service` 監聽 `FlightBooked` -> 嘗試預訂飯店。
    -   **成功 (Success)**: 發布 `HotelBooked` -> `Order Service` 將訂單標記為完成。
    -   **失敗 (Failure)**: 發布 `HotelBookingFailed`。
4.  `Flight Service` 監聽 `HotelBookingFailed` -> **執行補償事務 (Compensating Transaction)** 取消機票 -> 發布 `FlightBookingCancelled`。
5.  `Order Service` 監聽 `FlightBookingCancelled` -> 將訂單標記為失敗。

**優點 (Pros)**: 簡單，低耦合。
**缺點 (Cons)**: 流程複雜時難以追蹤（誰觸發了誰？），容易產生循環依賴。

### 4.3 方案 B：編排式 Saga (Orchestration-based Saga) - *推薦用於複雜流程*

引入一個 `Saga Orchestrator`（如 AWS Step Functions, Temporal, 或自建的 State Machine）來指揮流程。

Introduce a `Saga Orchestrator` (e.g., AWS Step Functions, Temporal, or a custom State Machine) to direct the flow.

**虛擬碼示例 (Pseudo-code Example):**

```typescript
class TravelBookingSaga {
  
  async execute(bookingRequest: Request) {
    const sagaId = generateId();
    
    try {
      // Step 1: Book Flight
      // 呼叫 Flight Service (Call Flight Service)
      const flightResult = await flightService.book(bookingRequest.flightId);
      
      // Step 2: Book Hotel
      // 呼叫 Hotel Service (Call Hotel Service)
      try {
        const hotelResult = await hotelService.book(bookingRequest.hotelId);
      } catch (hotelError) {
        // 飯店失敗，觸發機票補償 (Hotel failed, trigger flight compensation)
        await flightService.cancel(flightResult.bookingId);
        throw new Error("Hotel booking failed, flight cancelled");
      }
      
      // Step 3: Confirm Order
      await orderService.confirm(sagaId);
      
    } catch (e) {
      // 全局失敗處理 (Global failure handling)
      await orderService.fail(sagaId, e.message);
    }
  }
}
```

**為何這在實務中可行？ (Why this works in practice?)**
它將流程邏輯集中化，易於測試與監控。若使用 Temporal 等工具，甚至能自動處理重試（Retries）與狀態保存，解決了「Orchestrator 當機」的問題。

It centralizes flow logic, making it easier to test and monitor. Tools like Temporal can even handle retries and state persistence automatically, solving the "Orchestrator crash" problem.

### 4.4 關鍵技術：Transactional Outbox Pattern

在上述流程中，如何保證「寫入本地 DB」與「發送 Event」是原子的？如果 DB 寫入成功但 Event Broker 掛了怎麼辦？

In the above flows, how do we guarantee atomicity between "writing to local DB" and "publishing an Event"? What if the DB write succeeds but the Event Broker is down?

**解決方案 (Solution):**
1.  在同一個 DB Transaction 中，將業務資料與 Event 資料寫入一張 `Outbox` Table。
2.  使用一個獨立的 Process（或 CDC 工具如 Debezium）讀取 `Outbox` Table 並發送到 Message Queue。

**Solution:**
1.  Within the same DB Transaction, write business data and Event data to an `Outbox` Table.
2.  Use a separate process (or CDC tool like Debezium) to read the `Outbox` Table and publish to the Message Queue.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 分散式單體 (Distributed Monolith)

**錯誤描述**：微服務之間使用 HTTP 同步呼叫串聯。例如 Service A 呼叫 B，B 呼叫 C，C 呼叫 D。
**Error Description**: Microservices chained together using synchronous HTTP calls. E.g., Service A calls B, B calls C, C calls D.

**為何不好**：
**Why it's bad**:
-   **延遲疊加 (Latency Accumulation)**：總延遲是所有服務延遲的總和。
-   **可用性降低 (Availability Drop)**：任何一個服務掛掉，整個鏈條都會失敗。
-   **替代方案**：使用非同步訊息傳遞（Asynchronous Messaging）或 Saga 模式。

## 5.2 忽略冪等性 (Ignoring Idempotency)

**錯誤描述**：在重試機制（Retry）下，沒有處理重複請求。
**Error Description**: Not handling duplicate requests under retry mechanisms.

**為何不好**：
**Why it's bad**:
-   在分散式系統中，網路超時是常態。上游服務超時重試，可能導致下游服務重複扣款或重複出貨。
-   **替代方案**：所有具備副作用（Side-effect）的 API 都必須實作冪等性（Idempotency Key）。
    -   `POST /payment` 應包含 `Idempotency-Key: uuid-1234`。如果 Server 發現該 Key 已處理過，直接回傳上次的成功結果，不執行扣款。

## 5.3 濫用 CQRS (Overusing CQRS)

**錯誤描述**：對簡單的 CRUD 服務也使用 CQRS（Command Query Responsibility Segregation），將讀寫模型完全分離。
**Error Description**: Using CQRS for simple CRUD services, completely separating read and write models.

**為何不好**：
**Why it's bad**:
-   **複雜度爆炸 (Complexity Explosion)**：你需要維護兩個資料模型、處理同步延遲（Lag），並解決「讀不到剛寫入資料」的問題。
-   **替代方案**：除非讀寫負載差異極大，或讀取邏輯極度複雜，否則標準的 CRUD 即可。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你如何在微服務中處理分散式交易？(How do you handle distributed transactions in microservices?)

**高分回答要點 (Key Points for a High Score):**
-   首先表明**避免分散式交易**是最佳策略（透過良好的邊界劃分）。
    State that **avoiding distributed transactions** is the best strategy (via good boundary context definition).
-   解釋 **Saga Pattern** 是標準解法，並能比較 Choreography 與 Orchestration 的優缺點。
    Explain that **Saga Pattern** is the standard solution and compare Choreography vs. Orchestration.
-   必須提到 **補償事務 (Compensation)** 的概念，即「無法 Rollback，只能執行反向操作」。
    Must mention **Compensation**, i.e., "cannot rollback, can only execute reverse operations."
-   加分項：提到 **Transactional Outbox Pattern** 來確保訊息發送的可靠性。
    Bonus: Mention **Transactional Outbox Pattern** for reliable message delivery.

## Q2: 什麼是最終一致性？會帶來什麼問題？如何解決？(What is Eventual Consistency? What problems does it cause, and how to solve them?)

**高分回答要點 (Key Points for a High Score):**
-   定義：系統保證在沒有新更新的情況下，所有副本最終會同步。
    Definition: The system guarantees that if no new updates are made, all replicas will eventually converge.
-   問題：使用者可能讀到舊資料（Stale Read）。例如，使用者剛修改個人資料，刷新頁面卻看到舊的。
    Problem: Users might read stale data. E.g., a user updates their profile but sees the old one upon refresh.
-   解決方案：
    -   **Read-your-own-writes (Session Consistency)**：將該使用者的讀取路由到主庫（Primary）或剛寫入的節點。
    -   **UI 欺騙 (UI Optimistic Updates)**：前端先顯示更新後的值，後端慢慢同步。

## Q3: 在 Saga 模式中，如果補償事務（Compensating Transaction）也失敗了怎麼辦？(In Saga, what if the Compensating Transaction also fails?)

**高分回答要點 (Key Points for a High Score):**
-   這是一個極端情況（Edge Case）。
    This is an edge case.
-   **重試 (Retry)**：補償操作必須設計為**冪等 (Idempotent)**，這樣可以無限重試直到成功。
    **Retry**: Compensation operations must be **idempotent** so they can be retried indefinitely until success.
-   **人工介入 (Manual Intervention / Dead Letter Queue)**：如果重試多次仍失敗（例如程式碼 Bug 或資料庫損壞），則將事件送入 Dead Letter Queue (DLQ)，觸發警報，由營運人員手動修復資料。
    **Manual Intervention**: If retries fail (e.g., bug or DB corruption), send to a Dead Letter Queue (DLQ), trigger an alert, and have ops manually fix the data.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **CAP 定理**：在雲端分散式系統中，P (Partition Tolerance) 是前提，我們通常在 CP (強一致性) 與 AP (高可用性) 之間做取捨。
2.  **Saga 模式**：取代了 2PC。透過一系列的本地交易與事件驅動來完成長流程，失敗時執行補償事務。
3.  **冪等性 (Idempotency)**：是分散式系統可靠性的基石，確保重試不會破壞資料。
4.  **Outbox Pattern**：解決了微服務中「更新資料庫」與「發送訊息」的原子性問題。
5.  **CQRS**：強大的讀寫分離模式，但帶來了複雜度與一致性延遲，需謹慎使用。

## 後續延伸 (Next Steps)

-   **實作練習**：嘗試使用 Temporal.io 或 AWS Step Functions 實作一個簡單的 Saga 流程。
-   **延伸閱讀**：下一章將探討 **Observability (可觀測性)**。當資料分散在各地，交易是非同步時，Distributed Tracing (如 OpenTelemetry) 成為除錯的唯一救命稻草。
    **Further Reading**: The next chapter will explore **Observability**. When data is distributed and transactions are asynchronous, Distributed Tracing (e.g., OpenTelemetry) becomes the only lifeline for debugging.