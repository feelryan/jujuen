# 1. 前言與學習目標 (Introduction & Learning Objectives)

在傳統的 CRUD 架構中，我們習慣將讀取（Read）與寫入（Write）操作綁定在同一個資料模型（Data Model）與資料庫實體上。然而，當系統面臨極端的讀寫比例差異（例如 1000:1 的讀寫比），或是業務邏輯需要絕對精確的歷程追溯（如金融帳務、供應鏈追蹤）時，單一模型往往成為效能與擴展性的瓶頸。

In traditional CRUD architectures, we are accustomed to binding Read and Write operations to the same Data Model and database entity. However, when a system faces extreme disparities in read/write ratios (e.g., a 1000:1 read-to-write ratio), or when business logic requires absolute historical precision (such as financial ledgers or supply chain tracking), a single model often becomes a bottleneck for performance and scalability.

本章將探討 **CQRS (Command Query Responsibility Segregation)** 與 **Event Sourcing** 這兩種常被一起討論、但可獨立使用的模式。完成本章後，你應該能夠：

This chapter explores **CQRS (Command Query Responsibility Segregation)** and **Event Sourcing**, two patterns that are often discussed together but can be used independently. After completing this chapter, you should be able to:

1.  **區分適用場景**：清楚判斷何時該引入 CQRS/Event Sourcing，以及何時這屬於過度設計（Over-engineering）。
    **Distinguish Use Cases**: Clearly judge when to introduce CQRS/Event Sourcing and when it constitutes over-engineering.
2.  **設計讀寫分離架構**：設計出 Write Side（專注於業務邏輯與一致性）與 Read Side（專注於查詢效能）分離的系統。
    **Design Segregated Architectures**: Design systems where the Write Side (focused on business logic and consistency) is separated from the Read Side (focused on query performance).
3.  **處理最終一致性（Eventual Consistency）**：在面試或實務中，提出具體策略來解決資料同步延遲帶來的 UX 或業務挑戰。
    **Handle Eventual Consistency**: Propose concrete strategies in interviews or practice to address UX or business challenges caused by data synchronization latency.
4.  **理解事件驅動的資料持久化**：掌握如何將「狀態（State）」視為「事件序列（Sequence of Events）」的衍生結果。
    **Understand Event-Driven Persistence**: Grasp how to view "State" as a derivative result of a "Sequence of Events."

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 CQRS：解耦讀與寫 (Decoupling Reads and Writes)

**直覺類比**：想像一家米其林餐廳。
- **Write Model (Command)**：廚房。這裡關注的是「動作」與「規則」（食材庫存、烹飪順序、衛生標準）。廚師不需要知道菜單排版好不好看，只在乎訂單能否被執行。
- **Read Model (Query)**：精美的菜單與外場展示櫃。這裡關注的是「呈現」與「速度」。菜單上的資料是經過整理的（Projection），目的是讓顧客快速決定，而不是為了管理庫存。

**Intuitive Analogy**: Imagine a Michelin-starred restaurant.
- **Write Model (Command)**: The Kitchen. It focuses on "Actions" and "Rules" (inventory, cooking sequence, hygiene standards). Chefs don't care about the menu layout; they only care if the order can be executed.
- **Read Model (Query)**: The exquisite menu and display case. It focuses on "Presentation" and "Speed." The data on the menu is curated (Projection) to help customers decide quickly, not to manage inventory.

**定義**：CQRS 是一種架構模式，它將改變資料的命令（Commands）與讀取資料的查詢（Queries）分開處理，通常會導致使用不同的資料模型，甚至不同的資料庫技術（例如 Write 用關聯式資料庫，Read 用 Elasticsearch 或 Redis）。

**Definition**: CQRS is an architectural pattern that separates operations that modify data (Commands) from operations that read data (Queries). This often leads to using different data models or even different database technologies (e.g., Relational DB for Write, Elasticsearch or Redis for Read).

## 2.2 Event Sourcing：狀態即歷程 (State as History)

