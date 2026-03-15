# 專案結構與分層架構最佳實踐 / Project Structure & Layered Architecture Best Practices

## Mental model｜心智模型

在 Spring Boot 專案中，架構不僅僅是資料夾的排列組合，它是**關注點分離 (Separation of Concerns)** 的具體展現。

想像你的專案是一座**現代化圖書館**：
1.  **Controller (櫃台)**：負責接待讀者（HTTP Request），驗證借閱證（Validation），但不負責修書或寫書。
2.  **Service (館員/後勤)**：核心業務邏輯所在。負責調度書籍、處理逾期罰款、採購流程。這是圖書館運作的「大腦」。
3.  **Repository (書庫管理系統)**：只負責從倉庫（Database）存取資料，不關心書被借出去後要做什麼。
4.  **DTO (表單)**：讀者填寫的借閱單。它不是書本體（Entity），只是用來傳遞資訊的載體。

**核心原則 (Core Principle)**：
**"Screaming Architecture"** — 當你打開專案結構時，它應該大聲告訴你「這是一個電商系統」或「這是一個庫存管理系統」，而不是只告訴你「這是一個 MVC 框架」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Package-by-Feature over Package-by-Layer
**優先採用「按功能分包」，而非「按層級分包」。**

*   **Package-by-Layer (Traditional)**: 把所有 Controller 放一起，所有 Service 放一起。
    *   *缺點*：功能分散，修改一個功能需要在多個資料夾間跳轉；Package 權限難以控管（類別必須是 `public` 才能跨包呼叫）。
*   **Package-by-Feature (Recommended)**: 將與特定業務功能（如 `order`, `user`, `product`）相關的 Controller, Service, Repository 放在同一個 Package 下。
    *   *優點*：高內聚 (High Cohesion)。除了對外暴露的介面外，其他類別可設為 `package-private`，實現模組化封裝。

### 2. Strict Layering & DTO Mapping Strategy
**嚴格分層與 DTO 轉換策略。**

*   **Controller Layer**: 僅處理 HTTP 協定（Status Code, Header）、輸入驗證（`@Valid`）與 DTO 轉換。**絕不包含業務邏輯。**
*   **Service Layer**: 處理 Transaction (`@Transactional`)、業務規則、呼叫 Repository。輸入輸出建議皆為 DTO 或 Domain Model，盡量避免直接回傳 Entity 給 Controller。
*   **Repository Layer**: 專注於 JPA/SQL 查詢。
*   **DTO Strategy**:
    *   **Request DTO**: 接收前端參數，搭配 Bean Validation。
    *   **Response DTO**: 回傳前端所需欄位，隱藏敏感資訊（如密碼、內部 ID）。
    *   **Mapping**: 使用工具（如 MapStruct）或手寫 Converter，避免在 Controller 中散落大量的 `set/get` 程式碼。

### 3. Dependency Rule
**依賴方向必須是單向的。**

*   `Controller` -> `Service` -> `Repository`
*   外層依賴內層，內層決不知道外層的存在。
*   **避免** Service 互相依賴導致的循環引用 (Circular Dependency)。如果 Service A 需要 Service B，而 Service B 又需要 Service A，這通常代表需要提取第三個 Service 或使用 Event-Driven 機制解耦。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fat Controller" (肥胖的控制器)
*   **徵兆**：Controller 類別中包含大量的 `if-else` 邏輯、資料計算或直接呼叫 DB。
*   **後果**：難以測試（需要 Mock HTTP 環境）、邏輯無法重用、違反單一職責原則。
*   **修正**：將所有邏輯下推至 Service 層。

### 2. Leaking JPA Entities to the Web Layer (實體洩漏)
*   **徵兆**：Controller 直接回傳 `@Entity` 物件給前端。
*   **後果**：
    *   **安全性風險**：意外暴露敏感欄位（如 `password`, `salt`）。
    *   **效能問題**：觸發 JPA 的 N+1 查詢或 Lazy Loading 異常 (`LazyInitializationException`)，因為 JSON 序列化時會嘗試讀取關聯物件。
    *   **耦合**：前端 API 合約與資料庫結構綁死，改 DB 欄位就壞 API。
*   **修正**：務必在 Service 或 Controller 邊界將 Entity 轉換為 DTO。

### 3. Spaghetti Dependency Injection (義大利麵式依賴注入)
*   **徵兆**：一個 Service 注入了 10 個其他的 Repository 或 Service。
*   **後果**：該 Service 承擔了過多職責 (God Class)，難以維護與測試。
*   **修正**：使用 Facade Pattern 整合多個 Service，或重新設計領域邊界 (Domain Boundaries)。

