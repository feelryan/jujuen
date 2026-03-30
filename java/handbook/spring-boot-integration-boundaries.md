# Java 與 Spring Boot 的整合邊界與決策 / Integration Boundaries and Decisions with Spring Boot

## Mental model｜心智模型

在現代 Java 開發中，Spring Boot 提供了極大的便利性，但過度依賴框架往往會導致系統僵化、測試緩慢以及技術債。身為資深工程師，我們必須建立一個核心的心智模型：**「Spring 是基礎設施（Infrastructure），而純 Java 是核心領域（Core Domain）。」**

In modern Java development, Spring Boot offers immense convenience, but over-reliance on the framework often leads to rigid systems, slow tests, and technical debt. As senior engineers, we must establish a core mental model: **"Spring is the infrastructure, while pure Java is the core domain."**

- **框架作為細節 (Framework as a Detail)**：將 Spring 視為一種「交付機制」與「依賴組裝工具」。你的核心商業邏輯應該是純粹的 Java 類別（POJOs），不依賴任何 `org.springframework.*` 套件。
  **Framework as a Detail**: Treat Spring as a "delivery mechanism" and a "dependency wiring tool." Your core business logic should consist of pure Java classes (POJOs) that do not depend on any `org.springframework.*` packages.
- **控制反轉的真諦 (The True Meaning of IoC)**：IoC 不是指「把所有東西都加上 `@Component`」，而是「將依賴的實例化推遲到系統邊界」。
  **The True Meaning of IoC**: IoC doesn't mean "annotating everything with `@Component`"; it means "pushing the instantiation of dependencies to the boundaries of the system."
- **AOP 是雙面刃 (AOP is a Double-Edged Sword)**：Spring 的 AOP（如 `@Transactional`, `@Async`, `@Cacheable`）非常強大，但它們透過動態代理（Dynamic Proxies）運作，會掩蓋真實的執行流程與效能瓶頸。
  **AOP is a Double-Edged Sword**: Spring's AOP features (like `@Transactional`, `@Async`, `@Cacheable`) are powerful, but they operate via Dynamic Proxies, which can obscure the actual execution flow and performance bottlenecks.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 建構子注入與純 Java 實例化 / Constructor Injection and Pure Java Instantiation
永遠使用建構子注入（Constructor Injection）而非欄位注入（Field Injection，即 `@Autowired` 放在屬性上）。這不僅讓類別在脫離 Spring 容器時依然可用，也強迫你正視依賴過多的問題（Code Smell）。
Always use Constructor Injection instead of Field Injection (`@Autowired` on fields). This not only makes the class usable outside the Spring container but also forces you to confront the code smell of having too many dependencies.