**直覺類比**：銀行存摺（或區塊鏈）。
- 傳統 DB 存的是「餘額：$100」。
- Event Sourcing 存的是「開戶 $0」->「存入 $50」->「存入 $80」->「轉出 $30」。
- 目前的餘額 $100 只是這些事件重播（Replay）後的結果。

**Intuitive Analogy**: A bank ledger (or Blockchain).
- A traditional DB stores "Balance: $100".
- Event Sourcing stores "Account Opened $0" -> "Deposit $50" -> "Deposit $80" -> "Withdraw $30".
- The current balance of $100 is merely the result of replaying these events.

**關鍵差異**：
- **CRUD**：破壞性更新。更新一筆紀錄後，舊的狀態就消失了（除非有額外的 Audit Log）。
- **Event Sourcing**：Append-only。資料庫中只有 Insert，沒有 Update 或 Delete。

**Key Difference**:
- **CRUD**: Destructive updates. Once a record is updated, the old state is lost (unless there's an extra Audit Log).
- **Event Sourcing**: Append-only. The database only sees Inserts, never Updates or Deletes.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 System Design Interview 或大型專案中，我們不會無緣無故使用這些模式。通常是為了以下目的：

In System Design Interviews or large-scale projects, we don't use these patterns without reason. They are typically employed for the following purposes:

## 3.1 典型架構角色 (Typical Architectural Roles)

一個完整的 CQRS + Event Sourcing 架構通常包含以下組件：

A complete CQRS + Event Sourcing architecture typically includes the following components:

1.  **Command API**: 接收寫入請求（如 `PlaceOrder`）。
2.  **Domain Aggregate**: 執行業務邏輯驗證（如檢查庫存）。
3.  **Event Store**: 唯一的 Source of Truth（如 PostgreSQL, EventStoreDB），儲存不可變的事件（Events）。
4.  **Event Bus / Broker**: 廣播事件（如 Kafka, RabbitMQ）。
5.  **Projectors (Event Handlers)**: 訂閱事件，將資料轉換並寫入 Read Database。
6.  **Read Database**: 針對查詢優化的 DB（如 MongoDB, ElasticSearch, Neo4j）。
7.  **Query API**: 直接從 Read Database 讀取資料回傳給 Client。

1.  **Command API**: Receives write requests (e.g., `PlaceOrder`).
2.  **Domain Aggregate**: Executes business logic validation (e.g., checking inventory).
3.  **Event Store**: The single Source of Truth (e.g., PostgreSQL, EventStoreDB), storing immutable Events.
4.  **Event Bus / Broker**: Broadcasts events (e.g., Kafka, RabbitMQ).
5.  **Projectors (Event Handlers)**: Subscribe to events, transform data, and write to the Read Database.
6.  **Read Database**: A DB optimized for queries (e.g., MongoDB, ElasticSearch, Neo4j).
7.  **Query API**: Reads data directly from the Read Database and returns it to the Client.

## 3.2 對系統屬性的影響 (Impact on System Attributes)

-   **可擴充性 (Scalability)**: **極高**。讀寫可以獨立擴展。Read Side 可以有無數個 Replicas 或不同的 View。
    **Scalability**: **Very High**. Reads and writes can be scaled independently. The Read Side can have infinite replicas or different Views.
-   **一致性 (Consistency)**: **複雜**。Write Side 強一致，Read Side 最終一致（Eventual Consistency）。這是最大的 Trade-off。
    **Consistency**: **Complex**. Write Side is strongly consistent; Read Side is eventually consistent. This is the biggest trade-off.
-   **可觀測性與除錯 (Observability & Debugging)**: **強大**。你可以進行 "Time Travel" 除錯，將系統狀態回滾到任意時間點重現 Bug。
    **Observability & Debugging**: **Powerful**. You can perform "Time Travel" debugging, rolling back the system state to any point in time to reproduce a bug.

---

# 4. 逐步示例：電商購物車與訂單 (Walkthrough: E-Commerce Cart & Order)

## 4.1 問題背景 (Scenario)

我們需要設計一個購物車系統，行銷團隊希望分析使用者的「猶豫行為」（例如：放入購物車又拿出來，最後又放入的商品）。傳統 CRUD 只記錄最後購物車裡有什麼，無法滿足分析需求。

We need to design a shopping cart system where the marketing team wants to analyze user "hesitation behavior" (e.g., items added to the cart, removed, and then added again). Traditional CRUD only records what is currently in the cart, failing to meet analysis requirements.

## 4.2 從 Naive 到 Event Sourcing (From Naive to Event Sourcing)

### Naive Approach (CRUD)
資料表 `cart_items`：
```sql
UPDATE cart_items SET quantity = 2 WHERE user_id = 'u1' AND product_id = 'p1';
```
*缺點*：我們遺失了「使用者先設為 5，後來改為 2」的過程。

*Drawback*: We lose the history that "the user first set it to 5, then changed it to 2."

### Mature Approach (Event Sourcing)

我們不存「當前狀態」，而是存「發生了什麼」。

We don't store the "current state"; we store "what happened."

#### Step 1: 定義事件 (Define Events)
```typescript
interface ItemAddedToCart {
  type: 'ItemAddedToCart';
  data: { userId: string; productId: string; quantity: number; price: number };
  timestamp: Date;
}

interface ItemRemovedFromCart {
  type: 'ItemRemovedFromCart';
  data: { userId: string; productId: string };
  timestamp: Date;
}

interface CartCheckedOut {
  type: 'CartCheckedOut';
  data: { userId: string; totalAmount: number };
  timestamp: Date;
}
```

#### Step 2: 聚合根與狀態重建 (Aggregate & Rehydration)
當使用者要結帳（Command）時，我們需要知道當前總價。我們從 Event Store 讀取該使用者的所有事件並 `reduce` 出當前狀態。

When a user wants to checkout (Command), we need to know the current total. We read all events for that user from the Event Store and `reduce` them to derive the current state.

```typescript
class CartAggregate {
  private items: Map<string, number> = new Map(); // productId -> quantity
  private total: number = 0;

  // Replay events to build state
  public loadFromHistory(events: CartEvent[]) {
    for (const event of events) {
      this.apply(event);
    }
  }

  private apply(event: CartEvent) {
    switch (event.type) {
      case 'ItemAddedToCart':
        const qty = this.items.get(event.data.productId) || 0;
        this.items.set(event.data.productId, qty + event.data.quantity);
        this.total += event.data.quantity * event.data.price;
        break;
      case 'ItemRemovedFromCart':
        // logic to decrease total and remove item...
        break;
    }
  }

  // Command Logic
  public checkout(): CartCheckedOut {
    if (this.items.size === 0) throw new Error("Cart is empty");
    // Return new event to be saved
    return { 
      type: 'CartCheckedOut', 
      data: { userId: '...', totalAmount: this.total },
      timestamp: new Date()
    };
  }
}
```

#### Step 3: Projection (Read Model)
為了讓前端快速顯示購物車列表，我們不能每次都重算。我們有一個背景 Worker 監聽這些事件，並更新一個 Redis Hash 或 SQL Table。

To allow the frontend to quickly display the cart list, we can't recalculate every time. We have a background Worker listening to these events and updating a Redis Hash or SQL Table.

*   **Event**: `ItemAddedToCart` -> **Projector** -> `UPSERT INTO read_cart_view ...`

## 4.3 複雜度與邊界 (Complexity & Boundaries)

-   **時間複雜度**：重建狀態（Rehydration）是 $O(N)$，其中 $N$ 是事件數量。如果 $N$ 很大（例如長壽命的銀行帳戶），需要引入 **Snapshot** 機制（每 100 個事件存一個快照），將複雜度降為 $O(1) + O(k)$。
-   **空間複雜度**：儲存空間隨時間線性增長，永遠不刪除資料。

-   **Time Complexity**: State Rehydration is $O(N)$, where $N$ is the number of events. If $N$ is large (e.g., a long-lived bank account), a **Snapshot** mechanism is needed (saving a snapshot every 100 events) to reduce complexity to $O(1) + O(k)$.
-   **Space Complexity**: Storage space grows linearly with time; data is never deleted.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 為了用而用 (Resume Driven Development)
**錯誤**：在簡單的 CRUD 系統（如部落格文章管理）中使用 CQRS/ES。
**後果**：程式碼量增加 3-5 倍，除錯難度大增，新進人員上手困難。
**修正**：只有當「業務邏輯極其複雜」或「需要完整的 Audit Trail」時才使用。

**Mistake**: Using CQRS/ES in a simple CRUD system (like blog post management).
**Consequence**: Code volume increases 3-5x, debugging becomes much harder, and onboarding new hires is difficult.
**Correction**: Only use it when "business logic is extremely complex" or "a complete Audit Trail is required."

## 5.2 依賴同步 Projection (Relying on Synchronous Projections)
**錯誤**：在寫入 Command 後，強制等待 Read Model 更新完才回傳 Response 給 Client。
**後果**：失去了 CQRS 的效能優勢，且將 Write Side 的可用性與 Read Side 綁死。
**修正**：接受 Eventual Consistency。Client 端可以透過 Optimistic UI（樂觀更新）來欺騙使用者眼睛，或者由 Client 輪詢（Polling）。

**Mistake**: Forcing a wait for the Read Model update after a Write Command before returning a Response to the Client.
**Consequence**: Loses the performance benefits of CQRS and couples Write Side availability to the Read Side.
**Correction**: Accept Eventual Consistency. The Client can use Optimistic UI to trick the user's eye, or use Polling.

## 5.3 事件架構變更 (Event Schema Evolution)
**錯誤**：修改了事件結構（例如把 `price` 欄位改名），導致舊的事件無法被反序列化（Deserialize）。
**後果**：系統崩潰，無法重建 Aggregate 狀態。
**修正**：
1.  永遠不要修改舊事件。
2.  建立新版本的事件（`ItemAddedToCartV2`）。
3.  在 Code 層做 Upcasting（讀取舊事件時動態轉換為新結構）。

**Mistake**: Changing the event structure (e.g., renaming the `price` field), causing old events to fail deserialization.
**Consequence**: System crash; unable to rebuild Aggregate state.
**Correction**:
1.  Never modify old events.
2.  Create a new version of the event (`ItemAddedToCartV2`).
3.  Implement Upcasting in the code (dynamically transform old events to the new structure upon reading).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何處理 CQRS 中的「讀後寫（Read-Your-Own-Write）」延遲問題？
**How to handle "Read-Your-Own-Write" latency in CQRS?**

*   **情境**：使用者更新了個人資料，重新整理頁面，卻發現還是舊資料（因為 Read DB 還沒同步）。
*   **高分回答要點**：
    1.  **Client-side Intelligence**: 前端暫存更新後的值，不依賴立即的 GET 請求。
    2.  **Version/Token Tracking**: Command 回傳一個 Version ID，Query 時帶上這個 ID，如果 Read DB 的版本過舊，則 Read API 等待或從 Write DB 強制讀取（犧牲效能換取體驗）。
    3.  **Sticky Session**: 確保使用者的讀寫都導向同一組尚未同步但可能有快取的節點（較少見於分散式 DB）。

*   **Key Points for a High Score**:
    1.  **Client-side Intelligence**: Frontend caches the updated value, not relying on an immediate GET request.
    2.  **Version/Token Tracking**: Command returns a Version ID. The Query includes this ID. If the Read DB version is too old, the Read API waits or forces a read from the Write DB (sacrificing performance for UX).
    3.  **Sticky Session**: Ensure user reads/writes are routed to the same node which might have local caching (less common in distributed DBs).

## Q2: Event Sourcing 系統如何符合 GDPR（被遺忘權）的要求？
**How does an Event Sourcing system comply with GDPR (Right to be Forgotten)?**

*   **情境**：Event Store 是不可變（Immutable）的，不能刪除資料，但法律要求刪除使用者個資。
*   **高分回答要點**：
    1.  **Crypto-shredding (加密銷毀)**：所有敏感個資在存入 Event Store 前都用該使用者的專屬 Key 加密。當需要「刪除」時，只需銷毀該 Key。資料雖然還在，但已變成亂碼無法讀取。
    2.  **Stream Truncation**: 如果法規允許，可以重寫整個 Stream（類似 Git rebase），移除特定事件，但這在生產環境極其昂貴且危險。

*   **Key Points for a High Score**:
    1.  **Crypto-shredding**: All sensitive PII is encrypted with a user-specific Key before storing. To "delete," simply destroy the Key. The data remains but becomes unreadable ciphertext.
    2.  **Stream Truncation**: If regulations permit, rewrite the entire Stream (like Git rebase) to remove specific events, but this is extremely expensive and risky in production.

## Q3: 在微服務間，應該傳遞 Command 還是 Event？
**Should we pass Commands or Events between microservices?**

*   **高分回答要點**：
    *   **Service 內部**：使用 Command（意圖，Intent）。
    *   **Service 之間**：使用 Event（事實，Fact）。
    *   **理由**：Command 意味著耦合（發送者知道誰要處理），Event 意味著解耦（發送者只廣播「發生了什麼」，不關心誰在聽）。跨服務通訊應盡量降低耦合度，故 Event 較佳（Choreography pattern）。

*   **Key Points for a High Score**:
    *   **Inside a Service**: Use Command (Intent).
    *   **Between Services**: Use Event (Fact).
    *   **Reasoning**: Command implies coupling (sender knows who processes it). Event implies decoupling (sender broadcasts "what happened," doesn't care who listens). Cross-service communication should minimize coupling, so Events are preferred (Choreography pattern).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **CQRS** 將讀寫模型分離，解決了高讀寫落差與複雜 View 的需求。
2.  **Event Sourcing** 將狀態視為事件的總和，提供了完美的 Audit Log 與 Time-travel 能力。
3.  **Eventual Consistency** 是必然的代價，必須在 UI/UX 或業務流程中處理。
4.  **Snapshot** 是解決 Event Replay 效能問題的關鍵手段。
5.  **Schema Evolution** 需要謹慎處理，永遠不要修改已發生的事件。

1.  **CQRS** separates read and write models, solving high read/write disparity and complex View requirements.
2.  **Event Sourcing** treats state as the sum of events, offering perfect Audit Logs and Time-travel capabilities.
3.  **Eventual Consistency** is an inevitable cost that must be handled in UI/UX or business processes.
4.  **Snapshotting** is the key method to solve Event Replay performance issues.
5.  **Schema Evolution** requires caution; never modify events that have already occurred.

## 後續延伸 (Next Steps)
-   **分散式交易 (Distributed Transactions)**: 學習 **Saga Pattern**，這是基於事件驅動架構下處理跨服務交易的標準解法（下一章可能的重點）。
-   **工具研究**: 深入研究 **Apache Kafka** (作為 Event Bus) 或 **Axon Framework** (Java 生態系中成熟的 CQRS/ES 框架)。
-   **實作練習**: 嘗試用你熟悉的語言實作一個簡單的「記帳系統」，包含 `Deposit`, `Withdraw` 事件與 `Balance` Projection。

-   **Distributed Transactions**: Learn the **Saga Pattern**, the standard solution for cross-service transactions in event-driven architectures (potential focus for the next chapter).
-   **Tool Research**: Deep dive into **Apache Kafka** (as Event Bus) or **Axon Framework** (a mature CQRS/ES framework in the Java ecosystem).
-   **Hands-on Practice**: Try implementing a simple "Ledger System" in your preferred language, including `Deposit`, `Withdraw` events, and a `Balance` Projection.