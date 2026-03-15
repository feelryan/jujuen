# Chapter 09: 工具遷移與現代化重構 (Migration Strategies and Modernization)

## 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，除了開發新功能，更常面臨的是維護與現代化既有的 Legacy System。建置工具（Build Tool）的遷移往往牽涉到團隊開發流程的改變與 CI/CD 的重構。本章旨在協助你評估 Maven 與 Gradle 的適用場景，並掌握從 Legacy 系統遷移至現代化 Gradle Kotlin DSL 的策略。

In the career of a Senior Software Engineer, beyond developing new features, you often face the maintenance and modernization of existing Legacy Systems. Migrating Build Tools involves changes in team development workflows and CI/CD refactoring. This chapter aims to help you evaluate the trade-offs between Maven and Gradle, and master the strategies for migrating from legacy systems to modern Gradle Kotlin DSL.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **評估技術選型 (Evaluate Technical Trade-offs)**：從效能、靈活性與維護成本的角度，客觀分析 Maven 與 Gradle 在特定專案中的優劣。
    Analyze the pros and cons of Maven and Gradle for specific projects objectively, focusing on performance, flexibility, and maintenance costs.
2.  **制定遷移策略 (Formulate Migration Strategies)**：設計「漸進式遷移（Incremental Migration）」計畫，確保在轉換建置工具的過程中，不中斷現有的交付流程。
    Design an "Incremental Migration" plan to ensure that the existing delivery pipeline is not disrupted during the build tool transition.
3.  **實作現代化重構 (Implement Modernization)**：熟練使用 Gradle Kotlin DSL (`.kts`) 取代 Groovy，並運用 Version Catalogs 進行依賴管理，提升建置腳本的型別安全（Type Safety）與可讀性。
    Proficiently use Gradle Kotlin DSL (`.kts`) to replace Groovy, and utilize Version Catalogs for dependency management, enhancing the type safety and readability of build scripts.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 建置哲學的差異：約定 vs. 編排 (Convention vs. Orchestration)

**Maven** 採用高度的「約定優於配置（Convention over Configuration）」與嚴格的生命週期（Lifecycle）。你可以將 Maven 想像成**公車路線**：站點（Phases）是固定的，你只能決定要在哪一站上下車或掛載貨物（Plugins），但不能輕易改變路線。

**Maven** adopts a high degree of "Convention over Configuration" with a strict Lifecycle. You can think of Maven as a **Bus Route**: the stops (Phases) are fixed; you can only decide where to get on/off or load cargo (Plugins), but you cannot easily change the route.

**Gradle** 則是基於「有向無環圖（DAG, Directed Acyclic Graph）」的任務編排系統。它更像是**Uber/導航系統**：雖然有建議路徑，但你可以完全自定義起點、終點與中間經過的邏輯。這賦予了 Gradle 極高的靈活性，但也帶來了複雜度。

**Gradle** is a task orchestration system based on a "Directed Acyclic Graph (DAG)". It is more like an **Uber/Navigation System**: while there are suggested routes, you can fully customize the start, end, and logic in between. This gives Gradle immense flexibility but also introduces complexity.

### 2.2 遷移的心智模型：絞殺榕模式 (Strangler Fig Pattern)

在進行建置工具遷移時，不應視為一次性的「大霹靂（Big Bang）」切換。應採用類似微服務遷移的 **Strangler Fig Pattern**。

When migrating build tools, it should not be viewed as a one-time "Big Bang" switch. Instead, adopt the **Strangler Fig Pattern**, similar to microservices migration.

-   **共存期 (Coexistence)**：專案根目錄同時存在 `pom.xml` 與 `build.gradle.kts`。
    **Coexistence**: Both `pom.xml` and `build.gradle.kts` exist in the project root.
-   **逐步接管 (Gradual Takeover)**：先讓 Gradle 負責部分子模組或特定任務（如測試、打包），CI Server 同時跑兩套驗證。
    **Gradual Takeover**: Let Gradle handle specific submodules or tasks (e.g., testing, packaging) first, with the CI Server validating both.
