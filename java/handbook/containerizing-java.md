# 容器化 Java 應用與記憶體感知 / Containerizing Java and Memory Awareness

## Mental model｜心智模型

**傳統 JVM 的錯覺：以為自己擁有整棟大樓**
在過去，JVM 啟動時會讀取「實體主機 (Host)」的硬體資訊來設定預設的記憶體與執行緒池大小。當你把 Java 應用放進 Docker 容器並限制記憶體（例如 512MB），早期的 JVM 依然會以為它擁有宿主機的 32GB 記憶體。結果就是 JVM 瘋狂分配記憶體，最終被作業系統的 OOM Killer 無情砍掉（**OOMKilled**）。

**The Illusion of Legacy JVMs: Thinking it owns the whole building**
Historically, when the JVM started, it read the underlying "Host" hardware to configure its default memory and thread pools. If you put a Java app in a Docker container with a 512MB limit, an older JVM would still think it had access to the host's 32GB of RAM. The result? The JVM allocates memory aggressively until the OS's OOM Killer ruthlessly terminates it (**OOMKilled**).

**現代 JVM 的容器感知：遵守租約的房客**
從 Java 8u191 與 Java 11 開始，JVM 預設啟用了 `UseContainerSupport`。它終於學會去讀取 Linux cgroups 的限制。這意味著 JVM 現在知道自己身處容器中，會根據容器的限制（而非宿主機）來調整 Heap Size 與 CPU 核心數。

**Modern JVM Container Awareness: A tenant who respects the lease**
Starting from Java 8u191 and Java 11, the JVM enables `UseContainerSupport` by default. It finally learned to read Linux cgroups limits. This means the JVM now knows it's in a container and will adjust its Heap Size and CPU core count based on the container's limits, not the host's.

**Image 瘦身：只打包必需品**
容器映像檔（Image）是交付的載體。不要把整個「製造工廠」（JDK）打包進去，你只需要「成品與執行環境」（JRE 或客製化 Runtime）。

**Image Shrinking: Pack only the essentials**
A container image is a delivery vehicle. Don't pack the entire "manufacturing plant" (JDK) into it; you only need the "finished goods and runtime" (JRE or custom Runtime).

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用相對比例配置記憶體 / Use Percentage-Based Memory Allocation
在 Kubernetes 或 Docker 環境中，不要寫死 `-Xmx`。請使用 `-XX:MaxRAMPercentage`。這樣當你調整 Pod 的資源限制時，JVM 會自動按比例縮放，無需重新修改啟動參數。
In Kubernetes or Docker environments, avoid hardcoding `-Xmx`. Use `-XX:MaxRAMPercentage` instead. This allows the JVM to scale proportionally when you adjust the Pod's resource limits, without needing to change the startup arguments.

### 2. 多階段建置與分層打包 / Multi-stage Builds and Layered Packaging
不要把幾十 MB 的依賴庫和幾 KB 的業務程式碼塞進同一個 Fat JAR 層。利用 Spring Boot 的 Layered JAR 功能或手動解包，將不常變動的依賴（Dependencies）與常變動的業務邏輯（Application code）分開打包，大幅加快 CI/CD 速度。
Don't stuff tens of megabytes of dependencies and a few kilobytes of business code into a single Fat JAR layer. Use Spring Boot's Layered JAR feature or manual unpacking to separate infrequently changing dependencies from frequently changing application code. This drastically speeds up CI/CD.

### 3. 使用極簡的 Base Image / Use Minimal Base Images
拋棄龐大的 `openjdk` 映像檔。改用 `eclipse-temurin:17-jre-alpine`、`distroless/java17-debian11` 或 Ubuntu Chiseled。這不僅能減少映像檔體積，還能大幅降低安全漏洞（CVEs）的攻擊面。
Abandon the bloated `openjdk` images. Switch to `eclipse-temurin:17-jre-alpine`, `distroless/java17-debian11`, or Ubuntu Chiseled. This not only reduces the image size but also significantly minimizes the attack surface for security vulnerabilities (CVEs).

