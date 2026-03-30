# 異常處理策略與反模式 / Exception Handling Strategies and Anti-patterns

## Mental model｜心智模型

在 Java 中，異常處理不僅僅是 `try-catch` 語法，它是系統架構中「錯誤邊界 (Error Boundaries)」與「控制流 (Control Flow)」的核心設計。
In Java, exception handling is not just about `try-catch` syntax; it is a core design of "Error Boundaries" and "Control Flow" in system architecture.

一個成熟的工程師看待異常的心智模型應包含以下三個維度：
A mature engineer's mental model for exceptions should include the following three dimensions:

1. **異常是為了「非預期狀況」而生 (Exceptions are for exceptional conditions)**：
   異常不應該被用來處理正常的業務邏輯分支。如果一個狀況是可以預見且經常發生的（例如：找不到使用者、密碼錯誤），考慮使用 `Optional`、`Either` 模式或特定的回傳值，而不是拋出異常。
   Exceptions should not be used to handle normal business logic branches. If a condition is foreseeable and happens frequently (e.g., user not found, wrong password), consider using `Optional`, `Either` patterns, or specific return values instead of throwing exceptions.

2. **Checked vs Unchecked 的現代取捨 (The modern trade-off of Checked vs Unchecked)**：
   Java 是少數強制區分 Checked Exception 的語言。然而，現代 Java 開發（特別是結合 Spring Boot 與 Streams API）強烈傾向於 **預設使用 Unchecked Exceptions (RuntimeException)**。Checked Exceptions 破壞了封裝性，且與 Lambda 表達式極度不合。
   Java is one of the few languages that enforces Checked Exceptions. However, modern Java development (especially with Spring Boot and Streams API) strongly leans towards **defaulting to Unchecked Exceptions (RuntimeException)**. Checked Exceptions break encapsulation and are highly incompatible with Lambda expressions.

3. **錯誤處理的責任轉移 (Responsibility transfer of error handling)**：
   當你捕捉一個異常時，你必須問自己：「我能在這裡修復它嗎？」如果不行，就應該將其包裝並往上拋，交給「全域異常處理器 (Global Exception Handler)」來統一決定如何記錄日誌與回應客戶端。
   When you catch an exception, you must ask yourself: "Can I fix it here?" If not, you should wrap it and throw it upwards, letting the "Global Exception Handler" uniformly decide how to log it and respond to the client.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用 Unchecked Exceptions (Prefer Unchecked Exceptions)
在定義自訂異常時，繼承 `RuntimeException`。這能保持方法簽章的乾淨，並讓呼叫者自行決定是否要攔截。
When defining custom exceptions, extend `RuntimeException`. This keeps method signatures clean and lets the caller decide whether to intercept them.

```java
// Good: 繼承 RuntimeException
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}
```

