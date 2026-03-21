# 行為模式：流程控制與事件驅動 / Behavioral Patterns: Flow Control and Event-Driven

本章節探討如何管理物件之間的演算法切換、職責分配與通訊。這些模式的核心價值在於將「做什麼（What）」與「誰來做（Who）」以及「何時做（When）」分離，從而避免巨大的條件判斷語句（Giant If-Else/Switch）與緊密耦合的組件。

This chapter explores how to manage algorithm switching, responsibility assignment, and communication between objects. The core value of these patterns lies in separating "What to do" from "Who does it" and "When to do it," thereby avoiding giant conditional statements and tightly coupled components.

---

## Mental model｜心智模型

要掌握行為模式，請將思維從「靜態結構」轉向「動態互動」。

To master behavioral patterns, shift your mindset from "static structure" to "dynamic interaction."

### 1. The "Plug-and-Play" Logic (隨插即用的邏輯)
不要將演算法寫死在物件內部。想像你的程式碼是一個遊戲主機，而演算法是「卡帶」。主機（Context）本身不變，但插入不同的卡帶（Strategy/State），行為就會完全改變。
Don't hardcode algorithms inside objects. Imagine your code is a game console, and algorithms are "cartridges." The console (Context) remains the same, but inserting a different cartridge (Strategy/State) completely changes the behavior.

### 2. The "Radio Broadcast" (廣播電台)
對於組件通訊，不要讓 A 直接打電話給 B、C、D。而是讓 A 成為廣播電台（Subject/Observable），發出訊號。B、C、D 如果感興趣，就訂閱這個頻道（Observer）。這樣 A 就不需要知道誰在聽，實現了解耦。
For component communication, don't let A call B, C, and D directly. Instead, let A be a radio station (Subject) broadcasting a signal. If B, C, and D are interested, they subscribe to the channel (Observer). A doesn't need to know who is listening, achieving decoupling.

### 3. The "Request as an Object" (請求即物件)
將「動作」封裝成一個包裹（Command）。這個包裹可以被排隊、被延遲、甚至被退回（Undo）。這將「發起請求的人」與「執行請求的人」完全隔開。
Encapsulate an "action" into a package (Command). This package can be queued, delayed, or even returned (Undo). This completely separates the "invoker" from the "receiver."

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Strategy Pattern (策略模式)
**Best for:** Runtime algorithm selection (e.g., Payment methods, Validation rules, Sorting strategies).
**適用於：** 執行時期的演算法切換（例如：支付方式、驗證規則、排序策略）。

*   **實戰技巧 (Practical Tip)**：
    *   **利用 Lambda/Functions**：在現代語言（JS/TS, Java 8+, C#）中，Strategy 往往不需要建立完整的 Class。直接傳遞 Function 或 Lambda 表達式通常更簡潔。
    *   **配合 Factory**：通常會結合 Factory 模式來根據設定檔或使用者輸入決定要實例化哪個 Strategy。

### 2. Observer / Pub-Sub Pattern (觀察者 / 發布訂閱模式)
**Best for:** One-to-many dependencies, Event handling, UI updates based on data changes.
**適用於：** 一對多的依賴關係、事件處理、基於數據變更的 UI 更新。

*   **實戰技巧 (Practical Tip)**：
    *   **區分同步與非同步**：標準 Observer 通常是同步執行的（Subject 呼叫 notify 時直接執行 Observer 方法）。如果處理耗時，請務必引入 Message Queue 或 Event Bus 轉為非同步。
    *   **Immutable Data**：傳遞給 Observer 的數據最好是不可變的（Immutable），避免某個 Observer 偷偷修改數據影響到其他訂閱者。

### 3. Command Pattern (命令模式)
**Best for:** Task scheduling, Undo/Redo operations, Transactional behavior.
**適用於：** 任務排程、復原/重做操作、交易行為。

*   **實戰技巧 (Practical Tip)**：
    *   **序列化 (Serialization)**：將 Command 設計為可序列化的（JSON），這樣你可以將未執行的命令存入資料庫（Job Queue），系統重啟後仍可繼續執行。
    *   **巨集命令 (Macro Command)**：Command 可以包含其他 Command，形成組合模式，用於執行「批次任務」。

### 4. State Pattern (狀態模式)
**Best for:** Objects with complex lifecycles where behavior depends on current state (e.g., Order status, TCP Connection, Game Character).
**適用於：** 具有複雜生命週期且行為取決於當前狀態的物件（例如：訂單狀態、TCP 連線、遊戲角色）。

*   **實戰技巧 (Practical Tip)**：
    *   **消除 Boolean Flags**：如果你發現物件裡有 `isPaid`, `isShipped`, `isCancelled` 等多個 boolean 且互相牽制，請立刻重構為 State Pattern。
    *   **狀態表驅動 (Table-Driven)**：對於簡單的狀態機，可以使用 Map 或 Dictionary 來定義 `(CurrentState, Event) -> NextState` 的映射，比寫一堆 Class 更輕量。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Lapsed Listener Problem (失效的監聽者)