-   **完全替換 (Replacement)**：當 Gradle 建置穩定且效能超越 Maven 後，移除 `pom.xml`。
    **Replacement**: Once the Gradle build is stable and outperforms Maven, remove the `pom.xml`.

### 2.3 Kotlin DSL vs. Groovy DSL

早期的 Gradle 使用 Groovy，這是一種動態語言。雖然寫起來簡潔，但在大型專案中缺乏 IDE 的自動補全（Auto-completion）與重構支援。**Kotlin DSL** 引入了靜態型別，讓寫 Build Script 就像寫 Application Code 一樣，編譯器能幫你抓錯。

Early Gradle used Groovy, a dynamic language. While concise, it lacked IDE auto-completion and refactoring support in large projects. **Kotlin DSL** introduces static typing, making writing Build Scripts feel like writing Application Code, with the compiler helping to catch errors.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 遷移的商業價值與技術債 (Business Value & Technical Debt)

在系統設計面試或向高層匯報時，遷移建置工具不能只說是「因為 Gradle 比較潮」。必須連結到以下指標：

In system design interviews or reports to leadership, migrating build tools cannot be justified simply because "Gradle is trendy." It must be linked to the following metrics:

1.  **Feedback Loop Speed**：Gradle 的 Incremental Build 與 Build Cache 機制，通常能將大型 Monolith 的建置時間縮短 50%–90%。這直接影響開發者的生產力。
    **Feedback Loop Speed**: Gradle's Incremental Build and Build Cache mechanisms can often reduce build times for large Monoliths by 50%–90%. This directly impacts developer productivity.
2.  **CI/CD Cost**：更快的建置意味著更少的 CI Agent 佔用時間，直接節省雲端成本。
    **CI/CD Cost**: Faster builds mean less CI Agent occupation time, directly saving cloud costs.
3.  **Flexibility for Modern Stacks**：對於混合語言專案（如 Java Backend + Kotlin Mobile + React Frontend），Gradle 的多語言支援與插件生態系整合度較佳。
    **Flexibility for Modern Stacks**: For polyglot projects (e.g., Java Backend + Kotlin Mobile + React Frontend), Gradle's multi-language support and plugin ecosystem integration are superior.

### 3.2 大型系統中的依賴管理架構 (Dependency Management Architecture)

在微服務或多模組架構中，如何管理數百個依賴版本是關鍵。

In microservices or multi-module architectures, managing hundreds of dependency versions is critical.

-   **Maven**: 使用 `<dependencyManagement>` 與 BOM (Bill of Materials)。
    **Maven**: Uses `<dependencyManagement>` and BOM (Bill of Materials).
-   **Gradle Modern Practice**: 使用 **Version Catalogs (libs.versions.toml)**。這是 Gradle 7.0+ 的標準，讓依賴定義與建置邏輯分離，並可在多個專案間共享。
    **Gradle Modern Practice**: Uses **Version Catalogs (libs.versions.toml)**. This is the standard for Gradle 7.0+, allowing separation of dependency definitions from build logic and sharing across multiple projects.

---

## 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)

你有一個包含 20 個模組的 Legacy Java 專案，目前使用 Maven。目標是遷移到 Gradle Kotlin DSL，並引入 Version Catalogs。

You have a Legacy Java project with 20 modules, currently using Maven. The goal is to migrate to Gradle Kotlin DSL and introduce Version Catalogs.

### Step 1: 初始化與共存 (Initialization & Coexistence)

不要手動建立檔案。使用 Gradle 內建的轉換工具作為起點。

Do not create files manually. Use Gradle's built-in conversion tool as a starting point.

```bash
# 在專案根目錄執行
gradle init
```

選擇 `pom.xml` 作為轉換來源，並選擇 `Kotlin` 作為 DSL。這會產生初步的 `build.gradle.kts` 與 `settings.gradle.kts`。此時，`pom.xml` 依然存在且可運作。

Select `pom.xml` as the conversion source and choose `Kotlin` as the DSL. This generates the initial `build.gradle.kts` and `settings.gradle.kts`. At this point, `pom.xml` still exists and is functional.

### Step 2: 建立 Version Catalog (Create Version Catalog)

