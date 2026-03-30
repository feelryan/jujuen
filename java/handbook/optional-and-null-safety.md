# Optional 與 Null 安全實務 / Optional and Null Safety Practices

## Mental model｜心智模型

在 Java 中，`Optional` 的本質並不是用來「消滅所有的 `null`」，而是一種**語意表達工具（Semantic Tool）**。它的核心心智模型是：「明確地向 API 呼叫者宣告，這個操作的結果可能不存在，且『不存在』是一個合理、預期內的狀態」。

In Java, the essence of `Optional` is not to "eliminate all `null`s," but rather to serve as a **semantic tool**. Its core mental model is: "Explicitly declaring to the API caller that the result of this operation might be absent, and that 'absence' is a valid, expected state."

將 `Optional` 想像成一個「可能裝有物品的物流箱」。身為收件人，你不能預設箱子裡一定有東西，你必須先檢查箱子（或提供備用方案）才能取出內容物。然而，這個箱子本身也是一個 Java 物件，它會佔用記憶體（Heap memory），也會增加垃圾回收（GC）的負擔。因此，我們只在「邊界（Boundaries）」使用它，而不是在系統內部到處傳遞空箱子。

Think of `Optional` as a "delivery box that might contain an item." As the recipient, you cannot assume the box is full; you must check it (or provide a fallback) before extracting the contents. However, this box itself is a Java object—it consumes heap memory and adds overhead to Garbage Collection (GC). Therefore, we only use it at "boundaries," rather than passing empty boxes everywhere inside the system.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 僅作為方法的返回型別 / Use exclusively as method return types
最標準的用法是將 `Optional` 用於可能找不到結果的查詢方法（例如資料庫查詢、快取讀取）。這強迫呼叫者必須處理「無值」的情況。
The most standard use case is applying `Optional` to query methods where a result might not be found (e.g., database queries, cache lookups). This forces the caller to handle the "no value" scenario.

```java
// Good Practice
public Optional<User> findUserById(String userId) { ... }
```

### 2. 善用函數式鏈式呼叫 / Leverage functional chaining
不要把 `Optional` 當作傳統的 `if-else` 來寫。應該善用 `.map()`、`.flatMap()` 和 `.filter()` 來轉換資料，這樣可以保持程式碼的流暢與安全。
Do not write `Optional` like traditional `if-else` statements. Leverage `.map()`, `.flatMap()`, and `.filter()` to transform data, keeping the code fluent and safe.

```java
// Good Practice: Extracting a user's city if the user and address exist
String city = userRepository.findById(userId)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown City");
```

### 3. 針對基本型別使用特化版本 / Use primitive specializations
為了避免自動裝箱（Auto-boxing）帶來的效能損耗，當你需要回傳 `int`、`long` 或 `double` 的 Optional 時，請使用 `OptionalInt`、`OptionalLong` 或 `OptionalDouble`。
To avoid the performance overhead of auto-boxing, when you need to return an Optional of `int`, `long`, or `double`, use `OptionalInt`, `OptionalLong`, or `OptionalDouble`.

```java
// Good Practice
public OptionalInt findMaxScore(List<Integer> scores) { ... }
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 致命陷阱：`orElse()` vs `orElseGet()` 的效能差異 / Fatal Trap: `orElse()` vs `orElseGet()` performance difference
這是真實專案中最常見的效能地雷。`orElse(value)` 是**積極求值（Eager evaluation）**，無論 Optional 內是否有值，括號內的方法都會被執行。如果裡面是一個耗時操作（如 DB 查詢或建立新物件），將造成嚴重的效能浪費。請改用 `orElseGet(Supplier)` 進行**延遲求值（Lazy evaluation）**。
This is the most common performance landmine in real-world projects. `orElse(value)` is **eagerly evaluated**; the method inside the parentheses is executed regardless of whether the Optional is empty or not. If it contains an expensive operation (like a DB query or new object creation), it causes severe performance waste. Use `orElseGet(Supplier)` for **lazy evaluation** instead.

```java
// Anti-pattern: createDefaultUser() is ALWAYS called!
User user = findUserById(id).orElse(createDefaultUser()); 

// Good Practice: createDefaultUser() is ONLY called if the user is not found.
User user = findUserById(id).orElseGet(() -> createDefaultUser());
```

### 2. 將 Optional 作為類別屬性或方法參數 / Using Optional as class fields or method parameters
`Optional` 沒有實作 `Serializable` 介面，作為實體類別（Entity/DTO）的屬性會導致序列化失敗，且浪費記憶體。此外，將其作為方法參數會強迫呼叫者包裝引數，讓 API 變得囉嗦。
`Optional` does not implement the `Serializable` interface. Using it as a field in Entity/DTO classes causes serialization failures and wastes memory. Furthermore, using it as a method parameter forces callers to wrap arguments, making the API clunky.

```java
// Anti-pattern
public class User {
    private Optional<String> email; // Bad: Not serializable, memory overhead
}
public void updateEmail(Optional<String> email) { ... } // Bad: Clunky API

