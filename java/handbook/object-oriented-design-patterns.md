# Java 物件導向與常見設計模式 / OOP and Common Design Patterns in Java

## Mental model｜心智模型

設計模式是開發者之間溝通的「共用語彙」，而非必須死守的「教條」。在真實專案中，模式的價值在於**控制複雜度**與**隔離變動**。
Design patterns are a "shared vocabulary" among developers, not a strict "dogma" to be blindly followed. In real-world projects, the value of patterns lies in **controlling complexity** and **isolating changes**.

隨著現代 Java（如 Lambdas, Records, 介面預設方法）的演進，傳統 GoF (Gang of Four) 模式的實作方式已經發生了巨大的變化。我們不再需要為了套用模式而建立大量冗餘的類別；相反地，我們應該利用 Java 的現代特性，以更輕量、函數式的方式來達成相同的設計目標。
With the evolution of modern Java (e.g., Lambdas, Records, Interface Default Methods), the implementation of traditional GoF patterns has changed drastically. We no longer need to create massive boilerplate classes just to apply a pattern; instead, we should leverage modern Java features to achieve the same design goals in a lighter, more functional way.

**核心思維 / Core Mindset：**
1. **組合優於繼承 / Composition over Inheritance:** 盡量使用介面與委派，避免過深的類別繼承樹。 / Favor interfaces and delegation, avoid deep class inheritance trees.
2. **現代化簡化 / Modern Simplification:** 能用 Lambda 或 Record 解決的，就不要寫完整的 Strategy 或 Builder 類別。 / If it can be solved with a Lambda or Record, don't write a full Strategy or Builder class.
3. **框架代勞 / Framework Delegation:** 在 Spring 等框架中，Singleton 和 Factory 通常由 IoC 容器接管，無需手動實作。 / In frameworks like Spring, Singletons and Factories are usually managed by the IoC container, eliminating the need for manual implementation.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Builder Pattern (建造者模式)
**情境 / Scenario:** 當物件有超過 4 個以上的屬性，且部分為選填，或是需要建立不可變 (Immutable) 物件時。 / When an object has more than 4 properties, some of which are optional, or when creating immutable objects.
*   **Best Practice:** 使用靜態內部類別 (Static Inner Class) 實作，或直接使用 Lombok 的 `@Builder` 標註。在現代 Java 中，如果只是單純的資料載體，請優先考慮 `Record` 搭配精簡的建構子。
*   **Best Practice:** Implement using a Static Inner Class, or simply use Lombok's `@Builder` annotation. In modern Java, if it's just a data carrier, prioritize `Record` with compact constructors.

### 2. Factory Pattern (工廠模式)
**情境 / Scenario:** 需要將「物件建立的邏輯」與「物件使用的邏輯」解耦時。 / When you need to decouple "object creation logic" from "object usage logic".
*   **Best Practice:** 利用 Java 8+ 的介面靜態方法 (Interface Static Methods) 作為簡單工廠。對於動態建立，可以使用 `Supplier<T>` 函數式介面來取代傳統的 Factory 介面。
*   **Best Practice:** Use Java 8+ Interface Static Methods as a simple factory. For dynamic creation, use the `Supplier<T>` functional interface instead of traditional Factory interfaces.

### 3. Singleton Pattern (單例模式)
**情境 / Scenario:** 確保系統中某個類別只有一個實例（例如全域配置管理）。 / Ensuring only one instance of a class exists in the system (e.g., global configuration manager).
*   **Best Practice:** 除非你在寫底層函式庫，否則**交給 Spring IoC (`@Component`) 管理**。若必須手動實作，**使用 Enum 實作單例** 是最安全且防禦反射攻擊 (Reflection attacks) 與序列化問題的最佳解。
*   **Best Practice:** Unless you are writing a low-level library, **let Spring IoC (`@Component`) manage it**. If manual implementation is required, **using an Enum for Singleton** is the safest approach, protecting against reflection attacks and serialization issues.

