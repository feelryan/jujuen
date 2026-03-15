# Spring Security 實作檢核清單 / Spring Security Implementation Checklist

## Mental model｜心智模型

Spring Security 的核心並非魔法，而是一連串的 **Servlet Filters（過濾器鏈）**。理解它的關鍵在於將其視為機場的安檢流程，而非單一的守門員。

The core of Spring Security is not magic; it's a chain of **Servlet Filters**. The key to understanding it is to visualize it as an airport security process, not a single gatekeeper.

1.  **The Filter Chain (安檢通道)**:
    *   請求進入應用程式前，必須通過 `SecurityFilterChain`。
    *   這是一系列有順序的過濾器（Filters），每個過濾器負責不同的職責（如：檢查 Header、驗證 Session、處理 CORS、防禦 CSRF）。
    *   **關鍵點**：一旦某個 Filter 拋出異常或拒絕請求，後續的 Controller 邏輯完全不會執行。

2.  **Authentication vs. Authorization (身分驗證 vs. 授權)**:
    *   **Authentication (Who are you?)**: 驗證你是誰。由 `AuthenticationManager` 負責。成功後，身分資訊會被存入 `SecurityContextHolder` (ThreadLocal)。
    *   **Authorization (What can you do?)**: 驗證你能做什麼。發生在 Authentication 之後，通常由 `FilterSecurityInterceptor` 或 Method Security 檢查 `SecurityContext` 中的權限 (Authorities)。

3.  **Stateless vs. Stateful (無狀態 vs. 有狀態)**:
    *   **Stateful (Session)**: 傳統 Web 應用。登入後 Server 建立 Session，Client 拿 Cookie。
    *   **Stateless (JWT)**: 現代前後端分離。Server 不存 Session，Client 拿 Token。**Spring Security 預設是 Stateful 的，實作 JWT 時必須明確關閉 Session Creation。**

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Configuration with Lambda DSL (使用 Lambda DSL 配置)
Spring Security 5.2+ (及 Spring Boot 3/Security 6) 強烈建議使用 Lambda DSL，這讓縮排更清晰，且避免了 `and()` 的混亂。

Use the Lambda DSL introduced in Spring Security 5.2+ (standard in Spring Boot 3). It improves readability and eliminates the confusion of chaining `and()`.

```java
// Recommended Style
http
    .csrf(csrf -> csrf.disable())
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/public/**").permitAll()
        .anyRequest().authenticated()
    );
```

### 2. Stateless Authentication (JWT) Setup (無狀態驗證設定)
對於 REST API，必須明確將 Session 策略設為 `STATELESS`，並確保 CSRF 被禁用（因為沒有 Session Cookie 需要保護）。

For REST APIs, explicitly set the session policy to `STATELESS` and disable CSRF (since there are no session cookies to protect).

*   **Session Management**: `SessionCreationPolicy.STATELESS`
*   **CSRF**: `disable()` (僅限非瀏覽器 Session 的 API 情境)
*   **Filter Placement**: 將自定義的 `JwtAuthenticationFilter` 放在 `UsernamePasswordAuthenticationFilter` **之前**。

### 3. Password Storage (密碼儲存)
永遠使用 `DelegatingPasswordEncoder`。這允許系統支援多種雜湊演算法（如 bcrypt, argon2），並能無縫遷移舊密碼。

Always use `DelegatingPasswordEncoder`. It supports multiple hashing algorithms (like bcrypt, argon2) and allows seamless migration of legacy passwords.

### 4. Method Level Security (方法層級安全)
對於細粒度的權限控制，優先使用 `@EnableMethodSecurity` (Spring Security 6) 取代舊的 `@EnableGlobalMethodSecurity`。

For fine-grained control, prefer `@EnableMethodSecurity` over the deprecated `@EnableGlobalMethodSecurity`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The CORS/CSRF Confusion (CORS 與 CSRF 的混淆)
*   **Pitfall**: 以為 `csrf().disable()` 就能解決跨域問題，或者在 Controller 層加了 `@CrossOrigin` 卻在 Security 層被擋下。
*   **Correction**:
    *   **CORS (Cross-Origin Resource Sharing)**: 瀏覽器的安全機制。必須在 Spring Security 中配置 `.cors()`，並提供 `CorsConfigurationSource` Bean，讓 OPTIONS pre-flight 請求能通過 Filter Chain。
    *   **CSRF (Cross-Site Request Forgery)**: 攻擊者利用使用者的 Session。如果是純 JWT (Stateless)，可以安全地 Disable；如果是 Session-based，絕對不能關。

