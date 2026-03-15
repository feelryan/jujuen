# 核心機制與 Bean 生命週期實戰 / Core Mechanisms & Bean Lifecycle in Practice

## Mental model｜心智模型

要掌握 Spring Boot 的核心，必須從「黑盒子」思維轉向「工廠流水線」思維。不要只把 Spring 當作一個 Map (IoC Container)，而要將其視為一個分階段的**物件加工廠**。

To master Spring Boot, you must shift from a "Black Box" mindset to a "Factory Assembly Line" mindset. Don't just view Spring as a Map (IoC Container), but as a multi-staged **Object Processing Factory**.

### 1. The Three-Stage Assembly Line (三階段流水線)
Spring Bean 的誕生並非一瞬間完成，而是經歷三個主要階段：

1.  **Definition (定義階段)**: Spring 掃描 `@Component`, `@Configuration`, xml 等，將這些資訊解析為 `BeanDefinition`（藍圖）。此時還沒有任何 Java 物件被建立。
2.  **Instantiation (實例化階段)**: 根據藍圖，呼叫 Constructor 建立「原始物件」。
3.  **Initialization (初始化/加工階段)**:
    - **Populate Properties**: 注入依賴 (`@Autowired`).
    - **Post-Processing**: 這是最關鍵的一步。AOP、`@Transactional`、`@Async` 都在這裡透過 **Proxy (代理模式)** 包裝原始物件。
    - **Lifecycle Callbacks**: 執行 `@PostConstruct` 或 `afterPropertiesSet`。

### 2. The Proxy Illusion (代理的錯覺)
當你在 Controller 注入一個 Service 時，你拿到的通常**不是**你寫的那個 Class 的實例，而是一個 **CGLIB 生成的代理物件 (Proxy)**。

- **Mental Image**: 你以為你握著的是「本尊」，其實你握著的是「經紀人」。
- **Implication**: 當你呼叫方法時，是先經過「經紀人」（處理 Transaction, Logging），再轉交給「本尊」。如果你在「本尊」內部呼叫自己的另一個方法（`this.method()`），你會繞過「經紀人」，導致 Transaction 失效。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Constructor Injection as Default (建構子注入為預設)
永遠優先使用建構子注入，而非 Field Injection (`@Autowired` on fields)。

*   **Why**:
    *   **Immutability**: 欄位可以設為 `final`。
    *   **Testability**: 單元測試時不需要啟動 Spring Context，直接 `new Service(mockRepo)` 即可。
    *   **Fail Fast**: 依賴缺失時，App 啟動當下就會報錯，而不是等到執行時遇到 NullPointer。

```java
// ✅ Best Practice
@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}

// ❌ Anti-pattern
@Service
public class UserService {
    @Autowired // Field injection
    private UserRepository userRepository; 
}
```

### 2. Smart Lifecycle Management (智慧生命週期管理)
區分「Bean 的初始化」與「應用程式的啟動邏輯」。

*   **`@PostConstruct`**: 用於 Bean 內部的邏輯驗證或輕量設定（例如檢查某個 config 是否合法）。
*   **`CommandLineRunner` / `ApplicationReadyEvent`**: 用於應用程式啟動後的重型任務（例如 Cache Warming、發送啟動通知）。避免在 `@PostConstruct` 做耗時操作，這會卡住整個 App 的啟動時間。

### 3. Conditional Configuration (條件式配置)
善用 `@ConditionalOnProperty` 來管理 Feature Flags 或環境差異，而不是在程式碼裡寫大量的 `if (env.equals("dev"))`。

```java
@Bean
@ConditionalOnProperty(name = "features.audit-log", havingValue = "true")
public AuditService realAuditService() {
    return new DatabaseAuditService();
}

@Bean
@ConditionalOnProperty(name = "features.audit-log", havingValue = "false", matchIfMissing = true)
public AuditService noOpAuditService() {
    return new NoOpAuditService(); // Null Object Pattern
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Self-Invocation" Trap (自我呼叫陷阱)
這是 Spring 開發者最常踩的坑。在同一個 Class 內部呼叫帶有 `@Transactional`, `@Async`, `@Cacheable` 的方法，這些註解會**完全失效**。

*   **Reason**: 內部呼叫 (`this.method()`) 繞過了 Spring Proxy。
*   **Solution**:
    1.  **Self-inject**: 注入自己 (需使用 `@Lazy` 避免循環依賴)。
    2.  **Refactor**: 將該方法抽離到另一個 Bean (推薦做法)。

### 2. Prototype Bean Injection into Singleton (Singleton 內的 Prototype 陷阱)
如果你在 Singleton Bean (預設) 中注入一個 Prototype Bean，這個 Prototype Bean **只會被建立一次**（在 Singleton 建立時）。

*   **Consequence**: 你以為每次用都是新的，實際上它是同一個實例，導致線程安全問題。
*   **Solution**: 使用 `ObjectProvider<T>` 或 `@Lookup` 方法。

```java
@Service
public class SingletonService {
    // ❌ 這樣寫，prototypeBean 永遠是同一個
    // private final PrototypeBean prototypeBean;

