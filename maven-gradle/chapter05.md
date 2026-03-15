# Chapter 05: Custom Plugins and DSL Development
# 第 05 章：客製化插件與 DSL 開發

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Software Engineer, your relationship with build tools should shift from "consumption" to "architecture." Writing custom plugins and Domain-Specific Languages (DSLs) is the key to scaling engineering practices across an organization. Instead of copy-pasting boilerplate XML or Groovy scripts across hundreds of microservices, you encapsulate logic into reusable, versioned plugins.
身為資深軟體工程師，你與建置工具的關係應從「使用」轉變為「架構」。撰寫客製化插件（Plugins）與領域特定語言（DSLs）是將工程實踐擴展至整個組織的關鍵。你不應在數百個微服務中複製貼上樣板 XML 或 Groovy 腳本，而應將邏輯封裝成可重複使用且受版本控制的插件。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Architect Build Logic**: Move complex script logic from `pom.xml` or `build.gradle.kts` into standalone, testable plugins.
    **架構建置邏輯**：將複雜的腳本邏輯從 `pom.xml` 或 `build.gradle.kts` 遷移至獨立且可測試的插件中。
2.  **Develop Custom Extensions**: Implement Maven Mojos and Gradle Plugins (using Kotlin DSL) to solve enterprise-specific problems (e.g., security compliance, custom deployment).
    **開發客製化擴充**：實作 Maven Mojos 與 Gradle Plugins（使用 Kotlin DSL）以解決企業特定問題（如安全性合規、客製化部署）。
3.  **Design Internal DSLs**: Create intuitive configuration blocks in Gradle to simplify developer experience (DX).
    **設計內部 DSL**：在 Gradle 中建立直覺的配置區塊，以簡化開發者體驗（DX）。
4.  **Optimize Build Performance**: Understand the lifecycle implications of your code to avoid breaking incremental builds or parallel execution.
    **優化建置效能**：理解程式碼對生命週期的影響，避免破壞增量建置（Incremental Builds）或平行執行。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Build as Code" Abstraction
### 2.1 「建置即程式碼」的抽象層

Think of your build script (`pom.xml` / `build.gradle`) as the `main()` function of your application's delivery process. Custom plugins are the **shared libraries**.
請將你的建置腳本（`pom.xml` / `build.gradle`）想像成應用程式交付流程中的 `main()` 函式。而客製化插件則是**共用函式庫**。

-   **Naive Approach**: Writing complex logic (loops, conditionals, file I/O) directly in the build script. This is equivalent to putting all business logic in `main()`.
    **天真做法**：直接在建置腳本中撰寫複雜邏輯（迴圈、條件判斷、檔案 I/O）。這等同於將所有商業邏輯都塞進 `main()`。
-   **Senior Approach**: Extracting that logic into a plugin. The build script simply *configures* the plugin.
    **資深做法**：將該邏輯提取至插件中。建置腳本僅負責*配置*該插件。

### 2.2 Maven Mojo vs. Gradle Task/Plugin
### 2.2 Maven Mojo 與 Gradle Task/Plugin 的對比

| Feature | Maven (Mojo) | Gradle (Plugin/Task) |
| :--- | :--- | :--- |
| **Unit of Work** | **Mojo** (Maven plain Old Java Object). A single executable goal bound to a lifecycle phase. | **Task**. An atomic unit of work in the Directed Acyclic Graph (DAG). |
| **Dependency Injection** | Uses JSR-330 (`@Inject`) or legacy Plexus to inject Maven components (Project, Session). | Uses Gradle's internal DI to inject services (`ObjectFactory`, `ProviderFactory`). |
| **Configuration** | XML configuration mapped to Java fields via `@Parameter`. | **Extensions** (DSL objects) mapped to Task properties. |
| **Execution Model** | Linear phases (Validate -> Compile -> Test...). | Graph-based (Task A depends on Task B). |

### 2.3 The Gradle Lifecycle Trap
### 2.3 Gradle 生命週期陷阱

A crucial mental model for Gradle plugin development is distinguishing between the **Configuration Phase** and the **Execution Phase**.
開發 Gradle 插件時，一個至關重要的心智模型是區分**配置階段（Configuration Phase）**與**執行階段（Execution Phase）**。

