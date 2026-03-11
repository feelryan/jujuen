# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，安全性（Security）往往是區分「能寫功能」與「能架構系統」的分水嶺。Spring Security 是 Java 生態系中最強大但也最複雜的框架之一。本章不只教你如何設定，更要深入其核心機制與現代化 OAuth2/OIDC 架構。

In the career of a Senior Software Engineer, security is often the dividing line between "implementing features" and "architecting systems." Spring Security is one of the most powerful yet complex frameworks in the Java ecosystem. This chapter goes beyond basic configuration to explore its core mechanisms and modern OAuth2/OIDC architecture.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **精通 Filter Chain 機制**：理解並能客製化 `SecurityFilterChain`，知道如何正確插入自定義過濾器（如 Rate Limiting 或 Audit Log）。
    **Master the Filter Chain Mechanism**: Understand and customize the `SecurityFilterChain`, knowing how to correctly insert custom filters (e.g., Rate Limiting or Audit Log).
2.  **實作 OAuth2/OIDC 架構**：在微服務環境中，正確區分 Resource Server 與 Client 的職責，並處理 JWT 的解析與權限映射（Authority Mapping）。
    **Implement OAuth2/OIDC Architecture**: Correctly distinguish the responsibilities of Resource Servers and Clients in a microservices environment, and handle JWT parsing and Authority Mapping.
3.  **防禦常見資安漏洞**：針對 OWASP Top 10（如 Injection, Broken Access Control），在 Spring Boot 層級實作具體的防禦策略。
    **Defend Against Common Vulnerabilities**: Implement concrete defense strategies at the Spring Boot level for OWASP Top 10 (e.g., Injection, Broken Access Control).
4.  **處理無狀態驗證的挑戰**：解釋 JWT 的撤銷（Revocation）難題，並設計出基於 Refresh Token 或黑名單的解決方案。
    **Handle Stateless Authentication Challenges**: Explain the difficulty of JWT revocation and design solutions based on Refresh Tokens or blacklists.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 The Filter Chain: 洋蔥模型 (The Onion Model)

Spring Security 的核心並非單一的攔截器，而是一層層的 **Servlet Filters**。想像這是一個機場安檢流程：你必須依序通過「檢查機票（Authentication）」、「身份核對（Authorization）」、「隨身行李檢查（CSRF/CORS）」才能到達登機門（Controller）。

The core of Spring Security is not a single interceptor, but layers of **Servlet Filters**. Imagine this as an airport security process: you must sequentially pass "Ticket Check (Authentication)", "ID Verification (Authorization)", and "Carry-on Check (CSRF/CORS)" before reaching the boarding gate (Controller).

*   **DelegatingFilterProxy**: Spring 在標準 Servlet 容器中的掛鉤（Hook），它將工作委派給 Spring Context 中的 Bean。
    **DelegatingFilterProxy**: Spring's hook in the standard Servlet container, delegating work to a Bean in the Spring Context.
*   **FilterChainProxy**: 安全過濾器的總管，負責決定針對當前請求應該執行哪一條 `SecurityFilterChain`。
    **FilterChainProxy**: The manager of security filters, responsible for deciding which `SecurityFilterChain` to execute for the current request.
*   **SecurityFilterChain**: 實際執行邏輯的地方（如 `UsernamePasswordAuthenticationFilter`, `BearerTokenAuthenticationFilter`）。
    **SecurityFilterChain**: Where the logic actually executes (e.g., `UsernamePasswordAuthenticationFilter`, `BearerTokenAuthenticationFilter`).

### 2.2 OAuth 2.0 & OIDC: 飯店房卡 (The Hotel Key Card)

在現代架構中，我們不再讓應用程式直接持有使用者的帳號密碼，而是使用 **Token**。

In modern architecture, we no longer let applications hold user credentials directly; instead, we use **Tokens**.

*   **Access Token (JWT)**: 就像飯店房卡。房卡上寫著過期時間、你能去的樓層（Scopes/Roles）。Resource Server（房門鎖）只認卡，不需打電話回櫃台（Auth Server）確認，除非要做深度驗證。
    **Access Token (JWT)**: Like a hotel key card. It has an expiration time and lists the floors you can access (Scopes/Roles). The Resource Server (door lock) validates the card itself without calling the front desk (Auth Server), unless deep validation is needed.
