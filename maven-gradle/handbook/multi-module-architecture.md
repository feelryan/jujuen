# 多模組專案架構設計模式 / Multi-Module Architecture Design Patterns

## Mental model｜心智模型

在進入語法細節之前，必須先建立正確的架構觀點。多模組（Multi-module）不僅僅是將程式碼分資料夾存放，它是關於 **「依賴邊界（Dependency Boundaries）」** 與 **「建置圖譜（Build Graph）」** 的設計。

### 1. The Build Graph (DAG)
無論是 Maven 還是 Gradle，多模組專案的核心都是一個 **有向無環圖（Directed Acyclic Graph, DAG）**。
- **節點（Nodes）**：代表你的模組（Modules/Projects）。
- **邊（Edges）**：代表依賴關係（Dependencies）。
- **關鍵點**：建置工具會根據這個圖來決定編譯順序與平行化策略。如果你的圖設計得太過扁平（所有人都依賴 core）或太過深長（長鏈依賴），都會影響建置效能與維護性。

### 2. Inheritance vs. Aggregation (繼承 vs. 聚合)
這是 Maven 使用者最容易混淆的概念，但在架構上至關重要：
- **聚合（Aggregation / Composition）**：回答「這個專案包含哪些部分？」。通常由 Root `pom.xml` 或 `settings.gradle` 定義。這是為了方便一次建置所有模組。
- **繼承（Inheritance）**：回答「這些模組共享什麼屬性？」。例如共享依賴版本、Plugin 設定。
- **Gradle 的觀點**：Gradle 傾向於使用 **Composition (Composite Builds)** 與 **Convention Plugins** 來取代傳統的繼承模式，強調「功能組合」而非「屬性繼承」。

### 3. The "Library" Mindset
將每個模組視為一個獨立發布的 Library。
- 即使你是在 Monorepo 中開發，模組 A 依賴模組 B 時，應該問自己：「如果 B 是第三方 Library，它的 API 設計合理嗎？它的依賴是否乾淨？」

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 依賴版本集中管理 (Centralized Version Management)
絕對不要在子模組中硬寫版本號。

- **Maven Pattern: The BOM (Bill of Materials)**
  - 使用 `<dependencyManagement>` 在 Parent POM 或獨立的 BOM 模組中定義所有依賴的版本。子模組只需宣告依賴，不需宣告版本。
  - **Why:** 確保所有模組使用相同版本的 Spring Boot 或 Jackson，避免 Classpath Hell。

- **Gradle Pattern: Version Catalogs (`libs.versions.toml`)**
  - 在 `gradle/libs.versions.toml` 定義所有依賴與 Plugin 版本。
  - 在 `build.gradle` 中以類型安全的方式引用：`implementation(libs.retrofit)`。
  - **Why:** 這是 Gradle 目前的標準做法，支援 IDE 自動補全且易於跨專案共享。

### 2. 結構分層模式 (Standard Layering)
一個典型的後端應用應該避免將所有東西丟進 `common`。推薦結構：

```text
root-project
├── build-logic (Gradle only: 自定義插件邏輯)
├── model (or api)      -> 純 POJO, DTO, Interfaces (無業務邏輯，極少依賴)
├── core (or domain)    -> 核心業務邏輯 (依賴 model)
├── infra               -> 資料庫實作, 外部 API Client (依賴 core)
└── application (or web)-> 啟動入口, Controller (聚合所有模組)
```

### 3. Gradle: Convention Plugins (慣例插件)
這是現代 Gradle 多模組架構的 **黃金標準**。
- **不要** 在 Root `build.gradle` 使用巨大的 `subprojects {}` 或 `allprojects {}` 區塊來注入邏輯（這會導致配置階段變慢且難以維護）。
- **要** 在 `build-logic` 目錄中撰寫自定義 Plugin（例如 `my-company.java-conventions`），讓子模組自行 apply 需要的 Plugin。

### 4. 模組間的 API 封裝 (Implementation Hiding)
- **Gradle**: 善用 `api` vs `implementation`。
  - `implementation`: 依賴不會傳遞給消費者（編譯隔離，加速建置）。
  - `api`: 依賴會洩漏給消費者（僅在必要時使用，如介面參數型別）。
- **Maven**: 雖然預設是傳遞依賴，但可使用 `<optional>true</optional>` 或 `<scope>provided</scope>` 來模擬類似效果，或透過 Maven Enforcer Plugin 強制檢查。

### 5. Gradle Composite Builds (複合建置)
當你的專案過大，或者你需要同時開發 Library 與 Application 時：
- 使用 `includeBuild` 將另一個獨立的 Git Repo 包含進目前的建置流程。
- 這允許你將龐大的 Monorepo 拆解成多個邏輯上的 Repo，但在開發時又能像單一專案一樣 Debug。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Common" Dumpster Fire (通用模組垃圾場)
- **現象**：建立一個名為 `common` 或 `utils` 的模組，把所有「不知道放哪」的程式碼都丟進去。
- **後果**：`common` 變得極其肥大，且依賴了各種不相干的 Library（同時依賴 AWS SDK, PDF 生成器, Kafka Client）。任何模組只要依賴 `common`，就繼承了這堆垃圾依賴。
- **解法**：按功能拆分，如 `common-logging`, `common-kafka`, `common-utils`。

