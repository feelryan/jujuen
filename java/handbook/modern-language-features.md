# 現代 Java 語法特性 (Records, Sealed Classes, Pattern Matching) / Modern Java Features (Records, Sealed Classes, Pattern Matching)

## Mental model｜心智模型

現代 Java（Java 14 至 Java 21+）的演進核心，是將語言從傳統的「冗長且以可變狀態為中心的 Bean 模型」推向「以資料為導向、不可變性（Immutability）與代數資料型別（Algebraic Data Types, ADTs）」的現代化設計。
The core evolution of modern Java (Java 14 to Java 21+) shifts the language from the traditional "verbose, mutable bean-centric model" towards a "data-oriented, immutable, and Algebraic Data Types (ADTs)" modern design.

作為資深工程師，你應該建立以下的心智模型：
As a senior engineer, you should adopt the following mental model:

1. **Records = 透明的資料載體 (Transparent Data Carriers)**
   不要把它們當作「少寫 Getter/Setter 的語法糖」，把它們視為「純粹的資料」。它們的語意是：我的狀態就是這些欄位，沒有隱藏的內部狀態，且預設不可變（Shallowly Immutable）。
   Do not treat them merely as "syntactic sugar to avoid writing getters/setters". Treat them as "pure data". Their semantics mean: my state is exactly these fields, there is no hidden internal state, and they are shallowly immutable by default.
2. **Sealed Classes = 受控的繼承體系 (Controlled Inheritance)**
   傳統介面是開放的（任何人都可以實作），而 Sealed Classes 是封閉的。它告訴編譯器與開發者：「這個領域概念的子型別是有限且已知的（Sum Types）」。
   Traditional interfaces are open (anyone can implement them), whereas Sealed Classes are closed. It tells the compiler and developers: "The subtypes of this domain concept are finite and known (Sum Types)."
3. **Pattern Matching = 安全的解構與分派 (Safe Deconstruction and Dispatch)**
   取代過去充滿雜訊的 `instanceof` 檢查與強制轉型。它讓你能夠以宣告式的方式，根據資料的「形狀（Shape）」與「型別（Type）」來提取資料並執行邏輯。
   Replacing the noisy `instanceof` checks and casting of the past. It allows you to declaratively extract data and execute logic based on the "shape" and "type" of the data.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Records 作為 DTOs 與領域事件 (Records as DTOs and Domain Events)
在 API 請求/回應、資料庫 Projection 或訊息佇列的事件中，使用 Records 是最佳選擇。它們天生具備正確的 `equals()`, `hashCode()`, 與 `toString()`。
Using Records is the best choice for API requests/responses, database projections, or message queue events. They inherently possess correct `equals()`, `hashCode()`, and `toString()` implementations.

### 2. 利用精簡建構子進行防禦性驗證 (Defensive Validation via Compact Constructors)
Records 允許你宣告「精簡建構子（Compact Constructors）」，你不需要重新指派欄位，只需專注於驗證邏輯與資料清理。
Records allow you to declare "Compact Constructors". You don't need to reassign fields; you only focus on validation logic and data sanitization.

```java
public record UserAccount(String username, String email) {
    // Compact constructor
    public UserAccount {
        if (username == null || username.isBlank()) {
            throw new IllegalArgumentException("Username cannot be blank");
        }
        email = email.toLowerCase(); // Data sanitization
    }
}
```

### 3. 以 Sealed Classes 建立領域狀態機 (Modeling Domain State Machines with Sealed Classes)
當你的業務邏輯有明確的狀態（如：付款成功、付款失敗、處理中），使用 Sealed Classes 搭配 Records 可以完美建立出不會出現非法狀態的模型。
When your business logic has explicit states (e.g., Payment Success, Payment Failed, Processing), using Sealed Classes with Records perfectly models the domain without allowing illegal states.

