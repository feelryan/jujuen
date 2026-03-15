# 1. 前言與學習目標 (Introduction & Learning Goals)

在資深工程師的職涯中，建置工具（Build Tools）往往被視為隱形的基礎設施。然而，當系統擴展至數十個微服務或大型 Monorepo 時，不良的模組設計將導致編譯時間呈指數級增長，並引發「相依性地獄（Dependency Hell）」。本章專注於 **Maven Reactor** 與 **Gradle Composite Builds** 的架構設計，旨在解決大型專案的耦合與效率問題。

In the career of a Senior Software Engineer, build tools are often viewed as invisible infrastructure. However, as systems scale to dozens of microservices or large Monorepos, poor module design leads to exponential growth in build times and triggers "Dependency Hell." This chapter focuses on the architectural design of **Maven Reactor** and **Gradle Composite Builds**, aiming to solve coupling and efficiency issues in large-scale projects.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **設計可擴展的模組架構**：區分 Maven Reactor 與 Gradle Composite Builds 的適用場景，並針對 Monorepo 選擇最佳策略。
    **Design scalable module architectures**: Distinguish between Maven Reactor and Gradle Composite Builds scenarios, and select the optimal strategy for Monorepos.
2.  **優化編譯效能與相依性圖譜**：利用 DAG（有向無環圖）原理優化平行構建，並透過 BOM (Maven) 或 Version Catalogs/Platforms (Gradle) 統一管理版本。
    **Optimize build performance and dependency graphs**: Leverage DAG (Directed Acyclic Graph) principles to optimize parallel builds, and unify version management via BOM (Maven) or Version Catalogs/Platforms (Gradle).
3.  **解決循環依賴與類別路徑洩漏**：識別並重構導致循環依賴的模組，並正確使用 `api` vs `implementation` 以封裝模組內部細節。
    **Resolve circular dependencies and classpath leakage**: Identify and refactor modules causing circular dependencies, and correctly use `api` vs `implementation` to encapsulate module internals.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 建置即圖譜 (Build as a DAG)

無論是 Maven 還是 Gradle，核心運作機制都是建立一個 **有向無環圖（Directed Acyclic Graph, DAG）**。
Both Maven and Gradle operate by constructing a **Directed Acyclic Graph (DAG)**.

-   **Maven Reactor**：讀取所有模組的 `pom.xml`，計算依賴順序，決定構建路徑。它本質上是一個單一的繼承樹與聚合結構。
    **Maven Reactor**: Reads all module `pom.xml` files, calculates dependency order, and determines the build path. It is essentially a single inheritance tree and aggregation structure.
-   **Gradle Task Graph**：Gradle 的粒度更細，是基於 Task 的 DAG。而在 **Composite Builds** 中，它允許將多個獨立的構建（Builds）組合成一個大的構建，這比 Maven 的 Reactor 更靈活，因為每個被包含的構建（Included Build）都是獨立的。
    **Gradle Task Graph**: Gradle operates at a finer granularity, based on a Task DAG. In **Composite Builds**, it allows combining multiple independent builds into one large build. This is more flexible than Maven's Reactor because each "Included Build" stands alone.

## 2.2 依賴管理的兩種模型 (Two Models of Dependency Management)

在多模組設計中，我們必須區分「定義（Definition）」與「解析（Resolution）」。
In multi-module design, we must distinguish between "Definition" and "Resolution".

1.  **繼承模型 (Inheritance - Maven Parent POM)**：
    子模組繼承父模組的配置。這很直觀，但容易造成「父模組過重（God Parent）」，導致所有子模組都繼承了不需要的依賴。
    **Inheritance Model (Maven Parent POM)**:
    Child modules inherit configuration from the parent. This is intuitive but prone to the "God Parent" anti-pattern, where child modules inherit unnecessary dependencies.