### 4. 啟用 CDS 加速啟動 / Enable Class Data Sharing (CDS)
對於非 GraalVM Native Image 的傳統 JVM，啟用 AppCDS 可以將類別的元資料快取起來，讓容器啟動時間減少 20%~40%，同時降低記憶體消耗。
For traditional JVMs not using GraalVM Native Image, enabling AppCDS caches class metadata, reducing container startup time by 20%~40% while also lowering memory footprint.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 反模式 1：Heap Size 等於容器限制 / Anti-pattern 1: Heap Size equals Container Limit
**情境 / Scenario**：Kubernetes Pod Limit 設為 1GB，你把 JVM 參數設為 `-Xmx1G` 或 `-XX:MaxRAMPercentage=100.0`。
**後果 / Consequence**：必定發生 **OOMKilled**。JVM 除了 Heap 之外，還需要記憶體來存放 Metaspace、執行緒堆疊 (Thread Stacks)、Direct Buffers (NIO) 以及 JVM 自身的 C++ 程式碼。
**解法 / Solution**：通常將 `-XX:MaxRAMPercentage` 設為 `70.0` 到 `80.0`，保留 20%-30% 的記憶體給 Non-Heap 與作業系統。

### ❌ 反模式 2：在生產環境使用 JDK Image / Anti-pattern 2: Using JDK Images in Production
**情境 / Scenario**：Dockerfile 使用 `FROM maven:3.8-openjdk-17` 或 `FROM openjdk:17` 作為最終執行環境。
**後果 / Consequence**：映像檔高達 400MB+，且包含了編譯器、除錯工具等駭客最愛的工具鏈，極不安全。
**解法 / Solution**：使用 Multi-stage build，在 Builder 階段使用 JDK，在 Runtime 階段使用 JRE 或 JLink 裁減過的 Runtime。

### ❌ 反模式 3：忽略 CPU 節流限制 / Anti-pattern 3: Ignoring CPU Throttling limits
**情境 / Scenario**：在 K8s 中將 CPU Limit 設得太低（例如 `0.5` 核心），導致 Java 應用啟動極慢。
**後果 / Consequence**：JVM 啟動時需要大量 CPU 進行 JIT 編譯。CPU 被節流（Throttled）會導致啟動超時，甚至觸發 K8s Liveness Probe 失敗而無限重啟。
**解法 / Solution**：給予足夠的 CPU Limit（至少 1-2 cores），或者將 Liveness Probe 的 `initialDelaySeconds` 拉長。

---

## Checklists & workflows｜檢查清單與流程

### 容器化 Java 檢查清單 / Containerized Java Checklist

- [ ] **記憶體感知 (Memory Awareness)**
  - [ ] 確認使用的 Java 版本 >= 11 (或至少 8u191)。 / Verified Java version is >= 11 (or at least 8u191).
  - [ ] 啟動腳本使用 `-XX:MaxRAMPercentage=75.0` 而非 `-Xmx`。 / Startup script uses `-XX:MaxRAMPercentage=75.0` instead of `-Xmx`.
  - [ ] K8s 容器的 Memory Limit 大於 (Heap + Metaspace + Thread Stacks + Native Memory)。 / K8s container Memory Limit is greater than (Heap + Metaspace + Thread Stacks + Native Memory).
- [ ] **映像檔最佳化 (Image Optimization)**
  - [ ] 採用 Multi-stage build，生產環境 Image 不含原始碼與 Maven/Gradle。 / Multi-stage build is used; production image lacks source code and Maven/Gradle.
  - [ ] 生產環境使用 JRE 或 Distroless 基礎映像檔。 / Production uses JRE or Distroless base images.
  - [ ] 應用程式 JAR 檔已分層（Layered），依賴庫與業務程式碼分離。 / Application JAR is layered; dependencies and business code are separated.
