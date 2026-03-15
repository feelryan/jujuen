# 1. 前言與學習目標 (Introduction & Learning Objectives)

在現代軟體工程中，建置工具不僅僅是將程式碼編譯成執行檔的工具，更是軟體供應鏈安全（Software Supply Chain Security）的第一道防線。對於資深工程師而言，懂得如何防範相依性混淆（Dependency Confusion）、自動化弱點掃描以及生成 SBOM，是確保系統在生產環境中安全運行的關鍵能力。

In modern software engineering, build tools are not just for compiling code into executables; they serve as the first line of defense for Software Supply Chain Security. For a Senior Engineer, knowing how to prevent Dependency Confusion, automate vulnerability scanning, and generate SBOMs is critical to ensuring the security of systems in production environments.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **防範 Dependency Confusion 攻擊**：理解 Maven 與 Gradle 解析相依性的優先順序，並配置儲存庫策略以防止惡意套件注入。
    **Prevent Dependency Confusion Attacks:** Understand the dependency resolution precedence in Maven and Gradle, and configure repository policies to prevent malicious package injection.
2.  **整合自動化弱點掃描**：在建置流程中整合 OWASP Dependency Check 或類似工具，並建立有效的例外處理機制（Suppression）。
    **Integrate Automated Vulnerability Scanning:** Integrate OWASP Dependency Check or similar tools into the build process and establish effective suppression mechanisms.
3.  **生成與管理 SBOM**：產出符合業界標準（如 CycloneDX 或 SPDX）的軟體物料清單，以滿足合規性與快速回應零時差攻擊（如 Log4Shell）。
    **Generate and Manage SBOMs:** Produce industry-standard Software Bill of Materials (e.g., CycloneDX or SPDX) to meet compliance requirements and respond quickly to zero-day attacks (like Log4Shell).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 軟體供應鏈 (The Software Supply Chain)

你可以將軟體建置過程想像成汽車製造工廠。Maven/Gradle 是組裝線，而 `dependencies` 是來自外部供應商的零件（引擎、輪胎）。如果供應商送來的零件含有爆裂物（惡意程式碼）或瑕疵（CVE 漏洞），整台車（應用程式）就會變得危險。

You can visualize the software build process as a car manufacturing plant. Maven/Gradle is the assembly line, and `dependencies` are parts from external suppliers (engines, tires). If a supplier delivers parts with explosives (malicious code) or defects (CVE vulnerabilities), the entire car (application) becomes dangerous.

-   **SCA (Software Composition Analysis)**：這是你的「品管部門」，負責檢查所有引入的零件是否在已知的瑕疵清單（Vulnerability Database）上。
    **SCA (Software Composition Analysis):** This is your "Quality Control Department," responsible for checking if any imported parts are on a known list of defects (Vulnerability Database).
-   **SBOM (Software Bill of Materials)**：這是整台車的「詳細零件清單」，包含每個螺絲的來源與版本。當發現某批次的螺絲有問題時，SBOM 能讓你在一秒鐘內知道哪些車輛需要召回。
    **SBOM (Software Bill of Materials):** This is the detailed "ingredients list" for the car, including the source and version of every screw. When a batch of screws is found to be defective, the SBOM lets you know in a second which cars need to be recalled.

## 2.2 Dependency Confusion (相依性混淆)

這是一種攻擊手法。攻擊者在公共儲存庫（如 Maven Central）上發布一個與你公司內部私有套件（如 `com.company:internal-auth`）同名但版本號更高（例如 `99.9.9`）的惡意套件。如果你的建置工具配置不當，它可能會優先下載公共網路上的惡意高版本，而非內部的正確版本。

This is an attack vector. An attacker publishes a malicious package on a public repository (like Maven Central) with the same name as your company's private package (e.g., `com.company:internal-auth`) but with a higher version number (e.g., `99.9.9`). If your build tool is misconfigured, it might prioritize downloading the malicious higher version from the public internet instead of the correct internal version.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在企業級架構中，建置安全性通常涉及三個層面：開發者本機、CI/CD 伺服器、以及 Artifact Repository Manager (Nexus/Artifactory)。

In enterprise architecture, build security typically involves three layers: Developer Local, CI/CD Servers, and the Artifact Repository Manager (Nexus/Artifactory).

## 3.1 架構角色 (Architectural Roles)

1.  **Repository Manager (Nexus/Artifactory)**:
    -   這是防禦的核心。它應該作為所有外部請求的 Proxy。
    -   **設計決策**：應配置「路由規則（Routing Rules）」或「封鎖清單」，禁止從 Maven Central 下載屬於公司內部 namespace（如 `com.mycompany.*`）的套件。
    -   **Design Decision**: It acts as the core defense and should proxy all external requests. Configure "Routing Rules" or "Blocking Lists" to forbid downloading packages belonging to internal namespaces (e.g., `com.mycompany.*`) from Maven Central.