2.  **組合模型 (Composition - Gradle Composite Builds / Maven BOM)**：
    -   **Maven BOM (Bill of Materials)**：透過 `<dependencyManagement>` 僅引入版本定義，而不強迫繼承依賴。
    -   **Gradle Composite Builds**：將一個獨立專案（如內部的 Common Library）直接 `include` 到當前專案中。Gradle 會自動將二進位依賴（Binary Dependency）替換為專案依賴（Project Dependency），這對於同時開發 Library 和 Application 的場景極為強大。
    **Composition Model (Gradle Composite Builds / Maven BOM)**:
    -   **Maven BOM**: Imports version definitions via `<dependencyManagement>` without forcing dependency inheritance.
    -   **Gradle Composite Builds**: Directly `include` an independent project (like an internal Common Library) into the current project. Gradle automatically substitutes the binary dependency with the project dependency, which is powerful for developing a Library and Application simultaneously.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 Monorepo 中的角色 (Role in Monorepo)

在現代微服務架構或模組化單體（Modular Monolith）中，多模組設計決定了開發體驗（DevEx）與 CI/CD 效率。
In modern microservices architectures or Modular Monoliths, multi-module design dictates Developer Experience (DevEx) and CI/CD efficiency.

-   **API vs Implementation Separation**：
    透過多模組強制分離介面與實作。例如，`order-service-api` 模組只包含 DTOs 和 Interfaces，供其他服務依賴；而 `order-service-impl` 包含業務邏輯與 DB 存取，不對外暴露。
    **API vs Implementation Separation**:
    Enforce separation of interface and implementation via multi-modules. For example, an `order-service-api` module contains only DTOs and Interfaces for other services to depend on; whereas `order-service-impl` contains business logic and DB access, hidden from the outside.

-   **CI/CD 增量構建 (Incremental Builds)**：
    設計良好的模組圖譜允許 CI 系統（如 Jenkins, GitHub Actions）只測試與構建「受影響的模組及其下游」。若模組間耦合過高，改一行程式碼就必須重跑整個系統的測試，這在大型組織中是無法接受的。
    **CI/CD Incremental Builds**:
    A well-designed module graph allows CI systems (like Jenkins, GitHub Actions) to test and build only "affected modules and their downstream consumers." If coupling is too tight, changing one line of code forces a rebuild of the entire system, which is unacceptable in large organizations.

## 3.2 架構圖示 (Architecture Visualization)

想像一個典型的分層架構：
Imagine a typical layered architecture:

```text
[Root Project]
 ├── build-logic (Gradle) / parent-pom (Maven)  <-- 統一建置邏輯與版本
 ├── platform-bom                               <-- 定義所有第三方依賴版本
 ├── libs                                       <-- 共用函式庫
 │    ├── common-utils
 │    └── security-lib
 ├── services                                   <-- 業務服務
 │    ├── user-service
 │    │    ├── user-api (depends on common-utils)
 │    │    └── user-impl (depends on user-api, security-lib)
 │    └── payment-service
 └── legacy-system (Isolated via Composite Build)
```

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：從混亂到 Gradle Composite Builds (Scenario: From Chaos to Gradle Composite Builds)

### 背景 (Context)
你的團隊維護一個核心函式庫 `company-common-lib` 和多個微服務。每次修改 `common-lib`，你需要：
1. 修改 Lib 程式碼。
2. `mvn deploy` 發布 SNAPSHOT 版本。
3. 在微服務專案更新依賴版本。
4. 重新整理 IDE。
這流程非常慢且容易出錯。

Your team maintains a core library `company-common-lib` and multiple microservices. Every time you modify `common-lib`, you need to:
1. Modify Lib code.
2. `mvn deploy` to publish a SNAPSHOT version.
3. Update dependency versions in the microservice project.
4. Refresh the IDE.
This process is slow and error-prone.

### 解決方案：Gradle Composite Builds (Solution)

我們不發布 SNAPSHOT，而是告訴 Gradle：**「在這個構建中，如果看到 `com.company:common-lib` 的依賴，請直接用本地原始碼編譯並替換它。」**

Instead of publishing SNAPSHOTs, we tell Gradle: **"In this build, if you see a dependency on `com.company:common-lib`, replace it directly with the local source code compilation."**

#### 步驟 1: 專案結構 (Project Structure)

假設目錄結構如下：
Assume the directory structure is as follows:

```text
/workspace
  /company-common-lib  (Independent Gradle project)
  /user-service        (Depends on company-common-lib:1.0.0)
```

