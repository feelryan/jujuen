# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，建置工具（Build Tools）的角色不再僅止於「編譯程式碼」，而是整個軟體供應鏈（Software Supply Chain）的核心樞紐。本章將探討如何利用 Maven 與 Gradle 實現現代化的發布工程（Release Engineering）。

In the career of a Senior Software Engineer, the role of Build Tools extends far beyond merely "compiling code"; they act as the central hub of the entire Software Supply Chain. This chapter explores how to leverage Maven and Gradle to implement modern Release Engineering.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作企業級版本控制策略**：理解並應用 Semantic Versioning，區分 Snapshot 與 Release 的生命週期管理。
    **Implement Enterprise-grade Versioning Strategies**: Understand and apply Semantic Versioning, distinguishing the lifecycle management of Snapshots versus Releases.
2.  **整合私有製品庫（Artifact Repository）**：配置 Maven/Gradle 與 Nexus 或 Artifactory 的安全整合，確保依賴的可追溯性。
    **Integrate Private Artifact Repositories**: Configure secure integration between Maven/Gradle and Nexus or Artifactory, ensuring dependency traceability.
3.  **自動化容器交付（Container Delivery）**：使用 Jib 或 Docker 插件將應用程式打包為最佳化的 Docker Image，並整合至 CI/CD 流程。
    **Automate Container Delivery**: Use Jib or Docker plugins to package applications into optimized Docker Images and integrate them into CI/CD pipelines.
4.  **設計不可變的發布流程（Immutable Release Process）**：消除「在我的機器上可以跑」的問題，確保從建置到生產環境的一致性。
    **Design an Immutable Release Process**: Eliminate "it works on my machine" issues, ensuring consistency from build to production environments.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 製品生命週期：Snapshot vs. Release
## 2.1 Artifact Lifecycle: Snapshot vs. Release

在發布工程中，最核心的心智模型是對「可變性（Mutability）」的控制。
In release engineering, the core mental model is the control of "Mutability".

-   **SNAPSHOT (Mutable)**: 代表開發中的版本。每次建置都可能產生不同的二進位檔（Binary），即使版本號相同（如 `1.0.0-SNAPSHOT`）。它像是工廠的「原型機」，隨時在變更。
    **SNAPSHOT (Mutable)**: Represents a version under development. Each build may produce a different binary, even if the version number is the same (e.g., `1.0.0-SNAPSHOT`). It is like a "prototype" in a factory, constantly changing.
-   **RELEASE (Immutable)**: 代表已發布的版本。一旦發布（如 `1.0.0`），該二進位檔絕對不可變更。若有 Bug，必須發布 `1.0.1` 而非覆蓋 `1.0.0`。這像是工廠已出貨的「正式產品」。
    **RELEASE (Immutable)**: Represents a published version. Once released (e.g., `1.0.0`), the binary must never change. If there is a bug, you must release `1.0.1` rather than overwriting `1.0.0`. This is like a "final product" shipped from the factory.

## 2.2 軟體供應鏈與製品庫
## 2.2 Software Supply Chain and Artifact Repositories

將 Maven/Gradle 視為生產線的「輸送帶」，而 Nexus/Artifactory 則是「倉庫」。
Think of Maven/Gradle as the "conveyor belt" of the production line, and Nexus/Artifactory as the "warehouse".

-   **Proxy Repository**: 代理外部依賴（如 Maven Central），提供快取與防火牆功能，避免每次都去外網下載。
    **Proxy Repository**: Proxies external dependencies (like Maven Central), providing caching and firewall capabilities to avoid downloading from the internet every time.
-   **Hosted Repository**: 存放內部團隊產出的 JAR/WAR 或 Docker Images。
    **Hosted Repository**: Stores JAR/WAR files or Docker Images produced by internal teams.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 CI/CD Pipeline 中的角色
## 3.1 Role in CI/CD Pipelines

