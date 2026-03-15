# 現代 Java 特性與 Spring Boot 3 整合 / Integrating Modern Java Features with Spring Boot 3

## Mental model｜心智模型

在 Spring Boot 3 (基於 Java 17+) 的時代，我們不再只是撰寫「樣板程式碼 (Boilerplate)」，而是轉向 **Data-Oriented Programming (資料導向程式設計)** 與 **High-Throughput Concurrency (高吞吐並發)**。

將你的思維從舊有的 Java 8/11 模式轉換到現代模式：

1.  **Data Carriers vs. Objects**: 以前我們習慣建立充滿 Getters/Setters/equals/hashCode 的 POJO；現在對於純資料傳輸（DTOs, Events, Configs），應將其視為不可變的數據載體，直接使用 **Records**。
2.  **Expressive Logic vs. Control Flow**: 以前用層層堆疊的 `if-else` 或 Visitor pattern 處理多型；現在利用 **Pattern Matching** 與 **Sealed Classes** 讓編譯器幫你確保邏輯的完整性與表達力。
3.  **Logical Tasks vs. OS Threads**: 以前並發受限於作業系統執行緒（OS Threads）的昂貴成本，必須依賴 Reactive Stack (WebFlux) 來榨乾效能；現在透過 **Virtual Threads**，你可以用同步（Blocking）的寫法，獲得非同步（Non-blocking）的吞吐量。

> **The Core Shift**: Write less code to define data, use structure to drive logic, and stop worrying about thread pool exhaustion for I/O tasks.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Records as First-Class Citizens in Spring
在 Spring Boot 3 中，Records 已經被廣泛支援。

-   **Controller DTOs**: 使用 Record 定義 Request/Response body。Spring MVC 的 Jackson 序列化器能完美處理它們。
-   **Configuration Properties**: 使用 `@ConfigurationProperties` 綁定設定檔時，使用 Record 可以確保設定不可變（Immutable）。
-   **JPA Projections**: 使用 Record 來接收 JPA Query 的特定欄位結果（唯讀視圖），比 Interface projection 更直觀且效能更好。

### 2. Pattern Matching for Business Logic
利用 `switch` 表達式與模式匹配來簡化複雜的業務規則，特別是在處理多種實作類型時。

-   **Global Exception Handling**: 在 `@ControllerAdvice` 中，利用 Pattern Matching 針對不同的 Exception 類型回傳不同的 HTTP Status，減少 `instanceof` 的濫用。
-   **Domain Events**: 當有多種事件類型（如 `OrderCreated`, `OrderShipped`）時，使用 Sealed Interface + Pattern Matching 確保所有事件都被處理。

### 3. Virtual Threads for I/O Bound Tasks
Spring Boot 3.2+ 正式支援 Virtual Threads。

-   **Enable it simply**: 在 `application.properties` 設定 `spring.threads.virtual.enabled=true`。這會自動將 Tomcat 和 TaskExecutor 切換為虛擬執行緒。
-   **Imperative Style**: 你不需要再為了效能強迫自己寫 Reactor/WebFlux。對於大多數 CRUD + 呼叫外部 API 的微服務，Virtual Threads + RestClient 是最佳解。

### 4. Text Blocks for SQL/JSON
在程式碼中嵌入 SQL 或 JSON 範本時（例如 `@Query` 或測試用的 JSON payload），務必使用 Text Blocks (`"""`) 保持可讀性。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Record as JPA Entity" Trap (Record 當作 Entity)
-   **Bad Practice**: 嘗試將 `record` 用作 `@Entity`。
-   **Why**: JPA 規範要求 Entity 必須有無參數建構子（No-args constructor）且通常是非 final 的（為了 Lazy Loading proxy）。Record 是 final 且全參數建構，這與 JPA/Hibernate 的核心機制衝突。
-   **Correction**: 繼續使用一般的 Class 作為 `@Entity`，但使用 Record 作為 DTO。

### 2. Virtual Thread Pinning (虛擬執行緒釘選)
-   **Bad Practice**: 在 Virtual Threads 執行的路徑中，長時間持有 `synchronized` 區塊。
-   **Why**: 當 Virtual Thread 進入 `synchronized` 方法或區塊時，它會被 "Pin" 在底層的 OS Thread 上，導致無法卸載（Unmount），這會讓 Virtual Threads 失去優勢，甚至退化成傳統執行緒的效能瓶頸。
-   **Correction**: 將 `synchronized` 替換為 `ReentrantLock`，或者確保同步區塊極短且不包含 I/O 操作。

### 3. Modifying Collections in Records
-   **Bad Practice**: 在 Record 中回傳可變的集合（Mutable Collections）。
-   **Why**: Record 承諾的是不可變性（Immutability）。如果你的 Record getter 回傳了 `ArrayList` 的參考，外部呼叫者可以修改內容，破壞了 Record 的契約。
-   **Correction**: 在 Compact Constructor 中將集合包裝為 `List.copyOf()` 或 `Collections.unmodifiableList()`。

