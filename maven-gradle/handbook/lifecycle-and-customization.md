# 生命週期控制與客製化邏輯 / Lifecycle Control & Custom Logic

此章節探討如何介入 Maven 與 Gradle 的建置流程。這是從「使用者」跨越到「工程師」的關鍵分水嶺：不再只是執行 `mvn clean install` 或 `./gradlew build`，而是懂得如何在特定的時間點插入自定義的程式碼生成、Docker 映像檔建置、或環境檢查邏輯。

---

## Mental model｜心智模型

理解兩者在生命週期管理上的根本差異，是避免「寫出維護惡夢」的第一步。

### 1. Maven: The Train Schedule (火車時刻表)
Maven 的生命週期是**線性且剛性**的。
- **概念**：想像一條固定的鐵路軌道（Lifecycle），上面有固定的車站（Phases: `validate`, `compile`, `test`, `package`, `deploy`）。
- **機制**：你不能改變車站的順序，也不能隨意新增車站。你唯一能做的是將貨物（Plugins/Goals）堆放到特定的車站上。當火車開過該車站時，貨物就會被處理。
- **限制**：如果你需要一個不在標準流程內的步驟（例如「在測試前啟動 DB」），你必須找到最接近的現有 Phase（如 `pre-integration-test`）並將 Plugin 綁定上去。

### 2. Gradle: The Two-Pass Graph (兩階段圖形)
Gradle 的執行模型是**有向無環圖 (DAG)**，且分為兩個截然不同的階段。
- **概念**：想像你在畫一張流程圖。任務（Task）之間透過 `dependsOn` 連結。
- **關鍵機制：Configuration vs. Execution**（這是 90% Gradle 新手的死穴）：
    1.  **Configuration Phase (規劃階段)**：Gradle 讀取所有 `build.gradle`，建構出 Task Graph。這時候**不執行**任何實際建置動作（不編譯、不搬檔），只決定「要做什麼」。
    2.  **Execution Phase (執行階段)**：根據上一步畫出的圖，依序執行 Task 的 `doLast` 或 `doFirst` 區塊內的程式碼。
- **彈性**：你可以隨意插入 Task，重新導向依賴關係，甚至在 Configuration 階段動態產生 Task。

---

## Patterns & best practices｜常見模式與最佳實務

### Maven Patterns

#### 1. 明確綁定執行階段 (Explicit Execution Binding)
不要依賴 Plugin 的預設 Phase，即使它有預設值。明確寫出 `<phase>` 可以讓閱讀 POM 的人一眼看出邏輯發生在何時。

```xml
<plugin>
    <artifactId>maven-antrun-plugin</artifactId>
    <executions>
        <execution>
            <id>clean-temp-files</id>
            <phase>prepare-package</phase> <!-- 明確指定：打包前執行 -->
            <goals>
                <goal>run</goal>
            </goals>
            <configuration>...</configuration>
        </execution>
    </executions>
</plugin>
```

#### 2. 使用 Profile 隔離環境邏輯
不要把所有邏輯都塞在主 `<build>` 區塊。針對 CI/CD、開發環境或特定發布需求，使用 `<profiles>` 來啟用特定的 Plugin 綁定。

### Gradle Patterns

#### 1. Configuration Avoidance (配置迴避)
使用 `tasks.register(...)` 而不是 `tasks.create(...)` (或舊式的 `task myTask`)。這確保了 Task 只有在真正需要被執行時，才會進行配置與初始化，大幅提升大型專案的 Configuration 速度。

#### 2. Custom Task Types over Ad-hoc Tasks
如果你的邏輯稍微複雜（超過 10 行腳本），請定義一個 Custom Task Class，而不是在 `build.gradle` 裡寫一大坨 `doLast`。

```groovy
// Best Practice: 定義明確的 Task 類型
abstract class GenerateDocs extends DefaultTask {
    @Input String docTitle
    @OutputFile File outputDir

    @TaskAction
    void generate() {
        // 實作邏輯
    }
}
```

#### 3. 正確宣告 Inputs/Outputs (Incremental Build)
Gradle 的強項是增量建置。如果你寫了客製化 Task，務必使用 Annotation (`@Input`, `@InputFile`, `@OutputFile`) 標記輸入輸出。這樣 Gradle 才能判斷 `UP-TO-DATE`，避免重複執行。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Maven Pitfalls

1.  **The `maven-antrun-plugin` Abuse**：
    -   **現象**：在 POM 檔中寫了幾百行的 Ant XML 腳本來做檔案搬移、取代字串。
    -   **後果**：XML 難以除錯、沒有語法檢查、難以閱讀。
    -   **解法**：寫一個簡單的 Java/Groovy Maven Plugin，或是改用 `exec-maven-plugin` 呼叫外部腳本。

2.  **Binding to `validate` or `initialize` for Heavy Work**：
    -   **現象**：在極早期的 Phase 下載大檔案或編譯。
    -   **後果**：導致 IDE (IntelliJ/Eclipse) 匯入專案時卡死，因為 IDE 通常會在匯入時執行這些早期 Phase 來解析模型。

