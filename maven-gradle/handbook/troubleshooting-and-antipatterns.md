# 疑難排解流程與常見反模式 / Troubleshooting Workflows & Common Anti-patterns

## Mental model｜心智模型

在處理 Maven 或 Gradle 的建置問題時，最核心的心智模型是將建置系統視為一個 **「有向無環圖的執行引擎」（DAG Execution Engine）**，而非單純的腳本執行器。

### 1. The Phase Distinction (階段區分)
除錯的第一步是判斷錯誤發生在哪個階段：
- **Configuration Phase (配置階段)**：
    - **Gradle**: 評估 `build.gradle`，建立 Task Graph。如果這裡出錯，通常是語法錯誤或邏輯錯誤，Task 根本還沒開始跑。
    - **Maven**: 讀取 POM，解析依賴與 Plugin 設定。
- **Execution Phase (執行階段)**：
    - 實際編譯程式碼、執行測試、打包。錯誤通常是程式碼編譯失敗、測試不過或資源檔遺失。

### 2. The Dependency Graph (依賴圖譜)
大部分「詭異」的問題（如 `ClassNotFoundException`, `NoSuchMethodError`）都源自於 **Dependency Hell**。
- **Mental Image**: 想像你的專案是一棵樹，但這棵樹的樹葉（Transitive Dependencies）可能會互相打架（版本衝突）。你必須具備「透視」這棵樹的能力，而不是只看根節點（Direct Dependencies）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Observability First: Build Scans & Verbose Logs
不要猜測，讓建置系統告訴你發生了什麼。

- **Gradle Build Scans**:
    - 這是 Gradle 最強大的除錯工具。它會生成一個互動式的網頁報告，顯示依賴解析、Task 執行時間、失敗原因。
    - **Action**: 執行 `gradle build --scan`。
- **Maven Debug Logging**:
    - Maven 沒有內建像 Build Scan 那麼華麗的 UI（雖然有 Gradle Enterprise for Maven），但詳細日誌是基本功。
    - **Action**: 使用 `mvn -X clean install` 來查看完整的 debug log。

### 2. Dependency Insight Tools (依賴透視)
當遇到類別衝突或版本不一致時，使用工具找出元兇。

- **Maven**:
    - `mvn dependency:tree -Dverbose`: 顯示完整的依賴樹，並標記出哪些版本被覆蓋或衝突。
    - `mvn dependency:analyze`: 檢查是否有「用了但沒宣告」（Used undeclared）或「宣告了但沒用」（Unused declared）的依賴。
- **Gradle**:
    - `gradle dependencies`: 列出依賴樹。
    - `gradle dependencyInsight --dependency <name>`: **殺手級指令**，直接告訴你某個 library 是誰引進來的，以及為什麼選用這個版本。

### 3. Isolation & Reproducibility (隔離與重現)
- **The "Clean" Habit**: 遇到怪問題，先 `clean`。Maven (`mvn clean`) 和 Gradle (`gradle clean`) 的快取機制有時會造成 stale outputs。
- **Wrapper Usage**: 永遠使用 `mvnw` 或 `gradlew`。這保證了所有開發者和 CI Server 使用完全相同的 Build Tool 版本，消滅 "It works on my machine"。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The God Module (上帝模組)
- **現象**: 整個專案只有一個巨大的 `pom.xml` 或 `build.gradle`，所有 source code 都在 `src/main/java` 下。
- **後果**: 建置極慢（無法平行化）、依賴混亂、IDE 索引變慢。
- **修正**: 拆分為 Multi-module 架構，依據業務領域或層級（Core, API, Web）拆分。

### 2. Circular Dependencies (循環依賴)
- **現象**: Module A 依賴 Module B，Module B 又依賴 Module A。
- **後果**: Maven 會直接報錯拒絕建置。Gradle 雖然可以透過某些 hack 允許，但這代表架構設計有嚴重缺陷（高耦合）。
- **修正**: 提取公共介面或邏輯到第三個 Module C，讓 A 和 B 都依賴 C。

### 3. Phantom Dependencies (幽靈依賴)
- **現象**: 你的程式碼用了 Library X，但 `pom.xml` 裡沒寫 X，是因為你依賴的 Library Y 剛好帶入了 X（Transitive Dependency）。
- **後果**: 當 Library Y 升級並移除了 X，你的專案就會突然編譯失敗。
- **修正**: **Explicitly declare what you use.** 如果你的程式碼直接 import 了某個包，請務必在配置檔中顯式宣告它。