在典型的微服務架構中，Maven/Gradle 在 CI/CD 流程中扮演「守門員」與「打包者」的角色。
In a typical microservices architecture, Maven/Gradle acts as the "gatekeeper" and "packager" within the CI/CD pipeline.

**流程設計 (Process Design):**
1.  **Commit**: 開發者提交程式碼。
    **Commit**: Developer commits code.
2.  **CI Build**: Jenkins/GitHub Actions 觸發建置。
    **CI Build**: Jenkins/GitHub Actions triggers the build.
3.  **Test & Scan**: 執行單元測試與靜態分析（Checkstyle/SonarQube）。
    **Test & Scan**: Executes unit tests and static analysis (Checkstyle/SonarQube).
4.  **Publish**:
    -   若是 Feature Branch -> `mvn deploy` 到 Snapshot Repo。
        If Feature Branch -> `mvn deploy` to Snapshot Repo.
    -   若是 Release Tag -> `mvn deploy` 到 Release Repo。
        If Release Tag -> `mvn deploy` to Release Repo.
5.  **Containerize**: 使用 Jib 建置 Docker Image 並推送到 Registry。
    **Containerize**: Build Docker Image using Jib and push to Registry.

## 3.2 對系統屬性的影響
## 3.2 Impact on System Attributes

-   **可維護性 (Maintainability)**: 透過統一的 Parent POM 或 Gradle Plugins 管理版本與發布邏輯，減少各個微服務的配置漂移（Configuration Drift）。
    **Maintainability**: Managing versioning and release logic through a unified Parent POM or Gradle Plugins reduces Configuration Drift across microservices.
-   **安全性 (Security)**: 在建置階段整合依賴掃描（Dependency Scanning），並確保只有經過驗證的 Artifacts 能進入 Release 庫。
    **Security**: Integrating dependency scanning at the build stage and ensuring only verified Artifacts enter the Release repository.
-   **可重複性 (Reproducibility)**: 確保在任何時間點，拉取特定的 Git Tag 都能建置出完全相同的 Artifact（Byte-for-byte 相同是理想目標，但在 Java 中較難，至少要做到功能一致）。
    **Reproducibility**: Ensuring that at any point in time, pulling a specific Git Tag builds the exact same Artifact (Byte-for-byte identity is the ideal goal, though harder in Java; functional consistency is the baseline).

---

# 4. 逐步示例 (Walkthrough / Example)

本節將展示如何配置一個 Spring Boot 專案，使其具備：
1. 自動化版本管理（CI Friendly Versioning）。
2. 發布至私有庫。
3. 使用 Jib 建立分層最佳化的 Docker Image。

This section demonstrates how to configure a Spring Boot project to have:
1. Automated Versioning (CI Friendly Versioning).
2. Publishing to a private repository.
3. Creating layer-optimized Docker Images using Jib.

## 4.1 Maven 設定：CI Friendly Versioning 與 Distribution
## 4.1 Maven Setup: CI Friendly Versioning and Distribution

傳統 Maven Release Plugin 操作繁瑣（需多次 commit）。現代做法是使用 `revision` 屬性。
The traditional Maven Release Plugin is cumbersome (requiring multiple commits). The modern approach uses the `revision` property.

**pom.xml:**

