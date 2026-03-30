# 列舉 (Enums) 與常數設計模式 / Enums and Constant Design Patterns

## Mental model｜心智模型

在 Java 中，列舉（Enum）絕對不只是 C/C++ 裡單純的「具名整數（Named Integers）」。**Java 的 Enum 是功能完整的類別（Class），並且是由 JVM 保證執行緒安全的單例物件（Singleton Objects）集合。**
In Java, an Enum is absolutely not just a "named integer" like in C/C++. **Java Enums are fully-fledged classes, and they are a collection of thread-safe singleton objects guaranteed by the JVM.**

將 Enum 想像成一個**「封閉的實例宇宙（Closed universe of instances）」**。當你有一組固定不變的概念（例如：訂單狀態、支付方式、使用者角色）時，Enum 允許你將「狀態（資料）」與「行為（邏輯）」封裝在一起。
Think of an Enum as a **"closed universe of instances."** When you have a fixed set of concepts (e.g., order statuses, payment methods, user roles), Enums allow you to encapsulate both "state (data)" and "behavior (logic)" together.

對於常數管理，心智模型應該從「把所有常數塞進一個大檔案」轉變為「依據業務語意進行強型別分組」。
For constant management, the mental model should shift from "dumping all constants into one giant file" to "grouping them by business semantics with strong typing."

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Enum 實作策略模式 / Strategy Pattern via Enum
與其在外部寫冗長的 `switch-case` 或 `if-else` 來判斷類型並執行對應邏輯，不如讓 Enum 本身攜帶行為。你可以透過定義抽象方法，強制每個 Enum 實例實作自己的邏輯。
Instead of writing lengthy `switch-case` or `if-else` statements externally to evaluate types and execute logic, let the Enum itself carry the behavior. You can define an abstract method to force each Enum instance to implement its own logic.

### 2. 狀態機模式 / State Machine Pattern
訂單或工作流程的狀態轉換非常適合用 Enum 實作。你可以讓每個狀態實例知道自己「允許轉換到哪些下一個狀態」，將防禦性邏輯內聚在 Enum 中。
State transitions for orders or workflows are perfect candidates for Enums. You can make each state instance aware of "which next states it is allowed to transition to," keeping the defensive logic cohesive within the Enum.

### 3. 使用 EnumSet 與 EnumMap / Utilizing EnumSet and EnumMap
當你需要將 Enum 作為集合的元素或 Map 的 Key 時，**永遠優先使用 `EnumSet` 和 `EnumMap`**。它們底層基於位元向量（Bit-vector）與陣列實作，效能遠勝 `HashSet` 與 `HashMap`，且不會產生額外的記憶體開銷。
When you need to use Enums as collection elements or Map keys, **always prefer `EnumSet` and `EnumMap`**. They are backed by bit-vectors and arrays, offering vastly superior performance compared to `HashSet` and `HashMap` without additional memory overhead.

### 4. 帶有屬性的強型別常數 / Strongly-Typed Constants with Properties
不要使用 `public static final String` 來定義錯誤碼或系統代碼。使用 Enum 並賦予它們屬性（如 `code` 和 `message`），這樣能在編譯期就抓出型別錯誤。
Do not use `public static final String` to define error codes or system codes. Use Enums and assign them properties (like `code` and `message`) so type errors can be caught at compile time.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 依賴 `ordinal()` 進行業務邏輯或資料庫映射 / Relying on `ordinal()` for logic or DB mapping
**Pitfall:** `ordinal()` 回傳的是 Enum 宣告的順序（0, 1, 2...）。如果未來有開發者在中間插入了一個新的 Enum 值，所有依賴 `ordinal()` 的資料庫欄位或邏輯都會瞬間崩潰且難以察覺。
**Pitfall:** `ordinal()` returns the declaration order of the Enum (0, 1, 2...). If a developer later inserts a new Enum value in the middle, all database columns or logic relying on `ordinal()` will silently break.
**Fix:** 永遠使用 `name()` 或自訂的 `code` 屬性。在 JPA 中，務必使用 `@Enumerated(EnumType.STRING)`。
**Fix:** Always use `name()` or a custom `code` property. In JPA, always use `@Enumerated(EnumType.STRING)`.

### ❌ 在 Enum 中放置可變狀態 / Mutable state in Enums
**Pitfall:** Enum 是全域單例（Global Singletons）。如果你在 Enum 中定義了非 `final` 的屬性並修改它，會引發嚴重的執行緒安全（Thread-safety）問題。
**Pitfall:** Enums are global singletons. If you define non-`final` fields in an Enum and mutate them, it will cause severe thread-safety issues.
**Fix:** Enum 中的所有屬性都應該宣告為 `final`。
**Fix:** All fields in an Enum must be declared as `final`.

### ❌ 常數介面反模式 / The "Constant Interface" Anti-pattern
**Pitfall:** 建立一個只包含常數的 `interface`，然後讓類別去 `implements` 它，只為了能少打幾個字（直接使用常數名稱）。這會嚴重污染類別的公開 API。
**Pitfall:** Creating an `interface` containing only constants and having classes `implements` it just to save a few keystrokes. This severely pollutes the class's public API.
**Fix:** 使用 `final class` 搭配私有建構子來集中管理常數，並在需要時使用 `import static`。
**Fix:** Use a `final class` with a private constructor to group constants, and use `import static` when needed.