### 4. 窮舉式的 Switch 表達式 (Exhaustive Switch Expressions)
當 Switch 搭配 Sealed Classes 時，編譯器會強制要求你處理所有可能的子類別。**不要寫 `default` 分支**，這樣當未來新增子類別時，編譯器會主動報錯提醒你補上邏輯。
When Switch is used with Sealed Classes, the compiler enforces that you handle all possible subclasses. **Do not write a `default` branch**, so when a new subclass is added in the future, the compiler will fail and remind you to implement the new logic.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 踩雷點 1：Records 的淺層不可變性陷阱 (The Shallow Immutability Trap of Records)
**問題 (Problem):** Records 只保證欄位參考不可變，但如果欄位本身是可變物件（如 `List`, `Date`, `HashMap`），外部依然可以修改它。
Records only guarantee that the field references are immutable. If the field itself is a mutable object (like `List`, `Date`, `HashMap`), it can still be modified externally.
**解法 (Solution):** 在精簡建構子中進行防禦性複製（Defensive Copying）。
Perform defensive copying in the compact constructor.

```java
// Anti-pattern: The tags list can be mutated externally
public record Article(String title, List<String> tags) {}

// Best Practice: Defensive copy using List.copyOf()
public record Article(String title, List<String> tags) {
    public Article {
        tags = List.copyOf(tags); // Makes the list unmodifiable
    }
}
```

### ❌ 踩雷點 2：濫用 Sealed Classes 限制擴充性 (Overusing Sealed Classes Restricting Extensibility)
**問題 (Problem):** 將基礎設施層的介面（如 `PaymentProcessor` 或 `Repository`）宣告為 `sealed`，導致未來無法輕易透過依賴注入（DI）新增實作或進行 Mock 測試。
Declaring infrastructure-level interfaces (like `PaymentProcessor` or `Repository`) as `sealed`, making it impossible to easily add implementations via Dependency Injection (DI) or mock them for testing in the future.
**解法 (Solution):** Sealed Classes 應該專注於「領域資料模型（Domain Data Models）」與「事件（Events）」，而非「服務或行為（Services or Behaviors）」。
Sealed Classes should focus on "Domain Data Models" and "Events", not "Services or Behaviors".

### ❌ 踩雷點 3：擁有過多欄位的 Records (Massive Records with Too Many Fields)
**問題 (Problem):** Records 沒有內建的 Builder 模式。當一個 Record 有超過 5-6 個欄位時，建構它會變得非常容易傳錯參數順序。
Records do not have a built-in Builder pattern. When a Record has more than 5-6 fields, constructing it becomes highly prone to passing arguments in the wrong order.
**解法 (Solution):** 考慮將大 Record 拆分成多個具備業務意義的小 Records（組合優於繼承），或者引入第三方庫（如 RecordBuilder）來生成 Builder。
Consider breaking down large Records into smaller, business-meaningful Records (composition over inheritance), or introduce third-party libraries (like RecordBuilder) to generate builders.

---

## Checklists & workflows｜檢查清單與流程

### 🛠️ 決策樹：我該用 Class, Record 還是 Sealed Class？ (Decision Tree: Class, Record, or Sealed Class?)

1. 這個物件需要改變內部的狀態嗎？ (Does this object need to mutate its internal state?)
   👉 **Yes**: 使用傳統 `class`。 (Use traditional `class`.)
2. 這個物件純粹是用來傳遞不可變資料的嗎？ (Is this object purely used to carry immutable data?)
   👉 **Yes**: 使用 `record`。 (Use `record`.)
3. 這個介面/類別的子型別，在業務領域中是固定且已知數量的嗎？ (Are the subtypes of this interface/class fixed and known in the business domain?)
   👉 **Yes**: 使用 `sealed interface/class`。 (Use `sealed interface/class`.)

### ✅ 實戰檢查清單 (Practical Checklist)

