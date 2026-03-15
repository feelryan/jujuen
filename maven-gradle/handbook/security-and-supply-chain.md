# 建置安全性與軟體供應鏈管理 / Build Security & Software Supply Chain Management

## Mental model｜心智模型

### The Procurement Gatekeeper (採購守門員)

不要只把 Maven 或 Gradle 當作「編譯程式碼的工廠」，請將它們視為軟體專案的 **「採購部門與海關」 (Procurement Department & Customs)**。

在現代軟體開發中，你的原始碼（Source Code）通常只佔最終產出物（Artifact）的一小部分，其餘 80%-90% 來自第三方依賴（Dependencies）。
- **Build Tool as a Gatekeeper**: 建置工具是外部程式碼進入你產品的第一道防線。
- **Supply Chain Visibility**: 你必須知道「誰進來了」（Dependency Tree）、「他們是否安全」（CVE Scanning）以及「他們來自哪裡」（Repository Origin）。

### The "Chain of Custody" (監管鏈)

軟體供應鏈安全不僅是依賴掃描，它包含三個階段的信任建立：
1.  **Ingestion (輸入)**: 驗證下載的依賴包是否被篡改（Checksums, Signatures）。
2.  **Build (建置)**: 確保建置環境乾淨，且產出物可追溯（Reproducible Builds）。
3.  **Output (輸出)**: 提供成分清單（SBOM）並對產出物簽章，讓下游使用者能信任你。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 自動化漏洞掃描 (Automated Vulnerability Scanning)
不要依賴人工檢查。將 CVE 掃描整合進 Build Pipeline，並設定「品質閘門」（Quality Gate）。

- **Maven**: 使用 `owasp-dependency-check-maven` 或 `snyk-maven-plugin`。
- **Gradle**: 使用 `org.owasp.dependencycheck` plugin。
- **Practice**: 設定 `failBuildOnCVSS` 閾值（例如 CVSS > 7.0 則建置失敗），強迫團隊在開發階段就處理高風險漏洞。

### 2. 生成軟體物料清單 (SBOM Generation)
SBOM (Software Bill of Materials) 是軟體的「食品成分表」。現在已是企業級合規的標準配置。

- **Standard**: 推薦使用 **CycloneDX** 或 **SPDX** 格式。
- **Implementation**:
    - Maven: `cyclonedx-maven-plugin`
    - Gradle: `org.cyclonedx.bom`
- **Why**: 當下一個 "Log4Shell" 發生時，擁有 SBOM 可以讓你在幾秒鐘內查詢全公司數百個專案中，哪些受到了影響，而不是逐一去跑 `dependency:tree`。

### 3. 鎖定依賴來源與防範 Dependency Confusion
這是最容易被忽視的攻擊向量。攻擊者在公開倉庫（Maven Central）上傳一個與你公司內部私有套件「同名但版號更高」的惡意套件，若配置不當，Build Tool 可能會優先下載公開的惡意版本。

- **Gradle**: 使用 **Repository Content Filtering**。明確宣告哪個 Repository 包含哪些 Group/Artifact。
- **Maven**: 在 `settings.xml` 或 Repository Manager (Nexus/Artifactory) 中嚴格設定路由規則，禁止從 Public Proxy 抓取內部 Group ID 的套件。

### 4. 驗證 Wrapper 與依賴完整性 (Integrity Verification)
- **Wrapper Verification**: 攻擊者可能修改專案中的 `gradle-wrapper.jar` 或 `maven-wrapper.jar` 來執行惡意程式碼。
    - **Action**: 使用 GitHub Action `gradle/wrapper-validation-action` 或手動檢查 Wrapper 的 SHA-256 checksum。
- **Dependency Verification (Gradle)**: Gradle 支援生成 `verification-metadata.xml`，鎖定所有依賴的 Checksum 與 Signature，確保依賴包未被中間人篡改。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 使用動態版本 (Dynamic Versions)
- **Anti-pattern**: 在 `build.gradle` 中寫 `implementation 'com.example:lib:1.+'` 或 `latest.release`。
- **Risk**: 這不僅破壞了建置的可重現性（Reproducibility），更讓惡意軟體能透過發布新版本瞬間感染你的專案。
- **Fix**: 永遠使用具體的版本號，並配合 Dependabot 或 Renovate 進行有控制的升級。

### 2. 混合使用 HTTP 與 HTTPS Repositories
- **Anti-pattern**: 定義 `maven { url "http://repo.mycompany.com" }`。
- **Risk**: 中間人攻擊（MITM）可以輕易攔截並替換下載的 JAR 檔。
- **Fix**: 強制所有 Repository 使用 HTTPS。Gradle 預設已開始阻擋 HTTP 連線。

