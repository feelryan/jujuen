# GraalVM 與 Native Image 實戰 / GraalVM and Native Image in Practice

## Mental model｜心智模型

傳統的 Java 虛擬機（JVM）採用**即時編譯（JIT, Just-In-Time）**，程式在執行時才將 Bytecode 轉換為機器碼。這帶來了極高的尖峰吞吐量（Peak Throughput），但代價是較長的冷啟動時間（Cold Start）與較高的記憶體消耗。
Traditional Java Virtual Machines (JVMs) use **Just-In-Time (JIT)** compilation, converting bytecode to machine code at runtime. This provides extremely high peak throughput but comes at the cost of slow cold start times and high memory consumption.

GraalVM Native Image 則採用**提前編譯（AOT, Ahead-Of-Time）**，在建置期（Build time）就對程式碼進行靜態分析，並直接編譯成特定作業系統的獨立執行檔（Standalone Executable）。
GraalVM Native Image, on the other hand, uses **Ahead-Of-Time (AOT)** compilation. It statically analyzes the code at build time and compiles it directly into a standalone executable for a specific operating system.

**核心心智模型：封閉世界假設（Closed-World Assumption）**
**Core Mental Model: The Closed-World Assumption**
Native Image 要求在編譯時必須知道所有在執行期會被執行的程式碼。這就像是把一本「活頁夾（JIT）」變成了一本「膠裝書（AOT）」。你不能在程式執行時無中生有地載入新類別，任何動態特性（如 Reflection、Dynamic Proxies、JNI、動態載入 Resource）都必須在建置期明確宣告。
Native Image requires that all code to be executed at runtime must be known at compile time. It's like turning a "loose-leaf binder (JIT)" into a "perfect-bound book (AOT)". You cannot load new classes out of thin air at runtime; any dynamic features (Reflection, Dynamic Proxies, JNI, dynamic resource loading) must be explicitly declared at build time.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 Tracing Agent 收集 Metadata / Leverage the Tracing Agent for Metadata
不要手寫反射設定檔。在標準 JVM 上掛載 `native-image-agent` 執行你的完整測試套件，讓 Agent 自動生成 `reflect-config.json`、`resource-config.json` 等設定檔。
Never write reflection configuration files by hand. Run your comprehensive test suite on a standard JVM with the `native-image-agent` attached, allowing it to automatically generate `reflect-config.json`, `resource-config.json`, and other configuration files.

```bash
# 執行應用程式並收集 metadata / Run app and collect metadata
java -agentlib:native-image-agent=config-output-dir=META-INF/native-image -jar my-app.jar
```

### 2. 選擇 AOT 友善的框架 / Choose AOT-Friendly Frameworks
在真實專案中，與其自己處理龐大依賴的 AOT 轉換，不如直接使用為 Native Image 設計的現代框架（如 Quarkus, Micronaut, Helidon）或支援 AOT 的 Spring Boot 3.x。這些框架會在建置期（Build-time）解析依賴注入與反射，生成無需反射即可執行的程式碼。
In real-world projects, rather than manually handling AOT conversions for massive dependencies, use modern frameworks designed for Native Image (like Quarkus, Micronaut, Helidon) or Spring Boot 3.x with AOT support. These frameworks resolve dependency injection and reflection at build-time, generating reflection-free code.

### 3. 區分建置期與執行期初始化 / Distinguish Build-Time vs. Run-Time Initialization
Native Image 預設會在「執行期」初始化類別，但為了極致的啟動速度，你可以設定某些類別在「建置期」初始化。最佳實務是：將沒有副作用的靜態常數放在建置期初始化，將依賴環境變數、隨機數生成（如 `SecureRandom`）、執行緒啟動的邏輯強制保留在執行期。
Native Image initializes classes at "run-time" by default, but for extreme startup speed, you can configure certain classes to initialize at "build-time". Best practice: Initialize side-effect-free static constants at build-time, but strictly keep logic depending on environment variables, random number generation (like `SecureRandom`), and thread starting at run-time.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 迷思：Native Image 效能一定比 JVM 好 / Myth: Native Image always performs better than JVM
**Pitfall**: 認為編譯成機器碼後，所有的效能指標都會提升。
**Consequence**: 實際上，Native Image 的「啟動速度」和「記憶體佔用」遠勝傳統 JVM，但「尖峰吞吐量（Peak Throughput）」通常較差，因為它缺乏 JIT 根據執行期實際數據進行的動態最佳化（如 Method Inlining、Branch Prediction）。
**Correction**: 如果你的應用是長時間運行的重度運算後端（Long-running heavy backend），請保持使用傳統 JVM。如果是 Serverless (AWS Lambda)、CLI 工具或微服務，才使用 Native Image。若要在 Native Image 提升吞吐量，需導入 PGO (Profile-Guided Optimization，需企業版或較新社群版支援)。

