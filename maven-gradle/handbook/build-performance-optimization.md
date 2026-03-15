# 建置效能優化與快取策略 / Build Performance Optimization & Caching Strategies

在現代軟體開發中，建置速度直接影響開發者的生產力與心情。等待編譯的時間就是浪費的時間。本章節將深入探討如何透過 Gradle 與 Maven 的進階功能，將建置時間從「去喝杯咖啡」縮短為「眨眼即完成」。

## Mental model｜心智模型

要優化建置效能，必須建立三個核心的心智模型：**避免重工 (Avoid Rework)**、**並行處理 (Parallelism)** 與 **熱機待命 (Warm Warm-up)**。

### 1. 增量與指紋 (Incremental & Fingerprinting)
想像建置過程是一個函數 `f(inputs) = outputs`。
- **Gradle 的做法**：它會對每一個 Task 的輸入（程式碼、依賴、設定）與輸出（編譯後的 class、jar 檔）計算雜湊值（Fingerprint）。
- **快取邏輯**：在執行 Task 之前，先檢查「輸入的指紋」是否變過？
  - 如果沒變，且「輸出的指紋」與上次一致，則標記為 `UP-TO-DATE`，直接跳過。
  - 如果本地沒變但 CI Server 跑過，則從 **Build Cache** 下載結果（FROM-CACHE）。
- **Maven 的做法**：傳統 Maven 主要依賴 timestamp 檢查 source 是否比 target 新。但在引入 Build Cache Extension (如 Develocity 或 mvnd) 後，也能達到類似 Gradle 的指紋快取效果。

### 2. 依賴圖譜與並行 (Dependency Graph & Parallelism)
- 不要把建置看作一條單行道（Sequence），而是一個有向無環圖（DAG）。
- 只要兩個模組（Module/Project）之間沒有依賴關係，它們就應該同時被建置。
- **優化目標**：盡可能讓 DAG 變得寬（減少耦合），而不是深（長依賴鏈）。

### 3. 守護行程 (The Daemon)
- JVM 啟動很慢，JIT (Just-In-Time) 編譯器需要時間熱身。
- **策略**：不要每次建置都殺死 JVM。保持一個長駐的背景行程（Gradle Daemon / Maven Daemon `mvnd`），讓它保持「熱機」狀態，保留記憶體中的依賴與 JIT 優化結果。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Gradle 效能黃金三角 (The Gradle Performance Trinity)
在 `gradle.properties` 中必須開啟的三個設定：

```properties
# 1. 啟用並行執行，讓獨立的專案同時建置
org.gradle.parallel=true

# 2. 啟用守護行程 (通常預設開啟，但顯式宣告較保險)
org.gradle.daemon=true

# 3. 啟用建置快取 (最重要的一步)
org.gradle.caching=true
```

### 2. Maven 的現代化加速：mvnd 與 Parallel
傳統 Maven (`mvn`) 是單執行緒且每次重啟 JVM。請改用以下模式：

- **使用 Maven Daemon (`mvnd`)**：這是 Maven 生態系的 Game Changer，直接替換 `mvn` 指令，速度通常提升 2-4 倍。
- **並行建置 (`-T`)**：如果無法使用 `mvnd`，至少在 CI 或本地使用多執行緒。
  ```bash
  # 使用每個 CPU 核心對應一個執行緒
  mvn clean install -T 1C
  ```

### 3. 遠端建置快取 (Remote Build Cache)
這是團隊效能提升的關鍵。
- **原理**：CI Server 執行建置後，將結果（Compiled Classes, Jars）上傳到共享快取伺服器。
- **效果**：開發者早上拉下最新的 code，執行 build 時，不需要重新編譯別人寫的 code，直接從 Server 下載二進位檔。
- **實作模式**：
  - **CI (Continuous Integration)**: Push (寫入) & Pull (讀取)。
  - **Local Developer**: Only Pull (唯讀)。避免本地髒資料汙染共用快取。

### 4. 模組化架構優化 (Modularization for Speed)
- **扁平化模組**：將巨大的 Monolith 拆解。Gradle/Maven 只能以「模組」為單位進行並行處理。
- **ABI (Application Binary Interface) 相容性**：Gradle 支援 Compile Avoidance。如果模組 A 依賴模組 B，但模組 B 只有 method body 改變（method signature 沒變），則模組 A **不需要**重新編譯。這需要良好的介面設計。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 習慣性執行 `clean` (The "Clean" Addiction)
- **反模式**：開發者習慣每次都打 `mvn clean install` 或 `./gradlew clean build`。
- **後果**：你主動刪除了所有增量編譯的基礎與快取，強迫工具從零開始。
- **修正**：信任工具的 `UP-TO-DATE` 機制。只有在遇到詭異問題時才執行 `clean`。

### 2. 非決定性的 Task 輸入 (Non-deterministic Inputs)
- **反模式**：在 Task 中加入時間戳記、隨機數，或依賴絕對路徑。
  ```groovy
  // Gradle Anti-pattern
  task generateVersion {
      inputs.property("timestamp", System.currentTimeMillis()) // 永遠都會導致 Cache Miss
      ...
  }
  ```
