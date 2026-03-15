# 交易管理與 JPA 常見陷阱檢核 / Transaction Management & Common JPA Pitfalls

## Mental model｜心智模型

要掌握 Spring Boot 的交易與 JPA，必須建立兩個核心的心智模型：**代理機制 (The Proxy Mechanism)** 與 **持久化上下文 (Persistence Context)**。

### 1. 代理人模式 (The Proxy Wrapper)
Spring 的 `@Transactional` 並不是魔法，它是透過 AOP (Aspect Oriented Programming) 運作的。
*   **想像一個「守門員」**：當你從外部呼叫一個 Service 方法時，你其實是先呼叫了 Spring 產生的 Proxy (守門員)。守門員負責開啟交易 (`Begin`)，然後呼叫你的實際方法，最後根據結果提交 (`Commit`) 或回滾 (`Rollback`)。
*   **繞過守門員 (Self-invocation)**：如果你在同一個 Class 內部，由方法 A 呼叫有 `@Transactional` 的方法 B，你是直接呼叫物件本身 (`this`)，守門員不在中間，因此**交易行為不會發生**。

### 2. 第一級快取與髒檢查 (L1 Cache & Dirty Checking)
JPA (Hibernate) 不是直接操作資料庫，而是操作一個「暫存區」 (Persistence Context)。
*   **狀態機**：Entity 有 Managed, Detached, Transient, Removed 等狀態。
*   **延遲寫入 (Write-behind)**：當你修改了一個 Managed Entity 的屬性，SQL `UPDATE` 不會馬上執行。Hibernate 會等到交易結束前 (Flush time)，比對快照 (Snapshot)，發現有變更才送出 SQL。這就是**髒檢查 (Dirty Checking)**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 交易邊界控制 (Transaction Boundaries)
*   **Service Layer as Boundary**: 交易應始於 Service 層，終於 Service 層。Controller 層不應觸碰交易邏輯，Repository 層則應只負責單純的 CRUD。
*   **Read-Only Optimization**: 對於唯讀操作，務必加上 `@Transactional(readOnly = true)`。
    *   **Why?** 這會告訴 Hibernate 不需要保留髒檢查用的快照 (Snapshot)，顯著降低記憶體消耗並提升效能。

### 2. 解決 N+1 問題的策略 (Strategies for N+1 Problem)
N+1 是 JPA 最常見的效能殺手（查詢 1 次主表，結果有 N 筆資料，又各自發動 N 次查詢去拿關聯資料）。
*   **Join Fetch**: 在 JPQL 中明確使用 `JOIN FETCH`。
*   **Entity Graph**: 使用 `@EntityGraph` 宣告需要一起撈取的關聯屬性，這是比寫 JPQL 更優雅的解法。
*   **Batch Size**: 設定 `spring.jpa.properties.hibernate.default_batch_fetch_size` (例如 100)，讓 Hibernate 在 Lazy Load 時一次抓取多筆 ID，將 N+1 變成 (N/100)+1。

### 3. DTO Projection (DTO 投影)
*   **只拿需要的欄位**：不要總是把整個 Entity 撈出來（包含所有關聯）。如果只是要列表顯示，定義一個 Java Record 或 Interface (Projection)，讓 JPA 只生成 `SELECT col1, col2` 的 SQL。這能避開大部分 Lazy Loading 與序列化問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 內部呼叫失效 (The Self-Invocation Trap)
*   **Anti-pattern**: 在同一個 Service 類別中，由 `methodA()` (無交易) 呼叫 `methodB()` (有 `@Transactional`)。
*   **Consequence**: `methodB` 的交易設定完全無效，發生例外也不會回滾。
*   **Fix**: 將 `methodB` 移到另一個 Service，或注入 `Self` (不推薦)，或重構架構。

### 2. 長時間交易 (Long-Running Transactions)
*   **Anti-pattern**: 在 `@Transactional` 方法中執行耗時的 IO 操作（如呼叫外部 API、發送 Email、處理大型檔案）。
*   **Consequence**: 資料庫連線 (Connection) 會被佔用直到方法結束。在高併發下，DB Connection Pool 會迅速耗盡，導致系統癱瘓。
*   **Fix**: 將非 DB 操作移出交易範圍。先做完 IO，再開交易寫入 DB。

### 3. Open Session In View (OSIV) 的兩難
*   **Scenario**: Spring Boot 預設開啟 `spring.jpa.open-in-view=true`。這讓你在 Controller 或 View 層還能讀取 Lazy Loading 的屬性。
*   **Pitfall**: 資料庫連線從 Request 開始就一直被佔用，直到 Response 寫回才釋放。這延長了 Connection 持有時間，吞吐量大減。
*   **Recommendation**: 在高流量系統中，設定 `spring.jpa.open-in-view=false`。強迫自己在 Service 層就組裝好所有需要的資料 (使用 DTO 或 Fetch Join)，避免在 View 層發生 `LazyInitializationException`。