### ❌ 肥大 Enum / Fat Enums
**Pitfall:** 將過多與外部服務整合的邏輯（如呼叫 API、注入 Spring Bean）塞進 Enum 中，導致 Enum 難以單元測試且職責過載。
**Pitfall:** Stuffing too much external integration logic (e.g., calling APIs, injecting Spring Beans) into an Enum, making it hard to unit test and overloading its responsibilities.
**Fix:** Enum 應該只負責純粹的領域邏輯（Pure Domain Logic）。需要外部依賴的邏輯應交給外部的 Service 或 Strategy Factory 處理。
**Fix:** Enums should only handle pure domain logic. Logic requiring external dependencies should be delegated to external Services or Strategy Factories.

---

## Checklists & workflows｜檢查清單與流程

- [ ] **檢查資料庫映射 (Check DB Mapping):** 是否已確認沒有任何 Enum 是透過 `ordinal()` 寫入資料庫或進行序列化的？
- [ ] **檢查不可變性 (Check Immutability):** Enum 內部的所有成員變數（Fields）是否都已經標記為 `final`？
- [ ] **評估策略模式 (Evaluate Strategy Pattern):** 專案中是否有一長串針對特定狀態的 `switch-case`？是否能將這些邏輯重構為 Enum 內部的多型方法？
- [ ] **檢查集合型別 (Check Collection Types):** 當儲存 Enum 集合時，是否已經將 `HashSet<MyEnum>` 替換為 `EnumSet.noneOf(MyEnum.class)`？
- [ ] **消除常數介面 (Eliminate Constant Interfaces):** 是否移除了所有只包含常數的 `interface`，並改用 `final class` 或 Enum 替代？

---

## Real-world examples｜實戰案例

### 案例 1：利用 Enum 實作折扣策略 (Discount Strategy via Enum)
將計算邏輯直接綁定在 Enum 上，避免在 Service 層寫出巨大的 `if-else`。
Binding calculation logic directly to the Enum avoids giant `if-else` blocks in the Service layer.

```java
public enum DiscountPolicy {
    NO_DISCOUNT("No Discount") {
        @Override
        public BigDecimal applyDiscount(BigDecimal amount) {
            return amount;
        }
    },
    TEN_PERCENT_OFF("10% Off") {
        @Override
        public BigDecimal applyDiscount(BigDecimal amount) {
            // amount * 0.9
            return amount.multiply(BigDecimal.valueOf(0.9)); 
        }
    },
    FIXED_MINUS_FIFTY("Minus $50") {
        @Override
        public BigDecimal applyDiscount(BigDecimal amount) {
            BigDecimal discounted = amount.subtract(BigDecimal.valueOf(50));
            return discounted.compareTo(BigDecimal.ZERO) > 0 ? discounted : BigDecimal.ZERO;
        }
    };

    // 1. Immutable property / 不可變屬性
    private final String description;

    DiscountPolicy(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    // 2. Abstract method for strategy / 策略模式的抽象方法
    public abstract BigDecimal applyDiscount(BigDecimal amount);
}

// Usage / 使用方式:
// BigDecimal finalPrice = DiscountPolicy.TEN_PERCENT_OFF.applyDiscount(originalPrice);
```

### 案例 2：安全的訂單狀態機 (Safe Order State Machine)
在 Enum 內部定義狀態的合法轉換路徑，防止出現「已取消的訂單變成已出貨」這種不合理的業務臭蟲。
Define valid transition paths within the Enum to prevent illogical business bugs like "a canceled order becoming shipped."

```java
import java.util.EnumSet;
import java.util.Set;

public enum OrderStatus {
    CREATED,
    PAID,
    SHIPPED,
    DELIVERED,
    CANCELLED;

    // 定義每個狀態允許的「下一個合法狀態」
    // Define the allowed "next valid states" for each state
    private Set<OrderStatus> validNextStates;

    // 靜態初始化區塊，用來設定狀態機規則 (避免 forward-reference 問題)
    // Static block to setup state machine rules (avoids forward-reference issues)
    static {
        CREATED.validNextStates = EnumSet.of(PAID, CANCELLED);
        PAID.validNextStates = EnumSet.of(SHIPPED, CANCELLED);
        SHIPPED.validNextStates = EnumSet.of(DELIVERED);
        DELIVERED.validNextStates = EnumSet.noneOf(OrderStatus.class); // 終點狀態 / End state
        CANCELLED.validNextStates = EnumSet.noneOf(OrderStatus.class); // 終點狀態 / End state
    }

    /**
     * 檢查是否可以轉換到目標狀態
     * Check if transition to target state is allowed
     */
    public boolean canTransitionTo(OrderStatus nextState) {
        return this.validNextStates.contains(nextState);
    }
}

// Usage / 使用方式:
// if (!currentStatus.canTransitionTo(newStatus)) {
//     throw new IllegalStateException("Invalid state transition from " + currentStatus + " to " + newStatus);
// }
```

### 案例 3：取代常數介面 (Replacing Constant Interfaces)
如果常數沒有關聯的行為，只是單純的系統設定值，請使用帶有私有建構子的 `final class`。
If constants have no associated behavior and are just system settings, use a `final class` with a private constructor.

```java
// ❌ Anti-pattern: Constant Interface
public interface SecurityConstants {
    String TOKEN_PREFIX = "Bearer ";
    int MAX_RETRY = 3;
}

// ✅ Best Practice: Utility Class for Constants
public final class SecurityConstants {
    
    // Prevent instantiation / 防止被實例化
    private SecurityConstants() {
        throw new AssertionError("Utility class should not be instantiated");
    }

    public static final String TOKEN_PREFIX = "Bearer ";
    public static final int MAX_RETRY = 3;
}
```