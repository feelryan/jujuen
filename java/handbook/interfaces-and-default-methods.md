# 介面演進與預設方法 (Default Methods) / Interface Evolution and Default Methods

## Mental model｜心智模型

在 Java 8 之前，介面（Interface）是 100% 純粹的契約（Contract），不包含任何實作細節。這導致了一個嚴重的問題：**一旦介面被發布並被廣泛實作，你就再也無法在不破壞現有程式碼的情況下為其新增方法。**

Before Java 8, interfaces were 100% pure contracts with no implementation details. This led to a severe problem: **once an interface was published and widely implemented, you could never add new methods to it without breaking existing code.**

預設方法（Default Methods）的引入改變了這個心智模型。現在的介面更像是 Scala 中的**特徵（Traits）**或**混入（Mixins）**。它們不僅定義了「必須做什麼」（抽象方法），還能提供「如果沒有特別指定，預設該怎麼做」（預設方法）。

The introduction of Default Methods shifted this mental model. Modern Java interfaces act more like **Traits** or **Mixins** in Scala. They not only define "what must be done" (abstract methods) but also provide a fallback on "how to do it if not explicitly specified" (default methods).

**核心觀念 / Core Concepts:**
1. **向後相容性防護網 (Backward Compatibility Safety Net):** 預設方法的主要存在意義是「API 演進」。它允許框架作者在不破壞舊有客戶端的前提下，為介面擴充新功能。
   The primary purpose of default methods is "API evolution". It allows framework authors to extend interfaces with new features without breaking legacy clients.
2. **無狀態行為 (Stateless Behavior):** 介面仍然不能擁有實例狀態（Instance fields）。預設方法只能依賴介面中定義的其他方法來完成邏輯。
   Interfaces still cannot hold instance state (fields). Default methods must rely solely on other methods defined within the interface to execute their logic.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 增量 API 演進 / Incremental API Evolution
當你需要為一個已經被外部系統廣泛實作的介面新增功能時，使用 `default` 方法提供一個合理的預設行為或空操作（No-op）。
When you need to add functionality to an interface widely implemented by external systems, use `default` methods to provide a reasonable fallback or a No-op.

```java
public interface PaymentProcessor {
    void processPayment(Order order);
    
    // 新增的方法：提供預設實作以避免破壞舊的實作類別
    // New method: Provide a default implementation to avoid breaking legacy classes
    default void refundPayment(Order order) {
        throw new UnsupportedOperationException("Refund not supported by this processor yet.");
    }
}
```

### 2. 替代骨架抽象類別 / Replacing Skeletal Abstract Classes
過去我們常使用「介面 + 抽象類別」（例如 `List` 與 `AbstractList`）來提供預設實作。現在，對於無狀態的預設邏輯，你可以直接寫在介面中，釋放寶貴的單一繼承空間。
Historically, we used the "Interface + Abstract Class" pattern (e.g., `List` and `AbstractList`) to provide default implementations. Now, for stateless default logic, you can put it directly in the interface, freeing up the precious single inheritance slot.

### 3. 特徵混入 (Trait Mixins) / Trait Mixins
透過介面將正交的功能（Orthogonal capabilities）「混入」到類別中，例如 `Loggable` 或 `Auditable`。
Use interfaces to "mix in" orthogonal capabilities into classes, such as `Loggable` or `Auditable`.

```java
public interface Loggable {
    // Java 9+ 支援 private 方法，適合用於重用介面內部邏輯
    // Java 9+ supports private methods, perfect for reusing internal interface logic
    private org.slf4j.Logger getLogger() {
        return org.slf4j.LoggerFactory.getLogger(this.getClass());
    }

    default void logInfo(String message) {
        getLogger().info(message);
    }
}

// 任何類別只要實作 Loggable 就能直接使用 logInfo
// Any class implementing Loggable can use logInfo directly
public class OrderService implements Loggable { ... }
```

### 4. 介面級別的工具方法 / Interface-scoped Utilities
不再需要建立 `Collections` 這種純粹為了存放靜態方法的工具類別（Utility Classes）。直接將相關的 `static` 方法放在介面中，提高內聚性。
There is no longer a need to create Utility Classes like `Collections` just to hold static methods. Place related `static` methods directly inside the interface to improve cohesion.

```java
public interface Validator {
    boolean validate(String input);

    // 靜態工廠方法直接放在介面中
    // Static factory methods placed directly in the interface
    static Validator notNull() {
        return input -> input != null;
    }
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 試圖覆寫 Object 的方法 / Attempting to Override Object Methods
**❌ 錯誤 (Pitfall):** 嘗試在介面中使用 `default` 方法來覆寫 `equals`, `hashCode`, 或 `toString`。Java 編譯器會直接報錯。
**❌ Pitfall:** Attempting to use `default` methods to override `equals`, `hashCode`, or `toString`. The Java compiler will reject this.
**💡 原因 (Reason):** 類別的繼承層級永遠優先於介面。任何類別都繼承自 `Object`，因此 `Object` 的方法實作永遠會贏過介面的預設方法。允許介面覆寫它們會造成嚴重的邏輯混亂。
**💡 Reason:** Class inheritance always wins over interface inheritance. Every class inherits from `Object`, so `Object`'s implementations would always win anyway. Allowing interfaces to override them would cause severe logical confusion.

### 2. 菱形繼承問題 (The Diamond Problem) / The Diamond Problem
**❌ 錯誤 (Pitfall):** 實作了多個介面，而這些介面提供了簽名相同但實作不同的預設方法，導致編譯失敗。
**❌ Pitfall:** Implementing multiple interfaces that provide default methods with the exact same signature but different implementations, causing a compilation error.

```java
interface A { default void doWork() { System.out.println("A"); } }
interface B { default void doWork() { System.out.println("B"); } }

