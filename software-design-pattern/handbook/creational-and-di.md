# 物件建立與依賴管理實戰 / Creational Patterns and Dependency Management

## Mental model｜心智模型

### 1. 分離「組裝」與「使用」 (Separation of Construction and Consumption)
在現代軟體開發中，最核心的心智模型是將 **「如何製造一個物件」** 與 **「如何使用一個物件」** 徹底分開。
想像你正在組裝一台電腦：
- **Consumer (使用者)**：只關心電腦能不能開機、跑程式（使用介面）。
- **Creator (組裝者)**：關心 CPU 插槽是否相容、電源瓦數是否足夠（建立細節）。

如果你的 Business Logic (Consumer) 裡面充滿了 `new DatabaseConnection()`，就像是你在寫程式的時候，還得同時去工廠焊接電路板。這導致了高耦合與難以測試。

### 2. 依賴倒置與接線板 (Dependency Inversion as a Patch Panel)
將系統視為一個巨大的 **接線板 (Patch Panel)**。
- **傳統模式**：模組 A 直接 `new` 模組 B。這就像把兩條電線直接焊死，要換掉 B 就必須破壞 A。
- **DI 模式**：模組 A 宣告「我需要一個符合 B 介面的插頭」。由外部容器（Container）負責在系統啟動時，將 B 的插頭插進 A 的插座。

### 3. 物件生命週期光譜 (Object Lifecycle Spectrum)
不是所有東西都需要 Factory 或 DI。建立物件時，請在心中將其分類：
- **Value Objects / DTOs**：短暫存在，通常用 `new` 或 Builder 建立。
- **Services / Components**：長期存在，通常由 DI Container 管理單例 (Singleton Scope)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 現代化的 Factory 應用 (Modern Factory Usage)
不再盲目建立 `AbstractFactory` 類別，而是傾向輕量級做法：

*   **Static Factory Methods (靜態工廠方法)**：
    取代複雜的 Constructor。例如 `Time.fromTimestamp(ts)` 比 `new Time(ts, true)` 更具語意。
*   **Simple Factory for Polymorphism (多型工廠)**：
    當你需要根據設定檔或輸入參數決定實作時（例如：`PaymentFactory.getProvider('stripe')`），這是封裝 `switch-case` 邏輯的最佳地點。

### 2. Builder Pattern for Immutability (用於不可變物件的 Builder)
在建立複雜的 Configuration 物件或 DTO 時，Constructor 參數過多（Telescoping Constructor Problem）是惡夢。
*   **Fluent Interface**：使用 `User.builder().name("A").age(10).build()`。
*   **Test Data Builders**：在單元測試中，Builder 是神器。它可以提供預設值，讓你只覆蓋測試關心的欄位。

### 3. Dependency Injection (DI) 的黃金標準
*   **Constructor Injection (建構子注入)**：
    **這是最佳實務**。強制依賴關係顯性化。如果一個 Class 的 Constructor 參數超過 5 個，代表它違反了單一職責原則 (SRP)，這是一個極佳的重構訊號。
*   **Composition Root**：
    確保只有一個地方（通常是 `AppMain` 或 `DI Config`）負責組裝所有的物件圖 (Object Graph)。

### 4. Singleton 的現代詮釋
*   **Container-Managed Singleton**：
    不要手寫 `private static instance`。讓 Spring、NestJS 或其他 DI Container 來管理 Scope。這樣在測試時，你可以輕鬆替換成新的 Instance，而不會被全域狀態汙染。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Service Locator Pattern (服務定位器)
這是 DI 的反模式。
*   **Bad**: `ServiceLocator.get('UserService')` 隱藏了依賴關係。使用者必須讀完程式碼才知道它依賴了 UserService。
*   **Good**: 在 Constructor 中宣告 `constructor(private userService: UserService)`。

### 2. The "New" Operator in Business Logic (業務邏輯中的 New)
在 Service 層級的程式碼中直接 `new` 另一個 Service 或外部依賴（如 HTTP Client）。
*   **後果**：無法 Mock 該依賴，單元測試變整合測試，速度變慢且脆弱。

