# 常見反模式與程式碼異味 / Common Anti-patterns & Code Smells

## Mental model｜心智模型

在維護 Spring Boot 專案時，我們應將程式碼結構視為一個 **「嚴格分工的廚房 (Commercial Kitchen)」**，而非單純的程式碼堆疊。

1.  **職責邊界 (Boundaries of Responsibility)**：
    *   **Controller (外場服務生)**：只負責接單 (Request) 和上菜 (Response)。絕不應該進入廚房切菜或烹飪 (Business Logic)。
    *   **Service (內場廚師)**：負責烹飪 (Business Logic)。不應該直接跑去產地種菜 (Database details)，也不該管客人坐哪裡 (HTTP details)。
    *   **Repository (倉儲管理)**：只負責拿取食材 (Data Access)。

2.  **依賴的流向 (Flow of Dependencies)**：
    *   依賴應該是單向的、層次分明的。如果廚師 A 需要廚師 B，而廚師 B 又需要廚師 A 才能工作，這就是死鎖 (Circular Dependency)，整個廚房會停擺。

3.  **異味的本質 (The Essence of Smells)**：
    *   **Code Smells** 通常不是 Bug，而是「設計債 (Design Debt)」的訊號。它們暗示著高耦合 (High Coupling) 或低內聚 (Low Cohesion)，這會導致系統在未來難以測試與擴充。

---

## Patterns & best practices｜常見模式與最佳實務

在重構或撰寫新功能時，請遵循以下模式來避免異味：

### 1. Constructor Injection over Field Injection
**建構子注入優於欄位注入**。
這是 Spring 團隊官方推薦的做法。它保證了 Bean 在實例化時依賴已經備齊，並且讓單元測試更容易（不需要啟動 Spring Context 即可 `new` 出物件）。

*   **Good Pattern:**
    ```java
    @Service
    public class UserService {
        private final OrderService orderService;

        // 明確的依賴契約，且可以用於 final 欄位
        public UserService(OrderService orderService) {
            this.orderService = orderService;
        }
    }
    ```

### 2. DTO Pattern (Data Transfer Object)
**嚴格區分 API 模型與資料庫模型**。
永遠不要在 Controller 的回傳值或參數中直接使用 `@Entity`。這能防止「過度獲取 (Over-fetching)」、JSON 無限遞迴 (Infinite Recursion) 以及資料庫結構洩漏給前端。

### 3. Facade Pattern for Complex Logic
**使用外觀模式拆解 God Classes**。
當一個 Service 過大時，不要只是把它拆成 `Helper`。應該根據業務領域 (Domain) 拆分，如果需要協作，建立一個上層的 `Facade` 來協調多個細粒度的 Service。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Fat Controller (臃腫的控制器)
**徵兆**：Controller 方法中包含大量的 `if-else`、資料轉換、甚至是呼叫 Repository。
**後果**：無法單獨測試業務邏輯，API 介面與實作細節強耦合。

*   **Anti-pattern Example:**
    ```java
    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody UserDto dto) {
        // 錯誤：在 Controller 進行驗證與業務判斷
        if (repo.findByEmail(dto.getEmail()) != null) {
            return ResponseEntity.badRequest().body("Exists");
        }
        User user = new User();
        user.setEmail(dto.getEmail());
        // 錯誤：直接操作 DB
        repo.save(user); 
        return ResponseEntity.ok(user);
    }
    ```

### 2. God Class / The Blob (全能類別)
**徵兆**：一個類別（通常是 `UserService` 或 `CommonService`）超過 1000 行，依賴了十幾個其他的 Repository 或 Service。
**後果**：
*   **維護惡夢**：改一行程式碼可能影響完全不相關的功能（例如改「註冊」壞了「重設密碼」）。
*   **啟動變慢**：Bean 初始化依賴過多。
*   **違反 SRP**：單一職責原則蕩然無存。

### 3. Circular Dependencies (循環依賴)
**徵兆**：啟動時拋出 `BeanCurrentlyInCreationException`。
**情境**：Service A 依賴 Service B，Service B 又依賴 Service A。
**錯誤解法**：使用 `@Lazy` 或 `@Autowired` (Field Injection) 來暫時繞過檢查。這只是掩蓋了架構設計的錯誤。
**正確解法**：
1.  **萃取 (Extract)**：將 A 和 B 共用的邏輯抽離到第三個 Service C。
2.  **事件驅動 (Events)**：使用 Spring ApplicationEventPublisher，讓 A 發出事件，B 監聽事件，解開直接依賴。

### 4. Transactional Self-Invocation (交易自我呼叫)
**徵兆**：在同一個 Class 內，一個非交易方法呼叫另一個標註 `@Transactional` 的方法。
**後果**：交易失效。因為 Spring AOP 是基於 Proxy 的，類別內部呼叫 (this.method) 會繞過 Proxy，導致交易設定被忽略。