```xml
<project>
    <groupId>com.example.system</groupId>
    <artifactId>payment-service</artifactId>
    <!-- 使用變數定義版本，由 CI 工具注入 -->
    <!-- Define version using a variable, injected by CI tools -->
    <version>${revision}</version>

    <properties>
        <!-- 預設值為 SNAPSHOT，開發時使用 -->
        <!-- Default to SNAPSHOT for local development -->
        <revision>1.0.0-SNAPSHOT</revision>
    </properties>

    <!-- 配置私有庫位置 -->
    <!-- Configure private repository location -->
    <distributionManagement>
        <repository>
            <id>nexus-releases</id>
            <url>https://nexus.example.com/repository/maven-releases/</url>
        </repository>
        <snapshotRepository>
            <id>nexus-snapshots</id>
            <url>https://nexus.example.com/repository/maven-snapshots/</url>
        </snapshotRepository>
    </distributionManagement>

    <build>
        <plugins>
            <!-- Flatten Plugin 是必須的，它會將 ${revision} 解析為實際版號供消費者使用 -->
            <!-- Flatten Plugin is mandatory; it resolves ${revision} to the actual version for consumers -->
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>flatten-maven-plugin</artifactId>
                <version>1.5.0</version>
                <configuration>
                    <updatePomFile>true</updatePomFile>
                    <flattenMode>resolveCiFriendliesOnly</flattenMode>
                </configuration>
                <executions>
                    <execution>
                        <id>flatten</id>
                        <phase>process-resources</phase>
                        <goals><goal>flatten</goal></goals>
                    </execution>
                    <execution>
                        <id>flatten.clean</id>
                        <phase>clean</phase>
                        <goals><goal>clean</goal></goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

**CI Command (e.g., Jenkins/GitHub Actions):**

```bash
# 在 CI 中動態指定版本號
# Dynamically specify the version in CI
mvn deploy -Drevision=1.2.0
```

## 4.2 Gradle 設定：Maven Publish 與 Jib
## 4.2 Gradle Setup: Maven Publish and Jib

Gradle 的配置相對靈活，我們使用 `maven-publish` 與 Google 的 `jib-gradle-plugin`。
Gradle configuration is relatively flexible. We use `maven-publish` and Google's `jib-gradle-plugin`.

**build.gradle:**

```groovy
plugins {
    id 'java'
    id 'maven-publish'
    id 'com.google.cloud.tools.jib' version '3.4.0'
}

group = 'com.example.system'
// 從專案屬性讀取版本，若無則預設 SNAPSHOT
// Read version from project properties, default to SNAPSHOT if missing
version = project.findProperty('projVersion') ?: '1.0.0-SNAPSHOT'

publishing {
    publications {
        mavenJava(MavenPublication) {
            from components.java
        }
    }
    repositories {
        maven {
            name = 'myRepo'
            // 根據版本號決定上傳位置
            // Determine upload location based on version
            def releasesRepoUrl = "https://nexus.example.com/repository/maven-releases/"
            def snapshotsRepoUrl = "https://nexus.example.com/repository/maven-snapshots/"
            url = version.endsWith('SNAPSHOT') ? snapshotsRepoUrl : releasesRepoUrl
            credentials {
                username = System.getenv("NEXUS_USER")
                password = System.getenv("NEXUS_PASSWORD")
            }
        }
    }
}