### 3. 忽略傳遞性依賴 (Ignoring Transitive Dependencies)
- **Anti-pattern**: 只掃描直接依賴（Direct Dependencies），認為傳遞性依賴（Transitive Dependencies）是別人的責任。
- **Risk**: 大多數漏洞都藏在深層的依賴樹中。
- **Fix**: 確保掃描工具遍歷整個依賴樹。使用 `mvn dependency:tree` 或 `gradle dependencies` 定期檢視「誰被帶進來了」。

### 4. 盲目信任 `mavenLocal()`
- **Anti-pattern**: 在 CI/CD 環境或 `build.gradle` 頂層加入 `mavenLocal()`。
- **Risk**: 本機快取可能被汙染，導致建置結果不可靠且難以追蹤來源。
- **Fix**: CI 環境應保持無狀態（Stateless），依賴應來自受控的 Remote Repository。

---

## Checklists & workflows｜檢查清單與流程

### Project Setup Checklist (專案設定階段)
- [ ] **Repository Security**: 確認所有 Repository URL 均為 `HTTPS`。
- [ ] **Wrapper Validation**: 確認 `gradle-wrapper.properties` 或 `maven-wrapper.properties` 中的 distributionUrl 指向官方連結，且已驗證 Checksum。
- [ ] **Dependency Locking**: Gradle 啟用 Dependency Locking 或 Verification Metadata；Maven 使用 dependency management 嚴格管控版本。

### CI/CD Pipeline Workflow (持續整合階段)
1.  **Build Start**: 驗證 Wrapper 完整性。
2.  **Dependency Resolution**: 下載依賴，若 checksum 不符則立即失敗。
3.  **SCA Scan (Software Composition Analysis)**:
    - 執行 OWASP Dependency Check / Snyk。
    - 若發現 High/Critical CVE -> **Fail Build**。
4.  **Compilation & Test**: 執行常規建置。
5.  **Post-Build**:
    - 生成 SBOM (e.g., `bom.json`).
    - 對 Artifact (JAR/WAR) 與 SBOM 進行 GPG 簽章。
6.  **Publish**: 將 Artifact、Signature 與 SBOM 一同上傳至 Nexus/Artifactory。

---

## Real-world examples｜實戰案例

### Example 1: Gradle Dependency Verification (防止篡改)

在金融或高安全性專案中，你需要確保下載的 JAR 檔與開發者當初使用的一模一樣。

**操作步驟：**
1. 生成驗證元數據：
   ```bash
   ./gradlew --write-verification-metadata sha256 help
   ```
   這會產生 `gradle/verification-metadata.xml`，紀錄所有依賴的 SHA-256。

2. 在 CI 中執行建置：
   Gradle 會自動比對下載檔案的 Hash 與 xml 中的紀錄。如果不符（例如 Repository 被駭，檔案被換掉），Build 會直接報錯停止。

### Example 2: Maven CycloneDX SBOM Integration (生成物料清單)

為了符合供應鏈安全規範（如美國行政命令 EO 14028），你需要隨軟體附上 SBOM。

**pom.xml 配置：**

```xml
<plugin>
    <groupId>org.cyclonedx</groupId>
    <artifactId>cyclonedx-maven-plugin</artifactId>
    <version>2.7.9</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals>
                <goal>makeAggregateBom</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <projectType>library</projectType>
        <schemaVersion>1.4</schemaVersion>
        <includeBomSerialNumber>true</includeBomSerialNumber>
        <includeCompileScope>true</includeCompileScope>
        <includeProvidedScope>true</includeProvidedScope>
        <includeRuntimeScope>true</includeRuntimeScope>
        <includeTestScope>false</includeTestScope>
    </configuration>
</plugin>
```
執行 `mvn package` 後，你會在 `target/` 下看到 `bom.json`，這就是你的軟體身分證。

### Example 3: Preventing Dependency Confusion in Gradle

防止私有套件被公開倉庫的同名套件覆蓋。

**build.gradle (Kotlin DSL):**

```kotlin
repositories {
    mavenCentral {
        content {
            // 這個倉庫只允許抓取一般公開套件，明確排除公司內部 group
            excludeGroup("com.mycompany.internal")
        }
    }
    maven {
        url = uri("https://repo.mycompany.com/maven-private")
        credentials { ... }
        content {
            // 這個倉庫專門用來抓取公司內部套件
            includeGroup("com.mycompany.internal")
        }
    }
}
```
透過 `content {}` 區塊，你明確定義了流量規則，杜絕了外部惡意套件混入內部的風險。