### 4. 吞掉例外導致無法回滾 (Swallowing Exceptions)
*   **Anti-pattern**:
    ```java
    @Transactional
    public void doSomething() {
        try {
            repository.save(data);
            throw new RuntimeException("Error");
        } catch (Exception e) {
            log.error("Error", e);
            // 這裡沒有 re-throw，Spring 認為方法正常結束，因此 Commit！
        }
    }
    ```
*   **Fix**: 必須 `throw e`，或者手動呼叫 `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()`。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist for Transaction/JPA
在提交程式碼前，請依序檢查：

- [ ] **交易邊界**：是否在 Service 層級定義 `@Transactional`？
- [ ] **唯讀優化**：純查詢的方法是否標註了 `@Transactional(readOnly = true)`？
- [ ] **內部呼叫**：是否有 `this.method()` 呼叫了帶有交易註解的方法？(若有，需重構)
- [ ] **N+1 檢核**：
    - [ ] 是否在迴圈中呼叫 Repository 方法？
    - [ ] 關聯物件 (OneToMany, ManyToOne) 是否使用了 `FetchType.LAZY` (預設是 EAGER 的要小心)？
    - [ ] 列表查詢是否使用了 `@EntityGraph` 或 `JOIN FETCH`？
- [ ] **外部 IO**：交易區塊內是否包含 HTTP 請求或耗時運算？(應移出交易外)
- [ ] **例外處理**：`try-catch` 區塊內是否正確拋出例外以觸發 Rollback？
- [ ] **OSIV**：如果專案關閉了 OSIV，是否確認所有 Lazy 屬性都在 Service 層初始化完畢？

### Debugging Workflow: N+1 Detection
如何驗證是否存在 N+1 問題？

1.  **開啟 SQL Log**: 設定 `spring.jpa.show-sql=true` 與 `spring.jpa.properties.hibernate.format_sql=true`。
2.  **觀察 Log**: 執行一次 API 請求。
3.  **計數**: 看到一條 `SELECT ... FROM main_table`，隨後跟著一堆 `SELECT ... FROM child_table WHERE id = ?`？
4.  **判定**: 如果 child_table 的查詢次數隨著資料量增加，這就是 N+1。

---

## Real-world examples｜實戰案例

### Example 1: 修正內部呼叫 (Fixing Self-Invocation)

**❌ Bad (Transaction ignored):**
```java
@Service
public class OrderService {
    
    public void processOrder(OrderDto dto) {
        // 驗證邏輯...
        saveOrder(dto); // 這裡呼叫的是 this.saveOrder，繞過了 Proxy
    }

    @Transactional // 這裡的設定無效！
    public void saveOrder(OrderDto dto) {
        orderRepository.save(dto.toEntity());
    }
}
```

**✅ Good (Refactored):**
```java
@Service
public class OrderService {
    private final OrderRepositoryRepo repo;

    // 方法 1: 直接在入口處開交易 (最常見)
    @Transactional
    public void processOrder(OrderDto dto) {
        // 驗證邏輯...
        repo.save(dto.toEntity());
    }
}
// 或者 方法 2: 拆分 Service (當邏輯複雜時)
```

### Example 2: 解決 N+1 問題 (Solving N+1 with EntityGraph)

假設 `Author` 與 `Book` 是 1:N 關係。

**❌ Bad (Causes N+1):**
```java
// Repository
List<Author> findAll();

// Service
@Transactional(readOnly = true)
public List<AuthorDto> getAuthors() {
    List<Author> authors = authorRepository.findAll(); // 1 query
    return authors.stream().map(author -> {
        // 這裡會觸發 Lazy Loading，每有一個作者就多發一次 SQL 查書
        return new AuthorDto(author.getName(), author.getBooks().size()); 
    }).toList();
}
```

**✅ Good (Using EntityGraph):**
```java
// Repository
public interface AuthorRepository extends JpaRepository<Author, Long> {
    
    // 告訴 JPA 在查詢 Author 時，順便把 books 屬性抓出來
    @EntityGraph(attributePaths = {"books"})
    List<Author> findAll();
}

// Service 程式碼不用改，但 SQL 只會發出一條含有 LEFT JOIN 的查詢
```

### Example 3: 避免長交易 (Avoiding Long Transaction)

**❌ Bad (DB Connection held during external API call):**
```java
@Transactional
public void registerUser(UserDto dto) {
    User user = repo.save(dto.toEntity()); // DB Lock/Connection start
    
    // 外部 API 呼叫，可能耗時 3-5 秒
    emailService.sendWelcomeEmail(user.getEmail()); 
    paymentService.createWallet(user.getId());
    
    user.setStatus(Status.ACTIVE);
    repo.save(user); // Commit
}
```

**✅ Good (Narrow Transaction Scope):**
```java
// 不在最外層加 @Transactional
public void registerUser(UserDto dto) {
    // 1. 快速交易：先寫入 DB
    User user = userService.createUser(dto); 
    
    // 2. 耗時操作：不佔用 DB Connection
    emailService.sendWelcomeEmail(user.getEmail());
    paymentService.createWallet(user.getId());
    
    // 3. 快速交易：更新狀態
    userService.activateUser(user.getId());
}
```