*   **Refresh Token**: 當房卡過期，你需要去櫃台換新卡。這是一個長效憑證，用來獲取新的 Access Token。
    **Refresh Token**: When the key card expires, you go to the front desk to get a new one. This is a long-lived credential used to obtain a new Access Token.
*   **OIDC (OpenID Connect)**: OAuth 2.0 只是授權（Authorization），OIDC 補足了身份驗證（Authentication）。它增加了一個 `ID Token`，告訴 Client「這個人是誰」。
    **OIDC (OpenID Connect)**: OAuth 2.0 is only for Authorization; OIDC completes it with Authentication. It adds an `ID Token` to tell the Client "who this person is."

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 微服務中的安全模式 (Security Patterns in Microservices)

在分散式系統中，資深工程師通常會採用 **Token Relay** 或 **Gateway Offloading** 模式。

In distributed systems, Senior Engineers typically adopt **Token Relay** or **Gateway Offloading** patterns.

1.  **API Gateway as OAuth2 Client (BFF Pattern)**:
    *   前端（SPA/Mobile）與 Gateway 進行驗證（可能透過 Session 或 Token）。
    *   Gateway 負責與 Identity Provider (IdP) 交換 Token。
    *   Gateway 將 Access Token (JWT) 放入 Header 轉發給後端微服務。
    *   **優點**：後端服務不需要處理複雜的 OAuth 流程，只需驗證 JWT 簽章。
    *   **Pros**: Backend services don't need to handle complex OAuth flows, only JWT signature validation.

2.  **Resource Server (Backend Services)**:
    *   每個微服務都是一個 Resource Server。
    *   它們不保存 Session，完全無狀態（Stateless）。
    *   **擴充性**：因為無狀態，服務可以水平擴展而不需同步 Session。
    *   **Scalability**: Being stateless, services can scale horizontally without session synchronization.

### 3.2 權限傳遞與細粒度控制 (Permission Propagation & Fine-Grained Control)

*   **Role-Based Access Control (RBAC)**: 粗粒度控制（例如 `ROLE_ADMIN`）。通常在 Filter 層級處理。
    **Role-Based Access Control (RBAC)**: Coarse-grained control (e.g., `ROLE_ADMIN`). Usually handled at the Filter level.
*   **Attribute-Based Access Control (ABAC)**: 細粒度控制（例如「使用者只能編輯*自己*的貼文」）。這通常透過 Spring Security 的 `@PreAuthorize` 結合 SpEL (Spring Expression Language) 在 Method 層級處理。
    **Attribute-Based Access Control (ABAC)**: Fine-grained control (e.g., "Users can only edit *their own* posts"). This is usually handled at the Method level using Spring Security's `@PreAuthorize` with SpEL.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將實作一個 **Resource Server**，它接受 JWT，並將 JWT 中的 Claims 轉換為 Spring Security 的 Authorities，同時加入一個自定義的黑名單過濾器。

We will implement a **Resource Server** that accepts JWTs, converts JWT Claims into Spring Security Authorities, and adds a custom blacklist filter.

### 4.1 依賴設定 (Dependencies)

```groovy
// build.gradle
implementation 'org.springframework.boot:spring-boot-starter-security'
implementation 'org.springframework.boot:spring-boot-starter-oauth2-resource-server'
```

### 4.2 配置 Security Filter Chain (Configuring the Security Filter Chain)

自 Spring Security 5.7+ (Spring Boot 3.x) 起，我們不再繼承 `WebSecurityConfigurerAdapter`，而是定義 `SecurityFilterChain` Bean。

Since Spring Security 5.7+ (Spring Boot 3.x), we no longer extend `WebSecurityConfigurerAdapter` but define a `SecurityFilterChain` Bean.

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Enable @PreAuthorize
public class SecurityConfig {

    private final JwtAuthConverter jwtAuthConverter; // Custom converter defined below

    public SecurityConfig(JwtAuthConverter jwtAuthConverter) {
        this.jwtAuthConverter = jwtAuthConverter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Disable CSRF for stateless APIs
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN") // Requires ROLE_ADMIN
                .anyRequest().authenticated()
            )
            