### 2. Cyclic Dependencies (循環依賴)
- **現象**：模組 A 依賴 B，B 依賴 A（直接或間接）。
- **後果**：Maven 和 Gradle 都會直接報錯，建置失敗。這通常代表架構邊界劃分錯誤。
- **解法**：
  1. 提取介面（Interface）到第三個模組 C（A -> C, B -> C）。
  2. 使用依賴反轉原則（DIP）。

### 3. Leaky Abstractions via Parent POM (父層洩漏)
- **現象**：在 Parent POM 的 `<dependencies>` (注意不是 dependencyManagement) 中加入了具體的 Library（如 `lombok`, `logging`）。
- **後果**：專案中每一個子模組都強迫繼承了這些依賴，即使它們不需要。
- **原則**：Parent POM 應該只負責「管理（Management）」，儘量少負責「定義實體依賴」。

### 4. Split Packages (套件分裂)
- **現象**：在模組 A 和模組 B 中都定義了 `com.mycompany.service` 這個 package。
- **後果**：在 Java 9+ 模組化系統（JPMS）中會報錯，且容易造成 Classpath 載入順序導致的詭異 Bug。
- **原則**：一個 Package 應該只屬於一個模組。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Should I create a new module? (我該開新模組嗎？)
- [ ] **重用性 (Reusability)**: 這段程式碼會被兩個以上的其他模組使用嗎？ -> **Yes**
- [ ] **依賴隔離 (Dependency Isolation)**: 這段程式碼是否引入了很重的依賴（如 Kafka, gRPC），而我不希望其他部分受影響？ -> **Yes**
- [ ] **變更頻率 (Rate of Change)**: 這部分是否很少變動，而業務邏輯變動頻繁？（分開可利用 Cache 加速建置） -> **Yes**
- [ ] **邊界清晰 (Clear Boundary)**: 我能給這個模組一個明確的職責名稱嗎？（除了 "Common" 以外的名字） -> **Yes**
- **結論**：如果以上皆否，請保持在同一個模組內，避免過度工程化（Over-engineering）。

### Workflow: Extracting a Module (模組拆分流程)
1. **Identify**: 識別出高內聚的程式碼區塊。
2. **Isolate**: 嘗試將該區塊內的 class 改為 package-private，看是否有外部依賴報錯。
3. **Move**: 建立新模組目錄，移動程式碼。
4. **Declare**:
   - **Maven**: 在 Root POM 加入 `<module>`，在新模組建立 `pom.xml` 定義 parent。
   - **Gradle**: 在 `settings.gradle` 加入 `include`。
5. **Connect**: 在新模組宣告其所需的第三方依賴；在原模組宣告對新模組的依賴。
6. **Verify**: 執行 `./mvnw clean verify` 或 `./gradlew build --scan` 檢查依賴樹與循環依賴。

### Checklist: Dependency Health (依賴健康檢查)
- [ ] 是否使用了 BOM / Version Catalog 管理版本？
- [ ] `common` 模組是否過於肥大？
- [ ] 是否有模組使用了 `api` (Gradle) 但其實應該用 `implementation`？
- [ ] 是否有子模組覆蓋了 Parent 定義的版本號而未加註解說明？
- [ ] 執行 `mvn dependency:tree` 或 `gradle dependencies` 是否看到意外的傳遞依賴？

---

## Real-world examples｜實戰案例

### Example 1: Modern Gradle Setup with `build-logic`
這是目前大型 Gradle 專案（如 Android 官方推薦架構）的標準起手式。

**File Structure:**
```text
/
├── settings.gradle.kts      // includeBuild("build-logic")
├── gradle/libs.versions.toml // 定義 versions
├── build-logic/             // 獨立的 Composite Build
│   ├── settings.gradle.kts
│   └── src/main/kotlin/
│       ├── my.java-conventions.gradle.kts // 定義 Java 版本, Checkstyle 等
│       └── my.library-conventions.gradle.kts // 定義 Library 通用設定
├── core/
│   └── build.gradle.kts     // plugins { id("my.library-conventions") }
└── app/
    └── build.gradle.kts     // plugins { id("my.java-conventions") }
```
**Concept**: 將建置邏輯（Build Logic）視為原始碼的一部分，並封裝成 Plugin。這樣 `core` 和 `app` 的 build script 會變得非常乾淨，只有依賴宣告。

### Example 2: Maven Aggregator vs Parent
很多開發者會把這兩者混在同一個 `pom.xml`，雖然可行，但在大型專案建議分開。

**Scenario**: 公司有多個微服務，希望共享設定，但分開建置。

1.  **Corporate Parent POM** (獨立 Git Repo, 獨立發布):
    - 定義 `<dependencyManagement>`, `<build><pluginManagement>`, Checkstyle 規則, Nexus URL。
    - 這是所有專案的 "基底"。

2.  **Service A (Multi-module)**:
    - **Root POM**:
        - `<parent>` 指向 Corporate Parent POM。
        - `<modules>` 包含 `api`, `service`, `worker`。
        - `<packaging>pom</packaging>`。
    - **Sub-module POM**:
        - `<parent>` 指向 Service A Root POM。

這種 **雙層繼承（Corporate -> Service Root -> Module）** 模式在企業級環境非常常見，能兼顧全公司規範與單一專案的靈活性。