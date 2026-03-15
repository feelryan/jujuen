# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，建置工具（Build Tools）不僅僅是用來編譯程式碼的工具，更是確保軟體交付品質的第一道防線。本章節專注於如何利用 Maven 與 Gradle 建立穩健的測試策略與品質閘門（Quality Gates）。
In the career of a Senior Software Engineer, build tools are not just for compiling code; they are the first line of defense for software delivery quality. This chapter focuses on how to use Maven and Gradle to establish robust testing strategies and Quality Gates.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精確區分與配置單元測試（UT）與整合測試（IT）**：理解 Maven 生命周期中的 `test` 與 `verify` 階段差異，以及 Gradle 中自定義 SourceSets 的技巧。
    **Accurately distinguish and configure Unit Tests (UT) and Integration Tests (IT)**: Understand the difference between `test` and `verify` phases in the Maven lifecycle, and techniques for custom SourceSets in Gradle.
2.  **整合程式碼覆蓋率與靜態分析工具**：熟練配置 JaCoCo 與 SonarQube，並理解如何解讀報告以驅動重構，而非盲目追求數字。
    **Integrate code coverage and static analysis tools**: Proficiently configure JaCoCo and SonarQube, and understand how to interpret reports to drive refactoring rather than blindly chasing numbers.
3.  **設計自動化的品質閘門（Quality Gates）**：在 CI/CD 流程中實作「Fail-Fast」機制，確保不符合標準的程式碼無法進入主要分支。
    **Design automated Quality Gates**: Implement "Fail-Fast" mechanisms in CI/CD pipelines to ensure code that does not meet standards cannot merge into the main branch.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 測試金字塔與構建生命週期 (The Test Pyramid & Build Lifecycle)

在心智模型中，我們應將構建工具視為一個「過濾器管道（Filter Pipeline）」。越早期的過濾器（Unit Test）應該越快且越嚴格；越後期的過濾器（Integration Test）則越接近真實環境但允許較慢的執行速度。
In your mental model, view the build tool as a "Filter Pipeline." The earlier filters (Unit Tests) should be faster and stricter; later filters (Integration Tests) should be closer to the real environment but allow for slower execution speeds.

### Maven 的雙階段測試模型 (Maven's Two-Phase Test Model)
Maven 透過兩個特定的 Plugin 來區分測試類型：
Maven distinguishes test types through two specific plugins:

*   **maven-surefire-plugin**: 負責執行單元測試。綁定於 `test` 階段。一旦失敗，構建立即停止。
    **maven-surefire-plugin**: Responsible for executing unit tests. Bound to the `test` phase. If it fails, the build stops immediately.
*   **maven-failsafe-plugin**: 負責執行整合測試。綁定於 `integration-test` 與 `verify` 階段。即使測試失敗，也會繼續執行到 `post-integration-test` 以便清理環境（如關閉 Docker 容器），最後在 `verify` 階段拋出錯誤。
    **maven-failsafe-plugin**: Responsible for executing integration tests. Bound to the `integration-test` and `verify` phases. Even if tests fail, it proceeds to `post-integration-test` to clean up the environment (e.g., shutting down Docker containers), and finally throws an error in the `verify` phase.

### Gradle 的靈活任務模型 (Gradle's Flexible Task Model)
Gradle 沒有強制規定生命週期，但慣例上我們將測試分為不同的 `SourceSet`。
Gradle does not enforce a strict lifecycle, but conventionally, we separate tests into different `SourceSets`.

*   **SourceSet**: 邏輯上的程式碼群組（例如 `src/main`, `src/test`, `src/integrationTest`）。
    **SourceSet**: A logical grouping of code (e.g., `src/main`, `src/test`, `src/integrationTest`).
*   **Task Dependency**: 設定 `check` 任務依賴於 `test` 和自定義的 `integrationTest` 任務。
    **Task Dependency**: Configure the `check` task to depend on `test` and a custom `integrationTest` task.

## 2.2 品質閘門的概念 (The Concept of Quality Gates)