// Good Practice
public class User {
    private String email; // Use null internally
    public Optional<String> getEmail() { return Optional.ofNullable(email); } // Expose safely
}
public void updateEmail(String email) { ... } // Caller passes null or actual value
```

### 3. 回傳 Optional 的集合 / Returning an Optional of a Collection
永遠不要回傳 `Optional<List<T>>` 或 `Optional<Map<K, V>>`。集合框架本身已經有「空狀態」的概念（即空集合）。
Never return `Optional<List<T>>` or `Optional<Map<K, V>>`. The Collections framework already has a concept of an "empty state" (i.e., an empty collection).

```java
// Anti-pattern
public Optional<List<User>> findUsersByRole(String role) { ... }

// Good Practice
public List<User> findUsersByRole(String role) { 
    return users.isEmpty() ? Collections.emptyList() : users; 
}
```

### 4. 呼叫 `.get()` 前不檢查 / Calling `.get()` without checking
直接呼叫 `.get()` 如果遇到空值，會拋出 `NoSuchElementException`，這跟拋出 `NullPointerException` 一樣糟糕，完全失去了使用 Optional 的意義。
Calling `.get()` directly on an empty Optional throws a `NoSuchElementException`, which is just as bad as a `NullPointerException`, completely defeating the purpose of using Optional.

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或撰寫程式碼時，請使用以下清單驗證 Optional 的使用是否正確：
Use the following checklist during Code Review or coding to verify the correct usage of Optional:

- [ ] **邊界驗證 (Boundary Check):** `Optional` 是否僅用於方法的 `return type`？（沒有出現在 Field、Constructor 參數或 Method 參數中）。 / Is `Optional` used strictly as a method `return type`? (Not in fields, constructor parameters, or method parameters).
- [ ] **集合驗證 (Collection Check):** 是否避免了回傳 `Optional<List/Set/Map>`？（請改回傳 `Collections.emptyList()`）。 / Did I avoid returning `Optional<List/Set/Map>`? (Return `Collections.emptyList()` instead).
- [ ] **效能驗證 (Performance Check):** 備用方案如果是耗時操作或需要 `new` 新物件，是否已經使用了 `.orElseGet()` 而不是 `.orElse()`？ / If the fallback is an expensive operation or creates a new object, did I use `.orElseGet()` instead of `.orElse()`?
- [ ] **安全驗證 (Safety Check):** 程式碼中是否完全移除了對 `.get()` 的直接呼叫？（改用 `.orElseThrow()` 語意更清晰）。 / Are all direct calls to `.get()` completely removed from the code? (Use `.orElseThrow()` for clearer semantics).
- [ ] **巢狀驗證 (Nesting Check):** 是否避免了 `Optional<Optional<T>>` 的出現？（如果出現，請使用 `.flatMap()` 攤平）。 / Did I avoid `Optional<Optional<T>>`? (If it occurs, use `.flatMap()` to flatten it).

---

## Real-world examples｜實戰案例

### 案例 1：重構舊有的 Null 檢查地獄 / Scenario 1: Refactoring legacy Null-check hell

在真實的業務邏輯中，我們經常需要深入物件圖（Object Graph）獲取資料。
In real-world business logic, we often need to traverse deep into an Object Graph to fetch data.

**Before (Anti-pattern: 容易漏掉 null check 導致 NPE)**
```java
public String getCustomerDiscountCode(String customerId) {
    Customer customer = repository.findById(customerId);
    if (customer != null) {
        MemberProfile profile = customer.getMemberProfile();
        if (profile != null) {
            DiscountCode code = profile.getDiscountCode();
            if (code != null) {
                return code.getValue();
            }
        }
    }
    return "DEFAULT_CODE";
}
```

**After (Best Practice: 乾淨、安全且具備聲明性)**
```java
public String getCustomerDiscountCode(String customerId) {
    return repository.findOptionalById(customerId) // Returns Optional<Customer>
        .map(Customer::getMemberProfile)           // Returns Optional<MemberProfile>
        .map(MemberProfile::getDiscountCode)       // Returns Optional<DiscountCode>
        .map(DiscountCode::getValue)               // Returns Optional<String>
        .orElse("DEFAULT_CODE");                   // Safe fallback
}
```

### 案例 2：拋出業務異常 / Scenario 2: Throwing business exceptions

當找不到資料時，我們通常需要拋出特定的業務異常交給全域異常處理器（Global Exception Handler）。
When data is not found, we typically need to throw a specific business exception to be handled by a Global Exception Handler.

```java
// Good Practice: Using orElseThrow with method reference
public Order processOrder(String orderId) {
    Order order = orderRepository.findById(orderId)
        .orElseThrow(() -> new OrderNotFoundException("Order not found: " + orderId));
        
    order.setStatus(OrderStatus.PROCESSED);
    return orderRepository.save(order);
}
```