    // ✅ 正確做法
    private final ObjectProvider<PrototypeBean> prototypeProvider;

    public void doSomething() {
        PrototypeBean instance = prototypeProvider.getObject(); // 每次取得新的
        instance.process();
    }
}
```

### 3. Heavy Logic in Constructors (建構子中的重邏輯)
不要在 Constructor 中執行資料庫連線、外部 API 呼叫或複雜運算。

*   **Risk**: 拖慢啟動速度；如果依賴還沒完全準備好（例如 DB 連線池），可能會拋出異常；難以測試。
*   **Fix**: 移至 `@PostConstruct` 或 `ApplicationReadyEvent`。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist (程式碼審查清單)

- [ ] **Injection Style**: 是否使用了 Constructor Injection？欄位是否為 `final`？
- [ ] **Proxy Awareness**: 是否有在類別內部呼叫 `@Transactional` 或 `@Async` 方法的情況？(Self-invocation check)
- [ ] **Startup Performance**: 建構子 (`Constructor`) 和 `@PostConstruct` 中是否包含網路請求或耗時 I/O？
- [ ] **Scope Safety**: 是否在 Singleton Bean 中注入了帶有狀態 (Stateful) 的 Prototype/Request Scope Bean？
- [ ] **Circular Dependencies**: 是否使用了 `@Lazy` 來解決循環依賴？(這通常暗示架構設計有問題，應考慮重構)。

### Debugging Bean Issues Workflow (Bean 除錯流程)

當遇到 `NoSuchBeanDefinitionException` 或配置不生效時：

1.  **Check Scanning**: 該類別是否在 `@SpringBootApplication` 的 package 或子 package 下？如果不是，是否有加 `@ComponentScan`？
2.  **Check Annotations**: 是否漏了 `@Component`, `@Service`, `@Configuration`？
3.  **Check Conditionals**: 是否有 `@ConditionalOnProperty` 或 `@Profile` 擋住了 Bean 的建立？
    *   *Tip*: 在 `application.properties` 加入 `debug=true`，啟動時查看 **Conditions Evaluation Report**。
4.  **Check Definition Overriding**: 是否有同名的 Bean 被覆蓋了？(Spring Boot 2.1+ 預設禁止覆蓋，需開啟 `spring.main.allow-bean-definition-overriding=true` 才能覆蓋，但應儘量避免)。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Silent" Transaction Failure (無聲的交易失敗)

**情境**: 開發者寫了一個 `UserService`，希望在大量匯入使用者時，若發生錯誤則回滾。

**錯誤寫法 (Anti-pattern)**:
```java
@Service
public class UserService {

    public void importUsers(List<User> users) {
        for (User user : users) {
            // ❌ 這裡呼叫的是 this.createUser()，繞過了 Proxy
            // 導致 @Transactional 根本沒生效，發生錯誤不會回滾
            createUser(user);
        }
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createUser(User user) {
        // DB Insert logic...
    }
}
```

**修正寫法 (Refactoring)**:
將 `createUser` 移至另一個 Service，或使用 `AopContext.currentProxy()` (較醜)，或自我注入。最乾淨的方式是職責分離：

```java
@Service
public class UserImportService {
    private final UserPersistenceService userPersistenceService;

    // Constructor Injection
    public UserImportService(UserPersistenceService userPersistenceService) {
        this.userPersistenceService = userPersistenceService;
    }

    public void importUsers(List<User> users) {
        for (User user : users) {
            // ✅ 透過外部 Bean 呼叫，Proxy 生效，Transaction 正常運作
            userPersistenceService.createUser(user);
        }
    }
}

@Service
public class UserPersistenceService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createUser(User user) {
        // DB Insert logic...
    }
}
```

### Scenario 2: Safe Cache Warming (安全的快取預熱)

**情境**: 應用程式啟動後，需要從 DB 撈取 Config 放入 Redis。

**錯誤做法**: 放在 `@PostConstruct`。
**後果**: 如果 Redis 連線短暫失敗，會導致整個 App 啟動失敗 (Crash Loop)。

**最佳實踐**:
```java
@Component
@Slf4j
public class CacheWarmer implements ApplicationRunner {

    private final ConfigService configService;

    public CacheWarmer(ConfigService configService) {
        this.configService = configService;
    }

    @Override
    public void run(ApplicationArguments args) {
        try {
            log.info("Starting cache warming...");
            configService.loadConfigsToRedis();
            log.info("Cache warming finished.");
        } catch (Exception e) {
            // 這裡可以決定是否要讓 App 啟動失敗，或是僅紀錄 Error log 讓 App 繼續運行
            log.error("Cache warming failed, system will run with DB fallback", e);
        }
    }
}
```