-   **Configuration Phase**: Gradle evaluates the build scripts and constructs the Task Graph. **Do not perform heavy I/O here.**
    **配置階段**：Gradle 評估建置腳本並建構任務圖（Task Graph）。**切勿在此執行繁重的 I/O 操作。**
-   **Execution Phase**: Gradle executes the tasks in the graph. This is where your plugin's action logic belongs.
    **執行階段**：Gradle 執行圖中的任務。這才是你的插件動作邏輯該存在的地方。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Standardization in Microservices
### 3.1 微服務中的標準化

In a company with 50+ microservices, maintaining consistency is a distributed system problem.
在一間擁有 50 個以上微服務的公司裡，維護一致性是一個分散式系統問題。

-   **Scenario**: Security team mandates that all JARs must be signed and scanned for CVEs before upload.
    **情境**：資安團隊強制要求所有 JAR 檔在上傳前必須經過簽章並掃描 CVE。
-   **Without Plugins**: You update 50 `pom.xml` files. If the scanning tool URL changes, you update 50 files again.
    **沒有插件**：你需要更新 50 個 `pom.xml` 檔案。如果掃描工具的 URL 變更，你又要再更新 50 個檔案。
-   **With Plugins**: You publish `com.company:security-compliance-plugin:1.2.0`. Services just apply the plugin. Logic changes are centralized.
    **使用插件**：你發布 `com.company:security-compliance-plugin:1.2.0`。服務只需套用該插件。邏輯變更得以集中管理。

### 3.2 The "Enterprise Build Plugin" Pattern
### 3.2 「企業級建置插件」模式

A common architectural pattern is to create a "Convention Plugin" (Gradle) or "Parent POM + Plugin" (Maven) that encapsulates:
一個常見的架構模式是建立「慣例插件（Convention Plugin）」（Gradle）或「父 POM + 插件」（Maven），其中封裝了：

1.  **Repository definitions**: (e.g., internal Artifactory/Nexus).
    **Repository 定義**：（例如：內部 Artifactory/Nexus）。
2.  **Linting rules**: (Checkstyle, Spotless configurations).
    **程式碼檢查規則**：（Checkstyle, Spotless 配置）。
3.  **Versioning strategy**: (Git-based semantic versioning).
    **版本策略**：（基於 Git 的語意化版本控制）。

This reduces the "Mean Time to Hello World" for new services and enforces governance.
這降低了新服務的「Hello World 前置時間」，並強制執行治理規範。

---

## 4. Walkthrough / Example
## 4. 逐步示例

We will implement a simple logic: **"Fail the build if the project version ends with `-SNAPSHOT` in a release environment."**
我們將實作一個簡單的邏輯：**「若在發布環境中專案版本以 `-SNAPSHOT` 結尾，則使建置失敗。」**

### 4.1 Maven Custom Mojo
### 4.1 Maven 客製化 Mojo

**Step 1: Define the Mojo**
Create a Java class extending `AbstractMojo`.
**步驟 1：定義 Mojo**
建立一個繼承 `AbstractMojo` 的 Java 類別。

```java
@Mojo(name = "check-release-version", defaultPhase = LifecyclePhase.VERIFY)
public class ReleaseVersionCheckMojo extends AbstractMojo {

    @Parameter(defaultValue = "${project}", required = true, readonly = true)
    private MavenProject project;

    @Parameter(property = "enforceRelease", defaultValue = "false")
    private boolean enforceRelease;

    public void execute() throws MojoExecutionException {
        String version = project.getVersion();
        getLog().info("Checking version: " + version);

        if (enforceRelease && version.endsWith("-SNAPSHOT")) {
            throw new MojoExecutionException("SNAPSHOT versions are not allowed when enforceRelease is true!");
        }
    }
}
```

**Step 2: Usage in Consumer POM**
**步驟 2：在消費端 POM 中使用**

