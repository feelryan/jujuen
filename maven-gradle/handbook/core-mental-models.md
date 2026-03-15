# 核心架構與心智模型：Maven Lifecycle vs Gradle Task Graph / Core Architecture & Mental Models: Maven Lifecycle vs Gradle Task Graph

## Mental model｜心智模型

理解這兩個工具的關鍵，在於從「如何看待建置過程」的根本哲學差異切入。

### 1. Maven: The Assembly Line (流水線工廠)
Maven 的核心是 **Convention over Configuration（約定優於配置）**。想像一條固定軌道的火車或工廠流水線。

- **Linear Phases (線性階段)**: 車站（Phases）是固定的（如 `validate`, `compile`, `test`, `package`, `install`, `deploy`）。你不能改變車站的順序，也不能隨意插入新車站。
- **Plugin Binding (插件掛載)**: 你能做的，是決定在某個車站「上下什麼貨物」。也就是將 Plugin 的 Goal 綁定到特定的 Phase 上。
- **Predictability (可預測性)**: 任何接手 Maven 專案的工程師，只要輸入 `mvn install`，都知道會發生什麼事。

> **Mental Image**: 一條單向通行的火車軌道。你只能決定在「台中站」要不要停下來買便當，但你不能把「台中站」搬到「台北站」前面。

### 2. Gradle: The Programmable Graph (可程式化圖形)
Gradle 的核心是 **Directed Acyclic Graph (DAG, 有向無環圖)**。想像你在寫一個腳本來指揮一群機器人。

- **Task Graph (任務圖)**: 沒有固定的流水線。建置過程是由一個個 Task 組成的節點，以及 Task 之間的依賴關係（Dependencies）構成的網狀圖。
- **Configuration vs. Execution (配置與執行)**: 這是 Gradle 最重要的心智模型。
    1.  **Configuration Phase**: Gradle 讀取所有腳本，建立 DAG 圖。**這時候不執行實際動作**。
    2.  **Execution Phase**: 根據 DAG 圖，按順序執行 Task 的 Action (`doLast`, `doFirst`)。
- **Flexibility (靈活性)**: 你可以創造任何 Task，並定義它依賴於誰。

> **Mental Image**: 一張導航地圖。你想去「目的地（Task）」，系統會根據地圖（DAG）算出你需要先經過哪些路口（Dependencies）。你可以隨意重新規劃路徑。

---

## Patterns & best practices｜常見模式與最佳實務

### Maven Patterns
1.  **Strict Phase Binding (嚴格階段綁定)**
    *   **Pattern**: 始終將自定義行為綁定到最合適的標準 Phase。
    *   **Example**: 程式碼生成（Code Gen）應綁定在 `generate-sources`；整合測試應綁定在 `integration-test` 與 `verify`，而不是 `test`（單元測試）。
    *   **Why**: 保持 `mvn clean install` 的語意正確性，避免破壞 CI/CD 流程。

2.  **Bill of Materials (BOM) Import**
    *   **Pattern**: 在 `<dependencyManagement>` 中使用 BOM 來統一控制依賴版本，而非在每個 `<dependency>` 中寫死版本號。
    *   **Why**: 這是 Maven 處理大型多模組專案依賴地獄（Dependency Hell）的標準解法。

### Gradle Patterns
1.  **Configuration Avoidance (配置迴避)**
    *   **Pattern**: 使用 `tasks.register(...)` 而不是 `tasks.create(...)`。
    *   **Why**: `register` 是惰性的（Lazy）。只有當該 Task 真的需要被執行（或被查詢）時，Gradle 才會去配置它。這能顯著提升大型專案的 Configuration Phase 速度。

2.  **Typed Tasks over Ad-hoc Scripts (類型化任務優於臨時腳本)**
    *   **Pattern**: 盡量編寫自定義的 Task Class（放在 `buildSrc` 或獨立 Plugin 中），而不是在 `build.gradle` 裡寫一大堆 `doLast { ... }` 腳本。
    *   **Why**: 這樣可以利用 Gradle 的 **Incremental Build（增量建置）** 機制（Input/Output 檢查），若檔案沒變，Task 就不會重跑 (`UP-TO-DATE`)。

3.  **Lifecycle Task Grouping (生命週期任務分組)**
    *   **Pattern**: 雖然 Gradle 沒有固定 Phase，但最佳實務是建立像 `build`, `check`, `publish` 這樣的 "Lifecycle Tasks"（本身不做事，只是依賴其他 Tasks），以模擬類似 Maven 的標準介面。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Maven: The "God Parent" Anti-pattern
- **Bad Practice**: 把所有可能的 Plugin 配置、Profile、甚至具體依賴都塞進 Parent POM。
- **Consequence**: 子模組繼承了大量不需要的建置邏輯，導致建置變慢，且難以除錯。
- **Fix**: Parent POM 僅負責 `pluginManagement` 和 `dependencyManagement`（版本控制），子模組按需引用。

