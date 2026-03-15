# 依賴管理機制與衝突解決實戰 / Dependency Management Mastery & Conflict Resolution

## Mental model｜心智模型

要掌握依賴管理，必須從「清單思維」轉變為「圖論思維」。

### 1. The Dependency Graph (依賴圖譜)
不要將依賴視為一個扁平的列表（Flat List），而是一個 **有向無環圖 (Directed Acyclic Graph, DAG)**。
- **Transitive Dependencies (傳遞性依賴)**：當你引入 `Library A`，而 `A` 依賴 `B`，`B` 就會自動進入你的 Classpath。這構成了樹狀結構。
- **The "Flattening" Problem**：JVM 的 Classpath 本質上是扁平的。當圖譜中出現兩個不同版本的 `Library B`（例如 `v1.0` 和 `v2.0`），建置工具必須決定保留哪一個，這就是衝突發生的根源。

### 2. Resolution Strategies: Maven vs. Gradle
兩大工具解決衝突的演算法本質不同，這是除錯時的關鍵心智模型：

| Feature | Maven Strategy | Gradle Strategy |
| :--- | :--- | :--- |
| **預設衝突解決** | **Nearest Definition Wins (路徑最短者優先)**。<br>若深度相同，則先宣告者優先。這意味著你在 `pom.xml` 頂層宣告的版本絕對生效。 | **Newest Version Wins (最新版本優先)**。<br>Gradle 會遍歷整個圖譜，預設選擇版號最高的版本，因為假設新版向下相容。 |
| **Scope 隔離** | 較為簡單 (Compile, Runtime, Test, Provided)。 | **Variant-aware resolution**。<br>區分 `api` (會傳遞) 與 `implementation` (不傳遞)，這不僅影響 Classpath，更直接影響編譯速度。 |

### 3. The "Bill of Materials" (BOM) Concept
將依賴版本視為「採購清單」而非「個別商品」。
- 在大型專案中，不應在個別模組指定版本。應透過 **BOM (Maven)** 或 **Platform / Version Catalog (Gradle)** 統一管理「版本集合」，確保所有模組使用的 Spring Boot 或 AWS SDK 版本一致。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Centralized Version Management (集中式版本管理)
永遠不要在多模組專案的子模組中 Hardcode 版本號。

- **Maven**: 使用 `<dependencyManagement>`。父 POM 定義版本，子 POM 只宣告依賴（不寫 `<version>`）。
- **Gradle**: 使用 **Version Catalogs (`libs.versions.toml`)**。這是 Gradle 7.0+ 的標準做法，它提供了類型安全（Type-safe）的依賴存取，並能在多個專案間共享。

### 2. Scope Precision (精準控制依賴範圍)
減少 Classpath 污染與 JAR 包大小的關鍵。

- **Gradle `implementation` vs `api`**:
  - 預設使用 `implementation`。這會隱藏依賴的內部實作，當該依賴變更時，不會觸發消費者的重新編譯（Recompile），顯著提升建置效能。
  - 僅當你需要將依賴的類別暴露給外部使用者時（例如在方法簽章中使用了該型別），才使用 `api`。
- **Provided / CompileOnly**:
  - 對於 Lombok 或 Servlet API 這類僅編譯時需要、或由容器提供的依賴，務必使用 Maven `<scope>provided</scope>` 或 Gradle `compileOnly`。

### 3. Handling Transitive Conflicts (處理傳遞性衝突)
- **Maven**: 使用 `<exclusions>` 排除特定分支的舊版依賴，或在 `<dependencyManagement>` 中強制指定版本（Bom pattern）。
- **Gradle**: 優先使用 `constraints` 來推薦或強制版本，而非暴力 exclude。
  ```kotlin
  dependencies {
      constraints {
          implementation("com.fasterxml.jackson.core:jackson-databind:2.13.0") {
              because("previous versions have security vulnerabilities")
          }
      }
  }
  ```

### 4. Semantic Versioning Alignment
確保你的團隊理解語意化版本（SemVer）。在 Gradle 中，可以設定 `ResolutionStrategy` 來自動拒絕不穩定的版本（如 `-SNAPSHOT` 或 `alpha`）進入 Release build。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Uber-Exclusion" (暴力排除)
- **Bad Practice**: 看到衝突就無腦使用 `exclude group: '*', module: '*'` 或者排除整個大 library。
- **Consequence**: 可能導致 `NoClassDefFoundError`，因為你排除了該 library 運作所需的其他核心依賴。應精準排除造成衝突的特定 artifact。

### 2. Leaking Test Dependencies (測試依賴洩漏)
- **Bad Practice**: 在 Maven 中忘記加 `<scope>test</scope>`，或在 Gradle 中誤用 `implementation` 引入 JUnit/Mockito。
- **Consequence**: 測試框架被打包進 Production Artifact，增加資安風險與檔案大小。