### 3. God Factory / God Builder
試圖用一個 Factory 建立系統中所有類型的物件，或者 Builder 內部包含了過多的預設邏輯驗證。
*   **原則**：Factory 應該只負責「建立」，不該負責「驗證業務規則」。

### 4. Field Injection (欄位注入)
使用 `@Inject` 或 `@Autowired` 直接標註在 private field 上，跳過 Constructor。
*   **陷阱**：這會讓物件在沒有 DI Container 的環境下（如純單元測試）無法被實例化，導致必須依賴反射機制或啟動整個容器才能測試。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 如何選擇建立模式？

1.  **這個物件是 "Data" 還是 "Service"？**
    *   **Data (DTO, Entity)**: 往下看。
    *   **Service (Repository, Manager)**: 使用 **DI (Dependency Injection)**。

2.  **如果是 Data，它的建構過程複雜嗎？**
    *   **簡單 (1-3 個參數)**: 直接使用 `constructor` 或 `static factory method`。
    *   **複雜 (參數多、需驗證、部分可選)**: 使用 **Builder Pattern**。
    *   **需要多型 (回傳介面而非實作)**: 使用 **Factory Method**。

### Code Review Checklist (PR 審查清單)

- [ ] **顯性依賴**：是否所有的 Service 依賴都是透過 Constructor 傳入的？
- [ ] **無隱藏狀態**：是否避免了手寫 `static instance` 的 Singleton？
- [ ] **可測試性**：在單元測試中，是否可以輕鬆 Mock 掉所有外部依賴（DB, API）？
- [ ] **參數數量**：Constructor 的參數是否少於 5 個？（若多於 5 個，是否該拆分 Service 或封裝成 Config Object？）
- [ ] **Factory 職責**：Factory 是否只包含建立邏輯，而沒有混入業務運算邏輯？

---

## Real-world examples｜實戰案例

### Case 1: Test Data Builder (測試資料建構器)
在測試中，我們常需要建立「合法的假資料」。使用 Builder 模式可以避免測試程式碼充滿無意義的參數。

```typescript
// Bad: 測試意圖不明，充滿 magic values
const user = new User("id-123", "John", "Doe", "john@example.com", true, false, "admin");

// Good: 使用 Builder，只關注測試需要的屬性
const user = new UserBuilder()
  .withEmail("john@example.com") // 測試重點
  .asAdmin()                     // 測試重點
  .build();
// 其他欄位由 Builder 填入隨機或預設合法值
```

### Case 2: Strategy Selection via Factory (透過工廠選擇策略)
在支付系統或通知系統中，根據動態參數選擇實作。

```java
// Client Code
public void processOrder(Order order) {
    // Client 不需要知道 Stripe 或 PayPal 的具體建立細節
    PaymentProcessor processor = paymentFactory.getProcessor(order.getPaymentMethod());
    processor.pay(order.getAmount());
}

// Factory Implementation
public class PaymentFactory {
    // 依賴注入所有的策略
    private final Map<String, PaymentProcessor> processors;

    public PaymentProcessor getProcessor(String method) {
        // 封裝選擇邏輯，甚至可以在此處做 Lazy Loading
        return processors.getOrDefault(method, defaultProcessor);
    }
}
```

### Case 3: Proper Dependency Injection (正確的依賴注入)
現代後端框架（如 NestJS, Spring Boot, ASP.NET Core）的標準寫法。

```typescript
// Service 定義 (Consumer)
class OrderService {
    // 明確宣告依賴，不關心 Repository 如何連線 DB
    constructor(
        private readonly repo: OrderRepository,
        private readonly notifier: NotificationService
    ) {}

    async create(order: Order) {
        await this.repo.save(order);
        await this.notifier.send("Order Created");
    }
}

// Composition Root / Module Config (Wiring)
// 這是唯一 "new" 出現的地方，或是由框架自動掃描完成
const repo = new SqlOrderRepository(dbConnection);
const notifier = new EmailNotificationService(smtpConfig);
const service = new OrderService(repo, notifier);
```