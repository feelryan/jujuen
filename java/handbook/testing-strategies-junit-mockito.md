# 測試策略：JUnit 5 與 Mockito 實戰 / Testing Strategies: JUnit 5 and Mockito

## Mental model｜心智模型

在現代 Java 開發中，測試不再只是「確保程式碼能跑」，而是**「可執行的規格書（Executable Specifications）」**與**「重構的安全網（Safety Net for Refactoring）」**。
In modern Java development, testing is no longer just "making sure the code runs." It serves as **Executable Specifications** and a **Safety Net for Refactoring**.

要建立高可維護的測試，我們需要建立以下心智模型：
To build highly maintainable tests, we need to adopt the following mental models:

1. **邊界隔離（Boundary Isolation）**：
   單元測試的核心在於「隔離」。你的業務邏輯不應該依賴外部系統的狀態。Mockito 就像是手術刀，用來切斷你的類別與外部依賴（如資料庫、API、檔案系統）的連結，讓你專注驗證核心邏輯。
   The core of unit testing is "isolation." Your business logic shouldn't depend on the state of external systems. Mockito acts as a scalpel, cutting the ties between your class and external dependencies (DB, APIs, File System), allowing you to focus purely on core logic.

2. **真實環境模擬（Simulating Reality）**：
   當進入整合測試時，過去我們常依賴 H2 等記憶體資料庫，但這會導致「測試環境與生產環境不一致」的假象。Testcontainers 改變了遊戲規則，它允許我們在測試期間啟動真實的 Docker 容器（如 PostgreSQL, Redis），確保測試的真實性。
   When moving to integration testing, we historically relied on in-memory DBs like H2, which created a false sense of security due to "environment mismatch." Testcontainers changed the game by allowing us to spin up real Docker containers (e.g., PostgreSQL, Redis) during tests, ensuring absolute fidelity.

3. **測試金字塔的演進（Evolution of the Test Pyramid）**：
   現代微服務架構中，單純的單元測試是不夠的。我們更傾向於「鑽石型」或「蜂巢型」測試策略：適量的單元測試（邏輯複雜處）、大量的整合測試（組件之間的互動），以及少量的端到端測試。
   In modern microservices, pure unit tests aren't enough. We lean towards a "Diamond" or "Honeycomb" testing strategy: a moderate amount of unit tests (for complex logic), a heavy emphasis on integration tests (component interactions), and a few End-to-End tests.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Arrange-Act-Assert (AAA) / Given-When-Then
保持測試結構清晰是可讀性的關鍵。永遠將測試分為三個明顯的區塊，並用空白行隔開。
Keeping the test structure clear is key to readability. Always divide your tests into three distinct blocks, separated by blank lines.

```java
@Test
void should_CalculateDiscount_When_UserIsPremium() {
    // Arrange (Given): Setup mocks and test data
    User user = new User("PREMIUM");
    Cart cart = new Cart(100.0);
    when(discountPolicy.getRate(user)).thenReturn(0.2);

    // Act (When): Call the method under test
    double finalPrice = checkoutService.calculate(user, cart);

    // Assert (Then): Verify the result and side effects
    assertEquals(80.0, finalPrice);
    verify(metricsLogger).logCheckout(user);
}
```

### 2. Contextual Grouping with `@Nested` / 使用 `@Nested` 進行上下文分組
當一個類別有多種狀態或情境時，使用 JUnit 5 的 `@Nested` 可以將測試組織得像樹狀結構，極大地提升測試報告的可讀性。
When a class has multiple states or scenarios, use JUnit 5's `@Nested` to organize tests into a tree-like structure, drastically improving the readability of test reports.

```java
class OrderServiceTest {
    @Nested
    class WhenOrderIsValid {
        @Test void should_ProcessPayment() { ... }
        @Test void should_DeductInventory() { ... }
    }

    @Nested
    class WhenInventoryIsInsufficient {
        @Test void should_ThrowException() { ... }
        @Test void should_NotProcessPayment() { ... }
    }
}
```

