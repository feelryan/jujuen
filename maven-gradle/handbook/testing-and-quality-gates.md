# 測試策略與品質閘門整合 / Testing Strategies & Quality Gates Integration

## Mental model｜心智模型

在建置工具（Build Tools）的語境下，測試與品質檢查不只是「執行程式碼」，而是**生產線上的品質過濾器（Quality Filters in the Assembly Line）**。

### 1. The Separation of Concerns (關注點分離)
- **Unit Tests (單元測試)**：應該是極速的、記憶體內的（in-memory）、無外部依賴的。它們屬於開發者的「熱路徑（Hot path）」，在每次存檔或編譯後執行。
- **Integration Tests (整合測試)**：通常涉及資料庫、網路、Spring Context 啟動。它們較慢，應該在「冷路徑（Cold path）」或 CI 流程的特定階段執行。
- **Quality Gates (品質閘門)**：靜態分析（Linting）與覆蓋率（Coverage）是「不可協商的合約」。如果合約未達成，建置**必須失敗**，而不是只產生一份沒人看的報告。

### 2. Maven vs. Gradle Execution Model
- **Maven**: 依賴生命週期階段（Lifecycle Phases）。
  - `test` 階段僅執行單元測試（Surefire Plugin）。
  - `integration-test` 執行整合測試，但不會失敗建置。
  - `verify` 才是真正的閘門，這裡會檢查整合測試結果（Failsafe Plugin）與品質指標（Checkstyle/JaCoCo check）。
- **Gradle**: 依賴任務圖（Task Graph）。
  - `test` 是標準任務。
  - 整合測試通常需要自定義 SourceSet 與 Task。
  - `check` 是一個 Lifecycle Task，它聚合了所有驗證任務（test, lint, coverage）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 嚴格區分單元測試與整合測試 (Strict Separation of UT & IT)

不要讓慢速的整合測試拖累日常開發節奏。

- **Maven Pattern**:
  - 使用 **Maven Surefire Plugin** 執行 `**/*Test.java` (Unit Tests)。
  - 使用 **Maven Failsafe Plugin** 執行 `**/*IT.java` (Integration Tests)。
  - 綁定 Failsafe 的 `integration-test` 與 `verify` goals，確保 `mvn clean verify` 才會跑完整流程，而 `mvn clean package` 跳過 IT。
- **Gradle Pattern**:
  - 建立獨立的 `sourceSets.create('integrationTest')`。
  - 註冊一個 `integrationTest` task，並讓 `check` 依賴它（或透過 flag 決定是否依賴）。

### 2. 強制性品質閘門 (Enforcing Quality Gates)

報告（Reporting）是給人看的，檢查（Checking）是給機器擋的。**不要只生成 HTML，要設定閾值（Thresholds）。**

- **Code Coverage (JaCoCo)**:
  - 設定 `minimum` coverage ratio（例如 0.80）。
  - **Gradle**: `jacocoTestCoverageVerification` task 必須在 `test` 後執行。
  - **Maven**: 在 `jacoco-maven-plugin` 的 `check` goal 中設定 `<haltOnFailure>true</haltOnFailure>`。
- **Code Style (Spotless / Checkstyle)**:
  - 推薦使用 **Spotless**（Gradle/Maven 均支援），因為它不僅檢查，還能 `apply`（自動修正）。
  - 在 CI 中執行 `check`（檢查模式），在本地開發執行 `apply`（修正模式）。

### 3. Fail Fast vs. Fail Complete

- **Fail Fast**: 在本地開發時，如果 Checkstyle 沒過，不需要跑測試，直接失敗。
- **Fail Complete**: 在 CI Server 上，建議設定 `failAtEnd`（Maven）或 `ignoreFailures = true` (Gradle test task level) 配合最終的聚合報告，讓開發者一次看到所有錯誤（測試失敗 + Checkstyle 錯誤），而不是修了一個又爆下一個。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Clean Install" Habit (Maven)
- **Anti-pattern**: 習慣性執行 `mvn clean install` 來跑單元測試。
- **Why**: `install` 會將 artifact 放入本地倉庫，且通常會觸發整合測試（如果配置在 verify 前）。
- **Fix**: 日常開發使用 `mvn clean test`；只有在需要整合驗證時才用 `mvn clean verify`。

### 2. Mixing Test Dependencies (Gradle)
- **Anti-pattern**: 在 Gradle 中將所有測試依賴都放在 `testImplementation`，即使是只有整合測試才需要的重量級依賴（如 Testcontainers）。
- **Why**: 污染了單元測試的 Classpath，增加了編譯時間。
- **Fix**: 使用獨立的 SourceSet (`integrationTestImplementation`)。