### 4. Overusing `var`
-   **Bad Practice**: 在所有地方都用 `var`，導致程式碼可讀性下降。
-   **Why**: 雖然 `var` 減少了打字量，但在 Spring 專案中，如果回傳型別不明顯（例如 `var result = service.process();`），Code Review 會很痛苦。
-   **Correction**: 僅在變數名稱能清楚表達型別，或型別非常冗長（如泛型巢狀）時使用 `var`。

---

## Checklists & workflows｜檢查清單與流程

### Migration & Implementation Checklist

在升級或開發 Spring Boot 3 專案時，請依序檢查以下項目：

#### Phase 1: Data Structures (Records)
- [ ] **DTOs**: 所有 Controller 的 Request/Response 是否已轉換為 `record`？
- [ ] **Config**: `@ConfigurationProperties` 是否改用 `record` 配合 `@ConstructorBinding`（Spring Boot 3.0+ 預設支援）？
- [ ] **Validation**: Record 欄位上是否正確加上了 Bean Validation 註解（如 `@NotNull`, `@Size`）？

#### Phase 2: Logic Flow (Pattern Matching)
- [ ] **Refactoring**: 檢查 Service 層是否有冗長的 `if (obj instanceof Type) { ... }`，並重構為 Pattern Matching `if (obj instanceof Type t) { ... }`。
- [ ] **Switch Expressions**: 檢查是否有複雜的狀態機判斷，改用 `switch` 表達式以確保覆蓋所有 case。

#### Phase 3: Concurrency (Virtual Threads)
- [ ] **Configuration**: 設定 `spring.threads.virtual.enabled=true`。
- [ ] **Dependency Check**: 檢查使用的第三方 Library 是否有嚴重的 `synchronized` I/O 依賴（可能導致 Pinning）。
- [ ] **Observability**: 使用 JFR (Java Flight Recorder) 或 Micrometer 監控虛擬執行緒的 Pinning 事件。

---

## Real-world examples｜實戰案例

### Example 1: Modern DTO with Validation & Transformation
結合 Record、Compact Constructor 進行正規化，以及 Instance Methods 進行轉換。

```java
// 定義：包含驗證與自動修剪空白的 DTO
public record CreateUserRequest(
    @NotBlank String username,
    @Email String email
) {
    // Compact Constructor: 在賦值前進行資料正規化
    public CreateUserRequest {
        username = username.trim();
        email = email.toLowerCase();
    }

    // 轉換邏輯直接內聚在 Record 中
    public UserEntity toEntity() {
        return new UserEntity(this.username, this.email);
    }
}

// 使用：Controller 層極度簡潔
@PostMapping
public ResponseEntity<Void> createUser(@Valid @RequestBody CreateUserRequest request) {
    userService.save(request.toEntity());
    return ResponseEntity.status(HttpStatus.CREATED).build();
}
```

### Example 2: Pattern Matching in Error Handling
在全域異常處理中，利用 Switch Pattern Matching 讓程式碼更扁平。

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleExceptions(Exception ex) {
        return switch (ex) {
            // 針對特定業務異常的解構與處理
            case UserNotFoundException unfe -> 
                ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, unfe.getMessage());
            
            case InsufficientBalanceException ibe -> 
                ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Current balance: " + ibe.getCurrentBalance());
            
            // 處理 Spring Security 或其他框架異常
            case AccessDeniedException ade -> 
                ProblemDetail.forStatusAndDetail(HttpStatus.FORBIDDEN, "Access Denied");
            
            // 預設處理
            default -> {
                logger.error("Unexpected error", ex);
                yield ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Internal Server Error");
            }
        };
    }
}
```

### Example 3: Virtual Threads Integration
啟用虛擬執行緒後，你可以像寫傳統 Blocking Code 一樣寫高並發程式，無需 `CompletableFuture` 或 `Mono/Flux`。

**application.properties**:
```properties
spring.threads.virtual.enabled=true
```

**Service Layer**:
```java
@Service
public class AggregationService {
    
    private final RestClient restClient;

    public AggregationService(RestClient.Builder builder) {
        this.restClient = builder.build();
    }

    // 這個方法在 Virtual Thread 上執行
    // 即使外部 API 回應慢，底層 OS Thread 也會被釋放去處理其他請求
    public DashboardData getDashboard() {
        // 平行呼叫兩個外部服務 (Structured Concurrency 範式預覽中，此為現階段可用寫法)
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            
            Supplier<UserData> userTask = scope.fork(() -> 
                restClient.get().uri("/users/me").retrieve().body(UserData.class));
                
            Supplier<OrdersData> ordersTask = scope.fork(() -> 
                restClient.get().uri("/orders/recent").retrieve().body(OrdersData.class));

            scope.join(); // 等待所有任務完成 (Non-blocking wait)
            scope.throwIfFailed(); // 處理異常

            return new DashboardData(userTask.get(), ordersTask.get());
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException(e);
        }
    }
}
```