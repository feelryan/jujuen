# REST API 設計規範與全域異常處理 / REST API Design Standards & Global Exception Handling

## Mental model｜心智模型

### 1. The "Traffic Cop" at the Edge (邊界上的交通指揮)
將全域異常處理（Global Exception Handling）想像成應用程式邊界的「最後一道防線」。當 Service 層或 Repository 層拋出異常（Exception）時，它們不應直接暴露給客戶端。`@ControllerAdvice` 就像是一個交通指揮官，攔截所有試圖衝出應用程式的異常，將其「翻譯」成客戶端聽得懂的標準 HTTP 回應。

Think of Global Exception Handling as the "last line of defense" at the application boundary. When exceptions occur in the Service or Repository layers, they shouldn't leak directly to the client. `@ControllerAdvice` acts as a traffic cop, intercepting all bubbling exceptions and "translating" them into standardized HTTP responses that clients can understand.

### 2. The Contract (契約精神)
REST API 是一種契約。成功的請求（2xx）有定義好的格式，失敗的請求（4xx, 5xx）也必須有定義好的格式。如果前端開發者需要針對不同的 API endpoint 寫不同的 `try-catch` 或錯誤解析邏輯，這就是後端設計的失敗。

REST API is a contract. Successful requests (2xx) have a defined format, and failed requests (4xx, 5xx) must also have a strictly defined format. If frontend developers need to write different error parsing logic for different endpoints, the backend design has failed.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Adopt RFC 7807 (Problem Details for HTTP APIs)
Spring Boot 3 已經原生支援 RFC 7807。這是 IETF 定義的標準錯誤回應格式，能有效解決「每個專案都發明自己的錯誤格式」的問題。

Spring Boot 3 natively supports RFC 7807. This is the IETF standard for error responses, solving the "every project invents its own error format" problem.

*   **Type:** URI reference identifying the problem type.
*   **Title:** Short summary of the problem.
*   **Status:** The HTTP status code.
*   **Detail:** Human-readable explanation specific to this occurrence.
*   **Instance:** URI reference to the specific occurrence of the problem.

### 2. The "Unified Envelope" Pattern (統一封裝模式)
雖然 RFC 7807 是標準，但在許多企業內部系統中，仍流行使用自定義的統一封裝（Envelope）。關鍵在於**一致性**。

While RFC 7807 is the standard, the "Unified Envelope" pattern is still prevalent in many enterprise systems. The key is **consistency**.

```json
{
  "code": "USR-001",
  "message": "User not found",
  "timestamp": "2023-10-27T10:00:00Z",
  "data": null
}
```

### 3. Layered Exception Translation (分層異常轉換)
不要讓底層異常（如 `SQLException`）直接穿透到 Controller。
*   **Repository Layer:** Catch database errors, wrap in generic DataAccess exceptions.
*   **Service Layer:** Throw semantic `BusinessException` (e.g., `InsufficientBalanceException`).
*   **Controller Layer:** Focus on validation (`@Valid`) and request mapping.
*   **Global Handler:** Map `BusinessException` to 4xx, and unhandled exceptions to 500.

### 4. Validation First (優先驗證)
善用 Bean Validation (Hibernate Validator)。不要在 Controller 寫大量的 `if (name == null)`。使用 `@NotNull`, `@Size`, `@Email` 等註解，並在 Global Handler 中統一處理 `MethodArgumentNotValidException`。

Leverage Bean Validation. Avoid writing massive `if` checks in Controllers. Use annotations and handle `MethodArgumentNotValidException` centrally.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Leaking Stack Traces (洩漏堆疊追蹤)
**The Cardinal Sin.** 永遠不要在生產環境的 API 回應中包含 `e.printStackTrace()` 或完整的 stack trace。這會暴露系統架構、套件版本，成為駭客攻擊的指引。

**The Cardinal Sin.** Never include stack traces in production API responses. It exposes system architecture and library versions, serving as a guide for attackers.

### 2. Returning 200 OK for Errors (錯誤卻回傳 200)
這是一種常見但糟糕的做法（通常受早期 SOAP 或某些 GraphQL 實作影響）。如果資源找不到，回傳 `404`；如果權限不足，回傳 `403`。不要回傳 `200 OK` 然後在 body 裡寫 `{"error": "true"}`。這會破壞 HTTP 協定的語意，讓監控工具（如 Prometheus/Grafana）無法正確統計錯誤率。

Do not return `200 OK` with `{"error": "true"}` in the body. It breaks HTTP semantics and prevents monitoring tools from correctly tracking error rates. Use appropriate status codes (404, 403, etc.).