### 5. Leaking JPA Entities (洩漏實體)
**徵兆**：REST API 直接回傳 Hibernate Entity，且該 Entity 包含 `@OneToMany` 等關聯。
**後果**：
*   **效能殺手**：Jackson 序列化時觸發 Lazy Loading，導致 N+1 查詢甚至 `LazyInitializationException`。
*   **安全性**：不小心把 `password` 或 `salt` 欄位序列化傳給前端。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或提交 PR 前，請使用此清單自我檢核：

### Code Review Checklist
- [ ] **Controller 潔癖檢查**：Controller 是否只做「接收參數 -> 呼叫 Service -> 回傳 DTO」？有無任何業務邏輯？
- [ ] **依賴注入檢查**：是否移除了所有的 `@Autowired` 欄位注入，改用 `final` + 建構子注入？
- [ ] **God Class 預警**：是否有單一 Service 注入超過 5 個以上的依賴？如果是，是否該拆分？
- [ ] **循環依賴檢查**：是否依賴了 `@Lazy` 來解決啟動錯誤？如果是，請標記為 Refactor 項目。
- [ ] **實體隔離檢查**：Controller 的輸入與輸出是否完全使用了 DTO，而非 `@Entity`？
- [ ] **交易邊界檢查**：是否有 `private` 方法標註了 `@Transactional`（無效）？是否有內部互相呼叫導致交易失效？

### Refactoring Workflow: Breaking a God Class
當你發現一個巨大的 `UserService` 時，請依循以下步驟重構：

1.  **Group Methods**：將所有方法按功能分組（如：Authentication, Profile Management, Notification）。
2.  **Extract Service**：
    *   建立 `UserAuthService` (處理登入/註冊)。
    *   建立 `UserProfileService` (處理資料更新)。
    *   建立 `UserNotificationService` (處理信件發送)。
3.  **Delegate**：在原本的 `UserService` 中注入這些新 Service，將呼叫轉發（Deprecated 階段）。
4.  **Replace**：將呼叫端 (Controller) 改為直接呼叫新的細粒度 Service。
5.  **Delete**：移除舊的 God Class。

---

## Real-world examples｜實戰案例

### 案例 1：解決循環依賴 (Circular Dependency)

**情境**：
`OrderService` 需要在下單時呼叫 `CustomerService` 扣款。
`CustomerService` 需要在刪除用戶時呼叫 `OrderService` 清除歷史訂單。

**Bad Practice (使用 @Lazy 掩蓋)**：
```java
@Service
public class OrderService {
    @Autowired @Lazy private CustomerService customerService; // 治標不治本
}
```

**Best Practice (使用 Event 解耦)**：

1.  `OrderService` 專注於訂單邏輯。
2.  `CustomerService` 刪除用戶時，發出 `UserDeletedEvent`。
3.  `OrderService` (或獨立的 Listener) 監聽該事件並清理資料。

```java
// CustomerService.java
public void deleteUser(Long userId) {
    repo.deleteById(userId);
    eventPublisher.publishEvent(new UserDeletedEvent(userId)); // 只發送事件
}

// OrderCleanupListener.java (解耦)
@Component
public class OrderCleanupListener {
    private final OrderRepository orderRepo;

    @EventListener
    public void handleUserDeleted(UserDeletedEvent event) {
        orderRepo.deleteAllByUserId(event.getUserId());
    }
}
```

### 案例 2：重構 Controller 中的業務邏輯

**Bad Practice (邏輯洩漏)**：
```java
// UserController.java
@PutMapping("/{id}")
public User update(@PathVariable Long id, @RequestBody UserDto dto) {
    User user = repo.findById(id).orElseThrow();
    if (dto.getName() != null) user.setName(dto.getName()); // 髒邏輯
    if (dto.getStatus().equals("ACTIVE")) {                 // 業務規則洩漏
        emailService.sendWelcome(user.getEmail());
    }
    return repo.save(user);
}
```

**Best Practice (職責分離)**：
```java
// UserController.java
@PutMapping("/{id}")
public UserDto update(@PathVariable Long id, @RequestBody UserUpdateRequest request) {
    // Controller 只負責傳遞指令
    return userFacade.updateUserProfile(id, request);
}

// UserFacade / UserService
@Transactional
public UserDto updateUserProfile(Long id, UserUpdateRequest request) {
    User user = findUser(id);
    user.updateDetails(request.getName()); // 領域模型行為
    
    if (request.shouldActivate()) {
        user.activate();
        emailService.sendWelcome(user.getEmail());
    }
    
    return userMapper.toDto(userRepository.save(user));
}
```