### 3. The "Ignored" Gate
- **Anti-pattern**: 安裝了 JaCoCo 或 Checkstyle，但沒有設定 `failure` 條件。CI 永遠顯示綠燈，即使覆蓋率只有 5%。
- **Fix**: 必須配置 Build Failure。如果標準太高，先降低標準（Baseline），然後逐步調高（Ratchet mechanism）。

### 4. Flaky Tests as "Normal"
- **Anti-pattern**: 允許不穩定的測試存在，並透過 `rerun` 機制掩蓋。
- **Fix**: 使用 Build Tool 的功能（如 Maven Surefire 的 `rerunFailingTestsCount`）是權宜之計。根本解法是隔離測試環境（Testcontainers）或修復並發問題。

---

## Checklists & workflows｜檢查清單與流程

### Project Setup Checklist (專案設定檢查清單)

- [ ] **目錄結構分離**：是否已將 Unit Test 與 Integration Test 的程式碼或設定分開？
  - Maven: `*Test.java` vs `*IT.java`
  - Gradle: `src/test` vs `src/integrationTest`
- [ ] **靜態分析配置**：是否已配置 Checkstyle/Spotless 並設定「違反即失敗（Fail on violation）」？
- [ ] **覆蓋率門檻**：JaCoCo 是否設定了具體的百分比門檻（例如 Line Coverage > 80%）？
- [ ] **執行效率**：是否開啟了測試平行執行（Parallel Execution / Forking）？

### Developer Workflow (開發者流程)

1.  **Coding**: 撰寫程式碼。
2.  **Format**: 執行 `mvn spotless:apply` 或 `gradle spotlessApply` 自動排版。
3.  **Unit Test**: 執行 `mvn test` 或 `gradle test` (Fast feedback)。
4.  **Pre-push**: 執行 `mvn verify` 或 `gradle check` (Full gate check)。

---

## Real-world examples｜實戰案例

### 1. Maven: Surefire vs Failsafe & JaCoCo Gate

在 `pom.xml` 中標準的企業級配置：

```xml
<build>
    <plugins>
        <!-- Unit Tests: Run fast, fail fast -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <configuration>
                <includes>
                    <include>**/*Test.java</include>
                </includes>
            </configuration>
        </plugin>

        <!-- Integration Tests: Run during 'integration-test' phase, verify in 'verify' -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-failsafe-plugin</artifactId>
            <executions>
                <execution>
                    <goals>
                        <goal>integration-test</goal>
                        <goal>verify</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>

        <!-- Quality Gate: JaCoCo -->
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <executions>
                <execution>
                    <id>prepare-agent</id>
                    <goals><goal>prepare-agent</goal></goals>
                </execution>
                <execution>
                    <id>check</id>
                    <goals><goal>check</goal></goals>
                    <phase>verify</phase> <!-- Gatekeeper at the end -->
                    <configuration>
                        <rules>
                            <rule>
                                <element>BUNDLE</element>
                                <limits>
                                    <limit>
                                        <counter>LINE</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.80</minimum> <!-- 80% Threshold -->
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

### 2. Gradle: Custom SourceSet & Spotless

在 `build.gradle` (Groovy DSL) 中分離整合測試並強制代碼風格：

```groovy
plugins {
    id 'java'
    id 'jacoco'
    id 'com.diffplug.spotless' version '6.25.0'
}

// 1. Separate SourceSet for Integration Tests
sourceSets {
    integrationTest {
        java {
            srcDir 'src/integrationTest/java'
        }
        resources {
            srcDir 'src/integrationTest/resources'
        }
        compileClasspath += sourceSets.main.output + sourceSets.test.output
        runtimeClasspath += sourceSets.main.output + sourceSets.test.output
    }
}

// 2. Configuration for dependencies
configurations {
    integrationTestImplementation.extendsFrom testImplementation
    integrationTestRuntimeOnly.extendsFrom testRuntimeOnly
}

// 3. Define the task
task integrationTest(type: Test) {
    description = 'Runs integration tests.'
    group = 'verification'
    testClassesDirs = sourceSets.integrationTest.output.classesDirs
    classpath = sourceSets.integrationTest.runtimeClasspath
    shouldRunAfter test // Run Unit Tests first
}

// 4. Hook into the 'check' lifecycle
check.dependsOn integrationTest

// 5. Quality Gate: Spotless (Code Style)
spotless {
    java {
        googleJavaFormat() // Use Google Style
        removeUnusedImports()
    }
}

// 6. Quality Gate: JaCoCo Verification
jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = 0.8
            }
        }
    }
}
// Ensure verification runs after tests
check.dependsOn jacocoTestCoverageVerification
```