### 2. Ignoring "Ignoring" (濫用 WebSecurityCustomizer)
*   **Pitfall**: 使用 `web.ignoring().requestMatchers(...)` 來放行靜態資源或公開 API。
*   **Consequence**: 這會完全繞過 Spring Security Filter Chain。這意味著沒有安全 Header (HSTS, X-Content-Type-Options) 且無法記錄存取日誌。
*   **Correction**: 應在 `SecurityFilterChain` 中使用 `.permitAll()`，讓請求走過 Filter Chain 但不要求驗證。僅對 CSS/JS/Images 等純靜態資源使用 `ignoring`。

### 3. Incorrect Filter Order (錯誤的 Filter 順序)
*   **Pitfall**: 自定義的 Auth Filter 順序錯誤，導致請求在進入自定義邏輯前就被預設的 `AnonymousAuthenticationFilter` 或 `AuthorizationFilter` 攔截。
*   **Correction**: 使用 `http.addFilterBefore(myFilter, UsernamePasswordAuthenticationFilter.class)` 確保在標準驗證前執行。

### 4. Improper Exception Handling (不當的異常處理)
*   **Pitfall**: 當 JWT 過期或無效時，API 回傳 HTML 錯誤頁面或 500 Internal Server Error。
*   **Correction**: 實作 `AuthenticationEntryPoint` (處理 401) 和 `AccessDeniedHandler` (處理 403)，確保回傳標準的 JSON 錯誤格式。

---

## Checklists & workflows｜檢查清單與流程

在將 Spring Security 部署到生產環境前，請執行以下檢核：

Before deploying Spring Security to production, perform the following checks:

### Configuration & Architecture
- [ ] **Session Policy**: 確認 API 專案已設定 `SessionCreationPolicy.STATELESS`。
- [ ] **CSRF**: 若是無狀態 API，確認已 Disable CSRF；若是 MVC 應用，確認 CSRF Token 機制運作正常。
- [ ] **CORS**: 已在 Spring Security 層級配置 CORS（非僅 Controller 層），且未在生產環境使用 `AllowedOrigins("*")` 搭配 `AllowCredentials(true)`。
- [ ] **Public Endpoints**: 確認 Actuator、Swagger UI、Login 等端點已正確配置 `permitAll()`。

### Authentication & Authorization
- [ ] **Password Encoding**: 確認使用 BCrypt 或 Argon2，且未儲存明文密碼。
- [ ] **Filter Order**: 確認 JWT Filter 位於 `UsernamePasswordAuthenticationFilter` 之前。
- [ ] **Role Prefix**: 確認資料庫中的角色名稱與配置匹配（Spring Security 預設需要 `ROLE_` 前綴，或需自定義 `GrantedAuthorityDefaults`）。
- [ ] **Method Security**: 若使用了 `@PreAuthorize`，確認 `@EnableMethodSecurity` 已啟用。

### Error Handling
- [ ] **401/403 Responses**: 驗證未登入 (401) 與權限不足 (403) 時，回傳的是前端可解析的 JSON 而非預設 HTML 頁面。
- [ ] **Exception Translation**: 確認 Filter 內拋出的異常能被 `AuthenticationEntryPoint` 捕獲。

---

## Real-world examples｜實戰案例

### 1. Standard Stateless API Configuration (Spring Boot 3+)

這是一個標準的 JWT 後端配置，涵蓋了 CORS、CSRF 禁用、Session 無狀態化以及異常處理。

This is a standard configuration for a JWT-based backend, covering CORS, disabling CSRF, stateless sessions, and exception handling.

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Enable @PreAuthorize
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final CustomAuthenticationEntryPoint customEntryPoint;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthFilter, 
                          CustomAuthenticationEntryPoint customEntryPoint) {
        this.jwtAuthFilter = jwtAuthFilter;
        this.customEntryPoint = customEntryPoint;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // 1. Disable CSRF for stateless APIs
            .csrf(AbstractHttpConfigurer::disable)
            
            // 2. Configure CORS (requires a CorsConfigurationSource bean)
            .cors(Customizer.withDefaults())
            
            // 3. Set Session management to stateless
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            
            // 4. Define authorization rules
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/public/**").permitAll() // Public endpoints
                .requestMatchers("/api/admin/**").hasRole("ADMIN")         // Role-based
                .anyRequest().authenticated()                              // All others require auth
            )
            
            // 5. Add JWT Filter before the standard authentication filter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            
            // 6. Custom Exception Handling for 401s
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(customEntryPoint)
            );

        return http.build();
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 2. Handling 401 Errors properly (JSON Response)

不要讓前端收到 Spring 預設的 HTML 登入頁面或空白的 403。

Do not let the frontend receive Spring's default HTML login page or a blank 403.

```java
@Component
public class CustomAuthenticationEntryPoint implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED); // 401
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        
        // Construct a meaningful JSON error
        String jsonPayload = String.format("{\"error\": \"Unauthorized\", \"message\": \"%s\"}", 
                                           authException.getMessage());
        
        response.getWriter().write(jsonPayload);
    }
}
```