# 測試策略：從單元測試到 Testcontainers / Testing Strategy: From Unit Tests to Testcontainers

## Mental model｜心智模型

在 Spring Boot 專案中，測試不只是一個「金字塔」，更像是一組「同心圓」或「切片（Slices）」。要建立高效且高信心的測試策略，你需要建立以下心智模型：

1.  **Context Weight (上下文權重)**：
    *   **Pure Unit Test (POJO)**：不啟動 Spring Context。速度最快，適用於純商業邏輯（Domain Logic）、工具類別。
    *   **Slice Test (@WebMvcTest, @DataJpaTest)**：只啟動 Spring Context 的一部分。速度中等，專注於測試「框架整合點」（如 Controller 的 JSON 序列化、Repository 的 SQL 語法）。
    *   **Integration Test (@SpringBootTest + Testcontainers)**：啟動完整 Context 與真實外部依賴（Docker）。速度最慢但信心度最高，確保各組件與真實資料庫/MQ 協作無誤。

2.  **Production Parity (生產環境一致性)**：
    *   過去我們常使用 H2 (In-memory DB) 來測試，但 H2 與 PostgreSQL/MySQL 語法與行為存在差異（例如 JSONB 支援、特定 Constraint）。
    *   **Testcontainers 的核心哲學**：在測試中使用與生產環境完全相同的基礎設施（Dockerized dependencies）。"Don't mock what you don't own" —— 對於資料庫，不要 Mock，用真的。

3.  **Context Caching (上下文快取)**：
    *   Spring Test Framework 會嘗試快取 ApplicationContext。如果你的測試設定（Profiles, Properties, Mocks）在不同測試類別間頻繁變動，會導致 Context 重啟（Context Reloading），這是測試執行時間暴增的元兇。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Spring Boot 3.1+ Testcontainers Connection
在 Spring Boot 3.1 之後，利用 `@ServiceConnection` 自動管理連線資訊，取代舊有的 `DynamicPropertySource`。

```java
@Testcontainers
@SpringBootTest
class ApplicationIntegrationTest {

    @Container
    @ServiceConnection // 自動注入 spring.datasource.url 等屬性
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @Test
    void contextLoads() {
        // ...
    }
}
```

### 2. The Singleton Container Pattern (單例容器模式)
為了避免每個 Test Class 都重新啟動 Docker Container（非常耗時），應使用 Abstract Base Class 或是手動管理 Singleton Container，讓所有整合測試共用同一個 DB 實例。

*   **實作方式**：宣告 `static final` 的 Container 並手動 start，或使用 Shared Container Pattern。

### 3. Slice Testing 職責分離
嚴格遵守 Slice Testing 的邊界，不要越界測試。

*   **@WebMvcTest (Controller Layer)**：
    *   **Focus**：HTTP Status、JSON 格式、Input Validation、Exception Handling。
    *   **Mock**：必須 Mock Service 層 (`@MockBean`)。
    *   **Don't**：不要測試商業邏輯或資料庫存取。
*   **@DataJpaTest (Repository Layer)**：
    *   **Focus**：Custom JPQL、Native Query、Entity Mapping、Database Constraints。
    *   **Tool**：配合 Testcontainers 驗證真實 SQL 語法。
    *   **Don't**：不要載入 Controller 或 Service。

### 4. Testing "Pure" Business Logic
將核心商業邏輯從 Framework 中抽離。如果你的 Service 充滿了 `HttpServletRequest` 或 `Entity` 狀態管理，它就很難單元測試。
*   **Pattern**：將複雜計算邏輯移至 Domain Model (POJO) 中，對其編寫不需要 Spring Context 的 JUnit 測試（執行速度 < 10ms）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "H2" Trap (H2 陷阱)
*   **現象**：開發用 H2 跑測試全過，上線後因為 SQL 語法差異（如 MySQL 的 `GROUP BY` 嚴格模式或 Postgres 的 `JSONB` 操作）導致爆炸。
*   **解法**：全面棄用 H2 進行整合測試，改用 Testcontainers。

### 2. Context Reloading Hell (上下文重啟地獄)
*   **現象**：執行 `mvn test` 需要 10 分鐘，但單獨跑每個測試都很快。
*   **原因**：濫用 `@MockBean`、`@DirtyContext` 或在不同測試類別使用不同的 `@TestPropertySource`。這會導致 Spring 無法重複利用 Cached Context。
*   **解法**：
    *   盡量減少 `@MockBean` 的使用（改用 Stub 或 Fake）。
    *   統一測試配置基類（Base Integration Test Class）。

