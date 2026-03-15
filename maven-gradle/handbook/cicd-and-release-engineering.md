# 持續整合與發布工程 / CI/CD Integration & Release Engineering

## Mental model｜心智模型

在 Maven 與 Gradle 的世界中，發布工程的核心在於理解 **Artifact Immutability（產物不可變性）** 與 **Trust Chain（信任鏈）**。

### 1. Snapshot vs. Release：可變與不可變的二元對立
請將 Artifact 的生命週期想像成「草稿」與「出版品」的區別：

-   **SNAPSHOT (Drafts/Nightly Builds):**
    -   **性質**：Mutable（可變的）。
    -   **行為**：版本號以 `-SNAPSHOT` 結尾（Maven）或動態後綴（Gradle）。同一個版本號（如 `1.0.0-SNAPSHOT`）可以被多次覆寫。
    -   **用途**：開發團隊內部的快速迭代，允許依賴方拉取最新的開發中程式碼。
    -   **策略**：Maven Repository 會對 Snapshot 採取 "Unique Version" 策略（加上時間戳記），但在邏輯上它們仍視為「同一個開發版本」。

-   **RELEASE (Published Books):**
    -   **性質**：Immutable（不可變的）。**這是發布工程的黃金鐵律**。
    -   **行為**：一旦發布（例如 `1.0.0`），該 Artifact 絕對不應該被修改或覆寫。如果程式碼有變，必須發布 `1.0.1`。
    -   **用途**：生產環境部署、對外公開的 Library。

### 2. The Trust Chain：簽署與驗證
當你的 Artifact 離開了你的 CI Server，進入公共或公司內部的 Repository (Nexus/Artifactory) 時，使用者如何確認「這真的是你編譯的」且「傳輸過程中未被竄改」？
這就是 **GPG/PGP Signing** 的角色。它如同實體世界中的「騎縫章」或「數位簽章」，是供應鏈安全的第一道防線。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Maven CI-Friendly Versions (The Modern Standard)
傳統 `maven-release-plugin` 會在 Git 上進行兩次 Commit（去 Snapshot -> Tag -> 升版 Snapshot），這在現代 CI/CD (GitLab CI, GitHub Actions) 中容易造成 Commit 污染或觸發無窮迴圈。

**Best Practice:** 使用 Maven 3.5.0+ 的 `${revision}` 機制。
在 `pom.xml` 中定義佔位符，由 CI Server 在建置時注入版本號。

```xml
<properties>
    <revision>1.0.0-SNAPSHOT</revision>
</properties>
<version>${revision}</version>
```

### 2. Gradle Versioning Strategy
Gradle 靈活性極高，建議將版本邏輯與 Build Script 分離。

**Best Practice:** 使用 `gradle.properties` 管理版本，並允許 CI 環境變數覆蓋。
在 `build.gradle` 中：
```groovy
version = System.getenv('CI_PIPELINE_IID') ? "1.0.${System.getenv('CI_PIPELINE_IID')}" : '1.0.0-SNAPSHOT'
```
這確保了 Local 開發是 Snapshot，CI 建置是具體的版號。

### 3. Repository Separation
永遠不要將 Snapshot 與 Release 混在同一個 Repository URL。
-   **Snapshots Repo:** 允許 Redeploy，清理策略較激進（如保留最近 30 天）。
-   **Releases Repo:** 禁止 Redeploy，永久保存。

### 4. Semantic Versioning (SemVer)
嚴格遵守 `Major.Minor.Patch`：
-   **Major**: Breaking changes (API 不相容)。
-   **Minor**: New features (向下相容)。
-   **Patch**: Bug fixes (向下相容)。
CI/CD 腳本應能根據 Commit Message (如 Conventional Commits) 自動決定升版策略。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Snapshot Dependency" in Release (致命錯誤)
**Anti-pattern:** 發布一個 Release 版本的 Artifact（如 `1.0.0`），但它依賴了 `com.example:utils:2.0.0-SNAPSHOT`。
**後果:** 當 `utils` 的 Snapshot 更新後，你的 `1.0.0` 行為會改變，導致 "It works on my machine" 但生產環境崩潰，且無法回溯。
**防禦:** 使用 `maven-enforcer-plugin` 或 Gradle 的檢查邏輯，在 Release 建置時強制檢查 `no-snapshot-dependencies`。

### 2. Hardcoded Credentials in SCM
**Anti-pattern:** 將 Nexus/Artifactory 的帳號密碼直接寫在 `pom.xml` 或 `build.gradle` 中並推送到 Git。
**後果:** 安全漏洞。
**修正:**
-   **Maven:** 使用 `~/.m2/settings.xml` 搭配 CI 的 Secret Injection。
-   **Gradle:** 使用 `~/.gradle/gradle.properties` 或環境變數 (`ORG_GRADLE_PROJECT_username`)。

### 3. Rebuilding the Same Tag
**Anti-pattern:** 為了修一個小 config，重新 build 已經發布的 `v1.0.1` tag 並強制推送到 Nexus。
**後果:** 下游專案可能快取了舊的 `v1.0.1`，導致雜湊不一致（Checksum mismatch）或行為不一致。
**修正:** 永遠向前滾動版本（Roll forward），發布 `v1.0.2`。

---

## Checklists & workflows｜檢查清單與流程

在設定 CI/CD Pipeline 時，請對照此清單：

