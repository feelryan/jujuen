# 工具遷移與現代化重構指南 / Migration Strategies & Modernization Guide

## Mental model｜心智模型

### 1. 翻譯 vs. 重構 (Translation vs. Refactoring)
遷移建置工具（例如 Maven 到 Gradle）不應被視為單純的「語法翻譯」。
- **Maven** 是 **宣告式 (Declarative)** 的 XML，它描述了「專案是什麼 (What the project is)」。
- **Gradle** 是 **程式化 (Programmable)** 的腳本，它描述了「建置如何發生 (How the build happens)」。
- **心智模型轉換**：從填寫靜態表格 (Filling a form) 轉變為編寫軟體 (Writing software)。遷移過程是償還技術債的機會，應將建置邏輯視為 Production Code 一樣對待，進行模組化與重構。

### 2. 漸進式現代化 (Incremental Modernization)
不要試圖進行 "Big Bang" 式的遷移。現代化是一個光譜：
1.  **Coexistence (共存期)**: Maven 與 Gradle 並存，CI 逐步切換。
2.  **Parity (功能對齊)**: 確保產出的 Artifacts 二進位兼容。
3.  **Idiomatic Adoption (慣用寫法採用)**: 從 Groovy 轉向 Kotlin DSL，引入 Version Catalogs。
4.  **Performance Tuning (效能調優)**: 啟用 Configuration Cache 與 Build Cache。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Maven to Gradle: The "Side-by-Side" Pattern
在遷移大型單體 (Monorepo) 或多模組專案時，保持兩個系統同時運作。
- **實作**：保留 `pom.xml`，同時引入 `settings.gradle.kts` 與 `build.gradle.kts`。
- **驗證**：使用腳本比對兩者產出的 JAR/WAR 檔案內容（排除 timestamp 差異）。
- **切換**：先將 CI 的驗證步驟 (Verify) 切換為 Gradle，最後才切換發布步驟 (Publish)。

### 2. Groovy to Kotlin DSL: Type-Safe Build Logic
從動態型別的 Groovy 遷移到靜態型別的 Kotlin DSL (`.kts`) 是現代化的關鍵。
- **Pattern**: 優先遷移 `settings.gradle` -> `settings.gradle.kts`，接著是 Root `build.gradle`，最後是子模組。
- **Best Practice**: 不要將複雜邏輯寫在 `.kts` 檔案中。將邏輯提取到 `buildSrc` 或獨立的 `build-logic` 複合建置 (Composite Build) 中，以 Kotlin Plugin 的形式引用。這能大幅提升 IDE 補全支援與編譯速度。

### 3. Dependency Management Modernization (Version Catalogs)
現代 Gradle (7.4+) 應全面採用 **Version Catalogs (`libs.versions.toml`)**。
- 取代傳統的 `ext` 變數或 `buildSrc` 常數管理依賴版本。
- 這讓依賴管理標準化，且易於被 Dependabot 或 Renovate 等工具自動更新。
- **Maven 對應**：這相當於 Maven 的 `<dependencyManagement>` 加上 BOM，但更靈活且可跨專案共享。

### 4. JDK Upgrade Strategy: Toolchains
處理 JDK 升級（如 JDK 8 -> 17/21）時，**Gradle Toolchains** 是最佳解法。
- **解耦**：將「執行 Gradle 的 JDK」與「編譯專案的 JDK」分開。
- **自動化**：Gradle 可以自動下載並配置指定版本的 JDK，確保團隊成員與 CI 環境的一致性，無需手動設定 `JAVA_HOME`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Script Soup" (腳本大雜燴)
- **現象**：在 `build.gradle.kts` 中編寫大量 imperative code（if/else, 迴圈），試圖模擬 Maven AntRun plugin 或複雜的 Shell script。
- **後果**：破壞 Gradle 的 Configuration Cache，導致建置變慢，且難以維護。
- **修正**：將邏輯封裝成 Custom Task 或 Plugin。

### 2. Ignoring Scope Mapping (忽視依賴範圍對應)
- **現象**：將 Maven 的 `<scope>compile</scope>` 全部轉為 Gradle 的 `implementation`，或全部轉為 `api`。
- **後果**：
    - 全部 `api`：導致 Classpath 洩漏 (Leaking)，編譯速度變慢（因為改動會連鎖觸發重新編譯）。
    - 全部 `implementation`：下游模組編譯失敗。
- **修正**：嚴格區分 `api` (會暴露給消費者) 與 `implementation` (內部實作細節)。

### 3. The "Snapshot" Trap during Migration
- **現象**：在遷移過程中依賴 `SNAPSHOT` 版本或動態版本 (`1.0.+`)。
- **後果**：Maven 和 Gradle 解析 Snapshot 的時間點或策略可能不同，導致 "It works on my machine" 但 CI 失敗，或兩邊建置結果不一致。
- **修正**：遷移期間鎖定具體版本 (Dependency Locking)。