### 3. Catch-All without Logging (吞掉異常且不記錄)
```java
@ExceptionHandler(Exception.class)
public ResponseEntity<Object> handleAll(Exception ex) {
    return ResponseEntity.internalServerError().build(); // BAD: No log!
}
```
如果發生未知錯誤（500），必須記錄 ERROR 等級的 Log，否則你永遠不知道生產環境發生了什麼。

If an unknown error (500) occurs, it MUST be logged at the ERROR level. Otherwise, you'll be flying blind in production.

### 4. Magic Strings & Codes (魔術字串與代碼)
不要在程式碼中散落 `"User not found"` 或 `"ERR-999"`。請使用 Enum 或常數類別來管理錯誤代碼與訊息，便於維護與國際化（i18n）。

Avoid scattering hardcoded strings. Use Enums or Constant classes to manage error codes and messages for easier maintenance and i18n.

---

## Checklists & workflows｜檢查清單與流程

### Design Phase (設計階段)
- [ ] **Define Format:** 決定使用 RFC 7807 還是自定義 Envelope？（全團隊統一）。
- [ ] **Status Code Mapping:** 定義業務錯誤代碼（Business Error Code）與 HTTP Status Code 的對應表。
- [ ] **Validation Strategy:** 確定哪些驗證在 DTO 層（@Valid），哪些在 Service 層（邏輯驗證）。

### Implementation Phase (實作階段)
- [ ] **Create Base Exception:** 建立一個 `BaseException` 或 `BusinessException` 繼承 `RuntimeException`。
- [ ] **Setup @ControllerAdvice:** 建立全域處理器類別。
- [ ] **Handle Specific Exceptions:**
    - [ ] `MethodArgumentNotValidException` (Validation failed -> 400)
    - [ ] `HttpMessageNotReadableException` (JSON parse error -> 400)
    - [ ] `AccessDeniedException` (Security -> 403)
    - [ ] `NoResourceFoundException` (Spring Boot 3.2+ -> 404)
    - [ ] Custom `BusinessException` (Domain logic -> 400/404/409)
- [ ] **Handle Fallback:** 實作 `Exception.class` 的處理器（Catch-all -> 500），並確保有 Log。

### Security & Production (安全與生產環境)
- [ ] **Hide Internals:** 確認 `server.error.include-stacktrace` 在生產環境設為 `never`。
- [ ] **Sanitize Messages:** 確保回傳給前端的錯誤訊息不包含敏感資料（如 SQL 語法、資料庫 IP）。

---

## Real-world examples｜實戰案例

### 1. Modern Spring Boot 3 Way (Using ProblemDetail)
這是目前最推薦的標準做法，利用 Spring Boot 3 的 `ProblemDetail` API。

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // 1. Handle Custom Business Logic Errors
    @ExceptionHandler(BusinessException.class)
    public ProblemDetail handleBusinessException(BusinessException ex) {
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(
            ex.getHttpStatus(), // e.g., 404 or 409
            ex.getMessage()
        );
        problemDetail.setTitle("Business Rule Violation");
        problemDetail.setProperty("errorCode", ex.getErrorCode()); // Custom extension
        problemDetail.setProperty("timestamp", Instant.now());
        
        return problemDetail;
    }

    // 2. Handle Validation Errors (Override standard Spring handler)
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex, HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Validation Failed");
        problemDetail.setTitle("Invalid Request Content");
        
        // Collect all validation errors
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .toList();
        
        problemDetail.setProperty("errors", errors);
        
        return createResponseEntity(problemDetail, headers, HttpStatus.BAD_REQUEST, request);
    }

    // 3. Catch-All for Unexpected Errors (500)
    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGlobalException(Exception ex) {
        log.error("Unexpected error occurred: ", ex); // CRITICAL: Log the stack trace internally
        
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR, 
            "An internal server error occurred. Please contact support."
        );
        problemDetail.setTitle("Internal Server Error");
        return problemDetail;
    }
}
```

### 2. Custom Exception Structure (自定義異常結構)
建立清晰的異常繼承體系，讓 Service 層的程式碼更乾淨。

```java
// Base class
@Getter
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode; // Enum
    private final HttpStatus httpStatus;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.httpStatus = errorCode.getHttpStatus();
    }
}

// Usage in Service
public UserDTO getUser(Long id) {
    return userRepository.findById(id)
        .map(userMapper::toDTO)
        .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
}
```

### 3. The JSON Response (Client View)
當上述 `User not found` 發生時，前端會收到標準的 RFC 7807 回應：

```json
{
  "type": "about:blank",
  "title": "Business Rule Violation",
  "status": 404,
  "detail": "User with ID 123 not found",
  "instance": "/api/users/123",
  "errorCode": "USR_004",
  "timestamp": "2023-10-27T14:30:00Z"
}
```