品質閘門是 CI 流程中的「檢查哨」。它不只是看測試有沒有通過，還包含：
Quality Gates are "checkpoints" in the CI process. They check not only if tests pass but also:

*   **Coverage Thresholds**: 覆蓋率是否低於 80%？
    **Coverage Thresholds**: Is coverage below 80%?
*   **Code Smells**: 是否引入了新的 Critical Issues？
    **Code Smells**: Have new Critical Issues been introduced?
*   **Duplication**: 程式碼重複率是否過高？
    **Duplication**: Is code duplication too high?

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 CI/CD 流水線中的角色 (Role in CI/CD Pipelines)

在典型的微服務架構中，Build Tool 的配置直接影響 CI/CD 的效率與可靠性。
In a typical microservices architecture, the configuration of the Build Tool directly impacts the efficiency and reliability of CI/CD.

*   **Commit Stage (PR Check)**: 僅執行 `compile` + `unit test` + `static analysis (fast)`。目標是 5-10 分鐘內給出回饋。此時通常會略過耗時的整合測試。
    **Commit Stage (PR Check)**: Executes only `compile` + `unit test` + `static analysis (fast)`. The goal is feedback within 5-10 minutes. Time-consuming integration tests are usually skipped here.
*   **Nightly / Merge Stage**: 執行 `integration test` + `end-to-end test` + `full sonar scan`。這是為了捕捉跨服務或資料庫層面的回歸錯誤。
    **Nightly / Merge Stage**: Executes `integration test` + `end-to-end test` + `full sonar scan`. This is to catch regression errors at the cross-service or database level.

## 3.2 對可維護性的影響 (Impact on Maintainability)

資深工程師知道，**測試程式碼也是程式碼**。如果 Maven/Gradle 配置混亂（例如 UT/IT 混在一起跑），會導致：
Senior engineers know that **test code is code**. If Maven/Gradle configuration is messy (e.g., running UT/IT together), it leads to:

1.  **Flaky Builds**: 因為整合測試通常依賴外部資源（DB, Network），混在一起會讓整個構建變得不穩定。
    **Flaky Builds**: Since integration tests often rely on external resources (DB, Network), mixing them makes the entire build unstable.
2.  **Slow Feedback Loop**: 開發者改一行 code 卻要等 30 分鐘才能知道結果，這會嚴重拖慢開發速度。
    **Slow Feedback Loop**: If a developer changes one line of code and has to wait 30 minutes for results, it severely slows down development velocity.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例背景 (Scenario)
我們有一個 Spring Boot 專案，混合了單元測試（Mocking）與整合測試（Testcontainers + PostgreSQL）。目前的構建時間過長，且無法阻擋低品質程式碼合併。
We have a Spring Boot project mixing Unit Tests (Mocking) and Integration Tests (Testcontainers + PostgreSQL). The current build time is too long, and we cannot prevent low-quality code from being merged.

## 4.1 Maven 實作：分離 UT 與 IT (Maven Implementation: Separating UT and IT)

我們利用命名慣例：`*Test.java` 為單元測試，`*IT.java` 為整合測試。
We use naming conventions: `*Test.java` for Unit Tests, `*IT.java` for Integration Tests.

