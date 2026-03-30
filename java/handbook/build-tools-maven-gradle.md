# Maven 與 Gradle 建置最佳實踐 / Maven and Gradle Build Best Practices

## Mental model｜心智模型

建置工具不僅僅是編譯程式碼的腳本執行器，它們本質上是**「依賴圖 (Dependency Graphs)」**與**「生命週期狀態機 (Lifecycle State Machines)」**。
Build tools are not just script runners for compiling code; fundamentally, they are **"Dependency Graphs"** and **"Lifecycle State Machines."**

- **Maven 的心智模型 (The Maven Mental Model)**：
  Maven 是「宣告式 (Declarative)」且具有嚴格的生命週期。你不需要告訴 Maven *如何*建置，你只需要告訴它你的專案長什麼樣子（透過 `pom.xml`），它會按照固定的階段（如 `validate`, `compile`, `test`, `package`, `deploy`）來執行。它的核心哲學是「慣例優於設定 (Convention over Configuration)」。
  Maven is declarative with a strict lifecycle. You don't tell Maven *how* to build; you describe what your project looks like (via `pom.xml`), and it executes through fixed phases. Its core philosophy is "Convention over Configuration."

- **Gradle 的心智模型 (The Gradle Mental Model)**：
  Gradle 是基於「有向無環圖 (DAG, Directed Acyclic Graph)」的任務執行引擎。它分為三個明確的階段：初始化 (Initialization)、配置 (Configuration) 與執行 (Execution)。你可以用程式化的方式（Groovy 或 Kotlin DSL）動態改變建置邏輯，這帶來了極大的靈活性，但也考驗開發者對生命週期的理解。
  Gradle is a task execution engine based on a Directed Acyclic Graph (DAG). It has three distinct phases: Initialization, Configuration, and Execution. You can dynamically alter build logic programmatically (Groovy/Kotlin DSL), which offers immense flexibility but requires a deep understanding of its lifecycle.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 集中化依賴管理 / Centralized Dependency Management
在多模組專案中，絕對不要在各個子模組中散落版本號。
In multi-module projects, never scatter version numbers across submodules.
- **Maven**: 使用 `<dependencyManagement>` 或引入 BOM (Bill of Materials) 來鎖定版本。子模組只需宣告 `groupId` 和 `artifactId`。
  Use `<dependencyManagement>` or import a BOM to lock versions. Submodules should only declare `groupId` and `artifactId`.
- **Gradle**: 使用現代的 **Version Catalogs** (`gradle/libs.versions.toml`)。這不僅能統一版本，還能提供 IDE 的自動補全支援。
  Use modern **Version Catalogs** (`gradle/libs.versions.toml`). This not only unifies versions but also provides IDE auto-completion support.

### 2. 模組化架構設計 / Modular Architecture Design
依據領域 (Domain) 或架構層級 (Architecture Layer) 拆分模組。
Split modules based on Domain or Architecture Layer.
- **API 模組 (API Modules)**：只包含介面 (Interfaces)、DTOs 與 Exceptions。保持極度輕量，**零外部依賴 (Zero external dependencies)**。
  Contains only Interfaces, DTOs, and Exceptions. Keep it extremely lightweight with **zero external dependencies**.
- **實作模組 (Implementation Modules)**：依賴 API 模組，並包含具體邏輯與第三方依賴。
  Depends on API modules and contains concrete logic and third-party dependencies.

### 3. 依賴範圍的精準控制 / Precise Control of Dependency Scopes
不要把所有依賴都設為預設的 `compile` (Maven) 或 `implementation` (Gradle)。
Do not set all dependencies to the default `compile` (Maven) or `implementation` (Gradle).
- **Gradle `api` vs `implementation`**：如果你的模組對外暴露了某個依賴的類別，使用 `api`；如果只是內部實作細節，使用 `implementation` 以避免依賴污染並加速編譯。
  If your module exposes a dependency's class in its public API, use `api`; if it's an internal implementation detail, use `implementation` to prevent dependency leakage and speed up compilation.