2.  **CI Pipeline (Jenkins/GitLab CI/GitHub Actions)**:
    -   這是執法點（Enforcement Point）。
    -   **設計決策**：Pipeline 必須包含 `generate-sbom` 與 `vulnerability-scan` 步驟。若發現 High/Critical 漏洞且未被豁免（Suppressed），應直接讓 Build 失敗（Break the Build）。
    -   **Design Decision**: The pipeline is the enforcement point. It must include `generate-sbom` and `vulnerability-scan` steps. If High/Critical vulnerabilities are found and not suppressed, the build should fail immediately.

## 3.2 對系統屬性的影響 (Impact on System Attributes)

-   **安全性 (Security)**：大幅降低供應鏈攻擊風險。
-   **可維護性 (Maintainability)**：雖然初期配置繁瑣，但透過集中管理的 Suppression File，可以避免團隊被假警報淹沒。
-   **合規性 (Compliance)**：SBOM 是金融與醫療領域日益嚴格的合規要求（如美國行政命令 EO 14028）。

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 防範 Dependency Confusion (Preventing Dependency Confusion)

### Gradle 解決方案：Repository Content Filtering
Gradle 提供了非常強大的 API 來限制特定儲存庫只能（或不能）提供哪些套件。這是最推薦的防禦方式。

Gradle provides a powerful API to restrict which repositories can (or cannot) provide specific packages. This is the most recommended defense mechanism.

```kotlin
// build.gradle.kts

repositories {
    // 1. 定義內部私有儲存庫 (Internal Private Repo)
    maven {
        url = uri("https://artifacts.company.com/maven-private")
        name = "CompanyPrivate"
        
        // 關鍵配置：宣告此儲存庫「獨佔」公司內部的 Group ID
        // Key Config: Declare that this repo has "exclusive" content for company Group IDs
        content {
            includeGroup("com.mycompany")
            includeGroupAndSubgroups("com.mycompany.internal")
        }
    }

    // 2. 定義公共儲存庫 (Public Repo)
    mavenCentral {
        content {
            // 明確排除公司內部的 Group ID，防止從外部下載假冒的內部套件
            // Explicitly exclude company Group IDs to prevent downloading fake internal packages from outside
            excludeGroup("com.mycompany")
            excludeGroupAndSubgroups("com.mycompany.internal")
        }
    }
}
```

### Maven 解決方案
Maven 原生不具備像 Gradle 這樣細緻的 include/exclude 機制（Maven 3.x）。通常依賴 Repository Manager (Nexus/Artifactory) 的設定，或者在 `settings.xml` 中嚴格定義 `<mirror>` 指向內部 Proxy，並在 Proxy 上設定路由規則。

Maven natively lacks the granular include/exclude mechanism found in Gradle (for Maven 3.x). It typically relies on Repository Manager (Nexus/Artifactory) settings, or strictly defining `<mirror>` in `settings.xml` to point to an internal Proxy, where routing rules are enforced.

## 4.2 整合 OWASP Dependency Check

這是一個開源工具，用於掃描專案依賴是否包含已知的 CVE。

This is an open-source tool used to scan project dependencies for known CVEs.

### Gradle Setup

```kotlin
// build.gradle.kts
plugins {
    id("org.owasp.dependencycheck") version "8.4.0"
}

dependencyCheck {
    // 設定若發現 CVSS 分數大於等於 7 (High/Critical) 的漏洞，則建置失敗
    // Fail the build if vulnerabilities with CVSS score >= 7 (High/Critical) are found
    failBuildOnCVSS = 7.0f
    
    // 指定豁免檔案，用於忽略特定的誤報或暫時無法修復的漏洞
    // Specify suppression file to ignore false positives or vulnerabilities that cannot be fixed yet
    suppressionFile = "config/dependency-check-suppression.xml"
    
    // 為了效能，通常只在 CI 環境或特定指令下執行分析
    // For performance, usually run analysis only in CI or via specific commands
    analyzers {
        assemblyEnabled = false
    }
}
```

### Maven Setup

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>8.4.0</version>
    <configuration>
        <failBuildOnCVSS>7</failBuildOnCVSS>
        <suppressionFile>config/dependency-check-suppression.xml</suppressionFile>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## 4.3 生成 SBOM (CycloneDX)

CycloneDX 是目前最流行的 SBOM 標準之一。

CycloneDX is one of the most popular SBOM standards.

```kotlin
// Gradle (build.gradle.kts)
plugins {
    id("org.cyclonedx.bom") version "1.7.4"
}

tasks.cyclonedxBom {
    // 包含所有相依性 (compile, runtime, test...)
    includeConfigs = listOf("runtimeClasspath")
    // 輸出格式
    projectType = "application"
    schemaVersion = "1.4"
    destination = file("build/reports")
    outputName = "bom"
    outputFormat = "json"
}
```

執行後，你會在 `build/reports/bom.json` 得到一份完整的物料清單，這份檔案應隨你的 Docker Image 或 Jar 檔一起發布。