- [ ] **Immutability Check**: 我是否確保了 Record 中的集合型別（如 `List`, `Map`）都使用了 `List.copyOf()` 或 `Collections.unmodifiable...` 進行封裝？ (Did I ensure collection types in Records are encapsulated using `List.copyOf()`?)
- [ ] **Validation Check**: 我是否利用了 Record 的 Compact Constructor 來集中處理 `null` 檢查與業務規則驗證？ (Did I utilize the Compact Constructor for centralized `null` checks and business rule validation?)
- [ ] **Exhaustiveness Check**: 在處理 Sealed Classes 的 `switch` 表達式時，我是否移除了 `default` 分支，讓編譯器幫我把關窮舉性？ (Did I remove the `default` branch in `switch` expressions handling Sealed Classes to let the compiler enforce exhaustiveness?)
- [ ] **Framework Compatibility**: 我使用的 JSON 序列化庫（如 Jackson）或 ORM（如 Hibernate）版本是否夠新，能夠原生支援 Records？ (Are my JSON serialization libraries or ORMs modern enough to natively support Records?)

---

## Real-world examples｜實戰案例

以下是一個結合 **Sealed Classes**, **Records** 與 **Pattern Matching (Java 21+)** 的真實電商支付處理案例。這個設計保證了型別安全，且徹底消除了 `instanceof` 與強制轉型的壞味道。
Below is a real-world e-commerce payment processing example combining **Sealed Classes**, **Records**, and **Pattern Matching (Java 21+)**. This design guarantees type safety and completely eliminates the code smell of `instanceof` and casting.

```java
import java.math.BigDecimal;
import java.time.Instant;

// 1. 定義封閉的領域事件 (Define closed domain events)
public sealed interface PaymentEvent {
    // 2. 使用 Records 作為具體的事件載體 (Use Records as concrete event carriers)
    record Success(String transactionId, BigDecimal amount, Instant timestamp) implements PaymentEvent {}
    record Failed(String transactionId, ErrorCode reason) implements PaymentEvent {}
    record Pending(String transactionId, int retryCount) implements PaymentEvent {}
}

enum ErrorCode { INSUFFICIENT_FUNDS, TIMEOUT, FRAUD_DETECTED }

public class PaymentProcessor {

    // 3. 現代化的 Pattern Matching 與 Switch 表達式 (Modern Pattern Matching and Switch Expression)
    public String handlePayment(PaymentEvent event) {
        // 注意：這裡沒有 default 分支。如果未來新增了 Refund 事件，編譯器會報錯要求補齊。
        // Note: There is no default branch here. If a 'Refund' event is added later, the compiler will fail and demand implementation.
        return switch (event) {
            
            // Record Pattern Matching (Java 21+): 直接在 case 中解構 Record 欄位
            // Record Pattern Matching (Java 21+): Deconstruct Record fields directly in the case
            case PaymentEvent.Success(var txId, var amount, var time) -> 
                String.format("Payment %s succeeded with amount $%s at %s", txId, amount, time);
                
            // 可以結合 Guard Conditions (when 子句) 進行更細緻的邏輯分派
            // Can combine with Guard Conditions (when clauses) for finer-grained logic dispatch
            case PaymentEvent.Failed(var txId, var reason) when reason == ErrorCode.FRAUD_DETECTED -> {
                alertSecurityTeam(txId);
                yield "Payment " + txId + " blocked due to fraud!"; // 使用 yield 回傳區塊結果
            }
            
            case PaymentEvent.Failed(var txId, var reason) -> 
                "Payment " + txId + " failed. Reason: " + reason;
                
            case PaymentEvent.Pending(var txId, var retries) -> 
                "Payment " + txId + " is pending. Retry count: " + retries;
        };
    }

    private void alertSecurityTeam(String transactionId) {
        // 實作資安通報邏輯 (Implementation for security alert)
        System.err.println("CRITICAL: Fraud detected on tx " + transactionId);
    }
}
```

**案例解析 (Case Analysis):**
1. **強大的領域表達力 (Strong Domain Expressiveness):** 透過 `sealed interface`，我們明確定義了支付事件只有三種可能。
2. **免除樣板程式碼 (Boilerplate-free):** `record` 自動處理了建構子、Getter 與 `toString`，讓開發者專注於資料結構。
3. **編譯期安全 (Compile-time Safety):** `switch` 表達式確保所有狀態都被處理，且透過 Record Patterns (`case Success(var txId, ...)`) 直接解構變數，程式碼極度簡潔且不易出錯。