### 2. 全域異常攔截設計 (Global Exception Handling Design)
在 Web 應用（如 Spring Boot）中，不要在每個 Controller 寫 `try-catch`。使用 `@RestControllerAdvice` 集中處理，並轉換為標準化的 API 錯誤格式（例如 RFC 7807 Problem Details）。
In Web applications (like Spring Boot), do not write `try-catch` in every Controller. Use `@RestControllerAdvice` to handle them centrally and convert them into standardized API error formats (e.g., RFC 7807 Problem Details).

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ProblemDetail handleUserNotFound(UserNotFoundException ex) {
        // 將業務異常轉換為 404 Not Found
        // Converts business exception to 404 Not Found
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problemDetail.setTitle("User Not Found");
        return problemDetail;
    }
}
```

### 3. Fail-Fast 提早失敗 (Fail-Fast Principle)
在方法的開頭立即驗證輸入參數，遇到無效狀態時立刻拋出 `IllegalArgumentException` 或 `NullPointerException`，避免錯誤狀態在系統深處才引爆。
Validate input parameters immediately at the beginning of a method. Throw `IllegalArgumentException` or `NullPointerException` right away when encountering invalid states, preventing the error from detonating deep within the system.

```java
public void processOrder(Order order) {
    Objects.requireNonNull(order, "Order cannot be null");
    if (order.getItems().isEmpty()) {
        throw new IllegalArgumentException("Order must contain at least one item");
    }
    // ... business logic
}
```

### 4. 保留根本原因 (Preserve the Root Cause)
當捕捉並重新拋出異常時，**永遠**要把原始異常當作 `cause` 傳遞進去，否則你會失去最關鍵的 Stack Trace。
When catching and rethrowing an exception, **always** pass the original exception as the `cause`. Otherwise, you will lose the most critical Stack Trace.

```java
// Good: 保留原始異常 e / Preserves original exception e
try {
    Files.readAllLines(Path.of("config.txt"));
} catch (IOException e) {
    throw new ConfigurationLoadException("Failed to load config file", e);
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 吞沒異常 (Swallowing Exceptions)
**反模式**：捕捉了異常卻什麼都不做，或者只印出一行無用的日誌，導致系統狀態不一致且無法排查。
**Anti-pattern**: Catching an exception but doing nothing, or just printing a useless log line, leading to inconsistent system states and impossible troubleshooting.

```java
// Bad: 吞沒異常 / Swallowing exception
try {
    processPayment();
} catch (Exception e) {
    // 什麼都不做，或者只寫 e.printStackTrace()
    // Doing nothing, or just e.printStackTrace()
}
```

### 2. 日誌與拋出並行 (Log and Throw)
**反模式**：在 catch 區塊中記錄了錯誤日誌，然後又把異常拋出。這會導致同一個錯誤在日誌系統中被記錄多次，造成雜訊。
**Anti-pattern**: Logging the error in the catch block and then rethrowing the exception. This causes the same error to be logged multiple times in the logging system, creating noise.

```java
// Bad: 導致重複日誌 / Causes duplicate logs
try {
    callExternalApi();
} catch (ApiException e) {
    log.error("API call failed", e); // 第一處日誌 / First log
    throw e; // 上層攔截到又會再 log 一次 / Upper layer will log again
}
```
**解法 (Solution)**：要麼處理並記錄它（Log and Handle），要麼直接往上拋（Just Throw）。

### 3. 用異常控制業務流程 (Exceptions for Control Flow)
**反模式**：利用拋出異常來作為 `if-else` 的替代品（例如：用 `NumberFormatException` 來判斷字串是否為數字）。異常的實例化（特別是填寫 Stack Trace）在 JVM 中是非常昂貴的操作。
**Anti-pattern**: Using exceptions as a substitute for `if-else` (e.g., using `NumberFormatException` to check if a string is numeric). Instantiating exceptions (especially filling the Stack Trace) is a very expensive operation in the JVM.

### 4. 拋出過於寬泛的異常 (Throwing Generic Exceptions)
**反模式**：方法簽章宣告 `throws Exception`，或直接拋出 `new RuntimeException("error")`。這讓呼叫者無法針對特定的錯誤進行精細的處理。
**Anti-pattern**: Method signatures declaring `throws Exception`, or directly throwing `new RuntimeException("error")`. This prevents the caller from handling specific errors granularly.

---

## Checklists & workflows｜檢查清單與流程

在 code review 或撰寫異常處理邏輯時，請使用以下檢查清單：
Use the following checklist during code reviews or when writing exception handling logic:

- [ ] **是否吞沒了異常？ (Are exceptions swallowed?)**
  確認所有的 `catch` 區塊都有實質的處理邏輯。如果故意忽略，是否加上了明確的註解說明原因？
  Ensure all `catch` blocks have substantive handling logic. If intentionally ignored, is there a clear comment explaining why?
- [ ] **是否保留了 Root Cause？ (Is the Root Cause preserved?)**
  檢查 `throw new CustomException("msg", e)` 中是否確實傳入了原始異常 `e`。
  Check if the original exception `e` is actually passed into `throw new CustomException("msg", e)`.
- [ ] **是否避免了 Log and Throw？ (Is 'Log and Throw' avoided?)**
  確認沒有在同一個 catch block 裡同時 `log.error` 並且 `throw`。
  Ensure there is no simultaneous `log.error` and `throw` in the same catch block.
- [ ] **異常訊息是否包含上下文？ (Does the exception message contain context?)**
  錯誤訊息是否具備可操作性？（例如：`"User 12345 not found"` 優於 `"User not found"`）。
  Is the error message actionable? (e.g., `"User 12345 not found"` is better than `"User not found"`).
- [ ] **是否洩漏了敏感資訊？ (Are sensitive details leaked?)**
  確保全域異常處理器沒有將資料庫 SQL 語法或完整的 Stack Trace 直接回傳給外部 API 客戶端。
  Ensure the global exception handler does not return database SQL queries or full Stack Traces directly to external API clients.

---

## Real-world examples｜實戰案例

### 案例 1：在 Streams API 中處理 Checked Exception (Handling Checked Exceptions in Streams API)
**情境**：在 `Stream.map()` 中呼叫會拋出 `IOException` 的方法。
**Scenario**: Calling a method that throws `IOException` inside `Stream.map()`.

```java
// 假設我們有一個拋出 Checked Exception 的方法
// Assume we have a method throwing a Checked Exception
public String readFile(Path path) throws IOException { ... }

// Bad: 程式碼變得極度冗長且難以閱讀
// Bad: Code becomes extremely verbose and hard to read
List<String> contents = paths.stream()
    .map(path -> {
        try {
            return readFile(path);
        } catch (IOException e) {
            throw new RuntimeException(e); // 被迫在這裡包裝 / Forced to wrap here
        }
    })
    .toList();

// Good: 實作一個 Wrapper 介面或使用第三方庫 (如 Vavr)
// Good: Implement a Wrapper interface or use a 3rd-party lib (like Vavr)
List<String> contents = paths.stream()
    .map(Unchecked.function(this::readFile)) // 隱藏 try-catch 細節 / Hides try-catch details
    .toList();
```

### 案例 2：微服務中的重試機制與自訂異常 (Retry Mechanism and Custom Exceptions in Microservices)
**情境**：呼叫外部金流 API，區分「可重試的網路錯誤」與「不可重試的業務錯誤」。
**Scenario**: Calling an external payment API, distinguishing between "retryable network errors" and "non-retryable business errors".

```java
public PaymentResponse charge(PaymentRequest request) {
    try {
        return httpClient.post("/charge", request);
    } catch (SocketTimeoutException e) {
        // 網路超時：拋出特定的重試異常，讓上層 (如 Spring Retry) 進行重試
        // Network timeout: Throw a specific retryable exception for upper layers (e.g., Spring Retry) to retry
        throw new RetryablePaymentException("Payment API timeout, safe to retry", e);
    } catch (HttpClientErrorException.BadRequest e) {
        // 400 Bad Request：客戶端資料錯誤，重試也沒用，拋出致命異常
        // 400 Bad Request: Client data error, retrying is useless, throw fatal exception
        throw new FatalPaymentException("Invalid payment request data", e);
    }
}
```