### 4. Strategy Pattern (策略模式)
**情境 / Scenario:** 演算法或業務邏輯需要在執行時期動態切換。 / When algorithms or business logic need to be dynamically switched at runtime.
*   **Best Practice:** 捨棄建立多個實體策略類別，改用 `Enum` 結合 Lambda 運算式，或者直接傳遞 `Function<T, R>` 等函數式介面。
*   **Best Practice:** Discard creating multiple concrete strategy classes; instead, use `Enum` combined with Lambda expressions, or directly pass functional interfaces like `Function<T, R>`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **Patternitis (模式病 / 過度設計)**
  - **Pitfall:** 為了預防「未來可能發生的變化」，在簡單的 CRUD 系統中套用 Abstract Factory 或 Visitor 模式，導致程式碼難以追蹤。
  - **Pitfall:** Applying Abstract Factory or Visitor patterns in a simple CRUD system to prevent "potential future changes", making the code extremely hard to trace.
  - **Solution:** 遵循 YAGNI (You Aren't Gonna Need It) 原則。先寫出乾淨的直白程式碼，直到重構時發現痛點再引入模式。 / Follow the YAGNI principle. Write clean, straightforward code first, and introduce patterns only when pain points arise during refactoring.

- **Flawed Double-Checked Locking (有缺陷的雙重檢查鎖定)**
  - **Pitfall:** 手寫 Singleton 時，使用了 Double-Checked Locking 但忘記加上 `volatile` 關鍵字，導致多執行緒環境下指令重排 (Instruction Reordering) 產生半初始化物件。
  - **Pitfall:** When hand-coding a Singleton, using Double-Checked Locking but forgetting the `volatile` keyword, leading to partially initialized objects due to instruction reordering in multithreaded environments.
  - **Solution:** 改用 Enum Singleton 或 Initialization-on-demand holder idiom (靜態內部類別法)。 / Switch to Enum Singleton or the Initialization-on-demand holder idiom.

- **God Builder (上帝建造者)**
  - **Pitfall:** Builder 模式中包含了 30~50 個欄位。這通常意味著你的領域模型 (Domain Model) 缺乏內聚性，沒有將相關屬性分組。
  - **Pitfall:** A Builder pattern containing 30~50 fields. This usually indicates a lack of cohesion in your Domain Model, failing to group related attributes.
  - **Solution:** 將大物件拆分為多個小物件（例如將地址相關欄位抽取為 `Address` 物件），並在 Builder 中組合它們。 / Break the large object into smaller ones (e.g., extract address-related fields into an `Address` object) and compose them in the Builder.

---

## Checklists & workflows｜檢查清單與流程

### Object Creation Decision Tree｜物件建立決策樹
- [ ] 屬性數量 <= 3 且無複雜邏輯？ -> **直接使用 Constructor 或 Record**。 / Properties <= 3 and no complex logic? -> **Use Constructor or Record directly**.
- [ ] 屬性數量 > 4，且有選填項目或需保證不可變性 (Immutability)？ -> **使用 Builder 模式**。 / Properties > 4, with optional fields or requiring immutability? -> **Use Builder pattern**.
- [ ] 需要根據條件回傳不同的子類別實作？ -> **使用 Factory 模式 (或 Interface Static Method)**。 / Need to return different subclass implementations based on conditions? -> **Use Factory pattern (or Interface Static Method)**.
- [ ] 這個物件是無狀態的 (Stateless) 服務類別？ -> **交給 DI 框架 (如 Spring) 作為 Singleton 管理**。 / Is this object a stateless service class? -> **Let a DI framework (like Spring) manage it as a Singleton**.

### Code Review Checklist｜程式碼審查清單
- [ ] **Strategy:** 是否為了極簡單的邏輯建立了過多類別？能否用 Lambda 或 Enum 簡化？ / Did we create too many classes for extremely simple logic? Can it be simplified with Lambdas or Enums?
- [ ] **Builder:** Builder 產出的物件是否為 `final` 且欄位不可變？ / Is the object produced by the Builder `final` and are its fields immutable?
- [ ] **Factory:** 工廠方法的回傳型別是否依賴於抽象介面，而非具體實作？ / Does the factory method return type depend on an abstract interface rather than a concrete implementation?

---

## Real-world examples｜實戰案例

### 1. Modern Builder (現代建造者模式 - Immutable & Safe)
在不依賴 Lombok 的情況下，標準且安全的 Builder 實作方式。確保物件一旦建立即不可變。
A standard and safe Builder implementation without relying on Lombok. Ensures the object is immutable once created.

```java
public final class HttpClientConfig {
    private final String url;          // Required
    private final int timeoutMillis;   // Optional, default 5000
    private final boolean followRedirects; // Optional, default true

    // Private constructor to enforce Builder usage
    private HttpClientConfig(Builder builder) {
        this.url = builder.url;
        this.timeoutMillis = builder.timeoutMillis;
        this.followRedirects = builder.followRedirects;
    }

    // Getters only, no Setters (Immutability)
    public String getUrl() { return url; }
    public int getTimeoutMillis() { return timeoutMillis; }
    public boolean isFollowRedirects() { return followRedirects; }

    public static class Builder {
        private final String url; // Required field in Builder constructor
        private int timeoutMillis = 5000;
        private boolean followRedirects = true;

        public Builder(String url) {
            if (url == null || url.isBlank()) {
                throw new IllegalArgumentException("URL cannot be null or blank");
            }
            this.url = url;
        }

        public Builder timeoutMillis(int timeoutMillis) {
            this.timeoutMillis = timeoutMillis;
            return this;
        }

        public Builder followRedirects(boolean followRedirects) {
            this.followRedirects = followRedirects;
            return this;
        }

        public HttpClientConfig build() {
            return new HttpClientConfig(this);
        }
    }
}

// Usage:
// HttpClientConfig config = new HttpClientConfig.Builder("https://api.example.com")
//                              .timeoutMillis(3000)
//                              .build();
```

### 2. Enum-based Strategy Pattern (基於 Enum 的現代策略模式)
傳統的策略模式需要一個介面和多個實作類別。在現代 Java 中，如果策略邏輯不複雜且不需要注入外部依賴，使用 Enum 結合 Lambda 介面是最優雅的做法。
The traditional Strategy pattern requires an interface and multiple implementation classes. In modern Java, if the strategy logic is not complex and doesn't require injecting external dependencies, using an Enum combined with Lambda interfaces is the most elegant approach.

```java
import java.math.BigDecimal;
import java.util.function.BiFunction;

public enum DiscountStrategy {
    // 1. Define strategies using Lambda expressions / 使用 Lambda 定義策略
    NONE((price, qty) -> price.multiply(BigDecimal.valueOf(qty))),
    
    BULK_DISCOUNT((price, qty) -> {
        BigDecimal total = price.multiply(BigDecimal.valueOf(qty));
        // 10% off for 10 or more items / 滿10件打9折
        return qty >= 10 ? total.multiply(new BigDecimal("0.9")) : total;
    }),
    
    VIP_DISCOUNT((price, qty) -> {
        BigDecimal total = price.multiply(BigDecimal.valueOf(qty));
        // Flat 20% off for VIPs / VIP無條件8折
        return total.multiply(new BigDecimal("0.8"));
    });

    // 2. Functional interface to hold the behavior / 儲存行為的函數式介面
    private final BiFunction<BigDecimal, Integer, BigDecimal> calculator;

    DiscountStrategy(BiFunction<BigDecimal, Integer, BigDecimal> calculator) {
        this.calculator = calculator;
    }

    // 3. Execution method / 執行方法
    public BigDecimal calculateTotal(BigDecimal price, int quantity) {
        return calculator.apply(price, quantity);
    }
}

// Usage:
// BigDecimal total = DiscountStrategy.BULK_DISCOUNT.calculateTotal(new BigDecimal("100"), 12);
```

### 3. Interface Static Factory (介面靜態工廠)
隱藏實作細節，直接透過介面提供建立物件的入口。
Hiding implementation details and providing an entry point for object creation directly through the interface.

```java
public interface NotificationSender {
    void send(String message, String recipient);

    // Static factory method / 靜態工廠方法
    static NotificationSender create(String type) {
        return switch (type.toLowerCase()) {
            case "email" -> new EmailSender();
            case "sms" -> new SmsSender();
            default -> throw new IllegalArgumentException("Unknown type: " + type);
        };
    }
}

// Concrete implementations are package-private (hidden) 
// 具體實作設為 package-private (隱藏細節)
class EmailSender implements NotificationSender {
    @Override
    public void send(String message, String recipient) { /* ... */ }
}

class SmsSender implements NotificationSender {
    @Override
    public void send(String message, String recipient) { /* ... */ }
}

// Usage:
// NotificationSender sender = NotificationSender.create("email");
// sender.send("Hello", "user@example.com");
```