```xml
<plugin>
    <groupId>com.mycompany</groupId>
    <artifactId>compliance-maven-plugin</artifactId>
    <version>1.0.0</version>
    <executions>
        <execution>
            <goals><goal>check-release-version</goal></goals>
        </execution>
    </executions>
    <configuration>
        <enforceRelease>true</enforceRelease>
    </configuration>
</plugin>
```

### 4.2 Gradle Custom Plugin (Kotlin DSL)
### 4.2 Gradle 客製化插件（Kotlin DSL）

**Step 1: Define Extension (DSL) and Plugin**
Gradle allows creating a DSL for configuration.
**步驟 1：定義擴充（DSL）與插件**
Gradle 允許建立用於配置的 DSL。

```kotlin
// 1. The Configuration Object (DSL)
open class ComplianceExtension {
    var enforceRelease: Boolean = false
}

// 2. The Plugin Logic
class CompliancePlugin : Plugin<Project> {
    override fun apply(project: Project) {
        // Create the 'compliance' DSL block
        val extension = project.extensions.create("compliance", ComplianceExtension::class.java)

        project.tasks.register("checkReleaseVersion") {
            group = "verification"
            description = "Ensures no SNAPSHOTs in release mode"
            
            // Use 'doLast' to ensure this runs in Execution Phase, not Configuration Phase
            doLast {
                val version = project.version.toString()
                println("Checking version: $version")
                
                if (extension.enforceRelease && version.endsWith("-SNAPSHOT")) {
                    throw GradleException("SNAPSHOT versions are not allowed when enforceRelease is true!")
                }
            }
        }
    }
}
```

**Step 2: Usage in Consumer `build.gradle.kts`**
**步驟 2：在消費端 `build.gradle.kts` 中使用**

```kotlin
plugins {
    id("com.mycompany.compliance") version "1.0.0"
}

compliance {
    enforceRelease = true
}
```

**Analysis**:
The Gradle approach allows for a more fluid DSL (`compliance { ... }`) compared to Maven's rigid XML structure. However, Maven's lifecycle binding is often simpler to understand for beginners.
**分析**：
相較於 Maven 僵化的 XML 結構，Gradle 的做法允許更流暢的 DSL（`compliance { ... }`）。然而，Maven 的生命週期綁定通常對初學者來說較易理解。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Gradle: Logic in Configuration Phase
### 5.1 Gradle：邏輯置於配置階段

-   **Anti-pattern**: Putting print statements or file operations directly in the task body (outside `doFirst` / `doLast`).
    **反模式**：將列印語句或檔案操作直接放在任務主體中（在 `doFirst` / `doLast` 之外）。
-   **Consequence**: This code runs **every time** the user types `gradle <anything>`, even `gradle help`, slowing down the build significantly.
    **後果**：這段程式碼會在**每次**使用者輸入 `gradle <任何指令>` 時執行，即使是 `gradle help`，這會顯著拖慢建置速度。
-   **Fix**: Move execution logic into `doLast { ... }`.
    **修正**：將執行邏輯移至 `doLast { ... }` 中。

### 5.2 Maven: Not Thread-Safe
### 5.2 Maven：非執行緒安全

-   **Anti-pattern**: Using static fields in Mojo classes to store state.
    **反模式**：在 Mojo 類別中使用靜態欄位來儲存狀態。
-   **Consequence**: Maven 3+ supports parallel builds (`-T 4`). Static state causes race conditions when multiple modules are built concurrently.
    **後果**：Maven 3+ 支援平行建置（`-T 4`）。當多個模組同時建置時，靜態狀態會導致競態條件（Race Conditions）。
-   **Fix**: Use instance variables and `@Parameter`.
    **修正**：使用實例變數與 `@Parameter`。

### 5.3 Breaking Incremental Builds (Gradle)
### 5.3 破壞增量建置（Gradle）

-   **Anti-pattern**: Writing a task that doesn't declare inputs and outputs.
    **反模式**：撰寫一個未宣告輸入（Inputs）與輸出（Outputs）的任務。
-   **Consequence**: Gradle cannot know if the task is "up-to-date," so it re-runs it every time, negating Gradle's performance benefits.
    **後果**：Gradle 無法得知該任務是否為「最新狀態（up-to-date）」，因此每次都會重新執行，抵銷了 Gradle 的效能優勢。