### 3. Maven's "Nearest Wins" Trap (Maven 最短路徑陷阱)
- **Scenario**: 你的專案依賴 `A (v1.0)`，`A` 依賴 `Jackson (v2.13)`。你又引入了 `B`，`B` 依賴 `C`，`C` 依賴 `Jackson (v2.6)`。
- **Pitfall**: 如果 `B -> C -> Jackson` 的路徑比 `A -> Jackson` 更短（或相同長度但先宣告），Maven 可能會選用舊版 `v2.6`，導致 `A` 在執行時拋出 `NoSuchMethodError`。
- **Fix**: 在 `<dependencyManagement>` 明確鎖定 `Jackson` 版本。

### 4. Dynamic Versions in Production (生產環境使用動態版本)
- **Bad Practice**: 使用 `1.2.+` 或 `latest.release`。
- **Consequence**: 不可重複的建置（Non-reproducible builds）。今天能跑的程式碼，明天因為依賴方發布新版就壞了。務必使用 **Dependency Locking** 機制鎖定具體版本。

---

## Checklists & workflows｜檢查清單與流程

### Conflict Resolution Workflow (衝突解決標準流程)

1.  **Detection (偵測)**: 建置失敗或 Runtime 噴錯 (`NoSuchMethodError`, `ClassNotFoundException`)。
2.  **Visualization (視覺化)**:
    - Maven: `mvn dependency:tree -Dverbose -Dincludes=groupId:artifactId`
    - Gradle: `./gradlew dependencies --configuration runtimeClasspath` 或使用 Build Scan (`./gradlew build --scan`)。
3.  **Analysis (分析)**: 找出誰引入了不同版本？是哪條路徑導致舊版被選中？
4.  **Resolution (解決)**:
    - **Option A (BOM/Platform)**: 透過 BOM 統一版本（推薦）。
    - **Option B (Force)**: 強制指定頂層版本。
    - **Option C (Exclude)**: 排除不需要的傳遞依賴（僅當該依賴確實不需要時）。
5.  **Verification (驗證)**: 重新執行 dependency tree 指令，確認最終解析版本為預期版本。

### Dependency Health Checklist (依賴健康度檢查)

- [ ] **License Audit**: 所有依賴的授權條款是否符合公司規範（如避免 AGPL 進入商業軟體）？
- [ ] **Security Scan**: 是否已掃描 CVE 漏洞（使用 OWASP Dependency Check 或 Snyk）？
- [ ] **Scope Validation**: 確認測試庫僅在 test scope，編譯工具僅在 provided/compileOnly scope。
- [ ] **Unused Check**: 是否有宣告了但未使用的依賴？（Gradle 可用 `gradle-lint-plugin` 或 `dependencyAnalysis` plugin 檢查）。
- [ ] **Convergence**: (Maven) 是否通過 `maven-enforcer-plugin` 的 `dependencyConvergence` 檢查？確保所有模組對同一依賴的版本共識一致。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Logging Hell" (SLF4J Multiple Bindings)
這是 Java 生態系最經典的衝突。專案同時引入了 `log4j-over-slf4j` 和 `slf4j-log4j12`，導致無窮遞迴或 StackOverflowError。

**Maven Solution (Exclusion Pattern):**
```xml
<dependency>
    <groupId>org.some-legacy-lib</groupId>
    <artifactId>legacy-core</artifactId>
    <version>1.0.0</version>
    <exclusions>
        <!-- 排除它自帶的舊版 logging binding -->
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### Scenario 2: Modern Gradle with Version Catalog
使用 `libs.versions.toml` 管理多模組專案的依賴，這是現代 Android 與 Spring Boot 專案的標準。

**File: `gradle/libs.versions.toml`**
```toml
[versions]
jackson = "2.15.2"
springBoot = "3.1.0"

[libraries]
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
jackson-kotlin = { module = "com.fasterxml.jackson.module:jackson-module-kotlin", version.ref = "jackson" }
# 定義一個 bundle 一次引入
jackson-bundle = ["jackson-databind", "jackson-kotlin"]

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "springBoot" }
```

**File: `build.gradle.kts` (Module Level)**
```kotlin
dependencies {
    // 優雅、類型安全、版本統一
    implementation(libs.bundles.jackson.bundle)
}
```

### Scenario 3: Enforcing Consistency with Maven Enforcer
在 CI/CD 階段強制失敗，如果發現依賴版本衝突。

**File: `pom.xml`**
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <executions>
        <execution>
            <id>enforce</id>
            <goals><goal>enforce</goal></goals>
            <configuration>
                <rules>
                    <dependencyConvergence/> <!-- 強制所有依賴版本必須收斂一致 -->
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```