```xml
<!-- pom.xml -->
<build>
    <plugins>
        <!-- Unit Tests: Runs by default on 'mvn test' -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.1.2</version>
            <configuration>
                <!-- Exclude Integration Tests from the fast test phase -->
                <excludes>
                    <exclude>**/*IT.java</exclude>
                </excludes>
            </configuration>
        </plugin>

        <!-- Integration Tests: Runs on 'mvn verify' -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-failsafe-plugin</artifactId>
            <version>3.1.2</version>
            <configuration>
                <includes>
                    <include>**/*IT.java</include>
                </includes>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>integration-test</goal>
                        <goal>verify</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
        
        <!-- JaCoCo: Code Coverage -->
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>0.8.10</version>
            <executions>
                <execution>
                    <goals>
                        <goal>prepare-agent</goal>
                    </goals>
                </execution>
                <!-- Quality Gate: Fail build if coverage < 80% -->
                <execution>
                    <id>check</id>
                    <goals>
                        <goal>check</goal>
                    </goals>
                    <configuration>
                        <rules>
                            <rule>
                                <element>BUNDLE</element>
                                <limits>
                                    <limit>
                                        <counter>INSTRUCTION</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.80</minimum>
                                    </limit>
                                </limits>
                            </rule>
                        </rules>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

**操作說明 (Instructions):**
- 執行 `mvn test`：只跑 UT，速度快。
- 執行 `mvn verify`：跑 UT + IT + JaCoCo Check。如果覆蓋率不足，構建失敗。
- Run `mvn test`: Runs only UT, fast.
- Run `mvn verify`: Runs UT + IT + JaCoCo Check. If coverage is insufficient, the build fails.

## 4.2 Gradle 實作：自定義 SourceSet (Gradle Implementation: Custom SourceSet)

Gradle (Kotlin DSL) 提供了更強大的隔離性。
Gradle (Kotlin DSL) offers more powerful isolation.

```kotlin
// build.gradle.kts
plugins {
    java
    jacoco
    id("org.sonarqube") version "4.3.0.3225"
}

// 1. Define a separate source set for Integration Tests
val integrationTest by sourceSets.creating {
    compileClasspath += sourceSets.main.get().output + sourceSets.test.get().output
    runtimeClasspath += sourceSets.main.get().output + sourceSets.test.get().output
}

// 2. Configure dependencies specifically for IT
val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.testImplementation.get())
}

// 3. Register the task
val integrationTestTask = tasks.register<Test>("integrationTest") {
    description = "Runs integration tests."
    group = "verification"
    testClassesDirs = integrationTest.output.classesDirs
    classpath = integrationTest.runtimeClasspath
    shouldRunAfter("test") // Run UT first
    
    useJUnitPlatform()
}

// 4. Enforce Quality Gate with JaCoCo
tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = 0.8.toBigDecimal()
            }
        }
    }
}