// 編譯錯誤：class C inherits unrelated defaults for doWork() from types A and B
public class C implements A, B { 
    // 必須手動解決衝突 / Must resolve the conflict manually
    @Override
    public void doWork() {
        A.super.doWork(); // 顯式指定呼叫 A 的預設方法 / Explicitly call A's default method
    }
}
```

### 3. 濫用預設方法取代抽象類別 / Overusing Default Methods over Abstract Classes
**❌ 錯誤 (Pitfall):** 忘記介面不能擁有狀態（Fields），為了把所有邏輯塞進介面，寫出極度複雜且效能低下的預設方法。
**❌ Pitfall:** Forgetting that interfaces cannot hold state (fields). To cram all logic into an interface, developers might write overly complex and inefficient default methods.
**💡 解決方案 (Solution):** 如果多個實作類別需要共享「狀態（成員變數）」或「生命週期」，**請乖乖使用抽象類別 (Abstract Class)**。預設方法只適合「無狀態」的行為。
**💡 Solution:** If multiple implementations need to share "state (fields)" or "lifecycle", **stick to Abstract Classes**. Default methods are only suitable for "stateless" behaviors.

---

## Checklists & workflows｜檢查清單與流程

當你考慮在介面中加入 `default` 或 `static` 方法時，請通過以下決策樹：
When considering adding a `default` or `static` method to an interface, run through this decision tree:

- [ ] **這是一個已經發布且被外部使用的 API 嗎？ (Is this a published API used externally?)**
  - 是的 $\rightarrow$ 必須使用 `default` 方法來保證向後相容性。 (Yes $\rightarrow$ Must use `default` to guarantee backward compatibility.)
  - 不是（僅內部專案使用） $\rightarrow$ 考慮直接新增抽象方法，並利用 IDE 重構工具更新所有實作，這能確保每個實作都經過明確的思考。 (No $\rightarrow$ Consider adding a standard abstract method and updating all implementations via IDE to ensure explicit handling.)
- [ ] **這個行為需要依賴實例變數（State）嗎？ (Does this behavior rely on instance state?)**
  - 是的 $\rightarrow$ 介面無法滿足需求，應該使用 `Abstract Class`。 (Yes $\rightarrow$ Interfaces cannot fulfill this; use an `Abstract Class`.)
  - 不是 $\rightarrow$ 可以使用 `default` 方法。 (No $\rightarrow$ Safe to use a `default` method.)
- [ ] **這是一個與特定實例無關的通用輔助邏輯嗎？ (Is this a general utility logic independent of specific instances?)**
  - 是的 $\rightarrow$ 使用 `static` 介面方法。 (Yes $\rightarrow$ Use a `static` interface method.)
- [ ] **預設方法中的邏輯是否過於龐大？ (Is the logic inside the default method too large?)**
  - 是的 $\rightarrow$ 使用 Java 9+ 的 `private` 介面方法將邏輯拆解，避免污染公開 API。 (Yes $\rightarrow$ Use Java 9+ `private` interface methods to break down the logic and avoid polluting the public API.)

---

## Real-world examples｜實戰案例

### 案例：演進一個外掛系統架構 (Evolving a Plugin System Architecture)

假設你維護一個電商平台的 SDK，其中有一個 `DiscountStrategy` 介面。在 v1.0 時，它只有一個計算折扣的方法。
Assume you maintain an e-commerce SDK with a `DiscountStrategy` interface. In v1.0, it only had one method for calculating discounts.

**v1.0 SDK**
```java
public interface DiscountStrategy {
    BigDecimal calculateDiscount(Order order);
}
```

在 v2.0 中，業務需求改變，我們需要知道這個折扣策略是否可以與其他折扣「疊加 (Stackable)」。如果我們直接新增 `boolean isStackable();`，所有使用 v1.0 SDK 的第三方外掛都會在升級時崩潰（`NoSuchMethodError` 或編譯失敗）。
In v2.0, business requirements change. We need to know if this discount strategy is "Stackable" with others. If we simply add `boolean isStackable();`, all third-party plugins using v1.0 SDK will break upon upgrading (`NoSuchMethodError` or compilation failure).

**v2.0 SDK (使用 Default Methods 安全演進 / Safe Evolution with Default Methods)**
```java
public interface DiscountStrategy {
    
    // 原有契約保持不變
    // Original contract remains unchanged
    BigDecimal calculateDiscount(Order order);

    // 新增預設方法：預設所有舊的折扣策略都「不可疊加」，保護業務邏輯與系統穩定
    // New default method: Default all legacy strategies to "not stackable", protecting business logic and system stability
    default boolean isStackable() {
        return false;
    }
    
    // 新增靜態工廠方法：提供開箱即用的標準實作
    // New static factory method: Provide out-of-the-box standard implementations
    static DiscountStrategy noDiscount() {
        return order -> BigDecimal.ZERO;
    }
}
```

**為什麼這樣設計很好？ (Why is this a good design?)**
1. **零破壞 (Zero Breakage):** 第三方開發者升級到 v2.0 SDK 時，不需要修改任何一行程式碼。
2. **安全的業務預設值 (Safe Business Defaults):** 將 `isStackable` 預設為 `false` 是最保守且安全的做法，避免舊外掛意外造成公司財務損失（折扣無限疊加）。
3. **高內聚 (High Cohesion):** `noDiscount()` 靜態方法直接放在介面中，開發者輸入 `DiscountStrategy.` 時，IDE 的自動補全會直接提示這個標準實作，開發體驗極佳。