- [ ] **生命週期與探針 (Lifecycle & Probes)**
  - [ ] 應用程式能正確處理 `SIGTERM` 訊號並進行優雅停機 (Graceful Shutdown)。 / App correctly handles `SIGTERM` for Graceful Shutdown.
  - [ ] K8s Readiness/Liveness Probe 的啟動延遲時間足以應付 JVM JIT 暖機。 / K8s probe delays are sufficient to handle JVM JIT warmup.

---

## Real-world examples｜實戰案例

### 實戰：現代化 Spring Boot 應用的 Dockerfile (分層與記憶體感知)
### Real-world: Modern Spring Boot Dockerfile (Layered & Memory Aware)

這是一個符合最佳實踐的 Dockerfile，使用了多階段建置、分層 JAR 提取，以及輕量級的 JRE 基礎映像檔。
This is a best-practice Dockerfile using multi-stage builds, layered JAR extraction, and a lightweight JRE base image.

```dockerfile
# ==========================================
# Stage 1: Builder (Extracting layers)
# ==========================================
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app

# 假設已經在 CI 階段編譯好 fat-jar (Assuming fat-jar is built in CI)
COPY target/my-app-1.0.0.jar application.jar

# 使用 Spring Boot 內建工具解包分層 (Extract layers using Spring Boot tools)
RUN java -Djarmode=layertools -jar application.jar extract

# ==========================================
# Stage 2: Runtime (Minimal JRE)
# ==========================================
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 建立非 root 使用者以提升安全性 (Create non-root user for security)
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# 依序複製分層，利用 Docker Cache 加速後續建置 
# (Copy layers sequentially to leverage Docker cache)
COPY --from=builder app/dependencies/ ./
COPY --from=builder app/spring-boot-loader/ ./
COPY --from=builder app/snapshot-dependencies/ ./
COPY --from=builder app/application/ ./

# 暴露 Port (Expose port)
EXPOSE 8080

# 啟動參數：
# 1. 確保開啟容器支援 (預設已開，顯式宣告作文件用途)
# 2. 將 75% 的容器記憶體分配給 Heap
# 3. 發生 OOM 時輸出 Heap Dump 供排查
# Startup arguments:
# 1. Ensure container support is on (default, but explicit for documentation)
# 2. Allocate 75% of container RAM to Heap
# 3. Output Heap Dump on OOM for troubleshooting
ENTRYPOINT ["java", \
            "-XX:+UseContainerSupport", \
            "-XX:MaxRAMPercentage=75.0", \
            "-XX:+HeapDumpOnOutOfMemoryError", \
            "-XX:HeapDumpPath=/tmp/heapdump.hprof", \
            "org.springframework.boot.loader.JarLauncher"]
```

**架構決策說明 / Architecture Decision Notes：**
1. **為什麼不直接 `java -jar my-app.jar`？** 
   因為每次修改一行程式碼，整個 50MB 的 JAR 檔都要重新上傳到 Docker Registry。分層後，`dependencies` 層（通常最大且最少變動）會被 Docker 快取，每次部署只需上傳幾 KB 的 `application` 層。
   *Why not just `java -jar my-app.jar`?* Because every time you change one line of code, the entire 50MB JAR must be re-uploaded to the Docker Registry. With layering, the `dependencies` layer (usually the largest and least changed) is cached by Docker, meaning only a few KB of the `application` layer are uploaded per deployment.
2. **為什麼是 `75.0`？**
   如果 K8s 限制 Pod 記憶體為 1024MB，JVM Heap 最大會是 768MB。剩下的 256MB 足夠留給 Metaspace、執行緒和 OS 網路緩衝區，完美避開 OOMKilled。
   *Why `75.0`?* If K8s limits Pod memory to 1024MB, the JVM Heap will max out at 768MB. The remaining 256MB is plenty for Metaspace, threads, and OS network buffers, perfectly avoiding OOMKilled.