#### 步驟 2: 配置 User Service (Configure User Service)

在 `user-service/settings.gradle.kts` 中，我們使用 `includeBuild`。
In `user-service/settings.gradle.kts`, we use `includeBuild`.

```kotlin
rootProject.name = "user-service"

// 正常包含內部的模組
include("user-api", "user-impl")

// 關鍵：將外部的獨立專案包含進來作為 Composite Build
// Key: Include the external independent project as a Composite Build
includeBuild("../company-common-lib") {
    dependencySubstitution {
        // 強制將二進位依賴替換為專案依賴
        // Force substitution of binary dependency with project dependency
        substitute(module("com.company:common-lib"))
            .using(project(":")) // 指向 company-common-lib 的 root project
    }
}
```

#### 步驟 3: 驗證效果 (Verification)

當你在 `user-service` 執行 `./gradlew build` 時：
1. Gradle 檢測到 `user-service` 依賴 `com.company:common-lib:1.0.0`。
2. 根據 `includeBuild` 規則，它攔截請求。
3. 它編譯 `../company-common-lib` 的原始碼。
4. 將編譯產物直接放入 `user-service` 的 classpath。

When you run `./gradlew build` in `user-service`:
1. Gradle detects `user-service` depends on `com.company:common-lib:1.0.0`.
2. Based on `includeBuild` rules, it intercepts the request.
3. It compiles the source code of `../company-common-lib`.
4. It puts the compiled artifacts directly into `user-service`'s classpath.

**優勢 (Benefits)**：
- **Zero Latency**：修改 Lib 後無需發布，直接在 Service 端生效。
- **Isolation**：Lib 仍然是獨立專案，擁有自己的 CI 流程。
- **IDE Support**：IntelliJ IDEA 支援此模式，你可以直接跳轉（Jump to Definition）到 Lib 的原始碼進行編輯。

**Maven 對應方案**：Maven 沒有完全等價的 Composite Builds。通常透過 **Multi-Module Project (Reactor)** 將 Lib 和 Service 放在同一個 Parent 下，或是使用 IDE 的 "Link Maven Projects" 功能，但靈活性不如 Gradle。

**Maven Equivalent**: Maven doesn't have a fully equivalent Composite Build feature. Usually, this is handled via a **Multi-Module Project (Reactor)** by putting Lib and Service under the same Parent, or using IDE features like "Link Maven Projects," but it lacks Gradle's flexibility.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 循環依賴 (Circular Dependencies)

-   **現象**：Module A 依賴 Module B，Module B 又依賴 Module A。Maven/Gradle 會直接報錯並停止構建。
    **Symptom**: Module A depends on Module B, and Module B depends on Module A. Maven/Gradle will fail immediately.
-   **反模式**：使用 "Cycle Breaker" 類型的 hack 手段，或者將所有類別合併到一個巨型模組中以規避問題。
    **Anti-pattern**: Using "Cycle Breaker" hacks, or merging all classes into a giant module to bypass the issue.
-   **解決方案**：
    1.  **萃取介面 (Extract Interface)**：建立 Module C (API)，讓 A 和 B 都依賴 C。
    2.  **事件驅動 (Event Driven)**：解耦直接調用，改用內部事件匯流排（Event Bus）。

## 5.2 依賴洩漏 (Leaking Dependencies)

-   **現象**：Gradle 中濫用 `compile` (已廢棄) 或 `api`。例如，`common-lib` 內部使用了 `Jackson`，並透過 `api` 暴露出去。依賴 `common-lib` 的 `user-service` 不小心直接使用了 `Jackson` 的類別。當 `common-lib` 升級或更換 JSON 庫時，`user-service` 編譯失敗。
    **Symptom**: Misusing `compile` (deprecated) or `api` in Gradle. For instance, `common-lib` uses `Jackson` internally and exposes it via `api`. `user-service`, depending on `common-lib`, accidentally uses `Jackson` classes directly. When `common-lib` upgrades or switches JSON libraries, `user-service` breaks.