### 3. Over-Mocking (過度模擬)
*   **現象**：測試程式碼中充滿了 `when(repo.save(any())).thenReturn(...)`。
*   **後果**：你測試的是 Mock 的行為，而不是系統的行為。如果 Repository 方法改名或邏輯改變，測試可能仍然通過（False Negative）。
*   **原則**：Integration Test 中盡量少 Mock，讓資料真正寫入 Testcontainer DB。

### 4. Testing Private Methods
*   **現象**：使用 Reflection 或 PowerMock 去測試 private 方法。
*   **後果**：重構時測試極易損壞。
*   **解法**：只測試 `public` 介面。如果 `private` 方法複雜到需要單獨測試，代表它應該被重構為另一個獨立類別的 `public` 方法。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Which test to write?
- **邏輯是否依賴外部資源 (DB, API)?**
    - **No** → **Unit Test** (JUnit 5 + Mockito if needed). *Speed: Fast.*
    - **Yes** → **Is it a Controller?**
        - **Yes** → **@WebMvcTest** (Mock Service). *Speed: Medium.*
        - **No** → **Is it a Repository/DB Query?**
            - **Yes** → **@DataJpaTest** (w/ Testcontainers). *Speed: Medium-Slow.*
            - **No (Full Flow)** → **@SpringBootTest** (w/ Testcontainers). *Speed: Slow.*

### CI/CD Integration Checklist
- [ ] **Docker Availability**：CI Agent (Jenkins/GitHub Actions/GitLab CI) 支援 Docker-in-Docker 或 Docker Socket Binding (這是 Testcontainers 運作的前提)。
- [ ] **Resource Limits**：Testcontainers 會吃掉大量記憶體，確認 CI 機器有足夠 RAM (至少 4GB+ 建議)。
- [ ] **Test Reporting**：配置 Surefire Plugin 產出 XML 報告，以便 CI 工具解析失敗原因。
- [ ] **Flaky Test Detection**：監控是否有測試偶爾失敗（通常是因為異步處理或 Container 啟動超時）。

### Code Review Checklist for Tests
- [ ] **Readability**：測試名稱是否描述了行為？(e.g., `shouldReturn404WhenUserNotFound` vs `test1`).
- [ ] **Independence**：測試之間是否互相依賴？(e.g., Test B 依賴 Test A 產生的資料 —— **絕對禁止**)。
- [ ] **Assertions**：是否使用了具語意化的斷言庫 (AssertJ)？(e.g., `assertThat(list).hasSize(1)` 優於 `assertEquals(1, list.size())`)。
- [ ] **Cleanup**：整合測試是否依賴 `@Transactional` 自動回滾？如果是，請確認這不會掩蓋 Transaction 邊界的 Bug。

---

## Real-world examples｜實戰案例

### 1. Controller Slice Test (Web Layer Only)
專注於 API 合約測試，不啟動 DB。

```java
@WebMvcTest(UserController.class)
// 排除 Security Filter Chain 以簡化測試，或匯入專門的 TestSecurityConfig
@Import(TestSecurityConfig.class) 
class UserControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean UserService userService; // Mock 下一層

    @Test
    void shouldReturnUser_WhenIdExists() throws Exception {
        // Given
        UserDto user = new UserDto(1L, "Alice");
        given(userService.findById(1L)).willReturn(user);

        // When & Then
        mockMvc.perform(get("/api/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

### 2. Repository Test with Testcontainers (Data Layer Only)
驗證真實 SQL 與 DB Constraint，使用 Spring Boot 3.1 `@ServiceConnection`。

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE) // 關閉 H2 自動替換
@Testcontainers
class UserRepositoryTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired UserRepository userRepository;

    @Test
    void shouldFindActiveUsers() {
        // Given
        userRepository.save(new User("Bob", Status.ACTIVE));
        userRepository.save(new User("Alice", Status.INACTIVE));

        // When
        List<User> activeUsers = userRepository.findByStatus(Status.ACTIVE);

        // Then (Using AssertJ)
        assertThat(activeUsers)
            .hasSize(1)
            .extracting(User::getName)
            .containsExactly("Bob");
    }
}
```

### 3. Base Integration Test Class (Optimization)
解決 Container 重複啟動問題的實戰模式。

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public abstract class BaseIntegrationTest {

    static final PostgreSQLContainer<?> postgres;

    static {
        // 使用 static block 手動啟動，確保所有繼承此類別的測試共用同一個 Container
        postgres = new PostgreSQLContainer<>("postgres:15");
        postgres.start();
    }

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
    
    @Autowired
    protected ObjectMapper objectMapper;
    
    // 可以在這裡加入 @BeforeEach 來清除 DB 資料 (如果 @Transactional 不適用的話)
}
```