*   **Symptom**: 記憶體洩漏（Memory Leak）。
*   **Context**: 在 Observer 模式中，訂閱者（Observer）註冊後忘記取消訂閱（Unsubscribe）。導致 Subject 持有對 Observer 的引用，GC 無法回收。
*   **Fix**: 實作 `dispose()` 或 `unsubscribe()` 機制，並確保在組件銷毀時呼叫。

### 2. State Explosion (狀態爆炸)
*   **Symptom**: 為了處理極其細微的差異，建立了數十個 State 類別。
*   **Context**: 過度應用 State Pattern，導致類別數量失控。
*   **Fix**: 如果狀態之間的行為差異很小，考慮使用參數化配置，或者將部分邏輯合併。不要為了模式而模式。

### 3. Logic in the Wrong Place (邏輯錯置)
*   **Symptom**: Context 類別仍然充滿了 `if (state is StateA)` 的判斷。
*   **Context**: 雖然用了 State 或 Strategy 模式，但呼叫端（Client/Context）還是試圖控制細節，沒有真正授權給策略物件。
*   **Fix**: 確保 Context 只負責 `execute()`，具體判斷邏輯應封裝在具體的 State/Strategy 類別中。

### 4. Event Hell (事件地獄)
*   **Symptom**: 程式執行流程極難追蹤，Debug 時在各個 Event Handler 間跳來跳去。
*   **Context**: 過度依賴全域 Event Bus，導致資料流向不透明。
*   **Fix**: 限制 Event 的作用域（Scope）。優先使用區域性的 Observer，謹慎使用全域 Event Bus。

---

## Checklists & workflows｜檢查清單與流程

### Decision Framework: Which pattern to use? (決策框架)

- [ ] **需要「復原 (Undo)」功能嗎？**
    - YES $\rightarrow$ **Command Pattern** (將操作封裝為物件，並保存反向操作邏輯)。
- [ ] **有多個演算法需要動態切換嗎？** (例如：依據會員等級計算折扣)
    - YES $\rightarrow$ **Strategy Pattern** (消除 `switch-case` 計算邏輯)。
- [ ] **一個物件改變，需要通知其他多個物件嗎？**
    - YES $\rightarrow$ **Observer Pattern** (解耦通知源與接收者)。
- [ ] **物件的行為是否完全取決於它目前的狀態？** (例如：訂單「已付款」後不能「取消」，只能「退款」)
    - YES $\rightarrow$ **State Pattern** (將每個狀態的行為封裝在獨立類別)。

### Implementation Checklist (實作檢查清單)

- [ ] **Strategy**: Context 是否只依賴介面（Interface），而不依賴具體實作？
- [ ] **Observer**: 是否提供了 Unsubscribe/Dispose 的機制以防止記憶體洩漏？
- [ ] **Command**: Command 物件是否包含執行該動作所需的所有資訊（Self-contained）？
- [ ] **State**: 狀態轉換（Transition）的邏輯是放在 Context 還是 State 類別中？（建議統一，通常放在 State 中較靈活，但放在 Context 中較易讀）。

---

## Real-world examples｜實戰案例

### Scenario 1: E-commerce Order Processing (State Pattern)
**情境**：電商訂單流轉。訂單有 `New`, `Paid`, `Shipped`, `Delivered`, `Cancelled` 等狀態。
**問題**：在 `Order` 類別中寫滿了 `if (status == 'Paid') { ... }`，且邏輯越來越複雜（例如：只有 `Paid` 狀態可以轉 `Shipped`）。

**Solution**:
```typescript
interface OrderState {
    cancel(order: Order): void;
    ship(order: Order): void;
}

class PaidState implements OrderState {
    cancel(order: Order) {
        console.log("Initiating refund...");
        order.setState(new CancelledState());
    }
    ship(order: Order) {
        console.log("Generating shipping label...");
        order.setState(new ShippedState());
    }
}

class ShippedState implements OrderState {
    cancel(order: Order) {
        throw new Error("Cannot cancel shipped order. Return required.");
    }
    ship(order: Order) {
        throw new Error("Already shipped.");
    }
}
// Context delegates calls to current state
```

### Scenario 2: Job Queue System (Command Pattern)
**情境**：一個背景任務系統，需要處理「發送 Email」、「生成 PDF」、「清理快取」。
**問題**：需要將這些請求排隊，並且在失敗時重試。

**Solution**:
定義 `Command` 介面 `execute()`。將所有請求封裝成 `SendEmailCommand`, `GeneratePdfCommand`。
Worker 只需要從 Queue 中取出 Command 並呼叫 `.execute()`，完全不需要知道具體業務邏輯。如果失敗，將 Command 物件放回 Queue 或 Dead Letter Queue。

### Scenario 3: Form Validation (Strategy Pattern)
**情境**：一個表單驗證器，需要根據不同國家驗證手機號碼格式。
**問題**：不想在驗證器裡寫死所有國家的 Regex。

**Solution**:
```typescript
// Context
class PhoneValidator {
    constructor(private strategy: ValidationStrategy) {}

    validate(phoneNumber: string): boolean {
        return this.strategy.isValid(phoneNumber);
    }
}

// Usage
const usValidator = new PhoneValidator(new USPhoneStrategy());
const twValidator = new PhoneValidator(new TWPhoneStrategy());
```