            // Configure as Resource Server with JWT
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter))
            );

        return http.build();
    }
}
```

### 4.3 自定義 JWT Converter (Custom JWT Converter)

預設的 Converter 僅讀取 `scope` 或 `scp` claim。但在企業環境（如 Keycloak 或 Azure AD），角色通常存放在 `realm_access.roles` 或 `groups` 中。我們需要手動映射。

The default Converter only reads `scope` or `scp` claims. However, in enterprise environments (like Keycloak or Azure AD), roles are often stored in `realm_access.roles` or `groups`. We need to map them manually.

```java
@Component
public class JwtAuthConverter implements Converter<Jwt, AbstractAuthenticationToken> {

    private final JwtGrantedAuthoritiesConverter defaultGrantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();

    @Override
    public AbstractAuthenticationToken convert(Jwt jwt) {
        // Combine default scopes with custom roles
        Collection<GrantedAuthority> authorities = Stream.concat(
            defaultGrantedAuthoritiesConverter.convert(jwt).stream(),
            extractResourceRoles(jwt).stream()
        ).collect(Collectors.toSet());

        // Return a standard authentication token with the principal name (e.g., username/sub)
        return new JwtAuthenticationToken(jwt, authorities, getPrincipalClaimName(jwt));
    }

    private Collection<? extends GrantedAuthority> extractResourceRoles(Jwt jwt) {
        Map<String, Object> resourceAccess = jwt.getClaim("resource_access");
        if (resourceAccess == null) {
            return Set.of();
        }
        
        // Example: Parsing Keycloak specific structure
        // "resource_access": { "my-client": { "roles": ["ADMIN", "USER"] } }
        Map<String, Object> resource = (Map<String, Object>) resourceAccess.get("my-client-id");
        if (resource == null) {
            return Set.of();
        }

        Collection<String> resourceRoles = (Collection<String>) resource.get("roles");
        return resourceRoles.stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role)) // Map to ROLE_ format
            .collect(Collectors.toSet());
    }

    private String getPrincipalClaimName(Jwt jwt) {
        return jwt.getClaim("preferred_username"); // Use username instead of UUID
    }
}
```

### 4.4 插入自定義過濾器 (Inserting a Custom Filter)

假設我們需要檢查 Token 是否已被撤銷（Revoked）。這無法單靠 JWT 簽章驗證（因為 JWT 是無狀態的）。我們需要在 `BearerTokenAuthenticationFilter` 之後檢查 Redis 黑名單。

Suppose we need to check if a Token has been revoked. This cannot be done by JWT signature validation alone (since JWT is stateless). We need to check a Redis blacklist after the `BearerTokenAuthenticationFilter`.

```java
public class TokenBlacklistFilter extends OncePerRequestFilter {

    private final RedisTemplate<String, String> redisTemplate;

    public TokenBlacklistFilter(RedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        
        if (auth instanceof JwtAuthenticationToken) {
            Jwt jwt = (Jwt) auth.getPrincipal();
            String tokenId = jwt.getId(); // jti claim

            if (Boolean.TRUE.equals(redisTemplate.hasKey("blacklist:" + tokenId))) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("Token is revoked");
                return; // Stop the chain
            }
        }
        
        filterChain.doFilter(request, response);
    }
}