### ❌ Gradle: Logic in Configuration Phase (最常見的初學者錯誤)
- **Bad Practice**: 把執行邏輯直接寫在 Task 的閉包（Closure）中，而不是 `doLast` 或 `doFirst` 區塊內。
- **Consequence**: **無論你執行哪個 Task**，這段程式碼都會在 Configuration Phase 被執行。這會導致建置極慢，甚至產生不可預期的副作用（如檔案被誤刪）。

```groovy
// ❌ WRONG: Prints every time, even on ./gradlew help
task badTask {
    println("I run during configuration!") 
}

// ✅ RIGHT: Runs only when requested
task goodTask {
    doLast {
        println("I run during execution!")
    }
}
```

### ❌ Gradle: Hard Dependencies on "clean"
- **Bad Practice**: 強制所有建置都依賴 `clean` (e.g., `dependsOn 'clean'`)。
- **Consequence**: 破壞了增量建置（Incremental Build）的優勢，導致每次建置都要重頭再來，浪費時間。
- **Fix**: 信任 Gradle 的 Input/Output 緩存機制。

---

## Checklists & workflows｜檢查清單與流程

在引入新工具或除錯建置問題時，請使用此檢查清單確認你的心智模型是否正確應用。

### Debugging Workflow (除錯流程)

- **Maven**:
  - [ ] **Check Effective POM**: 執行 `mvn help:effective-pom`。這是 Maven 的「最終真理」，能看到所有繼承和 Profile 合併後的結果。
  - [ ] **Visualize Dependency Tree**: 執行 `mvn dependency:tree` 確認依賴衝突。
  - [ ] **Debug Execution Order**: 使用 `mvn clean install -X` (Debug mode) 查看 Plugin 實際綁定到哪個 Phase 以及執行順序。

- **Gradle**:
  - [ ] **Visualize Task Graph**: 執行 `./gradlew <task> --dry-run` (或 `-m`)。這會告訴你 Gradle **打算** 執行哪些 Task 以及順序，但不會真的執行。
  - [ ] **Check Project Model**: 執行 `./gradlew model` 查看專案結構。
  - [ ] **Scan the Build**: 使用 `./gradlew build --scan`。這是 Gradle 最強大的除錯工具，能提供網頁版報告，分析 Configuration time vs Execution time。
  - [ ] **Verify Configuration Safety**: 檢查是否有耗時操作（HTTP request, File IO）發生在 Configuration Phase。

### Decision Tree: Maven vs Gradle?

1.  **專案是否極度標準化？** (e.g., 標準 Spring Boot CRUD)
    *   Yes -> **Maven** (簡單、穩定、IDE 支援度極高)。
2.  **是否需要高度客製化建置邏輯？** (e.g., Android App, 動態生成程式碼, 複雜的多語言編譯)
    *   Yes -> **Gradle** (強大的 DSL 與 API)。
3.  **團隊對 Groovy/Kotlin 的熟悉度？**
    *   Low -> **Maven** (XML 雖然繁瑣但門檻低)。
    *   High -> **Gradle** (Kotlin DSL 提供良好的型別檢查)。

---

## Real-world examples｜實戰案例

### Scenario: Adding a "Pre-compile" Code Generation Step
情境：我們需要在編譯 Java 程式碼之前，先執行一個腳本生成 Version 檔案。

#### Maven Approach (Bind to Phase)
在 Maven 中，我們必須找到 `compile` 之前的 Phase，通常是 `generate-sources`。

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>exec-maven-plugin</artifactId>
    <executions>
        <execution>
            <id>generate-version-file</id>
            <!-- 關鍵：明確綁定到 generate-sources 階段 -->
            <phase>generate-sources</phase>
            <goals>
                <goal>exec</goal>
            </goals>
            <configuration>
                <executable>./scripts/gen-version.sh</executable>
            </configuration>
        </execution>
    </executions>
</plugin>
```
*Mental Model check*: 我們把貨物（exec goal）掛載到了 `generate-sources` 這個車站。

#### Gradle Approach (Task Dependency)
在 Gradle 中，我們定義一個 Task，並告訴 `compileJava` 依賴它。

```kotlin
// build.gradle.kts

// 1. 定義 Task
val generateVersion by tasks.registering(Exec::class) {
    commandLine("./scripts/gen-version.sh")
    
    // 最佳實務：定義 Output，讓 Gradle 支援增量建置
    outputs.file(layout.buildDirectory.file("generated/version.txt"))
}

// 2. 建立依賴關係 (The Graph)
tasks.named("compileJava") {
    // 關鍵：明確告知 compileJava 必須在 generateVersion 之後跑
    dependsOn(generateVersion)
}
```
*Mental Model check*: 我們在圖（Graph）上畫了一條線，從 `compileJava` 指向 `generateVersion`。Gradle 解析圖形時會先執行被依賴者。