After execution, you will get a complete bill of materials in `build/reports/bom.json`. This file should be published along with your Docker Image or Jar file.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略傳遞性依賴 (Ignoring Transitive Dependencies)
-   **錯誤 (Pitfall)**：只檢查直接宣告在 build 檔中的依賴，忽略了依賴的依賴（Transitive Dependencies）。
-   **後果 (Consequence)**：像 Log4Shell 這樣的漏洞往往深藏在傳遞依賴中，若掃描工具未涵蓋完整的 dependency tree，將導致安全盲區。
-   **修正 (Correction)**：確保掃描工具（如 OWASP Dependency Check）預設會遞迴掃描整個圖譜。

## 5.2 缺乏豁免管理機制 (Lack of Suppression Management)
-   **錯誤 (Pitfall)**：遇到掃描報錯就直接關閉掃描，或者因為太多 False Positives 而麻痺。
-   **後果 (Consequence)**：團隊會養成「忽略安全警告」的壞習慣。
-   **修正 (Correction)**：建立維護 `suppression.xml` 的流程。當發現誤報或確認該漏洞在當前使用場景下無效（Not Exploitable）時，應明確加入豁免並附上註解與過期時間，而非關閉掃描。

## 5.3 在 Build Script 中硬編碼 Credentials
-   **錯誤 (Pitfall)**：將 Nexus/Artifactory 的帳號密碼直接寫在 `build.gradle` 或 `pom.xml` 中。
-   **後果 (Consequence)**：憑證洩漏風險極高。
-   **修正 (Correction)**：使用環境變數（Environment Variables）或使用者層級的 `~/.gradle/gradle.properties` / `~/.m2/settings.xml`，並結合 CI/CD 的 Secret Management。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 什麼是 Dependency Confusion？你在實務上如何確保你的 Build Tool 不會下載到惡意套件？
**What is Dependency Confusion? How do you ensure your build tool doesn't download malicious packages in practice?**

-   **高分回答要點 (Key Points)**：
    -   解釋命名空間衝突的原理（Public vs Private repo 擁有同名套件）。
    -   **Gradle**：使用 `repositories { exclusiveContent { ... } }` 明確綁定 Group ID 到特定 URL。
    -   **Maven/General**：強調 Repository Manager (Nexus/Artifactory) 的重要性，設定 Routing Rules 封鎖 Public Proxy 對內部 namespace 的存取。
    -   提及不要混合使用 `latest.integration` 或動態版本號，這會增加被攻擊的風險。

## Q2: 我們專案掃描出了 100 個漏洞，Build 變得很慢且一直失敗，開發團隊很反彈，身為資深工程師你會怎麼處理？
**Our project scan found 100 vulnerabilities, the build is slow and keeps failing, and the dev team is pushing back. As a Senior Engineer, how would you handle this?**

-   **高分回答要點 (Key Points)**：
    -   **Triage (分流)**：首先區分 Critical/High 與 Low/Medium。只針對 Critical/High 設定 `failBuild`。
    -   **Suppression**：引入 Suppression File 機制，排除 False Positives（誤報）或不影響當前架構的漏洞。
    -   **Baseline**：如果是既有專案（Legacy），可以建立一個「基準線（Baseline）」，只針對「新增」的漏洞報錯，逐步償還技術債。
    -   **Performance**：將掃描移至 CI 的獨立 Stage，不影響開發者本機的快速迭代（或只在本機做輕量掃描）。

## Q3: 為什麼我們需要 SBOM？它和一般的 `mvn dependency:tree` 有什麼不同？
**Why do we need an SBOM? How is it different from a standard `mvn dependency:tree`?**

-   **高分回答要點 (Key Points)**：
    -   **標準化**：`dependency:tree` 是特定工具的輸出格式，SBOM (CycloneDX/SPDX) 是機器可讀的通用業界標準。
    -   **完整性**：SBOM 不只包含套件名稱版本，還包含授權資訊（License）、雜湊值（Hash/Digest）、供應商資訊等。
    -   **用途**：SBOM 用於供應鏈透明化，可被第三方工具攝取（Ingest）以進行持續監控，即使軟體已經部署到生產環境，也能快速比對新發現的 CVE。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點摘要 (Key Takeaways)
1.  **Shift Left Security**：將安全性檢查從「部署前」提前到「建置時」。
2.  **Explicit Repository Policy**：明確定義哪些 Group ID 只能從哪些 Repository 下載，杜絕 Dependency Confusion。
3.  **Automated Scanning**：整合 OWASP Dependency Check 或 Snyk，並設定合理的 `failBuildOnCVSS` 門檻。
4.  **Suppression is Healthy**：正確管理豁免清單是維持開發速度與安全性的平衡點。
5.  **SBOM is Mandatory**：生成 SBOM 已成為現代軟體交付的標準配備，用於提升透明度與合規性。

## 後續延伸 (Next Steps)
-   **下一章預告**：將 Maven/Gradle 與 Docker/Kubernetes 整合（Containerization & CI/CD Optimization）。
-   **延伸閱讀**：研究 **Sigstore** 與 **Cosign**，了解如何對你的建置產物（Artifacts）進行數位簽章，確保從 Build 到 Deploy 的完整性（Integrity）。