```java
// Good: Pure Java friendly. Can be instantiated with `new OrderService(repo)` in tests.
@Service
public class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

### 2. 領域模型與框架解耦 / Decoupling Domain Models from the Framework
不要在實體（Entities）或領域物件（Domain Objects）中使用 Spring 的依賴注入。如果領域物件需要外部服務來完成計算，請透過方法參數（Method Arguments）傳入，而非將其變成 Spring Bean。
Do not use Spring's dependency injection inside Entities or Domain Objects. If a domain object requires an external service to perform a calculation, pass it via Method Arguments rather than turning the domain object into a Spring Bean.

### 3. 原生 API 與 Spring 封裝的抉擇 / Choosing Between Native APIs and Spring Wrappers
- **非同步處理 (Asynchronous Processing)**：對於簡單的背景任務，可以使用 `@Async`；但對於複雜的非同步流程編排（如多個任務組合、超時處理），請果斷使用 Java 原生的 `CompletableFuture` 與自訂的 `ExecutorService`，這會提供更好的可控性。
  **Asynchronous Processing**: Use `@Async` for simple background fire-and-forget tasks. However, for complex asynchronous orchestration (e.g., combining multiple tasks, timeout handling), decisively use Java's native `CompletableFuture` and custom `ExecutorService` for better control.
- **排程任務 (Scheduling)**：`@Scheduled` 適合單節點的簡單排程。若涉及分散式系統或需要精細的生命週期控制，應考慮使用純 Java 的 `ScheduledExecutorService` 或專業的排程框架（如 Quartz, ShedLock）。
  **Scheduling**: `@Scheduled` is suitable for simple, single-node scheduling. For distributed systems or fine-grained lifecycle control, consider pure Java's `ScheduledExecutorService` or dedicated scheduling frameworks (like Quartz, ShedLock).

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. `@SpringBootTest` 依賴症 / The `@SpringBootTest` Addiction
**現象 / Symptom**：專案中幾乎所有的單元測試都加上了 `@SpringBootTest`，導致測試啟動需要數分鐘，開發者不願意頻繁執行測試。
Almost all unit tests in the project are annotated with `@SpringBootTest`, causing tests to take minutes to start, which discourages developers from running them frequently.
**解法 / Solution**：嚴格區分「單元測試」與「整合測試」。核心邏輯應該完全不需要啟動 Spring Context 即可測試（使用 JUnit + Mockito 或純 Java 實例化）。只有在測試資料庫連線或 HTTP 端點時才使用 Spring 測試切片（如 `@DataJpaTest`, `@WebMvcTest`）。
Strictly separate "Unit Tests" from "Integration Tests". Core logic should be fully testable without starting the Spring Context (using JUnit + Mockito or pure Java instantiation). Only use Spring test slices (like `@DataJpaTest`, `@WebMvcTest`) when testing database connections or HTTP endpoints.

### 2. AOP 內部呼叫失效 / The AOP Self-Invocation Pitfall
**現象 / Symptom**：在同一個類別中，方法 A 呼叫了標註有 `@Transactional` 或 `@Async` 的方法 B，但交易或非同步行為卻沒有生效。
In the same class, Method A calls Method B, which is annotated with `@Transactional` or `@Async`, but the transaction or asynchronous behavior does not take effect.
**原因 / Cause**：Spring AOP 基於代理（Proxy）模式。同類別內的內部呼叫（`this.methodB()`）不會經過代理物件，因此 AOP 攔截器無法介入。
Spring AOP is based on the Proxy pattern. Internal calls within the same class (`this.methodB()`) bypass the proxy object, so the AOP interceptor cannot intervene.
**解法 / Solution**：將需要 AOP 增強的方法抽離到另一個獨立的 Spring Bean 中，或者重新設計架構，避免依賴內部呼叫來觸發 AOP。
Extract the method requiring AOP enhancement into a separate Spring Bean, or redesign the architecture to avoid relying on self-invocation to trigger AOP.

### 3. 萬物皆 Bean / Everything is a Bean
**現象 / Symptom**：將純粹的工具類別（Utility classes）或無狀態的計算邏輯標註為 `@Component`，僅僅為了能被 `@Autowired`。
Annotating pure utility classes or stateless calculation logic with `@Component` just so they can be `@Autowired`.
**解法 / Solution**：如果是純函數（Pure Functions）或無狀態邏輯，直接使用 `static` 方法，或者直接 `new` 出來即可。不要無謂地增加 Spring 容器的負擔與啟動時間。
If it's a pure function or stateless logic, just use `static` methods or simply instantiate it with `new`. Do not unnecessarily increase the burden and startup time of the Spring container.

---

## Checklists & workflows｜檢查清單與流程

在決定一個類別是否應該成為 Spring Bean，或是決定使用純 Java API 還是 Spring 功能時，請使用以下決策流程：
When deciding whether a class should be a Spring Bean, or choosing between pure Java APIs and Spring features, use the following decision workflow:

- [ ] **領域純度檢查 (Domain Purity Check)**：這個類別包含核心商業邏輯嗎？如果是，它是否完全沒有 `import org.springframework.*`？
      Does this class contain core business logic? If yes, is it completely free of `import org.springframework.*`?
- [ ] **測試隔離性 (Test Isolation)**：我可以在不啟動 Spring Context 的情況下，在 10 毫秒內完成這個類別的單元測試嗎？
      Can I unit test this class in under 10 milliseconds without starting the Spring Context?
- [ ] **依賴注入方式 (DI Method)**：我是否使用了 `final` 欄位與建構子注入？有沒有任何 `@Autowired` 出現在欄位上？
      Am I using `final` fields and constructor injection? Are there any `@Autowired` annotations on fields?
- [ ] **AOP 邊界 (AOP Boundaries)**：標註了 `@Transactional` 或 `@Async` 的方法，是否都是由外部類別呼叫的？（檢查是否有 Self-invocation 風險）。
      Are methods annotated with `@Transactional` or `@Async` only called by external classes? (Check for self-invocation risks).
- [ ] **非同步複雜度 (Async Complexity)**：這個非同步任務需要回傳結果、組合其他任務或處理超時嗎？如果是，請放棄 `@Async`，改用 `CompletableFuture`。
      Does this async task need to return a result, combine with other tasks, or handle timeouts? If yes, drop `@Async` and use `CompletableFuture`.

---

## Real-world examples｜實戰案例

### 案例：重構過度耦合的訂單服務 / Refactoring an Over-coupled Order Service

**❌ 反模式：業務邏輯與框架高度耦合 (Anti-pattern: Business logic highly coupled with framework)**

```java
@Service
public class OrderService {
    @Autowired
    private DiscountRepository discountRepo;
    