-   **解決方案**：
    -   嚴格使用 `implementation`：依賴不會傳遞給消費者。
    -   僅對真正需要暴露的介面模組使用 `api`。
    **Solution**:
    -   Strictly use `implementation`: Dependencies are not transitive to consumers.
    -   Only use `api` for interface modules that explicitly need to expose types.

## 5.3 巨型父層 (God Parent POM / Root Project)

-   **現象**：在 Root `build.gradle` 或 Parent `pom.xml` 中定義了所有子模組的依賴和插件。
    **Symptom**: Defining all dependencies and plugins for all submodules in the Root `build.gradle` or Parent `pom.xml`.
-   **後果**：建置變慢，且簡單的 `utils` 模組可能意外引入了 `spring-boot-starter-web` 及其所有依賴。
    **Consequence**: Slow builds, and a simple `utils` module might accidentally pull in `spring-boot-starter-web` and all its dependencies.
-   **解決方案**：使用 **Convention Plugins** (Gradle `buildSrc` 或 `build-logic`) 或 **BOM** (Maven) 來管理版本，但在各個模組中按需宣告依賴。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何優化大型 Monorepo 的構建時間？
**How do you optimize build time for a large Monorepo?**

*   **高分回答要點 (Key Points)**：
    1.  **增量構建 (Incremental Build)**：確保 Input/Output 緩存配置正確。
    2.  **並行執行 (Parallel Execution)**：Maven `-T` 或 Gradle `org.gradle.parallel=true`。
    3.  **遠端緩存 (Remote Build Cache)**：特別是 Gradle Enterprise 或 Develocity，讓開發者共享 CI 的構建產物。
    4.  **模組化策略**：避免過大的單一模組，將變動頻率高的程式碼與穩定的程式碼分離。

## Q2: 解釋 Gradle 中 `api` 與 `implementation` 的區別，以及它對編譯效率的影響。
**Explain the difference between `api` and `implementation` in Gradle, and its impact on build efficiency.**

*   **高分回答要點 (Key Points)**：
    1.  **可見性 (Visibility)**：`api` 會傳遞依賴（Transitive），`implementation` 不會。
    2.  **編譯類別路徑 (Compile Classpath)**：使用 `implementation` 依賴的模組發生變更時，消費者不需要重新編譯（因為消費者看不見其實作細節），只需重新打包（Runtime Classpath）。
    3.  **結論**：`implementation` 能顯著減少大型專案的重新編譯範圍（Recompilation Scope），提升構建速度。

## Q3: 在微服務架構中，如何管理跨服務的共用依賴版本？
**In a microservices architecture, how do you manage shared dependency versions across services?**

*   **高分回答要點 (Key Points)**：
    1.  **Maven BOM / Gradle Platform**：建立一個獨立的 Platform 專案，定義所有依賴的版本號。
    2.  **發布流程**：所有微服務依賴這個 Platform/BOM，而不是各自寫死版本號。
    3.  **自動化更新**：配合 Renovate 或 Dependabot 自動升級 Platform 版本。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **DAG 是核心**：理解構建工具如何建立有向無環圖，是優化構建的基礎。
2.  **Composite Builds 勝於 SNAPSHOTs**：在 Gradle 中，優先使用 Composite Builds 進行多專案協同開發，避免 SNAPSHOT 帶來的版本混亂與延遲。
3.  **API vs Impl**：嚴格區分介面與實作模組，並正確使用 `implementation` 來縮減編譯路徑。
4.  **集中版本，分散依賴**：使用 BOM 或 Platform 統一管理版本號，但在各模組中按需引入依賴。
5.  **避免循環依賴**：這是架構設計不良的警訊，應透過介面萃取或事件機制解決。

## 後續延伸 (Next Steps)
-   **進階實作**：學習如何編寫 **Custom Gradle Plugins** (Kotlin DSL)，將重複的構建邏輯（如 Checkstyle, Docker publish）封裝成插件。
-   **CI/CD 整合**：研究如何在 Jenkins 或 GitHub Actions 中實作 **Affected Module Detection**，只針對變更模組跑測試。
-   **閱讀下一章**：`chapter04` - **Containerization & Orchestration (Docker/K8s)**，將我們構建好的模組打包並部署到雲端環境。