-   **Fix**: Annotate task properties with `@Input`, `@InputFile`, `@OutputFile`.
    **修正**：使用 `@Input`, `@InputFile`, `@OutputFile` 註解任務屬性。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### 6.1 Design a Build Standardization Strategy
### 6.1 設計建置標準化策略

-   **Question**: "We have 100 microservices with drifting build configurations. How would you architect a solution to standardize them using Maven or Gradle?"
    **問題**：「我們有 100 個微服務，其建置配置逐漸分歧。你會如何架構一個解決方案，使用 Maven 或 Gradle 來標準化它們？」
-   **Key Points**:
    *   **Centralization**: Create a shared plugin (Gradle) or Parent POM (Maven).
    *   **Versioning**: How to roll out updates? (Force upgrade vs. semantic versioning).
    *   **Flexibility**: Allow overrides via DSL/Properties for edge cases (don't be too rigid).
    *   **Migration**: Scripted migration (e.g., OpenRewrite) vs. manual adoption.

### 6.2 Gradle Lifecycle & Performance
### 6.2 Gradle 生命週期與效能

-   **Question**: "A developer complains that the build takes 10 seconds just to initialize before doing any work. What could be the cause in a custom plugin?"
    **問題**：「開發者抱怨建置在開始任何工作前，光是初始化就花了 10 秒。客製化插件中的什麼問題可能導致此情況？」
-   **Key Points**:
    *   Expensive logic (HTTP requests, heavy parsing) placed in the **Configuration Phase**.
    *   Resolving dependencies eagerly instead of lazily.
    *   Abuse of `project.afterEvaluate` causing cascading evaluation delays.

### 6.3 Maven vs. Gradle Plugin Architecture
### 6.3 Maven 與 Gradle 插件架構比較

-   **Question**: "Compare the extension model of Maven and Gradle. Which one is easier to test and why?"
    **問題**：「比較 Maven 與 Gradle 的擴充模型。哪一個比較容易測試？為什麼？」
-   **Key Points**:
    *   Gradle (especially with Kotlin DSL) is generally easier to unit test because Tasks are plain classes that can be instantiated and asserted against easily using `ProjectBuilder`.
    *   Maven requires `maven-plugin-testing-harness`, which often involves creating dummy `pom.xml` files for integration testing (more boilerplate).

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Encapsulation**: Move logic out of build scripts into plugins to promote reuse and maintainability.
    **封裝**：將邏輯從建置腳本移至插件中，以促進重複使用與可維護性。
2.  **Lifecycle Awareness**: In Gradle, strictly separate Configuration (setup) from Execution (action). In Maven, bind Mojos to appropriate phases.
    **生命週期意識**：在 Gradle 中，嚴格區分配置（設定）與執行（動作）。在 Maven 中，將 Mojos 綁定至適當的階段。
3.  **DSL Design**: Use Gradle Extensions to create readable, declarative configurations for your teams.
    **DSL 設計**：使用 Gradle Extensions 為團隊建立可讀且宣告式的配置。
4.  **Performance**: Declare Inputs/Outputs to enable incremental builds and build caching.
    **效能**：宣告輸入/輸出以啟用增量建置與建置快取。
5.  **Testing**: Treat build logic as production code—write unit and integration tests for your plugins.
    **測試**：將建置邏輯視為正式程式碼——為你的插件撰寫單元測試與整合測試。

### Next Steps
### 後續延伸

-   **Advanced Caching**: Learn how to make your custom plugins compatible with **Gradle Build Cache** or **Maven Build Cache** (Develocity/Gradle Enterprise).
    **進階快取**：學習如何使你的客製化插件相容於 **Gradle Build Cache** 或 **Maven Build Cache**（Develocity/Gradle Enterprise）。
-   **Artifact Management**: Proceed to **Chapter 06**, where we will discuss managing artifacts (Nexus/Artifactory) and designing a robust dependency promotion pipeline.
    **Artifact 管理**：前往 **第 06 章**，我們將討論管理 Artifacts（Nexus/Artifactory）並設計穩健的相依性晉升（Promotion）管線。