### 3. Data-Driven Testing with `@ParameterizedTest` / 參數化測試
避免為了不同的輸入值寫一堆重複的測試。使用 `@ParameterizedTest` 結合 `@CsvSource` 或 `@MethodSource`。
Avoid writing duplicate tests just for different input values. Use `@ParameterizedTest` combined with `@CsvSource` or `@MethodSource`.

```java
@ParameterizedTest
@CsvSource({
    "100, 0.1, 90",
    "200, 0.2, 160",
    "50,  0.0, 50"
})
void should_ApplyDiscountCorrectly(double price, double discount, double expected) {
    assertEquals(expected, calculator.apply(price, discount));
}
```

### 4. The Singleton Testcontainer Pattern / 單例測試容器模式
啟動 Testcontainers 很耗時。不要在每個測試類別中啟動/關閉容器，而是使用一個靜態的共用容器，讓整個測試套件共用，大幅縮短 CI 執行時間。
Starting Testcontainers is slow. Don't start/stop containers for every test class. Instead, use a static shared container for the entire test suite to drastically reduce CI execution time.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- ❌ **Mocking Value Objects or Data Structures (過度 Mock 資料物件)**
  - **Pitfall:** 使用 `mock(User.class)` 或 `mock(List.class)`。這會讓測試變得脆弱且難以理解。
  - **Solution:** 直接使用 `new User()` 實例化資料物件。只 Mock 具有行為的依賴（如 Service, Repository, Client）。
  - **Pitfall:** Using `mock(User.class)` or `mock(List.class)`. This makes tests fragile and hard to understand.
  - **Solution:** Instantiate data objects directly using `new User()`. Only mock dependencies with behavior (e.g., Services, Repositories, Clients).

- ❌ **Testing Implementation Details (測試實作細節)**
  - **Pitfall:** 大量使用 `verify()` 檢查內部私有方法的呼叫順序，導致只要稍微重構程式碼，測試就壞掉（Fragile Tests）。
  - **Solution:** 測試「行為與結果（狀態改變或回傳值）」，而不是「怎麼實作的」。`verify()` 應該保留給會產生外部副作用的操作（如發送 Email、呼叫外部 API）。
  - **Pitfall:** Heavily using `verify()` to check the exact order of internal method calls, causing tests to break on minor refactoring (Fragile Tests).
  - **Solution:** Test "behavior and outcomes (state changes or return values)", not "how it's implemented". Reserve `verify()` for external side effects (e.g., sending an email, calling an external API).

- ❌ **Ignoring Time and Randomness (忽略時間與隨機性)**
  - **Pitfall:** 在業務邏輯中直接呼叫 `LocalDateTime.now()`，導致測試在跨日或特定時間點失敗。
  - **Solution:** 注入 `java.time.Clock`。在測試中傳入 `Clock.fixed(...)` 來凍結時間。
  - **Pitfall:** Calling `LocalDateTime.now()` directly in business logic, causing tests to fail at midnight or specific times.
  - **Solution:** Inject `java.time.Clock`. Pass `Clock.fixed(...)` in tests to freeze time.

- ❌ **Using H2 for Integration Tests (使用 H2 進行整合測試)**
  - **Pitfall:** 生產環境用 PostgreSQL，測試環境用 H2。當使用到特定 SQL 語法（如 JSONB 查詢）時，H2 無法支援，或者行為不一致。
  - **Solution:** 全面改用 Testcontainers 啟動與生產環境相同版本的資料庫。
  - **Pitfall:** Using PostgreSQL in production but H2 for tests. When using specific SQL features (like JSONB queries), H2 fails or behaves differently.
  - **Solution:** Switch entirely to Testcontainers to spin up the exact same database version as production.

---

## Checklists & workflows｜檢查清單與流程

在提交 Pull Request 前，請透過以下清單檢查你的測試程式碼：
Before submitting a Pull Request, verify your test code against this checklist:

- [ ] **獨立性 (Independence)**：測試是否可以任意順序執行？（有沒有共享的靜態可變狀態？） / Can tests run in any order? (Are there shared static mutable states?)
- [ ] **命名清晰 (Clear Naming)**：測試方法名稱是否清楚說明了「情境」與「預期結果」？ / Does the test method name clearly state the "scenario" and "expected outcome"?
- [ ] **單一斷言概念 (Single Assertion Concept)**：每個測試是否只驗證一個邏輯概念？（可以有多個 `assert`，但必須針對同一件事）。 / Does each test verify only one logical concept? (Multiple `assert`s are fine if they relate to the same thing).
- [ ] **邊界條件 (Edge Cases)**：是否涵蓋了 Null、空集合、極端數值、以及預期的 Exception？ / Are Nulls, empty collections, extreme values, and expected Exceptions covered?
- [ ] **Mock 驗證 (Mock Verification)**：是否只 Mock 了介面/外部依賴，而沒有 Mock 受測系統 (SUT) 本身？ / Did you only mock interfaces/external dependencies, and NOT the System Under Test (SUT) itself?
- [ ] **資源清理 (Resource Cleanup)**：整合測試後，資料庫狀態是否被正確清理（例如使用 `@Transactional` 回滾，或在 `@AfterEach` 清理）？ / Are database states properly cleaned up after integration tests (e.g., using `@Transactional` rollback, or cleaning in `@AfterEach`)?

---

## Real-world examples｜實戰案例

以下展示一個真實場景：`OrderService` 負責建立訂單。它需要查詢資料庫（Repository）並呼叫外部金流 API（PaymentGateway）。
The following demonstrates a real-world scenario: `OrderService` is responsible for creating orders. It needs to query the database (Repository) and call an external payment API (PaymentGateway).

### 1. Unit Test with Mockito (單元測試：專注業務邏輯)

我們使用 `@ExtendWith(MockitoExtension.class)` 來自動初始化 Mocks。
We use `@ExtendWith(MockitoExtension.class)` to initialize mocks automatically.

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository; // Mock the DB

    @Mock
    private PaymentGateway paymentGateway;   // Mock the external API

    @InjectMocks
    private OrderService orderService;       // System Under Test (SUT)

    @Test
    void should_ThrowException_When_PaymentFails() {
        // Arrange
        Order order = new Order("item-123", 100.0);
        // Simulate payment failure
        when(paymentGateway.charge(any())).thenReturn(PaymentResult.FAILED);

        // Act & Assert
        PaymentException exception = assertThrows(PaymentException.class, () -> {
            orderService.placeOrder(order);
        });
        
        assertEquals("Payment declined", exception.getMessage());
        
        // Verify that we NEVER tried to save the order to the DB
        verify(orderRepository, never()).save(any());
    }
    
    @Test
    void should_SaveOrder_When_PaymentSucceeds() {
        // Arrange
        Order order = new Order("item-123", 100.0);
        when(paymentGateway.charge(any())).thenReturn(PaymentResult.SUCCESS);
        when(orderRepository.save(order)).thenReturn(order);

        // Act
        Order result = orderService.placeOrder(order);

        // Assert
        assertNotNull(result);
        // Verify side-effect: API was called exactly once
        verify(paymentGateway, times(1)).charge(order.getAmount());
        // Verify side-effect: Order was saved
        verify(orderRepository).save(order);
    }
}
```

### 2. Integration Test with Testcontainers (整合測試：真實資料庫)

驗證 Repository 層是否能正確與 PostgreSQL 互動。這裡我們不使用 Mockito，而是啟動真實的 Docker 容器。
Verify if the Repository layer interacts correctly with PostgreSQL. Here we don't use Mockito; instead, we spin up a real Docker container.

```java
@Testcontainers
@DataJpaTest // Spring Boot annotation for testing JPA slices
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // Disable H2 auto-replacement
class OrderRepositoryIntegrationTest {

    // Singleton Container Pattern: Static container shared across all test methods
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        // Wire the container's random port to Spring Boot properties
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void should_SaveAndRetrieveOrder_FromRealPostgres() {
        // Arrange
        Order order = new Order("item-999", 250.0);

        // Act
        Order savedOrder = orderRepository.save(order);
        Optional<Order> retrievedOrder = orderRepository.findById(savedOrder.getId());

        // Assert
        assertTrue(retrievedOrder.isPresent());
        assertEquals("item-999", retrievedOrder.get().getItemCode());
        // This proves our JPA mappings and DB constraints work in reality!
    }
}
```