// In SecurityConfig:
// http.addFilterAfter(new TokenBlacklistFilter(redisTemplate), BearerTokenAuthenticationFilter.class);
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在 JWT 中儲存敏感資訊 (Storing Sensitive Data in JWT)
*   **錯誤 (Mistake)**: 將使用者的 PII（如身分證號、地址）或權限細節直接放入 JWT Payload。
*   **為什麼不好 (Why it's bad)**: JWT 只是 Base64 編碼，**並未加密**。任何拿到 Token 的人都可以解碼看到內容。
*   **修正 (Fix)**: JWT 只應包含最少的識別資訊（User ID, Roles, Expiry）。敏感資料應透過 User ID 從資料庫查詢。

### 5.2 忽略 PKCE (Ignoring PKCE)
*   **錯誤 (Mistake)**: 在開發 Mobile App 或 SPA 時，仍然使用傳統的 Authorization Code Flow 甚至 Implicit Flow，而不加 PKCE。
*   **為什麼不好 (Why it's bad)**: 公開客戶端（Public Clients）無法安全保存 Client Secret。沒有 PKCE，Authorization Code 可能被惡意 App 攔截並交換成 Token。
*   **修正 (Fix)**: 強制所有 Public Clients 使用 **Authorization Code Flow with PKCE**。

### 5.3 錯誤的異常處理 (Incorrect Exception Handling)
*   **錯誤 (Mistake)**: 依賴 `@ControllerAdvice` 來處理 401/403 錯誤。
*   **為什麼不好 (Why it's bad)**: Spring Security 的 Filter Chain 發生在 DispatcherServlet **之前**。如果驗證失敗（例如 Token 無效），請求根本不會到達 Controller，因此 `@ControllerAdvice` 捕獲不到。
*   **修正 (Fix)**: 設定 `AuthenticationEntryPoint` (處理 401) 和 `AccessDeniedHandler` (處理 403) 於 `http.exceptionHandling()` 中。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: JWT 是無狀態的，我們要如何實作「強制登出」功能？
**JWT is stateless; how do we implement a "Force Logout" feature?**

*   **高分回答重點 (Key Points)**:
    *   承認 JWT 本質上無法「被撤銷」（除非 Key Rotation，但代價大）。
    *   提出 **Short-lived Access Token** (e.g., 5-15 mins) + **Refresh Token** 的策略。
    *   登出時，撤銷 Refresh Token（在 DB/Redis 中刪除或標記）。
    *   對於 Access Token 的空窗期，實作 **Token Blacklist** (存入 Redis, TTL 等於 Access Token 剩餘效期) 或 **Token Versioning** (User DB 中存一個 version，JWT 中帶 version，不一致則拒絕)。

### Q2: 解釋 Spring Security 中 `Authentication` 與 `Authorization` 的區別，以及它們在 Filter Chain 中的對應元件。
**Explain the difference between `Authentication` and `Authorization` in Spring Security, and their corresponding components in the Filter Chain.**

*   **高分回答重點 (Key Points)**:
    *   **Authentication (AuthN)**: 驗證你是誰。對應 `AuthenticationManager`。在 Filter Chain 中通常由 `UsernamePasswordAuthenticationFilter` 或 `BearerTokenAuthenticationFilter` 發起。
    *   **Authorization (AuthZ)**: 驗證你能做什麼。對應 `AuthorizationManager` (Spring Security 6) 或 `AccessDecisionManager` (舊版)。通常由 `AuthorizationFilter` (最後一道防線) 執行。
    *   強調順序：先 AuthN 再 AuthZ。

### Q3: 在微服務架構下，你會如何設計服務間的通訊安全（Service-to-Service Security）？
**In a microservices architecture, how would you design Service-to-Service Security?**

*   **高分回答重點 (Key Points)**:
    *   **Client Credentials Flow**: 服務 A 呼叫 服務 B 時，A 作為 OAuth2 Client 向 IdP 申請自己的 Token。
    *   **Token Relay**: 如果是代表使用者操作，服務 A 應將使用者的 Access Token 透傳給 服務 B。
    *   **mTLS (Mutual TLS)**: 除了應用層的 Token，網路層使用 mTLS 確保只有受信任的服務可以建立連線（Zero Trust 概念）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Filter Chain 是核心**：Spring Security 的一切魔法都在 Filter Chain 中，學會使用 `SecurityFilterChain` Bean 進行配置。
2.  **JWT Converter**：Resource Server 預設不一定能讀懂你的 ID Provider 的角色格式，需自定義 Converter。
3.  **Stateless vs Stateful**：理解 JWT 的權衡。無狀態帶來擴充性，但犧牲了即時撤銷的能力（需靠 Blacklist 補強）。
4.  **OAuth2 Flows**：後端服務間用 Client Credentials，前端用 Auth Code + PKCE。
5.  **Exception Handling**：Security 的錯誤處理要在 `AuthenticationEntryPoint` 做，而不是 Controller Advice。

### 後續延伸 (Next Steps)
*   **可觀測性 (Observability)**：學習如何將 User ID 或 Request ID 注入到 MDC (Mapped Diagnostic Context)，以便在 ELK/Splunk 中追蹤特定使用者的所有 Log。
*   **進階授權 (Advanced AuthZ)**：研究 **Open Policy Agent (OPA)**，將授權邏輯從程式碼中抽離，實現 Policy as Code。
*   **Vault 整合**：學習如何使用 HashiCorp Vault 動態管理 Database Credentials 和 Encryption Keys。