- **Maven `provided` / `test`**：對於執行環境已提供的套件（如 Servlet API）使用 `provided`；測試專用套件務必使用 `test`。
  Use `provided` for libraries supplied by the runtime (e.g., Servlet API); strictly use `test` for testing libraries.

### 4. 建置效能優化 / Build Performance Optimization
- **Gradle**: 啟用 Build Cache (`org.gradle.caching=true`) 與 Configuration Cache (`org.gradle.configuration-cache=true`)。
  Enable Build Cache and Configuration Cache in `gradle.properties`.
- **Maven**: 使用 Maven Daemon (`mvnd`) 或並行建置 (`mvn -T 1C clean install`) 來利用多核心 CPU。
  Use Maven Daemon (`mvnd`) or parallel builds to utilize multi-core CPUs.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 動態版本號 / Dynamic Versions
- **Pitfall**: 使用 `1.0.+`, `LATEST` 或 `RELEASE` 作為版本號。
  Using `1.0.+`, `LATEST`, or `RELEASE` as version numbers.
- **Consequence**: 破壞了建置的「可重現性 (Reproducibility)」。今天建置成功，明天可能因為某個第三方套件發布了有 bug 的新版本而突然崩潰。
  Breaks build reproducibility. A build that succeeds today might suddenly crash tomorrow because a third-party library released a buggy new version.
- **Fix**: 永遠鎖定具體的版本號。
  Always lock down specific version numbers.

### 2. 依賴傳遞的濫用 (幽靈依賴) / Abusing Transitive Dependencies (Phantom Dependencies)
- **Pitfall**: 你的程式碼中 `import` 了某個類別，但你的 `pom.xml` 或 `build.gradle` 卻沒有明確宣告它（它是被其他依賴偷偷帶進來的）。
  Importing a class in your code without explicitly declaring it in your build file (it was brought in transitively by another dependency).
- **Consequence**: 當你升級或移除那個上層依賴時，底層的傳遞依賴可能會消失或版本大改，導致 `ClassNotFoundException` 或 `NoSuchMethodError`。
  When you upgrade or remove the top-level dependency, the transitive dependency might disappear or change versions, leading to `ClassNotFoundException` or `NoSuchMethodError`.
- **Fix**: 只要你的程式碼直接用到了某個套件，就必須顯式宣告它 (Declare what you use)。
  Explicitly declare any library your code directly imports.

### 3. 混淆 Gradle 的配置與執行階段 / Confusing Gradle Configuration and Execution Phases
- **Pitfall**: 在 Gradle 腳本的頂層（配置階段）寫入耗時的邏輯（如打 API、讀寫大檔案）。
  Writing time-consuming logic (like API calls or large file I/O) at the top level of a Gradle script (Configuration phase).
- **Consequence**: 即使你只是執行 `gradle tasks` 或其他無關的任務，這些耗時邏輯都會被執行，導致整個專案的建置體驗極度緩慢。
  Even if you just run `gradle tasks` or an unrelated task, this slow logic will execute, making the entire build experience extremely sluggish.
- **Fix**: 將執行邏輯包裝在 Task 的 `doLast { ... }` 或 `doFirst { ... }` 區塊中。
  Wrap execution logic inside `doLast { ... }` or `doFirst { ... }` blocks of a Task.

---

## Checklists & workflows｜檢查清單與流程

### 依賴衝突排查流程 / Dependency Conflict Resolution Workflow

- [ ] **Step 1: 視覺化依賴樹 / Visualize the dependency tree**
  - Maven: `mvn dependency:tree -Dverbose -Dincludes=groupId:artifactId`
  - Gradle: `gradle :module-name:dependencies --configuration runtimeClasspath`
- [ ] **Step 2: 識別衝突來源 / Identify the source of conflict**
  - 檢查是否有兩個不同版本的同一個套件被引入（例如 `guava:20.0` 和 `guava:31.1-jre`）。
  - Check if two different versions of the same library are introduced.