### Release Engineering Checklist
- [ ] **Clean Environment**: 建置必須在乾淨的容器或 Workspace 中進行，不受上一檔案殘留影響。
- [ ] **Tests & Quality Gates**: 單元測試、整合測試通過，SonarQube/Checkstyle 檢查通過。
- [ ] **No Snapshot Dependencies**: 確認所有依賴項皆為 Release 版本。
- [ ] **Javadoc/Sources**: 發布 Library 時，必須包含 `-sources.jar` 與 `-javadoc.jar`（Maven Central 強制要求）。
- [ ] **GPG Signing**: 所有 Artifacts (pom, jar, source, javadoc) 皆已簽署 `.asc` 檔案。
- [ ] **Checksums**: 生成 MD5/SHA1/SHA256 雜湊檔。
- [ ] **Idempotency**: 確保 Release 流程失敗時可以重試，而不會留下部分上傳的垃圾檔案（Staging Repository 概念）。

### Typical CI/CD Decision Tree
1.  **Trigger:** Git Tag push (`v1.0.0`) OR Manual Trigger on `main` branch.
2.  **Validate:** Check SemVer format.
3.  **Build:** Compile & Test.
4.  **Sign:** Sign artifacts using GPG key (injected via CI secrets).
5.  **Publish:**
    -   IF version ends with `-SNAPSHOT` -> Push to **Snapshot Repo**.
    -   IF version is Release -> Push to **Staging/Release Repo**.
6.  **Notify:** Update Jira/Slack/Email.

---

## Real-world examples｜實戰案例

### 1. Maven: GPG Signing & Distribution Management
這是標準的 `pom.xml` 片段，用於發布到私有 Nexus 並進行簽署。關鍵在於將敏感資訊移出 POM。

```xml
<!-- pom.xml -->
<project>
    ...
    <distributionManagement>
        <snapshotRepository>
            <id>nexus-snapshots</id>
            <url>https://nexus.company.com/repository/maven-snapshots/</url>
        </snapshotRepository>
        <repository>
            <id>nexus-releases</id>
            <url>https://nexus.company.com/repository/maven-releases/</url>
        </repository>
    </distributionManagement>

    <profiles>
        <profile>
            <id>release</id>
            <build>
                <plugins>
                    <!-- GPG Signing Plugin -->
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-gpg-plugin</artifactId>
                        <version>3.0.1</version>
                        <executions>
                            <execution>
                                <id>sign-artifacts</id>
                                <phase>verify</phase>
                                <goals>
                                    <goal>sign</goal>
                                </goals>
                                <configuration>
                                    <!-- Prevent GPG from asking for passphrase interactively -->
                                    <gpgArguments>
                                        <arg>--pinentry-mode</arg>
                                        <arg>loopback</arg>
                                    </gpgArguments>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <!-- Source & Javadoc Plugins omitted for brevity -->
                </plugins>
            </build>
        </profile>
    </profiles>
</project>
```

**CI Server 設定 (settings.xml):**
```xml
<settings>
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>${env.NEXUS_USER}</username>
      <password>${env.NEXUS_PASSWORD}</password>
    </server>
  </servers>
</settings>
```

### 2. Gradle: Maven Publish & Signing Plugin
Gradle 的現代化發布方式，使用 `maven-publish` 與 `signing` plugin。

```groovy
// build.gradle
plugins {
    id 'java-library'
    id 'maven-publish'
    id 'signing'
}

group = 'com.company.app'
version = System.getenv('RELEASE_VERSION') ?: '1.0.0-SNAPSHOT'

java {
    withJavadocJar()
    withSourcesJar()
}

publishing {
    publications {
        mavenJava(MavenPublication) {
            from components.java
            
            pom {
                name = 'My Library'
                description = 'A description of my library'
                url = 'http://www.example.com/library'
                // ... licenses, developers, scm info
            }
        }
    }
    repositories {
        maven {
            name = "OSSRH"
            // 動態決定上傳目標
            def releasesRepoUrl = "https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/"
            def snapshotsRepoUrl = "https://s01.oss.sonatype.org/content/repositories/snapshots/"
            url = version.endsWith('SNAPSHOT') ? snapshotsRepoUrl : releasesRepoUrl
            
            credentials {
                username = System.getenv("OSSRH_USERNAME")
                password = System.getenv("OSSRH_PASSWORD")
            }
        }
    }
}

signing {
    // 只有在非 Snapshot 版本時才強制簽署
    required { !version.endsWith('SNAPSHOT') && gradle.taskGraph.hasTask("publish") }
    
    // 從環境變數讀取 GPG Key 內容 (Base64 encoded)
    def signingKey = System.getenv("GPG_SIGNING_KEY")
    def signingPassword = System.getenv("GPG_SIGNING_PASSWORD")
    useInMemoryPgpKeys(signingKey, signingPassword)
    
    sign publishing.publications.mavenJava
}
```

### 3. CI Pipeline Command (Pseudo-code)
在 CI (如 Jenkins/GitLab CI) 中執行發布的指令範例：

```bash
# Maven Release
mvn clean deploy -P release -Drevision=1.2.0 --settings ci-settings.xml

# Gradle Release
export RELEASE_VERSION=1.2.0
export ORG_GRADLE_PROJECT_signingKeyId=...
./gradlew clean publish
```