- **後果**：Cache Key 每次都不同，快取永遠失效 (Cache Miss)。
- **修正**：確保輸入是穩定的（例如使用 Git Commit Hash 而非當下時間）。

### 3. 依賴範圍過大 (Over-dependency)
- **反模式**：在 Root Project 宣告所有 Sub-projects 的依賴；或者使用 `api` (Gradle) / `compile` (Maven) 依賴所有東西。
- **後果**：牽一髮動全身。修改底層一個小 utils，導致上層所有模組重新編譯。
- **修正**：精確使用 `implementation` (Gradle) 來隱藏內部依賴，阻斷重新編譯的連鎖反應。

### 4. 網路依賴與 Snapshot (Network & Snapshots)
- **反模式**：依賴大量的 `-SNAPSHOT` 版本，且設定 `always update`。
- **後果**：Maven/Gradle 每次都要去遠端 Repository 檢查是否有新版，造成巨大的網路 I/O 延遲。
- **修正**：在開發階段鎖定版本，或限制 Snapshot 的更新頻率（例如每天一次）。

---

## Checklists & workflows｜檢查清單與流程

### Performance Diagnosis Workflow (效能診斷流程)

當覺得建置變慢時，請依照此流程檢查：

1.  **Measure (測量)**：不要憑感覺。
    - Gradle: 使用 `--scan` 產生 Build Scan 報告。
    - Maven: 使用 `mvnd --scan` 或 Maven Profiler。
2.  **Profile (分析)**：
    - 查看 Build Scan 中的 "Performance" 分頁。
    - 找出 "Task Execution" 中耗時最長的 Task。
    - 檢查 "Cache Misses" 的原因（是因為 inputs 改變，還是 overlapping outputs？）。
3.  **Optimize (優化)**：
    - 針對 Critical Path 上的 Task 進行優化。
    - 調整記憶體設定 (`jvmargs`)。

### Daily Development Checklist (日常開發檢查清單)

- [ ] **Gradle 使用者**：
    - [ ] `gradle.properties` 是否已開啟 `parallel` 與 `caching`？
    - [ ] 是否避免使用 `clean` 指令，除非必要？
    - [ ] 本地 Java 版本是否與 CI 一致（避免 Cache Key 因 Java 版本不同而失效）？
- [ ] **Maven 使用者**：
    - [ ] 是否已安裝並使用 `mvnd` 替代 `mvn`？
    - [ ] 若使用原生 `mvn`，是否加上了 `-T 1C` 參數？
- [ ] **CI/CD 設定**：
    - [ ] CI Pipeline 是否設定了 Remote Build Cache 的寫入權限？
    - [ ] CI 是否正確保存了 dependency cache (如 `~/.gradle/caches` 或 `~/.m2/repository`)？

---

## Real-world examples｜實戰案例

### 案例一：Gradle Build Scan 分析 Cache Miss

**情境**：開發者發現明明沒改 code，每次跑 `test` task 卻都重新執行，沒有吃到 Cache。

**診斷**：
執行 `./gradlew test --scan`，打開報告連結，點選 **Performance > Task execution**，找到 `:app:test` task，點擊查看詳細資訊。

**發現**：
報告顯示 Cache miss 原因為：`Input property 'buildTimestamp' has changed for task ':app:test'`.

**程式碼問題**：
```groovy
// build.gradle (Bad Practice)
tasks.withType(Test) {
    systemProperty 'build.time', System.currentTimeMillis() // 兇手在這裡
}
```

**解決方案**：
移除隨機變數，或將其標記為 `@Internal` (不參與 Cache Key 計算)，或僅在 CI 發布階段才注入時間戳記。

### 案例二：Maven Monolith 的加速

**情境**：一個擁有 50 個模組的傳統 Maven 專案，完整建置需要 15 分鐘。

**優化步驟**：

1.  **安裝 mvnd**：
    ```bash
    brew install mvndaemon/homebrew-mvnd/mvnd  # macOS
    choco install mvnd                           # Windows
    ```
2.  **執行並行建置**：
    ```bash
    mvnd clean install
    ```
    *結果：時間縮短至 4 分鐘 (因 Daemon 熱機 + 並行編譯)。*

3.  **進階優化 (針對 CI)**：
    引入 Gradle Enterprise Maven Extension (現名 Develocity) 或類似的 Build Cache Extension。
    *結果：CI 時間縮短至 1 分鐘 (因為大部分模組未變更，直接從 Cache 還原)。*

### 案例三：Gradle 記憶體調優

**情境**：大型專案在並行編譯時經常發生 `OutOfMemoryError` 或 GC 頻繁導致卡頓。

**配置調整 (`gradle.properties`)**：

```properties
# 給予 Daemon 足夠的 Heap Size，但不要超過實體記憶體的 80%
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g -XX:+HeapDumpOnOutOfMemoryError

# 限制並行 Worker 數量，避免 CPU Context Switch 過於頻繁
# 預設是 CPU 核心數，若記憶體不足，可適當調低
org.gradle.workers.max=4
```