### 4. Anemic Domain Model (貧血模型) - *Contextual*
*   **徵兆**：Entity 只有 Getters/Setters，所有邏輯都在 Service。
*   **說明**：雖然這是 Spring 常見模式，但若邏輯純粹是操作該物件的狀態（如 `order.calculateTotal()`），應放回 Entity 中，讓物件擁有行為（Rich Domain Model），Service 僅負責協調。

---

## Checklists & workflows｜檢查清單與流程

### Project Structure Review Checklist
在建立新功能或 Code Review 時使用：

- [ ] **Packaging**: 相關的類別（Controller, Service, Repository）是否放在同一個 Feature Package 下？
- [ ] **Visibility**: 非公開的 Helper 類別或實作類別，是否已設為 `package-private`（不加 public 修飾符）？
- [ ] **Layering**: Controller 是否完全沒有業務邏輯？是否只負責轉發？
- [ ] **Data Safety**: Controller 的回傳值是否為 DTO 而非 Entity？
- [ ] **Validation**: 輸入驗證是否在 Controller 層（使用 `@Valid`）就攔截掉，而不是進到 Service 才檢查 null？
- [ ] **Exception Handling**: 是否有定義全域異常處理（`@ControllerAdvice`），而不是在 Controller 裡寫滿 try-catch？

### Decision Tree: Where to put logic?
當你不確定一段程式碼該放哪裡時：

1.  **是關於 HTTP、JSON 解析、Status Code 嗎？** -> `Controller`
2.  **是關於資料庫查詢語法、SQL 嗎？** -> `Repository`
3.  **是關於單一物件的狀態變更（如計算總價）？** -> `Domain Entity` (優先) 或 `Service`
4.  **涉及多個物件互動、交易控制、發送 Email、呼叫第三方 API？** -> `Service`
5.  **是單純的資料欄位轉換（Entity <-> DTO）？** -> `Mapper` / `Converter`

---

## Real-world examples｜實戰案例

### 1. Directory Structure Comparison

**❌ Bad Practice (Package-by-Layer):**
專案變大時，要在這些資料夾海中找到「訂單取消」邏輯非常困難。
```text
com.example.app
├── controllers
│   ├── OrderController.java
│   ├── UserController.java
│   └── ProductController.java
├── services
│   ├── OrderService.java
│   └── ...
├── repositories
│   ├── OrderRepository.java
│   └── ...
└── dtos
    └── OrderDto.java
```

**✅ Good Practice (Package-by-Feature):**
模組化清晰，刪除或重構「訂單」功能時，只需關注 `order` 資料夾。
```text
com.example.app
├── order                 // Feature: Order
│   ├── OrderController.java
│   ├── OrderService.java
│   ├── OrderRepository.java
│   ├── Order.java        // Entity
│   └── dto
│       ├── CreateOrderRequest.java
│       └── OrderResponse.java
├── user                  // Feature: User
│   ├── UserController.java
│   └── ...
└── common                // Shared utilities
    └── exception
```

### 2. DTO Mapping & Layering Implementation

這是一個標準的 Service 方法實作範例，展示了從 DTO 到 Entity 再回到 DTO 的流程。

```java
// Service Layer
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductClient productClient; // External dependency
    private final OrderMapper orderMapper;     // MapStruct or custom mapper

    @Transactional
    public OrderResponse createOrder(CreateOrderRequest request) {
        // 1. Business Validation (Logic not suitable for @Valid)
        if (!productClient.hasStock(request.getProductId())) {
            throw new OutOfStockException("Product is out of stock");
        }

        // 2. Map DTO to Entity
        Order order = orderMapper.toEntity(request);
        
        // 3. Execute Domain Logic
        order.setStatus(OrderStatus.PENDING);
        order.calculateTotalPrice(); // Logic inside Entity (Rich Domain)

        // 4. Persistence
        Order savedOrder = orderRepository.save(order);

        // 5. Map Entity to Response DTO (Never return 'savedOrder' directly)
        return orderMapper.toResponse(savedOrder);
    }
}
```

### 3. Avoiding Circular Dependency

**Problem:**
`UserService` 需要 `EmailService` 發信；`EmailService` 需要 `UserService` 查 Email 地址。

**Solution (Event-Driven):**
1. `UserService` 完成註冊後，發布一個 `UserRegisteredEvent`。
2. `EmailService` 監聽這個 Event。
3. 解耦：`UserService` 不再依賴 `EmailService`。

```java
// UserService.java
@Transactional
public void register(UserDto dto) {
    User user = repo.save(mapper.toEntity(dto));
    // Publish event instead of calling EmailService directly
    applicationEventPublisher.publishEvent(new UserRegisteredEvent(user));
}

// EmailService.java (Listener)
@EventListener
public void handleUserRegistered(UserRegisteredEvent event) {
    sendWelcomeEmail(event.getUser().getEmail());
}
```