### 4. Groovy/Kotlin Hybrid Confusion
- **現象**：在 Kotlin DSL 中試圖使用 Groovy 的動態特性（如直接呼叫字串名稱的 task）。
- **後果**：編譯錯誤，因為 Kotlin DSL 需要強型別存取 (Accessors)。
- **修正**：使用 `tasks.named("taskName")` 或類型安全的 Accessors。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Maven to Gradle Migration
1. **Preparation**:
   - [ ] 執行 `mvn clean install` 確保專案目前是健康的。
   - [ ] 整理依賴樹 (`mvn dependency:tree`)，移除未使用的依賴。
2. **Initialization**:
   - [ ] 執行 `gradle init --type pom` (自動轉換工具僅供起步，產出通常需要手動修正)。
   - [ ] 設定 `settings.gradle.kts` 包含所有模組。
3. **Configuration**:
   - [ ] 設定 **Version Catalog** (`libs.versions.toml`) 並遷移依賴版本。
   - [ ] 設定 **Toolchain** 以鎖定 JDK 版本。
   - [ ] 處理 Maven Plugins 對應 (如 Surefire -> Test task, Shade -> Shadow plugin)。
4. **Verification**:
   - [ ] 比較 Artifacts：`diff -r maven-target/ gradle-build/`。
   - [ ] 驗證測試報告：確保測試通過數量一致。

### Checklist: Groovy to Kotlin DSL Migration
- [ ] **單引號轉雙引號**：將所有 `'string'` 改為 `"string"`。
- [ ] **括號標準化**：方法呼叫加上括號，如 `implementation 'lib'` -> `implementation("lib")`。
- [ ] **Plugins Block**：確保使用 `plugins { id("...") }` 語法。
- [ ] **Task Configuration**：
    - Groovy: `test { ... }`
    - Kotlin: `tasks.test { ... }` 或 `tasks.withType<Test> { ... }`
- [ ] **Property Assignment**：
    - Groovy: `sourceCompatibility = 1.8`
    - Kotlin: `sourceCompatibility = JavaVersion.VERSION_1_8` (或使用 `=` 賦值給 var，使用 `.set()` 賦值給 Property)。

### Checklist: JDK Upgrade (e.g., to JDK 17/21)
- [ ] **Gradle Version**：升級 Gradle 到支援該 JDK 的版本 (JDK 17 需 Gradle 7.3+)。
- [ ] **Dependencies**：升級 Bytecode 操作相關庫 (Lombok, ASM, CGLIB, ByteBuddy)。
- [ ] **JVM Args**：檢查是否需要 `--add-opens` (針對 JDK 16+ 的模組化封裝)。
- [ ] **Toolchain**：
  ```kotlin
  java {
      toolchain {
          languageVersion.set(JavaLanguageVersion.of(17))
      }
  }
  ```

---

## Real-world examples｜實戰案例

### Example 1: Migrating Dependency Management (Maven to Gradle Version Catalog)

**Legacy (Maven `pom.xml`):**
```xml
<properties>
    <jackson.version>2.13.0</jackson.version>
</properties>
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>${jackson.version}</version>
</dependency>
```

**Modern (Gradle `libs.versions.toml` + `build.gradle.kts`):**

*file: gradle/libs.versions.toml*
```toml
[versions]
jackson = "2.13.0"

[libraries]
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
jackson-kotlin = { module = "com.fasterxml.jackson.module:jackson-module-kotlin", version.ref = "jackson" }

[bundles]
jackson = ["jackson-databind", "jackson-kotlin"]
```

*file: build.gradle.kts*
```kotlin
dependencies {
    implementation(libs.bundles.jackson)
}
```
*Benefit: Type-safe auto-completion in IDE, centralized management.*

### Example 2: Handling JDK 17 Encapsulation Issues
當升級到 JDK 17+ 時，舊的測試框架或 Lombok 可能會報錯 `InaccessibleObjectException`。

**Fix in `build.gradle.kts`:**
```kotlin
tasks.withType<Test> {
    jvmArgs(
        "--add-opens", "java.base/java.lang=ALL-UNNAMED",
        "--add-opens", "java.base/java.util=ALL-UNNAMED"
    )
}
```

### Example 3: Configuring a Composite Build for Logic Reuse
為了避免 `build.gradle.kts` 變成 "Script Soup"，建立一個 `build-logic` 專案。

**Structure:**
```text
root/
├── build-logic/
│   ├── settings.gradle.kts
│   ├── build.gradle.kts
│   └── src/main/kotlin/com.company.java-conventions.gradle.kts
├── settings.gradle.kts (includeBuild("build-logic"))
└── app/
    └── build.gradle.kts (plugins { id("com.company.java-conventions") })
```
*這將建置邏輯編譯為 Plugin，提供更佳的效能與嚴格的封裝。*