在 `gradle/libs.versions.toml` 建立依賴清單。這是現代化重構的重點。

Create the dependency list in `gradle/libs.versions.toml`. This is the focus of modernization.

```toml
# gradle/libs.versions.toml

[versions]
springBoot = "3.2.0"
jackson = "2.15.0"
junit = "5.10.0"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "springBoot" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "springBoot" }
```

### Step 3: 重構 build.gradle.kts (Refactor build.gradle.kts)

將自動產生的腳本重構為使用 Catalog 的形式。比較一下 Maven 與 Gradle Kotlin DSL 的寫法。

Refactor the auto-generated script to use the Catalog. Compare the syntax of Maven and Gradle Kotlin DSL.

**Legacy Maven (`pom.xml`):**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>${spring.boot.version}</version>
    </dependency>
</dependencies>
```

**Modern Gradle (`build.gradle.kts`):**

```kotlin
plugins {
    java
    // 使用 Catalog 中定義的 plugin
    alias(libs.plugins.spring.boot) 
}

dependencies {
    // Type-safe accessors generated from TOML
    implementation(libs.spring.boot.starter.web)
    implementation(libs.jackson.databind)
    testImplementation(libs.junit.jupiter)
}

tasks.test {
    useJUnitPlatform()
}
```

### Step 4: 驗證與效能調優 (Validation & Performance Tuning)

1.  **Parallel Execution**: 在 `gradle.properties` 中開啟 `org.gradle.parallel=true`。
    **Parallel Execution**: Enable `org.gradle.parallel=true` in `gradle.properties`.
2.  **Build Scan**: 執行 `./gradlew build --scan` 來視覺化建置效能瓶頸，這對比對 Maven 的建置時間非常有用。
    **Build Scan**: Run `./gradlew build --scan` to visualize build performance bottlenecks, which is very useful for comparing with Maven build times.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在 Kotlin DSL 中寫過多命令式邏輯 (Imperative Logic in Kotlin DSL)

*   **錯誤案例 (Bad)**：在 `build.gradle.kts` 中寫複雜的 `if-else` 或迴圈來處理檔案複製。
    **Bad**: Writing complex `if-else` or loops in `build.gradle.kts` to handle file copying.
*   **原因 (Why)**：這破壞了 Gradle 的 Configuration Cache，導致每次建置都要重新計算模型，變慢且難以維護。
    **Why**: This breaks Gradle's Configuration Cache, causing the model to be recalculated on every build, making it slow and hard to maintain.
*   **修正 (Fix)**：將邏輯封裝成自定義 Plugin 或 Task 類別，並明確宣告 Input/Output，讓 Gradle 能進行快取。
    **Fix**: Encapsulate logic into custom Plugins or Task classes, and explicitly declare Inputs/Outputs so Gradle can cache them.

### 5.2 忽略 CI 環境的 Cache 設定 (Ignoring CI Environment Cache)

*   **錯誤案例 (Bad)**：在本地端跑 Gradle 很快，但在 Jenkins/GitLab CI 上卻比 Maven 還慢。
    **Bad**: Gradle runs fast locally but is slower than Maven on Jenkins/GitLab CI.
*   **原因 (Why)**：Gradle 的效能優勢很大程度來自於 Local Daemon 和 Cache。CI Agent 通常是 Ephemeral（用完即丟）的，若沒掛載 Cache Volume，每次都要重新下載依賴並重新編譯。
    **Why**: Gradle's performance advantage largely comes from the Local Daemon and Cache. CI Agents are usually Ephemeral; without mounting a Cache Volume, dependencies are re-downloaded and re-compiled every time.
*   **修正 (Fix)**：設定 CI Pipeline 快取 `~/.gradle/caches` 和 `~/.gradle/wrapper`。
    **Fix**: Configure the CI Pipeline to cache `~/.gradle/caches` and `~/.gradle/wrapper`.

### 5.3 `allprojects` 與 `subprojects` 的濫用 (Abuse of `allprojects` and `subprojects`)

*   **錯誤案例 (Bad)**：在 Root `build.gradle.kts` 中使用 `subprojects { ... }` 注入所有依賴與插件。
    **Bad**: Using `subprojects { ... }` in the Root `build.gradle.kts` to inject all dependencies and plugins.
*   **原因 (Why)**：這導致子模組間的耦合度過高（Cross-project configuration），且會讓 Configuration Phase 變慢。
    **Why**: This leads to high coupling between submodules (Cross-project configuration) and slows down the Configuration Phase.
*   **修正 (Fix)**：使用 Convention Plugins（在 `buildSrc` 或 `build-logic` 中定義共用邏輯），讓每個子模組明確 apply 需要的 plugin。
    **Fix**: Use Convention Plugins (defined in `buildSrc` or `build-logic`) and let each submodule explicitly apply the plugins it needs.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如果要將一個大型 Monolith 從 Maven 遷移到 Gradle，你會如何規劃以確保風險最小化？
**How would you plan the migration of a large Monolith from Maven to Gradle to ensure minimal risk?**

*   **高分回答要點 (Key Points)**：
    *   **Strangler Fig Pattern**：強調雙軌並行，不建議一次性切換。
    *   **CI Pipeline Integration**：先在 CI 中建立 Gradle 步驟但不阻擋 Release，收集數據比對產出物（Artifacts）是否一致（Bit-for-bit comparison 雖難，但至少要確保 JAR 內容結構一致）。
    *   **Module-by-Module**：從依賴最少的底層模組（Leaf modules）開始。
    *   **Training**：提到團隊對 Kotlin DSL 的學習曲線管理。

### Q2: 為什麼 Gradle 在大型專案中通常比 Maven 快？什麼情況下會變慢？
**Why is Gradle generally faster than Maven in large projects? When might it be slower?**

*   **高分回答要點 (Key Points)**：
    *   **Incremental Builds**：Gradle 會檢查 Input/Output hash，只重新執行變更的 Task；Maven 主要是基於 Module 層級。
    *   **Build Cache**：Gradle 可以重用來自其他開發者或 CI 的建置結果（Remote Cache）。
    *   **Daemon**：常駐記憶體的 Process 避免 JVM 啟動開銷。
    *   **變慢的情況**：Configuration Cache 失效（腳本寫太爛）、CI 沒有設定 Cache、JVM Heap Size 設定過小。

### Q3: 請解釋 Gradle 的 Configuration Phase 與 Execution Phase 的區別，這對腳本效能有何影響？
**Explain the difference between Gradle's Configuration Phase and Execution Phase. How does this affect script performance?**

*   **高分回答要點 (Key Points)**：
    *   **Configuration Phase**：評估所有腳本，建立 Task Graph。任何寫在 Task 外部或 `project.afterEvaluate` 的程式碼都在此執行。
    *   **Execution Phase**：根據 Graph 執行具體的 Actions (`doLast`, `doFirst`)。
    *   **效能影響**：如果在 Configuration Phase 做耗時操作（如網路請求、IO），會拖慢**每一次**建置（即使只是跑 `./gradlew help`）。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 本章重點回顧 (Key Takeaways)

1.  **工具本質**：Maven 是基於約定的 XML 宣告；Gradle 是基於 DAG 的可程式化編排。
2.  **遷移策略**：採用 Strangler Fig 模式，讓 Maven 與 Gradle 共存，逐步替換。
3.  **現代化標準**：新專案或重構應全面採用 **Kotlin DSL** 與 **Version Catalogs**，以獲得最佳的 IDE 支援與依賴管理體驗。
4.  **效能關鍵**：善用 Incremental Build 與 Build Cache，並避免在 Configuration Phase 執行耗時邏輯。
5.  **CI/CD**：Gradle 的威力在 CI 環境中需要正確的 Cache 設定才能發揮。

### 後續延伸 (Next Steps)

*   **進階實作**：學習如何編寫 **Custom Gradle Plugins** 來封裝企業內部的建置邏輯（對應 Chapter 10）。
*   **效能分析**：深入研究 **Gradle Enterprise (Develocity)** 或免費的 Build Scans，學習如何診斷建置效能瓶頸。
*   **DevOps 整合**：探索如何將 Gradle 建置資訊整合進 Kubernetes 或 Docker Image 的 Metadata 中。