- [ ] **Step 3: 排除不需要的依賴 / Exclude unwanted dependencies**
  - 使用 `<exclusion>` (Maven) 或 `exclude group: '...', module: '...'` (Gradle) 將錯誤版本的傳遞依賴剔除。
  - Use exclusions to remove the transitive dependency of the wrong version.
- [ ] **Step 4: 強制鎖定版本 / Force version resolution**
  - 如果排除太麻煩，直接在 Maven `<dependencyManagement>` 或 Gradle `resolutionStrategy.force` 中宣告你期望的最終版本。
  - If excluding is too tedious, declare the desired final version in Maven `<dependencyManagement>` or Gradle `resolutionStrategy.force`.

### 專案健康度檢查 / Project Health Checklist

- [ ] 是否已將所有外部依賴版本抽離至統一的設定檔 (BOM 或 Version Catalog)？ / Are all external dependency versions extracted to a centralized config?
- [ ] 是否移除了所有的動態版本號？ / Are all dynamic versions removed?
- [ ] 多模組專案中，子模組是否只宣告了它真正需要的依賴？ / In multi-module projects, do submodules only declare dependencies they actually need?
- [ ] CI/CD 環境是否已妥善設定 `~/.m2/repository` 或 `~/.gradle/caches` 的快取機制？ / Is the dependency cache mechanism properly configured in the CI/CD environment?

---

## Real-world examples｜實戰案例

### 案例 1：解決日誌框架衝突 (SLF4J Multiple Bindings) / Case 1: Resolving Logging Framework Conflicts
**情境 (Scenario)**：專案啟動時出現 `SLF4J: Class path contains multiple SLF4J bindings.` 警告，因為引入的第三方套件自帶了 `slf4j-simple`，而你的專案使用的是 `logback-classic`。
The project shows `SLF4J: Class path contains multiple SLF4J bindings.` on startup because a third-party library brought in `slf4j-simple`, while your project uses `logback-classic`.

**解決方案 (Solution)**：
在引入該第三方套件時，排除不需要的日誌實作。
Exclude the unwanted logging implementation when declaring the third-party dependency.

*Maven:*
```xml
<dependency>
    <groupId>com.thirdparty</groupId>
    <artifactId>legacy-library</artifactId>
    <version>1.2.3</version>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

*Gradle:*
```gradle
implementation('com.thirdparty:legacy-library:1.2.3') {
    exclude group: 'org.slf4j', module: 'slf4j-simple'
}
```

### 案例 2：Gradle Version Catalogs 實戰 / Case 2: Gradle Version Catalogs in Practice
**情境 (Scenario)**：在多模組專案中，統一管理 Spring Boot 與工具庫的版本。
Unifying versions for Spring Boot and utility libraries in a multi-module project.

**解決方案 (Solution)**：
建立 `gradle/libs.versions.toml` 檔案：
Create the `gradle/libs.versions.toml` file:

```toml
[versions]
springBoot = "3.2.0"
guava = "32.1.3-jre"

[libraries]
# 定義單一依賴 / Define single dependencies
guava = { module = "com.google.guava:guava", version.ref = "guava" }

# 引入 BOM / Import a BOM
spring-boot-dependencies = { module = "org.springframework.boot:spring-boot-dependencies", version.ref = "springBoot" }

[bundles]
# 將常用的依賴打包 / Bundle commonly used dependencies together
core-utils = ["guava"]
```

在子模組的 `build.gradle` 中優雅地使用：
Use it elegantly in the submodule's `build.gradle`:

```gradle
dependencies {
    // 引入 BOM 以統一 Spring 相關套件版本 / Import BOM to unify Spring versions
    implementation platform(libs.spring.boot.dependencies)
    implementation 'org.springframework.boot:spring-boot-starter-web' // 不需寫版本號 / No version needed
    
    // 引入 Bundle / Import bundle
    implementation libs.bundles.core.utils
}
```