jib {
    from {
        image = 'eclipse-temurin:17-jre-alpine'
    }
    to {
        image = "my-docker-registry.com/payment-service:${version}"
        auth {
            username = System.getenv("DOCKER_USER")
            password = System.getenv("DOCKER_PASSWORD")
        }
    }
    container {
        // 設定 JVM 參數與優化
        // Set JVM flags and optimizations
        jvmFlags = ['-Xms512m', '-Xmx512m']
        ports = ['8080']
    }
}
```

**Why Jib?**
Jib 不需要 Docker Daemon，且會將應用程式拆分為 dependencies, resources, classes 等多層（Layers）。當你只改了一行 code，Docker 只需更新 classes 層，依賴層（通常最大）會被快取，大幅加速 CI/CD。
Jib does not require a Docker Daemon and splits the application into multiple layers (dependencies, resources, classes). When you change a single line of code, Docker only needs to update the classes layer; the dependency layer (usually the largest) is cached, significantly speeding up CI/CD.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 依賴 SNAPSHOT 進行生產發布
## 5.1 Depending on SNAPSHOTs for Production Releases

-   **錯誤 (Pitfall)**: 在生產環境的 `pom.xml` 或 `build.gradle` 中依賴 `1.0.0-SNAPSHOT` 版本的共用庫。
    **Pitfall**: Depending on a `1.0.0-SNAPSHOT` version of a shared library in the production `pom.xml` or `build.gradle`.
-   **後果 (Consequence)**: 建置不可重複。今天部署沒問題，明天重新部署時，因為 SNAPSHOT 被更新了，導致系統崩潰。
    **Consequence**: Non-reproducible builds. Deployment works today, but fails tomorrow upon redeployment because the SNAPSHOT was updated, causing a system crash.
-   **修正 (Correction)**: 生產環境必須依賴 Release 版本。使用 Maven Enforcer Plugin 禁止 Release 版本依賴 SNAPSHOT。
    **Correction**: Production must depend on Release versions. Use the Maven Enforcer Plugin to ban Release versions from depending on SNAPSHOTs.

## 5.2 "Uber-JAR" in Docker
## 5.2 "Uber-JAR" in Docker

-   **錯誤 (Pitfall)**: 先打成一個巨大的 Fat JAR (Uber-JAR)，然後在 Dockerfile 中 `COPY app.jar .`。
    **Pitfall**: Building a huge Fat JAR (Uber-JAR) first, then using `COPY app.jar .` in a Dockerfile.
-   **後果 (Consequence)**: 浪費儲存空間與頻寬。只要改一行 Code，整個 100MB 的 JAR 都要重新推送到 Registry，無法利用 Docker Layer Caching。
    **Consequence**: Wasted storage and bandwidth. Changing one line of code requires re-pushing the entire 100MB JAR to the registry, failing to leverage Docker Layer Caching.
-   **修正 (Correction)**: 使用 Jib 或 Spring Boot 的 Layered Jar 功能，將依賴庫與應用程式碼分層。
    **Correction**: Use Jib or Spring Boot's Layered Jar feature to separate dependencies from application code into different layers.

## 5.3 環境特定的建置 (Environment-Specific Builds)
## 5.3 Environment-Specific Builds

-   **錯誤 (Pitfall)**: 為了 Dev, QA, Prod 環境分別執行 `mvn package -Pdev` 或 `mvn package -Pprod`，產出不同的 JAR 檔。
    **Pitfall**: Running `mvn package -Pdev` or `mvn package -Pprod` to produce different JAR files for Dev, QA, and Prod environments.
-   **後果 (Consequence)**: 違反「Build Once, Deploy Anywhere」原則。你在 QA 測過的 Binary 與 Prod 跑的 Binary 本質上是不同的檔案，風險極高。
    **Consequence**: Violates the "Build Once, Deploy Anywhere" principle. The binary tested in QA is fundamentally different from the one running in Prod, creating high risk.
-   **修正 (Correction)**: 建置一個通用的 Artifact，將環境配置（Config）外部化（如使用 Kubernetes ConfigMap 或環境變數）。
    **Correction**: Build a single generic Artifact and externalize environment configurations (e.g., using Kubernetes ConfigMaps or environment variables).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 如何設計一個支援多團隊協作的依賴管理機制？
## 6.1 How do you design a dependency management mechanism supporting multi-team collaboration?

-   **關鍵點 (Key Points)**:
    -   **BOM (Bill of Materials)**: 建立一個公司層級的 BOM (Maven) 或 Platform (Gradle)，統一管理常用第三方庫（如 Spring Boot, Jackson, Log4j）的版本。
        **BOM (Bill of Materials)**: Create a company-level BOM (Maven) or Platform (Gradle) to unify versions of common third-party libraries.
    -   **Snapshot Policy**: 開發期允許 Snapshot，但進入 Integration Test 前必須鎖定版本。
        **Snapshot Policy**: Allow Snapshots during development, but versions must be locked before Integration Testing.
    -   **Repository Isolation**: 區分 Public Repo (Proxy) 與 Private Repo (Hosted)，並設定權限控管。
        **Repository Isolation**: Distinguish between Public Repo (Proxy) and Private Repo (Hosted), and configure access controls.

## 6.2 `mvn install` 與 `mvn deploy` 有何不同？在 CI Server 上應該用哪個？
## 6.2 What is the difference between `mvn install` and `mvn deploy`? Which one should be used on a CI Server?

-   **關鍵點 (Key Points)**:
    -   `install`: 將 Artifact 安裝到 **本地 (Local)** Repository (`~/.m2/repository`)。僅供本機其他專案使用。
        `install`: Installs the Artifact to the **Local** Repository (`~/.m2/repository`). Only for use by other projects on the same machine.
    -   `deploy`: 將 Artifact 上傳到 **遠端 (Remote)** Repository (Nexus/Artifactory)。供團隊共用。
        `deploy`: Uploads the Artifact to the **Remote** Repository (Nexus/Artifactory). Shared by the team.
    -   **CI Server**: 應該使用 `deploy`。但在多模組專案（Multi-module project）的建置過程中，若模組間有依賴，Maven Reactor 會自動處理，通常不需要顯式 `install`，除非是為了跨專案的依賴快取。但在最終階段，務必是 `deploy` 以發布產出物。
        **CI Server**: Should use `deploy`. However, in multi-module project builds, the Maven Reactor handles inter-module dependencies automatically, so explicit `install` is often unnecessary unless for cross-project dependency caching. But for the final stage, it must be `deploy` to publish the artifacts.

## 6.3 為什麼在 Docker 時代我們還需要 Maven/Gradle？
## 6.3 Why do we still need Maven/Gradle in the Docker era?

-   **關鍵點 (Key Points)**:
    -   **依賴解析 (Dependency Resolution)**: Docker 無法處理 Java 複雜的遞移依賴（Transitive Dependencies）與版本衝突解決。
        **Dependency Resolution**: Docker cannot handle Java's complex transitive dependencies and version conflict resolution.
    -   **測試與報告 (Testing & Reporting)**: 單元測試、覆蓋率報告、靜態分析仍然依賴建置工具生態系。
        **Testing & Reporting**: Unit tests, coverage reports, and static analysis still rely on the build tool ecosystem.
    -   **分層建置 (Layered Build)**: 如 Jib 所示，建置工具能理解 Java 結構，從而建立比單純 `COPY` 更高效的 Docker Image。
        **Layered Build**: As seen with Jib, build tools understand Java structure, enabling the creation of more efficient Docker Images than a simple `COPY`.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 7.1 重點回顧 (Key Takeaways)
1.  **Immutability is King**: Release 版本一旦發布即不可變；Snapshot 用於快速迭代。
    **Immutability is King**: Release versions are immutable once published; Snapshots are for rapid iteration.
2.  **Single Source of Truth**: 所有依賴與產出物都應透過 Nexus/Artifactory 管理，而非直接依賴檔案系統或 Git。
    **Single Source of Truth**: All dependencies and artifacts should be managed via Nexus/Artifactory, not directly via file systems or Git.
3.  **CI Friendly Versioning**: 使用 `revision` 屬性或 Gradle 動態版本，讓 CI 系統主導版本號，而非手動修改 POM 檔。
    **CI Friendly Versioning**: Use the `revision` property or Gradle dynamic versioning to let the CI system drive version numbers, rather than manually editing POM files.
4.  **Container Optimization**: 使用 Jib 或 Layered Jars 來最大化 Docker Layer Caching 的效益。
    **Container Optimization**: Use Jib or Layered Jars to maximize the benefits of Docker Layer Caching.

## 7.2 後續延伸 (Next Steps)
-   **Advanced**: 研究 **Gradle Enterprise** (Develocity) 或 **Maven Build Cache** extension，學習如何透過遠端建置快取（Remote Build Cache）將 CI 時間縮短 50% 以上。
    **Advanced**: Investigate **Gradle Enterprise** (Develocity) or **Maven Build Cache** extension to learn how to reduce CI time by over 50% using Remote Build Cache.
-   **Security**: 深入了解 **SBOM (Software Bill of Materials)** 的生成（如 CycloneDX），這是現代供應鏈安全的重要環節。
    **Security**: Dive into **SBOM (Software Bill of Materials)** generation (e.g., CycloneDX), a critical part of modern supply chain security.