### ❌ Gradle Pitfalls

1.  **Configuration Phase Logic Injection (最常見錯誤)**：
    -   **錯誤寫法**：
        ```groovy
        task deploy {
            println "Deploying to server..." // 錯！這會在每次執行任何指令時都印出來
        }
        ```
    -   **正確寫法**：
        ```groovy
        tasks.register('deploy') {
            doLast {
                println "Deploying to server..." // 對！這只有在執行 gradle deploy 時才跑
            }
        }
        ```
    -   **後果**：即使你只是跑 `./gradlew clean`，那個 "Deploying..." 也會執行，造成副作用或效能低落。

2.  **Hard Ordering with `mustRunAfter`**：
    -   **現象**：過度依賴 `mustRunAfter` 來控制順序，而不是建立正確的 `dependsOn` 依賴關係。
    -   **後果**：當並行執行（Parallel Execution）開啟時，Task 執行順序可能變得不可預測，導致建置失敗。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Where to put logic? (邏輯該放哪？)

1.  **Is it standard?** (編譯、測試、打包) -> 使用標準 Lifecycle/Plugins。
2.  **Is it a simple script?** (如：印出版本號、複製單一檔案)
    -   Maven: `maven-antrun-plugin` (keep it small).
    -   Gradle: Ad-hoc task with `doLast`.
3.  **Is it complex logic?** (如：解析 API Spec 生成程式碼、複雜的環境驗證)
    -   Maven: **Write a Custom Plugin**. 不要猶豫，寫一個 Plugin 其實很簡單。
    -   Gradle: **Write a Custom Task Type** in `buildSrc` directory.
4.  **Is it shared across projects?**
    -   Extract to a standalone Plugin repository.

### Debugging Checklist

- [ ] **Maven**: 執行 `mvn help:effective-pom` 查看最終合併後的 Plugin 設定與綁定關係。
- [ ] **Maven**: 執行 `mvn [goal] -X` 開啟 Debug 模式，觀察 Plugin 在哪個 Phase 被觸發。
- [ ] **Gradle**: 執行 `./gradlew [task] --dry-run` (或 `-m`)。這會跑完 Configuration Phase 並列出將要執行的 Task 順序，但不實際執行。
- [ ] **Gradle**: 使用 `taskTree` plugin 或 `./gradlew task --console=plain` 檢查依賴樹。
- [ ] **Gradle**: 檢查你的 Custom Task 是否在 Configuration Phase 做了不該做的事（如 IO 操作、網路請求）。

---

## Real-world examples｜實戰案例

### Scenario 1: Code Generation before Compilation (編譯前生成程式碼)

這是最常見的客製化需求（例如：Protobuf, JOOQ, OpenAPI）。

**Maven Approach:**
將生成器 Plugin 綁定到 `generate-sources` phase。

```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>generate</goal>
            </goals>
            <phase>generate-sources</phase> <!-- 關鍵點 -->
            <configuration>
                <!-- 設定輸入輸出 -->
            </configuration>
        </execution>
    </executions>
</plugin>
<!-- 記得將生成的目錄加入 source root，否則 compile 階段找不到 -->
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>build-helper-maven-plugin</artifactId>
    <executions>
        <execution>
            <phase>generate-sources</phase>
            <goals><goal>add-source</goal></goals>
            <configuration>
                <sources><source>${project.build.directory}/generated-sources/openapi</source></sources>
            </configuration>
        </execution>
    </executions>
</plugin>
```

**Gradle Approach:**
定義生成 Task，並建立依賴關係。

```kotlin
// Kotlin DSL
val generateOpenApi = tasks.register("generateOpenApi") {
    // 定義生成邏輯或呼叫外部工具
    doLast { ... }
}

// 關鍵：告訴 Gradle，compileJava 依賴於 generateOpenApi
tasks.named("compileJava") {
    dependsOn(generateOpenApi)
}

// 將生成目錄加入 SourceSet
sourceSets {
    main {
        java {
            srcDir("$buildDir/generated/openapi")
        }
    }
}
```

### Scenario 2: Docker Build & Push (建置後封裝與推送)

**Maven Approach:**
綁定到 `package` (建置 image) 和 `deploy` (推送 image)。

```xml
<plugin>
    <groupId>com.google.cloud.tools</groupId>
    <artifactId>jib-maven-plugin</artifactId>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>dockerBuild</goal></goals>
        </execution>
    </executions>
</plugin>
```

**Gradle Approach:**
利用 Gradle 的彈性，我們可以建立一個獨立的 Lifecycle Task。

```groovy
// 建立一個名為 'dockerize' 的任務
tasks.register('dockerize', com.google.cloud.tools.jib.gradle.BuildDockerTask) {
    dependsOn tasks.build // 確保先跑完測試與打包
    jib {
        to { image = 'my-app:latest' }
    }
}
// 開發者只需執行 ./gradlew dockerize
```