**Pitfall**: Assuming that compiling to machine code improves all performance metrics.
**Consequence**: In reality, while Native Image drastically improves "startup time" and "memory footprint", its "peak throughput" is usually lower because it lacks JIT's dynamic optimizations based on actual runtime profiling (like aggressive method inlining and branch prediction).
**Correction**: Stick to the traditional JVM for long-running, compute-heavy backends. Use Native Image for Serverless (AWS Lambda), CLI tools, or microservices. To improve throughput in Native Image, use PGO (Profile-Guided Optimization, available in Enterprise or newer Community Editions).

### ❌ 忽略資源檔的打包 / Ignoring Resource File Packaging
**Pitfall**: 程式碼中使用 `Class.getResourceAsStream("config.properties")`，但在 Native Image 執行時回傳 `null`。
**Consequence**: 導致 NullPointerException 或應用程式啟動失敗。因為 AOT 編譯器預設不會將非 `.class` 檔案打包進執行檔中。
**Correction**: 必須在 `resource-config.json` 中使用 Regex 明確宣告需要包含的資源檔。

**Pitfall**: Using `Class.getResourceAsStream("config.properties")` in code, but it returns `null` when running as a Native Image.
**Consequence**: Leads to `NullPointerException` or application startup failure. The AOT compiler does not include non-`.class` files in the executable by default.
**Correction**: You must explicitly declare the required resource files using Regex in `resource-config.json`.

---

## Checklists & workflows｜檢查清單與流程

在將專案轉換為 Native Image 時，請遵循以下標準化流程：
Follow this standardized workflow when converting a project to Native Image:

- [ ] **Phase 1: Dependency Audit (依賴審查)**
  - [ ] 確認核心依賴是否已知支援 GraalVM（可查閱 GraalVM Reachability Metadata Repository）。
  - [ ] 移除或替換高度依賴動態位元組碼生成（Dynamic Bytecode Generation, e.g., CGLib）的舊版函式庫。
- [ ] **Phase 2: Metadata Collection (收集元數據)**
  - [ ] 使用 `native-image-agent` 執行單元測試與整合測試。
  - [ ] 確認測試覆蓋率足夠高，確保所有反射、JNI、Proxy 的執行路徑都有被 Agent 捕捉到。
- [ ] **Phase 3: Build & Configuration (建置與設定)**
  - [ ] 檢查生成的 `reflect-config.json` 是否包含預期的類別。
  - [ ] 確保 `SecureRandom` 或依賴環境變數的靜態區塊被標記為 `--initialize-at-run-time`。
- [ ] **Phase 4: Containerization & Testing (容器化與測試)**
  - [ ] 使用 Multi-stage Docker build，在 builder 階段編譯 Native Image，並將產物複製到輕量級 base image（如 `scratch`, `distroless`, `alpine`）。
  - [ ] 在容器環境中執行 E2E 測試，驗證資源讀取與網路連線是否正常。

---

## Real-world examples｜實戰案例

### 案例：Spring Boot 3.x AOT 與 Docker 多階段建置 / Case: Spring Boot 3.x AOT with Docker Multi-stage Build

在真實微服務場景中，我們通常結合 Spring Boot 3 的 AOT 引擎與 GraalVM 來打造極小體積、毫秒啟動的容器映像檔。
In real-world microservice scenarios, we typically combine Spring Boot 3's AOT engine with GraalVM to create ultra-small, millisecond-startup container images.

**情境 (Scenario)**：
將一個 Spring Boot 應用程式部署至 AWS ECS 或 Knative，要求在流量突增時能在 100ms 內完成冷啟動擴容（Scale-out）。
Deploying a Spring Boot application to AWS ECS or Knative, requiring cold-start scale-out within 100ms during traffic spikes.

**Dockerfile 實踐 (Dockerfile Practice)**：

```dockerfile
# Stage 1: Build the native image using GraalVM JDK
# 階段 1：使用 GraalVM JDK 建置 Native Image
FROM ghcr.io/graalvm/native-image-community:21 AS builder
WORKDIR /app
COPY . .
# Spring Boot 3 內建 AOT 支援，直接透過 Maven Profile 觸發
# Spring Boot 3 has built-in AOT support, triggered via Maven Profile
RUN ./mvnw -Pnative native:compile

# Stage 2: Create the minimal runtime image
# 階段 2：建立極簡執行期映像檔
# 使用 distroless 提供極小的攻擊面與體積 (無 shell)
# Using distroless for minimal attack surface and size (no shell)
FROM gcr.io/distroless/base-nossl
WORKDIR /app
# 將編譯好的二進位執行檔複製過來
# Copy the compiled binary executable
COPY --from=builder /app/target/my-spring-app /app/my-spring-app

# 直接執行二進位檔，無需 java -jar
# Execute the binary directly, no 'java -jar' needed
ENTRYPOINT ["/app/my-spring-app"]
```

**執行結果對比 (Execution Result Comparison)**：
- **傳統 JVM (JIT)**：啟動時間 ~2.5 秒，基礎記憶體佔用 ~300 MB。
- **Native Image (AOT)**：啟動時間 ~0.08 秒 (80ms)，基礎記憶體佔用 ~45 MB。
- **Traditional JVM (JIT)**: Startup time ~2.5 seconds, base memory footprint ~300 MB.
- **Native Image (AOT)**: Startup time ~0.08 seconds (80ms), base memory footprint ~45 MB.