### 4. Logic in Configuration (配置檔中的邏輯)
- **現象**: 在 `build.gradle` 中寫了大量的 `if-else`、迴圈或複雜的 Groovy/Kotlin 邏輯來決定變數。
- **後果**: 難以維護、難以閱讀、IDE 支援差。
- **修正**: 將複雜邏輯提取為自定義的 Plugin 或 `buildSrc` 中的腳本。保持構建腳本是「宣告式」（Declarative）的。

### 5. Mutable Snapshots in Production (生產環境使用快照)
- **現象**: 正式發布的依賴版本依賴於 `1.0-SNAPSHOT`。
- **後果**: 今天的建置結果可能跟明天不一樣，因為 Snapshot 隨時會變。違反了「不可變建置」（Immutable Build）原則。
- **修正**: Release 版本必須依賴具體的 Release 版本（如 `1.0.0`）。

---

## Checklists & workflows｜檢查清單與流程

當建置失敗時，請依照此 SOP 進行排查：

### Phase 1: Initial Diagnosis (初步診斷)
- [ ] **Read the Error Message**: 不要只看最後一行，往上捲動尋找 "Caused by"。
- [ ] **Clean Build**: 執行 `mvn clean` 或 `gradle clean` 後重試。
- [ ] **Check Environment**: 確認 `java -version` 與 `mvn -v`/`gradle -v` 符合專案需求。

### Phase 2: Dependency Issues (依賴問題)
- [ ] **Conflict Check**: 是否有 `NoSuchMethodError` 或 `ClassNotFoundException`？
    - [ ] Maven: 跑 `mvn dependency:tree` 尋找衝突。
    - [ ] Gradle: 跑 `gradle dependencyInsight` 鎖定問題庫。
- [ ] **Force Resolution**: 是否需要使用 `<exclusion>` (Maven) 或 `exclude group:` (Gradle) 來排除衝突版本？
- [ ] **Snapshot Check**: 是否依賴了過期的 Snapshot？嘗試用 `-U` (Maven) 或 `--refresh-dependencies` (Gradle) 強制更新。

### Phase 3: Performance & Logic (效能與邏輯)
- [ ] **Verbose Mode**: 開啟 Debug log (`-X` / `--info`) 查看卡在哪個步驟。
- [ ] **Skip Tests**: 如果是為了快速驗證編譯，暫時跳過測試 (`-DskipTests` / `-x test`) 確認是否為測試程式碼問題。
- [ ] **Build Scan**: (Gradle 用戶) 生成 Build Scan 分享給資深同事求救。

---

## Real-world examples｜實戰案例

### Example 1: Resolving "Dependency Hell" (Log4j Conflict)

**情境**: 你的專案依賴 `Framework-A` (使用 slf4j-log4j12) 和 `Framework-B` (使用 log4j-over-slf4j)。這兩者會導致 Classpath 衝突。

**Maven Solution (Exclusion)**:
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>framework-a</artifactId>
    <version>1.0.0</version>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

**Gradle Solution (Exclusion)**:
```kotlin
implementation("com.example:framework-a:1.0.0") {
    exclude(group = "org.slf4j", module = "slf4j-log4j12")
}
```

### Example 2: The "Works on My Machine" Fix

**情境**: CI Server 報錯 `JAVA_HOME not set` 或編譯版本錯誤，但本地正常。

**Anti-pattern (Bad)**:
在 CI script 中寫死路徑：`export JAVA_HOME=/usr/lib/jvm/java-8-oracle`

**Best Practice (Good)**:
使用 Toolchains (Maven/Gradle) 來解耦本地環境與建置需求。

**Gradle Toolchain**:
```kotlin
java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}
```
這會強制 Gradle 自動下載並使用 JDK 17 進行編譯，無論機器上預設安裝的是什麼版本。

### Example 3: Debugging Slow Builds

**情境**: 每次建置都要 10 分鐘，開發者在等待中浪費生命。

**Workflow**:
1.  執行 `gradle build --scan`。
2.  打開報告，點擊 **Performance** 頁籤。
3.  發現 `test` task 佔用了 8 分鐘。
4.  進一步發現是某個整合測試在等待 DB timeout。
5.  **Action**: 將該測試標記為 `@SlowTest` 並在一般開發流程中排除，或修復 DB 連線配置。