// 5. Hook into the build lifecycle
tasks.check {
    dependsOn(integrationTestTask) // 'check' runs both UT and IT
    dependsOn(tasks.jacocoTestCoverageVerification)
}
```

**為何這樣做可行？ (Why this works?)**
這將整合測試的編譯路徑與執行路徑完全獨立。開發者可以單獨執行 `./gradlew test` (快) 或 `./gradlew integrationTest` (慢)，或者用 `./gradlew check` 執行完整驗證。
This completely isolates the compilation and execution paths of integration tests. Developers can run `./gradlew test` (fast) or `./gradlew integrationTest` (slow) independently, or use `./gradlew check` for full verification.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 錯誤：在 Unit Test 階段啟動 Spring Context (Pitfall: Starting Spring Context in UT Phase)
**描述**：在 `maven-surefire-plugin` 或 Gradle `test` 任務中，包含了啟動完整 ApplicationContext 的測試。
**Description**: Including tests that start the full ApplicationContext within the `maven-surefire-plugin` or Gradle `test` task.
**為何不好**：這違反了「單元測試應在毫秒級完成」的原則。一旦專案變大，`mvn test` 可能需要 10 分鐘，導致開發者不願意在本地頻繁執行測試。
**Why it's bad**: This violates the principle that "Unit tests should finish in milliseconds." As the project grows, `mvn test` might take 10 minutes, causing developers to avoid running tests locally.
**修正**：將依賴 Spring Context 的測試移至 IT 階段，或使用 Slice Test (如 `@JsonTest`, `@WebMvcTest`) 僅加載必要組件。
**Fix**: Move tests depending on Spring Context to the IT phase, or use Slice Tests (e.g., `@JsonTest`, `@WebMvcTest`) to load only necessary components.

## 5.2 錯誤：盲目追求 100% 覆蓋率 (Pitfall: Blindly Chasing 100% Coverage)
**描述**：為了滿足 SonarQube 的閘門，工程師為 Getter/Setter 或 DTO 撰寫無意義的測試。
**Description**: Engineers write meaningless tests for Getters/Setters or DTOs just to satisfy SonarQube gates.
**為何不好**：浪費維護成本，且產生虛假的安全感。
**Why it's bad**: Wastes maintenance effort and creates a false sense of security.
**修正**：在 JaCoCo/SonarQube 設定中 `exclude` DTO、Configuration 類別，專注於業務邏輯的覆蓋率。
**Fix**: Configure JaCoCo/SonarQube to `exclude` DTOs and Configuration classes, focusing coverage on business logic.

## 5.3 錯誤：整合測試共用同一個髒資料庫 (Pitfall: Shared Dirty Database for ITs)
**描述**：所有 IT 都在同一個實體 DB 上執行，且沒有在測試後清理資料。
**Description**: All ITs run against the same physical DB without cleaning up data after tests.
**為何不好**：測試順序會影響結果（Flaky Tests），無法平行執行。
**Why it's bad**: Test order affects results (Flaky Tests), and parallel execution is impossible.
**修正**：使用 **Testcontainers** 為每個測試類別或套件啟動乾淨的 DB 容器，或使用 `@Transactional` 在測試結束後 rollback。
**Fix**: Use **Testcontainers** to spin up clean DB containers for each test class/suite, or use `@Transactional` to rollback after tests.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在大型 Monorepo 中優化測試執行時間？
**How to optimize test execution time in a large Monorepo?**

*   **高分回答要點 (Key Points)**：
    *   **Gradle Build Cache**: 解釋 Gradle 如何重用未變更模組的測試結果（Test Avoidance）。
    *   **Parallel Execution**: 在 Maven (`-T 1C`) 或 Gradle (`maxParallelForks`) 中啟用平行測試。
    *   **Test Splitting**: 在 CI 層級將測試分片（Sharding）到不同機器執行。
    *   **Impact Analysis**: 僅執行受變更程式碼影響的模組測試。

## Q2: 你會如何設計一個「不可略過」的 Quality Gate？
**How would you design an "unskippable" Quality Gate?**

*   **高分回答要點 (Key Points)**：
    *   **Branch Protection Rules**: 在 GitHub/GitLab 設定 Main 分支保護，強制要求 CI Status Check 通過。
    *   **SonarQube Webhook**: CI 等待 SonarQube 分析結果的回調（Quality Gate Status），若為 Failed 則 CI 失敗。
    *   **Admin Override**: 提到緊急修復（Hotfix）時的例外處理流程（Break glass procedure），展現資深工程師的務實思維。

## Q3: 什麼時候應該讓 CI 構建失敗？什麼時候應該只是警告？
**When should a CI build fail, and when should it just warn?**

*   **高分回答要點 (Key Points)**：
    *   **Fail**: 編譯錯誤、單元測試失敗、嚴重安全性漏洞（CVE）、覆蓋率大幅下降（Ratchet mechanism）。
    *   **Warn**: 輕微的 Code Style 問題、TODO 標記、非阻塞性的 Deprecation 警告。
    *   **策略**: 新專案從嚴（Fail），遺留系統從寬（Warn）並逐步收緊（Ratchet）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **分離關注點**：使用 Maven 的 `surefire`/`failsafe` 或 Gradle 的 `SourceSets` 嚴格區分 UT 與 IT。
2.  **Fail-Fast**：單元測試必須快且在構建早期執行；整合測試雖然慢但負責把關系統整合性。
3.  **數據驅動品質**：利用 JaCoCo 與 SonarQube 建立可量化的品質標準，但要避免指標虛榮化。
4.  **環境隔離**：整合測試應搭配 Testcontainers 確保環境一致性與可重複性。

## 後續延伸 (Next Steps)
*   **Next Chapter**: 探索 **Artifact Management & Release Strategy**（製品管理與發布策略），學習如何將通過測試的構建產物（JAR/Docker Image）安全地推送到 Nexus/Artifactory。
*   **Advanced Topic**: 研究 **Mutation Testing** (如 PITest)，這是一種比代碼覆蓋率更高級的測試品質評估技術，能檢測測試案例是否真的具備捕捉錯誤的能力。