    // 混合了交易管理、資料庫存取與核心計算邏輯
    // Mixes transaction management, DB access, and core calculation logic
    @Transactional
    public Order createOrder(Cart cart) {
        Order order = new Order();
        double total = 0;
        for (Item item : cart.getItems()) {
            Discount discount = discountRepo.findByItemId(item.getId());
            // 核心商業邏輯被埋在 Spring Service 中
            // Core business logic is buried inside the Spring Service
            if (discount != null && discount.isValid()) {
                total += item.getPrice() * discount.getRate();
            } else {
                total += item.getPrice();
            }
        }
        order.setTotal(total);
        // ... save order
        return order;
    }
}
```

**✅ 最佳實踐：分離純 Java 領域邏輯與 Spring 編排 (Best Practice: Separate pure Java domain logic from Spring orchestration)**

我們將「計算折扣」這個核心邏輯抽離成純 Java 類別，Spring Service 只負責「取得資料」與「協調」。
We extract the core logic of "calculating discounts" into a pure Java class. The Spring Service is only responsible for "fetching data" and "orchestration".

```java
// 1. Pure Java Domain Logic (No Spring dependencies, easily testable)
public class OrderPricingCalculator {
    public static double calculateTotal(Cart cart, Map<String, Discount> discountMap) {
        return cart.getItems().stream()
            .mapToDouble(item -> {
                Discount discount = discountMap.get(item.getId());
                if (discount != null && discount.isValid()) {
                    return item.getPrice() * discount.getRate();
                }
                return item.getPrice();
            }).sum();
    }
}

// 2. Spring Service as an Orchestrator (Thin layer)
@Service
public class OrderService {
    private final DiscountRepository discountRepo;
    private final OrderRepository orderRepo;

    // Constructor Injection
    public OrderService(DiscountRepository discountRepo, OrderRepository orderRepo) {
        this.discountRepo = discountRepo;
        this.orderRepo = orderRepo;
    }

    @Transactional
    public Order createOrder(Cart cart) {
        // Fetch necessary data (Infrastructure)
        List<String> itemIds = cart.getItems().stream().map(Item::getId).toList();
        Map<String, Discount> discountMap = discountRepo.findMapByItemIds(itemIds);

        // Delegate to pure Java domain logic (Core)
        double total = OrderPricingCalculator.calculateTotal(cart, discountMap);

        // Save state (Infrastructure)
        Order order = new Order(cart.getUserId(), total);
        return orderRepo.save(order);
    }
}
```

**架構決策解析 / Architectural Decision Breakdown**：
透過這樣的重構，`OrderPricingCalculator` 可以包含上百行的複雜折扣規則，而它的單元測試只需要 `new` 出物件並傳入 Mock 資料，執行時間不到 1 毫秒。Spring 的 `@Transactional` 邊界被清晰地限制在 `OrderService` 中，完美實現了框架與核心邏輯的整合邊界。
Through this refactoring, `OrderPricingCalculator` can contain hundreds of lines of complex discount rules, and its unit tests only require instantiating objects with `new` and passing mock data, executing in under 1 millisecond. Spring's `@Transactional` boundary is clearly confined to `OrderService`, perfectly realizing the integration boundary between the framework and core logic.